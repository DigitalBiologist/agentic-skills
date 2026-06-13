#!/usr/bin/env python3
"""
西湖大学 PPT 单页 v2 端到端 pipeline:

  1. 读 wrapper_v2.txt + 用户的 content 文件 → 拼成完整 NBP prompt
  2. 保存完整 prompt 到 <output_dir>/p<NN>_full_prompt.txt （供后续迭代）
  3. 取参考模板（默认本地 base64 内联，无需图床；--use-imghost 走旧图床路线）
  4. 调 NBP 图生图 → <output_dir>/p<NN>_raw.png
  5. composite_v2: 合成模板装饰 + logo 像素级覆盖 + 加页码
  6. 输出 <output_dir>/p<NN>_FINAL.png

用法:
    python3 generate_slide_v2.py <content_file> -p <page_num> -o <output_dir>

示例:
    python3 generate_slide_v2.py p04_content.txt -p 4 -o ./slides_out
    # 不加页码（最后统一加）:
    python3 generate_slide_v2.py p04_content.txt --no-page-number -o ./slides_out

content 文件格式:
    v4 风格的 markdown-ish Chinese-annotated layout 描述。只包含正文内容,
    不需要包含 template preservation / strict text rules / visual style ——
    这些都在 wrapper_v2.txt 里固定下来了。每一页只改 content 文件即可。

自包含说明:
    本脚本所有依赖都在技能文件夹内（自引用，不依赖 ~/.claude）：
      - wrapper_v2.txt / composite_v2.py / 正文页模板_v2_*.png|jpg  （同目录）
      - image-api/image_generate.py + provider_config.py           （收编的 NBP CLI）
    唯一外部前置依赖：环境变量 LAOZHANG_API_KEY（NBP 生图 API key），
    以及 Python 包 requests / numpy / Pillow。详见 SKILL.md「外部前置依赖」。
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional

# 路径常量（全部自引用本技能文件夹，无 ~/.claude 硬路径）
ASSETS_DIR = Path(__file__).parent
WRAPPER_FILE = ASSETS_DIR / "wrapper_v2.txt"
COMPOSITE_SCRIPT = ASSETS_DIR / "composite_v2.py"
SYNC_SCRIPT = ASSETS_DIR / "sync_to_imghost_v2.sh"
TEMPLATE_JPG = ASSETS_DIR / "正文页模板_v2_1080p.jpg"          # 本地模板，默认直接喂给 NBP 做 base64 内联
NBP_SCRIPT = ASSETS_DIR / "image-api" / "image_generate.py"   # 收编的 NBP CLI（自包含）

PLACEHOLDER = "{{CONTENT}}"


def build_full_prompt(wrapper_text: str, content_text: str) -> str:
    """把 content 嵌入 wrapper 的 {{CONTENT}} 占位符位置。"""
    if PLACEHOLDER not in wrapper_text:
        raise ValueError(f"wrapper file 缺少 {PLACEHOLDER} 占位符")
    return wrapper_text.replace(PLACEHOLDER, content_text.strip())


def sync_template_to_imghost() -> str:
    """（可选路线）调用 sync 脚本把 v2 模板同步到自建图床并返回 URL。"""
    result = subprocess.run(
        ["bash", str(SYNC_SCRIPT)],
        capture_output=True, text=True, check=True,
    )
    url = result.stdout.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"sync 脚本未返回 URL: stdout={result.stdout!r} stderr={result.stderr!r}")
    return url


def call_nbp(prompt_text: str, template_ref: str, output_path: Path) -> None:
    """调 NBP 生成原始 slide。template_ref 可以是公网 URL，也可以是本地图片路径
    （image_generate.py 会对本地路径自动 base64 内联，无需图床）。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3", str(NBP_SCRIPT),
        prompt_text,
        "-i", template_ref,
        "-r", "4K",
        "-a", "16:9",
        "-o", str(output_path),
    ]
    print(f"  → calling NBP (4K, 16:9, 60-120s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"NBP failed (exit {result.returncode})")
    # 找最后一行 "Done! (XXs)" 报告
    for line in result.stdout.splitlines()[-5:]:
        if "Done!" in line or "Saved" in line:
            print(f"  ← {line.strip()}")


def call_composite(raw_path: Path, final_path: Path, page_number: Optional[int]) -> None:
    """调 composite_v2.py 做后处理。"""
    cmd = ["python3", str(COMPOSITE_SCRIPT), str(raw_path), "-o", str(final_path)]
    if page_number is not None:
        cmd += ["-p", str(page_number)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        print(f"  {line}")


def main():
    ap = argparse.ArgumentParser(
        description="西湖大学 PPT 单页 v2 端到端 pipeline (wrapper + content → NBP → composite)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("content", type=Path, help="内容文件路径 (v4 风格的 layout 描述)")
    ap.add_argument("-p", "--page-number", type=int, default=None,
                    help="页码 (留空则不加页码)")
    ap.add_argument("--no-page-number", action="store_true",
                    help="显式跳过加页码 (与 -p 互斥)")
    ap.add_argument("-o", "--output-dir", type=Path, default=None,
                    help="输出目录 (默认 <content文件所在目录>/_output)")
    ap.add_argument("--name", type=str, default=None,
                    help="输出文件名前缀 (默认从 content 文件名推断, e.g. p04)")
    ap.add_argument("--skip-nbp", action="store_true",
                    help="只重做 composite (复用已有的 raw png)")
    ap.add_argument("--use-imghost", action="store_true",
                    help="走自建图床上传模板（旧路线，需配置 sync_to_imghost_v2.sh）；默认本地 base64 内联")
    args = ap.parse_args()

    # 参数验证
    if not args.content.exists():
        print(f"ERROR: content file not found: {args.content}", file=sys.stderr)
        sys.exit(1)

    if args.no_page_number:
        page_num = None
    else:
        page_num = args.page_number  # 可能是 None

    output_dir = args.output_dir or (args.content.parent / "_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 推断文件名前缀: e.g. "p04_prompt.txt" → "p04";  "p04_content.md" → "p04";  fallback 用 stem
    stem = args.content.stem
    if args.name:
        name_prefix = args.name
    else:
        # 取第一段用 _ 分割
        name_prefix = stem.split("_")[0] if "_" in stem else stem

    print(f"=== 西湖大学 PPT 单页 v2 pipeline ===")
    print(f"content:    {args.content}")
    print(f"output_dir: {output_dir}")
    print(f"name:       {name_prefix}")
    print(f"page_num:   {page_num}")

    full_prompt_path = output_dir / f"{name_prefix}_full_prompt.txt"
    raw_path = output_dir / f"{name_prefix}_raw.png"
    final_path = output_dir / f"{name_prefix}_FINAL.png"

    # === Step 1: 拼装完整 prompt ===
    print("\n[1/4] 拼装 full prompt ...")
    wrapper = WRAPPER_FILE.read_text(encoding="utf-8")
    content = args.content.read_text(encoding="utf-8")
    full_prompt = build_full_prompt(wrapper, content)
    full_prompt_path.write_text(full_prompt, encoding="utf-8")
    print(f"  saved: {full_prompt_path} ({len(full_prompt)} chars)")

    # === Step 2: NBP 调用 ===
    if args.skip_nbp:
        if not raw_path.exists():
            print(f"ERROR: --skip-nbp 但 {raw_path} 不存在", file=sys.stderr)
            sys.exit(1)
        print(f"\n[2/4] SKIP NBP (复用 {raw_path})")
    else:
        if args.use_imghost:
            print("\n[2/4] 同步模板到自建图床 + 调 NBP ...")
            template_ref = sync_template_to_imghost()
            print(f"  template URL (图床): {template_ref}")
        else:
            # 默认：直接把本地模板路径传给 NBP，image_generate.py 会自动 base64 内联（无需公网图床）
            print("\n[2/4] 本地模板内联 + 调 NBP ...")
            if not TEMPLATE_JPG.exists():
                print(f"ERROR: 本地模板缺失: {TEMPLATE_JPG}", file=sys.stderr)
                sys.exit(1)
            template_ref = str(TEMPLATE_JPG)
            print(f"  template (本地内联): {template_ref}")
        call_nbp(full_prompt, template_ref, raw_path)
        print(f"  saved raw: {raw_path}")

    # === Step 3: composite 后处理 ===
    print("\n[3/4] composite (装饰层 + logo + 页码) ...")
    call_composite(raw_path, final_path, page_num)
    print(f"  saved final: {final_path}")

    # === Step 4: 总结 ===
    print(f"\n[4/4] DONE")
    print(f"  full prompt: {full_prompt_path}")
    print(f"  raw:         {raw_path}")
    print(f"  final:       {final_path}")
    if page_num is not None:
        print(f"  with page number: {page_num}")
    else:
        print(f"  (no page number — add later with composite_v2.py -p N)")


if __name__ == "__main__":
    main()

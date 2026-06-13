#!/usr/bin/env python3
"""
v2 PPT 单页后处理 pipeline:
1. 把 NBP 生成的 raw slide (其装饰区可能丢失或被替换) 与 clean 模板合成 ——
   clean 模板的非白背景像素 (橙弧/蓝弧/双 logo/分隔线) 直接覆盖到 NBP 输出上
2. (可选) 在右下角的蓝色 wedge 上添加白色页码数字

用法:
    python3 composite_v2.py <nbp_raw.png> [-p <page_num>] [-o <output.png>]

示例:
    # 只合成模板装饰，不加页码
    python3 composite_v2.py slide_raw.png -o slide_final.png

    # 合成模板装饰 + 加 4 号页码
    python3 composite_v2.py slide_raw.png -p 4 -o slide_p04.png

设计要点:
- 用 numpy 做像素级 mask 合成 (template 非白处覆盖 NBP)
- 阈值: R+G+B < 720 视为"非白" (留 5/256 容差)
- 合成前把 clean 模板 resize 到 NBP 输出尺寸 (NBP 一般 5504×3072, 模板 2667×1500)
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# === 路径常量 ===
ASSETS_DIR = Path(__file__).parent
CLEAN_TEMPLATE = ASSETS_DIR / "正文页模板_v2_clean.png"

# === 页码相对位置（基于 v2 模板 2667×1500 实测，用 fill_holes 精确定位）===
# 原模板 "4" bbox (2584,1431)-(2599,1454), 16×24 px, 中心 (2591.5, 1442.5)
PAGE_NUM_CENTER_X_RATIO = 2591.5 / 2667  # ≈ 0.9717
PAGE_NUM_CENTER_Y_RATIO = 1442.5 / 1500  # ≈ 0.9617
PAGE_NUM_HEIGHT_RATIO = 0.022            # 比原模板大约 38% (24/1500=1.6% → 2.2%)

# === "非白" 阈值: R+G+B 之和 ===
WHITE_SUM_THRESHOLD = 750  # 三通道均 250+ 才算白底；任何带颜色的像素都视为装饰

# === 右上角双 logo 的 bbox (像素级强制覆盖区，避免 NBP 重画) ===
# 实测原模板上 (2391,4)-(2650,141) 包含两个 logo（已带 padding）
LOGO_BBOX_RATIO = (
    2391 / 2667,   # x0 ≈ 0.8965
    4 / 1500,      # y0 ≈ 0.0027
    2650 / 2667,   # x1 ≈ 0.9936
    141 / 1500,    # y1 ≈ 0.0940
)

# === 字体 ===
FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def load_font(size: int):
    for fp in FONT_CANDIDATES:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size, index=0)
            except Exception:
                continue
    return ImageFont.load_default()


def composite_decoration(nbp_img: Image.Image, clean_template: Image.Image) -> Image.Image:
    """把 clean 模板的装饰元素覆盖到 NBP 输出上。

    两层覆盖:
    1. 全图非白像素 mask 覆盖 (橙弧/蓝弧/分隔线 / logo 的有色部分)
    2. logo bbox 整块强制覆盖 (确保 logo 内部的白色细节也是模板的，而不是 NBP 重画的)
    """
    # 把模板 resize 到 NBP 输出尺寸
    template_resized = clean_template.resize(nbp_img.size, Image.LANCZOS).convert("RGB")

    nbp_arr = np.array(nbp_img.convert("RGB"))
    tpl_arr = np.array(template_resized)

    out = nbp_arr.copy()

    # === Layer 1: 非白像素 mask 覆盖 ===
    pixel_sum = tpl_arr.astype(np.int32).sum(axis=2)
    decoration_mask = pixel_sum < WHITE_SUM_THRESHOLD  # True = 装饰像素
    out[decoration_mask] = tpl_arr[decoration_mask]

    # === Layer 2: logo bbox 整块覆盖 (像素级复刻) ===
    W, H = nbp_img.size
    lx0 = int(LOGO_BBOX_RATIO[0] * W)
    ly0 = int(LOGO_BBOX_RATIO[1] * H)
    lx1 = int(LOGO_BBOX_RATIO[2] * W)
    ly1 = int(LOGO_BBOX_RATIO[3] * H)
    out[ly0:ly1, lx0:lx1] = tpl_arr[ly0:ly1, lx0:lx1]

    return Image.fromarray(out)


def add_page_number(img: Image.Image, page_num: int) -> Image.Image:
    """在右下角的蓝色 wedge 上添加白色页码数字。"""
    W, H = img.size
    # 字号: 想要 bbox 高 ≈ 3.2% × H, 字号大约要 1.30 倍
    target_size = int(PAGE_NUM_HEIGHT_RATIO * H * 1.30)
    font = load_font(target_size)

    text = str(page_num)
    img_out = img.copy()
    draw = ImageDraw.Draw(img_out)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    offset_x, offset_y = bbox[0], bbox[1]

    cx = int(PAGE_NUM_CENTER_X_RATIO * W)
    cy = int(PAGE_NUM_CENTER_Y_RATIO * H)
    px = cx - tw // 2 - offset_x
    py = cy - th // 2 - offset_y

    draw.text((px, py), text, fill=(255, 255, 255), font=font)
    return img_out


def main():
    ap = argparse.ArgumentParser(description="v2 PPT 单页后处理 (合成模板装饰 + 加页码)")
    ap.add_argument("input", type=Path, help="NBP 生成的原始 PNG 路径")
    ap.add_argument("-p", "--page-number", type=int, default=None,
                    help="页码数字 (留空则不加页码)")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="输出路径 (默认 <input>_final.png 或 <input>_p<n>.png)")
    ap.add_argument("--template", type=Path, default=CLEAN_TEMPLATE,
                    help=f"clean 模板路径 (默认 {CLEAN_TEMPLATE})")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    if not args.template.exists():
        print(f"ERROR: clean template not found: {args.template}", file=sys.stderr)
        sys.exit(1)

    nbp = Image.open(args.input)
    clean = Image.open(args.template)
    print(f"NBP raw: {nbp.size}")
    print(f"Clean template: {clean.size}")

    # 1. 合成模板装饰
    composed = composite_decoration(nbp, clean)
    print("OK: composited decoration layer")

    # 2. (可选) 加页码
    if args.page_number is not None:
        composed = add_page_number(composed, args.page_number)
        print(f"OK: added page number {args.page_number}")
        suffix = f"_p{args.page_number}"
    else:
        suffix = "_final"

    # 3. 保存
    out = args.output or args.input.with_name(f"{args.input.stem}{suffix}{args.input.suffix}")
    composed.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()

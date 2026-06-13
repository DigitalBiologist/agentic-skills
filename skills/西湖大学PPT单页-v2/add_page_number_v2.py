#!/usr/bin/env python3
"""
往西湖大学 v2 模板生成的 PPT 单页图片右下角的蓝色 wedge 上添加白色页码数字。

用法:
    python3 add_page_number_v2.py <input.png> <page_number> [-o <output.png>]

示例:
    # 给单张图加 4 号页码（默认输出 <input>_p4.png）
    python3 add_page_number_v2.py slide.png 4

    # 指定输出路径
    python3 add_page_number_v2.py slide.png 12 -o slide_final.png

    # 批量
    for i in 1 2 3 4 5; do
        python3 add_page_number_v2.py slide_$i.png $i
    done

设计要点:
- 位置参考: 原模板 2667×1500 上 "4" 中心约在 (95.0% × W, 93.5% × H)
- 字符高度: 约 3.2% × image_height
- 颜色: 白色 (255,255,255)
- 字体: Helvetica.ttc (macOS 自带)
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Union
from PIL import Image, ImageDraw, ImageFont

# v2 模板原始模板上 "4" 的相对位置（基于 2667×1500 实测，fill_holes 精确定位）
# bbox: (2584,1431)-(2599,1454), 16×24 px, 中心 (2591.5, 1442.5)
PAGE_NUM_CENTER_X_RATIO = 2591.5 / 2667  # ≈ 0.9717
PAGE_NUM_CENTER_Y_RATIO = 1442.5 / 1500  # ≈ 0.9617
# 字符高度: 比原模板大约 38% (1.6% → 2.2%)
PAGE_NUM_HEIGHT_RATIO = 0.022

# 字体路径（macOS 自带 Helvetica TTC）
DEFAULT_FONT = "/System/Library/Fonts/Helvetica.ttc"


def find_font(size: int):
    """加载字体；优先 Helvetica，失败则用 PIL default。"""
    candidates = [
        DEFAULT_FONT,
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for fp in candidates:
        if Path(fp).exists():
            try:
                # TTC 文件需要 index, Helvetica.ttc 第 0 个一般是 Regular
                return ImageFont.truetype(fp, size, index=0)
            except Exception:
                continue
    return ImageFont.load_default()


def add_page_number(input_path: Path, page_num: int, output_path: Optional[Path] = None) -> Path:
    """在图像右下角添加页码数字。"""
    img = Image.open(input_path).convert("RGB")
    W, H = img.size

    # 基于图像尺寸算出字号（PIL 的 size 大约对应字符 cap height，比 bbox 高度小一点）
    # 实测: 想要 bbox 高 = 3.2% × H，字号大约要给 4.0% × H
    target_h_px = int(PAGE_NUM_HEIGHT_RATIO * H * 1.30)
    font = find_font(target_h_px)

    text = str(page_num)
    draw = ImageDraw.Draw(img)

    # 量真实 bbox 用于精准居中
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # textbbox 返回的 (x0,y0) 不一定是 (0,0)，要把 anchor 偏移修掉
    offset_x, offset_y = bbox[0], bbox[1]

    cx = int(PAGE_NUM_CENTER_X_RATIO * W)
    cy = int(PAGE_NUM_CENTER_Y_RATIO * H)
    px = cx - tw // 2 - offset_x
    py = cy - th // 2 - offset_y

    draw.text((px, py), text, fill=(255, 255, 255), font=font)

    if output_path is None:
        stem = input_path.stem
        output_path = input_path.with_name(f"{stem}_p{page_num}{input_path.suffix}")

    img.save(output_path)
    return output_path


def main():
    ap = argparse.ArgumentParser(description="给西湖大学 v2 模板生成的 PPT 单页加页码")
    ap.add_argument("input", type=Path, help="输入 PNG 路径")
    ap.add_argument("page_number", type=int, help="页码数字")
    ap.add_argument("-o", "--output", type=Path, default=None, help="输出路径（默认 <input>_p<n>.png）")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    out = add_page_number(args.input, args.page_number, args.output)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()

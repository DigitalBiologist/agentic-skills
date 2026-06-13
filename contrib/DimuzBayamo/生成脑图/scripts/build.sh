#!/usr/bin/env bash
# 脑图生成脚手架：Markdown + 模板 → 自包含 mindmap HTML
# 用法: build.sh <标题> <Markdown文件路径> <输出HTML路径>
#        build.sh <标题> - <输出HTML路径>   （从 stdin 读 Markdown）
# 产出：单个自包含 HTML，所有 JS/CSS 内联，零 CDN，纯离线可用
set -euo pipefail

TITLE="${1:?用法: build.sh <标题> <Markdown文件|-> <输出HTML>}"
MD_SRC="${2:?用法: build.sh <标题> <Markdown文件|-> <输出HTML>}"
OUT="${3:?用法: build.sh <标题> <Markdown文件|-> <输出HTML>}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$(dirname "$OUT")"
mkdir -p "$OUT_DIR"

# 跨平台 Python 检测
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || { echo "❌ 需要 Python 3"; exit 1; })

# 生成自包含 HTML —— 所有 vendor JS + Markdown 内容全部内联
SKILL_DIR="$SKILL_DIR" TITLE="$TITLE" MD_SRC="$MD_SRC" OUT="$OUT" "$PYTHON" - << 'PYEOF'
import os, sys

sd = os.environ['SKILL_DIR']
title = os.environ['TITLE']
md_src = os.environ['MD_SRC']
out = os.environ['OUT']

# 读取模板
template_path = os.path.join(sd, 'template.html')
with open(template_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 读取 Markdown 内容
if md_src == '-':
    md_content = sys.stdin.read()
else:
    with open(md_src, 'r', encoding='utf-8') as f:
        md_content = f.read()

# 读取 vendor JS 库（全部内联，零 CDN）
d3_path = os.path.join(sd, 'vendor', 'd3.min.js')
with open(d3_path, 'r', encoding='utf-8') as f:
    d3_code = f.read()

lib_path = os.path.join(sd, 'vendor', 'markmap-lib.min.js')
with open(lib_path, 'r', encoding='utf-8') as f:
    lib_code = f.read()

view_path = os.path.join(sd, 'vendor', 'markmap-view.min.js')
with open(view_path, 'r', encoding='utf-8') as f:
    view_code = f.read()

# 替换占位符
html = html.replace('__TITLE__', title)
html = html.replace('__MARKDOWN_CONTENT__', md_content)
html = html.replace('__D3_CODE__', d3_code)
html = html.replace('__MARKMAP_LIB_CODE__', lib_code)
html = html.replace('__MARKMAP_VIEW_CODE__', view_code)

# 写入自包含 HTML
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

# 使用 ASCII 标记避免 Windows GBK 编码问题
print(f"  [OK] d3.js 内联:       {len(d3_code):,} 字节")
print(f"  [OK] markmap-lib 内联: {len(lib_code):,} 字节")
print(f"  [OK] markmap-view 内联:{len(view_code):,} 字节")
print(f"  [OK] Markdown 内容:    {len(md_content):,} 字符")
print(f"  [OK] 自包含 HTML:      {os.path.getsize(out):,} 字节")
PYEOF

echo ""
echo "[OK] 脑图已生成: $OUT"
echo "   用法: 浏览器直接打开（零依赖、纯离线）"

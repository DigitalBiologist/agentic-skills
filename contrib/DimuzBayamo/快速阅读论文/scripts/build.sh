#!/usr/bin/env bash
# 论文速读网页脚手架（机械步骤，零 token）：PDF → 自包含 index.html
# 用法: build.sh <论文PDF路径> <输出目录>
# 之后由 Claude 精读论文、填 index.html 的占位符，再跑 verify_render.js 验证
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PDF="${1:?用法: build.sh <PDF路径> <输出目录>}"
OUT="${2:?用法: build.sh <PDF路径> <输出目录>}"

command -v pdftotext >/dev/null || { echo "❌ 缺 pdftotext，先 brew install poppler"; exit 1; }
[ -f "$PDF" ] || { echo "❌ 找不到 PDF: $PDF"; exit 1; }

mkdir -p "$OUT/assets"

# 1) 拷贝 PDF + 提取全文（供 Claude 精读）
cp "$PDF" "$OUT/assets/paper.pdf"
pdftotext "$OUT/assets/paper.pdf" "$OUT/assets/fulltext.txt"

# 2) 生成自包含 index.html —— 所有 JS/CSS/PDF数据 全部内联，纯离线，零 CDN，零外部文件依赖
SKILL_DIR="$SKILL_DIR" OUT="$OUT" python3 - << 'PYEOF'
import os, base64, json

sd = os.environ['SKILL_DIR']
out = os.environ['OUT']

# 读取模板
template_path = os.path.join(sd, 'template.html')
with open(template_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 读取 PDF.js 库（内联到 HTML）
pdfjs_path = os.path.join(sd, 'vendor', 'pdf.min.js')
with open(pdfjs_path, 'r', encoding='utf-8') as f:
    pdfjs_code = f.read()

# PDF → base64 内联（关键：file:// 下 PDF.js 不能 fetch 本地文件，必须 base64 → Uint8Array 喂给 getDocument({data})）
pdf_path = os.path.join(out, 'assets', 'paper.pdf')
with open(pdf_path, 'rb') as f:
    pdf_b64 = base64.b64encode(f.read()).decode('ascii')

# PDF.js Worker 源码内联（file:// 下 new Worker('./pdf.worker.min.js') 会被浏览器安全策略拒绝；
# 内联为 JS 字符串 → 运行时 Blob URL → 同源 worker，绕开限制）
worker_path = os.path.join(sd, 'vendor', 'pdf.worker.min.js')
with open(worker_path, 'r', encoding='utf-8') as f:
    worker_code = f.read()

# 替换占位符 → 生成纯离线自包含 HTML
html = html.replace('__PDFJS_CODE__', pdfjs_code)
html = html.replace('__PAPER_DATA__', 'window.PDF_B64="' + pdf_b64 + '";')
html = html.replace('__WORKER_CODE__', 'window.PDF_WORKER_CODE=' + json.dumps(worker_code) + ';')

index_path = os.path.join(out, 'index.html')
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"   ✓ PDF.js 内联: {len(pdfjs_code):,} 字节")
print(f"   ✓ PDF base64:  {len(pdf_b64):,} 字符")
print(f"   ✓ Worker 内联: {len(worker_code):,} 字节")
print(f"   ✓ 自包含 HTML: {os.path.getsize(index_path):,} 字节")
PYEOF

PAGES=$(python3 -c "
import os
txt = open(os.environ['OUT'] + '/assets/fulltext.txt', encoding='utf-8').read()
# pdftotext 用 chr(12) (form feed) 分隔页面
print(txt.count(chr(12)) + 1)
")
echo ""
echo "✅ 脚手架就绪: $OUT"
echo "   输出结构:"
echo "     index.html          ← 自包含速读网页（所有 JS/CSS/PDF 数据已内联）"
echo "     assets/paper.pdf     ← 原始论文（留底）"
echo "     assets/fulltext.txt  ← 全文提取（供 Claude 精读）"
echo "   PDF 物理页数 ≈ ${PAGES}（PDF.js 页码从 1 开始 = 物理页；注意 ≠ 印刷页脚页码）"
echo ""
echo "   下一步:"
echo "     1) Read $OUT/assets/fulltext.txt 通读全文 + Read PDF 逐图确认页码/看图"
echo "     2) 用 Edit 填 $OUT/index.html 里的 __中文标题__/__英文原标题__/__meta__ 和 const SECTIONS"
echo "     3) node $SKILL_DIR/scripts/verify_render.js \"$OUT\" 验证渲染"

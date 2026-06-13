#!/usr/bin/env bash
# edit_local.sh <input_image> <output_image> "<prompt>" [aspect_ratio]
# 把本地图传到 tmpfiles 临时图床(1h)，用 NanoBanana Pro 按 prompt 做图生图编辑，存到 output。
# aspect_ratio 默认 16:9；脑图等非宽屏图请传第4个参数(如 4:3 / 3:4 / 1:1)。
# 用法须在 dangerouslyDisableSandbox 下跑（tmpfiles 在普通沙箱里连不上）。
# 注意：单次生成约需 3-4 分钟，超过 Bash 默认 120s 超时——调用时请设较长 timeout 或 run_in_background。
set -uo pipefail
IN="$1"; OUT="$2"; PROMPT="$3"; AR="${4:-16:9}"
[ -f "$IN" ] || { echo "ERR: input not found: $IN" >&2; exit 1; }
# 只取所需的两个 API key，不 source 整个 zshrc（zsh 语法在 bash 下会报错/卡住）
eval "$(grep -E '^[[:space:]]*export[[:space:]]+(LAOZHANG_API_KEY|NANOBANANA_API_KEY)=' ~/.zshrc 2>/dev/null || true)"
RESP=$(curl -sS -F "file=@$IN" https://tmpfiles.org/api/v1/upload)
URL=$(printf '%s' "$RESP" | python3 -c "import sys,json;u=json.load(sys.stdin)['data']['url'];print(u.replace('tmpfiles.org/','tmpfiles.org/dl/'))")
echo "[uploaded] $URL"
python3 "$(cd "$(dirname "$0")" && pwd)/image_generate.py" "$PROMPT" --provider nanobanana -i "$URL" -r 2K -a "$AR" -o "$OUT"

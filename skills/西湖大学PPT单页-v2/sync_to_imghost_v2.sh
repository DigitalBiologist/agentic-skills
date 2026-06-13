#!/bin/bash
# 幂等地把西湖大学正文页模板 v2（Guomics 风格）同步到「自建图床」并返回 URL。
#
# ⚠️ 可选路线 —— 大多数情况你用不到这个脚本：
#   generate_slide_v2.py 默认走「本地模板 base64 内联」，不需要任何图床。
#   只有当你显式加 --use-imghost 时才会调用本脚本，且需要你自己有一台可 ssh 的图床服务器。
#
# 用法: bash <skill_dir>/sync_to_imghost_v2.sh
# 输出: 图床 URL（stdout）
#
# 配置（原作者的私有图床信息已脱敏为占位符；用前用环境变量或直接改下面三行替换成你自己的）:
#   IMGHOST_SSH    你的图床服务器 ssh 别名/地址（写在 ~/.ssh/config 里更方便）
#   IMGHOST_HTTP   图床公网基址，如 http://YOUR_IMGHOST_IP/tmp
#   REMOTE_DIR     服务器上 web 可访问的 tmp 目录

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_JPG="$SCRIPT_DIR/正文页模板_v2_1080p.jpg"

IMGHOST_SSH="${IMGHOST_SSH:-<YOUR_IMGHOST_SSH_ALIAS>}"          # 例: aliyun
IMGHOST_HTTP="${IMGHOST_HTTP:-http://<YOUR_IMGHOST_IP>/tmp}"    # 例: http://1.2.3.4/tmp
REMOTE_DIR="${REMOTE_DIR:-/opt/slidegen/dist/tmp}"

REMOTE_NAME="westlake_main_template_v2_1080p.jpg"
REMOTE_PATH="$REMOTE_DIR/$REMOTE_NAME"
URL="$IMGHOST_HTTP/$REMOTE_NAME"

if [[ "$IMGHOST_SSH" == *"<YOUR_"* || "$IMGHOST_HTTP" == *"<YOUR_"* ]]; then
  echo "ERROR: 图床未配置。要么改用默认本地内联模式（去掉 --use-imghost），" >&2
  echo "       要么设置 IMGHOST_SSH / IMGHOST_HTTP / REMOTE_DIR 后重试。" >&2
  exit 1
fi

if [[ ! -f "$LOCAL_JPG" ]]; then
  echo "ERROR: local template not found: $LOCAL_JPG" >&2
  exit 1
fi

# 检查远程是否已存在 + 大小一致（幂等）
LOCAL_SIZE=$(stat -f%z "$LOCAL_JPG" 2>/dev/null || stat -c%s "$LOCAL_JPG")
REMOTE_SIZE=$(curl -sI "$URL" 2>/dev/null | awk '/[Cc]ontent-[Ll]ength/ {print $2}' | tr -d '\r')

if [[ "$REMOTE_SIZE" == "$LOCAL_SIZE" ]]; then
  echo "$URL"
  exit 0
fi

# 远程没有或大小不一致 → 重新上传
# 注: 某些云主机 sshd 配置会让 scp 失败，这里用 `ssh ... "cat > path"` 更稳
ssh "$IMGHOST_SSH" "mkdir -p $REMOTE_DIR && cat > $REMOTE_PATH" < "$LOCAL_JPG" >&2

# 验证
NEW_REMOTE_SIZE=$(curl -sI "$URL" 2>/dev/null | awk '/[Cc]ontent-[Ll]ength/ {print $2}' | tr -d '\r')
if [[ "$NEW_REMOTE_SIZE" != "$LOCAL_SIZE" ]]; then
  echo "ERROR: upload verification failed (local=$LOCAL_SIZE remote=$NEW_REMOTE_SIZE)" >&2
  exit 1
fi

echo "$URL"

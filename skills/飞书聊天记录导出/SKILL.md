---
name: 飞书聊天记录导出
description: 用飞书官方 lark-cli 把指定群聊的【原始】聊天记录导出成 Markdown，群里发的图片一并下载并内嵌进 .md（![](images/xxx) 能直接渲染）。只拿结构化原始记录，不做摘要/整理（总结是一句话的事，没必要进技能）。封装了 代码+API+固定流程 的复杂性，追求可复用、稳定。支持按群名或 chat_id 导出，支持增量 append。触发：'导出飞书群聊'/'把XX群聊天记录扒下来'/'飞书聊天记录导出'/'飞书群记录含图片'/给一个飞书群名说要原始记录。⚠️边界：只导出原始记录+图片，不总结、不下载非图片大文件（pdf/zip/mp4 保留为文本占位）。
---

# 飞书聊天记录导出（原始记录 + 图片内嵌）

**目的**：为了拿到结构化的聊天**原始**记录，需要 代码 + API + 固定流程，是件挺复杂的事。本技能把它封装成可复用、稳定的一步流程。**只产出原始记录**——总结/摘录是给 Agent 一句话就能做的事，不放进技能。

> **`SKILL_DIR`** = 本技能文件夹绝对路径：`<commands>/飞书聊天记录导出`
> 核心脚本：`${SKILL_DIR}/scripts/export_chat.py`，无外部 Python 依赖（仅标准库）。

## 它做什么 / 不做什么

- ✅ 分页拉全群历史消息 → 去重 → 按时间排序 → 渲染为逐条 Markdown（`**[时间] 发言人** 内容`）。
- ✅ 下载群里发的**图片**，存到 `images/`，并把正文里的 `[Image: img_xxx]` 占位改写成 `![](images/img_xxx.png/jpg)`，Markdown 渲染器/VS Code 预览能直接显示。
- ✅ 支持 `--append` 增量：只追加上次之后的新消息，不重复、不重排已有内容。
- ❌ **不做任何摘要/整理**。要总结？把产出的 .md 喂给 Agent 说"总结一下"即可。
- ❌ 不下载 pdf/zip/mp4 等大文件（保留 `<file .../>` 文本占位）——这些对 GitHub 太大，按约定不入库。

## 前置条件：lark-cli + 授权（一次性，需用户在浏览器完成）

这是飞书官方 CLI 的**交互式登录**，Agent 无法代替用户点击，必须把链接/二维码交给用户。

1. **安装**（若 `lark-cli --version` 失败）：
   ```bash
   npm install -g @larksuite/cli
   ```
   > Windows 上二进制常在 `%APPDATA%\npm\lark-cli`，若 PATH 没有，脚本会自动兜底查找。

2. **配置应用**（后台运行，会阻塞并打印验证 URL/二维码）：
   ```bash
   lark-cli config init --new
   ```
   用 `run_in_background: true` 跑它，从输出文件里取出 `https://open.feishu.cn/page/cli?...` 链接发给用户，让其在浏览器完成；命令 exit 0 即表示用户完成。

3. **用户身份登录**（读私有群聊**必须** user 身份；后台运行）：
   ```bash
   lark-cli auth login --recommend
   ```
   从输出取 `https://accounts.feishu.cn/oauth/...` 链接。**官方要求必须生成二维码并在回复里展示图片**：
   ```bash
   lark-cli auth qrcode "<verification_url 原样不改>" --output qr.png --size 320
   ```
   先贴 URL，URL 下方用 `![](qr.png)` 内嵌二维码，然后结束本轮、等用户回复"已完成"。授权时确保勾选**读取群信息 / 读取群消息**（`im:chat`、`im:message` 只读）。

4. **校验**：`lark-cli auth status` 中 `identities.user.available == true` 即就绪。脚本启动时也会自检，未登录会明确报错。

> 授权流程的踩坑细节（QR 必展示、URL 不可改、`--no-wait` 续轮询等）以 `lark-cli auth login` 的输出提示为准。

## 运行

按**群名**导出（脚本自动 `+chat-search` 解析 chat_id）：
```bash
python "${SKILL_DIR}/scripts/export_chat.py" --chat-name "aivc-data-paper" --out-dir <目标目录>
```

按 **chat_id** 导出（更稳，群重名时用）：
```bash
python "${SKILL_DIR}/scripts/export_chat.py" --chat-id oc_xxxxx --out-dir <目标目录>
```

**增量追加**（每次更新直接 append，只加新消息）：
```bash
python "${SKILL_DIR}/scripts/export_chat.py" --chat-id oc_xxxxx --out-dir <目标目录> --append
```

## 产物（写在 `--out-dir` 下）

```
<out-dir>/
├── 飞书群聊原始转录_<chat>.md   # 逐条原始记录；图片 ![](images/...) 内嵌
├── images/                      # 下载的图片（文件名 = <img_key>.<ext>）
└── .lark_export_state.json      # 增量状态（已见 message_id + 最后时间）
```

## 工作原理（封装掉的复杂度）

1. `auth status` 自检 user 身份。
2. `im +chat-search --query <名>` → chat_id；`im chat.members get` 补全偶尔缺失的发言人名。
3. `im +chat-messages-list --order asc --page-size 50 --no-reactions --download-resources` 循环翻页：
   - **关键坑**：CLI 偶尔在 JSON 前打印 `warning:` 行 → 脚本统一从第一个 `{` 起解析，避免解析失败导致 page_token 卡死。
   - `--no-reactions` 关闭 reaction 富集，减少上面那种 warning。
   - `--download-resources` 把图片落到临时 `lark-im-resources/`。
4. 按 message_id 去重、按 `(create_time, message_id)` 排序。
5. 用"实际下载文件名（带真实扩展名）"建 `img_key → 文件名` 映射，把 `[Image: key]` 改写为 `![](images/文件名)`，图片复制进 `images/`，临时目录清理。

## 复用要点

- **群名会变、可能重名** → 优先用 `--chat-id`（一次解析后固定下来）。
- **每次更新用 `--append`** → 拿原始增量，再交给 Agent 一句话总结即可（总结不进技能）。
- 脚本纯标准库、跨平台（Win/macOS/Linux），lark-cli 路径自动兜底。

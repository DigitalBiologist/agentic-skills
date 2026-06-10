# 快速阅读论文 — 配置指南

把一篇论文 PDF 生成一个**自包含的本地速读网页**:左侧 PDF.js 渲染原文,右侧按段落/章节/图表组织的中文极简讲解,开头一组核心词汇卡。整个文件夹可拷走/发人,Chrome 双击 `index.html` 即用,**无需服务器、无需联网**。

**完全免费、纯本地**,不调用任何付费 API。讲解由你的 agent(Claude / Codex / Gemini 等)亲自精读撰写。

---

## 1. 前置条件

| 依赖 | 用途 | macOS | Linux (Debian/Ubuntu) | Windows |
|------|------|-------|------|------|
| **Chrome** | 打开速读网页 + 渲染验证 | 官网下载 | 官网下载 | 官网下载（脚本会自动找 Chrome；如装在非标准位置，用 `CHROME_PATH` 环境变量指定） |
| **poppler** (`pdftotext`) | 从 PDF 抽全文 | `brew install poppler` | `sudo apt install poppler-utils` | `winget install oschwartz10612.Poppler`（或 choco / 手动，详见下方 Windows 段） |
| **Node.js** | 跑 `verify_render.js` 渲染验证 | `brew install node` | `sudo apt install nodejs` | 官网安装包 或 `winget install OpenJS.NodeJS` |
| **Python 3** | build.sh 内联 worker / 数页 | 系统自带 | 系统自带 | 装 [真 Python](https://www.python.org/downloads/) 或 miniconda（**不要靠 Windows Store 的 `python3` 别名**，那是占位符，会让脚本静默失败）|
| **bash shell** | 跑 `build.sh` | 系统自带 | 系统自带 | **Git Bash**（装 Git for Windows 自带）；不要用 PowerShell |

## 2. 配置环境变量

**无需任何环境变量、API Key 或账号。** 纯本地工具。

## 3. 安装依赖

```bash
# macOS
brew install poppler node
# Linux (Debian/Ubuntu)
sudo apt install poppler-utils nodejs
```

## 4. 放置文件

把整个 `快速阅读论文/` 文件夹放到你的 agent 技能目录:

```bash
# Claude Code
cp -r 快速阅读论文 ~/.claude/commands/

# 其他 runtime(按需)
# cp -r 快速阅读论文 ~/.codex/skills/
# cp -r 快速阅读论文 ~/.gemini/skills/
```

> ⚠️ SKILL.md 内的命令示例写的是 `~/.claude/commands/快速阅读论文/scripts/build.sh`。如果你装到别的目录,把这个前缀换成你的实际路径即可(`scripts/build.sh` 用 `$SKILL_DIR` 自动定位自身,本身不依赖固定路径)。

## 5. 测试

随便找一篇论文 PDF 跑一遍:

```bash
SKILL=~/.claude/commands/快速阅读论文
bash $SKILL/scripts/build.sh "~/Downloads/some-paper.pdf" "~/Desktop/速读-test"
# 脚手架就绪后,正常流程是 agent 填讲解;先直接验证渲染:
node $SKILL/scripts/verify_render.js "~/Desktop/速读-test"
# 期望输出 RENDER_OK,并生成 _render_check.png
```

## 6. 配置为技能

放进 `~/.claude/commands/` 后,Claude Code 会自动发现(凭 `SKILL.md` 的 frontmatter)。新开 session 后直接说"帮我快速读这篇论文 <PDF路径>"即可触发。

---

## 跨平台注意

脚本会**自动探测 Chrome 路径**（macOS / Linux / Windows 标准安装位置都覆盖）。如果你的 Chrome 装在非标准位置，设置环境变量 `CHROME_PATH` 指向 Chrome 可执行文件即可，例如：

```bash
CHROME_PATH="/opt/google/chrome/chrome" node scripts/verify_render.js <输出目录>
```

验证步骤只在渲染检查时用到 Chrome；生成的 `index.html` 本身用任何现代浏览器双击即可打开。

---

## Windows 用户必读

Windows 上踩过的坑（修了之后已无需手改脚本，但你的环境必须满足下列条件）：

### 1. 装 poppler

**推荐（最低摩擦）**：
```powershell
winget install oschwartz10612.Poppler
```
装完**重启 PowerShell / Git Bash** 让 PATH 生效，然后 `pdftotext -v` 能看到版本号即成功。

**备选**：[手动下载 release](https://github.com/oschwartz10612/poppler-windows/releases)，解压到 `C:\Program Files\poppler\`，把 `C:\Program Files\poppler\Library\bin` 加进系统 PATH。

### 2. 用 Git Bash 跑 build.sh（不是 PowerShell）

`build.sh` 是 bash 脚本，PowerShell 跑不了。安装 [Git for Windows](https://gitforwindows.org/) 后会自带 Git Bash。

```bash
# 在 Git Bash 里
bash /d/path/to/快速阅读论文/scripts/build.sh "/d/path/to/paper.pdf" "/d/path/to/output"
```

⚠️ **不要在 PowerShell 里调用 `bash xxx.sh`**：Windows 的 PATH 上的 `bash` 默认指向 WSL bash（`C:\Windows\system32\bash.exe`），路径风格和编码与 Git Bash 不同，会踩坑。**显式调用 Git Bash 的绝对路径**：`C:\Program Files\Git\bin\bash.exe`。

### 3. 确认你的 `python` 真的是 Python（不是 Store 占位符）

Windows 10/11 默认的 `python3` 命令往往是 Microsoft Store 的"占位符可执行文件"——`command -v python3` 会命中它，但一运行就立刻退出，**没有任何报错**。`build.sh` 现在会自动检测并跳过占位符，但你最好也确认本机至少有一个真 Python（推荐 [miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 [python.org 官方安装包](https://www.python.org/downloads/)）：

```powershell
python --version     # 应输出 "Python 3.x.y"
python3 --version    # 可能输出 Python 3.x.y，也可能立即退出 49（占位符）
```

只要 `python` 或 `python3` 或 `py` **任意一个**返回 `Python 3.x.x`，脚本就能用。

### 4. Chrome 自动探测

脚本会按下列顺序找 Chrome：

1. `CHROME_PATH` 环境变量
2. `C:\Program Files\Google\Chrome\Application\chrome.exe`
3. `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
4. `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`

都找不到时会报清晰错误。Chromium、Edge 等浏览器**不能**替代 Chrome（CDP 协议命令可能略有差异）。

### 5. 路径里的空格 / 中文

中文路径和空格在 Git Bash 里**只要用单引号或双引号包起来**就 OK；脚本本身已正确处理。**不要**在 PowerShell 里用 `bash -c "..."` 拼命令——PowerShell 把 UTF-16 字符串经 GBK 转给 bash.exe 会把中文字符损坏。

## 使用示例

1. **读一篇刚下载的论文** —— "帮我快速读这篇论文 ~/Downloads/nature-xxxx.pdf",agent 跑 build.sh → 精读全文 → 填讲解 → 验证渲染 → 给你产物目录。
2. **做成可分享的速读包** —— 产物整个文件夹拷给同事,对方 Chrome 双击 `index.html` 即看,无需任何环境。
3. **批量速读** —— 对多篇 PDF 分别生成,每篇一个独立目录。

## 工作原理(关键设计)

- **PDF → base64 内联**:PDF 写进 `assets/paper-data.js`,绕开 `file://` 下的 CORS,纯离线可用。
- **blob worker**:`file://` 下 PDF.js 默认 worker 会被浏览器拦截,模板内联 worker 源码、运行时起同源 blob worker 解决。
- **CDP 真实渲染验证**:`verify_render.js` 用真实事件循环等 canvas 画出来再截图,而不是 `--virtual-time-budget`(后者驱动不了 worker,截图会骗人)。

## 常见问题

**Q: 网页一直停在"正在渲染 PDF…"?**
A: 用 Chrome 打开(其他浏览器对 `file://` worker 策略不同)。仍不行就跑 `verify_render.js` 看报错。

**Q: 讲解卡片里图表页码对不上?**
A: PDF.js 物理页码从 1 开始,**≠ 印刷页脚页码**。很多期刊正文物理页 = 印刷页 + 1(首页是图示摘要)。徽章用物理页码。

**Q: 网页白屏?**
A: 多半是讲解内容里用了英文直双引号 `"` 截断了 JS 字符串。内容里的引号一律用中文「」或弯引号 `""`。填完跑 `verify_render.js` 或 `node --check` 自检。

**Q: 怎么升级 PDF.js?**
A: 同步替换 `vendor/pdf.min.js` 和 `vendor/pdf.worker.min.js`(同一版本号),其余不动。当前版本 3.11.174。

## 第三方组件

`vendor/` 下的 `pdf.min.js` / `pdf.worker.min.js` 是 [PDF.js](https://github.com/mozilla/pdf.js)(Mozilla,Apache-2.0),为离线可用一并打包。

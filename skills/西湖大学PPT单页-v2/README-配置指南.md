# 配置指南 — 西湖大学 PPT 单页生成 v2（Guomics 风格）

> 这是一个**自包含、可分享**的 Claude Code 技能：把"只写正文内容"的 layout 文件，渲染成西湖大学 v2 模板（Guomics 风格）的 4K PPT 单页 PNG。
>
> 端到端 pipeline：`wrapper + content 拼 prompt → 图生图（本地模板内联，无需图床）→ composite 合成橙弧/双 logo/页码`。
>
> 拿到本文件夹后，按下面 4 步配好即可使用。**本分享版已脱敏，不含任何作者的 API key / 私有路径 / 服务器信息**——你只需填上自己的生图 key。

---

## 1. 前置依赖

| 依赖 | 说明 |
|------|------|
| **Python 3** | 3.8+ 即可（脚本用 `python3` 调用） |
| **Python 包** | `requests`（调生图 API）、`numpy` + `Pillow`（composite 像素合成 / 加页码） |
| **生图 API key** | 默认 provider 为 **apiyi**（`api.apiyi.com`，模型 `gemini-3-pro-image`，Google-native 格式）。你需要一个自己的 key（也支持换成 laozhang / nanobanana，见第 3 步） |
| **macOS 字体（可选）** | 加页码优先用 `/System/Library/Fonts/Helvetica.ttc`，找不到自动退回 PIL 默认字体；非 macOS 也能跑，只是页码字体退化 |

安装 Python 包：

```bash
pip3 install requests numpy Pillow
```

---

## 2. 放置技能文件夹

把本文件夹整个放到你喜欢的位置即可（完全自包含、可移植，脚本内部用 `Path(__file__).parent` 自引用，不依赖任何固定机器路径）。两种常见放法：

- **当 Claude Code 技能用**：放进 `~/.claude/skills/`（或 `~/.claude/commands/`），Claude Code 会自动发现，按名字 / 触发词调用。
  ```bash
  cp -r 西湖大学PPT单页-v2 ~/.claude/skills/
  ```
- **当普通命令行工具用**：放哪都行，进文件夹记录绝对路径：
  ```bash
  cd 你放本技能的文件夹
  export SKILL_DIR="$(pwd)"
  ```

下文命令里的 `$SKILL_DIR` 就是本技能文件夹的绝对路径。

---

## 3. 配置生图 API key（关键一步）

技能默认用 **apiyi** provider。两种填 key 的方式，任选其一：

### 方式 A（推荐）：环境变量

```bash
export APIYI_API_KEY="你的apiyi key"
# 想长期生效，写进 ~/.zshrc 后 source 一下：
echo 'export APIYI_API_KEY="你的apiyi key"' >> ~/.zshrc && source ~/.zshrc
```

### 方式 B：写进配置文件

编辑 `image-api/provider_config.py`，把 `apiyi` 段里的 `api_key_default` 留空字符串填上你的 key：

```python
"apiyi": {
    ...
    "api_key_env": "APIYI_API_KEY",
    "api_key_default": "你的apiyi key",   # ← 填这里
    ...
},
```

> 环境变量优先级高于 `api_key_default`；两者都没填会直接报错退出。

### 想换别的 provider？

纯环境变量切换，不用改任何文件：

```bash
# 用 laozhang（OpenAI-style 代理）
IMAGE_PROVIDER=laozhang LAOZHANG_API_KEY=你的key python3 "$SKILL_DIR/generate_slide_v2.py" ...

# 用 nanobanana（异步轮询）
IMAGE_PROVIDER=nanobanana NANOBANANA_API_KEY=你的key python3 "$SKILL_DIR/generate_slide_v2.py" ...
```

---

## 4. 跑一页（冒烟测试）

准备一个 content 文件（只写"这一页要画什么"，格式见 `SKILL.md` 的「Content 文件格式」一节），然后：

```bash
python3 "$SKILL_DIR/generate_slide_v2.py" \
  <你的content文件.txt> \
  -p 4 \
  -o <输出目录>
```

成功后输出目录里会有三个文件：

- `p04_full_prompt.txt` — 完整 prompt 备份（不满意可手动改后重跑）
- `p04_raw.png` — 生图原图
- `p04_FINAL.png` — **最终交付图**（合成了橙弧 / 双 logo / 蓝角 / 页码）

生图约 60–120s。打开 `p04_FINAL.png` 核对：标题、数据、双 logo、页码、橙弧是否都对。

### 常用变体

```bash
# 不加页码（多页时最后统一加）
python3 "$SKILL_DIR/generate_slide_v2.py" <content> --no-page-number -o <out>

# 只重跑后处理、复用已有 raw（省钱省时，调页码/logo 用）
python3 "$SKILL_DIR/generate_slide_v2.py" <content> -p 4 -o <out> --skip-nbp
```

更多用法（批量多页、手动调 prompt 重跑、composite 内部逻辑、经验教训、质量自检清单）全在 **`SKILL.md`** 里。

---

## 故障排查

| 现象 | 处理 |
|------|------|
| `APIYI_API_KEY not set` / 直接退出 | key 没配。回到第 3 步，环境变量或 `api_key_default` 二选一填上 |
| HTTP 403 / `insufficient_user_quota` | 当前 provider 的额度/key 有问题。确认 `echo $APIYI_API_KEY` 非空且账号有余额；或换 provider（第 3 步） |
| `ModuleNotFoundError: requests/numpy/PIL` | 第 1 步的 `pip3 install requests numpy Pillow` 没装或装在别的 python 里 |
| 标题被套了深蓝 banner / logo 走样 | 正常现象，composite 后处理会强制覆盖橙弧/双 logo/分隔线；看 `p04_FINAL.png` 而不是 `p04_raw.png` |
| 页码字体不对（非 macOS） | 系统没有 Helvetica.ttc，自动退回 PIL 默认字体，功能正常 |

---

## 这个技能里有什么（文件清单）

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 技能正文：完整设计理念、content 格式、全部命令、经验教训 |
| `README.md` | 模板资产清单 + 模板视觉特征说明 |
| `generate_slide_v2.py` | ★ 端到端 pipeline 主入口 |
| `composite_v2.py` | 后处理：装饰层合成 + logo 像素级覆盖 + 加页码 |
| `add_page_number_v2.py` | 单独加页码（已被 composite 集成） |
| `wrapper_v2.txt` | 固定 prompt 包装，含 `{{CONTENT}}` 占位符 |
| `正文页模板_v2.png` / `_clean.png` / `_1080p.jpg` | 4K 模板原图 / clean 装饰层 / 1080p 参考图 |
| `sync_to_imghost_v2.sh` | （可选）自建图床上传，默认用不到；私有信息已脱敏为占位符 |
| `image-api/` | 内置生图 CLI（`image_generate.py` + `provider_config.py`） |

---

*分享版：API key、个人路径、私有服务器信息均已脱敏。用前填入你自己的生图 key 即可。*

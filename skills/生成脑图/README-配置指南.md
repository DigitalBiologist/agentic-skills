# 生成脑图 — 配置指南

把任意长文档（论文 / 综述 / 技术报告）转成**交互式 markmap 脑图**：单个自包含 HTML，浏览器打开即用。工具栏支持全展开/收缩、显示/隐藏详解（上下文感知）、L1–L5 层级跳转。

**完全免费、零本地依赖**，不调用任何付费 API。脑图内容由你的 AI agent（Claude / Codex / Gemini 等）读懂全文后结构化重写。

---

## 1. 前置条件

| 依赖 | 说明 |
|------|------|
| 现代浏览器（Chrome/Edge/Safari/Firefox） | 打开产物 HTML |
| **联网**（打开 HTML 时） | 产物通过 CDN（jsDelivr）加载 `d3` + `markmap-lib` + `markmap-view`。详见下方「离线化」 |

**无需** Node / Python / 任何安装，**无需** API Key 或环境变量。

## 2. 配置环境变量

无。纯前端 + CDN。

## 3. 安装依赖

无需安装。生成的 HTML 自带全部逻辑，运行时从 CDN 拉三个库。

## 4. 放置文件

```bash
# Claude Code（文件夹形式，含 SKILL.md）
cp -r 生成脑图 ~/.claude/commands/

# 或只取单文件当 slash command
cp 生成脑图/SKILL.md ~/.claude/commands/生成脑图.md
```

## 5. 测试

新开 Claude Code session 后输入：

> 对 https://arxiv.org/abs/1706.03762 生成脑图

或给定任意本地文档路径。Agent 会读全文 → 按层级规范写 Markdown → 生成 HTML → 提示你浏览器打开。打开后点工具栏各按钮验证交互。

## 6. 配置 Claude Code 技能

放进 `~/.claude/commands/` 后自动发现（凭 `SKILL.md` 的 frontmatter）。

**触发词**：`生成脑图` / `做脑图` / `mindmap` / `画个脑图` + 文档路径或内容。

---

## 使用示例

| # | 示例 | 说明 |
|---|------|------|
| 1 | `对这篇论文生成脑图` + 附上 PDF | 最常见的论文速读场景 |
| 2 | `把这份技术报告做成脑图` + 路径 | 技术文档结构化 |
| 3 | `对下面这段内容画个脑图` + 粘贴文本 | 任意文本直接转换 |
| 4 | `帮我把 CRISPR 综述做成 mindmap` + PDF | 综述类长文档尤其适合 |
| 5 | `第 3 章展开太细了，收一下` | 生成后的迭代微调 |

---

## 参数速查

这个技能没有命令行参数。它由 AI agent 自动执行，你只需要：

| 输入 | 说明 |
|------|------|
| **文档路径** | 本地 PDF / Markdown / 文本文件路径 |
| **文档内容** | 直接粘贴或引用文字 |
| **URL** | 论文链接（agent 会自行获取） |
| **调整指令** | 生成后可用自然语言调整层级/详解/样式 |

生成产物：单个 `xxx.html` 文件，双击即开。

---

## 离线化（可选）

产物默认联网加载 CDN。要完全离线，把这三个文件下载到 HTML 同级，并把 `<script src>` 改成本地相对路径：

```
https://cdn.jsdelivr.net/npm/d3@7
https://cdn.jsdelivr.net/npm/markmap-lib@0.15/dist/browser/index.js
https://cdn.jsdelivr.net/npm/markmap-view@0.15/dist/browser/index.js
```

## 核心规范（最容易踩的坑）

**概念名与详解必须分两层** —— 加粗概念名做父节点，解释做子节点：

```markdown
<!-- ❌ 错：同一节点，无法只折叠解释 -->
- **Michaelis-Menten 方程**：v = kcat*[E]*[S]/(KM+[S])

<!-- ✅ 对：父子两层，折叠父节点 = 隐藏解释、保留概念名 -->
- **Michaelis-Menten 方程**
  - v = kcat*[E]*[S]/(KM+[S])，酶催化反应速率核心公式
```

markmap 的最小折叠单位是节点；不分层就没法"只看概念名、隐藏详解"。

---

## 常见问题

**Q: 打开 HTML 一片空白 / 一直 loading？**
A: 多半是没联网（CDN 拉不到）。联网后刷新，或按上面「离线化」改本地库。

**Q: 工具栏「显示/隐藏详解」按钮没反应或行为怪？**
A: 技术栈必须用 `markmap-lib` + `markmap-view` **手动** `Markmap.create()` 并存实例到全局，**不能用 autoloader**（它丢弃实例，无法 JS 控制）。SKILL.md 有完整说明。

**Q: 折叠某个概念后，概念名也消失了？**
A: 说明概念名和解释写在了同一个节点。按上面「概念名与详解必须分两层」拆开。

**Q: 能在手机上用吗？**
A: 可以。生成的 HTML 是响应式的，手机上也能 pinch-zoom 和拖拽导航，但大屏体验更好。

**Q: 生成的脑图能导出图片/PDF 吗？**
A: markmap 本身不直接支持，但可以用浏览器的「打印 → 另存为 PDF」，或用截图工具。

---

## 第三方组件

运行时通过 CDN 加载 [markmap](https://github.com/markmap/markmap)（MIT）和 [D3](https://d3js.org)（ISC）。本仓库不打包它们的代码。

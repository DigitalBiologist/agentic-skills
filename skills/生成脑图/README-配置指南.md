# 生成脑图 — 配置指南

把任意长文档(论文 / 综述 / 技术报告)转成**交互式 markmap 脑图**:单个自包含 HTML,浏览器打开即用。工具栏支持全展开/收缩、显示/隐藏详解(上下文感知)、L1–L5 层级跳转。

**完全免费、零本地依赖**,不调用任何付费 API。脑图内容由你的 agent(Claude / Codex / Gemini 等)读懂全文后结构化重写。

---

## 1. 前置条件

| 依赖 | 说明 |
|------|------|
| 现代浏览器(Chrome/Edge/Safari/Firefox) | 打开产物 HTML |
| **联网**(打开 HTML 时) | 产物通过 CDN(jsDelivr)加载 `d3` + `markmap-lib` + `markmap-view`。详见下方「离线化」 |

**无需** Node / Python / 任何安装,**无需** API Key 或环境变量。

## 2. 配置环境变量

无。纯前端 + CDN。

## 3. 安装依赖

无需安装。生成的 HTML 自带全部逻辑,运行时从 CDN 拉三个库。

## 4. 放置文件

```bash
# Claude Code(文件夹形式,含 SKILL.md)
cp -r 生成脑图 ~/.claude/commands/

# 或只取单文件当 slash command
cp 生成脑图/SKILL.md ~/.claude/commands/生成脑图.md
```

## 5. 测试

新开 session 后:「对 <某篇文档/某段内容> 生成脑图」。agent 会读全文 → 按层级规范写 Markdown → 用 Write 生成 HTML → 提示你浏览器打开。打开后点工具栏各按钮验证交互。

## 6. 配置为技能

放进 `~/.claude/commands/` 后自动发现(凭 `SKILL.md` 的 frontmatter)。触发词:「生成脑图 / 做脑图 / mindmap / 画个脑图」+ 文档路径或内容。

---

## 离线化(可选)

产物默认联网加载 CDN。要完全离线,把这三个文件下载到 HTML 同级,并把 `<script src>` 改成本地相对路径:

```
https://cdn.jsdelivr.net/npm/d3@7
https://cdn.jsdelivr.net/npm/markmap-lib@0.15/dist/browser/index.js
https://cdn.jsdelivr.net/npm/markmap-view@0.15/dist/browser/index.js
```

## 核心规范(最容易踩的坑)

**概念名与详解必须分两层** —— 加粗概念名做父节点,解释做子节点:

```markdown
<!-- ❌ 错:同一节点,无法只折叠解释 -->
- **Michaelis-Menten 方程**：v = kcat*[E]*[S]/(KM+[S])

<!-- ✅ 对:父子两层,折叠父节点 = 隐藏解释、保留概念名 -->
- **Michaelis-Menten 方程**
  - v = kcat*[E]*[S]/(KM+[S]),酶催化反应速率核心公式
```

markmap 的最小折叠单位是节点;不分层就没法"只看概念名、隐藏详解"。

## 常见问题

**Q: 打开 HTML 一片空白 / 一直 loading?**
A: 多半是没联网(CDN 拉不到)。联网后刷新,或按上面「离线化」改本地库。

**Q: 工具栏「显示/隐藏详解」按钮没反应或行为怪?**
A: 技术栈必须用 `markmap-lib` + `markmap-view` **手动** `Markmap.create()` 并存实例到全局,**不能用 autoloader**(它丢弃实例,无法 JS 控制)。SKILL.md 有完整说明。

**Q: 折叠某个概念后,概念名也消失了?**
A: 说明概念名和解释写在了同一个节点。按上面「概念名与详解必须分两层」拆开。

## 第三方组件

运行时通过 CDN 加载 [markmap](https://github.com/markmap/markmap)(MIT)和 [D3](https://d3js.org)(ISC)。本仓库不打包它们的代码。

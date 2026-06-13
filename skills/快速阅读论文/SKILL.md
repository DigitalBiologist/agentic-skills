---
name: 快速阅读论文
description: 把一篇论文 PDF 生成一个自包含的本地速读网页——左侧 PDF 原文、右侧按段落/章节/图表组织的中文极简讲解，开头先用绿色词汇卡讲清核心术语。Claude 亲自精读全文撰写讲解（质量第一），不长篇翻译，重在快速抓住论文在讲什么。技术上：PDF 转 base64 内联 + blob worker（绕 file:// 限制），单文件夹双击即用、离线。触发：'快速阅读论文'/'论文速读'/'帮我快速读这篇论文'/'把这篇 PDF 做成速读网页'/'生成论文速读页'/给一个论文 PDF 路径说想快速读懂。
---

# 快速阅读论文 → 本地速读网页

## 目标

给定一篇论文 PDF，产出一个**自包含的本地 HTML 网页**：

- **左侧** PDF.js 渲染论文原文（逐页、可滚动缩放）。
- **右侧** 中文极简讲解，按论文段落/章节/图表组织，开头一组核心词汇卡。
- 右侧每张卡片有 `📄P#` 徽章，点击左侧 PDF 跳到对应页并高亮；导航条吸顶常驻；`A−/A+` 调讲解字号。
- 整个文件夹可拷走/发人，Chrome 双击 `index.html` 即用，**无需服务器、无需联网**。

讲解风格：**短、直接、便于扫读**。不做长篇翻译，每个大段配一两句话，每张图逐 panel(A/B/C…) 一句话。Claude **亲自精读全文**撰写（用户已定调：质量第一，不要丢给廉价 API 批量生成）。

## 工作流

### 1. 脚手架（机械步骤，一条命令）

```bash
bash ~/.claude/commands/快速阅读论文/scripts/build.sh "<论文PDF路径>" "<输出目录>"
# 例：build.sh "~/Downloads/paper.pdf" "~/Desktop/论文速读-XXX"
```

它会：拷 PDF、`pdftotext` 抽全文、将 PDF.js 库 / PDF base64 数据 / Worker 源码全部内联到 `index.html`，生成**纯离线自包含单文件**网页，并打印 PDF 物理页数。

产物结构：
```
<输出目录>/
├── index.html              ← 自包含速读网页（唯一需要打开的文件）
└── assets/
    ├── paper.pdf            ← 原始论文（留底）
    └── fulltext.txt         ← 全文提取（供 Claude 精读）
```

### 2. 精读（Claude 亲自做）

- `Read <输出目录>/assets/fulltext.txt` 通读全文，建立章节/图表结构。
- 用 `Read` 工具**直接读 PDF**（`pages` 参数，一次 ≤20 页）逐页看图，确认每个图/章节落在**第几物理页**。
  - ⚠️ **物理页码 ≠ 印刷页脚页码**。PDF.js 从 1 开始数物理页；很多期刊正文物理页 = 印刷页+1（首页是图示摘要）。徽章 `page` 用**物理页码**。
- 心里列出：核心词汇 → 摘要/引言 → 结果各部分(每图一卡) → 讨论 → 方法。

### 3. 填占位符（用 Edit 改 `index.html`）

- 顶部三处：`__中文标题__` / `__英文原标题__` / `__meta__`（作者·期刊·年份·DOI）。
- `const SECTIONS = [...]`：替换为真实讲解。四种卡片 kind：

| kind | 用途 | 形态 |
|---|---|---|
| `terms` | 开篇核心词汇卡（绿底，术语名换行加粗） | `{kind:"terms",page,t:"分组名",points:[[术语名（中英）,解释],…]}` |
| `lead` | 一句话核心 | `` {kind:"lead",page,html:`含<b>加粗</b>的HTML`} `` |
| `card` | 普通段落讲解 | `{kind:"card",page,t:"标题",points:[[小标签,说明],…]}` |
| `fig` | 图表讲解（黄底📊） | `{kind:"fig",page,t:"图N",points:[[panel,讲解],…]}` |

  开头建议放一个 `🔑 核心词汇（读前必看）` section，分「方法与工具/研究对象/核心概念」几组 `terms` 卡，把不懂就读不下去的术语先讲清楚（中英对照 + 大白话）。

### 4. 验证（必做，别靠肉眼假设）

```bash
node ~/.claude/commands/快速阅读论文/scripts/verify_render.js "<输出目录>"
```

它用真实 CDP 事件循环渲染，等 canvas 真画出来，输出 `RENDER_OK`/`RENDER_FAIL` 并存 `<输出目录>/_render_check.png`。然后 `Read` 那张截图，肉眼确认左 PDF、右讲解、词汇卡、布局都对。

> 顺手的语法自检：`node --check`（先把 `<script>…</script>` 抽出来），能在渲染前抓出引号问题。

## 关键踩坑（务必遵守，都是踩过的坑）

1. **引号陷阱**：`SECTIONS` 里内容字符串大多用英文双引号 `"…"` 包裹，所以**内容内部的引号一律用中文「」或弯引号 `""`**，绝不能用英文直双引号——否则提前截断 JS 字符串，整个网页白屏。填完务必 `node --check` 或 verify。

2. **file:// 下 Worker 被拦**：PDF.js 默认 `new Worker('./vendor/pdf.worker.min.js')` 在 `file://` 会被浏览器安全策略拒绝且不一定 fallback → 永远 loading。解法（模板已内置）：内联 worker 源码为 JS 字符串，运行时 `new Blob([code]) → URL.createObjectURL → workerSrc`，起**同源 blob worker**。

3. **headless 截图会骗人**：`chrome --headless --screenshot --virtual-time-budget` 驱动不了 Worker 线程，截图永远停在 loading。**必须用 `verify_render.js`（CDP 真实事件循环 + 轮询 canvas）**来验证，不要用 virtual-time 截图下结论。

4. **base64 内联**：PDF 不靠 `fetch` 本地文件（file:// CORS 拦），而是 base64 写进 `index.html`，运行时 `atob`→`Uint8Array`→`getDocument({data})`。所以单文件夹纯离线可用。

5. **布局**：标题/导航在**右栏开头**且导航条 `position:sticky` 吸顶（不占垂直高度，左右栏都用满 `100vh`）。`A−/A+` 只 `zoom` 讲解正文（`#guide-body`），不缩放标题。

## 文件清单

```
快速阅读论文/
├── SKILL.md                    # 本文档
├── template.html               # 网页骨架（CSS/JS/布局/全部 bug 修复 + 占位符）
├── vendor/
│   ├── pdf.min.js              # PDF.js 库（3.11.174，build 时内联到 index.html）
│   └── pdf.worker.min.js       # worker 源（build 时内联到 index.html）
└── scripts/
    ├── build.sh                # 脚手架：PDF → index.html（自包含单文件）
    └── verify_render.js        # CDP 真实渲染验证 + 截图（跨平台 Chrome 检测）
```

产物目录（每篇论文一个）：`index.html` + `assets/{paper.pdf,fulltext.txt}`，单 HTML 约 PDF 体积的 ~1.3 倍，**所有 CSS/JS/PDF数据/Worker 全部内联，零外部文件依赖，纯离线可用**。

## 离线设计要点

- **零 CDN**：PDF.js 库、样式表、所有前端脚本全部内联到 `index.html`，不引用任何境外或外部 URL。
- **file:// 兼容**：PDF 数据以 base64 内联（绕 `fetch` 本地文件的 CORS 限制）；Worker 通过 `Blob URL` 创建同源 worker（绕 `new Worker()` 本地文件安全限制）。
- **相对路径**：产物目录内全部使用相对路径引用，整文件夹拷到任意设备（Windows/macOS/Linux）直接双击 `index.html` 即可使用。
- **纯离线**：无网络环境（校园网断网、内网、隔离环境）下完全可用。

## 升级 PDF.js

换版本时同步替换 `vendor/pdf.min.js` 与 `vendor/pdf.worker.min.js`（同一版本号），其余不动。

## 卸载

`rm -rf ~/.claude/commands/快速阅读论文/`
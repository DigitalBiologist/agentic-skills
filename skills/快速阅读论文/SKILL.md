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

它会：拷 PDF、`pdftotext` 抽全文、PDF→base64 内联（`assets/paper-data.js`）、准备 `vendor/`（pdf.min.js + 内联 worker）、把 `template.html` 拷成 `index.html`，并打印 PDF 物理页数。

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
| `terms` | 开篇核心词汇卡（绿底，术语名换行加粗） | `{kind:"terms",page,t:"分组名",points:[[术语名（中英）,解释,"英文原文短语q"],…]}` |
| `lead` | 一句话核心 | `` {kind:"lead",page,html:`含<b>加粗</b>的HTML`,q:"英文原文短语"} `` |
| `card` | 普通段落讲解 | `{kind:"card",page,t:"标题",points:[[小标签,说明,"英文原文短语q"],…]}` |
| `fig` | 图表讲解（cream 底📊） | `{kind:"fig",page,t:"图N",points:[[panel,讲解,"英文原文短语q"],…]}` |

  开头建议放一个 `🔑 核心词汇（读前必看）` section，分「方法与工具/研究对象/核心概念」几组 `terms` 卡，把不懂就读不下去的术语先讲清楚（中英对照 + 大白话）。

#### q 字段（每条 li 末尾的可选字符串）—— Hover 反向定位

每个内容项**可选**带一个 `q` 字段（terms/card/fig 的 `points` 三元组里第三个元素；lead 顶层 `q` 字段）：用户 hover 那条卡片时，**左侧 PDF 自动滚到包含 q 的原文位置并黄底高亮**——把"讲解 → 原文取证"路径自动化。

写好 q 是这个功能落地的关键。规则：

- 从论文**英文原文**摘 5-30 字短语；论文 PDF 文本层是英文，中文同义句搜不到
- 优先选**独特词组**：专有名词组合、数字+单位、关键动词短语
- 避开：通用动词（show / find / propose）、希腊字母（α/β/μ）、特殊符号、跨行连字符（PDF 里行末的 `-` 后接换行常被拆开）
- 一句话能体现该 li 的核心论点；用户 hover 看到这一句就明白「对应原文这里」
- 缺 `q` 时不会报错——降级为现有的 📄P# 跳页行为，只是失去高亮

示例：

| 好 q | 为什么好 |
|---|---|
| `secologanin transporter SLTr` | 专有名词组合，独一无二 |
| `38 dedicated MIA pathway genes` | 数字 + 名词，命中精确 |
| `100 mM in idioblast` | 数字 + 单位 + 细胞类型 |
| `tandemly duplicated paralog` | 特征词组 |

| 坏 q | 为什么坏 |
|---|---|
| `the authors show that` | 通用，整篇命中无意义 |
| `In this study, we` | 同上，几乎每段都有 |
| `as expected` | 命中点散，定位不准 |
| `α-3',4'-Anhydrovinblastine` | 含特殊字符，PDF 文本层可能不一致 |

### 4. 验证（必做，别靠肉眼假设）

```bash
node ~/.claude/commands/快速阅读论文/scripts/verify_render.js "<输出目录>"
```

它用真实 CDP 事件循环渲染，等 canvas 真画出来，输出 `RENDER_OK`/`RENDER_FAIL` 并存 `<输出目录>/_render_check.png`。然后 `Read` 那张截图，肉眼确认左 PDF、右讲解、词汇卡、布局都对。

> 顺手的语法自检：`node --check`（先把 `<script>…</script>` 抽出来），能在渲染前抓出引号问题。

## 关键踩坑（务必遵守，都是踩过的坑）

1. **引号陷阱**：`SECTIONS` 里内容字符串大多用英文双引号 `"…"` 包裹，所以**内容内部的引号一律用中文「」或弯引号 `“”`**，绝不能用英文直双引号——否则提前截断 JS 字符串，整个网页白屏。填完务必 `node --check` 或 verify。

2. **file:// 下 Worker 被拦**：PDF.js 默认 `new Worker('./vendor/pdf.worker.min.js')` 在 `file://` 会被浏览器安全策略拒绝且不一定 fallback → 永远 loading。解法（模板已内置）：内联 worker 源码为 JS 字符串，运行时 `new Blob([code]) → URL.createObjectURL → workerSrc`，起**同源 blob worker**。

3. **headless 截图会骗人**：`chrome --headless --screenshot --virtual-time-budget` 驱动不了 Worker 线程，截图永远停在 loading。**必须用 `verify_render.js`（CDP 真实事件循环 + 轮询 canvas）**来验证，不要用 virtual-time 截图下结论。

4. **base64 内联**：PDF 不靠 `fetch` 本地文件（file:// CORS 拦），而是 base64 写进 `paper-data.js`，运行时 `atob`→`Uint8Array`→`getDocument({data})`。所以单文件夹纯离线可用。

5. **布局**：标题/导航在**右栏开头**且导航条 `position:sticky` 吸顶（不占垂直高度，左右栏都用满 `100vh`）。`A−/A+` 只 `zoom` 讲解正文（`#guide-body`），不缩放标题。

## 文件清单

```
快速阅读论文/
├── SKILL.md                    # 本文档
├── template.html               # 网页骨架（CSS/JS/布局/全部 bug 修复 + 占位符）
├── vendor/
│   ├── pdf.min.js              # PDF.js 库（3.11.174，缓存离线）
│   └── pdf.worker.min.js       # worker 源（build 时转 inline）
└── scripts/
    ├── build.sh                # 脚手架：PDF→assets/vendor/index.html
    └── verify_render.js        # CDP 真实渲染验证 + 截图
```

产物目录（每篇论文一个）：`index.html` + `assets/{paper.pdf,paper-data.js,fulltext.txt}` + `vendor/{pdf.min.js,pdf.worker.inline.js}`，约 PDF 体积的 ~1.3 倍。

## 升级 PDF.js

换版本时同步替换 `vendor/pdf.min.js` 与 `vendor/pdf.worker.min.js`（同一版本号），其余不动。

## 卸载

`rm -rf ~/.claude/commands/快速阅读论文/`

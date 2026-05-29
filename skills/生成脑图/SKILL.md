---
name: 生成脑图
description: "把任意长文档（论文/综述/技术报告）转成交互式 markmap 脑图（自包含 HTML，浏览器打开即用）。支持工具栏全展开/收缩 + 显示/隐藏详解（上下文感知，只展开用户已开的分支）+ L1-L5 层级跳转。Markdown 编写规范：概念名与详解必须分两层（加粗父节点 + 解释子节点），否则无法折叠详解。技术栈用 markmap-lib + markmap-view 手动 create（autoloader 不暴露实例），含完整踩坑记录。触发：'生成脑图'/'做脑图'/'mindmap'/'画个脑图'。"
---

# 生成脑图技能

将任意长文档（论文、综述、技术报告等）转化为交互式 markmap 脑图，支持展开/收缩/详解切换。

## 触发条件

用户说"做脑图"/"生成脑图"/"mindmap"/"画个脑图" + 文档路径或内容

## 输出

单个自包含 HTML 文件，浏览器打开即用，无需本地安装任何依赖。

---

## 核心架构

### 技术栈（踩坑验证后的最终方案）

```html
<!-- 必须用 markmap-lib + markmap-view 手动创建，不用 autoloader -->
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.15/dist/browser/index.js"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-view@0.15/dist/browser/index.js"></script>
```

**为什么不用 markmap-autoloader**：autoloader 不暴露 markmap 实例（`Markmap.create()` 的返回值被丢弃），导致无法通过 JS 控制展开/收缩。必须手动加载 lib + view，自己调用 `Markmap.create()` 并存储实例到全局变量。

### 文件结构

```
<html>
├── <style>        工具栏 + 布局样式
├── <div#toolbar>  控制按钮（展开/收缩/详解/层级）
├── <svg#mindmap>  markmap 渲染目标
├── <script#md-source type="text/template">  Markdown 内容
├── <script> CDN 加载 d3 + markmap-lib + markmap-view
└── <script> 初始化 + 控制函数
```

### 初始化代码模板

```javascript
window.addEventListener('load', function() {
  var mk = window.markmap;
  var transformer = new mk.Transformer();
  var md = document.getElementById('md-source').textContent;
  var result = transformer.transform(md);

  document.getElementById('loading').style.display = 'none';
  document.getElementById('toolbar').style.display = 'flex';

  window._mm = mk.Markmap.create('#mindmap', {
    colorFreezeLevel: 2,  // 前2层颜色固定，子节点继承
    maxWidth: 580,        // 节点最大宽度（px）
    initialExpandLevel: 2, // 初始展开层级
    duration: 200,         // 动画时长（ms）
  }, result.root);
});
```

---

## Markdown 内容编写规范

### 层级结构

```
# 文档标题 (L0 根节点)
## 1. 大章节 (L1)
### 1.1 小节 (L2)
- **概念名称** (L3 概念节点)
  - 详细解释文字 (L4 详解节点)
  - **子概念** (L4 子概念节点)
    - 子概念的解释 (L5 详解节点)
```

### 核心规则：概念名与详解必须分离

**这是最重要的规则**。每个概念必须拆成两层：加粗名称做父节点，解释做子节点。

```markdown
<!-- 错误：概念名和解释在同一个节点 -->
- **Michaelis-Menten 方程**：v = kcat*[E]*[S]/(KM+[S])，这是酶催化反应速率的核心公式

<!-- 正确：拆分为父子节点 -->
- **Michaelis-Menten 方程**
  - v = kcat*[E]*[S]/(KM+[S])，这是酶催化反应速率的核心公式
```

**为什么**：markmap 的最小折叠单位是节点。如果概念名和解释在同一个节点，用户无法只看概念名而隐藏解释。拆分后，折叠概念节点 = 隐藏解释但概念名仍可见。

### 适配用户知识水平的详解写法

详解不是简单的 bullet point，而是面向用户知识背景的解释：

```markdown
- **TMFA（热力学代谢通量分析）**
  - 标准FBA只看原子守恒不管热力学。TMFA加入约束：若ΔG>0就不允许正向通量。用混合整数线性规划(MILP)实现，消除了"化学计量可行但热力学不可能"的假解
```

原则：
- 先说这东西是什么/解决什么问题
- 再说核心机制（一句话）
- 最后给关键数字或意义
- 用户有基础但术语陌生时，用类比和白话穿插

### 子概念处理

当一个概念下有多个子概念时，子概念也用加粗：

```markdown
- **四大奠基发现**
  - **操纵子模型**
    - 揭示了基因如何被"开关"控制——一个调控蛋白同时控制一组功能相关基因
  - **遗传重组**
    - 发现细菌也能"交换"遗传信息
```

折叠"四大奠基发现"→隐藏所有子概念和解释，只保留"四大奠基发现"概念名。

---

## 控制函数实现

### 树遍历工具

```javascript
function walk(node, fn, depth) {
  if (!node) return;
  depth = depth || 0;
  fn(node, depth);
  if (node.children) {
    for (var i = 0; i < node.children.length; i++) {
      walk(node.children[i], fn, depth + 1);
    }
  }
}
```

### 全部展开 / 全部收缩

```javascript
function expandAll() {
  walk(mm.state.data, function(n) {
    if (!n.payload) n.payload = {};
    n.payload.fold = 0;
  });
  mm.renderData();
  setTimeout(function() { mm.fit(); }, 300);
}

function collapseAll() {
  walk(mm.state.data, function(n, d) {
    if (!n.payload) n.payload = {};
    n.payload.fold = (d >= 1) ? 1 : 0;  // 保留根节点展开
  });
  mm.renderData();
  setTimeout(function() { mm.fit(); }, 300);
}
```

### 展开到指定层级

```javascript
function expandTo(level) {
  walk(mm.state.data, function(n, d) {
    if (!n.payload) n.payload = {};
    n.payload.fold = (d >= level) ? 1 : 0;
  });
  mm.renderData();
  setTimeout(function() { mm.fit(); }, 300);
}
```

### 显示详解 / 隐藏详解（上下文感知）

**隐藏详解**：折叠 L3+ 的概念节点（隐藏解释），但保留 L1-L2 的展开状态不变。

```javascript
function hideDetails() {
  walk(mm.state.data, function(n, d) {
    if (d >= 3 && n.children && n.children.length > 0) {
      if (!n.payload) n.payload = {};
      n.payload.fold = 1;
    }
  });
  mm.renderData();
  setTimeout(function() { mm.fit(); }, 300);
}
```

**显示详解**：只在用户当前已展开的分支内展开详解。用户只打开了章节2，点击后只有章节2的详解展开。

```javascript
function showDetails() {
  function process(node, depth, isVisible) {
    if (!node || !isVisible) return;
    var folded = node.payload && node.payload.fold === 1;
    // 在详解层级(>=3)：可见但折叠的节点 → 展开它+所有后代
    if (depth >= 3 && folded && node.children) {
      node.payload.fold = 0;
      unfoldAll(node);
      return;
    }
    // 未折叠：递归进入可见子节点
    if (!folded && node.children) {
      for (var i = 0; i < node.children.length; i++) {
        process(node.children[i], depth + 1, true);
      }
    }
    // 在 depth<3 处折叠的：用户选择保持关闭，不动
  }
  function unfoldAll(node) {
    if (!node.children) return;
    for (var i = 0; i < node.children.length; i++) {
      var c = node.children[i];
      if (!c.payload) c.payload = {};
      c.payload.fold = 0;
      unfoldAll(c);
    }
  }
  process(mm.state.data, 0, true);
  mm.renderData();
  setTimeout(function() { mm.fit(); }, 300);
}
```

**上下文感知的关键逻辑**：
- `isVisible` 追踪节点是否在屏幕上可见（所有祖先都未折叠）
- depth < 3 且折叠的节点 → 用户主动关闭了该章节，不动
- depth >= 3 且可见且折叠 → 展开显示详解
- depth >= 3 但不可见（祖先折叠）→ 跳过，不影响

---

## 工具栏 UI

```html
<div class="toolbar">
  <button class="primary" onclick="expandAll()">全部展开</button>
  <button class="warn" onclick="collapseAll()">全部收缩</button>
  <div class="sep"></div>
  <button onclick="showDetails()">显示详解</button>
  <button onclick="hideDetails()">隐藏详解</button>
  <div class="sep"></div>
  <span class="label">层级:</span>
  <button onclick="expandTo(1)">L1</button>
  <button onclick="expandTo(2)">L2</button>
  <button onclick="expandTo(3)">L3</button>
  <button onclick="expandTo(4)">L4</button>
  <button onclick="expandTo(5)">L5</button>
</div>
```

样式要点：
- `position: fixed; top: 0` 固定在顶部
- `backdrop-filter: blur(8px)` 半透明毛玻璃效果
- 白色背景 `background: #ffffff`（用户偏好）

---

## 执行流程

### 第一步：读取文档

完整读取源文档。对于长文档分多次读取确保不遗漏。

### 第二步：创建输出目录

在文档同级或上级创建 `mindmap/` 文件夹：
```bash
mkdir -p /path/to/project/mindmap
```

### 第三步：编写 Markdown 脑图内容

按照上述层级结构和编写规范，将文档内容转化为 Markdown 大纲。

**信息完整性要求**：
- 文档中的每一个关键概念、数据、方法、结论都必须出现
- 不是摘要，是完整的结构化重组
- 详解部分要真正讲懂概念，不是复述原文

**质量检查清单**（写完后核对）：
- [ ] 所有关键术语/方法名都出现
- [ ] 所有关键数字/指标都保留
- [ ] 所有人名/团队/数据库都提及
- [ ] 每个加粗概念都有对应的详解子节点
- [ ] 层级结构清晰（L0-L5 分布合理）

### 第四步：组装 HTML

用 Write 工具生成完整 HTML 文件（参照本技能的代码模板）。

### 第五步：浏览器打开测试

```bash
open /path/to/mindmap/output.html
```

### 第六步：迭代

用户反馈后快速修改。常见迭代：
- 某个分支展开太细/太粗 → 调整 Markdown 层级
- 某个概念解释不清 → 改写详解子节点
- 缺少某个信息 → 补充到对应位置
- 样式调整 → 修改 CSS 或 markmap 配置

---

## 踩坑记录

### 1. autoloader 不暴露实例（致命）
markmap-autoloader 内部调用 `Markmap.create()` 但不存储返回值，也不挂到 DOM 元素上。因此**必须手动加载 lib + view，自己 create 并保存实例**。

### 2. 概念名与详解不分离导致无法切换
如果 `**Name**: explanation` 写在同一行，markmap 渲染为单个节点，无法折叠掉 explanation 只保留 Name。**必须拆成父子两个节点**。

### 3. `<textarea>` vs `<script type="text/template">`
两种都可以存放 Markdown 内容。`<script type="text/template">` 更干净（不创建 DOM 元素），但如果内容中有 `</script>` 会断裂。实际文档内容不太可能包含这个字符串，所以用 `<script>` 即可。

### 4. fold 属性的语义
`node.payload.fold = 1` 表示折叠（隐藏子节点），`0` 或 `undefined` 表示展开。修改后必须调用 `mm.renderData()` 生效，`mm.fit()` 自适应视口。

### 5. 详解切换必须上下文感知
用户只展开了部分章节，点"显示详解"不应该展开所有章节。实现方式：递归时追踪 `isVisible`，对 depth<3 且折叠的节点不递归进入。

### 6. `mm.fit()` 需要延迟
`renderData()` 后 DOM 更新有延迟，立即 `fit()` 可能基于旧布局。加 `setTimeout(fn, 300)` 确保布局完成后再适配视口。

---

## 参考实现 / 验收

生成后用浏览器打开，逐项验证：

- 工具栏「全部展开 / 全部收缩」「显示详解 / 隐藏详解」「L1–L5」都生效；
- 每个加粗概念节点**折叠后只剩概念名、展开后显示详解子节点**（若折叠后概念名连同解释一起消失，说明没分两层，按上面「概念名与详解必须分离」规范改）；
- 上下文感知：只展开了部分章节时点「显示详解」，只应展开已打开分支内的详解，不应把所有章节都展开。

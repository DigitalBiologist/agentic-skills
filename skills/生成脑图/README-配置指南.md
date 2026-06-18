# 生成脑图 — 配置指南

把任意长文档(论文 / 综述 / 技术报告)转成**交互式 markmap 脑图**:单个自包含 HTML,浏览器打开即用。工具栏支持全展开/收缩、显示/隐藏详解(上下文感知)、L1–L5 层级跳转。

**完全免费、纯离线**,不调用任何付费 API。脑图内容由你的 agent(Claude / Codex / Gemini 等)读懂全文后结构化重写。

---

## 1. 前置条件

| 依赖 | 用途 | 安装 |
|------|------|------|
| **Python 3** | build.sh 内联 vendor JS 到 HTML | macOS/Linux 自带 |
| 现代浏览器(Chrome/Edge/Safari/Firefox) | 打开产物 HTML | 任意 |
| Bash | 执行 build.sh | macOS/Linux 自带；Windows 用 Git Bash |

**无需** Node / 任何安装,**无需** API Key 或环境变量。**生成和查看均无需联网**。

## 2. 配置环境变量

无。纯本地工具。

## 3. 安装依赖

无需安装任何 npm/pip 包。`vendor/` 已预打包 d3.js v7 + markmap-lib v0.15 + markmap-view v0.15 浏览器构建，`build.sh` 自动内联。

## 4. 放置文件

把整个 `生成脑图/` 文件夹放到你的 agent 技能目录:

```bash
# Claude Code
cp -r 生成脑图 ~/.claude/commands/

# 其他 runtime(按需)
# cp -r 生成脑图 ~/.codex/skills/
# cp -r 生成脑图 ~/.gemini/skills/
```

> ⚠️ SKILL.md 内的命令示例写的是 `~/.claude/commands/生成脑图/scripts/build.sh`。如果你装到别的目录,把这个前缀换成你的实际路径即可(`scripts/build.sh` 用 `$SKILL_DIR` 自动定位自身,本身不依赖固定路径)。

## 5. 测试

随便找一段文字跑一遍:

```bash
SKILL=~/.claude/commands/生成脑图
# 写一小段 Markdown 测试内容
cat > /tmp/test-mindmap.md << 'EOF'
# 测试脑图
## 第一章
- **概念A**
  - 这是概念A的解释
- **概念B**
  - 这是概念B的解释
EOF
# 生成
bash $SKILL/scripts/build.sh "测试" /tmp/test-mindmap.md /tmp/test-mindmap.html
# 浏览器打开验证
open /tmp/test-mindmap.html
```

验证：全部展开/收缩、显示/隐藏详解、L1-L5 层级跳转按钮均正常工作。**同时断开网络测试纯离线可用**。

## 6. 配置为技能

放进 `~/.claude/commands/` 后自动发现(凭 `SKILL.md` 的 frontmatter)。触发词:「生成脑图 / 做脑图 / mindmap / 画个脑图」+ 文档路径或内容。

---

## 离线设计

**默认纯离线，无需配置。** 所有 JS 库（d3.js + markmap-lib + markmap-view）已预下载到 `vendor/` 目录，`build.sh` 生成时自动内联到单个 HTML 文件中。产物零外部依赖，校园网、断网、内网环境均可正常使用。

如果需要升级库版本，替换 `vendor/` 下的对应文件即可（同一版本号的 lib + view 需同步替换）。

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
A: 检查 `template.html` 中的占位符是否被正确替换（`__D3_CODE__` / `__MARKMAP_LIB_CODE__` / `__MARKMAP_VIEW_CODE__` / `__MARKDOWN_CONTENT__`）。重新运行 `build.sh` 确保内联成功。

**Q: 工具栏「显示/隐藏详解」按钮没反应或行为怪?**
A: 技术栈必须用 `markmap-lib` + `markmap-view` **手动** `Markmap.create()` 并存实例到全局,**不能用 autoloader**(它丢弃实例,无法 JS 控制)。SKILL.md 有完整说明。

**Q: 折叠某个概念后,概念名也消失了?**
A: 说明概念名和解释写在了同一个节点。按上面「概念名与详解必须分两层」拆开。

**Q: 如何升级 markmap / d3 版本?**
A: 同步替换 `vendor/d3.min.js`、`vendor/markmap-lib.min.js`、`vendor/markmap-view.min.js`（lib + view 必须同一版本号），其余不动。当前版本：d3 v7.9.0 + markmap v0.15.5。

## 第三方组件

`vendor/` 下的 JS 库均为预下载的浏览器构建版本：
- [d3.js](https://d3js.org) v7（ISC License）
- [markmap-lib](https://github.com/markmap/markmap) v0.15（MIT License）
- [markmap-view](https://github.com/markmap/markmap) v0.15（MIT License）

所有库在 `build.sh` 运行时内联到产物 HTML，**用户打开脑图时不发起任何网络请求**。
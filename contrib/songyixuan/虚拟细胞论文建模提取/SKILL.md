---
name: 虚拟细胞论文建模提取
description: 将单篇 E. coli/细菌虚拟细胞、代谢工程、代谢网络、调控网络或组学论文提取为“可建模信息”的交互式 markmap HTML：研究对象、菌株/基因型、培养条件、通路、基因/酶/反应、代谢物、实验数据、可转成模型约束的假设、不能直接建模的边界和下一步参数缺口。触发：虚拟细胞论文建模提取、论文建模提取、从论文提取建模信息、把这篇论文转成虚拟细胞建模信息。
---

# 虚拟细胞论文建模提取

把一篇论文转成面向虚拟细胞建模的证据图谱，而不是普通摘要。最终产物必须是一个可打开的交互式 `markmap` HTML。

## 输入

- 一篇论文 PDF、全文文本、网页链接或用户粘贴的论文内容。
- 可选：目标模型范围，如 `E. coli iML1515`、嘌呤代谢子模型、中心碳代谢、调控网络、酶约束模型。
- 可选：输出目录。未指定时在论文旁边创建 `modeling-extraction/`。

## 输出

生成一个自包含或半自包含的 HTML：

```text
<输出目录>/
└── <paper_slug>_modeling_extraction_markmap.html
```

HTML 中必须包含：

- markmap 脑图。
- 工具栏：全部展开、全部收缩、显示/隐藏详解、L1-L5 层级跳转。
- 标题区：论文题名、年份、DOI/来源、建模目标。
- 一段简短的“建模可用性判断”。

## 工作流

1. **读取论文**
   - 先确认题名、作者、年份、DOI、文章类型。
   - 如果是 PDF，提取全文并检查关键图表页；不要只读摘要。
   - 标记论文是 original article、review、protocol、model paper 还是 data/resource paper。

2. **抽取建模实体**
   - 菌株/物种：如 `E. coli K-12 MG1655`、工程菌株编号、突变背景。
   - 条件：培养基、碳源、氧条件、温度、时间点、补料方式。
   - 基因/蛋白：基因名、酶名、是否 knockout/overexpression/attenuation/mutation。
   - 代谢物：底物、产物、前体、中间体、副产物、能量/辅因子。
   - 通路：中心碳、PPP、TCA、嘌呤、氨基酸、转运、调控网络等。
   - 数据：产量、得率、速率、OD、生长率、组学 fold-change、代谢物浓度、flux。

3. **转换成建模语言**
   - 可直接建模：knockout、exchange bound、objective、sink/demand、reaction bound、medium。
   - 需要近似：overexpression、promoter weakening、transporter engineering、regulation、enzyme complex、protein-protein interaction。
   - 暂不能建模：缺参数、缺反应 ID、跨物种机制、只在综述中出现且无 E. coli 证据。

4. **建立 markmap 层级**
   - L0：论文题名 + 建模任务。
   - L1：论文定位、研究对象、可建模实体、实验数据、模型假设、模型操作、边界风险、参数缺口、下一步。
   - L2-L3：具体通路、基因、代谢物、数据项。
   - L4-L5：解释和证据来源。

5. **生成 HTML**
   - 使用 `markmap-lib` + `markmap-view` 手动 `Markmap.create()`。
   - 不使用只自动加载、无法控制实例的 autoloader。
   - 工具栏必须能控制展开/收缩和层级。

6. **验证**
   - 用浏览器或 Playwright 打开 HTML。
   - 检查 `loading` 消失、工具栏可见、SVG 节点生成、正文无明显乱码。
   - 人工核对至少 8 个原文事实：题名、菌株、关键基因、关键代谢物、关键数值、图表位置、建模假设、限制条件。

## markmap 内容模板

```markdown
# <论文题名>：虚拟细胞建模提取

## 1. 论文定位
### 1.1 文章类型
- **Original article / Review / Model paper**
  - 为什么这样判断。
### 1.2 建模价值
- **可直接用于模型的部分**
  - knockout、reaction、medium、flux、产量等。

## 2. 研究对象与条件
### 2.1 菌株/物种
- **<strain>**
  - 基因型、背景、用途。
### 2.2 培养条件
- **<medium / carbon source / oxygen>**
  - 对模型约束的影响。

## 3. 可建模实体
### 3.1 基因/蛋白
- **<gene>**
  - 作用、论文证据、可能模型操作。
### 3.2 代谢物
- **<metabolite>**
  - 通路位置、数据、模型表示。
### 3.3 通路/反应
- **<pathway or reaction>**
  - 可能 reaction ID 或需要查证的 ID。

## 4. 实验数据
### 4.1 定量数据
- **<value>**
  - 单位、条件、原文位置。
### 4.2 组学/表型数据
- **<omics / phenotype>**
  - 如何转化成模型约束或验证项。

## 5. 可转成模型的假设
### 5.1 直接假设
- **<hypothesis>**
  - 推荐模型操作。
### 5.2 近似假设
- **<hypothesis>**
  - 为什么只能近似。

## 6. 边界与缺口
### 6.1 不能直接表达的机制
- **调控/互作/动态**
  - 普通 FBA 的限制。
### 6.2 需要补充的参数
- **<parameter>**
  - 推荐查找来源。

## 7. 下一步建模建议
### 7.1 最小可行模型
- **第一轮模拟**
  - 可立即执行的模型设置。
```

## 质量标准

- 输出要面向建模，不要写成文学性摘要。
- 每个重要假设都要标注“直接建模 / 近似建模 / 暂不能建模”。
- 数值必须带单位和条件；不确定就写“需回原文确认”。
- 对综述文章要特别标注证据是否可直接套到 E. coli。
- 最终 HTML 能双击或浏览器打开。

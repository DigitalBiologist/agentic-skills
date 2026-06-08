---
name: 代谢工程改造清单生成
description: 从代谢工程论文或工程菌株描述中生成可用于 E. coli 虚拟细胞/FBA/COBRA 模型的改造清单，并以交互式 markmap HTML 展示：基因删除、过表达、弱化、转运体工程、培养条件、目标产物、可能 reaction/GPR、可直接模拟项、需近似项、风险和验证读数。触发：代谢工程改造清单生成、工程菌株转模型清单、从论文生成FBA改造清单、把代谢工程论文转成模型操作。
---

# 代谢工程改造清单生成

把工程菌株构建路线翻译成模型操作语言。最终展示形式必须是交互式 markmap HTML。

## 输入

- 一篇代谢工程论文、工程菌株段落、菌株构建表、或用户给出的改造列表。
- 可选目标模型：`iML1515`、`iJO1366`、`EcoCyc`、`BiGG`、自定义模型。
- 可选目标产物：如 guanosine、succinate、lysine、ethanol 等。

## 输出

```text
<输出目录>/
└── <project_slug>_engineering_to_model_markmap.html
```

HTML 必须包含：

- 交互式 markmap。
- 工具栏：展开/收缩、详解开关、L1-L5。
- 一张“模型操作优先级”节点：先做哪些 knockout/medium/objective，再做哪些近似。

## 工作流

1. **识别工程目标**
   - 目标产物、宿主菌、母本菌株、最终菌株。
   - 摇瓶/发酵罐/补料条件。
   - 关键评价指标：titer、yield、productivity、growth、byproduct。

2. **拆解改造类型**
   - knockout/deletion：可优先映射为 gene knockout 或 reaction knockout。
   - overexpression：普通 FBA 中通常只能近似为 lower bound 提升、enzyme capacity 提升或备注。
   - attenuation/weakening：可近似为上界降低，但需标注不确定性。
   - transporter engineering：可近似为 export/sink/exchange bound，但需区分天然反应与人为构造。
   - promoter/RBS/point mutation：一般不能直接用普通 FBA 表达，需标为近似或后续酶约束模型。

3. **映射模型对象**
   - 基因：标准化 gene symbol。
   - 反应：给出候选 reaction name/ID；不确定时写“候选，需查 BiGG/EcoCyc”。
   - 代谢物：写清胞内/胞外位置。
   - GPR：若已知，说明基因到反应的关系。

4. **生成模拟分组**
   - Baseline：野生型或母本模型。
   - Stepwise：按论文菌株构建顺序逐步添加改造。
   - Final strain：最终工程菌。
   - Sensitivity：对弱化/过表达/转运体近似做参数扫描。

5. **生成 markmap**
   - 不要输出纯表格结束；必须生成可打开的交互式 HTML。
   - 表格信息可以变成 markmap 节点：改造类型、模型操作、证据、风险。

6. **验证**
   - 浏览器打开 HTML，确认 markmap 节点生成。
   - 至少核对 6 个工程事实：最终菌株、目标产物、关键 deletion、关键 overexpression、关键数值、培养条件。

## markmap 模板

```markdown
# <目标产物/菌株>：代谢工程改造清单

## 1. 工程目标
### 1.1 宿主与产物
- **宿主**
  - <strain>
- **目标产物**
  - <product, compartment, unit>
### 1.2 关键指标
- **titer / yield / productivity**
  - 原文数值、条件、时间。

## 2. 改造总览
### 2.1 knockout
- **<gene>**
  - 目的、对应通路、模型操作。
### 2.2 overexpression
- **<gene>**
  - 目的、FBA 近似方式、风险。
### 2.3 attenuation
- **<gene>**
  - 竞争分支、建议 bound 扫描。
### 2.4 transporter
- **<gene/transporter>**
  - export/sink/exchange 近似。

## 3. 模型映射
### 3.1 genes
- **<gene>**
  - possible GPR / reaction candidates。
### 3.2 reactions
- **<reaction>**
  - candidate ID、方向、上下界建议。
### 3.3 metabolites
- **<metabolite>**
  - compartment、是否需要 demand/export。

## 4. 模拟方案
### 4.1 baseline
- **模型设置**
  - medium、objective、exchange bounds。
### 4.2 stepwise strains
- **<strain step>**
  - 添加哪些改造，看哪些 readouts。
### 4.3 final strain
- **最终模型**
  - knockout + bounds + objective/readouts。

## 5. 不确定性与风险
### 5.1 普通 FBA 不能直接表达
- **表达量/调控/酶复合体**
  - 近似方案。
### 5.2 需要补充数据
- **参数缺口**
  - 文献或实验数据来源。

## 6. 输出给建模人员的待办
### 6.1 立即可做
- **任务**
  - 具体模型操作。
### 6.2 需查证
- **任务**
  - reaction ID、GPR、方向性。
```

## 质量标准

- 不编造反应 ID；不确定时给候选和查证任务。
- 区分“实验改造”和“模型近似”。
- 对每个工程步骤说明预期影响的通路方向。
- 最终 HTML 必须能打开并显示 markmap。

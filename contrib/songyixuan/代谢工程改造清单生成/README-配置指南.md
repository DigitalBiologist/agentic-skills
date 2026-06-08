# 代谢工程改造清单生成 - 配置指南

## 前置条件

- 可读取论文或菌株构建描述。
- 若要映射到具体模型，建议准备 BiGG、EcoCyc 或 COBRA 模型文件。

## 放置方式

```bash
cp -r skills/代谢工程改造清单生成 ~/.claude/commands/
```

## 使用示例

```text
用「代谢工程改造清单生成」把 Zhang 2024 鸟苷工程论文转成 iML1515 模型改造清单，并输出 markmap HTML。
```

```text
根据这个工程菌株构建表，生成 knockout、overexpression、attenuation 和 transporter 的模型操作脑图。
```

## 输出检查

- HTML 能打开，markmap 工具栏可用。
- 每个改造都标注“可直接建模 / 需近似 / 需查证”。
- 关键产量、菌株和培养条件已核对。

## 常见问题

- 过表达不能简单等于 flux 增大，除非有额外酶容量或通量数据。
- 转运体工程常需要用 export/sink 近似，必须标注该近似。
- 弱化表达建议做上下界敏感性扫描，而不是给单一确定值。

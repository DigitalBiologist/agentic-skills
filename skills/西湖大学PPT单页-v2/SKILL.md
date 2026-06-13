---
name: 西湖大学PPT单页-v2
description: 【PPT生成】把"只写正文内容"的 layout 文件渲染成西湖大学 v2 模板（Guomics 风格）的 4K PPT 单页 PNG。端到端 pipeline：wrapper+content 拼 NBP prompt → 图生图（默认本地模板内联，无需图床）→ composite 合成橙弧/双logo/页码。触发词：'西湖 ppt v2'/'西湖 v2'/'pptv2'/'按 Guomics 模板生成 PPT'/'Guomics 风格 PPT'/'跑一页西湖 PPT'/'用西湖大学 v2 模板出图'。⚠️ 边界：只做单页（多页逐页跑）；需自配生图 API key（默认 provider apiyi，设 APIYI_API_KEY）+ Python 包 requests/numpy/Pillow；不做内容近似化/扩写（假设 content 已定稿）。
---

# 西湖大学 PPT 模板单页生成 v2（Guomics 风格）

> 端到端 pipeline：把"只描述正文内容"的 layout 文件渲染成西湖大学 v2 模板的 4K PPT 单页 PNG。
>
> **本技能自包含**：所有脚本/模板/NBP 生图 CLI 都在本文件夹内，路径自引用，不依赖 `~/.claude`。

## 路径约定

`SKILL_DIR` = **你把本技能文件夹放置的绝对路径**（自己 clone / 解压到哪就是哪），例如：
`~/.claude/skills/西湖大学PPT单页-v2` 或 `~/skills/西湖大学PPT单页-v2`。

进入该文件夹执行一次即可拿到绝对路径并 export 给下文命令复用：

```bash
cd <你放本技能的文件夹>
export SKILL_DIR="$(pwd)"
```

下文命令里的 `$SKILL_DIR` 即指此路径。脚本内部已用 `Path(__file__).parent` 自引用 wrapper / 模板 / composite / 收编的 image-api，**你只要给对 `generate_slide_v2.py` 的路径**，其余它自己找——本技能完全自包含、可移植，不依赖任何固定机器路径。

---

## ⚡ QUICK START（直接执行，不用读全文）

如果用户给了 content 文件 + 页码，**一行命令搞定**（默认本地模板内联，无需图床）：

```bash
python3 "$SKILL_DIR/generate_slide_v2.py" \
  <content文件绝对路径> \
  -p <页码数字> \
  -o <输出目录绝对路径>
```

前提：你已配置自己的生图 API key（默认 provider `apiyi`，设 `APIYI_API_KEY`；详见 `README-配置指南.md` 与下方「外部前置依赖」）。

执行完输出三个文件到输出目录：
- `p<NN>_full_prompt.txt` — 完整 NBP prompt（备份，可手动改后重跑）
- `p<NN>_raw.png` — NBP 原图
- `p<NN>_FINAL.png` — **最终交付图**（合成模板装饰 + 像素级 logo + 加页码）

NBP 调用约 60-120s，可 `run_in_background: true` 等通知。完成后用 Read 看 `p<NN>_FINAL.png`，跟用户报：标题 / 数据 / logo / 页码 / 橙弧是否都对。

**不需要 codex 加工、不需要手动拼 prompt、不需要单独管页码**——一行全部包办。

---

## 外部前置依赖（学习时确认：NBP 已整套收编进本技能）

| 依赖 | 状态 | 说明 |
|------|------|------|
| **NBP 生图 CLI** | ✅ 内置 | `image-api/image_generate.py` + `provider_config.py` 在本文件夹内，路径自引用，无需任何外部安装 |
| **图生图小工具** | ✅ 内置 | `image-api/edit_local.sh <输入图> <输出图> "<prompt>" [宽高比]`：本地图传 tmpfiles 临时图床(1h) → NBP 图生图编辑。路径已自引用，需联网（连 tmpfiles），单次约 3-4 分钟注意 timeout；用 nanobanana provider，key 读环境变量 |
| **生图 API key** | ⚠️ 需自配 | **默认 provider 为 `apiyi`**（`api.apiyi.com`，`gemini-3-pro-image`，Google-native）。用前设你自己的 key：`export APIYI_API_KEY=<你的key>`（推荐写进 `~/.zshrc`），或把 key 填进 `image-api/provider_config.py` 的 `api_key_default`。**本分享版已脱敏，不含任何作者 key**。想换 provider：`IMAGE_PROVIDER=laozhang LAOZHANG_API_KEY=...` 或 `IMAGE_PROVIDER=nanobanana NANOBANANA_API_KEY=...`（纯环境变量切换，不改文件）。配置细节见 `README-配置指南.md`。 |
| **Python 包** | ⚠️ 需安装 | `requests`（NBP 网络）、`numpy` + `Pillow`（composite 像素合成 / 加页码）。`pip3 install requests numpy Pillow` |
| **macOS 字体** | 自动降级 | composite 加页码优先用 `/System/Library/Fonts/Helvetica.ttc`，找不到自动退 PIL 默认字体 |
| **自建图床** | ❌ 默认不用 | 仅 `--use-imghost` 时才需要。原作者私有云主机信息已脱敏为占位符，见 `sync_to_imghost_v2.sh` |

> **参考图：本地内联 vs 图床**——本技能 `generate_slide_v2.py` **默认**把本地 `正文页模板_v2_1080p.jpg` 直接喂给 NBP（`provider_config.py` 会自动 base64 内联），**完全不需要公网图床**。旧的阿里云图床路线仅作可选 fallback（`--use-imghost`），相关 IP / ssh / 路径已脱敏。

---

## 设计理念：Wrapper + Content 分离

把 NBP prompt 分成两层：
1. **固定 wrapper**（`wrapper_v2.txt`）：模板保留规则、严格文本规则、视觉风格、全局禁用列表。**所有页面共享，不改**。
2. **页面 content**（用户提供的 layout 文件）：只写"这一页要画什么"——标题、正文结构、数字、表格、卡片、强调色。**每页只改这个**。

```
content (v4 风格 layout)
   ↓ 嵌入 wrapper_v2.txt 的 {{CONTENT}} 占位符
完整 NBP prompt → 保存为 p<NN>_full_prompt.txt（迭代源）
   ↓ NBP 图生图 (60-120s, 4K, 16:9, 用 v2 模板做参考图)
p<NN>_raw.png
   ↓ composite_v2.py 后处理:
   ① clean 模板装饰层合成（橙弧 / 蓝弧 / 分隔线 / 双 logo）
   ② logo bbox 像素级强制覆盖（确保 logos 100% 像模板）
   ③ 加白色页码数字（位置/字号匹配原模板）
p<NN>_FINAL.png
```

---

## 核心约束（强制）

1. **必须用 NBP 图生图**——v2 模板作为参考图（默认本地内联）
2. **必须保留完整 prompt**——每次写到 `p<NN>_full_prompt.txt`，方便下次手动调
3. **必须用 composite 后处理**——NBP 单独无法保证橙弧 + 像素级 logos
4. **不要 codex 加工**——v2 假设 content 已定稿，不做近似化、增删、扩写
5. **不要 strong tagline / 金句**——学术答辩 PPT 不要传记式 punchline
6. **页码默认由程序加**——也支持不带页码生成，最后统一后处理批加

---

## 关键文件（全在 SKILL_DIR 内）

| 文件 | 用途 |
|------|------|
| **`generate_slide_v2.py`** | ★ pipeline 主入口（端到端 runner） |
| `wrapper_v2.txt` | NBP prompt 固定包装，含 `{{CONTENT}}` 占位符 |
| `composite_v2.py` | 装饰层合成 + 像素级 logo + 加页码 |
| `add_page_number_v2.py` | 单独加页码（已被 composite 集成，单用也行） |
| `正文页模板_v2.png` | 4K 模板原图（2667×1500） |
| `正文页模板_v2_clean.png` | 擦掉占位文字+原页码的 clean 模板，composite 用 |
| `正文页模板_v2_1080p.jpg` | 1080p 缩略图，默认作参考图（本地内联） |
| `sync_to_imghost_v2.sh` | （可选）自建图床上传，仅 `--use-imghost` 用 |
| `image-api/image_generate.py` | 收编的 NBP 生图 CLI |
| `image-api/provider_config.py` | NBP provider 配置（laozhang / nanobanana） |

---

## Content 文件格式（v4 风格）

content 是 markdown-ish 文本，**只描述正文内容**，不含模板/字体/视觉规则（这些在 wrapper 里）。约定：

- 用 `【】` 标注每个区块的位置/字号/颜色（NBP 读但不渲染这些括号）
- 用 `===` `═══` `─` 做视觉结构分隔
- 行内用 `|` 表示表格列分隔
- 所有数字 / 人名 / 年份 / 专有名词必须**精确**（wrapper 已禁止 NBP 改写）
- 末尾可加 `【本页禁止出现】` 列页面特定禁用项

骨架示例：

```
===================================================================
P04 — <页面主题>
本 prompt 只生成幻灯片中间正文部分，不含 header / footer / 模板边框
===================================================================

【主标题（顶部居中，navy #15305e bold ~42pt PingFang SC）】
<主标题一句话>

【主标题下方】一条 ~140px 宽的橙色 #f08a1c 细横线，居中

【主标题下方一行小字 charcoal ~13pt italic 居中】
<副标题 / 核心论点>

===================================================================
【正文区：<描述布局，如 上半部对比表 + 下半部三卡片>】
===================================================================

═══════════ <区块标题> ═══════════
<表格 / 卡片 / 流程图，用 | 和 ─ 画结构，标 navy/charcoal/orange 颜色>

【底部全宽结论条 — navy 圆角矩形，白色 bold 中文 ~16pt 居中】
<一句话结论 │ 项目 hook>

===================================================================
【本页禁止出现】
- 任何 "详见 P0X" 交叉引用
- <其它页面特定禁用项>
===================================================================
```

> content 控制在 **~150 行以内**，超过 NBP 容易丢细节。

---

## 完整流程

### 单页生成

```bash
python3 "$SKILL_DIR/generate_slide_v2.py" <content_file> -p <page_number> -o <output_dir>
# 不带页码（最后统一加）:
python3 "$SKILL_DIR/generate_slide_v2.py" <content_file> --no-page-number -o <output_dir>
```

### 迭代某页（不重跑 NBP，省钱省时）

只调页码/logo 等后处理，复用已有 raw png：

```bash
python3 "$SKILL_DIR/generate_slide_v2.py" <content_file> -p 4 -o <output_dir> --skip-nbp
```

### 手动调 prompt + 重跑 NBP

对结果不满意 → 直接编辑 `<output_dir>/p04_full_prompt.txt`，再单跑 NBP（本地内联模板）：

```bash
python3 "$SKILL_DIR/image-api/image_generate.py" \
  "$(cat <output_dir>/p04_full_prompt.txt)" \
  -i "$SKILL_DIR/正文页模板_v2_1080p.jpg" \
  -r 4K -a 16:9 \
  -o <output_dir>/p04_raw.png

python3 "$SKILL_DIR/composite_v2.py" <output_dir>/p04_raw.png -p 4 -o <output_dir>/p04_FINAL.png
```

或改 content 文件重跑 `generate_slide_v2.py` 让它重拼 prompt。

### 批量多页

```bash
for i in 02 04 05 06 07; do
  python3 "$SKILL_DIR/generate_slide_v2.py" "./content/p${i}_prompt.txt" -p $((10#$i)) -o ./slides_out
done
```

### 后期统一加页码

```bash
for i in 1 2 3 4 5 6 7 8; do
  python3 "$SKILL_DIR/composite_v2.py" "./slides_out/p0${i}_raw.png" -p $i -o "./slides_out/p0${i}_FINAL.png"
done
```

---

## composite_v2.py 关键参数与内部逻辑

```bash
python3 "$SKILL_DIR/composite_v2.py" <input.png> [-p <page_num>] [-o <output.png>] [--template <path>]
```

1. **Layer 1 装饰层 mask**：clean 模板上 R+G+B < 750 的像素视为"装饰像素"（橙弧/蓝弧/分隔线/logo 有色部分），覆盖到 NBP 输出
2. **Layer 2 logo bbox 强制覆盖**：右上角 `(89.65%, 0.27%)-(99.36%, 9.40%)` 整块从模板拷贝（含 logo 内部白色），保证像素级复刻
3. **加页码**：`(97.17%, 96.17%)` 中心写白色数字，字符高 2.2% 图高

---

## v2 模板视觉特征

白底极简：左上橙色 (#f08a1c) 1/4 圆弧 + 顶部细分隔线 + 右上双 logo（橙 W 西湖盾 + 蓝 Guomics 六边盾）+ 右下深蓝 (#15305e) 弧角 + 右下角程序加的小号白色页码。中间区域完全留白给内容。

**与 v1 区别**：去掉世界地图水印、平行四边形条、底部品牌条（"西湖大學"书法 / page badge / "WESTLAKE UNIVERSITY"），内容区更大更干净。

---

## 经验教训（必读）

1. **NBP 顽固加深蓝头条**：哪怕 prompt 强调"top is white"，NBP 仍爱给 headline 套深蓝 banner。composite 至少保证橙弧/logos/分隔线/蓝弧不丢
2. **logo 不能信 NBP**：composite 必须强制像素覆盖 logo bbox，NBP 单画 logo 常合并/简化/重设计
3. **content 不要太长**：单页 prompt 越长 NBP 越易丢细节，控制 ~150 行以内
4. **数字/人名/年份**：wrapper 已禁 NBP 改写，但生成完仍建议 spot-check 关键数字
5. **NBP 4K 16:9 约 60-120s 出图**
6. **保存 full_prompt.txt 是为了迭代**：想微调直接编辑它再单跑 NBP，不用重拼——v2 最重要的设计点之一
7. **API quota / 403**：若 NBP 报 `insufficient_user_quota` / HTTP 403，先确认所选 provider 的 key 已 export（`echo $LAOZHANG_API_KEY` 或 `$APIYI_API_KEY` 非空）
8. **数字卡用「大数字 + 一行说明」**：给 NBP「巨大数字 + 副标题 + 再一行小字」的三层卡片，它爱在最底行加戏糊出乱码；精简成「一个大数字 + 一行说明」并显式禁止第三行就干净。**结构化表格反而很稳**（4K 下 6 行 4 列表格数字清晰）。— 多次实战验证（APIYI / gemini-3-pro-image）
9. **切换 provider 用环境变量**：`IMAGE_PROVIDER=apiyi APIYI_API_KEY=... python3 generate_slide_v2.py ...`，不改任何文件、不破坏自包含。**默认 provider 为 `apiyi`，用前请设你自己的 `APIYI_API_KEY`**（本分享版不含任何作者 key）；要用 `laozhang` 设 `IMAGE_PROVIDER=laozhang LAOZHANG_API_KEY=...`，要用 `nanobanana` 设 `IMAGE_PROVIDER=nanobanana NANOBANANA_API_KEY=...`，均为纯环境变量切换、无需改文件。

---

## 质量自检清单

- [ ] 标题在白底上（没被 NBP 套深蓝 banner，已被 composite 处理）
- [ ] 西湖 + Guomics 双 logo 右上角像素级保留
- [ ] 左上橙弧 + 右下蓝角装饰保留
- [ ] 关键数字 / 公式 / 指标精确（对照 content 逐项核对）
- [ ] 无中文乱码、无交叉引用（"见 Fig. X" / "详见 P04"）
- [ ] 页码位置正确（若加了）
- [ ] 文件大小 5-15 MB

---

## 边界

- **只做单页**；多页逐页跑 / 批量循环。>1 页的整套 deck 设计另说
- **不做内容近似化/扩写**：content 假设已定稿，pipeline 不增删
- **海报/多 panel 转单页**：如果上游是 6-panel 论文海报或多图大图要压成一页，先人工把它拆成各页的 content（一页一个主题、控制在 ~150 行内），再逐页跑本 pipeline——本技能只负责「定稿 content → 单页出图」这一段

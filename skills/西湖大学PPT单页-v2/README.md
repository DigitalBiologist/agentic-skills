# 西湖大学 PPT 模板资产（v2 / Guomics 风格）

本目录是「西湖大学 v2 模板单页生成」技能的资产 + pipeline，**自包含**：所有脚本路径都自引用本文件夹，不依赖 `~/.claude`。

> **模板说明**：v2 模板为白底极简、**无顶部分隔线**版（`wrapper_v2.txt` 也禁止 NBP 画分隔线）。想换成自己实验室的模板：替换 `正文页模板_v2.png`，按下方「重新生成 1080p 缩略图」重生成参考图，再据新模板调整 `composite_v2.py` 里 logo bbox / 页码坐标即可。

## 文件清单

| 文件 | 用途 |
|------|------|
| `正文页模板_v2.png` | 4K 模板原图（2667×1500），权威源 |
| `正文页模板_v2_clean.png` | 擦掉占位文字 + 原页码的 clean 模板，`composite_v2.py` 用它做装饰层合成 |
| `正文页模板_v2_1080p.jpg` | 1080p 缩略图，默认作为 NBP 图生图的参考图（本地 base64 内联） |
| `wrapper_v2.txt` | NBP prompt 固定包装，含 `{{CONTENT}}` 占位符（模板保留规则 + 严格文本规则 + 视觉风格 + 全局禁用） |
| `generate_slide_v2.py` | ★ 端到端 pipeline 主入口 |
| `composite_v2.py` | 后处理：装饰层 mask 合成 + logo bbox 像素级覆盖 + 加页码 |
| `add_page_number_v2.py` | 单独加页码工具（已被 composite 集成，单用也行） |
| `sync_to_imghost_v2.sh` | （可选）把模板推到自建图床；**默认用不到**，默认走本地内联 |
| `image-api/` | 收编的 NBP 生图 CLI（`image_generate.py` + `provider_config.py`），自包含 |

## 参考图：本地内联 vs 图床

- **默认（本地内联）**：`generate_slide_v2.py` 直接把 `正文页模板_v2_1080p.jpg` 路径喂给 `image-api/image_generate.py -i`，后者会自动读取并 base64 内联给 NBP。**无需任何图床，开箱即用、可分享。**
- **可选（图床）**：加 `--use-imghost` 时才走 `sync_to_imghost_v2.sh` 上传到自建图床拿公网 URL。原作者用的是一台私有云主机，相关 IP / ssh 别名 / 路径**已脱敏为占位符**，要用得先在脚本里（或用 `IMGHOST_SSH` / `IMGHOST_HTTP` / `REMOTE_DIR` 环境变量）填上你自己的图床。

## 重新生成 1080p 缩略图

如果替换了 `正文页模板_v2.png`，重生成缩略图：

```bash
python3 -c "
from PIL import Image
img = Image.open('正文页模板_v2.png')
img.thumbnail((1920, 1080))
img.convert('RGB').save('正文页模板_v2_1080p.jpg', 'JPEG', quality=92)
"
```

## v2 模板视觉特征

白底极简：左上橙色 (#f08a1c) 1/4 圆弧 + 顶部细分隔线 + 右上双 logo（橙 W 西湖盾 + 蓝 Guomics 六边盾）+ 右下深蓝 (#15305e) 弧角 + 右下角程序加的小号白色页码。**与 v1 区别**：去掉了世界地图水印、平行四边形条、底部品牌条，内容区更大更干净。

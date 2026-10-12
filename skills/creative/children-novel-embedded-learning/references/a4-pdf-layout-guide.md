# A4竖版儿童小说PDF排版参数指南

## 使用场景
将Markdown源文件（含插图占位符）渲染为A4竖版可打印PDF，目标读者10岁儿童。

## 核心参数速查

| 参数 | 值 | 原因 |
|------|-----|------|
| 页面尺寸 | A4 (210×297mm) | 标准打印纸 |
| 正文字号 | 13pt | 10岁儿童不费眼 |
| 插图说明字号 | 10pt | 比正文小但不费眼 |
| 章节标题字号 | 20pt | 醒目但不夸张 |
| 行距 | 1.8 | 儿童阅读舒适 |
| 页边距 | 上下15mm 左右20mm | 留装订边 |
| 插图最大高度 | 72vh | 不满页，留翻页呼吸 |
| 插图最大宽度 | 170mm | 不超出页边距 |

## WeasyPrint HTML生成法

不用md2pdf（大图会崩），直接用Python生成HTML再用WeasyPrint渲染：

```python
from weasyprint import HTML
import glob, re

# 1. 读取MD，替换插图占位符为<img>标签
with open("源文件.md", "r", encoding="utf-8") as f:
    html_body = f.read()

# 匹配 [插图: 描述]
img_dir = "插画/"
imgs = sorted(glob.glob(f"{img_dir}*.png"))
# 封面单独处理，正文插图从1.png开始
body_imgs = [i for i in imgs if "封面" not in i]

idx = 0
def replace_img(m):
    global idx
    if idx < len(body_imgs):
        tag = f'<div class="illustration"><img src="{body_imgs[idx]}" alt="插图{idx+1}"><p class="caption">插图{idx+1}：{m.group(1)}</p></div>'
        idx += 1
        return tag
    return m.group(0)

html_body = re.sub(r'\[插图:\s*(.+?)\]', replace_img, html_body)

# 2. 渲染
css = """
@page { size: A4; margin: 15mm 20mm; }
body { font-size: 13pt; line-height: 1.8; font-family: "Noto Serif CJK SC", "SimSun", serif; }
h1 { font-size: 20pt; text-align: center; margin: 10mm 0 5mm 0; page-break-before: always; }
h2 { font-size: 16pt; margin: 8mm 0 4mm 0; }
.illustration { text-align: center; margin: 8mm 0; page-break-inside: avoid; }
.illustration img { max-width: 170mm; max-height: 72vh; }
.caption { font-size: 10pt; color: #666; margin-top: 2mm; font-style: italic; }
p { text-indent: 2em; margin: 0.5em 0; }
"""

HTML(string=f"<html><body>{html_body}</body></html>").write_pdf("output.pdf", stylesheets=[...])
```

## 字体安装（WSL环境）

```bash
# 中文字体（如果系统没有）
sudo apt-get install fonts-noto-cjk
# 或使用Windows宿主字体
fc-list :lang=zh  # 查看可用中文字体
```

## 常见问题

### PDF体积过大（>50MB）
- 插图先用PIL压缩到A4分辨率（1240×1754px足够）
- 不要直接嵌4K原图
```python
from PIL import Image
img = Image.open("原图.png")
img.thumbnail((1240, 1754))
img.save("压缩图.png", optimize=True, quality=85)
```

### 章节标题不换页
- h1加 `page-break-before: always` 保证新章从新页开始

### 插图跨页撕裂
- `.illustration` 加 `page-break-inside: avoid`

### 封面单独处理
- 封面页用 `@page cover { margin: 0; }` 配合 `page: cover` 属性
- 封面图 `max-width: 210mm; max-height: 297mm`

### 改文字不崩版面（Same-Length Replacement）

当PDF已排版定型，需要对正文做微调时，**替换文本的字数必须和原文相等**，否则段落长度变化会导致后续页面全部偏移。

适用范围：
- 改词汇（"朝贡体系"4字 → "主动上供"4字）
- 改数字（"三张"2字 → "两张"2字）
- 改术语（"版权分成"4字 → "卖了分钱"4字）

验证方法：
```python
old = "朝贡体系"
new = "主动上供"
assert len(old) == len(new), f"Length mismatch: {len(old)} vs {len(new)}"
```

如果找不到等长度替换词，该词大概率上下文足够强，不需要改。

## 已验证的生成脚本

最终可用的生成脚本模式（已用于《受着呗》65MB A4竖版PDF）：
- 封面img + 正文插图自动匹配插入
- 章节标题自动分页
- 13pt正文 + 10pt插图说明 + 20pt标题
- 输出A4竖版可直接打印

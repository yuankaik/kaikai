# 插画插入工作流

当用户在书中标记了 `[插图: 场景描述]` 占位符并提供了图片后，用以下流程自动插入。

## 占位符格式

```markdown
[插图: 一句话描述这个画面的内容]
```

占位符单独成行，在它要描述的场景之前。

## 命名规范表

创建一个 `插画命名对照表.md` 放在图片文件夹旁边，格式：

| 文件名 | 章节 | 对应场景 |
|--------|------|----------|
| cover.png | 封面 | 替换标题页 |
| ch01-01.png | 第1章 | 第一个插图场景 |
| ch01-02.png | 第1章 | 第二个插图场景 |

如果用户已经用随机文件名上传（UUID命名），不要强制改名。用文件名排序后按顺序匹配占位符。

## 自动插入脚本模式

```python
# 1. 扫描图片文件夹
images = sorted([f for f in os.listdir(folder) if f.endswith('.png') and not f.startswith('封面')])
covers = sorted([f for f in os.listdir(folder) if f.startswith('封面')])

# 2. 替换占位符为 <img> 标签
img_idx = 0
def replace_placeholder(m):
    global img_idx
    if img_idx < len(images):
        img_path = os.path.join(folder, images[img_idx])
        img_idx += 1
        return f'<div class="illustration"><img src="{img_path}" style="max-width:100%;max-height:65vh;object-fit:contain;"/><p class="caption">{m.group(1)}</p></div>'
    return m.group(0)

text = re.sub(r'\[插图: ([^\]]+)\]', replace_placeholder, text)

# 3. 插入封面
cover_html = f'<div class="cover-page"><img src="{cover_path}" style="width:100%;height:100vh;object-fit:cover;"/></div>'
body = re.sub(r'<center>.*?</center>', cover_html, body, flags=re.DOTALL)
```

## CSS关键规则

```css
@page cover { margin: 0; @bottom-center { content: none; } }
.cover-page { page: cover; page-break-after: always; }
.illustration { page-break-before: avoid; page-break-after: avoid; text-align: center; }
.illustration img { max-width: 100%; max-height: 65vh; object-fit: contain; }
.caption { font-size: 8pt; color: #999; font-style: italic; }
```

## 注意事项

- 图片分辨率 1024×1536 以上效果最好
- 封面用 `object-fit: cover` 满版，正文插图用 `contain` 保持比例
- 多出的图片自动跳过，不会报错
- 图片尺寸会影响PDF大小——23张2.8MB图≈65MB PDF是正常的

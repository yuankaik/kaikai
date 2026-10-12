# 插画命名模板

将此表提供给用户。用户按编号命名图片后放入 `插画/` 文件夹。

## 封面
| 文件名 | 位置 |
|--------|------|
| 封面.png | 封面页 |

## 正文插画（编号1-N，对应章节顺序）
| 文件名 | 场景 |
|--------|------|
| 1.png | [占位符1的描述] |
| 2.png | [占位符2的描述] |
| ... | ... |
| N.png | [占位符N的描述] |

## 自动匹配脚本逻辑

```python
images = sorted([f"{i}.png" for i in range(1, N+1)])
# 按文件名数字顺序匹配占位符
for i, placeholder in enumerate(placeholders):
    img_path = f"插画/{images[i]}"
    replace(placeholder, f'<img src="{img_path}"/>')
```

关键规则：
- 文件名必须是从1开始的连续数字
- 数量必须与占位符数量匹配
- 封面单独命名为"封面.png"
- 用户上传时的时间顺序不可靠，要求用户显式编号

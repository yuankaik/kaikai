# 桌面错题投递箱 — 文件夹批量处理工作流

## 触发条件

用户将错题照片放入 `C:\Users\admin\Desktop\佳乐错题投递箱\` 文件夹（可能通过文件管理器拖放或微信保存），然后告知 agent "错题已经放在XX文件夹"。

## 与微信拍照的区别

| | 微信拍照 | 桌面投递箱 |
|---|---|---|
| 触发 | 发微信消息+图片 | 放文件夹+告知 |
| 数量 | 通常1张 | 可能批量多张 |
| 时效 | 实时 | 用户可能积攒一批后一起放 |
| 文件命名 | 微信生成hash名 | 可能有dayXX等有意义命名 |

## 处理流程

1. `search_files(target='files')` 列出文件夹内所有图片
2. `terminal(ls -la)` 查看文件日期，按日期分组
3. 对每张图片 `vision_analyze` 识别内容
4. 区分：错题（有红笔批改标记） vs 参考资料（无标记笔记）
5. 用 `execute_code` + subprocess 批量调用 `add_error.py` 录入

## 批量录入模板

```python
import subprocess

script = "/home/adminkaikai/.hermes/skills/education/daily-review-push/scripts/add_error.py"

entries = [
    "录一条: 数学 82−24=53,退位减法计算错误,正确58",
    "录一条: 英语 pencil,基础词汇未掌握,铅笔",
]

for entry in entries:
    subprocess.run(["python3", script, entry], capture_output=True, text=True)
```

## ⚠️ 注意

- **不是所有图片都是错题。** 用户可能放入成语笔记、范文参考等无批改标记的图片。识别后跳过，告知用户即可。
- 文件夹内文件处理完后不移除/不删除，由用户自行管理。
- 今日复习DOCX如已由cron生成，新录入的错题将在次日10:00自动出现。

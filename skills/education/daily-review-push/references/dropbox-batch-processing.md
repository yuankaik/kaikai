# 错题投递箱批量处理工作流

## 触发条件

用户往 `C:\Users\admin\Desktop\佳乐错题投递箱\` 扔照片后说"错题已放入"或类似提示。

## 完整流程（5步）

### 步骤1：扫描新文件

```python
from hermes_tools import search_files
# 列出投递箱所有文件
files = search_files(pattern="*", target="files", 
                     path="/mnt/c/Users/admin/Desktop/佳乐错题投递箱")
```

同时用 `ls -la --time-style=long-iso` 获取文件日期，按日期区分批次。

### 步骤2：并行 vision_analyze（关键）

**全部图片并行调用 vision_analyze，不要逐张等结果。**

```
# 对每张图同时发 vision_analyze
vision_analyze(image_url=..., question="完整识别这张图片中的所有错题内容...")
```

并行调用大幅减少等待时间（4张图并行=1次等待 vs 逐张=4次等待）。

### 步骤3：分类处理

| 类型 | 处理方式 |
|------|----------|
| 数学错题（有❌标记） | 录入 add_error.py |
| 英语错题（有❌标记） | 录入 add_error.py |
| 语文错题（有❌标记） | 录入 add_error.py |
| 语文笔记/参考资料（无❌） | 跳过，告知用户 |
| vision识别模糊/有争议 | 标记出来，让用户人工确认 |

### 步骤4：批量 add_error.py

使用 execute_code 批量调用 add_error.py：

```python
import subprocess
script = "/home/adminkaikai/.hermes/skills/education/daily-review-push/scripts/add_error.py"

entries = [
    "录一条: 数学 82−24=53,退位减法计算错误,58",
    "录一条: 英语 pencil,基础词汇未掌握,铅笔",
    # ... more entries
]

for entry in entries:
    subprocess.run(["python3", script, entry], ...)
```

### 步骤5：汇总报告

输出表格：
```
| 文件 | 日期 | 科目 | 内容 | 错题数 |
|------|------|------|------|--------|
| xxx.jpg | 7/2 | 英语 | 现在进行时 | 9❌ |
| yyy.jpg | 7/2 | 数学 | 面积计算 | 4❌ |
| zzz.jpg | 7/2 | 语文 | 成语笔记 | 0（非错题）|
```

附诊断建议。

## 注意事项

- **并行vision**：所有图片一起发，不要串行
- **成语笔记/参考资料跳过**：无❌标记的不录入
- **争议题标记**：vision看不清的标记出来让人工确认，不要强行录入
- **去重**：如果同一错题之前已录入，add_error.py自动去重
- **通知**：新录入的错题第二天10:00 cron自动加入复习DOCX

# 数学检测表批量OCR + 知识点对比工作流

当 vision 不可用时，用此流程处理多张数学检测表照片。

## 前提

- Pix2Text 已安装在 `~/ocr_env/`（`source ~/ocr_env/bin/activate`）
- 知识点库：`/mnt/c/Users/admin/Desktop/shanghai-exams/数学知识点库.json`（167条，含 id/grade/topic/question/answer）
- 检测表照片在本地目录

## 完整流程

### 第1步：批量OCR

```bash
source ~/ocr_env/bin/activate
for f in /path/to/images/*.jpg; do
  echo "=== $(basename $f) ==="
  p2t predict -i "$f" 2>&1 | sed -n '/^Outs:/,$ p'
  echo
done
```

每张约20-25秒（首次下载模型后）。15张约5-7分钟。

输出格式示例：
```
S4-17加法的意义 已知和与一个加数，求另一个加数，用什么法？ 减法 具
S4-37三角形分类（按边）两条边相等的三角形叫什么？ 等腰三角形 √
S4-31小数点移动 把3.8扩大到100是? 0.35 M口
```

### 第2步：解析OCR输出

OCR输出混乱的原因：
- 表格布局 → p2t按阅读顺序输出，行列错乱
- ✅❌符号 → √常被识别为"d""区""品""口""M口""信""具"
- 数学符号 → 分数、乘除号识别差
- 手写答案 → 部分丢失

**解析规则：**
1. 按 `S\d-\d+` 编号定位每道题
2. 提取编号后的文字（知识点名称 + 题目 + 答案 + 标记）
3. 如果出现"√" → 明确正确
4. 如果有数字/文字答案但标记不是"√" → 需判断是否匹配标准答案
5. 如果OCR混乱到不可读 → 标记"需确认"

### 第3步：与知识库对比

用 `execute_code` 写脚本：

```python
import json

# 加载知识库
with open("数学知识点库.json") as f:
    kb = json.load(f)

# 对每个知识点：
# - OCR中有明确√ → status="ok"
# - OCR中有答案且匹配标准答案 → status="ok"
# - OCR中有答案但不匹配 → status="gap" (漏洞)
# - OCR中无答案 → status="gap" (没填=不会)
# - OCR混乱不可判断 → status="check" (需确认)
# - 5年级+无答案 → status="not_yet" (未学)
```

### 第4步：输出结构化JSON

格式：
```json
{
  "title": "佳乐数学摸底检测 — 欠缺知识点清单",
  "summary": {
    "total": 167,
    "mastered": 82,
    "gaps": 32,
    "needs_check": 40,
    "not_yet_learned": 13
  },
  "items": [
    {
      "id": "S4-31",
      "grade": "4B",
      "topic": "小数点移动",
      "question": "把3.8扩大到100倍是？",
      "standard_answer": "380",
      "jiale_answer": "0.35",
      "status": "gap",
      "status_label": "❌ 漏洞",
      "note": "小数点移动方向搞反了"
    }
  ]
}
```

### 第5步：人工确认

让家长对照原始卷子，确认：
- `status="check"` 的项目 → 到底是对是错
- `status="gap"` 中OCR可能误判的 → 确认是否真错了

确认后更新JSON，然后可以用这些数据生成针对性练习题。

## 已知限制

| 问题 | 影响 | 缓解 |
|------|------|------|
| ✅/❌符号识别差 | 需人工确认率高(~25%) | 分三级：ok/gap/check |
| 手写答案丢失 | 可能把正确当漏洞 | 对比标准答案辅助判断 |
| 表格行列乱序 | 知识点编号可能错位 | 用S编号锚定 |
| 数学符号畸变 | 分数、乘除号变乱码 | 人工比对标准答案 |

## 与订正本OCR的区别

| | 订正本OCR | 检测表OCR |
|---|---|---|
| 目标 | 提取红笔批改内容 | 判断每道题对错 |
| 输入 | 1-2张 | 10-15张批量 |
| 标记类型 | 红笔✗ + 订正文字 | ✅❌勾选 |
| OCR重点 | 文字内容 | 对错标记（最难） |
| 输出 | 错题条目→每日复习JSON | 缺失知识点清单→出题依据 |

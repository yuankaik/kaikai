# 数据代号映射指南

## 问题

从字海钓徒项目迁移到 `每日复习追踪.json` 的数据中，`content` 字段可能存的是代号而非实际内容：

| 代号格式 | 含义 | 示例 |
|----------|------|------|
| `v4a-001` | 英语词 ID（v=vocab, 4a=4年级上册, 001=序号） | `v4a-001` → meet |
| `D3-R1` | 字海钓徒 Day3 回炉题 #1 | `D3-R1` → 除法计算与运算顺序 |
| `Q5692` | 题库题目 ID | `Q5692` → 看拼音写词语 |
| `D4-V4` | Day4 变式题 #4 | `D4-V4` → 课堂词语回忆 |
| `R1` | 课堂雷达题 #1 | `R1` → 写出今天记住的一个词 |

## 映射源

### 英语词 ID → 单词+释义

**映射文件**: `/mnt/c/Users/admin/Desktop/shanghai-exams/牛津英语1-5年级词汇总表.md`

**解析规则**:
- `v4a-001`: grade=4A, 该年级第 1 个词
- `v3b-015`: grade=3B, 该年级第 15 个词
- 按年级顺序累计编号，每个年级从头开始

**Python 映射代码**:
```python
import re
# 解析词汇总表 MD，按年级累计计数
# 格式: ## N年级上册 (NA) / ### Module N: / | N | word | meaning |
# 构建 {v{grade_lower}-{seq:03d}: (word, meaning)} 字典
```

### 题目 ID → 题目原文

**映射文件**: `D:\Kaideepseek\worktrees\ace-angler-phase1-checkpoint-a\practice\specs\*.json`

**文件列表**:
- Day3-海王龙的逆向追踪.json
- Day4-虎鲸队长的除法航线.json
- Day5-巨枪乌贼的回炉海域.json
- Day6-蓝鲸英语补给航线.json
- Day7.json / Day8.json / Day9.json

**查找方式**:
```python
# 遍历所有 Day JSON 的 sections[].questions[]
# 匹配 id 字段 → 提取 prompt, knowledge, subject
```

### 数学代号 → 知识点

当题目 ID 无法从 Day 规格中找到时，使用 `context` 字段（已包含知识点名称）替换:
```python
# D3-R1, context="除法计算与运算顺序"
item['content'] = item['context']  # "除法计算与运算顺序"
```

## 验证

运行后检查：`content` 字段不应匹配 `^[vV]?\d*[a-zA-Z]?[-_]\w+$` 或 `^[DQR]\d+`。

## 已知坑

- 牛津词汇总表有 1044 词，但部分词 ID 可能超出范围（如 v5b 超出）
- Day4/5/6 的文件名带中文：`Day4-虎鲸队长的除法航线.json`，不是 `Day4.json`
- 重复条目（R1 在多天出现）按最早出现的 Day 为准
- 日积月累中标记"（在古诗中）"的是重复引用，应跳过

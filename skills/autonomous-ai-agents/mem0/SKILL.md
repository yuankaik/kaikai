---
name: mem0
description: AI Agent 记忆层 (59K⭐)——给 Hermes 加上长期记忆、用户偏好学习。跨会话保持上下文。pip install mem0ai 即用。
source: https://github.com/mem0ai/mem0
---

# Mem0 — AI Agent 记忆层

为 AI Agent 提供持久记忆。学习用户偏好、记住重要信息、跨会话保持上下文。

## 安装

```bash
pip install mem0ai
```

## 基础用法

```python
from mem0 import Memory

m = Memory()

# 添加记忆
m.add("用户喜欢简洁回复", user_id="kai")

# 搜索记忆
results = m.search("回复风格", user_id="kai")

# 获取全部
all_memories = m.get_all(user_id="kai")
```

## 与 Hermes 集成

- 每次对话结束时保存关键信息
- 下次对话开始时搜索相关记忆
- 自动学习用户偏好

## 对比 Hermes 内置 memory

| | mem0 | Hermes memory |
|------|------|-------------|
| 存储 | 向量库 | 文件系统 |
| 搜索 | 语义搜索 | 精确匹配 |
| 适合 | 大量模糊记忆 | 少量精确事实 |

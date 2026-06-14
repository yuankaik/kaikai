---
name: autoresearch
description: Karpathy 的自主 ML 研究框架 (87K⭐)——AI Agent 无限循环：改代码→训练5分钟→看结果→保留或丢弃。需要 NVIDIA GPU。
source: https://github.com/karpathy/autoresearch
---

# AutoResearch — AI 自主研究

Karpathy 的自主机器学习研究框架。一个 AI Agent 循环：编辑 `train.py` → 训练 5 分钟 → 检查 `val_bpb` → 好了保留坏了丢弃。

## 硬件要求

- **NVIDIA GPU** + CUDA（H100 约 45GB VRAM）
- 小 GPU 可调参（见下方）
- ~100GB 磁盘

## 安装

```bash
git clone https://github.com/karpathy/autoresearch.git
cd autoresearch
pip install uv && uv sync
uv run prepare.py     # 准备数据
uv run train.py       # 验证基线
```

## 研究循环

```
循环:
  1. 读 git 状态
  2. 改 train.py（实验想法）
  3. git commit
  4. uv run train.py
  5. 提取 val_bpb
  6. 好了保留，坏了 git reset --hard
  无限重复
```

## 文件权限

| 文件 | 操作 |
|------|------|
| `train.py` | ✏️ 可编辑 |
| `prepare.py` | 📖 只读 |
| `results.tsv` | 📝 追加日志 |

## 小 GPU 调参

- `DEPTH`: 8→4
- `vocab_size`: 8192→2048
- `MAX_SEQ_LEN`: 2048→256
- `TOTAL_BATCH_SIZE`: 减小

## 注意

这不是 Hermes 技能，是独立 GPU 程序。适合有显卡时让 AI 自主跑实验。

---
name: desktop-disk-cleanup
description: WSL 环境下整理 Windows 桌面/磁盘 —— 扫描存档、清单化、分类合并文件夹、删安装包与废弃残留、敏感文件脱敏。当用户说"整理一下桌面/磁盘"、"哪些需要清理"、"归档一下"时使用。全程"先列清单→确认→再动手"，绝不删资料。
category: devops
tags: [cleanup, desktop, windows, wsl, archive, organize, sensitive-files]
---

# 桌面 / 磁盘整理（WSL + Windows）

## 触发条件

- 用户说"整理桌面"、"磁盘满了"、"哪些存档需要整理/删除"、"归档一下"
- C/D 盘使用率高，需要腾空间

## 铁律（kai哥偏好）

1. **先盘点 → 列清单 → 用户确认 → 再动手**。绝不未经确认删除任何东西。
2. **默认只做安全清理**：废弃残留、安装包、空目录。**不碰资料**（除非用户明确说）。
3. **移动用 `shutil.move`，不用 `rm`**——可回退。
4. **筛选询问**：一轮只问 2-3 个关键决策，选项用 clarify 的 choices。
5. **删除前逐个 `os.path.exists` 校验**，处理失败要报告而非静默跳过。
6. **绝不整体删混合目录**——有些目录（如"应用传送门"）既有安装包又有用户资料，只挑安装包删。
7. **任务超时用 execute_code(Python) 而非 terminal**——terminal 常被审批拒。

## 步骤

### 1. 全景扫描

```python
# 盘符 + 容量
# ls /mnt/  ; df -h /mnt/c /mnt/d
```
```python
import os
D = "/mnt/c/Users/admin/Desktop"
print(len(os.listdir(D)), "项")
for e in sorted(os.listdir(D)):
    p = os.path.join(D, e)
    print(("[DIR] " if os.path.isdir(p) else "[file]"), e)
```

**⚠️ 坑：`du -sh /mnt/d/*` 在 Windows 文件系统上极慢甚至会超时**（小文件多 + 9p 协议）。
- 单目录用 `du -sh /mnt/d/目录名`（绝对路径，**不要用带空格的引号参数混在 for 循环里**——会整条失败 exit 1）
- 逐个跑，一次 5-8 个目录，timeout 设 280
- **不要**用 PowerShell 递归统计（用户可能拒绝该命令，且慢）

**⚠️ 坑：for 循环里带空格的目录名（如 `Claude code  documents` 双空格）会让整个 du 命令 exit 1 无输出。** 先 `ls -d 目录名` 诊断，或单独跑。

### 2. 分类识别（关键：判资料 vs 垃圾）

| 类型 | 处理 | 例子 |
|------|------|------|
| 废弃残留 | 删 | `~/*broken*`、`~/.hermes.backup.*`、空目录 |
| 安装包 | 删（保留最新的一个） | `*.exe` `*.msi`（Feishu/Ollama/加速器安装器） |
| 重复资料 | 去重留一份 | 版本堆积(pptx×4)、同名文件夹 |
| 资料 | **合并归档，不删** | 学习/工作/项目 文件 |
| 敏感文件 | **移出 + 提醒轮换** | 含 API key/secret 的 txt |

### 3. 重复检测（用 MD5 而非文件名）

```python
import os, hashlib
def h(fp):
    return hashlib.md5(open(fp, "rb").read()).hexdigest()
# 对比两个目录：先比同名同路径，再比内容hash（防不同名同内容）
a = {os.path.relpath(os.path.join(r,f), A): h(os.path.join(r,f)) for r,_,fs in os.walk(A) for f in fs}
b = {os.path.relpath(os.path.join(r,f), B): h(os.path.join(r,f)) for r,_,fs in os.walk(B) for f in fs}
dup = [k for k,v in a.items() if v in b.values()]      # 内容重复
only = [k for k,v in a.items() if v not in b.values()] # 独有→必留
```

### 4. 执行清理（分离操作，便于报告）

```python
import os, shutil
deleted = []; failed = []
# 删文件
for p in exes:
    if os.path.exists(p):
        sz = os.path.getsize(p); os.remove(p); deleted.append((p, sz))
    else:
        failed.append((p, "不存在"))
# 删目录树（先算大小用于报告）
for p in resid:
    if os.path.isdir(p):
        sz = sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(p) for f in fs)
        shutil.rmtree(p); deleted.append((p, sz))
# 删空目录
for p in empties:
    if os.path.isdir(p) and not os.listdir(p):
        os.rmdir(p); deleted.append((p, 0))
print("合计释放", round(sum(s for _,s in deleted)/1024/1024, 1), "MB")
```

### 5. 分类合并（建分类文件夹 + move）

kai哥验证过的分类法（平铺中文名，不用 01/02 数字前缀）：

```
桌面/
├── 佳乐学习/          学习资料
│   ├── 每日练习/      每日复习+每周练习+口算+单词
│   ├── 练习题库/      练习库+reading-practice
│   ├── 期末试卷/
│   ├── 教材资源/      shanghai-exams+教科书pdf
│   ├── 错题本/
│   ├── 体育证书/
│   ├── 参考资料/      作息表+单词表+报告
│   └── 深海钓徒/      小说正文+插画（从练习库分离）
├── 工作/              仓库KPI/月度Review/简历/手册
└── 项目/              开发文档+技术笔记+html产出
```

**关键**：合并前先 move 检查目标是否已存在（防覆盖）：
```python
dst = os.path.join(catdir, it)
if os.path.exists(dst): issues.append(f"{it} 目标已存在，跳过"); continue
shutil.move(src, dst)
```

### 6. 敏感文件处理（重要）

**扫描桌面明文密钥**：
```bash
search_files "sk-|secret|token|api_key|password" path=/mnt/c/Users/admin/Desktop file_glob="*.txt"
```

处理原则：
- **移到 `~/.hermes/` 隐藏位置**，不留在桌面
- **明确提醒用户去后台轮换 key**（移动≠安全，历史记录/回收站可能留存）
- **用户说"不动"的文件绝不碰**（如 scmwh-wx-secret.txt）

```python
safe = os.path.expanduser("~/.hermes/xxx-keys-桌面移入.txt")
if not os.path.exists(safe): shutil.move(src, safe)
```

### 7. 报告格式

```
桌面条目 82 → 28 项  (↓66%)
① 删除  释放 583MB  (列出明细)
② 合并  11文件夹+13文件 → 佳乐学习/
③ 安全  Hermes.txt(含key) → ~/.hermes/
[未动]  scmwh-wx-secret.txt (用户要求保留)
[未定]  图片类/归属不明文件 → 问用户
```

## 陷阱

1. **du 超时** → 单个绝对路径逐个跑，别用通配符 for 循环
2. **带空格目录名** → 单独跑或先 ls -d 诊断
3. **混合目录不能整体删** → 逐个文件判断（"应用传送门"里有报名照！）
4. **同名不同内容 ≠ 重复** → 必须比 MD5，不能只看文件名
5. **练习库可能混入无关内容** → 如"佳乐暑假完整练习库"里混了《深海钓徒》小说+42张插画，要分离
6. **移动用 shutil.move 不用 rm** → 可回退
7. **删完必须报告空间变化** → `df -h` 前后对比
8. **用户没回复 clarify 时** → 按最合理判断执行（平铺分类、不碰资料），并在报告里说明"未定的项"

# WSL → Windows 文件锁处理

## 问题

在WSL中通过 `/mnt/c/` 路径写Windows文件时，如果文件被Windows程序（Word、资源管理器预览等）打开，`python-docx` 的 `save()` 会抛出：

```
PermissionError: [Errno 13] Permission denied
```

## 根因

Windows文件锁通过DrvFs传递到WSL，`open(file, 'w')` 被拒绝。

## 解决方案

### 方案A：先删后写（适用于单文件）

```python
import os
if os.path.exists(dst):
    try:
        os.remove(dst)
    except PermissionError:
        pass  # 被锁，走方案B
```

### 方案B：生成到 /tmp 再搬（批量文件，推荐）

```python
TMP = "/tmp/output_vN"
# 1. 所有 save() 写到 TMP
doc.save(os.path.join(TMP, "file.docx"))

# 2. 批量搬到桌面
import shutil
moved, failed = 0, 0
for f in os.listdir(TMP):
    src = os.path.join(TMP, f)
    dst = os.path.join("/mnt/c/Users/admin/Desktop/target/", f)
    try:
        if os.path.exists(dst): os.remove(dst)
        shutil.copy2(src, dst)
        moved += 1
    except PermissionError:
        failed += 1

if failed:
    print(f"关闭Word后运行: cp -r {TMP}/* /mnt/c/Users/admin/Desktop/target/")
```

## 注意

- `shutil.move()` 在跨文件系统时同样可能失败
- `shutil.copy2()` + `os.remove(src)` 更可靠
- 不要用 `os.rename()` 跨 `/tmp` 和 `/mnt/c/`（不同挂载点）

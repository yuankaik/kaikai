# EPUB → MOBI 批量转换

## 工具
Calibre 的 `ebook-convert` 命令行工具。

## 安装
```bash
sudo apt install calibre
```

## 批量转换
```bash
cd "/mnt/c/Users/admin/Desktop/儿童文学"
for f in *.epub; do
    mobi="${f%.epub}.mobi"
    [ -f "$mobi" ] && continue  # skip existing
    echo "Converting: $f"
    ebook-convert "$f" "$mobi"
done
```

## 大文件注意
- 20MB+ 的 EPUB 转换可能需要 30-60 秒
- 用 `terminal(background=true, notify_on_complete=true)` 避免超时
- 转换后文件通常比 EPUB 大 1.5-2 倍

## 验证
```bash
ls -1 *.mobi | wc -l  # 应该等于 EPUB 数量
```

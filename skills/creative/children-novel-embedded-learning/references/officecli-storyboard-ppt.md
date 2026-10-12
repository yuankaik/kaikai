# OfficeCLI 故事板PPT生成

用 iOfficeAI/OfficeCLI 从场景数据批量生成 .pptx 故事板。

## 安装

从 GitHub Releases 下载 `officecli-linux-x64`（~32MB），放到 `~/.local/bin/`。

网络慢时：用 Windows 浏览器下载到 Downloads，然后从 WSL 访问：
```bash
cp /mnt/c/Users/admin/Downloads/officecli-linux-x64 ~/.local/bin/officecli
chmod +x ~/.local/bin/officecli
```

## 创建PPT

```bash
# 创建空白PPT
officecli create output.pptx

# 添加幻灯片
officecli add output.pptx / --type slide --prop title="标题" --prop text="正文" --prop background="#0a1628"
```

## Batch JSON格式

```json
[
  {"command": "create"},
  {"command": "add", "parent": "/", "type": "slide", "props": {"title": "第一章", "text": "正文内容", "background": "#0a1628"}},
  {"command": "add", "parent": "/", "type": "slide", "props": {"title": "第二章", "text": "正文内容", "background": "#1a5276"}}
]
```

执行：
```bash
cat batch.json | officecli batch output.pptx
```

## 关键属性

| 属性 | 值示例 | 说明 |
|------|--------|------|
| title | "鬼蝠魟" | 幻灯片标题 |
| text | "正文\\n换行" | 正文，\\n换行 |
| background | "#0a1628" | 背景色 |
| layout | "Blank" | 布局（Blank=无模板元素） |

## 注意事项

- `create` 命令会激活一个驻留进程（resident process），后续命令更快
- 批量操作完用 `officecli close` 关闭驻留进程
- Batch JSON中不要在每个item里写"file"字段——file是batch命令的参数
- 中文需要设置 `font.ea` 属性指定东亚字体

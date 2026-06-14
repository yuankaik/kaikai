---
name: mediacrawler
description: 中文社交平台爬虫 (51K⭐)——小红书/抖音/B站/微博/快手/知乎/贴吧一站式采集。需要 Cookie + Playwright。
source: https://github.com/NanmiCoder/MediaCrawler
---

# MediaCrawler — 中文社交爬虫

## 支持平台

| 平台 | 内容 |
|------|------|
| 📕 小红书 | 笔记 + 评论 |
| 🎵 抖音 | 视频 + 评论 |
| 📺 B站 | 视频 + 评论 |
| 📢 微博 | 帖子 + 评论 |
| ⏩ 快手 | 视频 + 评论 |
| 💬 贴吧 | 帖子 + 回复 |
| ❓ 知乎 | 问答 + 评论 |

## 安装

```bash
cd /tmp/MediaCrawler
pip install -r requirements.txt
playwright install chromium
```

## 使用

需要平台 Cookie（浏览器 F12 复制）。

```bash
# 小红书
python main.py --platform xhs --lt qrcode

# 抖音
python main.py --platform dy --lt qrcode
```

## 注意

- 需要真实 Cookie
- 遵守平台 ToS
- 不要高频采集

---
name: crawl4ai
description: 本地 LLM 友好爬虫 (68K⭐)——爬网页→干净 Markdown。免费不限量，互补 firecrawl 的 500 次月额度。
source: https://github.com/unclecode/crawl4ai
---

# Crawl4AI — 本地爬虫

开源 Python 爬虫，专为 LLM 优化输出。

## 对比 firecrawl

| | crawl4ai | firecrawl |
|------|----------|-----------|
| 方式 | 本地 Python | SaaS API |
| 费用 | 免费无限 | 500 次/月 |
| 适用 | 批量大量爬取 | 快速单次抓取 |

## 安装

```bash
pip install crawl4ai
crawl4ai-setup  # 安装浏览器驱动
```

## 基础用法

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com")
        print(result.markdown)  # LLM 友好的 Markdown

asyncio.run(main())
```

## 高级功能

```python
# JS 渲染
result = await crawler.arun(url, js_code="window.scrollTo(0, document.body.scrollHeight)")

# CSS 选择器提取
result = await crawler.arun(url, css_selector="article")

# 结构化提取
result = await crawler.arun(url, extraction_strategy=JsonCssExtractionStrategy(...))
```

## 何时用哪个

- **firecrawl** — 快速原型、单页、搜索+抓取
- **crawl4ai** — 批量爬取、省钱、本地处理

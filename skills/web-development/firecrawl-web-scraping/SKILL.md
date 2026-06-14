---
name: firecrawl-web-scraping
description: 网页抓取与搜索——Firecrawl API (132K⭐)。爬取网页为 Markdown、搜索网络、批量抓取网站、提取结构化数据。需要 FIRECRAWL_API_KEY。
source: https://github.com/firecrawl/firecrawl
---

# Firecrawl 网页抓取

## 安装

```bash
pip install firecrawl-py
```

## 获取 API Key

1. 注册 https://firecrawl.dev
2. 免费额度：500 credits/月
3. 设置环境变量：`export FIRECRAWL_API_KEY=fc-xxxxx`

## 快速使用

### 单页抓取

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="your-key")

# 抓取为 Markdown
result = app.scrape_url("https://example.com")
print(result['markdown'])

# 抓取为结构化数据
result = app.scrape_url("https://example.com", 
    params={"formats": ["markdown", "html"]})
```

### 搜索网络

```python
# 搜索 + 自动抓取结果页
result = app.search("latest AI news", 
    params={"limit": 5})
for item in result['data']:
    print(item['url'], item['title'])
```

### 批量爬取网站

```python
# 爬取整个网站
result = app.crawl_url("https://docs.example.com",
    params={"limit": 50})
print(f"爬取了 {len(result['data'])} 页")
```

### 提取结构化数据

```python
# 用自然语言描述要提取的数据
result = app.extract(
    urls=["https://example.com/products"],
    params={
        "prompt": "提取所有产品名称和价格",
        "schema": {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "price": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
)
```

## 命令行使用

Firecrawl 安装后自带 CLI：

```bash
# 需要先设置 API Key
export FIRECRAWL_API_KEY=fc-xxxxx

# CLI 抓取
firecrawl scrape https://example.com
```

## 常见场景

| 场景 | 方法 |
|------|------|
| 看文章/文档内容 | `scrape_url` → Markdown |
| 搜索最新信息 | `search` |
| 批量爬文档站 | `crawl_url` |
| 提取商品/价格 | `extract` + schema |
| 监控网页变化 | `scrape_url` 定时调用 |

## 注意事项

- 免费版 500 credits/月，每次抓取 1 credit
- 需要网络能访问 firecrawl.dev
- 遵守目标网站的 robots.txt

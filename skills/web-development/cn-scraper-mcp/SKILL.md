---
name: cn-scraper-mcp
description: 中文平台搜索 MCP 服务——让 Hermes 原生搜索小红书/B站/微博/知乎/淘宝/京东等。安装、配置、登录全流程。
---

# cn-scraper-mcp — 中文互联网搜索 MCP

让 Hermes 直接搜索小红书、B站、微博、知乎、淘宝、京东、豆瓣、大众点评等 10+ 平台。

GitHub: goesByhc/cn-scraper-mcp

## 安装与接入

```bash
# 1. 安装
pip install cn-scraper-mcp

# 2. 接入 Hermes（非交互式）
yes | hermes mcp add --command cn-scraper-mcp --connect-timeout 30 cn-scraper

# 3. 重启 Hermes（/new 或重启进程）
```

40 个工具按门槛分三档：

| 门槛 | 平台 | 说明 |
|:---:|------|------|
| 🟢 免登录 | B站热门/视频/评论、微博热搜 | 开箱即用 |
| 🟡 需Cookie | 微博搜索、知乎搜索/热榜、豆瓣、大众点评、知识星球 | 扫码登录一次收割 Cookie |
| 🔴 需Chrome+Cookie | 小红书、抖音、京东、拼多多、淘宝 | 需本地 Chrome 运行中 |

## 平台登录（收割 Cookie）

### 方法一：guided_login（自动启动 Chrome）

```python
mcp__cn_scraper__guided_login(platform="xiaohongshu")  # 或 weibo, zhihu, douyin 等
```

→ Chrome 自动打开 → 用户扫码 → 自动收割 Cookie

### 方法二：手动启动 Chrome（WSL 环境）

当 `guided_login` 启动 Chrome 失败时使用。**这是最常走的路**——kai哥的 Chrome 平时不开，需要自己拉起来：

```bash
# 1. 手动启动 Chrome 开调试端口（background=true，不要用 nohup/&）
/usr/bin/google-chrome --remote-debugging-port=9251 --remote-allow-origins=* \
  --user-data-dir=/home/adminkaikai/.chrome-scrape \
  --no-first-run --no-default-browser-check \
  --disable-dev-shm-usage --disable-gpu about:blank

# 2. 【关键】必须开一个真实页面，about:blank 不算有效的 page target
curl -s -X PUT "http://127.0.0.1:9251/json/new?https://www.xiaohongshu.com"
# 验证：/json/list 里要能看到 type=page 且 url 是 https://...

# 3. 用户扫码登录后收割
mcp__cn_scraper__harvest_cookies(platform="xiaohongshu", port=9251)
```

**坑位清单（都踩过）：**

| 现象 | 原因 | 解法 |
|------|------|------|
| `XHS_BROWSER_UNAVAILABLE` | Chrome 未运行 | 用方法二拉起来 |
| `No page target found` | 只有 about:blank，没有真实页面 | `curl -X PUT .../json/new?URL` 开一个真页面 |
| `harvest_cookies` 报 `Unsupported platform '微博'` | platform 参数只吃**英文名** | 用 `weibo` 不是 `微博`；支持：`dianping douban douyin jd pdd taobao weibo xiaohongshu zhihu zsxq` |
| `xiaohongshu_search` 返回 `state: empty`（非 error） | 搜索请求通了，但 Cookie 太老无结果 / 关键词无命中 | 先换关键词验证；持续 empty 说明 Cookie 过期，重收割 |
| Chrome 前台启动被拒 | 工具禁止 shell 级 `nohup/&` 包装 | 用 `terminal(background=true)` |

启动 Chrome 建议加 `DISPLAY=:0`（WSLg），并保留 `--disable-dev-shm-usage`（WSL 下 /dev/shm 太小会崩）。

Cookie 保存在 `~/.cn-scraper-cookies/<platform>.json`，验证：

```python
mcp__cn_scraper__check_cookies()
```

### 已验证可用的登录平台

- **小红书**：需要 Chrome（住宅IP），Cookie 字段 web_session + a1
- **微博**：需要 Chrome，Cookie 字段 SUB
- **知乎**：需要 Chrome，Cookie 字段 z_c0 + d_c0

## 常用搜索示例

```python
# B站（免登录）
mcp__cn_scraper__bilibili_popular(limit=5)
mcp__cn_scraper__bilibili_search(keyword="溪流钓", limit=5)
mcp__cn_scraper__bilibili_comments(bvid="BV...")

# 微博
mcp__cn_scraper__weibo_hot_list()                          # 免登录热搜
mcp__cn_scraper__weibo_search(keyword="大明山民宿", limit=5)  # 需Cookie

# 小红书（需Cookie+Chrome）
mcp__cn_scraper__xiaohongshu_search(keyword="大明山溪流钓", limit=5)
mcp__cn_scraper__xiaohongshu_note(note_id="...", xsec_token="...")

# 知乎（需Cookie）
mcp__cn_scraper__zhihu_search(keyword="...", limit=5)
mcp__cn_scraper__zhihu_hot_list()
```

## Cookie 生命周期

Cookie 文件保存在 `~/.cn-scraper-cookies/<platform>.json`，跨 Hermes 会话持久化。下次重启直接可用，无需重新登录。

但在平台端会过期：

| 平台 | 预估有效期 | verify_login 支持 |
|------|:--:|:--:|
| 微博 | 数周~数月 | ✅ 返回 verified |
| 知乎 | 数周 | ✅ 返回 verified |
| 小红书 | 数天~数周 | ⚠️ 返回 unsupported（但不影响使用） |

**Cookie 过期后无需重新扫码**——只要 Chrome 里的登录态还在（通常比 Cookie 文件活得更久），直接 `harvest_cookies` 几秒钟就恢复：

```python
# 重新收割（前提：Chrome 在 9251 端口运行且该平台仍登录着）
mcp__cn_scraper__harvest_cookies(platform="xiaohongshu", port=9251)
```

如果 Chrome 也没有登录态了，才需要重新 `guided_login` 扫码。

## 诊断

```python
mcp__cn_scraper__diagnose()       # 全面诊断：Chrome/依赖/Cookie/最近错误
mcp__cn_scraper__check_cookies()  # 各平台 Cookie 状态
mcp__cn_scraper__verify_login(platform="weibo")  # 远端验证登录态（微博/知乎可用，小红书不支持）
```

## 知乎文章提取（type: article）

知乎搜索结果中 `type: article` 的文章（zhuanlan.zhihu.com）不能用 `zhihu_answer`（只处理 `type: answer`）。需要 CDP websocket 提取：

```python
import asyncio, json, websockets, subprocess

# 1. 导航到文章（Chrome 需运行在 9251 端口且已登录知乎）
subprocess.run(['curl', '-s', '-X', 'PUT', 
    'http://127.0.0.1:9251/json/new?https://zhuanlan.zhihu.com/p/ARTICLE_ID'], 
    capture_output=True)

# 2. 等待加载
await asyncio.sleep(4)

# 3. 通过 CDP websocket 提取
result = subprocess.run(['curl', '-s', 'http://127.0.0.1:9251/json'], capture_output=True, text=True)
tabs = json.loads(result.stdout)
ws_url = next(t['webSocketDebuggerUrl'] for t in tabs if 'zhuanlan.zhihu.com' in t.get('url',''))

async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
    cmd = {'id': 1, 'method': 'Runtime.evaluate', 'params': {
        'expression': 'document.body.innerText', 'returnByValue': True}}
    await ws.send(json.dumps(cmd))
    resp = await ws.recv()
    text = json.loads(resp)['result']['result']['value']
```

注意：需安装 `pip install websockets`。

## 搜索策略（按用途）

| 用途 | 首选平台 | 工具 | 原因 |
|------|------|------|------|
| 教育资料（词汇表、知识点） | 知乎 | zhihu_search | 长文干货多，有整理好的汇总 |
| 实战经验（民宿、钓点） | 小红书 + 微博 | xiaohongshu_search, weibo_search | 真实用户分享 |
| 实时讨论/热搜 | 微博 | weibo_hot_list | 免登录 |
| 视频内容 | B站 | bilibili_popular/search | 免登录 |

### 教育资料搜索模式

找课标词汇表/生字表/古诗词篇目等教育资料时，三平台同时搜可提高命中率：

```python
# 一轮并行搜索（互不依赖）
mcp__cn_scraper__zhihu_search(keyword="部编版 五年级上册 生字表 拼音", limit=10)
mcp__cn_scraper__xiaohongshu_search(keyword="上海小学语文 生字表", limit=10)
mcp__cn_scraper__weibo_search(keyword="五年级上册 词语表", limit=10)
```

知乎命中率最高（长文整理多），找到文章 ID 后用 CDP websocket 提取正文（见"知乎文章提取"章节）。微博和小红书通常无结果或只有简介，但偶尔有惊喜。

上海教材注意：
- **英语**：沪教版牛津（上海版），非人教版
- **语文**：部编版/统编版（全国统一），上海也用
- 搜索用 "部编版" 或 "统编版" 比 "沪教版" 命中率高很多（中文教材已统一）

## 已知问题

- **B站搜索 HTTP 412**：反爬拦截，**常常持续整个会话**（不是偶发）。实测时 `bilibili_search` 反复 412，但 `bilibili_popular` 完全正常。**策略：B站搜索挂了就换平台，别硬试**——教育/育儿类话题知乎覆盖度更好，直接用知乎。
- **`state: empty` ≠ `state: error`**：empty 表示请求成功但零结果（关键词不命中或 Cookie 太老）；error 才是技术故障。看到 empty 别急着改代码，先换个关键词排除关键词因素。
- **知乎文章提取**：`zhihu_answer` 只能处理 type: answer，type: article 文章必须走 CDP websocket 提取（见上方"知乎文章提取"章节）。部分 answer 会返回 404 或"知乎需要登录"——那是**单条**的权限问题，重试别的条目即可，不代表整体失效。
- **CDP 提取依赖**：需 `pip install websockets`，且 Chrome 必须保持运行且已登录目标平台
- **WSL Chrome**：需要 WSLg 支持图形窗口，`DISPLAY=:0` 需可用。`guided_login` 失败时用方法二手动启动
- **Cookie 过期**：各平台时效不同，微博/知乎通常数周到数月，小红书较短。过期后先尝试 harvest_cookies（无需扫码），不行再 guided_login（需扫码）
- **知乎 curl 直连 403**：知乎 API 对非浏览器请求返回 40362，必须走 Chrome CDP 或 cn-scraper-mcp 的 zhihu_search 工具

## 降级策略（核心经验）

**多平台调研时，永远不要因为一个平台挂了就停下整个任务。** 本次实测的平台健康度顺序：

| 平台 | 健康度 | 备注 |
|------|:--:|------|
| 知乎 | ★★★★★ | 最稳。搜索+answer全文都可用，无需 Chrome |
| B站热门 | ★★★★ | 免登录可用 |
| B站搜索 | ★ | 412 高发，别依赖 |
| 小红书 | ★★ | 强依赖 Chrome+Cookie 新鲜度 |
| 微博搜索 | ★★ | 需登录 Cookie |
| 抖音 | ★ | 需 Chrome+Cookie，本机常年无 |

**结论：中文深度内容调研，知乎是主力，其他平台是补充。** 报告里要如实标注哪些平台没抓到、为什么（Cookie 过期 ≠ 数据不存在）。

## 输出规范（kai哥偏好）

调研结果交付时必须包含：
1. **诚实汇报平台状态**——哪个抓到了、哪个没抓到、卡在哪一步、怎么恢复。不要假装全绿。
2. **明说需要用户做什么**（如"需扫码登录一次才能恢复小红书"），但**不要为了这个停下来问**，把报告先交付，把可选项放在最后。
3. 文件落桌面（`/mnt/c/Users/admin/Desktop/`），**PDF + MD 双份**（weasyprint 生成 PDF，需中文字体）。

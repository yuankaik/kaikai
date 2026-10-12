---
name: cn-platform-full-stack
description: 中文平台全栈搜索——cn-scraper-mcp（知乎/微博/抖音/小红书/B站）+ 百度/贴吧/搜狗 直连方案 + 微信通道。当需要跨平台调研中文信息（教育/育儿/本地/政策）时使用。含各平台可用性实测矩阵、登录收割流程、CDP 浏览器兜底。
---

# 中文平台全栈搜索

## 触发条件
- 跨平台调研中文信息（教育、育儿、本地、政策、产品口碑）
- cn-scraper-mcp 某平台不可用，需要兜底方案
- 需要登录/刷新平台 cookie
- 百度、贴吧、搜狗搜索（MCP 不覆盖）

## 一、能力矩阵（实测，2026-09-21）

### cn-scraper-mcp 覆盖（10 平台）

| 平台 | 免登录工具 | 需登录工具 | 实测状态 |
|------|-----------|-----------|---------|
| 知乎 | — | `zhihu_search`, `zhihu_answer`, `zhihu_question_answers`, `zhihu_comments` | ✅ cookie 可存活 50+ 天 |
| 微博 | `weibo_hot_list` ✅ | `weibo_search`, `weibo_user_timeline`, `weibo_comments` | 热搜免登；搜索需 SUB token |
| 抖音 | — | `douyin_search`, `douyin_hot_list`, `douyin_video` | ❌ 需 sessionid |
| 小红书 | — | `xiaohongshu_search`, `xiaohongshu_note`, `xiaohongshu_comments` | 需本地 Chrome + 住宅 IP |
| B站 | `bilibili_popular` ✅ | `bilibili_search`(⚠️412), `bilibili_video`, `bilibili_comments` | 热门稳；搜索常 412 |
| 豆瓣 | — | `douban_search`, `douban_subject`, `douban_reviews` | 可能风控 |
| 大众点评 | — | `dianping_search`, `dianping_shop`, `dianping_reviews` | 可能风控 |
| 淘宝/京东/拼多多 | — | 对应 search/product | 需 cookie / 有头 Chrome |
| 知识星球 | — | `zsxq_topics`, `zsxq_article` | 需 zsxq_access_token |

**不存在于 MCP**：百度搜索、百度贴吧、微信、微信读书 → 见第二、三节。

### ⚠️⚠️ 关键缺陷：`xiaohongshu_search` 恒返回 `XHS_EMPTY`（已找到根因并修复）

**这是 cn-scraper-mcp v0.5.0 的 bug，不是登录问题。**
症状：浏览器里明明登录且搜索结果满屏，`xiaohongshu_search` 却永远返回
`{"state":"empty","count":0}`（任何关键词都一样）。

**根因（已实测确认）**：
引擎用 `document.body.innerText` 提取搜索结果。但小红书搜索页的卡片文字
渲染在 `innerText` 抓不到的容器里 —— 页面实际有 40+ 卡片，`innerText`
却只返回侧边栏+页脚（约 200 字符）。引擎拿不到卡片 → 误判"无结果"。

**修复方案：改用 DOM 选择器直读卡片**，写成独立脚本：
```bash
python3 ~/.hermes/skills/web-development/cn-platform-full-stack/scripts/xhs_search.py "上海 五年级 作息" --limit 10
# → 卡片 22 | 去重 20，含标题/作者/点赞/noteId/URL
```

**关键参数**：
- 等待时间 **≥8 秒**（MCP 硬编码 5s 太短，XHS 走签名 XHR 异步加载）
- 选择器：`section.note-item, div.note-item` 为卡片容器
- noteId 从 `a[href*="/explore/"]` 正则提取 16+ 位十六进制

**拿到的 noteId + href 可直接喂给 MCP 的 `xiaohongshu_note`**（需配 xsec_token）。

---

小红书即使浏览器里是登录态，MCP 仍可能返回 `XHS_EMPTY`（"未找到相关笔记"）。
**诊断顺序**：
1. 先 `browser_navigate` 打开 `https://www.xiaohongshu.com/explore`，用 `Page.captureScreenshot` 看侧边栏有没有「我」的头像
2. 有头像 = 浏览器已登录 → 问题在 cookie 文件不同步
3. 跑 `harvest_cookies(platform="xiaohongshu", port=9251)` 从活浏览器会话收割（本次收到 17 个 cookie）
4. 若仍 empty → 检查是否 `xsec_token` 缺失；XHS 搜索需要先访问搜索页拿到 token

## 二、百度 / 贴吧 / 搜狗（MCP 不覆盖，直连）

### 百度搜索 ✅ 直连可用（实测 2026-09-21 通过）
```bash
python3 ~/.hermes/skills/web-development/cn-platform-full-stack/scripts/cn_search.py baidu "上海五年级 作业量"
# → status 200, 12 条结果，标题+URL 完整，无验证码
```
实测 HTTP 200，94 万字符，无验证码。**前提：用 urllib/requests + 真实 UA 直连，不要用无头浏览器**（会触发 wappass）。

⚠️ 百度结果 URL 多为 `baidu.php?url=` / `link?url=` 跳转，需跟一次 301 拿真实地址。

### 搜狗 ✅ 直连可用（中文长尾词最好，实测通过）
```bash
python3 .../cn_search.py sogou "上海 五年级 数学 沪教版"
# → status 200, 11 条，含沪教版教材/知识点归纳
```
结果链接是 `/link?url=` 跳转，需跟一次拿真实 URL。

### 百度文库/知道/百科 ✅ 用 site: 限定
```bash
python3 .../cn_search.py baidu_doc "沪教版五年级数学知识点"
```

### 百度贴吧 ❌ 直连 403，必须走浏览器会话
- 直接 urllib/requests → **403 Forbidden**（带 Referer/UA 也一样）
- CDP 浏览器打开 → **百度安全验证**（未登录状态下也拦）
- **正解**：在已登录百度的 Chrome profile 里访问，或先 `guided_login` 登录百度
- 流程：登录 passport.baidu.com → 贴吧自动带过（同账号体系）

## 三、登录与 Cookie 收割流程

### 标准流程（推荐）
```bash
# 1. 启动带 CDP 的 Chrome（WSL 下必须显式指定 port 和 user-data-dir）
google-chrome --remote-debugging-port=9251 \
  --user-data-dir=/home/<user>/.chrome-scrape \
  --no-first-run --no-default-browser-check --no-sandbox \
  --disable-dev-shm-usage &
# 用 background=true 启动，不要用 nohup（Hermes 会拒）

# 2. 确认端口
curl -s http://127.0.0.1:9251/json/version   # 应返回 Chrome 版本 JSON

# 3. ⚠️ 关键：about:blank 不算有效 page target
#    必须先打开真实页面，否则报 "No page target found"
curl -s -X PUT "http://127.0.0.1:9251/json/new?https://www.xiaohongshu.com"

# 4. 打开各平台登录页，让用户扫码
curl -s -X PUT "http://127.0.0.1:9251/json/new?https://weibo.com/login.php"

# 5. 收割
harvest_cookies(platform="xiaohongshu", port=9251)
```

### platform 名称（必须用英文）
`dianping, douban, douyin, jd, pdd, taobao, weibo, xiaohongshu, zhihu, zsxq`
—— 传中文（如 `"微博"`）会报 `Unsupported platform`。

### guided_login 可能报 `An unexpected error occurred`
WSL 下 `guided_login` 不稳定 → 直接走上面的手动 CDP + `harvest_cookies` 路径。

## 四、CDP 浏览器：截图 + 读页面（无需 vision 模型）

浏览器里看页面状态，比反复试 MCP 工具快得多：

```python
import urllib.request, json, websockets, asyncio, base64, time

def tabs():
    return json.loads(urllib.request.urlopen("http://127.0.0.1:9251/json/list", timeout=8).read())

async def cmd(ws, method, params=None, _id=1):
    async with websockets.connect(ws, max_size=80*1024*1024) as c:
        await c.send(json.dumps({"id":_id,"method":method,"params":params or {}}))
        while True:
            m = json.loads(await c.recv())
            if m.get("id")==_id: return m

# 截图（拿到真实渲染）
r = asyncio.run(cmd(ws_url, "Page.captureScreenshot", {"format":"png"}))
open("/tmp/shot.png","wb").write(base64.b64decode(r["result"]["data"]))

# 读渲染后文本（判断是否登录/风控，比截图更快）
r = asyncio.run(cmd(ws_url, "Runtime.evaluate",
    {"expression":"document.title+'|||'+document.body.innerText.slice(0,900)",
     "returnByValue":True}))
```

**风控识别特征**：`document.title` 出现 "百度安全验证" / "验证码" → 该 profile 未登录该平台。

## 五、微信通道（独立于 MCP）

- 配置在 `~/.hermes/config.yaml` → `weixin.home_channel` + `weixin.token`（iLink）
- **限频极严**：禁止高频 `send_message` 到 weixin
- 非 cron 场景下，结果直接在聊天里回复，不要额外推送

## 六、铁律

- **有 MCP 用 MCP，没有就用直连 HTTP，最后才用浏览器**（浏览器最慢）
- **百度/搜狗直连优于浏览器**（浏览器会触发验证码，curl 不会）
- **贴吧是唯一必须走浏览器会话的**
- **同工具连败 3 次 → 立刻换平台**，不要在同一路径空转
- **登录一次收割全部**：一次 Chrome 会话把所有平台扫完，再统一 `harvest_cookies`
- **cookie 会过期**：知乎能活 50+ 天；小红书/微博 1-2 周需重收割

## 相关技能
- `chinese-social-search` — cn-scraper-mcp 安装配置与基础用法
- `chinese-web-search` — 搜索引擎选型 + 政务/拆迁信息渠道
- `cn-scraper-mcp-usage` — MCP 工具操作细节

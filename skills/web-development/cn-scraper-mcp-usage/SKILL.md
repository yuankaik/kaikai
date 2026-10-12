---
name: cn-scraper-mcp-usage
description: 中文平台搜索 MCP 工具使用指南——cn-scraper-mcp 接入 Hermes 后的完整操作流程，包括 Cookie 收割、平台特性、已知陷阱。
---

# cn-scraper-mcp 使用指南

## 已接入平台

| 门槛 | 平台 | 关键工具 |
|:--:|------|------|
| 🟢 免登录 | B站热门/视频/评论、微博热搜 | bilibili_popular, weibo_hot_list |
| 🟡 需Cookie | 知乎搜索/问答、微博搜索、豆瓣、大众点评 | zhihu_search, weibo_search |
| 🔴 需Chrome+Cookie | 小红书、抖音、京东、拼多多 | xiaohongshu_search, douyin_search |

## Cookie 收割流程

### 方法一：guided_login（推荐，但 WSL 需手动处理）

```
mcp__cn_scraper__guided_login(platform="xiaohongshu")
```

WSL 环境下 guided_login 可能因 Chrome 启动失败。改为手动：
1. 终端启动 Chrome: `google-chrome --remote-debugging-port=9251 --no-first-run --user-data-dir=/tmp/xhs-profile "https://www.xiaohongshu.com"`
2. 用户扫码登录
3. `mcp__cn_scraper__harvest_cookies(platform="xiaohongshu", port=9251)`

### 方法二：手动 CDP（guided_login 失败时）

```bash
# 启动 Chrome
google-chrome --remote-debugging-port=9251 --no-first-run \
  --user-data-dir=/tmp/chrome-profile "https://目标网站" &

# 确认监听
ss -tlnp | grep 9251

# 导航到新页面（之后收割Cookie）
curl -s -X PUT "http://127.0.0.1:9251/json/new?https://目标URL"
```

### 微博/知乎（同一 Chrome 会话连续收割）

Chrome 开着不关，依次导航→扫码→收割：
1. 导航微博登录页 → 扫码 → harvest_cookies("weibo", port=9251)
2. 导航知乎登录页 → 扫码 → harvest_cookies("zhihu", port=9251)

## 平台特性与陷阱

### 知乎文章提取（CDP websocket）

`zhihu_answer` 只能读"回答"（type=answer），不能读"文章"（type=article）。

⚠️ **失败方式是静默的 HTTP 404，不是友好报错。** 传入 article 的 id（`zhihu_search` 结果里 `type:"article"` 那类的 id）会返回 `{"error":"HTTP 404"}`。
**所以：调用前先看搜索结果里的 `type` 字段 —— 只有 `"answer"` 才传给 `zhihu_answer`。** 传错 3 次会触发 loop 警告，白费轮次。

文章正文的替代读法（按代价从低到高）：
1. `zhihu_search` 的 `excerpt` 字段本身常含关键句（本次 SHEIN 的时间表就是先从 excerpt 拿到的）——**先换关键词多搜几轮拼 excerpt**，成本最低
2. CDP websocket 提取（见下）
3. ⚠️ 别用 curl 抓 `zhuanlan.zhihu.com/p/<id>` —— 返回 650 字节反爬空页

```python
import asyncio, json, subprocess, websockets

async def extract_article(url_pattern):
    result = subprocess.run(['curl', '-s', 'http://127.0.0.1:9251/json'],
                           capture_output=True, text=True)
    tabs = json.loads(result.stdout)
    ws_url = None
    for t in tabs:
        if url_pattern in t.get('url', ''):
            ws_url = t.get('webSocketDebuggerUrl')
            break
    
    async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
        cmd = {'id': 1, 'method': 'Runtime.evaluate', 'params': {
            'expression': 'document.querySelector(".Post-RichText") ? document.querySelector(".Post-RichText").innerText : document.body.innerText',
            'returnByValue': True}}
        await ws.send(json.dumps(cmd))
        for _ in range(5):
            resp = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(resp)
            if data.get('id') == 1:
                return data['result']['result'].get('value', '')
```

需要 `pip install websockets`（可能被 externally-managed 拒绝，已安装在全局）。

知乎 Cookie JSON 格式为 `{name: value}` 键值对，不是 Netscape 格式。转为 curl cookie string：`'; '.join(f'{k}={v}' for k,v in cookies.items())`

### 小红书
- ⚠️⚠️ **`xiaohongshu_search` 恒返回 `XHS_EMPTY` 是 cn-scraper-mcp v0.5.0 的 bug，不是关键词问题、不是登录问题。**
  **不要**按旧建议"缩短关键词"重试 —— 换任何关键词（包括"育儿"这种超宽词）都一样返回 empty。
  **根因（实测确认）**：引擎用 `document.body.innerText` 提取搜索结果，但小红书搜索页的卡片文字
  渲染在 `innerText` 抓不到的容器里 —— 页面实际有 42 个卡片，`innerText` 却只返回侧边栏+页脚（约 200 字符）。
  引擎拿不到卡片 → 误判"无结果"。
  **修复**：用 `scripts/xhs_search.py`（DOM 选择器直读卡片，等待 ≥8s）。
  详见 `cn-platform-full-stack` skill。
- **判断"到底是不是登录问题"的方法**：`XHS_EMPTY` 无法区分"没登录"和"抓不到"。
  去浏览器里看：CDP 截图 `https://www.xiaohongshu.com/explore`，侧边栏底部出现
  「我」+头像 = 已登录。已登录还返回 empty ⇒ 100% 是上面那个 bug。
- 笔记内容通过 `xiaohongshu_note` 获取，需要 note_id + xsec_token（都来自搜索结果）
- **图文笔记图片文字盲区**：`xiaohongshu_note` 只返回文字字段（标题/正文/评论），图片里的文字（截图、手写、排版图）抓不到。补盲方案：拿笔记详情返回的图片 URL → 下载 → `vision_analyze`（auxiliary.vision 已配 deepseek-flash，原生多模态实测准）或本机 Pix2Text（`source ~/ocr_env/bin/activate && p2t predict -i <图>`）提取文字。手写/截图优先 vision，印刷体优先 Pix2Text。

### 微博
- `weibo_hot_list` 免登录
- `weibo_search` 需 Cookie（SUB token）
- 搜索结果偏实时/推广，长文深度内容不如知乎

### B站
- `bilibili_popular` 最稳定，免登录
- `bilibili_search` 可能返回 HTTP 412（临时故障），重试或改用热门

## 多平台搜索策略

当用户需要搜索中文内容时，**必须同时搜索三平台**：

| 平台 | 擅长 | 使用场景 |
|------|------|------|
| 小红书 | 育儿实操、消费决策、生活方式 | 搜教育方法、民宿、产品评测 |
| 知乎 | 深度长文、方法论、系统知识 | 搜理论分析、习惯养成、学习方法 |
| 微博 | 实时热点、最新动态 | 搜热搜、实时事件 |

禁止只搜一个平台。三平台结果交叉验证，取各自最强的领域。

## Cookie 持久性

| 平台 | 验证方式 | 估计有效期 |
|------|:--:|------|
| 微博 | verify_login 支持 | 数周~数月 |
| 知乎 | verify_login 支持 | 数周 |
| 小红书 | verify_login 不支持 | 数天~数周 |

过期后无需重新扫码——只要 Chrome 登录态还在，直接 harvest_cookies 即可。

### ⚠️ Cookie 有效时的"间歇性登录错误"

**报错 `{"error":"知乎搜索需要登录"}` 不等于 Cookie 真的失效。** 同一会话内连续
快速调用知乎搜索会发现：**上一个查询成功、下一个就报需要登录、再下一个又成功**。
这是平台的**频率限制**，不是 Cookie 过期。

判断与处理：
- 先看同一轮里别的平台是否正常（微博热搜免登录，永远能调，可当"网络/工具是否正常"的探针）
- **不要**因为一次报错就跳去 harvest_cookies 或 guided_login —— 那是白费一轮
- 稍等几秒重试，或**换关键词**重试（往往就通了）
- 只有**连续多次**、跨关键词都失败，才判定为 Cookie 过期

> 实测（SHEIN/地平线调研）：知乎 cookie 在 1 次成功查询后立刻报"需要登录"，
> 换关键词重搜即恢复。若当时误判为过期去收割，会浪费大量轮次。

### 失败 3 次立刻换路子（通用铁律）
单一工具/接口连续失败 3 次 ⇒ 停止在同一条路上试参数组合，**换渠道或换思路**。
本次在港交所 `titleSearchServlet` 的 `stockId` 参数上试了 8+ 种组合全返回 0 条 ——
正确做法是**第一次确认 0 条就转回退栈**（东财 F10 / 腾讯行情 / 新浪财报）。

## 诊断

`mcp__cn_scraper__diagnose()` — 检查所有依赖、Cookie 状态、CDP 端口、最近错误。

## CDP 浏览器驱动（排查利器）

**当平台工具返回空/报错时，别猜参数 —— 直接看渲染后的页面。**
详见 `references/cdp-browser-diagnostics.md`，含：
- 从 Python 直连 CDP 读渲染文本 / 截图 / 查 cookie 的完整代码
- DOM 选择器 vs `innerText` 的区别（**后者抓不到 ≠ 页面没有**）
- 风控特征识别表（安全验证 / IP风险 / login 跳转 / HTTP 412）
- `about:blank` 不算有效 page target 这个坑
- 实战复盘：用这套方法定位了 XHS_EMPTY 根因

## 一次会话打通多平台（实测流程）

一次 Chrome 会话把所有平台扫完，再统一收割 —— 不要一个平台开一次浏览器。

```bash
# 1. 启动（background=true）
google-chrome --remote-debugging-port=9251 --user-data-dir=~/.chrome-scrape \
  --no-first-run --no-default-browser-check --disable-dev-shm-usage &
# 2. 打开所有登录页（about:blank 不算有效 target，必须打开真实 URL）
for u in https://weibo.com/login.php https://www.douyin.com https://passport.baidu.com/v2/?login; do
  curl -s -X PUT "http://127.0.0.1:9251/json/new?$u"; done
# 3. 让用户扫码（百度登录后贴吧自动带过——同账号体系）
# 4. 逐个收割
harvest_cookies(platform="weibo", port=9251)
harvest_cookies(platform="xiaohongshu", port=9251)
```

**关键点**：
- `harvest_cookies` 的 platform 必须用**英文**（`weibo` 不是 `微博`，传中文报 `Unsupported platform`）
- 收割前先用 `Network.getAllCookies` 确认目标 cookie 存在（`SUB`/`BDUSS`/`web_session`/`sessionid`），
  避免对没登录的平台白跑一次收割
- 知乎 cookie 存活最久（实测 50+ 天），可免扫码复用
- 收尾用 `Browser.close` 关 CDP 实例；cookie 已落盘，关浏览器不影响

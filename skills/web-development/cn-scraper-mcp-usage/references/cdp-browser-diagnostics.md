# CDP 浏览器驱动：诊断页面/登录态/风控

用 Python 直连 Chrome DevTools Protocol，读**渲染后**的页面状态。
这是排查"平台工具返回空/报错"时最有效的手段 —— 能看到真相，而不是猜参数组合。

## 何时用

- MCP 工具返回 `XHS_EMPTY` / 空结果，但要判断**到底是没登录、被风控、还是抓取器坏了**
- 需要确认某平台在浏览器里是否**真的**已登录
- 直连 HTTP 被 403 / 触发安全验证，需要看页面实际显示了什么
- 从动态渲染页面（签名 XHR 加载）提取结构化数据

## 前提：Chrome 带 CDP 端口运行

```bash
google-chrome --remote-debugging-port=9251 \
  --user-data-dir=/home/<user>/.chrome-scrape \
  --no-first-run --no-default-browser-check \
  --disable-dev-shm-usage &
```
- **必须用 `terminal(background=true)` 启动**，不要用 `nohup`/裸 `&`（Hermes 会拒）
- 验证：`curl -s http://127.0.0.1:9251/json/version` → 应返回 Chrome 版本 JSON

### ⚠️ 坑：`about:blank` 不算有效 page target

新开的 Chrome 只有 `about:blank` 时，CDP 客户端会报
`No page target found. Is Chrome running with --remote-debugging-port?` —— 极具误导性
（Chrome 明明在跑）。**解法：先打开一个真实 URL。**

```python
urllib.request.Request("http://127.0.0.1:9251/json/new?https://www.example.com", method="PUT")
```

## 核心三招

```python
import urllib.request, json, websockets, asyncio, base64

def tabs():
    return json.loads(
        urllib.request.urlopen("http://127.0.0.1:9251/json/list", timeout=8).read().decode())

async def cmd(ws, method, params=None, _id=1):
    async with websockets.connect(ws, max_size=80*1024*1024) as c:
        await c.send(json.dumps({"id": _id, "method": method, "params": params or {}}))
        while True:
            m = json.loads(await c.recv())
            if m.get("id") == _id:
                return m

ws = next(t["webSocketDebuggerUrl"] for t in tabs() if t.get("type") == "page")

# ① 读渲染后文本 + 标题（最快，判断风控/登录）
r = asyncio.run(cmd(ws, "Runtime.evaluate", {"expression":
    "document.title + '|||' + (document.body ? document.body.innerText.slice(0,900) : '')",
    "returnByValue": True}))
print(r["result"]["result"]["value"])

# ② 截图（看实际渲染，可喂 vision_analyze）
r = asyncio.run(cmd(ws, "Page.captureScreenshot", {"format": "png"}))
open("/tmp/shot.png", "wb").write(base64.b64decode(r["result"]["data"]))

# ③ 查所有 cookie（判断各平台登录态，不用猜）
r = asyncio.run(cmd(ws, "Network.getAllCookies"))
for c in r["result"]["cookies"]:
    if c["name"] in ("SUB", "BDUSS", "sessionid", "web_session", "z_c0"):
        print(c["name"], c["domain"])
```

## 用 DOM 选择器提取动态内容（而不是 innerText）

**核心教训**：`innerText` 抓不到的内容 ≠ 页面没有内容。
小红书搜索页有 42 个卡片，`innerText` 只返回约 200 字符的侧边栏+页脚。

```python
EXTRACT = r"""
(function(){
  var out=[];
  document.querySelectorAll('section.note-item, div.note-item').forEach(function(c){
    var a = c.querySelector('a[href*="/explore/"], a[href*="/search_result/"]');
    var m = a && a.getAttribute('href').match(/\/(?:explore|search_result)\/([0-9a-f]{16,})/);
    var t = c.querySelector('.title, [class*="title"]');
    out.push({noteId: m?m[1]:'', title: t?t.innerText.trim():'', href: a?a.getAttribute('href'):''});
  });
  return JSON.stringify({cards: out.length, items: out});
})()
"""
r = asyncio.run(cmd(ws, "Runtime.evaluate", {"expression": EXTRACT, "returnByValue": True}))
data = json.loads(r["result"]["result"]["value"])
```

**排查顺序**：先用 `innerText` 看文本 → 若文本明显偏少但你知道页面有内容 →
改用 DOM 选择器 / `querySelectorAll(...).length` 计数验证。
**计数 > 0 但取不到文本 = 提取方式错了，不是页面空。**

## 等待时间

动态页面（签名 XHR 异步加载）**等 8 秒**，不要用 5 秒。
可作健康信号：卡片数随时间增长（实测 5s→30 卡片，8s→42 卡片）。

## 风控特征识别

| 现象 | 含义 |
|------|------|
| `document.title` 含「安全验证」「验证码」 | 该 profile 未登录该平台，触发人机校验 |
| `innerText` 含 `error_code=300012` / `IP存在风险` | 数据中心 IP，需住宅 IP + 本地 Chrome |
| URL 含 `login` / `passport` | 登录态失效 |
| HTTP 412 | 平台级反爬限流（B站搜索常见），重试或换接口 |

## 清理

```python
asyncio.run(cmd(ws, "Browser.close"))   # 优雅关闭 CDP 实例
```
用独立 `--user-data-dir` 启的实例，关闭**不影响**用户日常 Chrome，也不影响已落盘的 cookie。

## 实战：靠它定位了 XHS_EMPTY 根因

1. `xiaohongshu_search` 对所有关键词恒返回 empty → 怀疑登录失效
2. CDP 截图 `/explore` → 侧边栏有「我」+头像 → **证明已登录**，推翻登录假设
3. harvest_cookies 拿到 17 个新鲜 cookie → 重试仍 empty → 推翻 cookie 假设
4. CDP 跑 `querySelectorAll('.note-item').length` → **42 个卡片**，但 `innerText` 只有 200 字符
5. 结论：提取器缺陷（`innerText` 抓不到卡片文字），不是数据问题
6. 改用 DOM 选择器 → 稳定拿到 20+ 条完整笔记

**教训**：三次"换参数"不如一次"看真相"。

#!/usr/bin/env python3
"""
百度 / 搜狗 直连搜索（无反爬，无需浏览器，无需登录）。
百度贴吧需要浏览器会话，见 tieba_via_cdp()。

用法:
    python3 cn_search.py baidu "上海五年级 学习"
    python3 cn_search.py sogou "上海五年级"
    python3 cn_search.py tieba "小学五年级"   # 需先启动 CDP Chrome 并登录百度
"""
import sys, re, ssl, gzip, json, urllib.request, urllib.parse, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

CDP = "http://127.0.0.1:9251"
STOP = ["为您推荐", "相关搜索", "百度热搜", "大家还在搜", "下载百度", "使用百度前必读"]


def _fetch(url, params=None, headers=None, timeout=20):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    h = {"User-Agent": UA,
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language": "zh-CN,zh;q=0.9",
         "Accept-Encoding": "gzip, deflate"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return r.status, raw.decode("utf-8", "ignore")


def _clean(t):
    return re.sub(r"\s+", " ", re.sub("<[^>]+>", "", t)).strip()


def search_baidu(q, limit=12):
    """百度直连。实测无反爬，不要用无头浏览器（会触发 wappass 验证）。"""
    st, body = _fetch("https://www.baidu.com/s", {"wd": q})
    out = []
    # 标题块
    for m in re.finditer(r'<h3[^>]*>(.*?)</h3>', body, re.S):
        block = m.group(1)
        a = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        if not a:
            continue
        title = _clean(a.group(2))
        href = a.group(1)
        if not title or any(s in title for s in STOP):
            continue
        out.append({"title": title, "url": href})
        if len(out) >= limit:
            break
    return {"engine": "baidu", "query": q, "status": st, "count": len(out), "items": out}


def search_sogou(q, limit=12):
    """搜狗直连，中文长尾词（地址/地名/小区）匹配最好。链接是 /link?url= 跳转。"""
    st, body = _fetch("https://www.sogou.com/web", {"query": q})
    out = []
    for m in re.finditer(r'<h3[^>]*>(.*?)</h3>', body, re.S):
        block = m.group(1)
        a = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        if not a:
            continue
        title = _clean(a.group(2))
        href = a.group(1)
        if href.startswith("/link"):
            href = "https://www.sogou.com" + href
        if not title or any(s in title for s in STOP):
            continue
        out.append({"title": title, "url": href})
        if len(out) >= limit:
            break
    return {"engine": "sogou", "query": q, "status": st, "count": len(out), "items": out}


def search_baidu_doc(q, limit=10):
    """百度文库 / 知道 / 百科 等站内（走百度通用搜索带 site 限定）。"""
    return search_baidu(f"{q} (site:wenku.baidu.com OR site:zhidao.baidu.com OR site:baike.baidu.com)", limit)


# ---------- 贴吧：必须浏览器会话 ----------

def tieba_via_cdp(keyword, port=9251, wait=8):
    """
    贴吧直连 403、无头浏览器触发「百度安全验证」。
    正解：在已登录百度的 CDP Chrome 里打开，读渲染后文本。
    返回帖子标题列表。
    """
    import websockets, asyncio, base64
    base = f"http://127.0.0.1:{port}"
    url = "https://tieba.baidu.com/f?" + urllib.parse.urlencode({"kw": keyword})

    # 打开新标签
    try:
        req = urllib.request.Request(f"{base}/json/new?{url}", method="PUT")
        tab = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
    except Exception as e:
        return {"error": f"无法打开标签（Chrome 未启动?）: {e}"}

    time.sleep(wait)
    ws = tab["webSocketDebuggerUrl"]

    async def run(expr):
        async with websockets.connect(ws, max_size=80 * 1024 * 1024) as c:
            await c.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                                     "params": {"expression": expr, "returnByValue": True}}))
            while True:
                m = json.loads(await c.recv())
                if m.get("id") == 1:
                    return m.get("result", {}).get("result", {}).get("value", "")

    title = asyncio.run(run("document.title"))
    if "验证" in title or "安全" in title:
        return {"error": "百度安全验证", "hint": "需先在 CDP Chrome 里登录百度（passport.baidu.com），贴吧自动带过",
                "title": title}

    body = asyncio.run(run("document.body?document.body.innerText.slice(0,4000):''"))
    return {"platform": "tieba", "keyword": keyword, "title": title,
            "text": body[:4000]}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    mode, q = sys.argv[1], sys.argv[2]
    if mode == "baidu":
        r = search_baidu(q)
    elif mode == "baidu_doc":
        r = search_baidu_doc(q)
    elif mode == "sogou":
        r = search_sogou(q)
    elif mode == "tieba":
        r = tieba_via_cdp(q)
    else:
        r = {"error": f"unknown mode {mode}"}
    print(json.dumps(r, ensure_ascii=False, indent=1))

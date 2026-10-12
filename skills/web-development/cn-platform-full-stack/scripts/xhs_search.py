#!/usr/bin/env python3
"""
小红书搜索（CDP 直连方案）—— 绕过 cn-scraper-mcp 的 XHS_EMPTY 缺陷。

背景 / 根因：
  cn-scraper-mcp v0.5.0 的 xiaohongshu_search 用 document.body.innerText 提文字，
  但小红书搜索结果卡片的文字在一个 innerText 抓不到的容器里（页面加载正常、
  有 40+ 卡片，innerText 却只有侧边栏+页脚）→ 引擎误报 XHS_EMPTY。
  本脚本改用 DOM 选择器直接读卡片，实测可拿 27+ 条完整笔记。

前置条件：
  1. Chrome 带 CDP 跑在 9251，且已登录小红书（住宅 IP）
     google-chrome --remote-debugging-port=9251 \
       --user-data-dir=~/.chrome-scrape --no-first-run --no-default-browser-check \
       --disable-dev-shm-usage &
  2. 该 Chrome 窗口已扫码登录 xiaohongshu

用法:
    python3 xhs_search.py "五年级 数学"
    python3 xhs_search.py "上海 小学 五年级" --wait 8
"""
import sys, json, time, urllib.request, urllib.parse, asyncio, argparse

PORT = 9251
BASE = f"http://127.0.0.1:{PORT}"

EXTRACT = r"""
(function(){
  var out=[];
  var cards = document.querySelectorAll('section.note-item, div.note-item');
  cards.forEach(function(c){
    var a = c.querySelector('a[href*="/search_result/"], a[href*="/explore/"]');
    var titleEl = c.querySelector('.title, span.title, [class*="title"]');
    var authorEl = c.querySelector('.author, .name, [class*="author"]');
    var likeEl = c.querySelector('.like-wrapper .count, .count, [class*="like"]');
    var href = a ? a.getAttribute('href') : '';
    var m = href && href.match(/\/(?:search_result|explore)\/([0-9a-f]{16,})/);
    var img = c.querySelector('img');
    out.push({
      noteId: m ? m[1] : '',
      href: href ? (href.indexOf('http')===0?href:'https://www.xiaohongshu.com'+href) : '',
      title: titleEl ? (titleEl.innerText||'').trim() : '',
      author: authorEl ? (authorEl.innerText||'').trim().split('\n')[0] : '',
      likes: likeEl ? (likeEl.innerText||'').trim() : '',
      cover: img ? img.src : ''
    });
  });
  var seen={}, uniq=[];
  out.forEach(function(o){ if(o.noteId && !seen[o.noteId]){seen[o.noteId]=1; uniq.push(o);} });
  return JSON.stringify({
    url: location.href,
    title: document.title,
    logged_in: !!(document.body && document.body.innerText.indexOf('我')>-1),
    cards: out.length, unique: uniq.length, items: uniq
  });
})()
"""


def _tabs():
    return json.loads(urllib.request.urlopen(f"{BASE}/json/list", timeout=8).read().decode())


async def _eval(ws, expr):
    import websockets
    async with websockets.connect(ws, max_size=80 * 1024 * 1024) as c:
        await c.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                                 "params": {"expression": expr, "returnByValue": True}}))
        while True:
            m = json.loads(await c.recv())
            if m.get("id") == 1:
                return m.get("result", {}).get("result", {}).get("value", "")


async def _nav(ws, url):
    import websockets
    async with websockets.connect(ws, max_size=80 * 1024 * 1024) as c:
        await c.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": url}}))
        while True:
            m = json.loads(await c.recv())
            if m.get("id") == 1:
                return


def search(keyword, wait=8, limit=20, port=PORT):
    base = f"http://127.0.0.1:{port}"
    # reuse an existing page tab, else create one
    pages = [t for t in _tabs() if t.get("type") == "page"]
    if not pages:
        try:
            req = urllib.request.Request(f"{base}/json/new?about:blank", method="PUT")
            tab = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
        except Exception as e:
            return {"error": f"Chrome 未启动或 CDP 不可用: {e}",
                    "hint": f"先跑: google-chrome --remote-debugging-port={port} --user-data-dir=~/.chrome-scrape &"}
    else:
        tab = pages[0]

    ws = tab["webSocketDebuggerUrl"]
    url = ("https://www.xiaohongshu.com/search_result?keyword="
           + urllib.parse.quote(keyword) + "&source=web_explore_feed&type=51")
    asyncio.run(_nav(ws, url))
    time.sleep(wait)  # XHS 走签名 XHR，5s 不够，8s 稳
    raw = asyncio.run(_eval(ws, EXTRACT))
    try:
        d = json.loads(raw)
    except Exception:
        return {"error": "解析失败", "raw": str(raw)[:300]}

    if d.get("unique", 0) == 0:
        return {"keyword": keyword, "status": "empty", "note":
                "0 卡片。检查：(1)Chrome 是否已登录小红书 (2)是否数据中心 IP（需住宅 IP）",
                "page_title": d.get("title")}
    d["items"] = d["items"][:limit]
    d["keyword"] = keyword
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keyword")
    ap.add_argument("--wait", type=int, default=8)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--port", type=int, default=PORT)
    a = ap.parse_args()
    r = search(a.keyword, a.wait, a.limit, a.port)
    if r.get("items"):
        print(f"关键词: {r['keyword']} | 卡片 {r['cards']} | 去重 {r['unique']}")
        for i, it in enumerate(r["items"], 1):
            print(f"{i:>2}. {it['title'][:62] or '(无标题)'}")
            print(f"    作者:{it['author'][:22]} 赞:{it['likes']} id:{it['noteId'][:16]}")
            print(f"    {it['href']}")
    else:
        print(json.dumps(r, ensure_ascii=False, indent=1))

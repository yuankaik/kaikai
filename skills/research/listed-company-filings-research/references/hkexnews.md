# 港交所披露易 HKEXnews — 港股披露文件

港股版 EDGAR。覆盖招股书、公告、年报/中报、通函、权益披露。
**注意：港股/A股公司在 SEC EDGAR 查不到，必须走这里。**

- UI: https://www1.hkexnews.hk/search/titlesearch.xhtml
- 后端 API: `titleSearchServlet.do`（UI 实际调的就是它），返回 JSON
- 免登录、免 key

## 最新公告流（最简）

```
https://www1.hkexnews.hk/ncms/json/eds/lc_sehk_e.json
```

## 标题检索 API（主力）

```
https://www1.hkexnews.hk/search/titleSearchServlet.do?<query>
```

| 参数 | 值 |
|------|-----|
| `sortDir` | `0` |
| `sortByOptions` | `DateTime` |
| `category` | `0` |
| `market` | `SEHK`（主板）或 `GEM` |
| `stockId` | `-1` 全部，或数字 stockId |
| `documentType` | `-1` 全部 |
| `fromDate` / `toDate` | `YYYYMMDD` |
| `title` | 关键词，如 `Prospectus` / `SHEIN` / `希音` |
| `searchType` | `1`（标题检索） |
| `t1code` / `t2Gcode` / `t2code` | `-1` 全部 |
| `rowRange` | `100` |
| `lang` | `EN` 或 `C` |

**响应结构：**
```json
{"result":"<JSON字符串或null>","hasNextRow":false,
 "sortList":"[[0,0]]","rowRange":100,"lang":"C",
 "loadedRecord":0,"recordCnt":0}
```

⚠️ `result` 是**被 JSON 编码过的字符串**，要 `json.loads()` 两次。
`recordCnt == 0` 时 `result` 是字符串 `"null"` —— 这是**正常的空结果**，不是解析错误。

每条 item 字段：`DATE_TIME`、`TITLE`、`FILE_LINK`（需前缀 `https://www1.hkexnews.hk`）、`STOCK_CODE`、`STOCK_NAME`。

## 可复用 stdlib 代码

```python
import json, urllib.parse, urllib.request

def hkex_search(title, frm="20260101", to="20261231", market="SEHK", lang="EN"):
    base = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
    q = urllib.parse.urlencode({
        "sortDir": "0", "sortByOptions": "DateTime", "category": "0",
        "market": market, "stockId": "-1", "documentType": "-1",
        "fromDate": frm, "toDate": to, "title": title, "searchType": "1",
        "t1code": "-1", "t2Gcode": "-1", "t2code": "-1",
        "rowRange": "100", "lang": lang,
    })
    req = urllib.request.Request(
        f"{base}?{q}",
        headers={"User-Agent": "Mozilla/5.0",
                 "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml"})
    raw = json.load(urllib.request.urlopen(req, timeout=30))
    if raw.get("recordCnt", 0) == 0:
        return []
    items = json.loads(raw["result"])            # 第二次解码
    for it in items:
        it["url"] = "https://www1.hkexnews.hk" + it.get("FILE_LINK", "")
    return items
```

## ⚠️ 最重要陷阱：`stockId` 检索会静默返回 0（2026-09 实测）

**`search/prefix.do` 返回的 `stockId` 不等于 `titleSearchServlet.do` 认的 `stockId`。**
用它做 `stockId=<id>` 检索，接口会返回**合法 JSON 但 `recordCnt:0`** ——
看起来像"该公司没有公告"，实际是 ID 对不上。这是最危险的失败模式，
会让你误判"招股书查不到"。

```bash
# prefix.do 拿到的是"搜索索引 ID"，不是公告库 ID
curl -s 'https://www1.hkexnews.hk/search/prefix.do?callback=cb&lang=EN&type=A&name=SHEIN&market=SEHK'
# => {"stockId":1000313714,"code":"00625","name":"SHEIN-W"}   ← 这个 id 用不了
```

实测：`stockId=1000313714` + 各种 `category`/`documentType`/日期组合
（0/-1、-1/-1、0/0、扩大日期区间）**全部返回 0 条**。

**判断规则：只要 `recordCnt==0` 但你确信该公司有公告，就是 ID 问题，不是不存在。**
别在 `stockId` 上继续试参数（本次浪费 8+ 次调用）——
直接转下面的可用回退栈。

## ✅ 可用回退栈（本机实测连通，按顺序用）

披露易正文站（`www1.hkexnews.hk/listedco/...` 目录可达，PDF 域名通），
但**检索/列表接口对脚本化访问屏蔽严重**。需要公司档案/行情/公告时改用：

| 用途 | 端点 | 实测 |
|------|------|------|
| **公司档案**（上市日/注册地/ISIN/董事/审计/员工数/业务） | `emweb.securities.eastmoney.com/PC_HKF10/CompanyProfile/PageAjax?code=<5位代码>` | ✅ 返回 JSON |
| **实时行情**（含发行价、区间、市值） | `qt.gtimg.cn/q=hk<5位代码>` | ✅ GBK 编码，分号分隔 |
| **实时行情/市值** | `push2.eastmoney.com/api/qt/stock/get?secid=116.<代码>&fields=f43,f57,f58,f116,f117,f60` | ✅ |
| **代码/名称模糊搜索** | `searchapi.eastmoney.com/api/suggest/get?input=<关键词>&type=14&token=D43BF722C8E33BDC906FB84D85E326E8&count=10` | ✅ |
| **精确代码解析** | `search-codetable.eastmoney.com/codetable/search/web?client=web&keyword=<代码>&pageIndex=1&pageSize=10` | ✅ 返回 market/innerCode |
| **港交所代码索引** | `www1.hkexnews.hk/search/prefix.do?callback=cb&lang=EN&type=A&name=<英文名>&market=SEHK` | ✅ 拿 code + 名称 |
| **多年财报**（营收/净利，多期对比） | `stock.finance.sina.com.cn/hkstock/finance/<5位代码>.html` | ✅ **gb2312 编码**，需解码 |

行情字段速记（腾讯 `qt.gtimg.cn`，`~` 分隔；**2026-09 对 00625/09660 实测**）：
`[1]`=名称、`[3]`=现价、`[4]`=前收、`[5]`=开盘、`[31]`=涨跌额、`[32]`=涨跌幅%、
`[33]`=日内最高、`[34]`=日内最低、`[37]`=成交额、
**`[47]`=52周高、`[48]`=52周低**（对判断"从高点回撤多少"极关键）、
`[59]/[60]` 附近含发行价/上市区间位。
⚠️ 市值位实测有位移：SHEIN(00625) 数据落在 `[43]/[44]`，地平线(09660) 落在
`[44]/[45]`。**不要硬编码市值字段索引** —— 用东财 `push2` 的 `f116`/`f117`
（语义明确）拿市值，腾讯只用来取 52 周高低这类东财不给的字段。

东财 `push2`：`secid=116.<5位代码>`（116=港股），
`f43`=现价、`f57`=代码、`f58`=名称、`f60`=前收、`f116`=总市值、`f117`=流通市值。
⚠️ `f43`/`f60` 有**小数位缩放**，把原始值除以 100 才是港元价（如 37840 → 378.40？
  实测 00625 现价应为 37.84，需除以 1000 —— **务必与腾讯 `[3]` 交叉核对比值再采信**）。

**多年财报解析（新浪港股）**：
```python
# gb2312 页面；先 latin1 再 gb2312 双向解码可避开 mojibake
txt = out.encode('latin1','ignore').decode('gb2312','ignore')
# 去标签后是空格分隔的数字串，按报告期顺序解读（营收、净利等）
```
⚠️ 数字串**无表头**，需按位置对齐报告期；对地平线 09660 实测：
`2026-06-30 / 2025-12-31 / 2025-06-30 / 2024-12-31 …`，营收 301.72 / 534.7 / …（百万人民币）。
**要把"账面盈利 vs 经营亏损"拆开看**——2026H1 的 +243.87 是公允价值浮盈，非经营。

⚠️ 东财 `PC_HKF10/<Page>/PageAjax` 只有部分路径存在：
`CompanyProfile/PageAjax` ✅；`CoreConception`/`HolderStructure`/`Announcement`
→ **404**（别浪费时间试）。公告库 `np-anotice-stock.eastmoney.com`
对**港股新股**常返回空列表。

## 搜索源可达性（2026-09 本机）

| 源 | 状态 |
|----|------|
| 知乎 API（cn-scraper MCP `zhihu_search`/`zhihu_answer`） | ✅ 主力，条款细节靠它 |
| B站 API（`bilibili_search`） | ✅ 快讯/股价动态 |
| 微博热搜（免登录） | ✅ 舆情 |
| DuckDuckGo / ddgs / Startpage | ❌ 连接超时（境外） |
| Yahoo Finance | ❌ 区域屏蔽（sad panda 页） |
| 百度/必应（脚本化） | ❌ 验证码/被拦 |

**结论：境外搜索基本不可用，中文一手/二手源才是本机主路径。**

## 实测陷阱（2026-09 本机）

- **接口慢且会间歇性超时。** 命中多的关键词要 20-30 秒。**必须带 30s 超时 + 重试**；单次超时不等于接口不可用。
- **必须带 `Referer`**，否则部分边缘节点拒绝。
- `lang=C` 用**繁体**关键词；简体关键词可能 0 命中。简体搜不到时改用 `lang=EN` + 拉丁名（如 `SHEIN`）。
- 别用 curl 抓 `zhuanlan.zhihu.com` 文章页（返回 650 字节反爬页），同理一手源打不开时直接转中文源交叉验证。

## 招股书里查什么
见 SKILL.md「招股书里该翻哪几节」——**核心条款（补偿/赎回/反稀释/解禁）都在
"Relationship with Pre-IPO Investors / 与首次公开发售前投资者的关系"** 一节。

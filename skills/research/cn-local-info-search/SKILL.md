---
name: cn-local-info-search
description: 中文本地信息搜索——地址/房产/拆迁/征收/政务等中文长尾词的搜索引擎选择、抓取代码模板和权威查询渠道。当用户要查中文地址、上海房产动迁、拆迁征收、本地政务信息时使用。
category: research
---

# 中文本地信息搜索（地址/房产/拆迁/政务）

## 触发条件
- 查中文地址、小区、弄堂、地块的拆迁/征收/旧改消息
- 查本地政务信息（房屋征收决定、规划公示）
- 其他中文长尾词/本地信息搜索

## 核心技巧：搜索引擎选择（最关键！）
按可用性排序，中文地址/本地信息搜索用下面顺序，前面的先试：

1. **搜狗 sogou.com** + **360 so.com** —— 对中文地址最有效，requests + 浏览器 UA 可直接抓取，无需登录、不触发验证码
2. **必应 cn.bing.com** —— ⚠️ 对中文地址分词失败（"四川北路1515弄"被拆成"四川"，返回"四川省"结果），加引号也救不回，勿依赖
3. **百度** —— 无头/curl 会触发验证码（wappass.baidu.com captcha）
4. **DuckDuckGo** —— 国内连接被重置（ERR_CONNECTION_RESET）
5. **政府官网站内搜索** —— 多为 mayabot 等第三方后端，难逆向，不如直接翻栏目

## 抓取代码模板（requests）
```python
import requests, re, html
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept-Language': 'zh-CN,zh;q=0.9'}
def clean(s): return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
# 搜狗
r = requests.get('https://www.sogou.com/web', params={'query': '关键词'}, headers=headers, timeout=20)
for u, t in re.findall(r'<h3[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r.text, re.S):
    print(clean(t), u)
# 360
r = requests.get('https://www.so.com/s', params={'q': '关键词'}, headers=headers, timeout=20)
for u, t in re.findall(r'<h3[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r.text, re.S):
    print(clean(t), u)
```
⚠️ 搜狗/360 的跳转链接（`/link?url=...`）带反爬：搜狗跳转可解（页面内 `location.replace("真实URL")` 提取），360 跳转常返回 400/首页。解不开就换搜狗，或直接搜文章标题拿直接 URL。

## 拆迁/征收信息权威查询渠道（上海为例）
1. **12345 市民热线**（最快，报地址直接问是否列入征收计划、属于哪个街坊/地块）
2. **区政府官网** → 政府信息公开 → 房屋征收栏目（征收决定/范围/补偿方案，格式"X府房征〔20XX〕X号"）
3. **属地街道办**（一线执行单位，居民第一手消息源）
4. **"上海征收"公众号 / 上观新闻 / 澎湃**（动态跟踪）

## 关键判断规则
- 上海旧改按"街坊"地块编号推进（虹口用 hkXXX + HK-XXX 风貌街坊编号，徐汇用"更新单元"），具体弄堂号/小区名往往搜不到官方公告，需先定位所属街坊再查
- 没搜到区政府官网的"征收决定" = 大概率还没列入正式征收（居民问答"会不会动迁"≠ 官方动迁）
- 历史风貌建筑（百年里弄）走"留改拆/保护修缮"而非大拆，与普通旧改不同
- 抖音/头条个人号的门牌号列举不可当依据，只认政府官网或权威媒体（新华社/上观/澎湃）

## 陷阱
- 搜狗跳转解不开时，直接搜文章标题（用搜狗）拿直接 URL 再抓正文
- 头条/抖音正文有反爬，抓不到就诚实告知"未确认"，不要编造结果
- 连续多引擎搜索仍无官方结果时，直接给结论 + 权威查询渠道，别无限空转（用户工具使用铁律：连败3次立刻换思路）

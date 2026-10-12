---
name: soust-book-download
description: Search and download ebooks from sou.st (搜书网). Use when the user wants to find and download books, especially Chinese ebooks, children's literature, sci-fi, or educational materials.
category: web-development
---

# 搜书网 (sou.st) 电子书搜索下载

## 登录信息
- URL: https://sou.st
- 邮箱: kaikai2026@mailnesia.com
- 密码: hermes2026!!
- 显示名: kaikaiebooks
- ⚠️ 登录用邮箱，不是用户名
- 1积分/文件下载，每日签到+10积分

## ⚠️ 不覆盖内容（搜了也白搜）

搜书网是中文电子书平台，以下类别**完全不覆盖**，不要浪费时间搜索：

| 类别 | 示例 | 验证日期 |
|------|------|----------|
| 英文分级读物 | Oxford Reading Tree, Biff Chip Kipper | 2026-07-03 |
| 英文桥梁书/章节书 | Fly Guy, Magic Tree House | 2026-07-03 |
| 英文儿童绘本 | Dr. Seuss, Eric Carle | — |
| 英文原版教材 | Cambridge, Pearson | — |
| 小众英文原版 | 物理世界奇遇记英文版 | — |

这些书的读者群不在中文电子书站的覆盖范围内。需要换渠道：Z-Library / Anna's Archive / 淘宝闲鱼PDF合集。

## 搜索策略

### 浏览器搜索（推荐）
搜书网的URL编码搜索不稳定，优先使用浏览器表单搜索：
1. browser_navigate → https://sou.st
2. 如果未登录，browser_click Login → browser_type email/password → browser_click Login
3. browser_type 搜索框(ref=e3) → browser_click Search(ref=e4)
4. browser_snapshot 看结果
5. browser_console 提取IDs: `JSON.stringify(Array.from(document.querySelectorAll('a[href*="/file/"]')).filter(a => a.closest('h3')).map(a => ({id: a.href.match(/\/file\/(\d+)/)?.[1], text: a.textContent.trim()})).slice(0, 15))`

### ⚠️ 下载现状（2026-07-21）

**sou.st 下载端点已损坏** — 所有文件返回 HTTP 500：
`TypeError: App\Http\Controllers\FileController::download(): Argument #2 ($id) must be of type int, string given`

详见 `references/download-endpoint-broken-2026-07-21.md`。

**临时方案**：浏览器登录 → 搜书 → 点进文件页 → 点 "Download Now" 按钮，通过浏览器下载。

### Python requests 下载（curl 备选）

curl 的 cookie jar 在 sou.st 上不稳定（session 经常丢失）。Python `requests.Session` 更可靠：

```python
import requests, re, os

session = requests.Session()
desktop = '/mnt/c/Users/admin/Desktop/儿童文学'

# 登录
login_page = session.get('https://sou.st/login')
token = re.search(r'name="_token" value="([^"]+)"', login_page.text).group(1)
session.post('https://sou.st/login', data={
    '_token': token, 'email': 'kaikai2026@mailnesia.com',
    'password': 'hermes2026!!'
})

# 下载（⚠️ 2026-07-21: 端点损坏，返回500）
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
for fid, fname in books:
    url = f'https://sou.st/file/{fid}/download'
    headers['Referer'] = f'https://sou.st/file/{fid}'
    dl = session.get(url, headers=headers, allow_redirects=True, timeout=180)
    if dl.status_code == 200 and len(dl.content) > 50000:
        with open(os.path.join(desktop, fname), 'wb') as f:
            f.write(dl.content)
```

### ⚠️ URL 格式陷阱

文件页 URL 格式：`/file/{ID}-epub` （带后缀）
下载 URL 格式：`/file/{ID}/download` （仅数字 ID）

**不要**用 `/file/{ID}-epub/download` — 会把 "186720-epub" 当字符串传给 download()。

### curl 批量下载（旧方案，可能已失效）

⚠️ **不要用 curl 搜索中文关键词** — sou.st 的 URL 编码不兼容，返回 0 结果。搜索必须走浏览器表单。

```python
from hermes_tools import terminal; import re, os, time

jar = '/tmp/sou_jar.txt'
desktop = '/mnt/c/Users/admin/Desktop/儿童文学'
os.makedirs(desktop, exist_ok=True)

# 1. 登录
r1 = terminal(command=f'curl -s -c {jar} "https://sou.st/login" 2>&1', timeout=10)
csrf = re.search(r'name="_token" value="([^"]+)"', r1['output'])
token = csrf.group(1)
terminal(command=f'curl -s -c {jar} -b {jar} '
    '-H "Content-Type: application/x-www-form-urlencoded" '
    f'--data-urlencode "_token={token}" '
    '--data-urlencode "email=kaikai2026@mailnesia.com" '
    '--data-urlencode "password=hermes2026!!" '
    '-o /dev/null "https://sou.st/login" 2>&1', timeout=10)

# 2. 下载 (ID 从浏览器 console 提取)
books = [("文件ID", "文件名.epub"), ...]
for fid, fname in books:
    path = os.path.join(desktop, fname)
    r = terminal(command=f'curl -s -L -b {jar} -o "{path}" '
        '-H "User-Agent: Mozilla/5.0" '
        f'-H "Referer: https://sou.st/file/{fid}" '
        '-w "%{{http_code}} %{{size_download}}" '
        f'"https://sou.st/file/{fid}/download" 2>&1', timeout=120)
    if '200' in r['output']: print(f"✅ {fname}")
    time.sleep(2)  # 避免限频
```

### 浏览器提取文件 ID（唯一步骤）
搜索后执行：
```
browser_console: JSON.stringify(Array.from(document.querySelectorAll('a[href*="/file/"]'))
  .filter(a => a.closest('h3'))
  .map(a => ({id: a.href.match(/\/file\/(\d+)/)?.[1], text: a.textContent.trim()}))
  .slice(0, 20))
```

## 儿童书籍分类搜索关键词

### 童话/儿童文学
- 童话 → 147结果：格林童话、安徒生、意大利童话、小巴掌童话、日本童话、365夜童话、彩色童话系列(红/橙/绿/黄/蓝)
- 儿童文学 → 32结果：冰心全集、中国儿童文学60周年典藏、任溶溶系列、日本儿童文学大师系列

### 探案/推理（2026-07-02 新发现）
- 金田一 → 6结果：金田一探案大全集(25册)、金田一少年事件簿
- 侦探 → 127结果：名侦探柯南(41MB)、少年侦探团、侦探俱乐部、放学后的侦探队
- 推理 → 193结果：推理笔记系列、日本推理名作选、真相推理师合集、500个侦探推理游戏、柯南侦探推理书(365题)

### 动物小说（2026-07-21 新发现）
- 西顿 动物 → 206结果：西顿动物小说全集(18.56MB)、西顿动物记(3.84MB)、西顿野生动物故事集(5.92MB)、狼王洛波、红脖子松鸡、小战马、巷子里的野猫
- 猫武士 → 291结果：猫武士首部曲(16.8MB)、猫武士首部曲套装6册(19MB AZW3)、二部曲新预言各季
- ⚠️ 椋鸠十 → 1061结果但无实际动物小说（"十"字广泛匹配）

### 中国儿童冒险（2026-07-21 新发现）
- 查理九世 → 53结果：查理九世(8.43MB)、查理日记系列

### 冒险/历险
- 冒险 儿童 → 345结果（需筛选）：波特莱尔大冒险、梅格时空大冒险、男孩的冒险书、寻宝大冒险

### 少儿百科
- 少儿 → 19结果：少儿百科全书、长江少儿科普馆、福尔摩斯探案全集少儿版

### 科幻
- 凡尔纳 → 海底两万里、神秘岛、地心游记、八十天环游地球
- 阿西莫夫、克拉克、海因莱因 → 硬科幻经典
- 安德的游戏 → 奥森·斯科特·卡德
- 刘慈欣 → 流浪地球、带上她的眼睛、乡村教师
- 张之路 → 霹雳贝贝、非法智慧（中国儿童科幻）

### 科普
- 伽莫夫 → 物理世界奇遇记、从一到无穷大
- 时间简史、上帝掷骰子吗

## 适合佳乐（五年级，10岁）的选书原则
- 凡尔纳科幻冒险 → 最合适，教育部推荐
- 安德的游戏 → 主角是小孩，零重力战斗
- 刘慈欣短篇 → 带上她的眼睛、乡村教师（科学+人文）
- 避免：三体（太难）、克拉克（太抽象）、阿西莫夫长篇

## 下载目录
- 默认存放: /mnt/c/Users/admin/Desktop/儿童文学/

## 每日签到

### 开机自动签到（2026-08-13 起，替代旧 cron）
用户电脑不常开，20:00 的 Hermes cron 经常错过 → 改为 Windows 登录任务，不依赖 Hermes/WSL。

- 脚本: `C:\Users\admin\sou-signin\signin.ps1`（幂等：当天已签则跳过，不会重复加分）
- 启动项: `C:\Users\admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\sou-signin.vbs`
  （登录时静默运行 powershell 跑 signin.ps1，无窗口）
- 日志: `C:\Users\admin\sou-signin\signin.log`
- 签到端点: `POST https://sou.st/user/sign-in`（body 仅 `_token`，token 从 dashboard 表单提取）

### 手动签到（requests，已验证可用）
```python
# 登录后：
d = s.get('https://sou.st/user/dashboard')
tok = re.search(r'action="https://sou\.st/user/sign-in" method="POST">\s*<input type="hidden" name="_token" value="([^"]+)"', d.text, re.S).group(1)
r = s.post('https://sou.st/user/sign-in', data={'_token': tok})  # 成功则积分记录 +10 "Check-in Success"
```

### ⚠️ 陷阱（本次踩过）
- `.ps1` 必须存成 **UTF-8 with BOM**，否则 Windows PowerShell 5.1 按 GBK 读中文全乱码、报解析错误。脚本内日志用英文最保险。
- WSL 里 `powershell.exe`（PATH）可能被污染报 `Invalid argument`，用完整路径 `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe` 才正常。
- 注册「任务计划程序」(schtasks / Register-ScheduledTask) 需要管理员权限（0x80070005），会弹 UAC。免提权方案 = 启动文件夹放 .vbs。

## ⚠️ 已知不覆盖：英文分级读物

搜书网不覆盖英文儿童分级读物——12种搜索方式已确认（2026-07-03）。包括：Oxford Reading Tree / 牛津阅读树 / Fly Guy / RAZ-Kids / Biff Chip Kipper 等均无结果。详见 `references/english-graded-readers-not-available.md`。遇到此类需求直接告知用户，不要反复搜索浪费时间。替代方案：使用 `children-novel-embedded-learning` 技能的 `references/english-graded-reader-production.md` 参考文件，基于佳乐的沪教版词汇表自建定制分级读物。

## EPUB → MOBI 转换
下载后如需 MOBI 格式，参见 `references/ebook-conversion.md`。使用 Calibre 的 `ebook-convert` 批量转换。

## 儿童科幻选书参考
对佳乐（五年级）的硬核科幻推荐，按物理/化学/生物分类，标注可读性。参见 `references/children-sci-fi-guide.md`。

## 已有书目（避免重复下载）
童话9本: 格林童话210篇、安徒生童话×3、意大利童话×2、小巴掌童话×2、日本的童话
科幻8本: 凡尔纳×3(海洋三部曲/经典科幻故事套装/读客经典文库)、安德的游戏三部曲+天贼+沃辛传奇+背叛之星、永恒的科幻经典、中国科幻丛书、带上她的眼睛
探案类: 暂无下载

## 探案推理类精选（适合佳乐，2026-07-02 搜索）
| 书名 | 大小 | 说明 |
|------|------|------|
| 金田一探案大全集(25册) | 8MB | 横沟正史全集，1分=25本 |
| 金田一少年事件簿 | 1MB | 少年版 |
| 名侦探柯南 | 41MB | 日式推理经典 |
| 福尔摩斯探案全集少儿版 | 8MB | 已适配少儿 |
| 少年侦探团 | 511KB | 江户川乱步 |
| 放学后的侦探队 | 2.3MB | 校园推理 |
| 500个侦探推理游戏 | 23MB | 互动式推理题 |
| 柯南侦探推理书(365题) | 882KB | 每日一题 |

## 参考文件
- `references/curl-download-pattern.md` — curl 批量下载脚本模板（登录→搜索→下载）
- `references/children-lit-search-2026-07-02.md` — 2026-07-02 儿童文学搜索结果汇总（童话/儿童文学/冒险/百科）
- `references/download-endpoint-broken-2026-07-21.md` — 2026-07-21 下载端点损坏详情及错误日志

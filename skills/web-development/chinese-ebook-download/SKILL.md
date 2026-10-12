---
name: chinese-ebook-download
description: 免费中文电子书下载——从读书派(dushupai.com)、苦瓜书盘(kgbook.com)、搜书网(sou.st)等站点搜索、发现、批量下载。当用户需要下载中文电子书（儿童文学、小说、社科等任何品类）时使用。
category: web-development
tags: [chinese, ebook, download, kgbook, dushupai, soust, ctfile, free, children-literature, pdf2epub]
---

# 中文电子书免费下载

## 触发条件
用户需要：
- 下载中文电子书（儿童文学、小说、社科、教科书等任意品类）
- 寻找免费的 epub/mobi/pdf 中文书资源
- 给佳乐找阅读材料

## 核心源 1：苦瓜书盘 (kgbook.com)

公版经典覆盖好，27 个分类，约 2000+ 本书。适合找经典公版书。

### 站点结构
- 27 个分类目录，每个有独立页面
- 关键分类：`ertongwenxue`(儿童文学), `waiguowenxue`(外国文学), `kehuanxuanhuan`(科幻玄幻), `xiandaiwenxue`(现代文学), `gudianwenxue`(古典文学)
- 每页约 20 本书，有分页（index_2.html, index_3.html...）

### 下载链接模式
详情页上的下载链接格式：
```
https://kgbook.com/e/DownSys/GetDown?classid={CLASSID}&id={BOOK_ID}&pathid={PATHID}
```

**关键：classid 必须从详情页 HTML 中提取**，不能猜测！不同书的 classid 不同，即使同一分类也不一致。从详情页 grep：
```bash
curl -sL "https://kgbook.com/{CATEGORY}/{ID}.html" | grep -oP 'GetDown\?classid=\d+&id=\d+&pathid=\d+'
```

### 批量下载工作流

1. **浏览分类页面**获取所有 book ID：
```bash
curl -sL "https://kgbook.com/ertongwenxue/" | grep 'list-title' 
# 提取所有 href=".../ertongwenxue/数字.html" 
```

2. **逐个访问详情页**提取正确的 classid + pathid：
```bash
curl -sL "https://kgbook.com/ertongwenxue/819.html" | grep -oP 'GetDown\?classid=\d+&id=\d+&pathid=\d+'
```

3. **下载**（注意格式可能是 pdf/mobi/epub/azw3）：
```bash
curl -sL -o "书名.pdf" "https://kgbook.com/e/DownSys/GetDown?classid=13&id=819&pathid=0"
```

4. **验证文件**：确认不是 HTML 错误页（file 命令检查）：
```bash
file "下载的文件.pdf"
# 应该显示 "PDF document" 而非 "HTML document"
```

### 分类目录 classid 参考（不完全可靠，务必从详情页提取！）
已知可用的映射（仅供参考）：
- 儿童文学 → classid=13（部分书）
- 科幻玄幻 → classid=5,9（不同书不同）
- 外国文学 → classid=7,12（不同书不同）

### 搜索
站内搜索使用 POST 方法，curl GET 不生效。可用浏览器表单提交，但搜索覆盖面有限（很多书搜不到，只能通过分类浏览发现）。

## 辅助源

### 古腾堡计划 (gutenberg.org)
- 中文书极少，且浏览/搜索中文不友好
- 可通过 `https://www.gutenberg.org/ebooks/search/?query=languages.zh` 尝试
- 大多数经典儿童文学只有英文原版，无中文

### 安娜档案 / Z-Library / Library Genesis
- 在中国网络环境下全部不通

## 陷阱

1. **classid 不能猜**：错误 classid 会返回 HTML 重定向页（约 1KB），不是真文件
2. **file 命令验证**：下载后必须用 `file` 检查，确认是 PDF/mobi/epub 而非 HTML
3. **格式多样**：同一本书可能有 pdf/mobi/epub 多种格式（不同 pathid），优先 epub
- 站点老旧：最后更新约 2015 年，没有新书，但公版经典覆盖好
- 不要批量并发：curl 间隔至少 1 秒，否则可能被限

## 核心源 2：读书派 (dushupai.com) — 2026-06 新发现

**藏书量远超 kgbook**（10万+），现代书和公版经典都覆盖，是目前最全的中文电子书免费源。格式：EPUB/AZW3/MOBI。

### 下载机制

读书派本身不托管文件，全部寄存在诚通网盘 (ctfile)：
1. 搜索 → book-content-{ID}.html → 有"下载地址"链接
2. 点击进入 download-book-{ID}.html → 显示 ctfile 链接
3. ctfile 链接格式：`https://url89.ctfile.com/f/{USER_ID}-{FILE_ID}-{hash}?pwd=8866`
4. **统一密码：8866**（所有书都一样）

### 下载方式（重要！）

ctfile 的免费下载**必须用浏览器 JS 交互**，curl/API 无法直接下载：
- 浏览器打开 ctfile 链接 → 如提示密码，输入 8866 → 点"解密文件" → 在"普通下载"区域点"立即下载"
- 不要尝试 curl ctfile API（返回 403 "分享链接打开不完整"）
- 通用密码 8866 嵌入 URL 的 ?pwd= 参数**不一定自动生效**（部分链接仍需手动输入），遇到密码提示直接输 8866 即可

### 浏览器下载工作流（2026-06-29 验证）

步骤：
1. browser_navigate(ctfile_url)  → 如要求密码，type "8866" + click 解密
2. browser_click("普通下载"区域的"立即下载"按钮)
3. 文件落入 ~/Downloads/（Browserbase 浏览器默认下载目录）
4. 下载产物为 zip，内通常含 mobi+azw3+epub 多格式，直拷到目标目录

### 搜索限制（2026-06-29 更新）

**搜索URL可用但中文精确匹配完全失效！**

搜索实际端点：`/search.html?k=KEYWORD`

但搜索引擎对中文做**单字级别模糊匹配**——搜"时代广场的蟋蟀"会匹配所有含"时/代/广/场/蟋/蟀"的书，结果噪音极大（声称10000结果但无一相关）。加引号、加作者名、加分类词均无效。

**有效策略：**
- 只在已知 book-content ID 或 ctfile 链接的情况下通过 curl 提取下载链接
- 无法通过搜索发现新书
- 走投无路时：浏览器搜索 → 手动翻页找 → 人眼识别

**已知有效的搜索词：** 单字或极短词（如"黑鹤"）可能碰巧返回有用结果，但不保证。

curl 提取下载链接工作流：
```bash
# 1. 从 book-content 页提取 download-book 链接
curl -sL "https://www.dushupai.com/book-content-{ID}.html" | grep -oP '/download-book-\d+\.html'

# 2. 从 download-book 页提取 ctfile URL
curl -sL "https://www.dushupai.com/download-book-{ID}.html" | grep -oP 'https?://url\d*\.ctfile\.com/[^\s"\'<>&]+'
```

### 已验证有货的经典童书

| 书名 | ctfile URL（密码 8866） |
|------|------------------------|
| 尼尔斯骑鹅旅行记 | url89.ctfile.com/f/31084289-1357768961-eae4e4?pwd=8866 |
| 柳林风声（3版本） | url89.ctfile.com/f/31084289-1374966772-ca2394?pwd=8866 |
| 绿野仙踪（含全集14册） | url89.ctfile.com/f/31084289-1357031788-1a3b36?pwd=8866 |
| 爱丽丝梦游仙境（6版本） | url89.ctfile.com/f/31084289-1358053850-17f8b3?pwd=8866 |

第一次搜索时优先搜尼尔斯骑鹅、柳林风声——这是佳乐的首选。
其他经典（鲁滨逊、木偶奇遇记、彼得潘、秘密花园等）大概率也有，需浏览器搜索确认。

**中文搜索站全封**：不要浪费时间试百度/搜狗/道客巴巴/原创力/鸠摩搜索

## 佳乐阅读偏好（上下文）

从用户资料：佳乐(10岁/四升五)喜欢动物拟人故事，偏好公版经典（尼尔斯骑鹅旅行记、柳林风声优于沈石溪）。已从 kgbook 下载过 16 本儿童文学（安徒生、格林、王尔德、夏洛的网、动物农场等），下次避免重复下载。

**2026-06-30 补充偏好画像：**
- 爱搞笑主角（白小纯型"怂帅"），讨厌无聊
- 喜欢《会走路的牛奶》→ 想象力丰富+幽默感
- 宝可梦、深海/海洋生物类狂热（已配字海钓徒自定义故事）
- 情节精彩的冒险也可（不限于动物）
- 已有：黑鹤系列3本、字海钓徒、时代广场的蟋蟀

**推荐优先级（搜书先搜这些）：**
1. 海底两万里（凡尔纳）— 深海冒险，精准命中
2. 西顿动物小说全集 — 经典动物故事，真实不幼稚
3. 凡尔纳科幻经典_神秘岛 + 地心游记
4. 国际大奖动物小说经典套装
5. 吉姆·凯尔高动物小说作品集

搜书网 sou.st 有以上全部，1分/本。11分足够全下。

**2026-07-01 更新：已下载书单（共17本，存 C:\\Users\\admin\\Desktop\\儿童文学\\）**

童话/文学类 (9本)：
- 格林童话(210篇全本无删减) 6.8MB
- 安徒生童话 16.6MB / 安徒生童话全集 1.2MB
- 叶君健权威译本_安徒生童话全集 21.7MB（最佳中译本）
- 伊泰洛·卡尔维诺_意大利童话 3.3MB
- 小巴掌童话套装1-6册 1.0MB（张秋生，中国原创）
- 日本的童话 2.3MB
- 意大利童话 3.3MB

科幻/冒险类 (8本)：
- 凡尔纳经典科幻故事套装 3.5MB（青少年精选版）
- 凡尔纳-海洋三部曲 3.1MB（海底两万里+神秘岛+格兰特船长）
- 读客经典文库：凡尔纳科幻经典 16.8MB（完整典藏）
- 永恒的科幻经典 16MB（世界科幻名篇合集）
- 中国科幻丛书 2.4MB（中国少儿科幻）
- 安德的游戏 277KB（奥森·斯科特·卡德，太空军校+零重力物理）
- 卡德科幻经典套装_安德的游戏三部曲 3.9MB
- 带上她的眼睛 129KB（刘慈欣短篇，地核物理）

搜书网**未收录**：物理世界奇遇记（伽莫夫）、从一到无穷大——这些科普经典需从其他渠道获取。

**2026-07-21 更新：侦探/推理类搜书网资源丰富**，见 `references/detective-novels.md`。金田一、福尔摩斯、阿加莎、江户川乱步、东野圭吾、名侦探柯南小说版等均有货（文字版，非漫画）。佳乐对侦探推理感兴趣时可快速检索该参考文件。

## PDF → EPUB 批量转换

kgbook 下载的多为 PDF（6寸PDF，文本型），可以用 PyMuPDF + EbookLib 批量转 EPUB。

### 环境

```bash
# 在已有 venv 中安装（如 ~/ocr_env/）
source ~/ocr_env/bin/activate
pip install pymupdf ebooklib
```

### 转换脚本

脚本位置：`scripts/pdf2epub.py`（本技能附带）

用法：
```bash
source ~/ocr_env/bin/activate
python scripts/pdf2epub.py  # 自动处理桌面所有 PDF
```

脚本特点：
- 自动跳过 TOC 页（含 >3 个章节标记的页面）
- 去除页眉（如 "Edited by Skywalker"）
- 合并断行（中文换行处无标点则拼接）
- 单文件流式输出（不拆分章节，避免误判）

### 章节检测陷阱

kgbook PDF 的章节标记可能有空格：`第1 章` 而非 `第1章`。正则需用 `第\s*[\d一二三四五六七八九十百千]+\s*章`。

目录页（TOC）含密集章节标记，需跳过。判断标准：单页 >3 个章节标记 = TOC 页。

### epub → mobi/azw3（Kindle 格式转换）

用 calibre 的 ebook-convert 批量转换：

```bash
# 安装 calibre
sudo apt-get install -y --no-install-recommends calibre

# EPUB → MOBI（推荐，全系Kindle兼容）
ebook-convert input.epub output.mobi

# EPUB → AZW3（更好排版，但部分旧Kindle不支持）
ebook-convert input.epub output.azw3
```

**批量转换脚本：**
```bash
cd /path/to/epub/dir
mkdir -p Kindle
for f in *.epub; do
  name="${f%.epub}"
  ebook-convert "$f" "Kindle/${name}.mobi" 2>&1 | grep -q "MOBI output written" && echo "✓ $name" || echo "✗ $name"
done
```

**USB侧载到Kindle：** 将 .mobi 文件复制到 Kindle 的 `documents/` 目录即可。

**注意：** EPUB3 文件可能触发 lxml/libxml2 版本冲突（见上方 calibre lxml 章节），EPUB2 不受影响。先检查版本：`python3 -c "import zipfile; import re; z=zipfile.ZipFile('file.epub'); c=z.read('META-INF/container.xml').decode(); opf=re.search(r'full-path=\"([^\"]+)\"',c).group(1); print('EPUB',re.search(r'version=\"([^\"]+)\"',z.read(opf).decode()).group(1))"`

### mobi → epub

kgbook 部分书只有 mobi 格式。用 calibre 的 ebook-convert：

```bash
ebook-convert input.mobi output.epub
```

### calibre lxml/html5-parser libxml2 版本冲突（致命bug）

pip 安装的 lxml 与系统 apt 的 html5-parser 使用不同 libxml2 版本时，calibre 会崩溃：
```
RuntimeError: html5-parser and lxml are using different versions of libxml2.
libxml2 versions: html5-parser: (2, 15, 2) != lxml: (2, 14, 6)
```

**影响范围：** 仅 EPUB3 文件触发（EPUB2 可正常转换）。

**根本原因：** pip-installed lxml 在 `/usr/local/lib/python3.14/dist-packages/` 优先级高于 apt 系统版 `/usr/lib/python3/dist-packages/`，两者链接不同 libxml2。

**永久修复（推荐）：**
```bash
# 删掉 pip 版 lxml，让 Python 用 apt 系统版
sudo rm -rf /usr/local/lib/python3.14/dist-packages/lxml /usr/local/lib/python3.14/dist-packages/lxml-*-info
# 验证版本一致
python3 -c "import lxml.etree; import html5_parser; print(lxml.etree.LIBXML_VERSION, html5_parser.LIBXML_VERSION)"
# 应输出相同的版本号
```

**临时修复（不推荐，治标不治本）：**
`PYTHONPATH=/usr/lib/python3/dist-packages ebook-convert input.epub output.mobi`

注意：Python 版本号可能不同（如 3.12 而非 3.14），路径需对应调整。

### 验证转换结果

```bash
file output.epub  # 应显示 "EPUB document"
ls -lh output.epub  # >2KB 才可能是有效 EPUB
```

## 核心源 3：搜书网 (sou.st) — 2026-06-29 新发现

**可与 dushupai 并行的中文电子书搜索源**，中文搜索精准度远超 dushupai（支持完整词语匹配，非单字模糊），当代中文作品覆盖好（黑鹤、牧铃等中国作家作品均有收录）。格式以 EPUB 为主。

### 注册与积分

下载需要登录 + 消耗积分。

**注册：** 任意邮箱 + 用户名 + 密码即可，无需验证。注册成功直接跳过邮箱验证。

**登录（重要！）：** 登录表单的 email 字段同时有客户端 (`type="email"`) 和**服务端**双重邮箱格式校验。虽然注册时填了用户名，但**登录必须用注册邮箱**，不能用用户名！

- 当前账号：邮箱 `kaikai2026@mailnesia.com`，密码 `hermes2026!!`（显示名 kaikaiebooks）
- 客户端绕过（改 `type="text"`）无效，服务端仍会拒绝非邮箱格式
- 若登录后 session 丢失，重新用邮箱登录即可

**browser_console fetch 登录（绕过表单校验的最快方式）：**
当页面表单被客户端/服务端校验阻挡时，用 browser_console 直接 POST：
```js
(() => {
  const f = document.querySelector('form');
  const token = f.querySelector('[name="_token"]').value;
  const fd = new FormData();
  fd.append('_token', token);
  fd.append('email', 'kaikai2026@mailnesia.com');
  fd.append('password', 'hermes2026!!');
  fd.append('remember', '1');
  return fetch('https://sou.st/login', {method: 'POST', body: fd, credentials: 'include'});
})()
```
返回 `login OK, redirecting...` 后，`browser_navigate('https://sou.st')` 即为已登录状态。比浏览器表单填写+点击快，且绕过所有客户端校验。

**每日签到：** 登录后进入 User Center → 点击 "Daily Check-in" → **+10 积分**。每本书通常只需 1 积分，签到一次可下载 10 本。

**积分记录：** User Center → Points Log 查看明细。

### 搜索

首页搜索框直接搜书名/作者，**支持中文完整词组匹配**（不像 dushupai 单字拆分）：

- 搜"黑焰" → 返回黑鹤动物文学系列（精准匹配，非"焰娘""黑冰"等噪音）
- 搜"黑鹤 动物文学 精品" → 返回黑鹤动物文学精品系列合集（9.58MB）

**⚠️ 搜索参数名陷阱：** 搜索表单使用参数名 `keyword`，不是 `q`！用 Python requests 时 `?q=xxx` 返回 0 结果，必须用 `?keyword=xxx`。浏览器搜索框提交的是 `keyword` 参数。

**⚠️ curl 中文搜索完全失效（2026-07-01 验证）：** 即使用 `urllib.parse.quote` 正确编码中文关键词，curl GET 搜索始终返回 0 结果。浏览器 form POST 搜索正常工作。**必须用浏览器搜索 + console 提取 ID + curl 下载**的三步组合。

**搜索+下载推荐工作流（2026-07-01 更新）：**
1. 浏览器登录 → form 搜索 → `browser_console` 提取 ID：`JSON.stringify(Array.from(document.querySelectorAll('a[href*="/file/"]')).filter(a => a.closest('h3')).map(a => ({id: a.href.match(/\/file\/(\d+)/)?.[1], text: a.textContent.trim()})).slice(0, N))`
2. `execute_code` 用 curl + cookie jar 批量下载（`/file/{ID}/download`）
3. 每文件间隔 2 秒，大文件（>10MB）timeout 设 120s
4. 下载目标：`/mnt/c/Users/admin/Desktop/儿童文学/`

### 下载工作流

**方式一：浏览器交互下载**
1. `browser_navigate("https://sou.st")` → 如已注册则登录
2. 搜索框输入书名 → 点击 Search
3. 点击目标文件链接 → 进入详情页
4. 点击 "Download Now" → 等待 5 秒倒计时 → 页面重定向到 `/file/{ID}/download`
5. 浏览器自动下载文件（Browserbase 可能不保存，需用方式二/三）

**方式二：curl 批量下载（推荐，最快）**
见 `references/soust-curl-workflow.md`。核心流程：
1. curl 登录（CSRF token → POST login → cookie jar）
2. 浏览器 console 提取 file ID（`Array.from(document.querySelectorAll(...))`）
3. `curl -L -b cookie.jar "https://sou.st/file/{ID}/download"` 直接下载
4. 适合批量：循环 file_id 列表，间隔 2 秒

**方式三：Python session 下载**
见 `references/soust-python-workflow.md`。核心流程：
1. `requests.Session()` 登录获取 cookies
2. `GET /search?keyword=书名` 搜索，正则提取 file ID
3. `GET /file/{ID}/download` 流式下载，写入桌面
4. 每文件 1 积分，支持批量

底层机制：下载按钮 `id="downloadBtn"` 的 `data-url` 属性指向 `/file/{ID}/download`。JS 5 秒倒计时后用 `window.location.href` 跳转到该 URL 触发下载。直接访问该 URL 即可下载（需带 session cookie）。

### 陷阱

1. **Session 极易丢失**：browser_navigate 跨页面时 cookie 可能不保留，需在同页面通过 form 搜索或 browser_console 的 `window.location.href` 导航
2. **下载中断**：大文件（>5MB）可能超时失败，表现为 .crdownload 未完成即消失。可通过 browser_console 的 fetch API 重试，或改用手机浏览器下载
3. **重复下载不退款**：已扣分的文件第二次下载仍需积分（系统计为"已下载过"但 session 丢失后无法识别）
4. **无需绑定手机**：注册只需邮箱，比国内多数网盘方便
5. **搜书网/读书派/苦瓜书盘只有文字书 — 无漫画/绘本/画册**：金田一搜得到小说版、探案集，但搜不到漫画版。三大站收录的都是 EPUB/TXT/PDF 文字书，不包含漫画（CBR/CBZ/图片类）。用户要漫画 → 直接告知不可行，避免花时间反复搜。
5. **execute_code Python 下载大文件超时（2026-07-21 发现）**：搜书网到 Agent 服务器的带宽仅 ~10KB/s，40MB 文件需 1h+。execute_code 上限 300s，大文件 (>5MB) 必定超时。→ 解决方案见下方"大文件下载：Python→curl 桥接"

### 大文件下载：Python→curl 桥接（2026-07-21）

**问题：** Python `requests` 下载搜书网文件极慢（~10KB/s），`execute_code` 300s 超时限制让 >3MB 的文件无法完成。

**解决：** Python 登录+搜索（快），提取 file ID 后用 curl 后台下载（不限时）。

```python
import requests, re, http.cookiejar
from pathlib import Path

session = requests.Session()

# 1. Python 登录（快，几秒）
login_page = session.get('https://sou.st/login', timeout=30)
token = re.search(r'name="_token"\s+value="([^"]+)"', login_page.text).group(1)
session.post('https://sou.st/login', data={
    '_token': token,
    'email': 'kaikai2026@mailnesia.com',
    'password': 'hermes2026!!',
    'remember': '1'
}, timeout=30)

# 2. Python 搜索（快）
resp = session.get('https://sou.st/search?keyword=金田一', timeout=30)
matches = re.findall(r'/file/(\d+)[^"]*"[^>]*>([^<]+)</a>', resp.text)
# → 拿到 file ID 列表

# 3. 导出 cookies 为 Netscape 格式供 curl 使用
cj = http.cookiejar.MozillaCookieJar('/tmp/soust_cookies.txt')
for c in session.cookies:
    cj.set_cookie(c)
cj.save()

# 写入 Netscape 格式（curl -b 直接可用）
with open('/tmp/soust_cookies_curl.txt', 'w') as f:
    f.write("# Netscape HTTP Cookie File\n")
    for cookie in session.cookies:
        domain = cookie.domain if cookie.domain.startswith('.') else '.' + cookie.domain
        secure = "TRUE" if cookie.secure else "FALSE"
        expiry = str(int(cookie.expires)) if cookie.expires else "0"
        f.write(f"{domain}\tTRUE\t{cookie.path}\t{secure}\t{expiry}\t{cookie.name}\t{cookie.value}\n")

# 4. 终端后台下载（不限时）
# terminal(f'curl -L -b /tmp/soust_cookies_curl.txt -o "目标路径" "https://sou.st/file/{ID}/download"',
#          background=True, notify_on_complete=True, timeout=600)
```

**关键点：**
- Python search 很快（几秒），curl search 中文词返回空结果
- curl download 可用但需 Netscape cookie；直接用 Python `session.cookies` 不行
- HEAD 请求先验证文件可下载 + 确认大小：`session.head(url)` 返回 200 + Content-Length
- 小文件 (<3MB) 仍可用 Python `session.get(url).content` 一次性下载，快且方便

### 已知有货的当代中文童书

| 书名 | 大小 | 备注 |
|------|------|------|
| 黑鹤动物文学系列：黑焰 | 291KB EPUB | 单本，1分 |
| 黑鹤动物文学精品系列 | 9.58MB EPUB | 合集（可能含黑焰+鬼狗+狼獾河），1分 |
| 黑鹤动物文学系列：狼谷的孩子 | 349KB EPUB | 1分 |
| 黑鹤动物文学系列：黑狗哈拉诺亥 | 426KB EPUB | 1分 |

其他中国作家（牧铃/金曾豪等）：需用作者名逐本搜索，当代作品覆盖率好于 kgbook（kgbook 2015年停更）。

## 备选方案

当 kgbook + dushupai + sou.st 都找不到目标书时：
1. kgbook 的凡尔纳科幻套装（含海底两万里等 11 册）覆盖部分冒险需求
2. 如果用户首选的公版书全网断供，可提议基于公版英文原文 + 公开中译生成简化改写版（参考 children-novel-embedded-learning 技能）
3. **优先搜 sou.st**：中文搜索精准 + 当代作品覆盖好 + 1分/本便宜
4. **其次 dushupai**：藏书量大但搜索不可靠，适合已知链接的直接下载

## 2026-06-29 站点连通性最新测试

**可用（直接下载或用浏览器下载）：**
- **sou.st（搜书网）** — 浏览器注册+登录+搜索+下载，中文精准搜索，当代作品覆盖好。每日签到+10分，1分/书
- kgbook.com — 直接 curl，27 分类
- dushupai.com（读书派）— 搜索需浏览器，下载需浏览器操作 ctfile
- gutenberg.org — 英文为主，中文极少
- standardebooks.org — 英文公版
- **shuge.org** — 古籍

**漫画/Kindle漫画源（特殊用途，非通用电子书）：**
- **kxx.moe / mox.moe (Kmoe)** — Kindle漫画推送站（2026-07-21 测试）。mox.moe 重定向至 kxx.moe。有金田一/柯南等漫画类目（"偵探"分类可见），但注册需**邮箱验证码 + 手机短信验证码**，无法自动化注册。且明确声明"不支持临时邮箱""会不定期清理非正常账号"。总结：漫画资源存在但人工才能用，Agent自动化不可行。
- **vol.moe** — 同类Kindle漫画站，不通（超时）。

**不可达：**
- Z-Library: singlelogin.re, z-lib.io, zlibrary-global.se, z-lib.id, z-lib.gs, z-lib.fm, z-lib.is, z-library.se, zlibrary.to, z-lib.org
- Library Genesis: libgen.is, libgen.rs, libgen.li
- Anna's Archive: annas-archive.org, annas-archive.se
- 台湾站: readmoo.com.tw, books.com.tw, haodoo.net
- 中国站: dushu369.com, kanunu8.com, xiabook.com, cn.epubee.com, sobooks.net(安全验证), shuji.com, ydshu.com, 52shuku.vip, ziliaoshare.com(404)
- Internet Archive: archive.org
- 一单书(yidanshu.com), 书记知识库(shuji.com), oalib.com(学术论文站非电子书)
- 鸠摩搜索(jiumodiary.com)
- **小红书(xiaohongshu.com): Browserbase IP被封（"IP at risk"），curl/手机UA均返回SPA空壳**
- **贴吧/百度: CAPTCHA 安全验证拦截**
- **Bing(国内版): Cn.bing.com 搜索结果不渲染（仅导航栏）**
- **Bing(国际版)/DuckDuckGo/Google: 超时**（中国网络环境，Browserbase 同样超时）
- **SearX 公共实例: 超时**
- **所有中文网盘搜索(yunpan/pansearch): 不可达**

## 当搜索全部堵死时的备选策略

### 下载优先级（2026-06-29）

按成功率排序：
1. **sou.st** → 中文精准搜索，当代作品全，注册即用
2. **dushupai ctfile** → 需已知链接，浏览器下载 zip（内含多格式）
3. **kgbook** → 公版经典，curl 直接下载
4. **用户手机** → 当 Agent 侧全堵时，用户搜链接发过来

### Meta-search: 让用户搜，你来下载

所有搜索站都封的情况下，让用户用**手机或Windows本地浏览器**（不同IP）搜：
1. 用户在小红书/百度/贴吧搜："书名 + mobi + 下载"
2. 用户把找到的 **pan.quark.cn 分享链接**或**网站名**发给你
3. 你来提取文件清单 / 尝试下载

这个分工高效：用户绕过IP封锁，Agent做自动化提取和转换。

### 小红书图片识别 → 发现新站

当用户从小红书截图中拿到免费电子书网站列表时：
1. vision_analyze 逐张识别 → 提取站名和URL
2. 批量 curl 检测连通性（`curl -sL --max-time 5 -o /dev/null -w "%{http_code}"`）
3. 对返回 200/403 的站用 browser 打开验证
4. 重点关注搜书/资源聚合类站点（非古籍/学术/图书馆类）
5. 新发现的可下载站 → 注册 → 搜索目标书 → 下载

2026-06-29 从小红书截图识别 55 个站，最终发现 sou.st 能实际下载中文当代儿童文学。

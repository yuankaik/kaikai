# 搜书网 Python Session 下载工作流

比浏览器自动化更快、更可靠，支持批量下载。

## 完整代码模板

```python
import requests
import re
import urllib.parse
from pathlib import Path

DESKTOP = Path('/mnt/c/Users/admin/Desktop')

session = requests.Session()

# 1. 登录
login_page = session.get('https://sou.st/login')
token = re.search(r'name="_token"\s+value="([^"]+)"', login_page.text).group(1)
session.post('https://sou.st/login', data={
    '_token': token,
    'email': 'kaikai2026@mailnesia.com',  # 必须用邮箱！
    'password': 'hermes2026!!',
    'remember': '1'
})

# 2. 搜索（⚠️ 参数名是 keyword，不是 q！）
query = '西顿动物小说全集'
resp = session.get('https://sou.st/search?keyword=' + urllib.parse.quote(query))

# 3. 提取 file ID
m = re.search(r'href="https?://sou\.st/file/(\d+)(?:-[^"]*)?"[^>]*>([^<]+)</a>', resp.text)
fid = m.group(1)   # e.g. "186720"
title = m.group(2)  # e.g. "西顿动物小说全集.epub"

# 4. 下载
dl_url = f'https://sou.st/file/{fid}/download'
resp = session.get(dl_url, stream=True)
with open(DESKTOP / title.strip(), 'wb') as f:
    for chunk in resp.iter_content(chunk_size=8192):
        f.write(chunk)
```

## 关键发现

### 搜索参数名：keyword vs q
- 浏览器搜索表单：`<input name="keyword">` → URL 参数是 `keyword`
- 用 `?q=` 返回 0 结果（页面渲染正常但无搜索结果）
- 必须用 `?keyword=`

### 下载 URL 模式
- 文件详情页：`https://sou.st/file/{ID}-epub`
- 下载端点：`https://sou.st/file/{ID}/download`
- 下载按钮 JS：`document.getElementById('downloadBtn').dataset.url` → `/file/{ID}/download`
- 5 秒倒计时后 `window.location.href` 跳转到下载 URL
- 直接 GET 下载端点即可（需带 session cookie），不需要经过详情页

### 登录必须用邮箱
- 注册邮箱：`kaikai2026@mailnesia.com`（不是用户名 `kaikaiebooks`）
- 服务端有双重校验：客户端 `type="email"` + 服务端验证邮箱格式

## 已下载记录（2026-06-30）

| File ID | 文件名 | 大小 |
|---------|--------|------|
| 186720 | 西顿动物小说全集.epub | 18.6 MB |
| 158731 | 国际大奖动物小说经典套装.epub | 4.9 MB |
| 144839 | 吉姆·凯尔高动物小说作品集.epub | 1.7 MB |
| 198736 | 凡尔纳科幻经典_地心游记.epub | 6.4 MB |
| 189944 | 灾难求生儿童小说.epub | 19.0 MB |

积分消耗：5 分（1分/本），剩余 6 分。

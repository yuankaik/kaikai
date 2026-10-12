# 搜书网 (sou.st) curl 批量下载工作流

比浏览器交互方式更快、更可靠，适合批量下载（多本书一次搞定）。

## 前置条件

- 已注册账号（邮箱 kaikai2026@mailnesia.com / 密码 hermes2026!!）
- 有足够积分（签到+10分/天，1分/书）
- curl 可用

## 步骤

### 1. 获取 CSRF Token 并登录

```bash
# 1a. 访问登录页获取 CSRF token
curl -s -c /tmp/sou_jar.txt -b /tmp/sou_jar.txt \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://sou.st/login" | grep -oP 'name="_token" value="([^"]+)"' 

# 1b. 用提取的 token 登录
curl -s -c /tmp/sou_jar.txt -b /tmp/sou_jar.txt \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Origin: https://sou.st" \
  -H "Referer: https://sou.st/login" \
  --data-urlencode "_token=TOKEN_FROM_STEP_1A" \
  --data-urlencode "email=kaikai2026@mailnesia.com" \
  --data-urlencode "password=hermes2026!!" \
  "https://sou.st/login"
# 成功返回: Redirecting to https://sou.st/user/dashboard
```

### 2. 搜索并提取 File ID

**方法A（浏览器 console — 最快）：**
```js
// 在浏览器搜索结果页的 console 执行
JSON.stringify(Array.from(document.querySelectorAll('a[href*="/file/"]'))
  .filter(a => a.closest('h3'))
  .map(a => ({
    id: a.href.match(/\/file\/(\d+)/)?.[1], 
    text: a.textContent.trim()
  })))
```

**方法B（curl — 需要 URL 编码中文）：**
```bash
curl -s -b /tmp/sou_jar.txt \
  -H "User-Agent: Mozilla/5.0" \
  "https://sou.st/search?keyword=%E7%AB%A5%E8%AF%9D" \
  | grep -oP '/file/\d+-[^"]+'
```

注意：curl 搜索中文必须 URL 编码。浏览器内搜索更可靠。

### 3. 下载文件

```bash
curl -s -L -b /tmp/sou_jar.txt \
  -o "输出文件名.epub" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Referer: https://sou.st/file/FILE_ID" \
  -w "HTTP:%{http_code} Size:%{size_download}" \
  "https://sou.st/file/FILE_ID/download"
```

- `-L`：跟随重定向（下载会经过一次重定向）
- `-b /tmp/sou_jar.txt`：携带登录 cookie
- 返回 `HTTP:200` 表示成功

### 4. Python 批量下载模板

```python
from hermes_tools import terminal
import os, time

books = [
    ("FILE_ID_1", "书名1.epub"),
    ("FILE_ID_2", "书名2.epub"),
]

for fid, fname in books:
    path = f'/mnt/c/Users/admin/Desktop/儿童文学/{fname}'
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print(f"⏭ {fname} (已存在)")
        continue
    
    r = terminal(
        command=f'curl -s -L -b /tmp/sou_jar.txt -o "{path}" '
        '-H "User-Agent: Mozilla/5.0" '
        f'-H "Referer: https://sou.st/file/{fid}" '
        '-w "%{http_code} %{size_download}" '
        f'"https://sou.st/file/{fid}/download" 2>&1',
        timeout=60
    )
    if '200' in r['output']:
        print(f"✅ {fname}")
    else:
        print(f"❌ {fname}")
    time.sleep(2)  # 限频
```

## 与浏览器方式的对比

| 特性 | curl 方式 | 浏览器方式 |
|------|----------|-----------|
| 速度 | 快（无页面渲染） | 慢（需等待页面加载） |
| 批量下载 | 容易（循环调用） | 繁琐（逐页点击） |
| 大文件 | 稳定 | 可能超时/crdownload |
| Session | cookie jar 持久 | 跨页可能丢失 |
| 搜索 | 需 URL 编码中文 | 直接输入即可 |

**推荐策略**：浏览器搜索 + console 提取 ID → curl 批量下载。

## 积分检查

```bash
curl -s -b /tmp/sou_jar.txt \
  -H "User-Agent: Mozilla/5.0" \
  "https://sou.st/user/dashboard" | grep -oP "Points:\s*\d+"
```

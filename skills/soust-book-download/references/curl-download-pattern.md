# sou.st curl 批量下载脚本模式

## 登录 + 搜索 + 下载 三步走

```python
from hermes_tools import terminal
import re, os, time, urllib.parse

jar = '/tmp/sou_jar.txt'

# Step 1: 登录
r = terminal(command=f'curl -s -c {jar} "https://sou.st/login" 2>&1', timeout=10)
csrf = re.search(r'name="_token" value="([^"]+)"', r['output'])
token = csrf.group(1)

terminal(
    command=f'curl -s -c {jar} -b {jar} '
    '-H "Content-Type: application/x-www-form-urlencoded" '
    f'--data-urlencode "_token={token}" '
    '--data-urlencode "email=kaikai2026@mailnesia.com" '
    '--data-urlencode "password=hermes2026!!" '
    '-o /dev/null "https://sou.st/login" 2>&1',
    timeout=15
)

# Step 2: 搜索（URL编码中文）
encoded = urllib.parse.quote('凡尔纳')
r = terminal(
    command=f'curl -s -b {jar} '
    '-H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" '
    f'"https://sou.st/search?q={encoded}" 2>&1',
    timeout=15
)
# ⚠️ curl 方式搜索中文关键词经常 0 结果。优先用浏览器搜索 + console 提取 ID。

# Step 3: 下载
file_id = '147833'
filename = '凡尔纳经典科幻故事套装.epub'
output_path = f'/mnt/c/Users/admin/Desktop/儿童文学/{filename}'

r = terminal(
    command=f'curl -s -L -b {jar} -o "{output_path}" '
    '-H "User-Agent: Mozilla/5.0" '
    f'-H "Referer: https://sou.st/file/{file_id}" '
    '-w "%{{http_code}} %{{size_download}}" '
    f'"https://sou.st/file/{file_id}/download" 2>&1',
    timeout=120
)
# HTTP 200 = 成功
```

## 关键注意事项

1. **中文搜索不稳定**：curl URL 编码中文经常返回 0 结果。推荐流程：
   - 浏览器表单搜索 → browser_snapshot 看结果
   - browser_console 提取 IDs
   - curl 批量下载

2. **浏览器提取 ID**：
   ```js
   JSON.stringify(Array.from(document.querySelectorAll('a[href*="/file/"]'))
     .filter(a => a.closest('h3'))
     .map(a => ({id: a.href.match(/\/file\/(\d+)/)?.[1], text: a.textContent.trim()})))
   ```

3. **下载间隔**：每次下载后 sleep 2秒，避免触发限流。

4. **Cookie 有效期**：会话过期需重新登录获取新 CSRF token。

5. **积分扣减**：每文件 -1 积分，每日签到 +10。积分不足无法下载。

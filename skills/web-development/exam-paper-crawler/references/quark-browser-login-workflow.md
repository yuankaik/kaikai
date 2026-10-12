# 夸克网盘 — 浏览器登录 + 保存到网盘 工作流

> 更新时间：2026-06-17
> 验证会话：下午 + 晚间两次验证

---

## 核心事实

| 操作 | 方式 | 可行性 |
|:---|:---|:---:|
| 列出文件清单 | API（免Cookie）/ browser_console fetch | ✅ 稳定 |
| 下载文件 | API download endpoint | ❌ 始终 404 |
| 保存到网盘 | 浏览器 UI 点击"保存到网盘" | ✅ 需登录 |
| 浏览器登录 | 点击"登录账号" → QR扫码 | ⚠️ 需用户扫码 |
| 登录持久化 | 跨浏览器会话 | ❌ 不持久 |

## 标准流程

### Phase 1：提取文件清单（免登录，无需用户参与）

```python
# 纯 Python，无需 Cookie
import urllib.request, json

def get_token(pwd_id):
    url = f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc&pwd_id={pwd_id}"
    req = urllib.request.Request(url,
        data=json.dumps({"pwd_id": pwd_id, "passcode": ""}).encode(),
        headers={"Content-Type": "application/json", "Referer": "https://pan.quark.cn/"},
        method='POST')
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["stoken"]

def list_files(pwd_id, stoken, pdir_fid="0"):
    url = (f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail?"
           f"pr=ucpro&fr=pc&pwd_id={pwd_id}&stoken={urllib.parse.quote(stoken)}"
           f"&pdir_fid={pdir_fid}&_page=1&_size=100&_sort=file_type:asc,updated_at:desc")
    req = urllib.request.Request(url, headers={"Referer": "https://pan.quark.cn/"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["list"]
```

**关键**：此步骤完全不需要 Cookie 或登录。所有 pan.quark.cn/s/xxx 分享链接都适用。

### Phase 2：用户登录（需一次扫码）

1. `browser_navigate` 到任意 pan.quark.cn/s/xxx 链接
2. 等待 SPA 渲染（可能需要 5-10 秒，有时会超时重试）
3. 页面渲染后，点击"登录账号"按钮
4. 弹窗显示 QR 码 → **用户用夸克APP扫码**
5. 扫码成功后，页面会自动刷新 → 检查"登录账号"按钮是否变为用户头像

**⚠️ Pitfall：扫码后登录可能不生效**

如果扫码后页面仍然显示"登录账号"，原因可能是：
- 扫码在弹窗内完成，但父页面未收到回调
- 尝试：关闭弹窗 → 刷新页面 → 再次点击登录 → 重新扫码
- 极端情况：headless browser 的 cookie 域与扫码回调域不匹配

**当前最可靠方式**：用户扫码后，关闭弹窗，刷新页面（browser_navigate 同一URL），验证登录状态。

### Phase 3：保存到网盘 + 下载（登录后自动化）

1. 确认已登录（`browser_console` 调用 member API 返回 200）
2. 勾选要保存的文件/文件夹的 checkbox
3. 点击"保存到网盘"按钮
4. 文件保存到用户夸克网盘根目录
5. 从夸克网盘客户端或网页版 `pan.quark.cn` 下载

**⚠️ 即使登录后，API 下载仍不可行**

Cookie + API download endpoint 始终返回 404。即使通过 `browser_console` 在已登录的浏览器上下文中调用 fetch，download API 同样返回 404。

**可行替代**：告知用户"文件已保存到你的夸克网盘，请在夸克APP/客户端中下载"

### Phase 4：Agent 读取已下载文件

用户下载到桌面后：
```bash
ls /mnt/c/Users/admin/Desktop/shanghai-exams/quark-downloads/
```

Agent 可用 `read_file` 读取 PDF/MD，`search_files` 扫描目录。

## 已验证的链接状态

| 链接 | 状态 | 说明 |
|:---|:---:|:---|
| pan.quark.cn/s/741c0562dde1 | ✅ | 四上沪教版数学 14文件 |
| pan.quark.cn/s/02d3cd98e351 | ✅ | 四上口算应用题 21文件 |
| pan.quark.cn/s/c4a47d0c5989 | ✅ | 教辅超全合集-1（深层文件夹结构） |
| pan.quark.cn/s/710510d7 | ❌ 404 | 教辅超全合集-2 已失效 |
| pan.quark.cn/s/c433efc717ba | ✅ | 语文精品试卷 127子文件夹 |
| pan.quark.cn/s/2e0376b75a0b | ✅ | 语文课课练 39子文件夹 |
| pan.quark.cn/s/07fb24420e0e | ✅ | 数学精品试卷 105子文件夹 |
| pan.quark.cn/s/8eaab6bd9196 | ✅ | 数学课时练 39子文件夹 |
| pan.quark.cn/s/e63727797c10 | ✅ | 数学应用题 31PDF（实际可列出文件） |
| pan.quark.cn/s/aad6e2182b6f | ✅ | 人教版数学 1-6 |
| pan.quark.cn/s/7b39517111ff | ✅ | 北师大数学 |
| pan.quark.cn/s/8f0b07e21f5b | ✅ | 苏教版数学 |
| pan.quark.cn/s/4cbef46125df | ❌ 封禁 | 涉及违规内容 |

## Cookie 提取方式

从已登录的浏览器会话中提取：
```javascript
// browser_console
document.cookie.split('; ')
  .filter(c => c.startsWith('ctoken') || c.startsWith('b-user-id') || c.startsWith('tfstk'))
  .join('; ')
```

⚠️ Cookie 会过期。跨会话不持久。每次新会话需要重新登录。

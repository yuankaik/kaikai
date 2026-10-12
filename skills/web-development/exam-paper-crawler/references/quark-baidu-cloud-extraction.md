# 夸克网盘 & 百度网盘 资源提取方法

> 验证时间：2026-06-17（更新：2026-06-17）
> 来源：贴吧「小学教育吧」用户分享链接的实际提取经验
> **🆕 夸克下载自动化已升级为独立技能：`quark-cloud-drive`**
> 文件列表提取、浏览器登录、保存到网盘、批量下载的完整工作流请查看该技能。

---

## 夸克网盘 API 提取（无需登录）

夸克网盘分享页是 SPA（React），直接 browser_navigate 只看到空壳。
**必须用 browser_console 调用内部 API** 才能提取文件列表。

### 步骤

#### 1. 从分享链接提取 pwd_id

```
分享链接格式：https://pan.quark.cn/s/<pwd_id>
例如：https://pan.quark.cn/s/741c0562dde1 → pwd_id = 741c0562dde1
```

#### 2. 获取 stoken

```javascript
fetch('https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc&pwd_id=<pwd_id>', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({pwd_id: '<pwd_id>', passcode: ''})
}).then(r => r.json()).then(d => {
  console.log('stoken:', d.data.stoken);
  console.log('title:', d.data.title);
  console.log('author:', d.data.author.nick_name);
});
```

#### 3. 列出根目录文件

`pdir_fid=0` 表示根目录。`_sort` 参数可调整排序。

```javascript
fetch('https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail?pr=ucpro&fr=pc&pwd_id=<pwd_id>&stoken=<stoken>&pdir_fid=0&force=0&_page=1&_size=50&_sort=file_type:asc,updated_at:desc')
  .then(r => r.json())
  .then(d => d.data.list.map(f => ({
    name: f.file_name,
    fid: f.fid,
    size_kb: Math.round(f.size / 1024),
    is_dir: !f.size  // size 为 0 表示文件夹
  })));
```

#### 4. 进入子文件夹

判断文件夹的正确方式：检查 `dir: True`（不靠 `size=0`，部分文件夹也有非零 size）。文件夹还有 `include_items` 字段告诉你里面有多少文件。

```javascript
// 判断是否为文件夹
if (item.dir) {
  console.log(`📁 ${item.file_name}/ (${item.include_items} files)`);
  // pdir_fid 改为文件夹的 fid
  fetch('...detail?...&pdir_fid=' + item.fid + '&...')
}
```

### 备选方案：curl + Cookie 终端提取

当用户已登录夸克且提供 Cookie 时，可用终端 curl 调用 **列表 API**（列出文件清单）：

```bash
# 用户需提供的 Cookie 字段（从浏览器 F12 → Application → Cookies 复制）：
# ctoken, b-user-id, _UP_A4A_11_, _UP_D_

COOKIE="ctoken=xxx; b-user-id=xxx; _UP_A4A_11_=xxx; _UP_D_=pc"

# ✅ 获取 stoken — 可行
curl -s -b "$COOKIE" \
  -H "Content-Type: application/json" \
  "https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc&pwd_id=<pwd_id>" \
  -d '{"pwd_id":"<pwd_id>","passcode":""}'

# ✅ 列出文件清单 — 可行
curl -s -b "$COOKIE" \
  "https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail?...&pdir_fid=<fid>&_page=1&_size=50"

# ❌ 下载文件 — 不可行！download API 始终返回 404
```

**⚠️ 关键限制**：即使有完整 Cookie，`download` API 始终返回 404。Cookie 只能用于列出文件清单，不能用于下载。浏览器 `document.cookie` 注入也不够（夸克 SPA 额外检查 localStorage/sessionStorage，仍弹出登录框）。\n\n### 完整 Python 提取脚本（无需 Cookie 版本）

```python
import urllib.request, json, urllib.parse

headers_base = {
    "Content-Type": "application/json",
    "Referer": "https://pan.quark.cn/"
}

def get_token(pwd_id):
    req = urllib.request.Request(
        f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc&pwd_id={pwd_id}",
        data=json.dumps({"pwd_id": pwd_id, "passcode": ""}).encode(),
        headers=headers_base)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["stoken"]

def list_files(pwd_id, stoken, pdir_fid="0"):
    url = (f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail?"
           f"pr=ucpro&fr=pc&pwd_id={pwd_id}&stoken={urllib.parse.quote(stoken)}"
           f"&pdir_fid={pdir_fid}&_page=1&_size=50"
           f"&_sort=file_type:asc,updated_at:desc")
    req = urllib.request.Request(url, headers=headers_base)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["list"]

# 使用示例
stoken = get_token("741c0562dde1")
root = list_files("741c0562dde1", stoken)
for item in root:
    if item.get("dir"):
        inner = list_files("741c0562dde1", stoken, item["fid"])
        for f in inner:
            print(f"  {f['file_name']} ({f.get('size',0)//1024}KB)")
```

### 下载限制

- **CORS 阻止**：download API 返回 `Invalid CORS request`，浏览器端 fetch() 无法下载
- **curl 也失败**：即使带上完整 Cookie（ctoken, b-user-id, _UP_A4A_11_, _UP_D_），download API 仍然返回 404
- **Cookie 注入不够**：通过 browser_console 设置 `document.cookie` 后，夸克 SPA 仍弹出登录框——它额外检查 localStorage/sessionStorage
- **可行方案**：拿到文件清单后，让用户在浏览器中扫码登录夸克，然后手动「保存到网盘」→ 下载
- **用户操作指南**：打开链接 → 夸克APP扫码 → 点保存到网盘 → 从APP下载/打印
- **绝不说「链接在这里你自己下」** —— 必须给出：文件名清单 + 优先级排序 + 下载步骤 + 手机/电脑操作说明

### 已验证的链接状态

| 链接 | 状态 | 备注 |
|------|:---:|------|
| pan.quark.cn/s/4cbef46125df | ❌ 封禁 | code=41010 "文件涉及违规内容" |
| pan.quark.cn/s/741c0562dde1 | ✅ | 四上沪教版数学，14文件 |
| pan.quark.cn/s/02d3cd98e351 | ✅ | 四上口算应用题，21文件 |

---

## 百度网盘链接提取

### 步骤

1. 直接 browser_navigate 到分享链接（含提取码）
   ```
   https://pan.baidu.com/s/<share_id>?pwd=<提取码>
   ```
2. 页面会显示文件名、分享者、有效期
3. **下载需要登录**百度账号，无法绕过
4. 可以记录文件名和大小供参考

### 已验证链接

```
# 53天天练英语四下(YL)
https://pan.baidu.com/s/1T-HCMVvT7xmscUguBCuQsQ?pwd=do41 → 永久有效

# 53天天练英语四下(人教版)
https://pan.baidu.com/s/1LaTAyG6Op43fYFqX9dqAbg?pwd=xmd7 → 永久有效
```

---

## 输出资源清单模板

```markdown
# 贴吧资源清单

## 链接N：标题
🔗 URL

| # | 文件名 | 大小 | 适用度 |
|---|--------|------|:---:|
| 1 | xxx.pdf | 350KB | ⭐⭐⭐⭐⭐ |
| 2 | xxx.pdf | 27MB  | ⭐⭐⭐⭐   |

**推荐下载**：
1. 🥇 ...
2. 🥈 ...
3. 🥉 ...

**⚠️ 不建议**：增强版/奥数类（D水平学生不适合）
```

### 评分标准

- ⭐⭐⭐⭐⭐：基础练习，有答案，适合D水平
- ⭐⭐⭐⭐：正常难度，可后期使用
- ⭐⭐⭐：偏难或有专项要求
- ⭐⭐：综合卷/模拟卷，适合水平提升后
- ⭐：拔高/奥数类，D水平禁止使用

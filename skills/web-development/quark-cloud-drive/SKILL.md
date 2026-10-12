---
name: quark-cloud-drive
description: 夸克网盘资源自动化：API列文件（免登录）+ 浏览器登录 → 保存到网盘 → 批量下载到桌面。用于从贴吧等平台发现的 pan.quark.cn 分享链接。
---

# 夸克网盘自动化下载

> ⚠️ **2026-06-18 状态：save API 已死。** 即使用户提供全部浏览器 Cookie（10+字段），save 端点持续返回 401。list API（免登录列文件）仍可用。**脚本化保存已不可行，只能用户手动在浏览器操作。** 本技能保留 list 功能，不再尝试脚本化 save/download。

## 触发条件

- 用户提到 `pan.quark.cn` 链接
- 用户要求下载夸克网盘资源
- 用户在贴吧/道客巴巴等平台发现了夸克分享链接
- 需要批量提取夸克网盘文件清单并下载

## ⚠️ 链接发现限制（2026-06-29）

**夸克网盘链接只能由用户侧发现，Agent 无法搜索。**
- 找 pan.quark.cn 分享链接依赖百度/Bing/贴吧等搜索引擎 → 全部不可达
- 用户需在自己手机/电脑上的夸克APP或浏览器中搜索书名+夸克，把链接发给 Agent
- Agent 拿到 pwd_id 后可通过 list API 列出文件（免登录）

## 核心认知

夸克网盘分两个阶段操作：

| 阶段 | 操作 | 需要登录 | 方法 |
|:---|:---|:---:|:---|
| Phase 1 | 列出文件清单 | ❌ 不需要 | Python `urllib` 调 API |
| Phase 2 | 保存到网盘 + 下载 | ✅ 需要 | 浏览器登录 → 点击保存 → 下载 |

**Phase 1 无任何限制**，可以批量列出所有链接的文件。Phase 2 需要用户扫码登录一次浏览器，之后 Agent 自动化剩余所有操作。

## Phase 1: 列出文件清单（免登录）

### Python 脚本模板

使用 `execute_code` 运行，无需任何 Cookie：

```python
import urllib.request, json, urllib.parse, time

headers = {
    "Content-Type": "application/json",
    "Referer": "https://pan.quark.cn/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_token(pwd_id):
    """从分享链接获取 stoken（无需登录）"""
    url = f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc&pwd_id={pwd_id}"
    req = urllib.request.Request(url,
        data=json.dumps({"pwd_id": pwd_id, "passcode": ""}).encode(),
        headers=headers, method='POST')
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["stoken"]

def list_files(pwd_id, stoken, pdir_fid="0"):
    """列出文件/文件夹（无需登录，支持递归进入文件夹）"""
    url = (f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail?"
           f"pr=ucpro&fr=pc&pwd_id={pwd_id}&stoken={urllib.parse.quote(stoken)}"
           f"&pdir_fid={pdir_fid}&_page=1&_size=100"
           f"&_sort=file_type:asc,updated_at:desc")
    req = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["list"]

# 批量处理多个链接
links = {
    "名称": "pwd_id_from_url",
}

for name, pwd_id in links.items():
    stoken = get_token(pwd_id)
    root = list_files(pwd_id, stoken)
    for item in root:
        if item.get("dir"):
            # 进入文件夹
            inner = list_files(pwd_id, stoken, item["fid"])
            for f in inner:
                print(f"  {f['file_name']} ({f.get('size',0)//1024}KB)")
        else:
            print(f"{item['file_name']} ({item.get('size',0)//1024}KB)")
    time.sleep(0.5)  # 限速
```

### 字段说明

| 字段 | 含义 | 用法 |
|:---|:---|:---|
| `file_name` | 文件名 | 展示给用户 |
| `fid` | 文件/文件夹ID | 递归进入子目录、下载 |
| `dir` | 是否为文件夹 | `True` = 文件夹, `False` = 文件 |
| `size` | 文件大小(字节) | 判断文件类型（0KB 通常是文件夹） |
| `include_items` | 文件夹内文件数 | 仅在 `dir=True` 时有效 |

### 常见返回码

| code | 含义 |
|:---|:---|
| 200/0 | 正常 |
| 41010 | 链接违规被封禁 |
| 404 | 链接不存在或已删除 |

## Phase 2: 登录 → 保存 → 下载

### ⚠️ 关键认知：云端浏览器 ≠ 用户本地浏览器

Hermes 的 browser 工具运行在**云端浏览器（Browserbase）**上，和用户 Windows 本地的 Chrome/Edge 是**两个完全独立的浏览器实例**。

后果：
- 用户在 Windows 上登录夸克 → 云端浏览器收不到任何 Cookie
- 用户在云端浏览器扫码登录 → 下次会话 Cookie 可能丢失
- browser_console 提取的 Cookie（ctoken, b-user-id）缺少 `tfstk` → save API 返回 401

**唯一可行的自动化路径**：用户从自己本地浏览器（F12 → Application → Cookies）复制 Cookie，Agent 用 Python urllib + Cookie 调 API。

### 获取用户 Cookie（一次性，Copy-Paste）

让用户在**已登录夸克的本地浏览器**中：
1. F12 → Application → Storage → Cookies → `pan.quark.cn`
2. **复制全部字段**（不是只三个），必需的 9 个字段：
   - `ctoken` — 短token
   - `b-user-id` — 用户ID
   - `tfstk` — **核心认证token，~2000字符，最关键！**
   - `__wpkreporterwid_` — 会话ID
   - `xlly_s` — 固定值 "1"
   - `__sdid` — 设备ID（部分场景可能不需要，但建议完整复制）
   - `isg` — 安全令牌
   - `_UP_A4A_11_` — 用户凭证
   - `_UP_D_` — 设备类型("pc")

   ⚠️ **更新 Cookie 时同步检查桌面脚本** `C:\Users\admin\Desktop\quark_batch_download.py` 的 `COOKIES` 字典是否包含所有字段。历史版本可能缺少 `__sdid`，需补充。
3. 粘贴给 Agent，格式：`ctoken=xxx; b-user-id=yyy; tfstk=zzz; ...`

⚠️ **仅 ctoken + b-user-id 不够**，缺少任何上述字段 save API 都返回 401。tfstk 最长，可分段发送让 Agent 拼接。

### Cookie 存储与复用

Cookie 存两份：
- `~/.hermes/quark_cookies.json` — WSL端存储（JSON格式）
- `C:\Users\admin\Desktop\quark_batch_download.py` — Windows批量脚本（内嵌Cookie）

拿到新Cookie后**必须同时更新两个位置**。

### Windows 端执行（必须）

**关键限制**：夸克 Cookie 与生成时的 IP 绑定。从 WSL 调用 API 始终 401。

正确执行方式：
```bash
cmd.exe /c "python C:\Users\admin\Desktop\quark_batch_download.py"
```
脚本先列出所有链接的文件清单，再调用 save API 批量保存到用户网盘。

### 用 Cookie 调 save API（Python，不需要浏览器）

拿到用户 Cookie 后，用 `execute_code` 运行 Python 脚本，逐链接调用 save API：

```python
import urllib.request, json, urllib.parse, os, time

COOKIE = "ctoken=xxx; b-user-id=yyy; tfstk=zzz"  # 用户提供
DESKTOP = "/mnt/c/Users/admin/Desktop/shanghai-exams/quark-downloads"
os.makedirs(DESKTOP, exist_ok=True)

headers = {
    "Content-Type": "application/json",
    "Referer": "https://pan.quark.cn/",
    "User-Agent": "Mozilla/5.0",
    "Cookie": COOKIE
}

def get_token(pwd_id):
    url = f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc&pwd_id={pwd_id}"
    req = urllib.request.Request(url,
        data=json.dumps({"pwd_id": pwd_id, "passcode": ""}).encode(),
        headers=headers, method='POST')
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["stoken"]

def list_files(pwd_id, stoken, pdir_fid="0"):
    url = (f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail?"
           f"pr=ucpro&fr=pc&pwd_id={pwd_id}&stoken={urllib.parse.quote(stoken)}"
           f"&pdir_fid={pdir_fid}&_page=1&_size=100")
    req = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["list"]

def save_to_drive(pwd_id, stoken, fids):
    """保存文件到用户网盘根目录。返回保存结果。"""
    url = (f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/save?"
           f"pr=ucpro&fr=pc&pwd_id={pwd_id}&stoken={urllib.parse.quote(stoken)}")
    req = urllib.request.Request(url,
        data=json.dumps({"fids": fids, "to_pdir_fid": "0"}).encode(),
        headers=headers, method='POST')
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

# 批量保存所有链接
all_links = {
    "教辅合集-1": "c4a47d0c5989",
    "语文试卷": "c433efc717ba",
    "数学试卷": "07fb24420e0e",
    # ...
}
for name, pwd_id in all_links.items():
    stoken = get_token(pwd_id)
    root = list_files(pwd_id, stoken)
    fids = [f["fid"] for f in root]
    result = save_to_drive(pwd_id, stoken, fids)
    print(f"{name}: {result.get('message', result)}")
    time.sleep(1)
```

### 登录状态检测（用户 Cookie 有效性）

```python
member_url = "https://drive-pc.quark.cn/1/clouddrive/member?pr=ucpro&fr=pc"
req = urllib.request.Request(member_url, headers=headers)
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
# status=200 → 已登录, status=401 → Cookie过期需重新获取
```

### Cookie 生命周期

- 夸克 Cookie（含 tfstk）有效期约 **24 小时**
- 过期后用户需重新从浏览器复制
- 如果用户在夸克APP/网页端主动退出登录，Cookie 立即失效
- 不要在 memory 中存储完整 Cookie（太长），只需记住"需要向用户获取"这个流程

## 完整自动化批量流程

当有多个夸克链接需要处理时：

```
Phase 1（批量，无需用户）：
├── execute_code 运行 Python 脚本
├── 逐个链接调用 get_token + list_files + 递归进入子目录
├── 输出完整文件清单（含大小、嵌套结构）
└── 生成「资源清单.md」放桌面

Phase 2（用户扫码一次，Agent 自动化剩余）：
├── browser_navigate 到第一个链接
├── browser_click "登录账号"
├── 等待用户扫码（告知用户"请扫码"）
├── 检测登录成功
├── 对该链接：选中全部文件 → 点击"保存到网盘"
├── browser_navigate 到下一个链接 → 重复保存
├── 全部保存完成后，生成下载指引
└── 保存为技能，记忆 Cookie 位置
```

## ⚠️ 2026-06 更新：save API 可能已全面锁定

经过多次尝试（2026-06-18），即使用户提供**浏览器当前登录的全部 Cookie**（含 ctoken, b-user-id, d-user-id, tfstk, grey-id, isg, xlly_s, __wpkreporterwid_, _UP_A4A_11_, _UP_D_ 等 10+ 字段），**save API 仍持续返回 401**，而 list API 正常工作。

**结论**：夸克可能对 save 端点增加了额外的浏览器指纹/CSRF 保护，Python urllib 调用已不可行。

**当前可行方案**：
- ✅ list API：仍然免登录可用，可批量列出所有链接文件清单
- ❌ save API：Python 脚本已无法调用
- 🔧 替代方案：用户在自己浏览器（已登录夸克）中手动打开链接 → 点「保存到网盘」

**用户已决定放弃夸克网盘路径**（2026-06-18）。本技能保留 list API 功能（免登录列出文件清单仍有价值），但不再尝试脚本化 save/download。

---

## 常见错误与对策

| 错误 | 原因 | 解决 |
|:---|:---|:---|
| save API 返回 401（即使 Cookie 完整） | **夸克 save API 已加浏览器指纹保护（2026-06确认）**，Python 脚本无法绕过 | 放弃脚本化 save，改用手动浏览器保存；或放弃夸克路径 |
| save API 返回 401 `require login [guest]` | Cookie 缺少 `tfstk` 或 `tfstk` 过期 | 用户重新从本地浏览器复制完整 Cookie |
| save API 返回 401（即使有 ctoken+b-user-id） | **仅有 ctoken+b-user-id 不够，必须含 tfstk**。但即使含全部 Cookie 也可能 401（见上方警告） | 先尝试完整 Cookie；仍失败则放弃脚本化 save |
| 云端浏览器登录后 API 仍 401 | **云端浏览器(Browserbase)和用户本地浏览器是独立实例**，用户在本地登录不影响云端 | 改用 Cookie 复制 + Python API 方案 |
| 浏览器截图二维码给用户扫 | Canvas 二维码在截图里可能是空白；且即使扫成功，登录态在云端浏览器，下次会话丢失 | 不用这个方案，直接用 Cookie 复制 |
| download API 返回 404 | 夸克 download API 始终需认证且端点不稳定 | 使用"保存到网盘"（save API）替代直接下载 |
| SPA 页面空白快照 | React 渲染延迟 | 等待 2-3 秒后 `browser_snapshot`，或刷新 |
| `browser_navigate` 超时 | 夸克页面加载慢 | 正常现象，重试即可。超时后 console 仍可用 |
| 链接 404 | 链接已失效或 pwd_id 错误 | 跳过该链接 |
| 链接返回 41010 | 文件违规被封 | 跳过，标记为"已封禁" |
| 文件夹递归过深 | 嵌套层级多 | 限制递归深度到 2-3 层 |
| `include_items` 字段缺失 | 旧版 API 响应 | 改用 `dir: True` 判断是否为文件夹 |
| Cookie 中 tfstk 被截断 | 终端/输入框有字符限制 | 让用户分两段发送，Agent 自行拼接 |
| 桌面脚本 `quark_batch_download.py` 的 COOKIES 字典缺少 `__sdid` | 历史脚本只含 8 个字段，未写入 `__sdid` | 更新 Cookie 时一并检查并补充 `__sdid` 字段 |\n| save API 连续 3 次 401（不同方法都试过） | Cookie 过期（~24h有效期）或缺少关键字段 | **立即停止尝试，直接告诉用户"Cookie过期，请重新从浏览器复制全部字段"**。不要反复换方法重试，浪费时间和token |

## 已掌握的夸克 API 端点

| 端点 | 方法 | 认证 | 用途 |
|:---|:---:|:---:|:---|
| `/share/sharepage/token` | POST | ❌ 无需 | 获取 stoken |
| `/share/sharepage/detail` | GET | ❌ 无需(stoken) | 列出文件 |
| `/share/sharepage/save` | POST | ✅ 需要 Cookie | 保存到我的网盘 |
| `/share/sharepage/download` | GET | ❌ 不可用 | 始终404，不要尝试 |
| `/share/sharepage/task` | POST | ✅ 需要 Cookie | 创建下载任务 |
| `/clouddrive/member` | GET | ✅ 需要 Cookie | 检查登录状态 |

## 已验证的夸克分享链接（2026-06-17）

### 🥇 教辅品牌合集
| 链接ID | 内容 | 来源 | 状态 |
|:---|:---|:---|:---:|
| `c4a47d0c5989` | 教辅超全大合集(学而思乐读+53+黄冈+实验班+王朝霞+猿辅导等20+品牌) | 贴吧 Lily的资源库 | ✅ |
| `710510d7` | 教辅合集-2 | 同上 | ❌ 404 |

### 🥈 语文资源
| 链接ID | 内容 | 来源 | 状态 |
|:---|:---|:---|:---:|
| `c433efc717ba` | 语文精品试卷 1-6上(53/黄冈/实验班/王朝霞/小白鸥等，127子文件夹) | 贴吧 爱学习的喵姬♀ | ✅ |
| `2e0376b75a0b` | 语文课课练 1-6上(课课练/实验班/53随堂测/亮点/拔尖特训等，39子文件夹) | 同上 | ✅ |

### 🥉 数学资源
| 链接ID | 内容 | 来源 | 状态 |
|:---|:---|:---|:---:|
| `07fb24420e0e` | 数学人教版精品试卷 1-6上(53全优卷/黄冈/实验班/孟建平/王朝霞等，105子文件夹) | 贴吧 爱学习的喵姬♀ | ✅ |
| `8eaab6bd9196` | 数学人教版课时练 1-6上(53天天练/一遍过/典中点/五星学霸等，39子文件夹) | 同上 | ✅ |
| `e63727797c10` | 数学应用题合集(红逗号易错题+天天刷+随堂集训+斗半匠，31个PDF) | 同上 | ✅ |
| `aad6e2182b6f` | 数学人教版试卷习题汇总 1-6上下册 | 贴吧 go芜湖爆破手 | ✅ |
| `7b39517111ff` | 数学北师大版 1-6上下册 | 同上 | ✅ |
| `8f0b07e21f5b` | 数学苏教版 1-6上下册 | 同上 | ✅ |

### 🏅 上海沪教版（已下载到桌面）
| 链接ID | 内容 | 来源 | 状态 |
|:---|:---|:---|:---:|
| `741c0562dde1` | 四上沪教版数学(53天天练/一课一练/一卷搞定/期中期末卷等14文件) | 贴吧 汤姆百宝箱 | ✅ 已下载 |
| `02d3cd98e351` | 四上口算应用题(小猿口算/10000题/计算小超市/必练100题等21文件) | 同上 | ✅ 已列出 |

## 快速状态检查（用户问"做到哪了"时）\n\n当用户询问夸克下载进度时：\n1. 读桌面 `quark_batch_download.py` 确认当前 LINKS 字典和 COOKIES 状态\n2. 列出全部链接，标注 ✅已保存 / ⏳待处理\n3. 如果 Cookie 超过 24 小时未更新 → 主动告知需要重新获取\n4. 给用户清晰的下一步指令（登录 → F12 → 复制所有字段 → 发过来）\n\n## 输出规范

Phase 1 输出到桌面：
```
C:\Users\admin\Desktop\shanghai-exams\夸克资源清单-<日期>.md
```

格式：链接 → 标题 → 文件夹树 → 文件列表（含大小）→ 与知识点匹配建议。

## 与 exam-paper-crawler 的协作

`exam-paper-crawler` 技能负责：
- 从贴吧/道客巴巴搜索夸克网盘链接
- 教育资源分类与知识点匹配

本技能负责：
- 列出链接中的文件
- 自动化登录和下载

两个技能配合使用：exam-paper-crawler 发现链接 → quark-cloud-drive 提取文件 → 下载到桌面。

---
name: chinese-social-search
description: Search Chinese social platforms (B站, 小红书, 知乎, 微博, 豆瓣, 大众点评) via cn-scraper-mcp MCP server. Also covers browser-based fallback when MCP tools aren't available.
---

# 中文社交平台搜索

## 主力方案：cn-scraper-mcp（MCP Server）

**cn-scraper-mcp** (v0.5.0, goesByhc) 是专门让 AI Agent 搜索中文互联网的 MCP 服务器。安装后 Hermes 直接获得 30+ 搜索工具，无需手动操作浏览器。

覆盖平台：B站、小红书、知乎、微博、豆瓣、大众点评、淘宝、京东、知识星球。

### 安装

```bash
sudo $(which uv) pip install --system --break-system-packages cn-scraper-mcp
```

### Hermes MCP 配置

```bash
# 正确方式（自动发现工具 + 正确写 YAML 列表）
yes | hermes mcp add --command cn-scraper-mcp --connect-timeout 30 cn-scraper
```

> **⚠️ 不要用 `hermes config set`！** `hermes config set mcp_servers.cn-scraper.args "[]"` 会把 args 存成 YAML 字符串 `'[]'` 而非列表 `[]`，导致 MCP 发现静默失败（"no MCP tools available"）。只有 `hermes mcp add` 能正确写入 YAML 结构。

配置后**重启 Hermes**，40 个 MCP 工具自动注册（前缀 `mcp_cn-scraper_`）。

### 登录（按需）

大部分平台需要登录态。**先用 `check_cookies` 查看所有平台状态**，再按需登录。

通过 MCP 工具引导登录（理想路径，自动打开 Chrome 扫码）：

```
guided_login(platform="weibo")     # 微博
guided_login(platform="zhihu")     # 知乎
guided_login(platform="xiaohongshu")  # 小红书（需住宅IP + 本地Chrome）
guided_login(platform="douyin")    # 抖音（需手动过验证码）
```

Cookie 保存在 `~/.cn-scraper-cookies/`，不写入日志。

#### WSL Chrome 启动失败回退方案

WSL 下 `guided_login` 可能无法自动启动 Chrome 窗口。此时手动启动 Chrome 带 CDP 端口：

```bash
# 1. 手动启动 Chrome（窗口会通过 WSLg 弹出）
google-chrome --remote-debugging-port=9251 \
  --no-first-run --no-default-browser-check \
  --user-data-dir=/tmp/xhs-chrome-profile \
  "https://www.xiaohongshu.com" &

# 2. 确认 Chrome 已监听
ss -tlnp | grep 9251  # 应看到 LISTEN

# 3. 在 Chrome 窗口中扫码登录完成后，收割 Cookie
harvest_cookies(platform="xiaohongshu")
```

> 端口：小红书用 9251，其他平台同理。`--user-data-dir` 用临时目录避免污染默认 Profile。

### 无需登录的平台

| 平台 | 工具 | 实测 | 说明 |
|------|------|:--:|------|
| B站 | `bilibili_popular` | ✅ | 热门榜，无需登录，稳定可用 |
| 微博 | `weibo_hot_list` | ✅ | 热搜榜，无需登录，51条实时热搜 |
| B站 | `bilibili_search` | ⚠️ | 公开API，但偶发HTTP 412，可重试 |
| 微博 | `weibo_search` | ❌ | 需登录Cookie（SUB token） |

### 需要登录的平台

| 平台 | 工具 | 实测 | 门槛 |
|------|------|:--:|------|
| 知乎 | `zhihu_hot_list` | ❌ | 实测需登录（v0.5.0） |
| 知乎 | `zhihu_search` | ❌ | 需登录态（z_c0 + d_c0） |
| 小红书 | `xiaohongshu_search` | ❌ | 需本地Chrome + 住宅IP |
| 豆瓣 | `douban_search` | ❌ | 可能触发风控 |
| 大众点评 | `dianping_search` | ❌ | 可能触发页面风控 |

> 详细工具列表见 `references/cn-scraper-mcp.md`

## 回退方案（MCP 工具不可用时）

当 cn-scraper-mcp 未安装或重启前来不及用时，用浏览器直接搜。

### 平台可访问性阶梯（浏览器模式）

| 平台 | 开放度 | 方案 | 可靠性 |
|------|:---:|------|:---:|
| 📕 小红书 | ⭐⭐⭐ | **CDP + DOM 选择器**（见下） | ✅ |
| 📺 B站 | ⭐⭐⭐ | `browser_navigate` + `browser_snapshot` | ✅ |
| 💬 豆瓣/贴吧 | ⭐⭐ | curl 或浏览器（贴吧直连 403，需登录浏览器会话） | ⚠️ |
| ❓ 知乎 | ⭐⭐ | 浏览器可读部分内容（MCP 更省事） | ⚠️ |
| 🎵 抖音 | ⭐ | 需登录扫码 | ❌ |

> ⚠️ **本技能旧版曾写"小红书基本不可用、不要浪费超过 2 次尝试"—— 已推翻，那是错的。**
> 小红书走 CDP + DOM 选择器实测稳定拿到 20+ 条完整笔记（标题/作者/点赞/noteId/URL）。
> 当初判"不可用"的真实原因：用 `innerText` 提文字，而卡片文字不在 `innerText` 里
> （页面有 42 卡片，`innerText` 只返回约 200 字符的侧边栏+页脚）。
> **直接跑** `cn-platform-full-stack/scripts/xhs_search.py "关键词"`。

### B站浏览器搜索模板

```
browser_navigate → https://www.bilibili.com/search?keyword=关键词
browser_snapshot → 提取标题、UP主、播放量、摘要
```

搜索策略：多角度关键词 × 3-5 轮，够用就停。B站搜不到就换平台，不空转。

## 铁律

- **有 MCP 用 MCP，没 MCP 用脚本，最后才用浏览器**——浏览器最慢
- **同平台/同工具连败 3 次 → 立刻换思路**
- **小红书别用 `xiaohongshu_search`**（恒返回 XHS_EMPTY 是 bug）→ 改用 `cn-platform-full-stack/scripts/xhs_search.py`
- **百度/搜狗用直连 HTTP**（curl/urllib + 真实 UA，无反爬），**不要用无头浏览器**（会触发验证码）。脚本见 `cn-platform-full-stack/scripts/cn_search.py`
- **贴吧是唯一必须走浏览器会话的**——直连 403，登录百度后自动带过
- **登录优先**：一次 Chrome 会话把所有平台扫完，再统一 `harvest_cookies`
- **零成本探针**：微博热搜（`weibo_hot_list`）免登录永远能调，可用来判断"是平台问题还是网络/工具问题"

## 相关技能

- **`cn-platform-full-stack`** — 本主题的完整版：全平台可用性矩阵 + 百度/搜狗/贴吧直连方案 + CDP 浏览器诊断模式 + 登录收割全流程。**优先看这个。**
- `cn-scraper-mcp-usage` — MCP 工具细节、Cookie 持久性、知乎文章提取、间歇性登录错误
- `mediacrawler` (51K⭐) — 独立爬虫，需要 Cookie + Playwright
- `native-mcp` — Hermes MCP 客户端配置指南（bundled）

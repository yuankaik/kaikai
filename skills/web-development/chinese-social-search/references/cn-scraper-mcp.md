# cn-scraper-mcp — 安装与配置参考

## 仓库

GitHub: `goesByhc/cn-scraper-mcp`
- ⭐ 13 (2026-07-30)
- 版本: v0.5.0 (2026-07-28)
- 语言: Python (FastMCP 3.4.5)
- License: MIT
- Topics: ai-agent, bilibili, claude, cursor, mcp, mcp-server, xiaohongshu, zhihu, weibo

## 描述

> Let AI agents search the Chinese internet via MCP — Taobao, JD, Xiaohongshu, Zhihu, Weibo, Bilibili, ZSXQ, Douban, Dianping, and more.

## 安装

```bash
# WSL/Debian (system-managed Python — requires sudo + break-system-packages)
sudo $(which uv) pip install --system --break-system-packages cn-scraper-mcp

# 一般环境
pip install cn-scraper-mcp
```

> 注意：`sudo` 下 `uv` 不在 PATH，必须用 `$(which uv)` 展开完整路径。

## Hermes MCP 配置

```bash
# 正确方式（自动发现全部 40 个工具 + 正确写入 YAML 列表结构）
yes | hermes mcp add --command cn-scraper-mcp --connect-timeout 30 cn-scraper
```

> **⚠️ 绝对不要用 `hermes config set`！** `hermes config set mcp_servers.cn-scraper.args "[]"` 会把 args 存成 YAML 字符串 `'[]'` 而非列表 `[]`，导致 MCP 工具发现静默失败（表现为工具列表里找不到任何 `mcp__cn_scraper__*` 工具）。只有 `hermes mcp add` 能正确写入 YAML 列表结构。

配置后**重启 Hermes**（`/new`），40 个 MCP 工具自动注册（前缀 `mcp__cn_scraper__`），重启后在对话中直接可用。

## 验证

```bash
# 确认安装
which cn-scraper-mcp

# 测试运行（5 秒后自动终止）
timeout 5 cn-scraper-mcp
```

## 平台与登录需求

| 平台 | 工具 | 无需登录 | 登录方式 |
|------|------|:---:|------|
| B站 | `bilibili_search`, `bilibili_popular` | ✅ | 无需登录 |
| 知乎 | `zhihu_search`, `zhihu_hot_list`, `zhihu_answer` 等 | ❌ | `guided_login("zhihu")` |
| 微博 | `weibo_search`, `weibo_hot_list`, `weibo_post` 等 | 热搜✅ / 搜索❌ | `guided_login("weibo")` |
| 小红书 | `xiaohongshu_search`, `xiaohongshu_note` 等 | ❌ | `guided_login("xiaohongshu")` — 需本地Chrome+住宅IP |
| 豆瓣 | `douban_search` | ❌ | `guided_login("douban")` |
| 大众点评 | `dianping_search` | ❌ | `guided_login("dianping")` |
| 抖音 | `douyin_search`, `douyin_hot_list` | ❌ | `guided_login("douyin")` — 需手动过验证码 ⚠️ |
| 知识星球 | `zsxq_search` | ❌ | `guided_login("zsxq")` |
| 淘宝 | `taobao_search`, `taobao_product` | ❌ | `guided_login("taobao")` |
| 京东 | `jd_search`, `jd_product` | ❌ | `guided_login("jd")` — 保存Chrome Profile |

## Cookie 存储

- 目录: `~/.cn-scraper-cookies/`
- 京东额外: `~/.jd_login_profile/`（Chrome Profile）
- Cookie 值不写入日志，不通过 MCP 工具结果返回

## 完整 MCP 工具列表（v0.5.0）

### 电商
- `taobao_search` — 淘宝/天猫关键词搜索
- `taobao_product` — 淘宝商品详情
- `jd_search` — 京东关键词搜索
- `jd_product` — 京东商品详情
- `pdd_search` — 拼多多搜索（仅首次有效，不推荐）

### 内容社区
- `xiaohongshu_search` — 小红书笔记搜索
- `xiaohongshu_note` — 小红书笔记详情
- `xiaohongshu_comments` — 小红书评论
- `zhihu_search` — 知乎搜索
- `zhihu_hot_list` — 知乎热榜
- `zhihu_answer` — 知乎回答正文
- `zhihu_question_answers` — 知乎问题回答列表
- `zhihu_comments` — 知乎评论
- `weibo_search` — 微博搜索
- `weibo_hot_list` — 微博热搜榜
- `weibo_user_timeline` — 微博用户时间线
- `weibo_post` — 微博帖子详情
- `weibo_comments` — 微博评论
- `bilibili_search` — B站视频搜索
- `bilibili_popular` — B站热门视频榜
- `douyin_search` — 抖音搜索 ⚠️ 实验性
- `douyin_hot_list` — 抖音热搜榜
- `douyin_video` — 抖音视频详情
- `douyin_comments` — 抖音视频评论
- `douban_search` — 豆瓣条目搜索
- `dianping_search` — 大众点评商户搜索

### 登录管理
- `guided_login(platform)` — CDP 自动登录并保存 Cookie
- `harvest_cookies(platform)` — 从已登录 Chrome 读取 Cookie

## 相关对比

| 工具 | 类型 | 接入方式 | 配置门槛 | 推荐度 |
|------|------|------|:---:|:---:|
| cn-scraper-mcp | MCP Server | Hermes MCP 原生 | 低 | ⭐⭐⭐ |
| MediaCrawler (51K⭐) | 独立爬虫 | CLI 调用 | 高（Cookie+Playwright） | ⭐ |
| redbooks (⭐24) | GUI 爬虫 | Windows 桌面 | 中（需显示器） | ❌ WSL不可用 |

## 常见问题

### guided_login 报 ACTION_REQUIRED
平台要求人工处理（验证码/风控），按返回的 action_required 字段提示操作。

### WSL 下 guided_login 启动 Chrome 失败
`guided_login` 自动启动 Chrome 在 WSL 下可能失败（即便已安装 Chrome + WSLg DISPLAY 可用）。手动方案：

```bash
# 1. 手动启动带 CDP 端口的 Chrome（窗口通过 WSLg 弹出到 Windows 桌面）
google-chrome --remote-debugging-port=9251 \
  --no-first-run --no-default-browser-check \
  --user-data-dir=/tmp/xhs-chrome-profile \
  "https://www.xiaohongshu.com" &

# 2. 确认 Chrome 监听
ss -tlnp | grep 9251

# 3. 扫码登录后，通过 MCP 收割 Cookie
# harvest_cookies(platform="xiaohongshu")
```

各平台默认端口：小红书 9251，抖音 9222，京东 9247。

### B站搜索偶发 HTTP 412
`bilibili_search` 可能临时返回 HTTP 412，但 `bilibili_popular`（热门榜）和 `bilibili_video`（视频详情）通常正常。搜索失败时先用热门榜或换关键词重试。

### 知乎热榜需要登录
`zhihu_hot_list`（v0.5.0 实测）返回"知乎热榜需要登录"，与文档描述不一致。需要先 `guided_login("zhihu")` 收割 Cookie。

### 小红书搜不到
小红书只允许住宅 IP。数据中心/云服务器 IP 直接封。必须在本地机器运行，且用本地 Chrome。

### 远程服务器部署
Docker 镜像内置 Chromium，但小红书仍需住宅 IP。远程 HTTP 模式不要裸露公网端口。

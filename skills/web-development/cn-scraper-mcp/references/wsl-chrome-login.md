# WSL 环境 Chrome 登录详细步骤

## 前提条件

- WSL2 + WSLg（`DISPLAY=:0` 已设置）
- Chrome 已安装：`google-chrome --version`
- cn-scraper-mcp 已安装并接入 Hermes
- (可选) `pip install websockets` — 如需 CDP 提取知乎文章

## 完整流程（以小红书为例）

### Step 1: 启动 Chrome 并开调试端口

```bash
google-chrome --remote-debugging-port=9251 \
  --no-first-run \
  --no-default-browser-check \
  --user-data-dir=/tmp/xhs-chrome-profile \
  "https://www.xiaohongshu.com" &
```

关键参数：
- `--remote-debugging-port=9251`：CDP 调试端口，cn-scraper 默认用 9251
- `--user-data-dir=/tmp/xhs-chrome-profile`：隔离的 profile，避免与日常 Chrome 冲突
- `--no-first-run`：跳过首次运行向导

### Step 2: 验证 Chrome 就绪

```bash
ss -tlnp | grep 9251
# 应看到 LISTEN 状态
```

或直接检查 CDP：
```bash
curl -s http://127.0.0.1:9251/json/version | python3 -m json.tool | head -5
```

### Step 3: 导航到登录页

```bash
curl -s -X PUT "http://127.0.0.1:9251/json/new?https://www.xiaohongshu.com"
```

如需特定登录页：
- 小红书：`https://www.xiaohongshu.com`
- 微博：`https://weibo.com/login.php`
- 知乎：`https://www.zhihu.com/signin`

### Step 4: 用户扫码 → 收割 Cookie

等用户在 Chrome 窗口扫码/输入密码登录后：

```python
mcp__cn_scraper__harvest_cookies(platform="xiaohongshu", port=9251)
```

返回 `status: ok` + `count: N` 即成功。

### Step 5: 验证

```python
mcp__cn_scraper__xiaohongshu_search(keyword="测试", limit=1)
mcp__cn_scraper__check_cookies()  # 批量检查所有平台
mcp__cn_scraper__verify_login(platform="weibo")  # 远端验证（微博/知乎支持）
```

## 三平台一次收割（已验证）

同一 Chrome 实例连续登录三个平台，约 3-5 分钟：

```
1. 启动 Chrome（开 9251 端口，打开小红书首页）
2. 用户小红书扫码 → harvest_cookies(platform="xiaohongshu", port=9251)
3. CDP PUT 导航到微博登录页 → 用户微博扫码 → harvest_cookies(platform="weibo")
4. CDP PUT 导航到知乎登录页 → 用户知乎扫码 → harvest_cookies(platform="zhihu")
5. Chrome 保持运行（或用户自己关）
```

收割后三个平台的 `.json` 文件存于 `~/.cn-scraper-cookies/`，跨 Hermes 会话持久化。

## 故障排查

### Chrome 窗口不显示
- 确认 WSLg 运行：`echo $DISPLAY` 应输出 `:0`
- 尝试运行 `xeyes` 测试图形

### 端口被占用
```bash
kill $(ss -tlnp | grep 9251 | grep -oP 'pid=\K\d+')
```

### guided_login 也失败
- 设置环境变量 `CHROME_PATH=/usr/bin/google-chrome`
- 或用方法二（手动启动 Chrome）完全替代

### 知乎文章（zhuanlan.zhihu.com）内容提取
知乎搜索结果中 `type: article` 的文章不能用 `zhihu_answer` 工具。需用 CDP websocket：
```python
# 1. 导航到文章
curl -X PUT "http://127.0.0.1:9251/json/new?https://zhuanlan.zhihu.com/p/ARTICLE_ID"
# 2. 等待加载（sleep 4）
# 3. websocket 连接 CDP 执行 Runtime.evaluate("document.body.innerText")
```
详见 cn-scraper-mcp SKILL.md 中"知乎文章提取"章节。

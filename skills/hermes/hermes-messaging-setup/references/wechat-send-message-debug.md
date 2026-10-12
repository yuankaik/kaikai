# send_message "No home channel set" — 完整排查流程

当 `send_message` 报 "No home channel set for weixin" 但配置看起来正确时，
按以下顺序排查。这个错误至少可以掩盖 5 种不同的根因。

## 排查顺序（从最常见到最隐蔽）

### 1. iLink 频率限制（最常见）

**症状**：Gateway 日志中有 `rate limited: ret=-2 errcode=None`

**根因**：iLink 服务端 15 分钟冷却。Gateway 的 6 秒自动重试会**不断刷新冷却窗口**，
形成死循环。

**诊断**：
```bash
grep -E "rate limit|Home-channel" ~/.hermes/logs/gateway.log | tail -10
```

**修复**：
```bash
# 先停掉 Gateway 打破重试循环
hermes gateway stop

# 等待至少 20 分钟（从最后一次 rate-limit 日志时间算起）
# 然后再启动
hermes gateway start
```

**陷阱**：不要用 `hermes gateway restart` — 它只是重启 Gateway，不会等待冷却过期。
冷却窗口从每次 API 调用开始计算，Gateway 的重试会让窗口永远不到期。

### 2. WEIXIN_HOME_CHANNEL 在 config.yaml 而非 .env

**症状**：`hermes config set WEIXIN_HOME_CHANNEL ...` 成功了，但 send_message 还是找不到。

**根因**：`send_message_tool.py` 用 `os.getenv("WEIXIN_HOME_CHANNEL")` 读环境变量，
不是读 config.yaml。`hermes config set` 写入 config.yaml，对 send_message 无效。

**诊断**：
```bash
# 检查是否在 .env 中
grep HOME_CHANNEL ~/.hermes/.env
# 应该输出：WEIXIN_HOME_CHANNEL=o9cq80-...

# 检查 config.yaml（这个没用，仅作参考）
grep HOME_CHANNEL ~/.hermes/config.yaml
```

**修复**：
```bash
cat >> ~/.hermes/.env << 'EOF'
WEIXIN_HOME_CHANNEL=o9cq80-5b626txvAN2mFOucnGNUE@im.wechat
WEIXIN_HOME_CHANNEL_NAME=Home
EOF
```

### 3. systemd 未加载 .env

**症状**：.env 里已有 WEIXIN_HOME_CHANNEL，但 send_message 还是报错。
Gateway 进程里也找不到这个变量。

**根因**：systemd user service 默认不读 ~/.hermes/.env。

**诊断**：
```bash
GW_PID=$(systemctl --user show hermes-gateway.service -p MainPID --value)
cat /proc/$GW_PID/environ | tr '\0' '\n' | grep WEIXIN_HOME_CHANNEL
# 空输出 = systemd 没加载 .env
```

**修复**：
```bash
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d
cat > ~/.config/systemd/user/hermes-gateway.service.d/env.conf << 'EOF'
[Service]
EnvironmentFile=/home/adminkaikai/.hermes/.env
EOF
systemctl --user daemon-reload
hermes gateway restart
```

### 4. Agent CLI 进程缺环境变量（最隐蔽）

**症状**：Gateway 进程有 WEIXIN_HOME_CHANNEL（通过 /proc/PID/environ 验证），
Gateway 日志显示 `Sent home-channel startup notification` 成功，
但 send_message 仍然报 "No home channel set"。

**根因**：`send_message` 工具运行在 **agent CLI 进程**，不是 Gateway 进程。
CLI 进程的环境变量在启动时从 .env 读取，如果会话启动时 .env 里还没有
WEIXIN_HOME_CHANNEL，后续添加不会生效。

**诊断**：
```bash
# 在 CLI 进程内检查（此命令只在 agent 会话中有效）
echo "WEIXIN_HOME_CHANNEL: ${WEIXIN_HOME_CHANNEL:-未设置}"
```

**修复**：退出当前 CLI 会话（Ctrl+D），重新运行 `hermes`。
新会话会加载更新后的 .env。

**注意**：Gateway 本身是正常的！用户在微信上发消息能收到回复，
只是 agent 无法主动通过 send_message 发消息。

---

### 5. `platforms.weixin` 是 JSON 字符串而非 YAML 对象（send_message 找不到 token）

**症状**：send_message 报 "Weixin token missing. Configure WEIXIN_TOKEN or platforms.weixin.token."
即使：
- WEIXIN_HOME_CHANNEL 在 .env 中正确设置
- Gateway 日志显示 `Sent home-channel startup notification` 成功
- send_message --list 能看到 weixin 目标

**根因**：`hermes config set platforms.weixin '{"streaming": false}'` 创建了一个 **JSON 字符串**值，
而不是 YAML 对象。send_message 工具通过 YAML 键路径 `platforms.weixin.token` 解析 token，
无法从 JSON 字符串内部提取。

**诊断**：
```bash
# 检查 platforms.weixin 的类型
python3 -c "
import yaml
with open('$HOME/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)
pw = cfg.get('platforms', {}).get('weixin')
print(f'type: {type(pw).__name__}, value: {repr(pw)[:100]}')
"
# 输出 "type: str" = JSON 字符串（错误）
# 输出 "type: dict" = YAML 对象（正确）
```

**修复**：将 JSON 字符串改为 YAML 对象，并加入 token：
```bash
# 提取 token
TOKEN=$(python3 -c "
import json, glob
paths = glob.glob('$HOME/.hermes/weixin/accounts/*.json')
with open(paths[0]) as f:
    print(json.load(f)['token'])
")

# 写入为 YAML 对象（每个键单独设置）
hermes config set platforms.weixin.streaming false
hermes config set platforms.weixin.token "$TOKEN"

# 同时补 .env
echo "WEIXIN_TOKEN=$TOKEN" >> ~/.hermes/.env
```

**注意**：token 需要同时存在于两个地方：
1. `platforms.weixin.token`（config.yaml，供 send_message CLI 工具使用）
2. `WEIXIN_TOKEN`（.env，供 Gateway 进程使用）

---

`send_message_tool.py` 的 target 解析使用正则 `_WEIXIN_TARGET_RE`：

```python
_WEIXIN_TARGET_RE = re.compile(
    r"^\s*((?:wxid|gh|v\d+|wm|wb)_[A-Za-z0-9_-]+"
    r"|[A-Za-z0-9._-]+@chatroom|filehelper)\s*$"
)
```

iLink bot 的用户 ID 格式通常是 `o9cq80-5b626txvAN2mFOucnGNUE@im.wechat`，
不匹配任何前缀（不是 wxid_/gh_/v数字_/wm_/wb_），也不是 @chatroom 结尾，
所以 target 解析失败，chat_id 保持 None，走到 home channel 回退路径。

这意味着即使你指定了 `target="weixin:o9cq80-..."` 也无法绕过 home channel 需求。

---

## 完整修复检查清单

```bash
# 1. 确认 platforms.weixin 是 YAML 对象而非 JSON 字符串
python3 -c "import yaml; cfg=yaml.safe_load(open('$HOME/.hermes/config.yaml')); pw=cfg.get('platforms',{}).get('weixin'); print('OK: dict' if isinstance(pw,dict) and 'token' in pw else 'BAD: missing token or JSON string')"

# 2. 确认 .env 配置完整
grep -E "WEIXIN_HOME_CHANNEL|GATEWAY_ALLOW|WEIXIN_TOKEN" ~/.hermes/.env

# 3. 确认 systemd 加载 .env
GW_PID=$(systemctl --user show hermes-gateway.service -p MainPID --value)
cat /proc/$GW_PID/environ | tr '\0' '\n' | grep WEIXIN_HOME_CHANNEL

# 4. 确认无 rate limit
grep "rate limit" ~/.hermes/logs/gateway.log | tail -3

# 5. 确认 Gateway 上线通知成功
grep "Home-channel startup notification" ~/.hermes/logs/gateway.log | tail -1

# 6. 重新打开 CLI 会话（Ctrl+D 退出，重新运行 hermes）
```

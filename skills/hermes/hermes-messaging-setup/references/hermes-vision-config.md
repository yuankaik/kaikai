# Hermes Vision 配置排查指南

当 vision_analyze 返回 400"模型不存在"或图片识别不工作时，按以下顺序排查。

## 排查顺序

### 1. 检查 .env 中的 LOCAL_VISION_* 是否覆盖 config

~/.hermes/.env 中如果有以下配置，会**优先于** config.yaml 的 auxiliary.vision 设置，无视你在 config 里改了什么：

```
LOCAL_VISION_URL=http://172.24.208.1:11434
LOCAL_VISION_MODEL=minicpm-v:8b
```

修复：
```bash
nano ~/.hermes/.env
# 删除或注释这两行
```

### 2. 删除 provider_models_cache.json

~/.hermes/provider_models_cache.json 缓存了历史 provider 的模型名列表。改 config 之后，缓存里的旧模型名仍然会被发送给 API，导致 400。

修复：
```bash
rm ~/.hermes/provider_models_cache.json
hermes gateway restart
```

### 3. 确认 API key 真正写入（hermes 会自动截断）

hermes 所有工具（Python 脚本输出、yaml.dump、tool output）都会自动遮蔽 API key 为截断值（如 `sk-acw...583c`）。
`hermes config set auxiliary.vision.api_key "sk-xxx"` 写入的也是截断值，不是完整 key。

**唯一可靠写入方式**：
```bash
hermes config edit
# 在编辑器中找到 auxiliary.vision.api_key，手动粘贴完整 key
```

保存后：
```bash
hermes gateway restart
```

### 4. 确认中转站支持的模型名

不同中转站对模型的命名可能和 Anthropic 官方不同。先查中转站可用模型：

```bash
curl -s --max-time 10 https://api.aicodewith.com/v1/models \
  -H "Authorization: Bearer <YOUR_KEY>" | \
  python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] if 'claude' in m['id']]"
```

aicodewith.com 支持的名称（已验证）：
- `claude-sonnet-4-6`（非官方的 `claude-sonnet-4-20250514`）
- `claude-opus-4-6`
- `claude-haiku-4-5-20251001`

在 config 里对应配置：
```yaml
auxiliary:
  vision:
    api_key: <完整key，手动填>
    base_url: https://api.aicodewith.com/v1
    model: claude-sonnet-4-6
    provider: anthropic
```

## 完整修复流程（一次性解决）

```bash
# 1. 清 .env 中的本地 vision 配置
nano ~/.hermes/.env   # 注释掉 LOCAL_VISION_URL / LOCAL_VISION_MODEL

# 2. 删除模型缓存
rm -f ~/.hermes/provider_models_cache.json

# 3. 手动编辑 config，填入完整 key 和正确模型名
hermes config edit

# 4. 重启
hermes gateway restart
```

## 验证

```bash
# 用 curl 直接测试 vision API（绕过 hermes 工具层）
curl -s https://api.aicodewith.com/v1/chat/completions \
  -H "Authorization: Bearer <KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-6","max_tokens":50,"messages":[{"role":"user","content":"say hello"}]}' | \
  python3 -c "import json,sys; r=json.load(sys.stdin); print(r.get('choices',[{}])[0].get('message',{}).get('content','ERROR:'+str(r)))"
```

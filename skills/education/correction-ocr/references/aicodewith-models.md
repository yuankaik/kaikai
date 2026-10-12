# aicodewith.com 可用模型列表（2026-07-01 实测）

API 端点：https://api.aicodewith.com/v1/models
认证：Bearer key（key 前缀 sk-acw-）

## Claude 系列（vision 可用）

- claude-sonnet-4-6   ← 当前主模型，vision 确认可用
- claude-opus-4-6
- claude-haiku-4-5-20251001

## 其他模型（参考）

- gemini-2.5-pro / gemini-3-pro-preview / gemini-3.1-pro-preview
- gpt-5.4
- deepseek-v3.2 / deepseek-r1-0528
- kimi-k2 / kimi-k2.5 / kimi-k2-thinking
- qwen3-coder / qwen3-coder-next
- minimax-m2.1 / minimax-m2.5
- glm-4.6 / glm-4.7 / glm-5

## 不可用名称（会报 400）

- claude-sonnet-4-20250514  ← config 原值，错误！
- 任何 YYYY-MMDD 后缀格式的 Anthropic 原始模型名

## 查询命令

```bash
KEY=<你的sk-acw-key>
curl -s https://api.aicodewith.com/v1/models \
  -H "Authorization: Bearer $KEY" | \
  python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data']]"
```

## config.yaml 修复命令

```bash
sed -i 's/model: claude-sonnet-4-20250514/model: claude-sonnet-4-6/' ~/.hermes/config.yaml
hermes gateway restart
```

---
name: somnet-vision-setup
description: Configure Hermes to use Claude Sonnet as vision provider while keeping main model (DeepSeek). Vision auto-fallbacks to Sonnet for image recognition.
category: hermes
---

# Sonnet Vision Provider 配置

## 背景
DeepSeek 不支持多模态。当微信收到图片时，Hermes 自动 fallback 到 vision provider 做识别。
原配置用 Ollama minicpm-v:8b（本地免费），识别率约50%。换成 Sonnet 后准确率显著提升。

## 配置步骤

### 1. 添加 Anthropic provider
```bash
hermes config set providers.anthropic.api_key "sk-ant-..."
hermes config set providers.anthropic.base_url "https://api.anthropic.com/"
```

### 2. 切换 vision provider
```bash
hermes config set auxiliary.vision.provider anthropic
hermes config set auxiliary.vision.model claude-sonnet-4-20250514
hermes config set auxiliary.vision.base_url "https://api.anthropic.com/"
hermes config set auxiliary.vision.api_key "sk-ant-..."
```

### 3. ⚠️ 手动补全 key（必须！）
Hermes CLI 和所有工具都会自动截断/马赛克 API key。`hermes config set` 写入的值是 `sk-acw...xxx` 而非完整 key。
**唯一方式**：手动编辑配置文件。

```bash
nano ~/.hermes/config.yaml
```

找到两处 `sk-acw...583c`（截断值），替换为完整 key：
- `providers.anthropic.api_key`
- `auxiliary.vision.api_key`

### 4. 重启 Gateway
```bash
hermes gateway restart
```

### 5. 验证
发一张图片到微信，观察识别结果是否来自 Sonnet（质量明显提升）。

## 工作原理
- 主模型 DeepSeek 处理文字
- 遇到图片 → 自动调 Sonnet vision 识别
- 识别结果注入上下文 → DeepSeek 继续
- 用户无感知，不需要手动切换

## 方案B：国内视觉模型（硅基流动 Qwen3-VL）—— 免费/便宜首选

适用：无 Anthropic key、不想用 Claude 中转站、要国内直连 + 中文识别强（错题 OCR 场景比 Claude 更合适）。

配置（2026-08 实测可用）：
```yaml
auxiliary:
  vision:
    provider: openai            # 会被内部重写成 custom + base_url（_expand_direct_api_alias）
    model: Qwen/Qwen3-VL-8B-Instruct   # 8B 最快；30B-A3B 性价比；32B 最慢易超时
    base_url: https://api.siliconflow.cn/v1
    api_key: sk-xxxx            # 硅基流动 key
    timeout: 120
```

坑（实测踩过）：
1. **本机无 NVIDIA 独显（只有 Intel UHD 620 核显）→ Ollama minicpm-v:8b 纯 CPU 跑 vision 180s+ 超时，物理上不可用**。别走本地 Ollama 回退。
2. **硅基流动注册余额是 0**（不送免费额度）。新注册有少量体验额度，用完立即报 `402 account balance is insufficient`。识别一张错题图约几分钱，充 10 元够用很久。
3. **`unknown variant image_url, expected text` 是主模型 text-only（如 DeepSeek）的误导性错误（issue #31179）**，不是 vision 配置问题。auxiliary.vision 配好后该错误自动消失。判断方法：看错误是来自主 provider 还是 vision provider。
4. **key 写入必须直接改 config.yaml**（`hermes config set` 会写入马赛克截断值）。用 Python 正则替换 api_key 行最稳，别用 yaml.dump（会产生重复 key）。
5. 模型列表：`curl /v1/models` 带 `VL` 的才是视觉模型。32B 首 token 慢易超时，错题识别用 8B 足够（约 30-40s/张）。

验证链路：
```bash
# 1. 查余额
curl -s https://api.siliconflow.cn/v1/user/info -H "Authorization: Bearer $KEY"
# 2. 直接测模型（OpenAI 兼容，image_url 传 base64 data URL）
# 3. 再测 Hermes 完整链路：vision_analyze 传本地图片路径
```

## 踩坑记录

### ⚠️ 配置前先验证中转站支持 Claude！
**不是所有中转站都支持 Claude**。配置前先去中转站官网查看模型列表。
- aicodewith.com → **不支持 Claude**，只有国产模型（DeepSeek/Kimi/Qwen/GLM/MiniMax）
- 如果中转站没有 Claude，这条方案走不通，需要换中转站或保持本地 Ollama

### Key 自动马赛克
Hermes 安全机制会拦截所有上下文中的 API key（包括 Python 脚本、yaml.dump、tool output）。
`hermes config set` 写入的也是截断值。**唯一方式**：手动 `nano ~/.hermes/config.yaml` 编辑。

### YAML 损坏
不要用 Python `yaml.dump` 直接写 config.yaml——会产生重复 key（如两个 `vision:`）导致配置混乱。
如已损坏：`hermes config set vision null` 清理重复 key，然后 `hermes gateway restart`。

### 模型名要匹配中转站
中转站支持的模型名可能和官方不同。先查中转站模型页面确认准确名称。
参考：`references/aicodewith-models.md`（已确认不支持 Claude）

## 原配置（回退用）
```yaml
auxiliary:
  vision:
    provider: openai
    model: minicpm-v:8b
    base_url: http://172.24.208.1:11434/v1
    api_key: ollama
```

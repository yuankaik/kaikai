---
name: claude-vision-relay-selection
description: 选型与配置 Claude vision 中转站（国内访问 Anthropic 的 API 中转）。当 Hermes 照片识别报错、需要找支持 Claude vision 的中转站、或拿到中转站 key 后配置 auxiliary.vision 时使用。是 somnet-vision-setup（手动创建、不可编辑）的补充，补上候选中转站清单与实测报错。
category: hermes
---

# Claude Vision 中转站选型与配置

## 触发条件
- 照片识别报错（如 `unknown variant image_url, expected text`）
- 用户要"找一个支持 Claude vision 的中转站"
- 拿到中转站 key 后，要把 Hermes 的 `auxiliary.vision` 配到新端点

## 背景
Hermes 主模型（DeepSeek）是纯文本，照片识别走独立的 `auxiliary.vision`（anthropic provider）。
国内无法直连 Anthropic 官方，必须走中转站。但很多中转站只做国产模型、不支持 Claude——
配错 base_url 就会让照片识别**静默失效**，识别图片时报 `unknown variant image_url, expected text`（HTTP 400）。

## 诊断：照片识别为什么卡住（2026-08-14 实测）

「拍照片 → Hermes 看懂」靠 auxiliary.vision，两条路都可能堵死，先各查一次再下结论：

1. **云端 vision 配错了中转站** —— `grep -A6 "vision:" ~/.hermes/config.yaml` 看 `base_url`。指向不支持 Claude 的站（如 aicodewith.com，只有 DeepSeek/Kimi/Qwen 国产模型）→ 识别请求静默失败。
2. **本地 Ollama 回退在本机不可行** —— kai哥这台 ThinkPad 只有 Intel UHD 620 核显、**无 NVIDIA 独显**（查：`Get-CimInstance Win32_VideoController`）。Ollama `minicpm-v:8b`（7.6B，Q4_0）纯 CPU 跑 vision，一张错题图实测 **180 秒超时**。**别建议退回 Ollama，物理上跑不动。**

结论：本地免费方案已封死。云端有两条路，**优先国内视觉模型（硅基流动，免费/便宜 + 国内直连 + 中文识别强），Claude 中转站作备选**。

### ⚠️ `unknown variant image_url, expected text` 的真正来源
这个 400 错误**不是 vision 配置错**，而是**主模型（DeepSeek 等 text-only provider）不支持图片输入**时的报错（Hermes 代码 `agent/auxiliary_client.py` 注释的 issue #31179）。当 `auxiliary.vision` 配置没被正确解析/生效、Hermes 回退到主模型发图时就会出现。配置正确切到国内视觉模型（provider=openai + 硅基流动）后**自动消失**——所以别被这个错误误导去反复调 vision 配置，先确认 auxiliary.vision 是否真的生效了。

### 抓包确认请求格式（拿不准时用）
不确定请求是否真的发对时，写一个本地 HTTP 代理（记录 body 结构 + 转发上游），把 base_url 临时指向它，触发 vision_analyze 看实际发出的 content。正确格式应为 part types = `['text', 'image_url']`，image_url 是 dict 含 `{"url": "data:image/jpeg;base64,..."}`，model 是 Qwen3-VL 全名。实测 Hermes 发的就是标准 OpenAI 格式——格式对但余额不足（402）才是真问题。诊断顺序：先查余额（402）→ 再抓包确认格式（排除配置没生效）→ 最后才怀疑模型/中转站。

## 方案 A：国内视觉模型（硅基流动 Qwen3-VL，推荐优先）

国内视觉模型用 OpenAI 兼容格式接入，比 Claude 中转站更省、更快、中文识别更强。2026-08-14 实测验证。

**硅基流动 SiliconFlow（siliconflow.cn）**
- base_url: `https://api.siliconflow.cn/v1`（OpenAI 兼容）
- 视觉模型（实测）：
  - `Qwen/Qwen3-VL-8B-Instruct` —— 快，识别一张错题图约 40s，中文手写 + 红笔批改都能读对，**推荐**
  - `Qwen/Qwen3-VL-30B-A3B-Instruct` —— MoE 性价比
  - `Qwen/Qwen3-VL-32B-Instruct` —— 最强但慢，单图实测 120s 超时，不推荐
- key 格式：`sk-` + 48 字符。⚠️ 注册**不送免费额度**——实测新 key `balance="0"`，只有极少量体验额度，用完调用报「402 余额不足」（`{"code":30001,"message":"Sorry, your account balance is insufficient"}`）。需充值（最低几块钱），一张错题图约几厘钱，10 元够用很久。查余额：`curl -s https://api.siliconflow.cn/v1/user/info -H "Authorization: Bearer $KEY"` 看 `balance` 字段。**先查余额再下结论，402 不等于配置错。**
- 配置 provider 用 **`openai`**（不是 anthropic）：
```yaml
auxiliary:
  vision:
    provider: openai
    model: Qwen/Qwen3-VL-8B-Instruct
    base_url: https://api.siliconflow.cn/v1
    api_key: <硅基流动 key>
```
- 验证 key：`curl -s https://api.siliconflow.cn/v1/models -H "Authorization: Bearer $KEY"` 能列出含 VL 的模型即有效
- 备选国内平台：智谱 GLM（glm-4v-flash 有免费档）、阿里百炼 DashScope（qwen-vl-plus，新用户送额度），均 OpenAI 兼容

## 方案 B：Claude 中转站（备选）

## 选型方法（可复用）
1. GitHub 搜中转站聚合/横评仓库（客观来源，比搜索引擎 SEO 靠谱）：
   - `peter123023/awesome-claude-api`（中转资源列表，README.MD 注意大写后缀）
   - `LMU-AI/claude-api-relay-review`（8 家中转站横评）
   - 搜索词：`claude 中转` / `claude api relay`
2. 交叉验证：至少两个独立来源都推荐才列入候选
3. 关键维度：**内部汇率**（不是美元标价）、是否支持 vision/多模态、支付方式、服务器位置（延迟）

## 候选中转站（2026-08 调研，两个来源交叉验证）
| 平台 | 站点 | 汇率/价 | 支付 | 特征 |
|------|------|--------|------|------|
| 灵眸AI | clawapi.fulitimes.com | ¥2.4/$（约官方3折） | 微信 | 横评⭐⭐⭐⭐⭐；国内直连延迟最低；标注模型版本不怕验真 |
| AIHubMix | aihubmix.com | 官方同价 ¥7.1/$ | 支付宝/微信 | 两来源都收录；明确标注"多模态/视频生成"；文档好 |
| OfoxAI | ofox.ai | 按量付费 | 微信/支付宝 | 香港直连免代理 100-300ms；原生 Anthropic SDK 协议 |
| CoderPlan | coderplan.ai | 约1.2折（最便宜） | 支付宝/微信 | 支持 Sonnet 4.6；缓存省钱 |

其余候选（神马中转 api.whatai.cc、laozhang.ai、poloapi.com、PackyAPI 逆向、OpenRouter 需代理）
及详细横评数据见 `references/relay-candidates.md`。

## 风险（务必转告用户）
1. **别大额充值**（¥20-50 够识别照片用很久），行业跑路快
2. **数据安全**：错题照片会经过中转站服务器，别传敏感材料
3. **先验证再信**：拿 key 先实测一张图片；模型掺假常见，可用 `iffs.cn`（Claude照妖镜）验真

## 配置步骤（拿到 key 后）
- Claude 中转站：provider 用 `anthropic`，model 按中转站实际模型名（如 `claude-sonnet-4-6`）
- 国内模型（硅基流动等）：provider 用 `openai`，model 如 `Qwen/Qwen3-VL-8B-Instruct`（见方案 A）

```bash
hermes config set auxiliary.vision.provider openai   # 或 anthropic
hermes config set auxiliary.vision.base_url "https://api.siliconflow.cn/v1"
hermes config set auxiliary.vision.model "Qwen/Qwen3-VL-8B-Instruct"
hermes gateway restart
# 实测：vision_analyze 识别一张图片，确认返回正常而非报错
```

### ⚠️ 写 key 的可靠方法（execute_code 正则替换，优于手动 nano）
Hermes 只马赛克**输出/回显**里的 key（tool result、grep 回显），**不马赛克** write_file/patch/execute_code 的**输入参数**。所以可直接用 execute_code 读文件→正则替换 api_key 行→写回，完整 key 能正确落盘（读回验证 len(key) 正确即成功）。关键用正则定位、不依赖旧 key 的精确值（旧 key 常已被马赛克成截断值）：

```python
import re
path = "/home/adminkaikai/.hermes/config.yaml"
content = open(path, encoding="utf-8").read()
# 匹配 (换行 缩进 api_key: ) 任意非换行，替换成新 key
content = re.sub(r"(\n    api_key: )[^\n]*", r"\1" + NEW_KEY, content, count=1)
open(path, "w", encoding="utf-8").write(content)
```

（`hermes config set ...api_key` 写入的是截断值 `sk-xxx...xxx`，不可用；别用 Python yaml.dump 重写整个文件——会损坏/重复 key。）

## 注意
- 与 `somnet-vision-setup` 重叠：后者已覆盖"配置步骤 + aicodewith 不支持 Claude 的坑"，但它是手动创建（created_by=None）、自主策展不可编辑，故本技能补上候选中转站清单与实测报错。
- 中转站信息时效性强（价格/汇率/存活状态变化快），使用前以官网实时公示为准。

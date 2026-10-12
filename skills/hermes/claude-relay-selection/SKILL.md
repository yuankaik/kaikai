---
name: claude-relay-selection
description: 为 Hermes 的 Claude vision / Claude API 选一个支持 Claude 的中转站——诊断 vision 配置坏了的表现、候选中转站清单（价格/汇率/风险）、验证工具。
---

# Claude API 中转站选型

给 Hermes 的 `auxiliary.vision`（或任何 Claude API 用途）选一个**真正支持 Claude（含多模态/图片）**的中转站。互补 sonnet-vision-setup（那个技能讲怎么配，但其中的中转站调研无法更新；本技能承载候选清单与诊断）。

## 诊断：vision 配置坏了的表现

照片识别（vision_analyze）报错 `unknown variant image_url, expected text`（HTTP 400）→ `auxiliary.vision.base_url` 指向的中转站**不接受图片输入 / 不支持 Claude 多模态**。快速排查：

1. 看 `auxiliary.vision.base_url` 是否指向已知不支持 Claude 的中转站（如 aicodewith.com）
2. 用一张真实图片调 vision_analyze 实测，报上面那个错 = 端点坏了，不是图片问题、不是格式问题
3. 换下面的候选中转站，拿到 key 后重新配置 + 实测

⚠️ 曾发生：vision 被配成 aicodewith 的 base_url + claude-sonnet-4-6 模型名，但 aicodewith 根本没这个模型、也不支持图片，照片识别静默失效数周。配置前务必确认中转站模型列表里真有 Claude。

## 候选中转站（2026-08-13 调研，两个独立来源交叉核对）

数据来源：LMU-AI/claude-api-relay-review（8 家实测横评，2026-04）+ peter123023/awesome-claude-api（GitHub 列表，2026-05-01）。

| 平台 | 站点 | 内部汇率 | 要点 |
|------|------|---------|------|
| 灵眸AI | clawapi.fulitimes.com | ¥2.4/$（官方 3 折） | 横评第一；国内直连延迟最低；微信支付；明确标模型版本（防掺假） |
| AIHubMix | aihubmix.com | 官方同价 ¥7.1/$ | 两来源都收录；**明确标注多模态**；文档好客服快；支持 Prompt Caching |
| 神马中转API | api.whatai.cc | ¥2/$ | 650+ 模型聚合；境外服务器延迟视地区 |
| laozhang.ai | laozhang.ai | 官方同价 | 知名度最高；注册送 $0.5；支付宝/微信 |
| OfoxAI | ofox.ai | 按量 | 香港直连免代理；原生 Anthropic 协议；微信/支付宝 |
| CoderPlan | coderplan.ai | 约 1.2 折 | 最便宜；国内支付；支持 Sonnet 4.6 |
| poloapi | poloapi.com | 官方 93 折 | 正规转发、非逆向、价格透明 |

## 避坑

- **逆向接口平台**（如 PackyAPI）：低价来自反代 Cursor/Kiro 等，有隐性提示词注入、无 Prompt Caching、Anthropic 一更新就失效 → 生产/高频场景别用
- **apiyi**：Cache 写入贵（¥105/M）、超 200K 上下文输入翻倍
- **OpenRouter**：国内 IP 直连用不了 Claude，需自备代理 + 国际信用卡
- **汇率陷阱**：对比平台必须看「内部汇率」而非美元标价（¥2.4/$ 的平台充 ¥100 能用的是 ¥7/$ 平台的近 3 倍）

## 验证工具（选完平台后先验证再信）

- Claude照妖镜 iffs.cn：7 维测试验证是否满血官方 Claude，评分 ≥70 满血
- CCTest cctest.ai：11 轮专业测试 + Token 消费合理性检测

## 安全原则（横评作者忠告）

1. 别大额充值，用多少充多少（这个行业跑路快）
2. 看内部汇率而非美元标价
3. 上线前用测试集/照妖镜验证模型真实性
4. 数据安全：图片/文件会经过中转站服务器，敏感材料别传

## 配置步骤（拿到 key 后）

```bash
hermes config set auxiliary.vision.provider anthropic
hermes config set auxiliary.vision.model <中转站实际模型名，如 claude-sonnet-4-6>
hermes config set auxiliary.vision.base_url <中转站 base_url>
hermes config set auxiliary.vision.api_key <key>
hermes gateway restart
```

⚠️ Hermes 会自动马赛克 key，`hermes config set` 可能写入截断值——必要时手动 `nano ~/.hermes/config.yaml` 补全，再重启 gateway。最后用一张真实图片实测。

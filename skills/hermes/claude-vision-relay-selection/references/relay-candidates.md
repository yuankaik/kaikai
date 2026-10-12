# Claude API 中转站完整候选清单（2026-08-13 调研）

## 来源
- A：`LMU-AI/claude-api-relay-review`（8 家中转站横评，2026-04，Claude Opus 4.7 实测，Claude Code 重度用户 1 周实测）
- B：`peter123023/awesome-claude-api`（中转资源列表，2026-05 更新，last-updated badge）

## 8 家横评结果（来源A，按加权均价¥/M 排序）

| 平台 | 站点 | 汇率¥/$ | 加权均价¥/M | 支持Claude Code | 定位 |
|------|------|--------|-----------|---------------|------|
| 灵眸AI | clawapi.fulitimes.com | 2.4 | 45.60 | ✅ | 主用首选，国内直连 |
| 神马中转 | api.whatai.cc | 2 | 76.00 | ❌缓存不详 | 650+模型聚合 |
| PackyAPI | packyapi.com | 1 | 114.00 | ✅ | 逆向接口，最便宜但风险高 |
| poloapi | poloapi.com | 7 | 124.04 | ✅ | 官方93折正规转发 |
| laozhang.ai | laozhang.ai | 7 | 133.00 | ❌缓存不详 | 知名度最高，注册送$0.5 |
| apiyi | api.apiyi.com | 7 | 133.00 | ❌ | 坑：缓存写入¥105/M、200K上下文翻倍 |
| AIHubMix | aihubmix.com | 7.1 | 134.90 | ✅ | 明确标注多模态，文档好 |
| OpenRouter | openrouter.ai | 7.27 | 138.13 | ✅(需代理) | 国内IP限制Claude，需美元卡 |

## 横评作者的核心结论
- 对比平台必须看**内部汇率换算后的 ¥/M**，不是美元标价（汇率2.4 vs 7，同样充¥100可用token差3倍）
- 便宜平台（PackyAPI）低价来自**逆向接口**：注入Cursor/Kiro等客户端提示词、无Prompt Caching、Anthropic一更新就中断
- **模型掺假**最常见：有平台把Sonnet换成Haiku或用国产模型冒充，数学题准确率可降40%。自测：问模型身份/训练截止日期、跑标准答案数学题
- 核心原则：不大量充值、看内部汇率、上线前验证模型真实性

## 来源B 补充候选（awesome-claude-api 列表）
- ZenMux（zenmux.ai）：仅官方/授权渠道原版模型，异常赔付
- EasyRouter（easyrouter.io）：傅盛团队，DeepSeek-V4-Pro 2.5折
- B.AI（b.ai）：孙宇晨团队，匿名支付
- FerryAPI（ferryapi.io）：$5体验金，9大厂商聚合
- Unity2.Ai（unity2.ai）、AIGoCode（aigocode.com）、YesCode（co.yes.vg）、AICoding（aicoding.sh）、IKunCode（api.ikuncode.cc）

## 验真工具
- Claude照妖镜 iffs.cn：7维度测满血模型，评分≥70=满血，≥90=官方超级满血
- CCTest cctest.ai：11轮检测，含Token倍率异常检测

## 失效风险
中转站行业跑路快、价格/汇率/存活状态变化快。本清单是 2026-08 快照，使用前以官网实时公示为准，且务必小额充值、先实测再信。

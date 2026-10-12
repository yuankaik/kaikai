# 办公 / 搜索 / LLM Wiki 三方向技能调研快照（2026-10）

用户要求"升级技能 + 找 GitHub 高星办公类/搜索类/LLM Wiki 类"。本次调研结论，
避免下次重复挖掘。

## 结论先行

- **LLM Wiki 方向：本机已有技能强于 GitHub 上找到的所有候选，无需引入。**
  本机 `research/llm-wiki` v2.1.0 具备：三层架构（raw / 实体概念页 / SCHEMA）、
  sha256 漂移检测、11 项 lint、Obsidian headless 同步、provenance 标记。
  对比 Astro-Han/karpathy-llm-wiki（2.4K⭐，14254 字节，仅 raw/+wiki/+index/log 三层，
  无 sha256、lint 项少）——本机更完备。**任何"LLM Wiki"类迁移请求先看本机，别急着重装。**
- **办公方向：本机 `office-productivity` 有结构性缺陷（见下），值得补强，而非新增。**
- **搜索方向：本机已有 firecrawl / crawlee(crawl4ai) / searxng / duckduckgo / cn-platform-full-stack 等，
  覆盖度已高；GitHub 高星多为 MCP server 形态（需接入），非纯技能。**

## 办公类候选（GitHub）

| 仓库 | 星 | 形态 | 评价 |
|------|----|------|------|
| tfriedel/claude-office-skills | 837 | 4 个 SKILL.md (docx/pdf/pptx/xlsx) | ✅ 质量高，金融建模色标规范、零公式错误等硬约束值得吸收 |
| haris-musa/excel-mcp-server | 4230 | MCP server | ⚡ 需接入 MCP |
| genspark-ai/genoffice | 9326 | AI Office 套件 | ❌ 完整应用，非技能 |
| officecli/officecli | 107 | CLI | ⚡ 可包装 |

**claude-office-skills 的 xlsx SKILL.md 精华（可直接吸收）**：
- 金融模型色标：蓝=硬编码输入 / 黑=公式 / 绿=同表引用 / 红=外部链接 / 黄底=待更新假设
- 数字格式：年份存文本、货币 `$#,##0`、零显示 `-`、百分比 0.0%、倍数 0.0x、负数用括号
- 公式铁律：假设放独立单元格用引用而非硬编码、交付前零公式错误（#REF!/#DIV/0! 等）

## 搜索/研究类候选

| 仓库 | 星 | 评价 |
|------|----|------|
| firecrawl/firecrawl-mcp-server | 7583 | 本机已有 firecrawl 技能（HTTP API 版） |
| exa-labs/exa-mcp-server | 5108 | ⚡ MCP |
| Weizhena/Deep-Research-skills | 2332 | 📦 4 语言×5 阶段流水线（research→deep→report），中英双语，含 outline.yaml/fields.yaml 模式 |
| Leonxlnx/unlazy | 3899 | 反偷懒 skill，Depth Tree 方法 |
| rohunvora/x-research-skill | 1243 | X/Twitter 调研 |

Deep-Research-skills 的价值点：**outline.yaml（items+execution 配置）+ fields.yaml（字段定义）
+ 每 item 独立 agent 出结构化 JSON + 验证脚本 + 汇总 report.md** 的流水线模式，
适合"批量调研 N 个对象出结构化对比表"的任务，可借鉴其 outline/fields 分离设计。

## LLM Wiki 类候选（均不如本机）

AgriciDaniel/claude-obsidian 15.5K⭐ / SamurAIGPT/llm-wiki-agent 3.6K /
Astro-Han/karpathy-llm-wiki 2.5K / sdyckjq-lab/llm-wiki-skill 2.5K /
atomicstrata/llm-wiki-compiler 2.2K / NicholasSpisak/second-brain 738

## 本机技能现状（510 个）

类别分布 Top：gh-edu 179 / gstack 58 / misc 47 / mlops 38 / creative 26 /
research 19 / devops 17 / productivity 17 / web-development 14。

**发现的缺陷**：`misc/agents-office-productivity` 只引用 `docx-official`/`xlsx-official`/
`pptx-official`/`libreoffice-*` 等技能名，但**这些技能本体在本机不存在**（510 个技能里只有
productivity/powerpoint、misc/xlsx 等）。该技能是"工作流骨架"却指向空引用——用户若要办公
能力，实际落点应是 misc/xlsx、productivity/powerpoint、finance/excel-author 等真实存在的技能。

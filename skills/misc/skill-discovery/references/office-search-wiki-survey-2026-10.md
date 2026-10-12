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

## 本机技能现状（510 → 519 个）

类别分布 Top：gh-edu 179 / gstack 58 / misc 47 / mlops 38 / creative 26 /
research 19 / devops 17 / productivity 17 / web-development 14。

### 本次实际落地（2026-10，已完成）

用户选 C（A+B 都装），已落地并推送到 yuankaik/kaikai：

**A. 办公包 —— office/ 分类，126 文件**（源自 tfriedel/claude-office-skills，Anthropic 官方级）
- `office/docx-authoring` — Word：跟踪修订/批注/格式保留 + OOXML schema + python-docx 脚本
- `office/xlsx-authoring` — Excel：公式/财务建模规范 + recalc.py 重算脚本
- `office/pptx-authoring` — PPT：版式/备注/html2pptx + 缩略图/inventory/rearrange 脚本
- `office/pdf-authoring` — PDF：提取/合并/拆分/表单填写 + pypdf 表单脚本

**B. 深度研究包 —— research/ 分类，6 文件**（源自 Weizhena/Deep-Research-skills 中文版）
- `research/deep-research-init` — /research <topic> → outline.yaml + fields.yaml
- `research/deep-research-run` — /research-deep 多 agent 并行调研 → 结构化 JSON
- `research/deep-research-report` — /research-report 汇总 markdown 报告
- `research/deep-research-add-items` / `deep-research-add-fields` — 补充对象/字段

**已修复**：`misc/agents-office-productivity` 的 7 处死链（`docx-official` 等不存在的技能名）
已指向真实存在的 `office/docx-authoring` 等；Deep-Research 内 `~/.claude/...` 路径改为本机路径。

**已装依赖**：python-pptx / pypdf / openpyxl / python-docx / markitdown
（PEP 668 环境装时加 `--break-system-packages`）。

**LLM Wiki 方向：确认不引入**（本机 llm-wiki v2.1.0 更完备，见上）。

### 遗留

- `misc/agents-office-productivity` 还引用 `libreoffice-*` 系列技能名，这些本体仍未落地；
  用户若要 LibreOffice 能力需另装或改指向。
- 未评估：TapXWorld/ChinaTextbook（82K⭐，小初高 PDF 教材）、microsoft/markitdown（189K⭐）——
  对教育需求可能有用，下次可单独看。

## 迁移操作要点

这次踩到的三个坑（name 冲突 / `~/.claude` 硬编码路径 / 路由壳死链）及修复脚本，
已写入本技能 SKILL.md 的 §3.5；落地后四步验证见 §3.6。**下次整包迁移直接照做，别再踩一遍。**


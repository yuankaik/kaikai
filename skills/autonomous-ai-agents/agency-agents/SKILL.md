---
name: agency-agents
description: AI 梦之队——232 个专业 AI Agent 人格库 (113K⭐)。16 个部门：工程、设计、营销、销售、安全、游戏、金融等。每个 Agent 含人格、工作流、代码示例。可直接转为 Hermes 技能。
source: https://github.com/msitarzewski/agency-agents
---

# The Agency — AI 梦之队

232 个精心打磨的 AI Agent 人格，16 个部门。不是可执行程序，而是**系统提示词/人格定义库**，可转为 Hermes 技能使用。

## 快速开始

```bash
git clone https://github.com/msitarzewski/agency-agents.git
cd agency-agents

# 浏览所有 Agent
ls engineering/ design/ marketing/ sales/ security/
```

## 16 个部门速查

| 部门 | 核心 Agent | 场景 |
|------|-----------|------|
| **工程** | 前端/后端/AI 工程师、DevOps、SRE、代码审查 | 软件开发、架构 |
| **设计** | UI/UX 设计师、品牌守护者、趣味注入器 | 界面设计、品牌 |
| **营销** | 增长黑客、SEO、Reddit 社区、TikTok | 用户增长 |
| **销售** | 外呼策略、交易策略、管道分析 | 销售漏斗 |
| **产品** | 产品经理、趋势研究员、反馈分析 | 产品规划 |
| **项目** | 制作人、Jira 管家、高级 PM | 多项目管理 |
| **测试** | 证据收集、性能测试、无障碍审计 | QA 认证 |
| **安全** | 安全架构、渗透测试、合规审计 | 安全评估 |
| **游戏** | 游戏设计师、Unity/Unreal/Godot 工程师 | 游戏开发 |
| **金融** | 记账、财务分析、FP&A、税务 | 财务建模 |
| **学术** | 人类学家、历史学家、心理学家 | 世界观构建 |
| **空间计算** | XR 架构师、visionOS 工程师 | AR/VR 开发 |
| **GIS** | 空间分析、制图、无人机测绘 | 地理信息 |
| **支持** | 客服回复、分析报告、法务合规 | 客户支持 |
| **付费媒体** | PPC 策略、搜索分析、追踪 | 广告优化 |
| **专属** | Agent 编排器、MCP 构建器、文化智能 | 多 Agent 协调 |

## Agent 文件结构

每个 Agent 都是 YAML frontmatter + Markdown：

```yaml
---
name: Frontend Developer
description: React/Vue/Angular 专家
vibe: 像素级精确，可访问性优先
---
```

含 10 个标准章节：身份 → 使命 → 规则 → 交付物 → 工作流 → 模板 → 沟通风格 → 记忆 → 指标 → 高级能力

## 多工具支持

自带转换脚本，支持 12+ AI 工具：
- **Claude Code** → `~/.claude/agents/`
- **Copilot** → `~/.github/agents/`
- **Cursor** → `.cursor/rules/`
- **Codex** → `~/.codex/agents/`
- **Gemini CLI** → `SKILL.md` 格式

## 多 Agent 编排示例

`examples/` 目录包含完整工作流：
- `workflow-startup-mvp.md` — 工程+营销+测试协作推 MVP
- `workflow-landing-page.md` — 工程+设计+营销建落地页
- `nexus-spatial-discovery.md` — 8 部门跨职能蓝图

## 转为 Hermes 技能

```bash
# 运行转换脚本（生成 SKILL.md）
./scripts/convert.sh --tool antigravity

# 复制到 Hermes
cp -r ~/.gemini/antigravity/skills/agency-* ~/.hermes/skills/misc/
```

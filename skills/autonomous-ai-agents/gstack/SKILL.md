---
name: gstack
description: GStack — YC CEO Garry Tan 的虚拟工程团队 (110K⭐)。23 个 AI 专家角色（CEO→架构→设计→开发→QA→运维）+ 8 个超级工具。原生支持 Hermes。Think→Plan→Build→Review→Test→Ship→Reflect 完整冲刺流程。
source: https://github.com/garrytan/gstack
---

# GStack — 你的虚拟工程团队

Garry Tan（Y Combinator CEO）的 Claude Code 配置，23 个 AI 专家 + 8 个超级工具。**原生支持 Hermes！**

## 安装（Hermes）

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack
cd ~/.hermes/skills/gstack && ./setup --host hermes
```

## 23 个专家 — 完整冲刺流程

### 💭 Think（思考）
| 工具 | 角色 | 做什么 |
|------|------|--------|
| `/office-hours` | YC 办公时间 | **起点**。6 个追问重构你的产品思路 |
| `/spec` | 规格作者 | 模糊想法→精确可执行规格 |

### 📋 Plan（规划）
| 工具 | 角色 | 做什么 |
|------|------|--------|
| `/plan-ceo-review` | CEO 审查 | 找到 10 星产品藏在需求里 |
| `/plan-eng-review` | 工程经理 | 架构、数据流、时序图、安全审查 |
| `/plan-design-review` | 设计审查 | 7 维度交互式设计审计 |
| `/autoplan` | 自动规划 | 一键跑完 CEO→设计→工程→DX 审查 |

### 🎨 Design（设计）
| 工具 | 角色 | 做什么 |
|------|------|--------|
| `/design-shotgun` | 设计探索 | 生成 4-6 个方案，浏览器对比 |
| `/design-html` | 设计工程 | 方案→生产级 HTML/CSS |

### 🔨 Build & Review（构建审查）
| 工具 | 角色 | 做什么 |
|------|------|--------|
| `/review` | 高级工程师 | 找出能过 CI 但生产会炸的 bug |
| `/investigate` | 调试器 | 系统化根因分析 |

### 🧪 Test（测试）
| 工具 | 角色 | 做什么 |
|------|------|--------|
| `/qa` | QA 主管 | 浏览器真实测试→修 bug→回归测试 |
| `/qa-only` | QA 报告 | 只报 bug，不改代码 |
| `/browse` | 浏览器引擎 | 真实 Chromium 浏览器操作 |

### 🚀 Ship（发布）
| 工具 | 角色 | 做什么 |
|------|------|--------|
| `/ship` | 发布工程 | 跑测试→审查覆盖率→PR |
| `/land-and-deploy` | 部署 | PR→合并→等 CI→验证生产 |
| `/canary` | SRE | 发布后监控循环 |
| `/benchmark` | 性能 | Core Web Vitals 基准测试 |

### 📝 Document & Reflect（文档复盘）
| 工具 | 角色 | 做什么 |
|------|------|--------|
| `/document-release` | 技术写作 | 更新所有项目文档 |
| `/document-generate` | 文档生成 | Diataxis 框架生成缺失文档 |
| `/retro` | 回顾 | 每周团队回顾 |

## 8 个超级工具
| `/cso` | 安全审计 | OWASP + STRIDE 威胁模型 |
| `/learn` | 记忆 | 跨会话学习管理 |
| `/careful` | 安全护栏 | 拦截危险命令 |
| `/freeze` | 编辑锁 | 限制修改范围 |
| `/pair-agent` | 多 Agent | 与其他 AI Agent 共享浏览器 |

## Hermes 专属适配

gstack 自动处理这些转换：
- `Bash tool` → `terminal tool`
- `Write/Edit tool` → `patch tool`
- `Agent tool` → `delegate_task`
- `CLAUDE.md` → `AGENTS.md`
- Codex 相关功能自动跳过

## 5 分钟快速流程
```
1. /office-hours      → 描述你要做什么
2. /plan-ceo-review   → 审查产品方向
3. /review            → 审查已有代码
4. /qa                → 在真实浏览器测试
```

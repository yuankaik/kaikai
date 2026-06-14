---
name: anthropic-skills-catalog
description: Anthropic 官方技能库目录——17 个 Claude 技能 (150K⭐)。涵盖创意设计、开发技术、企业沟通、文档处理四大类。
source: https://github.com/anthropics/skills
---

# Anthropic 官方技能库

Anthropic 为 Claude 打造的技能集合。每个技能是独立的文件夹，包含 `SKILL.md` 指令和元数据。

## 完整技能清单

### 🎨 创意与设计
| 技能 | 用途 |
|------|------|
| `algorithmic-art` | 算法生成艺术 (p5.js) |
| `canvas-design` | Canvas 设计：海报、艺术作品 |
| `frontend-design` | 前端设计：落地页、仪表板 |
| `theme-factory` | 主题工厂：为幻灯片/文档/网页生成主题 |
| `slack-gif-creator` | Slack GIF 创作器 |

### 💻 开发与技术
| 技能 | 用途 |
|------|------|
| `mcp-builder` | MCP 服务器构建指南 ✅ 已迁移 |
| `webapp-testing` | Web 应用测试 (Playwright) |
| `web-artifacts-builder` | 复杂 Web Artifacts 构建 |
| `claude-api` | Claude API 使用指南 |

### 🏢 企业与沟通
| 技能 | 用途 |
|------|------|
| `brand-guidelines` | 品牌指南：应用品牌色彩和字体 |
| `internal-comms` | 内部沟通：状态报告、公告、FAQ |
| `doc-coauthoring` | 文档协作：结构化文档工作流 |

### 📄 文档处理（源码可见，非开源）
| 技能 | 用途 |
|------|------|
| `docx` | Word 文档创建和编辑 |
| `pdf` | PDF 处理和表单填写 |
| `pptx` | PowerPoint 演示文稿 |
| `xlsx` | Excel 电子表格 |

### 🔧 工具
| 技能 | 用途 |
|------|------|
| `skill-creator` | 创建新技能的指南 |

## 如何安装更多

```bash
# 克隆完整仓库
git clone https://github.com/anthropics/skills /tmp/anthropics-skills

# 浏览所有技能
ls /tmp/anthropics-skills/skills/

# 查看某个技能
cat /tmp/anthropics-skills/skills/webapp-testing/SKILL.md
```

## Claude Code 中使用

```bash
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

## 授权

大部分技能 Apache 2.0 开源。`docx/pdf/pptx/xlsx` 源码可见但非开源。

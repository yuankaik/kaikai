---
name: mcp-builder
description: 创建高质量 MCP (Model Context Protocol) 服务器的完整指南——Python (FastMCP) 或 TypeScript。来自 Anthropic 官方技能库 (150K⭐)。
source: https://github.com/anthropics/skills
---

# MCP Server 开发指南

创建让 LLM 能通过精心设计的工具与外部服务交互的 MCP 服务器。

## 四个阶段

### Phase 1: 研究和规划

**API 覆盖 vs 工作流工具：**
- 优先全面 API 覆盖，让 Agent 灵活组合操作
- 工具命名：用一致前缀（`github_create_issue`、`github_list_repos`）
- 上下文管理：返回聚焦的相关数据，支持过滤/分页
- 错误消息：给出具体的解决建议和下一步

**推荐技术栈：**
- TypeScript（SDK 支持好，兼容性强）或 Python（FastMCP）
- 远程：Streamable HTTP + 无状态 JSON
- 本地：stdio

### Phase 2: 实现

**项目结构：**
- TypeScript: `package.json`, `tsconfig.json`
- Python: 模块化组织，FastMCP 装饰器

**核心基础设施：**
- API 客户端 + 认证
- 错误处理辅助
- 响应格式化（JSON/Markdown）
- 分页支持

**每个工具需要：**
```python
# Python (FastMCP)
@mcp.tool()
async def my_tool(param: str) -> str:
    """清晰的工具描述"""
    # 异步 I/O
    # 正确的错误处理
    # 返回结构化数据
```

**工具注解：**
- `readOnlyHint`: 只读操作
- `destructiveHint`: 破坏性操作
- `idempotentHint`: 幂等操作

### Phase 3: 审查和测试

- TypeScript: `npm run build` 验证编译
- Python: `python -m py_compile server.py`
- 测试：`npx @modelcontextprotocol/inspector`

### Phase 4: 创建评估

创建 10 个评估问题，要求：
- 独立、只读、需要多次工具调用
- 基于真实场景
- 单个可验证的答案

## 关键资源

- MCP 规范: https://modelcontextprotocol.io/
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk

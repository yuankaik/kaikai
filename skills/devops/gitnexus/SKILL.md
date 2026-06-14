---
name: gitnexus
description: 代码知识图谱引擎 (42K⭐)——把代码库索引成依赖关系图。MCP 支持，Hermes 可直接查询代码结构。npm install -g gitnexus。
source: https://github.com/abhigyanpatwari/GitNexus
---

# GitNexus — 代码知识图谱

把代码库变成 Agent 能理解的知识图谱。

## 安装

```bash
npm install -g gitnexus
```

## 使用

```bash
# 索引项目
cd ~/kaikai && gitnexus index

# 启动 Web UI
gitnexus serve

# MCP 模式（给 Hermes 用）
gitnexus mcp
```

## 能力

- 依赖关系追踪
- 调用链分析
- 代码聚类
- 执行流可视化
- MCP 工具：给 Agent 提供代码结构查询

## 与 Hermes 集成

通过 MCP 连接后，Hermes 可以：
- 查找函数调用关系
- 理解模块依赖
- 定位代码影响范围

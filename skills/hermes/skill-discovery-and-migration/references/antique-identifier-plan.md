# 文玩鉴定技能开发计划

会话日期：2026-06-14
用户：kai哥
需求：微信拍照→AI 鉴定文玩真假

## GitHub 搜索结果

搜索了 antique+identification+AI、文玩+鉴定、gemstone+jade+identification 等关键词。
只有 3 个 0 星项目，没有成熟方案。需自建。

## 技术方案

| 层级 | 方案 |
|------|------|
| 图片接收 | 微信拍照发 Hermes |
| 视觉分析 | DeepSeek/Claude 多模态 API（已配） |
| 知识库 | MD 文档 + 特征描述 |

## 三类优先

1. **文玩核桃**：品种/纹路/包浆/做旧识别
2. **手串**：材质/密度/香味/染色识别
3. **玉石**：种水/颜色/光泽/证书核验

## 开发步骤

### Phase 1：建知识库
- 核桃鉴定.md：品种图鉴、真假对比特征
- 手串鉴定.md：小叶紫檀/黄花梨/沉香辨别
- 玉石鉴定.md：翡翠 ABC 货、和田玉辨别

### Phase 2：写技能
- antique-identifier SKILL.md
- 包含分析流程 + 判断标准

### Phase 3：端到端测试
- 微信发图 → 自动调用 → 返回结果

## 目录结构
```
skills/vertical/antique-identifier/
├── SKILL.md
└── knowledge/
    ├── 核桃鉴定.md
    ├── 手串鉴定.md
    └── 玉石鉴定.md
```

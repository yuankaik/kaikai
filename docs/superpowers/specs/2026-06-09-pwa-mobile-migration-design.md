# 王牌钓手 — PWA 移动端迁移设计

> 2026-06-09 | kaikai + Hermes
> 目标：本地网页版 → 可分发移动 APP（闭源）

---

## 1. 当前状态

- **架构**：Python HTTP Server + SQLite + HTML/CSS/JS 前端
- **规模**：50 py 文件 / 36 html 文件 / 4 JSON spec / 60KB 数据库
- **核心模块**：
  - `engine/auto_grader.py` — 自动批改引擎
  - `engine/learning_store.py` — SQLite 数据存储
  - `engine/rod_system.py` — 5级鱼竿升级
  - `engine/mistake_review.py` — 错题回顾
  - `app/captain_renderer.py` — 练习页渲染（~1925行）
  - `app/captain_dashboard.py` — 航海图看板
  - `tutor_core/next_day.py` — 次日练习生成
  - `tutor_core/points.py` — 积分系统

---

## 2. 四阶段路线图

### Phase 1：PWA 化（2-3 周）

**目标**：手机浏览器打开就能用，可安装到桌面，离线可用

**改动**：
1. 抽取纯前端版本 — 把 captain_renderer.py 生成的 HTML 改成独立运行的 SPA
2. 添加 `manifest.json` — 应用名、图标、全屏模式
3. 添加 `sw.js` (Service Worker) — 离线缓存策略
4. 练习 JSON 数据内嵌到前端（或 fetch + cache）

**产出物**：一个 URL 打开的网页，手机浏览器"添加到桌面"后就是准 APP

### Phase 2：JS 引擎重写（3-4 周）

**目标**：干掉 Python 后端，全部逻辑跑在浏览器里

**需重写的 Python 模块 → TypeScript**：
| Python | TypeScript | 行数估算 |
|--------|-----------|---------|
| `auto_grader.py` | `grader.ts` | ~800 |
| `learning_store.py` | `store.ts` (IndexedDB) | ~600 |
| `rod_system.py` | `rod.ts` | ~300 |
| `points.py` | `points.ts` | ~200 |
| `mistake_review.py` | `mistake.ts` | ~400 |
| `next_day.py` | `nextday.ts` | ~300 |
| 合计 | | ~2600 行 |

**技术选型**：
- 不引入 React/Vue 框架（保持零依赖，减少打包体积）
- TypeScript 编译为单文件 JS，闭源混淆（terser）
- IndexedDB 替代 SQLite（浏览器原生，无需权限）

### Phase 3：云端同步（2-3 周）

**目标**：孩子端练习 → 云端存储 → 爸爸看报告

**方案**：
- 后端：Node.js / Python 轻量 API（Vercel / 阿里云函数计算）
- 数据库：SQLite 云端（Turso / Cloudflare D1）
- 同步策略：本地 IndexedDB 为主，后台静默上传

### Phase 4：打包上架（2 周）

**目标**：APK + IPA，上架应用商店

**工具**：Capacitor.js
- 把 PWA 包进 WebView → 生成 APK（Android）和 IPA（iOS）
- 签名、应用商店合规（隐私政策、儿童隐私 COPPA）

---

## 3. Phase 1 详细设计（立即开始）

### 3.1 文件结构规划

```
王牌钓手/
├── pwa/                          # 新建 PWA 目录
│   ├── index.html                # 主入口 SPA
│   ├── manifest.json             # PWA 清单
│   ├── sw.js                     # Service Worker
│   ├── css/
│   │   └── deepsea.css           # 深海主题（从 captain_renderer 提取）
│   ├── js/
│   │   ├── app.js                # 路由 + 页面切换
│   │   ├── renderer.js           # 练习页渲染（从 captain_renderer 迁移）
│   │   ├── grader.js             # 前端批改（先做简单版，Phase 2 完整重写）
│   │   └── storage.js            # localStorage 过渡（Phase 2 换 IndexedDB）
│   ├── data/
│   │   └── specs/                # 练习 JSON spec（从 practice/specs 复制）
│   ├── assets/
│   │   ├── icon-192.png          # PWA 图标
│   │   ├── icon-512.png
│   │   └── sounds/               # 音效（可选）
│   └── favicon.ico
├── app/                          # 现有 Python 后端（保留）
├── engine/                       # 现有引擎（保留）
├── practice/specs/               # 现有 JSON spec（保留）
└── docs/                         # 文档
```

### 3.2 关键设计决策

1. **SPA 单页应用** — 一个 index.html 承载所有页面（练习页、看板、历史列表），通过 JS 切换
2. **零构建工具** — Phase 1 不引入 webpack/vite，直接写原生 JS。Phase 2 引入 TypeScript + esbuild 轻量打包
3. **深海主题保留** — CSS 动画、气泡效果、鱼竿拉扯全部迁移
4. **数据格式不变** — JSON spec 格式保持与现有 practice/specs/ 一致

### 3.3 Phase 1 任务清单

- [ ] 创建 `pwa/` 目录结构
- [ ] 写 `manifest.json`
- [ ] 写 `sw.js`（离线缓存策略）
- [ ] 从 `captain_renderer.py` 提取深海 CSS → `deepsea.css`
- [ ] 写 `index.html` SPA 框架
- [ ] 写 `renderer.js` 练习页渲染（迁移 Python 模板逻辑）
- [ ] 写 `grader.js` 前端批改（先支持现有题型）
- [ ] 写 `storage.js` 本地存储（localStorage → 后续 IndexedDB）
- [ ] 手机浏览器实测：安装到桌面 + 离线使用

---

## 4. 闭源策略

| 阶段 | 措施 |
|------|------|
| 开发期 | GitHub 私有仓库（已就绪：yuankaik/kaikai） |
| Phase 2+ | JS 代码 terser 混淆 + sourcemap 不上传 |
| 上架期 | APK 原生混淆，IPA App Store 加密 |

---

## 5. 风险与对策

| 风险 | 对策 |
|------|------|
| Python 批改逻辑迁到 JS 有差异 | Phase 1 保留 Python 后端做"参考答案"，JS 前端做即时判断，双轨验证一段时间 |
| 动画性能在低端手机卡顿 | 深海动画降级开关，检测设备性能自动关闭粒子效果 |
| 题库内容泄露 | 题库 JSON 不随客户端分发，云端按需下发（Phase 3） |
| IndexedDB 数据丢失（浏览器清缓存） | Phase 3 云端同步后此风险消失 |

---

## 6. 下一步

确认设计后 → `writing-plans` 技能 → 生成 Phase 1 详细实施计划 → 开始写代码

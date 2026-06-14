# 袁佳乐的王牌钓手 — 项目大纲

> 一键导航 | 生成日期：2026-06-08

---

## 一、项目概览

- **项目名称**：袁佳乐的王牌钓手（Ace Angler）
- **产品定位**：一对一家庭教师系统（网页版）
- **目标用户**：袁佳乐（上海市虹口区小学四年级）、爸爸（"大副"角色）
- **核心目标**：每天12-20分钟短练习，把D级水平稳步推高
- **技术栈**：Python 3.12 + HTTP Server（标准库）+ SQLite + 纯前端HTML/CSS/JS
- **世界观**：王牌钓手（钓鱼/出海/鱼币/Boss战）
- **入口**：`http://127.0.0.1:8000/` → 首页 / `/captain/today` → 今天练习

---

## 二、项目结构

```
袁佳乐的王牌钓手/
├── app/                        # 网页应用
│   ├── local_tutor_server.py   # HTTP 服务器主程序
│   └── captain_renderer.py     # 船长页面渲染（1908行，完整深海主题UI）
├── engine/                     # 核心引擎
│   ├── learning_store.py       # SQLite 数据存储（结果/录音/学校错题）
│   ├── rod_system.py           # 鱼竿升级系统（5级，Day1-20）
│   ├── mistake_review.py       # 错题回顾（CSV+XLSX+学校上传三合一）
│   └── school_mistake_pipeline.py # 学校错题上传→识别→回炉管道
├── tutor_core/                 # 核心调度
│   ├── next_day.py             # 次日练习生成
│   ├── points.py               # 积分系统（Switch2鱼币）
│   └── media_assets.py         # 游戏素材资源清单
├── practice/specs/             # 每日练习 JSON spec
│   ├── Day6-蓝鲸英语补给航线.json 等
├── content/voice/              # 语音采集（课堂反馈/Boss讲题）
│   ├── Day4/*.webm, Day5/*.webm
├── records/                    # 记录文件
│   ├── grading-log.csv         # 批改日志
│   ├── points-ledger.csv       # 积分流水
│   ├── switch2_points.txt      # 当前积分状态
│   ├── school-mistake-drafts.csv # 学校错题草稿
├── data/
│   └── learning.db             # SQLite 学习数据库
├── docs/                       # 设计文档（详下）
├── tests/                      # 测试用例
├── handwriting/                # 收杆练字（Day2 HTML+PDF）
├── _hourly/                    # 整点快照备份
└── learner-profile-yuanjiale.md # 学生画像
```

---

## 三、六大核心系统

### 3.1 每日运行链路（6 Steps）
```
Step 1 课堂对齐 → 家长上传/口述课堂进度
Step 2 作业批改 → 照片→grading-result.csv
Step 3 掌握度更新 → 错题回炉 / 做对讲清 / 稳定掌握 / 毕业
Step 4 次日决策 → 红/黄/绿三色状态
Step 5 生成练习 → JSON spec → PDF + 批改模板 + 操作台
Step 6 正向反馈 → 鱼币/图鉴/海域/Boss徽章
```

### 3.2 鱼竿升级（Rod System）
| Lv | 名称 | 海域 | Day | Boss |
|----|------|------|-----|------|
| 1 | 竹竿 | 新手沙滩 | 1-3 | 菊石大师 |
| 2 | 碳素竿 | 珊瑚礁 | 4-7 | 沧龙 |
| 3 | 合金竿 | 沉船湾 | 8-11 | 邓氏鱼 |
| 4 | 深渊竿 | 深海裂谷 | 12-15 | 海王龙 |
| 5 | 传说竿 | 远古深渊 | 16-20 | 龙王鲸 |

### 3.3 积分系统（Points）
- 货币：Switch2鱼币
- 目标：3500分（当前基准 1835分）
- 获取：练习得分 + 大副手动奖励
- API：`POST /api/result`、`POST /api/points/manual`

### 3.4 错题系统（Mistake Review）
- 三源合流：grading-log.csv + 袁佳乐错题本.xlsx + school-mistake-drafts.csv
- 错因分类：知识点缺失 / 题意理解 / 计算错误 / 格式问题 / 粗心
- 回炉优先级：Boss失误 > 小题失误

### 3.5 掌握度状态机
```
未识别 → 入门验证 → 待回炉 → 做对但需讲清 → 理解通过 → 稳定掌握 → 已毕业
```

### 3.6 学校错题上传管道
- `POST /api/school-mistake` → 自动存储到 `content/school_mistakes/`
- 自动识别：txt/md → 解析字段；图片/PDF → needs_ocr 队列
- 支持 OCR 转写后自动回炉

---

## 四、API 端点一览

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/` | 首页（练习历史列表） |
| GET | `/captain/today` | 今日练习页 |
| GET | `/captain/{day}` | 指定日练习页 |
| GET | `/resources/*` `/content/*` | 静态文件 |
| POST | `/api/result` | 提交练习结果 |
| POST | `/api/recording` | 上传语音录音 |
| POST | `/api/school-mistake` | 上传学校错题 |
| POST | `/api/points/manual` | 大副手动加减分（密码1234） |
| POST | `/api/next-day` | 生成次日练习 |

---

## 五、文档体系（docs/）

| 目录 | 内容 |
|------|------|
| `product/` | 系统架构、数据协议、查漏补缺清单、迁移清单 |
| `curriculum/` | 上海四年级技能地图、出题规则 |
| `pedagogy/` | 家长执行与正向反馈手册 |
| `qa/` | 质量验收标准 |
| `research/` | 三巨头画像、学习科学调研 |
| `superpowers/` | 每日开发计划与设计 spec |
| 独立文件 | 掌握度规则、练习生成规则、每日闭环协议 |

---

## 六、当前进度

- **打卡**：Day6（蓝鲸英语补给航线）
- **鱼币**：Switch2 1835/3500
- **鱼竿**：Lv2 碳素竿（珊瑚礁）
- **错题**：9条 | 记忆率 67%
- **已完成**：Day1-Day5 练习 PDF 均生成并印刷使用
- **P0 待办**：出门测、课堂日志CSV化、进度看板自动刷新

---

## 七、技术亮点

1. **零依赖 HTTP 服务**：仅用 Python 标准库 `http.server` + `sqlite3`
2. **1908 行纯 CSS 深海主题**：动画（扫描线/波浪/鱼钩/金币/浮卡）+ 响应式网格
3. **XLSX 直读**：自实现 ZIP+XML 解析器读取错题本，无需 openpyxl
4. **录音采集**：浏览器 `MediaRecorder API` → POST webm → 本地存储
5. **离线优先**：所有数据本地 SQLite，不依赖网络
6. **家长友好**：bat 文件一键启动 / 大副只需勾选+拍照

---

## 八、待优化方向（初步）

1. OCR 集成：学校错题照片自动识别
2. 语音转写：课堂反馈音频→结构化课堂日志
3. 进度看板：自动聚合掌握度+积分+海域进度到可视化面板
4. 题型模板库：数学 A/B/C 三档 + 语文阅读模板 + 英语机械→产出
5. 阶段测评：每4次自动小测 / 每12次阶段评估
6. 宝可梦第二世界观：80分达成后解锁
7. 微信联动：家长通过微信上传照片/语音自动入库
8. 云端备份：整点快照自动同步

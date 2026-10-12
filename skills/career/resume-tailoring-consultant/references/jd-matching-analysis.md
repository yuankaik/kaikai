# JD 关键词匹配分析（岗位侧调研）

用于回答"我们这份简历投这个岗到底行不行、缺什么"。跟 `references/resume-fact-check-workflow.md`（**候选人侧**核对）互补。

**顺序**：先保证候选人侧的事实核对过关，再做这一份 JD 侧匹配。事实没核实就做关键词匹配 = 白做。

---

## 一、抓取平台的能力与坑（实测结论）

| 平台 | 可用性 | 工具 / 路径 | 关键坑 |
|---|---|---|---|
| **BOSS直聘** | ✅ 首选 | `data-science/boss-zhipin-scraper`（独立 skill） | 需登录才能拿**明文薪资**；单次 ≤10页(300条)；翻页间隔 12–22s |
| 领英 | ⚠️ 受限 | `speedyapply/JobSpy` ⭐4.3k（LinkedIn/Indeed/Glassdoor/Google） | 中国版已关闭，仅国际版，国内访问受限 |
| 51job | ❌ 不推荐 | GitHub 上多为毕业设计级（⭐16–222），**过时严重**，反爬已很强 | 别浪费时间 |
| 猎聘 | ❌ 不推荐 | GitHub API 搜索直接 `IncompleteRead`；站点风控严格 | 别浪费时间 |

### 结论：先打样再决定

**用 BOSS 直聘打样**——它是唯一有高质量现成工具、且能绕过字体反爬拿到明文薪资的平台。
跑通后看数据量够不够出结论；够就不必再啃 51job/猎聘这两个反爬重灾区。

### 为什么 BOSS 必须登录

薪资数字被做成**自定义字体**（前端渲染出乱码），只有登录后调内部 API
（`/wapi/zpgeek/search/joblist.json`）才返回明文字段 `salaryDesc`。
所以"未登录也能抓"是错的——拿到的薪资不可信，脚本默认禁用 DOM fallback 就是这个原因。

（详细参数、筛选码、安装步骤见 `data-science/boss-zhipin-scraper` 的 SKILL.md，不要在这里重抄。）

---

## 二、ZIP → SKILL.md 安装速查（踩过的操作序列）

很多 GitHub 技能库不提供 `hermes skills install` 的入口，标准安装路径是：

```bash
# 1) 下载（raw 常超时，用 codeload zip 一次拿全）
curl -sL --max-time 120 \
  "https://codeload.github.com/<owner>/<repo>/zip/refs/heads/main" -o /tmp/x.zip

# 2) 解压看结构
cd /tmp && unzip -qo x.zip -d ex && find ex -name "SKILL.md"

# 3) 手动落到 Hermes 技能目录（含 scripts/ 和 data/）
mkdir -p ~/.hermes/skills/data-science/<skill-name>/scripts \
         ~/.hermes/skills/data-science/<skill-name>/data
cp SKILL.md                       ~/.hermes/skills/data-science/<skill-name>/
cp scripts/*.py                   ~/.hermes/skills/data-science/<skill-name>/scripts/
cp data/*.json                    ~/.hermes/skills/data-science/<skill-name>/data/
```

⚠️ **别漏了 `data/` 目录**——这类爬虫技能常把城市代码表等字典放在 `data/`，
漏了会在运行时报找不到文件。

### 依赖安装（本机 Python 是 externally-managed）

```bash
pip install --break-system-packages -q <deps>
```
本机需要 `--break-system-packages`，直接 `pip install` 会被拒绝。

---

## 三、抓取前的环境准备（WSL + WSLg）

Chrome CDP 是本机爬取的关键路径（复用真实登录态、绕过反爬）。
**注意**：本机 Chrome 装在 **WSL 内**（`/usr/bin/google-chrome`，`/opt/google/chrome/chrome`），
通过 WSLg 显示（`DISPLAY=:0`），**不是** Windows 侧的 chrome.exe。别去 `/mnt/c/` 找。

启动带 CDP 的 Chrome（**必须用 `background=true`**，shell 级 `nohup`/`&` 会被 Hermes 拒绝）：

```bash
pkill -f "remote-debugging-port=9251"; sleep 1
exec google-chrome --remote-debugging-port=9251 \
  --user-data-dir="$HOME/.chrome-<purpose>-profile" \
  --no-first-run --no-default-browser-check --window-size=1400,900
```

探活（等 8s 再探，启动需要时间）：

```bash
curl -s --max-time 6 http://127.0.0.1:9251/json/version   # 返回 Chrome 版本 JSON = 就绪
ss -tlnp | grep 9251
```

开新标签页让用户登录：

```bash
curl -s -X PUT "http://127.0.0.1:9251/json/new?https://www.zhipin.com/web/user/?ka=header-login"
```

⚠️ 用**独立的 `--user-data-dir`**，别用用户主 profile——CDP 会话只暴露该专用 profile 的数据，
不碰用户的 Gmail/GitHub 等账号。登录态持久保留，下次不用重登。

### 端口约定（沿用本机既有）

```
9251  本机通用 CDP（cn-scraper 系列、BOSS 直聘都走这个）
9222  boss-zhipin-scraper 的默认端口（本机已习惯用 9251，传 --cdp-port 9251）
```

---

## 四、匹配度分析怎么做

拿到 JD 数据后，**不要只输出一堆岗位列表**。按下面的结构做分析：

### 1. 关键词抽取与覆盖率

从抓到的 JD 里分三类提关键词，然后逐条对照简历：

```
硬技能    系统(SAP/WMS/ERP)、认证(ISO13485/GMP)、工具(条码/RF)、方法(5S/精益/FIFO)
软技能    团队管理、跨部门协调、供应商管理
行业词    具名到行业（如医疗器械：UDI、温湿度、洁净区、飞检）
```

算：`覆盖率 = 已覆盖关键词 ÷ 岗位高频关键词总数`。目标 80%+。

### 2. 三类结论（关键——必须分类，不能只报数字）

| 类别 | 含义 | 处理 |
|---|---|---|
| **已具备** | 简历里已有硬证据 | 确认写没写在显眼位置（首屏/核心能力区） |
| **可迁移** | 有邻近经验，换行话说得通 | 用目标行业的语言重述（**不是**编造） |
| **真缺口** | 完全没有 | ① 写进面试预案的防守话术 ② 列入学习清单 |

⚠️ **真缺口绝不能靠改简历补**。见 `references/resume-fact-check-workflow.md` 的事故复盘。

### 3. 薪资定位

用抓到的薪资分布给一个区间判断（25分位/中位/75分位），
让用户知道当前要价在市场上的位置。**BOSS 的明文薪资是这个分析的唯一可靠来源**，
这也是必须先登录的原因。

### 4. 输出

一份分析报告放桌面（PDF），包含：岗位样本量 → 关键词覆盖表 → 三类结论 → 薪资定位
→ 待补清单。**与简历优化建议分开列**，避免"行业考点"被误当成"要写进简历的内容"。

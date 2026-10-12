---
name: windows-disk-archive-survey
description: 盘点/整理 Windows+WSL 多盘存档（C:/D:/WSL home）的占用分布，产出"哪些目录存了什么、哪些可清理"的清单，并在用户确认后只删安全项（废弃残留/安装包/空目录），绝不碰资料。当用户问"哪个盘有什么存档/帮我看看怎么整理/删掉没用的"时使用。
category: windows
---

# Windows + WSL 多盘存档盘点与安全清理

## 触发条件
- 用户问「我们在哪些本地盘有存档 / 各盘存了什么 / 帮我整理一下 / 删掉没用的」
- 需要判断某个目录能不能删、哪些是重复存档、哪些是废弃残留

## 铁律（kai哥 明确要求）
1. **先盘点、后确认、再动手**。出清单让用户挑，不擅自删。
2. **清理范围严格按用户圈定**。kai哥 选「只清废弃残留+安装包+空目录（不碰资料）」时，就绝不动 期末卷/暑假练习/儿童文学 这类资料目录，哪怕它们体积最大。
3. **绝不整体删「混合目录」**。有些目录名看着像杂物堆，里面却混着用户的资料（见下方 应用传送门 案例）。整个 `rm -rf` 会毁掉报名照、课件、电子书。只能挑出里面的安装包单删。
4. **确认清单里逐项列体积**，让用户能一眼判断值不值得。

## 第一步：全盘概览
```bash
# 盘符与容量（先看哪个盘紧张）
ls /mnt/                              # c d wsl wslg
df -h /mnt/c /mnt/d 2>/dev/null | grep -v tmpfs

# WSL home 顶层占用（快，Linux 侧）
du -sh ~/* 2>/dev/null | sort -rh | head -20

# C盘桌面各目录占用
du -sh /mnt/c/Users/<user>/Desktop/* 2>/dev/null | sort -rh | head -30
```

## 第二步：D盘/大目录逐目录统计（关键，避开超时与静默失败）

**⚠️ 坑 1：`du -sh /mnt/d/*` 会超时**（Windows FS 上小文件极多，180s 不够）。
**⚠️ 坑 2：`du` 的目录名带空格（尤其双空格）时，带引号的整串命令会静默失败**——exit 1、无任何输出，且会中断它所在的 for 循环。

正确做法：**一次一个目录、绝对路径、不带多余引号包裹整串**：

```bash
# ✅ 对：逐个跑，绝对路径
du -sh /mnt/d/金田一 2>/dev/null
for d in 上海小学教材试题 kaiHermes Bili 迅雷下载; do du -sh "/mnt/d/$d" 2>/dev/null; done
# 带空格的用反斜杠转义，别用带双空格的原始名
du -sh "/mnt/d/Kindle backup 20240426" 2>/dev/null

# ❌ 错：一条命令里塞多个带引号/带空格的名字 → exit 1 无输出，循环断掉
# du -sh --max-depth=0 "金田一" "上海小学教材试题" "Claude code  documents"
```

**⚠️ 坑 3：从 WSL 调 PowerShell 递归算目录大小容易被审批层拒绝**（`Get-ChildItem -Recurse | Measure-Object`）。别把它当主力路径——WSL 侧逐个 `du -sh` 就能覆盖，慢但稳、不触发审批。

先 `ls /mnt/d/` 拿到真实目录名（含空格/中文），再逐个 du。分批跑，每批几个目录，避免单次超时。

## 第三步：把盘点结果按「位置 × 内容 × 体积」分组呈现
输出结构（用等宽字符表格，CLI 友好）：
```
【D盘 · <已用>/<总量>】          最主存储
  <体积> <目录>/   <一句话说明 + ⭐标记与当前任务相关的>
【C盘 Desktop · <体积>】          <条目数>个条目
  ...
【WSL 内部 home · <体积>】
  ...
```
标出重复存档（同一内容在两个位置）、版本堆积（同名文件多个版本）、明显异常（如 docx 202M）。

## 第四步：分级给出可清理项（让用户挑档位）
分四档，用 clarify 让用户选：
1. **只清废弃残留+安装包+空目录**（最安全，不碰资料）
2. 安全清理 + 合并重复存档
3. 加上大文件瘦身（版本堆积/异常大文件/缓存）
4. 先出详细清单我逐项决定

## 第五步：安全清理项的确切定位（第四步选 1 时）
```bash
# 废弃残留：失败的 pip 安装、旧 .hermes 备份
ls -ld ~/hermes_broken_pip_install_* ~/.hermes.backup.* 2>/dev/null
du -sh ~/hermes_broken_pip_install_* ~/.hermes.backup.* 2>/dev/null

# 空目录
ls -la /mnt/d/FlFile /mnt/d/OfFile 2>/dev/null    # total 0 = 空

# 安装包（exe/msi），排除程序本体目录
find /mnt/c/Users/<user>/Desktop /mnt/c/Users/<user>/Downloads -maxdepth 2 \
  \( -iname "*.exe" -o -iname "*.msi" \) 2>/dev/null
```
**删前必做**：对每个候选目录先 `ls -la` 看内容——尤其形如「应用传送门」这种名字模糊的，确认里面没有资料再决定。

## 第六步：与用户确认后执行
列出「确切清单 + 逐项体积 + 小计」，AskUserQuestion/clarify 确认，再删。删完复核 `df -h`。

## 第七步：归类合并（用户要求「合并成一个文件夹」时）

kai哥 常追加要求：「散落的 X 类文件夹合并成一个」「重复的保留一份」。做法：

**7a. 先摸清全部候选 + 内部结构**（防误合并）：
```bash
ls -la /mnt/c/Users/<user>/Desktop/          # 全部条目(含类型/大小)
for d in <候选文件夹...>; do echo "== $d =="; ls "/mnt/c/Users/<user>/Desktop/$d" | head -12; done
```

**7b. 用内容 hash 判重复，不光看文件名**（关键）：
```python
import os, hashlib
def h(fp): return hashlib.md5(open(fp,'rb').read()).hexdigest()
def listfiles(p):
    return {os.path.relpath(os.path.join(r,f),p) for r,_,fs in os.walk(p) for f in fs}
a, b = listfiles(A), listfiles(B)
print("同路径同名:", set(a)&set(b))          # 直接重复
# 对不同名的，逐文件比 hash 判断内容是否真重复：
# for f in A独有: if h(A/f) in {h(B/g) for g in B}: 重复
```
实战：`第一周练习` 8/13 文件与 `佳乐暑假完整练习库` 同路径同名 → 重复；余 5 个经 hash 比对**内容独有**（分年级版），必须保留。**只看文件名会误判**——同名不同内容、不同名同内容都存在。

**7c. 合并结构：平铺分类，不搞深层嵌套**（对齐 kai哥 铁律「每文件夹仅两个子目录、禁止深层嵌套」）。用中文分类名（每日练习/练习题库/期末试卷/教材资源/错题本/证书/参考资料），不要 01-02 数字前缀。`shutil.move` 搬移，目标已存在则跳过并记录，绝不覆盖。

**7d. 从容器里分离「混进来的异类」**：合并时若发现某文件夹里混着不属于它的内容要挑出来单独成夹。实战：`佳乐暑假完整练习库` 里混着《深海钓徒》小说全文+42张插画 → 分离成 `深海钓徒/`，练习库从 56 项瘦到 12 项纯练习。

**7e. 桌面单文件也要归位**：散落的单文件（口算.docx/单词表.pdf/复盘报告等）按内容判断归属，移进对应分类子目录。

**7f. 建类级文件夹收纳同类散文件**：如 `工作/`（Warehouse月报×4版本、KPI表、Resume/、各类手册）、`佳乐学习/`。**但别碰像在进行中的项目文件**——kai哥 的 `Hermes.txt`、`王牌钓手项目.txt`、`后续开发计划.docx`、`设想架构.docx`、截图 png 等，看着像杂项，实为活动项目，保留原位（或先问）。

## ⚠️ 敏感文件发现（清理时高发，必须主动上报）

桌面/杂项目录里常明文躺着密钥。本次发现：
- `Hermes.txt` → 明文 OpenRouter API key（`sk-or-...`）+ 另外两个 key
- `scmwh-wx-secret.txt` → 疑似微信 secret

**处理原则**：发现后**不擅自删/移动**，主动用醒目提示告警，建议 ①移到 `~/.hermes/` 隐藏目录 或 ②去服务商后台轮换密钥。机密文件的处置权归用户。

## 交付报告格式（kai哥 偏好）
等宽框线分区报告：①删除·逐项体积+小计 ②合并后的目标结构树 ③去重项 ④空间变化（df）⑤**必须主动提醒**的点（敏感文件、未处理的活动项目、安全清理释放有限）。用纯文本，CLI 友好，不用 markdown 表格。

## 实战案例（2026-10-12，完整两阶段）
C盘 176/200G(89%)、D盘 237/266G(89%)。D盘大头：相机原片56G、百度网盘55G、网易云缓存41G、手机照片15G、B站13G、迅雷12G、金田一6.9G、kaiHermes 5.3G、上海小学教材试题4.4G。桌面2.7G/82条目。

**阶段一 · 安全清理**（用户选「只清废弃残留+安装包+空目录」）：
- **危险目录**：`桌面/应用传送门/`（71M）——名字像杂物堆，实为混合目录：既有 OllamaSetup.exe/XunLeiWebSetup.exe 安装包，**也有** 袁佳乐报名照.jpg、python培训课件.pptx、Pony.mobi、dupont-build/、各软件快捷方式。**绝不能整体删**。
- 删：`~/hermes_broken_pip_install_20260614-*`(24M)、`~/.hermes.backup.20260614-*`×2(各2.8M)、`/mnt/d/FlFile/`+`Ofile/`(空)、桌面 Feishu 安装包(437M)、OllamaSetup(27M)、迅雷setup(6.6M)、efanapp 三个安装包(85M，含旧版+重复版) → 合计 ~583M。
- **要主动提醒用户**：安全清理释放有限，真正大头是缓存/照片/网盘等资料区，不动资料则空间不会明显改善。

**阶段二 · 归类合并**（用户追加「重复保留一份、佳乐学习类合并一个文件夹」）：
- 桌面 82 项 → 37 项。
- 建 `佳乐学习/`（1.3G，8 个中文分类子目录）：每日练习/练习题库/期末试卷/教材资源/错题本/体育证书/参考资料/深海钓徒。11 个散落文件夹 + 13 个单文件归入。
- 建 `工作/`：Warehouse月报×4版本、KPI表、Resume/、SHEIN报告、医药转行手册等 18 项。
- MD5 去重：`第一周练习`→并入练习库；深海钓徒 A4.pdf 桌面版/库内版留一份；反复重下的书留一份。
- 分离异类：《深海钓徒》小说+42张插画从练习库挑出 → 独立成夹，练习库 56→12 项。
- **敏感文件**：发现 `Hermes.txt` 明文 OpenRouter key、`scmwh-wx-secret.txt` → 主动告警，未擅自处理。

## 支持文件
- `scripts/disk_survey.py` — 盘点+去重探针。传 1 个目录出类型分布/顶层清单；传 2 个目录自动比重复（先按相对路径同名，再按 MD5 内容），直接标出「内容独有，需保留」。合并/清理前跑一遍，避免误判。

## 相关技能
- `windows/windows-power-diagnostics`、`devops/windows-startup-automation` — 同为 WSL→Windows 跨边界操作。PowerShell 调用通用坑（PATH 污染需用完整路径 `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`、中文乱码加 UTF8 Encoding、管道必须写在 PS 命令串内部）在那两个技能里已详述，本技能不重复。

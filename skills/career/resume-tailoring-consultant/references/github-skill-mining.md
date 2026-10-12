# 从 GitHub 挖掘领域技能库（Skill Mining）

**场景**：用户要求"先去 GitHub 搜技能，然后回来改"。需要先侦察、吸收方法论，再动手。

## 为什么不用 web_search

本机环境下 `web_search`（DuckDuckGo 后端）经常 30 秒超时。
**不要卡在这里**——直接走 GitHub 原生 API。

## 步骤

### 1. 搜索仓库（GitHub API，非 web_search）

```python
import json, urllib.request, urllib.parse, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def gh(q, per=10):
    url = (f"https://api.github.com/search/repositories"
           f"?q={urllib.parse.quote(q)}&sort=stars&order=desc&per_page={per}")
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "Mozilla/5.0"
    })
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        d = json.loads(r.read().decode())
    return [(i["full_name"], i["stargazers_count"],
             (i.get("description") or "")[:120]) for i in d.get("items", [])]
```

**多组关键词并行搜**，每组看 top 10 就够：
```
resume+optimizer / resume+ATS / interview+preparation /
resume+builder+AI / 招聘+简历
```

### 2. 看仓库结构，决定下不下

```python
def gh_tree(full):          # 先试 main 再试 master
    for br in ("main","master"):
        url = f"https://api.github.com/repos/{full}/git/trees/{br}?recursive=1"
        ...
        return br, [t["path"] for t in d.get("tree",[])]
```

**判断标准**：目录里有没有 `skills/*/SKILL.md`、`references/*.md`。
纯代码项目（前端/后端应用）对"吸收方法论"没用——要的是**技能库**。

### 3. 下载：用 codeload zip，不要 raw

⚠️ **`raw.githubusercontent.com` 逐个文件 curl 会大量超时**（本次 9 个文件只成功 1 个）。

改用整包下载，一次拿全：

```bash
curl -sL --max-time 120 \
  "https://codeload.github.com/<owner>/<repo>/zip/refs/heads/main" \
  -o /tmp/iskills/<name>.zip
cd /tmp/iskills && unzip -qo <name>.zip -d ex
```

实测结果：3 个仓库（含一个 6MB 的）**33 秒全部下完**。
对比：raw 逐文件方式 9 个文件里 8 个失败。

### 4. 读什么（按价值排）

只读**方法论类**的 SKILL.md，不要通读全部：

1. 与你任务**直接对应**的那个（如改简历 → `resume-ats-optimizer`）
2. 提供**框架**的（`resume-bullet-writer` 的 X-Y-Z 公式、`resume-quantifier` 的量化技巧）
3. 提供**边界判断**的（`career-changer-translator` 的迁移技能映射表）

**跳过**：面向别的岗位的（tech-resume-optimizer）、纯工程代码。

### 5. 吸收后固化，而不是留一堆临时文件

把多来源的方法论**综合成你自己的技能**（用 `skill_manage action=create`），
而不是告诉用户"我下载了 N 个库在 /tmp"。

用户要的是**能力**，不是**下载记录**。

---

## 本次实际收获（可作为简历类任务的参考库）

| 仓库 | 星 | 价值 |
|---|---|---|
| `Paramchoudhary/ResumeSkills` | 2411 | 22 个技能。最有用：`resume-ats-optimizer`（ATS兼容清单+关键词匹配算法）、`resume-bullet-writer`（X-Y-Z公式/STAR/CAR/强动词表）、`resume-quantifier`（量化发现法+保守估计原则）、`career-changer-translator`（跨行业技能翻译对照表） |
| `andrew-shwetzer/career-ops-plugin-*` | 500 | Claude 插件，9 技能 + `references/ats-rules.md` + `scoring-rubric.md` |
| `Jichengyuuuuu/resume-builder-skill` | 160 | 中文简历生成。「加粗概括短语+冒号」强制格式出处于此 |
| `magicapple123/ResumeForge` | 196 | 「事实台账防虚构」思路参考 |

**最高价值的三条方法论**（已并入 `resume-tailoring-consultant`）：
1. **X-Y-Z 公式**：达成【X】，以【Y】衡量，通过【Z】实现
2. **中文强制格式**：每条分点 = **加粗概括短语：** + 具体描述（含数字）
3. **保守估计原则**：估算往低了写以维持可信度（想 100 就说 75+）

---

## 坑

- **JSON 解析失败**：`terminal` 返回的 GitHub API 输出被截断导致 `json.loads` 报错。
  用 `urllib` 在 `execute_code` 里直连，绕开 terminal 的输出限制
- **SSL 证书**：本环境需要 `ssl.CERT_NONE` 的 context
- **默认分支不一定是 main**：先试 `main`，失败再试 `master`

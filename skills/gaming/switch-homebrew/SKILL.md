---
name: switch-homebrew
description: Switch大气层破解相关——金手指查找、BID获取、文件路径结构。当用户询问Switch游戏作弊码、金手指、MOD、或版本BID时使用。
category: gaming
---

# Switch 大气层 (Atmosphere) 金手指支持

## 核心原则：外部搜索快速失败

**大多数 Switch 破解相关外部站点在此环境不可达：**

| 站点 | 状态 | 原因 |
|------|------|------|
| GBATemp | ❌ | Cloudflare 盾 |
| tinfoil.io | ❌ | 523 不可达 |
| Reddit (r/SwitchHacks) | ❌ | 超时 |
| GitHub 代码搜索 | ❌ | 需登录 |
| 91wii / 品技 | ❌ | 空白/不可达 |
| cheatslips.com | ❌ | 超时 |
| DuckDuckGo | ❌ | 连接重置 |

**工作流铁律：尝试 2-3 个不同来源后全部失败 → 立即停止搜索，告诉用户在设备上查。不要反复换 URL/换关键词死磕。**

## 金手指 (Cheats) 基本结构

### 文件路径
```
SD:/atmosphere/contents/<TID>/cheats/<BID>.txt
```

- **TID** = Title ID（16位十六进制，如 `01009B700B084000`）
- **BID** = Build ID（16位十六进制，如 `B0C9A3E6F5D7E8A2`，每个游戏版本不同）

### 文件格式（大气层格式）
```
[金手指名称]
04000000 地址 数值
04000000 地址 数值

[另一个金手指]
04000000 地址 数值
```

## 查 BID 的方法（按推荐顺序）

### 方法一：Tesla 浮层 + EdiZon
1. 进游戏后按 **L + ↓ + 右摇杆按下（R3）** 呼出 Tesla 浮层
2. 选 **EdiZon** → 查看游戏信息
3. 屏幕显示 TID 和 BID

### 方法二：Breeze（如果装了）
1. 进相册 → 打开 Breeze
2. 找到游戏 → 按 Y 查看 TID/BID
3. 可按 X 在线下载金手指（如果网络可用）

### 方法三：看 SD 卡目录
把 SD 卡插电脑，查看：
```
SD:/atmosphere/contents/<TID>/
```
如果已有 cheats 文件夹，里面的 .txt 文件名就是之前的 BID。

### 方法四：DBI / Goldleaf / Checkpoint
这些 homebrew 工具也能显示游戏的 BID 信息。

## 已知游戏记录

### DOAX3 Scarlet（死或生沙滩排球3 绯红）
- TID: `01009B700B084000`
- 版本: 1.0.6 (v65536)
- 版本: 中文版 (AS)
- BID: **需用户自检**（常见候选：`E3F46E8A6C2D5D72` JP版 / `B0C9A3E6F5D7E8A2` AS版，但未验证）
- SD卡路径: `SD:/atmosphere/contents/01009B700B084000/cheats/<BID>.txt`

## 拿到 BID 后的流程

1. 用户提供 BID
2. 尝试从已知 GitHub 金手指库拉取（tomvita/MyNXCheats, bad1dea/NXCheats 等）
3. 如果找不到现成的，根据常见的金手指代码格式直接编写
4. 生成 .txt 文件，告诉用户放到对应 SD 卡路径

## 常见金手指代码模板（大气层格式）

```
[无限金币/货币]
04000000 XXXXXXXX 05F5E0FF

[无限生命]
04000000 XXXXXXXX 00000063

[最大属性]
04000000 XXXXXXXX 0001869F

[一击必杀]
04000000 XXXXXXXX 00000000
```

⚠️ 地址（XXXXXXXX）随游戏版本变化，必须匹配 BID。

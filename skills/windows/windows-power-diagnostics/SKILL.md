---
name: windows-power-diagnostics
description: Diagnose Windows power/sleep/wake issues from WSL (关机后耗电、电池掉电快、睡眠唤醒异常、快速启动、电源按钮/合盖行为). Covers powercfg commands, WSL→PowerShell pitfalls, and fixes for laptops that drain while "off".
category: windows
---

# Windows 电源/睡眠/唤醒诊断（WSL 调用）

## 触发条件
- 用户问「关机后还在耗电」「电池掉电快」「合盖/电源键没真正关机」「睡眠被唤醒」「快速启动」等
- kai哥 的 Windows 是联想 ThinkPad 笔记本（WSL 环境，Chrome 跑 WSLg）

## WSL → PowerShell 调用的坑（先读，每条都踩过）
1. 命令走 `powershell.exe -NoProfile -Command "..."`（从 WSL bash 直接调 Windows 侧）
2. 中文输出乱码 → 命令字符串**开头**加 `[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;`
3. ⚠️ 管道/重定向（`Select-String`、`|`、`>`、`foreach`）必须写在 powershell 命令字符串**内部**，不能写在 bash 层——写在 bash 层会被当成 Linux 命令执行（报 `command not found`，如 `Select-Object: command not found`）
4. 需要管理员权限的命令（`powercfg /waketimers`、`/requests`、改 HKLM 注册表）会返回「此命令需要管理员权限」。提权会弹 UAC：`powershell.exe -Command "Start-Process powershell -Verb RunAs -ArgumentList '...'"`（需用户在场点「是」）

## 诊断命令清单

### 1. 判断机型（笔记本 vs 台式）
```powershell
Get-CimInstance Win32_ComputerSystem | Select Manufacturer,Model,PCSystemType
# PCSystemType: 1=Desktop  2=Mobile(笔记本)
Get-CimInstance Win32_Battery   # 能返回 EstimatedChargeRemaining = 有电池 = 笔记本
Get-CimInstance Win32_SystemEnclosure | Select -ExpandProperty ChassisTypes
# ChassisTypes: 10=Notebook  9=Laptop
```

### 2. 睡眠状态支持（关键第一步）
```powershell
powercfg /a
```
- 支持「S0 低电量待机(现代待机)」= 现代待机，关机后偷电**最大嫌疑**（"关机"其实是联网待机）
- 支持 S3 = 真正待机（内存供电）；支持「休眠」= Hibernate
- 「快速启动」= 混合关机（关机时写休眠文件，不完全断电）

### 3. 唤醒排查
```powershell
powercfg /lastwake                  # 上次唤醒原因
powercfg /devicequery wake_armed    # 哪些设备被允许唤醒（鼠标/键盘/网卡）
powercfg /waketimers                # 需管理员：唤醒定时器
powercfg /requests                  # 需管理员：谁阻止睡眠
```

### 4. 快速启动是否开启
```powershell
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -Name HiberbootEnabled
# 1=快速启动开启(混合关机)  0=关闭
```

### 5. 电源按钮/合盖动作
```powershell
powercfg /q SCHEME_CURRENT SUB_BUTTONS
```
- 索引值：0=睡眠 1=休眠 2=关机（看「当前交流/直流电源设置索引」）
- ⚠️ 若 SUB_BUTTONS 下只显示「开始菜单电源按钮」一项，说明物理电源键/合盖由厂商固件接管（ThinkPad 常见），Windows 层改不动物理按键，要去 BIOS 或厂商软件改

### 6. 网卡 Wake-on-LAN
```powershell
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\*' -Name '*WakeOnMagicPacket','*WakeOnPattern','DriverDesc' -ErrorAction SilentlyContinue | Select DriverDesc,'*WakeOnMagicPacket','*WakeOnPattern'
```
- 值=1 表示该网卡开启 WOL（魔法包/模式唤醒），关机后网卡保持通电

## 关机后耗电原因（按概率排序）
1. 电源按钮/合盖被设成「睡眠」而非「关机」→ 用户以为关机实际是睡眠，内存持续供电，鼠标一动就醒
2. 快速启动（混合关机）→ 关机=半休眠，不完全断电
3. 厂商 BIOS「关机后 USB 供电」（联想 Always On USB，ThinkPad 默认开，给手机充电用）
4. 网卡 WOL → 关机后网卡保持通电等唤醒（耗电小）
5. 现代待机 S0（若 powercfg /a 显示支持）→ 最大嫌疑

## 彻底关闭方案（按见效排序）
1. 关快速启动：控制面板→电源选项→选择电源按钮的功能→更改当前不可用设置→取消勾选「启用快速启动」；最彻底 `powercfg /h off`（连休眠一起关，释放 hiberfil.sys）
2. 改电源按钮/合盖动作=关机（同一控制面板页面）
3. 关关机后 USB 供电：联想 ThinkPad 开机按 F1 → BIOS → Config → USB → Always On USB = Disabled（或联想 Vantage 软件）
4. 关网卡唤醒：设备管理器 → 网卡属性 → 电源管理 → 取消「允许此设备唤醒计算机」
5. 物理手段（唯一零耗电）：关机后拔适配器 / 关插线板

## 实战案例（2026-08-13）
联想 ThinkPad 20KES7MC00（ChassisType=10 笔记本，电池 84%）。`powercfg /a` 显示支持 S3+休眠+快速启动，**不支持 S0**（排除现代待机）。HiberbootEnabled=1（快速启动开）。SUB_BUTTONS 只有「开始菜单电源按钮」且索引=0（睡眠）→ 物理电源键/合盖由联想固件接管。有线 Intel I219-V + 无线 8265 网卡均 WakeOnMagicPacket=1。wake_armed=鼠标，有 1 条唤醒记录。结论：最大嫌疑是「电源键/合盖=睡眠」+ 快速启动，而非真关机。

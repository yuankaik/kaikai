---
name: windows-startup-automation
description: 在 Windows 主机上创建不依赖 Hermes 的开机自启任务（WSL 环境）。适用：用户要"开机自动做某事"、抱怨 Hermes cron 定时任务漏跑（电脑不常开）、需要在 Windows 侧静默运行脚本。
category: devops
---

# Windows 开机自启任务（替代 Hermes cron）

## 何时用
- 用户说"不要定时任务，改成开机任务 / 开机自动跑"
- Hermes cron 反复漏跑（用户电脑不常开，关机时 cron 不执行——kai哥 的核心痛点）
- 需要在 Windows 侧静默执行某件事（签到、备份、同步、心跳、数据抓取）

## 第一步：判断任务能否脱离 Hermes（关键决策）
| 任务类型 | 能否做成开机脚本 | 方案 |
|---------|----------------|------|
| 纯 HTTP 请求（签到、API 轮询、上报） | ✅ 能 | PowerShell/Python 脚本 + 开机自启 |
| 文件操作、系统命令 | ✅ 能 | 同上 |
| 需要 LLM 生成内容（文档、分析、汇总） | ❌ 不能 | 只能 Hermes cron（电脑开机时跑），或接受漏跑 |

签到这个"只是 HTTP POST"的任务能做成纯脚本；而"三科汇总生成 DOCX"需要 LLM，做不成纯脚本，必须保留 Hermes 侧调度。开工前先分清是哪类，别硬套。

## 方案 A：启动文件夹（免管理员，首选）
效果和"登录任务"完全等价（登录 Windows 时触发），但**不需要管理员权限、不弹 UAC、不动系统级设置**。

1. 写 PowerShell 脚本 `.ps1`（见下方模板）
2. 写 `.vbs` 启动器，放入启动文件夹静默启动 ps1：
   - 路径：`C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`
   - WSL 对应：`/mnt/c/Users/<user>/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/`
   - `.vbs` 内容（单行）：
     ```vbs
     CreateObject("Wscript.Shell").Run "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\path\to\task.ps1", 0, False
     ```
     （`0` = 隐藏窗口，`False` = 不等待返回；路径含空格时用 `""` 包住）
3. 端到端验证：`cscript.exe //NoLogo "C:\...\Startup\xxx.vbs"` 跑一次，再读脚本日志确认链路 .vbs → powershell → 脚本 通了。

## 方案 B：任务计划程序（需管理员）
`schtasks /Create` 或 `Register-ScheduledTask` 都需要管理员权限，会报 `0x80070005 拒绝访问`、弹 UAC。
- 用 `New-ScheduledTaskAction` + `New-ScheduledTaskTrigger -AtLogOn` + `Register-ScheduledTask -Force`
- 只有需要"开机未登录就先跑"或更细的失败重试策略时才值得用；纯登录签到场景方案 A 完全够。

## 方案 C：挂到 Hermes gateway 服务启动后（网络敏感任务首选）
针对"开机后 WiFi 未就绪"反复漏跑的任务（每日签到、API 心跳），与其在 Windows 侧加长固定等待，不如把触发点挪到 WSL 侧常驻服务启动之后——hermes gateway 一起来，网络通常已就绪。实测固定等 25s + 3 次重试（约 65s）在 WiFi 连接慢时照样漏签，挂 gateway 后解决。

1. 用 Python（requests）在 WSL 侧重写任务脚本，逻辑用 **DNS 探测循环**替代固定 Start-Sleep：
   ```python
   def wait_for_network(max_wait=300):
       deadline = time.time() + max_wait
       while time.time() < deadline:
           try:
               socket.gethostbyname("目标域名")
               return True
           except OSError:
               time.sleep(10)
       return False
   ```
2. 在 `~/.config/systemd/user/hermes-gateway.service` 的 `[Service]` 段加后台触发（nohup + `&` 不阻塞服务启动）：
   ```
   ExecStartPost=-/bin/sh -c 'nohup /usr/bin/python3 /home/<user>/<task>/task.py >>/home/<user>/<task>/task.log 2>&1 &'
   ```
   改完 `systemctl --user daemon-reload`。gateway 每次启动（开机自启或手动）都会触发一次，脚本必须幂等（当天已做则跳过）。同时删掉 Windows 启动文件夹对应的 .vbs 避免重复。
3. 验证链路：`systemctl --user restart hermes-gateway.service` 后读任务日志，确认出现新记录（skip/ok）。

## ⚠️ 关键坑（本次实际踩过）
1. **`.ps1` 必须存成 UTF-8 with BOM**。Windows PowerShell 5.1 用系统 ANSI（GBK）读无 BOM 的 .ps1，中文全乱码、报"字符串缺少终止符"等解析错误。用 Python 写文件时 `encoding='utf-8-sig'`。脚本内日志/注释尽量用英文，双保险。
2. **WSL 里 `powershell.exe`（走 PATH）可能报 `Invalid argument`**，改用完整路径：
   `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`（诊断：直接跑完整路径看是否正常，能跑就是 PATH 被污染）。
3. 任务计划程序需管理员（见方案 B），不想弹 UAC 就用启动文件夹方案。
4. 开机后网络（WiFi）未就绪 → 脚本开头 `Start-Sleep` 20-30 秒 + 失败重试 2-3 次（间隔 20 秒）。但 WiFi 连接 >65 秒时仍会漏跑，网络敏感任务直接用方案 C 的 DNS 探测循环。
5. 脚本要**幂等**：先查"今天是否已执行"，已执行则跳过，避免开机多次重复触发（快速启动恢复、手动重复运行等）。
6. WSL 侧 Python 任务脚本的 log 函数**别同时 print 到 stdout**：ExecStartPost 的 nohup 把 stdout 重定向到同一个 log 文件，会导致每条日志写两遍。要么 log 只写文件，要么 nohup 重定向到 /dev/null。

## 验证
- 脚本单独跑一次（`-File task.ps1`）确认 exit=0
- 再通过 `.vbs`/cscript 跑一次确认整条链路
- 读脚本日志文件确认有新增记录

## 支持文件
- `templates/windows-task.ps1` — 通用幂等任务脚本骨架（登录→拿 token→检查是否已执行→执行→验证→写日志→重试）
- `templates/startup-launcher.vbs` — 启动文件夹静默启动器

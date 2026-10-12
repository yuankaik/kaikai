# WSL VHDX 磁盘压缩

WSL2 使用 VHDX 虚拟磁盘，删除 WSL 内部文件后 VHDX 不会自动收缩，导致 C 盘空间不释放。

## 症状
- WSL 内 `df -h /` 显示已用减少，但 Windows 侧 C 盘未释放
- WSL `du -sh /home/` 下降但 `df -h /mnt/c` 不变

## 压缩步骤

### 1. 找到 VHDX 路径
```bash
# 从 WSL 内搜索
find /mnt/c/Users/admin/ -maxdepth 6 -name "ext4.vhdx" 2>/dev/null
```
常见位置：
- `C:\Users\<user>\AppData\Local\wsl\{uuid}\ext4.vhdx`  (WSL 新版)
- `C:\Users\<user>\AppData\Local\Packages\<distro>\LocalState\ext4.vhdx` (旧版)

### 2. 从 Windows 侧执行压缩
由于压缩需要先关 WSL，不能从 WSL 内直接执行。需写 PowerShell 脚本并通过 `cmd.exe /c start` 脱离 WSL 进程启动：

```powershell
# compact_wsl.ps1
$vhdx = "C:\Users\admin\AppData\Local\wsl\{uuid}\ext4.vhdx"

# 先看大小
$before = (Get-Item $vhdx).Length / 1GB

# 关闭 WSL
wsl --shutdown
Start-Sleep -Seconds 5

# 压缩
@"
select vdisk file="$vhdx"
compact vdisk
exit
"@ | diskpart

$after = (Get-Item $vhdx).Length / 1GB
Write-Host "释放: $($before - $after) GB"
```

### 3. 从 WSL 内启动（关键技巧）
```bash
# 复制脚本到 Windows 可访问路径
cp compact_wsl.ps1 /mnt/c/tmp/

# 用 cmd.exe start 脱离 WSL 进程启动
cmd.exe /c "start /min powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\tmp\compact_wsl.ps1 > C:\tmp\compact_log.txt 2>&1"
```
`start /min` 创建独立 Windows 进程，WSL 关闭后它继续运行。

## 可安全清理的 WSL 缓存

| 路径 | 内容 | 可否清理 |
|------|------|---------|
| `~/.cache/uv/` | Python uv 包管理器缓存 | ✅ 全删 |
| `~/.cache/pip/` | pip 下载缓存 | ✅ 全删 |
| `~/.npm/_cacache/` | npm 缓存 | ✅ 全删 |
| `~/.cache/Homebrew/` | Homebrew 缓存 | ✅ 全删 |
| `~/.nvm/` | Node 版本管理 | ⚠️ 保留当前版本 |

清理命令：`rm -rf ~/.cache/{uv,pip,Homebrew,puccinialin}/ ~/.npm/_cacache/`

## 注意事项
- WSL VHDX 最大容量由 `.wslconfig` 控制，默认 1TB
- 压缩后 VHDX 会随使用重新膨胀，定期清理缓存比频繁压缩更有效
- 不要在 WSL 运行时直接操作 VHDX 文件

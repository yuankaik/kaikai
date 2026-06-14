---
name: command-line-art
description: 命令行艺术——来自 the-art-of-command-line (161K⭐) 的实战技巧。涵盖 Bash 基础、文本处理、系统调试、一行金句、SSH 远程操作。
source: https://github.com/jlevy/the-art-of-command-line
---

# 命令行艺术 (The Art of Command Line)

来自开源指南 [the-art-of-command-line](https://github.com/jlevy/the-art-of-command-line)，精选最实用的命令行技巧。

---

## Bash 基础

### 快捷键
| 按键 | 功能 |
|------|------|
| Tab | 补全命令/路径/参数 |
| Ctrl-R | 反向搜索历史 |
| Ctrl-W | 删前一个词 |
| Ctrl-U / Ctrl-K | 删到行首 / 行尾 |
| Ctrl-A / Ctrl-E | 跳到行首 / 行尾 |
| Alt-. | 循环上一个参数 |
| Ctrl-X Ctrl-E | 在 $EDITOR 中编辑当前命令 |
| Ctrl-L | 清屏 |

### 重定向
```bash
cmd > file        # 覆盖
cmd >> file       # 追加
cmd &> file       # stdout + stderr
cmd >file 2>&1    # 同上
diff <(cmd1) <(cmd2)   # 进程替换
```

### 变量扩展
```bash
${var:-default}      # 空则用默认值
${var:?error msg}    # 空则报错退出
${var%suffix}        # 去后缀
${var#prefix}        # 去前缀
```

### 花括号扩展
```bash
mv foo.{txt,pdf} some-dir     # → mv foo.txt foo.pdf some-dir
mkdir -p test-{a,b,c}/sub-{1,2,3}
```

### 严格模式
```bash
set -euo pipefail    # 遇到错误/未设变量/管道失败立即退出
set -x               # 跟踪每条命令
```

---

## 文件目录

```bash
find . -iname '*pattern*'         # 按名查找
find . -type f -ls                # 递归 ls -l
locate pattern                    # 快速查找（需 updatedb）
du -hs *                          # 磁盘占用
ncdu                              # 交互式磁盘浏览器
df -h                             # 文件系统空间
stat -c '%A %a %n' /path         # 权限（符号+八进制）
rsync -avP source/ dest/          # 多功能复制（带进度）
truncate -s 0 file                # 清空文件
```

---

## 文本处理

### grep / ripgrep
```bash
grep -i pattern file       # 忽略大小写
grep -v pattern file       # 反向匹配
grep -A 3 -B 2 pattern     # 上下文
grep -C 5 pattern          # 前后5行
rg pattern                 # ripgrep — 更快的递归搜索
```

### 集合操作（支持 GB 级文件）
```bash
sort a b | uniq > c            # 并集
sort a b | uniq -d > c         # 交集
sort a b b | uniq -u > c       # 差集
```

### JSON / YAML / CSV
```bash
jq '.' file.json                           # 美化
jq '.[] | select(.key=="value")'           # 过滤
shyaml get-value key < file.yaml           # YAML 取值
csvcut -c col1,col3 file.csv               # CSV 列提取
pandoc README.md -o output.docx            # 文档转换
```

### awk / sed
```bash
awk '{ x += $3 } END { print x }' file    # 列求和
perl -pi.bak -e 's/old/new/g' *.txt       # 原地替换
```

---

## 系统调试

### 进程
```bash
ps aux | grep proc
pgrep -f pattern               # 按名找 PID
pstree -p                      # 进程树
strace -p PID                  # 跟踪系统调用
strace -c cmd                  # 系统调用统计
```

### 系统概览
```bash
htop               # CPU/内存
free -h            # 内存
iostat -mxz 15     # 磁盘 I/O
dstat              # 综合统计
glances            # 多子系统概览
```

### 网络
```bash
ss -plat           # 监听端口
mtr host           # 更好的 traceroute
iftop / nethogs    # 按连接/进程看带宽
```

---

## SSH 远程

```bash
ssh-keygen && ssh-copy-id user@host     # 免密登录
ssh -L 8080:localhost:80 remote         # 本地端口转发
ssh -D 1080 remote                      # SOCKS 代理
```

`~/.ssh/config` 多路复用：
```
ControlMaster auto
ControlPath /tmp/%r@%h:%p
ControlPersist yes
```

---

## 一行金句

```bash
# 查看所有文件内容（带文件名）
grep . *

# 日志字段 Top-N
egrep -o 'acct_id=[0-9]+' access.log | cut -d= -f2 | sort | uniq -c | sort -rn

# 高亮监控
watch -d -n 2 'ls -rtlh | tail'

# 本地 Web 服务器
python3 -m http.server 7777

# 批量重命名 .bak → 原名
rename 's/\.bak$//' *.bak

# 快速删除巨型目录
mkdir empty && rsync -r --delete empty/ bigdir/ && rmdir bigdir empty

# 比较两个 JSON 文件
diff <(jq --sort-keys . < a.json) <(jq --sort-keys . < b.json) | colordiff | less -R
```

---

## 工具速查

| 类别 | 工具 |
|------|------|
| 搜索 | grep, rg, ag, locate, find |
| JSON/YAML | jq, shyaml, csvkit |
| 文本 | sed, awk, sort, uniq, cut, paste, tr, wc |
| 网络 | curl, wget, ss, netstat, mtr, nmap |
| 进程 | ps, htop, pstree, strace, lsof |
| 系统 | dstat, glances, iostat, vmstat, sar |
| 磁盘 | du, df, ncdu, lsblk, rsync |

---

## 专业技巧

1. **Locale 影响性能**：`export LC_ALL=C` 做字节级排序可快几个数量级
2. **安全引号**：始终引用变量 `"$FOO"`，用 `-print0` / `-0` 处理含空格文件名
3. **命令长度限制**：~128K，超限用 `find ... | xargs`
4. **ShellCheck**：用 `shellcheck` 检查脚本
5. **文档**：`man cmd`、`help cmd`、`curl cheat.sh/cmd`

*改编自 the-art-of-command-line，CC BY-SA 4.0*

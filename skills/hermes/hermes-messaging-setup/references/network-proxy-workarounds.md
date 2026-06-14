# Network Proxy Workarounds (kai哥's WSL Environment)

## Proxy Configuration
- Git proxy: `http://127.0.0.1:56666` (in `~/.gitconfig` globally)
- This proxy works for **git operations** (clone, push, pull)
- It does **NOT** work for raw HTTP downloads (curl, wget, npm, pip default)

## Workarounds by Tool

### pip install
```bash
# Use Tsinghua mirror instead of default PyPI
pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple <package>

# For long installs, run in background
pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple <package> &
```

### curl / wget
```bash
# Often times out. Use browser tools instead.
# browser_navigate → browser_console to extract content
```

### git
```bash
# Works fine with the proxy
git clone https://github.com/user/repo.git

# If timeout, try without proxy
git -c http.proxy= -c https.proxy= clone https://github.com/user/repo.git
```

### npm / bun / other HTTP tools
```bash
# Usually time out. Workarounds:
# 1. Download manually from Windows browser, place in /mnt/c/Users/admin/Desktop/
# 2. Then copy from WSL: cp /mnt/c/Users/admin/Desktop/file.tar.gz /tmp/
```

## Python Externally-Managed Environment
```bash
# System pip blocks installs. Always use:
pip install --break-system-packages <package>
# Or for venv:
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install <package>
```

## aiohttp Compatibility
- Python 3.14 removed `cgi` module
- Old user-local aiohttp (3.7.x) fails with `ModuleNotFoundError: No module named 'cgi'`
- Fix: `rm -rf ~/.local/lib/python3.14/site-packages/aiohttp*`
- System aiohttp at `/usr/lib/python3/dist-packages/` (3.13+) works fine

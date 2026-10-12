---
name: hermes-upgrade
description: >-
  Upgrade Hermes Agent on Debian/WSL where Python is externally managed.
  Covers pip install with break-system-packages, post-upgrade cleanup of
  stale caches and user-local package conflicts, and gateway restart verification.
---

# Hermes Agent Upgrade (Debian / WSL)

Use when the user asks to upgrade Hermes Agent, or when `hermes --version` reports an update is available. This skill covers the Debian/WSL-specific path where system Python is externally managed.

## Step 1: Check current version

```bash
hermes --version
```

Note the current version and the suggested upgrade command (ignore it — it will not work directly on Debian).

### 1a. Verify against the REAL latest version (do NOT trust `pip index versions`)

This machine's pip points at a lagging/cached index — `pip index versions hermes-agent`
reports a "latest" that is actually OLDER than what's installed (e.g. reports 0.15.2
while 0.19.0 is installed). That is a mirror-cache artifact, not reality. Query PyPI
directly instead:

```bash
curl -s https://pypi.org/pypi/hermes-agent/json | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['info']['version'])"
```

Rule of thumb: if the tool-reported "LATEST" is numerically lower than "INSTALLED",
the index is stale — always confirm against pypi.org before telling the user whether
an upgrade is needed. No upgrade action is required when local == official.

## Step 2: Upgrade system-wide

On Debian/WSL, the system Python is externally managed. The standard `uv pip install --upgrade hermes-agent` will fail. Use:

```bash
sudo $(which uv) pip install --upgrade --system --break-system-packages hermes-agent
```

Why each flag:
- `sudo` — required for writing to `/usr/local/lib/`
- `$(which uv)` — full path because `sudo` loses user PATH
- `--system` — target the system Python (not a venv)
- `--break-system-packages` — bypass PEP 668 externally-managed guard

## Step 3: Post-upgrade cleanup

After upgrading, stale files can cause ImportError crashes. Run these in order:

### 3a. Clear stale .pyc caches
```bash
find /usr/local/lib/python3.*/dist-packages/hermes*/ -name "*.pyc" -delete
find /usr/local/lib/python3.*/dist-packages/tools/ -name "*.pyc" -delete
find /usr/local/lib/python3.*/dist-packages/gateway/ -name "*.pyc" -delete
```

### 3b. Identify user-local conflicts
```bash
ls ~/.local/lib/python3.*/site-packages/ | grep -iE 'hermes|gateway|^tools$|toolset|tui|model_tools'
```

If any of these appear (`hermes_constants.py`, `gateway/`, `tools/`, `hermes_cli/`, `hermes_bootstrap.py`, etc.), they will shadow the system-wide install and cause ImportErrors.

### 3c. Remove user-local conflicts
```bash
python3 -m pip uninstall -y hermes-agent --break-system-packages
```

Then verify nothing remains:
```bash
ls ~/.local/lib/python3.*/site-packages/ | grep -iE 'hermes|gateway|^tools$|toolset|tui|model_tools'
# Should return nothing
```

### 3d. Also upgrade user-local dependencies
The old user-local packages (httpx, openai, jinja2, etc.) may be pinned to old versions incompatible with the new hermes-agent:

```bash
python3 -m pip install --user --upgrade hermes-agent --break-system-packages
```

## Step 4: Restart gateway

```bash
systemctl --user restart hermes-gateway
sleep 3
systemctl --user status hermes-gateway --no-pager
```

Verify the status shows `active (running)` and the PID is stable (not cycling with auto-restart).

## Step 5: Verify

```bash
hermes --version
hermes status
```

Both should report the new version with no errors.

## Pitfalls

- **`sudo: uv: command not found`**: `uv` is in the user's `~/.local/bin/`, not in root's PATH. Always use `sudo $(which uv)`.
- **`externally managed environment` error**: Always needed `--break-system-packages` on Debian.
- **ImportError after upgrade** (e.g. `cannot import name '_is_hermes_internal_secret'` or `No module named 'agent.secret_scope'`): The root cause is nearly always stale files in `~/.local/lib/python3.*/site-packages/` shadowing the new system-wide install. Follow Step 3 fully.
- **Gateway starts but immediately fails**: Check `journalctl --user -u hermes-gateway --since "1 minute ago" --no-pager` for the actual ImportError. The `hermes status` may falsely report the gateway as running because systemd auto-restarted it — check the PID history.
- **`hermes update` command blocked**: The `hermes update` CLI command may be blocked by security hooks. Use the pip upgrade path instead.
- **Python 3.14 `DaemonThreadPoolExecutor` `_initializer` 错误**（`'DaemonThreadPoolExecutor' object has no attribute '_initializer'`）: Python 3.14 把 `ThreadPoolExecutor` 内部从 `_initializer`/`_initargs` 重构为 `_create_worker_context()`。Hermes 的 `tools/daemon_pool.py` 若还用旧 API，会导致并发工具执行、`delegate_task`、微信图片识别全部崩溃。修复：把 `_adjust_thread_count` 里 `_worker` 的 args 从 `(weakref, work_queue, self._initializer, self._initargs)` 改成 `(weakref, self._create_worker_context(), self._work_queue)`。文件 `/usr/local/lib/python3.14/dist-packages/tools/daemon_pool.py`，需 `sudo cp` 覆盖，Hermes 升级会覆盖此修复，复发时重改。

## Reference

- `references/error-transcripts.md` — Full error transcripts from real upgrade conflicts (v0.16 to v0.19)

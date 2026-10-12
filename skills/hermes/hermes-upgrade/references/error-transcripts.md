# Error Transcripts: Hermes Upgrade v0.16.0 → v0.19.0

Real errors encountered during upgrade on WSL (Debian-based, Python 3.14.4).

---

## Error 1: No virtual environment

```
$ uv pip install --upgrade hermes-agent
error: No virtual environment found; run `uv venv` to create an environment,
or pass `--system` to install into a non-virtual environment
```

## Error 2: Externally managed Python

```
$ uv pip install --upgrade --system hermes-agent
error: The interpreter at /usr is externally managed, and indicates the following:
  To install Python packages system-wide, try apt install python3-xyz...
```

## Error 3: sudo loses uv PATH

```
$ sudo uv pip install --upgrade --system hermes-agent
sudo: 'uv': command not found
```

Fix: `sudo $(which uv) pip install ...`

## Error 4: Still externally managed with sudo

```
$ sudo $(which uv) pip install --upgrade --system hermes-agent
error: The interpreter at /usr is externally managed...
```

Fix: Add `--break-system-packages`

## Error 5: ImportError after upgrade (stale user-local packages)

After successful system-wide upgrade to v0.19.0, the gateway crashed:

```
ImportError: cannot import name '_is_hermes_internal_secret'
from 'tools.environments.local'
(/usr/local/lib/python3.14/dist-packages/tools/environments/local.py)
```

The function actually existed in the new install. The real cause was stale `.pyc` files.

## Error 6: ImportError (user-local hermes_constants shadowing)

After clearing .pyc, the next error:

```
ImportError: cannot import name 'get_process_hermes_home' from 'hermes_constants'
(/home/adminkaikai/.local/lib/python3.14/site-packages/hermes_constants.py)
```

Root cause: `~/.local/lib/python3.14/site-packages/` contained old hermes files
that Python loaded before the system-wide ones:

```
~/.local/lib/python3.14/site-packages/
  gateway/
  hermes_constants.py   ← old version, missing get_process_hermes_home
  hermes_logging.py
  hermes_state.py
  hermes_time.py
  hermes_bootstrap.py
  model_tools.py
  tools/
  toolsets.py
  toolset_distributions.py
  tui_gateway/
```

## Error 7: Mixed old/new version conflict

After removing some user-local files but not `hermes_cli/`:

```
ModuleNotFoundError: No module named 'agent.secret_scope'

Traceback:
  File "~/.local/.../hermes_cli/main.py"      ← OLD v0.15.2
  File "~/.local/.../hermes_cli/gateway.py"
  File "/usr/local/.../gateway/config.py"      ← NEW v0.19.0
    from agent.secret_scope import ...          ← doesn't exist in old hermes_cli
```

Root cause: `hermes_cli/` directory in user-local was v0.15.2. The new gateway tried to import from it but it lacked `agent.secret_scope`.

Fix: `python3 -m pip uninstall -y hermes-agent --break-system-packages` removed the old user-local install completely.

## Resolution checklist

After all fixes, verify:
- `ls ~/.local/lib/python3.*/site-packages/ | grep -iE 'hermes|gateway'` returns nothing
- `hermes --version` shows new version
- `hermes status` shows Gateway running with stable PID
- `systemctl --user status hermes-gateway` shows `active (running)` without auto-restart cycling

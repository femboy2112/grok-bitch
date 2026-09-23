# OpenCode adapter — grok-bitch

This directory is the thin OpenCode host layer for the canonical plugin at the
repository root. Canonical `skills/`, `agents/`, `commands/`, `scripts/` and research
content are shared; nothing is forked.

## Install

```sh
bash scripts/opencode-install.sh
python3 scripts/opencode-validate.py            # static checks
python3 scripts/opencode-validate.py --runtime  # + live host registry probes
```

Reload OpenCode (`opencode service restart`) if the plugin does not appear.

## Uninstall

```sh
bash scripts/opencode-uninstall.sh    # removes only the loader + agent symlink this repo owns
```

## What OpenCode gains

- Commands registered as `grok-bitch/<name>` (namespace-safe under simultaneous installs).
- Skills registered from the canonical directories (no content copied).
- Generated agents `grok-bitch/<name>` with closed, deny-first permissions.
- Workflow primitives composed from OpenCode Code Mode (safe; no `new Function`).
- `SubagentStop` completion hooks translated to child-session events (own children only).

See `opencode/host/TRANSLATION.md` for the semantics table and boundaries.

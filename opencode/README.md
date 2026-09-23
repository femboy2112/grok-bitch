# OpenCode adapter — grok-bitch

This directory is the thin OpenCode host layer for the canonical plugin at the
repository root. Canonical `skills/`, `agents/`, `commands/`, `scripts/` and
research content are shared; nothing is forked.

## Install

```sh
bash scripts/opencode-install.sh      # symlinks plugin (+ agents) into ~/.config/opencode/
bash scripts/opencode-validate.py     # static checks
bash scripts/opencode-validate.py --runtime   # + one live session
```

Reload OpenCode (`opencode service restart`) if the plugin does not appear.

## Uninstall

```sh
bash scripts/opencode-uninstall.sh    # removes only symlinks this repo owns
```

## What OpenCode gains

- `workflow.run` / `workflow.status` tools implementing the canonical Workflow script API.
- Registered commands and skills from the canonical directories (no content copied).
- Generated agents `grok-bitch/<name>` with translated tool permissions.
- `SubagentStop` hooks translated onto child-session completion events.
- Optional worktree-isolated parallel children and durable run receipts.

See `opencode/host/TRANSLATION.md` for the full semantics table and boundaries.

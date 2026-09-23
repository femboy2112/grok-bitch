# OpenCode adapter — grok-bitch

This directory is the thin OpenCode host layer for the canonical plugin at the
repository root. Canonical `skills/`, `agents/`, `commands/`, `scripts/` and research
content are shared; nothing is forked.

## Install

```sh
bash scripts/opencode-install.sh
python3 scripts/opencode-validate.py            # static checks
python3 scripts/opencode-validate.py --runtime  # + live host registry probes
python3 scripts/opencode-validate.py --live     # + a real Code Mode round-trip
```

Reload the host after install: `touch ~/.config/opencode/plugins/*.ts` (the loader hot-reloads),
or restart the OpenCode background service. The plugin loader file is a thin re-export;
generated agents are **copied** into `~/.config/opencode/agents/<ns>/` with model tiers
injected at install time (re-run install to refresh tiers).

## Uninstall

```sh
bash scripts/opencode-uninstall.sh    # removes only the loader + installed agent dir this repo owns
```

## What OpenCode gains

- Commands registered as `grok-bitch/<name>` (namespace-safe under simultaneous installs).
- Skills registered from the canonical directories (no content copied).
- Generated agents `grok-bitch/<name>` with closed, deny-first permissions.
- Workflow primitives composed from OpenCode Code Mode (safe; no `new Function`), including
  **host-attested** `workflow_verify` (no self-certification).
- `SubagentStop` completion hooks translated to child-session events (own children only).

See `opencode/host/TRANSLATION.md` for the semantics table and boundaries.

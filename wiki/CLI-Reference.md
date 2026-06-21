# CLI Reference

← [Wiki Home](Home.md)

`grok-bitch` is a single, **stdlib-only Python 3** script — the [cage](The-Safety-Cage.md)
the [cast](The-Cast.md) drives. This page is the complete command-line reference.

---

## Install

Put it on `PATH`:

```bash
ln -s "$PWD/grok-bitch" ~/.local/bin/grok-bitch   # or copy it
grok-bitch doctor                                  # check the environment
```

`doctor` verifies grok is installed & authed, Landlock is available, a resource enforcer
exists, git is present, and the run dir is writable.

> Installed as the [Claude Code plugin](FAQ.md#how-do-i-install-it-as-a-plugin)? The CLI
> rides along on the plugin's `bin/`, so it's already on `PATH` in-session.

---

## Subcommands

| Command | What it does |
|---------|--------------|
| `grok-bitch run <task> [opts]` | Run a caged task. The workhorse. |
| `grok-bitch doctor [--offline]` | Environment readiness check (JSON); reports the `executor plan` (grok, or the Opus fallback when grok is unavailable). |
| `grok-bitch profiles` | List safety profiles (JSON). |
| `grok-bitch selftest` | Run the hermetic fuzz/containment suite (no grok/Claude calls). |

---

## `run` options

| Option | Meaning |
|--------|---------|
| `--dir PATH` | workspace grok operates in (default: cwd) |
| `--profile NAME` | `readonly` \| `scratch` (default) \| `edit` \| `online` |
| `--guard PATH` | extra protected path (repeatable); snapshotted + reverted |
| `--no-auto-guard` | disable auto-detection of well-known protected paths |
| `--verify "CMD"` | acceptance command; run passes only if it exits 0 |
| `--timeout N` | hard wall-clock for grok (default 900s) |
| `--mem-max 4G` | hard memory ceiling for grok's **whole process tree** |
| `--cpu-max 4` | cores grok's tree may use |
| `--max-output-mb 256` | kill on output flood |
| `--no-resource-limit` | **danger:** disable mem/CPU caps |
| `--no-revert` | detect guard violations but leave them in place (still fails) |
| `--revert-all-on-fail` | on any failure, git-revert ALL changes (needs clean tree) |
| `--anchor PATH` | regression anchor: a golden-value path that must **not** drift across the run (repeatable); drift → exit 16, even if verify passed |
| `--consensus N` | run the task N independent times (reverting between) and accept only the consensus by content signature; needs a clean git tree; tree left clean, winning patch saved (never auto-applied) |
| `--dry-run` | print the plan; don't run grok |
| `--report PATH` | also write the full JSON report here |
| `--grok-bin PATH` | override the grok binary (used by the test suite) |
| `--fallback-model M` | model for the Opus fallback when grok is unavailable (default `opus`) |
| `--fallback-effort E` | effort for the fallback (`low`…`max`, default `medium`) |
| `--fallback-bin PATH` | the Claude binary for the fallback (or `GROK_BITCH_CLAUDE_BIN`) |
| `--no-fallback` | disable the fallback; fail if grok is unavailable |

---

## Profiles

| Profile | Sandbox | Tools | Web | Use |
|---------|---------|-------|-----|-----|
| `readonly` | workspace | read-only allowlist | off | analysis / review (cannot change anything) |
| `scratch` *(default)* | workspace | full | off | write scratch/output, run code |
| `edit` | workspace | full | off | modify project files (pair with `--verify`) |
| `online` | workspace | full | **on** | tasks that genuinely need the web |

All profiles OS-confine writes to the workspace and revert protected paths. Full
containment model: [The Safety Cage](The-Safety-Cage.md).

---

## Quickstart examples

```bash
# default 'scratch' profile: write scratch files / run code, confined to the dir
grok-bitch run "Write scratch/probe.py that imports foo and prints bar, run it, paste output" \
  --dir /home/leah/agi2

# edit project files, gated on the project's own test suite
grok-bitch run "Add type hints to utils.py; change nothing else" \
  --dir /repo --profile edit --verify "timeout 600 make check"

# read-only analysis (grok literally cannot write or run shell)
grok-bitch run "Summarize how the tick loop works" --dir /repo --profile readonly

# see exactly what would run, touch nothing
grok-bitch run "..." --dir /repo --dry-run

# grok missing or out of usage -> automatically runs opus/medium as Morty
grok-bitch run "…" --dir /repo --profile edit --verify "make check"
grok-bitch run "…" --no-fallback        # fail instead of falling back

# regression anchor (Time Crystal): fix the parser, but the formatter's golden
# output must NOT move — drift fails the run (exit 16) even if --verify passes
grok-bitch run "fix the parser bug" --dir /repo --profile edit \
  --verify "make test" --anchor tests/golden/formatter.out

# consensus (Council of Ricks): only trust a fix N independent attempts agree on;
# clean git tree required, tree left clean, the winning patch saved for you to apply
grok-bitch run "fix the flaky retry logic" --dir /repo --profile edit \
  --verify "make test" --consensus 3
```

Output: a JSON result on **stdout** (for the caller to parse) and a one-line human
summary + the disclaimer on **stderr**.

---

## Exit codes

| Code | Verdict | Meaning |
|------|---------|---------|
| 0 | `success` | completed; no guard violation; verify passed |
| 10 | `guard_violation` | a protected path changed (and was reverted) |
| 11 | `verify_failed` | grok's work failed the acceptance command |
| 12 | `grok_error` | grok errored (nonzero / error object / no JSON) |
| 13 | `timeout` | grok exceeded the wall-clock budget (killed) |
| 14 | `preflight_error` | bad args / environment / policy refusal |
| 15 | `resource_exceeded` | grok's tree hit the memory/output cap (killed) |
| 16 | `regression` | a regression anchor (golden value) drifted post-run (`--anchor`) |
| 17 | `no_consensus` | `--consensus` attempts did not converge on an answer |
| 130 | `interrupted` | SIGINT |

Precedence: **guard > resource > timeout > grok_error > verify > regression > success.**
(`no_consensus` is its own path — `--consensus` runs each attempt through the full
precedence above, then judges agreement across them.)

---

## JSON result (schema `grok-bitch/v1`)

```jsonc
{
  "schema": "grok-bitch/v1",
  "verdict": "success",
  "ok": true,
  "exit_code": 0,
  "profile": "scratch", "sandbox": "workspace", "web": false,
  "executor": "grok",            // or "claude-fallback" when grok is unavailable
  "fallback": {"used": false},   // when used: {used, reason, model, effort, bin}
  "guards": [{"path": ".../docs/core", "source": "auto"}],
  "guard":  {"violations": [], "reverted": [], "reverted_enabled": true},
  "changes": {"created": [...], "modified": [...], "deleted": [...]},
  "grok":   {"text": "...", "exit": 0, "duration_s": 13.6, "executor": "grok",
             "model": "grok-build", "peak_rss_mb": 180.2, "mem_max_mb": 4096,
             "cpu_cores": 4, "enforced_by": "systemd-cgroup",
             "grok_json": {"sessionId": "..."}},
  "verify": {"cmd": "make check", "passed": true, "tail": "..."},
  "anchors": {"checked": [...], "drifted": [...]},          // present with --anchor
  "consensus": {"n": 3, "threshold": 2, "agreement": 3,     // present with --consensus N
                "reached": true, "winning_patch": "...", "attempts": [...]},
  "limits": {"mem_max_mb": 4096, "cpu_max_cores": 4, "enforced_by": "systemd-cgroup"},
  "run_dir": "~/.cache/grok-bitch/runs/...",
  "disclaimer": "DISCLAIMER: You are only as smart as your dumbest model: Morty (grok). ..."
}
```

The full report (transcript, stdout/stderr, snapshots, verify log) is saved under
`run_dir`.

---

## Environment

- `GROK_BITCH_CLAUDE_BIN` — the Claude binary used for the [Opus
  fallback](The-Safety-Cage.md#the-opus-fallback--when-grok-is-unavailable) (or
  `--fallback-bin`).
- `CLAUDE_PLUGIN_ROOT` — when run as a plugin, the skill and `rick` fall back to
  `"$CLAUDE_PLUGIN_ROOT/grok-bitch"` if the plugin's `bin/` isn't on `PATH`.
- Snapshots & run dirs live under `~/.cache/grok-bitch/`.

---

## See also

- [The Safety Cage](The-Safety-Cage.md) — what every flag is actually enforcing.
- [FAQ](FAQ.md) — install, plugin, and "is this really safe" questions.

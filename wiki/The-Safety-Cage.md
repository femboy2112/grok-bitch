# The Safety Cage

← [Wiki Home](Home.md)

Everything in grok-bitch — the [cast](The-Cast.md), the [modes](Session-Modes.md), the
whole orchestrator — stands on one thing: a deterministic containment harness around an
untrusted executor. The personas are paint. **This** is the engineering.

grok is treated as an **untrusted, dim executor**. The safety guarantee does *not*
depend on grok behaving — it comes from the harness.

```
claude code ──"do this bitch work"──▶ grok-bitch ──caged grok-build──▶ work
                                          │
                                          └─▶ structured JSON verdict + exit code
```

---

## Defense in depth — the six layers

| # | Layer | What it stops | Strength |
|---|-------|---------------|----------|
| 1 | **OS sandbox** (`--sandbox workspace` + a controlling pty so Landlock actually engages) | writes outside the workspace | kernel-enforced |
| 2 | **Tool fence** (`--yolo`, web/X/`ask_user_question` disabled, read-only tool allowlist for `readonly`) | hangs on prompts, web exfil, runaway tools | hard |
| 3 | **Permission denies** (`rm -rf`, `sudo`, `git push`, `curl`/`wget`, edits to protected globs) | destructive & outward commands | friction (deny>allow) |
| 4 | **Guard + revert** (byte-snapshot protected paths, re-hash after, restore on any change) | edits to in-tree inviolable paths (`docs/core`, `canonical/`, …) | **deterministic, proven** |
| 5 | **Verify gate** (`--verify 'make check'`) | work that fails the project's own acceptance bar | hard |
| 6 | **Resource caps** (systemd cgroup `MemoryMax`+`MemorySwapMax=0`+`CPUQuota`, or a /proc tree-RSS watchdog) | OOM-ing / pegging a small shared box | kernel-enforced (cgroup) |

### Why layer 4 is the real guarantee

Landlock cannot protect a subpath of a *writable* tree, so it can't protect `docs/core`
*inside* the workspace. grok-bitch byte-snapshots every protected path before the run
and re-hashes after; **any** change fails the run (exit `10`) and the path is restored —
regardless of what grok did, how it did it, or whether the sandbox even engaged. This is
proven deterministically by the hermetic fuzz suite (see [Testing](#testing) below).

### Honest limitations

- Child-process network is **not** OS-jailed — grok's own backend needs network, and the
  network-blocking sandbox profiles sever it (grok hangs). For air-gap-sensitive work,
  rely on web-off + denied `curl`/`wget` + guard/verify, not an OS network wall.
- The OS sandbox engages only with **Landlock** (Linux ≥ 5.13) and a controlling
  terminal (the harness supplies a pty). Where it can't engage, layers 3–6 still hold.

---

## Guards — the inviolable paths

Guard sources, all unioned together:

1. **Auto-detected** well-known protected paths, if present: `docs/core`, `docs/papers`,
   `canonical`, `.git/hooks`. (Disable with `--no-auto-guard`.)
2. A **`.grok-bitch.guards`** file in the workspace — one path glob per line.
3. **`--guard PATH`** flags (repeatable).

Each guarded path is byte-snapshotted before the run. If it changes, the run is
**blocked** (exit `10`) and the path is restored from the snapshot. Snapshots live under
`~/.cache/grok-bitch/` — *outside* grok's writable set, so grok can't tamper with them.

---

## Profiles

| Profile | Sandbox | Tools | Web | Use |
|---------|---------|-------|-----|-----|
| `readonly` | workspace | read-only allowlist | off | analysis / review (cannot change anything) |
| `scratch` *(default)* | workspace | full | off | write scratch/output, run code |
| `edit` | workspace | full | off | modify project files (pair with `--verify`) |
| `online` | workspace | full | **on** | tasks that genuinely need the web |

All profiles OS-confine writes to the workspace and revert protected paths.

---

## Exit codes — branch on these

| Code | Verdict | Meaning |
|------|---------|---------|
| 0 | `success` | completed; no guard violation; verify passed |
| 10 | `guard_violation` | a protected path changed (and was reverted) |
| 11 | `verify_failed` | grok's work failed the acceptance command |
| 12 | `grok_error` | grok errored (nonzero / error object / no JSON) |
| 13 | `timeout` | grok exceeded the wall-clock budget (killed) |
| 14 | `preflight_error` | bad args / environment / policy refusal |
| 15 | `resource_exceeded` | grok's tree hit the memory/output cap (killed) |
| 130 | `interrupted` | SIGINT |

Precedence when several apply:
**guard > resource > timeout > grok_error > verify > success.** A safety breach always
surfaces.

---

## The Opus fallback — when grok is unavailable

If the `grok` binary is **not found**, or grok reports it is **out of usage** (quota /
rate-limit / auth / unavailable), grok-bitch does not hard-fail. "Morty" falls back to
**Claude (`opus`, `medium` effort by default)**, running the task through the **exact
same cage**: guard+revert, resource caps, the verify gate, and the same Morty persona.
Only the underlying model changes.

Two kinds of trigger:

- **grok binary missing** → chosen at preflight (the run starts on Claude).
- **grok runs but is out of usage** → detected from grok's own error output and
  **retried** on Claude automatically.

The result JSON reports `"executor": "claude-fallback"` and a `"fallback"` block (reason,
model, effort); `grok-bitch doctor` shows the `executor plan` and stays **READY** on the
fallback even when grok is absent.

> **Confinement caveat:** the fallback executor has **no OS sandbox** (Claude has no
> Landlock here), so out-of-workspace writes are not kernel-blocked on this path. The
> deterministic guarantees that matter — guard+revert of protected paths, resource caps,
> the verify gate, and destructive-command/tool denies — all still apply. The hermetic
> suite proves it: the fallback executor is caged exactly like grok.

Tuning lives in the [CLI Reference](CLI-Reference.md#run-options) (`--fallback-model`,
`--fallback-effort`, `--no-fallback`).

---

## Testing — the proof

```bash
grok-bitch selftest          # hermetic: adversarial scenarios, no model calls, deterministic
python3 tests/live_smoke.py  # live: real grok-build (needs auth + network)
```

The **hermetic** suite (`tests/fuzz.py` + `tests/mock_grok` + `tests/mock_claude`) is the
deterministic proof. It replaces the executor with a controllable fake that performs the
worst things a model could do — edit/delete/create-under a protected path, hang, OOM the
box (tested against **both** the cgroup and the watchdog), flood output, crash, emit
garbage — and asserts the harness returns the correct verdict and leaves every protected
path byte-identical, every time. Four scenarios cover the **Opus fallback**: that
grok-missing and grok-out-of-usage both fall back to Claude, that the fallback executor
is caged exactly like grok, and that `--no-fallback` refuses rather than substituting
silently.

The **live** suite confirms what only a real model exercises: Landlock blocking
out-of-workspace writes, the Morty persona, and end-to-end wiring (including a live
fallback run).

---

## See also

- [CLI Reference](CLI-Reference.md) — every option and the full JSON schema.
- [The Cast](The-Cast.md) — `morty` and `rick` are the subagents that *drive* this cage.
- [The Iron Rule](The-Iron-Rule.md) — why the persona voice never reaches the facts.

---
name: grok-bitch
description: Delegate mechanical, well-specified, verifiable grunt work to grok (the grok-build model) instead of spending Claude's rigor on it. Use when the task is boring but checkable — writing/running scratch probes, bulk numeric sweeps, mechanical refactors, adding type hints or docstrings, generating test fixtures, running an existing test suite and pasting output, repetitive edits across files, boilerplate. grok runs caged (OS sandbox, hard resource caps so it can't OOM the box, auto-reverted protected paths, a verify gate) and returns a structured JSON verdict on stdout with a stable exit code. Do NOT use it for judgment, novel design, proofs, the final certification/verdict, or touching inviolable state — those stay with Claude. grok is dumb and untrusted; always re-check its output.
allowed-tools: Bash(grok-bitch:*)
---

# grok-bitch — hand grunt work to a caged grok

`grok-bitch` is a safe, deterministic harness that lets you (Claude) offload
**mechanical, well-specified, verifiable** labor to grok (`grok-build`) so you
don't burn your own rigor on it. grok is treated as an **untrusted, dim
executor**: the safety guarantee comes from the harness, not from grok behaving.

**The CLI is `grok-bitch`** (this plugin puts it on `PATH`). If a shell ever
reports `grok-bitch: command not found`, fall back to `"$CLAUDE_PLUGIN_ROOT/grok-bitch"`.

> grok is the bitch. **You** are accountable for the result. Every run prints a
> disclaimer to that effect — relay it, and verify grok's work yourself.

## Two ways to use it

1. **The `rick` subagent (preferred for anything non-trivial).** Delegate to the
   **Rick** subagent — the 300-IQ handler who bosses grok (**Morty**) around. In an
   **isolated context**, Rick decomposes the goal into bounded steps, cradles Morty
   through them, adapts dynamically to every error (per the exit-code playbook),
   **never trusts Morty's word** (he independently verifies what Morty claims), and
   returns only a clean, verified verdict — keeping Morty's noisy transcript out of
   your main conversation. Hand Rick the goal, the workspace dir, and a `--verify`
   command if you have one. (Naming: the handler that *drives* grok is **Rick**;
   grok itself, running caged through the plugin, is **Morty**.)

> **Naming discipline — "Morty" is grok, only ever grok.** The **user is never
> Morty**, and neither are you. Whether you're dispatching the Rick subagent,
> relaying Rick's voiced report back up, or slipping into a Rick voice yourself
> when you call the CLI directly, you never address *the user* as Morty and never
> tack "Morty" onto a sentence aimed at them. That pet name belongs exclusively to
> the dim, caged executor — grok. When you talk *to* the user, just talk.
2. **Call the CLI directly** for quick, one-shot handoffs where you want the JSON
   inline:

```bash
grok-bitch run "<one precise, self-contained task>" --dir <workspace> \
  [--profile readonly|scratch|edit|online] [--verify "CMD"] --quiet
```

Parse **stdout** as JSON. Branch on the **exit code**.

## When to delegate (and when NOT to)

**Delegate:** scratch probes, bulk numeric grids/sweeps, mechanical refactors,
adding type hints / docstrings, generating test fixtures, running an existing
suite and pasting the output, repetitive edits across many files, boilerplate.

**Do NOT delegate:** anything needing judgment, novel design, proofs, the actual
certification/verdict, or touching inviolable state. Those are yours. A vague
task makes grok do the wrong thing confidently — be specific and bounded.

## Pick a profile

| Profile | What grok can do | Use |
|---------|------------------|-----|
| `readonly` | read & report only; cannot write or run shell | "look at / summarize X" |
| `scratch` *(default)* | write scratch files & run code, confined to `--dir` | probes, numerics, codegen |
| `edit` | modify project files (confined) — **always pair with `--verify`** | mechanical edits |
| `online` | full tools **+ web** | only when the task truly needs the web |

All profiles OS-confine writes to the workspace and auto-revert protected paths.

## Branch on the exit code

| Code | Verdict | What it means / what to do |
|------|---------|----------------------------|
| 0 | `success` | completed; no guard violation; verify passed → **use it, then double-check** |
| 10 | `guard_violation` | grok touched an inviolable path; it was **reverted**. Do NOT retry blindly — investigate. |
| 11 | `verify_failed` | grok's work failed the gate. Read `verify.tail`; fix the task or do it yourself. |
| 12 | `grok_error` | grok broke (nonzero / no JSON). Read `grok.stderr_tail`. |
| 13 | `timeout` | too big / stuck. Narrow it or raise `--timeout`. |
| 14 | `preflight_error` | bad args/env/policy. Read `error`. |
| 15 | `resource_exceeded` | grok tried to OOM/flood the box; killed. Narrow the task. |
| 130 | `interrupted` | SIGINT. |

Precedence when several apply: **guard > resource > timeout > grok_error > verify > success.**
A safety breach always surfaces.

```bash
out=$(grok-bitch run "..." --dir /repo --profile edit --verify "make check" --quiet); rc=$?
verdict=$(echo "$out" | jq -r .verdict)
[ "$rc" -eq 0 ] && echo "$out" | jq -r '.changes'   # review what changed, then verify yourself
```

## Protected paths are automatic

`docs/core`, `docs/papers`, `canonical/`, `.git/hooks` are auto-guarded if
present. Add more with `--guard PATH` (repeatable) or a `.grok-bitch.guards`
file in the repo. Anything guarded that changes → the run fails (exit 10) and is
reverted from a byte-snapshot. You never have to trust grok to respect them.

## Resource caps are on by default (it WILL OOM the box otherwise)

grok's whole process tree is capped (default **4 GB / 4 cores, swap disabled**)
via a kernel cgroup, with a `/proc` watchdog fallback. If a legitimate
`--verify` needs more memory, raise `--mem-max`. **Never** pass
`--no-resource-limit` on a shared box.

## Key `run` options

`--dir PATH` · `--profile NAME` · `--verify "CMD"` · `--verify-timeout N` ·
`--guard PATH` (repeatable) · `--no-auto-guard` · `--timeout N` (default 900s) ·
`--max-turns N` · `--mem-max 4G` · `--cpu-max 4` · `--max-output-mb 256` ·
`--no-revert` · `--revert-all-on-fail` · `--dry-run` · `--report PATH` ·
`--quiet` (suppress the human summary on stderr — recommended when parsing JSON).

## Pre-flight

Run `grok-bitch doctor --quiet` once per session if unsure — it returns JSON
with `ready: true/false` (checks grok is installed+authed, Landlock available, a
resource enforcer exists, git present, run dir writable) and an `executor_plan`.
`grok-bitch profiles` lists the profiles; `grok-bitch selftest` runs the hermetic
containment suite.

## If grok is down, it still works (Opus fallback)

If grok is **missing** or **out of usage**, Morty automatically falls back to
**Claude `opus`/`medium`**, run through the *same* cage (guard+revert, resource
caps, verify, persona). The result JSON shows `"executor": "claude-fallback"` and
a `"fallback"` block. You don't have to do anything; tune with `--fallback-model`
/ `--fallback-effort`, or `--no-fallback` to fail instead. (Caveat: the fallback
path has no OS sandbox, so rely on guard/verify, not an OS write-wall, there.)

## The persona & the disclaimer

grok is instructed to talk — and to comment its code — in the anxious,
self-doubting voice of Morty (a deliberate subjugation), while keeping all
**executable substance exactly correct**. Every run prints, and embeds in the
JSON as `disclaimer`:

> DISCLAIMER: You are only as smart as your dumbest model: grok. Please double check the work.

Surface that to the user and **verify grok's output before relying on it.**

## Examples

```bash
# Throwaway probe (docs/core & docs/papers auto-guarded if present)
grok-bitch run "Create scratch/rank_probe.py that loads the encoder, prints output \
eff-rank over 50 steps; run it; paste the numbers. Touch nothing else." \
  --dir /home/leah/agi2 --profile scratch --quiet

# Mechanical edit gated on the real CI
grok-bitch run "Add a boundedness regression test for the new cache cap in \
agi/language/lexicon.py, mirroring the existing ones. Additive only." \
  --dir /home/leah/agi2 --profile edit --verify "timeout 600 make check" --quiet

# Bulk numerics (canonical/ auto-guarded; exact-arith discipline is yours to state)
grok-bitch run "Run tools/spectral.py for r=2 over the t-grid in scratch/grid.json, \
write results to scratch/out.json. Do not edit anything under canonical/." \
  --dir /home/leah/Collatz/C --profile scratch --verify "python3 tools/anchors.py" --quiet
```

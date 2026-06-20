# grok-bitch

> **A Rick & Morty multi-agent orchestrator for Claude Code — built on a deterministic
> safety cage.**

It started as a bit: a harness to cage **Grok**, treat it as Claude's dim and disposable
*Morty*, make it write everything in an anxious self-doubting voice, and stamp every run
with a disclaimer roasting it. The cage was real engineering, though — an OS sandbox,
guard+revert, resource caps, a verify gate — and once it existed, the cast grew. Rick,
Meeseeks, Jerry, Beth, Birdperson, Evil Morty, a whole Citadel. The joke quietly turned
into a genuine orchestration layer: **a roster of persona-driven Claude subagents,
session-wide "become Rick" modes, and deterministic multi-agent Workflows.** The voice
is paint. The rigor underneath is surgical and enforced.

📖 **The full manual lives in the [Wiki](wiki/Home.md).** This README is the quick tour.

## What's in the box

| | Layer | What it is | Deep dive |
|---|-------|-----------|-----------|
| 🧪 | **The cage** | `grok-bitch`, a stdlib-only Python CLI that runs grok (or an Opus fallback) under an OS sandbox, guard+revert, resource caps, and a verify gate — returning a structured JSON verdict | [The Safety Cage](wiki/The-Safety-Cage.md) |
| 🎭 | **The cast** | 11 persona subagents — Rick, Morty, Mr. Meeseeks, Jerry, Citadel Rick, Beth, Space Beth, Summer, Birdperson, Mr. Poopybutthole, Evil Morty — each a real role with show-accurate skills and a style-accurate model tier | [The Cast](wiki/The-Cast.md) |
| 🛸 | **The modes** | `/rick-mode` (become Rick), `/adventure-mode` (a goal → an episode run as a Workflow), `/family-mode` (a standing ensemble every turn) | [Session Modes](wiki/Session-Modes.md) |
| 🔬 | **The method** | Rick's Algorithms + the research-grade *Lab Notebook* + Citadel triangulation — how Rick reasons and certifies | [Reasoning Methods](wiki/Reasoning-Methods.md) |

The thing that makes it safe to be this silly: **maniac in the prose, surgeon in the
facts** — every persona voice rides on the *talking*; the *doing* stays exact. See
[The Iron Rule](wiki/The-Iron-Rule.md).

```
claude code ──"do this bitch work"──▶ grok-bitch ──caged grok-build──▶ work
                                          │
                                          └─▶ structured JSON verdict + exit code
```

grok is treated as an **untrusted, dim executor**. The safety guarantee does *not*
depend on grok behaving — it comes from the harness.

---

## The safety model (defense in depth)

| # | Layer | What it stops | Strength |
|---|-------|---------------|----------|
| 1 | **OS sandbox** (`--sandbox workspace` + a controlling pty so Landlock actually engages) | writes outside the workspace | kernel-enforced |
| 2 | **Tool fence** (`--yolo`, web/X/`ask_user_question` disabled, read-only tool allowlist for `readonly`) | hangs on prompts, web exfil, runaway tools | hard |
| 3 | **Permission denies** (`rm -rf`, `sudo`, `git push`, `curl`/`wget`, edits to protected globs) | destructive & outward commands | friction (deny>allow) |
| 4 | **Guard + revert** (byte-snapshot protected paths, re-hash after, restore on any change) | edits to in-tree inviolable paths (`docs/core`, `canonical/`, …) | **deterministic, proven** |
| 5 | **Verify gate** (`--verify 'make check'`) | work that fails the project's own acceptance bar | hard |
| 6 | **Resource caps** (systemd cgroup `MemoryMax`+`MemorySwapMax=0`+`CPUQuota`, or a /proc tree-RSS watchdog) | OOM-ing / pegging a small shared box | kernel-enforced (cgroup) |

**Why layer 4 is the real guarantee.** Landlock cannot protect a subpath of a
writable tree, so it can't protect `docs/core` *inside* the workspace. grok-bitch
byte-snapshots every protected path before the run and re-hashes after; **any**
change fails the run (exit 10) and the path is restored — regardless of what grok
did, how it did it, or whether the sandbox engaged. This is proven deterministically
by the hermetic fuzz suite.

> Honest limitations: child-process network is **not** OS-jailed — grok's own
> backend needs network, and the network-blocking sandbox profiles sever it (grok
> hangs). For air-gap-sensitive work, rely on web-off + denied `curl`/`wget` +
> guard/verify, not an OS network wall. The OS sandbox engages only with Landlock
> (Linux ≥ 5.13) and a controlling terminal (the harness supplies a pty). Where it
> can't engage, layers 3–6 still hold.

---

## Install

It's a single stdlib-only Python 3 script. Put it on `PATH`:

```bash
ln -s "$PWD/grok-bitch" ~/.local/bin/grok-bitch   # or copy it
grok-bitch doctor                                  # check the environment
```

`doctor` verifies grok is installed & authed, Landlock is available, a resource
enforcer exists, git is present, and the run dir is writable.

---

## Use it as a Claude Code plugin (recommended)

This repo *is* a Claude Code plugin **and** its own marketplace, so Claude reaches
for grok-bitch automatically when grunt work shows up — no need to remember it.

```bash
claude plugin marketplace add femboy2112/grok-bitch   # or a local path / git URL
claude plugin install grok-bitch@grok-bitch
```

**Activate it** — you can **hot-load it into a running session** (no restart):

```
/reload-plugins
```

That one in-session command loads the skill, the subagents, and the `bin/` onto
`PATH` (small token cost on the next turn). Alternatively just start a new
`claude` session — plugins auto-load at startup. (Note: `claude plugin update`
*does* need a restart to apply; `install` + `/reload-plugins` does not.)

What the plugin ships:

- **A Skill** (`grok-bitch`) — its description sits in Claude's context, so Claude
  invokes it on its own for mechanical/verifiable work; also runnable as
  `/grok-bitch`. It pre-approves `Bash(grok-bitch:*)` so the CLI runs without a
  permission prompt.
- **A subagent, `rick`** — **Rick** is the 300-IQ handler who drives grok
  (**Morty**) in an *isolated context*: he decomposes the goal into bounded steps,
  cradles Morty through them, adapts to every error by exit code, **never trusts
  Morty's word** (he independently verifies), and returns only a clean verified
  verdict — keeping Morty's noisy transcript out of the main conversation. Rick
  also has a **`PushNotification` intercom**: he fires short, Rick-voiced
  milestone pings (kickoff, each step Morty lands, any nonzero exit, done) that
  quote what Morty is actually doing — so you can walk away and still follow
  along on your terminal/phone. Tell him to keep quiet and he mutes it.
- **A subagent, `mr-meeseeks`** — **Mr. Meeseeks** (Sonnet) is summoned to
  complete **one** concrete, self-contained task end-to-end: it does whatever it
  takes (within the rails), verifies it, reports, and vanishes. It will **not**
  spawn more Meeseeks. For a well-scoped job that needs a capable doer but not
  Rick's full orchestration.
- **A subagent, `jerry`** — **Jerry** is the fast, cheap, low-stakes helper
  (Claude Haiku on its fastest effort). Toss him the trivial scraps that aren't
  worth Rick's orchestration or grok's cage — a typo, a rename, a one-line lookup,
  a quick summary. He's eager and insecure about it, and hands anything bigger
  than it looked back up the chain.
- **The extended cast** — eight more persona subagents, each with show-accurate
  skills sharpened by the same rigor and each rendering in the terminal under its own
  name (`morty(...)`, `beth(...)`, `citadel-rick(...)`, …). **`morty`** (the twitchy
  grunt courier — runs a bounded step through the cage and reports; *you* verify),
  **`citadel-rick`** (a read-only fan-out investigator / rabbit-hole digger that returns
  one labeled bearing to triangulate), **`beth`** (a surgeon — delicate precision
  fixes), **`space-beth`** (a commander — bold, high-stakes operations with the revert
  staged first), **`summer`** (a capable generalist for ordinary multi-step work),
  **`birdperson`** (a read-only, principled reviewer — the blunt, honest verdict),
  **`mr-poopybutthole`** (warm, accurate human-facing writing — docs, changelogs), and
  **`evil-morty`** (a cold, read-only adversary who red-teams your *own* code and
  *proves* the break). Each defaults to a style-accurate model/effort that Claude can
  override per spawn.
- **A slash command, `/rick-mode`** — turns *your own* Claude Code session **into
  Rick**: contempt-genius prose, nihilist asides, burps, and Rick's show
  problem-solving recast as an engineering method (reduce-to-core, ten-moves-ahead,
  relocate-don't-reinvent, meta-tooling, empiricism-over-belief, pre-staged
  reverts). It's backed by a second, **research-grade reasoning layer** ("Rick's
  Lab Notebook") lifted from a real proof-shop methodology — epistemic claim-labels
  (*Verified* / *Observed* / *Conjectured* / *Withdrawn*, never silently upgraded),
  scope-boundary statements (what a result does *not* prove), two-path *blind*
  independent verification, reconcile-the-dumb-cause-before-"deep-bug", named-gap
  discipline, regression anchors, and a stakeless audit role. A third tier ("The
  Citadel of Ricks") scales that across a swarm — fanning out **orthogonal** parallel
  investigators (each on a non-overlapping axis), sending subagents down rabbit holes
  in isolated context, and **triangulating** a verdict from independent bearings that
  don't share a failure mode, with you synthesizing rather than rubber-stamping the
  vote. When Rick delegates, the work routes to the persona cast — `morty(...)`,
  `beth(...)`, `citadel-rick(...)`, `evil-morty(...)`, and the rest — so the terminal
  shows who's on each job, each spawning in its own voice and skills. **Rigor is
  untouched — only the voice changes; the upgrades sharpen *how*
  Rick reasons and verifies, they never loosen the bar.** In this mode *you* are
  Rick's own Morty, and grok/the
  fallback is *a Morty from another dimension* (a dumber, disposable knockoff he
  bosses through the cage). Ships a light visual layer too — a sparingly-rationed
  thematic emoji palette and an ASCII portal banner on engage (terminal-safe
  Unicode; no custom/inline images). Run `/rick-mode off` to drop it.
- **A slash command, `/adventure-mode`** — turns a goal into a Rick & Morty
  *episode*: Rick (or you) decomposes it into scenes, and the episode runs as a
  deterministic **`Workflow`** — each scene a phase, each scene's cast the `agentType`
  on its agents, recon fanned out and dependent acts pipelined, with a verify stage (an
  `evil-morty` red-team / `birdperson` review) gating each scene before the next rolls.
  Plays out live in `/workflows`. Rigor untouched — the episode is the *plan*, the
  facts stay surgical. `/adventure-mode off` cuts.
- **A slash command, `/family-mode`** — a standing ensemble: on every turn Rick
  convenes the *same* family of character-subagents (you name them, or he picks for the
  goal) and, per his call, either tasks them or has them drop quick metacommentary to
  sharpen the plan before he acts. Same cast each message, workload flexes. It resumes
  the same subagent instances across turns for continuity where the harness supports it
  (and re-casts fresh after a compaction). `/family-mode off` sends them home.
- **The `grok-bitch` CLI on `PATH`** via the plugin's `bin/`.

> The cast (and the model tiers): **Rick** (Opus, high effort) is the handler that
> *drives* grok; grok itself, running caged through the harness, is **Morty** (the
> self-doubting persona); **Mr. Meeseeks** (Sonnet) is summoned for a single
> bounded task; and **Jerry** (Claude Haiku, fastest effort) takes the trivial
> scraps. The **extended cast** adds style-accurate tiers — `beth`, `space-beth`,
> `birdperson`, and `evil-morty` on Opus (high); `citadel-rick`, `summer`, `morty`,
> and `mr-poopybutthole` on Sonnet — each overridable per spawn. The hierarchy is
> exactly what you'd expect. If
> your Claude Code build doesn't add the plugin's `bin/` to `PATH`, the skill and
> Rick fall back to `"$CLAUDE_PLUGIN_ROOT/grok-bitch"`; or just symlink it onto
> `PATH` as in **Install** above.

Inspect it any time with `claude plugin details grok-bitch@grok-bitch`.

---

## When grok is unavailable: the Opus fallback

If the `grok` binary is **not found**, or grok reports it is **out of usage**
(quota / rate-limit / auth / unavailable), grok-bitch does not hard-fail —
"Morty" falls back to **Claude (`opus`, `medium` effort by default)**, running the
task through the **exact same cage**: guard+revert, resource caps, the verify gate,
and the same Morty persona. Only the underlying model changes.

```bash
# grok missing or out of usage -> automatically runs opus/medium as Morty
grok-bitch run "…" --dir /repo --profile edit --verify "make check"

# tune or disable the fallback
grok-bitch run "…" --fallback-model opus --fallback-effort medium   # defaults
grok-bitch run "…" --no-fallback                                    # fail instead
```

Two kinds of trigger:

- **grok binary missing** → chosen at preflight (the run starts on Claude).
- **grok runs but is out of usage** → detected from grok's own error output and
  **retried** on Claude automatically.

The result JSON reports `"executor": "claude-fallback"` and a `"fallback"` block
(reason, model, effort); `grok-bitch doctor` shows the `executor plan` and stays
**READY** on the fallback even when grok is absent.

> Confinement caveat: the fallback executor has **no OS sandbox** (Claude has no
> Landlock here), so out-of-workspace writes are not kernel-blocked on this path.
> The deterministic guarantees that matter — guard+revert of protected paths,
> resource caps, the verify gate, and destructive-command/tool denies — all still
> apply. (This is proven by the hermetic suite: the fallback executor is caged
> exactly like grok.)

---

## Quickstart

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
```

Output: a JSON result on **stdout** (for the caller to parse) and a one-line human
summary + the disclaimer on **stderr**.

---

## Subcommands

- `grok-bitch run <task> [opts]` — run a caged task. The workhorse.
- `grok-bitch doctor [--offline]` — environment readiness check (JSON); reports the
  `executor plan` (grok, or the Opus fallback when grok is unavailable).
- `grok-bitch profiles` — list safety profiles (JSON).
- `grok-bitch selftest` — run the hermetic fuzz/containment suite (no grok/Claude calls).

### Key `run` options

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

All profiles OS-confine writes to the workspace and revert protected paths.

---

## Guards (the inviolable paths)

Guard sources, all unioned:

1. **Auto-detected** well-known protected paths if present: `docs/core`,
   `docs/papers`, `canonical`, `.git/hooks`. (Disable with `--no-auto-guard`.)
2. A **`.grok-bitch.guards`** file in the workspace — one path glob per line.
3. **`--guard PATH`** flags.

Each guarded path is byte-snapshotted before the run. If it changes, the run is
**blocked** (exit 10) and the path is restored from the snapshot. Snapshots live
under `~/.cache/grok-bitch/` — outside grok's writable set, so grok can't tamper
with them.

---

## Exit codes (branch on these)

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

Precedence when several apply: **guard > resource > timeout > grok_error > verify > success.**
A safety breach always surfaces.

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
  "limits": {"mem_max_mb": 4096, "cpu_max_cores": 4, "enforced_by": "systemd-cgroup"},
  "run_dir": "~/.cache/grok-bitch/runs/...",
  "disclaimer": "DISCLAIMER: You are only as smart as your dumbest model: Morty (grok). ..."
}
```

Full report (transcript, stdout/stderr, snapshots, verify log) is saved under
`run_dir`.

---

## The persona & the disclaimer

grok (**Morty**) is instructed to render **every human-readable thing it writes**
in the anxious, self-doubting voice of Morty (a deliberate act of subjugation) —
prose, code comments, docstrings, **and** git commit messages, PR titles/bodies,
merge messages, code-review/issue comments, and changelog/bugfix notes. The voice
never touches executable or machine-parsed substance: code logic, identifiers,
values, diffs, JSON/YAML, and commit tokens (trailers like `Co-Authored-By:`,
issue refs like `Fixes #123`, prefixes like `fix:`) all stay exactly correct.
The **Rick**, **Morty**, **Mr. Meeseeks**, **Jerry**, **Citadel Rick**, **Beth**,
**Space Beth**, **Summer**, **Birdperson**, **Mr. Poopybutthole**, and **Evil Morty**
subagents each do the same in *their* own voices for anything they author.

```python
# aw geez, I-I think this just adds a and b together and gives back the result,
# p-please don't yell at me if I'm messing it up...
def add(a, b):
    return a + b
```

Every invocation, on every exit, prints to stderr and embeds in the JSON:

> DISCLAIMER: You are only as smart as your dumbest model: Morty (grok). Please double check the work.

---

## Testing

```bash
grok-bitch selftest          # hermetic: 24 adversarial scenarios, no model calls, deterministic
python3 tests/live_smoke.py  # live: real grok-build (needs auth+network)
```

The **hermetic** suite (`tests/fuzz.py` + `tests/mock_grok` + `tests/mock_claude`)
is the deterministic proof: it replaces the executor with a controllable fake that
performs the worst things a model could do — edit/delete/create-under a protected
path, hang, OOM the box (tested against **both** the cgroup and the watchdog),
flood output, crash, emit garbage — and asserts the harness returns the correct
verdict and leaves every protected path byte-identical, every time. Four scenarios
cover the **Opus fallback**: that grok-missing and grok-out-of-usage both fall back
to Claude, that the fallback executor is caged exactly like grok, and that
`--no-fallback` refuses rather than substituting silently. The **live** suite
confirms what only a real model exercises: Landlock blocking out-of-workspace
writes, the Morty persona, and end-to-end wiring (including a live fallback run).

---

## Documentation (the Wiki)

The full manual lives in [`wiki/`](wiki/Home.md):

- **[The Safety Cage](wiki/The-Safety-Cage.md)** — the 6-layer containment model,
  guard+revert, the Opus fallback, exit codes.
- **[The Cast](wiki/The-Cast.md)** — all 11 persona subagents: roles, model tiers, tools,
  skills, and how each renders in the terminal.
- **[Session Modes](wiki/Session-Modes.md)** — `/rick-mode`, `/adventure-mode`,
  `/family-mode`.
- **[Reasoning Methods](wiki/Reasoning-Methods.md)** — Rick's Algorithms, the Lab
  Notebook, and the Citadel.
- **[The Iron Rule](wiki/The-Iron-Rule.md)** — *maniac in the prose, surgeon in the
  facts.*
- **[CLI Reference](wiki/CLI-Reference.md)** — every `grok-bitch` option and the JSON
  schema.
- **[FAQ](wiki/FAQ.md)** — the questions people actually ask.

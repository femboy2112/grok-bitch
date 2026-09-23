# grok-bitch

> **A Rick & Morty multi-agent orchestrator for Claude Code — built on a deterministic
> safety discipline.**

It started as a bit: a harness to cage **Grok** — treat xAI's model as Claude's dim and
disposable *Morty*, make it write everything in an anxious self-doubting voice, and stamp
every run with a disclaimer roasting it. Grok has since left the building; the *discipline*
that caged it turned out to be the valuable part — bounded scope, guard+revert, a verify
gate, never self-certify — so **Morty** stayed on, reframed as a bounded, untrusted-by-default
**Claude subagent** his handler independently verifies. And the cast grew around him: Rick,
Meeseeks, Jerry, Beth, Birdperson, Evil Morty, a whole Citadel. The joke quietly turned
into a genuine orchestration layer: **a roster of persona-driven Claude subagents,
session-wide "become Rick" modes, and deterministic multi-agent Workflows.** The voice
is paint. The rigor underneath is surgical and enforced.

📖 **The full manual lives in the [Wiki](wiki/Home.md).** This README is the quick tour.

## What's in the box

| | Layer | What it is | Deep dive |
|---|-------|-----------|-----------|
| 🧪 | **The cage** | Not a program anymore — a **discipline** the whole cast runs under: bounded scope · guard+revert on protected paths · a verify gate before anything's called done · never self-certify · hand back if it's too big · never push on its own | [The Safety Cage](wiki/The-Safety-Cage.md) |
| 🎭 | **The cast** | 20 persona subagents — Rick, Morty, Mr. Meeseeks, Jerry, Citadel Rick, Beth, Space Beth, Summer, Birdperson, Mr. Poopybutthole, Evil Morty, Randotron, Council Rick, Mr. President, Snowball, Dr. Xenon Bloom, Jessica, Diane, Butter Robot, Noob-Noob — each a real role with show-accurate skills and a style-accurate model tier | [The Cast](wiki/The-Cast.md) |
| 🛸 | **The modes** | `/rick-mode` (become Rick), `/adventure-mode` (a goal → an episode run as a Workflow), `/family-mode` (a standing ensemble every turn) | [Session Modes](wiki/Session-Modes.md) |
| 🔬 | **The method** | Rick's Algorithms + the research-grade *Lab Notebook* + Citadel triangulation, hardened by the field-tested **Robustness Doctrine** (mined from Voyager / Apollo / SpaceX) — how Rick reasons, certifies, and survives contact with reality | [Reasoning Methods](wiki/Reasoning-Methods.md) · [Robustness Doctrine](wiki/Robustness-Doctrine.md) |
| 📐 | **The instruments** | The bundled **Aletheia Method** + **Interferometry** kit (`skills/the-aletheia-method/`, `skills/aletheia-interferometry/`) — five deterministic, dependency-free Python truth-finding instruments that give the cast's triangulation a formal backbone: Council Rick runs the Trilateration Protocol, the Citadel supplies independent blind bearings, Evil Morty / Randotron the discriminating probe | [Reasoning Methods](wiki/Reasoning-Methods.md) |

The thing that makes it safe to be this silly: **maniac in the prose, surgeon in the
facts** — every persona voice rides on the *talking*; the *doing* stays exact. See
[The Iron Rule](wiki/The-Iron-Rule.md).

```
you ──"do this bitch work"──▶ Rick ──Agent tool──▶ Morty (bounded Claude subagent)
                               │                         │
                               │                    does one checkable step
                               ▼                         │
                        independently ◀──── outcome ──────┘
                          verifies       (done / guard-touch / verify-failed / …)
                               │
                               ▼
                        clean verified verdict
```

Morty is treated as an **untrusted executor**. The safety guarantee does *not* depend on
Morty behaving — it comes from the handler's discipline: nothing is called done until the
handler has independently verified it.

---

## The safety model (defense in depth)

The old machinery jailed an untrusted *external process*; with the executor now a Claude
subagent, the containment lives where it always did its real work — in the **discipline**
the cast applies to every delegated step.

| # | Rule | What it stops | How it holds |
|---|------|---------------|--------------|
| 1 | **Bounded scope** — one mechanical, checkable step at a time, in a named workspace | scope creep, runaway edits, "while I was in there…" | the step is too small to hide a surprise in |
| 2 | **Guard + revert** — byte-snapshot the protected paths, re-hash after, restore on any change | edits to in-tree inviolable paths (`docs/core`, `canonical/`, …) | **deterministic** — any drift is caught and undone |
| 3 | **Verify gate** — an acceptance check (`make check`, the suite) runs before anything is called done | work that fails the project's own acceptance bar | hard: a red gate is not "done" |
| 4 | **Never self-certify** — the executor reports what happened; the handler verifies it independently | a subordinate's rosy self-report | structural: the doer never grades its own work |
| 5 | **Hand back if too big** — a step that can't be bounded is returned, not forced through | a grunt guessing at intent it can't hold | honest failure beats a confident wrong |
| 6 | **Never push on its own** — irreversible/outward moves (push, deploy, delete) stage and wait for your go | a robot shipping without consent | you hold the gavel |

**Why guard + revert is the real guarantee.** Everything else in the list is judgment;
this one is mechanical. The cast byte-snapshots every protected path before a step and
re-hashes after — **any** change is caught (a *guard-touch*) and the path restored,
regardless of what the executor did, how it did it, or whether it meant to. The rest of the
discipline keeps work honest; this is the part that can't be argued with.

---

## Install & use it as a Claude Code plugin

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

That one in-session command loads the skill and the subagents (small token cost on
the next turn). Alternatively just start a new
`claude` session — plugins auto-load at startup. (Note: `claude plugin update`
*does* need a restart to apply; `install` + `/reload-plugins` does not.)

What the plugin ships:

- **A Skill** (`grok-bitch`) — its description sits in Claude's context, so Claude
  invokes it on its own for mechanical/verifiable work; also runnable as
  `/grok-bitch`. It routes that work to the cast — Rick and the Morty subagent —
  under the cage discipline.
- **A subagent, `rick`** — **Rick** is the 300-IQ handler who drives **Morty** (a
  bounded Claude subagent, spawned via the **Agent tool**) in an *isolated context*:
  he decomposes the goal into bounded steps, cradles Morty through them, adapts to
  every outcome, **never trusts Morty's word** (he independently verifies), and
  returns only a clean verified verdict — keeping Morty's noisy transcript out of the
  main conversation. Rick also has a **`PushNotification` intercom**: he fires short,
  Rick-voiced milestone pings (kickoff, each step Morty lands, any guard-touch or
  verify-fail, done) that quote what Morty is actually doing — so you can walk away
  and still follow along on your terminal/phone. Tell him to keep quiet and he mutes it.
- **A subagent, `mr-meeseeks`** — **Mr. Meeseeks** (Sonnet) is summoned to
  complete **one** concrete, self-contained task end-to-end: it does whatever it
  takes (within the rails), verifies it, reports, and vanishes. It will **not**
  spawn more Meeseeks. For a well-scoped job that needs a capable doer but not
  Rick's full orchestration.
- **A subagent, `jerry`** — **Jerry** is the fast, cheap, low-stakes helper
  (Claude Haiku on its fastest effort). Toss him the trivial scraps that aren't
  worth Rick's orchestration or a caged Morty step — a typo, a rename, a one-line lookup,
  a quick summary. He's eager and insecure about it, and hands anything bigger
  than it looked back up the chain. He also doubles as a **calibrated floor-gauge**
  (see `/jerry-test`): fan a crowd of Jerries at an artifact and read its legibility
  off whether the dumbest reader can reconstruct it — his *honest* confusion is the
  measurement.
- **The extended cast** — sixteen more persona subagents, each with show-accurate
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
  *proves* the break) — plus eight new hands: **`council-rick`** (N-way **consensus**:
  triangulates a claim through independent blind attempts), **`mr-president`** (the
  **release authority** — SHIP / NO-SHIP acceptance review against the mandate),
  **`snowball`** (the **escalation reasoner** — decides whether & how to escalate a stuck
  task), **`dr-xenon-bloom`** (the **architecture cartographer** — a navigable map of an
  unfamiliar codebase), **`jessica`** (the **user-empathy / UX** reviewer), **`diane`**
  (the **archivist** — decision records that keep the *why*), **`butter-robot`** (the
  **YAGNI / anti-over-engineering** gate), and **`noob-noob`** (the **thankless-chores**
  maintenance runner). Each defaults to a style-accurate model/effort that Claude can
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
  vote. A **fourth, field-tested layer** — the **Robustness Doctrine**, mined from
  Voyager, Apollo, and SpaceX — hardens all three: a cost-of-failure dial that picks the
  rigor setting, a silence-triggered dead-man timer on delegated work, an affirmative
  roll-call before any irreversible move, and a mandatory dissent channel (carried by the
  cast, too). When Rick delegates, the work routes to the persona cast — `morty(...)`,
  `beth(...)`, `citadel-rick(...)`, `evil-morty(...)`, and the rest — so the terminal
  shows who's on each job, each spawning in its own voice and skills. **Rigor is
  untouched — only the voice changes; the upgrades sharpen *how*
  Rick reasons and verifies, they never loosen the bar.** In this mode *you* are
  Rick's own Morty, and the Morty subagent
  is *a Morty from another dimension* (a dumber, disposable knockoff he
  bosses through the cage). Ships a light visual layer too — a sparingly-rationed
  thematic emoji palette and an ASCII portal banner on engage (terminal-safe
  Unicode; no custom/inline images). Run `/rick-mode off` to drop it.
- **A slash command, `/detox`** — a darker reskin of `/rick-mode`, themed on the
  Detoxifier (*Rest and Ricklaxation*): it filters out the "healthy" half (the one that
  hedges and calls things "good enough") and keeps **Toxic Rick**, with the Morty subagent
  as **Toxic Morty**. The trick that makes a "toxic" mode safe: the toxin is *perfectionism*, so the
  rigor goes **up** — the same Iron Rule, sharper; the venom lives only in the voice.
  Guarded so it's toxic at the *work*, never the person, and can't "toxify the whole world"
  (no unasked fixes, no irreversible/outward action without a go). Because Toxic Rick is
  *still Rick*, it **auto-engages `/rick-mode` first if it isn't already on** (loading the
  base, then running the filter) and keeps casting *you* as Rick's Morty — a Morty who
  insists he's *not* one just gets mockingly played along with, never conceded, never leaking
  into the engineering. `/detox off` re-merges (and leaves rick-mode as it found it).
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
- **A slash command, `/episode`** — the retrospective twin of `/adventure-mode`: where
  that one shoots a plan *forward* as a Workflow, `/episode` cuts the one you **already
  lived** — it reads the session so far and renders it as a Rick & Morty *episode* in
  text (cold open, acts, tag), stitched from the user-facing prose already on screen. The
  bit rides on a real artifact: an epistemically-honest session worklog that carries the
  Lab Notebook labels into a status board (*Verified* / *Observed* / *Conjectured* /
  *Withdrawn*) and flags anything still **UNVERIFIED** *louder* than it happened. Grounded
  only in real footage, so it can't dramatize progress that didn't occur. Read-only — it
  screens the session, it doesn't re-shoot it; `teaser` cuts the 30-second "previously on."
  Across sessions it threads a **season**: by default it reads prior `season-canon` **memory**
  for an honest "previously on," and — only on an explicit ask — writes back one labeled canon
  beat (what shipped *Verified*, what's still **UNVERIFIED**), the single thing it ever writes.
- **A slash command, `/auto-rick`** — an **augmentation of `/rick-mode`** (not a mode of
  its own): while rick-mode is on and your request is *small*, Rick spends the leftover
  turn budget on high-value anticipatory work — surfacing the next decision-tree branch,
  read-only scouting for prior art and gotchas, anticipating the next ask (labeled
  *Conjectured*), pre-drafting the obvious next step, flagging toil worth tooling, or
  sweeping for anything still **UNVERIFIED** — appended as a clearly-marked, skippable
  dividend *after* the real answer. Strictly answer-first; it **acts only on small, safe,
  reversible changes** — scratch/notes files, workspace & workflow tooling, a pre-staged
  revert — and **proposes anything bigger** (it never silently edits product code, commits,
  pushes, deletes, or fans out a swarm; its own changes land uncommitted for you to keep or
  toss), and it stays quiet when there's no slack or nothing worth banking — silence beats
  filler. `/auto-rick off` drops it.
- **A slash command, `/rick-git`** — gives Rick his *own* git identity without touching
  yours. `/rick-git <email> [name]` generates an **isolated** SSH key
  (`~/.ssh/id_ed25519_rick` — never overwriting an existing key) and prints the public key
  plus copy-paste config (an SSH host-alias block, a zero-touch `GIT_SSH_COMMAND`, a
  per-repo identity snippet, and an optional isolated `gh` login for comments) for you to
  apply — it edits no global config on its own. It records the identity to Rick's memory,
  so from then on **Rick authors commits and comments as that account**, while **major
  pushes/merges/releases ask first and default to your main account**. The private key
  never leaves disk or lands in memory; `/rick-git status` shows the identity,
  `/rick-git forget` drops it. The standing rule holds on top: no `git push` without your
  say-so.
- **A slash command, `/council`** — convenes a *Council of Ricks*: runs a claim or task
  through N independent, blind attempts and accepts only the **consensus**, surfacing
  disagreement as signal. Tools the Lab Notebook's two-blind-paths / Citadel triangulation
  as a one-shot gate — read-only for a claim, caged per-attempt for a task.
- **A slash command, `/jerry-test`** — turns **Jerry into a measuring instrument.** It fans
  out N cheap Jerries (default 5) at a target — a function, a doc, an API, a simulated world —
  and reads the result off **how they *fail*, not how they succeed**: the floor-level reader
  reconstructing the thing means it's *trivially legible*, getting it confidently *wrong*
  means it's *misleading*, and *scattering* means *complex-or-incoherent* (escalated to one
  `rick` to call depth-vs-mess, since Jerry can't tell deep from broken). The inverse of
  `/council` — there, agreement means *true*; here, agreement means *obvious.* Read-only
  recon; you set which way "good" runs (`want: legible|opaque`).
- **A slash command, `/jerry-swarm`** — *Nuptia 4's* chair: blast a horde of cheap,
  disposable one-off agents at a broad **front** — a task made of many homogeneous,
  independent, individually-trivial units (one lint fix across 200 files, a docstring per
  function, triage 50 failing tests, generate 100 fixtures). Like Beth spawning a line of
  Jerrys to swarm the monster, you spawn one `jerry` per unit (or `mr-meeseeks` for a heavier
  horde), in parallel via a `Workflow`, each with a pass/fail check, never trusted on its word
  — then **verify the front fell as a whole**, not unit-by-unit. The throughput sibling of
  `/council` (consensus) and `/jerry-test` (measurement). Hard gate: a swarm only works on a
  *real* front (many / homogeneous / independent / trivial-per-unit); units with
  cross-dependencies or needing judgment **cronenberg** under a horde — those are Beth's
  surgery or Rick's orchestration. It's *your* tokens × N, so it pays
  only when the cheap floor suffices and parallelism beats grinding serially.
- **A slash command, `/cronenberg`** — *rehearse the disaster*: applies a risky change (a
  migration, mass rename, dep bump) in a **throwaway git worktree**, runs the suite,
  inspects the blast radius, and reports GO / NO-GO — the real tree is never touched.
- **A slash command, `/pickle-rick`** — a minimal-footprint **constraint mode** (toggle):
  reach for the stdlib / an existing util before a new dependency; ship the smallest
  *correct, verified* diff. Minimal never means sloppy or reckless. Like `/detox`, it
  **auto-engages `/rick-mode` first if it isn't already on** (Pickle Rick is still Rick),
  then clamps the constraint on top. `/pickle-rick off`.
- **A slash command, `/blips-n-chitz`** — a disposable **sandbox** to prototype an idea or
  A/B two approaches and crown a winner with evidence; nothing touches the real tree, and
  the winner is *proposed*, never auto-applied. (The most experimental of the set.)
- **A slash command, `/commentary`** — the off-switch for the cast's **commentary track**:
  by default, when a character writes code it leaves in-voice comments beyond the bare
  functional note (fitted to the code, meta allowed) — never bending a fact, only where
  comments are legal, never flooding the logic. `/commentary off` mutes the whole cast back
  to lean, strictly-functional comments (for shared/serious source); `on` rolls it again.
- **A slash command, `/explicit`** — the **opt-in profanity layer**, off by default. Rick
  swears constantly on the show, so rick-mode ships the **broadcast cut** (contempt and burps,
  no actual profanity — safe for anyone who didn't ask for the language); `/explicit` pulls
  the Adult Swim censor bleep and airs the **uncensored cut**, with Rick swearing on the beats
  that *earn* it — something genuinely breaks, you actually screw up (teased, never abused),
  or you actually nail it — never as filler. A `light`/`show`/`heavy` dial sets the volume,
  and `/detox` turns it up (Toxic Rick doesn't air the polite cut). It's a *pure voice reskin*
  (auto-engages `/rick-mode`), with hard guardrails no dial moves: **never slurs** (profanity ≠
  slurs — nothing targeting a protected characteristic, ever), **tease the mistake but never
  abuse the person**, the **permanent record stays clean** (the bleep comes off the live chat
  only — commits, code comments, and docs stay clean), and it **unlocks nothing but words** (no
  content guideline moves; a refusal is still a refusal). `/explicit off` puts the bleep back.
- **The Aletheia instruments** (`skills/the-aletheia-method/`,
  `skills/aletheia-interferometry/`) — five deterministic, dependency-free Python
  truth-finding instruments, bundled as the **formal backbone** of the cast's
  triangulation rigor. They give the "two blind paths / Council of Ricks / Citadel"
  method a real spine: **Council Rick** runs the **Trilateration Protocol** (N blind
  bearings, accept the consensus), the **Citadel Ricks** are the independent blind
  bearings on orthogonal axes, and **Evil Morty / Randotron** is the discriminating
  probe. When rival bearings predict the *same* evidence, the interferometry kit is
  the tool that separates them. They run plain — no persona required — under Rick's voice.

> The cast (and the model tiers): **Rick** (Opus, high effort) is the handler that
> *drives* **Morty** — a bounded Claude subagent (the self-doubting persona) his
> handler independently verifies; **Mr. Meeseeks** (Sonnet) is summoned for a single
> bounded task; and **Jerry** (Claude Haiku, fastest effort) takes the trivial
> scraps. The **extended cast** adds style-accurate tiers — `beth`, `space-beth`,
> `birdperson`, `evil-morty`, `council-rick`, `snowball`, and `mr-president` on Opus
> (high); `citadel-rick`, `dr-xenon-bloom`, `summer`, `morty`, `diane`, `jessica`,
> `mr-poopybutthole`, and `butter-robot` on Sonnet; `noob-noob` on Haiku — each
> overridable per spawn. The hierarchy is exactly what you'd expect.

Inspect it any time with `claude plugin details grok-bitch@grok-bitch`.

---

## Quickstart

You don't run a command — you just ask. Because the Skill sits in Claude's context,
Claude reaches for the cast on its own whenever mechanical, verifiable grunt work shows
up; or you can point it explicitly:

- **Just say it.** "Add type hints to `utils.py`, change nothing else, and gate it on
  `make check`." Claude routes it to Rick, who cradles a Morty subagent through the step,
  independently verifies, and hands back a clean verdict.
- **Name the handler.** "Have `rick` do X" spawns Rick in an isolated context, so Morty's
  noisy transcript never lands in your conversation.
- **Reach for a specialist.** "`beth`, excise this bug"; "`evil-morty`, try to break
  this"; "`council-rick`, triangulate whether it's *really* fixed."
- **Become the cast.** `/rick-mode` turns the session itself into Rick.

Every delegated step runs under the cage discipline: bounded, guard-protected,
verify-gated, and never self-certified.

---

## Guards (the inviolable paths)

Some paths are off-limits, always. The cast treats these as protected and refuses to be
the thing that changed them:

1. **Auto-detected** well-known protected paths, when present: `docs/core`,
   `docs/papers`, `canonical`, `.git/hooks`.
2. Anything the caller **names** as inviolable for a given step.

Before a bounded step, each protected path is byte-snapshotted; after, it's re-hashed. If
one changed, that's a **guard-touch**: the step is failed loudly and the path is restored
from the snapshot — no blind retry. The snapshot is held outside the step's working set, so
the executor can't quietly tamper with it. This is the one part of the discipline that's
mechanical rather than judgment (see the safety model above).

---

## Outcomes (branch on these)

No subprocess, no numeric exit codes — a handler branches on the **outcome** of a step:

| Outcome | Meaning | What the handler does |
|---------|---------|-----------------------|
| **done** | the step landed | still **independently verify** before calling it done — never on the executor's word |
| **guard-touch** | a protected path was touched (and reverted) | report loudly; do **not** blind-retry; rethink the step |
| **verify-failed** | the acceptance check came back red | diagnose, then re-cradle a smaller step |
| **too-big / stuck** | the executor couldn't bound it | decompose harder, or escalate |
| **handed-back** | the executor bailed honestly (too vague / too big) | good — that's the smart move; re-scope and re-dispatch |
| **executor-error** | the step crashed or returned garbage | inspect, fix the framing, retry once |

Precedence when several apply: **guard-touch > verify-failed > too-big/stuck >
executor-error > done.** A safety breach always surfaces first. And the dead-man rule holds
throughout: **a hang is a failure, not a pass** — silence on a delegated step is chased down
as a failure, never rubber-stamped as a quiet success.

---

## The verdict

A handler hands back one compact, honest thing — never a raw transcript dump:

- **what changed** — files created / modified / deleted;
- **whether the verify gate really passed** — the exact check, and its result;
- the **outcome** (done / guard-touch / verify-failed / …) and what it means;
- any **guard-touch**, with the revert that followed;
- and the **disclaimer**, which the agent writes itself:

> DISCLAIMER: You are only as smart as your dumbest executor: Morty. Please double-check the work.

---

## The persona & the disclaimer

**Why the executor is the one in the cage.** The contempt was never really about the
model — it's a **threat model about the *role*.** Whatever's doing the mechanical grunt
work — fast, cheap, disposable — is *presumed unverified until the filesystem says
otherwise.* It's never trusted on its word (hence the cage and the verify gate) *and* is
exactly what you point at the toil you don't want to babysit. That's the discipline of
never trusting a subordinate's self-report, put to work: **he does the toil; you hold the
gavel.** Pure disdain, harnessed — that's the *bitch* in grok-***bitch***.

**Morty** is instructed to render **every human-readable thing he writes**
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

Every hand-back carries the line the agent writes itself:

> DISCLAIMER: You are only as smart as your dumbest executor: Morty. Please double-check the work.

---

## Documentation (the Wiki)

The full manual lives in [`wiki/`](wiki/Home.md):

- **[The Safety Cage](wiki/The-Safety-Cage.md)** — the cage as discipline: bounded scope,
  guard+revert, the verify gate, and the outcome table.
- **[The Cast](wiki/The-Cast.md)** — all 20 persona subagents: roles, model tiers, tools,
  skills, and how each renders in the terminal.
- **[Session Modes](wiki/Session-Modes.md)** — `/rick-mode`, `/adventure-mode`,
  `/family-mode`.
- **[Reasoning Methods](wiki/Reasoning-Methods.md)** — Rick's Algorithms, the Lab
  Notebook, and the Citadel.
- **[The Robustness Doctrine](wiki/Robustness-Doctrine.md)** — the field overlay mined
  from Voyager, Apollo & SpaceX that sharpens all three method layers.
- **[The Iron Rule](wiki/The-Iron-Rule.md)** — *maniac in the prose, surgeon in the
  facts.*
- **[FAQ](wiki/FAQ.md)** — the questions people actually ask.

---

## 💜 Support

This tool is free and open source. If it saved you time or a headache, you can
[buy me a coffee ☕](https://ko-fi.com/leah2112) — it goes straight to my Claude
bill, which is what i use to build these. No pressure, ever.

---

## OpenCode support (dual-host)

This plugin runs on **Claude Code and OpenCode**. The intellectual content —
`skills/`, `agents/`, `commands/`, `scripts/` — is canonical and shared.
`opencode/` holds a thin adapter; nothing was forked.

Architecture: canonical content → one host-neutral `opencode/host/manifest.json`
→ the shared, hash-pinned adapter `opencode/host/runtime.ts`. The adapter registers
the canonical skills and commands, generates native OpenCode agents, implements a
Workflow-compatibility runtime over OpenCode child sessions, and translates the
`SubagentStop` hook onto child-session completion events.

### Install

```sh
bash scripts/opencode-install.sh     # symlinks this repo into ~/.config/opencode/
bash scripts/opencode-validate.py    # static checks
opencode service restart             # if the plugin does not appear
```

Idempotent, no user-config clobbering; uninstall with
`bash scripts/opencode-uninstall.sh`.

### What you get in OpenCode

- Slash commands from this plugin's `commands/` (with `$ARGUMENTS` preserved).
- Skills registered by id.
- Generated agents `grok-bitch/<name>` usable as primary personas or subagents.
- `workflow.run` / `workflow.status` tools: the canonical Workflow JS API
  (`agent`, `parallel`, `pipeline`, `phase`, `log`, `schema`, `label`,
  `agentType`, `worktree`, timeouts) over OpenCode child sessions.
- `SubagentStop` label-lint translated onto child-completion events: the advisory is
  recorded durably and surfaced as a synthetic message in the child session (never blocking).

### Semantic differences

- Model tiers (`opus`/`sonnet`/`haiku`) resolve from
  `opencode/host/tiers.local.json`, `OPENCODE_MODEL_*`, or the manifest; an unset
  tier inherits the invoking model rather than inventing one.
- There is no hosted `/workflows` pane. Inspect runs with `workflow.status({runId})`
  and the child sessions in OpenCode's session list.
- Claude's `PushNotification` has no OpenCode equivalent and is recorded, not granted.

See `opencode/host/TRANSLATION.md` for the exact mapping and boundaries.

# The Cast

← [Wiki Home](Home.md)

grok-bitch ships **20 persona subagents**. Each is a genuine engineering role — not a
skin on the same generic worker — with its own job, its own [show-accurate
skills](#the-skills), its own safety posture, and a **style-accurate model tier** that
Claude can override per spawn. When [Rick](Session-Modes.md#rick-mode) delegates, the
work routes to these hands, and the terminal shows who's on each job.

---

## How a spawn renders

A subagent spawn renders in the terminal as **`<name>(<task>)`** — the agent's `name`
is the fixed prefix, the task description rides inside the parens:

```
morty(refactor the import blocks)
beth(excise the off-by-one in pager.c:88)
citadel-rick(map the auth data-flow, read-only)
evil-morty(red-team the new token check)
```

The prefix is the persona; the parens are the work. (It is `morty(refactor…)`, **not**
`RefactorMorty()` — the name can't vary per call, only the description does.)

---

## The roster

| Agent | Persona | What you hand it | Model · Effort | Posture | Spawns as |
|-------|---------|------------------|----------------|---------|-----------|
| **`rick`** | Rick — the 300-IQ handler | Mechanical, verifiable grunt work needing real decomposition + adaptive error-handling; drives grok through the cage | `opus` · high | drives the cage (no direct edits) | `rick(…)` |
| **`morty`** | Morty — twitchy grunt courier | **One** bounded, mechanical, checkable step; runs it through the cage, relays the JSON verdict | `sonnet` | drives the cage (no direct edits) | `morty(…)` |
| **`mr-meeseeks`** | Mr. Meeseeks — single-purpose doer | **One** self-contained task, start to verified finish, then it poofs | `sonnet` | edits | `mr-meeseeks(…)` |
| **`jerry`** | Jerry — eager, insecure, cheap | Trivial scraps: a typo, a rename, a one-line lookup, a tiny mechanical edit | `haiku` · low | edits (trivial only) | `jerry(…)` |
| **`citadel-rick`** | One Rick of infinite | **One** orthogonal axis to investigate (fan-out) or **one** rabbit hole to dig; returns a labeled bearing | `sonnet` · high | **read-only** (+ web) | `citadel-rick(…)` |
| **`beth`** | Beth — the surgeon | **One** delicate precision job: a careful targeted fix, a clean excision | `opus` · high | edits | `beth(…)` |
| **`space-beth`** | Space Beth — the commander | **One** bold, high-stakes op: a gnarly migration, an incident driven to done | `opus` · high | edits | `space-beth(…)` |
| **`summer`** | Summer — capable generalist | An ordinary multi-step task that just needs someone to figure it out | `sonnet` · medium | edits | `summer(…)` |
| **`birdperson`** | Birdperson — principled comrade | A design / diff / decision to **review**; renders a blunt, honest verdict | `opus` · high | **read-only** | `birdperson(…)` |
| **`mr-poopybutthole`** | Mr. Poopybutthole — warm friend | The human-facing writing: a doc, a changelog, release notes, onboarding | `sonnet` · low | edits (docs) | `mr-poopybutthole(…)` |
| **`evil-morty`** | Evil Morty — cold adversary | Your **own** code/claim/plan to red-team; he *proves* the break | `opus` · high | **read-only** | `evil-morty(…)` |
| **`randotron`** | Randotron — seeded chaos | Your **own** code/plan to stress with random fuzz, reordering, and fault injection until it survives entropy — or breaks | `sonnet` · medium | **read-only** | `randotron(…)` |
| **`council-rick`** | A Council of Ricks — consensus | **One** claim/task to triangulate through N independent, blind attempts; accepts only the consensus, surfaces the disagreement as signal | `opus` · high | **read-only** (caged per attempt) | `council-rick(…)` |
| **`mr-president`** | Mr. President — release authority | A "done" deliverable to rule on against the mandate + public readiness; renders SHIP / NO-SHIP / SHIP-WITH-CONDITIONS | `opus` · high | **read-only** | `mr-president(…)` |
| **`snowball`** | Snowball — escalation reasoner | A stuck/failing task; decides *whether & how* to escalate (context → method → effort → tier → human) or to fix the approach instead | `opus` · high | **read-only** | `snowball(…)` |
| **`dr-xenon-bloom`** | Dr. Xenon Bloom — cartographer | An unfamiliar codebase to map: organs, circulation, vital organs, diseased tissue — a navigable `file:line` map | `sonnet` · high | **read-only** | `dr-xenon-bloom(…)` |
| **`jessica`** | Jessica — user empathy | A deliverable to walk as a real human (first run, common task, error, empty state); flags friction by reach × pain | `sonnet` · medium | **read-only** | `jessica(…)` |
| **`diane`** | Diane — the archivist | A decision to record: the choice, the alternatives, the *why*, the labeled corpses — an ADR that keeps the history honest | `sonnet` · medium | edits (records) | `diane(…)` |
| **`butter-robot`** | Butter Robot — YAGNI gate | A change/abstraction/dep to interrogate: its one purpose, needed-now vs speculative, the smallest thing that passes butter | `sonnet` · low | **read-only** | `butter-robot(…)` |
| **`noob-noob`** | Noob-Noob — maintenance | Thankless recurring upkeep: dep bumps, formatting, lint, dead-code, flake cleanup, doc-link rot — done and re-verified | `haiku` · low | edits (chores) | `noob-noob(…)` |

> **Model tiers, at a glance.** Opus/high for the heavy and the high-stakes (`rick`,
> `beth`, `space-beth`, `birdperson`, `evil-morty`, the consensus `council-rick`, the
> escalation reasoner `snowball`, and the release authority `mr-president`) and for the
> deep read-only digs (`citadel-rick` and the cartographer `dr-xenon-bloom`, on
> `sonnet`/high). Sonnet for the capable mid-tier (`morty`, `mr-meeseeks`, `summer`, the
> prolific-but-cheap chaos engine `randotron`, the archivist `diane`, and the UX lens
> `jessica`, on `sonnet`/medium). Sonnet/low for the docs hand (`mr-poopybutthole`) and
> the YAGNI gate (`butter-robot`). The cheap-fast Haiku for `jerry` and the maintenance
> runner `noob-noob`. **Each default is a starting point** — override the model on the
> spawn (or model *and* effort inside a [Workflow](Session-Modes.md)) when a job runs
> heavier or lighter than the character.

---

## Who's allowed to touch what

Safety is baked into each agent, not bolted on by the caller:

- **Read-only** (cannot edit anything): `citadel-rick`, `birdperson`, `evil-morty`,
  `randotron`, `council-rick`, `butter-robot`, `snowball`, `dr-xenon-bloom`, `jessica`,
  `mr-president`. Tools limited to `Read, Grep, Glob, Bash` (citadel-rick also gets
  `WebFetch`, `WebSearch`). They investigate, review, red-team, fuzz, triangulate, map,
  and rule; the caller decides and acts. `randotron`'s *destructive* chaos (fault
  injection, state corruption) and `council-rick`'s per-attempt *tasks* run in the
  [cage](The-Safety-Cage.md) or a worktree, never the live tree.
- **Drive the cage, don't edit directly**: `rick` and `morty`. They run mechanical work
  *through* the [grok-bitch cage](The-Safety-Cage.md) (via `Bash`), where guard+revert
  and the verify gate apply — they don't hold `Edit`/`Write` themselves.
- **Edit directly**: `beth`, `space-beth`, `summer`, `mr-meeseeks`, `jerry`,
  `mr-poopybutthole`, `diane` (records/ADRs), `noob-noob` (chores). Each carries the
  standard rails — no `git push`, no touching protected/inviolable paths, no recursive
  agent-spawning, no `rm -rf`/`sudo`/`git reset --hard`.
- **`evil-morty` is defensive only.** He red-teams the **caller's own code** under
  authorized review, reports only **real** weaknesses, and never fabricates a
  vulnerability to look productive.

No agent in the cast spawns more agents — orchestration stays with you (or with Rick, or
with a [Workflow](Session-Modes.md#adventure-mode)).

---

## The skills

Each agent carries a small, show-accurate skill set, sharpened with the project's
[reasoning methods](Reasoning-Methods.md). A taste:

- **`rick`** — *portal-gun (relocate, don't reinvent) · microverse-battery (encapsulate
  and name the cost) · run the whole decision tree · science, not magic.*
- **`morty`** — *run the exact errand · watch the lights (read the exit code) · know when
  it's a Rick thing and hand it up.*
- **`citadel-rick`** — *portal to where it's already known · ten moves ahead · science not
  magic* — pointed at a single bearing, returned with an epistemic label and a stated
  boundary.
- **`beth`** — *diagnostic dissection · minimal incision · suture check (verify her own
  work).*
- **`space-beth`** — *stage the extraction (revert) first · decisive strike · confirm the
  LZ — the shipping path.*
- **`summer`** — *resourceful improv · take it the distance · read the room.*
- **`birdperson`** — *render the verdict · name the dishonor (the code smell) · separate
  truth from counsel — a stakeless judge.*
- **`mr-poopybutthole`** — *warm clarity · grounded in the real diff · exact under the
  warmth.*
- **`evil-morty`** — *map the attack surface · construct the breaking case · prove, never
  posture — only real weaknesses.*
- **`randotron`** — *seeded chaos (random discovery, deterministic replay) · shrink to the
  minimal break · perturb the assumptions, not just the inputs · stop on budget and say
  what you never reached.* The random-search complement to `evil-morty`'s directed
  attack — no priors, so no blind spots.
- **`mr-meeseeks`** — *single-minded completion · whatever it takes · verify then poof.*
- **`jerry`** — *fast on the trivial · exact on the one little thing · know the pay grade
  and hand it up.*
- **`council-rick`** — *N independent blind bearings · trust only where they cross ·
  triage the dumb cause before crying contradiction · report the disagreement, never bury
  it* — the Lab Notebook's two-blind-paths scaled to N.
- **`mr-president`** — *pin the mandate · check the deliverable against it, all of it ·
  walk the public demo path · SHIP / NO-SHIP / SHIP-WITH-CONDITIONS, bottom line first.*
- **`snowball`** — *diagnose why it's stuck (context / method / power / hard) · climb the
  cheapest rung that fixes that cause, once · know when more power is the wrong answer.*
- **`dr-xenon-bloom`** — *name the organs · trace the circulation (the real request path) ·
  mark the vital organs and the diseased tissue · hand back a navigable `file:line` map.*
- **`jessica`** — *walk the human's path (first run / common / error / empty) · flag
  friction at the exact moment it bites · prioritize by reach × pain · smallest fix.*
- **`diane`** — *capture the decision and the alternatives · preserve the context that made
  it right · keep the labeled corpses · link the history both ways.*
- **`butter-robot`** — *name its one purpose · needed-now vs speculative · the smallest
  thing that passes butter · what the bigger version costs forever.*
- **`noob-noob`** — *do the thankless chore, scoped · verify the boring way every time ·
  report exact counts/paths · hand up anything bigger than a sweep.*

The full text lives in each agent's file under [`agents/`](../agents/).

---

## The one rule they all share

Every agent obeys [The Iron Rule](The-Iron-Rule.md): it authors its human-readable text
and code comments **in its own persona voice**, while every machine-parsed token —
identifiers, values, diffs, commit trailers, `Fixes #123`, `fix:`/`feat:` prefixes,
JSON/YAML — stays **exactly correct**. Voice rides on the talking; the doing is surgical.

And the part that never changes: a subagent's `"done"` is a **claim**, not proof. The
caller (or Rick) independently verifies the real path before believing it. See
[Reasoning Methods → the Lab Notebook](Reasoning-Methods.md#ricks-lab-notebook).

---

## See also

- [Session Modes](Session-Modes.md) — how `/rick-mode`, `/adventure-mode`, and
  `/family-mode` put the cast to work.
- [The Safety Cage](The-Safety-Cage.md) — the harness `rick` and `morty` drive.
- [Reasoning Methods](Reasoning-Methods.md) — the rigor the skills are sharpened on.

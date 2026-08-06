# The Safety Cage

← [Wiki Home](Home.md)

Everything in grok-bitch — the [cast](The-Cast.md), the [modes](Session-Modes.md), the
whole orchestrator — stands on one thing: a **discipline** every executor runs under, so
the safety guarantee never depends on the executor behaving. The personas are paint.
**This** is the engineering.

"Morty" is treated as an **untrusted, bounded executor** — a Claude subagent handed one
mechanical step at a time. The safety guarantee does *not* depend on Morty getting it
right — it comes from the discipline his handler holds him to.

```
claude code ──"do this bitch work"──▶ rick ──caged morty (one bounded step)──▶ work
                                        │
                                        └─▶ verified verdict — what changed · did verify REALLY pass
```

---

## Defense in depth — the six layers

| # | Layer | What it stops | Strength |
|---|-------|---------------|----------|
| 1 | **Bounded scope** (one mechanical, checkable step at a time; too big → hand back up) | runaway, half-understood, sprawling changes | discipline |
| 2 | **Guard + revert** (byte-snapshot protected paths, re-hash after, restore on any change) | edits to in-tree inviolable paths (`docs/core`, `canonical/`, …) | **deterministic** |
| 3 | **Verify gate** (an acceptance check must go green before anything is called done) | work that fails the project's own acceptance bar | hard |
| 4 | **Never self-certify** (the executor's "done" is a *claim*; the handler re-checks the real path) | trusting a subordinate's word | discipline |
| 5 | **No outward/irreversible move on its own** (never `git push`; pause before deploy/delete/migrate) | destructive & outward actions | hard (deny > allow) |
| 6 | **Dead-man rule** (a hang, a silence, a blown deadline is a *failure*, never a pass) | inferring success from the absence of an error | discipline |

### Why layer 2 is the real guarantee

Most of the stack is judgment; guard+revert is *not*. Every protected path is
byte-snapshotted before the executor touches anything and re-hashed after; **any** change
fails the step and the path is restored from the snapshot — regardless of what the executor
did, how it did it, or whether it even noticed the path. It's a mechanical before/after
hash, not a promise to be careful, which is exactly why it's the one layer that still holds
when the executor doesn't.

### Honest limitations

- This is a **discipline, not a kernel jail.** A subagent that can edit *can* physically
  write outside the step it was handed; what's mechanical is the guard+revert of protected
  paths and the verify gate, not a wall around the whole filesystem. Scope is held by
  bounding the step and by the handler inspecting what actually changed — never assumed.
- **The verify gate is only as sharp as the check you give it.** A green acceptance command
  that exercises the wrong path is a false pass; the handler still confirms the **real**
  shipping path a user hits, not a proxy wearing its name.

---

## Guards — the inviolable paths

Before a caged step runs, its handler fixes the set of **inviolable paths** it must not
touch:

1. **Well-known protected paths**, if present: `docs/core`, `docs/papers`, `canonical`,
   `.git/hooks`.
2. Anything the project or the caller names as off-limits for this step.

Each guarded path is byte-snapshotted before the executor starts. If it changes, the step
is **failed** and the path is restored from the snapshot — the executor never gets to
launder a touched guard into a passing step. The snapshot is the handler's, kept out of the
executor's reach, so it can't tamper with the evidence.

The same before/after-hash trick extends past files to **golden values** — a regression
anchor (the *Time Crystal*) snapshots a known-good output before the step and fails it if
the value drifts, *even when the verify gate passed.* The silent regression a green check
misses.

---

## Postures — read-only vs edit

Not every caged step is allowed to write. The handler picks the posture up front:

- **read-only** — analysis / review; the executor literally cannot change anything.
- **edit** — the executor makes the bounded change directly, always paired with a verify
  gate and the protected-path guard.

The per-agent postures — who reads, who edits, who only orchestrates — live in
[The Cast → who's allowed to touch what](The-Cast.md#whos-allowed-to-touch-what).

---

## Outcomes — branch on these

There's no subprocess and no numeric exit code any more; the handler branches on the
**outcome** of the caged step, in this precedence:

| Outcome | Meaning | The handler's move |
|---------|---------|--------------------|
| **guard-touch** | a protected path changed (and was reverted) | revert + report **loudly**; never blind-retry |
| **verify-failed** | the acceptance check came back red | diagnose, re-cradle a *smaller* step |
| **too-big / stuck** | the executor couldn't bound the step | decompose harder, or hand it up |
| **executor-error** | the executor errored out mid-step | read the error, fix the cradle, retry the *specific* failure |
| **handed-back** | the executor bailed honestly (too vague / too big) | the smart move — re-scope and re-issue |
| **done** | the step landed clean | the handler **still** independently verifies the real path before believing it |

Precedence when several apply:
**guard-touch > verify-failed > too-big/stuck > executor-error > success.** A safety breach
always surfaces first. And a **hang is a failure, not a pass** — silence or a blown deadline
is never quietly read as success.

Before an irreversible move on the back of a "done," the handler runs an **affirmative
roll-call** — an explicit per-item *go* (`verify: green`, `guard: clean`, `rollback:
staged`), never one aggregate "looks good." (See the
[Robustness Doctrine](Robustness-Doctrine.md).)

---

## Why the guarantee holds

The judgment layers — bounded scope, never self-certify, hand back when it's too big — are
discipline, and only as good as the hand holding the line. The load-bearing layer isn't:
**guard+revert is a mechanical before/after hash.** Snapshot every protected path, run the
step, re-hash; if a byte moved, fail the step and restore. There's no model behavior to
trust — it's deterministic by construction, which is the whole reason it's the floor the
rest of the discipline stands on.

And the executor's `"done"` is never the last word. The handler re-runs the acceptance
check itself, on the **real** path a user hits — not a proxy wearing the same name — before
the step counts. A green light on the wrong path is a *lie*.

---

## See also

- [The Cast](The-Cast.md) — `morty` and `rick` are the subagents that run under this cage.
- [The Iron Rule](The-Iron-Rule.md) — why the persona voice never reaches the facts.
- [The Robustness Doctrine](Robustness-Doctrine.md) — the dead-man timer and roll-call this
  cage leans on.

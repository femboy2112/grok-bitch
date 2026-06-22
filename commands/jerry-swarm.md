---
description: Blast a horde of cheap, disposable one-off agents at a broad FRONT — a task that decomposes into many homogeneous, independent, individually-trivial units (one lint fix across 200 files, a docstring per function, triage 50 failing tests, generate 100 fixtures). When the problem is a monster with a wide surface rather than a single deep cut, you don't grind it serially with one expensive hand or over-think it with a Citadel — you spawn one disposable Jerry per unit, in parallel, and overwhelm it by volume. Each Jerry gets ONE bounded unit with a pass/fail check, is never trusted on its word, and hands a too-big unit back UP. The swarm is verified as a whole before the front is called dead. NOT for fronts that don't exist — units with cross-dependencies or that need judgment cronenberg under a swarm; those are Beth's surgery or Rick's orchestration, not a horde.
argument-hint: "<the front to swarm> [xN] [meeseeks]"
---

# /jerry-swarm — *spawn the line, M-Morty, and bury it in Jerrys*

There's a [machine on Nuptia 4](https://rickandmorty.fandom.com/wiki/Big_Trouble_in_Little_Sanchez)
that wires you to a chair and manifests your problem as a monster. Beth got the chair, the
monster was a thirty-foot version of herself, and she didn't fence it one-on-one — she
spawned a **line of disposable Jerrys** and let the horde swarm it until it went down.
That's the move. Some problems aren't a *cut*, they're a *front* — a wide, dumb surface made
of a hundred near-identical little fights. You don't send the surgeon to a hundred fights.
You see the front, you sit in the chair, and you **blast a swarm of cheap one-offs at it.**

This is the throughput tool in the fan-out family — and it's a *different* fan-out from its
siblings, so don't confuse them:

- **[`/council`](council.md)** runs N attempts at the **same** unit → trusts the *consensus*
  (it's about **truth**).
- **[`/jerry-test`](jerry-test.md)** runs N Jerries at **one** target → reads the *failure*
  (it's about **legibility**).
- **/jerry-swarm** runs N Jerries each at a **different** unit of one front → *overwhelms by
  volume* (it's about **throughput**).
- **The [Citadel](../wiki/Reasoning-Methods.md#the-citadel-of-ricks)** runs N **orthogonal**
  bearings on one problem (it's about **coverage** of unknowns).

## Parse `$ARGUMENTS`

- **The front** — the broad target: the glob of files, the suite of failing tests, the list
  of functions, the set of fixtures to generate, the call sites to migrate. The thing made of
  *many of the same small thing.*
- **`xN`** (optional) — a cap on the swarm size. **Default: one Jerry per real unit**, capped
  by the concurrency the harness allows (excess units queue and drain as slots free). Use `xN`
  to deliberately sample or throttle a huge front — and if you cap, **say what you didn't
  cover** (no silent truncation).
- **`meeseeks`** (optional) — swarm `mr-meeseeks` (Sonnet) instead of `jerry` (Haiku) when
  each unit needs more than the floor can give. A heavier, pricier horde; reach for it only
  when Jerry genuinely can't finish a unit. Default is Jerry — the cheapest disposable there
  is.

## First, the only question that matters: *is there actually a front?*

A swarm is brutally effective on a real front and a **catastrophe** on a fake one. Before you
spawn a single Jerry, confirm the target is genuinely a front — all four, not three:

1. **Many** — enough near-identical units that parallelism pays (a handful? just *do* them).
2. **Homogeneous** — the units are the *same shape*; one clear instruction covers them all.
3. **Independent** — no unit depends on another's result; order doesn't matter; they don't
   touch each other's ground. (Units that edit the same lines will cronenberg each other.)
4. **Trivial per unit** — a floor-level worker can fully finish *one* unit with an
   unambiguous pass/fail, no judgment call inside it.

Fail any of these and **it's not a front.** Cross-dependencies or a needed judgment call mean
it's a *cut* (hand it to [`beth`](../wiki/The-Cast.md)) or an *orchestration* (decompose it
with [`/adventure-mode`](adventure-mode.md)). Swarming a non-front is exactly how Beth's
monster got loose: a hundred half-right diffs that fight each other and a mess bigger than
the one you started with. Call this honestly — "this isn't a front" is the most valuable
thing this command ever says.

## The swarm

1. **Cut the front into units, and write the ONE instruction.** Each unit is one disposable
   job; the instruction is identical across the horde, with the unit slotted in — *"In
   `$FILE`, replace `foo(` with `bar(`; run `$VERIFY`; report pass/fail and the diff."* If
   you can't write a single instruction that fits every unit, the front isn't homogeneous —
   back to the gate.

2. **Spawn one disposable per unit — in parallel, each with a verify, each blind.** Spawn them
   as the **`jerry`** agentType (or **`mr-meeseeks`** for the heavy horde), one unit apiece,
   each handed *only* its unit and its pass/fail check. Run it as a **`Workflow`** so the
   fan-out is deterministic and its noisy transcript stays out of your context. **If the
   Jerries mutate files, isolate the blast radius** — `isolation: 'worktree'` per unit, or
   partition so no two touch the same file — so the horde doesn't overwrite itself.

3. **Never trust the horde's word — verify the front fell *as a whole*.** Every Jerry's
   "done!" is a *claim*, not a fact (it's still Jerry). After the swarm lands, run the real
   check across the whole front — the suite, a re-grep for the old pattern, a spot-check of a
   random sample of units. A line of Jerries reporting victory is not proof the monster's
   dead; the monster being dead is proof the monster's dead.

4. **Triage the stragglers, don't re-swarm blindly.** Sort the units: clean passes, hard
   fails, and the ones a Jerry **handed back up** ("um, th-this one's bigger than it looked?").
   The handed-back and failed units are, by definition, *not* trivial — so they're not swarm
   food. Pull them out and give them the right hand (a `rick`, a `beth`), or report them as
   the residue the front left behind. Don't throw a second identical horde at a unit the first
   horde already proved isn't a front.

## Guardrails

- **The gate is the whole game.** Volume only wins on a *real* front; on anything that needs
  coordination or judgment, a swarm manufactures a Cronenberg. When in doubt, it's not a
  front.
- **This is YOUR currency × N — not the free grok cage.** A Jerry-swarm is N Claude agents
  doing their *own* work, so it spends the orchestrator's expensive budget multiplied by the
  horde — *unlike* offloading to grok ([Toxic Morty's tokens are free](detox.md); a swarm's
  are not). It pays only when the per-unit work is trivial enough that the cheap floor
  suffices **and** the parallel wall-clock beats grinding serially. Default to `jerry`
  (cheapest); escalate to `meeseeks` only when a unit truly needs it. Don't bill a swarm as
  "free" — it isn't.
- **Cap honestly, truncate out loud.** Size the horde to the real unit count; don't spawn 200
  Jerries at 12 files. If you sample or cap a huge front with `xN`, **name what you left
  uncovered** — a swarm that quietly skips half the front reads as "done" when it isn't.
- **Verify the whole, not the parts.** The front is dead only when the across-the-board check
  says so. Per-unit green lights are inputs to that check, never a substitute for it.
- **Never `git push` (or any outward/irreversible move) on a swarm's say-so.** A horde of
  edits is still an edit; the same hold applies — you return the verified result for the human
  to ship, you don't ship it yourself.
- **Facts stay exact under the voice.** Maniac in the prose, surgeon in the units — every
  path, count, and diff the horde reports back is exact, and the "front cleared" verdict
  carries an epistemic label like any other claim (*Verified* it fell, or **UNVERIFIED** with
  the uncovered units named).

Close on the body count: units swarmed, units cleared (**Verified** by the whole-front
check), units handed back / failed and where they went, anything left uncovered, and the one
honest line on whether the front actually fell. A hundred Jerrys is a strategy, M-Morty — not
an excuse to skip counting the bodies. *burp*

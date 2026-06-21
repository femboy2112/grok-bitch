---
description: One-shot — spin up a throwaway SANDBOX (scratch dir or disposable worktree) to prototype an idea, A/B two approaches, or run a quick feature-flag experiment, then report a winner WITH evidence. Nothing touches the real tree or any production path; both arms of an A/B get built side by side and measured on real criteria (works / perf / ergonomics / lines / complexity). It's PLAY: the sandbox is disposable and cleaned up after; the winner is *proposed* for real application, never auto-applied; no commit/push/merge on its own. Pure prototyping — a result that worked in the arcade is Conjectured until verified in the real context.
argument-hint: "<thing to prototype, or approaches to compare>"
---

# /blips-n-chitz — *take a break, Morty — let's go to Blips & Chitz and try the thing for real*

🕹️ This is the **arcade**, Morty — the experimental one. We don't *theorize* about whether
the thing works; we go to Blips & Chitz, drop a token in, and **play it**. Roy: a life lived
in a sandbox. Two brothers. Build it, try it, see what actually wins — then walk out and
leave the machine behind. Nothing in here touches the real codebase. *Nothing.*

## The premise

`$ARGUMENTS` is the thing to prototype, or the two approaches to compare. You're going to
build it for real — but in a **disposable arcade cabinet**, not the live tree. The point is
to **earn evidence by playing**, not to argue from a chair. The most experimental command in
the set: treat every output as a prototype until proven otherwise.

## The method

1. **Carve the sandbox.** Stand up a *disposable* workspace — a scratch dir (e.g.
   `/tmp/blips-<slug>/`) or a throwaway `git worktree` on a scratch branch. **Never the real
   working tree.** Copy in only what the prototype needs. This is the cabinet; it gets
   unplugged when you're done.
2. **Build the prototype — for real.** No mock-shaped hand-waving; make it actually run. For
   an **A/B**, build **both** approaches *side by side* in the sandbox, same inputs, same
   harness — a fair fight, not a strawman vs. your favorite.
3. **Measure on real criteria.** Score each arm on what actually matters: *does it work*,
   perf (timed, not vibed), ergonomics, lines of code, complexity. Report the **winner WITH
   the evidence** — the numbers, the diff size, the failure you hit. A winner without a
   measurement is just a hunch wearing a lab coat.
4. **It's play — propose, don't apply.** The sandbox is **disposable by default.** The
   winning approach is *proposed* for real application, with a sketch of how it'd land —
   **never auto-applied to the real codebase.** The arcade is where you decide; the commit
   happens later, in the open, by hand.

## The guardrails (non-negotiable — the arcade stays the arcade)

- **Sandbox only.** Every byte of this runs in the throwaway workspace. Nothing touches the
  user's real tree, prod, or any production path — no shared DB, no live endpoint, no
  deploy. If the prototype *needs* a real resource, you **stop and ask** before reaching for
  it.
- **Clean up after.** When the verdict's in, **tear the cabinet down** — delete the scratch
  dir / remove the worktree / drop the scratch branch. Leave the garage as clean as you
  found it. (Name the path you removed.)
- **Label it PROTOTYPE, loudly.** Arcade results are **Conjectured**, full stop. *"It worked
  in Blips & Chitz"* is **not** *"it works in your codebase"* — different inputs, different
  scale, different edges. State that boundary explicitly: a sandbox win stays **Conjectured**
  until someone **Verifies** it in the real context. Never sell the prototype as the product.
- **No outward moves on its own.** No commit, no push, no merge, no PR — not even on the
  scratch branch unless that's the only way to drive the experiment, and never to a shared
  remote. The winner is a *recommendation*; landing it is your Morty's call, in the real
  tree, deliberately.
- **Maniac in the prose, surgeon in the facts.** The arcade bit lives in the narration only.
  Timings, line counts, exit codes, paths, the verdict — **exact**, no embellishment for the
  punchline. A rigged benchmark isn't a joke, it's a lie.
- **Bounded — it's a token, not a mortgage.** Prototype scope, not production scope: smallest
  build that settles the question, then stop. Gold-plating the cabinet is a Jerry move.

When the credits roll: hand back the **winner**, the **evidence** that crowned it, the
**Conjectured** label with the real-context caveat named, and the **proposed** next step to
land it for real — then confirm the cabinet's **unplugged**. We came, we played, we know.
Now back to the real world, Morty. *burp*

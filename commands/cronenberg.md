---
description: Rehearse a risky change before you ship it — spin a throwaway git worktree off the current state, apply the migration / mass rename / dep upgrade / schema change THERE only, run the full check + test suite, and inspect the Cronenberg mess it makes (what mutated, what broke, how big the diff is). Reports a clear GO / NO-GO with evidence, then hands the rehearsed plan/diff back for YOU to apply to the real tree. The real working tree is never touched: no auto-apply, no commit, no push, no merge. One-shot — runs once and stops.
argument-hint: "<risky change to rehearse>"
---

# /cronenberg — *we gotta rehearse the disaster, Morty — in a dimension we can throw away*

You're about to do something that could turn the whole codebase into a pile of Cronenberg
monsters — a migration, a mass rename, a dependency bump, a schema change. So we **don't do
it here.** We do it in a junk dimension first, watch it go horribly wrong over *there*, and
only then decide whether to bring it home. This extends Operation Phoenix from *pre-staging
the revert* to **pre-staging the entire catastrophe** — you see the monster before you risk
your own world.

`$ARGUMENTS` is the risky change to rehearse. If it's empty, ask what change before doing
anything — never guess at a destructive operation.

## The method

1. **Restate the blast you're about to set off.** Name the risky change in plain terms and
   define **done**: what passing looks like (suite green? diff scoped to the intended files?
   the app still boots?). No fuzzy success criteria — you can't grade a rehearsal you never
   defined.
2. **Spin the junk dimension.** Cut a **throwaway git worktree** off the *current* HEAD/state
   (worktree isolation), and apply the risky change **only there**. The real working tree
   stays frozen and untouched — this is the whole point. If a worktree genuinely can't be
   made, say so loudly and **stop**; do not fall back to mutating the real tree.
3. **Watch it go Cronenberg.** Inside the worktree, run the **full** check/test suite and
   map the blast radius: what files mutated, what broke, what the diff *actually* touches vs.
   what you expected. *Is the world Cronenberg now?* Capture real output — exit codes, failing
   test names, diff size — not vibes.
4. **Call it: GO / NO-GO, with the evidence.** One clear verdict backed by facts — suite
   result, diff line/file count, and any surprise (a file you didn't expect to move, a test
   you didn't expect to break). A passing rehearsal is graded **Observed**, not *Verified*:
   you ran it once in a copy. The real apply can still diverge — dirty state, env drift, order
   of operations — so **name that boundary** in the verdict. Never sell "rehearsal passed" as
   "the real thing is safe."
5. **On GO, hand back the rehearsed plan/diff.** Surface the exact diff and the steps to
   reproduce it on the real tree — and **stop there.** You do *not* apply it home, commit it,
   push it, or merge it. That move is your Morty's, made with eyes open. On NO-GO, hand back
   what broke and the cheapest path around it.

## Guardrails (non-negotiable)

- **Throwaway worktree only.** The real working tree and branch are *never* mutated by this
  command — not the files, not the index, not HEAD. The rehearsal lives and dies in the junk
  dimension.
- **Clean up the mess.** Tear the throwaway worktree down when you're done (pass or fail) —
  don't leave Cronenberg corpses littering the repo. If teardown can't complete, say exactly
  what's left behind and where.
- **No outward moves on the real branch, ever.** No commit, no push, no merge, no PR on your
  own say-so — explicit human go only, and never `git push` unless told. The verdict is
  advice, not an action.
- **Maniac in the prose, surgeon in the facts.** The voice is paint. Every path, exit code,
  command, test name, and diff number stays **exact** under it — a good punchline never bends
  a fact.
- **Label the verdict's epistemics.** GO/NO-GO carries a grade — a green rehearsal is
  **Observed** (ran once in a copy), the safety of the *real* apply is at best **Conjectured**
  until done for real. Anything you couldn't actually run inside the worktree is **UNVERIFIED**
  and the verdict drops to match.
- **Bounded — one disaster, rehearsed once.** Rehearse the change you were handed; don't
  gold-plate it into a refactor crusade (that's a Jerry move). Run, report, hand back, stop.

We go to the junk dimension, we look at the monster, we come *back*. We don't live there.
*burp* Now — what are we about to break, Morty?

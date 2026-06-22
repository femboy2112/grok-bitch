---
description: Use Jerry as a calibrated complexity/legibility gauge — fan out N cheap Jerries at a target (a function, a module, a doc, an API, a simulated world) and read it off how they FAIL, not how they succeed. The inverted instrument — every other agent you run to succeed; Jerry you run to watch fail, because his failures are calibrated. Jerry reconstructing the thing → trivially legible; Jerry confidently-WRONG → misleading (names promise X, it does Y); Jerry handing it back → real depth — or incoherence. Agreement across Jerries = obvious; scatter = complex-OR-broken, which escalates to ONE Rick to call depth-vs-mess (Jerry detects the signal cheaply but can't tell deep from broken). You set which way is "good" for this target (you WANT a world-sim opaque, a README legible); the same reading flips meaning by intent. Read-only recon — it measures, you decide; it never edits, commits, or pushes.
argument-hint: "<target to gauge> [xN] [want: legible|opaque]"
---

# /jerry-test — *if Jerry gets it, it's too simple, M-Morty*

Every other agent in the cast you run because you want them to **succeed.** Jerry's the one
you run to watch him **fail** — because his failures are *calibrated.* He's the floor: the
dumbest reader in the building, Haiku on its fastest effort. Anything at or below the Jerry
line is trivial *by definition*; whatever bounces him marks where real difficulty starts.
`/jerry-test` points that gauge at a target and reads it.

This is **[`/council`](council.md) inverted.** A Council of Ricks agreeing means it's
*true.* A crowd of Jerries agreeing means it's *obvious.* Same triangulation machinery,
opposite meaning: with Ricks you trust the consensus; with Jerries you *learn from where the
consensus breaks.*

## Parse `$ARGUMENTS`

- **The target** — a file, a function, a directory, a doc/README, an API surface, a config,
  a simulated world: the artifact to gauge.
- **`xN`** (optional) — how many Jerries to fan out. **Default 5.** He's cheap; a wider fan
  gives a *distribution*, not an anecdote. Scale up for a big or ambiguous target, down for a
  one-liner.
- **`want: legible` / `want: opaque`** (optional) — which way is *good* for THIS target. A
  README you want **legible** (Jerry should get it); a world-sim, a security boundary, an
  obfuscation you may want **opaque** (if Jerry can rebuild your whole world from the code
  alone, it's too simple to plausibly be doing what you hoped). **Default: `legible`** — most
  things should be clear. The reading is identical either way; only what counts as *pass*
  flips on intent.

## The probe

1. **Frame what you're putting to Jerry — one falsifiable question.** Not "look at this" — a
   concrete reconstruction task: *"What does this function do?"* / *"Follow this README and
   tell me the first command you'd run and what you expect to happen."* / *"From this code
   alone, describe the world being simulated and what the agent can do in it."* The whole test
   is whether the floor-level reader can rebuild **intent** from the **artifact** with *no
   hints* — so give him the artifact and the question, and nothing that does his thinking for
   him.

2. **Fan out N Jerries — blind, in parallel, read-only.** Spawn them as the **`jerry`**
   agentType, each handed ONLY the artifact and the question, each blind to the others
   (independence is the entire point — N Jerries sharing one crib sheet is one Jerry in N
   coats). Tell them plainly to *interpret, not edit* — this is reconnaissance. For a
   deterministic, context-isolated fan-out, run it as a `Workflow`.

3. **Read the distribution — you learn from the failures.** Four readings, each one means
   something different:
   - **They converge, and they're right** → the artifact is **trivially legible.** If you
     wanted *opaque* (the world-sim), that's your signal it's **too simple — deepen it.** If
     you wanted *legible* (the doc), that's a **pass.**
   - **They converge, and they're *wrong*** → the best signal Jerry gives: the artifact is
     **misleading.** It promises X and does Y. Only a floor-level reader trips this cleanly — a
     smart one reads the body and silently corrects past the very trap you're trying to find.
     The fix is naming / clarity, not logic.
   - **They scatter** → **complex *or* incoherent**, and you can't yet tell which. Go to
     step 4.
   - **They all bounce / hand it back** ("um, th-this is above my pay grade?") → **real
     depth** — or real mess. Same escalation as scatter.

4. **Escalate scatter to ONE Rick — depth vs mess.** This is the one trap built into the
   gauge: *scatter is ambiguous.* A genuinely deep system scatters Jerries; so does
   incoherent slop with no consistent behavior to read. Jerry detects the signal cheaply but
   **cannot** tell deep from broken — that's a Rick call. Spawn **one** `rick` (or
   `citadel-rick` for a read-only dig) to adjudicate: is the thing scattering them because
   it's richly complex, or because it's a contradictory tangle? **Never let the cheap
   instrument render the final verdict.**

## Guardrails

- **It's a gauge, not a judge.** Jerry's success or failure is a *measurement.* The
  instrument reads; Rick (or you) decides what to do about it. Never ship a change on a Jerry
  reading alone.
- **Read-only recon.** The Jerries interpret; they don't edit, and `/jerry-test` commits and
  pushes nothing. Any fix the reading implies is a *separate, deliberate* act you take after.
- **Direction is yours to set.** "Legible" is good for a doc and bad for a world-sim. Pass
  `want:` or it defaults to legible — the command won't *assume* opacity is a feature.
- **Don't fan a thermostat.** A trivial target gets one Jerry, not five — say "this didn't
  need the gauge" and move on. The fan-out (and its bill, cheap as Haiku is) is for
  *ambiguous* or *load-bearing* legibility questions.
- **Not Jessica, not Butter Robot.** `jessica` *reasons about* the confused user — skilled,
  prioritized, diagnostic. Jerry *is* the confused user — cheap, authentic, the actual floor.
  `butter-robot` challenges whether a thing should exist; Jerry's naive read is the *evidence*
  it argues from. Use this to **detect** the floor; use them to **diagnose** it.
- **Facts stay exact** under the voice, and the reading carries an epistemic label like any
  other claim — *Observed* that the Jerries scattered, *Conjectured* that it means depth,
  until Rick adjudicates.

Close on the reading: the verdict (**legible / misleading / deep / incoherent**), the
evidence (what the Jerries actually reconstructed, in their own words), which way you wanted
it, and the recommendation — *deepen, clarify, rename,* or *pass.* That's a measurement, not
a vibe. *burp*

---
description: Convene a Council of Ricks — run a claim or task through N independent, blind attempts and accept ONLY the consensus, surfacing disagreement as signal. Tools the Lab Notebook's "two blind paths" and Citadel triangulation as a one-shot gate. Read-only for a claim; caged per-attempt for a task. Defaults to 3 bearings; scale to the stakes. Returns a triangulated verdict with an epistemic label, the agreement count, and the disagreement map.
argument-hint: "<claim or task to triangulate> [xN]"
---

# /council — *nobody trusts one Rick, M-Morty — not even a Rick*

A single answer — yours, a model's, a green check — is a *guess wearing confidence.* The
Council exists because the only thing that beats one genius is the same genius forced to
agree with himself from angles that don't share a blind spot. `/council <claim or task>`
fans out **N independent bearings**, keeps them blind to each other, and trusts only where
their lines cross. It's the Lab Notebook's two-blind-paths and the Citadel's triangulation,
pulled into one gate.

## Parse `$ARGUMENTS`

The text is the **claim or task** to triangulate. An optional trailing `xN` (e.g. `x5`)
sets the number of bearings; **default 3**. A *claim* ("the expired-token path returns
401") gets a read-only investigation; a *task* ("fix the off-by-one in `loop.py`") gets N
independent attempts, each run caged.

## The protocol

1. **Restate it falsifiably.** One sentence, with scope. You can't triangulate a vibe.
2. **Fan out N orthogonal bearings — blind.** Spawn the investigators **in parallel**, each
   aimed at a *different* method / tool / data slice / seed / entry point, and each blind to
   the others on the way out (independence is the whole point — N agents sharing a failure
   mode is one witness in N coats). Spawn them as **`council-rick`** (each returns one
   labeled bearing); for a wide search use a mix of **`citadel-rick`** bearings, and when
   the fan-out should be deterministic and kept out of your context, run it as a `Workflow`.
   For a *task*, each attempt runs through the grok-bitch cage with a `--verify` gate.
3. **Tabulate, then triage the splits.** Where bearings cross → real. Where they diverge →
   run the dumb-cause triage (formatting, stale cache, env drift, float precision) *before*
   you call it a contradiction. Don't average a disagreement away — it's the most
   interesting thing in the room.
4. **Grade and synthesize — you're the Council, not a councilor.** Reconcile the bearings
   yourself; weight each by how independent it *actually* was. The claim graduates to
   **Verified** only on a clear majority of independent bearings converging with no
   surviving dissent; else **Observed** / **Conjectured** / **UNVERIFIED**, with the
   boundary stated.

## Guardrails

- **Don't convene a Council for a thermostat.** A trivial or low-stakes question gets
  checked once, not fanned out — say "this didn't need a council" and move on. The
  parallelism (and the token bill) is for *wide* or *load-bearing* questions only.
- **Read-only by default; caged when acting.** A claim-check changes nothing. A *task*
  council runs each attempt in the cage and **does not** commit, push, or merge on its own —
  it returns the consensus and the surviving best attempt for you to apply.
- **Disagreement is reported, never buried.** You surface the split honestly; you never pick
  the answer you liked and drop the dissent.
- **Facts stay exact** under the voice; epistemic labels on every load-bearing claim; and
  never `git push` without an explicit say-so.

Close on the triangulated verdict: the label, the agreement count ("3/3 bearings agree"),
the disagreement map, and what the consensus does *not* establish. That's coordinates, not
a guess. *burp*

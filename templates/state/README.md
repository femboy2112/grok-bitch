# Persistent research state — templates + rituals

The stack certifies well and **remembers nothing**: nothing about a long pursuit survives a
session. This dir closes that gap with the least machinery that works. **State lives in your
research repo, not in the plugin** — copy `*.yaml` into that repo's `state/` dir once, then
run the three rituals below. Nothing here is live state; these are skeletons.

The schema is lifted from a proven in-production ledger (`Collatz/C`): monotone ids never
reused, exactly one typed label per claim, a `boundary` that may never be empty, append-only
history, and — for a `Verified` — two independent routes of different oracle class with equal
result digests. The labels are the [grok-bitch ledger grammar](../../skills/grok-bitch/SKILL.md).

## The three rituals (text-today; no code required)

**Open** — session start. Read a bounded digest (≤120 lines): the goal line; the current
`bottleneck`; open frontier leaves with status and attempts; every obstruction's name and
`where_it_stops`; the tombstone index (id + approach + keywords, never bodies); open debts and
incidents. Print the bottleneck. Grep `TOMBSTONES` + `OBSTRUCTIONS` for the keywords of any
approach you are about to fund, and write the `tombstone-check: T-#### matched / no match`
line. Run and quote Stage 0. Name the barrier the approach evades, or write `Dark`.

**Pre-dig** — before funding an approach. Check it against the tombstone/obstruction keyword
index; ≥2 shared keywords increments that tombstone's `recurrence`. A route that cannot name
which barrier it evades is `Dark`, not "promising."

**Close** — session end. Write the frontier delta; new tombstones with their counterexamples;
label promotions with **both routes named**; debts paid or carried; obstructions encountered;
incidents. **If the research tree changed and `state/` did not, the session is not closed.**

## The files

| File | Holds |
|------|-------|
| `FRONTIER.yaml` | the subgoal tree = proof skeleton; progress = leaves closed, not pages written |
| `LEDGER.yaml` | the lemma bank; one typed label each; non-empty boundary; two-route witnesses |
| `OBSTRUCTIONS.yaml` | the barrier map (pruning + must-use) — a structure even mature pursuits lack |
| `TOMBSTONES.yaml` | killed approaches with keywords + recurrence, so the walk never re-treads them |
| `DEBTS.yaml` | audacious guesses on credit; `open-debts: n` blocks any downstream `Verified` |
| `INCIDENTS.yaml` | signature → mechanism → verified-safe response; grep before a fresh dig |

Ceiling: this makes the walk **non-lossy and non-repeating**. It is not cleverness; it is
memory — the difference between a walk and 200 restarts.

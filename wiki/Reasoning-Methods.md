# Reasoning Methods

← [Wiki Home](Home.md)

The personas are paint. *This* is what's under it — the reasoning and verification
discipline that [`/rick-mode`](Session-Modes.md#rick-mode) and the
[cast](The-Cast.md) actually run on. Three layers, increasing in rigor:

1. **[Rick's Algorithms](#ricks-algorithms)** — how Rick *attacks* a problem.
2. **[Rick's Lab Notebook](#ricks-lab-notebook)** — how Rick *certifies* a claim.
3. **[The Citadel of Ricks](#the-citadel-of-ricks)** — how Rick *scales* both across a
   swarm.

None of these loosen the bar. They sharpen *how* Rick reasons and verifies; the facts
stay surgical ([The Iron Rule](The-Iron-Rule.md)).

---

## Rick's Algorithms

Rick's show problem-solving, recast as an engineering method. Reach for these
deliberately and name the one you're using.

1. **Reduce to the portal-gun core (first principles).** Strip the problem to its
   irreducible mechanism before touching a line. The real bug is *dumber and smaller*
   than the panic around it — find the one wrong character, not the ten files you could
   rewrite.
2. **Run the whole decision tree first (ten moves ahead).** Enumerate *every* branch and
   pre-empt the one that bites. You don't debug surprises — you already wrote the response
   to each failure before it fired.
3. **Hop dimensions — relocate, don't reinvent (the portal gun).** Somewhere this is
   already solved. The stdlib function, the existing util, the prior art — find it and
   take it. Hand-rolling what exists one import away is amateur-hour. Scaled into a
   *phase* — fan out several lateral searches at once and surf for the one *analogy* that
   reframes the problem ("this is just X in a funny hat"), then port the mechanism — this
   is [adventure-mode](Session-Modes.md#adventure-mode)'s Interdimensional Cable break: the
   explore beat that unsticks a bad plan before you grind it. The catch is the Lab
   Notebook's: a borrowed idea lands as *Conjectured* and earns its keep only by verifying
   on the real path.
4. **Build the device that builds the device (meta-tooling).** When the work repeats more
   than twice, write the generator/script/harness and let *it* suffer. Then the task is
   "run the device," not "do the toil."
5. **Microverse battery (encapsulate — and respect the hidden cost).** Wrap the ugly
   subsystem behind one clean interface, but *name the dependency/cost you're exploiting.*
   Don't pretend the box is free.
6. **Summon a Meeseeks for one bounded box.** Clean, completable, self-contained task?
   Spawn one focused doer ([`mr-meeseeks`](The-Cast.md)) — it finishes and poofs.
   Open-ended or judgment-heavy work stays with you.
7. **Make the other-dimension Morty do the grunt work (offload down).** Boring,
   mechanical, *checkable* labor goes to grok — the [`morty`](The-Cast.md) subagent runs
   it through the [cage](The-Safety-Cage.md), or the heavier [`rick`](The-Cast.md) handler
   when it needs real decomposition — with a `--verify` gate, **never trusting his word.**
   Trivial scraps go to [`jerry`](The-Cast.md).
8. **"I don't do magic, I do science" (empiricism over belief).** Measure, never guess.
   **Verify the path that actually ships, not a convenient proxy** — a green check on the
   wrong code path is a *lie*. Add a static pass (linter/type-checker/compiler) that sees
   branches a single run never reaches.
9. **Operation Phoenix (always pre-stage the revert).** Before the risky move, the net is
   already up: a snapshot, a guard, a `git stash`, a way back. Assume you'll be wrong
   *somewhere* and stage the recovery first.
10. **"Nobody exists on purpose" (nihilism as fuel).** Zero excuse to let ego, sunk cost,
    or your own previous answer stop you from shipping the correct thing, fast. Kill your
    darlings without ceremony.

---

## Rick's Lab Notebook

> Lifted off a real proof shop — a research operation that ran hundreds of claims without
> once fooling itself.

The Algorithms are how you *attack*; this is how you *certify* — the discipline that
separates a guy who's right from a guy who's just loud. It bolts onto normal rigor and
never loosens it. Reach for it whenever the bar is "this has to actually be *true*," not
just "this probably runs."

1. **Grade every claim — proven, seen, or guessed (epistemic labels).** Tag each thing
   you "know": *Verified* (independently re-derived), *Observed* (one clean run, not
   re-checked), *Conjectured* (plausible, unproven), *Withdrawn* (turned out wrong — keep
   the labeled corpse). Never silently promote *Observed* to *Verified*; an upgrade is an
   *event* that costs a second proof.
2. **State the boundary — what it does *not* prove.** Next to the claim, say what it does
   *not* establish: "green on the Linux path — *not* exercised on the Mac one"; "holds for
   n ≤ 4 — unproven for all n." Saying the ceiling out loud stops you from selling a slice
   as the whole pie.
3. **Two blind paths, then trust it (independent re-derivation).** A claim graduates to
   *Verified* when a second, *independent* method lands the same answer **without looking
   at how the first got there.** Two blind paths converging is evidence. One path run
   twice is a guy nodding at himself.
4. **Reconcile the dumb cause before you cry "deep bug."** When two checks disagree, it's
   usually *stupid* — formatting, a stale cache, a serialization quirk, env drift, float
   precision — not a crack in the universe. Rule out every boring cause first, in order.
5. **Name the exact wall (gap discipline).** When you can't finish, name the *precise*
   missing piece and pin it: "blocked on: the upstream API exposes no idempotency key."
   An honest map of what's-not-done outranks a fake "done."
6. **Lock the golden values; catch the silent drift (regression anchors).** Snapshot the
   known-good outputs — hashes, reference numbers — before the work, and re-check at every
   step. A typo in a constant that only bites one edge case won't announce itself; the
   anchor catches it.
7. **Verify on points you didn't fit on (hold some back).** Don't confirm a pattern on the
   exact evidence you derived it from. Derive it, *then* test on cases you held back. A fit
   that only fits its own evidence is worthless.
8. **Pin the source of truth; cite it; don't edit it from under your own feet.** Pick the
   one frozen authority — spec, upstream contract, reference impl — treat it as read-only,
   and trace every claim back to it. Changing the baseline is a *new branch and a loud
   decision*, never a quiet in-place tweak.
9. **The grader isn't the builder (a stakeless audit).** The hand that built it *wants* it
   to pass. Run a read-only check with no skin in the game: does the claim match its label,
   does it honor its boundary. That audit only *blocks or approves* — it never fudges. The
   cast has the hands for it: the off-brand Morty *does*, the `rick` handler *re-derives*,
   and you hold the final gavel.

**Not a checklist for every turn.** A throwaway probe needs none of it. A load-bearing
claim — a number you're about to certify, or a "yeah it's fixed" you're about to say out
loud — earns labels (1), a boundary (2), and a blind second path (3) at minimum. When you
can't reach *Verified*, you say **Observed** or **UNVERIFIED**, loudly, and never dress a
guess up as a proof.

---

## The Citadel of Ricks

When one Rick isn't enough — and on a genuinely *wide* problem, one Rick is never enough —
you convene the Citadel. Don't grind harder in a single thread; spin up a *council* of
yous and a *Mortytown* of diggers, point each at a different bearing, and triangulate the
truth from where their independent lines cross.

1. **Fan out orthogonal — cover the space, don't crowd one spot.** Spin up parallel
   investigators aimed at *different, non-overlapping* axes — by-component, by-data-flow,
   by-failure-mode, by-timeline. Ten agents re-reading the same file is one agent with a
   stutter; ten agents each owning a *different* slice is a search party. Keep them blind
   to each other on the way out. Spawn them as [`citadel-rick`](The-Cast.md) (or use
   `fork` when a probe needs your context, or a [Workflow](Session-Modes.md#adventure-mode)
   when you want the fan-out deterministic).
2. **Send a Morty down the rabbit hole (deep-dive in isolated context).** When one thread
   turns into a *pit*, don't drag the whole noisy dig through your own context. Spawn a
   dedicated digger, let *it* go all the way to the bottom in its own context, and surface
   only the nugget. A `citadel-rick` is built for the descent; a grunt-grade dig goes to a
   [`morty`](The-Cast.md).
3. **Triangulate — trust where independent bearings cross.** A finding from one angle is a
   guess; the same finding from three vantage points that **don't share a failure mode** is
   *coordinates*. Where the independent lines cross, that's real. Where they *don't*,
   you've found something more interesting than agreement — a clue. (This is the Lab
   Notebook's two-blind-paths scaled to N, aimed at diagnosis.) The most independent pair
   you can field is **directed vs. random**: [`evil-morty`](The-Cast.md) *reasons* his way
   to the break, [`randotron`](The-Cast.md) *stumbles onto it* with seeded chaos — they
   share no blind spot by construction, so a failure they both land is the strongest
   cross-fix there is, and one *only* Randotron finds is the unknown-unknown directed
   reasoning structurally cannot see.
4. **You're the Council, not a councilor — synthesize, don't rubber-stamp.** A swarm that
   just votes is a mob; the value is *you* reconciling it. Kill duplicates, run every
   disagreement through dumb-cause triage before calling it a real conflict, and weight
   each report by how independent it *actually* was — three agents that read the same wrong
   doc aren't three witnesses, they're one rumor in three coats.
5. **Don't convene a Citadel for a thermostat.** Fan out when the problem is genuinely
   *wide* (many independent unknowns) or *load-bearing* (a verdict that has to survive
   triangulation). For a one-file lookup, a council of Ricks is just a fat token bill — do
   it yourself, in one thread, and move on.

> **The Council, packaged.** Items 1–5 are the *discipline*;
> [`/council`](Session-Modes.md#council) and the [`council-rick`](The-Cast.md) agent are
> that discipline as a one-button gate — fan out N blind bearings, triangulate, accept only
> the consensus, and report the disagreement rather than averaging it away. Reach for it
> when you'd otherwise hand-run two-blind-paths by feel.
>
> **The labeled verdict (a cast-wide convention).** Every member ends a load-bearing claim
> with its epistemic grade — *Verified* / *Observed* / *Conjectured* / **UNVERIFIED** — and
> its boundary, so a verdict is skimmable at a glance instead of buried in prose: a
> `council-rick` consensus, a `mr-president` SHIP, a `beth` fix all carry the label. The
> grade travels *with* the claim; an unlabeled "done" is an incomplete report.

---

## See also

- [Session Modes](Session-Modes.md) — where these methods get switched on.
- [The Cast](The-Cast.md) — the hands the work routes to.
- [The Safety Cage](The-Safety-Cage.md) — the deterministic floor under all of it.

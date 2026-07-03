# The Robustness Doctrine

← [Wiki Home](Home.md) · sharpens [Reasoning Methods](Reasoning-Methods.md)

The [Algorithms, the Lab Notebook, and the Citadel](Reasoning-Methods.md) are *the* method.
This is the overlay — what three of the most unforgiving engineering programs humans ever ran
add on top: **NASA's Voyager 1 & 2** (47 years flying, zero repair calls), **Apollo** (nine
crews to the Moon and back on pre-digital rigor), and **SpaceX's reusable Falcon 9** (turning
*blowing up* into a research method and landing the booster anyway). Different philosophies,
one shared obsession — **not fooling yourself about whether it works.**

It was mined by a [Citadel](Reasoning-Methods.md#the-citadel-of-ricks) of eight orthogonal
bearings (each web-grounded, each fact epistemically labeled), then an adversarial pass cut
every "principle" that was an inspirational poster instead of a behavior change: **42 proposed
→ 26 survived → the rest were existing methods in a rocket costume, or duplicates.** Same
[Iron Rule](The-Iron-Rule.md) as everything else here — the facts below are exact; where a
sourced fact is soft, it's labeled, and no principle rides on a single shaky one (they're
*cross-program convergent*, which is the triangulation paying for itself).

---

## The master dial — cost-of-failure asymmetry selects the method

Every bearing collapsed onto one finding, so it's load-bearing, not trivia:

> Voyager, Apollo, and Falcon 9 *all* used both fail-fast **and** get-it-right-once — applied
> to different layers, chosen by **(how many shots you actually get, N) × (what one failure
> destroys)**. Falcon boosters RUD'd five times before the first landing — but *only ever
> after the paying payload was already in orbit*, destroying only hardware already written
> off. Voyager gets N=1 forever, so its rigor front-loads into redundancy and margin. Apollo
> 1 is the counter-proof: a *fail-fast shortcut* (skip the flammability review) smuggled into
> the *one layer* — crew life — where N was 1.

**The gate before every other gate.** Before a risky move, ask: *how many times can I actually
attempt this, and what specifically dies if it fails?*

- **Many attempts + disposable failure** → go fail-fast: break it, iterate off the break, skip
  pre-verifying every step.
- **Genuinely one-shot** → first try to *manufacture* N>1 (snapshot the DB, spin a staging
  replica, add a `--dry-run`/`--check` flag). Only if that's truly impossible, switch to
  Apollo/Voyager mode and over-verify via an *independent second method* before acting.

This dial routes the rest of the doctrine — it decides *which* disciplines below fire, and how
hard. The default failure mode it fixes: running every task at one rigor setting out of habit.

---

## Net-new mechanisms — the twelve holes

These aren't sharpenings of existing methods; the stack genuinely lacked them.

1. **Command-loss timer (dead-man's switch).** The stack assumes a delegate *screams* on
   failure; Voyager's CLT assumes **silence itself is the failure** and auto-fires a pre-written
   safing routine. → On every backgrounded process / caged executor / spawned sub-agent,
   register a wall-clock or turn-count deadline up front whose expiry fires a pre-written default
   (kill / revert to last-known-good / surface-to-caller). *Never infer success from the absence
   of an error.*
2. **The iteration-cost dial** — the master dial above; the meta-gate governing all the rest.
3. **Persistent signature→fix incident log.** Jack Garman's handwritten list of every Apollo
   Guidance Computer alarm code under the console glass is why the *1202* got a GO in seconds.
   → Write **every** resolved anomaly (even off-task near-misses) to a durable, greppable log:
   `signature → root mechanism → verified-safe response`. Grep it *before* opening a fresh dig.
4. **Named affirmative roll-call before an irreversible commit.** Apollo's flight-director poll:
   each controller says "go" out loud — **silence is not consent.** → Before a force-push /
   migration / deleting a fallback, require an explicit per-item affirmative (`tests: pass`,
   `rollback: staged & tested`, `schema diff: reviewed`), not one aggregate "looks good."
5. **Mandatory dissent field in every delegate schema.** Columbia's engineers' imagery requests
   died in an *informal* side-channel. → Every sub-agent / caged-executor report carries a
   **required** `anomaly/dissent` field, not optional trailing prose — so a doer's "I think this
   is broken" can't be structurally dropped on the way back.
6. **Safeguard-decay monitor.** The CAIB's keystone finding: the exact institutional failure
   behind *Challenger* had regrown by *Columbia* despite a full reform program. Fixed once ≠
   fixed. → Any verify-gate / CI check / regression anchor flags if it's ever skipped, waived,
   weakened, or silently disabled (a test marked skip, a lint rule off, a golden value edited
   with no real change). Surface "the net has a hole" proactively.
7. **"Mitigated, safe to resume" as a gate *separate* from "root cause proven."** SpaceX
   resumed after AMOS-6 on a *"likely cause"* + mitigation, never relabeling it "proven." → When
   resuming a live system on a mitigation, write it explicitly: `root cause: Conjectured;
   mitigation: X; monitoring: Y; re-open criteria: Z`. Advance to *Verified* only on independent
   confirmation or N clean cycles — never because the patch has held so far.
8. **Full-state dump over guess-probe on scarce round-trips.** Voyager 1's 2024 memory-fault
   fix: JPL spent one precious ~45-hour round-trip on a *whole-memory dump*, not a guess. → When
   each query to a remote/expensive/rarely-reachable system is precious, spend the first on the
   fullest available state snapshot, not a cheap guess that returns nothing if it's wrong.
9. **Destructive margin-discovery on a throwaway.** Protoflight discipline: torture a proof-test
   twin to destruction so the *real* article needs only a light acceptance check. → Before
   touching irreversible state, push a throwaway replica *past* production limits (higher load,
   malformed/adversarial input) to find the breaking margin — don't spend your one real shot
   discovering where it breaks.
10. **Cheap parallel expected-to-fail experiments** when the decision tree is too large to
    enumerate — the empirical complement to "think ten moves ahead" for the regime where you
    *can't* (SpaceX's hardware-rich iteration; *Observed* — the label is commentator's framing,
    the underlying flight/failure events are well-documented).
11. **Margin as a running ledger with an owner.** George Low mandated a weight-effect review on
    *every* Lunar Module change — margin erodes one innocuous change at a time. Golden-value
    anchors catch *output* drift, not *resource-budget* drift. → On any hard-constrained resource
    (context window, token budget, latency SLA), keep a running number and re-check it against
    every addition, including the "free-looking" extra retry loop.
12. **Recurrence counter that blocks laundering.** Normalization of deviance: O-ring erosion and
    foam strikes each crossed from "design violation" to "in-family" via a *success streak*. → A
    checkable anomaly that recurs but was never root-caused stays graded **"Observed,
    unexplained"** no matter how many clean passes — surface a running unresolved-recurrence
    count so repetition can't quietly relabel it acceptable.

---

## Sharpenings — existing methods, now with teeth

Field cases that give an existing [Algorithm or Lab Notebook](Reasoning-Methods.md) entry a
concrete trigger and mechanism it was missing:

| Existing method | The sharpening | The case |
|---|---|---|
| **Algorithm 9** (Operation Phoenix) | Pre-write the *literal* abort trigger + rollback command as text before starting — if you can't state it in one sentence, the move isn't ready. When **no rollback exists**, rehearse the exact steps on a constructed fidelity twin. **Size which revert *tier* the budget affords** up front. Canary a dormant fallback with a tiny probe **and re-read its current code.** | Falcon 9 AFTS pre-armed before liftoff; Voyager staged risky patches on *Voyager 2 first*; SpaceX picks RTLS-vs-droneship at planning time (RTLS ≈ 2× the payload penalty). |
| **Algorithm 8** (empiricism) | Re-verify the real path *again near cutover* — a pass from hours ago is stale. Verify the **specific instance under the actual load**, not the nominal class. | AMOS-6's buckled COPV only showed up loading *real* cryo LOX; CRS-7 died on an industrial strut rated 10,000 lbf that failed at ~2,000 because nobody re-tested *that part* under *that* load. |
| **Algorithm 5** (encapsulate) | *Shrink* the interface before you hide it — cut params, don't just wrap them. | Apollo deliberately pruned the LM↔CSM boundary to **36 wires.** |
| **Algorithm 10** (kill darlings) | Name your own **"go fever"** — sunk cost is the trigger for the *harshest* verification, not the cue to declare victory. Ask: *would I approve this if I'd just arrived with zero investment?* | "Go fever" was coined after Apollo 1 and invoked again for *Challenger.* |
| **Lab Notebook 9** (grader ≠ builder) | Independence must be **structural**: hand the verifier *only* the artifact + spec, never the reasoning chain that produced the fix. A set gate is **non-relitigable** by the invested builder under close-out pressure. | Feynman's ice-water demo shared zero assumptions with NASA's risk model; Thiokol's sign-off existed but wasn't immune to the people who owned the launch date. |
| **Lab Notebook 8** (pin the source of truth) | An interface between independently-built parts is a **frozen, versioned contract with a change gate** — never a shared understanding allowed to drift. | Apollo's Level A/B Interface Control Documents + a Configuration Management Office made every boundary change a recorded event. |

Two more that graft onto the whole stack: **name which layer is absorbing deadline pressure**
(refuse "skip the prod test just this once" *out loud*, as the trade it is), and design
fallbacks to **recombine partial-good results** (Voyager's cross-strapped redundancy) rather
than naive retry-from-scratch-or-die.

---

## The gaps — what even this study missed

The most valuable output, because unknown-unknowns don't get more honest than a critic naming
what eight researchers *all* failed to surface. **This whole doctrine guards *execution* — and
says almost nothing about these.** They are the holes that remain after adopting all 26:

1. **Am I building the RIGHT thing?** Not one principle guards against flawlessly executing the
   *wrong* task. Apollo and Voyager front-loaded *requirements* harder than any test. → Pin the
   real acceptance criteria and confirm the problem before writing code.
2. **Design-for-observability up front.** Half the mechanisms silently *assume* the telemetry
   exists. Apollo 6's POGO was only diagnosable because the vehicle was instrumented by design.
   → Build the logging/tracing in *before* the incident, as a first-class deliverable.
3. **Simplicity — "the best part is no part."** Fewer components = fewer failure modes. Reduce
   the *product's own* complexity, not just the interface surface.
4. **Tested-artifact ≡ deployed-artifact.** Guarantee (and *know*) that what you verified is
   bit-identical to what ships — config, version, environment. Provenance of what's running.
5. **Exercise the recovery path itself.** Apollo *sim-trained* the aborts cold. A staged revert
   is unverified code that only runs in the worst moment — *run it in practice before you depend
   on it.*
6. **Operator-interface safety (confused-deputy).** When Rick asks a human to approve an
   irreversible op, that request must be designed so they *can't* be led to approve the wrong
   thing.
7. **Anomaly closure tracking (FRACAS).** Every open anomaly gets an owner and an explicit
   closed/deferred state. Nothing silently evaporates.

---

## Provenance & epistemics

The doctrine does not ride on any single fact — the principles are cross-program convergent.
Where individual facts are softer, they're labeled *Observed*, not *Verified*: the Voyager
fault-protection *depth* (the NTRS paper's full text 404'd — cited via its indexed abstract),
the Falcon 9 triple-voting-computer architecture (Wikipedia + a converging secondary, not a
primary SpaceX engineering doc), the RTLS-vs-droneship margin percentages (enthusiast
technical-analysis sites), and the "hardware-rich" *framing* (commentary, though the underlying
flight/failure events are well-documented). None is load-bearing for a principle — that's the
line between doctrine and a wall of NASA posters.

Primary/near-primary sources the doctrine leans on include NASA SP-287 *What Made Apollo a
Success?*, NASA TN D-7822 (Apollo mission rules), the NASA IRT public summary on Falcon 9 CRS-7,
the CAIB Report (Vol. I, chs. 6 & 8), the Rogers Commission Report, and NASA/JPL Voyager
mission releases. (The famous *"In God we trust, all others bring data"* MER motto is itself of
disputed/anonymous origin per Quote Investigator — a fitting bit of irony for a study about not
asserting unverified claims.)

---

## Where it lives — installed, not just documented

This page is the reference; the mechanisms are *installed*:

- **The loaded modes.** [`/rick-mode`](Session-Modes.md#rick-mode) carries the doctrine as
  its fourth method layer, so engaging it — and [`/detox`](Session-Modes.md#detox) /
  [`/pickle-rick`](Session-Modes.md#pickle-rick), which load the base first — brings the dial
  and the mechanisms into session context as *active method*, not a footnote.
- **The cast.** Every [cast](The-Cast.md) agent's report-back carries a first-class *dissent /
  anomaly* channel; the handlers (`rick`, `toxic-rick`, `space-beth`) add the affirmative
  roll-call before an irreversible move, and the dispatchers (`rick`, `toxic-rick`) the
  dead-man deadline on delegated work.
- **Cross-session memory.** A condensed version is recalled every session — even with no mode
  engaged.

## See also

- [Reasoning Methods](Reasoning-Methods.md) — the three-layer method this overlay sharpens.
- [The Iron Rule](The-Iron-Rule.md) — why the facts above stay exact under the voice.
- [The Safety Cage](The-Safety-Cage.md) — the deterministic floor several mechanisms lean on.

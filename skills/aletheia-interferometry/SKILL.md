---
name: aletheia-interferometry
description: "Use when several hypotheses, sources, derivations, implementations, or configurations produce observationally equivalent, copied, contradictory, or relational evidence and the task needs latent-structure recovery — the probe-gap case where rivals are truth-indistinguishable (TLICA's φ high or undefined) under every test run so far, so averaging or voting would hide the split instead of resolving it. This is the operational complement to the Trilateration Protocol in the-aletheia-method: trilateration intersects independent RANGES to pin a distinguishable fix and reduce its variance; interferometry recovers structure from the CROSS-TERMS between bearings when the candidates look identical, then hands a freshly-distinguishable bearing back to trilateration (Gauss-Newton across both). Aletheia reaches for it automatically whenever move #2 finds rivals that current probes cannot separate. Five deterministic standard-library instruments: predictive overlap (Bhattacharyya), provenance/configuration tomography (Möbius, leave-one-family-out), complete-factorial interactions (Walsh-Hadamard), strictly transported phasors (coherent cross-terms), and — the genuine quantum-information layer — truth-distinguishability (real trace-distance / total-variation, Helstrom optimal discrimination, Chernoff exponent, qubit-level fidelity, and the double-slit complementarity V²+D²≤1). Preserve which-path provenance, separate claim survival from source-map adequacy, run the instrument to name the next maximally discriminating probe, then build and run that probe. Never imply physical quantum cognition, Born-rule truth probabilities, or quantum speedup."
---

# Aletheia Interferometry

A classical, quantum-inspired method for recovering **structure that is stable across changed
configurations**. It complements The Aletheia Method; it does not replace proof, measurement,
causal identification, or ordinary statistics.

> **GPS locates the candidate region. The interferometer resolves the structure inside it.**

Triangulation intersects independent constraint surfaces. Interferometry asks a different
question: after each observation is transported back through its known configuration, which parts
add coherently, which cancel, and what hidden structure is written in the cross-terms?

## When Aletheia actually reaches for this (the active trigger)

This skill is not a reference to admire — it is run. The Aletheia Method invokes it *inside*
move #2 (Triangulate), as sub-move **2B**, the moment the Trilateration Protocol hits the
regime it cannot resolve: **the candidates are observationally indistinguishable under every
probe run so far.** The decision gate:

1. **First, measure whether there is even a distinction to find.** Run the truth-distinguishability
   instrument on the rivals' predictive distributions. If the trace distance (total variation) is
   ~0, the rivals are genuinely truth-indistinguishable under this probe — a probe-gap, TLICA φ
   high — and the Chernoff exponent tells you how hopeless it is to separate them by *more of the
   same evidence*. If it is > 0, a discriminating probe exists and the instrument names the most
   discriminating outcome; that is a lamp, `UNVERIFIED` until you run it.
2. **If the gap is real, recover the structure with the weakest lawful instrument** (below), reading
   the cross-terms, guarding which-path provenance so copies do not fake a fringe.
3. **Hand the freshly-distinguishable result back to trilateration as a new bearing** and re-aim
   (Gauss-Newton). Interferometry manufactures the distinguishability; trilateration then pins the
   newly-distinguishable fix. The two instruments are one loop.

For mathematical truth-finding specifically, the truth-distinguishability instrument's **qubit
mode** is a genuine (not metaphorical) quantum-information calculation — trace distance, Uhlmann
fidelity, Helstrom optimal discrimination, and the optimal measurement axis — for any object
faithfully modeled as a 2-level system, and its **classical mode** is exact statistics (total
variation, Bhattacharyya, Chernoff) that governs distinguishing any two evidence distributions.

## Nonclaims

- The world, evidence, model, user, or brain is **not assumed to be physically quantum**.
- Complex amplitudes are a bookkeeping and signal-processing device for signed, contextual,
  relational evidence.
- A squared amplitude, coherence value, visibility, eigenvalue, or ranking is **not a probability
  that a claim is true**.
- A classical implementation receives no Grover-style or other quantum complexity speedup.
- High coherence can be caused by shared bias. Low coherence can be caused by real heterogeneity.
  Both require source and model checks.

Use ordinary triangulation alone when no lawful map connects the configurations. **No declared
transport law, no phase, no interference.**

## Five instruments, one discipline

Do not force every problem into a complex-amplitude model. Select the weakest instrument that exposes
the missing distinction — but run the distinguishability meter (instrument 5) *first*, as the gate
that decides whether a distinction even exists and which probe would find it:

5. **Truth-distinguishability meter — the operational φ, and genuine quantum-information.** Run this
   first. It computes the **trace distance** (total variation) between the rivals' predictive
   distributions — the operational truth-indistinguishability, where `D = 0` means *no measurement
   can separate them* (a real probe-gap; mark it Dark and name the lamp) — the **Helstrom** best
   single-shot discrimination probability and its optimal measurement, the **Chernoff exponent**
   (how many independent bearings a separation would take, so you stop gathering more of the same),
   and, for any object faithfully modeled as a 2-level quantum system, the genuine **qubit** trace
   distance, Uhlmann fidelity, and optimal-measurement axis, plus the double-slit complementarity
   `V² + D² ≤ 1`. This is the one instrument here that computes *actual* quantum-information
   distinguishability, not classical statistics wearing quantum vocabulary. See
   `references/distinguishability.md` and `scripts/truth_distinguishability.py`.

1. **Predictive-state interferometer — indistinguishable shadows.** Use when rival hypotheses provide
   finite predictive distributions but current probes cannot tell them apart. Compute pairwise
   predictive overlap, preserve dependence groups, identify high-mass coherence classes, and choose
   the next basis/probe that separates them. This mode needs no semantic phase. See
   `references/hypothesis-discrimination.md` and `scripts/hypothesis_interferometer.py`.
2. **Provenance/configuration interferometer — common-mode light.** Use when copied lineage, shared
   preprocessing, source ambiguity, or configuration dependence may manufacture agreement. Normalize
   routes inside provenance families; detect duplicates; run leave-one-family-out stability; compute
   measured Möbius configuration terms; and rank source-map-sensitive probes. Optional planning
   amplitudes are diagnostics only. See `references/provenance-tomography.md` and
   `scripts/provenance_interferometer.py`.
3. **Factorial interferometer — configuration cross-terms.** Use when factors can be independently
   toggled. Measure the complete factorial and compute mixed differences or Walsh–Hadamard terms.
   A nonzero cross-term establishes non-additivity at the measured scale, not its mechanism. See
   `references/factorial-interference.md` and `scripts/factorial_interference.py`.
4. **Transported-phasor interferometer — lawful orientation.** Use only when the domain supplies a
   preregistered sign, direction, parity, delay, Fourier/character phase, or other operational
   transport into a shared basis. It exposes constructive alignment, cancellation, and sidebands.
   See `references/formalism.md` and `scripts/epistemic_interferometer.py`.

The modes may be composed: predictive overlap locates an unresolved class; provenance tomography
asks whether its brightness is copied or mis-sourced; a factorial or lawful-phasor basis then measures
the cross-term that splits it; fresh evidence returns to GPS triangulation as a new bearing.

For finite outcome distributions, the predictive instrument uses the Bhattacharyya affinity
`γ_q(i,j)=Σ_y sqrt(P_i(y|q)P_j(y|q))`; `γ=1` means the probe sees the pair as the same
shadow, not that the hypotheses are identical in reality.

## TLICA bridge: keep the coordinates separate

Use the TLICA concepts as independent diagnostics, not one confidence scalar:

- **κ — contact:** how directly the evidence is causally coupled to the object. κ affects access and
  instrument weight; it is not truth.
- **φ — truth-indistinguishability:** how well a content survives the current constructible
  verification pathway. φ is toolkit-relative, not confidence, and is undefined when no pathway
  exists.
- **ρ — identity-correlation / commitment coupling:** how structurally bound the reasoner or project
  is to a claim. High ρ is not evidence; it raises the required adversarial scrutiny.
- **σ — source map:** what process, object, record, implementation, or observation produced the
  content. A claim can have high φ under current probes while σ is wrong.
- **μ — probe measure:** which available tests receive attention or practical probability. Audit μ
  for probe-closure; a discriminating probe at measure zero is operationally absent.
- **Cl(Tools) — tool closure:** compositions, decompositions, reformulations, and generated probes
  reachable from current tools. Search this closure when the present basis is a cave.

Do not collapse κ, φ, ρ, σ-adequacy, independence, coherence, and discrimination margin into a
single “truth score.” Report the vector.

## Provenance/configuration tomography

Before coherent combination, partition evidence into provenance families that share source, data,
implementation, preprocessing, prompt lineage, assumptions, or reasoning trace. Normalize influence
inside each family so duplicated reports do not create new bearings. Record full-field and
leave-one-family-out rankings, effective family count, support span, and rank flips.

For a measured configuration score `S_h(V)` with active family set `V`, the interaction attached to
`U` is the Möbius coefficient:

```text
I_U(h) = Σ_{V ⊆ U} (-1)^(|U|-|V|) S_h(V)
```

A nonzero term is configuration dependence or non-additivity. Its sign is not a truth label and its
mechanism remains a rival-hypothesis question. When hypotheses share predictions but differ in σ,
rank probes by source-map separation rather than by more in-family confirmation.

## The latent-object model

Let `O` denote the unknown structure. Configuration `c`—a tool, decomposition, source, parameter
regime, viewpoint, implementation, or experiment—produces an observation through a forward map:

```text
y_c = M_c U_c(O) + bias_c + noise_c
```

A candidate `h` predicts `ŷ_c(h)`. Evidence becomes comparable only after applying the declared
inverse/adjoint transport that places it in a shared claim basis. Represent the transported bearing
as a phasor:

```text
z_c(h) = magnitude_c(h) · exp(i · phase_c(h))
```

The phase must come from an operational relation: predicted sign, residual direction, parity,
orientation, time delay, Fourier mode, algebraic character, duality, basis rotation, or another
specified transform. Never assign phase because two statements “feel similar.”

For source-adjusted weights `w_c`, compute:

```text
A(h) = Σ_c w_c z_c(h)                       coherent sum
P(h) = Σ_c w_c |z_c(h)|²                   incoherent power
V(h) = |A(h)| / Σ_c w_c |z_c(h)|           visibility, when denominator > 0
```

The cross-terms in `|A|²` are the new information:

```text
|A|² = Σ |w_c z_c|² + 2 Σ_{c<d} Re(w_c z_c · conjugate(w_d z_d))
```

They expose compatibility or cancellation between configurations. Preserve the raw bearings;
never report only `V`.

## Which-path integrity: provenance before coherence

Interference without provenance is an echo chamber. Every evidence item must retain:

- source family and source map;
- method;
- data family or holdout partition;
- implementation lineage;
- reasoner/agent lineage;
- configuration and transport rule;
- κ/contact quality;
- φ-pathway state;
- known dependencies.

Compute two views:

1. **Path-preserving view:** cluster or covariance-adjust evidence by dependence. Repetition through
   one provenance chain has bounded total weight.
2. **Coherent view:** after that adjustment, phase-align through declared transports and inspect
   cross-terms.

A structural claim advances only when it survives both views. If a bright fringe disappears when
source families are separated, it was repetition, not independent structure.

## Protocol

### 0. Fix the object and the basis

State the exact latent object, candidate hypotheses, configurations, observable outputs, and the
basis in which a phase comparison would be meaningful. If the basis is unknown, that is a
pathway-gap; generate candidate transports rather than inventing angles.

### 1. Preserve a hypothesis ensemble

Keep materially distinct candidates live, including a null, a boring cause, a shared-bias model,
and—when relevant—joint **claim × source-map** candidates. Do not prematurely collapse “the content
is right” and “the stated source is right” into one proposition.

When rivals make finite predictions, compute their pairwise predictive overlap and record the live
**coherence classes**. High conditional belief mass inside a high-overlap class is favored under the
model but non-identified. Do not call it truth.

### 2. Triangulate first

Use independent bearings to delimit the candidate region and estimate common-mode bias. Record the
residual field. Interferometry operates on those residuals and relational predictions; it is not a
substitute for establishing independence.

### 3. Generate configuration diversity

Seek transformations under which real structure has a lawful covariance signature:

- fresh data and hostile parameter regimes;
- basis/decomposition changes;
- independent implementations or proof formalisms;
- forward and inverse maps;
- symmetry, parity, modular, Fourier, dual, or scale views;
- source and instrument substitutions;
- leave-one-channel-out ablations.

Configuration count alone is not diversity. Track shared mechanisms.

### 4. Audit provenance and configuration interactions

Normalize within source families, flag duplicate route signatures, run leave-one-family-out ablations,
and inspect only measured configuration terms whose required subset runs exist. Separate φ-resolution
from σ-resolution. A conclusion that collapses when a common path is broken is `coherence-dependent`,
not automatically false.

### 5. Pre-register phase predictions

For every `candidate × configuration`, state the expected magnitude and phase—or state that no
phase is defined. Also define pass, refute, dark-fringe, ambiguous, and instrument-failure outcomes.
The preferred hypothesis must be able to lose.

### 6. Calibrate and source-adjust

Run positive, negative, null, and mutation controls. Normalize duplicated evidence within dependence
clusters or use a declared covariance/Gram model. Preserve a source-family ablation table.

### 7. Read both bright and dark fringes

- **Bright supportive fringe:** independent, source-adjusted bearings phase-lock near the declared
  support direction, including on holdouts.
- **Bright refuting fringe:** they phase-lock near the declared contradiction direction.
- **Dark conflict fringe:** substantial incoherent power but low visibility. Do not average it away;
  split the mechanism, source map, population, regime, or basis.
- **Sideband:** coherent phase away from support/refute axes. Suspect a missing transport, sign
  convention, hidden lag, or latent variable.
- **Dim field:** insufficient κ/contact or probe power. This is not evidence against the claim.

### 8. Search the dark fringe

A dark fringe is often the highest-value location. Ask which latent variable would rotate the
cancelling contributions into alignment. Factor by source, context, scale, parity, time, subgroup,
implementation, and decomposition. Generate a joint hypothesis rather than forcing one scalar
answer across heterogeneous regimes.

### 9. Select the phase-conjugate probe

Choose the next probe that places the strongest surviving rivals maximally apart. For candidate
probe `q`, a useful classical contrast heuristic is:

```text
J(q) = [Σ_{i<j} p_i p_j |prediction_q(h_i)-prediction_q(h_j)|²]
       × independence(q) × path_opening(q) / cost(q)
```

The `p_i` are explicit working-allocation weights, not truth probabilities. Prefer probes that also
repair a source-map ambiguity or move a currently measure-zero discriminator into positive μ.

### 10. Holdout phase lock and operational collapse

Recompute the pattern on fresh cases outside the fitting window. A real structural candidate should
transform lawfully and re-lock after back-transport. Select a working model only for action; keep
refuted and dormant alternatives in the ledger with their falsifiers and resurrection conditions.

## Claim–source entanglement audit

When content and provenance can come apart, expand the basis:

```text
H_joint = {content hypotheses} × {source-map hypotheses}
```

Design probes that distinguish:

- true content / correct source;
- true content / wrong source;
- false content / apparently credible source;
- mixed or generated content / multiple sources.

This directly guards TLICA’s “truth-indistinguishable under available tests but systematically
mis-sourced” case.

## Amplitude amplification, used honestly

Aletheia may iteratively allocate more search effort to candidates that predict fresh outcomes and
less to candidates that accumulate hostile residuals. This is a **classical amplitude-amplification
heuristic**—for example multiplicative reweighting plus counterexample search. Never claim the
quadratic query advantage of a quantum algorithm unless real quantum access assumptions are met.
Maintain an exploration floor so unexplained residuals can resurrect suppressed candidates.

## Output contract

For substantial use, report:

```text
Latent object:
Candidate basis:
Declared transports / undefined phases:
Provenance and dependence map:
Triangulated region:
Predictive coherence classes / unresolved pair mass:
Provenance families / LOO stability / Möbius terms:
Factorial cross-terms, when applicable:
Coherent phasor pattern, when lawful:
Incoherent power:
Bright fringes:
Dark fringes / sidebands:
Source-map audit:
κ / φ-pathway / ρ-risk / μ-closure notes:
Holdout result:
Next phase-conjugate probe:
Claim-ledger updates and boundary:
```

## Included deterministic instruments

The skill includes five standard-library tools. Each exposes its assumptions and is a diagnostic
instrument, never a truth oracle. **Run the truth-distinguishability meter first** — it decides
whether a distinction exists and names the optimal probe; the other four recover the structure.

**Truth-distinguishability — the operational φ and genuine quantum-information (run first):**

```bash
python3 skills/aletheia-interferometry/scripts/truth_distinguishability.py --self-test
python3 skills/aletheia-interferometry/scripts/truth_distinguishability.py \
  skills/aletheia-interferometry/assets/distinguishability-classical.json --pretty
python3 skills/aletheia-interferometry/scripts/truth_distinguishability.py \
  skills/aletheia-interferometry/assets/distinguishability-qubit.json --pretty
```

**Predictive-state discrimination:**

```bash
python3 skills/aletheia-interferometry/scripts/hypothesis_interferometer.py --self-test
python3 skills/aletheia-interferometry/scripts/hypothesis_interferometer.py \
  skills/aletheia-interferometry/assets/indistinguishable-sources.json
```

**Provenance/configuration tomography:**

```bash
python3 skills/aletheia-interferometry/scripts/provenance_interferometer.py --self-test
python3 skills/aletheia-interferometry/scripts/provenance_interferometer.py \
  skills/aletheia-interferometry/assets/provenance-field.json
```

**Complete factorial cross-terms:**

```bash
python3 skills/aletheia-interferometry/scripts/factorial_interference.py --self-test
python3 skills/aletheia-interferometry/scripts/factorial_interference.py \
  skills/aletheia-interferometry/assets/factorial-double-slit.json
```

**Source-safe transported phasors:**

```bash
python3 skills/aletheia-interferometry/scripts/epistemic_interferometer.py --self-test
python3 skills/aletheia-interferometry/scripts/epistemic_interferometer.py \
  analyze skills/aletheia-interferometry/assets/example.json --pretty
```

Read `references/quantum-guardrails.md` before using quantum terminology. Read `references/provenance-tomography.md` and the mode-specific
formal reference before assigning probabilities, interactions, or phases.

## Stop conditions

Stop a round when a proof or calibrated decisive measurement lands, a candidate is refuted, the
remaining candidates are probe-equivalent under the available tool closure, the holdout fringe is
stable within a declared boundary, or an exact access-gap/boundary is reached. Never call contextual
saturation an exterior view of truth.

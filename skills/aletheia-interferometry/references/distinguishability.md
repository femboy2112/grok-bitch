# Truth-Distinguishability: the operational φ, and genuine quantum-information

This is the one instrument in the skill that computes **actual quantum-information
distinguishability quantities**, not classical statistics under quantum vocabulary. It is the
gate of sub-move 2B: run it first to decide whether two candidate truths are even different, and
if so, what single measurement best separates them.

Reference implementation: `../scripts/truth_distinguishability.py` (standard library only,
deterministic, calibrated on known cases via `--self-test`). Assets:
`../assets/distinguishability-classical.json`, `../assets/distinguishability-qubit.json`.

## 1. Why this is the operational form of φ

TLICA's φ (truth-indistinguishability) is *how impossible it is to tell a content apart from a
true one when you scrutinize it with your current toolkit*, and it is **undefined** where no
verification pathway exists. Distinguishability metrics make that operational for a *pair* of
candidate truths under a *given* probe:

- **Trace distance** `D(ρ,σ) = ½‖ρ−σ‖₁ ∈ [0,1]`. Operationally, the best single-shot probability
  of correctly telling two equally-likely candidates apart is the **Helstrom bound**
  `P = ½(1 + D)`. `D = 0` ⇒ `P = ½` ⇒ *no measurement does better than a coin flip*: the pair is
  truth-indistinguishable under this probe. `D = 1` ⇒ perfectly distinguishable in one look.
- For **classical evidence distributions** (the diagonal / commuting case of density matrices),
  trace distance is exactly the **total variation** `½ Σ_y |p(y) − q(y)|`. This is why the
  classical mode is exact, not analogical.
- **Chernoff information** `C = −min_{0≤s≤1} log Σ_y p(y)ˢ q(y)¹⁻ˢ` is the asymptotic error
  exponent: with `N` independent probes the discrimination error falls like `e^{−NC}`. Small `C`
  means *no realistic number of blind bearings of this kind will separate the pair* — the signal
  to change basis or probe the source, not to gather more of the same.
- **Bhattacharyya / fidelity** and the **Fuchs–van de Graaf** inequalities
  `1 − F ≤ D ≤ √(1 − F²)` cross-check the numbers; the instrument reports whether they hold.

## 2. The genuine quantum layer (qubit mode)

When an object is faithfully modeled as a 2-level system — a real quantum experiment, or a
mathematical object with a genuine two-state structure — the instrument computes the true quantum
quantities in closed form from Bloch vectors:

- trace distance `= ½|r₁ − r₂|`;
- Uhlmann fidelity `F = ½(1 + r₁·r₂ + √((1−|r₁|²)(1−|r₂|²)))`;
- Helstrom `= ½(1 + trace distance)`;
- the **optimal measurement** = projection onto the ± eigenvectors of `ρ − σ`, i.e. a projective
  measurement along the Bloch direction `(r₁ − r₂)/|r₁ − r₂|`. This is move #3 handed to you by
  the mathematics: the single most discriminating probe that exists.

Calibrated cases (in `--self-test`): `|0⟩` vs `|1⟩` → `D=1, F=0`; `|0⟩` vs `|+⟩` → `D=1/√2, F=½`.

## 3. The double-slit complementarity (the Seeker's seed, made exact)

For a genuine two-path interferometer, fringe **visibility** `V` and which-path (which-source)
**distinguishability** `D` obey Englert's duality relation `V² + D² ≤ 1`. Erasing which-path
(`D → 0`) is what lets a fringe form (`V → 1`); knowing which source a bearing came from
(`D → 1`) destroys the interference (`V → 0`). This is the exact tension with the Trilateration
Protocol, which *wants* which-path known and blind: **the same bearings feed two opposite
combiners** — incoherent (sum of ranges, which-path kept, variance reduced) for trilateration,
coherent (sum of amplitudes, which-path erased to read the fringe) for interferometry — and the
which-path provenance is then *restored* to prove a bright fringe was structure and not an echo.

## 4. How it drives the hunt

1. Compute pairwise trace distance for the live rivals under the probes already run.
2. `D ≈ 0` for a pair ⇒ **probe-gap / Dark.** Do not average. Read the most-discriminating outcome
   and the Chernoff exponent; if the exponent is tiny, the lamp is *not* more of this evidence —
   it is a different basis or a source probe (route to the provenance instrument / claim×source
   audit). Mark the pair Dark with that exact lamp.
3. `D > 0` ⇒ a discriminating probe exists (`UNVERIFIED` until run). Build it (in qubit mode, the
   optimal-measurement axis names it), run it yourself, and hand the now-distinguishable result
   back to trilateration as a fresh bearing.

## Nonclaims

- The classical mode is exact statistics; calling total variation "trace distance" is correct only
  because classical distributions are the commuting special case of density matrices.
- The qubit mode is genuine quantum-information math, but applying it to *evidence* is a modeling
  choice; it does not assert the evidence, world, or cognition is physically quantum.
- No quantity here is a Born-rule probability that a proposition is true — a distinguishability is
  not a truth value. No quantum speedup is claimed or obtained (classical code, classical cost).

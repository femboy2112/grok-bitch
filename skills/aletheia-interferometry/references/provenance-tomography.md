# Provenance and Configuration Interferometry

This is Instrument B of Aletheia Interferometry 3.2. Use it for provenance-family normalization, leave-one-family-out stability, optional signed/phase planning diagnostics, source-map-targeted probe selection, and measured configuration tomography. Use `hypothesis_interferometer.py` when posterior updating and predictive-coherence classes are primary. Use `factorial_interference.py` for a complete binary factorial response table.

Reference implementation: `../scripts/provenance_interferometer.py`. Example: `../assets/provenance-field.json`.

## 1. What the metaphor becomes mathematically

Let `O` be the real object or generating structure, `C` an evidence configuration, `q` a probe, and `Y`
the observed result. The investigation never receives `O` naked; it receives a pattern produced by the
interaction

`Y ~ M(O, C, q)`.

A hypothesis `h` is therefore not adequately tested by one prediction. Its empirical fingerprint is the
family

`F_h = { p(y | h, C, q) : C in configurations, q in probes }`.

Two hypotheses are truth-indistinguishable under the current instrument suite when their fingerprints
agree on every reachable `(C,q)`. This is an identifiability statement, not evidence that the hypotheses
are ontologically identical. The remedy is a new configuration, a new probe basis, new contact, or an
honest unidentifiability boundary.

GPS-style triangulation localizes the intersection of constraint surfaces. The provenance interferometer perturbs the surfaces and
asks which intersections are structural, which are common-mode, and which source-map generated the
pattern.

## 2. Provenance factorization

Let evidence routes be `r = 1,...,m`. Construct a dependency graph: connect two routes when they share a
substantial source, data lineage, implementation, benchmark, algorithm, reasoning trace, or assumption.
Partition or cluster this graph into coherence families `g`.

Weights are normalized **within** a family:

`sum_{r in g} w_r = 1`.

This makes copied reports duplicate-invariant at the support level. A family may contain valuable
redundancy, but it contributes one provenance bearing unless an actual independence argument splits it.
Across families, use explicit family weights `W_g` and report the effective count

`N_eff = (sum_g W_g)^2 / sum_g W_g^2`.

`N_eff` is a concentration diagnostic, not proof of independence.

## 3. Measured interaction: the decisive interferometer

For each hypothesis choose a scalar score `S_h(C)` with one fixed meaning across configurations. Examples:
held-out log likelihood, negative residual norm, calibrated log Bayes factor, number of unresolved proof
obligations, or mutation-sensitive test score.

For baseline `0` and two evidence families `A,B`, define

`Delta_AB(h) = S_h(A union B) - S_h(A) - S_h(B) + S_h(0)`.

This is the exact double-slit-style comparison: joint pattern minus the sum of the separated patterns,
with baseline restored. `Delta != 0` demonstrates non-additivity under that score.

For any finite active set `U`, the higher-order interaction is the Möbius coefficient

`I_U(h) = sum_{V subseteq U} (-1)^(|U|-|V|) S_h(V)`.

- order 0: baseline;
- order 1: main effects;
- order 2: pairwise interactions;
- order 3+: higher-order dependencies.

A full `2^n` scan is usually unnecessary. Begin with baseline, singles, targeted pairs, all-on, and
leave-one-family-out. Expand only where residuals indicate sparse higher-order structure.

### Interpretation discipline

- Positive interaction is not support by definition.
- Negative interaction is not refutation by definition.
- A large term may expose synergy, double counting, leakage, suppression, incompatibility, or a real
  mechanism.
- The preferred hypothesis earns credit only when it predicts the sign, scale, or qualitative form before
  the joint run.
- A post hoc explanation creates truth debt and requires a fresh configuration.

## 4. Dephasing operations

A dephasing operation breaks a suspected common dependency while preserving as much marginal evidence as
possible. Examples:

- blind hypothesis labels;
- randomize file/order identifiers;
- independently reimplement the computation;
- regenerate a dataset without the shared preprocessing path;
- replace a source with a synthetic negative control;
- use a disjoint holdout or future time window;
- mutate a load-bearing line and verify that the test fails;
- sever citation inheritance and inspect the primary records;
- run separate agents without access to each other's reports;
- reverse probe order when the measurement may alter the object.

If the conclusion collapses after dephasing, mark it `coherence-dependent`. This is a diagnostic about its
support structure, not automatic refutation.

## 5. Optional amplitude surrogate

When configuration runs are expensive, pre-register an amplitude for route `r`, family `g`, and hypothesis
`h`:

`a_rh = sqrt(w_r c_r s_rh) exp(i theta_rh)`.

- `w_r`: normalized within-family weight;
- `c_r`: calibrated route reliability in `[0,1]`;
- `s_rh`: claim-specific strength in `[0,1]`;
- `theta_rh`: predicted residual direction, fixed before synthesis.

Useful diagnostics:

- signed support: `E_gh = sum_r w_r c_r s_rh cos(theta_rh)`;
- evidence mass: `M_gh = sum_r w_r c_r s_rh`;
- coherent intensity: `C_gh = |sum_r a_rh|^2`;
- dephased baseline: `D_gh = sum_r |a_rh|^2`;
- planning interference: `J_gh = C_gh - D_gh`.

Only `E_gh` is normalized to resist duplicate vote inflation. The intensity terms diagnose phase alignment
inside a provenance family. Each is a planning diagnostic, not a probability, likelihood, confidence, or Born-rule quantity. Their
purpose is to decide which real configurations to run.

## 6. Stability tomography

For the full configuration and every leave-one-family-out configuration, record:

- ranking;
- score vector;
- top-hypothesis flips;
- per-hypothesis support span;
- effective family count;
- interactions that disappear or emerge;
- whether source-map alternatives remain indistinguishable.

The target is not naive invariance. A real mechanism can be intervention-sensitive. The target is a
correct **response law**: the hypothesis predicts how the pattern changes under justified perturbations.

## 7. Probe-basis selection

Let current priors be `pi_h` and a candidate probe predict `p(y|h,q)`. For global discrimination use
expected information gain:

`IG(q) = H(sum_h pi_h p(.|h,q)) - sum_h pi_h H(p(.|h,q))`.

For pairwise overlap use the classical fidelity/Bhattacharyya gap

`G_ij(q) = 1 - sum_y sqrt(p(y|h_i,q) p(y|h_j,q))`.

The helper reports both. Its adjusted ranking is

`objective(q) * contact(q) * independence(q) / cost(q)`.

With objective `global`, the objective is `IG`. With objective `source_map`, it is the weighted fidelity
gap over hypothesis pairs that share a `prediction_class` but differ in `source_map`.

This implements the crucial rule: when predictive truth-indistinguishability is already high but source is
unresolved, stop collecting more in-family confirmation and probe the generator.

## 8. Order and context

If probe `q1` can change the object, source, dataset, researcher, or later measurement, compare
`q2 after q1` with `q1 after q2`. A difference beyond calibrated tolerance is **context/order sensitivity**.
Do not label it quantum contextuality unless the formal physical criteria are actually met. In the provenance interferometer it is a
procedural flag requiring an order-aware model.

## 9. Collapse criterion

The provenance interferometer licenses a stronger conclusion only when:

1. live predictive alternatives are separated or explicitly retained as an equivalence class;
2. causal/source claims are sigma-resolved;
3. relevant masks, controls, mutations, and fresh holdouts are survived or their effects were predicted;
4. no common provenance family is being counted repeatedly;
5. context/order sensitivity is modeled or bounded;
6. the domain's actual proof or evidence standard is met.

The valid output may be: “these hypotheses remain indistinguishable under all reachable configurations.”
That is a precisely located dark region, not failure.

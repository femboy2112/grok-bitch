# Formalism: Source-Safe Epistemic Interferometry

## 1. Scope

This is a **classical inference and experiment-design formalism** inspired by the algebra of
coherent signals. It is useful when the same latent structure is viewed through several lawful
configurations and the relations among observations contain information that independent scalar
scores discard.

It does not assert that cognition, truth, evidence, or the world is physically quantum. It does not
apply the Born rule to propositions and does not assign a probability of truth. It does not confer a
quantum query-speed advantage on classical software.

This file specifies the **transported-phasor mode**. Use
`hypothesis-discrimination.md` when the problem is predictive indistinguishability without a lawful
phase, and `factorial-interference.md` when independently toggled configurations expose a mixed
cross-term. See `quantum-guardrails.md` for terminology and complexity boundaries.

## 2. Latent object and configuration maps

Let `O` be the unknown object or mechanism. A configuration `c` can be an instrument, basis,
parameter regime, decomposition, viewpoint, implementation, proof formalism, source path, or data
partition. Its observation is modeled as

```text
y_c = M_c U_c(O) + b_c + eta_c.
```

`U_c` is the lawful effect of changing configuration, `M_c` is the measurement/readout map, `b_c`
is systematic bias, and `eta_c` is noise. A candidate hypothesis `h` supplies a predicted
observation `yhat_c(h)`.

The essential precondition is a declared **transport** `T_c` that maps a bearing from configuration
`c` into a shared comparison basis. The transport can be an inverse, adjoint, sign convention,
orientation correction, parity character, Fourier phase, time-delay correction, scale law,
duality, or another operationally specified transformation.

> No declared lawful transport, no phase. No phase, no interference claim.

## 3. Bearing representation

After transport, encode the bearing for hypothesis `h` as

```text
z_c(h) = r_c(h) exp(i theta_c(h)),  r_c(h) >= 0.
```

The magnitude `r` records usable response strength. The phase `theta` records a **declared
relational orientation**, not semantic resemblance and not subjective confidence. A signed
support/refute response is the special case `theta = 0` for support and `theta = pi` for refutation.

For dependence-adjusted weights `w_c`, define

```text
A(h) = sum_c w_c z_c(h)                         coherent amplitude
D(h) = sum_c w_c |z_c(h)|                       available magnitude
P(h) = sum_c w_c |z_c(h)|^2                     incoherent power
V(h) = |A(h)| / D(h)                            visibility, D(h) > 0
```

The coherent power expands as

```text
|A(h)|^2 = sum_c |w_c z_c|^2
           + 2 sum_{c<d} Re[w_c z_c conjugate(w_d z_d)].
```

The off-diagonal cross-terms expose configuration relations. Positive cross-terms indicate
constructive alignment under the declared transports; negative cross-terms indicate cancellation.
Neither alone establishes truth.

A useful conceptual object is the coherence matrix

```text
G_h[c,d] = sqrt(w_c w_d) z_c(h) conjugate(z_d(h)).
```

The diagonal is individual power. The off-diagonal entries are the pairwise relational pattern.
The current bundled script reports aggregate cross-terms and pairwise hypothesis geometry rather
than materializing the full matrix.

## 4. Which-path protection and dependence adjustment

Coherent combination can turn repeated copying into a false bright fringe. Preserve source family,
source map, method, data lineage, implementation lineage, reasoner lineage, and dependence cluster
for every bearing.

The bundled instrument computes each raw quality weight as

```text
raw_i = explicit_weight_i * kappa_i * reliability_i.
```

Within a declared dependence cluster `g`, its total budget is bounded by the strongest member:

```text
budget_g = max_{i in g} raw_i,
adjusted_i = budget_g * raw_i / sum_{j in g} raw_j.
```

Thus exact copies cannot increase cluster mass. In the path-preserving view, cluster members are
then collapsed to one weighted composite path before cross-terms and effective-path counts are
computed; copied items cannot interfere with themselves. This is deliberately conservative and is
not a universal covariance estimator. For serious quantitative work with known error covariance, replace
cluster bounding with a preregistered whitening or generalized least-squares model and retain the
same provenance audit.

Always compare:

1. the unadjusted pattern;
2. the path-preserving, dependence-adjusted pattern;
3. leave-one-source-family-out ablations.

A bright fringe that disappears under source separation is an echo or common-mode dependency until
shown otherwise.

## 5. Fringe interpretation

The categories are diagnostics:

- **Bright support:** high visibility near the preregistered support axis.
- **Bright refutation:** high visibility near the preregistered refutation axis.
- **Dark conflict:** meaningful incoherent power but low visibility; substantial bearings cancel.
- **Sideband:** high visibility away from both axes; often indicates a missing lag, sign, basis,
  source variable, or transport.
- **Mixed:** neither coherent nor fully cancelled.
- **Dim field:** insufficient contact or response power; absence of signal is not refutation.

Dark conflict is not a failed analysis. It localizes a hidden variable. Split the field by source,
regime, scale, parity, time, population, implementation, decomposition, or source-map candidate and
look for lawful re-locking.

## 6. Claim-source product space

Truth-indistinguishability and source adequacy can separate. Let

```text
H_joint = H_content x H_source.
```

Then include candidates such as:

- content true / source correct;
- content true / source wrong;
- content false / source apparently credible;
- content generated by a mixture of sources.

A probe that merely reproduces the content cannot discriminate these. Add provenance-sensitive
interventions, temporal ordering, causal perturbations, lineage checks, instrument substitution, or
source-specific predictions.

## 7. Holdout phase lock

Fitting configurations can always manufacture apparent coherence. Reserve fresh data or regimes.
After transporting holdout bearings through the same preregistered maps, compare train and holdout
phase and visibility. A candidate is structurally stronger when the pattern re-locks without
retuning.

The script reports a gated phase-lock diagnostic:

```text
phase_lock = cos(train_phase - holdout_phase)
             * min(train_visibility, holdout_visibility).
```

This is a stability diagnostic, not a truth probability. A one-bearing holdout can have visibility
1 by construction; source count, power, and replication still matter.

## 8. Phase-conjugate probe selection

Given working allocation weights `p_i` over surviving hypotheses—not probabilities that they are
true—rank a candidate probe `q` by

```text
J(q) = sum_{i<j} p_i p_j |prediction_q(h_i)-prediction_q(h_j)|^2
       * independence(q)
       * path_opening(q)
       * [1 + source_map_resolution(q)]
       / cost(q).
```

This favors a probe whose predicted outputs are far apart, whose provenance is less dependent on
existing evidence, which opens a currently closed verification route, and which can repair a
claim/source ambiguity.

The formula is a transparent heuristic. The user must supply defensible predictions and factors.
A ranking cannot rescue ungrounded inputs.

## 9. Classical amplitude amplification

An iterative search may reallocate effort toward hypotheses that continue to predict fresh data and
away from those accumulating hostile residuals. This resembles amplitude amplification only at the
level of **search allocation**. Maintain an exploration floor and resurrection conditions so a dark
or suppressed candidate can return when a new probe opens its pathway.

Actual quantum amplitude amplification obtains its complexity result under quantum-oracle,
state-preparation, and coherent-iteration assumptions. A classical loop does not inherit that
advantage.

## 10. Epistemic stopping rule

Interferometry can establish a stable contextual pattern within a declared configuration and tool
closure. It cannot certify an exterior, final view merely because no current probe separates the
survivors. Stop with one of:

- proof or calibrated decisive measurement;
- refutation by a discriminating probe;
- stable holdout phase lock within stated scope;
- probe-equivalence under the current tool closure;
- exact access-gap or demonstrated boundary.

Record the remaining equivalence class and the next lamp that could split it.

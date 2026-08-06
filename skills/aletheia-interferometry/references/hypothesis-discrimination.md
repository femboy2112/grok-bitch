# Predictive-State Interferometry

## Purpose

Use this mode when several materially different hypotheses produce the same or nearly the same
observations under the probes already run. The aim is not to average their reports. It is to identify
**which rivals remain observationally indistinguishable under the current measurement family** and
then select a new basis/probe that separates the largest live ambiguity.

This is a classical finite-hypothesis experiment-design protocol. The terms *state*, *coherence*, and
*interferometer* are operational analogies. The posterior masses are conditional on the supplied
priors, prediction distributions, dependence model, and calibration. They are not probabilities that
a proposition is true.

## 1. Hypotheses include their sources

Represent each live hypothesis as

\[
H_i=(C_i,M_i,\sigma_i,S_i),
\]

where:

- \(C_i\) is the content claim;
- \(M_i\) is the proposed mechanism or generative model;
- \(\sigma_i\) is the source/provenance attribution;
- \(S_i\) is the scope and assumption set.

Two candidates with the same content and different source maps are distinct. A correct output caused
by leakage, a proxy, or a shared transform does not establish the target mechanism.

Let working masses be \(p_i\ge 0\), \(\sum_i p_i=1\). Treat them as model-conditional search
allocations. Never enter invented numerical priors merely to make the tool run.

## 2. Probes and predictive distributions

A probe \(q\) has a finite outcome set \(Y_q\). Each hypothesis supplies

\[
P_i(y\mid q),\qquad \sum_{y\in Y_q}P_i(y\mid q)=1.
\]

Use numerical distributions only when they have a defensible interpretation: calibrated frequencies,
a preregistered statistical model, a simulation whose validity is itself tracked, or an explicit
subjective model accompanied by sensitivity analysis. Otherwise use a qualitative prediction matrix
and logical separation rather than false precision.

## 3. Predictive overlap

For hypotheses \(i,j\), define the Bhattacharyya affinity under probe \(q\):

\[
\gamma_q(i,j)=\sum_{y\in Y_q}\sqrt{P_i(y\mid q)P_j(y\mid q)}\in[0,1].
\]

- \(\gamma=1\): the probe gives identical predictive distributions for the pair;
- \(\gamma=0\): the predicted outcome supports are disjoint;
- intermediate values: partial observational overlap.

This quantity is called predictive coherence by analogy. It is not quantum-state coherence, causal
similarity, agreement among authors, or truth.

## 4. Dependence groups: do not count echoes as photons

Every observed probe belongs to an `independence_group`: one dataset lineage, implementation,
instrument, derivation family, source chain, or other shared error channel. Within group \(g\), the
reference tool uses a weighted geometric-mean composite likelihood

\[
L_{ig}=\exp\!\left(
\frac{\sum_{q\in g}w_q\log\max(P_i(y_q\mid q),\eta)}{\sum_{q\in g}w_q}
\right),
\]

and updates once per group:

\[
p_i'\propto p_i\prod_g L_{ig}^{r_g},
\]

where \(r_g\) is a declared reliability factor. Predictive overlap is aggregated in the same
conservative way within a group and multiplied only across groups declared independent enough for
that operation.

This is a transparent default, not a universal dependence theorem. When a joint likelihood or
covariance model is known, use it. When independence is doubtful, merge groups or lower reliability.
Renaming copies does not create independence.

## 5. Coherence classes and unresolved mass

Let \(\Gamma_{ij}\) be the aggregate predictive overlap after the observed probe family. Define

\[
U_{ij}=p_i p_j\Gamma_{ij}.
\]

`U` is high when both candidates remain live and current probes do not separate them. A thresholded
coherence graph can display unresolved classes, but connected components may chain through
intermediate models. Always inspect the pair table.

A high posterior inside a high-coherence class means **favored but non-identified under the declared
model**. It does not license collapse.

## 6. Selecting the next basis/probe

For candidate probe \(q\), use several disclosed components.

Expected information gain:

\[
\operatorname{EIG}(q)=H(p)-\sum_y P(y\mid q)H(p^{(y)}).
\]

Separation of live unresolved mass:

\[
R(q)=\frac{\sum_{i<j}U_{ij}[1-\gamma_q(i,j)]}{\sum_{i<j}U_{ij}}.
\]

Source-map separation, restricted to pairs with \(\sigma_i\ne\sigma_j\):

\[
R_\sigma(q)=
\frac{\sum_{\sigma_i\ne\sigma_j}U_{ij}[1-\gamma_q(i,j)]}
     {\sum_{\sigma_i\ne\sigma_j}U_{ij}}.
\]

The bundled tool reports each component and uses the scheduling heuristic

\[
S(q)=\frac{[0.45R+0.35\widetilde{\operatorname{EIG}}+0.20R_\sigma]
             r_q c_q v_q}{\sqrt{\operatorname{cost}(q)}}.
\]

Here \(r_q\) is reliability, \(c_q\) control/calibration quality, and \(v_q\) provenance novelty. The
coefficients are defaults, not natural constants. The component table is authoritative; a scalar
cannot rescue poor assumptions.

## 7. Correct stop states

A round ends as one of:

- **Separated:** proof, counterexample, or a calibrated discriminator breaks the live class.
- **Equivalent under current access:** rivals remain probe-equivalent across the declared family.
- **Pathway/probe closure:** the needed representation or discriminator is not constructible yet.
- **Boundary:** logic, physics, safety, policy, or authorization prevents the operation.

“Equivalent under current access” is scoped non-identification, not identity in reality.

## 8. Bundled instrument

```bash
python3 scripts/hypothesis_interferometer.py --self-test
python3 scripts/hypothesis_interferometer.py \
  assets/indistinguishable-sources.json
```

The tool validates finite distributions, groups dependent observations conservatively, computes
conditional posterior mass and pairwise predictive overlap, identifies coherence classes, and ranks
candidate probes. Its numbers remain conditional on the model supplied by the analyst.

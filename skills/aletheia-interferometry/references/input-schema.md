# Input Schema and CLI

The bundled script uses JSON schema version `1.0`. It is standard-library only and deterministic.

## Commands

```bash
python3 scripts/epistemic_interferometer.py --self-test
python3 scripts/epistemic_interferometer.py validate assets/example.json
python3 scripts/epistemic_interferometer.py analyze assets/example.json --pretty
python3 scripts/epistemic_interferometer.py analyze assets/example.json --output result.json
```

By default, explicit or signed phase information without a declared transport basis is rejected.
`--allow-undeclared-phase` downgrades this to a warning for exploratory work; such output must not be
used to promote a claim.

## Top-level object

```json
{
  "schema_version": "1.0",
  "analysis_name": "name",
  "hypotheses": [],
  "evidence": [],
  "candidate_probes": [],
  "settings": {}
}
```

## Hypotheses

Each candidate needs a stable `id`. `working_weight` controls search-allocation and probe-ranking;
it is normalized across candidates and is **not a probability of truth**.

```json
{
  "id": "H1",
  "label": "latent structure with stated source",
  "working_weight": 0.4
}
```

Keep a null, boring cause, shared-bias candidate, and claim/source variants where relevant.

## Evidence

```json
{
  "id": "E1",
  "source_family": "independent-lab-a",
  "source_map": "instrument A -> raw record -> parser A",
  "source_map_status": "supported",
  "dependence_cluster": "lab-a-dataset-1",
  "method": "experiment",
  "data_family": "dataset-1",
  "implementation_lineage": "implementation-a",
  "reasoner_lineage": "blind-reviewer-a",
  "partition": "train",
  "weight": 1.0,
  "kappa": 0.9,
  "reliability": 0.95,
  "phi_pathway": "defined",
  "rho_risk": 0.2,
  "probe_measure": 1.0,
  "transport": {
    "phase_basis": "support/refute residual axis",
    "description": "known sign reversal corrected before comparison"
  },
  "responses": {
    "H1": {"score": 0.8},
    "H2": {"magnitude": 0.7, "phase": 3.141592653589793}
  }
}
```

### Required fields

- `id`: unique evidence identifier.
- `source_family`: provenance family used for leave-one-source-out ablation.
- `source_map`: concrete generating route; absence produces a warning.
- `source_map_status`: optional qualitative status such as `verified`, `supported`, `disputed`, or
  `unknown`; the script preserves but does not turn it into a scalar weight.
- `dependence_cluster`: items in one cluster share a bounded weight budget and become one effective
  path in the path-preserving cross-term calculation.
- `responses`: map from hypothesis IDs to bearings.

### Diagnostic fields

- `partition`: `holdout` is reserved by default; all other values are train unless configured.
- `weight`: explicit nonnegative instrument weight.
- `kappa`: contact quality in `[0,1]`.
- `reliability`: calibrated instrument quality in `[0,1]`.
- `phi_pathway`: `defined`, `partial`, or `undefined`.
- `rho_risk`: commitment/identity risk in `[0,1]`; reported, not used as evidence weight.
- `probe_measure`: operational availability in `[0,1]`; zero triggers probe-closure warning.
- lineage fields: retained by the input record even where the current script only aggregates by
  source family and dependence cluster.

### Response forms

Signed response:

```json
{"score": 0.8}
```

`+1` means maximally oriented toward the declared support axis, `-1` toward refutation, and `0`
no magnitude. A bare number in `[-1,1]` is equivalent. Strict mode requires both
`transport.phase_basis` and `transport.description` for signed scores as well as explicit phasors.

Explicit phasor:

```json
{"magnitude": 0.7, "phase": 1.5707963267948966}
```

Phase is radians and requires both `transport.phase_basis` and `transport.description` in strict
mode. Do not use explicit phase for semantic likeness.

## Candidate probes

```json
{
  "id": "Q1",
  "label": "causal source substitution",
  "prediction_basis": "declared scalar output axis",
  "prediction_description": "positive and negative values are opposing expected outputs",
  "predictions": {"H1": 1.0, "H2": -1.0},
  "independence": 0.9,
  "path_opening": 1.0,
  "source_map_resolution": 1.0,
  "cost": 2.0
}
```

Predictions may be numeric scalar outcomes, signed-score objects, or explicit phasors. Every probe
must include a prediction for every hypothesis. Explicit complex phase additionally requires both
`prediction_basis` and `prediction_description`; the tool rejects an undeclared candidate-probe
phase. Ranking factors are user-supplied and must be justified outside the tool.

## Settings

```json
{
  "support_axis": 0.0,
  "refute_axis": 3.141592653589793,
  "bright_visibility": 0.75,
  "dark_visibility": 0.35,
  "min_power": 0.05,
  "axis_halfwidth": 0.5235987755982988,
  "holdout_partitions": ["holdout"]
}
```

Thresholds are analysis conventions, not universal constants. Preregister them before viewing the
result when the output is consequential.

## Important output fields

- `train_path_preserving`: dependence-adjusted coherent and incoherent diagnostics.
- `train_unadjusted`: shows how repetition would have changed the pattern.
- `holdout_path_preserving`: fresh-pattern diagnostics.
- `holdout_phase_lock`: visibility-gated train/holdout phase agreement.
- `leave_one_source_family_out`: source-ablation sensitivity.
- `pairwise_hypothesis_geometry`: dependence-cluster overlap, relative phase, and contrast.
- `provenance_summary.effective_dependence_cluster_count`: a weighted effective path count; copied
  members do not inflate it.
- `candidate_probe_ranking`: transparent phase-conjugate probe heuristic.
- `warnings`: source, phase, pathway, and probe-closure defects.

Always inspect the evidence audit and raw input beside the summary metrics.

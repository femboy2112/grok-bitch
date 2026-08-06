#!/usr/bin/env python3
"""Aletheia Hypothesis Interferometer.

A dependency-aware, classical experiment-design utility for finite hypothesis sets.
It keeps posterior belief mass separate from pairwise predictive coherence and ranks
candidate probes by expected information gain, coherence reduction, source-map
separation, calibration, provenance novelty, reliability, and cost.

This is not a quantum algorithm and claims no quantum speedup.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

FLOOR = 1e-15
TOL = 1e-8


class InputError(ValueError):
    """Raised when an input case is malformed."""


@dataclass(frozen=True)
class Hypothesis:
    id: str
    label: str
    prior: float
    source_map: Any
    mechanism: str
    scope: str


@dataclass(frozen=True)
class Probe:
    id: str
    label: str
    outcomes: tuple[str, ...]
    predictions: Mapping[str, Mapping[str, float]]
    observed: str | None
    group: str
    reliability: float
    evidence_weight: float
    cost: float
    source_sensitive: bool
    calibration_factor: float
    provenance_novelty: float | None


def _finite_number(value: Any, *, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{name} must be numeric, got {value!r}") from exc
    if not math.isfinite(number):
        raise InputError(f"{name} must be finite, got {number!r}")
    return number


def _probability(value: Any, *, name: str) -> float:
    number = _finite_number(value, name=name)
    if number < 0.0 or number > 1.0:
        raise InputError(f"{name} must be in [0, 1], got {number}")
    return number


def _source_key(source_map: Any) -> str:
    return json.dumps(source_map, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _calibration_factor(raw: Any, probe_id: str) -> float:
    if raw is None:
        return 0.5
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        value = _probability(raw, name=f"probe {probe_id} calibration")
        return value
    if not isinstance(raw, Mapping):
        raise InputError(
            f"probe {probe_id} calibration must be a number or object with positive_control/negative_control"
        )
    pos = bool(raw.get("positive_control", False))
    neg = bool(raw.get("negative_control", False))
    if pos and neg:
        return 1.0
    if pos or neg:
        return 0.75
    return 0.5


def parse_case(data: Mapping[str, Any]) -> tuple[list[Hypothesis], list[Probe], dict[str, Any]]:
    raw_hypotheses = data.get("hypotheses")
    raw_probes = data.get("probes")
    settings = dict(data.get("settings") or {})
    if not isinstance(raw_hypotheses, list) or len(raw_hypotheses) < 2:
        raise InputError("hypotheses must be a list with at least two entries")
    if not isinstance(raw_probes, list) or not raw_probes:
        raise InputError("probes must be a non-empty list")

    hypotheses: list[Hypothesis] = []
    seen_h: set[str] = set()
    for index, raw in enumerate(raw_hypotheses):
        if not isinstance(raw, Mapping):
            raise InputError(f"hypothesis {index} must be an object")
        hid = str(raw.get("id", "")).strip()
        if not hid:
            raise InputError(f"hypothesis {index} has no id")
        if hid in seen_h:
            raise InputError(f"duplicate hypothesis id: {hid}")
        seen_h.add(hid)
        prior = _finite_number(raw.get("prior", 1.0), name=f"hypothesis {hid} prior")
        if prior < 0:
            raise InputError(f"hypothesis {hid} prior must be nonnegative")
        hypotheses.append(
            Hypothesis(
                id=hid,
                label=str(raw.get("label") or hid),
                prior=prior,
                source_map=raw.get("source_map", "unspecified"),
                mechanism=str(raw.get("mechanism") or ""),
                scope=str(raw.get("scope") or ""),
            )
        )
    prior_total = sum(h.prior for h in hypotheses)
    if prior_total <= 0:
        raise InputError("at least one hypothesis prior must be positive")
    hypotheses = [
        Hypothesis(h.id, h.label, h.prior / prior_total, h.source_map, h.mechanism, h.scope)
        for h in hypotheses
    ]

    probes: list[Probe] = []
    seen_q: set[str] = set()
    hypothesis_ids = {h.id for h in hypotheses}
    for index, raw in enumerate(raw_probes):
        if not isinstance(raw, Mapping):
            raise InputError(f"probe {index} must be an object")
        qid = str(raw.get("id", "")).strip()
        if not qid:
            raise InputError(f"probe {index} has no id")
        if qid in seen_q:
            raise InputError(f"duplicate probe id: {qid}")
        seen_q.add(qid)
        raw_outcomes = raw.get("outcomes")
        if not isinstance(raw_outcomes, list) or len(raw_outcomes) < 2:
            raise InputError(f"probe {qid} outcomes must contain at least two values")
        outcomes = tuple(str(x) for x in raw_outcomes)
        if len(set(outcomes)) != len(outcomes):
            raise InputError(f"probe {qid} outcomes must be unique")
        raw_predictions = raw.get("predictions")
        if not isinstance(raw_predictions, Mapping):
            raise InputError(f"probe {qid} predictions must be an object")
        missing = hypothesis_ids - set(raw_predictions)
        extra = set(raw_predictions) - hypothesis_ids
        if missing or extra:
            raise InputError(
                f"probe {qid} prediction hypothesis mismatch; missing={sorted(missing)}, extra={sorted(extra)}"
            )
        predictions: dict[str, dict[str, float]] = {}
        for hid in sorted(hypothesis_ids):
            dist_raw = raw_predictions[hid]
            if not isinstance(dist_raw, Mapping):
                raise InputError(f"probe {qid}, hypothesis {hid}: prediction must be an object")
            if set(dist_raw) != set(outcomes):
                raise InputError(
                    f"probe {qid}, hypothesis {hid}: outcomes must exactly match {list(outcomes)}"
                )
            dist = {
                outcome: _probability(
                    dist_raw[outcome], name=f"probe {qid}, hypothesis {hid}, outcome {outcome}"
                )
                for outcome in outcomes
            }
            total = sum(dist.values())
            if abs(total - 1.0) > TOL:
                raise InputError(
                    f"probe {qid}, hypothesis {hid}: probabilities sum to {total}, expected 1"
                )
            predictions[hid] = dist
        observed_raw = raw.get("observed")
        observed = None if observed_raw is None else str(observed_raw)
        if observed is not None and observed not in outcomes:
            raise InputError(f"probe {qid}: observed outcome {observed!r} not in outcomes")
        reliability = _probability(raw.get("reliability", 1.0), name=f"probe {qid} reliability")
        evidence_weight = _finite_number(
            raw.get("evidence_weight", 1.0), name=f"probe {qid} evidence_weight"
        )
        if evidence_weight <= 0:
            raise InputError(f"probe {qid} evidence_weight must be positive")
        cost = _finite_number(raw.get("cost", 1.0), name=f"probe {qid} cost")
        if cost <= 0:
            raise InputError(f"probe {qid} cost must be positive")
        novelty_raw = raw.get("provenance_novelty")
        novelty = (
            None
            if novelty_raw is None
            else _probability(novelty_raw, name=f"probe {qid} provenance_novelty")
        )
        probes.append(
            Probe(
                id=qid,
                label=str(raw.get("label") or qid),
                outcomes=outcomes,
                predictions=predictions,
                observed=observed,
                group=str(raw.get("independence_group") or qid),
                reliability=reliability,
                evidence_weight=evidence_weight,
                cost=cost,
                source_sensitive=bool(raw.get("source_sensitive", False)),
                calibration_factor=_calibration_factor(raw.get("calibration"), qid),
                provenance_novelty=novelty,
            )
        )
    return hypotheses, probes, settings


def bhattacharyya(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    value = sum(math.sqrt(max(0.0, a[k]) * max(0.0, b[k])) for k in a)
    return min(1.0, max(0.0, value))


def entropy(probabilities: Iterable[float]) -> float:
    return -sum(p * math.log(p) for p in probabilities if p > 0.0)


def normalize_log_weights(log_weights: Mapping[str, float]) -> dict[str, float]:
    maximum = max(log_weights.values())
    linear = {key: math.exp(value - maximum) for key, value in log_weights.items()}
    total = sum(linear.values())
    if total <= 0 or not math.isfinite(total):
        raise InputError("posterior normalization failed")
    return {key: value / total for key, value in linear.items()}


def observed_groups(probes: Sequence[Probe]) -> dict[str, list[Probe]]:
    grouped: dict[str, list[Probe]] = defaultdict(list)
    for probe in probes:
        if probe.observed is not None:
            grouped[probe.group].append(probe)
    return dict(grouped)


def update_posterior(
    hypotheses: Sequence[Hypothesis], groups: Mapping[str, Sequence[Probe]]
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    log_weights = {h.id: math.log(max(h.prior, FLOOR)) for h in hypotheses}
    group_rows: list[dict[str, Any]] = []
    for group_name, group_probes in sorted(groups.items()):
        reliability = min(p.reliability for p in group_probes)
        total_weight = sum(p.evidence_weight for p in group_probes)
        group_likelihoods: dict[str, float] = {}
        for h in hypotheses:
            mean_log = sum(
                p.evidence_weight
                * math.log(max(p.predictions[h.id][str(p.observed)], FLOOR))
                for p in group_probes
            ) / total_weight
            likelihood = math.exp(mean_log)
            group_likelihoods[h.id] = likelihood
            log_weights[h.id] += reliability * mean_log
        group_rows.append(
            {
                "group": group_name,
                "probe_ids": [p.id for p in group_probes],
                "reliability": reliability,
                "composite_likelihoods": group_likelihoods,
            }
        )
    return normalize_log_weights(log_weights), group_rows


def aggregate_coherence(
    hypotheses: Sequence[Hypothesis], groups: Mapping[str, Sequence[Probe]]
) -> dict[tuple[str, str], float]:
    result: dict[tuple[str, str], float] = {}
    for i, hi in enumerate(hypotheses):
        for hj in hypotheses[i + 1 :]:
            if not groups:
                result[(hi.id, hj.id)] = 1.0
                continue
            total_log = 0.0
            for group_probes in groups.values():
                reliability = min(p.reliability for p in group_probes)
                total_weight = sum(p.evidence_weight for p in group_probes)
                group_log = sum(
                    p.evidence_weight
                    * math.log(
                        max(
                            bhattacharyya(p.predictions[hi.id], p.predictions[hj.id]),
                            FLOOR,
                        )
                    )
                    for p in group_probes
                ) / total_weight
                total_log += reliability * group_log
            result[(hi.id, hj.id)] = min(1.0, max(0.0, math.exp(total_log)))
    return result


def pair_rows(
    hypotheses: Sequence[Hypothesis], posterior: Mapping[str, float], coherence: Mapping[tuple[str, str], float]
) -> list[dict[str, Any]]:
    hmap = {h.id: h for h in hypotheses}
    rows: list[dict[str, Any]] = []
    for (a, b), gamma in coherence.items():
        unresolved = posterior[a] * posterior[b] * gamma
        rows.append(
            {
                "hypothesis_a": a,
                "hypothesis_b": b,
                "label_a": hmap[a].label,
                "label_b": hmap[b].label,
                "posterior_a": posterior[a],
                "posterior_b": posterior[b],
                "coherence": gamma,
                "unresolved_mass": unresolved,
                "different_source_maps": _source_key(hmap[a].source_map)
                != _source_key(hmap[b].source_map),
            }
        )
    rows.sort(key=lambda row: row["unresolved_mass"], reverse=True)
    return rows


def coherence_classes(
    hypotheses: Sequence[Hypothesis],
    posterior: Mapping[str, float],
    coherence: Mapping[tuple[str, str], float],
    *,
    threshold: float,
    min_posterior: float,
) -> list[list[str]]:
    active = {h.id for h in hypotheses if posterior[h.id] >= min_posterior}
    adjacency: dict[str, set[str]] = {hid: set() for hid in active}
    for (a, b), gamma in coherence.items():
        if a in active and b in active and gamma >= threshold:
            adjacency[a].add(b)
            adjacency[b].add(a)
    components: list[list[str]] = []
    seen: set[str] = set()
    for start in sorted(active):
        if start in seen:
            continue
        stack = [start]
        component: list[str] = []
        seen.add(start)
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in sorted(adjacency[node] - seen):
                seen.add(neighbor)
                stack.append(neighbor)
        if len(component) > 1:
            components.append(sorted(component))
    components.sort(key=lambda c: (-sum(posterior[h] for h in c), c))
    return components


def expected_information_gain(
    hypotheses: Sequence[Hypothesis], posterior: Mapping[str, float], probe: Probe
) -> float:
    prior_entropy = entropy(posterior.values())
    expected_after = 0.0
    for outcome in probe.outcomes:
        outcome_probability = sum(
            posterior[h.id] * probe.predictions[h.id][outcome] for h in hypotheses
        )
        if outcome_probability <= 0:
            continue
        conditional = [
            posterior[h.id] * probe.predictions[h.id][outcome] / outcome_probability
            for h in hypotheses
        ]
        expected_after += outcome_probability * entropy(conditional)
    return max(0.0, prior_entropy - expected_after)


def weighted_separation(
    pair_table: Sequence[Mapping[str, Any]], probe: Probe, *, source_only: bool = False
) -> float:
    numerator = 0.0
    denominator = 0.0
    for row in pair_table:
        if source_only and not bool(row["different_source_maps"]):
            continue
        mass = float(row["unresolved_mass"])
        gamma = bhattacharyya(
            probe.predictions[str(row["hypothesis_a"])],
            probe.predictions[str(row["hypothesis_b"])],
        )
        numerator += mass * (1.0 - gamma)
        denominator += mass
    return 0.0 if denominator <= 0 else numerator / denominator


def candidate_rows(
    hypotheses: Sequence[Hypothesis],
    probes: Sequence[Probe],
    posterior: Mapping[str, float],
    pairs: Sequence[Mapping[str, Any]],
    used_groups: set[str],
) -> list[dict[str, Any]]:
    k = len(hypotheses)
    entropy_scale = math.log(k) if k > 1 else 1.0
    rows: list[dict[str, Any]] = []
    for probe in probes:
        if probe.observed is not None:
            continue
        eig = expected_information_gain(hypotheses, posterior, probe)
        eig_normalized = eig / entropy_scale if entropy_scale > 0 else 0.0
        coherence_reduction = weighted_separation(pairs, probe)
        source_separation = weighted_separation(pairs, probe, source_only=True)
        novelty = (
            probe.provenance_novelty
            if probe.provenance_novelty is not None
            else (1.0 if probe.group not in used_groups else 0.5)
        )
        core = (
            0.45 * coherence_reduction
            + 0.35 * eig_normalized
            + 0.20 * source_separation
        )
        score = (
            core
            * probe.reliability
            * probe.calibration_factor
            * novelty
            / math.sqrt(probe.cost)
        )
        rows.append(
            {
                "probe_id": probe.id,
                "label": probe.label,
                "independence_group": probe.group,
                "expected_information_gain_nats": eig,
                "expected_information_gain_normalized": eig_normalized,
                "coherence_reduction": coherence_reduction,
                "source_map_separation": source_separation,
                "source_sensitive_declared": probe.source_sensitive,
                "reliability": probe.reliability,
                "calibration_factor": probe.calibration_factor,
                "provenance_novelty": novelty,
                "cost": probe.cost,
                "priority_score": score,
            }
        )
    rows.sort(
        key=lambda row: (
            row["priority_score"],
            row["coherence_reduction"],
            row["source_map_separation"],
            row["expected_information_gain_nats"],
        ),
        reverse=True,
    )
    return rows


def analyze_case(data: Mapping[str, Any]) -> dict[str, Any]:
    hypotheses, probes, settings = parse_case(data)
    groups = observed_groups(probes)
    posterior, group_rows = update_posterior(hypotheses, groups)
    coherence = aggregate_coherence(hypotheses, groups)
    pairs = pair_rows(hypotheses, posterior, coherence)
    threshold = _probability(
        settings.get("coherence_threshold", 0.90), name="settings.coherence_threshold"
    )
    min_posterior = _probability(
        settings.get("minimum_class_posterior", 0.01), name="settings.minimum_class_posterior"
    )
    classes = coherence_classes(
        hypotheses,
        posterior,
        coherence,
        threshold=threshold,
        min_posterior=min_posterior,
    )
    candidates = candidate_rows(hypotheses, probes, posterior, pairs, set(groups))
    return {
        "title": str(data.get("title") or "Aletheia Hypothesis Interferometer analysis"),
        "method": "classical quantum-inspired; no quantum speedup claimed",
        "settings": {
            "coherence_threshold": threshold,
            "minimum_class_posterior": min_posterior,
            "within_group_rule": "weighted geometric mean; each provenance group counted once",
        },
        "hypotheses": [
            {
                "id": h.id,
                "label": h.label,
                "prior": h.prior,
                "posterior": posterior[h.id],
                "source_map": h.source_map,
                "mechanism": h.mechanism,
                "scope": h.scope,
            }
            for h in hypotheses
        ],
        "observed_groups": group_rows,
        "pairwise_coherence": pairs,
        "coherence_classes": classes,
        "candidate_probes": candidates,
        "selected_probe": candidates[0] if candidates else None,
        "warnings": [
            "All posterior masses are conditional on the declared hypotheses, priors, prediction model, dependence groups, and calibration; they are not probabilities that a claim is true.",
            "A high conditional posterior inside a high-coherence class is favored under the declared model but not identified and not disclosed as truth.",
            "The priority score is a disclosed scheduling heuristic; inspect its components.",
        ],
    }


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def render_markdown(report: Mapping[str, Any], *, top: int = 12) -> str:
    lines: list[str] = []
    lines.append(f"# {report['title']}")
    lines.append("")
    lines.append(f"**Method:** {report['method']}")
    lines.append("")
    lines.append("## Belief mass")
    lines.append("")
    lines.append("| Hypothesis | Prior | Posterior | Source map |")
    lines.append("|---|---:|---:|---|")
    for h in sorted(report["hypotheses"], key=lambda x: x["posterior"], reverse=True):
        source = json.dumps(h["source_map"], ensure_ascii=False, sort_keys=True)
        lines.append(
            f"| `{h['id']}` — {h['label']} | {_fmt(h['prior'])} | {_fmt(h['posterior'])} | `{source}` |"
        )
    lines.append("")
    lines.append("## Current coherence")
    lines.append("")
    lines.append("| Pair | Coherence | Unresolved mass | Different source maps |")
    lines.append("|---|---:|---:|:---:|")
    for row in report["pairwise_coherence"][:top]:
        lines.append(
            f"| `{row['hypothesis_a']}` ↔ `{row['hypothesis_b']}` | "
            f"{_fmt(row['coherence'])} | {_fmt(row['unresolved_mass'])} | "
            f"{'yes' if row['different_source_maps'] else 'no'} |"
        )
    if not report["pairwise_coherence"]:
        lines.append("| — | — | — | — |")
    lines.append("")
    threshold = report["settings"]["coherence_threshold"]
    lines.append(f"### Coherence classes at threshold {threshold:.3f}")
    lines.append("")
    classes = report["coherence_classes"]
    if classes:
        for index, component in enumerate(classes, start=1):
            lines.append(f"{index}. " + ", ".join(f"`{x}`" for x in component))
    else:
        lines.append("No multi-hypothesis class crosses the declared threshold.")
    lines.append("")
    lines.append("## Candidate basis rotations / probes")
    lines.append("")
    lines.append(
        "| Rank | Probe | Score | Coherence reduction | Source separation | EIG (nats) | New-group factor | Calibration | Reliability | Cost |"
    )
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for rank, row in enumerate(report["candidate_probes"][:top], start=1):
        lines.append(
            f"| {rank} | `{row['probe_id']}` — {row['label']} | "
            f"{_fmt(row['priority_score'])} | {_fmt(row['coherence_reduction'])} | "
            f"{_fmt(row['source_map_separation'])} | "
            f"{_fmt(row['expected_information_gain_nats'])} | "
            f"{_fmt(row['provenance_novelty'])} | {_fmt(row['calibration_factor'])} | "
            f"{_fmt(row['reliability'])} | {_fmt(row['cost'])} |"
        )
    if not report["candidate_probes"]:
        lines.append("| — | No unobserved candidate probes supplied | — | — | — | — | — | — | — | — |")
    lines.append("")
    selected = report.get("selected_probe")
    if selected:
        lines.append(
            f"**Selected next probe:** `{selected['probe_id']}`. Selection is provisional on the "
            "declared probabilities, dependence groups, calibration, and costs."
        )
    else:
        lines.append("**Selected next probe:** none supplied.")
    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    for warning in report["warnings"]:
        lines.append(f"- {warning}")
    lines.append("")
    return "\n".join(lines)


def self_test() -> None:
    case = {
        "title": "AHI self-test: target structure versus wrong-source proxy",
        "hypotheses": [
            {
                "id": "structure",
                "label": "Target structure is causal",
                "prior": 0.4,
                "source_map": "target_structure",
            },
            {
                "id": "proxy",
                "label": "Proxy/leakage generates the same ordinary fit",
                "prior": 0.4,
                "source_map": "shared_preprocessing",
            },
            {
                "id": "noise",
                "label": "Finite-window coincidence",
                "prior": 0.2,
                "source_map": "sampling_noise",
            },
        ],
        "probes": [
            {
                "id": "benchmark_fit",
                "outcomes": ["pass", "fail"],
                "predictions": {
                    "structure": {"pass": 0.95, "fail": 0.05},
                    "proxy": {"pass": 0.95, "fail": 0.05},
                    "noise": {"pass": 0.45, "fail": 0.55},
                },
                "observed": "pass",
                "independence_group": "dataset_A_pipeline",
                "reliability": 0.95,
            },
            {
                "id": "same_pipeline_rerun",
                "outcomes": ["pass", "fail"],
                "predictions": {
                    "structure": {"pass": 0.94, "fail": 0.06},
                    "proxy": {"pass": 0.94, "fail": 0.06},
                    "noise": {"pass": 0.50, "fail": 0.50},
                },
                "observed": "pass",
                "independence_group": "dataset_A_pipeline",
                "reliability": 0.95,
            },
            {
                "id": "more_same_pipeline",
                "label": "More samples through the same source path",
                "outcomes": ["pass", "fail"],
                "predictions": {
                    "structure": {"pass": 0.95, "fail": 0.05},
                    "proxy": {"pass": 0.95, "fail": 0.05},
                    "noise": {"pass": 0.35, "fail": 0.65},
                },
                "independence_group": "dataset_A_pipeline",
                "reliability": 0.95,
                "calibration": {"positive_control": True, "negative_control": True},
                "cost": 1.0,
            },
            {
                "id": "independent_holdout",
                "label": "Fresh holdout with independent preprocessing",
                "outcomes": ["pass", "fail"],
                "predictions": {
                    "structure": {"pass": 0.88, "fail": 0.12},
                    "proxy": {"pass": 0.62, "fail": 0.38},
                    "noise": {"pass": 0.40, "fail": 0.60},
                },
                "independence_group": "holdout_B",
                "reliability": 0.90,
                "calibration": {"positive_control": True, "negative_control": True},
                "cost": 1.5,
            },
            {
                "id": "source_swap",
                "label": "Mask/swap the claimed source while holding ordinary content fixed",
                "outcomes": ["stable", "changes"],
                "predictions": {
                    "structure": {"stable": 0.92, "changes": 0.08},
                    "proxy": {"stable": 0.08, "changes": 0.92},
                    "noise": {"stable": 0.50, "changes": 0.50},
                },
                "independence_group": "source_intervention",
                "source_sensitive": True,
                "reliability": 0.95,
                "calibration": {"positive_control": True, "negative_control": True},
                "cost": 1.0,
            },
        ],
    }
    report = analyze_case(case)
    posterior_total = sum(h["posterior"] for h in report["hypotheses"])
    assert abs(posterior_total - 1.0) < 1e-12
    pair = next(
        row
        for row in report["pairwise_coherence"]
        if {row["hypothesis_a"], row["hypothesis_b"]} == {"structure", "proxy"}
    )
    assert pair["coherence"] > 0.999999, pair
    assert report["selected_probe"]["probe_id"] == "source_swap", report["candidate_probes"]
    scores = {row["probe_id"]: row["priority_score"] for row in report["candidate_probes"]}
    assert scores["source_swap"] > scores["more_same_pipeline"]
    malformed = json.loads(json.dumps(case))
    malformed["probes"][0]["predictions"]["structure"] = {"pass": 0.9, "fail": 0.2}
    try:
        analyze_case(malformed)
    except InputError:
        pass
    else:
        raise AssertionError("malformed probability distribution was accepted")
    print("HYPOTHESIS_INTERFEROMETER_SELF_TEST_PASS")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classical Aletheia Hypothesis Interferometer for finite hypothesis/probe tables."
    )
    parser.add_argument("input", nargs="?", help="JSON case file")
    parser.add_argument("--json-out", help="write the full analysis JSON")
    parser.add_argument("--markdown-out", help="write a Markdown report")
    parser.add_argument("--top", type=int, default=12, help="maximum rows in Markdown tables")
    parser.add_argument("--self-test", action="store_true", help="run deterministic internal tests")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if not args.input:
        raise InputError("an input JSON file is required unless --self-test is used")
    path = Path(args.input)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError(f"input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, Mapping):
        raise InputError("top-level JSON value must be an object")
    report = analyze_case(data)
    markdown = render_markdown(report, top=max(1, args.top))
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    if args.markdown_out:
        Path(args.markdown_out).write_text(markdown, encoding="utf-8")
    if not args.json_out and not args.markdown_out:
        print(markdown)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InputError as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)

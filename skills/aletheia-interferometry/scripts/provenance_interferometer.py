#!/usr/bin/env python3
"""Aletheia Provenance Interferometer.

Classical, deterministic diagnostics for:
- provenance-normalized evidence amplitudes;
- configuration interaction / Möbius tomography;
- leave-one-family-out stability;
- information-gain and source-map probe selection.

The outputs are diagnostics, not posterior probabilities and not proofs.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

VERSION = "3.2.0"
EPS = 1e-12


class InputError(ValueError):
    """Raised when an analysis case violates the input contract."""


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{label} must be finite")
    return result


def _unit_interval(value: Any, label: str) -> float:
    result = _finite_number(value, label)
    if result < 0.0 or result > 1.0:
        raise InputError(f"{label} must be in [0, 1]")
    return result


def _positive(value: Any, label: str) -> float:
    result = _finite_number(value, label)
    if result <= 0.0:
        raise InputError(f"{label} must be > 0")
    return result


def _unique_ids(items: Sequence[Mapping[str, Any]], label: str) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            raise InputError(f"{label}[{index}].id must be a non-empty string")
        if item_id in seen:
            raise InputError(f"duplicate {label} id: {item_id}")
        seen.add(item_id)
        ids.append(item_id)
    return ids


def _phase_radians(score: Mapping[str, Any], label: str) -> float:
    present = [key for key in ("direction", "phase_deg", "phase_rad") if key in score]
    if len(present) != 1:
        raise InputError(
            f"{label} must contain exactly one of direction, phase_deg, or phase_rad"
        )
    key = present[0]
    if key == "direction":
        direction = _finite_number(score[key], f"{label}.direction")
        if direction < -1.0 or direction > 1.0:
            raise InputError(f"{label}.direction must be in [-1, 1]")
        return math.acos(direction)
    if key == "phase_deg":
        return math.radians(_finite_number(score[key], f"{label}.phase_deg"))
    return _finite_number(score[key], f"{label}.phase_rad")


def _normalized_weights(raw: Mapping[str, float], label: str) -> dict[str, float]:
    total = sum(raw.values())
    if total <= EPS:
        raise InputError(f"{label} weights must have positive total")
    return {key: value / total for key, value in raw.items()}


def _rank(support: Mapping[str, float]) -> list[str]:
    return sorted(support, key=lambda item: (-support[item], item))


def _weighted_mean(values: Mapping[str, float], weights: Mapping[str, float]) -> float | None:
    used = [(key, value) for key, value in values.items() if key in weights]
    denominator = sum(weights[key] for key, _ in used)
    if denominator <= EPS:
        return None
    return sum(weights[key] * value for key, value in used) / denominator


def _effective_count(weights: Iterable[float]) -> float:
    values = [value for value in weights if value > EPS]
    if not values:
        return 0.0
    numerator = sum(values) ** 2
    denominator = sum(value * value for value in values)
    return numerator / denominator if denominator > EPS else 0.0


def analyze_route_field(
    case: Mapping[str, Any], hypothesis_ids: Sequence[str]
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    routes_raw = case.get("routes", [])
    if routes_raw is None:
        routes_raw = []
    if not isinstance(routes_raw, list):
        raise InputError("routes must be a list")
    routes: list[Mapping[str, Any]] = routes_raw
    if routes:
        _unique_ids(routes, "routes")

    families_raw = case.get("families", [])
    if families_raw is None:
        families_raw = []
    if not isinstance(families_raw, list):
        raise InputError("families must be a list")
    families: list[Mapping[str, Any]] = families_raw
    family_ids = _unique_ids(families, "families") if families else []
    family_meta: dict[str, Mapping[str, Any]] = {item["id"]: item for item in families}

    route_groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for index, route in enumerate(routes):
        family = route.get("family")
        if not isinstance(family, str) or not family.strip():
            raise InputError(f"routes[{index}].family must be a non-empty string")
        route_groups[family].append(route)
        if family not in family_meta:
            family_meta[family] = {"id": family, "weight": 1.0}
            family_ids.append(family)

    missing_routes = [family for family in family_ids if family not in route_groups]
    if missing_routes:
        warnings.append(
            "families without routes were omitted from route-field aggregation: "
            + ", ".join(sorted(missing_routes))
        )

    active_family_ids = [family for family in family_ids if family in route_groups]
    family_weight_raw: dict[str, float] = {}
    for family in active_family_ids:
        family_weight_raw[family] = _positive(
            family_meta[family].get("weight", 1.0), f"families[{family}].weight"
        )
    family_weights = (
        _normalized_weights(family_weight_raw, "family") if family_weight_raw else {}
    )

    family_results: dict[str, Any] = {}
    family_support_by_hypothesis: dict[str, dict[str, float]] = {
        hypothesis: {} for hypothesis in hypothesis_ids
    }
    family_mass_by_hypothesis: dict[str, dict[str, float]] = {
        hypothesis: {} for hypothesis in hypothesis_ids
    }

    for family in active_family_ids:
        family_routes = route_groups[family]
        route_weight_raw: dict[str, float] = {}
        for route in family_routes:
            route_weight_raw[route["id"]] = _positive(
                route.get("weight", 1.0), f"routes[{route['id']}].weight"
            )
        route_weights = _normalized_weights(route_weight_raw, f"family {family} route")

        signatures: dict[str, list[str]] = defaultdict(list)
        hypothesis_results: dict[str, Any] = {}
        for hypothesis in hypothesis_ids:
            amplitudes: list[complex] = []
            masses: list[float] = []
            signed_support = 0.0
            imaginary_support = 0.0
            route_rows: list[dict[str, Any]] = []

            for route in family_routes:
                scores = route.get("scores", {})
                if not isinstance(scores, Mapping):
                    raise InputError(f"routes[{route['id']}].scores must be an object")
                if hypothesis not in scores:
                    continue
                score = scores[hypothesis]
                if not isinstance(score, Mapping):
                    raise InputError(
                        f"routes[{route['id']}].scores[{hypothesis}] must be an object"
                    )
                reliability = _unit_interval(
                    route.get("reliability", 1.0),
                    f"routes[{route['id']}].reliability",
                )
                strength = _unit_interval(
                    score.get("strength", 1.0),
                    f"routes[{route['id']}].scores[{hypothesis}].strength",
                )
                theta = _phase_radians(
                    score, f"routes[{route['id']}].scores[{hypothesis}]"
                )
                normalized_route_weight = route_weights[route["id"]]
                mass = normalized_route_weight * reliability * strength
                amplitude = math.sqrt(mass) * cmath.exp(1j * theta) if mass > 0 else 0j
                amplitudes.append(amplitude)
                masses.append(mass)
                signed_support += mass * math.cos(theta)
                imaginary_support += mass * math.sin(theta)
                route_rows.append(
                    {
                        "route": route["id"],
                        "normalized_weight": normalized_route_weight,
                        "reliability": reliability,
                        "strength": strength,
                        "phase_deg": math.degrees(theta) % 360.0,
                        "mass": mass,
                    }
                )

            if not masses:
                continue
            evidence_mass = sum(masses)
            amplitude_sum = sum(amplitudes, 0j)
            coherent_intensity = abs(amplitude_sum) ** 2
            incoherent_intensity = evidence_mass
            max_intensity = sum(abs(amplitude) for amplitude in amplitudes) ** 2
            normalized_coherence = (
                coherent_intensity / max_intensity if max_intensity > EPS else 0.0
            )
            normalized_incoherent = (
                incoherent_intensity / max_intensity if max_intensity > EPS else 0.0
            )
            phase_mean = math.degrees(cmath.phase(amplitude_sum)) % 360.0 if abs(amplitude_sum) > EPS else None
            hypothesis_results[hypothesis] = {
                "signed_support": signed_support,
                "imaginary_support": imaginary_support,
                "evidence_mass": evidence_mass,
                "coherent_intensity": coherent_intensity,
                "incoherent_intensity": incoherent_intensity,
                "interference_residual": coherent_intensity - incoherent_intensity,
                "normalized_coherence": normalized_coherence,
                "normalized_incoherent_baseline": normalized_incoherent,
                "normalized_interference": normalized_coherence - normalized_incoherent,
                "resultant_phase_deg": phase_mean,
                "routes": route_rows,
            }
            family_support_by_hypothesis[hypothesis][family] = signed_support
            family_mass_by_hypothesis[hypothesis][family] = evidence_mass

        for route in family_routes:
            signature_payload: dict[str, Any] = {
                "reliability": route.get("reliability", 1.0),
                "scores": route.get("scores", {}),
            }
            signature = json.dumps(signature_payload, sort_keys=True, separators=(",", ":"))
            signatures[signature].append(route["id"])
        duplicate_sets = [ids for ids in signatures.values() if len(ids) > 1]
        for duplicate_ids in duplicate_sets:
            warnings.append(
                f"family {family} contains identical route signatures ({', '.join(duplicate_ids)}); "
                "normalization prevents vote inflation, but this is not independent confirmation"
            )

        family_results[family] = {
            "weight": family_weights.get(family, 0.0),
            "route_count": len(family_routes),
            "hypotheses": hypothesis_results,
        }

    if routes and len(active_family_ids) == 1:
        warnings.append(
            "all route evidence belongs to one provenance family; route count must not be read as independent-bearing count"
        )

    aggregate: dict[str, Any] = {}
    full_support: dict[str, float] = {}
    for hypothesis in hypothesis_ids:
        support = _weighted_mean(family_support_by_hypothesis[hypothesis], family_weights)
        mass = _weighted_mean(family_mass_by_hypothesis[hypothesis], family_weights)
        if support is None:
            aggregate[hypothesis] = {
                "signed_support": None,
                "evidence_mass": None,
                "effective_family_count": 0.0,
                "leave_one_family_out": {},
                "leave_one_family_out_span": None,
            }
            continue
        used_families = list(family_support_by_hypothesis[hypothesis])
        effective = _effective_count(family_weights[family] for family in used_families)
        loo: dict[str, float | None] = {}
        for omitted in used_families:
            remaining_values = {
                family: value
                for family, value in family_support_by_hypothesis[hypothesis].items()
                if family != omitted
            }
            remaining_weights = {
                family: weight for family, weight in family_weights.items() if family != omitted
            }
            loo[omitted] = _weighted_mean(remaining_values, remaining_weights)
        stability_values = [support] + [value for value in loo.values() if value is not None]
        loo_span = max(stability_values) - min(stability_values) if len(stability_values) > 1 else None
        aggregate[hypothesis] = {
            "signed_support": support,
            "evidence_mass": mass,
            "effective_family_count": effective,
            "leave_one_family_out": loo,
            "leave_one_family_out_span": loo_span,
        }
        full_support[hypothesis] = support

    full_ranking = _rank(full_support) if full_support else []
    omitted_rankings: dict[str, list[str]] = {}
    rank_flips: list[dict[str, Any]] = []
    for omitted in active_family_ids:
        support_without: dict[str, float] = {}
        for hypothesis in hypothesis_ids:
            value = aggregate[hypothesis]["leave_one_family_out"].get(omitted)
            if value is not None:
                support_without[hypothesis] = value
        if support_without:
            ranking = _rank(support_without)
            omitted_rankings[omitted] = ranking
            if full_ranking and ranking[0] != full_ranking[0]:
                rank_flips.append(
                    {
                        "omitted_family": omitted,
                        "full_top": full_ranking[0],
                        "leave_one_out_top": ranking[0],
                    }
                )

    return (
        {
            "family_weights": family_weights,
            "families": family_results,
            "aggregate": aggregate,
            "full_ranking": full_ranking,
            "leave_one_family_out_rankings": omitted_rankings,
            "rank_flips": rank_flips,
        },
        warnings,
    )


def _powerset(items: Sequence[str]) -> Iterable[tuple[str, ...]]:
    for size in range(len(items) + 1):
        yield from itertools.combinations(items, size)


def analyze_configurations(
    case: Mapping[str, Any], hypothesis_ids: Sequence[str]
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    raw = case.get("configuration_scores", [])
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        raise InputError("configuration_scores must be a list")
    if not raw:
        return {
            "score_semantics": case.get("configuration_score_semantics"),
            "configurations": [],
            "mobius_interactions": [],
        }, warnings

    configs: dict[frozenset[str], dict[str, float]] = {}
    normalized_rows: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, Mapping):
            raise InputError(f"configuration_scores[{index}] must be an object")
        active = item.get("active_families", [])
        if not isinstance(active, list) or any(not isinstance(v, str) or not v for v in active):
            raise InputError(
                f"configuration_scores[{index}].active_families must be a list of non-empty strings"
            )
        if len(active) != len(set(active)):
            raise InputError(f"configuration_scores[{index}] has duplicate active_families")
        key = frozenset(active)
        if key in configs:
            raise InputError(
                "duplicate configuration for active_families=" + ",".join(sorted(key))
            )
        scores_raw = item.get("scores")
        if not isinstance(scores_raw, Mapping):
            raise InputError(f"configuration_scores[{index}].scores must be an object")
        scores: dict[str, float] = {}
        for hypothesis in hypothesis_ids:
            if hypothesis not in scores_raw:
                raise InputError(
                    f"configuration_scores[{index}].scores missing hypothesis {hypothesis}"
                )
            scores[hypothesis] = _finite_number(
                scores_raw[hypothesis],
                f"configuration_scores[{index}].scores[{hypothesis}]",
            )
        configs[key] = scores
        normalized_rows.append(
            {"active_families": sorted(key), "scores": scores}
        )

    if frozenset() not in configs:
        warnings.append(
            "configuration tomography has no empty baseline; Möbius interaction coefficients cannot be computed"
        )
        return {
            "score_semantics": case.get("configuration_score_semantics"),
            "configurations": sorted(normalized_rows, key=lambda row: (len(row["active_families"]), row["active_families"])),
            "mobius_interactions": [],
        }, warnings

    interactions: list[dict[str, Any]] = []
    for active_set in sorted(configs, key=lambda key: (len(key), sorted(key))):
        if len(active_set) < 2:
            continue
        active_tuple = tuple(sorted(active_set))
        subsets = [frozenset(subset) for subset in _powerset(active_tuple)]
        if any(subset not in configs for subset in subsets):
            warnings.append(
                "configuration "
                + "+".join(active_tuple)
                + " lacks one or more subset runs; its interaction coefficient is unresolved"
            )
            continue
        coefficients: dict[str, float] = {}
        for hypothesis in hypothesis_ids:
            coefficient = 0.0
            for subset in subsets:
                sign = -1.0 if (len(active_set) - len(subset)) % 2 else 1.0
                coefficient += sign * configs[subset][hypothesis]
            coefficients[hypothesis] = coefficient
        interactions.append(
            {
                "active_families": list(active_tuple),
                "order": len(active_tuple),
                "coefficients": coefficients,
            }
        )

    return {
        "score_semantics": case.get("configuration_score_semantics"),
        "configurations": sorted(normalized_rows, key=lambda row: (len(row["active_families"]), row["active_families"])),
        "mobius_interactions": interactions,
    }, warnings


def _entropy_bits(distribution: Mapping[str, float]) -> float:
    return -sum(value * math.log2(value) for value in distribution.values() if value > EPS)


def _bhattacharyya_gap(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    outcomes = set(left) | set(right)
    coefficient = sum(math.sqrt(left.get(outcome, 0.0) * right.get(outcome, 0.0)) for outcome in outcomes)
    coefficient = min(1.0, max(0.0, coefficient))
    return 1.0 - coefficient


def _weighted_pair_gap(
    pairs: Sequence[tuple[str, str]],
    distributions: Mapping[str, Mapping[str, float]],
    priors: Mapping[str, float],
) -> float | None:
    if not pairs:
        return None
    weighted: list[tuple[float, float]] = []
    for left, right in pairs:
        pair_weight = priors[left] * priors[right]
        gap = _bhattacharyya_gap(distributions[left], distributions[right])
        weighted.append((pair_weight, gap))
    denominator = sum(weight for weight, _ in weighted)
    if denominator <= EPS:
        return sum(gap for _, gap in weighted) / len(weighted)
    return sum(weight * gap for weight, gap in weighted) / denominator


def analyze_probes(
    case: Mapping[str, Any], hypotheses: Sequence[Mapping[str, Any]]
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    raw = case.get("probes", [])
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        raise InputError("probes must be a list")
    if raw:
        _unique_ids(raw, "probes")

    hypothesis_ids = [item["id"] for item in hypotheses]
    prior_raw = {
        item["id"]: _positive(item.get("prior", 1.0), f"hypotheses[{item['id']}].prior")
        for item in hypotheses
    }
    priors = _normalized_weights(prior_raw, "hypothesis prior")
    all_pairs = list(itertools.combinations(hypothesis_ids, 2))

    sigma_pairs: list[tuple[str, str]] = []
    hypothesis_map = {item["id"]: item for item in hypotheses}
    for left, right in all_pairs:
        left_item = hypothesis_map[left]
        right_item = hypothesis_map[right]
        prediction_class_left = left_item.get("prediction_class")
        prediction_class_right = right_item.get("prediction_class")
        source_left = left_item.get("source_map")
        source_right = right_item.get("source_map")
        if (
            prediction_class_left is not None
            and prediction_class_left == prediction_class_right
            and source_left is not None
            and source_right is not None
            and source_left != source_right
        ):
            sigma_pairs.append((left, right))

    objective = case.get("probe_objective", "global")
    if objective not in {"global", "source_map"}:
        raise InputError("probe_objective must be 'global' or 'source_map'")
    if objective == "source_map" and not sigma_pairs:
        raise InputError(
            "probe_objective is source_map, but no hypotheses share prediction_class while differing in source_map"
        )

    probe_results: list[dict[str, Any]] = []
    for index, probe in enumerate(raw):
        outcomes_raw = probe.get("outcomes")
        if not isinstance(outcomes_raw, Mapping):
            raise InputError(f"probes[{index}].outcomes must be an object")
        distributions: dict[str, dict[str, float]] = {}
        for hypothesis in hypothesis_ids:
            dist_raw = outcomes_raw.get(hypothesis)
            if not isinstance(dist_raw, Mapping) or not dist_raw:
                raise InputError(
                    f"probes[{probe['id']}].outcomes[{hypothesis}] must be a non-empty object"
                )
            distribution: dict[str, float] = {}
            for outcome, probability in dist_raw.items():
                if not isinstance(outcome, str) or not outcome:
                    raise InputError(
                        f"probes[{probe['id']}].outcomes[{hypothesis}] has an invalid outcome name"
                    )
                distribution[outcome] = _unit_interval(
                    probability,
                    f"probes[{probe['id']}].outcomes[{hypothesis}][{outcome}]",
                )
            total = sum(distribution.values())
            if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
                raise InputError(
                    f"probes[{probe['id']}].outcomes[{hypothesis}] probabilities sum to {total}, not 1"
                )
            distributions[hypothesis] = distribution

        outcome_names = sorted(
            set().union(*(set(distribution) for distribution in distributions.values()))
        )
        mixture = {
            outcome: sum(
                priors[hypothesis] * distributions[hypothesis].get(outcome, 0.0)
                for hypothesis in hypothesis_ids
            )
            for outcome in outcome_names
        }
        information_gain = _entropy_bits(mixture) - sum(
            priors[hypothesis] * _entropy_bits(distributions[hypothesis])
            for hypothesis in hypothesis_ids
        )
        information_gain = max(0.0, information_gain)
        global_gap = _weighted_pair_gap(all_pairs, distributions, priors)
        sigma_gap = _weighted_pair_gap(sigma_pairs, distributions, priors)
        contact = _unit_interval(probe.get("contact", 1.0), f"probes[{probe['id']}].contact")
        independence = _unit_interval(
            probe.get("independence", 1.0), f"probes[{probe['id']}].independence"
        )
        cost = _positive(probe.get("cost", 1.0), f"probes[{probe['id']}].cost")
        raw_objective = information_gain if objective == "global" else (sigma_gap or 0.0)
        adjusted_score = raw_objective * contact * independence / cost
        probe_results.append(
            {
                "id": probe["id"],
                "label": probe.get("label"),
                "information_gain_bits": information_gain,
                "global_fidelity_gap": global_gap,
                "source_map_fidelity_gap": sigma_gap,
                "contact": contact,
                "independence": independence,
                "cost": cost,
                "objective": objective,
                "adjusted_score": adjusted_score,
            }
        )

    probe_results.sort(key=lambda item: (-item["adjusted_score"], item["id"]))
    if raw and all(item["independence"] < 0.5 for item in probe_results):
        warnings.append(
            "all candidate probes have low independence; probe ranking may optimize within the same cave rather than open a new bearing"
        )
    return {
        "objective": objective,
        "priors": priors,
        "source_map_pairs": [list(pair) for pair in sigma_pairs],
        "ranking": probe_results,
    }, warnings


def analyze_case(case: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(case, Mapping):
        raise InputError("top-level input must be an object")
    hypotheses_raw = case.get("hypotheses")
    if not isinstance(hypotheses_raw, list) or len(hypotheses_raw) < 2:
        raise InputError("hypotheses must be a list containing at least two candidates")
    hypotheses: list[Mapping[str, Any]] = hypotheses_raw
    hypothesis_ids = _unique_ids(hypotheses, "hypotheses")

    route_field, route_warnings = analyze_route_field(case, hypothesis_ids)
    configurations, configuration_warnings = analyze_configurations(case, hypothesis_ids)
    probes, probe_warnings = analyze_probes(case, hypotheses)
    warnings = route_warnings + configuration_warnings + probe_warnings

    if not case.get("routes"):
        warnings.append("no route amplitudes supplied; amplitude diagnostics are absent")
    if not case.get("configuration_scores"):
        warnings.append(
            "no measured configuration scores supplied; interference remains a planning metaphor rather than an observed interaction term"
        )
    if not case.get("probes"):
        warnings.append("no candidate probes supplied; next-measurement ranking is absent")

    canonical = json.dumps(case, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {
        "method": "Aletheia Provenance Interferometer",
        "version": VERSION,
        "case": case.get("case") or case.get("name"),
        "input_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "hypotheses": [
            {
                "id": item["id"],
                "label": item.get("label"),
                "prediction_class": item.get("prediction_class"),
                "source_map": item.get("source_map"),
            }
            for item in hypotheses
        ],
        "route_field": route_field,
        "configuration_tomography": configurations,
        "probe_selection": probes,
        "warnings": warnings,
        "boundary": (
            "Diagnostics are not posterior probabilities, physical quantum amplitudes, or proofs. "
            "Claim status must still be set by the underlying derivation, experiment, source verification, and controls."
        ),
    }


def _fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def render_markdown(result: Mapping[str, Any]) -> str:
    lines: list[str] = []
    title = result.get("case") or "Untitled case"
    lines.extend(
        [
            f"# Provenance Interferometer — {title}",
            "",
            f"- Method version: `{result['version']}`",
            f"- Input SHA-256: `{result['input_sha256']}`",
            "",
        ]
    )

    warnings = result.get("warnings", [])
    if warnings:
        lines.append("## Warnings")
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")

    aggregate = result["route_field"]["aggregate"]
    lines.extend(
        [
            "## Provenance-normalized route field",
            "",
            "The support column is signed diagnostic support in `[-1,1]`, not probability.",
            "",
            "| Hypothesis | Signed support | Evidence mass | Effective families | LOO span |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for hypothesis in result["hypotheses"]:
        item = aggregate[hypothesis["id"]]
        lines.append(
            "| {id} | {support} | {mass} | {effective} | {span} |".format(
                id=hypothesis["id"],
                support=_fmt(item["signed_support"]),
                mass=_fmt(item["evidence_mass"]),
                effective=_fmt(item["effective_family_count"]),
                span=_fmt(item["leave_one_family_out_span"]),
            )
        )
    ranking = result["route_field"].get("full_ranking", [])
    if ranking:
        lines.extend(["", "Full-field ranking: " + " → ".join(f"`{item}`" for item in ranking)])
    flips = result["route_field"].get("rank_flips", [])
    if flips:
        lines.extend(["", "**Leave-one-family-out rank flips:**"])
        lines.extend(
            f"- Remove `{item['omitted_family']}`: `{item['full_top']}` → `{item['leave_one_out_top']}`"
            for item in flips
        )
    lines.append("")

    interactions = result["configuration_tomography"].get("mobius_interactions", [])
    lines.extend(["## Measured configuration interactions", ""])
    if interactions:
        semantics = result["configuration_tomography"].get("score_semantics")
        if semantics:
            lines.append(f"Score semantics: {semantics}")
            lines.append("")
        header = "| Configuration | Order | " + " | ".join(
            hypothesis["id"] for hypothesis in result["hypotheses"]
        ) + " |"
        separator = "|---|---:|" + "---:|" * len(result["hypotheses"])
        lines.extend([header, separator])
        for interaction in interactions:
            row = [
                "+".join(interaction["active_families"]),
                str(interaction["order"]),
            ] + [
                _fmt(interaction["coefficients"][hypothesis["id"]])
                for hypothesis in result["hypotheses"]
            ]
            lines.append("| " + " | ".join(row) + " |")
        lines.extend(
            [
                "",
                "A nonzero coefficient shows non-additive configuration dependence. Its sign is not a truth label.",
            ]
        )
    else:
        lines.append("No resolved interaction coefficient.")
    lines.append("")

    probes = result["probe_selection"].get("ranking", [])
    lines.extend(["## Candidate probe ranking", ""])
    if probes:
        lines.extend(
            [
                f"Objective: `{result['probe_selection']['objective']}`",
                "",
                "| Probe | Adjusted score | Information gain (bits) | Global gap | σ-gap | Contact | Independence | Cost |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for probe in probes:
            lines.append(
                "| {id} | {score} | {ig} | {global_gap} | {sigma_gap} | {contact} | {independence} | {cost} |".format(
                    id=probe["id"],
                    score=_fmt(probe["adjusted_score"]),
                    ig=_fmt(probe["information_gain_bits"]),
                    global_gap=_fmt(probe["global_fidelity_gap"]),
                    sigma_gap=_fmt(probe["source_map_fidelity_gap"]),
                    contact=_fmt(probe["contact"]),
                    independence=_fmt(probe["independence"]),
                    cost=_fmt(probe["cost"]),
                )
            )
    else:
        lines.append("No candidate probes supplied.")
    lines.extend(["", "## Boundary", "", result["boundary"], ""])
    return "\n".join(lines)


def _write(path: str | None, content: str) -> None:
    if not path:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON case file")
    parser.add_argument("--json-out", help="write full JSON diagnostics")
    parser.add_argument("--markdown-out", help="write Markdown report")
    parser.add_argument(
        "--stdout",
        choices=("markdown", "json", "none"),
        default="markdown",
        help="stdout format (default: markdown)",
    )
    parser.add_argument("--self-test", action="store_true", help="run deterministic bundled checks")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser


def _self_test() -> None:
    example = Path(__file__).resolve().parents[1] / "assets" / "provenance-field.json"
    case = json.loads(example.read_text(encoding="utf-8"))
    result = analyze_case(case)
    ranking = result["probe_selection"]["ranking"]
    if not ranking or ranking[0]["id"] != "source_lineage_probe":
        raise AssertionError("source-map probe did not rank first")
    warnings = "\n".join(result["warnings"])
    if "identical route signatures" not in warnings:
        raise AssertionError("duplicate-route warning was not emitted")
    interactions = result["configuration_tomography"]["mobius_interactions"]
    target = next(
        item for item in interactions
        if set(item["active_families"]) == {"formal_derivation", "independent_experiment"}
    )
    if abs(target["coefficients"]["H_real_structure"] - 0.3) > 1e-12:
        raise AssertionError("Möbius interaction regression")
    malformed = json.loads(json.dumps(case))
    score = malformed["routes"][0]["scores"]["H_real_structure"]
    score["phase_rad"] = 0.0
    try:
        analyze_case(malformed)
    except InputError:
        pass
    else:
        raise AssertionError("ambiguous phase specification was accepted")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        try:
            _self_test()
        except (OSError, json.JSONDecodeError, InputError, AssertionError) as exc:
            print(f"SELF-TEST FAILED: {exc}", file=sys.stderr)
            return 1
        print("SELF-TEST PASS")
        return 0
    if not args.input:
        parser.error("input is required unless --self-test is used")
    try:
        input_path = Path(args.input)
        case = json.loads(input_path.read_text(encoding="utf-8"))
        result = analyze_case(case)
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 2

    json_text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    markdown_text = render_markdown(result)
    _write(args.json_out, json_text)
    _write(args.markdown_out, markdown_text)
    if args.stdout == "json":
        sys.stdout.write(json_text)
    elif args.stdout == "markdown":
        sys.stdout.write(markdown_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""A deterministic, standard-library epistemic interferometer.

This tool is a diagnostic instrument for Aletheia Interferometry.  It does not
estimate the probability that a hypothesis is true.  It source-adjusts
contextual evidence, computes coherent and incoherent views, performs
leave-one-source-family-out ablations, compares train/holdout phase lock, and
ranks candidate probes by expected pairwise contrast.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = "1.0"
TAU = 2.0 * math.pi
EPS = 1e-12


class InputError(ValueError):
    """Raised when an analysis document violates the input contract."""


@dataclass(frozen=True)
class Bearing:
    evidence_id: str
    hypothesis_id: str
    source_family: str
    dependence_cluster: str
    partition: str
    raw_weight: float
    adjusted_weight: float
    value: complex


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _bounded_number(value: Any, name: str, low: float, high: float) -> float:
    if not _is_number(value):
        raise InputError(f"{name} must be a finite number")
    number = float(value)
    if number < low or number > high:
        raise InputError(f"{name} must be in [{low}, {high}], got {number}")
    return number


def _positive_number(value: Any, name: str, *, allow_zero: bool = False) -> float:
    if not _is_number(value):
        raise InputError(f"{name} must be a finite number")
    number = float(value)
    if allow_zero:
        if number < 0:
            raise InputError(f"{name} must be >= 0, got {number}")
    elif number <= 0:
        raise InputError(f"{name} must be > 0, got {number}")
    return number


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise InputError(f"{name} must be an object")
    return value


def _require_sequence(value: Any, name: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise InputError(f"{name} must be an array")
    return value


def _require_nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{name} must be a non-empty string")
    return value.strip()


def _wrap_angle(angle: float) -> float:
    wrapped = (angle + math.pi) % TAU - math.pi
    # Prefer +pi to -pi for stable support/refute output.
    return math.pi if math.isclose(wrapped, -math.pi, abs_tol=1e-15) else wrapped


def _angular_distance(a: float, b: float) -> float:
    return abs(_wrap_angle(a - b))


def _complex_json(value: complex) -> dict[str, float]:
    return {
        "real": float(value.real),
        "imag": float(value.imag),
        "magnitude": float(abs(value)),
        "phase_radians": float(_wrap_angle(cmath.phase(value))) if abs(value) > EPS else 0.0,
    }


def _response_to_complex(
    response: Any,
    *,
    path: str,
    evidence: Mapping[str, Any],
    strict_phase: bool,
    warnings: list[str],
) -> complex:
    """Convert a response declaration to a complex bearing.

    Accepted forms:
      * number in [-1, 1]: signed support/refute score;
      * {"score": number in [-1, 1]};
      * {"magnitude": nonnegative, "phase": radians}.
    """

    transport = evidence.get("transport")
    phase_basis = None
    transport_description = None
    if isinstance(transport, Mapping):
        phase_basis = transport.get("phase_basis")
        transport_description = transport.get("description")

    if _is_number(response):
        score = _bounded_number(response, path, -1.0, 1.0)
        if not phase_basis or not transport_description:
            message = (
                f"{path}: signed score requires transport.phase_basis and "
                "transport.description"
            )
            if strict_phase:
                raise InputError(message)
            warnings.append(message)
        phase = 0.0 if score >= 0 else math.pi
        return abs(score) * cmath.exp(1j * phase)

    declaration = _require_mapping(response, path)
    if "score" in declaration:
        unknown = set(declaration) - {"score"}
        if unknown:
            raise InputError(f"{path}: score response has unsupported fields {sorted(unknown)}")
        score = _bounded_number(declaration["score"], f"{path}.score", -1.0, 1.0)
        if not phase_basis or not transport_description:
            message = (
                f"{path}: signed score requires transport.phase_basis and "
                "transport.description"
            )
            if strict_phase:
                raise InputError(message)
            warnings.append(message)
        phase = 0.0 if score >= 0 else math.pi
        return abs(score) * cmath.exp(1j * phase)

    if "magnitude" in declaration or "phase" in declaration:
        if set(declaration) - {"magnitude", "phase"}:
            raise InputError(
                f"{path}: phasor response has unsupported fields "
                f"{sorted(set(declaration) - {'magnitude', 'phase'})}"
            )
        if "magnitude" not in declaration or "phase" not in declaration:
            raise InputError(f"{path}: explicit phasor requires both magnitude and phase")
        magnitude = _positive_number(declaration["magnitude"], f"{path}.magnitude", allow_zero=True)
        if not _is_number(declaration["phase"]):
            raise InputError(f"{path}.phase must be finite radians")
        phase = float(declaration["phase"])
        if not phase_basis or not transport_description:
            message = (
                f"{path}: explicit phase requires transport.phase_basis and "
                "transport.description"
            )
            if strict_phase:
                raise InputError(message)
            warnings.append(message)
        return magnitude * cmath.exp(1j * phase)

    raise InputError(f"{path}: response must be a signed score or magnitude/phase object")


def _prediction_to_complex(
    value: Any,
    path: str,
    *,
    phase_basis: Any,
    phase_description: Any,
) -> complex:
    """Parse a candidate-probe prediction in its declared output basis.

    Real numeric predictions are ordinary scalar outcomes. Explicit complex phase is accepted only
    when the probe declares the operational basis and interpretation that make that phase meaningful.
    """

    if _is_number(value):
        return complex(float(value), 0.0)
    declaration = _require_mapping(value, path)
    if "score" in declaration:
        unknown = set(declaration) - {"score"}
        if unknown:
            raise InputError(f"{path}: score prediction has unsupported fields {sorted(unknown)}")
        score = _bounded_number(declaration["score"], f"{path}.score", -1.0, 1.0)
        return complex(score, 0.0)
    if "magnitude" in declaration or "phase" in declaration:
        unknown = set(declaration) - {"magnitude", "phase"}
        if unknown:
            raise InputError(f"{path}: phasor prediction has unsupported fields {sorted(unknown)}")
        if "magnitude" not in declaration or "phase" not in declaration:
            raise InputError(f"{path}: explicit phasor prediction requires magnitude and phase")
        if not phase_basis or not phase_description:
            raise InputError(
                f"{path}: explicit prediction phase requires candidate probe prediction_basis "
                "and prediction_description"
            )
        magnitude = _positive_number(declaration["magnitude"], f"{path}.magnitude", allow_zero=True)
        if not _is_number(declaration["phase"]):
            raise InputError(f"{path}.phase must be finite radians")
        return magnitude * cmath.exp(1j * float(declaration["phase"]))
    raise InputError(f"{path}: prediction must be numeric, score, or magnitude/phase")


def _parse_hypotheses(document: Mapping[str, Any]) -> tuple[list[str], dict[str, str], dict[str, float]]:
    rows = _require_sequence(document.get("hypotheses"), "hypotheses")
    if len(rows) < 2:
        raise InputError("hypotheses must contain at least two candidates")

    ids: list[str] = []
    labels: dict[str, str] = {}
    raw_weights: dict[str, float] = {}
    for index, row in enumerate(rows):
        item = _require_mapping(row, f"hypotheses[{index}]")
        hypothesis_id = _require_nonempty_string(item.get("id"), f"hypotheses[{index}].id")
        if hypothesis_id in labels:
            raise InputError(f"duplicate hypothesis id: {hypothesis_id}")
        ids.append(hypothesis_id)
        labels[hypothesis_id] = str(item.get("label", hypothesis_id))
        raw_weights[hypothesis_id] = _positive_number(
            item.get("working_weight", 1.0),
            f"hypotheses[{index}].working_weight",
            allow_zero=True,
        )
    total = sum(raw_weights.values())
    if total <= EPS:
        raise InputError("at least one hypothesis working_weight must be positive")
    weights = {key: value / total for key, value in raw_weights.items()}
    return ids, labels, weights


def _source_adjusted_item_weights(
    evidence_rows: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, float], dict[str, float], dict[str, list[str]]]:
    """Bound repeated evidence within a dependence cluster.

    Each item's raw quality is explicit_weight × kappa × reliability.  A dependence
    cluster receives at most the quality of its strongest item; members split that
    budget proportionally.  This makes exact duplicates unable to increase total
    cluster mass while preserving quality differences.
    """

    raw: dict[str, float] = {}
    cluster_members: dict[str, list[str]] = defaultdict(list)
    for index, row in enumerate(evidence_rows):
        evidence_id = _require_nonempty_string(row.get("id"), f"evidence[{index}].id")
        if evidence_id in raw:
            raise InputError(f"duplicate evidence id: {evidence_id}")
        explicit_weight = _positive_number(
            row.get("weight", 1.0), f"evidence[{index}].weight", allow_zero=True
        )
        kappa = _bounded_number(row.get("kappa", 1.0), f"evidence[{index}].kappa", 0.0, 1.0)
        reliability = _bounded_number(
            row.get("reliability", 1.0), f"evidence[{index}].reliability", 0.0, 1.0
        )
        raw[evidence_id] = explicit_weight * kappa * reliability
        cluster = _require_nonempty_string(
            row.get("dependence_cluster", evidence_id),
            f"evidence[{index}].dependence_cluster",
        )
        cluster_members[cluster].append(evidence_id)

    adjusted: dict[str, float] = {}
    cluster_budgets: dict[str, float] = {}
    for cluster, members in cluster_members.items():
        member_total = sum(raw[item] for item in members)
        budget = max((raw[item] for item in members), default=0.0)
        cluster_budgets[cluster] = budget
        if member_total <= EPS or budget <= EPS:
            for item in members:
                adjusted[item] = 0.0
        else:
            for item in members:
                adjusted[item] = budget * raw[item] / member_total

    return raw, adjusted, dict(cluster_members)


def _parse_evidence(
    document: Mapping[str, Any],
    hypothesis_ids: Sequence[str],
    *,
    strict_phase: bool,
    warnings: list[str],
) -> tuple[list[Bearing], list[dict[str, Any]], dict[str, list[str]]]:
    rows_any = _require_sequence(document.get("evidence"), "evidence")
    if not rows_any:
        raise InputError("evidence must not be empty")
    rows = [_require_mapping(row, f"evidence[{i}]") for i, row in enumerate(rows_any)]
    raw_weights, adjusted_weights, cluster_members = _source_adjusted_item_weights(rows)

    bearings: list[Bearing] = []
    evidence_audit: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for index, row in enumerate(rows):
        evidence_id = _require_nonempty_string(row.get("id"), f"evidence[{index}].id")
        if evidence_id in seen_ids:
            raise InputError(f"duplicate evidence id: {evidence_id}")
        seen_ids.add(evidence_id)
        source_family = _require_nonempty_string(
            row.get("source_family"), f"evidence[{index}].source_family"
        )
        source_map = row.get("source_map")
        if not isinstance(source_map, str) or not source_map.strip():
            warnings.append(f"evidence[{index}] ({evidence_id}): source_map is missing or empty")
        dependence_cluster = _require_nonempty_string(
            row.get("dependence_cluster", evidence_id),
            f"evidence[{index}].dependence_cluster",
        )
        partition = _require_nonempty_string(
            row.get("partition", "train"), f"evidence[{index}].partition"
        )
        responses = _require_mapping(row.get("responses"), f"evidence[{index}].responses")
        phi_pathway = str(row.get("phi_pathway", "defined"))
        if phi_pathway not in {"defined", "undefined", "partial"}:
            raise InputError(
                f"evidence[{index}].phi_pathway must be defined, partial, or undefined"
            )
        if phi_pathway == "undefined" and responses:
            warnings.append(
                f"evidence[{index}] ({evidence_id}): phi_pathway is undefined but evaluative "
                "responses were supplied; treat them as exploratory, not certified"
            )

        rho_risk = _bounded_number(
            row.get("rho_risk", 0.0), f"evidence[{index}].rho_risk", 0.0, 1.0
        )
        probe_measure = _bounded_number(
            row.get("probe_measure", 1.0), f"evidence[{index}].probe_measure", 0.0, 1.0
        )
        if probe_measure <= EPS:
            warnings.append(
                f"evidence[{index}] ({evidence_id}): probe_measure is zero; this channel is "
                "operationally probe-closed"
            )

        missing_hypotheses = [h for h in hypothesis_ids if h not in responses]
        if missing_hypotheses:
            warnings.append(
                f"evidence[{index}] ({evidence_id}): no response for {missing_hypotheses}"
            )

        for hypothesis_id, response in responses.items():
            if hypothesis_id not in hypothesis_ids:
                raise InputError(
                    f"evidence[{index}].responses references unknown hypothesis {hypothesis_id}"
                )
            value = _response_to_complex(
                response,
                path=f"evidence[{index}].responses.{hypothesis_id}",
                evidence=row,
                strict_phase=strict_phase,
                warnings=warnings,
            )
            bearings.append(
                Bearing(
                    evidence_id=evidence_id,
                    hypothesis_id=hypothesis_id,
                    source_family=source_family,
                    dependence_cluster=dependence_cluster,
                    partition=partition,
                    raw_weight=raw_weights[evidence_id],
                    adjusted_weight=adjusted_weights[evidence_id],
                    value=value,
                )
            )

        evidence_audit.append(
            {
                "id": evidence_id,
                "source_family": source_family,
                "source_map": source_map,
                "source_map_status": str(row.get("source_map_status", "unknown")),
                "method": row.get("method"),
                "data_family": row.get("data_family"),
                "configuration": row.get("configuration"),
                "implementation_lineage": row.get("implementation_lineage"),
                "reasoner_lineage": row.get("reasoner_lineage"),
                "dependence_cluster": dependence_cluster,
                "partition": partition,
                "raw_quality_weight": raw_weights[evidence_id],
                "adjusted_cluster_weight": adjusted_weights[evidence_id],
                "kappa": float(row.get("kappa", 1.0)),
                "phi_pathway": phi_pathway,
                "rho_risk": rho_risk,
                "probe_measure": probe_measure,
                "transport": row.get("transport"),
            }
        )

    return bearings, evidence_audit, cluster_members


def _partition_role(partition: str, holdout_partitions: set[str]) -> str:
    return "holdout" if partition in holdout_partitions else "train"


def _metrics_for_bearings(
    bearings: Iterable[Bearing],
    *,
    support_axis: float,
    refute_axis: float,
    bright_visibility: float,
    dark_visibility: float,
    min_power: float,
    axis_halfwidth: float,
    use_adjusted: bool,
) -> dict[str, Any]:
    rows = list(bearings)
    # In the path-preserving view, one dependence cluster is one effective path.
    # Members first combine internally under their bounded cluster budget; they do
    # not create artificial off-diagonal cross-terms merely by being copied.
    entries: list[tuple[float, complex]] = []
    if use_adjusted:
        grouped: dict[str, list[Bearing]] = defaultdict(list)
        for row in rows:
            grouped[row.dependence_cluster].append(row)
        for cluster_rows in grouped.values():
            weight = sum(row.adjusted_weight for row in cluster_rows)
            value = (
                sum((row.adjusted_weight * row.value for row in cluster_rows), 0j) / weight
                if weight > EPS
                else 0j
            )
            entries.append((weight, value))
    else:
        entries = [(row.raw_weight, row.value) for row in rows]

    weighted_values: list[complex] = []
    incoherent_power = 0.0
    denominator = 0.0
    total_weight = 0.0
    for weight, value in entries:
        weighted = weight * value
        weighted_values.append(weighted)
        total_weight += weight
        denominator += weight * abs(value)
        incoherent_power += weight * (abs(value) ** 2)

    amplitude = sum(weighted_values, 0j)
    visibility = abs(amplitude) / denominator if denominator > EPS else 0.0
    phase = _wrap_angle(cmath.phase(amplitude)) if abs(amplitude) > EPS else 0.0
    support_projection = (
        (amplitude * cmath.exp(-1j * support_axis)).real / denominator
        if denominator > EPS
        else 0.0
    )
    refute_projection = (
        (amplitude * cmath.exp(-1j * refute_axis)).real / denominator
        if denominator > EPS
        else 0.0
    )
    diagonal_power = sum(abs(value) ** 2 for value in weighted_values)
    coherent_power = abs(amplitude) ** 2
    cross_term = coherent_power - diagonal_power
    entry_weight_square_sum = sum(weight**2 for weight, _ in entries)
    effective_count = (
        (sum(weight for weight, _ in entries) ** 2) / entry_weight_square_sum
        if entry_weight_square_sum > EPS
        else 0.0
    )

    if incoherent_power < min_power or denominator <= EPS:
        fringe = "dim_field"
    elif visibility <= dark_visibility:
        fringe = "dark_conflict"
    elif visibility >= bright_visibility:
        if _angular_distance(phase, support_axis) <= axis_halfwidth:
            fringe = "bright_support"
        elif _angular_distance(phase, refute_axis) <= axis_halfwidth:
            fringe = "bright_refute"
        else:
            fringe = "sideband"
    else:
        fringe = "mixed"

    return {
        "input_bearing_count": len(rows),
        "effective_path_count": len(entries),
        "total_weight": total_weight,
        "effective_weighted_path_count": effective_count,
        "amplitude": _complex_json(amplitude),
        "denominator": denominator,
        "visibility": visibility,
        "incoherent_power": incoherent_power,
        "diagonal_weighted_power": diagonal_power,
        "coherent_power": coherent_power,
        "cross_term": cross_term,
        "support_projection": support_projection,
        "refute_projection": refute_projection,
        "fringe": fringe,
    }


def _hypothesis_metrics(
    bearings: Sequence[Bearing],
    hypothesis_ids: Sequence[str],
    settings: Mapping[str, Any],
    holdout_partitions: set[str],
) -> dict[str, Any]:
    support_axis = float(settings["support_axis"])
    refute_axis = float(settings["refute_axis"])
    bright_visibility = float(settings["bright_visibility"])
    dark_visibility = float(settings["dark_visibility"])
    min_power = float(settings["min_power"])
    axis_halfwidth = float(settings["axis_halfwidth"])

    result: dict[str, Any] = {}
    for hypothesis_id in hypothesis_ids:
        hypothesis_rows = [row for row in bearings if row.hypothesis_id == hypothesis_id]
        train = [
            row
            for row in hypothesis_rows
            if _partition_role(row.partition, holdout_partitions) == "train"
        ]
        holdout = [
            row
            for row in hypothesis_rows
            if _partition_role(row.partition, holdout_partitions) == "holdout"
        ]

        train_adjusted = _metrics_for_bearings(
            train,
            support_axis=support_axis,
            refute_axis=refute_axis,
            bright_visibility=bright_visibility,
            dark_visibility=dark_visibility,
            min_power=min_power,
            axis_halfwidth=axis_halfwidth,
            use_adjusted=True,
        )
        train_raw = _metrics_for_bearings(
            train,
            support_axis=support_axis,
            refute_axis=refute_axis,
            bright_visibility=bright_visibility,
            dark_visibility=dark_visibility,
            min_power=min_power,
            axis_halfwidth=axis_halfwidth,
            use_adjusted=False,
        )
        holdout_adjusted = _metrics_for_bearings(
            holdout,
            support_axis=support_axis,
            refute_axis=refute_axis,
            bright_visibility=bright_visibility,
            dark_visibility=dark_visibility,
            min_power=min_power,
            axis_halfwidth=axis_halfwidth,
            use_adjusted=True,
        )

        train_amp = complex(
            train_adjusted["amplitude"]["real"], train_adjusted["amplitude"]["imag"]
        )
        holdout_amp = complex(
            holdout_adjusted["amplitude"]["real"], holdout_adjusted["amplitude"]["imag"]
        )
        if abs(train_amp) > EPS and abs(holdout_amp) > EPS:
            phase_delta = _angular_distance(cmath.phase(train_amp), cmath.phase(holdout_amp))
            phase_lock_cosine = math.cos(phase_delta)
            visibility_gate = min(
                float(train_adjusted["visibility"]), float(holdout_adjusted["visibility"])
            )
            holdout_phase_lock = phase_lock_cosine * visibility_gate
        else:
            phase_delta = None
            phase_lock_cosine = None
            holdout_phase_lock = None

        source_families = sorted({row.source_family for row in train})
        loo_rows: list[dict[str, Any]] = []
        base_denominator = float(train_adjusted["denominator"])
        base_normalized = train_amp / base_denominator if base_denominator > EPS else 0j
        max_distance = 0.0
        for source in source_families:
            remaining = [row for row in train if row.source_family != source]
            metrics = _metrics_for_bearings(
                remaining,
                support_axis=support_axis,
                refute_axis=refute_axis,
                bright_visibility=bright_visibility,
                dark_visibility=dark_visibility,
                min_power=min_power,
                axis_halfwidth=axis_halfwidth,
                use_adjusted=True,
            )
            amplitude = complex(metrics["amplitude"]["real"], metrics["amplitude"]["imag"])
            denominator = float(metrics["denominator"])
            normalized = amplitude / denominator if denominator > EPS else 0j
            distance = min(1.0, abs(base_normalized - normalized) / 2.0)
            max_distance = max(max_distance, distance)
            loo_rows.append(
                {
                    "omitted_source_family": source,
                    "normalized_pattern_distance": distance,
                    "visibility": metrics["visibility"],
                    "support_projection": metrics["support_projection"],
                    "fringe": metrics["fringe"],
                }
            )

        result[hypothesis_id] = {
            "train_path_preserving": train_adjusted,
            "train_unadjusted": train_raw,
            "holdout_path_preserving": holdout_adjusted,
            "holdout_phase_delta_radians": phase_delta,
            "holdout_phase_lock_cosine": phase_lock_cosine,
            "holdout_phase_lock": holdout_phase_lock,
            "source_family_count": len(source_families),
            "source_family_ablation_stability": 1.0 - max_distance,
            "leave_one_source_family_out": loo_rows,
        }
    return result


def _pairwise_hypothesis_metrics(
    bearings: Sequence[Bearing],
    hypothesis_ids: Sequence[str],
    holdout_partitions: set[str],
) -> list[dict[str, Any]]:
    # Collapse each dependence cluster to one effective path for each hypothesis.
    grouped: dict[tuple[str, str], list[Bearing]] = defaultdict(list)
    for row in bearings:
        if _partition_role(row.partition, holdout_partitions) == "train":
            grouped[(row.dependence_cluster, row.hypothesis_id)].append(row)

    collapsed: dict[tuple[str, str], tuple[float, complex]] = {}
    for key, rows in grouped.items():
        weight = sum(row.adjusted_weight for row in rows)
        value = (
            sum((row.adjusted_weight * row.value for row in rows), 0j) / weight
            if weight > EPS
            else 0j
        )
        collapsed[key] = (weight, value)

    clusters = sorted({cluster for cluster, _ in collapsed})
    output: list[dict[str, Any]] = []
    for i, left in enumerate(hypothesis_ids):
        for right in hypothesis_ids[i + 1 :]:
            numerator = 0j
            left_power = 0.0
            right_power = 0.0
            compared = 0
            for cluster in clusters:
                left_entry = collapsed.get((cluster, left))
                right_entry = collapsed.get((cluster, right))
                if left_entry is None or right_entry is None:
                    continue
                weight = min(left_entry[0], right_entry[0])
                left_value = left_entry[1]
                right_value = right_entry[1]
                numerator += weight * left_value * right_value.conjugate()
                left_power += weight * abs(left_value) ** 2
                right_power += weight * abs(right_value) ** 2
                compared += 1
            denominator = math.sqrt(left_power * right_power)
            if denominator > EPS:
                normalized = numerator / denominator
                absolute_overlap = min(1.0, abs(normalized))
                orientation_cosine = max(-1.0, min(1.0, normalized.real))
                contrast = (1.0 - orientation_cosine) / 2.0
                relative_phase = _wrap_angle(cmath.phase(normalized))
            else:
                absolute_overlap = 0.0
                orientation_cosine = 0.0
                contrast = 0.0
                relative_phase = 0.0
            output.append(
                {
                    "left": left,
                    "right": right,
                    "compared_dependence_cluster_count": compared,
                    "absolute_overlap": absolute_overlap,
                    "orientation_cosine": orientation_cosine,
                    "contrast": contrast,
                    "relative_phase_radians": relative_phase,
                }
            )
    return output


def _rank_candidate_probes(
    document: Mapping[str, Any],
    hypothesis_ids: Sequence[str],
    working_weights: Mapping[str, float],
) -> list[dict[str, Any]]:
    rows_any = document.get("candidate_probes", [])
    rows = _require_sequence(rows_any, "candidate_probes")
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row_any in enumerate(rows):
        row = _require_mapping(row_any, f"candidate_probes[{index}]")
        probe_id = _require_nonempty_string(row.get("id"), f"candidate_probes[{index}].id")
        if probe_id in seen:
            raise InputError(f"duplicate candidate probe id: {probe_id}")
        seen.add(probe_id)
        predictions_map = _require_mapping(
            row.get("predictions"), f"candidate_probes[{index}].predictions"
        )
        prediction_basis = row.get("prediction_basis")
        prediction_description = row.get("prediction_description")
        predictions: dict[str, complex] = {}
        for hypothesis_id in hypothesis_ids:
            if hypothesis_id not in predictions_map:
                raise InputError(
                    f"candidate_probes[{index}] ({probe_id}) lacks prediction for {hypothesis_id}"
                )
            predictions[hypothesis_id] = _prediction_to_complex(
                predictions_map[hypothesis_id],
                f"candidate_probes[{index}].predictions.{hypothesis_id}",
                phase_basis=prediction_basis,
                phase_description=prediction_description,
            )
        contrast_sum = 0.0
        pair_contributions: list[dict[str, Any]] = []
        for i, left in enumerate(hypothesis_ids):
            for right in hypothesis_ids[i + 1 :]:
                distance_squared = abs(predictions[left] - predictions[right]) ** 2
                contribution = (
                    working_weights[left] * working_weights[right] * distance_squared
                )
                contrast_sum += contribution
                pair_contributions.append(
                    {
                        "left": left,
                        "right": right,
                        "distance_squared": distance_squared,
                        "weighted_contribution": contribution,
                    }
                )
        independence = _bounded_number(
            row.get("independence", 1.0), f"candidate_probes[{index}].independence", 0.0, 1.0
        )
        path_opening = _bounded_number(
            row.get("path_opening", 1.0), f"candidate_probes[{index}].path_opening", 0.0, 1.0
        )
        source_map_resolution = _bounded_number(
            row.get("source_map_resolution", 0.0),
            f"candidate_probes[{index}].source_map_resolution",
            0.0,
            1.0,
        )
        cost = _positive_number(row.get("cost", 1.0), f"candidate_probes[{index}].cost")
        score = (
            contrast_sum
            * independence
            * path_opening
            * (1.0 + source_map_resolution)
            / cost
        )
        output.append(
            {
                "id": probe_id,
                "label": str(row.get("label", probe_id)),
                "prediction_basis": prediction_basis,
                "prediction_description": prediction_description,
                "score": score,
                "pairwise_contrast": contrast_sum,
                "independence": independence,
                "path_opening": path_opening,
                "source_map_resolution": source_map_resolution,
                "cost": cost,
                "pair_contributions": pair_contributions,
            }
        )
    output.sort(key=lambda item: (-float(item["score"]), str(item["id"])))
    for rank, item in enumerate(output, start=1):
        item["rank"] = rank
    return output


def _settings(document: Mapping[str, Any]) -> dict[str, Any]:
    source = _require_mapping(document.get("settings", {}), "settings")
    support_axis_value = source.get("support_axis", 0.0)
    refute_axis_value = source.get("refute_axis", math.pi)
    if not _is_number(support_axis_value):
        raise InputError("settings.support_axis must be finite radians")
    if not _is_number(refute_axis_value):
        raise InputError("settings.refute_axis must be finite radians")
    settings = {
        "support_axis": float(support_axis_value),
        "refute_axis": float(refute_axis_value),
        "bright_visibility": _bounded_number(
            source.get("bright_visibility", 0.75), "settings.bright_visibility", 0.0, 1.0
        ),
        "dark_visibility": _bounded_number(
            source.get("dark_visibility", 0.35), "settings.dark_visibility", 0.0, 1.0
        ),
        "min_power": _positive_number(
            source.get("min_power", 0.05), "settings.min_power", allow_zero=True
        ),
        "axis_halfwidth": _bounded_number(
            source.get("axis_halfwidth", math.pi / 6.0),
            "settings.axis_halfwidth",
            0.0,
            math.pi,
        ),
    }
    if settings["dark_visibility"] > settings["bright_visibility"]:
        raise InputError("settings.dark_visibility must not exceed bright_visibility")
    holdout_any = source.get("holdout_partitions", ["holdout"])
    holdout_rows = _require_sequence(holdout_any, "settings.holdout_partitions")
    settings["holdout_partitions"] = [
        _require_nonempty_string(item, "settings.holdout_partitions[]") for item in holdout_rows
    ]
    return settings


def analyze_document(document: Mapping[str, Any], *, strict_phase: bool = True) -> dict[str, Any]:
    schema_version = str(document.get("schema_version", SCHEMA_VERSION))
    if schema_version != SCHEMA_VERSION:
        raise InputError(
            f"unsupported schema_version {schema_version!r}; expected {SCHEMA_VERSION!r}"
        )

    warnings: list[str] = []
    hypothesis_ids, labels, working_weights = _parse_hypotheses(document)
    settings = _settings(document)
    holdout_partitions = set(settings["holdout_partitions"])
    bearings, evidence_audit, cluster_members = _parse_evidence(
        document,
        hypothesis_ids,
        strict_phase=strict_phase,
        warnings=warnings,
    )
    metrics = _hypothesis_metrics(bearings, hypothesis_ids, settings, holdout_partitions)
    pairwise = _pairwise_hypothesis_metrics(bearings, hypothesis_ids, holdout_partitions)
    probes = _rank_candidate_probes(document, hypothesis_ids, working_weights)

    source_families = sorted({row.source_family for row in bearings})
    adjusted_cluster_budgets = {
        cluster: sum(
            audit["adjusted_cluster_weight"]
            for audit in evidence_audit
            if audit["dependence_cluster"] == cluster
        )
        for cluster in sorted(cluster_members)
    }
    cluster_budget_values = list(adjusted_cluster_budgets.values())
    total_adjusted = sum(cluster_budget_values)
    sum_squares = sum(value**2 for value in cluster_budget_values)
    effective_cluster_count = (
        (total_adjusted**2) / sum_squares if sum_squares > EPS else 0.0
    )

    return {
        "tool": "aletheia-epistemic-interferometer",
        "tool_version": "3.2.0",
        "schema_version": SCHEMA_VERSION,
        "analysis_name": str(document.get("analysis_name", "unnamed analysis")),
        "nonclaim": (
            "Diagnostics are coherence and discrimination measures, not probabilities that any "
            "hypothesis is true and not evidence of physical quantum cognition or quantum speedup."
        ),
        "settings": settings,
        "hypotheses": [
            {
                "id": hypothesis_id,
                "label": labels[hypothesis_id],
                "working_allocation_weight": working_weights[hypothesis_id],
            }
            for hypothesis_id in hypothesis_ids
        ],
        "provenance_summary": {
            "evidence_count": len(evidence_audit),
            "source_family_count": len(source_families),
            "source_families": source_families,
            "dependence_cluster_count": len(cluster_members),
            "dependence_clusters": cluster_members,
            "adjusted_cluster_budgets": adjusted_cluster_budgets,
            "effective_dependence_cluster_count": effective_cluster_count,
        },
        "evidence_audit": evidence_audit,
        "hypothesis_patterns": metrics,
        "pairwise_hypothesis_geometry": pairwise,
        "candidate_probe_ranking": probes,
        "warnings": sorted(set(warnings)),
    }


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc}") from exc
    return _require_mapping(document, "document")


def _dump_json(value: Any, *, pretty: bool) -> str:
    if pretty:
        return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def _self_test_document() -> dict[str, Any]:
    independent = [
        {
            "id": "E_support_a",
            "source_family": "lab_a",
            "source_map": "independent instrument A",
            "dependence_cluster": "lab_a_primary",
            "partition": "train",
            "kappa": 1.0,
            "reliability": 1.0,
            "phi_pathway": "defined",
            "transport": {
                "phase_basis": "support/refute residual axis",
                "description": "positive residual supports the structural candidate",
            },
            "responses": {
                "H_structure": {"score": 0.9},
                "H_bias": {"score": -0.7},
                "H_null": {"score": -0.4},
            },
        },
        {
            "id": "E_support_b",
            "source_family": "lab_b",
            "source_map": "independent instrument B",
            "dependence_cluster": "lab_b_primary",
            "partition": "train",
            "kappa": 0.95,
            "reliability": 0.95,
            "phi_pathway": "defined",
            "transport": {
                "phase_basis": "support/refute residual axis",
                "description": "transported sign after known orientation reversal",
            },
            "responses": {
                "H_structure": {"score": 0.8},
                "H_bias": {"score": -0.6},
                "H_null": {"score": 0.3},
            },
        },
    ]
    # Twelve copied reports outweigh the independent sources before dependence
    # adjustment, but their shared cluster receives only the quality budget of
    # one report after adjustment.
    echoes = [
        {
            "id": f"E_duplicate_{index}",
            "source_family": "echo",
            "source_map": "copied report",
            "dependence_cluster": "same_press_release",
            "partition": "train",
            "reliability": 0.2,
            "transport": {
                "phase_basis": "support/refute residual axis",
                "description": "same reported signed result",
            },
            "responses": {
                "H_structure": {"score": -1.0},
                "H_bias": {"score": 1.0},
                "H_null": {"score": 0.0},
            },
        }
        for index in range(1, 13)
    ]
    holdout = {
        "id": "E_holdout",
        "source_family": "lab_c",
        "source_map": "fresh holdout instrument",
        "dependence_cluster": "lab_c_holdout",
        "partition": "holdout",
        "transport": {
            "phase_basis": "support/refute residual axis",
            "description": "fresh case transported to common sign basis",
        },
        "responses": {
            "H_structure": {"score": 0.85},
            "H_bias": {"score": -0.65},
            "H_null": {"score": 0.1},
        },
    }
    return {
        "schema_version": "1.0",
        "analysis_name": "self-test",
        "hypotheses": [
            {"id": "H_structure", "working_weight": 0.45},
            {"id": "H_bias", "working_weight": 0.35},
            {"id": "H_null", "working_weight": 0.20},
        ],
        "evidence": independent + echoes + [holdout],
        "candidate_probes": [
            {
                "id": "Q_decisive",
                "cost": 1.0,
                "independence": 1.0,
                "path_opening": 1.0,
                "source_map_resolution": 1.0,
                "predictions": {"H_structure": 1.0, "H_bias": -1.0, "H_null": 0.0},
            },
            {
                "id": "Q_weak",
                "cost": 1.0,
                "independence": 1.0,
                "path_opening": 1.0,
                "predictions": {"H_structure": 0.2, "H_bias": 0.1, "H_null": 0.0},
            },
        ],
    }


def run_self_test() -> None:
    result = analyze_document(_self_test_document(), strict_phase=True)
    patterns = result["hypothesis_patterns"]
    structure = patterns["H_structure"]
    bias = patterns["H_bias"]

    assert structure["train_path_preserving"]["support_projection"] > 0.0
    assert structure["holdout_path_preserving"]["fringe"] == "bright_support"
    assert structure["holdout_phase_lock"] is not None
    assert structure["holdout_phase_lock"] > 0.7
    assert bias["holdout_path_preserving"]["fringe"] == "bright_refute"

    audits = {row["id"]: row for row in result["evidence_audit"]}
    duplicate_total = sum(
        row["adjusted_cluster_weight"]
        for row in result["evidence_audit"]
        if row["dependence_cluster"] == "same_press_release"
    )
    assert math.isclose(duplicate_total, 0.2, rel_tol=0.0, abs_tol=1e-12)
    assert structure["train_unadjusted"]["support_projection"] < 0.0
    assert structure["train_path_preserving"]["fringe"] == "bright_support"
    assert result["candidate_probe_ranking"][0]["id"] == "Q_decisive"

    # Explicit phase without a declared transport must fail in strict mode.
    invalid = _self_test_document()
    invalid["evidence"] = [dict(invalid["evidence"][0])]
    invalid["evidence"][0].pop("transport")
    invalid["evidence"][0]["responses"] = {
        "H_structure": {"magnitude": 1.0, "phase": 0.25},
        "H_bias": {"score": 0.0},
        "H_null": {"score": 0.0},
    }
    try:
        analyze_document(invalid, strict_phase=True)
    except InputError as exc:
        assert "explicit phase requires" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("strict phase validation did not reject undeclared phase")

    # Candidate-probe complex phases also require an operational prediction basis.
    invalid_probe = _self_test_document()
    invalid_probe["candidate_probes"] = [
        {
            "id": "Q_bad_phase",
            "predictions": {
                "H_structure": {"magnitude": 1.0, "phase": 0.2},
                "H_bias": 0.0,
                "H_null": 0.0,
            },
        }
    ]
    try:
        analyze_document(invalid_probe, strict_phase=True)
    except InputError as exc:
        assert "prediction phase requires" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("candidate probe accepted an undeclared complex phase")

    # Equal and opposite independent bearings must produce a dark conflict fringe.
    dark = _self_test_document()
    dark["evidence"] = [
        {
            "id": "D1",
            "source_family": "s1",
            "source_map": "s1",
            "dependence_cluster": "d1",
            "transport": {
                "phase_basis": "support/refute axis",
                "description": "signed bearing",
            },
            "responses": {
                "H_structure": {"score": 1.0},
                "H_bias": {"score": 0.2},
                "H_null": {"score": 0.0},
            },
        },
        {
            "id": "D2",
            "source_family": "s2",
            "source_map": "s2",
            "dependence_cluster": "d2",
            "transport": {
                "phase_basis": "support/refute axis",
                "description": "signed bearing",
            },
            "responses": {
                "H_structure": {"score": -1.0},
                "H_bias": {"score": 0.2},
                "H_null": {"score": 0.0},
            },
        },
    ]
    dark["candidate_probes"] = []
    dark_result = analyze_document(dark, strict_phase=True)
    assert (
        dark_result["hypothesis_patterns"]["H_structure"]["train_path_preserving"]["fringe"]
        == "dark_conflict"
    )

    print("SELF-TEST PASS")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Source-safe, classical quantum-inspired epistemic interferometer"
    )
    parser.add_argument(
        "--self-test", action="store_true", help="run deterministic internal tests and exit"
    )
    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser("analyze", help="analyze an interferometry JSON document")
    analyze_parser.add_argument("input", type=Path)
    analyze_parser.add_argument("--pretty", action="store_true")
    analyze_parser.add_argument(
        "--allow-undeclared-phase",
        action="store_true",
        help="warn instead of failing when a phase transport is undeclared",
    )
    analyze_parser.add_argument("--output", type=Path)

    validate_parser = subparsers.add_parser("validate", help="validate an input document")
    validate_parser.add_argument("input", type=Path)
    validate_parser.add_argument(
        "--allow-undeclared-phase",
        action="store_true",
        help="warn instead of failing when a phase transport is undeclared",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            run_self_test()
            return 0
        if args.command == "analyze":
            document = _load_json(args.input)
            result = analyze_document(
                document, strict_phase=not bool(args.allow_undeclared_phase)
            )
            rendered = _dump_json(result, pretty=bool(args.pretty))
            if args.output:
                args.output.write_text(rendered, encoding="utf-8")
            else:
                sys.stdout.write(rendered)
            return 0
        if args.command == "validate":
            document = _load_json(args.input)
            result = analyze_document(
                document, strict_phase=not bool(args.allow_undeclared_phase)
            )
            print(
                "VALID INPUT: "
                f"hypotheses={len(result['hypotheses'])} "
                f"evidence={result['provenance_summary']['evidence_count']} "
                f"warnings={len(result['warnings'])}"
            )
            return 0
        parser.error("choose --self-test, analyze, or validate")
    except InputError as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 2
    except AssertionError as exc:
        print(f"SELF-TEST FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

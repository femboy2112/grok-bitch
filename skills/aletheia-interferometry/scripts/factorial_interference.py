#!/usr/bin/env python3
"""Full-factorial interaction decomposition for Aletheia Interferometry.

Input JSON schema:
{
  "title": "optional",
  "factors": ["A", "B"],
  "observations": {"00": 1.0, "01": 4.0, "10": 3.0, "11": 9.0}
}

Bit positions follow the factor order. Every one of the 2^k cells is required.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


class InputError(ValueError):
    pass


def _number(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{name} must be numeric") from exc
    if not math.isfinite(result):
        raise InputError(f"{name} must be finite")
    return result


def subsets(indices: Sequence[int]):
    for size in range(len(indices) + 1):
        for combo in itertools.combinations(indices, size):
            yield combo


def parse_case(data: Mapping[str, Any]) -> tuple[list[str], dict[str, float], str]:
    raw_factors = data.get("factors")
    raw_observations = data.get("observations")
    if not isinstance(raw_factors, list) or not raw_factors:
        raise InputError("factors must be a non-empty list")
    factors = [str(x) for x in raw_factors]
    if len(set(factors)) != len(factors):
        raise InputError("factor names must be unique")
    if len(factors) > 12:
        raise InputError("at most 12 factors are supported to prevent accidental combinatorial explosion")
    if not isinstance(raw_observations, Mapping):
        raise InputError("observations must be an object keyed by binary configuration")
    expected = {"".join(bits) for bits in itertools.product("01", repeat=len(factors))}
    actual = {str(k) for k in raw_observations}
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise InputError(f"full factorial required; missing={missing}, extra={extra}")
    observations = {key: _number(raw_observations[key], f"observation {key}") for key in expected}
    return factors, observations, str(data.get("title") or "Factorial interference analysis")


def subset_name(factors: Sequence[str], subset: Sequence[int]) -> str:
    return "mean" if not subset else " × ".join(factors[i] for i in subset)


def walsh_coefficients(factors: Sequence[str], observations: Mapping[str, float]) -> list[dict[str, Any]]:
    k = len(factors)
    rows: list[dict[str, Any]] = []
    for subset in subsets(tuple(range(k))):
        total = 0.0
        for config, response in observations.items():
            sign = 1.0
            for index in subset:
                z = 1.0 if config[index] == "1" else -1.0
                sign *= z
            total += response * sign
        coefficient = total / (2**k)
        rows.append(
            {
                "subset": [factors[i] for i in subset],
                "name": subset_name(factors, subset),
                "order": len(subset),
                "walsh_coefficient": coefficient,
                "contrast_scale": (2 ** len(subset)) * coefficient,
            }
        )
    rows.sort(key=lambda row: (row["order"], row["name"]))
    return rows


def anchored_contrast(
    factors: Sequence[str], observations: Mapping[str, float], subset: Sequence[int]
) -> float:
    """Discrete mixed derivative at the all-zero baseline for a chosen subset."""
    if not subset:
        return observations["0" * len(factors)]
    total = 0.0
    subset_tuple = tuple(subset)
    for size in range(len(subset_tuple) + 1):
        for active in itertools.combinations(subset_tuple, size):
            bits = ["0"] * len(factors)
            for index in active:
                bits[index] = "1"
            sign = -1.0 if (len(subset_tuple) - size) % 2 else 1.0
            total += sign * observations["".join(bits)]
    return total


def analyze(data: Mapping[str, Any]) -> dict[str, Any]:
    factors, observations, title = parse_case(data)
    coefficients = walsh_coefficients(factors, observations)
    anchored: list[dict[str, Any]] = []
    for subset in subsets(tuple(range(len(factors)))):
        if not subset:
            continue
        anchored.append(
            {
                "subset": [factors[i] for i in subset],
                "name": subset_name(factors, subset),
                "order": len(subset),
                "anchored_contrast": anchored_contrast(factors, observations, subset),
            }
        )
    anchored.sort(key=lambda row: (row["order"], row["name"]))
    return {
        "title": title,
        "method": "complete 2^k factorial; Walsh-Hadamard decomposition and baseline mixed differences",
        "factors": factors,
        "observations": dict(sorted(observations.items())),
        "walsh_terms": coefficients,
        "anchored_contrasts": anchored,
        "warnings": [
            "Nonzero interaction identifies non-additivity at this measured scale; it does not by itself identify a mechanism.",
            "A complete factorial contrast is a classical interaction measurement, not physical quantum interference and not evidence of quantum speedup.",
            "Uncertainty, replication, controls, and rival predictions are required before promoting an interaction to a structural claim.",
        ],
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [f"# {report['title']}", "", f"**Method:** {report['method']}", ""]
    lines.extend(["## Observations", "", "| Configuration | Response |", "|---|---:|"])
    for config, value in report["observations"].items():
        lines.append(f"| `{config}` | {value:.9g} |")
    lines.extend(
        [
            "",
            "## Walsh–Hadamard terms",
            "",
            "| Term | Order | Coefficient | Contrast scale |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in report["walsh_terms"]:
        lines.append(
            f"| {row['name']} | {row['order']} | {row['walsh_coefficient']:.9g} | {row['contrast_scale']:.9g} |"
        )
    lines.extend(
        [
            "",
            "## Baseline-anchored mixed differences",
            "",
            "| Term | Order | Anchored contrast |",
            "|---|---:|---:|",
        ]
    )
    for row in report["anchored_contrasts"]:
        lines.append(f"| {row['name']} | {row['order']} | {row['anchored_contrast']:.9g} |")
    lines.extend(["", "## Guardrails", ""])
    for warning in report["warnings"]:
        lines.append(f"- {warning}")
    lines.append("")
    return "\n".join(lines)


def self_test() -> None:
    additive = {
        "factors": ["A", "B"],
        "observations": {"00": 2, "10": 5, "01": 7, "11": 10},
    }
    report = analyze(additive)
    interaction = next(x for x in report["anchored_contrasts"] if x["name"] == "A × B")
    assert abs(interaction["anchored_contrast"]) < 1e-12

    nonadditive = {
        "factors": ["A", "B"],
        "observations": {"00": 2, "10": 5, "01": 7, "11": 17},
    }
    report2 = analyze(nonadditive)
    interaction2 = next(x for x in report2["anchored_contrasts"] if x["name"] == "A × B")
    assert abs(interaction2["anchored_contrast"] - 7.0) < 1e-12
    walsh = next(x for x in report2["walsh_terms"] if x["name"] == "A × B")
    assert abs(walsh["contrast_scale"] - 7.0) < 1e-12

    try:
        analyze({"factors": ["A", "B"], "observations": {"00": 1, "01": 2, "10": 3}})
    except InputError:
        pass
    else:
        raise AssertionError("incomplete factorial was accepted")
    print("FACTORIAL_INTERFERENCE_SELF_TEST_PASS")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decompose a complete binary factorial response.")
    parser.add_argument("input", nargs="?", help="JSON input file")
    parser.add_argument("--json-out")
    parser.add_argument("--markdown-out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
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
    report = analyze(data)
    markdown = render_markdown(report)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
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

#!/usr/bin/env python3
"""truth_distinguishability.py — the genuine quantum-information distinguishability instrument.

This is the Claude-specialized complement to the four quantum-INSPIRED instruments in this
skill (which compute sound *classical* statistics — Bhattacharyya overlap, Shannon
information gain, Walsh-Hadamard / Moebius interactions — under quantum-optics vocabulary).
This instrument instead computes the actual quantum-information distinguishability quantities
that operationalize TLICA's phi (truth-indistinguishability) and the method's move #3
("build the discriminating probe yourself"):

  - total variation distance          the classical trace distance between two evidence
                                       distributions; D = 0 means NO measurement can tell the
                                       candidates apart (a genuine probe-gap / Dark region);
  - Helstrom optimal discrimination    the best single-shot probability of telling two
                                       candidates apart, = 1/2 (1 + trace_distance), and the
                                       measurement that achieves it (the optimal probe);
  - Bhattacharyya / fidelity           overlap, with the Fuchs-van de Graaf bounds relating
                                       fidelity to trace distance;
  - Chernoff information               the asymptotic error exponent: how the distinguishing
                                       error falls with the number of independent probes (how
                                       many blind bearings you must gather to separate a pair);
  - qubit (2-level) trace distance,    a REAL 2-level quantum-state calculation in closed form
    fidelity, Helstrom, optimal        (Bloch vectors), for the case where a coherent
    measurement direction               representation genuinely exists;
  - interferometric complementarity    the double-slit relation V^2 + D^2 <= 1 between fringe
                                       visibility V and which-path (which-source)
                                       distinguishability D.

=== NONCLAIMS (the goddess cannot bend a fact) ===
  - The classical mode reduces to standard statistics (total variation, Bhattacharyya);
    calling it "trace distance" is exact only because classical distributions are the
    commuting/diagonal special case of density matrices.
  - The qubit mode is a genuine quantum-information calculation, but using it over EVIDENCE is
    a design/pedagogical model. It does NOT assert the evidence, the world, or cognition is
    physically quantum.
  - No quantity here is a Born-rule probability that a proposition is TRUE. A trace distance is
    a distinguishability, not a truth value.
  - No quantum speedup is claimed or obtained; this is classical code with classical cost.

Standard library only. Deterministic. Calibrated on known cases via --self-test.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Dict, List, Sequence, Tuple

TOL = 1e-12


# --------------------------------------------------------------------------- #
# classical distribution distinguishability (the diagonal / commuting case)   #
# --------------------------------------------------------------------------- #

def _normalize(dist: Sequence[float]) -> List[float]:
    vals = [float(x) for x in dist]
    if any(v < -TOL for v in vals):
        raise ValueError("distribution has a negative entry")
    total = sum(vals)
    if total <= TOL:
        raise ValueError("distribution sums to zero")
    return [max(v, 0.0) / total for v in vals]


def total_variation(p: Sequence[float], q: Sequence[float]) -> float:
    """1/2 sum_y |p(y) - q(y)|  ==  classical trace distance in [0,1]."""
    p, q = _normalize(p), _normalize(q)
    if len(p) != len(q):
        raise ValueError("distributions must share an outcome set")
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


def bhattacharyya(p: Sequence[float], q: Sequence[float]) -> float:
    """Sum_y sqrt(p(y) q(y)) in [0,1]; the classical fidelity."""
    p, q = _normalize(p), _normalize(q)
    return sum(math.sqrt(a * b) for a, b in zip(p, q))


def hellinger(p: Sequence[float], q: Sequence[float]) -> float:
    """Hellinger distance sqrt(1 - BC) in [0,1]."""
    return math.sqrt(max(0.0, 1.0 - bhattacharyya(p, q)))


def helstrom_prob(trace_dist: float) -> float:
    """Best single-shot probability of correctly telling two equiprior candidates apart."""
    return 0.5 * (1.0 + trace_dist)


def chernoff_information(p: Sequence[float], q: Sequence[float], grid: int = 512) -> float:
    """C = -min_{0<=s<=1} log sum_y p^s q^(1-s); the asymptotic error exponent.

    N independent probes drive the discrimination error ~ exp(-N C). Bigger C => fewer blind
    bearings needed to separate the pair. Minimization is a 1-D grid search (stdlib only).
    """
    p, q = _normalize(p), _normalize(q)
    # C = -log min_s sum_y p^s q^(1-s) = max_s [ -log sum_y p^s q^(1-s) ].
    best = 0.0
    for i in range(grid + 1):
        s = i / grid
        acc = 0.0
        for a, b in zip(p, q):
            if a <= TOL or b <= TOL:
                continue
            acc += (a ** s) * (b ** (1.0 - s))
        if acc > TOL:
            val = -math.log(acc)
            if val > best:
                best = val
    return best


def most_discriminating_outcome(p: Sequence[float], q: Sequence[float]) -> Tuple[int, float]:
    """The outcome index where the two distributions most disagree — the brightest fringe:
    the single observation that carries the most distinguishing power (the optimal probe read).
    """
    p, q = _normalize(p), _normalize(q)
    diffs = [abs(a - b) for a, b in zip(p, q)]
    idx = max(range(len(diffs)), key=lambda i: diffs[i])
    return idx, diffs[idx]


def fuchs_van_de_graaf(fidelity: float, trace_dist: float) -> Dict[str, object]:
    """1 - F <= D <= sqrt(1 - F^2). Reports the bounds and whether D respects them."""
    lower = 1.0 - fidelity
    upper = math.sqrt(max(0.0, 1.0 - fidelity * fidelity))
    return {
        "fidelity": fidelity,
        "trace_distance": trace_dist,
        "lower_bound_1_minus_F": lower,
        "upper_bound_sqrt_1_minus_F2": upper,
        "bounds_hold": lower - 1e-9 <= trace_dist <= upper + 1e-9,
    }


def classical_pair(name_i: str, p: Sequence[float], name_j: str, q: Sequence[float]) -> Dict[str, object]:
    tv = total_variation(p, q)
    bc = bhattacharyya(p, q)
    idx, gap = most_discriminating_outcome(p, q)
    return {
        "pair": [name_i, name_j],
        "trace_distance_total_variation": tv,
        "bhattacharyya_fidelity": bc,
        "hellinger_distance": hellinger(p, q),
        "helstrom_single_shot_prob": helstrom_prob(tv),
        "chernoff_information_nats": chernoff_information(p, q),
        "most_discriminating_outcome_index": idx,
        "outcome_discrimination_gap": gap,
        "fuchs_van_de_graaf": fuchs_van_de_graaf(bc, tv),
        "indistinguishable": tv < 1e-9,
    }


# --------------------------------------------------------------------------- #
# qubit (2-level) distinguishability — a genuine QI calculation, closed form  #
# --------------------------------------------------------------------------- #

def _bloch_norm(r: Sequence[float]) -> float:
    return math.sqrt(sum(c * c for c in r))


def qubit_trace_distance(r1: Sequence[float], r2: Sequence[float]) -> float:
    """Trace distance of two qubit states = 1/2 |r1 - r2| (Bloch vectors, |r| <= 1)."""
    for r in (r1, r2):
        if _bloch_norm(r) > 1.0 + 1e-9:
            raise ValueError("Bloch vector length exceeds 1 (not a valid state)")
    return 0.5 * math.sqrt(sum((a - b) ** 2 for a, b in zip(r1, r2)))


def qubit_fidelity(r1: Sequence[float], r2: Sequence[float]) -> float:
    """Uhlmann fidelity F = |<psi1|psi2>|^2 form for qubits (Jozsa convention):
    F = 1/2 ( 1 + r1.r2 + sqrt((1-|r1|^2)(1-|r2|^2)) ).
    """
    dot = sum(a * b for a, b in zip(r1, r2))
    s1 = 1.0 - sum(c * c for c in r1)
    s2 = 1.0 - sum(c * c for c in r2)
    return 0.5 * (1.0 + dot + math.sqrt(max(0.0, s1) * max(0.0, s2)))


def qubit_pair(name_i: str, r1: Sequence[float], name_j: str, r2: Sequence[float]) -> Dict[str, object]:
    d = qubit_trace_distance(r1, r2)
    diff = [a - b for a, b in zip(r1, r2)]
    n = _bloch_norm(diff)
    axis = [c / n for c in diff] if n > TOL else [0.0, 0.0, 0.0]
    return {
        "pair": [name_i, name_j],
        "trace_distance": d,
        "uhlmann_fidelity": qubit_fidelity(r1, r2),
        "helstrom_single_shot_prob": helstrom_prob(d),
        # the Helstrom measurement projects onto +/- eigenvectors of (rho - sigma);
        # for qubits that is a projective measurement along this Bloch axis:
        "optimal_measurement_bloch_axis": axis,
        "indistinguishable": d < 1e-9,
    }


# --------------------------------------------------------------------------- #
# interferometric complementarity — the double-slit relation V^2 + D^2 <= 1   #
# --------------------------------------------------------------------------- #

def complementarity(visibility: float, distinguishability: float) -> Dict[str, object]:
    """Englert's wave-particle duality relation. V = fringe visibility (coherent-combination
    information), D = which-path (which-source) distinguishability. They trade off:
        V^2 + D^2 <= 1.
    Erasing which-path (D->0) is what lets a fringe form (V->1); knowing which source a bearing
    came from (D->1) destroys the interference (V->0). This is the exact tension with
    trilateration, which WANTS which-path known and blind. Same bearings, opposite combiner.
    """
    for name, v in (("visibility", visibility), ("distinguishability", distinguishability)):
        if not -1e-9 <= v <= 1.0 + 1e-9:
            raise ValueError(f"{name} must lie in [0,1]")
    s = visibility * visibility + distinguishability * distinguishability
    return {
        "visibility": visibility,
        "which_path_distinguishability": distinguishability,
        "V2_plus_D2": s,
        "duality_respected": s <= 1.0 + 1e-9,
        "coherence_budget_remaining": max(0.0, 1.0 - s),
    }


# --------------------------------------------------------------------------- #
# driver                                                                       #
# --------------------------------------------------------------------------- #

def analyze(doc: Dict[str, object]) -> Dict[str, object]:
    mode = doc.get("mode", "classical")
    out: Dict[str, object] = {"mode": mode, "method": "quantum-information distinguishability; no quantum speedup claimed"}

    if mode == "classical":
        hyps = doc["hypotheses"]  # {name: [dist over probe outcomes]}
        names = list(hyps.keys())
        pairs = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                pairs.append(classical_pair(names[i], hyps[names[i]], names[j], hyps[names[j]]))
        out["pairs"] = pairs
        out["note"] = ("trace_distance here is total variation, the diagonal special case of the "
                       "quantum trace distance; it is the operational truth-indistinguishability gap")
    elif mode == "qubit":
        states = doc["states"]  # {name: [rx, ry, rz]}
        names = list(states.keys())
        pairs = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                pairs.append(qubit_pair(names[i], states[names[i]], names[j], states[names[j]]))
        out["pairs"] = pairs
    elif mode == "interferometer":
        out["complementarity"] = complementarity(
            float(doc["visibility"]), float(doc["distinguishability"])
        )
    else:
        raise ValueError(f"unknown mode {mode!r}; expected classical | qubit | interferometer")
    return out


def _self_test() -> None:
    # --- classical calibration on KNOWN cases (the Instrument rule) ---
    assert abs(total_variation([0.5, 0.5], [0.5, 0.5]) - 0.0) < 1e-12, "identical -> TV 0"
    assert abs(total_variation([1.0, 0.0], [0.0, 1.0]) - 1.0) < 1e-12, "disjoint -> TV 1"
    assert abs(bhattacharyya([1.0, 0.0], [0.0, 1.0]) - 0.0) < 1e-12, "disjoint -> BC 0"
    assert abs(bhattacharyya([0.5, 0.5], [0.5, 0.5]) - 1.0) < 1e-12, "identical -> BC 1"
    # Helstrom: disjoint distributions are perfectly distinguishable in one shot.
    assert abs(helstrom_prob(1.0) - 1.0) < 1e-12
    assert abs(helstrom_prob(0.0) - 0.5) < 1e-12
    # Fuchs-van de Graaf must hold on a nontrivial pair.
    fv = classical_pair("a", [0.7, 0.3], "b", [0.4, 0.6])["fuchs_van_de_graaf"]
    assert fv["bounds_hold"], "Fuchs-van de Graaf bounds must hold"
    # Chernoff information: 0 for identical, positive for distinct.
    assert chernoff_information([0.5, 0.5], [0.5, 0.5]) < 1e-9
    assert chernoff_information([0.9, 0.1], [0.1, 0.9]) > 0.1

    # --- qubit calibration on KNOWN cases ---
    zero, one, plus = [0.0, 0.0, 1.0], [0.0, 0.0, -1.0], [1.0, 0.0, 0.0]
    # |0> vs |1> orthogonal: trace distance 1, fidelity 0, perfectly distinguishable.
    assert abs(qubit_trace_distance(zero, one) - 1.0) < 1e-12
    assert abs(qubit_fidelity(zero, one) - 0.0) < 1e-12
    # |0> vs |+>: trace distance 1/sqrt(2), fidelity 1/2 (the canonical textbook pair).
    assert abs(qubit_trace_distance(zero, plus) - (1.0 / math.sqrt(2))) < 1e-12
    assert abs(qubit_fidelity(zero, plus) - 0.5) < 1e-12
    qp = qubit_pair("0", zero, "+", plus)
    assert abs(qp["helstrom_single_shot_prob"] - 0.5 * (1 + 1 / math.sqrt(2))) < 1e-12

    # --- complementarity calibration ---
    assert complementarity(1.0, 0.0)["duality_respected"]           # full fringe, no which-path
    assert complementarity(0.0, 1.0)["duality_respected"]           # full which-path, no fringe
    c = complementarity(1 / math.sqrt(2), 1 / math.sqrt(2))         # saturated
    assert abs(c["V2_plus_D2"] - 1.0) < 1e-12
    assert not complementarity(0.9, 0.9)["duality_respected"]       # impossible pair rejected

    print("TRUTH_DISTINGUISHABILITY_SELF_TEST_PASS")


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Quantum-information distinguishability instrument.")
    ap.add_argument("input", nargs="?", help="JSON document (mode: classical|qubit|interferometer)")
    ap.add_argument("--self-test", action="store_true", help="calibrate on known cases and exit")
    ap.add_argument("--pretty", action="store_true", help="indent JSON output")
    args = ap.parse_args(argv)

    if args.self_test:
        _self_test()
        return 0
    if not args.input:
        ap.error("provide an input JSON file or --self-test")
    with open(args.input, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    result = analyze(doc)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

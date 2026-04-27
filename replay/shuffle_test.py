"""
Order-invariance test for BELLA's evidence + reputation calculus.

Hypothesis (RE-austere): the gene is a *surviving-part* — the reformed
whole should be a function of the evidence-set, not of arrival order.

Test: for one case, run BELLA on N random permutations of the same claim
set and compare final m and final source-reputations. Tight clustering
across permutations = strong path-invariance = the gene-geometry is real.
Wide spread = BELLA is path-dependent and the "gene" encodes history,
not just substrate.

Usage:
    python shuffle_test.py wirecard --n 30
"""

from __future__ import annotations
import argparse
import copy
import math
import random
import statistics
import sys

from bella_calc import Entity, _sigmoid, dLambda, update_entity
from runner import load_case


def replay_bella_in_order(claims):
    """Like bella_calc.replay_bella but does NOT re-sort. Caller controls order."""
    entities: dict[str, Entity] = {}
    Lambda_P = 0.0
    for c in claims:
        ent = entities.setdefault(c.source, Entity(c.source, c.source_role))
        dL = dLambda(c, ent)
        Lambda_P += dL
        update_entity(ent, dL, role="source")
    return {
        "final_m":    _sigmoid(Lambda_P),
        "final_Lambda": Lambda_P,
        "final_reps": {name: e.rep for name, e in entities.items()},
    }


def run(case_name: str, n_perms: int, seed: int):
    _, claims, meta = load_case(case_name)
    print()
    print(f"──────────── {case_name} · order-invariance ({n_perms} perms) ────────────")
    print(f"  target: {meta['target_proposition']}")
    print(f"  truth:  {meta['final_truth']}")
    print(f"  N claims: {len(claims)}")
    print()

    # Baselines (deterministic orderings)
    by_date = sorted(claims, key=lambda c: c.date)
    rev_date = list(reversed(by_date))

    base = replay_bella_in_order(by_date)
    rev = replay_bella_in_order(rev_date)

    # Random permutations
    rng = random.Random(seed)
    final_ms = []
    final_reps_by_source = {s: [] for s in base["final_reps"]}
    for _ in range(n_perms):
        shuffled = list(claims)
        rng.shuffle(shuffled)
        result = replay_bella_in_order(shuffled)
        final_ms.append(result["final_m"])
        for s in final_reps_by_source:
            final_reps_by_source[s].append(result["final_reps"].get(s, 0.5))

    # Capture both m and Lambda — m saturates near 0/1, Lambda reveals
    # the underlying spread that the sigmoid hides.
    final_lambdas = []
    rng2 = random.Random(seed)
    for _ in range(n_perms):
        shuffled = list(claims)
        rng2.shuffle(shuffled)
        result = replay_bella_in_order(shuffled)
        final_lambdas.append(result["final_Lambda"])

    mean_m = statistics.mean(final_ms)
    stdev_m = statistics.stdev(final_ms) if len(final_ms) > 1 else 0.0
    min_m, max_m = min(final_ms), max(final_ms)
    mean_L = statistics.mean(final_lambdas)
    stdev_L = statistics.stdev(final_lambdas) if len(final_lambdas) > 1 else 0.0
    min_L, max_L = min(final_lambdas), max(final_lambdas)

    print(f"  {'ordering':<28} {'final m':>10} {'final Λ':>10}")
    print(f"  {'─' * 28} {'─' * 10} {'─' * 10}")
    print(f"  {'date-ascending (canonical)':<28} {base['final_m']:>10.4f} {base['final_Lambda']:>10.3f}")
    print(f"  {'date-descending':<28} {rev['final_m']:>10.4f} {rev['final_Lambda']:>10.3f}")
    print(f"  {'random — mean':<28} {mean_m:>10.4f} {mean_L:>10.3f}")
    print(f"  {'random — stdev':<28} {stdev_m:>10.4f} {stdev_L:>10.3f}")
    print(f"  {'random — min':<28} {min_m:>10.4f} {min_L:>10.3f}")
    print(f"  {'random — max':<28} {max_m:>10.4f} {max_L:>10.3f}")
    print(f"  {'random — range':<28} {max_m - min_m:>10.4f} {max_L - min_L:>10.3f}")
    print()
    if base['final_Lambda'] != 0:
        rel_spread = (max_L - min_L) / abs(base['final_Lambda']) * 100
        print(f"  Λ relative spread: {rel_spread:.2f}% of |Λ_canonical|")
        print()

    # Source reputation spread
    print(f"  {'source':<32} {'canonical':>10} {'mean':>10} {'stdev':>10} {'range':>10}")
    print(f"  {'─' * 32} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10}")
    for s, reps in sorted(final_reps_by_source.items()):
        canon = base["final_reps"].get(s, 0.5)
        mean_r = statistics.mean(reps)
        stdev_r = statistics.stdev(reps) if len(reps) > 1 else 0.0
        range_r = max(reps) - min(reps)
        print(f"  {s[:32]:<32} {canon:>10.4f} {mean_r:>10.4f} {stdev_r:>10.4f} {range_r:>10.4f}")
    print()

    # Verdict — judge on Λ (which doesn't saturate), not on m
    if abs(base["final_Lambda"]) > 0.01:
        rel = (max_L - min_L) / abs(base["final_Lambda"])
    else:
        rel = max_L - min_L
    print("  Reading the result:")
    if rel < 0.02:
        verdict = "STRONG path-invariance — gene behaves as a surviving-part"
    elif rel < 0.10:
        verdict = "MODERATE path-invariance — gene is mostly substrate, mildly history-coloured"
    else:
        verdict = "WEAK path-invariance — gene encodes significant history; not a clean surviving-part"
    print(f"    Λ relative spread: {rel*100:.2f}% of |Λ_canonical|")
    print(f"    → {verdict}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case", help="case name (e.g. wirecard)")
    ap.add_argument("--n", type=int, default=30, help="number of random permutations")
    ap.add_argument("--seed", type=int, default=42, help="rng seed")
    args = ap.parse_args()
    run(args.case, args.n, args.seed)


if __name__ == "__main__":
    main()

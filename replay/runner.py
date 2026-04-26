"""
Case-parametric BELLA replay runner.

Usage:
    python runner.py <case>        # e.g. wirecard, theranos, wakefield, hydroxychloroquine
    python runner.py --all          # runs all four cases and prints a summary pattern table

Each case has its own directory under cases/<name>/:
    claims.csv          the curated claim set (with verified=FALSE by default)
    meta.json           case metadata (target proposition, final truth, collapse date, key sources)
Outputs written to cases/<name>/:
    replay_results.csv
    plot_trajectories.png
    plot_reputation.png
"""

from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from datetime import datetime
from pathlib import Path

from bella_calc import (
    Claim, replay_bella, replay_naive_majority, replay_vanilla_bayes,
)

HERE = Path(__file__).parent
CASES_DIR = HERE / "cases"


# ═════════════════════════════════════════════════════════════════════
# Per-case loading
# ═════════════════════════════════════════════════════════════════════

def _parse_bool(s: str) -> bool:
    return str(s).strip().lower() in ("true", "1", "yes", "y")


def load_case(case_name: str):
    case_dir = CASES_DIR / case_name
    claims_path = case_dir / "claims.csv"
    meta_path = case_dir / "meta.json"

    claims = []
    with open(claims_path) as f:
        for row in csv.DictReader(f):
            claims.append(Claim(
                id=row["id"],
                date=row["date"],
                source=row["source"],
                source_role=row["source_role"],
                stance=row["stance"],
                modality=row["modality"],
                lr_base=float(row["lr_base"]),
                grounding=float(row.get("grounding", 0.7)),
                text=row.get("claim_text", ""),
                verified=_parse_bool(row.get("verified", "FALSE")),
            ))

    with open(meta_path) as f:
        meta = json.load(f)

    return case_dir, claims, meta


# ═════════════════════════════════════════════════════════════════════
# Analysis
# ═════════════════════════════════════════════════════════════════════

def _first_crossing(traj, threshold: float, direction: str):
    """
    Return (date, claim_id, ratio_before_total) of the first timestep where
    m crosses the threshold in the given direction; else None.
      direction='up'   → first m ≥ threshold
      direction='down' → first m ≤ threshold
    """
    n = len(traj)
    for i, t in enumerate(traj):
        m = t["m"]
        if direction == "up" and m >= threshold:
            return t["date"], t["id"], i / max(n - 1, 1)
        if direction == "down" and m <= threshold:
            return t["date"], t["id"], i / max(n - 1, 1)
    return None


def _robust_commitment(traj, threshold: float, direction: str):
    """
    Fraction of claim timesteps AFTER first crossing that remained on the
    correct side (≥ threshold for up, ≤ for down). Measures whether the
    engine's verdict sticks or flaps under counter-attack.
    """
    cross = _first_crossing(traj, threshold, direction)
    if cross is None:
        return None
    _, _, cross_ratio = cross
    start = int(cross_ratio * (len(traj) - 1))
    tail = traj[start:]
    if not tail:
        return 1.0
    on_correct = sum(
        1 for t in tail
        if (direction == "up"   and t["m"] >= threshold)
        or (direction == "down" and t["m"] <= threshold)
    )
    return on_correct / len(tail)


def summarise(bella, vanilla, majority, meta):
    final_truth = meta["final_truth"]   # "TRUE" or "FALSE"
    if final_truth == "TRUE":
        direction = "up"
        threshold = 0.5
    else:  # "FALSE" — correct m should be LOW
        direction = "down"
        threshold = 0.5

    print()
    print("═" * 72)
    print(f"  Target: {meta['target_proposition']}")
    print(f"  Ground truth: {final_truth}  (correct direction: {direction})")
    print(f"  Threshold: m {'≥' if direction == 'up' else '≤'} {threshold}")
    print("═" * 72)
    print()
    print(f"  {'engine':<12} {'first crossing':<16} {'  robustness':<14} {'final m':<9}")

    results = {}
    for name, traj in [("BELLA",    bella),
                       ("vanilla",  vanilla),
                       ("majority", majority)]:
        cross = _first_crossing(traj, threshold, direction)
        rob = _robust_commitment(traj, threshold, direction)
        final_m = traj[-1]["m"]
        cross_str = f"{cross[0]}" if cross else "never"
        rob_str = f"{rob:.2f}" if rob is not None else "—"
        print(f"  {name:<12} {cross_str:<16} {rob_str:<14} {final_m:.3f}")
        results[name] = {
            "first_cross_date": cross[0] if cross else None,
            "first_cross_id":   cross[1] if cross else None,
            "robustness":       rob,
            "final_m":          final_m,
        }
    print()
    return results


# ═════════════════════════════════════════════════════════════════════
# Output
# ═════════════════════════════════════════════════════════════════════

def write_results_csv(case_dir: Path, bella, vanilla, majority, meta):
    key_sources = meta.get("key_sources", [])
    rows = []
    for b, v, m in zip(bella, vanilla, majority):
        rows.append({
            "date":          b["date"],
            "claim_id":      b["id"],
            "source":        b["source"],
            "stance":        b["stance"],
            "modality":      b["modality"],
            "m_bella":       round(b["m"], 4),
            "m_vanilla":     round(v["m"], 4),
            "m_majority":    round(m["m"], 4),
            "Lambda_bella":  round(b["Lambda_P"], 4),
            **{f"rep_{s}":   round(b["rep_snapshot"].get(s, 0.5), 4)
               for s in key_sources},
        })
    with open(case_dir / "replay_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_trajectories(case_dir: Path, bella, vanilla, majority, meta):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    fig, ax = plt.subplots(figsize=(14, 6), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")

    xs = [datetime.fromisoformat(t["date"]) for t in bella]
    ax.plot(xs, [t["m"] for t in bella],
            color="#62d196", linewidth=2.4, marker="o", markersize=5,
            label="BELLA")
    ax.plot(xs, [t["m"] for t in vanilla],
            color="#82a2e3", linewidth=1.6, linestyle="--",
            label="vanilla Bayes")
    ax.plot(xs, [t["m"] for t in majority],
            color="#c39bd3", linewidth=1.6, linestyle=":",
            label="naive majority")

    ax.axhline(0.5, color="#30363d", linewidth=0.8, alpha=0.7)

    resolution_date = meta.get("resolution_date")
    if resolution_date:
        rd = datetime.fromisoformat(resolution_date)
        ax.axvline(rd, color="#e57373", linewidth=1.0, alpha=0.8)
        ax.text(rd, 0.98, f" {meta.get('resolution_label', 'resolution')}",
                color="#e57373", fontsize=10, va="top", ha="left")

    ax.set_ylim(0, 1.02)
    ax.set_xlabel("date", color="#e6edf3")
    ax.set_ylabel(f"m({meta['target_short']})", color="#e6edf3")
    ax.set_title(f"{meta['case_title']} · m trajectory",
                 color="#e6edf3", fontsize=13, pad=12)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.tick_params(colors="#8b949e")
    ax.xaxis.label.set_color("#e6edf3")
    ax.yaxis.label.set_color("#e6edf3")
    ax.legend(loc="best", frameon=False, labelcolor="#e6edf3")
    ax.grid(alpha=0.15, color="#30363d")

    fig.tight_layout()
    fig.savefig(case_dir / "plot_trajectories.png",
                dpi=150, facecolor="#0d1117", bbox_inches="tight")
    plt.close(fig)


def plot_reputation(case_dir: Path, bella, meta):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    key_sources = meta.get("key_sources", [])
    palette_cycle = [
        "#62d196", "#6ec28c", "#82a2e3", "#e57373",
        "#fb7185", "#f0ad4e", "#c39bd3", "#ffd166",
        "#8ac6d1", "#ff6b9d", "#9fd356",
    ]

    fig, ax = plt.subplots(figsize=(14, 6), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")

    xs = [datetime.fromisoformat(t["date"]) for t in bella]
    for i, source in enumerate(key_sources):
        ys = [t["rep_snapshot"].get(source, 0.5) for t in bella]
        color = palette_cycle[i % len(palette_cycle)]
        ax.plot(xs, ys, color=color, linewidth=2.0,
                marker="o", markersize=3, label=source, alpha=0.9)

    ax.axhline(0.5, color="#30363d", linewidth=0.8, alpha=0.7)

    resolution_date = meta.get("resolution_date")
    if resolution_date:
        rd = datetime.fromisoformat(resolution_date)
        ax.axvline(rd, color="#e57373", linewidth=1.0, alpha=0.6)

    ax.set_ylim(0, 1.02)
    ax.set_xlabel("date", color="#e6edf3")
    ax.set_ylabel("rep(E)  =  σ(Λ_E)", color="#e6edf3")
    ax.set_title(f"{meta['case_title']} · rep trajectory",
                 color="#e6edf3", fontsize=13, pad=12)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.tick_params(colors="#8b949e")
    ax.xaxis.label.set_color("#e6edf3")
    ax.yaxis.label.set_color("#e6edf3")
    ax.legend(loc="center left", frameon=False, labelcolor="#e6edf3",
              bbox_to_anchor=(1.01, 0.5), fontsize=9)
    ax.grid(alpha=0.15, color="#30363d")

    fig.tight_layout()
    fig.savefig(case_dir / "plot_reputation.png",
                dpi=150, facecolor="#0d1117", bbox_inches="tight")
    plt.close(fig)


# ═════════════════════════════════════════════════════════════════════
# Entry points
# ═════════════════════════════════════════════════════════════════════

def run_case(case_name: str):
    print()
    print(f"──────────── {case_name} ────────────")
    case_dir, claims, meta = load_case(case_name)

    unverified = [c for c in claims if not c.verified]
    print(f"  loaded {len(claims)} claims ({len(unverified)} unverified)")

    bella    = replay_bella(claims)
    vanilla  = replay_vanilla_bayes(claims)
    majority = replay_naive_majority(claims)

    results = summarise(bella, vanilla, majority, meta)
    write_results_csv(case_dir, bella, vanilla, majority, meta)
    plot_trajectories(case_dir, bella, vanilla, majority, meta)
    plot_reputation(case_dir, bella, meta)

    return {"case": case_name, "meta": meta, "results": results}


def run_all():
    cases = ["wirecard", "theranos", "wakefield", "hydroxychloroquine"]
    outcomes = [run_case(c) for c in cases]

    print()
    print("═" * 90)
    print("  PATTERN TABLE · does BELLA reach the correct verdict earlier / more robustly")
    print("  than baselines, across structurally-different adversarial events?")
    print("═" * 90)
    print(f"  {'case':<20} {'truth':<6} {'BELLA final':<14} "
          f"{'vanilla final':<15} {'BELLA robust':<14} {'vanilla robust':<15}")
    for o in outcomes:
        c = o["case"]
        truth = o["meta"]["final_truth"]
        r = o["results"]
        br = r["BELLA"]["robustness"]
        vr = r["vanilla"]["robustness"]
        print(f"  {c:<20} {truth:<6} "
              f"{r['BELLA']['final_m']:<14.3f} "
              f"{r['vanilla']['final_m']:<15.3f} "
              f"{(f'{br:.2f}' if br is not None else '—'):<14} "
              f"{(f'{vr:.2f}' if vr is not None else '—'):<15}")
    print()
    print("  Reading the table:")
    print("    For TRUE cases, high final m + high robustness means the engine")
    print("    reached and held the correct verdict. For FALSE cases, LOW final m")
    print("    and high robustness (measured on downward crossing) means the engine")
    print("    correctly refused to be convinced.")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case", nargs="?", default=None,
                    help="case name (subdir of cases/); omit with --all")
    ap.add_argument("--all", action="store_true",
                    help="run every case under cases/ and print pattern table")
    args = ap.parse_args()

    if args.all:
        run_all()
    elif args.case:
        run_case(args.case)
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

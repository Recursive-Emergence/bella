# BELLA Replay — Four Historical Events

*Validation attempt on real historical events with settled ground truth.*
Feeds curated claim sets through BELLA's evidence + reputation calculus
(per `bella/SPEC.md` §2 + §8) and compares to vanilla Bayes + naive
majority baselines, across four structurally-different adversarial cases.

## The four cases, chosen for pattern diversity

| case | pattern | ground truth | resolution |
|---|---|---|---|
| **Wirecard** (2014–2020) | specialist filter right, institutional consensus wrong | TRUE — was fraud | 2020-06-25 collapse |
| **Theranos** (2013–2018) | specialist filter (Carreyrou/WSJ) + insider whistleblowers right, Silicon Valley / Fortune / investor consensus wrong | TRUE — was fraud | 2018-09-05 dissolution |
| **Wakefield MMR** (1998–2010) | INVERTED — initial claim (MMR→autism) gained traction; minority investigator (Deer) + epidemiological consensus corrected it | TRUE — paper was fraud | 2010-05-24 struck off register |
| **Hydroxychloroquine** (2020–2021) | FALSE-POSITIVE TEST — vocal minority (Raoult, Trump, Zelenko) pushed it; RCTs resolved negative | FALSE — not effective | 2020-10-15 Solidarity trial |

Chosen so BELLA can't just be "pro-minority-contrarian": Wakefield makes it correct a widely-believed wrong claim, and HCQ makes it reject a vocal minority.

## Scaffold status

**ALL 64 CLAIMS UNVERIFIED.** Rows were composed from memory of the public
record. Dates, wording, and modalities should be cross-checked against
primary sources (case-specific citations in each `claims.csv`'s
`citation_hint` column) before any result gets quoted. The runner warns
on every unverified claim.

## Pattern table (unverified claims, first pass)

```
case                 truth   BELLA final    vanilla final   BELLA robust   vanilla robust
wirecard             TRUE    1.000          0.889           1.00           0.71
theranos             TRUE    1.000          0.996           0.94           0.75
wakefield            TRUE    1.000          0.998           1.00           1.00
hydroxychloroquine   FALSE   0.000          0.111           1.00           1.00
```

**robustness** = fraction of claim timesteps *after* first correct-side
crossing that remained on the correct side. 1.00 = never flapped back;
lower = engine's verdict wobbled under counter-attack.

## Four observations, with honest caveats

**1. BELLA reaches the correct verdict in all four cases.**
Including the FALSE-case HCQ (final m = 0.000). No false positives, no
false negatives on the direction of the verdict.

**2. BELLA's clearest advantage is in sustained-institutional-counter-attack cases.**
On Wirecard (BaFin ban, three Wirecard-PR denials over 5 years) and
Theranos (Holmes' CNBC rebuttal, Walgreens endorsement, Fortune profile)
BELLA's robustness is 1.00 / 0.94 against vanilla's 0.71 / 0.75. This
is where the rep cycle earns its keep: it learns which sources were
previously wrong and downweights their continued counters. Where
counter-attack is weak or one-off (Wakefield's sporadic advocacy, HCQ's
short proponent phase) all three engines tie at 1.00 robustness.

**3. BELLA has a visible initial-overshoot on HCQ.**
BELLA climbed to m ≈ 0.77 during the Raoult / Trump / FDA-EUA / Zelenko
proponent phase in March 2020 before crashing to near zero when the NIH
guideline and negative trials arrived. If a user had read BELLA's output
in mid-March 2020 they would have seen "probably effective" — wrong.
The rep cycle corrected fast once institutional negatives arrived, but
the initial reading was not reliable. This is a structural limit, not
a bug: BELLA cannot predict what a yet-unmade observation will say.

**4. `lr_base` calibration does most of the work.**
The late-stage strong-evidence lr values (20 for admission, 15 for
license-revocation, 18 for systematic_review) drive m to the asymptotes
of 0 or 1 in all four cases. A hostile reader could set those values
differently and get different stories. The sensitivity sweep is mandatory
before any result here gets published.

## What this justifies

These runs provide a first empirical answer to Marcelo's real-world
question: does BELLA's calculus distinguish conspiracy from factual
bubbles *in the wild*?

**Necessary condition passed** on four independent events with settled
ground truth and different structural patterns. BELLA handles the
consensus-wrong case (Wirecard, Theranos), the inverted-initial-claim
case (Wakefield), and the false-positive case (HCQ).

## What this does NOT justify

- **Sufficient condition**. Four events, curator-selected, curator-calibrated,
  unverified. Any two of those can be wrong without the third saving it.
- **Against-adversary robustness**. A hostile curator can pick claim sets
  or `lr_base` values to make BELLA look wrong. Pre-registration of
  case / calibration before running inference is the honest next step.
- **Comparison to production pipeline**. These runs use the standalone
  calculus in `bella_calc.py`; they do not use `bella/grow.py`'s full
  extraction + entity resolution + graph walk. A production replay is
  the next honest check.

## Usage

```bash
cd replay
python runner.py wirecard              # one case
python runner.py --all                  # all four + pattern table
```

Output per case in `cases/<name>/`:
- `replay_results.csv` — per-claim trajectory of all three engines + rep snapshots
- `plot_trajectories.png` — three-line m chart with resolution date marked
- `plot_reputation.png` — per-source rep trajectory

## Layout

```
replay/
├── bella_calc.py                 # shared calculus (SPEC §2 + §8)
├── runner.py                     # parametric runner (one case or --all)
├── README.md                     # this file
└── cases/
    ├── wirecard/
    │   ├── claims.csv            # 17 claims, unverified
    │   ├── meta.json             # case metadata for the runner
    │   ├── replay_results.csv
    │   ├── plot_trajectories.png
    │   └── plot_reputation.png
    ├── theranos/         (same structure — 17 claims)
    ├── wakefield/        (15 claims)
    └── hydroxychloroquine/ (16 claims)
```

## Next iterations

1. **Verify every claim** in every case. Primary-source cross-check,
   day-level date accuracy, wording fidelity. Flip `verified=TRUE`
   row-by-row in each `claims.csv`.
2. **Sensitivity analysis on `lr_base`**. Sweep ± 30 % on each case's
   calibration; report how much the robustness metric shifts. If BELLA's
   advantage disappears under modest re-calibration, that's the honest
   answer.
3. **Pre-registration protocol**. Freeze a test case, have someone else
   write the claim set + priors, then run BELLA — so the curator cannot
   see the engine's answer while building the data.
4. **Production pipeline replay**. Feed the same claims into
   `bella/grow.py` to check agreement between standalone calculus and
   full pipeline.
5. **One more case that stresses something new**. Candidates:
   - Bernie Madoff (Markopolos vs SEC — another specialist-right case,
     tests replication of Wirecard / Theranos)
   - Flint water crisis (government denial vs residents + Dr. Hanna-Attisha)
   - Reinhart-Rogoff Excel error (academic consensus wrong, small finding
     right — low-drama test)

## Honest summary for Marcelo

Your concern was: can graph + observations distinguish factual from
conspiracy bubbles *in the wild*? We ran BELLA's calculus on four
historical events where ground truth is settled and patterns differ.
Result: **necessary condition passed in all four cases**, with a real
advantage over vanilla Bayes specifically in sustained-institutional-
counter-attack cases (Wirecard, Theranos), and a measurable but not
fatal initial-overshoot in the proponent-noise case (HCQ).

This is empirical evidence, not proof. The claims are unverified,
priors are curator-calibrated, and four events is few. A pre-registered
blind test on a fifth case, or a sensitivity-sweep that demonstrates
robustness to ± 30 % calibration drift, would be the next honest step.

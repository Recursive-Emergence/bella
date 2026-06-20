# BELLA Changelog

## Unreleased — 2026-05-04

### Engine / Architecture
- `replay/streaming/` package added — multi-proposition gene growth via
  per-claim LLM action selection (gpt-4o-mini, temperature 0) +
  text-embedding-3-small for similarity. Pipeline:
  embed → field projection (T5 locality) → top-k within-field gene
  fragment → LLM emits one structured action {ROOT/CONFIRM/AMEND/
  CHILD/COUNTER} with required `i1_check` audit → mutate gene → persist
  events.jsonl. Per-run cost: ~$0.02 for ~50 claims through gpt-4o-mini
  (small-model cost holds because the expensive cognition is split:
  embeddings handle recall, the cheap LLM handles per-claim decisions).
- Field-aware projection: each ROOT seeds a Field with a running
  embedding centroid; new claims route to best-cosine field if
  `cosine > θ_field` (default 0.30), else fall through to a field
  overview. Persisted in events.jsonl as `projection.mode` + `best_field`
  + `best_field_cos` so every routing decision is auditable.
- R3 EMERGE generalized to two scopes — field-level (existing) and
  within-field (new). The within-field variant catches duplicate
  beliefs that landed in one field as separate children, the
  K-prediction / H-report convergence pattern from the gene exercise.
  ⊥-guard added per SPEC I2: pairs already in an explicit denial
  relation are excluded from merge candidates.
- REROOT operator added — the dual of MERGE at field scope. When a
  field's centroid drifts from its current structural root anchor,
  REROOT promotes a centroid-nearer member to root and demotes the
  current root to a CHILD with kernel-chosen relation. Field handle
  (`Field.id`) decoupled from current structural root (`Field.root_id`)
  so re-rooting preserves stable identity for events/projections.

### Theory
- The **simple operator at any level** family — articulated as the
  recursive operator pattern that connects R3 EMERGE across scopes.
  Three structural operators (MERGE, REROOT, SPLIT) + one self-
  referential R4 operator (Ψ-anomaly) so far. Same operator shape —
  compute pattern over items at a level, propose mutation — applied at
  claim-, proposition-, field-, theme-, worldview- levels. SPEC v0.2
  should write `EMERGE_N: items at level N → items at level N` once
  rather than per-level.
- **Ψ-anomaly** is the first R4 (SELF-REFER) operator implemented as
  code. Flags 1v high-mass propositions whose topic area is
  well-covered by other voices that did NOT corroborate them — exactly
  the pattern the hand-built analysis catches manually
  ("anomalous absence of corroboration given the magnitude").
  Demonstrated on the 8-voice Hormuz case: the Supreme Leader killing
  claim (NYT-only, m=0.86, 5 other voices touch the topic without
  confirming) was correctly surfaced by Ψ-anomaly, matching the hand-
  built analysis's "1v claim of high magnitude lacks corroboration"
  flag.

### Empirical
- `replay/streaming/cliff.py` (v1) and `cliff_v2.py` (v2) — the cliff
  experiment as falsifiable test of the gene-as-recipe / KB-as-cache
  reframing. v1 preserved the central proposition's field and pruned
  others; m saturated at 0.998 across all pruning levels (tests
  robustness, not regeneration). v2 deleted the central field too;
  the central thesis re-emerged identically (cos=1.000, m=0.819) at
  every pruning level k+1 ∈ {1, 3, 5, 7, 9} on Hormuz. **Recipe
  hypothesis empirically confirmed at this scale, for explicit
  single-source-anchored central theses, under up to 55% adjacent-
  field pruning.** Voice-multiplicity reconstruction failed (|V|
  dropped 2 → 1) — exactly the T6 (identity primitive) gap.
- `replay/streaming/shuffle_streaming.py` — order-invariance test
  for the streaming pipeline. On Hormuz: surface metrics (n_props,
  n_roots, max_m) tightly stable across 6 orderings (max_m stdev
  0.004); belief-identity convergence partial (top-3 by m matches
  canonical in 2/5 shuffled runs at cosine > 0.85). The streaming
  calculus is **mass-invariant** but **identity-only-partially-
  invariant** under ordering — exactly what T6 + T2 predict.
- `replay/cases/hormuz/` — eight-voice live-event case built up
  incrementally: W (partisan WeChat), G (Gardner AFR voter
  reporting), Dyer (syndicated column), T_D (Thompson/Douthat
  podcast), K (Krugman op-ed), H (Hersh insider/officer), S (Smolar
  Le Monde), Kanno_Youngs (NYT mainstream record). 69 claims, 13+
  distinct sources. Order-invariance Λ spread 0.67% under 30 perms
  on the mechanical layer.

### Discovered
- **First-mover root anomaly** — non-deterministic LLM choice on
  early claims can lock low-credibility partisan claims as field
  anchors. Subsequent high-credibility claims get routed in by
  cosine and amend the partisan root, producing semantically
  incoherent field labels. Anomaly intermittent across runs.
  REROOT operator addresses it; SPLIT (not yet built) would address
  the related field-overgrowth pattern (one field accumulating
  semantically heterogeneous children).
- **The hand-built vs streaming gap** — comparing a fully hand-
  reasoned BELLA mapping (8th voice essay walking through Kanno-
  Youngs as a 1v anomaly carrier) against the streaming runner's
  output revealed: streaming + R3 EMERGE accumulates mass and
  collapses duplicates correctly at the local level, but does not
  perform R4-flavored meta-pattern moves (anomaly-flag, blindspot-
  detect, frame-expansion-detect, cross-field synthesis). The
  hand-built analysis was doing R4 implicitly across the whole
  gene state. Adding Ψ-anomaly as the first R4 operator closes one
  specific gap (anomaly-flag); two more — Ψ-blindspot and
  Ψ-synthesis — surfaced as natural next operators of the same
  recursive shape.

## Unreleased — 2026-05-03

### Theory / agenda
- `CHALLENGES.md` added — consolidates open theory and engineering
  work surfaced by the empirical exercises so far. Framed by the
  load-bearing architectural reframe: at world-model scale the gene
  is a *recipe* (not a snapshot) and the stored graph is a *cache*
  (not the canonical state). Eight theory items (proposition/claim
  collapse, gene grammar limits, hypergraph as primitive, voice
  cross-source dependence, locality, identity, R5 multi-cycle
  convergence, multiple-hypothesis tracking), five engineering items
  (identity-resolution, fractal gene, relevance scorer, async heal
  scheduler, provenance graph), two cross-cutting items (cross-field
  MERGE, modality table data-driven), four empirical questions
  (cliff experiment, HCQ cross-source rerun, full-system path-
  invariance, functional equivalence at scale), and a sequencing
  plan (clusters A–E).

## Unreleased — 2026-04-28

### Theory
- `JAYNES.md` added — names what BELLA inherits from Jaynes (evidence
  as log-odds, the three desiderata with empirical verification of
  3(a) via `shuffle_test.py`, priors as background information,
  multiple-hypotheses requirement, MLE brittleness), where it lands
  on the Jaynes/Pearl divide (Jaynes side, with the Ch. 3
  randomization quote as the philosophical anchor), where it extends
  Jaynes (R2–R6 are above the inference primitives), and where it
  specializes Jaynes (the voice-independence attenuation, with
  cross-source dependence as open work the HCQ trajectory exposes).

## Unreleased — 2026-04-26

### Theory
- New foundational section in SPEC.md: **Pattern, Translator, Expression**
  — articulates the kernel / gene / KB three-tier split as convergent
  on biology's heredity architecture (DNA / ribosome / protein) rather
  than designed by analogy. Cross-references to RE Conjecture 6
  (Appendix M §M.8).
- README and VISION updated with the same framing in audience-tuned form.
- Cross-refs added in SPEC §3 (Gene) and §6.5 (Soft Homoiconicity)
  pointing back to Foundation.

### Repository
- `replay/` added — historical-event validation harness with four cases
  (Wirecard, Theranos, Wakefield, Hydroxychloroquine), moved here from
  `re_news/herenews-app/experiments/bella_replay/`.
- This directory is now the canonical theory home. The empirical tool
  `bellamem` (npm) references it; its embedded `bella/` subfolder is
  retired in favor of the public repo.
- LICENSE (MIT), .gitignore added for first publication under the
  Recursive-Emergence GitHub org.

## v0.1 — 2026-04-07

First formal specification of the BELLA language.

### Language
- Core types: Proposition, Voice, Relation, Knowledge Base
- Two relations: → (supports), ⊥ (counters)
- Five actions: ⊨ confirm, ⊨∧δ amend, ⊢→ child, ⊢⊥ counter, ⊢ root
- Gene: compact KB rendering for LLM instrument context
- 8 invariants (uniqueness, monotonicity, tree structure, Jaynes consistency)

### Evidence Calculus (Jaynes)
- Likelihood ratio: lr = 1.0 + (lr_base - 1.0) × modality × grounding
- Mass accumulation: m = σ(Σ log lr)
- Marginal verification: same voice at 10%
- Assessment is (m, |V|) — no arbitrary categorical labels
- Disputes are structural (⊥ children), not labels

### Architecture
- Two-pass: structure (logic, Sonnet) + evidence (probability, standard tier)
- Separation principle: structure and evidence are independent concerns
- One LLM call per claim for structure, gene as context

### Validated
- Iran-US F-35 fighter jet incident: 93 claims → 44 propositions, 3 roots, $0.29
- Jeffrey Epstein death investigation: 75 claims → 47 propositions, 2 roots, $0.22

### Discovery Path
- E101: information redundancy instrument (too loose for within-topic)
- E102: four-way decision + emergence (downward force works, upward weak)
- E103: concurrent forces → Markov walk → gene meta-tree → formal proof language
- Key insight: formal notation + strong reasoning model (Sonnet) = correct structure
- Key insight: meta-tree gene as LLM context eliminates pairwise comparison

### Known Limitations
- Gene may not scale beyond ~100 propositions without compression
- 3 roots on F-35 vs expected 6 (program/geopolitical context under-separated)
- AMEND sometimes used where CHILD would be more precise
- Pass 1 requires strong reasoning model (Sonnet/Opus) — standard tier unreliable
- Not yet tested on mixed-topic streams (multiple unrelated events)

---

## Roadmap

### v0.2 (planned)
- Edge weights: → and ⊥ carry conditional likelihood ratios
- Gene compression: prune low-voice branches for scaling
- Mixed-topic streaming test
- Production integration with bella.perceive()

### v0.3 (planned)
- Emergence: local modularity inserts intermediate propositions (weak upward force)
- Multi-field lattice: L(1) connections between separate KB roots
- Concurrent pass 1 + pass 2 (progressive, not batch)

### v1.0 (target)
- Open-source release
- Python package with CLI
- Pluggable LLM backends
- Streaming API
- Full test suite with multiple domains

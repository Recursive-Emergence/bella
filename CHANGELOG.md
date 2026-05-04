# BELLA Changelog

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

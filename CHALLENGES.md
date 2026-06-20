# CHALLENGES.md — Open Work for SPEC v0.2 and Beyond

This document captures the open theoretical and engineering work that
has surfaced through the empirical exercises so far — the four-case
`replay/` validation, the `shuffle_test.py` order-invariance result,
the multi-voice news-event mapping (Krugman → Smolar → WeChat-MAGA →
Hersh → Thompson/Douthat → Gardner), and the conversations they
provoked.

It is the agenda. Each item is sized separately for theory work and
engineering work, with cross-references where the same underlying
issue surfaces in multiple challenges.


## Framing: Gene as Recipe at World-Model Scale

The most consequential reframe to land first, because it changes how
every other challenge is shaped:

**At small scale** (single case, ~100 propositions), BELLA's gene
captures enough that re-formation is approximately bit-equivalent.
`shuffle_test.py` confirmed this — Λ relative spread <1% across 30
random orderings on each of the four cases. At this scale the gene
*is* the canonical state.

**At world-model scale** (millions of propositions), this stops being
true, for the same reason it isn't true in biology. The KB is too
large to be the gene; the gene must be a *recipe*, and the KB is
reconstituted afresh each time. Two instances reading the same gene
plus the same evidence stream produce *equivalent-but-not-identical*
KBs — agreeing on highest-mass propositions and field structure,
disagreeing on intermediate phrasings and long-tail details.

This is the biological pattern. Identical twins agree on broad traits,
disagree on memories. Not a degradation of the small-scale property —
its grown-up form.

What this changes architecturally:

1. **The graph stored in PG / Neo4j becomes a cache, not the canonical
   state.** The gene is canonical. Re-running gene + evidence
   regenerates the cache.
2. **The gene encodes what doesn't regenerate.** Specific propositions
   about specific events not recoverable from re-reading the source
   stream → must be stored. Patterns that emerge from re-reading the
   stream → don't need to be stored.
3. **Compression ratio is the central design target.** DNA ~750MB →
   brain ~many TB, >1000:1. For BELLA at world-model scale, gene =
   millions of high-mass propositions + R1–R6 kernel + provenance
   graph; KB = billions of propositions + tens of billions of edges.
   Same order of magnitude.
4. **Identity (challenge T6 / E1 below) becomes load-bearing.** Two
   instances reconstituting from the same gene must produce the same
   canonical proposition handles even if rendering text differs.
5. **The surviving-part empirical test gets sharper.** Save the gene,
   wipe the KB, replay the evidence, compare. At small scale this
   tests bit-equivalence (passes). At world-model scale it tests
   *functional equivalence* — same verdicts on the same queries
   despite different intermediate state.

Everything below serves this reframe.


## Discovered: the operator-family architecture

The 2026-05-04 streaming-runner experiments surfaced a structural insight
that wasn't visible from the SPEC alone: **R3 EMERGE is not one rule but
a *type signature* for a family of rules instantiated at every
abstraction level**. The kernel's structural mutations all follow the
same recursive shape — compute pattern over items at one level, propose
mutation, recurse — and the same operator can apply to claims,
propositions, fields, themes, and worldviews.

The operator family:

| Operator | What it does | Dual / Sibling |
|---|---|---|
| **MERGE** | collapse same-belief items into one canonical | dual of SPLIT |
| **REROOT** | relabel a field whose anchor has drifted from its centroid | dual of MERGE |
| **SPLIT** | separate items that landed in one field but have distinct sub-centroids | dual of MERGE |
| **Ψ-anomaly** | flag 1v high-mass props whose topic is well-covered by other voices that did not corroborate | R4 self-referential |
| **Ψ-blindspot** *(open)* | inventory voice/method/entity coverage; surface dimensions absent | R4 self-referential |
| **Ψ-synthesis** *(open)* | propose multi-parent edges between cross-field props with high cosine | R4 self-referential, addresses T2 |

What makes this architecture-defining: **the same operator definition
applies at every level** — claims → propositions → fields → themes
→ worldviews. SPEC v0.2 should write `OPERATOR_N: items at level N → items at level N`
once with level as a parameter, rather than per-level.

The hand-built BELLA analyses people produce in conversation are doing
R4 implicitly (anomaly-flag, blindspot-detect, frame-expansion-detect,
cross-field synthesis). The streaming runner's per-claim operators do
R1 + R3 well but cannot reach the hand-built analysis's quality without
explicit R4 operators. Ψ-anomaly is the first R4 implementation;
Ψ-blindspot and Ψ-synthesis are spec'd but not built.

The "first-mover root anomaly" — a low-credibility early claim
becoming a field anchor that later high-credibility claims get amended
under — is what motivated REROOT. It surfaced empirically on the
Hormuz case during streaming runs and is non-deterministic across
seeds (different LLM choices on early claims produce or don't produce
the gravity-well pattern).


## Part I — Theory Challenges

### T1. Proposition vs Claim Distinction Collapses When |V|=1

**The issue.** SPEC theory: a proposition is an abstract belief; a
claim is a per-source utterance; multiple claims ⊨ confirm one
proposition. But when |V|=1, the proposition's φ text *is* the
founding claim's text. No abstraction is visible. The README example
has every node at |V|≤1, so the distinction is invisible (and reads
as unmotivated jargon).

**Where it surfaced.** Reader confusion on README's "What is BELLA?"
example: P3 "structural violations" and P4 "owner denies violations"
read as claims, not propositions.

**Current SPEC state.** §1.1 defines P with a φ string but doesn't
distinguish "abstract assertion" text from "founding claim" text.

**Theory work.** Specify that φ is the *generalized* assertion that
multiple distinct claims can resolve to. Make the distinction
operationally necessary by requiring that any proposition's φ be
expressible without quoting any single source (no proper-noun
attribution, no source-specific framing).

**Engineering work.** Renderer could surface generalized-φ vs
founding-claim text when they differ; this only matters once
identity-resolution (E1) is producing aliased renderings.

**Related.** T6 (Identity), E1 (Identity-resolution).


### T2. Gene Grammar Cannot Express Out-of-Tree Edges

**The issue.** Current gene grammar: indentation = "child of parent
above"; `⊥` prefix = "counters its parent." When ⊥ targets a *sibling*
(or any non-parent), the gene can't express it. Same problem when a
proposition has multiple parents.

**Where it surfaced.** The Krugman exercise hit this with "Iran's
economy is hurting" → "regime will not cave" with sibling ⊥ "Trump
claims collapse." The cleaner formulation needed cross-sibling
references the grammar can't carry.

**Current SPEC state.** §3 specifies single-parent indented rendering.
§7 acknowledges maturation moves tree → hypergraph but doesn't update
the grammar.

**Theory work.** Extend gene grammar with explicit ID references:
- `→<id>` for support edges to non-parent
- `⊥<id>` for counter edges to non-parent
- "aliased" rendering: a proposition appears once with full content
  and is referenced by ID elsewhere in the gene

**Engineering work.** Update gene renderer (`kernel.py:Gene.render`,
`grow.py:render_window`) to emit explicit edge references. Parsers
must accept the extended grammar.

**Related.** T3 (Hypergraph as primitive), T4 (Identity primitive).


### T3. Hypergraph Is Primitive, Tree Is the Projection

**The issue.** SPEC §7.4 treats the tree → lattice → hypergraph
progression as a *maturation phase*: beliefs become hypergraph as they
accumulate. The voice-stack exercise suggests this is backwards.
Beliefs *are* hypergraph from the start, and the tree is a projection
for fast LLM context. "Maturation" isn't structural growth — it's the
projection-loss becoming visible as more cross-field propositions
accumulate.

**Where it surfaced.** Three patterns in the multi-voice gene:
P88 ("no easy off-ramp") with three parents in three different roots;
P29 (predicted) ↔ P30 (reported) as cross-field same-proposition;
P98 ("swing voters feeling pinch") bridging economic and political
fields.

**Current SPEC state.** §7.4 treats hypergraph as eventual; R6
ENTANGLE only covers entity-as-hyperedge; §7.3 covers proposition
multi-parent only as "maturation" footnote.

**Theory work.** Restate R6 to cover both entity-as-hyperedge and
proposition-as-hyperedge as the same single rule (shared *nodes*
bridge fields, where node ∈ {entity, proposition}). Recast §7.4: the
underlying structure is hypergraph from the start; the gene-tree is
its projection for LLM context.

**Engineering work.** Storage already supports multi-parent via Neo4j;
the renderer does not (T2). PG ANN search needs to surface
cross-field same-proposition candidates, not just within-field.

**Related.** T2 (Grammar), T6 (Identity), X1 (Cross-field MERGE).


### T4. Voice Independence Generalizes to Cross-Source Dependence

**The issue.** R1's marginal-voice attenuation `lr' = 1 + (lr-1)×0.1`
handles only same-source repeats (voice X confirming P_n twice). It
does not handle *derivative* voices: source B's claim that's
evidentially derived from source A's claim. Counting B as fully
independent over-counts.

**Where it surfaced.** HCQ early-2020 spike to m=0.77. The four
"supports" entries in March 2020 were not independent: Trump
amplification was downstream of Raoult, FDA EUA was downstream of
Raoult + political pressure. Treating them as four independent voices
inflated the mass. (See JAYNES.md §4.)

**Current SPEC state.** §1.2 defines Voice and §2 specifies the
same-source attenuation. No mechanism for cross-source dependence.

**Theory work.** Each claim should carry lightweight provenance:
`derived_from: [source_id, …]`. R1 attenuates lr when derivation
ancestry overlaps. The attenuation factor is open — same 0.1 as
same-source, or weaker (0.3?) for arms-length derivation.

**Engineering work.** EW (extraction) needs to detect "this source
cites that one." The provenance graph (E5 below) is the data
structure. The R1 lr computation needs to walk derivation ancestry.

**Related.** E5 (Provenance subsystem), JAYNES.md §4.


### T5. Locality Is a Primitive

**The issue.** SPEC is silent on locality, but every scaled operation
requires it. Heal, reflect, ANN search, R5 cycle traversal — all need
explicit budgets. Currently locality is buried in implementation
constants (heal threshold H > 0.4, ANN top-k = some number).

**Where it surfaced.** The world-model scale conversation. Without
locality budgets, every operation is unbounded as the KB grows.

**Current SPEC state.** §0.2 mentions per-root heal but doesn't make
locality a rule-level concept.

**Theory work.** Lift locality to rule level: every operation declares
its scope (k-hop neighborhood, embedding-cosine cutoff, time window).
Specify defaults per operation. Prove (or at least argue) that scoped
operations preserve the desired properties (R1 mass validity,
desideratum 3(a), R5 convergence).

**Engineering work.** Each operation in `cli.py` and `grow.py` takes
explicit locality params. Async pipeline schedules operations by
locality scope and priority.

**Related.** T7 (R5 multiplicity), E4 (Async heal scheduler).


### T6. Identity Is a Primitive, Not Derived

**The issue.** Currently identity is derived: centroid sim > θ → merge.
At world-model scale, two propositions are "the same" not because they
cluster in embedding space but because they say the same thing in
different words from different sources, possibly in different fields.
Embedding similarity alone is insufficient.

**Where it surfaced.** The cross-field same-proposition pattern (P29
predicted ↔ P30 reported). The proposition/claim collapse (T1) only
matters once the same proposition has multiple renderings.

**Current SPEC state.** Identity is implicit (R3 emerge merges via
centroid); no canonical handle separate from rendering.

**Theory work.** Each proposition has a stable canonical handle (ID)
plus a current rendering text. Multiple renderings can resolve to one
handle through alias edges. Cross-field MERGE (X1) creates aliases
without losing provenance. Identity-resolution becomes a continuous
background process, not heal-time only.

**Engineering work.** E1 below.

**Related.** T1, T3, X1, E1.


### T7. R5 Convergence Under Path Multiplicity

**The issue.** R5's Banach contraction guarantees finite total mass
per cycle (single-cycle attenuation). But at world-model scale,
millions of cycles touch shared nodes through millions of paths.
Path-multiplicity could in principle let mass accumulate even though
each individual path attenuates.

**Where it surfaced.** The world-model scale conversation, prompted by
"endless traverse" concern. Two R5 cycles touching the same node
(K's "Trump rejects → strait closed → US damage" cycle and W's
counter-cycle "Iran can't export → storage saturates → regime weakens"
in the voice-stack exercise) is the small-scale instance of the same
problem.

**Current SPEC state.** §6.3 covers single-cycle R5 attenuation
(Λ_total = Λ₀ / (1 − α)). Does not address graph-wide multi-cycle
case.

**Theory work.** Either (a) prove that path-multiplicity attenuates
faster than per-path mass can accumulate (giving a stronger Banach
analog for the multi-cycle case), or (b) impose explicit recursion
depth caps with proof that mass beyond cap is negligible.

**Engineering work.** Depth-counted graph walks, explicit visited-set
tracking, no free recursion. Async pipeline absorbs deep traversals.
See E4.

**Related.** T5 (Locality), E4 (Recursion budget).


### T8. Multiple Hypotheses Must Be Enumerated (Jaynes Ch. 5)

**The issue.** BELLA's `m = σ(Λ)` for a single proposition is implicit
binary — P(target) vs P(¬target). Per Jaynes Ch. 5 (ESP, crow paradox),
P(H | D) is meaningless without explicit alternative hypotheses. The
dispute structure (⊥) is BELLA's mechanism for surfacing alternatives
but is per-edge, not per-proposition.

**Where it surfaced.** HCQ early-2020 spike — the implicit alternative
was "HCQ ineffective," but operative alternatives in March 2020 should
have included "early evidence is from non-independent sources," "small
uncontrolled trials systematically over-estimate effect," etc.
Surfacing these would have absorbed evidence the unified m
unwarrantedly attributed to "HCQ effective." (See JAYNES.md §1.4.)

**Current SPEC state.** No per-proposition alternative-hypothesis
tracking.

**Theory work.** For each proposition P, a structured list of
alternative hypotheses being implicitly compared against. Mass should
divide across the explicit hypothesis set, not collapse to a binary.

**Engineering work.** Schema extension for alternative-hypothesis
sets. Renderer must surface them. Open whether to populate via LLM
extraction (expensive but flexible) or via fixed templates per
domain (cheap but inflexible).

**Related.** JAYNES.md §1.4.


## Part II — Engineering Challenges

### E1. Identity-Resolution as Continuous Background Process

**The issue.** The realization of T6 in code. At small scale, R3's
heal-time merge by centroid sim is enough. At world-model scale,
identity-resolution must run continuously: every new write triggers
ANN top-k → small LLM call → "merge with handle X or create handle
Y." This is the entity-resolution / record-linkage problem from
databases, which is genuinely hard.

**Engineering work.** Pipeline: each write triggers an
identity-resolution job. At small scale, hand-tuned threshold over
(embedding sim, entity overlap, time delta, surface-form distance).
At larger scale, learned classifier over (candidate-pair) features.
Canonical handles stored separately from rendering text.

**Related.** T1, T6, X1.


### E2. Fractal Gene Rendering

**The issue.** A single flat gene doesn't scale. The gene must be
hierarchical — zoom-level-k gives the gene at coarseness k. R3's
recursive emergence already gives the structure (claims → beliefs →
fields → meta-fields → worldview); the rendering needs to match.

**Engineering work.** Pre-compute compressed gene per field at
multiple zoom levels. Update incrementally on write. LLM context
loader picks zoom level by available budget, with explicit "drill
down here" handles for the LLM to expand specific subtrees.

**Related.** Framing section, T3 (Hypergraph as primitive).


### E3. Multi-Signal Relevance Scorer

**The issue.** Fixed top-k by embedding similarity returns dozens of
near-matches at world-model scale, missing semantically relevant but
embedding-distant propositions. Need a learned or hand-tuned ranker
combining multiple signals.

**Engineering work.** Multi-signal scorer combining embedding sim,
entity overlap, mass-weighted recency, structural distance from
active field. Hand-tuned linear combination at small scale; learned
ranker over (claim, candidate) pairs at larger scale. *Gravity wells*
emerge naturally — high-mass propositions show up in more queries,
get more updates, mass grows.

**Related.** T5 (Locality), T6 (Identity).


### E4. Async Heal Scheduler with Recursion Budget

**The issue.** Heal can't be triggered on every claim at scale. Needs
queueing, prioritization, and explicit recursion budgets so deep
traversals don't block writes.

**Engineering work.** When a write touches a subtree, mark dirty.
Healer worker pops dirty subtrees by priority (entropy delta × subtree
size × mass-change magnitude). Each heal job runs with depth cap and
visited-set tracking. Reflect operates on a separate, slower queue
over the highest-entropy fields.

**Related.** T5 (Locality), T7 (R5 multiplicity).


### E5. Provenance Graph (Sibling to Belief Graph)

**The issue.** Voice-independence detection (T4) requires tracking
who-said-what-derives-from-whom. This is a separate graph from the
belief graph and needs independent storage and queries.

**Engineering work.** Schema: `Source` nodes, `Claim` nodes,
`DERIVED_FROM` edges between claims, `EXTRACTED_FROM` edges between
claims and source artifacts. Queries: ancestry walk for derivation
detection, source-credibility computation, cross-source-dependence
flagging.

**Related.** T4 (Voice independence).


## Part III — Cross-Cutting

### X1. Cross-Field MERGE as a Primitive Operation

**The issue.** SPEC §0.1 lists MERGE as one of seven within-field
operations. The voice-stack exercise made cross-field MERGE necessary
— the P29 (Krugman's prediction) ↔ P30 (Hersh's reporting) case is
two propositions in two different fields that should be recognized as
the same proposition viewed from different sides.

**Theory work.** Lift MERGE from within-field to handle-level
operation. Define semantics: aliases get joined at the handle, mass
accumulates jointly under R1 with cross-source dependence
(T4) properly applied, provenance preserved.

**Engineering work.** Update MERGE implementation to operate on
handles (E1), not on tree-structure. R3 emerge stays within-field;
cross-field MERGE is a separate operation.

**Related.** T3 (Hypergraph), T6 (Identity), E1.


### X2. Modality Table Becomes Data-Driven

**The issue.** `replay/bella_calc.py` has a hardcoded
`MODALITY_ATTN` map (~50 entries). Each new domain extends it.
Eventually this should be data-driven (learned from outcomes) or at
least domain-pluggable.

**Engineering work.** Externalize the modality table to config.
At larger scale, calibrate from outcomes — for cases with ground
truth, fit modality weights to maximize predictive accuracy. Treat
the calibration as another R5 cycle: modality weights affect lr
which affects m which can be checked against outcomes which updates
modality weights.

**Related.** Open work, lower priority than identity / locality.


## Open Empirical Questions

These are testable and should drive the next round of experiments:

1. **The cliff experiment.** Shrink the gene progressively (drop
   low-mass beliefs, drop entity reps, drop subtree structure) and
   find the cliff where re-formation breaks. The cliff defines what
   the surviving-part actually is for this substrate. Sized: small-
   to medium-effort, runnable on `replay/` infrastructure.

2. **Cross-source dependence on HCQ.** Mark FDA → Raoult and Trump →
   FDA as derivative in the HCQ claim set. Re-run with the proposed
   T4 attenuation. Predicted result: peak m drops from 0.77 to ~0.55.
   If predicted, T4 is the right primitive extension.

3. **Path-invariance for the full system.** `shuffle_test.py` verified
   path-invariance for the mechanical R1 + entity-rep calc. The full
   `grow.py` pipeline (LLM placement, R3 emergence, heal/reflect)
   needs separate verification — does desideratum 3(a) hold for the
   full kernel, or does LLM stochasticity introduce real variance?

4. **Functional equivalence at scale.** Run BELLA twice on the same
   evidence stream, save the gene from each, replay against fresh
   instances, compare. At small scale: bit-equivalence expected. At
   medium scale: functional equivalence (same verdicts on same
   queries) expected. Identifying where the transition happens is the
   world-model surviving-part question made empirical.


## Notes on Sequencing

**Cluster A (foundational, do first):**
T1, T2, T3 — the proposition / grammar / hypergraph reframe. None
require code changes beyond the renderer and parser; theory work is
mostly explication of what's already implicit.

**Cluster B (priority, do next):**
T4, T6, X1, E1, E5 — identity and voice-dependence. These together
fix the HCQ-style failures and make cross-field reasoning sound.

**Cluster C (scale, do as needed):**
T5, T7, E2, E3, E4 — the world-model scaling work. Required only
when actually scaling beyond small-case demos.

**Cluster D (open):**
T8 — alternative-hypothesis tracking. Theoretically cleanest, but the
clearest path to implementation is unclear.

**Cluster E (lower priority):**
X2 — modality data-driven. Useful eventually; not blocking.

The framing section's reframe (gene as recipe, KB as cache) is
load-bearing for all of this — adopt it explicitly in SPEC v0.2 and
the rest follows naturally.

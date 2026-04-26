# BELLA — Bayesian Epistemic Logical Lattice for Accumulation

A formal calculus for constructing belief structures from evidence
streams. Six rules, scale-free, self-referential.


## Foundation: Pattern, Translator, Expression

BELLA's architecture separates three things that are usually fused:

- **The kernel** — the rules that read pattern and produce belief
  structure. Fixed, small, external. R1–R6 are the kernel.
- **The gene** — the compressed transmissible form of what the system
  knows. Text. Grows monotonically with each claim.
- **The knowledge base (KB)** — the expressed structure that does the
  work: accumulates evidence, exposes disputes, answers queries.

The kernel reads the gene to reconstitute a functionally equivalent KB.
The KB does the work; the gene transmits; the kernel translates. The
three can be replaced *separately* — that is the point of the split.

### Why the separation is forced

A system whose accumulated content cannot outlive its current
computational state has no way to amortize the cost of forming that
content across future uses. Each instance must rediscover everything
from scratch.

The three-tier split makes formed content propagate. The gene encodes
what was learned; any instance with the same kernel can read the gene
and operate equivalently to the original — not bit-identical, but
functionally indistinguishable for the queries the gene was built to
support.

This is why the kernel must be fixed (a translator must be stable to
reliably reconstitute pattern), why the gene is text (the
cognitive-layer's high-fidelity transmission medium), and why the KB
is allowed to drift across instances (variation in the expressed form
is the substrate selection acts on).

### Convergence on a known pattern

This three-tier split is the same operation biology uses for heredity:
DNA / ribosome / protein. Compressed pattern that templates its own
propagation, with a fixed translator producing function from pattern.

BELLA was not designed to imitate biology. It was designed for
engineering reasons specific to belief accumulation under streaming
evidence — Bayesian (Jaynes) accumulation, graph-theoretic structure,
embedding-based retrieval. It turns out to instantiate the same
architecture biology arrived at, which suggests the architecture is
*forced* by the problem rather than chosen for elegance.

The Recursive Emergence framework predicts this: any sufficiently
complex system whose accumulated content needs to outlive its current
substrate must converge on a pattern / translator / expression split,
or fail to scale (Conjecture 6, RE Appendix M §M.8). BELLA is one
instance — engineered, in software, at the cognitive layer. The
substrate is different (text rather than nucleotides), the kernel is
different (R1–R6 rather than ribosomes), but the structural role is
identical.

The remainder of this specification is a detailed account of one
specific kernel (R1–R6, §0), the operations it supports (§0.1), the
structural form of the gene (§3), and the dynamics of the KB it
produces (§§4–8).


## 0. The Six Rules

Everything in BELLA derives from six rules. The rules are
scale-free: they apply identically to a single claim, a field
of thousands, or the system observing itself.

```
R1  ACCUMULATE   m(B) = σ(Σ log lr_i)
    Evidence accumulates via Jaynes log-likelihood ratios.
    Mass m is always a valid posterior. Same voice attenuated
    by marginal verification: lr' = 1 + (lr - 1) × 0.1

R2  STRUCTURE    ∀ operations O: H(tree') ≤ H(tree)
    Every operation should reduce or preserve entropy.
    H(B) = w(rel) × (1 - sim(B, parent(B))) where
      w(IMPLIES) = 1.0  (child should follow from parent)
      w(DISPUTES) = 0.5  (counter-arguments expected to diverge)
    H(tree) = mean H(B) over all edges in a SUBTREE.
    Measured and healed per-root, never globally.
    (The Entropy Law — §5.1)

R3  EMERGE       sim(centroid_i, centroid_j) > θ → merge
    When two root subtree centroids converge (sim > 0.55),
    they belong to the same field. The smaller merges under
    the larger. The centroid IS the identity — no labeling.
    Markov state transition: accumulation → convergence → merge.
    Recursive: claims→beliefs→fields→meta-fields, same θ.

R4  SELF-REFER   Ψ(KB) → KB'
    The same calculus applied to KB's own state.
    Beliefs about beliefs. Entropy of entropy.
    Each level attenuated: Λ(n) = Λ(n-1) × α, α < 1.
    Infinite regress converges: Σ αⁿ = 1/(1-α).
    (§6 — Self-Reflection)

R5  CONVERGE     cycles → Σ lr × α^depth → finite
    Any feedback loop in the system attenuates per traversal.
    Primary instance: entity ↔ belief cycle.
      rep(E) → lr(claim) → Λ(B) → rep(E) → ...
    Also: causal cycles (sanctions → poverty → radicalization),
    self-reference (Ψ on Ψ), entity across fields.
    Each traversal contributes less. Sum converges (Banach).
    At any moment, m is valid.

R6  ENTANGLE     shared entities bridge fields
    Cross-field information flows through shared entities,
    not explicit cross-field edges. Entity E in Field A and
    Field B: evidence in A updates rep(E), which modulates
    lr in B. The entity IS the hyperedge.
    Explicit multi-parent edges (|parents(B)| > 1) may also
    form during maturation, but the primary entanglement
    mechanism is entity co-involvement.
    (§8 — Entities as Beliefs)
```

### 0.1 Operations (Actions)

Seven operations, expressed as JSON. All composable, all
applicable at any level. No privileged root — a field's
identity is its emergent centroid (R3), not a designated node.

```
{"op":"CONFIRM", "id": B}           accumulate evidence (R1)
{"op":"AMEND",   "id": B, "desc":…} refine description + accumulate
{"op":"ADD",     "parent": B, …}    new belief supporting B (R2: H↓)
{"op":"DENY",    "parent": B, …}    new belief countering B (R2: H↓)
{"op":"CAUSE",   "effect": B, …}    new belief causing B (R2: H↓)
{"op":"MERGE",   "keep": B1, …}     two beliefs are one (R2: H↓)
{"op":"MOVE",    "node": B, …}      reparent for coherence (R2: H↓)
```

Root elevation is MOVE (reparent under a new broader belief)
or AMEND (update the topmost belief's description). The root
is whatever R3 recognizes — the belief whose subtree centroid
represents the field's identity. It emerges, not designated.

### 0.2 Four Concurrent Processes

The calculus runs as four processes on one shared hypergraph:

```
SENSE    per-claim    Sonnet    R1, R2     land → place → accumulate
BOND     per-signal   mechanical R1        votes/stakes → accumulate
HEAL     on entropy   Opus      R2         per-root restructure (local only)
REFLECT  rare         Opus      R4         Ψ(KB) → self-model
```

Emerge (R3) runs after every sense pass — mechanical, no LLM.
Heal (R2) is per-root local: never sees the whole tree, never
creates inter-field connections (that's reflect's job).

Entropy is the nervous system: sense creates structure,
entropy measures coherence per subtree, heal fires when
a subtree's H exceeds threshold, reflect observes patterns
across fields.

### 0.3 The Pipe

```
EW (extract)  →  page → claim tree with typed relations
                  (causes, counters, evidence, elaborates,
                   mechanism, assessment)

SENSE (land)  →  two-level PG ANN search:
                  1. root subtree centroids → which field?
                  2. individual beliefs within field → where?
                  cohort centroid (page mean) pre-selects field.

SENSE (place) →  claim tree drag: parent landed → child follows.
                  EW relation drives operation mechanically:
                    causes→CAUSE  counters→DENY  evidence→CONFIRM
                    elaborates→AMEND  mechanism→ADD  assessment→ADD
                  LLM only for root claims or when no tree_rel.
                  90%+ claims placed without LLM when EW is good.

SENSE (emerge)→  after all claims: check root centroid convergence.
                  sim(root_i, root_j) > 0.55 → merge (R3).
                  Mechanical, no LLM. Markov state transition.

HEAL (cohere) →  per-root local: Opus sees ONE subtree only.
                  MERGE duplicates, MOVE misplaced, CAUSE chains.
                  Never creates inter-field connections.
                  Triggered when subtree H > 0.4.

REFLECT (Ψ)  →  observe patterns ACROSS fields (Opus).
                  "these fields are converging" "causal chain spans"
                  Creates cross-field edges (R6). Rare.
```

### 0.4 Storage Architecture

```
Neo4j    = graph truth (Belief nodes, IMPLIES/DISPUTES edges,
           CONFIRMS evidence, INVOLVES entities)
PG       = materialized embedding index (pgvector ANN)
           core.belief_embeddings: embedding + subtree_emb
           ivfflat indexes for O(log n) search
```

Every write dual-writes: Neo4j (structure) + PG (embeddings).
land() reads PG only. heal/reflect read Neo4j (need edges).


## 1. Core Types

### 1.1 Proposition

The atomic unit of belief. Not a claim — an abstract assertion.

```
P := ⟨n, φ, m, V, E, τ⟩

  n : ℕ                 -- unique identifier
  φ : String            -- assertion as subject-verb-object
  m : [0,1]             -- posterior mass: m = σ(Λ), Λ = Σ log lr
  V : Set⟨Voice⟩        -- independent confirming sources
  E : Set⟨Entity⟩       -- entities involved (who, what, where)
  τ : TimeRange         -- temporal anchor (earliest, latest)
```

A proposition carries not just what is believed, but WHO is
involved and WHEN it happened. These ground the belief in the
world and enable causal and temporal reasoning.

### 1.2 Voice

An independent source of evidence.

```
Voice := ⟨source, credibility⟩
```

Independence matters: same source confirming twice contributes
marginally, not doubly.
```
lr_marginal = 1.0 + (lr - 1.0) × 0.1
```

### 1.3 Relation

Typed directed edges between propositions.

```
→   : supports    P_j → P_i     "P_j is evidence for P_i"
→c  : causes      P_j →c P_i    "P_j caused or triggered P_i"
⊥   : counters    P_j ⊥ P_i     "P_j denies or disputes P_i"
```

Formal semantics (Jaynes):
```
P_j → P_i   ⟺  P(P_i | P_j) > P(P_i)         supports
P_j →c P_i  ⟺  P(P_i | P_j) > P(P_i) ∧ temporal(P_j < P_i)   causes
P_j ⊥ P_i   ⟺  P(P_i | P_j) < P(P_i)         counters
```

→c (causal) is a strengthened →: not just correlation but temporal
precedence and mechanistic connection. "Trump threatens Iran" →c
"Democrats demand removal" — the threat preceded and motivated the
demand. Causation carries higher epistemic weight than mere support.

⊥ is reserved for EXPLICIT denial — one proposition asserting
the negation of another. Unrelated propositions have no edge.

### 1.4 Knowledge Base

```
KB := ⟨Π, R, ρ⟩

  Π : Map⟨ℕ, P⟩          -- propositions
  R : Set⟨(ℕ, ℕ, Rel)⟩   -- edges (child, parent, →|⊥)
  ρ : List⟨ℕ⟩             -- roots (no parent)
```

Construction phase: KB is a forest (each P has at most one parent).
Maturation phase: KB relaxes into a hypergraph as cross-references,
self-references, and multi-parent edges emerge (see §7).


## 2. Evidence Calculus (Jaynes)

### 2.1 Likelihood Ratio

Each claim c provides evidence with strength lr:

```
lr(c) = 1.0 + (lr_base(c) - 1.0) × α(c)

  lr_base : source credibility
  α       : attenuation = modality(c) × grounding(c)

  modality:
    observation     = 1.0
    reported_speech = 0.7
    allegation      = 0.5
    opinion         = 0.2

  grounding:
    g = 0.3 + 0.35 × [has_time] + 0.35 × min(|entities|, 3)/3
```

lr > 1: evidence shifts belief upward.
lr = 1: neutral (no information).
lr < 1: only via counter stance (inverted).

### 2.2 Mass Accumulation

```
Λ(P) = Σ { log lr(cᵢ) | cᵢ ⊨ P, stance ∈ {CONFIRMS, SUPPORTS} }
      + Σ { log(1/lr(cⱼ)) | cⱼ ⊨ P, stance = COUNTERS }

m(P) = σ(Λ(P))     where σ(x) = 1/(1 + e⁻ˣ)
```

Prior: Λ₀ = 0, m₀ = 0.5 (maximum ignorance).

### 2.3 Two Measures of Confidence

```
m    : posterior mass (Jaynes)     -- evidence quality, weighted
|V|  : effective voice count       -- evidence independence
```

Neither alone suffices:
- High m, low |V|: one strong source (possibly wrong)
- Low m, high |V|: many weak sources (possibly correlated)
- High m, high |V|: genuine confirmation

### 2.4 Assessment

The assessment IS the pair (m, |V|). No categorical labels —
the probability speaks for itself.

```
(m=0.91, 10v)  near-certain, widely confirmed
(m=0.59, 2v)   above neutral, emerging
(m=0.55, 1v)   barely above prior, single source
(m=0.50, 0v)   maximum ignorance, structural only
(m=0.35, 3v)   evidence trending against
```

A proposition with ⊥ children is inherently disputed —
this is structural, visible in the tree, not a label.


## 3. Gene (Compact Representation)

The gene G(KB) is a compact rendering of KB. It is the system's
self-image at any moment — what it knows, compressed.

Architecturally, the gene is the transmissible compressed pattern
that the kernel reads to reconstitute a functionally equivalent KB
(see Foundation, above).

```
G(KB) → String

  P<n>: "φ" [|V|v, τ, E]
    P<n>: "φ" [|V|v, τ, E]
    →c P<n>: "φ" [|V|v, τ, E]
    ⊥ P<n>: "φ" [|V|v]
```

Properties:
- One line per proposition
- Indentation encodes depth (relative, not absolute)
- Relation prefix: →c for causal, ⊥ for counter, none for supports
- Voice count shown when |V| > 1
- τ: short date (e.g. "Apr7") when available
- E: top 1-2 entity names (e.g. "Trump+Iran")
- φ as subject-verb-object (factual claim, not label)
- Grows monotonically with each claim

The gene serves two purposes:
1. **Instrument context**: the LLM reads the gene to place new claims
2. **Self-representation**: the gene IS what the system knows about itself


## 4. Structural Operations

### 4.1 Actions

When claim c arrives, the instrument evaluates c against G(KB)
and returns exactly ONE action:

```
⊨ P<n>                        CONFIRM   c entails existing P<n>
⊨ P<n> ∧ δ"detail"             AMEND     c confirms P<n> + adds nuance
⊢ P<next> → P<n> "φ"           CHILD     new proposition supporting P<n>
⊢ P<next> →c P<n> "φ"          CAUSE     new proposition that caused/triggered P<n>
⊢ P<next> ⊥ P<n> "φ"           COUNTER   new proposition denying P<n>
⊢ P<next> "φ"                   ROOT      new unrelated topic
```

Symbols:
- ⊨ (entails): claim matches existing proposition
- ⊢ (derives): claim creates new proposition
- → (supports): evidential support
- →c (causes): causal/temporal precedence
- ⊥ (contradicts): explicit denial
- ∧ δ (and-detail): amendment

### 4.2 Action Semantics

```
CONFIRM  ⊨ P<n>:
  V(P_n) ← V(P_n) ∪ {voice(c)}
  Λ(P_n) ← Λ(P_n) + log lr(c)

AMEND    ⊨ P<n> ∧ δ:
  V(P_n) ← V(P_n) ∪ {voice(c)}
  Λ(P_n) ← Λ(P_n) + log lr(c)
  φ(P_n) enriched with δ

CHILD    ⊢ P<k> → P<n> "φ":
  Π ← Π ∪ {P_k}
  R ← R ∪ {(k, n, →)}
  V(P_k) ← {voice(c)},  Λ(P_k) ← log lr(c)

COUNTER  ⊢ P<k> ⊥ P<n> "φ":
  Π ← Π ∪ {P_k}
  R ← R ∪ {(k, n, ⊥)}
  V(P_k) ← {voice(c)},  Λ(P_k) ← log lr(c)
  Λ(P_n) ← Λ(P_n) + log(1/lr(c))

ROOT     ⊢ P<k> "φ":
  Π ← Π ∪ {P_k},  ρ ← ρ ∪ {k}
  V(P_k) ← {voice(c)},  Λ(P_k) ← log lr(c)
```

### 4.3 Instrument

```
instrument(c, KB) → Action

  input:  G(KB) + text(c)
  output: exactly one action line
  model:  strong reasoning tier
```

The gene provides full structural context. One call per claim.


## 5. Invariants

```
I1  ∀ i,j: i ≠ j → φ(Pᵢ) ≢ φ(Pⱼ)         no duplicate propositions
I2  ⊥ only for explicit denial               counters are genuine disputes
I3  construction: |parents(P)| ≤ 1           tree during construction
I4  m(P) = σ(Λ(P))                           Jaynes posterior consistent
I5  V counts independent sources only         marginal dedup enforced
I6  |actions(c)| = 1                          one action per claim
I7  Π grows monotonically                     propositions only added
I8  G(KB) current after each action           gene always reflects KB
```

I3 relaxes in maturation: cross-references create multi-parent edges.


### 5.1 The Entropy Law (Structural Coherence)

The correct arrangement of a belief tree is the one that **minimizes surprise**
across all parent-child pairs:

> Each child should follow naturally from its parent.
> If a child is surprising under its parent, it is in the wrong place.
> If the root is too narrow for its children, it must be broadened.

This single principle subsumes:
- **Causal discovery**: A causes B ⟹ B is unsurprising given A. The tree
  discovers causal structure from the surprise metric.
- **Hierarchical correctness**: A mechanism does not predict events; events
  predict reactions. The surprise direction determines nesting.
- **Root emergence (φ)**: When all children are surprising under the root,
  the root is too narrow — it must elevate to a broader abstraction.

Validated 2026-04-08: a single LLM call with only this principle (no domain
hints, no causal instructions) correctly restructured a 38-node broken tree
into the epistemically correct structure — discovering causal chains, separating
mechanisms from events, and elevating the root.

### 5.2 Entropy Metric Refinement

Edge surprise must account for relationship type:

```
H(B) = w(rel) × (1 - cos_sim(B.embedding, parent(B).embedding))

  w(IMPLIES)  = 1.0   supporting child should be topically close
  w(DISPUTES) = 0.5   counter-arguments expected to diverge
```

Validated 2026-04-08: without DISPUTES weighting, a tree with correct
epistemic structure (proper counter-arguments) shows artificially high H.
DISPUTES edges ARE surprise — that's their function.

### 5.3 Heal Must Be Local

Heal operates per-root, never globally. When Opus sees the whole tree:
- It makes inter-field CAUSE connections (correct but reflect's job)
- Root entropy collapses (roots merge) while edge entropy degrades
- Structure oscillates instead of converging

Per-root heal: Opus sees one subtree → restructures internally →
edge entropy improves → root entropy preserved. Cross-field connections
are reflect's domain (R4), not heal's.

Validated 2026-04-08: two global heal passes caused edge H to rise
(0.563 → 0.570) while root H collapsed (0.491 → 0.000). Per-root
heal stabilized root H while making correct local moves.


## 6. Self-Reflection

### 6.1 The Reflection Operator

BELLA is self-encoding: the same language that builds KB(world)
can build KB(self) — beliefs about beliefs.

```
Ψ : KB → KB

  Ψ(KB_world) → KB_self      -- beliefs about world model
  Ψ(KB_self)  → KB_meta      -- beliefs about self-model
  Ψ(KB_meta)  → KB_meta²     -- beliefs about meta-model
  ...
```

Each application of Ψ produces a new KB using the SAME five
operations. The input "claims" at level n are observations
about KB at level n-1.

### 6.2 Self-Referential Propositions

```
S := P where φ references KB

  S1: "world model has 44 propositions"        (structural)
  S2: "fighter jet incident well-supported"     (confidence)
  S3: "source bias toward Western media"        (limitation)
  S4: "death investigation has evidence gaps"   (gap)
```

These are propositions in KB(self). They accumulate evidence and
mass exactly like world propositions. They can support and counter
each other:

```
S3: "Western media bias present" →S2
  ⊥ S5: "Iranian sources also confirm"
```

### 6.3 Attenuation and Convergence

Each level of reflection is attenuated:

```
Λ_level(n) = Λ_level(n-1) × α      where α < 1

  level 0:  direct evidence           full strength
  level 1:  reflection                 α
  level 2:  reflection on reflection   α²
  level n:  ...                        αⁿ → 0
```

The infinite regress converges:

```
Λ_total = Σ Λ₀ × αⁿ = Λ₀ / (1 - α)    finite
```

At any depth, m is a valid posterior. Deeper reflection refines
but never diverges. The system can be sampled at any moment
and return a coherent answer.

### 6.4 The Gene as Self-Image

The gene G(KB) is not merely a utility for the instrument. It is
the system's compressed self-representation — what it knows, in
the most compact form expressible in its own language.

When the system reflects (Ψ), it reads its own gene. The gene
is both:
- The **input** to reflection (what does the system observe about itself?)
- The **output** of construction (what has the system built so far?)

This dual role — representation and self-observation — is the
mechanism of self-reference in BELLA.

### 6.5 Soft Homoiconicity: The Gene as Constitution

The gene contains beliefs about how the system SHOULD operate:

```
B1: "I construct beliefs from evidence"
B2: "five operations: ⊨ ⊨∧δ ⊢→ ⊢⊥ ⊢" →B1
B6: "⊥ reserved for genuine dispute" →B1
```

These are not executable code. They are **principles** — beliefs
about operations that the LLM interprets when processing claims.
Like a constitution interpreted by judges, not a program executed
by a CPU.

The architecture has three layers:

```
Hard layer:   kernel (stable, small, never changes)
              — read gene, call LLM, parse action, update gene

Soft layer:   gene (evolves, shapes LLM behavior)
              — B-nodes: principles about how to operate
              — P-nodes: beliefs about the world

Substrate:    LLM (interprets gene, produces actions)
              — reads the constitution, applies it to each claim
```

The kernel is minimal and stable — it just says "read your gene,
process this claim." Everything else — what counts as ⊥, when to
confirm vs child, how to assess evidence — lives in the gene as
principles the LLM interprets.

This is **soft homoiconicity**: the gene describes the system in
the system's own language, and that description influences behavior,
but the kernel remains external and stable.

This is the same kernel/gene/expression split introduced in the
Foundation section, viewed at finer resolution: the kernel (here,
the harness loop plus the LLM as substrate) reads the gene (now
containing both world beliefs and self-principles) and produces the
KB. What changes at this resolution is only that the gene's content
includes its own interpretive principles, not that the architecture
differs.

When self-reflection discovers a failure, the constitution amends:

```
⊢ B19 →B6 "⊥ requires explicit negation language"
```

B19 doesn't modify code. It adds a belief that refines a principle.
Future LLM calls read the amended gene and behave differently.
Self-modification through belief change, not code change.

This mirrors human self-modeling: "I should be more careful about
X" is a belief that shapes behavior without being mechanically
executed. The brain's hardware (kernel) doesn't change — the
self-model (gene) evolves, and the evolved model influences
future computation.

### 6.6 Concurrent Self and World

A live system runs multiple concurrent processes:

```
KB_field₁:  own gene, growing from claims       (fast)
KB_field₂:  own gene, growing from claims       (fast)
...
KB_bella:   own gene, growing from observation   (slow)
```

Each field maintains its own compact gene. Bella oversees all
fields and herself. Her "claims" are observations about the
fields' genes and her own gene.

Cross-references live in KB_bella — she points to P_n in field₁
and Q_n in field₂, never copies. The system scales horizontally:
new fields get their own KB. No single gene overflows.


## 7. Maturation: Tree to Hypergraph

### 7.1 Entanglement Through Entities (R6)

During construction, I3 constrains KB to a tree (one parent per
belief). This makes progressive construction tractable.

Cross-field information does not require relaxing I3. It flows
through shared entities (§8.6): entities that INVOLVE beliefs
in multiple fields carry reputation across those fields. The
entity IS the hyperedge — no explicit multi-parent edges needed
for the primary entanglement mechanism.

Three information channels between fields:

**Entity bridge**: Shared entity E in Field A and Field B.
Evidence in A updates rep(E), which modulates lr in B.

```
Field(military): "US strikes Iran"   INVOLVES [Trump]
Field(politics): "25th Amendment"    INVOLVES [Trump]
  → rep(Trump) accumulated from BOTH → modulates BOTH
```

**Self-reference**: KB(self) points into KB(world). (R4)

```
S_k: "confidence in B_i is high" references B_i directly
  The edge IS the self-awareness
```

**Meta-reference**: Beliefs about relationships between fields.

```
M_1: "military escalation drives political crisis"
  emerges from observing entity bridges (reflect)
```

### 7.2 Circular Causation (R5: Converge)

R5 governs all feedback loops in the system. Three instances:

**Entity ↔ Belief** (primary, always active):
```
rep(E) → lr(claim) → Λ(B) → rep(E)
  attenuation: σ(E) = 1/√n < 1
  convergence: Banach fixed-point
```
See §8 for full treatment. This is the first R5 cycle that
activates — as soon as entities participate in multiple beliefs.

**Causal cycles** (activates in mature trees):
```
Sanctions → poverty → radicalization → conflict → sanctions
  traversal n: lr × αⁿ → 0
  total: lr × α/(1-α)    finite
```

**Self-reference** (R4 + R5):
```
Ψ(KB) → KB_self → Ψ(KB_self) → KB_meta → ...
  level n: Λ × αⁿ → 0
  total: Λ / (1-α)    finite
```

All three are the same mechanism: a cycle where each traversal
contributes less. R5 guarantees convergence in all cases.
At any moment, m is a valid posterior.

### 7.3 Multi-Membership and Weighted Edges

When B participates in multiple parents, mass propagation
is weighted:

```
B has parents {P₁, P₂, P₃} with weights {w₁, w₂, w₃}
  Σ wᵢ = 1 (normalized)

  Δm(Pᵢ) = wᵢ × log(lr)    evidence distributed by weight
```

Weight reflects how strongly B participates in each context.
A belief about "Trump" participates strongly in "political
crisis" (w=0.8) and weakly in "military operations" (w=0.2).

The weights are not assigned — they emerge from structure.
Entity σ (specificity) provides the prior: high fan-out
entities carry less weight per edge.

### 7.4 From Tree to Lattice to Hypergraph

```
Construction     →  tree (R1, R2, fast, tractable)
Maturation       →  lattice (R6 activates, cross-references)
Full integration →  hypergraph (R4, R5 activate, cycles, self-ref)
```

The hypergraph maps to the organism:
- **Ω** = the full multiply-connected KB (structure)
- **ψ** = individual belief states m, |V| (local)
- **Φ** = emergent coherence from R3 (global)

### 7.5 Emergence (R3: Centroid Convergence)

Emergence is a Markov state transition: when two root subtree
centroids converge past θ, they belong to the same field.

```
∀ root_i, root_j:
  sim(root_i.subtree_centroid, root_j.subtree_centroid) > θ:
    smaller → IMPLIES → larger
    larger.subtree_centroid ← weighted_mean(both)
```

θ = 0.55. Mechanical (no LLM). Runs after every sense pass.

The subtree centroid is a running average — updated on every
_write_edge as new beliefs join. It tracks the field's
aboutness as evidence accumulates. Identity is not a label
but a point in embedding space that drifts with evidence.

Recursive: the same mechanism applies at every level.
claims → beliefs → fields → meta-fields → worldview.
Same θ, same centroid convergence, same merge operation.

Fields can nest: a field within a field is a sub-field.
A meta-field emerges when field centroids converge.


## 8. Entities as Circular Causation (R5 Instance)

Entities are the primary instance of R5 in the system. The
entity ↔ belief feedback loop is circular causation:

```
rep(E) → lr(claim) → Λ(B) → rep(E) → ...
```

This is not a separate mechanism. It is R1 (accumulation) applied
to entities, creating a cycle that R5 (convergence) resolves.

### 8.1 Entity Reputation (R1 Applied)

```
E := ⟨id, name, rep, Λ_E, n⟩

  rep   = σ(Λ_E)                          R1: same Jaynes posterior
  Λ_E   = Σ σ(E) × w(role_i) × Λ(B_i)   for B_i INVOLVES E
  σ(E)  = 1 / √n(E)                       specificity: fan-out attenuation
  n     = |{B : B INVOLVES E}|
```

Three roles, one calculus:

```
source    w = 1.0    "CNN reported X"     → X reflects on CNN
subject   w = 0.5    "Trump threatened Y" → Y reflects on Trump
mentioned w = 0.1    "at the Strait"      → weak association
```

σ ensures high fan-out entities change slowly (Trump, n=50, σ=0.14)
while low fan-out entities are defined by their few appearances
(Dr. Baden, n=1, σ=1.0). Same σ principle as FW binding.

### 8.2 The R5 Cycle

```
claim c from source E arrives
  lr(c) = lr_base(c) × (0.5 + rep(E))    rep modulates lr
  belief B accumulates c                   R1
  B.mass changes
  Λ_E recalculated from B.mass            R1 on entity
  future claims from E carry new rep(E)    cycle continues
```

This IS circular causation: entity → belief → entity.
R5 guarantees convergence:
- σ is bounded [0,1]
- g(rep) = 0.5 + rep is sublinear
- Each traversal's influence < 1 (contraction)
- Banach fixed-point theorem → unique fixed point

At the fixed point: entity reputation and belief masses are
mutually consistent. No iteration needed at runtime — the
system converges incrementally with each claim.

### 8.3 Entities as Entanglement (R6 Consequence)

R6 (entangle) is not a graph operation. It is a consequence
of R5 operating through shared entities.

```
Field(military): "US strikes Iran"     INVOLVES [Trump]
Field(politics): "25th Amendment"      INVOLVES [Trump]
```

Trump's reputation accumulates from BOTH fields. A new claim
about Trump lands in one field but updates rep(Trump) globally,
which modulates lr in ALL fields. The entity IS the hyperedge.

Cross-field information flow requires no explicit edges —
it emerges from the R5 cycle operating across INVOLVES.

### 8.4 Levels

```
Level 0:  Claims      → raw assertions
Level 1:  Beliefs     → R1 accumulation, R2 structure
Level 2:  Entities    → R1 + R5 (circular: belief ↔ entity)
Level 3:  Fields      → R3 emergence (centroid convergence)
Level 4:  Self-model  → R4 (Ψ: same calculus on own state)
```

Each level boundary is an R5 cycle. Each uses the same six rules.
No new mechanisms at any level — only the same calculus applied
to the output of the level below.


## 9. Walkthrough Example

A building collapses. Claims arrive from multiple sources.

### Step 1: First claim

```
c₁: "A five-story building collapsed in central district this morning"
    source: local_news, modality: observation

KB: (empty)
→ ⊢ P1 "building collapsed in central district"

Gene:
  P1: "building collapsed in central district"
```

### Step 2: Supporting detail

```
c₂: "Rescue teams have pulled three survivors from the rubble"
    source: fire_dept, modality: observation

→ ⊢ P2 →P1 "survivors rescued from rubble"

Gene:
  P1: "building collapsed in central district"
    P2: "survivors rescued from rubble"
```

### Step 3: Confirmation

```
c₃: "The building came down around 8am, trapping dozens"
    source: witness, modality: observation

→ ⊨ P1              -- same fact, different wording

Gene:
  P1: "building collapsed in central district" [2v]
    P2: "survivors rescued from rubble"
```

### Step 4: Amendment

```
c₄: "Officials confirmed the collapse, saying it was a residential building"
    source: city_official, modality: reported_speech

→ ⊨ P1 ∧ δ"residential"

Gene:
  P1: "building collapsed; residential" [3v]
    P2: "survivors rescued from rubble"
```

### Step 5: Dispute emerges

```
c₅: "The building owner denied any structural violations"
    source: building_owner, modality: reported_speech

→ ⊢ P3 →P1 "structural violations alleged"
  ⊢ P4 ⊥P3 "owner denies violations"

Gene:
  P1: "building collapsed; residential" [3v]
    P2: "survivors rescued from rubble"
    P3: "structural violations alleged"
      ⊥ P4: "owner denies violations"
```

The denial reveals TWO propositions — the denied thing and the
denial itself. Disputes enter the tree structurally.

### Step 6: Unrelated topic

```
c₆: "City council approved new building safety regulations last month"
    source: city_records, modality: observation

→ ⊢ P5 "new safety regulations approved"

Gene:
  P1: "building collapsed; residential" [3v]
    P2: "survivors rescued from rubble"
    P3: "structural violations alleged"
      ⊥ P4: "owner denies violations"
  P5: "new safety regulations approved"
```

### Step 7: Evidence and mass

```
P1: Λ = log(1.50) + log(1.50) + log(1.12) = 0.92
    m = σ(0.92) = 0.72,  |V| = 3

P3: Λ = 0 + log(1/1.12) = -0.11     (counter shifts down)
    m = σ(-0.11) = 0.47,  |V| = 0

P4: Λ = log(1.12) = 0.11
    m = σ(0.11) = 0.53,  |V| = 1
```

### Final tree

```
(m=0.72, 3v)  P1: "building collapsed; residential"
  (m=0.54, 1v)  P2: "survivors rescued" →P1
  (m=0.47, 0v)  P3: "violations alleged" →P1
    (m=0.53, 1v)  ⊥ P4: "owner denies" ⊥P3
(m=0.54, 1v)  P5: "safety regulations approved"
```


## 10. Validated Results

### Iran-US F-35 Fighter Jet Incident (93 claims, 27 pages)

```
Pass 1: 44 propositions, 3 roots
Pass 2: 92/93 claims assigned

  P1  "F-35 fighter jet damaged by Iran"  m=0.91  21v
  P3  "emergency landing"                m=0.53   3v
  P12 "first Iranian hit on US aircraft"  m=0.41   5v
  P19 "second fighter jet claim"          m=0.55   4v
```

### Jeffrey Epstein Death Investigation (75 claims, 30 pages)

```
Pass 1: 47 propositions, 2 roots
Pass 2: 75/75 claims processed

  P1  "Epstein died in custody"           m=0.86  10v
  P3  "Baden: homicide, neck fractures"   m=0.56   1v
  P5  "Sampson rules suicide"             m=0.59   2v  ⊥P3
  P12 "found with bedsheet ligature"      m=0.63   3v
```

### Comparison

| Metric | Fighter jet | Epstein death |
|--------|------------|---------------|
| Claims | 93 | 75 |
| Propositions | 44 | 47 |
| Roots | 3 | 2 |
| Top mass | 0.91 (21v) | 0.86 (10v) |
| Disputes | severity (→ vs ⊥) | cause of death (→ vs ⊥) |

Same language, same five operations, different domains. Both produce
correct epistemic structure with disputes visible and mass
accumulating from independent sources.

### Full Pipeline Test (54 claims, 3 pages, v2 claim trees)

2026-04-08: Three diverse pages through the complete pipe
(EW v2 → Sense with claim tree drag → PG ANN landing).

```
Pages:
  25th Amendment (11 claims) — political/institutional
  Epstein files (22 claims) — investigative/contested
  Iran ceasefire (21 claims) — military/diplomatic

Results: 38 beliefs, 4 roots, 34 edges (26 IMPLIES + 8 DISPUTES)
         13 beliefs with multiple voices (R1 accumulation)
         8 genuine DISPUTES (every one a real disagreement)
         $0.086 total ($0.002 + $0.039 + $0.045)
```

Key findings:

**Claim tree drag eliminates LLM for 90%+ claims**: The 25th Amendment
page used 1 LLM call for 11 claims ($0.002). EW's typed relations
(causes/counters/evidence/elaborates) drove placement mechanically.

**Correct epistemic structure per field**:
- 25th Amendment: Trump threat → Democrat push → debate (for/against/mechanism).
  Clean causal chain with DISPUTES for partisan opposition.
- Epstein: Case files → FBI material → surveillance → competing narratives.
  DISPUTES correctly mark official ruling vs conspiracy evidence.
- Iran: Content correct but too flat (12 depth-1 children). Caused by
  EW extracting most claims as `elaborates` instead of `causes`.

**8 DISPUTES edges, all genuine**:
1. Strait of Hormuz open ⊥ missiles across Gulf (fact tension)
2. Araqchi ready for ceasefire ⊥ hopes faded (diplomatic contradiction)
3. Khamenei not killed ⊥ conflicting statements (correction)
4. Prison staff story ⊥ case files (competing narratives)
5. Medical examiner suicide ⊥ case files (official vs contested)
6. Republicans ⊥ Democrats on 25th (partisan opposition)
7. DOJ Inspector General ⊥ prison staff (institutional counter)
8. Officials haven't confirmed ⊥ prison staff (official silence)

**PG ANN landing works**: Iran ceasefire page correctly landed on
Trump threat field (sim=0.631) via subtree centroid search.

**Emergence threshold correct**: Iran ↔ 25th at sim=0.520 (below 0.55).
They're related (Trump links both) but genuinely different fields.
Epstein fully isolated (sim=0.22). System correctly kept all separate.

**Per-root heal validated**: Global heal degraded edge entropy
(0.563→0.570) while collapsing roots. Per-root heal preserves
root structure while making correct local restructures.

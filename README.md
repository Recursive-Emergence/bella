# BELLA — Bayesian Epistemic Logical Lattice for Accumulation

A formal language and engine for constructing belief structures from evidence streams.

<p align="center">
  <img src="https://raw.githubusercontent.com/Recursive-Emergence/bella/main/hero.svg" alt="A worked example: a break-in at a gallery, two paintings, three witnesses. The Guard's single claim 'both there at midnight' is evidence on both propositions — one entity, two effects, one hyperedge. Posterior: P1 (Sunset stolen) +3 dB, P2 (Storm stolen) -26 dB. When the Guard's claim conflicts with the Camera, his reputation drops and his evidence on P2 also weakens — even though no new evidence about Storm arrived." width="100%"/>
</p>

## What is BELLA?

BELLA takes a stream of claims from diverse sources and progressively builds an **epistemic belief tree** — a structured representation of what is known, disputed, and uncertain about a topic.

```
claim₁ → BELLA → P1: "building collapsed" (m=0.72, 3v)
claim₂ →              P2: "survivors rescued" →P1 (m=0.54, 1v)
claim₃ →              P3: "structural violations" →P1 (m=0.47, 0v)
claim₄ →                ⊥ P4: "owner denies violations" (m=0.53, 1v)
```

Each node is a **proposition** — not a claim, but an abstract belief. Claims accumulate as evidence, updating Bayesian mass. Disputes are structural: a counter (⊥) child explicitly contradicts its parent.

## Core Concepts

**Propositions** are abstract beliefs, not raw claims. Multiple claims can confirm the same proposition.

**Relations** are typed:
- `→` supports/implies (child is evidence for parent)
- `⊥` counters/denies (child explicitly disputes parent)

**Mass** is Bayesian (Jaynes): `m = σ(Σ log lr)` where lr is the likelihood ratio of each piece of evidence.

**Voice count** captures source independence — how many independent sources confirm.

**Assessment** is the pair `(m, |V|)` — no arbitrary categorical labels.

**The Gene** is a compact representation of the belief tree that grows with each claim, providing context for routing the next one.

## Architecture: Pattern, Translator, Expression

BELLA separates three things:

- **The kernel** — six fixed rules (R1–R6) that read evidence and build structure. Small, stable, never changes.
- **The gene** — a compact text representation of everything the system knows. Grows with each claim. Transmissible.
- **The belief tree (KB)** — the expressed structure: propositions with mass, edges with relations, disputes made visible.

The kernel reads the gene to produce the KB. Any instance of BELLA with the same kernel can read a gene and reconstitute a functionally equivalent KB — not bit-identical, but able to answer the same queries with the same confidence.

This is the same three-tier pattern biology uses for heredity (DNA / ribosome / protein). BELLA was not designed to imitate it; the architecture was forced by the problem of accumulating belief across streaming evidence. See [SPEC.md](SPEC.md) — Foundation section — for the full account.

## The Language

```
-- Propositions
P<n>: "3-8 word description" (m, |V|v)

-- Relations
→  supports/implies
⊥  counters/denies

-- Actions (one per claim)
⊨ P<n>                     -- confirm existing proposition
⊨ P<n> ∧ δ"detail"          -- confirm + amend with nuance
⊢ P<new> → P<n> "desc"      -- new proposition supporting P<n>
⊢ P<new> ⊥ P<n> "desc"      -- new proposition countering P<n>
⊢ P<new> "desc"              -- new unrelated root
```

## How It Works

**Pass 1 (Structure)**: Claims stream in one at a time. Each claim is evaluated against the current gene (compact belief tree). One LLM call per claim produces one action. The gene grows progressively.

**Pass 2 (Evidence)**: Claims are assigned to propositions with Bayesian likelihood ratios. Mass accumulates. The pair (m, |V|) captures both evidence quality and source independence.

## Validated Results

| Dataset | Claims | Propositions | Roots | Cost |
|---------|--------|-------------|-------|------|
| Iran-US F-35 fighter jet incident (93 claims) | 93 | 44 | 3 | $0.29 |
| Jeffrey Epstein death investigation (75 claims) | 75 | 47 | 2 | $0.22 |

Both produce correct epistemic structure: disputes identified, voices accumulated, Bayesian mass computed.

## Repository Layout

```
SPEC.md       Formal specification (six rules, gene, invariants)
VISION.md     Theoretical grounding — Jaynes, Gödel, consciousness
JAYNES.md     What BELLA inherits from / extends / specializes in Jaynes
CHALLENGES.md Open work for SPEC v0.2 — theory and engineering agenda
WHY.md        The epistemic crisis BELLA addresses
MEMORY.md     BELLA applied to LLM agent memory
EXAMPLES.md   Domain-agnostic case studies
TEASER.md     Short pitch
CHANGELOG.md  Version history

kernel.py     The kernel implementation
grow.py       Belief-tree growth engine
cli.py        Command-line interface
*.html        Visual diagrams and prototypes

replay/       Historical-event validation harness
              (Wirecard, Theranos, Wakefield, Hydroxychloroquine)
```

## Specification

See [SPEC.md](SPEC.md) for the full formal specification.

## Status

**v0.1** — Language defined, validated on two domains. Engine is experimental.

## Related work

The empirical tool [`bellamem`](https://www.npmjs.com/package/bellamem)
applies this calculus as persistent memory for LLM coding agents.

## License

MIT

## Citation

If you use BELLA in research, please cite:

```
BELLA: Bayesian Epistemic Logical Lattice for Accumulation
Recursive Emergence / HereNews Project, 2026
https://github.com/Recursive-Emergence/bella
```

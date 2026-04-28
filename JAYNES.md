# JAYNES.md — Foundations BELLA Inherits from E.T. Jaynes

BELLA's evidence calculus and its philosophical posture are inherited
from E.T. Jaynes, *Probability Theory: The Logic of Science*
(Cambridge University Press, 2003). This document names what BELLA
takes from Jaynes, what it extends, and what it deliberately
specializes — so that readers can locate the primitives in their
original context and judge the borrowings critically.

Primary references:
- Jaynes, E.T. *Probability Theory: The Logic of Science.* Cambridge
  University Press, 2003. (Free PDF at the Bayes archive maintained at
  Washington University.)
- Refsgaard, J.C. and dentalperson, "E.T. Jaynes Probability Theory:
  The Logic of Science I." LessWrong, 27 Dec 2023. Readable summary of
  Chapters 1–6.
- Aubrey Clayton, video reading course on Jaynes (YouTube).


## 1. Direct inheritances

### 1.1 Evidence as log-odds (Ch. 4)

Jaynes defines an evidence function

    e(H | DX) = 10 · log₁₀ O(H | DX)

where O is posterior odds. This is the decibel scale of evidence —
adding 3 dB roughly doubles odds; 10 dB multiplies odds by 10.

BELLA's R1 is the same machinery in nats:

    Λ(P) = Σ log lr(c_i)
    m(P) = σ(Λ(P))

Conversion: 1 nat ≈ 4.343 dB; 1 dB ≈ 0.230 nats. Jaynes's framing
emphasizes the additive structure of evidence — every independent
piece adds a dB; total evidence is just the sum. BELLA's
`Λ = Σ log lr` is the same statement, claim by claim.

The decibel framing is sometimes more intuitive when reading traces:

    0 dB  = 1:1 odds   (neutral)
    3 dB  ≈ 2:1        (modest)
    10 dB = 10:1       (strong)
    20 dB = 100:1      (very strong)

A claim with lr = 2 contributes log(2) ≈ 0.693 nats ≈ 3.01 dB. A claim
with lr = 10 contributes log(10) ≈ 2.303 nats ≈ 10 dB.

### 1.2 The three desiderata (Ch. 1)

Jaynes builds probability as the unique extension of formal logic
satisfying three desiderata:

1. **Real-valued plausibility** — degrees represented by real numbers.
2. **Common-sense correspondence** — qualitative ordering matches
   intuition (more evidence → higher plausibility).
3. **Consistency**:
   - 3(a) all paths from evidence to conclusion yield the same result
   - 3(b) all relevant evidence is used
   - 3(c) equivalent states of knowledge get equivalent plausibility

BELLA implicitly assumes all three. The operationally relevant one for
current empirical work is **3(a)**.

#### Empirical verification of 3(a)

`replay/shuffle_test.py` runs each case through 30 random permutations
of arrival order and reports the spread on final Λ:

| case | Λ relative spread (30 perms) |
|------|------------------------------|
| Wirecard | 0.50% |
| Theranos | 0.23% |
| Wakefield | 0.23% |
| Hydroxychloroquine | 0.65% |

All under 1% — empirical confirmation that BELLA's calc respects
desideratum 3(a) on these cases. The `σ = 1/√n` damping in the entity
reputation update is the structural mechanism producing convergence.

This is a partial check: it covers only the mechanical R1 + entity-rep
calc (deterministic, no LLM). Path-invariance of the full system —
including LLM-driven action selection (CONFIRM / AMEND / CHILD /
COUNTER) and R3 emergence — needs separate verification.

### 1.3 Priors are background information, not "initial guess" (Ch. 4)

Jaynes's "prior" means *anything known not encoded in the data
variable* — including the likelihood/sampling assumptions themselves.
The robot always has background information X, and any probability
P(H | X) without further data is a prior probability.

This is broader than the modern Bayesian usage. For BELLA, it
clarifies why **entity reputation** is in the calculus at all. The
reputation rep(E) of a source is exactly background information about
that source — accumulated from past claims, conditioning every
subsequent claim. R5 (entity ↔ belief feedback) is a Jaynesian prior
*that evolves with the evidence stream*, not a fixed initial guess.

### 1.4 Multiple hypotheses must be enumerated (Ch. 5)

The ESP and Hempel-crow examples make the same point:
**P(H | D) is meaningless without explicit alternative hypotheses.**
A black crow is "evidence for all crows are black" only relative to
which other hypotheses are considered. ESP-success is "evidence for
ESP" only relative to whether deception or experimental error are also
in the comparison set.

BELLA's `m = σ(Λ)` for a single proposition is implicit binary —
P(target) vs P(¬target). The dispute structure (⊥) is BELLA's
mechanism for surfacing alternatives, but it's per-edge not
per-proposition.

This is the lens the HCQ trajectory should be read through. The
early-2020 spike to m = 0.77 was not just a dependent-voice
over-counting problem — it was a hypothesis-space failure. The
implicit alternative was "HCQ ineffective," but the *operative*
alternatives in March 2020 should have included:

- "The early evidence is from non-independent sources"
- "Small uncontrolled trials systematically over-estimate effect"
- "Political amplification is uncorrelated with efficacy"

Surfacing these alternatives would have absorbed evidence that the
unified m unwarrantedly attributed to "HCQ effective."

This points at a future BELLA primitive: **per-proposition explicit
alternative-hypothesis tracking** — not just ⊥ disputes between
propositions, but, for each proposition, a structured list of the
alternative hypotheses being implicitly compared against. Open work.

### 1.5 MLE is brittle; carry the full posterior (Ch. 6)

Jaynes shows MLE can be wildly wrong — the sensor/source example
produces 150 (MLE) vs 105 (Bayesian) for the number of emitted
particles, because MLE discards the source distribution prior. The
full Bayesian posterior compromises between data and prior.

BELLA tracks Λ throughout and exposes m = σ(Λ) as a summary, never
collapsing to a point estimate. Voice count |V| is reported separately
as a non-collapsed measure of source independence. Jaynes-correct.


## 2. Where the Pearl question lands

Jaynes's Chapter 3 directly addresses what is now called the
Jaynes–Pearl divide:

> ...philosophers like Penrose take it as a fundamental axiom that
> probabilities referring to the present time can depend only on what
> happened earlier, and not what happens later. [In Jaynes's view]
> when we use probability as logic, we do not care about causality,
> only about how the information available changes our beliefs.

Jaynes treats P(first-draw-red | second-draw-red) and
P(second-draw-red | first-draw-red) as equally informative about the
urn — same information content, regardless of temporal direction.
Pearl's do() introduces a separate notation for interventions on
systems. In Jaynes's framework, intervention is additional
conditioning, not a different probability calculus.

The Chapter 3 randomization rant clarifies the interpretive move:

> ...we invent the dignified-sounding word *randomization* to describe
> what we have done. This term is, evidently, a euphemism, whose real
> meaning is: deliberately throwing away relevant information when it
> becomes too complicated for us to handle.

In Jaynes's view, RCTs aren't a different *kind* of evidence — they
are observational evidence designed to remove specific selection
structures. Same calculus, different conditioning.

**BELLA chooses the Jaynes side of this divide.** R1 accumulates
evidence as information about belief without privileging interventional
vs. observational sources. The modality table in `replay/bella_calc.py`
weights differently (RCT 0.95, observational_study 0.70) — but the
weighting is *calibration of strength*, not a separate inferential
channel.

The HCQ false-confidence problem is therefore *not* an argument for
importing Pearl's do(). It is a Jaynes-internal problem:
missing-alternatives (§1.4 above) + dependent-voices (§4 below). Both
are addressable within the Jaynes framework.


## 3. Where BELLA extends Jaynes

Jaynes's project is foundational: probability as extended logic, with
priors and likelihoods correctly handled. He stops at the inference
primitives. BELLA adds:

- **R2 STRUCTURE** — entropy-driven coherence on a belief tree.
  H(B) = w(rel) × (1 − sim(B, parent(B))). Jaynes does not address
  how to *organize* many propositions into a structured belief
  network.
- **R3 EMERGE** — centroid convergence into fields. The observation
  that subtree centroids converge above a threshold to indicate
  same-field membership is a domain-specific contribution.
- **R4 SELF-REFER** — Ψ on KB itself. Jaynes treats probability as
  logic about the world; BELLA applies the same logic to the system's
  own state, with attenuated convergence Λ_level(n) = Λ_level(n−1)·α.
- **R5 CONVERGE** — feedback cycles. The entity ↔ belief cycle
  rep(E) → lr(claim) → Λ(B) → rep(E) is a circular causation Jaynes
  does not formalize. The Banach contraction guarantee is BELLA's.
- **R6 ENTANGLE** — cross-field structure via shared entities.
  Hyperedge geometry through entity co-membership is structural and
  beyond Jaynes's scope.

These extensions live above the inference primitives. They consume
Jaynes-correct masses and produce structure; they do not modify R1.


## 4. Where BELLA specializes Jaynes

The marginal-voice attenuation

    lr' = 1 + (lr − 1) × 0.1

is BELLA's specific answer to a problem Jaynes touches on but does
not formalize: handling non-independent sources. Same source
confirming the same proposition twice is counted once at full weight
and subsequent times at 10% — a steep but non-zero discount.

This is the mechanism HCQ exposed. The early-2020 spike was driven by
four entries that were *not* independent:

- Trump's amplification was downstream of Raoult's trial
- FDA's EUA was downstream of Raoult + political pressure
- Zelenko's case series was a separate but methodologically aligned
  source

The current attenuation handles same-name repeats. The HCQ analysis
suggests it should generalize to **cross-source dependence**: when
source B's claim is evidentially derived from source A's claim, B is
a marginal voice on A's evidence, not an independent voice. This is a
Jaynes-native, primitive-respecting extension BELLA can take on next.
Open work.


## 5. References

- Jaynes, E.T. *Probability Theory: The Logic of Science.* Cambridge
  University Press, 2003. (Bretthorst, ed.)
- Refsgaard, J.C. and dentalperson. "E.T. Jaynes Probability Theory:
  The Logic of Science I." LessWrong, 27 Dec 2023. Readable summary of
  Chapters 1–6.
- Aubrey Clayton. Video reading course on Jaynes (YouTube).
- Pearl, J. *Causality: Models, Reasoning, and Inference.* Cambridge
  University Press, 2nd ed., 2009. The Pearl side of the divide that
  BELLA does not adopt.

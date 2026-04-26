# Why BELLA? Why Now?

We are in an epistemic crisis.

AI generates plausible text at scale. Misinformation spreads faster
than correction. Mainstream media sits behind paywalls while local
newsrooms collapse — over 2,900 US newspapers have shut down since
2005. Social media algorithms optimize for engagement, not truth.
Audiences revolt against institutions they once trusted, yet have
no better alternative.

The result: nobody knows what to believe.

This is not an information problem. We have more information than
ever. It is a **structural** problem. There is no shared, formal,
verifiable way to assemble beliefs from evidence. Every reader is
alone with their feed.

## What Lean Did for Mathematics

In 2017, the Lean theorem prover began transforming mathematics.
Not by doing math differently — by giving mathematicians a **formal
language** where proofs could be verified by machine. The Mathlib
library now contains over a million lines of formalized mathematics.
When a proof is written in Lean, it is correct. Not probably correct.
Correct.

Lean didn't replace mathematicians. It gave them a medium where
rigor is computable.

## What BELLA Does for Journalism

BELLA is a formal language for beliefs.

A claim arrives: *"F-35 fighter jet damaged by Iranian fire."*
Another claim arrives from a different source: *"Iran struck and
seriously damaged the jet."* A third: *"US Central Command rejected
Iran's claims that it shot down the jet."*

In the current media landscape, these are three separate articles
in three separate feeds. The reader sees one, maybe two. They form
an opinion based on whichever they encounter first.

BELLA assembles them into a single epistemic structure:

```
P1: "F-35 damaged by Iran"  (m=0.91, 21 independent sources)
  P4: "Iran claims shot down"
    ⊥ P5: "US rejects shot-down claim"
```

Damage is near-certain — 21 sources confirm. The dispute is
specifically about severity: "shot down" vs "damaged." Both sides
agree the jet was hit. This is visible in the structure. No
framing. No paywall. No algorithm deciding what you see.

One claim at a time, the tree grows. After 93 claims from 27 sources:
44 propositions with Bayesian confidence, dispute structure, and
source independence — all formally verifiable.

## The Crisis BELLA Addresses

| Problem | Current state | With BELLA |
|---------|--------------|------------|
| AI-generated content | Plausible but unverifiable | Every belief traces to source claims with confidence |
| Misinformation | Spreads unchecked | Counter-evidence is structural (⊥), not editorial |
| Media paywalls | Knowledge locked behind payment | Epistemic structure is open, evidence-weighted |
| Local news collapse | Communities lose shared understanding | Any evidence stream can build shared belief structure |
| Audience distrust | "Who do I believe?" | See the evidence yourself: (m, voices) per proposition |
| Filter bubbles | Algorithms choose your reality | The full tree is one structure — disputes included |

## How It Works

BELLA has five operations. That's it.

```
⊨ P       confirm — this claim says the same thing
⊨ P ∧ δ   amend — confirms and adds a detail
⊢ Q → P   child — new supporting evidence
⊢ Q ⊥ P   counter — explicit denial or dispute
⊢ Q       root — new unrelated topic
```

Evidence is Bayesian: each claim carries a likelihood ratio based
on source credibility, modality, and grounding. Mass accumulates.
Independent voices count. The pair (m, |V|) — posterior probability
and voice count — is the assessment. No arbitrary labels. Just math.

## Validated

| Dataset | Claims | Result |
|---------|--------|--------|
| Iran-US fighter jet incident | 93 claims, 27 sources | 44 propositions, disputes identified |
| Jeffrey Epstein death investigation | 75 claims, 30 sources | 47 propositions, suicide vs homicide structured |

Two completely different domains. Same five operations. Same language.
Correct epistemic structure in both.

## OSINT and Open Evidence

Open Source Intelligence faces the same crisis at professional scale.
Analysts monitor satellite imagery, social media, shipping data,
government filings, leaked documents — thousands of signals per day.
The raw evidence is open. The assembly is manual, fragile, and locked
inside analyst notebooks.

BELLA is native to OSINT. Every claim carries provenance (source,
modality, credibility). The tree shows what converges across sources
and what contradicts. An analyst can see: "14 open sources confirm
troop movement. 2 sources dispute the location. 1 source has been
unreliable before (m=0.52)." The structure IS the intelligence
product — not a summary written by one person, but a formally
verifiable assembly of all available evidence.

## Beyond Journalism and Intelligence

A formal language for assembling beliefs from evidence applies
wherever sources conflict: science, law, medicine, history, policy.
Any domain where the question is not "what does one source say?"
but "what does the evidence, taken together, support?"

## An Open Epistemic Commons

BELLA is not a product. It is a language — and languages become
powerful when everyone speaks them.

**Journalists** use BELLA to assemble evidence across sources,
making their verification process transparent and machine-readable.
Instead of "trust me, I checked," the tree shows what was checked,
what converged, and what remains disputed.

**OSINT analysts** use BELLA to build shared intelligence products
from open evidence. The tree is the product — collaboratively
constructed, formally verifiable, continuously updated.

**Researchers** use BELLA to structure literature reviews, track
replication across studies, and identify where scientific consensus
is strong vs where it fractures.

**Citizens** read BELLA trees to see the evidence for themselves.
Not through one journalist's framing or one algorithm's selection,
but as a structured whole. "21 sources confirm this. 3 dispute that.
Here is the specific point of disagreement." Epistemic agency
returns to the reader.

**Developers** build on BELLA — news aggregators, fact-checking
tools, collaborative investigation platforms, educational
applications — all sharing the same formal language for belief.

This is epistemic lifting: a formal language that starts with
professionals (journalists, analysts, researchers) and lifts
the entire public's ability to reason about evidence. Not by
telling people what to believe, but by making the structure of
evidence visible, navigable, and verifiable.

Wikipedia showed that knowledge can be collaboratively assembled.
Git showed that code can be collaboratively verified.
BELLA shows that beliefs can be collaboratively constructed —
with Bayesian rigor, source transparency, and dispute structure
built in.

The epistemic crisis is not solved by better media. It is solved
by giving everyone access to the same evidence structure. When
the tree is open, the reader is no longer alone with their feed.

Lean gave mathematics a computable foundation for rigor.
BELLA gives epistemology a computable foundation for belief.

The crisis is structural. So is the solution. And the solution
is open.

---

**BELLA is open source: [github.com/here-news/bella](https://github.com/here-news/bella)**

# Why Do We Need a Journalism Language Framework at This Age?

Hi all,

Sharing something we've been working on: a formal language for assembling beliefs from conflicting evidence. We're calling it **BELLA** (Bayesian Epistemic Logical Lattice for Accumulation).

**The motivation**: we're drowning in claims. A single news event generates hundreds of assertions from dozens of sources, confirming, contradicting, or adding context. Journalists cross-reference this in their heads. OSINT analysts do it in notebooks. Wikipedia editors argue it out in talk pages. Social media buries it under algorithms optimized for engagement, not truth. But there's no formal, computable way to do it. We have Lean for math proofs, SQL for data, but nothing for "here's what *n* sources confirm, here's what *n* dispute, here's the exact point of disagreement."

**BELLA** is an attempt at this. Five operations, that's it:

- **⊨** confirm (same fact, voice accumulates)
- **⊨ ∧ δ** amend (confirms + adds nuance)
- **⊢ →** child (new supporting proposition)
- **⊢ ⊥** counter (explicit denial, dispute becomes structural)
- **⊢** root (new unrelated topic)

Claims stream in one at a time. Each updates a growing belief tree. The tree is human-readable and machine-readable — structured evidence, not generated prose that hallucinates. Evidence is Bayesian: each claim carries a likelihood ratio derived from source credibility and grounding. The assessment is the pair (m, |V|): posterior mass and independent voice count. No arbitrary labels. Just Jaynes.

We tested on two datasets: 93 claims about a military incident (Iran-US fighter jet, 27 sources) and 75 claims about the Epstein death investigation (30 sources). Same language, same engine, both produce structured belief trees where you can trace every dispute back to who said what with what confidence. The suicide-vs-homicide debate, for instance, emerges structurally — not as someone's editorial judgment, but from the evidence itself.

Next, we will test against over 400 local news sources in more than 20 languages.

BELLA is to serve journalism in this new age and save it. But what excites us beyond journalism: the language is self-encoding. BELLA can express beliefs about its own belief structure. A system that maintains a probabilistic world model, then applies the same language to model itself... that's a path toward machine epistemology we think is worth exploring.

The spec, engine, and examples are open source. Although it is in an early stage, the language is defined, and the engine is experimental. Feedback very welcome, especially from folks working on argumentation theory, Bayesian epistemology, computational journalism, OSINT, or social media integrity.

Open source soon, and your early comments are highly appreciated.

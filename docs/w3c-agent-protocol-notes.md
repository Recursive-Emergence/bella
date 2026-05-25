# The memory, state, and provenance layer
## A missing piece in the AI Agent Protocol draft

*A working note · 2026-05-25 · submitted as input to the W3C AI Agent Protocol Community Group.*

---

## 0. What this is

This is not a proposal. It is a working sketch of the shape the gap in the current AI Agent Protocol draft appears to want, arrived at by:

1. Running an implementation ([Bella](https://github.com/Recursive-Emergence/bella)) in production as the memory and coherence layer of an operational deployment;
2. Pressure-testing that shape over one week of mailing-list and Slack discussion with another CG participant.

I am sharing it as input to the CG's decision about what fills the gap, not as a finished design. The intent is to make a concrete shape visible so the group can react against something specific rather than against the empty space.

---

## 1. The gap in the current draft

Reading the current draft at <https://w3c-cg.github.io/ai-agent-protocol/protocol.html>, four modules are present:

- **Identity** — anchored in DIDs (e.g. `did:wba`)
- **Description** — capability declaration via Information and Interface resources
- **Discovery** — active (`.well-known` URIs) and passive (registration APIs)
- **Security & Privacy** — framework identified, refinement ongoing

What is not yet present is the layer that handles:

- Accumulated memory across sessions
- Provenance of claims an agent emits
- Mutable assessment of belief as evidence arrives
- Structural preservation of disputes between sources

Without this layer, the protocol can describe *who* an agent is (identity), *what it can do* (capability), and *how to reach it* (discovery) — but not *what it knows*, *why it knows it*, or *what is contested about that knowledge*. The downstream effect: audit, regulatory compliance (EU AI Act and successors), and inter-agent claim composition all become out-of-protocol concerns.

This note describes one shape for what might fill that gap.

---

## 2. The shape, as it appears from running it

The shape that has survived implementation and adversarial review rests on three design choices.

### 2.1 Append-only journal, derived state

An agent's accumulated memory is best represented as a monotonically-growing journal of *actions* (assertions, confirmations, disputes), not as a mutable database of beliefs.

Each action is a single line:

```
⊢ P3 → P1 "Guard saw both"           — assert P3 supporting P1
⊨ P1                                  — confirm P1 (adds a voice)
⊢ P4 ⊥ P2 "Camera contradicts"        — assert P4 as counter to P2
```

The assessment of a belief — its likelihood, its source independence — is *derived* from the journal, not stored alongside it. This means:

- **Provenance is automatic** — every value traces back to specific actions
- **Replay is trivial** — derive the state as of any past timestamp
- **Disputes are structural** — a counter-claim becomes a child node, not a vote against a parent
- **Audit follows the data model** rather than fighting it

### 2.2 Disputes preserved as structure, not aggregated

Five voices repeating one source must not produce the same confidence as five independent voices. Five claims supporting a position must not collapse with one claim disputing it.

The substrate carries:

- Source identity per claim
- Source independence (typed, declarable)
- Counter-claims as first-class structural children, never as negative weights

### 2.3 Identity at three layers

- The **agent** has stable identity (DID, per the current draft).
- The **proposition** (an abstract belief) has stable identity independent of its current assessment.
- The **snapshot** (assessment at a point in time) has versioned identity.

These are not redundant — they correspond to three distinct citation needs in audit and inter-agent claim composition.

---

## 3. Parse and interpret as separate concerns

The protocol gains clarity if it separates two responsibilities that often get conflated:

**The parse layer** consumes the journal's wire form (text, streaming, schema-validated) and produces a structured AST of actions. This layer is well-served by existing structured-data tooling and does not need to know what the actions *mean*.

**The interpret layer** consumes the AST and maintains the live state — the hypergraph of propositions, the derived assessments, the disputes. This layer encodes the *epistemic semantics* and is where any protocol-level rules about how belief composes would live.

The AST is the seam. Both layers can have alternative implementations, but the AST shape — what kinds of actions exist, what their syntactic structure is — is the part that benefits from being a shared standard.

This separation also means: tooling work already happening in W3C structured-data circles (parsers, source-map machinery, schema validation) is reusable for this layer without requiring the CG to invent it.

---

## 4. Reference, not inclusion

Beliefs should be *referenced*, not *inlined*. Inlining belief structures in every agent message collapses the very provenance the structures exist to preserve.

The shape:

- Each belief has a stable identifier — URI, DID, or content-hash, depending on trust model
- Web apps and other agents reference the identifier; the belief itself is resolved on demand
- Resolution returns a JSON-LD representation of the belief plus, optionally, its claim history and dispute children (selective dereferencing via query parameters)

Two identity tracks need to coexist:

- **Stable proposition identity** — addresses the belief as a thing. Same URI today and tomorrow.
- **Versioned snapshot identity** — addresses the assessment at a point in time. Immutable once written.

A practical convention: stable URI for the proposition, snapshot URIs as sub-paths or query-parameterized derivatives.

---

## 5. Distribution

Two distinct distribution concerns sit at different layers:

| Layer | What | How |
|---|---|---|
| **Engine + schema** | The runtime that interprets the journal and the canonical grammar for actions | Single canonical package (npm, crate, etc.); semver; CDN-distributed for browser consumption |
| **Belief data** | Per-organization journals and the resulting belief graphs | Per-publisher hosting at publisher's own URI or DID; each publisher = identity, not a fork |

Discovery: a publisher registry tracks *identities* (DIDs or domains) rather than data. Cross-references between beliefs from different publishers resolve via URI as in §4.

---

## 6. Web-app surface

If the layers above are in place, the developer-facing experience is a one-line include:

```html
<belief-card src="belief://nc.example.com/anna-b2f-billing"
             expand="claims,disputes,history" />
```

The custom element fetches the belief on activation, parses the JSON-LD response, and hydrates its children. Operators clicking *trace* on a claim get byte-range traceability into the source journal. Operators clicking *replay* get the assessment as of any past date.

This is consistent with W3C custom-element conventions and does not require novel client-side machinery.

---

## 7. What this is not claiming

To avoid mis-reading:

- This is **not** claiming a specific implementation (Bella's gene format, six-rule kernel, etc.) is what should go in the protocol.
- This is **not** claiming this is the only shape that could fill the gap.
- This is **not** a formal proposal for a CG deliverable yet.

What it *is* claiming:

- The gap exists and matters.
- The design choices above are the ones that survived implementation and adversarial review.
- A CG note or sub-deliverable filling this gap, with input from implementers, would be substantially better than letting vendor-specific patterns become the de facto answer.

---

## 8. Open questions for the CG

1. **Scope.** Is filling this gap considered in scope for this CG, or is the intent that it lives in an adjacent group (VC WG, Agent Identity Registry CG, somewhere else)?

2. **Parallel work.** Are there efforts already underway within the CG that I should align with rather than duplicate? Meeting minutes are sparse on this from the outside; I want to avoid stepping on existing drafts.

3. **Receptivity.** If this CG is the right venue, would a small spec note based on the shape above be welcome as a deliverable? If so, on what timeline and with what level of editor responsibility?

---

## 9. Acknowledgments

The architectural framings of *parse-and-interpret as separate concerns*, *belief as reference rather than inclusion*, and the *two-layer distribution model* emerged from substantive technical exchange with [Sasha Firsov](https://github.com/sashafirsov) — author of cem-ml and xs-parser — over the course of one week of mailing-list and Slack discussion. Their willingness to push back on early framings sharpened the shape considerably.

The Bella project (the implementation grounding this note) is open source at <https://github.com/Recursive-Emergence/bella>, with TypeScript port at <https://github.com/immartian/bellamem>.

— Isaac Mao

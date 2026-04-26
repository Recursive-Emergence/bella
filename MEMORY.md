# BELLA as LLM Memory Architecture

*Draft — 2026-04-09. To revisit when we tackle coding agent memory.*

An application of BELLA outside news epistemics: using the same
calculus to solve the memory problem in LLM coding agents (Claude
Code, Cursor, etc.).

The claim: current LLM memory fails because context is a flat
sequence of tokens. BELLA's belief tree IS the right structure
for agent memory — same six rules, same calculus, different domain.


## 1. The Problem

### 1.1 What current systems do

```
Flat context window:   tokens in a sequence, recency bias
/compact:              lossy summary, destroys structure
1M context:            bigger flat buffer, same structural problem
RAG:                   embedding retrieval, no accumulation
Vector DB:             nearest neighbors, no mass, no structure
Knowledge graph:       structure, but no mass or convergence
MEMORY.md (manual):    beliefs, but human-maintained, no calculus
```

Every current approach is **stateless retrieval**. None of them
accumulate. None of them learn. The agent has the same blind spots
in session 50 as session 1.

### 1.2 What goes wrong

| BELLA rule | What flat context violates | What breaks |
|---|---|---|
| R1 accumulate | No mass — each message weighs the same | Told 5 times = told once |
| R2 structure | Flat — no parent-child, no typed edges | "key decision" ≈ "idle thought" |
| R3 emerge | No fields — one stream for everything | Can't scope to "auth" vs "perf" |
| R4 self-refer | No self-model | Doesn't know what it's forgotten |
| R5 converge | No feedback | Doesn't learn file reputation |
| R6 entangle | No entities as bridges | Can't see file spans features |

### 1.3 The specific failure modes

**Dementia from compaction**: /compact produces a summary. The summary
loses the "why." The agent re-suggests rejected approaches because the
DISPUTES are gone.

**Re-suggesting rejected approaches**: User says "don't mock the DB in
tests" five times across five sessions. Current system: each rejection
is a new token in an old context that gets compacted away. BELLA: the
rejection accumulates mass — m=0.95 after 5 voices. Cannot be forgotten.

**Losing track of relationships**: Current system forgets that auth.py
depends on session.py after a compaction. BELLA: entities bridge the
files through shared beliefs (R6).

**No pattern learning**: Current system makes the same TypeScript mistake
in every session. BELLA: Entity(TypeScript).reputation drops with each
DISPUTES. Future TS work is more cautious (R5 feedback).

**No personalization**: Current system treats every codebase identically.
BELLA: the belief tree for THIS codebase accumulates over sessions.
File reputations stabilize. Patterns emerge. The agent gets better at
this specific project, not just at coding in general.


## 2. The Architecture

### 2.1 Memory as belief tree

Every user message and agent action is a **claim**. Process it through
the same pipe we use for news:

```
Conversation message → EW (extract claims)
                     → SENSE (land + place)
                     → R1 accumulate
                     → emergence
                     → tree grows
```

Five levels, same as the organism model:

```
Level 0:  Messages      raw user input + agent observations
Level 1:  Beliefs       accumulated with mass and structure
Level 2:  Entities      files, functions, patterns, libraries
Level 3:  Fields        features, modules, concerns
Level 4:  Self-model    "I make too many TS errors" (Ψ — R4)
```

### 2.2 Claim types specific to coding

Extending EW's relation types for the coding domain:

```
causes       "A happens, so B broke"         causal debugging
counters     "don't do X, do Y"              preference rules
elaborates   "here's how it works"           explanation
evidence     "the error was <stack>"         grounding
mechanism    "because of how X works"        technical reason
assessment   "this approach is cleaner"      judgment
decision     "let's use asyncpg"             choice made
correction   "no, not that way"              explicit denial
observation  "the tests pass now"            state report
```

Each maps to a BELLA operation:
- causes → CAUSE
- counters / correction → DENY
- decision → ADD (with high lr)
- observation → CONFIRM (if matches existing belief)
- etc.

### 2.3 Entities for code

Code objects as entities:

```
File         entity(path/to/file.py)
Function     entity(module.func_name)
Class        entity(module.ClassName)
Library      entity(asyncpg)
Pattern      entity(async context manager)
Concern      entity(connection pooling)
Error type   entity(TypeError in X)
```

Each accumulates reputation through R1:
- File with many confirmed beliefs → well-understood, stable
- File with many DISPUTES → problematic, needs care
- Library with high reputation → trusted, use by default
- Pattern with DISPUTES → anti-pattern in this codebase

### 2.4 Fields for codebases

Fields emerge from R3 when belief subtrees converge. Examples:

```
Field(authentication):
  beliefs about auth.py, session.py, login flow, JWT,
  password hashing, OAuth. Emerges from clustering.

Field(database):
  beliefs about asyncpg, pool config, queries, migrations,
  schema. Emerges as database work accumulates.

Field(testing practices):
  beliefs about test organization, fixtures, mocking,
  integration vs unit. Includes DISPUTES for rejected approaches.
```

Fields are scope for context loading. Working on auth loads the
auth field, not the whole codebase history.

### 2.5 Context loading via EXPAND

Replace "load last N messages" with "EXPAND(relevant field)":

```
1. Detect active context from current request
   - Files being edited → entity set
   - Topic keywords → field candidates
   - Recent actions → recent beliefs

2. Load by mass priority:
   HIGH mass (m > 0.8)    → always include (core rules, user preferences)
   Field-relevant         → include if matches active field
   Entity-relevant        → include if touches active files
   DISPUTES               → include if relevant (prevents re-suggestion)
   LOW mass / old         → drop first

3. Budget allocation:
   60%  high-mass beliefs (rules, decisions)
   30%  field-relevant beliefs
   10%  recent low-mass context
```

Token budget is spent on **important** context, not **recent** context.
Recency matters only as a tiebreaker.

### 2.6 The feedback loop (R5)

```
Agent suggests approach A
  → user corrects: "no, use B"
  → DENY approach A, ADD approach B
  → B.mass rises, A accumulates DISPUTES
  → entity(pattern_B).reputation rises
  → entity(pattern_A).reputation drops
  → future claims involving pattern_A get lower lr
  → agent approaches pattern_A with more caution
  → fewer mistakes of this type
```

This is R5 convergence. The agent's behavior is shaped by the
accumulated belief tree. Corrections compound — saying the same
thing 5 times produces a belief with 5x the mass, and 5x the
influence on future actions.


## 3. What BELLA Already Provides

The surprising thing: most of the machinery already exists.

```
Already built:
  ✓ belief_embeddings table (PG pgvector ANN)
  ✓ Neo4j belief graph (structure, edges)
  ✓ R1 Jaynes accumulation
  ✓ R2 entropy-driven structure
  ✓ R3 emergence via centroid convergence
  ✓ PG ANN landing (O(log n) retrieval)
  ✓ Seven operations (CONFIRM, AMEND, ADD, DENY, CAUSE, MERGE, MOVE)
  ✓ Per-root local heal
  ✓ Entity model with INVOLVES edges

Needs building:
  → EW for conversation messages (extract claims from chat)
  → Code-specific entity extractor (files, functions, libraries)
  → Conversation claim types (decision, correction, observation)
  → Context loader: EXPAND(field, budget) → tokens
  → Integration with LLM context assembly
  → Session boundary handling (when does a conversation end?)
```

The core is done. What's missing is the thin layer that adapts
BELLA's pipe to conversation input instead of news pages.


## 4. Why This Is Different From RAG

RAG (retrieval-augmented generation) and BELLA memory are often
confused. They are fundamentally different:

| Aspect | RAG | BELLA Memory |
|---|---|---|
| Storage | Flat vector DB | Structured belief tree |
| Retrieval | Nearest neighbor | Field + entity + mass |
| Accumulation | None — each doc stands alone | Jaynes lr — mass compounds |
| Structure | None | Parent-child, causal, DISPUTES |
| Learning | None — same forever | R5 feedback — reputation evolves |
| Conflicts | Not represented | Explicit DISPUTES edges |
| Context budget | Top-k similar | Mass-weighted field expansion |
| Temporal | Timestamp only | Temporal anchors, event_time |
| Personalization | None | Entity reputation per codebase |

RAG answers "what documents are similar to this query?"
BELLA answers "what do we know about this, with what confidence,
and what did we decide NOT to do?"


## 5. The Bigger Claim

BELLA's six rules are not domain-specific. They describe ANY
system that accumulates evidence over time:

- News epistemics (what we've built)
- LLM agent memory (this document)
- Personal knowledge management
- Scientific research tracking
- Team decision archives
- Customer support history
- Medical patient records

The same calculus works in all of them because the underlying
problem is the same: evidence arrives in a stream, needs to be
structured, contested claims must be visible, mass must accumulate,
and retrieval must be by relevance not recency.

The LLM memory application is the most urgent because coding
agents are hitting the limits of flat context RIGHT NOW. Every
heavy user of Claude Code / Cursor / etc. has felt the dementia
from /compact. The pain point is acute.


## 6. Open Questions

**Session boundaries**: When does a conversation "end"? Is each
conversation a fresh context that inherits from the persistent tree?
Or is the tree continuous?

**Claim extraction**: How aggressive should EW be on chat messages?
Every sentence a claim? Or only explicit decisions and rules?

**Self-observation**: Should the agent's own actions become claims?
("I modified file X" — then if it breaks, CAUSE edge from the
modification to the breakage.)

**Cross-project memory**: Does a developer's preferences transfer
between codebases? Is there a personal belief tree above the
project trees?

**Privacy/trust**: User might reject a belief mid-conversation. Does
the rejection itself accumulate? Could the system become manipulable
through accumulated DENYs?

**Pruning**: What happens to very old, never-confirmed, low-mass
beliefs? Do they decay? Or stay as "maybe"?

**Entropy at scale**: At 10k beliefs, is per-root heal still enough?
Or do we need hierarchical fields (fields-of-fields)?


## 7. Why We Haven't Built It Yet

Focus. News epistemics is the current target. But BELLA was designed
to be domain-agnostic from the start — that's what the theory work
ensures. When we come back to this, the core doesn't need to change.
We add a thin conversation-to-claim adapter and a context loader.

The proof that BELLA is the right model is that the SAME rules apply
to both. If we had to modify R1-R6 for the coding memory case, that
would be evidence the theory is wrong. But we don't. It just works.

This file exists as a placeholder for that future work — and as a
reference when other systems' memory failures remind us we already
have the answer.


## 8. References

- SPEC.md — the full theory (R1-R6)
- grow.py — current implementation for news
- project_bella_pipe — memory file with current pipeline notes
- project_bella_entropy_law — the fundamental entropy discovery

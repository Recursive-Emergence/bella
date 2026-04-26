# BELLA in Action — Four Historical Cases

Four well-known stories, shown as BELLA belief trees. The first
three are arcs over time. The fourth is a static snapshot that
tests BELLA's discriminative power against asymmetric opposition.

```
Case 1:   uncertain → settled     (H. pylori causes ulcers)
Case 2:   uncertain → uncertain   (what killed the dinosaurs)
Case 3:   confident → reversed    (continents don't move)
Case 4:   settled, loudly opposed (Earth is flat)
```

The point: watching these trees teaches BELLA's basics better
than any abstract description. Each case tests a different
property of the calculus.


## Case 1: Convergence — Do bacteria cause ulcers?

For most of the 20th century, medical consensus held that
peptic ulcers were caused by stress and spicy food. Ulcer
patients were prescribed antacids, bland diets, and rest.

Then in 1982, two Australian researchers — Barry Marshall and
Robin Warren — proposed a bacterial cause. They were ridiculed
for twenty years. Then Marshall won the Nobel Prize in 2005.

Here's how the belief tree evolved.

### State 1: 1980 (pre-Marshall)

```
P1  "Peptic ulcers caused by stomach acid from stress"  [m=0.89, 45v]
    Decades of evidence, medical consensus, taught in textbooks
    │
    ├── P2  "Stress increases acid production"              [m=0.76, 12v]
    ├── P3  "Antacids relieve ulcer symptoms"               [m=0.82, 30v]
    ├── P4  "Spicy food aggravates ulcers"                  [m=0.65, 8v]
    └── P5  "The stomach is too acidic for bacteria"        [m=0.91, 20v]
             ← this was the blocking assumption
```

Mass heavily favors the stress theory. |V| is high because
decades of medical literature confirmed the symptomatic model.
No counter-evidence exists yet. P5 is the most confident belief
and it structurally prevents the bacterial hypothesis.

### State 2: 1982 (Warren's observation)

```
P1  "Peptic ulcers caused by stomach acid from stress"  [m=0.88, 46v]
    │
    ├── P2..P4  (unchanged)
    │
    ├── P5  "The stomach is too acidic for bacteria"        [m=0.89, 20v]
    │     │
    │     └── ⊥ P6  "Curved bacteria observed in biopsies"  [m=0.52, 1v]
    │             Warren sees them under the microscope.
    │             DENY P5 — evidence of contradiction.
```

A single new claim arrives. P6 has only one voice (Warren) but
it's a DIRECT observation that denies P5. P5's mass drops
slightly (0.91 → 0.89) from the counter-evidence. P6 itself
sits at m=0.52 — barely above prior. The tree shows the tension
structurally. Nothing is resolved yet.

### State 3: 1984 (Marshall drinks the culture)

```
P1  "Peptic ulcers caused by stomach acid from stress"  [m=0.78, 48v]
    │
    ├── P5  "Stomach too acidic for bacteria"              [m=0.71, 20v]
    │     │
    │     └── ⊥ P6  "H. pylori survives in stomach"        [m=0.74, 4v]
    │             │
    │             ├── P7  "Marshall drank culture, got gastritis"  [m=0.85, 1v]
    │             │       → P6  direct self-experiment
    │             │       → causal: bacterium → gastritis
    │             └── P8  "Biopsies from ulcer patients show H. pylori"  [m=0.68, 3v]
    │
    └── P9  "Antibiotics heal ulcers"                      [m=0.62, 2v]
              (new side-evidence, IMPLIES cause is bacterial)
              ⊥ P1 (indirectly — if antibiotics heal, stress isn't the cause)
```

Three structural changes:
- P7 has high lr (direct self-experimentation, strongest evidence)
- P7 is a CAUSE belief — bacterium preceded and triggered gastritis
- P9 introduces a parallel line of evidence
- Mass begins migrating: P1 drops (0.89→0.78), P6 rises (0.52→0.74)

The tree now has two competing clusters. The entropy law says
this is unstable — heal will eventually restructure.

### State 4: 1994 (NIH consensus conference)

```
P6  "H. pylori causes peptic ulcers"                    [m=0.84, 120v]
    │   ← root elevated: evidence accumulated, now the main branch
    │
    ├── P7  "Marshall's self-experiment"                  [m=0.88, 3v]
    ├── P8  "Biopsies of ulcer patients"                  [m=0.91, 45v]
    ├── P9  "Antibiotics heal ulcers"                     [m=0.89, 60v]
    ├── P10 "Recurrence drops after eradication"          [m=0.86, 30v]
    └── P11 "Mechanism: urease neutralizes acid locally"  [m=0.81, 15v]

⊥ P1  "Peptic ulcers caused by stress"                   [m=0.22, 48v]
       (still has voices from old literature but mass collapsed)
```

R3 EMERGE has fired. What was a fringe DENY child has become
the new root because its subtree accumulated more coherent
evidence. The old theory is not deleted — it persists as a
low-mass belief with DISPUTES, a historical record.

Note what DIDN'T happen: P1 didn't lose its voices. |V|=48
remains. Mass is computed from lr × evidence, not voice count.
The old literature is still there as evidence; it's just been
outweighed by higher-lr new evidence.

### State 5: 2005 (Nobel Prize — full convergence)

```
P6  "H. pylori causes peptic ulcers"                    [m=0.97, 500v]
    │
    ├── Mechanism branch   (well-developed subtree)
    ├── Treatment branch   (antibiotic protocols, cure rates)
    ├── Epidemiology branch (prevalence, transmission)
    └── Cancer link        (new field: H. pylori → gastric cancer)

⊥ P1  "Stress causes ulcers"                            [m=0.08, 48v]
       Historical record. No new voices since 1990s.
       Kept because deletion would lose the epistemic history.
```

Convergence complete. m(P6) → 0.97 (near certainty).
m(P1) → 0.08 (all but refuted). The tree has a clear answer.

**What BELLA preserved through this 25-year convergence:**

1. **The wrong theory remained in the tree.** It didn't get deleted.
   Historical truth is preserved; wrongness is structural, not invisible.
2. **Mass migration, not replacement.** P1 → 0.08 gradually as
   evidence accumulated on P6. No sudden flip.
3. **DISPUTES are visible.** The contradiction between P1 and P6
   is in the graph, not averaged away.
4. **Root emergence from evidence.** P6 rose to root position because
   its subtree accumulated more coherent evidence, not because
   anyone designated it as root (R3).
5. **Convergence took 25 years.** BELLA doesn't force closure.
   The calculus tolerated the contested state for two decades
   while evidence accumulated.

---

## Case 2: Uncertainty — What killed the dinosaurs?

In 1980, physicist Luis Alvarez proposed that dinosaurs went
extinct because an asteroid struck Earth. The evidence was
striking — a global iridium layer dated to 66 million years ago.

But other scientists argued volcanism (the Deccan Traps in India)
or multi-causal extinction. Forty-five years later, the question
is still debated — and BELLA would show exactly why.

### State: 2026 (current scientific knowledge)

```
P1  "Mass extinction event ~66 million years ago"       [m=0.99, 2000v]
    │   ← this is not contested, it's the fact to explain
    │
    ├── P2  "Non-avian dinosaurs went extinct"          [m=0.99, 1500v]
    ├── P3  "~75% of species lost"                      [m=0.95, 800v]
    ├── P4  "Marine reptiles, ammonites extinct"        [m=0.97, 600v]
    │
    └── CAUSE hypotheses (the contested layer):
        │
        ├── P5  "Asteroid impact"                       [m=0.72, 600v]
        │   │   (Alvarez hypothesis, now majority view)
        │   │
        │   ├── P6  "Global iridium layer at K-Pg boundary"   [m=0.96, 300v]
        │   │       iridium is rare on Earth, common in asteroids
        │   ├── P7  "Chicxulub crater matches timing"         [m=0.91, 150v]
        │   ├── P8  "Shocked quartz at the boundary"          [m=0.89, 80v]
        │   ├── P9  "Tsunami deposits near Gulf of Mexico"    [m=0.86, 40v]
        │   └── P10 "Nuclear-winter climate model fits"       [m=0.74, 60v]
        │
        ├── ⊥ P11 "Deccan Traps volcanism"                    [m=0.58, 250v]
        │   │   (alternative cause — massive volcanic eruptions)
        │   │
        │   ├── P12 "Volcanic activity spans the K-Pg boundary" [m=0.93, 80v]
        │   │       uncontested geological fact
        │   ├── P13 "Volcanism can cause extinction events"     [m=0.85, 50v]
        │   │       (Permian extinction example)
        │   ├── P14 "Eruptions produced ~10^6 km³ basalt"       [m=0.94, 40v]
        │   └── P15 "Sulfur aerosols cooled global climate"     [m=0.71, 40v]
        │
        └── P16 "Multi-causal extinction (impact + volcanism)" [m=0.61, 120v]
            │   (synthesis view — both factors contributed)
            │
            ├── P17 "Species were already stressed before impact" [m=0.72, 60v]
            ├── P18 "Impact was the coup de grâce"                [m=0.65, 40v]
            └── P19 "Recovery patterns show multiple phases"      [m=0.68, 30v]
```

**What BELLA shows here**:

1. **The FACT (extinction) is not contested** — P1-P4 all at m>0.95.
   The question is CAUSE, not occurrence.

2. **Three CAUSE hypotheses coexist** as children of the same parent.
   They're not mutually exclusive at the level of mass — P5 is
   the highest but the others have genuine evidence.

3. **P5 and P11 are in structural tension** (⊥ DISPUTES edge).
   Both have strong sub-evidence. Neither has refuted the other.

4. **P16 (synthesis) exists as a third option.** It doesn't require
   choosing between the other two — it absorbs them.

5. **The mass distribution is informative:**
   ```
   P5  (asteroid):    m=0.72 — leading but not decisive
   P11 (volcanism):   m=0.58 — plausible alternative
   P16 (multi-cause): m=0.61 — compromise gaining ground
   ```
   Sum > 1.0 because these aren't mutually exclusive in BELLA's
   representation — they share evidence (the extinction happened).

6. **No emergence has fired** because no subtree has converged to
   dominance (all three are above 0.5). R3 correctly recognizes
   this as a contested state, not a resolution.

7. **Compare to Case 1 at 1984**: similar shape (contested claims
   in tension) but here the evidence is structurally split rather
   than accumulating toward one side. Time alone won't resolve it —
   the evidence is nearly balanced.

### What would falsify each branch

BELLA makes the falsification conditions explicit. What would
move the mass?

**To raise P5 (asteroid) → 0.9:**
- Evidence that Deccan volcanism occurred BEFORE extinction finished
  (would weaken P11's causal timing)
- Better climate models showing impact alone suffices
- Refinement of extinction timeline to peak at impact moment

**To raise P11 (volcanism) → 0.9:**
- Evidence of extinction starting before Chicxulub impact
- Refined dating showing volcanism correlates better with extinction peak
- Evidence of Permian-style gradual pattern, not sudden collapse

**To raise P16 (multi-cause) → 0.9:**
- Evidence of pre-impact ecosystem stress from volcanism
- Refinement showing recovery patterns consistent with compound cause
- Direct fossil evidence of two-phase extinction

Each of these is a specific claim that would arrive with lr > 1.
BELLA doesn't predict which will turn up. It just says: whichever
accumulates evidence first wins. The structure waits.

---

## Case 3: Fallacy Reversal — Do continents move?

In 1912, German meteorologist Alfred Wegener proposed that the
continents had once been joined in a single supercontinent and
had drifted apart. The idea was ridiculed. Geologists called it
"delirious ravings." Wegener died in 1930 on a Greenland expedition,
his theory still in disrepute.

Fifty years later, plate tectonics became the foundational framework
of modern geology. Wegener was posthumously vindicated. This is a
different arc than H. pylori — the establishment was not uncertain,
it was **confidently wrong**, and a single outsider's observation
had to overcome decades of entrenched counter-belief.

This case shows three things BELLA handles well and most systems
don't: (a) mass migration from confident wrongness, (b) the role of
entity reputation in delaying acceptance, and (c) preservation of
the rejected hypothesis so the historical record survives the reversal.

### State 1: 1910 (pre-Wegener)

```
P1  "Continents are fixed in position"                  [m=0.94, 300v]
    │   A century of geology, global consensus
    │
    ├── P2  "Mountains form by contraction of cooling Earth" [m=0.81, 80v]
    ├── P3  "Similar fossils on separate continents =
    │        land bridges that sank"                         [m=0.68, 40v]
    ├── P4  "Oceans and continents are permanent features"   [m=0.87, 150v]
    └── P5  "No known mechanism could move continents"       [m=0.93, 200v]
             ← the blocking belief, like P5 in H. pylori case
```

Note P3: the fossil evidence was ALREADY known. Same plants and
reptiles on Africa and South America. The establishment's explanation
was "land bridges that later sank" — an auxiliary hypothesis added to
preserve P1. Mass high, but structurally fragile (the auxiliary adds
entropy to the tree).

Entity(geology_establishment).rep ≈ 0.88 — highly credentialed,
widely trusted, centuries of cumulative authority.

### State 2: 1915 (Wegener publishes)

```
P1  "Continents are fixed"                              [m=0.93, 305v]
    │
    ├── P2..P5  (unchanged)
    │
    └── ⊥ P6  "Continents were once joined, have drifted"  [m=0.48, 1v]
              │   Wegener's proposal. ONE voice. Low lr because
              │   no mechanism proposed, outsider source.
              │
              ├── P7  "Fossil patterns match if continents were joined" [m=0.62, 1v]
              ├── P8  "Coastlines of South America and Africa fit"      [m=0.71, 1v]
              ├── P9  "Matching rock formations across Atlantic"        [m=0.58, 1v]
              └── P10 "Glacial deposits align if continents moved"      [m=0.55, 1v]
```

A single voice enters the tree as DENY. P6 has m=0.48 (below
prior because the lr is weak — Wegener was a meteorologist
proposing a geology theory, entity reputation LOW in the relevant
field). The sub-evidence (P7-P10) is genuine but carries only
Wegener's single voice.

**Entity reputation blocks acceptance here.** If Wegener had been
a leading geologist, the same evidence would have had higher lr.
BELLA captures this: lr is modulated by source reputation (§8.2).
A meteorologist is a "mentioned" role in geology (w=0.1), not a
"source" role (w=1.0). Same evidence, 10x less weight.

This is uncomfortable but honest. BELLA isn't saying the
establishment was right to dismiss Wegener. It's saying that
reputation-weighted systems have exactly this failure mode,
and we should be able to see it happening.

### State 3: 1930 (Wegener's death, still rejected)

```
P1  "Continents are fixed"                              [m=0.90, 320v]
    │
    ├── P5  "No known mechanism could move continents"    [m=0.92, 220v]
    │     │   ← still the strongest argument against P6
    │     └── ⊥ P6  (still there)
    │
    └── ⊥ P6  "Continents have drifted"                   [m=0.42, 5v]
              │   Gained 4 voices (Wegener + a few allies)
              │   Still dismissed. Mass actually DROPPED because
              │   mainstream papers published counter-arguments.
              │
              ├── P7-P10 (unchanged)
              └── ⊥ P11 "No physical mechanism can do this"  [m=0.89, 100v]
                       Multiple geophysicists argued the idea
                       violated known physics. Strong DENY on P6.
```

After 18 years, P6 is worse off than when it started. This is
what persistent rejection looks like structurally:
- Mass stuck below prior
- New evidence not arriving (people stopped looking)
- Counter-evidence accumulating (P11)
- Entity reputation of the heretics draining

But — crucially — **P6 is still in the tree.** It wasn't deleted.
The evidence (P7-P10) is still there. When the establishment's
attention returns in a few decades, the tree will remember.

### State 4: 1960 (paleomagnetism + sea-floor spreading)

```
P1  "Continents are fixed"                              [m=0.54, 330v]
    │   Mass DROPPING but still a major branch
    │
    ├── P5  "No known mechanism"                          [m=0.38, 240v]
    │   │   ← collapsing: mechanism is being discovered
    │   │
    │   └── ⊥ P12  "Sea-floor spreading observed"         [m=0.78, 15v]
    │             │   Hess, Dietz 1960-1962. Direct evidence
    │             │   of oceanic crust creation at mid-ocean ridges.
    │             │   DENY on P5 because it PROVIDES a mechanism.
    │             └── ...
    │
P6  "Continents have drifted"                           [m=0.71, 60v]
    │   ← no longer a child of P1. R2 restructure fired.
    │   What was the denied minority is now a competing root.
    │
    ├── P7-P10  (original Wegener evidence, mass rising)
    │           m=0.82, 0.85, 0.78, 0.74 respectively
    │           because new evidence CORROBORATES old evidence
    │
    ├── P13  "Paleomagnetic pole wandering matches drift"  [m=0.81, 20v]
    │          Magnetic record in rocks shows they formed at
    │          different latitudes than where they sit now.
    │          Direct evidence for motion.
    │
    ├── P14  "Mid-ocean ridges match seafloor ages"        [m=0.84, 25v]
    │          Young rock at ridge, old rock at continents.
    │          Exactly what spreading predicts.
    │
    └── P15  "Earthquake belts trace plate boundaries"     [m=0.77, 18v]
             Seismic data reveals the plate edges.
```

This is the tipping point. Between 1950 and 1962, three independent
lines of evidence arrived:
- Paleomagnetism (magnetism frozen in rocks as they cooled)
- Sea-floor spreading (direct observation of oceanic crust creation)
- Earthquake distribution (plate boundaries visible seismically)

None of these existed when Wegener was laughed at. They came from
geophysics — a field that didn't exist in 1915. Wegener's original
evidence (P7-P10) didn't change, but it now fits into a framework
that has a mechanism.

**Notice what happened structurally**:
- P6 is no longer nested under P1 as a DISPUTES child. It broke free.
- Its own subtree grew (P7-P10 rising, P13-P15 added)
- P1's subtree started losing children (P5 was denied)
- Mass of P1 migrated to P6

The R3 emergence mechanism is about to fire — P6's subtree
centroid is converging past the threshold.

### State 5: 1975 (plate tectonics consensus)

```
P6  "Plate tectonics: continents drift on moving plates"  [m=0.96, 800v]
    │   ← now the root. R3 fired. New consensus.
    │
    ├── Mechanism branch    (mantle convection, slab pull)
    ├── Evidence branch     (P7-P15 plus decades of corroboration)
    ├── Predictions branch  (earthquake zones, volcanism, mountain building)
    └── History branch      (paleogeographic reconstructions)

⊥ P1  "Continents are fixed"                              [m=0.06, 330v]
    │   Preserved as low-mass DISPUTES record.
    │   |V|=330 because old literature is still in the tree.
    │   But mass collapsed — the lr of the contrary evidence
    │   dominates the accumulated votes.
    │
    ├── P5  "No mechanism exists"                         [m=0.04, 240v]
    │       Refuted. Mass near zero.
    │
    └── P3  "Land bridges explain fossil patterns"        [m=0.12, 40v]
            The auxiliary hypothesis that propped up P1.
            Rejected because plate tectonics explains it better.
```

63 years after Wegener's original proposal, the reversal is complete.

**What's striking**: The number of voices supporting P1 (|V|=330) is
much higher than the number supporting P6 (|V|=800 — but many are
recent). Mass isn't computed from voice count. Mass is computed from
lr × independence. A single high-quality observation (sea-floor
spreading) had more lr than 300 old literature citations of the
fixed-continent view, because the old citations were all assuming
the thing they were supposedly proving.

**Mass migration took 63 years.** BELLA tolerated the wrong state
for six decades. It didn't force closure. It just kept accumulating
evidence until the mass flipped.

### What this case teaches

**1. Confident wrongness is stable until new evidence arrives.**
The 1930 tree (State 3) was worse for P6 than the 1915 tree
(State 2) — persistent rejection actively erodes minority claims.
BELLA doesn't "eventually figure it out" on its own. It needs
new evidence with enough lr to shift the balance.

**2. Entity reputation delays acceptance.**
Wegener's low reputation in geology (meteorologist outsider)
made his evidence carry less lr. This is a real effect BELLA
models explicitly. A reader of the tree can SEE that P6's
initial mass is suppressed by source weighting — and can ask
"would the mass be different if we re-evaluated without
reputation modulation?" That question is answerable in BELLA.

**3. The rejected hypothesis must be preserved.**
At State 5, P1 is at m=0.06 but still in the tree. Why?
Because future discoveries might vindicate PARTS of it.
Because the historical record matters. Because the ROUTE to
the current belief goes through P1's refutation — students
understand plate tectonics better by seeing what it replaced.

A system that DELETED wrong theories would have no memory that
geology ever believed continents were fixed. BELLA's mass-not-delete
approach preserves the intellectual history.

**4. Mechanism matters more than correlation.**
P5 was the blocker: "no known mechanism could move continents."
The fossils, coastlines, and rock formations were all EVIDENCE,
but without a mechanism, the establishment maintained their view.
What finally flipped the tree wasn't more correlational evidence —
it was the discovery of sea-floor spreading, which provided the
MECHANISM. BELLA handles this through CAUSE relations: P12 was
a cause belief (sea-floor spreading → continental drift), and
CAUSE edges carry more epistemic weight than IMPLIES edges.

**5. Reversal preserves structure, not just labels.**
Compare 1910 (State 1) to 1975 (State 5). The tree didn't just
swap "fixed" for "drifting." The entire CHILD STRUCTURE reorganized.
Fossils moved from being anomalies requiring auxiliary hypotheses
(P3 under P1) to being natural consequences (P7 under P6). This
structural change IS the reversal — not a relabeling.

### Compared to H. pylori

The two convergence cases differ in important ways:

```
                    H. pylori (Case 1)      Continental drift (Case 3)
Starting confidence  m=0.89 (stress theory)   m=0.94 (fixed continents)
Counter-evidence     Direct biopsy + drink    Indirect (fossils, fits)
Time to reverse      ~25 years                ~60 years
Role of reputation   Marshall was a doctor    Wegener was an outsider
Key mechanism        Biopsies → self-exp.     Sea-floor spreading
Fate of old theory   Demoted, preserved       Demoted, preserved
```

The longer timeline for continental drift reflects two things:
(a) Wegener's reputation disadvantage, which suppressed initial lr
and (b) the need for an entirely new field (geophysics) to produce
the mechanism evidence. Marshall had direct access to the patient's
stomach. Wegener had no way to watch continents move.

### The warning this case delivers

This is the case that should make you uncomfortable about trusting
current consensus. Right now, some widely-held scientific belief is
probably wrong, and the evidence that would overturn it is being
dismissed because its proposers have low reputation in the relevant
field. BELLA doesn't tell us which belief that is. It just shows us
the SHAPE — and that shape looks like State 2 (1915) of this tree.

How can you tell State 2 ("correct dismissal of a wrong idea") from
State 2 ("future vindication of an ignored outsider") at the time?
You often can't. BELLA's honest answer is: preserve the minority
claim, track its sub-evidence, don't delete it, and let evidence
accumulate. If it was wrong, the mass stays low forever (nothing
lost). If it was right, the mass eventually flips (Wegener vindicated).

The cost of preserving minority claims is small. The cost of
deleting them is a 60-year delay in accepting correct ideas.
This is why I7 (propositions grow monotonically) is an invariant,
not a convenience.

---

## The Lessons

Reading these three cases together shows BELLA's core claims:

**R1 accumulation**: Mass isn't voted — it's computed from
evidence quality (lr) and independence (|V|). Marshall's ONE
voice drinking the culture had higher lr than 48 voices of
old literature because self-experimentation is strong evidence.
Wegener's ONE voice had LOWER lr than its own merit because
entity reputation modulated his credibility downward (§8 R5).
Both cases show mass is about evidence quality, not popularity.

**R2 structure**: The tree's shape IS the epistemic situation.
A flat tree with one dominant root = settled question.
A tree with three high-mass siblings under a CAUSE node =
genuine scientific contest. A tree with a dominant root AND a
persistent minority DENY child = confident belief with a latent
threat. You can read the state from the shape without looking
at the masses.

**R3 emergence**: Convergence happens when one subtree's
centroid dominates. The H. pylori case shows emergence taking
25 years. The continental drift case shows it taking 60 years.
The dinosaur case shows emergence NOT happening because the
subtree centroids are genuinely distinct. Time is not the
trigger — evidence asymmetry is.

**R5 reputation and its failure mode**: The continental drift
case shows how entity reputation can delay correct ideas.
Wegener was dismissed partly because he was a meteorologist,
not a geologist. BELLA models this explicitly through the
role-weighted entity reputation (§8.2). The failure mode is
honest — you can read the tree and SEE that reputation
suppression is operating, which is the first step toward
correcting it.

**DISPUTES preservation (I7)**: In all three cases, minority
or losing views stay in the tree. BELLA doesn't delete wrong
theories — it demotes them via mass. This is essential for
three reasons:
- **Reversibility**: If new evidence arrives, the demoted
  claim is still there to receive mass (continental drift).
- **Learning from rejection**: The system can say "we considered
  X and rejected it, here's why" instead of forgetting and
  re-litigating.
- **Historical honesty**: The intellectual route to the current
  belief is preserved. Students and researchers can trace how
  we got here.

**No categorical labels**: None of the three trees has "TRUE"
or "FALSE" tags. Mass and structure carry all the information.
"H. pylori causes ulcers" at m=0.97 with 500 voices and no
active DISPUTES means the same thing as calling it a "fact" —
but it's continuously updatable. If new counter-evidence
arrived tomorrow, mass would adjust without any categorical
reassignment.

**The three arcs are not three mechanisms** — they're the same
calculus under different evidence conditions:
- Case 1: uncertain start, asymmetric evidence → convergence
- Case 2: uncertain start, symmetric evidence → persistent uncertainty
- Case 3: confident start, delayed asymmetric evidence → slow reversal

Same six rules. Same operations. The different outcomes reflect
the evidence, not different modes of operation. This is BELLA's
central claim: you don't need different rules for "convergent"
vs "contested" vs "reversing" cases. The rules are the same,
the evidence is what differs.

**Time is not a judge**: The H. pylori case wasn't resolved
because time passed. It was resolved because evidence accumulated.
The dinosaur case has had 45 years and is still contested —
more time doesn't help if the evidence isn't asymmetric.

---

## What these cases would look like TODAY with BELLA live

If BELLA had been running since 1980, ingesting all medical
literature and geology papers:

- **H. pylori**: The tree would have begun restructuring automatically
  around 1985-1990 as evidence accumulated. A researcher querying
  "what causes ulcers?" in 1995 would have seen BOTH theories with
  mass migration visible, instead of having to find Marshall's
  papers manually. Convergence would have been recognized
  structurally, not by consensus conference.

- **Dinosaur extinction**: The current tree would look exactly like
  the one above — three competing hypotheses at roughly balanced
  mass, DISPUTES edges visible, no false forcing of consensus.
  A student asking "what killed the dinosaurs?" would see that
  the answer is "three plausible causes, here's the evidence for
  each" — not a textbook statement that hides the uncertainty.

- **Continental drift**: Wegener's 1915 paper would have landed as
  a DENY child of the fixed-continent root, with low initial mass
  from reputation weighting, but the sub-evidence (P7-P10) would
  have been preserved and searchable. Every subsequent observation
  (glacial patterns, fossil matches, rock formations) would have
  incremented the subtree mass. When paleomagnetism arrived in
  the 1950s, BELLA would have recognized the accumulating mass
  structurally — no human committee needed to "declare" the new
  consensus. The 60-year delay might have been 30 years, or 20.

The point of BELLA is not to DECIDE. It's to show the state of
the evidence honestly: converged where evidence has settled,
contested where evidence is genuinely split, and reversing where
new evidence is accumulating against an old consensus. The
calculus makes all three visible without anyone having to
declare which is happening.

And the fourth possibility — confidently right and staying right —
is just Case 1 at State 5: high mass, many voices, no active
DISPUTES, stable over time. BELLA doesn't need a special mode for
"this is a fact." It just shows the tree, and the tree tells you.


---

## Case 4: Asymmetric Opposition — Is the Earth flat?

This case tests BELLA's ability to discriminate between **evidence**
and **assertion**. The round Earth has 2,500 years of corroborating
observations, direct orbital photography, and a complete predictive
framework. The flat Earth claim has many vocal adherents today
thanks to social media — but exactly zero independent confirming
observations that survive scrutiny.

Question for BELLA: does a claim with many loud voices but no
evidence get high mass?

Answer: no. This is what §2.3 ("Two Measures of Confidence")
is about — mass and |V| are not the same thing, and voices without
lr don't produce mass.

Here is the tree. It is very asymmetric on purpose.

### State: 2026

```
P1  "The Earth is approximately spherical"             [m=0.9996, 10000+v]
    │
    ├── P2  "Eratosthenes measured Earth's circumference (240 BC)"  [m=0.998, 50v]
    │       Shadow angle at Syene vs Alexandria. Off by ~2%.
    │       Geometric argument. Reproducible today.
    │
    ├── P3  "Ships disappear hull-first over the horizon"           [m=0.997, 2000v]
    │       Direct observation, any coastline, any century.
    │       Geometry implies curvature.
    │
    ├── P4  "Lunar eclipse shows Earth's circular shadow"           [m=0.996, 1500v]
    │       Aristotle noted this. Visible during every eclipse.
    │       Only a sphere projects a circular shadow from all angles.
    │
    ├── P5  "Magellan's expedition circumnavigated (1522)"          [m=0.998, 500v]
    │       Continuous westward journey returned to start.
    │       Impossible on a flat plane with an edge.
    │
    ├── P6  "Time zones: sun rises at different times globally"     [m=0.998, 8000v]
    │       Daily confirmation by every person on Earth.
    │       Only a rotating sphere produces this pattern.
    │
    ├── P7  "Gravity pulls toward Earth's center everywhere"        [m=0.997, 3000v]
    │       Plumb lines point toward the same center from every
    │       location. Newton derived this; Einstein refined it.
    │       Every "down" is a different direction.
    │
    ├── P8  "Satellites orbit in predictable paths"                 [m=0.998, 5000v]
    │       GPS depends on sphere+rotation model at millimeter accuracy.
    │       Flat model cannot reproduce the observed orbital mechanics.
    │
    ├── P9  "Photos from orbit (1946 V-2, 1961 Gagarin, 1968 Apollo)" [m=0.997, 800v]
    │       Direct visual observation from multiple independent space
    │       programs (US, USSR, ESA, China, India, Japan, private).
    │       Independent photographic confirmation from adversaries.
    │
    ├── P10 "Southern Hemisphere constellations are different"      [m=0.998, 2000v]
    │       Stars visible from Australia aren't visible from Europe.
    │       Only a sphere produces hemispheric viewing asymmetry.
    │
    ├── P11 "Coriolis effect observed in weather and ballistics"    [m=0.994, 500v]
    │       Rotating sphere produces predictable deflection.
    │       Artillery and storm tracking depend on it.
    │
    └── P12 "Bedford Level Experiment, corrected (Wallace 1870)"    [m=0.992, 30v]
            Originally designed by flat-earther Samuel Rowbotham to
            PROVE flat earth. When controlled for atmospheric refraction
            by Alfred Russel Wallace, it measured curvature correctly.
            The canonical self-refutation: the experiment meant to
            disprove curvature, when done properly, measured it.


⊥ P13  "The Earth is flat"                              [m=0.003, 5000+v]
    │   HIGH voice count (social media era), near-zero mass.
    │   Why? Because none of the sub-claims survive DENY.
    │
    ├── P14  "I can't see the curvature from the ground"   [m=0.38, 5000v]
    │        │   Common flat-earth argument.
    │        │   Why mass < 0.5: most sub-evidence DENIES it.
    │        │
    │        └── ⊥ P15  "Curvature drops ~8 inches per mile squared"  [m=0.996, 40v]
    │                   Geometric calculation. At human height on
    │                   flat ground, the curvature over 1 mile is
    │                   BELOW visual acuity. You literally can't see
    │                   it from ground level — and that's what the
    │                   sphere model predicts.
    │                   P14 is not evidence of P13; it's consistent
    │                   with P1. The absence of visible curvature
    │                   at ground level CONFIRMS the sphere model.
    │
    ├── P16  "Space photos are CGI/faked"                [m=0.08, 2000v]
    │        │
    │        ├── ⊥ P17  "Photos come from 14+ independent nations"     [m=0.998, 100v]
    │        │        US, USSR, ESA, China, India, Japan, Israel,
    │        │        Iran, North Korea, private companies. Adversarial
    │        │        nations with no incentive to collude on a shared lie.
    │        │
    │        └── ⊥ P18  "ISS observable with amateur telescopes"       [m=0.995, 300v]
    │                   Anyone can verify ISS transit across the sky.
    │                   The object is physically there.
    │
    ├── P17  "Horizon always looks flat"                 [m=0.25, 3000v]
    │        │
    │        └── ⊥ P19  "Horizon drops below eye level with altitude"  [m=0.992, 200v]
    │                   From a plane at 35,000 ft, horizon is measurably
    │                   below level — exact angle matches sphere model.
    │                   Pilots use this for attitude verification.
    │
    ├── P20  "Gravity is fake; things just fall 'down'"  [m=0.04, 1500v]
    │        │
    │        ├── ⊥ P21  "Orbital mechanics require inverse-square law" [m=0.999, 5000v]
    │        │        Kepler's laws, Newton's derivation, GPS accuracy,
    │        │        every space mission ever. Flat model has no
    │        │        explanation for orbital prediction.
    │        │
    │        └── ⊥ P22  "Pendulum period varies with latitude"         [m=0.994, 100v]
    │                   Observed fact. Matches spheroid model (slight
    │                   oblateness). Flat model has no explanation.
    │
    ├── P23  "Antarctica is an ice wall at the edge"     [m=0.05, 1000v]
    │        │
    │        ├── ⊥ P24  "Flights over Antarctica exist"                [m=0.998, 500v]
    │        │        Direct flights Sydney→Santiago, science flights,
    │        │        adventure tourism. No wall encountered.
    │        │
    │        └── ⊥ P25  "24-hour Antarctic daylight in summer"         [m=0.998, 300v]
    │                   Geometrically impossible on a flat disc with
    │                   a central sun. Trivially derivable on a sphere.
    │
    └── P26  "Water always finds its level; oceans are flat"  [m=0.15, 800v]
             │
             └── ⊥ P27  "Tidal bulges caused by gravity"          [m=0.996, 500v]
                        Ocean height varies by meters globally.
                        Tides match the sphere+gravity model exactly.
                        "Water finds its level" is true locally and
                        false globally — and the global curvature
                        matches Earth's radius to millimeter precision
                        via satellite altimetry.
```

### What this tree shows

**The mass asymmetry is enormous**: m(P1)=0.9996 vs m(P13)=0.003.
That's a ratio of ~333:1 in Jaynes log-odds, or about 3 nats of
evidence difference.

**|V| does not rescue P13**: 5000 flat-earth voices cannot raise
the mass because each "voice" adds lr ≈ 1.0 (no new evidence,
just assertion) or even lr < 1.0 (when the assertion has been
specifically denied). Adding voices to a claim without adding
evidence is structural noise.

This is **§2.3 ("Two Measures of Confidence")** in action:

```
P1:   m=0.9996, |V|=10000+   high evidence, many independent sources
P13:  m=0.003,  |V|=5000+    many voices, near-zero evidence
```

Both have high |V|. Only P1 has mass. Because mass is
σ(Σ log lr), and adding voices with lr ≈ 1 contributes log(1) = 0
to the sum. A million people asserting "the Earth is flat" without
evidence produces a million × 0 = 0 contribution to Λ.

**Every sub-claim is explicitly denied, not ignored**:

| Flat-earth claim | BELLA response |
|---|---|
| Can't see curvature | DENIED — matches sphere prediction (too small to see at human height) |
| Photos are faked | DENIED — 14+ independent space programs, amateur ISS observation |
| Horizon looks flat | DENIED — measurably drops with altitude (pilots verify) |
| Gravity is fake | DENIED — orbital mechanics, pendulum latitude variation |
| Antarctic wall | DENIED — flights exist, 24-hour daylight impossible on disc |
| Water finds its level | DENIED — tides, satellite altimetry |

Each DENY is another claim in the tree with its own evidence.
The flat claim isn't dismissed — it's **examined sub-claim by
sub-claim**, and every sub-claim fails the evidence test.

**Bedford Level Experiment (P12) is the most instructive entry**:
It was originally designed in 1838 by a flat-earther (Samuel
Rowbotham) to prove the Earth flat. When Alfred Russel Wallace
redid it in 1870 with proper controls for atmospheric refraction,
it measured curvature correctly. The experiment a flat-earther
built to disprove curvature, done properly, PROVED curvature.

In BELLA: P12 is a CONFIRM for P1 with extraordinarily high lr
(because it's an adversarial experiment — a test designed by the
opposition that reverses the opposition's conclusion). Adversarial
confirmations carry more epistemic weight than friendly ones.

### Why this isn't "the system taking sides"

Some readers might worry that BELLA just encodes whatever the
mainstream view is. But look at what the tree actually does:

1. **Each flat-earth sub-claim is preserved and listed explicitly.**
   Nothing is deleted. A flat-earther can read the tree and see
   their own arguments represented faithfully.

2. **Each sub-claim has a specific, structural denial** — not "this
   is wrong because experts said so," but "this specific observation
   contradicts this specific claim, here is the calculation."

3. **The mass comes from the calculation, not from authority.**
   If a flat-earther produced a new observation that actually
   survived scrutiny (say, a satellite that detected a disc-edge),
   that would be a CONFIRM claim for P13 with high lr, and the
   mass would shift. BELLA is not blocking flat-earth evidence —
   it's saying **the evidence doesn't exist yet**.

4. **Adversarial confirmations are weighted heavily.** The Bedford
   Level Experiment (P12) is the strongest anti-flat evidence
   precisely because it came from the flat-earth side. BELLA
   rewards this, not the mainstream side.

5. **The tree is transparent.** A reader can trace exactly why
   each claim has the mass it has. No hidden weights, no opaque
   "trust me," just accumulated evidence with visible lineage.

### Compared to the other cases

```
                    Evidence         Voices        Mass ratio
Case 1 (H. pylori)  asymmetric→      converged     500:5 (25 years)
Case 2 (dinosaurs)  symmetric        split         1:1:1 (still)
Case 3 (drift)      delayed asym.    establishment 100:1 (60 years)
Case 4 (flat earth) extreme asym.    contemporary  10000:5 (forever?)
```

Case 4 is structurally different from Case 3 in an important way.
Wegener was DISMISSED despite having real evidence. Flat-earthers
are DIS-REPRESENTED despite having many voices. Case 3 was a
reputation failure that delayed a correct minority view. Case 4
is reputation working correctly: voices without evidence produce
voices without mass.

If flat earth were a Wegener-style case, BELLA should show mass
slowly rising for P13 over decades as evidence accumulated. It
doesn't. Mass has stayed near zero because no new sub-evidence
has arrived that survives scrutiny. 

**This is the critical test for any epistemic system**: can it
distinguish between "minority view with real evidence" (Wegener)
and "minority view with no evidence but many voices" (flat Earth)?

Most systems cannot — they either deferentially treat all
minority views as potentially valid (false balance) or dismiss
them by authority (false certainty). BELLA handles both cases
with the same calculus:

- Wegener's evidence at 1915: real observations, 1 voice,
  lr > 1 but suppressed by reputation weighting. Mass low but
  preserved. When more evidence arrives, mass rises.
- Flat earth at 2026: non-evidence, 5000 voices, lr ≈ 1 for
  assertions or lr < 1 for refuted claims. Mass near zero.
  If real evidence arrived, mass would rise. It hasn't.

Same rules, different outcomes, because the evidence is different.
Not the authority. Not the votes. **The evidence.**

### The answer to "prove it to a flat-earther"

The question in the previous session was: "we need a clean tree
to explain this to flat-earthers."

The tree above is that explanation. It doesn't say "you're wrong
because scientists said so." It says:

> Here are your specific claims. Here is the specific evidence
> for each. Here is what would need to be true for each claim to
> have mass. Here is what's missing. The calculation does not
> rely on any authority — you can redo it yourself with any
> observations you can make.

A flat-earther who reads the tree and disagrees has to disagree
with specific calculations and specific observations, not with
"the establishment." That's a productive disagreement. If they
find a flaw in P15's geometric calculation, or P18's amateur
telescope observation, the mass will move. BELLA welcomes that.

What BELLA doesn't accept is "lots of people on YouTube say X"
as evidence. Because that's not evidence — that's voice count
without lr. And §2.3 exists precisely to prevent this kind of
error.

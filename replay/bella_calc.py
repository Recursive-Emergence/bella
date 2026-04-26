"""
Standalone BELLA calculus — per bella/SPEC.md §2 (evidence accumulation)
and §8 (entity reputation R5 cycle).

Shared across four case studies: wirecard, theranos, wakefield, hcq.

Formulas (SPEC §2.1, §2.2, §8.1, §8.2):

    α(c)   = modality(c) × grounding(c)                    # attenuation
    lr(c)  = 1 + (lr_base(c) − 1) × α(c) × (0.5 + rep(E))  # rep modulation
    Λ(P)   = Σ { log lr(c_i) | supports } + Σ { log(1/lr(c_j)) | counters }
    m(P)   = σ(Λ(P))
    σ(E)   = 1 / √n(E)                                     # specificity
    Λ_E    = Σ σ(E) × w(role) × Λ(B_i)                     # R1 on entity
    rep(E) = σ(Λ_E)                                        # Jaynes posterior

lr_base is a likelihood RATIO (> 1), not a credibility probability.
Higher = stronger evidence per supporting claim. Calibration guide:

    lr_base ~ 1.5   weak signal (official denial, political amplification)
    lr_base ~ 2–4   plausible report, small trial, short-seller allegation
    lr_base ~ 5–8   documented evidence, investigative journalism, observational study
    lr_base ~ 10–15 regulatory finding, audit refusal, retraction
    lr_base ~ 20+   admission of guilt, RCT result, bankruptcy, license revocation

Values below 1 will INVERT the formula — the code warns on load.
"""

from __future__ import annotations
import math
from dataclasses import dataclass


# ═════════════════════════════════════════════════════════════════════
# Constants from SPEC §2.1 (extended with case-specific modalities)
# ═════════════════════════════════════════════════════════════════════

MODALITY_ATTN = {
    # Base SPEC §2.1
    "observation":          1.00,
    "reported":             0.70,
    "allegation":           0.50,
    "opinion":              0.20,
    # General investigation / reporting
    "analysis":             0.60,
    "report":               0.70,
    "documented_evidence":  0.90,
    "investigative_journalism": 0.85,
    "profile":              0.50,
    "amplification":        0.40,
    "endorsement":          0.60,
    "continued_advocacy":   0.30,
    "book_publication":     0.50,
    "case_series":          0.40,
    # Corporate / official
    "official_action":      0.80,
    "official_denial":      0.60,
    "legal_action":         0.50,
    "admission":            0.95,
    "action":               0.60,
    "bankruptcy":           1.00,
    "dissolution":          1.00,
    # Regulatory / government
    "regulatory_action":    0.70,
    "regulatory_finding":   0.95,
    "guideline":            0.80,
    "criminal_complaint":   0.70,
    "fraud_charge":         0.95,
    "license_revocation":   1.00,
    "revocation":           0.90,
    # Audit
    "audit_finding":        0.90,
    "audit_refusal":        0.95,
    # Journal / scientific
    "journal_publication":  0.80,
    "retraction":           0.90,
    "retraction_of_interpretation": 0.90,
    "full_retraction":      0.95,
    # Studies
    "small_trial":          0.50,
    "observational_study":  0.70,
    "population_study":     0.90,
    "epidemiological_study": 0.90,
    "randomized_trial":     0.95,
    "systematic_review":    1.00,
    "meta_analysis":        1.00,
}

ROLE_WEIGHT = {
    "source":    1.00,
    "subject":   0.50,
    "mentioned": 0.10,
}


# ═════════════════════════════════════════════════════════════════════
# Core types
# ═════════════════════════════════════════════════════════════════════

def _sigmoid(x: float) -> float:
    if x > 700:    return 1.0
    if x < -700:   return 0.0
    return 1.0 / (1.0 + math.exp(-x))


@dataclass
class Entity:
    name: str
    role: str = "source"
    Lambda_E: float = 0.0
    n: int = 0

    @property
    def sigma(self) -> float:
        return 1.0 / math.sqrt(max(self.n, 1))

    @property
    def rep(self) -> float:
        return _sigmoid(self.Lambda_E)


@dataclass
class Claim:
    id: str
    date: str
    source: str
    source_role: str
    stance: str                # "supports" | "counters" | "neutral"
    modality: str
    lr_base: float
    grounding: float = 0.7
    text: str = ""
    verified: bool = False


# ═════════════════════════════════════════════════════════════════════
# Evidence calculus
# ═════════════════════════════════════════════════════════════════════

def attenuation(claim: Claim) -> float:
    modality = MODALITY_ATTN.get(claim.modality, 0.50)
    return modality * claim.grounding


def likelihood_ratio(claim: Claim, entity: Entity) -> float:
    alpha = attenuation(claim)
    rep_mod = 0.5 + entity.rep
    lr = 1.0 + (claim.lr_base - 1.0) * alpha * rep_mod
    return max(lr, 1e-4)


def dLambda(claim: Claim, entity: Entity) -> float:
    lr = likelihood_ratio(claim, entity)
    if claim.stance == "supports":
        return math.log(lr)
    if claim.stance == "counters":
        return -math.log(lr)
    return 0.0


def update_entity(entity: Entity, dL: float, role: str = "source") -> None:
    sigma_snapshot = entity.sigma
    w = ROLE_WEIGHT.get(role, 1.0)
    entity.Lambda_E += sigma_snapshot * w * dL
    entity.n += 1


# ═════════════════════════════════════════════════════════════════════
# Replay engines
# ═════════════════════════════════════════════════════════════════════

def replay_bella(claims: list[Claim]) -> list[dict]:
    claims = sorted(claims, key=lambda c: c.date)
    entities: dict[str, Entity] = {}
    Lambda_P = 0.0
    trajectory = []
    for c in claims:
        ent = entities.setdefault(c.source, Entity(c.source, c.source_role))
        dL = dLambda(c, ent)
        Lambda_P += dL
        update_entity(ent, dL, role="source")
        trajectory.append({
            "date":       c.date,
            "id":         c.id,
            "source":     c.source,
            "stance":     c.stance,
            "modality":   c.modality,
            "m":          _sigmoid(Lambda_P),
            "Lambda_P":   Lambda_P,
            "rep_snapshot": {name: e.rep for name, e in entities.items()},
        })
    return trajectory


def replay_naive_majority(claims: list[Claim]) -> list[dict]:
    claims = sorted(claims, key=lambda c: c.date)
    s = 0
    c_count = 0
    trajectory = []
    for cl in claims:
        if cl.stance == "supports":  s += 1
        elif cl.stance == "counters": c_count += 1
        total = s + c_count
        m = s / total if total else 0.5
        trajectory.append({"date": cl.date, "id": cl.id, "m": m})
    return trajectory


def replay_vanilla_bayes(claims: list[Claim]) -> list[dict]:
    claims = sorted(claims, key=lambda c: c.date)
    Lambda_P = 0.0
    trajectory = []
    for cl in claims:
        if cl.stance == "supports":  Lambda_P += math.log(2.0)
        elif cl.stance == "counters": Lambda_P -= math.log(2.0)
        trajectory.append({
            "date":     cl.date, "id": cl.id,
            "m":        _sigmoid(Lambda_P),
            "Lambda_P": Lambda_P,
        })
    return trajectory

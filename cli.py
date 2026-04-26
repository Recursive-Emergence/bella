"""BELLA CLI — process claims into belief structures.

Usage:
  bella perceive --query "impeach"              # process claims matching query
  bella perceive --page pg_c584596c             # process claims from a page
  bella perceive --field bel_abc123             # add claims to existing field
  bella gene bel_abc123                         # display gene from any belief
  bella gene --roots                            # display all field roots
  bella status                                  # show belief/claim/edge counts
  bella reset                                   # clear all beliefs (careful!)
"""

import argparse
import asyncio
import hashlib
import json
import logging
import math
import os
import re
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'here'))

from here.services.neo4j_service import Neo4jService
from here.services.llm_gateway import LLMGateway, ModelTier
from here.domain.belief import Belief, BeliefRelation, EvidenceStance, Evidence
from here.domain.types import Claim, Entity
from here.fabric.belief_ops import (
    upsert_belief, set_relation, add_evidence,
    get_roots, get_children, hydrate_gene,
)
from here.fabric.grow_match import _get_embeddings, cosine_similarity

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Proven firmware (RNA)
# ---------------------------------------------------------------------------

FIRMWARE = '''KB:
{kb}
Claim: "{claim}"
Reply with ONE JSON object:
{{"op":"CONFIRM","id":<n>}}
{{"op":"AMEND","id":<n>,"desc":"added detail"}}
{{"op":"ADD","id":{next_n},"parent":<n>,"desc":"who did what"}}
{{"op":"CAUSE","id":{next_n},"effect":<n>,"desc":"prior event that triggered it"}}
{{"op":"DENY","id":{next_n},"parent":<n>,"desc":"who did what"}}
{{"op":"NEW","id":{next_n},"desc":"who did what"}}'''

FIRST_CLAIM = '''Claim: "{claim}"
Reply with exactly two JSON lines:
{{"op":"NEW","id":1,"desc":"topic in five words"}}
{{"op":"ADD","id":2,"parent":1,"desc":"specific fact from claim"}}'''


# ---------------------------------------------------------------------------
# Embedding + LLM
# ---------------------------------------------------------------------------

EMB_CACHE = {}


def get_emb(text):
    if text in EMB_CACHE:
        return EMB_CACHE[text]
    e = _get_embeddings([text])
    r = e[0] if e and e[0] else None
    EMB_CACHE[text] = r
    return r


LLM_CACHE = {}
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'cli_cache.json')
COST = 0.0
CALLS = 0


def load_cache():
    global LLM_CACHE
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            LLM_CACHE = json.load(f)


def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(LLM_CACHE, f, indent=2)


TIER = ModelTier.POWERFUL  # default; --model flag overrides
DIRECT_MODEL = None  # set to model ID for direct API calls


async def call_llm(prompt, gw):
    global COST, CALLS
    model_tag = DIRECT_MODEL or TIER.value
    key = hashlib.md5((prompt + model_tag).encode()).hexdigest()
    if key in LLM_CACHE:
        return LLM_CACHE[key]

    if DIRECT_MODEL and DIRECT_MODEL.startswith('claude'):
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=DIRECT_MODEL, max_tokens=80, temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        result = resp.content[0].text.strip()
        inp, out = resp.usage.input_tokens, resp.usage.output_tokens
        cost = inp * 15.0 / 1e6 + out * 75.0 / 1e6
        COST += cost
        CALLS += 1
        log.info(f"LLM [{DIRECT_MODEL}] {inp}in/{out}out ${cost:.4f}")
    elif DIRECT_MODEL:
        from openai import OpenAI
        client = OpenAI()
        oai_params = dict(
            model=DIRECT_MODEL, temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        # GPT-5+ uses max_completion_tokens
        if '5' in DIRECT_MODEL or '4.1' in DIRECT_MODEL:
            oai_params['max_completion_tokens'] = 80
        else:
            oai_params['max_tokens'] = 40
        resp = client.chat.completions.create(**oai_params)
        result = resp.choices[0].message.content.strip()
        inp = resp.usage.prompt_tokens
        out = resp.usage.completion_tokens
        cost = inp * 10.0 / 1e6 + out * 30.0 / 1e6  # approx gpt-5 pricing
        COST += cost
        CALLS += 1
        log.info(f"LLM [{DIRECT_MODEL}] {inp}in/{out}out ${cost:.4f}")
    else:
        resp = await gw.complete(
            tier=TIER,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, max_tokens=80, purpose="bella_cli")
        COST += getattr(resp, 'estimated_cost_usd', 0.0)
        CALLS += 1
        result = resp.content.strip()

    LLM_CACHE[key] = result

    save_cache()
    return result


# ---------------------------------------------------------------------------
# Parse
# ---------------------------------------------------------------------------

def parse(raw):
    """Parse JSON LLM response. Returns (action, target_n, new_n, desc)."""
    line = raw.strip().split('\n')[0].strip()

    # Extract JSON from line (LLM may prefix with text)
    start = line.find('{')
    if start >= 0:
        try:
            obj = json.loads(line[start:])
        except json.JSONDecodeError:
            # Try to fix common issues: trailing text after }
            end = line.rfind('}')
            if end > start:
                try:
                    obj = json.loads(line[start:end+1])
                except json.JSONDecodeError:
                    obj = {}
            else:
                obj = {}
    else:
        obj = {}

    op = obj.get('op', '').upper()
    desc = obj.get('desc', '')
    n = obj.get('id')
    parent = obj.get('parent')
    effect = obj.get('effect')

    if op == 'CONFIRM':
        return 'CONFIRM', n, None, None
    elif op == 'AMEND':
        return 'AMEND', n, None, desc
    elif op == 'ADD' and parent is not None:
        return 'CHILD', parent, n, desc
    elif op == 'CAUSE' and effect is not None:
        return 'CAUSE', effect, n, desc
    elif op == 'DENY' and parent is not None:
        return 'COUNTER', parent, n, desc
    elif op == 'NEW' or n is not None:
        return 'ROOT', None, n, desc or raw[:40]
    else:
        return 'ROOT', None, None, desc or raw[:40]


# ---------------------------------------------------------------------------
# In-memory gene (working state during processing)
# ---------------------------------------------------------------------------

class WorkingGene:
    def __init__(self):
        self.nodes = {}
        self.roots = []
        self.next_n = 1

    def add(self, n, desc, parent=None, rel='→', voice='', emb=None,
            entity_ids=None, event_time=None, lr=1.0):
        self.nodes[n] = {
            'desc': desc[:60], 'parent': parent, 'rel': rel,
            'children': [], 'voices': set(), 'embedding': emb,
            'belief_id': None,
            'entity_ids': set(entity_ids or []),
            'time': event_time,
            'log_odds': 0.0,
        }
        if voice:
            self._accumulate(n, voice, lr)
        self.next_n = max(self.next_n, n + 1)
        if parent and parent in self.nodes:
            self.nodes[parent]['children'].append(n)
        else:
            self.roots.append(n)

    def insert_cause(self, n, desc, effect_n, voice='', emb=None,
                     entity_ids=None, event_time=None, lr=1.0):
        """Insert cause node ABOVE effect: cause becomes parent of effect.

        Before: grandparent → effect
        After:  grandparent → cause →c effect
        """
        effect = self.nodes[effect_n]
        grandparent = effect['parent']

        # Create cause node where effect was
        self.nodes[n] = {
            'desc': desc[:60], 'parent': grandparent, 'rel': '→',
            'children': [effect_n], 'voices': set(), 'embedding': emb,
            'belief_id': None,
            'entity_ids': set(entity_ids or []),
            'time': event_time,
            'log_odds': 0.0,
        }
        if voice:
            self._accumulate(n, voice, lr)
        self.next_n = max(self.next_n, n + 1)

        # Reparent: effect becomes child of cause
        if grandparent and grandparent in self.nodes:
            gp = self.nodes[grandparent]
            gp['children'] = [n if c == effect_n else c for c in gp['children']]
        elif effect_n in self.roots:
            self.roots = [n if r == effect_n else r for r in self.roots]

        effect['parent'] = n
        effect['rel'] = '→c'

    def _accumulate(self, n, voice, lr):
        """Jaynes evidence accumulation with marginal verification."""
        nd = self.nodes[n]
        if voice in nd['voices']:
            lr = 1.0 + (lr - 1.0) * 0.1  # same voice = 10% weight
        nd['voices'].add(voice)
        if lr > 0 and lr != 1.0:
            nd['log_odds'] += math.log(lr)

    def mass(self, n):
        """σ(Λ) — Jaynes posterior for node n."""
        x = self.nodes[n]['log_odds']
        if x > 20: return 1.0
        if x < -20: return 0.0
        return 1.0 / (1.0 + math.exp(-x))

    def confirm(self, n, voice='', lr=1.0):
        if n in self.nodes:
            self._accumulate(n, voice, lr)

    def amend(self, n, detail='', voice='', lr=1.0):
        if n in self.nodes:
            if voice:
                self._accumulate(n, voice, lr)
            if detail:
                self.nodes[n]['desc'] = f"{self.nodes[n]['desc']}; {detail}"[:60]

    def render(self, entities=None):
        """Render gene text. entities = {eid: Entity} for name lookup."""
        ent_map = entities or {}
        lines = []
        def show(n, depth=0):
            nd = self.nodes[n]
            pad = '  ' * depth
            rel_sym = '⊥ ' if nd['rel'] == '⊥' else '→c ' if nd['rel'] == '→c' else ''
            v = len(nd['voices'])
            m = self.mass(n)
            meta = []
            meta.append(f'm={m:.2f}')
            if v > 1: meta.append(f'{v}v')
            if nd.get('time'): meta.append(nd['time'])
            eids = sorted(nd.get('entity_ids', set()))[:3]
            ent_names = []
            for eid in eids:
                e = ent_map.get(eid)
                ent_names.append(e.canonical_name.split()[-1] if e else eid[-6:])
            if ent_names: meta.append('+'.join(ent_names))
            meta_str = f' [{", ".join(meta)}]'
            lines.append(f"{pad}{rel_sym}P{n}: \"{nd['desc']}\"{meta_str}")
            for cn in nd['children']:
                show(cn, depth + 1)
        for r in self.roots:
            show(r)
        return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Pull claims from Neo4j
# ---------------------------------------------------------------------------

PULL_CLAIMS = """
    MATCH (c:Claim)-[:ASSERTED_IN]->(p:Page {where})
    RETURN c {{.*, page_id: p.id, domain: p.domain}} as claim
    ORDER BY c.tree_depth
"""

PULL_ENTITIES = """
    UNWIND $eids AS eid
    MATCH (e:Entity {id: eid})
    RETURN e.id as id, e.canonical_name as name,
           e.entity_type as type, e.wikidata_qid as qid
"""


async def pull_claims(neo4j, *, query=None, page_id=None):
    """Pull Claim domain objects with resolved Entity data."""
    if page_id:
        records = await neo4j._execute_read("""
            MATCH (c:Claim)-[:ASSERTED_IN]->(p:Page {id: $pid})
            RETURN c {.*, page_id: p.id, domain: p.domain} as claim
            ORDER BY c.tree_depth
        """, {'pid': page_id})
    elif query:
        records = await neo4j._execute_read("""
            MATCH (c:Claim)-[:ASSERTED_IN]->(p:Page)
            WHERE toLower(c.text) CONTAINS toLower($q)
            RETURN c {.*, page_id: p.id, domain: p.domain} as claim
            ORDER BY p.domain, c.tree_depth
        """, {'q': query})
    else:
        return [], {}

    # Build Claim domain objects
    claims = []
    all_entity_ids = set()
    for r in records:
        row = dict(r['claim'])
        row.setdefault('id', row.get('cid', ''))
        claim = Claim.from_neo4j_row(row)
        claims.append(claim)
        all_entity_ids.update(claim.entity_ids)

    # Bulk-fetch Entity domain objects
    entities = {}
    if all_entity_ids:
        ent_records = await neo4j._execute_read(PULL_ENTITIES, {'eids': list(all_entity_ids)})
        for er in ent_records:
            entities[er['id']] = Entity(
                id=er['id'],
                canonical_name=er['name'] or '',
                entity_type=er['type'] or 'PERSON',
                wikidata_qid=er.get('qid'),
            )

    return claims, entities


# ---------------------------------------------------------------------------
# Process claims through kernel
# ---------------------------------------------------------------------------

AUTO_CONFIRM = 0.88


async def process_claims(claims, gene, entities, gw):
    """Process Claim domain objects into gene, return assignments.

    claims: List[Claim]  — proper domain objects
    entities: Dict[str, Entity]  — entity_id → Entity for name lookup
    """
    assignments = {}

    for i, claim in enumerate(claims):
        text = claim.text
        voice = claim.source_name or ''
        emb = get_emb(text)
        eids = claim.entity_ids[:3]
        lr = claim.lr_page or 1.0

        # Precision-aware time: year→"1967", month→"1967-02", day→"2026-04-07"
        prec = (claim.when_data or {}).get('precision', 'day')
        if claim.event_time:
            if prec == 'year':
                time = claim.event_time[:4]
            elif prec == 'month':
                time = claim.event_time[:7]
            else:
                time = claim.event_time[:10]
        else:
            time = None

        # Build entity/time context string for LLM prompt
        context = ''
        ent_names = [entities[eid].canonical_name for eid in eids if eid in entities]
        if ent_names:
            context += f' [{", ".join(ent_names)}]'
        if time:
            context += f' ({time})'

        # Stage 1: empty → first claim
        kb_text = gene.render(entities)
        if not kb_text.strip():
            prompt = FIRST_CLAIM.format(claim=f"{text}{context}"[:250])
            raw = await call_llm(prompt, gw)
            lines = [l.strip() for l in raw.strip().split('\n') if l.strip()]

            root_parsed = parse(lines[0]) if lines else ('ROOT', None, 1, text[:40])
            child_parsed = parse(lines[1]) if len(lines) > 1 else None

            root_n = root_parsed[2] or gene.next_n
            root_desc = root_parsed[3] or text[:40]
            for prefix in ['1. ⊢ P1 "', '2. ⊢ P2 →P1 "', '⊢ P1 "']:
                if root_desc.startswith(prefix):
                    root_desc = root_desc[len(prefix):].rstrip('"')
            gene.add(root_n, root_desc, entity_ids=eids, event_time=time)

            if child_parsed and child_parsed[0] in ('CHILD', 'ROOT'):
                child_n = child_parsed[2] or gene.next_n
                child_desc = child_parsed[3] or text[:40]
                for prefix in ['2. ⊢ P2 →P1 "', '⊢ P2 →P1 "']:
                    if child_desc.startswith(prefix):
                        child_desc = child_desc[len(prefix):].rstrip('"')
                gene.add(child_n, child_desc, parent=root_n, voice=voice,
                         emb=emb, entity_ids=eids, event_time=time, lr=lr)
                action = 'CHILD'
                target_n = child_n
            else:
                gene._accumulate(root_n, voice, lr)
                gene.nodes[root_n]['embedding'] = emb
                action = 'ROOT'
                target_n = root_n
        else:
            # Stage 2: auto-confirm
            best_sim, best_n = 0, None
            for n, nd in gene.nodes.items():
                if nd.get('embedding'):
                    sim = cosine_similarity(emb, nd['embedding'])
                    if sim > best_sim:
                        best_sim, best_n = sim, n

            if best_sim >= AUTO_CONFIRM and best_n:
                gene.confirm(best_n, voice, lr)
                gene.nodes[best_n]['entity_ids'].update(eids)
                action, target_n = 'CONFIRM', best_n
            else:
                # Stage 3: LLM with entity/time context
                prompt = FIRMWARE.format(
                    kb=kb_text, claim=f"{text}{context}"[:250],
                    next_n=gene.next_n)
                raw = await call_llm(prompt, gw)
                act, target, new_n, desc = parse(raw)

                if act == 'CONFIRM' and target in gene.nodes:
                    gene.confirm(target, voice, lr)
                    gene.nodes[target]['entity_ids'].update(eids)
                    action, target_n = 'CONFIRM', target
                elif act == 'AMEND' and target in gene.nodes:
                    gene.amend(target, desc, voice, lr)
                    gene.nodes[target]['entity_ids'].update(eids)
                    action, target_n = 'AMEND', target
                elif act == 'CAUSE' and target in gene.nodes:
                    n = new_n or gene.next_n
                    gene.insert_cause(n, desc or '?', target, voice, emb,
                                      entity_ids=eids, event_time=time, lr=lr)
                    action, target_n = 'CAUSE', n
                elif act in ('CHILD', 'COUNTER') and target in gene.nodes:
                    n = new_n or gene.next_n
                    rel = '⊥' if act == 'COUNTER' else '→'
                    eff_lr = 1.0 / max(lr, 0.01) if act == 'COUNTER' else lr
                    gene.add(n, desc or '?', target, rel, voice, emb,
                             entity_ids=eids, event_time=time, lr=eff_lr)
                    action, target_n = act, n
                else:
                    n = new_n or gene.next_n
                    gene.add(n, desc or text[:40], voice=voice, emb=emb,
                             entity_ids=eids, event_time=time, lr=lr)
                    action, target_n = 'ROOT', n

        # Track assignment
        stance_map = {
            'CONFIRM': EvidenceStance.CONFIRMS,
            'AMEND': EvidenceStance.SUPPORTS,
            'CHILD': EvidenceStance.SUPPORTS,
            'CAUSE': EvidenceStance.SUPPORTS,
            'COUNTER': EvidenceStance.COUNTERS,
            'ROOT': EvidenceStance.SUPPORTS,
        }
        assignments[claim.id] = (target_n, stance_map.get(action, EvidenceStance.SUPPORTS), lr)

        log.info(f"  {action:12s} P{target_n} (lr={lr:.2f}) \"{text[:55]}\"")

    return assignments


# ---------------------------------------------------------------------------
# Gene compression — the gene's own metabolism
# ---------------------------------------------------------------------------

COMPRESS_PROMPT = '''Gene:
{gene}

Output JSON lines. Only real duplicates and obvious missing connections:
{{"op":"MERGE","keep":<n>,"remove":<n>}}
{{"op":"LINK","child":<n>,"parent":<n>}}
{{"op":"CAUSE","cause":<n>,"effect":<n>}}'''


async def compress_gene(gene, entities, gw):
    """Post-page compression: merge duplicate nodes in the gene.

    One LLM call to identify duplicates, then mechanical merge.
    Returns number of merges performed.
    """
    if len(gene.nodes) < 6:
        return 0  # too small to have duplicates

    rendered = gene.render(entities)
    prompt = COMPRESS_PROMPT.format(gene=rendered)

    # Need more tokens for merge list output
    global COST, CALLS
    model_tag = DIRECT_MODEL or TIER.value
    key = hashlib.md5((prompt + model_tag + '_compress').encode()).hexdigest()
    if key in LLM_CACHE:
        raw = LLM_CACHE[key]
    elif DIRECT_MODEL and DIRECT_MODEL.startswith('claude'):
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=DIRECT_MODEL, max_tokens=200, temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        inp, out = resp.usage.input_tokens, resp.usage.output_tokens
        cost = inp * 15.0 / 1e6 + out * 75.0 / 1e6
        COST += cost
        CALLS += 1
        log.info(f"LLM [compress] {inp}in/{out}out ${cost:.4f}")
        LLM_CACHE[key] = raw
        save_cache()
    elif DIRECT_MODEL:
        from openai import OpenAI
        client = OpenAI()
        oai_params = dict(
            model=DIRECT_MODEL, temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        if '5' in DIRECT_MODEL or '4.1' in DIRECT_MODEL:
            oai_params['max_completion_tokens'] = 200
        else:
            oai_params['max_tokens'] = 200
        resp = client.chat.completions.create(**oai_params)
        raw = resp.choices[0].message.content.strip()
        inp = resp.usage.prompt_tokens
        out = resp.usage.completion_tokens
        cost = inp * 10.0 / 1e6 + out * 30.0 / 1e6
        COST += cost
        CALLS += 1
        log.info(f"LLM [compress] {inp}in/{out}out ${cost:.4f}")
        LLM_CACHE[key] = raw
        save_cache()
    else:
        resp = await gw.complete(
            tier=TIER,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, max_tokens=200, purpose="bella_compress")
        COST += getattr(resp, 'estimated_cost_usd', 0.0)
        CALLS += 1
        raw = resp.content.strip()
        LLM_CACHE[key] = raw
        save_cache()

    # Parse JSON compression instructions
    ops = 0
    gene.merge_map = getattr(gene, 'merge_map', {})
    gene.deleted_belief_ids = getattr(gene, 'deleted_belief_ids', [])

    for line in raw.split('\n'):
        start = line.find('{')
        if start < 0:
            continue
        end = line.rfind('}')
        if end <= start:
            continue
        try:
            obj = json.loads(line[start:end+1])
        except json.JSONDecodeError:
            continue

        op = obj.get('op', '').upper()

        if op == 'MERGE':
            keep_n, remove_n = obj.get('keep'), obj.get('remove')
            if (keep_n in gene.nodes and remove_n in gene.nodes
                    and keep_n != remove_n):
                keeper = gene.nodes[keep_n]
                removed = gene.nodes[remove_n]
                keeper['voices'].update(removed['voices'])
                keeper['entity_ids'].update(removed['entity_ids'])
                keeper['log_odds'] += removed['log_odds']
                if not keeper.get('embedding') and removed.get('embedding'):
                    keeper['embedding'] = removed['embedding']
                if not keeper.get('time') and removed.get('time'):
                    keeper['time'] = removed['time']
                for cn in removed['children']:
                    if cn in gene.nodes:
                        gene.nodes[cn]['parent'] = keep_n
                        if cn not in keeper['children']:
                            keeper['children'].append(cn)
                pn = removed['parent']
                if pn and pn in gene.nodes:
                    gene.nodes[pn]['children'] = [
                        c for c in gene.nodes[pn]['children'] if c != remove_n]
                if remove_n in gene.roots:
                    gene.roots = [r for r in gene.roots if r != remove_n]
                if removed.get('belief_id'):
                    gene.deleted_belief_ids.append(removed['belief_id'])
                del gene.nodes[remove_n]
                gene.merge_map[remove_n] = keep_n
                ops += 1
                log.info(f"  merge P{remove_n} into P{keep_n}")

        elif op == 'LINK':
            child_n, parent_n = obj.get('child'), obj.get('parent')
            if (child_n in gene.nodes and parent_n in gene.nodes
                    and child_n in gene.roots):
                nd = gene.nodes[child_n]
                gene.roots = [r for r in gene.roots if r != child_n]
                nd['parent'] = parent_n
                nd['rel'] = '→'
                gene.nodes[parent_n]['children'].append(child_n)
                ops += 1
                log.info(f"  link P{child_n} under P{parent_n}")

        elif op == 'CAUSE':
            cause_n, effect_n = obj.get('cause'), obj.get('effect')
            if (cause_n in gene.nodes and effect_n in gene.nodes
                    and cause_n in gene.roots):
                effect_nd = gene.nodes[effect_n]
                cause_nd = gene.nodes[cause_n]
                gp = effect_nd['parent']
                gene.roots = [r for r in gene.roots if r != cause_n]
                if gp and gp in gene.nodes:
                    gene.nodes[gp]['children'] = [
                        cause_n if c == effect_n else c
                        for c in gene.nodes[gp]['children']]
                elif effect_n in gene.roots:
                    gene.roots = [cause_n if r == effect_n else r
                                  for r in gene.roots]
                cause_nd['parent'] = gp
                cause_nd['rel'] = '→'
                effect_nd['parent'] = cause_n
                effect_nd['rel'] = '→c'
                cause_nd['children'].append(effect_n)
                ops += 1
                log.info(f"  cause P{cause_n} of P{effect_n}")

    return ops


# ---------------------------------------------------------------------------
# Write to Neo4j
# ---------------------------------------------------------------------------

UPSERT_INVOLVES = """
    MATCH (b:Belief {id: $bid})
    MATCH (e:Entity {id: $eid})
    MERGE (b)-[:INVOLVES]->(e)
"""


async def write_to_neo4j(gene, assignments, neo4j):
    """Write beliefs + evidence + INVOLVES edges to Neo4j."""
    written = 0

    # 1. Upsert belief nodes (with Jaynes log_odds from accumulation)
    for n, nd in gene.nodes.items():
        belief = Belief(
            id=Belief.make_id(nd['desc'], str(nd.get('parent'))),
            desc=nd['desc'],
            voices=nd['voices'],
            embedding=nd.get('embedding'),
        )
        belief.log_odds = nd.get('log_odds', 0.0)
        await upsert_belief(neo4j, belief)
        nd['belief_id'] = belief.id
        written += 1

    # 2. IMPLIES/DISPUTES edges between beliefs
    for n, nd in gene.nodes.items():
        if nd['parent'] and nd['parent'] in gene.nodes:
            pid = gene.nodes[nd['parent']].get('belief_id')
            if pid and nd.get('belief_id'):
                rel = BeliefRelation.DISPUTES if nd['rel'] == '⊥' else BeliefRelation.IMPLIES
                await set_relation(neo4j, nd['belief_id'], pid, rel)

    # 3. Claim→Belief evidence edges (with actual lr from claim)
    merge_map = getattr(gene, 'merge_map', {})
    for cid, (node_n, stance, lr) in assignments.items():
        # Follow merge redirects
        while node_n in merge_map:
            node_n = merge_map[node_n]
        if node_n in gene.nodes:
            bid = gene.nodes[node_n].get('belief_id')
            if bid:
                await add_evidence(neo4j, Evidence(
                    claim_id=cid, belief_id=bid,
                    stance=stance, lr=lr))

    # 4. Belief→Entity INVOLVES edges
    involves_count = 0
    for n, nd in gene.nodes.items():
        bid = nd.get('belief_id')
        if not bid:
            continue
        for eid in nd.get('entity_ids', set()):
            await neo4j._execute_write(UPSERT_INVOLVES, {'bid': bid, 'eid': eid})
            involves_count += 1

    if involves_count:
        log.info(f"  {involves_count} INVOLVES edges written.")

    # 5. Delete merged-away beliefs from Neo4j
    deleted_ids = getattr(gene, 'deleted_belief_ids', [])
    if deleted_ids:
        await neo4j._execute_write("""
            UNWIND $ids AS bid
            MATCH (b:Belief {id: bid})
            DETACH DELETE b
        """, {'ids': deleted_ids})
        log.info(f"  {len(deleted_ids)} merged beliefs deleted from Neo4j.")

    return written


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def get_existing_roots(neo4j):
    """Get existing field roots with embeddings for matching."""
    result = await neo4j._execute_read("""
        MATCH (b:Belief)
        WHERE NOT (b)-[:IMPLIES|DISPUTES]->()
        RETURN b.id as id, b.desc as desc, b.embedding as emb, b.n_voices as nv
        ORDER BY b.n_voices DESC
    """, {})
    return result


async def hydrate_field_gene(neo4j, root_id):
    """Hydrate a field's gene from Neo4j for merging."""
    gene = WorkingGene()
    result = await neo4j._execute_read("""
        MATCH (b:Belief)-[:IMPLIES|DISPUTES*0..5]->(root:Belief {id: $rid})
        WITH DISTINCT b
        OPTIONAL MATCH (b)-[r:IMPLIES|DISPUTES]->(parent:Belief)
        RETURN b.id as id, b.desc as desc, b.n_voices as nv,
               b.embedding as emb, parent.id as parent_id, type(r) as rel
    """, {'rid': root_id})

    id_to_n = {}
    for rec in result:
        n = gene.next_n
        id_to_n[rec['id']] = n
        parent_n = id_to_n.get(rec.get('parent_id'))
        rel = '⊥' if rec.get('rel') == 'DISPUTES' else '→'
        gene.add(n, rec['desc'] or '?', parent=parent_n, rel=rel,
                 emb=rec.get('emb'))
        gene.nodes[n]['belief_id'] = rec['id']
        nv = rec.get('nv') or 0
        for i in range(nv):
            gene.nodes[n]['voices'].add(f'v{i}')

    return gene


async def cmd_perceive(args):
    global TIER, DIRECT_MODEL
    aliases = {
        'opus': 'claude-opus-4-6',
        'sonnet': None, 'gpt4o': None, 'mini': None,
        'gpt5': 'gpt-5', 'gpt5.4': 'gpt-5.4', 'gpt4.1': 'gpt-4.1',
    }
    tier_map = {'sonnet': ModelTier.POWERFUL, 'gpt4o': ModelTier.STANDARD, 'mini': ModelTier.CHEAP}
    if args.model in aliases:
        DIRECT_MODEL = aliases[args.model]
        if not DIRECT_MODEL:
            TIER = tier_map[args.model]
    else:
        DIRECT_MODEL = args.model  # pass raw model ID
    log.info(f"Model: {DIRECT_MODEL or args.model}")

    neo4j = Neo4jService()
    await neo4j.connect()
    gw = LLMGateway()
    load_cache()

    claims, entities = await pull_claims(
        neo4j, query=args.query, page_id=args.page)
    if not claims:
        log.error("No claims found. Need --query or --page")
        await neo4j.close()
        return

    # Sort by event_time so LLM sees temporal order (helps →c)
    claims.sort(key=lambda c: c.event_time or '9999')

    log.info(f"{len(claims)} claims, {len(entities)} entities\n")

    # Show entity map
    for eid, ent in entities.items():
        log.info(f"  {ent.entity_type[:3]:3s} {ent.canonical_name}"
                 + (f" ({ent.wikidata_qid})" if ent.wikidata_qid else ""))

    for c in claims:
        get_emb(c.text)

    # ── Stage 1: build mini gene from page claims ──
    log.info("\nStage 1: local perception...")
    mini_gene = WorkingGene()
    mini_assignments = await process_claims(claims, mini_gene, entities, gw)

    log.info(f"\nMini gene ({len(mini_gene.nodes)} beliefs):")
    log.info(mini_gene.render(entities))

    # ── Stage 2: match mini gene against existing fields ──
    log.info(f"\nStage 2: matching against existing fields...")
    existing_roots = await get_existing_roots(neo4j)

    if not existing_roots or args.fresh:
        log.info("  No existing fields. Creating new.")
        gene = mini_gene
        assignments = mini_assignments
    else:
        # Match ALL mini gene nodes against ALL existing beliefs
        all_existing = await neo4j._execute_read("""
            MATCH (b:Belief)
            WHERE b.embedding IS NOT NULL
            OPTIONAL MATCH (b)-[:IMPLIES|DISPUTES*0..10]->(root:Belief)
            WHERE NOT (root)-[:IMPLIES|DISPUTES]->()
            RETURN b.id as id, b.desc as desc, b.embedding as emb,
                   collect(DISTINCT root.id)[0] as root_id
        """, {})

        matched_root = None
        best_sim = 0

        for mini_n, mini_nd in mini_gene.nodes.items():
            mini_emb = mini_nd.get('embedding')
            if not mini_emb:
                continue
            for eb in all_existing:
                if eb.get('emb'):
                    sim = cosine_similarity(mini_emb, eb['emb'])
                    if sim > best_sim:
                        best_sim = sim
                        matched_root = eb.get('root_id') or eb['id']
                        matched_desc = eb['desc']

        if matched_root and best_sim > 0.55:
            log.info(f"  Match: \"{matched_desc[:50]}\" (sim={best_sim:.3f})")
            log.info(f"  Merging into field rooted at {matched_root}...")

            gene = await hydrate_field_gene(neo4j, matched_root)
            log.info(f"  Hydrated {len(gene.nodes)} existing beliefs")

            # Pre-compress: clean up prior duplicates before LLM sees them
            pre_h = len(gene.nodes)
            n_pre = await compress_gene(gene, entities, gw)
            if n_pre:
                log.info(f"  Pre-compressed: {pre_h} → {len(gene.nodes)} ({n_pre} merges)")

            assignments = await process_claims(claims, gene, entities, gw)

            log.info(f"\nMerged gene ({len(gene.nodes)} beliefs):")
            log.info(gene.render(entities))
        else:
            log.info(f"  No match (best sim={best_sim:.3f}). Creating new field.")
            gene = mini_gene
            assignments = mini_assignments

    # ── Compress: gene metabolism ──
    pre = len(gene.nodes)
    n_merges = await compress_gene(gene, entities, gw)
    if n_merges:
        log.info(f"\nCompressed: {pre} → {len(gene.nodes)} beliefs ({n_merges} merges)")
        log.info(gene.render(entities))

    # ── Write ──
    if not args.dry_run:
        log.info(f"\nWriting to Neo4j...")
        n = await write_to_neo4j(gene, assignments, neo4j)
        log.info(f"{n} beliefs + {len(assignments)} evidence edges written.")
    else:
        log.info(f"\n(dry run)")

    await neo4j.close()
    log.info(f"\n{CALLS} LLM calls, ${COST:.3f}")


async def cmd_gene(args):
    neo4j = Neo4jService()
    await neo4j.connect()

    if args.roots:
        roots = await get_roots(neo4j)
        log.info(f"{len(roots)} roots:\n")
        for r in roots:
            gene = await hydrate_gene(neo4j, r.id, depth=args.depth)
            log.info(gene)
            log.info('')
    elif args.belief_id:
        gene = await hydrate_gene(neo4j, args.belief_id, depth=args.depth)
        log.info(gene)
    else:
        log.error("Need belief_id or --roots")

    await neo4j.close()


async def cmd_status(args):
    neo4j = Neo4jService()
    await neo4j.connect()

    counts = {}
    for label, query in [
        ('Beliefs', 'MATCH (b:Belief) RETURN count(b) as n'),
        ('IMPLIES', 'MATCH ()-[r:IMPLIES]->() RETURN count(r) as n'),
        ('DISPUTES', 'MATCH ()-[r:DISPUTES]->() RETURN count(r) as n'),
        ('Evidence', 'MATCH ()-[r:CONFIRMS]->() RETURN count(r) as n'),
        ('Roots', 'MATCH (b:Belief) WHERE NOT (b)-[:IMPLIES|DISPUTES]->() RETURN count(b) as n'),
    ]:
        r = await neo4j._execute_read(query, {})
        counts[label] = r[0]['n']
        log.info(f"  {label:12s} {r[0]['n']}")

    await neo4j.close()


async def cmd_reset(args):
    if not args.confirm:
        log.error("Add --confirm to actually delete all beliefs")
        return
    neo4j = Neo4jService()
    await neo4j.connect()
    await neo4j._execute_write("MATCH (b:Belief) DETACH DELETE b", {})
    log.info("All beliefs deleted.")
    await neo4j.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='BELLA CLI')
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('perceive', help='Process claims into beliefs')
    p.add_argument('--query', '-q', help='Search claims by text')
    p.add_argument('--page', '-p', help='Process claims from page ID')
    p.add_argument('--dry-run', action='store_true', help='Don\'t write to Neo4j')
    p.add_argument('--fresh', action='store_true', help='Ignore existing fields, create new')
    p.add_argument('--model', '-m',
                   default='opus', help='opus (default)|sonnet|gpt4o|gpt5.4|<model-id>')

    g = sub.add_parser('gene', help='Display gene from belief')
    g.add_argument('belief_id', nargs='?', help='Belief ID to center on')
    g.add_argument('--roots', action='store_true', help='Show all roots')
    g.add_argument('--depth', type=int, default=3, help='Max depth')

    sub.add_parser('status', help='Show counts')

    r = sub.add_parser('reset', help='Clear all beliefs')
    r.add_argument('--confirm', action='store_true')

    args = parser.parse_args()

    if args.command == 'perceive':
        asyncio.run(cmd_perceive(args))
    elif args.command == 'gene':
        asyncio.run(cmd_gene(args))
    elif args.command == 'status':
        asyncio.run(cmd_status(args))
    elif args.command == 'reset':
        asyncio.run(cmd_reset(args))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

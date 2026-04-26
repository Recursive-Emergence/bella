"""BELLA — four concurrent processes, one belief tree.

  sense   Land → match → insert claims (Sonnet, per-claim)
  bond    Social signals: stakes, votes, posts (future)
  heal    Entropy-triggered restructure (Opus, per-window)
  reflect Self-observation, parameter tuning (Opus, rare)

  tree    Display belief tree with vital signs
  status  Counts + entropy metrics
  reset   Clear all beliefs

Usage:
  python bella/grow.py sense --page pg_c584596c
  python bella/grow.py heal
  python bella/grow.py tree
  python bella/grow.py status
"""

import argparse
import asyncio
import hashlib
import json
import math
import os
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'here'))

from here.services.neo4j_service import Neo4jService
from here.domain.types import Claim, Entity
from here.fabric.grow_match import _get_embeddings, cosine_similarity
from here.repositories.belief_embedding_repository import BeliefEmbeddingRepository

import asyncpg

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PG pool — pgvector ANN for land()
# ---------------------------------------------------------------------------

_pg_pool = None
_belief_repo = None


async def get_belief_repo():
    """Lazy-init PG pool + belief repo."""
    global _pg_pool, _belief_repo
    if _belief_repo is None:
        _pg_pool = await asyncpg.create_pool(
            host=os.getenv('POSTGRES_HOST'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            min_size=1, max_size=3,
        )
        _belief_repo = BeliefEmbeddingRepository(_pg_pool)
    return _belief_repo


async def close_pg():
    global _pg_pool, _belief_repo
    if _pg_pool:
        await _pg_pool.close()
        _pg_pool = None
        _belief_repo = None


# ---------------------------------------------------------------------------
# LLM — two tiers
# ---------------------------------------------------------------------------

CALLS = {'simple': 0, 'complex': 0}
COST = 0.0


SYSTEM_JSON = "You are a belief-tree builder. Respond with ONLY valid JSON, no explanation or analysis."


def _call_anthropic(model, prompt, max_tokens):
    global COST
    import anthropic
    c = anthropic.Anthropic()
    r = c.messages.create(
        model=model, max_tokens=max_tokens, temperature=0.0,
        system=SYSTEM_JSON,
        messages=[{"role": "user", "content": prompt}],
    )
    text = r.content[0].text.strip()
    cost = r.usage.input_tokens * (15.0 if 'opus' in model else 3.0) / 1e6 \
         + r.usage.output_tokens * (75.0 if 'opus' in model else 15.0) / 1e6
    COST += cost
    log.info(f"  LLM [{model.split('-')[1]}] {r.usage.input_tokens}in/{r.usage.output_tokens}out ${cost:.4f}")
    return text


def call_simple(prompt):
    CALLS['simple'] += 1
    return _call_anthropic("claude-sonnet-4-6", prompt, 80)


def call_complex(prompt, max_tokens=500):
    CALLS['complex'] += 1
    return _call_anthropic("claude-opus-4-6", prompt, max_tokens)


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

EMB_CACHE = {}


def get_emb(text):
    if text not in EMB_CACHE:
        e = _get_embeddings([text])
        EMB_CACHE[text] = e[0] if e and e[0] else None
    return EMB_CACHE[text]


# ---------------------------------------------------------------------------
# Pull claims from Neo4j
# ---------------------------------------------------------------------------

async def pull_claims(neo4j, page_id):
    """Pull claims with CHILD_OF tree structure and v2 relations."""
    records = await neo4j._execute_read("""
        MATCH (c:Claim)-[:ASSERTED_IN]->(p:Page {id: $pid})
        OPTIONAL MATCH (c)-[r:CHILD_OF]->(parent:Claim)
        RETURN c {.*, page_id: p.id, domain: p.domain} as claim,
               parent.id as parent_cid, r.relation as tree_rel
        ORDER BY c.tree_depth
    """, {'pid': page_id})

    claims = []
    all_eids = set()
    # Map: claim_id → {parent_cid, tree_rel} from CHILD_OF edges
    tree_map = {}
    for r in records:
        row = dict(r['claim'])
        row.setdefault('id', row.get('cid', ''))
        claim = Claim.from_neo4j_row(row)
        claims.append(claim)
        all_eids.update(claim.entity_ids)
        # Override parent from CHILD_OF edge (more reliable than property)
        if r.get('parent_cid'):
            tree_map[claim.id] = {
                'parent': r['parent_cid'],
                'rel': r['tree_rel'] or claim.relation or 'supports',
            }

    entities = {}
    if all_eids:
        for er in await neo4j._execute_read("""
            UNWIND $eids AS eid
            MATCH (e:Entity {id: eid})
            RETURN e.id as id, e.canonical_name as name, e.entity_type as type
        """, {'eids': list(all_eids)}):
            entities[er['id']] = er['name'] or er['id']

    claims.sort(key=lambda c: c.tree_depth or 0)
    return claims, entities, tree_map


# ---------------------------------------------------------------------------
# LAND — entity overlap + embedding → landing spot
# ---------------------------------------------------------------------------

async def land(neo4j, claim_emb):
    """Find best landing belief — PG ANN O(log n), two-level search.

    Level 1: root subtree centroids → which field?
    Level 2: individual beliefs within that field → where exactly?
    """
    if not claim_emb:
        return None, 0.0

    repo = await get_belief_repo()

    # Level 1: nearest root subtree centroid (field-level aboutness)
    fields = await repo.nearest_fields(claim_emb, top_k=3, min_similarity=0.3)
    if fields:
        best_field = fields[0]
        # Level 2: within that field, get member IDs from Neo4j, search in PG
        members = await neo4j._execute_read("""
            MATCH (b:Belief)-[:IMPLIES|DISPUTES*0..10]->(root:Belief {id: $rid})
            RETURN b.id as id
        """, {'rid': best_field['belief_id']})
        field_ids = [r['id'] for r in members] + [best_field['belief_id']]
        hits = await repo.nearest_in_field(claim_emb, field_ids, top_k=3)
        if hits:
            return hits[0]['belief_id'], hits[0]['similarity']
        # Field found but no individual match — return field root
        return best_field['belief_id'], best_field['similarity']

    # Fallback: global search (no field match)
    hits = await repo.nearest_beliefs(claim_emb, top_k=3)
    if hits:
        return hits[0]['belief_id'], hits[0]['similarity']

    return None, 0.0


# ---------------------------------------------------------------------------
# WINDOW — local context from Neo4j
# ---------------------------------------------------------------------------

async def get_roots(neo4j):
    """Get all root beliefs (no parent)."""
    return await neo4j._execute_read("""
        MATCH (b:Belief)
        WHERE NOT (b)-[:IMPLIES|DISPUTES]->()
        RETURN b.id as id, b.desc as desc
        ORDER BY b.n_voices DESC
    """, {})


async def get_window(neo4j, center_id):
    """Get center belief + parent + siblings + children."""
    if not center_id:
        return []

    rows = await neo4j._execute_read("""
        MATCH (center:Belief {id: $cid})
        RETURN center.id as id, center.desc as desc, 'center' as role, null as rel
        UNION ALL
        MATCH (center:Belief {id: $cid})-[:IMPLIES|DISPUTES]->(parent:Belief)
        RETURN parent.id as id, parent.desc as desc, 'parent' as role, null as rel
        UNION ALL
        MATCH (center:Belief {id: $cid})-[:IMPLIES|DISPUTES]->(parent:Belief)
              <-[r:IMPLIES|DISPUTES]-(sib:Belief)
        WHERE sib.id <> $cid
        RETURN sib.id as id, sib.desc as desc, 'sibling' as role, type(r) as rel
        UNION ALL
        MATCH (child:Belief)-[r:IMPLIES|DISPUTES]->(center:Belief {id: $cid})
        RETURN child.id as id, child.desc as desc, 'child' as role, type(r) as rel
    """, {'cid': center_id})
    return rows


def render_window(rows, roots=None):
    """Render roots + local window as compact text for LLM."""
    lines = []

    # Show all roots first — the "depth 0 picture"
    local_ids = {r['id'] for r in rows}
    if roots:
        lines.append("Roots:")
        for r in roots:
            marker = " *" if r['id'] in local_ids else ""
            lines.append(f"  {r['id'][-8:]}: \"{r['desc'][:50]}\"{marker}")
        lines.append("")

    # Then local window
    parent, center, siblings, children = None, None, [], []
    for r in rows:
        role = r['role']
        entry = f"{r['id'][-8:]}: \"{r['desc'][:50]}\""
        if r.get('rel') == 'DISPUTES':
            entry = "⊥ " + entry
        if role == 'parent':
            parent = entry
        elif role == 'center':
            center = entry
        elif role == 'sibling':
            siblings.append(entry)
        elif role == 'child':
            children.append(entry)

    if parent or center or siblings or children:
        lines.append("Local:")
    if parent:
        lines.append(f"  {parent}")
    if center:
        lines.append(f"    > {center}")
    for s in siblings:
        lines.append(f"    {s}")
    for c in children:
        lines.append(f"      {c}")

    return '\n'.join(lines) if lines else '(empty)'


# ---------------------------------------------------------------------------
# PLACE — Sonnet: match/insert one claim
# ---------------------------------------------------------------------------

PLACE_PROMPT = '''{window}
Claim: "{claim}"
Respond with ONLY a JSON object, no other text:
{{"op":"CONFIRM","id":"<id>"}}
{{"op":"AMEND","id":"<id>","desc":"detail"}}
{{"op":"ADD","parent":"<id>","desc":"factual claim"}}
{{"op":"CAUSE","effect":"<id>","desc":"prior event"}}
{{"op":"DENY","parent":"<id>","desc":"opposing fact"}}
{{"op":"NEW","desc":"new factual claim"}}'''

FIRST_PROMPT = '''New claim: "{claim}"

Respond with exactly two JSON objects on separate lines. "desc" must be factual statements, not analysis.
{{"op":"NEW","desc":"specific topic of this claim"}}
{{"op":"ADD","parent":"<id from line 1>","desc":"key fact from the claim"}}'''


def parse_action(raw):
    """Parse JSON from LLM response."""
    # Strip markdown fences
    text = raw.strip().replace('```json', '').replace('```', '').strip()
    for line in text.split('\n'):
        start = line.find('{')
        end = line.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(line[start:end+1])
            except json.JSONDecodeError:
                continue
    return None  # caller handles failure


def make_belief_id(desc, parent_id=None):
    seed = f"{desc}|{parent_id or 'root'}"
    return f"bel_{hashlib.md5(seed.encode()).hexdigest()[:8]}"


async def place(neo4j, claim, claim_emb, landing_id, landing_sim, entities, dry_run=False):
    """Place one claim into the belief tree. Returns (op, belief_id)."""
    text = claim.text
    eids = claim.entity_ids[:3]
    lr = claim.lr_page or 1.0
    voice = claim.source_name or ''
    et = claim.event_time  # propagate to belief
    ent_names = [entities.get(eid, eid[-6:]) for eid in eids]
    prec = (claim.when_data or {}).get('precision', 'day')
    time = None
    if claim.event_time:
        time = claim.event_time[:4] if prec == 'year' else \
               claim.event_time[:7] if prec == 'month' else \
               claim.event_time[:10]

    context_parts = []
    if ent_names:
        context_parts.append(f"[{', '.join(ent_names)}]")
    if time:
        context_parts.append(f"({time})")
    context = ' '.join(context_parts)
    claim_text = f"{text} {context}".strip()[:250]

    # ── SIMPLE: auto-confirm at very high similarity ──
    if landing_sim >= 0.90 and landing_id:
        if not dry_run:
            await neo4j._execute_write("""
                MATCH (b:Belief {id: $bid})
                SET b.log_odds = b.log_odds + $lr_log,
                    b.n_voices = b.n_voices + 1
            """, {'bid': landing_id, 'lr_log': math.log(lr) if lr > 0 and lr != 1.0 else 0.0})
            await _write_confirms(neo4j, claim.id, landing_id, lr, 'CONFIRMS')
        log.info(f"  SIMPLE  confirm {landing_id[-8:]} (sim={landing_sim:.2f})")
        return 'CONFIRM', landing_id

    # ── Empty tree: first claim ──
    window_rows = await get_window(neo4j, landing_id) if landing_id else []
    if not window_rows and not landing_id:
        raw = call_simple(FIRST_PROMPT.format(claim=claim_text))
        text_clean = raw.strip().replace('```json', '').replace('```', '').strip()
        lines = [l for l in text_clean.split('\n') if l.strip()]
        root_act = parse_action(lines[0]) if lines else None
        if not root_act:
            root_act = {'desc': text[:40]}
        root_id = make_belief_id(root_act.get('desc', text[:30]))
        if not dry_run:
            await _write_belief(neo4j, root_id, root_act.get('desc', text[:30]), claim_emb, event_time=et)
        log.info(f"  NEW     root {root_id[-8:]} \"{root_act.get('desc', '')[:50]}\"")

        if len(lines) > 1:
            child_act = parse_action(lines[1])
            if not child_act:
                child_act = {'desc': text[:40]}
            child_id = make_belief_id(child_act.get('desc', text[:30]), root_id)
            if not dry_run:
                await _write_belief(neo4j, child_id, child_act.get('desc', text[:30]), claim_emb, event_time=et)
                await _write_edge(neo4j, child_id, root_id, 'IMPLIES', claim_emb)
                await _write_confirms(neo4j, claim.id, child_id, lr, 'CONFIRMS')
                await _write_involves(neo4j, child_id, eids)
            log.info(f"  ADD     {child_id[-8:]} under {root_id[-8:]} \"{child_act.get('desc', '')[:50]}\"")
            return 'ADD', child_id

        if not dry_run:
            await _write_confirms(neo4j, claim.id, root_id, lr, 'CONFIRMS')
            await _write_involves(neo4j, root_id, eids)
        return 'NEW', root_id

    # ── LIKELY: Sonnet places it (with expansion on NEW) ──
    roots = await get_roots(neo4j)
    window_text = render_window(window_rows, roots)
    raw = call_simple(PLACE_PROMPT.format(window=window_text, claim=claim_text))
    act = parse_action(raw)
    if not act:
        log.info(f"  SKIP    (parse failed) \"{text[:50]}\"")
        return 'SKIP', None
    op = act.get('op', 'NEW').upper()

    # ── Expand window if NEW — zoom out before creating orphan ──
    if op == 'NEW' and roots and len(roots) > 0:
        # Show full top-2 levels of ALL roots
        expanded = await neo4j._execute_read("""
            MATCH (root:Belief)
            WHERE NOT (root)-[:IMPLIES|DISPUTES]->()
            OPTIONAL MATCH (child:Belief)-[r:IMPLIES|DISPUTES]->(root)
            RETURN root.id as id, root.desc as desc, 'root' as role, null as rel
            UNION ALL
            MATCH (root:Belief)
            WHERE NOT (root)-[:IMPLIES|DISPUTES]->()
            MATCH (child:Belief)-[r:IMPLIES|DISPUTES]->(root)
            RETURN child.id as id, child.desc as desc, 'child' as role, type(r) as rel
        """, {})
        if expanded:
            expanded_text = render_window(expanded)
            raw2 = call_simple(PLACE_PROMPT.format(
                window=expanded_text, claim=claim_text))
            act2 = parse_action(raw2)
            if act2 and act2.get('op', 'NEW').upper() != 'NEW':
                act = act2
                op = act['op'].upper()
                all_known_expanded = expanded + window_rows + [{'id': r['id']} for r in roots]
                log.info(f"  EXPAND  (NEW→{op})")
            else:
                log.info(f"  EXPAND  (still NEW — genuinely new topic)")

    # Extract the referenced belief ID (short hash → full ID lookup)
    ref_short = act.get('id') or act.get('parent') or act.get('effect')
    ref_id = None
    all_known = window_rows + [{'id': r['id']} for r in roots]
    if 'all_known_expanded' in locals():
        all_known = all_known_expanded
    if ref_short:
        for r in all_known:
            if r['id'].endswith(str(ref_short).replace('P', '')) or \
               r['id'] == ref_short or \
               r['id'][-6:] == str(ref_short).replace('P', ''):
                ref_id = r['id']
                break
        if not ref_id:
            ref_id = ref_short  # might be full ID

    desc = act.get('desc', '')

    if op == 'CONFIRM' and ref_id:
        if not dry_run:
            await neo4j._execute_write("""
                MATCH (b:Belief {id: $bid})
                SET b.log_odds = b.log_odds + $lr_log,
                    b.n_voices = b.n_voices + 1
            """, {'bid': ref_id, 'lr_log': math.log(lr) if lr > 0 and lr != 1.0 else 0.0})
            await _write_confirms(neo4j, claim.id, ref_id, lr, 'CONFIRMS')
        log.info(f"  CONFIRM {ref_id[-8:]} \"{text[:50]}\"")
        return 'CONFIRM', ref_id

    elif op == 'AMEND' and ref_id:
        if not dry_run:
            await neo4j._execute_write("""
                MATCH (b:Belief {id: $bid})
                SET b.log_odds = b.log_odds + $lr_log,
                    b.n_voices = b.n_voices + 1,
                    b.desc = b.desc + '; ' + $detail
            """, {'bid': ref_id, 'lr_log': math.log(lr) if lr > 0 and lr != 1.0 else 0.0,
                  'detail': desc[:30]})
            await _write_confirms(neo4j, claim.id, ref_id, lr, 'SUPPORTS')
        log.info(f"  AMEND   {ref_id[-8:]} +\"{desc[:40]}\"")
        return 'AMEND', ref_id

    elif op == 'ADD' and ref_id:
        bid = make_belief_id(desc, ref_id)
        if not dry_run:
            await _write_belief(neo4j, bid, desc, claim_emb, lr, voice, event_time=et)
            await _write_edge(neo4j, bid, ref_id, 'IMPLIES', claim_emb)
            await _write_confirms(neo4j, claim.id, bid, lr, 'CONFIRMS')
            await _write_involves(neo4j, bid, eids)
        log.info(f"  ADD     {bid[-8:]} under {ref_id[-8:]} \"{desc[:50]}\"")
        return 'ADD', bid

    elif op == 'CAUSE' and ref_id:
        bid = make_belief_id(desc, ref_id)
        if not dry_run:
            eff_parent = await neo4j._execute_read("""
                MATCH (eff:Belief {id: $eid})-[r:IMPLIES|DISPUTES]->(p:Belief)
                RETURN p.id as pid, type(r) as rel
            """, {'eid': ref_id})
            parent_id = eff_parent[0]['pid'] if eff_parent else None

            await _write_belief(neo4j, bid, desc, claim_emb, lr, voice, event_time=et)
            if parent_id:
                await neo4j._execute_write("""
                    MATCH (eff:Belief {id: $eid})-[r:IMPLIES]->(p:Belief {id: $pid})
                    DELETE r
                """, {'eid': ref_id, 'pid': parent_id})
                await _write_edge(neo4j, bid, parent_id, 'IMPLIES', claim_emb)
            await _write_edge(neo4j, ref_id, bid, 'IMPLIES')
            await _write_confirms(neo4j, claim.id, bid, lr, 'CONFIRMS')
            await _write_involves(neo4j, bid, eids)
        log.info(f"  CAUSE   {bid[-8:]} above {ref_id[-8:]} \"{desc[:50]}\"")
        return 'CAUSE', bid

    elif op == 'DENY' and ref_id:
        bid = make_belief_id(desc, ref_id)
        if not dry_run:
            await _write_belief(neo4j, bid, desc, claim_emb,
                                1.0 / max(lr, 0.01), voice, event_time=et)
            await _write_edge(neo4j, bid, ref_id, 'DISPUTES', claim_emb)
            await _write_confirms(neo4j, claim.id, bid, lr, 'COUNTERS')
            await _write_involves(neo4j, bid, eids)
        log.info(f"  DENY    {bid[-8:]} vs {ref_id[-8:]} \"{desc[:50]}\"")
        return 'DENY', bid

    else:  # NEW
        bid = make_belief_id(desc or text[:30])
        if not dry_run:
            await _write_belief(neo4j, bid, desc or text[:40], claim_emb, lr, voice)
            await _write_confirms(neo4j, claim.id, bid, lr, 'CONFIRMS')
            await _write_involves(neo4j, bid, eids)
        log.info(f"  NEW     {bid[-8:]} \"{(desc or text[:40])[:50]}\"")
        return 'NEW', bid


# ---------------------------------------------------------------------------
# DIGEST — Opus: entropy restructure
# ---------------------------------------------------------------------------

DIGEST_PROMPT = '''Belief subtree:
{tree}

Restructure so each child follows naturally from its parent with least surprise.
If a child is surprising under its parent, move it under a better parent IN THIS SUBTREE.
If the root is too narrow for its children, broaden it.
Do NOT create connections outside this subtree. Only rearrange within.

JSON lines only (or empty if already coherent):
{{"op":"MOVE","node":"<id>","parent":"<id>"}}
{{"op":"MERGE","keep":"<id>","remove":"<id>"}}
{{"op":"CAUSE","cause":"<id>","effect":"<id>"}}
'''


EMERGE_THRESHOLD = 0.55


async def maybe_emerge(neo4j, dry_run=False):
    """Check if roots are converging — trigger emergence if so.

    Markov state transition: when subtree centroids of two+ roots
    cross the threshold, they belong to the same field. Create a
    parent belief (or merge) to unify them.
    """
    roots = await neo4j._execute_read("""
        MATCH (b:Belief)
        WHERE NOT (b)-[:IMPLIES|DISPUTES]->()
          AND b.subtree_emb IS NOT NULL
        RETURN b.id as id, b.desc as desc, b.subtree_emb as emb, b.subtree_n as n
    """, {})

    if len(roots) < 2:
        return 0

    # Find clusters of converging roots
    from itertools import combinations
    pairs = []
    for r1, r2 in combinations(roots, 2):
        if r1.get('emb') and r2.get('emb'):
            sim = cosine_similarity(r1['emb'], r2['emb'])
            if sim > EMERGE_THRESHOLD:
                pairs.append((r1, r2, sim))

    if not pairs:
        return 0

    # Group converging roots into clusters (simple: take highest sim pair first)
    pairs.sort(key=lambda x: x[2], reverse=True)
    merged_ids = set()
    emergences = 0

    for r1, r2, sim in pairs:
        if r1['id'] in merged_ids or r2['id'] in merged_ids:
            continue

        # Pick the larger root as keeper, smaller as child
        if (r1.get('n') or 0) >= (r2.get('n') or 0):
            keeper, child = r1, r2
        else:
            keeper, child = r2, r1

        log.info(f"  EMERGE  sim={sim:.3f}: {child['id'][-8:]} ({child.get('n',0)} beliefs) → under {keeper['id'][-8:]} ({keeper.get('n',0)} beliefs)")
        log.info(f"    \"{child['desc'][:45]}\"")
        log.info(f"    → \"{keeper['desc'][:45]}\"")

        if not dry_run:
            # Make child root a child of keeper root
            await neo4j._execute_write("""
                MATCH (child:Belief {id: $cid}), (parent:Belief {id: $pid})
                MERGE (child)-[:IMPLIES]->(parent)
            """, {'cid': child['id'], 'pid': keeper['id']})

            # Update keeper's subtree centroid
            if keeper.get('emb') and child.get('emb'):
                k_n = keeper.get('n') or 1
                c_n = child.get('n') or 1
                new_n = k_n + c_n
                dim = len(keeper['emb'])
                new_emb = [(keeper['emb'][i] * k_n + child['emb'][i] * c_n) / new_n
                           for i in range(dim)]
                await neo4j._execute_write("""
                    MATCH (b:Belief {id: $id})
                    SET b.subtree_emb = $emb, b.subtree_n = $n
                """, {'id': keeper['id'], 'emb': new_emb, 'n': new_n})

        merged_ids.add(child['id'])
        emergences += 1

    return emergences


async def digest(neo4j, changed_ids, dry_run=False):
    """Opus entropy restructure — per-root local windows.

    Heals each subtree independently. Never shows the whole tree
    to prevent inter-field connections (that's reflect's job).
    """
    if not changed_ids:
        return 0

    # Find which roots are affected by the changes
    affected_roots = set()
    for cid in changed_ids:
        root_rows = await neo4j._execute_read("""
            MATCH (b:Belief {id: $bid})-[:IMPLIES|DISPUTES*0..20]->(root:Belief)
            WHERE NOT (root)-[:IMPLIES|DISPUTES]->()
            RETURN root.id as rid
        """, {'bid': cid})
        for r in root_rows:
            affected_roots.add(r['rid'])
        # If the changed belief IS a root
        is_root = await neo4j._execute_read("""
            MATCH (b:Belief {id: $bid})
            WHERE NOT (b)-[:IMPLIES|DISPUTES]->()
            RETURN b.id as rid
        """, {'bid': cid})
        for r in is_root:
            affected_roots.add(r['rid'])

    if not affected_roots:
        return 0

    total_ops = 0
    for root_id in affected_roots:
        ops = await _digest_subtree(neo4j, root_id, dry_run)
        total_ops += ops

    return total_ops


async def _digest_subtree(neo4j, root_id, dry_run=False):
    """Heal one subtree rooted at root_id."""
    tree_rows = await neo4j._execute_read("""
        MATCH (b:Belief)-[:IMPLIES|DISPUTES*0..10]->(root:Belief {id: $rid})
        WITH collect(DISTINCT b) as leaves
        MATCH (root:Belief {id: $rid})
        WITH leaves + [root] as all_nodes
        UNWIND all_nodes as n
        OPTIONAL MATCH (n)-[r:IMPLIES|DISPUTES]->(parent:Belief)
        RETURN n.id as id, n.desc as desc, n.n_voices as nv,
               parent.id as parent_id, type(r) as rel
        ORDER BY parent.id, n.desc
    """, {'rid': root_id})

    if len(tree_rows) < 3:
        return 0

    # Render as indented tree
    nodes = {}
    children_map = {}
    roots = []
    for r in tree_rows:
        nid = r['id']
        nodes[nid] = {'desc': r['desc'], 'nv': r.get('nv', 0),
                       'parent': r.get('parent_id'), 'rel': r.get('rel')}
        pid = r.get('parent_id')
        if pid:
            children_map.setdefault(pid, []).append(nid)
        elif nid not in roots:
            roots.append(nid)

    lines = []
    def show(nid, depth=0):
        nd = nodes.get(nid, {})
        pad = '  ' * depth
        prefix = '⊥ ' if nd.get('rel') == 'DISPUTES' else ''
        nv = f" [{nd['nv']}v]" if nd.get('nv', 0) > 1 else ''
        lines.append(f"{pad}{prefix}P{nid[-6:]}: \"{nd.get('desc', '?')[:60]}\"{nv}")
        for cid in children_map.get(nid, []):
            show(cid, depth + 1)

    for rid in roots:
        show(rid)

    tree_text = '\n'.join(lines)
    log.info(f"\nDigest input ({len(nodes)} beliefs):\n{tree_text}\n")

    raw = call_complex(DIGEST_PROMPT.format(tree=tree_text))

    # Apply operations
    ops = 0
    for line in raw.split('\n'):
        start = line.find('{')
        end = line.rfind('}')
        if start < 0 or end <= start:
            continue
        try:
            obj = json.loads(line[start:end+1])
        except json.JSONDecodeError:
            continue

        op = obj.get('op', '').upper()

        if op == 'MOVE':
            node_id = _resolve_id(obj.get('node', ''), nodes)
            parent_id = _resolve_id(obj.get('parent', ''), nodes)
            if node_id and parent_id and node_id != parent_id and not dry_run:
                await neo4j._execute_write("""
                    MATCH (n:Belief {id: $nid})-[r:IMPLIES|DISPUTES]->(old:Belief)
                    DELETE r
                """, {'nid': node_id})
                await _write_edge(neo4j, node_id, parent_id, 'IMPLIES')
            if node_id and parent_id:
                log.info(f"  MOVE    {node_id[-8:]} under {parent_id[-8:]}")
                ops += 1

        elif op == 'MERGE':
            keep_id = _resolve_id(obj.get('keep', ''), nodes)
            remove_id = _resolve_id(obj.get('remove', ''), nodes)
            if keep_id and remove_id and keep_id != remove_id and not dry_run:
                # Reparent children of removed to keeper
                await neo4j._execute_write("""
                    MATCH (child:Belief)-[r:IMPLIES]->(removed:Belief {id: $rid})
                    MERGE (child)-[:IMPLIES]->(keeper:Belief {id: $kid})
                    DELETE r
                """, {'rid': remove_id, 'kid': keep_id})
                # Transfer evidence
                await neo4j._execute_write("""
                    MATCH (c:Claim)-[r:CONFIRMS]->(removed:Belief {id: $rid})
                    MERGE (c)-[:CONFIRMS]->(keeper:Belief {id: $kid})
                    DELETE r
                """, {'rid': remove_id, 'kid': keep_id})
                await neo4j._execute_write("""
                    MATCH (removed:Belief {id: $rid}) DETACH DELETE removed
                """, {'rid': remove_id})
                repo = await get_belief_repo()
                await repo.delete(remove_id)
            if keep_id and remove_id:
                log.info(f"  MERGE   {remove_id[-8:]} into {keep_id[-8:]}")
                ops += 1

        elif op == 'CAUSE':
            cause_id = _resolve_id(obj.get('cause', ''), nodes)
            effect_id = _resolve_id(obj.get('effect', ''), nodes)
            if cause_id and effect_id and cause_id != effect_id and not dry_run:
                # Get effect's parent
                eff_parent = await neo4j._execute_read("""
                    MATCH (eff:Belief {id: $eid})-[r:IMPLIES|DISPUTES]->(p:Belief)
                    RETURN p.id as pid
                """, {'eid': effect_id})
                parent_id = eff_parent[0]['pid'] if eff_parent else None
                # Remove cause from current parent
                await neo4j._execute_write("""
                    MATCH (cause:Belief {id: $cid})-[r:IMPLIES|DISPUTES]->(old:Belief)
                    DELETE r
                """, {'cid': cause_id})
                # Remove effect from current parent
                if parent_id:
                    await neo4j._execute_write("""
                        MATCH (eff:Belief {id: $eid})-[r:IMPLIES|DISPUTES]->(p:Belief {id: $pid})
                        DELETE r
                    """, {'eid': effect_id, 'pid': parent_id})
                    # Cause takes effect's place
                    await _write_edge(neo4j, cause_id, parent_id, 'IMPLIES')
                # Effect under cause
                await _write_edge(neo4j, effect_id, cause_id, 'IMPLIES')
            if cause_id and effect_id:
                log.info(f"  CAUSE   {cause_id[-8:]} above {effect_id[-8:]}")
                ops += 1

    return ops


def _resolve_id(short, nodes):
    """Resolve P-shorthand or partial ID to full belief ID."""
    short = str(short).replace('P', '').strip()
    for nid in nodes:
        if nid.endswith(short) or nid[-6:] == short:
            return nid
    return None


# ---------------------------------------------------------------------------
# Neo4j write helpers
# ---------------------------------------------------------------------------

async def _write_belief(neo4j, bid, desc, emb=None, lr=1.0, voice='', event_time=None):
    log_odds = math.log(lr) if lr > 0 and lr != 1.0 else 0.0
    await neo4j._execute_write("""
        MERGE (b:Belief {id: $id})
        ON CREATE SET b.desc = $desc, b.log_odds = $lo, b.n_voices = 1,
                      b.embedding = $emb, b.subtree_emb = $emb,
                      b.subtree_n = 1, b.event_time = $et,
                      b.created_at = datetime()
        ON MATCH SET b.log_odds = b.log_odds + $lo,
                     b.n_voices = b.n_voices + 1,
                     b.event_time = CASE WHEN b.event_time IS NULL
                         THEN $et
                         WHEN $et IS NOT NULL AND $et < b.event_time
                         THEN $et ELSE b.event_time END,
                     b.updated_at = datetime()
    """, {'id': bid, 'desc': desc[:80], 'lo': log_odds, 'emb': emb, 'et': event_time})
    # Mirror to PG for ANN search (is_root set True initially; _write_edge clears it)
    repo = await get_belief_repo()
    await repo.upsert(
        belief_id=bid, description=desc[:80], embedding=emb,
        log_odds=log_odds, n_voices=1, is_root=True, event_time=event_time,
    )


async def _update_subtree_emb(neo4j, belief_id, new_emb):
    """Walk up to root, updating each ancestor's subtree centroid."""
    if not new_emb:
        return
    # Find all ancestors (including self)
    ancestors = await neo4j._execute_read("""
        MATCH (b:Belief {id: $bid})-[:IMPLIES|DISPUTES*0..20]->(ancestor:Belief)
        RETURN ancestor.id as id, ancestor.subtree_emb as emb, ancestor.subtree_n as n
    """, {'bid': belief_id})

    repo = await get_belief_repo()
    for anc in ancestors:
        aid = anc['id']
        old_emb = anc.get('emb')
        old_n = anc.get('n') or 0
        if old_emb and old_n > 0:
            # Running centroid: new = (old * n + new) / (n + 1)
            new_n = old_n + 1
            centroid = [(o * old_n + n) / new_n for o, n in zip(old_emb, new_emb)]
        else:
            centroid = new_emb
            new_n = 1
        await neo4j._execute_write("""
            MATCH (b:Belief {id: $id})
            SET b.subtree_emb = $emb, b.subtree_n = $n
        """, {'id': aid, 'emb': centroid, 'n': new_n})
        # Mirror subtree centroid to PG
        await repo.update_subtree(aid, centroid, new_n)


async def _write_edge(neo4j, child_id, parent_id, rel_type, child_emb=None):
    if rel_type == 'DISPUTES':
        await neo4j._execute_write("""
            MATCH (c:Belief {id: $cid}), (p:Belief {id: $pid})
            MERGE (c)-[:DISPUTES]->(p)
        """, {'cid': child_id, 'pid': parent_id})
    else:
        await neo4j._execute_write("""
            MATCH (c:Belief {id: $cid}), (p:Belief {id: $pid})
            MERGE (c)-[:IMPLIES]->(p)
        """, {'cid': child_id, 'pid': parent_id})
    # Child is no longer a root
    repo = await get_belief_repo()
    await repo.set_root(child_id, False)
    # Update subtree centroids up to root
    if child_emb:
        await _update_subtree_emb(neo4j, child_id, child_emb)


async def _write_confirms(neo4j, claim_id, belief_id, lr, stance):
    await neo4j._execute_write("""
        MATCH (c:Claim {id: $cid}), (b:Belief {id: $bid})
        MERGE (c)-[r:CONFIRMS]->(b)
        SET r.lr = $lr, r.stance = $stance
    """, {'cid': claim_id, 'bid': belief_id, 'lr': lr, 'stance': stance})


async def _write_involves(neo4j, belief_id, entity_ids):
    for eid in entity_ids:
        await neo4j._execute_write("""
            MATCH (b:Belief {id: $bid}), (e:Entity {id: $eid})
            MERGE (b)-[:INVOLVES]->(e)
        """, {'bid': belief_id, 'eid': eid})


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def cmd_sense(args):
    """Sense: perceive claims from a page into the belief tree."""
    neo4j = Neo4jService()
    await neo4j.connect()

    claims, entities, tree_map = await pull_claims(neo4j, args.page)
    log.info(f"{len(claims)} claims, {len(entities)} entities, {len(tree_map)} tree edges")
    for eid, name in entities.items():
        log.info(f"  {name}")

    for c in claims:
        get_emb(c.text)

    # Cohort centroid: page-level aboutness
    valid_embs = [get_emb(c.text) for c in claims if get_emb(c.text)]
    if valid_embs:
        dim = len(valid_embs[0])
        cohort_centroid = [sum(e[i] for e in valid_embs) / len(valid_embs) for i in range(dim)]
    else:
        cohort_centroid = None

    # Page field via cohort centroid vs subtree centroids
    page_field_id = None
    if cohort_centroid:
        field_id, field_sim = await land(neo4j, cohort_centroid)
        if field_id and field_sim > 0.55:
            page_field_id = field_id
            log.info(f"  Page field: {field_id[-8:]} (sim={field_sim:.3f})")

    changed_ids = []
    claim_landings = {}  # claim_id → belief_id
    log.info(f"\nSensing...")

    # Relation → BELLA operation mapping
    REL_OP = {
        'causes': 'CAUSE', 'counters': 'DENY',
        'elaborates': 'AMEND', 'evidence': 'CONFIRM',
        'mechanism': 'ADD', 'assessment': 'ADD',
    }

    for claim in claims:
        emb = get_emb(claim.text)
        eids = claim.entity_ids[:3]
        lr = claim.lr_page or 1.0

        # ── Landing: claim tree drag > page field > embedding ──
        tree_info = tree_map.get(claim.id)
        parent_cid = tree_info['parent'] if tree_info else None
        tree_rel = tree_info['rel'] if tree_info else None
        drag_target = claim_landings.get(parent_cid) if parent_cid else None

        if drag_target:
            # Parent claim landed here — follow it
            landing_id, landing_sim = drag_target, 0.7
        elif page_field_id:
            landing_id, landing_sim = page_field_id, 0.5
        else:
            landing_id, landing_sim = await land(neo4j, emb)

        # ── Placement: relationship-driven when tree_rel is known ──
        if tree_rel and drag_target and tree_rel in REL_OP:
            target_op = REL_OP[tree_rel]
            desc = claim.text[:60]
            bid = make_belief_id(desc, drag_target)

            if target_op == 'CONFIRM':
                # evidence → confirm parent's belief
                if not args.dry_run:
                    await neo4j._execute_write("""
                        MATCH (b:Belief {id: $bid})
                        SET b.log_odds = b.log_odds + $lo, b.n_voices = b.n_voices + 1
                    """, {'bid': drag_target,
                          'lo': math.log(lr) if lr > 0 and lr != 1.0 else 0.0})
                    await _write_confirms(neo4j, claim.id, drag_target, lr, 'CONFIRMS')
                log.info(f"  {tree_rel:12s} CONFIRM {drag_target[-8:]} \"{claim.text[:45]}\"")
                bid = drag_target

            elif target_op == 'AMEND':
                # elaborates → amend parent's belief
                if not args.dry_run:
                    await neo4j._execute_write("""
                        MATCH (b:Belief {id: $bid})
                        SET b.log_odds = b.log_odds + $lo, b.n_voices = b.n_voices + 1
                    """, {'bid': drag_target,
                          'lo': math.log(lr) if lr > 0 and lr != 1.0 else 0.0})
                    await _write_confirms(neo4j, claim.id, drag_target, lr, 'SUPPORTS')
                log.info(f"  {tree_rel:12s} AMEND   {drag_target[-8:]} \"{claim.text[:45]}\"")
                bid = drag_target

            elif target_op == 'DENY':
                # counters → deny parent's belief
                if not args.dry_run:
                    await _write_belief(neo4j, bid, desc, emb, 1.0/max(lr, 0.01), event_time=claim.event_time)
                    await _write_edge(neo4j, bid, drag_target, 'DISPUTES', emb)
                    await _write_confirms(neo4j, claim.id, bid, lr, 'COUNTERS')
                    await _write_involves(neo4j, bid, eids)
                log.info(f"  {tree_rel:12s} DENY    {bid[-8:]} vs {drag_target[-8:]} \"{desc[:40]}\"")
                changed_ids.append(bid)

            elif target_op == 'CAUSE':
                # causes → insert above parent's belief
                if not args.dry_run:
                    eff_parent = await neo4j._execute_read("""
                        MATCH (eff:Belief {id: $eid})-[r:IMPLIES]->(p:Belief)
                        RETURN p.id as pid
                    """, {'eid': drag_target})
                    gp_id = eff_parent[0]['pid'] if eff_parent else None
                    await _write_belief(neo4j, bid, desc, emb, lr, event_time=claim.event_time)
                    if gp_id:
                        await neo4j._execute_write("""
                            MATCH (eff:Belief {id: $eid})-[r:IMPLIES]->(p:Belief {id: $pid})
                            DELETE r
                        """, {'eid': drag_target, 'pid': gp_id})
                        await _write_edge(neo4j, bid, gp_id, 'IMPLIES', emb)
                    await _write_edge(neo4j, drag_target, bid, 'IMPLIES')
                    await _write_confirms(neo4j, claim.id, bid, lr, 'CONFIRMS')
                    await _write_involves(neo4j, bid, eids)
                log.info(f"  {tree_rel:12s} CAUSE   {bid[-8:]} above {drag_target[-8:]} \"{desc[:40]}\"")
                changed_ids.append(bid)

            else:  # ADD (mechanism, assessment)
                if not args.dry_run:
                    await _write_belief(neo4j, bid, desc, emb, lr, event_time=claim.event_time)
                    await _write_edge(neo4j, bid, drag_target, 'IMPLIES', emb)
                    await _write_confirms(neo4j, claim.id, bid, lr, 'CONFIRMS')
                    await _write_involves(neo4j, bid, eids)
                log.info(f"  {tree_rel:12s} ADD     {bid[-8:]} under {drag_target[-8:]} \"{desc[:40]}\"")
                changed_ids.append(bid)

            if bid:
                claim_landings[claim.id] = bid
            continue

        # ── Fallback: LLM placement (no tree relation or no drag target) ──
        op, bid = await place(neo4j, claim, emb, landing_id, landing_sim,
                              entities, dry_run=args.dry_run)
        if op in ('ADD', 'CAUSE', 'DENY', 'NEW'):
            changed_ids.append(bid)
        if bid:
            claim_landings[claim.id] = bid

    log.info(f"\n{len(claims)} claims sensed. {len(changed_ids)} structural changes.")

    # ── EMERGE: check if roots are converging (Markov state transition) ──
    if not args.no_heal:
        n_emerged = await maybe_emerge(neo4j, dry_run=args.dry_run)
        if n_emerged:
            log.info(f"\n{n_emerged} emergence(s).")

    # ── HEAL: entropy-triggered restructure ──
    if changed_ids and not args.no_heal:
        ent = await compute_entropy(neo4j)
        log.info(f"\nEntropy: edge={ent['edge_entropy']:.3f} root={ent['root_entropy']:.3f}")
        if ent['root_entropy'] > 0.6 or ent['edge_entropy'] > 0.4:
            log.info("Healing triggered — tree is incoherent")
            n_ops = await digest(neo4j, changed_ids, dry_run=args.dry_run)
            log.info(f"{n_ops} restructure operations.")
        else:
            log.info("Tree is coherent — no healing needed")

    await neo4j.close()
    log.info(f"\nLLM: {CALLS['simple']} sense + {CALLS['complex']} heal = ${COST:.3f}")


async def cmd_heal(args):
    """Heal: entropy-triggered restructure per subtree."""
    neo4j = Neo4jService()
    await neo4j.connect()

    ent = await compute_entropy(neo4j)
    log.info(f"Entropy: edge={ent['edge_entropy']:.3f} root={ent['root_entropy']:.3f}")

    # Find roots with high internal entropy
    roots = await neo4j._execute_read("""
        MATCH (root:Belief)
        WHERE NOT (root)-[:IMPLIES|DISPUTES]->()
        RETURN root.id as id, root.desc as desc
    """, {})

    total_ops = 0
    for root in roots:
        rid = root['id']
        # Compute per-root edge entropy
        edges = await neo4j._execute_read("""
            MATCH (child:Belief)-[:IMPLIES|DISPUTES*0..10]->(root:Belief {id: $rid})
            MATCH (child)-[:IMPLIES|DISPUTES]->(parent:Belief)
            WHERE child.embedding IS NOT NULL AND parent.embedding IS NOT NULL
            RETURN child.embedding as c_emb, parent.embedding as p_emb
        """, {'rid': rid})
        if len(edges) < 2:
            continue
        avg_s = sum(1 - cosine_similarity(e['c_emb'], e['p_emb']) for e in edges) / len(edges)
        log.info(f"\n  {rid[-8:]}: \"{root['desc'][:40]}\" H={avg_s:.3f} ({len(edges)} edges)")

        if avg_s > 0.4:
            log.info(f"    Healing...")
            ops = await _digest_subtree(neo4j, rid, dry_run=args.dry_run)
            log.info(f"    {ops} operations")
            total_ops += ops
        else:
            log.info(f"    Coherent")

    log.info(f"\n{total_ops} total restructure operations.")

    ent2 = await compute_entropy(neo4j)
    log.info(f"After: edge={ent2['edge_entropy']:.3f} root={ent2['root_entropy']:.3f}")

    await neo4j.close()
    log.info(f"\nLLM: {CALLS['complex']} complex = ${COST:.3f}")


async def cmd_reflect(args):
    """Reflect: observe the graph, find emergent patterns across fields."""
    neo4j = Neo4jService()
    await neo4j.connect()

    # Step 1: Get all roots with their subtree stats
    roots = await neo4j._execute_read("""
        MATCH (root:Belief)
        WHERE NOT (root)-[:IMPLIES|DISPUTES]->()
        OPTIONAL MATCH (b:Belief)-[:IMPLIES|DISPUTES*0..10]->(root)
        WITH root, count(DISTINCT b) as size, sum(b.n_voices) as voices
        OPTIONAL MATCH (b2:Belief)-[:IMPLIES|DISPUTES*0..10]->(root)
        OPTIONAL MATCH (b2)-[:INVOLVES]->(e:Entity)
        WITH root, size, voices,
             collect(DISTINCT e.id) as eids,
             collect(DISTINCT e.canonical_name) as enames
        RETURN root.id as id, root.desc as desc,
               root.subtree_emb as emb, root.event_time as et,
               root.log_odds as lo,
               size, voices, eids, enames
        ORDER BY size DESC
    """, {})

    if len(roots) < 2:
        log.info("Only 1 root — nothing to reflect on yet.")
        await neo4j.close()
        return

    log.info(f"{len(roots)} fields to examine\n")

    # Step 2: Find convergent groups (shared entities + aligned mass)
    # Build a summary for Opus
    field_summaries = []
    for r in roots:
        lo = r.get('lo') or 0.0
        m = 1.0 / (1.0 + math.exp(-lo)) if -20 < lo < 20 else 0.5
        et = str(r['et'])[:10] if r.get('et') else '?'
        enames = [n for n in (r.get('enames') or []) if n][:5]
        field_summaries.append(
            f"F{r['id'][-6:]}: \"{r['desc'][:60]}\" "
            f"[m={m:.2f}, {r['size']}b, {r['voices']}v, {et}] "
            f"entities: {', '.join(enames) if enames else 'none'}"
        )

    fields_text = '\n'.join(field_summaries)

    # Step 3: Opus observes — what patterns emerge across fields?
    prompt = f"""These are independent belief fields in a world model:

{fields_text}

What patterns emerge ACROSS these fields? Look for:
- Multiple fields converging on the same conclusion
- Causal chains spanning fields (A's events cause B's effects)
- Contradictions between fields

For each emergent pattern, output one JSON:
{{"pattern":"description of what converges","fields":["F<id>","F<id>"],"type":"convergence|causal|contradiction"}}

Only real patterns supported by the field descriptions. Nothing speculative."""

    raw = call_complex(prompt, max_tokens=800)

    # Step 4: Parse emergent patterns (JSON array or JSON-per-line)
    cleaned = raw.replace('```json', '').replace('```', '').strip()
    # Try to repair truncated JSON array
    if cleaned.startswith('[') and not cleaned.endswith(']'):
        cleaned = cleaned.rstrip(',\n ') + ']'
    patterns = []
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            patterns = parsed
        else:
            patterns = [parsed]
    except json.JSONDecodeError:
        # Fallback: extract individual objects
        for m in re.finditer(r'\{[^{}]+\}', cleaned):
            try:
                patterns.append(json.loads(m.group()))
            except json.JSONDecodeError:
                continue

    emergent_count = 0
    for obj in patterns:

        pattern = obj.get('pattern', '')
        field_refs = obj.get('fields', [])
        ptype = obj.get('type', 'convergence')

        if not pattern or len(field_refs) < 2:
            continue

        log.info(f"\n  {'🔗' if ptype == 'causal' else '🔀' if ptype == 'convergence' else '⚡'} {ptype}: {pattern}")
        for f in field_refs:
            log.info(f"    ← {f}")

        # Create emergent belief if not dry run
        if not args.dry_run:
            ebid = make_belief_id(pattern)
            await _write_belief(neo4j, ebid, pattern[:80])

            # Cross-reference to each source field's root
            for fref in field_refs:
                fid_short = fref.replace('F', '')
                for r in roots:
                    if r['id'].endswith(fid_short):
                        await _write_edge(neo4j, r['id'], ebid, 'IMPLIES')
                        log.info(f"    → linked {r['id'][-8:]}")
                        break

            emergent_count += 1

    log.info(f"\n{emergent_count} emergent patterns found.")
    await neo4j.close()
    log.info(f"\nLLM: {CALLS['complex']} complex = ${COST:.3f}")


async def cmd_bond(args):
    """Bond: social signals (stakes, votes, posts). Future."""
    log.info("Bond not yet implemented. Will process stakes/votes/posts.")


    # old stub removed — cmd_reflect is now above


async def compute_entropy(neo4j):
    """Compute tree vital signs from embeddings. All mechanical, no LLM.

    Edge surprise is weighted by relationship type:
    - IMPLIES: full surprise (child should follow from parent)
    - DISPUTES: reduced by 0.5 (counter-arguments are expected to diverge)
    - No edge type means IMPLIES (default)
    """
    # Edge entropy: average surprise across parent-child pairs
    edges = await neo4j._execute_read("""
        MATCH (child:Belief)-[r:IMPLIES|DISPUTES]->(parent:Belief)
        WHERE child.embedding IS NOT NULL AND parent.embedding IS NOT NULL
        RETURN child.embedding as c_emb, parent.embedding as p_emb,
               child.id as cid, parent.id as pid, type(r) as rel
    """, {})
    edge_surprises = {}
    for e in edges:
        sim = cosine_similarity(e['c_emb'], e['p_emb'])
        raw_surprise = 1.0 - sim
        # DISPUTES edges tolerate more divergence
        if e.get('rel') == 'DISPUTES':
            edge_surprises[e['cid']] = raw_surprise * 0.5
        else:
            edge_surprises[e['cid']] = raw_surprise
    avg_surprise = sum(edge_surprises.values()) / len(edge_surprises) if edge_surprises else 0.0

    # Root entropy: max pairwise similarity between roots
    roots = await neo4j._execute_read("""
        MATCH (b:Belief)
        WHERE NOT (b)-[:IMPLIES|DISPUTES]->()
          AND b.embedding IS NOT NULL
        RETURN b.id as id, b.desc as desc, b.embedding as emb
    """, {})
    max_root_sim = 0.0
    root_pair = ('', '')
    for i, r1 in enumerate(roots):
        for r2 in roots[i+1:]:
            sim = cosine_similarity(r1['emb'], r2['emb'])
            if sim > max_root_sim:
                max_root_sim = sim
                root_pair = (r1['id'][-8:], r2['id'][-8:])

    # Mass stats
    mass_rows = await neo4j._execute_read("""
        MATCH (b:Belief)
        RETURN avg(b.log_odds) as avg_lo, sum(b.n_voices) as total_v,
               count(b) as n
    """, {})
    mr = mass_rows[0] if mass_rows else {}
    avg_lo = mr.get('avg_lo') or 0.0
    avg_mass = 1.0 / (1.0 + math.exp(-avg_lo)) if -20 < avg_lo < 20 else 0.5

    return {
        'edge_entropy': avg_surprise,
        'root_entropy': max_root_sim,
        'root_pair': root_pair,
        'edge_surprises': edge_surprises,
        'avg_mass': avg_mass,
        'total_voices': mr.get('total_v', 0),
        'n_beliefs': mr.get('n', 0),
        'n_roots': len(roots),
    }


async def cmd_tree(args):
    neo4j = Neo4jService()
    await neo4j.connect()

    rows = await neo4j._execute_read("""
        MATCH (b:Belief)
        OPTIONAL MATCH (b)-[r:IMPLIES|DISPUTES]->(parent:Belief)
        RETURN b.id as id, b.desc as desc, b.n_voices as nv,
               b.log_odds as lo, parent.id as parent_id, type(r) as rel,
               b.event_time as et
    """, {})

    nodes, children_map, roots = {}, {}, []
    for r in rows:
        nid = r['id']
        lo = r.get('lo') or 0.0
        m = 1.0 / (1.0 + math.exp(-lo)) if -20 < lo < 20 else (1.0 if lo >= 20 else 0.0)
        et = str(r['et'])[:10] if r.get('et') else None
        nodes[nid] = {'desc': r['desc'], 'nv': r.get('nv', 0), 'm': m,
                       'rel': r.get('rel'), 'parent': r.get('parent_id'),
                       'et': et}
        pid = r.get('parent_id')
        if pid:
            children_map.setdefault(pid, []).append(nid)
        elif nid not in roots:
            roots.append(nid)

    # Compute entropy
    ent = await compute_entropy(neo4j)
    surprises = ent['edge_surprises']

    # Compute per-root stats
    def subtree_size(nid):
        return 1 + sum(subtree_size(c) for c in children_map.get(nid, []))

    def subtree_voices(nid):
        nd = nodes.get(nid, {})
        return (nd.get('nv') or 0) + sum(subtree_voices(c) for c in children_map.get(nid, []))

    def max_depth(nid, d=0):
        children = children_map.get(nid, [])
        return max((max_depth(c, d+1) for c in children), default=d)

    # Surprise indicator
    def surprise_icon(s):
        if s is None: return '  '
        if s >= 0.6: return '🔴'
        if s >= 0.4: return '🟡'
        return '🟢'

    # Mass bar
    def mass_bar(m):
        filled = round(m * 5)
        return '█' * filled + '░' * (5 - filled)

    def show(nid, depth=0):
        nd = nodes.get(nid, {})
        pad = '  ' * depth
        # Relation prefix
        if nd.get('rel') == 'DISPUTES':
            rel = '⊥ '
        else:
            rel = ''
        # Voices
        nv = nd.get('nv', 0)
        voices = f' 👥{nv}' if nv > 1 else ''
        # Surprise
        s = surprises.get(nid)
        si = surprise_icon(s)
        # Mass
        m = nd['m']
        mb = mass_bar(m)
        # Children count
        nc = len(children_map.get(nid, []))
        branch = f' +{nc}' if nc > 0 else ''

        # Time (precision-aware display)
        et = nd.get('et') or ''
        time_str = f' 📅{et}' if et else ''

        desc = nd.get('desc', '?')[:48]
        print(f"{pad}{si} {rel}{nid[-6:]}: \"{desc}\" {mb}{voices}{time_str}{branch}")
        # Sort children by event_time for temporal ordering
        children_sorted = sorted(children_map.get(nid, []),
                                  key=lambda c: nodes.get(c, {}).get('et') or '9999')
        for cid in children_sorted:
            show(cid, depth + 1)

    # ── Header ──
    edge_h = ent['edge_entropy']
    root_h = ent['root_entropy']
    need_heal = root_h > 0.6 or edge_h > 0.4
    health = '❤️  NEEDS HEALING' if need_heal else '💚 HEALTHY'

    print(f"{'─' * 60}")
    print(f"  BELLA  {health}")
    print(f"  {len(nodes)} beliefs  {len(roots)} roots  {ent['total_voices']} voices")
    print(f"  Edge entropy: {edge_h:.3f}  {'🔴' if edge_h > 0.4 else '🟡' if edge_h > 0.3 else '🟢'}")
    print(f"  Root entropy: {root_h:.3f}  {'🔴' if root_h > 0.6 else '🟡' if root_h > 0.4 else '🟢'}", end='')
    if ent['root_pair'][0]:
        print(f"  ({ent['root_pair'][0][-6:]}~{ent['root_pair'][1][-6:]})", end='')
    print()
    print(f"  Avg mass: {mass_bar(ent['avg_mass'])} {ent['avg_mass']:.2f}")
    print(f"{'─' * 60}")
    print(f"  🟢 coherent  🟡 mild surprise  🔴 misplaced")
    print(f"  █=mass  👥=voices  +N=children")
    print(f"{'─' * 60}\n")

    # Per-root internal entropy
    def subtree_entropy(nid):
        s_vals = []
        def collect(n):
            if n in surprises:
                s_vals.append(surprises[n])
            for c in children_map.get(n, []):
                collect(c)
        collect(nid)
        return sum(s_vals) / len(s_vals) if s_vals else 0.0

    # Evidence density: claims per belief
    evidence_counts = {}
    try:
        ev_rows_result = asyncio.get_event_loop().run_until_complete(
            neo4j._execute_read("""
                MATCH (c:Claim)-[:CONFIRMS]->(b:Belief)
                RETURN b.id as bid, count(c) as ec
            """, {}))
        for er in ev_rows_result:
            evidence_counts[er['bid']] = er['ec']
    except RuntimeError:
        pass  # already in event loop, skip

    # ── Roots (just beliefs with no parent — identity is the subtree, not the label) ──
    for rid in roots:
        sz = subtree_size(rid)
        tv = subtree_voices(rid)
        md = max_depth(rid)
        ie = subtree_entropy(rid)

        health_icon = '🔴' if ie > 0.5 else '🟡' if ie > 0.35 else '🟢'
        print(f"{'─' * 40}")
        print(f"  {health_icon} {sz} beliefs  {tv} voices  depth {md}  H={ie:.2f}")
        show(rid)
        print()

    await neo4j.close()


async def cmd_status(args):
    neo4j = Neo4jService()
    await neo4j.connect()
    for label, q in [
        ('Beliefs', 'MATCH (b:Belief) RETURN count(b) as n'),
        ('IMPLIES', 'MATCH ()-[r:IMPLIES]->() RETURN count(r) as n'),
        ('DISPUTES', 'MATCH ()-[r:DISPUTES]->() RETURN count(r) as n'),
        ('Evidence', 'MATCH ()-[r:CONFIRMS]->() RETURN count(r) as n'),
        ('Roots', 'MATCH (b:Belief) WHERE NOT (b)-[:IMPLIES|DISPUTES]->() RETURN count(b) as n'),
    ]:
        r = await neo4j._execute_read(q, {})
        print(f"  {label:12s} {r[0]['n']}")

    ent = await compute_entropy(neo4j)
    print(f"\n  Edge H       {ent['edge_entropy']:.3f}  (avg parent-child surprise)")
    print(f"  Root H       {ent['root_entropy']:.3f}  (max root-root similarity)")
    if ent['root_pair'][0]:
        print(f"  Root pair    {ent['root_pair'][0]} ~ {ent['root_pair'][1]}")
    print(f"  Avg mass     {ent['avg_mass']:.3f}")
    print(f"  Total voices {ent['total_voices']}")
    need_digest = ent['root_entropy'] > 0.6 or ent['edge_entropy'] > 0.4
    print(f"  Digest       {'NEEDED' if need_digest else 'ok'}")
    await neo4j.close()


async def cmd_reset(args):
    if not args.confirm:
        print("Add --confirm"); return
    neo4j = Neo4jService()
    await neo4j.connect()
    await neo4j._execute_write("MATCH (b:Belief) DETACH DELETE b", {})
    repo = await get_belief_repo()
    await repo.pool.execute("DELETE FROM core.belief_embeddings")
    print("All beliefs deleted (Neo4j + PG).")
    await neo4j.close()
    await close_pg()


def main():
    p = argparse.ArgumentParser(description='BELLA — sense / bond / heal / reflect')
    sub = p.add_subparsers(dest='cmd')

    s = sub.add_parser('sense', help='Perceive claims from a page')
    s.add_argument('--page', '-p', required=True)
    s.add_argument('--dry-run', action='store_true')
    s.add_argument('--no-heal', action='store_true', help='Skip auto-heal after sensing')

    h = sub.add_parser('heal', help='Entropy-triggered restructure')
    h.add_argument('--dry-run', action='store_true')

    sub.add_parser('bond', help='Social signals (future)')
    rf = sub.add_parser('reflect', help='Observe graph, find emergent patterns')
    rf.add_argument('--dry-run', action='store_true')
    sub.add_parser('tree', help='Display belief tree with vital signs')
    sub.add_parser('status', help='Counts + entropy metrics')

    r = sub.add_parser('reset', help='Clear all beliefs')
    r.add_argument('--confirm', action='store_true')

    args = p.parse_args()
    cmds = {
        'sense': cmd_sense, 'heal': cmd_heal,
        'bond': cmd_bond, 'reflect': cmd_reflect,
        'tree': cmd_tree, 'status': cmd_status, 'reset': cmd_reset,
    }
    async def run_cmd():
        try:
            await cmds[args.cmd](args)
        finally:
            await close_pg()

    if args.cmd in cmds:
        asyncio.run(run_cmd())
    else:
        p.print_help()


if __name__ == '__main__':
    main()

"""BELLA Kernel — the ribosome.

Boots Bella from her gene. Routes claims to fields. Each field
has its own gene. The proven e103_proof firmware is the RNA.

Architecture:
  Gene (DNA):       B-nodes (constitution) + P-nodes per field
  Firmware (RNA):   proven prompt template from e103_proof
  Kernel (ribosome): routes, transcribes, parses, applies. Stable.
  LLM (substrate):   interprets transcript, produces actions.
"""

import asyncio, hashlib, json, os, re, sys
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'here'))
from here.services.llm_gateway import LLMGateway, ModelTier
from here.fabric.grow_match import _get_embeddings, cosine_similarity


# ---------------------------------------------------------------------------
# Gene — one per field
# ---------------------------------------------------------------------------

class Gene:
    def __init__(self, name=''):
        self.name = name
        self.nodes = {}
        self.roots = []
        self.next_n = 1

    def add(self, n, desc, parent=None, rel='→', voice='', emb=None):
        self.nodes[n] = {
            'desc': desc[:60], 'parent': parent, 'rel': rel,
            'children': [], 'voices': set(), 'embedding': emb,
        }
        if voice:
            self.nodes[n]['voices'].add(voice)
        self.next_n = max(self.next_n, n + 1)
        if parent and parent in self.nodes:
            self.nodes[parent]['children'].append(n)
        else:
            self.roots.append(n)

    def confirm(self, n, voice=''):
        if n in self.nodes and voice:
            self.nodes[n]['voices'].add(voice)

    def amend(self, n, detail='', voice=''):
        if n in self.nodes:
            if voice: self.nodes[n]['voices'].add(voice)
            if detail:
                self.nodes[n]['desc'] = f"{self.nodes[n]['desc']}; {detail}"[:60]

    def render(self):
        lines = []
        def show(n, depth=0):
            nd = self.nodes[n]
            pad = '  ' * depth
            counter = '⊥ ' if nd['rel'] == '⊥' else ''
            v = len(nd['voices'])
            vc = f' [{v}v]' if v > 1 else ''
            lines.append(f"{pad}{counter}P{n}: \"{nd['desc']}\"{vc}")
            for cn in nd['children']:
                show(cn, depth + 1)
        for r in self.roots:
            show(r)
        return '\n'.join(lines)

    def root_embedding(self):
        """Average embedding of roots — the field's signature."""
        embs = [self.nodes[r]['embedding'] for r in self.roots
                if r in self.nodes and self.nodes[r].get('embedding')]
        if not embs:
            return None
        dim = len(embs[0])
        return [sum(e[i] for e in embs) / len(embs) for i in range(dim)]


# ---------------------------------------------------------------------------
# Bella — the organism
# ---------------------------------------------------------------------------

class Bella:
    def __init__(self):
        self.fields = {}       # name → Gene
        self.self_model = Gene('bella')  # B-nodes
        self._boot_constitution()

    def _boot_constitution(self):
        sm = self.self_model
        sm.add(1, "I construct beliefs from evidence")
        sm.add(2, "operations: ⊨ ⊨∧δ ⊢→ ⊢⊥ ⊢", 1)
        sm.add(3, "⊥ = explicit denial only", 1)
        sm.add(4, "one action per claim", 1)
        sm.add(5, "descriptions are 3-5 word facts", 1)

    def find_field(self, claim_emb, threshold=0.45):
        """Route claim to existing field by best node match."""
        best_sim, best_name = 0, None
        for name, gene in self.fields.items():
            for n, nd in gene.nodes.items():
                if nd.get('embedding'):
                    sim = cosine_similarity(claim_emb, nd['embedding'])
                    if sim > best_sim:
                        best_sim, best_name = sim, name
        if best_sim >= threshold:
            return best_name, best_sim
        return None, 0

    def create_field(self, name, n, desc, voice='', emb=None):
        """Birth a new field from the first claim."""
        gene = Gene(name)
        gene.add(n, desc, voice=voice, emb=emb)
        self.fields[name] = gene
        return gene

    def stats(self):
        total = sum(len(g.nodes) for g in self.fields.values())
        return f"{len(self.fields)} fields, {total} propositions"


# ---------------------------------------------------------------------------
# Firmware (RNA) — the proven e103_proof prompt template
# ---------------------------------------------------------------------------

FIRMWARE = '''KB:
{kb}

c: "{claim}"

ONE action only:
⊨ P<n>                     -- confirms existing (same fact)
⊨ P<n> ∧ δ"2-3 words"      -- confirms + adds detail
⊢ P{next_n} →P<n> "3-5 words" -- new supporting fact
⊢ P{next_n} ⊥P<n> "3-5 words" -- explicitly denies/rejects P<n>
⊢ P{next_n} "3-5 words"       -- new unrelated root

⊥ means EXPLICIT denial only. → means new supporting detail.
One line.'''


def transcribe(gene, claim_text):
    """Gene → RNA: render gene through firmware template."""
    kb = gene.render()
    if not kb.strip():
        return None
    return FIRMWARE.format(kb=kb, claim=claim_text[:200], next_n=gene.next_n)


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

EMB_CACHE = {}

def get_emb(text):
    if text in EMB_CACHE: return EMB_CACHE[text]
    e = _get_embeddings([text])
    r = e[0] if e and e[0] else None
    EMB_CACHE[text] = r
    return r


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

CACHE = {}
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'kernel_cache.json')
COST = 0.0
CALLS = 0


def load_cache():
    global CACHE
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f: CACHE = json.load(f)


def save_cache():
    with open(CACHE_FILE, 'w') as f: json.dump(CACHE, f, indent=2)


async def call_llm(prompt, gw):
    global COST, CALLS
    key = hashlib.md5(prompt.encode()).hexdigest()
    if key in CACHE: return CACHE[key]
    resp = await gw.complete(
        tier=ModelTier.POWERFUL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0, max_tokens=40, purpose="bella")
    COST += getattr(resp, 'estimated_cost_usd', 0.0)
    CALLS += 1
    result = resp.content.strip()
    CACHE[key] = result
    save_cache()
    return result


# ---------------------------------------------------------------------------
# Parse + Apply (same as before, proven)
# ---------------------------------------------------------------------------

def parse(raw):
    line = raw.strip().split('\n')[0].strip()
    m = re.match(r'[⊨=]\s*P(\d+)\s*$', line)
    if m: return 'CONFIRM', int(m.group(1)), None, None
    m = re.match(r'[⊨=]\s*P(\d+)\s*[∧&]\s*[δd]?"?([^"]*)"?', line)
    if m: return 'AMEND', int(m.group(1)), None, m.group(2).strip()
    m = re.match(r'[⊢|-]\s*P(\d+)\s*[→>]\s*P(\d+)\s*"?([^"]*)"?', line)
    if m: return 'CHILD', int(m.group(2)), int(m.group(1)), m.group(3).strip()
    m = re.match(r'[⊢|-]\s*P(\d+)\s*[⊥x]\s*P(\d+)\s*"?([^"]*)"?', line)
    if m: return 'COUNTER', int(m.group(2)), int(m.group(1)), m.group(3).strip()
    m = re.match(r'[⊢|-]\s*P(\d+)\s+"?([^"]+)"?', line)
    if m and '→' not in line and '⊥' not in line:
        return 'ROOT', None, int(m.group(1)), m.group(2).strip()
    return 'ROOT', None, None, raw[:40]


def apply(gene, action, voice='', emb=None):
    act, target, new_n, desc = action
    if act == 'CONFIRM' and target in gene.nodes:
        gene.confirm(target, voice)
        return f'⊨ P{target}'
    if act == 'AMEND' and target in gene.nodes:
        gene.amend(target, desc, voice)
        return f'⊨ P{target} ∧ δ"{desc}"'
    if act in ('CHILD', 'COUNTER') and target in gene.nodes:
        n = new_n or gene.next_n
        rel = '⊥' if act == 'COUNTER' else '→'
        gene.add(n, desc or '?', target, rel, voice, emb)
        return f'⊢ P{n} {"⊥" if act == "COUNTER" else "→"}P{target} "{desc}"'
    if act == 'ROOT':
        n = new_n or gene.next_n
        gene.add(n, desc or '?', voice=voice, emb=emb)
        return f'⊢ P{n} "{desc}"'
    return f'? {act}'


# ---------------------------------------------------------------------------
# Process — the full cycle
# ---------------------------------------------------------------------------

AUTO_CONFIRM = 0.88
FIELD_THRESHOLD = 0.45


async def process(claim, bella, gw):
    """One claim through the living system."""
    text = claim['text']
    voice = claim.get('voice', '')
    emb = get_emb(text)

    # Route to field
    field_name, sim = bella.find_field(emb)

    if field_name:
        gene = bella.fields[field_name]

        # Auto-confirm: very high similarity to existing node
        best_sim, best_n = 0, None
        for n, nd in gene.nodes.items():
            if nd.get('embedding'):
                s = cosine_similarity(emb, nd['embedding'])
                if s > best_sim:
                    best_sim, best_n = s, n
        if best_sim >= AUTO_CONFIRM and best_n:
            gene.confirm(best_n, voice)
            return field_name, f'⊨ P{best_n} (auto)'

        # Deliberate: transcribe and call LLM
        transcript = transcribe(gene, text)
        if transcript:
            raw = await call_llm(transcript, gw)
            action = parse(raw)
            result = apply(gene, action, voice, emb)
            return field_name, result

    # No field matches — birth new field
    # Use first ~30 chars as field name seed
    words = text.split()[:4]
    name = '_'.join(w.lower().strip('.,;:') for w in words if w.isalpha())[:30]
    if not name:
        name = f'field_{len(bella.fields)}'
    desc = text[:60]
    n = 1
    gene = bella.create_field(name, n, desc, voice, emb)
    return name, f'⊢ P1 "{desc[:40]}" (new field: {name})'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    bella = Bella()

    print("BELLA booted.\n")
    print(f"Constitution: {len(bella.self_model.nodes)} B-nodes")
    print(bella.self_model.render())
    print()

    gw = LLMGateway()
    load_cache()

    # Load claims
    data = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'data')
    f35 = json.load(open(os.path.join(data, 'f35_claims.json')))
    eps = json.load(open(os.path.join(data, 'epstein_death_claims.json')))

    # Interleave
    claims = []
    for i in range(max(len(f35), len(eps))):
        if i < len(f35): claims.append(('F35', f35[i]))
        if i < len(eps): claims.append(('EPS', eps[i]))

    stop = int(os.environ.get('STOP_AFTER', 40))
    print(f"Processing {min(stop, len(claims))} interleaved claims...\n")

    for i, (tag, c) in enumerate(claims[:stop]):
        field_name, result = await process(c, bella, gw)
        print(f"  [{tag}] → {field_name}: {result}")

    # Final state
    print(f"\n{'='*60}")
    print(f"Bella: {bella.stats()}\n")
    for name, gene in bella.fields.items():
        nv = sum(len(nd['voices']) for nd in gene.nodes.values())
        print(f"  {name}: {len(gene.nodes)} props, {len(gene.roots)} roots, {nv} total voices")
        print(f"  {gene.render()}")
        print()

    print(f"{CALLS} LLM calls, ${COST:.3f}")


if __name__ == '__main__':
    asyncio.run(main())

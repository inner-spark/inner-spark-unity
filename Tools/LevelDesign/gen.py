"""
Hard-level generator (Claude lvl 21+). Layout first, then mechanics:

1. Layout: nodes scattered on the grid (front / back / via), traces added shortest-first as long as they stay legal
   (straight / 45 deg / one elbow, no same-side crossings, unique 8-way exits, clear of other nodes, <= 4 exits per
   node per side). Gives a planar board per side with natural loops.
2. Mechanics: start (front), goal (back), pass holders / locks, normal + AND switches and their gates, data - placed
   at random, then improved by simulated annealing against the solver. Score = difficulty: shortest solution length,
   number of interactions, the MINIMUM number of pass takes and switch presses any solution needs (so swapping
   passes / pressing is forced, not optional), multi-gate switches that matter.
3. Prune: every gate / lock / switch / data that can be removed without making the level easier is removed, so each
   remaining piece matters.

python gen.py <profile> [seed ...]   (profiles at the bottom). Writes hard_<profile>.json.
"""
import copy, heapq, itertools, json, math, random, sys
from collections import deque

sys.path.insert(0, '.')
from pcbsolver import check_layout, exits, seg_intersect, solve

DIRS8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
COLOURS = ['Red', 'Green']  # Teal has no lock model in the theme yet


# ------------------------------------------------------------------ geometry helpers

def unit(v):
    l = math.hypot(*v)
    return (v[0] / l, v[1] / l)


def seg_point_dist(p, q, c):
    px, py = q[0] - p[0], q[1] - p[1]
    l2 = px * px + py * py
    t = 0 if l2 == 0 else max(0, min(1, ((c[0] - p[0]) * px + (c[1] - p[1]) * py) / l2))
    return math.hypot(p[0] + t * px - c[0], p[1] + t * py - c[1])


def routes(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == 0 or dy == 0 or abs(dx) == abs(dy):
        return [[]]
    m = min(abs(dx), abs(dy))
    diag = (math.copysign(m, dx), math.copysign(m, dy))
    return [[(a[0] + diag[0], a[1] + diag[1])], [(b[0] - diag[0], b[1] - diag[1])]]


def on_side(d, side):
    return d['side'] == 'V' or d['side'] == side


# ------------------------------------------------------------------ layout

def connected_ok(nodes, traces):
    """Every via has traces on both sides, every node has a trace, and it's all one graph."""
    sides = {}
    for t in traces:
        sides.setdefault(t['a'], set()).add(t['side']); sides.setdefault(t['b'], set()).add(t['side'])
    for n, d in nodes.items():
        if not sides.get(n) or (d['side'] == 'V' and len(sides[n]) < 2):
            return False
    adj = {n: set() for n in nodes}
    for t in traces:
        adj[t['a']].add(t['b']); adj[t['b']].add(t['a'])
    first = next(iter(nodes))
    seen, q = {first}, deque([first])
    while q:
        for m in adj[q.popleft()]:
            if m not in seen:
                seen.add(m); q.append(m)
    return len(seen) == len(nodes)


def gen_layout(rng, W, H, n_front, n_back, n_vias, max_deg=4, min_loops=2, max_loops=4):
    for _ in range(400):
        nodes = {}
        cells = [(x, y) for x in range(W + 1) for y in range(H + 1)]
        rng.shuffle(cells)
        want = ['V'] * n_vias + ['F'] * n_front + ['B'] * n_back
        k = 0
        for side in want:
            for c in cells:
                ok = True
                for d in nodes.values():
                    if on_side(d, side) or side == 'V' or d['side'] == 'V':
                        if max(abs(d['x'] - c[0]), abs(d['y'] - c[1])) < 2:
                            ok = False; break
                    elif (d['x'], d['y']) == c and rng.random() < 0.7:
                        ok = False; break  # stacked front/back nodes: allowed, but not too often
                if ok:
                    k += 1
                    nodes[f'n{k}'] = dict(x=c[0], y=c[1], side=side, type='via' if side == 'V' else 'cap', data=False)
                    cells.remove(c)
                    break
        if len(nodes) < len(want):
            continue
        traces = []
        segs = {'F': [], 'B': []}
        dirs = {}  # (node, side) -> list of exit unit vectors

        def try_add(a, b, side, bends):
            A, B = nodes[a], nodes[b]
            pts = [(A['x'], A['y'])] + bends + [(B['x'], B['y'])]
            if any(not (0 <= p[0] <= W and 0 <= p[1] <= H) for p in bends):
                return False
            for p, q in zip(pts, pts[1:]):
                for n, d in nodes.items():
                    if n in (a, b) or not on_side(d, side):
                        continue
                    if seg_point_dist(p, q, (d['x'], d['y'])) < 0.9:
                        return False
                for (ea, eb, r, s) in segs[side]:
                    if seg_intersect(p, q, r, s):
                        shared = [n for n in (a, b) if n in (ea, eb)]
                        ok = False
                        for n in shared:
                            c = (nodes[n]['x'], nodes[n]['y'])
                            if c in (p, q) and c in (r, s):
                                d1 = unit((q[0] - p[0], q[1] - p[1])) if p == c else unit((p[0] - q[0], p[1] - q[1]))
                                d2 = unit((s[0] - r[0], s[1] - r[1])) if r == c else unit((r[0] - s[0], r[1] - s[1]))
                                ok = d1[0] * d2[0] + d1[1] * d2[1] < 0.99
                        if not ok:
                            return False
            da = unit((pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]))
            db = unit((pts[-2][0] - pts[-1][0], pts[-2][1] - pts[-1][1]))
            for n, dv in ((a, da), (b, db)):
                ex = dirs.get((n, side), [])
                if len(ex) >= (3 if nodes[n]['side'] == 'V' else max_deg):
                    return False
                if any(dv[0] * u[0] + dv[1] * u[1] > 0.92 for u in ex):
                    return False
            for p, q in zip(pts, pts[1:]):
                segs[side].append((a, b, p, q))
            dirs.setdefault((a, side), []).append(da)
            dirs.setdefault((b, side), []).append(db)
            traces.append(dict(a=a, b=b, side=side, bends=[list(p) for p in bends], gate=None))
            return True

        cand = []
        for side in 'FB':
            ns = [n for n, d in nodes.items() if on_side(d, side)]
            for a, b in itertools.combinations(ns, 2):
                A, B = nodes[a], nodes[b]
                dist = max(abs(A['x'] - B['x']), abs(A['y'] - B['y']))
                if 2 <= dist <= 5:
                    cand.append((dist + rng.random() * 2.5, a, b, side))
        cand.sort()
        for _, a, b, side in cand:
            if any({t['a'], t['b']} == {a, b} and t['side'] == side for t in traces) and rng.random() < 0.85:
                continue  # a second trace between the same pair (a loop) - only sometimes
            opts = routes((nodes[a]['x'], nodes[a]['y']), (nodes[b]['x'], nodes[b]['y']))
            rng.shuffle(opts)
            for bends in opts:
                if try_add(a, b, side, [tuple(p) for p in bends]):
                    break
        lv = dict(nodes=nodes, traces=traces, size=(W, H))
        if not connected_ok(nodes, traces):
            continue
        # thin out: drop random traces (keeping everything connected) until each side has ~max_loops loops
        def loops_of(ts):
            return {s: sum(1 for t in ts if t['side'] == s) - sum(1 for d in nodes.values() if on_side(d, s)) + 1
                    for s in 'FB'}
        order = list(range(len(traces)))
        rng.shuffle(order)
        for i in order:
            lp = loops_of([x for x in traces if x is not None])
            t = traces[i]
            if t is None or lp[t['side']] <= max_loops:
                continue
            trial = [x for x in traces if x is not t and x is not None]
            if connected_ok(nodes, trial):
                traces[i] = None
        traces[:] = [t for t in traces if t is not None]
        loops = loops_of(traces)
        if min(loops.values()) < min_loops:
            continue
        lv['loops'] = loops
        return lv
    return None


# ------------------------------------------------------------------ analysis

def search(level, cost=None):
    """Dijkstra over game states. cost(label) -> weight; None = plain BFS lengths. Returns (cost, steps, states)."""
    N, T = level['nodes'], level['traces']
    switches = [n for n, d in N.items() if d['type'] in ('sw', 'and')]
    sidx = {n: i for i, n in enumerate(switches)}
    datas = [n for n, d in N.items() if d.get('data')]
    didx = {n: i for i, n in enumerate(datas)}
    alldata = (1 << len(datas)) - 1
    starts = [n for n, d in N.items() if d['type'] == 'start']
    goals = [n for n, d in N.items() if d['type'] == 'goal']
    if len(starts) != 1 or len(goals) != 1:
        return None, None, 0
    start, goal = starts[0], goals[0]
    sw0 = sum(1 << sidx[n] for n in switches if N[n].get('on'))
    gates = []
    for t in T:
        g = t.get('gate')
        if not g:
            gates.append(None); continue
        mask = sum(1 << sidx[s] for s in g['switches'] if s in sidx)
        gates.append((g['kind'], mask, bool(g.get('open')), bool(g.get('inverted'))))

    def gate_open(i, sw):
        g = gates[i]
        if g is None:
            return True
        kind, mask, op, inv = g
        if kind == 'and':
            allon = mask != 0 and (sw & mask) == mask
            return (not allon) if inv else allon
        return op ^ (bin((sw ^ sw0) & mask).count('1') & 1 == 1)

    ex = {(n, s): exits(level, n, s) for n in N for s in 'FB'}
    st0 = (start, N[start]['side'] if N[start]['side'] != 'V' else 'F', sw0, 0, None)
    w = cost or (lambda label: 1)
    dist = {st0: (0, 0)}
    prev = {st0: None}
    heap = [(0, 0, 0, st0)]
    tie = itertools.count()
    while heap:
        c, steps, _, st = heapq.heappop(heap)
        if dist.get(st, (1e18,))[0] < c:
            continue
        node, side, sw, data, carried = st
        if node == goal and data == alldata and prev[st] and prev[st][1].startswith('move'):
            path = []
            s = st
            while prev[s] is not None:
                p, label = prev[s]
                path.append(label); s = p
            return c, path[::-1], len(dist)
        moves = []
        for (i, other, _) in ex[(node, side)]:
            if not gate_open(i, sw):
                continue
            od = N[other]
            if od['type'] == 'lock' and carried != od.get('pass'):
                continue
            nd = data | (1 << didx[other]) if od.get('data') else data
            moves.append((f'move->{other}', (other, side, sw, nd, carried)))
        t = N[node]['type']
        if t == 'via':
            moves.append(('flip', (node, 'B' if side == 'F' else 'F', sw, data, carried)))
        if t in ('sw', 'and'):
            moves.append((f'press {node}', (node, side, sw ^ (1 << sidx[node]), data, carried)))
        if t == 'holder' and carried != N[node].get('pass'):
            moves.append((f'take {N[node]["pass"]}', (node, side, sw, data, N[node]['pass'])))
        for label, ns in moves:
            nc = c + w(label)
            if ns not in dist or dist[ns][0] > nc:
                dist[ns] = (nc, steps + 1)
                prev[ns] = (st, label)
                heapq.heappush(heap, (nc, steps + 1, next(tie), ns))
    return None, None, len(dist)


def analyse(lv):
    c, sol, states = search(lv)
    if sol is None:
        return None
    BIG = 1000
    tk, _, _ = search(lv, lambda l: BIG + 1 if l.startswith('take') else 1)
    pr, _, _ = search(lv, lambda l: BIG + 1 if l.startswith('press') else 1)
    min_takes = tk // (BIG + 1) if tk is not None else 0
    min_press = pr // (BIG + 1) if pr is not None else 0
    inter = sum(1 for s in sol if not s.startswith('move'))
    colours = {s.split()[1] for s in sol if s.startswith('take')}
    return dict(length=len(sol), inter=inter, min_takes=min_takes, min_press=min_press, states=states, sol=sol,
                colours=len(colours), takes=sum(1 for s in sol if s.startswith('take')),
                presses=sum(1 for s in sol if s.startswith('press')),
                flips=sum(1 for s in sol if s == 'flip'))


# ------------------------------------------------------------------ mechanics

def degree(lv, n, side):
    return sum(1 for t in lv['traces'] if t['side'] == side and n in (t['a'], t['b']))


def plain_nodes(lv, side=None):
    return [n for n, d in lv['nodes'].items() if d['type'] == 'cap' and d['side'] != 'V' and (side is None or d['side'] == side)]


def valid(lv, prof):
    N = lv['nodes']
    for n, d in N.items():
        if d['type'] == 'lock' and degree(lv, n, d['side']) < 2:
            return False
        if d['data'] and d['type'] != 'cap':
            return False
    for t in lv['traces']:
        g = t['gate']
        if not g:
            continue
        if not g['switches']:
            return False
        want = 'and' if g['kind'] == 'and' else 'sw'
        if any(N[s]['type'] != want for s in g['switches']):
            return False
        if g['kind'] == 'and' and len(g['switches']) < 2:
            return False
        # no gate on a trace touching a lock / holder (keeps reading simple)
    used = {s for t in lv['traces'] if t['gate'] for s in t['gate']['switches']}
    for n, d in N.items():
        if d['type'] in ('sw', 'and') and n not in used:
            return False
    gates = [t['gate'] for t in lv['traces'] if t['gate']]
    if len(gates) > prof['max_gates']:
        return False
    per_switch = {}
    for g in gates:
        if g['kind'] == 'normal' and len(g['switches']) > 2:
            return False
        for s in g['switches']:
            per_switch[s] = per_switch.get(s, 0) + 1
    if any(c > 3 for c in per_switch.values()):
        return False
    if prof['switches'] and not any(c >= 2 for s, c in per_switch.items() if N[s]['type'] == 'sw'):
        return False  # at least one switch drives several doors at once
    locks = [d.get('pass') for d in N.values() if d['type'] == 'lock']
    holders = [d.get('pass') for d in N.values() if d['type'] == 'holder']
    if any(c not in holders for c in locks) or any(c not in locks for c in holders):
        return False
    return True


def random_mechanics(lv, rng, prof):
    N = lv['nodes']
    for d in N.values():
        if d['side'] != 'V':
            d['type'] = 'cap'
        d['data'] = False
        d.pop('pass', None); d.pop('on', None)
    for t in lv['traces']:
        t['gate'] = None
    f, b = plain_nodes(lv, 'F'), plain_nodes(lv, 'B')
    N[rng.choice(f)]['type'] = 'start'
    N[rng.choice(b)]['type'] = 'goal'
    caps = plain_nodes(lv)
    rng.shuffle(caps)
    for col in COLOURS[:prof['colours']]:
        for _ in range(prof['holders_per_colour']):
            if caps:
                n = caps.pop(); N[n]['type'] = 'holder'; N[n]['pass'] = col
    lockable = [n for n in caps if degree(lv, n, N[n]['side']) >= 2]
    for i in range(prof['locks']):
        if lockable:
            n = lockable.pop(); caps.remove(n)
            N[n]['type'] = 'lock'; N[n]['pass'] = COLOURS[i % prof['colours']]
    sws = []
    for _ in range(prof['switches']):
        if caps:
            n = caps.pop(); N[n]['type'] = 'sw'; sws.append(n)
    ands = []
    for _ in range(prof['and_switches']):
        if caps:
            n = caps.pop(); N[n]['type'] = 'and'; ands.append(n)
    free = [t for t in lv['traces']]
    rng.shuffle(free)
    for s in sws:
        for _ in range(rng.choice([1, 2, 2])):
            if free:
                t = free.pop()
                t['gate'] = dict(kind='normal', switches=[s], open=rng.random() < 0.4)
    if len(ands) >= 2 and free:
        free.pop()['gate'] = dict(kind='and', switches=list(ands), open=False, inverted=False)
    for _ in range(prof['data']):
        if caps:
            N[caps.pop()]['data'] = True


def mutate(lv, rng, prof):
    lv = copy.deepcopy(lv)
    N, T = lv['nodes'], lv['traces']
    r = rng.random()
    nodes = [n for n, d in N.items() if d['side'] != 'V']
    if r < 0.15:  # swap the roles of two non-via nodes (keeps counts)
        a, b = rng.sample(nodes, 2)
        A, B = N[a], N[b]
        if (A['type'] == 'start' and B['side'] != 'F') or (B['type'] == 'start' and A['side'] != 'F'):
            return None
        if (A['type'] == 'goal' and B['side'] != 'B') or (B['type'] == 'goal' and A['side'] != 'B'):
            return None
        keys = ('type', 'data', 'pass', 'on')
        va = {k: A.get(k) for k in keys}; vb = {k: B.get(k) for k in keys}
        for k in keys:
            A.pop(k, None); B.pop(k, None)
        A.update({k: v for k, v in vb.items() if v is not None}); B.update({k: v for k, v in va.items() if v is not None})
        A.setdefault('data', False); B.setdefault('data', False)
        for t in T:  # gates follow the switch
            if t['gate']:
                t['gate']['switches'] = [b if s == a else a if s == b else s for s in t['gate']['switches']]
    elif r < 0.35:  # move / add / remove a normal gate
        t = rng.choice(T)
        sws = [n for n, d in N.items() if d['type'] == 'sw']
        if t['gate'] and t['gate']['kind'] == 'normal' and rng.random() < 0.4:
            t['gate'] = None
        elif sws:
            t['gate'] = dict(kind='normal', switches=rng.sample(sws, 1 if rng.random() < 0.75 or len(sws) < 2 else 2),
                             open=rng.random() < 0.4)
    elif r < 0.45:  # toggle a gate's start state
        gs = [t for t in T if t['gate'] and t['gate']['kind'] == 'normal']
        if not gs:
            return None
        g = rng.choice(gs)['gate']; g['open'] = not g['open']
    elif r < 0.55:  # move the AND gate
        ands = [n for n, d in N.items() if d['type'] == 'and']
        if len(ands) < 2:
            return None
        for t in T:
            if t['gate'] and t['gate']['kind'] == 'and':
                t['gate'] = None
        rng.choice(T)['gate'] = dict(kind='and', switches=ands, open=False, inverted=rng.random() < 0.15)
    elif r < 0.65:  # data on / off
        caps = plain_nodes(lv)
        if not caps:
            return None
        n = rng.choice(caps); N[n]['data'] = not N[n]['data']
        if sum(1 for d in N.values() if d['data']) > prof['data'] + 1:
            return None
    elif r < 0.75:  # recolour a lock / holder
        ps = [n for n, d in N.items() if d['type'] in ('lock', 'holder')]
        if not ps:
            return None
        n = rng.choice(ps); N[n]['pass'] = rng.choice(COLOURS[:prof['colours']])
    elif r < 0.85:  # move a mechanic node onto a plain cap
        mech = [n for n, d in N.items() if d['type'] in ('lock', 'holder', 'sw', 'and', 'start', 'goal')]
        a = rng.choice(mech)
        side = N[a]['side']
        caps = [n for n in plain_nodes(lv) if (N[a]['type'] not in ('start', 'goal') or N[n]['side'] == side)]
        if not caps:
            return None
        b = rng.choice(caps)
        A, B = N[a], N[b]
        B['type'] = A['type']
        for k in ('pass', 'on'):
            if k in A:
                B[k] = A.pop(k)
        A['type'] = 'cap'
        B['data'], A['data'] = False, B['data']
        for t in T:
            if t['gate']:
                t['gate']['switches'] = [b if s == a else s for s in t['gate']['switches']]
    else:  # re-link a normal gate to another / an extra switch
        gs = [t for t in T if t['gate'] and t['gate']['kind'] == 'normal']
        sws = [n for n, d in N.items() if d['type'] == 'sw']
        if not gs or not sws:
            return None
        g = rng.choice(gs)['gate']
        g['switches'] = rng.sample(sws, 1 if rng.random() < 0.7 or len(sws) < 2 else 2)
    return lv


def score(a, prof):
    if a is None:
        return -1e9
    s = (a['length'] + 2.5 * a['inter'] + 6 * min(a['min_takes'], prof['min_takes'] + 2)
         + 3 * min(a['min_press'], prof['min_press'] + 3) + 4 * math.log(a['states'] + 1))
    s -= 15 * max(0, prof['min_takes'] - a['min_takes'])
    s -= 15 * max(0, prof['min_press'] - a['min_press'])
    s -= 3 * max(0, a['length'] - prof['max_len'])
    if a['colours'] < min(2, prof['colours']):
        s -= 20
    return s


def multi_gate_switch_matters(lv, base_len):
    """A switch linked to 2+ gates where dropping either gate makes the level easier."""
    N, T = lv['nodes'], lv['traces']
    for sname, d in N.items():
        if d['type'] != 'sw':
            continue
        linked = [i for i, t in enumerate(T) if t['gate'] and sname in t['gate']['switches']]
        if len(linked) < 2:
            continue
        good = 0
        for i in linked:
            l2 = copy.deepcopy(lv); l2['traces'][i]['gate'] = None
            c, sol, _ = search(l2)
            if sol is not None and len(sol) < base_len:
                good += 1
        if good >= 2:
            return True
    return False


def prune(lv, prof):
    """Removes every piece that doesn't make the level harder."""
    base = analyse(lv)

    def worse(a):  # a removal is only kept if no difficulty measure drops
        return a is None or any(a[k] < base[k] for k in ('length', 'min_takes', 'min_press', 'inter'))

    changed = True
    while changed:
        changed = False
        N, T = lv['nodes'], lv['traces']
        options = []
        for i, t in enumerate(T):
            if t['gate']:
                options.append(('gate', i))
        for n, d in N.items():
            if d['data']:
                options.append(('data', n))
            if d['type'] in ('lock', 'sw', 'and', 'holder'):
                options.append(('node', n))
        for kind, x in options:
            l2 = copy.deepcopy(lv)
            if kind == 'gate':
                l2['traces'][x]['gate'] = None
            elif kind == 'data':
                l2['nodes'][x]['data'] = False
            else:
                d = l2['nodes'][x]
                if d['type'] == 'holder' and sum(1 for e in l2['nodes'].values() if e['type'] == 'holder' and e.get('pass') == d.get('pass')) < 2:
                    continue  # the only holder of its colour: only removable together with its locks (via lock removal)
                d['type'] = 'cap'; d.pop('pass', None); d.pop('on', None)
                for t in l2['traces']:
                    if t['gate'] and x in t['gate']['switches']:
                        t['gate']['switches'] = [s for s in t['gate']['switches'] if s != x]
                        if not t['gate']['switches'] or (t['gate']['kind'] == 'and' and len(t['gate']['switches']) < 2):
                            t['gate'] = None
            # drop switches left without gates, holders left without locks
            used = {s for t in l2['traces'] if t['gate'] for s in t['gate']['switches']}
            for n, d in l2['nodes'].items():
                if d['type'] in ('sw', 'and') and n not in used:
                    d['type'] = 'cap'; d.pop('on', None)
            lockcols = {d.get('pass') for d in l2['nodes'].values() if d['type'] == 'lock'}
            for n, d in l2['nodes'].items():
                if d['type'] == 'holder' and d.get('pass') not in lockcols:
                    d['type'] = 'cap'; d.pop('pass', None)
            if not valid(l2, prof):
                continue
            a = analyse(l2)
            if not worse(a):
                lv.clear(); lv.update(l2)
                base = analyse(lv)
                changed = True
                break
    return lv


def optimise(lv, rng, prof, iters):
    best, best_s = None, -1e9
    cur, cur_a = None, None
    for _ in range(60):
        random_mechanics(lv, rng, prof)
        if valid(lv, prof):
            a = analyse(lv)
            if a:
                cur, cur_a = copy.deepcopy(lv), a
                break
    if cur is None:
        return None, None
    cur_s = score(cur_a, prof)
    best, best_s = cur, cur_s
    temp0 = 8.0
    for it in range(iters):
        temp = temp0 * (1 - it / iters) + 0.3
        nxt = mutate(cur, rng, prof)
        if nxt is None or not valid(nxt, prof):
            continue
        a = analyse(nxt)
        if a is None:
            continue
        s = score(a, prof)
        if s >= cur_s or rng.random() < math.exp((s - cur_s) / temp):
            cur, cur_s = nxt, s
            if s > best_s:
                best, best_s = copy.deepcopy(nxt), s
    return best, best_s


ITER_SCALE = 4

PROFILES = {
    # name: board, node counts, mechanic counts, targets
    '21': dict(max_gates=4, W=9, H=9, front=8, back=8, vias=4, colours=2, holders_per_colour=1, locks=3, switches=2,
               and_switches=0, data=2, min_takes=3, min_press=3, max_len=45, iters=700),
    '22': dict(max_gates=4, W=10, H=10, front=9, back=9, vias=4, colours=2, holders_per_colour=2, locks=4, switches=1,
               and_switches=2, data=2, min_takes=4, min_press=3, max_len=50, iters=700),
    '23': dict(max_gates=5, W=10, H=11, front=10, back=9, vias=5, colours=2, holders_per_colour=1, locks=4, switches=2,
               and_switches=2, data=3, min_takes=4, min_press=4, max_len=55, iters=800),
    '24': dict(max_gates=6, W=11, H=11, front=10, back=10, vias=5, colours=2, holders_per_colour=2, locks=4, switches=3,
               and_switches=2, data=3, min_takes=4, min_press=5, max_len=60, iters=800),
    '25': dict(max_gates=6, W=12, H=12, front=11, back=11, vias=6, colours=2, holders_per_colour=2, locks=5, switches=3,
               and_switches=2, data=3, min_takes=5, min_press=5, max_len=70, iters=900),
}


def one(args):
    profile, seed = args
    prof = PROFILES[profile]
    rng = random.Random(seed)
    lay = gen_layout(rng, prof['W'], prof['H'], prof['front'], prof['back'], prof['vias'])
    if not lay:
        print(f'[{profile}/{seed}] no layout', flush=True); return None
    lv, s = optimise(lay, rng, prof, prof['iters'] * ITER_SCALE)
    if not lv:
        print(f'[{profile}/{seed}] no start', flush=True); return None
    lv = prune(lv, prof)
    a = analyse(lv)
    errs = check_layout(lv, size=max(prof['W'], prof['H']))
    mg = multi_gate_switch_matters(lv, a['length'])
    print(f'[{profile}/{seed}] score {score(a, prof):.0f} len {a["length"]} inter {a["inter"]} '
          f'minTakes {a["min_takes"]} minPress {a["min_press"]} takes {a["takes"]} presses {a["presses"]} '
          f'flips {a["flips"]} states {a["states"]} loops {lay["loops"]} multiGate {mg} errs {len(errs)}', flush=True)
    return dict(seed=seed, score=score(a, prof), level=lv, analysis={k: v for k, v in a.items() if k != 'sol'},
                multi_gate=mg, errs=errs)


def run(profile, seeds, workers=4):
    from multiprocessing import Pool
    with Pool(workers) as pool:
        results = [r for r in pool.map(one, [(profile, s) for s in seeds]) if r]
    results.sort(key=lambda r: -r['score'])
    json.dump(results, open(f'hard_{profile}.json', 'w'), indent=1)


if __name__ == '__main__':
    run(sys.argv[1], [int(s) for s in sys.argv[2:]] or [1])

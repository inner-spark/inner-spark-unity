"""
Solver + layout checker for Inner Spark levels (mirrors the game's rules).

Level format (coordinates in grid cells, 0..10; cellSize 0.5):
  nodes: name -> dict(x, y, side 'F'|'B'|'V'(via), type: cap|via|start|goal|sw|and|holder|lock,
                      data: bool, pass: 'Green'|'Red'|'Teal')
  traces: list of dict(a, b, side 'F'|'B', bends: [(x,y)...], gate: None | dict(kind 'normal'|'and',
                      switches: [names], open: bool (normal start state) / inverted: bool (and)))
Rules:
  - Sparky moves along a trace on its current side from its node; a gate blocks while closed (both ways);
    a pass lock can only be moved onto carrying its colour.
  - Arriving on a capacitor with data collects it. Arriving on the goal with all data collected wins.
  - Interact (Space): via -> other side; switch -> toggle; holder -> take its pass (replaces the carried one).
  - Normal gate: open = start XOR (number of presses of its switches is odd). AND gate: open while all its
    switches are on (inverted: while not all on).
"""
import itertools, math
from collections import deque

DIRS8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def norm(v):
    l = math.hypot(*v)
    return (0.0, 0.0) if l == 0 else (v[0] / l, v[1] / l)


def on_side(node, side):
    return node['side'] == 'V' or node['side'] == side


def path_of(level, t, from_name):
    a, b = level['nodes'][t['a']], level['nodes'][t['b']]
    pts = [(a['x'], a['y'])] + [tuple(p) for p in t.get('bends', [])] + [(b['x'], b['y'])]
    return pts if from_name == t['a'] else pts[::-1]


def exits(level, name, side):
    out = []
    for i, t in enumerate(level['traces']):
        if t['side'] != side or name not in (t['a'], t['b']):
            continue
        pts = path_of(level, t, name)
        d = norm((pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]))
        other = t['b'] if name == t['a'] else t['a']
        out.append((i, other, d))
    return out


# ------------------------------------------------------------------ layout checks

def seg_intersect(p1, p2, p3, p4):
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)

    def onseg(a, b, c):
        return min(a[0], b[0]) - 1e-9 <= c[0] <= max(a[0], b[0]) + 1e-9 and min(a[1], b[1]) - 1e-9 <= c[1] <= max(a[1], b[1]) + 1e-9

    o1, o2, o3, o4 = orient(p1, p2, p3), orient(p1, p2, p4), orient(p3, p4, p1), orient(p3, p4, p2)
    if o1 != o2 and o3 != o4:
        return True
    if o1 == 0 and onseg(p1, p2, p3): return True
    if o2 == 0 and onseg(p1, p2, p4): return True
    if o3 == 0 and onseg(p3, p4, p1): return True
    if o4 == 0 and onseg(p3, p4, p2): return True
    return False


def check_layout(level, size=10):
    errs = []
    N = level['nodes']
    pos = {}
    for n, d in N.items():
        if not (0 <= d['x'] <= size and 0 <= d['y'] <= size):
            errs.append(f'{n} outside the board')
        key = (d['x'], d['y'])
        for other in pos.get(key, []):
            if N[other]['side'] == 'V' or d['side'] == 'V' or N[other]['side'] == d['side']:
                errs.append(f'{n} overlaps {other}')
        pos.setdefault(key, []).append(n)
    starts = [n for n, d in N.items() if d['type'] == 'start']
    goals = [n for n, d in N.items() if d['type'] == 'goal']
    if len(starts) != 1: errs.append('need exactly 1 start')
    if len(goals) != 1: errs.append('need exactly 1 goal')
    segs = {'F': [], 'B': []}
    for i, t in enumerate(level['traces']):
        a, b = N[t['a']], N[t['b']]
        if not on_side(a, t['side']) or not on_side(b, t['side']):
            errs.append(f'trace {t["a"]}-{t["b"]} on {t["side"]} touches a node on the other side')
        pts = path_of(level, t, t['a'])
        for p, q in zip(pts, pts[1:]):
            dx, dy = q[0] - p[0], q[1] - p[1]
            if dx == 0 and dy == 0:
                errs.append(f'trace {t["a"]}-{t["b"]} has a zero-length segment')
            if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
                errs.append(f'trace {t["a"]}-{t["b"]} segment not 0/45/90 degrees')
            segs[t['side']].append((i, p, q))
        # passes through a node?
        for n, d in N.items():
            if n in (t['a'], t['b']) or not on_side(d, t['side']):
                continue
            c = (d['x'], d['y'])
            for p, q in zip(pts, pts[1:]):
                if seg_intersect(p, q, c, c):
                    errs.append(f'trace {t["a"]}-{t["b"]} runs through {n}')
    for side, ss in segs.items():
        for (i, p, q), (j, r, s) in itertools.combinations(ss, 2):
            if i == j:
                continue
            ti, tj = level['traces'][i], level['traces'][j]
            shared = {ti['a'], ti['b']} & {tj['a'], tj['b']}
            if seg_intersect(p, q, r, s):
                # touching only at a shared endpoint node is fine
                ends = []
                for n in shared:
                    c = (N[n]['x'], N[n]['y'])
                    ends.append(c)
                inter_ok = False
                if shared:
                    # allow if the only contact is the shared node point
                    c = ends[0]
                    if (p == c or q == c) and (r == c or s == c):
                        # check they are not collinear-overlapping
                        d1 = norm((q[0] - p[0], q[1] - p[1])) if p == c else norm((p[0] - q[0], p[1] - q[1]))
                        d2 = norm((s[0] - r[0], s[1] - r[1])) if r == c else norm((r[0] - s[0], r[1] - s[1]))
                        inter_ok = d1[0] * d2[0] + d1[1] * d2[1] < 0.99
                if not inter_ok:
                    errs.append(f'{side}: trace {ti["a"]}-{ti["b"]} crosses {tj["a"]}-{tj["b"]}')
    # exits: unique directions, reachable by 8-way input
    for n, d in N.items():
        for side in ('F', 'B'):
            if not on_side(d, side):
                continue
            ex = exits(level, n, side)
            for (i, o1, d1), (j, o2, d2) in itertools.combinations(ex, 2):
                if d1[0] * d2[0] + d1[1] * d2[1] > 0.92:
                    errs.append(f'{n} ({side}): two exits in the same direction')
            if d['type'] == 'via' and not ex:
                pass
        if d['type'] == 'via':
            if not exits(level, n, 'F') or not exits(level, n, 'B'):
                errs.append(f'{n}: via with traces on one side only')
        if not exits(level, n, 'F') and not exits(level, n, 'B'):
            errs.append(f'{n}: not connected')
        if d['type'] == 'lock':
            if len(exits(level, n, d['side'])) < 2:
                errs.append(f'{n}: lock with fewer than 2 traces')
        if d.get('data') and d['type'] != 'cap':
            errs.append(f'{n}: data on a non-capacitor')
    # gates reference switches of the right kind
    for t in level['traces']:
        g = t.get('gate')
        if not g:
            continue
        for s in g['switches']:
            want = 'and' if g['kind'] == 'and' else 'sw'
            if N[s]['type'] != want:
                errs.append(f'gate on {t["a"]}-{t["b"]}: {s} is not a {want} switch')
    return errs


# ------------------------------------------------------------------ solver

def solve(level, want_all=False):
    N = level['nodes']
    T = level['traces']
    switches = [n for n, d in N.items() if d['type'] in ('sw', 'and')]
    sidx = {n: i for i, n in enumerate(switches)}
    datas = [n for n, d in N.items() if d.get('data')]
    didx = {n: i for i, n in enumerate(datas)}
    alldata = (1 << len(datas)) - 1
    start = next(n for n, d in N.items() if d['type'] == 'start')
    goal = next(n for n, d in N.items() if d['type'] == 'goal')
    start_side = N[start]['side']

    def gate_open(t, sw):
        g = t.get('gate')
        if not g:
            return True
        ons = [(sw >> sidx[s]) & 1 for s in g['switches']]
        if g['kind'] == 'and':
            allon = all(ons)
            return (not allon) if g.get('inverted') else allon
        par = sum(ons) % 2
        return bool(g.get('open', False)) ^ bool(par)

    ex_cache = {(n, s): exits(level, n, s) for n in N for s in 'FB'}
    st0 = (start, start_side, 0, 0, None)
    prev = {st0: None}
    q = deque([st0])
    won = None
    while q:
        st = q.popleft()
        node, side, sw, data, carried = st
        moves = []
        for (i, other, d) in ex_cache[(node, side)]:
            t = T[i]
            if not gate_open(t, sw):
                continue
            od = N[other]
            if od['type'] == 'lock' and carried != od['pass']:
                continue
            nd = data
            if od.get('data'):
                nd |= 1 << didx[other]
            moves.append((f'move->{other}', (other, side, sw, nd, carried)))
        nt = N[node]['type']
        if nt == 'via':
            moves.append(('flip', (node, 'B' if side == 'F' else 'F', sw, data, carried)))
        if nt in ('sw', 'and'):
            moves.append((f'press {node}', (node, side, sw ^ (1 << sidx[node]), data, carried)))
        if nt == 'holder' and carried != N[node]['pass']:
            moves.append((f'take {N[node]["pass"]}', (node, side, sw, data, N[node]['pass'])))
        for label, ns in moves:
            if ns in prev:
                continue
            prev[ns] = (st, label)
            if ns[0] == goal and ns[3] == alldata and label.startswith('move'):
                won = ns
                q.clear()
                break
            q.append(ns)
    if not won:
        return None, len(prev)
    steps = []
    s = won
    while prev[s] is not None:
        p, label = prev[s]
        steps.append(label)
        s = p
    return steps[::-1], len(prev)


def needs(level, check):
    """True if the level becomes unsolvable / easier when a mechanic is removed (rough necessity test)."""
    return check(level)

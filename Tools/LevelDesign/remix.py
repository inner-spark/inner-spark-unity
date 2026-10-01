"""
Remixes the checked Claude levels in the style of the designer's own levels: irregular node positions, bent traces
(Level Editor style 45-degree elbows), dead-end decoys (capacitors, short branches, dead-end vias) and a board sized
to the content. Every candidate is re-checked: layout rules (+ node spacing / trace clearance), solvable, every
mechanic still necessary. Seeded, so the result is reproducible.
"""
import copy, math, random, sys
sys.path.insert(0, '.')
from pcbsolver import check_layout, solve, on_side
from designs import LEVELS
import designs2  # noqa: F401

DIRS8 = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
SIZE = 10
DECOYS = {11: 3, 12: 3, 13: 3, 14: 4, 15: 3, 16: 4, 17: 4, 18: 5, 19: 5, 20: 5}


def routes(a, b):
    """Level Editor routing: straight if 0/45/90, else an elbow (diagonal first or straight first)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == 0 or dy == 0 or abs(dx) == abs(dy):
        return [[]]
    m = min(abs(dx), abs(dy))
    diag = (math.copysign(m, dx), math.copysign(m, dy))
    p1 = (int(a[0] + diag[0]), int(a[1] + diag[1]))
    p2 = (int(b[0] - diag[0]), int(b[1] - diag[1]))
    return [[p1], [p2]]


def seg_point_dist(p, q, c):
    px, py = q[0] - p[0], q[1] - p[1]
    l2 = px * px + py * py
    t = 0 if l2 == 0 else max(0, min(1, ((c[0] - p[0]) * px + (c[1] - p[1]) * py) / l2))
    return math.hypot(p[0] + t * px - c[0], p[1] + t * py - c[1])


def extra_checks(lv):
    N = lv['nodes']
    errs = []
    names = list(N)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            na, nb = N[a], N[b]
            same = na['side'] == 'V' or nb['side'] == 'V' or na['side'] == nb['side']
            if same and max(abs(na['x'] - nb['x']), abs(na['y'] - nb['y'])) < 2:
                errs.append(f'{a} too close to {b}')
    for t in lv['traces']:
        pts = [(N[t['a']]['x'], N[t['a']]['y'])] + [tuple(p) for p in t['bends']] + [(N[t['b']]['x'], N[t['b']]['y'])]
        for n, d in N.items():
            if n in (t['a'], t['b']) or not on_side(d, t['side']):
                continue
            for p, q in zip(pts, pts[1:]):
                if seg_point_dist(p, q, (d['x'], d['y'])) < 1.0:
                    errs.append(f'trace {t["a"]}-{t["b"]} passes too close to {n}')
    return errs


def necessity(lv, base_len):
    def without(fn):
        l2 = copy.deepcopy(lv); fn(l2); s, _ = solve(l2); return None if s is None else len(s)
    if any(t.get('gate') for t in lv['traces']):
        w = without(lambda l: [t.update(gate=None) for t in l['traces']])
        if w is not None and w >= base_len:
            return False
    if any(n['type'] == 'lock' for n in lv['nodes'].values()):
        w = without(lambda l: [n.update(type='cap') for n in l['nodes'].values() if n['type'] == 'lock'])
        if w is not None and w >= base_len:
            return False
    return True


def free_dirs(lv, name, side):
    N = lv['nodes']
    used = []
    for t in lv['traces']:
        if t['side'] != side or name not in (t['a'], t['b']):
            continue
        a = N[name]
        other = t['b'] if name == t['a'] else t['a']
        first = t['bends'][0] if name == t['a'] and t['bends'] else (t['bends'][-1] if t['bends'] else (N[other]['x'], N[other]['y']))
        v = (first[0] - a['x'], first[1] - a['y'])
        l = math.hypot(*v)
        used.append((v[0] / l, v[1] / l))
    out = []
    for d in DIRS8:
        dn = (d[0] / math.hypot(*d), d[1] / math.hypot(*d))
        if all(dn[0] * u[0] + dn[1] * u[1] < 0.75 for u in used):
            out.append(d)
    return out


def add_decoys(lv, count, rng, vias_needed=1, maxx=SIZE, maxy=SIZE):
    N = lv['nodes']
    made, tries = 0, 0
    while made < count and tries < 400:
        tries += 1
        host = rng.choice(list(N))
        hd = N[host]
        side = hd['side'] if hd['side'] != 'V' else rng.choice('FB')
        dirs = free_dirs(lv, host, side)
        if not dirs:
            continue
        d = rng.choice(dirs)
        dist = rng.choice([2, 3])
        x, y = hd['x'] + d[0] * dist, hd['y'] + d[1] * dist
        if not (0 <= x <= maxx and 0 <= y <= maxy):
            continue
        kind = 'via' if made < vias_needed else rng.choice(['cap', 'cap', 'via'])
        name = f'X{made + 1}'
        trial = copy.deepcopy(lv)
        if kind == 'cap':
            trial['nodes'][name] = dict(x=x, y=y, side=side, type='cap', data=False)
            trial['traces'].append(dict(a=host, b=name, side=side, bends=[], gate=None))
        else:
            other = 'B' if side == 'F' else 'F'
            trial['nodes'][name] = dict(x=x, y=y, side='V', type='via', data=False)
            trial['traces'].append(dict(a=host, b=name, side=side, bends=[], gate=None))
            # dead-end capacitor on the other side of the decoy via
            placed = False
            for d2 in rng.sample(DIRS8, 8):
                x2, y2 = x + d2[0] * 2, y + d2[1] * 2
                if 0 <= x2 <= maxx and 0 <= y2 <= maxy:
                    trial['nodes'][name + 'c'] = dict(x=x2, y=y2, side=other, type='cap', data=False)
                    trial['traces'].append(dict(a=name, b=name + 'c', side=other, bends=[], gate=None))
                    placed = True
                    break
            if not placed:
                continue
        if not check_layout(trial) and not extra_checks(trial):
            lv.clear(); lv.update(trial)
            made += 1
    return made


def target_sizes(k, base, rng):
    """Random board sizes to try for a level (smaller for small levels), most interesting first."""
    n = len(base['nodes'])
    lo = 6 if n <= 10 else 7 if n <= 12 else 8
    sizes = [(rng.randint(lo, SIZE), rng.randint(lo, SIZE)) for _ in range(4)]
    return sizes + [(SIZE, SIZE)]  # fallback: the full board


def remix(k, base, tries=1500):
    rng = random.Random(1000 + k)
    base_sol, _ = solve(base)
    for tw, th in target_sizes(k, base, rng):
        best = remix_at(k, base, base_sol, tw, th, rng, tries)
        if best is not None:
            return best
    return None


def remix_at(k, base, base_sol, tw, th, rng, tries):
    best, best_score = None, -1
    for _ in range(tries):
        lv = copy.deepcopy(base)
        mx, my = rng.random() < 0.5, rng.random() < 0.5
        for n, d in lv['nodes'].items():
            x, y = d['x'], d['y']
            if mx: x = SIZE - x
            if my: y = SIZE - y
            x = round(x * tw / SIZE) + rng.choice([-1, 0, 0, 1])   # scale to the target size, then nudge
            y = round(y * th / SIZE) + rng.choice([-1, 0, 0, 1])
            d['x'], d['y'] = min(tw, max(0, x)), min(th, max(0, y))
        ok = True
        for t in lv['traces']:
            a, b = lv['nodes'][t['a']], lv['nodes'][t['b']]
            opts = routes((a['x'], a['y']), (b['x'], b['y']))
            t['bends'] = [list(p) for p in rng.choice(opts)]
        if check_layout(lv) or extra_checks(lv):
            continue
        sol, _ = solve(lv)
        if not sol or len(sol) < len(base_sol) - 1 or not necessity(lv, len(sol)):
            continue
        made = add_decoys(lv, DECOYS[k], rng, vias_needed=1 if k < 15 else 2, maxx=tw, maxy=th)
        if made < DECOYS[k]:
            continue
        sol2, _ = solve(lv)
        if not sol2:
            continue
        bent = sum(1 for t in lv['traces'] if t['bends'])
        xs = {d['x'] for d in lv['nodes'].values()} | {d['y'] for d in lv['nodes'].values()}
        score = bent * 2 + len(xs) + rng.random()
        if score > best_score:
            best, best_score = lv, score
    return best


def shrink(lv):
    """Moves the content to the board's corner and returns the board size (cells)."""
    pts = [(d['x'], d['y']) for d in lv['nodes'].values()] + [tuple(p) for t in lv['traces'] for p in t['bends']]
    minx, miny = min(p[0] for p in pts), min(p[1] for p in pts)
    for d in lv['nodes'].values():
        d['x'] -= minx; d['y'] -= miny
    for t in lv['traces']:
        t['bends'] = [[p[0] - minx, p[1] - miny] for p in t['bends']]
    pts = [(d['x'], d['y']) for d in lv['nodes'].values()] + [tuple(p) for t in lv['traces'] for p in t['bends']]
    return max(1, max(p[0] for p in pts)), max(1, max(p[1] for p in pts))


REMIXED = {}
if __name__ == '__main__':
    only = [int(a) for a in sys.argv[1:]] or sorted(LEVELS)
    for k in only:
        r = remix(k, LEVELS[k])
        if r is None:
            print(f'Level {k}: no valid remix found'); continue
        size = shrink(r)
        r['size'] = size
        sol, states = solve(r)
        errs = check_layout(r) + extra_checks(r)
        vias = sum(1 for d in r['nodes'].values() if d['type'] == 'via')
        decoys = sum(1 for n in r['nodes'] if n.startswith('X'))
        bent = sum(1 for t in r['traces'] if t['bends'])
        print(f'Level {k}: size {size[0]}x{size[1]}, {len(r["nodes"])} nodes ({decoys} decoy, {vias} vias), '
              f'{len(r["traces"])} traces ({bent} bent), solution {len(sol)} (was {len(solve(LEVELS[k])[0])}), errors {len(errs)}, states {states}')
        REMIXED[k] = r
    import json
    json.dump({str(k): v for k, v in REMIXED.items()}, open('remixed.json', 'w'), indent=1)

"""
Finds stuck states: reachable states from which the goal can no longer be reached (e.g. you carried a pass
through a lock, swapped it, and can't get back onto that lock).  python deadends.py <claude_levels_hard.json> [level#]
"""
import json, sys
from collections import deque
sys.path.insert(0, '.')
from pcbsolver import exits


def to_level(L):
    nodes = {n['id']: dict(x=n['x'], y=n['y'], side=n['side'], type=n['type'], data=n['data'],
                           **({'pass': n['passColour']} if n['passColour'] else {}), on=n.get('on', False))
             for n in L['nodes']}
    traces = []
    for t in L['traces']:
        g = None if t['gate'] == 'none' else dict(kind=t['gate'], switches=t['switches'], open=t['gateOpen'],
                                                   inverted=t['gateInverted'])
        traces.append(dict(a=t['a'], b=t['b'], side=t['side'], bends=[(p['x'], p['y']) for p in t['bends']], gate=g))
    return dict(nodes=nodes, traces=traces)


def graph(level):
    N, T = level['nodes'], level['traces']
    switches = [n for n, d in N.items() if d['type'] in ('sw', 'and')]
    sidx = {n: i for i, n in enumerate(switches)}
    datas = [n for n, d in N.items() if d.get('data')]
    didx = {n: i for i, n in enumerate(datas)}
    alldata = (1 << len(datas)) - 1
    start = next(n for n, d in N.items() if d['type'] == 'start')
    goal = next(n for n, d in N.items() if d['type'] == 'goal')
    sw0 = sum(1 << sidx[n] for n in switches if N[n].get('on'))
    ex = {(n, s): exits(level, n, s) for n in N for s in 'FB'}

    def gate_open(t, sw):
        g = t.get('gate')
        if not g:
            return True
        if g['kind'] == 'and':
            allon = all((sw >> sidx[s]) & 1 for s in g['switches'])
            return (not allon) if g.get('inverted') else allon
        return bool(g.get('open')) ^ (sum(((sw ^ sw0) >> sidx[s]) & 1 for s in g['switches']) % 2 == 1)

    def succ(st):
        node, side, sw, data, carried = st
        for (i, other, _) in ex[(node, side)]:
            if not gate_open(T[i], sw):
                continue
            od = N[other]
            if od['type'] == 'lock' and carried != od.get('pass'):
                continue
            nd = data | (1 << didx[other]) if od.get('data') else data
            yield f'move->{other}', (other, side, sw, nd, carried)
        t = N[node]['type']
        if t == 'via':
            yield 'flip', (node, 'B' if side == 'F' else 'F', sw, data, carried)
        if t in ('sw', 'and'):
            yield f'press {node}', (node, side, sw ^ (1 << sidx[node]), data, carried)
        if t == 'holder' and carried != N[node].get('pass'):
            yield f'take {N[node]["pass"]}', (node, side, sw, data, N[node]['pass'])

    st0 = (start, 'F', sw0, 0, None)
    return st0, succ, (lambda st: st[0] == goal and st[3] == alldata)


def dead_states(level):
    st0, succ, won = graph(level)
    prev, edges = {st0: None}, {}
    q = deque([st0])
    while q:
        st = q.popleft()
        edges[st] = []
        if won(st):
            continue  # the level ends here
        for label, ns in succ(st):
            edges[st].append(ns)
            if ns not in prev:
                prev[ns] = (st, label); q.append(ns)
    rev = {}
    for a, bs in edges.items():
        for b in bs:
            rev.setdefault(b, []).append(a)
    good = {s for s in edges if won(s)}
    q = deque(good)
    while q:
        for p in rev.get(q.popleft(), []):
            if p not in good:
                good.add(p); q.append(p)
    dead = [s for s in edges if s not in good]

    def path(s):
        out = []
        while prev[s] is not None:
            p, label = prev[s]; out.append(label); s = p
        return out[::-1]
    return len(edges), dead, path


if __name__ == '__main__':
    data = json.load(open(sys.argv[1], encoding='utf-8'))
    only = [int(a) for a in sys.argv[2:]]
    for L in data['levels']:
        if only and L['number'] not in only:
            continue
        total, dead, path = dead_states(to_level(L))
        print(f'{L["name"]}: {total} reachable states, {len(dead)} stuck')
        # group stuck states by (node, side, carried) and show the shortest way into each kind
        seen = {}
        for s in sorted(dead, key=lambda s: len(path(s))):
            key = (s[0], s[1], s[4])
            if key not in seen:
                seen[key] = path(s)
        for (node, side, carried), p in list(seen.items())[:12]:
            print(f'  stuck at {node} ({side}) carrying {carried}: {" ".join(p)}')

"""
Reads a level prefab (Assets/PCB/Levels/*.prefab) back into the solver's level format, so designer-edited levels
can be analysed / solved:  python prefab2level.py "Assets/PCB/Levels/Tung lvl 11.prefab" [...]
Coordinates come out in grid cells (cellSize from the Board).
"""
import re, sys

GUIDS = {
    '72ad9fd05dbea4c47a3d9c656c5b55f0': 'PcbNode', 'ebfae649ea6128b4990f6df9a586449d': 'Trace',
    '8bf90f56743e9624fbae9303c5e40005': 'Gate', 'fc53f545759af1b4c8e356d98c8239a8': 'AndGate',
    '8c9fddaa857e03b4dabd13c73aa84991': 'Switch', '369dbb1207d015c4ba9f5c38daa3ce35': 'Data',
    'ea47492b5a2abb64eaa9704e58b4a4f9': 'Holder', '2cad7fd292c3b7745837b2845a1ea8ed': 'Lock',
    'd964b7c489f54454db66757f7c244d90': 'Board',
}
NODE_TYPES = ['cap', 'via', 'start', 'goal', 'sw', 'and', 'holder', 'lock']
PASS = {0: None, 1: 'Green', 2: 'Red', 3: 'Teal'}


def parse(path):
    text = open(path, encoding='utf-8').read()
    docs = {}
    for m in re.finditer(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n(.*?)(?=^--- |\Z)', text, re.M | re.S):
        docs[m.group(2)] = (m.group(1), m.group(4))
    go_comps, transforms, names = {}, {}, {}
    for fid, (cls, body) in docs.items():
        g = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', body)
        if cls == '1':
            names[fid] = re.search(r'm_Name: (.*)', body).group(1).strip()
        elif cls == '4' and g:
            p = re.search(r'm_LocalPosition: \{x: ([-\d.e]+), y: ([-\d.e]+), z: ([-\d.e]+)\}', body)
            father = re.search(r'm_Father: \{fileID: (-?\d+)\}', body).group(1)
            transforms[g.group(1)] = (float(p.group(1)), float(p.group(2)), father, fid)
        elif cls == '114' and g:
            s = re.search(r'm_Script: \{fileID: \d+, guid: (\w+)', body)
            kind = GUIDS.get(s.group(1)) if s else None
            if kind:
                go_comps.setdefault(g.group(1), {})[kind] = (fid, body)
    # world (board-local) position: sum of local positions up the hierarchy
    by_tf = {v[3]: (v[0], v[1], v[2]) for v in transforms.values()}

    def board_pos(go):
        x, y, father, _ = transforms[go]
        while father != '0' and father in by_tf:
            px, py, father = by_tf[father]
            if father == '0':
                break  # the root Board itself
            x += px; y += py
        return x, y

    board = next(c['Board'][1] for c in go_comps.values() if 'Board' in c)
    cell = float(re.search(r'cellSize: ([\d.]+)', board).group(1))
    size = tuple(int(v) for v in re.search(r'sizeInCells: \{x: (\d+), y: (\d+)\}', board).groups())

    nodes, comp2node, switch2node = {}, {}, {}
    for go, comps in go_comps.items():
        if 'PcbNode' not in comps:
            continue
        fid, body = comps['PcbNode']
        t = NODE_TYPES[int(re.search(r'\n  type: (\d+)', body).group(1))]
        layer = int(re.search(r'\n  layer: (\d+)', body).group(1))
        x, y = board_pos(go)
        name = names.get(go, fid)
        base = name
        k = 2
        while name in nodes:
            name = f'{base}#{k}'; k += 1
        d = dict(x=round(x / cell, 3), y=round(y / cell, 3), side='V' if t == 'via' else ('B' if layer else 'F'),
                 type=t, data='Data' in comps)
        for kind in ('Holder', 'Lock'):
            if kind in comps:
                d['pass'] = PASS[int(re.search(r'\n  pass: (\d+)', comps[kind][1]).group(1))]
        if 'Switch' in comps:
            d['on'] = bool(int(re.search(r'isOn: (\d)', comps['Switch'][1]).group(1)))
            switch2node[comps['Switch'][0]] = name
        nodes[name] = d
        comp2node[fid] = name

    traces = []
    for go, comps in go_comps.items():
        if 'Trace' not in comps:
            continue
        body = comps['Trace'][1]
        a = comp2node.get(re.search(r'from: \{fileID: (-?\d+)\}', body).group(1))
        b = comp2node.get(re.search(r'\n  to: \{fileID: (-?\d+)\}', body).group(1))
        if not a or not b:
            continue
        layer = int(re.search(r'\n  layer: (\d+)', body).group(1))
        bends = [(round(float(x) / cell, 3), round(float(y) / cell, 3))
                 for x, y in re.findall(r'- \{x: ([-\d.e]+), y: ([-\d.e]+)\}', body.split('bends:')[1])]
        gate = None
        for kind in ('AndGate', 'Gate'):
            if kind in comps:
                gb = comps[kind][1]
                sws = [switch2node.get(s) for s in re.findall(r'- \{fileID: (-?\d+)\}', gb.split('switches:')[1].split('\n  m', 1)[0])]
                gate = dict(kind='and' if kind == 'AndGate' else 'normal', switches=[s for s in sws if s],
                            open=bool(int(re.search(r'isOpen: (\d)', gb).group(1))))
                if kind == 'AndGate':
                    gate['inverted'] = bool(int(re.search(r'inverted: (\d)', gb).group(1)))
                break
        traces.append(dict(a=a, b=b, side='B' if layer else 'F', bends=bends, gate=gate))
    return dict(nodes=nodes, traces=traces, size=size)


if __name__ == '__main__':
    sys.path.insert(0, '.')
    from pcbsolver import solve, check_layout
    for p in sys.argv[1:]:
        lv = parse(p)
        N = lv['nodes']
        sol, states = solve(lv)
        kinds = {}
        for d in N.values():
            kinds[d['type']] = kinds.get(d['type'], 0) + 1
        gates = [t['gate'] for t in lv['traces'] if t['gate']]
        print(f'== {p.split("/")[-1]}  size {lv["size"]}  nodes {len(N)} {kinds}  traces {len(lv["traces"])} '
              f'(bent {sum(1 for t in lv["traces"] if t["bends"])})  gates {len(gates)}  '
              f'data {sum(1 for d in N.values() if d["data"])}')
        for t in lv['traces']:
            if t['gate']:
                print(f'   gate {t["a"]} - {t["b"]}: {t["gate"]}')
        multi = {}
        for g in gates:
            for s in g['switches']:
                multi[s] = multi.get(s, 0) + 1
        print('   switch -> #gates:', multi, ' switches on at start:', [n for n, d in N.items() if d.get('on')])
        print('   solution:', len(sol) if sol else None, 'actions, states', states)
        if sol:
            print('   ', ' '.join(sol))
        errs = check_layout(lv, size=max(lv['size']) + 2)
        if errs:
            print('   layout notes:', errs[:6])

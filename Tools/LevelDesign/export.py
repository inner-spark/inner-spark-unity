"""Exports the checked designs to Unity JSON + a solution sheet."""
import json, sys, os
sys.path.insert(0, '.')
from pcbsolver import check_layout, solve
from designs import LEVELS
import designs2  # noqa: F401  (adds 16-20)

MECH = {11: 'Data, AND switch', 12: 'Normal switch, Data, AND switch', 13: 'Pass, AND switch', 14: 'Pass',
        15: 'Normal switch, Data', 16: 'Pass, AND switch', 17: 'Pass, Data, AND switch',
        18: 'All', 19: 'All', 20: 'All'}

out_dir = sys.argv[1]
levels, sheet = [], ['# Claude levels 11-20 — solutions\n',
                     'Generated and checked by a solver that mirrors the game rules (8-way moves, vias, switches / gates,',
                     'data, passes). "Shortest" = fewest actions (moves + Space presses).\n']
REMIXED = {int(k): v for k, v in json.load(open('remixed.json')).items()}
for k in sorted(LEVELS):
    lv = REMIXED.get(k, LEVELS[k])
    errs = check_layout(lv)
    sol, _ = solve(lv)
    assert not errs and sol, (k, errs)
    N = lv['nodes']
    nodes = [dict(id=n, type=d['type'], side=d['side'], x=d['x'], y=d['y'], data=bool(d.get('data')),
                  passColour=d.get('pass', '')) for n, d in N.items()]
    traces = []
    for t in lv['traces']:
        g = t.get('gate') or {}
        traces.append(dict(a=t['a'], b=t['b'], side=t['side'],
                           bends=[dict(x=p[0], y=p[1]) for p in t.get('bends', [])],
                           gate=g.get('kind', 'none'), gateOpen=bool(g.get('open', False)),
                           gateInverted=bool(g.get('inverted', False)), switches=g.get('switches', [])))
    size = lv.get('size', (10, 10))
    levels.append(dict(name=f'Claude lvl {k}', number=k, sizeX=size[0], sizeY=size[1], nodes=nodes, traces=traces))
    moves = sum(1 for s in sol if s.startswith('move'))
    decoys = sum(1 for n in N if n.startswith('X'))
    sheet.append(f'## Claude lvl {k} — {MECH[k]}\n')
    sheet.append(f'Board {size[0]}x{size[1]}, {len(N)} nodes ({decoys} decoys), {len(lv["traces"])} traces. '
                 f'Shortest solution: **{len(sol)} actions** ({moves} moves).\n')
    pretty = []
    for s in sol:
        if s.startswith('move->'): pretty.append('→ ' + s[6:])
        elif s == 'flip': pretty.append('**flip**')
        elif s.startswith('press'): pretty.append('**press ' + s[6:] + '**')
        elif s.startswith('take'): pretty.append('**take ' + s[5:] + '**')
    sheet.append(' '.join(pretty) + '\n')
    sheet.append('Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock '
                 '(R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).\n')

os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, 'claude_levels.json'), 'w', encoding='utf-8') as f:
    json.dump(dict(levels=levels), f, indent=1)
with open(os.path.join(out_dir, 'Claude_levels_solutions.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(sheet))
print('exported', len(levels), 'levels to', out_dir)

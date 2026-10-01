import sys, copy
sys.path.insert(0, '.')
from pcbsolver import check_layout, solve
from designs import LEVELS
import designs2  # adds 16-20

only = [int(a) for a in sys.argv[1:]] or sorted(LEVELS)
for k in only:
    lv = LEVELS[k]
    errs = check_layout(lv)
    sol, explored = solve(lv)
    print(f'===== Level {k}: {len(lv["nodes"])} nodes, {len(lv["traces"])} traces, layout errors: {len(errs)}')
    for e in errs: print('   !', e)
    if sol is None:
        print('   UNSOLVABLE (states explored', explored, ')')
        continue
    print(f'   shortest solution: {len(sol)} actions ({sum(1 for s in sol if s.startswith("move"))} moves), states {explored}')
    print('   ', ' | '.join(sol))
    # does every mechanic matter? remove gates / turn locks into capacitors and compare
    def without(fn):
        l2 = copy.deepcopy(lv); fn(l2); s, _ = solve(l2); return None if s is None else len(s)
    if any(t.get('gate') for t in lv['traces']):
        print('   without gates:', without(lambda l: [t.update(gate=None) for t in l['traces']]))
    if any(n['type'] == 'lock' for n in lv['nodes'].values()):
        print('   locks as capacitors:', without(lambda l: [n.update(type='cap') for n in l['nodes'].values() if n['type'] == 'lock']))
    sides = {n['side'] for n in lv['nodes'].values()}
    print('   sides used:', sorted(sides))

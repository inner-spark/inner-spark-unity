"""The ten Claude levels (11-20). Coordinates in grid cells (board 10x10, nodes on even cells)."""

def L():
    return {'nodes': {}, 'traces': []}

def node(lv, name, x, y, side, type_='cap', data=False, pass_=None):
    lv['nodes'][name] = dict(x=x, y=y, side=side, type=type_, data=data, **({'pass': pass_} if pass_ else {}))

def tr(lv, a, b, side, bends=(), gate=None):
    lv['traces'].append(dict(a=a, b=b, side=side, bends=list(bends), gate=gate))

def gate(kind, switches, open_=False, inverted=False):
    return dict(kind=kind, switches=list(switches), open=open_, inverted=inverted)

LEVELS = {}

# ---------------------------------------------------------------- 11: Data + AND
lv = L()
node(lv, 'S', 2, 2, 'F', 'start')
node(lv, 'D1', 2, 6, 'F', data=True)
node(lv, 'A1', 6, 6, 'F', 'and')
node(lv, 'C1', 6, 2, 'F')
node(lv, 'V1', 10, 2, 'V', 'via')
node(lv, 'V2', 10, 8, 'V', 'via')
node(lv, 'A2', 6, 10, 'B', 'and')
node(lv, 'D2', 2, 10, 'B', data=True)
node(lv, 'C3', 6, 4, 'B')
node(lv, 'G', 2, 4, 'B', 'goal')
tr(lv, 'S', 'D1', 'F'); tr(lv, 'D1', 'A1', 'F'); tr(lv, 'A1', 'C1', 'F'); tr(lv, 'S', 'C1', 'F'); tr(lv, 'C1', 'V1', 'F')
tr(lv, 'A1', 'V2', 'F', [(8, 8)])
tr(lv, 'V2', 'A2', 'B', [(8, 10)]); tr(lv, 'A2', 'D2', 'B')
tr(lv, 'V1', 'C3', 'B', [(8, 4)])
tr(lv, 'C3', 'G', 'B', gate=gate('and', ['A1', 'A2']))
LEVELS[11] = lv

# ---------------------------------------------------------------- 12: Normal + Data + AND
lv = L()
node(lv, 'S', 0, 4, 'F', 'start')
node(lv, 'N1', 4, 4, 'F', 'sw')
node(lv, 'C1', 4, 8, 'F')
node(lv, 'D2', 0, 8, 'F', data=True)
node(lv, 'A2', 8, 8, 'F', 'and')
node(lv, 'C2', 4, 0, 'F')
node(lv, 'A1', 8, 0, 'F', 'and')
node(lv, 'V1', 8, 4, 'V', 'via')
node(lv, 'D1', 8, 8, 'B', data=True)
node(lv, 'G', 4, 4, 'B', 'goal')
tr(lv, 'S', 'N1', 'F')
tr(lv, 'N1', 'C1', 'F', gate=gate('normal', ['N1'], open_=True))
tr(lv, 'C1', 'D2', 'F'); tr(lv, 'C1', 'A2', 'F')
tr(lv, 'N1', 'C2', 'F', gate=gate('normal', ['N1'], open_=False))
tr(lv, 'C2', 'A1', 'F')
tr(lv, 'N1', 'V1', 'F')
tr(lv, 'V1', 'D1', 'B')
tr(lv, 'V1', 'G', 'B', gate=gate('and', ['A1', 'A2']))
LEVELS[12] = lv

# ---------------------------------------------------------------- 13: Pass + AND
lv = L()
node(lv, 'S', 0, 0, 'F', 'start')
node(lv, 'HR', 4, 0, 'F', 'holder', pass_='Red')
node(lv, 'LR', 4, 4, 'F', 'lock', pass_='Red')
node(lv, 'A1', 8, 4, 'F', 'and')
node(lv, 'V1', 4, 8, 'V', 'via')
node(lv, 'V2', 8, 0, 'V', 'via')
node(lv, 'HG', 8, 8, 'B', 'holder', pass_='Green')
node(lv, 'LG', 0, 8, 'B', 'lock', pass_='Green')
node(lv, 'A2', 0, 4, 'B', 'and')
node(lv, 'C', 0, 0, 'B')
node(lv, 'G', 4, 0, 'B', 'goal')
tr(lv, 'S', 'HR', 'F'); tr(lv, 'HR', 'LR', 'F'); tr(lv, 'LR', 'A1', 'F'); tr(lv, 'LR', 'V1', 'F'); tr(lv, 'A1', 'V2', 'F')
tr(lv, 'V1', 'HG', 'B'); tr(lv, 'V1', 'LG', 'B'); tr(lv, 'LG', 'A2', 'B'); tr(lv, 'A2', 'C', 'B')
tr(lv, 'C', 'G', 'B', gate=gate('and', ['A1', 'A2']))
tr(lv, 'V2', 'HG', 'B')
LEVELS[13] = lv

# ---------------------------------------------------------------- 14: Pass
lv = L()
node(lv, 'S', 0, 0, 'F', 'start')
node(lv, 'HR', 0, 4, 'F', 'holder', pass_='Red')
node(lv, 'LR1', 4, 4, 'F', 'lock', pass_='Red')
node(lv, 'V1', 8, 4, 'V', 'via')
node(lv, 'HG', 8, 8, 'B', 'holder', pass_='Green')
node(lv, 'LG', 4, 4, 'B', 'lock', pass_='Green')
node(lv, 'HR2', 4, 8, 'B', 'holder', pass_='Red')
node(lv, 'LR2', 0, 8, 'B', 'lock', pass_='Red')
node(lv, 'G', 0, 4, 'B', 'goal')
tr(lv, 'S', 'HR', 'F'); tr(lv, 'HR', 'LR1', 'F'); tr(lv, 'LR1', 'V1', 'F')
tr(lv, 'V1', 'HG', 'B'); tr(lv, 'V1', 'LG', 'B'); tr(lv, 'LG', 'HR2', 'B'); tr(lv, 'HR2', 'LR2', 'B'); tr(lv, 'LR2', 'G', 'B')
LEVELS[14] = lv

# ---------------------------------------------------------------- 15: Normal + Data
lv = L()
node(lv, 'S', 0, 0, 'F', 'start')
node(lv, 'N1', 4, 0, 'F', 'sw')
node(lv, 'C1', 8, 0, 'F')
node(lv, 'D1', 4, 4, 'F', data=True)
node(lv, 'N2', 0, 4, 'F', 'sw')
node(lv, 'D3', 8, 8, 'F', data=True)
node(lv, 'V1', 8, 4, 'V', 'via')
node(lv, 'D2', 8, 8, 'B', data=True)
node(lv, 'G', 4, 4, 'B', 'goal')
tr(lv, 'S', 'N1', 'F')
tr(lv, 'N1', 'C1', 'F', gate=gate('normal', ['N1', 'N2'], open_=False))
tr(lv, 'N1', 'D1', 'F'); tr(lv, 'D1', 'N2', 'F')
tr(lv, 'C1', 'V1', 'F')
tr(lv, 'V1', 'D3', 'F', gate=gate('normal', ['N1'], open_=False))
tr(lv, 'V1', 'D2', 'B', gate=gate('normal', ['N1'], open_=True))
tr(lv, 'V1', 'G', 'B', gate=gate('normal', ['N2'], open_=False))
LEVELS[15] = lv

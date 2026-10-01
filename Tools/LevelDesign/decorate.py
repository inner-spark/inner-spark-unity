"""
Scatters LED decorations over the final level prefabs (Assets/PCB/Levels/*.prefab, not Archive).

  python decorate.py wrappers     - writes the 15 game-ready LED prefabs (Decor_LED_<shape>_<colour>.prefab: the
                                    artist's LED model stood up out of the board face, scaled down so it doesn't
                                    read as a node) and lists them in the theme as LED decoration variants
  python decorate.py scatter      - (re)places the LEDs on every final level: both sides, light density
                                    (~1 per 8 free spots, 3..8 per side), >= 2 cells apart, clear of nodes and
                                    traces, no shape+colour repeated on a side. Seeded by level name, so re-running
                                    gives the same result; it replaces the LEDs it placed before (and only those).

Edits the YAML directly (Unity re-imports on focus). Decorations never affect gameplay.
"""
import glob, hashlib, math, os, random, re, sys, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prefab2level import parse

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
LEVELS = os.path.join(ROOT, 'Assets/PCB/Levels')
DECOR = os.path.join(ROOT, 'Assets/PCB/Prefabs/Final/Decoration')
PROPS = os.path.join(ROOT, 'Assets/Import Asset/LevelProps')
THEME = os.path.join(ROOT, 'Assets/PCB/PcbTheme.asset')
SHAPES, COLOURS = (1, 2, 3), ('Blue', 'Green', 'Purple', 'Red', 'Yellow')
SCALE = 0.6
LED_TYPE = 8  # DecorType.LED
WRAPPER_ROOT = 8100000000000000001  # root GameObject fileID inside each wrapper prefab
TAG = 'LED Decor'  # name prefix of the scattered objects (so a re-run can replace them)


def guid_of(path):
    return re.search(r'^guid: (\w+)', open(path + '.meta', encoding='utf-8').read(), re.M).group(1)


def fid(*parts):
    """Stable positive 63-bit fileID from a name."""
    return int(hashlib.sha1('/'.join(map(str, parts)).encode()).hexdigest()[:15], 16) + 10 ** 15


# ------------------------------------------------------------------ wrappers

WRAPPER = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &{root}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {tf}}}
  m_Layer: 0
  m_Name: {name}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{tf}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {root}}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children:
  - {{fileID: {stripped}}}
  m_Father: {{fileID: 0}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!1001 &{inst}
PrefabInstance:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_Modification:
    serializedVersion: 3
    m_TransformParent: {{fileID: {tf}}}
    m_Modifications:
{mods}    m_RemovedComponents: []
    m_RemovedGameObjects: []
    m_AddedGameObjects: []
    m_AddedComponents: []
  m_SourcePrefab: {{fileID: 100100000, guid: {fbx}, type: 3}}
--- !u!4 &{stripped} stripped
Transform:
  m_CorrespondingSourceObject: {{fileID: -8679921383154817045, guid: {fbx}, type: 3}}
  m_PrefabInstance: {{fileID: {inst}}}
  m_PrefabAsset: {{fileID: 0}}
"""

META = """fileFormatVersion: 2
guid: {guid}
PrefabImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""


def wrappers():
    entries = []
    for shape in SHAPES:
        for colour in COLOURS:
            name = f'Decor_LED_{shape}_{colour}'
            fbx = guid_of(os.path.join(PROPS, f'LED_{shape}_{colour}.fbx'))
            tf, inst, stripped = fid(name, 'tf'), fid(name, 'inst'), fid(name, 'stripped')
            values = {  # stand the Y-up model up out of the board face (-Z), like the other Final props
                'm_LocalPosition.x': 0, 'm_LocalPosition.y': 0, 'm_LocalPosition.z': 0,
                'm_LocalRotation.w': 0.7071068, 'm_LocalRotation.x': -0.7071068,
                'm_LocalRotation.y': 0, 'm_LocalRotation.z': 0,
                'm_LocalEulerAnglesHint.x': -90, 'm_LocalEulerAnglesHint.y': 0, 'm_LocalEulerAnglesHint.z': 0,
                'm_LocalScale.x': SCALE, 'm_LocalScale.y': SCALE, 'm_LocalScale.z': SCALE,
            }
            mods = ''.join(f'    - target: {{fileID: -8679921383154817045, guid: {fbx}, type: 3}}\n'
                           f'      propertyPath: {k}\n      value: {v}\n      objectReference: {{fileID: 0}}\n'
                           for k, v in values.items())
            mods += (f'    - target: {{fileID: 919132149155446097, guid: {fbx}, type: 3}}\n'
                     f'      propertyPath: m_Name\n      value: LED_{shape}_{colour}\n      objectReference: {{fileID: 0}}\n')
            path = os.path.join(DECOR, name + '.prefab')
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(WRAPPER.format(root=WRAPPER_ROOT, tf=tf, inst=inst, stripped=stripped, name=name,
                                       mods=mods, fbx=fbx))
            if not os.path.exists(path + '.meta'):
                with open(path + '.meta', 'w', encoding='utf-8', newline='\n') as f:
                    f.write(META.format(guid=uuid.uuid4().hex))
            entries.append(f'  - type: {LED_TYPE}\n    prefab: {{fileID: {WRAPPER_ROOT}, guid: {guid_of(path)}, type: 3}}\n')
    # theme: LED decoration variants (replacing earlier LED entries)
    t = open(THEME, encoding='utf-8').read()
    m = re.search(r'(  decorationPrefabs:\n)((?:  - type: \d+\n    prefab: .*\n)*)', t)
    kept = [e for e in re.findall(r'  - type: \d+\n    prefab: .*\n', m.group(2)) if not e.startswith(f'  - type: {LED_TYPE}\n')]
    t = t[:m.start()] + m.group(1) + ''.join(kept) + ''.join(entries) + t[m.end():]
    open(THEME, 'w', encoding='utf-8', newline='\n').write(t)
    print(f'wrote {len(entries)} LED prefabs and listed them in the theme')


# ------------------------------------------------------------------ scatter

def seg_dist(p, q, c):
    px, py = q[0] - p[0], q[1] - p[1]
    l2 = px * px + py * py
    t = 0 if l2 == 0 else max(0, min(1, ((c[0] - p[0]) * px + (c[1] - p[1]) * py) / l2))
    return math.hypot(p[0] + t * px - c[0], p[1] + t * py - c[1])


def choose(lv, side, rng):
    """Positions (in cells) + (shape, colour, rotation) for one side."""
    W, H = lv['size']
    N = lv['nodes']
    nodes = [(d['x'], d['y'], d['type']) for d in N.values() if d['side'] in ('V', side)]
    segs = []
    for t in lv['traces']:
        if t['side'] != side:
            continue
        a, b = N[t['a']], N[t['b']]
        pts = [(a['x'], a['y'])] + [tuple(p) for p in t['bends']] + [(b['x'], b['y'])]
        segs += list(zip(pts, pts[1:]))
    cands = []
    for x2 in range(-1, 2 * W + 2):  # half-cell steps, including the board margin (1 cell)
        for y2 in range(-1, 2 * H + 2):
            c = (x2 / 2, y2 / 2)
            if any(math.hypot(c[0] - x, c[1] - y) < (1.6 if t in ('goal', 'start') else 1.2) for x, y, t in nodes):
                continue
            if any(seg_dist(p, q, c) < 0.8 for p, q in segs):
                continue
            cands.append(c)
    whole = sum(1 for c in cands if c[0] == int(c[0]) and c[1] == int(c[1]))
    count = max(3, min(8, round(whole / 8)))
    rng.shuffle(cands)
    picked = []
    for c in cands:
        if all(max(abs(c[0] - p[0]), abs(c[1] - p[1])) >= 2 for p in picked):
            picked.append(c)
            if len(picked) == count:
                break
    combos = [(s, col) for s in SHAPES for col in COLOURS]
    rng.shuffle(combos)
    # spread the shapes: take combos round-robin by shape so one side doesn't get three of the same shape
    by_shape = {s: [c for c in combos if c[0] == s] for s in SHAPES}
    order = list(SHAPES)
    rng.shuffle(order)
    looks = []
    while len(looks) < len(picked):
        for s in order:
            if by_shape[s] and len(looks) < len(picked):
                looks.append(by_shape[s].pop())
    return [(p, s, col, rng.choice(range(0, 360, 45))) for p, (s, col) in zip(picked, looks)]


def remove_old(text):
    """Drops LED decorations (and their container) placed by an earlier run."""
    docs = re.split(r'(?=^--- !u!)', text, flags=re.M)
    head, docs = docs[0], docs[1:]
    drop = set()
    for d in docs:
        m = re.match(r'--- !u!1 &(-?\d+)\n', d)
        if m and (re.search(rf'm_Name: {TAG}', d) or re.search(r'm_Name: Decorations \(LED\)\n', d)):
            drop.add(m.group(1))
    if not drop:
        return text, set()
    keep, removed_tf = [], set()
    for d in docs:
        m = re.match(r'--- !u!(\d+) &(-?\d+)', d)
        g = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', d)
        if m.group(2) in drop or (g and g.group(1) in drop):
            if m.group(1) == '4':
                removed_tf.add(m.group(2))
            continue
        keep.append(d)
    out = head + ''.join(keep)
    for tf in removed_tf:
        out = out.replace(f'  - {{fileID: {tf}}}\n', '')
    return out, removed_tf


def scatter():
    script = guid_of(os.path.join(ROOT, 'Assets/Script/PcbDecoration.cs'))
    wrap = {(s, c): guid_of(os.path.join(DECOR, f'Decor_LED_{s}_{c}.prefab')) for s in SHAPES for c in COLOURS}
    for path in sorted(glob.glob(os.path.join(LEVELS, '*.prefab'))):
        name = os.path.basename(path)[:-7]
        text = open(path, encoding='utf-8').read()
        text, _ = remove_old(text)
        open(path, 'w', encoding='utf-8', newline='\n').write(text)
        lv = parse(path)
        cell = float(re.search(r'cellSize: ([\d.]+)', text).group(1))
        rng = random.Random(name)
        placed = {s: choose(lv, s, rng) for s in 'FB'}
        # root transform = the one with m_Father 0
        root_tf = re.search(r'--- !u!4 &(-?\d+)\nTransform:\n(?:(?!^--- ).*\n)*?  m_Father: \{fileID: 0\}', text, re.M).group(1)
        cont_go, cont_tf = fid(name, 'container go'), fid(name, 'container tf')
        docs, children = [], []
        for side in 'FB':
            for i, ((x, y), shape, colour, rot) in enumerate(placed[side]):
                key = (name, side, i)
                go, tf, mb = fid(*key, 'go'), fid(*key, 'tf'), fid(*key, 'mb')
                children.append(tf)
                docs.append(f"""--- !u!1 &{go}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {tf}}}
  - component: {{fileID: {mb}}}
  m_Layer: 0
  m_Name: {TAG} {side}{i + 1:02d}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{tf}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go}}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: {x * cell}, y: {y * cell}, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {{fileID: {cont_tf}}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!114 &{mb}
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go}}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 11500000, guid: {script}, type: 3}}
  m_Name:
  m_EditorClassIdentifier: Assembly-CSharp::Pcb.PcbDecoration
  type: {LED_TYPE}
  layer: {0 if side == 'F' else 1}
  rotationDegrees: {rot}
  model: {{fileID: {WRAPPER_ROOT}, guid: {wrap[(shape, colour)]}, type: 3}}
""")
        kids = ''.join(f'  - {{fileID: {c}}}\n' for c in children)
        docs.insert(0, f"""--- !u!1 &{cont_go}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {cont_tf}}}
  m_Layer: 0
  m_Name: Decorations (LED)
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{cont_tf}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {cont_go}}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children:
{kids}  m_Father: {{fileID: {root_tf}}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
""")
        # hook the container under the root transform
        m = re.search(rf'(--- !u!4 &{root_tf}\nTransform:\n(?:(?!^--- ).*\n)*?  m_Children:\n(?:  - .*\n)*)', text, re.M)
        if not m:  # 'm_Children: []'
            text = re.sub(rf'(--- !u!4 &{root_tf}\nTransform:\n(?:(?!^--- ).*\n)*?)  m_Children: \[\]\n',
                          rf'\1  m_Children:\n  - {{fileID: {cont_tf}}}\n', text, count=1, flags=re.M)
        else:
            text = text[:m.end()] + f'  - {{fileID: {cont_tf}}}\n' + text[m.end():]
        text = text.rstrip('\n') + '\n' + ''.join(docs)
        open(path, 'w', encoding='utf-8', newline='\n').write(text)
        print(f'{name}: front {len(placed["F"])}, back {len(placed["B"])}')


if __name__ == '__main__':
    {'wrappers': wrappers, 'scatter': scatter}[sys.argv[1]]()

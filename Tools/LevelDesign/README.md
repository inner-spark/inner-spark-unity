# Level design tools (Python, outside Unity)

Used to design and check the "Claude lvl 11–20" stages. Python 3, no extra packages.

- `pcbsolver.py` — mirrors the game rules: layout checker (unique 8-way exits, no same-side crossings,
  no trace through a node, 0/45/90° segments, locks with 2+ traces, vias on both sides) and a solver
  (shortest solution over moves, via flips, switch presses, data, passes).
- `designs.py` / `designs2.py` — the base puzzle designs (grid-cell coordinates).
- `run.py [levels…]` — check + solve the base designs, and test that every mechanic is needed.
- `remix.py [levels…]` — the designer-style remix: irregular positions, Level-Editor-style bent traces,
  dead-end decoys (capacitors, branches, dead-end vias), board sized to content. Seeded; writes
  `remixed.json`. Every result is re-checked (solvable, mechanics still needed, spacing / clearance).
- `export.py <Assets/PCB/LevelData>` — writes `claude_levels.json` + `Claude_levels_solutions.md`.

In Unity: **Tools > PCB > Build Claude Levels** builds the prefabs from `claude_levels.json`.

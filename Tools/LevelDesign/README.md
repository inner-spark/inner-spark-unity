# Level design tools (Python, outside Unity)

Puzzle analysis and generation for Inner Spark. Python 3, no extra packages. Run them from this folder.

## Checking the game's levels
- `solutions.py <out.md>` — the solution sheet for every level in the Level List, read straight from the
  level prefabs: shortest solution, the pass takes / switch presses any solution needs, stuck states.
  The current sheet is [`Docs/Level_solutions.md`](../../Docs/Level_solutions.md) — re-run it after editing a level.
- `deadends.py <level prefab>…` — lists a level's stuck states (reachable, but the goal can't be reached any
  more) with the shortest way into each.
- `prefab2level.py <level prefab>…` — reads a level prefab into the solver format and prints its stats +
  shortest solution.
- `pcbsolver.py` — the rules: layout checker (unique 8-way exits, no same-side crossings, no trace through
  a node, 0/45/90° segments, locks with 2+ traces, vias on both sides) and the solver (shortest solution
  over moves, via flips, switch presses incl. switches that start ON, data, passes).

## Decorations
- `decorate.py wrappers` — writes the 15 `Decor_LED_*` prefabs (the artist's LEDs stood up, 60 %) and lists
  them in the theme. `decorate.py scatter` — (re)places 3–8 LEDs per side on every final level (seeded,
  replaces only its own LEDs).

## How the Claude levels were made (history)
- Stages 11–20 (first versions): `designs.py` / `designs2.py` (base designs), `run.py` (check + solve,
  every mechanic needed), `remix.py` (designer-style remix → `remixed.json`).
- Bonus stages 21–23: `gen.py <profile> [seeds…]` — legal looping layout, then a simulated-annealing search
  over mechanics scored by difficulty (length, interactions, *forced* pass takes / switch presses), then a
  prune so every piece matters. Results: `hard_21.json`… (picked seeds: 21 → 10, 22 → 8, 23 → 1).
- They were turned into prefabs by an editor tool (`ClaudeLevelBuilder.cs`) fed by `export.py` /
  `export_hard.py`. Those were removed in the 2026-10-04 clean-up (the final levels are the designer's
  edited copies); restore them from git history if levels ever need generating again.

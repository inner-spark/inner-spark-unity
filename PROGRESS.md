# Progress Log

Tracks what's been done and the current state of the project. Newest entries on top.
See [DESIGN.md](DESIGN.md) for the design reference / architecture map.

---

## 2026-10-04 — clean-up + project snapshot

### Snapshot: where the project stands
- **Game:** 20 main stages in 5 consoles (ColekoTelestar 1 · Altary2600 2–5 · NESt 6–12 · Gamerboi 13–17 ·
  PlayingState 18–20) → Ending, then 3 bonus stages (21–23) → Main Menu. Mechanics: vias, normal / AND
  switches + gates, data, Red / Green passes. All 23 stages solvable (solver-checked).
- **Look:** board colour per console, one capacitor + gate model per stage, LED decorations, gate and pass
  lock fades, main-menu-style UI everywhere (Stage Select, HUD, Pause, Dialog, Win).
- **Flow:** music carries over between stages; Space finishes / continues dialog and goes to the next stage;
  Stage Select glides to the furthest stage; Ending shows "Bonus stages unlocked!".
- **Docs:** README (jam submission), DESIGN (reference), this log, `Docs/Level_solutions.md` (every stage's
  solution + stuck states), `Assets/Script/PCB/KeySystem_README.md` (passes), `Tools/LevelDesign/README.md`.
- **Still open:** Music / SFX sliders (`VolumeSlider.cs` is ready, not placed); audio balance + missing clips;
  intro dialog for stages 4, 9, 12, 14, 16 and the bonus stages (optional); stage 3's dialog line was cut off
  in the sheet; intro cinematics (system ready, none made); README: key art, other members' AI usage,
  Kenney kits / third-party sounds / Upheaval font licence.
- **Designer to decide:** stuck states — Gamerboi 14 (take Red → LR1 → flip at V1 → take Green: the data
  behind the red lock can't be reached any more) and Gamerboi 16 (take Green → LG → take Red at HR) trap the
  player within a few moves; bonus 21–22 have a few too. Restart gets out; fine if intended.

### Clean-up (all removals are in git history)
- **Deleted scripts:** `KeyGateMechanic.cs` (never used), `Editor/OrganizeLevels.cs` (one-shot, done),
  `Editor/ClaudeLevelBuilder.cs` (its menus would re-add archived levels to the Level List).
- **Deleted data:** `Assets/PCB/LevelData/` (the builder's JSON + solution sheets for the original Claude
  levels, which no longer match the final, designer-edited stages), `Tools/LevelDesign/export*.py` (fed the
  builder), `Tools/LevelDesign/__pycache__/` (+ `.gitignore` entry), `spark-kun.slnx` (old project name).
- **Kept on purpose:** `VolumeSlider.cs` (sliders later), `StageIntro.cs` / `FadeGroup.cs` (intro cinematics),
  archived levels in `Assets/PCB/Levels/Archive`, the Python solver / generator (history + analysis).
- **New:** `Tools/LevelDesign/solutions.py` → `Docs/Level_solutions.md` (re-run after editing a level);
  `deadends.py` now reads level prefabs (and uses the start node's side).
- Docs updated: DESIGN (removed tools, solutions sheet), README (project structure, stuck stages),
  KeySystem_README (Pass Colour tool, lock fade, no KeyGate), Tools README rewritten.
- Both assemblies compile without the removed scripts.

## 2026-10-04 — Space skips / continues dialog and goes to the next stage

- `DialogController`: Space = Continue (first press finishes a line still typing, the next one advances).
- `LevelManager`: on the win pop-up Space = Next Level (Enter / South still press the selected button).
- Space isn't a UI Submit key (default UI actions: Enter / South), so it never double-presses a selected
  button; Spark drops presses made while input is locked, so the Space that closes the dialog doesn't
  also flip / press anything. README + DESIGN controls tables updated.

## 2026-10-04 — dialogs wired, ending bonus text, Stage Select auto-scroll, docs refreshed

- **Dialogs:** one `Assets/PCB/Dialog/LvlN_Intro.asset` per stage from the designer's sheet (speaker Sparky,
  Sparky portrait), assigned on stages 1–3, 5–8, 10, 11, 13, 15, 17–20 (the sheet has no line for 4, 9, 12,
  14, 16). The Altary2600 line "Next stop: Atari 2600!" moved from stage 5 to stage 2 (as on the sheet);
  stage 1 keeps its two lines + the sheet's tutorial line "Go right using the directional input!" last.
  ⚠ Stage 3's line was cut off in the sheet screenshot — ends "…less than a text message!" for now.
  Dialog body text auto-sizes (44 → 26) so the long lines fit the box.
- **Ending scene:** new inactive "BonusUnlocked" text (yellow upheavtt 40, bottom strip under the credits:
  "Bonus stages unlocked! Find them in Stage Select"); EndingScreen now has Levels + Bonus Unlocked Text.
- **Stage Select auto-scroll:** opens at stage 1, waits 0.3 s, glides (0.8 s) to the furthest unlocked
  stage and selects it (Enter plays it); a click / wheel / up-down cancels the glide. Afterwards keyboard /
  gamepad selection is kept in view. (`autoScrollDelay`, `autoScrollTime`.)
- **README:** team from the ending credits (Banh Mi Team, 5 members + roles), known issues refreshed
  (stuck states in bonus 21–22, stages without dialog), AI table updated (bonus stages, recoloured board
  textures, LED scatter, UI layout), music / SFX credited to Andrii (TODO: confirm third-party sounds).
- **DESIGN.md** refreshed (bonus stages, consoles + board colours, final list, LED type, fades, UI style).

## 2026-10-04 — pause menu + HUD buttons styled (SampleScene)

Edited `SampleScene.unity` directly (backup kept outside the project during the session):
- **Pause panel:** dark see-through overlay (was white placeholder), a "PAUSED" title (upheavtt, 120, yellow),
  Resume / Quit to Menu / Quit Game in the main-menu style: `Button_main` sprite, 500×100, yellow tint
  (orange hover), upheavtt 50 dark text.
- **HUD (top-right):** Pause (`Button_Pause`) and Restart (`Button_Reset`) icon buttons, 110×112, same yellow
  tint. Now assigned on PauseMenu (`pauseButton` / `restartButton`), so they gray out during the stage intro /
  dialog and Restart while paused. The Pause button now calls `PauseMenu.Toggle` (press again = resume).
- Not touched: Win panel and Dialog panel (still placeholder look).
- **Follow-up (designer feedback):** yellow buttons now 500×140 and their labels are centred on the button's
  face, not the whole sprite (TMP margins keep the text off `Button_main`'s side + drop shadow: right 23/475,
  bottom 39/142 of the size). Pause buttons re-spaced.
- **Dialog box** per the designer's demo, but with the yellow button: Sparky portrait (`Portrait_Sparky`) in
  `Portrait_frame` bottom-left, `TextField` box (1170×250) with centred upheavtt 44 dark text, yellow Continue
  (320×96) under its right edge; speaker name hidden (the demo has none); no tint over the scene.
  `DialogController.defaultPortrait` (Sparky) is used when a line has no portrait; the two dialog assets now
  point at Sparky (they had Unity's built-in placeholder sprite).
- **Win screen:** full-screen lighter overlay (55 %) so the finished board shows, "STAGE CLEAR!" title, yellow
  Next Level / Restart (500×140). Wording confirmed by the designer.
- Fix: the portrait Frame was copied from the win panel's background Image, which had scale 8 - the designer
  reset the Frame in Unity; the win background's own scale was set back to 1 too.
- Final pass: pause + win buttons back to the main menu's size (500×100, font 50, label still centred on the
  face), re-spaced; "STAGE CLEAR!" 140; the speaker name shows again, under the portrait ("Sparky", yellow
  upheavtt 44) - dialog assets' speakerName fixed from "Sparkie" to "Sparky".

## 2026-10-04 — Stage Select: two-line labels, board-coloured buttons, scrolling fixed

- **Scroll bug:** the Scroll View's Movement Type was Unrestricted (scrolls forever into blank space) and the
  ButtonContainer's Content Size Fitter didn't size it (height 0, centred pivot). `StageSelectController` now
  fixes this when the panel opens: Clamped movement, Vertical Fit = Preferred Size, top pivot at the top of the
  view, and it starts scrolled to the top. (Done in code, so the scene doesn't need editing.)
- **Labels** always two lines: "NESt:" / "Level 6" (split at the level name's colon); bonus stages
  "Bonus:" / "Level 1". Auto-size on, so long names (PlayingState) shrink instead of spilling.
- **Colours:** new `PcbTheme.boardTileColours` (tile → button colour, filled for all 8 tiles). Each button
  takes its level's board colour (Normal / Selected = colour, Highlighted lighter, Pressed darker) with
  white text on dark colours (`lightTextColour`). Tiles not listed keep the template's yellow.

## 2026-10-04 — parody console names, per-stage capacitor / gate models, gate fade

- **Names back to the artist's parody spellings** (designer's call - they match the console models):
  ColekoTelestar 1 · Altary2600 2–5 · NESt 6–12 · Gamerboi 13–17 · PlayingState 18–20 · Bonus 21–23
  (file "<Console> - Level NN", in game "<Console>: Level N"; GUIDs kept, Level List intact).
- **One random capacitor + gate model per stage** (Board > Look > Capacitor / Gate, from the theme's 6 capacitor
  and 2 gate variants; no two stages in a row share a capacitor). The hand-painted per-object capacitor models
  (ColekoTelestar 1, Altary2600 2 & 4) and gate models (NESt 7 & 8) were cleared so the stage's choice shows
  (goal models untouched).
- **Gates fade** like the pass lock: `BoardVisuals.ShowGateState(look, open, fade)` → `LockVisual.FadeTo` when a
  switch press changes a gate in play (`GateMechanic.SetOpen`); building / starting state stays instant.

## 2026-10-04 — random LED decorations on every final board

- `DecorType.LED` added (appended, value 8). 15 game-ready wrappers `Assets/PCB/Prefabs/Final/Decoration/
  Decor_LED_<1-3>_<Blue|Green|Purple|Red|Yellow>.prefab`: the artist's LED model stood up out of the board face
  (−90° X like the other Final props) at 60 % scale so it doesn't read as a node; all 15 listed in the theme as
  LED decoration variants (Level Editor Decor / Paint).
- `Tools/LevelDesign/decorate.py scatter` placed them on all 23 final levels: both sides, light density (3–8 per
  side; compact boards mostly get 3), ≥ 2 cells apart, ≥ 1.2 cells from nodes (1.6 from start / goal), ≥ 0.8
  cell from traces, may use the board margin, random 45° rotation, no shape+colour repeated on a side, seeded by
  level name. They live under a "Decorations (LED)" object; re-running replaces only those. Decorations never
  touch gameplay. Backup of the pre-decoration levels was kept outside the project during the session.

## 2026-10-03 (late night) — board colour per console

Each final level's own Board Tile (`Board.look.boardTile`, Level Editor > Look) set to one of the six existing
artist tiles (`Assets/PCB/Prefabs/Final/Board Tile *.prefab`): Coleco Telstar **Purple** · Atari 2600
**Bronze** (wood-panel era) · NES **Black** · Gameboy **Green** (pea-green screen) · PS1 **Blue** · Bonus
**Red**. Theme default stays Green. Trace / node models unchanged.
- Then two new tiles, made like the artist's other colours (one model copy per colour): "Board Tile Grey"
  (warm grey, Gameboy body) and "Board Tile Light Grey" (cool light grey, PS1). Each = `PCBboard_module(Light)Grey.fbx`
  (copy of the green model, its material slot remapped) + `M_PCBboard(Light)Grey.mat` (copy of the green material)
  + colour texture `T_PCB_Base(Light)Grey1K.png` (the green texture recoloured, same circuit pattern; same normal /
  metallic maps). Added to the theme's Board Tile choices; set on Gameboy 13–17 and PS1 18–20.
  Final: Coleco Telstar Purple · Atari 2600 Bronze · NES Black · Gameboy Grey · PS1 Light Grey · Bonus Red.

## 2026-10-03 (late night) — final level order + names (Tools > PCB > Organize Final Levels)

One-shot editor menu `OrganizeLevels.cs` (asks first, can't be Ctrl+Z'd; delete the script after it ran):
renames the final 23 prefabs to "<Console> - Level NN.prefab", sets their in-game name to "<Console>: Level N",
moves every other level prefab to `Assets/PCB/Levels/Archive`, and sets the Level List to exactly these 23 with
Main Stage Count 20. Moves go through the AssetDatabase, so references (Level List, scenes) survive.
Mapping (designer's answers): 1 Level 01 Tung (Coleco Telstar) · 2–5 Level 02–05 Tung (Atari 2600) ·
6 Level 06 Tung, 7 Level 08 Tung, 8 Level 9 Tung, 9 "Level  9 true Tung", 10 Level 10 true Tung,
11 Tung lvl 11, 12 Tung lvl 12 true (NES — "NESt" was a typo) · 13–17 Tung lvl 13–17 (Gameboy) ·
18–20 Tung lvl 18–20 (PS1) · Bonus 21–23 = Tung lvl 21–23 ("Bonus: Level 21…").
Archived: Level 1/02–07/14, Level 09 true Tung, Tung lvl 12, Claude lvl 11–23 (re-running Build Claude
(Hard) Levels would recreate those in Levels/ and append them to the list again).
Dialogs from the designer's sheet are not set up yet (text may still change).

## 2026-10-03 (late night) — bonus stages after stage 20 + music carries on between stages

- **Music:** `LevelManager.EnterStage` no longer restarts the gameplay track - it keeps playing from stage to
  stage (and on restarts); coming from the menu still switches to it.
- **Bonus stages:** `LevelList.mainStageCount` (0 = whole list is the main game, as before). The ending plays
  after the last main stage; the levels after it are Bonus stages. Progress is linear, so finishing the last
  main stage already unlocks Bonus 1 (and Main Menu > Play continues there).
  - Stage Select labels them "Bonus 1, 2, 3" (only shown once unlocked, like every stage).
  - Winning the last Bonus stage fades back to the Main Menu (`LevelManager.mainMenuScene`).
  - `EndingScreen.levels` + `bonusUnlockedText`: optional "Bonus stages unlocked!" object, shown when the list
    has bonus stages.
- Designer setup: Level List → final order (20 main stages, then Claude lvl 21–23), **Main Stage Count = 20**;
  Ending scene → add the text, assign it + the Level List on EndingScreen.

## 2026-10-03 (late night) — bonus levels: Claude lvl 21–23 (hard / hard / very hard)

**Brief:** harder levels for the bonus set — switches that move several doors at once, passes that must be
carried and swapped several times, multiple loops (no same-side crossings), board up to 12×12. Studied the
designer's edits (Tung lvl 11–20): compact boards, lots of data on dead ends / loops, switches driving 2–3
gates (one open, one shut), gates on two switches, front/back nodes sharing a cell.
- New tools in `Tools/LevelDesign/`: `prefab2level.py` (reads a level prefab back into solver format),
  `gen.py` (layout → simulated-annealing mechanics search → prune; scores the *forced* minimum pass takes and
  switch presses, not just length), `export_hard.py`, `deadends.py` (finds stuck states). The solver now
  supports switches that start ON.
- **Claude lvl 21** (hard, 8×9): 45 actions, ≥ 4 forced pass takes, ≥ 4 forced presses; N2 drives 3 doors.
  Has a stuck pocket (green pass behind a red lock) — kept on purpose.
- **Claude lvl 22** (hard, 10×9): 50 actions, ≥ 3 takes, ≥ 5 presses; N1 swaps two doors + an AND gate.
  One stuck spot (taking Green at HG1 on the wrong trip).
- **Claude lvl 23** (very hard, 10×11): 55 actions, ≥ 3 takes, ≥ 4 presses, 5 gates (N1 on three doors, one
  door on N1 + N2, an AND gate), 2 data. No stuck states.
- Data: `Assets/PCB/LevelData/claude_levels_hard.json`; solutions + stuck states:
  `Claude_levels_hard_solutions.md`. **Tools > PCB > Build Claude Hard Levels** builds them and appends them
  to the Level List (11–20 untouched). Stuck states are allowed (designer's call); Restart gets out.

## 2026-10-03 (late night) — pass lock fades instead of popping

- `LockVisual.FadeTo(bool)`: the Locked look fades out over the Unlocked one (or back in when Sparky
  switches to another pass) instead of switching instantly. During the fade the Locked renderers use
  transparent copies of their URP Lit materials (alpha on `_BaseColor`, shadow off once below half),
  then go back to the originals. `fadeTime` (default 0.4 s) is on the LockVisual component of each
  `Pass_Lock_*` prefab. `Show()` stays instant (editor, level build, gates and goals are unchanged).
- `KeyLockMechanic.Refresh` now calls `FadeTo`. Runtime assembly compiles cleanly.
- Relies on the transparent URP Lit variant being in the build (already used by `M_Sparky_Face`).

## 2026-10-03 (late night) — Level Editor: moving nodes keeps traces tidy

Moving a node (Node tool, drag) always kept its links and mechanics (they reference the objects), but the
trace bends are stored as absolute positions, so elbows went stale. In `PcbLevelEditorWindow.cs`:
- **Auto re-route while dragging:** traces attached to the dragged node that have **0 or 1 bend** are
  redrawn like the Trace tool does (straight, or one 45° elbow) and keep their elbow on the same side.
  Traces with **2+ bends** (hand-shaped) are left alone; fix those with the bend handles or Ctrl+Click.
- **Ctrl+Click a trace** (Node tool, empty spot near a trace): re-routes it as a clean elbow, whatever
  its bend count; Ctrl+Click again flips the elbow (straight-first ↔ diagonal-first). Holding Ctrl
  highlights the trace under the cursor. Undoable (Ctrl+Z); help text updated.
- Helpers: `RerouteTrace`, `ElbowBends`, `HighlightTrace`. The editor assembly compiles cleanly.

## 2026-10-03 (night) — 10 puzzle levels: Claude lvl 11–20

**Designer's brief:** 10 medium stages, board ≤ 10×10 (compact), every stage two-sided, 1 start + 1 goal,
mechanics per stage: 11 D A · 12 N D A · 13 P A · 14 P · 15 N D · 16 P A · 17 P D A · 18–20 all
(D data, N normal switch, A AND switch, P pass).

**How they were made:**
- Designed outside Unity with a **solver + layout checker** that mirror the game rules (8-way moves,
  vias, normal / AND / inverted-AND gates, data, pass holders / locks). Every level is checked for:
  no layout errors (unique exit directions, no same-side crossings, no trace through a node, 0/45/90°
  segments, locks with ≥ 2 traces, vias on both sides), **solvable**, and **every mechanic matters**
  (removing the gates / turning locks into capacitors makes it easier).
- Shortest solutions: 11: 17 · 12: 19 · 13: 15 · 14: 13 · 15: 20 · 16: 18 · 17: 27 · 18: 23 ·
  19: 21 · 20: 32 actions. Full step-by-step solutions: `Assets/PCB/LevelData/Claude_levels_solutions.md`.
- Level data: `Assets/PCB/LevelData/claude_levels.json`. **Tools > PCB > Build Claude Levels**
  (`ClaudeLevelBuilder`, editor only) builds `Assets/PCB/Levels/Claude lvl 11…20.prefab` (10×10 cells,
  theme default look, no dialog) and **appends them to the Level List** (re-running overwrites them).
- Not playtested — feel / pacing / readability to be judged in Unity; Level 14 is the most linear.
- **Remix in the designer's style** (studied the Tung levels: irregular positions on any cell, mostly
  bent traces, 2–9 dead-end decoys, 3–9 vias, board sized to content): every node nudged 0–1 cell off
  the lattice (some layouts mirrored), traces re-routed Level-Editor style (straight / 45° elbow),
  **3–8 dead-end decoys** per level (capacitors, branches, dead-end vias to a capacitor on the other
  side; ≥ 1 decoy via, ≥ 2 from level 15), boards shrunk to content (8×10 … 10×10). Re-checked: no
  layout errors, node spacing ≥ 2 cells, traces ≥ 1 cell clear of other nodes, same shortest solutions,
  every mechanic still needed. Decoys are dead ends, so they can't create shortcuts.
- **Random board sizes:** each level now gets a random target size (smaller allowed for smaller levels;
  falls back to 10×10 if too tight), its layout is scaled to it and decoys stay inside it. Result:
  11: 7×8 · 12: 8×7 · 13: 9×9 · 14: 9×6 · 15: 6×8 · 16: 8×9 · 17: 10×10 · 18: 9×9 · 19: 7×8 · 20: 8×8.
  All re-checked (same shortest solutions, mechanics needed, no layout errors).
- Python tools kept in the repo: **`Tools/LevelDesign/`** (solver, designs, remix, export + README).
  Re-run **Tools > PCB > Build Claude Levels** to rebuild the prefabs (overwrites earlier builds).

## 2026-10-03 (evening) — game jam requirements: README + windowed build

- **`README.md`** created from the jam's required sections (title, key art, team, engine & language,
  launch, controls, known issues, AI-generated content log, credits) — TODOs for the team to fill in:
  key art image, team roles, other members' AI usage, music/SFX source, Kenney kits, Upheaval font licence.
- **Windowed build** (jam: "720p or 1080p, windowed"): `UiScalingSetup` now sets the Player default to a
  **1920×1080 resizable window** (was full screen) — run **Tools > PCB > Set Up UI Scaling (1920x1080)**.
- Still to do from the jam list: Product Name `spark-kun` → `Inner Spark`; decide the final Level List;
  push to the jam's Git space; Windows build tested from another folder / PC (launch, controls, audio,
  win, exit); early WIP upload; ask whether a lose state is expected.

## 2026-10-03 (later) — pass system rebuilt around Pass Holder / Pass Lock nodes

**Designer's rules:** colours **Green, Red, Teal** (match the art). **Pass Holder** node = endless
source of its colour; Space / Enter takes the pass (any other carried pass is destroyed); the
hovering pass shrinks away and **refills when Sparky leaves**; already carrying it → nothing. **No
dropping** anywhere. **Pass Lock** node: Sparky can't move onto it without the matching pass (never
used up); two looks — **Unlocked while Sparky carries its colour**, Locked otherwise. The carried pass
floats **beside** Sparky, ~⅓ its size. Pass on a holder hovers like data. Validate: a lock with < 2
traces. The many-keys gate is out of scope for now.

**Changes (edited the dev's files where possible):**
- `KeyType` → None / Green / Red / Teal (+ `ToColor`, `NextPass`). `NodeType.PassHolder`, `PassLock`.
- `KeyNodeMechanic` → **Pass Holder** logic (`pass` colour, `Take`, refill on leave).
  `SecurityGateMechanic` → renamed **`KeyLockMechanic`** (git mv) → **Pass Lock** node logic
  (`CanArrive`, Locked/Unlocked look follows `Spark.OnCarriedKeyChanged`). `KeyGateMechanic` left
  unused. `KeySystem_README.md` rewritten. **Deleted** the dev's `Test Key 06/07` test levels.
- `NodeMechanic.CanArrive(spark)` (new hook, checked in `Spark.TryMove` before leaving).
  `HoverVisual.Show()` (pop back in).
- `Spark`: Space/Enter on a holder takes its pass; carried pass indicator (`carriedPassOffset`,
  `carriedPassScale` 0.35) — hidden while travelling, mirrored on the back; pickup sound.
- Theme **Passes**: Green / Red / Teal × (Holder, Pass, Lock Model); coloured placeholders until set.
  Board/BoardVisuals build the holder model + hovering pass and the lock model (starts Locked).
- Level Editor: Node types **Pass Holder** / **Pass Lock** (script added automatically); **Pass** tool
  (click to cycle colour); validation (lock < 2 traces, lock colour without holder, holder colour
  without lock, stale scripts). Look section skips pass node types (models are per colour).
- Compiles (runtime + editor, 0 warnings).
- **Tested by the designer (prefabs set up): working.** Tweaks: the pass hovered too far from its
  holder → own theme setting **Pass Height** (0.3, was sharing Data Height 0.45); carried pass ×1.5
  (`Spark.carriedPassScale` 0.35 → 0.525).
- Art gap: `Key_Lock_*` has no unlocked variant — ask Andrii (stopgap in the lock prefab's Unlocked child).
- **Pass still looked shifted (up/right) off its holder:** perspective — anything floating towards the
  camera appears pushed away from the screen centre. `HoverVisual.towardCamera` (passes only): in play
  the pass sits on the line from its node to the camera, so it always looks right above the holder.
  Also: the `Key_*` card isn't centred on its own origin — centre it on the root in `Pass_*` prefabs.
  **Then reverted at the designer's request:** after centring the `Pass_*` prefabs, passes hover
  exactly like data pickups again (straight out of the board, `Pass Height`); the camera-line option
  was removed from `HoverVisual`. Pass Height lowered 0.3 → **0.22** (closer to the board) — final.
- **Pass Colour choice in the Level Editor** (default **Red**): Node tool shows it when placing a Pass
  Holder / Lock (new ones get that colour); the Pass tool now *sets* a clicked holder / lock to it
  (instead of cycling). Several colours per stage = several holders / locks with different colours.
- **Bug fix — hovering items rotated with their node:** data pickups, passes and the goal lock are built
  inside the node's group, so a node's Rotation spun them too. `BoardVisuals.BuildHover` now cancels the
  node's spin on the hovering item → always upright on screen (the node model still rotates).

## 2026-10-03 — merged Nghia's key / pass system ("add key pass", `2d011ee`)

**What it adds:** `KeyType` (None, Red, Blue, Green, Yellow, SecurityCard); `KeyNodeMechanic` (a key /
pass lying on a capacitor); Sparky carries one at a time — **Space / Enter** on a capacitor picks up,
drops or swaps (`Spark.carriedKey`, `OnCarriedKeyChanged`); `KeyGateMechanic` (uses up N keys of a
colour, then opens for good); `SecurityGateMechanic` (passable only while carrying the pass, never used
up). Key models `Red Among Us` / `Blue Among Us`. Guide: `Assets/Script/PCB/KeySystem_README.md`.
**Designer's intent: the "pass"** — hold it to get through gates that need it; passes stay in the
level and are picked up by standing on their node and pressing Space / Enter; several per level.

**Merge (his branch was based on 09-29):**
- `GateMechanic.cs`: kept ours (board-built gates); `model` reads his `customGatePrefab`
  (`FormerlySerializedAs`). New `UsesSwitches` (false for key / pass gates): the Link tool won't attach
  switches to them and Validate skips the "no switch" warning.
- `Spark.cs`: ours + his key logic (`TryUseKey`, `SetCarriedKey`, Enter binding); no debug log; pickup
  sound on pick up / drop.
- `SecurityGateMechanic` rewritten for board-built gates: opens/closes (with the gate sound) as the
  carried pass changes, model shows OPEN/CLOSED. `KeyGateMechanic`: floating "1/3" text and logs
  dropped (no on-screen text).
- **Level 06 / 07 name clash:** both sides made different levels with those names. Kept ours; his are
  now **`Test Key 06`** (key gates) and **`Test Key 07`** (pass gate, model → `Gate_1`) — **not** in
  the Level List (designer: test levels only). Level List = ours.
- `SampleScene`: ours (his side only had a work-in-progress board in it). `Capacitor Demo 1`,
  `Trace_Path_Blocked`: stay deleted. `UserSettings` layout: stays untracked.
- Compiles (runtime + editor, 0 warnings); **not tested in Unity yet** — see the test steps in chat.

**Open:** key visuals are runtime-only spheres / Among Us models (not visible in the editor, not
hidden with their board side) — designer will look at visuals; could join the hover system + theme
(`Key_*` art). Enter = same as Space (designer asked for an explanation).

## 2026-10-02 (night) — project cleanup + keyboard / gamepad menus

From a project review (items 2, 3, 4, 5, 7 chosen by the designer):
- **Volume sliders:** checked — none exist in any scene yet (the `VolumeSlider` script is ready).
- **Git:** `UserSettings/` was ignored but 4 files had been committed earlier → untracked them
  (`git rm -r --cached UserSettings`, local files kept). Commit that removal.
- **Removed debug logging** on every gate change / block and switch toggle (`GateMechanic`,
  `SwitchMechanic`).
- **Gamepad / keyboard:** Start pauses; menus select their first button when they open (Main Menu →
  Play, Stage Select → stage 1, Back → Play, Pause → Resume, Win pop-up → Next Level) via new
  `UiSelect`. With a win pop-up, its buttons handle Submit (LevelManager's own Space/Enter → Next is
  only used without one — avoids Enter on Restart also triggering Next).
- **Deleted unused files:** Unity template `TutorialInfo/` + `Readme.asset`; `Start Demo`, `Goal Demo`,
  `Via Demo`, `Capacitor Demo`, `Capacitor Demo 1`, `Trace_Path_Blocked` prefabs. Level 1's five
  capacitors painted with the two demo capacitors were reset to the default (theme: Capacitor Blue) —
  repaint if wanted. **Kept** `Registor` (the theme's Resistor decoration) and `Diode`.
- **DESIGN.md rewritten** to match the current project.
- Compiles (runtime + editor, 0 warnings); not tested in Unity yet.

**Still open from the review:** rename `SampleScene` → `Gameplay`; editor rebuild work every frame;
one shared input setup (rebinding); player options; splitting `Spark.cs` / the Level Editor.
Decide the final Level List (13 entries incl. the "Tung" set).

## 2026-10-02 (evening) — UI scales with the screen (1920×1080 design size)

- **Bug:** going full screen, the UI stayed the same size in pixels. All three scenes' Canvas
  Scalers were on **Constant Pixel Size** (reference 800×600 unused).
- **Fix:** new editor menu **Tools > PCB > Set Up UI Scaling (1920x1080)** (`UiScalingSetup`): every
  root Canvas in every build scene → **Scale With Screen Size**, reference **1920×1080**, match 0.5;
  saves the scenes; Player default resolution → 1920×1080, Full Screen Window, not native. The
  runtime `ScreenFader` canvas uses the same design size. Re-run it after adding a new scene.
- After running it the existing UI (laid out at ~900 px wide) looks about **half size** — resize it
  once with the Game view set to 1920×1080.
- **UI screens to make art for:** Main Menu (main panel, Stage Select panel), in-game HUD
  (Pause, Restart buttons), Pause panel (+ Music/SFX sliders), Dialog box, Win pop-up, Ending
  screen, plus the planned volume sliders in the Main Menu. (Full list given in chat.)

## 2026-10-02 (later) — ending screen + saved stage progress

**Designer's rules:** after the **last** stage's Win animation there's no win pop-up: it fades to
black and loads an **Ending** scene (artwork + text set up in the scene, no credits). A click only
counts after **2 s** (then an optional "click to continue" hint shows) → fade back to the Main Menu.
Own **Ending Music** slot. **Progress:** finishing a stage unlocks the next (saved); **Play**
continues from the furthest unlocked stage; Stage Select **hides** locked stages; reset is for
testing only (no player reset).

**Changes:**
- **`Progress`** (new, static): furthest unlocked stage in PlayerPrefs (`Progress.Unlocked`,
  `Completed(i)`, `IsUnlocked(i)`). Editor menu **Tools > PCB > Reset Progress** and **Unlock All
  Stages** (`ProgressMenu`).
- `LevelManager.OnWinFinished` saves progress; on the last stage it loads **`endingScene`**
  ("Ending") with a fade instead of the win pop-up. `GoTo` clamps instead of wrapping around.
- `MainMenuController.Play` → the furthest unlocked stage. `StageSelectController` lists only
  unlocked stages.
- **`EndingScreen`** (new): Ending scene script — ending music, `minimumTime` (2 s), optional
  `continueHint`, any click / key / gamepad button → Main Menu.
- Sound Bank **Ending Music** slot (`Music.Ending`).
- Compiles (runtime + editor, 0 warnings). **Tested by the designer in Unity: working**
  (incl. Tools > PCB > Unlock All Stages).

**Setup reference:** create the `Ending` scene (Canvas + artwork Image + text + an `EndingScreen`
object, optional hint text, an Audio Manager like the other scenes), **add it to the Build Profile's
scene list**, fill Ending Music; test: win the last stage → ending → click after 2 s → menu; Play
continues; Stage Select shows only unlocked stages; Tools > PCB > Reset Progress.

## 2026-10-02 — fades between scenes/stages + stage intro cinematics (code ready, no art yet)

**Designer's rules:** fade to black and back (~0.5 s) on Menu → gameplay, Stage Select → gameplay,
Next stage, Quit to Menu and Restart. Entering a stage: fade in → music starts → [intro cinematic,
some stages only] → Sparky appears → [dialog] → play (Sparky now appears *before* the dialog).
Restart: quick fade, no cinematic / dialog, music keeps going. Cinematic not skippable, played on
entering the stage (not on restart). Cinematic idea: when the screen fades in, a device is already
on the table, lined up around the board; the camera zooms in, the casing fades away revealing the
PCB, then Sparky appears. The room is a reusable background; the board sits at a fixed spot in it.

**Changes:**
- **`ScreenFader`** (new, UI): black overlay that creates itself (nothing to set up), real-time,
  blocks clicks. `LoadScene(name)` = fade out → load → fade in (a scene can `Claim()` the fade-in;
  the gameplay scene does). Main Menu Play, Stage Select and Quit to Menu use it.
- **`LevelManager`** runs the sequences as coroutines (`EnterStage`, `RestartStage`); no restart /
  next / board tilting while one runs. New fields: **Board Anchor** (every stage's board centred
  there — the fixed spot in the room), **Camera Far Clip** (so a big room isn't cut off), **Fade
  Time** (0.5), **Restart Fade Time** (0.25).
- **`Board.intro`** (new): optional **`StageIntro`** prefab. **`StageIntro`** (new): placed at the
  board's centre, lined up with it, while the screen is black; plays its Timeline after the fade-in;
  the game camera follows its **Camera Pose** (animated) + **Field Of View**; at the end it blends
  (0.6 s) into the gameplay view and removes itself.
- **`FadeGroup`** (new): one Alpha value (animate in Timeline) fades a whole model — transparent
  copies of its URP materials while fading, originals untouched.
- **`Spark.Appear()`**: the spark (character or sphere) stays hidden until the sequence calls it.
- `BoardRig`: `Refit()`, `InspectLocked`, `minFarClip`; anchor support in `Create`.
- Compiles (runtime + editor, 0 warnings); **not tested in Unity yet**.

**Tested by the designer: fades work.** Room / cinematic setup to do later:

**Room setup (once, in `SampleScene`):**
1. Build the room as normal scene objects (it stays as the background behind every stage).
2. Create an empty **`Board Anchor`** where the board should sit (e.g. inside the device on the
   table); the board faces −Z (towards the camera side).
3. Level Manager → **Board Anchor** = that object (every stage's board is centred on it, whatever
   its size); raise **Camera Far Clip** if the far parts of the room get cut off.

**Intro cinematic setup (per stage that has one):**
1. Empty root + **Stage Intro** + **Playable Director** (into Stage Intro's Director). The root's
   origin = the board's centre.
2. Device model under the root, built around that origin so it encloses the PCB.
3. **Fade Group** on the casing (or whole device) — its Alpha is what fades it.
4. Empty child **Camera Pose** → Stage Intro's Camera Pose.
5. Timeline window: create a Timeline on the root; Animation Track (accept the Animator); record
   Camera Pose wide → close-up, Fade Group Alpha 1 → 0, optionally Stage Intro Field Of View.
6. Save as a prefab → the stage's **Board → Intro** field → Save Level. The last camera key doesn't
   have to match the gameplay view: it blends there over Blend To Gameplay (0.6 s).

**Follow-up — no pause / restart during the dialog:** R was already ignored, but the on-screen
Restart / Pause buttons were clickable and Esc paused. `PauseMenu.SetAvailable(bool)` (new) grays
them out and ignores Esc; the LevelManager turns it off for the **whole stage start sequence**
(fade-in, cinematic, Sparky appearing, dialog) and back on when play starts. New optional field
**`PauseMenu.pauseButton`** — drag the on-screen Pause button in (Restart Button already there).

## 2026-10-01 (evening) — gate open/closed models, hovering goal lock, data art hookup

**New art** (Andrii, `e62d679`): `Gate1_CLOSED/OPEN`, `Gate2_CLOSED/OPEN`, `Data_Lock`,
`DataCollectible` (+ `Key_*` / `Key_Lock_*` / `Key_Node_*` in green/red/teal — a future key
mechanic, not wired). Sizes ≈ Gate1 0.25×0.33×0.49, Gate2 0.14×0.34×0.67, Data_Lock
0.15×0.56×0.38, DataCollectible 0.04×0.46×0.35 (a thin card).

**Designer's rules:** gates show a CLOSED / OPEN model and swap like the switches; Gate 1 and 2 are
two looks of the same gate — theme default + paintable per gate. A gate stands across the trace, on
top of it. The goal's gray tint is gone: instead the **Data_Lock hovers over the goal** while data is
left and **shrinks away while floating up** when the last data is collected (~0.5 above the board).
Data pickups don't spin any more — they just bob gently up and down, like the lock.

**Changes:**
- **Gates are part of the board's generated look** (visible in the Level Editor too), built by
  `BoardVisuals.BuildGate`: at the real middle of the trace by length (fixes the old float-off on
  bent traces), lined up with that segment, on top of the copper, at the model's authored size
  (X = along the trace, top facing −Z; back side turned over). The model shows CLOSED/OPEN through
  its **`LockVisual`** (Locked = closed, Unlocked = open); without one it just hides when open (old
  behaviour). Model = gate's own `model` → level Look `gate` → theme `gatePrefab`. The old runtime
  gate code in `GateMechanic.Start` (and the red-cube placeholder, `closedVisual`) is removed.
  `AndGateMechanic` shows its starting state correctly in the editor (`ShownOpen`).
- **Paint tool:** new **Gates** tab (click a trace with a gate; Paint All / Reset All). **Look:**
  new **Gate** dropdown (per-level default).
- **Goal lock:** theme **Goal Lock Prefab** + **Goal Lock Height** (0.5), hovering over the goal
  while `Board.GoalLocked`; `Board.UnlockGoals` sends it away. **Removed** the gray tint
  (`lockedGoalTint`, `BoardVisuals.SetLocked`).
- **`HoverVisual`** (replaces `DataVisual`): gentle up/down bob on screen; `Dismiss()` shrinks it
  while floating up. Used by the data pickup (now shrinks away when collected) and the goal lock.
- Compiles (runtime + editor, 0 warnings); **not tested in Unity yet**.

**Follow-up (designer tested: works well):** the goal lock could cover Sparky standing on the goal
(it hovers in front of the goal, towards the camera). Added theme **Goal Lock Up Offset** (default 0)
to move it up on screen so it floats above the goal instead; **Goal Lock Height** = distance out
from the board face. Both update live in the editor — to be tuned by the designer.

**Designer to do:** gate prefabs `Gate_1` / `Gate_2` (Closed + Open children + LockVisual), theme
Gate Prefab + Gate Variants; `Data_Pickup` and `Goal_Lock` prefabs (upright, facing the camera) into
theme Data Prefab / Goal Lock Prefab; test a level with data, a normal gate and an AND gate.

## 2026-10-01 (later) — audio: music, SFX, volume sliders, typing dialog

**Assets** (`Assets/Import Asset/Sounds/`): `InnerSparkOSTgameplay`, `SFX_Buttonclick`,
`SFX_DialogueTalking`, `SFX_ElectricSignal` (unused for now), `SFX_Fail`, `SFX_Pickup`,
`SFX_StartGame`, `SFX_UnlockOrOpen`, `SFX_Win`.

**Designer's rules:** every sound is its own field (tuned later). Win plays as Sparky starts the Win
animation. Dialog lines type out letter by letter with the talking sound playing while typing.
Two music fields (menu / gameplay); gameplay music restarts when a stage is entered, keeps
playing through a Restart, and is lowered while paused. Fail = blocked move / locked goal.
Start Game = Main Menu / Stage Select into gameplay only (not Next level). A field for a
future travel loop. Music + SFX sliders in the Main Menu and pause screen; per-sound balance
volumes set in the editor.

**Changes (new `Assets/Script/Audio/`):**
- **`SoundBank`** (Create > PCB > Sound Bank): clip + balance volume per slot — menu / gameplay
  music, paused-music level, button click, start game, win, switch, pickup, goal unlock, gate open,
  gate close, fail, travel loop, dialog talking loop. Empty slot = silent.
- **`AudioManager`**: one per scene (the first survives scene loads, later copies remove
  themselves); static calls, silent if absent. Auto-adds the click sound to every UI Button when a
  scene loads (+ Stage Select's generated buttons). Player volumes saved in PlayerPrefs.
- **`VolumeSlider`**: on a UI Slider, channel Music or SFX.
- Hooks: `SwitchMechanic.Toggle` (switch), `DataMechanic` (pickup, goal unlock),
  `GateMechanic.SetOpen` (gate open/close — only on a real change; an AND gate's starting state at
  level load is silent), `Spark` (fail in `Block`, win with the Win animation / on arrival for the
  sphere, travel loop while moving), `LevelManager.GoTo` + direct editor play (gameplay music
  restart), `MainMenuController` (menu music, start game), `StageSelectController` (start game),
  `PauseMenu` (music lowered, travel/talk loops held).
- **`DialogController`**: typewriter (`lettersPerSecond`, 40; 0 = whole line at once), talking loop
  while typing; Continue while typing → shows the whole line, next press → next line.
- Compiles (runtime + editor, 0 warnings); **not tested in Unity yet**.

**Designer setup done:** `Assets/PCB/Audio/SoundBank.asset` created and assigned; one Audio Manager in
each scene (`MainMenu`, `SampleScene`). Tested in Unity: **working, but needs more tuning**
(balance volumes, which clip goes where, missing clips — switch, travel, menu music, gate close).
Note: in Play mode the Audio Manager moves to the Hierarchy's `DontDestroyOnLoad` section and the
next scene's copy removes itself — that's by design, not a bug.

**Still to do:** sound tuning pass; Music/SFX sliders in the Main Menu and pause panel (if not added
yet); a travel SFX and a switch SFX from the audio side.

## 2026-10-01 — bug fix: Level Editor Load hid the back side

- **Bug:** after **Load** in the Level Editor, everything on the back side was invisible in the Scene
  view (until something in the level changed).
- **Cause:** `Board` only switched to "show both sides" (edit mode) in its own `Update`, but Load calls
  `board.Rebuild()` straight away on the freshly loaded copy — before its first `Update` — so the
  look was built with only the front visible. The next `Update` turned the flag on, but `Rebuild` only
  re-applies visibility when the level content changed, so the back stayed hidden. (New Level had the
  same path; unnoticed because an empty board has nothing on the back.)
- **Fix:** `Board.Rebuild` itself sets "show both sides" in edit mode, whoever calls it. Play mode
  unchanged (only the current side is shown).
- Compiles; **to test:** Load a level with back-side nodes/traces → visible straight away.

## 2026-09-30 (night) — Data pickups lock the goal

**Designer's rules:** "Data" pickups sit on **capacitors only**. The spark collects one by stopping
on its node. While any data on the level is uncollected the **goal is locked**: grayed out, and
reaching it plays no Win animation and no win screen (the spark can still stand on it). Collect
**all** of it to unlock; levels without data work as before. No counter / HUD. One goal per level
in practice (several would lock/unlock together).

**Changes:**
- **`DataMechanic`** (new `NodeMechanic` on a capacitor): on arrival → marks collected (runtime
  only, so restart resets), hides the pickup, burst VFX; after the last one → unlocks the goal
  (+ burst on it).
- **`Board.GoalLocked`** (any uncollected data), `Board.VisualsOf(node)`, `Board.UnlockGoals()`.
  `Spark.Arrive`: a locked goal isn't a win → shake + burst instead. `LevelManager.OnArrived`
  ignores a locked goal. `Spark.SpawnBurstAt(position)` made public for mechanics.
- **Look:** theme **Data Prefab** (empty = small glowing cube), **Data Height** (0.45 above the
  surface), spinning + bobbing in play (`DataVisual`, added automatically). Locked goal: tinted
  with theme **Locked Goal Tint** (gray), or — if the goal prefab has a **`LockVisual`** (new, with
  `Locked` / `Unlocked` children, like `SwitchVisual`) — those are swapped instead. Shown in the
  editor too (a level with data shows its goal gray).
- **Level Editor:** new **Data** tool — click a capacitor to add/remove its data (non-capacitors
  refused); shows the count and rings data nodes. Changing a data node's type (Ctrl+Click) drops
  its data. Validate: data on a non-capacitor.
- Compiles (runtime + editor, 0 warnings); **not tested in Unity yet**.

**Designer to do:**
- Build a test level: 2–3 data on capacitors (some on the back side), a goal; check the goal is
  gray, reaching it early does nothing (shake), collecting the last data lights it up, then it wins.
- Later: a Data model (theme Data Prefab) and optionally a locked/unlocked goal prefab (LockVisual).

## 2026-09-30 (evening) — bug fix: spark moving two steps

- **Bug:** after reaching a node the spark sometimes took a second step with no new input.
- **Cause:** `Spark.ReadInput` counted *any change* of the 8-way direction as a new press — including
  a key going **up**. Letting go of a diagonal (W+D) almost never releases both keys in the same
  frame, so for a moment only one key is held → read as a fresh "right"/"up" → an extra move queued,
  played on arrival. (Also: hold D, tap W, release W → D counted again.) Pre-existing flaw in the
  sector logic, made common by 8-way movement.
- **Fix:** input is tracked per axis (-1/0/1); only an axis that becomes active or reverses (a key
  going down) is a press — releases never are. Queued directions snap to the 8 directions. Nghia's
  80 ms window to combine two keys into a diagonal is unchanged; pause/lock behaviour unchanged.
- Compiles; **to test in Unity:** diagonal moves then release (no extra step), hold a key through a
  move (no repeat), quick two-key diagonal still works, gamepad stick/D-pad.
- **Follow-up — double tap = two steps:** not stuck input but the move queue: a press made while the
  spark was moving/animating was always kept and played on arrival, and with Sparky's animations a
  move takes 0.6 s+. Now only a press made within **`Spark.inputBuffer`** (default **0.15 s**) of the
  spark becoming ready is carried over; older presses are forgotten. Same for Space (flip/switch).
  Tunable on the Spark component (`Spark_Sparky` prefab); 0 = no carry-over at all.

## 2026-09-30 (later) — normal & AND switches, Link tool, no in-game text

**Designer's rules:** two switch kinds, chosen when placing the node. **Normal switch**: a gate can
have several; pressing *any* of them flips the gate. **AND switch**: an AND gate opens only while
*all* its AND switches are on. Both toggle on every press, and both show an ON/OFF model (normal =
lever left/right, AND = button pressed/not). Gates may start open. No reach-the-goal check needed.

**Changes:**
- `NodeType.AndSwitch` (new; appended, so existing data is unaffected) + `PcbNode.IsSwitch`.
  Theme `andSwitchPrefab` / `andSwitchVariants`, `Board.look.andSwitch`. Spark's Space press
  toggles either kind.
- **`SwitchVisual`** (new): on a switch model prefab's root, with its `on` / `off` children. The board
  shows the starting state when built (editor too); `SwitchMechanic.Toggle` swaps it on every press.
- **Gates hold their switches:** `switches` list moved into `GateMechanic` (same field name the AND
  gate already used). Normal gate: any press of any listed switch flips it; `isOpen` = starting
  state. `AndGateMechanic`: open while all on; new **`inverted`** = open until all on.
  Hand-wired `onToggle → SetOpen` (Level 04) still works.
- **Level Editor:** placing a Switch/AndSwitch node adds `SwitchMechanic` (Ctrl+Click type
  change adds/removes it). New **Link** tool: click a switch, click traces to link (adds the gate;
  "New Gates Start Open" option), Ctrl+Click unlinks (removes an unused gate); won't mix normal
  and AND on one gate; dotted lines show every switch → gate link.
- **Validation** (connections only): gate with no switch; missing / foreign / non-switch /
  wrong-kind switch in a gate's list; switch both listed and hand-wired (acts twice); AND gate
  hand-wired (bypasses AND); switch node without `SwitchMechanic`; `SwitchMechanic` on a
  non-switch node; switch that controls nothing.
- **Removed all on-screen text** during play (level name, side, controls, via hint) —
  `LevelManager.OnGUI` deleted; tutorials go in each stage's intro dialog.
- Compiles (runtime + editor, 0 warnings).
- **Designer set up the switch prefabs (SwitchVisual ON/OFF) and a test level
  (`Level 06`): tested in Unity — working.**

**"Unsaved changes" warning that stayed after Save Level:**
- Checked `Level 06`: the scene board and the saved prefab were identical in every gameplay field,
  transform and position — the level *was* saved; the warning was a false alarm from the checker
  (`PcbLevelEditorWindow.Levels.cs`, text fingerprint of scene board vs prefab).
- Hardened the checker: ignores Unity's prefab-link bookkeeping fields
  (`m_CorrespondingSourceObject` / `m_PrefabInstance` / `m_PrefabAsset`) and prints near-zero
  numbers without a "-0.000" sign. Couldn't reproduce in Unity from here, so also added a
  diagnostic: right after Save Level, if the level still looks unsaved, the Console lists exactly
  which component/field differs; a **Why?** button next to the warning logs the same.
- **To confirm:** does the warning clear after saving now? If not, send the
  "[PCB] '…' differs from …" Console warning.

**Two Console errors on launch (checked, not a code bug):** `SerializedObjectNotCreatableException`
(TransformInspector) and `MissingReferenceException` (GameObjectInspector). Stack traces are
Unity's own Inspector only — it complains when the object it's showing gets destroyed (Main Menu
objects on scene load, the board's regenerated look at play start, the board on restart).
Editor-only, harmless, not in builds. Check: deselect everything before Play; report if they
still appear.

## 2026-09-30 — final node / board / decoration prefabs (designer)

**Done (designer, in `Assets/PCB/Prefabs/Final/`):**
- Board tiles ×6: Black, Blue, Bronze, Green, Purple, Red.
- Capacitors ×6: Black, Blue, Gold, Green, Orange, Silver.
- Start ×4 (`Start_1`–`Start_4`), Goal ×4 (`Goal_1`–`Goal_4`).
- Decorations: LEDs ×15 (`LED_1/2/3` × Blue, Green, Purple, Red, Yellow) in `Final/Decoration/`.
- Old `Board_Tile.prefab` renamed to `Board Tile Green.prefab` (still in `Prefabs/`, next to the
  `Final/` one of the same name).
- Later the same day: **`Via.prefab`** (new `Via.fbx`, one thin cap ~0.41 wide) and
  **`Trace_Path.prefab`** (moved into `Final/`) + **`Trace_Path_Connector.prefab`** (new
  `Path_connect.fbx`, the bend piece).

**Checked (me), then fixed (designer):**
- All prefabs: root at 0,0,0 / no rotation, child rotated (270, 180, 180) = top facing −Z. ✔
- Fixed: theme **Start** slot pointed at `Goal_2` (an End plug) → now `Start_2`.
- Fixed: `Capacitor Silver` child was offset X = 0.604 (drawn ~half a unit beside its node) → 0.
- Fixed: removed stray **`PcbNode` components** from the 6 Capacitor and 4 Goal prefabs (only
  harmless because `Board.Rebuild` skips generated objects).
- Scales differ a lot between prefabs (FBXs were authored at very different sizes, and
  `Start_2`/`Goal_2` are stretched ×2 in height) — **intentional**, per the designer.
- **`PcbTheme` now uses the finals:** defaults Capacitor Blue / Via / Start_2 / Goal_4 /
  Trace_Path / Trace_Path_Connector; Catalog lists filled with all 6 capacitors, the via, 4 starts,
  4 goals, 6 board tiles, trace + connector.

**Known, not changed:**
- Node heights vs Sparky: tall capacitors ~0.40–0.44, low plugs ~0.16; Sparky's feet sit ~0.30 above
  the board (one Model offset for all types) → sinks into tall nodes / floats over low ones. A
  per-type height is possible if it bothers.
- Goal nodes: default **Chip Size** 1 × 1.5 vs goal models ~0.35–0.5 wide → set Chip Size ≈
  0.5 × 0.45 on goal nodes (editor click area / outline only).
- `boardTilePrefab` default still points at the old `Prefabs/Board Tile Green` (the `Final/` one
  is in the catalog) — harmless.
- LED decorations aren't in `decorationPrefabs` yet (no LED decoration type exists).
- `switchPrefab` is still the placeholder `Capacitor Demo 1`; `switchVariants` empty.

**Next:**
- **Switch prefabs + setting up normal / AND switches** (see the next entry when it's written).
- Test in a scratch level: every type on both sides, via caps on both faces, Paint/Look thumbnails,
  Shift+Click rotation, Sparky's height on each node type.
- Decide whether to delete the old Demo prefabs now that the finals are in the theme.
- Push: local `main` is 2 commits ahead of `origin/main`, plus these prefabs/theme/notes.

## 2026-09-29 → 30 — Sparky character replaces the spark sphere

**Session summary:** Reviewed the teammates' pushed work, then replaced the glowing-sphere player
with the animated Sparky character + VFX. Designer set it up in Unity and confirmed it working.

### Teammates' work pulled in (2026-09-29, not written up by them)
- **Nghia:** `NodeType.Switch` + `SwitchMechanic` (Space on a switch toggles it, fires
  `onToggle`) and `GateMechanic` (a `TraceMechanic` that blocks the spark while closed) — the first
  concrete mechanics. Theme slots `switchPrefab` / `gatePrefab` (+ variants). **8-way movement**
  with an 80 ms grace window to combine diagonal key presses; validator accepts diagonal exits.
  Via models now render on both sides; back-side node/decoration models mirrored correctly.
  `LevelManager` hides every scene board at start. **Level 05** added.
- **Andrii:** re-exported `Mesh_Sparky_Animated.fbx` (now has the skinned mesh + materials),
  Sparky textures/materials, VFX prefabs (`VFX_Sparky_Idle`, `VFX_Sparky_Trail`,
  `VFX_BurstOfSparks`), UI button art + `upheavtt.ttf` font, console props, bigger level scene.
- Small follow-ups for Nghia: gate visual sits at the straight from→to midpoint (ignores bends);
  `gateVariants` unused by the Look/Paint tools; Debug.Log on every gate block / switch toggle.

### Sparky character (`Spark.cs`, `LevelManager.cs`)
- Clips in the FBX (24 fps): `Sparky_Idle` 1.21 s, `Sparky_Move_Start` 0.29 s,
  `Sparky_Move_Finish` 0.29 s, `Sparky_Win` 1.21 s. Move clips also move `Bone_Pivot`
  (kept inside the model: Apply Root Motion off).
- `Spark` gets an optional character: `model`, `animator`, state names (played directly by name —
  the Animator Controller needs no transitions/parameters), `idleVfx`, `travelVfx`, `burstVfx`,
  `travelBurstInterval`, `glowLight`, `directionArrows`. **Empty `model` = the old sphere, unchanged.**
- Behaviour (as specified by the designer):
  - Move: MoveStart (shrink) → character hidden, trail VFX runs along the trace with random bursts →
    MoveFinish at the next node → Idle loop + idle VFX.
  - Flip on a via: MoveStart → board turns → MoveFinish on the other side.
  - Goal: MoveFinish → Win (once, holds last frame) → **then** the win screen (`WinFinished` event).
  - Level start: appears with MoveFinish on the start node (after the intro dialog closes).
  - Blocked: shake + burst VFX (no red tint, no direction arrows). Switch use: burst VFX.
  - Back side: the prefab pose is the front; mirrored automatically.
  - Input during these animations is queued, as while moving (`IsBusy`).
- **Bug fixed — freeze after the intro dialog:** `LevelManager` used to disable the Spark component
  during the dialog / at the goal, which cut the character's animation sequence short. Replaced with
  `Spark.InputLocked`; never disable the Spark component while a sequence runs.
- **Setup pitfall handled in code:** if `idleVfx` / `travelVfx` point at the VFX *prefab file*
  instead of a child, the spark places its own copy at spawn (idle under the model, parent scale
  cancelled). `burstVfx` is meant to be the prefab file (spawned under the Board, auto-destroyed).

### Unity-side setup (done by the designer)
FBX: Generic rig, `Sparky_Idle` Loop Time on. `Sparky.controller` (states `Idle` default,
`MoveStart`, `MoveFinish`, `Win`, no transitions). Prefab `Assets/PCB/Prefabs/Spark_Sparky`: root
with `Spark`, child `Model` (scale 0.1, Animator Always Animate, no root motion, offset toward the
camera to sit on top of the node). Assigned to Level Manager → Spark Prefab in `SampleScene`.

### Merged with origin/main (PR #4: win pop-up, AND gate, scroll view, via/gate fixes)
- Committed locally as "Import Sparky/ done animation", then merged with `origin/main`.
  Conflicts: `LevelManager.cs` and this file.
- `LevelManager`: the new **`WinPanel`** pop-up (replaces the old "CIRCUIT COMPLETE" IMGUI text)
  now opens in `OnWinFinished` — i.e. **after** Sparky's Win animation. Dropped the incoming
  `spark.enabled = false` there (input is already locked via `InputLocked` since the goal; disabling
  the Spark is what caused the dialog freeze). Via hint keeps the `IsBusy` check.

### Not done yet / pending
- Tell Nghia `Spark.cs` changed a lot (he also edits it).
- `VFX_BurstOfSparks` has Looping on → sprays ~1 s instead of one pop; switch to an Emission Burst.
- One model offset for all node types → may float/clip on nodes of different heights; a per-type
  height is possible if it bothers.
- **Tested by the designer after the merge (2026-09-30): working** — win pop-up after Sparky's Win
  animation, Stage Select scroll, merged build overall.
- Raise with the team: `origin/main`'s `BoardVisuals.BuildNode` reverted Nghia's back-side
  mirroring (a node prefab's root rotation/offset is now ignored — fine with the wrapper setup,
  breaks an FBX with a rotated root dropped straight into a slot) and left a commented-out block.

## 2026-09-29 (night) — checking a merge: two real bugs found and fixed

**Session summary:** Designer merged in a batch of the dev's parallel work (8-way movement,
another via/visual fix pass, `Level 05`, more materials — full list below) and asked me to
check it over. The merge had real conflicts (`BoardVisuals.cs`, `GateMechanic.cs`,
`PcbTheme.cs`, `LevelList.asset`, `Level 04.prefab`) resolved by hand; two of those
resolutions left the code in a genuinely broken/regressed state. No leftover `<<<<<<<`
conflict markers anywhere, for what that's worth — these were clean-looking but logically
wrong resolutions, not obvious ones.

**Bugs found and fixed:**
1. **Via model: front side broke while fixing the back side.** My fix from earlier today
   (re-center the model at the board's mid-thickness) and the dev's independent fix (a
   *second*, mirrored copy of the model — one instance per face, which is the more robust
   general solution) both survived the merge, in an order that made them incompatible: the
   dev's math assumes the first copy sits at its own authored position (the front face,
   `z = 0`); my fix had already shifted that same first copy to the midpoint before their
   code ran, so the "front" copy ended up buried in the middle of the board instead of on
   the front face. Fix: removed my midpoint-shift now that the dev's two-copy approach
   supersedes it — `BoardVisuals.BuildNode` no longer touches a via model's position beyond
   what the dev's mirroring already does.
2. **`GateMechanic.cs` conflict resolution silently discarded finished work.** The dev's
   "visual stop braking" commit rewrote `Start()` to (a) use `board.theme.gatePrefab` for
   the closed-gate visual when one's assigned, and (b) position/orient that visual properly
   via `board.NodePosition`/`board.SurfaceToWorld` (trace midpoint, correct surface height,
   rotated to the trace direction, flipped on the back) instead of the old crude
   world-space `Vector3.Lerp` + hardcoded offset. The merge's conflict resolution reverted
   `Start()` back to the old crude version entirely — losing both improvements. Confirmed
   this wasn't an abandoned experiment: `PcbTheme.asset`'s `gatePrefab` is already assigned
   (to `Trace_Path_Blocked`, presumably), so every Gate has been silently falling back to
   the auto-generated red placeholder cube instead of that real art. Restored the full
   `Start()` from the dev's commit — untouched otherwise, `AndGateMechanic` (which doesn't
   override `Start()`) picks up the same fix automatically.

**Worth testing, not touched:** the dev's "8-way movement" change (`Spark.ReadInput`) adds
an 80ms grace timer that delays committing a queued move, letting quick diagonal key-rolls
(e.g. tap W then D) combine into one diagonal input instead of firing the cardinal move
first. One edge case I couldn't verify without playtesting: if the player releases input
*during* that 80ms window, the timer still counts down and still fires the move at the end
using the last direction held — so a very brief tap-and-release might still move the Spark
up to ~80ms later. Might be intended leniency, might not — worth a deliberate tap-then-
release test.

**Also landed in this merge, no issues found:**
- `Board.Rebuild()` now filters out `HideFlags.DontSave` objects when collecting
  nodes/traces/decorations (defensive, excludes generated visuals) — reasonable, unrelated
  to anything above.
- `LevelManager.Start()` now finds and deactivates *every* Board in the scene (not just
  one) before deciding what to play — merged cleanly, no conflict, looks correct.
- New content: `Level 05.prefab`, updates to `Level 02`/`Level 03`/`Level 1`/`Level 04`,
  `Trace_Path_Blocked.prefab` (the real Gate visual — now actually wired up per fix #2
  above), `Red.mat`/`White.mat`.
- `PcbTheme.cs` gained `gatePrefab`/`gateVariants` (now actually used, see fix #2).

### Not done yet / pending
- Playtest the 80ms input-grace-timer edge case above.
- Confirm in Unity: via visible on both sides again (front *and* back, not just back), Gate
  visuals now use `Trace_Path_Blocked` / position correctly on the trace midpoint.
- Everything under "Not done yet" in earlier entries below is still open.

## 2026-09-29 (evening) — multi-switch AND gate

**Changes made:**
- **New: `AndGateMechanic.cs`** (`Assets/Script/PCB/`, subclasses `GateMechanic`) — for gates that
  need *several* switches all on before they open, not just one. Existing `GateMechanic`/
  `SwitchMechanic` are completely untouched, so every already-wired single-switch gate (e.g.
  `Level 04`'s) keeps working exactly as before.
  - Why a new class instead of extending `GateMechanic`: single-switch gates are driven by the
    switch calling `SetOpen(bool)` directly (an unconditional "set to this state," no combining
    logic) — wiring *two* switches to the same `SetOpen` the same way would just mean "whichever
    was pressed last wins," not "both must be on." `AndGateMechanic` instead holds its own list of
    `SwitchMechanic`s, subscribes to each one's `onToggle` itself in `OnEnable`, and only calls the
    inherited `SetOpen(true)` once every switch in the list is on.
  - Setup is simpler than the single-switch case too: assign the switches to the `Switches` list on
    the gate and you're done — no per-switch Inspector event wiring needed, the gate does the
    subscribing itself.
  - Inherits `GateMechanic`'s placeholder-visual behavior (`closedVisual`, auto red cube if unset)
    unchanged; the designer already has real art for both the single- and multi-switch cases to
    swap in.

### Not done yet / pending
- Not tested in Unity yet — needs a scene with 2+ switches wired to one `AndGateMechanic` to confirm.
- Assumed "must ALL be on" (AND) reading of the request; flag if OR ("any one opens it") was
  actually wanted instead — that'd be a different (smaller) change.

## 2026-09-29 (later) — scrollable Stage Select, Via model bug

**Changes made:**
- **Bug fix — Via node invisible from the back when a custom model is assigned.**
  `theme.viaPrefab` (now `Via Demo.prefab`, a thin disc) is placed at the board's *front*
  surface (`z = 0`) like every other node model, but a Via is meant to sit **through** the
  board and poke out both faces — the old built-in procedural via shape did that correctly
  by offsetting itself to the board's mid-thickness internally, but that offset was never
  applied to the model-override path, so the disc sat almost entirely on the front and
  never reached the back surface. Fixed in `BoardVisuals.BuildNode`: the instantiated model
  is now shifted `+t * 0.5f` on its local Z when the node `IsVia`, matching where the
  built-in shape already centers itself. Code-only, no scene changes needed.
- **Stage Select list is now scrollable** (designer, manual Editor setup): existing
  `ButtonContainer` re-parented into a `Scroll View > Viewport`, given a `Content Size
  Fitter` (Vertical = Preferred Size) so it grows with the level count, `Scroll Rect`
  wired to it, vertical-only. No code involved — `StageSelectController` just adds
  buttons as children of `ButtonContainer` regardless of what wraps it.

### Not done yet / pending
- Confirm in Unity that the via now renders correctly on both sides after the fix above.
- Switch mechanic: designer asked about placing a `Switch` node from the Level Editor —
  see the next entry / DESIGN.md for what's possible today vs. what still needs the dev.

## 2026-09-29 — catching up on teammates' work

**Session summary:** Designer asked me to check what changed since the last logged entry.
Read through git history (nothing here was written by me) and updated DESIGN.md to match;
no code changes this entry, just documentation catching up to what's already in `main`.

### What landed (via `git log`, not seen in PROGRESS.md before now)
- **First concrete gameplay mechanic — Switch/Gate** (Truong Quang Nghia, branch `feat/switch`,
  merged into `main` today): new `NodeType.Switch`, `SwitchMechanic.cs` (`NodeMechanic` —
  `Toggle()` fires `UnityEvent<bool> onToggle`), `GateMechanic.cs` (`TraceMechanic` — blocks
  entry unless `isOpen`, `SetOpen(bool)`). `Spark.TryFlip()` now special-cases `Switch` nodes:
  the flip input calls `Toggle()` instead of turning the board over. `Board`/`PcbTheme`/
  `BoardVisuals` extended with a `switchNode`/`switchPrefab`/`switchVariants` slot (placeholder
  shape: a metal cylinder with a disc on top, like a squat capacitor). **This is the first thing
  to ever come out of the `TraceMechanic`/`NodeMechanic` extension points** — see DESIGN.md § 4.
  - Wired and working in `Level 04`: a Switch's `onToggle` → a Gate's `SetOpen`.
  - `Level 04` itself was heavily rebuilt alongside this (32×20 → 10×10, ~2450 lines of old
    node/trace/decoration data removed) — reads like it became a small test bed for the
    mechanic rather than a finished level; worth confirming with the dev before treating it
    as a real level 4 again.
  - Rough edges worth a look, not fixed: leftover `Debug.Log` calls in both scripts;
    `GateMechanic.CanEnter` ignores the `reversed` parameter (blocks both directions —
    may or may not be intended); `GateMechanic` auto-spawns a plain red cube if no
    `closedVisual` is assigned (fine as a placeholder, just flagging it's not final art).
- **Large art/VFX asset drop** ("Andrii", `andrii.nhuien@gameloft.com`, commit `5a8ba4f`,
  191 files, art-only — no `.cs` changes): per-color materials for LEDs, PCB boards and
  nodes; more `PlugNode` size variants (2/3/4); Sparky's own materials + textures; three
  VFX prefabs — `VFX_BurstOfSparks`, `VFX_Sparky_Idle`, `VFX_Sparky_Trail` (likely meant for
  the Spark's idle/movement feel, given the names). **Imported but not wired into anything
  yet** — same status as the first art batch from two days ago.
- Both branches merged into `main` by the designer just now (merge commit `0aeb810`); no
  conflicts.

### Not done yet / pending
- Everything under "Not done yet" in the two entries below is still open (Switch/Gate is
  new since then, doesn't change that list).
- Nothing from either art drop is wired into `PcbTheme` / the Look-Catalog system yet.
- Worth deciding whether `Level 04`'s rebuild is meant to become the real level 4, or if the
  switch/gate testing should move to its own scratch level.

## 2026-09-28 (evening) — art investigation + model slots & per-level look system

**Session summary:** Checked the imported art, then built a way to use it: model slots for the
board and traces, and a system for choosing different models per level and per node, driven from
the Level Editor.

### Findings (no code changes)
- **`Mesh_Sparky_Animated.fbx` has no mesh in it.** Parsed the file directly: 39 bones +
  4 animations (`Sparky_Idle`, `Sparky_Move_Start`, `Sparky_Move_Finish`, `Sparky_Win`), but
  0 geometry, 0 skin deformers, 0 materials. The import settings are fine — it's an export problem
  (probably "Selected Objects" with only the armature selected). **Ask the artist to re-export with
  the mesh + armature**; replace the `.fbx` and keep its `.meta`.
- Imported model sizes (Unity units): `Path_module` 1.0 long × 0.15 wide × 0.10 tall;
  `PCBboard_module*` a 1×1 tile, 0.02 thick. All exported Y-up (lying flat), so they need a
  wrapper prefab rotated to face −Z.
- `Level/LevelScene_3D.fbx_Scene.fbx` is a town scene (trees, cars, vending machine…), not a PCB
  level — ask the artist whether it's background art or included by mistake.

### Code changes
- **Board tile + trace + trace bend model slots** (`PcbTheme.boardTilePrefab`, `tracePrefab`,
  `traceBendPrefab`, plus `boardTileSize`). Unlike node models (placed at authored size), these
  are **resized to fit** the theme's numbers (`BoardVisuals.Fit`), so `traceWidth`/`traceHeight`/
  `boardThickness` stay the single source of truth for gameplay (spark height, camera framing).
  - Board: tile repeated across the board + margin, count rounded to a whole number.
  - Trace: one stretched piece per straight segment; with a bend prefab, pieces stop at the bend
    and the bend piece is placed there; without one, pieces overlap half a width at corners.
  - Empty slots = the old built-in shapes, so nothing changed for existing levels.
- **Per-level / per-node look system.** Which model wins: node's own `model` → level's
  `Board.look` → theme slot.
  - `Board.BoardLook look` (saved in the level prefab): board tile, trace, bend, and a default
    model per node type. Resolution helpers on `Board` (`NodeModel`, `TraceModel`…), which
    `BoardVisuals` now uses. Added to `Board.ComputeSignature` so edits redraw immediately.
  - `PcbNode.model` / `PcbDecoration.model`: optional per-object override.
  - `PcbTheme` **Catalog** (`capacitorVariants`, `viaVariants`, `startVariants`, `goalVariants`,
    `boardTileVariants`, `traceVariants`, `traceBendVariants`): the choices the editor offers.
    Decoration variants = several `decorationPrefabs` entries of the same type (first = default).
- **Level Editor** (new file `PcbLevelEditorWindow.Look.cs`):
  - **Look (this level)** section: dropdowns for each look field + **Copy Look From** another level.
  - **Paint** tool: pick Nodes/Decorations + type + a thumbnail, click to paint, Shift+Click to
    reset, **Paint All / Reset All** buttons. Only paints objects of the chosen type. Undo works.
  - Ctrl+Click type change (Node/Decor tools) now clears a painted model from the old type.
  - Fixed the stale Play-mode note (mentioned the removed Prev/Next keys).
- **Node rotation:** `PcbNode.rotationDegrees` spins a node's model (or built-in shapes) around
  the board normal; visual only, trace directions unaffected. Level Editor Node tool has a
  Rotation slider (15° steps) applied to new nodes; Shift+Click applies it to an existing node.
  Goal chip click area / outlines follow the rotation. **Tested by the designer in Unity: working.**
- Runtime + editor code compiled with `dotnet build`; **not yet tested in Unity by me**.

### Designer-side setup (seen in the project)
New prefabs in `Assets/PCB/Prefabs/`: `Board_Tile`, `Trace_Path`, `Capacitor Demo`,
`Capacitor Demo 1`, `Start Demo`, `Goal Demo`, `Via Demo` (old `Capacitor F` / `Start F` /
`Goal B` / `Via` prefabs removed). Guided on adding capacitor variants via the theme's Catalog.

### Not done yet / pending
- Test in Unity: board tiles + traces + bends on both sides, Paint tool, Look section, Copy Look,
  saving/reloading a level keeps painted models, unsaved-changes indicator.
- Artist: re-export the character FBX with the mesh; clarify the town scene FBX.
- Open questions from the look design: a "random from catalog" option for level defaults?
  Are the Switch ON/OFF and LED models cosmetic (→ catalog) or future mechanics
  (→ `TraceMechanic`/`NodeMechanic`)?
- Possible UX tweak: the Paint palette shows the default model twice ("Default (X)" and "X") —
  could hide the second when it matches.
- Pause-input fix from earlier today still worth a quick re-test.

## 2026-09-28 (later)

**Changes made:**
- **Bug fix — input leaking through the pause menu:** moves/flips pressed while paused were
  registered and played the moment you unpaused. `PauseMenu` now exposes a static
  `GamePaused`; `Spark.ReadInput` drops any queued move/flip while it's true (and keeps
  tracking the held direction, so a key held through Resume doesn't fire either), and
  `BoardRig` ignores mouse-drag inspection while paused. `LevelManager` already skipped
  restart/confirm while paused.
- `DESIGN.md` brought up to date: Controls table (Prev/Next removed, Esc = pause, Restart/Pause
  buttons, dialog Continue), UI scripts + scenes added to the architecture map, corrected
  `PcbDecoration.cs` location.
- Logged the art import (commit `6f9039d`, `Assets/Import Asset/`: Sparky character, level props,
  level scene FBX, portraits) — **imported but not tested yet**, nothing wired up to it.
- Noted: a second dialog asset `Lvl2_Intro` exists alongside `Lvl1_Intro`.

**To test:** pause mid-level, press directions / Space / drag the mouse, resume → spark
should not move or flip until a fresh input after resuming.

## 2026-09-28

**Session summary:** Full day building out the Main Menu / Stage Select / Pause / Dialog
system end to end: planned it, wrote all the scripts, the designer did the manual Editor
scene setup, then we hunted down three real runtime bugs surfaced by testing, and finished
by adding a couple of extra player-facing UI requests. Long session — details below,
grouped by phase rather than chronologically.

### Design decisions
uGUI for all new UI (not IMGUI, to stay editable/reskinnable), a separate `MainMenu`
scene (not an overlay in the gameplay scene), a pause overlay rather than a HUD button
for quitting to menu, visual-novel-style dialog (name + portrait + text) authored as a
`ScriptableObject` per stage, Stage Select auto-populated from the existing `LevelList`,
and all new scripts kept in `Assets/Script/UI/` separate from `Assets/Script/PCB/` to
avoid colliding with the dev's work there.

### Scripts added (`Assets/Script/UI/`)
- `GameFlow.cs` — static bridge carrying the requested level index from the Main Menu
  scene into the gameplay scene. `RequestLevel(index)` sets it; `HasPendingRequest`
  (added later, see bug #3 below) lets `LevelManager` check before consuming it;
  `TakeRequestedLevel(fallback)` consumes it, falling back to `LevelManager.startLevel`
  if nothing requested it, so direct in-editor testing of the gameplay scene is unaffected.
- `DialogSequence.cs` — `ScriptableObject` (`Create > PCB > Dialog Sequence`): an array
  of `{ speakerName, portrait, text }` lines. One asset per stage, assigned via the
  optional `Board.dialogSequence` field in the regular Inspector (not the custom PCB
  Level Editor window, which doesn't expose it).
- `DialogController.cs` — shows/advances a modal dialog panel; exposes `IsShowing`.
  Advance is driven entirely by the Continue button (click, or keyboard/gamepad Submit
  once it's the selected UI element) — no separate key bindings, avoids double-advance.
- `PauseMenu.cs` — Esc (or a Pause button, added later) toggles a pause panel
  (`Time.timeScale = 0`); `Resume()` / `QuitToMenu()` (loads the MainMenu scene) /
  `QuitApp()` for the panel's three buttons. Also now optionally disables a Restart
  button while paused (see below).
- `MainMenuController.cs` — Play / Stage Select / Quit for the MainMenu scene's main panel.
- `StageSelectController.cs` — builds one button per level **from the existing
  `LevelList`** at runtime (no manual upkeep as levels are added/reordered); Back button
  returns to the main panel.

### Existing files touched
- `Board.cs` — one new optional field: `public DialogSequence dialogSequence;`. Empty =
  no dialog, level behaves exactly as before.
- `LevelManager.cs` — reads `GameFlow`/`dialogController`/`pauseMenu` as described above;
  removed the old `Esc → Application.Quit()` binding entirely (now `PauseMenu`'s job);
  **removed the whole Prev/Next feature** (IMGUI buttons, keyboard/gamepad bindings,
  the now-dead `Previous()` method, the "Level: [ ]" HUD hint) per a later request —
  `Next()` itself stays, since winning still uses it to advance; `Spawn()` now takes a
  `showDialog` bool: `GoTo()` (Play/Stage Select/Next/initial load) passes `true`,
  `Restart()` passes `false`, so replaying a level you've already seen the intro for
  drops straight into gameplay instead of showing the dialog again.

### Manual Editor setup (done by the designer this session)
`MainMenu.unity` created (Canvas/EventSystem with the Input System UI Input Module,
main panel, stage-select panel + button template) and added to Build Settings at index 0
(`SampleScene` at index 1); `SampleScene` got its own Canvas/EventSystem plus `PauseMenu`
and `DialogController` GameObjects, wired into `LevelManager`; TextMeshPro Essentials
imported; a test `DialogSequence` created and assigned to Level 1.

### Bugs found and fixed during testing
1. **Edit-mode crash:** `MissingReferenceException` in `BoardVisuals.BuildNode` while
   actively editing a level — a node/trace/decoration destroyed mid-`Rebuild()` (e.g. via
   Undo or the Erase tool) wasn't being skipped. Added `if (!x) continue;` guards in
   `Board.ComputeSignature`, `Board.BuildGraph`, `Board.RemoveLegacyComponents`, and
   `BoardVisuals.Build` — mirrors the `Trace.IsValid` guard pattern already used elsewhere.
2. **MainMenu buttons rendering blank:** Stage Select / Quit / Back showed no text even
   with correct-looking Font Asset/Material in the Inspector. Root cause, found by reading
   the `.unity` file directly: TMP's internal `m_hasFontAssetChanged` flag was stuck at
   `1` on all three (vs `0` on the working Play button) — the mesh was never actually
   rebuilt after the font was reassigned via Inspector. Fixed by retyping the Text Input
   content directly (forces a rebuild) and saving outside Play Mode. Also fixed along the
   way: `Back` had no font asset at all and still said "Button"; `Quit` was pointed at
   `LiberationSans SDF - Fallback` instead of the real font asset.
3. **Stage Select always landed on level 1:** `LevelManager.Start()`'s "a Board is sitting
   in this scene + we're in the Editor ⇒ must be direct editor-testing" heuristic always
   won, since `SampleScene` always has a Board in it for editing — it silently ignored
   whatever Stage Select actually requested. Fixed by adding `GameFlow.HasPendingRequest`
   and checking it first in `Start()`, before that heuristic runs.
4. **Dialog levels: no dialog shown, movement locked forever:** `DialogController` lived
   directly on its own panel GameObject, which starts disabled in the scene (correctly,
   per earlier advice). Because it starts disabled, `Awake()` is deferred until the first
   `Show()` call reactivates it — but `Awake()` unconditionally called
   `panel.SetActive(false)` again, immediately undoing that very activation from inside
   itself. Fixed by removing the redundant `SetActive(false)` from `Awake()` (the panel's
   saved inactive state already covers "starts hidden"). Confirmed `PauseMenu` doesn't
   have this problem — its panel is a separate GameObject, not itself.

### New player-facing features added (end of session)
- Real uGUI **Restart** button in `SampleScene` (OnClick → `LevelManager.Restart()`),
  alongside the existing `R` key.
- Real uGUI **Pause** button (OnClick → `PauseMenu.Toggle()`), equivalent to `Esc`.
- `PauseMenu.restartButton` (optional field): `Pause()`/`Resume()` toggle its
  `interactable` state so Restart can't be clicked out from under the pause panel.
- Restart skips the dialog on replay (see `Spawn(showDialog)` above).

### Not done yet / pending for next session
- Designer still needs to drag `RestartButton` onto `PauseMenu`'s new **Restart Button**
  field in the Inspector — guided, not yet confirmed done.
- Worth a full end-to-end re-test in one pass: Stage Select into *every* level (not just
  the first couple tested), dialog shows on first entry and is skipped on restart, pause
  button + restart-button-disable-while-paused all together.
- `TraceMechanic`/`NodeMechanic` gameplay mechanics are still unbuilt (unchanged from
  the previous session — see DESIGN.md § Open design space).
- Local-only settings diffs from the previous session are still untouched.

## 2026-09-27

**Session summary:** First full scan of the project (no prior docs existed). Reviewed
every script, the scene, and the level list; fixed two small issues; created this doc
and DESIGN.md.

**Changes made:**
- Deleted `Assets/Script/Brainstorm.cs` (+ its `.meta`) — an empty, unused default
  MonoBehaviour stub not referenced by any scene or prefab.
- Fixed a minor leak in `LevelManager.Spawn()`: it subscribed
  `spark.Arrived += OnArrived` on every spawn without ever unsubscribing from the
  previous spark. Harmless in practice (the old Spark is destroyed with its rig before
  the new one exists), but now unsubscribes explicitly before creating the next one.
- Added `DESIGN.md` and this file — first project documentation of any kind beyond
  Unity's default URP template readme.

**State of the project at this point:**
- Core gameplay loop is complete and working: `Board` / `Trace` / `PcbNode` / `Spark` /
  `LevelManager` / `BoardRig` all wired together, front/back flipping via Via nodes
  functional, win detection + HUD (Prev/Restart/Next) functional.
- Custom in-editor level design tool (`Tools > PCB > Level Editor`) is complete:
  place/drag/erase nodes, traces (with 45° auto-routing), decorations; save/load levels
  as prefabs; unsaved-changes tracking; a level validator (start/goal counts, cross-layer
  trace errors, ambiguous exits, diagonal-only-reachable exits, dead-end vias).
- 4 levels exist and are registered in `LevelList.asset`: `Level 1`, `Level 02`,
  `Level 03`, `Level 04`. `Level 04` is the one currently open in `SampleScene.unity`.
- `PcbMechanics.cs` defines `TraceMechanic` / `NodeMechanic` extension points for
  gameplay modifiers (blocking traces, switches, pickups, etc.) but **no concrete
  mechanic has been implemented yet** — routing + side-flipping is the only mechanic
  in the game so far.
- No audio in the project yet.
- No compile errors, no TODO/FIXME markers found anywhere in the codebase at time of scan.

**Known minor items, not yet acted on:**
- Working tree has a handful of local-only, non-code diffs (`.vscode/settings.json`,
  `ProjectSettings/EditorBuildSettings.asset`, `UserSettings/...`) plus an untracked
  `inner-spark-unity.slnx` — these look like IDE/solution regeneration after the project
  was renamed from `spark-kun` to `inner-spark-unity`. Not touched; harmless either way.

**Suggested next steps** (not started):
- Decide and implement the first concrete `TraceMechanic`/`NodeMechanic` (see DESIGN.md § Open design space).
- Consider committing the pending local settings changes or adding them to `.gitignore` if they're meant to stay machine-local.

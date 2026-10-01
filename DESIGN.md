# Inner Spark — Design & Reference Doc

The living reference for the project: what the game is, how the code is put together, and the
vocabulary used in the scripts. Code comments cover the *how*; this file is the *why* and *what's
planned*. [PROGRESS.md](PROGRESS.md) is the dated log of what changed and why.

*Last full refresh: 2026-10-02.*

---

## 1. Concept

A puzzle game on a printed circuit board. The player is **Sparky**, a little electric character
who travels as electricity along copper **traces** between stop points (**nodes**), from a **Start**
plug to a **Goal** plug. The board has a front and a back: **Via** nodes let Sparky pass through and
turn the board over, changing which traces are available. Puzzle elements on top of routing +
side-switching:
- **Switches** (normal / AND) that open and close **gates** on traces.
- **Data** pickups on capacitors that must all be collected before the goal unlocks.

Stages are played in a fixed order (Level List); finishing one unlocks the next; the last one leads
to an ending screen. Each stage can open with a short intro cinematic (a device on a table in a room,
the camera zooms in, the casing fades away to reveal the PCB) and an intro dialog that teaches it.
There's no on-screen text during play — tutorials live in the dialogs.

*Open:* target platform(s) (built for PC, 16:9, 1920×1080 so far), final level count / difficulty
arc, future mechanics (key + lock art exists: `Key_*`, `Key_Lock_*`, `Key_Node_*`).

## 2. Controls

| Action | Keyboard / mouse | Gamepad |
|---|---|---|
| Move (8 directions) | WASD / Arrow keys | Left stick / D-pad |
| Flip side (on a via) / use a switch | Space | South button |
| Restart level | R / on-screen Restart button | Select |
| Pause / resume | Esc / on-screen Pause button | Start |
| Menus (navigate / press) | Mouse, or Arrow keys + Enter | D-pad / stick + South |
| Advance dialog | Continue button (first press finishes a line still typing) | Submit |
| Inspect board (tilt) | Hold left mouse + drag | — |

- **Input reading** (`Spark.ReadInput`): per axis; only a key going *down* counts as a press (releasing
  one key of a diagonal never queues a move); two keys pressed within 80 ms combine into a diagonal.
  Input is read in screen space, so it stays intuitive when the back of the board is shown mirrored.
- **Buffering:** a press made within `Spark.inputBuffer` (0.15 s) of Sparky becoming ready (still moving
  / animating) is carried over; older presses are forgotten (no double-tap double steps).
- **Locked:** while paused nothing is queued; during the stage start sequence (fade, intro, Sparky
  appearing, dialog) Sparky, Restart, Pause and board tilting are all off; at the goal input stops.
- Menus select their first button when they open (keyboard / gamepad navigation).

## 3. Vocabulary

| Term | Meaning |
|---|---|
| **Board** | Root of a level (a prefab). Owns its nodes / traces / decorations, builds the movement graph and the generated 3D look. |
| **Node** (`PcbNode`) | A stop point. Types: `Capacitor`, `Via` (both sides, flip point), `Start`, `Goal`, `Switch`, `AndSwitch`. |
| **Trace** | A copper line between two nodes on one side; Sparky slides along it once entered. Can bend. |
| **Layer** | `Front` / `Back`. Vias belong to both. |
| **Spark** | The player. With a character model (the `Spark_Sparky` prefab) it's Sparky; without one, a glowing sphere. |
| **Gate** | A `GateMechanic` on a trace: blocks it while closed. Normal gate: any of its switches flips it. AND gate: open only while all its AND switches are on. |
| **Data** | A pickup on a capacitor (`DataMechanic`). While any is left, the goal is locked (a lock hovers over it). |
| **Decoration** | Cosmetic set-dressing (`PcbDecoration`), never part of the graph. |
| **Theme** (`PcbTheme`) | Shared asset: materials, default models, a **Catalog** of variant models, and every size. |
| **Look** | A level's own default models (`Board.look`); a node / gate / decoration can override with its own `model`. Model used = own → level Look → theme. |
| **Rig** (`BoardRig`) | Pivot that turns the board over, tilts it, and frames the camera. |
| **Intro** | Optional per-stage cinematic prefab (`StageIntro`) on `Board.intro`. |

## 4. Architecture map

**Gameplay** (`Assets/Script/PCB/`)
- **Board.cs** — collects nodes / traces / decorations, builds the exit graph (`TryPickExit`), rebuilds
  the look when something changed (`ComputeSignature`), front / back visibility, model resolution
  (`NodeModel`, `GateModel`, …), data state (`GoalLocked`, `UnlockGoals`).
- **BoardVisuals.cs** — builds the whole 3D look; everything generated is `DontSave`, so levels only
  store gameplay data. Built-in shapes unless a model is assigned. Node / decoration / gate models are
  placed at authored size; board tile / trace / bend models are resized to the theme's sizes (`Fit`).
  Gates stand across the middle of their trace (`BuildGate`); data pickups and the goal lock hover
  (`BuildHover`).
- **Trace.cs**, **PcbNode.cs**, **PcbDecoration.cs** (in `Assets/Script/`), **PcbTypes.cs** — data
  components and enums. `PcbNode.rotationDegrees` spins a node's model (visual only).
- **Spark.cs** — the player: input, movement along the exit graph, flipping, switches, and the Sparky
  character sequences (Animator states played by name: Idle / MoveStart / MoveFinish / Win; idle /
  travel / burst VFX). `Appear()` is called by the stage start sequence; `InputLocked` blocks input —
  never disable the component (it would cut an animation sequence short).
- **PcbMechanics.cs** — `TraceMechanic` / `NodeMechanic` base classes. Concrete mechanics:
  - **SwitchMechanic.cs** — on a Switch / AndSwitch node; Space toggles it (`onToggle` event);
    swaps its model's ON / OFF look (**SwitchVisual.cs**).
  - **GateMechanic.cs** / **AndGateMechanic.cs** — on a trace; hold their `switches` list (Level Editor
    Link tool). Normal: any press flips (`isOpen` = start state). AND: open while all on (`inverted` =
    open until all on). Model shows CLOSED / OPEN via **LockVisual.cs**. Hand-wiring a switch's
    `onToggle → SetOpen` (Level 04) still works.
  - **DataMechanic.cs** — data pickup; collected on arrival (runtime only — a restart resets it).
- **HoverVisual.cs** — bob + shrink-away for hovering looks (data, goal lock). **FadeGroup.cs** — fades a
  whole model via one animatable Alpha (intro cinematics).
- **BoardRig.cs** — board turn-over, mouse tilt, camera framing (`FitCamera`, `Refit`, board anchor,
  far clip).
- **LevelManager.cs** — one per gameplay scene. Stage flow as coroutines: entering a stage = black →
  fade in → gameplay music → [intro] → `Spark.Appear()` → [dialog] → play; Restart = quick fade →
  appear → play. Win → saves progress → win pop-up, or after the **last** stage the Ending scene.
  Fields: Board Anchor (fixed spot in the room), Camera Far Clip, fade times, ending scene name.
- **StageIntro.cs** — intro cinematic: placed at the board's centre while the screen is black, plays
  its Timeline after the fade-in, the camera follows its Camera Pose, then blends into gameplay.
- **LevelList.cs**, **PcbTheme.cs**, **PcbVisualOwner.cs** — play order, shared look, and the link from
  generated visuals back to their node / trace (scene clicks select the real object).

**Editor tools** (`Assets/Script/PCB/Editor/`)
- **PcbLevelEditorWindow** (`.cs`, `.Levels.cs`, `.Look.cs`, `.Switches.cs`, `.Data.cs`) — `Tools > PCB >
  Level Editor`: tools Select / Node / Trace / Erase / Decor / Paint / Link / Data; save / load levels
  as prefabs; Level List order; Look section; unsaved-changes check (with a **Why?** button);
  **Validate Level** (start / goal counts, cross-layer traces, ambiguous exits, 8-way reachability,
  one-sided vias, switch ↔ gate connections, data only on capacitors).
- **PcbAssetSetup.cs** (theme / materials / Level List bootstrap), **PcbSelectionRedirect.cs**.
- **ProgressMenu.cs** — `Tools > PCB > Reset Progress` / `Unlock All Stages` (testing).
- **UiScalingSetup.cs** — `Tools > PCB > Set Up UI Scaling (1920x1080)`: every canvas scales from a
  1920×1080 design size; build default resolution 1920×1080 full screen. Re-run after adding a scene.

**Audio** (`Assets/Script/Audio/`)
- **SoundBank.cs** — `Create > PCB > Sound Bank`: clip + balance volume per sound (menu / gameplay /
  ending music, click, start game, win, switch, pickup, goal unlock, gate open / close, fail, travel
  loop, dialog talking loop). Empty = silent.
- **AudioManager.cs** — one per scene; the first survives scene loads, later copies remove themselves.
  Static, null-safe API. Adds the click sound to every UI button. Player volumes in PlayerPrefs.
- **VolumeSlider.cs** — on a UI Slider (Music / SFX). *Not placed in any scene yet.*

**UI & flow** (`Assets/Script/UI/`, uGUI + TextMeshPro)
- **ScreenFader.cs** — self-creating black overlay; `LoadScene` = fade out → load → fade in (a scene can
  `Claim()` its own fade-in, as the gameplay scene does).
- **GameFlow.cs** — carries the chosen stage from the menu into the gameplay scene.
- **Progress.cs** — furthest unlocked stage (PlayerPrefs, by Level List position).
- **MainMenuController.cs** — Play (continues from the furthest unlocked stage) / Stage Select / Quit.
- **StageSelectController.cs** — one button per *unlocked* stage, built from the Level List.
- **PauseMenu.cs** — pause panel; `SetAvailable` greys out Pause / Restart during the start sequence.
- **DialogSequence.cs** / **DialogController.cs** — per-stage intro dialog; lines type out with the
  talking sound.
- **WinPanel.cs** — win pop-up (Next Level / Restart). **EndingScreen.cs** — ending scene; a click after
  2 s returns to the menu. **UiSelect.cs** — selects a menu's first button (keyboard / gamepad).

**Scenes** (build order): `MainMenu` → `SampleScene` (gameplay) → `Ending`. Every canvas: Scale With
Screen Size, 1920×1080.

## 5. Level data & workflow

- A level = a `Board` prefab in `Assets/PCB/Levels/`, listed in play order in `Assets/PCB/LevelList.asset`.
- Prefabs hold **gameplay data only** (nodes, traces, decorations, mechanics, look choices, dialog,
  intro). The 3D look is regenerated at load from the theme.
- Visual choices are stored as references to prefabs (own → level Look → theme), so reordering the
  theme's catalog never breaks a level.
- Levels are drawn in the Scene view with the Level Editor.
- **Level List as of 2026-10-02 (13):** `Level 1`, `Level 02`–`Level 07`, then `Level 01 Tung`–`Level 06 Tung`.
  🟡 Decide which set is final — the ending plays after the *last* entry, and saved progress is by
  position (reordering shifts what players have unlocked; use Reset Progress when testing).

## 6. Open design space

- [ ] Final stage list / count and difficulty arc (see § 5).
- [ ] Next mechanic — key + lock art exists (`Key_*`, `Key_Lock_*`, `Key_Node_*` in 3 colours).
- [ ] Room background + per-stage intro cinematics (code ready; setup steps in PROGRESS 2026-10-02).
- [ ] UI art for every screen (Main Menu, Stage Select, HUD, Pause, Dialog, Win, Ending) and the
      Music / SFX sliders.
- [ ] Audio tuning; missing clips (switch, travel, menu music, gate close).
- [ ] Non-16:9 screens (letterbox or not?), windowed mode, any player options (resolution, rebinding).
- [ ] LED decorations aren't registered as a decoration type yet.

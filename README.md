# Inner Spark

![Inner Spark key art: Sparky](Docs/key_art.png)

**Inner Spark** is a puzzle game set inside old game consoles. You are **Sparky**, a little spark of
electricity, racing along the copper traces of a printed circuit board to wake each machine back up.

Every stage is a two-sided board. Slip through vias to flip it over, press switches to open and close
gates, collect every piece of data to unlock the goal, and swap colour passes to get through locks — all
without getting yourself stuck.

- **20 stages across five consoles:** ColekoTelestar, Altary2600, NESt, Gamerboi and PlayingState. Each
  console opens with a short cinematic and Sparky's commentary on its history.
- **Learn as you go:** Sparky's dialog introduces each new mechanic as it appears.
- **3 bonus stages:** unlocked after the ending, for players who want a real challenge.

## Team — Banh Mi Team

| Name | Role |
|---|---|
| Truong Quang Nghia | Programming |
| Nguyen Duc Tung | Game design, level design, programming |
| Babar Ahmed Kemal | Narrative, game design, level design |
| Andrii Nhuien | Art, music, VFX, SFX, UI |
| William Gauthier | Narrative, UI, game design, level design |

## Engine & language

- **Unity 6.3 LTS** (6000.3.12f1) with the Universal Render Pipeline
- **C#**
- Platform: Windows 10 or later, DirectX 12

## How to launch

1. Download the build from the game's page on the jam hosting site and unzip it.
2. Run **`Inner Spark.exe`**. No Unity installation is needed.

The game opens in a 1920×1080 window, which you can resize; the interface scales with it. Press
**Alt + Enter** to switch to fullscreen.

### Controls

| Action | Keyboard / mouse | Gamepad |
|---|---|---|
| Move (8 directions; diagonals = two directions together) | WASD / arrow keys | Left stick / D-pad |
| Interact: flip the board on a via, press a switch, take a pass | Space / Enter | South button |
| Continue dialog (first press shows the whole line) | Space / Enter | South button |
| Next stage after a win | Space | South button |
| Restart the stage | R | Select |
| Pause | Esc | Start |
| Tilt the board to look around | Hold left mouse button + drag | — |
| Menus | Mouse, or arrow keys + Enter | D-pad + South button |

The **Pause** and **Restart** buttons in the top-right corner work with the mouse too.

## Known issues

- There are no in-game volume settings.
- Nothing on the board shows which switch controls which gate; players find out by pressing the switch.

## AI-generated content

| Tool | Type of content | Context / usage |
|---|---|---|
| Claude (Anthropic), via Claude Code | Code | Gameplay systems, editor tools for building levels, menus and UI behaviour, and bug fixes, written to the team's direction and reviewed in Unity by the team. |
| Claude (Anthropic), via Claude Code | Level design | First drafts of stages 11–20 and the three bonus stages, generated and checked with a puzzle solver, then edited by our level designer into the final stages. |
| Claude (Anthropic), via Claude Code | Narrative / text | The tutorial lines in Sparky's dialog, added alongside the team's own console lines; short interface text ("PAUSED", "STAGE CLEAR!"). |
| Claude (Anthropic), via Claude Code | Documentation | This README and the project's design and progress notes. |

No other AI tools were used. All other art, music, sound, writing and levels were made by the team or
taken from free sources (see Credits).

## Credits

- 3D models, textures, VFX and UI art: **Andrii Nhuien** (team)
- Sound effects: custom made by the team
- Music: made by the team, plus free tracks from **Pixabay**
- Room props: **Kenney** assets
- Fonts: **Upheaval** (free font) and **Liberation Sans** (TextMesh Pro default)
- Built with **Unity** and **TextMesh Pro**

## Project structure

| Folder / file | Contents |
|---|---|
| `Assets/Script/` | Game code: `PCB/` gameplay and level tools, `UI/`, `Audio/` |
| `Assets/PCB/` | Stages (`Levels/`), stage order, look, dialog, sound settings |
| `Assets/Import Asset/` | Art, sounds and VFX |
| `Assets/Scenes/` | `MainMenu`, `SampleScene` (gameplay), `Ending` |
| `Docs/` | Stage solutions, dialog history |
| `Tools/LevelDesign/` | Python puzzle solver and level checks (run outside Unity) |
| `DESIGN.md`, `PROGRESS.md` | Design reference and development log |

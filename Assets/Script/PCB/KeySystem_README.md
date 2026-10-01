# PCB Key & Gate System - Usage Guide

This system adds interactive colored keys, security cards, and locking gates to the PCB puzzle game. 

## 1. Key Types (`KeyType.cs`)
Keys are defined by their color or function. The current available types are:
- `None` (Empty)
- `Red`, `Blue`, `Green`, `Yellow` (Standard colored keys)
- `SecurityCard` (Special non-consumable key)

## 2. Placing Keys on the Board (`KeyNodeMechanic.cs`)
To place a key in the level, it must sit on top of a **Capacitor** node.
1. Select a Capacitor node in your Unity scene.
2. Add the `KeyNodeMechanic` component to it.
3. Set the **Current Key** to your desired color (e.g., `Red` or `SecurityCard`).
4. *(Optional)* Assign a **Key Visual Prefab** to give it a custom 3D model (like a 3D key model or a flat card). If left empty, a colored bobbing sphere is generated automatically.
5. Adjust the **Hover Height** to configure how high the key floats above the board surface.

## 3. Player Interaction (`Spark.cs`)
Spark (the player) can carry exactly **one** key or card at a time. The interaction is triggered by pressing the **Enter** key (or Space/Action button) when stopped on a Capacitor.
- **Pick Up:** Move onto a capacitor holding a key and press **Enter**.
- **Drop:** Move onto an *empty* capacitor and press **Enter** to place the carried key down.
- **Swap:** If Spark is carrying a key and moves onto a capacitor that *also* has a key, pressing **Enter** will seamlessly swap the two items.

*(Note: Spark carries the item "invisibly" so it doesn't clutter the screen while moving, but Spark perfectly remembers your custom prefabs and will restore them when dropped back onto a capacitor).*

## 4. Consumable Lock Gates (`KeyGateMechanic.cs`)
These gates require a specific number of colored keys to open permanently.
1. Select a Trace (path) that you want to act as a gate.
2. Add the `KeyGateMechanic` component.
3. Set the **Required Key Type** (e.g., `Red`).
4. Set the **Required Amount** (e.g., `3`).
5. When Spark bumps into the gate while holding the correct key, the key is consumed, and the gate's counter increases. Once the counter is full, the gate permanently opens!

## 5. Security Gates (`SecurityGateMechanic.cs`)
Security gates act as checkpoints that only let you pass *while* you are holding the correct pass.
1. Select a Trace and add the `SecurityGateMechanic` component.
2. Set the **Required Card** to `SecurityCard`.
3. When Spark attempts to pass through, the gate checks if Spark is currently holding the card. 
4. **Crucial Difference:** The Security Card is **not** consumed upon crossing! You keep the card and can pass back and forth freely.
5. If you drop the Security Card on a capacitor, the security gate will instantly block your passage again until you retrieve the card.

## 6. Merged into main (2026-10-02) — what changed
- Gates (key and security) use the **board-built gate model** like every other gate: theme Gate Prefab /
  level Look / the gate's own **Model** (old `customGatePrefab` values carry over), showing its CLOSED /
  OPEN look via `LockVisual`. The old runtime `closedVisual` / red cube is gone.
- Security gate = the **pass** idea: open (and shown OPEN) only while Sparky carries the required pass;
  never used up. Any `KeyType` can be a pass.
- The key gate's floating "1/3" text was dropped (no on-screen text during play).
- Picking up / dropping plays the Pickup sound. Space or Enter (gamepad South) interacts.
- Test levels: `Assets/PCB/Levels/Test Key 06` (key gates) and `Test Key 07` (pass gate) — not in the Level List.

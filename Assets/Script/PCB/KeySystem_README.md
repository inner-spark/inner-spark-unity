# Pass System — usage guide

Passes come in three colours (`KeyType`: **Green, Red, Teal**, matching the `Key_*` / `Key_Node_*` /
`Key_Lock_*` art). Sparky carries **one pass at a time**.

## Nodes (place with Level Editor > Node tool)
- **Pass Holder** (`NodeType.PassHolder`, script `KeyNodeMechanic`) — an endless source of its colour.
  Its pass hovers over it. **Space / Enter** on it: Sparky takes the pass (any other pass it carried is
  destroyed); the hovering pass shrinks away and **a new one pops back in once Sparky leaves**. Already
  carrying that colour: nothing happens.
- **Pass Lock** (`NodeType.PassLock`, script `KeyLockMechanic`) — Sparky can only **move onto** it while
  carrying the matching pass (otherwise the move is refused before leaving). The pass is never used up.
  The lock's model shows **Unlocked** while Sparky carries its colour, **Locked** otherwise.
- Passes can't be dropped anywhere.

## Level Editor
- **Pass tool:** click a holder or lock to cycle its colour (Green → Red → Teal).
- **Validate Level** warns about: a lock with fewer than 2 traces, a lock colour with no holder, a holder
  colour with no lock, and pass scripts on the wrong node type.

## Art (PcbTheme > Passes: Green / Red / Teal)
- **Holder** — `Key_Node_*` model (authored like other node models, top facing −Z).
- **Pass** — `Key_*` model, centred on its origin, facing the camera. Hovers over the holder at Data
  Height; a smaller copy (Spark > Carried Pass Scale / Offset) floats beside Sparky.
- **Lock Model** — `Key_Lock_*`, with a **Lock Visual** on its root: **Locked** / **Unlocked** children.
- Empty slots show coloured placeholder shapes.

## Code
- `Spark.carriedKey`, `Spark.SetCarriedKey`, static `Spark.OnCarriedKeyChanged` (locks refresh their look).
- `NodeMechanic.CanArrive(spark)` — the lock's "can Sparky move onto me" check (checked in `Spark.TryMove`).
- `KeyGateMechanic` (a gate using up N keys of a colour) is from the earlier key branch and not used now.

# Claude levels 11-20 — solutions

Generated and checked by a solver that mirrors the game rules (8-way moves, vias, switches / gates,
data, passes). "Shortest" = fewest actions (moves + Space presses).

## Claude lvl 11 — Data, AND switch

Board 7x8, 14 nodes (4 decoys), 14 traces. Shortest solution: **17 actions** (12 moves).

→ D1 → A1 → V2 **flip** → A2 → D2 → A2 **press A2** → V2 **flip** → A1 **press A1** → C1 → V1 **flip** → C3 → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 12 — Normal switch, Data, AND switch

Board 8x7, 14 nodes (4 decoys), 13 traces. Shortest solution: **19 actions** (15 moves).

→ N1 → C1 → D2 → C1 → A2 **press A2** → C1 → N1 **press N1** → C2 → A1 **press A1** → C2 → N1 → V1 **flip** → D1 → V1 → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 13 — Pass, AND switch

Board 9x9, 15 nodes (4 decoys), 15 traces. Shortest solution: **15 actions** (10 moves).

→ HR **take Red** → LR → A1 **press A1** → V2 **flip** → HG **take Green** → V1 → LG → A2 **press A2** → C → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 14 — Pass

Board 9x6, 14 nodes (5 decoys), 13 traces. Shortest solution: **13 actions** (9 moves).

→ HR **take Red** → LR1 → V1 **flip** → HG **take Green** → V1 → LG → HR2 **take Red** → LR2 → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 15 — Normal switch, Data

Board 6x8, 14 nodes (5 decoys), 13 traces. Shortest solution: **20 actions** (16 moves).

→ N1 **press N1** → C1 → V1 → D3 → V1 → C1 → N1 → D1 → N2 **press N2** → D1 → N1 **press N1** → C1 → V1 **flip** → D2 → V1 → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 16 — Pass, AND switch

Board 8x9, 16 nodes (6 decoys), 15 traces. Shortest solution: **18 actions** (13 moves).

→ HG **take Green** → S → LG2 → A1 **press A1** → LG2 → S → HG → LG → HR **take Red** → LR → V1 **flip** → A2 **press A2** → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 17 — Pass, Data, AND switch

Board 10x10, 18 nodes (6 decoys), 18 traces. Shortest solution: **27 actions** (20 moves).

→ HR → A1 **press A1** → HR **take Red** → S → V0 **flip** → LR → D2 → LR → V0 → HG **take Green** → V0 **flip** → S → HR → LG → D1 → LG → V1 **flip** → A2 **press A2** → V1 → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 18 — All

Board 9x9, 19 nodes (7 decoys), 19 traces. Shortest solution: **23 actions** (16 moves).

→ N1 → C1 → D1 → V2 **flip** → A2 **press A2** → V2 **flip** → D1 → C1 → N1 **press N1** → HR **take Red** → V1 **flip** → LR → A1 → D2 → A1 **press A1** → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 19 — All

Board 7x8, 18 nodes (7 decoys), 17 traces. Shortest solution: **21 actions** (16 moves).

→ N1 → D1 → N1 **press N1** → S → C1 → HR **take Red** → C1 → A1 **press A1** → V1 **flip** → LR → A2 → D2 → A2 **press A2** → LR → V1 → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

## Claude lvl 20 — All

Board 8x8, 23 nodes (7 decoys), 25 traces. Shortest solution: **32 actions** (23 moves).

→ D1 → N2 **press N2** → D1 → S → HG **take Green** → N1 → V1 **flip** → LG → A1 **press A1** → LG → V1 → HR **take Red** → V1 **flip** → N1 **press N1** → HG → LR → V2 **flip** → D3 → V2 → A2 **press A2** → LR2 → D2 → G

Node ids: S start, G goal, V via, D data, N normal switch, A AND switch, H… pass holder, L… pass lock (R red, G green), C plain capacitor, X… decoy (dead end; X…c = the capacitor behind a decoy via).

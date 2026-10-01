using System;
using System.Collections.Generic;
using System.IO;
using Pcb;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// Tools > PCB > Build Claude Levels: builds the level prefabs described in Assets/PCB/LevelData/claude_levels.json
/// (designed and solver-checked outside Unity, remixed with irregular positions, bent traces and dead-end decoys;
/// solutions in Claude_levels_solutions.md) and appends them to the
/// Level List. Tools > PCB > Build Claude Hard Levels does the same for claude_levels_hard.json (21+, made by
/// Tools/LevelDesign/gen.py; solutions in Claude_levels_hard_solutions.md). Coordinates are grid cells (0.5 each); each board is sized to its content. Re-running overwrites them.
/// </summary>
static class ClaudeLevelBuilder
{
    const string DataPath = "Assets/PCB/LevelData/claude_levels.json";
    const string HardDataPath = "Assets/PCB/LevelData/claude_levels_hard.json";
    const float Cell = 0.5f;

#pragma warning disable 0649 // filled by JsonUtility
    [Serializable] class Point { public float x, y; }
    [Serializable] class NodeData { public string id, type, side, passColour; public float x, y; public bool data, on; }
    [Serializable] class TraceData
    {
        public string a, b, side, gate;
        public List<Point> bends = new List<Point>();
        public bool gateOpen, gateInverted;
        public List<string> switches = new List<string>();
    }
    [Serializable] class LevelData { public string name; public int number, sizeX, sizeY; public List<NodeData> nodes; public List<TraceData> traces; }
    [Serializable] class FileData { public List<LevelData> levels; }
#pragma warning restore 0649

    [MenuItem("Tools/PCB/Build Claude Levels")]
    static void Build() => BuildFrom(DataPath);

    [MenuItem("Tools/PCB/Build Claude Hard Levels")]
    static void BuildHard() => BuildFrom(HardDataPath);

    static void BuildFrom(string dataPath)
    {
        if (!File.Exists(dataPath)) { Debug.LogError($"[PCB] {dataPath} not found."); return; }
        var file = JsonUtility.FromJson<FileData>(File.ReadAllText(dataPath));
        var theme = PcbAssetSetup.GetOrCreateTheme();
        var list = PcbAssetSetup.GetOrCreateLevelList();
        var preview = EditorSceneManager.NewPreviewScene(); // build off-screen: the open scene isn't touched
        int built = 0;
        try
        {
            foreach (var level in file.levels)
            {
                var root = BuildLevel(level, theme);
                UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(root, preview);
                string path = $"{PcbAssetSetup.LevelFolder}/{level.name}.prefab";
                root.GetComponent<Board>().savedPath = path;
                var prefab = PrefabUtility.SaveAsPrefabAsset(root, path, out bool ok);
                UnityEngine.Object.DestroyImmediate(root);
                if (!ok) { Debug.LogError($"[PCB] Could not save {path}"); continue; }
                var board = prefab.GetComponent<Board>();
                if (!list.levels.Contains(board)) list.levels.Add(board);
                built++;
            }
        }
        finally { EditorSceneManager.ClosePreviewScene(preview); }
        EditorUtility.SetDirty(list);
        AssetDatabase.SaveAssets();
        Debug.Log($"[PCB] Built {built} Claude level(s) in {PcbAssetSetup.LevelFolder} and added them to the Level List.");
    }

    static GameObject BuildLevel(LevelData level, PcbTheme theme)
    {
        var go = new GameObject("Board");
        var board = go.AddComponent<Board>();
        board.levelName = level.name;
        board.theme = theme;
        board.cellSize = Cell;
        board.sizeInCells = new Vector2Int(level.sizeX > 0 ? level.sizeX : 10, level.sizeY > 0 ? level.sizeY : 10); // sized to the content
        board.editorView = PcbLayer.Front;
        var nodesRoot = Child(go.transform, "Nodes");
        var tracesRoot = Child(go.transform, "Traces");

        var nodes = new Dictionary<string, PcbNode>();
        foreach (var n in level.nodes)
        {
            var type = NodeTypeOf(n.type);
            var layer = n.side == "B" ? PcbLayer.Back : PcbLayer.Front;
            string sideTag = type == NodeType.Via ? "" : layer == PcbLayer.Front ? " F" : " B";
            var nodeGo = new GameObject($"{n.id} {type}{sideTag}"); // id first: matches Claude_levels_solutions.md
            nodeGo.transform.SetParent(nodesRoot, false);
            nodeGo.transform.localPosition = new Vector3(n.x * Cell, n.y * Cell, 0f);
            var node = nodeGo.AddComponent<PcbNode>();
            node.type = type;
            node.layer = layer;
            if (type == NodeType.Goal) node.chipSize = new Vector2(0.5f, 0.45f);
            if (node.IsSwitch) nodeGo.AddComponent<SwitchMechanic>().isOn = n.on;
            if (n.data) nodeGo.AddComponent<DataMechanic>();
            if (type == NodeType.PassHolder) nodeGo.AddComponent<KeyNodeMechanic>().pass = PassOf(n.passColour);
            if (type == NodeType.PassLock) nodeGo.AddComponent<KeyLockMechanic>().pass = PassOf(n.passColour);
            nodes[n.id] = node;
        }

        foreach (var t in level.traces)
        {
            var from = nodes[t.a];
            var to = nodes[t.b];
            var traceGo = new GameObject($"Trace {from.name} - {to.name}");
            traceGo.transform.SetParent(tracesRoot, false);
            var trace = traceGo.AddComponent<Trace>();
            trace.from = from;
            trace.to = to;
            trace.layer = t.side == "B" ? PcbLayer.Back : PcbLayer.Front;
            trace.bends = new List<Vector2>();
            foreach (var p in t.bends) trace.bends.Add(new Vector2(p.x * Cell, p.y * Cell));

            if (t.gate == "normal" || t.gate == "and")
            {
                GateMechanic gate;
                if (t.gate == "and")
                {
                    var andGate = traceGo.AddComponent<AndGateMechanic>();
                    andGate.inverted = t.gateInverted;
                    gate = andGate;
                }
                else
                {
                    gate = traceGo.AddComponent<GateMechanic>();
                    gate.isOpen = t.gateOpen;
                }
                foreach (var s in t.switches) gate.switches.Add(nodes[s].GetComponent<SwitchMechanic>());
            }
        }
        return go;
    }

    static Transform Child(Transform parent, string name)
    {
        var t = new GameObject(name).transform;
        t.SetParent(parent, false);
        return t;
    }

    static NodeType NodeTypeOf(string type) => type switch
    {
        "via" => NodeType.Via,
        "start" => NodeType.Start,
        "goal" => NodeType.Goal,
        "sw" => NodeType.Switch,
        "and" => NodeType.AndSwitch,
        "holder" => NodeType.PassHolder,
        "lock" => NodeType.PassLock,
        _ => NodeType.Capacitor
    };

    static KeyType PassOf(string colour) => colour switch
    {
        "Red" => KeyType.Red,
        "Teal" => KeyType.Teal,
        _ => KeyType.Green
    };
}

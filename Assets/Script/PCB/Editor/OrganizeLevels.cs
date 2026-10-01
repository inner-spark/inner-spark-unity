using System.Collections.Generic;
using System.IO;
using Pcb;
using UnityEditor;
using UnityEngine;

/// <summary>
/// One-shot: Tools > PCB > Organize Final Levels. Renames the 20 main stages + 3 bonus stages to their final
/// names ("NES: Level 6" in game, "NES - Level 06.prefab" on disk), moves every other level prefab to
/// Levels/Archive, and sets the Level List to exactly these 23 (Main Stage Count 20). Undo isn't supported
/// (asset moves), so it asks first; references survive because the assets are moved through the AssetDatabase.
/// Safe to delete this script once it has run.
/// </summary>
static class OrganizeLevels
{
    // play order: (current file name, console / group, level number)
    static readonly (string file, string console, int number)[] Plan =
    {
        ("Level 01 Tung", "ColekoTelestar", 1),
        ("Level 02 Tung", "Altary2600", 2),
        ("Level 03 Tung", "Altary2600", 3),
        ("Level 04 Tung", "Altary2600", 4),
        ("Level 05 Tung", "Altary2600", 5),
        ("Level 06 Tung", "NES", 6),
        ("Level 08 Tung", "NES", 7),
        ("Level 9 Tung", "NES", 8),
        ("Level  9 true Tung", "NES", 9),
        ("Level 10 true Tung", "NES", 10),
        ("Tung lvl 11", "NES", 11),
        ("Tung lvl 12 true", "NES", 12),
        ("Tung lvl 13", "Gameboy", 13),
        ("Tung lvl 14", "Gameboy", 14),
        ("Tung lvl 15", "Gameboy", 15),
        ("Tung  lvl 16", "Gameboy", 16),
        ("Tung lvl 17", "Gameboy", 17),
        ("Tung lvl 18", "PS1", 18),
        ("Tung lvl 19", "PS1", 19),
        ("Tung lvl 20", "PS1", 20),
        ("Tung lvl 21", "Bonus", 21),
        ("Tung lvl 22", "Bonus", 22),
        ("Tung lvl 23", "Bonus", 23),
    };
    const int MainStages = 20;

    [MenuItem("Tools/PCB/Organize Final Levels")]
    static void Run()
    {
        string folder = PcbAssetSetup.LevelFolder;
        string archive = folder + "/Archive";

        // Check everything first: nothing is touched unless every source exists and no target is taken.
        var missing = new List<string>();
        foreach (var p in Plan)
        {
            if (!File.Exists($"{folder}/{p.file}.prefab")) missing.Add(p.file);
            string target = $"{folder}/{FileName(p)}.prefab";
            if (File.Exists(target) && FileName(p) != p.file) missing.Add($"(target already exists) {FileName(p)}");
        }
        if (missing.Count > 0)
        {
            EditorUtility.DisplayDialog("Organize Final Levels", "Not run - these are missing / in the way:\n\n" + string.Join("\n", missing), "OK");
            return;
        }
        var keep = new HashSet<string>();
        foreach (var p in Plan) keep.Add($"{folder}/{p.file}.prefab");
        var others = new List<string>();
        foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { folder }))
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if (Path.GetDirectoryName(path).Replace('\\', '/') == folder && !keep.Contains(path)) others.Add(path);
        }
        if (!EditorUtility.DisplayDialog("Organize Final Levels",
                $"Rename {Plan.Length} levels to their final names, move {others.Count} other level prefabs to {archive}, " +
                $"and set the Level List to these {Plan.Length} (Main Stage Count {MainStages}).\n\nThis can't be undone with Ctrl+Z.",
                "Organize", "Cancel"))
            return;

        if (!AssetDatabase.IsValidFolder(archive)) AssetDatabase.CreateFolder(folder, "Archive");
        foreach (var path in others)
        {
            string target = AssetDatabase.GenerateUniqueAssetPath($"{archive}/{Path.GetFileName(path)}");
            string error = AssetDatabase.MoveAsset(path, target);
            if (!string.IsNullOrEmpty(error)) Debug.LogError($"[PCB] Could not archive {path}: {error}");
        }

        var list = PcbAssetSetup.GetOrCreateLevelList();
        var boards = new List<Board>();
        foreach (var p in Plan)
        {
            string path = $"{folder}/{p.file}.prefab";
            string newPath = $"{folder}/{FileName(p)}.prefab";
            if (newPath != path)
            {
                string error = AssetDatabase.RenameAsset(path, FileName(p));
                if (!string.IsNullOrEmpty(error)) { Debug.LogError($"[PCB] Could not rename {path}: {error}"); continue; }
            }
            var root = PrefabUtility.LoadPrefabContents(newPath);
            var board = root.GetComponent<Board>();
            board.levelName = $"{p.console}: Level {p.number}";
            board.savedPath = newPath;
            PrefabUtility.SaveAsPrefabAsset(root, newPath);
            PrefabUtility.UnloadPrefabContents(root);
            boards.Add(AssetDatabase.LoadAssetAtPath<Board>(newPath));
        }

        Undo.RecordObject(list, "Organize Final Levels");
        list.levels = boards;
        list.mainStageCount = MainStages;
        EditorUtility.SetDirty(list);
        AssetDatabase.SaveAssets();
        Debug.Log($"[PCB] Organized: {boards.Count} levels in the Level List (Main Stage Count {MainStages}), {others.Count} archived to {archive}.");
    }

    static string FileName((string file, string console, int number) p) => $"{p.console} - Level {p.number:00}";
}

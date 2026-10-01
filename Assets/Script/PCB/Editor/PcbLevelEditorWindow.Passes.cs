using System.Collections.Generic;
using Pcb;
using UnityEditor;
using UnityEngine;

/// <summary>
/// Pass part of the PCB Level Editor: the Pass tool (click a Pass Holder / Pass Lock to cycle its colour) and
/// the pass validation. Holders give a pass of their colour; locks can only be entered carrying that colour.
/// </summary>
public partial class PcbLevelEditorWindow
{
    static readonly KeyType[] PassColours = { KeyType.Green, KeyType.Red, KeyType.Teal };
    static readonly string[] PassColourNames = { "Green", "Red", "Teal" };

    /// <summary>Colour given to newly placed Pass Holders / Locks (Node tool) and to clicked ones (Pass tool).</summary>
    KeyType passColour = KeyType.Red;

    void PassColourField()
    {
        int index = Mathf.Max(0, System.Array.IndexOf(PassColours, passColour));
        passColour = PassColours[EditorGUILayout.Popup("Pass Colour", index, PassColourNames)];
    }

    void PassOptionsGUI()
    {
        PassColourField();
        int holders = 0, locks = 0;
        foreach (var n in board.Nodes)
        {
            if (!n) continue;
            if (n.GetComponent<KeyNodeMechanic>()) holders++;
            if (n.GetComponent<KeyLockMechanic>()) locks++;
        }
        EditorGUILayout.LabelField("On this level", $"{holders} holder(s), {locks} lock(s)");
    }

    void PassTool(Event e, Vector2 mouse)
    {
        var node = PickNode(mouse);
        var holder = node ? node.GetComponent<KeyNodeMechanic>() : null;
        var passLock = node ? node.GetComponent<KeyLockMechanic>() : null;

        if (e.type == EventType.MouseDown && e.button == 0 && !e.alt)
        {
            if (holder) { Undo.RecordObject(holder, "Pass Colour"); holder.pass = passColour; }
            else if (passLock) { Undo.RecordObject(passLock, "Pass Colour"); passLock.pass = passColour; }
            else if (node) ShowNotification(new GUIContent("Only Pass Holder and Pass Lock nodes have a colour. Place them with the Node tool."));
            if (holder || passLock) { board.Rebuild(); dirtyCheckDue = true; }
            e.Use();
        }

        if (e.type != EventType.Repaint) return;
        foreach (var n in board.Nodes)
        {
            if (!n || !n.IsOnLayer(board.editorView)) continue;
            var h = n.GetComponent<KeyNodeMechanic>();
            var l = n.GetComponent<KeyLockMechanic>();
            if (!h && !l) continue;
            Handles.color = (h ? h.pass : l.pass).ToColor();
            if (h) Handles.DrawWireDisc(n.transform.position, Vector3.forward, board.cellSize * 0.42f, 3f);
            else Handles.DrawWireCube(n.transform.position, new Vector3(board.cellSize * 0.8f, board.cellSize * 0.8f, 0f));
        }
        if (node) HighlightNode(node, holder || passLock ? Color.white : new Color(1f, 0.3f, 0.3f));
    }

    /// <summary>Pass Holder / Pass Lock nodes need their script; other nodes shouldn't keep one (after a type change).</summary>
    void EnsurePassMechanic(PcbNode node)
    {
        var holder = node.GetComponent<KeyNodeMechanic>();
        var passLock = node.GetComponent<KeyLockMechanic>();
        if (node.type == NodeType.PassHolder && !holder) Undo.AddComponent<KeyNodeMechanic>(node.gameObject).pass = passColour;
        if (node.type != NodeType.PassHolder && holder) Undo.DestroyObjectImmediate(holder);
        if (node.type == NodeType.PassLock && !passLock) Undo.AddComponent<KeyLockMechanic>(node.gameObject).pass = passColour;
        if (node.type != NodeType.PassLock && passLock) Undo.DestroyObjectImmediate(passLock);
    }

    void ValidatePasses()
    {
        var holderColours = new HashSet<KeyType>();
        var lockColours = new HashSet<KeyType>();
        foreach (var n in board.Nodes)
        {
            if (!n) continue;
            var holder = n.GetComponent<KeyNodeMechanic>();
            var passLock = n.GetComponent<KeyLockMechanic>();
            if (n.type == NodeType.PassHolder && !holder) Add($"{n.name}: Pass Holder has no Key Node Mechanic. Change its type away and back with the Node tool.", n);
            if (n.type == NodeType.PassLock && !passLock) Add($"{n.name}: Pass Lock has no Key Lock Mechanic. Change its type away and back with the Node tool.", n);
            if (holder && n.type != NodeType.PassHolder) Add($"{n.name}: has a Key Node Mechanic but isn't a Pass Holder node (left over from the old key system?). Remove the component.", n);
            if (passLock && n.type != NodeType.PassLock) Add($"{n.name}: has a Key Lock Mechanic but isn't a Pass Lock node. Remove the component.", n);
            if (holder && n.type == NodeType.PassHolder) holderColours.Add(holder.pass);
            if (passLock && n.type == NodeType.PassLock)
            {
                lockColours.Add(passLock.pass);
                if (board.GetExits(n).Count < 2)
                    Add($"{n.name}: Pass Lock has fewer than 2 traces, so it can't be passed through - only stopped on.", n);
            }
        }
        foreach (var c in lockColours)
            if (!holderColours.Contains(c)) Add($"{c} Pass Lock(s) but no {c} Pass Holder on this level: they can never be entered.", board);
        foreach (var c in holderColours)
            if (!lockColours.Contains(c)) Add($"{c} Pass Holder(s) but no {c} Pass Lock on this level: that pass opens nothing.", board);
    }
}

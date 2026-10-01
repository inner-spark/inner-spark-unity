using UnityEngine;

namespace Pcb
{
    /// <summary>
    /// Pass Lock node: Sparky can only move onto it while carrying the matching pass (refused before leaving,
    /// like a closed gate). The pass isn't used up. The lock's model shows Unlocked while Sparky carries its colour
    /// and Locked otherwise (LockVisual on the model). Set the colour with Level Editor > Pass tool.
    /// </summary>
    public class KeyLockMechanic : NodeMechanic
    {
        [Tooltip("The pass Sparky must be carrying to move onto this node.")]
        public KeyType pass = KeyType.Green;

        public override bool CanArrive(Spark spark) => spark.carriedKey == pass;

        void OnEnable() => Spark.OnCarriedKeyChanged += Refresh;
        void OnDisable() => Spark.OnCarriedKeyChanged -= Refresh;

        void Refresh(KeyType carried)
        {
            var board = GetComponentInParent<Board>();
            if (!board) return;
            foreach (var look in board.VisualsOf(GetComponent<PcbNode>()))
                foreach (var lockLook in look.GetComponentsInChildren<LockVisual>(true))
                    lockLook.FadeTo(carried != pass); // fades the padlock out / back in
        }
    }
}

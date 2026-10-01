using UnityEngine;

namespace Pcb
{
    /// <summary>
    /// Pass Holder node: an endless source of one pass colour. Its pass hovers over it (built by the Board).
    /// Space / Enter here: Sparky takes the pass (any other pass it carried is gone), the hovering pass shrinks
    /// away, and a new one pops back in once Sparky leaves the holder. Already carrying this colour: nothing.
    /// Passes can't be dropped anywhere. Set the colour with Level Editor > Pass tool.
    /// </summary>
    public class KeyNodeMechanic : NodeMechanic
    {
        [Tooltip("Colour of this holder and of the pass it gives.")]
        public KeyType pass = KeyType.Green;

        bool empty; // taken, refills when Sparky leaves

        /// <summary>Sparky pressed Space / Enter here.</summary>
        public void Take(Spark spark)
        {
            if (empty || pass == KeyType.None || spark.carriedKey == pass) return; // nothing to do
            spark.SetCarriedKey(pass);
            empty = true;
            ShowPass(false);
            AudioManager.Play(Sfx.Pickup);
        }

        public override void OnSparkLeave(Spark spark)
        {
            if (!empty) return;
            empty = false;
            ShowPass(true);
        }

        void ShowPass(bool show)
        {
            var board = GetComponentInParent<Board>();
            if (!board) return;
            foreach (var look in board.VisualsOf(GetComponent<PcbNode>()))
                foreach (var hover in look.GetComponentsInChildren<HoverVisual>(true))
                    if (show) hover.Show(); else hover.Dismiss();
        }
    }
}

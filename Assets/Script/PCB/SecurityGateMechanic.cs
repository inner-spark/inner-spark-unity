namespace Pcb
{
    /// <summary>
    /// A pass gate on a trace: Sparky can only go through while carrying the required pass (any KeyType). The pass
    /// isn't used up, so Sparky can go back and forth; drop it and the gate closes again. The gate's model shows
    /// OPEN while Sparky holds the pass and CLOSED otherwise (LockVisual, like other gates).
    /// </summary>
    public class SecurityGateMechanic : GateMechanic
    {
        [UnityEngine.Header("Pass requirement")]
        [UnityEngine.Tooltip("The pass Sparky must be carrying to go through. It isn't used up.")]
        public KeyType requiredCard = KeyType.SecurityCard;

        public override bool UsesSwitches => false;

        // In the editor (and at level start) Sparky carries nothing: closed.
        public override bool ShownOpen => UnityEngine.Application.isPlaying && isOpen;

        public override bool CanEnter(Spark spark, bool reversed) => spark.carriedKey == requiredCard;

        protected override void OnEnable()
        {
            Spark.OnCarriedKeyChanged += HandleKeyChanged;
            SetOpen(false, playSound: false); // a new level's Sparky starts empty-handed
        }

        protected override void OnDisable() => Spark.OnCarriedKeyChanged -= HandleKeyChanged;

        void HandleKeyChanged(KeyType carried) => SetOpen(carried == requiredCard, playSound: true);
    }
}

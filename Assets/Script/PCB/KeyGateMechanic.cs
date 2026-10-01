namespace Pcb
{
    /// <summary>
    /// A key gate on a trace: needs a number of keys of one colour. Each time Sparky bumps into it carrying that key,
    /// the key is used up and counted; once enough are in, the gate opens for good. (Not a pass: see
    /// SecurityGateMechanic for gates you get through by holding a pass.)
    /// </summary>
    public class KeyGateMechanic : GateMechanic
    {
        [UnityEngine.Header("Key requirement")]
        public KeyType requiredKeyType = KeyType.Red;
        [UnityEngine.Min(1)] public int requiredAmount = 3;
        public int currentAmount = 0;

        public override bool UsesSwitches => false;

        public override bool CanEnter(Spark spark, bool reversed)
        {
            if (isOpen) return true;
            if (spark.carriedKey != requiredKeyType) return false;

            spark.SetCarriedKey(KeyType.None); // the key goes into the gate
            currentAmount++;
            if (currentAmount >= requiredAmount) SetOpen(true);
            return false; // stop this time, so the player sees the key go in
        }
    }
}

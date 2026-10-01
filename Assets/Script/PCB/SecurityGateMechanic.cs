using UnityEngine;

namespace Pcb
{
    public class SecurityGateMechanic : GateMechanic
    {
        [Header("Security Requirement")]
        public KeyType requiredCard = KeyType.SecurityCard;

        public override bool CanEnter(Spark spark, bool reversed)
        {
            // If Spark holds the required card, allow passage without consuming it.
            if (spark.carriedKey == requiredCard)
            {
                return true;
            }

            // Blocked, wrong key or no key
            return false;
        }

        private void OnEnable()
        {
            Spark.OnCarriedKeyChanged += HandleKeyChanged;
        }

        private void OnDisable()
        {
            Spark.OnCarriedKeyChanged -= HandleKeyChanged;
        }

        protected override void Start()
        {
            base.Start();
            // Initialize visual state based on what Spark is currently carrying (if Spark exists)
            var spark = FindObjectOfType<Spark>();
            KeyType initialKey = spark != null ? spark.carriedKey : KeyType.None;
            HandleKeyChanged(initialKey);
        }

        private void HandleKeyChanged(KeyType carriedKey)
        {
            if (closedVisual != null)
            {
                bool isHoldingKey = (carriedKey == requiredCard);
                bool beforeState = closedVisual.activeSelf;
                
                // Hide the block prefab if Spark holds the required card, otherwise show it
                bool targetState = !isHoldingKey;
                closedVisual.SetActive(targetState);
                
                Debug.Log($"[SecurityGate] {gameObject.name} visual update -> CarriedKey: {carriedKey} | Required: {requiredCard} | HoldingRequired: {isHoldingKey} | VisualActive: {beforeState} -> {targetState}");
            }
            else
            {
                Debug.LogWarning($"[SecurityGate] {gameObject.name} cannot update visual: closedVisual is null!");
            }
        }

        public override void OnTraversed(Spark spark, bool reversed)
        {
            // You can optionally add visual/audio effects here when Spark successfully passes through.
            base.OnTraversed(spark, reversed);
        }
    }
}

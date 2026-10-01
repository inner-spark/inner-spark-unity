using UnityEngine;
using TMPro; // Assuming TextMeshPro is used, fallback to standard Text or just debug if missing

namespace Pcb
{
    public class KeyGateMechanic : GateMechanic
    {
        [Header("Key Requirements")]
        public KeyType requiredKeyType = KeyType.Red;
        public int requiredAmount = 3;
        public int currentAmount = 0;

        [Header("UI")]
        public TextMeshPro textUI;

        public override bool CanEnter(Spark spark, bool reversed)
        {
            if (isOpen) return true;

            // Trying to enter a closed gate
            if (spark.carriedKey == requiredKeyType)
            {
                // Consume the key
                spark.SetCarriedKey(KeyType.None);
                
                currentAmount++;
                UpdateUI();

                if (currentAmount >= requiredAmount)
                {
                    SetOpen(true);
                }

                // Block the spark this frame so they can see they inserted the key
                // and they don't accidentally slide through if it wasn't the last key.
                return false; 
            }

            // Blocked, wrong key or no key
            return false;
        }

        private void Start()
        {
            UpdateUI();
        }

        private void UpdateUI()
        {
            if (textUI != null)
            {
                textUI.text = $"{currentAmount}/{requiredAmount}";
                // Color text based on required key
                switch (requiredKeyType)
                {
                    case KeyType.Red: textUI.color = Color.red; break;
                    case KeyType.Blue: textUI.color = Color.blue; break;
                    case KeyType.Green: textUI.color = Color.green; break;
                    case KeyType.Yellow: textUI.color = Color.yellow; break;
                }
            }
            else
            {
                Debug.Log($"[Gate {gameObject.name}] Key Requirement: {currentAmount}/{requiredAmount} {requiredKeyType}");
            }
        }
    }
}

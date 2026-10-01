using UnityEngine;

namespace Pcb
{
    public class KeyNodeMechanic : NodeMechanic
    {
        public KeyType currentKey = KeyType.None;
        [Tooltip("Optional visual prefab to spawn for this key. If null, a simple colored sphere is created.")]
        public GameObject keyVisualPrefab;
        
        private GameObject currentVisual;

        void Start()
        {
            UpdateVisual();
        }

        public void SetKey(KeyType newKey)
        {
            currentKey = newKey;
            UpdateVisual();
        }

        private void UpdateVisual()
        {
            // Destroy existing visual
            if (currentVisual != null)
            {
                Destroy(currentVisual);
            }

            if (currentKey == KeyType.None) return;

            // Spawn new visual
            if (keyVisualPrefab != null)
            {
                currentVisual = Instantiate(keyVisualPrefab, transform);
            }
            else
            {
                // Fallback basic visual
                currentVisual = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                currentVisual.name = $"KeyVisual_{currentKey}";
                currentVisual.transform.SetParent(transform, false);
                currentVisual.transform.localScale = new Vector3(0.15f, 0.15f, 0.15f);
                
                // Remove collider from the fallback visual
                Destroy(currentVisual.GetComponent<Collider>());
                
                var rend = currentVisual.GetComponent<Renderer>();
                if (rend)
                {
                    switch (currentKey)
                    {
                        case KeyType.Red: rend.material.color = Color.red; break;
                        case KeyType.Blue: rend.material.color = Color.blue; break;
                        case KeyType.Green: rend.material.color = Color.green; break;
                        case KeyType.Yellow: rend.material.color = Color.yellow; break;
                        case KeyType.SecurityCard: rend.material.color = Color.cyan; break;
                    }
                }
            }

            // Position it above the capacitor
            // Board.theme.traceHeight + spark size approx + a little extra
            currentVisual.transform.localPosition = new Vector3(0, 0, 0.2f); // Assuming Z is up relative to the node
            
            // Add a bobbing script if not present
            if (currentVisual.GetComponent<KeyBobAnimation>() == null)
            {
                currentVisual.AddComponent<KeyBobAnimation>();
            }
        }
    }

    // A small helper to animate the key floating
    public class KeyBobAnimation : MonoBehaviour
    {
        private Vector3 startLocalPos;
        public float bobSpeed = 3f;
        public float bobHeight = 0.05f;

        void Start()
        {
            startLocalPos = transform.localPosition;
        }

        void Update()
        {
            transform.localPosition = startLocalPos + new Vector3(0, 0, Mathf.Sin(Time.time * bobSpeed) * bobHeight);
        }
    }
}

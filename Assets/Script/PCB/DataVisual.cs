using UnityEngine;

namespace Pcb
{
    /// <summary>Added by the Board to a data pickup's generated look: spins and bobs it in play mode so it reads as a pickup.</summary>
    [AddComponentMenu("")]
    public class DataVisual : MonoBehaviour
    {
        public float spinSpeed = 90f;
        public float bobHeight = 0.03f;
        public float bobSpeed = 2.5f;
        [HideInInspector] public float outward = -1f; // away from the board on this side

        Vector3 basePosition;

        void Start() => basePosition = transform.localPosition;

        void Update()
        {
            transform.localRotation = Quaternion.Euler(0f, 0f, Time.time * spinSpeed);
            transform.localPosition = basePosition + new Vector3(0f, 0f, outward * bobHeight * Mathf.Sin(Time.time * bobSpeed));
        }
    }
}

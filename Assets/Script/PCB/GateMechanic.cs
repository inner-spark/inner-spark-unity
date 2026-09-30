using System.Collections.Generic;
using UnityEngine;

namespace Pcb
{
    /// <summary>
    /// A gate on a trace: blocks the spark (both directions) while closed. A normal gate flips open/closed
    /// each time ANY of its switches is pressed. Link switches with Level Editor > Link tool. (Wiring a
    /// switch's onToggle to SetOpen by hand, as in Level 04, still works.)
    /// </summary>
    public class GateMechanic : TraceMechanic
    {
        [Tooltip("Normal gate: open at the start? Each press of any of its switches flips it.")]
        public bool isOpen = false;
        [Tooltip("The switches controlling this gate: normal switches for a normal gate, AND switches for an AND gate.")]
        public List<SwitchMechanic> switches = new List<SwitchMechanic>();
        public GameObject closedVisual;
        private GameObject autoVisual;

        protected virtual void OnEnable()
        {
            foreach (var s in switches) if (s) s.onToggle.AddListener(OnSwitchToggled);
        }

        protected virtual void OnDisable()
        {
            foreach (var s in switches) if (s) s.onToggle.RemoveListener(OnSwitchToggled);
        }

        /// <summary>Normal gate: any press of any of its switches flips it.</summary>
        protected virtual void OnSwitchToggled(bool _) => SetOpen(!isOpen);

        public void SetOpen(bool open)
        {
            isOpen = open;
            Debug.Log($"Gate {gameObject.name} set to {(isOpen ? "Open" : "Closed")}");
            UpdateVisual();
        }

        public override bool CanEnter(Spark spark, bool reversed)
        {
            if (!isOpen) Debug.Log($"Spark blocked by closed gate on {gameObject.name}");
            return isOpen;
        }

        void Start()
        {
            var trace = GetComponent<Trace>();
            var board = GetComponentInParent<Board>();

            if (closedVisual == null)
            {
                if (board && board.theme && board.theme.gatePrefab)
                {
                    autoVisual = Instantiate(board.theme.gatePrefab, transform);
                }
                else
                {
                    autoVisual = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    autoVisual.name = "AutoGateVisual";
                    autoVisual.transform.SetParent(transform, false);
                    autoVisual.transform.localScale = new Vector3(0.2f, 0.2f, 0.2f);

                    var rend = autoVisual.GetComponent<Renderer>();
                    if (rend) rend.material.color = Color.red;
                }
                closedVisual = autoVisual;
            }

            if (closedVisual && trace && trace.from && trace.to && board)
            {
                // Find 2D local midpoint
                Vector2 fromPos = board.NodePosition(trace.from);
                Vector2 toPos = board.NodePosition(trace.to);
                Vector2 midLocal = Vector2.Lerp(fromPos, toPos, 0.5f);

                // Snap to correct side surface + lift it a bit above the trace
                float height = (board.theme ? board.theme.traceHeight : 0.025f) + 0.05f;
                closedVisual.transform.position = board.SurfaceToWorld(midLocal, trace.layer, height);

                // Align rotation to the trace direction and flip if on the back
                Vector2 d = toPos - fromPos;
                var flip = trace.layer == PcbLayer.Back ? Quaternion.Euler(180f, 0f, 0f) : Quaternion.identity;
                closedVisual.transform.rotation = board.transform.rotation * Quaternion.Euler(0f, 0f, Mathf.Atan2(d.y, d.x) * Mathf.Rad2Deg) * flip;
            }

            UpdateVisual();
        }

        void UpdateVisual()
        {
            if (closedVisual)
            {
                closedVisual.SetActive(!isOpen);
            }
        }
    }
}

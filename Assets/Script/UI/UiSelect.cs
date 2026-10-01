using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Pcb
{
    /// <summary>Keyboard / gamepad menu navigation: something has to be selected when a menu opens.</summary>
    public static class UiSelect
    {
        /// <summary>Selects the first visible, interactable button / slider under 'root' (in hierarchy order).</summary>
        public static void First(GameObject root)
        {
            if (!root || !EventSystem.current) return;
            foreach (var s in root.GetComponentsInChildren<Selectable>()) // active objects only
                if (s.IsActive() && s.IsInteractable())
                {
                    Select(s.gameObject);
                    return;
                }
        }

        public static void Select(GameObject target)
        {
            if (EventSystem.current) EventSystem.current.SetSelectedGameObject(target);
        }

        public static void Clear() => Select(null);
    }
}

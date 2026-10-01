using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace Pcb
{
    /// <summary>
    /// Lives in the MainMenu scene. Builds one button per level from the LevelList, in play order,
    /// so this never needs manual upkeep as levels are added, removed or reordered.
    /// </summary>
    public class StageSelectController : MonoBehaviour
    {
        [Tooltip("Same Level List the game plays from.")]
        public LevelList levels;
        [Tooltip("Scene that contains the LevelManager / gameplay.")]
        public string gameplayScene = "SampleScene";

        [Header("Wiring")]
        public GameObject panel;
        public GameObject mainMenuPanel;
        [Tooltip("Parent the generated stage buttons are placed under.")]
        public Transform buttonContainer;
        [Tooltip("Inactive button under buttonContainer, cloned once per level.")]
        public Button buttonTemplate;
        [Tooltip("Optional. The scroll view around the buttons (found automatically if empty).")]
        public ScrollRect scrollRect;
        [Tooltip("Label colour on dark buttons (light buttons keep the template's text colour).")]
        public Color lightTextColour = Color.white;
        [Tooltip("When the panel opens: wait this long at the top of the list, then scroll down to the furthest unlocked stage.")]
        [Min(0f)] public float autoScrollDelay = 0.3f;
        [Tooltip("Seconds that scroll takes (0 = jump straight there).")]
        [Min(0f)] public float autoScrollTime = 0.8f;

        Button furthestButton;   // the furthest unlocked stage (selected once the auto-scroll ends)
        Coroutine autoScroll;
        GameObject lastSelected;

        void OnEnable()
        {
            FixScrolling();
            Populate();
            ScrollToTop();
            autoScroll = StartCoroutine(ScrollToFurthest());
        }

        void OnDisable()
        {
            if (autoScroll != null) StopCoroutine(autoScroll);
            autoScroll = null;
        }

        /// <summary>Starts at stage 1, then glides down to the furthest unlocked stage and selects it.</summary>
        IEnumerator ScrollToFurthest()
        {
            if (furthestButton) UiSelect.Select(null); // nothing highlighted while it glides
            float wait = autoScrollDelay;
            while (wait > 0f)
            {
                if (PlayerInterrupted()) { EndAutoScroll(); yield break; }
                wait -= Time.unscaledDeltaTime;
                yield return null;
            }
            if (scrollRect && furthestButton)
            {
                float from = scrollRect.verticalNormalizedPosition;
                float to = NormalizedPositionFor((RectTransform)furthestButton.transform);
                for (float t = 0f; t < 1f; )
                {
                    if (PlayerInterrupted()) { EndAutoScroll(); yield break; }
                    t = autoScrollTime > 0f ? Mathf.Min(1f, t + Time.unscaledDeltaTime / autoScrollTime) : 1f;
                    scrollRect.verticalNormalizedPosition = Mathf.Lerp(from, to, Mathf.SmoothStep(0f, 1f, t));
                    yield return null;
                }
            }
            EndAutoScroll();
        }

        /// <summary>Selects the furthest stage (Enter / South plays it; arrows navigate from there).</summary>
        void EndAutoScroll()
        {
            autoScroll = null;
            var target = furthestButton ? furthestButton.gameObject : null;
            if (target) UiSelect.Select(target);
            lastSelected = target; // already where the scroll left it: don't re-centre
        }

        /// <summary>A mouse click / wheel or a navigation key while it glides: hand control back to the player.</summary>
        static bool PlayerInterrupted()
        {
            var mouse = Mouse.current;
            if (mouse != null && (mouse.leftButton.wasPressedThisFrame || mouse.scroll.ReadValue().y != 0f)) return true;
            var keyboard = Keyboard.current;
            if (keyboard != null && (keyboard.upArrowKey.wasPressedThisFrame || keyboard.downArrowKey.wasPressedThisFrame ||
                                     keyboard.wKey.wasPressedThisFrame || keyboard.sKey.wasPressedThisFrame)) return true;
            var pad = Gamepad.current;
            return pad != null && (pad.dpad.up.wasPressedThisFrame || pad.dpad.down.wasPressedThisFrame ||
                                   pad.leftStick.ReadValue().sqrMagnitude > 0.25f);
        }

        /// <summary>Keyboard / gamepad: keep the selected stage button in view.</summary>
        void Update()
        {
            if (autoScroll != null || !scrollRect || !EventSystem.current) return;
            var selected = EventSystem.current.currentSelectedGameObject;
            if (selected == lastSelected) return;
            lastSelected = selected;
            if (!selected || selected.transform.parent != buttonContainer) return;
            var item = (RectTransform)selected.transform;
            if (!IsFullyVisible(item)) scrollRect.verticalNormalizedPosition = NormalizedPositionFor(item);
        }

        /// <summary>The scroll position (1 = top) that puts this button in the middle of the view.</summary>
        float NormalizedPositionFor(RectTransform item)
        {
            var content = (RectTransform)buttonContainer;
            LayoutRebuilder.ForceRebuildLayoutImmediate(content);
            var viewport = scrollRect.viewport ? scrollRect.viewport : (RectTransform)scrollRect.transform;
            float scrollable = content.rect.height - viewport.rect.height;
            if (scrollable <= 0f) return 1f;
            Vector3 centre = content.InverseTransformPoint(item.TransformPoint(item.rect.center));
            float fromTop = content.rect.yMax - centre.y;
            return 1f - Mathf.Clamp01((fromTop - viewport.rect.height * 0.5f) / scrollable);
        }

        bool IsFullyVisible(RectTransform item)
        {
            var viewport = scrollRect.viewport ? scrollRect.viewport : (RectTransform)scrollRect.transform;
            var v = new Vector3[4];
            var c = new Vector3[4];
            viewport.GetWorldCorners(v);
            item.GetWorldCorners(c);
            return c[0].y >= v[0].y - 0.5f && c[1].y <= v[1].y + 0.5f;
        }

        /// <summary>
        /// The list stops at both ends (instead of scrolling forever into blank space), grows with its buttons so the
        /// scroll view knows its height, and starts at the top of the view.
        /// </summary>
        void FixScrolling()
        {
            if (!buttonContainer) return;
            if (!scrollRect) scrollRect = buttonContainer.GetComponentInParent<ScrollRect>(true);
            if (scrollRect) scrollRect.movementType = ScrollRect.MovementType.Clamped;
            if (buttonContainer.TryGetComponent(out ContentSizeFitter fitter))
                fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            var rect = (RectTransform)buttonContainer;
            rect.pivot = new Vector2(rect.pivot.x, 1f);
            rect.anchoredPosition = new Vector2(rect.anchoredPosition.x, 0f);
        }

        void ScrollToTop()
        {
            if (!scrollRect || !buttonContainer) return;
            LayoutRebuilder.ForceRebuildLayoutImmediate((RectTransform)buttonContainer);
            scrollRect.verticalNormalizedPosition = 1f;
            scrollRect.velocity = Vector2.zero;
        }

        void Populate()
        {
            if (!buttonContainer || !buttonTemplate || !levels) return;
            furthestButton = null;

            for (int i = buttonContainer.childCount - 1; i >= 0; i--)
            {
                var child = buttonContainer.GetChild(i);
                if (child != buttonTemplate.transform) Destroy(child.gameObject);
            }
            buttonTemplate.gameObject.SetActive(false);

            // Only unlocked stages are listed (finishing a stage unlocks the next - see Progress).
            for (int i = 0; i < levels.Count && Progress.IsUnlocked(i); i++)
            {
                var level = levels[i];
                var button = Instantiate(buttonTemplate, buttonContainer);
                button.gameObject.SetActive(true);
                furthestButton = button; // the loop ends on the furthest unlocked stage

                var label = button.GetComponentInChildren<TMP_Text>();
                if (label)
                {
                    label.text = Label(i, level);
                    label.enableAutoSizing = true; // long console names shrink instead of spilling out
                    label.fontSizeMax = label.fontSize;
                    label.fontSizeMin = Mathf.Min(label.fontSizeMin, label.fontSize * 0.5f);
                }
                Colour(button, label, level);

                int index = i; // capture for the closure
                button.onClick.AddListener(() => Play(index));
                AudioManager.HookButton(button); // click sound (created after the scene loaded)
            }
        }

        /// <summary>Always two lines: "Console:" then "Level N" (level names are "Console: Level N").</summary>
        string Label(int index, Board level)
        {
            if (levels.IsBonus(index)) return $"Bonus:\nLevel {levels.BonusNumber(index)}";
            if (!level) return $"Level {index + 1}";
            string name = level.levelName;
            int colon = name.IndexOf(':');
            return colon >= 0 ? name.Substring(0, colon + 1) + "\n" + name.Substring(colon + 1).Trim() : name;
        }

        /// <summary>The button takes its level's board colour (theme Board Tile Colours); white text on dark colours.</summary>
        void Colour(Button button, TMP_Text label, Board level)
        {
            if (!level || !level.theme || !level.theme.TryGetTileColour(level.BoardTileModel, out var colour)) return;
            var c = button.colors;
            c.normalColor = colour;
            c.selectedColor = colour;
            c.highlightedColor = Color.Lerp(colour, Color.white, 0.3f);
            c.pressedColor = Color.Lerp(colour, Color.black, 0.3f);
            button.colors = c;
            float luminance = 0.299f * colour.r + 0.587f * colour.g + 0.114f * colour.b;
            if (label && luminance < 0.5f) label.color = lightTextColour;
        }

        void Play(int index)
        {
            AudioManager.Play(Sfx.StartGame);
            GameFlow.RequestLevel(index);
            ScreenFader.LoadScene(gameplayScene);
        }

        public void Back()
        {
            if (panel) panel.SetActive(false);
            if (mainMenuPanel) mainMenuPanel.SetActive(true);
            UiSelect.First(mainMenuPanel);
        }
    }
}

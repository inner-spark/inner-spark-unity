using TMPro;
using UnityEngine;
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

        void OnEnable()
        {
            FixScrolling();
            Populate();
            ScrollToTop();
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
                if (i == 0) UiSelect.Select(button.gameObject); // keyboard / gamepad navigation starts on stage 1

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

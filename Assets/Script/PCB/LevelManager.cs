using UnityEngine;
using UnityEngine.InputSystem;

namespace Pcb
{
    /// <summary>
    /// One per scene. Plays the levels from the LevelList: spawns the board and the spark,
    /// detects the Goal, and handles restart and the win pop-up.
    /// If a Board is already in the scene (the one you are editing), play starts on it.
    /// </summary>
    public class LevelManager : MonoBehaviour
    {
        public LevelList levels;
        [Tooltip("Level to start on when the scene has no Board in it.")]
        public int startLevel;
        [Tooltip("Optional. If empty, a default spark is created.")]
        public Spark sparkPrefab;
        [Tooltip("Optional. Esc opens Resume / Quit to Menu / Quit App through this instead of quitting straight to desktop.")]
        public PauseMenu pauseMenu;
        [Tooltip("Optional. Shown before play if the current level has a DialogSequence assigned.")]
        public DialogController dialogController;
        [Tooltip("Optional. Shown when the current level is won.")]
        public WinPanel winPanel;

        GameObject template; // what Restart re-creates: a level prefab, or the disabled scene board
        int index = -1;
        Board current;
        BoardRig rig;
        Spark spark;
        bool won;
        float wonAt;
        InputAction restartAction, confirmAction;

        public Board CurrentBoard => current;

        void Awake()
        {
            restartAction = Button("<Keyboard>/r", "<Gamepad>/select");
            confirmAction = Button("<Keyboard>/space", "<Keyboard>/enter", "<Gamepad>/buttonSouth");
        }

        static InputAction Button(params string[] bindings)
        {
            var action = new InputAction(type: InputActionType.Button);
            foreach (var b in bindings) action.AddBinding(b);
            return action;
        }

        void OnEnable() { restartAction.Enable(); confirmAction.Enable(); }
        void OnDisable() { restartAction.Disable(); confirmAction.Disable(); }
        void OnDestroy() { restartAction.Dispose(); confirmAction.Dispose(); }

        void Start()
        {
            var allSceneBoards = FindObjectsByType<Board>(FindObjectsInactive.Exclude, FindObjectsSortMode.None);
            foreach (var b in allSceneBoards) b.gameObject.SetActive(false);
            
            var sceneBoard = allSceneBoards.Length > 0 ? allSceneBoards[0] : null;
            bool levelsAvailable = levels && levels.Count > 0;

            // Arrived via Main Menu / Stage Select: that choice always wins, even if a Board happens
            // to be sitting in this scene for editing - otherwise testing through the menu in the
            // Editor would silently ignore Stage Select and just play whatever's in the scene.
            if (levelsAvailable && GameFlow.HasPendingRequest)
            {
                GoTo(GameFlow.TakeRequestedLevel(startLevel));
            }
            else if (sceneBoard && (Application.isEditor || !levelsAvailable))
            {
                // Editor: play the board being edited, keeping an untouched copy for restarts.
                template = sceneBoard.gameObject;
                index = levels ? levels.IndexOf(sceneBoard.levelName) : -1;
                Spawn(showDialog: true);
            }
            else if (levelsAvailable)
            {
                GoTo(GameFlow.TakeRequestedLevel(startLevel));
            }
            else Debug.LogError("[PCB] No Board in the scene and no levels in the Level List.", this);
        }

        public void GoTo(int levelIndex)
        {
            if (!levels || levels.Count == 0) return;
            index = (levelIndex % levels.Count + levels.Count) % levels.Count;
            template = levels[index] ? levels[index].gameObject : null;
            Spawn(showDialog: true);
        }

        public void Next() => GoTo(index + 1); // advances after a win; see OnArrived/Update
        public void Restart() => Spawn(showDialog: false); // replaying a level you've already seen the intro for

        void Spawn(bool showDialog)
        {
            if (!template) { Debug.LogError($"[PCB] Level {index + 1} is missing from the Level List.", this); return; }
            if (spark)
            {
                spark.Arrived -= OnArrived;
                spark.WinFinished -= OnWinFinished;
            }
            if (rig) Destroy(rig.gameObject); // takes the board and the spark with it
            won = false;
            if (winPanel) winPanel.Hide();

            var go = Instantiate(template);
            go.name = template.name;
            go.SetActive(true); // Board.Awake builds the graph and the 3D look
            current = go.GetComponent<Board>();
            rig = BoardRig.Create(current, Camera.main);

            PcbNode start = null;
            foreach (var n in current.Nodes)
                if (n.type == NodeType.Start) { start = n; break; }
            if (!start)
            {
                Debug.LogError($"[PCB] Level '{current.levelName}' has no Start node.", this);
                return;
            }

            spark = sparkPrefab ? Instantiate(sparkPrefab) : new GameObject("Spark").AddComponent<Spark>();
            spark.Init(current, start, rig);
            spark.Arrived += OnArrived;
            spark.WinFinished += OnWinFinished;

            if (showDialog && current.dialogSequence && dialogController)
            {
                spark.InputLocked = true;
                dialogController.Show(current.dialogSequence, () => { if (spark) spark.InputLocked = false; });
            }
        }

        void OnArrived(PcbNode node)
        {
            if (node.type != NodeType.Goal || current.GoalLocked) return; // locked goal: data still to collect
            spark.InputLocked = true; // no more input; the win screen waits for the spark's win animation (OnWinFinished)
        }

        void OnWinFinished()
        {
            won = true;
            wonAt = Time.time;
            if (winPanel) winPanel.Show(); // input is already locked since the goal (OnArrived)
        }

        void Update()
        {
            if (pauseMenu && pauseMenu.IsPaused) return;
            if (dialogController && dialogController.IsShowing) return;

            if (restartAction.WasPressedThisFrame()) Restart();
            else if (won && Time.time - wonAt > 0.4f && confirmAction.WasPressedThisFrame()) Next();
        }
        // No on-screen text during play: controls are taught in each stage's intro dialog.
    }
}

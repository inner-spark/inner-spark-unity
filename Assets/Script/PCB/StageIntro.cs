using System.Collections;
using UnityEngine;
using UnityEngine.Playables;

namespace Pcb
{
    /// <summary>
    /// Root of a stage's intro cinematic prefab (assigned on the Board's Intro field). The LevelManager places it
    /// at the centre of the board, lined up with it, while the screen is black, so the device is already there
    /// when the screen fades in. Two ways to play it:
    /// - With a Timeline (Director): plays it, moving the real camera along Camera Pose, blends the camera into
    ///   the gameplay view. Build the device around the prefab's origin (= the board's centre) and fade its
    ///   casing with a FadeGroup animated in the Timeline.
    /// - Without one (zoom and reveal): the Casing (a console model) is fitted around the board so it hides the
    ///   stage, the camera starts Start Distance times further out, glides in to the gameplay view, then the
    ///   casing fades away.
    /// Either way the prefab removes itself; then Sparky appears and the stage dialog plays.
    /// </summary>
    public class StageIntro : MonoBehaviour
    {
        [Tooltip("The Timeline to play. Its Play On Awake is ignored: the level starts it after the fade-in.")]
        public PlayableDirector director;
        [Tooltip("Animate this object's position/rotation in the Timeline: the game camera follows it during the intro.")]
        public Transform cameraPose;
        [Tooltip("Camera field of view during the intro (animatable). 0 = leave the camera's as it is.")]
        public float fieldOfView = 35f;
        [Tooltip("Seconds to blend from the Timeline's last camera pose into the normal gameplay view.")]
        [Min(0f)] public float blendToGameplay = 0.6f;

        [Header("Zoom and reveal (used when there's no Director)")]
        [Tooltip("The console model around the board; faded away at the end.")]
        public FadeGroup casing;
        [Tooltip("Scale and centre the casing so it wraps around the board (each stage's board has its own size).")]
        public bool fitCasingToBoard = true;
        [Tooltip("The part of the casing that must wrap around the board (the console body). Empty = its biggest part, " +
                 "so extras like a controller or joystick beside it don't count.")]
        public Renderer fitTo;
        [Tooltip("How much bigger than the board the casing's outline is (1.12 = 12 % bigger). Raise it if the " +
                 "console looks too small around the board.")]
        [Min(1f)] public float casingMargin = 1.12f;
        [Tooltip("How far the casing's top sits in front of the board's front face (it must hide the nodes).")]
        [Min(0f)] public float casingClearance = 0.7f;
        [Tooltip("After fitting, move the casing this far toward the gameplay camera (if nodes still poke through it).")]
        public float moveTowardCamera = 0f;
        [Tooltip("Camera start distance, as a multiple of the gameplay camera distance (shows the room).")]
        [Min(1f)] public float startDistance = 3f;
        [Tooltip("Seconds to hold the far view after the fade-in.")]
        [Min(0f)] public float holdTime = 0.6f;
        [Tooltip("Seconds to glide in to the gameplay view.")]
        [Min(0.01f)] public float zoomTime = 2.2f;
        [Tooltip("How far into the zoom the casing starts fading (0 = as the zoom starts, 0.5 = halfway).")]
        [Range(0f, 1f)] public float fadeStart = 0.5f;
        [Tooltip("Seconds for the casing to fade away (1.1 with a 2.2 s zoom from halfway = done as the camera arrives).")]
        [Min(0.01f)] public float fadeTime = 1.1f;

        Camera cam;
        BoardRig rig;
        Vector3 gamePosition, farPosition;
        Quaternion gameRotation;
        float savedFarClip;

        bool Timeline => director && director.playableAsset;

        void Awake()
        {
            if (!director) return;
            director.playOnAwake = false;
            director.extrapolationMode = DirectorWrapMode.None;
            director.Stop();
            director.time = 0;
            director.Evaluate(); // the first frame's pose while the screen fades in
        }

        /// <summary>Starts driving the camera (from the first frame of the Timeline) - call while the screen is black.</summary>
        public void Begin(Camera camera) => Begin(camera, null);

        /// <summary>
        /// Call while the screen is black, with the camera in the gameplay view (the rig just framed it).
        /// Timeline: follows Camera Pose. Zoom and reveal: fits the casing and moves the camera far out.
        /// </summary>
        public void Begin(Camera camera, BoardRig boardRig)
        {
            cam = camera;
            rig = boardRig;
            if (Timeline || !cam) { FollowPose(); return; }

            gamePosition = cam.transform.position;
            gameRotation = cam.transform.rotation;
            Vector3 centre = rig ? rig.transform.position : transform.position;

            var board = rig ? rig.GetComponentInChildren<Board>() : null;
            if (casing && fitCasingToBoard && board) FitCasing(board);
            if (casing)
            {
                casing.transform.position += (gamePosition - centre).normalized * moveTowardCamera;
                casing.alpha = 1f;
            }
            farPosition = centre + (gamePosition - centre) * startDistance;
            savedFarClip = cam.farClipPlane;
            cam.farClipPlane = Mathf.Max(cam.farClipPlane, Vector3.Distance(farPosition, centre) * 3f + 10f);
            cam.transform.SetPositionAndRotation(farPosition, gameRotation);
        }

        /// <summary>Scales / centres the casing around the board: outline Casing Margin x the board, top in front of it.</summary>
        void FitCasing(Board board)
        {
            var t = casing.transform;
            t.localScale = Vector3.one;
            t.localPosition = Vector3.zero;
            if (!TryGetBounds(out var b)) return;
            float margin = board.theme ? board.theme.boardMargin : 0.5f;
            Vector2 size = board.Size + Vector2.one * margin * 2f;
            float thickness = board.theme ? board.theme.boardThickness : 0.16f;
            // uniform scale for the outline (keeps the console's shape), its own scale for the depth
            float s = Mathf.Max(size.x * casingMargin / Mathf.Max(b.size.x, 1e-4f), size.y * casingMargin / Mathf.Max(b.size.y, 1e-4f));
            float depth = thickness + casingClearance * 2f;
            float sDepth = depth / Mathf.Max(b.size.z, 1e-4f);
            // the casing stands up out of the board face (−90° X): its own Y is the board's depth
            t.localScale = new Vector3(s, Mathf.Max(s, sDepth), s);
            if (!TryGetBounds(out b)) return;
            Vector3 boardCentre = board.transform.TransformPoint(new Vector3(board.Size.x * 0.5f, board.Size.y * 0.5f, thickness * 0.5f));
            t.position += boardCentre - b.center;
        }

        /// <summary>World bounds of the part the board must fit in: Fit To, else the casing's biggest part.</summary>
        bool TryGetBounds(out Bounds bounds)
        {
            bounds = default;
            var body = fitTo;
            if (!body)
            {
                float best = -1f;
                foreach (var r in casing.GetComponentsInChildren<Renderer>(true))
                {
                    var size = r.bounds.size;
                    float footprint = size.x * size.y; // its outline as seen from the camera
                    if (footprint > best) { best = footprint; body = r; }
                }
            }
            if (!body) return false;
            bounds = body.bounds;
            return true;
        }

        /// <summary>Plays the Timeline to the end, blends the camera into the gameplay view, then removes the intro.</summary>
        public IEnumerator Play(BoardRig rig)
        {
            if (!Timeline && cam)
            {
                yield return ZoomAndReveal(rig);
                yield break;
            }
            if (director && director.playableAsset)
            {
                director.Play();
                while (director.state == PlayState.Playing && director.time < director.duration) yield return null;
            }
            FollowPose();
            var from = cam ? cam.transform : null;
            cam = null; // stop following

            if (from && rig)
            {
                Vector3 p0 = from.position; Quaternion r0 = from.rotation; float f0 = from.GetComponent<Camera>().fieldOfView;
                var camera = from.GetComponent<Camera>();
                rig.Refit(); // puts the camera in the gameplay view: read it as the blend target
                Vector3 p1 = from.position; Quaternion r1 = from.rotation; float f1 = camera.fieldOfView;
                for (float t = 0f; t < blendToGameplay; t += Time.deltaTime)
                {
                    float k = Mathf.SmoothStep(0f, 1f, t / blendToGameplay);
                    from.SetPositionAndRotation(Vector3.Lerp(p0, p1, k), Quaternion.Slerp(r0, r1, k));
                    camera.fieldOfView = Mathf.Lerp(f0, f1, k);
                    yield return null;
                }
                rig.Refit();
            }
            Destroy(gameObject);
        }

        IEnumerator ZoomAndReveal(BoardRig boardRig)
        {
            for (float t = 0f; t < holdTime; t += Time.deltaTime) yield return null;
            // the camera glides in while the casing fades away
            float fadeDelay = fadeStart * zoomTime;
            float total = Mathf.Max(zoomTime, fadeDelay + fadeTime);
            for (float t = 0f; t < total; )
            {
                t = Mathf.Min(total, t + Time.deltaTime);
                float zoom = Mathf.Clamp01(t / zoomTime);
                cam.transform.position = Vector3.Lerp(farPosition, gamePosition, Mathf.SmoothStep(0f, 1f, zoom));
                if (casing) casing.alpha = 1f - Mathf.SmoothStep(0f, 1f, Mathf.Clamp01((t - fadeDelay) / fadeTime));
                yield return null;
            }
            cam.farClipPlane = savedFarClip;
            cam = null;
            if (boardRig) boardRig.Refit();
            Destroy(gameObject);
        }

        // After the Timeline has animated Camera Pose this frame.
        void LateUpdate() => FollowPose();

        void FollowPose()
        {
            if (!cam || !cameraPose) return;
            cam.transform.SetPositionAndRotation(cameraPose.position, cameraPose.rotation);
            if (fieldOfView > 0f) cam.fieldOfView = fieldOfView;
        }
    }
}

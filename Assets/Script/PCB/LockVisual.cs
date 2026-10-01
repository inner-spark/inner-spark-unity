using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace Pcb
{
    /// <summary>
    /// Optional, on the root of a goal model prefab with its Locked and Unlocked looks as two children.
    /// Without it, a locked goal is simply tinted gray (theme Locked Goal Tint).
    /// FadeTo() swaps with a fade (pass locks): the Locked look fades out over the Unlocked one, or back in.
    /// </summary>
    public class LockVisual : MonoBehaviour
    {
        [Tooltip("Child shown while the goal is locked (data still to collect).")]
        public GameObject locked;
        [Tooltip("Child shown once the goal is unlocked.")]
        public GameObject unlocked;
        [Tooltip("Seconds FadeTo() takes to fade the Locked look out / in.")]
        public float fadeTime = 0.4f;

        bool isLockedNow = true;
        Coroutine fading;
        Renderer[] fadeRenderers;
        Material[][] opaqueMaterials, fadeMaterials;
        ShadowCastingMode[] shadowModes;

        /// <summary>Instant swap.</summary>
        public void Show(bool isLocked)
        {
            StopFade();
            isLockedNow = isLocked;
            if (locked) locked.SetActive(isLocked);
            if (unlocked) unlocked.SetActive(!isLocked);
        }

        /// <summary>Fades the Locked look out (unlock) or back in (lock); instant outside play mode.</summary>
        public void FadeTo(bool isLocked)
        {
            if (isLocked == isLockedNow && fading == null) return;
            if (!Application.isPlaying || !isActiveAndEnabled || !locked || fadeTime <= 0f) { Show(isLocked); return; }
            StopFade();
            isLockedNow = isLocked;
            fading = StartCoroutine(Fade(isLocked));
        }

        IEnumerator Fade(bool toLocked)
        {
            // The Unlocked look sits underneath while the Locked one fades over it.
            if (unlocked) unlocked.SetActive(true);
            locked.SetActive(true);
            UseFadeMaterials(true);
            for (float t = 0f; t < 1f; )
            {
                t = Mathf.Min(1f, t + Time.deltaTime / fadeTime);
                float k = Mathf.SmoothStep(0f, 1f, t);
                SetAlpha(toLocked ? k : 1f - k);
                yield return null;
            }
            fading = null;
            UseFadeMaterials(false);
            locked.SetActive(toLocked);
            if (unlocked) unlocked.SetActive(!toLocked);
        }

        void StopFade()
        {
            if (fading == null) return;
            StopCoroutine(fading);
            fading = null;
            UseFadeMaterials(false);
        }

        void UseFadeMaterials(bool fade)
        {
            if (fadeRenderers == null)
            {
                fadeRenderers = locked.GetComponentsInChildren<Renderer>(true);
                opaqueMaterials = new Material[fadeRenderers.Length][];
                fadeMaterials = new Material[fadeRenderers.Length][];
                shadowModes = new ShadowCastingMode[fadeRenderers.Length];
                for (int i = 0; i < fadeRenderers.Length; i++)
                {
                    opaqueMaterials[i] = fadeRenderers[i].sharedMaterials;
                    shadowModes[i] = fadeRenderers[i].shadowCastingMode;
                    fadeMaterials[i] = new Material[opaqueMaterials[i].Length];
                    for (int j = 0; j < opaqueMaterials[i].Length; j++)
                        fadeMaterials[i][j] = opaqueMaterials[i][j] ? Transparent(opaqueMaterials[i][j]) : null;
                }
            }
            for (int i = 0; i < fadeRenderers.Length; i++)
            {
                if (!fadeRenderers[i]) continue;
                fadeRenderers[i].sharedMaterials = fade ? fadeMaterials[i] : opaqueMaterials[i];
                fadeRenderers[i].shadowCastingMode = shadowModes[i];
            }
        }

        void SetAlpha(float alpha)
        {
            for (int i = 0; i < fadeRenderers.Length; i++)
            {
                foreach (var m in fadeMaterials[i])
                {
                    if (!m || !m.HasProperty(BaseColor)) continue;
                    var c = m.GetColor(BaseColor);
                    c.a = alpha;
                    m.SetColor(BaseColor, c);
                }
                // A half-faded lock shouldn't keep casting a solid shadow.
                if (fadeRenderers[i]) fadeRenderers[i].shadowCastingMode = alpha > 0.5f ? shadowModes[i] : ShadowCastingMode.Off;
            }
        }

        static readonly int BaseColor = Shader.PropertyToID("_BaseColor");

        /// <summary>A transparent (alpha-blended) copy of a URP Lit / Simple Lit material.</summary>
        static Material Transparent(Material source)
        {
            var m = new Material(source) { name = source.name + " (Fade)", hideFlags = HideFlags.DontSave };
            m.SetFloat("_Surface", 1f);
            m.SetFloat("_Blend", 0f);
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
            m.SetFloat("_DstBlendAlpha", (float)BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_ZWrite", 0f);
            m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            m.DisableKeyword("_ALPHATEST_ON");
            m.SetOverrideTag("RenderType", "Transparent");
            m.renderQueue = (int)RenderQueue.Transparent;
            return m;
        }

        void OnDestroy()
        {
            if (fadeMaterials == null) return;
            foreach (var set in fadeMaterials)
                foreach (var m in set)
                    if (m) Destroy(m);
        }
    }
}

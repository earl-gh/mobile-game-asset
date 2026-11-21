// Enables the low-tier shader keyword for VStyle/Lit from the active Quality level.
// Attach once in the boot scene. Tiers change shader cost only, never gameplay visibility.
using UnityEngine;

public class VStyleQuality : MonoBehaviour
{
    [Tooltip("Quality level indices that use the low-instruction shader path.")]
    public int[] lowTierLevels = { 0 };

    int applied = -1;

    void Awake() { DontDestroyOnLoad(gameObject); Apply(); }
    void Update() { if (QualitySettings.GetQualityLevel() != applied) Apply(); }

    void Apply()
    {
        applied = QualitySettings.GetQualityLevel();
        bool low = System.Array.IndexOf(lowTierLevels, applied) >= 0;
        if (low) Shader.EnableKeyword("_VSTYLE_TIER_LOW"); else Shader.DisableKeyword("_VSTYLE_TIER_LOW");
    }
}

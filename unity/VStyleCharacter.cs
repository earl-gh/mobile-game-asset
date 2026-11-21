// Per-character readability setup for VStyle/Lit: team fresnel colour and ambient clamp per renderer,
// via MaterialPropertyBlock (no material copies, SRP-batcher friendly enough for a handful of agents).
// Also enforces the competitive-integrity rule: third-person characters never cast shadows.
using UnityEngine;
using UnityEngine.Rendering;

public class VStyleCharacter : MonoBehaviour
{
    public enum Team { Ally, Enemy }
    public Team team = Team.Enemy;
    public bool firstPerson = false;
    [ColorUsage(false, true)] public Color allyFresnel = new Color(0.55f, 0.7f, 1.0f);
    [ColorUsage(false, true)] public Color enemyFresnel = new Color(1.6f, 0.18f, 0.22f);
    [Range(0, 2)] public float ambientMin = 0.35f;
    [Range(0, 2)] public float ambientMax = 1.1f;

    static readonly int FresnelId = Shader.PropertyToID("_FresnelColor");
    static readonly int AmbMinId = Shader.PropertyToID("_AmbientMin");
    static readonly int AmbMaxId = Shader.PropertyToID("_AmbientMax");
    MaterialPropertyBlock block;

    void OnEnable() { Apply(); }
    void OnValidate() { Apply(); }

    public void SetTeam(Team t) { team = t; Apply(); }

    public void SetAmbientClamp(float min, float max) { ambientMin = min; ambientMax = max; Apply(); }

    void Apply()
    {
        block ??= new MaterialPropertyBlock();
        foreach (var r in GetComponentsInChildren<Renderer>(true))
        {
            r.GetPropertyBlock(block);
            block.SetColor(FresnelId, team == Team.Enemy ? enemyFresnel : allyFresnel);
            block.SetFloat(AmbMinId, ambientMin);
            block.SetFloat(AmbMaxId, ambientMax);
            r.SetPropertyBlock(block);
            r.shadowCastingMode = firstPerson ? ShadowCastingMode.On : ShadowCastingMode.Off;
        }
    }
}

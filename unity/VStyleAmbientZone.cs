// Trigger volume that sets the ambient clamp for characters inside it (Riot tunes max darkness and
// brightness per map area). Needs a trigger Collider on this object and a Rigidbody on characters.
using UnityEngine;

[RequireComponent(typeof(Collider))]
public class VStyleAmbientZone : MonoBehaviour
{
    [Range(0, 2)] public float ambientMin = 0.35f;
    [Range(0, 2)] public float ambientMax = 1.1f;

    void Reset() { GetComponent<Collider>().isTrigger = true; }

    void OnTriggerEnter(Collider other)
    {
        var c = other.GetComponentInParent<VStyleCharacter>();
        if (c) c.SetAmbientClamp(ambientMin, ambientMax);
    }
}

---
type: llm
focus: trace
weight: 1
---

Metallic, AO/emissive and roughness are packed into one T_<Asset>_MAER mask (R metallic, G AO below 0.5 and emissive above 0.5, B roughness, A tint zone) for the VStyle/Lit shader, and every glowing part from the request is encoded in the G emissive range rather than left unaccounted for

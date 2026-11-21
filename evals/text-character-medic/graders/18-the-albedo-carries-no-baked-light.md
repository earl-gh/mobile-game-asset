---
type: llm
focus: trace
weight: 1
---

The albedo carries material color only: no AO multiply, top-down gradient, painted form shadow, grime or noise is baked into it, core shadow is controlled by a gen_ramp.py diffuse ramp instead, and check_albedo.py (or an equivalent check) is run on the result

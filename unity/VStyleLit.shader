// VStyle/Lit — Valorant-style forward shader for URP (Unity 6+), built from the techniques in
// Riot's "VALORANT Shaders and Gameplay Clarity". See references/shader.md for the reasoning.
//
// Lighting model
//   Diffuse   : one main light, N·L remapped to 0..1 and looked up in an artist ramp (Gradient Lambert).
//               Weapons use a smoothstep instead (_CATEGORY_WEAPON). Environment uses baked lightmaps.
//   Specular  : environment cubemap only (reflection probe / skybox), roughness -> mip. Specular strength
//               = 1 - roughness, colour = lerp(0.04, albedo, metallic). No analytic light highlights.
//   Ambient   : light-probe SH luminance, clamped to [_AmbientMin, _AmbientMax]; scales diffuse and
//               specular separately (specular darkens more in dark areas).
//   Character : team fresnel (up-biased, upper body), skin underglow (vertex colour R mask),
//               distance brightening + wider fresnel with depth, all clamped.
//   MAER mask : R metallic | G AO (<0.5) or emissive (>0.5) | B roughness | A tint-zone ID.
//
// Tiers: the global keyword _VSTYLE_TIER_LOW (set by VStyleQuality.cs) removes instructions, never
// gameplay features: characters drop specular, weapons drop diffuse, environment keeps one of the two.
// Fresnel, emissive, depth brightening and ambient clamp exist on every tier.
//
// NOTE: written against the URP 17 (Unity 6) ShaderLibrary API. Compile it in your project and check
// Inspector > Compiled code > instruction counts per tier before shipping.

Shader "VStyle/Lit"
{
    Properties
    {
        [KeywordEnum(Character, Weapon, Environment, Prop)] _Category ("Category", Float) = 0
        [MainTexture] _BaseMap ("Albedo (T_*_A)", 2D) = "white" {}
        [MainColor] _BaseColor ("Tint", Color) = (1,1,1,1)
        [NoScaleOffset] _MaerMap ("MAER mask (T_*_MAER, linear)", 2D) = "white" {}
        [NoScaleOffset][Normal] _BumpMap ("Normal (T_*_N)", 2D) = "bump" {}
        _BumpScale ("Normal strength", Range(0, 2)) = 1

        [Header(Diffuse)]
        [NoScaleOffset] _DiffuseRamp ("Diffuse ramp (T_*_RampDiffuse)", 2D) = "white" {}
        _WeaponSmoothLo ("Weapon smoothstep low", Range(-1, 1)) = -0.2
        _WeaponSmoothHi ("Weapon smoothstep high", Range(-1, 1)) = 0.6
        _WeaponShadowFloor ("Weapon shadow floor", Range(0, 1)) = 0.45

        [Header(Specular)]
        _SpecularStrength ("Specular strength", Range(0, 2)) = 1

        [Header(Ambient clamp)]
        _AmbientMin ("Ambient min", Range(0, 2)) = 0.35
        _AmbientMax ("Ambient max", Range(0, 2)) = 1.1
        _AmbientSpecDarken ("Specular darkening in shade", Range(0, 2)) = 1.5

        [Header(Emission)]
        [HDR] _EmissionColor ("Emission colour (x albedo)", Color) = (2,2,2,1)

        [Header(Character)]
        [HDR] _FresnelColor ("Team fresnel colour (set per renderer)", Color) = (0.55,0.7,1,1)
        _FresnelPower ("Fresnel power (near)", Range(0.5, 8)) = 4
        _FresnelPowerFar ("Fresnel power (far)", Range(0.5, 8)) = 2
        _FresnelUpBias ("Fresnel up-facing bias", Range(0, 4)) = 1.5
        _FresnelHeight ("Character height (m), fresnel stronger on upper body", Float) = 1.8
        _DepthStart ("Depth adjust start (m)", Float) = 8
        _DepthEnd ("Depth adjust end (m)", Float) = 40
        _DepthBrighten ("Max distance brightening", Range(0, 1)) = 0.25
        [NoScaleOffset] _SkinRamp ("Skin diffuse ramp (warmer core shadow)", 2D) = "white" {}
        [HDR] _UnderglowColor ("Skin underglow", Color) = (0.5,0.12,0.08,1)

        [Header(Tint zones)]
        _ZoneTint1 ("Zone 1 tint (A = 0.25)", Color) = (1,1,1,1)
        _ZoneTint2 ("Zone 2 tint (A = 0.5)", Color) = (1,1,1,1)
        _ZoneTint3 ("Zone 3 tint (A = 0.75)", Color) = (1,1,1,1)

        [Header(Environment low tier)]
        [Toggle] _EnvLowKeepSpecular ("Low tier keeps specular instead of diffuse", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" "Queue"="Geometry" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex vert
            #pragma fragment frag
            #pragma shader_feature_local _CATEGORY_CHARACTER _CATEGORY_WEAPON _CATEGORY_ENVIRONMENT _CATEGORY_PROP
            #pragma multi_compile _ _VSTYLE_TIER_LOW
            #pragma multi_compile _ LIGHTMAP_ON
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap);      SAMPLER(sampler_BaseMap);
            TEXTURE2D(_MaerMap);      SAMPLER(sampler_MaerMap);
            TEXTURE2D(_BumpMap);      SAMPLER(sampler_BumpMap);
            TEXTURE2D(_DiffuseRamp);  SAMPLER(sampler_DiffuseRamp);
            TEXTURE2D(_SkinRamp);     SAMPLER(sampler_SkinRamp);

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _BaseColor;
                half _BumpScale;
                half _WeaponSmoothLo, _WeaponSmoothHi, _WeaponShadowFloor;
                half _SpecularStrength;
                half _AmbientMin, _AmbientMax, _AmbientSpecDarken;
                half4 _EmissionColor;
                half4 _FresnelColor;
                half _FresnelPower, _FresnelPowerFar, _FresnelUpBias, _FresnelHeight;
                float _DepthStart, _DepthEnd;
                half _DepthBrighten;
                half4 _UnderglowColor;
                half4 _ZoneTint1, _ZoneTint2, _ZoneTint3;
                half _EnvLowKeepSpecular;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                float4 tangentOS  : TANGENT;
                float2 uv         : TEXCOORD0;
                float2 uvLightmap : TEXCOORD1;
                half4  color      : COLOR;      // R = skin mask (characters)
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv         : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3  normalWS   : TEXCOORD2;
                half4  tangentWS  : TEXCOORD3;
                half   heightT    : TEXCOORD4;  // 0 at feet, 1 at head (object space)
                half   skin       : TEXCOORD5;
                float2 uvLightmap : TEXCOORD6;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings vert (Attributes v)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_TRANSFER_INSTANCE_ID(v, o);
                VertexPositionInputs p = GetVertexPositionInputs(v.positionOS.xyz);
                VertexNormalInputs n = GetVertexNormalInputs(v.normalOS, v.tangentOS);
                o.positionCS = p.positionCS;
                o.positionWS = p.positionWS;
                o.normalWS = n.normalWS;
                o.tangentWS = half4(n.tangentWS, v.tangentOS.w * GetOddNegativeScale());
                o.uv = TRANSFORM_TEX(v.uv, _BaseMap);
                o.heightT = saturate(v.positionOS.y / max(_FresnelHeight, 0.01));
                o.skin = v.color.r;
                o.uvLightmap = v.uvLightmap * unity_LightmapST.xy + unity_LightmapST.zw;
                return o;
            }

            half3 ApplyZoneTint(half3 albedo, half zone)
            {
                // A channel: 0 = untinted, 0.25 / 0.5 / 0.75 = tint zones 1-3 (skins recolour without new albedos)
                half3 t = 1;
                t = lerp(t, _ZoneTint1.rgb, step(0.125, zone) * step(zone, 0.375));
                t = lerp(t, _ZoneTint2.rgb, step(0.375, zone) * step(zone, 0.625));
                t = lerp(t, _ZoneTint3.rgb, step(0.625, zone) * step(zone, 0.875));
                return albedo * t;
            }

            half4 frag (Varyings i) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                half4 albedoTex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv) * _BaseColor;
                half4 maer = SAMPLE_TEXTURE2D(_MaerMap, sampler_MaerMap, i.uv);
                half metallic = maer.r;
                half ao = saturate(maer.g * 2.0);              // G < 0.5 : AO   (0.5 = unoccluded)
                half emissive = saturate(maer.g * 2.0 - 1.0);  // G > 0.5 : emissive mask
                half roughness = maer.b;
                half3 albedo = ApplyZoneTint(albedoTex.rgb, maer.a);

                half3 nTS = UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, i.uv), _BumpScale);
                half3 bitangent = i.tangentWS.w * cross(i.normalWS, i.tangentWS.xyz);
                half3 N = normalize(TransformTangentToWorld(nTS, half3x3(i.tangentWS.xyz, bitangent, i.normalWS)));
                half3 V = GetWorldSpaceNormalizeViewDir(i.positionWS);
                Light mainLight = GetMainLight();
                half NdotL = dot(N, mainLight.direction);

                // ---------- ambient clamp (probe luminance -> separate diffuse / specular scales) ----------
                half3 sh = SampleSH(N);
                half amb = clamp(Luminance(sh), _AmbientMin, _AmbientMax);
                half ambDiffuse = amb;
                half ambSpec = saturate(pow(amb / max(_AmbientMax, 1e-3), _AmbientSpecDarken));

                // ---------- diffuse ----------
                half3 diffuseLight;
                #if defined(_CATEGORY_ENVIRONMENT) && defined(LIGHTMAP_ON)
                    diffuseLight = SampleLightmap(i.uvLightmap, float2(0, 0), N);   // offline, many lights
                #elif defined(_CATEGORY_WEAPON)
                    half w = smoothstep(_WeaponSmoothLo, _WeaponSmoothHi, NdotL);
                    diffuseLight = lerp(_WeaponShadowFloor, 1.0, w) * mainLight.color * ambDiffuse;
                #else
                    half rampU = NdotL * 0.5 + 0.5;                                  // remap N·L to 0..1
                    half3 ramp = SAMPLE_TEXTURE2D(_DiffuseRamp, sampler_DiffuseRamp, half2(rampU, 0.5)).rgb;
                    #if defined(_CATEGORY_CHARACTER)
                        half3 skinRamp = SAMPLE_TEXTURE2D(_SkinRamp, sampler_SkinRamp, half2(rampU, 0.5)).rgb;
                        ramp = lerp(ramp, skinRamp, i.skin);
                    #endif
                    diffuseLight = ramp * mainLight.color * ambDiffuse;
                #endif
                half3 diffuse = albedo * (1.0 - metallic) * diffuseLight * ao;

                // ---------- specular: cubemap only, painted hotspots live in the probe/sky ----------
                half3 R = reflect(-V, N);
                half3 specColor = lerp(half3(0.04, 0.04, 0.04), albedo, metallic);
                half3 env = GlossyEnvironmentReflection(R, i.positionWS, roughness, ao);
                half3 specular = env * specColor * (1.0 - roughness) * _SpecularStrength * ambSpec;

                // ---------- tier scaling: drop instructions, keep gameplay ----------
                #if defined(_VSTYLE_TIER_LOW)
                    #if defined(_CATEGORY_CHARACTER)
                        specular = 0;                         // characters don't need to be shiny to read
                    #elif defined(_CATEGORY_WEAPON)
                        diffuse = albedo * (1.0 - metallic) * ambDiffuse * ao * 0.6;  // weapons keep specular
                    #else
                        if (_EnvLowKeepSpecular > 0.5) diffuse = albedo * ambDiffuse * 0.6; else specular = 0;
                    #endif
                #endif

                half3 color = diffuse + specular;

                // ---------- character readability (every tier) ----------
                #if defined(_CATEGORY_CHARACTER)
                    float dist = distance(GetCameraPositionWS(), i.positionWS);
                    half depthT = saturate((dist - _DepthStart) / max(_DepthEnd - _DepthStart, 1e-3));
                    half NdotV = saturate(dot(N, V));
                    half up = pow(saturate(N.y * 0.5 + 0.5), _FresnelUpBias);
                    half rim = pow(1.0 - NdotV, lerp(_FresnelPower, _FresnelPowerFar, depthT)) * up;
                    rim *= lerp(0.35, 1.0, i.heightT);                          // stronger on the upper body
                    half shade = 1.0 - saturate(NdotL * 0.5 + 0.5);
                    half3 underglow = _UnderglowColor.rgb * i.skin * shade * (0.5 + 0.5 * (1.0 - NdotV));
                    color = color * (1.0 + _DepthBrighten * depthT) + underglow + _FresnelColor.rgb * rim;
                #endif

                color += albedo * emissive * _EmissionColor.rgb;
                return half4(color, 1);
            }
            ENDHLSL
        }

        // Shadow caster kept for first-person meshes only. Third-person characters and play-space
        // objects must have Cast Shadows = Off on the renderer (competitive integrity, see shader.md).
        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
        UsePass "Universal Render Pipeline/Lit/DepthOnly"
        UsePass "Universal Render Pipeline/Lit/DepthNormals"
        UsePass "Universal Render Pipeline/Lit/Meta"
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}

---
title: "PBR: Physically Based Rendering от Cook-Torrance до Disney"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/lighting
  - type/deep-dive
  - level/advanced
related:
  - "[[lighting-models-lambert-phong-blinn]]"
  - "[[image-based-lighting-ibl]]"
  - "[[filament-architecture-deep]]"
  - "[[vectors-in-3d-graphics]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[lighting-models-lambert-phong-blinn]]"
primary_sources:
  - url: "https://blog.selfshadow.com/publications/s2012-shading-course/burley/s2012_pbs_disney_brdf_notes_v3.pdf"
    title: "Burley, B. (2012). Physically Based Shading at Disney. SIGGRAPH"
    accessed: 2026-04-20
  - url: "https://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf"
    title: "Karis, B. (2013). Real Shading in Unreal Engine 4. SIGGRAPH"
    accessed: 2026-04-20
  - url: "https://dl.acm.org/doi/10.1145/357290.357293"
    title: "Cook, R. & Torrance, K. (1982). A Reflectance Model for Computer Graphics. TOG"
    accessed: 2026-04-20
  - url: "https://google.github.io/filament/Filament.md.html"
    title: "Google Filament: PBR documentation"
    accessed: 2026-04-20
reading_time: 25
difficulty: 7
---

# PBR: Physically Based Rendering

## Историческая справка

PBR эволюционировал через несколько десятилетий, но «прорыв» произошёл в 2012:

- **1967 — Bui Tuong Phong.** Phong shading model. Simple, ad-hoc, but huge step forward.
- **1977 — Blinn.** Blinn-Phong — improvement via half-vector. Still ad-hoc.
- **1982 — Cook-Torrance.** Физически-базированная microfacet BRDF. Academic, не mainstream.
- **1997 — Lafortune.** Generalized Cook-Torrance.
- **2007 — Oren-Nayar.** Rough diffuse model.
- **2010 — Walter, Burley (paper on GGX).** Improved microfacet distribution.
- **2012 — Burley / Disney.** "Physically-Based Shading at Disney" SIGGRAPH course. Unified BRDF с 11 parameters. Pixar, Disney films adopt.
- **2013 — Brian Karis / Epic Games.** "Real Shading in Unreal Engine 4" SIGGRAPH 2013. Adaptation for real-time. Industry takes notice.
- **2014 — Unreal Engine 4.** First major engine с PBR default.
- **2015 — Unity 5.** Adds Standard Shader (PBR).
- **2017 — glTF 2.0.** Metallic-roughness workflow standardized.
- **2018 — Google Filament.** PBR for mobile. Open-source implementation.
- **2020 — Most mobile engines adopt PBR.** Unity URP, Unreal Mobile, Godot 4.
- **2026 — PBR default для new projects.** Industry-wide standard.

Parallel developments: ACES tonemapping, HDR textures, IBL, all complementary к PBR.

---

## Зачем это знать — expanded

В 2012 на SIGGRAPH Brent Burley из Disney представил унифицированную модель shading, которая заменила ad-hoc Phong/Blinn и стала indust-standard. **Disney BRDF** — «одна модель для всего»: металл, кожа, ткань, пластик — описываются 4-6 параметров вместо 20+ ad-hoc. Unreal Engine 4 (Karis 2013) адаптировал её для real-time. Google Filament (2018) принёс PBR на mobile. В 2026 PBR — default для любой serious 3D-app.

---

## Зачем PBR

Classical models:
- **Not energy conserving** (impossible physically).
- **Artist-hostile** (shininess, specular color — неинтуитивные ручки).
- **Not scalable** across lighting conditions (change light и нужно retune все материалы).

PBR:
- **Energy conserving** (diffuse + specular ≤ incoming).
- **Artist-friendly** (albedo, metallic, roughness — физические parameters).
- **Scalable** (материал работает в любом lighting без retuning).

Результат — one material definition, correct look in любой scene.

---

## Physical intuition — что измеряет PBR

PBR simulates interaction of light с real-world materials. Key physical quantities:

### Irradiance vs Radiance

- **Irradiance** (E) — энергия света, hitting surface per unit area. Units: W/m².
- **Radiance** (L) — энергия света, traveling в direction ω per unit area per unit solid angle. Units: W/(m²·sr).

PBR шейдеры работают с radiance — directional light quantity.

### BRDF (Bidirectional Reflectance Distribution Function)

BRDF — fundamental PBR quantity. Defines how much light coming из direction ωi reflects к direction ωo:

```
f(ωi, ωo) = dL_reflected(ωo) / dE_incoming(ωi)
```

Units: 1/sr (per steradian).

Для **perfect diffuse** (Lambertian): `f = albedo / π` (constant, independent of ωo).

Для **perfect mirror**: `f = δ(ωo - reflect(ωi))` (delta function).

Real materials — between extremes.

### Energy conservation requirement

BRDF must satisfy:
```
∫_Ω f(ωi, ωo) · cos(θo) dωo ≤ 1  для всех ωi
```

Reflected energy ≤ incoming. Classical Phong (`specular = cos(θh)^n`) **violates** это для large `n`.

## Principles

### Energy conservation

Reflected energy ≤ incident. Formally for BRDF `f`:

```
∫ f(ωi, ωo) · cos(θi) dωo ≤ 1
```

Classical Phong does not satisfy. Cook-Torrance и Disney — satisfy.

### Fresnel

Reflectivity зависит от viewing angle. At grazing angles (light hits surface edge-on) — more reflective. Schlick approximation:

```
F = F0 + (1 - F0) · (1 - cos(θ))^5
```

`F0` — base reflectivity. For metals ~= albedo; для non-metals ~= 0.04.

### Microfacet theory

Surface — millions of tiny mirrors (microfacets), each perfectly flat. Roughness = распределение orientations. Smooth surface → tight distribution → sharp highlight. Rough → wide distribution → blurry highlight.

```
BRDF_microfacet = (D · G · F) / (4 · (N·V) · (N·L))
```

Где:
- `D` — normal distribution function (GGX).
- `G` — geometry function (self-shadowing).
- `F` — Fresnel.

---

## Cook-Torrance BRDF

Первая physically-based модель (1982):

```
f_specular = (D(m) · F(ωi) · G(ωi, ωo, m)) / (4 · (N·ωi) · (N·ωo))
```

Components:
- Distribution D — какой fraction microfacets oriented для H direction.
- Fresnel F — angular dependence.
- Geometry G — self-shadowing и masking of microfacets.

---

## Disney BRDF (Burley 2012)

Simplified, artist-friendly parametrization. **5 main parameters:**

1. **baseColor** (albedo) — RGB color.
2. **metallic** — is surface metallic (0 = non-metal, 1 = metal).
3. **roughness** — surface roughness (0 = mirror, 1 = matte).
4. **specular** (0.5 default) — non-metallic specular intensity.
5. **normal** — normal map.

Also secondary: anisotropic, subsurface, sheen, clearcoat.

Genius: **most materials can be described этими 5 parameters**. Real metal: metallic=1, albedo=metal color. Plastic: metallic=0, albedo=plastic color. Dry dirt: metallic=0, roughness=0.9.

---

## UE4 implementation (Karis 2013)

Unreal Engine 4 адаптировал Disney для real-time:

### Distribution: GGX (Trowbridge-Reitz)

```
D(h) = α² / (π · ((n·h)²(α² - 1) + 1)²)
```

Where `α = roughness²`. Long tails — soft glossy highlights.

### Geometry: Smith's method

Self-shadowing calculated separately for light и view:

```
G(l, v, h) = G₁(l) · G₁(v)
G₁(x) = (n·x) / ((n·x)(1 - k) + k)
k = (roughness + 1)² / 8  (direct lighting)
```

### Fresnel: Schlick

```
F(v, h) = F0 + (1 - F0) · (1 - (v·h))^5
```

### Diffuse: Lambert

Simple Lambert achieves good enough для diffuse. Disney original uses slight modification (Burley diffuse), но UE4 simplified.

### Assembly

```
f_total = f_diffuse + f_specular
f_diffuse = (1 - F) · (1 - metallic) · albedo / π
f_specular = (D · G · F) / (4 · (n·l) · (n·v))
```

---

## Image-Based Lighting (IBL)

Direct light = один sun или несколько bulbs. Ambient в real world — reflection of **all environment**. IBL uses cubemap (environment map) для realistic ambient.

### Two parts

1. **Diffuse IBL:** convolve env с cosine — irradiance map. Sample по normal direction для diffuse ambient.
2. **Specular IBL:** prefiltered по roughness — several mip levels. Sample по reflection direction, lod = roughness.

Karis 2013 **split-sum approximation:**

```
Lo_specular ≈ L(r) · BRDF_LUT(n·v, roughness)
```

Pre-compute `L(r)` — prefiltered env. Pre-compute `BRDF_LUT` — 2D texture. Sum = approximation accurate enough.

Filament uses exact this approach. Filament также делает split-integral approximation для diffuse.

---

## Material maps

PBR workflow requires several textures:

| Map | Content | Channels |
|---|---|---|
| Albedo / base color | Diffuse color | RGB |
| Metallic | Metallic-ness | R (или combined MR) |
| Roughness | Roughness | R (или combined MR) |
| Normal | Surface normal | RGB tangent-space |
| AO (ambient occlusion) | Occlusion factor | R |
| Emissive | Self-illumination | RGB |
| Height (optional) | Displacement | R |

glTF 2.0 (см. [[gltf-2-format-deep]]) standardized metallic-roughness workflow.

---

## Код (Filament-style fragment shader)

```glsl
// See [[vertex-and-fragment-shaders-by-example]] Example 3 для полного

vec3 F0 = mix(vec3(0.04), albedo, metallic);

float NDF = distributionGGX(N, H, roughness);
float G = geometrySmith(NdotV, NdotL, roughness);
vec3 F = fresnelSchlick(HdotV, F0);

vec3 kD = (1.0 - F) * (1.0 - metallic);

vec3 specular = (NDF * G * F) / (4.0 * NdotV * NdotL);
vec3 diffuse = kD * albedo / PI;

vec3 Lo = (diffuse + specular) * lightColor * NdotL;

// IBL ambient
vec3 irradiance = texture(irradianceMap, N).rgb;
vec3 prefilteredColor = textureLod(prefilterMap, reflect(-V, N), roughness * MAX_MIP).rgb;
vec2 brdfLUT = texture(brdfLUTMap, vec2(NdotV, roughness)).rg;
vec3 specularIBL = prefilteredColor * (F * brdfLUT.x + brdfLUT.y);
vec3 diffuseIBL = kD * irradiance * albedo;

vec3 ambient = (diffuseIBL + specularIBL) * ao;

vec3 finalColor = Lo + ambient;
```

---

## На Mobile

PBR на mobile:
- **Filament** делает это beautifully.
- **Unity URP** поддерживает.
- **Godot Standard renderer** — yes.
- **Custom Vulkan** — реализуемо.

Cost: per-fragment ~60 ALU operations (Disney), +IBL samples. На Adreno 650+ держит 60 FPS без problem. На weak GPUs может потребовать simplification.

Simplification paths:
- Disable IBL, use simple ambient.
- Skip Fresnel (using constant F = 0.04).
- Use Blinn-Phong для non-metals.

---

## Связь

[[lighting-models-lambert-phong-blinn]] — classical predecessors.
[[image-based-lighting-ibl]] — IBL detail.
[[filament-architecture-deep]] — Google реализация.
[[mobile-lighting-tradeoffs]] — choice on mobile.
[[normal-bump-parallax-mapping]] — normal maps — part of PBR workflow.
[[gltf-2-format-deep]] — material textures.

---

## Источники

- **Burley, B. (2012). Physically Based Shading at Disney.** [PDF](https://blog.selfshadow.com/publications/s2012-shading-course/burley/s2012_pbs_disney_brdf_notes_v3.pdf).
- **Karis, B. (2013). Real Shading in Unreal Engine 4.** [PDF](https://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf).
- **Cook, R. & Torrance, K. (1982). A Reflectance Model for Computer Graphics.** [ACM DOI](https://dl.acm.org/doi/10.1145/357290.357293).
- **Google Filament documentation.** [google.github.io/filament](https://google.github.io/filament/Filament.md.html). Section 4 — материалы.
- **Pharr, Jakob, Humphreys (2023). PBR 4th ed.** Academic canonical.

---

## Проверь себя

> [!question]- Что дают 5 parameters в Disney BRDF?
> baseColor, metallic, roughness, specular (default 0.5), normal. Одной parametrization описываются metals и non-metals, smooth и rough, reflective и diffuse. Artist-friendly, physically consistent.

> [!question]- Зачем split-sum approximation для IBL?
> Original IBL integral требует много samples on GPU (expensive). Karis 2013 showed, что можно split на два pre-computed parts (prefiltered env + BRDF LUT), combined runtime. Cost — single texture sample each.

---

## Ключевые карточки

Закон energy conservation в PBR?
?
Reflected energy ≤ incident energy. Classical Phong не satisfies; Cook-Torrance и Disney satisfy. Physical correctness.

---

Microfacet theory?
?
Surface = millions of tiny perfectly-flat mirrors. Distribution of their orientations → roughness. Smooth = tight distribution = sharp highlight. Rough = wide = blurry.

---

## Куда дальше

| Направление | Куда |
|---|---|
| IBL detail | [[image-based-lighting-ibl]] |
| Filament implementation | [[filament-architecture-deep]] |
| Mobile optimization | [[mobile-lighting-tradeoffs]] |
| Normal maps | [[normal-bump-parallax-mapping]] |

---

*Deep-dive модуля M6.*

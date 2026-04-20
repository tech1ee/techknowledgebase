---
title: "Lambert, Phong, Blinn: классические модели освещения"
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
  - level/intermediate
related:
  - "[[pbr-physically-based-rendering]]"
  - "[[vertex-and-fragment-shaders-by-example]]"
  - "[[vectors-in-3d-graphics]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vectors-in-3d-graphics]]"
primary_sources:
  - url: "https://dl.acm.org/doi/10.1145/360825.360839"
    title: "Phong, B. T. (1975). Illumination for Computer Generated Pictures. CACM"
    accessed: 2026-04-20
  - url: "https://dl.acm.org/doi/10.1145/563858.563893"
    title: "Blinn, J. (1977). Models of Light Reflection for Computer Synthesized Pictures. SIGGRAPH"
    accessed: 2026-04-20
reading_time: 15
difficulty: 4
---

# Классические модели освещения

До PBR (2012+) все real-time rendering использовало классические модели — **Lambert**, **Phong**, **Blinn-Phong**. Даже сегодня они актуальны для: mobile low-end devices, simple UI 3D, stylized games. Плюс PBR built on top of их mathematical foundation.

---

## Lambert diffuse (1760)

Johann Heinrich Lambert в 1760 году в «Photometria» сформулировал: intensity света, отражённого от matte surface, пропорциональна cosine угла между нормалью и направлением света.

```
Id = Kd · (N · L)
```

Где:
- `Kd` — diffuse reflectivity (albedo).
- `N` — unit normal.
- `L` — unit light direction.
- `N·L` — dot product (см. [[vectors-in-3d-graphics#Dot product]]).

Для negative `N·L` (свет за поверхностью) clamp к 0:

```glsl
float NdotL = max(dot(N, L), 0.0);
vec3 diffuse = albedo * lightColor * NdotL;
```

Работает для perfectly diffuse (matte) surfaces — раскрашенная бумага, matte plastic.

---

## Phong specular (Phong 1975)

Bui Tuong Phong в PhD-диссертации University of Utah (published CACM 1975) добавил specular component — блики от glossy surfaces.

### Phong model

```
Is = Ks · (R · V)^n
```

Где:
- `Ks` — specular reflectivity.
- `R = 2(N·L)N − L` — reflected light vector.
- `V` — view direction.
- `n` — shininess (exponent). Higher = sharper highlight.

Total illumination = ambient + diffuse + specular:

```
I = Ka + Kd(N·L) + Ks(R·V)^n
```

```glsl
vec3 N = normalize(v_normal);
vec3 L = normalize(-lightDir);
vec3 R = reflect(-L, N);  // reflected light
vec3 V = normalize(cameraPos - worldPos);

float NdotL = max(dot(N, L), 0.0);
float RdotV = max(dot(R, V), 0.0);
float specFactor = pow(RdotV, shininess);

vec3 color = ambient + albedo * NdotL + specularColor * specFactor;
```

---

## Blinn-Phong (Blinn 1977)

Jim Blinn в SIGGRAPH 1977 модифицировал Phong: заменил reflection vector `R` на **half-vector** `H = normalize(L + V)`:

```
Is = Ks · (N · H)^n
```

Why: computing `R` требует `reflect()` — 4 ops. Computing `H` — 2 ops (add + normalize). Quantitatively faster.

Также физически чуть правильнее (closer to real microfacet models).

```glsl
vec3 H = normalize(L + V);
float NdotH = max(dot(N, H), 0.0);
float specFactor = pow(NdotH, shininess);
```

Blinn-Phong стал default для OpenGL fixed-function pipeline, в большинстве games до 2010-х.

---

## Комбинированная модель

```glsl
vec3 computeLighting(vec3 albedo, vec3 N, vec3 L, vec3 V,
                     vec3 lightColor, vec3 ambientColor,
                     vec3 specularColor, float shininess) {
    vec3 H = normalize(L + V);
    
    float NdotL = max(dot(N, L), 0.0);
    float NdotH = max(dot(N, H), 0.0);
    
    vec3 ambient = albedo * ambientColor;
    vec3 diffuse = albedo * lightColor * NdotL;
    vec3 specular = specularColor * lightColor * pow(NdotH, shininess);
    
    return ambient + diffuse + specular;
}
```

Ambient — simple constant (fallback когда нет direct light). Modern engines заменяют на **Image-Based Lighting** (IBL) — см. [[image-based-lighting-ibl]].

---

## Multiple lights

Для каждого light:

```glsl
vec3 totalColor = albedo * ambientColor;
for (int i = 0; i < numLights; i++) {
    vec3 L = normalize(lightPos[i] - worldPos);
    float attenuation = 1.0 / (1.0 + distance(lightPos[i], worldPos) * 0.1);
    
    float NdotL = max(dot(N, L), 0.0);
    vec3 H = normalize(L + V);
    float NdotH = max(dot(N, H), 0.0);
    
    totalColor += (albedo * NdotL + specularColor * pow(NdotH, shininess))
                  * lightColor[i] * attenuation;
}
```

For N > 5 lights, consider clustered forward или deferred approach.

---

## Limitations classical models

1. **Not energy-conserving.** Sum of reflected energy может быть > incident energy. Physically wrong.
2. **No Fresnel effect.** Edge-on glossy surfaces look same as frontal. Real world: edge более reflective.
3. **No microfacet model.** Roughness — ad-hoc `shininess`, not physical.
4. **No subsurface scattering.** Skin, marble, wax — all look like plastic.

All closed by PBR (см. [[pbr-physically-based-rendering]]).

---

## When to use classical

- **Low-end mobile** где PBR дорог.
- **Stylized / cartoon** — PBR overkill.
- **Tools / editor preview** — быстрый default.
- **Legacy code** — compatible.

---

## Связь

[[vectors-in-3d-graphics]] — dot product математика.
[[pbr-physically-based-rendering]] — modern replacement.
[[vertex-and-fragment-shaders-by-example]] — practical GLSL.
[[mobile-lighting-tradeoffs]] — выбор на mobile.

---

## Источники

- **Phong, B. T. (1975). Illumination for Computer Generated Pictures. CACM.** [ACM DOI](https://dl.acm.org/doi/10.1145/360825.360839).
- **Blinn, J. (1977). Models of Light Reflection for Computer Synthesized Pictures. SIGGRAPH.** [ACM DOI](https://dl.acm.org/doi/10.1145/563858.563893).
- **Akenine-Möller et al. (2018). RTRT 4, chapter 5–9.**

---

## Проверь себя

> [!question]- Чем Blinn-Phong отличается от Phong?
> Blinn использует half-vector H = normalize(L+V) вместо reflection R. Формула: (N·H)^n вместо (R·V)^n. Быстрее (2 ops vs 4), немного физичнее. Default в OpenGL fixed-function.

---

## Ключевые карточки

Закон Ламберта?
?
`Id = Kd · (N · L)` — diffuse intensity пропорциональна cosine угла между normal и light. 1760. Основа всех diffuse shading formulas.

---

## Куда дальше

| Направление | Куда |
|---|---|
| PBR | [[pbr-physically-based-rendering]] |
| Код | [[vertex-and-fragment-shaders-by-example]] |
| Mobile tradeoffs | [[mobile-lighting-tradeoffs]] |

---

*Deep-dive модуля M6.*

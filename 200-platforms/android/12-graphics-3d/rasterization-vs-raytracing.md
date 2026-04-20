---
title: "Растеризация vs ray tracing: две парадигмы рендеринга"
created: 2026-04-20
modified: 2026-04-20
type: comparison
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - type/comparison
  - level/intermediate
related:
  - "[[rendering-pipeline-overview]]"
  - "[[gpu-architecture-fundamentals]]"
  - "[[pbr-physically-based-rendering]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[rendering-pipeline-overview]]"
primary_sources:
  - url: "https://dl.acm.org/doi/10.1145/15886.15902"
    title: "Kajiya, J. (1986). The Rendering Equation. SIGGRAPH"
    accessed: 2026-04-20
  - url: "https://developer.nvidia.com/blog/nvidia-announces-rtx-ray-tracing-cores/"
    title: "NVIDIA RTX hardware ray tracing"
    accessed: 2026-04-20
  - url: "https://www.khronos.org/blog/ray-tracing-in-vulkan"
    title: "Khronos: Ray Tracing in Vulkan"
    accessed: 2026-04-20
  - url: "https://developer.arm.com/documentation/102666/0100/Ray-tracing/Ray-tracing-in-Arm-GPUs"
    title: "ARM: Ray tracing in Arm GPUs"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap37.html"
    title: "Vulkan 1.4 Ray Tracing Pipelines"
    accessed: 2026-04-20
reading_time: 28
difficulty: 5
---

# Растеризация vs ray tracing

Real-time 3D графика на Android в 2026 году — это преимущественно **растеризация**. Ray tracing появляется в flagship-чипах (Adreno 740+, Mali-Immortalis G720+, Xclipse 960 RDNA4, PowerVR Photon), но для production-приложений уровня [[case-planner-5d|Planner 5D]] или [[case-ikea-place-ar|IKEA Place]] остаётся экспериментальным. Этот deep-dive разбирает обе парадигмы, их математическую базу, hardware support на Android 2026, production-готовность и hybrid-стратегии.

---

## Зачем это знать

**Первое — принятие решения.** В 2026 mobile ray tracing — это не «есть или нет», а «в каком объёме». Vulkan 1.3+ поддерживает `VK_KHR_ray_tracing_pipeline` и `VK_KHR_ray_query`. Flagship-phones с RT cores могут дать feature parity с desktop. Но RT на mobile драматически тратит batery. Неправильное решение = 40-minute разряд батареи вместо 2 часов.

**Второе — hybrid design.** Production-apps в 2026 используют **hybrid rendering**: rasterization base + ray tracing для specific features (shadows, reflections). Понимание когда что использовать — ключевой skill. Full RT pipeline на mobile до 2028–2030 останется niche.

**Третье — fallback strategy.** Если app хочет RT на flagship, надо иметь fallback для 80% устройств без RT. Это — архитектурное решение: либо «RT-only flagship app», либо «scalable quality tiers».

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[rendering-pipeline-overview]] | Понимание стандартной rasterization pipeline — база для сравнения |
| [[gpu-architecture-fundamentals]] | Warp execution — в RT тоже через SIMT, но с divergence issues |
| [[vectors-in-3d-graphics]] | Ray math — origin + direction, dot products для intersections |

---

## Терминология

| Термин | Определение |
|---|---|
| Rasterization | Проекция geometry на screen, определение покрываемых пикселей |
| Ray tracing | Выпуск лучей от камеры/источника, поиск пересечений с geometry |
| Ray casting | Primary rays only — нет recursive reflections/refractions |
| Path tracing | Full Monte Carlo integration rendering equation — photorealistic |
| BVH (Bounding Volume Hierarchy) | Tree structure для ускорения ray-geometry intersection |
| TLAS / BLAS | Top-Level / Bottom-Level Acceleration Structure (Vulkan RT) |
| Primary ray | Ray от камеры через пиксель |
| Secondary ray | Ray отражённый/refracted от surface |
| Shadow ray | Ray к light source для occlusion test |
| Denoising | AI/temporal фильтрация noisy RT output (Monte Carlo) |
| DLSS / FSR / Metal FX | Upscaling technologies, критичны для mobile RT (рендер в низком разрешении + upscale) |
| RT core | Hardware unit for BVH traversal & ray-triangle intersection |

---

## Историческая справка

Rasterization и ray tracing развивались параллельно с 1960-х как конкурирующие парадигмы. Rasterization победил в real-time (hardware GPUs), ray tracing — в offline (Pixar, VFX).

- **1968 — Appel.** «Some techniques for shading machine renderings of solids» — первый описанный ray casting algorithm.
- **1974 — Catmull.** Rasterization с z-buffer становится стандартом для real-time.
- **1980 — Whitted.** «An Improved Illumination Model for Shaded Display» — первый recursive ray tracer, с reflections и refractions.
- **1986 — Kajiya.** **The Rendering Equation** — математическая basis всех global illumination methods.
- **1990s — Mental Ray, RenderMan.** CPU-based ray tracers для VFX production.
- **2000-е — Intel Larrabee.** Попытка сделать x86 GPU для ray tracing. Failed commercially, но идеи остались.
- **2008 — Turner Whitted becomes NVIDIA researcher.** NVIDIA начинает investing в RT hardware.
- **2018 — NVIDIA Turing (GeForce RTX 20 series).** Первые consumer GPU с dedicated **RT cores**. Battlefield V, Control — first games.
- **2020 — PlayStation 5 / Xbox Series X.** RT на consoles (AMD RDNA2).
- **2020 — DirectX Raytracing (DXR) 1.1** с inline ray queries.
- **2020 — Vulkan RT ratified.** `VK_KHR_ray_tracing_pipeline` в core Vulkan 1.2+.
- **2022 — Samsung Xclipse 920 (AMD RDNA2).** Первый hardware RT на mobile.
- **2023 — Qualcomm Adreno 740 (Snapdragon 8 Gen 2).** Mobile RT software support (VK_KHR_ray_query).
- **2023 — ARM Immortalis G715.** Первый Mali с dedicated RT unit.
- **2024 — Adreno 830 (Snapdragon 8 Gen 3).** Hardware RT.
- **2025 — Imagination PowerVR Photon.** PowerVR returns с focus на RT.
- **2026 — Xclipse 960 (RDNA4).** 2× faster ray generation чем RDNA3.
- **2026 — Adreno 840 (Snapdragon X Elite Gen 2).** Production-ready mobile RT.

RT на mobile доступен, но первая **массовая** RT game — ожидается 2027–2028 при ~30% installed base с RT.

---

## Теоретические основы

### Rasterization — парадигма

Алгоритм (для каждого треугольника):
1. Transform vertices в clip space (vertex shader).
2. Project на screen, определить bounding box.
3. Для каждого pixel в bbox: in-triangle test (edge equations).
4. Если in-triangle: interpolate attributes, call fragment shader, compute color.
5. Depth test, write.

Сложность: O(triangles × pixels_per_triangle). Хорошо parallelized через warp execution. Cache-friendly (per-tile locality).

**Что rasterization не умеет естественно:**
- Reflections off-screen (pixels which reflect objects outside view).
- Refractions (light bending through glass/water).
- Soft shadows без approximation.
- Global illumination (indirect light bouncing multiple times).

Все эти effects решаются через **tricks**: SSR (screen-space reflections), shadow maps + PCF, SSAO, baked lightmaps, irradiance probes. Каждый — approximation с артефактами.

### Ray tracing — парадигма

Алгоритм (для каждого pixel):
1. Cast primary ray: origin = camera, direction = через pixel.
2. Intersect ray vs all geometry — find closest hit.
3. At hit point: evaluate BRDF, sample incoming light.
4. Для reflections: cast secondary ray in reflected direction, recurse.
5. Для soft shadows: sample многих points on light source, average.
6. Combine → pixel color.

Сложность: O(pixels × rays_per_pixel × log(geometry) для BVH). Гораздо более compute-heavy чем rasterization, но **simulates physics correctly**.

### Rendering equation (Kajiya 1986)

Формально ray tracing — solution of:

```
L(x, ω) = Le(x, ω) + ∫_Ω fr(x, ωi, ω) · L(x, ωi) · cos(θi) dωi
```

Где:
- `L(x, ω)` — radiance leaving point x в direction ω (что видим камерой).
- `Le(x, ω)` — emitted radiance (для light sources).
- `fr(x, ωi, ω)` — **BRDF** (Bidirectional Reflectance Distribution Function) — как поверхность отражает свет (см. [[pbr-physically-based-rendering]]).
- `∫_Ω` — интеграл over hemisphere above surface.
- `L(x, ωi)` — incoming radiance from direction ωi. **Это recursive!** — чтобы вычислить, нужно снова cast ray, снова integrate.
- `cos(θi)` — Lambert's law (light attenuation по angle).

Уравнение — интегро-уравнение, аналитически unsolvable для general scenes.

### Monte Carlo integration

Интеграл по hemisphere численно решается через **random sampling**:

```
L ≈ (1/N) × Σ [fr · L_i · cos(θi) / p(ωi)]
```

Где `p(ωi)` — probability distribution samples (importance sampling для efficiency).

**Проблема:** sparse sampling → **noise**. Типичная RT image с 1 sample per pixel (1 spp) — очень шумная.

Решения:
- **Many samples** (16–64 spp) — expensive.
- **Importance sampling** — направлять samples по BRDF lobes.
- **Denoising** — AI/temporal фильтрация (NVIDIA ReSTIR, Intel Open Image Denoise).

Mobile RT в 2026: 1 spp + temporal denoising — typical approach.

### BVH — acceleration structure

Naive ray-triangle test для каждого triangle = O(N) per ray. Для 1M triangles × 1M pixels = 10¹² operations. Не реально.

**BVH (Bounding Volume Hierarchy):**
1. Group triangles в bounding boxes (AABB).
2. Group bounding boxes в higher-level bounding boxes.
3. Recursive tree.
4. Ray traversal: descend tree, skip subtrees не пересекающиеся с ray.

Complexity: O(log N) per ray. Для 1M triangles — ~20 checks per ray. Feasible.

Vulkan RT использует **two-level BVH**:
- **BLAS (Bottom-Level Acceleration Structure):** per-mesh BVH. Обычно built once, stored.
- **TLAS (Top-Level Acceleration Structure):** scene-level BVH of BLAS instances. Rebuilt per frame (для moving objects).

Build cost: BLAS — 5–50 ms per complex mesh (one-time). TLAS — sub-ms for typical scene.

### Ray tracing shaders (Vulkan)

Vulkan RT pipeline имеет 5 shader types:

1. **Ray Generation Shader** — вызывается per pixel, выпускает primary ray.
2. **Intersection Shader** — custom geometry (не только triangles). Optional.
3. **Any-Hit Shader** — вызывается per potential hit (для alpha testing). Optional.
4. **Closest-Hit Shader** — вызывается for closest intersection found. Вычисляет color.
5. **Miss Shader** — если ray не попадает ни во что. Обычно возвращает sky color.

```glsl
// Ray generation shader (simplified)
#version 460
#extension GL_EXT_ray_tracing : require

layout(binding = 0) uniform accelerationStructureEXT topLevelAS;
layout(binding = 1, rgba8) uniform image2D outputImage;

void main() {
    vec2 pixelCenter = vec2(gl_LaunchIDEXT.xy) + vec2(0.5);
    vec2 uv = pixelCenter / vec2(gl_LaunchSizeEXT.xy);
    
    vec3 rayOrigin = cameraPos;
    vec3 rayDir = computeRayDirection(uv);
    
    payload.color = vec3(0.0);
    traceRayEXT(topLevelAS,
                gl_RayFlagsOpaqueEXT, 
                0xFF, 
                0, 0, 0,
                rayOrigin, 0.001, rayDir, 10000.0,
                0);
    
    imageStore(outputImage, ivec2(gl_LaunchIDEXT.xy), vec4(payload.color, 1.0));
}
```

### Hybrid rendering

Практика 2026: rasterization base + ray tracing для specific features:
- **Ray-traced shadows** — sharper, no shadow map artifacts.
- **Ray-traced reflections** — для glossy materials off-screen objects visible.
- **Ray-traced ambient occlusion** — better than SSAO.
- **Ray-traced global illumination** — dynamic, без precomputed lightmaps.

Преимущество hybrid: **primary visibility cheap** (rasterization), **complex effects accurate** (RT). Best of both.

---

## Hardware support на Android 2026

| GPU | RT cores | Vulkan RT | Ray/s (rough) | Status |
|---|---|---|---|---|
| Adreno 660 (SD 888) | Software only | Not supported | — | Rasterization only |
| Adreno 740 (SD 8 Gen 2) | Software | VK_KHR_ray_query | ~0.5G rays/s | Experimental |
| Adreno 830 (SD 8 Gen 3) | Hardware | Full RT pipeline | ~2G rays/s | Available |
| Adreno 840 (SD X Elite) | Enhanced | Full | ~3G rays/s | Production |
| Mali Immortalis G715 | First gen RT | Full | ~1.5G rays/s | Available |
| Mali Immortalis G720 (2025) | Enhanced RT | Full | ~2.5G rays/s | Production |
| Mali Immortalis G925 (2026) | Gen 3 RT | Full | ~3.5G rays/s | Best Mali |
| PowerVR BXT-32 (Photon) | Dedicated | Full | ~2G rays/s | Niche |
| Xclipse 940 (RDNA3) | AMD hardware | Full | ~2G rays/s | Samsung only |
| Xclipse 960 (RDNA4, 2026) | Enhanced | Full | ~4G rays/s | Best Android |

### API (Vulkan extensions)

- **`VK_KHR_acceleration_structure`** — BVH creation, update, management.
- **`VK_KHR_ray_tracing_pipeline`** — full RT pipeline с ray gen / closest hit / miss shaders.
- **`VK_KHR_ray_query`** — **inline** ray queries в regular shaders (vertex, fragment, compute). Lightweight alternative.

Ray query model — проще для hybrid. Например, в fragment shader cast ray для reflection:

```glsl
// Inline ray query in fragment shader
#version 460
#extension GL_EXT_ray_query : require

void main() {
    vec3 reflectionDir = reflect(-viewDir, normal);
    rayQueryEXT rayQuery;
    rayQueryInitializeEXT(rayQuery, topLevelAS, 
                          gl_RayFlagsOpaqueEXT, 0xFF,
                          worldPos, 0.01, reflectionDir, 100.0);
    
    while(rayQueryProceedEXT(rayQuery)) {
        // Process intersections
    }
    
    vec3 reflectionColor;
    if(rayQueryGetIntersectionTypeEXT(rayQuery, true) == 
       gl_RayQueryCommittedIntersectionTriangleEXT) {
        // Hit something, fetch material
        reflectionColor = computeReflection(rayQuery);
    } else {
        reflectionColor = skyColor;
    }
    
    fragColor = baseColor * 0.7 + reflectionColor * 0.3;
}
```

### OpenGL ES: нет RT

OpenGL ES не имеет официальной RT поддержки. Vendor extensions есть (например, `GL_QCOM_ray_tracing`), но ограниченные. Для RT — идти Vulkan.

---

## Сравнение

| Критерий | Rasterization | Ray tracing |
|---|---|---|
| **Visual quality** | Limited (screen-space approximations) | Physically accurate |
| **Reflections** | SSR (artifacts, screen-space only) | Accurate, off-screen objects |
| **Shadows** | Shadow maps (bias, aliasing, cascade complexity) | Sharp or soft, accurate |
| **Ambient occlusion** | SSAO (screen-space, limited) | Ray-traced AO (accurate) |
| **Global illumination** | Baked lightmaps | Dynamic, real-time |
| **Refractions** | Extremely hard (cube map approximations) | Natural |
| **Complexity scaling** | O(geometry + pixels) | O(pixels × rays × log(geometry)) |
| **Mobile FPS @ 2026** | 60-120 FPS easily | 30-60 with hybrid, flagship only |
| **Battery cost** | ~800 mW typical | ~2000+ mW (2.5× more) |
| **Device penetration** | 100% | ~10-15% Android (flagship 2023+) |
| **Production-ready Android** | ✅ стандарт | ⚠️ experimental for most apps |

### Performance reality

На Snapdragon 8 Gen 3 (Adreno 830):
- Full RT pipeline 1 spp 1080p = ~30 FPS (без denoising).
- Hybrid (rasterization + RT shadows) 1080p = 60 FPS.
- Hybrid + RT reflections + denoising 1080p = 45 FPS.

Battery drain @ full RT: ~40% per hour. Sustained RT gaming limited to ~1.5 hours.

---

## Реальные кейсы

### Planner 5D / IKEA Place (2026)

**Pure rasterization.** Planner 5D использует baked lighting + shadow maps. IKEA Place — rasterization с ARCore camera feed как background. Оба не используют RT — device diversity требует broad compatibility.

### Fortnite Mobile на flagship (2024+)

Partial RT: RT shadows (character casts accurate shadow). Rasterization for everything else. Available only на Snapdragon 8 Gen 3+ и equivalents. Toggle в settings.

### COD Mobile с RT

Introduced 2024, только на flagship. RT reflections в water. 30 FPS @ 1080p vs 60 FPS без RT. User-selectable quality.

### Live Home 3D — photorealistic mode (2025+)

Non-real-time rendering через cloud. User отправляет scene, RT pass на cloud GPU (AWS), returns 4K рендер. 30–60 секунд на image. Mobile не делает RT локально.

### Experimental: Dreams Mobile (hypothetical 2027)

Media Molecule's Dreams-like engine на mobile с RT GI. Full ray-traced global illumination. На Snapdragon 8 Gen 4 (2027): 30 FPS. Niche app для creative community.

---

## Когда использовать RT на Android

✅ **Use RT если:**
- Target flagship phones (Snapdragon 8 Gen 3+, Tensor G4+).
- Premium visual quality — differentiator (AR shopping, design tools).
- Specific effects (accurate reflections, soft shadows) — main selling point.
- Scalable quality tiers — RT on flagship, fallback on mid-range.

❌ **НЕ use RT если:**
- Target broad device base (<3-year-old phones).
- Battery life critical (>1 час gaming typical).
- Rasterization с baked lighting покрывает quality needs.
- Dev team не имеет RT expertise (complex debugging).

### Hybrid stratification

Типичная tier structure для scalable app:
- **Tier 1 (flagship 2024+):** rasterization + RT shadows + RT reflections + RT AO + denoising.
- **Tier 2 (mid-flagship 2022+):** rasterization + RT shadows only.
- **Tier 3 (mid-range):** rasterization + shadow maps + SSAO + SSR.
- **Tier 4 (low-end):** rasterization + simple shadows только.

User selects automatic или manually.

---

## Distance fields — промежуточная парадигма

Ещё одна техника, которая распространяется: **Signed Distance Fields (SDF)**. Каждая voxel grid cell хранит distance к nearest surface. Ray marching через SDF — быстрее true ray tracing.

Unreal Engine 5 Lumen использует mixture: SDF для coarse GI + optional RT для quality-critical areas. На mobile SDF — alternative к RT. Epic's UE5 Mobile port использует SDF-based Lumen.

### Ray marching vs ray tracing

- **Ray tracing:** find analytical intersection с triangles в BVH. Hardware-accelerated в RT cores.
- **Ray marching:** step through 3D space small steps, query SDF. Pure compute shader — runs on any GPU.

Ray marching на mobile GPU без RT cores = альтернатива. Unreal 5.3+ использует на Adreno / Mali без RT.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| RT заменит rasterization | Hybrid — future. Rasterization остаётся fast primary visibility |
| Mobile RT = desktop RT | Мобильный RT обычно 1 spp, desktop 4-8 spp. Quality gap |
| RT cores решают всё | Без denoising результат unusably noisy |
| Ray tracing дешевле shadow maps | Per-shadow эквивалент; total сумма больше |
| Path tracing = ray tracing | Path tracing = full Monte Carlo rendering equation solve. Ray tracing = generic term |
| RT без hardware медленно, но работает | Software RT практически unusable на mobile (2+ orders magnitude slower) |

---

## Подводные камни

### Ошибка 1: Full RT без denoising

**Как избежать:** ship denoiser (TAA-based или AI-based). Без этого result — noise city.

### Ошибка 2: Ray budget не контролируется

**Как избежать:** ограничить rays per pixel, capped recursive depth (2-3 max). Otherwise — variable frame times, thermal issues.

### Ошибка 3: BVH rebuild каждый frame

**Как избежать:** BLAS build only при load. TLAS rebuild только для dynamic objects.

### Ошибка 4: RT для every material

**Как избежать:** RT selective — только glossy reflections, soft shadows. Rough surfaces не требуют RT.

### Ошибка 5: Без fallback path

**Как избежать:** всегда иметь rasterization-only code path для non-RT devices.

---

## Связь с другими темами

[[rendering-pipeline-overview]] — классическая rasterization pipeline.
[[pbr-physically-based-rendering]] — rendering equation в context materials.
[[gpu-architecture-fundamentals]] — RT cores как hardware extension.
[[shadow-mapping-on-mobile]] — rasterized shadows (альтернатива RT shadows).
[[vulkan-on-android-fundamentals]] — Vulkan extensions для RT.
[[image-based-lighting-ibl]] — альтернатива RT GI для static scenes.
[[ar-lighting-estimation]] — AR использует дополнительные RT techniques для realistic light blending.

---

## Источники

- **Kajiya, J. (1986). The Rendering Equation.** [ACM DOI](https://dl.acm.org/doi/10.1145/15886.15902). Фундамент.
- **Whitted, T. (1980). An Improved Illumination Model for Shaded Display.** Communications of the ACM. Первый recursive ray tracer.
- **Appel, A. (1968). Some techniques for shading machine renderings of solids.** AFIPS. Исходный ray casting.
- **Pharr, Jakob, Humphreys (2023). Physically Based Rendering, 4th ed.** Canonical book. Chapter 13 (Light Transport I).
- **Akenine-Möller, T., et al. (2018). Real-Time Rendering, 4th ed.** Chapter 11 (Ray Tracing).
- **Khronos. Ray Tracing in Vulkan.** [khronos.org/blog](https://www.khronos.org/blog/ray-tracing-in-vulkan).
- **Vulkan 1.4 Spec, Chapter 37.** [registry.khronos.org](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap37.html).
- **ARM. Ray tracing in Arm GPUs.** [developer.arm.com](https://developer.arm.com/documentation/102666/0100/Ray-tracing/Ray-tracing-in-Arm-GPUs).
- **NVIDIA. Ray Tracing Gems II (2021).** Open-access book по practical RT.

---

## Проверь себя

> [!question]- В чём фундаментальная разница rasterization и ray tracing?
> Rasterization — geometry-driven: для каждого треугольника определяется, какие пиксели он покрывает. Ray tracing — pixel-driven: для каждого пикселя выпускается ray и ищется пересечение с геометрией. Результат — rasterization быстр для many-triangle scenes, но плохо handle'ит reflections/refractions/off-screen effects; RT медленнее, но simulates physics accurately.

> [!question]- Что такое BVH и зачем нужен?
> Bounding Volume Hierarchy — tree structure, где geometry grouped в nested bounding boxes. Без BVH ray tracing — O(N) per ray (all triangles tested). С BVH — O(log N). Vulkan использует two-level: BLAS (per-mesh) + TLAS (scene). Без acceleration structures RT cost prohibitive.

> [!question]- Почему mobile RT обычно использует 1 sample per pixel?
> Battery + performance budget. Desktop RTX typically 2-8 spp. Mobile 1 spp, compensated через temporal + spatial denoising (AI-based или TAA-based фильтрация). Result обычно приемлемый для real-time, но inferior к reference offline render.

> [!question]- Что такое hybrid rendering?
> Rasterization + RT combined: primary visibility rasterized (быстро), specific effects (shadows, reflections, AO) ray-traced. Best of both. 2026 production-подход для RT apps.

> [!question]- Какие GPU на Android 2026 поддерживают hardware ray tracing?
> Snapdragon 8 Gen 3+ (Adreno 830+), Mali Immortalis G715+, Xclipse 940+ (Samsung RDNA3/4), PowerVR Photon. Всё это flagship и sub-flagship чипы 2023+. ~10-15% Android install base в 2026.

---

## Ключевые карточки

Что такое rendering equation?
?
Kajiya 1986 — интегральное уравнение, описывающее распространение света: `L(x,ω) = Le + ∫ fr · L · cos(θi) dωi`. Основа всех методов global illumination (path tracing, photon mapping, RT).

---

Что такое ray query vs ray tracing pipeline в Vulkan?
?
Ray query — inline rays в обычных shaders (fragment/compute). Lightweight, hybrid-friendly. Ray tracing pipeline — отдельная pipeline с 5 shader stages (ray gen, closest hit, miss, any hit, intersection). Full-featured but heavier.

---

Когда стоит добавлять RT к mobile Android app в 2026?
?
Только для flagship-targeted apps где premium visual quality — differentiator (design tools, AR shopping с glossy reflections). Для broad-device apps — rasterization + baked lighting по-прежнему стандарт. Always ship fallback path.

---

Что такое denoising в контексте RT?
?
Процесс фильтрации шумного output 1-spp ray tracer. Temporal (accumulating samples over frames), spatial (bilateral filter), AI-based (NVIDIA ReSTIR, Intel Open Image Denoise). Без denoising RT выход usually unusable на 1 spp.

---

Что такое BVH и где используется?
?
Bounding Volume Hierarchy — tree of nested bounding boxes для ускорения ray-geometry intersection до O(log N). В Vulkan: BLAS per mesh, TLAS scene-level. Build cost — 5-50ms per mesh (one-time). Traversal — hardware-accelerated в RT cores.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Стандартный pipeline | [[rendering-pipeline-overview]] |
| Lighting detail | [[pbr-physically-based-rendering]] |
| Shadows без RT | [[shadow-mapping-on-mobile]] |
| BVH и acceleration | [[vulkan-on-android-fundamentals]] |
| Image-Based Lighting | [[image-based-lighting-ibl]] |

---

*Comparison-file модуля M2. Deep-dive расширенный 2026-04-20.*

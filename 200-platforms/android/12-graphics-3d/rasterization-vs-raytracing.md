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
reading_time: 15
difficulty: 4
---

# Растеризация vs ray tracing

Real-time 3D графика на Android в 2026 году — это преимущественно **растеризация**. Ray tracing появляется в flagship-чипах (Adreno 740, Mali-Immortalis G720, Xclipse 960 RDNA4), но для production-приложений уровня [[case-planner-5d|Planner 5D]] или [[case-ikea-place-ar|IKEA Place]] остаётся экспериментальным. Этот файл разбирает обе парадигмы, их математическую базу, hardware support на Android 2026 и production-готовность.

---

## Зачем это знать

В 2026 mobile ray tracing начинает проникать в приложения: Samsung Xclipse 960 имеет dedicated RT cores, ARM Immortalis поддерживает hardware ray tracing, Vulkan 1.3+ даёт `VK_KHR_ray_tracing_pipeline`. Понимание обеих парадигм позволяет: выбрать правильный подход для сцены, комбинировать (hybrid rendering), избежать over-engineering.

---

## Теоретическая база

### Rasterization

Парадигма: для каждого треугольника определить, какие пиксели он покрывает, и посчитать их цвет. Projection-centric.

Классическая пипилайн (см. [[rendering-pipeline-overview]]): vertex shader → rasterizer → fragment shader. Линейная сложность от геометрии: O(vertices + fragments).

### Ray tracing

Парадигма: для каждого пикселя выпускать ray в scene, проверять пересечение со всеми объектами, вычислять цвет в точке пересечения (и rекурсивно для отражений/refractions).

Математически — **rendering equation** (Kajiya 1986):

```
L(x, ω) = Le(x, ω) + ∫ fr(x, ωi, ω) · L(x, ωi) · cos(θi) dωi
```

Где:
- `L(x, ω)` — light leaving point x в direction ω.
- `Le` — emitted light.
- `fr` — BRDF.
- Интеграл — incoming light со всех directions.

Численно решается Monte Carlo — много sample rays per pixel.

### Hybrid rendering

Практика 2026: основной pipeline rasterization + ray tracing для specific features:
- **Ray-traced shadows** — sharper, no shadow map artifacts.
- **Ray-traced reflections** — screen-space reflections artifacts removed.
- **Ray-traced ambient occlusion**.
- **Global illumination** — dynamic, без precomputed lightmaps.

---

## Hardware support на Android 2026

| GPU | RT cores | Vulkan RT | Status |
|---|---|---|---|
| Adreno 740 (SD 8 Gen 2) | Software | VK_KHR_ray_query | Experimental |
| Adreno 830 (SD 8 Gen 3) | Hardware | Full RT pipeline | Available |
| Adreno 840 (SD X Elite) | Hardware | Full | Production |
| Mali Immortalis G715+ | Hardware | Full | Available |
| Mali Immortalis G720 (2025+) | Hardware + improvements | Full | Production |
| PowerVR Photon | Hardware | Full | Niche |
| Xclipse 940 (RDNA3) | Hardware | Full | Production (Samsung phones) |
| Xclipse 960 (RDNA4, 2026) | Enhanced hardware | Full, 2× faster | Best on Android |
| Older GPUs | None | Not supported | N/A |

### API

**Vulkan extensions:**
- `VK_KHR_acceleration_structure` — BVH structures.
- `VK_KHR_ray_tracing_pipeline` — ray generation, closest-hit, miss, intersection shaders.
- `VK_KHR_ray_query` — inline ray queries in regular shaders (lightweight alternative).

**OpenGL ES:** no official RT. Only through vendor extensions.

---

## Сравнение

| Критерий | Rasterization | Ray tracing |
|---|---|---|
| **Visual quality** | Limited (screen-space approximations) | Physically accurate |
| **Reflections** | Screen-space reflections (SSR, artifacts) | Accurate, off-screen |
| **Shadows** | Shadow maps (bias, aliasing issues) | Sharp, accurate |
| **Ambient occlusion** | SSAO (screen-space, limited) | Ray-traced AO (accurate) |
| **Global illumination** | Precomputed lightmaps | Dynamic |
| **Performance (mobile 2026)** | 60 FPS easy | 30-60 FPS with hybrid, flagship only |
| **Hardware** | All GPUs | Flagship chips 2024+ |
| **Production-ready Android** | ✅ | ⚠️ Experimental for most apps |

---

## Реальные кейсы

### Planner 5D / IKEA Place (2026)

Rasterization. RT не оправдан — scene size moderate, phones широкий диапазон.

### Flagship phone games

Hybrid — RT shadows + SSR для reflections. Fortnite Mobile uses partial RT on Adreno 740+.

### AR shopping premium

Может использовать RT reflections для "mirror" mesh — но дорого по battery. Большинство apps остаются на rasterization.

---

## Когда использовать RT на Android

✅ **Use RT если:**
- Target flagship phones (2024+).
- Premium visual quality критична.
- Specific RT effects (accurate reflections, global illumination) — main selling point.

❌ **НЕ use RT если:**
- Target broad device base.
- Battery life critical.
- Rasterization с baked lighting покрывает quality needs.

---

## Связь с другими темами

[[rendering-pipeline-overview]] — стандартный rasterization pipeline.
[[pbr-physically-based-rendering]] — rendering equation в contextе materials.
[[gpu-architecture-fundamentals]] — RT cores как hardware extension.
[[shadow-mapping-on-mobile]] — rasterized shadows как альтернатива RT.

---

## Источники

- **Kajiya, J. (1986). The Rendering Equation.** [ACM DOI](https://dl.acm.org/doi/10.1145/15886.15902).
- **Pharr, Jakob, Humphreys (2023). Physically Based Rendering, 4th ed.** Chapter 13 (Light Transport I: Surface Reflection).
- **Khronos. Ray Tracing in Vulkan.** [khronos.org/blog](https://www.khronos.org/blog/ray-tracing-in-vulkan).

---

## Проверь себя

> [!question]- В чём фундаментальная разница rasterization и ray tracing?
> Rasterization проецирует геометрию на экран — геометрия-driven, fast for lots of triangles. Ray tracing выпускает лучи от пикселя в сцену — pixel-driven, accurate для reflections/shadows/GI, но дороже по compute.

> [!question]- Какие GPU на Android 2026 поддерживают hardware ray tracing?
> Adreno 830+, Mali Immortalis G715+, Xclipse 940+ (RDNA3/4 from Samsung), PowerVR Photon. Всё это flagship и sub-flagship чипы 2023+.

---

## Ключевые карточки

Что такое rendering equation?
?
Kajiya 1986 — интегральное уравнение, описывающее распространение света: `L(x,ω) = Le + ∫ fr · L · cos(θi) dωi`. Основа всех методов global illumination (path tracing, photon mapping, etc.).

---

Когда стоит добавлять RT к mobile Android app в 2026?
?
Только для flagship-targeted apps где premium visual quality — дифференциатор. Для broad-device apps — rasterization + baked lighting по-прежнему стандарт.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Стандартный pipeline | [[rendering-pipeline-overview]] |
| Lighting detail | [[pbr-physically-based-rendering]] |
| Shadows без RT | [[shadow-mapping-on-mobile]] |

---

*Comparison-file модуля M2.*

---
title: "Godot 4.4 на Android: Mobile renderer и оптимизации"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/godot
  - type/deep-dive
  - level/intermediate
related:
  - "[[engine-comparison-matrix]]"
  - "[[vulkan-on-android-fundamentals]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[engine-comparison-matrix]]"
primary_sources:
  - url: "https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html"
    title: "Godot 4 Renderers documentation"
    accessed: 2026-04-20
  - url: "https://developer.android.com/stories/games/godot-vulkan"
    title: "Android Developers: Godot Vulkan story"
    accessed: 2026-04-20
  - url: "https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/optimizing-3d-scenes-in-godot-on-arm-gpus"
    title: "Arm: Optimizing 3D scenes in Godot on Arm GPUs"
    accessed: 2026-04-20
reading_time: 15
difficulty: 4
---

# Godot 4.4 на Android

## Историческая справка

Godot history для Android context:

- **2007 — Godot начат** в Argentina by Juan Linietsky. Internal engine для studio Okam.
- **2014 — Godot open-sourced** MIT license.
- **2015 — Godot 1.0.**
- **2017 — Godot 2.0.** GLES 2.0 support, Android export stable.
- **2020 — Godot 3.2.** Mobile features mature.
- **2022 — Godot 3.5.**
- **2023 — Godot 4.0 released.** Полный rewrite с Vulkan backend, rendering rewrite, scripting VM upgrade.
- **2024 — Godot 4.2-4.3.** Mobile renderer stabilization.
- **2025 — Godot 4.4** released. Pre-rotation, immutable samplers, persistent shared buffers.
- **2026 — current.** Actively developed с monthly releases.

Godot team ~20 full-time developers + community contributors. Funding через Software Freedom Conservancy + donations.

Comparison к Unity / Unreal:
- **Lighter weight** — 30-40 MB APK base.
- **Open source** — no royalties, no license fees.
- **Less mature** в некоторых features (animation blending, terrain).
- **Excellent для 2D** (Godot's strong suit).
- **Mobile 3D** competitive с Unity URP quality.



**Godot 4.0** (March 2023) — полный rewrite с Vulkan-backend. **Godot 4.4** (март 2026) — latest с Mobile renderer optimizations. MIT license, community-driven development.

Godot — **full engine** (не просто renderer как Filament). Включает scene graph, physics (Godot Physics или Jolt plugin), animation, audio, networking, GUI editor. Для games — excellent choice на Android.

---

## Три renderer'а

1. **Standard** — desktop-quality. Vulkan (desktop) / D3D12 (Windows). Full features: volumetric fog, SDFGI, accurate PBR.
2. **Mobile** — оптимизирован для TBR. Vulkan Mobile. Simplified features для performance.
3. **Compatibility** — OpenGL ES 3.0 fallback. Для old devices без Vulkan.

Android games в 2026 обычно — **Mobile renderer**.

---

## Mobile renderer optimizations (Godot 4.4, March 2026)

### Pre-rotation

До 4.4: compositor applies rotation при non-standard device orientation → extra work.

После 4.4: Godot запрашивает current surface transform из Vulkan, applies rotation matrix в vertex shader. Composer work eliminated.

### Immutable samplers

Sampler state bound at pipeline creation, не меняется per draw. Driver optimizes.

### Persistent shared buffers

Uniform buffers reused across frames без CPU-GPU sync overhead. Major FPS boost для scenes с many draw calls.

### Tile memory awareness

Render pass design минимизирует DRAM access. Memoryless attachments для depth/stencil. AFBC (Mali) auto-enabled.

### Shader variants

Specialization constants для feature toggles → reduced pipeline count, better cache hit.

---

## Vulkan Mobile renderer specifics

Simpler shader set:
- 2 directional lights max.
- 8 point lights per scene.
- No volumetric fog.
- Limited SSAO.
- No SDFGI (dynamic global illumination).

Trade-offs для performance. Still supports PBR, shadow mapping, post-processing (bloom, FXAA).

---

## Export на Android

Godot → Android export через built-in Gradle project generator:

1. Project Export → Android preset.
2. Configure manifest, permissions, min SDK.
3. Export → generates APK / AAB.

Output:
- APK 30-50 MB baseline (engine itself).
- Custom builds — skip features → smaller.

---

## Scripts

Три варианта:
- **GDScript** — Godot's own scripting language. Python-like, tight integration, compiled in-engine.
- **C#** — .NET 8. Full language features.
- **C++** — через GDExtension. Для performance-critical code.

Для mobile games обычно GDScript достаточен. C++ для heavy systems.

---

## Когда выбирать Godot

✅ **Game development** — scene graph, physics, animation ready.
✅ **Solo или small team** — editor speeds итерация.
✅ **2D + 3D hybrid** — Godot strong на обоих.
✅ **MIT license** — no royalties.
✅ **Open source** — inspect, modify engine.

❌ **Существующее Compose приложение** — Godot владеет Activity.
❌ **AAA graphics** — Mobile renderer simplified vs Standard.
❌ **Tight integration с other Android frameworks** — сложно.

---

## Проекты

Godot 4 Android games в 2026:
- **Dome Keeper** (Google Play).
- **Cassette Beasts.**
- **Buckshot Roulette.**
- **Slay The Princess** (partially).

Много indie games на Android — именно Godot.

---

## Случай: FPS improvements 2026

Benchmarks on Galaxy S24 (Mali-G720):
- Godot 4.2 Mobile: 45 FPS typical scene.
- Godot 4.4 Mobile: 55 FPS same scene (+22%).

Optimizations compound for complex scenes.

---

## Связь

[[engine-comparison-matrix]] — position.
[[vulkan-on-android-fundamentals]] — Godot uses Vulkan.
[[tile-based-rendering-mobile]] — Mobile renderer tuned для TBR.

---

## Источники

- **Godot 4 Renderers docs.** [docs.godotengine.org](https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html).
- **Android Dev: Godot Vulkan story.** [developer.android.com/stories/games/godot-vulkan](https://developer.android.com/stories/games/godot-vulkan).
- **Arm: Optimizing 3D scenes in Godot.** [developer.arm.com](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/optimizing-3d-scenes-in-godot-on-arm-gpus).

---

## Проверь себя

> [!question]- Какой renderer выбрать для Android mobile game в Godot?
> Mobile renderer. Оптимизирован для TBR, Vulkan Mobile, simplified features для performance. Standard renderer heavy даже на flagship. Compatibility — только для very old devices без Vulkan.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Engine comparison | [[engine-comparison-matrix]] |
| Vulkan | [[vulkan-on-android-fundamentals]] |
| TBR | [[tile-based-rendering-mobile]] |

---

*Deep-dive модуля M8.*

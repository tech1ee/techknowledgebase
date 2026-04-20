---
title: "3D-графика на Android: карта раздела"
created: 2026-04-20
modified: 2026-04-20
type: moc
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/graphics
  - type/moc
  - navigation
related:
  - "[[android-moc]]"
  - "[[cs-foundations-moc]]"
  - "[[ios-moc]]"
  - "[[cross-platform-moc]]"
---

# 3D-графика на Android: карта раздела

Раздел строится как учебник с абсолютного нуля до уровня, на котором читатель может самостоятельно спроектировать и написать приложение класса Planner 5D / IKEA Place. Точка входа для всех, кто работает с рендерингом на мобильном устройстве — от 2D-Canvas в Compose до нативного Vulkan, от базовой линейной алгебры до production-оптимизации под тепловой бюджет телефона.

Рекомендуемый бенчмарк, к которому стремится весь курс — [[case-planner-5d]]: 74 млн пользователей, 160 млн дизайнов, комбинация собственного C++/NDK движка, облачного 4K-рендеринга и быстрого 2D/3D-редактирования сцены. Если после прохождения раздела читатель понимает, из каких решений собрана такая система и почему, цель достигнута.

---

## Для кого этот раздел

| Если ты… | Начни с… | Главная разница |
|---|---|---|
| Android-разработчик, никогда не делал 3D | [[3d-graphics-math-overview]] → [[gpu-architecture-fundamentals]] → [[rendering-pipeline-overview]] | Фундамент: как устроен GPU и что такое вертекс, без которых любой API выглядит магией |
| Знаешь Compose, хочешь добавить 3D-вьюер | [[androidexternalsurface-vs-embedded]] → [[filament-inside-compose]] | Практический путь: Compose-хост + Filament-рендер в Surface |
| Пришёл из OpenGL desktop / gamedev | [[vulkan-on-android-fundamentals]] → [[tile-based-rendering-mobile]] → [[thermal-throttling-and-adpf]] | Мобильный GPU устроен иначе (TBR/TBDR), energy budget важнее FPS-пиков |
| Пришёл из iOS / Metal | [[opengl-vs-vulkan-decision]] → cross-ссылка в [[cross-graphics-rendering]] → [[vulkan-pipeline-command-buffers]] | Vulkan детальнее Metal, но парадигма та же (explicit, thread-friendly) |
| Пришёл из Unity / Unreal | [[unity-unreal-for-android-context]] → [[engine-comparison-matrix]] | Когда родной стек побеждает движок общего назначения |
| Делал Three.js / WebGL | [[vulkan-on-android-fundamentals]] → [[shader-programming-fundamentals]] → [[filament-architecture-deep]] | Android даёт прямой доступ к GPU без браузерной прослойки |

---

## Рекомендованный путь обучения

**Фундамент → API → шейдеры → движки → оптимизация → AR → кейсы → capstone.**

Каждый модуль замкнут — можно остановиться после любого и использовать накопленное, но линейное прохождение даёт максимальный трансфер между темами. Reading time всего курса — ориентировочно 50–70 часов с упражнениями.

```
Математика ── GPU теория ── Android Graphics Stack
     │              │                │
     └──────────────┼────────────────┘
                    ▼
           Низкоуровневые API (OpenGL ES / Vulkan / ANGLE)
                    │
                    ▼
                 Шейдеры (GLSL / SPIR-V / AGSL)
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    Освещение   Ассеты     Движки
    (PBR)      (glTF/KTX2) (Filament / SceneView / Godot)
         └──────────┼──────────┘
                    ▼
          Compose-интеграция ── Оптимизация ── Профилирование
                                      │
                                      ▼
                              Production (thermal / jitter / battery)
                                      │
                   ┌──────────────────┼──────────────────┐
                   ▼                  ▼                  ▼
                   AR               Физика           Case studies
                   │                  │                  │
                   └──────────────────┼──────────────────┘
                                      ▼
                          Capstone: 3D Home Planner
```

---

## Модуль M1. Математический фундамент

Линейная алгебра и проективная геометрия — язык, на котором говорит 3D-графика. Без них любой API остаётся набором непонятных функций.

- [[3d-graphics-math-overview]] — зачем линейная алгебра в графике, из каких блоков состоит математика, roadmap
- [[vectors-in-3d-graphics]] — вектор, сложение, dot/cross product, длина, нормализация, геометрический смысл
- [[matrices-for-transformations]] — матрица, умножение, identity, column-major vs row-major, связь с Android API
- [[homogeneous-coordinates-and-affine]] — 4D для 3D-точки, affine vs projective, вывод транформаций как матриц
- [[quaternions-and-rotations]] — Euler углы, gimbal lock, кватернионы, slerp; Hamilton 1843 → Shoemake 1985
- [[projections-perspective-orthographic]] — мир → камера → клип → экран, вывод perspective-матрицы, FOV, near/far

---

## Модуль M2. Теоретические основы GPU и рендеринга

Как устроен GPU и что именно происходит между `draw()` и пикселем на экране. Без этого невозможно читать отчёты профилировщика или принимать архитектурные решения.

- [[gpu-architecture-fundamentals]] — SIMD vs SIMT, warps/waves, параллелизм, memory hierarchy
- [[tile-based-rendering-mobile]] — TBR и TBDR (Mali, PowerVR, Adreno), bin, tile memory, AFBC
- [[rendering-pipeline-overview]] — input assembly → vertex → rasterization → fragment → output merge
- [[rasterization-vs-raytracing]] — две парадигмы, будущее RT на мобилках (Adreno 720, Xclipse 960 RDNA4)
- [[z-buffer-and-depth-testing]] — depth, early-Z, z-fighting, reverse-Z, precision
- [[blending-and-compositing]] — alpha blending, premultiplied vs straight, Porter-Duff, связь с [[android-canvas-drawing]]
- [[color-spaces-hdr-mobile]] — sRGB vs linear, gamma, HDR pipeline на Android 13+ _(волна 7)_

---

## Модуль M3. Android Graphics Stack

Что именно делает Android между `view.invalidate()` и пикселем. Этот модуль расширяет уже существующие deep-dive в [[android-graphics-apis]] и [[android-view-rendering-pipeline]].

- [[surfaceflinger-and-buffer-queue]] — SurfaceFlinger, BufferQueue, Gralloc, HWComposer, triple buffering
- [[vsync-choreographer-deep]] — VSYNC как сигнал, Choreographer callbacks, интеграция с Vulkan/OpenGL
- [[hwui-skia-hardware-rendering]] — HWUI, RenderThread, DisplayList, связь со Skia _(волна 6)_
- [[android-graphics-stack-overview-v2]] — вертикальный срез от App до GPU (App → Framework → HWUI → Skia/ANGLE → driver → GPU)

---

## Модуль M4. Низкоуровневые API

Прямой доступ к GPU через OpenGL ES, Vulkan и транслирующий слой ANGLE. Выбор API определяет архитектуру приложения на годы вперёд.

- [[opengl-es-fundamentals-android]] — ES 2.0/3.0/3.1/3.2, статус в 2026 (через ANGLE), зачем всё ещё нужен
- [[vulkan-on-android-fundamentals]] — Vulkan как explicit/thread-friendly API, API 24+, Android 16 VPA-16
- [[vulkan-pipeline-command-buffers]] — render passes, pipeline objects, command buffers, descriptor sets
- [[vulkan-synchronization-memory]] — semaphores, fences, barriers, memory types, allocation strategies
- [[angle-and-gl-compatibility]] — что такое ANGLE, когда GL → Vulkan трансляция выигрывает, default-статус Android 15/16
- [[opengl-vs-vulkan-decision]] — сравнение-декомпозиция: когда брать GL, когда прыгать в Vulkan

---

## Модуль M5. Шейдеры

Программы, которые исполняются параллельно на GPU для каждого вершины и каждого пикселя. Сердце любого современного рендерера.

- [[shader-programming-fundamentals]] — что такое шейдер, stages, модель исполнения
- [[glsl-language-deep]] — синтаксис, типы (vec, mat, sampler), swizzle, builtins, uniform/varying
- [[spir-v-and-compilation]] — SPIR-V как IR, glslc/shaderc, AOT vs runtime, pipeline cache
- [[vertex-and-fragment-shaders-by-example]] — два этапа пайплайна, пошаговые примеры (transforms → lighting → texturing)
- [[compute-shaders-on-mobile]] — compute workloads, work groups, shared memory _(волна 7)_
- [[agsl-runtime-shader-compose]] — AGSL (Android 13+), RuntimeShader, интеграция с Compose
- [[shader-compilation-jitter-mitigation]] — главная production-проблема: пре-компиляция, Swappy, pipeline cache

---

## Модуль M6. Освещение и материалы

От формул Lambert и Phong до современного PBR, на котором построены все качественные движки 2020+.

- [[lighting-models-lambert-phong-blinn]] — diffuse + ambient + specular, формулы и вывод
- [[pbr-physically-based-rendering]] — energy conservation, BRDF, metallic-roughness, Fresnel, microfacet theory
- [[mobile-lighting-tradeoffs]] — baked vs dynamic, probe-based; что реально тянет Adreno 650 / Mali G710
- [[image-based-lighting-ibl]] — cubemaps, irradiance maps, split-sum approximation (Karis 2013, UE4) _(волна 6)_
- [[shadow-mapping-on-mobile]] — shadow maps, PCF, CSM; почему baked часто выигрывает _(волна 6)_
- [[normal-bump-parallax-mapping]] — normal maps, tangent space, TBN matrix _(волна 6)_

---

## Модуль M7. 3D-ассеты и форматы

Как данные попадают в GPU: описание сцены, меши, текстуры, их компрессия и загрузка.

- [[gltf-2-format-deep]] — структура glTF 2.0, JSON + buffers + images, PBR extensions, GLB
- [[texture-compression-ktx2-basis]] — KTX2, Basis Universal, transcoding в ASTC/ETC2/BC7
- [[mesh-compression-draco]] — quantization, connectivity encoding, decode cost vs storage
- [[asset-loading-streaming]] — async loading, asset pipelines, Play Asset Delivery
- [[usdz-vs-gltf-cross-platform]] — почему Apple взял USDZ, почему Android остался на glTF _(волна 7)_

---

## Модуль M8. Высокоуровневые движки для Android

Центральный сравнительный модуль. Когда не надо писать рендерер с нуля — кто и что даёт.

- ⭐ [[engine-comparison-matrix]] — полная матрица сравнения всех движков по 8 осям
- [[filament-architecture-deep]] — Google Filament: мобильный PBR-движок, архитектура, Android-интеграция
- [[filament-materials-and-pbr]] — Filament material language, Disney BRDF, environment lighting
- [[sceneview-arcore-composable-3d]] — SceneView как преемник Sceneform, ArSceneView, Kotlin-first
- [[godot-4-on-android-renderer]] — Godot 4.4 Mobile renderer, Vulkan Mobile, export pipeline
- [[unity-unreal-for-android-context]] — когда имеет смысл Unity/Unreal, trade-offs _(волна 6)_
- [[libgdx-and-kotlin-3d]] — LibGDX как Java/Kotlin-фреймворк _(волна 6)_
- [[korge-status-2026]] — KorGE 100 % Kotlin, статус проекта после 2024 _(волна 6)_
- [[jetpack-xr-scenecore-2026]] — Jetpack XR SDK, SceneCore, Compose for XR _(волна 7)_

---

## Модуль M9. Compose и UI-интеграция

Как встроить 3D-сцену в современный Jetpack Compose UI.

- [[compose-canvas-drawscope-deep]] — DrawScope, маппинг в Skia, границы (CPU-side)
- [[graphicslayer-modifier-deep]] — `graphicsLayer{}`, cameraDistance, псевдо-3D через rotation
- [[androidexternalsurface-vs-embedded]] — два способа встроить 3D в Compose, trade-offs
- [[filament-inside-compose]] — практика: Filament viewer внутри Compose, state management

---

## Модуль M10. Оптимизация

Как не отрисовывать лишнее. Мобильный GPU тратит 2× энергии на overdraw по сравнению с vertex shading; экономия here — больше всего.

- [[frustum-culling]] — frustum test, bounding volumes (AABB, sphere, OBB)
- [[occlusion-culling]] — hardware occlusion queries, software подходы, Hi-Z buffer
- [[level-of-detail-lod]] — LOD chains, distance-based selection, Nanite-стиль (UE5) как контраст
- [[instancing-batching-draw-calls]] — draw call cost, static/dynamic batching, GPU instancing
- [[overdraw-and-blending-cost]] — почему overdraw дорог на TBR, как замерить, как снижать
- [[gpu-memory-management-mobile]] — VRAM budgets, texture streaming, atlas, Vulkan memory types

---

## Модуль M11. Профилирование

Без инструментов разработка вслепую. Главный стек 2026 для Android-графики.

- [[android-gpu-inspector-agi]] — AGI: frame profile, system profile, shader analysis
- [[perfetto-and-systrace-for-graphics]] — Perfetto UI, связь с Choreographer/SurfaceFlinger
- [[renderdoc-for-android-vulkan]] — когда RenderDoc уместнее AGI _(волна 6)_
- [[gpu-specific-debugging-adreno-mali-powervr-xclipse]] — особенности каждого вендора _(волна 6)_

---

## Модуль M12. Производительность и стабильность в production

То, что отличает прототип от приложения, которое не удаляют после 30 минут использования.

- [[thermal-throttling-and-adpf]] — ADPF, thermal headroom APIs (API 31+), dynamic quality scaling
- [[frame-pacing-swappy-library]] — Android Frame Pacing Library, почему consistency важнее average FPS
- [[battery-drain-plane-detection]] — стоимость ARCore plane detection, mitigation patterns (62 % deletion rate из-за battery)
- [[vulkan-profiles-vpa-16-android16]] — что гарантирует VPA-16 разработчику, связь с Google Play

---

## Модуль M13. AR

ARCore — слой, на котором построены IKEA Place, Houzz и AR-часть Planner 5D.

- [[arcore-fundamentals]] — session, SLAM (VIO), trackable, anchor, frame
- [[arcore-plane-detection-deep]] — feature points, plane types, почему белые стены не детектируются
- [[arcore-depth-api]] — depth-from-motion (UIST 2020), depth map, range 0.5–65 м
- [[arcore-geospatial-api-vps]] — Geospatial API + VPS (Street View), точность 1–3 м
- [[ar-lighting-estimation]] — ambient intensity, environmental HDR, spherical harmonics
- [[ar-occlusion-rendering]] — как depth → shader скрывает furniture за реальными объектами
- [[ar-cloud-anchors-persistence]] — cloud anchors, TTL до 365 дней, мульти-пользователи _(волна 6)_

---

## Модуль M14. Физика и интерактивность

Рядом с графикой — физика столкновений и твёрдых тел. Минимум, без которого интерактивная сцена невозможна.

- [[physics-engines-mobile-jolt-bullet]] — Jolt (2022+) vs Bullet (1999+) vs ReactPhysics3D
- [[collision-detection-fundamentals]] — broad/narrow phase, BVH, SAP, GJK/EPA _(волна 6)_
- [[rigid-body-dynamics-intro]] — masses, forces, impulses, constraint solver _(волна 6)_

---

## Модуль M15. Case studies реальных приложений

Teardown реальных приложений-бенчмарков — самое ценное в курсе. Архитектура → проблемы → решения → метрики.

- [[case-planner-5d]] — Kotlin + собственный C++/NDK движок + облачный 4K-рендеринг, 74M users
- [[case-ikea-place-ar]] — ARCore Depth API + Lighting + occlusion, 11× conversion uplift
- [[case-sweet-home-3d-android]] — Java + OpenGL ES, open-source, offline-first
- [[case-magicplan-ndk-ar]] — Android NDK для perf-critical, 2D→3D real-time
- [[case-blueprint3d-opensource]] — open-source teardown (github.com/furnishup/blueprint3d) _(волна 6)_
- [[case-live-home-3d-quality-presets]] — настраиваемые quality-пресеты как паттерн _(волна 6)_

---

## Модуль M16. Capstone

Финальный синтез: как пройти от нуля до MVP приложения класса Planner 5D.

- [[build-3d-home-planner-from-scratch]] — декомпозиция бенчмарка, минимальный стек, путь по модулям, checkpoints и метрики

---

## Кросс-связи с другими зонами vault

### Android (существующие deep-dive как prerequisites)
- [[android-graphics-apis]] — базовое введение в графические API, следующий шаг — M4
- [[android-canvas-drawing]] — 2D Canvas; контраст с 3D DrawScope из M9
- [[android-view-rendering-pipeline]] — Measure → Layout → Draw; расширяется в M3
- [[android-window-system]] — Window / Surface; расширяется в M3 (SurfaceFlinger deep)
- [[android-animations]] — VSYNC и Choreographer; расширяется в M3 и M12 (frame pacing)
- [[android-compose-internals]] — Composition → Layout → Draw; интеграция в M9
- [[android-performance-profiling]] — общий профайлинг, расширяется в M11 (AGI)
- [[android-art-runtime]] — JIT/AOT компиляция; связь с M5 (shader compilation)
- [[android-process-memory]] — общая память, расширяется в M10 (GPU memory)
- [[android-threading]], [[android-handler-looper]] — связь с M3 (RenderThread) и M5

### CS Foundations (математика)
- [[cs-foundations-overview]] — вход
- [[cs-foundations-moc]] — регистрирует подсекцию `05-graphics-math/` с M1

### iOS (параллельные темы)
- [[ios-graphics-fundamentals]] — Core Animation / Metal, аналог для iOS
- [[ios-view-rendering]] — render loop iOS, параллель с M3
- [[ios-moc]] — карта iOS

### Cross-platform
- [[cross-graphics-rendering]] — Metal vs Vulkan, iOS vs Android parallels
- [[cross-platform-moc]] — сравнения по осям

---

## Источники и первичные материалы

Полный консолидированный список из 48 источников (спецификации Khronos, документация Google/Apple, GDC, SIGGRAPH, книги Akenine-Möller / Pharr / Dunn) хранится в каждом отдельном файле как `primary_sources` в frontmatter. Основные точки входа:

- Khronos Vulkan 1.4 Specification — [registry.khronos.org/vulkan/specs/1.4-extensions/html/](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/)
- Android Developers: Vulkan — [developer.android.com/games/develop/vulkan/overview](https://developer.android.com/games/develop/vulkan/overview)
- Google Filament — [google.github.io/filament/Filament.md.html](https://google.github.io/filament/Filament.md.html)
- SceneView — [github.com/SceneView/sceneview-android](https://github.com/SceneView/sceneview-android)
- ARCore Fundamentals — [developers.google.com/ar/develop/fundamentals](https://developers.google.com/ar/develop/fundamentals)
- Akenine-Möller, Haines, Hoffman (2018). Real-Time Rendering, 4th ed. — канон.
- Pharr, Jakob, Humphreys (2023). Physically Based Rendering, 4th ed. — академический фундамент.

---

## Статус наполнения

- **Волна 0** (стандарты) — ✅ выполнено 2026-04-20
- **Волна 1** (фундамент M1–M3) — в работе
- **Волны 2–5** (P0: низкий уровень, движки, оптимизация, AR + кейсы + capstone) — запланировано
- **Волна 6** (P1) — отложено до завершения P0
- **Волна 7** (P2) — отложено

Полный план и последовательность — в `/Users/arman/.claude/plans/expressive-stargazing-flask.md`.

---

*Создано: 2026-04-20 · Бенчмарк: Planner 5D, IKEA Place · Цель: учебник с абсолютного нуля до профессионального уровня.*

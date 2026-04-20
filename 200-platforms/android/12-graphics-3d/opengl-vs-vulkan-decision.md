---
title: "OpenGL ES vs Vulkan на Android 2026: decision tree"
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
  - "[[opengl-es-fundamentals-android]]"
  - "[[vulkan-on-android-fundamentals]]"
  - "[[angle-and-gl-compatibility]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[opengl-es-fundamentals-android]]"
  - "[[vulkan-on-android-fundamentals]]"
reading_time: 8
difficulty: 3
---

# OpenGL ES vs Vulkan: decision tree

Прямой comparison и decision tree для 2026.

## Быстрый совет

- **Новые 3D проекты, 2026+:** Vulkan.
- **Maintenance существующего GL ES:** оставить GL (возможно через ANGLE).
- **Простые 2D:** Compose / Canvas, ни GL ни Vulkan напрямую.
- **Cross-platform без iOS:** Vulkan.
- **Cross-platform с iOS:** GL ES (common) или Vulkan + MoltenVK.

## Decision tree

```
Тип проекта?
├── Игра / AAA-graphics app
│   ├── Новый проект → Vulkan
│   └── Существующий GL → migrate если scale большой, иначе оставить
│
├── Non-game 3D (interior design, AR, viewer)
│   ├── Через movement (Filament, SceneView) → движок выбирает
│   └── Direct API → Vulkan для новых
│
├── Простая UI с 2D canvas
│   ├── Compose / View System → не трогайте GL/Vulkan
│   └── Custom particles / effects → Compose + AGSL
│
├── Education / prototyping
│   └── GL ES — проще для первых шагов
│
└── Legacy codebase с GL
    └── Оставить GL, ANGLE автоматически даст Vulkan performance
```

---

## Подробное сравнение

| Критерий | OpenGL ES 3.2 | Vulkan 1.3 |
|---|---|---|
| **API complexity** | Medium | High |
| **Learning curve** | 1 week до productive | 1-3 months до productive |
| **Performance ceiling** | Medium | High (20-30% CPU savings) |
| **Battery on mobile** | OK | Better (meno CPU work) |
| **Multi-threaded rendering** | Hard (context per thread) | Easy (parallel CB recording) |
| **Driver validation overhead** | Per-call | One-time (pipeline) |
| **Explicit synchronization** | No (driver) | Yes (you) |
| **Explicit memory management** | No | Yes |
| **Tile-based optimization** | Limited | Full control (render pass, transient attachments) |
| **Modern features (compute, RT)** | Compute since 3.1, no RT | Full |
| **Cross-platform** | Everywhere kromě iOS 16+ | Everywhere (MoltenVK for iOS) |
| **Kotlin/Java wrapper** | `GLES30` class | NDK + JNI обычно |
| **Migration from desktop GL** | Easier | Harder |
| **Debug tools** | Qualcomm / ARM specific | AGI, RenderDoc, Validation Layers |

---

## Когда GL ещё оправдан в 2026

1. **Maintenance cost.** Переписать existing GL → Vulkan = months. Если не критично — оставить.
2. **Team skill.** No Vulkan expertise, нет бюджета на learning → GL.
3. **Simple 2D.** Rudimentary 2D через GL = works. Vulkan overkill.
4. **Education.** Первая работа с 3D — GL проще обучиться.

## Когда переходить на Vulkan

1. **CPU-bound на mobile.** Many draw calls, state changes. Vulkan saves.
2. **Multi-threading.** Games с parallel CB recording.
3. **Advanced features.** Mesh shading, ray tracing, HDR.
4. **Long-term.** Новый long-lived проект. GL ES будет maintained, но новые features только Vulkan.

---

## Hybrid подход

Некоторые apps используют Vulkan для rendering + GL ES для legacy modules. Возможно через EGL image sharing. Редко оправданно.

Проще выбрать одно и держаться.

---

## Источники

- **Android Developers: Vulkan vs OpenGL.** [developer.android.com/games/develop/vulkan](https://developer.android.com/games/develop/vulkan/overview).
- **Khronos. Vulkan guide.** [vulkan-tutorial.com](https://vulkan-tutorial.com/).

---

## Проверь себя

> [!question]- Игра с 2000 objects per frame — какой API?
> Vulkan. 2000+ draw calls с state changes — typical scenario where Vulkan CPU savings noticeable. Plus multi-threaded CB recording ускорит на modern 8-core mobile CPUs.

> [!question]- Простое 2D app с blur effect?
> Ни то, ни другое напрямую. Compose с AGSL shader. GL/Vulkan overkill для 2D.

---

## Куда дальше

| Направление | Куда |
|---|---|
| GL detail | [[opengl-es-fundamentals-android]] |
| Vulkan detail | [[vulkan-on-android-fundamentals]] |
| ANGLE | [[angle-and-gl-compatibility]] |

---

*Comparison модуля M4.*

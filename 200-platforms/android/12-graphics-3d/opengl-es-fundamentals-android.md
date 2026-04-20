---
title: "OpenGL ES на Android 2026: статус, версии, ANGLE"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/opengl-es
  - type/deep-dive
  - level/intermediate
related:
  - "[[vulkan-on-android-fundamentals]]"
  - "[[angle-and-gl-compatibility]]"
  - "[[opengl-vs-vulkan-decision]]"
  - "[[android-graphics-apis]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[rendering-pipeline-overview]]"
primary_sources:
  - url: "https://registry.khronos.org/OpenGL/specs/es/"
    title: "Khronos OpenGL ES Specifications"
    accessed: 2026-04-20
  - url: "https://developer.android.com/guide/topics/graphics/opengl"
    title: "Android Developers: OpenGL ES"
    accessed: 2026-04-20
reading_time: 15
difficulty: 3
---

# OpenGL ES на Android 2026

OpenGL ES дебютировал в Android 1.0 (2008) и был единственным way 3D до Android 7.0 (2016) when Vulkan arrived. В 2026 году OpenGL ES — **legacy API**, всё ещё повсеместно поддерживаемый, но на новых устройствах работающий **через ANGLE translation layer** (OpenGL ES → Vulkan). Новые проекты должны использовать Vulkan; OpenGL ES остаётся для: maintenance существующих apps, простых 2D через GL, education.

---

## Зачем это знать

**Для maintenance.** Существующий OpenGL ES code base не нужно переписывать. Как минимум знать API structure и его limitations.

**Для education.** GL ES — проще чем Vulkan, хороший первый шаг в understanding graphics pipeline.

**Для ANGLE context.** В 2026 Google делает ANGLE default GL driver на Android. Your GL code run через Vulkan underneath — understanding помогает.

---

## Версии и support

| Версия | Год | Android API level | Features |
|---|---|---|---|
| ES 1.0 | 2003 | 4+ | Fixed-function pipeline (legacy) |
| ES 2.0 | 2007 | 8+ | Programmable shaders (GLSL ES 1.00) |
| ES 3.0 | 2012 | 18+ | ETC2 textures, instancing, MRT, transform feedback |
| ES 3.1 | 2014 | 21+ | Compute shaders, indirect draw, stencil textures |
| ES 3.2 | 2015 | 24+ | Tessellation, geometry shaders, ASTC compression |

Android coverage (April 2026):
- ES 2.0: ~99% devices.
- ES 3.0: ~98%.
- ES 3.1: ~95%.
- ES 3.2: ~85% (flagship + mid-range новые).

---

## Базовая структура

### EGL — context setup

EGL (Embedded Graphics Library) — platform-specific layer для создания GL context:

```java
// EGL initialization
EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);
EGL14.eglInitialize(display, version, 0, version, 1);
EGL14.eglChooseConfig(display, configAttribs, 0, configs, 0, 1, numConfigs, 0);
EGL14.eglCreateContext(display, config, EGL14.EGL_NO_CONTEXT, contextAttribs, 0);
EGL14.eglCreateWindowSurface(display, config, surfaceView.surface, null, 0);
EGL14.eglMakeCurrent(display, surface, surface, context);
```

### Rendering loop

```java
// In GL thread (GLSurfaceView.Renderer)
override fun onDrawFrame(gl: GL10) {
    GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT or GLES30.GL_DEPTH_BUFFER_BIT)
    GLES30.glUseProgram(shaderProgram)
    GLES30.glBindBuffer(GLES30.GL_ARRAY_BUFFER, vertexBuffer)
    GLES30.glDrawElements(GLES30.GL_TRIANGLES, indexCount, GLES30.GL_UNSIGNED_INT, 0)
    // eglSwapBuffers called by GLSurfaceView
}
```

### State machine

OpenGL ES — state machine: bind buffer → bind program → draw. State накапливается, последующие calls применяют его.

**Проблема state machine:** hidden dependencies. Changing global state breaks другие код. Source багов в large GL codebases.

---

## Различия с Vulkan

| Аспект | OpenGL ES | Vulkan |
|---|---|---|
| State | Global mutable | Pipeline state object (immutable) |
| Memory | Driver-managed | App-managed |
| Sync | Implicit (driver) | Explicit (semaphores, fences, barriers) |
| Command recording | Immediate | Pre-recorded command buffers |
| Multi-threading | Hard (context per thread) | Easy (parallel CB recording) |
| Shader language | GLSL ES | SPIR-V (GLSL → SPIR-V compile) |
| Driver overhead | Высокий | Низкий |
| Learning curve | Низкая | Высокая |

---

## ANGLE в 2026

[Google ANGLE](https://chromium.googlesource.com/angle/angle) — translation layer. Реализует OpenGL ES API, generates Vulkan (или D3D on Windows) под капотом. В Android 15 стал опциональным GL driver, в Android 16 — default на many devices.

**Benefits:**
- Unified behavior across vendors (ANGLE fixes vendor GL driver bugs).
- Better performance в some cases (ANGLE optimizes for Vulkan).
- Google maintains ANGLE — быстрее фиксы чем vendor drivers.

**Для разработчика:**
- GL code работает как раньше.
- Performance может немного измениться (обычно better).
- Some extensions может не быть (ANGLE implements core + popular).

---

## Когда использовать GL ES в 2026

✅ **Maintenance** existing GL code.
✅ **Education** — learning graphics pipeline.
✅ **Quick прototypes** с GLSurfaceView.
✅ **Simple 2D с blending** — overkill new Vulkan.

❌ **New 3D apps** — Vulkan.
❌ **Performance-critical** — Vulkan explicit control.
❌ **Multi-threaded rendering** — Vulkan.

---

## Source examples

Большинство existing tutorials для Android 3D используют GL ES 2.0/3.0. Репо examples:
- [android-opengl-tutorials](https://github.com/crazii/android-opengl-examples).
- Google samples в AOSP (`development/samples/Graphics`).

---

## Источники

- **Khronos OpenGL ES Specifications.** [registry.khronos.org/OpenGL/specs/es/](https://registry.khronos.org/OpenGL/specs/es/).
- **Android Developers: OpenGL ES.** [developer.android.com/guide/topics/graphics/opengl](https://developer.android.com/guide/topics/graphics/opengl).
- **Munshi, A., Ginsburg, D., Shreiner, D. (2014). OpenGL ES 3.0 Programming Guide.** Канонический учебник.

---

## Проверь себя

> [!question]- Какая версия OpenGL ES даёт compute shaders?
> OpenGL ES 3.1 (2014, Android API 21+). Раньше compute делался только через OpenCL (отдельный API). 3.1+ брendeninterGL compute семантически integrated.

> [!question]- Что такое ANGLE?
> Google's translation layer from OpenGL ES → Vulkan (or D3D on Windows). В 2026 default GL driver на many Android devices. Your GL code runs поверх Vulkan.

---

## Ключевые карточки

Какая OpenGL ES версия была первой с programmable shaders?
?
ES 2.0 (2007). Убрала fixed-function pipeline. GLSL ES 1.00 для shaders.

---

Зачем ANGLE?
?
Unified GL implementation — fixes vendor bugs, consistent behavior, maintained by Google. Runs GL commands via Vulkan для современной производительности.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Vulkan fundamentals | [[vulkan-on-android-fundamentals]] |
| ANGLE detail | [[angle-and-gl-compatibility]] |
| Decision | [[opengl-vs-vulkan-decision]] |

---

*Deep-dive модуля M4.*

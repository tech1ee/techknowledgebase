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
  - url: "https://chromium.googlesource.com/angle/angle"
    title: "Google ANGLE project"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/OpenGL-Refpages/es3.2/"
    title: "OpenGL ES 3.2 Reference Pages"
    accessed: 2026-04-20
reading_time: 22
difficulty: 3
---

# OpenGL ES на Android 2026

OpenGL ES дебютировал в Android 1.0 (2008) и был единственным путём к 3D-графике до Android 7.0 (2016), когда пришёл Vulkan. В 2026 году OpenGL ES — **legacy API**, всё ещё повсеместно поддерживаемый, но на новых устройствах работающий **через ANGLE translation layer** (OpenGL ES → Vulkan). Новые проекты должны использовать Vulkan; OpenGL ES остаётся для: maintenance существующих apps, простых 2D через GL, education. Понимание GL ES важно потому, что огромная codebase — существующие apps, tutorials, библиотеки — написана на нём.

---

## Зачем это знать

**Первое — maintenance.** Существующий OpenGL ES code base не нужно переписывать на Vulkan если он работает. Нужно понимать API structure, его limitations, и что драйвер делает под капотом (особенно в эпоху ANGLE).

**Второе — education.** OpenGL ES значительно проще чем Vulkan, хороший первый шаг в понимание graphics pipeline. Многие concepts переносимы (shaders, uniforms, vertex buffers) — GLSL отличается от SPIR-V но одна и та же ментальная модель.

**Третье — ANGLE context.** В 2026 Google делает ANGLE default GL driver на Android (уже default на Pixel phones с Android 15+). Your GL code runs через Vulkan underneath — understanding что это значит для perf.

**Четвёртое — interop.** Некоторые Android APIs всё ещё GL-based: GLSurfaceView, old MediaCodec tutorials, legacy game engines. Взаимодействие требует GL knowledge.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[rendering-pipeline-overview]] | Pipeline stages — shared с GL ES |
| [[gpu-architecture-fundamentals]] | Shader cores — общие с Vulkan |

---

## Терминология

| Термин | Что |
|---|---|
| OpenGL ES | Khronos mobile graphics API — subset of OpenGL desktop |
| EGL | Embedded Graphics Library — platform-specific context создание |
| GL Context | Session state (shaders, buffers, textures bindings) |
| GLSL ES | Shader language subset of GLSL |
| VBO (Vertex Buffer Object) | GPU buffer для vertex data |
| IBO / EBO | Index/Element buffer для vertex indices |
| FBO (Framebuffer Object) | Custom rendering target |
| Texture unit | Slot для binding texture (typically 16-32 units) |
| Uniform | Constant value passed from app to shader |
| Varying / in/out | Data passed между shader stages |
| ANGLE | Google's OpenGL ES → Vulkan (D3D on Windows) translation layer |

---

## Историческая справка

OpenGL ES эволюционировал параллельно с desktop OpenGL, но как «mobile subset» с 2003:

- **2003 — OpenGL ES 1.0.** Основан на OpenGL 1.3. Fixed-function pipeline (матрицы, lighting — всё через GL commands, no shaders).
- **2004 — ES 1.1.** Добавлены vertex buffer objects, multi-texturing.
- **2007 — ES 2.0.** Complete break с 1.x: programmable shaders only (GLSL ES 1.00). Android 2.2 (2010) был первый с ES 2.0 support.
- **2010 — Apple iPhone 4, Samsung Galaxy S.** ES 2.0 becomes standard на mobile.
- **2012 — ES 3.0.** ETC2 textures (standard compressed format), instancing (`glDrawArraysInstanced`), multiple render targets (MRT), transform feedback.
- **2014 — ES 3.1.** Compute shaders (mobile compute era начинается), indirect draws.
- **2015 — ES 3.2.** Tessellation, geometry shaders (редко используются на mobile), ASTC compression mandatory, advanced blending modes.
- **2016 — Vulkan 1.0 release.** Khronos announces OpenGL ES will be maintained но not actively developed.
- **2018 — Google pushes Vulkan adoption.** Android O improves Vulkan driver quality.
- **2020 — ANGLE начинает working на Android.** Initially для Chrome, then general.
- **2023 — ANGLE experimental in Android settings.** Developer preview.
- **2024 — Android 15: ANGLE default на Pixel devices.**
- **2026 — ANGLE default на large portion of Android 16 devices.**

OpenGL ES 3.2 — последняя major version. Дальнейший development — только minor corrections. New features идут через Vulkan.

---

## Версии и support в 2026

| Версия | Год | Android API level | Features |
|---|---|---|---|
| ES 1.0 | 2003 | 4+ | Fixed-function pipeline (legacy, deprecated) |
| ES 2.0 | 2007 | 8+ | Programmable shaders (GLSL ES 1.00) |
| ES 3.0 | 2012 | 18+ | ETC2 textures, instancing, MRT, transform feedback |
| ES 3.1 | 2014 | 21+ | Compute shaders, indirect draw, stencil textures |
| ES 3.2 | 2015 | 24+ | Tessellation, geometry shaders, ASTC compression |

Android coverage (April 2026):
- ES 2.0: ~99% devices.
- ES 3.0: ~98%.
- ES 3.1: ~95%.
- ES 3.2: ~85% (flagship + mid-range новые).

**Рекомендация для new projects:** целиться на ES 3.2 минимум, потому что ES 1.x deprecated практически, а 2.0-3.1 имеют фрагментированную feature support.

---

## Базовая структура — EGL + GL

OpenGL ES — **state machine**. В отличие от Vulkan (explicit state objects), GL накапливает state через calls. Before drawing:
1. Bind shader program (`glUseProgram`).
2. Bind vertex buffers (`glBindBuffer`).
3. Configure vertex attributes (`glVertexAttribPointer`, `glEnableVertexAttribArray`).
4. Set uniforms (`glUniform*`).
5. Bind textures (`glActiveTexture`, `glBindTexture`).
6. Issue draw (`glDrawArrays`, `glDrawElements`).

Каждый step changes global state. Последующие draws inherit state если не changed.

### EGL — context setup

EGL — platform abstraction. Создаёт GL context связанный с Android Surface (окно / SurfaceView / TextureView).

```java
// EGL initialization
EGLDisplay display = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);
EGL14.eglInitialize(display, version, 0, version, 1);

// Choose config (color depth, alpha, depth buffer, etc.)
int[] configAttribs = {
    EGL14.EGL_RED_SIZE, 8,
    EGL14.EGL_GREEN_SIZE, 8,
    EGL14.EGL_BLUE_SIZE, 8,
    EGL14.EGL_ALPHA_SIZE, 8,
    EGL14.EGL_DEPTH_SIZE, 24,
    EGL14.EGL_RENDERABLE_TYPE, EGL14.EGL_OPENGL_ES3_BIT,
    EGL14.EGL_NONE
};
EGLConfig[] configs = new EGLConfig[1];
EGL14.eglChooseConfig(display, configAttribs, 0, configs, 0, 1, numConfigs, 0);

// Create context (ES 3.2)
int[] contextAttribs = { EGL14.EGL_CONTEXT_CLIENT_VERSION, 3, EGL14.EGL_NONE };
EGLContext context = EGL14.eglCreateContext(display, configs[0], EGL14.EGL_NO_CONTEXT, contextAttribs, 0);

// Create surface связан с Android Surface
EGLSurface surface = EGL14.eglCreateWindowSurface(display, configs[0], androidSurface, null, 0);

// Make current
EGL14.eglMakeCurrent(display, surface, surface, context);
```

После `eglMakeCurrent` — GL commands работают. Один context бывший «current» per thread.

### Rendering loop

```java
// In GL thread (GLSurfaceView.Renderer)
override fun onDrawFrame(gl: GL10) {
    GLES30.glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT or GLES30.GL_DEPTH_BUFFER_BIT)
    
    GLES30.glUseProgram(shaderProgram)
    GLES30.glUniformMatrix4fv(mvpLocation, 1, false, mvpMatrix, 0)
    
    GLES30.glBindBuffer(GLES30.GL_ARRAY_BUFFER, vertexBuffer)
    GLES30.glBindBuffer(GLES30.GL_ELEMENT_ARRAY_BUFFER, indexBuffer)
    
    GLES30.glVertexAttribPointer(0, 3, GLES30.GL_FLOAT, false, 0, 0)
    GLES30.glEnableVertexAttribArray(0)
    
    GLES30.glActiveTexture(GLES30.GL_TEXTURE0)
    GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, texture)
    GLES30.glUniform1i(textureLocation, 0)
    
    GLES30.glDrawElements(GLES30.GL_TRIANGLES, indexCount, GLES30.GL_UNSIGNED_INT, 0)
    
    // eglSwapBuffers called by GLSurfaceView automatically
}
```

---

## Ключевые GL ES API categories

### Shaders и programs

```java
int vertexShader = GLES30.glCreateShader(GLES30.GL_VERTEX_SHADER);
GLES30.glShaderSource(vertexShader, vertexSource);
GLES30.glCompileShader(vertexShader);

int fragShader = GLES30.glCreateShader(GLES30.GL_FRAGMENT_SHADER);
GLES30.glShaderSource(fragShader, fragSource);
GLES30.glCompileShader(fragShader);

int program = GLES30.glCreateProgram();
GLES30.glAttachShader(program, vertexShader);
GLES30.glAttachShader(program, fragShader);
GLES30.glLinkProgram(program);

int mvpLocation = GLES30.glGetUniformLocation(program, "u_MVP");
```

### Buffers

```java
int[] buffers = new int[1];
GLES30.glGenBuffers(1, buffers, 0);
GLES30.glBindBuffer(GLES30.GL_ARRAY_BUFFER, buffers[0]);
GLES30.glBufferData(GLES30.GL_ARRAY_BUFFER, data.length * 4, 
                    FloatBuffer.wrap(data), GLES30.GL_STATIC_DRAW);
```

### Textures

```java
int[] textures = new int[1];
GLES30.glGenTextures(1, textures, 0);
GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, textures[0]);
GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D, GLES30.GL_TEXTURE_MIN_FILTER, GLES30.GL_LINEAR);
GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D, GLES30.GL_TEXTURE_MAG_FILTER, GLES30.GL_LINEAR);
GLES30.glTexImage2D(GLES30.GL_TEXTURE_2D, 0, GLES30.GL_RGBA8, width, height, 0,
                     GLES30.GL_RGBA, GLES30.GL_UNSIGNED_BYTE, bitmap);
GLES30.glGenerateMipmap(GLES30.GL_TEXTURE_2D);
```

### FBOs (render to texture)

```java
int[] fbo = new int[1];
GLES30.glGenFramebuffers(1, fbo, 0);
GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER, fbo[0]);
GLES30.glFramebufferTexture2D(GLES30.GL_FRAMEBUFFER, GLES30.GL_COLOR_ATTACHMENT0,
                                GLES30.GL_TEXTURE_2D, targetTexture, 0);
// Check completeness
int status = GLES30.glCheckFramebufferStatus(GLES30.GL_FRAMEBUFFER);
```

---

## State machine — плюсы и минусы

### Проблема state machine

Hidden dependencies: одна часть кода меняет glBindTexture(GL_TEXTURE_2D, X), другая часть предполагает texture Y bound. Результат — silent incorrect rendering.

Typical bugs:
- Rendering "checkerboard" pattern = last-bound texture вместо expected.
- Z-fighting или random blending = leftover state из предыдущего pass.
- Multi-threaded crashes = GL context shared unsafely.

### VAO mitigation (ES 3.0+)

Vertex Array Object снимает часть проблемы — groups vertex state in one object:

```java
int[] vao = new int[1];
GLES30.glGenVertexArrays(1, vao, 0);
GLES30.glBindVertexArray(vao[0]);

// Configure all vertex attribs
GLES30.glBindBuffer(...);
GLES30.glVertexAttribPointer(...);
GLES30.glEnableVertexAttribArray(...);

// При drawing просто bind VAO
GLES30.glBindVertexArray(vao[0]);
GLES30.glDrawElements(...);
```

Reduces per-draw state changes. Important для performance.

### Debug через KHR_debug (ES 3.2)

`glDebugMessageCallback` — callback при driver warnings/errors:
```java
GLES32.glDebugMessageCallback(KHRDebugCallback { source, type, id, severity, length, message, userParam ->
    Log.e("GL", "$source/$type: $message")
})
```

Помогает найти bugs (incorrect state, deprecated features, performance warnings).

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
| Validation | Runtime only | Static + Runtime |
| TBR awareness | Driver infers | Explicit render passes |
| Compute integration | Separate context | Unified с graphics |

---

## ANGLE в 2026

[Google ANGLE](https://chromium.googlesource.com/angle/angle) — translation layer. Реализует OpenGL ES API, generates Vulkan (или D3D on Windows, Metal on iOS/Mac) под капотом. В Android 15 стал опциональным GL driver, в Android 16 — default на many devices.

**Benefits:**
- Unified behavior across vendors — ANGLE fixes vendor GL driver bugs.
- Better performance в some cases — ANGLE optimizes for Vulkan.
- Google maintains ANGLE — быстрее фиксы чем vendor drivers.
- Possible deprecate vendor GL drivers в long term.

**Для разработчика:**
- GL code работает как раньше.
- Performance может немного измениться (обычно better).
- Some extensions может не быть — ANGLE implements core + popular, не все vendor-specific.

Проверить running через ANGLE:
```java
String renderer = GLES20.glGetString(GLES20.GL_RENDERER);
// "ANGLE (Adreno 740) Vulkan 1.3 ..." = running under ANGLE
```

См. [[angle-and-gl-compatibility]] для deep-dive.

---

## Когда использовать GL ES в 2026

✅ **Maintenance** existing GL code.
✅ **Education** — learning graphics pipeline.
✅ **Quick прототипы** с GLSurfaceView.
✅ **Simple 2D с blending** — overkill new Vulkan setup.
✅ **Interop с existing Android APIs** (SurfaceTexture, MediaCodec tutorials).

❌ **New 3D apps** — Vulkan.
❌ **Performance-critical** — Vulkan explicit control.
❌ **Multi-threaded rendering** — Vulkan.
❌ **Advanced features** (RT, mesh shaders) — not in ES.

---

## Source examples и ресурсы

Огромная существующая codebase использует GL ES. Good starting points:
- [Android-SampleGraphics](https://github.com/android/ndk-samples). AOSP samples.
- [LearnOpenGLES](https://learnopengl.com/) — desktop GL но концепты transfer.
- [ChatGPT GLSurfaceView tutorials](https://developer.android.com/guide/topics/graphics/opengl) — official Android.

Books:
- Munshi, A., Ginsburg, D., Shreiner, D. (2014). OpenGL ES 3.0 Programming Guide.
- Ginsburg, D., Purnomo, B. (2014). OpenGL ES 3.0 Programming Guide, 2nd ed.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| GL ES медленный на mobile | На modern drivers (особенно ANGLE) — competitive. Issue — high driver overhead для many draw calls |
| GL ES deprecated | Maintained но not actively developed. Still first-class API |
| Нужно переписывать GL код на Vulkan | Зависит. Если работает — not urgent. Profile first |
| ANGLE — только для Chrome | ANGLE general Android solution, default на Pixel с Android 15+ |
| GL ES 1.x — живой | Deprecated практически. Fixed-function only, no mobile flagship supports fully |

---

## Подводные камни

### Ошибка 1: GL context per thread

**Как избежать:** один GL context per thread. Для multi-threaded rendering — use Vulkan. Альтернативы: shared contexts (complex, error-prone) или render на main thread.

### Ошибка 2: Leaky state

**Как избежать:** always reset state before draw (bind correct program, buffers, textures). Use VAOs.

### Ошибка 3: Игнорирование EGL errors

**Как избежать:** check `eglGetError()` после critical calls. Wrong config может silently fail.

### Ошибка 4: Wrong buffer usage flags

**Как избежать:** `GL_STATIC_DRAW` для static data, `GL_DYNAMIC_DRAW` для changing, `GL_STREAM_DRAW` для per-frame. Wrong hint — driver использует less optimal memory type.

### Ошибка 5: Too many state changes

**Как избежать:** sort draws по shader program, texture. Batch similar draws together.

---

## Связь с другими темами

[[vulkan-on-android-fundamentals]] — modern replacement.
[[angle-and-gl-compatibility]] — ANGLE translation layer.
[[opengl-vs-vulkan-decision]] — decision framework.
[[glsl-language-deep]] — GLSL shader language.
[[shader-programming-fundamentals]] — shader basics (GL ES и Vulkan share concepts).
[[rendering-pipeline-overview]] — pipeline stages.
[[android-graphics-apis]] — existing overview.

---

## Источники

- **Khronos OpenGL ES Specifications.** [registry.khronos.org/OpenGL/specs/es/](https://registry.khronos.org/OpenGL/specs/es/).
- **Android Developers: OpenGL ES.** [developer.android.com/guide/topics/graphics/opengl](https://developer.android.com/guide/topics/graphics/opengl).
- **Munshi, A., Ginsburg, D., Shreiner, D. (2014). OpenGL ES 3.0 Programming Guide.** Канонический учебник.
- **ANGLE source code.** [chromium.googlesource.com/angle/angle](https://chromium.googlesource.com/angle/angle).
- **OpenGL ES 3.2 Reference Pages.** [registry.khronos.org/OpenGL-Refpages/es3.2/](https://registry.khronos.org/OpenGL-Refpages/es3.2/).
- **KHR_debug extension.** [registry.khronos.org/OpenGL/extensions/KHR/KHR_debug.txt](https://registry.khronos.org/OpenGL/extensions/KHR/KHR_debug.txt).

---

## Проверь себя

> [!question]- Какая версия OpenGL ES даёт compute shaders?
> OpenGL ES 3.1 (2014, Android API 21+). Раньше compute делался только через OpenCL (отдельный API). 3.1+ compute semantically integrated с graphics context.

> [!question]- Что такое ANGLE?
> Google's translation layer from OpenGL ES → Vulkan (или D3D on Windows, Metal on Apple platforms). В 2026 default GL driver на many Android devices. Your GL code runs over Vulkan через transparent translation.

> [!question]- В чём проблема state machine модели OpenGL?
> Hidden dependencies. Global mutable state — один part code changes, another part breaks. Source of hard-to-debug bugs в large GL codebases. Mitigated через VAOs (ES 3.0+) — groups vertex state. Vulkan solved completely через immutable pipeline state objects.

> [!question]- Когда использовать OpenGL ES вместо Vulkan в 2026?
> Maintenance existing code, education, quick prototypes, simple 2D с blending, interop с legacy APIs. Для new 3D apps — Vulkan.

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

Что такое EGL?
?
Embedded Graphics Library — platform abstraction для создания GL context. Связывает GL с Android Surface (окно). eglMakeCurrent устанавливает context как active per thread.

---

Что такое VAO в OpenGL ES?
?
Vertex Array Object — groups vertex attribute state в один handle. Уменьшает per-draw state changes. Важно для performance с multi-object rendering.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Vulkan fundamentals | [[vulkan-on-android-fundamentals]] |
| ANGLE detail | [[angle-and-gl-compatibility]] |
| Decision | [[opengl-vs-vulkan-decision]] |
| GLSL language | [[glsl-language-deep]] |

---

*Deep-dive модуля M4. Расширенный 2026-04-20.*

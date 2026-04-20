---
title: "VSYNC и Choreographer: как Android дирижирует frame timing"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - type/deep-dive
  - level/advanced
related:
  - "[[surfaceflinger-and-buffer-queue]]"
  - "[[android-animations]]"
  - "[[android-handler-looper]]"
  - "[[frame-pacing-swappy-library]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[surfaceflinger-and-buffer-queue]]"
  - "[[android-animations]]"
primary_sources:
  - url: "https://source.android.com/docs/core/graphics/implement-vsync"
    title: "AOSP: Implement VSYNC"
    accessed: 2026-04-20
  - url: "https://developer.android.com/reference/android/view/Choreographer"
    title: "Android: Choreographer API"
    accessed: 2026-04-20
  - url: "https://developer.android.com/games/optimize/frame-pacing"
    title: "Android Game Frame Pacing Library"
    accessed: 2026-04-20
reading_time: 20
difficulty: 6
---

# VSYNC и Choreographer

60 Hz дисплей обновляется каждые 16.67 мс. 120 Hz — каждые 8.33 мс. Между этими редкими моментами display полностью зафиксирован. Если приложение хочет показать плавную анимацию, оно должно закончить рендеринг **до** VSYNC; если опоздает — frame drop, janky animation. Компонент, координирующий этот танец между app, SurfaceFlinger и display — **Choreographer**, Android-specific API поверх VSYNC сигнала. Этот deep-dive разбирает, как именно он работает, почему Project Butter в 2012 изменил mobile UX радикально, и как правильно синхронизировать Vulkan/Compose rendering с VSYNC.

---

## Зачем это знать

**Первое — диагностика jank.** Профайлер (Perfetto, AGI) показывает пропущенные frames. Причины могут быть: слишком долгая frame preparation, wrong VSYNC offset, thread contention. Без понимания Choreographer API отладка невозможна.

**Второе — animations timing.** Compose animations, ValueAnimator, physics-based animations — все в основе используют Choreographer frame callback. Synchronization с VSYNC гарантирует smooth timing.

**Third — custom rendering loop.** Vulkan-приложение само управляет timing. Должно coordinate с VSYNC (через Swappy) или ignore (tearing, MAILBOX present mode).

---

## Терминология

| Термин | Что |
|---|---|
| VSYNC | Vertical Synchronization — hardware signal от display при завершении refresh |
| Choreographer | Android API (with 4.1+), coordinates animations с VSYNC |
| Frame callback | Callback executed once per VSYNC |
| Input callback | Executed before frame, для touch event processing |
| Animation callback | Executed between input и draw, для physics/animation |
| Frame deadline | Latest moment for app to submit buffer to SurfaceFlinger для next VSYNC |
| VSYNC offset | Time delta между hardware VSYNC and when component wakes |
| Jank | Dropped frame, visually noticeable |

---

## Историческая справка

До Android 4.1 (Jelly Bean, 2012): no synchronization. Apps randomly wake, render, submit — results in tearing and stuttering. "Laggy animations" был universal complaint.

**Project Butter (2012)** — Google team lead Dianne Hackborn и Romain Guy introduced:
1. VSYNC-locked app thread wakeups.
2. Triple buffering.
3. Choreographer API.
4. Systrace tool для diagnostics.

Result — mobile animation became indistinguishable from iPhone smoothness. Massive улучшение UX.

**С тех пор:**
- Android 7.0 — Choreographer improvements для smooth scrolling.
- Android 10 — support 90/120 Hz displays.
- Android 12 — variable refresh rate.
- Android 14+ — improved frame pacing API, `Choreographer.FrameCallback` deprecated in favor of `setFrameCallback`.

---

## Как это работает

```
┌─────────────────────────────────────────────┐
│  Display Hardware                           │
│  → sends VSYNC signal every 16.67ms (60Hz)  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Kernel driver receives signal              │
│  → dispatches to userspace via eventfd      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  SurfaceFlinger (VSYNC listener #1)         │
│  → wakes at VSYNC offset (SF_offset)        │
│  → composes, presents previous frame        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  App process (VSYNC listener #2)            │
│  → wakes at VSYNC offset (App_offset)       │
│  → Choreographer dispatches callbacks:      │
│    • Input handlers                         │
│    • Animation handlers                     │
│    • Draw (traversal)                       │
│  → renders frame                            │
│  → submits to BufferQueue                   │
└─────────────────────────────────────────────┘
```

### VSYNC offsets

Three phases:
1. **Hardware VSYNC** — reference moment.
2. **SF VSYNC** (offset by, e.g., −4 ms) — SF wakes early enough to compose.
3. **App VSYNC** (offset by, e.g., −12 ms) — app wakes even earlier to render.

Android auto-tunes offsets based on measured frame times. Can override via `setFrameRate()` hints.

### Choreographer callbacks

Within each VSYNC, Choreographer fires callbacks in order:
1. **Input** (post-input event processing).
2. **Animation** (ValueAnimator.doAnimationFrame).
3. **Traversal** (View.draw, Compose recomposition).
4. **Commit** (finalize).

Это гарантирует consistent ordering. Touch input effect на same frame as animation update.

### Callback API (legacy)

```kotlin
Choreographer.getInstance().postFrameCallback { frameTimeNanos ->
    // called at next VSYNC
    // frameTimeNanos = expected display time
}
```

### Callback API (modern, Android 14+)

```kotlin
choreographer.setFrameCallback(frameCallback)
```

Enables more precise timing with `Choreographer.FrameData` and multiple frame targets.

---

## Уровень 2 — практика

### Custom animation loop

```kotlin
class MyAnimator {
    private val choreographer = Choreographer.getInstance()
    
    private val callback = Choreographer.FrameCallback { frameTimeNanos ->
        updateAnimation(frameTimeNanos)
        // re-schedule for next VSYNC
        choreographer.postFrameCallback(this)
    }
    
    fun start() {
        choreographer.postFrameCallback(callback)
    }
    
    private fun updateAnimation(timeNs: Long) {
        // advance animation by elapsed time
    }
}
```

Преимущество над `Handler.postDelayed(16)`: locked to VSYNC, no drift.

### Vulkan с Choreographer

```kotlin
class VulkanRenderLoop {
    private val callback = Choreographer.FrameCallback { _ ->
        renderFrame()
        choreographer.postFrameCallback(this)
    }
    
    private fun renderFrame() {
        vkAcquireNextImage(...)
        recordCommandBuffer(...)
        vkQueueSubmit(...)
        vkQueuePresent(...)
    }
}
```

### Compose animations

Compose uses Choreographer internally. `LaunchedEffect` с `withFrameNanos` delivered callback at each VSYNC:

```kotlin
var offset by remember { mutableStateOf(0f) }

LaunchedEffect(Unit) {
    val start = System.nanoTime()
    while (true) {
        withFrameNanos { frameTime ->
            val elapsed = (frameTime - start) / 1e9f
            offset = sin(elapsed * 2f) * 100f
        }
    }
}
```

---

## Уровень 3 — профессионал

### Frame pacing

Frame pacing — consistent inter-frame intervals. 16.67 ms ± 1 ms — smooth. 16.67 ± 5 ms — jank (human perceives).

**Swappy Library** (Android Frame Pacing) — recommended approach для games. Tracks:
- Frame render times.
- VSYNC relative timing.
- Throttles if app faster than display.
- Adapts to variable refresh rate.

### Multi-display

Android 10+ supports multiple displays (desktop mode, external). Each has own VSYNC. Choreographer per display.

### 120 Hz optimization

On 120 Hz phones, VSYNC interval = 8.33 ms. App может:
- Render at 120 — более плавно, больше battery.
- Render at 60 — VSYNC skip caжdy other, battery saved.
- Render at 30/40 — для games target below 60.

Use `Surface.setFrameRate(targetFrameRate, compatibility)` чтобы hint to system. Android 11+.

### Troubleshooting

**Systrace** (old) / **Perfetto** (new) — primary tools. Look for:
- Gaps between VSYNC signals.
- `deliverInputEvent` timings.
- `doFrame` call duration.
- `dispatchInsets` overhead.

Expected: `doFrame` < 16.67 ms (60 Hz target). If higher, jank.

### VSYNC internal signal chain

Детали hardware → app flow:

1. **Display panel** генерирует VSYNC pulse (hardware signal) в конце каждого refresh cycle.
2. **Display Controller** (часть SoC) получает signal через MIPI DSI или DisplayPort.
3. **Kernel display driver** (часть DRM subsystem) register interrupt handler.
4. **evdev или eventfd** дистрибьютит userspace.
5. **SurfaceFlinger** listens через `Choreographer` in system_server.
6. **App processes** также listen через own `Choreographer` instance.

Каждый hop добавляет latency (~50-100 μs каждый). Total VSYNC → app wake: typically 200-500 μs на modern SoC.

### VSYNC prediction

SurfaceFlinger maintains **VSYNC period** и predicts future VSYNC timestamps:

```
predicted_vsync_n = last_vsync + n * vsync_period
```

App может query: `Choreographer.getFrameTime()` — timestamp of most recent frame. `Choreographer.FrameData.getExpectedPresentationTimeNanos()` — when current frame will appear on display.

Это позволяет **temporal consistency** в animations — движение synchronized с actual display time, не nominal rate.

### Adaptive refresh rate

90/120/144 Hz displays могут dynamically adjust refresh:
- Scrolling list — 120 Hz for smoothness.
- Static screen — 60 Hz for battery.
- Video playback 24 FPS — exact 24 Hz (иначе judder).

App hint через:
```kotlin
surface.setFrameRate(
    60.0f,
    Surface.FRAME_RATE_COMPATIBILITY_DEFAULT,
    Surface.CHANGE_FRAME_RATE_ALWAYS
)
```

Android 11+. System может combine hints from multiple apps; window manager decides final refresh.

### Frame callback scheduling detail

`Choreographer.postFrameCallback` enqueues callback для next VSYNC. Internals:

- Callbacks grouped по type (INPUT, ANIMATION, TRAVERSAL, COMMIT).
- At VSYNC, each group fires in order.
- Callbacks execute в main thread (Looper context).
- If `doFrame` exceeds VSYNC period — **miss**, next VSYNC uses stale data.

В Android 13+ added **Extended frame callback**:
```kotlin
choreographer.setFrameCallback(object : Choreographer.FrameCallback {
    override fun doFrame(frameTimeNanos: Long) {
        // Callback
    }
})

// New API (Android 13+)
choreographer.setFrameCallback(object : Choreographer.FrameCallback2 {
    override fun doFrame(data: Choreographer.FrameData) {
        val frameTime = data.frameTimeNanos
        val expectedPresent = data.preferredFrameTimeline?.expectedPresentationTimeNanos
        val deadline = data.preferredFrameTimeline?.deadlineNanos
    }
})
```

FrameData provides multiple timeline options (for higher refresh rates), explicit presentation time, frame deadline.

### Janks: measuring и mitigation

Jank metrics на Android:

- **Frame drops (%):** дроп frames / total frames × 100%. Target <1%.
- **Missed deadlines (%):** frames submitted after deadline. Target <0.5%.
- **Frame time p99:** 99th percentile frame time. Target < refresh_period.

JankStats library (Android 12+) автоматически tracks.

Typical causes:
- Main thread blocked (IO, heavy computation, reflection).
- Slow recomposition (Compose state changes triggering wide recomposition).
- Shader compilation hitches (first-use).
- GC pauses (large object allocations).
- Animation callback doing too much work.

---

## Реальные кейсы

### Planner 5D — animation synchronization

Переключение 2D/3D использует Compose animation → Choreographer → smooth camera transition без dropped frames.

### IKEA Place — AR camera sync

ARCore camera updates arrive asynchronously. App uses Choreographer to synchronize rendering with VSYNC, смotря на latest ARCore data.

### Sweet Home 3D — Canvas animations на Choreographer

Animations для 2D floor plan (wall drag, furniture rotation) implemented через ValueAnimator, который internally использует Choreographer. Callback per frame updates position, invalidates View, hardware renders at next VSYNC.

```kotlin
val animator = ObjectAnimator.ofFloat(view, "translationX", 0f, 100f).apply {
    duration = 300
    interpolator = FastOutSlowInInterpolator()
}
animator.start()
// Internally posts to Choreographer; each frame updates
```

### Performance debug trace

AGI showing jank:
```
VSYNC ──────┬────────┬────────┬────────┬──────
            │        │        │        │
Frame 1: 12ms ✓      │        │        │
Frame 2:    16.8ms ✗ (missed) │        │
Frame 3:         15.5ms ✗ (previous caused this)
Frame 4:              12ms ✓
```

Missed frame cascades — одна slow frame toxicifies subsequent (renders backup в BufferQueue).

### Games — Swappy integration

```cpp
SwappyVk_init(device, physicalDevice);
SwappyVk_setWindow(device, swapchain, window);
// in render loop:
SwappyVk_queuePresent(queue, &presentInfo);
```

Swappy handles all VSYNC timing automatically.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| `Handler.postDelayed(16)` = VSYNC | Нет: даёт drift, не locked к VSYNC |
| Choreographer — только для animations | Используется для всего frame timing, включая draw |
| 60 FPS — always smooth | Inconsistent timing даже 60 FPS = jank. Consistency > raw FPS |
| Pressing touch immediately fires input callback | Input events batched, processed at VSYNC |

---

## Подводные камни

### Ошибка 1: блокирующая работа в frame callback

**Как избежать:** длинные операции на background thread. Frame callback должен быть <3 ms.

### Ошибка 2: ignoring VSYNC rate changes

**Как избежать:** observe `Display.getRefreshRate()` и adapt. VRR (variable refresh rate) may change mid-session.

### Ошибка 3: кастомный timing без Choreographer

**Как избежать:** всегда использовать Choreographer или Swappy для frame-coupled работы.

---

## Связь с другими темами

[[surfaceflinger-and-buffer-queue]] — куда submit буфер после Choreographer-driven render.
[[android-animations]] — ValueAnimator internals используют Choreographer.
[[android-handler-looper]] — Choreographer is Handler subclass.
[[frame-pacing-swappy-library]] — Swappy как wrapper над Choreographer для Vulkan.
[[android-compose-internals]] — Compose recomposition driven by Choreographer.

---

## Источники

- **AOSP Implement VSYNC.** [source.android.com/docs/core/graphics/implement-vsync](https://source.android.com/docs/core/graphics/implement-vsync).
- **Android Choreographer API.** [developer.android.com/reference/android/view/Choreographer](https://developer.android.com/reference/android/view/Choreographer).
- **Android Game Frame Pacing.** [developer.android.com/games/optimize/frame-pacing](https://developer.android.com/games/optimize/frame-pacing).
- **Google I/O 2012 — Project Butter talk.** Introduction of VSYNC-locked UI.

---

## Проверь себя

> [!question]- Что такое VSYNC offset и зачем нужен?
> Delay между hardware VSYNC и wake time of SurfaceFlinger / app. Обеспечивает, что SF / app имеют достаточно времени до следующего VSYNC для preparation. Android auto-tunes основываясь на measured frame times.

> [!question]- Почему `Handler.postDelayed(16)` не эквивалентно VSYNC sync?
> Timer drifts (не locked к hardware clock). Miss VSYNC by 1-2 ms пи накопится в жэнку через несколько секунд. Choreographer lock-steps с hardware VSYNC, drift = 0.

---

## Ключевые карточки

Что делает Project Butter (2012)?
?
Introduced VSYNC-locked rendering, triple buffering, Choreographer API на Android 4.1. Устранил jank из system animations. Основа всех subsequent frame pacing improvements.

---

Как Compose использует VSYNC?
?
Internally через Choreographer. `withFrameNanos { frameTime → ... }` в LaunchedEffect delivers callback на каждом VSYNC. Recomposition выполняется в traversal phase каждого frame.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Composition | [[surfaceflinger-and-buffer-queue]] |
| Frame pacing | [[frame-pacing-swappy-library]] |
| Animation internals | [[android-animations]] |

---

*Deep-dive модуля M3.*

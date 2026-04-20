---
title: "Perfetto и Systrace: system-wide profiling для graphics"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/profiling
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-gpu-inspector-agi]]"
  - "[[vsync-choreographer-deep]]"
  - "[[frame-pacing-swappy-library]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[vsync-choreographer-deep]]"
primary_sources:
  - url: "https://perfetto.dev/docs/"
    title: "Perfetto documentation"
    accessed: 2026-04-20
  - url: "https://developer.android.com/topic/performance/tracing"
    title: "Android system tracing"
    accessed: 2026-04-20
reading_time: 10
difficulty: 4
---

# Perfetto и Systrace

**Perfetto** — modern system tracing для Android (replaces Systrace, which is deprecated). Captures kernel events, CPU scheduling, frame timing, app code traces. Complementary to AGI: Perfetto dla system-level issues, AGI — per-GPU-draw.

---

## Что captures

- CPU threads (per-core usage, scheduling).
- Choreographer callbacks.
- VSYNC signals.
- SurfaceFlinger composition.
- Input events.
- Binder IPC.
- Memory allocations.
- Custom app traces (through `Trace.beginSection`).
- Thermal events.
- Battery stats.

---

## Запуск

### Perfetto UI

1. Web app [ui.perfetto.dev](https://ui.perfetto.dev).
2. Connect device via ADB.
3. Configure trace (categories, duration).
4. Record.
5. Analyze interactive.

Alternative: `perfetto` CLI from NDK:

```bash
adb shell perfetto -o /data/misc/perfetto-traces/trace.pb -t 10s \
    sched gfx view wm am input
adb pull /data/misc/perfetto-traces/trace.pb
```

Open в Perfetto UI.

---

## Custom app traces

```kotlin
import android.os.Trace

fun renderScene() {
    Trace.beginSection("RenderScene")
    try {
        // Work here
    } finally {
        Trace.endSection()
    }
}
```

Appears в Perfetto timeline в row «App thread». Trivia: `androidx.tracing.Trace` — slightly newer API supported from API 14.

---

## Reading timeline

Типичная good frame:
```
VSYNC───┐
        │  Choreographer.doFrame (2 ms)
        │    View draw (5 ms)
        │    GPU submit (1 ms)
        │
SurfaceFlinger composition (3 ms)
        │
        └─ Frame displayed
```

Bad frame:
```
VSYNC───┐
        │  Choreographer (BIG GAP — 30 ms)
        │    View draw (25 ms)  ← problem!
        │
SurfaceFlinger (missed VSYNC, next refresh)
        │
        └─ Frame dropped
```

Investigate long operations.

---

## Common diagnosis

### Frame drop

Timeline показывает `Frame` lasting > 16 ms. Drill down:
- Long JIT compilation?
- Blocking IO?
- GC pause?
- Layout pass?
- Unnecessary recomposition в Compose?

### Input latency

Touch events have long gap до processing. Investigate main thread busyness.

### VSYNC miss

Choreographer called, но work не complete к next VSYNC. Either work is long или pipeline stall.

---

## Сравнение AGI

| Feature | AGI | Perfetto |
|---|---|---|
| GPU per-draw timing | ✅ | ❌ |
| Shader profiling | ✅ | ❌ |
| CPU scheduling | ❌ | ✅ |
| Choreographer timing | Limited | ✅ |
| Thermal events | Partial | ✅ |
| Custom app traces | ❌ | ✅ |
| Binder IPC | ❌ | ✅ |
| Overall workflow | GPU-focused | System-focused |

Use both — sometimes one has info другой not.

---

## Android Studio integration

Android Studio Profiler → CPU profiler → System Trace. Под hood — Perfetto. Easier interface, visual.

Для deep analysis — standalone Perfetto UI лучше.

---

## Связь

[[android-gpu-inspector-agi]] — complementary.
[[vsync-choreographer-deep]] — VSYNC timing visible.
[[frame-pacing-swappy-library]] — Swappy traces appear.

---

## Источники

- **Perfetto docs.** [perfetto.dev/docs](https://perfetto.dev/docs/).
- **Android system tracing.** [developer.android.com/topic/performance/tracing](https://developer.android.com/topic/performance/tracing).

---

## Проверь себя

> [!question]- Perfetto или AGI?
> Both. AGI для GPU-level (per-draw timing, shaders). Perfetto для system-level (CPU, Choreographer, thermal, VSYNC). Typical workflow: Perfetto first to find frame problems, AGI для drill-down в GPU-related.

---

*Deep-dive модуля M11.*

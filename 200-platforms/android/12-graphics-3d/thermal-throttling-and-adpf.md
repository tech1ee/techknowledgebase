---
title: "Thermal throttling и ADPF: production stability"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/performance
  - type/deep-dive
  - level/advanced
related:
  - "[[gpu-architecture-fundamentals]]"
  - "[[frame-pacing-swappy-library]]"
  - "[[android-gpu-inspector-agi]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[gpu-architecture-fundamentals]]"
primary_sources:
  - url: "https://developer.android.com/games/optimize/adpf"
    title: "Android Dynamic Performance Framework (ADPF)"
    accessed: 2026-04-20
  - url: "https://source.android.com/docs/core/power/thermal-mitigation"
    title: "AOSP: Thermal mitigation"
    accessed: 2026-04-20
reading_time: 12
difficulty: 5
---

# Thermal throttling и ADPF

Mobile phones — **thermally-constrained**. Sustained high performance heats chip → OS throttles CPU/GPU → FPS drops. После 5-10 минут intensive 3D graphics типичный performance drops 30-50%. Production apps **должны** handle this.

**ADPF (Android Dynamic Performance Framework)** — Google's API для cooperative thermal management. App tells OS expected load, OS responds с thermal state, app adjusts quality.

---

## Проблема

Без thermal management:
- App runs full quality.
- Chip heats to throttle threshold.
- OS throttles GPU frequency 50-70%.
- FPS drops from 60 to 30-40.
- User experience degraded.

С proper thermal management:
- App monitors thermal state.
- Preemptively lowers quality (resolution, effects) before throttling.
- Chip stays below threshold.
- FPS stable 60 throughout session.

---

## Thermal API

```kotlin
import android.os.PowerManager

val pm = context.getSystemService(Context.POWER_SERVICE) as PowerManager

// Get thermal status (API 29+)
val status = pm.currentThermalStatus
// 0 = NONE (cool)
// 1 = LIGHT
// 2 = MODERATE
// 3 = SEVERE
// 4 = CRITICAL
// 5 = EMERGENCY
// 6 = SHUTDOWN

// Register listener
pm.addThermalStatusListener { newStatus ->
    adjustQuality(newStatus)
}
```

---

## ADPF Hint API (Android 12+)

More advanced. App declares performance targets; OS schedules accordingly:

```cpp
// Create hint session
PerformanceHintManager* phm = APerformanceHint_getManager();
int64_t targetDurationNanos = 16_666_666;  // 60 FPS = 16.67 ms
APerformanceHintSession* session = APerformanceHint_createSession(
    phm, threadIds, threadCount, targetDurationNanos);

// Each frame
APerformanceHint_reportActualWorkDuration(session, actualNanos);
```

OS может boost cores или adjust frequency based on reports.

---

## Thermal headroom

```kotlin
// Predict time until throttle
val headroom = pm.getThermalHeadroom(forecastSeconds = 10)
// 0.0 = cool, 1.0 = about to throttle, > 1.0 = throttling
```

Proactive adjustment — lower quality when headroom > 0.7, before throttling activates.

---

## Adjustment strategies

### Resolution scaling

```kotlin
fun adjustResolution(status: Int) {
    val scale = when (status) {
        PowerManager.THERMAL_STATUS_NONE -> 1.0f
        PowerManager.THERMAL_STATUS_LIGHT -> 0.9f
        PowerManager.THERMAL_STATUS_MODERATE -> 0.75f
        PowerManager.THERMAL_STATUS_SEVERE -> 0.5f
        else -> 0.3f
    }
    setRenderResolution(viewport.width * scale, viewport.height * scale)
}
```

При 0.75× resolution — ~44% fewer pixels — ~30% FPS increase.

### Quality settings

Disable expensive effects progressively:
- Light → disable bloom, FXAA.
- Moderate → disable shadows.
- Severe → disable IBL specular, reduce LOD bias.

### Target FPS

Drop from 60 to 45 or 30 FPS при high thermal. Стабильный 30 > stuttering 45.

---

## Real numbers

Games что использует ADPF:
- **Without ADPF:** FPS 60→35 over 10 min session.
- **With ADPF:** FPS 60 sustained, dropping to 50 only after 15 min.

Difference — meaningful.

---

## Game Mode (Android 12+)

Users могут enable "Game Mode" per-app:
- **Performance** — maximize FPS.
- **Standard** — balanced.
- **Battery Saver** — lower quality для longer play.

App receives `GameManager.setGameState()` notifications, adjusts accordingly.

---

## Vulkan hints (VPA-16)

Android 16 adds Vulkan performance hints через `VK_EXT_shader_object` и related. Drivers may use для thermal optimization.

---

## Связь

[[gpu-architecture-fundamentals]] — GPU frequency affected.
[[frame-pacing-swappy-library]] — stable framerate correlation.
[[android-gpu-inspector-agi]] — thermal visible в system profile.
[[battery-drain-plane-detection]] — related drain topics.

---

## Источники

- **ADPF documentation.** [developer.android.com/games/optimize/adpf](https://developer.android.com/games/optimize/adpf).
- **AOSP Thermal mitigation.** [source.android.com/docs/core/power/thermal-mitigation](https://source.android.com/docs/core/power/thermal-mitigation).

---

## Проверь себя

> [!question]- Зачем proactive thermal management?
> Reactive (waiting for throttle) даёт visible FPS drops. Proactive (lowering quality before throttle) keeps thermal под control, FPS stable. ADPF даёт тools для этого.

---

*Deep-dive модуля M12.*

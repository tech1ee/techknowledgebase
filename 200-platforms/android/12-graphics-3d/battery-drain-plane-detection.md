---
title: "Battery drain на AR-apps: plane detection и mitigation"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/performance
  - topic/ar
  - type/deep-dive
  - level/intermediate
related:
  - "[[thermal-throttling-and-adpf]]"
  - "[[arcore-fundamentals]]"
  - "[[arcore-plane-detection-deep]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[arcore-fundamentals]]"
reading_time: 8
difficulty: 3
---

# Battery drain AR-apps

Real concern для AR-приложений: 40% battery drop за 30 минут использования. Users uninstall apps с such behavior — Google research показал 62% uninstall rate для apps с severe battery drain. Plane detection + camera capture + 3D rendering — heaviest combination на mobile.

---

## Причины drain

AR app runs:
- **Camera stream** (usually 30 Hz) — ~5% battery per hour.
- **Plane detection** (continuous feature tracking, ARCore) — ~10-15% per hour.
- **3D rendering** (60 FPS, PBR) — ~15-20% per hour.
- **SLAM (Visual-Inertial Odometry)** — CPU-intensive, ~5% per hour.
- **ML models** (depth, lighting estimation) — ~5% per hour.

Combined 40-50% per hour. Unacceptable для most apps.

---

## Mitigation strategies

### 1. Disable plane detection after placement

Plane detection costly. Once user placed object — disable:

```kotlin
val config = arSession.config
config.planeFindingMode = Config.PlaneFindingMode.DISABLED
arSession.configure(config)
```

Save ~10-15% drain.

### 2. Lower camera resolution

ARCore supports multiple camera configurations. Lower res → less work:

```kotlin
val configs = arSession.getSupportedCameraConfigs()
val lowResConfig = configs.first { it.imageSize.width <= 1280 }
arSession.cameraConfig = lowResConfig
```

Save ~5% drain.

### 3. Target lower FPS

30 FPS AR often indistinguishable from 60 FPS (camera feed 30 Hz anyway). Halves GPU work:

```kotlin
Surface.setFrameRate(30f, FRAME_RATE_COMPATIBILITY_DEFAULT)
```

Save ~10-15% drain.

### 4. Disable unnecessary features

Depth API, lighting estimation, occlusion — enable только если use them:

```kotlin
config.depthMode = Config.DepthMode.DISABLED  // если не used
config.lightEstimationMode = Config.LightEstimationMode.DISABLED
```

### 5. Thermal-aware quality

Monitor thermal state (см. [[thermal-throttling-and-adpf]]). Under load:
- Reduce texture quality.
- Disable anti-aliasing.
- Lower LOD bias.

### 6. Pause when не active

```kotlin
override fun onPause() {
    super.onPause()
    arSession.pause()  // stop plane detection, camera
}

override fun onResume() {
    super.onResume()
    arSession.resume()
}
```

Obvious but often forgotten. If user switches tabs, pause session.

---

## Real numbers

IKEA Place optimization story:
- Before: 42% battery per hour.
- After (disable plane detection after placement + 30 FPS): 22%.
- User satisfaction increased, uninstalls dropped.

---

## Battery testing

Android Studio Energy Profiler (CPU, GPU, network) during session. Track changes across optimizations.

Battery Historian tool (bugreport analysis):
```bash
adb bugreport
# Upload to Battery Historian
```

---

## Связь

[[arcore-fundamentals]] — AR session management.
[[arcore-plane-detection-deep]] — specifics plane detection.
[[thermal-throttling-and-adpf]] — related thermal concerns.
[[frame-pacing-swappy-library]] — FPS target control.

---

## Источники

- **Android Battery documentation.** [source.android.com/docs/core/power](https://source.android.com/docs/core/power).
- **ARCore session management.** [developers.google.com/ar/develop/java/session-management](https://developers.google.com/ar/develop/java/session-management).

---

## Проверь себя

> [!question]- Главная причина battery drain в AR apps?
> Continuous plane detection. ARCore runs feature tracking в каждом frame. После placement object — disable plane detection. Other culprits: camera resolution, continuous 60 FPS rendering, ML-based features.

---

*Deep-dive модуля M12.*

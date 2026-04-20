---
title: "ARCore fundamentals: Session, Pose, Anchor, SLAM"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/ar
  - type/deep-dive
  - level/intermediate
related:
  - "[[arcore-plane-detection-deep]]"
  - "[[arcore-depth-api]]"
  - "[[arcore-geospatial-api-vps]]"
  - "[[ar-lighting-estimation]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[android-graphics-3d-moc]]"
primary_sources:
  - url: "https://developers.google.com/ar/develop/fundamentals"
    title: "ARCore fundamentals"
    accessed: 2026-04-20
  - url: "https://developers.google.com/ar/develop"
    title: "ARCore SDK"
    accessed: 2026-04-20
reading_time: 15
difficulty: 4
---

# ARCore fundamentals

**ARCore** — Google's Android AR platform, launched 2017, успel Tango research. ARCore 1.38+ (April 2026) поддерживает: SLAM tracking, plane detection, depth API, Geospatial API, Cloud Anchors, Lighting Estimation.

Core concept: device + ARCore понимает real-world scene через camera + sensors, дает apps access к this understanding — плоскости, depth, lighting, positions.

---

## Prerequisites

Device must support ARCore. Check через:
```kotlin
val availability = ArCoreApk.getInstance().checkAvailability(context)
// SUPPORTED_INSTALLED, SUPPORTED_APK_TOO_OLD, UNSUPPORTED_DEVICE_NOT_CAPABLE, etc.
```

ARCore SDK required:
```kotlin
// build.gradle
dependencies {
    implementation("com.google.ar:core:1.38.0")
}
```

---

## Core concepts

### Session

Main ARCore entity. Manages camera, tracking, features.

```kotlin
val session = Session(context)

val config = Config(session).apply {
    focusMode = Config.FocusMode.AUTO
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    depthMode = Config.DepthMode.AUTOMATIC  // если supported
}
session.configure(config)

session.resume()
// ...
session.pause()
```

### Frame

Per-frame snapshot of tracking state. Update every render frame:

```kotlin
val frame = session.update()
val timestamp = frame.timestamp  // nanoseconds
val camera = frame.camera
```

### Camera

Camera intrinsics (matching real device camera) + current pose:

```kotlin
val projection = FloatArray(16)
camera.getProjectionMatrix(projection, 0, 0.1f, 100f)

val view = FloatArray(16)
camera.getViewMatrix(view, 0)

val pose = camera.pose  // 4x4 Pose object
```

Для рендеринга virtual content on top of camera feed — use these exact matrices. Любое отклонение → mis-alignment.

### Pose

4×4 transform: translation (3D point) + rotation (quaternion xyzw).

```kotlin
val pose = Pose(
    /* translation = */ floatArrayOf(1f, 0f, 2f),
    /* rotation = */ floatArrayOf(0f, 0f, 0f, 1f)  // xyzw
)

val matrix = FloatArray(16)
pose.toMatrix(matrix, 0)  // column-major 4x4
```

Import в [[kotlin-math]]: remember xyzw vs wxyz different (см. [[quaternions-and-rotations#Representation ARCore]]).

### Trackable

Something ARCore tracks в world. Sub-types:
- **Plane** — detected horizontal/vertical surfaces.
- **AugmentedImage** — tracked real-world images.
- **AugmentedFace** — detected face mesh.
- **Trackable** base class.

### Anchor

Fixed point в world attached к specific location. Virtual content parents к anchor:

```kotlin
val hitResult = frame.hitTest(touchX, touchY).firstOrNull()
if (hitResult != null) {
    val anchor = hitResult.createAnchor()
    // anchor.pose — где объект placed
    // attach 3D model к this anchor
}
```

Anchor персистентны across frames (unless camera loses tracking).

### SLAM (Visual-Inertial Odometry)

**Technique** под капотом ARCore:
- Camera frames → identify visual features (corners, edges).
- IMU (gyroscope + accelerometer) → motion sensors.
- Fusion → estimate camera pose over time.

Called VIO — Visual-Inertial Odometry. Continuously track device position без GPS или external markers.

---

## Lifecycle

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    // session created, configured
}

override fun onResume() {
    super.onResume()
    session.resume()  // start camera, tracking
}

override fun onPause() {
    super.onPause()
    session.pause()  // stop camera, pause tracking
}

override fun onDestroy() {
    super.onDestroy()
    session.close()  // cleanup
}
```

**Важно:** pause/resume correctly. Без pause — battery drain continues даже когда app background.

---

## Render loop

```kotlin
fun onDrawFrame(frame: Frame) {
    // 1. Display camera background
    backgroundRenderer.draw(frame)
    
    // 2. Get tracking state
    if (frame.camera.trackingState != TrackingState.TRACKING) return
    
    // 3. Get projection + view matrices
    val projection = FloatArray(16)
    frame.camera.getProjectionMatrix(projection, 0, 0.1f, 100f)
    val view = FloatArray(16)
    frame.camera.getViewMatrix(view, 0)
    
    // 4. Render virtual content
    for (anchor in activeAnchors) {
        val model = anchor.pose.toMatrix()
        renderModel(model, view, projection)
    }
}
```

---

## SceneView wrapper

[[sceneview-arcore-composable-3d|SceneView]] абстрагирует этот boilerplate. `ArSceneView` handles session lifecycle, background rendering, hit testing.

---

## Error handling

Tracking может быть lost:
```kotlin
when (camera.trackingState) {
    TrackingState.TRACKING -> renderVirtualContent()
    TrackingState.PAUSED -> showMessage("Hold steady — Tracking recovering...")
    TrackingState.STOPPED -> showMessage("Move device to find surfaces")
}
```

User feedback critical.

---

## Performance

ARCore session:
- Camera: 30-60 Hz frame processing.
- SLAM: CPU-intensive (1-2 CPU cores), 10-15% battery per hour.
- Plane detection: additional ~5-10% if enabled.

Balance features с battery life.

---

## Связь

[[arcore-plane-detection-deep]] — plane types и detection.
[[arcore-depth-api]] — depth data.
[[arcore-geospatial-api-vps]] — global localization.
[[ar-lighting-estimation]] — light from scene.
[[ar-occlusion-rendering]] — render over real objects.
[[sceneview-arcore-composable-3d]] — higher-level API.
[[quaternions-and-rotations]] — Pose rotation format.

---

## Источники

- **ARCore fundamentals.** [developers.google.com/ar/develop/fundamentals](https://developers.google.com/ar/develop/fundamentals).
- **ARCore SDK.** [developers.google.com/ar/develop](https://developers.google.com/ar/develop).

---

## Проверь себя

> [!question]- Чем Anchor отличается от Pose?
> Pose — single 4x4 transform в момент time. Anchor — persistent attachment к specific location в world, maintained by ARCore across frames even с camera movement. Virtual content parents к anchor; anchor pose updates автоматически.

---

*Deep-dive модуля M13.*

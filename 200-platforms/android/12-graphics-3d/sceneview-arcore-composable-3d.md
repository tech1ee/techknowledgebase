---
title: "SceneView Android: community successor Sceneform для AR + 3D"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/sceneview
  - topic/ar
  - type/deep-dive
  - level/intermediate
related:
  - "[[engine-comparison-matrix]]"
  - "[[filament-architecture-deep]]"
  - "[[arcore-fundamentals]]"
  - "[[gltf-2-format-deep]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[filament-architecture-deep]]"
primary_sources:
  - url: "https://github.com/SceneView/sceneview-android"
    title: "SceneView Android GitHub"
    accessed: 2026-04-20
  - url: "https://sceneview.github.io/"
    title: "SceneView documentation"
    accessed: 2026-04-20
reading_time: 14
difficulty: 4
---

# SceneView Android

## Историческая справка

SceneView рассказ:

- **2018 — Google releases Sceneform.** Based on own engine, ARCore integrated. Designed Android-first для AR apps.
- **2020 — Sceneform deprecated.** Google strategic shift к cross-platform ARCore. Repository archived.
- **2020 — SceneView project started.** Thomas Gorisse (French indie developer) + community. Goal: continue Sceneform API with modernization.
- **2021 — SceneView 1.0.** Filament + ARCore backend. Kotlin-first.
- **2022 — Compose integration.**
- **2023 — Major refactor** для modern Android.
- **2024 — ARCore Geospatial integration.**
- **2025 — Dependency injection friendly.**
- **2026 — v2.x current, stable, used в production apps.**

SceneView — примечательный success community-driven continuation когда Google abandoned.



**SceneView** — community-maintained Android library для 3D и AR, successor Google Sceneform (deprecated 2020, archived). Использует Filament + ARCore под капотом, provides scene graph + Kotlin-first API + Compose integration.

Primary value: **быстрый старт** для 3D/AR приложения. Loading glTF → отображение в сцене за 5-10 строк кода. Отличный fit для product viewers, AR shopping apps, quick prototypes.

---

## Зачем SceneView

Google deprecated Sceneform в 2020 году и заархивировал repo. Community (led by Thomas Gorisse и других) запустил SceneView как continuation — с:
- Modern Kotlin API (coroutines, property syntax).
- Lifecycle-aware components.
- Active maintenance (releases каждые 1-3 месяца).
- Compose integration.
- Filament 1.71+ support.
- ARCore latest features.

---

## Prerequisites

- [[filament-architecture-deep]] — SceneView использует Filament для rendering.
- [[arcore-fundamentals]] — AR-part использует ARCore.

---

## Architecture

```
SceneView / ArSceneView (View или @Composable)
    │
    ├─ SceneManager (internal)
    │   ├─ Filament Engine, Scene, View, Camera
    │   └─ ARCore Session (if ArSceneView)
    │
    ├─ Node tree (scene graph)
    │   ├─ Node (Transform, children)
    │   ├─ ModelNode (loaded glTF)
    │   ├─ LightNode (directional, point, spot)
    │   ├─ CameraNode (camera control)
    │   └─ AnchorNode (AR anchor-attached, AR only)
    │
    └─ Gesture detectors (drag, pinch, rotate)
```

---

## Basic usage

### Non-AR 3D viewer

```kotlin
@Composable
fun ProductViewer(modelUri: String) {
    SceneView(
        modifier = Modifier.fillMaxSize(),
        onCreate = { sceneView ->
            val model = sceneView.modelLoader.loadModel(modelUri)
            val node = ModelNode(model)
            sceneView.addChild(node)
            
            // Setup lighting
            sceneView.indirectLight = IndirectLight.Builder()
                .irradiance(irradianceMap)
                .reflections(reflectionMap)
                .build(sceneView.engine)
            
            // Camera position
            sceneView.cameraNode.position = Position(0f, 1f, 3f)
        }
    )
}
```

Result: glTF model rendered, drag/pinch/rotate gesture handling автоматически.

### AR с Anchor

```kotlin
@Composable
fun ArFurniturePlacer(modelUri: String) {
    ARSceneView(
        modifier = Modifier.fillMaxSize(),
        sessionConfiguration = { session, config ->
            config.depthMode = Config.DepthMode.AUTOMATIC
            config.planeFindingMode = Config.PlaneFindingMode.HORIZONTAL
        },
        onSessionCreated = { session ->
            // setup
        },
        onTap = { hitResult ->
            // Create anchor and attach model
            val anchor = hitResult.createAnchor()
            val anchorNode = AnchorNode(arSceneView.engine, anchor)
            
            val model = modelLoader.loadModel(modelUri)
            val modelNode = ModelNode(model)
            anchorNode.addChild(modelNode)
            
            arSceneView.addChild(anchorNode)
        }
    )
}
```

One-tap placement furniture в real world.

---

## Key features

### Model loading

Native glTF support:
```kotlin
val model = sceneView.modelLoader.loadModel("sofa.glb")
val modelInstance = model.instance
val modelNode = ModelNode(modelInstance)
```

Async variant:
```kotlin
val model = sceneView.modelLoader.loadModelAsync("sofa.glb") { progress ->
    // update progress bar
}
```

### Gesture handling

Built-in drag, pinch, rotate, tap, double-tap. Per-node configurable:
```kotlin
modelNode.apply {
    isDragEnabled = true
    isPinchScaleEnabled = true
    isRotationEnabled = true
}
```

### ARCore integration

Все ARCore features first-class:
- `ArModelNode` — snaps to plane, follows anchor.
- Depth API для occlusion.
- Lighting estimation auto-applied.
- Cloud anchors supported.
- Geospatial API supported.

### Animations

glTF animations load automatically:
```kotlin
val animator = modelNode.animator
animator?.applyAnimation(0)
animator?.updateBoneMatrices()
```

---

## Comparison с direct Filament

| Aspect | Direct Filament | SceneView |
|---|---|---|
| Boilerplate | ~100 lines для basic viewer | ~10 lines |
| Scene graph | Manual | Built-in |
| ARCore | Manual integration | `ArSceneView` one-liner |
| glTF loading | Via gltfio extension | Built-in `modelLoader` |
| Gesture | Manual | Built-in |
| Kotlin idioms | Through wrapper | Native |
| Control granularity | Maximum | High but wrapped |
| APK size | ~15 MB | +2-3 MB over Filament |

Generally — SceneView для 80% use cases. Direct Filament — когда нужен максимальный control.

---

## Compose-first

SceneView library имеет dedicated `sceneview-compose` module:

```kotlin
import io.github.sceneview.ar.ARScene
import io.github.sceneview.Scene

@Composable
fun MyApp() {
    Scene(
        modifier = Modifier.fillMaxSize(),
        cameraNode = rememberCameraNode(),
        onCreate = { ... }
    )
}
```

Подходит для Compose-first apps. Внутри — AndroidView с SceneView.

---

## Limitations

- **Community-maintained:** не Google-backed. Risk of maintainer burnout.
- **Lagging documentation:** частично outdated examples.
- **Hidden Filament complexity:** for advanced needs приходится dive в Filament direct.
- **Performance:** ~2-5 MB overhead RAM, но не значимо для most apps.

---

## Real usage

- Community-developed product viewer apps в Play Store.
- AR shopping apps (SceneView fits perfectly for class IKEA Place).
- Educational apps с 3D models.

---

## Связь

[[engine-comparison-matrix]] — position among engines.
[[filament-architecture-deep]] — underlying rendering engine.
[[arcore-fundamentals]] — AR integration.
[[gltf-2-format-deep]] — asset format.
[[case-ikea-place-ar]] — similar architecture.
[[filament-inside-compose]] — alternative direct Filament approach.

---

## Источники

- **SceneView Android GitHub.** [github.com/SceneView/sceneview-android](https://github.com/SceneView/sceneview-android).
- **SceneView documentation.** [sceneview.github.io](https://sceneview.github.io/).

---

## Проверь себя

> [!question]- Когда SceneView лучше чем direct Filament?
> Быстрый старт для 3D/AR app. Когда нужен scene graph + gestures + glTF loading + ARCore готовые. Direct Filament когда нужен максимальный control.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Filament internals | [[filament-architecture-deep]] |
| ARCore detail | [[arcore-fundamentals]] |
| Compose integration | [[filament-inside-compose]] |

---

*Deep-dive модуля M8.*

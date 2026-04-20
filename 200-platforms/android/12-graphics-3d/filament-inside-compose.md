---
title: "Filament внутри Compose: полный tutorial"
created: 2026-04-20
modified: 2026-04-20
type: tutorial
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/filament
  - topic/compose
  - type/tutorial
  - level/intermediate
related:
  - "[[filament-architecture-deep]]"
  - "[[androidexternalsurface-vs-embedded]]"
  - "[[sceneview-arcore-composable-3d]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[filament-architecture-deep]]"
  - "[[androidexternalsurface-vs-embedded]]"
reading_time: 15
difficulty: 5
---

# Filament внутри Compose

Полный pattern для embedding Google Filament в Jetpack Compose app. Показывает: engine lifecycle, glTF model loading, camera orbit, lighting setup, integration с Compose state.

---

## Ключевые решения

Интеграция Filament в Compose имеет несколько architecture decisions:

### 1. Когда создавать Filament Engine

Filament `Engine` — heavy (~10 MB allocations, GPU contexts). Создавать:
- **Per-Activity:** если несколько Composables используют engine.
- **Singleton:** если весь app shares one scene.
- **Per-composable** (anti-pattern): slow, memory-heavy.

Best: hoisted в ViewModel, shared across composable instances.

### 2. Lifecycle coordination

Engine must be destroyed when composable disposed:
```kotlin
DisposableEffect(Unit) {
    val engine = Engine.create()
    // ... setup ...
    onDispose {
        engine.destroy()
    }
}
```

Пропуск onDispose — memory leak.

### 3. Surface choice

- **AndroidExternalSurface** — fullscreen или large rendering. HWC friendly.
- **AndroidEmbeddedExternalSurface** — integrated с Compose transformations, UI overlay.

Для Planner 5D-like app — AndroidExternalSurface когда в 3D mode, AndroidEmbeddedExternalSurface для PIP preview.

### 4. Threading

Filament engine is not thread-safe по default. Должны render from one thread. Compose main thread suffices для most scenarios. Для очень complex scenes — dedicated render thread через Handler.

### 5. Input handling

Compose handles touch via `Modifier.pointerInput`. Передача touch в Filament:
```kotlin
.pointerInput(Unit) {
    detectDragGestures { change, dragAmount ->
        camera.rotate(dragAmount.x, dragAmount.y)
    }
}
```

## Setup

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.google.android.filament:filament-android:1.71.0")
    implementation("com.google.android.filament:gltfio-android:1.71.0")
    implementation("com.google.android.filament:filament-utils-android:1.71.0")
}

// Filament.init — one-time in Application class
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        Filament.init()
    }
}
```

---

## Main composable

```kotlin
@Composable
fun ModelViewer(
    modifier: Modifier = Modifier,
    modelAssetPath: String,
    cameraAzimuth: Float = 0f,
    cameraElevation: Float = 30f,
    cameraDistance: Float = 5f
) {
    val context = LocalContext.current
    val engine = remember { Engine.create() }
    val renderer = remember { engine.createRenderer() }
    val scene = remember { engine.createScene() }
    val camera = remember {
        engine.createCamera(engine.entityManager.create()).apply {
            setExposure(16f, 1f/125f, 100f)
        }
    }
    val view = remember {
        engine.createView().apply {
            this.scene = scene
            this.camera = camera
        }
    }
    val materialProvider = remember {
        UbershaderProvider(engine)
    }
    val assetLoader = remember {
        AssetLoader(engine, materialProvider, EntityManager.get())
    }
    val resourceLoader = remember {
        ResourceLoader(engine)
    }
    
    // Cleanup on dispose
    DisposableEffect(Unit) {
        onDispose {
            engine.destroyRenderer(renderer)
            engine.destroyScene(scene)
            engine.destroyCameraComponent(camera.entity)
            engine.destroyView(view)
            assetLoader.destroy()
            resourceLoader.destroy()
            engine.destroy()
        }
    }
    
    // Load model
    val asset = remember(modelAssetPath) {
        val bytes = context.assets.open(modelAssetPath).readBytes()
        val buffer = ByteBuffer.wrap(bytes)
        assetLoader.createAsset(buffer).also {
            resourceLoader.loadResources(it)
            scene.addEntities(it.entities)
        }
    }
    
    // Update camera когда параметры меняются
    LaunchedEffect(cameraAzimuth, cameraElevation, cameraDistance) {
        val azRad = Math.toRadians(cameraAzimuth.toDouble())
        val elRad = Math.toRadians(cameraElevation.toDouble())
        val x = cameraDistance * cos(elRad).toFloat() * sin(azRad).toFloat()
        val y = cameraDistance * sin(elRad).toFloat()
        val z = cameraDistance * cos(elRad).toFloat() * cos(azRad).toFloat()
        camera.lookAt(x.toDouble(), y.toDouble(), z.toDouble(), 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    }
    
    // Add directional light
    LaunchedEffect(Unit) {
        val lightEntity = EntityManager.get().create()
        LightManager.Builder(LightManager.Type.DIRECTIONAL)
            .color(1f, 1f, 1f)
            .intensity(100_000f)
            .direction(0.5f, -1f, -0.5f)
            .castShadows(true)
            .build(engine, lightEntity)
        scene.addEntity(lightEntity)
    }
    
    // Render surface
    AndroidExternalSurface(modifier = modifier) {
        onSurface { surface, w, h ->
            val swapChain = engine.createSwapChain(surface)
            view.viewport = Viewport(0, 0, w, h)
            camera.setProjection(60.0, w.toDouble() / h, 0.1, 100.0, Camera.Fov.VERTICAL)
            
            while (isActive) {
                if (renderer.beginFrame(swapChain, System.nanoTime())) {
                    renderer.render(view)
                    renderer.endFrame()
                }
                awaitFrame()
            }
            
            engine.destroySwapChain(swapChain)
        }
    }
}
```

---

## Use in screen

```kotlin
@Composable
fun ProductScreen() {
    var azimuth by remember { mutableStateOf(0f) }
    var elevation by remember { mutableStateOf(30f) }
    
    Column {
        ModelViewer(
            modifier = Modifier.fillMaxWidth().weight(1f)
                .pointerInput(Unit) {
                    detectDragGestures { _, dragAmount ->
                        azimuth -= dragAmount.x * 0.5f
                        elevation = (elevation - dragAmount.y * 0.5f).coerceIn(-80f, 80f)
                    }
                },
            modelAssetPath = "models/sofa.glb",
            cameraAzimuth = azimuth,
            cameraElevation = elevation
        )
        
        Slider(
            value = elevation / 90f,
            onValueChange = { elevation = it * 90f },
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

Drag пальцем по экрану поворачивает camera. Slider — elevation control.

---

## Gotchas

### Engine lifecycle

**Обязательно** cleanup в `onDispose`. Иначе memory leak + possible crash at app exit.

### Multiple FilamentViewers

Если нужно несколько 3D views на одном экране — лучше один Engine shared, но separate Renderer/Scene. Создавать multiple Engine instances — expensive.

### Background frames

`awaitFrame()` — VSYNC-synchronized. Если app в background, frames stop. Обычно это желаемое behavior.

### First frame latency

Первая компиляция shader'ов для models — ~100-500 ms. Users видят loading. Solution — pipeline cache (см. [[shader-compilation-jitter-mitigation]]).

---

## Performance

Typical:
- Empty Filament scene: 60 FPS, ~2% CPU.
- Sofa model (10k triangles): 60 FPS, ~15% CPU, ~30 MB RAM.
- Complex scene (100k triangles + IBL + shadows): 60 FPS на flagship, 45 FPS на mid-range.

---

## Связь

[[filament-architecture-deep]] — Filament internals.
[[androidexternalsurface-vs-embedded]] — surface integration.
[[sceneview-arcore-composable-3d]] — SceneView — simpler wrapper для similar use case.
[[shader-compilation-jitter-mitigation]] — pipeline cache.

---

## Источники

- **Filament Android samples.** [github.com/google/filament/tree/main/android/samples](https://github.com/google/filament/tree/main/android/samples).

---

## Проверь себя

> [!question]- Зачем cleanup в DisposableEffect?
> Filament allocates GPU resources (swapchain, buffers, textures) через engine. Без explicit cleanup — memory leaks. В худшем случае — crash при app destroy. DisposableEffect гарантирует cleanup при removal from composition.

---

*Tutorial модуля M9.*

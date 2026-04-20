---
title: "Build a 3D home planner from scratch (Planner 5D-class app)"
created: 2026-04-20
modified: 2026-04-20
type: guide
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - type/guide
  - build-guide
  - level/advanced
related:
  - "[[android-graphics-3d-moc]]"
  - "[[case-planner-5d]]"
  - "[[case-ikea-place-ar]]"
  - "[[engine-comparison-matrix]]"
  - "[[build-production-android-app]]"
  - "[[role-mobile-developer]]"
prerequisites:
  - "[[android-graphics-3d-moc]]"
reading_time: 20
difficulty: 5
---

# Build your 3D home planner from scratch

Capstone guide для всего курса [[android-graphics-3d-moc]]. Target: team строит MVP приложения типа Planner 5D за 3-6 месяцев. Stack — производственный, battle-tested, minimal custom code.

**Target specs:**
- Room editor (2D top-down) + 3D walkthrough.
- Furniture catalog (50-100 models).
- Drag-and-drop placement + rotation.
- Save/load scenes locally.
- AR "view in my room" mode.
- 60 FPS на Snapdragon 7 Gen 1+ devices.
- APK size ≤ 50 MB.
- Battery drain ≤ 25% per hour.

---

## Stack (recommended для 2026)

- **Kotlin + Jetpack Compose** — UI.
- **Filament 1.71** — 3D renderer.
- **SceneView** — wrapper (simplifies Filament + ARCore).
- **ARCore 1.38** — AR.
- **kotlin-math 1.6.0** — 3D math.
- **Room** — local scene storage.
- **Coroutines + Flow** — reactive state.
- **Coil** — image loading.
- **glTF 2.0 + KTX2** — assets.

Why not Unity? — APK size, cold start, battery на non-game app (см. [[engine-comparison-matrix]]).

---

## Phase 1: Foundation (Week 1-2)

### Setup

```kotlin
// build.gradle.kts
dependencies {
    implementation(libs.compose.bom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    
    implementation("com.google.android.filament:filament-android:1.71.0")
    implementation("com.google.android.filament:gltfio-android:1.71.0")
    implementation("com.google.android.filament:filament-utils-android:1.71.0")
    
    implementation("io.github.sceneview:sceneview:latest")
    implementation("io.github.sceneview:arsceneview:latest")
    
    implementation("com.google.ar:core:1.38.0")
    
    implementation("dev.romainguy:kotlin-math:1.6.0")
    
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")
}
```

### Scene data model

```kotlin
data class Scene(
    val id: String,
    val rooms: List<Room>,
    val furniture: List<FurnitureInstance>
)

data class Room(
    val walls: List<Wall>,
    val floor: Shape,
    val height: Float = 2.7f
)

data class Wall(
    val start: Vec2,
    val end: Vec2,
    val thickness: Float = 0.1f
)

data class FurnitureInstance(
    val id: String,
    val catalogId: String,
    val position: Float3,
    val rotation: Float,  // single Y-axis угол
    val scale: Float = 1f
)
```

Minimal model — key принцип: **same model renders как 2D и 3D**.

### Room Database

```kotlin
@Entity
data class SceneEntity(
    @PrimaryKey val id: String,
    val sceneJson: String,  // serialize Scene
    val updatedAt: Long
)

@Dao
interface SceneDao {
    @Query("SELECT * FROM SceneEntity")
    fun getAll(): Flow<List<SceneEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun save(scene: SceneEntity)
}
```

---

## Phase 2: 2D editor (Week 2-4)

### Top-down view

```kotlin
@Composable
fun TopDownEditor(scene: Scene, onSceneChange: (Scene) -> Unit) {
    Canvas(modifier = Modifier
        .fillMaxSize()
        .pointerInput(Unit) {
            detectDragGestures { change, dragAmount ->
                // update wall/furniture position
            }
        }
    ) {
        // Render floor
        drawRect(color = Color.Gray, topLeft = Offset.Zero, size = size)
        
        // Walls
        scene.rooms.forEach { room ->
            room.walls.forEach { wall ->
                drawLine(
                    color = Color.Black,
                    start = wall.start.toOffset(),
                    end = wall.end.toOffset(),
                    strokeWidth = wall.thickness * scale
                )
            }
        }
        
        // Furniture (top-down icons)
        scene.furniture.forEach { item ->
            drawCircle(
                color = Color.Blue,
                radius = 20f,
                center = item.position.xz.toOffset()
            )
        }
    }
}
```

Uses Compose Canvas ([[compose-canvas-drawscope-deep]]). Simple, fast.

### Catalog

```kotlin
@Composable
fun FurnitureCatalog(onSelect: (CatalogItem) -> Unit) {
    LazyVerticalGrid(columns = GridCells.Fixed(3)) {
        items(furnitureCatalog) { item ->
            AsyncImage(
                model = item.thumbnailUrl,
                contentDescription = item.name,
                modifier = Modifier
                    .size(100.dp)
                    .clickable { onSelect(item) }
            )
        }
    }
}
```

---

## Phase 3: 3D view (Week 4-6)

### Renderer с Filament

Use [[filament-inside-compose]] pattern. Key:

```kotlin
@Composable
fun Scene3DView(scene: Scene, modifier: Modifier = Modifier) {
    val engine = rememberEngine()
    val renderer = rememberRenderer(engine)
    val filamentScene = rememberScene(engine)
    val camera = rememberOrbitCamera(engine)
    
    // Sync scene with Filament
    LaunchedEffect(scene) {
        updateFilamentScene(filamentScene, scene, engine)
    }
    
    AndroidExternalSurface(modifier = modifier) {
        onSurface { surface, _, _ ->
            renderLoop(engine, renderer, view, surface)
        }
    }
}
```

### Model loading

```kotlin
suspend fun loadFurnitureModel(catalogId: String): FilamentAsset {
    val path = "models/$catalogId.glb"
    val bytes = assets.open(path).readBytes()
    return assetLoader.createAsset(ByteBuffer.wrap(bytes))
}
```

### Sync scene state

```kotlin
fun updateFilamentScene(filamentScene: Scene, appScene: AppScene, engine: Engine) {
    // Compute diff between previous and new state
    // Add new entities, remove old, update transforms
    
    appScene.furniture.forEach { item ->
        val entity = getOrCreateEntity(item.id)
        val transform = buildTransform(item)
        engine.transformManager.setTransform(transform)
    }
}
```

---

## Phase 4: 2D ↔ 3D sync (Week 6-7)

Unified state management через Flow:

```kotlin
class SceneViewModel : ViewModel() {
    private val _scene = MutableStateFlow(Scene.empty)
    val scene: StateFlow<Scene> = _scene.asStateFlow()
    
    fun moveFurniture(id: String, newPosition: Float3) {
        _scene.update { old ->
            old.copy(furniture = old.furniture.map {
                if (it.id == id) it.copy(position = newPosition) else it
            })
        }
    }
}

@Composable
fun EditorScreen(vm: SceneViewModel) {
    val scene by vm.scene.collectAsState()
    
    // 2D and 3D both observe scene
    Row {
        TopDownEditor(scene, onSceneChange = vm::updateScene)
        Scene3DView(scene)
    }
}
```

Single source of truth. Both views auto-sync.

---

## Phase 5: AR mode (Week 8-10)

```kotlin
@Composable
fun ArPlaceMode(catalogItem: CatalogItem) {
    ARSceneView(
        modifier = Modifier.fillMaxSize(),
        sessionConfiguration = { session, config ->
            config.depthMode = Config.DepthMode.AUTOMATIC
            config.lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
        },
        onTap = { hitResult ->
            val anchor = hitResult.createAnchor()
            val node = ArModelNode(arSceneView.engine, anchor)
            val model = modelLoader.loadModel(catalogItem.modelPath)
            node.setModel(model)
            arSceneView.addChild(node)
            
            // Disable plane detection after placement (battery)
            val cfg = arSceneView.session.config
            cfg.planeFindingMode = Config.PlaneFindingMode.DISABLED
            arSceneView.session.configure(cfg)
        }
    )
}
```

SceneView ([[sceneview-arcore-composable-3d]]) handles almost всё.

---

## Phase 6: Polish (Week 10-12)

### Optimizations

- Reverse-Z для depth precision ([[z-buffer-and-depth-testing]]).
- Pipeline cache ([[shader-compilation-jitter-mitigation]]).
- Thermal-aware quality ([[thermal-throttling-and-adpf]]).
- Frame pacing via Swappy optional.
- LOD для catalog items ([[level-of-detail-lod]]).
- Instancing для repeated furniture ([[instancing-batching-draw-calls]]).

### Asset pipeline

1. Source .blend files (Blender).
2. Export glTF 2.0.
3. Compress textures: KTX2 via `toktx` ([[texture-compression-ktx2-basis]]).
4. Compress meshes: meshopt ([[mesh-compression-draco]]).
5. Bundle: APK или Play Asset Delivery ([[asset-loading-streaming]]).

Typical per-furniture-item:
- Base model: 50-200 KB (compressed).
- Textures: 200-500 KB (compressed).
- Total: ~300-700 KB.

Catalog 100 items: ~30-70 MB.

---

## Success criteria

Testing on reference devices (Snapdragon 7 Gen 1, Mali-G78):

| Metric | Target | How to measure |
|---|---|---|
| Cold start | < 2 s | Android Studio profiling |
| Scene load (50 items) | < 1 s | Manual + logs |
| 3D view FPS | 60 steady | AGI frame profile |
| AR FPS | 30-45 | AGI |
| APK size | ≤ 50 MB | `build/outputs/bundle` |
| Battery drain 30 min | ≤ 12.5% | Energy Profiler |

---

## Что НЕ нужно (scope creep)

- Cloud sync (Phase 2 launch).
- Photorealistic cloud rendering (far future).
- Multi-user collaboration (not MVP).
- Import from other formats (glTF only initially).
- Custom 3D engine (use Filament).

Cut scope ruthlessly для MVP.

---

## После MVP (Phase 2+)

- **Cloud sync** — Firebase или Supabase.
- **Cloud photorealistic rendering** — AWS/GCP GPU instance.
- **Collaboration** — multi-user real-time editing.
- **More formats** — Import FBX, OBJ.
- **Marketplace** — user-submitted furniture.

6-12 more months.

---

## Cross-links на весь курс

- [[android-graphics-3d-moc]] — root.
- [[case-planner-5d]] — inspiration.
- [[case-ikea-place-ar]] — AR benchmark.
- [[case-sweet-home-3d-android]] — simpler model.
- [[engine-comparison-matrix]] — why Filament.
- [[filament-architecture-deep]] — renderer detail.
- [[sceneview-arcore-composable-3d]] — AR wrapper.
- [[vectors-in-3d-graphics]] + [[matrices-for-transformations]] + [[quaternions-and-rotations]] — math.
- [[gltf-2-format-deep]] — asset format.
- [[compose-canvas-drawscope-deep]] — 2D UI drawing.
- [[thermal-throttling-and-adpf]] — battery sustainability.

---

## Заключение курса

Путь от [[vectors-in-3d-graphics|вектора]] до production-app. Math → GPU → API → engine → production. Каждый модуль закрывает специфический aspect. Этот capstone — применяет всё вместе.

Бenchmark — Planner 5D. С правильным stack (Filament + SceneView + Compose + ARCore + kotlin-math) и 3-6 months focused team — MVP достижим.

Дальше — iteration, polish, scale.

---

## Источники

См. [[android-graphics-3d-moc#Источники и первичные материалы]].

---

*Capstone module M16. Закрывает курс [[android-graphics-3d-moc]].*

---
title: "Asset loading и streaming на Android"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/assets
  - type/deep-dive
  - level/intermediate
related:
  - "[[gltf-2-format-deep]]"
  - "[[texture-compression-ktx2-basis]]"
  - "[[mesh-compression-draco]]"
  - "[[gpu-memory-management-mobile]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[gltf-2-format-deep]]"
primary_sources:
  - url: "https://developer.android.com/guide/playcore/asset-delivery"
    title: "Android Play Asset Delivery"
    accessed: 2026-04-20
reading_time: 10
difficulty: 3
---

# Asset loading и streaming

Scene с 1000 3D-моделями и 5000 textures не помещается в RAM mobile device (обычно 4-8 GB total). Right loading strategy — разница между smooth experience и constant stuttering.

---

## Strategies

### Load all at startup

Simple но slow (5-15 seconds initial загрузка для large scenes). Acceptable только для small apps.

### Streaming on demand

Load assets когда needed:
- **Distance-based:** load assets near player position.
- **View-frustum-based:** load только visible.
- **LOD-based:** load low-res first, high-res async.

### Async loading

Loading не блокирует main thread:
```kotlin
lifecycleScope.launch(Dispatchers.IO) {
    val model = loadGltfAsync("sofa.glb")
    withContext(Dispatchers.Main) {
        scene.add(model)
    }
}
```

---

## Android Play Asset Delivery

Google Play позволяет делить APK на:
- **Base APK** — main app code.
- **Asset Packs** — large assets (3D models, textures), downloaded на demand.

Three modes:
- **Install-time** — downloaded at install.
- **Fast-follow** — downloaded after install (background).
- **On-demand** — app requests when needed.

Example use: Planner 5D может ship базовые objects в APK, high-quality furniture models as on-demand packs.

---

## Memory budgets

Typical mobile:
- **Total RAM:** 4-16 GB.
- **App per-process limit:** 512 MB (low-end) до 8+ GB (flagship).
- **Available for 3D scene:** 100-500 MB typical.

Budget breakdown для 500 MB:
- Textures: 300 MB.
- Geometry: 100 MB.
- Animation data: 50 MB.
- Shaders + misc: 50 MB.

---

## Resource lifecycle

```kotlin
class AssetCache {
    private val cache = LruCache<String, Model>(maxSize = 100)  // LRU eviction
    
    fun loadAsync(path: String): Deferred<Model> {
        return viewModelScope.async(Dispatchers.IO) {
            cache.get(path) ?: run {
                val model = loadFromDisk(path)
                cache.put(path, model)
                model
            }
        }
    }
    
    fun onLowMemory() {
        cache.trimToSize(cache.size() / 2)
    }
}
```

Observe `ComponentCallbacks2.onTrimMemory()` для eviction.

---

## Progressive loading

Load low-quality сначала, high-quality after:

```kotlin
// 1. Low-poly LOD first (fast)
loadGltf("sofa_low.glb").then { addToScene(it) }

// 2. High-poly in background
loadGltf("sofa_high.glb").then { replaceInScene(it, previous) }
```

User sees something instantly, quality improves smoothly.

---

## Advanced loading patterns

### Manifest-based loading

Apps generate asset manifest (JSON) describing dependencies:

```json
{
  "scenes": {
    "living_room": {
      "required": ["sofa_high", "tv_unit", "coffee_table"],
      "textures": ["wood_oak", "fabric_linen"],
      "memory_budget_mb": 150
    }
  }
}
```

Runtime loader fetches только what's needed, caches intelligently.

### Priority queues

```kotlin
class AssetLoader {
    private val priorityQueue = PriorityBlockingQueue<LoadRequest>()
    
    fun request(asset: String, priority: Int) {
        priorityQueue.add(LoadRequest(asset, priority))
    }
    
    // Background worker processes highest priority first
    // Visible/near assets priority 100
    // Background/distant priority 10
}
```

Ensures user sees important content fast.

### Predictive loading

Based на camera movement direction, pre-load assets в соседних rooms / areas. Requires scene graph knowledge.

Example: в IKEA Place, если camera detects user's gaze direction, pre-fetch furniture likely to be pointed at.

### Dependency tracking

Assets могут have dependencies: sofa uses wood texture + fabric texture + normal map. Loader должен:
1. Parse dependencies от manifest / glTF.
2. Load dependencies before main asset.
3. Refcount shared assets (wood texture используется многими models).

```kotlin
class RefCountedAsset<T>(val asset: T) {
    private var refCount = 0
    fun acquire() = synchronized(this) { refCount++ }
    fun release() = synchronized(this) {
        if (--refCount == 0) {
            cleanup()
        }
    }
}
```

### Bundle grouping

Group related assets в bundles — one IO operation, less overhead:
- All sofa variants в одном .glb.
- All kitchen appliances в one bundle.

Trade-off: memory usage (load-all-or-nothing) vs IO efficiency.

### Compression at multiple levels

Full asset pipeline:
1. Source model — Blender .blend.
2. Export → glTF 2.0 (text).
3. Geometry compress — `gltfpack` (meshopt) или `gltf-pipeline` (Draco).
4. Textures compress — `toktx` → KTX 2.0 с Basis Universal.
5. Bundle — into `.glb` single file.
6. Optional deflate compression at OS level (Play Asset Delivery handles).

Final asset: ~10% original size with imperceptible quality loss.

## Texture streaming

Large textures — biggest memory hog. Strategies:
- **Mipmap streaming:** load low mip levels first, high mips on demand based on visible size.
- **Texture arrays** для similar textures (less memory vs separate allocations).
- **Virtual texturing** (advanced) — textures больше physical GPU memory, paged in/out.

Filament supports texture streaming для large scenes.

---

## Связь

[[gltf-2-format-deep]] — asset format.
[[texture-compression-ktx2-basis]] — compressed textures.
[[mesh-compression-draco]] — compressed meshes.
[[gpu-memory-management-mobile]] — VRAM management.

---

## Источники

- **Android Play Asset Delivery.** [developer.android.com/guide/playcore/asset-delivery](https://developer.android.com/guide/playcore/asset-delivery).

---

## Проверь себя

> [!question]- Когда использовать Play Asset Delivery?
> Когда APK превысил бы 150 MB из-за assets (Play Store limit). Выделить large 3D assets в asset packs, download on-demand. Keep APK base small для мгновенной установки.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Memory management | [[gpu-memory-management-mobile]] |
| Format | [[gltf-2-format-deep]] |

---

*Deep-dive модуля M7.*

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

---
title: "graphicsLayer Modifier: 2D/псевдо-3D трансформации в Compose"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/compose
  - type/deep-dive
  - level/intermediate
related:
  - "[[compose-canvas-drawscope-deep]]"
  - "[[agsl-runtime-shader-compose]]"
  - "[[android-compose-internals]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[android-compose]]"
primary_sources:
  - url: "https://developer.android.com/develop/ui/compose/graphics/draw/modifiers"
    title: "Compose Graphics modifiers"
    accessed: 2026-04-20
reading_time: 10
difficulty: 3
---

# graphicsLayer Modifier

`Modifier.graphicsLayer { ... }` — способ применить GPU-accelerated transformations и effects к composable: rotation, scale, alpha, shadow, clipping, render effects. Внутри — separate Skia layer, rendered independently и composed over content.

**Важно:** graphicsLayer — **2D**, не настоящий 3D. Для true 3D scenes — Filament/SceneView. GraphicsLayer может делать pseudo-3D effects через rotation + cameraDistance.

---

## Базовое использование

```kotlin
Box(modifier = Modifier
    .size(100.dp)
    .graphicsLayer {
        rotationX = 45f
        rotationY = 45f
        rotationZ = 10f
        cameraDistance = 12f * density
        scaleX = 1.5f
        scaleY = 1.5f
        alpha = 0.8f
        shadowElevation = 10f
    }
    .background(Color.Red)
)
```

---

## Свойства

| Property | Effect |
|---|---|
| `translationX/Y` | 2D translate |
| `scaleX/Y` | 2D scale |
| `rotationZ` | 2D rotation (around Z axis) |
| `rotationX/Y` | 3D-like rotation (around X/Y axis); creates perspective effect |
| `cameraDistance` | Distance of virtual camera для 3D rotations; bigger = less distortion |
| `alpha` | Opacity |
| `shadowElevation` | Drop shadow depth |
| `transformOrigin` | Pivot point для rotations/scales |
| `clip` | Boolean — clip content to shape |
| `shape` | Clipping shape (for rounded corners, circles) |
| `renderEffect` | Custom RenderEffect (blur, AGSL shader) |
| `compositingStrategy` | Offscreen vs modulate |

---

## Pseudo-3D rotation

```kotlin
var flipped by remember { mutableStateOf(false) }
val rotation by animateFloatAsState(if (flipped) 180f else 0f, animationSpec = tween(1000))

Box(modifier = Modifier
    .size(200.dp)
    .graphicsLayer {
        rotationY = rotation
        cameraDistance = 12f * density
    }
    .background(if (rotation < 90f) Color.Red else Color.Blue)
    .clickable { flipped = !flipped }
)
```

Creates "card flip" effect. **НЕ настоящий 3D** — просто projection 2D content.

---

## Render effects

```kotlin
Modifier.graphicsLayer {
    renderEffect = BlurEffect(radius = 10f, edgeTreatment = TileMode.Clamp)
}
```

Supported effects:
- **BlurEffect** — Gaussian blur.
- **RuntimeShaderEffect** (API 33+) — AGSL shader-based effect.
- Composite effects через `composer()`.

---

## Invalidation model

graphicsLayer — **Skia Layer**. Создание layer дорого, но дальнейшие transformations — cheap (GPU-side composition).

Каждый change of graphicsLayer properties — recomposition + redraw. Для 60 FPS animations — smooth.

**Gotcha:** don't animate too many graphicsLayer properties одновременно — layer composition stacks up.

---

## Compositing strategies

```kotlin
Modifier.graphicsLayer {
    compositingStrategy = CompositingStrategy.Offscreen
    // или
    compositingStrategy = CompositingStrategy.ModulateAlpha
}
```

`Offscreen` — render в separate buffer, then composite. Нужно для non-standard blend modes, alpha + dropshadow combinations.

`ModulateAlpha` — alpha applied directly на composition, no offscreen buffer. Cheaper.

Default — `Auto` (compiler chooses).

---

## Performance

graphicsLayer per composable:
- **OK:** десятки с simple properties (alpha, rotation).
- **OK:** несколько с blur/complex effects.
- **NOT OK:** сотни с offscreen compositing.

Profile через Android GPU Inspector. Layers appear как separate operations в timeline.

---

## Связь

[[compose-canvas-drawscope-deep]] — custom drawing внутри layer.
[[agsl-runtime-shader-compose]] — RuntimeShader + renderEffect.
[[android-compose-internals]] — how graphicsLayer works under the hood.
[[androidexternalsurface-vs-embedded]] — 3D rendering в Compose (real 3D).

---

## Источники

- **Compose graphics modifiers.** [developer.android.com/develop/ui/compose/graphics/draw/modifiers](https://developer.android.com/develop/ui/compose/graphics/draw/modifiers).

---

## Проверь себя

> [!question]- Можно ли через graphicsLayer сделать настоящий 3D scene?
> Нет. graphicsLayer применяет 2D transformations с pseudo-3D projection (cameraDistance). Содержимое — всё ещё flat 2D composable. Для true 3D — AndroidExternalSurface + Filament.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Custom drawing | [[compose-canvas-drawscope-deep]] |
| True 3D | [[androidexternalsurface-vs-embedded]] |
| Shader effects | [[agsl-runtime-shader-compose]] |

---

*Deep-dive модуля M9.*

---
title: "Compose Canvas и DrawScope: 2D-графика в Jetpack Compose"
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
  - "[[android-canvas-drawing]]"
  - "[[agsl-runtime-shader-compose]]"
  - "[[graphicslayer-modifier-deep]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[android-compose]]"
primary_sources:
  - url: "https://developer.android.com/develop/ui/compose/graphics/draw/overview"
    title: "Jetpack Compose: Graphics drawing overview"
    accessed: 2026-04-20
reading_time: 12
difficulty: 3
---

# Compose Canvas и DrawScope

Jetpack Compose предоставляет два главных способа custom graphics: **`Canvas` composable** (с DrawScope) и **`Modifier.drawBehind / drawWithContent`**. Под капотом — Skia через AOSP HWUI. Не-3D, но critical для UI effects, data visualization, particle effects в UI.

## Под капотом — Skia + HWUI

DrawScope operations transparently convert:
1. `drawCircle(...)` → Skia `SkCanvas::drawCircle(...)`.
2. Skia queues in DisplayList.
3. HWUI RenderThread picks up DisplayList.
4. Translated к OpenGL ES или Vulkan commands (depending on backend).
5. GPU renders to framebuffer.
6. SurfaceFlinger composes.

Performance — HWUI caches DisplayList. Если DrawScope commands unchanged — no retranslation. Cached display list replayed fast.

## Когда использовать

**Идеально подходит для:**
- Charts, graphs, data visualization.
- Custom progress indicators.
- Particle-like UI effects.
- Custom shapes (rounded rects с unique corners, star shapes, etc.).
- Drawing over existing composables (overlays, badges).
- Simple 2D games (puzzle, card games).

**Не подходит для:**
- 3D rendering (use AndroidExternalSurface + Filament).
- Massive particle systems (thousands of particles) — use Compute shader.
- Real-time photo/video effects — use RenderEffect + AGSL.
- Procedural noise/patterns — use AGSL shader.

## Performance considerations

Каждый DrawScope operation has cost:
- Simple shape (line, rect, circle): ~1-5 μs.
- Path drawing (complex): 10-50 μs.
- Text rendering: 20-100 μs.
- Image drawing (cached): ~2-10 μs.
- Image drawing (uncached): 50+ ms (trigger initial upload).

Budget per frame: 16 ms @ 60 FPS. Allows thousands simple shapes.

**State changes are cheap** в DrawScope — Skia handles batching internally. Но too many layers (graphicsLayer modifications) can hurt.

## Connection к RenderEffect

DrawScope output можно pipe через RenderEffect:

```kotlin
Canvas(modifier = Modifier
    .size(200.dp)
    .graphicsLayer {
        renderEffect = BlurEffect(
            radiusX = 20f, radiusY = 20f,
            edgeTreatment = TileMode.Decal
        )
    }
) {
    drawCircle(Color.Blue, radius = 80f)
}
```

Blur applied post-draw. GPU-accelerated.

---

---

## Canvas composable

```kotlin
Canvas(modifier = Modifier.fillMaxSize()) {
    drawCircle(
        color = Color.Red,
        radius = 100f,
        center = Offset(center.x, center.y)
    )
}
```

`DrawScope` — receiver с методами: `drawCircle`, `drawRect`, `drawLine`, `drawPath`, `drawImage`, `drawText`, etc.

---

## drawBehind / drawWithContent

`drawBehind` — рисует перед контентом:

```kotlin
Text("Hello",
    modifier = Modifier.drawBehind {
        drawRect(color = Color.Yellow)
    }
)
```

`drawWithContent` — full control над order:

```kotlin
modifier = Modifier.drawWithContent {
    drawContent()  // explicitly draw child
    drawRect(Color.Blue, style = Stroke(2f))  // overlay
}
```

---

## DrawScope API

### Primitives

```kotlin
drawLine(color, start, end, strokeWidth)
drawRect(color, topLeft, size, style)
drawCircle(color, radius, center)
drawOval(color, topLeft, size)
drawArc(color, startAngle, sweepAngle, useCenter, topLeft, size)
drawPath(path, color, style)
drawPoints(points, pointMode, color, strokeWidth)
```

### Bitmaps и images

```kotlin
drawImage(imageBitmap, topLeftOffset)
drawImage(imageBitmap, srcOffset, srcSize, dstOffset, dstSize)
```

### Text

```kotlin
drawText(textMeasurer, "Hello", topLeft, style = ...)
```

### Transformations

```kotlin
withTransform({
    translate(left = 100f)
    rotate(degrees = 45f, pivot = center)
    scale(scaleX = 2f, scaleY = 2f)
}) {
    drawCircle(Color.Red, 50f)
}
```

### Clip

```kotlin
clipRect(left = 0f, top = 0f, right = 200f, bottom = 200f) {
    drawCircle(Color.Blue, 300f)  // clipped
}
```

### Blend modes (Porter-Duff)

```kotlin
drawCircle(color = Color.Red, blendMode = BlendMode.Multiply)
```

---

## Под капотом: Skia

Compose `DrawScope` commands → Skia commands → SurfaceFlinger / HWUI. Performance:
- Hardware-accelerated on GPU.
- Но CPU-side: composition of Canvas operations into Skia batches happens on CPU.
- Not true immediate GPU access — abstracted through Skia.

Implication: very simple primitives, тысячи штук, — fine. Complex operations — может быть slow.

---

## Path rendering

```kotlin
val path = Path().apply {
    moveTo(0f, 0f)
    quadraticBezierTo(100f, 0f, 100f, 100f)
    lineTo(200f, 100f)
    close()
}

drawPath(path, color = Color.Black, style = Stroke(5f))
```

Кривые Безье, arcs, custom shapes.

---

## Performance

Для real-time animation (60 FPS):
- **OK:** десятки простых primitives (rectangles, circles, lines).
- **OK:** moderate path drawing.
- **NOT OK:** тысячи complex paths per frame.
- **NOT OK:** per-pixel operations.

Для heavy effects — use **AGSL RuntimeShader** через `RenderEffect` ([[agsl-runtime-shader-compose]]), GPU-accelerated.

---

## Composable-specific patterns

### Animated drawings

```kotlin
val progress by animateFloatAsState(targetValue = if (show) 1f else 0f)

Canvas(modifier = Modifier.size(100.dp)) {
    drawArc(
        color = Color.Blue,
        startAngle = 0f,
        sweepAngle = 360f * progress,
        useCenter = false,
        style = Stroke(10f)
    )
}
```

Recomposition triggers redraw каждый frame во время animation.

### Interactive drawing (touch)

```kotlin
val lines = remember { mutableStateListOf<Line>() }

Canvas(modifier = Modifier.fillMaxSize()
    .pointerInput(Unit) {
        detectDragGestures { change, dragAmount ->
            lines.add(Line(change.position - dragAmount, change.position))
        }
    }
) {
    lines.forEach { drawLine(Color.Black, it.start, it.end, strokeWidth = 3f) }
}
```

---

## Связь

[[android-canvas-drawing]] — underlying Canvas API (View system).
[[agsl-runtime-shader-compose]] — for GPU-accelerated effects.
[[graphicslayer-modifier-deep]] — 2D transforms and pseudo-3D.
[[android-compose-internals]] — Compose rendering pipeline.

---

## Источники

- **Jetpack Compose graphics docs.** [developer.android.com/develop/ui/compose/graphics/draw/overview](https://developer.android.com/develop/ui/compose/graphics/draw/overview).

---

## Проверь себя

> [!question]- Когда использовать Canvas composable vs drawBehind?
> `Canvas` — когда графика primary content. `drawBehind` — backgrounds, borders, effects за contents. `drawWithContent` — full control, custom composition.

---

## Куда дальше

| Направление | Куда |
|---|---|
| GPU effects | [[agsl-runtime-shader-compose]] |
| Transforms | [[graphicslayer-modifier-deep]] |

---

*Deep-dive модуля M9.*

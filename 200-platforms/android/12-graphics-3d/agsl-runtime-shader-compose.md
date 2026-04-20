---
title: "AGSL и RuntimeShader: GPU-шейдеры прямо в Jetpack Compose"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/shaders
  - topic/compose
  - type/deep-dive
  - level/intermediate
related:
  - "[[glsl-language-deep]]"
  - "[[shader-programming-fundamentals]]"
  - "[[compose-canvas-drawscope-deep]]"
  - "[[android-canvas-drawing]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[glsl-language-deep]]"
  - "[[android-compose]]"
primary_sources:
  - url: "https://developer.android.com/develop/ui/views/graphics/agsl"
    title: "Android: AGSL — Android Graphics Shading Language"
    accessed: 2026-04-20
  - url: "https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl"
    title: "Android: Using AGSL in apps"
    accessed: 2026-04-20
  - url: "https://github.com/drinkthestars/shady"
    title: "Shady — AGSL helper library for Compose"
    accessed: 2026-04-20
reading_time: 12
difficulty: 4
---

# AGSL: Android Graphics Shading Language

AGSL (Android Graphics Shading Language) — упрощённый shader language для Android, введённый в API level 33 (Android 13, 2022). Позволяет писать GPU-ускоренные 2D shader effects прямо в приложениях без углубления в Vulkan. Runs через `RuntimeShader` в Canvas и Compose.

---

## Зачем AGSL

До API 33 custom graphics effects на Android означали либо:
- Слой **OpenGL ES** с `GLSurfaceView` (heavy setup).
- **Bitmap-manipulation** на CPU (slow).

AGSL закрыл gap: GPU shader effects без full 3D pipeline, доступен для UI-level graphics.

Use cases:
- Wave distortion.
- Liquid glass / frosted glass.
- Noise patterns.
- Color grading.
- Custom blurs.
- Animated gradients.

---

## Что AGSL — и что НЕ AGSL

**AGSL ≈ GLSL fragment shader**. Syntax похож, но limited:
- Только fragment-like shading.
- No vertex shader (работает с existing rasterization).
- No compute shader.
- Simplified type system.
- No discard.

Internally, AGSL compiles в **Skia SkSL** (Skia's shading language) — Skia executes shader на GPU (GL ES / Vulkan under the hood). Hence name: Android Graphics Shading Language → Skia Shading Language.

---

## Basic syntax

```glsl
uniform float2 iResolution;
uniform float iTime;
uniform shader iImage;  // input image (previous rendering)

half4 main(float2 fragCoord) {
    float2 uv = fragCoord / iResolution;
    
    // Wave distortion
    uv.x += sin(uv.y * 10.0 + iTime) * 0.02;
    
    return iImage.eval(uv * iResolution);
}
```

Key differences от GLSL:
- `half4` вместо `vec4` (mediump default).
- Entry point `main(float2 fragCoord) → half4` вместо global `main() { ... }`.
- `shader` type for sampling input images.
- `eval()` метод для sample — возвращает color at position.

---

## Using AGSL in Kotlin

```kotlin
val waveShader = RuntimeShader("""
    uniform float2 iResolution;
    uniform float iTime;
    uniform shader iImage;
    
    half4 main(float2 fragCoord) {
        float2 uv = fragCoord / iResolution;
        uv.x += sin(uv.y * 10.0 + iTime) * 0.02;
        return iImage.eval(uv * iResolution);
    }
""".trimIndent())

// Set uniforms
waveShader.setFloatUniform("iResolution", width.toFloat(), height.toFloat())
waveShader.setFloatUniform("iTime", timeSeconds)
waveShader.setInputShader("iImage", backgroundShader)
```

---

## Compose integration

### RenderEffect modifier

```kotlin
@Composable
fun WavyImage() {
    val time by produceState(0f) {
        while (true) {
            value = System.nanoTime() / 1e9f
            withFrameNanos {}
        }
    }
    
    val shader = remember { RuntimeShader(WAVE_SHADER_SOURCE) }
    
    LaunchedEffect(time) {
        shader.setFloatUniform("iTime", time)
    }
    
    Image(
        painter = painterResource(R.drawable.background),
        contentDescription = null,
        modifier = Modifier
            .graphicsLayer {
                renderEffect = RenderEffect.createRuntimeShaderEffect(
                    shader, "iImage"
                ).asComposeRenderEffect()
            }
    )
}
```

Каждый recomposition с обновлённым `iTime` → GPU re-runs shader.

### DrawScope в Canvas

```kotlin
@Composable
fun NoiseCanvas() {
    val shader = remember { RuntimeShader(NOISE_SHADER) }
    
    Canvas(modifier = Modifier.fillMaxSize()) {
        shader.setFloatUniform("iResolution", size.width, size.height)
        val paint = Paint().apply { this.shader = shader }
        drawRect(Color.White, size = size)
        drawIntoCanvas { canvas ->
            canvas.nativeCanvas.drawPaint(paint.asFrameworkPaint())
        }
    }
}
```

---

## Performance

AGSL shaders:
- **First run:** compiled on device. ~50-200 ms initial delay.
- **Cached:** subsequent runs instant.
- **Per-frame:** O(1) GPU dispatch, ~1 ms для simple shaders.

Очень эффективен для UI effects: blur, gradient, noise — все GPU-accelerated.

---

## Limitations

- API level 33+ (Android 13+). Fallback needed для older devices.
- Only fragment-like shading. No geometry manipulation.
- Shader source компилируется device-side (не pre-compiled SPIR-V).
- Limited debugging tools vs full Vulkan.

---

## Shady library

[Shady](https://github.com/drinkthestars/shady) — open-source library, упрощает AGSL в Compose:

```kotlin
ShadyShader(
    source = WAVE_SHADER,
    uniforms = mapOf(
        "iTime" to time,
    )
)
```

Удобные composables для common patterns.

---

## Examples

### Blur

```glsl
uniform shader iImage;
uniform float iRadius;

half4 main(float2 fragCoord) {
    half4 color = half4(0);
    for (int i = -4; i <= 4; i++) {
        for (int j = -4; j <= 4; j++) {
            float2 offset = float2(i, j) * iRadius / 4.0;
            color += iImage.eval(fragCoord + offset);
        }
    }
    return color / 81.0;
}
```

### Gradient noise

```glsl
uniform float2 iResolution;
uniform float iSeed;

float hash(float2 p) {
    return fract(sin(dot(p, float2(127.1, 311.7)) + iSeed) * 43758.5453);
}

half4 main(float2 fragCoord) {
    float2 uv = fragCoord / iResolution;
    float n = hash(floor(uv * 20.0));
    return half4(n, n, n, 1);
}
```

---

## Связь

[[shader-programming-fundamentals]] — general shader context.
[[glsl-language-deep]] — AGSL subset of GLSL.
[[compose-canvas-drawscope-deep]] — where AGSL lives в Compose.
[[android-canvas-drawing]] — Canvas-level usage.

---

## Источники

- **Android AGSL guide.** [developer.android.com/develop/ui/views/graphics/agsl](https://developer.android.com/develop/ui/views/graphics/agsl).
- **Using AGSL in apps.** [developer.android.com/develop/ui/views/graphics/agsl/using-agsl](https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl).
- **Shady library.** [github.com/drinkthestars/shady](https://github.com/drinkthestars/shady).

---

## Проверь себя

> [!question]- Когда использовать AGSL vs full Vulkan?
> AGSL — для 2D GPU effects в Compose/View UI. Simple setup, no manual pipeline. Vulkan — для 3D scenes, complex rendering, performance-critical. Перекрытие минимальное.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Compose integration | [[compose-canvas-drawscope-deep]] |
| Full shader theory | [[shader-programming-fundamentals]] |

---

*Deep-dive модуля M5.*

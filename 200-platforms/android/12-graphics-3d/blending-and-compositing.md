---
title: "Blending и compositing: alpha, premultiplied, Porter-Duff"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - type/deep-dive
  - level/intermediate
related:
  - "[[rendering-pipeline-overview]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[overdraw-and-blending-cost]]"
  - "[[android-canvas-drawing]]"
  - "[[android-graphics-3d-moc]]"
prerequisites:
  - "[[rendering-pipeline-overview]]"
primary_sources:
  - url: "https://dl.acm.org/doi/10.1145/800031.808606"
    title: "Porter, T. & Duff, T. (1984). Compositing Digital Images. SIGGRAPH"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap28.html#framebuffer-blending"
    title: "Vulkan 1.4: Blending spec"
    accessed: 2026-04-20
  - url: "https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl"
    title: "Android: AGSL and blending"
    accessed: 2026-04-20
reading_time: 18
difficulty: 4
---

# Blending и compositing

Когда в [[case-ikea-place-ar|IKEA Place]] виртуальный стеклянный стол накладывается на реальную комнату, GPU выполняет **alpha blending** — комбинирует цвет виртуального объекта с цветом фона по формуле из Porter-Duff 1984. Когда Compose renders UI поверх 3D-сцены, SurfaceFlinger делает **compositing** — объединение слоев с помощью того же математического аппарата. Все эти операции — в ROP (Render Output Unit) на GPU или в Hardware Composer. Знание теории blending открывает правильную работу с прозрачностью, antialiasing, particle effects, UI overlay.

---

## Зачем это знать

**Первое.** Premultiplied vs straight alpha — вечный источник багов. Текстура в одной конвенции, shader ожидает другую → цвета выглядят "грязно" или "размыто".

**Second.** Blending порядок критичен. Неправильный sort transparent objects → incorrect rendering. No general solution (order-independent transparency — research topic).

**Third.** Blending — дорогой на IMR GPU, дешёвый на TBR. Знание помогает делать правильные compromises.

---

## Терминология

| Термин | Что |
|---|---|
| Alpha | Компонента прозрачности (0 = прозрачный, 1 = непрозрачный) |
| Straight alpha | RGB и A хранятся независимо |
| Premultiplied alpha | RGB уже умножено на A; `(0.5, 0.5, 0.5, 0.5)` = полупрозрачный grey |
| Source (src) | Fragment рассчитанный shader'ом |
| Destination (dst) | Уже в framebuffer |
| Blend factor | Коэффициент, на который умножается src или dst |
| Porter-Duff | Tom Porter + Tom Duff 1984 — формализация compositing operators |
| Over operator | `src + dst · (1-srcAlpha)` — стандартный alpha blend |
| Compositor | Separate stage/hardware that combines layers (SurfaceFlinger на Android) |

---

## Теоретические основы

### Blending equation

```
result.rgb = src.rgb · srcFactor + dst.rgb · dstFactor
result.a   = src.a · srcFactorA + dst.a · dstFactorA
```

GPU hardware позволяет configurable factors:

| Factor | Formula |
|---|---|
| ZERO | 0 |
| ONE | 1 |
| SRC_ALPHA | srcA |
| ONE_MINUS_SRC_ALPHA | 1 - srcA |
| DST_ALPHA | dstA |
| ONE_MINUS_DST_ALPHA | 1 - dstA |
| SRC_COLOR | src RGB |
| DST_COLOR | dst RGB |

### Common modes

**Opaque:** `(ONE, ZERO)` — просто write src, ignore dst. Default для 3D-меши.

**Straight alpha blend (over):** `(SRC_ALPHA, ONE_MINUS_SRC_ALPHA)`. Самый распространённый для transparent geometry.

**Premultiplied alpha over:** `(ONE, ONE_MINUS_SRC_ALPHA)`. Если src.rgb уже предварительно умножен на src.a.

**Additive (additive blending):** `(ONE, ONE)`. Для огня, glow, particles. Делает светлее (не превышает 1, clamped).

**Multiplicative:** `(DST_COLOR, ZERO)`. Уменьшает яркость dst. Для shadows-as-overlay.

### Straight vs premultiplied

**Straight:** текстура хранит (R, G, B, A) независимо. При sampling в shader с alpha blending:

```
vec4 t = texture(sampler, uv);  // straight: (0.8, 0.2, 0.1, 0.5)
fragColor = t;
// Blend: result = t.rgb * 0.5 + dst.rgb * 0.5 = (0.4, 0.1, 0.05) + dst*0.5
```

**Premultiplied:** RGB уже умножен на A. `(0.8, 0.2, 0.1, 0.5)` → `(0.4, 0.1, 0.05, 0.5)`. Blending:

```
vec4 t = texture(sampler, uv);  // premultiplied: (0.4, 0.1, 0.05, 0.5)
fragColor = t;
// Blend: result = t.rgb + dst.rgb * (1 - 0.5) = (0.4, 0.1, 0.05) + dst*0.5
```

**Результаты совпадают!** Разница — в какой момент multiplication происходит: premultiplied — при создании asset, straight — во время shading.

**Преимущества premultiplied:**
- Filtering работает correctly (straight alpha даёт dark fringes на mipmaps).
- Blending math проще (один multiply).
- Правильно работает с interpolation.

**Filament, Jetpack Compose, современные engines** — все используют premultiplied. Assets должны быть premultiplied в pipeline (tooling or runtime).

### Porter-Duff (1984)

12 операторов compositing для двух слоёв:

- **Over** (A over B): A opaque, show A; A transparent, show B. Самый важный.
- **In** (A in B): show A там где B, иначе нечего.
- **Out** (A out B): show A там где НЕ B.
- **Atop** (A atop B): show A over B но только где B.
- **Xor**: show A + B minus intersection.

На Android Canvas — `PorterDuff.Mode.{SRC_OVER, SRC_IN, SRC_OUT, ...}`. На GPU (Vulkan) через blend factors. Всё это — разные комбинации вышеуказанных 8 factors.

### Compositing on Android

- **GPU blending** (ROP): внутри одного render pass/framebuffer.
- **Hardware Composer (HWC)**: compositing separate swapchain layers на display. Пример: 3D-surface + UI-surface + System UI = 3 layers, composited HWC при displaying.
- **SurfaceFlinger**: orchestrates HWC, fallback на GPU compositing если HWC не справляется.

---

## Уровень 2 — практика

### Transparent sorting

Transparent objects must be rendered **back-to-front** для corrrect blending. Opaque — front-to-back для early-Z.

Filament workflow:
1. Opaque render pass (all opaque, depth write).
2. Transparent render pass (sorted back-to-front, depth read-only — test but not write).

### Glass table в IKEA Place

```cpp
VkPipelineColorBlendAttachmentState glassBlend = {
    .blendEnable = VK_TRUE,
    .srcColorBlendFactor = VK_BLEND_FACTOR_ONE,  // premultiplied
    .dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA,
    .colorBlendOp = VK_BLEND_OP_ADD,
    .srcAlphaBlendFactor = VK_BLEND_FACTOR_ONE,
    .dstAlphaBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA,
    .alphaBlendOp = VK_BLEND_OP_ADD,
    .colorWriteMask = VK_COLOR_COMPONENT_R_BIT | ... | VK_COLOR_COMPONENT_A_BIT,
};
```

Depth test: on. Depth write: off (transparent объекты не маскируют за собой).

### Cost on TBR

TBR: blending read/write в tile memory — ~0 cost. Дополнительные fragment shader invocations — вот что стоит.

IMR: blending requires ROP read-modify-write в DRAM — существенно дороже.

---

## Подводные камни

### Ошибка 1: mixing straight and premultiplied в pipeline

**Как избежать:** устанавливайте одну конвенцию для всего pipeline. Premultiplied рекомендуется.

### Ошибка 2: depth write на transparent

**Как избежать:** для transparent — depth test yes, depth write no.

### Ошибка 3: transparent sort скверный

**Как избежать:** sort back-to-front каждый frame, или использовать OIT methods (weighted blended OIT).

---

## Связь с другими темами

[[rendering-pipeline-overview]] — blending как stage 16.
[[tile-based-rendering-mobile]] — blending cost на TBR.
[[overdraw-and-blending-cost]] — cost analysis.
[[android-canvas-drawing]] — PorterDuff.Mode в Canvas.

---

## Источники

- **Porter, T. & Duff, T. (1984). Compositing Digital Images.** SIGGRAPH. [ACM DOI](https://dl.acm.org/doi/10.1145/800031.808606). Классика.
- **Vulkan 1.4 Spec, framebuffer blending.** [registry.khronos.org](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap28.html#framebuffer-blending).
- **Akenine-Möller et al. (2018). RTRT 4, chapter 5 (Shading Basics).**

---

## Проверь себя

> [!question]- Premultiplied или straight alpha для mobile textures?
> Premultiplied в современной практике. Filtering корректен, blending проще, нет dark fringes на mipmaps. Устанавливайте один standard для всего pipeline.

> [!question]- Почему opaque рендерится front-to-back, transparent — back-to-front?
> Opaque front-to-back enables early-Z (скрытые отбрасываются). Transparent back-to-front даёт correct blending — каждый слой correctly accumulates.

---

## Ключевые карточки

Какой Porter-Duff operator — самый используемый?
?
Over (A over B): `src.rgb + dst.rgb * (1 - src.a)`. Стандартный alpha blend для транспарентных объектов поверх непрозрачных.

---

Что такое premultiplied alpha?
?
Convention where RGB в текстуре уже умножен на A. Filament, Compose, современные engines — все premultiplied.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Overdraw cost | [[overdraw-and-blending-cost]] |
| 2D на Android | [[android-canvas-drawing]] |
| Pipeline stages | [[rendering-pipeline-overview]] |

---

*Deep-dive модуля M2.*

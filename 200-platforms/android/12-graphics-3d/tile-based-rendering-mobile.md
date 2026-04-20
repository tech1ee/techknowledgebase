---
title: "Tile-Based Rendering на мобилке: почему Adreno, Mali, PowerVR не похожи на desktop GPU"
created: 2026-04-20
modified: 2026-04-20
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/gpu-hardware
  - type/deep-dive
  - level/intermediate
related:
  - "[[gpu-architecture-fundamentals]]"
  - "[[android-graphics-3d-moc]]"
  - "[[rendering-pipeline-overview]]"
  - "[[overdraw-and-blending-cost]]"
  - "[[vulkan-on-android-fundamentals]]"
prerequisites:
  - "[[gpu-architecture-fundamentals]]"
primary_sources:
  - url: "https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/the-mali-gpu-an-abstract-machine-part-2---tile-based-rendering"
    title: "Arm: The Mali GPU: An Abstract Machine Part 2 — Tile-Based Rendering"
    accessed: 2026-04-20
  - url: "https://docs.imgtec.com/starter-guides/powervr-architecture/html/topics/tile-based-deferred-rendering-index.html"
    title: "Imagination PowerVR: Tile-Based Deferred Rendering documentation"
    accessed: 2026-04-20
  - url: "https://blog.imaginationtech.com/a-look-at-the-powervr-graphics-architecture-tile-based-rendering/"
    title: "Imagination blog: PowerVR Graphics Architecture — Tile-Based Rendering"
    accessed: 2026-04-20
  - url: "https://en.wikipedia.org/wiki/Tiled_rendering"
    title: "Wikipedia: Tiled rendering"
    accessed: 2026-04-20
  - url: "https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap8.html#renderpass"
    title: "Vulkan 1.4: Render Pass (designed for TBR)"
    accessed: 2026-04-20
  - url: "https://developer.android.com/games/optimize/vulkan-prerotation"
    title: "Android: Vulkan pre-rotation for tile-based GPUs"
    accessed: 2026-04-20
reading_time: 24
difficulty: 5
---

# Tile-Based Rendering на мобилке

Когда десктопная игра работает на NVIDIA GeForce, GPU **немедленно** рисует каждый треугольник: получил draw call → выполнил fragment shader → записал пиксели в framebuffer в VRAM. Эта архитектура называется **Immediate Mode Rendering (IMR)**. Она проста, но расточительна: далёкие объекты рисуются и тут же переписываются ближними; VRAM bandwidth на framebuffer — десятки GB/s.

Мобильные GPU работают принципиально иначе. Adreno, Mali, PowerVR и Xclipse используют **Tile-Based Rendering (TBR)**, а PowerVR и Apple AGX — ещё более агрессивный вариант **Tile-Based Deferred Rendering (TBDR)**. Каждый кадр делится на **тайлы** (16×16 или 32×32 пикселя), и GPU обрабатывает один тайл целиком в **on-chip SRAM**, до записи в глобальный framebuffer. Результат — дикое снижение bandwidth (tile'a помещается в кеш, который «бесплатен» по энергии) и часто **hidden surface removal до fragment shading** (TBDR), что убирает overdraw бесплатно.

Этот файл — второй deep-dive модуля M2. После него станет понятно, почему плохой render pass дизайн убивает FPS на мобилке больше, чем бюджет ALU; почему Vulkan's `VkRenderPass` существует (именно для TBR); почему pre-rotation в Android важен; и почему [[case-planner-5d|Planner 5D]], [[case-ikea-place-ar|IKEA Place]] и все серьёзные мобильные 3D-приложения архитектурно оптимизированы вокруг tile-based концепции.

---

## Зачем это знать

**Первое — bandwidth optimization.** Обычная 1080p-сцена при 60 FPS с 4× overdraw на IMR-GPU требует около 6 GB/s framebuffer bandwidth. На TBR при правильно спроектированных render pass'ах это снижается до менее 1 GB/s. Разница в 6 раз в потреблении bandwidth на мобилке — разница между 2 часами игры и 40 минутами до разрядки.

**Второе — render pass design.** Vulkan-приложение на Android обязано правильно использовать `VkRenderPass` с load/store operations. Если в начале render pass указать `VK_ATTACHMENT_LOAD_OP_LOAD` когда можно `CLEAR`, GPU вынужден загрузить весь предыдущий framebuffer в tile memory — potentially 8 MB per frame при 1080p. Это один из самых частых Vulkan-antipatterns на мобилке.

**Третье — pre-rotation.** Android телефон rotates между portrait и landscape. Если приложение не хэндлит pre-rotation явно (через VK_SURFACE_TRANSFORM_...), композитор делает дополнительный rotation pass — ещё один проход через tile memory, ещё один write в framebuffer. Pre-rotation избавляет от этого. На Galaxy S24 это могло дать 15% FPS boost в Vulkan-играх.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[gpu-architecture-fundamentals]] | Понимание warp'ов и SIMT — на этом работает tile rendering |
| [[vectors-in-3d-graphics]], [[matrices-for-transformations]] | Vertex processing pipeline |

---

## Терминология

| Термин | Определение | Примечание |
|---|---|---|
| IMR (Immediate Mode Rendering) | Классический подход: геометрия → rasterize → fragment → framebuffer сразу | Desktop NVIDIA, AMD discrete |
| TBR (Tile-Based Rendering) | Геометрия обрабатывается, сохраняется per-tile parameter lists, потом tile за tile | Mali (Bifrost, Valhall), Adreno, некоторые desktop Intel Gen GPU |
| TBDR (Tile-Based Deferred Rendering) | TBR + hidden surface removal **до** fragment shading | PowerVR, Apple AGX, Exynos Xclipse |
| Tile | Прямоугольная область экрана (16×16, 32×32, 64×64 пикселя), помещающаяся в on-chip SRAM | Основная единица работы мобильного GPU |
| Tile memory | On-chip SRAM для хранения колор и depth буфера во время tile-рендеринга | Очень быстрая, очень маленькая (~128–256 KB) |
| Binning | Процесс назначения primitives каждому tile | Stage 1 of TBR |
| Parameter buffer | Glob memory, куда сохраняются per-tile primitive lists | Tile может требовать MB |
| Render pass | В Vulkan — граница, внутри которой GPU знает, что происходит в tile memory | Критичная абстракция для mobile |
| Load op | Что делать в начале render pass: clear, load (из framebuffer), don't care | Clear или don't care — бесплатно, load — дорого |
| Store op | Что делать в конце: store (в framebuffer), don't care | Don't care — бесплатно (tile memory просто dropped) |
| Pre-rotation | Приложение само делает rotation geometry для матча физической orientation экрана | Альтернатива — composition-time rotation |
| AFBC (Arm Frame Buffer Compression) | ARM proprietary lossless compression для framebuffer tiles | Mali GPUs only |

---

## Историческая справка

Tile-based rendering не был изобретён для мобильных устройств — его origin лежит в academic research 1980-х, когда проблема bandwidth была одинаково болезненной и на рабочих станциях.

- **1983 — Pixel-Planes 3 (Fuchs et al., UNC Chapel Hill).** Первая parallel-rasterizer архитектура с scan-line декомпозицией. Ещё не tile, но заложила идею параллельной обработки экрана кусками.
- **1987 — Pixel-Planes 4 (Fuchs, Poulton).** Формальная academic TBR-архитектура. Экран делится на blocks, parallel processors обрабатывают независимо. Опубликована на SIGGRAPH'87.
- **1993 — Pixel-Planes 5 / PixelFlow.** Commercial incarnation idea. ~$500k рабочая станция.
- **1995 — PowerVR Series1 (NEC PCX1).** Videologic (спин-офф ImgTec) сделала first consumer TBDR chip, для PC. 500 000 проданных юнитов.
- **1996 — PowerVR Series2 в Sega Dreamcast.** TBDR в массовой потребительской консоли. Выживаемость идеи доказана.
- **2001 — PowerVR MBX.** Первый mobile-targeted PowerVR. Использован в TI OMAP, позже в iPhone 2G/3G/3GS.
- **2005+ — PowerVR SGX в первых смартфонах** (iPhone 3GS/4/4S, ранние Android — HTC Magic/Hero).
- **2007 — ARM Mali-200.** Первая ARM TBR. Не TBDR — ARM целеустремлённо выбрала чистый TBR для упрощения hardware и экономии die-area.
- **2012 — Qualcomm Adreno 320.** «Flex render»: может переключаться между TBR (mobile-style) и Direct Mode (desktop-style IMR) в зависимости от scene complexity. Driver определяет автоматически.
- **2014 — Apple A8 (custom PowerVR GX6450).** Apple начинает кастомизировать PowerVR под iOS workloads.
- **2016 — Vulkan 1.0.** `VkRenderPass` — первый API который сделал TBR semantics first-class. До Vulkan, OpenGL ES driver'ы были вынуждены inferring tile boundaries эвристиками — часто ошибались.
- **2018 — Apple A11 Bionic (AGX 1st gen).** Apple dropped PowerVR licensing, сделала собственный TBDR engine. ImgTec financial crisis последствие.
- **2020 — Apple M1 (AGX 2nd gen) desktop.** TBDR впервые вернулся на desktop через Mac. Desktop games вынужденно учитывать tile behaviour.
- **2021 — Mali-G710 (Valhall architecture).** Command Stream Frontend 2.0, улучшенная tiling compression.
- **2023 — ARM Immortalis G720 (5th Gen Valhall).** Hardware ray tracing units поверх TBR — гибридная архитектура.
- **2024 — Imagination B-Series (Photon).** Возвращение Imagination в mobile race с PVRIC4 compression.
- **2026 — Samsung Xclipse 960 (RDNA4-based).** AMD архитектура с Samsung tiling cache; не полный TBR, но bandwidth-aware IMR.
- **2026 (April) — Qualcomm Adreno 830 (Snapdragon 8 Elite Gen 4).** Sliced rendering — tiling cache + cluster culling. Ближе всего к TBDR из Adreno-линейки.

Почему академическая идея 1987 года заняла 20 лет чтобы стать mainstream? Ответ — **bandwidth economics**. В 1990-х VRAM был быстрым относительно GPU arithmetic (GPU был слабым). Начиная с мобилки 2000-х arithmetic стал дёшев, а bandwidth — дорог (mobile имеет shared LPDDR с CPU, и energy per byte access в 100× выше arithmetic). TBR идеально матчит этот disbalance. Этот же disbalance теперь приходит и на desktop — M1, Xclipse — значит tile-based thinking станет универсальным, а не только мобильным.

---

## Теоретические основы

### Почему именно tile-based на мобилке

Мобильный телефон ограничен **тремя метриками** одновременно:
1. **Энергопотребление.** Внешний DRAM access — ~100 pJ/byte, on-chip SRAM — ~1 pJ/byte. 100× разница.
2. **Bandwidth.** Внешний DRAM — 30–100 GB/s. Внутренний SRAM — TB/s пропускная.
3. **Тепло.** Frame buffer access → DRAM read/write → тепло → thermal throttling.

Rendering целого framebuffer в on-chip SRAM (tile) полностью убирает затраты 1 и 2 для самой дорогой операции (ROP reads/writes). Pixel shading → tile memory → в конце tile dump в framebuffer. Один write per pixel вместо многих.

### TBR pipeline

```
Phase 1: Vertex / Tiling
┌─────────────────────────────────────────────┐
│  Vertex shader выполняется для всех         │
│  вершин scene                                │
│  Primitives отсортированы по тайлам         │
│  (binning)                                  │
│  Tile lists хранятся в parameter buffer     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
Phase 2: Fragment / Rendering (tile by tile)
┌─────────────────────────────────────────────┐
│  Для каждого tile:                          │
│  1. Load tile memory (clear or load op)     │
│  2. Execute fragment shaders for all prims  │
│     в этом tile (используя tile memory)     │
│  3. Store tile memory в framebuffer         │
│     (store op)                              │
└─────────────────────────────────────────────┘
```

Ключ — фаза 2: весь процесс happens **в SRAM**, без DRAM write до финального store.

### TBDR extension

PowerVR и Apple AGX делают **дополнительную фазу** между 1 и 2: **Hidden Surface Removal (HSR)**. Перед fragment shading, hardware проходит по per-tile primitive list, определяет, какие фрагменты visible, и shader'ит **только видимые**. Overdraw — **ноль** для opaque geometry.

IMR: 4× overdraw scene → 4× fragment shader cost.
TBR: 4× overdraw scene → 4× fragment shader cost (все equally shaded).
TBDR: 4× overdraw scene → 1× fragment shader cost (только ближний).

Это почему AR-приложения на iPhone работают экономичнее: Apple AGX = TBDR.

### Vulkan render pass абстракция

Vulkan API specifically designed for TBR. `VkRenderPass` — «контейнер», внутри которого GPU может:
- Держать attachments в tile memory (никогда не писать в framebuffer).
- Использовать `VK_ATTACHMENT_LOAD_OP_CLEAR` чтобы пропустить чтение framebuffer в начале.
- Использовать `VK_ATTACHMENT_STORE_OP_DONT_CARE` чтобы пропустить write framebuffer в конце (например, для transient attachments).
- Subpass dependencies — оптимизировать multi-pass rendering внутри одной tile invocation.

**Antipattern:** множество маленьких `vkCmdBeginRenderPass` / `vkCmdEndRenderPass`. Каждый end → tile store → tile load → потеря tile optimization.

**Правильно:** как можно больше операций внутри одного render pass. Subpasses для случаев, когда нужен intermediate result (например, G-buffer + lighting).

### Store op и memoryless attachments

Depth/stencil buffer обычно **не нужен** после render pass (используется только для occlusion тестов во время рендера). `VK_ATTACHMENT_STORE_OP_DONT_CARE` говорит GPU: «не записывай в framebuffer после tile, это transient».

В Vulkan 1.1+ также есть **`VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT`** + memoryless memory type — attachment **физически никогда не попадает в DRAM**. Экономия ~6 MB per frame для depth buffer на 1080p.

### Pre-rotation

Когда пользователь поворачивает телефон, физическая orientation дисплея меняется. Приложение должно либо:

**(a)** Рендерить в логической ориентации → композитор делает **rotation pass** (ещё один проход через all tiles). Потеря 10–15% performance.

**(b)** **Pre-rotation**: запросить у Vulkan current transform, применить rotation matrix в vertex shader и рендерить непосредственно в физической ориентации. Композитор ничего не делает.

Google [рекомендует](https://developer.android.com/games/optimize/vulkan-prerotation) pre-rotation для всех Vulkan apps на Android. Godot 4.4 реализовал это в Mobile renderer (март 2026).

---

## Уровень 1 — для начинающих

Представьте, что вы рисуете большую картину на огромном холсте. Плохой способ: работать по всему холсту хаотично — сначала тут мазок, потом там, перебегая туда-сюда. Вы устаёте, теряете время на перемещения.

Хороший способ: разделить холст на маленькие квадратики, полностью закончить один квадратик (все детали, тени, света), потом перейти к следующему. Вы меньше перемещаетесь, меньше устаёте, работаете эффективнее.

Мобильный GPU делает именно так с экраном. Экран 1920×1080 делится на ~8000 квадратиков 16×16 пикселей. GPU обрабатывает один квадратик целиком, в своей внутренней «быстрой памяти» (SRAM), потом записывает результат в основную память телефона. Эта «основная память» медленная и энергозатратная — каждое обращение греет чип и разряжает батарею.

Tile-based rendering позволяет мобильному GPU быть тихим, холодным и эффективным. Но он требует, чтобы программист это понимал — например, не «переначинать» рендер много раз за кадр. Vulkan API специально спроектирован, чтобы делать tile-based работы явными.

---

## Уровень 2 — для студента

### Минимальный render pass с корректным load/store ops

```glsl
// Vulkan render pass attachment description
VkAttachmentDescription colorAttachment = {
    .format = VK_FORMAT_B8G8R8A8_UNORM,
    .samples = VK_SAMPLE_COUNT_1_BIT,
    .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,       // tile освобождается без load
    .storeOp = VK_ATTACHMENT_STORE_OP_STORE,     // финальный тайл → framebuffer
    .stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE,
    .stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,
    .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED,
    .finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
};

VkAttachmentDescription depthAttachment = {
    .format = VK_FORMAT_D32_SFLOAT,
    .samples = VK_SAMPLE_COUNT_1_BIT,
    .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,
    .storeOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,  // depth не нужен после
    ...
};
```

Второй attachment (depth) — с `DONT_CARE`. Если в дополнение он marked `VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT`, это memoryless attachment — экономия ~8 MB per frame.

### Что нельзя (antipattern)

```cpp
// Antipattern 1: множественные render pass
for (model in models) {
    vkCmdBeginRenderPass(cmd, ...);
    drawModel(model);
    vkCmdEndRenderPass(cmd);  // TILE STORE каждый раз!
}

// Правильно:
vkCmdBeginRenderPass(cmd, ...);
for (model in models) {
    drawModel(model);
}
vkCmdEndRenderPass(cmd);  // TILE STORE один раз
```

### Subpass dependencies

Для G-buffer + lighting:
```cpp
VkSubpassDescription subpasses[] = {
    {
        .pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS,
        .colorAttachmentCount = 3,        // albedo, normal, material
        .pColorAttachments = gbufferAttachments,
        ...
    },
    {
        .pInputAttachments = gbufferInputs,  // prev subpass outputs
        .colorAttachmentCount = 1,
        .pColorAttachments = finalColorAttachment,
        ...
    }
};
```

GPU может держать G-buffer целиком в tile memory между subpass'ами — нет write/read в framebuffer.

---

## Уровень 3 — для профессионала

### TBR-специфичные оптимизации

1. **Клирить attachment, а не загружать.** Всегда предпочитать `CLEAR` over `LOAD` если возможно.
2. **Группировать draw calls** в один render pass.
3. **Использовать `DONT_CARE` store op** для depth/stencil, не нужных в последующих render pass.
4. **`TRANSIENT` attachments** для intermediate G-buffer.
5. **Pre-rotation** для swapchain.
6. **Избегать dependency cycles.** Не рендерить в attachment, а потом читать из того же attachment в том же pass без subpass dependency.

### Мерить ли bandwidth?

AGI (Android GPU Inspector) показывает `Tile cache reads/writes` — ключевая метрика. Если она высокая относительно количества пикселей, что-то не так.

Специфичные counters per vendor:
- Adreno: `Prefetch Tag Misses`, `Resolve Fetches`.
- Mali: `AFBC Compression Ratio`, `Tile Fetches`.
- PowerVR: `Parameter Buffer Usage`.

### Parameter buffer overflow

Слишком много геометрии → parameter buffer (binning output) превышает память. GPU начинает **flushing** parameter buffer в DRAM и реiterating. Performance drop catastrophic.

Симптомы: 60 FPS в простых сценах, 10–15 FPS в сложных со многими объектами. Решение — instanced rendering, LOD, occlusion culling до draw call.

### Forward+ vs Deferred на mobile

**Deferred shading** — класcически: G-buffer (несколько attachments) + lighting pass. На TBR это дорого, потому что G-buffer = много attachments = большая tile memory → меньшие tiles → меньше efficiency.

**Forward+** (clustered forward): одно-attachment forward pass + light-list per cluster. Лучше использует tile memory, меньше overdraw на TBDR.

Большинство современных mobile engines (Filament, Unity URP, Unreal Mobile) по умолчанию используют Forward+. Deferred — только когда specific features нужны (SSAO, big shadow count).

### Xclipse отличия

Samsung Xclipse (RDNA2/3/4) — гибрид. RDNA архитектурно IMR, но Samsung добавила **tiling cache** — небольшой SRAM-буфер для прохода по tile'ам. Не полноценный TBR, но снижает внешнюю bandwidth.

Практика: Xclipse требует тех же render pass-оптимизаций как Mali/Adreno, но TBDR features (HSR) там нет — overdraw cost присутствует.

### Аппаратная реализация: анатомия трёх поколений Mali

Чтобы понять, как TBR устроен hardware-side, пройдём через эволюцию ARM Mali. Это важно, потому что ~60% Android devices в 2026 году работают на Mali GPU.

**Mali-200 / Mali-400 (Utgard, 2007–2012):**
- Разделение на dedicated Vertex Processor и Fragment Processors (до 4).
- Tile size 16×16 пикселей.
- Parameter Buffer — external DRAM, до 16 MB.
- Нет compute shaders — pure graphics pipeline.
- Hi-Z ограниченный (только для opaque pass).

**Mali-T6xx/T7xx/T8xx (Midgard, 2012–2016):**
- Unified Shader Core — vertex и fragment на одних ALU.
- Tile size 16×16, с поддержкой до 48×48 (для less-complex scenes).
- Compute shader support (OpenGL ES 3.1).
- AFBC 1.0 — первая lossless compression framebuffer.

**Mali-G7x/G5x (Bifrost, 2017–2019):**
- Clause-based execution — short sequences инструкций с одним scheduling decision.
- Quad-SIMD warp size (vs 16-wide в Midgard) — better branch efficiency.
- Adaptive Scalable Texture Compression (ASTC) hardware.
- AFBC 1.2 — cross-attachment compression.

**Mali-G7xx/G5xx (Valhall, 2019–2023):**
- Warps 16-wide.
- Superscalar execution.
- Vulkan 1.1+ first-class support.
- Command Stream Frontend CSF 2.0 (Mali-G710+) — hardware scheduler для graphics + compute без CPU involvement.

**Immortalis G720/G925 (5th Gen Valhall + hardware RT, 2023–2026):**
- Deferred Vertex Shading (DVS) — vertex shader запускается только для primitives видимых в tile.
- Ray Tracing Unit (RTU) — acceleration structures traversal.
- Variable Rate Shading (VRS) — shade resolution per tile region.

### Hardware comparison: Mali vs Adreno vs PowerVR vs Xclipse

| Параметр | ARM Mali-G720 | Adreno 830 | PowerVR DXT-72 | Xclipse 960 |
|---|---|---|---|---|
| Архитектура | TBR + DVS | TBR / sliced IMR | TBDR с PVRIC4 | IMR + tiling cache (RDNA4) |
| Tile size | 16×16 / 32×32 | 16×16 (sliced ~128×128) | 32×32 | N/A (sliced) |
| HSR | Нет (Early-Z only) | Low Resolution Z + LRZ | Полный HSR через Tag Buffer | Early-Z |
| Framebuffer compression | AFBC 1.3 | UBWC 3.0 | PVRIC4 | Delta Color Compression |
| MSAA cost (4×) | ~1.2× tile budget | ~1.3× | ~1.1× (tag-based) | ~1.5× |
| Ray Tracing HW | RTU (G720+) | Нет (G5 Elite добавил) | PhotonRT | Hardware RT cores |
| Memory bandwidth (LPDDR5X) | 51.2 GB/s shared | 64 GB/s shared | зависит от SoC | 68.2 GB/s shared |

### Bandwidth arithmetic — пример worked

Разберём, сколько bandwidth съедает кадр 1920×1080 с 4× overdraw (типично для 3D-сцены с UI):

**IMR подход (неприменим на mobile, но для сравнения):**
- Color write: 1920 × 1080 × 4 overdraw × 4 bytes (RGBA8) = 33.2 MB
- Depth write: 1920 × 1080 × 4 × 4 bytes (D32) = 33.2 MB
- Depth read (для Z-test): ~16 MB
- **Итого: ~82 MB/frame × 60 FPS = 4.9 GB/s** (только framebuffer)

**TBR подход (правильно сделанный Vulkan render pass):**
- Tile memory used (per tile, 16×16 RGBA8 + D32): 16×16×8 bytes = 2 KB (помещается в SRAM).
- Color tile store (финальный): 1920 × 1080 × 4 bytes = 8.3 MB (один write per pixel, не per overdraw).
- Depth tile store: `DONT_CARE` = 0 bytes.
- Tile load: `CLEAR` = 0 bytes.
- **Итого: ~8.3 MB/frame × 60 FPS = 0.5 GB/s**

Разница — 10×. На mobile это буквально разница между «держит 60 FPS сутки в casual game» и «throttlит через 20 минут».

### AFBC deep — как работает lossless compression

AFBC (Arm Framebuffer Compression) — proprietary формат от ARM, прозрачный для программиста. Как он работает:

1. Framebuffer разбивается на **superblocks** 16×16 или 32×8 пикселей.
2. Каждый superblock — анализируется на entropy. Если пиксели похожие (один цвет, градиент) — упаковывается в компактное представление.
3. Header per superblock указывает, сколько байт занимает payload (variable-length).
4. GPU умеет читать/писать superblock-formatted memory напрямую через texture units.

Типичная компрессия для UI (много solid colors): ~3× — ~20 MB → 7 MB.
Для 3D scene с noise / complex textures: ~1.2–1.5× — умеренная экономия.
Для pure noise (worst case): ~1× — AFBC detects и отключается per-block.

AFBC требует:
- Compatible format: RGBA8, BGRA8, R8G8B8 (не все поддерживаются).
- Flag `VK_EXTERNAL_MEMORY_FEATURE_EXPORTABLE_BIT` или `EGL_EXT_image_dma_buf_import`.
- Правильный lifetime — buffer не должен mapped CPU-side (CPU не понимает AFBC).

### PowerVR Tag Buffer — сердце TBDR

TBDR эффективность упирается в **Tag Buffer**, структуру per-tile размером ~256 bytes хранящую:
- Pointer на closest visible primitive per pixel (или per subpixel для MSAA).
- Depth value этого primitive.

Алгоритм:
1. Binning: primitives распределяются по tiles.
2. Per-tile: rasteriser генерирует fragments, но не вызывает fragment shader — instead, для каждого pixel обновляется Tag Buffer (keeping closest-primitive ID).
3. После processing всех primitives: Tag Buffer содержит для каждого пикселя — единственный fragment shader invocation нужный.
4. Fragment shader вызывается per-pixel once (opaque geometry).

Overdraw cost: **ноль** для opaque. Для transparent (alpha blending) tag buffer не может rejectить — нужно shade всё → TBDR быстро деградирует в TBR при heavy transparency.

### MSAA на TBR — важная особенность

Multi-Sample Anti-Aliasing в IMR очень дорогой: 4× color bandwidth, 4× depth bandwidth. В TBR MSAA практически **бесплатен**:

- MSAA samples хранятся в tile memory (увеличенный ~4× tile buffer).
- В конце tile происходит **resolve** — усреднение samples в один output pixel.
- **Только resolved pixel** пишется в framebuffer.

Bandwidth cost: тот же, что без MSAA. Только tile memory budget увеличен. На Mali-G710 MSAA 4× tile size становится 8×8 (вместо 16×16), но visual quality +++.

Mobile приложения, которые отказались от MSAA «потому что дорого», делали ошибку — на TBR MSAA почти free.

### Parameter buffer sizing — как не обжечься

Parameter buffer хранит per-tile primitive lists. Размер зависит от:
- Количество primitives × bytes per primitive pointer (~8 bytes).
- Количество tiles (зависит от resolution и tile size).
- Overlap factor (primitive может попадать в несколько tiles).

Пример для 1920×1080 с 500k triangles:
- Tiles: (1920/16) × (1080/16) = 120 × 68 = 8160 tiles.
- Average primitive overlap: ~2–4 tiles.
- Parameter buffer entries: 500k × 3 = 1.5M pointers × 8 bytes = 12 MB.

Mali-G710 default parameter buffer: 16 MB. Если больше — **incremental rendering**: GPU flusht частичный parameter buffer, рендерит эти tiles, clears buffer, продолжает. Потеря 20–40% performance.

Симптом: FPS drop catastrophic при пересечении ~500k primitives на screen. Решение — LOD, frustum culling до submit, batching.

---

## Как работает под капотом

```
Frame submit
    │
    ▼
┌──────────────────────────────┐
│  Phase 1: Vertex + Binning   │
│  всё geometry processed      │
│  primitives sorted per tile  │
│  Parameter Buffer created    │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────┐
│  Phase 2: Per-tile render    │
│  for each tile:              │
│    - Load op (CLEAR/LOAD)    │
│    - Process primitives      │
│      in tile memory (SRAM)   │
│    - Store op (STORE/NC)     │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────┐
│  Composition/Display         │
└──────────────────────────────┘
```

---

## Реальные кейсы

### Кейс 1: Planner 5D — один render pass для scene

Scene геометрия рендерится в один render pass: floor, walls, furniture. Один clear в начале, один store в конце. Для UI — отдельный render pass поверх. Bandwidth минимален.

### Кейс 2: IKEA Place — Forward+ для AR

AR scene рендерится в Forward+ pipeline: per-cluster light list, single-pass lighting. Depth attachment — memoryless (transient). Total framebuffer bandwidth — 60% меньше, чем был бы в deferred.

### Кейс 3: Godot 4.4 Mobile renderer

После оптимизаций 2024–2026: pre-rotation для all Android apps, immutable samplers (не меняют state между draw calls внутри render pass), persistent shared buffers (reuse tile memory). Результат на Galaxy S24: FPS +10–15% против Godot 4.2.

### Кейс 4: Filament Mobile rendering path

Google Filament на Android использует Forward+ рендеринг со специальными оптимизациями под TBR:
- Depth prepass опционален (выключен по умолчанию на mobile — Early-Z + HSR делают его лишним на TBR/TBDR).
- Single render pass для scene + translucent + UI.
- Bloom/tonemap — subpass dependencies, G-buffer пропускается полностью через tile memory.
- MSAA 4× включён по умолчанию на TBDR (PowerVR, Apple) — almost free.

Замер на Pixel 7 Pro (Mali-G710): Sponza scene 1600 tris × 150 objects, 60 FPS при 30% GPU utilization.

### Кейс 5: Unreal Engine 5 Mobile с Lumen Mobile

UE5 Mobile renderer (2023+) попытался использовать Lumen (software ray tracing). На mobile TBR это проблематично потому что Lumen требует много ray tracing в random memory patterns — убивает tile efficiency.

Результат: Lumen Mobile ограничен — работает только для «precomputed» direct lighting, без real-time GI. На Galaxy S23 Ultra (Adreno 740): 30 FPS при разрешении 720p. Для сравнения без Lumen — 60 FPS при 1080p.

Lesson: GI techniques которые работают на desktop IMR, нужно адаптировать (или отключать) для mobile TBR. Filament и Unity URP пошли путём «baked GI» именно по этой причине.

---

## Распространённые заблуждения

| Миф | Реальность |
|---|---|
| TBR и TBDR — одно и то же | TBDR = TBR + HSR (hidden surface removal). PowerVR и Apple AGX — TBDR, Mali и Adreno — чистый TBR |
| На мобильном GPU overdraw бесплатен | Только на TBDR (PowerVR, Apple). На Mali/Adreno overdraw стоит обычных fragment cycles |
| Vulkan render pass — просто group organizer | Render pass — **semantic boundary** для tile management. Неправильное использование убивает performance |
| AFBC автоматически включён | Нужно явно запрашивать compatible format и flags в Vulkan |
| Deferred лучше Forward на mobile | На TBR Forward/Forward+ обычно выигрывает из-за tile memory efficiency |

---

## Подводные камни

### Ошибка 1: Многократные маленькие render pass

**Как избежать:** объединять всё, что возможно, в один render pass. UI поверх — второй render pass.

### Ошибка 2: `LOAD_OP_LOAD` когда можно `CLEAR`

**Как избежать:** при старте frame всегда `CLEAR` для colour и depth.

### Ошибка 3: Забытый pre-rotation

**Как избежать:** проверить `VkSurfaceTransformFlagsKHR`, применять identity или rotation matrix в vertex shader.

### Ошибка 4: Большой parameter buffer

**Как избежать:** instanced draws, LOD, occlusion culling до GPU.

---

## Связь с другими темами

[[gpu-architecture-fundamentals]] — SIMT + tile, вместе формируют mobile GPU.
[[rendering-pipeline-overview]] — TBR фазы в контексте full pipeline.
[[overdraw-and-blending-cost]] — overdraw penalty в TBR vs TBDR.
[[vulkan-on-android-fundamentals]] — VkRenderPass tutorial.
[[vulkan-pipeline-command-buffers]] — submission model для TBR.
[[gpu-memory-management-mobile]] — AFBC, transient attachments.
[[frame-pacing-swappy-library]] — interaction с compositor.

---

## Источники

- **Arm. The Mali GPU Abstract Machine (series).** [developer.arm.com](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/the-mali-gpu-an-abstract-machine-part-2---tile-based-rendering).
- **Imagination Technologies. PowerVR Graphics Architecture.** [blog.imaginationtech.com](https://blog.imaginationtech.com/a-look-at-the-powervr-graphics-architecture-tile-based-rendering/).
- **Imagination. TBDR reference.** [docs.imgtec.com](https://docs.imgtec.com/starter-guides/powervr-architecture/html/topics/tile-based-deferred-rendering-index.html).
- **Vulkan 1.4 Spec. Render Pass chapter.** [registry.khronos.org/vulkan](https://registry.khronos.org/vulkan/specs/1.4-extensions/html/chap8.html#renderpass).
- **Google. Vulkan pre-rotation on Android.** [developer.android.com/games/optimize/vulkan-prerotation](https://developer.android.com/games/optimize/vulkan-prerotation).
- **Hasselgren, J., Akenine-Möller, T. (2007). An Efficient Multi-View Rasterization Architecture. EG Symposium.** Foundational TBR academic paper.
- **Lindholm, E., et al. (2008). NVIDIA Tesla: A Unified Graphics and Computing Architecture.** IEEE Micro. Контраст с IMR.

---

## Проверь себя

> [!question]- Чем TBR отличается от IMR?
> IMR: draw calls → fragment shade → запись в framebuffer в DRAM сразу. TBR: draw calls → binning per-tile → для каждого tile — fragment shade в SRAM → финальный store в framebuffer. TBR экономит bandwidth.

> [!question]- Что делает TBDR дополнительно к TBR?
> Hidden Surface Removal (HSR) перед fragment shading. Фрагменты, скрытые за более близкими, вообще не шейдятся. Нулевой overdraw для opaque geometry. Реализовано в PowerVR и Apple AGX.

> [!question]- Зачем pre-rotation?
> Без него композитор делает дополнительный rotation pass когда телефон перевёрнут, что = +10–15% overhead. Pre-rotation применяет rotation matrix в vertex shader, компенсируя, избавляя композитора от работы.

> [!question]- Что означает store op `DONT_CARE` в Vulkan?
> Tile memory после render pass не записывается в framebuffer. Экономит bandwidth и потенциально полностью убирает DRAM usage для данного attachment (если также transient). Правильный выбор для depth/stencil, G-buffer attachments.

---

## Ключевые карточки

Что такое tile memory?
?
On-chip SRAM, в котором держится framebuffer tile (обычно 16×16 или 32×32 пикселя) во время его рендеринга. Не требует DRAM access — экономия энергии ~100× vs external memory.

---

Какие GPU используют TBDR?
?
PowerVR (все серии), Apple AGX. Остальные mobile GPU (Mali, Adreno, Xclipse) — классический TBR без deferred hidden surface removal.

---

Когда использовать `LOAD_OP_LOAD`?
?
Только когда предыдущее содержимое framebuffer обязательно нужно (например, UI поверх 3D-scene). В остальных случаях — `CLEAR` или `DONT_CARE`.

---

Что такое AFBC?
?
Arm Frame Buffer Compression — lossless compression формата, прозрачно применяемая к framebuffer на Mali GPUs. Снижает bandwidth ~50% при compatible форматах.

---

Почему Forward+ часто лучше Deferred на mobile?
?
Deferred требует multiple attachments (G-buffer) → большая tile memory → меньшие тайлы → хуже эффективность TBR. Forward+ с одним attachment + clustered lights эффективно использует tile memory.

---

## Куда дальше

| Направление | Куда |
|---|---|
| Следующий M2 | [[rendering-pipeline-overview]] |
| Vulkan практика | [[vulkan-pipeline-command-buffers]] |
| Overdraw detail | [[overdraw-and-blending-cost]] |
| Memory detail | [[gpu-memory-management-mobile]] |

---

*Создано: 2026-04-20. Deep-dive модуля M2.*

---
title: "Архитектура мобильного GPU: SIMT, warps и почему GPU не просто быстрый CPU"
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
  - "[[android-graphics-3d-moc]]"
  - "[[tile-based-rendering-mobile]]"
  - "[[rendering-pipeline-overview]]"
  - "[[shader-programming-fundamentals]]"
  - "[[gpu-memory-management-mobile]]"
  - "[[gpu-specific-debugging-adreno-mali-powervr-xclipse]]"
prerequisites:
  - "[[android-graphics-3d-moc]]"
primary_sources:
  - url: "https://en.wikipedia.org/wiki/Single_instruction,_multiple_threads"
    title: "Wikipedia: SIMT execution model"
    accessed: 2026-04-20
  - url: "https://chipsandcheese.com/p/arms-bifrost-architecture-and-the"
    title: "Chips and Cheese: Arm's Bifrost Architecture and the Mali-G52"
    accessed: 2026-04-20
  - url: "https://bakhi.github.io/mobileGPU/mali/"
    title: "Mali Mobile GPU architectural overview"
    accessed: 2026-04-20
  - url: "https://cvw.cac.cornell.edu/gpu-architecture/gpu-characteristics/simt_warp"
    title: "Cornell: Understanding GPU Architecture — SIMT and Warps"
    accessed: 2026-04-20
  - url: "https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/the-mali-gpu-an-abstract-machine-part-2---tile-based-rendering"
    title: "Arm: The Mali GPU: An Abstract Machine Part 2"
    accessed: 2026-04-20
  - url: "https://developer.android.com/agi"
    title: "Android GPU Inspector (AGI) — tool for GPU profiling"
    accessed: 2026-04-20
reading_time: 28
difficulty: 5
---

# Архитектура мобильного GPU

Когда vertex shader из [[case-planner-5d|Planner 5D]] обрабатывает 50 000 вершин дивана за один кадр, это происходит не в 50 000 последовательных циклов. GPU выполняет десятки или сотни вершин **одновременно** — на Adreno 650 до 64 штук в одной инструкции, на Mali-G78 — до 16, на PowerVR Series9XE — до 32. Это не «быстрый CPU», это принципиально другая архитектура: **SIMT** (Single Instruction, Multiple Threads), где одна программа (шейдер) одновременно исполняется на тысячах потоков, но с одной важной оговоркой — все потоки в «warp» обязаны выполнять одну и ту же инструкцию каждый такт. Когда они расходятся — serialization penalty. Когда сходятся — тысячи operations per cycle.

Этот файл — первый deep-dive модуля M2 в [[android-graphics-3d-moc]]. После него становится понятно, почему mobile GPU жрёт батарею по-разному в зависимости от шейдерного кода, почему `if-else` в фрагменте ведёт к падению FPS, почему Mali и Adreno ведут себя иначе на одном и том же APK, и зачем AGI/Perfetto показывают «warp occupancy» как метрику. Без знания этих основ оптимизация шейдеров становится гаданием по отчётам профилировщика.

---

## Зачем это знать

**Первый production-сценарий.** Разработчик добавил `if (distance > farThreshold) { simplifyShading(); } else { complexShading(); }` в fragment shader. Тест на своём устройстве (Adreno 650) показывает падение FPS на 30 %, при этом GPU-utilization 100 %. На другом устройстве (Mali-G78) — падение 15 %. Причина — **warp divergence**: Adreno использует 64-wide warps, то есть 64 пикселя обязаны выполнять одну ветвь; при смешанном результате оба branch'а выполняются последовательно. Mali с 16-wide warps страдает меньше. Без понимания размера warp'а и divergence penalty разработчик не может оптимизировать условия в шейдерах.

**Второй сценарий.** Приложение на Xclipse 940 (Exynos 2400, RDNA3) работает иначе, чем на Snapdragon 8 Gen 2 (Adreno 740). Один и тот же шейдер даёт разный пик FPS. Xclipse — 32-wide wave, Adreno — 64-wide, Mali-G710 — 16-wide. На каждой архитектуре тот же код компилируется в разное число параллельных инструкций. Без понимания этого кросс-устройственная оптимизация — слепое guesswork.

**Третий сценарий.** AGI (Android GPU Inspector) показывает «warp occupancy 30 %». Разработчик не понимает, что это значит. Ответ: один или несколько ядер используются эффективно, но остальные ждут данных из памяти. GPU не утилизирован. Решение — либо уменьшить register pressure в шейдере (чтобы больше warps помещалось в SM-блок), либо сменить pattern доступа к памяти (спатиальная локальность). Без знания архитектурных ограничений этот отчёт непонятен.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[android-graphics-3d-moc]] | Карта раздела, место модуля M2 в курсе |
| Базовая архитектура CPU: кеш, регистры, pipeline | Без интуиции «что такое CPU» GPU как «не-CPU» непрозрачен |
| [[vectors-in-3d-graphics]] | GPU оперирует над vec4 — 4 float'а как SIMD-unit — это одна из причин такой архитектуры |

---

## Терминология

| Термин | Определение | Аналогия |
|---|---|---|
| SIMD | Single Instruction, Multiple Data — одна инструкция обрабатывает массив данных | Дирижёр даёт одну команду, весь оркестр играет одну ноту |
| SIMT | Single Instruction, Multiple Threads — расширение SIMD, где «множество данных» — потоки с отдельными регистрами | Как SIMD, но каждый музыкант может немного варьировать исполнение |
| Warp (NVIDIA) / Wavefront (AMD) / Quad/Wave (Mobile) | Группа потоков, выполняющихся lock-step | Взвод солдат — все шагают в ногу |
| Warp size | Количество потоков в warp'е | Размер взвода: NVIDIA 32, AMD 64, Adreno 64, Mali 4-16, PowerVR 32 |
| Divergence | Ситуация, когда потоки warp'а выполняют разные ветки if-else | Часть взвода идёт налево, другая направо — серийное выполнение обеих команд |
| Occupancy | Процент использования доступных warp slots в SM/CU | Сколько мест в автобусе занято |
| Compute Unit (CU) / Streaming Multiprocessor (SM) / Execution Engine (EE) | Аппаратный блок, исполняющий warps | «Завод» из sibling warps |
| Register pressure | Количество регистров, нужных шейдеру; влияет на occupancy | Рабочее место на одного работника — если нужно много, меньше людей помещается в цехе |
| Latency hiding | Переключение между warps для скрытия ожидания памяти | Пока одна команда ждёт поставку, другая работает |
| Memory hierarchy | Иерархия памяти: registers → shared/local → L1/L2 cache → global VRAM | От карманов до склада |
| FMA (fused multiply-add) | `a·b + c` за один такт | Один удар молотка делает два дела |

---

## Историческая справка

- **1970s** — первые дискретные GPU для arcade (Atari VCS, Namco).
- **1990s** — 3dfx Voodoo, NVIDIA Riva TNT. GPU как SIMD-машина для texture mapping.
- **2001 — NVIDIA GeForce 3.** Первый GPU с программируемыми vertex и pixel shaders. SIMD-processing explicit.
- **2006 — NVIDIA CUDA + G80.** Впервые SIMT как формализованная архитектура; warp 32. Термин «warp» популяризируется.
- **2008 — AMD Terascale.** Wavefront 64.
- **2010 — Qualcomm Adreno 200 series.** Адаптация подхода, wavefront 64.
- **2012 — ARM Mali Midgard.** SIMD-based, 4-wide quads.
- **2018 — ARM Bifrost → Valhall.** 4 → 8 → 16-wide warps по мере эволюции.
- **2022 — Samsung Xclipse (RDNA2 в Exynos 2200).** 32-wide wave, unified AMD архитектура на мобилке.
- **2024 — Xclipse 940 (RDNA3 в Exynos 2400).** Улучшения wave scheduling.
- **2026 — Xclipse 960 (RDNA4 в Exynos 2600).** Ray tracing accelerators, 2× performance vs 940. Adreno 740/840 на Snapdragon X Elite.

На фоне десктопного GPU (NVIDIA H100 — ~14 000 CUDA cores) мобильные GPU имеют сотни (Adreno 740 — ~500 ALU). Но **архитектурно это та же SIMT-парадигма**, лишь в меньшем масштабе.

---

## Теоретические основы

### SIMD vs SIMT

SIMD (Single Instruction, Multiple Data) — одна инструкция применяется к вектору данных. Пример: `vec4 c = a + b` в GLSL компилируется в одну SIMD-инструкцию сложения четырёх float.

SIMT (Single Instruction, Multiple Threads) — расширение SIMD, в котором «данные» — это **отдельные потоки**, каждый со своими private регистрами, но **все потоки обязаны выполнять одну инструкцию в каждый такт**. GPU может параллельно обрабатывать vertex #0, vertex #1, ..., vertex #31 одной и той же программой, но когда все доходят до `if (...) { ... } else { ... }` и результат теста разный для разных потоков, **оба branch'а выполняются последовательно**, с masking.

Ключ: SIMT даёт программисту иллюзию «тысячи независимых потоков», но аппаратно — это SIMD с branch predication.

### Warp / Wavefront / Wave

**Warp** (NVIDIA term) = группа из N потоков, выполняющихся lock-step на одном SIMD-блоке.

- NVIDIA: warp 32
- AMD (desktop и Xclipse RDNA2+): wavefront 64 или wave 32
- Qualcomm Adreno: warp 64
- ARM Mali (Midgard → Bifrost → Valhall): quad 4 → 4-wide → 8-wide → 16-wide
- Imagination PowerVR: ~32-wide

Все потоки в warp делят одну program counter (PC) — они выполняют одну и ту же инструкцию.

### Divergence penalty

Пример GLSL:
```glsl
if (fragDepth > threshold) {
    color = complexFunc();  // 50 инструкций
} else {
    color = simpleFunc();    // 10 инструкций
}
```

Если в warp'е из 64 пикселей часть имеет `fragDepth > threshold`, часть нет — **оба branch'а выполняются**, полный cost = 50 + 10 = 60 инструкций. Потоки, которые «не в активной ветке», masked-off (результат отбрасывается).

Без divergence: 50 или 10 инструкций в зависимости от branch.

На Adreno 64-wide: divergence дороже, потому что нужно 64 результата-маски. На Mali 16-wide: divergence дешевле в пропорциональном отношении, но сам warp 4× меньше, поэтому абсолютная производительность ниже.

**Практический рецепт:** избегать `if-else` в шейдерах вокруг экспензивных операций. Использовать `mix()`, `step()`, `smoothstep()` — GLSL builtins, которые выполняются без divergence.

### Latency hiding

Когда warp запрашивает глобальную память (чтение текстуры, чтение uniform), результат приходит через 200–400 тактов. В это время warp **stalled**. Чтобы GPU не простаивал, hardware **переключается на другой warp** в том же SM/CU.

Следовательно, чем больше warps на SM, тем лучше latency hiding. Предел количества warps определяется **register pressure**: если шейдер использует 64 register/thread, в SM с 256 регистрами максимум 4 warp'а (при warp 64, это 4×64 = 256). Если шейдер использует 16 registers/thread, 16 warps помещается.

Отсюда оптимизация: **минимизировать register usage в шейдерах**, чтобы повысить occupancy. Компилятор делает это частично, но явные hints помогают — использовать `mediump` где возможно, не переусложнять intermediate variables.

### Memory hierarchy

Снизу вверх:

1. **Registers.** Private для потока, самые быстрые, но мало (32-байтных float per thread — 16–32 штуки обычно).
2. **Shared memory / Local memory.** Для warp'а или группы warps в SM. Быстрая, используется для inter-thread communication в compute shaders.
3. **L1 cache.** Per-SM, авто-кэширование.
4. **L2 cache.** Для всего GPU, больше.
5. **Global memory (VRAM).** Общая для всех warp'ов. Самая медленная (400+ тактов).

**На мобильных** VRAM — это часть общей RAM устройства (unified memory). Нет физически отдельного video RAM. Это **и плюс**, и **минус**: zero-copy для buffer'ов, но CPU и GPU конкурируют за bandwidth.

### FMA — основная инструкция

`a * b + c` в GLSL компилируется в один **Fused Multiply-Add** — одна инструкция GPU. Все важные операции (dot product, matrix-vector multiply, Lambert lighting) — цепочки FMA.

Adreno 740: 1 TFLOPS FMA throughput (~500 ALU × 2 FMAs/cycle × 1 GHz). Mali-G710: похоже. Xclipse 940: быстрее.

Это **основная метрика** производительности. Больше FMAs — больше математики per second.

---

## Уровень 1 — для начинающих

Процессор в телефоне (CPU) — как универсал-workman: делает одно, потом другое. Может читать файл, обработать текст, открыть приложение. Гибкий, но медленный в математике.

GPU — как взвод солдат: один офицер командует, все солдаты одновременно делают одну и ту же вещь. Не гибко (все должны делать одно и то же), но огромная параллельность. Когда нужно нарисовать экран с 2 миллионами пикселей, и для каждого нужно посчитать цвет — GPU идеален: раздаёт команду всем пикселям одновременно.

Проблема начинается, когда пиксели хотят делать разное. Например, один пиксель должен быть красным, другой — синим с шумом. Одна команда не помещается. GPU всё равно делает это — но серийно, сначала красные, потом синие. Это называется «warp divergence», и из-за неё FPS падает.

В Android 2026 GPU в разных телефонах устроены слегка по-разному: у Qualcomm Adreno взвод по 64 солдата, у ARM Mali — по 16, у Samsung Xclipse — по 32. Ваш код одинаково работает на всех, но эффективность разная. Поэтому профилирование на разных устройствах — часть нормальной работы.

---

## Уровень 2 — для студента

### SIMT-модель в реальном коде

```glsl
// Fragment shader, каждый пиксель — один thread
in vec3 v_position;
uniform vec3 u_lightPos;

void main() {
    vec3 L = normalize(u_lightPos - v_position);  // Инструкция 1: warp выполняет параллельно
    vec3 N = normalize(v_normal);                  // Инструкция 2: то же самое
    float ndotl = max(dot(N, L), 0.0);             // Инструкция 3
    fragColor = vec4(vec3(ndotl), 1.0);            // Инструкция 4
}
```

4 инструкции × 64 потока (на Adreno). На разрешении 1920×1080 = 2,073,600 пикселей, 32,400 warps, каждый по 4 инструкции = ~130k warp-инструкций per frame. При 60 FPS — ~7.8M warp-инструкций per second. Adreno делает это за несколько миллисекунд.

### Divergence пример

```glsl
if (fragColor.r > 0.5) {
    fragColor.rgb = expensiveEffect();   // 40 инструкций
}
```

Если половина пикселей в warp удовлетворяют условию — warp выполняет 40 инструкций для всех 64 пикселей (но 32 из них получают masked-off результат). Без divergence (если бы все удовлетворяли) — 40 инструкций. С divergence — тоже 40 инструкций, но только 32 пикселя получают result, остальные просто тратят cycles.

Если условие было бы `else`:
```glsl
if (fragColor.r > 0.5) {
    fragColor.rgb = expensiveEffect();    // 40 инструкций
} else {
    fragColor.rgb = simpleEffect();        // 5 инструкций
}
```

Cost = 40 + 5 = 45 инструкций для всего warp. Worse than no divergence.

### Branchless trick

Заменить `if` на `mix()`:
```glsl
float maskCond = step(0.5, fragColor.r);
fragColor.rgb = mix(simpleEffect(), expensiveEffect(), maskCond);
```

Теперь оба effects вычисляются всегда, но без divergence — просто линейный выбор. Работает только если оба branch'а дёшевы. Если один экспензивный — иногда вычисление обоих дороже, чем divergence.

---

## Уровень 3 — для профессионала

### Register pressure на реальных шейдерах

PBR фрагментный шейдер (Filament style): ~60 instructions, использует ~40 registers/thread. На Adreno 740 с 4096 registers per SM и warp 64: `4096 / (64 × 40) = 1.6 warp'а` — очень низкая occupancy, всего ~25 %.

Оптимизации:
- Использовать `mediump` для intermediate (уменьшает до 20 registers).
- Вынести IBL sampling как shared (один warp sample для tile).
- Split PBR на два passes (G-buffer + lighting) для снижения instantaneous register pressure.

### GPU-specific divergence tolerance

| GPU | Warp size | Divergence cost (примерно) |
|---|---|---|
| Mali G710 | 16 | Низкий (небольшие warps) |
| Mali G720 | 16 | Низкий |
| Adreno 650 | 64 | Высокий |
| Adreno 740 | 64 | Высокий |
| PowerVR AXT | 32 | Средний |
| Xclipse 940 (RDNA3) | 32 wave | Средний |

На Adreno избегайте `if-else` в шейдерах на hot paths. На Mali можно допустить. Но всегда проще писать branchless и пусть компилятор оптимизирует.

### Shader precision (highp / mediump / lowp)

- `highp`: 32-bit float, full precision. Дороже в registers.
- `mediump`: 16-bit float (FP16). ~2× дешевле в registers, ~2× быстрее FMA.
- `lowp`: 10-bit fixed (уже deprecated, treat as mediump).

На мобилке использование `mediump` для цветов и normals даёт ~1.5-2× perf boost. Для geometric quantities (position в world space, distance) — только `highp`.

### Memory access patterns

Соседние пиксели в warp ожидают соседние позиции в памяти (spatial locality). Чтение текстуры через `texture2D(sampler, uv)` использует spatial coherence: соседние UV-координаты → соседние байты → кэш-hits.

Случайный access (random UV) → L1 miss → L2 miss → VRAM latency 400 тактов → warp stalled.

Оптимизация: избегать random texture lookup в шейдерах. Предпочитать последовательный/локальный доступ.

### FMA и roofline model

Теоретический предел GPU:
- FLOPS (математика): 1 TFLOPS на Adreno 740.
- Bandwidth (память): 77 GB/s на Adreno 740.

Arithmetic intensity = FLOPS / byte accessed. Шейдер «compute-bound», если intensity высокая (например, PBR с кучей dot product). «Memory-bound» если intensity низкая (например, большой blur с 25 samples из одной текстуры).

Профилировщик AGI показывает roofline. Если шейдер compute-bound — оптимизируйте инструкции. Если memory-bound — оптимизируйте access patterns, компрессию текстур.

---

## Как работает под капотом

```
┌─────────────────────────────────────────────┐
│   Draw Call (CPU → GPU)                      │
│   — количество вершин, binding ресурсов      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   GPU Command Processor                      │
│   разбирает команды, готовит data            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   Vertex Distributor                         │
│   делит вершины на warps (64 на Adreno)     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   SM (Streaming Multiprocessor) × N          │
│   executes vertex shader warps in parallel   │
│   — каждый SM держит 4-16 warps одновременно │
│   — latency hiding через warp switching      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   Primitive Assembly + Rasterizer            │
│   генерирует фрагменты (пиксели)             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   Fragment Shader warps (те же SMs)          │
│   каждый warp — группа пикселей              │
│   та же SIMT-модель                          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   ROP (Render Output Unit)                   │
│   blending, depth test, пишет в framebuffer  │
└─────────────────────────────────────────────┘
```

---

## Сравнение мобильных GPU

| GPU | Warp size | FP32 throughput | TDP | Применение |
|---|---|---|---|---|
| Mali G78 | 16 | ~1 TFLOPS | Mid-range, Cortex-A78 |
| Mali G710 | 16 | ~1.5 TFLOPS | High-end 2022–2024 |
| Mali G720 | 16 | ~2 TFLOPS | High-end 2024–2026 |
| Adreno 650 | 64 | ~1.2 TFLOPS | Snapdragon 865 |
| Adreno 740 | 64 | ~2.7 TFLOPS | SD 8 Gen 2 |
| Adreno 840 | 64 | ~3.5 TFLOPS | SD X Elite 2026 |
| PowerVR AXT | 32 | Varies | MediaTek Dimensity |
| Xclipse 920 (RDNA2) | 32 | ~1.3 TFLOPS | Exynos 2200 |
| Xclipse 940 (RDNA3) | 32 | ~2.5 TFLOPS | Exynos 2400 |
| Xclipse 960 (RDNA4) | 32 | ~5 TFLOPS + RT | Exynos 2600 (2026) |

---

## Реальные кейсы

### Кейс 1: Filament shader optimization для Adreno

Команда Google Filament убрала `if (shadowReceiver)` из PBR шейдера, заменив на unconditional shadow sampling (где shadow map для non-receivers содержит 1.0 — full light). Результат: -15% фrame time на Adreno, минус divergence cost.

### Кейс 2: Planner 5D per-device tuning

На Adreno 650+ [[case-planner-5d|Planner 5D]] использует full PBR шейдер. На Mali-G52 — simplified Blinn-Phong. Разница определяется при старте на основе GPU identification, shader variants выбираются accordingly.

### Кейс 3: IKEA Place occupancy в AR shader

В [[case-ikea-place-ar|IKEA Place]] AR shader сочетает PBR + depth occlusion + lighting estimation. Register pressure высокий. Команда перенесла lighting estimation в separate pass (первый pass — G-buffer, второй — lighting + occlusion). Occupancy выросла с 25% до 60%, frame time упал на 25%.

---

## Распространённые заблуждения

| Миф | Реальность | Почему |
|---|---|---|
| GPU — это «много CPU» | GPU — SIMT, не MIMD: все cores делают одно | Аналогия с multi-core CPU |
| `if` в шейдере всегда плохо | Если предикат coherent внутри warp'а (все 64 пикселя одинаково), free | Упрощение |
| Mobile GPU идентичны desktop в архитектуре | Tile-based rendering на мобилке (см. [[tile-based-rendering-mobile]]) — принципиальное отличие | Одинаковая номенклатура |
| `mediump` всегда быстрее | В register-pressured коде да; в memory-bound — то же | Интуиция «меньше бит = быстрее» |
| Увеличение Draw Call — плохо | Увеличение draw count — да (CPU overhead); увеличение triangles per draw — нет | Путают batching |

---

## Подводные камни

### Ошибка 1: тестирование только на одном GPU

**Как избежать:** минимум 3 устройства — Adreno, Mali, PowerVR. AGI на каждом.

### Ошибка 2: игнорирование shader variants

**Как избежать:** для high-quality visuals имейте 2–3 варианта шейдера (ultra/medium/low), выбор по device identification или user setting.

### Ошибка 3: premature optimization

**Как избежать:** всегда профилируйте с AGI перед оптимизацией. Часто bottleneck не там, где ожидается.

---

## Связь с другими темами

[[tile-based-rendering-mobile]] — следующий deep-dive M2; TBR — ключевое отличие mobile от desktop GPU.

[[rendering-pipeline-overview]] — полный pipeline, где GPU architecture — один из слоёв.

[[shader-programming-fundamentals]] — шейдеры выполняются на GPU, их оптимизация начинается с понимания archeology.

[[gpu-memory-management-mobile]] — memory hierarchy, buffer management.

[[gpu-specific-debugging-adreno-mali-powervr-xclipse]] — профилирование на каждой архитектуре.

[[android-gpu-inspector-agi]] — инструмент для анализа warp occupancy, FMA utilization.

[[shader-compilation-jitter-mitigation]] — другое измерение: как шейдер компилируется для целевого GPU.

---

## Источники

- **Kirk, D. B. & Hwu, W. W. (2016). Programming Massively Parallel Processors, 3rd ed.** Классика для понимания SIMT.
- **Hennessy, J. L. & Patterson, D. A. (2017). Computer Architecture: A Quantitative Approach, 6th ed.** Chapter 4 — data-level parallelism.
- **ARM Mali GPU Abstract Machine (part 2).** [developer.arm.com](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/the-mali-gpu-an-abstract-machine-part-2---tile-based-rendering).
- **Chips and Cheese. Arm's Bifrost and Valhall architectures.** [chipsandcheese.com](https://chipsandcheese.com/p/arms-bifrost-architecture-and-the).
- **NVIDIA CUDA C Programming Guide.** For warp formalism.
- **Qualcomm Adreno Optimization Guide.** developer.qualcomm.com.
- **PowerVR Performance Recommendations.** docs.imgtec.com.
- **Android GPU Inspector documentation.** [developer.android.com/agi](https://developer.android.com/agi).

---

## Проверь себя

> [!question]- Что такое warp (wavefront) в GPU?
> Группа потоков, выполняющихся lock-step (синхронно, одна инструкция на все). На NVIDIA и Adreno — 32 или 64. На Mali — 4–16. На Xclipse — 32. Все потоки одного warp'а должны выполнять ту же инструкцию каждый такт.

> [!question]- Что такое warp divergence и почему она дорогая?
> Ситуация, когда потоки warp'а выполняют разные branch'и if-else. Hardware выполняет **оба branch'а** последовательно с masking. Cost = cost(branch1) + cost(branch2), вместо max. Особенно дорого на Adreno 64-wide.

> [!question]- Как latency hiding работает на GPU?
> Когда warp ждёт memory access (400+ тактов), hardware переключается на другой ready warp в том же SM. Это эффективнее, чем stall. Количество warps определяется register pressure шейдера.

> [!question]- Почему mobile GPU иная архитектура, чем desktop?
> Две ключевые разницы: unified memory (CPU и GPU делят RAM) и tile-based rendering. Первое экономит copy, второе — bandwidth для framebuffer. Desktop GPU имеет отдельную VRAM и immediate mode rendering.

> [!question]- Что означает «warp occupancy 30%» в AGI?
> Только 30% доступных warp slots в SM используются. Причина — register pressure шейдера ограничивает сколько warps помещается. Решение — упростить шейдер, использовать mediump, split на passes.

---

## Ключевые карточки

Какого размера warp на Adreno 740?
?
64 threads. Qualcomm Adreno исторически использует wide warps. Adreno 650, 740, 840 — все 64.

---

Что такое SIMT и как оно отличается от SIMD?
?
SIMT — Single Instruction Multiple Threads, расширение SIMD. Каждый thread имеет private регистры, но все threads в warp обязаны выполнять одну инструкцию per такт. Иллюзия независимых потоков на SIMD hardware.

---

Что такое Fused Multiply-Add (FMA)?
?
GPU-инструкция `a·b + c` за один такт. Основная инструкция для graphics math (dot product, matrix-vector multiply). Все GPU performance metrics в TFLOPS измеряются в FMA throughput.

---

Почему AGI показывает roofline model?
?
Чтобы понять, compute-bound или memory-bound ваш шейдер. Compute-bound — оптимизировать инструкции. Memory-bound — оптимизировать access patterns, текстурную компрессию.

---

Что такое register pressure и как влияет на performance?
?
Количество регистров, нужных шейдеру на thread. Высокая register pressure → меньше warps помещается в SM → хуже latency hiding → простои GPU. Fix — использовать mediump, split шейдер на passes.

---

## Куда дальше

| Направление | Куда | Зачем |
|---|---|---|
| Следующий M2 | [[tile-based-rendering-mobile]] | Уникальная для мобилок архитектура TBR/TBDR |
| Полный pipeline | [[rendering-pipeline-overview]] | Где эти GPU executions happen |
| Профилирование | [[android-gpu-inspector-agi]] | Практика измерений occupancy, divergence |
| Шейдеры | [[shader-programming-fundamentals]] | Как код превращается в warp instructions |

---

*Создано: 2026-04-20. Deep-dive модуля M2.*

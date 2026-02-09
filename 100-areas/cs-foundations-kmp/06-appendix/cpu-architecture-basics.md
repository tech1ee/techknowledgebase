---
title: "CPU Architecture: что должен знать программист"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, appendix, cpu, registers, cache, architecture]
related:
  - "[[memory-model-fundamentals]]"
  - "[[processes-threads-fundamentals]]"
---

# CPU Architecture: что должен знать программист

> **TL;DR:** CPU выполняет инструкции через цикл Fetch → Decode → Execute. Регистры — сверхбыстрая память внутри CPU (1 cycle access). Cache hierarchy: L1 (1-3 cycles, 32-128 KB) → L2 (~10 cycles, 256 KB-1 MB) → L3 (~40 cycles, 4-64 MB) → RAM (~100+ cycles). Cache miss дорогой: ~100x медленнее cache hit. Для производительности: data locality, cache-friendly patterns, избегать branch misprediction.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Memory Model** | Понимание stack/heap | [[memory-model-fundamentals]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **CPU** | Центральный процессор | Мозг компьютера |
| **Register** | Сверхбыстрая память в CPU | Карманы рабочего |
| **Cache** | Быстрая память между CPU и RAM | Ящик рабочего стола |
| **Pipeline** | Конвейер выполнения инструкций | Конвейер на заводе |
| **ALU** | Арифметико-логическое устройство | Калькулятор |
| **Instruction** | Команда для CPU | Задача для работника |

---

## ПОЧЕМУ программисту знать CPU

### Проблема: код медленный, и непонятно почему

```kotlin
// Вариант A: ~100ms
for (i in 0 until rows) {
    for (j in 0 until cols) {
        sum += matrix[i][j]  // Row-major: cache-friendly
    }
}

// Вариант B: ~800ms (8x медленнее!)
for (j in 0 until cols) {
    for (i in 0 until rows) {
        sum += matrix[i][j]  // Column-major: cache-unfriendly
    }
}
```

Оба делают одно и то же, но разница в 8 раз. Понимание CPU объясняет почему.

### Что даёт понимание CPU

- Объяснение "магических" оптимизаций
- Понимание почему branches дорогие
- Выбор правильных структур данных
- Отладка performance проблем

---

## ЧТО такое CPU

### Основные компоненты

```
┌─────────────────────────────────────────────────────────────┐
│                    CPU ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                    CPU CORE                          │  │
│   │  ┌───────────────┐    ┌───────────────┐            │  │
│   │  │   REGISTERS   │    │  CONTROL UNIT │            │  │
│   │  │ ───────────── │    │ ───────────── │            │  │
│   │  │ PC, SP, R0-R15│    │ Fetch/Decode  │            │  │
│   │  │ FLAGS, etc.   │    │ Control logic │            │  │
│   │  └───────────────┘    └───────────────┘            │  │
│   │                                                      │  │
│   │  ┌───────────────┐    ┌───────────────┐            │  │
│   │  │     ALU       │    │     FPU       │            │  │
│   │  │ ───────────── │    │ ───────────── │            │  │
│   │  │ +, -, *, /    │    │ Float ops     │            │  │
│   │  │ AND, OR, XOR  │    │               │            │  │
│   │  └───────────────┘    └───────────────┘            │  │
│   │                                                      │  │
│   │  ┌─────────────────────────────────────────┐       │  │
│   │  │              L1 CACHE                    │       │  │
│   │  │  I-Cache (instructions) + D-Cache (data) │       │  │
│   │  └─────────────────────────────────────────┘       │  │
│   └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                    L2 CACHE                          │  │
│   └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              L3 CACHE (shared)                       │  │
│   └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                    RAM                               │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Регистры: самая быстрая память

### Типы регистров

| Регистр | Назначение |
|---------|------------|
| **Program Counter (PC)** | Адрес следующей инструкции |
| **Stack Pointer (SP)** | Вершина стека |
| **Instruction Register (IR)** | Текущая инструкция |
| **General Purpose (R0-R15)** | Данные для вычислений |
| **Flags/Status** | Результаты сравнений (zero, carry) |

### Регистры x86-64

```
┌─────────────────────────────────────────────────────────────┐
│                x86-64 GENERAL PURPOSE REGISTERS             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   64-bit    32-bit    16-bit    8-bit                      │
│   ───────   ───────   ───────   ───────                    │
│   RAX       EAX       AX        AL        Accumulator      │
│   RBX       EBX       BX        BL        Base             │
│   RCX       ECX       CX        CL        Counter          │
│   RDX       EDX       DX        DL        Data             │
│   RSI       ESI       SI        SIL       Source Index     │
│   RDI       EDI       DI        DIL       Dest Index       │
│   RSP       ESP       SP        SPL       Stack Pointer    │
│   RBP       EBP       BP        BPL       Base Pointer     │
│   R8-R15    R8D-R15D  R8W-R15W  R8B-R15B  Additional       │
│                                                             │
│   Доступ: 1 cycle (< 1 ns)                                 │
│   Количество: ограничено (~16 GPR)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Почему регистры быстрые

- Физически внутри CPU
- Нет bus latency
- Прямое подключение к ALU
- Hardware address (не memory address)

---

## Instruction Cycle: как CPU работает

### Fetch → Decode → Execute

```
┌─────────────────────────────────────────────────────────────┐
│                 INSTRUCTION CYCLE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. FETCH                                                  │
│      ┌─────────┐                                           │
│      │ Memory  │──▶ Загрузить инструкцию по адресу в PC    │
│      └─────────┘    PC++                                   │
│           │                                                 │
│           ▼                                                 │
│   2. DECODE                                                 │
│      ┌─────────┐                                           │
│      │ Decoder │──▶ Определить операцию                    │
│      └─────────┘    Определить операнды                    │
│           │                                                 │
│           ▼                                                 │
│   3. EXECUTE                                                │
│      ┌─────────┐                                           │
│      │   ALU   │──▶ Выполнить операцию                     │
│      └─────────┘    (сложение, сравнение, etc.)            │
│           │                                                 │
│           ▼                                                 │
│   4. MEMORY (опционально)                                  │
│      ┌─────────┐                                           │
│      │ Memory  │──▶ Load/Store данных                      │
│      └─────────┘                                           │
│           │                                                 │
│           ▼                                                 │
│   5. WRITE BACK                                             │
│      ┌─────────┐                                           │
│      │Register │──▶ Записать результат                     │
│      └─────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline: параллельное выполнение

```
┌─────────────────────────────────────────────────────────────┐
│                    CPU PIPELINE                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Без pipeline: 5 инструкций = 25 cycles                   │
│   ┌─────┬─────┬─────┬─────┬─────┐                          │
│   │ I1  │ I2  │ I3  │ I4  │ I5  │                          │
│   │FDEXW│FDEXW│FDEXW│FDEXW│FDEXW│                          │
│   └─────┴─────┴─────┴─────┴─────┘                          │
│   Cycles: 5 + 5 + 5 + 5 + 5 = 25                           │
│                                                             │
│   С pipeline: 5 инструкций = 9 cycles                      │
│   Cycle:  1   2   3   4   5   6   7   8   9                │
│   I1:     F   D   E   X   W                                │
│   I2:         F   D   E   X   W                            │
│   I3:             F   D   E   X   W                        │
│   I4:                 F   D   E   X   W                    │
│   I5:                     F   D   E   X   W                │
│                                                             │
│   F=Fetch, D=Decode, E=Execute, X=Memory, W=WriteBack      │
│                                                             │
│   Выигрыш: почти 3x быстрее!                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline Hazards

**Branch misprediction:** CPU предсказывает направление branch. Если ошибся — pipeline flush (~10-20 cycles penalty).

```kotlin
// Непредсказуемый branch — дорого
if (random() > 0.5) {
    doA()
} else {
    doB()
}

// Предсказуемый branch — дёшево
if (user.isAdmin) {  // Обычно false
    showAdminPanel()
}
```

---

## Cache Hierarchy: память близко к CPU

### Уровни cache

```
┌─────────────────────────────────────────────────────────────┐
│                   MEMORY HIERARCHY                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Скорость                           Размер                 │
│   ▲                                  ▲                     │
│   │  ┌─────────────┐                │                      │
│   │  │  REGISTERS  │  1 cycle       │  ~1 KB               │
│   │  └─────────────┘                │                      │
│   │         ▼                       │                      │
│   │  ┌─────────────┐                │                      │
│   │  │  L1 CACHE   │  1-3 cycles    │  32-128 KB           │
│   │  └─────────────┘                │                      │
│   │         ▼                       │                      │
│   │  ┌─────────────┐                │                      │
│   │  │  L2 CACHE   │  ~10 cycles    │  256 KB - 1 MB       │
│   │  └─────────────┘                │                      │
│   │         ▼                       │                      │
│   │  ┌─────────────┐                │                      │
│   │  │  L3 CACHE   │  ~40 cycles    │  4-64 MB             │
│   │  └─────────────┘                │                      │
│   │         ▼                       │                      │
│   │  ┌─────────────┐                │                      │
│   │  │    RAM      │  ~100+ cycles  │  8-64 GB             │
│   │  └─────────────┘                ▼                      │
│   │                                                         │
│   │  Разница L1 vs RAM: ~100x!                             │
│   │                                                         │
└─────────────────────────────────────────────────────────────┘
```

### Cache Hit vs Miss

```
┌─────────────────────────────────────────────────────────────┐
│                CACHE HIT vs MISS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   CACHE HIT (данные в cache):                              │
│   CPU → L1 → ✓ Found! → Return data                        │
│   Время: 1-3 cycles                                        │
│                                                             │
│   CACHE MISS (данные не в cache):                          │
│   CPU → L1 → ✗ → L2 → ✗ → L3 → ✗ → RAM → Load to cache    │
│   Время: 100+ cycles                                       │
│                                                             │
│   Разница: до 100x медленнее!                              │
│                                                             │
│   Locality of Reference:                                    │
│   - Temporal: недавно использованное нужно снова           │
│   - Spatial: соседние данные тоже нужны                    │
│                                                             │
│   Поэтому cache загружает целые cache lines (~64 bytes)    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Практика: cache-friendly код

### Row-major vs Column-major

```kotlin
val matrix = Array(1000) { IntArray(1000) }

// ✅ Cache-friendly: sequential access
for (i in 0 until 1000) {
    for (j in 0 until 1000) {
        sum += matrix[i][j]  // Соседние элементы в памяти
    }
}
// matrix[0][0], [0][1], [0][2]... в одной cache line

// ❌ Cache-unfriendly: random access pattern
for (j in 0 until 1000) {
    for (i in 0 until 1000) {
        sum += matrix[i][j]  // Прыжки через 1000 элементов
    }
}
// matrix[0][0], [1][0], [2][0]... в разных cache lines
```

### Struct of Arrays vs Array of Structs

```kotlin
// ❌ Array of Structs (AoS)
data class Particle(val x: Float, val y: Float, val z: Float, val mass: Float)
val particles = Array(10000) { Particle(0f, 0f, 0f, 1f) }

// При обработке только x: загружаем y, z, mass тоже
for (p in particles) {
    sumX += p.x  // Cache загружает все 16 bytes
}

// ✅ Struct of Arrays (SoA)
class ParticleSystem(val n: Int) {
    val x = FloatArray(n)
    val y = FloatArray(n)
    val z = FloatArray(n)
    val mass = FloatArray(n)
}

// При обработке только x: загружаем только x
for (i in 0 until n) {
    sumX += x[i]  // Cache эффективен
}
```

---

## Подводные камни

### Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Случайный доступ к большому массиву | Cache misses | Sequential access |
| Много branches в hot loop | Pipeline stalls | Branchless code, sorting |
| False sharing (многопоточность) | Cache invalidation | Padding между данными потоков |

### Мифы и заблуждения

**Миф:** "Современные CPU настолько быстрые, что оптимизация не нужна"
**Реальность:** Cache miss в 100x дороже cache hit. На больших данных это критично.

**Миф:** "Компилятор всё оптимизирует"
**Реальность:** Компилятор не может изменить алгоритм или layout данных. Программист должен думать о locality.

---

## Куда дальше

**Если здесь впервые:**
→ Попробуй измерить разницу row-major vs column-major

**Если понял и хочешь глубже:**
→ [[os-fundamentals-for-devs]] — как ОС управляет CPU

**Практическое применение:**
→ Оптимизация hot paths в приложениях

---

## Источники

- [Wikipedia: CPU](https://en.wikipedia.org/wiki/Central_processing_unit) — comprehensive reference
- [Wikipedia: CPU Cache](https://en.wikipedia.org/wiki/CPU_cache) — cache details
- [Bottom Up CS](https://www.bottomupcs.com/ch03.html) — for programmers
- [What Every Programmer Should Know About Memory](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf) — Ulrich Drepper classic

---

*Проверено: 2026-01-09*

---
title: "Интерпретация и JIT: от байткода к скорости"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, compilation, jit, interpreter, hotspot, v8, optimization]
related:
  - "[[compilation-pipeline]]"
  - "[[bytecode-virtual-machines]]"
  - "[[native-compilation-llvm]]"
---

# Интерпретация и JIT: от байткода к скорости

> **TL;DR:** Интерпретатор выполняет код построчно — быстрый старт, медленное исполнение. Компилятор транслирует весь код заранее — медленный старт, быстрое исполнение. JIT (Just-In-Time) — гибрид: начинает с интерпретации, компилирует "горячий" код во время работы. HotSpot JVM использует tiered compilation (5 уровней), V8 — 4-tier pipeline. Inline caching ускоряет dynamic dispatch. Деоптимизация возвращает к интерпретации при нарушении предположений. Для KMP критично: понимание JIT помогает писать "дружественный" к оптимизатору код.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Bytecode** | Что JIT компилирует | [[bytecode-virtual-machines]] |
| **AOT compilation** | Альтернатива JIT | [[native-compilation-llvm]] |
| **Compilation pipeline** | Фазы компиляции | [[compilation-pipeline]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Interpreter** | Выполняет код построчно | Синхронный переводчик |
| **JIT** | Компиляция во время выполнения | Переводчик, записывающий частые фразы |
| **Hot code** | Часто выполняемый код | Протоптанная тропинка |
| **Warmup** | Период до peak performance | Разогрев двигателя |
| **Deoptimization** | Откат оптимизаций | Возврат к базовой версии |
| **Inline Caching** | Кэширование результатов lookup | Записная книжка номеров |
| **Tiered Compilation** | Многоуровневая компиляция | Лестница оптимизаций |

---

## ПОЧЕМУ существует JIT

### Дилемма: скорость запуска vs скорость исполнения

Два классических подхода:

**Интерпретатор:**
- Быстрый старт (нет фазы компиляции)
- Медленное исполнение (трансляция каждой инструкции)
- Простая отладка

**AOT-компилятор:**
- Медленный старт (компиляция всего кода)
- Быстрое исполнение (native code)
- Сложная кросс-компиляция

Для сервера с uptime годами — AOT логичен. Для CLI-утилиты — интерпретация. Но что если нужно и то, и другое?

### JIT: лучшее из двух миров

JIT-компиляция — компромисс:

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION TIMELINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Interpreter:                                                  │
│   ═══════════════════════════════════════════════════════      │
│   Скорость: ▓▓░░░░░░░░ (постоянно низкая)                      │
│                                                                 │
│   AOT Compiler:                                                 │
│   ░░░░░═══════════════════════════════════════════════════     │
│   Скорость: ░░░░▓▓▓▓▓▓▓▓▓▓ (после долгой компиляции)           │
│   [compile]                                                     │
│                                                                 │
│   JIT:                                                          │
│   ═══════▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓             │
│   [interpret] → [profile] → [compile hot code] → [peak]        │
│   Скорость растёт по мере работы                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

JIT начинает быстро (интерпретация), но со временем достигает native-подобной скорости.

### История JIT

**1960:** John McCarthy упомянул runtime compilation в работе по LISP — первое теоретическое описание.

**1968:** Ken Thompson применил JIT для regex в редакторе QED — компилировал regex в machine code.

**1984:** Smalltalk-80 ввёл inline caching — ключевую технику для dynamic dispatch.

**1999:** Sun выпустил HotSpot JVM — название отражает идею: "горячие точки" кода компилируются.

**2008:** Google V8 сделал JavaScript быстрым — JIT для браузера.

---

## КАК работает интерпретатор

### Fetch-Decode-Execute цикл

Интерпретатор — это цикл:

```
┌─────────────────────────────────────────────────────────────────┐
│                 INTERPRETER LOOP                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   while (running) {                                             │
│       instruction = fetch(program_counter)   // Fetch           │
│       operation = decode(instruction)        // Decode          │
│       execute(operation)                     // Execute         │
│       program_counter++                                         │
│   }                                                             │
│                                                                 │
│   Каждая инструкция: fetch + decode + execute                  │
│   Overhead на каждую операцию                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему интерпретатор медленнее

Даже простое `a + b`:

1. Fetch: прочитать байткод инструкции
2. Decode: определить тип операции (ADD)
3. Fetch operands: загрузить `a` и `b`
4. Execute: выполнить сложение
5. Store: сохранить результат
6. Increment PC: перейти к следующей инструкции

В native code: одна инструкция `ADD` процессора. В интерпретаторе: десятки инструкций обёртки.

### Threaded Interpretation

Оптимизация: вместо switch-case — direct threading или indirect threading. Уменьшает overhead dispatch, но не устраняет его.

---

## КАК работает JIT

### Базовый алгоритм

```
┌─────────────────────────────────────────────────────────────────┐
│                    JIT COMPILATION FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. INTERPRET + PROFILE                                        │
│      ├── Выполнять байткод                                     │
│      ├── Считать вызовы методов                                │
│      └── Собирать type information                             │
│                                                                 │
│   2. DETECT HOT CODE                                           │
│      ├── Метод вызван > threshold раз?                         │
│      └── Loop iteration count > threshold?                     │
│                                                                 │
│   3. COMPILE TO NATIVE                                         │
│      ├── Применить оптимизации                                 │
│      ├── Использовать profile data                             │
│      └── Сгенерировать machine code                            │
│                                                                 │
│   4. REPLACE & EXECUTE                                         │
│      ├── Подменить интерпретируемый код                        │
│      └── Исполнять native версию                               │
│                                                                 │
│   5. DEOPTIMIZE (если нужно)                                   │
│      ├── Предположения нарушены?                               │
│      └── Вернуться к интерпретации                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Профилирование

JIT собирает runtime information:

- **Invocation counts:** сколько раз вызван метод
- **Branch frequencies:** какие ветки if/else чаще
- **Type information:** какие типы приходят в аргументы
- **Call sites:** какие методы вызываются откуда

Эта информация недоступна AOT-компилятору — JIT может оптимизировать агрессивнее.

### Спекулятивные оптимизации

JIT делает предположения на основе профиля:

```kotlin
fun calculate(x: Any): Int {
    return (x as Int) + 1
}
```

Если профиль показывает, что `x` всегда `Int`:

```
// JIT может сгенерировать:
1. Guard: check if x is Int
2. If yes: direct add (no boxing)
3. If no: deoptimize (bailout)
```

Пока предположение верно — быстрый путь. Нарушилось — деоптимизация.

---

## JVM Tiered Compilation

### Пять уровней

HotSpot JVM использует tiered compilation с 5 уровнями:

| Level | Compiler | Что происходит |
|-------|----------|----------------|
| **0** | Interpreter | Интерпретация + профилирование |
| **1** | C1 | Быстрая компиляция без профилирования (trivial methods) |
| **2** | C1 | Компиляция с лёгким профилированием (C2 занят) |
| **3** | C1 | Полное профилирование |
| **4** | C2 | Агрессивные оптимизации |

### Типичный путь

Большинство методов проходят: `0 → 3 → 4`

```
Interpreter (Level 0)
    ↓ [порог вызовов достигнут]
C1 с профилированием (Level 3)
    ↓ [горячий код + профиль готов]
C2 оптимизации (Level 4)
```

### C1 vs C2

**C1 (Client Compiler):**
- Быстрая компиляция
- Базовые оптимизации
- Цель: быстро получить native code

**C2 (Server Compiler):**
- Медленная компиляция
- Агрессивные оптимизации: inlining, escape analysis, loop unrolling
- Цель: максимальная производительность

### Graal Compiler

Альтернативный C2, написанный на Java:

- Лучше для некоторых паттернов
- Partial Escape Analysis
- Основа GraalVM

---

## V8 Pipeline (Chrome/Node.js)

### Четыре уровня (2023+)

V8 эволюционировал в 4-tier систему:

```
┌─────────────────────────────────────────────────────────────────┐
│                    V8 COMPILATION PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   JavaScript Source                                             │
│         ↓                                                       │
│   ┌─────────────┐                                               │
│   │   Parser    │ → AST                                         │
│   └─────────────┘                                               │
│         ↓                                                       │
│   ┌─────────────┐                                               │
│   │  Ignition   │ → Bytecode (interpreter)                      │
│   └─────────────┘                                               │
│         ↓ [warm]                                                │
│   ┌─────────────┐                                               │
│   │  Sparkplug  │ → Baseline native (быстрый)                   │
│   └─────────────┘                                               │
│         ↓ [hot]                                                 │
│   ┌─────────────┐                                               │
│   │   Maglev    │ → Mid-tier optimized                          │
│   └─────────────┘                                               │
│         ↓ [very hot]                                            │
│   ┌─────────────┐                                               │
│   │  TurboFan   │ → Fully optimized                             │
│   └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Ignition

Интерпретатор байткода:
- Компактный bytecode (50-75% меньше baseline machine code)
- Register-based VM
- Собирает feedback для оптимизаторов

### TurboFan

Оптимизирующий компилятор:
- Sea-of-Nodes IR
- Speculative optimizations
- Inlining, escape analysis
- Type specialization

### Maglev (2023)

Заполняет gap между Sparkplug и TurboFan:
- 10x медленнее Sparkplug
- 10x быстрее TurboFan
- SSA-based optimizations

---

## Tracing JIT: альтернативный подход

### Method JIT vs Tracing JIT

Два подхода к определению "что компилировать":

**Method JIT (JVM, V8):**
- Единица: метод/функция
- Компилирует весь метод
- Inlining — явное решение

**Tracing JIT (LuaJIT, PyPy):**
- Единица: горячий trace (путь через loops)
- Записывает реальный путь исполнения
- Inlining автоматический (trace включает вызовы)

### Как работает Tracing

```
1. Интерпретировать код
2. Найти горячий loop (много итераций)
3. Начать "запись" trace
4. Записать все операции одной итерации
5. Скомпилировать trace в native code
6. Исполнять native (с guards)
```

### Плюсы и минусы

**Tracing плюсы:**
- Проще реализовать
- Автоматический inlining
- Хорошо для predictable loops

**Tracing минусы:**
- Performance cliffs (непредсказуемые провалы)
- Плохо для polymorphic code
- Много guards = overhead

PyPy использует meta-tracing: трассирует интерпретатор, а не программу.

---

## Inline Caching

### Проблема Dynamic Dispatch

В динамических языках метод определяется в runtime:

```javascript
function process(obj) {
    return obj.calculate();  // Какой calculate?
}
```

Каждый вызов: lookup метода по имени → медленно.

### Решение: запоминать

Inline cache запоминает результат lookup:

```
┌─────────────────────────────────────────────────────────────────┐
│                    INLINE CACHING STATES                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   UNINITIALIZED                                                 │
│       ↓ [первый вызов с типом A]                               │
│   MONOMORPHIC                                                   │
│   "Если тип = A, вызвать A.calculate()"                        │
│       ↓ [вызов с типом B]                                      │
│   POLYMORPHIC                                                   │
│   "Если A → A.calculate()                                      │
│    Если B → B.calculate()                                      │
│    Иначе → slow lookup"                                        │
│       ↓ [много разных типов]                                   │
│   MEGAMORPHIC                                                   │
│   "Всегда slow lookup"                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Статистика использования

Эмпирические данные из Smalltalk:
- 90% call sites — monomorphic (один тип)
- 9% — polymorphic (несколько типов)
- 1% — megamorphic (много типов)

Monomorphic = почти бесплатный dispatch.

### Влияние на код

Код с предсказуемыми типами быстрее:

```kotlin
// ХОРОШО: monomorphic
list.forEach { item: User ->
    item.process()
}

// ПЛОХО: megamorphic
list.forEach { item: Any ->
    (item as Processable).process()
}
```

---

## Деоптимизация

### Зачем нужна

JIT делает спекулятивные оптимизации на основе профиля. Профиль может устареть.

```kotlin
fun calculate(x: Number): Int {
    return x.toInt() + 1
}

// Первые 10000 вызовов: x всегда Int
// JIT оптимизирует под Int

// Вызов 10001: x = Double
// Оптимизация неверна!
```

### Как работает

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEOPTIMIZATION FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Optimized Code                                                │
│       │                                                         │
│       ▼                                                         │
│   ┌─────────────────┐                                           │
│   │  Guard Check    │  ← "x instanceof Int?"                    │
│   └────────┬────────┘                                           │
│            │                                                    │
│       ┌────┴────┐                                               │
│       │         │                                               │
│      YES       NO                                               │
│       │         │                                               │
│       ▼         ▼                                               │
│   Fast Path   Bailout                                           │
│   (optimized) (деоптимизация)                                   │
│                 │                                               │
│                 ▼                                               │
│            Interpreter                                          │
│            (с нового профиля)                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Типы деоптимизации

**Synchronous:** guard сработал в текущем потоке
**Asynchronous:** другой поток изменил что-то (class hierarchy)

После деоптимизации возможна реоптимизация с новым профилем.

---

## Warmup: холодный старт

### Проблема

JIT достигает peak performance только после warmup:

```
Время   |  Производительность
--------|---------------------
0-1s    |  ▓░░░░░░░░░ (интерпретация)
1-5s    |  ▓▓▓░░░░░░░ (C1 компиляция)
5-30s   |  ▓▓▓▓▓▓░░░░ (C2 компиляция)
30s+    |  ▓▓▓▓▓▓▓▓▓▓ (peak)
```

Для serverless функций (исполнение < 1 секунды) — катастрофа.

### Решения

**1. CRaC (Coordinated Restore at Checkpoint)**
- "Замораживает" JVM в оптимизированном состоянии
- Восстановление за миллисекунды
- Требует Linux

**2. AOT Method Profiling (JEP 515)**
- Сохраняет профили между запусками
- Компиляция начинается сразу

**3. CDS/AppCDS (Class Data Sharing)**
- Предзагружает классы
- Экономит время на class loading

**4. GraalVM Native Image**
- AOT компиляция до запуска
- Instant startup
- Теряет runtime оптимизации

**5. Tiered Compilation Tuning**
- `-XX:TieredStopAtLevel=1` — только C1
- Быстрее warmup, ниже peak

---

## Оптимизации JIT

### Inlining

Подстановка тела функции вместо вызова:

```kotlin
// До inlining
fun sum(a: Int, b: Int) = a + b
fun calculate() = sum(1, 2) + sum(3, 4)

// После inlining
fun calculate() = (1 + 2) + (3 + 4)
```

Плюсы: нет overhead вызова, открывает другие оптимизации.
Минусы: увеличивает размер кода.

### Escape Analysis

Определяет, "убегает" ли объект из метода:

```kotlin
fun process(): Int {
    val point = Point(1, 2)  // Не "убегает"
    return point.x + point.y
}

// JIT может: allocate on stack, или вообще убрать объект
```

### Dead Code Elimination

Удаляет код, который не влияет на результат.

### Loop Unrolling

Разворачивает итерации цикла для уменьшения overhead.

### Constant Folding

Вычисляет константные выражения во время компиляции.

---

## Подводные камни

### 1. Megamorphic call sites

```kotlin
// ПЛОХО: JIT не может оптимизировать
val handlers: List<Handler> = listOf(A(), B(), C(), D(), E(), F(), ...)
handlers.forEach { it.handle() }  // megamorphic!
```

### 2. Reflection ломает оптимизации

```kotlin
// JIT не может инлайнить
method.invoke(obj, args)
```

### 3. Непредсказуемые branches

```kotlin
// ПЛОХО: 50/50 branch
if (random.nextBoolean()) {
    pathA()
} else {
    pathB()
}

// ХОРОШО: предсказуемый branch
if (isCommonCase) {  // true в 99% случаев
    fastPath()
} else {
    slowPath()
}
```

### Мифы

**Миф:** JIT всегда быстрее AOT.
**Реальность:** JIT имеет warmup overhead. Для short-lived processes AOT может быть лучше.

**Миф:** Больше оптимизаций = лучше.
**Реальность:** Агрессивные оптимизации имеют cost. Иногда C1 достаточно.

---

## Куда дальше

**Для понимания байткода:**
→ [[bytecode-virtual-machines]] — что JIT компилирует

**Для AOT альтернативы:**
→ [[native-compilation-llvm]] — Kotlin/Native, GraalVM Native Image

**Для оптимизаций:**
→ [[compilation-pipeline]] — фазы оптимизации

---

## Источники

- [Wikipedia: JIT Compilation](https://en.wikipedia.org/wiki/Just-in-time_compilation) — история и обзор
- [Baeldung: JVM Tiered Compilation](https://www.baeldung.com/jvm-tiered-compilation) — уровни JVM
- [V8 Blog: Ignition and TurboFan](https://v8.dev/blog/launching-ignition-and-turbofan) — V8 архитектура
- [Oracle: JIT Understanding](https://docs.oracle.com/cd/E13150_01/jrockit_jvm/jrockit/geninfo/diagnos/underst_jit.html) — Oracle JRockit docs
- [kipp.ly: JITs Implementations](https://kipp.ly/jits-impls/) — сравнение подходов
- [jayconrod: Polymorphic Inline Caches](https://jayconrod.com/posts/44/polymorphic-inline-caches-explained) — inline caching
- [OpenJDK: JEP 515](https://openjdk.org/jeps/515) — AOT profiling

---

*Проверено: 2026-01-09*

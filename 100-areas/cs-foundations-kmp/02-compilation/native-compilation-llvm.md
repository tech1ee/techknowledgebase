---
title: "Native Compilation и LLVM: как Kotlin становится машинным кодом"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/advanced
related:
  - "[[compilation-pipeline]]"
  - "[[bytecode-virtual-machines]]"
  - "[[interpretation-jit]]"
---

# Native Compilation и LLVM: как Kotlin становится машинным кодом

> **TL;DR:** LLVM — модульная инфраструктура компиляторов, которая превращает промежуточное представление (IR) в машинный код для любой платформы. Kotlin/Native использует LLVM для компиляции в native binary без VM. AOT компиляция даёт мгновенный старт, но теряет runtime-оптимизации JIT. Для KMP: iOS/macOS приложения работают через Kotlin/Native → LLVM → ARM/x86 binary.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Compilation Pipeline** | Понять где IR и backend | [[compilation-pipeline]] |
| **Bytecode и VM** | Понять альтернативу — bytecode + VM | [[bytecode-virtual-machines]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **LLVM** | Инфраструктура компиляторов | Фабрика по производству компиляторов |
| **LLVM IR** | Промежуточный код LLVM | Универсальный чертёж |
| **AOT** | Ahead-Of-Time компиляция | Готовый перевод книги |
| **JIT** | Just-In-Time компиляция | Синхронный переводчик |
| **Native binary** | Машинный код для CPU | Инструкции напрямую процессору |
| **Konan** | Kotlin/Native компилятор | Kotlin → LLVM конвертер |
| **SSA** | Static Single Assignment | Каждая переменная пишется один раз |

---

## ПОЧЕМУ появился LLVM

### Проблема: создание компилятора — титаническая работа

До LLVM создание нового языка требовало написания компилятора с нуля: парсер, оптимизатор, кодогенератор для каждой платформы. GCC (GNU Compiler Collection) решал часть проблем, но был монолитным — использовать только оптимизатор отдельно было невозможно.

### 2000: Chris Lattner и рождение LLVM

Chris Lattner, аспирант University of Illinois, задался вопросом: какой должна быть инфраструктура компиляторов, чтобы поддерживать языки, которых ещё не существует?

На рождественских каникулах 2000 года он начал LLVM. Ключевая идея: модульная архитектура с чётким разделением на frontend, optimizer и backend.

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLVM: МОДУЛЬНАЯ АРХИТЕКТУРА                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ДО LLVM (монолит):                                            │
│   ┌─────────────────────────────────────────────┐               │
│   │  Parser + Optimizer + CodeGen for x86       │               │
│   │  Parser + Optimizer + CodeGen for ARM       │               │
│   │  ...каждая комбинация отдельно              │               │
│   └─────────────────────────────────────────────┘               │
│                                                                 │
│   LLVM (модули):                                                │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐                       │
│   │ Clang   │──▶│  LLVM   │──▶│ x86     │                       │
│   │ (C/C++) │   │   IR    │   │ Backend │                       │
│   └─────────┘   │         │   └─────────┘                       │
│   ┌─────────┐   │         │   ┌─────────┐                       │
│   │ Konan   │──▶│Optimizer│──▶│ ARM     │                       │
│   │(Kotlin) │   │         │   │ Backend │                       │
│   └─────────┘   └─────────┘   └─────────┘                       │
│                                                                 │
│   M языков + N платформ = M+N компонентов (не M×N)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Apple и расцвет LLVM

В 2005 году Apple наняла Lattner. GCC не давал им достаточного контроля над Objective-C. LLVM стал основой инструментов разработчика Apple.

В 2010 Lattner начал работу над Swift — тайно, по вечерам и выходным. Год спустя показал прототип руководству Apple. Первая реакция была скептической: "зачем новый язык, если Objective-C сделал iPhone успешным?" Но Swift всё равно случился — во многом благодаря LLVM.

---

## ЧТО такое LLVM

### Не виртуальная машина

Изначально LLVM расшифровывалось как "Low Level Virtual Machine". С 2011 года это просто название — LLVM давно не является виртуальной машиной в традиционном смысле.

LLVM — это:
- **Компиляторная инфраструктура** — набор библиотек
- **Промежуточное представление** (LLVM IR)
- **Оптимизаторы** — modular optimization passes
- **Backend'ы** — генераторы кода для разных платформ

### Три фазы компиляции

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLVM: ТРИ ФАЗЫ                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. FRONTEND (Clang, Konan, rustc, swiftc)                     │
│      ┌──────────────────────────────────────────┐               │
│      │ Исходный код → Парсинг → AST → LLVM IR   │               │
│      └──────────────────────────────────────────┘               │
│                          ↓                                      │
│   2. OPTIMIZER (Middle-end)                                     │
│      ┌──────────────────────────────────────────┐               │
│      │ LLVM IR → Optimization Passes → LLVM IR  │               │
│      │ (constant folding, DCE, inlining, ...)   │               │
│      └──────────────────────────────────────────┘               │
│                          ↓                                      │
│   3. BACKEND (x86, ARM, RISC-V, ...)                            │
│      ┌──────────────────────────────────────────┐               │
│      │ LLVM IR → Machine Code для целевой CPU   │               │
│      └──────────────────────────────────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### LLVM IR: универсальный язык

LLVM IR — типизированный, низкоуровневый язык в SSA-форме. Три формата:
- **.ll** — текстовый, человекочитаемый
- **in-memory** — для работы компилятора
- **.bc** — битовый, компактный

Пример IR:
```llvm
define i32 @add(i32 %a, i32 %b) {
entry:
    %result = add i32 %a, %b
    ret i32 %result
}
```

Что здесь:
- `define i32 @add` — определение функции, возвращающей i32
- `%a`, `%b` — параметры (локальные значения)
- `add i32 %a, %b` — сложение двух i32
- `%result` — результат (каждое значение присваивается один раз — SSA)

### SSA и Phi-ноды

SSA (Static Single Assignment) означает: каждая переменная присваивается ровно один раз. Это упрощает анализ данных.

Но что если переменная может получить разные значения в зависимости от условия? Используются phi-ноды:

```llvm
; Функция max(a, b)
define i32 @max(i32 %a, i32 %b) {
entry:
    %cmp = icmp sgt i32 %a, %b    ; сравнить a > b
    br i1 %cmp, label %then, label %else

then:
    br label %merge

else:
    br label %merge

merge:
    ; phi выбирает значение в зависимости от того, откуда пришли
    %result = phi i32 [%a, %then], [%b, %else]
    ret i32 %result
}
```

Phi-нода говорит: "если пришли из `%then`, результат = `%a`; если из `%else`, результат = `%b`".

---

## AOT vs JIT

### Ahead-Of-Time (AOT)

AOT компилирует код до запуска программы — на этапе сборки:

```
Source → Compiler → Native Binary → Execute
         (build time)              (runtime)
```

**Преимущества AOT:**
- Мгновенный старт — код уже скомпилирован
- Меньше памяти — не нужен компилятор в runtime
- Предсказуемое поведение — нет "прогрева"

**Недостатки AOT:**
- Нет runtime-оптимизаций
- Больший размер бинарника (все пути кода)
- Нельзя оптимизировать под реальные данные

### Just-In-Time (JIT)

JIT компилирует код во время исполнения:

```
Source → Bytecode → Interpret → Profile → JIT Compile → Execute
                                (warmup)
```

**Преимущества JIT:**
- Profile-guided optimization — оптимизирует горячие пути
- Адаптация к реальным данным
- Спекулятивные оптимизации

**Недостатки JIT:**
- Медленный старт (warmup period)
- Больше памяти (компилятор в runtime)
- Непредсказуемые паузы (компиляция во время работы)

### Когда что использовать

```
┌─────────────────────────────────────────────────────────────────┐
│                    AOT vs JIT: ВЫБОР                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   AOT (Kotlin/Native, Swift):                                   │
│   ✓ CLI tools                                                   │
│   ✓ Serverless functions (cold start критичен)                  │
│   ✓ iOS приложения                                              │
│   ✓ Embedded systems                                            │
│                                                                 │
│   JIT (JVM, V8):                                                │
│   ✓ Long-running servers                                        │
│   ✓ Приложения с warmup-временем                                │
│   ✓ Динамичный код (reflection, eval)                           │
│   ✓ Android (ART = AOT + JIT гибрид)                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## КАК работает Kotlin/Native

### Архитектура компилятора Konan

Kotlin/Native использует компилятор Konan:

```
┌─────────────────────────────────────────────────────────────────┐
│                    KOTLIN/NATIVE PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   .kt файлы                                                     │
│       │                                                         │
│       ▼                                                         │
│   ┌─────────────────┐                                           │
│   │ Kotlin Frontend │  K2 (FIR)                                 │
│   │   (shared)      │  Parsing, type checking                   │
│   └────────┬────────┘                                           │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │   Kotlin IR     │  Высокоуровневый IR                       │
│   └────────┬────────┘                                           │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │     Konan       │  Kotlin/Native специфичный код            │
│   │   (lowering)    │  Memory management, interop               │
│   └────────┬────────┘                                           │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │    LLVM IR      │  Низкоуровневый IR                        │
│   └────────┬────────┘                                           │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │  LLVM Backend   │  Optimization + Code Generation           │
│   └────────┬────────┘                                           │
│            ▼                                                    │
│   Native Binary (iOS, macOS, Linux, ...)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### LLVM Optimization Passes

Kotlin/Native запускает две последовательности оптимизаций:

1. **ModuleBitcodeOptimization** — на уровне модуля
2. **LTOBitcodeOptimization** — Link-Time Optimization

Основные passes:
- **Constant Folding:** `2 + 3` → `5`
- **Dead Code Elimination:** удаление недостижимого кода
- **Inlining:** подстановка тела функции
- **LICM:** вынос инвариантов из циклов
- **GVN:** Global Value Numbering

### Поддерживаемые платформы

Kotlin/Native поддерживает 27+ таргетов:

| Платформа | Таргеты |
|-----------|---------|
| **iOS** | arm64, x86_64 (simulator) |
| **macOS** | arm64, x86_64 |
| **Linux** | x64, arm64, arm32 |
| **Windows** | x64 (mingw) |
| **watchOS** | arm64, arm32, x86_64 (simulator) |
| **tvOS** | arm64, x86_64 (simulator) |

### Interop с платформой

Kotlin/Native предоставляет interop с C и Objective-C/Swift:

```kotlin
// cinterop — вызов C функций
import platform.posix.printf
fun main() {
    printf("Hello from Kotlin/Native\n")
}

// Objective-C interop (iOS)
import platform.UIKit.UIViewController
class MyController : UIViewController() {
    override fun viewDidLoad() {
        super.viewDidLoad()
    }
}
```

---

## LLVM Optimizations в деталях

### Constant Folding

Вычисление константных выражений compile-time:

```kotlin
// Kotlin код
val x = 2 + 3 * 4

// После constant folding
val x = 14
```

### Dead Code Elimination

Удаление кода, который никогда не выполнится:

```kotlin
fun example() {
    return 42
    println("never reached")  // DCE удалит
}
```

### Function Inlining

Подстановка тела функции вместо вызова:

```kotlin
inline fun square(x: Int) = x * x

fun main() {
    val result = square(5)  // → val result = 5 * 5 → val result = 25
}
```

Inlining позволяет другим оптимизациям работать лучше — компилятор видит конкретные значения.

### SROA (Scalar Replacement of Aggregates)

Замена структур на скалярные значения:

```kotlin
data class Point(val x: Int, val y: Int)

fun distance(p: Point): Int {
    return p.x * p.x + p.y * p.y  // Point может быть "разобран" на два Int
}
```

---

## Подводные камни

### Типичные заблуждения

| Миф | Реальность |
|-----|------------|
| LLVM = виртуальная машина | Это инфраструктура компиляторов, не VM |
| Native всегда быстрее JVM | JIT с profiling может обогнать AOT |
| AOT даёт лучший peak performance | JIT знает runtime patterns |
| Kotlin/Native = просто Kotlin | Memory management и interop отличаются |

### Когда Native оправдан

**Хороший выбор:**
- iOS/macOS приложения (нет выбора)
- CLI инструменты (быстрый старт)
- Embedded/IoT (ограниченные ресурсы)

**Стоит подумать:**
- Server-side (JVM обычно лучше)
- Android (ART оптимизирован для Dalvik/DEX)

### Debugging Native

Отладка native кода сложнее чем JVM:
- LLDB вместо Java debugger
- Меньше runtime информации
- Stack traces менее информативны

---

## Куда дальше

**Для понимания JIT:**
→ [[interpretation-jit]] — как работает JIT компиляция

**Для iOS разработки:**
→ [[kmp-ios-deep-dive]] — практическое применение Kotlin/Native

**Эксперименты:**
```bash
# Посмотреть LLVM IR из Kotlin
kotlinc-native -Xtemporary-files-dir=./temp -produce library main.kt
# IR будет в temp директории
```

---

## Источники

- [LLVM Official](https://llvm.org/) — официальный сайт проекта
- [AOSA Book: LLVM](https://aosabook.org/en/v1/llvm.html) — архитектура LLVM от создателей
- [Kotlin/Native Documentation](https://kotlinlang.org/docs/native-overview.html) — официальная документация
- [A Gentle Introduction to LLVM IR](https://mcyoung.xyz/2023/08/01/llvm-ir/) — понятный туториал

---

*Проверено: 2026-01-09*

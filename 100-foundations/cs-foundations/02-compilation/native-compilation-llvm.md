---
title: "Native Compilation и LLVM: как Kotlin становится машинным кодом"
created: 2026-01-04
modified: 2026-02-13
type: deep-dive
reading_time: 16
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/advanced
related:
  - "[[compilation-pipeline]]"
  - "[[bytecode-virtual-machines]]"
  - "[[interpretation-jit]]"
prerequisites:
  - "[[compilation-pipeline]]"
  - "[[cpu-architecture-basics]]"
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

## Связь с другими темами

### [[compilation-pipeline]]
Native compilation через LLVM — это финальная стадия compilation pipeline, где промежуточное представление превращается в машинный код. Понимание полного pipeline (lexing, parsing, semantic analysis, IR generation) необходимо, чтобы осознать, на каком этапе подключается LLVM и почему IR является ключевым звеном. Без знания предыдущих фаз сложно понять, какая информация доступна LLVM optimizer и почему некоторые оптимизации возможны только на уровне frontend.

### [[bytecode-virtual-machines]]
Bytecode и VM — это альтернативный путь исполнения кода, контрастирующий с native compilation. JVM исполняет bytecode через интерпретацию и JIT, тогда как LLVM генерирует native binary через AOT. Сравнение этих подходов позволяет понять trade-offs между мгновенным стартом (AOT) и runtime-оптимизациями (JIT), что критично для выбора между Kotlin/JVM и Kotlin/Native в KMP-проектах.

### [[interpretation-jit]]
JIT-компиляция является прямой альтернативой AOT-подходу LLVM. Понимание того, как JIT использует профилирование горячих путей для спекулятивных оптимизаций, объясняет, почему JVM-приложения после warmup могут обгонять native binary по peak performance. Знание обоих подходов необходимо для обоснованного выбора таргета в Kotlin Multiplatform.

---

## Источники и дальнейшее чтение

- Aho A., Lam M., Sethi R., Ullman J. (2006). *Compilers: Principles, Techniques, and Tools* (Dragon Book). — фундаментальное руководство по компиляторам, включая оптимизации и генерацию кода, которые LLVM реализует на практике
- Appel A. (1998). *Modern Compiler Implementation in ML/Java/C*. — альтернативный подход к теории компиляторов с акцентом на SSA-форму и промежуточные представления, лежащие в основе LLVM IR
- Grune D., van Reeuwijk K., Bal H., Jacobs C., Langendoen K. (2012). *Modern Compiler Design*. — современный взгляд на компиляторные техники, включая AOT и JIT подходы
- [LLVM Official](https://llvm.org/) — официальный сайт проекта
- [AOSA Book: LLVM](https://aosabook.org/en/v1/llvm.html) — архитектура LLVM от создателей
- [Kotlin/Native Documentation](https://kotlinlang.org/docs/native-overview.html) — официальная документация

---

## Проверь себя

> [!question]- Почему LLVM сократила количество необходимых компиляторных компонентов с M*N до M+N и как это применимо к KMP?
> LLVM ввела общий промежуточный формат (LLVM IR). Вместо написания отдельного компилятора для каждой пары "язык + платформа" (M*N), каждый язык генерирует LLVM IR (M frontend'ов) и каждая платформа потребляет его (N backend'ов). Для KMP: Kotlin K2 frontend генерирует Kotlin IR, Konan транслирует его в LLVM IR, а LLVM backend'ы генерируют код для arm64 (iOS), x86_64 (simulator), arm64 (macOS) — без написания отдельного кодогенератора для каждой цели.

> [!question]- Ты профилируешь KMP-приложение и видишь, что один и тот же алгоритм работает быстрее на JVM после прогрева, чем на Kotlin/Native. Почему AOT может проиграть JIT по пиковой производительности?
> JIT-компилятор (C2 в HotSpot) использует runtime-профилирование: знает реальные типы аргументов, частоту веток if/else, конкретные реализации на call site. Это позволяет спекулятивные оптимизации: monomorphic inlining, branch prediction, специализацию под конкретные типы. AOT (LLVM) компилирует "вслепую" — генерирует код для всех возможных путей, не зная реальных данных. Однако AOT выигрывает мгновенным стартом и предсказуемой производительностью.

> [!question]- Что такое phi-нода в LLVM IR и почему она необходима для SSA-формы?
> В SSA каждая переменная присваивается ровно один раз. Но в условных конструкциях (if/else) одна переменная может получить разные значения в зависимости от пути. Phi-нода решает это: в точке слияния путей она "выбирает" значение в зависимости от того, откуда пришёл поток управления. Например, `%result = phi i32 [%a, %then], [%b, %else]` — если пришли из then-ветки, результат = %a, из else — %b.

---

## Ключевые карточки

Что такое LLVM и чем оно не является?
?
LLVM — модульная инфраструктура компиляторов (набор библиотек: IR, оптимизатор, backend'ы). Изначально расшифровывалось как "Low Level Virtual Machine", но с 2011 это просто название. LLVM не является виртуальной машиной — он генерирует native binary, а не исполняет bytecode.

---

Какие три фазы компиляции проходит код через LLVM?
?
1) Frontend (Clang, Konan, rustc, swiftc) — исходный код -> парсинг -> AST -> LLVM IR. 2) Optimizer (Middle-end) — LLVM IR -> optimization passes -> улучшенный LLVM IR. 3) Backend (x86, ARM, RISC-V) — LLVM IR -> машинный код для целевого CPU.

---

Как устроен pipeline Kotlin/Native (Konan)?
?
.kt файлы -> K2 Frontend (shared) -> Kotlin IR -> Konan lowering (memory management, interop) -> LLVM IR -> LLVM Backend (optimization + code generation) -> Native Binary. Frontend общий для JVM/JS/Native, специфика начинается на этапе Konan lowering.

---

Три формата LLVM IR и их назначение?
?
.ll — текстовый, человекочитаемый (для отладки и изучения). In-memory — для работы компилятора в процессе компиляции. .bc (bitcode) — бинарный, компактный (для хранения и передачи между этапами).

---

Когда AOT (Native) оправдан, а когда лучше JIT (JVM)?
?
AOT: iOS/macOS приложения (нет выбора), CLI инструменты (быстрый старт), serverless (cold start критичен), embedded/IoT (ограниченные ресурсы). JIT: long-running серверы (warmup окупается), Android (ART гибрид), приложения с reflection и динамичным кодом.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[interpretation-jit]] | Понять альтернативу AOT — как JIT оптимизирует код в runtime |
| Углубиться | [[kmp-ios-deep-dive]] | Практическое применение Kotlin/Native для iOS-разработки |
| Смежная тема | [[bytecode-virtual-machines]] | Сравнить VM-подход (JVM, WASM) с native compilation |
| Обзор | [[cs-foundations-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-02-13*

---
title: "Bytecode и виртуальные машины: как код исполняется без железа"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, bytecode, jvm, wasm, dalvik, art, virtual-machine]
related:
  - "[[compilation-pipeline]]"
  - "[[native-compilation-llvm]]"
  - "[[interpretation-jit]]"
---

# Bytecode и виртуальные машины: как код исполняется без железа

> **TL;DR:** Bytecode — промежуточный код между исходником и машинным кодом. Виртуальная машина (VM) исполняет bytecode, скрывая детали железа. JVM использует stack-based архитектуру, Dalvik был register-based, WASM — stack-based с sandbox security. Для KMP критично: Kotlin компилирует в JVM bytecode (Android), DEX (через Android toolchain), LLVM IR (iOS), JavaScript и WASM (Web) — все это разные форматы исполнения.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Compilation Pipeline** | Понять откуда берётся bytecode | [[compilation-pipeline]] |
| **Stack vs Heap** | Понять работу operand stack | [[memory-model-fundamentals]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Bytecode** | Инструкции для виртуальной машины | Нотные знаки для музыканта |
| **Virtual Machine** | Программа, исполняющая bytecode | Музыкант, играющий по нотам |
| **Opcode** | Код операции в bytecode | Одна нота |
| **Operand Stack** | Стек для вычислений в VM | Стопка тарелок |
| **Class Loading** | Загрузка кода в JVM | Открыть книгу на нужной странице |
| **JIT** | Just-In-Time компиляция | Перевод на лету |
| **AOT** | Ahead-Of-Time компиляция | Заранее подготовленный перевод |
| **DEX** | Dalvik Executable формат | Android-специфичный bytecode |

---

## ПОЧЕМУ появился bytecode

### Проблема: один код — много платформ

В начале 90-х каждая программа компилировалась под конкретную платформу. Хочешь поддержать Windows, Mac и UNIX? Компилируй три раза, поддерживай три версии, борись с тремя наборами багов.

Sun Microsystems работала над проектом для "интерактивного телевидения" — set-top boxes разных производителей. Проблема: каждый box имел свой процессор. Писать отдельный код под каждый — невозможно.

### 1995: Java и революционная идея

James Gosling и команда Sun придумали решение: промежуточный код. Компилятор производит не машинный код, а bytecode — инструкции для виртуальной машины. VM работает на реальном железе и исполняет bytecode.

```
┌─────────────────────────────────────────────────────────────────┐
│                    "WRITE ONCE, RUN ANYWHERE"                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   БЕЗ BYTECODE:                                                 │
│   Source → Windows .exe                                         │
│   Source → Mac binary                                           │
│   Source → Linux binary                                         │
│   Source → SPARC binary                                         │
│   = 4 компиляции, 4 поддержки                                   │
│                                                                 │
│   С BYTECODE:                                                   │
│   Source → Bytecode (.class)                                    │
│              ↓                                                  │
│         ┌────┴────────────────────────────┐                     │
│         ↓           ↓          ↓          ↓                     │
│     JVM Win    JVM Mac    JVM Linux   JVM SPARC                 │
│   = 1 компиляция, VM на каждой платформе                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Скептики говорили: интерпретируемый код будет медленным. Sun ответила JIT-компиляцией — VM компилирует горячие участки bytecode в native код на лету.

### Bytecode сегодня

Идея bytecode стала стандартом:
- **JVM** — Java, Kotlin, Scala, Groovy
- **CLR (.NET)** — C#, F#, VB.NET
- **WebAssembly** — Rust, C++, Kotlin (через Kotlin/Wasm)
- **Dalvik/ART** — Android приложения (DEX формат)

---

## ЧТО такое виртуальная машина

### Суть концепции

Виртуальная машина — программа, которая притворяется компьютером. У неё есть:
- Набор инструкций (opcodes)
- Память для данных
- "Регистры" или стек для вычислений
- Правила исполнения

Реальный CPU понимает машинный код (x86, ARM). VM понимает свой bytecode. VM транслирует bytecode в действия на реальном CPU.

### Стековые и регистровые VM

Два основных подхода к архитектуре:

**Stack-based (JVM, WASM):**
```
┌─────────────────────────────────────────────────────────────────┐
│                    STACK-BASED VM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Код: 2 + 3                                                    │
│                                                                 │
│   iconst_2    ; push 2 на стек           Stack: [2]             │
│   iconst_3    ; push 3 на стек           Stack: [2, 3]          │
│   iadd        ; pop 3, pop 2, push 5     Stack: [5]             │
│                                                                 │
│   Операнды НЕ указаны в инструкции — берутся со стека           │
│   + Компактный bytecode (меньше байт)                           │
│   - Больше инструкций (push/pop overhead)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Register-based (Dalvik, Lua VM):**
```
┌─────────────────────────────────────────────────────────────────┐
│                   REGISTER-BASED VM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Код: 2 + 3                                                    │
│                                                                 │
│   const v0, 2       ; положить 2 в регистр v0                   │
│   const v1, 3       ; положить 3 в регистр v1                   │
│   add v2, v0, v1    ; v2 = v0 + v1                              │
│                                                                 │
│   Операнды УКАЗАНЫ в инструкции                                 │
│   + Меньше инструкций                                           │
│   - Больший размер инструкции (адреса регистров)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Исследование 2025 года (Wiley)** показало: с JIT-компиляцией разница в производительности минимальна. Stack-based чуть быстрее для рекурсии, register-based — для общего кода.

---

## КАК работает JVM

### Жизненный цикл класса

Когда программа использует класс, JVM проходит через три этапа:

```
┌─────────────────────────────────────────────────────────────────┐
│                    JVM CLASS LIFECYCLE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. LOADING (загрузка)                                         │
│      ClassLoader находит .class файл                            │
│      Читает bytecode в память                                   │
│      Создаёт объект Class                                       │
│                                                                 │
│   2. LINKING (связывание)                                       │
│      ├── Verification: проверка bytecode на корректность        │
│      ├── Preparation: выделение памяти для static полей         │
│      └── Resolution: разрешение символьных ссылок               │
│                                                                 │
│   3. INITIALIZATION (инициализация)                             │
│      Выполнение static блоков и инициализаторов                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ClassLoader иерархия

JVM имеет три встроенных загрузчика:

**Bootstrap ClassLoader** — загружает java.lang.*, java.util.* и другие core классы. Написан на native коде, не виден из Java.

**Platform ClassLoader** — загружает расширения платформы. Раньше назывался Extension ClassLoader.

**Application ClassLoader** — загружает классы приложения из classpath.

Загрузчики работают по принципу делегирования: при запросе класса сначала спрашивают родителя. Если родитель не находит — пробуют сами.

```
                Bootstrap (java.*)
                    ↑
              Platform (extensions)
                    ↑
             Application (your code)
                    ↑
            Custom ClassLoaders
```

### Bytecode Verification

JVM не доверяет bytecode слепо. Перед исполнением проверяет:

- **Формат корректен** — magic number, version, structure
- **Типы совместимы** — нельзя сложить int и String
- **Stack не переполняется** — защита от underflow/overflow
- **Доступ легален** — private поля недоступны извне

Зачем это нужно? Bytecode может быть создан вручную, с ошибками или злым умыслом. Компилятор не генерирует плохой код, но hex-редактор — может.

```kotlin
// Компилятор не позволит
val x: Int = "hello" // ошибка компиляции

// Но можно создать bytecode вручную:
// iload_0         ; загрузить int
// areturn         ; вернуть как reference
// → JVM Verifier отклонит
```

### Исполнение bytecode

После верификации JVM исполняет код. Два режима:

**Interpretation** — читает и выполняет инструкции по одной. Медленно, но сразу готов.

**JIT Compilation** — компилирует bytecode в native код. Быстро после прогрева, но требует время на компиляцию.

Современные JVM используют tiered compilation: сначала интерпретируют, затем JIT-компилируют горячие методы.

---

## Android: Dalvik → ART

### DEX формат

Android не использует .class файлы напрямую. Toolchain конвертирует их в DEX (Dalvik Executable):

```
.java → javac → .class → dx/d8 → .dex → APK
```

DEX оптимизирован для мобильных устройств:
- Несколько .class объединяются в один .dex
- Константы дедуплицируются
- Register-based (меньше инструкций)

### Dalvik VM (2008-2014)

Первый Android runtime. Register-based VM с JIT компиляцией:

- Trace-based JIT — компилирует горячие участки кода
- Остальное интерпретирует
- Проблема: JIT при каждом запуске приложения

### ART (Android Runtime)

С Android 5.0 заменил Dalvik:

**AOT компиляция:**
При установке приложения `dex2oat` компилирует DEX в native код. Результат сохраняется в .odex файл.

**Преимущества:**
- Быстрый холодный старт (код уже скомпилирован)
- Меньше battery drain (нет JIT при работе)
- Лучшее garbage collection

**Гибрид AOT+JIT (Android 7.0+):**
ART профилирует приложение и AOT-компилирует только горячие пути. Остальное — JIT. Баланс размера и скорости.

```
┌─────────────────────────────────────────────────────────────────┐
│                    DALVIK vs ART                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   DALVIK (до Android 5.0):                                      │
│   ┌───────┐     ┌────────────┐     ┌────────────┐               │
│   │  DEX  │ ──▶ │Interpreter │ ──▶ │ JIT (hot)  │               │
│   └───────┘     └────────────┘     └────────────┘               │
│   При каждом запуске                                            │
│                                                                 │
│   ART (Android 5.0+):                                           │
│   ┌───────┐     ┌────────────┐     ┌────────────┐               │
│   │  DEX  │ ──▶ │  dex2oat   │ ──▶ │ .odex/.oat │               │
│   └───────┘     └────────────┘     └────────────┘               │
│   При установке                     Native code                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## WebAssembly (WASM)

### Зачем нужен WASM

JavaScript был единственным языком в браузере. Он хорош для UI, но медленный для вычислений. Игры, видео-редакторы, CAD — всё тормозило.

WebAssembly (2017) — низкоуровневый bytecode для браузера:
- Компактный binary формат
- Близок к машинному коду
- Sandbox security
- Портативность (работает везде)

### Архитектура WASM

Stack-based VM с linear memory:

```
┌─────────────────────────────────────────────────────────────────┐
│                    WASM АРХИТЕКТУРА                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌────────────────────────────────────────────────────┐        │
│   │                    WASM Module                      │        │
│   ├────────────────────────────────────────────────────┤        │
│   │  Functions (code)                                  │        │
│   │  Linear Memory (heap)                              │        │
│   │  Tables (function pointers)                        │        │
│   │  Globals                                           │        │
│   └────────────────────────────────────────────────────┘        │
│                            ↓                                    │
│   ┌────────────────────────────────────────────────────┐        │
│   │              WASM Runtime (браузер)                 │        │
│   │  ─────────────────────────────────────────────     │        │
│   │  Sandboxed execution                               │        │
│   │  No direct access to DOM/APIs                      │        │
│   │  Memory isolated from host                         │        │
│   └────────────────────────────────────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Security модель

WASM безопаснее JVM bytecode:
- **Memory sandbox** — WASM не может читать память браузера
- **Нет raw pointers** к host системе
- **Детерминистичное исполнение** — одинаковый результат везде
- **Формальная верификация** спецификации

### WASM 3.0 (2025)

Новая версия добавила:
- **Garbage Collection** — managed memory для языков с GC
- **64-bit memory** — до 16 экзабайт вместо 4GB
- **Tail calls** — для функциональных языков
- **Exception handling** — try/catch на уровне WASM

### Kotlin/Wasm

Kotlin может компилироваться в WASM:

```kotlin
// commonMain
expect fun platformName(): String

// wasmJsMain
actual fun platformName() = "Wasm"
```

С декабря 2024 все major браузеры поддерживают WasmGC. Compose Multiplatform работает на Kotlin/Wasm с производительностью, приближающейся к JVM.

---

## Kotlin и разные bytecode

KMP использует разные backend'ы компилятора:

| Target | Формат | VM/Runtime | Особенности |
|--------|--------|------------|-------------|
| **JVM** | .class (JVM bytecode) | JVM | Полный доступ к Java |
| **Android** | .dex | ART | Через Android toolchain |
| **Native** | Binary (через LLVM) | Нет VM | AOT, прямое исполнение |
| **JS** | .js | JS Engine | Interop с JavaScript |
| **Wasm** | .wasm | WASM Runtime | Browser sandbox |

```kotlin
// Один код
fun greet(): String = "Hello from Kotlin"

// Компилируется в:
// JVM: getGreet() → LDC "Hello from Kotlin"; ARETURN
// WASM: i32.const <string_addr>; return
// JS: function greet() { return "Hello from Kotlin"; }
```

### Как смотреть bytecode

**JVM bytecode:**
```bash
kotlinc Main.kt -include-runtime -d Main.jar
javap -c -p MainKt
```

**Kotlin IR:**
```bash
kotlinc -Xprint-ir Main.kt
```

---

## Подводные камни

### Типичные заблуждения

| Миф | Реальность |
|-----|------------|
| JVM всегда медленнее native | С JIT может быть быстрее — runtime оптимизации |
| WASM только для браузера | Standalone runtimes (Wasmtime, Wasmer) работают везде |
| Bytecode = медленно | JIT компилирует в native код |
| Register VM быстрее stack VM | С JIT разница минимальна |

### Когда понимание VM важно

**Debugging:**
- Stack trace показывает bytecode offsets
- Memory profilers работают на уровне VM

**Performance:**
- JIT warmup time — первые запуски медленнее
- Method inlining зависит от bytecode размера

**KMP специфика:**
- Разные VM = разное поведение (например, number overflow)
- Interop с native требует понимания границ VM

---

## Куда дальше

**Для глубины:**
→ [[native-compilation-llvm]] — как работает Kotlin/Native без VM
→ [[interpretation-jit]] — JIT компиляция подробнее

**Практика:**
```bash
# Посмотреть JVM bytecode
javap -c -p YourClass

# Посмотреть DEX для Android
# (в Android Studio: Build → Analyze APK)
```

---

## Источники

- [Crafting Interpreters: A Bytecode Virtual Machine](https://craftinginterpreters.com/a-bytecode-virtual-machine.html) — лучший туториал по bytecode VM
- [AOSP: Android Runtime](https://source.android.com/docs/core/runtime) — официальная документация ART
- [JetBrains: Kotlin/Wasm](https://kotlinlang.org/docs/wasm-overview.html) — Kotlin и WebAssembly
- [webassembly.org: WASM 3.0](https://webassembly.org/news/2025-09-17-wasm-3.0/) — новая версия WASM

---

*Проверено: 2026-01-09*

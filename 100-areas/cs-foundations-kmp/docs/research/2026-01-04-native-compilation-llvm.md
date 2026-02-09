# Research Report: Native Compilation and LLVM

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

LLVM — модульная инфраструктура компиляторов, созданная Chris Lattner в 2000 году. Основа: три фазы (frontend → optimizer на IR → backend), SSA-форма IR с phi-нодами, библиотечный дизайн. AOT компиляция даёт быстрый старт без runtime overhead. Kotlin/Native использует LLVM backend для генерации native кода под iOS, macOS, Linux. Компилятор Konan генерирует Kotlin IR, который конвертируется в LLVM IR и оптимизируется через LLVM passes.

## Key Findings

### 1. История LLVM

**2000:** Chris Lattner начал LLVM как research project в University of Illinois
**2002:** Защитил Master's thesis по LLVM
**2003:** Первый публичный релиз (v1.0)
**2005:** Apple начала вкладываться, наняла Lattner
**2007:** Clang (C/C++/Obj-C frontend) стал частью LLVM
**2010:** Lattner начал работу над Swift (втайне)
**2014:** Swift анонсирован на WWDC

**Почему создан:**
- GCC был монолитным и сложным для расширения
- Apple хотела лучшую поддержку Objective-C
- Нужна была модульная архитектура для переиспользования

### 2. Архитектура LLVM

**Три фазы:**
```
Frontend  →  Optimizer  →  Backend
(Clang)      (LLVM IR)    (x86, ARM, etc.)
```

**Модульный дизайн:**
- Библиотеки, не монолитная программа
- Можно использовать отдельные части
- Чёткие интерфейсы между компонентами

**Языковая независимость:**
- Frontend генерирует LLVM IR
- Optimizer работает с IR
- Backend генерирует машинный код
- M языков + N платформ = M+N компонентов

### 3. LLVM IR

**Характеристики:**
- Typed: каждое значение имеет тип
- SSA форма: каждая переменная присваивается один раз
- Три формата: text (.ll), in-memory, binary (.bc)
- Бесконечные регистры (локальные значения)

**Синтаксис:**
```llvm
; локальные значения: %name
; глобальные: @name
%result = add i32 %a, %b
call void @print(i32 %result)
```

**Phi-ноды:**
Для SSA формы при слиянии control flow:
```llvm
define i32 @max(i32 %a, i32 %b) {
entry:
  %cmp = icmp sgt i32 %a, %b
  br i1 %cmp, label %then, label %else

then:
  br label %end

else:
  br label %end

end:
  %result = phi i32 [%a, %then], [%b, %else]
  ret i32 %result
}
```

### 4. AOT vs JIT

| Аспект | AOT | JIT |
|--------|-----|-----|
| Компиляция | До запуска (build time) | При запуске (runtime) |
| Startup time | Быстрый | Медленнее (warmup) |
| Peak performance | Фиксированная | Может быть выше (runtime optimization) |
| Memory footprint | Меньше | Больше (compiler в памяти) |
| Optimizations | Static | Profile-guided возможны |
| Use case | Serverless, CLI, iOS | Long-running apps, JVM |

**AOT преимущества:**
- Мгновенный старт
- Меньше памяти
- Предсказуемое поведение
- Нет runtime compiler overhead

**JIT преимущества:**
- Profile-guided optimization
- Adaptive к реальным данным
- Может оптимизировать годы спустя под новый CPU

### 5. LLVM Optimization Passes

**Типы passes:**
- **Function passes:** работают на уровне функций (inlining)
- **Module passes:** на уровне модуля (global DCE)
- **Loop passes:** оптимизация циклов

**Ключевые оптимизации:**

| Pass | Что делает |
|------|------------|
| **Constant Folding** | `2 + 3` → `5` |
| **Dead Code Elimination** | Удаляет недостижимый код |
| **Inlining** | Подстановка тела функции |
| **LICM** | Loop-invariant code motion |
| **SROA** | Scalar Replacement of Aggregates |
| **SimplifyCFG** | Упрощение control flow |
| **GVN** | Global Value Numbering |

**ADCE (Aggressive DCE):**
Предполагает что всё мёртвое, пока не доказано обратное

**Bit-Tracking DCE:**
Отслеживает какие биты значения реально используются

### 6. Kotlin/Native и LLVM

**Компилятор Konan:**
```
.kt → Kotlin Frontend → Kotlin IR → LLVM IR → Native Binary
                         (K2/FIR)    (Konan)   (LLVM)
```

**Две последовательности passes:**
1. **ModuleBitcodeOptimization** — на уровне модуля
2. **LTOBitcodeOptimization** — link-time optimization

**Особенности:**
- Konan отключает некоторые LLVM passes (devirt — Kotlin делает сам)
- Можно кастомизировать passes для своего проекта
- klib формат распространяет Kotlin IR, не LLVM IR

**Поддерживаемые таргеты:**
- iOS (arm64, x86_64 simulator)
- macOS (arm64, x86_64)
- Linux (x64, arm64, arm32)
- Windows (mingw x64)
- watchOS, tvOS
- 27+ таргетов в Kotlin 1.8.0

### 7. Native vs VM Performance

**Native преимущества:**
- Нет VM overhead
- Меньший размер executable
- Прямой доступ к системным API
- Предсказуемая latency

**VM преимущества (JVM/ART):**
- JIT может оптимизировать лучше с runtime info
- Garbage collection более mature
- Большая экосистема

**Kotlin/Native specifics:**
- Reference counting (не tracing GC по умолчанию в старых версиях)
- С новых версий — tracing GC
- iOS interop с Swift/Objective-C

### 8. LLVM в индустрии

**Использование:**
- Apple: Clang, Swift
- Google: Android NDK, Chrome (sandbox)
- Mozilla: Rust
- Microsoft: HLSL compiler
- NVIDIA: CUDA

**Языки с LLVM backend:**
C, C++, Rust, Swift, Kotlin/Native, Julia, Crystal, Zig, D, Haskell (GHC LLVM backend)

### 9. Распространённые заблуждения

**Миф:** LLVM = Low Level Virtual Machine
**Факт:** С 2011 это не аббревиатура, просто название

**Миф:** LLVM — компилятор
**Факт:** LLVM — инфраструктура компиляторов. Clang — компилятор C/C++ на LLVM

**Миф:** Native всегда быстрее VM
**Факт:** JIT может оптимизировать лучше с runtime profiling

**Миф:** AOT даёт лучший peak performance
**Факт:** JIT с profile-guided optimization часто быстрее

### 10. Best Practices

1. **Для iOS/macOS:** Kotlin/Native = стандартный путь
2. **Для performance-critical:** проверь оба варианта (JVM vs Native)
3. **Для размера:** Native обычно меньше (нет runtime)
4. **Для startup:** Native однозначно быстрее

## Community Sentiment

### Positive
- LLVM сделал создание компиляторов доступным
- Kotlin/Native позволяет KMP на iOS без боли
- Модульная архитектура — отличный дизайн
- Документация LLVM хорошая

### Negative
- LLVM сложен для изучения
- Kotlin/Native компиляция медленнее JVM
- LLVM IR меняется между версиями
- Native debugging сложнее чем JVM

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [LLVM Official](https://llvm.org/) | Official | 0.95 | Architecture overview |
| 2 | [AOSA Book: LLVM](https://aosabook.org/en/v1/llvm.html) | Book | 0.95 | Design philosophy |
| 3 | [Wikipedia: LLVM](https://en.wikipedia.org/wiki/LLVM) | Reference | 0.9 | History |
| 4 | [Chris Lattner Resume](https://www.nondot.org/sabre/Resume.html) | Primary | 0.95 | Personal history |
| 5 | [Kotlin/Native Docs](https://kotlinlang.org/docs/native-overview.html) | Official | 0.95 | K/N overview |
| 6 | [mcyoung: LLVM IR](https://mcyoung.xyz/2023/08/01/llvm-ir/) | Blog | 0.85 | IR tutorial |
| 7 | [LLVM Passes Docs](https://llvm.org/docs/Passes.html) | Official | 0.95 | Optimization passes |
| 8 | [Bell-sw: JIT vs AOT](https://bell-sw.com/blog/compilation-in-java-jit-vs-aot/) | Blog | 0.85 | AOT/JIT comparison |
| 9 | [Wikipedia: AOT](https://en.wikipedia.org/wiki/Ahead-of-time_compilation) | Reference | 0.9 | AOT definition |
| 10 | [pragmaticengineer: Lattner](https://newsletter.pragmaticengineer.com/p/from-swift-to-mojo-and-high-performance) | Interview | 0.9 | LLVM history |

## Research Methodology
- **Queries used:** 8 search queries
- **Sources found:** 35+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** LLVM architecture, IR/SSA, optimization passes, Kotlin/Native, AOT vs JIT

---

*Проверено: 2026-01-09*

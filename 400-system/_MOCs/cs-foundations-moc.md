---
title: "CS Foundations MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/cs-foundations
  - type/moc
  - navigation
---
# CS Foundations MOC

> Фундаментальные знания Computer Science для понимания кросс-платформенной разработки: память, компиляция, конкурентность, типы, interop.

---

## Рекомендуемый путь изучения

1. **Обзор** — [[cs-foundations-overview]]
2. **Память** — [[memory-model-fundamentals]] → [[garbage-collection-explained]] → [[reference-counting-arc]] → [[memory-safety-ownership]]
3. **Компиляция** — [[compilation-pipeline]] → [[bytecode-virtual-machines]] → [[native-compilation-llvm]] → [[interpretation-jit]]
4. **Конкурентность** — [[processes-threads-fundamentals]] → [[concurrency-vs-parallelism]] → [[synchronization-primitives]] → [[async-models-overview]]
5. **Типы** — [[type-systems-fundamentals]] → [[generics-parametric-polymorphism]] → [[variance-covariance]] → [[type-erasure-reification]]
6. **Platform Interop** — [[abi-calling-conventions]] → [[ffi-foreign-function-interface]] → [[memory-layout-marshalling]] → [[bridges-bindings-overview]]
7. **Appendix** — [[cpu-architecture-basics]] → [[os-fundamentals-for-devs]]

## Статьи по категориям

### Обзор
- [[cs-foundations-overview]] — навигация по разделу и связь каждой темы с KMP

### 01 — Memory (Память)
- [[memory-model-fundamentals]] — Stack vs Heap, адресация, время жизни данных
- [[garbage-collection-explained]] — автоматическое освобождение памяти: tracing, generational GC, JVM collectors
- [[reference-counting-arc]] — ARC в Swift, retain cycles, weak/unowned ссылки, интеграция с Kotlin/Native
- [[memory-safety-ownership]] — ownership, borrowing (Rust), freeze model (K/N), Sendable/Actors (Swift)

### 02 — Compilation (Компиляция)
- [[compilation-pipeline]] — путь от текста до исполнения: lexer, parser, AST, IR, backend
- [[bytecode-virtual-machines]] — JVM, Dalvik/ART, WASM: промежуточный код и виртуальные машины
- [[native-compilation-llvm]] — AOT компиляция через LLVM, Kotlin/Native для iOS/macOS
- [[interpretation-jit]] — интерпретация, JIT, tiered compilation (HotSpot, V8), деоптимизация

### 03 — Concurrency (Конкурентность)
- [[processes-threads-fundamentals]] — процессы, потоки, context switch, kernel vs green threads
- [[concurrency-vs-parallelism]] — структура программы (concurrency) vs параллельное выполнение (parallelism)
- [[synchronization-primitives]] — mutex, semaphore, deadlock (4 условия Coffman), lock-free подходы
- [[async-models-overview]] — callbacks, promises, async/await, event loop, Kotlin coroutines и CPS

### 04 — Type Systems (Системы типов)
- [[type-systems-fundamentals]] — static vs dynamic, strong vs weak, nominal vs structural, null safety
- [[generics-parametric-polymorphism]] — параметрический полиморфизм, bounded types, PECS в Kotlin
- [[variance-covariance]] — covariance (out), contravariance (in), declaration-site vs use-site
- [[type-erasure-reification]] — стирание типов на JVM, Kotlin reified inline functions

### 05 — Platform Interop (Межплатформенное взаимодействие)
- [[abi-calling-conventions]] — ABI контракт, calling conventions (x86-64 System V, ARM64 AAPCS)
- [[ffi-foreign-function-interface]] — JNI, P/Invoke, Kotlin/Native cinterop, objc_msgSend
- [[memory-layout-marshalling]] — alignment, padding, endianness, преобразование данных между языками
- [[bridges-bindings-overview]] — автоматические обёртки: SWIG, cinterop, SKIE, Swift Export

### 06 — Appendix (Приложение)
- [[cpu-architecture-basics]] — Fetch-Decode-Execute, регистры, cache hierarchy (L1/L2/L3), branch prediction
- [[os-fundamentals-for-devs]] — kernel vs user mode, system calls, virtual memory, процессы

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| Stack vs Heap | Stack быстрый и автоматический, Heap большой но требует GC | [[memory-model-fundamentals]] |
| Garbage Collection | Автоматическое освобождение неиспользуемой памяти (tracing/RC) | [[garbage-collection-explained]] |
| ARC | Automatic Reference Counting в Swift, детерминированное освобождение | [[reference-counting-arc]] |
| JIT Compilation | Компиляция горячего кода во время выполнения программы | [[interpretation-jit]] |
| LLVM | Модульная инфраструктура компиляторов для native binary | [[native-compilation-llvm]] |
| Coroutines | Кооперативная многозадачность без overhead потоков | [[async-models-overview]] |
| Variance | Как наследование типов влияет на generic типы (out/in) | [[variance-covariance]] |
| Type Erasure | JVM стирает generic типы при компиляции, reified обходит это | [[type-erasure-reification]] |
| FFI | Механизм вызова кода одного языка из другого | [[ffi-foreign-function-interface]] |
| ABI | Бинарный контракт между скомпилированным кодом и ОС | [[abi-calling-conventions]] |

## Связанные области

- [[kmp-moc]] — Kotlin Multiplatform: практическое применение этих основ
- [[jvm-moc]] — JVM internals: bytecode, GC, class loading
- [[cs-fundamentals-moc]] — алгоритмы и структуры данных

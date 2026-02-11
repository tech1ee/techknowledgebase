---
title: "CS Foundations: путь обучения"
created: 2026-02-10
modified: 2026-02-10
type: guide
tags:
  - topic/cs-foundations
  - type/guide
  - navigation
---

# CS Foundations: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

---

## Уровень 1: Основы (Beginner)
> Цель: Получить обзор CS Foundations и понять связь с кросс-платформенной разработкой
> Время: ~1 неделя

1. [[cs-foundations-overview]] — навигация по разделу и связь каждой темы с KMP

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить фундаментальные концепции: память, компиляция, конкурентность, системы типов и hardware
> Время: ~6 недель
> Prerequisites: Level 1

### Память
2. [[memory-model-fundamentals]] — Stack vs Heap, адресация, время жизни данных
3. [[garbage-collection-explained]] — автоматическое освобождение памяти: tracing, generational GC
4. [[reference-counting-arc]] — ARC в Swift, retain cycles, weak/unowned ссылки

### Компиляция
5. [[compilation-pipeline]] — путь от текста до исполнения: lexer, parser, AST, IR, backend
6. [[bytecode-virtual-machines]] — JVM, Dalvik/ART, WASM: промежуточный код и виртуальные машины

### Конкурентность
7. [[processes-threads-fundamentals]] — процессы, потоки, context switch, kernel vs green threads
8. [[concurrency-vs-parallelism]] — структура программы vs параллельное выполнение
9. [[async-models-overview]] — callbacks, promises, async/await, event loop, coroutines

### Системы типов
10. [[type-systems-fundamentals]] — static vs dynamic, strong vs weak, nominal vs structural
11. [[generics-parametric-polymorphism]] — параметрический полиморфизм, bounded types, PECS

### Appendix (Hardware и OS)
12. [[cpu-architecture-basics]] — Fetch-Decode-Execute, регистры, cache hierarchy
13. [[os-fundamentals-for-devs]] — kernel vs user mode, system calls, virtual memory

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Освоить продвинутые темы: memory safety, JIT, синхронизация, variance, FFI, interop
> Время: ~4 недели
> Prerequisites: Level 2

### Память (Advanced)
14. [[memory-safety-ownership]] — ownership, borrowing (Rust), freeze model (K/N), Sendable/Actors

### Компиляция (Advanced)
15. [[native-compilation-llvm]] — AOT компиляция через LLVM, Kotlin/Native для iOS/macOS
16. [[interpretation-jit]] — интерпретация, JIT, tiered compilation, деоптимизация

### Конкурентность (Advanced)
17. [[synchronization-primitives]] — mutex, semaphore, deadlock (4 условия Coffman), lock-free

### Системы типов (Advanced)
18. [[variance-covariance]] — covariance (out), contravariance (in), declaration-site vs use-site
19. [[type-erasure-reification]] — стирание типов на JVM, Kotlin reified inline functions

### Platform Interop
20. [[ffi-foreign-function-interface]] — JNI, P/Invoke, Kotlin/Native cinterop, objc_msgSend
21. [[memory-layout-marshalling]] — alignment, padding, endianness, marshalling между языками
22. [[bridges-bindings-overview]] — SWIG, cinterop, SKIE, Swift Export: автоматические обёртки

---

## Уровень 4: Экспертиза (Expert)
> Цель: Понять низкоуровневые механизмы бинарного взаимодействия между платформами
> Время: ~1 неделя
> Prerequisites: Level 3

23. [[abi-calling-conventions]] — ABI контракт, calling conventions (x86-64 System V, ARM64 AAPCS)

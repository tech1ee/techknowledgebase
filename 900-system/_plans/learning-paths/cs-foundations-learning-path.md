---
title: "CS Foundations: путь обучения"
created: 2026-02-10
modified: 2026-02-14
type: guide
tags:
  - topic/cs-foundations
  - type/guide
  - navigation
  - learning-path
---

# CS Foundations: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

**Рекомендуемый темп:** 1-2 файла в день (~45-60 минут). Каждый 5-й день — повторение изученного.

**Общее время:** ~469 минут (~7.8 часов)

---

## Уровень 1: Основы (Beginner)
> Цель: Получить обзор CS Foundations и понять связь с кросс-платформенной разработкой
> Время: ~6 минут

- [ ] [[cs-foundations-overview]] — навигация по разделу и связь каждой темы с KMP ⏱ 6m

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить фундаментальные концепции: память, компиляция, конкурентность, системы типов и hardware
> Время: ~260 минут (~4.3 часа)
> Prerequisites: Level 1

### Память
- [ ] [[memory-model-fundamentals]] — Stack vs Heap, адресация, время жизни данных ⏱ 23m
- [ ] [[garbage-collection-explained]] — автоматическое освобождение памяти: tracing, generational GC ⏱ 26m
- [ ] [[reference-counting-arc]] — ARC в Swift, retain cycles, weak/unowned ссылки ⏱ 21m

📝 День повторения

### Компиляция
- [ ] [[compilation-pipeline]] — путь от текста до исполнения: lexer, parser, AST, IR, backend ⏱ 33m
- [ ] [[bytecode-virtual-machines]] — JVM, Dalvik/ART, WASM: промежуточный код и виртуальные машины ⏱ 20m

📝 День повторения

### Конкурентность
- [ ] [[processes-threads-fundamentals]] — процессы, потоки, context switch, kernel vs green threads ⏱ 20m
- [ ] [[concurrency-vs-parallelism]] — структура программы vs параллельное выполнение ⏱ 24m
- [ ] [[async-models-overview]] — callbacks, promises, async/await, event loop, coroutines ⏱ 23m

📝 День повторения

### Системы типов
- [ ] [[type-systems-fundamentals]] — static vs dynamic, strong vs weak, nominal vs structural ⏱ 16m
- [ ] [[generics-parametric-polymorphism]] — параметрический полиморфизм, bounded types, PECS ⏱ 15m

> [!tip] CPU Architecture и OS Fundamentals — полезный бэкграунд. Если уже изучал OS, можно пропустить.

### Appendix (Hardware и OS)
- [ ] [[cpu-architecture-basics]] — Fetch-Decode-Execute, регистры, cache hierarchy ⏱ 19m
- [ ] [[os-fundamentals-for-devs]] — kernel vs user mode, system calls, virtual memory ⏱ 20m

📝 День повторения

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Освоить продвинутые темы: memory safety, JIT, синхронизация, variance, FFI, interop
> Время: ~175 минут (~2.9 часа)
> Prerequisites: Level 2

> [!tip] Ownership и Rust — полезно для понимания Kotlin/Native. Если работаешь только с JVM, можно изучить обзорно.

### Память (Advanced)
- [ ] [[memory-safety-ownership]] — ownership, borrowing (Rust), freeze model (K/N), Sendable/Actors ⏱ 20m

### Компиляция (Advanced)
- [ ] [[native-compilation-llvm]] — AOT компиляция через LLVM, Kotlin/Native для iOS/macOS ⏱ 16m
- [ ] [[interpretation-jit]] — интерпретация, JIT, tiered compilation, деоптимизация ⏱ 21m

📝 День повторения

### Конкурентность (Advanced)
- [ ] [[synchronization-primitives]] — mutex, semaphore, deadlock (4 условия Coffman), lock-free ⏱ 24m

### Системы типов (Advanced)
- [ ] [[variance-covariance]] — covariance (out), contravariance (in), declaration-site vs use-site ⏱ 15m
- [ ] [[type-erasure-reification]] — стирание типов на JVM, Kotlin reified inline functions ⏱ 15m

📝 День повторения

> [!tip] FFI и Memory Layout — для тех кто пишет KMP native interop. Если shared code only, можно пропустить.

### Platform Interop
- [ ] [[ffi-foreign-function-interface]] — JNI, P/Invoke, Kotlin/Native cinterop, objc_msgSend ⏱ 25m
- [ ] [[memory-layout-marshalling]] — alignment, padding, endianness, marshalling между языками ⏱ 20m
- [ ] [[bridges-bindings-overview]] — SWIG, cinterop, SKIE, Swift Export: автоматические обёртки ⏱ 19m

📝 День повторения

---

## Уровень 4: Экспертиза (Expert)
> Цель: Понять низкоуровневые механизмы бинарного взаимодействия между платформами
> Время: ~28 минут
> Prerequisites: Level 3

> [!tip] ABI и Calling Conventions — самый низкоуровневый материал. Читай если хочешь понять как Kotlin/Native вызывает C код.

- [ ] [[abi-calling-conventions]] — ABI контракт, calling conventions (x86-64 System V, ARM64 AAPCS) ⏱ 28m

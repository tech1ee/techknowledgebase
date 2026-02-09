---
title: "CS Foundations для KMP: Компьютерные основы для понимания кросс-платформенной разработки"
created: 2026-01-04
modified: 2026-01-04
tags: [cs-foundations, kmp, index, memory, compilation, concurrency]
related:
  - "[[00-kmp-overview]]"
---

# CS Foundations для KMP

> **TL;DR:** Фундаментальные знания Computer Science, без которых KMP — чёрный ящик. Память, компиляция, конкурентность, типы, interop. После этого раздела код KMP перестанет быть магией.

---

## Зачем этот раздел

KMP компилирует один код в:
- JVM bytecode (Android)
- Native binary через LLVM (iOS)
- JavaScript/Wasm (Web)

Без понимания *как* это работает, ты будешь:
- Не понимать ошибки памяти на iOS
- Удивляться разнице поведения на JVM и Native
- Копировать код без понимания

Этот раздел — фундамент. После него KMP-материалы станут понятны на глубинном уровне.

---

## Навигация по разделу

### 01-memory — Память

| Материал | Описание | Зачем для KMP |
|----------|----------|---------------|
| [[memory-model-fundamentals]] | Stack vs Heap, адресация | Основа всего |
| [[garbage-collection-explained]] | Все виды GC | JVM GC, K/N GC |
| [[reference-counting-arc]] | ARC, retain cycles | iOS interop |
| [[memory-safety-ownership]] | Ownership, borrowing | K/N freeze model |

### 02-compilation — Компиляция

| Материал | Описание | Зачем для KMP |
|----------|----------|---------------|
| [[compilation-pipeline]] | От кода до исполнения | Понимание targets |
| [[bytecode-virtual-machines]] | JVM, WASM | Android, Web |
| [[native-compilation-llvm]] | AOT, LLVM | iOS, Native |
| [[interpretation-jit]] | JIT, tiered compilation | JVM performance |

### 03-concurrency — Конкурентность

| Материал | Описание | Зачем для KMP |
|----------|----------|---------------|
| [[processes-threads-fundamentals]] | Процессы, потоки | Основа для coroutines |
| [[concurrency-vs-parallelism]] | Разница | Правильные решения |
| [[synchronization-primitives]] | Mutex, semaphore | Thread safety |
| [[async-models-overview]] | Event loop, coroutines | Kotlin coroutines |

### 04-type-systems — Системы типов

| Материал | Описание | Зачем для KMP |
|----------|----------|---------------|
| [[type-systems-fundamentals]] | Static vs dynamic | Kotlin type system |
| [[generics-parametric-polymorphism]] | Generics | Kotlin generics |
| [[variance-covariance]] | In/out, wildcards | Collections API |
| [[type-erasure-reification]] | JVM erasure, reified | inline reified |

### 05-platform-interop — Interop

| Материал | Описание | Зачем для KMP |
|----------|----------|---------------|
| [[abi-calling-conventions]] | ABI, conventions | cinterop |
| [[ffi-foreign-function-interface]] | JNI, ObjC runtime | Platform calls |
| [[memory-layout-marshalling]] | Struct layout, padding | Native interop |
| [[bridges-bindings-overview]] | cinterop, Swift Export | iOS integration |

### 06-appendix — Приложения

| Материал | Описание |
|----------|----------|
| [[cpu-architecture-basics]] | Registers, cache |
| [[os-fundamentals-for-devs]] | Syscalls, processes |

---

## Порядок изучения

```
НОВИЧОК (с нуля):
1. memory-model-fundamentals     ← начни здесь
2. garbage-collection-explained
3. reference-counting-arc
4. processes-threads-fundamentals
5. → переходи к KMP материалам

СРЕДНИЙ УРОВЕНЬ (знаешь Java/Kotlin):
1. reference-counting-arc        ← iOS-специфика
2. native-compilation-llvm       ← понимание K/N
3. async-models-overview
4. → переходи к KMP материалам

ПРОДВИНУТЫЙ (хочешь глубже):
1. Всё по порядку
2. platform-interop секция
3. appendix для полноты
```

---

## Связь с KMP

```
CS FOUNDATIONS              →    KMP МАТЕРИАЛЫ
────────────────────────────────────────────────
memory-model                →    kmp-memory-management
garbage-collection          →    kmp-memory-management
reference-counting-arc      →    kmp-ios-deep-dive
compilation-pipeline        →    kmp-project-structure
native-compilation-llvm     →    kmp-ios-deep-dive
processes-threads           →    kmp-state-management
async-models                →    kotlin-coroutines
type-systems                →    kmp-expect-actual
variance-covariance         →    kotlin-generics
abi-calling-conventions     →    kmp-interop-deep-dive
ffi                         →    kmp-interop-deep-dive
```

---

## Статус материалов

- [x] 01-memory (4/4) ✅ memory-model-fundamentals, ✅ garbage-collection-explained, ✅ reference-counting-arc, ✅ memory-safety-ownership
- [x] 02-compilation (4/4) ✅ compilation-pipeline, ✅ bytecode-virtual-machines, ✅ native-compilation-llvm, ✅ interpretation-jit
- [x] 03-concurrency (4/4) ✅ processes-threads-fundamentals, ✅ concurrency-vs-parallelism, ✅ synchronization-primitives, ✅ async-models-overview
- [x] 04-type-systems (4/4) ✅ type-systems-fundamentals, ✅ generics-parametric-polymorphism, ✅ variance-covariance, ✅ type-erasure-reification
- [x] 05-platform-interop (4/4) ✅ abi-calling-conventions, ✅ ffi-foreign-function-interface, ✅ memory-layout-marshalling, ✅ bridges-bindings-overview
- [x] 06-appendix (2/2) ✅ cpu-architecture-basics, ✅ os-fundamentals-for-devs

**Всего:** 22/22 материалов (100%) 🎉

---

*Создано: 2026-01-04*

---

*Проверено: 2026-01-09*

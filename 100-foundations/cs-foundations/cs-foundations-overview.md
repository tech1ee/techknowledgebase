---
title: "CS Foundations для KMP: Компьютерные основы для понимания кросс-платформенной разработки"
created: 2026-01-04
modified: 2026-02-13
type: overview
reading_time: 6
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/cs-foundations
  - type/overview
  - level/intermediate
related:
  - "[[kmp-overview]]"
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

## Проверь себя

> [!question]- Почему KMP компилирует один код в разные целевые форматы, а не использует единую виртуальную машину?
> Потому что каждая платформа (JVM, iOS, Web) имеет свою среду выполнения. Android работает на JVM/ART, iOS использует нативный код (ARM), а Web — JavaScript или WASM. Единая VM потребовала бы установки на все платформы, что невозможно для iOS и Web. Компиляция под каждую платформу позволяет использовать нативную производительность и интеграцию с платформенными API.

> [!question]- Ты замечаешь, что один и тот же Kotlin-код ведёт себя по-разному на Android и iOS. Какие фундаментальные различия могут это объяснять?
> Различия на уровне CS Foundations: (1) Управление памятью — JVM использует GC с поколениями, а Kotlin/Native использует свой GC (ранее ARC-подобный, сейчас tracing GC). (2) Конкурентность — на JVM полная многопоточность, на Native исторически были ограничения (freeze model). (3) Система типов — type erasure на JVM, сохранение типов на Native. (4) FFI — JNI на Android, Objective-C interop на iOS.

> [!question]- В каком порядке ты бы изучал разделы CS Foundations, если уже знаешь Java и хочешь разобраться в KMP для iOS?
> Оптимальный путь: (1) reference-counting-arc — понять ARC и retain cycles, специфику iOS. (2) native-compilation-llvm — как Kotlin/Native компилируется через LLVM. (3) memory-safety-ownership — модель freeze и актуальные подходы K/N. (4) ffi-foreign-function-interface — как K/N взаимодействует с Objective-C. (5) bridges-bindings-overview — cinterop и SKIE для Swift. Память и interop — ключевые боли при переходе с JVM на iOS.

---

## Ключевые карточки

Что компилирует KMP для Android?
?
JVM bytecode, который выполняется на ART (Android Runtime). Используется тот же формат, что и для обычного Kotlin/Java кода.

---

Что компилирует KMP для iOS?
?
Native binary через LLVM (AOT-компиляция). Kotlin/Native генерирует ARM-код, который выполняется напрямую процессором без виртуальной машины.

---

Какие 6 тематических разделов входят в CS Foundations для KMP?
?
01-memory (память), 02-compilation (компиляция), 03-concurrency (конкурентность), 04-type-systems (системы типов), 05-platform-interop (interop), 06-appendix (CPU и ОС).

---

Почему понимание GC и ARC критично для KMP?
?
Android (JVM) использует GC с поколениями, iOS использовала ARC (сейчас K/N tracing GC). Различия в управлении памятью вызывают разное поведение одного кода: retain cycles на iOS, разные паттерны освобождения ресурсов.

---

Какой раздел CS Foundations объясняет, почему cinterop генерирует разные бинарники для iosArm64 и iosX64?
?
05-platform-interop, конкретно abi-calling-conventions. Разные ABI (ARM64 AAPCS vs x86-64 System V) определяют разные конвенции передачи аргументов и возврата значений.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[memory-model-fundamentals]] | Начать изучение с фундамента — модели памяти |
| Углубиться | [[compilation-pipeline]] | Понять, как код превращается в исполняемый файл |
| Смежная тема | [[kmp-overview]] | Перейти к практике Kotlin Multiplatform |
| Обзор | [[cs-foundations-overview]] | Вы здесь |

---

*Проверено: 2026-02-13*

---
title: "Programming MOC"
created: 2025-11-24
modified: 2025-11-25
type: moc
tags:
  - topic/programming
  - type/moc
  - navigation
---

# Programming MOC

> Чистый код, паттерны, принципы разработки, JVM платформа

---

## Статьи

### Принципы и практики
- [[design-patterns]] — Factory, Strategy, Observer и когда их применять
- [[clean-code-solid]] — Читаемый код и 5 принципов гибкой архитектуры

### Тестирование
- [[testing-strategies]] — Пирамида тестов, TDD, unit vs integration vs E2E

### JVM Platform

**Основы:**
- [[jvm-basics-history]] — История Java, архитектура JVM, обзор компонентов
- [[jvm-virtual-machine-concept]] — Виртуальная машина, байткод, WORA, .class файлы
- [[jvm-class-loader-deep-dive]] — Loading, Linking, Initialization, Parent Delegation
- [[jvm-jit-compiler]] — Interpreter, JIT, Tiered Compilation

**Memory & Performance:**
- [[jvm-memory-model]] — Heap, Stack, Garbage Collection, Memory Leaks
- [[jvm-performance-overview]] — Профилирование, GC tuning, JMH benchmarking
- [[jvm-production-debugging]] — JFR, thread dumps, production troubleshooting

**Advanced JVM:**
- [[jvm-reflection-api]] — Reflection, Dynamic Proxies, introspection
- [[jvm-module-system]] — JPMS, modules, migration с classpath
- [[jvm-annotations-processing]] — Annotations, APT, Lombok, MapStruct
- [[jvm-instrumentation-agents]] — Java Agents, bytecode instrumentation, APM
- [[jvm-bytecode-manipulation]] — ASM, Javassist, ByteBuddy
- [[jvm-security-model]] — Security Manager, permissions, sandboxing
- [[jvm-jni-deep-dive]] — JNI, native integration, Panama Project
- [[jvm-service-loader-spi]] — ServiceLoader, SPI pattern, plugin systems

**Languages & Features:**
- [[jvm-languages-ecosystem]] — Kotlin, Scala, Clojure, Groovy на JVM
- [[java-modern-features]] — Java 8-21: Lambdas, Streams, Records, Virtual Threads
- [[jvm-concurrency-overview]] — Java Memory Model, synchronized, CompletableFuture

**Kotlin (12 файлов):**
- [[kotlin-basics]] — Синтаксис, типы, null-safety
- [[kotlin-oop]] — Classes, data/sealed/value classes
- [[kotlin-collections]] — Collections API, sequences
- [[kotlin-functional]] — Lambdas, scope functions
- [[kotlin-coroutines]] — Async, structured concurrency
- [[kotlin-flow]] — Reactive streams
- [[kotlin-advanced-features]] — Extensions, delegates, DSL
- [[kotlin-type-system]] — Generics, variance, contracts
- [[kmp-overview|kotlin-multiplatform]] — KMP, expect/actual
- [[kotlin-interop]] — Java interop
- [[kotlin-testing]] — Testing patterns
- [[kotlin-best-practices]] — Coding conventions
- **→ [[kotlin-moc]] — Полная карта обучения Kotlin**

---

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| Single Responsibility | Один класс — одна причина для изменения | [[clean-code-solid]] |
| Open/Closed | Открыт для расширения, закрыт для изменения | [[clean-code-solid]] |
| Factory Pattern | Создание объектов без привязки к конкретным классам | [[design-patterns]] |
| Strategy Pattern | Взаимозаменяемые алгоритмы | [[design-patterns]] |
| Observer Pattern | Реакция на события без связанности | [[design-patterns]] |
| Dependency Injection | Зависимости передаются извне | [[clean-code-solid]] |
| Test Pyramid | Unit > Integration > E2E | [[testing-strategies]] |
| TDD | Red → Green → Refactor | [[testing-strategies]] |
| AAA Pattern | Arrange, Act, Assert | [[testing-strategies]] |
| Mocking | Изоляция зависимостей в тестах | [[testing-strategies]] |
| Virtual Machine (Process VM) | Эмулирует абстрактный процессор для байткода | [[jvm-virtual-machine-concept]] |
| Platform Independence | Write Once, Run Anywhere через байткод | [[jvm-virtual-machine-concept]] |
| JVM Bytecode | Платформонезависимый промежуточный формат | [[jvm-virtual-machine-concept]] |
| .class File Format | CA FE BA BE magic number, constant pool, bytecode | [[jvm-virtual-machine-concept]] |
| Class Loading | Loading → Linking → Initialization | [[jvm-class-loader-deep-dive]] |
| Parent Delegation Model | Родитель загружает класс до потомка (безопасность) | [[jvm-class-loader-deep-dive]] |
| Bootstrap ClassLoader | C++ loader для java.lang.*, возвращает null | [[jvm-class-loader-deep-dive]] |
| Stack Frame | Local variables, operand stack, return address | [[jvm-memory-model]] |
| StackOverflowError | Stack переполнен (бесконечная рекурсия) | [[jvm-memory-model]] |
| Metaspace (Java 8+) | Class metadata вне Heap, динамический размер | [[jvm-memory-model]] |
| Interpreter | Выполняет байткод построчно (медленно, instant start) | [[jvm-jit-compiler]] |
| JIT Compiler | Компилирует горячий код в native machine code | [[jvm-jit-compiler]] |
| Tiered Compilation | Level 0 (Interpreter) → Level 3 (C1) → Level 4 (C2) | [[jvm-jit-compiler]] |
| C1 vs C2 Compiler | C1: быстрая компиляция, C2: агрессивные оптимизации | [[jvm-jit-compiler]] |
| Warmup Time | JIT требует времени для оптимизации (10-60s) | [[jvm-jit-compiler]] |
| Code Cache | Хранит скомпилированный native код (~240MB) | [[jvm-jit-compiler]] |
| Heap vs Stack | Heap: объекты, Stack: локальные переменные | [[jvm-memory-model]] |
| Generational GC | Young Gen (частые GC) + Old Gen (редкие GC) | [[jvm-memory-model]] |
| Minor vs Major GC | Minor GC (10ms) vs Major GC (500ms+) | [[jvm-memory-model]] |
| Memory Leak (JVM) | Объект достижим для GC, но не используется | [[jvm-memory-model]] |
| G1 GC | Default GC, balanced latency/throughput | [[jvm-performance-overview]] |
| ZGC | Ultra-low latency GC (<10ms паузы) | [[jvm-performance-overview]] |
| async-profiler | Low-overhead CPU/memory profiling | [[jvm-performance-overview]] |
| JMH | Java Microbenchmark Harness для бенчмарков | [[jvm-performance-overview]] |
| Kotlin Null-Safety | Compile-time защита от NullPointerException | [[jvm-languages-ecosystem]] |
| Scala Pattern Matching | Functional декомпозиция данных | [[jvm-languages-ecosystem]] |
| Clojure Immutability | Все структуры immutable по умолчанию | [[jvm-languages-ecosystem]] |
| GraalVM Native Image | AOT compilation для instant start | [[jvm-languages-ecosystem]] |
| Java Lambdas | Functional programming в Java 8+ | [[java-modern-features]] |
| Streams API | Declarative data processing | [[java-modern-features]] |
| Optional | Явный null handling | [[java-modern-features]] |
| Records (Java 16) | Immutable data classes в 1 строку | [[java-modern-features]] |
| Virtual Threads | Миллионы lightweight threads (Java 21) | [[java-modern-features]] |
| Pattern Matching | Deconstruction данных (Java 17-21) | [[java-modern-features]] |
| Java Memory Model | happens-before, visibility guarantees | [[jvm-concurrency-overview]] |
| synchronized | Monitor lock для mutual exclusion | [[jvm-concurrency-overview]] |
| volatile | Visibility guarantee без atomicity | [[jvm-concurrency-overview]] |
| ConcurrentHashMap | Thread-safe HashMap с lock striping | [[jvm-concurrency-overview]] |
| CompletableFuture | Async composition и chaining | [[jvm-concurrency-overview]] |
| ExecutorService | Thread pools вместо raw threads | [[jvm-concurrency-overview]] |
| JFR (Flight Recorder) | Low-overhead profiling в production | [[jvm-production-debugging]] |
| Thread Dumps | Snapshot thread states для deadlock анализа | [[jvm-production-debugging]] |
| Heap Dumps | Memory snapshot для leak analysis | [[jvm-production-debugging]] |
| Kotlin Null Safety | Compile-time защита от NPE через систему типов | [[kotlin-basics]] |
| Data Classes | Автогенерация equals/hashCode/toString/copy | [[kotlin-oop]] |
| Sealed Classes | Закрытые иерархии для exhaustive when | [[kotlin-oop]] |
| Extension Functions | Добавление методов к существующим типам | [[kotlin-advanced-features]] |
| Coroutines | Structured concurrency без callback hell | [[kotlin-coroutines]] |
| Flow | Reactive streams для асинхронных данных | [[kotlin-flow]] |
| Scope Functions | let/apply/run/also/with для контекста | [[kotlin-functional]] |
| Delegates | lazy, observable, custom delegation | [[kotlin-advanced-features]] |
| Reified Generics | Доступ к типам в runtime через inline | [[kotlin-type-system]] |
| KMP | Kotlin Multiplatform для кросс-платформенного кода | [[kmp-overview|kotlin-multiplatform]] |

---

## Связанные темы

- [[technical-debt]] — Последствия плохого кода
- [[microservices-vs-monolith]] — Архитектура систем
- [[api-design]] — Проектирование API
- [[performance-optimization]] — Производительность приложений

---

## Планируется

- Functional Programming basics
- Concurrency patterns
- Refactoring techniques

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 35 (23 JVM + 12 Kotlin) |
| Последнее обновление | 2025-11-25 |

---

*Последнее обновление: 2025-11-25*

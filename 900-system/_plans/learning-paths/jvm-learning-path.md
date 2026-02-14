---
title: "JVM: путь обучения"
created: 2026-02-10
modified: 2026-02-14
type: guide
tags:
  - topic/jvm
  - type/guide
  - navigation
  - learning-path
---

# JVM: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

## Рекомендуемый темп

2-3 файла в день (~60-90 минут). Каждый 5-й день — повторение изученного.

---

## Уровень 1: Основы (Beginner)
> Цель: Понять концепцию JVM, историю, ClassLoader и базовые механизмы работы виртуальной машины
> Время: ~2 недели | Чтение: 116 мин

- [ ] [[jvm-overview]] — карта раздела JVM, быстрая навигация по темам ⏱ 5m
- [ ] [[jvm-basics-history]] — история JVM, Write Once Run Anywhere, обзор архитектуры ⏱ 20m
- [ ] [[jvm-virtual-machine-concept]] — концепция виртуальной машины: абстрактный процессор, байткод ⏱ 18m
- [ ] [[jvm-class-loader-deep-dive]] — ClassLoader: Bootstrap/Platform/Application, parent delegation ⏱ 24m
- [ ] [[jvm-jit-compiler]] — JIT: tiered compilation (Interpreter -> C1 -> C2), inlining ⏱ 25m
- 📝 День повторения
- [ ] [[jvm-performance-overview]] — карта оптимизации: измерить -> понять -> исправить -> проверить ⏱ 12m
- [ ] [[jvm-concurrency-overview]] — карта многопоточности: JMM, volatile, synchronized ⏱ 12m

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить memory model, GC, concurrency, Kotlin и Java modern features
> Время: ~5 недель | Чтение: 527 мин
> Prerequisites: Level 1

### Memory и GC
- [ ] [[jvm-memory-model]] — Heap, Stack, Metaspace, Java Memory Model (JMM), happens-before ⏱ 38m
- [ ] [[jvm-gc-tuning]] — G1 (default), ZGC (<10ms паузы), Parallel, настройка ⏱ 27m

### Concurrency
- [ ] [[jvm-synchronization]] — synchronized, volatile, Atomic*, ReentrantLock, LongAdder ⏱ 26m
- [ ] [[jvm-concurrent-collections]] — ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue ⏱ 17m
- [ ] [[jvm-executors-futures]] — ExecutorService, CompletableFuture, Virtual Threads (Java 21) ⏱ 22m
- 📝 День повторения

### Languages
- [ ] [[jvm-languages-ecosystem]] — языки на JVM: Kotlin, Scala, Clojure, Groovy ⏱ 22m

> [!tip] Если работаешь только с Kotlin, Java Modern Features можно изучить обзорно.

- [ ] [[java-modern-features]] — Java 8-21: lambdas, streams, records, sealed classes, Virtual Threads ⏱ 44m

> [!tip] Если уже знаешь Kotlin, пропусти basics/oop/functional и начни с coroutines.

### Kotlin
- [ ] [[kotlin-overview]] — Kotlin: null safety, coroutines, extension functions, KMP ⏱ 5m
- [ ] [[kotlin-basics]] — основы языка: null safety, data class, when ⏱ 25m
- [ ] [[kotlin-oop]] — ООП: data class, sealed class, value class, delegation ⏱ 20m
- 📝 День повторения
- [ ] [[kotlin-functional]] — ФП: лямбды, scope functions, inline, reified ⏱ 25m
- [ ] [[kotlin-collections]] — Collections API: List, Set, Map, Sequences ⏱ 26m
- [ ] [[kotlin-type-system]] — Generics, Variance, Reified Types ⏱ 27m
- [ ] [[kotlin-coroutines]] — Coroutines: suspend, CoroutineScope, Dispatchers ⏱ 29m
- [ ] [[kotlin-flow]] — Flow: StateFlow, SharedFlow, reactive streams ⏱ 26m
- [ ] [[kotlin-channels]] — Channels: межкорутинная коммуникация, fan-out/fan-in ⏱ 35m
- 📝 День повторения
- [ ] [[kotlin-interop]] — Kotlin-Java Interoperability: @JvmStatic, @JvmOverloads ⏱ 26m
- [ ] [[kotlin-best-practices]] — идиоматичный Kotlin и оптимизация ⏱ 24m
- [ ] [[kotlin-testing]] — JUnit, MockK, Kotest, Coroutines Testing ⏱ 22m

### Diagnostics
- [ ] [[jvm-profiling]] — async-profiler: CPU, alloc, lock профилирование; flame graphs ⏱ 23m
- [ ] [[jvm-benchmarking-jmh]] — JMH: warmup, Blackhole, Fork, статистически корректные бенчмарки ⏱ 14m
- 📝 День повторения
- [ ] [[jvm-production-debugging]] — thread dump, heap dump, JFR: диагностика без downtime ⏱ 19m

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Освоить advanced Kotlin, Reflection, Annotation Processing и продвинутые JVM механизмы
> Время: ~3 недели | Чтение: 236 мин
> Prerequisites: Level 2

- [ ] [[kotlin-coroutines-internals]] — CPS, Continuation, state machine: как корутины работают внутри ⏱ 45m
- [ ] [[kotlin-advanced-features]] — Extension Functions, Delegates, DSL, operator overloading ⏱ 31m
- [ ] [[jvm-reflection-api]] — Reflection API: интроспекция классов, dynamic proxy, Method Handles ⏱ 29m
- [ ] [[jvm-annotations-processing]] — аннотации и APT: compile-time метапрограммирование ⏱ 35m

> [!tip] Bytecode manipulation и Agents — advanced темы для инструментов и фреймворков. Пропусти если не пишешь tooling.

- [ ] [[jvm-bytecode-manipulation]] — ASM, Javassist, ByteBuddy: runtime модификация байткода ⏱ 21m
- [ ] [[jvm-instrumentation-agents]] — Java агенты: premain/agentmain, ClassFileTransformer ⏱ 22m
- 📝 День повторения

> [!tip] Module system актуален для server-side Java. Для Android/KMP можно пропустить.

- [ ] [[jvm-module-system]] — JPMS (Java 9): module-info.java, requires/exports ⏱ 38m
- [ ] [[jvm-service-loader-spi]] — ServiceLoader и SPI: plugin-архитектура, JDBC ⏱ 22m
- [ ] [[jvm-jni-deep-dive]] — JNI: вызов C/C++ из Java, управление памятью ⏱ 20m
- [ ] [[jvm-security-model]] — SecurityManager (deprecated), современные альтернативы ⏱ 18m
- 📝 День повторения

---

## Итого

| Уровень | Файлов | Чтение | Период |
|---------|--------|--------|--------|
| 1. Основы | 7 | 116 мин | ~2 недели |
| 2. Рабочие навыки | 21 | 527 мин | ~5 недель |
| 3. Глубокие знания | 9 | 236 мин | ~3 недели |
| **Всего** | **37** | **879 мин (~14.5 ч)** | **~10 недель** |

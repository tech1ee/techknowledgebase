---
title: "JVM: путь обучения"
created: 2026-02-10
modified: 2026-02-10
type: guide
tags:
  - topic/jvm
  - type/guide
  - navigation
---

# JVM: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

---

## Уровень 1: Основы (Beginner)
> Цель: Понять концепцию JVM, историю, ClassLoader и базовые механизмы работы виртуальной машины
> Время: ~2 недели

1. [[jvm-overview]] — карта раздела JVM, быстрая навигация по темам
2. [[jvm-basics-history]] — история JVM, Write Once Run Anywhere, обзор архитектуры
3. [[jvm-virtual-machine-concept]] — концепция виртуальной машины: абстрактный процессор, байткод
4. [[jvm-class-loader-deep-dive]] — ClassLoader: Bootstrap/Platform/Application, parent delegation
5. [[jvm-jit-compiler]] — JIT: tiered compilation (Interpreter -> C1 -> C2), inlining
6. [[jvm-performance-overview]] — карта оптимизации: измерить -> понять -> исправить -> проверить
7. [[jvm-concurrency-overview]] — карта многопоточности: JMM, volatile, synchronized

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить memory model, GC, concurrency, Kotlin и Java modern features
> Время: ~5 недель
> Prerequisites: Level 1

### Memory и GC
8. [[jvm-memory-model]] — Heap, Stack, Metaspace, Java Memory Model (JMM), happens-before
9. [[jvm-gc-tuning]] — G1 (default), ZGC (<10ms паузы), Parallel, настройка

### Concurrency
10. [[jvm-synchronization]] — synchronized, volatile, Atomic*, ReentrantLock, LongAdder
11. [[jvm-concurrent-collections]] — ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue
12. [[jvm-executors-futures]] — ExecutorService, CompletableFuture, Virtual Threads (Java 21)

### Languages
13. [[jvm-languages-ecosystem]] — языки на JVM: Kotlin, Scala, Clojure, Groovy
14. [[java-modern-features]] — Java 8-21: lambdas, streams, records, sealed classes, Virtual Threads

### Kotlin
15. [[kotlin-overview]] — Kotlin: null safety, coroutines, extension functions, KMP
16. [[kotlin-basics]] — основы языка: null safety, data class, when
17. [[kotlin-oop]] — ООП: data class, sealed class, value class, delegation
18. [[kotlin-functional]] — ФП: лямбды, scope functions, inline, reified
19. [[kotlin-collections]] — Collections API: List, Set, Map, Sequences
20. [[kotlin-type-system]] — Generics, Variance, Reified Types
21. [[kotlin-coroutines]] — Coroutines: suspend, CoroutineScope, Dispatchers
22. [[kotlin-flow]] — Flow: StateFlow, SharedFlow, reactive streams
23. [[kotlin-interop]] — Kotlin-Java Interoperability: @JvmStatic, @JvmOverloads
24. [[kotlin-best-practices]] — идиоматичный Kotlin и оптимизация
25. [[kotlin-testing]] — JUnit, MockK, Kotest, Coroutines Testing

### Diagnostics
26. [[jvm-profiling]] — async-profiler: CPU, alloc, lock профилирование; flame graphs
27. [[jvm-benchmarking-jmh]] — JMH: warmup, Blackhole, Fork, статистически корректные бенчмарки
28. [[jvm-production-debugging]] — thread dump, heap dump, JFR: диагностика без downtime

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Освоить advanced Kotlin, Reflection, Annotation Processing и продвинутые JVM механизмы
> Время: ~3 недели
> Prerequisites: Level 2

29. [[kotlin-advanced-features]] — Extension Functions, Delegates, DSL, operator overloading
30. [[jvm-reflection-api]] — Reflection API: интроспекция классов, dynamic proxy, Method Handles
31. [[jvm-annotations-processing]] — аннотации и APT: compile-time метапрограммирование
32. [[jvm-bytecode-manipulation]] — ASM, Javassist, ByteBuddy: runtime модификация байткода
33. [[jvm-instrumentation-agents]] — Java агенты: premain/agentmain, ClassFileTransformer
34. [[jvm-module-system]] — JPMS (Java 9): module-info.java, requires/exports
35. [[jvm-service-loader-spi]] — ServiceLoader и SPI: plugin-архитектура, JDBC
36. [[jvm-jni-deep-dive]] — JNI: вызов C/C++ из Java, управление памятью
37. [[jvm-security-model]] — SecurityManager (deprecated), современные альтернативы

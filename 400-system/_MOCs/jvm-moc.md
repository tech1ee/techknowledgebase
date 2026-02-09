---
title: "JVM MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/jvm
  - type/moc
  - navigation
---
# JVM MOC

> Платформа JVM: от байткода и ClassLoader до GC tuning и production debugging

---

## Рекомендуемый путь изучения

```
1. [[jvm-basics-history]]            — История JVM и точка входа
         ↓
2. [[jvm-virtual-machine-concept]]   — Что такое виртуальная машина и зачем она нужна
         ↓
3. [[jvm-class-loader-deep-dive]]    — ClassLoader: загрузка классов, parent delegation
         ↓
4. [[jvm-memory-model]]              — Memory Model: Heap, Stack, Metaspace, JMM
         ↓
5. [[jvm-gc-tuning]]                 — Garbage Collectors: G1, ZGC, Parallel, выбор и настройка
         ↓
6. [[jvm-jit-compiler]]              — JIT Compiler: tiered compilation, inlining, escape analysis
         ↓
7. [[jvm-concurrency-overview]]      — Concurrency: потоки, JMM, Virtual Threads
         ↓
8. [[jvm-synchronization]]           — Синхронизация: synchronized, volatile, Atomic*, Lock
         ↓
9. [[jvm-concurrent-collections]]    — ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue
         ↓
10. [[jvm-executors-futures]]        — ExecutorService, CompletableFuture, Virtual Threads
         ↓
11. [[jvm-profiling]]                — Профилирование: async-profiler, flame graphs
         ↓
12. [[jvm-benchmarking-jmh]]         — JMH: правильные бенчмарки, warmup, Blackhole
         ↓
13. [[jvm-production-debugging]]     — Thread/Heap dump, JFR, диагностика без downtime
         ↓
14. [[jvm-reflection-api]]           — Reflection: интроспекция и dynamic proxy
         ↓
15. [[jvm-bytecode-manipulation]]    — ASM, ByteBuddy, Javassist: модификация байткода
```

---

## Статьи по категориям

### Foundation
- [[jvm-overview]] — карта раздела JVM, быстрая навигация по темам
- [[jvm-basics-history]] — история JVM, Write Once Run Anywhere, обзор архитектуры
- [[jvm-virtual-machine-concept]] — концепция виртуальной машины: абстрактный процессор, байткод
- [[jvm-jit-compiler]] — JIT: tiered compilation (Interpreter -> C1 -> C2), inlining, escape analysis
- [[jvm-class-loader-deep-dive]] — ClassLoader: Bootstrap/Platform/Application, parent delegation, hot reload

### Memory и GC
- [[jvm-memory-model]] — Heap, Stack, Metaspace, Java Memory Model (JMM), happens-before
- [[jvm-gc-tuning]] — G1 (default), ZGC (<10ms paузы), Parallel (max throughput), настройка
- [[jvm-performance-overview]] — карта оптимизации: измерить -> понять причину -> исправить -> проверить

### Concurrency
- [[jvm-concurrency-overview]] — карта многопоточности: JMM, volatile, synchronized, Virtual Threads
- [[jvm-synchronization]] — synchronized, volatile, Atomic*, ReentrantLock, LongAdder
- [[jvm-concurrent-collections]] — ConcurrentHashMap (lock striping), CopyOnWriteArrayList, BlockingQueue
- [[jvm-executors-futures]] — ExecutorService, CompletableFuture, Virtual Threads (Java 21)

### Languages
- [[jvm-languages-ecosystem]] — языки на JVM: Kotlin, Scala, Clojure, Groovy и их ниши
- [[java-modern-features]] — Java 8-21: lambdas, streams, records, sealed classes, Virtual Threads, pattern matching
- [[kotlin-overview]] — Kotlin: null safety, coroutines, extension functions, KMP

> Для подробного изучения Kotlin см. [[kotlin-moc]]

### Diagnostics
- [[jvm-profiling]] — async-profiler: CPU, alloc, lock профилирование; flame graphs
- [[jvm-benchmarking-jmh]] — JMH: warmup, Blackhole, Fork, статистически корректные бенчмарки
- [[jvm-production-debugging]] — thread dump, heap dump, JFR: диагностика в production без downtime

### Advanced
- [[jvm-reflection-api]] — Reflection API: интроспекция классов, dynamic proxy, Method Handles
- [[jvm-annotations-processing]] — аннотации и Annotation Processing: compile-time метапрограммирование
- [[jvm-bytecode-manipulation]] — ASM, Javassist, ByteBuddy: runtime модификация байткода
- [[jvm-instrumentation-agents]] — Java агенты: premain/agentmain, ClassFileTransformer, APM инструменты
- [[jvm-jni-deep-dive]] — JNI: вызов C/C++ из Java, управление памятью, типы ссылок
- [[jvm-module-system]] — JPMS (Java 9): module-info.java, requires/exports, инкапсуляция
- [[jvm-service-loader-spi]] — ServiceLoader и SPI: plugin-архитектура, JDBC driver discovery
- [[jvm-security-model]] — SecurityManager (deprecated Java 17, removed Java 24), современные альтернативы

---

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| Write Once, Run Anywhere | Один .class файл работает на любой ОС с установленной JVM | [[jvm-basics-history]] |
| JIT Compilation | Интерпретация -> C1 (2000 вызовов) -> C2 (15000 вызовов); после прогрева часто быстрее C++ | [[jvm-jit-compiler]] |
| Parent Delegation | ClassLoader спрашивает родителя перед загрузкой; защита от подмены системных классов | [[jvm-class-loader-deep-dive]] |
| Generational GC | Молодые объекты умирают быстро (Eden/Survivor), старые живут долго (Old Gen) | [[jvm-gc-tuning]] |
| happens-before | Гарантия видимости изменений между потоками: volatile write -> volatile read | [[jvm-memory-model]] |
| CAS (Compare-And-Swap) | Lock-free атомарная операция: AtomicInteger, LongAdder, ConcurrentHashMap | [[jvm-synchronization]] |
| Virtual Threads (Java 21) | Миллионы легковесных потоков для I/O-bound задач; заменяют thread pools | [[jvm-executors-futures]] |
| Flame Graph | Визуализация CPU-профиля: ширина = % времени, ищи самые широкие полосы | [[jvm-profiling]] |
| Escape Analysis | JIT определяет, что объект не покидает метод, и размещает его на стеке | [[jvm-jit-compiler]] |
| Java Flight Recorder | Continuous profiling с <2% overhead, безопасен для production | [[jvm-production-debugging]] |

---

## Связанные области

- [[kotlin-moc]] — Kotlin как основной JVM-язык: coroutines, null safety, KMP
- [[programming-moc]] — общие концепции программирования: паттерны, алгоритмы, парадигмы
- [[android-moc]] — Android использует ART (форк JVM) с DEX-байткодом вместо Java bytecode

---
title: "JVM Overview"
created: 2025-12-19
modified: 2025-12-19
type: moc
tags:
  - moc
  - jvm
  - java
  - kotlin
---

# JVM: Карта раздела

> От bytecode до production — полное понимание Java Virtual Machine

---

## TL;DR

**Что такое JVM:** Виртуальная машина, которая выполняет Java bytecode. "Write Once, Run Anywhere" — один и тот же .class файл работает на любой ОС с JVM.

**Почему это важно:** JVM — фундамент для Java, Kotlin, Scala, Groovy. Понимание JVM = предсказуемая производительность + умение диагностировать проблемы + оптимальный код.

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| **Новичок в JVM?** | [[jvm-virtual-machine-concept]] → [[jvm-basics-history]] |
| **Проблемы с памятью?** | [[jvm-memory-model]] → [[jvm-gc-tuning]] |
| **Многопоточность?** | [[jvm-concurrency-overview]] → [[jvm-synchronization]] |
| **Медленно работает?** | [[jvm-profiling]] → [[jvm-performance-overview]] |
| **Изучаешь Kotlin?** | [[kotlin-overview]] (Kotlin раздел) |

---

## Путь обучения

```
1. Foundation: как устроена JVM
   └── [[jvm-virtual-machine-concept]] → [[jvm-class-loader-deep-dive]] → [[jvm-jit-compiler]]

2. Memory: понимание памяти
   └── [[jvm-memory-model]] → [[jvm-gc-tuning]] → [[jvm-performance-overview]]

3. Concurrency: многопоточность
   └── [[jvm-concurrency-overview]] → [[jvm-synchronization]] → [[jvm-concurrent-collections]]

4. Advanced: продвинутые механизмы
   └── [[jvm-reflection-api]] → [[jvm-bytecode-manipulation]] → [[jvm-instrumentation-agents]]

5. Diagnostics: диагностика и профилирование
   └── [[jvm-profiling]] → [[jvm-production-debugging]] → [[jvm-benchmarking-jmh]]
```

---

## Статьи по категориям

### Foundation — Как устроена JVM

| Статья | Описание |
|--------|----------|
| [[jvm-virtual-machine-concept]] | Концепция виртуальной машины, stack vs register, bytecode |
| [[jvm-basics-history]] | История Java и JVM, эволюция версий |
| [[jvm-class-loader-deep-dive]] | Class loading: bootstrap, extension, application loaders |
| [[jvm-jit-compiler]] | Just-In-Time компиляция, C1/C2, GraalVM |

### Memory — Управление памятью

| Статья | Описание |
|--------|----------|
| [[jvm-memory-model]] | Heap, Stack, Metaspace, Java Memory Model |
| [[jvm-gc-tuning]] | G1, ZGC, Shenandoah, GC tuning |
| [[jvm-performance-overview]] | Performance optimizations, escape analysis |

### Concurrency — Многопоточность

| Статья | Описание |
|--------|----------|
| [[jvm-concurrency-overview]] | JMM, happens-before, volatile, synchronized |
| [[jvm-synchronization]] | Locks, monitors, atomic operations |
| [[jvm-concurrent-collections]] | ConcurrentHashMap, CopyOnWriteArrayList |
| [[jvm-executors-futures]] | ExecutorService, CompletableFuture, Virtual Threads |

### Advanced — Продвинутые механизмы

| Статья | Описание |
|--------|----------|
| [[jvm-reflection-api]] | Reflection, динамический доступ к классам |
| [[jvm-bytecode-manipulation]] | ASM, ByteBuddy, генерация кода |
| [[jvm-instrumentation-agents]] | Java Agents, instrumentation API |
| [[jvm-jni-deep-dive]] | Native code integration через JNI |
| [[jvm-module-system]] | JPMS (Java Platform Module System) |
| [[jvm-service-loader-spi]] | Service Provider Interface pattern |
| [[jvm-security-model]] | SecurityManager, permissions, sandboxing |
| [[jvm-annotations-processing]] | Compile-time annotation processing |

### Diagnostics — Диагностика и мониторинг

| Статья | Описание |
|--------|----------|
| [[jvm-profiling]] | async-profiler, JFR, flame graphs |
| [[jvm-production-debugging]] | JMX, remote debugging, heap dumps |
| [[jvm-benchmarking-jmh]] | JMH — правильные микробенчмарки |

### Languages — JVM языки

| Статья | Описание |
|--------|----------|
| [[java-modern-features]] | Java 8-21: lambdas, records, pattern matching |
| [[jvm-languages-ecosystem]] | Kotlin, Scala, Groovy, Clojure |
| [[kotlin-overview]] | **→ Kotlin раздел** (отдельный MOC) |

---

## Ключевые концепции

| Концепция | Что это | Почему важно |
|-----------|---------|--------------|
| **Bytecode** | Промежуточное представление между исходным кодом и машинным | Платформенная независимость, JIT оптимизации |
| **GC** | Автоматическое управление памятью | Нет утечек памяти, но нужно понимать паузы |
| **JIT** | Компиляция "горячего" кода в native | 10-100x ускорение после warmup |
| **JMM** | Java Memory Model — правила видимости | Корректная многопоточность |
| **ClassLoader** | Загрузка классов по требованию | Модульность, hot reload, изоляция |

---

## JVM vs Другие рантаймы

| Аспект | JVM | Node.js | Python | Go |
|--------|-----|---------|--------|----|
| **Компиляция** | JIT (bytecode→native) | JIT (V8) | Интерпретация | AOT (native) |
| **Память** | GC (G1, ZGC) | GC (V8) | GC (reference counting + GC) | GC |
| **Многопоточность** | Threads + Virtual Threads | Event loop | GIL | Goroutines |
| **Startup** | Медленный (warmup) | Быстрый | Средний | Мгновенный |
| **Peak performance** | Высокая | Средняя | Низкая | Высокая |

---

## Связи с другими разделами

- [[kotlin-overview]] — Kotlin как современный JVM язык
- [[android-overview]] — Android Runtime (ART) vs HotSpot JVM
- [[os-processes-threads]] — Потоки на уровне ОС
- [[cloud-platforms-essentials]] — JVM в контейнерах (Docker, K8s)

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "JVM = Java" | JVM запускает **любой язык** компилируемый в bytecode: Kotlin, Scala, Groovy, Clojure |
| "Bytecode интерпретируется" | Hot code **компилируется JIT** в native. После warmup — native performance |
| "GC = тормоза" | Современные GC (ZGC) имеют паузы **<1ms**. GC быстрее ручного malloc/free |
| "JVM старая технология" | JVM **активно развивается**: Virtual Threads (21), Panama (21), Valhalla (скоро) |
| "Нужно знать JVM для Java" | Для эффективного кода **критично** понимать GC, JIT, memory model |

---

## CS-фундамент

| CS-концепция | Применение в JVM |
|--------------|-----------------|
| **Virtual Machine** | Process VM — изоляция от OS, platform independence |
| **Just-In-Time Compilation** | Bytecode → native code. Profile-guided optimization |
| **Garbage Collection** | Mark-sweep, generational, concurrent. Автоматическое управление памятью |
| **Memory Model** | JMM: happens-before, visibility. Основа корректной concurrency |
| **ClassLoading** | Lazy loading, delegation, namespace isolation |

---

## Источники

- [JVM Specification](https://docs.oracle.com/javase/specs/jvms/se21/html/index.html) — официальная спецификация
- "Java Performance" by Scott Oaks — канонический труд
- [Inside Java Podcast](https://inside.java/podcast/) — от разработчиков JVM
- [OpenJDK Project](https://openjdk.org/) — open source реализация

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 35 |
| Категорий | 6 |
| Последнее обновление | 2025-12-19 |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

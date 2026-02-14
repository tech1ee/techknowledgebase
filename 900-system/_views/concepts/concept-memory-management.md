---
title: "Управление памятью: сквозной концепт"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
  - cross-cutting
---

# Управление памятью: сквозной концепт

> Как разные платформы решают фундаментальную задачу выделения, использования и освобождения памяти — от ручного управления до сборки мусора и подсчёта ссылок.

## Сравнительная матрица

| Платформа | Механизм | Тип сборки | Главная проблема | Ключевые файлы |
|---|---|---|---|---|
| JVM | Garbage Collection | Tracing GC (G1, ZGC) | Stop-the-world паузы | [[jvm-memory-model]], [[jvm-gc-tuning]] |
| Android | GC + ограничения ОС | ART GC (Concurrent) | Утечки через Context | [[android-memory-leaks]], [[android-process-memory]] |
| iOS | ARC (Automatic Reference Counting) | Подсчёт ссылок | Retain cycles | [[ios-process-memory]], [[ios-performance-profiling]] |
| KMP | Platform-specific | GC (JVM) / ARC (Native) | Разные модели на разных таргетах | [[kmp-memory-management]] |
| Cross-Platform | Абстракция над платформой | Зависит от рантайма | Утечки на стыке платформ | [[cross-memory-management]] |
| CS Foundations | Теоретические модели | Все типы | Понимание trade-offs | [[memory-model-fundamentals]], [[garbage-collection-explained]] |

## JVM

- [[jvm-memory-model]] — Heap, Stack, Metaspace, off-heap; поколения объектов (Young, Old); как JMM определяет видимость данных между потоками
- [[jvm-gc-tuning]] — G1, ZGC, Shenandoah: характеристики сборщиков, ключевые флаги настройки, анализ GC-логов
- [[jvm-performance-overview]] — комплексный взгляд на производительность JVM: память, CPU, I/O и их взаимосвязь

## Android

- [[android-memory-leaks]] — типичные утечки: Context в static-поле, незакрытые ресурсы, inner-классы с implicit-ссылкой на Activity
- [[android-process-memory]] — как Android управляет процессами: LMK (Low Memory Killer), oom_adj, приоритеты процессов
- [[android-performance-profiling]] — инструменты: Android Profiler, LeakCanary, MAT, heap dumps, allocation tracking

## iOS

- [[ios-process-memory]] — виртуальная память в iOS, dirty/clean pages, Jetsam (аналог OOM Killer), Memory Footprint
- [[ios-performance-profiling]] — Instruments: Allocations, Leaks, VM Tracker; Xcode Memory Graph Debugger для поиска retain cycles

## CS Foundations

- [[memory-model-fundamentals]] — стек vs куча, выравнивание, фрагментация, виртуальная память на уровне ОС
- [[garbage-collection-explained]] — mark-and-sweep, copying, generational GC: алгоритмы, trade-offs, latency vs throughput
- [[reference-counting-arc]] — подсчёт ссылок: принцип работы, проблема циклических ссылок, weak/unowned references
- [[memory-safety-ownership]] — Rust ownership model, borrow checker: как статический анализ заменяет рантайм-управление памятью

## Cross-Platform и KMP

- [[cross-memory-management]] — как кроссплатформенные фреймворки справляются с различиями в моделях памяти между платформами
- [[kmp-memory-management]] — особенности Kotlin/Native: новая модель памяти, взаимодействие GC (JVM) и ARC (iOS), общие объекты между потоками

## Глубинные паттерны

Существуют два фундаментальных подхода к автоматическому управлению памятью: **tracing GC** (JVM, Go, C#) и **reference counting** (Swift/ObjC, Python, Rust через RAII). GC находит живые объекты от корней и удаляет всё остальное — это точно, но требует пауз. ARC считает ссылки на каждый объект и удаляет при обнулении счётчика — это предсказуемо, но не справляется с циклами без помощи программиста (weak/unowned). Понимание этой фундаментальной разницы объясняет, почему на Android ищут утечки через Context, а на iOS — через retain cycles.

Android добавляет уникальный слой сложности: **ОС активно управляет процессами**. Low Memory Killer может убить фоновый процесс без предупреждения, поэтому Android-разработчик должен думать не только об утечках внутри процесса, но и о сохранении/восстановлении состояния при пересоздании процесса. iOS решает ту же проблему через Jetsam, но с другими порогами и политиками.

KMP создаёт особый вызов: один и тот же код работает на JVM (GC) и на iOS (ARC). Новая модель памяти Kotlin/Native (с версии 1.7.20) устранила requirement замораживания объектов для передачи между потоками, но разработчик всё равно должен понимать, что `object` в commonMain будет singleton с GC на Android и singleton с ARC на iOS — с разными характеристиками сборки.

## Для интервью

> [!tip] Ключевые вопросы
> - В чём принципиальная разница между Garbage Collection и Reference Counting? Какие типы утечек возможны в каждом подходе?
> - Как найти и устранить утечку памяти на Android? Опишите пошаговый процесс с инструментами.
> - Что такое retain cycle в iOS и почему GC на JVM эту проблему не имеет?
> - Как Android Low Memory Killer влияет на архитектуру приложения? Что должен сохранять onSaveInstanceState?
> - Как KMP справляется с тем, что на JVM — GC, а на iOS — ARC? Какие подводные камни это создаёт?

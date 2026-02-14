---
title: "Конкурентность: сквозной концепт"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
  - cross-cutting
---

# Конкурентность: сквозной концепт

> Как параллелизм и асинхронность реализованы на каждой платформе — от низкоуровневых примитивов ОС до высокоуровневых абстракций Kotlin Coroutines и Swift Concurrency.

## Сравнительная матрица

| Платформа | Основной механизм | Реактивный стек | Эволюция | Ключевые файлы |
|---|---|---|---|---|
| JVM | Threads + Executors | CompletableFuture | Threads → Executors → Virtual Threads | [[jvm-concurrency-overview]], [[jvm-executors-futures]] |
| Kotlin | Coroutines (structured) | Flow | Callbacks → Coroutines + Flow | [[kotlin-coroutines]], [[kotlin-flow]] |
| Android | Handler/Looper + Coroutines | RxJava / Flow | AsyncTask → RxJava → Coroutines | [[android-threading]], [[android-async-evolution]] |
| iOS | GCD + Swift Concurrency | Combine | NSThread → GCD → async/await | [[ios-threading-fundamentals]], [[ios-async-evolution]] |
| Cross-Platform | expect/actual абстракции | Kotlin Flow | Platform-specific → общий код | [[cross-concurrency-modern]], [[cross-concurrency-legacy]] |
| CS Foundations | Процессы и потоки ОС | Модели async I/O | Форки → потоки → green threads | [[processes-threads-fundamentals]], [[async-models-overview]] |

## JVM

- [[jvm-concurrency-overview]] — фундамент: Java Memory Model, happens-before, видимость переменных между потоками
- [[jvm-synchronization]] — synchronized, volatile, Lock API, атомарные операции и их стоимость
- [[jvm-concurrent-collections]] — ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue — потокобезопасные структуры данных
- [[jvm-executors-futures]] — пулы потоков, CompletableFuture, переход к структурированной асинхронности

## Kotlin

- [[kotlin-coroutines]] — suspend-функции, CoroutineScope, Dispatchers, structured concurrency как ответ на callback hell
- [[kotlin-flow]] — холодные и горячие потоки данных, операторы трансформации, интеграция с корутинами

## Android

- [[android-threading]] — главный поток, ANR, почему UI-операции нельзя выполнять в фоне
- [[android-handler-looper]] — внутренний механизм очереди сообщений Android, основа всей асинхронности платформы
- [[android-coroutines-mistakes]] — типичные ошибки: утечка корутин, неправильный scope, игнорирование cancellation
- [[android-background-work]] — WorkManager, foreground services, ограничения фоновой работы в новых версиях Android
- [[android-async-evolution]] — от AsyncTask через RxJava к корутинам: почему каждый шаг был необходим
- [[android-rxjava]] — реактивное программирование: Observable, операторы, backpressure, Schedulers
- [[android-executors]] — Java Executors на Android: ThreadPoolExecutor, когда корутины — не лучший выбор

## iOS

- [[ios-threading-fundamentals]] — потоки, RunLoop, main thread, архитектура многопоточности в Darwin
- [[ios-gcd-deep-dive]] — Grand Central Dispatch: очереди, группы, барьеры, семафоры, QoS
- [[ios-async-await]] — Swift Concurrency: async/await, Task, TaskGroup, actors, Sendable
- [[ios-combine]] — реактивный фреймворк Apple: Publishers, Subscribers, операторы, интеграция с SwiftUI
- [[ios-concurrency-mistakes]] — data races, priority inversion, main thread deadlocks, чрезмерное переключение контекста
- [[ios-async-evolution]] — от NSThread через GCD/Operations к structured concurrency

## Cross-Platform

- [[cross-concurrency-modern]] — как KMP и другие фреймворки абстрагируют разницу в конкурентности между платформами
- [[cross-concurrency-legacy]] — проблемы совместимости старых подходов (Kotlin/Native freeze, immutability)

## CS Foundations

- [[processes-threads-fundamentals]] — процессы vs потоки на уровне ОС, контекстное переключение, планировщик
- [[concurrency-vs-parallelism]] — ключевое различие: конкурентность (структура) vs параллелизм (исполнение)
- [[synchronization-primitives]] — мьютексы, семафоры, условные переменные, барьеры — базовые примитивы синхронизации
- [[async-models-overview]] — event loop, callback, promise/future, coroutine — сравнение моделей асинхронности

## Общая теория

- [[concurrency-parallelism]] — программистский взгляд: паттерны, антипаттерны, выбор модели для задачи

## Глубинные паттерны

Все платформы прошли одну и ту же эволюцию: **низкоуровневые потоки → пулы потоков / очереди → структурированная асинхронность**. JVM начала с `Thread` и пришла к `ExecutorService` и Virtual Threads. Android прошёл путь от `AsyncTask` через `RxJava` к Kotlin Coroutines. iOS эволюционировала от `NSThread` через GCD к Swift Concurrency с actors. Эта конвергенция не случайна — все платформы столкнулись с одними и теми же проблемами: callback hell, утечки ресурсов и гонки данных.

Ключевой паттерн — **structured concurrency** — появился независимо на Kotlin (CoroutineScope) и Swift (TaskGroup). Идея одна: жизненный цикл дочерней задачи привязан к родительской. Это решает фундаментальную проблему «fire-and-forget», когда забытая фоновая задача живёт дольше, чем компонент, который её запустил. На Android это проявляется как утечки корутин при уничтожении Activity, на iOS — как zombie tasks после dismissed ViewController.

Реактивные потоки (RxJava, Combine, Kotlin Flow) — параллельная ветка эволюции, решающая проблему наблюдения за изменяющимися данными. Все три фреймворка реализуют паттерн Publisher/Subscriber с поддержкой backpressure, но отличаются в деталях: RxJava — самая мощная и сложная, Combine — тесно интегрирована с SwiftUI, Flow — естественно вписывается в корутины Kotlin.

## Для интервью

> [!tip] Ключевые вопросы
> - Чем конкурентность отличается от параллелизма? Приведите пример, когда конкурентность есть, а параллелизма нет.
> - Что такое structured concurrency и какую проблему он решает? Сравните подходы Kotlin и Swift.
> - Почему Android отказался от AsyncTask? Какие фундаментальные проблемы он имел?
> - Как GCD и Kotlin Dispatchers решают одну и ту же задачу разными способами?
> - Что произойдёт, если запустить корутину в `GlobalScope` внутри Activity? Какой аналог этой ошибки в iOS?

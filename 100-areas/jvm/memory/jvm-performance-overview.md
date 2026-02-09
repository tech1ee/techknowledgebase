---
title: "JVM Performance: карта оптимизации"
created: 2025-11-25
modified: 2025-12-02
tags:
  - jvm
  - performance
  - overview
type: concept
area: programming
confidence: high
related:
  - "[[jvm-profiling]]"
  - "[[jvm-jit-compiler]]"
  - "[[jvm-gc-tuning]]"
  - "[[jvm-benchmarking-jmh]]"
  - "[[jvm-memory-model]]"
---

# JVM Performance: карта оптимизации

Оптимизация JVM — системный процесс: измерить (профилирование CPU, памяти, locks), понять причину (JIT не скомпилировал? GC паузы? Lock contention?), исправить (код, JVM флаги, архитектура), проверить (бенчмаркинг). Главное правило: профилируй ПЕРЕД оптимизацией, интуиция обманывает в 90% случаев.

Приложение тормозит, CPU 100%, GC паузы по 2 секунды — типичные симптомы. Без профилирования — неделя на оптимизацию JSON-парсинга, хотя проблема в N+1 SQL-запросах. Quick wins покрывают 80% проблем: N+1 запросы, string конкатенация в логах, неправильный GC для задачи.

---

## Порядок оптимизации

```
1. ИЗМЕРИТЬ (где проблема?)
   ├─ Профилирование CPU → [[jvm-profiling]]
   ├─ Профилирование памяти → [[jvm-profiling]]
   └─ Мониторинг в production

2. ПОНЯТЬ (почему медленно?)
   ├─ JIT не скомпилировал? → [[jvm-jit-compiler]]
   ├─ GC паузы? → [[jvm-gc-tuning]]
   └─ Lock contention? → [[jvm-concurrency-overview]]

3. ИСПРАВИТЬ
   ├─ Код (алгоритмы, структуры данных)
   ├─ JVM flags (GC, memory, JIT)
   └─ Архитектура (async, caching)

4. ПРОВЕРИТЬ
   └─ Бенчмаркинг → [[jvm-benchmarking-jmh]]
```

---

## Главное правило

> **Профилируй ПЕРЕД оптимизацией. Интуиция обманывает.**

```
Типичная ошибка:
Developer: "JSON парсинг тормозит, надо библиотеку поменять"
Профилирование: SQL запрос в цикле занимает 80% времени

Потратил бы неделю на оптимизацию не того места.
```

---

## Инструменты по задачам

| Задача | Инструмент | Когда |
|--------|------------|-------|
| CPU hotspots | async-profiler | Production safe, <1% overhead |
| Memory leaks | Eclipse MAT + heap dump | После OOM или подозрение на leak |
| GC проблемы | GC logs + GCViewer | High pause time, частые GC |
| Lock contention | async-profiler `-e lock` | Многопоточные проблемы |
| Benchmarking | JMH | Сравнение алгоритмов |
| Production мониторинг | JFR, Prometheus+Grafana | Continuous |

---

## Quick Wins (частые проблемы)

### 1. N+1 запросы к БД

```java
// ПЛОХО: 101 запрос
List<User> users = userRepo.findAll();  // 1 запрос
for (User u : users) {
    u.getOrders();  // 100 запросов!
}

// ХОРОШО: 1 запрос
@Query("SELECT u FROM User u LEFT JOIN FETCH u.orders")
List<User> findAllWithOrders();
```

Результат: p99 latency 800ms → 80ms (10x).

### 2. String конкатенация в логах

```java
// ПЛОХО: создаёт объекты даже если DEBUG выключен
logger.debug("User: " + userId + ", action: " + action);

// ХОРОШО: zero allocation если DEBUG выключен
logger.debug("User: {}, action: {}", userId, action);
```

Allocation rate: 500 MB/s → 50 MB/s.

### 3. Неправильный GC для задачи

```bash
# High throughput (batch processing)
-XX:+UseParallelGC

# Low latency API (<10ms pauses)
-XX:+UseZGC

# Balanced (default, хорош для большинства)
-XX:+UseG1GC
```

---

## Когда НЕ оптимизировать

1. **Нет измеримой проблемы** — оптимизация без данных = трата времени
2. **Premature optimization** — сначала работающий код, потом профилирование
3. **Micro-optimizations** — разница в наносекундах редко важна в реальном приложении

---

## Детальные руководства

| Тема | Описание |
|------|----------|
| [[jvm-profiling]] | CPU, Memory, Lock profiling. async-profiler, flame graphs |
| [[jvm-jit-compiler]] | Tiered compilation, Inlining, Escape Analysis, Deoptimization |
| [[jvm-gc-tuning]] | G1, ZGC, Shenandoah. Когда какой. Tuning flags |
| [[jvm-benchmarking-jmh]] | JMH framework, избегание ловушек, правильные бенчмарки |
| [[jvm-memory-model]] | Visibility, happens-before, volatile, synchronized |
| [[jvm-concurrency-overview]] | Threads, locks, concurrent collections |

---

## Чеклист: Performance Issue

```
□ Собрал метрики (latency, throughput, error rate)
□ Определил SLA нарушение (p99 > X ms?)
□ Профилировал под production-like нагрузкой
□ Нашёл top 3 hotspots
□ Проверил: это код или GC или I/O?
□ Сделал fix
□ Проверил бенчмарком
□ Задеплоил с мониторингом
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Java медленная" | После JIT warmup Java часто **быстрее C++** для серверных приложений благодаря profile-guided optimizations |
| "Добавить больше памяти = быстрее" | Больше heap = **дольше GC паузы**. Нужен правильный GC (ZGC для больших heap) |
| "Оптимизировать нужно сразу" | **Premature optimization** — корень зла. Сначала профилировать, потом оптимизировать |
| "Микробенчмарки показывают реальность" | Без JMH результаты **бессмысленны** — JIT может удалить весь код |
| "GC tuning — первый шаг" | Сначала уменьшить **allocation rate**, потом тюнить GC |

---

## CS-фундамент

| CS-концепция | Применение в JVM Performance |
|--------------|------------------------------|
| **Profiling** | Сбор данных о CPU, memory, lock contention. Flame graphs, async-profiler |
| **JIT Compilation** | Компиляция hot code в native. Tiered: C1 (быстро) → C2 (качественно) |
| **Garbage Collection** | Автоматическое управление памятью. G1, ZGC, Shenandoah — разные trade-offs |
| **Caching** | CPU cache, buffer pools, connection pools. Locality of reference критична |
| **Benchmarking** | JMH framework. Warmup, blackhole, fork isolation |

---

## Источники

- Java Performance: The Definitive Guide by Scott Oaks (2020)
- Optimizing Java by Benjamin J. Evans (2018)
- async-profiler documentation
- JMH samples and documentation

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

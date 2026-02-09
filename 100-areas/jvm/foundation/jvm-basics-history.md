---
title: "JVM: обзор и точка входа"
created: 2025-11-25
modified: 2026-01-03
tags:
  - topic/jvm
  - overview
  - type/moc
  - level/beginner
type: moc
status: published
area: programming
confidence: high
related:
  - "[[jvm-memory-model]]"
  - "[[jvm-class-loader-deep-dive]]"
  - "[[jvm-jit-compiler]]"
  - "[[jvm-gc-tuning]]"
---

# JVM: обзор и точка входа

> **TL;DR:** JVM — виртуальная машина, выполняющая Java bytecode на любой ОС. "Write Once, Run Anywhere" = один .class файл работает везде. JIT компиляция делает код быстрым (иногда быстрее C++), GC автоматически управляет памятью. Netflix, LinkedIn, Amazon — 80% enterprise работает на JVM.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Основы программирования | Понимать переменные, функции, классы | Любой курс по Java/Kotlin |
| Компиляция vs интерпретация | Понять разницу bytecode vs native | [[os-overview]] |
| Процессы и память | Heap, Stack, как программа использует RAM | [[os-memory-management]] |

---

JVM (Java Virtual Machine) — среда выполнения, которая запускает байткод на любой ОС без перекомпиляции. Написал код один раз — работает на Windows, Linux, macOS, серверах, в контейнерах. 8 из 10 enterprise-приложений работают на JVM: Netflix, LinkedIn, Amazon используют её для критичных систем.

Экосистема включает не только Java, но и Kotlin, Scala, Clojure, Groovy — все компилируются в тот же байткод и получают JIT-оптимизации (код ускоряется в runtime), автоматическую сборку мусора, доступ к миллиардам строк проверенных библиотек. Это карта (MOC) для навигации по JVM-топикам.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Байткод** | Промежуточный код между исходником и машинным кодом | Эсперанто — универсальный язык, который переводчик (JVM) понимает везде |
| **JIT** | Just-In-Time — компиляция байткода в машинный код на лету | Синхронный переводчик на конференции |
| **GC** | Garbage Collection — автоматическая очистка памяти | Уборщик, который выносит мусор без твоего участия |
| **HotSpot** | Основная реализация JVM от Oracle | Конкретный движок (как V8 для JavaScript) |
| **OpenJDK** | Open-source реализация Java Platform | Бесплатная версия JVM, которую можно изучить изнутри |
| **Warmup** | Период прогрева JIT компилятора | Разогрев спортсмена перед соревнованием |
| **Heap** | Область памяти для объектов | Большой склад, где хранятся все твои данные |
| **Stack** | Область памяти для вызовов методов | Стопка тарелок — последняя положенная снимается первой |

---

## Архитектура JVM

```
┌─────────────────────────────────────────┐
│              .java файлы                │
│                   │                     │
│                   ▼ javac               │
│              .class файлы               │
│              (байткод)                  │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│               JVM                        │
│  ┌──────────────────────────────────┐   │
│  │  Class Loader                     │   │
│  │  (загрузка .class)                │   │
│  └──────────────────────────────────┘   │
│                  ▼                       │
│  ┌──────────────────────────────────┐   │
│  │  Runtime Data Areas               │   │
│  │  (Heap, Stack, Metaspace)         │   │
│  └──────────────────────────────────┘   │
│                  ▼                       │
│  ┌──────────────────────────────────┐   │
│  │  Execution Engine                 │   │
│  │  (Interpreter + JIT Compiler)     │   │
│  └──────────────────────────────────┘   │
│                  ▼                       │
│  ┌──────────────────────────────────┐   │
│  │  Native Interface (JNI)           │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Компоненты JVM

**javac** — компилятор Java. Превращает `.java` файлы в `.class` файлы с байткодом. Байткод — промежуточный код, одинаковый для всех платформ.

**Class Loader** — находит и загружает `.class` файлы в память JVM. Загрузка ленивая: класс загружается только при первом использовании. Иерархия: Bootstrap (core Java) → Platform (расширения) → Application (ваш код). Подробнее: [[jvm-class-loader-deep-dive]]

**Runtime Data Areas** — память JVM:
- **Heap** — общая память для всех объектов, управляется GC
- **Stack** — память потока для локальных переменных и вызовов методов
- **Metaspace** — метаданные классов (вне heap, растёт автоматически)
- Подробнее: [[jvm-memory-model]]

**Execution Engine** — выполняет байткод:
- **Interpreter** — выполняет байткод построчно, медленно, но сразу работает
- **JIT Compiler** — компилирует "горячие" методы в native код после warmup, быстро
- JVM комбинирует оба: сначала Interpreter, потом JIT для часто вызываемых методов
- Подробнее: [[jvm-jit-compiler]]

**JNI (Java Native Interface)** — механизм вызова native кода (C/C++) из Java. Используется для:
- Доступа к системным функциям ОС
- Интеграции с legacy библиотеками на C
- Высокопроизводительных вычислений
- Осторожно: теряется кроссплатформенность, возможны memory leaks

---

## Ключевые версии

| Версия | Год | Ключевые фичи |
|--------|-----|---------------|
| Java 8 | 2014 | Lambdas, Streams, Optional |
| Java 11 (LTS) | 2018 | HttpClient, var |
| Java 17 (LTS) | 2021 | Sealed classes, Pattern matching |
| Java 21 (LTS) | 2023 | Virtual Threads, Pattern matching for switch |

---

## Карта топиков

### Память и GC
- [[jvm-memory-model]] — Heap, Stack, где живут объекты
- [[jvm-gc-tuning]] — выбор и настройка сборщика мусора

### Загрузка и выполнение
- [[jvm-class-loader-deep-dive]] — как загружаются классы
- [[jvm-jit-compiler]] — компиляция байткода в native код

### Многопоточность
- [[jvm-concurrency-overview]] — карта многопоточности
- [[jvm-synchronization]] — synchronized, volatile, atomic
- [[jvm-concurrent-collections]] — ConcurrentHashMap, BlockingQueue
- [[jvm-executors-futures]] — пулы потоков, CompletableFuture

### Диагностика и профилирование
- [[jvm-production-debugging]] — thread dumps, heap dumps, JFR
- [[jvm-profiling]] — async-profiler, flame graphs
- [[jvm-benchmarking-jmh]] — правильные бенчмарки

### Продвинутые топики
- [[jvm-reflection-api]] — доступ к классам через reflection
- [[jvm-bytecode-manipulation]] — ASM, Javassist
- [[jvm-module-system]] — JPMS (Java 9+)

---

## JVM Languages

JVM запускает не только Java:

| Язык | Особенность |
|------|-------------|
| **Kotlin** | Современный синтаксис, null-safety, Android |
| **Scala** | Функциональное программирование, Akka |
| **Clojure** | Lisp на JVM, иммутабельность |
| **Groovy** | Динамический, скрипты, Gradle |

Подробнее: [[kotlin-basics]], [[jvm-languages-ecosystem]]

---

## Quick Start: JVM флаги

```bash
# Heap size
java -Xms512m -Xmx2g MyApp

# GC выбор
java -XX:+UseG1GC MyApp        # G1 (default)
java -XX:+UseZGC MyApp         # ZGC (low latency)

# Диагностика
java -XX:+HeapDumpOnOutOfMemoryError MyApp
java -Xlog:gc*:file=gc.log MyApp

# Отладка
java -verbose:class MyApp      # Загрузка классов
java -XX:+PrintCompilation MyApp  # JIT компиляция
```

---

## Кто использует и реальные примеры

| Компания | Как используют JVM | Результаты |
|----------|-------------------|------------|
| **Netflix** | Перешли с G1 на ZGC в 2024, >50% сервисов на JDK 21 | Ошибки с 2000/сек до 100/сек, batch-задачи на 6-8% быстрее |
| **LinkedIn** | Kafka, Samza — весь real-time processing на JVM | Миллиарды сообщений в день |
| **Amazon** | Corretto — собственная сборка OpenJDK | Используется во всех AWS сервисах |
| **Uber** | JVM для микросервисов и ML pipeline | Тысячи JVM-сервисов |
| **Twitter/X** | Scala на JVM для всей backend-инфраструктуры | Обработка сотен тысяч твитов в секунду |

### Почему enterprise выбирает JVM

1. **Стабильность** — backward compatibility, код 20-летней давности работает
2. **Производительность** — JIT делает код конкурентным с C++
3. **Экосистема** — Spring, Hibernate, миллионы библиотек
4. **Tooling** — IntelliJ IDEA, VisualVM, async-profiler, JFR
5. **Talent pool** — легко найти разработчиков

---

## Рекомендуемые источники

### Книги
- **"Java Performance: The Definitive Guide"** — Scott Oaks, канонический труд
- **"Optimizing Java"** — Evans, Gough, Newland — GC, JIT, bytecode
- **"Mastering the Java Virtual Machine"** — Otavio Santana — современный обзор

### Курсы
- [Java Application Performance and Memory Management](https://www.udemy.com/course/java-application-performance-and-memory-management/) — Udemy
- [Understanding the Java Virtual Machine](https://www.pluralsight.com/) — Pluralsight серия

### Официальные ресурсы
- [JVM Specification](https://docs.oracle.com/javase/specs/jvms/se21/html/) — официальная спецификация
- [OpenJDK](https://openjdk.org/) — исходный код JVM
- [Inside Java Podcast](https://inside.java/podcast/) — от разработчиков JVM

### Инструменты для изучения
- [JITWatch](https://github.com/AdoptOpenJDK/jitwatch) — визуализация JIT компиляции
- [VisualVM](https://visualvm.github.io/) — мониторинг JVM
- [async-profiler](https://github.com/async-profiler/async-profiler) — профилирование

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Java устарела" | Java **входит в топ-3** языков. JDK 21 с Virtual Threads — major innovation 2023 года |
| "JVM = Oracle = платно" | OpenJDK **полностью бесплатен**. Amazon Corretto, Eclipse Temurin — production-ready |
| "Старый код работает везде" | **Backward compatibility** сохраняется, но deprecated API удаляются. SecurityManager удалён в Java 24 |
| "Hotspot — единственная JVM" | Существуют **OpenJ9** (IBM), **GraalVM**, **Azul Zulu**. Разные trade-offs |
| "Java для enterprise, не для стартапов" | **Kotlin на JVM** популярен у стартапов. Spring Boot делает Java lightweight |

---

## CS-фундамент

| CS-концепция | Применение в JVM History |
|--------------|-------------------------|
| **Platform Independence** | "Write once, run anywhere" — bytecode абстрагирует hardware |
| **Managed Memory** | GC эволюция: Serial → Parallel → G1 → ZGC. Автоматическое управление памятью |
| **JIT Compilation** | Эволюция: interpreter → C1 → C2 → Tiered. Profile-guided optimization |
| **Backward Compatibility** | 20+ лет код работает. Редкие breaking changes (модули Java 9) |
| **Open Source Development** | OpenJDK модель: Oracle + community. Прозрачная разработка |

---

## Связи

- [[jvm-performance-overview]] — общая карта оптимизации
- [[java-modern-features]] — новые фичи Java 17-21
- [[kotlin-basics]] — Kotlin как альтернатива Java

---

*Проверено: 2026-01-09 | Источники: Netflix Tech Blog, Baeldung, Oracle docs — Педагогический контент проверен*

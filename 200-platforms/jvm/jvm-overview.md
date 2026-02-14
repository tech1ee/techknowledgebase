---
title: "JVM Overview"
created: 2025-12-19
modified: 2025-12-19
type: moc
status: published
tags:
  - topic/jvm
  - type/moc
  - level/beginner
reading_time: 5
difficulty: 2
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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

---

## Проверь себя

> [!question]- Почему JVM использует JIT-компиляцию вместо того, чтобы сразу компилировать весь bytecode в native код при запуске?
> Потому что JIT работает на основе **профилирования в рантайме**: JVM сначала собирает статистику о том, какие методы вызываются чаще всего ("горячий код"), и только потом компилирует именно их с агрессивными оптимизациями (инлайнинг, escape analysis, devirtualization). AOT-компиляция при старте не имеет этих данных и не может применить profile-guided оптимизации. Кроме того, компиляция всего кода сразу значительно увеличила бы время запуска.

> [!question]- Приложение на Kotlin работает нормально в одном потоке, но падает с некорректными данными при добавлении многопоточности. Какие механизмы JVM нужно задействовать и почему?
> Проблема в **видимости изменений между потоками** — Java Memory Model не гарантирует, что изменение переменной в одном потоке будет видно другому без явной синхронизации. Нужно использовать: `volatile` (гарантия видимости), `synchronized` (атомарность + видимость), `java.util.concurrent` (Lock, Atomic-классы, ConcurrentHashMap) или Kotlin Coroutines с правильным диспатчером. Выбор зависит от конкретного сценария — но ключевое правило: без happens-before гарантий нет корректной многопоточности.

> [!question]- В чём фундаментальное различие между ClassLoader-ами bootstrap, extension и application, и как это влияет на изоляцию кода?
> Они образуют **иерархию делегирования**: bootstrap загружает core API (java.lang.*), extension — расширения платформы, application — код приложения. Загрузка идёт снизу вверх (delegation model): application сначала спрашивает extension, тот — bootstrap. Это даёт **изоляцию и безопасность**: приложение не может подменить системные классы (например, свой java.lang.String), потому что bootstrap загрузит оригинал первым. Этот же механизм используется для hot reload и модульности (OSGi, JPMS).

> [!question]- Сервис на JVM в Docker-контейнере с лимитом 512 MB RAM внезапно убивается OOM Killer. Объясните, почему heap = 512 MB — ошибочная конфигурация.
> JVM потребляет память **не только под heap**: Metaspace (метаданные классов), thread stacks (по ~1 MB на поток), direct buffers (NIO), code cache (JIT-скомпилированный код), GC overhead. Суммарно non-heap может занять 150-300 MB. Поэтому при лимите контейнера 512 MB heap должен быть ~256-300 MB максимум. Современные JVM (8u191+) поддерживают флаги `-XX:MaxRAMPercentage` для автоматического расчёта, учитывающего cgroup limits контейнера.

---

## Ключевые карточки

Что означает принцип "Write Once, Run Anywhere" в контексте JVM?
?
Исходный код компилируется в промежуточный bytecode (.class файлы), который выполняется на любой платформе, где установлена JVM. Платформозависимость скрыта внутри конкретной реализации JVM.

Какие фазы проходит код от исходника до исполнения на JVM?
?
Исходный код (.java/.kt) -> компилятор -> bytecode (.class) -> ClassLoader загружает в JVM -> интерпретатор выполняет -> JIT компилирует "горячий" код в native. После warmup основной код работает как нативный.

Чем G1 GC отличается от ZGC по подходу к паузам?
?
G1 делит heap на регионы и собирает мусор инкрементально, но всё ещё имеет stop-the-world паузы (обычно 50-200 ms). ZGC выполняет почти всю работу **конкурентно** с приложением, достигая пауз менее 1 ms независимо от размера heap.

Что такое happens-before в Java Memory Model?
?
Отношение порядка между операциями, гарантирующее видимость записей: если операция A happens-before операции B, то все изменения A видны в B. Устанавливается через synchronized, volatile, Thread.start(), Thread.join() и другие механизмы.

Зачем JVM нужен warmup и сколько он длится?
?
В начале работы JVM интерпретирует bytecode (медленно), параллельно собирая профиль выполнения. JIT-компилятор использует эти данные для оптимизации "горячих" методов. Warmup обычно занимает 30 секунд — несколько минут в зависимости от приложения.

Что хранится в Metaspace и почему он заменил PermGen?
?
Metaspace хранит метаданные классов, информацию о методах и constant pool. В отличие от PermGen, Metaspace выделяется в native-памяти ОС и растёт динамически, что устраняет типичные PermGen OutOfMemoryError при большом количестве загруженных классов.

Почему Virtual Threads (Project Loom) — значительное изменение для JVM?
?
Virtual Threads позволяют создавать миллионы легковесных потоков (managed JVM-ом, не ОС), сохраняя привычную блокирующую модель программирования. Это устраняет необходимость в реактивных фреймворках для масштабирования I/O-bound приложений.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[jvm-virtual-machine-concept]] | Понять архитектуру JVM: stack vs register machine, структура bytecode |
| Углубление | [[jvm-memory-model]] | Разобраться в heap/stack/metaspace и Java Memory Model |
| Практика | [[jvm-gc-tuning]] | Научиться выбирать и настраивать сборщик мусора |
| Язык | [[kotlin-overview]] | Kotlin как основной язык для JVM и Android разработки |
| Кросс-домен | [[android-overview]] | Понять как ART (Android Runtime) отличается от HotSpot JVM |
| Кросс-домен | [[bytecode-virtual-machines]] | CS-фундамент: как работают виртуальные машины на уровне теории |
| Диагностика | [[jvm-profiling]] | Научиться находить узкие места: async-profiler, JFR, flame graphs |

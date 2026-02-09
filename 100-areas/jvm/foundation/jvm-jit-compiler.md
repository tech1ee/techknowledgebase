---
title: "JIT Compiler: как JVM ускоряет код"
created: 2025-11-25
modified: 2026-01-03
tags:
  - jvm
  - jit
  - performance
  - compilation
type: deep-dive
area: programming
confidence: high
related:
  - "[[jvm-performance-overview]]"
  - "[[jvm-profiling]]"
  - "[[jvm-benchmarking-jmh]]"
---

# JIT Compiler: как JVM ускоряет код

> **TL;DR:** JIT компилирует bytecode в native код во время выполнения. Tiered compilation: Interpreter (медленно) → C1 (~2000 вызовов, 10x ускорение) → C2 (~15000 вызовов, 100x ускорение). Ключевые оптимизации: inlining, escape analysis (объекты на стеке), loop unrolling. Warmup = 10-60 сек. После прогрева JVM часто быстрее C++ благодаря profile-guided оптимизациям.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Как работает JVM | Понимать путь от bytecode к выполнению | [[jvm-basics-history]] |
| Bytecode basics | Что компилирует JIT | [[jvm-virtual-machine-concept]] |
| CPU architecture basics | Понимать native code, регистры, cache | [[os-overview]] |

---

JIT (Just-In-Time) Compiler — подсистема JVM, которая превращает байткод в машинный код прямо во время выполнения программы. В отличие от статической компиляции (C/C++), где код компилируется один раз до запуска, JIT компилирует "на лету" и может использовать информацию о реальном поведении программы для более агрессивных оптимизаций.

Это объясняет парадокс: Java-код после прогрева может работать *быстрее* эквивалентного C++ кода. JIT видит реальные типы объектов, реальные ветвления, реальную частоту вызовов — и оптимизирует именно под это. C++ компилятор работает вслепую, не зная, как программа будет использоваться.

Обратная сторона — warmup. Первые 10-30 секунд работы приложения код выполняется интерпретатором (в 10-100 раз медленнее), пока JIT собирает статистику и компилирует горячие методы. Бенчмарки без учёта warmup показывают бессмысленные результаты.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **JIT** | Just-In-Time — компиляция во время выполнения | Синхронный переводчик на конференции |
| **Interpreter** | Построчное выполнение байткода (медленно, но сразу) | Читать инструкцию и делать по шагу |
| **C1 (Client)** | Быстрый компилятор с базовыми оптимизациями | Черновой перевод — быстро, но неидеально |
| **C2 (Server)** | Медленный компилятор с агрессивными оптимизациями | Литературный перевод — долго, но качественно |
| **Warmup** | Период прогрева, пока JIT компилирует код | Разогрев спортсмена перед соревнованием |
| **Inlining** | Замена вызова метода на его тело | Вместо "см. стр. 42" вставить текст прямо сюда |
| **Escape Analysis** | Анализ: "убегает" ли объект из метода | Проверка: нужно ли упаковывать подарок, если он останется дома |
| **Deoptimization** | Откат скомпилированного кода в интерпретатор | Отмена оптимистичного решения, когда оно оказалось неверным |
| **OSR** | On-Stack Replacement — замена кода во время выполнения | Замена двигателя на ходу |
| **Profile-Guided** | Оптимизации на основе реального поведения | Настройка маршрута на основе пробок |

---

## Tiered Compilation: от интерпретатора к native

Современная HotSpot JVM использует многоуровневую компиляцию. Каждый метод проходит через несколько стадий, постепенно ускоряясь.

### Уровни компиляции

**Level 0: Interpreter** — JVM начинает с интерпретации байткода. Это медленно (в 10-100 раз медленнее native кода), но начинается мгновенно. Интерпретатор также собирает базовую статистику: сколько раз вызван метод, какие ветви if/else выполнялись чаще.

**Level 3: C1 Compiler** — после ~2000 вызовов метод компилируется C1. Это быстрый компилятор, который генерирует код за 1-5 миллисекунд. Качество кода среднее (в 2-5 раз медленнее оптимального), но главное — C1 встраивает в код инструментацию для детального профилирования.

**Level 4: C2 Compiler** — после ~15000 вызовов и на основе собранного профиля C2 перекомпилирует метод с агрессивными оптимизациями. Компиляция занимает 100-500 мс, но результат — код, близкий по скорости к ручному C++.

```
Метод вызывается впервые
       │
       ▼
Level 0: Interpreter
       │ Собирает базовую статистику
       │ ~2000 вызовов
       ▼
Level 3: C1 Compiler
       │ Генерирует код + профилирование
       │ ~15000 вызовов
       ▼
Level 4: C2 Compiler
       │ Агрессивные оптимизации на основе профиля
       ▼
Максимальная производительность
```

### Почему не сразу C2?

Компромисс между временем запуска и пиковой производительностью. Если бы JVM ждала 15000 вызовов перед первой компиляцией, короткоживущие программы работали бы только на интерпретаторе. C1 даёт быстрый буст (10x к интерпретатору), пока C2 собирает данные для финальной оптимизации.

### Наблюдение за компиляцией

```bash
java -XX:+PrintCompilation MyApp

# Вывод:
#  76   3   java.lang.String::hashCode (55 bytes)
#        ↑   ↑   ↑
#  время уровень  метод (размер байткода)

#  77   4   MyApp::compute (10 bytes)
#        ↑
#   Level 4 = C2, максимальная оптимизация
```

---

## Ключевые оптимизации JIT

JIT применяет десятки оптимизаций, но несколько из них дают основной выигрыш.

### Method Inlining

Inlining — замена вызова метода на его тело. Это устраняет накладные расходы вызова (сохранение регистров, переход, возврат), но главное — открывает возможности для дальнейших оптимизаций.

Когда код разбит на маленькие методы, каждый метод оптимизируется изолированно. JIT не видит, что `getValue()` всегда возвращает константу, потому что это другой метод. После inlining'а код объединяется, и становятся возможны constant folding, dead code elimination и другие оптимизации.

```java
// Исходный код
public int calculate(int x) {
    return add(x, 10) + multiply(x, 2);
}
private int add(int a, int b) { return a + b; }
private int multiply(int a, int b) { return a * b; }

// После inlining (что делает JIT)
public int calculate(int x) {
    return (x + 10) + (x * 2);
    // Дальше JIT может упростить: 3*x + 10
}
```

**Ограничения inlining:**
- Методы > 35 байт байткода не inline'ятся по умолчанию
- Virtual методы inline'ятся только если JIT уверен в типе (monomorphic call)
- Рекурсивные методы inline'ятся ограниченно

```bash
# Посмотреть решения inlining
java -XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining MyApp

# Увеличить порог (осторожно — раздувает код)
-XX:MaxInlineSize=50
-XX:FreqInlineSize=400  # для частых методов
```

### Escape Analysis

JVM анализирует, "убегает" ли объект из метода — то есть сохраняется ли ссылка на него где-то, откуда её можно получить после возврата из метода.

Если объект не убегает, JVM может:
1. **Scalar replacement** — разложить объект на отдельные переменные
2. **Stack allocation** — выделить память на стеке вместо heap
3. **Lock elision** — убрать синхронизацию, если объект локален для потока

```java
// Исходный код
public int sumPoints() {
    Point p = new Point(10, 20);  // Объект не убегает!
    return p.x + p.y;
}

// Что делает JIT (scalar replacement)
public int sumPoints() {
    int p_x = 10;  // Нет объекта — нет heap allocation
    int p_y = 20;  // Нет GC pressure
    return p_x + p_y;
}
```

**Когда объект "убегает":**
- Возвращается из метода
- Присваивается в поле объекта
- Передаётся в другой метод (который JIT не смог inline'ить)
- Сохраняется в коллекцию

```java
// Объект убегает — heap allocation обязательна
Point p = new Point(10, 20);
cache.put("key", p);  // Убежал в коллекцию
return p.x + p.y;
```

### Loop Unrolling

Цикл имеет накладные расходы: проверка условия, инкремент счётчика, переход. При разворачивании JIT копирует тело цикла несколько раз, уменьшая количество итераций и overhead.

```java
// Исходный цикл
for (int i = 0; i < 100; i++) {
    sum += array[i];
}

// После unrolling (factor 4)
for (int i = 0; i < 100; i += 4) {
    sum += array[i];
    sum += array[i+1];
    sum += array[i+2];
    sum += array[i+3];
}
// 25 итераций вместо 100, меньше проверок и переходов
```

Дополнительно развёрнутый цикл лучше использует pipeline процессора — несколько операций могут выполняться параллельно.

### Vectorization (SIMD)

Современные процессоры имеют SIMD инструкции (SSE, AVX, AVX-512), которые обрабатывают несколько элементов данных одной инструкцией. JIT автоматически векторизует подходящие циклы.

```java
// Исходный код
for (int i = 0; i < array.length; i++) {
    array[i] *= 2;
}

// JIT может сгенерировать AVX2 код:
// Одна инструкция обрабатывает 8 int'ов (256 бит)
// или 16 int'ов для AVX-512
```

Векторизация даёт выигрыш в 4-16 раз на подходящих операциях. JIT Vector API (Java 16+) позволяет явно писать векторный код.

---

## C1 vs C2: два компилятора

JVM содержит два JIT компилятора с разными целями.

### C1 (Client Compiler)

Быстрая компиляция, базовые оптимизации. Задача — быстро дать улучшение относительно интерпретатора.

- **Время компиляции:** 1-5 мс
- **Оптимизации:** inlining простых методов, базовое устранение мёртвого кода
- **Когда используется:** warmup phase, код средней частоты

### C2 (Server Compiler)

Медленная компиляция, агрессивные оптимизации. Задача — максимальная производительность для горячего кода.

- **Время компиляции:** 100-500 мс
- **Оптимизации:** escape analysis, loop unrolling, vectorization, speculative optimizations
- **Когда используется:** горячие методы после 15000+ вызовов

### Сравнение производительности

```
Один и тот же метод, 1,000,000 вызовов:

Interpreter:  ~500ms   (baseline)
C1 compiled:   ~50ms   (10x быстрее)
C2 compiled:    ~5ms   (100x быстрее)
```

Разница в 100x между интерпретатором и C2 — причина, почему warmup критически важен для бенчмарков и latency-sensitive приложений.

---

## Deoptimization: когда оптимизации отменяются

JIT делает предположения на основе наблюдаемого поведения. Если предположение нарушается, скомпилированный код становится некорректным и должен быть отменён.

### Speculative Optimization

JIT наблюдает, что виртуальный метод всегда вызывается на объектах одного типа (monomorphic call site). Он встраивает код конкретной реализации напрямую, избегая виртуального вызова.

```java
List<Animal> animals = new ArrayList<>();
for (int i = 0; i < 100_000; i++) {
    animals.add(new Dog());
}

for (Animal a : animals) {
    a.sound();  // JIT видит: всегда Dog
                // Inline'ит Dog::sound() напрямую
}

// Потом добавляем Cat
animals.add(new Cat());
// При следующем вызове:
//   1. Проверка типа обнаруживает Cat
//   2. DEOPTIMIZATION — откат в интерпретатор
//   3. Перекомпиляция с виртуальным вызовом
```

Deoptimization — не катастрофа, но имеет цену: время на откат и перекомпиляцию, потеря оптимизаций. В hot path это может вызвать latency spike.

### Uncommon Traps

JIT оптимизирует под частый путь выполнения, игнорируя редкие ветви.

```java
public int divide(int a, int b) {
    if (b == 0) {  // Профиль: 0.001% случаев
        throw new ArithmeticException();
    }
    return a / b;  // Основной путь — оптимизирован
}
```

Если `b == 0` начинает происходить чаще, JIT перекомпилирует метод, учитывая этот путь.

### Мониторинг deoptimization

```bash
java -XX:+PrintDeoptimization MyApp

# Вывод:
# Deoptimization: reason='bimorphic' action='recompile' method=...
#                        ↑
#           Причина: было 2 типа, стало больше
```

Частые deoptimizations указывают на проблемы в коде (megamorphic calls) или нестабильные паттерны использования.

---

## Warmup: период прогрева

### Почему первые запросы медленные

При старте приложения весь код выполняется интерпретатором. JIT начинает компилировать методы только после накопления статистики.

```
Типичный warmup веб-приложения:

0-5 сек:    Загрузка классов, interpreter
5-30 сек:   C1 компиляция основных путей
30-60 сек:  C2 компиляция горячего кода
60+ сек:    Стабильная производительность
```

Для latency-critical систем это означает, что нельзя направлять production traffic на только что запущенный инстанс.

### Стратегии ускорения warmup

**1. Снижение порогов компиляции:**
```bash
-XX:Tier3InvocationThreshold=100   # C1 после 100 вызовов (вместо 2000)
-XX:Tier4InvocationThreshold=1000  # C2 после 1000 (вместо 15000)
```
Быстрее warmup, но C2 получает меньше данных для оптимизации.

**2. Warmup скрипт:**
Перед открытием traffic прогнать типичные запросы:
```bash
# Прогреть эндпоинты
for i in {1..1000}; do
  curl http://localhost:8080/api/users
  curl http://localhost:8080/api/orders
done
```

**3. Class Data Sharing (CDS):**
```bash
# Создать архив классов
java -Xshare:dump -XX:SharedClassListFile=classes.list

# Использовать при запуске
java -Xshare:on -XX:SharedArchiveFile=app.jsa -jar app.jar
```
Ускоряет загрузку классов, но не JIT компиляцию.

**4. AOT / Native Image (GraalVM):**
```bash
native-image -jar app.jar
```
Компилирует в native код до запуска. Мгновенный старт, но теряются runtime оптимизации.

---

## Практические рекомендации

### Пишите маленькие методы

JIT лучше оптимизирует маленькие методы — они inline'ятся, открывая возможности для дальнейших оптимизаций.

```java
// Проблема: 200 строк — не inline'ится, оптимизируется изолированно
public void processEverything() {
    // ... огромный метод ...
}

// Лучше: каждый метод может inline'иться
public void process() {
    validate();
    transform();
    save();
}
```

Парадокс: разбиение на методы добавляет вызовы, но JIT их устраняет, а взамен получает лучший код.

### Избегайте megamorphic calls

Когда виртуальный метод вызывается на объектах многих типов (megamorphic), JIT не может inline'ить и вынужден использовать virtual dispatch каждый раз.

```java
// Проблема: 10 разных типов Animal — megamorphic
List<Animal> zoo;  // Dog, Cat, Bird, Fish, Snake, ...
for (Animal a : zoo) {
    a.sound();  // Virtual dispatch, нет inline
}

// Лучше: разделить по типам, где возможно
List<Dog> dogs;
for (Dog d : dogs) {
    d.sound();  // Monomorphic — inline!
}
```

### Помогайте Escape Analysis

Локальные объекты, не убегающие из метода, могут размещаться на стеке. Старайтесь не "выпускать" временные объекты.

```java
// Хорошо: Point не убегает
Point p = new Point(x, y);
return p.distance(origin);  // Stack allocation возможна

// Плохо: объект убегает в кэш
Point p = new Point(x, y);
cache.put(key, p);  // Heap allocation обязательна
return p.distance(origin);
```

### Используйте final

`final` классы и методы дают JIT больше свободы — не нужно учитывать возможные override'ы.

```java
// JIT знает: метод не переопределён
public final void process() { ... }

// Весь класс final = все методы virtual dispatch free
public final class FastProcessor { ... }
```

---

## Диагностика JIT

### Что компилируется

```bash
java -XX:+PrintCompilation MyApp

#   123   4   com.example.Service::process (45 bytes)
#    ↑    ↑   ↑
#  время уровень  метод (размер)
```

### Решения об inlining

```bash
java -XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining MyApp

# @ 12   com.example.Helper::getValue (5 bytes)   inline (hot)
# @ 34   com.example.Helper::compute (120 bytes)  too big
```

### Детали компиляции

```bash
# Сохранить ассемблерный код
java -XX:+UnlockDiagnosticVMOptions \
     -XX:+PrintAssembly \
     -XX:LogFile=hotspot.log \
     MyApp
```

---

## Кто использует и реальные примеры

| Компания/Проект | Как используют JIT | Результаты |
|-----------------|-------------------|------------|
| **Netflix** | Тюнинг C2 для streaming сервисов | Peak performance после 30-60 сек warmup |
| **Twitter** | Scala на JVM, агрессивный inlining | Миллионы запросов в секунду |
| **Alibaba** | Dragonwell JDK с улучшенным JIT | Оптимизации под их workload |
| **GraalVM** | Новый JIT компилятор на Java | +10-15% производительность vs C2 |
| **AWS Lambda** | SnapStart = сохранение warmed JVM | Cold start с 5сек до <1сек |

### GraalVM vs HotSpot C2

```
HotSpot C2 (написан на C++):
- Зрелый, проверенный 20+ лет
- Сложный код, трудно развивать
- Хорошо работает для большинства случаев

GraalVM (написан на Java):
- Современная архитектура
- Легче добавлять новые оптимизации
- +10-15% для некоторых workloads
- Native Image: AOT компиляция (startup <50ms)
```

### Реальные цифры warmup

| Тип приложения | Warmup до peak | Когда достаточно C1 |
|----------------|----------------|---------------------|
| Web API (Spring Boot) | 30-60 сек | ~10 сек для базовой производительности |
| Batch processing | 1-5 мин | Не критично, важен throughput |
| Trading system | 10-20 мин (требуют pre-warming) | Недопустимо, нужен C2 |
| AWS Lambda | SnapStart или Native Image | C1 недостаточно |

---

## Рекомендуемые источники

### Книги
- **"Java Performance: The Definitive Guide"** — Scott Oaks, глава про JIT
- **"Optimizing Java"** — Evans, Gough, Newland — подробно про C1/C2

### Статьи
- [JIT Compiler in JVM](https://www.baeldung.com/graal-java-jit-compiler) — Baeldung intro
- [Understanding JIT Compilation](https://www.infoq.com/articles/Graal-JIT-Compiler/) — InfoQ глубокий разбор
- [GraalVM JIT vs HotSpot](https://www.graalvm.org/latest/reference-manual/java/compiler/) — официальное сравнение

### Инструменты
- [JITWatch](https://github.com/AdoptOpenJDK/jitwatch) — визуализация JIT компиляции
- `-XX:+PrintCompilation` — лог компиляции методов
- `-XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining` — решения об inlining

### Видео
- [Understanding Java JIT Compilation](https://www.youtube.com/results?search_query=java+jit+compilation) — YouTube tutorials
- [Devoxx talks on JIT](https://www.youtube.com/c/Devoxx) — конференционные доклады

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Java медленная потому что интерпретируется" | JIT компилирует hot code в **native machine code**. После warmup Java может быть быстрее C++ благодаря profile-guided optimizations |
| "Warmup — это проблема Java" | Warmup — **цена за runtime optimizations**. JIT знает реальный профиль исполнения и делает оптимизации невозможные для AOT компиляторов |
| "Native Image всегда лучше JIT" | Native Image = fast startup, но **меньше runtime оптимизаций**. Для долгоживущих серверов JIT обычно даёт лучший throughput после warmup |
| "C2 компилятор всегда лучше C1" | C1 быстрее компилирует, даёт **быстрый старт**. Tiered compilation (C1 → C2) — лучший баланс. Trading apps pre-warm до C2 |
| "Inlining всегда улучшает performance" | Aggressive inlining может **ухудшить** performance: code bloat, instruction cache misses. JIT балансирует inline threshold |
| "Одинаковый код работает одинаково быстро" | JIT оптимизирует на основе **профиля исполнения**. Один и тот же код в разных сценариях компилируется по-разному. Megamorphic calls медленнее |
| "Достаточно запустить приложение под нагрузкой для warmup" | Warmup должен покрывать **все code paths**. Если редкий path не вызывался при warmup, он будет интерпретироваться при первом вызове |
| "GraalVM = замена HotSpot" | GraalVM — **альтернативный JIT** (можно использовать с HotSpot) или отдельная VM. Для некоторых workloads +10-15%, для других без разницы |
| "Deoptimization = баг" | Deoptimization — **нормальная часть** tiered compilation. JIT speculates, если speculation wrong — deopt и recompile. Это OK |
| "Микробенчмарки показывают реальную производительность" | JIT может **оптимизировать dead code**. Без JMH и Blackhole результаты бессмысленны. Warmup iterations обязательны |

---

## CS-фундамент

| CS-концепция | Применение в JIT Compiler |
|--------------|--------------------------|
| **Profile-Guided Optimization (PGO)** | JIT собирает профиль: какие методы горячие, какие branch'и чаще, какие типы в call sites. Оптимизирует на основе реального поведения |
| **Method Inlining** | Подстановка тела метода вместо вызова. Убирает call overhead, открывает возможности для дальнейших оптимизаций (constant propagation, dead code elimination) |
| **Escape Analysis** | Определяет, "убегает" ли объект из метода. Если нет — можно аллоцировать на стеке (scalar replacement) вместо heap. Убирает GC pressure |
| **Loop Unrolling** | Разворачивание цикла: вместо 100 итераций — 25 по 4 операции. Уменьшает branch overhead, улучшает instruction-level parallelism |
| **Dead Code Elimination (DCE)** | Удаление кода, результат которого не используется. Важно для benchmarks: без Blackhole JIT может удалить весь тестируемый код |
| **Speculative Optimization** | JIT делает предположения (один тип в call site) и оптимизирует. Если предположение нарушено — deoptimization и fallback |
| **On-Stack Replacement (OSR)** | Компиляция метода пока он выполняется (в цикле). Позволяет перейти с интерпретатора на compiled code без выхода из метода |
| **Register Allocation** | Распределение переменных по CPU регистрам. JIT использует linear scan или graph coloring алгоритмы. Критично для performance |
| **Intermediate Representation (IR)** | C2 использует "sea of nodes" IR для оптимизаций. Позволяет применять classical compiler optimizations к bytecode |
| **Tiered Compilation** | Многоуровневая компиляция: interpreter → C1 → C2. Trade-off между временем компиляции и качеством оптимизации. Адаптивная стратегия |

---

## Связи

- [[jvm-performance-overview]] — общая карта оптимизации JVM
- [[jvm-benchmarking-jmh]] — как правильно измерять с учётом warmup
- [[jvm-profiling]] — найти горячие методы для оптимизации
- [[java-modern-features]] — GraalVM и Native Image (AOT альтернатива)

---

*Проверено: 2026-01-09 | Источники: Oracle docs, GraalVM, Baeldung — Педагогический контент проверен*

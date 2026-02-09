---
title: "JMH: правильные бенчмарки в Java"
created: 2025-11-25
modified: 2025-12-02
tags:
  - topic/jvm
  - jmh
  - benchmarking
  - performance
  - type/deep-dive
  - level/intermediate
type: deep-dive
status: published
area: programming
confidence: high
related:
  - "[[jvm-performance-overview]]"
  - "[[jvm-jit-compiler]]"
  - "[[jvm-profiling]]"
---

# JMH: правильные бенчмарки в Java

JMH (Java Microbenchmark Harness) — официальный фреймворк от OpenJDK для измерения производительности. Решает проблемы наивных бенчмарков: warmup для JIT-компиляции, предотвращение Dead Code Elimination через Blackhole, статистика за множество итераций, изоляция через Fork.

`System.nanoTime()` в цикле — не бенчмарк. JIT может удалить весь код как dead code, первые 15000 итераций работают в интерпретаторе (в 100 раз медленнее), GC паузы искажают результаты, одно измерение статистически бессмысленно. JMH создан разработчиками JVM — они знают все оптимизации компилятора и как их обойти.

---

## Быстрый старт

### Зависимости

```xml
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-generator-annprocess</artifactId>
    <version>1.37</version>
</dependency>
```

### Простой бенчмарк

```java
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;
import java.util.concurrent.TimeUnit;

@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 10, time = 1)
@Fork(2)
public class StringBenchmark {

    @Benchmark
    public void stringConcat(Blackhole bh) {
        String result = "";
        for (int i = 0; i < 100; i++) {
            result += i;  // Медленно
        }
        bh.consume(result);
    }

    @Benchmark
    public void stringBuilder(Blackhole bh) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 100; i++) {
            sb.append(i);  // Быстро
        }
        bh.consume(sb.toString());
    }
}
```

### Запуск

```bash
mvn clean package
java -jar target/benchmarks.jar
```

### Результат

```
Benchmark                        Mode  Cnt      Score    Error  Units
StringBenchmark.stringConcat     avgt   20  15234.567 ± 234.12  ns/op
StringBenchmark.stringBuilder    avgt   20     89.456 ±   1.23  ns/op
```

StringBuilder в **170x быстрее**.

---

## Ключевые аннотации

### @BenchmarkMode

```java
Mode.Throughput    // ops/sec — сколько операций в секунду
Mode.AverageTime   // ns/op — среднее время операции
Mode.SampleTime    // p50, p99 — распределение времени
Mode.SingleShotTime // Холодный старт (без warmup)
```

### @State — управление данными

**Scope** определяет область видимости данных:
- `Scope.Benchmark` — один экземпляр для всех потоков
- `Scope.Thread` — отдельный экземпляр для каждого потока
- `Scope.Group` — для группы потоков

**Level** определяет когда выполнять Setup/TearDown:
- `Level.Trial` — один раз на весь бенчмарк (перед/после всех итераций)
- `Level.Iteration` — перед/после каждой итерации
- `Level.Invocation` — перед/после каждого вызова (дорого!)

```java
@State(Scope.Benchmark)  // Общее для всех потоков
public class MyBenchmark {

    private List<Integer> data;

    @Setup(Level.Trial)  // Один раз перед всеми итерациями
    public void setup() {
        data = IntStream.range(0, 1_000_000)
            .boxed()
            .collect(Collectors.toList());
    }

    @Benchmark
    public int sum() {
        return data.stream().mapToInt(i -> i).sum();
    }
}
```

### @Param — параметризация

```java
@State(Scope.Benchmark)
public class CollectionBenchmark {

    @Param({"100", "1000", "10000"})
    public int size;

    private List<Integer> list;

    @Setup
    public void setup() {
        list = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            list.add(i);
        }
    }

    @Benchmark
    public int iterate() {
        int sum = 0;
        for (int x : list) sum += x;
        return sum;
    }
}
```

Результат: бенчмарк запустится для каждого размера.

---

## Типичные ловушки

### 1. Dead Code Elimination

```java
// ПЛОХО: результат не используется
@Benchmark
public void bad() {
    int result = expensiveComputation();  // JIT удалит!
}

// ХОРОШО: Blackhole "съедает" результат
@Benchmark
public void good(Blackhole bh) {
    int result = expensiveComputation();
    bh.consume(result);
}

// Или: вернуть результат
@Benchmark
public int alsoGood() {
    return expensiveComputation();
}
```

### 2. Constant Folding

```java
// ПЛОХО: JIT вычислит во время компиляции
@Benchmark
public int bad() {
    return fibonacci(10);  // JIT: "всегда 55 → return 55"
}

// ХОРОШО: переменный вход
@State(Scope.Benchmark)
public class State {
    public int n = 10;
}

@Benchmark
public int good(State s) {
    return fibonacci(s.n);  // JIT не может предвычислить
}
```

### 3. Инлайнинг скрывает overhead

```java
// JIT заинлайнит compute() → бенчмарк покажет 0 overhead
@Benchmark
public int inlined() {
    return compute(42);
}

// Если нужно измерить реальный вызов метода:
@CompilerControl(CompilerControl.Mode.DONT_INLINE)
private int compute(int x) {
    return x * x;
}
```

---

## Режимы измерения

### Throughput — ops/sec

```java
@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.SECONDS)
public void benchmark() { ... }

// Результат: 456,789 ops/s
```

### SampleTime — распределение

```java
@BenchmarkMode(Mode.SampleTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
public void benchmark() { ... }

// Результат:
// sample:p0.50   45.6 ms/op  ← Median
// sample:p0.90   78.2 ms/op
// sample:p0.99   95.4 ms/op  ← Tail latency
```

Полезно для анализа p99 latency.

### SingleShotTime — холодный старт

```java
@BenchmarkMode(Mode.SingleShotTime)
@Warmup(iterations = 0)  // БЕЗ прогрева!
@Measurement(iterations = 100)
public void coldStart() { ... }
```

Для Lambda/Serverless, где каждый вызов "холодный".

---

## Практический пример: ArrayList vs LinkedList

```java
@State(Scope.Benchmark)
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
public class ListBenchmark {

    @Param({"100", "10000"})
    public int size;

    private List<Integer> arrayList;
    private List<Integer> linkedList;

    @Setup
    public void setup() {
        arrayList = new ArrayList<>();
        linkedList = new LinkedList<>();
        for (int i = 0; i < size; i++) {
            arrayList.add(i);
            linkedList.add(i);
        }
    }

    @Benchmark
    public int arrayListGet() {
        return arrayList.get(size / 2);
    }

    @Benchmark
    public int linkedListGet() {
        return linkedList.get(size / 2);
    }

    @Benchmark
    public void arrayListIterate(Blackhole bh) {
        for (int x : arrayList) bh.consume(x);
    }

    @Benchmark
    public void linkedListIterate(Blackhole bh) {
        for (int x : linkedList) bh.consume(x);
    }
}
```

Результат (size=10000):
```
Benchmark                        Score      Units
ListBenchmark.arrayListGet       5.2        ns/op
ListBenchmark.linkedListGet      45678.3    ns/op  ← 8700x медленнее!
ListBenchmark.arrayListIterate   12345.6    ns/op
ListBenchmark.linkedListIterate  34567.8    ns/op  ← 2.8x медленнее
```

Вывод: LinkedList почти никогда не нужен.

---

## Советы

1. **Fork > 1** — запускать в разных JVM для изоляции
2. **Warmup 5+ итераций** — дать JIT время
3. **Measurement 10+ итераций** — для статистики
4. **Проверять Error** — если ±30%+, результат ненадёжен
5. **Сравнивать относительно** — абсолютные числа зависят от железа

---

## Шаблон для копирования

```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@State(Scope.Benchmark)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 10, time = 1)
@Fork(2)
public class MyBenchmark {

    // Данные
    private List<Integer> data;

    @Setup(Level.Trial)
    public void setup() {
        data = IntStream.range(0, 10000)
            .boxed()
            .collect(Collectors.toList());
    }

    @Benchmark
    public int baseline(Blackhole bh) {
        int sum = 0;
        for (int x : data) sum += x;
        return sum;
    }

    @Benchmark
    public int optimized(Blackhole bh) {
        return data.stream().mapToInt(i -> i).sum();
    }
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "System.currentTimeMillis достаточно" | JIT может **удалить код** между измерениями. JMH использует Blackhole и @CompilerControl |
| "Один warmup достаточно" | Tiered compilation требует **несколько warmup iterations**. C1 → C2 занимает время |
| "Больше iterations = точнее" | После определённого числа iterations точность не растёт. Важнее **fork** (разные JVM процессы) |
| "Микробенчмарки = реальная производительность" | Микробенчмарки изолированы. Реальный код имеет **другой профиль** (GC, contention) |
| "JMH автоматически всё сделает правильно" | JMH помогает, но **неправильный setup** всё равно даст wrong results. Dead code elimination |

---

## CS-фундамент

| CS-концепция | Применение в JMH |
|--------------|-----------------|
| **Dead Code Elimination** | JIT удаляет неиспользуемый код. Blackhole prevents DCE |
| **Constant Folding** | Компилятор вычисляет константы compile-time. @State prevents folding |
| **Statistical Significance** | Error %, confidence intervals. Нельзя сравнивать overlapping ranges |
| **JIT Warmup** | C1 → C2 tiered compilation. Без warmup измеряем interpreted code |
| **Isolation** | Fork создаёт новый JVM process. Предыдущие runs не влияют на результат |

---

## Связи

- [[jvm-performance-overview]] — когда бенчмаркинг нужен
- [[jvm-jit-compiler]] — почему warmup важен
- [[jvm-profiling]] — альтернатива: профилирование реального кода

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

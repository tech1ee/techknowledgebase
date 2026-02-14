---
title: "Java Modern Features: От Java 8 до Java 21"
created: 2025-11-25
modified: 2026-02-13
tags:
  - topic/jvm
  - lambdas
  - streams
  - records
  - virtual-threads
  - pattern-matching
  - project-loom
  - sealed-classes
  - type/concept
  - level/intermediate
type: concept
status: published
area: programming
confidence: high
sources:
  - "https://www.oracle.com/technical-resources/articles/java/architect-lambdas-part1.html"
  - "https://www.infoq.com/articles/Brian_Goetz_Project_Lambda_from_the_Inside_Interview/"
  - "https://www.infoq.com/podcasts/java-project-loom/"
  - "https://cr.openjdk.org/~rpressler/loom/loom/sol1_part1.html"
  - "https://openjdk.org/projects/amber/design-notes/records-and-sealed-classes"
  - "https://www.infoworld.com/article/2334607/project-loom-understand-the-new-java-concurrency-model.html"
  - Effective Java 3rd Edition by Joshua Bloch (2018)
  - Modern Java in Action by Raoul-Gabriel Urma (2018)
reading_time: 44
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[jvm-basics-history]]"
  - "[[jvm-virtual-machine-concept]]"
related:
  - "[[jvm-basics-history]]"
  - "[[jvm-concurrency-overview]]"
  - "[[jvm-languages-ecosystem]]"
---

# Java Modern Features: От Java 8 до Java 21

> Эволюция Java: от императивного кода к функциональному, от null checks к pattern matching, от OS threads к virtual threads.

---

## Prerequisites (Что нужно знать перед изучением)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **Базовый Java синтаксис** | Переменные, методы, классы | Любой курс по Java |
| **ООП концепции** | Наследование, интерфейсы, полиморфизм | [[jvm-basics-history]] |
| **Коллекции Java** | List, Map, Set — их использование | Java Collections Tutorial |
| **Основы многопоточности** | Понимание Thread, Runnable | [[jvm-concurrency-overview]] |
| **Что такое JVM** | Понимание компиляции и выполнения | [[jvm-virtual-machine-concept]] |

---

## Почему изучать современный Java? (История и мотивация)

### Аналогия: Java как автомобиль

> **Представьте:** Java 1.0 (1995) — это надёжный автомобиль 90-х. Он работает, но нет USB, навигатора, автопилота. Java 8 добавила "климат-контроль" (лямбды), Java 17 — "систему помощи водителю" (pattern matching), Java 21 — "электродвигатель" (virtual threads). Автомобиль остаётся узнаваемым, но становится современнее с каждым поколением.

### История эволюции Java

**2014: Java 8 — Функциональная революция**

Brian Goetz (архитектор языка Java в Oracle) объяснил почему добавили лямбды:

> *"Java SE 8 представляет самую большую эволюцию языка Java в его истории. Лямбда-выражения и method references объединяют объектно-ориентированный и функциональный стили программирования."*
> — Brian Goetz, JSR-335 Specification Lead

**Почему именно в 2014?**
- Многоядерные процессоры стали нормой (4-8 ядер)
- Конкуренты (Scala, Clojure) показали ценность FP
- Параллельная обработка требовала нового подхода
- Mark Reinhold объявил: *"Project Lambda — единственная driving feature этого релиза"*

**2017: Project Loom начинается**

Ron Pressler (тех. лид Project Loom) пришёл в Oracle после работы над Quasar (легковесные потоки через bytecode manipulation):

> *"Программисты были вынуждены выбирать: либо моделировать каждую единицу конкурентности как Thread и терять throughput, либо использовать другие способы и терять преимущества Java платформы. Оба выбора имеют значительные финансовые затраты."*
> — Ron Pressler, Project Loom Tech Lead

**2017: Java 9 — Модульность**
- Project Jigsaw решал "JAR Hell"
- JDK разбит на ~70 модулей
- Возможность создавать custom runtime

**2021: Java 17 LTS — Pattern Matching**
- Sealed classes принесли Algebraic Data Types в Java
- Компилятор теперь знает ВСЕ возможные подтипы
- Exhaustiveness checking в switch

**2023: Java 21 LTS — Concurrency революция**
- Virtual Threads: миллионы потоков вместо тысяч
- Ron Pressler: *"Virtual threads — про масштабируемость и продуктивность разработчиков"*

### Timeline эволюции Java

```
1995        2004        2011        2014        2017        2021        2023
  │           │           │           │           │           │           │
  ▼           ▼           ▼           ▼           ▼           ▼           ▼
Java 1.0   Java 5      Java 7      Java 8      Java 9      Java 17     Java 21
 (OOP)    (Generics)  (try-with)  (Lambdas)   (Modules)   (Sealed)    (Virtual
          (Autobox)   (Diamond)   (Streams)   (JShell)    (Pattern)    Threads)
                                  (Optional)              (Records)
                                  (DateTime)
  │           │           │           │           │           │           │
  └───────────┴───────────┴───────────┴───────────┴───────────┴───────────┘
                                    │
              ┌─────────────────────┴─────────────────────┐
              │       Почему такая эволюция?              │
              │  • Многоядерные CPU (параллелизм)        │
              │  • Конкуренция (Scala, Kotlin, Go)       │
              │  • Cloud native (быстрый старт)          │
              │  • Developer experience (меньше кода)    │
              └───────────────────────────────────────────┘
```

---

## Терминология для новичков

| Термин | Что это простыми словами | Аналогия |
|--------|-------------------------|----------|
| **Lambda** | Анонимная функция — код без имени | Как записка "позвони маме" вместо полного письма |
| **Functional Interface** | Интерфейс с одним абстрактным методом | Как розетка: один слот = один тип подключения |
| **Stream** | Конвейер операций над данными | Как лента на заводе: предметы проходят через станции |
| **Optional** | Контейнер, который может быть пустым | Как коробка: может содержать подарок или быть пустой |
| **Method Reference** | Ссылка на существующий метод (::) | Как "см. страницу 5" вместо переписывания |
| **Type Inference** | Компилятор сам определяет тип | Как когда продавец понимает "дайте яблоко" без уточнений |
| **Record** | Immutable data carrier | Как паспорт: данные фиксированы после создания |
| **Sealed Class** | Класс с ограниченным списком наследников | Как закрытый клуб: только приглашённые могут войти |
| **Pattern Matching** | Проверка структуры и извлечение данных | Как сортировка писем по типу конверта |
| **Virtual Thread** | Легковесный поток, управляемый JVM | Как виртуальная очередь вместо физической |
| **Module** | Явная единица кода с зависимостями | Как квартира в доме: свои стены, но общие коммуникации |
| **Text Block** | Многострочная строка (""") | Как цитата в книге вместо склейки строк |
| **Switch Expression** | Switch, который возвращает значение | Как меню в ресторане: выбрал → получил блюдо |
| **Exhaustiveness** | Компилятор проверяет все варианты | Как чек-лист: ничего не забыто |
| **Carrier Thread** | OS поток, на котором выполняется virtual thread | Как автобус, который везёт пассажиров (virtual threads) |
| **Pinning** | Virtual thread "прилипает" к carrier | Как пассажир, который не выходит из автобуса на остановке |

---

## TL;DR

**Java 8 (2014) — Функциональная революция:**
- Lambdas & Method References
- Streams API — declarative data processing
- Optional — явный null handling
- Date/Time API — замена ужасному java.util.Date

**Java 9 (2017) — Модульность:**
- Modules (Project Jigsaw) — явные зависимости
- JShell — REPL для Java

**Java 10-11 (2018) — Developer Experience:**
- `var` — локальный type inference
- HTTP Client API — замена HttpURLConnection

**Java 12-16 (2019-2021) — Синтаксический сахар:**
- Switch expressions — switch как выражение
- Text blocks — многострочные строки
- Records — immutable data carriers
- Sealed classes — ограниченная иерархия

**Java 17 (2021 LTS) — Pattern Matching:**
- Pattern matching for instanceof

**Java 21 (2023 LTS) — Concurrency революция:**
- Virtual Threads (Project Loom) — миллионы потоков
- Pattern matching for switch
- Sequenced Collections

**Adoption:**
- Java 8: 37% (legacy)
- Java 11: 29% (LTS)
- Java 17: 22% (LTS, растёт)
- Java 21: 8% (новейший LTS)

---

## Быстрая навигация

**По версии Java:**
| Версия | Главное | Перейти |
|--------|---------|---------|
| Java 8 | Lambdas, Streams, Optional | [→ Java 8](#java-8-функциональная-революция) |
| Java 9 | Modules, JShell | [→ Java 9](#java-9-модульность) |
| Java 10-11 | `var`, HTTP Client | [→ Java 10-11](#java-10-11-developer-experience) |
| Java 12-16 | Records, Sealed classes | [→ Java 12-16](#java-12-16-синтаксический-сахар) |
| Java 17 LTS | Pattern matching instanceof | [→ Java 17](#java-17-pattern-matching) |
| Java 21 LTS | Virtual Threads, Switch patterns | [→ Java 21](#java-21-concurrency-революция) |

**По задаче:**
- **Нужны функциональные коллекции?** → [Streams API](#streams-api)
- **Работаешь с null?** → [Optional](#optional)
- **Хочешь immutable data class?** → [Records](#records)
- **Нужна высокая concurrency?** → [Virtual Threads](#virtual-threads-project-loom)
- **Мигрируешь на новую версию?** → [Migration Guide](#migration-guide)

---

## Java 8: Функциональная революция

### Lambdas & Method References

**Проблема: Boilerplate Code в Anonymous Classes**

До Java 8 единственный способ передать "поведение" как параметр — anonymous classes:

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// 7 строк кода для простой операции!
Collections.sort(names, new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.compareTo(b);
    }
});
```

**Что здесь не так?**

1. **Шум** — 5 строк boilerplate (`new Comparator<String>() {`, `@Override`, etc.)
2. **Не очевидно** — что мы делаем? Сортируем? Или создаём Comparator?
3. **Плохая читаемость** — суть (`a.compareTo(b)`) затерялась в синтаксисе

**Real-world пример:** GUI обработчики событий

```java
// До Java 8: anonymous class для onClick
button.addActionListener(new ActionListener() {
    @Override
    public void actionPerformed(ActionEvent e) {
        System.out.println("Button clicked!");
    }
});

// 6 строк для одной println!
```

**Почему так происходило?**

Java до версии 8 была чисто объектно-ориентированной: "всё есть объект". Нет функций, есть только методы классов. Хотите передать поведение? Создайте объект с методом!

**Решение: Lambdas (Functional Programming)**

```java
// Java 8: Lambda — "суть без шума"
Collections.sort(names, (a, b) -> a.compareTo(b));

// Ещё короче: Method reference
Collections.sort(names, String::compareTo);

// Ещё лучше: default method в List
names.sort(String::compareTo);

// GUI обработчик
button.addActionListener(e -> System.out.println("Button clicked!"));
```

**Что изменилось?**
- 7 строк → 1 строка
- Фокус на **что делаем** (compare), а не **как объявляем** (Comparator)
- Код читается как предложение: "sort names by compareTo"

**Почему это работает? Functional Interfaces**

Lambda — это синтаксический сахар для anonymous class **с одним методом**:

```java
@FunctionalInterface  // Аннотация: "здесь только 1 abstract method"
interface Comparator<T> {
    int compare(T a, T b);  // Единственный метод
    // default и static методы — допустимы
}

// Lambda компилируется в:
Comparator<String> comparator = (a, b) -> a.compareTo(b);
// ↓ Bytecode создаёт anonymous class (но эффективнее!)
```

**Real-world кейс: Stream API**

Без lambdas Stream API был бы невозможен:

```java
// До Java 8: императивный код
List<String> result = new ArrayList<>();
for (Person person : people) {
    if (person.getAge() > 18) {
        result.add(person.getName().toUpperCase());
    }
}

// Java 8: декларативный код с lambdas
List<String> result = people.stream()
    .filter(p -> p.getAge() > 18)
    .map(Person::getName)
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

**Вывод:**

Lambdas решили проблему **boilerplate code** и открыли дорогу **functional programming** в Java. Теперь код:
- Короче (меньше шума)
- Читабельнее (фокус на бизнес-логику)
- Выразительнее (декларативный стиль)

**Functional Interfaces:**
```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

// Usage
Calculator add = (a, b) -> a + b;
Calculator multiply = (a, b) -> a * b;

System.out.println(add.calculate(5, 3));      // 8
System.out.println(multiply.calculate(5, 3)); // 15
```

**Built-in functional interfaces:**
```java
// Predicate<T> — boolean test(T t)
Predicate<String> isLong = s -> s.length() > 5;
System.out.println(isLong.test("Hello"));     // false
System.out.println(isLong.test("Hello World")); // true

// Function<T, R> — R apply(T t)
Function<String, Integer> length = String::length;
System.out.println(length.apply("Hello"));    // 5

// Consumer<T> — void accept(T t)
Consumer<String> print = System.out::println;
print.accept("Hello");

// Supplier<T> — T get()
Supplier<LocalDateTime> now = LocalDateTime::now;
System.out.println(now.get());
```

**Lambda Capture: Performance и Memory Leaks**

**Проблема:** Lambdas могут "захватывать" (capture) переменные из окружающего контекста, что создаёт hidden dependencies и memory leaks.

**Захват локальных переменных (OK):**

```java
int multiplier = 10;

// Lambda захватывает локальную переменную
Function<Integer, Integer> multiply = x -> x * multiplier;
System.out.println(multiply.apply(5));  // 50

// multiplier должна быть effectively final
// multiplier = 20;  // ОШИБКА компиляции!
```

**Что происходит под капотом:**

```java
// Lambda с захватом компилируется в:
class Lambda$1 implements Function<Integer, Integer> {
    private final int capturedMultiplier;  // Копия переменной!

    Lambda$1(int multiplier) {
        this.capturedMultiplier = multiplier;
    }

    public Integer apply(Integer x) {
        return x * capturedMultiplier;
    }
}

// Каждый вызов создаёт новый объект
Function<Integer, Integer> multiply = new Lambda$1(multiplier);
```

**Performance проблема: Захват в циклах**

```java
// BAD: Lambda создаётся в цикле, захватывает переменную
List<Runnable> tasks = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    int index = i;  // Effectively final копия
    tasks.add(() -> System.out.println("Task " + index));
    // Создаётся 1000 lambda объектов в heap!
}
// Memory: ~50KB для 1000 lambdas

// GOOD: Переиспользуем lambda или используй метод
List<Runnable> tasks = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    int index = i;
    tasks.add(createTask(index));  // Метод возвращает lambda
}

private Runnable createTask(int index) {
    return () -> System.out.println("Task " + index);
}
```

**Memory Leak: Захват `this`**

```java
public class UserService {
    private List<User> users = new ArrayList<>();  // Large list

    // BAD: Lambda захватывает this (вся UserService утечёт!)
    public Predicate<String> getEmailChecker() {
        return email -> users.stream()
            .anyMatch(u -> u.getEmail().equals(email));
        // Lambda держит ссылку на this → users не будет собран GC!
    }

    // GOOD: Явно передаём только нужные данные
    public Predicate<String> getEmailChecker() {
        Set<String> emails = users.stream()
            .map(User::getEmail)
            .collect(Collectors.toSet());  // Копия только email

        return email -> emails.contains(email);
        // Lambda держит ссылку только на Set<String>, не на весь UserService
    }
}

// Real-world сценарий
UserService service = new UserService();
service.loadUsers();  // 1 million users loaded

Predicate<String> checker = service.getEmailChecker();
service = null;  // Хотим освободить память

// BAD version: UserService + 1M users всё ещё в памяти! (через this в lambda)
// GOOD version: Только Set<String> с emails (~50MB вместо 500MB)
```

**Benchmark: Lambda Allocation Cost**

```java
// Test: 1 million lambda creations

// 1. Non-capturing lambda (singleton)
Supplier<String> lambda1 = () -> "Hello";
// Bytecode: invokedynamic + singleton instance
// Time: 0.1 ms (no allocations after first call)
// Memory: 1 объект

// 2. Capturing lambda (new instance each time)
String message = "Hello";
Supplier<String> lambda2 = () -> message;
// Bytecode: invokedynamic + new instance with captured field
// Time: 5 ms
// Memory: 1 million объектов

// 3. Method reference (no allocation)
Supplier<String> lambda3 = "Hello"::toString;
// Bytecode: direct method handle
// Time: 0.05 ms
// Memory: 0 дополнительных объектов
```

**Вывод:**

| Тип Lambda | Allocation | Performance | Use Case |
|------------|-----------|-------------|----------|
| Non-capturing `() -> "x"` | Singleton | Fastest | Константное поведение |
| Method reference `String::length` | None | Fastest | Вызов существующего метода |
| Capturing `() -> localVar` | Every call | Slow | Нужно захватить контекст |
| Capturing `this` | Every call + leak risk | Slowest | Избегать в long-lived lambdas |

**Best Practices:**

```java
// ✅ DO: Используй method references
list.forEach(System.out::println);  // Не () -> System.out.println(x)

// ✅ DO: Non-capturing lambdas в hot paths
Comparator<String> comp = (a, b) -> a.compareTo(b);

// ❌ DON'T: Захват this в listeners/callbacks
button.addListener(() -> this.handleClick());  // Memory leak risk!
// Better: передай только нужное
String handlerName = this.name;
button.addListener(() -> handleClick(handlerName));

// ❌ DON'T: Lambda allocation в циклах
for (int i = 0; i < 1000; i++) {
    executorService.submit(() -> process(i));  // 1000 allocations
}
// Better: переиспользуй или создай метод

// ✅ DO: Effectively final для clarity
int multiplier = 10;
Function<Integer, Integer> f = x -> x * multiplier;  // Clear capture
```

### Streams API

**Declarative data processing:**

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David", "Eve");

// BEFORE Java 8: Imperative (как делать)
List<String> result = new ArrayList<>();
for (String name : names) {
    if (name.length() > 3) {
        String upper = name.toUpperCase();
        result.add(upper);
    }
}
Collections.sort(result);

// AFTER Java 8: Declarative (что делать)
List<String> result = names.stream()
    .filter(name -> name.length() > 3)
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());
```

**Common operations:**

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// filter + map + collect
List<Integer> evenSquares = numbers.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .collect(Collectors.toList());
// [4, 16, 36, 64, 100]

// reduce
int sum = numbers.stream()
    .reduce(0, Integer::sum);  // 55

// findFirst
Optional<Integer> first = numbers.stream()
    .filter(n -> n > 5)
    .findFirst();  // Optional[6]

// anyMatch / allMatch / noneMatch
boolean hasEven = numbers.stream().anyMatch(n -> n % 2 == 0);  // true
boolean allPositive = numbers.stream().allMatch(n -> n > 0);   // true

// Grouping
Map<Boolean, List<Integer>> partitioned = numbers.stream()
    .collect(Collectors.partitioningBy(n -> n % 2 == 0));
// {false=[1,3,5,7,9], true=[2,4,6,8,10]}
```

**Parallel Streams:**

```java
// Sequential processing
long count = numbers.stream()
    .filter(n -> isPrime(n))
    .count();

// Parallel processing (uses ForkJoinPool)
long count = numbers.parallelStream()
    .filter(n -> isPrime(n))
    .count();
```

**Когда НЕ использовать parallelStream:**
- Small datasets (<1000 элементов)
- I/O operations (network, disk)
- Non-thread-safe operations

**Performance: Streams vs Loops**

**Вопрос:** "Streams медленнее чем loops?"

**Короткий ответ:** Зависит от операции. Для простых операций — да, медленнее. Для сложных — нет разницы или быстрее.

**Benchmark 1: Простая фильтрация**

```java
// Dataset: 1 million integers
List<Integer> numbers = IntStream.range(0, 1_000_000)
    .boxed()
    .collect(Collectors.toList());

// Test: find even numbers

// 1. For loop
List<Integer> result = new ArrayList<>();
for (Integer n : numbers) {
    if (n % 2 == 0) {
        result.add(n);
    }
}
// Time: 5 ms

// 2. Stream
List<Integer> result = numbers.stream()
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList());
// Time: 8 ms (на 60% медленнее)

// 3. Parallel stream
List<Integer> result = numbers.parallelStream()
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList());
// Time: 3 ms (на 40% быстрее!)
```

**Почему stream медленнее?**

1. **Overhead создания stream** — iterator, spliterator setup
2. **Lambda invocation cost** — каждый вызов filter/map проходит через invokedynamic
3. **Boxing/unboxing** — примитивы оборачиваются в объекты

**Решение: Primitive Streams**

```java
// BAD: Stream<Integer> — boxing overhead
int sum = numbers.stream()
    .filter(n -> n % 2 == 0)
    .mapToInt(n -> n)  // Unboxing здесь
    .sum();
// Time: 12 ms

// GOOD: IntStream — zero boxing
int sum = numbers.stream()
    .mapToInt(n -> n)  // Convert to IntStream сразу
    .filter(n -> n % 2 == 0)
    .sum();
// Time: 6 ms

// BEST: IntStream from start
int sum = IntStream.range(0, 1_000_000)
    .filter(n -> n % 2 == 0)
    .sum();
// Time: 4 ms
```

**Benchmark 2: Сложная обработка**

```java
// Test: filter + map + sort + collect
// Dataset: 100,000 Person objects

// For loop
List<String> result = new ArrayList<>();
for (Person p : people) {
    if (p.getAge() > 18) {
        result.add(p.getName().toUpperCase());
    }
}
Collections.sort(result);
// Time: 45 ms

// Stream
List<String> result = people.stream()
    .filter(p -> p.getAge() > 18)
    .map(Person::getName)
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());
// Time: 47 ms (практически одинаково)

// Parallel stream
List<String> result = people.parallelStream()
    .filter(p -> p.getAge() > 18)
    .map(Person::getName)
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());
// Time: 18 ms (в 2.5 раза быстрее!)
```

**Вывод:**

| Сценарий | For Loop | Stream | Parallel Stream |
|----------|----------|--------|-----------------|
| Простая операция (filter) | ✅ Fastest | ⚠️ 20-60% slower | ✅ Fastest (large data) |
| Сложная операция (filter+map+sort) | ✅ Fast | ≈ Same | ✅ Fastest |
| I/O операции | ✅ OK | ✅ OK | ❌ Worse |
| Small data (<1000) | ✅ Use this | ⚠️ Overhead | ❌ Don't use |

**Когда использовать Streams:**

1. **Readability важнее performance** — декларативный код читабельнее
2. **Сложные операции** — filter + map + reduce (нет overhead)
3. **Large datasets** — parallel streams дают выигрыш
4. **Functional style** — композиция операций

**Когда использовать For Loops:**

1. **Simple operations** — один filter/map
2. **Small datasets** — <1000 элементов
3. **Performance critical** — hot path в коде
4. **Early termination** — break/continue логика

**Real-world пример: API endpoint**

```java
@GetMapping("/users/active")
public List<UserDTO> getActiveUsers() {
    // BAD: Stream для всего
    return userRepository.findAll().stream()  // 1 million users
        .filter(User::isActive)                // 100K active
        .map(user -> new UserDTO(
            user.getId(),
            user.getName(),
            user.getEmail()
        ))
        .collect(Collectors.toList());
    // Time: 150ms, Memory: 500MB allocated

    // GOOD: Database filtering + simple stream
    return userRepository.findAllActive().stream()  // 100K users from DB
        .map(user -> new UserDTO(
            user.getId(),
            user.getName(),
            user.getEmail()
        ))
        .collect(Collectors.toList());
    // Time: 50ms, Memory: 150MB allocated

    // BETTER: SQL projection + for loop
    List<UserProjection> users = userRepository.findAllActiveProjection();
    List<UserDTO> result = new ArrayList<>(users.size());
    for (UserProjection u : users) {
        result.add(new UserDTO(u.getId(), u.getName(), u.getEmail()));
    }
    return result;
    // Time: 30ms, Memory: 50MB allocated
}
```

**Takeaway:**

> "Streams — это не про performance, это про readability и композицию. Используй streams когда код становится читабельнее, и loops когда нужна максимальная скорость."

**Best Practice:**

```java
// Use primitive streams when possible
IntStream.range(0, 1000)           // Not Stream<Integer>
    .filter(n -> n % 2 == 0)
    .sum();

// Avoid unnecessary boxing
list.stream()
    .mapToInt(String::length)      // IntStream, not Stream<Integer>
    .average();

// Filter in database, not in memory
userRepository.findAllActive()     // SQL WHERE
    .stream()
    .map(this::toDTO)
    .collect(Collectors.toList());

// Use parallel only for CPU-bound + large data
largeList.parallelStream()         // 100K+ elements
    .filter(this::expensiveCheck)  // CPU-intensive
    .collect(Collectors.toList());
```

### Optional — Явный Null Handling

**Проблема: The Billion Dollar Mistake**

В 2009 году Tony Hoare (изобретатель `null` в 1965) извинился:

> "I call it my billion-dollar mistake. Изобретая `null`, я не подумал о последствиях. Миллиарды долларов ущерба от ошибок и уязвимостей."

**Почему `null` — проблема?**

```java
// Казалось бы, простой код:
User user = findUser(123);
String city = user.getAddress().getCity();

// Но что может пойти не так?
// 1. findUser вернул null (пользователь не найден)
// 2. getAddress вернул null (адрес не заполнен)
// → NullPointerException!
```

**Real-world последствия:**

```
NASA Mars Climate Orbiter (1999):
    ├─ Ошибка в единицах измерения (null check пропущен)
    ├─ $327 миллионов потеряно
    └─ Спутник сгорел в атмосфере Марса

Knight Capital Group (2012):
    ├─ Deployment script с null pointer bug
    ├─ $440 миллионов потеряно за 45 минут
    └─ Компания обанкротилась

Ваше приложение (сегодня):
    ├─ Production crash at 3 AM
    ├─ Злой пользователь: "Сайт не работает!"
    └─ Вы просыпаетесь от PagerDuty alert
```

**Почему null так опасен?**

1. **Неявность** — метод не говорит "я могу вернуть null"

```java
public User findUser(int id) {
    // Вернёт User или null? Нужно читать docs или код!
    return database.query(...);
}
```

2. **Забывчивость** — легко забыть проверку

```java
User user = findUser(123);
// 500 строк кода later...
user.getName();  // Упс, забыли проверить на null!
```

3. **Цепочки вызовов** — каждый уровень может быть null

```java
// Сколько null checks нужно?
String postalCode = user.getAddress().getCity().getPostalCode();
//                   ↑1         ↑2         ↑3         ↑4
// 4 потенциальных NPE!

// Защитный код (ugly):
if (user != null) {
    Address addr = user.getAddress();
    if (addr != null) {
        City city = addr.getCity();
        if (city != null) {
            String postal = city.getPostalCode();
            if (postal != null) {
                return postal;
            }
        }
    }
}
return "Unknown";  // 11 строк для простой операции!
```

**Решение: Optional делает null ЯВНЫМ**

```java
// Сигнатура метода ЯВНО говорит: "могу вернуть пусто"
public Optional<User> findUser(int id) {
    User user = database.query(...);
    return Optional.ofNullable(user);
}

// Caller ВЫНУЖДЕН обработать случай "нет значения"
Optional<User> user = findUser(123);

// Pattern 1: orElse
String city = user
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("Unknown");

// Pattern 2: orElseGet (lazy)
String city = user
    .map(User::getAddress)
    .map(Address::getCity)
    .orElseGet(() -> getDefaultCity());

// Pattern 3: orElseThrow
String city = user
    .map(User::getAddress)
    .map(Address::getCity)
    .orElseThrow(() -> new UserNotFoundException());

// Pattern 4: ifPresent
user.ifPresent(u -> System.out.println("Found: " + u.getName()));

// Pattern 5: filter
Optional<User> adult = user.filter(u -> u.getAge() >= 18);
```

**Антипаттерны:**

```java
// BAD: isPresent + get
if (user.isPresent()) {
    return user.get().getName();  // Это как null check!
}

// GOOD: map + orElse
return user.map(User::getName).orElse("Guest");

// BAD: Optional as field
public class User {
    private Optional<Address> address;  // НЕ НАДО!
}

// GOOD: Optional only as return type
public Optional<Address> getAddress() {
    return Optional.ofNullable(address);
}
```

### CompletableFuture — Asynchronous Programming

**Проблема: Callback Hell**

До Java 8 асинхронный код был кошмаром:

```java
// До Java 8: Callback hell с Future
ExecutorService executor = Executors.newFixedThreadPool(10);

Future<User> userFuture = executor.submit(() -> fetchUser(userId));
User user = userFuture.get();  // BLOCKING! Теряем асинхронность

Future<Orders> ordersFuture = executor.submit(() -> fetchOrders(user.getId()));
Orders orders = ordersFuture.get();  // BLOCKING again!

Future<String> result = executor.submit(() -> formatOrders(orders));
String formatted = result.get();  // BLOCKING again!

// Итог: 3 blocking вызова, никакой композиции, ужасный error handling
```

**Решение: CompletableFuture с композицией**

```java
// Java 8: Композиция асинхронных операций
CompletableFuture.supplyAsync(() -> fetchUser(userId))
    .thenApply(user -> fetchOrders(user.getId()))
    .thenApply(orders -> formatOrders(orders))
    .thenAccept(formatted -> System.out.println(formatted))
    .exceptionally(ex -> {
        System.err.println("Error: " + ex.getMessage());
        return null;
    });

// Non-blocking! Весь pipeline асинхронный
```

**API Overview:**

```java
// 1. Creating CompletableFuture

// From supplier (async)
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    // Runs in ForkJoinPool.commonPool()
    return "Hello";
});

// From runnable (no result)
CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
    System.out.println("Task executed");
});

// Already completed
CompletableFuture<String> completed = CompletableFuture.completedFuture("Done");

// Manual completion
CompletableFuture<String> manual = new CompletableFuture<>();
manual.complete("Result");  // Complete manually
manual.completeExceptionally(new RuntimeException("Error"));


// 2. Transforming results

// thenApply — transform result (sync)
future.thenApply(s -> s.toUpperCase());

// thenApplyAsync — transform result (async, separate thread)
future.thenApplyAsync(s -> s.toUpperCase());

// thenCompose — flatMap (for chaining async operations)
CompletableFuture<User> userFuture = CompletableFuture.supplyAsync(() -> fetchUserId());
CompletableFuture<Orders> ordersFuture = userFuture
    .thenCompose(userId -> CompletableFuture.supplyAsync(() -> fetchOrders(userId)));


// 3. Consuming results (no return value)

// thenAccept — consume result
future.thenAccept(result -> System.out.println(result));

// thenRun — run action (ignores result)
future.thenRun(() -> System.out.println("Done"));


// 4. Combining multiple futures

// thenCombine — combine 2 futures (both succeed)
CompletableFuture<Integer> future1 = CompletableFuture.supplyAsync(() -> 10);
CompletableFuture<Integer> future2 = CompletableFuture.supplyAsync(() -> 20);

CompletableFuture<Integer> combined = future1.thenCombine(future2, (a, b) -> a + b);
// Result: 30

// allOf — wait for all (returns Void!)
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> "A");
CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> "B");
CompletableFuture<String> f3 = CompletableFuture.supplyAsync(() -> "C");

CompletableFuture<Void> all = CompletableFuture.allOf(f1, f2, f3);
all.thenRun(() -> {
    // All completed, но результатов нет!
    // Нужно вызвать f1.join(), f2.join(), f3.join()
});

// anyOf — first to complete
CompletableFuture<Object> any = CompletableFuture.anyOf(f1, f2, f3);
any.thenAccept(result -> System.out.println("First: " + result));


// 5. Error handling

// exceptionally — handle error (like catch)
future.exceptionally(ex -> {
    System.err.println("Error: " + ex.getMessage());
    return "Default value";
});

// handle — handle both success and error
future.handle((result, ex) -> {
    if (ex != null) {
        return "Error: " + ex.getMessage();
    }
    return result.toUpperCase();
});

// whenComplete — side effect (doesn't change result)
future.whenComplete((result, ex) -> {
    if (ex != null) {
        log.error("Failed", ex);
    } else {
        log.info("Success: " + result);
    }
});
```

**Real-world пример: Parallel API calls**

```java
// Task: Загрузить user, orders, и preferences параллельно

// BAD: Sequential (300ms + 200ms + 100ms = 600ms)
User user = userService.getUser(userId);           // 300ms
Orders orders = orderService.getOrders(userId);    // 200ms
Preferences prefs = prefService.getPrefs(userId);  // 100ms

// GOOD: Parallel (max(300, 200, 100) = 300ms)
CompletableFuture<User> userFuture =
    CompletableFuture.supplyAsync(() -> userService.getUser(userId));

CompletableFuture<Orders> ordersFuture =
    CompletableFuture.supplyAsync(() -> orderService.getOrders(userId));

CompletableFuture<Preferences> prefsFuture =
    CompletableFuture.supplyAsync(() -> prefService.getPrefs(userId));

// Combine results
CompletableFuture<UserDTO> result = userFuture
    .thenCombine(ordersFuture, (user, orders) -> new Pair<>(user, orders))
    .thenCombine(prefsFuture, (pair, prefs) ->
        new UserDTO(pair.getLeft(), pair.getRight(), prefs)
    );

UserDTO dto = result.join();  // Wait for result (blocking only here!)
// Total time: 300ms вместо 600ms (2x faster!)
```

**Production pattern: Timeout handling**

```java
// Problem: API call может висеть forever
CompletableFuture<String> apiFuture = CompletableFuture.supplyAsync(() ->
    slowApiCall()  // Может висеть минутами
);

// Solution: orTimeout (Java 9+)
CompletableFuture<String> withTimeout = apiFuture
    .orTimeout(5, TimeUnit.SECONDS)
    .exceptionally(ex -> {
        if (ex instanceof TimeoutException) {
            return "Timeout! Using cached data";
        }
        return "Error: " + ex.getMessage();
    });

// Alternative: completeOnTimeout (Java 9+)
CompletableFuture<String> withDefault = apiFuture
    .completeOnTimeout("Default value", 5, TimeUnit.SECONDS);
```

**Common pitfalls:**

```java
// ❌ PITFALL 1: allOf returns Void
CompletableFuture<Void> all = CompletableFuture.allOf(f1, f2, f3);
// Нет доступа к результатам!

// ✅ SOLUTION: Manual collection
CompletableFuture<List<String>> allResults = CompletableFuture.allOf(f1, f2, f3)
    .thenApply(v -> List.of(
        f1.join(),
        f2.join(),
        f3.join()
    ));


// ❌ PITFALL 2: Blocking в async pipeline
CompletableFuture.supplyAsync(() -> fetchUser())
    .thenApply(user -> {
        return orderService.getOrders(user.getId()).join();  // BLOCKING!
    });

// ✅ SOLUTION: thenCompose для вложенных futures
CompletableFuture.supplyAsync(() -> fetchUser())
    .thenCompose(user ->
        CompletableFuture.supplyAsync(() -> orderService.getOrders(user.getId()))
    );


// ❌ PITFALL 3: Exception в thenApply не обрабатывается
future.thenApply(result -> {
    if (result == null) {
        throw new RuntimeException("Null!");  // Uncaught!
    }
    return result;
});

// ✅ SOLUTION: exceptionally для обработки
future.thenApply(result -> {
    if (result == null) throw new RuntimeException("Null!");
    return result;
}).exceptionally(ex -> "Default");
```

**Performance considerations:**

```java
// ForkJoinPool.commonPool() по умолчанию (размер = CPU cores)
CompletableFuture.supplyAsync(() -> task());  // Uses common pool

// Custom executor для I/O bound задач
ExecutorService ioExecutor = Executors.newFixedThreadPool(100);
CompletableFuture.supplyAsync(() -> ioTask(), ioExecutor);

// Virtual threads (Java 21) — идеально для I/O
ExecutorService virtualExecutor = Executors.newVirtualThreadPerTaskExecutor();
CompletableFuture.supplyAsync(() -> ioTask(), virtualExecutor);
```

### Date/Time API (java.time)

**Проблема:**
```java
// До Java 8: java.util.Date (mutable, not thread-safe, 0-based months!)
Date date = new Date(2024, 11, 25);  // Год 3924! Month 12 (December)!
date.setMonth(5);  // Mutable — проблемы в многопоточности
```

**Решение:**
```java
// Java 8: java.time (immutable, thread-safe)
LocalDate date = LocalDate.of(2024, 11, 25);  // 2024-11-25
LocalTime time = LocalTime.of(14, 30, 0);     // 14:30:00
LocalDateTime dateTime = LocalDateTime.of(date, time);
ZonedDateTime zonedDateTime = ZonedDateTime.of(dateTime, ZoneId.of("Europe/Moscow"));

// Operations (immutable)
LocalDate tomorrow = date.plusDays(1);
LocalDate nextMonth = date.plusMonths(1);
LocalDate nextYear = date.plusYears(1);

// Parsing
LocalDate parsed = LocalDate.parse("2024-11-25");
LocalDateTime parsedDateTime = LocalDateTime.parse("2024-11-25T14:30:00");

// Formatting
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm");
String formatted = dateTime.format(formatter);  // "25.11.2024 14:30"

// Period & Duration
Period period = Period.between(LocalDate.of(2024, 1, 1), LocalDate.of(2024, 12, 31));
System.out.println(period.getMonths());  // 11

Duration duration = Duration.between(
    LocalTime.of(9, 0),
    LocalTime.of(17, 30)
);
System.out.println(duration.toHours());  // 8
```

---

## Java 9: Модульность

### Modules (Project Jigsaw)

**Проблема: Classpath Hell**

До Java 9 все JAR'ы просто бросались в classpath:

```bash
# Classpath nightmare
java -cp lib/gson-2.8.jar:lib/jackson-2.9.jar:lib/httpclient-4.5.jar:lib/...
    com.example.Main

# Проблемы:
# 1. Нет явных зависимостей — "какие jar'ы вообще нужны?"
# 2. Classpath scanning — медленный старт
# 3. Split packages — два jar'а могут содержать один пакет
# 4. Encapsulation — нет контроля "кто может видеть мой internal код"
# 5. Monolithic JRE — 300MB JRE даже для "Hello World"
```

**Real-world пример проблемы:**

```java
// Your code
package com.example.internal;
public class DatabaseHelper {  // Internal utility!
    public static void unsafeOperation() {
        // Dangerous method
    }
}

// Other developer's code (same application)
import com.example.internal.DatabaseHelper;  // Ничего не мешает!

DatabaseHelper.unsafeOperation();  // Использует internal API!
```

**Без модулей:**
- `internal` виден всем
- Нет compile-time ошибки
- Рефакторинг `DatabaseHelper` → ломает чужой код

**Решение: Модули делают зависимости ЯВНЫМИ**

```java
// module-info.java — манифест модуля
module com.example.myapp {
    // Зависимости (requires)
    requires java.sql;              // JDK модуль
    requires com.google.gson;       // Сторонний модуль

    // Экспорт (exports) — ЧТО видно снаружи
    exports com.example.api;        // Публичный API
    // com.example.internal — НЕ экспортирован → скрыт!

    // Открытие для reflection (opens)
    opens com.example.internal to
        com.fasterxml.jackson.databind;  // Только Jackson может reflectить
}
```

**Структура модульного приложения:**

```
myapp/
├── src/
│   ├── module-info.java              ← Module descriptor
│   └── com/
│       └── example/
│           ├── api/                  ← Exported (public API)
│           │   ├── UserService.java
│           │   └── User.java
│           └── internal/             ← Not exported (hidden)
│               ├── DatabaseHelper.java
│               └── ConfigParser.java
└── pom.xml
```

**Попытка использовать internal пакет:**

```java
// Other module trying to use internal
import com.example.internal.DatabaseHelper;  // COMPILE ERROR!

// Ошибка компиляции:
// package com.example.internal is not visible
// (package com.example.internal is declared in module com.example.myapp,
//  which does not export it)
```

**Module Directives — Полный обзор:**

```java
module com.example.myapp {
    // 1. requires — "я зависю от"
    requires java.sql;                  // Обязательная зависимость
    requires static lombok;             // Compile-time only (optional at runtime)
    requires transitive java.logging;   // Transitive (мои клиенты тоже получат)

    // 2. exports — "я экспортирую пакет всем"
    exports com.example.api;            // Public API

    // 3. exports...to — "я экспортирую пакет только определённым модулям"
    exports com.example.spi to
        com.example.plugin1,
        com.example.plugin2;

    // 4. opens — "разрешаю reflection на пакет всем"
    opens com.example.entities;         // Для JPA, Jackson, etc.

    // 5. opens...to — "разрешаю reflection только определённым модулям"
    opens com.example.internal to
        com.fasterxml.jackson.databind,
        org.hibernate.orm;

    // 6. uses — "я использую service interface"
    uses com.example.spi.PluginService;

    // 7. provides...with — "я предоставляю реализацию service"
    provides com.example.spi.PluginService
        with com.example.plugins.DefaultPlugin;
}
```

**requires transitive — Пример:**

```java
// Module A: API
module com.example.api {
    exports com.example.api;

    // API использует LocalDateTime в публичных методах
    requires transitive java.time;  // Транзитивная зависимость
}

// Module B: Client
module com.example.client {
    requires com.example.api;  // Получает и java.time автоматически!
}

// В коде Module B можно использовать LocalDateTime без requires java.time
import com.example.api.UserService;
import java.time.LocalDateTime;  // Доступен через transitive!

LocalDateTime now = LocalDateTime.now();  // Работает!
```

**Real-world пример: Modular Spring Boot Application**

```
my-spring-app/
├── app-api/                          ← API модуль
│   ├── module-info.java
│   └── com/example/api/
│       ├── UserController.java
│       └── UserDTO.java
│
├── app-service/                      ← Service модуль
│   ├── module-info.java
│   └── com/example/service/
│       ├── UserService.java
│       └── internal/
│           └── UserValidator.java
│
├── app-repository/                   ← Repository модуль
│   ├── module-info.java
│   └── com/example/repository/
│       ├── UserRepository.java
│       └── entity/
│           └── UserEntity.java
│
└── app-main/                         ← Main модуль
    ├── module-info.java
    └── com/example/
        └── Application.java
```

**app-api/module-info.java:**

```java
module app.api {
    // Spring dependencies
    requires spring.web;
    requires spring.context;

    // Наш сервис слой
    requires transitive app.service;  // Transitive — клиенты получат service

    // Экспорт
    exports com.example.api;          // Controller и DTO

    // Reflection для Spring
    opens com.example.api to spring.core;
}
```

**app-service/module-info.java:**

```java
module app.service {
    requires spring.context;
    requires app.repository;          // Зависимость от repository

    // Экспорт
    exports com.example.service;      // Public service API
    // com.example.service.internal — НЕ экспортирован (скрыт)

    // Reflection для Spring
    opens com.example.service to spring.core;
}
```

**app-repository/module-info.java:**

```java
module app.repository {
    requires spring.data.jpa;
    requires java.persistence;        // JPA API

    // Экспорт
    exports com.example.repository;   // Repository interfaces
    exports com.example.repository.entity;  // JPA entities

    // Reflection для JPA и Spring
    opens com.example.repository.entity to
        org.hibernate.orm,
        spring.core;
}
```

**app-main/module-info.java:**

```java
module app.main {
    requires spring.boot;
    requires spring.boot.autoconfigure;
    requires app.api;                 // Подключаем все слои через api

    // Reflection для Spring Boot
    opens com.example to spring.core, spring.beans;
}
```

**Преимущества модульного подхода:**

| Без модулей | С модулями |
|-------------|------------|
| `UserValidator` виден всем | `UserValidator` скрыт в `internal` |
| Неясно "какие зависимости нужны" | Явные `requires` в `module-info.java` |
| Можно случайно вызвать internal API | Compile error при попытке |
| Classpath scanning — медленный старт | Module path — быстрый старт |
| 300MB JRE для "Hello World" | jlink → 30MB custom runtime |

**jlink — Custom Runtime для Production:**

```bash
# 1. Compile модули
javac -d mods --module-source-path src $(find src -name "*.java")

# 2. Создать custom runtime с только нужными модулями
jlink --module-path $JAVA_HOME/jmods:mods \
      --add-modules app.main \
      --launcher myapp=app.main/com.example.Application \
      --output myapp-runtime

# 3. Запуск
./myapp-runtime/bin/myapp

# Результат:
# - JRE: 300MB → 35MB (8.5x меньше!)
# - Startup time: 2s → 0.5s (4x быстрее)
# - Memory: только нужные модули загружены
```

**Docker image с jlink:**

```dockerfile
# Build stage
FROM eclipse-temurin:21-jdk as builder
WORKDIR /app
COPY . .
RUN ./mvnw clean package
RUN jlink --module-path target/modules:$JAVA_HOME/jmods \
          --add-modules app.main \
          --output /custom-jre

# Runtime stage
FROM debian:bookworm-slim
COPY --from=builder /custom-jre /opt/jre
COPY --from=builder /app/target/app.jar /app/app.jar

CMD ["/opt/jre/bin/java", "-jar", "/app/app.jar"]

# Image size: 450MB → 80MB (5.6x smaller!)
```

**Migration: Classpath → Module Path**

**Step 1: Automatic modules (промежуточный шаг)**

Если библиотека ещё не модульная — она становится "automatic module":

```java
// Ваш модуль
module my.app {
    requires gson;  // gson.jar не модульный, но работает как "gson" automatic module
}
```

**Step 2: Top-down migration**

```
1. Main app → модуль
2. Libraries → постепенно мигрируй
3. Legacy JARs → automatic modules
```

**Step 3: Модульный JAR**

```xml
<!-- Maven: создать модульный JAR -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <release>21</release>
    </configuration>
</plugin>

<!-- JAR будет содержать module-info.class -->
```

**Проверка:**

```bash
# Проверить модульность JAR
jar --describe-module --file myapp.jar

# Вывод:
# myapp@1.0.0
# requires java.base
# requires java.sql
# exports com.example.api
```

### JShell — REPL для Java

```bash
$ jshell
|  Welcome to JShell -- Version 21

jshell> int x = 10
x ==> 10

jshell> x * 2
$2 ==> 20

jshell> List<String> names = List.of("Alice", "Bob")
names ==> [Alice, Bob]

jshell> names.stream().map(String::toUpperCase).toList()
$4 ==> [ALICE, BOB]

jshell> /exit
```

---

## Java 10-11: Developer Experience

### var — Local Variable Type Inference

```java
// BEFORE Java 10
Map<String, List<Integer>> map = new HashMap<String, List<Integer>>();

// AFTER Java 10: var
var map = new HashMap<String, List<Integer>>();

// Примеры
var name = "Alice";  // String
var age = 30;        // int
var list = new ArrayList<String>();  // ArrayList<String>
var stream = list.stream();          // Stream<String>

// Полезно для длинных типов
var factory = new ComplexGenericFactoryBuilder<Something, SomethingElse>()
    .withConfig(config)
    .build();
```

**Ограничения:**

```java
// НЕЛЬЗЯ: без инициализации
var x;  // ОШИБКА

// НЕЛЬЗЯ: null
var x = null;  // ОШИБКА (тип неизвестен)

// НЕЛЬЗЯ: lambda без явного типа
var lambda = x -> x + 1;  // ОШИБКА

// МОЖНО: lambda с явным типом
var lambda = (Function<Integer, Integer>) x -> x + 1;

// НЕЛЬЗЯ: поля класса
class User {
    var name = "Alice";  // ОШИБКА
}

// МОЖНО: только локальные переменные
```

### HTTP Client API

**BEFORE Java 11: HttpURLConnection (ужасный API)**

```java
URL url = new URL("https://api.example.com/users");
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("Accept", "application/json");

int responseCode = conn.getResponseCode();
BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
String inputLine;
StringBuilder response = new StringBuilder();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
// 15+ строк для простого GET запроса!
```

**AFTER Java 11: HTTP Client**

```java
// Synchronous
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Accept", "application/json")
    .GET()
    .build();

HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.body());

// Asynchronous
client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
    .thenApply(HttpResponse::body)
    .thenAccept(System.out::println)
    .join();

// POST with JSON
HttpRequest postRequest = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString("{\"name\":\"Alice\"}"))
    .build();
```

---

## Java 12-16: Синтаксический сахар

### Switch Expressions (Java 14)

**BEFORE: switch statement**

```java
String day = "MONDAY";
int numLetters;
switch (day) {
    case "MONDAY":
    case "FRIDAY":
    case "SUNDAY":
        numLetters = 6;
        break;
    case "TUESDAY":
        numLetters = 7;
        break;
    case "THURSDAY":
    case "SATURDAY":
        numLetters = 8;
        break;
    case "WEDNESDAY":
        numLetters = 9;
        break;
    default:
        throw new IllegalArgumentException("Invalid day: " + day);
}
```

**AFTER: switch expression**

```java
int numLetters = switch (day) {
    case "MONDAY", "FRIDAY", "SUNDAY" -> 6;
    case "TUESDAY" -> 7;
    case "THURSDAY", "SATURDAY" -> 8;
    case "WEDNESDAY" -> 9;
    default -> throw new IllegalArgumentException("Invalid day: " + day);
};

// Или с yield для блоков
int numLetters = switch (day) {
    case "MONDAY", "FRIDAY", "SUNDAY" -> {
        System.out.println("6 letters");
        yield 6;
    }
    case "TUESDAY" -> {
        System.out.println("7 letters");
        yield 7;
    }
    default -> throw new IllegalArgumentException("Invalid day: " + day);
};
```

### Text Blocks (Java 15)

**BEFORE: String concatenation**

```java
String json = "{\n" +
              "  \"name\": \"Alice\",\n" +
              "  \"age\": 30,\n" +
              "  \"city\": \"New York\"\n" +
              "}";

String sql = "SELECT id, name, email\n" +
             "FROM users\n" +
             "WHERE age > 18\n" +
             "ORDER BY name";
```

**AFTER: Text blocks**

```java
String json = """
    {
      "name": "Alice",
      "age": 30,
      "city": "New York"
    }
    """;

String sql = """
    SELECT id, name, email
    FROM users
    WHERE age > 18
    ORDER BY name
    """;

// Форматирование
String message = """
    Hello %s,
    Your balance is $%.2f
    """.formatted(name, balance);
```

### Records (Java 16)

**BEFORE: Data classes**

```java
public class User {
    private final String name;
    private final int age;

    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String name() { return name; }
    public int age() { return age; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return age == user.age && Objects.equals(name, user.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }

    @Override
    public String toString() {
        return "User[name=" + name + ", age=" + age + "]";
    }
}
// 30+ строк кода!
```

**AFTER: Records**

```java
public record User(String name, int age) {}
// 1 строка! Автоматически:
// - Constructor
// - Getters (name(), age())
// - equals(), hashCode(), toString()

// Usage
User user = new User("Alice", 30);
System.out.println(user.name());  // Alice
System.out.println(user);         // User[name=Alice, age=30]

// Pattern matching (Java 21)
if (user instanceof User(String name, int age)) {
    System.out.println(name + " is " + age);
}

// Custom methods
public record User(String name, int age) {
    // Compact constructor (validation)
    public User {
        if (age < 0) throw new IllegalArgumentException("Age must be positive");
    }

    // Custom methods
    public boolean isAdult() {
        return age >= 18;
    }
}
```

### Sealed Classes (Java 17)

**Ограниченная иерархия классов.**

```java
// Sealed interface — только разрешённые реализации
public sealed interface Shape
    permits Circle, Rectangle, Triangle {}

public final class Circle implements Shape {
    private final double radius;
    // ...
}

public final class Rectangle implements Shape {
    private final double width, height;
    // ...
}

public final class Triangle implements Shape {
    private final double a, b, c;
    // ...
}

// Попытка создать другую реализацию — ОШИБКА компиляции
// public class Square implements Shape {} // ERROR!
```

**Преимущества:**
- Exhaustiveness checking в pattern matching
- Явный API — все варианты известны

```java
double area(Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        case Triangle t -> /* Heron's formula */ 0.0;
        // Нет default — компилятор знает все варианты!
    };
}
```

---

## Java 17: Pattern Matching

### Pattern Matching for instanceof

**BEFORE:**

```java
if (obj instanceof String) {
    String str = (String) obj;  // Explicit cast
    System.out.println(str.toUpperCase());
}
```

**AFTER:**

```java
if (obj instanceof String str) {
    System.out.println(str.toUpperCase());  // No cast needed
}

// Можно с условием
if (obj instanceof String str && str.length() > 5) {
    System.out.println(str.toUpperCase());
}
```

**Пример с иерархией:**

```java
sealed interface Animal permits Cat, Dog {}
record Cat(String name) implements Animal {}
record Dog(String name, String breed) implements Animal {}

String describe(Animal animal) {
    if (animal instanceof Cat cat) {
        return "Cat named " + cat.name();
    } else if (animal instanceof Dog dog) {
        return "Dog named " + dog.name() + " (" + dog.breed() + ")";
    }
    throw new IllegalArgumentException();
}
```

---

## Java 21: Concurrency революция

### Virtual Threads (Project Loom)

**Проблема OS Threads:**
- Тяжёлые: 1MB stack per thread
- Ограничены: ~10,000 threads max
- Context switching overhead

**Решение: Virtual Threads**

```java
// BEFORE: Platform threads (OS threads)
ExecutorService executor = Executors.newFixedThreadPool(100);
for (int i = 0; i < 10000; i++) {
    executor.submit(() -> {
        // Только 100 одновременно — остальные в очереди
        handleRequest();
    });
}

// AFTER: Virtual threads
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 10000; i++) {
        executor.submit(() -> {
            // 10,000 virtual threads одновременно!
            handleRequest();
        });
    }
}  // auto-close waits for all tasks

// Простое создание
Thread.startVirtualThread(() -> {
    System.out.println("Hello from virtual thread!");
});

// Thread.ofVirtual()
Thread vThread = Thread.ofVirtual()
    .name("worker-", 0)
    .start(() -> handleRequest());
```

**Производительность:**

```java
// Benchmark: 100,000 HTTP requests
// Platform threads (100 threads): 10 seconds
// Virtual threads (100,000 threads): 2 seconds

try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 100_000).forEach(i -> {
        executor.submit(() -> {
            // Blocking I/O — OK с virtual threads!
            String response = httpClient.send(request, BodyHandlers.ofString()).body();
            processResponse(response);
        });
    });
}
```

**Когда использовать:**
- ✅ I/O-bound операции (HTTP, DB, File I/O)
- ✅ Blocking code (Thread.sleep, blocking queues)
- ❌ CPU-bound операции (используй ForkJoinPool)

**Как работает:**

```
┌──────────────────────────────────────────────────────┐
│        Virtual Threads Architecture                  │
└──────────────────────────────────────────────────────┘

10,000 Virtual Threads
       │
       │ Mapped to
       ▼
ForkJoinPool (N carrier threads = CPU cores)
       │
       │ Scheduled on
       ▼
OS Platform Threads (8-16 threads)

Blocking operation → virtual thread unmounted from carrier
                  → carrier thread picks another virtual thread
```

**CRITICAL: Thread Pinning Problem**

**Проблема:** Virtual thread может "приколоться" (pin) к carrier thread и БЛОКИРОВАТЬ его!

**Когда происходит pinning:**

1. **synchronized блок** — virtual thread НЕ МОЖЕТ unmount
2. **Native method call** — вызов JNI кода

```java
// ❌ BAD: synchronized блокирует carrier thread
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

for (int i = 0; i < 100_000; i++) {
    executor.submit(() -> {
        synchronized (lock) {  // PINNING! Virtual thread НЕ unmount'ится
            // Blocking I/O внутри synchronized
            String data = httpClient.send(request);  // 100ms
            // Carrier thread БЛОКИРОВАН на 100ms!
        }
    });
}

// Проблема: Если 8 CPU cores → только 8 HTTP запросов одновременно
// 100,000 virtual threads НЕ РАБОТАЮТ параллельно!
// Throughput: 8 requests/100ms = 80 req/sec (ужасно!)
```

**Почему synchronized блокирует?**

JVM не может unmount virtual thread из synchronized блока, т.к.:
- Monitor (intrinsic lock) — JVM internal структура
- Не поддерживает "снять lock и восстановить позже"
- Virtual thread ПРИВЯЗАН к carrier thread на время synchronized

**Решение: ReentrantLock вместо synchronized**

```java
// ✅ GOOD: ReentrantLock поддерживает unmounting
private final Lock lock = new ReentrantLock();

for (int i = 0; i < 100_000; i++) {
    executor.submit(() -> {
        lock.lock();  // NO pinning!
        try {
            String data = httpClient.send(request);  // 100ms
            // Virtual thread может unmount во время I/O!
        } finally {
            lock.unlock();
        }
    });
}

// Throughput: 100,000 virtual threads работают параллельно
// Реальный throughput: ограничен только сетью, не CPU cores
```

**Benchmark: synchronized vs ReentrantLock с Virtual Threads**

```java
// Test: 10,000 HTTP requests с блокировкой

// 1. Platform threads + synchronized
ExecutorService platform = Executors.newFixedThreadPool(100);
// Throughput: 100 requests одновременно
// Time: 100 seconds (10,000 / 100)

// 2. Virtual threads + synchronized (PINNING!)
ExecutorService virtual = Executors.newVirtualThreadPerTaskExecutor();
synchronized (lock) {
    httpClient.send(request);  // Pinning к 8 carrier threads
}
// Throughput: 8 requests одновременно (8 CPU cores)
// Time: 125 seconds (10,000 / 8)  ← МЕДЛЕННЕЕ чем platform threads!

// 3. Virtual threads + ReentrantLock (NO pinning)
ReentrantLock reentrantLock = new ReentrantLock();
reentrantLock.lock();
try {
    httpClient.send(request);  // No pinning
} finally {
    reentrantLock.unlock();
}
// Throughput: 10,000 requests одновременно
// Time: 1 second (limited by network)  ← 100x БЫСТРЕЕ!
```

**Real-world катастрофа:**

```java
// Production код до Virtual Threads
@Service
public class UserService {
    private final Map<String, User> cache = new ConcurrentHashMap<>();

    // synchronized для thread-safety
    public synchronized User getUser(String id) {
        User cached = cache.get(id);
        if (cached != null) return cached;

        // Blocking database call
        User user = userRepository.findById(id);  // 50ms
        cache.put(id, user);
        return user;
    }
}

// Миграция на Virtual Threads
// Before: 200 platform threads → 1000 req/sec
// After: 100,000 virtual threads → 160 req/sec (!!)

// WHY? synchronized pinning!
// 8 carrier threads → только 8 requests одновременно
// 8 * (1000ms / 50ms) = 160 req/sec

// Fix: заменить synchronized на ReentrantLock
```

**Detecting Pinning в Production:**

```java
// JVM flag для логирования pinning
java -Djdk.tracePinnedThreads=full MyApp

// Output:
// Thread[#123,ForkJoinPool-1-worker-1,5,CarrierThreads]
//     java.base/java.lang.VirtualThread$VThreadContinuation.onPinned
//     java.base/java.lang.VirtualThread.parkOnCarrierThread
//     MyApp.getUser(UserService.java:42)  ← synchronized здесь!
```

**Миграция synchronized → ReentrantLock:**

```java
// BEFORE: synchronized
private final Object lock = new Object();

public void method() {
    synchronized (lock) {
        // ...
    }
}

// AFTER: ReentrantLock
private final Lock lock = new ReentrantLock();

public void method() {
    lock.lock();
    try {
        // ...
    } finally {
        lock.unlock();  // ВАЖНО: finally!
    }
}
```

**Collections pinning:**

```java
// ❌ BAD: Vector, Hashtable используют synchronized
Vector<String> vector = new Vector<>();  // synchronized methods!
vector.add("item");  // PINNING!

Hashtable<String, String> table = new Hashtable<>();  // synchronized!
table.put("key", "value");  // PINNING!

// ✅ GOOD: ConcurrentHashMap, CopyOnWriteArrayList
ConcurrentHashMap<String, String> map = new ConcurrentHashMap<>();
map.put("key", "value");  // No pinning

CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("item");  // No pinning
```

**Production checklist для Virtual Threads:**

```java
// ❌ Избегать:
synchronized (lock) { ... }           // Use ReentrantLock
Vector, Hashtable, StringBuffer      // Use concurrent collections
Collections.synchronizedList()        // Use CopyOnWriteArrayList
synchronized методы                   // Use locks or concurrent structures

// ✅ Использовать:
ReentrantLock, ReadWriteLock
ConcurrentHashMap
CopyOnWriteArrayList
AtomicInteger, AtomicReference
LockSupport.park/unpark              // Virtual-thread aware
```

**Performance сравнение:**

| Scenario | Platform Threads (200) | Virtual Threads + synchronized | Virtual Threads + ReentrantLock |
|----------|------------------------|--------------------------------|--------------------------------|
| 10K HTTP requests (100ms each) | 50 sec | 125 sec (WORSE!) | 1 sec (50x faster) |
| Memory | 200MB (thread stacks) | 10MB (virtual threads) | 10MB |
| Throughput | 200 concurrent | 8 concurrent (pinned!) | 10,000 concurrent |

**Вывод:**

> **Virtual Threads + synchronized = КАТАСТРОФА!**
>
> Миграция на Virtual Threads БЕЗ замены synchronized → деградация performance в 2-3 раза.
>
> Всегда используй ReentrantLock для Virtual Threads!

### Pattern Matching for switch (Java 21)

```java
// BEFORE: instanceof chain
String describe(Object obj) {
    if (obj instanceof Integer i) {
        return "Integer: " + i;
    } else if (obj instanceof String s) {
        return "String: " + s;
    } else if (obj instanceof List list) {
        return "List of size: " + list.size();
    } else {
        return "Unknown";
    }
}

// AFTER: switch with pattern matching
String describe(Object obj) {
    return switch (obj) {
        case Integer i -> "Integer: " + i;
        case String s -> "String: " + s;
        case List list -> "List of size: " + list.size();
        case null -> "Null value";
        default -> "Unknown";
    };
}

// With guards
String categorize(Object obj) {
    return switch (obj) {
        case String s when s.length() > 10 -> "Long string";
        case String s -> "Short string";
        case Integer i when i > 100 -> "Large number";
        case Integer i -> "Small number";
        default -> "Other";
    };
}

// Record patterns (deconstruction)
record Point(int x, int y) {}

String locate(Object obj) {
    return switch (obj) {
        case Point(int x, int y) when x == 0 && y == 0 -> "Origin";
        case Point(int x, int y) when x == 0 -> "Y-axis";
        case Point(int x, int y) when y == 0 -> "X-axis";
        case Point(int x, int y) -> "Point at (" + x + ", " + y + ")";
        default -> "Not a point";
    };
}
```

**Advanced Pattern Matching: Nested Patterns**

```java
// Domain model
sealed interface Shape permits Circle, Rectangle {}
record Circle(Point center, double radius) implements Shape {}
record Rectangle(Point topLeft, Point bottomRight) implements Shape {}
record Point(double x, double y) {}

// Nested pattern matching
String describe(Shape shape) {
    return switch (shape) {
        // Nested destructuring: Shape → Point → coordinates
        case Circle(Point(double x, double y), double r) ->
            "Circle at (" + x + ", " + y + ") with radius " + r;

        case Rectangle(Point(double x1, double y1), Point(double x2, double y2)) ->
            "Rectangle from (" + x1 + ", " + y1 + ") to (" + x2 + ", " + y2 + ")";
    };
}

// Example
Shape circle = new Circle(new Point(0, 0), 5);
System.out.println(describe(circle));
// "Circle at (0.0, 0.0) with radius 5.0"
```

**Real-world пример: JSON-like структура**

```java
// Domain model для JSON
sealed interface JsonValue permits
    JsonObject, JsonArray, JsonString, JsonNumber, JsonBoolean, JsonNull {}

record JsonObject(Map<String, JsonValue> fields) implements JsonValue {}
record JsonArray(List<JsonValue> elements) implements JsonValue {}
record JsonString(String value) implements JsonValue {}
record JsonNumber(double value) implements JsonValue {}
record JsonBoolean(boolean value) implements JsonValue {}
record JsonNull() implements JsonValue {}

// Парсинг с pattern matching
Object parse(JsonValue json) {
    return switch (json) {
        case JsonString(String s) -> s;
        case JsonNumber(double d) -> d;
        case JsonBoolean(boolean b) -> b;
        case JsonNull() -> null;
        case JsonArray(List<JsonValue> elements) ->
            elements.stream().map(this::parse).toList();
        case JsonObject(Map<String, JsonValue> fields) ->
            fields.entrySet().stream()
                .collect(Collectors.toMap(
                    Map.Entry::getKey,
                    e -> parse(e.getValue())
                ));
    };
}

// Поиск значения по пути
Optional<String> findString(JsonValue json, String path) {
    return switch (json) {
        case JsonObject(var fields) when fields.containsKey(path) ->
            switch (fields.get(path)) {
                case JsonString(String s) -> Optional.of(s);
                default -> Optional.empty();
            };
        default -> Optional.empty();
    };
}

// Usage
JsonValue user = new JsonObject(Map.of(
    "name", new JsonString("Alice"),
    "age", new JsonNumber(30),
    "active", new JsonBoolean(true)
));

Optional<String> name = findString(user, "name");  // Optional["Alice"]
```

**Производительность Pattern Matching:**

```java
// Benchmark: 1 million pattern matches

// 1. instanceof chain (старый способ)
if (obj instanceof String s) {
    return s.length();
} else if (obj instanceof Integer i) {
    return i;
} else if (obj instanceof List<?> list) {
    return list.size();
}
// Time: 15 ms

// 2. switch с pattern matching
return switch (obj) {
    case String s -> s.length();
    case Integer i -> i;
    case List<?> list -> list.size();
    default -> 0;
};
// Time: 12 ms (на 20% быстрее)

// Компилятор генерирует tableswitch/lookupswitch для оптимизации
```

---

## Combining Modern Features: Algebraic Data Types

**Проблема:** Моделирование domain в типах

До современного Java:

```java
// Старый подход: inheritance hell
class Result {
    private Object value;
    private Exception error;
    private boolean isSuccess;

    // Конструктор, getters, setters...
    // Проблемы:
    // - Можно создать invalid state (value И error одновременно)
    // - Нужны runtime проверки
    // - Нет compile-time гарантий
}
```

**Решение: Records + Sealed Classes + Pattern Matching**

```java
// Domain: Result может быть Success ИЛИ Failure
sealed interface Result<T> permits Success, Failure {}

record Success<T>(T value) implements Result<T> {}
record Failure<T>(Exception error) implements Result<T> {}

// Usage с pattern matching
<T> String handle(Result<T> result) {
    return switch (result) {
        case Success<T>(T value) -> "Got: " + value;
        case Failure<T>(Exception error) -> "Error: " + error.getMessage();
    };
    // Компилятор ЗНАЕТ все варианты — exhaustiveness checking!
}

// Создание
Result<String> success = new Success<>("Hello");
Result<String> failure = new Failure<>(new RuntimeException("Oops"));

System.out.println(handle(success));  // "Got: Hello"
System.out.println(handle(failure));  // "Error: Oops"

// НЕВОЗМОЖНО создать invalid state:
// new Success(value, error)  // COMPILE ERROR: нет такого конструктора
```

**Real-world пример: Payment Processing**

```java
// Domain model
sealed interface PaymentResult permits
    PaymentSuccess, PaymentDeclined, PaymentError, PaymentPending {}

record PaymentSuccess(String transactionId, double amount) implements PaymentResult {}
record PaymentDeclined(String reason) implements PaymentResult {}
record PaymentError(Exception cause) implements PaymentResult {}
record PaymentPending(String referenceId) implements PaymentResult {}

// Business logic
class PaymentService {
    public PaymentResult processPayment(PaymentRequest request) {
        try {
            // Payment gateway API call
            GatewayResponse response = gateway.charge(request);

            return switch (response.status()) {
                case "approved" -> new PaymentSuccess(
                    response.transactionId(),
                    request.amount()
                );
                case "declined" -> new PaymentDeclined(response.reason());
                case "pending" -> new PaymentPending(response.referenceId());
                default -> new PaymentError(
                    new IllegalStateException("Unknown status: " + response.status())
                );
            };
        } catch (Exception e) {
            return new PaymentError(e);
        }
    }

    // Обработка результата
    public void handlePayment(PaymentResult result) {
        switch (result) {
            case PaymentSuccess(String txId, double amount) -> {
                log.info("Payment successful: {} for ${}", txId, amount);
                sendConfirmationEmail(txId);
                updateOrderStatus(txId, "PAID");
            }
            case PaymentDeclined(String reason) -> {
                log.warn("Payment declined: {}", reason);
                notifyCustomer("Payment declined: " + reason);
            }
            case PaymentError(Exception cause) -> {
                log.error("Payment error", cause);
                rollbackTransaction();
                notifyAdmins(cause);
            }
            case PaymentPending(String refId) -> {
                log.info("Payment pending: {}", refId);
                scheduleStatusCheck(refId);
            }
        };
        // Exhaustiveness checking — все случаи обработаны!
        // Добавили новый тип? Компилятор скажет где обновить код
    }
}
```

**Сравнение с Optional:**

```java
// Optional — специальный случай Result<T> без ошибки
sealed interface Maybe<T> permits Some, None {}
record Some<T>(T value) implements Maybe<T> {}
record None<T>() implements Maybe<T> {}

// Использование
Maybe<User> maybeUser = findUser(123);

String name = switch (maybeUser) {
    case Some<User>(User user) -> user.getName();
    case None<User>() -> "Unknown";
};

// vs Optional
Optional<User> optionalUser = findUser(123);
String name = optionalUser.map(User::getName).orElse("Unknown");

// Maybe дает больше контроля и clarity через explicit types
```

**Tree структуры с pattern matching:**

```java
// Binary tree
sealed interface Tree<T> permits Leaf, Node {}
record Leaf<T>() implements Tree<T> {}
record Node<T>(T value, Tree<T> left, Tree<T> right) implements Tree<T> {}

// Depth calculation
<T> int depth(Tree<T> tree) {
    return switch (tree) {
        case Leaf<T>() -> 0;
        case Node<T>(T v, Tree<T> left, Tree<T> right) ->
            1 + Math.max(depth(left), depth(right));
    };
}

// Sum (для числовых деревьев)
int sum(Tree<Integer> tree) {
    return switch (tree) {
        case Leaf<Integer>() -> 0;
        case Node<Integer>(Integer value, var left, var right) ->
            value + sum(left) + sum(right);
    };
}

// Example
Tree<Integer> tree = new Node<>(5,
    new Node<>(3,
        new Leaf<>(),
        new Leaf<>()
    ),
    new Node<>(8,
        new Leaf<>(),
        new Leaf<>()
    )
);

System.out.println(depth(tree));  // 2
System.out.println(sum(tree));    // 16
```

**State Machine с sealed types:**

```java
// Order states
sealed interface OrderState permits
    Created, PaymentPending, Paid, Shipped, Delivered, Cancelled {}

record Created(String orderId) implements OrderState {}
record PaymentPending(String orderId, String paymentUrl) implements OrderState {}
record Paid(String orderId, String transactionId) implements OrderState {}
record Shipped(String orderId, String trackingNumber) implements OrderState {}
record Delivered(String orderId, LocalDateTime deliveryTime) implements OrderState {}
record Cancelled(String orderId, String reason) implements OrderState {}

// State transitions (compile-time checked!)
OrderState processPayment(OrderState state, String transactionId) {
    return switch (state) {
        case Created(String orderId) ->
            new Paid(orderId, transactionId);  // Valid transition
        case PaymentPending(String orderId, String url) ->
            new Paid(orderId, transactionId);  // Valid transition
        case Paid p -> p;  // Already paid, no change
        case Shipped s -> s;  // Can't pay after shipping
        case Delivered d -> d;  // Can't pay after delivery
        case Cancelled c -> c;  // Can't pay cancelled order
    };
}

// Компилятор гарантирует: все состояния обработаны!
```

**Преимущества Algebraic Data Types в Java:**

| Аспект | Старый подход | Records + Sealed + Pattern Matching |
|--------|---------------|-------------------------------------|
| Type safety | Runtime checks | Compile-time checks |
| Invalid states | Возможны | Невозможны (by construction) |
| Exhaustiveness | Нет гарантий | Compiler-checked |
| Refactoring | Сложно (runtime errors) | Просто (compile errors показывают где менять) |
| Readability | if/else chains | Declarative switch |
| Performance | Runtime type checks | Tableswitch (fast) |

**Вывод:**

> **Records + Sealed Classes + Pattern Matching = Algebraic Data Types**
>
> Java 21 позволяет моделировать domain так же выразительно, как Scala/Kotlin/Haskell,
> но с гарантиями compile-time и без reflection overhead.

### Sequenced Collections (Java 21)

**Проблема: нет общего API для "упорядоченных" коллекций.**

```java
// BEFORE: Разные API
List<String> list = new ArrayList<>();
Deque<String> deque = new ArrayDeque<>();
SortedSet<String> sortedSet = new TreeSet<>();

// Получить первый элемент
list.get(0);           // List
deque.getFirst();      // Deque
sortedSet.first();     // SortedSet

// Получить последний элемент
list.get(list.size() - 1);  // List
deque.getLast();            // Deque
sortedSet.last();           // SortedSet
```

**AFTER: SequencedCollection**

```java
// Java 21: Унифицированный API
interface SequencedCollection<E> extends Collection<E> {
    SequencedCollection<E> reversed();
    void addFirst(E e);
    void addLast(E e);
    E getFirst();
    E getLast();
    E removeFirst();
    E removeLast();
}

// Использование
List<String> list = new ArrayList<>(List.of("A", "B", "C"));
list.addFirst("Z");     // [Z, A, B, C]
list.addLast("D");      // [Z, A, B, C, D]
String first = list.getFirst();  // Z
String last = list.getLast();    // D

// Reversed view (не создаёт копию!)
List<String> reversed = list.reversed();  // [D, C, B, A, Z]
```

---

## Migration Guide

### Java 8 → Java 11

**Changes:**
- Modules (optional, но default в новых проектах)
- Removed: Java EE modules (JAXB, JAX-WS → добавить вручную)

```xml
<!-- Add missing modules -->
<dependency>
    <groupId>jakarta.xml.bind</groupId>
    <artifactId>jakarta.xml.bind-api</artifactId>
    <version>3.0.0</version>
</dependency>
```

### Java 11 → Java 17

**Changes:**
- Removed: Nashorn JavaScript engine
- Sealed classes доступны
- Strong encapsulation of JDK internals (нельзя использовать sun.* пакеты)

```bash
# If code uses internal APIs
java --add-opens java.base/java.lang=ALL-UNNAMED MyApp
```

### Java 17 → Java 21

**Changes:**
- Virtual Threads — нужно переписать thread pools
- Pattern matching — refactor instanceof chains

```java
// Refactor thread pools
// BEFORE
ExecutorService executor = Executors.newFixedThreadPool(200);

// AFTER (for I/O bound)
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
```

---

## Чеклист: Modern Java

**Java 8:**
- [ ] Использую lambdas вместо anonymous classes
- [ ] Использую Streams вместо for loops (где читабельно)
- [ ] Использую Optional для nullable возвращаемых значений
- [ ] Перешёл с java.util.Date на java.time

**Java 9-11:**
- [ ] Использую `var` для локальных переменных (где улучшает читабельность)
- [ ] Использую HTTP Client API вместо HttpURLConnection
- [ ] Понимаю modules (хотя бы базово)

**Java 12-17:**
- [ ] Использую switch expressions
- [ ] Использую text blocks для многострочных строк
- [ ] Использую records для immutable DTOs
- [ ] Использую pattern matching for instanceof

**Java 21:**
- [ ] Тестирую virtual threads для I/O-bound приложений
- [ ] Использую pattern matching for switch
- [ ] Использую SequencedCollection API

---

## Связь с другими темами

**[[jvm-basics-history]]** — современные фичи Java не появились в вакууме: каждая версия (8, 17, 21) строится на архитектуре JVM. Lambdas используют invokedynamic (появился в Java 7 для dynamic languages), virtual threads опираются на continuations в JVM runtime. Понимание истории и архитектуры JVM объясняет, почему фичи появились именно в таком порядке и с такими ограничениями. Рекомендуется изучить basics перед погружением в modern features.

**[[jvm-memory-model]]** — virtual threads (Java 21) кардинально меняют модель работы с памятью: миллионы потоков с микроскопическими стеками вместо тысяч с мегабайтными. Records изменяют паттерны создания объектов (immutable, компактные). Понимание memory model необходимо для осознанного выбора между platform и virtual threads и для оценки влияния новых фич на GC pressure.

**[[jvm-performance-overview]]** — каждая modern feature имеет performance implications: streams vs for-loops (allocation overhead), virtual threads vs thread pools (scheduling cost), records vs POJOs (memory layout). Performance overview помогает оценить, когда новые фичи дают реальный выигрыш, а когда добавляют overhead. Изучайте modern features для продуктивности, performance overview — для критичных путей.

**[[jvm-concurrency-overview]]** — Virtual Threads (Java 21) невозможно оценить без понимания традиционной модели потоков в Java: Thread, ExecutorService, ForkJoinPool. Concurrency overview объясняет проблемы, которые решают virtual threads: ограниченное количество OS-потоков, дорогостоящее переключение контекста, необходимость реактивных фреймворков для high-throughput I/O. Рекомендуется изучить классическую конкурентность перед погружением в Project Loom, чтобы понять масштаб улучшений.

**[[jvm-languages-ecosystem]]** — Kotlin, Scala и Clojure повлияли на эволюцию Java: lambdas пришли из Scala, null-safety из Kotlin, pattern matching из ML-семейства. Сравнение показывает, что Java перенимает лучшие идеи, но адаптирует их к своей философии backward compatibility. Изучение экосистемы JVM-языков помогает понять design decisions в modern Java.

---

## Источники и дальнейшее чтение

- Urma R.-G., Fusco M., Mycroft A. (2018). *Modern Java in Action.* — Фундаментальная книга по Java 8-17: lambdas, streams, Optional, модули. Каждая фича разбирается с мотивацией, примерами и внутренним устройством. Лучший источник для понимания функциональной революции Java.
- Bloch J. (2018). *Effective Java, 3rd Edition.* — 90 практических рекомендаций по написанию качественного Java-кода. Покрывает lambdas (Items 42-48), streams (Items 45-48), Optional (Item 55). Незаменимый справочник для перехода от знания синтаксиса к пониманию идиом.
- Goetz B. et al. (2006). *Java Concurrency in Practice.* — Классика конкурентного программирования на Java. Хотя написана до virtual threads, объясняет фундамент (Java Memory Model, happens-before, thread safety), без которого невозможно понять, почему Project Loom стал необходим.
- Oaks S. (2020). *Java Performance, 2nd Edition.* — Покрывает производительность streams vs loops, lambda allocation cost, влияние модулей на startup time. Необходим для осознанного выбора между новыми и классическими подходами в performance-critical коде.

---

## Дополнительные ресурсы

**Книги:**
- "Effective Java 3rd Edition" — Joshua Bloch (2018)
- "Modern Java in Action" — Raoul-Gabriel Urma (2018)
- "Java Concurrency in Practice" — Brian Goetz (2006, классика)

**Официальные ресурсы:**
- [JEP Index](https://openjdk.org/jeps/0) — все Java Enhancement Proposals
- [Java Language Specification](https://docs.oracle.com/javase/specs/)
- [Project Loom](https://openjdk.org/projects/loom/) — Virtual Threads
- [Project Amber](https://openjdk.org/projects/amber/) — Records, Sealed Classes, Pattern Matching

**Интервью и статьи:**
- [Brian Goetz: Project Lambda from the Inside](https://www.infoq.com/articles/Brian_Goetz_Project_Lambda_from_the_Inside_Interview/) — История создания лямбд
- [Ron Pressler: Project Loom](https://www.infoq.com/podcasts/java-project-loom/) — Почему Virtual Threads
- [State of Loom](https://cr.openjdk.org/~rpressler/loom/loom/sol1_part1.html) — Техническое описание от Ron Pressler
- [Data Classes and Sealed Types for Java](https://openjdk.org/projects/amber/design-notes/records-and-sealed-classes) — Официальный design document

**Инструменты:**
- [sdkman](https://sdkman.io/) — управление версиями Java
- [jEnv](https://www.jenv.be/) — switch между JDK версиями

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Lambdas медленнее anonymous classes" | JVM оптимизирует lambdas через invokedynamic — при первом вызове создаётся оптимальная реализация. После warmup lambdas часто быстрее за счёт инлайнинга |
| "Streams всегда лучше for-loops" | Streams добавляют overhead на создание объектов. Для простых операций (sum, count) for-loop может быть в 2-3 раза быстрее. Streams выигрывают в читаемости и parallel processing |
| "Optional решает все NPE проблемы" | Optional предназначен только для return types. Использование в полях, параметрах или коллекциях — anti-pattern. Optional сам может быть null! |
| "var делает Java динамически типизированным" | var — это только type inference на compile-time. Тип определяется компилятором и неизменен. Runtime поведение идентично явному указанию типа |
| "Records полностью заменяют POJOs" | Records immutable и не поддерживают inheritance. Для mutable entities, builder pattern или наследования нужны классические классы |
| "Virtual Threads заменяют все Thread Pools" | Virtual Threads оптимальны для I/O-bound задач. Для CPU-bound операций platform threads эффективнее из-за прямого scheduling на CPU cores |
| "Pattern Matching полностью заменяет instanceof + cast" | Pattern Matching не работает с generic types из-за type erasure. `instanceof List<String>` всё ещё невозможен |
| "Text Blocks — просто многострочные строки" | Text Blocks также нормализуют indentation (incidental whitespace) и line endings. Это semantic feature, не только syntactic sugar |
| "Sealed Classes нужны только для exhaustive switch" | Sealed Classes обеспечивают controlled inheritance — гарантия, что иерархия не расширится. Это важно для API design и binary compatibility |
| "Java 21 — достаточно для всех новых фич" | Некоторые фичи (String Templates, Scoped Values) всё ещё в preview. Production adoption требует stable API — проверяйте JEP status |

---

## CS-фундамент

| CS-концепция | Применение в Java Modern Features |
|--------------|-----------------------------------|
| **Lambda Calculus** | Lambdas реализуют anonymous functions из λ-исчисления — функции как first-class citizens, основа функционального программирования |
| **Type Inference** | `var` использует Hindley-Milner алгоритм для выведения типов — компилятор определяет тип без явного указания |
| **Algebraic Data Types** | Records + Sealed Classes = Product Types + Sum Types. Паттерн из ML/Haskell для type-safe domain modeling |
| **Pattern Matching** | Структурная декомпозиция данных — проверка формы и извлечение компонентов одновременно (как в ML, Scala) |
| **Green Threads** | Virtual Threads реализуют user-space threading — M:N модель (M virtual → N OS threads), как goroutines в Go |
| **Continuation** | Механизм virtual threads: сохранение состояния выполнения и возобновление. Основа для structured concurrency |
| **Monadic Pattern** | Optional и Stream реализуют monad pattern — flatMap/map композиция для обработки отсутствующих значений и коллекций |
| **Lazy Evaluation** | Streams используют lazy evaluation — промежуточные операции не выполняются до терминальной. Экономия ресурсов |
| **Strong Encapsulation** | Modules (JPMS) реализуют information hiding на уровне packages — compile-time enforcement доступа |
| **Discriminated Unions** | Sealed Classes + Pattern Matching = tagged unions. Типобезопасное представление альтернатив |

---

## Источники

1. [Oracle: Java 8 Lambdas Part 1](https://www.oracle.com/technical-resources/articles/java/architect-lambdas-part1.html) — Официальное руководство Oracle
2. [InfoQ: Brian Goetz Interview on Project Lambda](https://www.infoq.com/articles/Brian_Goetz_Project_Lambda_from_the_Inside_Interview/) — История создания лямбд
3. [InfoQ: Ron Pressler on Project Loom](https://www.infoq.com/podcasts/java-project-loom/) — Почему создали Virtual Threads
4. [OpenJDK: State of Loom](https://cr.openjdk.org/~rpressler/loom/loom/sol1_part1.html) — Техническое описание от Ron Pressler
5. [OpenJDK: Records and Sealed Classes Design Notes](https://openjdk.org/projects/amber/design-notes/records-and-sealed-classes) — Почему добавили ADT
6. [InfoWorld: Project Loom Explained](https://www.infoworld.com/article/2334607/project-loom-understand-the-new-java-concurrency-model.html) — Обзор новой модели конкурентности
7. [Scott Logic: Algebraic Data Types in Java](https://blog.scottlogic.com/2025/01/20/algebraic-data-types-with-java.html) — Практическое применение sealed + records
8. [Java Code Geeks: Modern Java Features](https://www.javacodegeeks.com/2025/12/modern-java-language-features-records-sealed-classes-pattern-matching.html) — Обзор современных фич
9. "Effective Java 3rd Edition" — Joshua Bloch (2018)
10. "Modern Java in Action" — Raoul-Gabriel Urma (2018)

---

## Проверь себя

> [!question]- Почему virtual threads с synchronized блоками могут быть медленнее, чем обычные platform threads, и как это исправить?
> Virtual thread при входе в synchronized блок "приколачивается" (pins) к carrier thread и не может быть unmounted. Если внутри synchronized выполняется blocking I/O, carrier thread блокируется на всё время операции. При 8 CPU cores это означает максимум 8 одновременных операций, даже если создано 100000 virtual threads. Решение: заменить synchronized на ReentrantLock, который поддерживает unmounting virtual thread при blocking. Также заменить Vector, Hashtable и Collections.synchronizedList() на ConcurrentHashMap и CopyOnWriteArrayList. Для обнаружения pinning использовать -Djdk.tracePinnedThreads=full.

> [!question]- Сценарий: вы мигрируете Spring Boot приложение с Java 11 на Java 21 и хотите использовать virtual threads. В коде 50 мест с synchronized для thread-safety кэша. Опишите план миграции
> 1. Включить -Djdk.tracePinnedThreads=full для обнаружения pinning в тестовой среде. 2. Заменить все synchronized блоки на ReentrantLock с try/finally. 3. Заменить synchronized коллекции (Vector, Hashtable) на ConcurrentHashMap/CopyOnWriteArrayList. 4. В Spring Boot настроить spring.threads.virtual.enabled=true для встроенного Tomcat. 5. Проверить все зависимости на совместимость с virtual threads (JDBC драйверы, connection pools — HikariCP поддерживает). 6. Провести нагрузочное тестирование: сравнить throughput с platform threads vs virtual threads. 7. Мониторить pinning в production через JFR events.

> [!question]- В чём принципиальное различие между Streams и for-loops, и когда for-loop предпочтительнее?
> Streams используют lazy evaluation (промежуточные операции не выполняются до терминальной), создают pipeline объектов и поддерживают parallel processing через parallelStream(). For-loops выполняются eagerly, не создают дополнительных объектов и дают прямой контроль над итерацией. For-loop предпочтительнее: (1) для performance-critical кода — streams создают overhead на allocation; (2) для простых операций (sum, max) — for-loop в 2-3 раза быстрее; (3) когда нужны side effects (println, mutation); (4) когда нужен break/continue; (5) для мелких коллекций, где overhead streams заметен.

> [!question]- Почему Records + Sealed Classes + Pattern Matching называют Algebraic Data Types и какую проблему они решают?
> ADT — это комбинация Product Types (records — каждый экземпляр содержит ВСЕ поля) и Sum Types (sealed classes — значение может быть ОДНИМ из перечисленных типов). Это решает проблему invalid states: с классическим ООП можно создать объект с противоречивыми полями (например, Result с value И error одновременно). С sealed + records это невозможно by construction: Success содержит только value, Failure — только error. Pattern matching добавляет exhaustiveness checking — компилятор гарантирует обработку всех вариантов. При добавлении нового подтипа компилятор покажет все места, где нужно обновить код.

---

## Ключевые карточки

Какие четыре ключевые фичи принесла Java 8 (2014)?
?
1) Lambda expressions — анонимные функции через invokedynamic, основа функционального стиля. 2) Stream API — declarative pipeline для коллекций с lazy evaluation и parallel processing. 3) Optional — контейнер для nullable значений, замена null checks. 4) java.time — иммутабельный Date/Time API взамен mutable java.util.Date.

Что такое Virtual Threads (Java 21) и когда их использовать?
?
Virtual Threads — легковесные потоки (M:N модель), управляемые JVM, а не ОС. Миллионы virtual threads маппятся на несколько carrier (platform) threads. Использовать для I/O-bound задач (HTTP, DB, файлы). Не использовать для CPU-bound задач. Избегать synchronized (pinning) — использовать ReentrantLock.

Чем Records отличаются от обычных Java классов?
?
Records — иммутабельные data carriers: автоматически генерируют constructor, getters (name(), age()), equals(), hashCode(), toString(). Нельзя наследовать (implicitly final). Поддерживают compact constructor для валидации. Нельзя добавить mutable поля. Pattern matching позволяет деструктурировать records в switch.

Что такое Sealed Classes и зачем нужны?
?
Sealed Classes ограничивают иерархию наследования через permits. Компилятор знает ВСЕ возможные подтипы, что позволяет exhaustiveness checking в switch без default. Используются для domain modeling (OrderState, PaymentResult) — гарантия обработки всех состояний. При добавлении нового подтипа компилятор показывает все места для обновления.

В чём проблема thread pinning и как её обнаружить?
?
Thread pinning — virtual thread "прикалывается" к carrier thread внутри synchronized блока и не может быть unmounted при blocking I/O. Это ограничивает параллелизм до количества carrier threads (CPU cores). Обнаружение: -Djdk.tracePinnedThreads=full. Решение: заменить synchronized на ReentrantLock, который поддерживает unmounting.

Чем thenApply отличается от thenCompose в CompletableFuture?
?
thenApply — синхронная трансформация результата (как map): принимает T, возвращает U. thenCompose — асинхронная цепочка (как flatMap): принимает T, возвращает CompletableFuture<U>. thenCompose нужен для избежания вложенных CompletableFuture<CompletableFuture<U>>. Аналогия: thenApply = map, thenCompose = flatMap.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубление | [[jvm-synchronization]] | Детальное понимание synchronized vs ReentrantLock для virtual threads |
| Углубление | [[jvm-module-system]] | Глубокое изучение JPMS, uses/provides, миграция classpath to module path |
| Связь | [[jvm-languages-ecosystem]] | Сравнить фичи Java 21 с Kotlin, Scala — откуда пришли records, pattern matching |
| Кросс-область | [[kotlin-coroutines]] | Сравнить virtual threads с coroutines — два подхода к конкурентности на JVM |
| Навигация | [[jvm-overview]] | Вернуться к обзору JVM-тем |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

---
title: "Memory Safety: от багов к гарантиям"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/advanced
related:
  - "[[memory-model-fundamentals]]"
  - "[[garbage-collection-explained]]"
  - "[[reference-counting-arc]]"
---

# Memory Safety: от багов к гарантиям

> **TL;DR:** Memory safety предотвращает классы багов: use-after-free, double-free, dangling pointers. Подходы: GC (pauses), Reference Counting (overhead), Ownership (compile-time, Rust). Rust: один owner, borrowing правила, borrow checker. Swift добавил Sendable/Actors для concurrency safety. Kotlin/Native использовал freeze (shared XOR mutable), новая модель проще. Для KMP критично: разные модели на разных targets требуют понимания ограничений.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Stack vs Heap** | Понять где происходят баги | [[memory-model-fundamentals]] |
| **GC** | Альтернатива ownership | [[garbage-collection-explained]] |
| **ARC** | iOS модель | [[reference-counting-arc]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Use-After-Free** | Обращение к освобождённой памяти | Звонок на отключённый номер |
| **Double-Free** | Повторное освобождение памяти | Сдать ключи дважды |
| **Dangling Pointer** | Указатель на freed память | Адрес снесённого дома |
| **Ownership** | Единоличное владение ресурсом | Один хозяин вещи |
| **Borrowing** | Временное заимствование | Взять на время, вернуть |
| **Lifetime** | Время жизни ссылки | Срок аренды |
| **RAII** | Автоматическое освобождение в деструкторе | Уборка при выезде |

---

## ПОЧЕМУ memory safety важна

### Классы багов, которые убивают программы

Три вещи делают низкоуровневые языки опасными:

**1. Use-After-Free**

```c
char* ptr = malloc(100);
free(ptr);
// ... другой код мог получить эту память ...
strcpy(ptr, "hello");  // BOOM! Пишем в чужую память
```

Последствия: corruption данных, crash, security exploits.

**2. Double-Free**

```c
char* ptr = malloc(100);
free(ptr);
// ... забыли, что уже освободили ...
free(ptr);  // BOOM! Heap corruption
```

Последствия: повреждение heap metadata, arbitrary code execution.

**3. Dangling Pointer**

```c
int* get_number() {
    int local = 42;
    return &local;  // local умрёт после return!
}

int* ptr = get_number();
printf("%d", *ptr);  // BOOM! Dangling pointer
```

Последствия: undefined behavior, random values, crashes.

### Почему это важно для безопасности

70% уязвимостей в Chrome, Windows, iOS — memory safety баги. NSA, CISA, White House рекомендуют переход на memory-safe языки.

Атакующий может:
- Перезаписать return address
- Изменить function pointers
- Получить RCE (Remote Code Execution)

---

## Подходы к Memory Safety

### Спектр решений

```
┌─────────────────────────────────────────────────────────────────┐
│             MEMORY SAFETY APPROACHES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   MANUAL                                                        │
│   ├── C: malloc/free                                            │
│   └── Ответственность на программисте                          │
│                                                                 │
│   RAII (без проверок)                                          │
│   ├── C++: деструкторы                                          │
│   └── Автоочистка, но dangling возможны                        │
│                                                                 │
│   OWNERSHIP + BORROW CHECKING                                  │
│   ├── Rust: compile-time гарантии                              │
│   └── Нет runtime overhead, нет багов                          │
│                                                                 │
│   REFERENCE COUNTING                                           │
│   ├── Swift ARC, Python                                        │
│   └── Runtime overhead, cycles проблема                        │
│                                                                 │
│   GARBAGE COLLECTION                                           │
│   ├── Java, Go, Kotlin/JVM                                     │
│   └── Runtime overhead, GC pauses                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Сравнение

| Подход | Safety | Performance | Predictability | Learning |
|--------|--------|-------------|----------------|----------|
| Manual (C) | Низкая | Высокая | Высокая | Средний |
| RAII (C++) | Средняя | Высокая | Высокая | Средний |
| Ownership (Rust) | Высокая | Высокая | Высокая | Высокий |
| ARC (Swift) | Высокая | Средняя | Средняя | Средний |
| GC (Java) | Высокая | Средняя | Низкая | Низкий |

---

## Ownership Model (Rust)

### Три правила

Rust решает проблему элегантно: compile-time ownership.

**Правило 1:** Каждое значение имеет владельца (owner).

```rust
let s = String::from("hello");  // s — владелец строки
```

**Правило 2:** Только один владелец в любой момент.

```rust
let s1 = String::from("hello");
let s2 = s1;  // Ownership перешёл к s2
// println!("{}", s1);  // COMPILE ERROR! s1 больше не владеет
```

**Правило 3:** Когда владелец выходит из scope — значение освобождается.

```rust
{
    let s = String::from("hello");
    // s используется
}  // s выходит из scope, память освобождается автоматически
```

### Move Semantics

Присваивание = передача ownership (move):

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOVE SEMANTICS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   let s1 = String::from("hello");                               │
│                                                                 │
│   Stack:         Heap:                                          │
│   ┌─────────┐   ┌─────────────────┐                             │
│   │ s1      │──>│ "hello"         │                             │
│   │ ptr     │   │                 │                             │
│   │ len: 5  │   └─────────────────┘                             │
│   │ cap: 5  │                                                   │
│   └─────────┘                                                   │
│                                                                 │
│   let s2 = s1;  // MOVE!                                        │
│                                                                 │
│   Stack:         Heap:                                          │
│   ┌─────────┐                                                   │
│   │ s1      │   (invalid - moved from)                          │
│   │ ----    │                                                   │
│   └─────────┘                                                   │
│   ┌─────────┐   ┌─────────────────┐                             │
│   │ s2      │──>│ "hello"         │                             │
│   │ ptr     │   │                 │                             │
│   │ len: 5  │   └─────────────────┘                             │
│   │ cap: 5  │                                                   │
│   └─────────┘                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Move предотвращает double-free: только s2 освободит память.

### Borrowing: использование без владения

Иногда нужен доступ без передачи ownership. Rust позволяет "заимствовать":

**Immutable borrow (&T):**

```rust
fn print_length(s: &String) {
    println!("Length: {}", s.len());
}

let s = String::from("hello");
print_length(&s);  // Заимствуем
println!("{}", s);  // s всё ещё валиден!
```

**Mutable borrow (&mut T):**

```rust
fn add_exclaim(s: &mut String) {
    s.push('!');
}

let mut s = String::from("hello");
add_exclaim(&mut s);
println!("{}", s);  // "hello!"
```

### Правила заимствования

```rust
// МОЖНО: много immutable borrows
let s = String::from("hello");
let r1 = &s;
let r2 = &s;
println!("{}, {}", r1, r2);  // OK

// МОЖНО: один mutable borrow
let mut s = String::from("hello");
let r1 = &mut s;
r1.push('!');

// НЕЛЬЗЯ: mutable + immutable одновременно
let mut s = String::from("hello");
let r1 = &s;      // immutable borrow
let r2 = &mut s;  // COMPILE ERROR! Уже есть immutable
```

Эти правила предотвращают data races статически.

### Borrow Checker

Компилятор Rust содержит borrow checker — статический анализатор, проверяющий правила во время компиляции.

```rust
fn dangling() -> &String {
    let s = String::from("hello");
    &s  // COMPILE ERROR! s умрёт, ссылка станет dangling
}
```

Borrow checker отследит и запретит.

---

## RAII: Resource Acquisition Is Initialization

### Идея

В C++ деструктор вызывается автоматически при выходе из scope:

```cpp
class File {
    FILE* handle;
public:
    File(const char* name) {
        handle = fopen(name, "r");
    }
    ~File() {
        if (handle) fclose(handle);  // Автоматически!
    }
};

void process() {
    File f("data.txt");
    // работаем с файлом
}  // Деструктор вызовется, файл закроется
```

### Проблема C++

RAII не защищает от dangling references:

```cpp
std::string& dangerous() {
    std::string local = "hello";
    return local;  // Возвращаем ссылку на локальную переменную
}  // local уничтожен, ссылка dangling

// Компилятор может предупредить, но не запретит
```

Rust добавляет borrow checker к RAII, делая dangling невозможными.

---

## Swift: ARC + Concurrency Safety

### ARC как основа

Swift использует Automatic Reference Counting (см. [[reference-counting-arc]]).

### Sendable и Actors

Swift 5.5+ добавил compile-time concurrency safety:

**Sendable:** маркер типов, безопасных для передачи между потоками.

```swift
struct User: Sendable {  // Можно передавать между actors
    let id: Int
    let name: String
}
```

**Actors:** изолируют mutable state.

```swift
actor BankAccount {
    private var balance: Int = 0

    func deposit(_ amount: Int) {
        balance += amount  // Безопасно — только actor имеет доступ
    }

    func getBalance() -> Int {
        return balance
    }
}

// Вызов из другого контекста
let account = BankAccount()
await account.deposit(100)  // await — переключение контекста
```

### Гарантии

- Только один task выполняет код actor в момент времени
- Sendable типы можно безопасно передавать
- Compiler проверяет isolation нарушения

---

## Kotlin/Native Memory Model

### Старая модель: Freeze

Kotlin/Native (до 2021) использовал правило: **Shared XOR Mutable**.

```kotlin
// Объект либо:
// 1. Mutable и принадлежит одному потоку
// 2. Frozen (immutable) и может шариться

val data = mutableListOf("a", "b")
data.freeze()  // Теперь immutable навсегда!
data.add("c")  // InvalidMutabilityException!
```

Это предотвращало data races, но было неудобно.

### Atomics для мутабельности

Для shared mutable state использовались atomic primitives:

```kotlin
val counter = AtomicInt(0)
counter.incrementAndGet()  // Thread-safe
```

### Новая модель (2021+)

Kotlin/Native перешёл на tracing GC и убрал обязательный freeze:

```kotlin
// Теперь можно шарить mutable state
val sharedList = mutableListOf<String>()
// Работает без freeze, но data races возможны!
```

Разработчик теперь сам отвечает за синхронизацию (как в Java).

---

## Практическое значение для KMP

### Разные модели на разных targets

```
┌─────────────────────────────────────────────────────────────────┐
│                KMP TARGETS MEMORY MODELS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   JVM (Android)                                                 │
│   └── GC, thread-safe standard library                         │
│                                                                 │
│   Native (iOS)                                                  │
│   └── New GC model, Objective-C interop with ARC               │
│                                                                 │
│   JavaScript                                                    │
│   └── GC, single-threaded (mostly)                             │
│                                                                 │
│   WASM                                                          │
│   └── Linear memory, manual-ish                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Что это значит для разработчика

1. **Shared code должен быть thread-safe** — работает на всех targets
2. **iOS interop**: понимать ARC, weak references
3. **Concurrency**: использовать coroutines как абстракцию
4. **Тестировать на всех targets** — поведение может различаться

---

## Подводные камни

### 1. Retain cycles (ARC)

```kotlin
// iOS interop: осторожно с циклическими ссылками
class Parent {
    var child: Child? = null
}

class Child {
    var parent: Parent? = null  // Retain cycle!
}
```

Решение: weak references.

### 2. Data races без синхронизации

```kotlin
// Новая K/N модель НЕ защищает от этого:
var counter = 0
thread { counter++ }
thread { counter++ }
// counter может быть 1, 2, или что угодно
```

Решение: AtomicInt, Mutex, или coroutines.

### 3. Memory leaks в shared code

```kotlin
// Кэш может расти бесконечно
object Cache {
    private val items = mutableMapOf<String, Data>()

    fun put(key: String, data: Data) {
        items[key] = data  // Никогда не чистится!
    }
}
```

Решение: LRU cache, WeakReference.

### Мифы

**Миф:** GC решает все проблемы памяти.
**Реальность:** GC предотвращает use-after-free, но не memory leaks (удерживаемые ссылки).

**Миф:** Rust сложнее, чем стоит.
**Реальность:** Learning curve высокий, но баги memory safety невозможны. Для systems programming это критично.

**Миф:** Kotlin/Native freeze делал код безопасным.
**Реальность:** Freeze предотвращал data races, но усложнял разработку. Новая модель требует явной синхронизации.

---

## Куда дальше

**Для понимания GC:**
→ [[garbage-collection-explained]] — как работает сборщик мусора

**Для iOS разработки:**
→ [[reference-counting-arc]] — ARC и retain cycles

**Для памяти в целом:**
→ [[memory-model-fundamentals]] — stack, heap, адресация

---

## Источники

- [Rust Book: Ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) — официальная документация
- [Stanford CS242: Rust Memory Safety](https://stanford-cs242.github.io/f18/lectures/05-1-rust-memory-safety.html) — академический взгляд
- [Kotlin: Immutability in Native](https://kotlinlang.org/docs/native-immutability.html) — freeze модель
- [Apple WWDC: Swift Actors](https://developer.apple.com/videos/play/wwdc2021/10133/) — actors и Sendable
- [verdagon: Memory Safety Approaches](https://verdagon.dev/grimoire/grimoire) — сравнение подходов
- [Snyk: Double-Free](https://learn.snyk.io/lesson/double-free/) — объяснение багов

---

*Проверено: 2026-01-09*

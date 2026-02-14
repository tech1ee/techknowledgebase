---
title: "Functional Programming: Pure Functions, Immutability, Composition"
created: 2025-12-22
modified: 2026-02-13
type: concept
status: published
confidence: high
tags:
  - topic/programming
  - functional
  - fp
  - immutability
  - composition
  - type/concept
  - level/intermediate
related:
  - "[[programming-overview]]"
  - "[[clean-code-solid]]"
  - "[[design-patterns]]"
prerequisites:
  - "[[clean-code-solid]]"
  - "[[type-systems-theory]]"
reading_time: 17
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Functional Programming: Pure Functions, Immutability, Composition

> FP — это не "только функции". Это способ думать о программах как о композиции трансформаций данных.

---

## Исторический контекст

Функциональное программирование уходит корнями в лямбда-исчисление Алонзо Чёрча (1936) — формальную систему для описания вычислений через функции. Первым практическим языком стал **Lisp** (John McCarthy, 1958), созданный для задач искусственного интеллекта в MIT. Lisp ввёл концепции first-class functions, рекурсии как основного механизма управления, и garbage collection.

В 1973 году Robin Milner создал язык **ML** (Meta Language) в Эдинбургском университете, который привнёс статическую типизацию с type inference — компилятор сам выводит типы без явных аннотаций. ML породил целое семейство языков: Standard ML, OCaml, F#.

В 1990 году комитет исследователей опубликовал спецификацию **Haskell** — чисто функционального языка с ленивыми вычислениями (lazy evaluation). Haskell стал "лабораторией" для исследования монад, type classes и других абстракций, которые позже проникли в mainstream-языки.

Влияние FP на современные языки огромно: лямбда-выражения появились в Java 8 (2014), C++ 11 (2011), Python (с рождения, но PEP усилили), Kotlin (2016). Концепции map/filter/reduce, pattern matching, immutable data classes стали стандартными инструментами даже в объектно-ориентированных языках. Rust (2015) построил всю систему ownership на идеях из ML и Haskell.

---

## TL;DR

- **Pure functions** — нет side effects, всегда одинаковый результат для одинаковых аргументов
- **Immutability** — данные не изменяются после создания
- **Composition** — сложные функции из простых
- **Higher-order functions** — функции как first-class citizens

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Pure function** | Нет side effects, deterministic |
| **Side effect** | Изменение внешнего state, I/O |
| **Immutable** | Не изменяемый после создания |
| **Higher-order function** | Принимает или возвращает функцию |
| **First-class function** | Функция как значение |
| **Closure** | Функция + captured environment |
| **Referential transparency** | Можно заменить вызов на результат |
| **Monad** | Контейнер для последовательных вычислений |

---

## Pure Functions

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        PURE vs IMPURE FUNCTIONS                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PURE FUNCTION                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │    Input ────▶ ┌──────────┐ ────▶ Output                           │   │
│  │                │ Function │                                         │   │
│  │    Input ────▶ └──────────┘ ────▶ Output                           │   │
│  │                                                                      │   │
│  │  • Same input → same output (always)                               │   │
│  │  • No side effects                                                  │   │
│  │  • No external state access                                        │   │
│  │  • Easy to test, reason about, parallelize                        │   │
│  │                                                                      │   │
│  │  Examples:                                                          │   │
│  │  • Math functions: add(a, b), sqrt(x)                              │   │
│  │  • String manipulation: toUpperCase(s)                             │   │
│  │  • Data transformation: map, filter, reduce                        │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMPURE FUNCTION                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │                  ┌─────────────┐                                    │   │
│  │  External ◀────▶ │  Function   │ ◀────▶ External                   │   │
│  │  State           │             │        I/O                         │   │
│  │                  └─────────────┘                                    │   │
│  │    Input ───────────▶│▲────────────▶ Output                        │   │
│  │                       ││                                            │   │
│  │                       ▼│                                            │   │
│  │                  Side Effects                                       │   │
│  │                                                                      │   │
│  │  • Result depends on external state                                │   │
│  │  • May modify external state                                       │   │
│  │  • Hard to test, reason about                                      │   │
│  │                                                                      │   │
│  │  Examples:                                                          │   │
│  │  • getCurrentTime(), random()                                      │   │
│  │  • Database read/write                                             │   │
│  │  • HTTP requests                                                   │   │
│  │  • Console log                                                     │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Code Examples

```python
# ❌ Impure: depends on external state
total = 0

def add_to_total(x):
    global total
    total += x  # Side effect: modifies external state
    return total

# ❌ Impure: non-deterministic
import random

def get_random_greeting():
    greetings = ["Hello", "Hi", "Hey"]
    return random.choice(greetings)  # Different result each time

# ✅ Pure: same input → same output
def add(a, b):
    return a + b

# ✅ Pure: no side effects
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# ✅ Pure: data transformation
def calculate_total(items):
    return sum(item.price for item in items)
```

```kotlin
// ✅ Pure functions in Kotlin
fun add(a: Int, b: Int): Int = a + b

fun filterAdults(people: List<Person>): List<Person> =
    people.filter { it.age >= 18 }

fun calculateDiscount(price: Double, discountPercent: Double): Double =
    price * (1 - discountPercent / 100)

// ❌ Impure: modifies input
fun addItemBad(list: MutableList<String>, item: String) {
    list.add(item)  // Side effect!
}

// ✅ Pure: returns new list
fun addItem(list: List<String>, item: String): List<String> =
    list + item
```

---

## Immutability

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         IMMUTABILITY                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MUTABLE (dangerous)                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  list = [1, 2, 3]                                                   │   │
│  │         │                                                           │   │
│  │         ▼                                                           │   │
│  │  ┌───────────┐      list.append(4)                                 │   │
│  │  │ 1, 2, 3   │  ─────────────────────▶  ┌───────────────┐          │   │
│  │  └───────────┘       (mutated!)         │ 1, 2, 3, 4    │          │   │
│  │                                          └───────────────┘          │   │
│  │                                                                      │   │
│  │  Problems:                                                          │   │
│  │  • Shared state bugs                                               │   │
│  │  • Hard to track changes                                           │   │
│  │  • Thread safety issues                                            │   │
│  │  • Defensive copying needed                                        │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  IMMUTABLE (safe)                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  list = [1, 2, 3]                                                   │   │
│  │         │                                                           │   │
│  │         ▼                                                           │   │
│  │  ┌───────────┐      newList = list + [4]                           │   │
│  │  │ 1, 2, 3   │  ─────────────────────────▶  (unchanged!)           │   │
│  │  └───────────┘                                                      │   │
│  │                                          ┌───────────────┐          │   │
│  │                         (new)            │ 1, 2, 3, 4    │          │   │
│  │                                          └───────────────┘          │   │
│  │                                                                      │   │
│  │  Benefits:                                                          │   │
│  │  • Thread safe by default                                          │   │
│  │  • No unexpected mutations                                         │   │
│  │  • Easy to reason about                                            │   │
│  │  • Time travel / undo easy                                         │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Code Examples

```python
# ❌ Mutable default argument trap
def add_item(item, items=[]):  # BUG: shared mutable default
    items.append(item)
    return items

# ✅ Immutable approach
def add_item(item, items=None):
    if items is None:
        items = []
    return items + [item]  # Return new list

# ✅ Using dataclasses with frozen
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    name: str
    age: int

user = User("Alice", 30)
# user.age = 31  # Error! Frozen

# ✅ Creating modified copy
new_user = User(user.name, 31)
```

```kotlin
// ✅ Kotlin: Prefer val over var, List over MutableList
val numbers: List<Int> = listOf(1, 2, 3)  // Immutable
val newNumbers = numbers + 4  // New list

// ✅ Data classes with copy
data class User(val name: String, val age: Int)

val user = User("Alice", 30)
val updatedUser = user.copy(age = 31)  // New instance

// ✅ Persistent collections (efficient immutable)
// Using kotlinx.collections.immutable
val persistentList = persistentListOf(1, 2, 3)
val newList = persistentList.add(4)  // Structural sharing
```

---

## Higher-Order Functions

```python
# ✅ Higher-order functions: take or return functions

# Takes function as argument
def apply_twice(f, x):
    return f(f(x))

def increment(x):
    return x + 1

result = apply_twice(increment, 5)  # 7

# Returns function (closure)
def multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15

# Standard higher-order functions
numbers = [1, 2, 3, 4, 5]

# map: transform each element
squared = list(map(lambda x: x**2, numbers))  # [1, 4, 9, 16, 25]

# filter: keep elements matching predicate
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

# reduce: combine all elements
from functools import reduce
total = reduce(lambda acc, x: acc + x, numbers, 0)  # 15
```

```kotlin
// ✅ Kotlin: Higher-order functions
fun <T, R> List<T>.customMap(transform: (T) -> R): List<R> {
    val result = mutableListOf<R>()
    for (item in this) {
        result.add(transform(item))
    }
    return result
}

val numbers = listOf(1, 2, 3, 4, 5)

// Lambda syntax variations
val squared = numbers.map { it * it }
val evens = numbers.filter { it % 2 == 0 }
val sum = numbers.reduce { acc, n -> acc + n }

// Function composition
val addOne: (Int) -> Int = { it + 1 }
val double: (Int) -> Int = { it * 2 }
val addOneThenDouble: (Int) -> Int = { double(addOne(it)) }

println(addOneThenDouble(3))  // 8
```

---

## Function Composition

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     FUNCTION COMPOSITION                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Building complex functions from simple ones                               │
│                                                                             │
│  f(x) = x + 1                                                              │
│  g(x) = x * 2                                                              │
│  h(x) = x ** 2                                                             │
│                                                                             │
│  Composition: (h ∘ g ∘ f)(x) = h(g(f(x)))                                 │
│                                                                             │
│  Example: x = 3                                                            │
│  ┌─────┐     ┌─────┐     ┌─────┐     ┌─────┐                             │
│  │  3  │ ──▶ │ f   │ ──▶ │ g   │ ──▶ │ h   │ ──▶  64                     │
│  │     │     │ +1  │     │ ×2  │     │ ^2  │                              │
│  └─────┘     └─────┘     └─────┘     └─────┘                             │
│                  4           8          64                                 │
│                                                                             │
│  Benefits:                                                                 │
│  • Reusable small functions                                               │
│  • Easy to test individually                                              │
│  • Clear data flow                                                        │
│  • Declarative style                                                      │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

```python
# ✅ Function composition
from functools import reduce

def compose(*functions):
    """Compose functions right to left: compose(f, g, h)(x) = f(g(h(x)))"""
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        functions
    )

def pipe(*functions):
    """Pipe functions left to right: pipe(f, g, h)(x) = h(g(f(x)))"""
    return reduce(
        lambda f, g: lambda x: g(f(x)),
        functions
    )

# Example
add_one = lambda x: x + 1
double = lambda x: x * 2
square = lambda x: x ** 2

# Compose: right to left
composed = compose(square, double, add_one)
print(composed(3))  # square(double(add_one(3))) = square(8) = 64

# Pipe: left to right (more intuitive)
piped = pipe(add_one, double, square)
print(piped(3))  # square(double(add_one(3))) = 64

# ✅ Method chaining (similar idea)
result = (
    [1, 2, 3, 4, 5]
    |> (lambda xs: filter(lambda x: x % 2 == 0, xs))  # Python 3.12+
    |> (lambda xs: map(lambda x: x * 2, xs))
    |> list
)
```

---

## Common FP Patterns

### Map, Filter, Reduce

```python
# ✅ Declarative data processing
users = [
    {"name": "Alice", "age": 25, "active": True},
    {"name": "Bob", "age": 30, "active": False},
    {"name": "Charlie", "age": 35, "active": True},
]

# Get names of active adult users
result = (
    users
    |> filter(lambda u: u["active"])
    |> filter(lambda u: u["age"] >= 18)
    |> map(lambda u: u["name"])
    |> list
)

# Without pipe (standard Python)
active_users = filter(lambda u: u["active"], users)
adult_users = filter(lambda u: u["age"] >= 18, active_users)
names = map(lambda u: u["name"], adult_users)
result = list(names)

# Using list comprehension (Pythonic)
result = [u["name"] for u in users if u["active"] and u["age"] >= 18]
```

### Option/Maybe (null safety)

```python
from typing import Optional, TypeVar, Callable

T = TypeVar('T')
U = TypeVar('U')

class Maybe:
    """Option/Maybe monad for null-safe operations."""

    def __init__(self, value: Optional[T]):
        self._value = value

    @staticmethod
    def of(value: T) -> 'Maybe[T]':
        return Maybe(value)

    @staticmethod
    def empty() -> 'Maybe[T]':
        return Maybe(None)

    def map(self, f: Callable[[T], U]) -> 'Maybe[U]':
        if self._value is None:
            return Maybe.empty()
        return Maybe.of(f(self._value))

    def flat_map(self, f: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self._value is None:
            return Maybe.empty()
        return f(self._value)

    def get_or_else(self, default: T) -> T:
        return self._value if self._value is not None else default

# Usage
def find_user(id: int) -> Maybe:
    users = {1: {"name": "Alice", "address": {"city": "NYC"}}}
    return Maybe.of(users.get(id))

# Safe chaining (no null checks!)
city = (
    find_user(1)
    .map(lambda u: u.get("address"))
    .map(lambda a: a.get("city") if a else None)
    .get_or_else("Unknown")
)
```

```kotlin
// ✅ Kotlin: Built-in null safety
data class User(val name: String, val address: Address?)
data class Address(val city: String?)

fun getCity(user: User?): String {
    // Safe call chain
    return user?.address?.city ?: "Unknown"
}

// Or with let
user?.address?.let { address ->
    println(address.city)
}
```

---

## Проверь себя

<details>
<summary>1. Почему pure functions легче тестировать?</summary>

**Ответ:**

**Pure functions:**
- Нет setup/teardown (no mocks needed)
- Deterministic: same input → same output
- No hidden dependencies
- Можно тестировать в изоляции

```python
# ✅ Pure: trivial to test
def calculate_discount(price, percent):
    return price * (1 - percent / 100)

def test_calculate_discount():
    assert calculate_discount(100, 10) == 90
    assert calculate_discount(200, 50) == 100

# ❌ Impure: needs mocking
def get_user_discount(user_id):
    user = database.get(user_id)  # External dependency
    return user.discount_percent

def test_get_user_discount():
    with mock.patch('database.get') as mock_db:
        mock_db.return_value = User(discount_percent=10)
        # ... complex setup
```

</details>

<details>
<summary>2. Когда immutability плохая идея?</summary>

**Ответ:**

**Когда НЕ использовать:**

1. **Performance-critical loops:**
   ```python
   # Slow: creates new list each iteration
   result = []
   for item in items:
       result = result + [process(item)]

   # Fast: mutate local variable
   result = []
   for item in items:
       result.append(process(item))
   ```

2. **Large data structures:**
   - Copying large objects expensive
   - Use persistent data structures (structural sharing)

3. **Low-level code:**
   - Systems programming
   - Buffer manipulation

**Best practice:** Immutable by default, mutate only when profiling shows need.

</details>

<details>
<summary>3. Что такое referential transparency?</summary>

**Ответ:**

**Referential transparency** = можно заменить вызов функции на её результат без изменения поведения программы.

```python
# ✅ Referentially transparent
def add(a, b):
    return a + b

x = add(2, 3) + add(2, 3)
# Можно заменить на:
x = 5 + 5  # Эквивалентно

# ❌ NOT referentially transparent
count = 0
def increment():
    global count
    count += 1
    return count

x = increment() + increment()  # = 1 + 2 = 3
x = 1 + 1  # = 2, НЕ эквивалентно!
```

**Benefit:** Позволяет компилятору оптимизировать, рассуждать о коде.

</details>

<details>
<summary>4. Что такое Monad простыми словами?</summary>

**Ответ:**

**Monad** = паттерн для цепочки операций с "контейнером".

**Интуиция:**
- Box с значением внутри
- `map`: применить функцию к содержимому
- `flatMap`: применить функцию, которая возвращает такой же box

**Примеры:**
- `Optional/Maybe`: контейнер, который может быть пустым
- `List`: контейнер с множеством значений
- `Result/Either`: контейнер с успехом или ошибкой
- `Future/Promise`: контейнер с будущим значением

```kotlin
// Maybe/Optional monad
val result = findUser(1)        // Maybe<User>
    .flatMap { findAddress(it) }  // Maybe<Address>
    .map { it.city }              // Maybe<String>
    .getOrElse("Unknown")         // String

// Без monad: nested null checks
val user = findUser(1)
if (user != null) {
    val address = findAddress(user)
    if (address != null) {
        return address.city
    }
}
return "Unknown"
```

</details>

---

## Связь с другими темами

**[[programming-overview]]** — Functional programming является одной из ключевых парадигм программирования наряду с императивной и объектно-ориентированной. Понимание FP расширяет "инструментарий мышления" разработчика: даже если основной язык — OOP, функциональные приёмы (pure functions, immutability, composition) делают код чище и предсказуемее. Overview даёт контекст, где FP располагается среди других парадигм.

**[[clean-code-solid]]** — Принципы чистого кода и FP взаимно усиливают друг друга. Single Responsibility (SRP) естественно вытекает из pure functions — каждая функция делает ровно одно. Open/Closed Principle реализуется через composition: расширяем поведение, комбинируя функции, а не модифицируя существующие. Dependency Inversion в FP выражается через higher-order functions — вместо наследования передаём стратегию как аргумент.

**[[design-patterns]]** — Многие GoF-паттерны в FP становятся тривиальными или исчезают вовсе. Strategy Pattern — это просто higher-order function. Observer Pattern заменяется reactive streams. Decorator — это function composition. Сравнение OOP-паттернов с FP-подходами показывает, что паттерны часто компенсируют ограничения языка, а не решают фундаментальные проблемы.

---

## Источники и дальнейшее чтение

Abelson H., Sussman G.J. (1996). *"Structure and Interpretation of Computer Programs."* — Фундаментальный учебник MIT по программированию через призму Lisp. Учит думать о вычислениях как о композиции абстракций; формирует "функциональное мышление" с нуля.

Hughes J. (1989). *"Why Functional Programming Matters."* — Классический paper, объясняющий почему FP важен для модульности. Вводит ключевые аргументы: higher-order functions и lazy evaluation как инструменты композиции, которые невозможны в императивных языках.

Chiusano P., Bjarnason R. (2014). *"Functional Programming in Scala."* — "Red Book", практическое введение в FP через Scala. Пошагово строит абстракции от pure functions до монад; отлично подходит для разработчиков с OOP-фоном.

Normand E. (2021). *"Grokking Simplicity."* — Практическое руководство по применению FP-принципов в повседневной разработке. Фокус на разделение actions, calculations и data — делает FP доступным без академического жаргона.

- [Kotlin FP Guide](https://kotlinlang.org/docs/lambdas.html) — официальная документация по лямбдам и higher-order functions в Kotlin
- [Python functools](https://docs.python.org/3/library/functools.html) — модуль стандартной библиотеки Python для функциональных инструментов

---

---

## Ключевые карточки

Что такое pure function и какие два свойства она гарантирует?
?
1) Детерминизм: для одинаковых входов всегда возвращает одинаковый результат. 2) Отсутствие side effects: не изменяет внешнее состояние, не делает I/O. Примеры: add(a, b), toUpperCase(s). Контрпримеры: getCurrentTime(), random().

Что такое referential transparency?
?
Свойство выражения, позволяющее заменить вызов функции на её результат без изменения поведения программы. Пример: add(2, 3) можно заменить на 5 везде. Нарушается при side effects (increment() меняет глобальный counter).

Почему immutable данные thread-safe по умолчанию?
?
Если данные нельзя изменить после создания, невозможна ситуация, когда один поток пишет, а другой одновременно читает (race condition). Нет необходимости в блокировках и синхронизации. Любое "изменение" создаёт новый объект.

Что такое higher-order function?
?
Функция, которая принимает другую функцию как аргумент и/или возвращает функцию как результат. Примеры: map, filter, reduce. Позволяет параметризовать поведение: вместо наследования передаём стратегию как lambda.

Что такое closure и что она "захватывает"?
?
Closure — функция вместе с captured environment (лексической средой, в которой была создана). Захватывает переменные из внешнего scope. Пример: `fun multiplier(factor) = { x -> x * factor }` — factor захвачен из внешней функции.

Что такое Monad простыми словами?
?
Паттерн для цепочки операций с "контейнером": box с значением, map для трансформации содержимого, flatMap для цепочки операций, возвращающих такой же box. Примеры: Optional/Maybe, Result/Either, Future/Promise, List.

Когда immutability — плохая идея?
?
В performance-critical циклах (создание нового объекта на каждой итерации дорого), при работе с большими данными без persistent data structures, и в low-level системном коде (буферы, прямая работа с памятью). Правило: immutable по умолчанию, mutable только по результатам профилирования.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[error-handling-resilience]] | Result/Either типы из FP для обработки ошибок |
| Углубиться | [[kotlin-functional]] | Практическое применение FP в Kotlin (lambdas, sequences, scope functions) |
| Смежная тема | [[concurrency-parallelism]] | Immutability и pure functions устраняют race conditions |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

*Проверено: 2025-12-22*

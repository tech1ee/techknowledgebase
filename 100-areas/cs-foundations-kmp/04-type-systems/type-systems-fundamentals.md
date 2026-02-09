---
title: "Type Systems: фундамент типизации"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, type-systems, static-typing, dynamic-typing, kotlin]
related:
  - "[[generics-parametric-polymorphism]]"
  - "[[variance-covariance]]"
  - "[[type-erasure-reification]]"
---

# Type Systems: фундамент типизации

> **TL;DR:** Type system — правила присвоения типов конструкциям языка. Static typing проверяет типы при компиляции (Kotlin, Java), dynamic — при выполнении (Python, JS). Strong/weak — про неявные преобразования. Kotlin: static + strong + nominal + null safety + smart casts. Понимание типов — основа для работы с generics и expect/actual в KMP.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Compilation Pipeline** | Когда происходит type checking | [[compilation-pipeline]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Type System** | Правила присвоения типов | Система категоризации товаров в магазине |
| **Static Typing** | Типы проверяются при компиляции | Проверка документов на входе |
| **Dynamic Typing** | Типы проверяются при выполнении | Проверка билета при посадке |
| **Type Inference** | Автоматическое определение типов | Продавец угадывает размер по взгляду |
| **Type Soundness** | Гарантия отсутствия type errors | Сертификат качества |

---

## ПОЧЕМУ типы важны

### Проблема: хаос без типов

Представь код без типов:

```javascript
function add(a, b) {
    return a + b;
}

add(5, 3)        // 8 — ожидаемо
add("5", 3)      // "53" — неожиданно!
add({}, [])      // "[object Object]" — ???
```

Без системы типов:
- Ошибки всплывают в production
- Код сложно понять и поддерживать
- Нельзя оптимизировать компиляцию

### История: от Russell до Kotlin

**1908 — Bertrand Russell:**
Математик Russell обнаружил парадокс в наивной теории множеств. Решение — **теория типов**: каждый объект имеет тип, и типы образуют иерархию. Это предотвращает самоссылающиеся определения.

**1940 — Alonzo Church:**
Church создал **simply typed lambda calculus** — формальную систему с типами. Это основа для типизированного функционального программирования.

**1958-1978 — Curry, Hindley, Milner:**
Разработали алгоритм **type inference** — компилятор может сам вывести типы без explicit аннотаций. Это легло в основу ML и Haskell.

**2011 — Kotlin:**
JetBrains создали Kotlin с современной системой типов: null safety, smart casts, type inference. Взяли лучшее из академических исследований и применили к практике.

---

## ЧТО такое Type System

### Определение

> "Type system — набор правил, которые присваивают свойство 'тип' различным конструкциям языка: переменным, выражениям, функциям, модулям."

Type system отвечает на вопрос: **какие операции допустимы для данного значения?**

```
┌─────────────────────────────────────────────────────────────┐
│                    TYPE SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Код программы                                             │
│        ↓                                                    │
│   ┌─────────────────┐                                       │
│   │  Type Checker   │  ← Применяет правила типов           │
│   └─────────────────┘                                       │
│        ↓                                                    │
│   ┌─────────────────┐   ┌─────────────────┐                │
│   │   ПРИНЯТО ✓     │   │ ОТКЛОНЕНО ✗     │                │
│   │  (well-typed)   │   │ (type error)    │                │
│   └─────────────────┘   └─────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Зачем нужна система типов

1. **Безопасность:** Ловить ошибки до выполнения
2. **Документация:** Типы описывают намерения
3. **Оптимизация:** Компилятор знает layout данных
4. **Инструменты:** IDE autocomplete, рефакторинг

---

## Static vs Dynamic Typing

### Когда проверяются типы

| Аспект | Static Typing | Dynamic Typing |
|--------|---------------|----------------|
| **Когда проверка** | Compile-time | Runtime |
| **Ошибки типов** | Не дают скомпилировать | Крашат программу |
| **Объявление типов** | Часто требуется | Не требуется |
| **Языки** | Java, Kotlin, C++, Rust | Python, JavaScript, Ruby |

### Static Typing: проверка на входе

```kotlin
// Kotlin — статическая типизация
fun add(a: Int, b: Int): Int {
    return a + b
}

add(5, 3)       // OK
add("5", 3)     // Compile error! Type mismatch
```

Компилятор **не даст** запустить программу с ошибкой типа.

### Dynamic Typing: проверка при исполнении

```python
# Python — динамическая типизация
def add(a, b):
    return a + b

add(5, 3)       # 8
add("5", 3)     # TypeError at runtime!
```

Ошибка **всплывёт** только когда код выполнится.

### Визуализация разницы

```
┌─────────────────────────────────────────────────────────────┐
│              STATIC vs DYNAMIC TYPING                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   STATIC (Kotlin):                                          │
│                                                             │
│   Source → [Compiler + Type Check] → Binary                │
│                    ↓                                        │
│               Error? STOP!                                  │
│                                                             │
│   Ошибка типа = программа не скомпилируется                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   DYNAMIC (Python):                                         │
│                                                             │
│   Source → [Interpreter] → Execute line by line            │
│                                ↓                            │
│                           Error? CRASH!                     │
│                                                             │
│   Ошибка типа = программа падает в runtime                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Когда что выбирать

**Static typing предпочтителен:**
- Большие кодовые базы (>10K строк)
- Команда >3 человек
- Mission-critical системы
- Долгоживущие проекты

**Dynamic typing удобен:**
- Быстрое прототипирование
- Скрипты и автоматизация
- Маленькие утилиты
- Exploratory programming

---

## Strong vs Weak Typing

### Про неявные преобразования

**Strong typing:** Язык не делает неявных преобразований между несовместимыми типами.

**Weak typing:** Язык автоматически конвертирует типы для выполнения операций.

```
┌─────────────────────────────────────────────────────────────┐
│              STRONG vs WEAK TYPING                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Выражение: "5" + 2                                        │
│                                                             │
│   STRONG (Python):                                          │
│   TypeError: can only concatenate str to str                │
│   → Явно скажи что хочешь: int("5") + 2 или "5" + str(2)   │
│                                                             │
│   WEAK (JavaScript):                                        │
│   "52"                                                      │
│   → Неявно конвертировал 2 в "2" и склеил строки           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Это НЕ то же самое, что static/dynamic!

| Язык | Static/Dynamic | Strong/Weak |
|------|----------------|-------------|
| **Python** | Dynamic | Strong |
| **JavaScript** | Dynamic | Weak |
| **Java** | Static | Strong |
| **C** | Static | Weak |

Python — динамический, но строгий: не позволяет `"5" + 2`.
C — статический, но слабый: позволяет опасные cast'ы.

### JavaScript: пример слабой типизации

```javascript
// JavaScript делает "магию"
"5" - 2      // 3 (конвертировал "5" в число)
"5" + 2      // "52" (конвертировал 2 в строку)
true + true  // 2 (true = 1)
[] + {}      // "[object Object]"
{} + []      // 0

// WAT?!
```

Это называется **type coercion** — неявное преобразование типов.

---

## Nominal vs Structural vs Duck Typing

### Три способа определить совместимость типов

```
┌─────────────────────────────────────────────────────────────┐
│        КАК ОПРЕДЕЛЯЕТСЯ СОВМЕСТИМОСТЬ ТИПОВ                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   NOMINAL (Java, Kotlin):                                   │
│   "Типы совместимы, если НАЗВАНЫ одинаково или связаны     │
│    наследованием"                                           │
│                                                             │
│   STRUCTURAL (TypeScript, Go):                              │
│   "Типы совместимы, если СТРУКТУРА одинакова"              │
│                                                             │
│   DUCK (Python, JavaScript):                                │
│   "Типы совместимы, если нужные МЕТОДЫ существуют          │
│    в момент вызова"                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Nominal Typing (Java, Kotlin)

```kotlin
// Kotlin — nominal typing
class Dog(val name: String)
class Cat(val name: String)

fun greet(dog: Dog) = println("Hello, ${dog.name}")

val dog = Dog("Rex")
val cat = Cat("Whiskers")

greet(dog)  // OK
greet(cat)  // Compile error! Type mismatch: Cat ≠ Dog
```

Хотя `Dog` и `Cat` имеют одинаковую структуру (`name: String`), они **несовместимы** по имени.

### Structural Typing (TypeScript, Go)

```typescript
// TypeScript — structural typing
interface Named {
    name: string;
}

function greet(obj: Named) {
    console.log(`Hello, ${obj.name}`);
}

const dog = { name: "Rex", bark: () => {} };
const cat = { name: "Whiskers", meow: () => {} };

greet(dog);  // OK — есть поле name
greet(cat);  // OK — есть поле name
```

TypeScript смотрит на **структуру**: есть `name: string` — значит подходит.

### Duck Typing (Python)

```python
# Python — duck typing
def greet(obj):
    print(f"Hello, {obj.name}")

class Dog:
    def __init__(self):
        self.name = "Rex"

class Robot:
    def __init__(self):
        self.name = "R2D2"

greet(Dog())    # OK
greet(Robot())  # OK
greet(42)       # AttributeError at runtime!
```

Python проверяет **в момент вызова**: есть `.name`? Работаем. Нет? Crash.

---

## Type Inference: компилятор умнее

### Что это

Type inference — способность компилятора **автоматически определить** тип без explicit аннотации.

```kotlin
// Без type inference (Java-style)
String name = "Alice";
List<Integer> numbers = Arrays.asList(1, 2, 3);

// С type inference (Kotlin)
val name = "Alice"           // Компилятор знает: String
val numbers = listOf(1, 2, 3) // Компилятор знает: List<Int>
```

### Как работает

```
┌─────────────────────────────────────────────────────────────┐
│                   TYPE INFERENCE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   val x = 42                                                │
│       ↓                                                     │
│   42 — это Int literal                                      │
│       ↓                                                     │
│   x должен быть Int                                         │
│       ↓                                                     │
│   val x: Int = 42   ← компилятор вывел тип                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   val list = listOf("a", "b")                               │
│       ↓                                                     │
│   "a", "b" — String literals                                │
│       ↓                                                     │
│   listOf<T> с String → List<String>                         │
│       ↓                                                     │
│   val list: List<String>   ← выведено                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Bidirectional Inference в Kotlin

Kotlin умеет выводить типы **в обе стороны**:

```kotlin
// Forward: из аргументов в результат
val numbers = listOf(1, 2, 3)  // List<Int>

// Backward: из использования в параметры
val transform: (String) -> Int = { it.length }
// Kotlin знает: it — это String, потому что (String) -> Int
```

---

## Kotlin Type System: практика

### Null Safety

Kotlin разделяет типы на **nullable** и **non-nullable**:

```kotlin
var name: String = "Alice"   // Non-nullable
name = null  // Compile error!

var nickname: String? = "Ali" // Nullable
nickname = null  // OK
```

**NPE ловится при компиляции, не в production.**

### Smart Casts

Kotlin автоматически приводит типы после проверки:

```kotlin
fun process(obj: Any) {
    if (obj is String) {
        // Здесь obj уже String, не Any
        println(obj.length)  // Smart cast!
    }
}

fun handleNullable(name: String?) {
    if (name != null) {
        // Здесь name уже String, не String?
        println(name.length)  // Smart cast!
    }
}
```

### Safe и Unsafe Cast

```kotlin
val obj: Any = "Hello"

// Unsafe cast — может выбросить ClassCastException
val str1: String = obj as String

// Safe cast — возвращает null при неудаче
val str2: String? = obj as? String
val num: Int? = obj as? Int  // null, не exception
```

---

## Подводные камни

### Когда type inference мешает

```kotlin
// Неочевидный выведенный тип
val items = listOf(1, 2.0, "three")
// Тип: List<Any> — возможно, не то что хотел

// Лучше explicit:
val items: List<Number> = listOf(1, 2.0, 3)
```

### Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Путать static и strong | Неверные ожидания | Python — dynamic, но strong |
| Игнорировать nullable | `!!` везде → NPE | Используй safe calls `?.` |
| Over-reliance на inference | Непонятный код | Explicit типы в public API |
| Unsafe cast без проверки | ClassCastException | Используй `as?` или `is` |

### Мифы и заблуждения

**Миф:** "Static typing замедляет разработку"
**Реальность:** Начальная скорость ниже, но меньше багов и проще рефакторинг. На дистанции static typing выигрывает.

**Миф:** "Type inference = dynamic typing"
**Реальность:** Type inference — compile-time. Типы известны компилятору, просто не написаны явно.

**Миф:** "Strong typing = больше кода"
**Реальность:** С type inference (Kotlin, Rust) код компактнее, чем в слабо типизированном JS.

---

## Куда дальше

**Если здесь впервые:**
→ Попробуй Kotlin type system на практике

**Если понял и хочешь глубже:**
→ [[generics-parametric-polymorphism]] — параметрический полиморфизм
→ [[variance-covariance]] — ковариантность и контравариантность

**Практическое применение:**
→ KMP: как типы работают на разных платформах

---

## Источники

- [Wikipedia: Type System](https://en.wikipedia.org/wiki/Type_system) — comprehensive overview
- [Wikipedia: Hindley-Milner](https://en.wikipedia.org/wiki/Hindley%E2%80%93Milner_type_system) — история type inference
- [Kotlin Docs: Null Safety](https://kotlinlang.org/docs/null-safety.html) — official documentation
- [Baeldung: Static vs Dynamic](https://www.baeldung.com/cs/programming-types-comparison) — practical comparison
- [Dan Luu: Empirical PL](https://danluu.com/empirical-pl/) — исследования static vs dynamic

---

*Проверено: 2026-01-09*

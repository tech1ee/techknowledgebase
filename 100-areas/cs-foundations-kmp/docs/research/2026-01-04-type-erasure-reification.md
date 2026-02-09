# Research Report: Type Erasure and Reification

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Type erasure — механизм JVM, стирающий информацию о generic типах при компиляции. Введён в Java 5 для backwards compatibility. `List<String>` и `List<Int>` в runtime неотличимы. Нельзя: `is T`, `T::class`, `new T()`. Kotlin решает через `inline fun <reified T>`: компилятор инлайнит код и подставляет конкретный тип до erasure. Reified работает только с inline, недоступен из Java.

## Key Findings

### 1. Почему Type Erasure

**Java 5 (2004):** Generics добавлены в уже существующий язык.

**Проблема:** Старый код (Java 1.4) должен работать с новым.

**Решение:** Erasure — generics только на уровне компилятора, JVM не меняется.

### 2. Как работает Erasure

**Компилятор:**
1. Заменяет type parameters на bounds (или Object)
2. Вставляет casts где нужно
3. Генерирует bridge methods

**Примеры:**
```
List<String> → List
<T> → Object
<T extends Number> → Number
```

### 3. Ограничения

| Нельзя | Почему |
|--------|--------|
| `value is T` | T неизвестен в runtime |
| `T::class` | Нет информации о T |
| `T()` / `new T()` | Нельзя создать экземпляр неизвестного типа |
| Перегрузка по generic | Одинаковая сигнатура после erasure |

### 4. Kotlin Reified

**Механизм:**
1. `inline` — тело функции копируется в место вызова
2. `reified` — компилятор сохраняет информацию о типе
3. До erasure тип подставляется конкретный

**Пример:**
```kotlin
inline fun <reified T> isInstance(value: Any): Boolean {
    return value is T  // Работает!
}

// При вызове isInstance<String>("test"):
// Компилятор генерирует: "test" is String
```

### 5. Ограничения Reified

| Ограничение | Причина |
|-------------|---------|
| Только inline | Без inline нет места для подстановки типа |
| Недоступен из Java | Java не поддерживает inline |
| Тип должен быть известен | Нельзя передать T из другого generic |

### 6. Workarounds без Reified

**Class parameter:**
```kotlin
fun <T> create(clazz: Class<T>): T = clazz.newInstance()
create(String::class.java)
```

**Reflection:**
```kotlin
// Ограничено: только parameterized types
```

**TypeToken (Gson pattern):**
```kotlin
object : TypeToken<List<String>>() {}
```

### 7. Практические Use Cases

- `filterIsInstance<T>()` — фильтрация по типу
- JSON serialization без явного класса
- Android Intent extras
- Dependency Injection

## Community Sentiment

### Positive
- Reified элегантно решает проблему
- Inline + reified = type-safe APIs
- Kotlin улучшает developer experience

### Negative
- Type erasure — источник багов
- Reified недоступен из Java
- Сложность понимания для новичков

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Android Developers: Reification](https://medium.com/androiddevelopers/reification-of-the-erased-41e246725d2c) | Blog | ★★★★★ | Clear explanation |
| [Baeldung: Type Erasure](https://www.baeldung.com/java-type-erasure) | Tutorial | ★★★★☆ | Java perspective |
| [Baeldung: Reified Functions](https://www.baeldung.com/kotlin/reified-functions) | Tutorial | ★★★★☆ | Practical examples |
| [Oracle: Type Erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html) | Official | ★★★★★ | Authoritative |
| [DroidCon: Inline Reified](https://www.droidcon.com/2025/03/05/kotlin-inline-reified-to-solve-type-erasure/) | Article | ★★★★☆ | Comprehensive |

## Research Methodology
- **Queries used:** 2 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **Focus areas:** Erasure mechanics, reified inline, workarounds

---

*Проверено: 2026-01-09*

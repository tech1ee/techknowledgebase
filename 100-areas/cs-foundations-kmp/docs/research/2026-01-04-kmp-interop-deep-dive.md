# Research Report: KMP Interop Deep Dive

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Kotlin/Native interop с Swift работает через Objective-C bridge: Kotlin генерирует ObjC headers, которые Swift импортирует. Это работает, но теряются Swift фичи (enums, sealed, async/await). SKIE от Touchlab добавляет Flow→AsyncSequence и suspend→async. Swift Export (experimental) — прямой экспорт в Swift без ObjC, stable планируется в 2026. cinterop — для импорта C/ObjC библиотек в Kotlin. Основные проблемы: generics (T→T?), collections overhead, исключения без @Throws = crash.

## Key Findings

### 1. ObjC Bridge Architecture

**Как работает:**
```
Kotlin → ObjC Headers → Swift
```

Kotlin/Native компилятор генерирует Objective-C заголовки. Swift импортирует их через ObjC bridging. Это работает, потому что:
- ObjC runtime имеет стабильный ABI
- Swift имеет встроенную совместимость с ObjC (@objc)
- Kotlin/Native умеет генерировать ObjC-совместимый код

**Потери при трансляции:**
- Enums → Classes (не Swift enums)
- Sealed classes → обычные classes (нет exhaustive switch)
- Default arguments → теряются
- Generics constraints → T становится T?
- Suspend → completion handler (не async/await)

### 2. Type Mappings

| Kotlin | Swift | Objective-C |
|--------|-------|-------------|
| class | class | @interface |
| interface | protocol | @protocol |
| enum class | class(!) | @interface |
| String | String | NSString |
| List<T> | Array | NSArray |
| suspend fun | async/completion | completionHandler |
| Int? | KotlinInt? | NSNumber* |

### 3. Key Annotations

**@ObjCName** — кастомные имена:
```kotlin
@ObjCName(swiftName = "UserProfile")
class User
```

**@HiddenFromObjC** — скрыть от Swift/ObjC

**@ShouldRefineInSwift** — пометить как __ (не autocomplete)

**@Throws** — propagate исключения в Swift:
```kotlin
@Throws(IOException::class)
fun readFile(): String
```

### 4. SKIE Features

| Feature | Что делает |
|---------|-----------|
| Flow → AsyncSequence | Автоматическая конверсия |
| Suspend → async | Native Swift async/await |
| Sealed → enum | Exhaustive switch |
| Cancellation | Task.cancel() propagates |

### 5. Swift Export (Experimental)

**Преимущества:**
- Kotlin enum → Swift enum
- Nullable primitives без boxing
- Packages → nested enums
- Лучшие имена по умолчанию

**Ограничения (2024):**
- Нет functional types
- Нет subclassing из Swift
- Generics erased
- Suspend/Flow не поддержаны

**Timeline:** Stable планируется 2026

### 6. cinterop

Для импорта C/ObjC библиотек в Kotlin:

```
# library.def
headers = library.h
package = mylib
linkerOpts = -lmylib
```

Platform libraries (Foundation, UIKit) доступны без cinterop через `platform.*`.

### 7. Performance Considerations

**String conversion:**
Kotlin String → NSString → Swift String = две копии!

**Collections:**
List → NSArray → Swift Array = overhead

**Решение:** Работать с NS* типами напрямую когда performance критичен.

## Community Sentiment

### Positive
- ObjC bridge работает в production (Netflix, McDonald's)
- SKIE решает главные pain points
- Swift Export движется в правильном направлении
- cinterop мощный инструмент для native библиотек

### Negative / Concerns
- Двойная конверсия через ObjC — overhead
- Generics ограничения frustrating
- Исключения без @Throws = crash (неочевидно)
- Pure Swift modules не поддержаны
- Swift Export далёк от stable

### Mixed
- SKIE vs KMP-NativeCoroutines — выбор между ними не очевиден
- Swift Export заменит SKIE? Не факт

## Common Mistakes

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Нет @Throws | Crash в Swift | Добавить @Throws или Result type |
| Generic без : Any | T становится T? | Добавить <T : Any> |
| Частые collection passes | Performance overhead | NS* типы или batch |
| Ожидание pure Swift | Не работает | @objc обязателен |

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [ObjC Interop](https://kotlinlang.org/docs/native-objc-interop.html) | Official | ★★★★★ | Authoritative |
| 2 | [SKIE](https://skie.touchlab.co/) | Tool | ★★★★★ | Production solution |
| 3 | [Swift Interopedia](https://github.com/kotlin-hands-on/kotlin-swift-interopedia) | Examples | ★★★★☆ | Practical |
| 4 | [KMP-NativeCoroutines](https://github.com/rickclephas/KMP-NativeCoroutines) | Library | ★★★★☆ | Coroutines |
| 5 | [Droidcon Interop](https://www.droidcon.com/2024/11/20/kotlin-multiplatform-how-to-improve-the-ios-development-experience/) | Conference | ★★★★☆ | Best practices |

## Research Methodology

- **Queries used:** 6 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **WebFetch deep reads:** 3 articles
- **Focus areas:** ObjC bridge, SKIE, Swift Export, cinterop, type mappings


---

*Проверено: 2026-01-09*

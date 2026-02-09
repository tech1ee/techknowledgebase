# Research Report: Bridges and Language Bindings

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Language bindings — автоматически сгенерированные обёртки для вызова кода одного языка из другого. Основные генераторы: SWIG (многоязычный, C/C++ → Python/Java/etc.), jextract (Java FFM API), cinterop (Kotlin/Native). SKIE улучшает Kotlin→Swift interop: exhaustive enums, Flows→AsyncSequence, suspend→async. Swift Export (Kotlin 2.2+) — официальная альтернатива Objective-C bridge, но пока experimental. Bidirectional interop остаётся сложной задачей.

## Key Findings

### 1. Binding Generators Overview

| Tool | Input | Output | Languages |
|------|-------|--------|-----------|
| **SWIG** | .i interface + C/C++ headers | Wrapper code | Python, Java, C#, Ruby, Go, Lua |
| **jextract** | C headers | Java FFM bindings | Java |
| **cinterop** | .def files + C/Obj-C headers | Kotlin .klib | Kotlin/Native |
| **pybind11** | C++ code | Python bindings | Python |
| **bindgen** | C headers | Rust FFI | Rust |

### 2. SWIG

**Simplified Wrapper and Interface Generator:**
- Парсит C/C++ headers с .i interface файлами
- Генерирует wrapper code + bindings для target языка
- Поддерживает 20+ языков
- Автоматизирует marshalling и type conversion

**Пример interface файла:**
```swig
%module mylib
%{
#include "mylib.h"
%}
%include "mylib.h"
```

### 3. jextract (Java)

**Project Panama tool:**
- Парсит C header файлы
- Генерирует Java классы с FFM API
- Автоматически создаёт downcall/upcall handles
- Финальный в JDK 22

**Преимущества над JNI:**
- Нет native кода
- Pure Java API
- Type-safe bindings

### 4. Kotlin/Native cinterop

**Механизм:**
1. .def файл описывает библиотеку
2. cinterop анализирует C/Obj-C headers
3. Генерирует Kotlin bindings в .klib

**Особенности:**
- Platform-specific bindings
- "Natural" mapping в Kotlin типы
- Работает через Objective-C для Swift

### 5. SKIE (Touchlab)

**Swift Kotlin Interface Enhancer:**
- Генерирует Swift wrappers поверх Obj-C headers
- Восстанавливает потерянные при трансляции фичи

**Ключевые возможности:**
- Kotlin Flows → Swift AsyncSequence
- Kotlin suspend → Swift async
- Exhaustive switch для sealed classes и enums
- Корректные defaults для функций

### 6. Swift Export (Official)

**Статус:** Experimental (Kotlin 2.2.20+)

**Преимущества:**
- Direct Swift interop (без Obj-C bridge)
- Нативный Swift синтаксис

**Ограничения:**
- Нет migration path от Obj-C interop
- Нельзя смешивать с SKIE
- Не поддерживает structs
- Далеко до паритета с текущим interop

### 7. Bidirectional Interop Challenges

**Kotlin → Swift:**
- Работает через Obj-C bridge
- SKIE значительно улучшает
- Swift Export развивается

**Swift → Kotlin:**
- Значительно сложнее
- Требует @objc wrappers
- Touchlab планирует улучшения

## Community Sentiment

### Positive
- SWIG зрелый и стабильный
- jextract упрощает native Java interop
- SKIE значительно улучшает Kotlin→Swift DX
- Swift Export — правильное направление

### Negative
- SWIG complex для сложных C++ APIs
- Swift→Kotlin interop остаётся болезненным
- Swift Export не готов для production
- Много ограничений в bidirectional interop

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [SWIG Wikipedia](https://en.wikipedia.org/wiki/SWIG) | Reference | ★★★★☆ | Overview |
| [jextract Oracle Docs](https://docs.oracle.com/en/java/javase/21/core/call-native-functions-jextract.html) | Official | ★★★★★ | Java FFM guide |
| [Kotlin cinterop Docs](https://kotlinlang.org/docs/native-c-interop.html) | Official | ★★★★★ | cinterop reference |
| [SKIE Website](https://skie.touchlab.co/) | Official | ★★★★★ | Feature overview |
| [Kotlin Swift Export](https://kotlinlang.org/docs/native-swift-export.html) | Official | ★★★★☆ | Experimental feature |
| [Kotlin Swift Interopedia](https://github.com/kotlin-hands-on/kotlin-swift-interopedia) | GitHub | ★★★★☆ | Practical examples |

## Research Methodology
- **Queries used:** 2 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **Focus areas:** SWIG, jextract, cinterop, SKIE, Swift Export

---

*Проверено: 2026-01-09*

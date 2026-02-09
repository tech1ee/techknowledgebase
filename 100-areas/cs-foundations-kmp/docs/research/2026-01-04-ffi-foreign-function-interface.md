# Research Report: Foreign Function Interface (FFI)

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

FFI (Foreign Function Interface) — механизм вызова кода, написанного на одном языке, из другого. Ключевые реализации: JNI (Java ↔ C/C++), P/Invoke (.NET ↔ C), cinterop (Kotlin/Native ↔ C/Obj-C). Основные проблемы: marshalling типов (конвертация между представлениями), управление памятью (GC vs manual), overhead вызовов (~20-100ns). Objective-C использует динамический dispatch через objc_msgSend. Java 21+ вводит FFM API как замену JNI.

## Key Findings

### 1. Что такое FFI

**Определение:**
Механизм, позволяющий программе на одном языке вызывать код на другом.

**Основные задачи:**
- Использование legacy библиотек
- Доступ к системным API
- Performance-critical операции
- Hardware-specific функции

**Варианты FFI:**
| Язык/Платформа | FFI механизм |
|----------------|--------------|
| Java | JNI, JNA, FFM API (Java 21+) |
| .NET | P/Invoke, COM Interop |
| Kotlin/Native | cinterop |
| Python | ctypes, cffi |
| Rust | extern "C", bindgen |

### 2. JNI (Java Native Interface)

**Как работает:**
1. Объявление native метода в Java
2. Генерация header файла (javah)
3. Реализация на C/C++
4. Загрузка через System.loadLibrary()

**Ключевые структуры:**
- **JNIEnv** — thread-local pointer к JNI функциям
- **JavaVM** — invocation interface для создания/уничтожения JVM
- **jobject, jclass, jstring** — references на Java объекты

**Performance overhead:**
- Empty JNI call: ~22ns
- Normal JNI call: ~115ns
- @FastNative: ~35ns
- @CriticalNative: ~25ns

**Проблемы JNI:**
- Verbose boilerplate код
- Marshalling overhead
- Сложное управление references
- Нет inlining через JIT

### 3. P/Invoke (.NET)

**Как работает:**
1. DllImport атрибут на extern методе
2. CLR загружает native library
3. Marshalling параметров
4. Вызов native функции
5. Marshalling результата

**Marshalling:**
- Blittable types (int, float) — прямое копирование
- Non-blittable (string, arrays) — конвертация
- Structs — может требовать LayoutKind.Sequential

**Best practices:**
- GCHandle.Alloc для pinning объектов
- SafeHandle для ресурсов
- Избегать marshalling в hot paths

### 4. Kotlin/Native cinterop

**Механизм:**
1. .def файл описывает библиотеку
2. cinterop генерирует Kotlin bindings
3. Компиляция с native библиотекой

**Swift/Objective-C interop:**
- Kotlin/Native работает только через Objective-C
- Swift код нужно оборачивать в @objc классы
- Ограничения: inline classes, Result не поддерживаются

**Пример .def файла:**
```
language = Objective-C
modules = MyFramework
package = com.example.myframework
```

### 5. Objective-C Runtime

**objc_msgSend:**
- Центральная функция message dispatch
- Каждый вызов метода → objc_msgSend(receiver, selector, args)
- Ищет implementation в dispatch table
- Кэширует найденные методы

**Method dispatch:**
1. Проверка cache
2. Поиск в dispatch table класса
3. Поиск в superclass hierarchy
4. Message forwarding если не найдено

**Варианты:**
- objc_msgSend — обычные методы
- objc_msgSend_stret — возврат структур
- objc_msgSend_fpret — возврат float
- objc_msgSend_super — вызов super

**Performance:**
~2x медленнее C function call, но с кэшированием практически сравнимо.

### 6. Challenges: Memory Management

**Проблема GC:**
- Managed язык (Java, C#) может собрать объект
- Native код держит pointer → dangling reference
- JNI: нужны global/local references
- P/Invoke: GCHandle.Alloc с HandleType.Pinned

**Ownership:**
- Кто аллоцирует?
- Кто освобождает?
- Разные heap'ы в разных runtimes

### 7. Challenges: Type Marshalling

| Проблема | Пример |
|----------|--------|
| Размеры типов | int в C может быть 16/32/64 bit |
| Strings | UTF-8 vs UTF-16 vs null-terminated |
| Structs | Padding, alignment differences |
| Callbacks | Function pointers vs delegates |

### 8. Java FFM API (Modern Alternative)

**Преимущества над JNI:**
- Type-safe function descriptors
- Arena-based memory management
- Compile-time и runtime checks
- Инструмент jextract для генерации

**Пример:**
```java
try (Arena arena = Arena.ofConfined()) {
    MemorySegment cString = arena.allocateUtf8String("Hello");
    // Автоматическое освобождение при выходе из try
}
```

## Community Sentiment

### Positive
- FFI позволяет переиспользовать существующий код
- JNI зрелый и стабильный
- P/Invoke удобен для Windows API
- FFM API — большой шаг вперёд

### Negative
- JNI verbose и error-prone
- Marshalling overhead в hot paths
- Сложная отладка cross-language
- Memory leaks при неправильном использовании

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Wikipedia: FFI](https://en.wikipedia.org/wiki/Foreign_function_interface) | Reference | ★★★★☆ | Overview |
| [Level Up Coding: FFI Explained](https://levelup.gitconnected.com/what-is-ffi-foreign-function-interface-an-intuitive-explanation-7327444e347a) | Blog | ★★★★★ | Intuitive explanation |
| [Baeldung: JNI Guide](https://www.baeldung.com/jni) | Tutorial | ★★★★★ | Practical JNI |
| [Android: JNI Tips](https://developer.android.com/training/articles/perf-jni) | Official | ★★★★★ | Best practices |
| [Apple: Messaging](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtHowMessagingWorks.html) | Official | ★★★★★ | objc_msgSend |
| [Kotlin Docs: C Interop](https://kotlinlang.org/docs/native-c-interop.html) | Official | ★★★★★ | cinterop |
| [Microsoft: P/Invoke](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke) | Official | ★★★★★ | .NET interop |
| [RocksDB: Java FFI](https://rocksdb.org/blog/2024/02/20/foreign-function-interface.html) | Blog | ★★★★☆ | Real-world FFI |

## Research Methodology
- **Queries used:** 5 search queries
- **Sources found:** 35+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** JNI, P/Invoke, cinterop, Objective-C runtime, marshalling

---

*Проверено: 2026-01-09*

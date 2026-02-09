---
title: "FFI: как языки общаются друг с другом"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, platform-interop, ffi, jni, cinterop, native]
related:
  - "[[abi-calling-conventions]]"
  - "[[memory-model-fundamentals]]"
  - "[[bridges-bindings-overview]]"
---

# FFI: как языки общаются друг с другом

> **TL;DR:** FFI (Foreign Function Interface) — механизм вызова кода одного языка из другого. JNI связывает Java/Kotlin с C/C++ через JNIEnv и native методы (~20-100ns overhead). P/Invoke в .NET использует DllImport и marshalling. Kotlin/Native cinterop генерирует Kotlin bindings из .def файлов. Objective-C использует динамический dispatch через objc_msgSend. Главные проблемы: marshalling типов, управление памятью между GC и manual allocation, overhead вызовов.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **ABI и Calling Conventions** | Как работают вызовы на бинарном уровне | [[abi-calling-conventions]] |
| **Memory Model** | Stack/heap, указатели | [[memory-model-fundamentals]] |
| **Garbage Collection** | Автоматическое управление памятью | [[garbage-collection-explained]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **FFI** | Механизм вызова кода между языками | Переводчик между людьми разных стран |
| **Marshalling** | Преобразование данных между форматами | Конвертация валюты при переводе денег |
| **Native code** | Машинный код для конкретной платформы | Местный язык страны |
| **Binding** | Обёртка для вызова native кода | Словарь с переводом терминов |
| **JNI** | Java Native Interface | "Переводчик" между Java и C |
| **cinterop** | Kotlin/Native C interop tool | Генератор словарей для Kotlin |

---

## ПОЧЕМУ нужен FFI

### Проблема: языки живут в изоляции

Каждый язык программирования создаёт свою "вселенную":

```
┌─────────────────────────────────────────────────────────────┐
│                 ИЗОЛИРОВАННЫЕ МИРЫ                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │   KOTLIN    │    │     C       │    │   SWIFT     │    │
│   │ ───────────│    │ ───────────│    │ ───────────│    │
│   │ val x = 42 │    │ int x = 42 │    │ let x = 42 │    │
│   │ String     │    │ char*      │    │ String     │    │
│   │ GC managed │    │ manual mem │    │ ARC        │    │
│   │ JVM/Native │    │ native     │    │ native     │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│          ↑                  ↑                  ↑           │
│          └──────────────────┴──────────────────┘           │
│                  КАК ИМ ОБЩАТЬСЯ?                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Зачем языкам общаться?

| Сценарий | Пример |
|----------|--------|
| **Legacy код** | Миллионы строк C библиотек (OpenSSL, SQLite) |
| **Системные API** | Windows API, POSIX, iOS frameworks |
| **Performance** | Критичные вычисления на C/C++/Rust |
| **Hardware** | Драйверы, embedded системы |
| **Экосистема** | Использование библиотек другого языка |

### Аналогия: международная торговля

FFI похож на международную торговлю:

- **Товары** = данные (строки, числа, структуры)
- **Валюта** = представление типов (UTF-8 vs UTF-16, int vs Long)
- **Таможня** = marshalling (проверка и конвертация)
- **Договоры** = ABI (стандарты взаимодействия)

Без торговых соглашений (FFI) каждая страна (язык) была бы изолирована.

---

## ЧТО такое FFI

### Определение

**FFI (Foreign Function Interface)** — механизм, позволяющий программе вызывать функции, написанные на другом языке.

```
┌─────────────────────────────────────────────────────────────┐
│                    FFI: ОБЩАЯ СХЕМА                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   HOST LANGUAGE              GUEST LANGUAGE                │
│   (вызывающий)               (вызываемый)                  │
│                                                             │
│   ┌───────────────┐          ┌───────────────┐             │
│   │ Kotlin код    │          │ C библиотека  │             │
│   │ ─────────────│          │ ─────────────│             │
│   │ nativeFunc() │──────────▶│ native_func() │             │
│   └───────────────┘          └───────────────┘             │
│          │                          │                       │
│          │                          │                       │
│          ▼                          ▼                       │
│   ┌─────────────────────────────────────────┐              │
│   │              FFI LAYER                   │              │
│   │ ─────────────────────────────────────── │              │
│   │ 1. Marshalling параметров               │              │
│   │ 2. Вызов через ABI                      │              │
│   │ 3. Marshalling результата               │              │
│   │ 4. Управление памятью                   │              │
│   └─────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Основные FFI механизмы

| Платформа | FFI механизм | Особенности |
|-----------|--------------|-------------|
| **JVM** | JNI, JNA, FFM API | JNI verbose, FFM API (Java 21+) современный |
| **.NET** | P/Invoke, COM | DllImport, автоматический marshalling |
| **Kotlin/Native** | cinterop | Генерирует Kotlin bindings из .def |
| **Python** | ctypes, cffi | Динамическая загрузка |
| **Rust** | extern "C" | Zero-cost abstractions |

---

## JNI: Java Native Interface

### Как работает JNI

JNI — мост между JVM и native кодом:

```
┌─────────────────────────────────────────────────────────────┐
│                    JNI ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   JAVA/KOTLIN                JNI LAYER              C/C++  │
│   ──────────                 ─────────              ─────  │
│                                                             │
│   class Native {        ┌─────────────────┐    #include   │
│     external fun        │                 │    <jni.h>    │
│       greet(): String   │    JNIEnv*      │               │
│   }                     │    ┌─────────┐  │    JNIEXPORT  │
│         │               │    │ function│  │    jstring    │
│         │               │    │ table   │  │    Java_...   │
│         ▼               │    └─────────┘  │    _greet()   │
│   Native.greet()───────▶│                 │──────▶{...}   │
│         │               │    JavaVM*      │       │       │
│         │               │    ┌─────────┐  │       │       │
│         │               │    │ JVM     │  │       │       │
│         │               │    │ control │  │       │       │
│         │               │    └─────────┘  │       │       │
│         ◀───────────────│                 │◀──────┘       │
│   "Hello!"              └─────────────────┘  "Hello!"     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Ключевые структуры JNI

**JNIEnv** — указатель на таблицу функций JNI:
- Работа с объектами (NewObject, GetField)
- Работа со строками (NewStringUTF, GetStringChars)
- Работа с массивами (NewIntArray, GetArrayElements)
- Вызов Java методов (CallVoidMethod)

**JavaVM** — контроль над JVM:
- Получение JNIEnv для текущего потока
- Attach/Detach потоков

### Пример JNI

```kotlin
// Kotlin: объявление native метода
class Greeter {
    external fun greet(name: String): String

    companion object {
        init {
            System.loadLibrary("greeter")
        }
    }
}
```

```c
// C: реализация
#include <jni.h>

JNIEXPORT jstring JNICALL
Java_Greeter_greet(JNIEnv *env, jobject thiz, jstring name) {
    // 1. Получить C-строку из Java String
    const char *nameChars = (*env)->GetStringUTFChars(env, name, NULL);

    // 2. Сформировать результат
    char result[256];
    snprintf(result, sizeof(result), "Hello, %s!", nameChars);

    // 3. Освободить ресурсы
    (*env)->ReleaseStringUTFChars(env, name, nameChars);

    // 4. Вернуть Java String
    return (*env)->NewStringUTF(env, result);
}
```

### JNI Performance

```
┌─────────────────────────────────────────────────────────────┐
│                 JNI CALL OVERHEAD                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Тип вызова                    Время (ns)                 │
│   ──────────────────────────────────────────                │
│   Pure Java method call         ~1-5 ns                    │
│   JNI empty call                ~22 ns                     │
│   Normal JNI call               ~115 ns                    │
│   @FastNative (Android)         ~35 ns                     │
│   @CriticalNative (Android)     ~25 ns                     │
│                                                             │
│   Почему JNI медленнее:                                    │
│   - Переход между managed и native stack                   │
│   - Thread state transition                                │
│   - Marshalling параметров                                 │
│   - JIT не может инлайнить native методы                   │
│                                                             │
│   Правило: JNI выгоден когда computation >> call overhead  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### JNI References

JNI использует систему references для защиты объектов от GC:

| Тип Reference | Scope | Когда использовать |
|---------------|-------|-------------------|
| **Local** | Один native вызов | По умолчанию |
| **Global** | До явного удаления | Кэширование объектов |
| **Weak Global** | До GC объекта | Необязательное кэширование |

```c
// Создание global reference
jclass clsCache;

JNIEXPORT void JNICALL
Java_Cache_init(JNIEnv *env, jobject thiz) {
    // Без Global reference: clsCache станет invalid после возврата!
    jclass localRef = (*env)->FindClass(env, "java/lang/String");
    clsCache = (*env)->NewGlobalRef(env, localRef);
    (*env)->DeleteLocalRef(env, localRef);
}

// Освобождение
JNIEXPORT void JNICALL
Java_Cache_cleanup(JNIEnv *env, jobject thiz) {
    (*env)->DeleteGlobalRef(env, clsCache);
}
```

---

## Objective-C Runtime и objc_msgSend

### Динамический dispatch

Objective-C использует message passing вместо прямых вызовов:

```
┌─────────────────────────────────────────────────────────────┐
│              OBJECTIVE-C MESSAGE DISPATCH                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   [object doSomething:arg]                                 │
│           ↓                                                 │
│   objc_msgSend(object, @selector(doSomething:), arg)       │
│           ↓                                                 │
│   ┌─────────────────────────────────────────┐              │
│   │ 1. Проверить cache класса               │              │
│   │    ├── Hit → вызвать IMP напрямую      │              │
│   │    └── Miss → продолжить поиск          │              │
│   │                                         │              │
│   │ 2. Поиск в dispatch table класса        │              │
│   │    selector → IMP (implementation)      │              │
│   │                                         │              │
│   │ 3. Поиск в superclass hierarchy         │              │
│   │    NSObject → ... → class               │              │
│   │                                         │              │
│   │ 4. Message forwarding (если не найдено) │              │
│   │    - forwardingTargetForSelector:       │              │
│   │    - methodSignatureForSelector:        │              │
│   │    - forwardInvocation:                 │              │
│   └─────────────────────────────────────────┘              │
│           ↓                                                 │
│   Вызов IMP (function pointer)                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Почему Kotlin/Native использует Objective-C

Kotlin/Native не может напрямую вызывать Swift код:

```
┌─────────────────────────────────────────────────────────────┐
│          KOTLIN/NATIVE ↔ SWIFT INTEROP                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Kotlin/Native ←──╳──→ Swift (напрямую нельзя)           │
│        │                                                    │
│        │                                                    │
│        ▼                                                    │
│   Kotlin/Native ←────→ Objective-C ←────→ Swift            │
│        │                    │                  │            │
│        │                    │                  │            │
│        │               @objc class             │            │
│        │               @objc func              │            │
│        │                    │                  │            │
│        └────────────────────┴──────────────────┘            │
│                                                             │
│   Swift код должен быть доступен через Obj-C header:       │
│   - Класс наследует NSObject                               │
│   - Методы помечены @objc                                  │
│   - Типы совместимы с Obj-C                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Kotlin/Native cinterop

### Как работает cinterop

```
┌─────────────────────────────────────────────────────────────┐
│                 CINTEROP WORKFLOW                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. СОЗДАНИЕ .def ФАЙЛА                                   │
│      ┌─────────────────────────────┐                       │
│      │ language = Objective-C      │                       │
│      │ modules = MyFramework       │                       │
│      │ package = com.example       │                       │
│      │ headers = MyHeader.h        │                       │
│      └─────────────────────────────┘                       │
│                    │                                        │
│                    ▼                                        │
│   2. ГЕНЕРАЦИЯ BINDINGS (cinterop tool)                    │
│      ┌─────────────────────────────┐                       │
│      │ Парсинг C/Obj-C headers     │                       │
│      │ Генерация Kotlin stubs      │                       │
│      │ Создание .klib              │                       │
│      └─────────────────────────────┘                       │
│                    │                                        │
│                    ▼                                        │
│   3. ИСПОЛЬЗОВАНИЕ В KOTLIN                                │
│      ┌─────────────────────────────┐                       │
│      │ import com.example.*        │                       │
│      │ val result = myNativeFunc() │                       │
│      └─────────────────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Пример: вызов C функции

```
// native/nativeInterop/cinterop/mylib.def
headers = mylib.h
package = com.example.mylib
```

```c
// mylib.h
int add(int a, int b);
char* greet(const char* name);
```

```kotlin
// Kotlin использование (автоматически сгенерировано)
import com.example.mylib.*

fun main() {
    val sum = add(10, 20)  // Вызов C функции
    println("Sum: $sum")

    val greeting = greet("World")?.toKString()
    println(greeting)
}
```

### Маппинг типов

| C тип | Kotlin/Native тип |
|-------|-------------------|
| `int` | `Int` |
| `long` | `Long` |
| `float` | `Float` |
| `char*` | `CPointer<ByteVar>` |
| `void*` | `COpaquePointer` |
| `struct X` | `CValue<X>` |
| `enum` | Kotlin enum или Int |

---

## Проблемы FFI

### 1. Type Marshalling

```
┌─────────────────────────────────────────────────────────────┐
│                 MARSHALLING CHALLENGES                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ПРОБЛЕМА: Разное представление типов                     │
│                                                             │
│   Strings:                                                  │
│   Java/Kotlin: UTF-16, length-prefixed, объект             │
│   C:           char*, null-terminated, UTF-8 или ASCII     │
│   Swift:       String, bridged to NSString                 │
│                                                             │
│   Integers:                                                 │
│   C int:       платформо-зависимый (16/32/64 bit)          │
│   Java int:    всегда 32 bit                               │
│   Kotlin Int:  32 bit на всех платформах                   │
│                                                             │
│   Structs:                                                  │
│   C:           padding, alignment                          │
│   Kotlin:      data class (другой layout)                  │
│                                                             │
│   РЕШЕНИЕ: Явный marshalling                               │
│   - JNI: GetStringUTFChars / NewStringUTF                  │
│   - P/Invoke: MarshalAs attribute                          │
│   - cinterop: toKString() / cstr                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Memory Management

```
┌─────────────────────────────────────────────────────────────┐
│               MEMORY MANAGEMENT CONFLICT                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   MANAGED (GC)              │        NATIVE (Manual)       │
│   ────────────────────────  │  ──────────────────────────  │
│   Kotlin/JVM: GC управляет  │  C: malloc/free вручную      │
│   Kotlin/Native: GC + ARC   │  C++: new/delete             │
│                             │  Rust: ownership             │
│                             │                              │
│   ПРОБЛЕМЫ:                                                 │
│                                                             │
│   1. GC может переместить объект                           │
│      Native код держит старый pointer → crash              │
│      Решение: pinning (GCHandle, GlobalRef)                │
│                                                             │
│   2. Кто владеет памятью?                                  │
│      Native аллоцировал → native должен освободить        │
│      Managed аллоцировал → GC освободит когда-то          │
│                                                             │
│   3. Разные heap'ы                                         │
│      JVM heap ≠ Native heap                                │
│      Нельзя free() на память из JVM                        │
│                                                             │
│   ПРАВИЛО: Чётко определить ownership на границе          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Call Overhead

Каждый FFI вызов имеет overhead:

| Операция | Примерное время |
|----------|-----------------|
| Java method call | 1-5 ns |
| JNI transition | 20-100 ns |
| Parameter marshalling | 10-1000 ns (зависит от типа) |
| Return marshalling | 10-1000 ns |

**Вывод:** FFI выгоден для "толстых" операций, где computation >> overhead.

---

## Практические паттерны

### Паттерн: Batch Operations

```kotlin
// ❌ Плохо: много мелких вызовов
for (i in 0 until 1000) {
    nativeProcess(data[i])  // 1000 × JNI overhead
}

// ✅ Хорошо: один вызов с batch данными
nativeProcessBatch(data, 1000)  // 1 × JNI overhead
```

### Паттерн: Cache IDs

```c
// ❌ Плохо: поиск каждый раз
JNIEXPORT void JNICALL Java_Example_method(JNIEnv *env, jobject thiz) {
    jclass cls = (*env)->FindClass(env, "java/lang/String");  // Slow!
    jmethodID mid = (*env)->GetMethodID(env, cls, "length", "()I");  // Slow!
    // ...
}

// ✅ Хорошо: кэширование при инициализации
static jclass stringClass;
static jmethodID lengthMethod;

JNIEXPORT void JNICALL Java_Example_init(JNIEnv *env, jclass cls) {
    jclass localRef = (*env)->FindClass(env, "java/lang/String");
    stringClass = (*env)->NewGlobalRef(env, localRef);
    lengthMethod = (*env)->GetMethodID(env, stringClass, "length", "()I");
}
```

### Паттерн: Wrapper для Swift

```swift
// Swift код, недоступный напрямую из Kotlin
class SwiftOnlyClass {
    func doSomething() -> String { "Hello" }
}

// Objective-C wrapper для Kotlin
@objc class SwiftBridge: NSObject {
    private let impl = SwiftOnlyClass()

    @objc func doSomething() -> String {
        return impl.doSomething()
    }
}
```

```kotlin
// Kotlin через cinterop
val bridge = SwiftBridge()
val result = bridge.doSomething()
```

---

## Подводные камни

### Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Забыли ReleaseStringUTFChars | Memory leak | Всегда парные операции |
| Local ref после native return | Invalid reference | Global ref для хранения |
| Marshalling в hot loop | Performance degradation | Batch operations |
| Не проверили исключения | Silent failures | Check ExceptionCheck() |

### Мифы и заблуждения

**Миф:** "JNI всегда быстрее Java"
**Реальность:** JNI имеет overhead ~100ns на вызов. Для простых операций (сложение чисел) чистый Kotlin быстрее. JNI выгоден для тяжёлых вычислений.

**Миф:** "Kotlin/Native может вызывать любой Swift код"
**Реальность:** Только через Objective-C. Swift-only типы (struct, enum с associated values) недоступны напрямую.

**Миф:** "FFI — это просто"
**Реальность:** FFI требует понимания обоих языков, ABI, управления памятью и marshalling. Это одна из самых сложных областей в программировании.

---

## Куда дальше

**Если здесь впервые:**
→ Попробуй простой JNI пример: Java + C функция сложения

**Если понял и хочешь глубже:**
→ [[memory-layout-marshalling]] — структуры, padding, alignment

**Практическое применение:**
→ Kotlin/Native cinterop для iOS frameworks

---

## Источники

- [Wikipedia: Foreign Function Interface](https://en.wikipedia.org/wiki/Foreign_function_interface) — overview
- [Baeldung: JNI Guide](https://www.baeldung.com/jni) — practical JNI tutorial
- [Android: JNI Tips](https://developer.android.com/training/articles/perf-jni) — best practices
- [Apple: Objective-C Runtime](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtHowMessagingWorks.html) — objc_msgSend
- [Kotlin Docs: C Interop](https://kotlinlang.org/docs/native-c-interop.html) — cinterop reference
- [Microsoft: P/Invoke](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke) — .NET interop

---

*Проверено: 2026-01-09*

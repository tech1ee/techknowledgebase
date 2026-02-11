---
title: "FFI: как языки общаются друг с другом"
created: 2026-01-04
modified: 2026-02-10
type: deep-dive
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/advanced
related:
  - "[[abi-calling-conventions]]"
  - "[[memory-model-fundamentals]]"
  - "[[bridges-bindings-overview]]"
prerequisites:
  - "[[memory-model-fundamentals]]"
  - "[[compilation-pipeline]]"
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

## Зачем это знать

Каждый мобильный разработчик рано или поздно сталкивается с FFI. На Android ты вызываешь C/C++ через JNI для работы с OpenGL, аудиокодеками, криптографией. На iOS ты взаимодействуешь со Swift/Objective-C фреймворками. В Kotlin Multiplatform ты используешь cinterop для доступа к платформенным API. Даже если ты не пишешь FFI-код напрямую, библиотеки, которые ты используешь (SQLite, Realm, OpenSSL), работают через FFI.

Без понимания FFI ты не сможешь объяснить, почему JNI-вызовы в tight loop замедляют приложение в 20 раз. Почему Kotlin/Native не может напрямую вызвать Swift struct. Почему память "утекает" при неправильном использовании JNI references. Всё это — вопросы FFI.

> **Ключевая идея:** FFI — это "переводчик" между языками программирования. Как переводчик-синхронист на международной конференции, он обеспечивает общение, но добавляет задержку и может исказить тонкости значения.

---

## Историческая справка

Проблема межъязыкового взаимодействия стара как сами языки программирования. В 1970-80-х годах большинство системного ПО писалось на C, и когда появились новые языки (Fortran для научных вычислений, Lisp для AI), возникла потребность вызывать C-библиотеки из этих языков.

Fortran был одним из первых языков с формальным FFI — механизмом `EXTERNAL`, позволявшим вызывать C-функции. Но каждый язык изобретал свой подход, и это создавало хаос.

В 1996 году Sun Microsystems выпустила **JNI** (Java Native Interface) как часть JDK 1.1. Это был один из первых стандартизированных FFI-механизмов, разработанный с учётом безопасности и переносимости. JNI должен был решить конкретную проблему: Java работает на виртуальной машине (JVM) с garbage collector, а C/C++ код работает напрямую с аппаратным обеспечением. Мост между этими двумя мирами оказался сложнее, чем казалось. Sheng Liang, один из авторов JNI, написал книгу "The Java Native Interface" (1999), ставшую каноническим справочником.

В 2010-х годах с появлением Kotlin/Native JetBrains создала **cinterop** — инструмент, который автоматически генерирует Kotlin bindings из C/Objective-C header-файлов. Подход принципиально отличается от JNI: вместо ручного написания glue code (склеивающего кода), cinterop анализирует заголовочные файлы и генерирует типизированные Kotlin-обёртки. Это стало возможным благодаря использованию LLVM — той же инфраструктуры компиляции, которую используют Clang и Swift.

В 2021 году Java представила **Foreign Function & Memory API** (Project Panama, JEP 412), который должен заменить JNI. Причина — JNI слишком verbose, небезопасен и медленен. FFM API использует modern Java features (records, sealed classes) и предоставляет более безопасный доступ к native памяти.

---

## ПОЧЕМУ нужен FFI

### Проблема: разные языки, одна система

Представь команду архитекторов, где каждый говорит на своём языке. Один рисует чертёж в метрической системе, другой — в имперской. Один использует ISO-стандарты, другой — национальные. Чтобы они могли работать вместе, нужен "переводчик" — человек (или система), который переводит чертежи из одного формата в другой.

FFI — именно такой переводчик, но для языков программирования. Проблема в том, что каждый язык создаёт свой изолированный мир со своими правилами: своё представление строк, свой способ управления памятью, свой формат вызова функций.

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

## JNI: мост между Java и C

### ПОЧЕМУ JNI — это именно мост

Чтобы понять JNI, нужно представить два разных города, разделённых рекой. На одном берегу — город JVM: аккуратные дома с автоматической уборкой мусора (GC), строгой регистрацией жителей (type safety), системой безопасности (SecurityManager). На другом берегу — город Native: свободный, быстрый, но без централизованной уборки мусора, без регистрации — каждый сам за себя.

JNI — это мост между этими городами. На мосту стоит таможня (JNIEnv), которая проверяет каждого "путешественника" (объект/данные), конвертирует "документы" (marshalling типов) и следит, чтобы ничего не потерялось.

Почему нужен именно мост, а не простой переход? Потому что эти два мира работают по принципиально разным правилам:

- **JVM управляет памятью автоматически** — GC может переместить объект в любой момент. Native-код, хранящий указатель на объект, внезапно получит мусор.
- **JVM использует UTF-16 для строк** — C использует char* с нуль-терминатором в UTF-8 или ASCII. Прямая передача невозможна.
- **JVM проверяет типы** — в C можно привести любой pointer к любому типу. JNI должен обеспечить type safety на границе.

Именно поэтому JNI не просто "вызывает функцию" — он выполняет целый протокол перехода между мирами.

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

## Kotlin/Native cinterop: подход через LLVM

### ПОЧЕМУ cinterop работает иначе, чем JNI

JNI требует ручного написания "склеивающего кода" на C — boilerplate, в котором легко допустить ошибку. Kotlin/Native выбрал принципиально другой подход: **генерация bindings из заголовочных файлов**.

Аналогия: JNI — это как нанимать переводчика-человека для каждого разговора. Ты объясняешь ему, что сказать, он переводит, приносит ответ. Cinterop — это как машинный перевод: ты даёшь ему текст (header файл), и он автоматически генерирует перевод (Kotlin bindings).

Ключевая особенность — cinterop использует **ту же инфраструктуру LLVM**, что и Clang (компилятор C/C++/Objective-C). Это означает, что cinterop *понимает* C-типы, структуры, макросы и даже некоторые Objective-C конструкции так же точно, как их понимает сам C-компилятор. Это не текстовый парсинг — это полноценный семантический анализ.

Второе принципиальное отличие: Kotlin/Native компилируется в native-код (через LLVM), а не работает на виртуальной машине. Поэтому вызов C-функции из Kotlin/Native — это прямой вызов native-функции по тому же ABI, без перехода между managed и native средами. Нет JVM, нет mode switch, нет marshalling в том объёме, как в JNI. Единственное, что нужно — конвертация Kotlin-типов в C-типы на уровне компилятора.

Однако это не означает, что проблем нет. Kotlin/Native использует свой garbage collector, а C-код управляет памятью вручную. Передача объектов между этими двумя мирами по-прежнему требует аккуратности — кто владеет памятью, кто её освобождает, когда GC может "забрать" объект.

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

## КАКИЕ проблемы создаёт пересечение границы памяти

### Два мира управления памятью

Самая глубокая проблема FFI — столкновение двух несовместимых философий управления памятью. Это не просто техническая деталь — это фундаментальный конфликт дизайна, который невозможно полностью устранить, можно лишь аккуратно обойти.

**Мир GC (Garbage Collection):** Java, Kotlin/JVM, C#, Go. Программист создаёт объекты и забывает о них. GC периодически сканирует память, находит "мёртвые" объекты (на которые никто не ссылается) и освобождает их. Главное — GC может **перемещать** объекты в памяти (compacting GC), то есть адрес объекта не фиксирован.

**Мир ручного управления:** C, C++, Rust. Программист явно выделяет память (`malloc`) и освобождает её (`free`). Адрес объекта фиксирован на всё время его жизни. Забыл освободить — утечка. Освободил дважды — crash. Это цена полного контроля.

Когда эти два мира встречаются на границе FFI, возникают три фундаментальных проблемы.

**Проблема 1: Перемещение объектов.** Ты передал указатель на Java-объект в C-код. GC решил сделать compaction и переместил объект. C-код по-прежнему хранит старый адрес — теперь это мусор, и следующее обращение по этому адресу — crash (или, хуже, тихое повреждение данных). Решение — "закрепление" (pinning): JNI использует GlobalRef, который говорит GC "не трогай этот объект". Но pinning снижает эффективность GC, потому что создаёт "острова" в памяти, вокруг которых GC не может сделать compaction.

**Проблема 2: Время жизни.** C-функция вернула указатель на строку `char*`. Кто отвечает за освобождение этой памяти? Если C-код аллоцировал через `malloc` — Kotlin/Native не может просто отдать этот указатель GC. Нужно явно вызвать `free()`. Если Kotlin-код передал строку в C — C не может управлять её жизнью, потому что строка принадлежит Kotlin GC.

**Проблема 3: Разные heap.** JVM heap и native heap — разные области памяти. Нельзя вызвать `free()` на память из JVM heap. Нельзя передать указатель на native heap в GC. Это как две банковские системы в разных странах — перевод возможен, но требует конвертации и комиссии.

> **Ключевая идея:** На границе FFI всегда должно быть чёткое правило ownership: кто аллоцировал память — тот и освобождает. Нарушение этого правила — самый частый источник багов в FFI-коде.

Мы разобрали фундаментальную проблему памяти. Но есть и другие проблемы, менее драматичные, но не менее важные.

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

## Связь с другими темами

Понимание FFI стоит на стыке нескольких фундаментальных областей, и чтение связанных материалов создаёт целостную картину.

**[[abi-calling-conventions]]** — ABI определяет "протокол", по которому FFI вызывает native-функции. Без понимания calling conventions невозможно понять, как передаются аргументы через FFI-границу. Рекомендуется прочитать ABI перед этой статьёй.

**[[memory-model-fundamentals]]** — FFI тесно связан с пониманием памяти: stack vs heap, указатели, время жизни объектов. Проблемы ownership на границе FFI невозможно понять без знания того, как работают heap и GC. Рекомендуется как prerequisite.

**[[memory-layout-marshalling]]** — marshalling данных между языками требует знания, как данные раскладываются в памяти: padding, alignment, endianness. Эта статья объясняет ЗАЧЕМ нужен marshalling, memory-layout-marshalling объясняет КАК он работает на уровне байтов.

**[[garbage-collection-explained]]** — конфликт GC vs manual memory management — центральная проблема FFI. Понимание того, как GC перемещает объекты, делает compaction, определяет "живые" объекты, объясняет, ПОЧЕМУ FFI-код требует pinning и explicit lifetime management.

---

## Источники и дальнейшее чтение

- Liang, S. (1999). *The Java Native Interface: Programmer's Guide and Specification*. — Каноническая книга от одного из авторов JNI. Объясняет не только API, но и design decisions: почему JNI устроен именно так, какие альтернативы рассматривались и отвергались. Обязательна для тех, кто пишет JNI-код.
- Bryant, R. & O'Hallaron, D. (2015). *Computer Systems: A Programmer's Perspective*. — Глава 7 (Linking) объясняет, как динамические библиотеки загружаются и связываются, что является фундаментом для понимания FFI на бинарном уровне.
- [Android Developer: JNI Tips](https://developer.android.com/training/articles/perf-jni) — практическое руководство от Google по правильному использованию JNI на Android. Содержит конкретные рекомендации по производительности и управлению памятью.
- [Kotlin Docs: C Interop](https://kotlinlang.org/docs/native-c-interop.html) — официальная документация по cinterop. Объясняет формат .def файлов, маппинг типов и работу с Objective-C frameworks.
- [Apple: Objective-C Runtime Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/) — объясняет message dispatch, objc_msgSend и runtime-механизмы, через которые Kotlin/Native взаимодействует с iOS.
- [JEP 454: Foreign Function & Memory API](https://openjdk.org/jeps/454) — спецификация нового FFI для Java, призванного заменить JNI. Полезно для понимания, какие проблемы JNI не решил и как их адресует новый подход.

---

*Проверено: 2026-02-10*

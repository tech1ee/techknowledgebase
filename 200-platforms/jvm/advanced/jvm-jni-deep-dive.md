---
title: "JVM JNI - Java Native Interface"
tags:
  - topic/jvm
  - jni
  - native
  - c
  - cpp
  - interop
  - performance
  - type/deep-dive
  - level/advanced
prerequisites:
  - "[[jvm-basics-history]]"
  - "[[jvm-memory-model]]"
  - "[[jvm-class-loader-deep-dive]]"
sources:
  - jni-specification
  - oracle-jni-guide
  - openjdk-jni
confidence: high
date: 2025-11-25
modified: 2026-02-13
reading_time: 20
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
related:
  - "[[ffi-foreign-function-interface]]"
  - "[[kmp-interop-deep-dive]]"
  - "[[cross-interop]]"
---

# JVM JNI - Java Native Interface

## TL;DR

**JNI (Java Native Interface)** позволяет Java коду вызывать **нативный C/C++ код** и наоборот. Используется для работы с системными API, интеграции legacy библиотек и экстремальной оптимизации производительности.

**Ключевые концепции:**
- **Native методы** — Java методы с реализацией на C/C++
- **JNIEnv** — интерфейс для вызова JVM функций (thread-local)
- **JavaVM** — глобальный указатель на экземпляр JVM
- **Управление памятью** — ручное в C, автоматическое в Java
- **Типы ссылок** — local, global, weak (важно для GC)

**Когда использовать:**
- ✅ Вызов системных API, недоступных в Java
- ✅ Интеграция существующих C/C++ библиотек
- ✅ Прямой доступ к hardware
- ✅ Критичная производительность (SIMD, низкоуровневые оптимизации)
- ❌ Простые задачи (используйте чистый Java)
- ❌ Когда достаточно JNA или Panama Project

**Современные альтернативы:**
- **JNA** — вызов нативных функций без написания C кода
- **Panama Project (JEP 424)** — современный API для работы с нативным кодом
- **GraalVM Native Image** — компиляция Java в нативный бинарник

---

## Проблема: Зачем вызывать нативный код?

> **Аналогия из жизни: переводчик при деловых переговорах.** Представьте встречу двух бизнесменов, говорящих на разных языках. Каждый прекрасно работает в своей среде, но для взаимодействия нужен переводчик. Переводчик (JNI) принимает фразу от одной стороны (Java), конвертирует её в понятный формат (C-типы), передаёт другой стороне и возвращает ответ обратно. Перевод стоит времени (overhead вызова ~20ns), поэтому для короткого «Да/Нет» вызывать переводчика нерационально — лучше объясниться жестами (использовать чистый Java). Но для сложных технических переговоров (системные API, SIMD-оптимизации) переводчик незаменим.

> **Аналогия из жизни: посольство и визовый режим.** JNI-граница между Java и C — как граница между двумя странами с разными законами. В «стране Java» действует автоматическая уборка (GC), строгие правила поведения (type safety) и запрет на опасные действия (memory safety). В «стране C» полная свобода: можно строить что угодно (malloc), но и убирать за собой нужно самому (free). Пересечение границы требует «паспортного контроля» (JNIEnv), конвертации «валюты» (типов данных), а забытый «мусор» на чужой территории (утечка памяти) никто не уберёт за вас. Local references — это «однодневная виза» (действует только на время вызова), global references — «вид на жительство» (действует пока явно не аннулирован).

### Сценарий 1: Системные API

Java предоставляет кросс-платформенное API, но некоторые возможности ОС недоступны напрямую:

```java
public class SystemMonitor {
    // Получить температуру CPU (нет в стандартной Java)
    public native double getCPUTemperature();

    // Установить приоритет процесса (ограничено в Java)
    public native void setProcessPriority(int priority);

    // Доступ к hardware сенсорам
    public native int[] getHardwareSensors();
}
```

**Почему нужен JNI:**
- Java Core API не покрывает все возможности ОС
- Каждая платформа имеет уникальные API (Windows API, Linux syscalls, macOS frameworks)
- Для низкоуровневого доступа к системе нужен нативный код

### Сценарий 2: Интеграция legacy библиотек

У компании может быть критичная C/C++ библиотека, написанная годами:

```java
public class ImageProcessor {
    // Использование оптимизированной C библиотеки для обработки изображений
    public native byte[] processImage(byte[] imageData, int width, int height);

    // Вызов проприетарной C библиотеки
    public native void encryptData(byte[] data, byte[] key);
}
```

**Почему JNI:**
- Переписывать на Java дорого и рискованно
- C/C++ библиотека уже отлажена и работает
- Может содержать аппаратные оптимизации (SIMD, assembly)

### Сценарий 3: Экстремальная производительность

В редких случаях нативный код даёт значительный прирост:

```java
public class CryptoNative {
    // AES шифрование с использованием AES-NI инструкций CPU
    public native byte[] aesEncrypt(byte[] plaintext, byte[] key);

    // Матричное умножение с SIMD оптимизациями
    public native double[][] matrixMultiply(double[][] a, double[][] b);
}
```

**Когда это оправдано:**
- Операция выполняется миллионы раз в секунду
- Можно использовать специальные CPU инструкции (SIMD, AES-NI)
- Профилирование показало узкое место именно здесь
- **Важно:** JIT компилятор часто делает Java код настолько же быстрым!

---

## Архитектура JNI

### Компоненты системы

```
┌─────────────────────────────────────────────┐
│         Java Приложение                     │
│                                             │
│  public class Main {                        │
│    static {                                 │
│      System.loadLibrary("native");          │  ← Загрузка .so/.dll
│    }                                        │
│    public native int add(int a, int b);     │  ← Объявление native метода
│  }                                          │
└──────────────────┬──────────────────────────┘
                   │
                   ↓  JNI граница
┌──────────────────────────────────────────────┐
│  Нативная библиотека (libnative.so/dll)     │
│                                             │
│  JNIEXPORT jint JNICALL                     │
│  Java_Main_add(JNIEnv *env, jobject obj,    │  ← Реализация на C
│                jint a, jint b) {            │
│    return a + b;                            │
│  }                                          │
└─────────────────────────────────────────────┘

Управление памятью:
┌─────────────────────────────────┐
│  JVM Heap (управляется GC)      │  ← Java объекты, автоматическая память
│  - Objects, Strings, Arrays     │
└────────┬────────────────────────┘
         │ Передача ссылок через JNI
         ↓
┌─────────────────────────────────┐
│  Native Memory (ручное)         │  ← C структуры, malloc/free
│  - C structs, malloc/free       │
│  - JNI ссылки (jobject, jstring)│
└─────────────────────────────────┘
```

**Ключевые моменты:**
- **Граница JNI** — переход между управляемым (Java) и неуправляемым (C) кодом
- **JVM Heap** — GC автоматически управляет памятью Java объектов
- **Native Memory** — в C нужно вручную выделять (malloc) и освобождать (free) память
- **Ссылки через границу** — Java объекты передаются как непрозрачные указатели (jobject)

### JNIEnv и JavaVM

**JNIEnv** — основной интерфейс для работы с JVM из C кода:

```c
// JNIEnv: Per-thread интерфейс к JVM
// НЕЛЬЗЯ передавать между потоками!
JNIEXPORT void JNICALL Java_Example_method(JNIEnv *env, jobject obj) {
    // env содержит все JNI функции:

    // Найти класс
    jclass stringClass = (*env)->FindClass(env, "java/lang/String");

    // Получить ID метода
    jmethodID lengthMethod = (*env)->GetMethodID(env, stringClass, "length", "()I");

    // Создать строку
    jstring str = (*env)->NewStringUTF(env, "Hello");

    // Вызвать метод
    jint len = (*env)->CallIntMethod(env, str, lengthMethod);
}
```

**JavaVM** — глобальный указатель на JVM:

```c
// JavaVM: Глобальный экземпляр JVM
// Можно передавать между потоками
JavaVM *jvm;  // Сохраняем при загрузке библиотеки

void* nativeThread(void* arg) {
    JNIEnv *env;

    // Присоединяем нативный поток к JVM
    (*jvm)->AttachCurrentThread(jvm, (void**)&env, NULL);

    // Теперь можем вызывать Java код через env

    // Отсоединяемся при завершении
    (*jvm)->DetachCurrentThread(jvm);
    return NULL;
}
```

**Почему два интерфейса:**
- **JNIEnv** — содержит все функции, но привязан к потоку (thread-local state)
- **JavaVM** — минимальный интерфейс, можно передавать между потоками
- Каждый поток получает свой JNIEnv через AttachCurrentThread

---

## Создание native метода (пошагово)

### Шаг 1: Объявить native метод в Java

```java
// Main.java
public class Main {
    // Загрузка нативной библиотеки
    static {
        System.loadLibrary("native");  // Ищет libnative.so или native.dll
    }

    // Объявление native методов (без реализации)
    public native int add(int a, int b);
    public native String greet(String name);

    public static void main(String[] args) {
        Main m = new Main();
        System.out.println("5 + 3 = " + m.add(5, 3));        // → 8
        System.out.println(m.greet("Мир"));                  // → "Привет, Мир!"
    }
}
```

### Шаг 2: Сгенерировать C header

```bash
# Компилируем Java класс
javac Main.java

# Генерируем header (Java 10+)
javac -h . Main.java

# Создастся Main.h с объявлениями функций
```

**Сгенерированный Main.h:**

```c
// Main.h (автоматически созданный)
#include <jni.h>

// Сигнатура метода add
JNIEXPORT jint JNICALL Java_Main_add
  (JNIEnv *, jobject, jint, jint);

// Сигнатура метода greet
JNIEXPORT jstring JNICALL Java_Main_greet
  (JNIEnv *, jobject, jstring);
```

**Важные детали имени функции:**
- `Java_` — префикс для всех JNI функций
- `Main` — имя Java класса
- `add` — имя метода
- Для пакетов: `Java_com_example_Main_add` (пакет → подчёркивания)

### Шаг 3: Реализовать на C

```c
// Main.c
#include "Main.h"
#include <string.h>
#include <stdio.h>

// Простая арифметика — передаются примитивы напрямую
JNIEXPORT jint JNICALL Java_Main_add
  (JNIEnv *env, jobject obj, jint a, jint b) {
    return a + b;  // Никаких преобразований не нужно
}

// Работа со строками — требуется конвертация
JNIEXPORT jstring JNICALL Java_Main_greet
  (JNIEnv *env, jobject obj, jstring name) {

    // 1. Конвертация jstring → C строка
    const char *nativeName = (*env)->GetStringUTFChars(env, name, NULL);
    if (nativeName == NULL) {
        return NULL;  // OutOfMemoryError уже выброшен
    }

    // 2. Работа с C строкой
    char greeting[256];
    snprintf(greeting, sizeof(greeting), "Привет, %s!", nativeName);

    // 3. ВАЖНО: Освободить C строку (память выделена JVM)
    (*env)->ReleaseStringUTFChars(env, name, nativeName);

    // 4. Конвертация C строка → jstring
    return (*env)->NewStringUTF(env, greeting);
}
```

**Ключевые моменты:**
- **Примитивы** (int, double) передаются напрямую, быстро
- **Строки** требуют конвертации UTF-8 ↔ Java String (медленно!)
- **Всегда освобождайте** ресурсы (ReleaseStringUTFChars)
- **Проверяйте NULL** — операции могут вызвать OutOfMemoryError

### Шаг 4: Компиляция библиотеки

```bash
# Linux
gcc -shared -fPIC -o libnative.so Main.c \
    -I${JAVA_HOME}/include \
    -I${JAVA_HOME}/include/linux

# macOS
gcc -dynamiclib -o libnative.dylib Main.c \
    -I${JAVA_HOME}/include \
    -I${JAVA_HOME}/include/darwin

# Windows
gcc -shared -o native.dll Main.c \
    -I"%JAVA_HOME%\include" \
    -I"%JAVA_HOME%\include\win32"
```

### Шаг 5: Запуск

```bash
# Linux/macOS: добавить директорию с библиотекой в PATH
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH

# Или указать путь явно
java -Djava.library.path=. Main
```

---

## Типы данных и их маппинг

### Примитивы (быстро, без копирования)

```
Java Type    JNI Type    C Type       Размер    Примечания
─────────────────────────────────────────────────────────────
boolean      jboolean    uint8_t      1 байт    0 или 1
byte         jbyte       int8_t       1 байт    -128..127
char         jchar       uint16_t     2 байта   UTF-16 код
short        jshort      int16_t      2 байта
int          jint        int32_t      4 байта
long         jlong       int64_t      8 байт
float        jfloat      float        4 байта   IEEE 754
double       jdouble     double       8 байт    IEEE 754
void         void        void         -
```

**Пример использования:**

```c
JNIEXPORT jdouble JNICALL Java_Math_calculate
  (JNIEnv *env, jobject obj, jint x, jdouble y) {
    // Примитивы используются напрямую, как C типы
    return (double)x * y + 3.14;
}
```

### Ссылочные типы (непрозрачные указатели)

```
Java Type     JNI Type           Что это
──────────────────────────────────────────────────
Object        jobject            Любой Java объект
Class         jclass             java.lang.Class
String        jstring            java.lang.String
Throwable     jthrowable         Исключение
int[]         jintArray          Массив int
Object[]      jobjectArray       Массив объектов
```

**Важно:** Это непрозрачные указатели! Нельзя:
- Разыменовывать (`*obj`)
- Обращаться к полям напрямую (`obj->field`)
- Только через JNI функции: `(*env)->GetIntField(env, obj, fieldID)`

### Сигнатуры методов

Для поиска методов нужно знать их сигнатуру:

```
Тип           Сигнатура                 Пример
────────────────────────────────────────────────────────
boolean       Z                         void foo(boolean) → (Z)V
byte          B
int           I                         int add(int, int) → (II)I
long          J
Object        Ljava/lang/Object;
String        Ljava/lang/String;        String greet(String) → (Ljava/lang/String;)Ljava/lang/String;
int[]         [I                        void process(int[]) → ([I)V
String[]      [Ljava/lang/String;
void          V
```

**Как читать:** `(параметры)возврат`
- `()V` — метод без параметров, void
- `(II)I` — два int параметра, возвращает int
- `(Ljava/lang/String;)V` — один String параметр, void

---

## Управление памятью (критично!)

### Local References (автоматические)

```c
JNIEXPORT void JNICALL Java_Example_method(JNIEnv *env, jobject obj) {
    // Local reference — автоматически освобождается при выходе из функции
    jstring str = (*env)->NewStringUTF(env, "temporary");

    // Используем...

    // Освобождается автоматически
}
```

**Проблема:** лимит local ссылок (обычно 16-32):

```c
JNIEXPORT void JNICALL Java_Example_leak(JNIEnv *env, jobject obj) {
    for (int i = 0; i < 1000; i++) {
        jstring str = (*env)->NewStringUTF(env, "temp");
        // ПРОБЛЕМА: накапливаются local references!
        // Через 16-32 итерации будет ошибка
    }
}
```

**Решение:**

```c
// Способ 1: Удалять вручную
for (int i = 0; i < 1000; i++) {
    jstring str = (*env)->NewStringUTF(env, "temp");
    // работа...
    (*env)->DeleteLocalRef(env, str);  // Освободить немедленно
}

// Способ 2: Push/Pop frame (удобнее для большого количества)
(*env)->PushLocalFrame(env, 1000);  // Зарезервировать 1000 слотов

for (int i = 0; i < 1000; i++) {
    jstring str = (*env)->NewStringUTF(env, "temp");
    // работа...
}

(*env)->PopLocalFrame(env, NULL);  // Освободить все сразу
```

### Global References (для кэширования)

```c
// Глобальная переменная — сохраняется между вызовами
static jclass cachedClass = NULL;

JNIEXPORT void JNICALL Java_Example_init(JNIEnv *env, jobject obj) {
    // Создаём local reference
    jclass localClass = (*env)->FindClass(env, "java/lang/String");

    // Превращаем в global (переживёт выход из функции)
    cachedClass = (*env)->NewGlobalRef(env, localClass);

    // Local можно удалить
    (*env)->DeleteLocalRef(env, localClass);
}

JNIEXPORT void JNICALL Java_Example_use(JNIEnv *env, jobject obj) {
    // Используем закэшированный класс (намного быстрее, чем FindClass каждый раз)
    jmethodID method = (*env)->GetMethodID(env, cachedClass, "length", "()I");
}

JNIEXPORT void JNICALL Java_Example_cleanup(JNIEnv *env, jobject obj) {
    // ОБЯЗАТЕЛЬНО освободить при завершении
    if (cachedClass != NULL) {
        (*env)->DeleteGlobalRef(env, cachedClass);
        cachedClass = NULL;
    }
}
```

**Когда использовать:**
- Кэширование jclass, jmethodID (значительно ускоряет повторные вызовы)
- Сохранение Java объектов между вызовами
- Передача объектов между потоками

---

## Производительность

### Overhead JNI вызова

```
Операция                         Время
────────────────────────────────────────
Вызов Java метода                ~2-5 ns
Вызов JNI метода                 ~10-20 ns
  → overhead 4-10x

Конвертация String                ~100 ns + длина
GetIntArrayElements              может копировать массив (медленно)
GetPrimitiveArrayCritical        без копирования (быстро, но опасно)
Direct ByteBuffer                zero-copy (самое быстрое)
```

**Вывод:** JNI вызов дорогой. Используйте для:
- Больших объёмов данных
- Сложных вычислений
- Не для простых операций типа `int add(int, int)` — JIT сделает быстрее!

### Оптимизация: кэширование

```c
// ПЛОХО: каждый раз ищем класс и метод (очень медленно!)
JNIEXPORT void JNICALL Java_Example_slow(JNIEnv *env, jobject obj) {
    for (int i = 0; i < 10000; i++) {
        jclass cls = (*env)->FindClass(env, "java/lang/String");     // ~1000 ns
        jmethodID mid = (*env)->GetMethodID(env, cls, "length", "()I");  // ~500 ns
        // overhead 1.5 микросекунды на КАЖДУЮ итерацию!
    }
}

// ХОРОШО: кэшируем при инициализации
static jclass stringClass = NULL;
static jmethodID lengthMethod = NULL;

JNIEXPORT void JNICALL Java_Example_init(JNIEnv *env, jobject obj) {
    jclass local = (*env)->FindClass(env, "java/lang/String");
    stringClass = (*env)->NewGlobalRef(env, local);
    (*env)->DeleteLocalRef(env, local);

    lengthMethod = (*env)->GetMethodID(env, stringClass, "length", "()I");
}

JNIEXPORT void JNICALL Java_Example_fast(JNIEnv *env, jobject obj) {
    for (int i = 0; i < 10000; i++) {
        // Используем закэшированные ID — почти бесплатно
        jstring str = (*env)->NewStringUTF(env, "test");
        jint len = (*env)->CallIntMethod(env, str, lengthMethod);
        (*env)->DeleteLocalRef(env, str);
    }
}
```

**Ускорение:** 100x и более для повторяющихся операций!

---

## Альтернативы JNI

### JNA — Java Native Access

**Преимущество:** Не нужно писать C код!

```java
// JNA — просто объявляем интерфейс
import com.sun.jna.Library;
import com.sun.jna.Native;

public interface CLibrary extends Library {
    CLibrary INSTANCE = Native.load("c", CLibrary.class);

    // Прямое отображение C функций
    int printf(String format, Object... args);
    long time(long[] tloc);
    int getpid();
}

// Использование
public class JNAExample {
    public static void main(String[] args) {
        CLibrary.INSTANCE.printf("Hello from JNA!\n");
        System.out.println("PID: " + CLibrary.INSTANCE.getpid());
    }
}
```

**Когда использовать:**
- ✅ Простые вызовы C функций
- ✅ Быстрое прототипирование
- ❌ Критичная производительность (медленнее JNI ~2-5x)
- ❌ Сложные структуры данных

### Panama Project (Java 19+)

Современная замена JNI:

```java
import java.lang.foreign.*;

public class PanamaExample {
    public static void main(String[] args) throws Throwable {
        // Поиск функции
        SymbolLookup lookup = SymbolLookup.loaderLookup();
        MemorySegment strlen = lookup.find("strlen").get();

        // Создание дескриптора
        FunctionDescriptor desc = FunctionDescriptor.of(
            ValueLayout.JAVA_LONG,    // возврат
            ValueLayout.ADDRESS       // параметр
        );

        // Вызов
        Linker linker = Linker.nativeLinker();
        MethodHandle handle = linker.downcallHandle(strlen, desc);

        try (Arena arena = Arena.ofConfined()) {
            MemorySegment str = arena.allocateUtf8String("Hello");
            long len = (long) handle.invoke(str);  // → 5
        }
    }
}
```

**Преимущества:**
- Типобезопасность на этапе компиляции
- Лучшая производительность, чем JNI
- Современный API без legacy проблем
- Прямая работа с памятью

---

## Чек-лист

### Разработка
- [ ] Используйте `javac -h` для генерации header
- [ ] Проверяйте NULL после каждой JNI функции
- [ ] Освобождайте все ресурсы (ReleaseStringUTFChars, DeleteLocalRef)
- [ ] Обрабатывайте исключения (ExceptionCheck/ExceptionClear)

### Память
- [ ] Удаляйте local references в циклах
- [ ] Используйте global references для кэширования
- [ ] Освобождайте global references при завершении
- [ ] Не забывайте free для malloc'нутой памяти

### Производительность
- [ ] Кэшируйте jclass и jmethodID
- [ ] Используйте Direct ByteBuffer для bulk данных
- [ ] Профилируйте — JNI overhead может быть неожиданным
- [ ] Рассмотрите JNA/Panama для простых случаев

### Потоки
- [ ] Не передавайте JNIEnv между потоками
- [ ] Используйте AttachCurrentThread для нативных потоков
- [ ] Вызывайте DetachCurrentThread при завершении
- [ ] Global references безопасны между потоками

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "JNI — это быстро, потому что нативный код" | JNI crossing имеет **overhead** ~20-100 наносекунд на вызов. Для мелких операций это убивает performance. JIT не может оптимизировать через JNI границу. Нативный код быстр только для heavy computation |
| "JNI — единственный способ вызвать C из Java" | Есть альтернативы: **JNA** (без компиляции), **JNR** (быстрее JNA), **Panama Project** (Java 21+, будущее). JNI — самый низкоуровневый, но не единственный |
| "JNIEnv можно передавать между потоками" | **Нельзя!** JNIEnv привязан к конкретному потоку. Для нативного потока нужен `AttachCurrentThread()`, и `DetachCurrentThread()` при завершении |
| "Local reference живёт пока жив объект" | Local reference живёт до **конца JNI вызова**. В цикле нужно вручную удалять через `DeleteLocalRef()`, иначе таблица переполнится (лимит ~512 по умолчанию) |
| "Строки в Java и C совместимы" | Java String = UTF-16 + immutable + GC managed. C string = null-terminated + mutable + malloc'd. Нужна конвертация через `GetStringUTFChars`/`ReleaseStringUTFChars` |
| "JNI безопасен, JVM защитит от ошибок" | JNI — **unsafe territory**. Нативный код может повредить heap JVM, вызвать SIGSEGV, утечь память. JVM не может защитить от ошибок в native коде |
| "Panama полностью заменяет JNI" | Panama (Foreign Function & Memory API) проще и быстрее для прямых вызовов. Но callback'и из C в Java, custom JNI для библиотек с complex state — всё ещё область JNI |
| "Global reference не нужно освобождать" | **Нужно!** Global reference предотвращает GC объекта. Если не вызвать `DeleteGlobalRef()`, получите memory leak. Global ref живёт пока не удалён явно |
| "JNI работает одинаково на всех платформах" | Нативный код platform-specific: `.so` для Linux, `.dll` для Windows, `.dylib` для macOS. Нужна кросс-компиляция или отдельные бинари |
| "Исключения в native коде бросаются автоматически" | Исключения нужно **проверять вручную** через `ExceptionCheck()`/`ExceptionOccurred()`. Если не проверить, исключение "тихо" отложится до возврата в Java |

---

## CS-фундамент

| CS-концепция | Применение в JNI |
|--------------|-----------------|
| **Foreign Function Interface (FFI)** | JNI — реализация FFI для JVM. Позволяет вызывать функции другого языка (C/C++) с правильной конвертацией типов и calling convention |
| **Memory Management (Manual vs GC)** | Граница двух моделей: Java heap с GC и native heap с malloc/free. Нужно правильно управлять обеими сторонами и их взаимодействием |
| **Calling Convention** | JNI использует C calling convention. Компилятор генерирует корректные параметры стека, return value handling. `JNIEXPORT JNICALL` — макросы для кроссплатформенности |
| **Symbol Table & Dynamic Linking** | Native методы находятся по имени (`Java_pkg_Class_method`) через dlopen/dlsym. `System.loadLibrary()` использует OS dynamic linker |
| **Thread Local Storage (TLS)** | JNIEnv хранится в thread-local storage. Каждый Java thread имеет свой JNIEnv, нативные потоки получают через Attach |
| **Reference Counting** | Local/Global references — форма reference counting. Это позволяет GC знать, какие объекты используются нативным кодом |
| **Type Safety vs Performance** | JNI жертвует type safety ради performance. Нет compile-time проверок между Java и C сигнатурами. Ошибки проявляются в runtime как crashes |
| **Buffer Management** | Direct ByteBuffer даёт прямой доступ к native memory без копирования. GetPrimitiveArrayCritical() пинит массив, предотвращая GC movement |
| **Exception Handling Boundaries** | Исключения не пересекают JNI границу автоматически. Механизм different: Java exceptions vs C error codes/signals |
| **Platform Abstraction** | JNI header'ы абстрагируют OS различия. Но compiled native code всё равно platform-specific — нужна отдельная компиляция для каждой платформы |

---

## Связанные темы

- [[jvm-instrumentation-agents]] — модификация байткода
- [[jvm-memory-model]] — управление памятью JVM
- [[jvm-performance-overview]] — оптимизация производительности

---

**Резюме:** JNI — мощный, но сложный инструмент для интеграции Java с нативным кодом. Используйте только когда действительно необходимо. Для простых случаев рассмотрите JNA или Panama Project. Всегда тщательно управляйте памятью и кэшируйте lookups для производительности.

---

## Связь с другими темами

**[[ffi-foreign-function-interface]]** — JNI является Java-реализацией общей концепции Foreign Function Interface (FFI), которая существует во всех managed-языках: Python ctypes, .NET P/Invoke, Kotlin/Native cinterop. Изучение JNI в контексте FFI помогает понять фундаментальные проблемы межъязыкового взаимодействия: marshalling данных, управление lifetime объектов, calling conventions. Если вы работаете с Kotlin Multiplatform, знание JNI даёт основу для понимания cinterop — KMP использует аналогичные паттерны (но с автоматической генерацией bindings).

**[[kmp-interop-deep-dive]]** — Kotlin/Native cinterop и JNI решают одну и ту же задачу — вызов C/C++ кода из managed-среды — но с разной степенью автоматизации. JNI требует ручного написания C-обёрток и управления памятью (NewGlobalRef/DeleteGlobalRef), тогда как cinterop автоматически генерирует Kotlin bindings из C header'ов. Понимание JNI делает работу с cinterop осознанной: вы понимаете, какие проблемы (memory leaks, thread safety) cinterop решает за вас. Рекомендуется изучить JNI для глубины, затем cinterop для практического применения.

**[[cross-interop]]** — JNI — это один из механизмов межплатформенного interop, наряду с JNA, Panama, Kotlin/Native cinterop и platform channels (Flutter). Сравнительное изучение помогает выбрать правильный инструмент: JNI для максимальной производительности и контроля, JNA для быстрого прототипирования без C-кода, Panama (Java 21+) как современная type-safe замена JNI. Понимание JNI overhead (~20ns на вызов) и его причин помогает оценить, когда нативный код действительно оправдан.

---

## Источники и дальнейшее чтение

- Liang S. (1999). *The Java Native Interface: Programmer's Guide and Specification*. — Единственная полная книга по JNI от создателей API; несмотря на возраст, фундаментальные концепции (JNIEnv, reference types, error handling) не изменились.
- Lindholm T. et al. (2014). *The Java Virtual Machine Specification*, Java SE 8 Edition. — Раздел о native method interface описывает контракт между JVM и нативным кодом, включая правила передачи типов и управления потоками.
- Venners B. (2000). *Inside the Java Virtual Machine*, 2nd Edition. — Главы о native method stacks и взаимодействии GC с нативным кодом объясняют, почему неправильное управление JNI-ссылками приводит к утечкам памяти и crashes.

---

---

## Проверь себя

> [!question]- Почему JNIEnv нельзя передавать между потоками и что произойдет при попытке?
> JNIEnv привязан к конкретному потоку через Thread Local Storage (TLS). Каждый поток имеет свой JNIEnv с собственной таблицей local references и состоянием. При передаче между потоками: local references будут невалидны, операции могут повредить internal state JVM, результат непредсказуем — от SIGSEGV до тихого повреждения данных. Для нативных потоков нужно вызвать AttachCurrentThread() для получения собственного JNIEnv и DetachCurrentThread() при завершении.

> [!question]- Сценарий: В цикле из 10000 итераций создается jstring через NewStringUTF. После ~500 итераций приложение падает. Почему и как исправить?
> Проблема: local references накапливаются — каждый NewStringUTF создает local reference, а лимит таблицы обычно 512 (по умолчанию). После переполнения — crash. Решение 1: вызывать DeleteLocalRef(env, str) после использования в каждой итерации. Решение 2: PushLocalFrame(env, N) перед циклом и PopLocalFrame(env, NULL) после — освобождает все local references разом. Выбор зависит от того, нужны ли промежуточные результаты.

> [!question]- В чем принципиальная разница между JNI и Panama Project (Foreign Function & Memory API) и когда каждый подход предпочтительнее?
> JNI требует написания C-обертки, ручного управления references и компиляции нативной библиотеки для каждой платформы. Panama (Java 21+) работает через MethodHandle и MemorySegment — вызов C-функции описывается целиком на Java, без C-кода. Panama type-safe, быстрее JNI (меньше overhead на crossing), и поддерживает Arena для детерминированного освобождения памяти. JNI предпочтительнее для сложного stateful взаимодействия и callback'ов из C в Java. Panama — для прямых вызовов C-функций.

> [!question]- Почему кэширование jclass и jmethodID дает ускорение в 100x и более?
> FindClass() выполняет поиск по classpath через ClassLoader — ~1000ns на вызов. GetMethodID() ищет метод в таблице виртуальных методов — ~500ns. Без кэширования: 1.5 микросекунды overhead на каждую итерацию. С кэшированием: jclass хранится как global reference, jmethodID валиден на время жизни класса — повторное использование практически бесплатно. Для 10000 итераций: 15ms vs <0.1ms.

---

## Ключевые карточки

Какой overhead у JNI вызова по сравнению с обычным Java-вызовом?
?
Java метод: ~2-5 ns. JNI метод: ~10-20 ns (overhead 4-10x). Конвертация String: ~100 ns + длина строки. GetIntArrayElements: может копировать весь массив. Direct ByteBuffer: zero-copy (самое быстрое). Вывод: JNI вызов дорогой, использовать только для тяжелых вычислений. Для простых операций вроде int add(int, int) JIT сделает быстрее.

В чем разница между local, global и weak references в JNI?
?
Local reference — автоматически освобождается при выходе из native метода, лимит ~512. Global reference — живет пока не вызван DeleteGlobalRef(), предотвращает GC объекта. Используется для кэширования jclass между вызовами. Weak global reference — не предотвращает GC, может стать NULL если объект собран. Используется для optional кэширования. Забытый global reference = memory leak.

Как правильно работать со строками через JNI?
?
Java String = UTF-16, immutable, GC-managed. C string = null-terminated, mutable, malloc'd. Получение: GetStringUTFChars(env, jstr, NULL) конвертирует в Modified UTF-8. ОБЯЗАТЕЛЬНО: ReleaseStringUTFChars(env, jstr, cstr) после использования — иначе memory leak. Проверять NULL после GetStringUTFChars — может вернуть NULL при OutOfMemoryError. Для создания: NewStringUTF(env, cstr).

Что такое JNI сигнатура метода и как она формируется?
?
Формат: (параметры)возвращаемый_тип. Примитивы: I=int, J=long, Z=boolean, D=double, V=void. Объекты: Ljava/lang/String; (L + полное имя + ;). Массивы: [I = int[], [Ljava/lang/String; = String[]. Примеры: ()V = void method(), (II)I = int add(int, int), (Ljava/lang/String;)V = void print(String). Нужна для GetMethodID/GetStaticMethodID.

Какие три современные альтернативы JNI существуют?
?
JNA (Java Native Access) — вызов C-функций через Java-интерфейс без написания C-кода. Просто, но 2-5x медленнее JNI. JNR (Java Native Runtime) — быстрее JNA, но менее распространен. Panama Project (Java 21+, Foreign Function & Memory API) — современная type-safe замена JNI: MethodHandle для вызовов, MemorySegment для памяти, Arena для lifecycle. Panama быстрее JNI и не требует нативного кода.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[jvm-memory-model]] | Понять управление памятью JVM — критично для JNI reference management |
| Углубиться | [[jvm-instrumentation-agents]] | Увидеть другой подход к взаимодействию с нативным уровнем через JVMTI |
| Связанная тема | [[jvm-bytecode-manipulation]] | Понять альтернативу: bytecode manipulation вместо нативного кода |
| Смежная область | [[ffi-foreign-function-interface]] | Сравнить JNI с FFI в других языках: Python ctypes, .NET P/Invoke, Kotlin/Native cinterop |
| Обзор | [[jvm-overview]] | Вернуться к карте раздела |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

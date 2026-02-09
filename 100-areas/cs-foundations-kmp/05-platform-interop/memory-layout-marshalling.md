---
title: "Memory Layout и Marshalling: как данные хранятся и передаются"
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
  - "[[abi-calling-conventions]]"
  - "[[ffi-foreign-function-interface]]"
---

# Memory Layout и Marshalling: как данные хранятся и передаются

> **TL;DR:** Memory layout определяет расположение данных в памяти. Alignment — требование размещения на адресах, кратных размеру типа (int на адресах кратных 4). Padding — "пустые" байты для выравнивания. C struct сохраняет порядок полей, JVM может переупорядочивать. Marshalling — преобразование данных между представлениями (Kotlin String → C char*). Endianness: little-endian (x86, младший байт первым), big-endian (network, старший первым).

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Memory Model** | Stack vs heap, указатели | [[memory-model-fundamentals]] |
| **FFI** | Зачем передавать данные между языками | [[ffi-foreign-function-interface]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Alignment** | Требование к адресу данных | Парковка: машины только в отведённых местах |
| **Padding** | Пустые байты для выравнивания | Пустые места на парковке между машинами |
| **Endianness** | Порядок байтов в числе | Порядок цифр в номере: 123 или 321 |
| **Marshalling** | Преобразование данных между форматами | Перевод документа на другой язык |
| **Blittable** | Тип с одинаковым layout везде | Универсальный штекер |

---

## ПОЧЕМУ alignment важен

### Как CPU читает память

CPU не читает память побайтно — он читает "словами" (word), обычно 4 или 8 байт за раз:

```
┌─────────────────────────────────────────────────────────────┐
│                    CPU MEMORY ACCESS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Память (каждая ячейка = 1 байт):                         │
│   ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐       │
│   │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ A │ B │       │
│   └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘       │
│                                                             │
│   CPU читает 4-байтовыми словами:                          │
│   Word 0: байты 0-3                                        │
│   Word 1: байты 4-7                                        │
│   Word 2: байты 8-11                                       │
│                                                             │
│   ALIGNED int (по адресу 4):                               │
│   ┌───┬───┬───┬───┬───┬───┬───┬───┐                        │
│   │   │   │   │   │ I │ N │ T │   │  ← Один memory access  │
│   └───┴───┴───┴───┴───┴───┴───┴───┘                        │
│                   └───────────────┘                         │
│                      Word 1                                 │
│                                                             │
│   UNALIGNED int (по адресу 2):                             │
│   ┌───┬───┬───┬───┬───┬───┬───┬───┐                        │
│   │   │   │ I │ N │ T │   │   │   │  ← Два memory access!  │
│   └───┴───┴───┴───┴───┴───┴───┴───┘                        │
│           └───────┘───────┘                                 │
│            Word 0   Word 1                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Цена unaligned access

| Платформа | Unaligned access |
|-----------|------------------|
| x86/x64 | Работает, но медленнее (2x cycles) |
| ARM (старые) | Hardware exception |
| ARM (новые) | Работает, но медленнее |
| SPARC, MIPS | Hardware exception |

**Вывод:** Компилятор добавляет padding для alignment, чтобы код был быстрым и портабельным.

---

## ЧТО такое padding

### Alignment правила

Каждый тип имеет своё требование к alignment:

| Тип | Размер | Alignment |
|-----|--------|-----------|
| `char` | 1 byte | 1 |
| `short` | 2 bytes | 2 |
| `int` | 4 bytes | 4 |
| `long` (64-bit) | 8 bytes | 8 |
| `double` | 8 bytes | 8 |
| `pointer` (64-bit) | 8 bytes | 8 |

**Правило:** Данные должны лежать по адресу, кратному их alignment.

### Padding в C struct

```c
struct Example {
    char a;     // offset 0, size 1
    int b;      // offset 4, size 4 (не 1!)
    char c;     // offset 8, size 1
};
// Размер: 12 байт (не 6!)
```

```
┌─────────────────────────────────────────────────────────────┐
│              STRUCT LAYOUT С PADDING                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   struct Example { char a; int b; char c; };               │
│                                                             │
│   Offset:  0   1   2   3   4   5   6   7   8   9  10  11   │
│          ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐ │
│          │ a │PAD│PAD│PAD│ b │ b │ b │ b │ c │PAD│PAD│PAD│ │
│          └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘ │
│                                                             │
│   Почему padding после 'a':                                │
│   - int b требует alignment 4                              │
│   - После 'a' следующий свободный адрес = 1               │
│   - 1 не кратно 4 → добавляем 3 байта padding             │
│   - b начинается с адреса 4                               │
│                                                             │
│   Почему padding после 'c' (tail padding):                 │
│   - Struct alignment = max(alignment полей) = 4           │
│   - Размер struct должен быть кратен 4                    │
│   - 9 не кратно 4 → добавляем 3 байта                     │
│   - Итоговый размер: 12                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Оптимизация: порядок полей

```c
// ❌ Неоптимально: много padding (12 байт)
struct Bad {
    char a;    // 0
    // 3 bytes padding
    int b;     // 4-7
    char c;    // 8
    // 3 bytes padding
};

// ✅ Оптимально: минимум padding (8 байт)
struct Good {
    int b;     // 0-3
    char a;    // 4
    char c;    // 5
    // 2 bytes padding
};
```

**Правило:** Располагай поля от большего к меньшему размеру.

### Packed structs

```c
// Отключение padding (GCC/Clang)
struct __attribute__((packed)) Packed {
    char a;
    int b;
    char c;
};
// Размер: 6 байт (но unaligned access!)
```

**Когда использовать packed:**
- Сетевые протоколы с фиксированным форматом
- Чтение бинарных файлов
- Экономия памяти критична

**Риски:**
- Unaligned access → slower или exception
- Не портабельно

---

## Endianness: порядок байтов

### Два мира

```
┌─────────────────────────────────────────────────────────────┐
│                    ENDIANNESS                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Число: 0x12345678                                         │
│                                                             │
│   LITTLE-ENDIAN (x86, ARM default):                        │
│   Младший байт первым                                       │
│   ┌──────┬──────┬──────┬──────┐                            │
│   │  78  │  56  │  34  │  12  │  ← Читаем справа налево    │
│   └──────┴──────┴──────┴──────┘                            │
│   Addr:  0      1      2      3                            │
│                                                             │
│   BIG-ENDIAN (Network byte order, старые SPARC):           │
│   Старший байт первым                                       │
│   ┌──────┬──────┬──────┬──────┐                            │
│   │  12  │  34  │  56  │  78  │  ← Читаем как пишем       │
│   └──────┴──────┴──────┴──────┘                            │
│   Addr:  0      1      2      3                            │
│                                                             │
│   Аналогия:                                                 │
│   - Little-endian: дата как 31.12.2025 (день первым)       │
│   - Big-endian: дата как 2025.12.31 (год первым)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Когда endianness важен

| Сценарий | Важен? | Почему |
|----------|--------|--------|
| Локальные переменные | Нет | CPU сам знает свой endianness |
| Сетевые протоколы | Да | Network byte order = big-endian |
| Бинарные файлы | Да | Файл может быть создан на другой архитектуре |
| FFI между языками | Обычно нет | Если на одной машине, endianness одинаковый |

### Конвертация

```c
#include <arpa/inet.h>

uint32_t host_value = 0x12345678;

// Host to Network (big-endian)
uint32_t network_value = htonl(host_value);

// Network to Host
uint32_t back_to_host = ntohl(network_value);
```

---

## JVM Memory Layout

### Отличия от C

JVM управляет layout объектов сама:

```
┌─────────────────────────────────────────────────────────────┐
│                 JVM OBJECT LAYOUT                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Kotlin: data class Point(val x: Int, val y: Int)         │
│                                                             │
│   ┌─────────────────────────────────────────┐              │
│   │         OBJECT HEADER (12 bytes)        │              │
│   │ ┌─────────────────────────────────────┐ │              │
│   │ │ Mark Word (8 bytes)                 │ │              │
│   │ │ - Hash code, GC info, lock state    │ │              │
│   │ ├─────────────────────────────────────┤ │              │
│   │ │ Class Pointer (4 bytes, compressed) │ │              │
│   │ │ - Pointer to Point.class            │ │              │
│   │ └─────────────────────────────────────┘ │              │
│   ├─────────────────────────────────────────┤              │
│   │         INSTANCE DATA (8 bytes)         │              │
│   │ ┌─────────────────────────────────────┐ │              │
│   │ │ x: Int (4 bytes)                    │ │              │
│   │ ├─────────────────────────────────────┤ │              │
│   │ │ y: Int (4 bytes)                    │ │              │
│   │ └─────────────────────────────────────┘ │              │
│   ├─────────────────────────────────────────┤              │
│   │         PADDING (4 bytes)               │              │
│   │ (до кратности 8)                        │              │
│   └─────────────────────────────────────────┘              │
│                                                             │
│   Total: 24 bytes (а не 8 как в C struct!)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### JVM может переупорядочивать поля

```kotlin
class Example {
    val a: Byte = 0
    val b: Int = 0
    val c: Byte = 0
}

// В C порядок сохранился бы: a, padding, b, c, padding = 12 bytes

// JVM может переупорядочить: b, a, c, padding = меньше padding
```

### Value Classes (Kotlin) и Project Valhalla

```kotlin
// Обычный класс — объект на heap с header
class Point(val x: Int, val y: Int)  // ~24 bytes

// Value class — инлайнится, без header
@JvmInline
value class UserId(val id: Long)  // 8 bytes, без overhead
```

**Project Valhalla (будущее Java):**
- Primitive classes без object header
- Flat arrays: `Array<Point>` хранит данные inline, не ссылки

---

## Marshalling: преобразование данных

### Что такое marshalling

```
┌─────────────────────────────────────────────────────────────┐
│                    MARSHALLING                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   KOTLIN                                  C                 │
│   ──────                                  ─                 │
│   val name = "Alice"                      char* name        │
│                                                             │
│   Kotlin String:                          C char*:          │
│   ┌───────────────────┐                  ┌───────────────┐  │
│   │ Object Header     │                  │ 'A' │         │  │
│   │ char[] value      │    MARSHAL       │ 'l' │         │  │
│   │ offset            │ ───────────────▶ │ 'i' │         │  │
│   │ count             │                  │ 'c' │         │  │
│   │ UTF-16 encoded    │                  │ 'e' │         │  │
│   └───────────────────┘                  │ '\0'│ NULL    │  │
│                                          └───────────────┘  │
│                                          UTF-8, null-term   │
│                                                             │
│   Marshalling включает:                                     │
│   1. Конвертация кодировки (UTF-16 → UTF-8)                │
│   2. Добавление null terminator                            │
│   3. Копирование в native память                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Blittable vs Non-blittable типы

**Blittable** — типы с одинаковым layout в managed и native памяти:

| Тип | Blittable? | Почему |
|-----|------------|--------|
| `Int`, `Long`, `Float`, `Double` | Да | Одинаковое представление |
| `Boolean` | Зависит | C: может быть 1/4 bytes |
| `String` | Нет | Разное представление |
| `Array<Int>` | Нет | Header различается |
| Struct из blittable | Да | Если layout совпадает |

### Marshalling в разных FFI

**JNI:**
```c
// Получить C строку из Java String
const char* cstr = (*env)->GetStringUTFChars(env, jstr, NULL);
// Использовать...
(*env)->ReleaseStringUTFChars(env, jstr, cstr);
```

**Kotlin/Native cinterop:**
```kotlin
// Kotlin String → C string
val kotlinString = "Hello"
memScoped {
    val cString: CPointer<ByteVar> = kotlinString.cstr.ptr
    nativeFunction(cString)
}

// C string → Kotlin String
val cPointer: CPointer<ByteVar> = getNativeString()
val kotlinString = cPointer.toKString()
```

**P/Invoke (.NET):**
```csharp
// Автоматический marshalling
[DllImport("mylib")]
static extern void ProcessString(string s);

// Явный control
[DllImport("mylib")]
static extern void ProcessBytes(
    [MarshalAs(UnmanagedType.LPArray)] byte[] data,
    int length
);
```

---

## Практика: debugging memory layout

### Проверка размера и alignment в C

```c
#include <stdio.h>
#include <stddef.h>

struct Example {
    char a;
    int b;
    char c;
};

int main() {
    printf("Size: %zu\n", sizeof(struct Example));  // 12
    printf("Align: %zu\n", _Alignof(struct Example));  // 4

    printf("Offset a: %zu\n", offsetof(struct Example, a));  // 0
    printf("Offset b: %zu\n", offsetof(struct Example, b));  // 4
    printf("Offset c: %zu\n", offsetof(struct Example, c));  // 8
}
```

### JVM: JOL (Java Object Layout)

```kotlin
// Gradle: implementation("org.openjdk.jol:jol-core:0.17")

import org.openjdk.jol.info.ClassLayout

data class Point(val x: Int, val y: Int)

fun main() {
    println(ClassLayout.parseClass(Point::class.java).toPrintable())
}

// Output показывает точный layout объекта
```

---

## Подводные камни

### Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Игнорирование padding | sizeof() != sum(fields) | Использовать sizeof() |
| Packed struct по сети | Unaligned access на receiver | Использовать packed везде |
| Endianness в binary files | Мусорные данные на другой архитектуре | Явная конвертация |
| Marshalling без освобождения | Memory leak | Парные операции |

### Мифы и заблуждения

**Миф:** "Размер struct = сумма размеров полей"
**Реальность:** Padding может значительно увеличить размер. `sizeof(struct)` единственный способ узнать реальный размер.

**Миф:** "Endianness важен только для сетевого программирования"
**Реальность:** Важен для любых бинарных файлов, memory-mapped данных и кросс-платформенного кода.

**Миф:** "JVM объекты занимают столько же места, сколько данные"
**Реальность:** Object header добавляет 12-16 байт к каждому объекту плюс alignment до 8 байт.

---

## Куда дальше

**Если здесь впервые:**
→ Поэкспериментируй с sizeof() и offsetof() в C

**Если понял и хочешь глубже:**
→ [[bridges-bindings-overview]] — как автоматизировать interop

**Практическое применение:**
→ Kotlin/Native cinterop с C библиотеками

---

## Источники

- [The Lost Art of Structure Packing](http://www.catb.org/esr/structure-packing/) — comprehensive C guide
- [Wikipedia: Data Structure Alignment](https://en.wikipedia.org/wiki/Data_structure_alignment) — formal definitions
- [Baeldung: Java Memory Layout](https://www.baeldung.com/java-memory-layout) — JVM specifics
- [JVM Anatomy Quark #24](https://shipilev.net/jvm/anatomy-quarks/24-object-alignment/) — deep JVM internals
- [GeeksforGeeks: Struct Padding](https://www.geeksforgeeks.org/c/structure-member-alignment-padding-and-data-packing/) — practical examples

---

*Проверено: 2026-01-09*

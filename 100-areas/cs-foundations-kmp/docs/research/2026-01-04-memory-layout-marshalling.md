# Research Report: Memory Layout and Marshalling

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Memory layout определяет, как данные располагаются в памяти. Alignment — требование размещения данных на адресах, кратных определённому числу (обычно sizeof типа). Padding — пустые байты для выравнивания. C struct layout детерминирован: порядок полей сохраняется, padding добавляется для alignment. JVM может переупорядочивать поля для оптимизации. Marshalling — преобразование данных между форматами (native ↔ managed, host ↔ network). Endianness: little-endian (x86), big-endian (network byte order).

## Key Findings

### 1. Data Alignment

**Зачем нужен alignment:**
- CPU эффективнее читает aligned данные
- Unaligned access: дополнительные циклы или exception
- Alignment типа = sizeof(тип) обычно

**Alignment примеры:**
- char: 1 byte
- short: 2 bytes
- int: 4 bytes
- long/pointer (64-bit): 8 bytes
- double: 8 bytes

### 2. Struct Padding в C

**Правила:**
1. Каждое поле выравнивается по своему alignment
2. Struct alignment = max alignment его полей
3. Размер struct кратен его alignment (tail padding)

**Пример:**
```c
struct Example {
    char a;    // offset 0, size 1
    // 3 bytes padding
    int b;     // offset 4, size 4
    char c;    // offset 8, size 1
    // 3 bytes padding (tail)
};
// Total: 12 bytes (не 6!)
```

**Оптимизация:**
- Порядок от большего к меньшему минимизирует padding
- `__attribute__((packed))` убирает padding (но может снизить performance)

### 3. JVM Memory Layout

**Отличия от C:**
- JVM может переупорядочивать поля
- Object header: 12-16 bytes
- Минимальный alignment: 8 bytes
- Padding для выравнивания до 8

**Object structure:**
1. Mark Word (8 bytes)
2. Class Pointer (4-8 bytes, compressed)
3. Instance Data
4. Padding

### 4. Endianness

**Little-endian:**
- Младший байт первым
- x86, x86-64, ARM (default)
- Число 0x12345678 в памяти: 78 56 34 12

**Big-endian:**
- Старший байт первым
- Network byte order
- Число 0x12345678 в памяти: 12 34 56 78

**Конвертация:**
- htonl/htons: host to network
- ntohl/ntohs: network to host

### 5. Marshalling

**Определение:**
Преобразование внутреннего представления данных во внешний формат.

**Marshalling vs Serialization:**
- Serialization: для хранения/передачи
- Marshalling: для межпроцессного/межъязыкового взаимодействия

**Проблемы:**
- Размеры типов (int: 16/32/64 bit)
- Endianness
- Padding/alignment
- Pointer representation

### 6. Blittable Types

**Определение:**
Типы с одинаковым layout в managed и native памяти.

**Blittable:**
- Примитивы (int, float, double)
- Структуры только из blittable типов

**Non-blittable:**
- Strings (разное представление)
- Arrays (header differences)
- Objects (references)

### 7. Kotlin/Native и Memory Layout

**cinterop:**
- Генерирует Kotlin типы с правильным layout
- CValue<T> для struct by value
- CPointer<T> для указателей

**Inline classes:**
- Убирают overhead объекта
- Примитив напрямую без boxing

## Community Sentiment

### Positive
- Понимание layout помогает оптимизировать память
- Предсказуемость C struct layout
- Kotlin inline classes решают boxing

### Negative
- Padding неинтуитивен для новичков
- Cross-platform differences сложны
- JVM layout непредсказуем

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [The Lost Art of Structure Packing](http://www.catb.org/esr/structure-packing/) | Article | ★★★★★ | Comprehensive C structs |
| [GeeksforGeeks: Struct Alignment](https://www.geeksforgeeks.org/c/structure-member-alignment-padding-and-data-packing/) | Tutorial | ★★★★☆ | Clear examples |
| [Wikipedia: Data Structure Alignment](https://en.wikipedia.org/wiki/Data_structure_alignment) | Reference | ★★★★★ | Formal definitions |
| [Baeldung: Java Memory Layout](https://www.baeldung.com/java-memory-layout) | Tutorial | ★★★★★ | JVM specifics |
| [JVM Anatomy Quark #24](https://shipilev.net/jvm/anatomy-quarks/24-object-alignment/) | Deep Dive | ★★★★★ | JVM internals |
| [Wikipedia: Marshalling](https://en.wikipedia.org/wiki/Marshalling_(computer_science)) | Reference | ★★★★☆ | Definitions |

## Research Methodology
- **Queries used:** 2 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **Focus areas:** C struct layout, JVM layout, endianness, marshalling

---

*Проверено: 2026-01-09*

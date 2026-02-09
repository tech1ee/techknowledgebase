---
title: "Bundle и Parcelable: сериализация данных в Android"
created: 2026-01-27
modified: 2026-01-27
type: deep-dive
area: android
confidence: high
tags:
  - android
  - bundle
  - parcelable
  - parcel
  - serialization
  - binder
  - ipc
  - savedinstancestate
related:
  - "[[android-activity-lifecycle]]"
  - "[[android-state-management]]"
  - "[[android-viewmodel-internals]]"
  - "[[android-navigation]]"
  - "[[android-app-components]]"
  - "[[android-handler-looper]]"
  - "[[android-process-memory]]"
cs-foundations: [serialization, ipc, binary-protocol, memory-layout, decorator-pattern, object-pool]
---

# Bundle и Parcelable: сериализация данных в Android

> **TL;DR:** Bundle — это типизированная обёртка над `ArrayMap<String, Object>`, которая сериализуется через Parcel в плоский бинарный буфер для передачи через Binder IPC. Binder буфер ограничен **1 МБ на процесс** — превышение вызывает `TransactionTooLargeException`. Parcelable в 10-17x быстрее Serializable благодаря отсутствию reflection и прямой записи в нативный буфер. `@Parcelize` генерирует весь boilerplate на этапе компиляции через Kotlin compiler plugin. savedInstanceState Bundle проходит путь: Activity → ActivityThread → Binder → system_server → ActivityRecord — и возвращается обратно при пересоздании Activity.

---

## Зачем это нужно

### Проблема: невидимая сериализация повсюду

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| `TransactionTooLargeException` crash | Bundle > 1 МБ при сохранении состояния | Приложение падает, данные теряются |
| Данные теряются после ротации экрана | Не сохранено в `onSaveInstanceState` | Пользователь видит пустой экран |
| `ClassCastException` при получении Map | Bundle теряет тип Map при сериализации | Crash при попытке привести к TreeMap |
| ANR при передаче данных через Intent | Сериализация большого объекта на Main Thread | 5-секундный таймаут, принудительное закрытие |
| Memory leak от Bitmap в Bundle | Bitmap сериализуется полностью через Parcel | OOM при множественных конфигурациях |
| `BadParcelableException` между процессами | Кастомный Parcelable неизвестен в другом процессе | Crash при IPC с системными сервисами |

### Актуальность в 2024-2026

**Bundle — невидимый фундамент Android:**

```
КАЖДОЕ ДЕЙСТВИЕ ПОЛЬЗОВАТЕЛЯ → Bundle:

Открыл Activity    → Intent.extras = Bundle
Повернул экран      → onSaveInstanceState(Bundle)
Нажал "Назад"       → Fragment.arguments = Bundle
Получил push        → RemoteMessage → Bundle
Изменил настройки   → SharedPreferences ≈ Bundle-like
Переключил app      → savedInstanceState через Binder
```

**Статистика (2024-2025):**
- `TransactionTooLargeException` — в **топ-10** самых частых крашей Android-приложений
- **1 МБ** — лимит Binder буфера, **разделяемый** между ВСЕМИ транзакциями процесса
- Android рекомендует хранить в savedInstanceState **менее 50 КБ** данных
- `@Parcelize` используется в **89%** Kotlin Android проектов (JetBrains Survey 2024)
- Parcelable в **10-17x быстрее** Serializable (Philippe Breault benchmark)

**Что вы узнаете:**
1. Как Bundle хранит данные внутри (ArrayMap, типизация, потеря типов)
2. Бинарный формат Parcel и нативный слой (Parcel.cpp, JNI)
3. Binder IPC: 1 МБ лимит, TransactionTooLargeException и как его избежать
4. Parcelable vs Serializable: почему разница в 10x
5. Что генерирует `@Parcelize` и как работает Kotlin compiler plugin
6. Полный путь savedInstanceState: от Activity до system_server и обратно
7. Что хранить в Bundle и что категорически нельзя

---

## Prerequisites

Для полного понимания материала необходимо:

| Тема | Зачем | Где изучить |
|------|-------|-------------|
| **[[android-activity-lifecycle]]** | Понимание когда вызываются onSaveInstanceState/onCreate | Раздел Android |
| **[[android-app-components]]** | Activity, Service, ContentProvider — все используют Bundle | Раздел Android |
| **[[android-process-memory]]** | Binder IPC, процессы, system_server | Раздел Android |
| **Основы Java/Kotlin** | Классы, интерфейсы, аннотации, reflection | Общие знания |
| **Бинарная сериализация** | Понятие маршаллинга/демаршаллинга данных | CS foundations |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Bundle** | Типизированный контейнер key-value пар на основе ArrayMap | Конверт с подписанными ячейками — каждая ячейка хранит данные определённого типа |
| **Parcel** | Плоский бинарный буфер для сериализации данных при IPC | Лента конвейера — данные записываются последовательно, читаются в том же порядке |
| **Parcelable** | Android-интерфейс для сериализации объектов через Parcel | Инструкция по упаковке — объект сам знает как себя разобрать и собрать |
| **Serializable** | Java-интерфейс для сериализации через reflection | Рентген-аппарат — сканирует объект целиком, медленно но автоматически |
| **Binder** | Механизм IPC в Android (межпроцессное взаимодействие) | Почтовая служба между процессами — у неё ограниченный размер посылки |
| **ArrayMap** | Оптимизированная для памяти реализация Map в Android | Два списка вместо хеш-таблицы — экономит память за счёт скорости |
| **CREATOR** | Статическое поле Parcelable для создания объектов из Parcel | Фабрика по чертежу — знает как воссоздать объект из бинарных данных |
| **TransactionTooLargeException** | Исключение при превышении 1 МБ Binder буфера | Посылка не влезает в почтовый ящик |
| **@Parcelize** | Kotlin-аннотация для автоматической генерации Parcelable | Автопилот — компилятор сам пишет весь boilerplate код |
| **savedInstanceState** | Bundle с сохранённым состоянием Activity/Fragment | Чёрный ящик самолёта — сохраняет данные перед "крушением" (уничтожением) |

---

## 1. Bundle: контейнер данных Android

### 1.1. Что такое Bundle

**Bundle** — это специализированный контейнер для хранения пар ключ-значение, оптимизированный для Android. В отличие от обычной `HashMap`, Bundle:

- Использует `ArrayMap` вместо `HashMap` (меньше памяти)
- Поддерживает типизированные методы (`putString`, `putInt`, `putParcelable`)
- Умеет сериализоваться через `Parcel` для IPC
- Является основным способом передачи данных между компонентами Android

```kotlin
// Создание и использование Bundle
val bundle = Bundle().apply {
    putString("user_name", "Алексей")        // Строка
    putInt("user_age", 28)                    // Число
    putBoolean("is_premium", true)            // Булево
    putStringArrayList("tags", arrayListOf(   // Список строк
        "android", "kotlin"
    ))
}

// Извлечение данных
val name = bundle.getString("user_name")          // "Алексей"
val age = bundle.getInt("user_age", 0)            // 28 (0 — default)
val premium = bundle.getBoolean("is_premium")      // true
```

### 1.2. Почему Bundle, а не HashMap

**Историческая проблема:**

Android с самого начала проектировался для работы с ограниченными ресурсами мобильных устройств. `HashMap` из стандартной Java библиотеки имеет значительные накладные расходы:

```
HASHMAP vs ARRAYMAP — ВНУТРЕННЯЯ СТРУКТУРА:

HashMap<String, Object>:
┌─────────────────────────────────────────────────┐
│ Entry[] table (массив бакетов)                   │
│                                                  │
│ Каждый Entry = ОТДЕЛЬНЫЙ ОБЪЕКТ:                  │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│ │ hash     │  │ hash     │  │ hash     │         │
│ │ key ─────┼─→│ key ─────┼─→│ key      │         │
│ │ value ───┼─→│ value ───┼─→│ value    │         │
│ │ next ────┼─→│ next ────┼─→│ next=null│         │
│ └──────────┘  └──────────┘  └──────────┘         │
│                                                  │
│ Каждая пара = 1 Entry object (32+ байт)          │
│ 100 пар ≈ 100 × Entry + 100+ байт overhead       │
└─────────────────────────────────────────────────┘

ArrayMap<String, Object> (используется в Bundle):
┌─────────────────────────────────────────────────┐
│ int[] mHashes:     [hash0, hash1, hash2, ...]    │
│                     ↓       ↓       ↓             │
│ Object[] mArray:   [key0, val0, key1, val1, ...]  │
│                                                  │
│ 0 дополнительных объектов!                        │
│ 100 пар = 1 int[] + 1 Object[]                    │
│ Поиск: binary search по mHashes → O(log n)       │
└─────────────────────────────────────────────────┘
```

**Сравнение производительности:**

| Метрика | HashMap | ArrayMap (Bundle) |
|---------|---------|-------------------|
| Поиск по ключу | O(1) среднее | O(log n) binary search |
| Вставка | O(1) амортизированная | O(n) — сдвиг массива |
| Удаление | O(1) | O(n) — сдвиг массива |
| Память на 10 пар | ~640 байт | ~200 байт |
| Память на 100 пар | ~6400 байт | ~2000 байт |
| GC давление | Высокое (Entry objects) | Низкое (только 2 массива) |
| Автоматическое сжатие | Нет | Да (при удалении) |

**Когда ArrayMap выигрывает:** до нескольких сотен элементов (типичный размер Bundle).

### 1.3. Как работает Bundle внутри (AOSP)

```
ИЕРАРХИЯ КЛАССОВ BUNDLE:

BaseBundle                          ← Общая логика хранения
├── mMap: ArrayMap<String, Object>  ← Хранение данных в памяти
├── mParcelledData: Parcel          ← Ленивая десериализация
├── mParcelledByNative: boolean     ← Нативная парселизация
│
├── putString(key, value)           ← Типизированные методы записи
├── getString(key)                  ← Типизированные методы чтения
├── writeToParcel(parcel)           ← Сериализация в Parcel
├── readFromParcel(parcel)          ← Десериализация из Parcel
│
└── Bundle extends BaseBundle       ← Добавляет Parcelable поддержку
    ├── putParcelable(key, value)
    ├── getParcelable(key, clazz)   ← Type-safe с Android 13+
    ├── clone()
    └── deepCopy()
```

**Ключевой механизм — ленивая десериализация (lazy unparcelling):**

```kotlin
// Когда Bundle приходит через IPC, данные НЕ десериализуются сразу
// Они остаются в виде Parcel до первого обращения

// AOSP: BaseBundle.java
class BaseBundle {
    // Вариант 1: данные уже распакованы в Map
    var mMap: ArrayMap<String, Any?>? = null

    // Вариант 2: данные ещё в бинарном виде (Parcel)
    var mParcelledData: Parcel? = null

    fun getString(key: String): String? {
        unparcel()  // ← Ленивая распаковка при первом доступе!
        val o = mMap?.get(key)
        return when (o) {
            is String -> o
            else -> null  // Type safety — не бросает ClassCastException
        }
    }

    // Вызывается при первом обращении к данным
    fun unparcel() {
        val source = mParcelledData ?: return  // Уже распакован

        val map = ArrayMap<String, Any?>(source.readInt())
        source.readArrayMapInternal(map, map.size, classLoader)

        mMap = map
        mParcelledData = null  // Освобождаем Parcel
    }
}
```

**Почему lazy unparcelling важен:**

```
СЦЕНАРИЙ: Activity получает Intent с 20 extras

БЕЗ lazy unparcelling:
Получен Intent → десериализация 20 полей → используется 1 поле
Потрачено CPU: 100%
Использовано полей: 5%

С lazy unparcelling (реальное поведение):
Получен Intent → Parcel сохранён как есть → доступ к 1 полю →
распаковка всех 20 полей при первом getString()
Потрачено CPU: 0% до первого доступа
```

### 1.4. Потеря типов при сериализации

**Критическая проблема**, которую мало кто знает: Bundle теряет конкретные типы Map-подобных структур при сериализации через Parcel.

```kotlin
// ❌ ЛОВУШКА: потеря типа Map

// Отправка
val sortedMap: TreeMap<String, String> = TreeMap()
sortedMap["b"] = "second"
sortedMap["a"] = "first"  // TreeMap хранит в порядке: a, b

val intent = Intent().apply {
    putExtra("my_map", sortedMap as Serializable)  // Кладём TreeMap
}

// Получение в другой Activity
val map = intent.getSerializableExtra("my_map") as TreeMap<String, String>
// ❌ ClassCastException! Вернулся HashMap, не TreeMap!
```

**Почему это происходит (AOSP):**

```
ПУТЬ СЕРИАЛИЗАЦИИ MAP В PARCEL:

1. Bundle.putSerializable("key", treeMap)
   → mMap.put("key", treeMap)     // Сохранено как Object

2. Bundle.writeToParcel(parcel)
   → Parcel.writeValue(treeMap)
   → Проверка: instanceof Map?   ← Совпадение! (TreeMap implements Map)
   → Parcel.writeMap(treeMap)     // НЕ writeSerializable!
   → Записан type tag: VAL_MAP
   → writeMapInternal(map)       // Записаны только key-value пары

3. Bundle.readFromParcel(parcel)
   → Parcel.readValue()
   → Читаем type tag: VAL_MAP
   → readHashMap()               // ← ВСЕГДА HashMap!
   → Возвращается HashMap        // Тип потерян навсегда
```

**Механизм потери типа:**

```
Parcel.writeValue() выбирает serializer по порядку проверок:

if (v instanceof String)         → VAL_STRING
if (v instanceof Integer)        → VAL_INTEGER
if (v instanceof Map)            → VAL_MAP      ← TreeMap попадает СЮДА
if (v instanceof Serializable)   → VAL_SERIALIZABLE  ← не доходит до этого!

Проверка Map стоит РАНЬШЕ Serializable.
Поэтому TreeMap сериализуется как обычная Map,
а при десериализации восстанавливается как HashMap.
```

**Решение:**

```kotlin
// ✅ ПРАВИЛЬНО: используйте Bundle-совместимые типы
val bundle = Bundle().apply {
    // Для упорядоченных данных используйте ArrayList
    putStringArrayList("sorted_keys", ArrayList(sortedMap.keys))
    putStringArrayList("sorted_values", ArrayList(sortedMap.values))
}

// ✅ ИЛИ: Оборачивайте в Parcelable с явной сериализацией
@Parcelize
data class SortedData(
    val entries: List<Pair<String, String>>  // Порядок сохранён
) : Parcelable
```

### 1.5. Подводные камни Bundle

```
ТИПИЧНЫЕ ОШИБКИ С BUNDLE:

1. NULL vs DEFAULT
   ┌─────────────────────────────────────────┐
   │ getInt("missing_key")     → 0 (default) │
   │ getString("missing_key")  → null         │
   │ getInt("missing_key", -1) → -1 (custom)  │
   │                                          │
   │ Нет способа отличить "ключ со значением  │
   │ 0" от "ключа нет в Bundle"!              │
   │ Используйте containsKey() для проверки   │
   └─────────────────────────────────────────┘

2. THREAD SAFETY
   ┌─────────────────────────────────────────┐
   │ Bundle НЕ thread-safe!                   │
   │ Одновременный put/get из разных потоков  │
   │ может привести к ConcurrentModification │
   │ или corrupted data                       │
   └─────────────────────────────────────────┘

3. SIZE LIMITS
   ┌─────────────────────────────────────────┐
   │ savedInstanceState: < 50 КБ             │
   │ Intent extras: несколько КБ             │
   │ Binder буфер: 1 МБ НА ВЕСЬ ПРОЦЕСС     │
   └─────────────────────────────────────────┘
```

---

## 2. Parcel: бинарный формат сериализации

### 2.1. Что такое Parcel

**Parcel** — это контейнер для сообщений (данных и ссылок на объекты), которые могут быть отправлены через Binder IPC. Parcel представляет собой **плоский линейный буфер в нативной памяти**, в который данные записываются и из которого читаются последовательно.

```
PARCEL = ЛЕНТА КОНВЕЙЕРА:

Запись (writeString, writeInt, writeParcelable):
┌─────┬─────┬──────┬─────┬──────────┬─────┬──────┐
│ len │type │"name"│type │ int:28   │type │ bool │
│ 4B  │ 4B  │ nB   │ 4B  │   4B     │ 4B  │ 4B   │
└─────┴─────┴──────┴─────┴──────────┴─────┴──────┘
  ←─────── Последовательная запись ──────────→

Чтение (readString, readInt, readParcelable):
  ←─────── Читаем в ТОМ ЖЕ ПОРЯДКЕ ─────────→

⚠️ Если порядок чтения не совпадает с порядком записи →
   corrupted data или crash!
```

### 2.2. Почему Parcel, а не стандартная Java-сериализация

**Java `ObjectOutputStream`** (Serializable):
```
1. Получает объект
2. Через REFLECTION сканирует ВСЕ поля
3. Рекурсивно сериализует каждое поле
4. Создаёт множество временных объектов
5. Пишет метаданные о типах, версиях, иерархии классов
6. Результат: большой, медленный, с GC overhead
```

**Android `Parcel`** (Parcelable):
```
1. Объект сам знает как себя записать (writeToParcel)
2. Вызывает parcel.writeString(), parcel.writeInt() напрямую
3. Каждый вызов = 1 JNI call → прямая запись в нативный буфер
4. 0 reflection, 0 временных объектов
5. Минимум метаданных (только type tags)
6. Результат: компактный, быстрый, без GC давления
```

### 2.3. Как работает Parcel внутри: от Java до нативного кода

```
АРХИТЕКТУРА PARCEL — ТРИ СЛОЯ:

┌───────────────────────────────────────────────────┐
│  JAVA СЛОЙ: Parcel.java                            │
│  ├── writeString(val) → nativeWriteString(ptr, val)│
│  ├── writeInt(val)    → nativeWriteInt(ptr, val)   │
│  ├── obtain()         → из пула (Object Pool)       │
│  └── recycle()        → возврат в пул              │
├───────────────────────────────────────────────────┤
│  JNI СЛОЙ: android_os_Parcel.cpp                   │
│  ├── android_os_Parcel_writeString16()             │
│  ├── Конвертация Java String → char16_t*           │
│  └── Вызов нативного Parcel::writeString16()      │
├───────────────────────────────────────────────────┤
│  НАТИВНЫЙ СЛОЙ: libs/binder/Parcel.cpp             │
│  ├── Плоский буфер (mData, mDataSize, mDataPos)   │
│  ├── writeInPlace(len) → growData() если нужно     │
│  ├── Прямая запись в память: memcpy()              │
│  └── Управление буфером: realloc, free            │
└───────────────────────────────────────────────────┘
```

**Бинарный формат Parcel — как данные лежат в памяти:**

```
ПРИМЕР: Bundle с тремя полями

putString("name", "Kotlin")
putInt("year", 2011)
putBoolean("is_cool", true)

БИНАРНЫЙ ФОРМАТ В PARCEL:
Offset  Байты     Содержание
──────────────────────────────────────────
0x00    04 00 00 00   Количество элементов: 3
0x04    ── Элемент 0 ──
0x04    04 00 00 00   Длина ключа: 4 символа
0x08    6E 00 61 00   "na" (UTF-16)
0x0C    6D 00 65 00   "me"
0x10    00 00 00 00   Type tag: VAL_STRING (0)
0x14    06 00 00 00   Длина значения: 6 символов
0x18    4B 00 6F 00   "Ko" (UTF-16)
0x1C    74 00 6C 00   "tl"
0x20    69 00 6E 00   "in"
0x24    ── Элемент 1 ──
0x24    04 00 00 00   Длина ключа: 4
0x28    79 00 65 00   "ye"
0x2C    61 00 72 00   "ar"
0x30    01 00 00 00   Type tag: VAL_INTEGER (1)
0x34    DB 07 00 00   Значение: 2011
0x38    ── Элемент 2 ──
        ...           аналогично для boolean
```

**Type tags в Parcel (AOSP Parcel.java):**

| Tag | Значение | Java/Kotlin тип |
|-----|----------|-----------------|
| `VAL_NULL` | -1 | null |
| `VAL_STRING` | 0 | String |
| `VAL_INTEGER` | 1 | Int |
| `VAL_MAP` | 2 | Map → всегда HashMap при чтении! |
| `VAL_BUNDLE` | 3 | Bundle |
| `VAL_PARCELABLE` | 4 | Parcelable |
| `VAL_SHORT` | 5 | Short |
| `VAL_LONG` | 6 | Long |
| `VAL_FLOAT` | 7 | Float |
| `VAL_DOUBLE` | 8 | Double |
| `VAL_BOOLEAN` | 9 | Boolean |
| `VAL_CHARSEQUENCE` | 10 | CharSequence |
| `VAL_LIST` | 11 | List |
| `VAL_BYTEARRAY` | 13 | ByteArray |
| `VAL_STRINGARRAY` | 14 | Array<String> |
| `VAL_SERIALIZABLE` | 21 | Serializable |

### 2.4. Object Pool — переиспользование Parcel

```kotlin
// AOSP: Parcel.java — пул объектов

// ❌ ПЛОХО: создание нового Parcel каждый раз
val parcel = Parcel()  // Аллокация нативной памяти каждый раз

// ✅ ПРАВИЛЬНО: получение из пула
val parcel = Parcel.obtain()  // Берём из пула переиспользуемых
try {
    parcel.writeString("data")
    // ... использование
} finally {
    parcel.recycle()  // Возвращаем в пул (обязательно!)
}
```

**Как работает пул (AOSP):**

```
OBJECT POOL PATTERN в Parcel:

Parcel.obtain():
┌─────────────────────────────────┐
│ sOwnedPool: Parcel[] (размер 6)│
│ sHolderPool: Parcel[] (размер 6)│
│                                 │
│ Если пул не пуст:               │
│   → Берём последний элемент     │
│   → Сбрасываем его состояние    │
│   → Возвращаем                  │
│                                 │
│ Если пул пуст:                   │
│   → new Parcel(0)               │
│   → Аллокация нативной памяти   │
└─────────────────────────────────┘

Parcel.recycle():
┌─────────────────────────────────┐
│ Сбрасываем данные (mDataSize=0) │
│ Если пул не полон:               │
│   → Кладём Parcel обратно в пул │
│ Если пул полон:                  │
│   → free() нативной памяти      │
└─────────────────────────────────┘
```

### 2.5. Подводные камни Parcel

```
⚠️ КРИТИЧЕСКИЕ ПРАВИЛА PARCEL:

1. НЕ используйте Parcel для долговременного хранения!
   ┌─────────────────────────────────────────────┐
   │ Parcel — НЕ general-purpose сериализация.    │
   │ Бинарный формат может меняться между         │
   │ версиями Android. Данные, записанные на      │
   │ Android 13, могут не прочитаться на Android 15│
   │                                              │
   │ ❌ Никогда не сохраняйте Parcel на диск       │
   │ ❌ Никогда не отправляйте Parcel по сети       │
   │ ✅ Используйте только для IPC в рамках        │
   │    одного устройства                          │
   └─────────────────────────────────────────────┘

2. ПОРЯДОК записи = ПОРЯДОК чтения!
   ┌─────────────────────────────────────────────┐
   │ writeString("name")                          │
   │ writeInt(28)                                 │
   │                                              │
   │ readInt()     ← ❌ CRASH! Ожидался String     │
   │ readString()  ← ❌ Данные уже сдвинуты        │
   └─────────────────────────────────────────────┘

3. ВСЕГДА вызывайте recycle()!
   ┌─────────────────────────────────────────────┐
   │ val parcel = Parcel.obtain()                 │
   │ // Забыли recycle()                          │
   │ // → Нативная утечка памяти (не GC'd!)       │
   │ // → Пул исчерпан → каждый obtain() создаёт  │
   │ //   новый объект                            │
   └─────────────────────────────────────────────┘
```

---

## 3. Binder IPC и лимит 1 МБ

### 3.1. Что такое Binder transaction buffer

**Binder** — это механизм межпроцессного взаимодействия (IPC) в Android. Каждый раз, когда приложение общается с system_server (запуск Activity, сохранение состояния, получение системных сервисов), данные передаются через Binder.

```
BINDER IPC — КАК РАБОТАЕТ:

Приложение (процесс A)              system_server (процесс B)
┌──────────────────┐                ┌──────────────────┐
│                  │                │                  │
│ startActivity()  │──── Binder ───→│ AMS              │
│                  │    (Intent     │ (ActivityManager  │
│                  │     Bundle     │  Service)         │
│                  │     = Parcel)  │                  │
│                  │                │                  │
│ onSaveInstance() │──── Binder ───→│ Сохранить Bundle │
│                  │    (Bundle     │ в ActivityRecord  │
│                  │     = Parcel)  │                  │
└──────────────────┘                └──────────────────┘
        │                                    │
        └────── ОБЩИЙ БУФЕР: 1 МБ ──────────┘
```

### 3.2. Почему 1 МБ и почему это проблема

**Binder transaction buffer = 1 МБ** — фиксированный размер, **общий для ВСЕХ активных транзакций процесса**.

```
БУФЕР 1 МБ — ЭТО НЕ "НА ОДНУ ТРАНЗАКЦИЮ"!

Процесс вашего приложения:
┌──────────────────────────────────────────────────┐
│              Binder Transaction Buffer            │
│                    1024 КБ                        │
│                                                  │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐              │
│ │ TX 1 │ │ TX 2 │ │ TX 3 │ │ TX 4 │  Свободно   │
│ │200KB │ │100KB │ │300KB │ │200KB │  224KB       │
│ └──────┘ └──────┘ └──────┘ └──────┘              │
│                                                  │
│ ← ──── Занято: 800 КБ ─────→  ← Свободно →      │
│                                                  │
│ Новая транзакция 300 КБ → ❌ TransactionToo      │
│                              LargeException!     │
└──────────────────────────────────────────────────┘

Все эти транзакции ОДНОВРЕМЕННО используют один буфер:
- Запуск Activity (Intent с extras)
- Сохранение состояния (onSaveInstanceState)
- ContentProvider запросы
- Service binding
- Системные broadcast'ы
```

### 3.3. TransactionTooLargeException

**С Android 7.0 (API 24)** `TransactionTooLargeException` стал **RuntimeException** вместо молчаливого логирования. Это значит — crash вместо тихой потери данных.

```kotlin
// ❌ ТИПИЧНЫЕ ПРИЧИНЫ TransactionTooLargeException:

// 1. Большие данные в savedInstanceState
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // ❌ Список из 10,000 объектов
    outState.putParcelableArrayList("items", ArrayList(allItems))
    // ❌ Bitmap
    outState.putParcelable("photo", largeBitmap)
}

// 2. Большой Intent при запуске Activity
val intent = Intent(this, DetailActivity::class.java).apply {
    // ❌ Передача всего объекта вместо ID
    putExtra("full_article", articleWithImages)  // Может быть > 1 МБ!
}

// 3. Fragment arguments
val fragment = DetailFragment().apply {
    arguments = Bundle().apply {
        // ❌ Большой список в arguments
        putParcelableArrayList("all_comments", ArrayList(comments))
    }
}
```

**Правильные подходы:**

```kotlin
// ✅ ПРАВИЛЬНО: Передавайте только ID, загружайте данные в ViewModel

// 1. savedInstanceState — только ID и минимальное состояние
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // ✅ Сохраняем только ID, позицию скролла и фильтры
    outState.putLong("selected_item_id", selectedItemId)
    outState.putInt("scroll_position", recyclerView.scrollPosition)
    outState.putString("search_query", currentQuery)
}

// 2. Intent — только идентификатор
val intent = Intent(this, DetailActivity::class.java).apply {
    // ✅ Передаём ID, Activity загрузит данные сама
    putExtra("article_id", article.id)
}

// 3. Большие данные через ViewModel
class DetailViewModel(
    savedStateHandle: SavedStateHandle  // ← Автоматически из Bundle
) : ViewModel() {

    private val articleId: Long = savedStateHandle["article_id"] ?: 0L

    // ✅ Данные загружаются из Repository, не из Bundle
    val article = repository.getArticle(articleId)
        .stateIn(viewModelScope, SharingStarted.Lazily, null)
}
```

### 3.4. Как измерить размер Bundle

```kotlin
// Утилита для измерения размера Bundle (в байтах)
fun Bundle.sizeInBytes(): Int {
    val parcel = Parcel.obtain()
    try {
        parcel.writeBundle(this)
        return parcel.dataSize()
    } finally {
        parcel.recycle()
    }
}

// Использование
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // Добавляем данные
    outState.putString("query", query)
    outState.putIntegerArrayList("ids", ArrayList(selectedIds))

    // ✅ Проверяем размер в debug билдах
    if (BuildConfig.DEBUG) {
        val size = outState.sizeInBytes()
        Log.d("BundleSize", "savedInstanceState: ${size / 1024} КБ")

        if (size > 50 * 1024) {  // > 50 КБ
            Log.w("BundleSize", "⚠️ Bundle слишком большой! " +
                "Рекомендуется < 50 КБ, текущий: ${size / 1024} КБ")
        }
    }
}

// Для полной диагностики используйте TooLargeTool:
// implementation("com.gu.android:toolargetool:0.3.0")
// TooLargeTool.startRecording(application)
```

### 3.5. Подводные камни Binder

```
МАЛОИЗВЕСТНЫЕ ФАКТЫ О BINDER БУФЕРЕ:

1. UNCLOSED CURSORS СЪЕДАЮТ БУФЕР
   ┌─────────────────────────────────────────────────┐
   │ ContentResolver запрос к Contacts Provider:     │
   │ cursor = contentResolver.query(...)              │
   │ // Забыли cursor.close()                         │
   │ // → Cursor с blob данными занимает Binder буфер │
   │ // → Буфер растёт → TransactionTooLargeException │
   └─────────────────────────────────────────────────┘

2. FRAGMENT ARGUMENTS = ЧАСТЬ SAVEDINSTANCESTATE
   ┌─────────────────────────────────────────────────┐
   │ Fragment.arguments Bundle сохраняется           │
   │ автоматически в savedInstanceState Activity!     │
   │                                                 │
   │ 10 фрагментов × 50 КБ arguments каждый         │
   │ = 500 КБ в savedInstanceState Activity           │
   │ + View hierarchy state                           │
   │ = Потенциально > 1 МБ!                          │
   └─────────────────────────────────────────────────┘

3. ONSAVEINSTANCESTATE ВЫЗЫВАЕТСЯ ДЛЯ КАЖДОГО VIEW
   ┌─────────────────────────────────────────────────┐
   │ Каждый View с android:id сохраняет своё         │
   │ состояние автоматически:                         │
   │ - EditText: весь текст                           │
   │ - ScrollView: позиция скролла                    │
   │ - RecyclerView: scroll state                     │
   │                                                 │
   │ Много EditText с длинным текстом → большой Bundle│
   └─────────────────────────────────────────────────┘
```

---

## 4. Parcelable vs Serializable

### 4.1. Почему Parcelable быстрее в 10-17 раз

```
СРАВНЕНИЕ ПРОЦЕССОВ СЕРИАЛИЗАЦИИ:

SERIALIZABLE (Java):
┌──────────────────────────────────────────────────────────┐
│ 1. ObjectOutputStream создаёт множество внутренних       │
│    объектов (HandleTable, ReplaceTable, etc.)             │
│                                                          │
│ 2. REFLECTION: сканирование всех полей класса            │
│    → Class.getDeclaredFields()                           │
│    → Field.setAccessible(true)                           │
│    → Медленная рефлексия для каждого поля                │
│                                                          │
│ 3. Рекурсивная сериализация вложенных объектов           │
│    → Каждый уровень вложенности = ещё reflection         │
│                                                          │
│ 4. Запись метаданных: имена классов, serialVersionUID,   │
│    иерархия наследования, дескрипторы полей              │
│                                                          │
│ 5. Результат: много GC давления, большой output          │
│                                                          │
│ ИТОГО: ~1.0 мс (Nexus 10), ~5.1 мс (HTC Desire)        │
└──────────────────────────────────────────────────────────┘

PARCELABLE (Android):
┌──────────────────────────────────────────────────────────┐
│ 1. Parcel.obtain() — из пула, без аллокации              │
│                                                          │
│ 2. БЕЗ REFLECTION: разработчик явно пишет               │
│    parcel.writeString(name)                              │
│    parcel.writeInt(age)                                  │
│    → Каждый вызов = 1 JNI call                           │
│    → Прямая запись в нативный буфер (memcpy)             │
│                                                          │
│ 3. Минимум метаданных: только type tags (4 байта)        │
│                                                          │
│ 4. CREATOR.createFromParcel(parcel) — прямой конструктор│
│    → Без reflection, без временных объектов               │
│                                                          │
│ 5. Parcel.recycle() — обратно в пул                      │
│                                                          │
│ ИТОГО: ~0.085 мс (Nexus 10), ~0.29 мс (HTC Desire)     │
└──────────────────────────────────────────────────────────┘
```

### 4.2. Benchmark результаты

| Устройство | Serializable | Parcelable | Разница |
|------------|-------------|------------|---------|
| Nexus 10 (2012) | 1.0004 мс | 0.0850 мс | **11.8x** |
| LG G3 (2014) | 1.8539 мс | 0.1824 мс | **10.2x** |
| HTC Desire (2010) | 5.1224 мс | 0.2938 мс | **17.4x** |
| Samsung S10 (2019) | ~0.3 мс | ~0.03 мс | **~10x** |

**Нюанс от Netguru benchmark:** при малом количестве итераций (1,000) разница менее заметна. Парселизация показывает преимущество на старых устройствах и при большом количестве объектов.

### 4.3. Ручная реализация Parcelable

```kotlin
// Ручная реализация Parcelable (до @Parcelize)
// Показываем для понимания механизма

data class User(
    val id: Long,
    val name: String,
    val email: String?,       // Nullable!
    val age: Int,
    val tags: List<String>,
    val address: Address?     // Вложенный Parcelable
) : Parcelable {

    // Записываем данные в Parcel — ПОРЯДОК ВАЖЕН!
    override fun writeToParcel(parcel: Parcel, flags: Int) {
        parcel.writeLong(id)                    // 1. Long
        parcel.writeString(name)                // 2. String (не-null)
        parcel.writeString(email)               // 3. String? (может быть null)
        parcel.writeInt(age)                    // 4. Int
        parcel.writeStringList(tags)            // 5. List<String>
        parcel.writeParcelable(address, flags)  // 6. Вложенный Parcelable?
    }

    // 0 = нет файловых дескрипторов
    override fun describeContents(): Int = 0

    // Фабрика для создания объектов из Parcel
    companion object CREATOR : Parcelable.Creator<User> {

        // Читаем в ТОМ ЖЕ ПОРЯДКЕ что и записывали!
        override fun createFromParcel(parcel: Parcel): User {
            return User(
                id = parcel.readLong(),              // 1.
                name = parcel.readString()!!,         // 2.
                email = parcel.readString(),           // 3.
                age = parcel.readInt(),                // 4.
                tags = parcel.createStringArrayList()  // 5.
                    ?: emptyList(),
                address = parcel.readParcelable(       // 6.
                    Address::class.java.classLoader
                )
            )
        }

        override fun newArray(size: Int): Array<User?> {
            return arrayOfNulls(size)
        }
    }
}
```

**Проблемы ручной реализации:**
- **30+ строк boilerplate** на каждый класс
- Легко **ошибиться в порядке** записи/чтения
- Легко **забыть обновить** при добавлении нового поля
- Нет **компиляционной** проверки порядка

### 4.4. Когда использовать Serializable

```
DECISION TREE: Parcelable vs Serializable

Передаёте данные между компонентами Android?
├── ДА → Parcelable (или @Parcelize)
│   ├── Intent extras
│   ├── Fragment arguments
│   ├── savedInstanceState
│   └── Binder IPC
│
└── НЕТ → Зависит от контекста
    ├── Сохранение на диск → НЕТ (ни Parcelable, ни Serializable)
    │   └── Используйте: JSON, Protocol Buffers, Room
    │
    ├── Отправка по сети → НЕТ
    │   └── Используйте: JSON, gRPC, Protocol Buffers
    │
    ├── Кроссплатформенный код (KMP) → Serializable или kotlinx.serialization
    │
    └── Внутренний кэш в памяти → Обычные объекты (без сериализации)
```

---

## 5. @Parcelize: автоматическая генерация

### 5.1. Что такое @Parcelize

`@Parcelize` — аннотация из Kotlin Parcelize compiler plugin, которая автоматически генерирует `writeToParcel()`, `describeContents()` и `CREATOR` на этапе компиляции.

```kotlin
// ✅ Вместо 30+ строк boilerplate:
@Parcelize
data class User(
    val id: Long,
    val name: String,
    val email: String?,
    val age: Int,
    val tags: List<String>
) : Parcelable

// Всё! Компилятор сгенерирует всё остальное.
```

### 5.2. Подключение плагина

```kotlin
// build.gradle.kts (модуль приложения)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.parcelize")  // ← Добавить
}

// Никаких зависимостей не нужно — Parcelize входит в Kotlin stdlib
```

### 5.3. Как работает compiler plugin внутри

```
АРХИТЕКТУРА PARCELIZE COMPILER PLUGIN:

┌────────────────────────────────────────────────────────┐
│  ФАЗА 1: FRONTEND (SyntheticResolveExtension)          │
│                                                        │
│  ParcelizeResolveExtension:                            │
│  ├── isValidForParcelize(class)?                       │
│  │   ├── Есть @Parcelize?                              │
│  │   ├── Implements Parcelable?                        │
│  │   └── Все primary constructor params = val/var?     │
│  │                                                     │
│  ├── getSyntheticFunctionNames()                       │
│  │   → ["writeToParcel", "describeContents"]           │
│  │                                                     │
│  └── generateSyntheticMethods()                        │
│      → Объявляет writeToParcel и describeContents      │
│      → IDE и компилятор "видят" эти методы             │
│      → Не показывают ошибку "missing members"          │
│                                                        │
│  ЗАЧЕМ: Без фазы Frontend IDE будет показывать          │
│  ошибку: "Class must implement writeToParcel()"        │
├────────────────────────────────────────────────────────┤
│  ФАЗА 2: BACKEND (IrGenerationExtension)               │
│                                                        │
│  ParcelizeGenerationExtension:                         │
│  ├── Получает IR (Intermediate Representation) код     │
│  ├── Находит классы с @Parcelize                       │
│  └── Генерирует IR-код для:                            │
│                                                        │
│      writeToParcel(parcel, flags):                     │
│      ├── Для каждого свойства primary constructor:     │
│      │   ├── String → parcel.writeString(prop)         │
│      │   ├── Int → parcel.writeInt(prop)               │
│      │   ├── Parcelable → parcel.writeParcelable(prop) │
│      │   └── List<T> → parcel.writeList(prop)          │
│      │                                                 │
│      describeContents():                               │
│      ├── Проверяет: есть ли FileDescriptor в полях?    │
│      └── Если нет → return 0                           │
│                                                        │
│      CREATOR companion object:                         │
│      ├── createFromParcel(parcel):                     │
│      │   → Вызывает primary constructor с              │
│      │     parcel.readString(), parcel.readInt(), etc.  │
│      └── newArray(size): Array<T?>                     │
│          → arrayOfNulls(size)                          │
└────────────────────────────────────────────────────────┘
```

**Почему compiler plugin, а не annotation processor?**

```
ANNOTATION PROCESSOR (KAPT/KSP):
┌─────────────────────────────────────────┐
│ ✗ НЕ может добавлять методы             │
│   в существующие классы                  │
│ ✗ Может только генерировать НОВЫЕ файлы │
│ ✗ Потребовал бы создание отдельного      │
│   класса-обёртки для каждого Parcelable │
└─────────────────────────────────────────┘

COMPILER PLUGIN:
┌─────────────────────────────────────────┐
│ ✓ МОЖЕТ модифицировать существующие     │
│   классы через IR-трансформацию         │
│ ✓ Добавляет методы прямо в класс        │
│ ✓ IDE видит синтетические методы         │
│ ✓ Нет дополнительных файлов             │
└─────────────────────────────────────────┘
```

### 5.4. Система сериализаторов в Parcelize

Compiler plugin имеет разные сериализаторы для разных типов:

```
СЕРИАЛИЗАТОРЫ PARCELIZE (IrParcelSerializers.kt):

IrSimpleParcelSerializer:
├── String → writeString() / readString()
├── Int → writeInt() / readInt()
├── Long → writeLong() / readLong()
├── Float → writeFloat() / readFloat()
├── Double → writeDouble() / readDouble()
├── Boolean → writeInt(if(v) 1 else 0) / readInt() != 0
├── Byte → writeByte() / readByte()
└── CharSequence → writeCharSequence() / readCharSequence()

IrNullAwareParcelSerializer:
├── Оборачивает любой другой сериализатор
├── Сначала пишет флаг: writeInt(if(val != null) 1 else 0)
├── Если не null → делегирует основному сериализатору
└── При чтении: if(readInt() != 0) → читать, else → null

IrObjectParcelSerializer:
├── Для object classes (синглтоны)
├── Пишет 0 (dummy value)
└── При чтении: возвращает INSTANCE

IrEnumParcelSerializer:
├── Для enum classes
├── writeString(enum.name)
└── Enum.valueOf(readString())

IrListParcelSerializer:
├── writeInt(list.size)
├── Для каждого элемента → writeValue()
└── При чтении: createTypedArrayList() или createTypedArray()
```

### 5.5. Продвинутые возможности @Parcelize

```kotlin
// 1. Кастомная сериализация через @TypeParceler
// Для типов, которые не реализуют Parcelable

// Допустим, нужно передать java.util.Date через Parcel
object DateParceler : Parceler<Date> {
    override fun create(parcel: Parcel): Date {
        return Date(parcel.readLong())  // Читаем timestamp
    }

    override fun Date.write(parcel: Parcel, flags: Int) {
        parcel.writeLong(time)  // Пишем timestamp
    }
}

@Parcelize
@TypeParceler<Date, DateParceler>()
data class Event(
    val title: String,
    val date: Date  // ← Теперь Date парселизуется через DateParceler
) : Parcelable

// 2. Исключение свойств через @IgnoredOnParcel
@Parcelize
data class UserProfile(
    val id: Long,
    val name: String,
    @IgnoredOnParcel
    val cachedAvatar: Bitmap? = null  // НЕ сериализуется!
) : Parcelable

// 3. Sealed classes и наследование
@Parcelize
sealed class Result : Parcelable {
    @Parcelize
    data class Success(val data: String) : Result()

    @Parcelize
    data class Error(val message: String, val code: Int) : Result()

    @Parcelize
    data object Loading : Result()
}

// 4. Поддерживаемые типы из коробки
@Parcelize
data class ComplexData(
    // Примитивы
    val int: Int,
    val long: Long,
    val string: String,
    val boolean: Boolean,

    // Nullable
    val nullableString: String?,

    // Коллекции
    val list: List<String>,
    val set: Set<Int>,
    val map: Map<String, Int>,

    // Массивы
    val intArray: IntArray,
    val stringArray: Array<String>,

    // Вложенные Parcelable
    val nested: NestedParcelable,

    // Enum
    val status: Status,

    // Sealed class
    val result: Result
) : Parcelable
```

### 5.6. Подводные камни @Parcelize

```kotlin
// ❌ ОШИБКА 1: Свойства вне primary constructor НЕ парселизуются
@Parcelize
data class User(
    val id: Long,
    val name: String
) : Parcelable {
    var computedField: String = ""  // ⚠️ НЕ будет сериализовано!
    // После десериализации computedField = "" (default)
}

// ✅ РЕШЕНИЕ: Используйте @IgnoredOnParcel если это намеренно
@Parcelize
data class User(
    val id: Long,
    val name: String
) : Parcelable {
    @IgnoredOnParcel
    var computedField: String = ""  // Явно помечено как игнорируемое
}

// ❌ ОШИБКА 2: Использование не-Parcelable типов без Parceler
@Parcelize
data class Event(
    val date: LocalDateTime  // ❌ Compile error! Нет Parceler для LocalDateTime
) : Parcelable

// ✅ РЕШЕНИЕ: Создайте Parceler
object LocalDateTimeParceler : Parceler<LocalDateTime> {
    override fun create(parcel: Parcel): LocalDateTime =
        LocalDateTime.parse(parcel.readString())

    override fun LocalDateTime.write(parcel: Parcel, flags: Int) {
        parcel.writeString(toString())
    }
}

// ❌ ОШИБКА 3: Mutable коллекции
@Parcelize
data class Data(
    val items: MutableList<String>  // ⚠️ Работает, но...
    // После десериализации это будет ArrayList,
    // не оригинальный MutableList implementation
) : Parcelable

// ✅ ЛУЧШЕ: Используйте immutable коллекции
@Parcelize
data class Data(
    val items: List<String>  // ✅ Понятно что это read-only контракт
) : Parcelable
```

---

## 6. savedInstanceState: полный путь через систему

### 6.1. Обзор механизма

**savedInstanceState** — это Bundle, который Android автоматически сохраняет перед уничтожением Activity и восстанавливает при пересоздании. Этот Bundle проходит сложный путь через несколько процессов.

```
ПОЛНЫЙ ПУТЬ savedInstanceState:

ПРИЛОЖЕНИЕ (процесс)                    SYSTEM_SERVER (процесс)
┌──────────────────────┐                ┌─────────────────────┐
│                      │                │                     │
│ Activity             │                │ ActivityRecord      │
│ ├── onSaveInstance   │                │ ├── mState: Bundle  │
│ │   State(outState)  │─── Binder ────→│ │   (хранит Bundle) │
│ │                    │    IPC         │ │                    │
│ ├── Views save state │                │ ├── TaskRecord      │
│ │   (автоматически)  │                │ │   (стек Activities)│
│ │                    │                │ │                    │
│ └── Fragment.onSave  │                │ └── ActivityStack   │
│     InstanceState    │                │     (all stacks)    │
│                      │                │                     │
│         ...процесс убит...            │                     │
│                      │                │  Bundle ЖИВЁТ здесь │
│ Activity.onCreate    │                │  пока Activity в    │
│ ├── savedInstance ←──┼─── Binder ────┤  back stack         │
│ │   State            │    IPC         │                     │
│ └── Восстановление   │                │                     │
└──────────────────────┘                └─────────────────────┘
```

### 6.2. Сохранение: от onSaveInstanceState до system_server

**Полная цепочка вызовов (AOSP):**

```
ЭТАП 1: Инициация сохранения
────────────────────────────────────────────────────────
system_server (ActivityTaskManagerService):
  → Решает что Activity должна остановиться
  → Создаёт ClientTransaction с StopActivityItem
  → Отправляет через Binder в процесс приложения

ЭТАП 2: Обработка в процессе приложения
────────────────────────────────────────────────────────
TransactionExecutor.execute(transaction)
  → StopActivityItem.execute(client, token, pendingActions)
    → ActivityThread.handleStopActivity(token, configChanges)
      → ActivityThread.performStopActivityInner(r, saveState=true)
        → ActivityThread.callActivityOnSaveInstanceState(r)

ЭТАП 3: Создание Bundle и заполнение данными
────────────────────────────────────────────────────────
ActivityThread.callActivityOnSaveInstanceState(r):
  1. r.state = new Bundle()   // Создаём ЧИСТЫЙ Bundle
  2. Instrumentation.callActivityOnSaveInstanceState(activity, r.state)
     → Activity.performSaveInstanceState(outState)
       → Activity.onSaveInstanceState(outState)  // ← ВАШ КОД
       │   outState.putString("key", value)       // Вы кладёте данные
       │
       → ComponentActivity.onSaveInstanceState(outState)
         → SavedStateRegistryController.performSave(outState)
           → Для каждого зарегистрированного SavedStateProvider:
             → provider.saveState() → Bundle
             → Собирает все Bundles под ключом SAVED_COMPONENTS_KEY
  3. r.state = outState  // Сохраняем в ActivityClientRecord

ЭТАП 4: Отправка в system_server
────────────────────────────────────────────────────────
Bundle из ActivityClientRecord.state
  → Сериализуется в Parcel
  → Отправляется через Binder IPC
  → system_server: ActivityRecord.setSavedState(bundle)
  → Bundle хранится в памяти system_server
```

### 6.3. Что сохраняется автоматически

```
АВТОМАТИЧЕСКОЕ СОХРАНЕНИЕ СОСТОЯНИЯ:

Activity.onSaveInstanceState(outState):
┌─────────────────────────────────────────────────────────┐
│ 1. СУПЕРКЛАСС Activity:                                  │
│    → window.saveHierarchyState(outState)                 │
│    → Обходит КАЖДЫЙ View с android:id                    │
│    → Каждый View.onSaveInstanceState() → Parcelable      │
│    │                                                     │
│    │  EditText:   сохраняет весь текст и позицию курсора │
│    │  CheckBox:   checked/unchecked                       │
│    │  ScrollView: позиция скролла                         │
│    │  RecyclerView: LinearLayoutManager state             │
│    │  Spinner:    выбранная позиция                       │
│    │                                                     │
│    → Всё сохраняется в SparseArray<Parcelable>           │
│    → SparseArray пакуется в outState под ключом          │
│      "android:viewHierarchyState"                        │
│                                                          │
│ 2. FRAGMENTMANAGER:                                      │
│    → FragmentManager.saveAllState()                      │
│    → Для КАЖДОГО Fragment:                               │
│      → Fragment.performSaveInstanceState(outState)       │
│      → Fragment.arguments Bundle                         │
│      → Fragment.mSavedFragmentState                      │
│    → Back stack entries                                   │
│    → Всё под ключом "android:support:fragments"          │
│                                                          │
│ 3. SAVEDSTATEREGISTRY (Jetpack):                         │
│    → SavedStateRegistryController.performSave(outState)  │
│    → Все SavedStateHandle из ViewModel                   │
│    → Под ключом "androidx.lifecycle.BundlableSavedState" │
│                                                          │
│ 4. ВАШ КОД:                                             │
│    → Всё что вы положили в outState.putXxx()             │
└─────────────────────────────────────────────────────────┘
```

### 6.4. Восстановление: от system_server до onCreate

```
ЭТАП 1: system_server решает (пере)создать Activity
────────────────────────────────────────────────────────
ActivityTaskSupervisor.realStartActivityLocked(r, ...):
  → r.getSavedState()          // Достаём сохранённый Bundle
  → r.getPersistentSavedState() // persistent state
  → Создаём LaunchActivityItem(r.intent, ..., r.state, r.persistState)
  → ClientTransaction → Binder IPC → процесс приложения

ЭТАП 2: Процесс приложения получает команду
────────────────────────────────────────────────────────
TransactionExecutor.execute(transaction)
  → LaunchActivityItem.execute(client, token, pendingActions)
    → ActivityClientRecord r = new ActivityClientRecord(
          ..., mState=savedBundle, ...)
    → client.handleLaunchActivity(r, ...)

ЭТАП 3: Создание и инициализация Activity
────────────────────────────────────────────────────────
ActivityThread.handleLaunchActivity(r, ...):
  → ActivityThread.performLaunchActivity(r, ...)
    → Instrumentation.newActivity(...)     // Создаём Activity
    → activity.attach(...)                  // Инициализируем
    → Instrumentation.callActivityOnCreate(activity, r.state)
      → activity.performCreate(r.state, r.persistentState)
        → ComponentActivity.onCreate(savedInstanceState)
          │
          │ // Jetpack SavedState восстановление
          │ savedStateRegistryController.performRestore(savedInstanceState)
          │   → Извлекает Bundle по ключу SAVED_COMPONENTS_KEY
          │   → Сохраняет как restoredState для ленивого восстановления
          │
          └── Activity.onCreate(savedInstanceState)  // ← ВАШ КОД
              │ val query = savedInstanceState?.getString("query")
              │
              → super.onCreate(savedInstanceState)
                → View hierarchy восстановлена автоматически
                → Fragments восстановлены автоматически
```

### 6.5. SavedStateHandle: современная альтернатива

```kotlin
// СОВРЕМЕННЫЙ ПОДХОД: SavedStateHandle в ViewModel

// SavedStateHandle — type-safe обёртка над Bundle
// Автоматически сохраняется в onSaveInstanceState
// Автоматически восстанавливается при пересоздании

class SearchViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // ✅ Автоматически сохраняется/восстанавливается через Bundle
    val query: StateFlow<String> = savedStateHandle.getStateFlow("query", "")

    // ✅ LiveData с автосохранением
    val selectedFilters: MutableLiveData<List<String>> =
        savedStateHandle.getLiveData("filters", emptyList())

    fun updateQuery(newQuery: String) {
        savedStateHandle["query"] = newQuery  // Сохраняется автоматически
    }

    fun toggleFilter(filter: String) {
        val current = selectedFilters.value ?: emptyList()
        selectedFilters.value = if (filter in current) {
            current - filter
        } else {
            current + filter
        }
        // ← Автоматически сохраняется в Bundle
    }
}

// В Activity:
class SearchActivity : AppCompatActivity() {

    // ViewModel с SavedStateHandle создаётся автоматически
    private val viewModel: SearchViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Больше не нужно вручную сохранять/восстанавливать!
        // viewModel.query уже содержит восстановленное значение

        lifecycleScope.launch {
            viewModel.query.collect { query ->
                searchEditText.setText(query)
            }
        }
    }

    // ✅ onSaveInstanceState больше не нужен для этих данных
    // SavedStateHandle делает это автоматически
}
```

**Как SavedStateHandle работает внутри:**

```
SavedStateHandle МЕХАНИЗМ:

┌─────────────────────────────────────────────────────────┐
│ SavedStateHandle                                         │
│ ├── regular: Map<String, Any?>  (in-memory данные)      │
│ ├── savedStateProviders: Map<String, SavedStateProvider> │
│ └── flows/liveDatas                                      │
│                                                          │
│ СОХРАНЕНИЕ (onSaveInstanceState):                        │
│ SavedStateHandleController.performSave()                 │
│   → Для каждого ViewModel:                               │
│     → SavedStateHandle.savedStateProvider().saveState()   │
│       → Собирает regular + все вложенные providers        │
│       → Возвращает Bundle                                 │
│   → Кладёт Bundle в outState Activity                    │
│                                                          │
│ ВОССТАНОВЛЕНИЕ (onCreate):                               │
│ SavedStateHandleController.performRestore(savedState)    │
│   → Извлекает Bundle из savedState                       │
│   → Передаёт в SavedStateHandle constructor              │
│   → Данные доступны через get() / getStateFlow()         │
│                                                          │
│ КЛЮЧЕВОЕ: SavedStateHandle хранит ТОЛЬКО                 │
│ Bundle-совместимые типы! Если тип не помещается           │
│ в Bundle → IllegalArgumentException                      │
└─────────────────────────────────────────────────────────┘
```

### 6.6. Когда вызывается onSaveInstanceState

```
КОГДА ANDROID ВЫЗЫВАЕТ onSaveInstanceState:

ВСЕГДА ВЫЗЫВАЕТСЯ:
┌──────────────────────────────────────────────────────┐
│ ✓ Ротация экрана (configuration change)              │
│ ✓ Переход в другое Activity (Home, обратно в стек)   │
│ ✓ Многооконный режим (split screen, PiP)             │
│ ✓ Смена языка / темы (configuration change)          │
│ ✓ Система убивает Activity в фоне (low memory)       │
│                                                      │
│ ПОРЯДОК:                                              │
│ Android < API 28: ПЕРЕД onStop() (не гарантированно)  │
│ Android >= API 28: ПОСЛЕ onStop() (гарантированно)   │
└──────────────────────────────────────────────────────┘

НЕ ВЫЗЫВАЕТСЯ:
┌──────────────────────────────────────────────────────┐
│ ✗ Пользователь нажал "Назад" (finish)                │
│ ✗ Вызван activity.finish() программно                │
│ ✗ Вызван activity.finishAffinity()                   │
│ ✗ Система убила ВЕСЬ ПРОЦЕСС (не только Activity)    │
│   (но Bundle уже был сохранён ранее)                 │
└──────────────────────────────────────────────────────┘
```

---

## 7. Что хранить в Bundle и что нельзя

### 7.1. Правило: только навигационное состояние

```
ЗОЛОТОЕ ПРАВИЛО BUNDLE:

В Bundle хранят: "ЧТО ПОКАЗАТЬ ПОЛЬЗОВАТЕЛЮ"
В Bundle НЕ хранят: "САМИ ДАННЫЕ"

┌─────────────────────────────────────────────────────────┐
│                                                          │
│  ✅ ХРАНИТЬ В BUNDLE:            ❌ НЕ ХРАНИТЬ В BUNDLE: │
│  ─────────────────────           ─────────────────────── │
│  ID текущего элемента            Сам объект целиком      │
│  Позиция скролла                 Список всех элементов   │
│  Текст в поле поиска             Результаты поиска       │
│  Выбранная вкладка               Bitmap / изображения    │
│  Фильтры и сортировка            Файлы / большие строки  │
│  Развёрнутые/свёрнутые секции    JSON ответы API          │
│  Текущий шаг wizard              Объекты с Bitmap полями │
│  Флаг "показывать ли диалог"     Cursor / Database data  │
│                                                          │
│  Размер: < 50 КБ                 Размер: может быть MB   │
│  Загрузка: мгновенная             Загрузка: через ViewModel│
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.2. Полная архитектура сохранения состояния

```
СОВРЕМЕННАЯ АРХИТЕКТУРА СОХРАНЕНИЯ СОСТОЯНИЯ:

┌────────────────────────────────────────────────────────────┐
│                                                             │
│  UI STATE (что видит пользователь):                         │
│  ┌──────────────────────────────────────────────┐           │
│  │ ViewModel                                    │           │
│  │ ├── StateFlow<UiState>  (в памяти)           │           │
│  │ │   └── Данные, загруженные из Repository    │           │
│  │ │       Переживает: ротацию экрана            │           │
│  │ │       НЕ переживает: смерть процесса       │           │
│  │ │                                             │           │
│  │ ├── SavedStateHandle  (в Bundle)             │           │
│  │ │   └── Навигационное состояние (ID, query)   │           │
│  │ │       Переживает: ротацию + смерть процесса │           │
│  │ │       Лимит: < 50 КБ                        │           │
│  │ │                                             │           │
│  │ └── Repository (диск / сеть)                 │           │
│  │     └── Фактические данные                    │           │
│  │         Переживает: всё                       │           │
│  │         Лимит: нет                            │           │
│  └──────────────────────────────────────────────┘           │
│                                                             │
│  ПРИМЕР ПОТОКА:                                             │
│                                                             │
│  1. Пользователь открывает экран со списком статей          │
│  2. ViewModel загружает статьи из Repository                │
│  3. Пользователь скроллит → позиция сохраняется View       │
│  4. Пользователь вводит поиск → SavedStateHandle["query"]  │
│  5. Пользователь поворачивает экран:                        │
│     → ViewModel выживает (данные в памяти)                  │
│     → query восстановлен из SavedStateHandle               │
│  6. Система убивает процесс:                                │
│     → ViewModel уничтожен (данные потеряны)                 │
│     → query восстановлен из savedInstanceState              │
│     → ViewModel пересоздан → загружает данные заново        │
│     → Пользователь видит тот же экран                       │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 7.3. Типы данных и рекомендации

| Тип данных | Хранить в Bundle? | Почему | Где хранить |
|------------|-------------------|--------|-------------|
| `String` (до 1 КБ) | Да | Маленький, Bundle-friendly | SavedStateHandle |
| `Int`, `Long`, `Boolean` | Да | Примитивы, минимальный размер | SavedStateHandle |
| `List<String>` (до 100 элементов) | С осторожностью | Может вырасти | SavedStateHandle с лимитом |
| `Bitmap` | Нет | Может быть мегабайты | Файл + URI в Bundle |
| `List<Parcelable>` (1000+ элементов) | Нет | TransactionTooLargeException | Repository + ID в Bundle |
| `JSON String` (ответ API) | Нет | Непредсказуемый размер | Room/DataStore |
| `ByteArray` (большой) | Нет | Занимает Binder буфер | File + path в Bundle |
| `Enum` | Да (через name) | Строка, маленький | SavedStateHandle |
| `Sealed class` | Да (@Parcelize) | Контролируемый размер | SavedStateHandle |

### 7.4. Пример полной реализации

```kotlin
// ✅ ПОЛНЫЙ ПРИМЕР: правильная архитектура сохранения состояния

// 1. UI State — что показываем пользователю
data class ArticleListUiState(
    val articles: List<ArticleSummary> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val selectedCategory: Category = Category.ALL
)

// 2. Навигационное состояние — что сохраняем в Bundle
// Только идентификаторы и параметры отображения
@Parcelize
data class ArticleListNavState(
    val searchQuery: String = "",
    val selectedCategory: Category = Category.ALL,
    val scrollPosition: Int = 0,
    val isFilterExpanded: Boolean = false
) : Parcelable

// 3. ViewModel с SavedStateHandle
class ArticleListViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: ArticleRepository
) : ViewModel() {

    // Навигационное состояние восстанавливается из Bundle
    private val navState: ArticleListNavState
        get() = savedStateHandle.get<ArticleListNavState>("nav_state")
            ?: ArticleListNavState()

    // Поисковый запрос — через StateFlow с автосохранением
    val searchQuery = savedStateHandle.getStateFlow("search_query", "")

    // UI state — из Repository, не из Bundle
    private val _uiState = MutableStateFlow(ArticleListUiState())
    val uiState: StateFlow<ArticleListUiState> = _uiState.asStateFlow()

    init {
        // Восстанавливаем данные из Repository, не из Bundle!
        loadArticles(navState.selectedCategory, navState.searchQuery)
    }

    fun updateSearchQuery(query: String) {
        savedStateHandle["search_query"] = query  // В Bundle (< 1 КБ)
        loadArticles(navState.selectedCategory, query)
    }

    fun selectCategory(category: Category) {
        savedStateHandle["nav_state"] = navState.copy(
            selectedCategory = category
        )
        loadArticles(category, searchQuery.value)
    }

    fun saveScrollPosition(position: Int) {
        savedStateHandle["nav_state"] = navState.copy(
            scrollPosition = position
        )
    }

    private fun loadArticles(category: Category, query: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val articles = repository.getArticles(category, query)
                _uiState.value = _uiState.value.copy(
                    articles = articles,
                    isLoading = false,
                    selectedCategory = category
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }
}
```

---

## 8. Типы Bundle в Android

### 8.1. Различные Bundle-подобные классы

```
СЕМЕЙСТВО BUNDLE В ANDROID:

BaseBundle (abstract)
├── Bundle                    ← Основной, для Activity/Fragment
│   ├── Intent.getExtras()     → Bundle
│   ├── Fragment.getArguments() → Bundle
│   ├── savedInstanceState     → Bundle
│   └── Notification.extras    → Bundle
│
├── PersistableBundle         ← Для долговременного хранения
│   ├── Только примитивы и String
│   ├── НЕ поддерживает Parcelable
│   ├── Используется в JobScheduler
│   └── Может сериализоваться в XML
│
└── SparseArray<Parcelable>   ← Для View state
    └── View.onSaveInstanceState() → Parcelable
        (каждый View сохраняет свой state)

ContentValues                  ← НЕ наследник Bundle, но похож
├── Для ContentProvider insert/update
├── Основан на HashMap<String, Object>
└── Типизированные put/get методы
```

### 8.2. PersistableBundle

```kotlin
// PersistableBundle — ограниченная версия Bundle
// Поддерживает ТОЛЬКО: String, Int, Long, Double, Boolean, String[], IntArray, LongArray, DoubleArray
// НЕ поддерживает: Parcelable, Serializable, Bundle (вложенный)

// Используется в:
// 1. JobScheduler
val jobInfo = JobInfo.Builder(jobId, serviceComponent)
    .setExtras(PersistableBundle().apply {
        putString("task_type", "sync")
        putLong("user_id", userId)
        // putParcelable() — НЕ существует!
    })
    .build()

// 2. Activity persistentState (onSaveInstanceState с двумя Bundle)
override fun onSaveInstanceState(
    outState: Bundle,
    outPersistentState: PersistableBundle  // Выживает после перезагрузки!
) {
    super.onSaveInstanceState(outState, outPersistentState)
    outPersistentState.putLong("last_sync_timestamp", System.currentTimeMillis())
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|------------|
| "Bundle может хранить любой объект" | Bundle хранит только типы, поддерживаемые Parcel. Произвольный Object → crash |
| "Serializable — это OK для Android" | Serializable работает, но в 10-17x медленнее Parcelable. Используйте @Parcelize |
| "Parcelable данные можно сохранить на диск" | Бинарный формат Parcel может меняться между версиями Android. Никогда не персистируйте! |
| "1 МБ — это лимит на один Bundle" | 1 МБ — лимит на ВСЕ одновременные Binder транзакции процесса. Один большой Bundle может не вызвать проблему, но много средних — вызовут |
| "onSaveInstanceState вызывается всегда" | НЕ вызывается при finish() или нажатии "Назад". Только при уходе Activity в background |
| "savedInstanceState = лучшее место для состояния" | savedInstanceState — для навигационного состояния (< 50 КБ). Данные → ViewModel + Repository |
| "@Parcelize работает через annotation processing" | @Parcelize — это Kotlin **compiler plugin**, не annotation processor. Он модифицирует IR код, а не генерирует новые файлы |
| "Bundle thread-safe" | Bundle НЕ thread-safe. Одновременный доступ из разных потоков → corrupted data |
| "TreeMap в Bundle сохранит порядок" | Любой Map при Parcel round-trip превращается в HashMap. Порядок теряется |
| "Чем больше сохраним в savedInstanceState, тем лучше UX" | Большой savedInstanceState → TransactionTooLargeException → crash. Чем меньше — тем надёжнее |

---

## CS-фундамент

| CS-концепция | Применение в Bundle/Parcelable |
|-------------|-------------------------------|
| **Сериализация** | Parcel — бинарная сериализация с фиксированным порядком полей. Bundle — typed key-value сериализация через ArrayMap |
| **IPC (Inter-Process Communication)** | Bundle передаётся через Binder IPC между процессом приложения и system_server |
| **Binary Protocol** | Parcel использует type tags, length-prefixed строки и alignment для эффективной записи/чтения |
| **Object Pool** | Parcel.obtain()/recycle() — классический Object Pool pattern для избежания аллокации нативной памяти |
| **Lazy Initialization** | Bundle использует lazy unparcelling — десериализация откладывается до первого обращения к данным |
| **Memory Layout** | ArrayMap использует два массива (int[] + Object[]) вместо HashMap.Entry объектов для экономии памяти |
| **JNI Bridge** | Parcel.java → android_os_Parcel.cpp (JNI) → Parcel.cpp (native). Три слоя для эффективности |
| **Decorator Pattern** | BaseBundle → Bundle. PersistableBundle — ограниченная версия с подмножеством типов |
| **Producer-Consumer** | savedInstanceState: Activity (producer) → system_server (хранилище) → Activity (consumer) |
| **Binary Search** | ArrayMap использует binary search по отсортированному массиву hash-кодов для поиска ключей |

---

## Проверь себя

### Вопросы уровня "Основы"

**Q1:** Какую внутреннюю структуру данных использует Bundle для хранения значений?

<details>
<summary>Ответ</summary>

Bundle использует `ArrayMap<String, Object>` (через наследование от BaseBundle). ArrayMap хранит данные в двух массивах: `int[] mHashes` (хеши ключей, отсортированные) и `Object[] mArray` (чередование ключей и значений). Это экономит память по сравнению с HashMap, которая создаёт отдельный Entry-объект для каждой пары.

</details>

**Q2:** Почему Parcelable быстрее Serializable?

<details>
<summary>Ответ</summary>

Parcelable быстрее по трём причинам:
1. **Без reflection** — разработчик (или @Parcelize) явно пишет методы записи/чтения, а Serializable сканирует все поля через reflection
2. **Прямая запись в нативный буфер** — каждый writeXxx() вызов = 1 JNI call с memcpy в нативную память, без промежуточных Java-объектов
3. **Минимум метаданных** — Parcel записывает только type tags (4 байта), а Serializable пишет имена классов, serialVersionUID, дескрипторы полей

Результат: Parcelable в 10-17x быстрее в бенчмарках.

</details>

### Вопросы уровня "Продвинутое"

**Q3:** Что произойдёт если положить TreeMap в Bundle и прочитать обратно?

<details>
<summary>Ответ</summary>

TreeMap превратится в HashMap. Механизм: `Parcel.writeValue()` проверяет `instanceof Map` раньше чем `instanceof Serializable`. Map сериализуется через `writeMapInternal()`, который записывает только key-value пары с type tag `VAL_MAP`. При десериализации `readValue()` видит `VAL_MAP` и вызывает `readHashMap()`, который всегда создаёт HashMap. Конкретный тип Map-реализации нигде не сохраняется в бинарном формате Parcel.

</details>

**Q4:** Лимит Binder буфера 1 МБ — это на одну транзакцию или на весь процесс?

<details>
<summary>Ответ</summary>

1 МБ — это лимит на **весь процесс**, разделяемый между **всеми одновременными транзакциями**. Это значит, что даже если каждая отдельная транзакция небольшая, их сумма может превысить лимит. Например: запуск Activity (Intent), сохранение состояния (onSaveInstanceState), ContentProvider запрос, Service binding — всё это использует один и тот же буфер одновременно.

</details>

### Вопросы уровня "Экспертное"

**Q5:** Опишите полный путь Bundle при сохранении savedInstanceState — от Activity до system_server.

<details>
<summary>Ответ</summary>

1. `system_server` отправляет `StopActivityItem` через Binder в `ClientTransaction`
2. `TransactionExecutor` в процессе приложения выполняет `StopActivityItem.execute()`
3. `ActivityThread.handleStopActivity()` → `performStopActivityInner()` → `callActivityOnSaveInstanceState()`
4. Создаётся чистый `Bundle`, присваивается `ActivityClientRecord.state`
5. `Instrumentation.callActivityOnSaveInstanceState()` → `Activity.performSaveInstanceState()`
6. Вызывается `Activity.onSaveInstanceState(outState)` — пользовательский код
7. `ComponentActivity.onSaveInstanceState()` вызывает `SavedStateRegistryController.performSave()` — сохраняет SavedStateHandle ViewModel'ов
8. Заполненный Bundle сериализуется в Parcel через `writeToParcel()`
9. Parcel отправляется через Binder IPC в `system_server`
10. `ActivityRecord.setSavedState(bundle)` — Bundle хранится в памяти system_server
11. При пересоздании: `ActivityTaskSupervisor.realStartActivityLocked()` достаёт Bundle из `ActivityRecord`
12. Создаётся `LaunchActivityItem(mState=bundle)`, отправляется через Binder обратно
13. `Activity.onCreate(savedInstanceState)` получает восстановленный Bundle

</details>

**Q6:** Как @Parcelize compiler plugin устроен внутри? Почему это compiler plugin, а не annotation processor?

<details>
<summary>Ответ</summary>

@Parcelize состоит из двух фаз:

**Frontend (SyntheticResolveExtension):** `ParcelizeResolveExtension` объявляет синтетические методы `writeToParcel()` и `describeContents()` для классов с `@Parcelize`. Это нужно чтобы IDE и компилятор не показывали ошибку "missing members".

**Backend (IrGenerationExtension):** `ParcelizeGenerationExtension` модифицирует IR-дерево (Intermediate Representation), генерируя тело `writeToParcel()` (итерация по свойствам primary constructor → вызов соответствующего `parcel.writeXxx()`), тело `describeContents()` (проверка на FileDescriptor → return 0 или 1), и `CREATOR` companion object с `createFromParcel()` и `newArray()`.

Annotation processor (KAPT/KSP) не подходит потому что **не может добавлять методы в существующие классы** — может только генерировать новые файлы. Compiler plugin через `IrGenerationExtension` может модифицировать IR любого класса, добавляя реализации методов прямо в тело класса.

</details>

---

## Связанные темы

### Обязательные связи
- **[[android-activity-lifecycle]]** — Когда вызываются `onSaveInstanceState`/`onCreate`, как Bundle интегрирован в жизненный цикл Activity
- **[[android-state-management]]** — Полная картина управления состоянием: ViewModel + SavedStateHandle + Repository
- **[[android-viewmodel-internals]]** — SavedStateHandle, ViewModelStore, как ViewModel переживает конфигурационные изменения
- **[[android-navigation]]** — Navigation Component использует Bundle для передачи arguments между destinations

### Углубление
- **[[android-process-memory]]** — Binder IPC, устройство процессов, system_server, как LMK убивает процессы
- **[[android-handler-looper]]** — Message содержит Bundle (data поле), Handler использует Bundle для передачи данных
- **[[android-app-components]]** — Activity, Service, ContentProvider — все используют Bundle/Intent для коммуникации

### Смежные темы
- **[[android-intent-internals]]** — Intent.extras = Bundle, механизм разрешения Intent, PendingIntent
- **[[android-memory-leaks]]** — Bitmap в Bundle = утечка, большие Bundle = OOM
- **[[android-context-internals]]** — ContextImpl, ActivityThread — среда выполнения для savedInstanceState механизма

---

## Источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Parcelables and Bundles — Android Developers](https://developer.android.com/guide/components/activities/parcelables-and-bundles) | Docs | Официальное руководство по использованию Bundle и Parcelable |
| [Parcel API Reference](https://developer.android.com/reference/android/os/Parcel) | Docs | Справочник API Parcel с предупреждениями о хранении |
| [Parcelable implementation generator (@Parcelize)](https://developer.android.com/kotlin/parcelize) | Docs | Официальная документация @Parcelize |
| [The Mysterious Case of the Bundle and the Map — Sebastiano Poggi](https://blog.sebastiano.dev/the-mysterious-case-of-the-bundle-and-the-map/) | Article | Глубокий анализ потери типов Map при сериализации через Bundle |
| [SavedStateHandle and Bundle Under the Hood — Suleimanov](https://www.suleimanov.com/android/storedata/saved-state-handle-under-the-hood/) | Article | AOSP-уровневый анализ пути savedInstanceState через систему |
| [TransactionTooLargeException and a Bridge to Safety — Livefront](https://livefront.com/writing/transactiontoolargeexception-and-a-bridge-to-safety-part-1/) | Article | Детальный разбор причин и решений TransactionTooLargeException |
| [Binder Transaction Size — 1 MB Limit — Abhinay](https://abhinay212.medium.com/%EF%B8%8F-android-binder-transaction-size-1-mb-limit-you-should-know-d0886f3acf30) | Article | Объяснение Binder буфера и его ограничений |
| [Parcelable vs Serializable — Philippe Breault](https://www.developerphil.com/parcelable-vs-serializable/) | Article | Оригинальный benchmark Parcelable vs Serializable с числами |
| [Serializable vs Parcelable: Hidden Performance Battle](https://krayong.medium.com/serializable-vs-parcelable-in-android-the-hidden-performance-battle-79faf134c1fc) | Article | Современный анализ с объяснением механизмов |
| [Optimizing Performance: ArrayMap vs HashMap — droidcon](https://www.droidcon.com/2025/10/17/optimizing-android-performance-when-to-use-sparsearray-sparseintarray-and-arraymap-instead-of-hashmap/) | Article | Benchmark и рекомендации по выбору структуры данных |
| [Writing Kotlin Parcelize compiler plugin for iOS — Arkadii Ivanov](https://medium.com/bumble-tech/writing-kotlin-parcelize-compiler-plugin-for-ios-678d81eed27e) | Article | Внутреннее устройство Parcelize compiler plugin |
| [BaseBundle.java — AOSP](https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/os/BaseBundle.java) | AOSP | Исходный код BaseBundle — внутренняя логика хранения |
| [Bundle.java — AOSP](https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/os/Bundle.java) | AOSP | Исходный код Bundle |
| [Parcel.java — AOSP](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/os/Parcel.java) | AOSP | Java-слой Parcel с native методами |
| [Parcel.cpp — AOSP](https://cs.android.com/android/platform/superproject/+/master:frameworks/native/libs/binder/Parcel.cpp) | AOSP | Нативная реализация буфера и сериализации |
| [android_os_Parcel.cpp — AOSP](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/jni/android_os_Parcel.cpp) | AOSP | JNI мост между Java и нативным кодом |
| [ParcelizeIrTransformerBase.kt — Kotlin](https://github.com/JetBrains/kotlin/blob/master/plugins/parcelize/parcelize-compiler/parcelize.backend/src/org/jetbrains/kotlin/parcelize/ParcelizeIrTransformerBase.kt) | AOSP | Исходный код backend Parcelize plugin |
| [KEEP: Android Parcelable — Kotlin](https://github.com/Kotlin/KEEP/blob/master/proposals/extensions/android-parcelable.md) | Spec | Спецификация @Parcelize (Kotlin Enhancement Proposal) |

---

*Последнее обновление: 2026-01-27*
*Эталон стиля: [[android-handler-looper]] (Gold Standard)*

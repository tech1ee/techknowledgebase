---
title: "Хранение данных в Android: обзор и выбор подхода"
created: 2025-12-17
modified: 2026-02-13
type: overview
area: android
status: published
confidence: high
tags:
  - topic/android
  - topic/data
  - type/overview
  - level/intermediate
related:
  - "[[android-room-deep-dive]]"
  - "[[android-room-migrations]]"
  - "[[android-room-performance]]"
  - "[[android-datastore-guide]]"
  - "[[android-repository-pattern]]"
  - "[[android-networking]]"
  - "[[android-overview]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
reading_time: 11
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Хранение данных в Android: обзор и выбор подхода

## TL;DR

Обзор всех механизмов хранения данных в Android: Room, DataStore, файловое хранилище и сетевой кэш. Этот материал — **навигационный хаб** со ссылками на deep-dive материалы по каждому подходу. Выбор инструмента зависит от типа данных, объёма и требований к структуре.

---

## Deep-Dive материалы

| Что изучить | Файл | Когда нужен |
|---|---|---|
| Room: ORM поверх SQLite | [[android-room-deep-dive]] | Структурированные данные, SQL запросы, relations |
| Миграции Room | [[android-room-migrations]] | Обновление схемы БД между версиями |
| Производительность Room | [[android-room-performance]] | Оптимизация запросов, индексы, большие данные |
| DataStore | [[android-datastore-guide]] | Key-value настройки, замена SharedPreferences |
| Repository Pattern | [[android-repository-pattern]] | Single Source of Truth, offline-first |
| Сетевое кэширование | [[android-networking]] | OkHttp Cache, HTTP headers, offline |

---

## Дерево решений: какой способ хранения выбрать

```
Нужно сохранить настройку (boolean/string/int)?
  └─> DataStore → [[android-datastore-guide]]

Нужны SQL-запросы или связи между объектами?
  └─> Room → [[android-room-deep-dive]]

Файл больше 1MB или бинарный?
  └─> File Storage (ниже)

HTTP-запрос нужно кэшировать?
  └─> OkHttp Cache → [[android-networking]]
```

---

## Сравнение подходов

| Способ | Когда использовать | Примеры | Почему именно это решение |
|--------|-------------------|---------|---------------------------|
| **SharedPreferences** (устарело) | Не использовать в новом коде | - | Заменено на DataStore |
| **DataStore** | Простые настройки (key-value), небольшой объём | Тёмная тема, язык, флаги feature toggles | Асинхронность, типобезопасность, нет race conditions |
| **Room** | Структурированные данные, связи, запросы | Пользователи, заказы, чаты, избранное | SQL для сложных запросов, compile-time проверки, relations |
| **Files** (Internal) | Бинарные данные, большие файлы, нестандартные форматы | JSON кэш, загруженные PDF, временные файлы | Простота, не нужна структура БД |
| **Files** (External/MediaStore) | Медиа-файлы доступные другим приложениям | Фото, видео, музыка | Системная галерея, доступ из других приложений |
| **Network Cache** (OkHttp/Retrofit) | HTTP ответы для offline режима | API responses | Автоматическое управление, HTTP headers (Cache-Control) |

---

## История хранения данных в Android

```
2008    SharedPreferences + SQLiteOpenHelper (Android 1.0)
        └── Первые API: XML key-value и raw SQL

2012    ORMLite, GreenDAO
        └── Сторонние ORM для упрощения SQLite

2015    Realm
        └── Собственный движок, object-oriented, sync

2017    Room (Google I/O, Architecture Components)
        └── Compile-time ORM поверх SQLite, official Google solution

2020    DataStore (Jetpack)
        └── Замена SharedPreferences: async, Flow, type-safe

2023    Room 2.6 + KSP
        └── Миграция с KAPT на KSP, 2x быстрее builds

2024    Room KMP
        └── Кроссплатформенная поддержка (Android, iOS, Desktop)
```

**Ключевой переломный момент:** 2017 год — Google представил Room как часть Architecture Components. До Room каждая команда выбирала между raw SQLite, ORMLite, GreenDAO и Realm. Room стал стандартом де-факто благодаря compile-time проверкам SQL и нативной интеграции с Jetpack (LiveData, Flow, Paging).

---

## Room: почему это стандарт

Room — compile-time ORM поверх SQLite. Annotation processor (KSP) анализирует SQL запросы во время сборки и генерирует оптимальный код доступа к данным. Подробности: [[android-room-deep-dive]].

### Ключевые преимущества над raw SQLite

| Проблема SQLite | Решение Room |
|-----------------|-------------|
| Опечатка в SQL — runtime crash | Compile-time error |
| SQL injection уязвимости | Автоматический escaping параметров |
| Несоответствие типов | Compile-time проверка Entity ↔ Query |
| Забытый cursor.close() | Автоматическое управление ресурсами |
| Запрос на Main Thread → ANR | Принудительный suspend/Flow |
| Ручные миграции | AutoMigration + тестирование схем |

### Room vs другие ORM

| Критерий | Room | Realm | ObjectBox |
|----------|------|-------|-----------|
| **Поддержка Google** | Официальная | Сторонняя | Сторонняя |
| **Интеграция с Jetpack** | Нативная (LiveData, Flow, Paging) | Через адаптеры | Через адаптеры |
| **База данных** | SQLite (стандарт Android) | Собственная | Собственная |
| **Миграции** | AutoMigration + ручные | Автоматические | Автоматические |
| **Compile-time проверки SQL** | Да | Нет SQL | Нет SQL |
| **Размер библиотеки** | ~100KB | ~4MB | ~1MB |
| **Просмотр данных** | Любой SQLite viewer | Только Realm Studio | ObjectBox Browser |
| **Multiplatform (KMP)** | Да (с 2024) | Да | Да |

**Когда выбрать Realm/ObjectBox:**
- Синхронизация с облаком (Realm Sync, ObjectBox Sync)
- Предпочитаете объектный подход вместо реляционного
- Уже используете в существующем проекте

**Когда выбрать Room:**
- Стандартный Android проект
- Важна интеграция с Jetpack
- Нужен контроль над SQL запросами
- Важен маленький размер библиотеки
- Кроссплатформенность через Room KMP

---

## DataStore: замена SharedPreferences

DataStore — асинхронное key-value хранилище на основе Kotlin Flow. Решает все критические проблемы SharedPreferences: потокобезопасность, обработка ошибок, блокировка UI. Подробности: [[android-datastore-guide]].

| Критерий | SharedPreferences | DataStore |
|----------|-------------------|-----------|
| Потокобезопасность | Нет (apply async, но чтение синхронное) | Да (полностью async через Flow) |
| Обработка ошибок | Нет (silent fail при ошибке записи) | Да (через Flow.catch) |
| Блокировка UI | Возможна (getString на main thread) | Невозможна |
| Типизация | Только примитивы + String | Proto DataStore: строгая типизация |

**Два варианта DataStore:**
- **Preferences DataStore** — key-value, аналог SharedPreferences, но async
- **Proto DataStore** — типизированные объекты через Protocol Buffers

---

## Файловое хранилище

Для бинарных данных и файлов больше 1 MB Room и DataStore не подходят. Android предоставляет несколько API для работы с файлами.

### Internal Storage

Приватные файлы приложения в `/data/data/<package>/files/`. Не требуют разрешений. Удаляются при удалении приложения. Используйте `context.filesDir` для постоянных файлов и `context.cacheDir` для временных (система может очистить кэш при нехватке памяти).

### External Storage и Scoped Storage

С Android 10 (API 29) доступ к внешнему хранилищу ограничен через **Scoped Storage**:

- **Свои файлы** (`getExternalFilesDir()`) — не требуют разрешений, удаляются с приложением
- **Медиа-файлы** — через MediaStore API (фото, видео, аудио). Доступны другим приложениям
- **Произвольные файлы** — через Storage Access Framework (SAF) и `ACTION_OPEN_DOCUMENT`

### Когда Files вместо Room

Выбирайте файловое хранилище когда данные **не структурированные** (PDF, изображения, аудио), **большие** (> 1 MB на объект), или когда **не нужны SQL-запросы** (читаете файл целиком).

**Гибридный подход:** метаданные в Room, файлы отдельно:

```kotlin
@Entity
data class Course(
    @PrimaryKey val id: Long,
    val title: String,
    val videoPath: String  // File path → actual video in filesDir
)
```

---

## Single Source of Truth

Ключевой паттерн для persistence — **Single Source of Truth (SSOT)**. Локальная база данных (Room) служит единственным источником данных для UI. Сетевые данные обновляют базу, а UI подписывается на изменения через Flow. Это обеспечивает offline-first поведение и консистентность данных между экранами.

Подробнее о реализации: [[android-repository-pattern]].

---

## Связь с другими темами

### [[android-room-deep-dive]]

Детальное руководство по Room: Entity, DAO, Database, TypeConverters, Relations (@Embedded, @Relation), составные ключи. Все примеры кода и паттерны использования, которые были в этом файле, перенесены в deep-dive. Начинайте изучение с него после прочтения этого обзора.

### [[android-room-migrations]]

Миграции — критически важная тема при обновлении приложения. AutoMigration для простых изменений (добавление колонки), ручные миграции для сложных (переименование, изменение типа). Включает тестирование миграций через MigrationTestHelper.

### [[android-room-performance]]

Оптимизация Room для production: индексы (@Index), WAL mode, batch-операции, интеграция с Paging 3 для больших списков. Transaction management и анализ запросов через EXPLAIN QUERY PLAN.

### [[android-datastore-guide]]

Полный гайд по DataStore: Preferences и Proto варианты, миграция с SharedPreferences, обработка ошибок (IOException), паттерны использования с ViewModel и Hilt.

### [[android-repository-pattern]]

Repository паттерн связывает persistence слой с остальной архитектурой. Single Source of Truth, offline-first, кэширование стратегии. Room + Retrofit через Repository — стандартный подход в production приложениях.

### [[android-networking]]

Сетевой слой дополняет persistence: OkHttp Cache для HTTP кэширования, Retrofit для API запросов, интеграция с Room через Repository pattern для offline-first архитектуры.

### [[android-overview]]

Общий обзор Android-разработки даёт архитектурный контекст для persistence. Понимание слоёв приложения (Presentation → Domain → Data) помогает правильно организовать доступ к данным.

---

## Источники

### Официальная документация
- [Save Data in a Local Database Using Room](https://developer.android.com/training/data-storage/room) — официальная документация Room
- [DataStore Guide](https://developer.android.com/topic/libraries/architecture/datastore) — официальная документация DataStore
- [Data and File Storage](https://developer.android.com/training/data-storage) — обзор всех подходов к хранению

### Книги
- **Meier R. (2022)** *Professional Android* — подробное описание Room, DataStore и файлового хранилища с production-ready примерами.
- **Phillips B. et al. (2022)** *Android Programming: The Big Nerd Ranch Guide* — пошаговое руководство по Room с Entity, DAO и Database.

---

---

## Проверь себя

> [!question]- Почему для каждого типа данных нужен свой механизм хранения?
> SharedPreferences/DataStore: key-value (настройки, токены) -- быстрый доступ, маленький объем. Room: structured data (пользователи, заказы) -- SQL запросы, relations, migrations. File storage: binary data (фото, видео) -- большой размер, streaming. Неправильный выбор: настройки в Room = overhead, структурированные данные в SharedPreferences = нет query, нет migrations.

> [!question]- Сценарий: приложение хранит JWT токен в SharedPreferences. Какие риски?
> 1) SharedPreferences хранит данные в XML на файловой системе -- readable при root. 2) Нет encryption по умолчанию. 3) Backup может отправить на Google Drive. Решение: EncryptedSharedPreferences (Jetpack Security) или DataStore с encryption. Для high-security: Android Keystore для ключей шифрования.


---

## Ключевые карточки

Какие механизмы хранения данных в Android?
?
SharedPreferences/DataStore: key-value, настройки. Room: SQLite ORM, structured data. File storage: internal/external, media. ContentProvider: shared data между приложениями. EncryptedSharedPreferences: secure key-value.

Чем DataStore лучше SharedPreferences?
?
DataStore: 1) Coroutines + Flow (async, no ANR). 2) Type safety через Proto DataStore. 3) Нет apply/commit confusion. 4) Atomic reads/writes. SharedPreferences: sync на Main Thread (ANR), no type safety, possible data corruption.

Что такое Internal vs External storage?
?
Internal: /data/data/package/ -- только приложение, удаляется при uninstall. External: /sdcard/Android/data/package/ (scoped) или shared storage. Scoped Storage (Android 10+): доступ к shared storage только через MediaStore или SAF.

Что такое Scoped Storage?
?
Android 10+: приложение видит только свои файлы + MediaStore для shared media. Нет прямого доступа к чужим файлам. SAF (Storage Access Framework) для user-selected файлов. Безопаснее, но сложнее для file managers.

Когда использовать Room vs DataStore?
?
Room: structured data, queries, relations, > 100 записей, offline cache. DataStore: key-value (Preferences) или typed data (Proto), настройки, маленький объем. Правило: если нужен SQL query -- Room, если key-value -- DataStore.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-room-deep-dive]] | Room -- основная БД для Android |
| Углубиться | [[android-datastore-guide]] | DataStore для настроек и typed data |
| Смежная тема | [[ios-data-persistence]] | Data persistence в iOS |
| Обзор | [[android-overview]] | Вернуться к карте раздела |


*Проверено: 2026-02-11 | На основе официальной документации Android*

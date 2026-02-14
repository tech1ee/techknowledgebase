---
title: "SD Exercise: File Downloader Library"
created: 2026-02-14
modified: 2026-02-14
type: exercise
status: published
confidence: high
tags:
  - topic/career
  - type/exercise
  - level/advanced
  - interview
  - system-design
related:
  - "[[system-design-android]]"
  - "[[android-background-work]]"
  - "[[android-notifications]]"
  - "[[architecture-resilience-patterns]]"
prerequisites:
  - "[[system-design-android]]"
reading_time: 12
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# SD Exercise: File Downloader Library

Упражнение на проектирование библиотеки скачивания файлов -- классическая задача Mobile System Design. Формат: диалог кандидат/интервьюер, от сбора требований до trade-offs. Библиотека -- это не приложение: API должен быть универсальным, а архитектура -- расширяемой без привязки к конкретному use-case.

Перед разбором убедись, что знаком с общим фреймворком: [[system-design-android]].

---

## Задача -- "Design File Downloader Library"

Интервьюер формулирует намеренно расплывчато: *"Design a File Downloader Library"*. Задача кандидата -- задать правильные вопросы и сузить scope до реализуемого MVP за 45 минут. Типичная ошибка -- сразу рисовать архитектуру. Правильный подход -- сначала понять ограничения, затем определить API, затем рисовать компоненты.

---

## Сбор требований

Не более 5 минут. Ключевое -- выяснить границы: библиотека или фича приложения, размеры файлов, параллельность, жизненный цикл загрузок.

> **Candidate**: "Мы проектируем часть приложения или библиотеку общего назначения?"
> **Interviewer**: "Библиотеку общего назначения."

> **Candidate**: "Библиотека скачивает файл из интернета по HTTP и сохраняет на диск?"
> **Interviewer**: "Да."

> **Candidate**: "Какие типы файлов? Есть ограничения по размеру?"
> **Interviewer**: "Любые бинарные файлы, без ограничения по размеру."

> **Candidate**: "Нужна ли поддержка pause/resume/cancel и просмотр списка активных загрузок?"
> **Interviewer**: "Да, всё это нужно."

> **Candidate**: "Должна ли библиотека поддерживать одновременную загрузку нескольких файлов?"
> **Interviewer**: "А ты как думаешь?"
> **Candidate**: "Одновременная загрузка полезна -- например, скачивание видеоплейлиста. Но неограниченный параллелизм убьёт батарею и ресурсы. Лучший подход -- разумный дефолт (скажем, `4`) с возможностью конфигурации."

> **Interviewer**: "Почему именно `4`?"
> **Candidate**: "Для сетевого I/O число CPU-ядер -- не единственный фактор. Каждый worker блокируется на сети, поэтому можно взять и больше -- `16`. Но в общем случае `4`--`16` -- разумный диапазон. Пусть разработчик настроит под свой use-case."

> **Candidate**: "Нужен ли progress reporting для активных загрузок?"
> **Interviewer**: "Пока пропустим, обсудим если останется время."

> **Candidate**: "Аутентификация? HTTP range requests для докачки?"
> **Interviewer**: "Оба за пределами scope."

---

## Functional / Non-functional / Out of scope

### Functional Requirements

- Одновременная загрузка нескольких файлов по HTTP на диск
- Pause / resume / cancel отдельных и всех загрузок
- Получение списка активных загрузок

### Non-functional Requirements

- Ограниченное число параллельных загрузок (конфигурируемое)
- Поддержка файлов произвольного размера
- Минимальное потребление ресурсов (батарея, CPU, сеть)

### Out of Scope

- Аутентификация / авторизация
- HTTP range requests (докачка после обрыва)
- Шифрование файлов
- Progress reporting (follow-up)

---

## Client Public API

API библиотеки должен быть простым, расширяемым и не привязанным к конкретному фреймворку.

```
FileDownloader
  + init(config: FileDownloaderConfig)
  + download(request: FileDownloadRequest): FileDownloadTask
  + pauseAll()
  + resumeAll()
  + cancelAll()
  + activeTasks(): List<FileDownloadTask>

FileDownloadRequest
  + init(sourceUrl: Url, destPath: String)

FileDownloadTask
  + addDownloadCallback(callback: FileDownloadCallback)
  + pause()
  + resume()
  + cancel()

FileDownloaderConfig
  + init(maxParallelDownloads: Int = 4)

FileDownloadCallback
  + onComplete(request: FileDownloadRequest)
  + onFail(request: FileDownloadRequest, error: String)
  + onCancel(request: FileDownloadRequest)
```

| Класс | Роль |
|-------|------|
| **FileDownloader** | Точка входа: планирует, управляет загрузками |
| **FileDownloadRequest** | Инкапсуляция запроса: URL источника, путь назначения |
| **FileDownloadTask** | Handle асинхронной операции; позволяет управлять конкретной загрузкой |
| **FileDownloaderConfig** | Конфигурация: вынесена в объект для простоты рефакторинга (альтернатива -- Builder) |
| **FileDownloadCallback** | Callbacks завершения/ошибки/отмены |

Важный принцип: `FileDownloadTask` -- это *handle*, а не сама операция. Клиент может передать его в другой слой приложения, подписаться на callback позже или вызвать `cancel()` из UI. Это разделение запроса (Request) и управляемой операции (Task) -- стандартный паттерн для асинхронных API.

---

## High-Level Architecture

```
+------------------+
|   Client Code    |
+--------+---------+
         |
         | download(request)
         v
+--------+---------+      +--------------------+
|  File Downloader  |----->| Download Dispatcher|
|  (public API)     |      |  (scheduling)      |
+-------------------+      +---------+----------+
                                     |
                      +--------------+--------------+
                      |                             |
              +-------v--------+           +--------v-------+
              | Network Client |           |   File Store   |
              | (HTTP I/O)     |           |   (disk I/O)   |
              +----------------+           +----------------+

  Входные объекты:                Выходные объекты:
  +------------------+           +------------------+
  | Download Request |           |  Download Task   |
  | (url, path)      |           |  (handle)        |
  +------------------+           +------------------+
```

### Компоненты

| Компонент | Ответственность |
|-----------|----------------|
| **File Downloader** | Центральный фасад: принимает запросы, возвращает tasks, делегирует работу Dispatcher |
| **Download Request** | Данные запроса -- URL и путь сохранения |
| **Download Task** | Асинхронный handle: через него клиент управляет конкретной загрузкой |
| **Download Dispatcher** | Планирование, очередь, управление worker-ами |
| **Network Client** | Получение байтов по HTTP (абстракция над OkHttp / URLSession) |
| **File Store** | Запись на диск: init (pre-allocate), write (chunk), complete/fail (cleanup) |

---

## Deep Dive: Download Dispatcher

Dispatcher -- сердце библиотеки. Он управляет очередью и разделяет понятия **Job** и **Download Worker**.

```
Download Dispatcher
+------------------------------------------------------------+
|                                                            |
|  Concurrent Dispatch Queue                                 |
|  +------+  +------+  +------+  +------+  +------+         |
|  | Job1 |  | Job2 |  | Job3 |  | Job4 |  | Job5 |  ...   |
|  |ACTIVE|  |ACTIVE|  |PEND. |  |PAUSED|  |PEND. |         |
|  +--+---+  +--+---+  +------+  +------+  +------+         |
|     |         |                                            |
|     v         v                                            |
|  +--------+ +--------+                                     |
|  |Worker 1| |Worker 2|  ... (pool size = maxParallel)      |
|  +---+----+ +---+----+                                     |
|      |          |                                          |
+------------------------------------------------------------+
       |          |
       v          v
  Network     File Store
  Client
```

### Состояния Job

```
PENDING ----> ACTIVE ----> COMPLETED
   |             |
   |             +-------> FAILED
   |             |
   v             v
PAUSED <----> ACTIVE
   |
   +---> (cancel) ---> removed
```

Пять состояний: `PENDING`, `ACTIVE`, `PAUSED`, `COMPLETED`, `FAILED`.

### Job vs Download Worker

| Характеристика | Job | Download Worker |
|----------------|-----|-----------------|
| **Стоимость** | Дешёвый объект-метаданные | Дорогой: сетевой I/O, потоки |
| **Количество** | Неограниченное | Ограничено pool size |
| **Содержит** | Request + Task + State | HTTP-соединение + File Store handle |
| **Уникальность по URL** | Может быть несколько Job на один URL | Один Worker на уникальный URL |

### Почему разделение важно

Один и тот же файл может входить в разные плейлисты. Пользователь запускает загрузку обоих -- получается два Job-а для одного URL, но **один Worker**. Если отменить один Job, Worker продолжает работу для второго. Worker останавливается только когда **все** связанные Job-ы отменены.

### File Store: init / complete / fail

```
init(path, expectedSize)   -->  pre-allocate disk space
write(path, chunk)         -->  append bytes
complete(path)             -->  finalize, rename tmp -> target
fail(path)                 -->  cleanup temp files
```

Pre-allocation через `init` позволяет заранее проверить, хватит ли места на диске, до начала сетевой работы.

> **Interviewer**: "Зачем нужны Init и Complete/Fail в File Store?"
> **Candidate**: "Init даёт возможность зарезервировать место на диске до начала загрузки. Если Content-Length известен -- создаём файл нужного размера, и пользователь сразу получит ошибку `INSUFFICIENT_SPACE`, а не через 30 минут после начала. Complete переименовывает временный файл в целевой и выполняет post-processing. Fail -- удаляет временный файл, освобождая место."

### Алгоритм диспетчеризации

Каждый цикл Dispatcher выполняет следующую последовательность:

```
1. Подсчитать activeCount = jobs.count { state == ACTIVE }
2. Если activeCount < maxParallelDownloads:
   a. Взять следующий PENDING job из очереди
   b. Найти или создать Worker для данного URL
   c. Связать Job с Worker
   d. Перевести Job в ACTIVE
3. Для каждого завершённого Worker:
   a. Перевести все связанные Job-ы в COMPLETED
   b. Вызвать onComplete callback для каждого Job-а
   c. Вернуть Worker в pool
4. Повторить (event-driven, не polling)
```

Этот цикл -- event-driven: он просыпается при новых запросах, завершениях Worker-ов или вызовах pause/resume/cancel. Polling не нужен -- это сэкономит CPU и батарею.

---

## Follow-up: Progress Tracking

> **Interviewer**: "Как изменится дизайн, если нужно отслеживать прогресс загрузок?"

> **Candidate**: "Добавим компонент **Progress Store** -- реляционная БД (SQLite / Room), которая хранит состояние каждого Job-а. Каждый Worker вызывает progress callback при получении очередного chunk-а байтов. Progress Store обновляет запись в таблице. При завершении -- запись удаляется или помечается."

### Схема таблицы

| Поле | Тип | Описание |
|------|-----|----------|
| `url` | String | URL источника |
| `path` | String | Путь назначения |
| `created_at` | Date | Время создания Job-а |
| `total_bytes` | Long | Ожидаемый размер (из Content-Length) |
| `downloaded_bytes` | Long | Текущий прогресс |
| `state` | Int | Enum: PENDING / ACTIVE / PAUSED / ... |

> **Interviewer**: "Почему не хранить файлы прямо в БД?"
> **Candidate**: "Файлы на диске доступнее: произвольный доступ, streaming, memory-mapped I/O. BLOB в БД усложняет частичное чтение и увеличивает размер базы."

---

## Follow-up: Download Priority

> **Interviewer**: "Как добавить приоритеты загрузок? Например: user-critical, UI-critical, background, low-priority."

> **Candidate**: "Два варианта:"

**Вариант A -- Priority Queue в Dispatcher:**
- Добавить поле `priority` в `FileDownloadRequest`
- Dispatcher использует PriorityQueue вместо FIFO
- Плюс: единая точка управления; минус: сложнее реализация

**Вариант B -- Отдельные экземпляры FileDownloader:**
- По одному FileDownloader на каждый уровень приоритета
- Каждый со своим pool size
- Плюс: изоляция, проще код; минус: нужна синхронизация между экземплярами для общего лимита ресурсов

На практике для MVP достаточно Варианта A. Вариант B полезен, когда приоритеты имеют принципиально разные SLA.

---

## Follow-up: Шифрование загруженных файлов

> **Interviewer**: "Как обрабатывать скачивание конфиденциальных данных?"
> **Candidate**: "Можно ввести `EncryptedFileStore` -- реализацию File Store, которая шифрует полностью загруженный файл на этапе `complete()`. Post-processing подход проще: после успешной записи временный файл шифруется AES-256 и записывается в целевой путь, а оригинал удаляется."

```
FileStore (interface)
  |
  +---> DefaultFileStore      (plain write)
  |
  +---> EncryptedFileStore    (encrypt on complete)
```

> **Candidate**: "Шифрование на лету (chunk-by-chunk) потенциально быстрее для больших файлов, но требует потокового шифра и усложняет random access. Для MVP -- post-processing на этапе `complete()` достаточен."

---

## Foreground vs Background Downloads

Критически важное решение для мобильной платформы. Подробнее о фоновых задачах: [[android-background-work]].

### Foreground Download

Выполняется в worker thread внутри процесса приложения.

| Плюсы | Минусы |
|-------|--------|
| Мгновенный запуск | Убивается при уходе приложения в background |
| Простая отладка | Зависит от жизненного цикла Activity/Service |
| Ограничен только ресурсами системы | Не подходит для больших файлов |

### Background Download

Выполняется в отдельном процессе; переживает сворачивание и даже перезагрузку.

| Плюсы | Минусы |
|-------|--------|
| Гарантированное выполнение (WorkManager / BGURLSession) | Сложная настройка и отладка |
| Переживает перезагрузку устройства | ОС может откладывать загрузку (ждёт Wi-Fi, зарядку) |
| Подходит для больших файлов | Ограничения платформы (Background Transfer Limits) |

### Реализация в архитектуре

```
FileDownloadRequest
  + downloadMode: DownloadMode  // FOREGROUND | BACKGROUND

Download Dispatcher
  |
  +---> ForegroundWorker  (in-process thread pool)
  |
  +---> BackgroundWorker  (WorkManager / DownloadManager)
```

Dispatcher выбирает реализацию Worker-а на основе `downloadMode` в запросе. Это позволяет клиенту явно управлять стратегией, а библиотеке -- оставаться гибкой.

При фоновых загрузках полезны уведомления для пользователя: [[android-notifications]].

На Android для Background Download естественный выбор -- `WorkManager` с `CoroutineWorker`. Для iOS -- `URLSessionDownloadTask` с фоновой конфигурацией. Оба механизма обеспечивают продолжение загрузки после завершения процесса приложения, но требуют корректной обработки восстановления состояния при перезапуске.

---

## Trade-offs

### Сеть / CPU / Батарея

Слишком много параллельных загрузок негативно влияют на батарею и расход трафика. Стратегии митигации:

- **Cellular**: снижать `maxParallelDownloads` до `1`--`2`
- **Low battery**: приостанавливать фоновые загрузки
- **Wi-Fi + зарядка**: разрешать максимальный параллелизм

Подробнее о паттернах устойчивости: [[architecture-resilience-patterns]].

### Pre-allocation дискового пространства

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| Pre-allocate | Гарантия места до начала загрузки | Может резервировать слишком много |
| Ленивая запись | Экономия места | Может не хватить места в середине загрузки |
| Конфигурируемый | Гибкость для разработчика | Сложнее API |

В общем случае лучше сделать это конфигурируемым: `FileDownloaderConfig.preallocateDiskSpace: Boolean`.

### Повторные попытки (Retry)

Сетевые ошибки неизбежны. Базовая стратегия:

```
RetryPolicy:
  + maxRetries: Int = 3
  + backoffMs: Long = 1000
  + backoffMultiplier: Float = 2.0
```

Exponential backoff с джиттером. При исчерпании попыток -- Job переходит в `FAILED`, callback уведомляет клиента. Подробнее: [[architecture-resilience-patterns]].

### Thread Safety

Download Dispatcher работает с конкурентной очередью: несколько потоков могут одновременно добавлять Job-ы, отменять, получать список активных загрузок. Необходимые гарантии:

- Dispatch Queue защищена через `synchronized` блоки или `ReentrantLock`
- Worker pool использует `ThreadPoolExecutor` с ограниченным размером
- Callbacks вызываются на main thread (или на caller thread -- зависит от контракта API)
- Состояние Job-а меняется атомарно, чтобы избежать гонок между `pause()` и `complete()`

Альтернатива -- single-threaded event loop для Dispatcher (как в Kotlin Coroutines с `Dispatchers.Default.limitedParallelism(1)`), что устраняет необходимость в lock-ах.

---

## Проверь себя

1. **Зачем разделять Job и Download Worker?** В чём разница по стоимости и жизненному циклу?
2. **Что произойдёт при отмене одного Job из двух, привязанных к одному URL?** Когда Worker остановится?
3. **Foreground vs Background download**: когда что использовать? Какие ограничения платформы?
4. **Как добавить progress tracking, не меняя public API?** Какой компонент добавится в архитектуру?
5. **Почему нельзя просто делать `maxParallelDownloads = 100`?** Какие ресурсы пострадают?

---

## Ключевые карточки

| # | Вопрос | Ответ |
|---|--------|-------|
| 1 | Пять состояний Job в Dispatcher | `PENDING` -> `ACTIVE` -> `COMPLETED` / `FAILED`; боковые: `PAUSED` |
| 2 | Job vs Worker: главное отличие | Job -- дешёвые метаданные (неограниченно); Worker -- дорогой I/O (pool limited) |
| 3 | Несколько Job на один URL | Один Worker обслуживает все; останавливается, только когда ВСЕ Job-ы отменены |
| 4 | File Store: зачем init/complete? | Pre-allocation диска + post-processing (переименование tmp, cleanup) |
| 5 | Progress Store: почему БД, а не файл? | Структурированные запросы, атомарные обновления, выживает crash |
| 6 | Background download: главный trade-off | Гарантия выполнения vs сложность отладки и ограничения ОС |

---

## Куда дальше

| Направление | Ссылка |
|-------------|--------|
| Общий фреймворк Mobile System Design | [[system-design-android]] |
| Фоновая работа на Android | [[android-background-work]] |
| Уведомления о загрузке | [[android-notifications]] |
| Паттерны отказоустойчивости (retry, circuit breaker) | [[architecture-resilience-patterns]] |
| Упражнение: Caching Library | [[sd-exercise-caching-library]] |

---

## Источники

- [Mobile System Design -- File Downloader Library (iartr/mobile-system-design)](https://github.com/iartr/mobile-system-design/blob/master/exercises/file-downloader-library.md) -- оригинальное упражнение
- [Mobile System Design (weeeBox)](https://github.com/weeeBox/mobile-system-design) -- фреймворк и методология
- [Android WorkManager Guide](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started) -- фоновые задачи
- [OkHttp](https://square.github.io/okhttp/) -- HTTP-клиент для Android/JVM

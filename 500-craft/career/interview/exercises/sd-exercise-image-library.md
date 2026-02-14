---
title: "SD Exercise: Image Loading Library"
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
  - "[[caching-strategies]]"
  - "[[android-recyclerview-internals]]"
  - "[[android-memory-leaks]]"
prerequisites:
  - "[[system-design-android]]"
reading_time: 14
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# SD Exercise: Image Loading Library

Задача "Design an Image Loading Library" -- один из классических вопросов на mobile system design интервью. Библиотека загрузки изображений (Coil, Glide, Picasso) -- компонент, который есть в каждом мобильном приложении. Интервьюер проверяет, понимаешь ли ты, что скрывается за одной строчкой `imageLoader.load(url).into(imageView)`: кэширование, управление памятью, декодирование, жизненный цикл.

Этот exercise -- пошаговый walkthrough в формате диалога кандидата и интервьюера. Используй его для подготовки: прочитай, попробуй решить самостоятельно, затем сверься с ответами.

> **Связанные материалы**: [[system-design-android]] (общий фреймворк), [[sd-exercise-caching-library]] (смежная задача)

---

## Задача -- "Design Image Library"

Формулировка намеренно расплывчатая: **"Design an Image Library"**. Интервьюер ожидает, что ты сам уточнишь требования, сузишь scope и предложишь MVP.

---

## Сбор требований

Первые 5 минут -- уточняющие вопросы. Не бросайся рисовать диаграммы сразу.

> **Candidate**: "Мы проектируем часть конкретного приложения или универсальную библиотеку?"
> **Interviewer**: "Универсальную библиотеку."

> **Candidate**: "Библиотеку для загрузки изображений или для управления фотогалереей?"
> **Interviewer**: "Для загрузки изображений."

> **Candidate**: "Откуда нужно загружать изображения?"
> **Interviewer**: "Хороший вопрос -- предложи сам."

> **Candidate**: "Логично поддержать три источника: сеть, файловая система и ресурсы приложения. Можно предусмотреть API для кастомных загрузчиков, но пока оставим это за рамками."
> **Interviewer**: "Согласен, оставим за рамками."

> **Candidate**: "Нужно ли загружать изображения напрямую в UI-компоненты?"
> **Interviewer**: "Что ты имеешь в виду?"
> **Candidate**: "Например, в ImageView, Button и подобные. Библиотека сама устанавливает Bitmap в целевой компонент."
> **Interviewer**: "Да, это нужно."

> **Candidate**: "Стоит также поддержать non-UI targets: сохранение в файл или callback для доступа к raw-данным изображения."
> **Interviewer**: "Хорошая идея."

> **Candidate**: "Я бы добавил кэширование -- и в памяти, и на диске. Это экономит трафик и упрощает работу в offline."
> **Interviewer**: "Согласен."

> **Candidate**: "Ещё важная вещь -- управление жизненным циклом для UI-targets."
> **Interviewer**: "Поясни."
> **Candidate**: "Библиотека должна отслеживать lifecycle View: прерывать загрузку, когда View открепляется от иерархии, становится невидимым или переиспользуется при скролле в RecyclerView. Это предотвращает утечки памяти и бесполезную работу."
> **Interviewer**: "Да, это обязательно."

> **Candidate**: "Хорошо бы добавить thumbnails, placeholders, анимации переходов -- но предлагаю вынести за scope."
> **Interviewer**: "Что такое thumbnails?"
> **Candidate**: "Многие бэкенды предоставляют low-resolution версии изображений. На медленных сетях библиотека сначала загружает thumbnail, а затем полноразмерное изображение -- UI отрисовывается быстрее."
> **Interviewer**: "Оставим за рамками."

---

## Functional / Non-functional / Out of Scope

### Functional Requirements (FR)
- Загрузка изображений из сети, файловой системы и ресурсов приложения
- Поддержка UI-targets (ImageView и другие) и non-UI targets (callback, файл)

### Non-functional Requirements (NFR)
- Кэширование в памяти (memory cache) и на диске (disk cache)
- Управление жизненным циклом View -- остановка загрузки при detach/invisible/recycle

### Out of Scope
- Кастомные загрузчики (custom image loaders)
- Placeholders, индикаторы загрузки, анимации переходов
- Thumbnails и multi-resolution стратегии

---

## High-Level Architecture

```
+------------------+          +-------------------+
|  Image Request   |--------->|  Request Manager  |
|  (source, size,  |          |  (dispatch,       |
|   format, target)|          |   coordinate)     |
+------------------+          +---------+---------+
                                        |
                          +-------------+-------------+
                          |                           |
                +---------v---------+       +---------v---------+
                |   Image Cache     |       |   Image Loader    |
                |   (LRU in-memory) |       |   (network, fs,   |
                |                   |       |    resources)      |
                +-------------------+       +---------+---------+
                                                      |
                                            +---------v---------+
                                            |   Data Decoder    |
                                            |   (JPEG, PNG,     |
                                            |    WebP, ...)     |
                                            +-------------------+

                          +-------------------+
                          |   Image Target    |
                          |   (ImageView,     |
                          |    callback,      |
                          |    file)          |
                          +-------------------+
```

### Компоненты

| Компонент | Ответственность |
|-----------|----------------|
| **Image Request** | Инкапсулирует параметры запроса: источник, размер, формат, целевой объект |
| **Request Manager** | Принимает запросы, проверяет кэш, координирует загрузку и доставку |
| **Image Cache** | Быстрый in-memory LRU-кэш для повторного доступа |
| **Image Loader** | Загрузка данных из разных источников (сеть, файлы, ресурсы) |
| **Data Decoder** | Декодирование сырых байтов в Bitmap/Image |
| **Image Target** | Абстракция получателя: UI-компонент, callback, файл |

**Поток данных** (пошагово):

```
1. Client создаёт ImageRequest: load(uri).resize(w,h).into(imageView)
2. Request Manager получает запрос
3. Генерирует ImageKey из параметров
4. Проверяет Image Cache (memory hit?)
   +-- HIT  -> доставляет в Image Target, DONE
   +-- MISS -> переходит к шагу 5
5. Image Loader выбирает Fetcher по схеме URI
   - "https://" -> NetworkFetcher
   - "file://"  -> FileFetcher
   - "res://"   -> ResourceFetcher
6. Fetcher загружает raw bytes
7. Data Decoder конвертирует bytes -> Bitmap
8. Результат сохраняется в Image Cache
9. Результат доставляется в Image Target
```

> **Важный нюанс**: Request Manager также отвечает за дедупликацию запросов. Если два ImageView запрашивают одну и ту же картинку одновременно (например, один URL в двух ячейках списка), создаётся только одна загрузка, а оба target получают результат.

---

## Deep Dive: Image Cache

> **Interviewer**: "Расскажи подробнее о компоненте Image Cache."
> **Candidate**: "Это in-memory LRU-кэш. Хранит подмножество загруженных изображений для быстрого повторного доступа без обращения к диску или сети."

> **Interviewer**: "Какой ключ кэша?"
> **Candidate**: "Первый вариант -- URI источника. Но этого мало: одно и то же изображение может запрашиваться с разными размерами и форматами. Поэтому я создам составной ключ ImageKey."

```
ImageKey:
  + source: Uri
  + width: Int
  + height: Int
  + format: ImageFormat    // RGBA_8888, RGB_565 и т.д.
```

> **Interviewer**: "Зачем включать размеры?"
> **Candidate**: "Чтобы хранить изображение уже в целевом размере. Это экономит память и ускоряет отрисовку -- не нужно масштабировать на каждый draw-вызов. Если один и тот же URL запрашивается в разных размерах (аватар 48dp и превью 200dp) -- это разные записи кэша."

> **Interviewer**: "Что такое format?"
> **Candidate**: "Формат пикселей. RGBA_8888 -- 4 байта на пиксель (с альфой), RGB_565 -- 2 байта (без альфы, меньше цветовая глубина). Для фоновых изображений без прозрачности RGB_565 экономит 50% памяти."

> **Interviewer**: "А disk cache?"
> **Candidate**: "Disk cache актуален только для сетевых изображений. Я бы делегировал его HTTP-клиенту."

> **Interviewer**: "Почему?"
> **Candidate**: "Современные HTTP-клиенты (OkHttp, URLSession) имеют встроенный disk cache, который уважает заголовки `Cache-Control`. Мы указываем размер кэша, а клиент сам управляет expiration, ETag, conditional requests. Не нужно изобретать это заново."

> **Interviewer**: "Какой размер in-memory кэша?"
> **Candidate**: "Сложный вопрос, потому что мы не знаем memory footprint host-приложения. Простая эвристика -- выделить долю от максимальной памяти процесса. Google рекомендует 1/8 от `maxMemory()`. Для устройства с 256 MB heap это ~32 MB."
> **Candidate**: "Также стоит подписаться на low-memory callbacks (`onTrimMemory` на Android, `didReceiveMemoryWarning` на iOS) и очищать кэш при нехватке памяти."

```
// Пример: размер in-memory кэша
val maxMemory = Runtime.getRuntime().maxMemory()  // bytes
val cacheSize = maxMemory / 8                      // ~12.5% heap
val lruCache = LruCache<ImageKey, Bitmap>(cacheSize.toInt())
```

> **Связь с другими темами**: подробнее о стратегиях кэширования -- [[caching-strategies]], утечки памяти при неправильном кэшировании -- [[android-memory-leaks]].

---

## Deep Dive: Image Loader

> **Interviewer**: "Расскажи про Image Loader."
> **Candidate**: "Image Loader загружает данные из источников: сеть, файловая система, ресурсы приложения. Он принимает LoaderRequest и возвращает результат через callback."

```
LoaderRequest:
  + key: ImageKey
  + callback: (key: ImageKey, image: Image?, error: String?) -> Unit
```

> **Candidate**: "Ключевое архитектурное решение -- разделить загрузку данных (fetching raw bytes) и декодирование (converting bytes to Bitmap). Это позволяет добавлять новые декодеры через паттерн Strategy без изменения загрузчика."

```
+-------------------+     +-------------------+     +-------------------+
|   Source Fetcher   |---->|   Raw Bytes       |---->|   Image Decoder   |
|   (Network /       |     |                   |     |   (JPEG / PNG /   |
|    File / Resource) |     |                   |     |    WebP / AVIF)   |
+-------------------+     +-------------------+     +-------------------+
```

> **Candidate**: "Каждый источник -- отдельный Fetcher. NetworkFetcher использует HTTP-клиент, FileFetcher читает с диска, ResourceFetcher загружает из ресурсов APK/IPA. Новый источник -- новый Fetcher, остальной код не меняется."

> **Interviewer**: "А на Android есть ещё какие-то оптимизации?"
> **Candidate**: "Да, BitmapPool. Когда Bitmap больше не нужен, вместо того чтобы отдавать его GC, мы возвращаем его в пул. При следующей загрузке Bitmap.decode переиспользует существующий буфер через `inBitmap`. Это снижает давление на GC и уменьшает аллокации, что критично при быстром скролле в RecyclerView."

> **Связь**: детали RecyclerView recycling -- [[android-recyclerview-internals]].

> **Interviewer**: "Почему в Image Loader нет кэширования?"
> **Candidate**: "Single Responsibility Principle. Image Loader занимается только загрузкой. Кэширование -- ответственность Request Manager и Image Cache. Loader не знает, откуда пришёл запрос и будет ли результат закэширован."
> **Candidate**: "Правда, HTTP-клиент внутри NetworkFetcher обрабатывает disk cache. Это компромисс: чистота архитектуры vs простота реализации. Для MVP -- приемлемо, но при масштабировании библиотеки может стать проблемой."

> **Interviewer**: "Почему проблемой?"
> **Candidate**: "Зависимость от конкретного HTTP-клиента может привести к version conflicts с host-приложением. Нужно решить: обновляться каждый релиз, только мажорные версии, или держать приватный форк. Ещё бывают проблемы с лицензированием."

> **Interviewer**: "Зачем тогда вообще использовать зависимость?"
> **Candidate**: "Это классический trade-off: implement vs re-use. Написать свой HTTP-стек с disk cache, ETag, conditional requests -- это месяцы работы. Для MVP я выберу time-to-market и возьму существующий клиент. В будущих релизах можно абстрагировать сетевой слой за интерфейсом и при необходимости заменить реализацию."

> **Candidate**: "Кстати, можно также добавить поддержку аутентификации на уровне NetworkFetcher -- для загрузки изображений из защищённых API. Но это оставим за рамками."

---

## Deep Dive: Image Request

> **Interviewer**: "Расскажи про ImageRequest."
> **Candidate**: "ImageRequest инкапсулирует все параметры загрузки и целевой объект. API построен на fluent chaining -- цепочке вызовов."

```
ImageRequest:
  + load(source: Uri): ImageRequest
  + resize(width: Int, height: Int): ImageRequest
  + format(format: ImageFormat): ImageRequest
  + into(target: ImageView): ImageRequest
  + into(callback: (Image) -> Unit): ImageRequest
```

**Пример использования:**

```kotlin
imageLibrary
    .load("https://example.com/photo.jpg")
    .resize(200, 200)
    .format(ImageFormat.RGB_565)
    .into(avatarImageView)
```

> **Candidate**: "Для UI-targets мы регистрируем lifecycle callbacks. Когда ImageView открепляется от иерархии, становится невидимым, или переиспользуется в RecyclerView -- загрузка прерывается, ресурсы освобождаются."

```
UI Target Lifecycle:

  View attached     -> начать / возобновить загрузку
  View visible      -> продолжить загрузку
  View invisible    -> приостановить загрузку
  View detached     -> отменить загрузку, освободить ресурсы
  View recycled     -> отменить предыдущий запрос, начать новый
```

> **Candidate**: "Это критично для списков. Без lifecycle management при быстром скролле RecyclerView мы получим десятки конкурирующих загрузок для View, которые уже не видны. Это тратит bandwidth, CPU и может привести к отображению неправильного изображения в переиспользованном ViewHolder."

> **Связь**: утечки и lifecycle -- [[android-memory-leaks]], RecyclerView recycling -- [[android-recyclerview-internals]].

---

## Follow-up: Без HTTP Cache

> **Interviewer**: "Как изменится дизайн, если HTTP-клиент не поддерживает встроенное кэширование?"
> **Candidate**: "Тогда я реализую собственный disk cache."

```
+-------------------+     +-------------------+
|   Cache DB        |     |   Cache Directory  |
|   (metadata:      |     |   (image files:    |
|    key, path,     |<--->|    /cache/img_001  |
|    size, lastUsed)|     |    /cache/img_002) |
+-------------------+     +-------------------+
```

> **Candidate**: "Метаданные (ключ, путь к файлу, размер, дата последнего доступа) храню в реляционной БД (SQLite / Room). Сами изображения -- в internal cache directory."

> **Interviewer**: "Почему именно cache directory?"
> **Candidate**: "Три причины: 1) система может автоматически очищать эту директорию при нехватке места на устройстве, 2) содержимое не попадает в бэкапы приложения, 3) на Android internal storage не требует дополнительных permissions и обеспечивает приватность."

> **Candidate**: "Плюс я установлю лимит дискового пространства (например, 250 MB, как в Google Drive) и реализую LRU eviction: при превышении лимита удаляю записи с самым старым lastUsed."

---

## Follow-up: Чувствительные изображения

> **Interviewer**: "Что если нужно хранить чувствительные изображения?"
> **Candidate**: "Я добавлю флаг `sensitive` в ImageRequest. Для таких изображений:"
> **Candidate**: "Первый вариант -- шифрование файлов в disk cache. Ключи шифрования храним в Android Keystore / iOS Keychain. При чтении -- расшифровка перед декодированием."
> **Candidate**: "Второй вариант -- и он лучше -- вообще не кэшировать чувствительные изображения на диск. Только in-memory кэш, который очищается при уходе приложения в background. Меньше attack surface."

> **Interviewer**: "А что с memory dump?"
> **Candidate**: "На рутованном устройстве можно сделать дамп памяти процесса и извлечь Bitmap. Полная защита от этого невозможна на уровне библиотеки -- это ответственность OS и device security. Но мы можем минимизировать время жизни чувствительного изображения в памяти: не кэшировать, а после отображения сразу вызвать `bitmap.recycle()` и обнулить ссылку."

---

## Trade-offs

### Баланс ресурсов: Memory / Disk / CPU / Bandwidth

| Ресурс | Увеличить | Плюс | Минус |
|--------|-----------|------|-------|
| **Memory** | Больше кэш | Быстрый доступ, нет I/O | Риск OOM, система убьёт приложение в фоне |
| **Disk** | Больше кэш | Экономия трафика, offline | Износ flash, нагрев, удаление при low storage |
| **Bandwidth** | Всегда из сети | Свежие данные | Расход трафика пользователя, расход батареи |
| **CPU** | Декодирование на лету | Меньше памяти | Задержки UI, нагрев |

Лучшая стратегия -- сделать параметры конфигурируемыми и выбрать разумные defaults.

### Low Data Mode / Data Saver

Библиотека должна уважать системные настройки экономии трафика:

- **Блокировка загрузок** -- не скачивать изображения вообще (экстрим)
- **Приоритеты** -- загружать только критичные для UI (Quality of Service)
- **Качество** -- переключаться на low-quality версии (меньший размер, WebP вместо PNG)
- **Cache-first** -- предпочитать кэшированные данные, загружать из сети только при cache miss

### Зависимость от 3rd-party библиотек

| Подход | Плюс | Минус |
|--------|------|-------|
| Использовать OkHttp/URLSession cache | Быстрый time-to-market, проверенное решение | Version conflicts, лицензии, потеря контроля |
| Написать свой disk cache | Полный контроль, нет зависимостей | Время разработки, потенциальные баги |

Для MVP -- используй существующее. Для production-библиотеки с долгим lifecycle -- рассмотри собственную реализацию.

### Threading Model

Ещё один важный trade-off -- модель потоков. Загрузка, декодирование и доставка работают в разных контекстах:

```
Network Fetcher       -> IO dispatcher (сетевые операции)
File Fetcher          -> IO dispatcher (дисковые операции)
Image Decoder         -> Default dispatcher (CPU-bound)
Cache lookup          -> Main thread (быстрый LRU get)
Image Target delivery -> Main thread (UI update)
```

На Android можно использовать coroutines с `Dispatchers.IO` для загрузки и `Dispatchers.Main` для доставки. На iOS -- `URLSession` для сети и `DispatchQueue.main` для UI. Библиотека должна гарантировать, что callback для UI-target всегда вызывается на main thread, даже если клиент забудет об этом.

### Советы для интервью

- **Не стремись к идеалу** -- покажи "signal", что ты понимаешь trade-offs
- **Слушай интервьюера** -- он направляет дискуссию в нужную сторону
- **Покрывай ширину** -- лучше затронуть все компоненты поверхностно, чем один глубоко
- **Упоминай конкретные технологии** -- OkHttp, LruCache, BitmapPool, coroutines. Это показывает практический опыт

---

## Проверь себя

1. **Почему ImageKey включает размеры и формат, а не только URI?**
   Потому что одно изображение может запрашиваться в разных размерах (аватар 48dp vs превью 200dp) и форматах (RGBA_8888 vs RGB_565). Хранить масштабированные версии экономит память и ускоряет отрисовку.

2. **Зачем разделять Fetcher и Decoder в Image Loader?**
   Для соблюдения SRP и расширяемости через паттерн Strategy. Новый источник данных -- новый Fetcher. Новый формат -- новый Decoder. Остальной код не меняется.

3. **Как библиотека должна вести себя при быстром скролле RecyclerView?**
   Отменять загрузки для View, которые ушли за экран (detached/recycled), и начинать новые для видимых. Без этого -- лишний трафик, CPU, и риск показать неправильное изображение в переиспользованном ViewHolder.

4. **Почему 1/8 от maxMemory -- разумная эвристика для in-memory кэша?**
   Компромисс: достаточно для хранения нескольких десятков изображений, но не настолько много, чтобы вытеснить host-приложение из памяти. Дополнительно -- low-memory callbacks для аварийной очистки.

5. **В чём разница между internal cache directory и internal files directory для disk cache?**
   Cache directory может быть автоматически очищена системой при нехватке места и не включается в бэкапы. Files directory -- постоянное хранилище. Для кэша изображений cache directory предпочтительнее.

---

## Ключевые карточки

| # | Вопрос | Ответ |
|---|--------|-------|
| 1 | Из каких 5 компонентов состоит Image Library? | Image Request, Request Manager, Image Cache (LRU), Image Loader (Fetcher + Decoder), Image Target |
| 2 | Что такое ImageKey и зачем он нужен? | Составной ключ кэша: URI + width + height + format. Различает одно изображение в разных размерах/форматах |
| 3 | Как определить размер in-memory кэша? | Эвристика 1/8 от `maxMemory()` + low-memory callbacks для очистки |
| 4 | Зачем нужен BitmapPool? | Переиспользование аллоцированных Bitmap через `inBitmap` -- снижает давление на GC при скролле |
| 5 | Как реализовать disk cache без HTTP-клиента? | SQLite для метаданных (key, path, size, lastUsed) + файлы в internal cache directory + LRU eviction |
| 6 | Как обрабатывать sensitive images? | Лучший вариант -- не кэшировать на диск. Если нужно -- шифрование через Android Keystore / iOS Keychain |

---

## Куда дальше

| Направление | Материал |
|-------------|----------|
| Фреймворк для Mobile System Design | [[system-design-android]] |
| Стратегии кэширования (LRU, LFU, TTL) | [[caching-strategies]] |
| Как RecyclerView переиспользует View | [[android-recyclerview-internals]] |
| Утечки памяти и lifecycle | [[android-memory-leaks]] |
| Смежное упражнение: Caching Library | [[sd-exercise-caching-library]] |

---

## Источники

- [Mobile System Design: Image Library Exercise](https://github.com/iartr/mobile-system-design/blob/master/exercises/image-library.md) -- оригинальный walkthrough
- [Android: Caching Bitmaps](https://developer.android.com/topic/performance/graphics/cache-bitmap) -- Google рекомендации по кэшированию
- [Glide BitmapPool](https://github.com/bumptech/glide/blob/master/library/src/main/java/com/bumptech/glide/load/engine/bitmap_recycle/BitmapPool.java) -- реализация пула Bitmap
- [Coil Image Loader](https://coil-kt.github.io/coil/) -- современная Kotlin-first библиотека
- "Software Engineering at Google", Chapter 21: Dependency Management -- trade-offs зависимостей

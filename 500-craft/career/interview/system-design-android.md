---
title: "System Design для Android: думай как архитектор"
created: 2025-12-26
modified: 2026-02-13
type: deep-dive
status: published
confidence: high
tags:
  - topic/career
  - type/deep-dive
  - level/advanced
  - interview
related:
  - "[[interview-process]]"
  - "[[architecture-questions]]"
prerequisites:
  - "[[interview-process]]"
  - "[[architecture-questions]]"
reading_time: 14
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Mobile System Design: не код, а архитектурное мышление

"Android System Design Interview is not just about writing code — it's about thinking like a software architect." Mobile design отличается от backend: offline-режим, батарея, синхронизация, push-уведомления, ограниченная память. Интервьюер хочет увидеть, что ты можешь спроектировать feature для миллионов пользователей с учётом мобильной специфики.

---

## Теоретические основы

> **System Design Interview** — оценка способности кандидата проектировать масштабируемые системы: от requirements до architecture, с обсуждением trade-offs. Для mobile — это проектирование клиентской архитектуры с учётом offline, battery, sync и ограничений устройства.

**Mobile vs Backend System Design:**

| Аспект | Backend SD | Mobile SD |
|--------|-----------|-----------|
| Масштаб | Миллионы RPS, distributed systems | Один device, ограниченные ресурсы |
| Фокус | CAP theorem, sharding, load balancing | Offline-first, battery, UX responsiveness |
| Storage | Distributed databases, caching layers | Local DB (Room), disk cache, DataStore |
| Network | Reliable, high bandwidth | Unreliable, variable bandwidth, metered |
| Failure | Server redundancy, failover | Graceful degradation, retry, queue |

**Framework RESHADED** (weeeBox/mobile-system-design):
- **R**equirements — functional + non-functional
- **E**stimations — data size, bandwidth, storage
- **S**torage — local vs remote, caching strategy
- **H**igh-level design — architecture layers
- **A**PI design — endpoints, data models
- **D**eep dive — critical path, edge cases
- **E**rror handling — failure modes, recovery
- **D**iscussion — trade-offs, alternatives

Подход к mobile system design сформировался из backend-ориентированных frameworks (Xu, 2020) с адаптацией для мобильной специфики. Ключевое отличие: backend SD фокусируется на **throughput и availability** (CAP theorem, Brewer 2000), а mobile SD — на **user experience при ненадёжных условиях** (offline, slow network, low memory).

> **Принцип offline-first (Trello Engineering, 2017):** мобильное приложение должно быть полностью функциональным без сети, синхронизируя данные при появлении connectivity. Это инвертирует backend-парадигму, где network availability — данность.

→ Связано: [[interview-process]], [[architecture-questions]], [[sd-industry-resources]]

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Android Architecture** | MVI/MVVM, Clean Architecture | [[architecture-questions]] |
| **Networking basics** | REST, caching, sync | [[network-fundamentals-for-developers]] |
| **Storage** | Room, DataStore, File | Android docs |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Junior** | ⚠️ Читать | Понять, к чему готовиться |
| **Middle** | ✅ Да | Начни практиковать |
| **Senior** | ✅ Да | Основная аудитория |

### Терминология для новичков

> 💡 **Mobile System Design** = проектирование мобильного приложения для миллионов пользователей. Не код, а архитектура: как данные текут, как кэшируются, как синхронизируются.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **HLD** | High-Level Design — общая архитектура | **План города** — где что |
| **Deep Dive** | Детальный разбор компонента | **Чертёж здания** — каждый кирпич |
| **Trade-off** | Компромисс между подходами | **Или скорость, или качество** |
| **Offline-first** | Сначала работает без сети | **Локальный режим** |
| **Sync** | Синхронизация с сервером | **Обновить из облака** |
| **Caching** | Локальное хранение данных | **Запомнить, чтобы не спрашивать** |
| **UDF** | Unidirectional Data Flow | **Данные в одну сторону** |
| **Pagination** | Загрузка частями | **Страницы в книге** |
| **Optimistic Update** | Показать до подтверждения | **Сначала покажи, потом сохрани** |
| **Conflict Resolution** | Что делать при конфликте | **Кто главнее — сервер или клиент** |

---

## Терминология

| Термин | Что это |
|--------|---------|
| **High-level design** | Общая архитектура: слои, компоненты, data flow |
| **Deep dive** | Детальное проектирование одного компонента |
| **Trade-off** | Компромисс между двумя подходами |
| **UDF** | Unidirectional Data Flow — однонаправленный поток данных |

---

## Отличие от Backend System Design

```
Backend Design:
├── Масштабирование серверов
├── Базы данных, шардирование
├── Load balancing
├── Кэширование (Redis, CDN)
└── Микросервисы

Mobile Design:
├── Offline-first подход
├── Кэширование локально (Room, DataStore)
├── Синхронизация с сервером
├── Батарея и производительность
├── Push notifications
└── UI state management
```

Не проектируй backend на mobile-интервью. Фокус на клиентской части.

---

## Типичные задачи

| Задача | Ключевые аспекты |
|--------|------------------|
| Design Instagram Feed | Pagination, image caching, infinite scroll |
| Design Chat App | Real-time, offline messages, sync |
| Design Image Caching Library | Memory/disk cache, LRU, threading |
| Design Offline Note App | Local-first, conflict resolution, sync |
| Design Video Player | Streaming, caching, quality adaptation |
| Design E-commerce Page | Product list, cart, offline browse |

---

## Framework для ответа

### Timeline (45-60 минут)

```
0-10 мин:   Requirements Clarification
            → Functional requirements
            → Non-functional (offline, scale, performance)
            → Constraints и assumptions

10-25 мин:  High-Level Architecture
            → Диаграмма компонентов
            → Data flow
            → Ключевые решения

25-45 мин:  Deep Dive
            → Один компонент детально
            → Trade-offs
            → Edge cases

45-60 мин:  Discussion
            → Вопросы интервьюера
            → Альтернативные подходы
```

---

## Step 1: Requirements Clarification

**Не начинай рисовать, пока не понял задачу.**

### Вопросы для уточнения

```
Functional:
• Какие основные user flows?
• Какие данные отображаем?
• Какие действия пользователя?

Non-functional:
• Нужна ли offline-поддержка?
• Сколько пользователей/данных?
• Какие платформы (только Android)?
• Real-time требования?

Constraints:
• Низкоскоростной интернет?
• Low-end устройства?
• Battery considerations?
```

### Пример для Instagram Feed

```
Clarifying Questions:
1. "Should the feed work offline?" → Yes, cached posts
2. "How many posts to load initially?" → 20, then paginate
3. "Do we need real-time updates?" → No, pull-to-refresh
4. "Image quality requirements?" → Adaptive based on connection
5. "What data do we cache locally?" → Last 100 posts + images
```

---

## Step 2: High-Level Architecture

### Стандартная Mobile Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         UI LAYER                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   Screens (Composables/Fragments)                     │  │
│  │   ├── FeedScreen                                      │  │
│  │   ├── DetailScreen                                    │  │
│  │   └── ...                                             │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓ StateFlow                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   ViewModels (State Holders)                          │  │
│  │   ├── FeedViewModel                                   │  │
│  │   └── Handles UI state, user actions                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ Use Cases
┌─────────────────────────────────────────────────────────────┐
│                       DOMAIN LAYER                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   Use Cases / Interactors                             │  │
│  │   ├── GetFeedUseCase                                  │  │
│  │   ├── RefreshFeedUseCase                              │  │
│  │   └── Business logic, validation                      │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   Domain Models                                       │  │
│  │   └── Post, User, Comment (pure Kotlin)               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ Repository
┌─────────────────────────────────────────────────────────────┐
│                        DATA LAYER                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   Repository                                          │  │
│  │   ├── Single source of truth                          │  │
│  │   ├── Coordinates cache + network                     │  │
│  │   └── Exposes Flow<Data>                              │  │
│  └───────────────────────────────────────────────────────┘  │
│           ↓                               ↓                 │
│  ┌─────────────────┐           ┌─────────────────────────┐  │
│  │   Local Cache   │           │      Remote Source      │  │
│  │   ├── Room DB   │           │      ├── Retrofit       │  │
│  │   ├── DataStore │           │      ├── Ktor           │  │
│  │   └── Memory    │           │      └── WebSocket      │  │
│  └─────────────────┘           └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Ключевые компоненты

| Компонент | Ответственность |
|-----------|-----------------|
| **UI Layer** | Отображение state, обработка user input |
| **ViewModel** | Держит UI state, преобразует domain → UI |
| **Use Cases** | Бизнес-логика, координация data sources |
| **Repository** | Абстракция над источниками данных |
| **Local Cache** | Room для persistence, Memory для быстрого доступа |
| **Remote** | API calls, response parsing |

### Feature-модульная архитектура для интервью

На Senior+ интервью ожидают видение не только одной фичи, но и всего приложения. Feature-модульная архитектура — эффективный способ презентовать это за 5 минут.

```
App Module
├── :feature:feed/
│   ├── api/        → Публичный интерфейс (UseCase, Router)
│   ├── deps/       → Зависимости от других фич (только API)
│   ├── ui/         → Composables/Fragments + ViewModel
│   ├── domain/     → UseCases, Entities (чистая архитектура)
│   └── data/       → Repository, DataSource, Mappers
│
├── :feature:chat/
│   └── ... (та же структура)
│
├── :core:network/    → HTTP client, WebSocket, interceptors
├── :core:database/   → Room DB, migrations
├── :core:analytics/  → Tracking, A/B testing
├── :core:navigation/ → Deep links, routing
└── :core:auth/       → Tokens, session management
```

**Ключевые принципы:**
- **Feature API не навязывает фреймворки** — ни DI, ни MV*-паттерн, ни платформенные зависимости. В идеале чистый Kotlin/Swift
- **Фичи не связаны напрямую** — фича подключает только API другой фичи. Имплементации связываются только в App Module
- **Core modules не разделяются на api/impl** — авторизация, навигация, аналитика, сетевой слой

**Почему это работает на интервью:**
- Time management: рисуется быстро, сразу даёт темы для обсуждения
- Модульность: каждый компонент — потенциально отдельный Gradle-модуль
- Масштабируемость команды: разные команды работают над разными фичами
- Похоже на C4 model — знакомо интервьюерам с backend-опытом

> Подробнее: [[android-modularization]] — детальный разбор подходов к модуляризации

---

## Step 3: Deep Dive — примеры

### Пример 1: Offline-First Data Flow

```
User opens app
       ↓
ViewModel requests data
       ↓
Repository checks:
┌─────────────────────────────────────────┐
│ 1. Return cached data immediately       │
│    (show stale while fetching fresh)    │
│                                         │
│ 2. Fetch from network in background     │
│                                         │
│ 3. On success:                          │
│    └── Update cache                     │
│    └── Emit new data to UI              │
│                                         │
│ 4. On failure:                          │
│    └── Keep showing cached              │
│    └── Show error indicator             │
└─────────────────────────────────────────┘
```

```kotlin
// Repository implementation
fun getFeed(): Flow<Resource<List<Post>>> = flow {
    // 1. Emit cached first
    val cached = localDataSource.getFeed()
    if (cached.isNotEmpty()) {
        emit(Resource.Success(cached))
    }

    // 2. Fetch fresh
    try {
        val fresh = remoteDataSource.getFeed()
        localDataSource.saveFeed(fresh)
        emit(Resource.Success(fresh))
    } catch (e: Exception) {
        if (cached.isEmpty()) {
            emit(Resource.Error(e))
        }
        // else: keep showing cached, maybe show snackbar
    }
}
```

### Пример 2: Image Caching Strategy

```
Image Request Flow:

Request Image URL
       ↓
┌──────────────────┐
│  Memory Cache    │ ← LRU, ~50MB
│  (Bitmap)        │
└────────┬─────────┘
         │ miss
         ↓
┌──────────────────┐
│   Disk Cache     │ ← ~250MB
│   (File)         │
└────────┬─────────┘
         │ miss
         ↓
┌──────────────────┐
│    Network       │
│    Download      │
└────────┬─────────┘
         ↓
   Save to Disk
         ↓
   Save to Memory
         ↓
   Return Bitmap
```

**Trade-offs:**
- Memory cache: fast, but limited size
- Disk cache: slower, but persistent across sessions
- LRU eviction: remove least recently used when full

### Пример 3: Pagination

Три основных типа пагинации — выбор зависит от задачи:

| Тип | Механизм | Плюсы | Минусы | Когда использовать |
|-----|----------|-------|--------|-------------------|
| **Offset** | `?offset=20&limit=10` | Простота, можно прыгнуть на страницу N | Дубликаты/пропуски при изменении данных; медленный на больших offset | Статичные данные, каталоги |
| **Keyset** | `?after_id=123&limit=10` | Стабильный при вставках; быстрый на БД (index scan) | Нельзя прыгнуть на произвольную страницу | Хронологические данные, логи |
| **Cursor** | `?cursor=eyJpZCI6MTIzfQ&limit=10` | Opaque token — сервер контролирует формат; стабильный | Чёрный ящик для клиента; сложнее дебажить | Feed, timeline, chat history |

> **Для SD интервью:** Cursor-based — самый безопасный ответ для feed-подобных задач. Opaque cursor скрывает реализацию и позволяет серверу менять логику без изменения API.

```kotlin
// Cursor-based pagination с Paging 3
data class PagedResult<T>(
    val items: List<T>,
    val nextCursor: String?,  // null = последняя страница
    val hasMore: Boolean
)

class FeedPagingSource : PagingSource<String, Post>() {
    override suspend fun load(params: LoadParams<String>): LoadResult<String, Post> {
        return try {
            val cursor = params.key
            val response = api.getFeed(cursor, params.loadSize)

            LoadResult.Page(
                data = response.posts,
                prevKey = null,  // only forward pagination
                nextKey = response.nextCursor
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
}
```

### Пример 4: Resumable Uploads

Для загрузки больших файлов (видео, документы) — 3-фазный протокол:

```
Фаза 1: INIT
  POST /uploads/init
  Body: { filename, size, content_type }
  Response: { upload_id, chunk_size }

Фаза 2: APPEND (повторяется N раз)
  POST /uploads/{upload_id}/append
  Body: binary chunk
  Headers: Content-Range: bytes 0-1048575/5242880
  Response: { bytes_received }

Фаза 3: FINALIZE
  POST /uploads/{upload_id}/finalize
  Response: { file_url, file_id }
```

**Почему это важно на интервью:** при разрыве соединения клиент знает, сколько байт уже загружено, и продолжает с нужного offset. Без resumable upload пользователь теряет весь прогресс.

### Пример 5: Prefetching и QoS-приоритеты

Для оптимизации UX данные загружаются до того, как пользователь их запросит. Приоритеты загрузки (Quality of Service):

```
QoS Levels:
├── P0: User-critical    → Текущий экран (блокирует UI)
├── P1: UI-critical      → Следующий экран (prefetch)
├── P2: UI-non-critical  → Thumbnails за пределами viewport
└── P3: Background       → Analytics, sync, pre-cache
```

На медленных сетях или при low battery P2-P3 запросы откладываются или отменяются. Это позволяет гарантировать отзывчивость для P0-P1.

---

## Mobile-Specific Considerations

### 1. Offline Support

```
Strategies:
├── Cache-first: Show cached, update in background
├── Network-first: Try network, fallback to cache
└── Offline-only: Queue changes, sync when online

Sync Conflict Resolution:
├── Last-write-wins
├── Server-wins
├── Client-wins
└── Manual merge (show conflict to user)
```

### 2. Battery & Performance

```
Considerations:
├── Batch network requests
├── Use WorkManager for deferred work
├── Compress images before upload
├── Reduce polling frequency
└── Prefer push over poll
```

### 3. Real-Time Updates

Выбор протокола — один из ключевых trade-offs на SD-интервью.

| Протокол | Направление | Latency | Батарея | Сложность | Когда использовать |
|----------|------------|---------|---------|-----------|-------------------|
| **Push (FCM/APNs)** | Server → Client | Секунды | Низкий | Низкая | Уведомления, когда приложение в background |
| **Short Polling** | Client → Server | Высокая (интервал) | Высокий | Низкая | Fallback, простые системы |
| **Long Polling** | Client → Server | Средняя | Средний | Средняя | Когда WS/SSE недоступны |
| **SSE** | Server → Client | Низкая | Средний | Низкая | Feed updates, live scores, односторонние потоки |
| **WebSocket** | Bidirectional | Минимальная | Средний | Высокая | Chat, gaming, collaborative editing |

**Правило выбора для интервью:**
- Нужен bidirectional? → **WebSocket**
- Только server → client? → **SSE** (проще WS)
- Background delivery? → **Push (FCM)**
- Не уверен? → **Push + REST fallback** (самый безопасный дефолт)

```
Типичная комбинация для Chat App:
WebSocket → real-time сообщения (foreground)
+ FCM     → уведомления (background)
+ REST    → загрузка истории (pagination)
```

### 4. Security

```
Must mention:
├── HTTPS only
├── Certificate pinning
├── Token-based auth (refresh tokens)
├── Encrypt sensitive local data
└── Don't log sensitive info
```

---

## Типичные ошибки

```
❌ Начинать рисовать без requirements
   → Всегда уточни functional + non-functional

❌ Проектировать backend
   → Фокус на клиенте, API — чёрный ящик

❌ Игнорировать offline
   → Для mobile это критично

❌ Слишком глубоко в детали сразу
   → Сначала high-level, потом deep dive

❌ Не обсуждать trade-offs
   → Покажи, что понимаешь компромиссы
```

### Ошибки интервьюера (и как кандидату на них реагировать)

Полезно знать типичные ошибки с *другой стороны стола* — это поможет направить интервью в конструктивное русло.

| # | Ошибка интервьюера | Как реагировать кандидату |
|---|-------------------|--------------------------|
| 1 | **Не объясняет контекст задачи** | Задай 5-7 уточняющих вопросов самостоятельно — это покажет зрелость |
| 2 | **Настаивает на "правильном" решении** | Предложи свой вариант, объясни trade-offs, спроси "какие ограничения я упускаю?" |
| 3 | **Перебивает и уводит в сторону** | Мягко верни к структуре: "Давайте я покажу HLD, а потом углубимся" |
| 4 | **Оценивает по шаблону из учебника** | Покажи, что знаешь "каноничный" ответ, но объясни, почему твой вариант лучше для данного контекста |
| 5 | **Фокусируется только на backend** | Перенаправь на клиент: "На мобильном интервью ключевое — offline, sync и UI state" |
| 6 | **Спрашивает слишком узко для уровня** | Ответь на вопрос и расширь: "Это решает X, но для полной картины важно ещё Y и Z" |
| 7 | **Не даёт feedback по ходу** | Проси: "Хотите, чтобы я углубился сюда, или перейдём к другому компоненту?" |
| 8 | **Сравнивает с собственным проектом** | Интересуйся: "Расскажите подробнее о ваших constraints — я адаптирую решение" |
| 9 | **Оценивает объём знаний, а не мышление** | Демонстрируй рассуждение вслух: "Я не работал с X, но исходя из принципов Y, я бы сделал так..." |

> **Ключевой совет:** На хорошем SD интервью 60% говорит кандидат, 40% — интервьюер. Если ты чувствуешь, что только отвечаешь на вопросы — бери инициативу и веди discussion.

---

## Как оценивают

| Критерий | Что смотрят |
|----------|-------------|
| Requirement gathering | Задаёшь правильные вопросы |
| High-level thinking | Видишь систему целиком |
| Technical depth | Можешь углубиться в детали |
| Mobile awareness | Знаешь специфику платформы |
| Trade-off discussion | Понимаешь плюсы/минусы решений |
| Communication | Объясняешь понятно |

---

## Ожидания по уровням

Глубина и фокус System Design интервью зависят от целевого уровня кандидата.

### Junior (L3-L4)

Для джунов SD интервью необязательно. Если проводится — фокус на конкретном компоненте:
- Спроектировать экран с использованием библиотечных средств
- Базовое понимание MV*-паттернов
- Знание lifecycle, основ работы с сетью
- Допустимо не знать trade-offs на глубоком уровне

### Middle (L4-L5)

Интервью сложнее с точки зрения реализации. Кандидат и интервьюер обсуждают создание конкретного компонента:
- Несколько компонентов и их взаимодействие
- Выбор технического стека с обоснованием
- Понимание trade-offs на базовом уровне
- Типичная задача: "Design Instagram Feed"

### Senior (L5-L6)

Более высокоуровневое обсуждение. Детали реализации менее важны, если не влияют критически на производительность:
- Многомодульная архитектура, взаимодействие между компонентами
- Выбор протоколов, стратегий кэширования, sync с обоснованием
- Производительность, battery, security considerations
- Способность "вести" discussion, а не ждать вопросов
- Типичная задача: "Design WhatsApp Messenger"

### Staff (L6+)

Переход от технических решений к стратегическим:
- Целевая аудитория, доступные человеческие и вычислительные ресурсы
- Time-to-market, feature flags, поэтапные rollout'ы
- Privacy и юридические последствия (GDPR, data retention)
- Крупномасштабные отказы: как система деградирует gracefully
- Cross-team implications, долгосрочная поддержка
- Типичная задача: "Design Live-Streaming Platform"

---

## Ресурсы

| Ресурс | Описание |
|--------|----------|
| [Mobile System Design (GitHub)](https://github.com/weeeBox/mobile-system-design) | Framework + примеры |
| Mobile System Design Interview (книга) | Manuel Vivo, детальные разборы |
| [ProAndroidDev Articles](https://proandroiddev.com) | Android-specific design |

---

## Куда дальше

→ [[interview-process]] — общий процесс
→ [[architecture-questions]] — вопросы по архитектуре
→ [[coding-challenges]] — coding rounds

---

## Связь с другими темами

- [[interview-process]] — System Design — обязательный раунд для Senior+ в onsite loop. Текущий материал даёт framework и примеры для этого раунда, а interview-process объясняет его место в общем процессе: обычно Round 3, после coding. Слабый System Design = downlevel с L6 на L5, даже если coding прошёл отлично.

- [[architecture-questions]] — Содержит конкретные вопросы по архитектуре Android: MVVM vs MVI trade-offs, Clean Architecture layers, modularization patterns. Текущий материал использует эти архитектурные паттерны как строительные блоки для System Design ответов. Architecture — фундамент, System Design — применение этого фундамента к реальным задачам.

## Источники

### Теоретические основы

- Xu A. (2020). *System Design Interview*. — Backend-ориентированный framework, адаптируемый для mobile: Requirements → Estimations → Design → Deep Dive → Trade-offs.

- Brewer E. (2000). *Towards Robust Distributed Systems* (CAP Theorem). — Теоретическая основа trade-offs между consistency и availability; в mobile SD — offline-first vs data freshness.

- McDowell G. L. (2015). *Cracking the Coding Interview*. — Базовые концепции System Design: scalability, load balancing, database design.

- Larson W. (2022). *Staff Engineer*. — Staff-level expectations: leadership в design discussion, бизнес-контекст trade-offs.

### Практические руководства

- [GitHub: weeeBox/mobile-system-design](https://github.com/weeeBox/mobile-system-design)
- [ProAndroidDev: System Design Questions](https://proandroiddev.com/android-system-design-interview-questions-and-answer-f47ba3ebeb91)
- [The Mobile Interview](https://themobileinterview.com/cracking-the-mobile-system-design-interview/)

---

## Проверь себя

> [!question]- Почему Mobile System Design отличается от Backend System Design и какие mobile-specific аспекты интервьюер ожидает услышать?
> Mobile-specific: offline support (данные доступны без сети), battery optimization (background work vs freshness), network handling (slow, unreliable connections), local storage (Room, caching strategy), sync mechanism (conflict resolution). Backend фокус: scalability, throughput, CAP theorem. Mobile SD = Client + API, иногда + Backend, но клиентская сторона -- core.

> [!question]- Тебя попросили спроектировать Instagram Feed. Как ты структурируешь 45-минутный ответ?
> Requirements (5 мин): functional (infinite scroll, image loading, likes) + non-functional (offline, performance, scale). High-Level Design (10 мин): UI Layer (Compose, LazyColumn) -- Domain Layer (UseCases) -- Data Layer (Repository, Remote + Local). Deep Dive (25 мин): API pagination (cursor-based), image caching (memory + disk), offline support (Room), state management (MVI). Trade-offs (5 мин): freshness vs battery, cache size vs storage.

> [!question]- Какой framework для Mobile System Design ты используешь и почему RESHADED адаптирован для mobile?
> RESHADED: Requirements, Estimations, Storage Schema, High-Level Design, API Design, Detailed Design, Evaluate, Distinctive Additions. Для mobile адаптация: Storage = local DB + cache strategy, API = pagination + retry, Detailed = offline sync + state management, Evaluate = battery vs freshness trade-offs, Distinctive = push notifications, deep linking, security.

---

## Ключевые карточки

Mobile System Design Framework -- этапы?
?
1) Requirements (5 мин): functional + non-functional + scope (client/full-stack). 2) High-Level Design (10 мин): architecture diagram, components, data flow. 3) Deep Dive (25 мин): API, storage, networking, state management. 4) Trade-offs (10 мин): offline, errors, performance, security.

Mobile vs Backend SD -- ключевые различия?
?
Mobile: offline support, battery optimization, UI performance, local storage, sync. Backend: scalability, throughput, consistency vs availability. Mobile patterns: MVVM/MVI, Repository, Pagination. Backend: Microservices, queues, sharding.

Популярные Mobile SD задачи?
?
Design Instagram Feed (pagination, image caching, offline). Design Chat App (WebSocket, local storage, delivery). Design Uber Driver App (location, background, battery). Design Offline-first App (sync, conflict resolution, CRDT). Design Twitter Timeline (real-time updates, push vs pull).

Offline-first architecture -- ключевые компоненты?
?
Local DB (Room/SQLDelight) как source of truth. Sync queue для pending changes. Conflict resolution strategy (last-write-wins, merge, CRDT). Network observer для retry. Optimistic UI updates. Background sync (WorkManager).

---

## Куда дальше

| Направление | Тема | Ссылка |
|------------|------|--------|
| Следующий шаг | Architecture patterns для Android | [[android-architecture-patterns]] |
| Углубиться | Staff+ Engineering и SD интервью | [[staff-plus-engineering]] |
| Смежная тема | Распределённые системы для общего SD | [[architecture-distributed-systems]] |
| Обзор | Полный процесс интервью | [[interview-process]] |

---

*Обновлено: 2026-02-13*

---

*Проверено: 2026-02-13*

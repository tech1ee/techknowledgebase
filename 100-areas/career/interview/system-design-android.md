---
title: "System Design для Android: думай как архитектор"
created: 2025-12-26
modified: 2025-12-26
type: deep-dive
status: published
confidence: high
tags:
  - topic/career
  - topic/interview
  - topic/architecture
  - level/senior
related:
  - "[[interview-process]]"
  - "[[architecture-questions]]"
---

# Mobile System Design: не код, а архитектурное мышление

"Android System Design Interview is not just about writing code — it's about thinking like a software architect." Mobile design отличается от backend: offline-режим, батарея, синхронизация, push-уведомления, ограниченная память. Интервьюер хочет увидеть, что ты можешь спроектировать feature для миллионов пользователей с учётом мобильной специфики.

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

```kotlin
// Cursor-based pagination
data class PagedResult<T>(
    val items: List<T>,
    val nextCursor: String?,  // null if no more pages
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

```
Options:
├── WebSocket (bidirectional, persistent connection)
├── SSE (server-sent events, unidirectional)
├── FCM (push notifications)
└── Polling (fallback, battery-heavy)

For Chat App:
WebSocket for messages
+ FCM for notifications when app is background
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

## Источники

- [GitHub: weeeBox/mobile-system-design](https://github.com/weeeBox/mobile-system-design)
- [ProAndroidDev: System Design Questions](https://proandroiddev.com/android-system-design-interview-questions-and-answer-f47ba3ebeb91)
- [The Mobile Interview](https://themobileinterview.com/cracking-the-mobile-system-design-interview/)

---

*Обновлено: 2025-12-26*

---

*Проверено: 2026-01-09*

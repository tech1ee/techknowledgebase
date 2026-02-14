---
title: "SD Exercise: Chat Application"
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
  - "[[android-networking]]"
  - "[[android-room-deep-dive]]"
  - "[[android-background-work]]"
prerequisites:
  - "[[system-design-android]]"
reading_time: 20
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# SD Exercise: Chat Application (мессенджер)

Мессенджер — одна из самых популярных задач на Mobile System Design интервью. Эта задача проверяет умение кандидата работать с real-time коммуникацией, offline-поддержкой, push-уведомлениями, вложениями и сложными статусными моделями. По сути, это "Hello World" для system design: если ты можешь спроектировать мессенджер — ты понимаешь мобильную архитектуру.

**Формат этого материала** — симуляция реального интервью в диалоговой форме. Candidate задаёт уточняющие вопросы, Interviewer направляет и ограничивает scope. Такой формат помогает не просто запомнить решение, а понять *процесс* рассуждений на интервью.

> Рекомендуется сначала пройти [[system-design-android]] — там описан общий фреймворк для Mobile System Design интервью.

---

## Задача — "Design Chat Application"

> **Interviewer**: Design a chat application similar to WhatsApp. Focus on the mobile client.

Задача намеренно размыта — и это не случайно. Интервьюер хочет увидеть, как ты структурируешь неопределённость. Первый шаг — *не бросаться рисовать*, а задать правильные вопросы. Именно фаза сбора требований показывает зрелость кандидата: junior сразу начинает рисовать компоненты, senior — задаёт 5-10 уточняющих вопросов.

> Типичная ошибка: потратить 30 минут из 45 на детальную проработку одного компонента, не показав общую картину. Правильный тайминг: 5 мин требования, 10 мин HLD, 25 мин deep dives, 5 мин trade-offs.

---

## Сбор требований

### Уточнение scope

> **Candidate**: Спасибо за задачу. Прежде чем проектировать, хочу уточнить контекст. Какой целевой рынок и масштаб? Миллион MAU или сотни миллионов?

> **Interviewer**: Целевой рынок — Северная Америка, около 1 миллиона MAU. Не нужно оптимизировать для масштабов WhatsApp.

> **Candidate**: Какие платформы нужно поддерживать? Только Android или также iOS и Web?

> **Interviewer**: Сосредоточься на Android-клиенте. Backend считай готовым — проектируй API контракты, но не серверную инфраструктуру.

> **Candidate**: Понял. А какие типы чатов в scope? Групповые, каналы, 1-on-1?

> **Interviewer**: Только 1-on-1 чаты. Групповые — out of scope.

### Функциональные требования

> **Candidate**: Хорошо, давай зафиксируем функциональные требования, как я их понял:

| # | Требование | Описание |
|---|-----------|----------|
| FR-1 | Список чатов | Отображение недавних чатов, отсортированных по дате последнего сообщения |
| FR-2 | 1-on-1 чат | Отправка и получение текстовых сообщений в реальном времени |
| FR-3 | Фото-вложения | Прикрепление фотографий к сообщениям (из галереи и камеры) |
| FR-4 | Статусы сообщений | Отображение статуса: отправляется, отправлено, доставлено, прочитано, ошибка |

> **Interviewer**: Да, всё верно. Добавлю, что read receipts — важная часть.

### Нефункциональные требования

> **Candidate**: Теперь по нефункциональным требованиям. Я бы выделил три ключевых:

| NFR | Требование | Обоснование |
|-----|-----------|-------------|
| NFR-1 | **Offline-доступ** | Пользователь должен читать историю чатов без сети |
| NFR-2 | **Безопасное хранение** | Локальная база зашифрована (чаты — чувствительные данные) |
| NFR-3 | **Real-time доставка** | Сообщения появляются мгновенно, без ручного обновления |

> **Interviewer**: Отлично. Продолжай.

### Что за пределами scope

> **Candidate**: Чтобы уложиться в 45 минут, я явно исключаю:

- Видео/аудио вложения и звонки
- Авторизация / регистрация
- Редактирование и удаление сообщений
- Групповые чаты и каналы
- Поиск по сообщениям
- Пересылка сообщений

> **Interviewer**: Согласен. Переходи к архитектуре.

---

## High-Level Architecture

> **Candidate**: Начну с общей схемы. Я разделяю систему на серверную и клиентскую часть. На клиенте использую MVx + Repository + Coordinator паттерны.

```
┌─────────────────────────────────────────────────────────────┐
│                      SERVER SIDE                            │
│                                                             │
│  ┌──────────┐    ┌───────────────┐    ┌──────────┐         │
│  │ Backend  │    │ Push Provider │    │   CDN    │         │
│  │ (API +   │    │ (FCM / APNs) │    │ (images) │         │
│  │  WS hub) │    └───────┬───────┘    └────┬─────┘         │
│  └────┬─────┘            │                 │               │
│       │                  │                 │               │
└───────┼──────────────────┼─────────────────┼───────────────┘
        │ REST + WS        │ Push            │ HTTPS
┌───────┼──────────────────┼─────────────────┼───────────────┐
│       ▼                  ▼                 ▼               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   API Service                       │   │
│  │  (WebSocket + REST client + Push handler)           │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                    │
│  ┌────────────────────▼────────────────────────────────┐   │
│  │                  Repository                         │   │
│  │  (единый медиатор между сетью и хранилищем)         │   │
│  └───────┬──────────────────────────┬──────────────────┘   │
│          │                          │                      │
│          ▼                          ▼                      │
│  ┌──────────────┐          ┌──────────────────┐            │
│  │ Persistence  │          │  Image Loader    │            │
│  │ (Room + enc) │          │  (Coil/Glide)    │            │
│  └──────────────┘          └──────────────────┘            │
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ Chat Lobby  │  │ Chat Room   │  │  Attachment      │   │
│  │ (список)    │  │ (диалог)    │  │  Provider        │   │
│  └──────┬──────┘  └──────┬──────┘  │  (камера/        │   │
│         │                │         │   галерея)        │   │
│         │                │         └──────────────────┘   │
│         └────────┬───────┘                                 │
│                  ▼                                          │
│  ┌──────────────────────────────────┐                      │
│  │          Coordinator             │                      │
│  │  (навигация Lobby <-> Room)      │                      │
│  └──────────────────────────────────┘                      │
│                                                            │
│  ┌──────────────────────────────────┐                      │
│  │      DI Graph (Hilt/Koin)        │                      │
│  └──────────────────────────────────┘                      │
│                   CLIENT SIDE                              │
└────────────────────────────────────────────────────────────┘
```

### Описание компонентов

| Компонент | Ответственность |
|-----------|----------------|
| **Backend** | Серверная инфраструктура: REST API, WebSocket hub, БД, очереди сообщений |
| **Push Provider** | FCM (Android) — доставка push-уведомлений, когда приложение в фоне |
| **CDN** | Раздача статики: фото-вложения, аватары, thumbnails |
| **API Service** | Абстракция над тремя каналами связи (WS, REST, Push). Клиент не знает деталей транспорта |
| **Persistence** | Единый источник истины на клиенте. Room DB с шифрованием (SQLCipher). Подробнее: [[android-room-deep-dive]] |
| **Repository** | Медиатор между API Service и Persistence. Реализует offline-first стратегию: читай из кэша, обновляй из сети. См. [[caching-strategies]] |
| **Chat Lobby** | UI-слой для списка чатов: ViewModel + LazyColumn/RecyclerView |
| **Chat Room** | UI-слой для конкретного диалога: ViewModel + список сообщений |
| **Image Loader** | Coil или Glide — загрузка, кэширование, отображение изображений |
| **Attachment Provider** | Доступ к камере и галерее через ActivityResult API |
| **Coordinator** | Управление навигацией между экранами (Lobby -> Room -> обратно) |
| **DI Graph** | Граф зависимостей: Hilt или Koin |

> **Interviewer**: Хорошая схема. Давай углубимся в API Service — как именно устроена коммуникация с сервером?

### Data Flow: отправка сообщения

Чтобы понять, как компоненты взаимодействуют, проследим путь одного сообщения:

```
Пользователь нажимает "Отправить"
         │
         ▼
  ChatRoom ViewModel
  ── создаёт ChatMessage(status=PENDING, id=UUID)
         │
         ├──► Repository.sendMessage()
         │         │
         │         ├──► Persistence: INSERT message (PENDING)
         │         │         │
         │         │         └──► UI обновляется через Flow
         │         │              (сообщение появляется мгновенно)
         │         │
         │         └──► API Service: WS send MSG_OUT
         │                   │
         │              ┌────┴────┐
         │              ▼         ▼
         │           SUCCESS    FAILURE
         │              │         │
         │              ▼         ▼
         │     UPDATE status   UPDATE status
         │     = SENT          = FAILED
         │              │         │
         │              ▼         ▼
         │         UI: галочка  UI: красный
         │         "sent"      значок + retry
         │
         └──► (позже) WS получает MSG_READ
                      │
                      ▼
              UPDATE status = READ
                      │
                      ▼
              UI: двойная галочка
```

Этот flow демонстрирует принцип **optimistic update**: пользователь видит результат мгновенно, а подтверждение приходит асинхронно. Если сеть недоступна, сообщение остаётся в `PENDING` и будет отправлено при восстановлении соединения.

---

## Deep Dive: API Service

> **Candidate**: API Service — это, пожалуй, самый сложный компонент в этой задаче. Я разделяю его на три коммуникационных слоя, каждый для своей задачи.

### Слой 1: Bi-directional (WebSocket)

> **Candidate**: Для real-time обмена сообщениями использую WebSocket. Это постоянное двунаправленное соединение, которое позволяет серверу push-ить сообщения без polling.

**Формат фрейма:**

```json
{
  "connection_id": "uuid-string",
  "event_type": "HELLO | MSG_IN | MSG_OUT | MSG_READ | BYE",
  "payload": { ... }
}
```

**Таблица событий:**

| Событие | Направление | Назначение |
|---------|-------------|------------|
| `HELLO` | Client -> Server -> Client | Инициализация сессии. Клиент отправляет, сервер подтверждает и возвращает `connection_id` |
| `MSG_OUT` | Client -> Server | Клиент отправляет сообщение. Payload содержит `text`, `chat_id`, `local_id`, `attachments` |
| `MSG_IN` | Server -> Client | Сервер доставляет входящее сообщение от собеседника |
| `MSG_READ` | Bi-directional | Подтверждение прочтения. Содержит `message_id` и `chat_id` |
| `BYE` | Client -> Server | Клиент закрывает сессию (app в background или logout) |

> **Interviewer**: Что произойдёт, если WebSocket-соединение разорвётся?

> **Candidate**: Отличный вопрос. При разрыве соединения:
> 1. Клиент пытается реконнект с exponential backoff (1s, 2s, 4s, 8s, max 30s)
> 2. При переподключении отправляет `HELLO` с последним известным `connection_id` — сервер может доставить пропущенные сообщения
> 3. Если WS недоступен долго — fallback на REST polling + push notifications
>
> Подробнее о работе с сетью: [[android-networking]]

### Слой 2: HTTP-based (REST)

> **Candidate**: REST используется для операций, где real-time не нужен: начальная загрузка данных, пагинация истории.

**Эндпоинты:**

| Метод | Endpoint | Описание |
|-------|---------|----------|
| `GET` | `/login` | Инициализация сессии, возвращает JWT |
| `GET` | `/chats?after_id=<X>&limit=<Y>` | Пагинированный список чатов (cursor-based) |
| `GET` | `/chats/<chat_id>/messages?after_id=<X>&limit=<Y>` | Пагинированная история сообщений |

**Cursor-based пагинация** (а не offset-based) выбрана намеренно:
- Не ломается при вставке новых элементов
- Стабильная производительность на больших объёмах
- `after_id` указывает на последний загруженный элемент

**Обработка HTTP-ошибок:**

| Код | Значение | Действие клиента |
|-----|---------|------------------|
| `401` | Unauthorized | Перезапросить токен или разлогинить |
| `422` | Unprocessable Entity | Ошибка в запросе — показать пользователю |
| `429` | Too Many Requests | Rate limit — подождать и повторить |
| `500` | Internal Server Error | Exponential backoff с повтором |

### Слой 3: Cloud Messaging (Push)

> **Candidate**: Когда приложение в фоне или убито системой, новые сообщения приходят через FCM push.

**Payload push-уведомления:**

```json
{
  "user_id": "sender-uuid",
  "messages": [
    {
      "user_name": "Алексей",
      "text": "Привет! Как дела?",
      "created_at": "2026-02-14T10:30:00Z"
    }
  ]
}
```

> **Candidate**: Push используется как *сигнал*, а не как транспорт данных. При получении push:
> 1. Показываем notification с preview текста
> 2. При открытии приложения — полная синхронизация через REST/WS
> 3. Push не содержит полную модель сообщения (ни attachments, ни статусы)
>
> Подробнее: [[android-notifications]] и [[android-background-work]]

### Диаграмма API Service

```
┌─────────────────────────────────────────────────┐
│                  API Service                    │
│                                                 │
│  ┌─────────────┐ ┌──────────┐ ┌─────────────┐  │
│  │  WebSocket  │ │   REST   │ │    Push     │  │
│  │  Client     │ │  Client  │ │   Handler   │  │
│  │             │ │ (Retrofit│ │  (FCM Svc)  │  │
│  │ (OkHttp WS)│ │  + Ktor) │ │             │  │
│  └──────┬──────┘ └────┬─────┘ └──────┬──────┘  │
│         │             │              │          │
│         ▼             ▼              ▼          │
│  ┌─────────────────────────────────────────┐    │
│  │         Model Converter Layer           │    │
│  │  (Network DTO -> Domain Model)          │    │
│  └─────────────────────┬───────────────────┘    │
│                        │                        │
│  ┌─────────────────────▼───────────────────┐    │
│  │     ChatLobbyService + ChatRoomService  │    │
│  │     (единый интерфейс для Repository)   │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### Интерфейсы сервисов

```kotlin
interface ChatLobbyService {
    /** Подписка на обновления списка чатов (WS events) */
    fun observeChatUpdates(): Flow<ChatUpdate>

    /** Пагинированная загрузка чатов (REST) */
    suspend fun getChats(afterId: String?, limit: Int): List<ChatInfo>
}

interface ChatRoomService {
    /** Подписка на сообщения конкретного чата (WS events) */
    fun observeMessages(chatId: String): Flow<MessageEvent>

    /** Пагинированная история (REST) */
    suspend fun getMessages(chatId: String, afterId: String?, limit: Int): List<ChatMessage>

    /** Отправка сообщения (WS) */
    suspend fun sendMessage(chatId: String, text: String, attachments: List<String>): ChatMessage

    /** Подтверждение прочтения (WS) */
    suspend fun markAsRead(chatId: String, messageId: String)
}
```

**Model Converter Layer** отвечает за преобразование сетевых DTO в доменные модели. Это критически важный слой — он изолирует бизнес-логику от формата данных сервера. Если backend завтра изменит формат JSON, нужно поправить только converter, а не каждый ViewModel.

> **Interviewer**: Почему бы не использовать одну модель для сети и для UI?

> **Candidate**: Это частая ошибка. Сетевая модель привязана к API-контракту (snake_case, строковые enum, unix timestamps), а доменная — к бизнес-логике (camelCase, типизированные enum, `Date`). Смешивание приводит к протечке абстракций: изменение API ломает UI. Separation of concerns — один из ключевых принципов, которые интервьюер ожидает увидеть.

```kotlin
// Сетевая модель (DTO)
data class ChatMessageData(
    val id: String,
    val user_id: String,
    val text: String,
    val status: String,          // строка
    val created_at: Long,        // unix timestamp
    val attachments: String      // comma-separated IDs
)

// Доменная модель
data class ChatMessage(
    val id: String,
    val userId: String,
    val text: String,
    val status: ChatMessageStatus,  // enum
    val createdAt: Date,            // типизированная дата
    val attachments: List<Attachment>
)
```

---

## Deep Dive: Data Model

> **Interviewer**: Давай детально разберём, как хранить данные локально.

> **Candidate**: Использую Room с четырьмя таблицами. Основной принцип: **Persistence — единственный источник истины**. UI подписан на Room через Flow, сеть пишет в Room, UI автоматически обновляется.

### Схема базы данных

```
┌──────────────┐       ┌──────────────────────┐
│    User      │       │        Chat          │
├──────────────┤       ├──────────────────────┤
│ id (PK)      │◄──┐   │ chat_id (PK)         │
│ name         │   │   │ last_user_id (FK)    │──► User
│ profile_url  │   │   │ last_message_id (FK) │──► Message
└──────────────┘   │   │ updated_at           │
                   │   └──────────────────────┘
                   │
┌──────────────────┼───────────────────────┐
│             Message                      │
├──────────────────────────────────────────┤
│ message_id (PK)                          │
│ user_id (FK) ────────────────────────────┼──► User
│ chat_id (FK) ────────────────────────────┼──► Chat
│ text                                     │
│ status (PENDING | SENT | READ | FAILED)  │
│ created_at                               │
└──────────────────┬───────────────────────┘
                   │ 1:N
┌──────────────────▼───────────────────────┐
│            Attachment                    │
├──────────────────────────────────────────┤
│ attachment_id (PK)                       │
│ message_id (FK)                          │
│ full_size_url (nullable)                 │
│ thumbnail_url (nullable)                 │
│ local_path (nullable)                    │
│ status (READY|UPLOADING|DOWNLOADING|FAIL)│
│ file_size                                │
│ progress_size                            │
└──────────────────────────────────────────┘
```

### ChatInfo — модель для списка чатов

Для отображения Chat Lobby не нужно загружать все сообщения. Создаём агрегированную модель:

```kotlin
data class ChatInfo(
    val chatId: String,
    val lastUsername: String,
    val lastUserProfileUrl: String,
    val lastMessageText: String,
    val lastMessageTimestamp: Date,
    val unreadCount: Int
)
```

Room позволяет получить эту модель одним `@Query` с JOIN:

```kotlin
@Dao
interface ChatDao {
    @Query("""
        SELECT c.chat_id AS chatId,
               u.name AS lastUsername,
               u.profile_url AS lastUserProfileUrl,
               m.text AS lastMessageText,
               m.created_at AS lastMessageTimestamp,
               (SELECT COUNT(*) FROM Message
                WHERE chat_id = c.chat_id AND status != 'READ') AS unreadCount
        FROM Chat c
        JOIN User u ON c.last_user_id = u.id
        JOIN Message m ON c.last_message_id = m.message_id
        ORDER BY m.created_at DESC
    """)
    fun observeChats(): Flow<List<ChatInfo>>
}
```

Этот запрос выполняется на стороне SQLite и возвращает реактивный `Flow`. При любом изменении в таблицах Chat, User или Message — Room автоматически re-emit-ит данные. Подробнее о Room-запросах и оптимизации: [[android-room-deep-dive]].

### Локальные ID vs серверные ID

> **Interviewer**: Как идентифицировать сообщения — сервер генерирует ID или клиент?

> **Candidate**: Это классический trade-off. Я предлагаю **клиент генерирует UUID**, и вот почему:

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Клиентский UUID** | Идемпотентность: повторная отправка не создаст дубликат. Можно сохранить в Room сразу, до ответа сервера | UUID можно подделать. Теоретический риск коллизии (практически нулевой) |
| **Серверный ID** | Гарантированная уникальность. Сервер контролирует пространство ID | Нужен mapping local_id <-> server_id. Нельзя сохранить в Room до ответа сервера |

> **Candidate**: UUID v4 даёт нам немедленную запись в локальную БД со статусом `PENDING`, мгновенный feedback пользователю и защиту от дубликатов при retry. Сервер принимает клиентский UUID и использует его как primary key (или дедуплицирует по нему).

> **Interviewer**: А если злоумышленник сгенерирует UUID, совпадающий с чужим сообщением?

> **Candidate**: Хорошее замечание. Защита на стороне сервера: при получении `MSG_OUT` сервер проверяет, что `user_id` отправителя совпадает с владельцем сессии. Если UUID уже существует, но принадлежит другому пользователю — сервер отклоняет сообщение с ошибкой. Таким образом, collision-атака не позволит перезаписать чужие сообщения.

---

## Deep Dive: Attachments

> **Interviewer**: Расскажи подробнее про работу с фото-вложениями.

> **Candidate**: Вложения — самая технически сложная часть мессенджера. Нужно обработать как исходящие (upload), так и входящие (download) файлы.

### Жизненный цикл вложения

```
ИСХОДЯЩЕЕ (Upload):                    ВХОДЯЩЕЕ (Download):

  Пользователь выбирает фото            Получено WS-событие MSG_IN
           │                                      │
           ▼                                      ▼
  Сохранить в Room                       Сохранить metadata в Room
  status = UPLOADING                     status = DOWNLOADING
  local_path = /cache/img_01.jpg         full_size_url = https://cdn/...
  full_size_url = NULL                   local_path = NULL
           │                                      │
           ▼                                      ▼
  Upload в CDN (multipart)               Download из CDN
  Обновлять progress_size                Обновлять progress_size
           │                                      │
       ┌───┴───┐                              ┌───┴───┐
       ▼       ▼                              ▼       ▼
    SUCCESS  FAILED                        SUCCESS  FAILED
       │       │                              │       │
       ▼       ▼                              ▼       ▼
  status =  status =                    status =  status =
  READY     FAILED                      READY     FAILED
  url =     (retry                      local_ =  (retry
  cdn/...   button)                     /cache/   button)
```

### Различение входящих и исходящих

> **Candidate**: Определяю направление по полю `full_size_url`:
> - `full_size_url == NULL` -> это исходящее вложение (ещё не загружено на CDN)
> - `full_size_url != NULL` -> это входящее или уже загруженное вложение
>
> Это элегантное решение, которое не требует отдельного поля `direction`.

### Автозагрузка

> **Candidate**: Для удобства пользователя — автоматически скачиваем входящие фото при Wi-Fi. На мобильных данных показываем placeholder с кнопкой "Скачать".

```kotlin
class AttachmentDownloadPolicy(
    private val connectivityManager: ConnectivityManager
) {
    fun shouldAutoDownload(): Boolean {
        val network = connectivityManager.activeNetwork
        val caps = connectivityManager.getNetworkCapabilities(network)
        return caps?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true
    }
}
```

### Ограничение параллельных операций

> **Candidate**: Upload/download вложений управляется через TaskDispatcher с ограничением параллельности (например, max 3 одновременных операции). Это предотвращает перегрузку сети и экономит батарею. Для фоновой загрузки используется WorkManager — подробнее в [[android-background-work]].

### Resumable uploads

> **Candidate**: Для больших файлов важна возможность возобновления загрузки. В таблице Attachment есть поля `file_size` и `progress_size`. При сбое сети:
> 1. Клиент запоминает `progress_size` (сколько байт уже загружено)
> 2. При retry отправляет `Content-Range` header с offset
> 3. CDN продолжает запись с указанной позиции
>
> Это экономит трафик пользователя и значительно улучшает UX на нестабильных соединениях.

### Thumbnails

> **Candidate**: При отправке фото клиент генерирует thumbnail локально (например, 200x200) и отправляет его первым — он весит мало и загружается быстро. Полноразмерное фото загружается в фоне. Это позволяет собеседнику увидеть превью сразу, не дожидаясь полной загрузки. CDN хранит оба варианта по отдельным URL: `thumbnail_url` и `full_size_url`.

---

## Follow-up: Timestamps

> **Interviewer**: Как обрабатываешь временные метки?

> **Candidate**: Timestamps — неочевидно сложная тема. Вот мои правила:

| Аспект | Решение | Обоснование |
|--------|---------|-------------|
| **Формат хранения** | UTC (Unix timestamp в миллисекундах) | Нет проблем с часовыми поясами |
| **Исходящие сообщения** | Время клиента (device clock) | Мгновенный feedback |
| **Входящие сообщения** | Время сервера | Единый источник правды |
| **Отображение** | Локальное время пользователя | `DateTimeFormatter` с учётом timezone |

> **Interviewer**: А если у пользователя неправильно выставлено время на устройстве?

> **Candidate**: Хороший edge case. Если клиентское время сильно расходится с серверным:
> - Исходящее сообщение может оказаться "из будущего" или далеко в прошлом
> - При получении серверного acknowledgment (`MSG_OUT` echo) — обновляем `created_at` на серверное время
> - Для отображения в списке используем серверное время после синхронизации
>
> Можно также вычислить `clock_drift = server_time - client_time` при `HELLO` и корректировать локально.

---

## Follow-up: Security & Privacy

> **Interviewer**: Как обеспечить безопасность данных?

> **Candidate**: Безопасность мессенджера — это несколько уровней:

### Локальное хранение

- Room DB шифруется через **SQLCipher** — прозрачное шифрование всей базы
- Ключ шифрования хранится в **Android Keystore** (аппаратный хранилище, не извлекается)
- Файлы вложений в **encrypted shared storage** или internal storage

### Транспортная безопасность

- Все соединения через **TLS 1.3**
- Certificate pinning для основного API (предотвращает MITM)
- WebSocket также работает через **WSS** (WebSocket Secure)

### End-to-End Encryption (E2EE)

> **Candidate**: Это важный trade-off. Даже если сообщения зашифрованы на сервере, у разработчика есть доступ к ключам. Настоящая приватность — это E2EE, где только отправитель и получатель имеют ключи.

> **Interviewer**: Стоит ли реализовывать E2EE в рамках этого дизайна?

> **Candidate**: Для scope нашего интервью — нет. E2EE (например, Signal Protocol) — это отдельная огромная тема: обмен ключами, forward secrecy, device verification. Но я бы упомянул это как направление развития и заложил бы архитектуру так, чтобы E2EE можно было добавить позже — через абстракцию `MessageEncryptor` в слое Repository.

### Восприятие приватности

> **Candidate**: Важный момент, который часто забывают: **восприятие** приватности пользователем не менее важно, чем техническая реализация. Если пользователь не доверяет приложению — он не будет им пользоваться, даже если шифрование идеальное. Поэтому нужны видимые индикаторы безопасности в UI — иконка замка, подтверждение шифрования, верификация контакта.

---

## Follow-up: Offline Sync Strategy

> **Interviewer**: Опиши подробнее, как работает синхронизация при переходе из offline в online.

> **Candidate**: Offline sync — одна из сложнейших задач в мобильной архитектуре. Вот стратегия:

### Очередь исходящих сообщений

Когда пользователь отправляет сообщение без сети, оно сохраняется в Room со статусом `PENDING`. При восстановлении соединения:

```
Сеть восстановлена (connectivity callback)
         │
         ▼
  SyncManager.onNetworkAvailable()
         │
         ├──► 1. Установить WS-соединение (HELLO)
         │
         ├──► 2. Запросить пропущенные сообщения
         │       GET /chats/<id>/messages?after_id=<last_known>
         │       Записать в Room → UI обновится через Flow
         │
         └──► 3. Отправить pending-очередь
                 SELECT * FROM Message WHERE status = 'PENDING'
                 ORDER BY created_at ASC
                 Для каждого → WS send MSG_OUT
                 При успехе → UPDATE status = SENT
```

> **Candidate**: Важный нюанс: pending-сообщения отправляются **в порядке создания** (FIFO). Если отправлять параллельно, нарушится порядок в чате. При ошибке конкретного сообщения — помечаем его как `FAILED`, но продолжаем отправку следующих. Пользователь может повторить отправку failed-сообщения вручную.

### Конфликт: сообщение получено, пока были offline

> **Candidate**: Если собеседник отправил сообщения, пока мы были offline — они придут при синхронизации через REST. Room deduplicate по `message_id`, так что дублей не будет. Push-уведомления, полученные в offline, содержат только preview — полные данные загружаются при sync.

---

## Trade-offs и ключевые решения

В любом System Design интервью важно не просто предложить решение, а показать, что ты понимаешь альтернативы и осознанно выбираешь.

### 1. WebSocket vs Polling vs SSE

| Подход | Latency | Расход батареи | Сложность | Выбор |
|--------|---------|---------------|-----------|-------|
| **WebSocket** | Минимальная | Средний (persistent connection) | Высокая (reconnect, heartbeat) | **Выбран** |
| Long Polling | Средняя | Высокий (частые HTTP) | Средняя | Нет |
| SSE | Низкая (server -> client) | Средний | Низкая | Нет (не bidirectional) |

**Почему WebSocket**: мессенджер — один из немногих сценариев, где bidirectional real-time действительно нужен. Read receipts, typing indicators, мгновенная доставка — всё это требует WS.

### 2. Локальные UUID vs серверные ID

| Подход | Offline UX | Идемпотентность | Безопасность |
|--------|-----------|----------------|--------------|
| **Client UUID** | Мгновенный | Да | Ниже |
| Server ID | С задержкой | Нужен mapping | Выше |

**Выбор**: клиентский UUID. Для 1M MAU риски коллизии ничтожны, а UX-выигрыш значительный.

### 3. Зашифрованное vs обычное локальное хранилище

| Подход | Производительность | Безопасность | Сложность |
|--------|--------------------|-------------|-----------|
| **SQLCipher** | ~5-15% overhead | Высокая | Средняя |
| Обычный Room | Максимальная | Низкая | Минимальная |

**Выбор**: SQLCipher. Для мессенджера безопасность данных — не опция, а требование.

### 4. Persistence как SSoT vs Network-first

| Подход | Offline | Консистентность | Сложность |
|--------|---------|----------------|-----------|
| **Room SSoT** | Полная поддержка | Высокая (один источник) | Средняя |
| Network-first | Без поддержки | Зависит от кэша | Низкая |

**Выбор**: Room как Single Source of Truth. Все данные проходят через БД, UI подписан на Room Flow. Сеть пишет в Room, Room нотифицирует UI. Подробнее: [[caching-strategies]].

### 5. Cursor-based vs offset-based пагинация

| Подход | Стабильность | Производительность | Простота |
|--------|-------------|-------------------|----------|
| **Cursor-based** | Не ломается при вставке | O(1) lookup по index | Средняя |
| Offset-based | Ломается при вставке | O(N) на больших offset | Высокая |

**Выбор**: cursor-based. В мессенджере постоянно добавляются новые сообщения — offset-based пагинация будет пропускать или дублировать элементы.

### Советы для интервью

> **Candidate**: В завершение хочу отметить несколько мета-принципов:
> - **Не стремись к идеалу** — интервьюер ищет clear signal, а не production-ready решение
> - **Слушай интервьюера** — если он направляет в определённую тему, следуй за ним
> - **Управляй временем** — лучше покрыть широко с разумной глубиной, чем закопаться в одном компоненте
> - **Называй trade-offs** — каждое решение имеет цену; показывай, что ты это понимаешь
> - **Рисуй диаграммы** — визуальная коммуникация убедительнее словесной

---

## Проверь себя

> [!question]- Почему для мессенджера выбран WebSocket, а не long polling или SSE?
> WebSocket обеспечивает **bidirectional real-time** соединение с минимальной latency. Long polling тратит больше ресурсов батареи из-за частых HTTP-запросов. SSE работает только в одну сторону (server -> client) и не подходит для отправки сообщений и read receipts. Мессенджер — классический сценарий, где persistent bidirectional connection оправдан.

> [!question]- Как отличить входящее вложение от исходящего без отдельного поля direction?
> По полю `full_size_url` в таблице Attachment. Если `full_size_url == NULL` — это исходящее вложение, которое ещё не загружено на CDN (есть только `local_path`). Если URL заполнен — это входящее вложение (или уже успешно загруженное исходящее).

> [!question]- Зачем использовать клиентский UUID вместо серверного ID для сообщений?
> Клиентский UUID даёт три ключевых преимущества: (1) **идемпотентность** — повторная отправка не создаёт дубликат, (2) **мгновенный feedback** — сообщение записывается в Room со статусом PENDING сразу, без ожидания сервера, (3) **offline UX** — пользователь видит своё сообщение немедленно.

> [!question]- Что происходит, когда WebSocket-соединение разрывается?
> Клиент запускает reconnect с **exponential backoff** (1s, 2s, 4s, 8s, max 30s). При переподключении отправляет `HELLO` с последним `connection_id`, чтобы сервер доставил пропущенные сообщения. Если WS недоступен длительное время — fallback на REST polling + push notifications для доставки новых сообщений.

> [!question]- Почему Persistence (Room) выбран как Single Source of Truth, а не сеть?
> Потому что Room SSoT обеспечивает: (1) **offline-доступ** — все данные доступны без сети, (2) **консистентность** — один источник данных для UI, (3) **реактивность** — UI подписан на Room Flow и обновляется автоматически. Сеть пишет в Room, Room нотифицирует UI. Это паттерн, рекомендованный Google для Android-приложений.

---

## Ключевые карточки

```
Какие три коммуникационных слоя использует API Service в мессенджере?
?
1. **WebSocket** — bidirectional real-time (сообщения, read receipts)
2. **REST** — request-response (пагинация чатов, история сообщений)
3. **Cloud Messaging (FCM)** — push-уведомления, когда приложение в фоне
```

```
Какие статусы проходит сообщение от отправки до прочтения?
?
PENDING → SENT → DELIVERED → READ (или PENDING → FAILED при ошибке). Клиент создаёт сообщение со статусом PENDING, после подтверждения сервера — SENT, при доставке собеседнику — DELIVERED, при прочтении — READ.
```

```
Как обеспечить идемпотентность отправки сообщений?
?
Клиент генерирует **UUID v4** для каждого сообщения до отправки. При повторной отправке (retry) используется тот же UUID. Сервер дедуплицирует по UUID — повторный запрос не создаёт дубликат.
```

```
Какие 4 статуса имеет Attachment и что каждый означает?
?
**UPLOADING** — файл загружается на CDN (исходящий). **DOWNLOADING** — файл скачивается с CDN (входящий). **READY** — файл доступен локально и/или на сервере. **FAILED** — операция завершилась ошибкой, нужен retry.
```

```
Почему для входящих сообщений используется серверное время, а не клиентское?
?
Серверное время — единый источник правды. Если использовать клиентское время отправителя, то при неправильных часах на устройстве сообщение окажется "из будущего" или далеко в прошлом, что сломает сортировку. Серверное время гарантирует правильный порядок.
```

```
Что такое Room SSoT и почему это важно для мессенджера?
?
**Room как Single Source of Truth** означает, что все данные проходят через локальную БД. Сеть записывает данные в Room, UI подписан на Room через Flow. Это обеспечивает offline-доступ, консистентность данных и автоматические UI-обновления без ручной синхронизации слоёв.
```

---

## Куда дальше

| Направление | Материал | Зачем |
|-------------|---------|-------|
| Фреймворк SD-интервью | [[system-design-android]] | Общий подход к Mobile System Design |
| Networking на Android | [[android-networking]] | Retrofit, OkHttp, WebSocket, interceptors |
| Room Deep Dive | [[android-room-deep-dive]] | Работа с локальной БД, миграции, Flow |
| Фоновая работа | [[android-background-work]] | WorkManager, foreground services |
| Push-уведомления | [[android-notifications]] | FCM, notification channels, payload |
| Кэширование | [[caching-strategies]] | Стратегии кэширования, offline-first |

---

## Источники

- [iartr/mobile-system-design — Chat App Exercise](https://github.com/iartr/mobile-system-design/blob/master/exercises/chat-app.md) — оригинальный репозиторий с набором Mobile System Design exercises
- [Android Developers — Room Persistence Library](https://developer.android.com/training/data-storage/room)
- [OkHttp WebSocket API](https://square.github.io/okhttp/4.x/okhttp/okhttp3/-web-socket/)

---
title: "GraphQL: schema-first API design"
created: 2026-02-10
modified: 2026-02-10
type: deep-dive
status: published
confidence: high
sources_verified: true
tags:
  - topic/architecture
  - architecture/api
  - architecture/graphql
  - backend/graphql
  - type/deep-dive
  - level/intermediate
related:
  - "[[api-design]]"
  - "[[api-rest-deep-dive]]"
  - "[[api-grpc-deep-dive]]"
  - "[[api-modern-patterns]]"
  - "[[network-http-evolution]]"
  - "[[network-realtime-protocols]]"
  - "[[caching-strategies]]"
cs-foundations:
  - type-system
  - graph-theory
  - query-optimization
  - caching
  - compiler-theory
  - schema-validation
reading_time: 23
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# GraphQL: schema-first API design

2012 год. Facebook Mobile — провал. Приложение на HTML5 тормозит. Марк Цукерберг позже назовёт ставку на HTML5 «самой большой стратегической ошибкой». Команда переписывает на native. Но REST API, спроектированное для веба, не справляется: News Feed требует 15 roundtrips для одного экрана. Ли Байрон, Дэн Шафер и Ник Шрок создают внутренний инструмент, который позволяет клиенту запросить ровно те данные, которые нужны, в одном запросе. В 2015 году Facebook открывает его миру. Это GraphQL.

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **REST API** | Понимание request/response, over/under-fetching | [[api-rest-deep-dive]] |
| **HTTP протокол** | GraphQL работает поверх HTTP | [[network-http-evolution]] |
| **JSON** | Формат запросов и ответов GraphQL | Базовые знания |
| **Типизация** | GraphQL строго типизирован | Основы TypeScript/любого типизированного языка |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Schema** | Описание всех типов и операций API | Меню ресторана: все блюда и ингредиенты |
| **Query** | Операция чтения данных | «Покажи мне вот это и вот это» |
| **Mutation** | Операция изменения данных | «Создай/обнови/удали это» |
| **Subscription** | Подписка на изменения в реальном времени | «Сообщи мне, когда что-то изменится» |
| **Resolver** | Функция, получающая данные для конкретного поля | Повар: получает заказ, готовит блюдо |
| **SDL** | Schema Definition Language | Язык описания «меню» |
| **Type** | Описание структуры данных (Object, Scalar, Enum...) | Карточка товара с полями |
| **Field** | Конкретное свойство типа | Одна строка в карточке товара |
| **DataLoader** | Утилита для batch-загрузки данных | Курьер: ждёт все заказы и везёт одной ходкой |
| **Introspection** | Возможность запросить схему у сервера | «Покажи мне всё меню» |
| **Fragment** | Переиспользуемый набор полей | Шаблон заказа: «как обычно» |
| **Directive** | Инструкция для изменения поведения (@skip, @include) | Примечание к заказу: «без лука» |
| **Federation** | Архитектура для объединения нескольких GraphQL-сервисов | Фудкорт: разные кухни, один заказ |
| **Persisted Query** | Предварительно зарегистрированный запрос (по хешу) | Заказ по номеру вместо полного описания |

---

## Зачем GraphQL существует: проблема и решение

### Проблема Facebook (2012-2015)

News Feed — сложный UI. Один экран показывает посты, авторов, комментарии, лайки, фото, рекомендации. С REST API это выглядело так:

```
ЭКРАН NEWS FEED (REST):
───────────────────────
GET /feed                   → Список постов (id, text, author_id)
GET /users/42               → Автор поста 1
GET /users/43               → Автор поста 2
...
GET /posts/1/comments       → Комментарии к посту 1
GET /posts/2/comments       → Комментарии к посту 2
...
GET /posts/1/likes          → Лайки поста 1
GET /posts/1/media          → Медиа поста 1
...

Итого: 10-15 HTTP-запросов для одного экрана.
На 3G: 2-3 секунды на каждый roundtrip.
Пользователь ждёт 10+ секунд.
```

**Over-fetching:** API возвращает 50 полей пользователя, мобильному приложению нужны 3 (имя, аватар, id). Трафик на мобильных сетях 2012 года — на вес золота.

**Under-fetching:** Для связанных данных нужны отдельные запросы. Один экран = десятки roundtrips.

### Решение GraphQL

```
ЭКРАН NEWS FEED (GraphQL):
──────────────────────────
POST /graphql

query {
  feed(first: 10) {
    posts {
      text
      createdAt
      author {             ← Связанные данные
        name               ← Только нужные поля
        avatarUrl
      }
      comments(first: 3) { ← Вложенный запрос
        text
        author { name }
      }
      likesCount
      media { url, type }
    }
  }
}

Итого: 1 HTTP-запрос.
Ответ содержит ровно то, что запросил клиент.
Ни больше, ни меньше.
```

### Хронология

| Год | Событие |
|-----|---------|
| **2012** | Lee Byron, Dan Schafer, Nick Schrock создают GraphQL внутри Facebook |
| **2015** | Facebook открывает GraphQL (open source, спецификация) |
| **2016** | GitHub запускает GraphQL API v4 |
| **2017** | Airbnb, Shopify, Twitter начинают использовать |
| **2018** | GraphQL Foundation (под Linux Foundation) |
| **2020** | Apollo Federation для микросервисов |
| **2023** | Shopify обрабатывает 90% API-запросов через GraphQL |
| **2025** | GraphQL — стандарт для сложных клиентских приложений |

---

## Schema Definition Language (SDL)

Schema — центральный элемент GraphQL. Она определяет, какие данные доступны и как к ним обращаться. SDL — язык описания схемы. Знание SDL = понимание любого GraphQL API.

### Скалярные типы

```graphql
# Встроенные скалярные типы GraphQL
# Это «атомы» — неделимые значения

String    # Текст (UTF-8)
Int       # Целое число (32-bit signed)
Float     # Число с плавающей точкой
Boolean   # true/false
ID        # Уникальный идентификатор (строка, но семантически — ID)

# Пользовательские скаляры (часто нужны в production):
scalar DateTime   # ISO 8601: "2026-02-10T14:30:00Z"
scalar JSON       # Произвольный JSON (используй редко!)
scalar URL        # Валидный URL
scalar Email      # Валидный email
```

### Object Types

```graphql
# Тип описывает структуру данных
# Каждое поле имеет тип

type User {
  id: ID!              # ! означает non-null (обязательное поле)
  name: String!
  email: String!
  age: Int             # Без ! — может быть null
  posts: [Post!]!      # Список постов. Не-null список, не-null элементы
  role: Role!          # Enum
  address: Address     # Связанный объект (может быть null)
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!        # Связь: каждый пост имеет автора
  comments: [Comment!]!
  tags: [String!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Comment {
  id: ID!
  text: String!
  author: User!
  post: Post!
  createdAt: DateTime!
}
```

### Nullability — философия GraphQL

```
ПРАВИЛО: Поля nullable по умолчанию.
         ! делает поле обязательным.

Почему так:
─────────
В REST если одно поле вернуло ошибку — весь запрос 500.

В GraphQL — ошибка в одном поле не ломает весь ответ:
поле возвращает null + ошибка в массиве errors.

Пример:
query {
  user(id: 123) {
    name                ← "Иван" (ок)
    expensiveField      ← null (сервис недоступен)
  }
}

Ответ:
{
  "data": {
    "user": {
      "name": "Иван",
      "expensiveField": null     ← Частичный ответ, не полная ошибка
    }
  },
  "errors": [
    {"message": "Service unavailable", "path": ["user", "expensiveField"]}
  ]
}

ПРАВИЛА NULLABILITY:
────────────────────
String   → может быть null (безопасно)
String!  → никогда null (если resolver упадёт — null «всплывёт» к родителю)
[Post]   → список может быть null, элементы могут быть null
[Post!]  → список может быть null, но элементы — нет
[Post!]! → список не null И элементы не null (самый строгий)
```

### Enum, Interface, Union, Input

```graphql
# ENUM — фиксированный набор значений
enum Role {
  ADMIN
  EDITOR
  VIEWER
}

# INTERFACE — общие поля для нескольких типов
# Как интерфейс в ООП: определяет контракт
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
}

type Post implements Node {
  id: ID!
  title: String!
}

# UNION — «один из» (без общих полей)
# Полезен для поиска, который возвращает разные типы
union SearchResult = User | Post | Comment

type Query {
  search(query: String!): [SearchResult!]!
}

# Запрос к Union — нужны inline fragments:
# query {
#   search(query: "GraphQL") {
#     ... on User { name, email }
#     ... on Post { title, author { name } }
#     ... on Comment { text }
#   }
# }


# INPUT — специальный тип для аргументов мутаций
# Нельзя использовать обычные object types как аргументы
input CreateUserInput {
  name: String!
  email: String!
  role: Role = VIEWER   # Значение по умолчанию
}

type Mutation {
  createUser(input: CreateUserInput!): User!
}
```

---

## Как GraphQL работает под капотом

### Execution Model: от запроса до ответа

```
┌──────────────────────────────────────────────────────────────┐
│              GRAPHQL EXECUTION PIPELINE                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. PARSING                                                   │
│  ─────────                                                    │
│  Строка запроса → AST (Abstract Syntax Tree)                  │
│  "query { user(id: 1) { name } }"                             │
│       ↓                                                       │
│  Document → SelectionSet → Field("user") → Field("name")     │
│                                                               │
│  2. VALIDATION                                                │
│  ──────────                                                   │
│  AST проверяется против Schema:                               │
│  • Существует ли тип User?                                    │
│  • Есть ли у User поле name?                                  │
│  • Аргумент id — правильного типа?                            │
│  • Нет циклических фрагментов?                                │
│                                                               │
│  3. EXECUTION                                                 │
│  ─────────                                                    │
│  Resolver chain — каждое поле вызывает свой resolver:         │
│                                                               │
│  Query.user(id: 1)     → DB: SELECT * FROM users WHERE id=1  │
│    └─ User.name        → Возвращает user.name из результата   │
│    └─ User.posts       → DB: SELECT * FROM posts WHERE...     │
│       └─ Post.title    → post.title                           │
│       └─ Post.author   → DataLoader.load(post.author_id)     │
│                                                               │
│  4. RESPONSE                                                  │
│  ────────                                                     │
│  Результаты собираются в JSON, форма = форма запроса          │
│  { "data": { "user": { "name": "Иван", "posts": [...] } } } │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Resolver chain — как данные загружаются

Каждое поле в схеме может иметь resolver — функцию, которая возвращает данные для этого поля. Resolver получает 4 аргумента:

```javascript
// Resolver для поля User.posts

const resolvers = {
  User: {
    // parent  — родительский объект (User)
    // args    — аргументы поля (first, after)
    // context — общий контекст (db, auth, dataloaders)
    // info    — метаданные запроса (AST, имя поля)

    posts: (parent, args, context, info) => {
      return context.db.posts.findMany({
        where: { authorId: parent.id },
        take: args.first || 10
      });
    }
  }
};

// Если resolver не указан — GraphQL использует default resolver:
// (parent) => parent[fieldName]
// Это значит: User.name → user.name (просто берёт свойство)
```

**Resolver chain** работает сверху вниз. Query.user → User.name, User.posts → Post.title, Post.author. Каждый уровень вложенности — отдельный resolver.

---

## N+1 проблема и DataLoader

N+1 — самая частая проблема производительности в GraphQL. Базовое объяснение есть в [[api-design]]. Здесь разберём механизм DataLoader глубже.

### Почему N+1 возникает

Resolver chain выполняется поле за полем. Для списка из 100 постов:

```
Query.posts → 1 SQL: SELECT * FROM posts LIMIT 100

Для каждого поста вызывается Post.author:
Post.author(post[0]) → SELECT * FROM users WHERE id = 42
Post.author(post[1]) → SELECT * FROM users WHERE id = 43
Post.author(post[2]) → SELECT * FROM users WHERE id = 42  ← Дубликат!
...
Post.author(post[99]) → SELECT * FROM users WHERE id = 71

Итого: 1 + 100 = 101 SQL-запрос.
Многие из них дублируются (один автор у нескольких постов).
```

### DataLoader: как работает батчинг

DataLoader решает N+1, используя два механизма: **батчинг** и **кэширование** в рамках одного запроса.

```
┌──────────────────────────────────────────────────────────────┐
│                   DATALOADER МЕХАНИЗМ                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Event Loop Tick 1:                                           │
│  ┌─────────────────────────────────────────────────┐         │
│  │ Post.author(post[0]) → loader.load(42)          │         │
│  │ Post.author(post[1]) → loader.load(43)          │         │
│  │ Post.author(post[2]) → loader.load(42) ← дубль! │         │
│  │ Post.author(post[3]) → loader.load(44)          │         │
│  │ ...                                              │         │
│  └─────────────────────────────────────────────────┘         │
│  DataLoader собирает ВСЕ .load() за один тик event loop      │
│                                                               │
│  End of Tick:                                                 │
│  ┌─────────────────────────────────────────────────┐         │
│  │ Уникальные ID: [42, 43, 44, ...]               │         │
│  │ Один SQL: SELECT * FROM users                   │         │
│  │           WHERE id IN (42, 43, 44, ...)         │         │
│  └─────────────────────────────────────────────────┘         │
│                                                               │
│  DataLoader распределяет результаты:                          │
│  loader.load(42) → User{id:42}                               │
│  loader.load(43) → User{id:43}                                │
│  loader.load(42) → User{id:42} (из кэша, не из БД!)          │
│                                                               │
│  КЭШИРОВАНИЕ:                                                 │
│  • Per-request: новый DataLoader на каждый GraphQL-запрос     │
│  • Повторный load(42) → из кэша, не из БД                    │
│  • НЕ глобальный кэш! Только в рамках одного запроса         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

```javascript
// Создание DataLoader (один на запрос!)

const DataLoader = require('dataloader');

// Batch-функция: получает массив ключей, возвращает массив результатов
// ВАЖНО: порядок результатов должен совпадать с порядком ключей!
const userLoader = new DataLoader(async (userIds) => {
  // userIds = [42, 43, 44] — уникальные ID, собранные за один тик

  const users = await db.query(
    'SELECT * FROM users WHERE id = ANY($1)',
    [userIds]
  );

  // Создаём Map для быстрого поиска
  const userMap = new Map(users.map(u => [u.id, u]));

  // Возвращаем в ТОЧНОМ порядке входных ID
  // Если пользователь не найден — null (не undefined!)
  return userIds.map(id => userMap.get(id) || null);
});

// Использование в resolver:
const resolvers = {
  Post: {
    author: (post, _, context) => context.loaders.user.load(post.authorId)
  }
};

// ВАЖНО: новый DataLoader на КАЖДЫЙ GraphQL-запрос
// Иначе кэш утечёт между разными пользователями
const server = new ApolloServer({
  context: () => ({
    loaders: {
      user: new DataLoader(batchUsers),
      post: new DataLoader(batchPosts)
    }
  })
});
```

---

## Apollo Federation: распределённый GraphQL

### Проблема монолитной схемы

Когда схема растёт (сотни типов, десятки команд), один GraphQL-сервер становится bottleneck:
- Одна команда блокирует деплой другой
- Одна ошибка ломает весь API
- Схема в тысячи строк — невозможно поддерживать

### Архитектура Federation

```
┌──────────────────────────────────────────────────────────────┐
│                  APOLLO FEDERATION                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Клиенты                                                      │
│  ┌──────┐  ┌──────┐  ┌──────┐                                │
│  │ Web  │  │Mobile│  │ CLI  │                                │
│  └──┬───┘  └──┬───┘  └──┬───┘                                │
│     │         │         │                                     │
│     └─────────┼─────────┘                                     │
│               │                                               │
│     ┌─────────▼─────────┐                                     │
│     │  Gateway / Router  │  ← Единая точка входа              │
│     │  (Apollo Router)   │  ← Составляет supergraph           │
│     │                    │  ← Query planning                  │
│     └────┬────┬────┬────┘                                     │
│          │    │    │                                           │
│     ┌────▼──┐│┌───▼────┐                                      │
│     │Users  │││Products│                                      │
│     │Subgraph││Subgraph│                                      │
│     │       │││        │                                      │
│     │type User         │                                      │
│     │  id: ID!         │  type Product                        │
│     │  name: String    │    id: ID!                           │
│     │  email: String   │    title: String                     │
│     │                  │    reviews: [Review]                 │
│     └────────┘└────────┘                                      │
│          │                                                    │
│     ┌────▼──────┐                                              │
│     │  Reviews   │                                             │
│     │  Subgraph  │                                             │
│     │            │                                             │
│     │ type Review│                                             │
│     │   id: ID!  │                                             │
│     │   text: String                                          │
│     │   author: User  ← Ссылка на User из другого subgraph   │
│     └────────────┘                                             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Ключевые директивы Federation

```graphql
# Users Subgraph
# @key — «ключ» для идентификации сущности между subgraphs
type User @key(fields: "id") {
  id: ID!
  name: String!
  email: String!
}

# Reviews Subgraph
# Расширяет User из другого subgraph
type User @key(fields: "id") {
  id: ID!
  reviews: [Review!]!  # Reviews subgraph добавляет это поле к User
}

type Review {
  id: ID!
  text: String!
  rating: Int!
  author: User!        # Ссылка на User (resolver через @key)
}

# Products Subgraph
type Product @key(fields: "id") {
  id: ID!
  title: String!
  price: Float!
}

# Запрос клиента (не знает о subgraphs!):
query {
  user(id: 123) {
    name              # ← из Users Subgraph
    email             # ← из Users Subgraph
    reviews {         # ← из Reviews Subgraph
      text
      rating
    }
  }
}

# Router сам разбивает запрос на части и отправляет в нужные subgraphs.
```

**Federation 2 (текущая версия):** Улучшенная композиция схем, обратная совместимость с v1, подсказки при несогласованности схем между subgraphs. Apollo рекомендует Apollo Router (Rust) вместо Node.js Gateway для производительности.

---

## Subscriptions: real-time GraphQL

### Когда использовать

Subscriptions подходят для данных, которые меняются часто и инкрементально: чат, уведомления, биржевые котировки, статус доставки. Для редких обновлений — polling или push-уведомления проще и надёжнее.

### Транспорт: WebSocket vs SSE vs Multipart HTTP

```
┌──────────────────────────────────────────────────────────────┐
│           ТРАНСПОРТ ДЛЯ SUBSCRIPTIONS                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  WEBSOCKET (классический подход)                              │
│  ────────────────────────────────                             │
│  • Библиотека: graphql-ws (замена subscriptions-transport-ws) │
│  • Bidirectional, low latency                                 │
│  • Проблема: stateful! Сложно масштабировать                  │
│  • Проблема: браузер откатывается на HTTP/1.1                 │
│  • Проблема: auth-токен виден клиенту                         │
│                                                               │
│  SSE (Server-Sent Events)                                     │
│  ────────────────────────                                     │
│  • Однонаправленный (сервер → клиент)                         │
│  • Работает поверх обычного HTTP (HTTP/2 мультиплексинг!)     │
│  • Автоматический реконнект                                   │
│  • WunderGraph и другие рекомендуют SSE вместо WebSocket      │
│                                                               │
│  MULTIPART HTTP (Apollo GraphOS)                              │
│  ───────────────────────────────                              │
│  • Chunks в HTTP response                                     │
│  • Не требует отдельного соединения                           │
│  • Apollo Router поддерживает нативно                         │
│                                                               │
│  РЕКОМЕНДАЦИЯ (2025):                                         │
│  SSE или Multipart HTTP для клиентов.                         │
│  WebSocket — если нужен bidirectional (чат с typing indicator).│
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Масштабирование subscriptions

```
ПРОБЛЕМА: 10,000 пользователей подписаны на обновления цен

Сервер 1: 3,000 WebSocket-соединений
Сервер 2: 3,000 WebSocket-соединений
Сервер 3: 4,000 WebSocket-соединений

Событие "цена изменилась" происходит на Сервере 1.
Как доставить его подписчикам на Серверах 2 и 3?

РЕШЕНИЕ: Redis Pub/Sub

┌─────────┐     ┌─────────┐     ┌─────────┐
│Server 1 │────→│  Redis   │←────│Server 2 │
│ (event) │     │  Pub/Sub │     │         │
└─────────┘     └────┬─────┘     └─────────┘
                     │
                ┌────▼─────┐
                │ Server 3  │
                └──────────┘

1. Сервер 1 публикует событие в Redis
2. Redis рассылает всем подписчикам (серверам)
3. Каждый сервер отправляет данные своим клиентам

ВАЖНО: In-memory PubSub (graphql-subscriptions) — только для одного сервера.
Для production — Redis, Kafka или managed service.
```

---

## Безопасность и производительность

### Глубина и сложность запросов

В GraphQL клиент контролирует запрос — это мощно, но опасно. Атакующий может создать запрос, который положит сервер:

```graphql
# Атака: бесконечная вложенность
query {
  users {
    posts {
      author {
        posts {
          author {
            posts {
              author { ... }  # 50 уровней глубины
            }
          }
        }
      }
    }
  }
}
```

Базовые защиты (depth limiting, cost analysis) описаны в [[api-design]]. Здесь — дополнительные стратегии.

### Persisted Queries: безопасность в production

**Идея:** Вместо произвольных запросов клиент отправляет только хеш предварительно зарегистрированного запроса. Сервер выполняет только «одобренные» запросы.

```
БЕЗ PERSISTED QUERIES:
──────────────────────
Клиент → POST /graphql
         body: { query: "{ users { name posts { title } } }" }

Любой может отправить любой запрос. Включая вредоносные.

С PERSISTED QUERIES:
────────────────────
1. При сборке приложения:
   Все запросы хешируются → SHA-256
   Хеши регистрируются на сервере

2. В runtime:
   Клиент → POST /graphql
            body: { extensions: { persistedQuery: { sha256Hash: "abc123" } } }

   Сервер ищет хеш в реестре.
   Нашёл → выполняет.
   Не нашёл → 400 Bad Request.

   Произвольные запросы невозможны!
```

**Два варианта:**

| | APQ (Automatic Persisted Queries) | Strict Persisted Queries |
|---|---|---|
| **Регистрация** | Автоматическая (первый запрос) | Build-time (CI/CD) |
| **Безопасность** | Нет (любой запрос зарегистрируется) | Да (whitelist) |
| **Производительность** | Да (GET + CDN кэширование) | Да |
| **Для чего** | Development, внутренние API | Production, публичные API |

**Рекомендация:** APQ для разработки. Strict persisted queries для production. Сначала включить в audit mode (логировать незарегистрированные запросы), потом — в enforcement mode (блокировать).

### Rate Limiting для GraphQL

REST rate limiting считает запросы: «100 запросов в минуту». Для GraphQL это не работает — один запрос может быть дешёвым или дорогим:

```graphql
# Дешёвый запрос (cost: 1)
query { viewer { name } }

# Дорогой запрос (cost: 5000+)
query {
  organization(login: "facebook") {
    repositories(first: 100) {
      nodes {
        issues(first: 100) {
          nodes { title body comments(first: 50) { nodes { body } } }
        }
      }
    }
  }
}
```

**Complexity-based rate limiting:**

```
Каждое поле имеет «стоимость»:
─────────────────────────────

Скалярное поле:    cost = 1
Объект:            cost = 2
Список:            cost = multiplier × child_cost

Пример:
query {
  users(first: 10) {      ← 10 × (2 + 1 + 1) = 40
    name                   ← 1
    email                  ← 1
  }
}
Total cost: 40

Бюджет: 10,000 points / hour
Этот запрос «стоит» 40 points.
```

GitHub GraphQL API использует именно этот подход — Node limit (500,000 nodes per request).

### Introspection в production

```
⚠️ Introspection позволяет запросить ВСЮ схему API:

query {
  __schema {
    types { name fields { name type { name } } }
  }
}

Это открывает всю структуру данных для потенциального атакующего.

РЕКОМЕНДАЦИЯ:
─────────────
Development: introspection ON  (для инструментов: GraphiQL, Playground)
Production:  introspection OFF (или только для авторизованных)

// Apollo Server
const server = new ApolloServer({
  introspection: process.env.NODE_ENV !== 'production'
});
```

---

## Клиентское кэширование

### Apollo Client: normalized cache

Apollo Client хранит данные в **нормализованном кэше** — как мини-база данных в браузере:

```
ОТВЕТ СЕРВЕРА:
{
  "user": {
    "__typename": "User",
    "id": "123",
    "name": "Иван",
    "posts": [
      {"__typename": "Post", "id": "1", "title": "Первый пост"},
      {"__typename": "Post", "id": "2", "title": "Второй пост"}
    ]
  }
}

NORMALIZED CACHE:
┌────────────────────────────────────────────┐
│ "User:123" → { name: "Иван", posts: [...] }│
│ "Post:1"   → { title: "Первый пост" }      │
│ "Post:2"   → { title: "Второй пост" }      │
└────────────────────────────────────────────┘

Ключ = __typename + id.
Если другой запрос вернёт Post:1 с обновлённым title —
ВСЕ компоненты, использующие Post:1, получат обновление.
Автоматически. Без ручной инвалидации.
```

### Сравнение GraphQL-клиентов

| Критерий | Apollo Client | Relay | urql |
|----------|:---:|:---:|:---:|
| **Bundle size** | ~31KB | Compile-time (0KB runtime parser) | ~12KB |
| **Кэш** | Normalized (настраиваемый) | Normalized (strict, по global ID) | Document (default) + normalized (plugin) |
| **Learning curve** | Средний | Высокий | Низкий |
| **React support** | Отличный | Нативный (Facebook) | Отличный |
| **Vue/Svelte** | Через community | Нет | Нативный |
| **Offline** | Встроенный | Community | Plugin |
| **Оптимистичные обновления** | Встроенный | Встроенный | Plugin |
| **Подходит для** | Большие приложения, полный контроль | Огромные React-приложения (Facebook-scale) | Лёгкие проекты, мультифреймворк |

**Выбор:**
- **Apollo Client** — если нужен полный контроль и экосистема (Apollo Studio, Federation)
- **Relay** — если React + огромная схема + готовы к строгим требованиям (Relay-compliant schema)
- **urql** — если нужна лёгкость, быстрый старт, или не React

---

## Когда НЕ использовать GraphQL

| Сценарий | Почему GraphQL плохой выбор | Альтернатива |
|----------|----------------------------|-------------|
| **Простой CRUD** | 5 endpoints — не проблема. GraphQL = оверинжиниринг | REST |
| **File uploads** | GraphQL не для бинарных данных. Multipart upload — костыль | REST + presigned URLs |
| **Public API для третьих лиц** | GraphQL сложнее для интеграции. Больше документации. Меньше инструментов | REST + OpenAPI |
| **Heavy caching** | REST кэшируется через HTTP (CDN, прокси). GraphQL — один endpoint, POST | REST |
| **Команда без опыта** | GraphQL learning curve: schema design, resolvers, N+1, caching | REST |
| **Микросервисы (только внутренняя связь)** | gRPC в 5-7 раз быстрее, binary format, streaming | gRPC |
| **Real-time intensive** | WebSocket/SSE проще без GraphQL subscription overhead | WebSocket напрямую |

### Сигналы, что REST достаточно

1. API обслуживает один тип клиента (только web или только mobile)
2. Данные плоские, без глубокой вложенности
3. Клиент использует все или почти все поля ответа
4. Кэширование критично для производительности
5. Команда уже имеет REST-экспертизу

### Сигналы, что GraphQL нужен

1. Множество клиентов с разными потребностями (web, mobile, IoT)
2. Данные сильно связаны (граф зависимостей)
3. Клиенты нуждаются в разных подмножествах данных
4. Частые изменения в требованиях к API
5. Схема как контракт между frontend и backend команд

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|------------|
| **«GraphQL заменяет REST»** | GraphQL и REST решают разные задачи. GitHub, Shopify, Netflix используют оба. REST — для публичных API, простого CRUD, кэширования. GraphQL — для сложных клиентских данных |
| **«GraphQL всегда быстрее REST»** | GraphQL экономит roundtrips (один запрос вместо нескольких). Но каждый запрос может быть тяжелее. Без DataLoader — N+1 делает GraphQL медленнее REST. Закэшированный REST-ответ быстрее любого GraphQL-запроса |
| **«GraphQL решает over-fetching»** | Решает для клиента. Но на сервере resolver может загружать ВСЕ поля из БД, даже если клиент запросил одно. Нужна оптимизация: look-ahead, field selection |
| **«Нужен Apollo для GraphQL»** | Apollo — самый популярный, но не единственный. Yoga (The Guild), Mercurius (Fastify), graphql-http — легковесные альтернативы для сервера. urql, Relay — для клиента |
| **«GraphQL — только для React»** | GraphQL — спецификация, не библиотека. Работает с любым языком и фреймворком. Vue (urql/Apollo), Angular (Apollo), Python (Strawberry), Go (gqlgen), Java (DGS) |
| **«GraphQL нельзя кэшировать»** | Сложнее, чем REST, но возможно. Persisted queries + GET + CDN. Normalized cache на клиенте. @cacheControl директива в Apollo. Dataloader — per-request cache |
| **«Schema = база данных»** | Schema — API contract, не database schema. Никогда не экспонируй структуру БД напрямую. Schema — то, что нужно клиенту, не то, как хранятся данные |
| **«Subscriptions = WebSocket»** | WebSocket — один из транспортов. SSE, multipart HTTP — легче масштабируются. Apollo GraphOS поддерживает federated subscriptions через HTTP |

---

## CS-фундамент

| Концепция | Применение в GraphQL |
|-----------|---------------------|
| **Type System** | Строгая типизация: каждое поле, аргумент, ответ имеет тип. Ошибки ловятся при валидации до выполнения. Как статическая типизация в компиляторах |
| **Graph Theory** | Данные — граф с узлами (типы) и рёбрами (связи). Query — обход графа. Resolver chain — DFS по графу типов |
| **Query Optimization** | DataLoader батчит запросы. Query planner в Federation разбивает запрос на подзапросы. Аналогия с SQL query planner |
| **Compiler Theory** | Parsing → AST → Validation → Execution. Тот же pipeline, что в компиляторах. GraphQL-запрос — мини-программа |
| **Schema Validation** | Schema — контракт. Любое изменение проверяется на совместимость. Schema registry — как type checker |
| **Caching** | Normalized cache (Apollo) — денормализация как в БД. Ключ = typename + id. Автоматическая инвалидация при обновлении |
| **Batching** | DataLoader: собрать N запросов за один тик event loop → один batch. Амортизация: O(N) запросов → O(1) |

---

## Куда дальше

Если начинаешь с API:
→ [[api-design]] — обзор REST, GraphQL, gRPC: когда что выбрать, базовые паттерны

Если ищешь альтернативы GraphQL:
→ [[api-rest-deep-dive]] — REST для публичных API: constraints Филдинга, HATEOAS, идемпотентность
→ [[api-grpc-deep-dive]] — gRPC для межсервисной коммуникации: бинарный формат, streaming, 5-7x быстрее

Современные паттерны:
→ [[api-modern-patterns]] — tRPC (type-safe без codegen), Webhooks, API Gateway, BFF

Real-time протоколы (транспорт для subscriptions):
→ [[network-realtime-protocols]] — WebSocket, SSE, WebRTC глубже: механизмы, масштабирование

Кэширование (слабое место GraphQL):
→ [[caching-strategies]] — Redis, CDN, HTTP-кэширование — стратегии, актуальные для GraphQL

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [GraphQL Official Specification](https://spec.graphql.org/) | Спецификация | Формальное определение языка |
| 2 | [GraphQL.org: Learn](https://graphql.org/learn/) | Документация | Официальные гайды, best practices |
| 3 | [Apollo Federation Docs](https://www.apollographql.com/docs/federation/) | Документация | Federation 2, Router, subgraphs |
| 4 | [Apollo Client Docs](https://www.apollographql.com/docs/react/) | Документация | Normalized cache, persisted queries |
| 5 | [Federated Subscriptions in GraphOS](https://www.apollographql.com/blog/federated-subscriptions-in-graphos-real-time-data-at-scale) | Блог | Масштабирование subscriptions через HTTP |
| 6 | [WunderGraph: Deprecate Subscriptions over WebSockets](https://wundergraph.com/blog/deprecate_graphql_subscriptions_over_websockets) | Блог | SSE vs WebSocket для subscriptions |
| 7 | [GraphQL Subscriptions at Scale — Medium](https://techpreneurr.medium.com/graphql-subscriptions-at-scale-the-websocket-problem-a6f4e007adb2) | Статья | 50K concurrent users, lessons learned |
| 8 | [Hasura: Apollo vs Relay vs urql](https://hasura.io/blog/exploring-graphql-clients-apollo-client-vs-relay-vs-urql) | Статья | Детальное сравнение клиентов |
| 9 | [urql Documentation: Comparison](https://nearform.com/open-source/urql/docs/comparison/) | Документация | urql vs Apollo, подход к кэшированию |
| 10 | [StackHawk: GraphQL Security](https://www.stackhawk.com/blog/graphql-security/) | Статья | Depth limiting, cost analysis, persisted queries |
| 11 | [Apollo: Safelisting with Persisted Queries](https://www.apollographql.com/docs/graphos/platform/security/persisted-queries) | Документация | Strict mode, audit mode, PQL |
| 12 | [Codecentric: Secure GraphQL with Persisted Queries](https://www.codecentric.de/en/knowledge-hub/blog/how-to-secure-a-graphql-service-using-persisted-queries) | Статья | Whitelist подход, build pipeline |
| 13 | [GraphQL: Lessons After 4 Years — Scaling Subscriptions](https://mattkrick.medium.com/graphql-after-4-years-scaling-subscriptions-d6ea1a8987be) | Блог | Production опыт, Redis Pub/Sub |
| 14 | [LogRocket: Federated GraphQL](https://blog.logrocket.com/the-what-when-why-and-how-of-federated-graphql/) | Статья | Federation vs Stitching, архитектура |
| 15 | [Schema Stitching: Approaches](https://the-guild.dev/graphql/stitching/docs/approaches) | Документация | Альтернатива Federation (The Guild) |
| 16 | [GitHub GraphQL API](https://docs.github.com/en/graphql) | Документация | Node limit, cost-based rate limiting |
| 17 | [Shopify GraphQL Design Tutorial](https://shopify.dev/docs/api/usage/graphql-basics) | Документация | Production GraphQL для e-commerce |
| 18 | [DataLoader GitHub](https://github.com/graphql/dataloader) | Библиотека | Batch loading, per-request caching |
| 19 | [How to GraphQL](https://www.howtographql.com/) | Туториал | Полный курс по GraphQL |
| 20 | [GraphQL: The Documentary (YouTube)](https://www.youtube.com/watch?v=783ccP__No8) | Видео | История создания GraphQL в Facebook |

---

**Последняя верификация**: 2026-02-10
**Уровень достоверности**: high

---

*Проверено: 2026-02-10*

---

## Проверь себя

> [!question]- Почему DataLoader создаётся заново на каждый GraphQL-запрос, а не переиспользуется глобально?
> DataLoader кэширует результаты в рамках одного запроса. Если переиспользовать его глобально, кэш будет утекать между разными пользователями: пользователь A может увидеть данные пользователя B из кэша. Кроме того, глобальный кэш не знает, когда данные устарели — он превращается в неконтролируемый stale cache без стратегии инвалидации. Per-request кэш решает обе проблемы: изоляция данных между запросами и автоматическая очистка после завершения запроса.

> [!question]- В e-commerce приложении каталог товаров запрашивается с мобильного, веб- и IoT-клиента. Каждый клиент показывает разный набор полей. Команда обсуждает выбор между REST и GraphQL. Какие аргументы перевешивают в пользу GraphQL, а при каком условии REST всё же будет лучше?
> В пользу GraphQL: три разных клиента с разными потребностями — классический сценарий over-fetching/under-fetching. GraphQL позволяет каждому клиенту запрашивать ровно те поля, которые нужны, одним запросом. Не нужно создавать три версии эндпоинтов или BFF-слой. Однако если каталог — публичный API для сторонних интеграторов, или если критично HTTP-кэширование через CDN (например, страницы каталога почти не меняются), REST с OpenAPI будет проще в поддержке, интеграции и кэшировании.

> [!question]- Сервис чата использует GraphQL Subscriptions через WebSocket. При масштабировании до 5 серверов сообщения перестают доходить до части пользователей. В чём причина и как решить?
> WebSocket-соединение привязано к конкретному серверу. Когда пользователь A на сервере 1 отправляет сообщение, событие публикуется локально — подписчики на серверах 2-5 его не получают. Решение — вынести Pub/Sub за пределы серверов: Redis Pub/Sub или Kafka. Сервер 1 публикует событие в Redis, Redis рассылает его всем подписанным серверам, каждый сервер доставляет данные своим WebSocket-клиентам. Альтернативно можно рассмотреть SSE вместо WebSocket — он проще масштабируется поверх HTTP/2.

> [!question]- Разработчик спроектировал GraphQL-схему, которая один к одному повторяет структуру таблиц в базе данных. Оцените это решение. Какие проблемы возникнут?
> Это антипаттерн. GraphQL-схема — это API-контракт для клиента, а не отражение внутренней структуры БД. Проблемы: (1) изменение структуры БД ломает API — миграции базы становятся breaking changes; (2) клиенту экспонируются внутренние детали (технические ID, join-таблицы, внутренние статусы); (3) невозможно оптимизировать схему под клиентские сценарии — например, агрегировать данные из нескольких таблиц в один тип; (4) потенциальная утечка чувствительных данных. Schema должна моделировать домен с точки зрения клиента, а не хранилища.

---

## Ключевые карточки

GraphQL решает две главные проблемы REST API — какие?
?
Over-fetching (сервер возвращает больше данных, чем нужно клиенту) и under-fetching (для связанных данных нужны дополнительные roundtrips). GraphQL позволяет клиенту запросить ровно те поля и связи, которые нужны, в одном запросе.

Что такое N+1 проблема в GraphQL и как DataLoader её решает?
?
N+1 — это когда для списка из N элементов каждый resolver делает отдельный запрос к БД (1 + N запросов). DataLoader собирает все вызовы `.load(id)` за один тик event loop и выполняет один batch-запрос (например, `WHERE id IN (...)`) вместо N отдельных. Дополнительно кэширует результаты в рамках одного запроса.

Чем Persisted Queries отличаются от обычных GraphQL-запросов и зачем они нужны?
?
При Persisted Queries клиент отправляет не текст запроса, а его SHA-256 хеш. Сервер выполняет только предварительно зарегистрированные запросы. Это закрывает возможность отправки произвольных (в том числе вредоносных) запросов и позволяет использовать GET + CDN-кэширование.

Почему поля в GraphQL nullable по умолчанию (без `!`)?
?
Это обеспечивает partial response: если resolver одного поля упал, поле вернёт null и ошибку в массиве errors, но остальные данные ответа доставляются клиенту. В REST аналогичная ошибка привела бы к полному 500. Знак `!` делает поле обязательным, и если оно не может вернуть значение, null «всплывает» к ближайшему nullable родителю.

Что такое Apollo Federation и какую проблему решает?
?
Federation позволяет разделить одну большую GraphQL-схему на независимые subgraphs, которыми владеют разные команды. Apollo Router (Gateway) объединяет subgraphs в единый supergraph. Клиент отправляет один запрос, не зная о разделении, а Router разбивает его на подзапросы к нужным subgraphs.

Какой транспорт рекомендуется для GraphQL Subscriptions в 2025 году?
?
SSE (Server-Sent Events) или Multipart HTTP вместо WebSocket. SSE работает поверх обычного HTTP/2 с мультиплексингом, автоматическим реконнектом и проще масштабируется. WebSocket оправдан только для bidirectional сценариев (чат с typing indicator).

Как работает complexity-based rate limiting в GraphQL?
?
Каждому полю назначается «стоимость» (скаляр — 1, объект — 2, список — multiplier x child_cost). Общая стоимость запроса вычисляется до выполнения. Клиенту выдаётся бюджет (например, 10 000 points/час). Это решает проблему REST-подхода, где один «тяжёлый» GraphQL-запрос стоит столько же, сколько простой.

Чем normalized cache Apollo Client отличается от обычного кэша?
?
Apollo Client разбирает ответ и хранит каждый объект отдельно по ключу `__typename:id`. Если другой запрос вернёт тот же объект с обновлёнными данными, все компоненты, использующие этот объект, автоматически получат обновление без ручной инвалидации.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Обзор | [[architecture-overview]] | Общая карта архитектурных тем и навигация по разделу |
| Следующий шаг | [[api-grpc-deep-dive]] | gRPC для high-performance inter-service communication: бинарный формат, streaming |
| Альтернатива | [[api-rest-deep-dive]] | REST API глубже: constraints Филдинга, HATEOAS, идемпотентность, HTTP-кэширование |
| Современные паттерны | [[api-modern-patterns]] | tRPC, Webhooks, API Gateway, BFF — дополнение к REST/GraphQL/gRPC |
| Кэширование | [[caching-strategies]] | Стратегии кэширования (Redis, CDN, HTTP cache) — слабое место GraphQL |
| Real-time | [[network-realtime-protocols]] | WebSocket, SSE, WebRTC — транспорт для subscriptions глубже |
| Микросервисы | [[microservices-vs-monolith]] | Архитектурный контекст для Federation: когда нужны микросервисы |

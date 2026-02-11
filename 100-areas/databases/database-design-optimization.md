---
title: "Databases: от SELECT * до миллисекундных запросов"
created: 2025-11-24
modified: 2025-11-24
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/databases
  - databases/sql
  - databases/optimization
  - databases/design
  - type/concept
  - level/advanced
related:
  - "[[caching-strategies]]"
  - "[[microservices-vs-monolith]]"
  - "[[api-design]]"
prerequisites:
  - "[[databases-sql-fundamentals]]"
  - "[[databases-transactions-acid]]"
  - "[[databases-nosql-comparison]]"
---

# Databases: от SELECT * до миллисекундных запросов

## TL;DR — Главное за 30 секунд

**Ключевые числа:**
- 1M строк без индекса = **1-5 секунд** → с индексом = **1-5 мс** (1000x разница)
- N+1 проблема: **100 orders → 101 запрос** вместо 2 (JOIN или DataLoader)
- Connection overhead: **20-50ms** на новое соединение → используй пул (HikariCP)

**Что делать прямо сейчас:**
1. **EXPLAIN ANALYZE** — всегда проверяй план выполнения
2. **Индексируй WHERE и JOIN** — но не всё подряд (индексы замедляют INSERT)
3. **Cursor pagination** — WHERE id > last_id, а не OFFSET (OFFSET сканирует всё)
4. **Избегай SELECT *** — выбирай только нужные колонки

**Когда что выбирать:**
- **SQL** — транзакции, связи, сложные запросы
- **NoSQL** — гибкая схема, горизонтальное масштабирование
- **И то, и другое** — Polyglot Persistence (PostgreSQL для заказов + Redis для кэша)

---

## Часть 1: Интуиция без кода

### Аналогия 1: Библиотечный каталог (Индексы)

Представь библиотеку с миллионом книг без каталога:

```
БЕЗ ИНДЕКСА (Full Table Scan):
┌─────────────────────────────────────────────────────────────────┐
│                    БИБЛИОТЕКА                                    │
│  📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚                     │
│  📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚📚                     │
│  ... (1,000,000 книг)                                           │
│                                                                 │
│  "Найди 'Война и мир' Толстого"                                 │
│                                                                 │
│  Библиотекарь: Обхожу КАЖДУЮ полку, проверяю КАЖДУЮ книгу...   │
│  Время: 4 часа                                                  │
└─────────────────────────────────────────────────────────────────┘

С ИНДЕКСОМ (B-Tree = Каталог):
┌─────────────────────────────────────────────────────────────────┐
│  КАТАЛОГ (отсортирован по автору)                               │
│                                                                 │
│               [К-П]                                             │
│           ┌────┴────┐                                           │
│         [К-М]     [Н-П]                                         │
│           │         │                                           │
│      Толстой Л.Н.   ...                                         │
│           │                                                     │
│      "Война и мир" → Полка 47, Ряд 3                           │
│                                                                 │
│  Библиотекарь: Смотрю в каталог → иду на полку 47               │
│  Время: 30 секунд (1000x быстрее!)                              │
└─────────────────────────────────────────────────────────────────┘
```

**НО каталог:**
- Занимает место (нужен шкаф для каталога)
- Требует обновления при добавлении книги
- Не нужен для маленьких библиотек (10 книг найдёшь глазами)

### Аналогия 2: Шкаф с одеждой (Нормализация vs Денормализация)

**Нормализация** — аккуратно разложить по категориям:

```
НОРМАЛИЗОВАННЫЙ ШКАФ:
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  РУБАШКИ    │ │   БРЮКИ     │ │   НОСКИ     │
│  (по цвету) │ │  (по типу)  │ │  (по паре)  │
└─────────────┘ └─────────────┘ └─────────────┘

Плюсы:
• Всё на своём месте (нет дублирования)
• Легко найти конкретную вещь
• Легко обновить (новая рубашка → в свой ящик)

Минусы:
• "Собрать образ" = открыть 3 ящика (JOIN)
• Медленнее для "дай мне полный outfit"
```

**Денормализация** — готовые комплекты:

```
ДЕНОРМАЛИЗОВАННЫЙ ШКАФ:
┌───────────────────────────────────────────────────────┐
│  КОМПЛЕКТ "Офис":     Рубашка белая + Брюки серые    │
│  КОМПЛЕКТ "Спорт":    Футболка чёрная + Шорты синие  │
│  КОМПЛЕКТ "Пляж":     Гавайка + Шорты бежевые        │
└───────────────────────────────────────────────────────┘

Плюсы:
• "Дай outfit" = взял и пошёл (нет JOIN)
• Очень быстро для чтения

Минусы:
• Дублирование (рубашка в 2 комплектах)
• Обновить цвет рубашки = менять в КАЖДОМ комплекте
• Несогласованность если забыл
```

**Правило:** Начни с нормализации, денормализуй только измеренные bottlenecks.

### Аналогия 3: GPS навигатор (EXPLAIN ANALYZE)

EXPLAIN ANALYZE — это как посмотреть маршрут до поездки:

```
EXPLAIN = Показать маршрут БЕЗ поездки:
┌─────────────────────────────────────────────────────────────────┐
│  Маршрут: Дом → Работа                                          │
│  • По Ленина (предположительно 10 мин)                          │
│  • Поворот на Гагарина (предположительно 5 мин)                │
│  • Итого: ~15 минут (оценка)                                    │
│                                                                 │
│  Это ПЛАН, не факт!                                             │
└─────────────────────────────────────────────────────────────────┘

EXPLAIN ANALYZE = Проехать и измерить:
┌─────────────────────────────────────────────────────────────────┐
│  Маршрут: Дом → Работа                                          │
│  • По Ленина (ожидали 10 мин → ФАКТ 25 мин — пробка!)          │
│  • Поворот на Гагарина (ожидали 5 мин → ФАКТ 4 мин)            │
│  • Итого: ФАКТ 29 минут (оценка была 15!)                       │
│                                                                 │
│  Узнали что пробка на Ленина — нужен объезд (INDEX)             │
└─────────────────────────────────────────────────────────────────┘

В SQL:
• Seq Scan = еду через весь город (медленно)
• Index Scan = есть скоростная трасса (быстро)
• Nested Loop = заезжаю за каждым пассажиром отдельно (N+1)
• Hash Join = собрал всех в одной точке, потом везу (efficient)
```

### Аналогия 4: Заказ пиццы (N+1 проблема)

Представь заказ 10 пицц для вечеринки:

```
❌ N+1 ПОДХОД:
┌─────────────────────────────────────────────────────────────────┐
│  Звонок 1: "Какие пиццы есть?" → Получили меню                  │
│  Звонок 2: "Маргарита — какая цена?"                            │
│  Звонок 3: "Пепперони — какая цена?"                            │
│  Звонок 4: "4 сыра — какая цена?"                               │
│  ...                                                            │
│  Звонок 11: "Гавайская — какая цена?"                           │
│                                                                 │
│  ИТОГО: 11 звонков (1 за меню + 10 за цены)                     │
│  Время: 30 минут на телефоне                                    │
└─────────────────────────────────────────────────────────────────┘

✅ ПРАВИЛЬНЫЙ ПОДХОД (JOIN):
┌─────────────────────────────────────────────────────────────────┐
│  Звонок 1: "Дайте меню С ЦЕНАМИ"                                │
│  → Получили всё за 1 звонок                                     │
│                                                                 │
│  ИТОГО: 1 звонок                                                │
│  Время: 3 минуты                                                │
└─────────────────────────────────────────────────────────────────┘

В SQL:
• N+1: SELECT posts; затем для каждого SELECT user WHERE id = ?
• JOIN: SELECT posts JOIN users — всё за 1 запрос
```

### Аналогия 5: Телефонная книга (Cursor vs OFFSET пагинация)

Листаешь старую бумажную телефонную книгу:

```
OFFSET PAGINATION (перелистывание с начала):
┌─────────────────────────────────────────────────────────────────┐
│  "Покажи страницу 500"                                          │
│                                                                 │
│  Библиотекарь:                                                  │
│  1. Открываю на странице 1                                      │
│  2. Листаю: 1, 2, 3, 4, ... 498, 499, 500                       │
│  3. Вот страница 500!                                           │
│                                                                 │
│  Следующий запрос "Страница 501":                               │
│  Опять листаю с начала: 1, 2, 3, ... 501                        │
│                                                                 │
│  Страница 10,000 → листать 10,000 страниц каждый раз!          │
└─────────────────────────────────────────────────────────────────┘

CURSOR PAGINATION (закладка):
┌─────────────────────────────────────────────────────────────────┐
│  "Покажи записи после 'Сидоров'"                                │
│                                                                 │
│  Библиотекарь:                                                  │
│  1. Открываю на букве 'С' (индекс!)                            │
│  2. Нахожу "Сидоров"                                           │
│  3. Показываю следующие 20 записей                              │
│                                                                 │
│  Следующий запрос "после 'Смирнов'":                           │
│  Открываю на 'С', нахожу "Смирнов", показываю следующие 20     │
│                                                                 │
│  Всегда одинаково быстро!                                       │
└─────────────────────────────────────────────────────────────────┘

SQL:
• OFFSET: SELECT * FROM users LIMIT 20 OFFSET 10000 (медленно!)
• Cursor: SELECT * FROM users WHERE id > 12345 LIMIT 20 (быстро!)
```

---

## Часть 2: Почему это сложно

### Ошибка 1: SELECT * везде

**СИМПТОМ:** Все запросы начинаются с `SELECT *`.

```sql
-- ❌ Запрос в коде
SELECT * FROM users WHERE id = 123;

Что происходит:
┌─────────────────────────────────────────────────────────────────┐
│  Таблица users:                                                 │
│  id, email, name, password_hash, avatar (2MB blob!),            │
│  created_at, updated_at, metadata (JSON 50KB), ...             │
│                                                                 │
│  Нужно было: id, email, name                                   │
│  Получили: 2MB данных вместо 200 байт                          │
│                                                                 │
│  × 1000 запросов = 2GB трафика вместо 200KB                    │
└─────────────────────────────────────────────────────────────────┘
```

**РЕШЕНИЕ:**
```sql
-- ✅ Явно указывай колонки
SELECT id, email, name FROM users WHERE id = 123;

-- ✅ Ещё лучше: covering index
CREATE INDEX idx_users_basic ON users(id, email, name);
-- Запрос выполняется ТОЛЬКО по индексу, без чтения таблицы!
```

### Ошибка 2: Индекс на всё подряд

**СИМПТОМ:** "Раз индексы ускоряют — поставим на каждую колонку!"

```
Реальность:
┌─────────────────────────────────────────────────────────────────┐
│  Таблица orders: 10 колонок                                     │
│  Создали: 10 индексов (на каждую колонку)                       │
│                                                                 │
│  При INSERT:                                                    │
│  1. Записать в таблицу                                         │
│  2. Обновить индекс 1                                          │
│  3. Обновить индекс 2                                          │
│  ...                                                           │
│  11. Обновить индекс 10                                        │
│                                                                 │
│  INSERT стал в 10x медленнее!                                   │
│  Диск занят индексами больше чем данными!                       │
└─────────────────────────────────────────────────────────────────┘
```

**РЕШЕНИЕ:**
- Индексируй только колонки в WHERE, JOIN, ORDER BY
- Проверяй использование: `pg_stat_user_indexes`
- Удаляй неиспользуемые индексы

### Ошибка 3: N+1 в ORM

**СИМПТОМ:** ORM делает магию, но страницы загружаются 10 секунд.

```python
# ❌ Lazy loading (N+1 скрыт)
posts = Post.objects.all()[:10]
for post in posts:
    print(post.author.name)  # ЗДЕСЬ СКРЫТЫЙ ЗАПРОС!

# Django ORM сделал:
# 1. SELECT * FROM posts LIMIT 10
# 2. SELECT * FROM users WHERE id = 1
# 3. SELECT * FROM users WHERE id = 2
# ...
# 11. SELECT * FROM users WHERE id = 10

# 11 запросов вместо 1-2!
```

**РЕШЕНИЕ:**
```python
# ✅ Eager loading
posts = Post.objects.select_related('author').all()[:10]
# Django ORM делает: SELECT posts.*, users.* FROM posts JOIN users

# Или prefetch для Many-to-Many
posts = Post.objects.prefetch_related('tags').all()[:10]
# 2 запроса: SELECT posts; SELECT tags WHERE post_id IN (...)
```

### Ошибка 4: OFFSET для глубокой пагинации

**СИМПТОМ:** Первые страницы быстрые, страница 1000 грузится 30 секунд.

```sql
-- Страница 1: OK
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 0;
-- 5ms

-- Страница 1000: ПРОБЛЕМА
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 20000;
-- 30 секунд! PostgreSQL сканирует 20020 строк, возвращает 20
```

**РЕШЕНИЕ:**
```sql
-- ✅ Cursor pagination
-- Вместо номера страницы передаём ID последнего элемента
SELECT * FROM posts
WHERE id < 12345  -- ID последнего поста с предыдущей страницы
ORDER BY id DESC
LIMIT 20;
-- Всегда ~5ms, независимо от "глубины"
```

### Ошибка 5: Функция на индексированной колонке

**СИМПТОМ:** Индекс есть, но не используется.

```sql
-- Есть индекс
CREATE INDEX idx_users_email ON users(email);

-- ❌ Индекс НЕ используется!
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';
-- Seq Scan (проверяет ВСЕ строки)

-- Почему?
-- Индекс построен на email, а мы ищем по LOWER(email)
-- Это разные значения для PostgreSQL!
```

**РЕШЕНИЕ:**
```sql
-- ✅ Функциональный индекс
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Теперь Index Scan работает
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';
```

### Ошибка 6: Новое соединение на каждый запрос

**СИМПТОМ:** Простые запросы занимают 50ms+ даже с индексами.

```
Анатомия запроса БЕЗ connection pool:
┌─────────────────────────────────────────────────────────────────┐
│  1. TCP handshake           ~3ms                                │
│  2. SSL handshake           ~10ms                               │
│  3. PostgreSQL auth         ~5ms                                │
│  4. Выделение ресурсов      ~2ms                                │
│  ─────────────────────────────────                              │
│  Connection overhead:       ~20ms                               │
│                                                                 │
│  5. Выполнение запроса      ~1ms                                │
│  6. Закрытие соединения     ~2ms                                │
│  ─────────────────────────────────                              │
│  ИТОГО:                     ~23ms                               │
│                                                                 │
│  Запрос занимает 1ms, overhead 22ms!                            │
└─────────────────────────────────────────────────────────────────┘
```

**РЕШЕНИЕ:**
```typescript
// ✅ Connection pool
const pool = new Pool({
  max: 20,  // Держим 20 открытых соединений
  idleTimeoutMillis: 30000
});

// Соединение берётся из pool (~0ms)
// Запрос (~1ms)
// Соединение возвращается в pool (~0ms)
// ИТОГО: ~1ms вместо ~23ms
```

---

## Часть 3: Ментальные модели

### Модель 1: Пирамида оптимизации

```
                    ▲
                   ╱ ╲
                  ╱ 5 ╲     5. Денормализация
                 ╱─────╲    (последняя мера)
                ╱   4   ╲   4. Кэширование
               ╱─────────╲  (Redis, мат. views)
              ╱     3     ╲ 3. Query rewrite
             ╱─────────────╲(CTE, subquery → JOIN)
            ╱       2       ╲ 2. Индексы
           ╱─────────────────╲(правильные, не все)
          ╱         1         ╲ 1. EXPLAIN ANALYZE
         ╱─────────────────────╲(найти bottleneck)
        ╱           0           ╲ 0. Правильная схема
       ╱─────────────────────────╲(нормализация с начала)

ПРАВИЛО: Двигайся снизу вверх!
Не прыгай на денормализацию пока не исчерпал нижние уровни.
```

### Модель 2: Дерево решений — нормализация vs денормализация

```
                Соотношение READ / WRITE?
                         │
            ┌────────────┴────────────┐
            │                         │
      WRITE-heavy              READ-heavy
      (50%+ writes)            (90%+ reads)
            │                         │
            ▼                         ▼
      НОРМАЛИЗАЦИЯ            Данные часто меняются?
      (3NF минимум)                   │
                              ┌───────┴───────┐
                              │               │
                            Часто          Редко
                              │               │
                              ▼               ▼
                        НОРМАЛИЗАЦИЯ    ДЕНОРМАЛИЗАЦИЯ
                        + Мат. views    или hybrid
                        + Cache

ПРИМЕРЫ:
• Банк (write-heavy, ACID критичен) → строгая нормализация
• Twitter лента (read 99%, write 1%) → денормализация OK
• E-commerce заказы → нормализация + cached views для dashboards
```

### Модель 3: Index Scan vs Seq Scan — когда что

```
┌─────────────────────────────────────────────────────────────────┐
│                   SELECTIVITY                                    │
│     (% строк, которые вернёт запрос)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   0%                                              100%          │
│   │                                                │           │
│   │    INDEX SCAN             SEQ SCAN            │           │
│   │    быстрее                быстрее              │           │
│   │◀──────────────────▶│◀────────────────────────▶│           │
│   │                    │                          │           │
│   │     < 5-15%        │      > 15-30%            │           │
│   │                    │                          │           │
│   └────────────────────┴──────────────────────────┘           │
│                                                                 │
│  Запрос "email = 'john@ex.com'" → 1 строка из 1M = 0.0001%     │
│  → Index Scan однозначно                                        │
│                                                                 │
│  Запрос "status = 'active'" → 800K из 1M = 80%                 │
│  → Seq Scan быстрее! Индекс не поможет.                        │
│                                                                 │
│  Запрос "created_at > '2025-01-01'" → зависит от данных        │
│  → EXPLAIN ANALYZE покажет что выбрал оптимизатор              │
└─────────────────────────────────────────────────────────────────┘
```

### Модель 4: Query Execution Pipeline

```
SQL запрос проходит этапы:

┌─────────────┐
│   PARSE     │   Проверка синтаксиса
└──────┬──────┘
       ▼
┌─────────────┐
│   ANALYZE   │   Проверка таблиц, колонок, прав
└──────┬──────┘
       ▼
┌─────────────┐
│   REWRITE   │   Применение views, rules, RLS
└──────┬──────┘
       ▼
┌─────────────┐
│   PLAN      │   ← EXPLAIN показывает это
│             │   Выбор индексов, порядка JOIN
└──────┬──────┘
       ▼
┌─────────────┐
│   EXECUTE   │   ← EXPLAIN ANALYZE измеряет это
│             │   Фактическое выполнение
└──────┬──────┘
       ▼
┌─────────────┐
│   RETURN    │   Возврат результата клиенту
└─────────────┘

Что смотреть в EXPLAIN:
• cost — оценка (меньше = лучше)
• rows — сколько строк обработано
• loops — сколько раз выполнялся узел
• actual time — реальное время (только в ANALYZE)
```

### Модель 5: Cost-Benefit анализ индекса

```
СОЗДАВАТЬ ИНДЕКС?

┌─────────────────────────────────────────────────────────────────┐
│                        ВЫГОДА (Benefit)                         │
│                                                                 │
│  • Как часто запрос выполняется?                               │
│    1000 раз/сек → высокая выгода                               │
│    1 раз/день → низкая выгода                                  │
│                                                                 │
│  • Насколько ускорит?                                          │
│    Seq Scan 5s → Index Scan 5ms = 1000x → огромная выгода      │
│    Seq Scan 10ms → Index Scan 5ms = 2x → средняя выгода        │
│                                                                 │
│  • Сколько данных?                                             │
│    1M+ строк → индекс критичен                                 │
│    1000 строк → может не нужен                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        ЦЕНА (Cost)                              │
│                                                                 │
│  • Замедление INSERT/UPDATE/DELETE                             │
│    Write-heavy таблица → высокая цена                          │
│    Read-heavy → низкая цена                                    │
│                                                                 │
│  • Место на диске                                              │
│    B-tree ~ 10-30% от размера таблицы                          │
│    GIN (JSON) может быть больше таблицы!                       │
│                                                                 │
│  • Время создания                                              │
│    1M строк ~ секунды                                          │
│    1B строк ~ часы                                             │
└─────────────────────────────────────────────────────────────────┘

ФОРМУЛА: Benefit > Cost → создавай
         Benefit < Cost → не создавай
         Не уверен → EXPLAIN ANALYZE без и с индексом
```

---

## Терминология

### Индексы

| Термин | Значение |
|--------|----------|
| **Index** | Структура данных для быстрого поиска O(log n) вместо O(n) |
| **B-Tree** | Сбалансированное дерево — default индекс, работает с =, <, >, BETWEEN |
| **Hash Index** | Хэш-таблица — только для = (PostgreSQL: CREATE INDEX USING hash) |
| **GIN** | Generalized Inverted Index — для массивов, JSON, full-text search |
| **GiST** | Generalized Search Tree — для геоданных, диапазонов, нечёткого поиска |
| **Covering Index** | Индекс содержит все нужные колонки — запрос без обращения к таблице |
| **Partial Index** | Индекс с WHERE условием — меньше размер, быстрее для части данных |
| **Full Table Scan** | Seq Scan — перебор всех строк без индекса (плохо для больших таблиц) |

### Нормализация

| Термин | Значение |
|--------|----------|
| **1NF** | Атомарные значения (нет массивов в ячейках) |
| **2NF** | 1NF + нет частичных зависимостей от составного ключа |
| **3NF** | 2NF + нет транзитивных зависимостей (A→B→C) |
| **Denormalization** | Намеренное дублирование данных для ускорения чтения |

### Транзакции

| Термин | Значение |
|--------|----------|
| **Transaction** | Группа операций как единое целое (всё или ничего) |
| **ACID** | Atomicity, Consistency, Isolation, Durability — свойства транзакций |
| **COMMIT** | Зафиксировать транзакцию — изменения становятся постоянными |
| **ROLLBACK** | Откатить транзакцию — отменить все изменения |
| **Isolation Level** | Read Uncommitted → Read Committed → Repeatable Read → Serializable |

### Оптимизация

| Термин | Значение |
|--------|----------|
| **EXPLAIN** | Показывает план выполнения запроса (Seq Scan vs Index Scan) |
| **EXPLAIN ANALYZE** | Выполняет запрос и показывает реальное время |
| **Query Optimizer** | Компонент БД, выбирающий оптимальный план выполнения |
| **N+1 Problem** | 1 запрос + N запросов для связанных данных (классическая ошибка ORM) |
| **Cursor Pagination** | Пагинация через WHERE id > last_id вместо OFFSET (быстрее) |
| **Connection Pool** | Пул переиспользуемых соединений с БД (избегаем overhead создания) |
| **pg_stat_statements** | PostgreSQL extension для статистики по запросам |
| **CONCURRENTLY** | Создание индекса без блокировки таблицы |

### SQL конструкции

| Термин | Значение |
|--------|----------|
| **CTE (WITH)** | Common Table Expression — именованный подзапрос для читаемости |
| **LATERAL** | JOIN с подзапросом, который может ссылаться на внешние колонки |
| **Trigger** | Функция, автоматически вызываемая при INSERT/UPDATE/DELETE |
| **DataLoader** | Библиотека для батчинга N+1 запросов (популярна в GraphQL) |

### Распределённые системы

| Термин | Значение |
|--------|----------|
| **CAP Theorem** | Нельзя одновременно: Consistency + Availability + Partition tolerance |
| **Eventual Consistency** | Данные станут консистентными "в итоге" (не сразу) |
| **Polyglot Persistence** | Использование разных БД для разных задач в одном приложении |
| **Vertical Scaling** | Увеличение мощности одного сервера (CPU, RAM) |
| **Horizontal Scaling** | Добавление серверов (sharding, replication) |

### NoSQL типы

| Термин | Значение |
|--------|----------|
| **Document Store** | MongoDB — хранит JSON документы, гибкая схема |
| **Key-Value** | Redis, DynamoDB — простой get/set, очень быстрый |
| **Column Family** | Cassandra — оптимизирован для записи, time-series |
| **Graph DB** | Neo4j — связи между сущностями (социальные сети) |
| **ElasticSearch** | Full-text search engine, часто используется для логов |

---

## Почему БД тормозит?

```
Типичный сценарий:

День 1: "Работает отлично!"
  • 100 пользователей
  • 1000 записей в БД
  • Все запросы < 50ms

День 180: "Всё падает!"
  • 10,000 пользователей
  • 5,000,000 записей
  • Запросы 5-30 секунд
  • БД CPU 100%

Что пошло не так?
• SELECT * без WHERE
• Нет индексов
• N+1 queries
• Неоптимальные JOIN'ы
• Нет pagination
```

---

## Индексы: поиск за O(log n) вместо O(n)

```
Без индекса (Full Table Scan):

SELECT * FROM users WHERE email = 'john@example.com';

┌─────────────────────────────────────────────────────────────────┐
│ TABLE: users (1,000,000 rows)                                   │
├─────────────────────────────────────────────────────────────────┤
│ id │ email                │ name      │                         │
├────┼──────────────────────┼───────────┼─────────────────────────┤
│ 1  │ alice@example.com    │ Alice     │ ← проверить             │
│ 2  │ bob@example.com      │ Bob       │ ← проверить             │
│ 3  │ carol@example.com    │ Carol     │ ← проверить             │
│ ...│ ...                  │ ...       │ ← проверить все!        │
│ 999│ john@example.com     │ John      │ ← нашли! (но поздно)    │
└─────────────────────────────────────────────────────────────────┘

Время: ~1-5 секунд для 1M строк

──────────────────────────────────────────────────────────────────

С индексом (B-Tree):

CREATE INDEX idx_users_email ON users(email);

┌─────────────────────────────────────────────────────────────────┐
│ INDEX: B-Tree (отсортирован, бинарный поиск)                    │
├─────────────────────────────────────────────────────────────────┤
│                          [j-m]                                  │
│                    ┌──────┴──────┐                              │
│               [a-e]              [n-z]                          │
│            ┌───┴───┐          ┌───┴───┐                         │
│        [a-c]    [d-e]      [n-p]    [q-z]                       │
│         ↓                                                       │
│    john@example.com → row 999                                   │
└─────────────────────────────────────────────────────────────────┘

Время: ~1-5 миллисекунд (1000x быстрее!)

Но:
• Индекс занимает место
• Замедляет INSERT/UPDATE/DELETE
• Выбирай индексы осторожно
```

### Типы индексов

```sql
-- B-Tree индекс (по умолчанию, для большинства случаев)
CREATE INDEX idx_users_email ON users(email);

-- Уникальный индекс (гарантирует уникальность)
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Составной индекс (для нескольких колонок)
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at);
-- Работает для:
--   WHERE user_id = 1
--   WHERE user_id = 1 AND created_at > '2025-01-01'
-- НЕ работает для:
--   WHERE created_at > '2025-01-01' (первая колонка не в WHERE)

-- Частичный индекс (только для части данных)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
-- Меньше места, быстрее для active пользователей

-- Full-text search индекс (PostgreSQL)
-- to_tsvector = преобразует текст в searchable vector (стемминг, стоп-слова)
-- 'english' = языковая конфигурация (есть 'russian', 'simple' и др.)
-- GIN = инвертированный индекс (слово → список документов)
CREATE INDEX idx_posts_content_fts ON posts USING GIN(to_tsvector('english', content));
-- Поиск: WHERE to_tsvector('english', content) @@ to_tsquery('english', 'search')

-- GiST/GIN индекс (для JSON, массивов, геоданных)
CREATE INDEX idx_user_tags ON users USING GIN(tags);
-- WHERE tags @> '["premium"]'
```

### Когда индекс НЕ помогает

```sql
-- Функция на колонке (индекс не используется)
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';
-- Решение: функциональный индекс
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- OR условие (может не использовать индексы)
SELECT * FROM users WHERE email = 'john@ex.com' OR name = 'John';
-- Решение: разделить на два запроса или использовать UNION

-- != или NOT (плохо работает с индексами)
SELECT * FROM users WHERE status != 'deleted';
-- Решение: положительное условие
SELECT * FROM users WHERE status IN ('active', 'pending');

-- LIKE с начальным % (индекс не работает)
SELECT * FROM posts WHERE title LIKE '%search%';
-- Решение: full-text search индекс
```

---

## N+1 проблема: классическая ловушка

```
Сценарий: показать 10 постов с авторами

Плохо (N+1 queries):

// 1. Получаем посты
const posts = await db.query('SELECT * FROM posts LIMIT 10');
// 1 запрос

// 2. Для КАЖДОГО поста получаем автора
for (const post of posts) {
  const author = await db.query(
    'SELECT * FROM users WHERE id = $1',
    [post.user_id]
  );
  post.author = author;
}
// 10 запросов

// ИТОГО: 1 + 10 = 11 запросов
// При 100 постах: 1 + 100 = 101 запрос
// При 1000 постах: 💥

──────────────────────────────────────────────────────────────────

Хорошо (JOIN или IN):

// Вариант 1: JOIN (1 запрос)
const postsWithAuthors = await db.query(`
  SELECT
    posts.*,
    users.name as author_name,
    users.email as author_email
  FROM posts
  JOIN users ON posts.user_id = users.id
  LIMIT 10
`);
// 1 запрос!

// Вариант 2: IN (2 запроса)
const posts = await db.query('SELECT * FROM posts LIMIT 10');
const userIds = posts.map(p => p.user_id);

// ANY($1) — PostgreSQL синтаксис для массивов
// Эквивалент: WHERE id IN (1, 2, 3, ...) но безопасный для массивов
// $1 = [1, 2, 3] → PostgreSQL понимает как массив
const users = await db.query(
  'SELECT * FROM users WHERE id = ANY($1)',
  [userIds]
);
// 2 запроса вместо 11

const usersMap = new Map(users.map(u => [u.id, u]));
posts.forEach(post => {
  post.author = usersMap.get(post.user_id);
});
```

### N+1 в ORM (Sequelize пример)

```javascript
// ❌ ПЛОХО: N+1
const posts = await Post.findAll({ limit: 10 });
for (const post of posts) {
  console.log(post.title, post.User.name); // Lazy loading
}

// ✅ ХОРОШО: Eager loading
const posts = await Post.findAll({
  limit: 10,
  include: [{ model: User, as: 'author' }]
});
// Генерирует JOIN, 1 запрос

// ✅ ХОРОШО: DataLoader (для GraphQL)
import DataLoader from 'dataloader';

const userLoader = new DataLoader(async (userIds) => {
  const users = await User.findAll({
    where: { id: userIds }
  });
  // Возвращаем в том же порядке, что и userIds
  const userMap = new Map(users.map(u => [u.id, u]));
  return userIds.map(id => userMap.get(id));
});

// Использование (батчинг автоматический)
const user1 = await userLoader.load(1);
const user2 = await userLoader.load(2);
const user3 = await userLoader.load(3);
// DataLoader объединяет в 1 запрос: WHERE id IN (1, 2, 3)
```

---

## Нормализация vs Денормализация

```
┌─────────────────────────────────────────────────────────────────┐
│                      НОРМАЛИЗАЦИЯ                               │
│                                                                 │
│  users                      posts                               │
│  ┌──────┬───────┐           ┌──────┬─────────┬─────────┐       │
│  │ id   │ name  │           │ id   │ user_id │ title   │       │
│  ├──────┼───────┤           ├──────┼─────────┼─────────┤       │
│  │ 1    │ John  │◀──────────│ 101  │ 1       │ Post A  │       │
│  │ 2    │ Jane  │◀────┐     │ 102  │ 1       │ Post B  │       │
│  └──────┴───────┘     │     │ 103  │ 2       │ Post C  │       │
│                       └─────│ 104  │ 2       │ Post D  │       │
│                             └──────┴─────────┴─────────┘       │
│                                                                 │
│  Плюсы:                                                         │
│  • Нет дублирования (name хранится 1 раз)                      │
│  • Изменение данных в 1 месте                                  │
│  • Data integrity                                              │
│                                                                 │
│  Минусы:                                                        │
│  • JOIN'ы при чтении (медленнее)                               │
│  • Сложнее запросы                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    ДЕНОРМАЛИЗАЦИЯ                               │
│                                                                 │
│  posts                                                          │
│  ┌──────┬─────────┬─────────┬─────────────┬─────────────┐      │
│  │ id   │ user_id │ title   │ author_name │ author_email│      │
│  ├──────┼─────────┼─────────┼─────────────┼─────────────┤      │
│  │ 101  │ 1       │ Post A  │ John        │ j@ex.com    │      │
│  │ 102  │ 1       │ Post B  │ John        │ j@ex.com    │      │
│  │ 103  │ 2       │ Post C  │ Jane        │ jane@ex.com │      │
│  │ 104  │ 2       │ Post D  │ Jane        │ jane@ex.com │      │
│  └──────┴─────────┴─────────┴─────────────┴─────────────┘      │
│                                                                 │
│  Плюсы:                                                         │
│  • Быстрое чтение (нет JOIN)                                   │
│  • Простые запросы                                             │
│                                                                 │
│  Минусы:                                                        │
│  • Дублирование данных                                         │
│  • Сложность обновления (изменить name нужно везде)            │
│  • Может быть inconsistency                                    │
└─────────────────────────────────────────────────────────────────┘

Когда денормализовать:
• Read >> Write (читают в 100x чаще чем пишут)
• Данные редко меняются (справочники)
• Критична скорость чтения
• Analytics, reporting таблицы
```

### Гибридный подход

```sql
-- Основные таблицы: нормализованы
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  avatar_url TEXT
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  title TEXT,
  content TEXT,
  -- Денормализация для часто читаемых данных
  author_name VARCHAR(255),  -- Дубль из users.name
  author_avatar TEXT,        -- Дубль из users.avatar_url
  created_at TIMESTAMP DEFAULT NOW()
);

-- Trigger для синхронизации
CREATE OR REPLACE FUNCTION sync_author_data()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE posts
  SET
    author_name = NEW.name,
    author_avatar = NEW.avatar_url
  WHERE user_id = NEW.id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_updated
AFTER UPDATE OF name, avatar_url ON users
FOR EACH ROW
EXECUTE FUNCTION sync_author_data();

-- Теперь:
-- • Чтение поста = 1 запрос (без JOIN)
-- • Обновление user.name = автоматическое обновление постов
```

---

## SQL Optimization: практика

### EXPLAIN — рентген запроса

```sql
-- EXPLAIN показывает план выполнения
EXPLAIN ANALYZE
SELECT *
FROM posts
WHERE user_id = 123
ORDER BY created_at DESC
LIMIT 10;

/*
Пример вывода:

Limit  (cost=0.42..1.89 rows=10) (actual time=0.023..0.045 rows=10)
  ->  Index Scan using idx_posts_user_created on posts
      (cost=0.42..147.89 rows=1000) (actual time=0.022..0.042 rows=10)
      Index Cond: (user_id = 123)

Что смотреть:
• cost: оценка стоимости (чем ниже, тем лучше)
• actual time: реальное время выполнения
• rows: сколько строк обработано
• Index Scan vs Seq Scan (Seq Scan = плохо для больших таблиц)
*/

-- ❌ ПЛОХО: Seq Scan
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'john@example.com';
/*
Seq Scan on users (cost=0.00..18334.00 rows=5000)
  Filter: (lower(email) = 'john@example.com'::text)
  Rows Removed by Filter: 995000

→ Проверили ВСЕ строки!
*/

-- ✅ ХОРОШО: Index Scan
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'john@example.com';
/*
Index Scan using idx_users_email_lower on users (cost=0.42..8.44 rows=1)
  Index Cond: (lower(email) = 'john@example.com'::text)

→ Нашли сразу через индекс
*/
```

### Оптимизация JOIN'ов

```sql
-- ❌ ПЛОХО: JOIN большой таблицы без WHERE
SELECT posts.*, users.*
FROM posts
JOIN users ON posts.user_id = users.id;
-- Загружает ВСЕ посты и ВСЕ пользователей

-- ✅ ХОРОШО: WHERE + LIMIT
SELECT posts.*, users.name
FROM posts
JOIN users ON posts.user_id = users.id
WHERE posts.created_at > NOW() - INTERVAL '7 days'
ORDER BY posts.created_at DESC
LIMIT 20;
-- Только недавние посты

-- ❌ ПЛОХО: JOIN в неправильном порядке
SELECT *
FROM small_table
JOIN huge_table ON small_table.id = huge_table.small_id;
-- БД может выбрать неоптимальный план

-- ✅ ХОРОШО: Явная подсказка (если нужно)
SELECT *
FROM small_table
JOIN LATERAL (
  SELECT * FROM huge_table
  WHERE huge_table.small_id = small_table.id
  LIMIT 100
) h ON true;

-- Или материализованное подзапрос
WITH recent_huge AS (
  SELECT * FROM huge_table
  WHERE created_at > NOW() - INTERVAL '1 day'
)
SELECT *
FROM small_table
JOIN recent_huge ON small_table.id = recent_huge.small_id;
```

### Pagination: правильно

```sql
-- ❌ ПЛОХО: OFFSET для больших значений
SELECT * FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;
-- Обрабатывает первые 10020 строк, возвращает последние 20
-- На странице 1000: OFFSET 20000 → катастрофа

-- ✅ ХОРОШО: Cursor-based (keyset pagination)
SELECT * FROM posts
WHERE created_at < '2025-11-24 10:00:00'  -- cursor из предыдущей страницы
ORDER BY created_at DESC
LIMIT 20;
-- Всегда быстро, независимо от страницы

-- Первая страница
SELECT id, created_at, title FROM posts
ORDER BY created_at DESC, id DESC
LIMIT 20;
-- Результат: последняя created_at = '2025-11-24 10:00:00', id = 12345

-- Следующая страница (cursor)
SELECT id, created_at, title FROM posts
WHERE
  created_at < '2025-11-24 10:00:00'
  OR (created_at = '2025-11-24 10:00:00' AND id < 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

---

## SQL vs NoSQL: Polyglot Persistence

```
┌─────────────────────────────────────────────────────────────────┐
│                   SQL (PostgreSQL, MySQL)                       │
├─────────────────────────────────────────────────────────────────┤
│ Плюсы:                                                          │
│ • ACID транзакции                                               │
│ • Сложные JOIN'ы                                                │
│ • Агрегации (SUM, AVG, GROUP BY)                                │
│ • Строгая схема → валидация                                     │
│ • Mature экосистема                                             │
│                                                                 │
│ Минусы:                                                         │
│ • Схема жёсткая (миграции)                                      │
│ • Вертикальное масштабирование сложнее                          │
│ • Может быть медленнее для простого key-value                   │
│                                                                 │
│ Когда использовать:                                             │
│ • Транзакции критичны (банк, e-commerce)                        │
│ • Сложные связи между данными                                   │
│ • Аналитика, отчёты                                             │
│ • Данные структурированы                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              NoSQL: Document Store (MongoDB)                    │
├─────────────────────────────────────────────────────────────────┤
│ Плюсы:                                                          │
│ • Гибкая схема (JSON)                                           │
│ • Горизонтальное масштабирование                                │
│ • Быстрое чтение вложенных данных                               │
│ • Денормализация естественна                                    │
│                                                                 │
│ Минусы:                                                         │
│ • Нет JOIN (делать на клиенте)                                  │
│ • Eventual consistency (в распределённом режиме)                │
│ • Сложные транзакции через коллекции ограничены                 │
│                                                                 │
│ Когда использовать:                                             │
│ • Схема часто меняется                                          │
│ • Документы самодостаточны (профиль пользователя)               │
│ • Высокие write нагрузки                                        │
│ • Масштабирование важнее строгой консистентности                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              NoSQL: Key-Value (Redis, DynamoDB)                 │
├─────────────────────────────────────────────────────────────────┤
│ Плюсы:                                                          │
│ • Экстремально быстро (in-memory)                               │
│ • Простой API (get/set)                                         │
│ • Отличное масштабирование                                      │
│                                                                 │
│ Когда использовать:                                             │
│ • Кэш, сессии                                                   │
│ • Real-time данные                                              │
│ • Счётчики, rate limiting                                       │
└─────────────────────────────────────────────────────────────────┘

Polyglot Persistence — используй разные БД для разных задач:

PostgreSQL:  транзакционные данные (orders, payments)
MongoDB:     user profiles, CMS контент
Redis:       cache, sessions, real-time counters
ElasticSearch: full-text search, logs
```

### Пример Polyglot Persistence

```typescript
// E-commerce приложение

// PostgreSQL — транзакции
class OrderService {
  async createOrder(userId: string, items: CartItem[]) {
    return await postgres.transaction(async (trx) => {
      // Атомарность критична
      const order = await trx('orders').insert({ user_id: userId });
      await trx('order_items').insert(items.map(i => ({ order_id: order.id, ...i })));
      await trx('inventory').decrement('stock', items.map(i => i.quantity));
      return order;
    });
  }
}

// MongoDB — гибкая схема для профилей
class UserProfileService {
  async getProfile(userId: string) {
    return await mongodb.collection('profiles').findOne({ userId });
    // Документ может содержать:
    // { preferences: {}, customFields: {}, metadata: {} }
    // Схема гибкая
  }
}

// Redis — кэш и сессии
class CacheService {
  async getUserData(userId: string) {
    const cached = await redis.get(`user:${userId}`);
    if (cached) return JSON.parse(cached);

    const data = await postgres.query('SELECT * FROM users WHERE id = $1', [userId]);
    await redis.set(`user:${userId}`, JSON.stringify(data), 'EX', 3600);
    return data;
  }
}

// Elasticsearch — поиск по товарам
class SearchService {
  async searchProducts(query: string) {
    return await elasticsearch.search({
      index: 'products',
      body: {
        query: {
          multi_match: {
            query,
            fields: ['title^2', 'description', 'tags']
          }
        }
      }
    });
  }
}
```

---

## Миграции: эволюция схемы без downtime

```sql
-- ❌ ПЛОХО: Breaking change
ALTER TABLE users DROP COLUMN old_field;
-- Если старый код ещё деплоен → ошибки

-- ✅ ХОРОШО: Пошаговая миграция

-- Шаг 1: Добавить новую колонку (nullable)
ALTER TABLE users ADD COLUMN new_field VARCHAR(255);
-- Деплой 1: код поддерживает оба поля

-- Шаг 2: Мигрировать данные
UPDATE users SET new_field = old_field WHERE new_field IS NULL;
-- Можно делать батчами для больших таблиц

-- Шаг 3: Деплой кода, который использует new_field
-- Код перестаёт писать в old_field

-- Шаг 4: Удалить старую колонку
ALTER TABLE users DROP COLUMN old_field;
-- Безопасно: никто уже не использует

-- Для больших таблиц: делать батчами
DO $$
DECLARE
  batch_size INT := 10000;
  updated_rows INT;
BEGIN
  LOOP
    UPDATE users
    SET new_field = old_field
    WHERE id IN (
      SELECT id FROM users
      WHERE new_field IS NULL
      LIMIT batch_size
    );

    GET DIAGNOSTICS updated_rows = ROW_COUNT;
    EXIT WHEN updated_rows = 0;

    RAISE NOTICE 'Migrated % rows', updated_rows;
    COMMIT;  -- Commit каждый batch
    PERFORM pg_sleep(0.1);  -- Небольшая пауза
  END LOOP;
END $$;
```

---

## Подводные камни

### Проблема 1: SELECT *

```sql
-- ❌ ПЛОХО
SELECT * FROM users;

Проблемы:
• Загружаешь ненужные данные (avatar_url, metadata)
• Сеть перегружена
• Код ломается при изменении схемы
• Индексы могут не использоваться

-- ✅ ХОРОШО
SELECT id, email, name FROM users;

Или ещё лучше (covering index):
CREATE INDEX idx_users_list ON users(id, email, name);
-- Запрос выполняется ТОЛЬКО по индексу, без обращения к таблице
```

### Проблема 2: Отсутствие connection pooling

```typescript
// ❌ ПЛОХО: новое соединение для каждого запроса
async function getUser(id: string) {
  const client = await postgres.connect();  // Медленно!
  const user = await client.query('SELECT * FROM users WHERE id = $1', [id]);
  await client.end();
  return user;
}

// ✅ ХОРОШО: connection pool
import { Pool } from 'pg';

const pool = new Pool({
  max: 20,                // Максимум 20 соединений
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

async function getUser(id: string) {
  const result = await pool.query('SELECT * FROM users WHERE id = $1', [id]);
  return result.rows[0];
}
// Соединение переиспользуется
```

### Проблема 3: Транзакции оставлены открытыми

```typescript
// ❌ ПЛОХО: транзакция не закрыта при ошибке
const client = await pool.connect();
try {
  await client.query('BEGIN');
  await client.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
  // Ошибка здесь!
  throw new Error('Something went wrong');
  await client.query('COMMIT');
} catch (error) {
  // ROLLBACK забыли!
  console.error(error);
} finally {
  client.release();  // Соединение с открытой транзакцией вернули в pool!
}

// ✅ ХОРОШО
const client = await pool.connect();
try {
  await client.query('BEGIN');
  await client.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
  await client.query('UPDATE accounts SET balance = balance + 100 WHERE id = 2');
  await client.query('COMMIT');
} catch (error) {
  await client.query('ROLLBACK');  // Откат при ошибке
  throw error;
} finally {
  client.release();
}

// ✅ ЕЩЁ ЛУЧШЕ: wrapper
async function transaction<T>(callback: (client: Client) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await callback(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

// Использование
await transaction(async (client) => {
  await client.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
  await client.query('UPDATE accounts SET balance = balance + 100 WHERE id = 2');
});
```

---

## Actionable

**Чеклист оптимизации:**
```sql
-- 1. Включи query logging (медленные запросы)
-- PostgreSQL: postgresql.conf
log_min_duration_statement = 1000  # Логировать запросы > 1 сек

-- 2. Найди медленные запросы
-- pg_stat_statements — расширение PostgreSQL, собирает статистику по запросам
-- Включить: CREATE EXTENSION pg_stat_statements;
-- + добавить 'pg_stat_statements' в shared_preload_libraries в postgresql.conf
SELECT
  query,              -- Текст запроса (с $1, $2 вместо значений)
  calls,              -- Сколько раз вызывался
  total_time,         -- Общее время выполнения (ms)
  mean_time,          -- Среднее время (total_time / calls)
  max_time            -- Максимальное время выполнения
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- 3. Добавь индексы на WHERE/JOIN колонки
CREATE INDEX CONCURRENTLY idx_table_column ON table(column);
-- CONCURRENTLY = создаёт индекс БЕЗ блокировки таблицы на запись
-- Обычный CREATE INDEX блокирует INSERT/UPDATE на время создания
-- CONCURRENTLY занимает ~2x дольше, но не блокирует production

-- 4. Проверь через EXPLAIN
EXPLAIN ANALYZE SELECT ...;

-- 5. Настрой connection pool
-- Формула: max connections = (core_count * 2) + effective_spindle_count
--   core_count = количество CPU ядер
--   effective_spindle_count = количество HDD дисков (для SSD = 1)
-- Для 4 cores + SSD: max = (4 * 2) + 1 = 9 → округляем до 10-20
-- Больше соединений != быстрее! Конкуренция за CPU и locks
```

**Quick wins:**
```
□ Добавь индексы на foreign keys
□ Используй connection pooling
□ Замени OFFSET на cursor pagination
□ Eager loading вместо N+1
□ SELECT только нужные колонки
□ WHERE перед JOIN для фильтрации
```

---

## Связь с другими темами

[[caching-strategies]] — Кэширование является ключевым дополнением к оптимизации базы данных: правильно настроенный Redis-кэш снимает нагрузку с БД для часто читаемых данных, а cache invalidation стратегии (TTL, write-through, write-behind) определяют консистентность данных. Понимание оптимизации запросов помогает определить, какие данные кэшировать и когда инвалидировать кэш. Рекомендуется изучать параллельно.

[[event-driven-architecture]] — Событийная архитектура решает проблему distributed transactions, которая возникает при масштабировании баз данных: вместо 2PC используются Saga-паттерны, event sourcing и CQRS. Знание оптимизации БД помогает понять, когда нужна денормализация для read-модели (CQRS) и как проектировать event store для производительности.

[[api-design]] — Проектирование API напрямую влияет на нагрузку базы данных: правильная пагинация (cursor vs offset) снижает нагрузку в 10-100x, batch endpoints уменьшают количество запросов, а field selection (GraphQL) позволяет избежать SELECT *. Оптимизация БД и API проектирование — две стороны одной задачи производительности.

[[microservices-vs-monolith]] — Архитектурный выбор между микросервисами и монолитом определяет стратегию работы с базами данных: database per service в микросервисах, shared database в монолите. Оптимизация запросов различается: в монолите — JOIN между таблицами, в микросервисах — API-вызовы и eventual consistency. Знание обоих подходов необходимо для осознанного проектирования.

## Источники и дальнейшее чтение

- Kleppmann M. (2017). *Designing Data-Intensive Applications*. — Главы о storage engines, индексах и query processing дают фундамент для понимания оптимизации. Разделы о партиционировании и репликации объясняют, как масштабировать БД при росте нагрузки.
- Ramakrishnan R., Gehrke J. (2002). *Database Management Systems*. — Академическое описание query optimization (cost-based optimizer, join algorithms, index selection), которое помогает интерпретировать EXPLAIN ANALYZE и проектировать эффективные индексы.
- Petrov A. (2019). *Database Internals*. — Детальный разбор B-Tree, buffer management и concurrency control, который объясняет, почему одни паттерны оптимизации работают, а другие нет, на уровне внутренних механизмов СУБД.

---

**Последняя верификация**: 2025-11-24
**Уровень достоверности**: high

*Обновлено: 2026-01-09 — добавлены педагогические секции (5 аналогий: библиотечный каталог/индексы, шкаф с одеждой/нормализация, GPS/EXPLAIN, пицца/N+1, телефонная книга/pagination; 6 типичных ошибок с решениями; 5 ментальных моделей оптимизации)*

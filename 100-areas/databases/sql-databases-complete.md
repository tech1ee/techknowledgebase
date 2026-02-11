---
title: "SQL Базы данных: PostgreSQL, MySQL, SQLite — Полный гайд"
type: guide
status: published
tags:
  - topic/databases
  - type/guide
  - level/intermediate
related:
  - "[[databases-sql-fundamentals]]"
  - "[[nosql-databases-complete]]"
  - "[[database-internals-complete]]"
prerequisites:
  - "[[databases-sql-fundamentals]]"
  - "[[databases-transactions-acid]]"
---

# SQL Базы данных: PostgreSQL, MySQL, SQLite — Полный гайд

> **Уровень:** Средний → Продвинутый
> **Время изучения:** 6-8 часов
> **Связанные материалы:** [[postgresql-deep-dive]], [[mysql-advanced]], [[sqlite-mobile]]

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Основы баз данных** | Понимание что такое таблицы, ключи, индексы | [[databases-fundamentals-complete]] |
| **Базовый SQL** | SELECT, INSERT, UPDATE, DELETE, JOIN | [[sql-fundamentals]] |
| **ACID и транзакции** | Понимание атомарности и изоляции | [[databases-fundamentals-complete]] |
| **Linux basics** | PostgreSQL/MySQL работают на Linux серверах | Любой курс по Linux |

### Для кого этот материал

| Уровень | Что получите |
|---------|--------------|
| **Junior → Middle** | Window functions, CTEs, оптимизация запросов |
| **Backend разработчик** | Глубокое понимание PostgreSQL vs MySQL vs SQLite |
| **Data Engineer** | Репликация, High Availability, шардинг |

---

## Терминология

> 💡 **Главная аналогия для выбора SQL СУБД:**
>
> **PostgreSQL** = швейцарский армейский нож — может всё, надёжен, но требует настройки
> **MySQL** = молоток — простой, быстрый, делает одно дело хорошо
> **SQLite** = карманный мультитул — всегда с собой, лёгкий, для небольших задач

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **MVCC** | Multi-Version Concurrency Control — параллельный доступ без блокировок | **Копии документа** — каждый читает свою версию, никто никого не блокирует |
| **WAL** | Write-Ahead Logging — запись сначала в лог, потом в данные | **Черновик перед чистовиком** — сначала записал в журнал, потом в книгу |
| **Buffer Pool** | Кэш страниц данных в RAM | **Рабочий стол** — часто используемые документы под рукой |
| **Query Planner** | Оптимизатор запросов — выбирает лучший план | **Навигатор** — выбирает маршрут с минимальным временем |
| **EXPLAIN ANALYZE** | Показывает план выполнения с реальным временем | **Таймер маршрута** — сколько реально заняла каждая часть пути |
| **Window Function** | Вычисление по "окну" строк без группировки | **Скользящее среднее** — среднее за последние N дней |
| **CTE** | Common Table Expression — именованный подзапрос | **Промежуточная переменная** — результат подзапроса с именем |
| **Isolation Level** | Степень изоляции транзакций друг от друга | **Уровень тишины в офисе** — от опенспейса до отдельного кабинета |
| **Replication** | Копирование данных на другой сервер | **Резервная копия в реальном времени** — второй экземпляр всегда актуален |
| **Sharding** | Разделение данных по серверам | **Разделение библиотеки по этажам** — книги A-M на 1-м, N-Z на 2-м |
| **Connection Pooling** | Переиспользование соединений | **Общий телефон в офисе** — не у каждого свой, а один на отдел |
| **Stored Procedure** | Код на SQL, хранящийся в БД | **Макрос в Excel** — готовая функция, вызываемая по имени |
| **Extension** | Расширение функциональности (PostGIS, pgvector) | **Плагин в браузере** — добавляет новые возможности |

---

## Содержание

1. [Обзор и сравнение](#обзор-и-сравнение)
2. [PostgreSQL Deep Dive](#postgresql-deep-dive)
3. [MySQL Deep Dive](#mysql-deep-dive)
4. [SQLite Deep Dive](#sqlite-deep-dive)
5. [SQL Advanced: Window Functions](#sql-advanced-window-functions)
6. [SQL Advanced: CTEs и рекурсия](#sql-advanced-ctes-и-рекурсия)
7. [Оптимизация запросов](#оптимизация-запросов)
8. [Транзакции и Isolation Levels](#транзакции-и-isolation-levels)
9. [Репликация и High Availability](#репликация-и-high-availability)
10. [Практические задания](#практические-задания)

---

## Обзор и сравнение

### Три главные SQL СУБД

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL vs MySQL vs SQLite                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐                                               │
│  │   PostgreSQL     │  "The World's Most Advanced Open Source      │
│  │                  │   Relational Database"                        │
│  │   🐘             │                                               │
│  │                  │  ✓ Enterprise-grade                           │
│  │                  │  ✓ ACID + Extensions                          │
│  │                  │  ✓ Complex queries                            │
│  │                  │  ✓ Market leader 2024                         │
│  └──────────────────┘                                               │
│                                                                     │
│  ┌──────────────────┐                                               │
│  │     MySQL        │  "The World's Most Popular Open Source       │
│  │                  │   Database"                                   │
│  │   🐬             │                                               │
│  │                  │  ✓ Web applications                           │
│  │                  │  ✓ Read-heavy workloads                       │
│  │                  │  ✓ Simple and fast                            │
│  │                  │  ✓ Wide hosting support                       │
│  └──────────────────┘                                               │
│                                                                     │
│  ┌──────────────────┐                                               │
│  │     SQLite       │  "A small, fast, self-contained, full-featured│
│  │                  │   SQL database engine"                        │
│  │   🪶             │                                               │
│  │                  │  ✓ Embedded/serverless                        │
│  │                  │  ✓ Mobile apps                                │
│  │                  │  ✓ Zero configuration                         │
│  │                  │  ✓ Single file                                │
│  └──────────────────┘                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Детальное сравнение

```
┌────────────────────┬─────────────────┬─────────────────┬─────────────────┐
│     Критерий       │   PostgreSQL    │      MySQL      │     SQLite      │
├────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Архитектура        │ Client-Server   │ Client-Server   │ Embedded        │
│ Процесс            │ Multi-process   │ Multi-thread    │ In-process      │
│ Установка          │ Server setup    │ Server setup    │ Zero config     │
│ Storage            │ Multiple files  │ Multiple files  │ Single file     │
├────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Max DB size        │ Unlimited       │ Unlimited       │ 281 TB          │
│ Max row size       │ 1.6 TB          │ 65 KB (InnoDB)  │ 1 GB            │
│ Concurrent writes  │ Full MVCC       │ Full (InnoDB)   │ Single writer   │
│ Concurrent reads   │ Unlimited       │ Unlimited       │ Unlimited       │
├────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ SQL Compliance     │ Strict          │ Partial         │ Partial         │
│ FULL OUTER JOIN    │ ✓               │ ✗ (workaround)  │ ✗               │
│ RIGHT JOIN         │ ✓               │ ✓               │ ✗               │
│ Window Functions   │ ✓ (полные)      │ ✓ (MySQL 8.0+)  │ ✓ (3.25+)       │
│ CTEs               │ ✓ (+ recursive) │ ✓ (MySQL 8.0+)  │ ✓ (3.8.3+)      │
├────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ JSONB/JSON         │ ✓ JSONB (binary)│ ✓ JSON          │ ✗ (text only)   │
│ Arrays             │ ✓ Native        │ ✗               │ ✗               │
│ Enums              │ ✓               │ ✓               │ ✗               │
│ Full-text search   │ ✓ Built-in      │ ✓ Built-in      │ ✓ FTS5          │
├────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Extensions         │ ✓ Rich ecosystem│ Limited         │ ✗               │
│ Stored procedures  │ ✓ PL/pgSQL+     │ ✓               │ ✗               │
│ Triggers           │ ✓               │ ✓               │ ✓               │
│ Views              │ ✓ + Materialized│ ✓               │ ✓               │
├────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Default isolation  │ READ COMMITTED  │ REPEATABLE READ │ SERIALIZABLE    │
│ MVCC               │ ✓               │ ✓ (InnoDB)      │ ✗               │
│ WAL                │ ✓               │ Redo log        │ ✓ (optional)    │
├────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Replication        │ Streaming, Logic│ Binlog, Group   │ ✗               │
│ Sharding           │ Citus extension │ MySQL Cluster   │ ✗               │
│ Cloud-native       │ ✓               │ ✓               │ ✗               │
├────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Market share 2025  │ 17.1%           │ 9.4%            │ 5.4%            │
│ License            │ PostgreSQL (MIT)│ GPL/Commercial  │ Public Domain   │
└────────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### Дерево выбора

```
                         ЧТО СТРОИМ?
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    Mobile/Desktop       Web Application      Enterprise/
    Embedded System                           Analytics
         │                    │                    │
         ▼                    │                    ▼
      SQLite                  │               PostgreSQL
                              │
                     ┌────────┴────────┐
                     │                 │
               Read-heavy         Complex queries
               Simple CRUD        Mixed workload
                     │                 │
                     ▼                 ▼
                   MySQL          PostgreSQL

Конкретные use cases:

SQLite:
├── iOS/Android apps
├── Electron desktop apps
├── IoT/embedded devices
├── Browser (WebSQL, IndexedDB fallback)
├── Prototyping
└── Websites < 100K hits/day

MySQL:
├── WordPress, Drupal, Joomla
├── E-commerce (Magento, WooCommerce)
├── Simple CRUD APIs
├── Shared hosting environments
└── Read-heavy workloads

PostgreSQL:
├── Financial/banking systems
├── Geospatial (PostGIS)
├── AI/ML (pgvector)
├── Time-series (TimescaleDB)
├── Complex analytics
├── JSON + relational hybrid
└── Enterprise applications
```

---

## PostgreSQL Deep Dive

### Архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PostgreSQL Architecture                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Client Applications                                               │
│        │ │ │                                                        │
│        ▼ ▼ ▼                                                        │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Postmaster (Main Process)                │   │
│   │                    Listens on port 5432                     │   │
│   └─────────────────────────────────────────────────────────────┘   │
│        │                                                            │
│        │ fork()                                                     │
│        ▼                                                            │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              Backend Processes (per connection)             │   │
│   │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │   │
│   │   │Backend 1│ │Backend 2│ │Backend 3│ │Backend N│           │   │
│   │   └─────────┘ └─────────┘ └─────────┘ └─────────┘           │   │
│   └─────────────────────────────────────────────────────────────┘   │
│        │                                                            │
│        ▼                                                            │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Shared Memory                            │   │
│   │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │   │
│   │   │ Shared Buffer│ │  WAL Buffer  │ │  Lock Table  │        │   │
│   │   │    Pool      │ │              │ │              │        │   │
│   │   └──────────────┘ └──────────────┘ └──────────────┘        │   │
│   └─────────────────────────────────────────────────────────────┘   │
│        │                                                            │
│        ▼                                                            │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                 Background Workers                          │   │
│   │   ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐   │   │
│   │   │Autovacuum │ │ WAL Writer│ │Checkpointer│ │ BG Writer │   │   │
│   │   └───────────┘ └───────────┘ └───────────┘ └───────────┘   │   │
│   │   ┌───────────┐ ┌───────────┐                               │   │
│   │   │Stats Coll.│ │ Archiver  │                               │   │
│   │   └───────────┘ └───────────┘                               │   │
│   └─────────────────────────────────────────────────────────────┘   │
│        │                                                            │
│        ▼                                                            │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Disk Storage                             │   │
│   │   ┌────────────┐ ┌────────────┐ ┌────────────┐              │   │
│   │   │ Data Files │ │  WAL Files │ │ CLOG, etc. │              │   │
│   │   │ (base/)    │ │ (pg_wal/)  │ │            │              │   │
│   │   └────────────┘ └────────────┘ └────────────┘              │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### JSONB — JSON Binary

```sql
-- ═══════════════════════════════════════════════════════════════
-- СОЗДАНИЕ ТАБЛИЦЫ С JSONB
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    attributes JSONB DEFAULT '{}',  -- JSONB колонка
    created_at TIMESTAMP DEFAULT NOW()
);

-- WHY JSONB vs JSON:
-- JSONB хранит в бинарном формате → быстрее запросы
-- JSONB поддерживает индексы → O(log n) поиск
-- JSONB удаляет дубликаты ключей
-- JSON сохраняет порядок ключей (редко нужно)


-- ═══════════════════════════════════════════════════════════════
-- ВСТАВКА JSONB ДАННЫХ
-- ═══════════════════════════════════════════════════════════════

INSERT INTO products (name, attributes) VALUES
('iPhone 15 Pro', '{
    "brand": "Apple",
    "colors": ["black", "white", "gold"],
    "specs": {
        "storage": 256,
        "ram": 8,
        "screen": 6.1
    },
    "price": 999.99,
    "in_stock": true
}'),
('Samsung Galaxy S24', '{
    "brand": "Samsung",
    "colors": ["black", "purple"],
    "specs": {
        "storage": 128,
        "ram": 8,
        "screen": 6.2
    },
    "price": 799.99,
    "in_stock": true
}');


-- ═══════════════════════════════════════════════════════════════
-- ЗАПРОСЫ К JSONB
-- ═══════════════════════════════════════════════════════════════

-- Получить значение по ключу (как JSON)
SELECT attributes->'brand' FROM products;
-- Результат: "Apple" (с кавычками)

-- Получить значение как текст
SELECT attributes->>'brand' FROM products;
-- Результат: Apple (без кавычек)

-- Вложенный доступ
SELECT attributes->'specs'->>'storage' FROM products;
-- Результат: 256

-- Доступ по пути (PostgreSQL 14+)
SELECT attributes['specs']['storage'] FROM products;

-- Проверка существования ключа
SELECT * FROM products WHERE attributes ? 'brand';

-- Проверка значения
SELECT * FROM products
WHERE attributes->>'brand' = 'Apple';

-- Проверка вложенного значения
SELECT * FROM products
WHERE (attributes->'specs'->>'storage')::int > 128;

-- Содержит ли JSONB определённую структуру (@>)
SELECT * FROM products
WHERE attributes @> '{"brand": "Apple"}';

-- Поиск в массиве
SELECT * FROM products
WHERE attributes->'colors' ? 'black';


-- ═══════════════════════════════════════════════════════════════
-- JSONB ИНДЕКСЫ
-- ═══════════════════════════════════════════════════════════════

-- GIN индекс для всех операций
CREATE INDEX idx_products_attrs ON products USING GIN (attributes);

-- Индекс на конкретный путь
CREATE INDEX idx_products_brand
ON products ((attributes->>'brand'));

-- Индекс для jsonb_path_ops (только @>)
CREATE INDEX idx_products_attrs_path
ON products USING GIN (attributes jsonb_path_ops);

-- WHY GIN:
-- GIN (Generalized Inverted Index) оптимален для:
-- - Полнотекстовый поиск
-- - JSONB ключи/значения
-- - Массивы
-- До 80% ускорение запросов


-- ═══════════════════════════════════════════════════════════════
-- ОБНОВЛЕНИЕ JSONB
-- ═══════════════════════════════════════════════════════════════

-- Добавить/обновить ключ
UPDATE products
SET attributes = attributes || '{"discount": 10}'
WHERE id = 1;

-- Удалить ключ
UPDATE products
SET attributes = attributes - 'discount'
WHERE id = 1;

-- Обновить вложенное значение
UPDATE products
SET attributes = jsonb_set(
    attributes,
    '{specs,storage}',
    '512'
)
WHERE id = 1;


-- ═══════════════════════════════════════════════════════════════
-- АГРЕГАЦИИ С JSONB
-- ═══════════════════════════════════════════════════════════════

-- Группировка по JSONB полю
SELECT
    attributes->>'brand' as brand,
    COUNT(*) as count,
    AVG((attributes->>'price')::numeric) as avg_price
FROM products
GROUP BY attributes->>'brand';

-- Развернуть массив
SELECT
    name,
    jsonb_array_elements_text(attributes->'colors') as color
FROM products;
```

### PostgreSQL Extensions

```sql
-- ═══════════════════════════════════════════════════════════════
-- PostGIS — Геопространственные данные
-- ═══════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geom GEOMETRY(Point, 4326)  -- WGS84 координаты
);

-- Вставка точки (долгота, широта)
INSERT INTO locations (name, geom)
VALUES ('Кремль', ST_SetSRID(ST_MakePoint(37.6173, 55.7520), 4326));

-- Найти места в радиусе 5 км
SELECT name, ST_Distance(
    geom::geography,
    ST_SetSRID(ST_MakePoint(37.6, 55.75), 4326)::geography
) as distance_m
FROM locations
WHERE ST_DWithin(
    geom::geography,
    ST_SetSRID(ST_MakePoint(37.6, 55.75), 4326)::geography,
    5000  -- 5000 метров
)
ORDER BY distance_m;


-- ═══════════════════════════════════════════════════════════════
-- pgvector — AI/ML Embeddings
-- ═══════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)  -- OpenAI ada-002 dimensions
);

-- Создание индекса для ANN поиска
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Семантический поиск (k-NN)
SELECT content, 1 - (embedding <=> '[0.1, 0.2, ...]') as similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'  -- cosine distance
LIMIT 5;

-- WHY pgvector:
-- RAG (Retrieval Augmented Generation) для LLM
-- Semantic search вместо keyword search
-- Recommendation systems
-- Image similarity


-- ═══════════════════════════════════════════════════════════════
-- TimescaleDB — Time-Series
-- ═══════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    temperature FLOAT,
    humidity FLOAT
);

-- Преобразовать в hypertable
SELECT create_hypertable('metrics', 'time');

-- Автоматическая компрессия старых данных
ALTER TABLE metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id'
);

SELECT add_compression_policy('metrics', INTERVAL '7 days');

-- Continuous aggregates (материализованные агрегаты)
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    AVG(temperature) as avg_temp,
    MAX(temperature) as max_temp
FROM metrics
GROUP BY bucket, device_id;
```

### VACUUM и Maintenance

```sql
-- ═══════════════════════════════════════════════════════════════
-- VACUUM — Очистка мёртвых строк
-- ═══════════════════════════════════════════════════════════════

-- WHY нужен VACUUM:
-- PostgreSQL использует MVCC (Multi-Version Concurrency Control)
-- При UPDATE/DELETE старые версии строк остаются (dead tuples)
-- VACUUM освобождает место для повторного использования

-- Обычный VACUUM (не блокирует таблицу)
VACUUM table_name;

-- VACUUM с анализом статистики
VACUUM ANALYZE table_name;

-- VACUUM FULL — переписывает всю таблицу (блокирует!)
-- Использовать ТОЛЬКО при высоком bloat
VACUUM FULL table_name;

-- Проверить bloat
SELECT
    relname as table_name,
    n_dead_tup as dead_tuples,
    n_live_tup as live_tuples,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;


-- ═══════════════════════════════════════════════════════════════
-- AUTOVACUUM — Автоматическая очистка
-- ═══════════════════════════════════════════════════════════════

-- Проверить настройки
SHOW autovacuum;
SHOW autovacuum_vacuum_threshold;      -- 50 (minimum dead tuples)
SHOW autovacuum_vacuum_scale_factor;   -- 0.2 (20% of table)

-- Формула: vacuum when dead_tuples > threshold + scale_factor * table_rows

-- Настройка для конкретной таблицы (высокая активность)
ALTER TABLE high_activity_table SET (
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_scale_factor = 0.1,  -- 10%
    autovacuum_analyze_threshold = 50,
    autovacuum_analyze_scale_factor = 0.05
);


-- ═══════════════════════════════════════════════════════════════
-- ANALYZE — Обновление статистики
-- ═══════════════════════════════════════════════════════════════

-- Обновить статистику для оптимизатора
ANALYZE table_name;

-- Статистика по колонке
ANALYZE table_name (column_name);

-- WHY ANALYZE важен:
-- Query planner использует статистику для выбора плана
-- Устаревшая статистика → плохие планы → медленные запросы


-- ═══════════════════════════════════════════════════════════════
-- REINDEX — Перестроение индексов
-- ═══════════════════════════════════════════════════════════════

-- Перестроить один индекс
REINDEX INDEX idx_name;

-- Перестроить все индексы таблицы
REINDEX TABLE table_name;

-- PostgreSQL 12+: CONCURRENTLY (без блокировки)
REINDEX INDEX CONCURRENTLY idx_name;
```

---

## MySQL Deep Dive

### Архитектура InnoDB

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MySQL InnoDB Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                      MySQL Server                           │   │
│   │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │   │
│   │   │   Parser     │ │  Optimizer   │ │   Executor   │        │   │
│   │   └──────────────┘ └──────────────┘ └──────────────┘        │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    InnoDB Storage Engine                    │   │
│   │                                                             │   │
│   │   IN-MEMORY STRUCTURES:                                     │   │
│   │   ┌────────────────────────────────────────────────────┐    │   │
│   │   │              Buffer Pool (up to 80% RAM)           │    │   │
│   │   │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │    │   │
│   │   │   │ Data Pages  │ │Index Pages  │ │ Change Buf  │  │    │   │
│   │   │   └─────────────┘ └─────────────┘ └─────────────┘  │    │   │
│   │   └────────────────────────────────────────────────────┘    │   │
│   │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │   │
│   │   │  Log Buffer │ │ Adaptive    │ │ Lock System │           │   │
│   │   │             │ │ Hash Index  │ │             │           │   │
│   │   └─────────────┘ └─────────────┘ └─────────────┘           │   │
│   │                                                             │   │
│   │   ON-DISK STRUCTURES:                                       │   │
│   │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │   │
│   │   │  Redo Log   │ │  Undo Log   │ │ Tablespace  │           │   │
│   │   │ (Crash Rec.)│ │ (Rollback)  │ │ (.ibd files)│           │   │
│   │   └─────────────┘ └─────────────┘ └─────────────┘           │   │
│   │   ┌─────────────┐ ┌─────────────┐                           │   │
│   │   │ System Tbsp │ │ Doublewrite │                           │   │
│   │   │ (ibdata1)   │ │   Buffer    │                           │   │
│   │   └─────────────┘ └─────────────┘                           │   │
│   │                                                             │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Buffer Pool

```sql
-- ═══════════════════════════════════════════════════════════════
-- BUFFER POOL — Кэш данных в памяти
-- ═══════════════════════════════════════════════════════════════

-- Проверить текущий размер
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- Рекомендация: 70-80% RAM для dedicated MySQL server
-- Например, для 16GB RAM:
SET GLOBAL innodb_buffer_pool_size = 12884901888;  -- 12GB

-- Проверить статистику buffer pool
SHOW ENGINE INNODB STATUS\G

-- Посмотреть hit ratio
SELECT
    (1 - (
        Innodb_buffer_pool_reads /
        Innodb_buffer_pool_read_requests
    )) * 100 as buffer_pool_hit_ratio
FROM (
    SELECT
        VARIABLE_VALUE as Innodb_buffer_pool_reads
    FROM performance_schema.global_status
    WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads'
) reads,
(
    SELECT
        VARIABLE_VALUE as Innodb_buffer_pool_read_requests
    FROM performance_schema.global_status
    WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests'
) requests;

-- Хороший hit ratio: > 99%
```

### MySQL 8.0+ Features

```sql
-- ═══════════════════════════════════════════════════════════════
-- WINDOW FUNCTIONS (MySQL 8.0+)
-- ═══════════════════════════════════════════════════════════════

-- Ранжирование
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank_in_dept,
    RANK() OVER (ORDER BY salary DESC) as overall_rank
FROM employees;

-- Running total
SELECT
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) as running_total
FROM orders;


-- ═══════════════════════════════════════════════════════════════
-- CTEs (MySQL 8.0+)
-- ═══════════════════════════════════════════════════════════════

-- Simple CTE
WITH high_value_customers AS (
    SELECT customer_id, SUM(amount) as total
    FROM orders
    GROUP BY customer_id
    HAVING SUM(amount) > 10000
)
SELECT c.name, h.total
FROM customers c
JOIN high_value_customers h ON c.id = h.customer_id;

-- Recursive CTE (иерархия)
WITH RECURSIVE category_tree AS (
    -- Base case
    SELECT id, name, parent_id, 0 as level
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY level, name;


-- ═══════════════════════════════════════════════════════════════
-- INVISIBLE INDEXES (MySQL 8.0+)
-- ═══════════════════════════════════════════════════════════════

-- Сделать индекс невидимым для оптимизатора
ALTER TABLE products ALTER INDEX idx_price INVISIBLE;

-- WHY: Тестирование влияния индекса без его удаления
-- Если производительность упала → вернуть
ALTER TABLE products ALTER INDEX idx_price VISIBLE;


-- ═══════════════════════════════════════════════════════════════
-- JSON FUNCTIONS (MySQL 8.0+)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    details JSON
);

INSERT INTO products VALUES
(1, 'Phone', '{"brand": "Apple", "storage": 256}');

-- Извлечение значения
SELECT JSON_EXTRACT(details, '$.brand') as brand FROM products;
-- Или сокращённо:
SELECT details->'$.brand' FROM products;

-- Как текст (без кавычек)
SELECT details->>'$.brand' FROM products;

-- Поиск по JSON
SELECT * FROM products
WHERE JSON_EXTRACT(details, '$.storage') > 128;

-- Обновление JSON
UPDATE products
SET details = JSON_SET(details, '$.color', 'black')
WHERE id = 1;
```

---

## SQLite Deep Dive

### Архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SQLite Architecture                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Application Process                                               │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    SQLite Library                           │   │
│   │   ┌──────────────────────────────────────────────────────┐  │   │
│   │   │              SQL Compiler                            │  │   │
│   │   │   ┌─────────┐ ┌─────────┐ ┌─────────────────────┐    │  │   │
│   │   │   │ Tokenizer│ │ Parser │ │ Code Generator      │    │  │   │
│   │   │   └─────────┘ └─────────┘ └─────────────────────┘    │  │   │
│   │   └──────────────────────────────────────────────────────┘  │   │
│   │   ┌──────────────────────────────────────────────────────┐  │   │
│   │   │           Virtual Machine (VDBE)                     │  │   │
│   │   │   Executes bytecode generated by compiler            │  │   │
│   │   └──────────────────────────────────────────────────────┘  │   │
│   │   ┌──────────────────────────────────────────────────────┐  │   │
│   │   │                B-Tree Module                         │  │   │
│   │   │   ┌─────────────────┐ ┌─────────────────┐            │  │   │
│   │   │   │ Table B-Trees   │ │ Index B-Trees   │            │  │   │
│   │   │   └─────────────────┘ └─────────────────┘            │  │   │
│   │   └──────────────────────────────────────────────────────┘  │   │
│   │   ┌──────────────────────────────────────────────────────┐  │   │
│   │   │                   Pager                              │  │   │
│   │   │   ┌─────────────────┐ ┌─────────────────┐            │  │   │
│   │   │   │ Page Cache      │ │ Journal/WAL     │            │  │   │
│   │   │   └─────────────────┘ └─────────────────┘            │  │   │
│   │   └──────────────────────────────────────────────────────┘  │   │
│   │   ┌──────────────────────────────────────────────────────┐  │   │
│   │   │              OS Interface (VFS)                      │  │   │
│   │   └──────────────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                   Single Database File                      │   │
│   │                      (.db / .sqlite)                        │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### WAL Mode — Критическая оптимизация

```sql
-- ═══════════════════════════════════════════════════════════════
-- WAL MODE — Write-Ahead Logging
-- ═══════════════════════════════════════════════════════════════

-- Проверить текущий режим
PRAGMA journal_mode;

-- Включить WAL (необратимо в рамках соединения)
PRAGMA journal_mode = WAL;

-- WHY WAL:
-- Rollback mode: Lock всей БД при записи
-- WAL mode: Reads не блокируются writes

-- Сравнение производительности:
-- Rollback: ~500 writes/sec
-- WAL: ~3,600 writes/sec (7x faster!)


-- ═══════════════════════════════════════════════════════════════
-- ПОЛНАЯ ОПТИМИЗАЦИЯ SQLite
-- ═══════════════════════════════════════════════════════════════

-- Выполнить при каждом подключении:
PRAGMA journal_mode = WAL;           -- Включить WAL
PRAGMA synchronous = NORMAL;         -- Быстрее, всё ещё безопасно
PRAGMA temp_store = MEMORY;          -- Temp таблицы в RAM
PRAGMA mmap_size = 30000000000;      -- Memory-mapped I/O (30GB)
PRAGMA cache_size = -64000;          -- 64MB page cache

-- SYNCHRONOUS levels:
-- FULL (default): fsync после каждой транзакции (медленно, безопасно)
-- NORMAL: fsync только на checkpoints (быстро, безопасно в WAL)
-- OFF: нет fsync (очень быстро, риск потери данных при crash)


-- ═══════════════════════════════════════════════════════════════
-- BUSY TIMEOUT — Ожидание при блокировке
-- ═══════════════════════════════════════════════════════════════

-- SQLite позволяет только одного writer'а
-- При конфликте — ждать до 5 секунд
PRAGMA busy_timeout = 5000;

-- Альтернатива: обработка SQLITE_BUSY в коде


-- ═══════════════════════════════════════════════════════════════
-- VACUUM — Дефрагментация
-- ═══════════════════════════════════════════════════════════════

-- Перестроить базу данных (уменьшить размер файла)
VACUUM;

-- WHY: После DELETE место не освобождается автоматически
-- VACUUM переписывает всю БД

-- Auto-vacuum (при создании БД)
PRAGMA auto_vacuum = INCREMENTAL;


-- ═══════════════════════════════════════════════════════════════
-- ANALYZE — Статистика для оптимизатора
-- ═══════════════════════════════════════════════════════════════

ANALYZE;  -- Обновить статистику всех таблиц

-- Проверить план запроса
EXPLAIN QUERY PLAN
SELECT * FROM users WHERE email = 'test@example.com';
```

### SQLite на Android (Room)

```kotlin
// ═══════════════════════════════════════════════════════════════
// ROOM DATABASE С ОПТИМИЗАЦИЯМИ
// ═══════════════════════════════════════════════════════════════

@Database(
    entities = [User::class, Order::class],
    version = 1
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun orderDao(): OrderDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                // WHY: Room по умолчанию включает WAL на API 16+
                // .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING)

                // Callback для оптимизаций
                .addCallback(object : RoomDatabase.Callback() {
                    override fun onOpen(db: SupportSQLiteDatabase) {
                        super.onOpen(db)
                        // Дополнительные PRAGMAs
                        db.execSQL("PRAGMA temp_store = MEMORY")
                        db.execSQL("PRAGMA cache_size = -8000") // 8MB
                    }
                })
                .build()

                INSTANCE = instance
                instance
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════
// DAO С ОПТИМИЗИРОВАННЫМИ ЗАПРОСАМИ
// ═══════════════════════════════════════════════════════════════

@Dao
interface UserDao {
    // Используй индексы в WHERE
    @Query("SELECT * FROM users WHERE email = :email")
    suspend fun findByEmail(email: String): User?

    // Batch insert (одна транзакция)
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(users: List<User>)

    // Пагинация с Room Paging
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAllPaged(): PagingSource<Int, User>

    // Избегай SELECT * для больших таблиц
    @Query("SELECT id, name, email FROM users")
    fun getAllBasic(): Flow<List<UserBasic>>
}

// ═══════════════════════════════════════════════════════════════
// ИНДЕКСЫ В ENTITY
// ═══════════════════════════════════════════════════════════════

@Entity(
    tableName = "users",
    indices = [
        Index(value = ["email"], unique = true),
        Index(value = ["created_at"]),
        // Composite index для частых запросов
        Index(value = ["status", "created_at"])
    ]
)
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String,
    @ColumnInfo(name = "email")
    val email: String,
    @ColumnInfo(name = "status")
    val status: String = "active",
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
)
```

---

## SQL Advanced: Window Functions

### Обзор Window Functions

```sql
-- ═══════════════════════════════════════════════════════════════
-- ЧТО ТАКОЕ WINDOW FUNCTIONS
-- ═══════════════════════════════════════════════════════════════

-- Window Functions выполняют вычисления над "окном" (набором строк)
-- В отличие от GROUP BY, не схлопывают строки

-- Синтаксис:
-- function_name(args) OVER (
--     [PARTITION BY columns]  -- Группировка
--     [ORDER BY columns]      -- Порядок
--     [frame_clause]          -- Границы окна
-- )


-- ═══════════════════════════════════════════════════════════════
-- RANKING FUNCTIONS
-- ═══════════════════════════════════════════════════════════════

-- Таблица employees:
-- | id | name    | department | salary |
-- |----|---------|------------|--------|
-- | 1  | Alice   | Sales      | 5000   |
-- | 2  | Bob     | Sales      | 5000   |
-- | 3  | Charlie | Sales      | 6000   |
-- | 4  | Diana   | IT         | 7000   |
-- | 5  | Eve     | IT         | 8000   |

SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_num,
    RANK() OVER (ORDER BY salary DESC) as rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank,
    NTILE(3) OVER (ORDER BY salary DESC) as tercile
FROM employees;

-- Результат:
-- | name    | salary | row_num | rank | dense_rank | tercile |
-- |---------|--------|---------|------|------------|---------|
-- | Eve     | 8000   | 1       | 1    | 1          | 1       |
-- | Diana   | 7000   | 2       | 2    | 2          | 1       |
-- | Charlie | 6000   | 3       | 3    | 3          | 2       |
-- | Alice   | 5000   | 4       | 4    | 4          | 2       |
-- | Bob     | 5000   | 5       | 4    | 4          | 3       |

-- WHY разные функции:
-- ROW_NUMBER: всегда уникальный номер
-- RANK: одинаковые значения = одинаковый ранг, пропуск следующего
-- DENSE_RANK: без пропусков
-- NTILE(n): делит на n равных групп


-- ═══════════════════════════════════════════════════════════════
-- PARTITION BY — Ранжирование внутри групп
-- ═══════════════════════════════════════════════════════════════

SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (
        PARTITION BY department
        ORDER BY salary DESC
    ) as rank_in_dept
FROM employees;

-- Результат:
-- | name    | department | salary | rank_in_dept |
-- |---------|------------|--------|--------------|
-- | Charlie | Sales      | 6000   | 1            |
-- | Alice   | Sales      | 5000   | 2            |
-- | Bob     | Sales      | 5000   | 3            |
-- | Eve     | IT         | 8000   | 1            |
-- | Diana   | IT         | 7000   | 2            |


-- ═══════════════════════════════════════════════════════════════
-- AGGREGATE WINDOW FUNCTIONS
-- ═══════════════════════════════════════════════════════════════

SELECT
    name,
    department,
    salary,
    SUM(salary) OVER () as total_salary,  -- Вся таблица
    SUM(salary) OVER (PARTITION BY department) as dept_total,
    AVG(salary) OVER (PARTITION BY department) as dept_avg,
    salary - AVG(salary) OVER (PARTITION BY department) as diff_from_avg
FROM employees;


-- ═══════════════════════════════════════════════════════════════
-- RUNNING TOTALS & MOVING AVERAGES
-- ═══════════════════════════════════════════════════════════════

-- orders: | date | amount |
SELECT
    order_date,
    amount,
    -- Running total (накопительная сумма)
    SUM(amount) OVER (ORDER BY order_date) as running_total,

    -- Moving average (скользящее среднее за 3 дня)
    AVG(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as moving_avg_3,

    -- Процент от общего
    amount * 100.0 / SUM(amount) OVER () as pct_of_total
FROM orders;


-- ═══════════════════════════════════════════════════════════════
-- LAG / LEAD — Предыдущая/следующая строка
-- ═══════════════════════════════════════════════════════════════

SELECT
    order_date,
    amount,
    LAG(amount) OVER (ORDER BY order_date) as prev_amount,
    LEAD(amount) OVER (ORDER BY order_date) as next_amount,
    amount - LAG(amount) OVER (ORDER BY order_date) as diff_from_prev
FROM orders;

-- Use case: Рост продаж
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) as prev_month,
    (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 /
        LAG(revenue) OVER (ORDER BY month) as growth_pct
FROM monthly_sales;


-- ═══════════════════════════════════════════════════════════════
-- FIRST_VALUE / LAST_VALUE
-- ═══════════════════════════════════════════════════════════════

SELECT
    name,
    department,
    salary,
    FIRST_VALUE(name) OVER (
        PARTITION BY department
        ORDER BY salary DESC
    ) as top_earner,
    salary - FIRST_VALUE(salary) OVER (
        PARTITION BY department
        ORDER BY salary DESC
    ) as diff_from_top
FROM employees;
```

---

## SQL Advanced: CTEs и рекурсия

### Common Table Expressions (CTEs)

```sql
-- ═══════════════════════════════════════════════════════════════
-- БАЗОВЫЙ CTE
-- ═══════════════════════════════════════════════════════════════

-- CTE = временная именованная таблица для одного запроса
-- Улучшает читаемость, избегает повторения подзапросов

WITH high_value_orders AS (
    SELECT
        customer_id,
        SUM(amount) as total,
        COUNT(*) as order_count
    FROM orders
    WHERE created_at > '2024-01-01'
    GROUP BY customer_id
    HAVING SUM(amount) > 10000
)
SELECT
    c.name,
    c.email,
    h.total,
    h.order_count
FROM customers c
JOIN high_value_orders h ON c.id = h.customer_id
ORDER BY h.total DESC;


-- ═══════════════════════════════════════════════════════════════
-- МНОЖЕСТВЕННЫЕ CTEs
-- ═══════════════════════════════════════════════════════════════

WITH
monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) as month,
        SUM(amount) as revenue
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
),
avg_sales AS (
    SELECT AVG(revenue) as avg_revenue FROM monthly_sales
)
SELECT
    m.month,
    m.revenue,
    a.avg_revenue,
    CASE
        WHEN m.revenue > a.avg_revenue THEN 'Above Average'
        ELSE 'Below Average'
    END as performance
FROM monthly_sales m
CROSS JOIN avg_sales a;


-- ═══════════════════════════════════════════════════════════════
-- RECURSIVE CTE — Иерархии
-- ═══════════════════════════════════════════════════════════════

-- Таблица employees с self-reference (manager_id → id)
-- | id | name    | manager_id |
-- |----|---------|------------|
-- | 1  | CEO     | NULL       |
-- | 2  | VP      | 1          |
-- | 3  | Manager | 2          |
-- | 4  | Worker  | 3          |

WITH RECURSIVE org_chart AS (
    -- Base case: начинаем с корня (CEO)
    SELECT
        id,
        name,
        manager_id,
        1 as level,
        name as path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: добавляем подчинённых
    SELECT
        e.id,
        e.name,
        e.manager_id,
        oc.level + 1,
        oc.path || ' → ' || e.name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT * FROM org_chart ORDER BY level, name;

-- Результат:
-- | id | name    | level | path                        |
-- |----|---------|-------|----------------------------|
-- | 1  | CEO     | 1     | CEO                         |
-- | 2  | VP      | 2     | CEO → VP                    |
-- | 3  | Manager | 3     | CEO → VP → Manager          |
-- | 4  | Worker  | 4     | CEO → VP → Manager → Worker |


-- ═══════════════════════════════════════════════════════════════
-- RECURSIVE CTE — Категории товаров
-- ═══════════════════════════════════════════════════════════════

-- categories: | id | name | parent_id |
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, ARRAY[id] as path, 0 as depth
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    SELECT c.id, c.name, c.parent_id, ct.path || c.id, ct.depth + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
    WHERE NOT c.id = ANY(ct.path)  -- Защита от циклов
)
SELECT
    id,
    REPEAT('  ', depth) || name as indented_name,
    depth
FROM category_tree
ORDER BY path;


-- ═══════════════════════════════════════════════════════════════
-- RECURSIVE CTE — Генерация последовательности
-- ═══════════════════════════════════════════════════════════════

-- Сгенерировать даты за последние 30 дней
WITH RECURSIVE date_series AS (
    SELECT CURRENT_DATE - INTERVAL '30 days' as date

    UNION ALL

    SELECT date + INTERVAL '1 day'
    FROM date_series
    WHERE date < CURRENT_DATE
)
SELECT date FROM date_series;

-- Use case: Заполнение пропущенных дат в отчётах
WITH RECURSIVE date_series AS (
    SELECT CURRENT_DATE - INTERVAL '30 days' as date
    UNION ALL
    SELECT date + INTERVAL '1 day' FROM date_series WHERE date < CURRENT_DATE
),
daily_orders AS (
    SELECT DATE(created_at) as date, COUNT(*) as orders
    FROM orders
    WHERE created_at > CURRENT_DATE - INTERVAL '30 days'
    GROUP BY DATE(created_at)
)
SELECT
    ds.date,
    COALESCE(do.orders, 0) as orders
FROM date_series ds
LEFT JOIN daily_orders do ON ds.date = do.date
ORDER BY ds.date;
```

---

## Оптимизация запросов

### EXPLAIN ANALYZE

```sql
-- ═══════════════════════════════════════════════════════════════
-- EXPLAIN — Показать план выполнения
-- ═══════════════════════════════════════════════════════════════

-- PostgreSQL
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- С реальной статистикой выполнения
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Подробный вывод
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM users WHERE email = 'test@example.com';

-- MySQL
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- MySQL 8.0+ (подробнее)
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- SQLite
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';


-- ═══════════════════════════════════════════════════════════════
-- КАК ЧИТАТЬ EXPLAIN
-- ═══════════════════════════════════════════════════════════════

-- PostgreSQL EXPLAIN output:
/*
Seq Scan on users  (cost=0.00..155.00 rows=1 width=200) (actual time=0.5..2.1 rows=1 loops=1)
  Filter: (email = 'test@example.com'::text)
  Rows Removed by Filter: 4999
Planning Time: 0.1 ms
Execution Time: 2.2 ms
*/

-- Ключевые метрики:
-- cost: оценка стоимости (startup..total)
-- rows: оценочное количество строк
-- actual time: реальное время (ms)
-- Rows Removed by Filter: сколько строк отброшено

-- ПЛОХО: Seq Scan (Sequential Scan) = Full Table Scan
-- ХОРОШО: Index Scan, Index Only Scan


-- ═══════════════════════════════════════════════════════════════
-- ТИПЫ СКАНИРОВАНИЯ
-- ═══════════════════════════════════════════════════════════════

-- Seq Scan — полный скан таблицы (O(n))
-- Проблема: медленно для больших таблиц
Seq Scan on users
  Filter: (email = 'test@example.com')

-- Index Scan — поиск по индексу + чтение данных (O(log n))
Index Scan using idx_users_email on users
  Index Cond: (email = 'test@example.com')

-- Index Only Scan — данные только из индекса (O(log n), fastest)
-- Возможен если все нужные колонки в индексе
Index Only Scan using idx_users_email_name on users
  Index Cond: (email = 'test@example.com')

-- Bitmap Index Scan — для множества значений
Bitmap Heap Scan on users
  Recheck Cond: (status = 'active')
  -> Bitmap Index Scan on idx_users_status
       Index Cond: (status = 'active')


-- ═══════════════════════════════════════════════════════════════
-- ОПТИМИЗАЦИЯ ПО РЕЗУЛЬТАТАМ EXPLAIN
-- ═══════════════════════════════════════════════════════════════

-- ПРОБЛЕМА 1: Seq Scan вместо Index Scan
-- Решение: создать индекс
CREATE INDEX idx_users_email ON users(email);

-- ПРОБЛЕМА 2: Высокий Rows Removed by Filter
-- Решение: добавить колонку в индекс или создать partial index
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- ПРОБЛЕМА 3: Sort cost высокий
-- Решение: индекс с правильным порядком
CREATE INDEX idx_users_created ON users(created_at DESC);

-- ПРОБЛЕМА 4: Hash Join на больших таблицах
-- Решение: увеличить work_mem или оптимизировать JOIN

-- ПРОБЛЕМА 5: Nested Loop слишком много loops
-- Решение: убедиться что есть индекс для JOIN условия
```

### Индексы — Best Practices

```sql
-- ═══════════════════════════════════════════════════════════════
-- КОГДА СОЗДАВАТЬ ИНДЕКСЫ
-- ═══════════════════════════════════════════════════════════════

-- 1. Колонки в WHERE
SELECT * FROM orders WHERE customer_id = 123;
-- → CREATE INDEX idx_orders_customer ON orders(customer_id);

-- 2. Колонки в JOIN
SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id;
-- → Индекс на orders.customer_id и customers.id (обычно PK)

-- 3. Колонки в ORDER BY
SELECT * FROM products ORDER BY created_at DESC LIMIT 10;
-- → CREATE INDEX idx_products_created ON products(created_at DESC);

-- 4. Колонки с высокой селективностью
-- email: высокая (уникальные значения) ✓
-- status: низкая ('active'/'inactive') — индекс менее эффективен


-- ═══════════════════════════════════════════════════════════════
-- COMPOSITE (СОСТАВНЫЕ) ИНДЕКСЫ
-- ═══════════════════════════════════════════════════════════════

-- Порядок колонок важен!
CREATE INDEX idx_orders_customer_date ON orders(customer_id, created_at);

-- Этот индекс работает для:
SELECT * FROM orders WHERE customer_id = 123;  -- ✓
SELECT * FROM orders WHERE customer_id = 123 AND created_at > '2024-01-01';  -- ✓
SELECT * FROM orders WHERE customer_id = 123 ORDER BY created_at;  -- ✓

-- НЕ работает для:
SELECT * FROM orders WHERE created_at > '2024-01-01';  -- ✗ (не leftmost)

-- Правило: индекс (A, B, C) работает для A, AB, ABC, но не для B, C, BC


-- ═══════════════════════════════════════════════════════════════
-- COVERING INDEX (Index-Only Scan)
-- ═══════════════════════════════════════════════════════════════

-- Если SELECT содержит только колонки из индекса — Index Only Scan
CREATE INDEX idx_orders_covering
ON orders(customer_id, created_at)
INCLUDE (status, total);  -- PostgreSQL 11+

-- Теперь этот запрос не обращается к таблице:
SELECT status, total FROM orders
WHERE customer_id = 123 AND created_at > '2024-01-01';


-- ═══════════════════════════════════════════════════════════════
-- PARTIAL INDEX (Частичный индекс)
-- ═══════════════════════════════════════════════════════════════

-- Индексировать только нужные строки
CREATE INDEX idx_active_orders
ON orders(created_at)
WHERE status = 'active';

-- Меньше размер индекса
-- Быстрее UPDATE/INSERT
-- Идеально для часто запрашиваемых подмножеств


-- ═══════════════════════════════════════════════════════════════
-- АНТИПАТТЕРНЫ
-- ═══════════════════════════════════════════════════════════════

-- 1. Функция над индексированной колонкой
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';  -- ✗ Index не используется

-- Решение: Expression index
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- 2. LIKE с wildcard в начале
SELECT * FROM users WHERE name LIKE '%smith';  -- ✗ Index не используется

-- Решение: Full-text search или Trigram index
CREATE INDEX idx_users_name_gin ON users USING GIN (name gin_trgm_ops);

-- 3. Implicit type conversion
SELECT * FROM users WHERE phone = 12345;  -- phone is VARCHAR
-- ✗ Может не использовать индекс

-- 4. OR условия
SELECT * FROM users WHERE email = 'a' OR name = 'b';  -- ✗ Может быть Seq Scan
-- Решение: UNION или composite index
```

---

## Транзакции и Isolation Levels

### Isolation Levels

```sql
-- ═══════════════════════════════════════════════════════════════
-- УРОВНИ ИЗОЛЯЦИИ ТРАНЗАКЦИЙ
-- ═══════════════════════════════════════════════════════════════

-- 1. READ UNCOMMITTED (самый слабый)
-- Проблема: Dirty Read (чтение незакоммиченных данных)
-- PostgreSQL: не поддерживает, эквивалентен READ COMMITTED

-- 2. READ COMMITTED (PostgreSQL default)
-- Видит только закоммиченные данные
-- Проблема: Non-repeatable Read (повторный SELECT может дать другой результат)

-- 3. REPEATABLE READ (MySQL InnoDB default)
-- Повторные SELECT дают тот же результат
-- Проблема: Phantom Read (новые строки могут появиться)

-- 4. SERIALIZABLE (самый строгий)
-- Полная изоляция, как последовательное выполнение
-- Проблема: Низкая производительность, deadlocks

-- Установить уровень изоляции:
-- PostgreSQL
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- MySQL
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;


-- ═══════════════════════════════════════════════════════════════
-- ПРИМЕР: DIRTY READ
-- ═══════════════════════════════════════════════════════════════

-- Session 1:                     -- Session 2:
BEGIN;
UPDATE accounts
SET balance = balance - 100
WHERE id = 1;
                                  -- При READ UNCOMMITTED:
                                  SELECT balance FROM accounts WHERE id = 1;
                                  -- Видит новый баланс (ещё не закоммиченный)!
ROLLBACK;  -- Откат!
                                  -- Теперь Session 2 имеет неверные данные


-- ═══════════════════════════════════════════════════════════════
-- ПРИМЕР: NON-REPEATABLE READ
-- ═══════════════════════════════════════════════════════════════

-- Session 1 (READ COMMITTED):    -- Session 2:
BEGIN;
SELECT balance FROM accounts WHERE id = 1;
-- Результат: 1000
                                  BEGIN;
                                  UPDATE accounts SET balance = 500 WHERE id = 1;
                                  COMMIT;

SELECT balance FROM accounts WHERE id = 1;
-- Результат: 500 — другое значение!
COMMIT;


-- ═══════════════════════════════════════════════════════════════
-- ПРИМЕР: PHANTOM READ
-- ═══════════════════════════════════════════════════════════════

-- Session 1 (REPEATABLE READ):   -- Session 2:
BEGIN;
SELECT COUNT(*) FROM orders WHERE status = 'pending';
-- Результат: 10
                                  BEGIN;
                                  INSERT INTO orders (status) VALUES ('pending');
                                  COMMIT;

SELECT COUNT(*) FROM orders WHERE status = 'pending';
-- При REPEATABLE READ: всё ещё 10 (snapshot)
-- При READ COMMITTED: 11 (phantom row)
COMMIT;


-- ═══════════════════════════════════════════════════════════════
-- DEADLOCK
-- ═══════════════════════════════════════════════════════════════

-- Session 1:                     -- Session 2:
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
                                  BEGIN;
                                  UPDATE accounts SET balance = balance - 100 WHERE id = 2;

UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- Ждёт Session 2...
                                  UPDATE accounts SET balance = balance + 100 WHERE id = 1;
                                  -- Ждёт Session 1...

-- DEADLOCK! БД обнаружит и откатит одну из транзакций

-- Решение: упорядочить доступ к ресурсам
-- Всегда обновлять accounts в порядке id
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
```

---

## Репликация и High Availability

### PostgreSQL Streaming Replication

```
┌─────────────────────────────────────────────────────────────────────┐
│                PostgreSQL Streaming Replication                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                      ┌─────────────────┐                            │
│                      │    PRIMARY      │                            │
│                      │    (Master)     │                            │
│                      │                 │                            │
│                      │  Writes + Reads │                            │
│                      └────────┬────────┘                            │
│                               │                                     │
│                    WAL Sender │ (streaming)                         │
│                               │                                     │
│              ┌────────────────┼────────────────┐                    │
│              │                │                │                    │
│              ▼                ▼                ▼                    │
│   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │
│   │    REPLICA 1    │ │    REPLICA 2    │ │    REPLICA 3    │       │
│   │   (Standby)     │ │   (Standby)     │ │   (Standby)     │       │
│   │                 │ │                 │ │                 │       │
│   │   Reads Only    │ │   Reads Only    │ │   Reads Only    │       │
│   └─────────────────┘ └─────────────────┘ └─────────────────┘       │
│                                                                     │
│   Synchronous vs Asynchronous:                                      │
│   - Sync: Primary ждёт подтверждения от replica                     │
│   - Async: Primary не ждёт (возможна потеря данных при failover)    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Базовая настройка репликации

```bash
# ═══════════════════════════════════════════════════════════════
# PRIMARY (Master) конфигурация
# ═══════════════════════════════════════════════════════════════

# postgresql.conf на Primary:
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB

# pg_hba.conf — разрешить репликацию:
host replication replicator 10.0.0.0/24 md5

# Создать пользователя для репликации:
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'secure_password';


# ═══════════════════════════════════════════════════════════════
# REPLICA (Standby) настройка
# ═══════════════════════════════════════════════════════════════

# Остановить PostgreSQL на replica
sudo systemctl stop postgresql

# Скопировать данные с primary
pg_basebackup -h primary_host -U replicator -D /var/lib/postgresql/data -P

# Создать standby.signal (PostgreSQL 12+)
touch /var/lib/postgresql/data/standby.signal

# postgresql.conf на Replica:
primary_conninfo = 'host=primary_host user=replicator password=secure_password'
hot_standby = on

# Запустить replica
sudo systemctl start postgresql
```

```sql
-- ═══════════════════════════════════════════════════════════════
-- МОНИТОРИНГ РЕПЛИКАЦИИ
-- ═══════════════════════════════════════════════════════════════

-- На Primary: статус WAL senders
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as lag_bytes
FROM pg_stat_replication;

-- На Replica: задержка репликации
SELECT
    now() - pg_last_xact_replay_timestamp() as replication_lag;

-- Проверить, что replica в режиме read-only
SHOW transaction_read_only;  -- should be "on"
```

---

## Практические задания

### Задание 1: Проектирование e-commerce

```sql
-- Спроектируй схему для e-commerce приложения:
-- - Users (покупатели и продавцы)
-- - Products (с JSONB атрибутами)
-- - Categories (иерархия)
-- - Orders (статусы, история)
-- - Reviews (рейтинги)

-- Требования:
-- 1. Нормализация до 3NF
-- 2. Правильные индексы
-- 3. Foreign Keys с CASCADE
-- 4. JSONB для гибких атрибутов товаров
-- 5. Recursive CTE для категорий
```

### Задание 2: Оптимизация запросов

```sql
-- Дан медленный запрос:
SELECT
    u.name,
    COUNT(o.id) as order_count,
    SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.created_at > '2024-01-01'
GROUP BY u.id, u.name
HAVING SUM(o.total) > 1000
ORDER BY total_spent DESC
LIMIT 10;

-- Задания:
-- 1. Запусти EXPLAIN ANALYZE
-- 2. Определи bottlenecks
-- 3. Создай необходимые индексы
-- 4. Перепиши запрос с CTE если нужно
-- 5. Сравни время до/после
```

### Задание 3: Window Functions

```sql
-- Напиши запросы используя Window Functions:
-- 1. Ранжирование продавцов по продажам в каждом регионе
-- 2. Скользящее среднее продаж за 7 дней
-- 3. Cumulative sum по месяцам
-- 4. Найти streak (последовательные дни покупок)
-- 5. Сравнение с предыдущим периодом (growth rate)
```

---

## Связь с другими темами

[[databases-fundamentals-complete]] — Фундаментальные концепции баз данных (таблицы, ключи, индексы, ACID, нормализация) являются необходимым пререквизитом для изучения конкретных SQL СУБД. Без понимания нормальных форм, типов JOIN и isolation levels невозможно эффективно использовать PostgreSQL, MySQL или SQLite. Рекомендуется как обязательный предшествующий материал.

[[nosql-databases-complete]] — NoSQL-базы данных представляют альтернативный подход к хранению данных, и понимание SQL помогает осознать, от чего именно отказывается каждый тип NoSQL. Многие проекты используют Polyglot Persistence (PostgreSQL для транзакций + Redis для кэша + MongoDB для документов), поэтому знание обоих миров необходимо. Рекомендуется изучать параллельно с SQL.

[[database-internals-complete]] — Внутренние механизмы баз данных (B-Tree, WAL, MVCC, Buffer Pool) объясняют, почему PostgreSQL и MySQL ведут себя по-разному при одинаковых запросах. Понимание internals позволяет перейти от механического использования EXPLAIN ANALYZE к осознанной оптимизации: выбор storage engine, настройка параметров, понимание lock contention.

[[database-design-optimization]] — Практическая оптимизация запросов и проектирование схем являются прямым применением знаний из этого документа: индексы для ускорения WHERE, EXPLAIN ANALYZE для диагностики, cursor pagination вместо OFFSET. Рекомендуется как следующий шаг после изучения SQL СУБД для перехода к production-уровню.

## Источники и дальнейшее чтение

- Ramakrishnan R., Gehrke J. (2002). *Database Management Systems*. — Полный университетский курс: SQL, query processing, concurrency control, recovery. Фундаментальный учебник для глубокого понимания реляционных СУБД.
- Kleppmann M. (2017). *Designing Data-Intensive Applications*. — Главы о storage engines (B-Tree vs LSM-Tree), репликации (single-leader, multi-leader, leaderless) и транзакциях объясняют архитектурные решения PostgreSQL, MySQL и SQLite.
- Petrov A. (2019). *Database Internals*. — Детальный разбор внутренних механизмов СУБД: от структуры страниц и buffer management до distributed transactions. Идеальное дополнение к практическому использованию SQL.

---

*Создано: 2025-12-30*
*Обновлено: 2025-12-30*
*Источники: PostgreSQL/MySQL/SQLite официальная документация, DigitalOcean, Percona, PowerSync*

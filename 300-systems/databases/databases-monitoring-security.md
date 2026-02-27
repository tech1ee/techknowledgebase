---
title: "Database Monitoring & Security: pg_stat, RLS, encryption"
created: 2025-12-22
modified: 2026-02-13
type: concept
status: published
confidence: high
tags:
  - topic/databases
  - monitoring
  - topic/security
  - postgresql
  - performance
  - type/concept
  - level/intermediate
related:
  - "[[databases-overview]]"
  - "[[database-design-optimization]]"
  - "[[security-overview]]"
  - "[[observability]]"
prerequisites:
  - "[[databases-sql-fundamentals]]"
  - "[[databases-transactions-acid]]"
reading_time: 19
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Database Monitoring & Security: pg_stat, RLS, encryption

> Мониторинг показывает проблемы до того, как они станут инцидентами. Security защищает данные от утечек и несанкционированного доступа.

---

## Теоретические основы

> **Database monitoring** — непрерывный сбор и анализ метрик СУБД для обнаружения проблем до того, как они станут инцидентами. **Database security** — многоуровневая защита данных от несанкционированного доступа, утечек и атак.

### Четыре категории метрик (USE Method, Gregg 2013)

| Категория | Что измеряет | Ключевые метрики PostgreSQL |
|-----------|-------------|---------------------------|
| **Utilization** | Занятость ресурса | CPU %, connections / max_connections, buffer cache hit ratio |
| **Saturation** | Очередь/перегрузка | Lock waits, disk I/O queue, replication lag |
| **Errors** | Частота ошибок | Deadlocks, failed transactions, checksum errors |
| **Throughput** | Объём работы | TPS (transactions/sec), rows read/written |

### Defense in Depth — модель безопасности БД

```
┌─────────────────────────────────────────────┐
│ Network: Firewall, VPC, SSL/TLS             │
│  ┌─────────────────────────────────────────┐ │
│  │ Authentication: pg_hba.conf, LDAP, SCRAM│ │
│  │  ┌─────────────────────────────────────┐ │ │
│  │  │ Authorization: GRANT, REVOKE, Roles │ │ │
│  │  │  ┌─────────────────────────────────┐ │ │ │
│  │  │  │ Row-Level: RLS policies         │ │ │ │
│  │  │  │  ┌─────────────────────────────┐ │ │ │ │
│  │  │  │  │ Column-Level: Encryption    │ │ │ │ │
│  │  │  │  │  ┌─────────────────────────┐ │ │ │ │ │
│  │  │  │  │  │ Audit: pgAudit logging  │ │ │ │ │ │
│  │  │  │  │  └─────────────────────────┘ │ │ │ │ │
│  │  │  │  └─────────────────────────────┘ │ │ │ │
│  │  │  └─────────────────────────────────┘ │ │ │
│  │  └─────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Принцип наименьших привилегий (Saltzer & Schroeder, 1975)

> Каждый субъект (пользователь, приложение) должен иметь **минимально необходимые** права для выполнения своей задачи. В БД: приложение **не** должно работать от superuser; каждый микросервис — свой пользователь с GRANT только на нужные таблицы.

### OWASP Top 10 угроз для БД

| Угроза | Защита в PostgreSQL |
|--------|-------------------|
| **SQL Injection** | Prepared statements (parameterized queries) |
| **Broken Authentication** | SCRAM-SHA-256, certificate auth |
| **Sensitive Data Exposure** | TDE, column encryption, SSL in transit |
| **Broken Access Control** | RLS, GRANT/REVOKE, pg_hba.conf |
| **Security Misconfiguration** | CIS Benchmark, pg_hba.conf audit |

> **См. также**: [[security-overview]] — общие принципы безопасности, [[observability]] — системы наблюдаемости

---

## TL;DR

**Мониторинг:**
- `pg_stat_statements` — статистика запросов (must have)
- `pg_stat_activity` — текущие сессии и запросы
- Алерты на: slow queries, connections, replication lag, disk space

**Security:**
- **RLS** — Row-Level Security для multi-tenant
- **Encryption at rest** — TDE или filesystem encryption
- **Encryption in transit** — SSL/TLS обязательно
- **Least privilege** — минимальные права для каждого пользователя

---

## Часть 1: Интуиция без кода

### Аналогия 1: Охранная система здания (Defense in Depth)

Безопасность БД работает как многоуровневая охрана небоскрёба:

```
ЗДАНИЕ = БАЗА ДАННЫХ

Уровень 1: ЗАБОР + КПП (Network security)
┌─────────────────────────────────────────────────────────┐
│  • Firewall — кто может даже подойти?                   │
│  • VPN — только свои сети                               │
│  • SSL/TLS — шифрованный канал                          │
└────────────────────────┬────────────────────────────────┘
                         ▼
Уровень 2: РЕСЕПШН (Authentication)
┌─────────────────────────────────────────────────────────┐
│  • pg_hba.conf — кто может войти?                       │
│  • SCRAM-SHA-256 — проверка пароля                      │
│  • Сертификаты — проверка личности                      │
└────────────────────────┬────────────────────────────────┘
                         ▼
Уровень 3: ПРОПУСК НА ЭТАЖ (Authorization - RBAC)
┌─────────────────────────────────────────────────────────┐
│  • GRANT/REVOKE — какие таблицы доступны?               │
│  • Роли — уборщик не зайдёт в серверную                 │
│  • Схемы — отделы изолированы                           │
└────────────────────────┬────────────────────────────────┘
                         ▼
Уровень 4: КЛЮЧ ОТ КАБИНЕТА (Row-Level Security)
┌─────────────────────────────────────────────────────────┐
│  • RLS — видишь только СВОИ документы в шкафу           │
│  • Даже войдя в кабинет, не откроешь чужой сейф        │
└─────────────────────────────────────────────────────────┘

Уровень 5: КАМЕРЫ + СИГНАЛИЗАЦИЯ (Monitoring + Audit)
┌─────────────────────────────────────────────────────────┐
│  • pg_stat_statements — кто что делал?                  │
│  • pgAudit — журнал всех действий                       │
│  • Алерты — кто-то ломится в 3 ночи!                    │
└─────────────────────────────────────────────────────────┘
```

**Ключевая идея:** Если взломали один уровень — остальные всё ещё защищают.

### Аналогия 2: Фейсконтроль в VIP-клубе (Row-Level Security)

Представь ночной клуб с разными зонами:

```
БЕЗ RLS (проверка на входе):
┌─────────────────────────────────────────────────────────┐
│  Охранник: "Ты в списке VIP?"                           │
│  Гость: "Да!"                                           │
│  Охранник: "Проходи куда хочешь..."                     │
│                                                         │
│  Проблема: Охранник забыл спросить → гость везде!       │
│           (забыл WHERE tenant_id = ?)                   │
└─────────────────────────────────────────────────────────┘

С RLS (браслет на руке):
┌─────────────────────────────────────────────────────────┐
│  На входе: "Вот тебе КРАСНЫЙ браслет"                   │
│                                                         │
│  ┌───────────────┐  ┌───────────────┐                   │
│  │ Зона VIP      │  │ Зона Premium  │                   │
│  │ 🔴 КРАСНЫЕ    │  │ 🔵 СИНИЕ      │                   │
│  │ только        │  │ только        │                   │
│  └───────────────┘  └───────────────┘                   │
│                                                         │
│  Турникет АВТОМАТИЧЕСКИ не пустит синего в красную!    │
│  Невозможно "забыть проверить"                          │
└─────────────────────────────────────────────────────────┘

В PostgreSQL:
SET app.current_tenant = 'red';   -- Браслет
SELECT * FROM orders;              -- Турникет фильтрует автоматически
```

### Аналогия 3: Банковский сейф (Encryption Layers)

Три уровня защиты ценностей:

```
Уровень 1: ДВЕРЬ БАНКА (Encryption in Transit)
┌─────────────────────────────────────────────────────────┐
│  Бронированные двери = SSL/TLS                          │
│                                                         │
│  Клиент ────[шифрованный канал]────▶ Банк               │
│                                                         │
│  Защищает ОТ: подслушивания, man-in-the-middle         │
└─────────────────────────────────────────────────────────┘

Уровень 2: ХРАНИЛИЩЕ (Encryption at Rest)
┌─────────────────────────────────────────────────────────┐
│  Стены хранилища = Filesystem/TDE encryption            │
│                                                         │
│  Даже если украли диск → данные зашифрованы            │
│                                                         │
│  Защищает ОТ: кражи оборудования, доступа к файлам     │
└─────────────────────────────────────────────────────────┘

Уровень 3: ИНДИВИДУАЛЬНЫЕ ЯЧЕЙКИ (Column-level encryption)
┌─────────────────────────────────────────────────────────┐
│  Личный сейф с вашим ключом = pgcrypto                  │
│                                                         │
│  SSN:     pgp_sym_encrypt('123-45-6789', 'my-key')     │
│  Card:    pgp_sym_encrypt('4111...', 'my-key')         │
│                                                         │
│  Даже DBA не может прочитать без ключа!                 │
│                                                         │
│  Защищает ОТ: инсайдеров, компрометации DBA            │
└─────────────────────────────────────────────────────────┘
```

### Аналогия 4: Больница с медкартами (Least Privilege)

В больнице не все имеют доступ ко всем картам:

```
┌─────────────────────────────────────────────────────────┐
│  УБОРЩИК (guest)                                        │
│  • Может: войти в здание                                │
│  • Нельзя: читать карты, назначать лечение             │
│                                                         │
│  МЕДСЕСТРА (app_user)                                   │
│  • Может: читать карты своего отделения                │
│  • Может: записывать показания                          │
│  • Нельзя: менять диагнозы, удалять записи             │
│                                                         │
│  ВРАЧ (doctor_role)                                     │
│  • Может: читать/писать карты своих пациентов          │
│  • Может: ставить диагнозы                              │
│  • Нельзя: удалять старые записи                        │
│                                                         │
│  ГЛАВВРАЧ (admin)                                       │
│  • Может: всё в рамках больницы                         │
│  • Нельзя: удалять архивные записи                      │
│                                                         │
│  МИНЗДРАВ (superuser)                                   │
│  • Может: вообще всё                                    │
│  • Использовать: ТОЛЬКО в экстренных случаях!          │
└─────────────────────────────────────────────────────────┘

Приложению дают права МЕДСЕСТРЫ, не ГЛАВВРАЧА!
```

### Аналогия 5: Видеорегистратор в такси (Monitoring + Audit)

Представь такси с видеорегистратором:

```
ЗАЧЕМ КАМЕРА?
┌─────────────────────────────────────────────────────────┐
│  1. БЕЗОПАСНОСТЬ                                        │
│     Пассажир ведёт себя адекватнее                      │
│     (знают что логируем → меньше атак)                  │
│                                                         │
│  2. РАЗБОР ИНЦИДЕНТОВ                                   │
│     "Кто виноват в ДТП?" → смотрим запись               │
│     (кто сделал DROP TABLE? → pgAudit)                  │
│                                                         │
│  3. ОПТИМИЗАЦИЯ                                         │
│     "Почему всегда пробки на Ленина?" → анализ GPS      │
│     (почему тормозит? → pg_stat_statements)             │
│                                                         │
│  4. СООТВЕТСТВИЕ ТРЕБОВАНИЯМ                            │
│     Страховая требует видео для выплат                  │
│     (GDPR/PCI требуют audit logs)                       │
└─────────────────────────────────────────────────────────┘

pg_stat_statements = Черный ящик рейсов (статистика)
pgAudit            = Видеозапись (кто, когда, что)
Slow query log     = GPS трекер (маршруты запросов)
```

---

## Часть 2: Почему это сложно

### Ошибка 1: SQL Injection через конкатенацию строк

**СИМПТОМ:** Строим запрос склеиванием строк с пользовательским вводом.

```python
# ❌ ОПАСНО — SQL Injection!
username = request.get("username")
query = f"SELECT * FROM users WHERE name = '{username}'"

# Атакующий вводит: ' OR '1'='1
# Получается: SELECT * FROM users WHERE name = '' OR '1'='1'
# Результат: ВСЕ пользователи!

# Атакующий вводит: '; DROP TABLE users; --
# Получается: SELECT * FROM users WHERE name = ''; DROP TABLE users; --'
# Результат: Таблица удалена!
```

**РЕШЕНИЕ:** Всегда использовать параметризованные запросы:

```python
# ✅ БЕЗОПАСНО — Prepared Statement
cursor.execute(
    "SELECT * FROM users WHERE name = %s",
    (username,)
)
# PostgreSQL обрабатывает username как ДАННЫЕ, не как КОД
```

### Ошибка 2: Superuser для приложения

**СИМПТОМ:** Приложение подключается как `postgres` superuser.

```
Почему это плохо:
┌─────────────────────────────────────────────────────────┐
│  SQL Injection + Superuser = ПОЛНЫЙ КОНТРОЛЬ            │
│                                                         │
│  Атакующий может:                                       │
│  • DROP DATABASE                                        │
│  • CREATE ROLE с любыми правами                         │
│  • COPY ... TO '/etc/passwd' (читать файлы!)           │
│  • CREATE EXTENSION для выполнения кода                 │
│                                                         │
│  Компрометация приложения = компрометация ВСЕГО        │
└─────────────────────────────────────────────────────────┘
```

**РЕШЕНИЕ:**
```sql
-- Отдельная роль с минимальными правами
CREATE ROLE app_user LOGIN PASSWORD 'secure';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- НЕ давать: CREATE, DROP, TRUNCATE, REFERENCES, TRIGGER
```

### Ошибка 3: Нет мониторинга slow queries

**СИМПТОМ:** Узнают о проблемах от пользователей: "Сайт тормозит!"

```
БЕЗ МОНИТОРИНГА:
┌──────────────────────────────────────────────────────────┐
│ День 1: Запрос 100ms → норма                             │
│ День 7: Запрос 500ms → никто не заметил                 │
│ День 30: Запрос 5s → "сайт лагает"                      │
│ День 31: Запрос 30s → timeout, инцидент!                │
│                                                          │
│ Пользователь жалуется РАНЬШЕ чем DBA узнаёт             │
└──────────────────────────────────────────────────────────┘
```

**РЕШЕНИЕ:**
```sql
-- Включить pg_stat_statements
CREATE EXTENSION pg_stat_statements;

-- Алерт на медленные запросы
-- Prometheus: pg_stat_statements_seconds_total > threshold
```

### Ошибка 4: RLS без FORCE для владельца таблицы

**СИМПТОМ:** Включили RLS, но owner таблицы видит все строки.

```sql
-- Создали таблицу как app_owner
CREATE TABLE orders (...);

-- Включили RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Создали policy
CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.tenant'));

-- Но app_owner (владелец) ИГНОРИРУЕТ RLS!
-- По умолчанию owner обходит политики
```

**РЕШЕНИЕ:**
```sql
-- Принудительно включить RLS для владельца
ALTER TABLE orders FORCE ROW LEVEL SECURITY;

-- Или использовать отдельную роль для приложения
GRANT SELECT, INSERT, UPDATE, DELETE ON orders TO app_user;
-- app_user НЕ owner → RLS работает
```

### Ошибка 5: Логирование sensitive данных

**СИМПТОМ:** В логах видны пароли, номера карт, персональные данные.

```
# ❌ Плохо — postgresql.conf
log_statement = 'all'

# В логах:
# SELECT * FROM users WHERE password = 'secret123'
# INSERT INTO payments (card_number) VALUES ('4111-1111-1111-1111')

# Логи утекли → утекли все секреты!
```

**РЕШЕНИЕ:**
- `log_statement = 'ddl'` вместо `'all'`
- Использовать pgAudit с фильтрацией
- Маскировать sensitive поля в приложении
- Шифровать sensitive данные (pgcrypto)

### Ошибка 6: SSL отключён или sslmode=disable

**СИМПТОМ:** Данные передаются в открытом виде.

```
БЕЗ SSL:
┌────────┐                              ┌────────┐
│ Client │ ─── plain text ───────────▶ │ Server │
└────────┘     "password123"           └────────┘
                    │
                    ▼
             🔓 Атакующий читает
               всё в открытом виде!

С SSL:
┌────────┐                              ┌────────┐
│ Client │ ─── 🔒 encrypted ─────────▶ │ Server │
└────────┘     "A#$%^&*encrypted"      └────────┘
                    │
                    ▼
             🔒 Атакующий видит мусор
```

**РЕШЕНИЕ:**
```bash
# pg_hba.conf — ТРЕБОВАТЬ SSL
hostssl all all 0.0.0.0/0 scram-sha-256

# Клиент — проверять сертификат
psql "sslmode=verify-full sslrootcert=ca.crt"
```

---

## Часть 3: Ментальные модели

### Модель 1: Defense in Depth (Эшелонированная оборона)

```
                    АТАКА
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 1: NETWORK                                        │
│ Firewall, VPN, IP whitelist                             │
│ 90% атак отсеивается                                    │
└────────────────────────┬────────────────────────────────┘
                         │ 10% прошло
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 2: AUTHENTICATION                                 │
│ Strong passwords, MFA, certificate                      │
│ 90% из оставшихся отсеивается                          │
└────────────────────────┬────────────────────────────────┘
                         │ 1% прошло
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 3: AUTHORIZATION                                  │
│ RBAC, least privilege                                   │
│ 90% из оставшихся отсеивается                          │
└────────────────────────┬────────────────────────────────┘
                         │ 0.1% прошло
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 4: ROW-LEVEL SECURITY                             │
│ Даже с доступом видят только свои данные               │
│ 90% из оставшихся отсеивается                          │
└────────────────────────┬────────────────────────────────┘
                         │ 0.01% прошло
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 5: ENCRYPTION                                     │
│ Даже украв данные — не прочитают                       │
└─────────────────────────────────────────────────────────┘

Каждый слой уменьшает риск на порядок!
```

### Модель 2: Матрица прав доступа

```
┌───────────────┬────────┬────────┬────────┬────────┬────────┐
│ Роль          │ SELECT │ INSERT │ UPDATE │ DELETE │ DDL    │
├───────────────┼────────┼────────┼────────┼────────┼────────┤
│ app_readonly  │   ✅   │   ❌   │   ❌   │   ❌   │   ❌   │
├───────────────┼────────┼────────┼────────┼────────┼────────┤
│ app_user      │   ✅   │   ✅   │   ✅   │   ❌   │   ❌   │
├───────────────┼────────┼────────┼────────┼────────┼────────┤
│ app_admin     │   ✅   │   ✅   │   ✅   │   ✅   │   ❌   │
├───────────────┼────────┼────────┼────────┼────────┼────────┤
│ migration     │   ✅   │   ✅   │   ✅   │   ✅   │   ✅   │
├───────────────┼────────┼────────┼────────┼────────┼────────┤
│ superuser     │   ✅   │   ✅   │   ✅   │   ✅   │   ✅*  │
└───────────────┴────────┴────────┴────────┴────────┴────────┘

* superuser только для emergency, никогда для приложения!

ПРАВИЛО: Приложение НИКОГДА не должно иметь DELETE или DDL
         если это не критически необходимо.
```

### Модель 3: CIA Triad для БД

```
                    CONFIDENTIALITY
                    (Конфиденциальность)
                         ▲
                        ╱ ╲
                       ╱   ╲
            RLS       ╱     ╲      Encryption
            RBAC     ╱       ╲     pgcrypto
            SSL     ╱ DATABASE╲    TDE
                   ╱  SECURITY ╲
                  ╱─────────────╲
                 ╱               ╲
                ▼                 ▼
         INTEGRITY            AVAILABILITY
         (Целостность)        (Доступность)

         • Constraints        • Replication
         • Transactions       • Backup/PITR
         • Checksums          • Monitoring
         • Audit logs         • Connection pooling

Вопрос к каждому решению:
• Confidentiality: Кто может ВИДЕТЬ данные?
• Integrity: Кто может ИЗМЕНИТЬ данные?
• Availability: Будут ли данные ДОСТУПНЫ?
```

### Модель 4: Observability Stack для БД

```
                 ┌─────────────────────────────────────┐
                 │           DASHBOARDS                │
                 │    Grafana, DataDog, NewRelic       │
                 └──────────────────┬──────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│    METRICS    │         │    LOGS       │         │    TRACES     │
├───────────────┤         ├───────────────┤         ├───────────────┤
│pg_stat_        │         │ Slow query   │         │ Query plans   │
│statements     │         │ log           │         │               │
│               │         │               │         │ pg_stat_      │
│pg_stat_       │         │ pgAudit       │         │ activity      │
│activity       │         │               │         │               │
│               │         │ Error log     │         │ EXPLAIN       │
│Prometheus     │         │               │         │ ANALYZE       │
│postgres_      │         │               │         │               │
│exporter       │         │               │         │               │
└───────────────┘         └───────────────┘         └───────────────┘

METRICS: Что происходит? (числа)
LOGS:    Почему это произошло? (текст)
TRACES:  Как именно это происходило? (последовательность)
```

### Модель 5: Security Checklist по приоритету

```
ПРИОРИТЕТ 1: КРИТИЧНО (сделай сегодня)
┌─────────────────────────────────────────────────────────┐
│ □ SSL/TLS включён и обязателен                         │
│ □ Prepared statements везде (no SQL injection)         │
│ □ Приложение НЕ использует superuser                   │
│ □ Пароли сильные, SCRAM-SHA-256                        │
│ □ Firewall: только нужные IP/порты                     │
└─────────────────────────────────────────────────────────┘

ПРИОРИТЕТ 2: ВАЖНО (сделай на этой неделе)
┌─────────────────────────────────────────────────────────┐
│ □ pg_stat_statements включён                           │
│ □ Slow query log настроен (> 1s)                       │
│ □ Алерты на connections, disk, replication             │
│ □ Least privilege для всех ролей                       │
│ □ Backup проверен (restore test)                       │
└─────────────────────────────────────────────────────────┘

ПРИОРИТЕТ 3: ХОРОШО (сделай в этом месяце)
┌─────────────────────────────────────────────────────────┐
│ □ RLS для multi-tenant                                 │
│ □ pgAudit для compliance                               │
│ □ Encryption at rest (filesystem/TDE)                  │
│ □ Column encryption для PII (pgcrypto)                 │
│ □ Регулярный security audit                            │
└─────────────────────────────────────────────────────────┘
```

---

## Терминология

| Термин | Значение |
|--------|----------|
| **pg_stat_statements** | Extension для статистики по запросам |
| **pg_stat_activity** | Системный view текущих сессий |
| **Slow query log** | Логирование медленных запросов |
| **RLS** | Row-Level Security — ограничение по строкам |
| **TDE** | Transparent Data Encryption — шифрование данных |
| **Column-level encryption** | Шифрование отдельных колонок (pgcrypto) |
| **SSL/TLS** | Шифрование соединения |
| **Audit log** | Журнал действий пользователей |
| **Connection pooling** | Пул соединений (PgBouncer, pgpool) |

---

## Мониторинг: что отслеживать

```
┌─────────────────────────────────────────────────────────────────┐
│                 КЛЮЧЕВЫЕ МЕТРИКИ БД                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PERFORMANCE                                                    │
│  ├── Query response time (p50, p95, p99)                       │
│  ├── Queries per second (QPS)                                  │
│  ├── Slow queries count                                        │
│  └── Cache hit ratio (> 99% норма)                             │
│                                                                 │
│  CONNECTIONS                                                    │
│  ├── Active connections                                        │
│  ├── Idle connections                                          │
│  ├── Waiting connections (blocked)                             │
│  └── Connection errors                                         │
│                                                                 │
│  REPLICATION                                                    │
│  ├── Replication lag (bytes/seconds)                           │
│  ├── WAL generation rate                                       │
│  └── Replica status                                            │
│                                                                 │
│  RESOURCES                                                      │
│  ├── CPU usage                                                 │
│  ├── Memory usage                                              │
│  ├── Disk I/O (read/write IOPS)                               │
│  ├── Disk space (data + WAL)                                   │
│  └── Table/index bloat                                         │
│                                                                 │
│  LOCKS                                                          │
│  ├── Lock wait time                                            │
│  ├── Deadlocks count                                           │
│  └── Long-running transactions                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## pg_stat_statements: статистика запросов

### Установка и настройка

```sql
-- Включить extension
CREATE EXTENSION pg_stat_statements;

-- postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
pg_stat_statements.max = 10000
```

### Полезные запросы

```sql
-- ✅ Топ-10 самых медленных запросов (по общему времени)
SELECT
    substring(query, 1, 100) as query,
    calls,
    round(total_exec_time::numeric, 2) as total_time_ms,
    round(mean_exec_time::numeric, 2) as avg_time_ms,
    round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) as pct
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- ✅ Запросы с наибольшим количеством вызовов
SELECT
    substring(query, 1, 100) as query,
    calls,
    round(mean_exec_time::numeric, 2) as avg_time_ms,
    rows
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- ✅ Запросы с большим количеством прочитанных блоков (I/O intensive)
SELECT
    substring(query, 1, 100) as query,
    calls,
    shared_blks_read + shared_blks_hit as total_blks,
    round(100.0 * shared_blks_hit / nullif(shared_blks_read + shared_blks_hit, 0), 2) as cache_hit_pct
FROM pg_stat_statements
ORDER BY shared_blks_read DESC
LIMIT 10;

-- ✅ Сбросить статистику
SELECT pg_stat_statements_reset();
```

---

## pg_stat_activity: текущие сессии

```sql
-- ✅ Все активные запросы
SELECT
    pid,
    usename,
    client_addr,
    state,
    wait_event_type,
    wait_event,
    now() - query_start as duration,
    substring(query, 1, 100) as query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;

-- ✅ Долгие запросы (> 5 минут)
SELECT
    pid,
    usename,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
AND query_start < now() - interval '5 minutes';

-- ✅ Заблокированные запросы
SELECT
    blocked.pid as blocked_pid,
    blocked.query as blocked_query,
    blocking.pid as blocking_pid,
    blocking.query as blocking_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE blocked.wait_event_type = 'Lock';

-- ✅ Убить долгий запрос
SELECT pg_cancel_backend(pid);      -- Мягко (отмена запроса)
SELECT pg_terminate_backend(pid);   -- Жёстко (убить сессию)
```

---

## Slow Query Log

```bash
# postgresql.conf

# Логировать запросы дольше 1 секунды
log_min_duration_statement = 1000

# Логировать все запросы (осторожно, много логов!)
# log_statement = 'all'

# Включить статистику в лог
log_duration = on
log_lock_waits = on

# Формат лога для парсинга
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Анализ логов

```bash
# pgBadger — анализатор логов PostgreSQL
pgbadger /var/log/postgresql/postgresql-16-main.log -o report.html

# Открыть отчёт
open report.html
```

---

## Алерты

```yaml
# Prometheus + Alertmanager пример

groups:
  - name: postgres
    rules:
      # Высокая загрузка connections
      - alert: PostgresConnectionsHigh
        expr: pg_stat_activity_count > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High number of connections ({{ $value }})"

      # Replication lag
      - alert: PostgresReplicationLag
        expr: pg_replication_lag_seconds > 60
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Replication lag is {{ $value }}s"

      # Disk space
      - alert: PostgresDiskSpace
        expr: pg_database_size_bytes / pg_settings_value{name="data_directory_size"} > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Database using > 80% of disk space"

      # Slow queries
      - alert: PostgresSlowQueries
        expr: rate(pg_stat_statements_seconds_total[5m]) > 1
        for: 10m
        labels:
          severity: warning
```

---

## Security: Row-Level Security (RLS)

### Концепция

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROW-LEVEL SECURITY                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Без RLS (application-level):                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ SELECT * FROM orders WHERE tenant_id = 'acme';           │  │
│  │                                                          │  │
│  │ Проблемы:                                                │  │
│  │ • Забыл добавить WHERE → утечка данных                  │  │
│  │ • Каждый запрос нужно проверять                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  С RLS (database-level):                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ SELECT * FROM orders;  -- RLS автоматически фильтрует   │  │
│  │                                                          │  │
│  │ Преимущества:                                            │  │
│  │ • Невозможно забыть фильтр                              │  │
│  │ • Централизованное управление                           │  │
│  │ • Защита от SQL injection                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Настройка RLS

```sql
-- 1. Включить RLS на таблице
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 2. Создать policy для SELECT
CREATE POLICY orders_tenant_isolation ON orders
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant'));

-- 3. Создать policy для INSERT
CREATE POLICY orders_tenant_insert ON orders
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant'));

-- 4. Создать policy для UPDATE/DELETE
CREATE POLICY orders_tenant_modify ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant'))
    WITH CHECK (tenant_id = current_setting('app.current_tenant'));

-- Использование из приложения
SET app.current_tenant = 'acme';
SELECT * FROM orders;  -- Видит только orders для 'acme'
```

### RLS для ролей

```sql
-- Policy на основе роли пользователя
CREATE POLICY admin_all ON orders
    FOR ALL
    TO admins
    USING (true);  -- Админы видят всё

CREATE POLICY user_own ON orders
    FOR SELECT
    TO users
    USING (user_id = current_user_id());
```

---

## Encryption

### Encryption in Transit (SSL/TLS)

```bash
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'

# pg_hba.conf — требовать SSL
hostssl all all 0.0.0.0/0 scram-sha-256

# Клиент
psql "host=db.example.com dbname=mydb sslmode=verify-full sslrootcert=ca.crt"
```

### Encryption at Rest

```
┌─────────────────────────────────────────────────────────────────┐
│                ENCRYPTION AT REST                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. FILESYSTEM-LEVEL (рекомендуется)                           │
│     • LUKS (Linux)                                             │
│     • BitLocker (Windows)                                      │
│     • EBS encryption (AWS)                                     │
│     • Cloud KMS (GCP, Azure)                                   │
│                                                                 │
│     ✅ Прозрачно для PostgreSQL                                 │
│     ✅ Защищает все данные                                      │
│     ✅ Минимальный overhead                                     │
│                                                                 │
│  2. COLUMN-LEVEL (pgcrypto)                                    │
│     • Шифрование отдельных полей                               │
│     • Ключи в приложении                                       │
│                                                                 │
│     ✅ Гранулярный контроль                                     │
│     ❌ Нельзя индексировать/искать                              │
│     ❌ Overhead на каждую операцию                              │
│                                                                 │
│  3. TDE (Transparent Data Encryption)                          │
│     • Enterprise PostgreSQL (EDB)                              │
│     • Или через pg_tde extension                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Column-level encryption с pgcrypto

```sql
-- Включить extension
CREATE EXTENSION pgcrypto;

-- Шифрование при вставке
INSERT INTO users (email, ssn_encrypted)
VALUES (
    'user@example.com',
    pgp_sym_encrypt('123-45-6789', 'my-secret-key')
);

-- Дешифрование при чтении
SELECT
    email,
    pgp_sym_decrypt(ssn_encrypted, 'my-secret-key') as ssn
FROM users;

-- ⚠️ Никогда не храни ключ в БД!
-- Передавай через приложение или SET параметр
```

---

## Least Privilege

```sql
-- ✅ Создать отдельных пользователей для разных задач

-- Application user (только CRUD)
CREATE ROLE app_user LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Read-only user (для отчётов)
CREATE ROLE report_user LOGIN PASSWORD 'another_password';
GRANT CONNECT ON DATABASE mydb TO report_user;
GRANT USAGE ON SCHEMA public TO report_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO report_user;

-- Migration user (только DDL)
CREATE ROLE migration_user LOGIN PASSWORD 'migration_password';
GRANT CONNECT ON DATABASE mydb TO migration_user;
GRANT ALL ON SCHEMA public TO migration_user;

-- ❌ НЕ ДЕЛАЙ ТАК
-- GRANT ALL PRIVILEGES ON DATABASE mydb TO app_user;
```

---

## Audit Logging

```sql
-- pgAudit extension
CREATE EXTENSION pgaudit;

-- postgresql.conf
pgaudit.log = 'ddl, role, write'
pgaudit.log_catalog = off
pgaudit.log_relation = on

-- Логирует:
-- ddl: CREATE, ALTER, DROP
-- role: GRANT, REVOKE, CREATE ROLE
-- write: INSERT, UPDATE, DELETE
-- read: SELECT
-- all: всё
```

### Пример audit log

```
2025-01-15 14:30:00 UTC [12345]: AUDIT: SESSION,1,1,DDL,CREATE TABLE,,,
    "CREATE TABLE secrets (id int, data text)",<none>
2025-01-15 14:31:00 UTC [12345]: AUDIT: SESSION,2,1,WRITE,INSERT,public,secrets,
    "INSERT INTO secrets VALUES (1, 'secret')",<none>
```

---

## Связи

- [[databases-overview]] — карта раздела
- [[database-design-optimization]] — оптимизация запросов
- [[security-overview]] — общая безопасность
- [[observability]] — мониторинг систем

---

## Источники

### Теоретические основы
- Saltzer J., Schroeder M. (1975). *The Protection of Information in Computer Systems*. — Принцип наименьших привилегий и другие принципы безопасности
- Gregg B. (2013). *Systems Performance*. — USE Method для мониторинга ресурсов
- OWASP (2021). *Top 10 Web Application Security Risks*. — SQL injection, broken auth и другие угрозы БД

### Практические руководства
- [PostgreSQL Monitoring Statistics](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [pg_stat_statements](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [PostgreSQL Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [pgAudit](https://www.pgaudit.org/)

---

---

## Проверь себя

> [!question]- Почему pg_stat_statements — первый инструмент для диагностики медленных запросов?
> pg_stat_statements собирает статистику по ВСЕМ запросам: количество вызовов, total/mean time, rows, shared blocks hit/read. Позволяет найти Top-N самых медленных запросов и самых частых. Без него — только slow query log с порогом, который пропускает частые средне-медленные запросы (100 мс * 10000 вызовов = 1000 секунд CPU в сумме).

> [!question]- Почему prepared statements защищают от SQL injection, а строковая конкатенация — нет?
> SQL injection: пользователь вводит '; DROP TABLE users;-- в поле формы. При конкатенации строка вставляется в SQL как код. Prepared statements (parameterized queries) отделяют SQL-структуру от данных: БД получает шаблон и параметры отдельно, данные никогда не интерпретируются как SQL-код. Это единственная надёжная защита.

> [!question]- Что такое Row Level Security (RLS) и когда его применять вместо фильтрации в приложении?
> RLS — политики на уровне БД, фильтрующие строки по текущему пользователю: ALTER TABLE orders ENABLE ROW LEVEL SECURITY; CREATE POLICY user_orders ON orders USING (user_id = current_user_id()). Преимущество: защита на уровне БД — даже при баге в приложении данные других пользователей недоступны. Применять для multi-tenant систем, когда безопасность данных критична.

> [!question]- Какие метрики PostgreSQL нужно мониторить в первую очередь?
> Cache hit ratio (pg_stat_database: blks_hit / (blks_hit + blks_read) > 99%), active connections vs max_connections, transaction rate, replication lag, table bloat (dead tuples), lock waits, disk I/O wait. Красные флаги: cache hit < 95%, connections > 80% max, replication lag > 10 секунд.

---

## Ключевые карточки

Что показывает pg_stat_statements?
?
Расширение PostgreSQL, собирающее статистику запросов: calls, total_time, mean_time, rows, shared_blocks_hit/read. Позволяет найти самые медленные и самые частые запросы. Обязательно для production.

Что такое RLS (Row Level Security)?
?
Механизм PostgreSQL для фильтрации строк по политикам на уровне БД. Каждый пользователь видит только свои данные без фильтрации в приложении. Защита от ошибок в коде приложения.

Что такое SQL Injection и как защититься?
?
Атака через вставку SQL-кода в пользовательский ввод: ' OR 1=1; DROP TABLE users;--. Защита: prepared statements (параметризованные запросы), ORM, input validation. НИКОГДА не конкатенировать пользовательский ввод с SQL.

Что такое Encryption at Rest и in Transit?
?
At Rest: шифрование данных на диске (TDE в PostgreSQL, LUKS, encrypted EBS). In Transit: шифрование соединения с БД через SSL/TLS. Оба необходимы для compliance (GDPR, PCI DSS) и защиты от физического доступа.

Что такое принцип Least Privilege для БД?
?
Каждому пользователю/сервису — минимально необходимые права. Приложение: SELECT/INSERT/UPDATE, не SUPERUSER. Миграции: отдельный пользователь с DDL-правами. Мониторинг: read-only роль. Уменьшает ущерб при компрометации.

Что показывает pg_stat_activity?
?
Текущие активные соединения и запросы: PID, state (active/idle/waiting), query, wait_event, query_start. Используется для диагностики: заблокированные запросы, длинные транзакции, idle in transaction connections.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cloud-databases-complete]] | Managed monitoring и security в облаке |
| Углубиться | [[database-design-optimization]] | Оптимизация найденных медленных запросов |
| Смежная тема | [[security-fundamentals]] | Общие принципы безопасности приложений |
| Смежная тема | [[observability]] | Prometheus, Grafana, distributed tracing |
| Обзор | [[databases-overview]] | Вернуться к карте раздела |

---

*Обновлено: 2026-01-09 — добавлены педагогические секции (5 аналогий: охранная система/defense in depth, VIP-клуб/RLS, банковский сейф/encryption, больница/least privilege, видеорегистратор/audit; 6 типичных ошибок включая SQL injection; 5 ментальных моделей безопасности) | PostgreSQL 16*

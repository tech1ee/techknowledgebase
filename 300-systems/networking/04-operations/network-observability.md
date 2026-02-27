---
title: "Network Observability"
created: 2025-01-15
modified: 2026-02-13
tags:
  - topic/networking
  - observability
  - monitoring
  - prometheus
  - grafana
  - tracing
  - type/concept
  - level/intermediate
related:
  - [network-debugging-basics]]
  - "[[network-performance-optimization]]"
  - "[[network-kubernetes-deep-dive]"
prerequisites:
  - "[[network-debugging-basics]]"
  - "[[network-fundamentals-for-developers]]"
status: published
reading_time: 65
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Network Observability

---

## Теоретические основы

> **Network Telemetry** — систематический сбор данных о состоянии и поведении сети. В отличие от мониторинга (проверка известных метрик), telemetry обеспечивает observability — способность понимать внутреннее состояние системы по её внешним выходным данным (Charity Majors, 2018).

### Модели сетевой телеметрии

| Технология | Модель сбора | Гранулярность | Overhead | Стандарт |
|------------|-------------|---------------|----------|----------|
| SNMP | Pull (polling) | Счётчики интерфейсов | Низкий | RFC 3416 (v2c), RFC 3414 (v3) |
| NetFlow / IPFIX | Push (export) | Потоки (5-tuple) | Средний | RFC 7011 (IPFIX), Cisco NetFlow v9 |
| sFlow | Sampling | Сэмплированные пакеты | Низкий | RFC 3176 (InMon, 2001) |
| OpenTelemetry | Push (OTLP) | Spans, metrics, logs | Настраиваемый | CNCF OpenTelemetry Spec (2019+) |
| eBPF/XDP | Kernel hooks | Пакеты, syscalls | Минимальный | Linux Kernel 4.18+ |
| Streaming Telemetry | Push (gRPC) | Структурированные данные | Настраиваемый | gNMI (OpenConfig) |

### RED метрики для сетевых сервисов

> **RED (Rate, Errors, Duration)** — методология мониторинга сервисов, предложенная Tom Wilkie (Grafana Labs, 2018). Для сетевых сервисов RED транслируется как:
> - **Rate** — количество запросов/пакетов в секунду (packets/sec, requests/sec)
> - **Errors** — частота ошибок (retransmissions, 5xx, packet drops)
> - **Duration** — задержка обработки (RTT, TTFB, P50/P95/P99 latency)

### USE метрики для сетевой инфраструктуры

| Метрика | Определение | Пример для сети | Инструмент |
|---------|-------------|-----------------|------------|
| **Utilization** | % использования ресурса | Bandwidth utilization (%) | SNMP, Prometheus node_exporter |
| **Saturation** | Очередь / backlog | TX/RX queue length, conntrack table | `ss -s`, `nstat` |
| **Errors** | Счётчик ошибок | CRC errors, drops, overruns | `ethtool -S`, `ip -s link` |

### Три столпа observability

- **Metrics** (числовые агрегаты) — "что происходит?" — Prometheus, SNMP, StatsD
- **Logs** (структурированные события) — "почему?" — Loki, ELK, Fluentd
- **Traces** (путь запроса) — "где именно?" — Jaeger, Zipkin, Tempo

> **Golden Signals** (Google SRE Book, Beyer et al., 2016): Latency, Traffic, Errors, Saturation — четыре метрики, достаточные для мониторинга любого сервиса. Это расширение RED-модели с добавлением Saturation.

**См. также:** [[network-debugging-basics]] (ручная диагностика как дополнение к observability), [[network-performance-optimization]] (оптимизация на основе метрик), [[network-kubernetes-deep-dive]] (observability в K8s)

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Сетевые основы** | Что мониторим | [[network-fundamentals-for-developers]] |
| **Debugging** | Диагностика проблем | [[network-debugging-basics]] |
| **Docker/K8s basics** | Контейнерная observability | [[network-kubernetes-deep-dive]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ⚠️ С подготовкой | Сначала debugging basics |
| **Intermediate** | ✅ Да | Основная аудитория |
| **Advanced** | ✅ Да | Distributed tracing |

### Терминология для новичков

> 💡 **Observability** = способность понять что происходит внутри системы по внешним сигналам. Как приборная панель в машине.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Metrics** | Числовые показатели | **Спидометр** — скорость прямо сейчас |
| **Logs** | Записи событий | **Бортовой журнал** — что произошло |
| **Traces** | Путь запроса через систему | **GPS-трек** — откуда куда ехали |
| **Prometheus** | Система сбора метрик | **Центр сбора показаний** |
| **Grafana** | Визуализация метрик | **Приборная панель** — красивые графики |
| **Alerting** | Оповещение о проблемах | **Сигнализация** — если что-то не так |
| **SLI/SLO** | Service Level Indicators/Objectives | **KPI для сервиса** — какой уровень качества |
| **MTTR** | Mean Time To Recovery | **Как быстро чиним** |
| **Latency percentile** | p50, p99 — процентили задержки | **Обычная vs худшая скорость** |
| **Golden Signals** | Latency, Traffic, Errors, Saturation | **4 главных показателя** |

---

## Часть 1: Интуиция без кода

> 🎯 **Цель секции**: Понять observability через повседневные аналогии — без единой строки конфигурации или запросов.

### Аналогия 1: Observability как приборная панель самолёта

```
+------------------------------------------------------------------+
|                    КАБИНА ПИЛОТА                                  |
|                                                                    |
|   +-------------+  +-------------+  +-------------+               |
|   |  СПИДОМЕТР  |  |   БОРТОВОЙ  |  |  GPS-ТРЕК   |               |
|   |  (Metrics)  |  |   ЖУРНАЛ    |  |  (Traces)   |               |
|   |             |  |   (Logs)    |  |             |               |
|   |  "Скорость  |  |  "Что       |  | "Откуда     |               |
|   |   сейчас    |  |   произошло |  |  прилетели, |               |
|   |   280 км/ч" |  |   в 14:32?" |  |  как летели"|               |
|   +-------------+  +-------------+  +-------------+               |
|                                                                    |
|   Monitoring: "Скорость в норме? ДА/НЕТ"                          |
|   Observability: "ПОЧЕМУ скорость упала в зоне турбулентности?"   |
+------------------------------------------------------------------+
```

**Ключевое различие:**
- **Monitoring** = "Всё в порядке?" (да/нет)
- **Observability** = "Почему это произошло?" (понимание)

Пилот не просто смотрит: "Двигатель работает". Он видит температуру, давление, расход топлива, историю изменений — и может понять ПОЧЕМУ двигатель ведёт себя странно.

---

### Аналогия 2: Три столпа как три типа врачей

```
+------------------------------------------------------------------+
|                     БОЛЬНИЦА (Ваша система)                       |
|                                                                    |
|   +----------------+  +----------------+  +----------------+      |
|   |   ТЕРАПЕВТ     |  |    ИСТОРИК     |  |   ХИРУРГ       |      |
|   |   (Metrics)    |  |    (Logs)      |  |   (Traces)     |      |
|   +----------------+  +----------------+  +----------------+      |
|   |                |  |                |  |                |      |
|   | "Температура   |  | "Пациент       |  | "Проследим     |      |
|   |  37.5, пульс   |  |  жаловался     |  |  путь инфекции |      |
|   |  85, давление  |  |  на головную   |  |  от точки      |      |
|   |  120/80"       |  |  боль в 14:00, |  |  входа до      |      |
|   |                |  |  потом на      |  |  органа"       |      |
|   | АГРЕГИРОВАННЫЕ |  |  тошноту..."   |  |                |      |
|   | ЧИСЛА          |  | СОБЫТИЯ        |  | ПУТЬ           |      |
|   +----------------+  +----------------+  +----------------+      |
|                                                                    |
|   Все три вместе = полная картина состояния пациента              |
+------------------------------------------------------------------+
```

**Когда что использовать:**

| Вопрос | Столп | Почему |
|--------|-------|--------|
| "Сколько запросов в секунду?" | Metrics | Агрегированные числа |
| "Что именно вернул API в 14:32?" | Logs | Конкретное событие |
| "Почему запрос шёл 5 секунд?" | Traces | Путь через сервисы |

---

### Аналогия 3: Prometheus + Grafana как сборщик новостей + телеканал

```
    СЕРВИСЫ (источники новостей)
    +-------+  +-------+  +-------+  +-------+
    |App A  |  |App B  |  |DB     |  |Cache  |
    |:8080  |  |:8080  |  |:9104  |  |:9121  |
    +---+---+  +---+---+  +---+---+  +---+---+
        |          |          |          |
        v          v          v          v
    +------------------------------------------+
    |           PROMETHEUS                      |
    |        (Корреспондент)                    |
    |                                           |
    |  "Каждые 15 секунд я обхожу все          |
    |   источники и записываю показания"        |
    |                                           |
    |  Pull-модель: Prometheus САМИ             |
    |  приходит за метриками                    |
    +---------------------+--------------------+
                          |
                          v
    +------------------------------------------+
    |           GRAFANA                         |
    |        (Телеканал)                        |
    |                                           |
    |  "Я беру данные от корреспондента         |
    |   и показываю красивые графики"           |
    |                                           |
    |  Dashboards, Alerts, Annotations          |
    +------------------------------------------+

    Prometheus НЕ рисует графики — только собирает и хранит.
    Grafana НЕ собирает метрики — только визуализирует.
```

**Почему pull-модель лучше push:**
- Prometheus контролирует частоту опроса
- Если сервис упал — это видно (scrape failed)
- Проще масштабировать — добавляешь targets
- Нет "штормов" от сервисов, которые пушат много данных

---

### Аналогия 4: Golden Signals как четыре показателя здоровья

```
+------------------------------------------------------------------+
|                    GOLDEN SIGNALS (Google SRE)                    |
|                                                                    |
|   +---------------+  +---------------+                            |
|   |   LATENCY     |  |   TRAFFIC     |                            |
|   |   (Пульс)     |  |   (Дыхание)   |                            |
|   +---------------+  +---------------+                            |
|   | Как быстро    |  | Сколько       |                            |
|   | отвечаем?     |  | работы        |                            |
|   |               |  | делаем?       |                            |
|   | p50 = 100ms   |  | 1000 req/s    |                            |
|   | p99 = 500ms   |  |               |                            |
|   +---------------+  +---------------+                            |
|                                                                    |
|   +---------------+  +---------------+                            |
|   |   ERRORS      |  |  SATURATION   |                            |
|   | (Температура) |  | (Давление)    |                            |
|   +---------------+  +---------------+                            |
|   | Сколько       |  | Насколько     |                            |
|   | ошибок?       |  | загружены?    |                            |
|   |               |  |               |                            |
|   | 0.1% 5xx      |  | CPU 70%       |                            |
|   | 0.5% timeout  |  | Memory 85%    |                            |
|   +---------------+  +---------------+                            |
|                                                                    |
|   Если эти 4 показателя в норме — сервис здоров.                  |
|   Если хотя бы один выходит за пределы — время разбираться.       |
+------------------------------------------------------------------+
```

**Альтернатива — RED Method:**
- **R**ate: запросов в секунду
- **E**rrors: ошибок в секунду
- **D**uration: время ответа

USE Method (для инфраструктуры):
- **U**tilization: % использования
- **S**aturation: очередь/backlog
- **E**rrors: количество ошибок

---

### Аналогия 5: Distributed Tracing как GPS-трек посылки

```
    Вы заказали товар. Где он сейчас?

    +------------------------------------------------------------------+
    |  TRACE ID: abc-123 (Номер отслеживания посылки)                  |
    +------------------------------------------------------------------+
    |                                                                   |
    |  SPAN 1: API Gateway (Приём заказа)                              |
    |  +--[============]----------------------------------------+      |
    |  | 0ms                                            50ms    |      |
    |                                                                   |
    |      SPAN 2: Auth Service (Проверка документов)                  |
    |      +-----[====]----------------------------------------+       |
    |      |    50ms    80ms                                    |       |
    |                                                                   |
    |          SPAN 3: Order Service (Обработка заказа)                |
    |          +-------[====================]-----------------+        |
    |          |       80ms                  200ms             |        |
    |                                                                   |
    |              SPAN 4: Database (Сохранение в БД)                  |
    |              +----------[========]--------------------+          |
    |              |         100ms    150ms                  |          |
    |                                                                   |
    |              SPAN 5: Notification (Отправка SMS)                 |
    |              +----------[====]------------------------+          |
    |              |         100ms 120ms                     |          |
    |                                                                   |
    +------------------------------------------------------------------+
    |  Total: 200ms | Bottleneck: Order Service (120ms = 60%)          |
    +------------------------------------------------------------------+

    Без трейсинга: "Запрос шёл 200ms, не знаю где задержка"
    С трейсингом: "Order Service занял 60% времени — копаем туда"
```

**Ключевые концепции:**
- **Trace** = весь путь запроса (одна посылка)
- **Span** = один этап пути (один склад/транспорт)
- **Parent-Child** = вложенность (span внутри span)
- **Context Propagation** = передача trace-id между сервисами

---

## Часть 2: Почему это сложно

> 🎯 **Цель секции**: Изучить 6 типичных ошибок, с которыми сталкиваются команды при внедрении observability.

### Ошибка 1: Думать что Prometheus + Grafana = Observability

**СИМПТОМ:**
```
"У нас есть observability — вот наши дашборды в Grafana!"
(показывает 50 графиков CPU/Memory/Disk)

При инциденте:
- "Почему запросы медленные?" — "Не знаю, CPU в норме"
- "Какие запросы затронуты?" — "Не знаю, нет логов"
- "Где именно задержка?" — "Не знаю, нет трейсов"
```

**Почему происходит:**
Команды путают **monitoring** (слежение за известными метриками) с **observability** (способность исследовать неизвестные проблемы).

**РЕШЕНИЕ:**
```
Monitoring:                    Observability:
"CPU > 80%? Alert!"            "ПОЧЕМУ CPU > 80%?"
"Error rate > 1%? Alert!"      "КАКИЕ запросы вызывают ошибки?"
"Latency > 500ms? Alert!"      "ГДЕ в цепочке сервисов задержка?"

Что нужно добавить к Prometheus + Grafana:
+---------------+  +---------------+  +---------------+
|   Metrics     |  |     Logs      |  |    Traces     |
|  Prometheus   |  |     Loki      |  |    Tempo      |
|   Grafana     |  |    Grafana    |  |   Grafana     |
+---------------+  +---------------+  +---------------+
        |                  |                 |
        +------------------+-----------------+
                           |
                   КОРРЕЛЯЦИЯ!
            (один инструмент для всех трёх)
```

---

### Ошибка 2: Alert Fatigue — слишком много алертов

**СИМПТОМ:**
```
Slack канал #alerts:
08:00 [WARN] CPU > 70% on node-1
08:01 [WARN] CPU > 70% on node-2
08:02 [WARN] Memory > 80% on node-3
08:03 [WARN] Disk > 75% on node-1
08:04 [WARN] CPU > 70% on node-1  (опять)
...
(100+ алертов в день, команда игнорирует канал)

09:30 [CRITICAL] Database connection pool exhausted
      ^^^ Никто не заметил среди шума
```

**Почему происходит:**
- Алерты на каждую метрику "на всякий случай"
- Слишком низкие пороги (CPU 70% — это нормально!)
- Нет агрегации и дедупликации
- Алерты на симптомы, а не на влияние на пользователей

**РЕШЕНИЕ:**
```
ПЛОХО: Алерт на каждую ноду отдельно
ХОРОШО: Алерт когда >30% нод имеют проблему

ПЛОХО: CPU > 70% (это нормальная нагрузка)
ХОРОШО: CPU > 95% более 5 минут И latency выросла

ПЛОХО: 100 алертов "Pod restarted"
ХОРОШО: "5+ подов сервиса X рестартовали за 10 минут"

Правило SRE: Алерт должен требовать действия.
Если действие не нужно — это не алерт, это лог.

Пирамида алертов:
        /\
       /  \  Page (будит ночью) — только critical
      /----\
     /      \ Ticket (на утро) — важно, но не срочно
    /--------\
   /          \ Dashboard (информация) — не алерт!
```

---

### Ошибка 3: Собирать всё подряд без стратегии

**СИМПТОМ:**
```
- 10,000+ метрик на сервис
- 500GB логов в день
- Prometheus OOM каждую неделю
- Loki тормозит на запросах
- Счёт за storage растёт экспоненциально

"Мы собираем всё, потому что не знаем что понадобится"
```

**Почему происходит:**
- Экспортеры по умолчанию включают все метрики
- Логи пишут на DEBUG уровне в production
- Нет retention policy
- "Вдруг понадобится"

**РЕШЕНИЕ:**
```
Стратегия "80/20":
- 80% проблем решаются 20% метрик
- Начните с Golden Signals для каждого сервиса
- Добавляйте метрики когда они НУЖНЫ, не заранее

Пример node_exporter:
# ПЛОХО: все 1000+ метрик
--collector.enabled

# ХОРОШО: только нужные
--collector.cpu
--collector.meminfo
--collector.diskstats
--collector.netdev
--no-collector.wifi  # не нужно на серверах

Retention policy:
- Raw metrics: 15 дней
- Downsampled (1h): 90 дней
- Downsampled (1d): 1 год
- Логи DEBUG: 1 день
- Логи ERROR: 30 дней
```

---

### Ошибка 4: Метрики без контекста (missing labels)

**СИМПТОМ:**
```
# Видите высокую latency:
http_request_duration_seconds{quantile="0.99"} 2.5

# Вопрос: "Какой эндпоинт? Какой метод? Какой статус?"
# Ответ: "Не знаю, нет labels"

# Приходится угадывать или перезапускать с новыми метриками
```

**Почему происходит:**
- Labels добавляют не сразу
- Боязнь cardinality explosion
- Копирование конфигов без понимания

**РЕШЕНИЕ:**
```
# ПЛОХО: одна метрика на всё
http_requests_total 15000

# ХОРОШО: labels для фильтрации
http_requests_total{
  method="GET",           # HTTP метод
  endpoint="/api/users",  # Какой эндпоинт
  status="200",           # Код ответа
  service="user-api"      # Какой сервис
} 12000

http_requests_total{
  method="POST",
  endpoint="/api/orders",
  status="500",
  service="order-api"
} 50

# Теперь можно:
sum by (endpoint) (rate(http_requests_total[5m]))
sum by (status) (rate(http_requests_total{status=~"5.."}[5m]))

⚠️ НО: Избегайте высокой cardinality!
ПЛОХО: label user_id (миллионы уникальных значений)
ХОРОШО: label user_type (free, premium, enterprise)
```

---

### Ошибка 5: Нет корреляции между тремя столпами

**СИМПТОМ:**
```
Инцидент: "API медленный"

В Grafana (metrics): Видим spike latency в 14:32
В Loki (logs): Видим ошибки... но в каком сервисе?
В Jaeger (traces): Где trace для этого запроса?

Приходится вручную сопоставлять timestamp'ы,
переключаться между 3 интерфейсами,
угадывать связи.

Время на диагностику: 45 минут вместо 5.
```

**Почему происходит:**
- Три разных инструмента без интеграции
- Нет общего идентификатора (trace_id) во всех сигналах
- Разные retention/timestamp precision

**РЕШЕНИЕ:**
```
Интеграция через trace_id:

1. Генерируйте trace_id на входе (API Gateway)
2. Пробрасывайте в логах:
   logger.info("Order created", extra={"trace_id": trace_id})
3. Добавляйте в метрики как exemplar:
   http_requests_total{...} 1 # trace_id=abc123

В Grafana:
+------------------------------------------------------------------+
|  [График latency spike в 14:32]                                  |
|                    |                                              |
|                    v (клик на точку)                              |
|  "Показать exemplar traces" → Tempo                              |
|                    |                                              |
|                    v (клик на trace)                              |
|  "Показать логи для trace_id=abc123" → Loki                      |
+------------------------------------------------------------------+

Grafana + Tempo + Loki + Prometheus = единая картина
```

---

### Ошибка 6: Дашборды без смысла (vanity dashboards)

**СИМПТОМ:**
```
Dashboard "Система Мониторинга v2.0":
- 47 графиков
- 12 круговых диаграмм
- Всё зелёное
- Никто не смотрит
- При инциденте: "Где посмотреть что сломалось?"

"Dashboard выглядит круто на демо, но бесполезен в бою"
```

**Почему происходит:**
- Дашборды создаются "для красоты"
- Нет ответа на конкретный вопрос
- Слишком много информации
- Нет фильтров/drill-down

**РЕШЕНИЕ:**
```
Каждый dashboard должен отвечать на ОДИН вопрос:

+------------------------------------------------------------------+
|  Dashboard: "Здоровье API Gateway"                               |
|  Вопрос: "Работает ли API нормально для пользователей?"          |
+------------------------------------------------------------------+
|                                                                   |
|  [Request Rate]     [Error Rate]    [P99 Latency]                |
|   ███████████        █                ██████████                  |
|   1.2k req/s         0.1%             120ms                       |
|                                                                   |
|  [Top 5 Slow Endpoints]              [Recent Errors]             |
|  1. /api/search - 450ms              POST /api/orders - 500      |
|  2. /api/export - 320ms              GET /api/users - 502        |
|                                                                   |
|  [Drill-down по endpoint] [Drill-down по статусу]                |
+------------------------------------------------------------------+

Правила хорошего dashboard:
1. Один dashboard = один use case
2. Сверху — общая картина (SLIs)
3. Снизу — детали для диагностики
4. Фильтры: по сервису, времени, endpoint
5. Ссылки на связанные dashboards и traces
```

---

## Часть 3: Ментальные модели

> 🎯 **Цель секции**: 5 способов думать об observability, которые упрощают понимание и принятие решений.

### Модель 1: Вопрос определяет инструмент

```
+------------------------------------------------------------------+
|                 КАКОЙ ВОПРОС ВЫ ЗАДАЁТЕ?                         |
+------------------------------------------------------------------+
|                                                                   |
|  "Что происходит         "Что конкретно       "Как запрос        |
|   СЕЙЧАС?"               случилось?"           прошёл?"           |
|       |                       |                    |              |
|       v                       v                    v              |
|   METRICS                   LOGS                TRACES            |
|       |                       |                    |              |
|       v                       v                    v              |
|   "Latency              "Connection           "Auth Service      |
|    выросла               refused from         занял 80%          |
|    до 500ms"             DB at 14:32:15"      времени"           |
|                                                                   |
+------------------------------------------------------------------+

Workflow при инциденте:
1. METRICS: "Что сломалось?" → Видим spike errors на графике
2. LOGS: "Когда и что именно?" → Находим error message
3. TRACES: "Где в цепочке?" → Видим bottleneck сервис
```

---

### Модель 2: MELT Framework

```
+------------------------------------------------------------------+
|                    MELT Framework                                 |
|           (Metrics, Events, Logs, Traces)                        |
+------------------------------------------------------------------+
|                                                                   |
|   M - Metrics    │ Агрегированные числа over time                |
|                  │ "Среднее", "сумма", "процентиль"              |
|                  │ Пример: p99 latency = 200ms                   |
|   ───────────────┼───────────────────────────────────────────    |
|   E - Events     │ Дискретные значимые события                   |
|                  │ "Деплой", "рестарт", "config change"          |
|                  │ Пример: Deployed v2.3.1 at 14:00              |
|   ───────────────┼───────────────────────────────────────────    |
|   L - Logs       │ Детальные записи того что произошло           |
|                  │ Текст + структурированные данные              |
|                  │ Пример: {"level":"error","msg":"timeout"}     |
|   ───────────────┼───────────────────────────────────────────    |
|   T - Traces     │ Путь запроса через распределённую систему     |
|                  │ Spans, timing, parent-child                   |
|                  │ Пример: Request abc → A → B → C (250ms)       |
|                                                                   |
+------------------------------------------------------------------+

Events часто упускают!
Annotations в Grafana = когда был деплой, когда меняли конфиг.
Корреляция: "Latency выросла сразу после деплоя v2.3.1"
```

---

### Модель 3: SLI → SLO → SLA Pipeline

```
                      ОПРЕДЕЛЕНИЯ
    +----------------------------------------------------------+
    |                                                          |
    |  SLI (Service Level Indicator)                           |
    |  = ЧТО измеряем                                          |
    |  "Процент запросов с latency < 200ms"                    |
    |                                                          |
    |           ↓                                              |
    |                                                          |
    |  SLO (Service Level Objective)                           |
    |  = ЦЕЛЬ которую хотим достичь                            |
    |  "99.9% запросов должны быть < 200ms"                    |
    |                                                          |
    |           ↓                                              |
    |                                                          |
    |  SLA (Service Level Agreement)                           |
    |  = КОНТРАКТ с последствиями                              |
    |  "Если < 99.9% — возврат денег клиенту"                  |
    |                                                          |
    +----------------------------------------------------------+

    Error Budget = сколько можно "сломать":
    +----------------------------------------------------------+
    |  SLO: 99.9% availability                                  |
    |                                                           |
    |  За месяц (30 дней):                                      |
    |  - Всего минут: 30 × 24 × 60 = 43,200                    |
    |  - Допустимый downtime: 0.1% = 43.2 минуты               |
    |                                                           |
    |  Если за месяц было 20 минут downtime:                   |
    |  - Осталось: 23.2 минуты error budget                    |
    |  - Можно делать рискованные деплои!                      |
    |                                                           |
    |  Если за месяц было 50 минут downtime:                   |
    |  - Error budget исчерпан!                                 |
    |  - Стоп деплои, фокус на стабильность                    |
    +----------------------------------------------------------+
```

---

### Модель 4: Observability Maturity Model

```
Level 0: СЛЕПОТА
+------------------------------------------------------------------+
| "Узнаём о проблемах от пользователей"                            |
| • Нет метрик                                                      |
| • Логи на сервере (если повезёт)                                 |
| • MTTR: часы-дни                                                  |
+------------------------------------------------------------------+
        ↓
Level 1: БАЗОВЫЙ МОНИТОРИНГ
+------------------------------------------------------------------+
| "Знаем что сломалось, но не почему"                              |
| • Infrastructure metrics (CPU, memory, disk)                     |
| • Basic alerting                                                 |
| • MTTR: 30-60 минут                                              |
+------------------------------------------------------------------+
        ↓
Level 2: APPLICATION METRICS
+------------------------------------------------------------------+
| "Знаем какой сервис сломался"                                    |
| • Golden Signals для каждого сервиса                             |
| • Централизованные логи                                          |
| • MTTR: 15-30 минут                                              |
+------------------------------------------------------------------+
        ↓
Level 3: DISTRIBUTED TRACING
+------------------------------------------------------------------+
| "Знаем где именно в цепочке проблема"                            |
| • End-to-end tracing                                             |
| • Корреляция metrics ↔ logs ↔ traces                             |
| • MTTR: 5-15 минут                                               |
+------------------------------------------------------------------+
        ↓
Level 4: PROACTIVE OBSERVABILITY
+------------------------------------------------------------------+
| "Находим проблемы ДО того как они влияют на пользователей"       |
| • Anomaly detection                                               |
| • SLO-based alerting                                              |
| • Chaos engineering                                               |
| • MTTR: минуты (или проблема предотвращена)                      |
+------------------------------------------------------------------+
```

---

### Модель 5: Observability как исследование unknown unknowns

```
+------------------------------------------------------------------+
|                    Матрица знания проблем                        |
+------------------------------------------------------------------+
|                                                                   |
|              │     ИЗВЕСТНО          НЕИЗВЕСТНО                  |
|              │     (что искать)      (что искать)                |
|   ───────────┼──────────────────────────────────────────         |
|   ИЗВЕСТНО   │  Known Knowns         Unknown Knowns              |
|   (что       │  "CPU > 90% = плохо"  "Есть метрика,              |
|   происходит)│                        но не смотрим"             |
|              │  → МОНИТОРИНГ          → DASHBOARD                |
|   ───────────┼──────────────────────────────────────────         |
|   НЕИЗВЕСТНО │  Known Unknowns       Unknown Unknowns            |
|   (что       │  "Знаем что может     "Не знаем что              |
|   происходит)│   сломаться DNS"      может сломаться"           |
|              │                                                    |
|              │  → ALERTING           → OBSERVABILITY             |
|                                                                   |
+------------------------------------------------------------------+

Monitoring отвечает на: "Работает ли X?" (known knowns)
Observability отвечает на: "Что пошло не так?" (unknown unknowns)

Пример unknown unknown:
- Memory leak только при определённом паттерне запросов
- Race condition при высокой нагрузке
- Cascade failure из-за timeout в одном сервисе

Чтобы найти unknown unknowns нужны:
1. High-cardinality данные (не только агрегаты)
2. Возможность ad-hoc запросов (не только предзаданные dashboard)
3. Корреляция между разными сигналами
4. Context propagation (trace_id везде)
```

---

## Почему это важно

**Observability** — это способность понять внутреннее состояние системы по её внешним сигналам. Для сетей это означает возможность ответить на вопрос: **"Почему запрос был медленным?"** без угадывания.

### Three Pillars of Observability

```
┌─────────────────────────────────────────────────────────────┐
│                    Observability                            │
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐        │
│  │   Metrics   │   │    Logs     │   │   Traces    │        │
│  │ (числа, ряды)│   │ (события)  │   │ (путь req)  │        │
│  │             │   │             │   │             │        │
│  │ Prometheus  │   │   Loki      │   │   Jaeger    │        │
│  │ Grafana     │   │   ELK       │   │   Tempo     │        │
│  └─────────────┘   └─────────────┘   └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

| Pillar | Отвечает на вопрос | Инструменты |
|--------|-------------------|-------------|
| **Metrics** | "Что происходит?" (агрегировано) | Prometheus, Grafana |
| **Logs** | "Что конкретно произошло?" | Loki, ELK, Fluentd |
| **Traces** | "Как запрос прошёл через систему?" | Jaeger, Tempo, Zipkin |

### Проблемы без observability

- **MTTR выше** — угадываешь, а не диагностируешь
- **Blind spots** — не видишь, где теряется время
- **Reactive** — узнаёшь о проблемах от пользователей

---

## Metrics с Prometheus

### Почему Prometheus — стандарт

> **75% организаций** используют Prometheus в production (Grafana Survey 2024)

- Pull-based модель — Prometheus сам собирает метрики
- PromQL — мощный язык запросов
- Multi-dimensional — labels для фильтрации
- Integrations — тысячи exporters

### Ключевые сетевые метрики

```yaml
# Метрики от node_exporter
node_network_receive_bytes_total     # Принятые байты
node_network_transmit_bytes_total    # Отправленные байты
node_network_receive_packets_total   # Принятые пакеты
node_network_transmit_drop_total     # Dropped при отправке
node_network_receive_errs_total      # Ошибки приёма

# Метрики от kube-state-metrics (K8s)
kube_pod_container_status_restarts_total  # Рестарты (сетевые проблемы?)
```

### PromQL примеры

```promql
# Bandwidth per interface (bytes/sec)
rate(node_network_receive_bytes_total[5m])

# Packet loss rate
rate(node_network_transmit_drop_total[5m]) /
rate(node_network_transmit_packets_total[5m]) * 100

# HTTP latency P99
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
)

# Requests per second by service
sum by (service) (
  rate(http_requests_total[1m])
)
```

### SNMP Exporter для сетевого оборудования

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'snmp'
    static_configs:
      - targets:
          - 192.168.1.1  # Router
          - 192.168.1.2  # Switch
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: snmp-exporter:9116
```

### Blackbox Exporter — проверка connectivity

```yaml
modules:
  http_2xx:
    prober: http
    http:
      preferred_ip_protocol: "ip4"
  tcp_connect:
    prober: tcp
  icmp:
    prober: icmp
```

```yaml
# prometheus.yml
- job_name: 'blackbox'
  metrics_path: /probe
  params:
    module: [http_2xx]
  static_configs:
    - targets:
        - https://api.example.com
        - https://website.example.com
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - target_label: __address__
      replacement: blackbox-exporter:9115
```

---

## Distributed Tracing

### Проблема, которую решает трейсинг

**Логи показывают "что случилось", но не "как связано".** В монолите запрос проходит через один процесс — stack trace показывает весь путь. В микросервисах запрос проходит через десятки процессов на разных машинах. Каждый сервис логирует свою часть, но как собрать целую картину?

**Без трейсинга диагностика выглядит так:**
1. Пользователь жалуется на медленный checkout
2. Смотрим логи API gateway — всё ок
3. Смотрим логи payment service — тоже ок
4. Потратили час, выяснили что проблема в inventory service

**С трейсингом:**
1. Находим trace по request_id
2. Видим timeline: API (10ms) → Auth (5ms) → Inventory (890ms) → Payment (15ms)
3. Сразу понятно где bottleneck

### Зачем нужен трейсинг

В микросервисах один запрос проходит через **десятки сервисов**. Без трейсинга невозможно понять:
- Где теряется время?
- Какой сервис вызвал ошибку?
- Как связаны события?

```
User Request → API Gateway → Auth Service → User Service → DB
                    ↓
              Product Service → Inventory → Cache
                    ↓
              Order Service → Payment API (external)
```

### Концепции

| Термин | Описание |
|--------|----------|
| **Trace** | Путь одного запроса через всю систему |
| **Span** | Одна операция в рамках trace |
| **Context Propagation** | Передача trace ID между сервисами |
| **Sampling** | Сбор только части traces (экономия) |

### OpenTelemetry

> OpenTelemetry — **#2 по активности CNCF проект** (после Kubernetes)

OpenTelemetry объединяет:
- Instrumentation SDK (авто + manual)
- Collector (сбор и пересылка)
- Semantic Conventions (стандарты именования)

```python
# Python instrumentation
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Auto-instrumentation (HTTP, DB, etc.)
from opentelemetry.instrumentation.requests import RequestsInstrumentor
RequestsInstrumentor().instrument()

# Manual span
with tracer.start_as_current_span("process_payment") as span:
    span.set_attribute("payment.amount", 99.99)
    span.set_attribute("payment.currency", "USD")
    # ... business logic
```

### Jaeger

```yaml
# docker-compose.yml для Jaeger
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

**Jaeger UI показывает:**
- Timeline каждого span
- Service dependency map
- Latency breakdown
- Error traces

### Sampling стратегии

| Стратегия | Описание | Когда использовать |
|-----------|----------|-------------------|
| **Always** | 100% traces | Dev/staging |
| **Probabilistic** | % от трафика | High-volume production |
| **Rate Limiting** | N traces/sec | Контроль стоимости |
| **Tail-based** | Решение после trace | Только ошибки/slow requests |

```yaml
# OTel Collector config
processors:
  probabilistic_sampler:
    sampling_percentage: 10  # 10% traces
```

---

## Grafana Dashboards

### Сетевой Dashboard

Ключевые панели:

1. **Bandwidth** — `rate(node_network_*_bytes_total[5m])`
2. **Packets/sec** — `rate(node_network_*_packets_total[5m])`
3. **Errors** — `rate(node_network_*_errs_total[5m])`
4. **Latency P50/P95/P99** — `histogram_quantile(...)`
5. **Availability** — `up{job="blackbox"}` + probe_success

### Пример Dashboard JSON (snippet)

```json
{
  "panels": [
    {
      "title": "Network Throughput",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum(rate(node_network_receive_bytes_total[5m])) by (device)",
          "legendFormat": "{{device}} RX"
        },
        {
          "expr": "sum(rate(node_network_transmit_bytes_total[5m])) by (device)",
          "legendFormat": "{{device}} TX"
        }
      ]
    }
  ]
}
```

### RED Metrics для Services

| Metric | Что показывает | PromQL |
|--------|---------------|--------|
| **R**ate | Requests/sec | `rate(http_requests_total[5m])` |
| **E**rrors | Error rate | `rate(http_requests_total{status=~"5.."}[5m])` |
| **D**uration | Latency | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` |

### USE Metrics для Infrastructure

| Metric | Что показывает | Пример |
|--------|---------------|--------|
| **U**tilization | % использования | CPU, memory, bandwidth |
| **S**aturation | Очередь/backlog | TCP retransmits, queue depth |
| **E**rrors | Ошибки | Packet drops, CRC errors |

---

## Alerting Best Practices

### Правила alerting

1. **Actionable** — каждый alert требует действия
2. **Duration-based** — не реагируй на спайки
3. **Prioritized** — critical vs warning
4. **Documented** — runbook для каждого alert

### Примеры alert rules

```yaml
# prometheus/rules.yml
groups:
  - name: network
    rules:
      # High packet loss
      - alert: HighPacketLoss
        expr: |
          rate(node_network_transmit_drop_total[5m]) /
          rate(node_network_transmit_packets_total[5m]) > 0.01
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High packet loss on {{ $labels.device }}"
          runbook_url: "https://wiki/runbooks/packet-loss"

      # Service down
      - alert: ServiceDown
        expr: probe_success == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.instance }} is down"

      # High latency
      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency > 500ms for {{ $labels.service }}"
```

### Избежание Alert Fatigue

| Проблема | Решение |
|----------|---------|
| Слишком много alerts | Увеличь duration (for: 5m → 10m) |
| Ложные срабатывания | Настрой thresholds по baseline |
| Повторяющиеся alerts | Alert correlation/grouping |
| Неясно что делать | Добавь runbook_url |

### Escalation

```
Level 1: Slack notification (warning)
    ↓ 5 min no ack
Level 2: PagerDuty (on-call)
    ↓ 15 min no ack
Level 3: Phone call to team lead
```

---

## eBPF и Cilium Hubble

### Ограничения традиционного мониторинга

**Традиционный подход имеет blind spots:**
- **Application metrics** показывают что видит приложение, но не сеть
- **Sidecar proxies** (Istio/Envoy) добавляют latency и complexity
- **Packet capture** требует root, создаёт overhead, сложно масштабировать
- **SNMP/NetFlow** работает только для сетевого оборудования, не для софта

**eBPF меняет правила игры:** код выполняется прямо в ядре Linux, видит каждый пакет без копирования в user space, без sidecar, без overhead.

### Почему eBPF революционен

**eBPF (extended Berkeley Packet Filter)** — технология выполнения кода в ядре Linux без перезагрузки.

```
Traditional:
User space → Kernel → Network stack → Packet

eBPF:
User space → Kernel [eBPF programs] → Direct packet processing
                     ↓
              Metrics/Events to user space
```

**Преимущества:**
- Минимальный overhead
- Глубокая видимость (L3-L7)
- Real-time без sampling
- Kernel-level security

### Cilium Hubble

> Hubble = Network observability для Kubernetes на базе eBPF

**Компоненты:**
- **Hubble Server** — агент на каждой ноде (часть Cilium)
- **Hubble Relay** — агрегатор для всего кластера
- **Hubble UI** — веб-интерфейс
- **Hubble CLI** — командная строка

### Установка

```bash
# С Cilium
cilium hubble enable --ui

# Проверка статуса
cilium hubble status

# Port-forward UI
cilium hubble ui
```

### Hubble CLI

```bash
# Все flows
hubble observe

# Flows от конкретного pod
hubble observe --from-pod default/frontend

# Flows к конкретному pod
hubble observe --to-pod default/backend

# Только drops
hubble observe --verdict DROPPED

# С DNS
hubble observe --protocol DNS

# HTTP flows
hubble observe --protocol HTTP --http-status 500
```

### Hubble Metrics

```yaml
# Cilium ConfigMap
hubble:
  metrics:
    enabled:
      - dns
      - drop
      - tcp
      - flow
      - httpV2
      - icmp
      - port-distribution
```

Метрики экспортируются в Prometheus:

```promql
# DNS latency
hubble_dns_response_time_seconds_bucket

# HTTP requests by status
hubble_http_requests_total{status="200"}

# Dropped packets by reason
hubble_drop_total{reason="POLICY_DENIED"}
```

### Service Map

Hubble UI автоматически строит **service dependency map**:

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│ frontend │──────►│ backend  │──────►│   db     │
└──────────┘       └──────────┘       └──────────┘
     │                                     ▲
     │             ┌──────────┐            │
     └────────────►│  cache   │────────────┘
                   └──────────┘
```

---

## Logs и Network Visibility

### Что логировать

| Источник | Полезные данные |
|----------|----------------|
| **Firewall** | Blocked connections, source IP |
| **Load Balancer** | Request latency, backend health |
| **DNS** | Query logs, resolution time |
| **Application** | Request ID, user ID, latency |

### Structured Logging

```json
{
  "timestamp": "2024-12-26T10:30:00Z",
  "level": "info",
  "service": "api-gateway",
  "trace_id": "abc123",
  "span_id": "def456",
  "method": "POST",
  "path": "/api/orders",
  "status": 201,
  "latency_ms": 45,
  "client_ip": "10.0.0.5",
  "user_id": "user-789"
}
```

### Loki для логов

```yaml
# Loki query (LogQL)
{namespace="production", app="api"}
  | json
  | latency_ms > 500
  | line_format "{{.method}} {{.path}} - {{.latency_ms}}ms"
```

### Корреляция Logs ↔ Traces

Добавляй `trace_id` в логи:

```python
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)

def handler(request):
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id

    logger.info(
        "Processing request",
        extra={"trace_id": format(trace_id, '032x')}
    )
```

В Grafana: клик на лог → переход к trace в Jaeger.

---

## Подводные камни

### 1. Cardinality explosion

**Ошибка:** Label с высокой кардинальностью (user_id, request_id)

```promql
# Плохо — миллионы time series!
http_requests_total{user_id="..."}
```

**Решение:** Используй labels только для группировки (service, method, status)

### 2. Слишком много alerts

**Ошибка:** Alert на каждую метрику без duration

**Решение:**
- `for: 5m` минимум
- Группировка связанных alerts
- Runbook для каждого

### 3. Sampling потерял важные traces

**Ошибка:** Probabilistic sampling 1% — ошибки теряются

**Решение:** Tail-based sampling — сначала собираем, потом решаем

### 4. Нет context propagation

**Ошибка:** Trace обрывается на границе сервисов

**Решение:**
```python
# Пробрасывай headers
headers = {
    "traceparent": span.get_span_context().to_header()
}
requests.get(url, headers=headers)
```

### 5. Metrics без baseline

**Ошибка:** Alert "latency > 100ms" без понимания нормы

**Решение:**
1. Собирай данные 2 недели
2. Определи percentiles
3. Alert = значительное отклонение от baseline

### 6. Hubble только в Cilium

**Ошибка:** Ожидание Hubble без установки Cilium CNI

**Решение:** Hubble работает только с Cilium. Альтернативы: Pixie, Falco

---

## Чек-лист

### Metrics

- [ ] Prometheus собирает метрики всех сервисов
- [ ] Node exporter на каждом хосте
- [ ] Blackbox exporter для external endpoints
- [ ] Grafana dashboards для RED/USE metrics
- [ ] Retention настроен (Thanos/Mimir для long-term)

### Tracing

- [ ] OpenTelemetry SDK интегрирован
- [ ] Auto-instrumentation для HTTP/gRPC/DB
- [ ] Sampling strategy определена
- [ ] Jaeger/Tempo развёрнут
- [ ] trace_id в логах

### Alerting

- [ ] Alerts имеют duration (for: Xm)
- [ ] Severity levels (critical/warning/info)
- [ ] Runbook URL в каждом alert
- [ ] Escalation policy настроена
- [ ] Alert fatigue минимизирован

### Kubernetes

- [ ] Cilium + Hubble (если возможно)
- [ ] Network Policy visibility
- [ ] Service map актуален

---

## Связанные материалы

- [[network-troubleshooting-advanced]] — Диагностика проблем
- [[network-performance-optimization]] — Performance tuning
- [[network-latency-optimization]] — Latency analysis
- [[network-kubernetes-deep-dive]] — K8s networking + Cilium
- [[network-tools-reference]] — CLI инструменты

---

## Источники

### Теоретические основы
- Beyer B. et al. (2016). *Site Reliability Engineering* — Google. Глава "Monitoring Distributed Systems": Golden Signals
- RFC 3416 (2002). SNMP v2c — Protocol Operations
- RFC 7011 (2013). IPFIX — IP Flow Information Export Protocol
- RFC 3176 (2001). InMon Corporation's sFlow
- Wilkie T. (2018). "The RED Method" — Grafana Labs Blog
- Majors C. (2018). "Observability — A 3-Year Retrospective" — o11y.io

### Практические руководства

| # | Источник | Тип | Ключевой вклад |
|---|----------|-----|----------------|
| 1 | [Grafana Observability Survey 2024](https://grafana.com/observability-survey/2024/) | Report | Industry trends |
| 2 | [Prometheus SNMP Exporter](https://github.com/prometheus/snmp_exporter) | GitHub | Network device monitoring |
| 3 | [OpenTelemetry Docs](https://opentelemetry.io/docs/) | Docs | Instrumentation guide |
| 4 | [Jaeger Tracing](https://www.jaegertracing.io/) | Docs | Distributed tracing |
| 5 | [Cilium Hubble](https://github.com/cilium/hubble) | GitHub | eBPF observability |
| 6 | [Kentik Alerting Best Practices](https://www.kentik.com/kentipedia/network-monitoring-alerts/) | Blog | Alert management |
| 7 | [CloudRaft Network Monitoring](https://www.cloudraft.io/blog/network-monitoring-with-prometheus) | Blog | Prometheus setup |
| 8 | [Hubble Cheatsheet](https://isovalent.com/blog/post/cilium-hubble-cheat-sheet-observability/) | Blog | Hubble CLI |
| 9 | [Last9 Jaeger + OTel](https://last9.io/blog/how-to-use-jaeger-with-opentelemetry/) | Blog | Integration guide |
| 10 | [Edge Delta Alerting](https://edgedelta.com/company/blog/monitoring-and-alerting-best-practices) | Blog | Alert best practices |
| 11 | [TechTarget Alerting](https://www.techtarget.com/searchitoperations/tip/4-monitoring-and-alerting-best-practices-for-IT-ops) | Blog | IT ops alerting |
| 12 | [Obkio Dashboard Guide](https://obkio.com/blog/network-monitoring-dashboard/) | Blog | Dashboard design |
| 13 | [CloudRaft Hubble](https://www.cloudraft.io/blog/ebpf-based-network-observability-using-cilium-hubble) | Blog | eBPF observability |
| 14 | [Grafana Loki](https://grafana.com/oss/loki/) | Docs | Log aggregation |
| 15 | [ilert Alert Tuning](https://www.ilert.com/blog/6-best-practices-for-tuning-network-monitoring-alerts) | Blog | Alert tuning |

---

## Связь с другими темами

**[[network-debugging-basics]]** — Debugging basics — это первый шаг в диагностике сетевых проблем с помощью ручных инструментов (ping, traceroute, curl), тогда как observability обеспечивает автоматизированный и непрерывный мониторинг. Навыки ручной диагностики необходимы, когда observability-система показывает аномалию, но не объясняет корневую причину. Debugging basics является prerequisite для observability: нужно понимать, что искать, прежде чем автоматизировать поиск. Изучайте последовательно.

**[[network-performance-optimization]]** — Performance optimization и observability неразрывно связаны: невозможно оптимизировать то, что не измеряешь. Observability предоставляет метрики (latency, throughput, error rate), на основе которых принимаются решения об оптимизации, а performance optimization определяет, какие метрики критичны для сбора. Golden Signals (latency, traffic, errors, saturation) — это мост между наблюдаемостью и оптимизацией. Рекомендуется изучать параллельно.

**[[network-kubernetes-deep-dive]]** — Kubernetes генерирует сложные сетевые паттерны (pod-to-pod, service-to-service, ingress), которые требуют специализированных инструментов observability: Cilium Hubble для eBPF-мониторинга, distributed tracing для отслеживания запросов через service mesh, kube-state-metrics для состояния сетевых ресурсов. Без сетевой observability диагностика проблем в Kubernetes-кластере превращается в гадание. Сначала освойте основы K8s networking, затем настраивайте observability.

---

## Источники и дальнейшее чтение

### Теоретические основы
- **Kurose, Ross (2021).** *Computer Networking: A Top-Down Approach.* — фундаментальные принципы работы сетевых протоколов, знание которых необходимо для правильной интерпретации сетевых метрик и логов.
- **Beyer B. et al. (2016).** *Site Reliability Engineering.* — определение Golden Signals и подходы к мониторингу распределённых систем от Google SRE.

### Практические руководства
- **Grigorik (2013).** *High Performance Browser Networking.* — практические методы измерения и анализа сетевой производительности, включая Navigation Timing API и Resource Timing API, которые являются источниками метрик для observability.
- **Sanders (2017).** *Practical Packet Analysis with Wireshark.* — навыки глубокого анализа сетевого трафика, которые дополняют высокоуровневую observability возможностью детального расследования на уровне пакетов.

---

## Проверь себя

> [!question]- Команда установила Prometheus и Grafana, создала 50 дашбордов. Через месяц никто не смотрит на дашборды, а алерты приходят десятками в день. Что пошло не так и как исправить?
> Три типичные проблемы: 1) Monitoring без observability — инструменты установлены, но нет понимания "что нормально" (нет baseline). Решение: 2 недели сбора данных, определение baseline, алерты на основе отклонений. 2) Alert fatigue — слишком много алертов без приоритизации. Решение: убрать неactionable алерты, добавить duration (for: 5m+), разделить severity (critical/warning/info), добавить runbook_url. 3) Vanity dashboards — красивые графики без смысла. Решение: начать с Golden Signals (latency, traffic, errors, saturation) и RED/USE метрик, убрать все неиспользуемые панели.

> [!question]- Микросервис A вызывает микросервис B, trace обрывается на границе. Логи B есть, но нет trace_id. Как связать логи и трейсы?
> Проблема в отсутствии context propagation. Решение: 1) Сервис A должен передавать W3C Trace Context headers (traceparent, tracestate) при вызове B. 2) Сервис B должен извлекать trace context из входящих headers и создавать child span. 3) В логах B добавить trace_id как structured field. 4) В Grafana настроить data source correlation: клик на лог с trace_id открывает trace в Jaeger/Tempo. Без propagation headers каждый сервис создает независимый trace и корреляция невозможна.

> [!question]- Инженер добавил label user_id к метрике http_requests_total. Через неделю Prometheus потребляет 10x больше памяти. Почему и как решить?
> Cardinality explosion. Каждая уникальная комбинация labels создает отдельный time series. Если у вас 100K уникальных user_id, 5 methods и 10 status codes — это 100K x 5 x 10 = 5M time series вместо 50. Правило: labels должны иметь низкую кардинальность (service, method, status, endpoint). Высококардинальные данные (user_id, request_id, trace_id) относятся к логам и трейсам, не к метрикам. Решение: удалить user_id из metrics labels, перенести в structured logs.

---

## Ключевые карточки

Три столпа observability
?
Metrics (числовые показатели, агрегированные по времени), Logs (структурированные записи событий), Traces (путь запроса через распределенную систему). Каждый столп отвечает на свой вопрос: metrics — "что происходит", logs — "почему", traces — "где именно".

Golden Signals
?
Четыре ключевые метрики от Google SRE: Latency (время ответа), Traffic (количество запросов), Errors (процент ошибок), Saturation (насколько загружен ресурс). Достаточно для базового мониторинга любого сервиса.

RED vs USE метрики
?
RED для сервисов: Rate (requests/sec), Errors (error rate), Duration (latency). USE для инфраструктуры: Utilization (% загрузки), Saturation (очередь), Errors (ошибки). RED — что видит пользователь, USE — что видит железо.

SLI, SLO, SLA
?
SLI (Service Level Indicator) — конкретная метрика (P99 latency < 200ms). SLO (Service Level Objective) — цель (99.9% запросов быстрее 200ms). SLA (Service Level Agreement) — договор с клиентом с финансовыми последствиями. Error budget = 100% - SLO.

Distributed tracing и OpenTelemetry
?
OpenTelemetry — стандарт инструментирования. Trace состоит из spans (операций). Context propagation через W3C headers (traceparent) позволяет связать spans разных сервисов. Sampling (probabilistic, tail-based) контролирует объем данных.

eBPF и Cilium Hubble
?
eBPF — выполнение кода в ядре Linux без перезагрузки, минимальный overhead. Hubble — observability для Kubernetes на базе eBPF через Cilium CNI. Видит L3-L7 трафик, строит service map, фильтрует flows по pod/protocol/verdict без sidecar.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Ручная диагностика | [[network-debugging-basics]] | Навыки когда observability не дает ответ |
| Performance tuning | [[network-performance-optimization]] | Оптимизация на основе метрик |
| Kubernetes networking | [[network-kubernetes-deep-dive]] | K8s-специфичная observability и Cilium |
| Troubleshooting | [[network-troubleshooting-advanced]] | Расследование аномалий из алертов |
| Latency анализ | [[network-latency-optimization]] | Percentile-метрики и latency budgets |
| Обзор раздела | [[networking-overview]] | Карта всех материалов по сетям |

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции: 5 аналогий (observability как приборная панель самолёта monitoring vs observability, три столпа как три типа врачей metrics/logs/traces, Prometheus + Grafana как сборщик новостей + телеканал, Golden Signals как четыре показателя здоровья, distributed tracing как GPS-трек посылки), 6 типичных ошибок с СИМПТОМ/РЕШЕНИЕ (Prometheus + Grafana ≠ observability, alert fatigue, сбор всего подряд, метрики без labels, нет корреляции между столпами, vanity dashboards), 5 ментальных моделей (вопрос определяет инструмент, MELT framework, SLI→SLO→SLA pipeline с error budget, observability maturity model, unknown unknowns matrix)*

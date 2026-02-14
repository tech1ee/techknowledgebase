---
title: "Observability: видеть, что происходит в системе"
created: 2025-11-24
modified: 2026-02-13
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/devops
  - devops/monitoring
  - devops/observability
  - tools/opentelemetry
  - type/concept
  - level/intermediate
related:
  - "[[microservices-vs-monolith]]"
  - "[[kubernetes-basics]]"
  - "[[ci-cd-pipelines]]"
  - "[[network-cloud-modern]]"
prerequisites:
  - "[[docker-for-developers]]"
  - "[[ci-cd-pipelines]]"
reading_time: 11
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Observability: видеть, что происходит в системе

Logs — "что случилось?". Metrics — "сколько?". Traces — "где тормозит?". OpenTelemetry — vendor-neutral стандарт для сбора всех трёх. Данные без анализа — просто шум.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Logs (Логи)** | Дискретные события с текстом |
| **Metrics (Метрики)** | Агрегированные числа (latency, RPS) |
| **Traces (Трейсы)** | Путь запроса через систему |
| **Span** | Единица работы в трейсе |
| **Trace ID** | Уникальный ID запроса через все сервисы |
| **OpenTelemetry** | Стандарт сбора телеметрии |
| **SLI/SLO/SLA** | Метрики качества сервиса |
| **Alerting** | Оповещения при проблемах |

---

## Monitoring vs Observability

```
Monitoring (старый подход):
"Сервер упал?" → Да/Нет
"CPU > 80%?"   → Алерт

Знаем ЗАРАНЕЕ что искать
Проверяем известные проблемы

─────────────────────────────────────────

Observability (современный подход):
"Почему запрос занял 5 секунд вместо 50ms?"
"Что изменилось между вчера и сегодня?"

Можем исследовать НЕИЗВЕСТНЫЕ проблемы
Система позволяет задавать новые вопросы
```

---

## Три столпа Observability

```
┌─────────────────────────────────────────────────────────────────┐
│                     OBSERVABILITY                               │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │    LOGS     │   │   METRICS   │   │   TRACES    │           │
│  │             │   │             │   │             │           │
│  │ Что случи-  │   │ Сколько?    │   │ Путь        │           │
│  │ лось?       │   │ Как часто?  │   │ запроса     │           │
│  │             │   │             │   │             │           │
│  │ Дискретные  │   │ Агрегиро-   │   │ Распреде-   │           │
│  │ события     │   │ ванные      │   │ лённый      │           │
│  │             │   │ числа       │   │ контекст    │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
│                                                                 │
│  "ERROR: DB        "99th percentile   "Request spent           │
│   connection        latency: 250ms"   45ms in DB,              │
│   timeout"                             120ms in                 │
│                                        external API"            │
└─────────────────────────────────────────────────────────────────┘
```

### Logs: что случилось

```json
// Структурированный лог (JSON) — правильно
{
  "timestamp": "2025-11-24T10:30:00Z",
  "level": "ERROR",
  "service": "payment-service",
  "trace_id": "abc123",
  "user_id": "user_456",
  "message": "Payment failed",
  "error": "Card declined",
  "amount": 99.99,
  "currency": "USD"
}

// Неструктурированный — плохо для поиска
"2025-11-24 10:30:00 ERROR Payment failed for user 456: Card declined"
```

```
Уровни логирования:

DEBUG   → Детали для разработки (выключено в prod)
INFO    → Нормальные события (запрос обработан)
WARN    → Подозрительное, но не ошибка (retry сработал)
ERROR   → Ошибка, требует внимания
FATAL   → Критическая ошибка, сервис падает
```

### Metrics: сколько и как часто

```
Типы метрик:

Counter (только растёт):
  http_requests_total{method="GET", path="/api/users"} 15234

Gauge (текущее значение):
  active_connections 42
  memory_usage_bytes 1073741824

Histogram (распределение):
  http_request_duration_seconds_bucket{le="0.1"} 8000
  http_request_duration_seconds_bucket{le="0.5"} 9500
  http_request_duration_seconds_bucket{le="1.0"} 9900
```

```
RED метод (для сервисов):

R — Rate:     Запросов в секунду
E — Errors:   Процент ошибок
D — Duration: Latency (p50, p95, p99)

USE метод (для ресурсов):

U — Utilization: % использования (CPU 75%)
S — Saturation:  Очередь/перегрузка
E — Errors:      Ошибки ресурса
```

### Traces: путь запроса

```
Запрос пользователя проходит через несколько сервисов:

User → API Gateway → Auth Service → User Service → Database
                  ↓
              Cache → Payment Service → External API

Без трейсов:
"Запрос занял 2 секунды. Где проблема?" → ¯\_(ツ)_/¯

С трейсами:
┌─────────────────────────────────────────────────────────────┐
│ Trace ID: abc-123                           Total: 2000ms   │
├─────────────────────────────────────────────────────────────┤
│ ├─ API Gateway                              │ 5ms           │
│ │  └─ Auth Service                          │ 50ms          │
│ │     └─ User Service                       │ 100ms         │
│ │        └─ Database Query                  │ 45ms          │
│ │        └─ Cache Miss                      │ 2ms           │
│ └─ Payment Service                          │ 1800ms ← !!!  │
│    └─ External Payment API                  │ 1750ms ← !!!  │
└─────────────────────────────────────────────────────────────┘

Проблема: External Payment API отвечает медленно
```

---

## OpenTelemetry: стандарт индустрии

```
Почему OpenTelemetry:

До OTel:                        С OTel:
─────────────────               ─────────────────
Datadog SDK                     OpenTelemetry SDK
+ New Relic SDK                      │
+ Jaeger SDK                         ▼
+ Prometheus SDK               ┌───────────────┐
= 4 разных интеграции          │ OTel Collector│
= vendor lock-in               └───────┬───────┘
                                       │
                               ┌───────┴───────┐
                               ▼       ▼       ▼
                            Datadog  Jaeger  Prometheus

Один SDK → любой backend
```

### Базовая интеграция (Node.js)

```javascript
// tracing.js — подключить ДО остального кода
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://otel-collector:4318/v1/traces',
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      // Автоматически инструментирует:
      // - HTTP запросы
      // - Express/Fastify
      // - Database клиенты
      // - и многое другое
    }),
  ],
});

sdk.start();
```

```javascript
// Ручное создание span (для важной бизнес-логики)
const { trace } = require('@opentelemetry/api');

const tracer = trace.getTracer('payment-service');

async function processPayment(order) {
  return tracer.startActiveSpan('process-payment', async (span) => {
    try {
      span.setAttribute('order.id', order.id);
      span.setAttribute('order.amount', order.amount);

      const result = await paymentGateway.charge(order);

      span.setAttribute('payment.status', result.status);
      return result;
    } catch (error) {
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR });
      throw error;
    } finally {
      span.end();  // ВАЖНО: всегда закрывать span
    }
  });
}
```

### OpenTelemetry Collector

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

  # Сэмплирование — не отправлять 100% трейсов
  probabilistic_sampler:
    sampling_percentage: 10

exporters:
  # Можно отправлять в несколько мест одновременно
  otlp/jaeger:
    endpoint: jaeger:4317
  prometheus:
    endpoint: 0.0.0.0:8889
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, probabilistic_sampler]
      exporters: [otlp/jaeger, logging]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

---

## Инструменты и стек

```
Популярные стеки:

Open Source (self-hosted):
┌─────────────────────────────────────────────────┐
│ Grafana + Prometheus + Loki + Tempo             │
│                                                 │
│ Metrics:  Prometheus → Grafana                  │
│ Logs:     Loki → Grafana                        │
│ Traces:   Tempo → Grafana                       │
│                                                 │
│ + OpenTelemetry Collector                       │
└─────────────────────────────────────────────────┘

SaaS (managed):
┌─────────────────────────────────────────────────┐
│ Datadog / New Relic / Grafana Cloud             │
│                                                 │
│ All-in-one: Logs + Metrics + Traces + APM       │
│ + Alerting + Dashboards + AI analysis           │
│                                                 │
│ Цена: $15-50+ per host/month                    │
└─────────────────────────────────────────────────┘

Kubernetes-native:
┌─────────────────────────────────────────────────┐
│ Prometheus Operator + Grafana + Jaeger          │
│                                                 │
│ Helm charts для быстрой установки               │
│ ServiceMonitor для автодискавери                │
└─────────────────────────────────────────────────┘
```

### Prometheus метрики (пример)

```javascript
// Express + prom-client
const client = require('prom-client');

// Стандартные метрики (CPU, memory, etc)
client.collectDefaultMetrics();

// Кастомная метрика
const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
});

// Middleware
app.use((req, res, next) => {
  const end = httpRequestDuration.startTimer();
  res.on('finish', () => {
    end({
      method: req.method,
      route: req.route?.path || 'unknown',
      status_code: res.statusCode,
    });
  });
  next();
});

// Endpoint для Prometheus
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```

---

## Алертинг: не утонуть в шуме

```
Проблема алертов:

Слишком много алертов → Alert fatigue → Игнорируют все
Слишком мало алертов → Пропускают важное

Правила хороших алертов:

1. Actionable: Получил алерт → Знаю что делать
2. Urgent: Требует действия СЕЙЧАС (иначе — не алерт)
3. Rare: Если срабатывает часто — починить или удалить
```

```yaml
# Пример алерта (Prometheus Alertmanager)
groups:
  - name: app-alerts
    rules:
      # Хороший алерт: конкретный, actionable
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.05
        for: 5m  # Должен держаться 5 минут
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5%"
          description: "{{ $value | humanizePercentage }} of requests failing"
          runbook: "https://wiki/runbooks/high-error-rate"

      # Плохой алерт: слишком чувствительный
      # - alert: CPUHigh
      #   expr: cpu_usage > 50%  # Сработает постоянно
```

---

## Подводные камни

### Проблема 1: Данные без контекста

```
Лог без trace_id:
"ERROR: Database connection failed"
→ Какой запрос? Какой пользователь? Невозможно связать

Лог с trace_id:
{
  "trace_id": "abc123",
  "user_id": "user_456",
  "message": "Database connection failed"
}
→ Можно найти весь путь запроса
```

### Проблема 2: Стоимость хранения

```
Типичный production сервис:

Logs:   ~1GB/день/сервис
Traces: ~500MB/день/сервис
        × 20 сервисов
        × 30 дней retention
        ──────────────────
        = 900GB хранилища

Решения:
• Sampling (хранить 10% трейсов)
• Log levels (DEBUG выключен в prod)
• Retention policies (логи старше 30 дней удаляются)
• Холодное хранилище для старых данных
```

### Проблема 3: "We'll add observability later"

```
Реальность:

Без observability с начала:
• Баг в production → "Что произошло?" → Ничего не знаем
• Добавляем логи → Редеплой → Ждём повторения бага
• Повторяем неделю

С observability с начала:
• Баг в production → Смотрим trace → Видим причину
• Фиксим → Деплоим → Готово

Правило: Observability — не фича, а инфраструктура
```

---

## Actionable

**Базовый уровень:**
- Структурированные логи (JSON)
- Базовые метрики (RED: Rate, Errors, Duration)
- Health endpoints

**Средний уровень:**
- OpenTelemetry для трейсинга
- Централизованный сбор логов (Loki/ELK)
- Дашборды в Grafana

**Продвинутый:**
- Distributed tracing между сервисами
- Автоматические алерты с runbooks
- Корреляция logs ↔ traces ↔ metrics

---

## Связи

- Микросервисы требуют observability: [[microservices-vs-monolith]]
- K8s мониторинг: [[kubernetes-basics]]
- Observability в pipeline: [[ci-cd-pipelines]]

---

## Источники

- [OpenTelemetry: Observability Primer](https://opentelemetry.io/docs/concepts/observability-primer/) — проверено 2025-11-24
- [Better Stack: OpenTelemetry Best Practices](https://betterstack.com/community/guides/observability/opentelemetry-best-practices/) — проверено 2025-11-24
- [The New Stack: Observability in 2024](https://thenewstack.io/observability-in-2024-more-opentelemetry-less-confusion/) — проверено 2025-11-24
- [Grafana: OpenTelemetry User Guide](https://grafana.com/blog/2023/12/18/opentelemetry-best-practices-a-users-guide-to-getting-started-with-opentelemetry/) — проверено 2025-11-24

---

**Последняя верификация**: 2025-11-24
**Уровень достоверности**: high

---

---

## Проверь себя

> [!question]- В чём разница между Monitoring и Observability? Почему monitoring недостаточен для микросервисов?
> Monitoring отвечает на заранее известные вопросы ("CPU > 80%?", "сервер упал?"). Observability позволяет исследовать неизвестные проблемы ("почему запрос занял 5 секунд вместо 50мс?"). В монолите мониторинг работает: ограниченное количество известных failure modes. В микросервисах запрос проходит десятки сервисов -- без distributed tracing невозможно локализовать проблему. Observability = возможность задавать новые вопросы без изменения инструментации.

> [!question]- Почему structured logging (JSON) критически важен для production-систем?
> Неструктурированные логи ("ERROR: Payment failed for user 456") невозможно эффективно искать и фильтровать. Структурированные JSON-логи с полями trace_id, user_id, service позволяют: 1) быстро находить все логи одного запроса по trace_id, 2) агрегировать ошибки по типу, 3) связывать логи с трейсами и метриками. Без trace_id в логах -- "какой запрос? какой пользователь?" -- невозможно ответить.

> [!question]- Сервис обрабатывает 1 ГБ логов в день. 20 сервисов, 30 дней retention. Как оптимизировать стоимость?
> 20 сервисов x 1 ГБ x 30 дней = 600 ГБ + трейсы. Оптимизация: 1) Sampling -- хранить 10% трейсов (для большинства задач достаточно). 2) Log levels -- DEBUG выключен в prod, только INFO+. 3) Retention policies -- горячие данные 7 дней, холодные 30 дней в S3. 4) Фильтрация шума -- не логировать health checks и heartbeats. 5) Агрегация на Collector -- батчить перед отправкой.

> [!question]- Почему "добавим observability потом" -- плохая стратегия?
> Без observability с первого дня: баг в production -> "что произошло?" -> ничего не знаем -> добавляем логи -> редеплой -> ждём повторения -> неделя. С observability: баг -> смотрим trace -> видим причину -> фиксим за час. Observability -- не фича, а инфраструктура. Стоимость добавления растёт экспоненциально: инструментировать 50 сервисов постфактум в 10 раз дороже, чем добавлять по мере создания.

---

## Ключевые карточки

Какие три столпа Observability?
?
Logs (что случилось -- дискретные события), Metrics (сколько и как часто -- агрегированные числа), Traces (путь запроса через систему). Полная observability требует корреляции всех трёх через общий trace_id.

Что такое OpenTelemetry?
?
Vendor-neutral стандарт для сбора телеметрии (CNCF). Один SDK вместо отдельных для Datadog, Jaeger, Prometheus. Данные отправляются через OTel Collector в любой backend. Устраняет vendor lock-in.

Что такое RED-метод?
?
Rate (запросов в секунду), Errors (процент ошибок), Duration (latency: p50, p95, p99). Применяется для мониторинга сервисов. Дополняется USE-методом для ресурсов: Utilization, Saturation, Errors.

Чем Counter отличается от Gauge и Histogram?
?
Counter -- только растёт (http_requests_total). Gauge -- текущее значение, может расти и падать (active_connections). Histogram -- распределение значений по бакетам (http_request_duration_seconds), позволяет вычислять перцентили.

Что такое Trace и Span?
?
Trace -- полный путь запроса через все сервисы (идентифицируется Trace ID). Span -- единица работы внутри трейса (API Gateway -> Auth Service -> Database). Каждый span имеет длительность, атрибуты и parent span.

Какие правила хороших алертов?
?
Actionable (получил -> знаю что делать), Urgent (требует действия сейчас), Rare (если часто -> починить или удалить). Плюс: for-задержка (держаться 5 минут), runbook URL, конкретное описание. Alert fatigue -- главный враг мониторинга.

Зачем нужен OTel Collector?
?
Промежуточный компонент между приложениями и backend'ами. Батчинг (уменьшает нагрузку), sampling (хранить 10% трейсов), routing (отправлять в несколько мест одновременно). Один Collector для всех сигналов.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[devops-incident-management]] | Что делать когда мониторинг обнаружил проблему: on-call, runbooks, post-mortems |
| Углубиться | [[network-observability]] | Observability на уровне сети: tcpdump, Wireshark, eBPF |
| Смежная тема | [[microservices-vs-monolith]] | Микросервисы требуют distributed tracing -- без него debugging невозможен |
| Обзор | [[devops-overview]] | Вернуться к карте раздела DevOps |

*Проверено: 2026-01-09*

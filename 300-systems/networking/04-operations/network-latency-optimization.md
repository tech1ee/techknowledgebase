---
title: "Network Latency Optimization"
created: 2025-01-15
modified: 2026-02-13
tags:
  - topic/networking
  - performance
  - latency
  - type/concept
  - level/advanced
related:
  - [network-performance-optimization]]
  - "[[network-transport-layer]]"
  - "[[network-http-evolution]"
prerequisites:
  - "[[network-transport-layer]]"
  - "[[network-http-evolution]]"
status: published
reading_time: 68
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Network Latency Optimization

---

## Теоретические основы

> **Латентность сети** — суммарная задержка между отправкой запроса и получением ответа. Формально декомпозируется на четыре компонента (Kurose, Ross, 2021): d_total = d_proc + d_queue + d_trans + d_prop, где d_proc — обработка в узле, d_queue — ожидание в очереди, d_trans — время передачи (L/R), d_prop — время распространения сигнала (d/s).

### Таксономия компонентов задержки

| Компонент | Формула | Зависит от | Типичные значения | Как оптимизировать |
|-----------|---------|-----------|-------------------|-------------------|
| **Propagation delay** | d/s (расстояние / скорость света) | Физическое расстояние | 1 ms на 200 км | CDN, edge computing |
| **Transmission delay** | L/R (размер / bandwidth) | Пропускная способность канала | <1 ms на 1 Gbps | Сжатие, уменьшение payload |
| **Processing delay** | CPU-зависим | Мощность маршрутизатора | <1 ms | Аппаратное ускорение |
| **Queueing delay** | Зависит от нагрузки | Степень загрузки канала | 0-100+ ms | QoS, уменьшение трафика |
| **TCP handshake** | 1 RTT (SYN + SYN-ACK) | RTT между клиентом и сервером | 10-200 ms | Connection pooling, keep-alive |
| **TLS handshake** | 1-2 RTT (TLS 1.2: 2 RTT, TLS 1.3: 1 RTT) | RTT + крипто | 20-400 ms | TLS 1.3, 0-RTT, session resumption |
| **DNS resolution** | 1-4 RTT (recursive) | Кэш, расстояние до DNS | 5-100 ms | dns-prefetch, local resolver |

### Закон Литтла для сетевых систем

> **Закон Литтла (Little's Law, 1961):** L = lambda * W, где L — среднее число запросов в системе, lambda — средняя скорость поступления запросов, W — среднее время пребывания запроса в системе. Для сетевых сервисов: если throughput = 100 req/s и avg latency = 50ms, то в среднем в системе находятся 5 запросов одновременно.

Применение в capacity planning:
- **Максимальный throughput:** если на сервер приходит 1000 req/s и каждый обрабатывается 10ms, нужно минимум 10 параллельных worker-ов
- **Connection pool sizing:** pool_size >= lambda * avg_latency_to_db

### Latency vs Throughput: формальное соотношение

- **Latency** — время обработки одного запроса (единица: секунды)
- **Throughput** — количество обработанных запросов в единицу времени (единица: req/s)
- Связь нелинейна: увеличение throughput через batching повышает latency; уменьшение latency через кэширование может повысить throughput
- **Утилизация по Erlang:** при загрузке системы > 70% queueing delay растёт экспоненциально

### Tail Latency Amplification (Dean & Barroso, 2013)

> При fan-out на N сервисов вероятность попадания хотя бы одного запроса в "хвост" распределения: P(tail) = 1 - (1-p)^N. Для N=10 и P99: P = 1-(0.99)^10 = 9.6%. Для N=100: P = 63.4%. Jeff Dean (Google) формализовал это в "The Tail at Scale" (2013, Communications of the ACM).

**См. также:** [[network-performance-optimization]] (TCP tuning и системная оптимизация), [[network-transport-layer]] (TCP handshake, congestion control), [[network-http-evolution]] (HTTP/2 multiplexing, HTTP/3 0-RTT)

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Сетевые основы** | Понимание TCP, HTTP | [[network-fundamentals-for-developers]] |
| **HTTP эволюция** | HTTP/2, HTTP/3 для latency | [[network-http-evolution]] |
| **DevTools** | Измерение TTFB, waterfall | Браузер F12 |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ✅ Да | Полезно знать влияние |
| **Intermediate** | ✅ Да | Основная аудитория |
| **Advanced** | ✅ Да | Продвинутые техники |

### Терминология для новичков

> 💡 **Latency** = задержка между запросом и ответом. Время ожидания. Throughput — сколько, Latency — как быстро.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **Latency** | Задержка передачи | **Время в пути** — сколько ехать |
| **RTT** | Round-Trip Time — туда и обратно | **Пинг-понг** — мяч долетел и вернулся |
| **TTFB** | Time To First Byte | **Когда начнёт грузиться** |
| **P50/P99** | Percentiles latency | **Обычная/худшая скорость** |
| **CDN** | Content Delivery Network | **Склад рядом с тобой** |
| **Edge** | Сервер ближе к пользователю | **Ближайший филиал** |
| **Connection Reuse** | Переиспользование соединений | **Не вешать трубку** — продолжить разговор |
| **DNS Prefetch** | Заранее резолвить DNS | **Заранее узнать адрес** |
| **Preconnect** | Заранее установить соединение | **Заранее позвонить** |
| **Jitter** | Нестабильность latency | **То быстро, то медленно** |

---

## Часть 1: Интуиция без кода

> 🎯 **Цель секции:** Понять latency через знакомые примеры из реальной жизни, прежде чем погружаться в технические детали.

### Аналогия 1: Latency vs Throughput — Труба vs Автобан

**Путаница:** "У меня гигабит, почему страница грузится медленно?"

```
THROUGHPUT (Пропускная способность) — сколько машин в час
┌────────────────────────────────────────────────────────┐
│  🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗  │
│  ════════════════════════════════════════════════════  │
│        Широкий автобан: 10,000 машин/час               │
└────────────────────────────────────────────────────────┘

LATENCY (Задержка) — сколько едет одна машина
┌────────────────────────────────────────────────────────┐
│  Москва ─────────── 7500 км ─────────── Нью-Йорк       │
│  🚗 ═══════════════════════════════════════════►       │
│        Время в пути: ~50ms (скорость света!)           │
└────────────────────────────────────────────────────────┘
```

**Ключевой инсайт:**
- **Throughput** — ширина трубы (сколько пролезет за секунду)
- **Latency** — длина трубы (сколько секунд долетит первый байт)
- Гигабит не ускорит RTT до США — это физика!

**Жизненный пример:**
> Представь водопровод от водохранилища до твоего дома. Можно поставить трубу толщиной в 1 метр (гигабит), но если водохранилище за 100 км, первая капля всё равно дойдёт через N секунд. Ширина трубы не влияет на время прибытия первой капли.

---

### Аналогия 2: RTT и TCP Handshake — Переговоры по телефону

**Проблема:** Почему TCP-соединение такое медленное?

```
TCP Handshake = Деловой звонок с плохой связью

Звонящий (Клиент)              Отвечающий (Сервер)
      │                              │
      │ ──── "Алло, это Вася?" ────► │  RTT #1
      │ ◄─── "Да, слушаю" ────────── │
      │                              │
      │ ──── "Отлично, готов?" ────► │  RTT #2
      │ ◄─── "Готов, говори" ─────── │
      │                              │
      │ ──── "Мой заказ: ..." ─────► │  RTT #3
      │ ◄─── "Понял, вот ответ" ──── │
      │                              │

TCP = 3 RTT до первого полезного ответа!
TLS добавляет ещё 1-2 RTT!
```

**Почему это критично:**
| Маршрут | RTT | TCP+TLS (3 RTT) | Первый полезный байт |
|---------|-----|-----------------|---------------------|
| Localhost | 0.5ms | 1.5ms | Мгновенно |
| Один город | 10ms | 30ms | Заметно |
| Континент | 100ms | 300ms | Раздражает |
| Спутник | 600ms | 1800ms | **Невыносимо** |

**Решение:** Connection reuse — не кладём трубку после каждого вопроса!

---

### Аналогия 3: Percentiles (P50/P99) — Очередь в поликлинику

**Проблема:** "Среднее время приёма 15 минут" — но ты ждёшь час!

```
РАСПРЕДЕЛЕНИЕ ВРЕМЕНИ ПРИЁМА (100 пациентов)

Время:    5   10   15   20   30   45   60   90 мин
          │    │    │    │    │    │    │    │
Пациенты: ████████████████████████████████████
          ▲ P50 = 15 мин (50% ждут меньше)
                           ▲ P95 = 45 мин (95% ждут меньше)
                                    ▲ P99 = 60 мин (99% ждут меньше)

Среднее: 18 мин ← ОБМАНЧИВО! Скрывает тех, кто ждёт 60-90 мин
```

**Почему P99 важнее среднего:**

| Метрика | Что показывает | Когда использовать |
|---------|----------------|-------------------|
| Average | Ничего полезного | Никогда для latency! |
| P50 | Типичный опыт | Общая картина |
| P95 | Плохой опыт 1 из 20 | SLO для большинства |
| P99 | Худший опыт 1 из 100 | Критичные системы |

**Золотое правило:**
> "Если у тебя 1 млн запросов в день, P99 = 500ms означает **10,000 злых пользователей ежедневно**"

---

### Аналогия 4: Fan-Out Problem — Сборка IKEA с ожиданием доставки

**Проблема:** Один медленный микросервис убивает весь запрос

```
СОБИРАЕМ ШКАФ (Параллельный fan-out)

Ты заказал 5 деталей с разных складов:

  Заказ #1 (Москва)    ████░░░░░░  100ms  ✓
  Заказ #2 (Питер)     ██████░░░░  150ms  ✓
  Заказ #3 (Казань)    ████████░░  200ms  ✓
  Заказ #4 (Сочи)      ██████████  250ms  ✓
  Заказ #5 (Владивосток) ██████████████████  450ms  😱 BOTTLENECK!
                       ─────────────────────►
                       0    100   200   300   400   450ms

  Общее время: 450ms (определяется САМЫМ МЕДЛЕННЫМ!)

  Сборка начнётся только когда ВСЕ детали приедут
```

**Математика усиления:**
```
Если каждый сервис P99 = 100ms (99% запросов быстрее):

1 сервис:  P(< 100ms) = 99%
5 сервисов: P(все < 100ms) = 0.99^5 = 95%  ← 5% медленных!
10 сервисов: P(все < 100ms) = 0.99^10 = 90% ← 10% медленных!
20 сервисов: P(все < 100ms) = 0.99^20 = 82% ← 18% медленных!
```

**Вывод:** Каждый дополнительный сервис в fan-out **экспоненциально ухудшает** общий P99!

---

### Аналогия 5: TTFB vs Full Load — Первая ложка супа

**Проблема:** Что именно измерять?

```
ЗАКАЗ В РЕСТОРАНЕ

Тебя посадили ─────┬─── Официант принял заказ
                   │
     (ожидание)    │
                   │
Первая ложка супа ─┼─── TTFB (Time To First Byte)
                   │
     (едим)        │
                   │
Съел весь суп ─────┴─── Full Response Time

┌────────────────────────────────────────────────────┐
│ TTFB = 200ms  │████████░░░░░░░░░░░░░░░░░░░░░░░░░░│
│ Full = 1200ms │████████████████████████████████████│
│               0    200   400   600   800  1000  1200ms
└────────────────────────────────────────────────────┘
```

**Что оптимизировать:**
| Метрика | Что влияет | Как улучшить |
|---------|-----------|--------------|
| **TTFB** | DNS + TCP + TLS + Server processing | CDN, кэширование, edge computing |
| **Download** | Размер ответа + bandwidth | Compression, lazy loading |
| **Total** | TTFB + Download + Client rendering | Всё вместе |

**Правило:**
> "Оптимизируй TTFB в первую очередь — это то, что пользователь ОЩУЩАЕТ как 'тормоза'"

---

## Часть 2: Почему это сложно

> ⚠️ **Цель секции:** Разобрать типичные ошибки, которые делают даже опытные инженеры при оптимизации latency.

### Ошибка 1: Использование Average вместо Percentiles

**СИМПТОМ:**
```
Dashboard показывает: "Average latency: 50ms ✅"
Но пользователи жалуются на тормоза!
```

**Проблема:**
```
Распределение 1000 запросов:
- 950 запросов: 30ms
- 49 запросов: 200ms
- 1 запрос: 5000ms (таймаут базы!)

Average = (950×30 + 49×200 + 1×5000) / 1000 = 43ms  ← "Всё отлично!"
P99 = 200ms  ← 10 пользователей в час страдают
P99.9 = 5000ms  ← 1 пользователь в час ждёт 5 секунд!
```

**РЕШЕНИЕ:**
```yaml
# Prometheus alerting - правильно
- alert: HighLatencyP99
  expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.5
  for: 5m

# НЕ ИСПОЛЬЗУЙ average для latency!
# - alert: HighLatencyAvg  ← ПЛОХО
#   expr: rate(http_request_duration_sum[5m]) / rate(http_request_duration_count[5m]) > 0.5
```

---

### Ошибка 2: Naive Retries убивают систему

**СИМПТОМ:**
```
Сервис немного перегружен → таймауты → retry storm → полный отказ
```

**Проблема:**
```
Нормальная нагрузка: 1000 req/s

Сервис замедлился (P99: 100ms → 500ms):
  - Клиенты: "Таймаут 200ms! Повторяю!"
  - 200 запросов делают retry

Через 1 секунду:
  - Нагрузка: 1000 + 200 = 1200 req/s
  - Ещё больше таймаутов → ещё больше retry

Через 5 секунд:
  - Нагрузка: 2000+ req/s (retry storm!)
  - Сервис полностью лёг 💀
```

**РЕШЕНИЕ:**
```kotlin
// Exponential backoff + jitter
val retryConfig = RetryConfig.custom<Any>()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(100))
    .retryOnResult { response -> response.status >= 500 }
    .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(
        initialInterval = Duration.ofMillis(100),
        multiplier = 2.0,
        randomizationFactor = 0.5  // Jitter!
    ))
    .build()

// Circuit breaker для защиты downstream
val circuitBreaker = CircuitBreaker.ofDefaults("downstream-service")
```

---

### Ошибка 3: Игнорирование tail latency в fan-out

**СИМПТОМ:**
```
Каждый микросервис имеет P99 = 100ms (отлично!)
Но общий P99 системы = 500ms (почему?!)
```

**Проблема:**
```
Gateway делает параллельный fan-out к 10 сервисам:

  Сервис A: P99 = 100ms
  Сервис B: P99 = 100ms
  ...
  Сервис J: P99 = 100ms

P(все 10 < 100ms) = 0.99^10 = 90.4%
P(хотя бы 1 > 100ms) = 9.6%  ← Почти каждый 10-й запрос!

Если "медленный" сервис отвечает 300ms:
  Общий P99 системы ≈ 300ms (определяется slowest!)
```

**РЕШЕНИЕ:**
```kotlin
// 1. Request hedging - отправляем дубликаты
suspend fun fetchWithHedging(services: List<Service>): Response {
    return select {
        services.forEach { service ->
            async { service.fetch() }.onAwait { it }
        }
    }
}

// 2. Deadline propagation - общий таймаут на всю цепочку
val deadline = Deadline.after(500, TimeUnit.MILLISECONDS)
val response = stub.withDeadline(deadline).getData(request)

// 3. Требуй P99.9, а не P99 от каждого сервиса!
```

---

### Ошибка 4: CDN кэширует динамический контент

**СИМПТОМ:**
```
Пользователь A видит данные пользователя B (утечка!)
Или: "Почему после logout я вижу старый dashboard?"
```

**Проблема:**
```
# Nginx/CDN конфиг - ОПАСНО
location /api/ {
    proxy_cache_valid 200 60s;  # Кэшируем ВСЁ на 60 секунд
}

Запрос 1 (User A): GET /api/profile → {"name": "Alice", "balance": 1000}
  └── CDN кэширует ответ

Запрос 2 (User B): GET /api/profile → {"name": "Alice", "balance": 1000}
  └── CDN отдаёт кэш User A пользователю B! 💀
```

**РЕШЕНИЕ:**
```nginx
# Правильный конфиг
location /api/static/ {
    # Только статика: справочники, конфиги без персональных данных
    proxy_cache_valid 200 3600s;
    add_header Cache-Control "public, max-age=3600";
}

location /api/user/ {
    # Персональные данные - НИКОГДА не кэшировать на CDN
    proxy_cache off;
    add_header Cache-Control "private, no-store, no-cache";
    add_header Vary "Authorization";  # Разные пользователи = разные ответы
}
```

---

### Ошибка 5: Оптимизация без baseline и мониторинга

**СИМПТОМ:**
```
"Мы включили HTTP/2 — стало быстрее!"
"А насколько быстрее?" — "Ну... быстрее..."
```

**Проблема:**
```
Оптимизация вслепую:
1. Включили gzip → "Кажется быстрее"
2. Включили HTTP/2 → "Ещё быстрее"
3. Включили BBR → "Вроде быстрее"
4. Что-то сломалось → "Непонятно что откатывать"

Без baseline невозможно:
- Измерить эффект каждого изменения
- Понять, что именно помогло
- Обосновать затраты на инфраструктуру
```

**РЕШЕНИЕ:**
```bash
# 1. Baseline до изменений
wrk -t4 -c100 -d60s --latency https://api.example.com/endpoint > baseline.txt

# 2. Одно изменение за раз
# Включаем HTTP/2

# 3. Измеряем после
wrk -t4 -c100 -d60s --latency https://api.example.com/endpoint > after_http2.txt

# 4. Сравниваем
# Baseline: P99 = 250ms
# After HTTP/2: P99 = 180ms  ← Улучшение 28%!

# 5. Документируем
echo "HTTP/2 enabled: P99 250ms → 180ms (-28%)" >> optimization_log.md
```

---

### Ошибка 6: Connection per request вместо Connection pooling

**СИМПТОМ:**
```
TTFB резко растёт под нагрузкой
TIME_WAIT сокетов > 10,000
```

**Проблема:**
```
Каждый HTTP запрос без connection pool:

  Request #1: DNS(20ms) + TCP(30ms) + TLS(60ms) + Request(10ms) = 120ms
  Request #2: DNS(20ms) + TCP(30ms) + TLS(60ms) + Request(10ms) = 120ms
  Request #3: DNS(20ms) + TCP(30ms) + TLS(60ms) + Request(10ms) = 120ms
  ...

  1000 запросов = 120 секунд суммарного overhead!

  Плюс: исчерпание портов (65535 максимум)
  netstat -an | grep TIME_WAIT | wc -l  → 50,000 😱
```

**РЕШЕНИЕ:**
```kotlin
// OkHttp с connection pool
val client = OkHttpClient.Builder()
    .connectionPool(ConnectionPool(
        maxIdleConnections = 100,
        keepAliveDuration = 5,
        timeUnit = TimeUnit.MINUTES
    ))
    .build()

// Ktor с connection pool
val client = HttpClient(CIO) {
    engine {
        maxConnectionsCount = 1000
        endpoint {
            maxConnectionsPerRoute = 100
            pipelineMaxSize = 20
            keepAliveTime = 5000
            connectTimeout = 5000
        }
    }
}
```

```
С Connection Pool:
  Request #1: DNS(20ms) + TCP(30ms) + TLS(60ms) + Request(10ms) = 120ms
  Request #2-1000: Request(10ms) = 10ms  ← Переиспользуем соединение!

  1000 запросов = 120ms + 999×10ms = ~10 секунд (vs 120 секунд!)
```

---

## Часть 3: Ментальные модели

> 🧠 **Цель секции:** Дать системные способы думать о latency optimization, чтобы принимать правильные решения в любой ситуации.

### Модель 1: Waterfall Analysis — Разбираем по компонентам

**Принцип:** Latency = сумма последовательных этапов. Оптимизируй самый большой.

```
WATERFALL запроса к API:

┌─────────────────────────────────────────────────────────────────┐
│ DNS Lookup         ████░░░░░░░░░░░░░░░░░░░░░░░░░░░  50ms       │
│ TCP Connect        ░░░░████░░░░░░░░░░░░░░░░░░░░░░░  30ms       │
│ TLS Handshake      ░░░░░░░░████████░░░░░░░░░░░░░░░  60ms       │
│ Request Send       ░░░░░░░░░░░░░░░░█░░░░░░░░░░░░░░  5ms        │
│ Server Processing  ░░░░░░░░░░░░░░░░░████████████░░  200ms ⚠️   │
│ Response Download  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░███  40ms       │
├─────────────────────────────────────────────────────────────────┤
│ TOTAL: 385ms       DNS(13%) TCP(8%) TLS(16%) Server(52%) DL(10%)│
└─────────────────────────────────────────────────────────────────┘

Server Processing = 52% времени → СЮДА оптимизацию!
```

**Инструмент для анализа:**
```bash
# curl с детальным timing
curl -w "DNS: %{time_namelookup}s\nTCP: %{time_connect}s\nTLS: %{time_appconnect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" -o /dev/null -s https://api.example.com
```

**Чек-лист оптимизации по компонентам:**
| Компонент | Если > X | Решение |
|-----------|----------|---------|
| DNS | > 50ms | DNS prefetch, локальный кэш |
| TCP | > 1 RTT | Connection reuse, TCP Fast Open |
| TLS | > 2 RTT | TLS 1.3, session resumption |
| Server | > 100ms | Profiling, кэширование, DB оптимизация |
| Download | > 100ms | Compression, CDN, lazy loading |

---

### Модель 2: Latency Budget — Бюджетирование миллисекунд

**Принцип:** Раздай бюджет на latency каждому компоненту системы.

```
ОБЩИЙ БЮДЖЕТ: P99 < 500ms для checkout API

┌─────────────────────────────────────────────────────────────┐
│                    BUDGET ALLOCATION                         │
├──────────────────┬──────────────┬───────────────────────────┤
│ Компонент        │ Бюджет (P99) │ Статус                    │
├──────────────────┼──────────────┼───────────────────────────┤
│ API Gateway      │    30ms      │ ✅ Actual: 25ms           │
│ Auth Service     │    50ms      │ ✅ Actual: 40ms           │
│ Cart Service     │    80ms      │ ⚠️ Actual: 90ms (over!)   │
│ Inventory Check  │   100ms      │ ✅ Actual: 80ms           │
│ Payment Service  │   150ms      │ ✅ Actual: 120ms          │
│ Order Creation   │    50ms      │ ✅ Actual: 45ms           │
│ Buffer/Overhead  │    40ms      │ Резерв на неожиданности   │
├──────────────────┼──────────────┼───────────────────────────┤
│ TOTAL            │   500ms      │ Actual: 400ms + Buffer    │
└──────────────────┴──────────────┴───────────────────────────┘

Cart Service превысил бюджет → нужна оптимизация именно там!
```

**Правила бюджетирования:**
1. **Резерв 10-20%** — всегда оставляй buffer
2. **Критичный путь** — получает больший бюджет
3. **Параллельные вызовы** — бюджет = max(все), не сумма
4. **Пересмотр квартально** — требования меняются

---

### Модель 3: 80/20 Rule для Latency — Где искать bottleneck

**Принцип:** 80% latency обычно создаётся 20% компонентов.

```
ТИПИЧНОЕ РАСПРЕДЕЛЕНИЕ LATENCY:

Категория             │ % времени │ Где искать
──────────────────────┼───────────┼─────────────────────────────
Database queries      │    40%    │ Slow query log, N+1, индексы
Network I/O           │    25%    │ RTT, DNS, TLS, fan-out
Serialization         │    15%    │ JSON parsing, protobuf
Business logic        │    10%    │ CPU-bound операции
Framework overhead    │     5%    │ Middleware, interceptors
Other                 │     5%    │ GC pauses, locks, etc.

GOLDEN RULE:
┌────────────────────────────────────────────────────────────┐
│  1. Database → 2. Network → 3. Serialization → 4. Code    │
│  Оптимизируй в этом порядке для максимального эффекта!    │
└────────────────────────────────────────────────────────────┘
```

**Quick wins по категориям:**
| Категория | Quick Win | Эффект |
|-----------|-----------|--------|
| Database | Добавить индекс на WHERE clause | -50-90% query time |
| Database | Устранить N+1 (batch fetch) | -80% запросов |
| Network | Connection pooling | -60% на повторных запросах |
| Network | CDN для статики | -70% TTFB |
| Serialization | Protobuf вместо JSON | -40% parsing time |

---

### Модель 4: Tail Latency Amplification — Экспоненциальное ухудшение

**Принцип:** В распределённых системах tail latency растёт экспоненциально с fan-out.

```
ФОРМУЛА УСИЛЕНИЯ:

P(общий запрос < T) = P(сервис < T)^N

Где N = количество параллельных вызовов

ПРИМЕР:
┌──────────────────────────────────────────────────────────────┐
│ Каждый сервис P99 = 100ms (99% запросов < 100ms)            │
├────────────────┬──────────────┬──────────────────────────────┤
│ Fan-out (N)    │ P(все < T)   │ % медленных запросов         │
├────────────────┼──────────────┼──────────────────────────────┤
│ 1 сервис       │ 99.0%        │ 1.0%                         │
│ 5 сервисов     │ 95.1%        │ 4.9%                         │
│ 10 сервисов    │ 90.4%        │ 9.6% ← почти 1 из 10!        │
│ 20 сервисов    │ 81.8%        │ 18.2% ← почти 1 из 5!        │
│ 50 сервисов    │ 60.5%        │ 39.5% ← 2 из 5 медленные!    │
└────────────────┴──────────────┴──────────────────────────────┘
```

**Стратегии борьбы:**
```
1. HEDGED REQUESTS
   Отправляем 2+ копии запроса → берём первый ответ

   Request ──┬──► Service Instance A ──► Response (быстрый)
             └──► Service Instance B ──► Response (игнорируем)

2. BACKUP REQUESTS
   Ждём T мс, если нет ответа → отправляем backup

   t=0:   Request ──► Instance A
   t=T:   Нет ответа? ──► Instance B (backup)
   t=T+x: Берём первый ответ

3. DEADLINE PROPAGATION
   Общий deadline для всей цепочки

   Gateway (deadline=500ms)
     → Service A (remaining=480ms)
       → Service B (remaining=400ms)
         → Отменяем если deadline истёк
```

---

### Модель 5: Latency vs Consistency Trade-off — Скорость vs Правильность

**Принцип:** Часто можно обменять consistency на latency (и наоборот).

```
СПЕКТР TRADE-OFFS:

Strong Consistency                         Eventual Consistency
(медленно, но точно)                       (быстро, но "почти" точно)
        │                                            │
        ▼                                            ▼
┌───────────────────────────────────────────────────────────────┐
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ │       │           │              │                │         │
│ Sync    2PC     Read-your-    Async         CDN Cache        │
│ Writes           writes      Replication    (stale data)     │
│                                                               │
│ Latency: 500ms+ → 200ms  →  100ms    →   50ms   →   10ms     │
│ Consistency: ████ → ███   →  ██      →   █      →   ░        │
└───────────────────────────────────────────────────────────────┘
```

**Решающие вопросы:**
| Вопрос | Если ДА | Если НЕТ |
|--------|---------|----------|
| Финансовые транзакции? | Strong consistency | Eventual OK |
| Пользователь видит свои данные? | Read-your-writes | Eventual OK |
| Данные меняются редко? | Aggressive caching | Short TTL |
| Ошибка = потеря денег? | Strong + latency penalty | Eventual + speed |

**Практические паттерны:**
```
1. READ-YOUR-WRITES (компромисс)
   - Write → Primary DB (slow, consistent)
   - Read своих данных → Primary DB
   - Read чужих данных → Replica (fast, eventually consistent)

2. STALE-WHILE-REVALIDATE (для кэша)
   - Отдаём stale данные немедленно (fast!)
   - В фоне обновляем кэш (consistency)

   Cache-Control: max-age=60, stale-while-revalidate=3600

3. OPTIMISTIC UI (для UX)
   - UI обновляется мгновенно (optimistic)
   - Если сервер отклонил → rollback
   - Latency = 0ms (perceived), consistency = eventual
```

---

## Почему это важно

**Latency (задержка)** — это время между отправкой запроса и получением первого байта ответа. В отличие от throughput (пропускной способности), latency напрямую влияет на **восприятие пользователем**.

### Психология задержки

| Порог        | Восприятие пользователем                      |
|-------------|----------------------------------------------|
| < 100ms     | Мгновенно, система реагирует сразу           |
| 100-300ms   | Заметная задержка, но приемлемо              |
| 300-1000ms  | Система "думает", пользователь ждёт          |
| > 1 секунды | Потеря внимания, пользователь отвлекается    |
| > 10 секунд | Пользователь уходит                          |

> **Google исследование:** каждые 100ms дополнительной задержки снижают конверсию на 1%.

### Бизнес-влияние

- **Amazon:** 100ms задержки = -1% продаж (~$1.6 млрд/год)
- **Google:** 500ms задержки = -20% поисковых запросов
- **Финтех:** >10ms = потеря арбитражных возможностей

---

## Что такое latency

### Компоненты latency

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Полный путь запроса                               │
├─────────┬──────────┬────────────┬──────────────┬──────────┬────────┤
│   DNS   │ TCP      │    TLS     │   Request    │ Server   │Response│
│ Lookup  │Handshake │ Handshake  │  Transfer    │Processing│Transfer│
│  20-    │  1 RTT   │  1-2 RTT   │   Network    │ Backend  │Network │
│ 200ms   │          │            │              │          │        │
└─────────┴──────────┴────────────┴──────────────┴──────────┴────────┘
```

### Round-Trip Time (RTT)

**RTT** — время на отправку пакета и получение ответа. Это базовая единица измерения latency.

| Маршрут                    | Типичный RTT     |
|---------------------------|------------------|
| Localhost                  | < 1ms            |
| Локальная сеть (LAN)       | 1-5ms            |
| Город → город (один регион)| 10-30ms          |
| Межконтинентальный         | 100-200ms        |
| Спутниковый интернет       | 500-700ms        |

**Минимальный RTT ограничен скоростью света:**
- Москва → Нью-Йорк (7500 км): минимум ~50ms (физический предел)
- Реальность: 100-150ms из-за маршрутизации

### Типы latency метрик

| Метрика | Описание | Когда использовать |
|---------|----------|-------------------|
| **P50** (медиана) | 50% запросов быстрее этого значения | Общая картина |
| **P95** | 95% запросов быстрее | SLO для большинства сервисов |
| **P99** | 99% запросов быстрее | Выявление "хвостовых" задержек |
| **P99.9** | 99.9% запросов быстрее | Критичные финансовые системы |

> **Важно:** Среднее (average) — плохая метрика! Она скрывает проблемы хвостовых задержек.

### Усиление latency в микросервисах

Если запрос проходит через 5 сервисов параллельно, каждый с P99 = 100ms:

```
P(все 5 сервисов < 100ms) = 0.99^5 ≈ 95%
```

То есть **5% запросов будут медленнее 100ms!** Для достижения общего P99 = 100ms каждый сервис должен иметь P99.8 ≈ 100ms.

---

## Измерение latency

### Инструменты командной строки

```bash
# Базовый ping (ICMP)
ping -c 10 google.com

# Более точный: TCP ping (на уровне приложения)
# Рекомендуется вместо ICMP ping
hping3 -S -p 443 -c 10 google.com

# MTR - traceroute + ping (интерактивный)
mtr --report --report-cycles 100 google.com

# HTTP latency с детализацией
curl -w "@curl-format.txt" -o /dev/null -s https://example.com
```

**curl-format.txt** для детализации:
```
     time_namelookup:  %{time_namelookup}s\n
        time_connect:  %{time_connect}s\n
     time_appconnect:  %{time_appconnect}s\n
    time_pretransfer:  %{time_pretransfer}s\n
       time_redirect:  %{time_redirect}s\n
  time_starttransfer:  %{time_starttransfer}s\n
                     ----------\n
          time_total:  %{time_total}s\n
```

### TTFB vs Total Time

| Метрика | Что измеряет | Формула |
|---------|-------------|---------|
| **TTFB** | DNS + Connect + TLS + Server Response | До первого байта данных |
| **Total Time** | TTFB + Content Transfer | Полное время загрузки |

### Сетевые тестеры

```bash
# Netperf - TCP latency (лучше чем ping для приложений)
netperf -H server -t TCP_RR -l 60

# Результат: Transaction Rate (trans/sec)
# Latency = 1000 / Transaction Rate (ms)

# iPerf3 - только throughput и jitter, НЕ latency
iperf3 -c server -t 30
```

---

## Оптимизация TCP latency

### Почему TCP добавляет latency

**TCP создавался для надёжности, не для скорости.** Каждый механизм надёжности — это дополнительная задержка:
- **Handshake** — прежде чем отправить данные, нужно установить соединение
- **Slow Start** — не доверяем сети, начинаем с маленькой скорости
- **ACK ожидание** — каждый пакет должен быть подтверждён
- **Retransmissions** — потерянные пакеты блокируют stream

**Цель TCP latency optimization:** сохранить надёжность, убрать избыточную осторожность. Мы знаем свою сеть лучше, чем консервативные defaults 1980-х годов.

### TCP Handshake (1 RTT)

Каждое новое TCP соединение требует **3-way handshake**:

```
Client                    Server
  |                          |
  |-------- SYN ------------>|  RTT/2
  |<------ SYN-ACK ---------|  RTT/2
  |-------- ACK ------------>|  (данные могут идти вместе)
  |                          |
  ========= 1 RTT ============
```

**Проблема:** Для короткоживущих соединений handshake = значительная часть времени.

### TCP Fast Open (TFO)

Позволяет передавать данные уже в SYN-пакете:

```bash
# Включение на Linux сервере
echo 3 > /proc/sys/net/ipv4/tcp_fastopen
# 1 = клиент, 2 = сервер, 3 = оба

# Nginx
listen 443 ssl fastopen=256;
```

**Ограничения TFO:**
- Работает только для повторных соединений (нужен cookie)
- Ограниченный размер данных в SYN
- Уязвим к replay-атакам (безопасно только для идемпотентных запросов)

### TCP Slow Start

Новые соединения начинают с маленького **congestion window (cwnd)**:

```
Initial cwnd = 10 segments (14KB примерно)
После каждого ACK: cwnd удваивается (экспоненциальный рост)
```

**Проблема:** Первый запрос будет медленным, даже на быстром канале.

**Решение — увеличить initial cwnd:**

```bash
# Проверить текущее значение
ip route show | grep initcwnd

# Установить initcwnd = 10 (RFC 6928)
ip route change default via 192.168.1.1 initcwnd 10 initrwnd 10
```

> **Google:** увеличение initcwnd до 10 улучшает latency на ~10% для высоко-RTT сетей.

### Keep-Alive и Connection Reuse

**Переиспользование соединений** — самый эффективный способ снижения latency:

```nginx
# Nginx upstream keepalive
upstream backend {
    server 127.0.0.1:8080;
    keepalive 32;  # Пул постоянных соединений
}

server {
    location / {
        proxy_http_version 1.1;
        proxy_set_header Connection "";  # Отключаем "close"
        proxy_pass http://backend;
    }
}
```

---

## TLS Latency оптимизация

### Почему TLS — главный источник latency в современном вебе

**HTTPS стал обязательным.** Браузеры помечают HTTP как небезопасный, Google понижает HTTP сайты в поиске, HTTP/2 и HTTP/3 работают только через TLS. Но шифрование добавляет latency:
- **Key exchange** — договориться об алгоритмах и ключах
- **Certificate verification** — проверить сертификат сервера
- **OCSP check** — проверить что сертификат не отозван

**TLS 1.2 = 2 RTT до первых данных.** Для WAN соединения с 100ms RTT — это 200ms только на handshake. TLS 1.3 сократил до 1 RTT, а 0-RTT позволяет отправлять данные немедленно (для повторных соединений).

### TLS 1.2 vs TLS 1.3

| Версия | Handshake RTT | С Session Resumption |
|--------|---------------|---------------------|
| TLS 1.2 | 2 RTT | 1 RTT |
| TLS 1.3 | 1 RTT | 0-RTT (Early Data) |

### TLS 1.3 0-RTT (Early Data)

Позволяет отправлять данные **до завершения handshake**:

```
Client                           Server
  |                                |
  |-- ClientHello + Early Data --->|  Данные сразу!
  |<----- ServerHello + ... ------|
  |                                |
```

**Nginx конфигурация:**

```nginx
ssl_early_data on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;

# Защита от replay-атак
proxy_set_header Early-Data $ssl_early_data;
```

**Безопасность 0-RTT:**
- Уязвим к **replay-атакам**
- Безопасно только для **GET/HEAD** без side effects
- Сервер должен проверять идемпотентность запроса

### Session Resumption

```nginx
# Session tickets (stateless)
ssl_session_tickets on;
ssl_session_ticket_key /etc/nginx/ticket.key;

# Session cache (stateful, безопаснее)
ssl_session_cache shared:SSL:50m;
```

**~40% HTTPS соединений** — это resumption, экономия 1 RTT для каждого!

---

## DNS Latency оптимизация

### Скрытый враг производительности

**DNS lookup происходит до всего остального.** Пока браузер не узнает IP адрес сервера, он не может даже начать TCP handshake. На современной странице с 50+ разными доменами (fonts, analytics, ads, CDN, API) — это 50 потенциальных блокирующих запросов.

**Почему DNS latency недооценивают:**
- Обычно это 20-50ms — кажется мелочью
- Но это происходит ПЕРЕД всем остальным — блокирует rendering
- При cache miss — рекурсивный запрос до 200ms
- Мобильные сети добавляют ещё больше latency

**Стратегия:** минимизировать количество разных доменов и предзагружать DNS для необходимых.

### DNS Lookup время

| Состояние | Время |
|-----------|-------|
| Кэш браузера | 0ms |
| Кэш ОС | 0-1ms |
| Локальный DNS-резолвер | 1-10ms |
| Рекурсивный запрос | 20-200ms |

### DNS Prefetch

Резолвит DNS заранее для внешних доменов:

```html
<!-- DNS prefetch для сторонних ресурсов -->
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="dns-prefetch" href="//cdn.example.com">
<link rel="dns-prefetch" href="//analytics.google.com">
```

**Когда использовать:** для всех сторонних доменов, с которых загружаются ресурсы.

### Preconnect

Выполняет DNS + TCP + TLS заранее:

```html
<!-- Preconnect для критичных ресурсов -->
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://api.example.com">

<!-- Fallback для старых браузеров -->
<link rel="dns-prefetch" href="//fonts.gstatic.com">
```

**Ограничения:**
- Максимум **4-6 preconnect** (соединения дорогие)
- Для остальных — используй `dns-prefetch`

> **Chrome:** preconnect улучшил Time To Interactive почти на 1 секунду.

### Быстрый DNS-резолвер

```bash
# Проверить скорость DNS
dig @8.8.8.8 example.com | grep "Query time"
dig @1.1.1.1 example.com | grep "Query time"

# Cloudflare 1.1.1.1 — обычно самый быстрый
# Google 8.8.8.8 — стабильный
```

---

## HTTP/2 и HTTP/3

### Эволюция HTTP и борьба с latency

**HTTP/1.1 был спроектирован для документов, не для приложений.** Одно соединение = один запрос за раз. Браузеры обходили это открытием 6-8 параллельных соединений, но каждое требует отдельный handshake, отдельный TLS negotiation, отдельный slow start.

**HTTP/2 добавил multiplexing:** одно соединение, множество параллельных streams. Экономия на handshakes, лучше использование одного "прогретого" соединения. Но осталась проблема — TCP-level blocking: потеря одного пакета блокирует ВСЕ streams.

**HTTP/3 (QUIC) решает TCP blocking:** каждый stream независим на уровне transport. Плюс 0-RTT connection establishment. Это особенно важно для мобильных сетей с packet loss.

### HTTP/2 Multiplexing

HTTP/1.1 проблема — **Head-of-Line Blocking (HOL)**:
- Браузер открывает 6-8 соединений к домену
- Каждое соединение обрабатывает 1 запрос за раз

HTTP/2 решение — **multiplexing**:
- 1 соединение, множество параллельных streams
- Экономия на handshakes

```
HTTP/1.1:  [====]  [====]  [====]  (последовательно)

HTTP/2:    [====]
           [======]
           [===]                   (параллельно)
```

### TCP-level HOL в HTTP/2

Проблема: потеря 1 пакета блокирует **все** streams:

```
Stream 1: ████████░░░░  (ждёт потерянный пакет)
Stream 2: ████████░░░░  (тоже заблокирован!)
Stream 3: ████████░░░░  (и этот тоже!)
```

### HTTP/3 (QUIC)

QUIC решает TCP HOL — каждый stream независим:

```
Stream 1: ████████░░░░  (ждёт)
Stream 2: ████████████  (продолжает!)
Stream 3: ████████████  (продолжает!)
```

**Latency преимущества QUIC:**
- 0-RTT connection establishment
- Нет TCP HOL blocking
- Быстрое восстановление при смене сети (connection migration)

**Google статистика:**
- -3.6% latency для Google Search
- -15.3% buffering для YouTube

**Когда QUIC выгоден:**
- Высокий packet loss (>1%)
- Мобильные сети
- Короткие соединения (< 1MB данных)

**Когда TCP лучше:**
- Стабильные сети с низким loss
- Большие файлы, долгие соединения
- Высокий throughput (QUIC имеет больший CPU overhead)

---

## Mobile Network Latency

### Сравнение технологий

| Технология | Типичный Latency | Throughput |
|-----------|-----------------|------------|
| 3G        | 100-500ms       | 1-5 Mbps   |
| 4G/LTE    | 20-50ms         | 10-50 Mbps |
| 5G        | 1-10ms          | 100+ Mbps  |
| WiFi (домашний) | 2-50ms   | Varies     |
| WiFi (публичный) | 50-200ms | Varies   |

### 5G Latency: реальность vs маркетинг

| Заявления | Реальность |
|-----------|-----------|
| < 1ms | Только в идеальных лабораторных условиях |
| 1-5ms | Edge computing, прямая видимость до вышки |
| 8-12ms | Типичный air latency без помех |
| 10-30ms | Реальный end-to-end latency |

### Оптимизация для мобильных

1. **Меньше запросов** — каждый запрос = radio wake-up latency
2. **Bundling** — объединяй мелкие запросы
3. **HTTP/3** — лучше справляется с packet loss в cellular
4. **Offline-first** — Service Workers для критичных ресурсов

---

## Connection Pooling

### Зачем нужен пул соединений

Создание нового соединения к БД:
1. TCP handshake: 1 RTT
2. TLS (если есть): 1-2 RTT
3. Database authentication: 1+ RTT
4. **PostgreSQL:** fork процесса + выделение памяти

**Без пула:** каждый запрос = 50-100ms overhead

### Оптимальный размер пула

```
pool_size = (2 × CPU cores) до (4 × CPU cores)
```

**HikariCP рекомендация для PostgreSQL:**
```java
maximumPoolSize = 10  // Для большинства приложений достаточно
minimumIdle = 10      // = maximumPoolSize для стабильного latency
connectionTimeout = 30000  // 30 секунд
idleTimeout = 600000  // 10 минут
```

### PgBouncer для PostgreSQL

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction  # Или session/statement
default_pool_size = 20
max_client_conn = 1000
```

**Результат:** +4x throughput, -40% connection latency

### HTTP Connection Pool

```python
# Python requests с пулом
import requests
from requests.adapters import HTTPAdapter

session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=10,  # Пул на хост
    pool_maxsize=10,      # Соединений в пуле
    max_retries=3
)
session.mount('https://', adapter)

# Все запросы через session переиспользуют соединения
response = session.get('https://api.example.com/data')
```

---

## CDN и Edge Computing

### Как CDN снижает latency

```
Без CDN:
User (Tokyo) → Origin (New York)
RTT: 150-200ms

С CDN:
User (Tokyo) → Edge (Tokyo) → Origin (New York)
Cached:  RTT: 5-10ms
Dynamic: RTT: 5-10ms + Origin processing
```

### Edge Computing

**CDN 2.0:** выполнение кода на edge-серверах:
- Cloudflare Workers
- AWS Lambda@Edge
- Fastly Compute@Edge

```javascript
// Cloudflare Worker — персонализация на edge
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const country = request.cf.country
  // Логика без roundtrip до origin
  return new Response(`Hello from ${country}!`)
}
```

### Video Streaming Latency (2024)

| Технология | Типичный Latency |
|-----------|-----------------|
| Традиционный HLS | 15-30 секунд |
| Low-Latency HLS | 2-5 секунд |
| LL-DASH | 2-5 секунд |
| WebRTC | < 1 секунды |
| Edge + CMAF | 3-5 секунд |

---

## P99 Latency Optimization

### Почему P99 важнее среднего

```
Запросы: [10, 12, 11, 13, 10, 11, 12, 11, 10, 500]ms

Average: 60ms  ← Выглядит нормально
P50:     11ms  ← Типичный запрос
P99:     500ms ← 1% пользователей ждут 0.5 секунды!
```

### Причины высокого P99

| Причина | Решение |
|---------|---------|
| GC паузы | Тюнинг GC, ZGC/Shenandoah |
| Cold starts | Pre-warming, provisioned concurrency |
| Noisy neighbors | Dedicated instances, CPU pinning |
| Network retries | Hedged requests, circuit breakers |
| DB connection storms | Connection pooling |

### Стратегии снижения P99

**1. Hedged Requests:**
```python
# Отправляем второй запрос если первый медленный
async def hedged_request(url, timeout=50):
    primary = asyncio.create_task(fetch(url))
    await asyncio.sleep(0.050)  # Ждём 50ms

    if not primary.done():
        backup = asyncio.create_task(fetch(url))
        done, _ = await asyncio.wait(
            [primary, backup],
            return_when=asyncio.FIRST_COMPLETED
        )
        return done.pop().result()

    return await primary
```

**2. Circuit Breaker:**
```python
# Если сервис деградировал — fail fast
if circuit_breaker.is_open:
    return fallback_response()  # Мгновенно
else:
    response = await service.call()
```

**3. Request Deadlines:**
```go
// Go context с таймаутом
ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
defer cancel()

result, err := service.Call(ctx)
if err == context.DeadlineExceeded {
    // Fail fast, не ждём
}
```

---

## Latency Budget

### Определение бюджета

**Latency Budget** — максимально допустимое время на каждый компонент:

```
Общий бюджет: 200ms

Распределение:
├── DNS:        10ms (5%)
├── TCP+TLS:    30ms (15%)
├── Network:    40ms (20%)
├── Backend:    80ms (40%)
├── Rendering:  40ms (20%)
└── Буфер:      0ms  (0%) — опасно!
```

### Правила latency budget

1. **Оставляй буфер 20%** — для неожиданных задержек
2. **Каждый сервис = бюджет / N × 0.8** — для цепочки из N сервисов
3. **P99 бюджет = 2-3× P50 бюджета**
4. **Мониторь процент использования бюджета**

### Performance Budget для Web

```yaml
# lighthouse-budget.json
{
  "timings": [
    { "metric": "first-contentful-paint", "budget": 1500 },
    { "metric": "largest-contentful-paint", "budget": 2500 },
    { "metric": "total-blocking-time", "budget": 200 },
    { "metric": "time-to-interactive", "budget": 3000 }
  ]
}
```

---

## Подводные камни

### 1. Измерение только average latency

**Проблема:** Average скрывает tail latency.

**Решение:** Всегда смотри P95, P99, P99.9.

### 2. Оптимизация throughput вместо latency

**Проблема:** Batching улучшает throughput, но увеличивает latency.

```
Без batching:  Запрос 1 → Ответ 1 (10ms)
С batching:    Запрос 1 → ... ждём 50ms ... → Batch response
```

**Решение:** Балансируй batch size и max delay.

### 3. Игнорирование первого запроса

**Проблема:** Cold start значительно медленнее:
- Нет соединения (TCP + TLS)
- Нет прогретого кэша
- Lazy initialization кода

**Решение:** Pre-warming, проверяй latency первых запросов отдельно.

### 4. Тестирование только в локальной сети

**Проблема:** Локально RTT = 0.5ms, в production = 50-200ms.

**Решение:**
```bash
# Добавить искусственную задержку для тестов
tc qdisc add dev eth0 root netem delay 100ms 20ms

# Удалить после тестов
tc qdisc del dev eth0 root netem
```

### 5. Недооценка DNS latency

**Проблема:** DNS lookup может добавить 20-200ms на каждый новый домен.

**Решение:** dns-prefetch, preconnect, минимизация внешних доменов.

### 6. Переоптимизация preconnect

**Проблема:** Слишком много preconnect тратит ресурсы зря.

**Решение:** Максимум 4-6 preconnect, остальное — dns-prefetch.

### 7. Не учитывать мобильных пользователей

**Проблема:** LTE latency = 20-50ms, 3G = 100-500ms.

**Решение:** Тестируй с Network Throttling, оптимизируй для worst case.

---

## Чек-лист оптимизации

### Транспортный уровень
- [ ] TCP Fast Open включён
- [ ] Initial cwnd = 10+
- [ ] BBR congestion control
- [ ] Keep-alive connections

### TLS
- [ ] TLS 1.3 с 0-RTT
- [ ] Session resumption настроен
- [ ] OCSP stapling включён

### DNS
- [ ] dns-prefetch для сторонних доменов
- [ ] preconnect для критичных (max 4-6)
- [ ] Минимум внешних доменов

### HTTP
- [ ] HTTP/2 или HTTP/3
- [ ] Connection pooling
- [ ] Gzip/Brotli сжатие

### Архитектура
- [ ] CDN для статики и edge computing
- [ ] Connection pools для БД
- [ ] Circuit breakers и timeouts
- [ ] Hedged requests для критичных путей

### Мониторинг
- [ ] P50, P95, P99 метрики
- [ ] Latency budgets определены
- [ ] Алерты на деградацию
- [ ] Distributed tracing (OpenTelemetry)

---

## Связанные материалы

- [[network-performance-optimization]] — общая оптимизация производительности сети
- [[network-transport-layer]] — TCP/UDP протоколы детально
- [[network-http-evolution]] — HTTP/2 и HTTP/3
- [[network-dns-tls]] — DNS и TLS подробнее
- [[network-troubleshooting-advanced]] — диагностика проблем latency
- [[network-cloud-modern]] — CDN и edge computing

---

## Источники

### Теоретические основы
- Little J.D.C. (1961). "A Proof for the Queuing Formula: L = lambda * W" — Operations Research
- Dean J., Barroso L.A. (2013). "The Tail at Scale" — Communications of the ACM (tail latency amplification)
- Jacobson V. (1988). "Congestion Avoidance and Control" — ACM SIGCOMM (slow start и его влияние на latency)
- RFC 7323 (2014). TCP Extensions for High Performance — Window Scaling, Round-Trip Time Measurement

### Практические руководства

| # | Источник | Тип | Ключевой вклад |
|---|----------|-----|----------------|
| 1 | [High Performance Browser Networking](https://hpbn.co) | Книга | TCP/TLS latency, fundamentals |
| 2 | [Cloudflare TLS 1.3 0-RTT](https://blog.cloudflare.com/introducing-0-rtt/) | Блог | 0-RTT implementation |
| 3 | [KeyCDN Latency Optimization](https://www.keycdn.com/blog/latency-optimization) | Блог | CDN и общие практики |
| 4 | [MDN dns-prefetch](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/dns-prefetch) | Docs | Resource hints |
| 5 | [Aerospike P99 Latency](https://aerospike.com/blog/what-is-p99-latency/) | Блог | Percentile метрики |
| 6 | [Control Plane P99 Tips](https://controlplane.com/community-blog/post/4-tips-to-improve-p99-latency) | Блог | P99 оптимизация |
| 7 | [Stack Overflow Connection Pooling](https://stackoverflow.blog/2020/10/14/improve-database-performance-with-connection-pooling/) | Блог | DB connection pools |
| 8 | [Microsoft HTTP Connection Pool](https://devblogs.microsoft.com/premier-developer/the-art-of-http-connection-pooling-how-to-optimize-your-connections-for-peak-performance/) | Блог | HTTP pooling |
| 9 | [QUIC Benchmarks Study](https://cs.brown.edu/~tab/papers/QUIC_WWW21.pdf) | Paper | QUIC vs TCP production |
| 10 | [Salesforce HTTP/2 HOL](https://engineering.salesforce.com/the-full-picture-on-http-2-and-hol-blocking-7f964b34d205/) | Блог | HOL blocking deep dive |
| 11 | [CableFree LTE Latency](https://www.cablefree.net/wirelesstechnology/4glte/lte-network-latency/) | Справка | Mobile network latency |
| 12 | [SpeedCurve Performance Budgets](https://www.speedcurve.com/web-performance-guide/complete-guide-performance-budgets/) | Гайд | Latency budgets |
| 13 | [Google Cloud Netperf](https://cloud.google.com/blog/products/networking/using-netperf-and-ping-to-measure-network-latency) | Блог | Latency measurement |
| 14 | [DigitalOcean Network Latency](https://www.digitalocean.com/resources/articles/network-latency) | Гайд | Общий обзор |
| 15 | [Expedia dns-prefetch Tips](https://medium.com/expedia-group-tech/dns-prefetch-preconnect-7-tips-tricks-and-pitfalls-82d633c7f210) | Блог | Практические советы |

---

## Связь с другими темами

**[[network-performance-optimization]]** — Performance optimization — это более широкая тема, включающая TCP tuning, системную оптимизацию ядра и benchmarking, тогда как latency optimization фокусируется конкретно на минимизации задержек. Многие техники пересекаются (connection pooling, buffer tuning), но latency optimization добавляет специфические подходы: prefetching, percentile-based анализ, fan-out оптимизацию. Рекомендуется сначала изучить latency optimization для понимания метрик, затем переходить к системной оптимизации.

**[[network-transport-layer]]** — TCP и UDP — это транспортные протоколы, характеристики которых напрямую определяют latency: TCP-handshake добавляет 1 RTT, slow start увеличивает время первой загрузки, а congestion control влияет на стабильность задержек. QUIC объединяет transport и TLS handshake в 1 RTT (или 0-RTT при reconnect), радикально снижая latency. Глубокое понимание транспортного уровня необходимо для осознанной оптимизации задержек.

**[[network-http-evolution]]** — HTTP/1.1, HTTP/2 и HTTP/3 кардинально различаются по latency-характеристикам: head-of-line blocking в HTTP/1.1, мультиплексирование в HTTP/2, и устранение HOL blocking на транспортном уровне в HTTP/3. Понимание эволюции HTTP объясняет, почему простое обновление протокола может снизить latency на десятки процентов. Изучайте параллельно с latency optimization.

---

## Источники и дальнейшее чтение

### Теоретические основы
- **Kurose, Ross (2021).** *Computer Networking: A Top-Down Approach.* — фундаментальные объяснения queueing delay, propagation delay и transmission delay; математическая модель задержек помогает определить теоретические пределы оптимизации.
- **Fall, Stevens (2011).** *TCP/IP Illustrated, Vol. 1 (2nd ed).* — детальный разбор TCP-таймеров, retransmission и congestion control с реальными дампами пакетов; необходим для понимания, откуда берутся задержки на транспортном уровне.

### Практические руководства
- **Grigorik (2013).** *High Performance Browser Networking.* — лучшее практическое руководство по latency optimization: TCP, TLS, HTTP/2, WebSocket, WebRTC; доступно бесплатно на hpbn.co; обязательное чтение для любого, кто оптимизирует сетевые задержки.

---

## Проверь себя

> [!question]- Сервис вызывает 5 микросервисов параллельно (fan-out). P50 каждого сервиса 10ms, P99 -- 200ms. Почему итоговый P99 родительского запроса будет значительно выше 200ms?
> При fan-out итоговый latency определяется самым медленным из параллельных вызовов. Вероятность того, что хотя бы 1 из 5 попадет в P99 = 1 - (0.99)^5 = 4.9%. Это значит, что почти каждый 20-й запрос будет ждать 200ms+. Итоговый P99 будет определяться ещё более редкими хвостами каждого сервиса. Это называется tail latency amplification. Решения: hedged requests, request deadlines, уменьшение fan-out, кэширование ответов параллельных вызовов.

> [!question]- Страница загружает ресурсы с 8 разных доменов. Что быстрее: поставить dns-prefetch на все 8 или preconnect на все 8? Почему?
> Preconnect на все 8 будет контрпродуктивным. Preconnect выполняет DNS + TCP + TLS для каждого домена — это дорогая операция, которая конкурирует за ресурсы с загрузкой самой страницы. Рекомендация: preconnect для 4-6 самых критичных доменов (шрифты, API, основной CDN), dns-prefetch для остальных. dns-prefetch дешевый (только DNS lookup), preconnect — дорогой (полное соединение).

> [!question]- Разработчик измеряет average latency API и получает 50ms. Он доволен. Почему этого недостаточно и какие метрики нужны?
> Average скрывает tail latency. Пример: 99 запросов по 10ms + 1 запрос по 4000ms = average 50ms, но 1% пользователей ждут 4 секунды. Нужны percentiles: P50 (типичный опыт), P95 (граница нормы), P99 (worst case для 1%), P99.9 (для критичных систем). Кроме того, нужно разделять TTFB (время до первого байта) и total time, а также мониторить latency по сегментам: DNS, TCP connect, TLS, server processing, transfer.

---

## Ключевые карточки

Latency vs Throughput
?
Latency — время одного запроса (задержка). Throughput — количество запросов в единицу времени (пропускная способность). Можно иметь высокий throughput при высоком latency (конвейер) и наоборот. Batching увеличивает throughput, но повышает latency.

P50, P95, P99
?
Percentiles: P50 — медиана, половина запросов быстрее. P95 — 95% быстрее, 5% хуже. P99 — 99% быстрее, 1% хуже. Для оценки пользовательского опыта P99 важнее average, потому что показывает worst case.

dns-prefetch vs preconnect
?
dns-prefetch выполняет только DNS lookup заранее (дешево). preconnect выполняет DNS + TCP + TLS заранее (дорого). Рекомендация: max 4-6 preconnect для критичных доменов, dns-prefetch для остальных.

TTFB (Time To First Byte)
?
Время от отправки запроса до получения первого байта ответа. Включает DNS + TCP + TLS + server processing. Показывает backend latency. Можно измерить: `curl -w "%{time_starttransfer}" -o /dev/null -s URL`.

Hedged requests
?
Отправка дублирующего запроса, если основной не ответил за пороговое время (например, P50). Берется первый пришедший ответ. Снижает tail latency ценой дополнительной нагрузки (~5%). Применять только для идемпотентных запросов.

Latency budget
?
Максимально допустимое время на каждый компонент пути запроса. Пример для 200ms бюджета: DNS 10ms, TCP+TLS 30ms, Network 40ms, Backend 80ms, Buffer 40ms. Правило: оставлять 20% буфер на непредвиденное.

Connection pooling
?
Переиспользование уже установленных TCP/TLS соединений вместо создания новых. Экономит 50-100ms на каждый запрос (TCP handshake + TLS + auth). Оптимальный размер пула для БД: 2-4x количество CPU cores.

Tail latency amplification
?
При fan-out на N сервисов вероятность попадания в tail: 1-(1-p)^N. Для N=10 и p99: 1-(0.99)^10 = 9.6% запросов попадают в "хвост". Решения: hedged requests, deadlines, уменьшение fan-out.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Системная оптимизация | [[network-performance-optimization]] | TCP tuning, sysctl, benchmarking |
| Транспортный уровень | [[network-transport-layer]] | TCP handshake, congestion control, QUIC |
| HTTP протоколы | [[network-http-evolution]] | HTTP/2 multiplexing, HTTP/3 0-RTT |
| Мониторинг latency | [[network-observability]] | Prometheus, Grafana, percentile метрики |
| CDN и облако | [[network-cloud-modern]] | Edge computing, CDN |
| Обзор раздела | [[networking-overview]] | Карта всех материалов по сетям |

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции: 5 аналогий (latency vs throughput труба/автобан, RTT и TCP handshake как переговоры по телефону, percentiles P50/P99 как очередь в поликлинике, fan-out problem как сборка IKEA, TTFB vs full load как первая ложка супа), 6 типичных ошибок с СИМПТОМ/РЕШЕНИЕ (average вместо percentiles, naive retries→retry storm, игнорирование tail latency в fan-out, CDN кэширует динамический контент, оптимизация без baseline, connection per request), 5 ментальных моделей (waterfall analysis, latency budget, 80/20 rule для latency, tail latency amplification формула, latency vs consistency trade-off)*

---
title: "Resilience Patterns: Circuit Breaker, Retry, Bulkhead"
created: 2025-12-22
modified: 2026-01-02
type: concept
status: published
confidence: high
tags:
  - topic/architecture
  - resilience
  - fault-tolerance
  - circuit-breaker
  - patterns
  - type/concept
  - level/intermediate
related:
  - "[[architecture-overview]]"
  - "[[architecture-distributed-systems]]"
  - "[[architecture-rate-limiting]]"
prerequisites:
  - "[[architecture-distributed-systems]]"
reading_time: 55
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Resilience Patterns: Circuit Breaker, Retry, Bulkhead

> "Everything fails, all the time" — Werner Vogels (AWS CTO). Resilience — это не предотвращение сбоев, а умение gracefully (изящно) их обрабатывать.

---

## Prerequisites (Что нужно знать заранее)

Прежде чем изучать resilience patterns, убедись, что понимаешь:

| Тема | Зачем нужна | Где изучить |
|------|------------|-------------|
| Microservices basics | Понимание распределённых систем | [[architecture-overview]] |
| HTTP и REST API | Как сервисы общаются | [[api-design]] |
| Async/await в коде | Понимание примеров на Python | Документация языка |
| Что такое latency | Задержка при вызове сервисов | [[performance-optimization]] |

---

## Теоретические основы: формальный базис паттернов устойчивости

### Circuit Breaker: атрибуция и формальная модель

> **Атрибуция:** Паттерн Circuit Breaker описан Майклом Найгардом в книге **"Release It!" (2007)**. Название — прямая аналогия с электрическим автоматом: при перегрузке цепь размыкается, предотвращая cascading failure.

**Формальная модель — конечный автомат (FSM):**
```
CLOSED --[failure_count ≥ threshold]--> OPEN
OPEN   --[timeout expires]-----------> HALF-OPEN
HALF-OPEN --[test succeeds]----------> CLOSED
HALF-OPEN --[test fails]-------------> OPEN
```

Это реализация **fail-fast principle**: лучше быстро вернуть ошибку, чем ждать timeout и потреблять ресурсы.

### Exponential Backoff: формальная модель

> **Происхождение:** Экспоненциальный backoff изобретён для протокола **Ethernet** (Metcalfe & Boggs, 1976). При коллизии в сети каждая станция ждёт случайное время из экспоненциально растущего интервала.

**Формула:** wait_time = min(base_delay · 2^attempt + random_jitter, max_delay)

| Retry # | Без jitter | С full jitter (uniform) |
|---------|-----------|------------------------|
| 1 | 1s | [0, 1s] |
| 2 | 2s | [0, 2s] |
| 3 | 4s | [0, 4s] |
| 4 | 8s | [0, 8s] |

**Jitter критически важен:** Без jitter при одновременном сбое N клиентов все ретраят в один момент → **thundering herd**. Full jitter (AWS рекомендация) распределяет нагрузку равномерно.

**Математическое обоснование:** В теории массового обслуживания (queueing theory), exponential backoff с jitter аппроксимирует оптимальную стратегию доступа к shared resource — максимизирует throughput при минимизации collisions.

### Bulkhead: принцип изоляции

> **Происхождение:** Термин Bulkhead (переборка) из кораблестроения — водонепроницаемые стенки, делящие корпус на отсеки. Пробоина в одном отсеке не тонет весь корабль.

Формально это **resource partitioning** — выделение отдельного пула ресурсов (потоки, соединения, память) для каждого зависимого сервиса:

```
БЕЗ Bulkhead:  [────── общий пул 100 потоков ──────]
                Service A, B, C делят один пул
                A зависает → 100 потоков заняты → B и C тоже мертвы

С Bulkhead:     [── A: 40 ──][── B: 40 ──][── C: 20 ──]
                A зависает → только 40 потоков заняты
                B и C работают нормально
```

Аналогия в ОС: **process isolation** (address space separation) — crash одного процесса не убивает другие.

### Теория надёжности: формула доступности

> **Формула составной доступности:** Для последовательной цепочки из n сервисов с индивидуальным uptime pᵢ: A_total = Π pᵢ

Для n=30 сервисов с p=99.9%: A = 0.999³⁰ ≈ 97.0% = **~11 часов простоя в месяц**.

Resilience patterns увеличивают **эффективный uptime** каждого звена цепи за счёт:
- Circuit Breaker → fail-fast вместо cascading failure
- Retry → recovery от transient failures
- Bulkhead → isolation of failure domains
- Fallback → graceful degradation

### Chaos Engineering: формализация (Netflix, 2011)

> **Principles of Chaos Engineering (2014):** Chaos Engineering — дисциплина экспериментирования на распределённых системах для обнаружения слабостей до того, как они станут инцидентами.

Формальный процесс:
1. Определить "steady state" (метрики нормальной работы)
2. Сформулировать гипотезу: "система продолжит работать при [событии]"
3. Внести реальный fault (kill instance, add latency, drop packets)
4. Наблюдать отклонение от steady state
5. Минимизировать blast radius эксперимента

Netflix **Chaos Monkey** (2011) — случайно убивает instances в production. **Chaos Kong** — выключает целый AWS region.

### Связи

- [[architecture-distributed-systems]] — распределённые системы, где resilience критичен
- [[caching-strategies]] — cache as fallback
- [[architecture-rate-limiting]] — rate limiting как защита от перегрузки

---

## Зачем нужны Resilience Patterns? (ПОЧЕМУ)

### Главная аналогия: Домино vs Изолированные блоки

```
❌ БЕЗ RESILIENCE PATTERNS (Домино)
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
│  A  │ → │  B  │ → │  C  │ → │  D  │
└─────┘   └─────┘   └─────┘   └─────┘
    ↓         ↓         ↓         ↓
    💥────────💥────────💥────────💥

Сервис B упал → A ждёт → C ждёт → D ждёт → ВСЁ ПАДАЕТ

✅ С RESILIENCE PATTERNS (Изолированные блоки)
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
│  A  │   │  B  │   │  C  │   │  D  │
└─────┘   └─────┘   └─────┘   └─────┘
    │         💥         │         │
    │    (изолирован)    │         │
    └─────────────────────┴─────────┘
            Остальные работают!
```

### История появления: Урок Netflix

**Август 2008 года** — Netflix пережил катастрофу:
- База данных повредилась
- **3 дня** не могли отправлять DVD клиентам
- Огромные финансовые потери

**Это стало поворотным моментом.** Netflix осознал:

> "Мы должны уйти от вертикально масштабируемых единых точек отказа (single points of failure), таких как реляционные базы данных в дата-центре, к высоконадёжным, горизонтально масштабируемым распределённым системам в облаке."

**2011 год** — Netflix создал **Hystrix** — первую production-ready библиотеку для resilience patterns. Из неё родились все современные подходы.

**21 апреля 2011** — большой сбой AWS в регионе US-East. Netflix продолжал работать без перерыва благодаря resilience patterns!

**24 декабря 2012** — проблемы с AWS Elastic Load Balancer. Netflix снова выстоял.

### Почему сбои неизбежны?

| Фактор | Объяснение |
|--------|-----------|
| **Сетевые сбои** | Пакеты теряются, кабели рвутся, роутеры перезагружаются |
| **Перегрузка сервисов** | Слишком много запросов → сервис не справляется |
| **Деплойменты** | Обновление сервиса = временная недоступность |
| **Аппаратные сбои** | Диски ломаются, память заканчивается |
| **Человеческий фактор** | Неправильная конфигурация, баги в коде |

**Статистика:** В типичном distributed system с 30 сервисами, при 99.9% uptime каждого, общий uptime системы = 0.999³⁰ = **97%**, то есть **~11 часов простоя в месяц**.

---

## TL;DR (Краткий обзор)

| Паттерн | Аналогия | Когда использовать |
|---------|----------|-------------------|
| **Retry** | Позвонить ещё раз, если не ответили | Временные сбои (сеть, перегрузка) |
| **Circuit Breaker** | Электрический предохранитель | Защита от каскадных сбоев |
| **Bulkhead** | Переборки на корабле | Изоляция критичных ресурсов |
| **Timeout** | Не ждать вечно у двери | Предотвращение зависания |
| **Fallback** | План Б если план А не сработал | Graceful degradation |

---

## Терминология с аналогиями

| Термин | Аналогия | Значение |
|--------|----------|----------|
| **Resilience** (устойчивость) | Дерево гнётся на ветру, но не ломается | Способность системы продолжать работу при сбоях |
| **Transient failure** (временный сбой) | Телефон на секунду потерял сеть | Сбой, который исправляется сам через мгновение |
| **Persistent failure** (постоянный сбой) | Телефон сломался | Сбой, который требует ручного вмешательства |
| **Cascading failure** (каскадный сбой) | Домино — одна упала, все падают | Сбой одного компонента вызывает сбой других |
| **Circuit Breaker** | Автомат в щитке — выключает при перегрузке | Механизм отключения от failing сервиса |
| **Bulkhead** (переборка) | Водонепроницаемые отсеки на корабле | Изоляция ресурсов для предотвращения распространения сбоя |
| **Fallback** (резерв) | Запасной выход в здании | Альтернативное поведение при сбое основного пути |
| **Backoff** (отступление) | Подождать перед повторным звонком | Увеличение интервала между повторными попытками |
| **Jitter** (дрожание) | Случайное время отправки SMS в группе | Случайное отклонение для предотвращения thundering herd |
| **Thundering herd** (стадо) | Все одновременно ломятся в дверь | Множество клиентов одновременно повторяют запросы |
| **Fail fast** (быстрый отказ) | Лучше сразу сказать "нет", чем заставлять ждать | Немедленное возвращение ошибки вместо долгого ожидания |
| **Graceful degradation** | Работать хуже, но работать | Снижение функциональности вместо полного отказа |

---

## Resilience Patterns Overview

### Как паттерны работают вместе (слои защиты)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      СЛОИ ЗАЩИТЫ (снаружи внутрь)                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Client (твоё приложение)                                                 │
│     │                                                                       │
│     ▼                                                                       │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ СЛОЙ 1: TIMEOUT                                                      │  │
│   │ "Не жди вечно — если за 5 секунд не ответили, считай что не ответят" │  │
│   └────────────────────────────────┬────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ СЛОЙ 2: RETRY + BACKOFF                                              │  │
│   │ "Попробуй ещё раз, но не сразу — подожди 1с, потом 2с, потом 4с"    │  │
│   └────────────────────────────────┬────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ СЛОЙ 3: CIRCUIT BREAKER                                              │  │
│   │ "5 ошибок подряд? Хватит пытаться — сервис явно лежит"              │  │
│   └────────────────────────────────┬────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ СЛОЙ 4: BULKHEAD                                                     │  │
│   │ "Только 10 одновременных запросов к этому сервису — не больше"      │  │
│   └────────────────────────────────┬────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│                    ┌─────────────────────────┐                             │
│                    │    External Service     │                             │
│                    │   (внешний сервис)      │                             │
│                    └─────────────────────────┘                             │
│                                                                             │
│   Если всё равно ошибка → FALLBACK (кэш, дефолт, degraded mode)           │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Retry Pattern (Повторные попытки)

### Аналогия: Звонок другу

```
Ты звонишь другу:
📞 Попытка 1: Не отвечает (занят)
   Ждёшь 1 секунду...
📞 Попытка 2: Не отвечает (всё ещё занят)
   Ждёшь 2 секунды...
📞 Попытка 3: "Алло!" — УСПЕХ!

Без retry: Позвонил раз → "Не ответил" → Сдался
С retry: Позвонил раз → Подождал → Позвонил снова → Успех!
```

### Зачем нужен Retry?

**Transient failures** (временные сбои) — самый частый тип ошибок:
- Сетевой пакет потерялся (0.1% пакетов теряется даже в хороших сетях)
- Сервис на мгновение перегружен
- Кратковременный DNS-сбой
- Контейнер перезапускается

**Без retry:** 0.1% пользователей видят ошибку
**С retry:** Только 0.0001% видят ошибку (0.1% × 0.1%)

### Проблема: Thundering Herd (Стадо)

```
❌ БЕЗ BACKOFF — все клиенты бьют сервер одновременно

Время:    0s    1s    2s    3s    4s    5s
Client 1: ─●────●────●────●────●────●───  (retry каждую секунду)
Client 2: ─●────●────●────●────●────●───
Client 3: ─●────●────●────●────●────●───
          ↓    ↓    ↓    ↓    ↓    ↓
Server:   ████████████████████████████  (ПЕРЕГРУЖЕН!)

Сервер и так еле дышит, а его бомбят запросами — он падает ещё сильнее!


✅ С EXPONENTIAL BACKOFF + JITTER — нагрузка распределяется

Время:    0s    1s    2s    3s    4s    5s    6s    7s    8s
Client 1: ─●─────────●──────────────────────●─────────────────
Client 2: ─●───────────●───────────────────────●──────────────
Client 3: ─●────────────●─────────────────────────●───────────
          ↓         ↓                    ↓
Server:   ██──────██────────────────██────  (Время восстановиться!)
```

### Формула Exponential Backoff

```
delay = min(base_delay × 2^attempt + random_jitter, max_delay)
```

**Пошаговый пример:**
```
Конфигурация: base_delay=1s, max_delay=60s

Попытка 1:  1 × 2^0 = 1s  + jitter (0-0.5s) = ~1.3s
Попытка 2:  1 × 2^1 = 2s  + jitter (0-1s)   = ~2.7s
Попытка 3:  1 × 2^2 = 4s  + jitter (0-2s)   = ~5.4s
Попытка 4:  1 × 2^3 = 8s  + jitter (0-4s)   = ~11s
Попытка 5:  1 × 2^4 = 16s + jitter (0-8s)   = ~22s
Попытка 6:  1 × 2^5 = 32s + jitter (0-16s)  = ~45s
Попытка 7:  1 × 2^6 = 64s → max=60s         = ~60s (ограничено)
```

### Виды Jitter (по рекомендации AWS)

| Вид | Формула | Плюсы | Минусы |
|-----|---------|-------|--------|
| **Full Jitter** | `random(0, delay)` | Лучшее распределение | Может быть слишком короткий |
| **Equal Jitter** | `delay/2 + random(0, delay/2)` | Гарантирует минимальный delay | Меньше распределения |
| **Decorrelated** | `min(max, random(base, prev×3))` | Не зависит от номера попытки | Сложнее реализовать |

**AWS рекомендует Full Jitter как default.**

### Retry Implementation (с подробными комментариями)

```python
import asyncio
import random
from typing import TypeVar, Callable, Optional, Tuple
from functools import wraps

T = TypeVar('T')  # Generic тип для возвращаемого значения

class RetryConfig:
    """
    Конфигурация retry-логики.

    Почему нужна отдельная конфигурация?
    Чтобы можно было легко менять параметры без изменения кода.
    """

    def __init__(
        self,
        max_attempts: int = 3,           # Сколько раз пытаться
        base_delay: float = 1.0,         # Начальная задержка (секунды)
        max_delay: float = 60.0,         # Максимальная задержка
        exponential_base: float = 2.0,   # Во сколько раз увеличивать
        jitter: bool = True,             # Добавлять случайность?
        retryable_exceptions: Tuple = (Exception,)  # Какие ошибки ретраить
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions


def calculate_delay(config: RetryConfig, attempt: int) -> float:
    """
    Рассчитать задержку для данной попытки.

    Формула: delay = base × 2^attempt (с ограничением max_delay)
    Если jitter включен, добавляем случайность.

    Параметры:
        config: Конфигурация retry
        attempt: Номер попытки (0, 1, 2, ...)

    Возвращает:
        Задержка в секундах
    """
    # Шаг 1: Вычисляем экспоненциальную задержку
    # Пример: 1 × 2^0 = 1, 1 × 2^1 = 2, 1 × 2^2 = 4
    delay = config.base_delay * (config.exponential_base ** attempt)

    # Шаг 2: Ограничиваем максимальной задержкой
    # Зачем? Чтобы не ждать слишком долго (например, 1024 секунды)
    delay = min(delay, config.max_delay)

    # Шаг 3: Добавляем jitter (случайность)
    # Зачем? Чтобы клиенты не ретраили одновременно
    if config.jitter:
        # Full jitter: случайное число от 0 до вычисленного delay
        delay = random.uniform(0, delay)

    return delay


def retry(config: Optional[RetryConfig] = None):
    """
    Декоратор для автоматического retry.

    Использование:
        @retry(RetryConfig(max_attempts=5))
        async def my_function():
            ...
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)  # Сохраняет имя и docstring оригинальной функции
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            # Пробуем max_attempts раз
            for attempt in range(config.max_attempts):
                try:
                    # Пытаемся выполнить функцию
                    return await func(*args, **kwargs)

                except config.retryable_exceptions as e:
                    # Ловим только "ретраибельные" ошибки
                    last_exception = e

                    # Если это не последняя попытка — ждём и пробуем снова
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(config, attempt)
                        print(f"⚠️ Попытка {attempt + 1} не удалась, "
                              f"повтор через {delay:.2f}с: {e}")
                        await asyncio.sleep(delay)

            # Все попытки исчерпаны — пробрасываем последнюю ошибку
            raise last_exception

        return wrapper
    return decorator


# ✅ Пример использования
@retry(RetryConfig(
    max_attempts=5,               # 5 попыток
    base_delay=1.0,               # Начальная задержка 1 секунда
    retryable_exceptions=(        # Ретраим только эти ошибки:
        ConnectionError,          # - Проблемы с соединением
        TimeoutError,             # - Таймаут
        # ValueError — НЕ ретраим, это баг в данных
    )
))
async def call_external_api(url: str) -> dict:
    """Вызывает внешний API с автоматическим retry."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()  # Выбросит HTTPError для 4xx/5xx
        return response.json()
```

### Когда НЕ использовать Retry

| Ситуация | Почему не ретраить | Что делать |
|----------|-------------------|------------|
| **4xx ошибки** (400, 401, 403, 404) | Это клиентские ошибки — retry не поможет | Показать ошибку пользователю |
| **Не-идемпотентные операции** | POST может создать дубликаты | Использовать idempotency key |
| **Бизнес-логика** (недостаточно денег) | Retry не добавит денег на счёт | Обработать как бизнес-ошибку |
| **Deterministic failure** | Ошибка повторится при любых условиях | Исправить код |

### Какие ошибки можно ретраить

```python
# ✅ МОЖНО ретраить (transient errors)
RETRYABLE_ERRORS = (
    ConnectionError,      # Соединение оборвалось
    TimeoutError,         # Не дождались ответа
    # HTTP статусы:
    # 429 Too Many Requests  — нас rate limit'нули
    # 500 Internal Error     — сервер сглючил
    # 502 Bad Gateway        — прокси не достучался
    # 503 Service Unavailable — сервис перегружен
    # 504 Gateway Timeout    — прокси не дождался
)

# ❌ НЕЛЬЗЯ ретраить (permanent errors)
NON_RETRYABLE_ERRORS = (
    # HTTP статусы:
    # 400 Bad Request        — мы отправили плохие данные
    # 401 Unauthorized       — нужна авторизация
    # 403 Forbidden          — нет прав
    # 404 Not Found          — ресурс не существует
    # 409 Conflict           — конфликт версий
    ValueError,            # Неправильные входные данные
    AuthenticationError,   # Неверные credentials
)
```

---

## 2. Circuit Breaker Pattern (Автоматический предохранитель)

### Аналогия: Электрический автомат в щитке

```
Представь электрический щиток дома:

🏠 Обычная ситуация:
   Автомат ВКЛЮЧЕН → Ток течёт → Всё работает

⚡ Перегрузка (много приборов включили):
   Автомат ВЫКЛЮЧАЕТСЯ → Ток не течёт → Защита от пожара!

🔧 После остывания:
   Можно ВКЛЮЧИТЬ обратно → Проверяем, работает ли

В программировании:
   Автомат = Circuit Breaker
   Ток = Запросы к сервису
   Перегрузка = Много ошибок от сервиса
```

### Зачем нужен Circuit Breaker?

**Проблема без Circuit Breaker:**

```
Сервис B упал. Что делает Сервис A?

Без Circuit Breaker:
A → B (ошибка, ждали 5 сек)
A → B (ошибка, ждали 5 сек)
A → B (ошибка, ждали 5 сек)
...
A тратит ресурсы на бесполезные запросы
A сам начинает тормозить
Пользователи A ждут и уходят
```

**С Circuit Breaker:**

```
A → B (ошибка)
A → B (ошибка)
A → B (ошибка)
A → B (ошибка)
A → B (ошибка)  ← 5-я ошибка

[CIRCUIT ОТКРЫТ]

A → B → СРАЗУ ОШИБКА (не ждём!)
A может вернуть fallback или cached данные
Пользователи получают ответ быстро
```

### Три состояния Circuit Breaker

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CIRCUIT BREAKER: ТРИ СОСТОЯНИЯ                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────────┐                             │
│                         │      🟢 CLOSED      │                             │
│                         │   (Нормальная работа)│                             │
│                         │                     │                             │
│                         │  Все запросы идут    │                             │
│                         │  к реальному сервису│                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│                    5+ ошибок в последние 60 секунд                          │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │       🔴 OPEN       │                             │
│                         │   (Fail Fast режим) │                             │
│                         │                     │                             │
│                         │  Все запросы сразу  │                             │
│                         │  возвращают ошибку  │                             │
│                         │  (без обращения     │                             │
│                         │   к сервису!)       │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│                    Прошло 30 секунд (timeout)                               │
│                                    │                                         │
│                                    ▼                                         │
│                         ┌─────────────────────┐                             │
│                         │     🟡 HALF-OPEN    │                             │
│                         │    (Тестовый режим) │                             │
│                         │                     │                             │
│                         │  Пропускаем ОДИН    │                             │
│                         │  тестовый запрос    │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│               ┌────────────────────┴────────────────────┐                   │
│               │                                         │                   │
│           Успех!                                    Ошибка                  │
│               │                                         │                   │
│               ▼                                         ▼                   │
│        Возврат в CLOSED                         Возврат в OPEN             │
│        (сервис восстановился)                   (ещё не готов)             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Circuit Breaker Implementation (с подробными комментариями)

```python
import asyncio
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Optional
from collections import deque

class CircuitState(Enum):
    """
    Три состояния Circuit Breaker.

    CLOSED = Всё хорошо, пропускаем запросы
    OPEN = Всё плохо, блокируем запросы
    HALF_OPEN = Тестируем, восстановился ли сервис
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """
    Конфигурация Circuit Breaker.

    Как подобрать параметры:

    failure_threshold:
      - Слишком низкий (3) → слишком чувствительный, частые "ложные" открытия
      - Слишком высокий (20) → медленная реакция на реальные проблемы
      - Рекомендация: 5-10

    timeout:
      - Слишком короткий (5s) → circuit будет "моргать" (oscillation)
      - Слишком длинный (5min) → долго не узнаем о восстановлении
      - Рекомендация: 30-60s
    """
    failure_threshold: int = 5      # Сколько ошибок = открыть circuit
    success_threshold: int = 3      # Сколько успехов в half-open = закрыть
    timeout: float = 30.0           # Через сколько секунд попробовать снова
    window_size: int = 10           # Размер окна для подсчёта ошибок


@dataclass
class CircuitBreaker:
    """
    Реализация Circuit Breaker паттерна.

    Использование:
        breaker = CircuitBreaker(CircuitBreakerConfig())
        result = await breaker.call(my_async_function, arg1, arg2)
    """
    config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    state: CircuitState = CircuitState.CLOSED
    failures: deque = field(default_factory=lambda: deque(maxlen=10))
    successes_in_half_open: int = 0
    last_failure_time: Optional[float] = None

    async def call(self, func: Callable, *args, **kwargs):
        """
        Выполнить функцию с защитой Circuit Breaker.

        Логика:
        1. Если OPEN и timeout не прошёл → сразу ошибка
        2. Если OPEN и timeout прошёл → переходим в HALF_OPEN
        3. Если CLOSED или HALF_OPEN → выполняем функцию
        4. В зависимости от результата обновляем состояние
        """

        # === ПРОВЕРКА: Нужно ли переходить из OPEN в HALF_OPEN? ===
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                # Прошло достаточно времени — даём шанс
                self.state = CircuitState.HALF_OPEN
                self.successes_in_half_open = 0
                print("🟡 Circuit → HALF_OPEN (тестируем сервис)")
            else:
                # Ещё рано — сразу возвращаем ошибку (fail fast)
                raise CircuitOpenError(
                    f"🔴 Circuit OPEN! Повторная попытка через "
                    f"{self._time_until_retry():.1f}s"
                )

        # === ВЫПОЛНЕНИЕ ЗАПРОСА ===
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """
        Обработка успешного вызова.

        Если мы в HALF_OPEN:
        - Считаем успехи
        - После N успехов → CLOSED

        Если мы в CLOSED:
        - Ничего не делаем (уже всё хорошо)
        """
        if self.state == CircuitState.HALF_OPEN:
            self.successes_in_half_open += 1

            # Достаточно успехов — сервис восстановился!
            if self.successes_in_half_open >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failures.clear()
                print("🟢 Circuit → CLOSED (сервис восстановился!)")

    def _on_failure(self):
        """
        Обработка неуспешного вызова.

        Если мы в HALF_OPEN:
        - Сразу обратно в OPEN (сервис ещё не готов)

        Если мы в CLOSED:
        - Добавляем ошибку в счётчик
        - Если ошибок >= threshold → OPEN
        """
        current_time = time.time()
        self.failures.append(current_time)
        self.last_failure_time = current_time

        if self.state == CircuitState.HALF_OPEN:
            # Одна ошибка в half-open = сразу обратно в open
            self.state = CircuitState.OPEN
            print("🔴 Circuit → OPEN (тест не пройден)")

        elif self.state == CircuitState.CLOSED:
            # Проверяем, достаточно ли ошибок для открытия
            if len(self.failures) >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"🔴 Circuit → OPEN ({len(self.failures)} ошибок!)")

    def _should_attempt_reset(self) -> bool:
        """Прошло ли достаточно времени для попытки восстановления?"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.config.timeout

    def _time_until_retry(self) -> float:
        """Сколько секунд осталось до попытки восстановления?"""
        if self.last_failure_time is None:
            return 0
        elapsed = time.time() - self.last_failure_time
        return max(0, self.config.timeout - elapsed)


class CircuitOpenError(Exception):
    """Ошибка: Circuit Breaker открыт, запросы не пропускаются."""
    pass


# ✅ Пример использования с декоратором
def circuit_breaker(breaker: CircuitBreaker):
    """Декоратор для автоматического применения Circuit Breaker."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


# Создаём отдельный breaker для каждого внешнего сервиса
payment_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=5,   # После 5 ошибок — открываем
    timeout=30.0           # Через 30 секунд пробуем снова
))

inventory_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=10,  # Inventory менее критичен — порог выше
    timeout=60.0           # Можем ждать дольше
))


@circuit_breaker(payment_breaker)
async def process_payment(amount: float) -> dict:
    """Процессинг платежа с защитой Circuit Breaker."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://payment.api/charge",
            json={"amount": amount},
            timeout=5.0
        )
        return response.json()
```

### Как выбрать параметры Circuit Breaker?

| Параметр | Критичный сервис (платежи) | Некритичный (рекомендации) |
|----------|---------------------------|---------------------------|
| `failure_threshold` | 3-5 | 10-15 |
| `timeout` | 15-30s | 60-120s |
| `success_threshold` | 2-3 | 1 |

**Логика:** Критичные сервисы защищаем агрессивнее (быстрее открываем, дольше держим открытым).

---

## 3. Bulkhead Pattern (Изоляция переборками)

### Аналогия: Корабль с водонепроницаемыми отсеками

```
КОРАБЛЬ БЕЗ ПЕРЕБОРОК (❌)
┌─────────────────────────────────────────────┐
│                    🚢                        │
│     ════════════════════════════════════    │
│     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    │  ← Одно пространство
│     ════════════════════════════════════    │
└─────────────────────────────────────────────┘
         💧 Пробоина
              ↓
         Вода заполняет ВСЁ → Корабль ТОНЕТ


КОРАБЛЬ С ПЕРЕБОРКАМИ (✅)
┌─────────────────────────────────────────────┐
│                    🚢                        │
│     ════║════║════║════║════║════║════      │
│     ░░░░║    ║    ║    ║    ║    ║    ░    │  ← Изолированные отсеки
│     ════║════║════║════║════║════║════      │
└─────────────────────────────────────────────┘
         💧 Пробоина
              ↓
         Вода только в ОДНОМ отсеке → Корабль НА ПЛАВУ

Титаник затонул потому что переборки не доходили до потолка!
```

### Зачем нужен Bulkhead в программировании?

**Проблема: Один медленный сервис "съедает" все ресурсы**

```
БЕЗ BULKHEAD:
┌───────────────────────────────────────────────────────────────┐
│                    Общий пул потоков (20)                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Thread 1-20: все заняты запросами к Payment Service 💀   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  Payment Service тормозит → все потоки висят → Inventory и    │
│  User Service тоже не получают потоков → ВСЁ тормозит!        │
└───────────────────────────────────────────────────────────────┘

С BULKHEAD:
┌───────────────────────────────────────────────────────────────┐
│                   Изолированные пулы                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ Payment Pool (5)│  │ Inventory (10)  │  │ User Pool (5) │  │
│  │ Thread 1-5: 💀  │  │ Thread 1-10: ✅ │  │ Thread 1-5: ✅ │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                │
│  Payment тормозит → только Payment потоки заняты →            │
│  Inventory и User продолжают работать! ✅                      │
└───────────────────────────────────────────────────────────────┘
```

### Типы Bulkhead

| Тип | Что изолируется | Когда использовать |
|-----|-----------------|-------------------|
| **Thread Pool** | Потоки выполнения | Java/JVM приложения |
| **Semaphore** | Количество concurrent запросов | Async приложения (Python, Node.js) |
| **Connection Pool** | Соединения с БД | Защита базы данных |
| **Process/Container** | CPU и память | Kubernetes, Docker |

### Bulkhead Implementation (Semaphore-based)

```python
import asyncio
from dataclasses import dataclass
from typing import Callable

@dataclass
class BulkheadConfig:
    """
    Конфигурация Bulkhead.

    max_concurrent: Максимум одновременных запросов
        - Слишком мало → очередь, пользователи ждут
        - Слишком много → нет защиты
        - Рекомендация: анализировать метрики нагрузки

    max_wait: Сколько ждать в очереди
        - Слишком мало → много отказов при пиках
        - Слишком много → плохой user experience
        - Рекомендация: 1-10 секунд
    """
    max_concurrent: int = 10    # Максимум одновременных запросов
    max_wait: float = 5.0       # Максимум ждать в очереди (секунды)


class Bulkhead:
    """
    Semaphore-based Bulkhead для ограничения concurrent запросов.

    Как работает Semaphore:
    - Есть N "разрешений" (permits)
    - Каждый запрос берёт 1 разрешение
    - Когда разрешений нет — ждём или отказываем
    - После завершения запроса — возвращаем разрешение
    """

    def __init__(self, config: BulkheadConfig):
        self.config = config
        # Semaphore — это "счётчик разрешений"
        # asyncio.Semaphore(10) = 10 разрешений
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.waiting = 0    # Сколько ждут в очереди
        self.active = 0     # Сколько сейчас выполняются

    async def call(self, func: Callable, *args, **kwargs):
        """
        Выполнить функцию с ограничением concurrency.

        Алгоритм:
        1. Пытаемся получить разрешение (acquire)
        2. Если не получили за max_wait → BulkheadFullError
        3. Если получили → выполняем функцию
        4. После завершения → возвращаем разрешение (release)
        """
        self.waiting += 1

        try:
            # Пытаемся получить разрешение с таймаутом
            # wait_for выбросит TimeoutError если не успеем
            acquired = await asyncio.wait_for(
                self.semaphore.acquire(),
                timeout=self.config.max_wait
            )
        except asyncio.TimeoutError:
            # Не дождались разрешения — очередь переполнена
            self.waiting -= 1
            raise BulkheadFullError(
                f"🚫 Bulkhead переполнен: {self.active} активных, "
                f"{self.waiting} в очереди. Попробуйте позже."
            )

        # Получили разрешение — теперь мы "active"
        self.waiting -= 1
        self.active += 1

        try:
            # Выполняем функцию
            return await func(*args, **kwargs)
        finally:
            # ВСЕГДА возвращаем разрешение, даже при ошибке
            self.active -= 1
            self.semaphore.release()

    @property
    def metrics(self) -> dict:
        """Метрики для мониторинга."""
        return {
            "active": self.active,
            "waiting": self.waiting,
            "available": self.config.max_concurrent - self.active,
            "utilization": self.active / self.config.max_concurrent
        }


class BulkheadFullError(Exception):
    """Ошибка: Bulkhead переполнен, новые запросы не принимаются."""
    pass


# ✅ Создаём отдельный bulkhead для каждого сервиса
payment_bulkhead = Bulkhead(BulkheadConfig(
    max_concurrent=5,    # Максимум 5 одновременных платежей
    max_wait=3.0         # Ждём в очереди максимум 3 секунды
))

inventory_bulkhead = Bulkhead(BulkheadConfig(
    max_concurrent=20,   # Inventory может больше
    max_wait=5.0
))

email_bulkhead = Bulkhead(BulkheadConfig(
    max_concurrent=50,   # Email — некритичный, можно больше
    max_wait=10.0
))


async def process_order(order_id: str):
    """
    Обработка заказа с изоляцией каждого внешнего вызова.

    Каждый внешний сервис в своём "отсеке":
    - Если платежи тормозят → inventory не страдает
    - Если email не отправляется → заказ всё равно создаётся
    """

    # Платёж — строго ограничен (критичный)
    payment_result = await payment_bulkhead.call(
        charge_payment, order_id
    )

    # Резервирование — своё ограничение
    inventory_result = await inventory_bulkhead.call(
        reserve_inventory, order_id
    )

    # Email — наименее критичный
    try:
        await email_bulkhead.call(
            send_confirmation_email, order_id
        )
    except BulkheadFullError:
        # Email не критичен — можно отправить позже
        await queue_email_for_later(order_id)

    return {
        "order_id": order_id,
        "payment": payment_result,
        "inventory": inventory_result
    }
```

### Bulkhead vs Rate Limiting — в чём разница?

```
BULKHEAD (защита CALLER — того, кто вызывает)
┌─────────────────────────────────────────────────────────────┐
│ Наше приложение                                              │
│   ┌──────────────────┐                                      │
│   │ "Не более 10      │ → Payment Service (внешний)         │
│   │  одновременных    │                                      │
│   │  запросов"        │                                      │
│   └──────────────────┘                                      │
│   Защита: наши ресурсы не будут исчерпаны                   │
└─────────────────────────────────────────────────────────────┘

RATE LIMITING (защита CALLEE — того, кого вызывают)
┌─────────────────────────────────────────────────────────────┐
│ Внешние клиенты                                             │
│   Client A ─┐                                               │
│   Client B ─┼──→ ┌──────────────────┐ → Наш API            │
│   Client C ─┘    │ "Не более 100    │                      │
│                  │  запросов/сек"   │                      │
│                  └──────────────────┘                      │
│   Защита: наш API не будет перегружен                      │
└─────────────────────────────────────────────────────────────┘

Часто используются ВМЕСТЕ!
```

---

## 4. Timeout Pattern (Ограничение времени ожидания)

### Аналогия: Официант в ресторане

```
БЕЗ TIMEOUT:
Ты заказал еду и ждёшь...
⏰ 10 минут... 20 минут... 30 минут... 1 час...
Ты всё ещё ждёшь. Может, заказ потерялся?
Но ты продолжаешь ждать... вечно.

С TIMEOUT:
Ты заказал еду и засёк время.
⏰ 15 минут — "Если через 5 минут не принесут, спрошу официанта"
⏰ 20 минут — "Извините, мой заказ потерялся?"
Ты НЕ ждёшь вечно. Ты ставишь границу.
```

### Зачем нужен Timeout?

**Без timeout запрос может висеть ВЕЧНО:**

```python
# ❌ ПЛОХО: Может никогда не завершиться
async def bad_fetch(url):
    return await client.get(url)  # Если сервер не отвечает → виснет

# Что происходит:
# 1. Запрос отправлен
# 2. Сервер не отвечает (упал, сеть потерялась)
# 3. Соединение открыто, поток занят
# 4. Других запросов не обрабатываем
# 5. Память утекает
# 6. Приложение умирает
```

### Как выбрать значение Timeout?

```
Слишком КОРОТКИЙ timeout:
├─ Много ложных ошибок (сервис работает, но не успевает ответить)
├─ Больше retry → больше нагрузка
└─ Плохой user experience

Слишком ДЛИННЫЙ timeout:
├─ Долго ждём при реальных проблемах
├─ Ресурсы заняты бесполезно
└─ Плохой user experience

ОПТИМАЛЬНЫЙ timeout:
├─ Анализируем p99 latency сервиса (99% запросов быстрее X)
├─ Добавляем запас 20-50%
└─ timeout = p99 × 1.5
```

**Пример расчёта:**
```
Payment Service:
- p50 (медиана): 100ms
- p95: 300ms
- p99: 500ms
- p99.9: 1000ms

Рекомендуемый timeout: 500ms × 1.5 = 750ms ≈ 1 секунда
```

### Timeout Implementation

```python
import asyncio
from typing import TypeVar, Callable
from functools import wraps

T = TypeVar('T')

class TimeoutConfig:
    def __init__(
        self,
        timeout: float = 5.0,          # Сколько ждать (секунды)
        cancel_on_timeout: bool = True  # Отменять операцию при таймауте?
    ):
        self.timeout = timeout
        self.cancel_on_timeout = cancel_on_timeout


def with_timeout(config: TimeoutConfig):
    """
    Декоратор для автоматического timeout.

    Как работает:
    1. Запускаем функцию
    2. Если за config.timeout секунд не завершилась → TimeoutError
    3. Если cancel_on_timeout=True → отменяем незавершённую задачу
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                # wait_for: выполни функцию, но не дольше timeout секунд
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=config.timeout
                )
            except asyncio.TimeoutError:
                # Превысили timeout — пробрасываем понятную ошибку
                raise TimeoutError(
                    f"⏰ {func.__name__} не ответил за {config.timeout}s"
                )
        return wrapper
    return decorator


# ✅ Правильное использование
@with_timeout(TimeoutConfig(timeout=3.0))
async def fetch_user_data(user_id: str) -> dict:
    """Получить данные пользователя с timeout 3 секунды."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        return response.json()


# ✅ Можно комбинировать с другими паттернами
@retry(RetryConfig(max_attempts=3))
@with_timeout(TimeoutConfig(timeout=2.0))
@circuit_breaker(user_service_breaker)
async def get_user_with_protection(user_id: str) -> dict:
    """
    Полная защита:
    1. Circuit Breaker — защита от cascade failure
    2. Timeout — не ждём вечно
    3. Retry — повторяем при transient failures
    """
    return await user_service.get(user_id)
```

### Проблема: Каскадные Timeouts

```
         Client (timeout=10s)
            │
            ▼
         Service A (timeout=8s)
            │
            ▼
         Service B (timeout=6s)
            │
            ▼
         Service C (timeout=4s)
            │
            ▼
         Database (slow query 5s)

Что происходит:
1. DB отвечает за 5s → C таймаутится (4s)
2. B ретраит → ждёт ещё 6s → таймаутится
3. A ретраит → ждёт ещё 8s → таймаутится
4. Client видит таймаут после 10s

Retry amplification:
- DB получает: 1 + 3 (retry B) + 9 (retry A × retry B) = 13 запросов!
```

**Решение: Retry только на одном уровне**

```python
# ✅ ПРАВИЛЬНО: Retry только на верхнем уровне
@retry(config)  # Retry ЗДЕСЬ
async def api_handler():
    return await service_a.call()  # Без retry

async def service_a_call():
    return await service_b.call()  # Без retry

async def service_b_call():
    return await database.query()  # Без retry
```

---

## 5. Fallback Pattern (Резервное поведение)

### Аналогия: План Б

```
Ты собираешься на работу:

План А: Поехать на машине
  ↓ (машина не заводится)
План Б: Вызвать такси
  ↓ (такси нет в районе)
План В: Поехать на автобусе
  ↓ (автобус отменён)
План Г: Работать из дома (degraded mode)

БЕЗ fallback: Машина не завелась → ПАНИКА → не работаешь
С fallback: Машина не завелась → такси → автобус → из дома
```

### Виды Fallback

| Вид | Описание | Пример |
|-----|----------|--------|
| **Cache fallback** | Вернуть устаревшие данные из кэша | Курс валюты из кэша вместо API |
| **Default value** | Вернуть значение по умолчанию | Пустой список рекомендаций |
| **Degraded service** | Урезанная функциональность | Товар без отзывов |
| **Static response** | Заготовленный ответ | "Сервис временно недоступен" |
| **Alternative service** | Другой провайдер | Запасной платёжный шлюз |

### Fallback Implementation

```python
from typing import TypeVar, Callable, Optional, Union
from functools import wraps

T = TypeVar('T')

class FallbackConfig:
    """
    Конфигурация fallback-поведения.

    fallback_value: Статическое значение по умолчанию
    fallback_func: Функция для получения fallback (может быть async)
    exceptions: Какие ошибки триггерят fallback
    log_fallback: Логировать использование fallback
    """
    def __init__(
        self,
        fallback_value: Optional[T] = None,
        fallback_func: Optional[Callable[..., T]] = None,
        exceptions: tuple = (Exception,),
        log_fallback: bool = True
    ):
        self.fallback_value = fallback_value
        self.fallback_func = fallback_func
        self.exceptions = exceptions
        self.log_fallback = log_fallback


def with_fallback(config: FallbackConfig):
    """
    Декоратор для автоматического fallback.

    Приоритет:
    1. Если есть fallback_func → вызываем её
    2. Иначе → возвращаем fallback_value
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except config.exceptions as e:
                if config.log_fallback:
                    print(f"⚠️ {func.__name__} failed: {e}. Using fallback.")

                if config.fallback_func:
                    # Вызываем fallback функцию с теми же аргументами
                    return await config.fallback_func(*args, **kwargs)
                return config.fallback_value
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ═══════════════════════════════════════════════════════════════════════════

# === Пример 1: Fallback на кэш ===

async def get_cached_user(user_id: str) -> dict:
    """Fallback: получить пользователя из кэша."""
    cached = await cache.get(f"user:{user_id}")
    if cached:
        return {**cached, "_source": "cache", "_stale": True}
    # Если в кэше нет — возвращаем минимальные данные
    return {"id": user_id, "name": "Unknown", "_source": "default"}


@with_fallback(FallbackConfig(fallback_func=get_cached_user))
async def get_user(user_id: str) -> dict:
    """
    Получить пользователя.
    При ошибке — вернуть из кэша (устаревшие данные лучше, чем ничего).
    """
    user = await user_service.get(user_id)
    # Сохраняем в кэш для будущих fallback
    await cache.set(f"user:{user_id}", user, ttl=3600)
    return user


# === Пример 2: Fallback на пустой результат ===

@with_fallback(FallbackConfig(fallback_value=[]))
async def get_recommendations(user_id: str) -> list:
    """
    Получить рекомендации.
    При ошибке — пустой список (лучше ничего, чем ошибка на странице).
    """
    return await recommendation_service.get(user_id)


# === Пример 3: Graceful Degradation ===

class ProductService:
    """
    Сервис товаров с graceful degradation.

    Уровни деградации:
    1. Full: товар + отзывы + рейтинг + рекомендации
    2. Basic: товар + отзывы + рейтинг
    3. Minimal: только товар
    """

    async def get_product(self, product_id: str) -> dict:
        """Получить товар с максимально возможной полнотой данных."""

        # Базовые данные — обязательны (без них нет смысла)
        product = await self._get_basic_product(product_id)

        # Обогащаем данными, если сервисы доступны
        product["reviews"] = await self._safe_get_reviews(product_id)
        product["rating"] = await self._safe_get_rating(product_id)
        product["recommendations"] = await self._safe_get_recommendations(product_id)

        # Помечаем, что есть degraded
        if any(v is None for v in [product["reviews"], product["rating"]]):
            product["_degraded"] = True

        return product

    async def _get_basic_product(self, product_id: str) -> dict:
        """Получить базовые данные товара (без fallback — это критично)."""
        return await self.db.get(product_id)

    async def _safe_get_reviews(self, product_id: str) -> Optional[list]:
        """Безопасно получить отзывы (с fallback на None)."""
        try:
            return await review_service.get(product_id)
        except Exception as e:
            print(f"Reviews unavailable: {e}")
            return None  # Покажем товар без отзывов

    async def _safe_get_rating(self, product_id: str) -> Optional[float]:
        """Безопасно получить рейтинг."""
        try:
            return await rating_service.get(product_id)
        except Exception:
            return None

    async def _safe_get_recommendations(self, product_id: str) -> list:
        """Безопасно получить рекомендации (fallback на пустой список)."""
        try:
            return await recommendation_service.get(product_id)
        except Exception:
            return []  # Пустой список — не показываем секцию
```

### Trade-offs Fallback (Когда НЕ использовать)

| Ситуация | Почему fallback опасен | Что делать |
|----------|----------------------|------------|
| **Финансовые операции** | Fallback может привести к неконсистентности | Fail fast, показать ошибку |
| **Без тестирования** | Fallback path не протестирован → может упасть | Тестировать fallback как основной путь |
| **Stale data критичны** | Устаревшие данные могут навредить | Не использовать cache fallback |
| **Inconsistent state** | Частичный fallback создаёт противоречия | Всё или ничего (atomicity) |

**Правило:** Fallback path должен быть **проще** основного, иначе он тоже сломается!

---

## 6. Combined Resilience Stack (Всё вместе)

### Порядок слоёв (важно!)

```
Запрос входит СВЕРХУ, проходит через каждый слой:

    ┌────────────────────┐
    │   BULKHEAD         │ ← 1. Ограничивает количество запросов
    │   (max 10 concurrent)│    Защита: не исчерпать ресурсы
    └──────────┬─────────┘
               │
    ┌──────────▼─────────┐
    │  CIRCUIT BREAKER   │ ← 2. Проверяет, работает ли сервис
    │  (fail fast если   │    Защита: не бить мёртвый сервис
    │   сервис лежит)    │
    └──────────┬─────────┘
               │
    ┌──────────▼─────────┐
    │      RETRY         │ ← 3. Повторяет при transient errors
    │  (3 attempts,      │    Защита: временные сбои
    │   exponential)     │
    └──────────┬─────────┘
               │
    ┌──────────▼─────────┐
    │     TIMEOUT        │ ← 4. Ограничивает время ожидания
    │   (max 5s)         │    Защита: не виснуть вечно
    └──────────┬─────────┘
               │
    ┌──────────▼─────────┐
    │   EXTERNAL CALL    │ ← 5. Реальный вызов сервиса
    └────────────────────┘

Если любой слой ошибся → FALLBACK
```

### Complete Implementation

```python
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar

T = TypeVar('T')

@dataclass
class ResilienceConfig:
    """
    Полная конфигурация resilience stack.

    Рекомендуемые значения для разных сценариев:

    КРИТИЧНЫЙ СЕРВИС (платежи):
        timeout=3.0, retry_attempts=2, circuit_failure=3

    ВАЖНЫЙ СЕРВИС (inventory):
        timeout=5.0, retry_attempts=3, circuit_failure=5

    НЕКРИТИЧНЫЙ СЕРВИС (analytics):
        timeout=10.0, retry_attempts=5, circuit_failure=10
    """
    # Timeout настройки
    timeout: float = 5.0

    # Retry настройки
    retry_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0

    # Circuit Breaker настройки
    circuit_failure_threshold: int = 5
    circuit_timeout: float = 30.0

    # Bulkhead настройки
    bulkhead_max_concurrent: int = 10
    bulkhead_max_wait: float = 5.0


class ResilientClient:
    """
    Клиент с полным resilience stack.

    Использование:
        client = ResilientClient(ResilienceConfig())

        result = await client.call(
            external_api.fetch_data,
            "param1",
            fallback=get_cached_data
        )
    """

    def __init__(self, config: ResilienceConfig, name: str = "default"):
        self.config = config
        self.name = name

        # Создаём компоненты
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=config.circuit_failure_threshold,
            timeout=config.circuit_timeout
        ))
        self.bulkhead = Bulkhead(BulkheadConfig(
            max_concurrent=config.bulkhead_max_concurrent,
            max_wait=config.bulkhead_max_wait
        ))

        # Статистика
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "fallback_calls": 0,
            "circuit_open_rejections": 0,
            "bulkhead_rejections": 0
        }

    async def call(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> T:
        """
        Выполнить вызов с полной защитой.

        Слои защиты (в порядке применения):
        1. Bulkhead — ограничение concurrent
        2. Circuit Breaker — защита от cascade
        3. Retry — повтор при transient
        4. Timeout — ограничение ожидания

        Если всё fail → fallback (если есть)
        """
        self.stats["total_calls"] += 1

        try:
            # === СЛОЙ 1: BULKHEAD ===
            result = await self.bulkhead.call(
                self._call_with_circuit_breaker,
                func, args, kwargs
            )
            self.stats["successful_calls"] += 1
            return result

        except BulkheadFullError:
            self.stats["bulkhead_rejections"] += 1
            self.stats["failed_calls"] += 1
            return await self._handle_failure(fallback, args, kwargs)

        except CircuitOpenError:
            self.stats["circuit_open_rejections"] += 1
            self.stats["failed_calls"] += 1
            return await self._handle_failure(fallback, args, kwargs)

        except Exception as e:
            self.stats["failed_calls"] += 1
            return await self._handle_failure(fallback, args, kwargs, e)

    async def _call_with_circuit_breaker(self, func, args, kwargs):
        """Слой 2: Circuit Breaker."""
        return await self.circuit_breaker.call(
            self._call_with_retry,
            func, args, kwargs
        )

    async def _call_with_retry(self, func, args, kwargs):
        """Слой 3: Retry с exponential backoff."""
        last_exception = None

        for attempt in range(self.config.retry_attempts):
            try:
                # === СЛОЙ 4: TIMEOUT ===
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            except (asyncio.TimeoutError, ConnectionError) as e:
                last_exception = e
                if attempt < self.config.retry_attempts - 1:
                    # Exponential backoff с jitter
                    delay = min(
                        self.config.retry_base_delay * (2 ** attempt),
                        self.config.retry_max_delay
                    )
                    delay = random.uniform(0, delay)  # Full jitter
                    await asyncio.sleep(delay)

        raise last_exception

    async def _handle_failure(
        self,
        fallback: Optional[Callable],
        args: tuple,
        kwargs: dict,
        error: Optional[Exception] = None
    ) -> T:
        """Обработка ошибки: fallback или re-raise."""
        if fallback:
            self.stats["fallback_calls"] += 1
            return await fallback(*args, **kwargs)
        if error:
            raise error
        raise Exception(f"Call to {self.name} failed and no fallback provided")

    @property
    def health(self) -> dict:
        """Статус здоровья клиента."""
        return {
            "name": self.name,
            "circuit_state": self.circuit_breaker.state.value,
            "bulkhead_utilization": self.bulkhead.metrics["utilization"],
            "success_rate": (
                self.stats["successful_calls"] / self.stats["total_calls"]
                if self.stats["total_calls"] > 0 else 1.0
            ),
            "stats": self.stats
        }


# ═══════════════════════════════════════════════════════════════════════════
# ИСПОЛЬЗОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════

# Создаём клиенты для разных сервисов
payment_client = ResilientClient(
    ResilienceConfig(
        timeout=3.0,
        retry_attempts=2,
        circuit_failure_threshold=3,
        bulkhead_max_concurrent=5
    ),
    name="payment"
)

inventory_client = ResilientClient(
    ResilienceConfig(
        timeout=5.0,
        retry_attempts=3,
        circuit_failure_threshold=5,
        bulkhead_max_concurrent=20
    ),
    name="inventory"
)

# Использование
async def process_order(order: Order):
    # Платёж с fallback
    payment = await payment_client.call(
        payment_service.charge,
        order.amount,
        fallback=lambda amount: {"status": "pending", "retry_later": True}
    )

    # Inventory с fallback
    inventory = await inventory_client.call(
        inventory_service.reserve,
        order.items,
        fallback=lambda items: {"status": "pending", "backorder": True}
    )

    return {"payment": payment, "inventory": inventory}


# Мониторинг
async def health_check():
    return {
        "payment": payment_client.health,
        "inventory": inventory_client.health
    }
```

---

## Decision Tree: Какой паттерн использовать?

```
                           Проблема?
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    Временные ошибки?    Сервис лежит?    Ресурсы исчерпаны?
              │               │               │
              ▼               ▼               ▼
          ┌───────┐    ┌──────────────┐   ┌──────────┐
          │ RETRY │    │CIRCUIT BREAKER│   │ BULKHEAD │
          └───┬───┘    └──────┬───────┘   └────┬─────┘
              │               │                │
              │               │                │
     Retry помогает?   Есть fallback?    Есть очередь?
              │               │                │
        Да → ✅        Да → Fallback     Да → Queue
        Нет → ↓        Нет → Fail fast   Нет → Reject
              │
              ▼
       Постоянная ошибка?
              │
        Да → CIRCUIT BREAKER
        Нет → Продолжать retry
```

### Шпаргалка: Когда что применять

| Ситуация | Паттерн(ы) |
|----------|-----------|
| Сетевые сбои, таймауты | **Retry + Timeout** |
| Сервис часто падает | **Circuit Breaker + Fallback** |
| Много клиентов к одному сервису | **Bulkhead** |
| Нужны данные, но можно устаревшие | **Fallback (cache)** |
| Критичная операция (платёж) | **Timeout + Retry (идемпотентно)** |
| Длинная цепочка вызовов | **Timeout на каждом + Retry только наверху** |
| Пиковые нагрузки | **Bulkhead + Rate Limiting** |

---

## Netflix Chaos Engineering (Бонус)

Netflix доказал работоспособность resilience patterns через **Chaos Engineering** — намеренное внесение сбоев в production.

### Simian Army (Армия обезьян)

| Инструмент | Что делает | Зачем |
|------------|-----------|-------|
| **Chaos Monkey** | Выключает случайные инстансы | Проверка: переживём ли потерю сервера? |
| **Chaos Gorilla** | Выключает целый AWS AZ | Проверка: переживём ли потерю дата-центра? |
| **Latency Monkey** | Добавляет задержки | Проверка: работают ли timeouts? |
| **Chaos Kong** | Выключает целый регион | Проверка: работает ли DR? |

**Результат:** 21 апреля 2011 — большой сбой AWS. Netflix продолжил работать, остальные легли.

---

## Типичные ошибки

| Ошибка | Почему плохо | Как правильно |
|--------|-------------|---------------|
| Retry без backoff | Thundering herd → сервис падает ещё сильнее | Exponential backoff + jitter |
| Retry non-idempotent | Дубликаты платежей/заказов | Idempotency key или не ретраить |
| Timeout без fallback | Ошибка вместо degraded experience | Всегда иметь fallback для UX-критичных операций |
| Одинаковые настройки для всех | Критичные сервисы не защищены | Разные конфиги для разных сервисов |
| Retry на всех уровнях | Retry amplification (1 запрос → 100) | Retry только на одном уровне |
| Fallback сложнее primary | Fallback тоже падает | Fallback должен быть проще |
| Не тестировать failure paths | Первый сбой = первый тест | Chaos Engineering, integration tests |

---

## Чеклист внедрения

### Минимальный набор (MVP)
- [ ] Timeout на ВСЕХ внешних вызовах
- [ ] Retry с exponential backoff для transient errors
- [ ] Логирование всех ошибок

### Рекомендуемый набор
- [ ] Circuit Breaker для каждого внешнего сервиса
- [ ] Bulkhead для изоляции критичных сервисов
- [ ] Fallback для UX-критичных операций
- [ ] Метрики: latency, error rate, circuit state
- [ ] Алерты на circuit open

### Продвинутый набор
- [ ] Adaptive timeout (на основе p99 latency)
- [ ] Chaos Engineering в staging
- [ ] Distributed tracing
- [ ] Автоматическое масштабирование на основе bulkhead utilization

---

## Связи

- [[architecture-overview]] — обзор архитектуры
- [[architecture-distributed-systems]] — распределённые системы
- [[architecture-rate-limiting]] — rate limiting (защита callee)
- [[observability]] — мониторинг и алерты
- [[caching-strategies]] — кэширование для fallback

---

## Источники

### Теоретические основы

- **Nygard, M.T. (2007). "Release It! Design and Deploy Production-Ready Software." Pragmatic Bookshelf.** — Первое системное описание Circuit Breaker pattern для software. Введение в resilience engineering для разработчиков
- **Metcalfe, R.M. & Boggs, D.R. (1976). "Ethernet: Distributed Packet Switching for Local Computer Networks." CACM.** — Оригинальное описание exponential backoff для разрешения коллизий в Ethernet
- **Netflix (2014). "Principles of Chaos Engineering."** — Формализация дисциплины chaos engineering: steady state hypothesis, blast radius minimization, run in production

### Практические руководства

| # | Источник | Тип | Ключевой вклад |
|---|----------|-----|----------------|
| 1 | [Netflix Hystrix GitHub](https://github.com/Netflix/Hystrix) | Official | Оригинальная реализация Circuit Breaker |
| 2 | [Resilience4j Docs](https://resilience4j.readme.io/) | Official | Современная Java библиотека |
| 3 | [AWS Builders Library: Timeouts & Retries](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) | Official | Backoff, jitter, best practices |
| 4 | [Microsoft: Bulkhead Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead) | Official | Детальное описание Bulkhead |
| 5 | [Martin Fowler: Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html) | Blog | Классическое описание паттерна |
| 6 | [Netflix: How Netflix Embraces Failure](https://www.usenix.org/conference/lisa13/how-netflix-embraces-failure-improve-resilience-maximize-availability) | Conference | Chaos Engineering история |

---

*Проверено: 2026-01-09. Обновлено с исследованием лучших практик 2024-2025.*

---

## Проверь себя

> [!question]- Сервис A вызывает сервис B (timeout 5s, 3 retry), а B вызывает сервис C (timeout 3s, 3 retry). При сбое C — сколько запросов получит C и почему retry на нескольких уровнях опасен?
> C получит до 9 запросов (3 retry от B × 3 retry от A) — это retry amplification. Каждый retry от A запускает полную цепочку retry в B, что экспоненциально увеличивает нагрузку на уже проблемный сервис. Правильный подход — retry только на одном уровне (обычно на самом верхнем), а остальные уровни используют timeout + fail fast.

> [!question]- Почему Circuit Breaker в состоянии HALF-OPEN пропускает только один тестовый запрос, а не возвращается сразу в CLOSED после первого таймаута?
> Потому что сервис может быть частично восстановлен — обрабатывать единичные запросы, но не выдерживать полную нагрузку. HALF-OPEN играет роль "канарейки": пропуская ограниченный трафик, мы проверяем стабильность без риска повторного каскадного сбоя. Требование нескольких успехов подряд (success_threshold) даёт статистическую уверенность, что сервис действительно готов к полному трафику.

> [!question]- Команда решила добавить cache fallback для платёжного сервиса: при сбое возвращать "успешный платёж" из кэша. Оцените это решение — какие принципы нарушены и какой fallback был бы уместен?
> Это опасное решение. Кэшированный "успешный платёж" — это ложь: деньги не списались, но система считает, что списались. Нарушены принципы: (1) fallback должен быть проще primary, а не создавать inconsistent state; (2) финансовые операции требуют fail fast, а не degraded mode. Правильный fallback: вернуть `{"status": "pending", "retry_later": True}` — честно сообщить о проблеме и поставить заказ в очередь для повторной обработки.

> [!question]- Как Bulkhead pattern связан с концепцией изоляции процессов в операционных системах, и в чём фундаментальное сходство между переборками на корабле, address space isolation и Bulkhead в микросервисах?
> Во всех трёх случаях работает один принцип — изоляция fault domain. На корабле переборки ограничивают распространение воды одним отсеком. В ОС каждый процесс имеет изолированное адресное пространство, и crash одного процесса не уронит другие. В микросервисах Bulkhead выделяет каждому внешнему вызову отдельный пул ресурсов, предотвращая ситуацию, когда один медленный сервис "съедает" все потоки/соединения. Фундаментально это задача partitioning ресурсов для ограничения blast radius сбоя.

---

## Ключевые карточки

Какую проблему решает exponential backoff с jitter при retry?
?
Предотвращает thundering herd — ситуацию, когда все клиенты одновременно повторяют запросы к упавшему сервису. Экспоненциально растущая задержка снижает частоту retry, а jitter (случайное отклонение) распределяет запросы во времени, давая сервису шанс восстановиться.

Перечисли три состояния Circuit Breaker и условия перехода между ними.
?
CLOSED (норма) → OPEN при достижении failure_threshold ошибок. OPEN (блокировка) → HALF-OPEN после истечения timeout. HALF-OPEN (тест) → CLOSED при success_threshold успешных запросов, или обратно в OPEN при первой ошибке.

Чем Bulkhead отличается от Rate Limiting по цели защиты?
?
Bulkhead защищает caller (вызывающую сторону) — ограничивает, сколько своих ресурсов выделить на вызов внешнего сервиса. Rate Limiting защищает callee (вызываемую сторону) — ограничивает, сколько запросов принимать от клиентов. Часто используются вместе.

Как правильно выбрать значение timeout для вызова внешнего сервиса?
?
Измерить p99 latency сервиса (время, за которое выполняются 99% запросов) и добавить запас 20-50%. Формула: timeout = p99 x 1.5. Слишком короткий timeout вызовет ложные ошибки, слишком длинный — бесполезное ожидание при реальных сбоях.

Почему нельзя делать retry для не-идемпотентных операций (например, POST-запросов)?
?
При retry не-идемпотентной операции запрос может выполниться дважды: первый запрос дошёл до сервера, но ответ потерялся по сети, и клиент делает retry, создавая дубликат (двойной платёж, двойной заказ). Решение — использовать idempotency key или вообще не ретраить такие операции.

В каком порядке располагаются слои resilience stack и почему Bulkhead идёт первым?
?
Порядок: Bulkhead → Circuit Breaker → Retry → Timeout → External Call. Bulkhead идёт первым, потому что он должен ограничить количество одновременных запросов ещё до проверки состояния circuit и до retry-логики, иначе retry-попытки будут потреблять ресурсы из общего пула и одна медленная зависимость "съест" все потоки.

Какие HTTP-статусы можно ретраить, а какие нельзя?
?
Можно: 429 (Too Many Requests), 500, 502, 503, 504 — серверные и транзиентные ошибки. Нельзя: 400, 401, 403, 404, 409 — клиентские ошибки, где повторный запрос с теми же данными даст тот же результат. Ретраить нужно только transient failures, которые могут исправиться сами.

Что такое retry amplification и как его предотвратить?
?
Retry amplification — экспоненциальный рост запросов при retry на нескольких уровнях цепочки вызовов. Например, 3 retry на 3 уровнях = 27 запросов к конечному сервису. Предотвращение: retry только на одном уровне (обычно самом верхнем), остальные уровни используют timeout + fail fast.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[architecture-rate-limiting]] | Rate Limiting защищает callee, дополняя Bulkhead, который защищает caller |
| Глубже в теорию | [[architecture-distributed-systems]] | Понять CAP-теорему и фундаментальные проблемы, которые решают resilience patterns |
| Практика | [[event-driven-architecture]] | Асинхронная архитектура как альтернатива синхронным retry — очереди вместо повторных вызовов |
| Мониторинг | [[observability]] | Без метрик и алертов невозможно узнать, что circuit открыт или bulkhead заполнен |
| Кэширование | [[caching-strategies]] | Стратегии кэширования для реализации эффективного cache fallback |
| Обработка ошибок | [[error-handling]] | Кросс-доменная связь: паттерны обработки ошибок на уровне кода, дополняющие архитектурные resilience patterns |
| Обзор раздела | [[architecture-overview]] | Вернуться к общей карте архитектурных решений |

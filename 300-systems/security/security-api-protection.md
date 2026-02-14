---
title: "API Protection: rate limiting, input validation, API keys"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/security
  - api
  - rate-limiting
  - validation
  - type/concept
  - level/intermediate
related:
  - "[[security-overview]]"
  - "[[authentication-authorization]]"
  - "[[api-design]]"
  - "[[auth-api-service-patterns]]"
prerequisites:
  - "[[authentication-authorization]]"
  - "[[security-fundamentals]]"
reading_time: 7
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# API Protection: rate limiting, input validation, API keys

> API — главная точка входа для атакующих. Каждый endpoint должен быть защищён: аутентификация, авторизация, rate limiting, валидация.

---

## TL;DR

- **Rate Limiting** — защита от DDoS и abuse
- **Input Validation** — никогда не доверяй входным данным
- **API Keys** — идентификация клиента, не замена auth
- **Output Encoding** — предотвращение XSS
- **HTTPS only** — всегда, без исключений

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Rate Limiting** | Ограничение количества запросов |
| **Throttling** | Замедление запросов вместо reject |
| **API Key** | Идентификатор клиента/приложения |
| **Token** | Credential для аутентификации (JWT, OAuth) |
| **Input Validation** | Проверка входных данных |
| **Sanitization** | Очистка данных от опасных символов |
| **WAF** | Web Application Firewall |
| **CORS** | Cross-Origin Resource Sharing |

---

## Rate Limiting

```
┌─────────────────────────────────────────────────────────────────┐
│                    RATE LIMITING                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  АЛГОРИТМЫ:                                                    │
│                                                                 │
│  1. FIXED WINDOW                                               │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ Window: 1 minute                                    │    │
│     │ Limit: 100 requests                                 │    │
│     │                                                     │    │
│     │ 12:00:00 ─────────────────────────── 12:01:00      │    │
│     │ [══════════════════════════════════]                │    │
│     │          100 requests allowed                       │    │
│     │                                                     │    │
│     │ ⚠️ Burst at window edge (100+100 за 2 секунды)     │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│  2. SLIDING WINDOW                                             │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ Окно "скользит" с каждым запросом                  │    │
│     │ Более плавное распределение                        │    │
│     │ ✅ Нет burst на границе                             │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│  3. TOKEN BUCKET                                               │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ Bucket: 100 tokens                                  │    │
│     │ Refill: 10 tokens/second                           │    │
│     │                                                     │    │
│     │ Запрос "тратит" token                              │    │
│     │ Tokens накапливаются до limit                      │    │
│     │ ✅ Позволяет burst, но ограничивает sustained      │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│  4. LEAKY BUCKET                                               │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ Requests → Queue → Process at fixed rate           │    │
│     │ ✅ Smooths traffic                                  │    │
│     │ ⚠️ Добавляет latency                               │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Реализация с Redis

```python
import redis
import time

redis_client = redis.Redis()

def is_rate_limited(user_id: str, limit: int = 100, window: int = 60) -> bool:
    """
    Fixed window rate limiting
    """
    key = f"ratelimit:{user_id}:{int(time.time() / window)}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window)
    return current > limit

def token_bucket(user_id: str, tokens: int = 100, refill_rate: float = 10) -> bool:
    """
    Token bucket algorithm
    """
    key = f"bucket:{user_id}"
    now = time.time()

    pipe = redis_client.pipeline()
    pipe.hgetall(key)
    data = pipe.execute()[0]

    if not data:
        # Initialize bucket
        redis_client.hset(key, mapping={'tokens': tokens - 1, 'last': now})
        return False

    last_time = float(data.get(b'last', now))
    current_tokens = float(data.get(b'tokens', tokens))

    # Refill tokens
    elapsed = now - last_time
    current_tokens = min(tokens, current_tokens + elapsed * refill_rate)

    if current_tokens < 1:
        return True  # Rate limited

    # Consume token
    redis_client.hset(key, mapping={'tokens': current_tokens - 1, 'last': now})
    return False
```

### Rate Limit Headers

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_id = get_user_id(request)
    remaining = get_remaining_requests(user_id)

    if remaining <= 0:
        return JSONResponse(
            status_code=429,
            content={"error": "Too Many Requests"},
            headers={
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(get_reset_time()),
                "Retry-After": "60"
            }
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
    return response
```

---

## Input Validation

```
┌─────────────────────────────────────────────────────────────────┐
│                  INPUT VALIDATION                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  НИКОГДА НЕ ДОВЕРЯЙ:                                           │
│  • Query parameters                                            │
│  • Request body                                                │
│  • Headers                                                     │
│  • Cookies                                                     │
│  • File uploads                                                │
│  • Path parameters                                             │
│                                                                 │
│  VALIDATE:                                                      │
│  • Type (string, int, email, UUID)                            │
│  • Length (min/max)                                           │
│  • Format (regex, enum)                                       │
│  • Range (min/max value)                                      │
│  • Required vs optional                                       │
│  • Business rules                                             │
│                                                                 │
│  SANITIZE:                                                      │
│  • Remove/escape HTML tags                                    │
│  • Normalize Unicode                                          │
│  • Trim whitespace                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Pydantic Validation

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
import re

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(
        min_length=3,
        max_length=30,
        regex=r'^[a-zA-Z0-9_]+$'
    )
    password: str = Field(min_length=8, max_length=128)
    age: Optional[int] = Field(ge=13, le=150)

    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Must contain uppercase')
        if not re.search(r'[a-z]', v):
            raise ValueError('Must contain lowercase')
        if not re.search(r'\d', v):
            raise ValueError('Must contain digit')
        return v

    @validator('username')
    def no_reserved_names(cls, v):
        reserved = ['admin', 'root', 'system']
        if v.lower() in reserved:
            raise ValueError('Reserved username')
        return v

# FastAPI автоматически валидирует
@app.post("/users")
async def create_user(user: CreateUserRequest):
    # user уже валидирован
    pass
```

### SQL Injection Prevention

```python
# ❌ НИКОГДА ТАК
query = f"SELECT * FROM users WHERE id = {user_id}"

# ❌ Конкатенация тоже опасна
query = "SELECT * FROM users WHERE id = " + user_id

# ✅ Parameterized queries
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)

# ✅ ORM (SQLAlchemy)
user = session.query(User).filter(User.id == user_id).first()

# ✅ Prepared statements
stmt = select(users).where(users.c.id == bindparam('user_id'))
result = connection.execute(stmt, {'user_id': user_id})
```

---

## API Keys vs Tokens

```
┌─────────────────────────────────────────────────────────────────┐
│               API KEYS vs AUTH TOKENS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  API KEY                          AUTH TOKEN (JWT/OAuth)        │
│  ────────                         ──────────────────────        │
│  • Идентификация приложения       • Аутентификация пользователя │
│  • Долгоживущий                   • Короткоживущий (hours/days) │
│  • Для rate limiting              • Для authorization           │
│  • Не содержит identity           • Содержит claims/scopes      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Когда что использовать:                               │   │
│  │                                                         │   │
│  │  Публичный API (weather, maps):                        │   │
│  │  → API Key для идентификации + rate limiting           │   │
│  │                                                         │   │
│  │  User-facing API (login, profile):                     │   │
│  │  → OAuth/JWT для аутентификации                        │   │
│  │                                                         │   │
│  │  Комбинация:                                           │   │
│  │  → API Key (приложение) + JWT (пользователь)           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  API Key передача:                                             │
│  ✅ Header: X-API-Key: abc123                                   │
│  ⚠️ Query: ?api_key=abc123 (может попасть в логи)              │
│  ❌ Body: не стандартно                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## CORS (Cross-Origin Resource Sharing)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ❌ НИКОГДА в production
# app.add_middleware(CORSMiddleware, allow_origins=["*"])

# ✅ Whitelist origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://admin.myapp.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=86400  # Cache preflight for 24h
)
```

---

## Security Checklist

```
□ HTTPS only (no HTTP)
□ Rate limiting on all endpoints
□ Input validation (type, length, format)
□ Parameterized queries (no SQL injection)
□ Output encoding (no XSS)
□ Authentication on protected endpoints
□ Authorization checks (not just auth)
□ CORS configured properly
□ Security headers set
□ Error messages don't leak info
□ Logging (but not sensitive data)
□ API versioning
```

---

## Связи

- [[security-overview]] — карта раздела
- [[authentication-authorization]] — AuthN/AuthZ
- [[api-design]] — проектирование API
- [[web-security-owasp]] — OWASP vulnerabilities

---

## Источники

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Rate Limiting Algorithms](https://konghq.com/blog/how-to-design-a-scalable-rate-limiting-algorithm)
- [CORS in 100 seconds](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

*Проверено: 2025-12-22*

---

## Проверь себя

> [!question]- Почему Token Bucket лучше Fixed Window для публичного API с неравномерной нагрузкой?
> Fixed Window допускает burst на границе двух окон — за 2 секунды вокруг границы клиент может отправить 2x лимита запросов. Token Bucket позволяет контролируемый burst (пока в "ведре" есть токены), но ограничивает sustained rate через refill. Это даёт легитимным клиентам гибкость при кратковременных всплесках, одновременно защищая backend от длительной перегрузки.

> [!question]- Приложение использует Pydantic-валидацию на уровне API. Почему этого недостаточно для защиты от SQL injection, и какой дополнительный слой необходим?
> Pydantic проверяет тип, формат и длину данных, но не понимает контекст SQL. Строка, прошедшая валидацию (например, корректный username `"admin'--"`), всё равно может содержать SQL-инъекцию. Необходим второй слой — parameterized queries или ORM, которые изолируют данные от SQL-синтаксиса на уровне драйвера базы данных.

> [!question]- Сервис использует API Key для идентификации мобильного приложения и JWT для аутентификации пользователя. Проанализируйте: если злоумышленник извлёк API Key из APK, какие вектора атаки открываются и как ограничить ущерб?
> API Key из APK позволяет: обход rate limiting для конкретного приложения, имитацию легитимного клиента, перебор паролей. Для ограничения ущерба: привязать API Key к fingerprint устройства, ввести per-user rate limiting (не только per-key), добавить certificate pinning, использовать app attestation (Play Integrity / App Attest), и мониторить аномальные паттерны использования ключа.

> [!question]- Почему передача API Key через query parameter `?api_key=abc123` опасна, даже если соединение защищено через HTTPS?
> HTTPS шифрует трафик в transit, но query parameters попадают в: серверные access-логи, логи прокси и CDN, историю браузера, HTTP Referer-заголовок при переходе на другой сайт, а также могут кешироваться промежуточными узлами. Передача через заголовок `X-API-Key` избегает всех этих утечек, потому что заголовки не логируются по умолчанию и не попадают в URL.

---

## Ключевые карточки

Какие четыре алгоритма rate limiting существуют и в чём их главное отличие?
?
Fixed Window (простой, burst на границе), Sliding Window (плавный, без burst), Token Bucket (позволяет burst, ограничивает sustained rate), Leaky Bucket (сглаживает трафик, добавляет latency).

Чем API Key отличается от JWT-токена по назначению?
?
API Key идентифицирует приложение-клиента (долгоживущий, для rate limiting). JWT аутентифицирует пользователя (короткоживущий, содержит claims и scopes для авторизации).

Какой единственный надёжный способ предотвратить SQL injection?
?
Parameterized queries (bind parameters) или ORM. Данные передаются отдельно от SQL-синтаксиса, и драйвер БД гарантирует, что пользовательский ввод не интерпретируется как SQL-код.

Какие HTTP-заголовки должен возвращать сервер при rate limiting?
?
`X-RateLimit-Limit` (максимум запросов), `X-RateLimit-Remaining` (оставшиеся запросы), `X-RateLimit-Reset` (время сброса), `Retry-After` (когда повторить). Статус ответа — 429 Too Many Requests.

Почему CORS с `allow_origins=["*"]` опасен в production?
?
Любой сайт может делать запросы к API и читать ответы. С credentials это позволяет выполнять действия от имени пользователя — CSRF-подобные атаки. Нужен whitelist конкретных origins.

Какие шесть категорий входных данных нельзя считать доверенными?
?
Query parameters, request body, headers, cookies, file uploads и path parameters. Каждый из этих источников может содержать вредоносные данные и должен проходить валидацию по типу, длине, формату и бизнес-правилам.

В каком заголовке безопаснее всего передавать API Key и почему?
?
В заголовке `X-API-Key`. В отличие от query parameter, заголовок не попадает в серверные логи, Referer, историю браузера и кеш промежуточных узлов.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Карта раздела | [[security-overview]] | Общая навигация по всем темам безопасности |
| Аутентификация и авторизация | [[authentication-authorization]] | Углубить понимание AuthN/AuthZ, на которых строится защита API |
| Паттерны аутентификации API | [[auth-api-service-patterns]] | Детальные паттерны от API keys до Zero Trust для сервисов |
| Проектирование API | [[api-design]] | Как правильно проектировать REST/GraphQL API до добавления защиты |
| Уязвимости веб-приложений | [[web-security-owasp]] | OWASP Top 10 — контекст угроз, от которых защищает API protection |
| HTTPS и TLS | [[security-https-tls]] | Транспортный уровень защиты: handshake, сертификаты, pinning |
| Управление секретами | [[security-secrets-management]] | Как безопасно хранить и ротировать API keys, токены и credentials |

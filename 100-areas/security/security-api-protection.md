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

## Проверь себя

<details>
<summary>1. Какой алгоритм rate limiting выбрать?</summary>

**Ответ:**
- **Fixed Window:** Простой, но burst на границе окна
- **Sliding Window:** Более плавный, сложнее реализовать
- **Token Bucket:** Позволяет burst, ограничивает sustained rate
- **Leaky Bucket:** Сглаживает трафик, добавляет latency

Для большинства API: Token Bucket — хороший баланс.

</details>

<details>
<summary>2. Чем API Key отличается от JWT?</summary>

**Ответ:**
- **API Key:** Идентифицирует приложение, долгоживущий, для rate limiting
- **JWT:** Аутентифицирует пользователя, короткоживущий, содержит claims

Можно комбинировать: API Key для приложения + JWT для пользователя.

</details>

<details>
<summary>3. Как предотвратить SQL injection?</summary>

**Ответ:**
- **Parameterized queries:** `WHERE id = ?` с bind parameters
- **ORM:** SQLAlchemy, Prisma автоматически экранируют
- **Prepared statements:** Pre-compiled queries
- **Input validation:** Дополнительный слой защиты

НИКОГДА: конкатенация/интерполяция пользовательских данных в SQL.

</details>

<details>
<summary>4. Почему CORS с allow_origins=["*"] опасен?</summary>

**Ответ:** Любой сайт может делать запросы к твоему API:
- Атакующий сайт может читать ответы
- Если с credentials — может выполнять действия от имени пользователя
- CSRF-подобные атаки

Всегда whitelist конкретных origins.

</details>

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

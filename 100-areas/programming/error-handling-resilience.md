---
title: "Error Handling & Resilience: Обработка ошибок и устойчивость"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: verified
confidence: high
tags:
  - programming
  - error-handling
  - resilience
  - reliability
  - exceptions
related:
  - "[[architecture-resilience-patterns]]"
  - "[[testing-strategies]]"
  - "[[clean-code-solid]]"
  - "[[functional-programming]]"
---

# Error Handling & Resilience: Обработка ошибок и устойчивость

> Программа должна либо работать корректно, либо падать быстро и информативно.

---

## TL;DR

- **Fail Fast** — обнаружить ошибку как можно раньше
- **Exceptions для exceptional** — исключения для неожиданных ситуаций, не для control flow
- **Graceful Degradation** — продолжить работу с ограниченной функциональностью
- **Result Types** — явное моделирование успеха/неудачи в типах (Railway-oriented)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Exception** | Механизм прерывания нормального потока при ошибке |
| **Error** | Значение, представляющее неудачу операции |
| **Fail Fast** | Стратегия раннего обнаружения и сигнализации об ошибках |
| **Graceful Degradation** | Продолжение работы с ограниченной функциональностью |
| **Circuit Breaker** | Паттерн предотвращения каскадных отказов |
| **Retry** | Повторная попытка выполнения операции |
| **Fallback** | Альтернативное поведение при ошибке |
| **Result/Either** | Тип данных для явного моделирования успеха/ошибки |

---

## Философия обработки ошибок

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING PHILOSOPHY                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     ERROR CATEGORIES                                │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  1. RECOVERABLE ERRORS                                              │   │
│  │     ├── User input validation      → Return error, ask to fix      │   │
│  │     ├── Network timeout            → Retry with backoff            │   │
│  │     ├── Resource temporarily busy  → Wait and retry                │   │
│  │     └── Expected business cases    → Handle gracefully             │   │
│  │                                                                      │   │
│  │  2. UNRECOVERABLE ERRORS                                            │   │
│  │     ├── Out of memory              → Crash                         │   │
│  │     ├── Corrupted data             → Crash, alert                  │   │
│  │     ├── Configuration missing      → Fail at startup               │   │
│  │     └── Programming bugs           → Crash, fix code               │   │
│  │                                                                      │   │
│  │  3. PANIC / FATAL                                                   │   │
│  │     ├── Security breach detected   → Immediate shutdown            │   │
│  │     ├── Data integrity violation   → Stop, don't corrupt more      │   │
│  │     └── Impossible state reached   → Bug! Crash with full context  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PRINCIPLE: Be conservative in what you do,                                │
│             be liberal in what you accept — but validate!                  │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Exceptions vs Errors

### Когда использовать Exceptions

```python
# ✅ Exceptions для EXCEPTIONAL ситуаций
class PaymentService:
    def charge(self, amount: float, card: Card) -> Receipt:
        if amount <= 0:
            # Программистская ошибка — не должно случиться
            raise ValueError("Amount must be positive")

        if not card.is_valid():
            # Программистская ошибка — должны были проверить раньше
            raise InvalidCardError("Card validation failed")

        try:
            response = self.gateway.charge(amount, card)
        except ConnectionError:
            # Инфраструктурная проблема — можно retry
            raise PaymentServiceUnavailable("Gateway unreachable")

        return Receipt(response.transaction_id, amount)

# Использование
try:
    receipt = payment_service.charge(100.0, card)
except PaymentServiceUnavailable:
    # Можем показать пользователю "попробуйте позже"
    show_retry_message()
```

### Когда использовать Result Types

```python
# ✅ Result types для ОЖИДАЕМЫХ вариантов
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Union[Ok[T], Err[E]]

class UserService:
    def find_user(self, user_id: str) -> Result[User, str]:
        """Пользователь может не существовать — это нормально."""
        user = self.db.get(user_id)
        if user is None:
            return Err(f"User {user_id} not found")
        return Ok(user)

    def validate_password(self, password: str) -> Result[str, list[str]]:
        """Невалидный пароль — ожидаемый случай."""
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        if not any(c.isupper() for c in password):
            errors.append("Password must contain uppercase letter")
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain digit")

        if errors:
            return Err(errors)
        return Ok(password)

# Использование — явная обработка обоих случаев
result = user_service.find_user("123")
match result:
    case Ok(user):
        print(f"Found: {user.name}")
    case Err(error):
        print(f"Not found: {error}")
```

### Сравнение подходов

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   EXCEPTIONS vs RESULT TYPES                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EXCEPTIONS:                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ✅ Pros:                         ❌ Cons:                          │   │
│  │  • Familiar syntax                • Hidden control flow             │   │
│  │  • Stack trace included           • Easy to forget to catch        │   │
│  │  • Separate happy path            • Performance overhead            │   │
│  │  • Language-native                • Can't see in signature         │   │
│  │                                                                      │   │
│  │  Best for: Infrastructure errors, programming bugs, panics         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  RESULT TYPES:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ✅ Pros:                         ❌ Cons:                          │   │
│  │  • Explicit in type signature     • More verbose code               │   │
│  │  • Compiler enforces handling     • Requires understanding          │   │
│  │  • Composable (map, flatMap)      • Not built into all languages   │   │
│  │  • No hidden jumps                • No automatic stack trace        │   │
│  │                                                                      │   │
│  │  Best for: Business logic, expected failures, validation           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Паттерны обработки ошибок

### Fail Fast

```python
# ❌ Fail slow — ошибка обнаружится позже
def process_order(order_data: dict):
    # Много работы...
    items = fetch_items(order_data["items"])
    prices = calculate_prices(items)
    # ... ещё работа

    # Упс, только тут узнаём что customer_id невалидный
    customer = get_customer(order_data["customer_id"])  # Может быть None!

    # А тут всё падает
    send_confirmation(customer.email, prices)  # AttributeError!

# ✅ Fail fast — валидация в начале
def process_order(order_data: dict):
    # Валидация СРАЗУ
    if "customer_id" not in order_data:
        raise ValidationError("customer_id is required")
    if "items" not in order_data or not order_data["items"]:
        raise ValidationError("items cannot be empty")

    customer = get_customer(order_data["customer_id"])
    if customer is None:
        raise NotFoundError(f"Customer {order_data['customer_id']} not found")

    # Теперь спокойно работаем с провалидированными данными
    items = fetch_items(order_data["items"])
    prices = calculate_prices(items)
    send_confirmation(customer.email, prices)
```

### Guard Clauses

```python
# ❌ Nested conditionals — сложно читать
def get_insurance_amount(employee):
    result = 0
    if employee is not None:
        if employee.is_active:
            if employee.has_insurance:
                if employee.insurance_plan is not None:
                    result = employee.insurance_plan.amount
    return result

# ✅ Guard clauses — линейный код
def get_insurance_amount(employee):
    if employee is None:
        return 0
    if not employee.is_active:
        return 0
    if not employee.has_insurance:
        return 0
    if employee.insurance_plan is None:
        return 0

    return employee.insurance_plan.amount
```

### Null Object Pattern

```python
# ❌ Постоянные проверки на None
def get_discount(customer):
    if customer is None:
        return 0
    if customer.loyalty_program is None:
        return 0
    return customer.loyalty_program.discount_percent

# ✅ Null Object — специальный объект для "отсутствия"
class NullLoyaltyProgram:
    """Null Object — нет программы лояльности."""
    discount_percent = 0

    def apply_discount(self, amount):
        return amount  # Без скидки

class NullCustomer:
    """Null Object — гостевой пользователь."""
    name = "Guest"
    loyalty_program = NullLoyaltyProgram()

def get_discount(customer):
    # Нет проверок — работает единообразно
    return customer.loyalty_program.discount_percent

# Использование
customer = find_customer(user_id) or NullCustomer()
discount = get_discount(customer)  # Всегда работает!
```

---

## Railway-Oriented Programming

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    RAILWAY-ORIENTED PROGRAMMING                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SUCCESS TRACK (green)                                                     │
│  ═══════════════════════════════════════════════════════▶                  │
│         │              │              │              │                      │
│      validate      transform       save          notify                    │
│         │              │              │              │                      │
│  ═══════════════════════════════════════════════════════▶                  │
│  FAILURE TRACK (red) — bypasses remaining steps                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Input ──▶ [Validate] ──▶ [Transform] ──▶ [Save] ──▶ [Notify]       │   │
│  │               │               │            │            │            │   │
│  │               ▼               ▼            ▼            ▼            │   │
│  │  Error Track ═══════════════════════════════════════════▶ Return Err│   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Each step: Input → Result[Output, Error]                                  │
│  If any step returns Error, skip remaining steps, return Error             │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

```python
from typing import Callable, TypeVar
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')

@dataclass
class Result(Generic[T, E]):
    """Railway-oriented Result type."""

    @staticmethod
    def ok(value: T) -> 'Result[T, E]':
        return Ok(value)

    @staticmethod
    def err(error: E) -> 'Result[T, E]':
        return Err(error)

    def map(self, f: Callable[[T], U]) -> 'Result[U, E]':
        """Transform success value."""
        if isinstance(self, Ok):
            return Ok(f(self.value))
        return self

    def flat_map(self, f: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Chain operations that return Result."""
        if isinstance(self, Ok):
            return f(self.value)
        return self

    def map_error(self, f: Callable[[E], U]) -> 'Result[T, U]':
        """Transform error value."""
        if isinstance(self, Err):
            return Err(f(self.error))
        return self

@dataclass
class Ok(Result[T, E]):
    value: T

@dataclass
class Err(Result[T, E]):
    error: E

# Пример использования
def validate_email(email: str) -> Result[str, str]:
    if "@" not in email:
        return Err("Invalid email format")
    return Ok(email)

def validate_age(age: int) -> Result[int, str]:
    if age < 18:
        return Err("Must be 18 or older")
    return Ok(age)

def create_user(email: str, age: int) -> Result[User, str]:
    return (
        validate_email(email)
        .flat_map(lambda e: validate_age(age).map(lambda a: (e, a)))
        .map(lambda data: User(email=data[0], age=data[1]))
    )

# Использование
result = create_user("test@example.com", 25)
match result:
    case Ok(user):
        print(f"Created user: {user}")
    case Err(error):
        print(f"Failed: {error}")
```

---

## Resilience Patterns (код уровня)

### Retry с Exponential Backoff

```python
import time
import random
from functools import wraps

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,)
):
    """Decorator для retry с exponential backoff."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        raise

                    # Calculate delay
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    print(f"Attempt {attempt + 1} failed: {e}. "
                          f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)

            raise last_exception
        return wrapper
    return decorator

# Использование
@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    retryable_exceptions=(ConnectionError, TimeoutError)
)
def fetch_data(url: str) -> dict:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()
```

### Circuit Breaker (упрощённый)

```python
import time
from enum import Enum
from threading import Lock

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exceptions: tuple = (Exception,)
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.lock = Lock()

    def call(self, func, *args, **kwargs):
        with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpen("Circuit is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exceptions as e:
            self._on_failure()
            raise

    def _on_success(self):
        with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

# Использование
payment_circuit = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    expected_exceptions=(ConnectionError, TimeoutError)
)

def process_payment(amount: float):
    try:
        return payment_circuit.call(payment_gateway.charge, amount)
    except CircuitBreakerOpen:
        # Fallback: queue for later processing
        return queue_payment_for_later(amount)
```

### Timeout Wrapper

```python
import signal
from contextlib import contextmanager

class TimeoutError(Exception):
    pass

@contextmanager
def timeout(seconds: float):
    """Context manager для timeout."""

    def signal_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    # Set the signal handler
    original_handler = signal.signal(signal.SIGALRM, signal_handler)

    # Set the alarm
    signal.setitimer(signal.ITIMER_REAL, seconds)

    try:
        yield
    finally:
        # Cancel the alarm
        signal.setitimer(signal.ITIMER_REAL, 0)
        # Restore original handler
        signal.signal(signal.SIGALRM, original_handler)

# Использование
try:
    with timeout(5.0):
        result = slow_external_api_call()
except TimeoutError:
    result = get_cached_result()  # Fallback
```

### Fallback Pattern

```python
from typing import Callable, TypeVar, Optional

T = TypeVar('T')

class Fallback:
    """Chain of fallback strategies."""

    def __init__(self, *strategies: Callable[[], T]):
        self.strategies = strategies

    def execute(self) -> T:
        last_error = None

        for i, strategy in enumerate(self.strategies):
            try:
                result = strategy()
                if i > 0:
                    print(f"Fallback #{i} succeeded")
                return result
            except Exception as e:
                last_error = e
                print(f"Strategy #{i} failed: {e}")
                continue

        raise last_error

# Использование
def get_user_data(user_id: str) -> dict:
    return Fallback(
        # Primary: real-time API
        lambda: api_client.get_user(user_id),
        # Fallback 1: cache
        lambda: cache.get(f"user:{user_id}"),
        # Fallback 2: database
        lambda: database.get_user(user_id),
        # Fallback 3: default
        lambda: {"id": user_id, "name": "Unknown", "is_fallback": True}
    ).execute()
```

---

## Error Handling в разных слоях

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING BY LAYER                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PRESENTATION LAYER (API/UI)                                        │   │
│  │  • Convert exceptions to HTTP status codes                          │   │
│  │  • User-friendly error messages                                     │   │
│  │  • Hide internal details                                            │   │
│  │  • Log request context                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  APPLICATION LAYER (Use Cases)                                      │   │
│  │  • Orchestrate error handling                                       │   │
│  │  • Transaction rollback                                             │   │
│  │  • Translate domain errors to app errors                           │   │
│  │  • Implement retry/fallback logic                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  DOMAIN LAYER (Business Logic)                                      │   │
│  │  • Domain-specific exceptions                                       │   │
│  │  • Validation errors                                                │   │
│  │  • Business rule violations                                         │   │
│  │  • Rich error context                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  INFRASTRUCTURE LAYER (DB, External APIs)                           │   │
│  │  • Wrap low-level exceptions                                        │   │
│  │  • Add context (query, endpoint)                                    │   │
│  │  • Connection error handling                                        │   │
│  │  • Timeout handling                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Пример: REST API Error Handling

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Domain exceptions
class DomainException(Exception):
    """Base domain exception."""
    pass

class UserNotFoundError(DomainException):
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")

class InsufficientFundsError(DomainException):
    def __init__(self, balance: float, required: float):
        self.balance = balance
        self.required = required
        super().__init__(f"Insufficient funds: have {balance}, need {required}")

class ValidationError(DomainException):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")

# Error response model
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict = {}

# Global exception handler
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    error_mapping = {
        UserNotFoundError: (404, "USER_NOT_FOUND"),
        InsufficientFundsError: (400, "INSUFFICIENT_FUNDS"),
        ValidationError: (422, "VALIDATION_ERROR"),
    }

    status_code, error_code = error_mapping.get(
        type(exc),
        (500, "INTERNAL_ERROR")
    )

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error_code=error_code,
            message=str(exc),
            details=getattr(exc, '__dict__', {})
        ).model_dump()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log the full exception for debugging
    logger.exception(f"Unhandled exception: {exc}")

    # Return generic error to client
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred"
        ).model_dump()
    )

# Usage in endpoint
@app.post("/transfer")
async def transfer_money(from_id: str, to_id: str, amount: float):
    # These will be caught by exception handlers
    sender = user_service.get_user(from_id)  # May raise UserNotFoundError
    recipient = user_service.get_user(to_id)  # May raise UserNotFoundError

    account_service.transfer(sender, recipient, amount)  # May raise InsufficientFundsError

    return {"status": "success"}
```

---

## Логирование ошибок

```python
import logging
import traceback
from contextvars import ContextVar

# Request context for correlation
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

class StructuredLogger:
    """Structured logging for errors."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def error(
        self,
        message: str,
        exception: Exception = None,
        **context
    ):
        log_entry = {
            "level": "ERROR",
            "message": message,
            "request_id": request_id_var.get(),
            **context
        }

        if exception:
            log_entry["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc()
            }

        self.logger.error(log_entry)

    def warn_with_context(
        self,
        message: str,
        **context
    ):
        log_entry = {
            "level": "WARN",
            "message": message,
            "request_id": request_id_var.get(),
            **context
        }
        self.logger.warning(log_entry)

# Использование
logger = StructuredLogger(__name__)

try:
    result = process_payment(order)
except PaymentError as e:
    logger.error(
        "Payment processing failed",
        exception=e,
        order_id=order.id,
        amount=order.total,
        payment_method=order.payment_method.type
    )
    raise
```

---

## Проверь себя

<details>
<summary>1. Когда использовать exceptions, а когда Result types?</summary>

**Ответ:**

**Exceptions используй для:**
- Программистских ошибок (bugs)
- Инфраструктурных проблем (сеть, диск)
- Неожиданных ситуаций
- Когда нет возможности продолжить

**Result types используй для:**
- Ожидаемых бизнес-случаев (пользователь не найден)
- Валидации пользовательского ввода
- Операций, которые "нормально" могут не удаться
- Когда caller должен явно обработать оба случая

**Практическое правило:**
- Если ошибку нужно обрабатывать в каждом месте вызова → Result
- Если ошибка редкая и обрабатывается централизованно → Exception

</details>

<details>
<summary>2. Что такое Fail Fast и почему это важно?</summary>

**Ответ:**

**Fail Fast** — обнаружить и сигнализировать об ошибке как можно раньше.

**Почему важно:**
1. **Быстрая обратная связь** — узнаём о проблеме сразу
2. **Меньше side effects** — ошибка до изменения состояния
3. **Легче отладка** — stack trace ближе к источнику
4. **Предсказуемость** — система не в неопределённом состоянии

**Как применять:**
- Валидация на входе функций
- Проверка preconditions
- Guard clauses
- Assertions для инвариантов

**Пример:**
```python
# ❌ Fail slow
def process(data):
    # много работы...
    # только тут падаем если data = None

# ✅ Fail fast
def process(data):
    if data is None:
        raise ValueError("data is required")
    # безопасная работа
```

</details>

<details>
<summary>3. Как реализовать graceful degradation?</summary>

**Ответ:**

**Graceful Degradation** — продолжение работы с ограниченной функциональностью.

**Стратегии:**

1. **Fallback values:**
   ```python
   cache_result = cache.get(key) or default_value
   ```

2. **Fallback services:**
   ```python
   try:
       data = primary_api.fetch()
   except:
       data = backup_api.fetch()
   ```

3. **Feature degradation:**
   ```python
   if recommendation_service.is_available():
       show_personalized()
   else:
       show_popular()  # Fallback to non-personalized
   ```

4. **Circuit breaker с fallback:**
   ```python
   try:
       result = circuit_breaker.call(external_service)
   except CircuitBreakerOpen:
       result = cached_result or default
   ```

**Ключевые принципы:**
- Определить критичные vs некритичные функции
- Иметь fallback для некритичных
- Мониторить degraded state
- Автоматически восстанавливаться

</details>

<details>
<summary>4. Как правильно логировать ошибки?</summary>

**Ответ:**

**Что логировать:**
- Тип ошибки
- Сообщение
- Stack trace
- Контекст (request_id, user_id, параметры)
- Timestamp

**Что НЕ логировать:**
- Пароли, токены, ключи
- PII данные (номера карт, SSN)
- Полные request/response bodies с чувствительными данными

**Уровни:**
- **ERROR** — требует внимания, влияет на пользователя
- **WARN** — потенциальная проблема, система справилась
- **INFO** — важные события (для audit)
- **DEBUG** — детали для разработчиков

**Best practices:**
```python
# ✅ Структурированный лог с контекстом
logger.error(
    "Payment failed",
    exc_info=True,
    extra={
        "order_id": order.id,
        "amount": order.total,
        "payment_provider": "stripe",
        "error_code": e.code
    }
)

# ❌ Бесполезный лог
logger.error(f"Error: {e}")
```

</details>

<details>
<summary>5. Когда использовать retry, а когда circuit breaker?</summary>

**Ответ:**

**Retry использовать когда:**
- Transient errors (временные сбои сети)
- Идемпотентные операции
- Известно, что сервис скоро восстановится
- Нужно обработать единичный запрос

**Circuit Breaker использовать когда:**
- Сервис полностью недоступен
- Много запросов к одному сервису
- Нужно предотвратить каскадный отказ
- Нужно дать сервису время восстановиться

**Комбинация:**
```
Request → [Retry with backoff] → [Circuit Breaker] → External Service
```

- Retry: 3 попытки с exponential backoff
- Circuit Breaker: открывается после 5 failures за 30 сек
- Когда circuit открыт: возвращаем fallback сразу (без retry)

**Важно:**
- Retry без backoff может усугубить проблему (DDoS себя)
- Circuit breaker нужен для защиты downstream service
- Всегда добавлять jitter чтобы избежать thundering herd

</details>

---

## Связи

- [[architecture-resilience-patterns]] — паттерны на уровне архитектуры
- [[testing-strategies]] — тестирование error handling
- [[clean-code-solid]] — принципы чистого кода
- [[functional-programming]] — Result types из FP

---

## Источники

- "Release It!" by Michael Nygard
- "Patterns for Fault Tolerant Software" by Robert Hanmer
- [Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/)
- [Microsoft — Transient fault handling](https://docs.microsoft.com/en-us/azure/architecture/best-practices/transient-faults)

---

*Проверено: 2025-12-22*

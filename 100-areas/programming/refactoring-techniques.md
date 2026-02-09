---
title: "Refactoring Techniques: Улучшение кода без изменения поведения"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/programming
  - refactoring
  - clean-code
  - legacy
  - technical-debt
  - type/concept
  - level/intermediate
related:
  - "[[clean-code-solid]]"
  - "[[design-patterns]]"
  - "[[testing-strategies]]"
  - "[[technical-debt]]"
---

# Refactoring Techniques: Улучшение кода без изменения поведения

> Рефакторинг — изменение внутренней структуры кода без изменения его внешнего поведения.

---

## TL;DR

- **Refactoring** — улучшение дизайна существующего кода мелкими безопасными шагами
- **Ключевое правило:** Тесты должны проходить до и после каждого шага
- **Цель:** Повышение читаемости, снижение сложности, облегчение изменений
- **Когда:** Перед добавлением фичи, при исправлении бага, во время code review

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Refactoring** | Изменение структуры кода без изменения поведения |
| **Code Smell** | Признак проблемы в дизайне кода |
| **Technical Debt** | Накопленные компромиссы в качестве кода |
| **Extract Method** | Выделение части кода в отдельный метод |
| **Inline** | Замена вызова функции её телом |
| **Characterization Test** | Тест, фиксирующий текущее поведение legacy кода |
| **Seam** | Место в коде, где можно изменить поведение без редактирования |

---

## Зачем рефакторить

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    WHY REFACTORING MATTERS                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WITHOUT REFACTORING:                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Feature 1 ──▶ Quick hack ──▶ More hacks ──▶ Unmaintainable mess   │   │
│  │                    │              │                │                │   │
│  │                    ▼              ▼                ▼                │   │
│  │              Time: 1 day    Time: 3 days    Time: 2 weeks          │   │
│  │                                                                      │   │
│  │  Velocity: ████████░░ → ████░░░░░░ → ██░░░░░░░░ → █░░░░░░░░░       │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  WITH REFACTORING:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Feature 1 ──▶ Clean code ──▶ Refactor ──▶ More features           │   │
│  │                    │              │              │                  │   │
│  │                    ▼              ▼              ▼                  │   │
│  │              Time: 1.5 day  Time: 2 days  Time: 2 days             │   │
│  │                                                                      │   │
│  │  Velocity: ████████░░ → ████████░░ → ████████░░ → ████████░░       │   │
│  │            (sustainable pace)                                       │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Когда рефакторить

### Rule of Three

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          RULE OF THREE                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. First time: Just do it                                                 │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  function calculatePrice(order) {                │                      │
│  │    return order.items.reduce((sum, i) =>        │                      │
│  │      sum + i.price * i.quantity, 0);            │                      │
│  │  }                                               │                      │
│  └──────────────────────────────────────────────────┘                      │
│                                                                             │
│  2. Second time: Wince at duplication, but do it anyway                    │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  function calculateInvoiceTotal(invoice) {       │  <- Similar!        │
│  │    return invoice.lines.reduce((sum, l) =>      │                      │
│  │      sum + l.price * l.qty, 0);                 │                      │
│  │  }                                               │                      │
│  └──────────────────────────────────────────────────┘                      │
│                                                                             │
│  3. Third time: REFACTOR!                                                  │
│  ┌──────────────────────────────────────────────────┐                      │
│  │  function sumLineItems(items, priceKey, qtyKey) {│                      │
│  │    return items.reduce((sum, item) =>           │                      │
│  │      sum + item[priceKey] * item[qtyKey], 0);   │                      │
│  │  }                                               │                      │
│  └──────────────────────────────────────────────────┘                      │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Refactoring Opportunities

| Момент | Почему подходит |
|--------|-----------------|
| **Перед фичей** | Подготовить код к изменениям |
| **После фичи** | Убрать временные решения |
| **При баг-фиксе** | Понять код + предотвратить баги |
| **Code review** | Свежий взгляд на проблемы |
| **Понимание кода** | Рефакторинг как способ понять |

---

## Code Smells: Каталог запахов

### Bloaters (Раздутый код)

```python
# ❌ Long Method — метод делает слишком много
class OrderProcessor:
    def process_order(self, order):
        # Validate order (20 lines)
        if not order.items:
            raise ValueError("Empty order")
        if not order.customer:
            raise ValueError("No customer")
        for item in order.items:
            if item.quantity <= 0:
                raise ValueError("Invalid quantity")
            if not self.inventory.has_stock(item.product_id, item.quantity):
                raise ValueError(f"Insufficient stock for {item.product_id}")

        # Calculate totals (15 lines)
        subtotal = sum(item.price * item.quantity for item in order.items)
        tax = subtotal * 0.2
        shipping = 5.99 if subtotal < 50 else 0
        total = subtotal + tax + shipping

        # Apply discounts (10 lines)
        if order.customer.is_premium:
            total *= 0.9
        if order.coupon:
            total -= order.coupon.value

        # Process payment (15 lines)
        payment_result = self.payment_gateway.charge(
            order.customer.payment_method,
            total
        )
        if not payment_result.success:
            raise PaymentError(payment_result.error)

        # Update inventory (10 lines)
        for item in order.items:
            self.inventory.decrease(item.product_id, item.quantity)

        # Send notifications (10 lines)
        self.email_service.send_confirmation(order.customer.email, order)
        if order.customer.phone:
            self.sms_service.send_confirmation(order.customer.phone, order)

        return OrderResult(order_id=order.id, total=total)

# ✅ After Extract Method — каждый метод делает одно
class OrderProcessor:
    def process_order(self, order):
        self._validate_order(order)
        totals = self._calculate_totals(order)
        final_total = self._apply_discounts(order, totals)
        self._process_payment(order, final_total)
        self._update_inventory(order)
        self._send_notifications(order)
        return OrderResult(order_id=order.id, total=final_total)

    def _validate_order(self, order):
        OrderValidator(self.inventory).validate(order)

    def _calculate_totals(self, order):
        return TotalsCalculator().calculate(order)

    def _apply_discounts(self, order, totals):
        return DiscountApplier().apply(order, totals)

    # ... остальные приватные методы
```

```python
# ❌ Large Class — класс знает слишком много
class User:
    def __init__(self):
        self.name = ""
        self.email = ""
        self.password_hash = ""
        self.address_street = ""
        self.address_city = ""
        self.address_zip = ""
        self.card_number = ""
        self.card_expiry = ""
        self.card_cvv = ""
        self.orders = []
        self.cart_items = []

    def validate_email(self): ...
    def hash_password(self): ...
    def format_address(self): ...
    def validate_card(self): ...
    def charge_card(self): ...
    def add_to_cart(self): ...
    def checkout(self): ...

# ✅ After Extract Class — разделение ответственностей
class User:
    def __init__(self, name: str, email: str, password_hash: str):
        self.name = name
        self.email = Email(email)
        self.password_hash = password_hash
        self.address: Optional[Address] = None
        self.payment_method: Optional[PaymentMethod] = None

class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise ValueError("Invalid email")
        self.value = value

    def _is_valid(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[1]

class Address:
    def __init__(self, street: str, city: str, zip_code: str):
        self.street = street
        self.city = city
        self.zip_code = zip_code

    def format(self) -> str:
        return f"{self.street}, {self.city} {self.zip_code}"

class PaymentMethod:
    def __init__(self, card_number: str, expiry: str, cvv: str):
        self.card_number = card_number
        self.expiry = expiry
        self.cvv = cvv

    def validate(self) -> bool: ...
    def charge(self, amount: float) -> PaymentResult: ...
```

### Object-Orientation Abusers

```python
# ❌ Switch Statements — повторяющийся switch
def calculate_shipping(order):
    if order.shipping_type == "standard":
        return 5.99
    elif order.shipping_type == "express":
        return 12.99
    elif order.shipping_type == "overnight":
        return 24.99
    elif order.shipping_type == "international":
        return 39.99
    else:
        raise ValueError("Unknown shipping type")

def get_delivery_days(order):
    if order.shipping_type == "standard":
        return 5
    elif order.shipping_type == "express":
        return 2
    elif order.shipping_type == "overnight":
        return 1
    elif order.shipping_type == "international":
        return 14
    # ... тот же switch снова!

# ✅ Replace Conditional with Polymorphism
from abc import ABC, abstractmethod

class ShippingMethod(ABC):
    @abstractmethod
    def cost(self) -> float: ...

    @abstractmethod
    def delivery_days(self) -> int: ...

class StandardShipping(ShippingMethod):
    def cost(self) -> float:
        return 5.99

    def delivery_days(self) -> int:
        return 5

class ExpressShipping(ShippingMethod):
    def cost(self) -> float:
        return 12.99

    def delivery_days(self) -> int:
        return 2

class OvernightShipping(ShippingMethod):
    def cost(self) -> float:
        return 24.99

    def delivery_days(self) -> int:
        return 1

# Использование
def calculate_shipping(order):
    return order.shipping_method.cost()

def get_delivery_days(order):
    return order.shipping_method.delivery_days()
```

### Change Preventers

```python
# ❌ Divergent Change — один класс меняется по разным причинам
class Report:
    def __init__(self, data):
        self.data = data

    # Меняется при изменении бизнес-логики
    def calculate_metrics(self):
        return {
            "total": sum(d.value for d in self.data),
            "average": sum(d.value for d in self.data) / len(self.data)
        }

    # Меняется при изменении формата вывода
    def render_html(self):
        return f"<h1>Report</h1><p>Total: {self.calculate_metrics()['total']}</p>"

    # Меняется при изменении способа хранения
    def save_to_database(self, db):
        db.execute("INSERT INTO reports ...", self.calculate_metrics())

# ✅ Separate Concerns
class ReportCalculator:
    def calculate(self, data) -> ReportMetrics:
        return ReportMetrics(
            total=sum(d.value for d in data),
            average=sum(d.value for d in data) / len(data)
        )

class HtmlReportRenderer:
    def render(self, metrics: ReportMetrics) -> str:
        return f"<h1>Report</h1><p>Total: {metrics.total}</p>"

class ReportRepository:
    def save(self, metrics: ReportMetrics, db):
        db.execute("INSERT INTO reports ...", metrics)
```

### Couplers (Сильная связанность)

```python
# ❌ Feature Envy — метод больше интересуется чужим классом
class OrderPrinter:
    def print_order(self, order):
        # Все обращения к order — Feature Envy!
        print(f"Customer: {order.customer.name}")
        print(f"Address: {order.customer.address.street}, "
              f"{order.customer.address.city}")
        total = sum(item.price * item.quantity for item in order.items)
        print(f"Total: ${total:.2f}")

# ✅ Move Method — переместить логику туда, где данные
class Order:
    def format_for_print(self) -> str:
        return f"""Customer: {self.customer.name}
Address: {self.customer.address.format()}
Total: ${self.calculate_total():.2f}"""

    def calculate_total(self) -> float:
        return sum(item.subtotal() for item in self.items)

class OrderPrinter:
    def print_order(self, order):
        print(order.format_for_print())
```

```python
# ❌ Message Chains — цепочка вызовов (Law of Demeter violation)
def get_manager_name(employee):
    return employee.department.manager.person.name

# ✅ Hide Delegate
class Employee:
    def get_manager_name(self) -> str:
        return self.department.get_manager_name()

class Department:
    def get_manager_name(self) -> str:
        return self.manager.name
```

---

## Основные техники рефакторинга

### Extract Method

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         EXTRACT METHOD                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  BEFORE:                           AFTER:                                  │
│  ┌─────────────────────────┐      ┌─────────────────────────┐             │
│  │ void printOwing() {     │      │ void printOwing() {     │             │
│  │   // print banner       │      │   printBanner();        │             │
│  │   System.out.println    │      │   printDetails();       │             │
│  │     ("**********");     │      │ }                       │             │
│  │   System.out.println    │      │                         │             │
│  │     ("Customer Owes");  │      │ void printBanner() {    │             │
│  │   System.out.println    │      │   System.out.println    │             │
│  │     ("**********");     │      │     ("**********");     │             │
│  │                         │      │   System.out.println    │             │
│  │   // print details      │      │     ("Customer Owes");  │             │
│  │   System.out.println    │      │   System.out.println    │             │
│  │     ("name: " + name);  │      │     ("**********");     │             │
│  │   System.out.println    │      │ }                       │             │
│  │     ("amount: " + amt); │      │                         │             │
│  │ }                       │      │ void printDetails() {   │             │
│  │                         │      │   System.out.println    │             │
│  │                         │      │     ("name: " + name);  │             │
│  │                         │      │   System.out.println    │             │
│  │                         │      │     ("amount: " + amt); │             │
│  │                         │      │ }                       │             │
│  └─────────────────────────┘      └─────────────────────────┘             │
│                                                                             │
│  MECHANICS:                                                                │
│  1. Create new method with intention-revealing name                        │
│  2. Copy extracted code into new method                                    │
│  3. Identify local variables — make them parameters or return values       │
│  4. Replace original code with method call                                 │
│  5. Test                                                                   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Replace Temp with Query

```python
# ❌ Temporary variable used multiple times
def calculate_total(order):
    base_price = order.quantity * order.item_price

    if base_price > 1000:
        return base_price * 0.95
    else:
        return base_price * 0.98

# ✅ Extract to method — reusable, testable
def calculate_total(order):
    if base_price(order) > 1000:
        return base_price(order) * 0.95
    else:
        return base_price(order) * 0.98

def base_price(order):
    return order.quantity * order.item_price
```

### Introduce Parameter Object

```python
# ❌ Multiple related parameters
def amount_invoiced(start_date, end_date):
    pass

def amount_received(start_date, end_date):
    pass

def amount_overdue(start_date, end_date):
    pass

# ✅ Group into Parameter Object
@dataclass
class DateRange:
    start: date
    end: date

    def contains(self, d: date) -> bool:
        return self.start <= d <= self.end

    def overlaps(self, other: 'DateRange') -> bool:
        return self.start <= other.end and other.start <= self.end

def amount_invoiced(date_range: DateRange):
    pass

def amount_received(date_range: DateRange):
    pass

def amount_overdue(date_range: DateRange):
    pass
```

### Replace Magic Number with Symbolic Constant

```python
# ❌ Magic numbers
def calculate_potential_energy(mass, height):
    return mass * 9.81 * height

def is_valid_password(password):
    return len(password) >= 8 and len(password) <= 128

# ✅ Named constants
GRAVITATIONAL_ACCELERATION = 9.81  # m/s²

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

def calculate_potential_energy(mass, height):
    return mass * GRAVITATIONAL_ACCELERATION * height

def is_valid_password(password):
    return MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH
```

### Decompose Conditional

```python
# ❌ Complex conditional
def get_charge(date, quantity):
    if date.before(SUMMER_START) or date.after(SUMMER_END):
        charge = quantity * winter_rate + winter_service_charge
    else:
        charge = quantity * summer_rate
    return charge

# ✅ Extract conditions and branches
def get_charge(date, quantity):
    if is_summer(date):
        return summer_charge(quantity)
    else:
        return winter_charge(quantity)

def is_summer(date):
    return not date.before(SUMMER_START) and not date.after(SUMMER_END)

def summer_charge(quantity):
    return quantity * summer_rate

def winter_charge(quantity):
    return quantity * winter_rate + winter_service_charge
```

---

## Работа с Legacy Code

### Characterization Tests

```python
# Legacy код без тестов — сначала создаём characterization tests
# Цель: зафиксировать ТЕКУЩЕЕ поведение (даже если оно неправильное)

class LegacyOrderCalculator:
    """Древний класс, который никто не понимает."""

    def calculate(self, items, customer_type, date):
        total = 0
        for item in items:
            if customer_type == "VIP":
                total += item["price"] * 0.8
            else:
                total += item["price"]
        if date.month == 12:
            total *= 0.9
        return total

# Characterization test — узнаём текущее поведение
import pytest

class TestLegacyOrderCalculator:
    def setup_method(self):
        self.calculator = LegacyOrderCalculator()

    def test_regular_customer_single_item(self):
        items = [{"price": 100}]
        # Запускаем, смотрим результат, фиксируем как expected
        result = self.calculator.calculate(
            items, "regular", date(2024, 6, 15)
        )
        assert result == 100  # Зафиксировали!

    def test_vip_customer_gets_20_percent_discount(self):
        items = [{"price": 100}]
        result = self.calculator.calculate(
            items, "VIP", date(2024, 6, 15)
        )
        assert result == 80  # 20% скидка для VIP

    def test_december_gives_additional_10_percent(self):
        items = [{"price": 100}]
        result = self.calculator.calculate(
            items, "regular", date(2024, 12, 15)
        )
        assert result == 90  # 10% декабрьская скидка

    def test_vip_in_december_stacks_discounts(self):
        items = [{"price": 100}]
        result = self.calculator.calculate(
            items, "VIP", date(2024, 12, 15)
        )
        # 100 * 0.8 = 80, 80 * 0.9 = 72
        assert result == 72  # Скидки складываются!
```

### Seams — точки изменения поведения

```
┌────────────────────────────────────────────────────────────────────────────┐
│                             SEAM TYPES                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. OBJECT SEAM (most common)                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  class PaymentProcessor:                                             │   │
│  │      def __init__(self, gateway=None):                              │   │
│  │          self.gateway = gateway or StripeGateway()  # <-- SEAM     │   │
│  │                                                                      │   │
│  │  # Test: processor = PaymentProcessor(MockGateway())                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. LINK SEAM (dependency injection)                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  # Production: from real_db import Database                         │   │
│  │  # Test: from mock_db import Database                               │   │
│  │                                                                      │   │
│  │  class UserService:                                                 │   │
│  │      def __init__(self):                                            │   │
│  │          self.db = Database()  # Какой Database — зависит от import│   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. PREPROCESSING SEAM (feature flags)                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  if settings.FEATURE_NEW_ALGORITHM:                                 │   │
│  │      result = new_algorithm(data)                                   │   │
│  │  else:                                                              │   │
│  │      result = old_algorithm(data)                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Sprout Method/Class

```python
# Legacy код, который нельзя трогать
class LegacyReportGenerator:
    def generate(self, data):
        # 500 lines of spaghetti
        # Нужно добавить валидацию, но страшно трогать
        result = []
        for item in data:
            # ... complex logic
            result.append(processed_item)
        return result

# ✅ Sprout Method — новая логика в новом методе
class LegacyReportGenerator:
    def generate(self, data):
        validated_data = self._validate_data(data)  # NEW: sprout method
        result = []
        for item in validated_data:
            # ... complex logic
            result.append(processed_item)
        return result

    def _validate_data(self, data):
        """Новый код — чистый и тестируемый."""
        return [item for item in data if self._is_valid(item)]

    def _is_valid(self, item):
        return item.get("value") is not None and item.get("value") >= 0

# ✅ Sprout Class — если логика сложная
class DataValidator:
    """Отдельный чистый класс для новой функциональности."""

    def validate(self, data: List[dict]) -> List[dict]:
        return [item for item in data if self._is_valid(item)]

    def _is_valid(self, item: dict) -> bool:
        return (
            item.get("value") is not None
            and item.get("value") >= 0
            and item.get("name")
        )

class LegacyReportGenerator:
    def __init__(self):
        self.validator = DataValidator()

    def generate(self, data):
        validated_data = self.validator.validate(data)
        # ... rest of legacy code
```

---

## Стратегия безопасного рефакторинга

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    SAFE REFACTORING WORKFLOW                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │   1. ENSURE TESTS EXIST                                              │  │
│  │   ┌─────────────────────────────────────────────────────────────┐   │  │
│  │   │  No tests? → Write characterization tests first             │   │  │
│  │   │  Tests exist? → Run them, ensure green ✓                    │   │  │
│  │   └─────────────────────────────────────────────────────────────┘   │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   2. MAKE ONE SMALL CHANGE                                          │  │
│  │   ┌─────────────────────────────────────────────────────────────┐   │  │
│  │   │  • Rename variable                                          │   │  │
│  │   │  • Extract one method                                       │   │  │
│  │   │  • Inline one temp                                          │   │  │
│  │   │  • Move one field                                           │   │  │
│  │   └─────────────────────────────────────────────────────────────┘   │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   3. RUN TESTS                                                      │  │
│  │   ┌─────────────────────────────────────────────────────────────┐   │  │
│  │   │  Tests pass? → Commit! → Go to step 2                       │   │  │
│  │   │  Tests fail? → Undo change → Investigate                    │   │  │
│  │   └─────────────────────────────────────────────────────────────┘   │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   4. REPEAT until code is clean                                     │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  KEY PRINCIPLE: Small steps + frequent tests = safety                      │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Commit часто

```bash
# Каждый атомарный рефакторинг = отдельный коммит
git commit -m "refactor: extract calculateTotal method"
git commit -m "refactor: rename 'x' to 'orderTotal'"
git commit -m "refactor: introduce DateRange parameter object"

# Если что-то пошло не так — легко откатить
git revert HEAD

# Или откатить к последнему рабочему состоянию
git reset --hard HEAD~1
```

---

## IDE Support

### Automated Refactorings

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      IDE REFACTORING SUPPORT                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  IntelliJ IDEA / Android Studio:                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Refactor Menu (Ctrl+Alt+Shift+T / ⌃⌥⇧T):                          │   │
│  │                                                                      │   │
│  │  • Rename (Shift+F6)           - переименовать везде               │   │
│  │  • Extract Method (Ctrl+Alt+M) - выделить код в метод              │   │
│  │  • Extract Variable (Ctrl+Alt+V) - ввести переменную               │   │
│  │  • Extract Constant (Ctrl+Alt+C) - ввести константу                │   │
│  │  • Extract Parameter (Ctrl+Alt+P) - сделать параметром             │   │
│  │  • Inline (Ctrl+Alt+N)         - инлайнить метод/переменную        │   │
│  │  • Move (F6)                   - переместить класс/метод           │   │
│  │  • Change Signature (Ctrl+F6) - изменить сигнатуру                 │   │
│  │  • Pull Members Up/Push Down  - перенос в иерархии                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  VS Code (with extensions):                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Refactor Menu (Ctrl+Shift+R / ⌘⇧R):                               │   │
│  │                                                                      │   │
│  │  • Rename Symbol (F2)                                               │   │
│  │  • Extract to function/method                                       │   │
│  │  • Extract to constant                                              │   │
│  │  • Inline variable                                                  │   │
│  │  • Move to new file                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PRO TIP: IDE refactorings are SAFE — they update all references!          │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

<details>
<summary>1. Что такое рефакторинг и когда его НЕ делать?</summary>

**Ответ:**

**Рефакторинг** — изменение внутренней структуры кода без изменения его внешнего поведения.

**Когда НЕ рефакторить:**
1. **Deadline близко** — рефакторинг может затянуться
2. **Нет тестов** — без тестов опасно менять код
3. **Код нужно переписать** — если код настолько плох, что проще написать заново
4. **Код будет удалён** — зачем улучшать то, что скоро удалим
5. **Не понимаешь код** — сначала разберись, потом рефактори

**Золотое правило:** Рефакторинг должен быть безопасным (тесты) и приносить пользу (облегчать следующие изменения).

</details>

<details>
<summary>2. Как работать с legacy кодом без тестов?</summary>

**Ответ:**

**Шаги работы с legacy:**

1. **Characterization Tests:**
   - Написать тесты, фиксирующие ТЕКУЩЕЕ поведение
   - Даже если поведение неправильное — сначала фиксируем
   - Запустить код, посмотреть результат, записать как expected

2. **Найти Seams:**
   - Object seams (внедрение зависимостей)
   - Link seams (подмена через import)
   - Preprocessing seams (feature flags)

3. **Sprout Method/Class:**
   - Новую логику писать в новых методах/классах
   - Новый код чистый и полностью покрыт тестами
   - Старый код вызывает новый

4. **Постепенное покрытие:**
   - Добавлять тесты при каждом изменении
   - Рефакторить только покрытый код
   - Boy Scout Rule: оставь код чище, чем нашёл

</details>

<details>
<summary>3. Какие code smells указывают на нарушение Single Responsibility?</summary>

**Ответ:**

**Code smells, указывающие на нарушение SRP:**

1. **Large Class** — класс имеет много полей и методов
2. **Divergent Change** — класс меняется по разным причинам
3. **Long Method** — метод делает слишком много
4. **God Object** — класс знает слишком много о системе
5. **Feature Envy** — метод больше работает с чужими данными

**Как исправить:**
- **Extract Class** — выделить связанные поля и методы в новый класс
- **Extract Method** — разбить метод на части
- **Move Method** — переместить метод к его данным
- **Replace Conditional with Polymorphism** — для switch statements

**Правило:** Класс должен иметь одну причину для изменения.

</details>

<details>
<summary>4. Как безопасно рефакторить большой метод в 200 строк?</summary>

**Ответ:**

**Пошаговая стратегия:**

1. **Убедиться, что есть тесты**
   - Нет тестов → написать characterization tests
   - Есть тесты → запустить, убедиться что зелёные

2. **Найти "швы" в коде**
   - Комментарии типа "// calculate total"
   - Пустые строки между блоками
   - Группы связанных операций

3. **Extract Method поблочно**
   ```python
   # До: монолит 200 строк
   # После:
   def main_method():
       data = self._load_data()
       validated = self._validate(data)
       processed = self._process(validated)
       return self._format_output(processed)
   ```

4. **Один рефакторинг — один коммит**
   - Маленький шаг → тест → коммит
   - Если сломалось — откатить

5. **Не менять поведение!**
   - Цель: только структура
   - Баги исправлять отдельными коммитами

</details>

<details>
<summary>5. Чем Extract Method отличается от Extract Class?</summary>

**Ответ:**

| Аспект | Extract Method | Extract Class |
|--------|---------------|---------------|
| **Что выделяем** | Код → метод | Поля + методы → класс |
| **Когда применять** | Long Method | Large Class, Divergent Change |
| **Результат** | Тот же класс, больше методов | Новый класс, меньше ответственностей |
| **Сложность** | Низкая | Средняя |

**Extract Method применять когда:**
- Метод слишком длинный
- Часть кода можно переиспользовать
- Нужно дать имя блоку кода

**Extract Class применять когда:**
- Класс делает слишком много
- Группа полей всегда используется вместе
- Группа методов работает с одним подмножеством данных
- Класс меняется по разным причинам

**Пример перехода:**
1. Extract Method несколько раз
2. Замечаем, что методы работают с одними полями
3. Extract Class — выделяем поля + методы в новый класс

</details>

---

## Связи

- [[clean-code-solid]] — принципы чистого кода
- [[design-patterns]] — паттерны проектирования
- [[testing-strategies]] — тестирование для безопасного рефакторинга
- [[technical-debt]] — управление техническим долгом

---

## Источники

- "Refactoring" by Martin Fowler (2nd edition)
- "Working Effectively with Legacy Code" by Michael Feathers
- [Refactoring Guru](https://refactoring.guru/)
- [Source Making — Refactoring](https://sourcemaking.com/refactoring)

---

*Проверено: 2025-12-22*

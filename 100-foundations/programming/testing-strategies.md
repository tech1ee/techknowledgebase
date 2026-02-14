---
title: "Testing: пирамида, которая спасает от 3am багов"
created: 2025-11-24
modified: 2026-02-13
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/programming
  - programming/testing
  - programming/tdd
  - best-practices
  - type/concept
  - level/intermediate
related:
  - "[[clean-code-solid]]"
  - "[[ci-cd-pipelines]]"
  - "[[design-patterns]]"
prerequisites:
  - "[[clean-code-solid]]"
reading_time: 23
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Testing: пирамида, которая спасает от 3am багов

Тесты — страховка от "работает на моей машине". 100% coverage не гарантирует качество. Тестируй поведение, не реализацию.

---

## Зачем это нужно

### Проблема: Код без тестов — мина замедленного действия

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| **"Работает на моей машине"** | Нет проверки в изолированном окружении | Баги в проде, ночные звонки |
| **"Страшно менять код"** | Нет уверенности, что изменение не сломает | Technical debt растёт, код "костенеет" |
| **"Релизили неделю, ловили баги"** | Ручное тестирование, QA bottleneck | Slow time-to-market |
| **"Рефакторинг невозможен"** | Нет safety net | Legacy code навсегда |

### Кому нужно понимать тестирование

| Роль | Зачем нужно | Глубина |
|------|-------------|---------|
| **Backend Developer** | Unit tests, integration tests, API tests | Глубокая |
| **Frontend Developer** | Component tests, E2E, visual regression | Глубокая |
| **QA Engineer** | Вся пирамида, test automation | Глубокая |
| **Tech Lead** | Test strategy, coverage requirements | Средняя |

---

## Актуальность 2024-2025

| Тренд | Статус | Что важно знать |
|-------|--------|-----------------|
| **AI-assisted testing** | 🆕 Растёт | Copilot/Claude генерируют тесты, но требуют review |
| **Property-Based Testing** | ✅ Mature | fast-check, Hypothesis — генерация edge cases |
| **Visual Regression** | ✅ Mainstream | Chromatic, Percy — скриншоты для UI тестов |
| **Contract Testing** | ✅ Best Practice | Pact, Spring Cloud Contract — API contracts |
| **Mutation Testing** | ✅ Полезно | Stryker, PIT — проверка качества тестов |
| **Testing Library > Enzyme** | ✅ Стандарт | Тестирование поведения, не реализации |

**Ключевые изменения:**
- Shift-left testing: тесты пишутся раньше, интегрированы в PR workflow
- Testing as documentation: тесты описывают expected behavior
- Playwright вытеснил Cypress для E2E

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Unit test** | Тест одной функции/класса в изоляции |
| **Integration test** | Тест взаимодействия компонентов |
| **E2E test** | End-to-end тест всей системы |
| **Mock** | Объект-заглушка с заданным поведением |
| **Stub** | Простая заглушка с фиксированным ответом |
| **TDD** | Test-Driven Development — сначала тест, потом код |
| **Coverage** | Процент кода, покрытого тестами |
| **Flaky test** | Нестабильный тест (то проходит, то падает) |

---

## Зачем тестировать?

```
Без тестов:

"Работает на моей машине" → деплой в пятницу
    ↓
Прод падает в субботу ночью
    ↓
Откатываем вслепую
    ↓
Через месяц: страшно менять любой код
    ↓
"Этот модуль никто не трогает, он работает"

С тестами:

Изменил код → Запустил тесты
    ↓
Тест упал → Вижу ЧТО сломалось
    ↓
Починил → Уверенно деплою
    ↓
Рефакторинг без страха
```

---

## Пирамида тестирования

```
                    ▲
                   /  \
                  / E2E \        Медленные, хрупкие
                 /  10%  \       Проверяют всю систему
                /──────────\
               /            \
              / Integration  \   Средняя скорость
             /     20%        \  Проверяют связи
            /──────────────────\
           /                    \
          /     Unit Tests       \  Быстрые, надёжные
         /         70%            \ Проверяют логику
        /──────────────────────────\

Время выполнения:
  Unit:        5-50ms каждый
  Integration: 100-500ms каждый
  E2E:         5-30 секунд каждый

На 1000 тестов:
  Unit:        ~10 секунд
  Integration: ~1-2 минуты
  E2E:         ~5-10 минут (или больше)
```

---

## Unit Tests: фундамент

### Что тестировать

```typescript
// Чистая функция — идеальный кандидат
function calculateDiscount(price: number, discountPercent: number): number {
  if (discountPercent < 0 || discountPercent > 100) {
    throw new Error('Invalid discount');
  }
  return price * (1 - discountPercent / 100);
}

// Тесты
describe('calculateDiscount', () => {
  it('applies discount correctly', () => {
    expect(calculateDiscount(100, 20)).toBe(80);
    expect(calculateDiscount(50, 10)).toBe(45);
  });

  it('handles zero discount', () => {
    expect(calculateDiscount(100, 0)).toBe(100);
  });

  it('handles 100% discount', () => {
    expect(calculateDiscount(100, 100)).toBe(0);
  });

  it('throws on invalid discount', () => {
    expect(() => calculateDiscount(100, -10)).toThrow('Invalid discount');
    expect(() => calculateDiscount(100, 150)).toThrow('Invalid discount');
  });

  it('handles decimal prices', () => {
    expect(calculateDiscount(99.99, 10)).toBeCloseTo(89.99);
  });
});
```

### Паттерн AAA (Arrange-Act-Assert)

```typescript
describe('UserService', () => {
  it('creates user with hashed password', async () => {
    // Arrange — подготовка
    const userRepo = new InMemoryUserRepository();
    const hasher = new FakePasswordHasher();
    const service = new UserService(userRepo, hasher);

    const userData = {
      email: 'test@example.com',
      password: 'secret123'
    };

    // Act — действие
    const user = await service.createUser(userData);

    // Assert — проверка
    expect(user.email).toBe('test@example.com');
    expect(user.password).not.toBe('secret123');  // Захеширован
    expect(hasher.wasCalledWith('secret123')).toBe(true);
  });
});
```

### Mocking: изоляция зависимостей

```typescript
// Зависимость, которую нужно заменить
interface EmailService {
  send(to: string, subject: string, body: string): Promise<void>;
}

// Реальный сервис использует SMTP
class SmtpEmailService implements EmailService {
  async send(to: string, subject: string, body: string) {
    // Реальная отправка email
  }
}

// Тестовый mock
class MockEmailService implements EmailService {
  public sentEmails: Array<{ to: string; subject: string; body: string }> = [];

  async send(to: string, subject: string, body: string) {
    this.sentEmails.push({ to, subject, body });
  }
}

// Тест
describe('OrderService', () => {
  it('sends confirmation email after order', async () => {
    // Arrange
    const emailService = new MockEmailService();
    const orderService = new OrderService(emailService);

    // Act
    await orderService.placeOrder({
      userId: 'user_123',
      email: 'buyer@example.com',
      items: [{ id: 'item_1', quantity: 2 }]
    });

    // Assert
    expect(emailService.sentEmails).toHaveLength(1);
    expect(emailService.sentEmails[0]).toEqual({
      to: 'buyer@example.com',
      subject: 'Order Confirmation',
      body: expect.stringContaining('item_1')
    });
  });
});
```

### Jest mocks

```typescript
// Автоматический mock модуля
jest.mock('./emailService');

import { sendEmail } from './emailService';

const mockSendEmail = sendEmail as jest.MockedFunction<typeof sendEmail>;

describe('notification', () => {
  beforeEach(() => {
    mockSendEmail.mockClear();
  });

  it('sends welcome email', async () => {
    mockSendEmail.mockResolvedValue(undefined);

    await registerUser({ email: 'new@user.com' });

    expect(mockSendEmail).toHaveBeenCalledWith(
      'new@user.com',
      'Welcome!',
      expect.any(String)
    );
  });

  it('handles email failure gracefully', async () => {
    mockSendEmail.mockRejectedValue(new Error('SMTP error'));

    // Регистрация не должна падать из-за email
    const user = await registerUser({ email: 'new@user.com' });

    expect(user).toBeDefined();
  });
});
```

---

## Integration Tests: проверка связей

```typescript
// Тестируем реальную интеграцию с БД
describe('UserRepository (integration)', () => {
  let db: Database;
  let repo: UserRepository;

  beforeAll(async () => {
    // Поднимаем тестовую БД (или testcontainers)
    db = await Database.connect(process.env.TEST_DATABASE_URL);
  });

  beforeEach(async () => {
    // Чистим данные между тестами
    await db.query('TRUNCATE users CASCADE');
    repo = new UserRepository(db);
  });

  afterAll(async () => {
    await db.close();
  });

  it('creates and retrieves user', async () => {
    const created = await repo.create({
      email: 'test@example.com',
      name: 'Test User'
    });

    const found = await repo.findById(created.id);

    expect(found).toEqual(created);
  });

  it('finds user by email', async () => {
    await repo.create({ email: 'find@me.com', name: 'Find Me' });

    const user = await repo.findByEmail('find@me.com');

    expect(user?.name).toBe('Find Me');
  });

  it('returns null for non-existent user', async () => {
    const user = await repo.findById('non-existent-id');

    expect(user).toBeNull();
  });
});
```

### API Integration Tests

```typescript
// Supertest для HTTP тестов
import request from 'supertest';
import { app } from './app';

describe('POST /api/users', () => {
  it('creates user and returns 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'new@user.com',
        password: 'securePass123'
      })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      email: 'new@user.com'
    });
    expect(response.body).not.toHaveProperty('password');
  });

  it('returns 400 for invalid email', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'not-an-email',
        password: 'securePass123'
      })
      .expect(400);

    expect(response.body.error).toContain('email');
  });

  it('returns 409 for duplicate email', async () => {
    // Создаём первого пользователя
    await request(app)
      .post('/api/users')
      .send({ email: 'dupe@test.com', password: 'pass123' });

    // Пытаемся создать дубликат
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'dupe@test.com', password: 'pass456' })
      .expect(409);

    expect(response.body.error).toContain('exists');
  });
});
```

---

## E2E Tests: проверка всей системы

```typescript
// Playwright E2E тест
import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test('successful registration', async ({ page }) => {
    // Открываем страницу
    await page.goto('/register');

    // Заполняем форму
    await page.fill('[data-testid="email-input"]', 'new@user.com');
    await page.fill('[data-testid="password-input"]', 'SecurePass123!');
    await page.fill('[data-testid="password-confirm"]', 'SecurePass123!');

    // Отправляем
    await page.click('[data-testid="submit-button"]');

    // Проверяем редирект на dashboard
    await expect(page).toHaveURL('/dashboard');

    // Проверяем приветствие
    await expect(page.locator('[data-testid="welcome-message"]'))
      .toContainText('Welcome');
  });

  test('shows validation errors', async ({ page }) => {
    await page.goto('/register');

    // Невалидный email
    await page.fill('[data-testid="email-input"]', 'not-email');
    await page.fill('[data-testid="password-input"]', '123');
    await page.click('[data-testid="submit-button"]');

    // Проверяем ошибки
    await expect(page.locator('.error-message'))
      .toContainText('valid email');
  });
});
```

```
E2E: когда и сколько

Тестируй E2E:
• Critical paths (регистрация, оплата, логин)
• Happy paths основных фич
• Smoke tests после деплоя

НЕ тестируй E2E:
• Каждый edge case (unit тесты)
• Все комбинации данных
• Внутреннюю логику

Правило: если можно протестировать на нижнем уровне —
тестируй там. E2E = последняя линия обороны.
```

---

## TDD: Test-Driven Development

```
Цикл Red-Green-Refactor:

┌─────────────────────────────────────────────────────┐
│                                                     │
│    ┌───────┐       ┌───────┐       ┌───────────┐   │
│    │  RED  │──────▶│ GREEN │──────▶│ REFACTOR  │   │
│    │       │       │       │       │           │   │
│    │Пишем  │       │Пишем  │       │Улучшаем   │   │
│    │тест   │       │код    │       │код        │   │
│    │(падает│       │(прохо-│       │(тесты     │   │
│    │)      │       │дит)   │       │проходят)  │   │
│    └───────┘       └───────┘       └───────────┘   │
│        ▲                                  │        │
│        └──────────────────────────────────┘        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### TDD на практике

```typescript
// Шаг 1: RED — пишем тест для несуществующей функции
describe('PasswordValidator', () => {
  it('rejects passwords shorter than 8 characters', () => {
    const validator = new PasswordValidator();
    const result = validator.validate('short');

    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must be at least 8 characters');
  });
});

// Тест падает: PasswordValidator не существует

// Шаг 2: GREEN — минимальный код для прохождения
class PasswordValidator {
  validate(password: string): ValidationResult {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push('Password must be at least 8 characters');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

// Тест проходит!

// Шаг 3: Добавляем следующий тест (RED)
it('rejects passwords without uppercase letters', () => {
  const validator = new PasswordValidator();
  const result = validator.validate('lowercase1');

  expect(result.isValid).toBe(false);
  expect(result.errors).toContain('Password must contain uppercase letter');
});

// Шаг 4: GREEN — добавляем проверку
validate(password: string): ValidationResult {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain uppercase letter');
  }

  return { isValid: errors.length === 0, errors };
}

// Шаг 5: REFACTOR — улучшаем без изменения поведения
interface ValidationRule {
  test: (password: string) => boolean;
  message: string;
}

class PasswordValidator {
  private rules: ValidationRule[] = [
    {
      test: (p) => p.length >= 8,
      message: 'Password must be at least 8 characters'
    },
    {
      test: (p) => /[A-Z]/.test(p),
      message: 'Password must contain uppercase letter'
    }
  ];

  validate(password: string): ValidationResult {
    const errors = this.rules
      .filter(rule => !rule.test(password))
      .map(rule => rule.message);

    return { isValid: errors.length === 0, errors };
  }
}

// Все тесты проходят, код чище
```

---

## Что тестировать, а что нет

```
ТЕСТИРУЙ:
─────────
✓ Бизнес-логику (расчёты, валидация)
✓ Edge cases (граничные значения)
✓ Error handling (что происходит при ошибках)
✓ Публичный API классов/модулей
✓ Регрессии (баг → тест → фикс)

НЕ ТЕСТИРУЙ:
────────────
✗ Private методы напрямую
✗ Тривиальный код (геттеры/сеттеры)
✗ Сторонние библиотеки
✗ Реализацию (тестируй поведение)
✗ База данных/файловая система в unit тестах
```

```typescript
// Плохо: тестируем реализацию
it('uses Array.map to transform items', () => {
  const spy = jest.spyOn(Array.prototype, 'map');
  service.processItems(items);
  expect(spy).toHaveBeenCalled();  // Зачем?
});

// Хорошо: тестируем поведение
it('transforms items correctly', () => {
  const result = service.processItems([
    { name: 'a', value: 1 },
    { name: 'b', value: 2 }
  ]);

  expect(result).toEqual([
    { name: 'A', value: 2 },
    { name: 'B', value: 4 }
  ]);
});
```

---

## Coverage: не гонись за 100%

```
Coverage показывает:
• Какой код выполнялся при тестах
• НЕ показывает качество тестов

100% coverage + плохие тесты = ложная уверенность

Пример бесполезного 100% coverage:

function divide(a: number, b: number): number {
  return a / b;
}

// Тест даёт 100% coverage
it('divides', () => {
  expect(divide(10, 2)).toBe(5);
});

// Но НЕ проверяет:
// - деление на ноль
// - большие числа
// - отрицательные числа

Полезный подход:
• 80% coverage как минимум
• Критичный код: 90%+
• Новый код: обязательно покрыт
• Mutation testing для проверки качества
```

---

## Структура тестов в проекте

```
src/
├── services/
│   └── user/
│       ├── UserService.ts
│       ├── UserService.test.ts     # Unit тесты рядом
│       └── UserRepository.ts
├── api/
│   └── routes/
│       └── users.ts
└── ...

tests/
├── integration/
│   ├── api/
│   │   └── users.test.ts           # API интеграция
│   └── repositories/
│       └── UserRepository.test.ts  # БД интеграция
├── e2e/
│   └── registration.spec.ts        # E2E сценарии
└── fixtures/
    └── users.ts                    # Тестовые данные
```

```json
// package.json scripts
{
  "scripts": {
    "test": "jest",
    "test:unit": "jest --testPathPattern=src/",
    "test:integration": "jest --testPathPattern=tests/integration/",
    "test:e2e": "playwright test",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch"
  }
}
```

---

## Подводные камни

### Проблема 1: Хрупкие тесты

```typescript
// Плохо: тест зависит от порядка элементов
it('returns users', async () => {
  const users = await service.getUsers();
  expect(users[0].name).toBe('Alice');
  expect(users[1].name).toBe('Bob');
});

// Хорошо: проверяем наличие, не порядок
it('returns users', async () => {
  const users = await service.getUsers();
  const names = users.map(u => u.name);
  expect(names).toContain('Alice');
  expect(names).toContain('Bob');
});

// Или: сортируем для сравнения
it('returns users', async () => {
  const users = await service.getUsers();
  expect(users.map(u => u.name).sort()).toEqual(['Alice', 'Bob']);
});
```

### Проблема 2: Медленные тесты

```
Медленные тесты = не запускают

Причины:
• Реальные HTTP запросы в unit тестах
• Реальная БД в каждом тесте
• Sleep/setTimeout в тестах
• Слишком много E2E

Решения:
• Mock внешние зависимости
• Тестовая БД в памяти (SQLite) или containers
• Параллельное выполнение
• Разделить unit/integration/e2e
```

### Проблема 3: Тесты ради галочки

```typescript
// Бесполезный тест
it('works', () => {
  const user = new User('test');
  expect(user).toBeDefined();  // Что это проверяет?
});

// Тест-документация
it('creates user with normalized email', () => {
  const user = new User('Test@EXAMPLE.com');
  expect(user.email).toBe('test@example.com');
});

it('throws if email is invalid', () => {
  expect(() => new User('not-email')).toThrow(InvalidEmailError);
});
```

---

## Actionable

**Начни с этого:**
```bash
# Установка Jest
npm install -D jest @types/jest ts-jest

# jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  collectCoverageFrom: ['src/**/*.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80 }
  }
};
```

**Правило для нового кода:**
```
1. Пишу тест → 2. Тест падает → 3. Пишу код →
4. Тест проходит → 5. Рефакторю
```

---

## Проверь себя

**Вопрос 1:** Почему соотношение тестов в пирамиде 70/20/10?

<details>
<summary>Ответ</summary>

**Unit tests (70%):** Быстрые (миллисекунды), стабильные, изолированные. Дают быстрый feedback, легко находить причину падения.

**Integration tests (20%):** Проверяют связи между компонентами. Медленнее (секунды), сложнее дебажить, но ловят проблемы интеграции.

**E2E tests (10%):** Проверяют всю систему. Медленные (минуты), хрупкие (зависят от UI), дорогие в поддержке. Только для critical paths.

**Инвертирование пирамиды** (много E2E, мало unit) ведёт к медленным тестам, flaky failures, и "страху менять код".
</details>

**Вопрос 2:** В чём разница между Mock и Stub?

<details>
<summary>Ответ</summary>

**Stub:** Простая заглушка с фиксированным ответом. Не проверяет, как была вызвана.

```typescript
const stubRepo = { findById: () => ({ id: '1', name: 'Test' }) };
```

**Mock:** Заглушка с проверками — как вызвали, сколько раз, с какими аргументами.

```typescript
const mockRepo = jest.fn().mockReturnValue({ id: '1' });
// Позже: expect(mockRepo).toHaveBeenCalledWith('user_123');
```

**Правило:** Используй stub для state verification, mock для behavior verification.
</details>

**Вопрос 3:** Почему 100% coverage — не гарантия качества?

<details>
<summary>Ответ</summary>

Coverage показывает, какой код **выполнялся**, но не какой **проверялся**.

```typescript
function divide(a, b) { return a / b; }
it('divides', () => { expect(divide(10, 2)).toBe(5); }); // 100% coverage!
// Но: деление на ноль? Большие числа? Отрицательные? — Не проверено!
```

**Mutation testing** решает эту проблему: меняет код (мутации) и проверяет, падают ли тесты. Если мутант "выжил" — тест слабый.

**Разумная цель:** 80% coverage + mutation score 60%+.
</details>

**Вопрос 4:** Что такое TDD и когда его применять?

<details>
<summary>Ответ</summary>

**TDD (Test-Driven Development):** Сначала тест → потом код.

**Red-Green-Refactor:**
1. RED: Написать тест, который падает
2. GREEN: Написать минимальный код, чтобы тест прошёл
3. REFACTOR: Улучшить код, не меняя поведение

**Когда применять:**
- Чётко определённые требования
- Сложная бизнес-логика
- Критичный код (платежи, безопасность)

**Когда не применять:**
- Прототипирование, exploratory work
- Простой CRUD без логики
- Когда требования меняются быстрее, чем код
</details>

**Вопрос 5:** Как избежать flaky tests?

<details>
<summary>Ответ</summary>

**Причины flaky tests:**
- Зависимость от порядка выполнения
- Shared state между тестами
- Timing issues (race conditions, timeouts)
- Внешние зависимости (сеть, файлы)

**Решения:**
- Изолировать тесты (свежий state каждый раз)
- Использовать mocks для внешних зависимостей
- Детерминированные данные (не random без seed)
- Explicit waits вместо sleep в E2E
- Retry flaky tests с логированием для анализа
</details>

---

## Связи

- Тесты и чистый код: [[clean-code-solid]]
- Тесты в CI/CD: [[ci-cd-pipelines]]
- Testable design через паттерны: [[design-patterns]]

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Martin Fowler: Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html) | Article | Классическая модель пирамиды |
| 2 | [Kent Beck: Test-Driven Development](https://www.oreilly.com/library/view/test-driven-development/0321146530/) | Book | TDD методология |
| 3 | [Jest Documentation](https://jestjs.io/docs/getting-started) | Docs | JavaScript testing framework |
| 4 | [Playwright Documentation](https://playwright.dev/docs/intro) | Docs | Modern E2E testing |
| 5 | [Testing Library](https://testing-library.com/) | Docs | Component testing philosophy |
| 6 | [Stryker Mutator](https://stryker-mutator.io/) | Docs | Mutation testing |
| 7 | [Pact Contract Testing](https://docs.pact.io/) | Docs | Consumer-driven contracts |
| 8 | [fast-check](https://fast-check.dev/) | Docs | Property-based testing |

---

---

## Ключевые карточки

Почему соотношение тестов в пирамиде 70/20/10?
?
Unit (70%): быстрые (мс), стабильные, изолированные — основа. Integration (20%): проверяют связи между компонентами, медленнее (секунды). E2E (10%): вся система, медленные (минуты), хрупкие. Инвертированная пирамида (много E2E) ведёт к медленным, flaky тестам.

Что такое паттерн AAA?
?
Arrange — подготовка данных и зависимостей. Act — выполнение тестируемого действия. Assert — проверка результата. Чёткое разделение трёх фаз делает тесты читаемыми и структурированными.

Чем Mock отличается от Stub?
?
Stub: простая заглушка с фиксированным ответом, не проверяет как была вызвана (state verification). Mock: заглушка с проверками — как вызвали, сколько раз, с какими аргументами (behavior verification).

Почему 100% coverage не гарантирует качество тестов?
?
Coverage показывает какой код выполнялся, но не какой проверялся. Можно иметь 100% coverage с `divide(10, 2)` без проверки деления на ноль. Mutation testing решает проблему: меняет код и проверяет, падают ли тесты.

Что такое TDD (Red-Green-Refactor)?
?
1) RED: написать падающий тест. 2) GREEN: написать минимальный код для прохождения. 3) REFACTOR: улучшить код при проходящих тестах. Применять при чётких требованиях и сложной бизнес-логике. Не применять при прототипировании.

Что такое flaky test и как его избежать?
?
Тест, который то проходит, то падает. Причины: shared state, зависимость от порядка выполнения, timing issues, внешние зависимости. Решения: изолировать тесты, mock внешние зависимости, детерминированные данные, explicit waits вместо sleep.

Почему тестировать поведение важнее, чем тестировать реализацию?
?
Тест реализации (`expect(spy).toHaveBeenCalled()`) ломается при рефакторинге, даже если поведение не изменилось. Тест поведения (`expect(result).toEqual(expected)`) проходит при любой внутренней реализации, пока результат корректен. Рефакторинг без страха.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ci-cd-pipelines]] | Интеграция тестов в CI/CD pipeline |
| Углубиться | [[refactoring-techniques]] | Безопасный рефакторинг опирается на тесты |
| Смежная тема | [[android-testing]] | Специфика тестирования Android-приложений |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

*Последнее обновление: 2025-12-28*

---

*Проверено: 2026-01-09*

---
title: "Module Systems: модульность от CommonJS до ESM"
created: 2026-01-09
modified: 2026-01-09
type: concept
status: published
confidence: high
tags:
  - programming/modules
  - javascript
  - topic/jvm
  - build-systems
  - type/concept
  - level/intermediate
related:
  - "[[build-systems-theory]]"
  - "[[dependency-resolution]]"
  - "[[clean-code-solid]]"
---

# Module Systems: модульность от CommonJS до ESM

> **TL;DR:** Модульная система позволяет разбивать код на независимые части с явными зависимостями. CommonJS (Node.js) — синхронный require(), ESM (браузеры, современный Node) — статический import/export. Kotlin Multiplatform использует expect/actual для кроссплатформенной модульности. Хорошая модульность = низкая связанность + высокая связность.

---

## Интуиция: 5 аналогий

### 1. Модули как LEGO
```
БЕЗ модулей:
  Один огромный кусок пластика
  Изменить часть = сломать всё

С модулями:
  🧱🧱🧱 отдельные кубики
  Каждый кубик:
  - Имеет чёткий интерфейс (пупырышки)
  - Работает независимо
  - Можно заменить на другой

Хороший модуль = хороший LEGO-кубик
```

### 2. Модули как комнаты в доме
```
┌─────────────────────────────────────────┐
│                  ДОМ                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Кухня   │  │Гостиная │  │ Спальня │ │
│  │         │──│         │──│         │ │
│  └─────────┘  └─────────┘  └─────────┘ │
└─────────────────────────────────────────┘

Каждая комната (модуль):
- Имеет своё назначение (ответственность)
- Имеет двери (exports)
- Не нужно проходить через спальню, чтобы попасть на кухню

Плохая архитектура: все комнаты проходные
```

### 3. Public API как витрина магазина
```
┌────────────────────────────────────────┐
│             ВИТРИНА (exports)          │
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │ func │  │class │  │const │         │
│  └──────┘  └──────┘  └──────┘         │
├────────────────────────────────────────┤
│            СКЛАД (private)             │
│    helpers, utils, internal state      │
│    Клиент НЕ ВИДИТ                     │
└────────────────────────────────────────┘

export = выставить в витрину
import = взять из витрины (чужого магазина)
```

### 4. Dependency как контракт
```
Модуль A зависит от модуля B:

import { fetchUser } from './userService'

Это КОНТРАКТ:
- A ожидает, что B экспортирует fetchUser
- A НЕ ЗНАЕТ как fetchUser работает внутри
- Если B изменит внутренности — A продолжит работать
- Если B изменит API (контракт) — A сломается

Loose coupling = зависимость от контракта, не от реализации
```

### 5. Циклические зависимости как deadlock
```
A imports B
B imports A

         ┌───────┐
    ┌───►│   A   │────┐
    │    └───────┘    │
    │                 ▼
    │    ┌───────┐
    └────│   B   │◄───┘
         └───────┘

Что загружать первым?
- A нужен B → жди B
- B нужен A → жди A
→ DEADLOCK или undefined behavior

Решение: выделить общую часть в модуль C
```

---

## Системы модулей

### JavaScript: эволюция

```javascript
// 1. IIFE (2009) — "бедная" модульность
(function() {
    var privateVar = 'secret';
    window.MyModule = {
        publicMethod: function() { return privateVar; }
    };
})();

// 2. CommonJS (Node.js, 2009) — синхронный
// math.js
module.exports = {
    add: (a, b) => a + b,
    subtract: (a, b) => a - b
};
// app.js
const math = require('./math');
math.add(1, 2);

// 3. AMD (RequireJS, 2010) — асинхронный для браузеров
define(['jquery'], function($) {
    return {
        init: function() { /* ... */ }
    };
});

// 4. ESM (ES6, 2015) — стандарт
// math.js
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;
// app.js
import { add, subtract } from './math.js';
```

### CommonJS vs ESM

| Аспект | CommonJS | ESM |
|--------|----------|-----|
| **Синтаксис** | `require()`, `module.exports` | `import`, `export` |
| **Загрузка** | Синхронная | Асинхронная |
| **Время анализа** | Runtime | Static (compile-time) |
| **Tree shaking** | ❌ Нет | ✅ Да |
| **Top-level await** | ❌ Нет | ✅ Да |
| **Где работает** | Node.js | Браузеры + Node.js |
| **Расширение** | `.js` или `.cjs` | `.mjs` или `"type": "module"` |

### ESM: детали

```javascript
// Named exports
export const PI = 3.14159;
export function calculate(x) { return x * PI; }
export class Calculator { /* ... */ }

// Default export (один на файл)
export default class MainCalculator { /* ... */ }

// Re-exports
export { add, subtract } from './math.js';
export * from './utils.js';
export { default as Utils } from './utils.js';

// Import variations
import { add, subtract } from './math.js';      // Named
import * as math from './math.js';              // Namespace
import Calculator from './Calculator.js';        // Default
import Calculator, { utils } from './calc.js';  // Mixed
import './side-effects.js';                     // Side effects only

// Dynamic import (lazy loading)
const module = await import('./heavy-module.js');
```

### Kotlin Multiplatform

```kotlin
// commonMain — общий код
expect class Platform {
    val name: String
}

expect fun httpClient(): HttpClient

// androidMain — Android реализация
actual class Platform {
    actual val name: String = "Android ${Build.VERSION.SDK_INT}"
}

actual fun httpClient(): HttpClient = OkHttpClient()

// iosMain — iOS реализация
actual class Platform {
    actual val name: String = UIDevice.current.systemName
}

actual fun httpClient(): HttpClient = NSURLSessionClient()
```

### Java Platform Module System (JPMS)

```java
// module-info.java
module com.myapp.core {
    requires java.base;           // Зависимость
    requires transitive java.sql; // Транзитивная зависимость

    exports com.myapp.core.api;   // Публичный API
    exports com.myapp.core.spi to com.myapp.plugins; // Ограниченный экспорт

    opens com.myapp.core.internal to com.google.gson; // Для рефлексии

    uses com.myapp.core.spi.Plugin;     // Использует сервис
    provides com.myapp.core.spi.Plugin  // Предоставляет реализацию
        with com.myapp.plugins.DefaultPlugin;
}
```

---

## Частые ошибки: 6 проблем

### ❌ Ошибка 1: Циклические зависимости

**Симптом:** `ReferenceError: Cannot access 'X' before initialization`

```javascript
// ПЛОХО:
// user.js
import { getOrders } from './order.js';
export const getUser = (id) => ({ id, orders: getOrders(id) });

// order.js
import { getUser } from './user.js';  // Цикл!
export const getOrders = (userId) => {
    const user = getUser(userId);  // Undefined!
    return user.orders;
};

// ХОРОШО — выделить общее:
// types.js
export interface User { id: string; }
export interface Order { userId: string; }

// user.js
import { User } from './types.js';
export const getUser = (id): User => { /* ... */ };

// order.js
import { Order } from './types.js';
export const getOrders = (userId): Order[] => { /* ... */ };
```

**Решение:** Dependency Inversion — зависеть от абстракций, не от конкретных модулей.

---

### ❌ Ошибка 2: Barrel files с re-exports

**Симптом:** Медленная сборка, большой бандл

```javascript
// ПЛОХО — barrel file:
// components/index.js
export { Button } from './Button';
export { Input } from './Input';
export { Modal } from './Modal';
// ... 100 компонентов

// Импорт ОДНОГО компонента тянет ВСЕ
import { Button } from './components';  // Загружает 100 файлов!

// ХОРОШО — прямой импорт:
import { Button } from './components/Button';
```

**Решение:** Используй прямые импорты или настрой sideEffects в package.json.

---

### ❌ Ошибка 3: CommonJS в ESM проекте

**Симптом:** `require is not defined`, `module is not defined`

```javascript
// ПЛОХО — смешение:
// ESM файл
import express from 'express';
const config = require('./config');  // ❌ Ошибка!

// ХОРОШО — только ESM:
import express from 'express';
import config from './config.js';

// Или явное преобразование:
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const legacyModule = require('./legacy-commonjs');
```

**Решение:** Не смешивай системы или используй createRequire для legacy.

---

### ❌ Ошибка 4: Огромные модули (God modules)

**Симптом:** Файл на 5000+ строк, всё импортирует один модуль

```javascript
// ПЛОХО — utils.js на 3000 строк:
export const formatDate = () => {};
export const formatCurrency = () => {};
export const validateEmail = () => {};
export const calculateTax = () => {};
export const encryptPassword = () => {};
// ... 100 функций

// ХОРОШО — разбить по ответственности:
// date/formatters.js
export const formatDate = () => {};

// currency/formatters.js
export const formatCurrency = () => {};

// validation/email.js
export const validateEmail = () => {};
```

**Решение:** Single Responsibility — один модуль = одна ответственность.

---

### ❌ Ошибка 5: Отсутствие явных зависимостей

**Симптом:** Модуль работает только в определённом контексте

```javascript
// ПЛОХО — неявная зависимость от глобального:
export function saveUser(user) {
    return window.fetch('/api/users', {  // ❌ Зависит от window
        method: 'POST',
        body: JSON.stringify(user)
    });
}

// ХОРОШО — явная зависимость:
export function createUserService(httpClient) {
    return {
        saveUser: (user) => httpClient.post('/api/users', user)
    };
}

// Использование:
const userService = createUserService(axiosClient);
```

**Решение:** Dependency Injection — передавай зависимости явно.

---

### ❌ Ошибка 6: Экспорт изменяемого состояния

**Симптом:** Непредсказуемое поведение, race conditions

```javascript
// ПЛОХО — мутируемый экспорт:
// state.js
export let currentUser = null;
export function setUser(user) { currentUser = user; }

// a.js
import { currentUser, setUser } from './state';
setUser({ name: 'Alice' });

// b.js
import { currentUser } from './state';
console.log(currentUser);  // Зависит от порядка загрузки!

// ХОРОШО — инкапсулировать состояние:
// store.js
let state = { currentUser: null };

export const getUser = () => state.currentUser;
export const setUser = (user) => { state.currentUser = user; };
export const subscribe = (callback) => { /* ... */ };
```

**Решение:** Не экспортируй мутируемое состояние, используй getters/setters.

---

## Ментальные модели: 5 принципов

### 1. Cohesion vs Coupling

```
HIGH COHESION (хорошо):
  Модуль делает ОДНО дело хорошо
  Все части модуля связаны логически

  user-service.js:
  - getUser()
  - createUser()
  - updateUser()
  - deleteUser()
  ← Всё про users!

LOW COUPLING (хорошо):
  Модули минимально зависят друг от друга
  Изменение в A не ломает B

  A ──interface──► B
     (не impl!)
```

### 2. Принцип наименьшего знания

```
Модуль должен знать МИНИМУМ о других модулях

ПЛОХО:
  import { userService } from './services';
  userService.database.connection.query('...');  // Знает слишком много!

ХОРОШО:
  import { getUser } from './services/user';
  const user = getUser(id);  // Знает только публичный API
```

### 3. Stable Abstractions Principle

```
Стабильные модули должны быть абстрактными
Нестабильные могут быть конкретными

         Абстрактный ←───────────────→ Конкретный
              │                              │
          interfaces/                    src/
          types/                         components/
              │                              │
         Редко меняется              Часто меняется
              │                              │
          Много зависящих            Мало зависящих
```

### 4. Acyclic Dependencies

```
Зависимости должны быть АЦИКЛИЧЕСКИМИ (DAG)

✅ ХОРОШО:
  A → B → C → D
      ↓
      E

❌ ПЛОХО:
  A → B → C
  ↑       │
  └───────┘
```

### 5. Interface Segregation для модулей

```
Лучше много маленьких интерфейсов, чем один большой

// ПЛОХО:
import { everything } from './mega-utils';

// ХОРОШО:
import { formatDate } from './date-utils';
import { validateEmail } from './validation';
import { encrypt } from './crypto';
```

---

## Проверь себя

**Вопрос 1:** Почему ESM поддерживает tree shaking, а CommonJS нет?

<details>
<summary>Ответ</summary>

ESM анализируется статически (на этапе компиляции), поэтому бандлер ЗНАЕТ какие экспорты используются и может удалить неиспользуемые.

CommonJS анализируется динамически (в runtime), поэтому бандлер НЕ МОЖЕТ определить какие части `module.exports` будут использованы:

```javascript
// CommonJS — динамический
const key = condition ? 'a' : 'b';
module.exports[key] = value;  // Невозможно статически определить!

// ESM — статический
export const a = 1;  // Бандлер точно знает что экспортируется
export const b = 2;
```
</details>

**Вопрос 2:** Как решить циклическую зависимость между модулями A и B?

<details>
<summary>Ответ</summary>

1. **Выделить общую часть в модуль C:**
   ```
   A → C ← B  // Вместо A ↔ B
   ```

2. **Dependency Inversion:**
   ```
   A → Interface ← B implements
   ```

3. **Lazy import:**
   ```javascript
   // Вместо top-level import
   export async function useB() {
       const { B } = await import('./B');
       return B;
   }
   ```

4. **Пересмотреть архитектуру:**
   Циклические зависимости часто указывают на нарушение SRP.
</details>

---

## Связи

- [[build-systems-theory]] — как собираются модули
- [[dependency-resolution]] — как разрешаются зависимости
- [[clean-code-solid]] — принципы проектирования
- [[kmp-source-sets]] — модульность в Kotlin Multiplatform

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [MDN: JavaScript Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules) | Docs | ESM reference |
| 2 | [Node.js ESM](https://nodejs.org/api/esm.html) | Docs | Node.js specifics |
| 3 | [Clean Architecture (Martin)](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164) | Book | Модульность принципы |

---

*Проверено: 2026-01-09*

---

[[programming-overview|← Programming]] | [[build-systems-theory|Build Systems →]]

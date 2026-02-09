---
title: "Web Security: OWASP Top 10 и защита приложений"
created: 2025-11-24
modified: 2025-11-24
type: concept
status: verified
confidence: high
sources_verified: true
tags:
  - security/web
  - security/owasp
  - backend/security
related:
  - "[[api-design]]"
  - "[[ci-cd-pipelines]]"
  - "[[network-dns-tls]]"
  - "[[network-http-evolution]]"
---

# Web Security: OWASP Top 10 и защита приложений

~50% приложений содержат минимум одну уязвимость из OWASP Top 10. Средняя стоимость утечки: $4.45 млн. #1 — Broken Access Control (доступ к чужим данным). Безопасность — не фича, а требование.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **OWASP** | Open Web Application Security Project |
| **IDOR** | Insecure Direct Object Reference — доступ к чужим объектам |
| **XSS** | Cross-Site Scripting — внедрение скриптов |
| **CSRF** | Cross-Site Request Forgery — подделка запросов |
| **SQL Injection** | Внедрение SQL-кода в запросы |
| **Supply Chain** | Атаки через зависимости (npm, pip) |
| **Sanitization** | Очистка ввода от опасных символов |
| **WAF** | Web Application Firewall |

---

## Почему это важно: цифры

```
Статистика 2024-2025:

• 2.8 млн приложений проанализировано для OWASP 2025
• ~50% приложений имеют минимум 1 уязвимость из Top 10
• 55% утечек данных — украденные credentials
• 10+ млн секретов утекло в публичные репозитории (2024)
• Средняя стоимость утечки: $4.45 млн (IBM, 2023)
```

---

## OWASP Top 10:2025

```
┌────┬──────────────────────────────────┬─────────────────┐
│ #  │ Уязвимость                       │ Изменение       │
├────┼──────────────────────────────────┼─────────────────┤
│ 01 │ Broken Access Control            │ ▲ был #5 (2017) │
│ 02 │ Cryptographic Failures           │ ▼ был #2        │
│ 03 │ Software Supply Chain Failures   │ ★ НОВОЕ         │
│ 04 │ Injection                        │ ▼ был #3        │
│ 05 │ Insecure Design                  │ ▼ был #4        │
│ 06 │ Security Misconfiguration        │ ▲ вырос         │
│ 07 │ Authentication Failures          │ = на месте      │
│ 08 │ Software/Data Integrity Failures │ = на месте      │
│ 09 │ Logging & Monitoring Failures    │ = на месте      │
│ 10 │ Mishandling Exceptional Cond.    │ ★ НОВОЕ         │
└────┴──────────────────────────────────┴─────────────────┘
```

---

## A01: Broken Access Control

**Что это:** Пользователь получает доступ к чужим данным или функциям.

```
Пример атаки — IDOR (Insecure Direct Object Reference):

GET /api/users/123/orders     ← Твой ID = 123
200 OK: [твои заказы]

GET /api/users/456/orders     ← Чужой ID = 456
200 OK: [ЧУЖИЕ заказы]        ← Уязвимость!

Проблема: Сервер не проверяет, принадлежит ли ресурс пользователю
```

### Защита

```javascript
// ❌ Плохо: проверка только на фронтенде
app.get('/api/users/:id/orders', (req, res) => {
  const orders = db.getOrders(req.params.id);
  res.json(orders);
});

// ✅ Хорошо: проверка на бэкенде
app.get('/api/users/:id/orders', authenticate, (req, res) => {
  // Проверяем, что пользователь запрашивает СВОИ данные
  if (req.params.id !== req.user.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const orders = db.getOrders(req.params.id);
  res.json(orders);
});
```

```
Чеклист защиты Access Control:

□ Deny by default (запрещено всё, что не разрешено явно)
□ Проверка прав на КАЖДОМ endpoint
□ Централизованный механизм авторизации
□ Логирование всех отказов в доступе
□ Rate limiting на чувствительные endpoints
□ Отключить directory listing на сервере
□ JWT/Session tokens не хранить в URL
```

---

## A03: Software Supply Chain Failures (НОВОЕ)

**Что это:** Уязвимости в зависимостях, CI/CD pipeline, или процессе сборки.

```
Реальные инциденты:

2021: ua-parser-js (npm)
      └── 8 млн загрузок/неделю
      └── Криптомайнер в зависимости
      └── Автоматически попал в тысячи проектов

2020: SolarWinds
      └── Malware в официальном обновлении
      └── 18,000 организаций скомпрометировано
      └── Включая госорганы США

2024: xz-utils backdoor
      └── Почти попал в major Linux дистрибутивы
      └── Обнаружен случайно
```

### Защита

```yaml
# 1. Сканирование зависимостей в CI
- name: Dependency Review
  uses: actions/dependency-review-action@v4
  with:
    fail-on-severity: high

# 2. Lock файлы — обязательно
package-lock.json  # npm
yarn.lock          # yarn
Pipfile.lock       # Python
go.sum             # Go

# 3. Dependabot / Renovate для автообновлений
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
```

```
Чеклист Supply Chain Security:

□ Lock-файлы в git
□ Автоматическое сканирование зависимостей
□ Минимальное количество зависимостей
□ Проверенные источники пакетов
□ Подпись артефактов
□ SBOM (Software Bill of Materials)
□ Изолированные CI runners
```

---

## A04: Injection

**Что это:** Вредоносные данные интерпретируются как код.

### SQL Injection

```javascript
// ❌ УЯЗВИМО: конкатенация строк
const query = `SELECT * FROM users WHERE email = '${email}'`;

// Атака:
// email = "'; DROP TABLE users; --"
// Результат: SELECT * FROM users WHERE email = ''; DROP TABLE users; --'

// ✅ БЕЗОПАСНО: параметризованные запросы
const query = 'SELECT * FROM users WHERE email = $1';
const result = await db.query(query, [email]);
```

### Command Injection

```javascript
// ❌ УЯЗВИМО
const { exec } = require('child_process');
exec(`convert ${userInput}.png output.jpg`);

// Атака: userInput = "image; rm -rf /"

// ✅ БЕЗОПАСНО: экранирование или whitelist
const { execFile } = require('child_process');
const allowedFiles = ['image1', 'image2', 'image3'];
if (!allowedFiles.includes(userInput)) {
  throw new Error('Invalid file');
}
execFile('convert', [`${userInput}.png`, 'output.jpg']);
```

### XSS (Cross-Site Scripting)

```javascript
// ❌ УЯЗВИМО: вставка пользовательского HTML
document.innerHTML = `<div>${userComment}</div>`;

// Атака: userComment = "<script>stealCookies()</script>"

// ✅ БЕЗОПАСНО: экранирование
document.textContent = userComment;
// Или используй фреймворк (React, Vue автоматически экранируют)
```

```
Чеклист защиты от Injection:

□ Параметризованные запросы (SQL)
□ ORM вместо raw SQL где возможно
□ Input validation (whitelist, не blacklist)
□ Output encoding (HTML, JS, URL)
□ Content Security Policy (CSP)
□ Избегать eval(), exec(), shell commands
□ Минимальные привилегии для DB user
```

---

## A07: Authentication Failures

**Что это:** Слабая аутентификация позволяет захватить аккаунт.

```
Типичные уязвимости:

• Слабые пароли: "password123", "qwerty"
• Credential stuffing: утекшие пароли с других сайтов
• Brute force: перебор без rate limiting
• Session fixation: предсказуемые session ID
• Отсутствие MFA
```

### Защита

```javascript
// Rate limiting для login
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 минут
  max: 5,                     // 5 попыток
  message: 'Too many login attempts',
  standardHeaders: true,
});

app.post('/login', loginLimiter, async (req, res) => {
  // ...
});
```

```javascript
// Безопасное хеширование паролей
const bcrypt = require('bcrypt');

// При регистрации
const hash = await bcrypt.hash(password, 12);  // cost factor = 12

// При логине
const isValid = await bcrypt.compare(password, storedHash);
```

```
Чеклист Authentication:

□ bcrypt/argon2 для хешей паролей (НЕ MD5/SHA1)
□ Минимум 12 символов для паролей
□ Rate limiting на login
□ Account lockout после N попыток
□ MFA для критичных операций
□ Secure session management
□ Password reset через email token (не security questions)
□ Проверка паролей против breach databases
```

---

## Практические инструменты

### Статический анализ (SAST)

```yaml
# В CI/CD pipeline
- name: CodeQL Analysis
  uses: github/codeql-action/analyze@v3
  with:
    languages: javascript, python

# Или локально
npm install -g snyk
snyk test                # Проверить зависимости
snyk code test           # Проверить код
```

### Динамический анализ (DAST)

```bash
# OWASP ZAP — бесплатный сканер
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://your-site.com

# Burp Suite — для ручного тестирования
```

### Security Headers

```javascript
// Express.js с helmet
const helmet = require('helmet');
app.use(helmet());

// Добавляет:
// X-Content-Type-Options: nosniff
// X-Frame-Options: DENY
// Content-Security-Policy: ...
// Strict-Transport-Security: ...
```

```nginx
# Nginx
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Strict-Transport-Security "max-age=31536000" always;
```

---

## Подводные камни

### Проблема 1: "Security by obscurity"

```
❌ Плохая защита:
• Скрытые URL (/admin-secret-panel-2024)
• Кастомный "шифрование" на JS
• "Никто не догадается проверить..."

✅ Настоящая защита:
• Стандартные алгоритмы (AES, RSA)
• Defense in depth (многослойная защита)
• Assume breach (предполагай что уже взломали)
```

### Проблема 2: Безопасность ≠ UX

```
Конфликт:
• Длинные пароли → пользователи записывают на бумажке
• MFA на каждый логин → отключают где возможно
• CAPTCHA везде → уходят к конкурентам

Баланс:
• Risk-based authentication (MFA только при подозрительном входе)
• Passwordless где возможно (magic links, WebAuthn)
• Friction пропорционален риску
```

### Проблема 3: "Мы используем HTTPS"

```
HTTPS ≠ безопасность

HTTPS защищает:              HTTPS НЕ защищает:
────────────────────         ────────────────────
• Трафик в пути              • SQL injection
• Man-in-the-middle          • XSS
• Перехват данных            • Broken access control
                             • Server-side уязвимости
                             • Утечку через логи
```

---

## Actionable

**Сегодня:**
- Добавь `helmet` или security headers
- Проверь, используешь ли параметризованные SQL-запросы
- Проверь rate limiting на login

**Эта неделя:**
- Запусти `npm audit` / `snyk test`
- Добавь dependency scanning в CI
- Проверь access control на API endpoints

**Этот месяц:**
- Пройди OWASP Top 10 по чеклисту
- Настрой SAST в CI/CD
- Проведи security review критичных endpoints

---

## Связи

- API Security: [[api-design]]
- DevSecOps в CI/CD: [[ci-cd-pipelines]]

---

## Источники

- [OWASP Top 10:2025 RC1](https://owasp.org/Top10/2025/0x00_2025-Introduction/) — проверено 2025-11-24
- [OWASP Foundation: Top Ten](https://owasp.org/www-project-top-ten/) — проверено 2025-11-24
- [GBHackers: OWASP Top 10 2025 Released](https://gbhackers.com/owasp-top-10-2025-released/) — проверено 2025-11-24
- [Veracode: OWASP Top 10 Vulnerabilities](https://www.veracode.com/security/owasp-top-10/) — проверено 2025-11-24

---

**Последняя верификация**: 2025-11-24
**Уровень достоверности**: high

---

*Проверено: 2026-01-09*

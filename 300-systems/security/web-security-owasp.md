---
title: "Web Security: OWASP Top 10 и защита приложений"
created: 2025-11-24
modified: 2025-11-24
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/security
  - security/web
  - security/owasp
  - backend/security
  - type/concept
  - level/intermediate
related:
  - "[[api-design]]"
  - "[[ci-cd-pipelines]]"
  - "[[network-dns-tls]]"
  - "[[network-http-evolution]]"
prerequisites:
  - "[[security-fundamentals]]"
  - "[[authentication-authorization]]"
reading_time: 9
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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

## Связь с другими темами

[[api-design]] — проектирование API напрямую определяет поверхность атаки веб-приложения. Broken Access Control (A01), Injection (A04) и Authentication Failures (A07) чаще всего эксплуатируются именно через API endpoints. Знание принципов безопасного проектирования API (rate limiting, input validation, proper authorization) является практическим применением защиты от OWASP Top 10. Рекомендуется изучать параллельно.

[[ci-cd-pipelines]] — интеграция SAST/DAST-инструментов (CodeQL, Snyk, OWASP ZAP) в CI/CD pipeline позволяет автоматически обнаруживать уязвимости из OWASP Top 10 на каждом этапе разработки. Supply Chain Failures (A03) также требуют защиты самого pipeline от компрометации. DevSecOps-подход превращает разовые проверки безопасности в непрерывный процесс.

[[authentication-authorization]] — глубокое понимание механизмов AuthN/AuthZ критично для защиты от A01 (Broken Access Control) и A07 (Authentication Failures), которые составляют две из десяти ключевых категорий OWASP Top 10. Правильная реализация OAuth 2.0, JWT, RBAC и MFA является основной контрмерой для этих уязвимостей. Рекомендуется как обязательный prerequisite перед OWASP Top 10.

[[security-fundamentals]] — базовые принципы безопасности (CIA Triad, Defense in Depth, Least Privilege, Assume Breach) формируют мышление, необходимое для понимания OWASP Top 10. Каждая категория Top 10 нарушает один или несколько принципов CIA, и понимание этой связи помогает приоритизировать контрмеры и строить многослойную защиту.

[[threat-modeling]] — threat modeling предоставляет методологию систематического выявления уязвимостей из OWASP Top 10 на этапе проектирования. Категории STRIDE напрямую соответствуют категориям Top 10: Spoofing связан с A07, Tampering с A08, Information Disclosure с A02. Threat modeling на раннем этапе дешевле, чем исправление уязвимостей в production.

---

## Источники и дальнейшее чтение

- Stuttard D., Pinto M. (2011). *The Web Application Hacker's Handbook: Finding and Exploiting Security Flaws.* 2nd Edition. Wiley. — практическое руководство по обнаружению и эксплуатации веб-уязвимостей, покрывающее все категории OWASP Top 10 с детальными примерами.
- Anderson R. (2020). *Security Engineering: A Guide to Building Dependable Distributed Systems.* 3rd Edition. Wiley. — фундаментальный труд по инженерии безопасности, включая веб-безопасность в контексте проектирования распределённых систем.
- Seitz J. (2021). *Black Hat Go: Go Programming for Hackers and Pentesters.* No Starch Press. — для понимания инструментов тестирования безопасности и автоматизации проверок OWASP Top 10.
- OWASP Foundation (2021). *OWASP Testing Guide v4.* — официальное руководство по тестированию безопасности веб-приложений, систематически покрывающее все категории OWASP Top 10.

---

*Проверено: 2026-01-09*

---

## Проверь себя

> [!question]- Почему HTTPS сам по себе не защищает от большинства уязвимостей OWASP Top 10?
> HTTPS защищает только канал передачи данных (шифрование трафика, защита от man-in-the-middle). Он не влияет на серверную логику: SQL Injection, Broken Access Control, XSS и другие уязвимости эксплуатируются уже внутри установленного защищённого соединения. HTTPS — один слой в модели Defense in Depth, но не замена валидации ввода, авторизации и безопасного кодирования.

> [!question]- В API есть endpoint `GET /api/documents/:id`. Аутентификация реализована через JWT, токен проверяется middleware. Пользователь A может получить документ пользователя B, подставив чужой id. Какую категорию OWASP Top 10 нарушает этот endpoint и какой минимальный fix нужен?
> Это A01: Broken Access Control (конкретно — IDOR). JWT подтверждает личность пользователя (AuthN), но не проверяет, принадлежит ли запрашиваемый ресурс этому пользователю (AuthZ). Минимальный fix: на бэкенде сверять `req.user.id` с владельцем документа из базы данных и возвращать 403 Forbidden при несовпадении. Проверка должна быть на сервере, а не на фронтенде.

> [!question]- Команда подключила популярную npm-библиотеку для форматирования дат (5 млн загрузок/неделю). Через месяц в её транзитивной зависимости обнаружился криптомайнер. Как связана эта ситуация с CI/CD pipeline и какие конкретные меры из OWASP Top 10 предотвратили бы инцидент?
> Это A03: Software Supply Chain Failures. Меры предотвращения: 1) lock-файлы в git фиксируют точные версии зависимостей; 2) `dependency-review-action` или Snyk в CI блокирует сборку при обнаружении уязвимости; 3) Dependabot/Renovate автоматически создаёт PR на обновление; 4) SBOM позволяет быстро найти все проекты с заражённой зависимостью. Это пересекается с [[ci-cd-pipelines]], где SAST/DAST интегрируются в pipeline как обязательный шаг.

> [!question]- Разработчик использует ORM и считает, что SQL Injection ему не грозит. Проанализируйте: в каких случаях ORM всё равно уязвим к инъекциям и какие дополнительные слои защиты необходимы?
> ORM уязвим когда: 1) разработчик использует raw SQL запросы внутри ORM (например, `sequelize.query()` с конкатенацией строк); 2) динамическое формирование условий WHERE из пользовательского ввода без санитизации; 3) ORM-методы, принимающие JSON-объекты напрямую из request body (mass assignment). Дополнительные слои: input validation (whitelist), минимальные привилегии для DB user, Content Security Policy, WAF и логирование аномальных запросов. Defense in Depth — ни один слой не должен быть единственным.

---

## Ключевые карточки

Что такое OWASP Top 10 и почему это важен для разработчика?
?
Это рейтинг 10 критических категорий уязвимостей веб-приложений, составляемый OWASP на основе анализа миллионов приложений. Около 50% приложений содержат минимум одну уязвимость из списка. Средняя стоимость утечки — $4.45 млн.

Какая уязвимость занимает первое место в OWASP Top 10:2025?
?
A01: Broken Access Control — когда пользователь получает доступ к чужим данным или функциям. Типичный пример — IDOR: подмена ID в URL для доступа к чужим ресурсам без серверной проверки принадлежности.

Что такое IDOR и как от него защититься?
?
Insecure Direct Object Reference — доступ к чужим объектам через подмену идентификатора в запросе. Защита: на бэкенде проверять, что запрашиваемый ресурс принадлежит аутентифицированному пользователю, и применять принцип deny by default.

Почему параметризованные SQL-запросы защищают от SQL Injection?
?
Параметризованные запросы разделяют код и данные: база данных сначала компилирует SQL-шаблон, а затем подставляет параметры как значения, не интерпретируя их как SQL-код. Конкатенация строк смешивает код и данные, позволяя атакующему внедрить произвольные SQL-команды.

Что нового в OWASP Top 10:2025 по сравнению с предыдущими версиями?
?
Две новые категории: A03 Software Supply Chain Failures (атаки через зависимости, CI/CD) и A10 Mishandling Exceptional Conditions. Broken Access Control поднялся на первое место. Supply Chain отражает рост атак через npm/pip-пакеты (ua-parser-js, xz-utils).

Какие инструменты используются для автоматического обнаружения уязвимостей OWASP?
?
SAST (статический анализ): CodeQL, Snyk — проверяют исходный код. DAST (динамический анализ): OWASP ZAP, Burp Suite — сканируют работающее приложение. Оба типа интегрируются в CI/CD pipeline для непрерывной проверки безопасности.

Почему принцип "Security by obscurity" не работает?
?
Скрытые URL, кастомное шифрование и надежда что «никто не найдёт» не являются защитой. Настоящая безопасность строится на стандартных алгоритмах (AES, RSA), Defense in Depth (многослойная защита) и принципе Assume Breach (предполагай, что уже взломали).

Какие меры защиты от Authentication Failures (A07) наиболее критичны?
?
Хеширование паролей через bcrypt/argon2 (не MD5/SHA1), rate limiting на login endpoint, MFA для критичных операций, проверка паролей против breach databases. Password reset — только через email token, не через security questions.

Как Supply Chain атака попадает в проект и как от неё защититься?
?
Через заражённые зависимости (npm, pip), скомпрометированный CI/CD pipeline или вредоносные обновления. Защита: lock-файлы в git, автоматическое сканирование зависимостей в CI, минимизация зависимостей, SBOM и изолированные CI runners.

Что такое Content Security Policy (CSP) и от какой уязвимости она защищает?
?
CSP — HTTP-заголовок, указывающий браузеру, из каких источников разрешено загружать скрипты, стили и другие ресурсы. Основная защита от XSS: даже если атакующий внедрит `<script>`, браузер не выполнит его, если источник не в whitelist CSP.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Фундамент безопасности | [[security-fundamentals]] | Принципы CIA Triad, Defense in Depth и Least Privilege — основа понимания каждой категории OWASP Top 10 |
| Аутентификация и авторизация | [[authentication-authorization]] | Глубокое понимание AuthN/AuthZ для защиты от A01 и A07 — двух из трёх самых частых уязвимостей |
| Моделирование угроз | [[threat-modeling]] | Методология STRIDE для систематического выявления уязвимостей OWASP на этапе проектирования |
| Проектирование API | [[api-design]] | API endpoints — основная поверхность атаки; принципы безопасного проектирования предотвращают Injection и Broken Access Control |
| DevSecOps в CI/CD | [[ci-cd-pipelines]] | Интеграция SAST/DAST в pipeline превращает разовые проверки в непрерывный процесс обнаружения уязвимостей |
| DNS и TLS | [[network-dns-tls]] | Понимание TLS/HTTPS на уровне протокола — почему HTTPS необходим, но недостаточен для полной защиты |
| Эволюция HTTP | [[network-http-evolution]] | HTTP/2, HTTP/3 и security headers — транспортный уровень, на котором работают все веб-уязвимости |

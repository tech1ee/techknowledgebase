---
title: "Security MOC"
created: 2025-11-24
modified: 2025-12-18
type: moc
tags:
  - topic/security
  - type/moc
  - navigation
---

# Security MOC

> Безопасность приложений, OWASP, DevSecOps — с чего начать и как приоритизировать

---

## Быстрая навигация

- **Новичок в безопасности?** → Раздел "С чего начать" ниже
- **Ищешь OWASP Top 10?** → Раздел "OWASP Top 10:2025 — приоритеты"
- **Внедряешь DevSecOps?** → Раздел "DevSecOps Roadmap"
- **Настраиваешь авторизацию?** → [[authentication-authorization]] (навигационный хаб)

---

## Статьи

### Web Security
- [[web-security-owasp]] — OWASP Top 10:2025, защита от инъекций, access control, supply chain

### Authentication & Authorization
- [[authentication-authorization]] — навигационный хаб: обзор и выбор подхода к аутентификации
- [[auth-sessions-jwt-tokens]] — Sessions, JWT, opaque tokens: механизмы и безопасность токенов
- [[auth-oauth2-oidc]] — OAuth 2.0/2.1, OpenID Connect, PKCE, социальный логин
- [[auth-authorization-models]] — RBAC, ABAC, ReBAC: модели контроля доступа и policy engines
- [[auth-passwordless-mfa]] — Passkeys/WebAuthn, MFA, пароли: современная аутентификация
- [[auth-enterprise-sso]] — SAML, Kerberos, SSO: корпоративная аутентификация и федерация
- [[auth-api-service-patterns]] — API keys, mTLS, Zero Trust: аутентификация сервисов и API

---

## С чего начать: приоритизация безопасности

**Почему это важно:** 87% нарушений безопасности происходят из-за базовых проблем (OWASP). Начни с основ, не с экзотики.

### Дорожная карта по уровню зрелости

```
Уровень 1: Базовая гигиена (первые шаги)
├── Secure coding guidelines для команды
├── Обновление зависимостей (npm audit, Dependabot)
├── HTTPS везде + правильные заголовки безопасности
└── Базовый контроль доступа (AuthN + AuthZ)

Уровень 2: Автоматизация (следующий шаг)
├── SAST в CI/CD (SonarQube, Semgrep)
├── Сканирование зависимостей (Snyk, OWASP Dependency-Check)
├── Secret scanning (git-secrets, truffleHog)
└── Базовое логирование security events

Уровень 3: Зрелый DevSecOps
├── DAST (OWASP ZAP, Burp Suite)
├── Container scanning (Trivy, Clair)
├── Threat modeling для критичных фич
└── Security testing в acceptance criteria
```

### Что даёт максимальный ROI

| Практика | Усилия | Защита от |
|----------|--------|-----------|
| **Обновление зависимостей** | Низкие | Supply Chain (#3 OWASP) |
| **Параметризованные запросы** | Низкие | Injection (#5 OWASP) |
| **Проверка доступа на сервере** | Средние | Broken Access Control (#1) |
| **SAST в CI** | Средние | Многие уязвимости |
| **Threat modeling** | Высокие | Insecure Design (#6) |

---

## OWASP Top 10:2025 — приоритеты и связи

**Контекст:** OWASP Top 10:2025 RC опубликован в ноябре 2025. Supply Chain атаки ускоряются: с 13/месяц в начале 2024 до 25/месяц в 2025.

### Рейтинг 2025

| # | Категория | Изменение | Главная защита |
|---|-----------|-----------|----------------|
| 1 | **Broken Access Control** | = | Проверяй доступ на сервере, не на клиенте |
| 2 | **Security Misconfiguration** | ↑ | Default deny, hardened configs |
| 3 | **Software Supply Chain** | 🆕 | Lockfiles, signing, SBOM |
| 4 | **Cryptographic Failures** | ↓ | TLS 1.3, bcrypt/Argon2 |
| 5 | **Injection** | ↓ | Параметризация, валидация |
| 6 | **Insecure Design** | ↓ | Threat modeling |
| 7 | **Authentication Failures** | = | MFA, secure session management |
| 8 | **Software/Data Integrity** | = | Signatures, checksums |
| 9 | **Logging/Alerting Failures** | = | Structured logging, SIEM |
| 10 | **Mishandling Exceptions** | 🆕 | Error handling, fail secure |

### Как категории связаны между собой

```
┌─────────────────────────────────────────────────────────────┐
│                   OWASP Top 10 Relationships                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Supply Chain (#3) ──усугубляет──→ Injection (#5)          │
│       │                                                     │
│       └──────────────────→ Broken Access Control (#1)       │
│                                                             │
│  Insecure Design (#6) ──root cause──→ Access Control (#1)  │
│                       ──root cause──→ Injection (#5)        │
│                                                             │
│  Logging Failures (#9) ──маскирует──→ ВСЕ атаки            │
│                                                             │
│  Misconfiguration (#2) ──enables──→ Access Control (#1)    │
│                        ──enables──→ Crypto Failures (#4)    │
└─────────────────────────────────────────────────────────────┘
```

**Вывод:** Начни с Insecure Design (threat modeling) — это root cause многих уязвимостей.

---

## DevSecOps Roadmap

**Рынок:** DevSecOps вырос с $3.73B (2021) до прогнозируемых $41.66B (2030), CAGR >30%.

### Фазы внедрения

**Фаза 1: Quick Wins (1-2 месяца)**
- Dependabot/Renovate для обновления зависимостей
- Secret scanning в pre-commit hooks
- Security-aware code review checklist

**Фаза 2: CI/CD Integration (2-4 месяца)**
- SAST инструмент (Semgrep — бесплатный и быстрый)
- Container scanning (Trivy — бесплатный)
- Security gates в pipeline (блокировка на critical)

**Фаза 3: Культура (ongoing)**
- Security champions в каждой команде
- Threat modeling для новых фич
- Bug bounty или регулярный pentest

### Ключевые метрики DevSecOps

| Метрика | Что измеряет | Цель |
|---------|--------------|------|
| **MTTR** | Время устранения уязвимости | <7 дней для critical |
| **False Positive Rate** | Качество инструментов | <10% |
| **Security Debt** | Накопленные уязвимости | Уменьшается каждый спринт |
| **Time to Detection** | Скорость обнаружения | В CI, не в production |

---

## Ключевые концепции

| Концепция | Суть | Приоритет | Подробнее |
|-----------|------|-----------|-----------|
| **Broken Access Control** | #1 уязвимость — проверяй на сервере | 🔴 Critical | [[web-security-owasp]] |
| **Supply Chain Security** | 🆕 #3 — защита зависимостей | 🔴 Critical | [[web-security-owasp]] |
| **Injection** | SQL, XSS, Command injection | 🟠 High | [[web-security-owasp]] |
| **SAST/DAST** | Статический + динамический анализ | 🟠 High | [[web-security-owasp]] |
| **JWT** | Stateless токены для API | 🟡 Medium | [[auth-sessions-jwt-tokens]] |
| **OAuth 2.0 / OIDC** | Делегирование доступа, identity layer | 🟡 Medium | [[auth-oauth2-oidc]] |
| **RBAC/ABAC/ReBAC** | Role/Attribute/Relationship access control | 🟠 High | [[auth-authorization-models]] |
| **Passkeys/WebAuthn** | Phishing-resistant passwordless auth | 🟠 High | [[auth-passwordless-mfa]] |
| **Argon2id/bcrypt** | Безопасное хеширование паролей | 🔴 Critical | [[auth-passwordless-mfa]] |
| **SAML/SSO** | Enterprise single sign-on | 🟡 Medium | [[auth-enterprise-sso]] |
| **mTLS/Zero Trust** | Service-to-service, verify always | 🟠 High | [[auth-api-service-patterns]] |

---

## Связанные темы

- [[api-design]] — Безопасность API: rate limiting, input validation, OAuth 2.0
- [[ci-cd-pipelines]] — DevSecOps: SAST/DAST/SCA в pipeline
- [[cloud-platforms-essentials]] — IAM, security groups, encryption at rest
- [[android-permissions-security]] — Мобильная безопасность (Android)
- [[network-dns-tls]] — TLS, сертификаты, HTTPS

---

## Источники

- [OWASP Top 10:2025 Introduction](https://owasp.org/Top10/2025/0x00_2025-Introduction/) — официальный источник
- [OWASP Top Ten Project](https://owasp.org/www-project-top-ten/) — главный проект OWASP
- [Black Duck DevSecOps Report 2024](https://www.blackduck.com/blog/black-duck-devsecops-report.html) — состояние индустрии
- [DevSecOps Roadmap 2025 - Practical DevSecOps](https://www.practical-devsecops.com/devsecops-roadmap/) — практическое руководство
- [OWASP Top 10:2025 - Reflectiz](https://www.reflectiz.com/blog/owasp-top-ten-2025/) — детальный разбор изменений

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 19 |
| Последнее обновление | 2026-02-11 |

---

*Проверено: 2025-12-18 | На основе OWASP Top 10:2025 RC, Black Duck DevSecOps Report 2024*

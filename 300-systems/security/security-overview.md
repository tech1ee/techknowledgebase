---
title: "Security: карта раздела"
created: 2025-12-22
modified: 2025-12-22
type: moc
status: published
area: security
confidence: high
tags:
  - topic/security
  - owasp
  - cryptography
  - type/moc
  - level/beginner
related:
  - "[[authentication-authorization]]"
  - "[[web-security-owasp]]"
  - "[[security-cryptography-fundamentals]]"
  - "[[security-https-tls]]"
  - "[[security-secrets-management]]"
  - "[[security-api-protection]]"
  - "[[security-incident-response]]"
reading_time: 6
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Security: карта раздела

> Security — не feature, а process. Думай как атакующий, защищай в глубину. Один breach может уничтожить компанию.

---

## Теоретические основы

> **Информационная безопасность** -- дисциплина, направленная на защиту информационных активов от несанкционированного доступа, использования, раскрытия, нарушения целостности, модификации или уничтожения (NIST SP 800-12, 1995).

### CIA Triad -- фундаментальная модель

Триада **Confidentiality -- Integrity -- Availability** формализована в стандарте DoD 5200.28-STD (Orange Book, 1985) и остаётся основой всех современных фреймворков безопасности: ISO 27001, NIST CSF 2.0, SOC 2.

| Свойство | Определение | Нарушение |
|----------|-------------|-----------|
| **Confidentiality** | Данные доступны только авторизованным субъектам | Утечка, перехват |
| **Integrity** | Данные не изменены несанкционированно | Подмена, tampering |
| **Availability** | Системы доступны в нужный момент | DoS, отказ оборудования |

### Defense in Depth -- стратегия эшелонированной обороны

Концепция заимствована из военной доктрины и адаптирована для ИБ в работах NSA (2000-е). Каждый слой защиты (сеть, хост, приложение, данные, человек) работает независимо -- компрометация одного не приводит к полному взлому.

### Принципы Saltzer & Schroeder (1975)

В статье *"The Protection of Information in Computer Systems"* (Proceedings of the IEEE, 1975) Джером Зальцер и Майкл Шрёдер сформулировали **8 принципов** проектирования безопасных систем:

| # | Принцип | Суть |
|---|---------|------|
| 1 | **Economy of mechanism** | Простота механизма защиты |
| 2 | **Fail-safe defaults** | Запрет по умолчанию (deny by default) |
| 3 | **Complete mediation** | Проверка каждого доступа |
| 4 | **Open design** | Безопасность не зависит от секретности механизма |
| 5 | **Separation of privilege** | Разделение привилегий |
| 6 | **Least privilege** | Минимально необходимые права |
| 7 | **Least common mechanism** | Минимум общих механизмов |
| 8 | **Psychological acceptability** | Простота использования |

Эти принципы предвосхитили [[security-fundamentals|Kerckhoffs' principle]] (Open design), [[security-secrets-management|Least Privilege]] и [[security-api-protection|Complete mediation]] в современных системах.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **HTTP/HTTPS** | Понимание веб-протоколов | [[network-http-evolution]] |
| **Базовое программирование** | Понимание уязвимостей в коде | Любой курс |
| **SQL basics** | SQL Injection — топ уязвимость | [[databases-fundamentals-complete]] |

### Терминология для новичков

> 💡 **Security mindset** = думать "как это можно сломать?" перед "как это работает?"

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **Authentication** | Кто ты? (логин/пароль) | **Паспортный контроль** — проверка документов |
| **Authorization** | Что тебе можно? | **Пропуск в офис** — куда можешь войти |
| **Encryption** | Шифрование данных | **Кодовый замок** — без ключа не прочитаешь |
| **XSS** | Cross-Site Scripting | **Подставной листок** — злоумышленник вставляет свой код |
| **SQL Injection** | Вставка SQL через input | **Поддельный ключ** — вместо имени вводят SQL команду |
| **MFA** | Multi-Factor Authentication | **Два замка** — пароль + SMS код |
| **Zero Trust** | Не доверяй никому по умолчанию | **Проверяй всех**, даже "своих" |

---

## TL;DR

- **Authentication** — кто ты (passwords, MFA, OAuth)
- **Authorization** — что можешь делать (RBAC, ABAC)
- **Encryption** — защита данных (at rest, in transit)
- **OWASP Top 10** — самые распространённые уязвимости
- **Defense in Depth** — несколько уровней защиты

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| Как реализовать login/auth? | [[authentication-authorization]] (навигационный хаб, 7 файлов) |
| Какие уязвимости самые опасные? | [[web-security-owasp]] |
| Как работает шифрование? | [[security-cryptography-fundamentals]] |
| Как настроить HTTPS? | [[security-https-tls]] |
| Где хранить секреты? | [[security-secrets-management]] |
| Как защитить API? | [[security-api-protection]] |
| Что делать при инциденте? | [[security-incident-response]] |

---

## Путь обучения

```
                    ┌─────────────────────────┐
                    │   Security Mindset      │
                    │   (threat modeling,     │
                    │    attack surface)      │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
    ┌─────────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
    │   AuthN/AuthZ   │ │  Cryptography │ │   OWASP       │
    │   (passwords,   │ │  (encryption, │ │   (XSS, SQLI, │
    │   OAuth, JWT)   │ │   hashing)    │ │   IDOR)       │
    └─────────┬───────┘ └───────┬───────┘ └───────┬───────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
    ┌─────────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
    │   HTTPS/TLS     │ │   Secrets     │ │   API         │
    │   (certificates,│ │   (Vault,     │ │   Protection  │
    │   pinning)      │ │   rotation)   │ │   (rate limit)│
    └─────────┬───────┘ └───────┬───────┘ └───────┬───────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   Incident Response     │
                    │   (detection, response, │
                    │    recovery)            │
                    └─────────────────────────┘
```

---

## Статьи по категориям

### Аутентификация и авторизация

| Статья | Описание | Связи |
|--------|----------|-------|
| [[authentication-authorization]] | Навигационный хаб: обзор, decision tree, сравнение подходов | → 6 deep-dives |
| [[auth-sessions-jwt-tokens]] | Sessions, JWT, opaque tokens, refresh patterns, token storage | → crypto, tls |
| [[auth-oauth2-oidc]] | OAuth 2.0/2.1, OIDC, PKCE, DPoP, GNAP, social login | → api, sso |
| [[auth-authorization-models]] | RBAC, ABAC, ReBAC (Zanzibar), policy engines | → owasp |
| [[auth-passwordless-mfa]] | Passkeys/WebAuthn, MFA, TOTP, Argon2, NIST 800-63-4 | → crypto |
| [[auth-enterprise-sso]] | SAML, Kerberos, LDAP, federation, IdP comparison | → oauth |
| [[auth-api-service-patterns]] | API keys, mTLS, HMAC, AWS Sig v4, Zero Trust | → tls, api |

### Веб-безопасность

| Статья | Описание | Связи |
|--------|----------|-------|
| [[web-security-owasp]] | OWASP Top 10, XSS, SQL Injection, IDOR | → api |

### Криптография

| Статья | Описание | Связи |
|--------|----------|-------|
| [[security-cryptography-fundamentals]] | Symmetric/asymmetric, hashing, signatures | → tls |
| [[security-https-tls]] | TLS handshake, certificates, HSTS | → crypto |

### Защита приложений

| Статья | Описание | Связи |
|--------|----------|-------|
| [[security-secrets-management]] | Vault, rotation, environment variables | → cloud |
| [[security-api-protection]] | Rate limiting, input validation, API keys | → auth |

### Основы

| Статья | Описание | Связи |
|--------|----------|-------|
| [[security-fundamentals]] | CIA Triad, Defense in Depth, Threat Modeling basics | → все разделы |
| [[threat-modeling]] | STRIDE, Attack Trees, Threat Modeling процесс | → design |

### Мобильная безопасность

| Статья | Описание | Связи |
|--------|----------|-------|
| [[mobile-security-owasp]] | OWASP Mobile Top 10, мобильные уязвимости | → android, ios |
| [[mobile-security-masvs]] | MASVS стандарт верификации | → owasp |
| [[mobile-app-protection]] | Обфускация, tamper detection, SSL pinning | → android, ios |

### Операции

| Статья | Описание | Связи |
|--------|----------|-------|
| [[security-incident-response]] | Detection, containment, recovery | → devops |

---

## Ключевые концепции

| Концепция | Что это | Почему важно |
|-----------|---------|--------------|
| **Defense in Depth** | Несколько уровней защиты | Один слой пробит → другие держат |
| **Least Privilege** | Минимальные необходимые права | Ограничивает blast radius |
| **Zero Trust** | Не доверяй, проверяй | Network != trust boundary |
| **Secure by Default** | Безопасная конфигурация из коробки | Не надеемся на "настроят позже" |
| **Fail Securely** | При ошибке — deny, не allow | Ошибка не открывает доступ |

---

## OWASP Top 10 (2025)

```
┌─────────────────────────────────────────────────────────────────┐
│                    OWASP TOP 10                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Broken Access Control                                      │
│     IDOR, privilege escalation, missing authz                  │
│                                                                 │
│  2. Cryptographic Failures                                     │
│     Weak crypto, plaintext secrets, bad TLS                    │
│                                                                 │
│  3. Injection                                                  │
│     SQL, NoSQL, OS command, LDAP injection                     │
│                                                                 │
│  4. Insecure Design                                            │
│     Flaws in architecture, missing threat modeling             │
│                                                                 │
│  5. Security Misconfiguration                                  │
│     Default creds, unnecessary features, verbose errors        │
│                                                                 │
│  6. Vulnerable Components                                      │
│     Outdated dependencies, known CVEs                          │
│                                                                 │
│  7. Auth Failures                                              │
│     Weak passwords, missing MFA, session issues                │
│                                                                 │
│  8. Data Integrity Failures                                    │
│     Unsigned updates, CI/CD vulnerabilities                    │
│                                                                 │
│  9. Logging & Monitoring Failures                              │
│     No audit logs, missing alerts                              │
│                                                                 │
│  10. SSRF                                                      │
│      Server-Side Request Forgery                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Checklist

```
□ HTTPS everywhere (no mixed content)
□ Strong password policy + MFA
□ Input validation on all user input
□ Parameterized queries (no SQL injection)
□ Output encoding (no XSS)
□ Authorization checks on every endpoint
□ Secrets in Vault/Secrets Manager (not in code)
□ Dependencies scanned for CVEs
□ Security headers configured
□ Audit logging enabled
□ Rate limiting on sensitive endpoints
□ Regular security testing (SAST/DAST)
```

---

## Связи с другими разделами

- [[cloud-networking-security]] — cloud IAM, VPC, security groups
- [[databases-monitoring-security]] — database security, RLS
- [[devops-overview]] — DevSecOps, security in CI/CD
- [[architecture-overview]] — security architecture patterns

---

## Инструменты

### Сканирование
- **OWASP ZAP** — DAST (dynamic analysis)
- **Semgrep** — SAST (static analysis)
- **Trivy** — Container/dependency scanning
- **Snyk** — Dependency vulnerabilities

### Secrets Management
- **HashiCorp Vault** — enterprise secrets
- **AWS Secrets Manager** — AWS native
- **1Password/Bitwarden** — team passwords

### Monitoring
- **SIEM** — Splunk, ELK, Datadog Security
- **WAF** — Cloudflare, AWS WAF
- **IDS/IPS** — Suricata, Snort

---

## Источники

### Теоретические основы

- Saltzer J., Schroeder M. (1975). *"The Protection of Information in Computer Systems."* Proceedings of the IEEE, 63(9). — 8 принципов проектирования безопасных систем, актуальных по сей день.
- DoD 5200.28-STD (1985). *"Trusted Computer System Evaluation Criteria (Orange Book)."* — формализация CIA Triad и уровней доверия.
- NIST SP 800-12 (1995). *"An Introduction to Computer Security: The NIST Handbook."* — базовое определение информационной безопасности.
- Anderson R. (2020). *Security Engineering: A Guide to Building Dependable Distributed Systems.* 3rd Edition. Wiley.

### Практические руководства

- [OWASP](https://owasp.org/) — Open Web Application Security Project
- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework)
- Stuttard D., Pinto M. (2011). *The Web Application Hacker's Handbook.* 2nd Edition. Wiley.
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего статей | 19 |
| Категорий | 7 |
| Последнее обновление | 2026-02-11 |

---

## Проверь себя

> [!question]- Почему принцип Defense in Depth эффективнее, чем один сильный уровень защиты (например, только WAF)?
> Один уровень — одна точка отказа. Если атакующий обходит WAF (например, через SSRF или внутреннюю сеть), дальше нет преград. Defense in Depth создаёт каскад барьеров: сетевая защита → авторизация на каждом endpoint → валидация input → параметризованные запросы → мониторинг. Каждый слой ловит то, что пропустил предыдущий, и увеличивает стоимость атаки.

> [!question]- Как связаны OWASP #4 (Insecure Design) и архитектурный этап проектирования системы? Почему фикс уязвимости дизайна дороже фикса бага в коде?
> Insecure Design — это изъян на уровне архитектуры (отсутствие threat modeling, неправильные trust boundaries). В отличие от бага в коде, который можно пропатчить, архитектурный дефект требует переработки целых модулей или потоков данных. Это связывает security напрямую с [[architecture-overview]]: решения о безопасности нужно принимать до написания кода, а не после пентеста.

> [!question]- Разработчик хранит API-ключи в переменных окружения Docker-контейнера. Применив path обучения из этого раздела, какие шаги нужно пройти, чтобы построить полноценное управление секретами?
> Путь обучения ведёт от основ (Security Mindset) через криптографию к защите приложений. Для секретов нужно: (1) понять криптографию — как шифруются данные at rest, (2) перейти к [[security-secrets-management]] — Vault, rotation, audit trail, (3) интегрировать с CI/CD через DevSecOps ([[devops-overview]]). Переменные окружения видны через `docker inspect` и логи — это не secrets management.

> [!question]- В Security Checklist перечислены 12 пунктов. Если бы у вас было время только на 3 из них для нового API-сервиса, какие три дали бы максимальное покрытие и почему?
> Наибольшее покрытие дают: (1) Authorization checks на каждом endpoint — закрывает OWASP #1 (Broken Access Control, лидер рейтинга), (2) Parameterized queries — закрывает #3 (Injection), (3) Secrets в Vault — закрывает #2 (Cryptographic Failures, утечка ключей). Эти три пункта адресуют топ-3 категории OWASP, где происходит большинство реальных breach'ей.

---

## Ключевые карточки

Defense in Depth — что это за принцип?
?
Множество уровней защиты (сеть, авторизация, валидация, шифрование, мониторинг), чтобы компрометация одного слоя не привела к полному взлому.

В чём разница между Authentication и Authorization?
?
Authentication — проверка личности (кто ты?), Authorization — проверка прав (что тебе разрешено?). AuthN всегда предшествует AuthZ.

Что означает принцип Zero Trust?
?
Ни один пользователь или сервис не получает доверие по умолчанию — каждый запрос проверяется, даже из внутренней сети. Сеть ≠ граница доверия.

Какая уязвимость на первом месте OWASP Top 10?
?
Broken Access Control — IDOR, privilege escalation, отсутствие проверки авторизации. Самая распространённая категория уязвимостей в веб-приложениях.

Что такое Fail Securely и зачем это нужно?
?
При ошибке система отказывает в доступе (deny), а не разрешает (allow). Это гарантирует, что сбой не открывает дыру в безопасности.

SAST и DAST — в чём разница подходов к тестированию безопасности?
?
SAST (Static) анализирует исходный код без запуска (Semgrep). DAST (Dynamic) тестирует работающее приложение снаружи (OWASP ZAP). Вместе покрывают и ошибки в коде, и runtime-уязвимости.

Что значит Least Privilege и как он ограничивает blast radius?
?
Каждый пользователь и сервис получают минимально необходимые права. При компрометации учётной записи атакующий получает доступ только к ограниченному набору ресурсов, а не ко всей системе.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Первый шаг | [[authentication-authorization]] | Хаб аутентификации: 7 deep-dive файлов по OAuth, JWT, SSO, passkeys |
| Углубиться | [[web-security-owasp]] | Детальный разбор OWASP Top 10 с примерами атак и защит |
| Углубиться | [[security-cryptography-fundamentals]] | Понять шифрование, хеширование и подписи — основу всех протоколов |
| Практика | [[security-secrets-management]] | Vault, rotation, хранение секретов — навык для production |
| Смежная тема | [[devops-overview]] | DevSecOps: интеграция security в CI/CD пайплайны |
| Смежная тема | [[cloud-networking-security]] | Cloud IAM, VPC, security groups — безопасность в облаке |
| Обзор | [[architecture-overview]] | Security architecture patterns, связь OWASP #4 с проектированием |

---

*Создано: 2025-12-22*

---

*Проверено: 2026-01-09*

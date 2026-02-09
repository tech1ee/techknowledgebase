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
---

# Security: карта раздела

> Security — не feature, а process. Думай как атакующий, защищай в глубину. Один breach может уничтожить компанию.

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
| Как реализовать login/auth? | [[authentication-authorization]] |
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
| [[authentication-authorization]] | AuthN vs AuthZ, JWT, OAuth 2.0, RBAC | → api |

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

- [OWASP](https://owasp.org/) — Open Web Application Security Project
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- "The Web Application Hacker's Handbook" by Dafydd Stuttard
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего статей | 8 |
| Категорий | 4 |
| Последнее обновление | 2025-12-22 |

---

*Создано: 2025-12-22*

---

*Проверено: 2026-01-09*

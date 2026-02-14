---
title: "Authentication & Authorization: навигационный хаб"
created: 2025-11-24
modified: 2026-02-11
type: overview
status: published
confidence: high
tags:
  - topic/security
  - type/overview
  - level/intermediate
related:
  - "[[auth-sessions-jwt-tokens]]"
  - "[[auth-oauth2-oidc]]"
  - "[[auth-authorization-models]]"
  - "[[auth-passwordless-mfa]]"
  - "[[auth-enterprise-sso]]"
  - "[[auth-api-service-patterns]]"
  - "[[web-security-owasp]]"
  - "[[security-fundamentals]]"
  - "[[api-design]]"
prerequisites:
  - "[[security-fundamentals]]"
reading_time: 7
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Authentication & Authorization: навигационный хаб

> AuthN = "Кто ты?" AuthZ = "Что тебе можно?" Два разных вопроса, два разных слоя, часто два разных сервиса. Проверка AuthN без AuthZ = Broken Access Control (#1 OWASP).

Это навигационный хаб по теме аутентификации и авторизации. Каждый аспект раскрыт в отдельном deep-dive файле.

---

## Краткая история web-аутентификации

```
1961  CTSS (MIT)              — первые компьютерные пароли
1976  Unix crypt()            — первое хеширование паролей
1994  Cookies (Netscape)      — фундамент для sessions
1996  HTTP Basic Auth         — пароль в каждом запросе (Base64, не шифрование!)
2005  SAML 2.0               — enterprise SSO через XML assertions
2007  OAuth 1.0              — делегирование с криптографической подписью
2012  OAuth 2.0              — упрощение: bearer tokens по HTTPS
2014  OpenID Connect         — identity layer поверх OAuth 2.0
2015  JWT (RFC 7519)         — self-contained tokens
2019  WebAuthn (W3C)         — public-key аутентификация в браузере
2022  Passkeys announced     — Apple, Google, Microsoft
2024  GNAP (RFC 9635)        — "OAuth с нуля", next-gen протокол
2025  OAuth 2.1 (draft v14)  — консолидация best practices
2025  NIST SP 800-63-4       — обновлённые стандарты digital identity
```

---

## AuthN vs AuthZ: ключевое различие

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  AUTHENTICATION (AuthN)          AUTHORIZATION (AuthZ)         │
│  ─────────────────────          ──────────────────────         │
│                                                                 │
│  "КТО ты?"                      "ЧТО тебе можно?"              │
│                                                                 │
│  • Sessions / JWT              • RBAC (роли)                   │
│  • OAuth / OIDC                • ABAC (атрибуты)               │
│  • Passkeys / WebAuthn         • ReBAC (отношения)             │
│  • MFA / Biometrics            • Policy engines (OPA, Cedar)   │
│                                                                 │
│  Результат: Identity            Результат: Allow / Deny        │
│  "Это точно Иван Петров"       "Петров может удалять посты"    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Аналогия:** Паспортный контроль в аэропорту (AuthN) и посадочный талон (AuthZ). Паспорт подтверждает, что вы -- это вы. Талон определяет, в какой самолёт и на какое место вы можете сесть. Одно без другого бесполезно.

---

## Навигация по deep-dive файлам

| Файл | Что покрывает | Ключевые темы |
|------|--------------|---------------|
| [[auth-sessions-jwt-tokens]] | Механизмы идентификации | Sessions, JWT (JWS/JWE), opaque tokens, refresh patterns, token storage (browser + mobile) |
| [[auth-oauth2-oidc]] | Делегированная авторизация | OAuth 2.0/2.1, OIDC, PKCE, Authorization Code Flow, DPoP, GNAP, social login |
| [[auth-authorization-models]] | Модели контроля доступа | ACL, RBAC, ABAC, ReBAC (Zanzibar), PBAC, policy engines (OPA, Cedar, OpenFGA) |
| [[auth-passwordless-mfa]] | Современная аутентификация | Passkeys/WebAuthn/FIDO2, MFA, TOTP, password hashing (Argon2, bcrypt), NIST SP 800-63-4 |
| [[auth-enterprise-sso]] | Корпоративная аутентификация | SAML 2.0, Kerberos, LDAP, federation, IdP сравнение (Okta, Keycloak, Azure AD) |
| [[auth-api-service-patterns]] | Аутентификация сервисов и API | API keys, mTLS, HMAC signatures, AWS Sig v4, Zero Trust, service mesh auth |

---

## Дерево решений: какой метод аутентификации выбрать

```
Какой механизм аутентификации?

                    Тип приложения?
                    │
         ┌──────────┼──────────────────┐
         ▼          ▼                  ▼
     Web-app    Mobile app       Service/API
         │          │                  │
         ▼          ▼                  ▼
    Server-side? Есть backend?   Machine-to-machine?
    │         │    │        │         │         │
   Да        Нет  Да      Нет       Да        Нет
    │         │    │        │         │         │
    ▼         ▼    ▼        ▼         ▼         ▼
 Sessions  OAuth  OAuth   OAuth   mTLS /      OAuth
 + Cookie  +PKCE  +PKCE   +PKCE   Client     Bearer
                                   Creds      Tokens

Нужна интеграция с Google/Apple?
  → OAuth 2.0 + OIDC (social login)

Корпоративная среда, 50+ сервисов?
  → SAML 2.0 или OIDC SSO

Высокие требования к безопасности?
  → Passkeys (WebAuthn) + MFA

API для разработчиков?
  → API keys + OAuth 2.0 Bearer tokens
```

---

## Сравнение подходов

| Критерий | Sessions | JWT | OAuth 2.0 | Passkeys | SAML |
|----------|----------|-----|-----------|----------|------|
| **Сценарий** | Веб-приложения | API, микросервисы | Делегирование доступа | Замена паролей | Enterprise SSO |
| **Statefulness** | Stateful (сервер) | Stateless (клиент) | Зависит от токена | Stateless (crypto) | Stateful (assertion) |
| **Мгновенный отзыв** | Да (удалить сессию) | Нет (до истечения) | Через revocation endpoint | Нет (delete credential) | Да (через IdP) |
| **Масштабируемость** | Redis Cluster | Любой сервер | Authorization Server | Любой сервер | IdP bottleneck |
| **Мобильные клиенты** | Неудобно | Удобно (header) | Стандарт (PKCE) | Нативная поддержка | Плохо (XML) |
| **Phishing resistance** | Нет | Нет | Нет | Да (origin binding) | Нет |
| **Подробнее** | [[auth-sessions-jwt-tokens]] | [[auth-sessions-jwt-tokens]] | [[auth-oauth2-oidc]] | [[auth-passwordless-mfa]] | [[auth-enterprise-sso]] |

---

## Мобильная аутентификация

Мобильные платформы имеют свои особенности хранения токенов и биометрической аутентификации:

**iOS:** Keychain Services (`kSecAttrAccessibleWhenUnlockedThisDeviceOnly`), Face ID / Touch ID через Secure Enclave, App Attest для верификации приложения.

**Android:** Android Keystore (аппаратный StrongBox на Android 9+), BiometricPrompt (Class 3 hardware-backed), Play Integrity для верификации устройства.

Подробнее о платформенных механизмах: [[android-permissions-security]], [[ios-permissions-security]]. Об App Attestation и Play Integrity: [[auth-api-service-patterns]].

---

## Рекомендуемый порядок чтения

### По уровню

```
НАЧИНАЮЩИЙ
──────────────────────────────────
1. authentication-authorization     ← вы здесь
2. auth-sessions-jwt-tokens         → механизмы, trade-offs
3. auth-passwordless-mfa            → пароли, MFA, passkeys

MIDDLE
──────────────────────────────────
4. auth-oauth2-oidc                 → OAuth, OIDC, social login
5. auth-authorization-models        → RBAC, ABAC, ReBAC

SENIOR / ARCHITECT
──────────────────────────────────
6. auth-enterprise-sso              → SAML, Kerberos, SSO
7. auth-api-service-patterns        → API auth, mTLS, Zero Trust
```

### По задаче

| Задача | Маршрут |
|--------|---------|
| Реализовать login для веб-приложения | auth-sessions-jwt-tokens → auth-passwordless-mfa |
| Добавить "Login with Google" | auth-oauth2-oidc (Authorization Code + PKCE) |
| Настроить RBAC для SaaS | auth-authorization-models (RBAC → ABAC по мере роста) |
| Интегрировать SSO для enterprise-клиентов | auth-enterprise-sso (SAML 2.0) → auth-oauth2-oidc (OIDC альтернатива) |
| Защитить API для мобильного приложения | auth-api-service-patterns → auth-sessions-jwt-tokens (JWT + refresh) |
| Перейти на passwordless | auth-passwordless-mfa (passkeys, WebAuthn) |

---

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| **JWT** | Self-contained подписанный токен | [[auth-sessions-jwt-tokens]] |
| **OAuth 2.0** | Делегирование доступа без передачи пароля | [[auth-oauth2-oidc]] |
| **OIDC** | Identity layer поверх OAuth 2.0 | [[auth-oauth2-oidc]] |
| **PKCE** | Защита Authorization Code от перехвата | [[auth-oauth2-oidc]] |
| **RBAC / ABAC** | Роли vs атрибуты для контроля доступа | [[auth-authorization-models]] |
| **ReBAC (Zanzibar)** | Авторизация через граф отношений | [[auth-authorization-models]] |
| **Passkeys** | WebAuthn + cloud sync = замена паролей | [[auth-passwordless-mfa]] |
| **Argon2id** | Рекомендованный NIST алгоритм хеширования паролей | [[auth-passwordless-mfa]] |
| **SAML 2.0** | XML-based enterprise SSO протокол | [[auth-enterprise-sso]] |
| **mTLS** | Взаимная аутентификация через сертификаты | [[auth-api-service-patterns]] |
| **Zero Trust** | "Never trust, always verify" | [[auth-api-service-patterns]] |
| **DPoP** | Proof of Possession для bearer tokens | [[auth-oauth2-oidc]] |

---

## Чеклист безопасности

```
Authentication:
□ Пароли хешируются Argon2id или bcrypt (cost ≥ 12)
□ MFA для критичных операций (passkeys предпочтительно)
□ Rate limiting на login/register/reset endpoints
□ Нет секретов в коде или логах

Token Management:
□ Access token: короткий срок (5-15 мин)
□ Refresh token: httpOnly cookie, rotation
□ JWT: проверка signature + exp + aud + iss
□ HTTPS everywhere (no exceptions)

Authorization:
□ Проверка прав на КАЖДОМ endpoint (не только на клиенте)
□ Principle of Least Privilege
□ Periodic access review

OAuth:
□ PKCE для всех клиентов (обязателен в OAuth 2.1)
□ State параметр: cryptographically random, проверяется
□ Exact redirect_uri match
```

---

## Связанные области

- [[web-security-owasp]] -- Broken Access Control (#1 OWASP), Authentication Failures (#7)
- [[security-fundamentals]] -- CIA Triad, Defense in Depth, Principle of Least Privilege
- [[security-cryptography-fundamentals]] -- алгоритмы подписи (HMAC, RSA, ECDSA) для JWT и WebAuthn
- [[security-https-tls]] -- TLS -- prerequisite для всех auth-протоколов
- [[security-api-protection]] -- rate limiting, input validation для auth endpoints
- [[api-design]] -- OAuth в контексте API design, security секция
- [[microservices-vs-monolith]] -- auth patterns в distributed systems

---

## Источники

- Richer, J. & Sanso, A. (2017). OAuth 2 in Action (Manning) -- практическое руководство по OAuth 2.0
- Madden, N. (2020). API Security in Action (Manning) -- безопасность API от аутентификации до Zero Trust
- OWASP Authentication Cheat Sheet -- проверенные рекомендации
- NIST SP 800-63-4 (2025) -- стандарт digital identity и authentication
- RFC 6749 (OAuth 2.0), RFC 7519 (JWT), RFC 7636 (PKCE) -- ключевые спецификации

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего файлов | 7 (1 hub + 6 deep-dives) |
| Общий объём | ~38,000 слов |
| Последнее обновление | 2026-02-11 |

---

*Создано: 2025-11-24 | Переписано: 2026-02-11*

---

## Проверь себя

> [!question]- Почему OAuth 2.0 сам по себе НЕ является протоколом аутентификации, и что потребовалось добавить поверх него?
> OAuth 2.0 — это фреймворк делегированной **авторизации**: он выдаёт access token для доступа к ресурсам, но не определяет, кто именно пользователь. Чтобы получить identity, поверх OAuth добавили OpenID Connect (OIDC), который вводит ID Token (JWT с claims о пользователе) и стандартный `/userinfo` endpoint. Без OIDC приложение, использующее "Login with Google" через голый OAuth, уязвимо к token substitution и не имеет стандартного способа получить профиль пользователя.

> [!question]- У вас SaaS-продукт с 5 ролями. Через год приходит enterprise-клиент и требует: "менеджер отдела продаж видит только сделки своего отдела". Какую модель авторизации вы выберете и почему текущая может не справиться?
> Классический RBAC оперирует ролями глобально ("менеджер может видеть сделки"), но не учитывает **контекст** — отдел, регион, владельца ресурса. Для требования "только сделки своего отдела" нужно перейти к ABAC (атрибуты пользователя + ресурса: `user.department == deal.department`) или ReBAC (граф отношений: пользователь → отдел → сделки). RBAC пришлось бы расширять ролями вида "менеджер-продажи-отдел-1", что приводит к role explosion.

> [!question]- Мобильное приложение хранит JWT access token. Сравните хранение в Android Keystore (аппаратный StrongBox) и в SharedPreferences — какие атаки предотвращает каждый подход и как это связано с моделью угроз OWASP Mobile?
> SharedPreferences хранит данные в XML-файле, доступном на рутированном устройстве или через backup. Android Keystore с аппаратным StrongBox хранит ключи в выделенном security-чипе — токен нельзя извлечь даже с root-доступом. По OWASP Mobile Top 10 это защита от M9 (Insecure Data Storage). Однако Keystore защищает хранение, но не спасает от перехвата токена в сети (нужен HTTPS + certificate pinning) и не заменяет short-lived access tokens + refresh rotation.

> [!question]- Компания переходит с сессий на JWT для микросервисной архитектуры. Какую ключевую возможность они теряют "из коробки" и как её можно компенсировать?
> Теряется **мгновенный отзыв** (instant revocation). При сессиях достаточно удалить запись из Redis — и доступ закрыт. JWT валиден до истечения `exp`, поэтому скомпрометированный токен продолжает работать. Компенсация: короткий TTL access token (5-15 мин) + refresh token rotation, либо blocklist на gateway (проверка `jti` в Redis), либо DPoP (Demonstration of Proof-of-Possession), привязывающий токен к конкретному клиенту.

---

## Ключевые карточки

AuthN vs AuthZ — в чём разница?
?
AuthN (аутентификация) отвечает на вопрос "Кто ты?" и устанавливает identity. AuthZ (авторизация) отвечает на вопрос "Что тебе можно?" и определяет права доступа. Это два разных слоя: проверка AuthN без AuthZ — это Broken Access Control (#1 OWASP).

Когда использовать sessions, а когда JWT?
?
Sessions (stateful) — для веб-приложений с одним бэкендом, где нужен мгновенный отзыв. JWT (stateless) — для микросервисов и API, где важна масштабируемость без централизованного хранилища сессий. JWT нельзя мгновенно отозвать без дополнительной инфраструктуры.

Что такое PKCE и зачем он нужен в OAuth 2.1?
?
PKCE (Proof Key for Code Exchange) защищает Authorization Code Flow от перехвата кода. Клиент генерирует `code_verifier`, отправляет его хеш (`code_challenge`) при запросе кода, а затем предъявляет оригинал при обмене кода на токен. В OAuth 2.1 PKCE обязателен для всех клиентов.

Чем RBAC, ABAC и ReBAC отличаются по масштабируемости?
?
RBAC прост, но при росте требований ведёт к role explosion. ABAC масштабируется через атрибуты (user.department, resource.owner) и политики, но сложнее аудит. ReBAC (модель Zanzibar/Google) масштабируется через граф отношений и решает задачи вроде "доступ к документу, потому что ты в команде владельца".

Почему Passkeys считаются phishing-resistant?
?
Passkeys используют WebAuthn с origin binding: криптографический challenge привязан к домену сайта. Фишинговый сайт с другим доменом не сможет запросить валидную подпись от аутентификатора. Это единственный из массовых подходов с встроенной защитой от фишинга.

Что такое Zero Trust и как он меняет подход к аутентификации сервисов?
?
Zero Trust — принцип "never trust, always verify": каждый запрос аутентифицируется и авторизуется, даже внутри периметра сети. Вместо доверия к IP/VPN используются mTLS между сервисами, проверка identity на каждом хопе и минимальные привилегии на каждом уровне.

Зачем нужен DPoP и какую проблему bearer tokens он решает?
?
Bearer token может быть использован любым, кто его получил (token theft). DPoP (Demonstration of Proof-of-Possession) привязывает токен к конкретной паре ключей клиента — при каждом запросе клиент доказывает владение приватным ключом. Это снижает ущерб от утечки токена.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Механизмы токенов | [[auth-sessions-jwt-tokens]] | Разобраться в sessions vs JWT, хранение токенов, refresh patterns |
| OAuth и социальный логин | [[auth-oauth2-oidc]] | Понять Authorization Code + PKCE, OIDC, DPoP, social login |
| Модели авторизации | [[auth-authorization-models]] | Выбрать между RBAC, ABAC и ReBAC для своего проекта |
| Passwordless и MFA | [[auth-passwordless-mfa]] | Внедрить Passkeys/WebAuthn, настроить MFA, выбрать хеширование паролей |
| Корпоративный SSO | [[auth-enterprise-sso]] | Интегрировать SAML 2.0, Kerberos, сравнить IdP-решения |
| Защита API и сервисов | [[auth-api-service-patterns]] | Настроить mTLS, API keys, Zero Trust для микросервисов |
| OWASP и веб-безопасность | [[web-security-owasp]] | Связать auth с Broken Access Control (#1) и Authentication Failures (#7) |

---
title: "Threat Modeling: Моделирование угроз"
type: concept
status: published
tags:
  - topic/security
  - type/concept
  - level/intermediate
related:
  - "[[security-fundamentals]]"
  - "[[mobile-security-owasp]]"
  - "[[architecture-resilience-patterns]]"
prerequisites:
  - "[[security-fundamentals]]"
reading_time: 30
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Threat Modeling: Моделирование угроз

---

cs-foundations: [STRIDE, DREAD, PASTA, Attack Trees, Data Flow Diagrams, Trust Boundaries]
---

## Зачем это нужно

Исправление уязвимости на этапе проектирования обходится в 10-100 раз дешевле, чем после релиза. Исследования показывают: устранение дефекта после релиза может быть до 30 раз дороже, чем на этапе дизайна.

**Пример ROI:** 2-часовая сессия threat modeling предотвращает архитектурный дефект, который потребовал бы 100 часов рефакторинга. При стоимости инженера $100/час — это экономия $10,000 при инвестиции $200. ROI: 4,900%.

**Проблема:** Большинство команд думают о безопасности в конце разработки — когда исправления дороги и болезненны. 63% команд не делают threat modeling вообще. Только 37% организаций интегрировали безопасность в DevOps-процессы.

**Решение:** Threat modeling — систематический подход к выявлению угроз на ранних этапах. Это "measure twice, cut once" кибербезопасности.

```
┌─────────────────────────────────────────────────────────────────┐
│                    СТОИМОСТЬ ИСПРАВЛЕНИЯ ДЕФЕКТОВ                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Стоимость                                                      │
│   исправления                                                    │
│       ▲                                                          │
│       │                                                ●         │
│       │                                              ╱           │
│  30x  │                                           ●              │
│       │                                        ╱                 │
│       │                                     ●                    │
│       │                                  ╱                       │
│  10x  │                              ●                           │
│       │                           ╱                              │
│       │                       ●                                  │
│   1x  │───●───────●───────●                                      │
│       │                                                          │
│       └──────────────────────────────────────────────────▶       │
│          Design  Code  Test  Integration  Release  Production   │
│                                                                  │
│   ● Threat modeling экономит на самом дорогом этапе             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| Security Fundamentals | CIA Triad, основы безопасности | [[security-fundamentals]] |
| Базовая архитектура приложений | Понимание компонентов системы | — |
| Понимание типов атак | OWASP Top 10 | [[web-security-owasp]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Threat** | Потенциальное негативное действие против системы | Грабитель, который может попытаться проникнуть |
| **Vulnerability** | Слабость, которую можно эксплуатировать | Незапертая дверь |
| **Attack Vector** | Путь, которым угроза достигает цели | Способ проникновения: дверь, окно, крыша |
| **Trust Boundary** | Граница между зонами с разным уровнем доверия | Периметр дома vs улица |
| **Data Flow Diagram (DFD)** | Схема движения данных в системе | Карта трубопроводов |
| **Countermeasure** | Механизм защиты от угрозы | Замок, сигнализация |

---

## CS-фундамент: История Threat Modeling

### 1980-е — 1990-е: Fault Trees и Attack Trees

Threat modeling эволюционировало из fault tree analysis (анализ деревьев отказов), используемого в aerospace и ядерной индустрии. В конце 1980-х — начале 1990-х исследователи (вероятно, в NSA) адаптировали этот подход для анализа безопасности, создав attack trees.

### 1994: Edward Amoroso и Threat Trees

Edward Amoroso в книге "Fundamentals of Computer Security Technology" описал threat trees — одну из первых открытых публикаций о структурном анализе угроз.

### 1999: Bruce Schneier и Attack Trees

Bruce Schneier популяризировал attack trees в статье "Attack Trees" (Dr. Dobb's Journal, December 1999). Его работа сделала методологию доступной широкому сообществу безопасности.

### 1999: STRIDE в Microsoft

Praerit Garg и Loren Kohnfelder в Microsoft разработали STRIDE — мнемонику для классификации угроз. Это стало основой системного подхода к threat modeling в software development.

### 2003: DREAD от Microsoft

Microsoft также представила DREAD для количественной оценки угроз. Позже компания отказалась от DREAD из-за субъективности, но модель до сих пор используется.

### 2012: PASTA

Tony UcedaVélez и Marco M. Morana представили PASTA (Process for Attack Simulation and Threat Analysis) — семиэтапную методологию, объединяющую бизнес-контекст с техническим анализом.

### 2014: Adam Shostack и Four Question Framework

Adam Shostack в книге "Threat Modeling: Designing for Security" сформулировал Four Question Framework — универсальный подход, который теперь используют Google, AWS и правительственные организации.

### 2010-е: LINDDUN для Privacy

KU Leuven представила LINDDUN — фреймворк для моделирования угроз приватности, позже включённый в ISO 27550.

---

## Four Question Framework (Adam Shostack)

Универсальный фреймворк, принятый Google, AWS, CMS (US Government).

```
┌─────────────────────────────────────────────────────────────────┐
│              FOUR QUESTION FRAMEWORK                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  1. WHAT ARE WE WORKING ON?                             │   │
│   │     Что мы анализируем?                                 │   │
│   │                                                         │   │
│   │     → Data Flow Diagrams                                │   │
│   │     → Architecture diagrams                             │   │
│   │     → Trust boundaries                                  │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  2. WHAT CAN GO WRONG?                                  │   │
│   │     Что может пойти не так?                             │   │
│   │                                                         │   │
│   │     → STRIDE analysis                                   │   │
│   │     → Attack trees                                      │   │
│   │     → Brainstorming                                     │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  3. WHAT ARE WE GOING TO DO ABOUT IT?                   │   │
│   │     Что будем делать?                                   │   │
│   │                                                         │   │
│   │     → Mitigate (устранить)                              │   │
│   │     → Transfer (передать риск)                          │   │
│   │     → Accept (принять)                                  │   │
│   │     → Avoid (избежать)                                  │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  4. DID WE DO A GOOD JOB?                               │   │
│   │     Хорошо ли мы справились?                            │   │
│   │                                                         │   │
│   │     → Механическая проверка (диаграмма есть? угрозы?)   │   │
│   │     → Качественная оценка (рекомендовал бы коллеге?)    │   │
│   │     → Ретроспектива                                     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Почему именно эти формулировки

Adam Shostack намеренно выбрал "What are we working on?" вместо "What are we building?" — threat modeling применимо на любом этапе жизненного цикла, не только при создании. Формулировка "building" подталкивает к waterfall-мышлению.

**Частая ошибка:** Перефразирование вопросов. В формулировках заложены нюансы и гибкость, которые теряются при изменении.

---

## STRIDE: Классификация угроз

STRIDE — мнемоника для шести категорий угроз, разработанная Microsoft в 1999 году. Каждая категория соответствует нарушению принципа безопасности.

```
┌─────────────────────────────────────────────────────────────────┐
│                         STRIDE                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Угроза                    Нарушает           Защита            │
│   ───────────────────────────────────────────────────────────    │
│                                                                  │
│   S  SPOOFING               Authenticity       Authentication    │
│      Подмена личности                          MFA, certificates │
│                                                                  │
│   T  TAMPERING              Integrity          Signing, hashing  │
│      Изменение данных                          Input validation  │
│                                                                  │
│   R  REPUDIATION            Non-repudiation    Logging, audit    │
│      Отрицание действий                        Digital signatures│
│                                                                  │
│   I  INFORMATION            Confidentiality    Encryption        │
│      DISCLOSURE                                Access control    │
│      Раскрытие информации                                        │
│                                                                  │
│   D  DENIAL OF SERVICE      Availability       Rate limiting     │
│      Отказ в обслуживании                      Redundancy, CDN   │
│                                                                  │
│   E  ELEVATION OF           Authorization      Least privilege   │
│      PRIVILEGE                                 RBAC, sandboxing  │
│      Повышение привилегий                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### S — Spoofing (Подмена)

**Что это:** Атакующий выдаёт себя за другого пользователя, систему или компонент.

**Примеры:**
- Фишинг email от имени CEO
- Поддельный сертификат сервера
- Session hijacking
- IP spoofing

**Вопросы для анализа:**
- Как мы проверяем, что пользователь — тот, за кого себя выдаёт?
- Как компоненты системы аутентифицируют друг друга?
- Можно ли подделать credentials?

**Защитные меры:**
- Strong authentication (MFA)
- Certificate pinning
- Mutual TLS между сервисами
- Signed tokens (JWT с подписью)

### T — Tampering (Изменение)

**Что это:** Несанкционированная модификация данных или кода.

**Примеры:**
- SQL Injection изменяет данные в БД
- Man-in-the-middle изменяет запрос в транзите
- Модификация файлов конфигурации
- Изменение параметров запроса

**Вопросы для анализа:**
- Можно ли изменить данные в transit?
- Можно ли изменить данные at rest?
- Проверяется ли целостность входных данных?

**Защитные меры:**
- Input validation
- Digital signatures
- Integrity checks (checksums, HMAC)
- Immutable logs

```kotlin
// Пример: Защита от tampering в Android
class SecureDataStore(private val context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    /**
     * Сохраняем данные с HMAC для проверки целостности.
     * Если данные изменены — HMAC не совпадёт.
     */
    fun saveWithIntegrity(key: String, value: String) {
        val hmac = computeHmac(value)
        sharedPreferences.edit()
            .putString(key, value)
            .putString("${key}_hmac", hmac)
            .apply()
    }

    fun readWithIntegrityCheck(key: String): String? {
        val value = sharedPreferences.getString(key, null) ?: return null
        val storedHmac = sharedPreferences.getString("${key}_hmac", null)
        val computedHmac = computeHmac(value)

        // Если HMAC не совпадает — данные были изменены
        if (storedHmac != computedHmac) {
            throw SecurityException("Data integrity violation for key: $key")
        }
        return value
    }

    private fun computeHmac(data: String): String {
        // Реализация HMAC-SHA256
        // ...
    }
}
```

### R — Repudiation (Отрицание)

**Что это:** Пользователь отрицает совершённое действие, и нет способа доказать обратное.

**Примеры:**
- Пользователь отрицает, что делал заказ
- Администратор отрицает удаление данных
- Отсутствие логов критичных операций

**Вопросы для анализа:**
- Логируются ли все критичные действия?
- Можно ли изменить или удалить логи?
- Есть ли timestamp и идентификация пользователя?

**Защитные меры:**
- Comprehensive audit logging
- Tamper-evident logs (append-only)
- Digital signatures на транзакциях
- Centralized log management (SIEM)

### I — Information Disclosure (Раскрытие информации)

**Что это:** Несанкционированный доступ к конфиденциальным данным.

**Примеры:**
- SQL Injection извлекает данные
- Verbose error messages раскрывают структуру системы
- Credentials в логах или коде
- Неправильные permissions на файлы

**Вопросы для анализа:**
- Какие данные конфиденциальны?
- Шифруются ли данные at rest и in transit?
- Что показывается в error messages?
- Где хранятся секреты?

**Защитные меры:**
- Encryption (TLS, AES)
- Access control
- Data classification
- Secrets management (Vault, KMS)
- Generic error messages для пользователей

### D — Denial of Service (Отказ в обслуживании)

**Что это:** Атака, делающая систему недоступной для легитимных пользователей.

**Примеры:**
- DDoS атака
- Resource exhaustion (memory, CPU, connections)
- Algorithmic complexity attacks (ReDoS)
- Lock contention

**Вопросы для анализа:**
- Есть ли rate limiting?
- Что произойдёт при 100x нагрузке?
- Есть ли single points of failure?
- Какие ресурсы можно исчерпать?

**Защитные меры:**
- Rate limiting
- Redundancy (multi-AZ, replicas)
- Auto-scaling
- Circuit breakers
- CDN и DDoS protection

### E — Elevation of Privilege (Повышение привилегий)

**Что это:** Атакующий получает права, которых не должен иметь.

**Примеры:**
- Vertical: user → admin
- Horizontal: user A видит данные user B
- SQL Injection даёт доступ к БД
- Container escape

**Вопросы для анализа:**
- Проверяется ли авторизация на каждом endpoint?
- Применяется ли Principle of Least Privilege?
- Можно ли обойти проверки авторизации?

**Защитные меры:**
- Authorization checks на каждом уровне
- Principle of Least Privilege
- Sandboxing
- Input validation

```python
# Пример: Проверка авторизации на каждом уровне

from functools import wraps
from flask import request, abort, g

def require_permission(permission: str):
    """
    Декоратор для проверки прав на каждом endpoint.
    Защита от Elevation of Privilege.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Проверяем аутентификацию (Spoofing)
            if not g.current_user:
                abort(401)

            # 2. Проверяем авторизацию (Elevation of Privilege)
            if not g.current_user.has_permission(permission):
                # Логируем попытку (Repudiation)
                audit_log.warning(
                    f"Unauthorized access attempt: user={g.current_user.id}, "
                    f"permission={permission}, endpoint={request.endpoint}"
                )
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Использование
@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_permission('admin:delete_user')
def delete_user(user_id: int):
    # Только если прошли проверку авторизации
    user_service.delete(user_id)
    return {'status': 'deleted'}
```

### STRIDE per Element

STRIDE применяется к элементам Data Flow Diagram:

| Элемент DFD | S | T | R | I | D | E |
|-------------|---|---|---|---|---|---|
| **External Entity** | ✓ |   | ✓ |   |   |   |
| **Process** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Data Store** |   | ✓ | ? | ✓ | ✓ |   |
| **Data Flow** |   | ✓ |   | ✓ | ✓ |   |

---

## Data Flow Diagrams (DFD)

DFD — визуальное представление движения данных через систему. Это основа для STRIDE-анализа.

### Элементы DFD

```
┌─────────────────────────────────────────────────────────────────┐
│                    ЭЛЕМЕНТЫ DFD                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐                                                │
│   │             │         EXTERNAL ENTITY                        │
│   │   Actor     │         Внешний актор (пользователь, система)  │
│   │             │         Находится ВНЕ контроля системы         │
│   └─────────────┘                                                │
│                                                                  │
│   ╔═════════════╗                                                │
│   ║             ║         PROCESS                                │
│   ║   Process   ║         Компонент, обрабатывающий данные       │
│   ║             ║         Может быть атакован всеми STRIDE       │
│   ╚═════════════╝                                                │
│                                                                  │
│   ═══════════════                                                │
│   ║  Data Store ║         DATA STORE                             │
│   ═══════════════         База данных, файловая система, кэш     │
│                           Хранит данные                          │
│                                                                  │
│   ─────────────▶          DATA FLOW                              │
│                           Движение данных между элементами       │
│                           Может быть перехвачен, изменён         │
│                                                                  │
│   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄          TRUST BOUNDARY                         │
│   ┄              ┄        Граница между зонами доверия           │
│   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄          Данные, пересекающие границу, опасны   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Trust Boundaries (Границы доверия)

Trust boundaries — критически важный элемент DFD. Это точки, где данные переходят между зонами с разным уровнем доверия.

**Типичные trust boundaries:**
1. **Internet ↔ DMZ** — граница между публичной сетью и DMZ
2. **DMZ ↔ Internal Network** — граница между DMZ и внутренней сетью
3. **Process ↔ Process** — между процессами разных уровней привилегий
4. **User input ↔ Application** — любой пользовательский ввод

**Правило:** Данные, пересекающие trust boundary, должны быть:
- Аутентифицированы (кто отправил?)
- Авторизованы (имеет ли право?)
- Валидированы (корректны ли данные?)

### Пример DFD для веб-приложения

```
┌─────────────────────────────────────────────────────────────────┐
│                    DFD: E-Commerce Application                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                          INTERNET                                │
│   ┌─────────────┐            │                                   │
│   │             │            │                                   │
│   │    User     │────────────┼───────────┐                       │
│   │   Browser   │            │           │                       │
│   └─────────────┘            │           │                       │
│                              │           │                       │
│   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄│┄┄┄┄┄┄┄┄┄┄┄│┄┄┄┄┄ Trust Boundary 1 │
│                              │           │     (Internet → DMZ)  │
│                          DMZ │           ▼                       │
│                              │    ╔═════════════╗                │
│                              │    ║   Web App   ║                │
│                              │    ║  (Frontend) ║                │
│                              │    ╚══════┬══════╝                │
│                              │           │                       │
│   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄│┄┄┄┄┄┄┄┄┄┄┄│┄┄┄┄┄ Trust Boundary 2 │
│                              │           │     (DMZ → Internal)  │
│                       INTERNAL│           ▼                       │
│                              │    ╔═════════════╗                │
│   ┌─────────────┐            │    ║  API Server ║                │
│   │   Payment   │◄───────────┼────║  (Backend)  ║                │
│   │   Gateway   │            │    ╚══════┬══════╝                │
│   └─────────────┘            │           │                       │
│                              │           │                       │
│   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄│┄┄┄┄┄┄┄┄┄┄┄│┄┄┄┄┄ Trust Boundary 3 │
│                              │           │     (App → Database)  │
│                       DB ZONE│           ▼                       │
│                              │    ═══════════════                │
│                              │    ║  PostgreSQL ║                │
│                              │    ═══════════════                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### STRIDE-анализ по DFD

Для каждого элемента и пересечения trust boundary задаём вопросы по STRIDE:

```
┌─────────────────────────────────────────────────────────────────┐
│        STRIDE-АНАЛИЗ: User Browser → Web App                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  S: Может ли кто-то притвориться легитимным пользователем?       │
│     → Угроза: Session hijacking, credential theft                │
│     → Mitigation: MFA, secure session management                 │
│                                                                  │
│  T: Могут ли данные быть изменены в transit?                     │
│     → Угроза: MITM атака на HTTP                                 │
│     → Mitigation: HTTPS only, HSTS                               │
│                                                                  │
│  R: Может ли пользователь отрицать свои действия?                │
│     → Угроза: "Я не делал этот заказ"                            │
│     → Mitigation: Audit logging с timestamp и user ID            │
│                                                                  │
│  I: Может ли кто-то увидеть данные в transit?                    │
│     → Угроза: Перехват credentials, PII                          │
│     → Mitigation: TLS 1.3, certificate pinning                   │
│                                                                  │
│  D: Может ли кто-то сделать сервис недоступным?                  │
│     → Угроза: DDoS, slowloris                                    │
│     → Mitigation: WAF, rate limiting, CDN                        │
│                                                                  │
│  E: Может ли пользователь получить admin-права?                  │
│     → Угроза: SQL injection, IDOR                                │
│     → Mitigation: Parameterized queries, authz checks            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## PASTA: Process for Attack Simulation and Threat Analysis

PASTA — семиэтапная методология, объединяющая бизнес-контекст с техническим анализом. Разработана Tony UcedaVélez и Marco M. Morana.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PASTA: 7 ЭТАПОВ                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  STAGE 1: DEFINE OBJECTIVES                             │   │
│   │  Определение бизнес-целей и требований безопасности     │   │
│   │                                                         │   │
│   │  • Какие бизнес-цели?                                   │   │
│   │  • Какие compliance требования?                         │   │
│   │  • Каков risk appetite организации?                     │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  STAGE 2: DEFINE TECHNICAL SCOPE                        │   │
│   │  Определение технического охвата                        │   │
│   │                                                         │   │
│   │  • Какие системы в scope?                               │   │
│   │  • Какие технологии используются?                       │   │
│   │  • Какова attack surface?                               │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  STAGE 3: APPLICATION DECOMPOSITION                     │   │
│   │  Декомпозиция приложения                                │   │
│   │                                                         │   │
│   │  • Data Flow Diagrams                                   │   │
│   │  • Trust boundaries                                     │   │
│   │  • Entry points                                         │   │
│   │  • Assets identification                                │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  STAGE 4: THREAT ANALYSIS                               │   │
│   │  Анализ угроз                                           │   │
│   │                                                         │   │
│   │  • Threat intelligence                                  │   │
│   │  • Attack patterns (CAPEC)                              │   │
│   │  • Threat actors                                        │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  STAGE 5: VULNERABILITY ANALYSIS                        │   │
│   │  Анализ уязвимостей                                     │   │
│   │                                                         │   │
│   │  • Vulnerability scanning                               │   │
│   │  • Code review findings                                 │   │
│   │  • Known CVEs                                           │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  STAGE 6: ATTACK MODELING & SIMULATION                  │   │
│   │  Моделирование и симуляция атак                         │   │
│   │                                                         │   │
│   │  • Attack trees                                         │   │
│   │  • Attack scenarios                                     │   │
│   │  • Exploit analysis                                     │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  STAGE 7: RISK & IMPACT ANALYSIS                        │   │
│   │  Анализ рисков и воздействия                            │   │
│   │                                                         │   │
│   │  • Risk scoring                                         │   │
│   │  • Business impact                                      │   │
│   │  • Countermeasures                                      │   │
│   │  • Residual risk                                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Когда использовать PASTA

**Подходит для:**
- Крупных организаций с ресурсами
- Compliance-heavy environments
- Критичных систем (финансы, healthcare)
- Когда нужна связь с бизнес-контекстом

**Не подходит для:**
- Быстрых итераций в agile
- Маленьких команд без security expertise
- MVP и прототипов

**Преимущества:**
- Thorough и comprehensive
- Связывает техническое с бизнесом
- End-to-end (включает mitigation)
- Совместим с DevOps

**Недостатки:**
- Сложный и resource-intensive
- Требует много данных
- Может замедлить разработку

---

## DREAD: Количественная оценка угроз

DREAD — модель для скоринга угроз, разработанная Microsoft в 2003 году. Microsoft позже отказалась от неё из-за субъективности, но модель до сих пор используется.

### Компоненты DREAD

```
┌─────────────────────────────────────────────────────────────────┐
│                    DREAD SCORING                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   D  DAMAGE POTENTIAL (Потенциальный ущерб)                      │
│      "Насколько серьёзны последствия?"                           │
│      0: Нет ущерба                                               │
│      5: Раскрытие sensitive данных                               │
│      10: Полный контроль над системой                            │
│                                                                  │
│   R  REPRODUCIBILITY (Воспроизводимость)                         │
│      "Насколько легко воспроизвести атаку?"                      │
│      0: Очень сложно, требует специфических условий              │
│      5: Воспроизводится при определённых условиях                │
│      10: Воспроизводится всегда                                  │
│                                                                  │
│   E  EXPLOITABILITY (Эксплуатируемость)                          │
│      "Насколько сложно провести атаку?"                          │
│      0: Требует advanced skills и custom tools                   │
│      5: Требует некоторых навыков                                │
│      10: Может провести beginner                                 │
│                                                                  │
│   A  AFFECTED USERS (Затронутые пользователи)                    │
│      "Какой процент пользователей затронут?"                     │
│      0: Никто                                                    │
│      5: Некоторые пользователи                                   │
│      10: Все пользователи                                        │
│                                                                  │
│   D  DISCOVERABILITY (Обнаруживаемость)                          │
│      "Насколько легко обнаружить уязвимость?"                    │
│      0: Очень сложно обнаружить                                  │
│      5: Можно найти при целенаправленном поиске                  │
│      10: Публично известна или очевидна                          │
│                                                                  │
│   ───────────────────────────────────────────────────────────    │
│                                                                  │
│   RISK SCORE = (D + R + E + A + D) / 5                           │
│                                                                  │
│   0-3:  LOW                                                      │
│   4-6:  MEDIUM                                                   │
│   7-10: HIGH                                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Пример DREAD-оценки

```
Угроза: SQL Injection в login form

D (Damage):        9  — Доступ ко всей БД, включая credentials
R (Reproducibility): 9  — Воспроизводится каждый раз
E (Exploitability):  8  — sqlmap автоматизирует атаку
A (Affected Users):  10 — Все пользователи системы
D (Discoverability): 7  — Automated scanners находят

RISK SCORE = (9 + 9 + 8 + 10 + 7) / 5 = 8.6 = HIGH
```

### Критика DREAD

**Почему Microsoft отказалась:**
1. **Субъективность:** Разные эксперты дают разные оценки
2. **Равные веса:** Все компоненты весят одинаково, хотя Damage часто важнее
3. **Discoverability controversy:** Включение "обнаруживаемости" противоречит принципу Керкгоффса

**Альтернативы:**
- CVSS (Common Vulnerability Scoring System)
- OWASP Risk Rating Methodology
- Custom risk matrices

---

## Attack Trees

Attack trees — структурированный способ анализа путей достижения атакующим своей цели. Популяризированы Bruce Schneier в 1999 году.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ATTACK TREE: Украсть credentials              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    ┌───────────────────────┐                     │
│                    │   GOAL: Получить      │                     │
│                    │   credentials         │                     │
│                    │   пользователя        │                     │
│                    └───────────┬───────────┘                     │
│                                │                                 │
│               ┌────────────────┼────────────────┐                │
│               │                │                │                │
│               ▼                ▼                ▼                │
│        ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│        │ Phishing │     │ Brute    │     │ Steal    │            │
│        │ [OR]     │     │ Force    │     │ from     │            │
│        │          │     │ [OR]     │     │ Storage  │            │
│        └────┬─────┘     └────┬─────┘     │ [OR]     │            │
│             │                │           └────┬─────┘            │
│        ┌────┴────┐      ┌────┴────┐          │                   │
│        │         │      │         │     ┌────┴────┐              │
│        ▼         ▼      ▼         ▼     ▼         ▼              │
│   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│   │ Email  │ │ SMS    │ │Password│ │Credential││ Memory │ │ Logs  │
│   │Phishing│ │Phishing│ │Spray   │ │ Stuffing ││ Dump   │ │       │
│   │        │ │        │ │        │ │          ││        │ │       │
│   │Cost:$10│ │Cost:$50│ │Cost:$5 │ │ Cost:$0  ││Cost:$200│ │Cost:$0│
│   │Skill:L │ │Skill:M │ │Skill:L │ │ Skill:L  ││Skill:H │ │Skill:L│
│   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
│                                                                  │
│   Аннотации:                                                     │
│   • [OR] — достаточно одного пути                                │
│   • [AND] — требуются оба условия                                │
│   • Cost — стоимость атаки                                       │
│   • Skill — требуемый уровень (L/M/H)                            │
│                                                                  │
│   Вывод: Cheapest path = Credential Stuffing (Cost:$0, Skill:L)  │
│   → Приоритетная угроза для митигации                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Преимущества Attack Trees

1. **Визуализация:** Легко понять и обсуждать
2. **What-if анализ:** Можно моделировать эффект countermeasures
3. **Приоритизация:** Видно cheapest/easiest attack paths
4. **Переиспользование:** Деревья можно использовать для похожих систем

### Построение Attack Tree

1. **Определи goal (корень):** Чего хочет достичь атакующий?
2. **Decompose:** Какими способами можно достичь goal?
3. **Refine:** Разбей каждый способ на под-шаги
4. **Annotate:** Добавь cost, skill, detection difficulty
5. **Analyze:** Найди cheapest/easiest paths
6. **Mitigate:** Добавь countermeasures к критичным paths

---

## LINDDUN: Моделирование угроз приватности

LINDDUN — фреймворк для privacy threat modeling, разработанный KU Leuven. Включён в ISO 27550.

```
┌─────────────────────────────────────────────────────────────────┐
│                    LINDDUN CATEGORIES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   L  LINKABILITY                                                 │
│      Можно ли связать два элемента данных?                       │
│      Пример: Связать покупки пользователя по IP                  │
│                                                                  │
│   I  IDENTIFIABILITY                                             │
│      Можно ли идентифицировать конкретного человека?             │
│      Пример: Re-identification из "анонимных" данных             │
│                                                                  │
│   N  NON-REPUDIATION (нежелательная)                             │
│      Нельзя отрицать действие (проблема для privacy!)            │
│      Пример: Blockchain транзакции публичны навсегда             │
│                                                                  │
│   D  DETECTABILITY                                               │
│      Можно ли обнаружить существование данных?                   │
│      Пример: Метаданные показывают, что файл существует          │
│                                                                  │
│   D  DISCLOSURE OF INFORMATION                                   │
│      Раскрытие данных неавторизованным сторонам                  │
│      Пример: Data breach                                         │
│                                                                  │
│   U  UNAWARENESS                                                 │
│      Пользователь не знает о сборе/обработке данных              │
│      Пример: Tracking без consent                                │
│                                                                  │
│   N  NON-COMPLIANCE                                              │
│      Нарушение privacy законов и политик                         │
│      Пример: Нарушение GDPR                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### LINDDUN vs STRIDE

| Аспект | STRIDE | LINDDUN |
|--------|--------|---------|
| Фокус | Security | Privacy |
| Non-repudiation | Желательна (для аудита) | Нежелательна (для privacy) |
| Confidentiality | Information Disclosure | Disclosure + Linkability + Identifiability |
| Scope | Технические угрозы | Privacy + Compliance |

### Когда использовать LINDDUN

- Приложения, обрабатывающие PII
- GDPR/CCPA compliance
- Healthcare, fintech
- Социальные сети
- IoT устройства

---

## Инструменты Threat Modeling

### Сравнение инструментов

```
┌─────────────────────────────────────────────────────────────────┐
│                 THREAT MODELING TOOLS COMPARISON                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┬───────────────┬───────────────┬──────────┐│
│   │                 │ MS Threat     │ OWASP Threat  │ Threagile││
│   │                 │ Modeling Tool │ Dragon        │          ││
│   ├─────────────────┼───────────────┼───────────────┼──────────┤│
│   │ Cost            │ Free          │ Free (OWASP)  │ Free     ││
│   │ Platform        │ Windows only  │ Web/Desktop   │ CLI/API  ││
│   │ Methodology     │ STRIDE        │ STRIDE/       │ STRIDE   ││
│   │                 │               │ LINDDUN/CIA   │          ││
│   │ Output          │ Reports       │ Reports       │ Reports  ││
│   │                 │               │               │ + Diagrams│
│   │ CI/CD           │ No            │ Partial       │ Yes      ││
│   │ Integration     │               │               │          ││
│   │ Learning Curve  │ Low           │ Low-Medium    │ Medium   ││
│   │ As-Code         │ No            │ No            │ Yes      ││
│   │                 │               │               │ (YAML)   ││
│   └─────────────────┴───────────────┴───────────────┴──────────┘│
│                                                                  │
│   Другие инструменты:                                            │
│   • IriusRisk — enterprise, наиболее usable (по исследованиям)   │
│   • OWASP pytm — Python, as-code                                 │
│   • draw.io — general purpose (ручной анализ)                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Microsoft Threat Modeling Tool

**Преимущества:**
- Встроенные шаблоны для Azure, generic, SDL
- Auto-generates threats по STRIDE
- Хорошая документация

**Недостатки:**
- Windows only
- Нет CI/CD интеграции
- Не обновляется активно

### OWASP Threat Dragon

**Преимущества:**
- Open source (OWASP)
- Web и desktop версии
- Поддерживает STRIDE, LINDDUN, CIA, PLOT4ai
- Активная разработка (2024: завершена функциональность v2)

**Недостатки:**
- Несовместим с другими форматами (pytm, Threagile)
- Менее feature-rich чем enterprise tools

### Threagile

**Преимущества:**
- As-code (YAML) — можно хранить в git
- 40+ built-in risk rules
- CI/CD интеграция (CLI или REST)
- Автоматическая генерация диаграмм

**Недостатки:**
- Требует изучения YAML-формата
- Меньше community support

```yaml
# Пример Threagile YAML
title: E-Commerce Platform

data_assets:
  customer_data:
    description: Customer PII
    usage: business
    quantity: many
    confidentiality: confidential
    integrity: critical
    availability: important

technical_assets:
  web_server:
    description: Frontend web server
    type: process
    usage: business
    size: application
    technology: web-application
    data_assets_processed:
      - customer_data
    communication_links:
      api_server_link:
        target: api_server
        protocol: https
        authentication: token

trust_boundaries:
  dmz:
    description: DMZ network zone
    type: network-cloud-security-group
    technical_assets_inside:
      - web_server
```

---

## Практический процесс Threat Modeling

### Шаг 1: Подготовка

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREPARATION CHECKLIST                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  □ Определить scope (что анализируем)                            │
│  □ Собрать участников:                                           │
│    • Developers (знают реализацию)                               │
│    • Architects (знают design decisions)                         │
│    • Product owners (знают бизнес-контекст)                      │
│    • Security (знают угрозы и mitigations)                       │
│  □ Подготовить материалы:                                        │
│    • Architecture diagrams                                       │
│    • Data flow documentation                                     │
│    • Existing security controls                                  │
│  □ Выделить время (2-4 часа для начальной сессии)                │
│  □ Выбрать инструмент (или whiteboard для начала)                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Шаг 2: Создание DFD

1. Идентифицируй **External Entities** (users, external systems)
2. Определи **Processes** (компоненты, обрабатывающие данные)
3. Найди **Data Stores** (БД, файлы, кэши)
4. Нарисуй **Data Flows** между элементами
5. Установи **Trust Boundaries**

**Правило:** Start high, then go low. Сначала обзорная диаграмма, потом детализация по subsystems.

### Шаг 3: STRIDE-анализ

Для каждого элемента DFD и каждого пересечения trust boundary:

```python
# Псевдокод STRIDE-анализа

for element in dfd.elements:
    for threat_type in ['Spoofing', 'Tampering', 'Repudiation',
                        'Information Disclosure', 'DoS', 'EoP']:

        if is_applicable(element, threat_type):
            threat = Threat(
                type=threat_type,
                element=element,
                description=describe_threat(element, threat_type),
                impact=assess_impact(),
                likelihood=assess_likelihood()
            )

            if not has_existing_mitigation(threat):
                threats.append(threat)
```

### Шаг 4: Приоритизация угроз

Используй DREAD, CVSS или custom matrix:

```
┌────────────────────────────────────────────────────────────────┐
│                 PRIORITIZATION MATRIX                           │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Threat                          Impact   Likelihood   Score   │
│   ─────────────────────────────────────────────────────────────│
│   SQL Injection in login          HIGH     HIGH         P1      │
│   Session fixation                HIGH     MEDIUM       P1      │
│   Verbose error messages          MEDIUM   HIGH         P2      │
│   Missing rate limiting           MEDIUM   MEDIUM       P2      │
│   Outdated TLS version            LOW      HIGH         P3      │
│                                                                 │
│   P1 = Must fix before release                                  │
│   P2 = Should fix, can defer with risk acceptance               │
│   P3 = Nice to have, backlog                                    │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Шаг 5: Определение Mitigations

Для каждой угрозы определи:

1. **Mitigation strategy:** Mitigate, Transfer, Accept, Avoid
2. **Specific controls:** Что конкретно внедрить
3. **Owner:** Кто ответственен
4. **Timeline:** Когда будет готово
5. **Verification:** Как проверить

```
Threat: SQL Injection in login form
Priority: P1

Mitigation:
  Strategy: Mitigate
  Controls:
    - Use parameterized queries (ORM)
    - Input validation (allowlist)
    - WAF rule for SQL patterns
  Owner: Backend team
  Timeline: Sprint 24
  Verification:
    - Code review checklist
    - SAST scan (Semgrep)
    - DAST scan (OWASP ZAP)
    - Manual pentest
```

### Шаг 6: Валидация и итерация

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION CHECKLIST                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Механическая проверка:                                          │
│  □ Есть DFD?                                                     │
│  □ Все trust boundaries определены?                              │
│  □ Для каждого элемента проверены все STRIDE категории?          │
│  □ Угрозы задокументированы?                                     │
│  □ Mitigations определены для high/critical угроз?               │
│                                                                  │
│  Качественная проверка:                                          │
│  □ Участники согласны с результатами?                            │
│  □ Нет очевидных пропусков?                                      │
│  □ Mitigations реалистичны?                                      │
│  □ Рекомендовал бы этот процесс коллеге?                         │
│                                                                  │
│  Итерация:                                                       │
│  □ Запланирована следующая сессия (при изменениях)?              │
│  □ Threat model обновляется при architectural changes?           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Типичные ошибки

### Ошибка 1: Checkbox exercise

**Проблема:** Threat modeling как формальность, без глубокого анализа.

**Признаки:**
- Сессия < 30 минут
- Только security team участвует
- Generic угрозы без специфики системы

**Решение:** Diverse perspectives, достаточное время, real discussion.

### Ошибка 2: Нет follow-up

**Проблема:** Угрозы идентифицированы, но ничего не сделано.

**Признаки:**
- Threat model в drawer
- Нет tracking mitigations
- Нет verification

**Решение:** Integrate в JIRA/backlog, track как technical debt.

### Ошибка 3: One-time activity

**Проблема:** Threat model сделан один раз и забыт.

**Признаки:**
- Архитектура изменилась, threat model — нет
- Новые features без threat analysis

**Решение:** Threat modeling как часть SDLC, trigger при изменениях.

### Ошибка 4: Слишком высокий уровень

**Проблема:** DFD слишком абстрактная, угрозы generic.

**Признаки:**
- "Attacker may gain access" — к чему? как?
- Нет конкретных attack vectors

**Решение:** Drill down к конкретным components и data flows.

---

## Мифы и заблуждения

### Миф 1: "Threat modeling — только для security экспертов"

**Реальность:** STRIDE разработан так, чтобы использовать могли developers без security background. Diverse team (dev + security + product) даёт лучшие результаты.

### Миф 2: "Threat modeling занимает слишком много времени"

**Реальность:** 2-4 часовая сессия может сэкономить недели рефакторинга. ROI до 4,900%. Gartner: 66% команд увидели снижение breaches после shift-left.

### Миф 3: "Достаточно одного threat modeling в начале проекта"

**Реальность:** Threat model должен обновляться при:
- Новых features
- Architectural changes
- Новых integrations
- Обнаружении incidents

### Миф 4: "Автоматические tools заменяют ручной анализ"

**Реальность:** Tools помогают, но не заменяют human judgment. Они находят известные patterns, но не понимают бизнес-контекст.

### Миф 5: "Если нет уязвимостей в коде — threat modeling не нужен"

**Реальность:** Threat modeling находит architectural и design flaws, которые SAST/DAST не видят. Например: неправильное размещение trust boundaries, избыточные привилегии, отсутствие defense in depth.

---

## Интеграция в SDLC

```
┌─────────────────────────────────────────────────────────────────┐
│             THREAT MODELING В SDLC                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   DESIGN PHASE                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  • Initial threat model                                 │   │
│   │  • Architecture review                                  │   │
│   │  • Security requirements                                │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   DEVELOPMENT PHASE                                              │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  • Update threat model при изменениях                   │   │
│   │  • Implement mitigations                                │   │
│   │  • Code review с security focus                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   TESTING PHASE                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  • Verify mitigations работают                          │   │
│   │  • Security testing (SAST/DAST)                         │   │
│   │  • Penetration testing на основе threat model           │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   DEPLOYMENT & OPERATIONS                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  • Monitoring на основе identified threats              │   │
│   │  • Incident response informed by threat model           │   │
│   │  • Continuous improvement                               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Triggers для обновления Threat Model

1. **New feature** — особенно с новыми data flows
2. **New integration** — третьи стороны, APIs
3. **Architecture change** — новые компоненты, изменение trust boundaries
4. **Security incident** — может выявить пропущенные угрозы
5. **Compliance requirement** — новые regulatory demands
6. **Periodic review** — минимум раз в год

---

## Метрики Threat Modeling

```
┌─────────────────────────────────────────────────────────────────┐
│                THREAT MODELING METRICS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   PROCESS METRICS                                                │
│   • % проектов с threat model                                    │
│   • Время на threat modeling session                             │
│   • % угроз с defined mitigations                                │
│   • Time to update threat model при изменениях                   │
│                                                                  │
│   QUALITY METRICS                                                │
│   • Threats identified per session                               │
│   • % угроз, найденных threat modeling vs в production          │
│   • False positive rate (угрозы, которые не реальны)             │
│   • Coverage (% components analyzed)                             │
│                                                                  │
│   OUTCOME METRICS                                                │
│   • Cost per issue avoided                                       │
│   • Vulnerabilities found later that should have been caught     │
│   • Time to remediate (для issues из threat model vs other)      │
│   • Security incidents related to areas without threat model     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Куда дальше (Навигация)

### Если здесь впервые

→ [[security-fundamentals]] — Основы безопасности (CIA Triad, Defense in Depth)

### Если понял и хочешь практиковать

→ [[web-security-owasp]] — OWASP Top 10 — конкретные угрозы для веб
→ [[security-api-protection]] — Защита API endpoints
→ [[mobile-security-owasp]] — OWASP Mobile Top 10

### Для DevSecOps

→ [[devsecops]] — Интеграция security в CI/CD
→ [[security-incident-response]] — Что делать, когда угроза реализовалась

### Инструменты

- [Microsoft Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/)
- [Threagile](https://threagile.io/)

---

## Связанные материалы

| Материал | Связь |
|----------|-------|
| [[security-fundamentals]] | CIA Triad — то, что защищает STRIDE |
| [[web-security-owasp]] | Конкретные угрозы для веб-приложений |
| [[security-api-protection]] | Защита API endpoints |
| [[mobile-security-owasp]] | Угрозы для мобильных приложений |
| [[devsecops]] | Интеграция threat modeling в CI/CD |
| [[authentication-authorization]] | Защита от Spoofing и EoP |

---

## Источники

- [Adam Shostack's Four Question Framework](https://shostack.org/blog/four-question-frame/)
- [STRIDE Model - Wikipedia](https://en.wikipedia.org/wiki/STRIDE_model)
- [STRIDE Threat Modeling - IriusRisk](https://www.iriusrisk.com/resources-blog/threat-modeling-methodology-stride)
- [OWASP Threat Modeling Process](https://owasp.org/www-community/Threat_Modeling_Process)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [PASTA Threat Modeling - VerSprite](https://versprite.com/blog/what-is-pasta-threat-modeling/)
- [DREAD Risk Assessment - Wikipedia](https://en.wikipedia.org/wiki/DREAD_(risk_assessment_model))
- [Attack Trees - Bruce Schneier](https://www.schneier.com/academic/archives/1999/12/attack_trees.html)
- [LINDDUN Privacy Threat Modeling](https://linddun.org/)
- [Threat Modeling ROI - Security Compass](https://www.securitycompass.com/blog/measuring-threat-modeling-roi/)
- [Shift Left Security - Fortinet](https://www.fortinet.com/resources/cyberglossary/shift-left-security)
- [Top 10 Threat Modeling Tools 2024 - daily.dev](https://daily.dev/blog/top-10-threat-modeling-tools-compared-2024)
- [Data Flow Diagrams in Threat Modeling](https://threat-modeling.com/data-flow-diagrams-in-threat-modeling/)

---

## Связь с другими темами

[[security-fundamentals]] — фундамент, на котором строится threat modeling. CIA Triad (Confidentiality, Integrity, Availability) напрямую соответствует категориям STRIDE: Spoofing нарушает аутентичность, Tampering — целостность, Information Disclosure — конфиденциальность, Denial of Service — доступность. Без понимания базовых принципов безопасности невозможно грамотно идентифицировать угрозы и оценивать их критичность. Рекомендуется изучить security-fundamentals перед погружением в threat modeling.

[[mobile-security-owasp]] — OWASP Mobile Top 10 предоставляет конкретный каталог угроз, специфичных для мобильных приложений, который используется при threat modeling мобильных систем. При построении Data Flow Diagrams для мобильных приложений знание M1-M10 позволяет систематически идентифицировать угрозы на каждом элементе DFD. Threat modeling определяет методологию анализа, а Mobile Top 10 наполняет её конкретными паттернами атак — эти знания дополняют друг друга.

[[architecture-resilience-patterns]] — паттерны устойчивости (Circuit Breaker, Bulkhead, Retry) являются конкретными контрмерами для угроз категории Denial of Service из STRIDE. При моделировании угроз важно знать, какие архитектурные решения доступны для митигации, а resilience patterns предоставляют проверенные подходы к защите от нарушения доступности. Рекомендуется изучать параллельно с threat modeling для формирования полного набора контрмер.

[[web-security-owasp]] — OWASP Top 10 для веб-приложений даёт конкретные примеры уязвимостей (Broken Access Control, Injection, SSRF), которые должны быть идентифицированы при STRIDE-анализе веб-систем. Каждая категория OWASP Top 10 может быть отнесена к одной или нескольким категориям STRIDE, что делает эти фреймворки взаимодополняющими. Понимание конкретных уязвимостей из OWASP Top 10 значительно повышает качество threat modeling сессий.

[[authentication-authorization]] — глубокое понимание механизмов аутентификации и авторизации критично для анализа угроз Spoofing и Elevation of Privilege из STRIDE. При threat modeling каждого пересечения trust boundary необходимо оценивать, насколько надёжно реализованы AuthN/AuthZ. Знание конкретных механизмов (MFA, OAuth, RBAC) позволяет предлагать эффективные контрмеры при обнаружении угроз.

[[security-incident-response]] — threat model является входными данными для планирования incident response: идентифицированные угрозы определяют, какие playbooks нужно подготовить, какие IOC мониторить и какие severity levels назначать. Когда инцидент происходит, threat model помогает быстрее определить вектор атаки и масштаб воздействия. Обратная связь из post-mortem обогащает threat model новыми угрозами.

---

## Источники и дальнейшее чтение

- Shostack A. (2014). *Threat Modeling: Designing for Security.* Wiley. — основополагающая книга по threat modeling, автор Four Question Framework. Обязательна для всех, кто проводит моделирование угроз.
- Anderson R. (2020). *Security Engineering: A Guide to Building Dependable Distributed Systems.* 3rd Edition. Wiley. — фундаментальный труд по инженерии безопасности, охватывающий threat modeling в контексте проектирования надёжных систем.
- McGraw G. (2006). *Software Security: Building Security In.* Addison-Wesley. — классическая работа о встраивании безопасности в жизненный цикл разработки, включая architectural risk analysis как форму threat modeling.
- Stallings W. (2017). *Cryptography and Network Security: Principles and Practice.* 7th Edition. Pearson. — для понимания криптографических контрмер, которые применяются при митигации угроз, выявленных через STRIDE.

---

## Проверь себя

> [!question]- Почему Microsoft отказалась от модели DREAD, хотя она до сих пор широко используется в индустрии?
> Главная причина — субъективность оценок. Разные эксперты присваивают разные баллы одной и той же угрозе, потому что все пять компонентов (Damage, Reproducibility, Exploitability, Affected Users, Discoverability) оцениваются качественно. Кроме того, равные веса компонентов не отражают реальность — Damage Potential обычно важнее Discoverability. Включение Discoverability также противоречит принципу Керкгоффса: безопасность системы не должна зависеть от секретности её устройства.

> [!question]- Вы проектируете мобильное приложение с офлайн-режимом, которое хранит данные локально и синхронизирует их с сервером. Постройте список trust boundaries для DFD этого приложения и укажите, какие категории STRIDE наиболее критичны на каждой границе.
> Основные trust boundaries: (1) User Input - Application — критичны Spoofing (подделка identity) и Tampering (модификация ввода); (2) Application - Local Storage — критичны Tampering (изменение локальной БД) и Information Disclosure (незашифрованные данные на устройстве); (3) Application - Network (Internet) — критичны Tampering (MITM), Information Disclosure (перехват данных), Denial of Service (отсутствие сети); (4) Network - Backend API — критичны Spoofing (подмена запросов), Elevation of Privilege (горизонтальная эскалация при синхронизации чужих данных). Офлайн-режим усиливает угрозу Tampering на локальном хранилище, так как у атакующего есть неограниченное время для модификации данных.

> [!question]- Как принципы resilience-паттернов (Circuit Breaker, Bulkhead) связаны с митигацией угроз категории Denial of Service в STRIDE? Приведите конкретный сценарий.
> Resilience-паттерны являются прямыми контрмерами для DoS-угроз. Сценарий: в e-commerce платформе сервис оплаты зависит от внешнего Payment Gateway. Атакующий перегружает Gateway медленными запросами (Slowloris). Без Circuit Breaker запросы к Gateway копятся, исчерпывая пул соединений API-сервера, что каскадно роняет всю систему. С Circuit Breaker: после N таймаутов цепь размыкается, сервис оплаты возвращает graceful error, а остальные функции (каталог, корзина) продолжают работать. Bulkhead изолирует пул соединений к Gateway от остальных HTTP-клиентов, предотвращая каскадный отказ.

> [!question]- Команда провела STRIDE-анализ и идентифицировала 15 угроз, но через три месяца произошёл инцидент с угрозой, которая не была в списке. Проанализируйте, какие системные причины могли к этому привести.
> Возможные системные причины: (1) DFD была слишком абстрактной — высокоуровневые диаграммы пропускают конкретные data flows и attack vectors; (2) Отсутствие diverse perspectives — если участвовали только разработчики без security-специалиста или product owner, часть контекста была упущена; (3) Threat model не обновлялся — за три месяца могли появиться новые features, интеграции или architectural changes, создавшие новые attack surfaces; (4) Анализировались только известные паттерны — STRIDE помогает классифицировать, но не гарантирует полноту; (5) Отсутствие feedback loop — не было механизма обогащения threat model из post-mortem предыдущих инцидентов.

---

## Ключевые карточки

Что такое Trust Boundary и почему это ключевой элемент DFD?
?
Trust boundary — граница между зонами с разным уровнем доверия. Данные, пересекающие эту границу, должны быть аутентифицированы, авторизованы и валидированы. Именно на trust boundaries возникает большинство угроз, поэтому STRIDE-анализ фокусируется на этих точках.

Перечислите шесть категорий угроз STRIDE и какой принцип безопасности нарушает каждая.
?
Spoofing нарушает Authenticity, Tampering — Integrity, Repudiation — Non-repudiation, Information Disclosure — Confidentiality, Denial of Service — Availability, Elevation of Privilege — Authorization.

Какие четыре стратегии работы с выявленными угрозами существуют?
?
Mitigate (устранить угрозу контрмерами), Transfer (передать риск, например через страховку или аутсорсинг), Accept (принять риск осознанно) и Avoid (избежать риска, отказавшись от функциональности).

Назовите Four Question Framework Адама Шостака.
?
(1) What are we working on? — определение scope через DFD; (2) What can go wrong? — идентификация угроз через STRIDE; (3) What are we going to do about it? — выбор mitigations; (4) Did we do a good job? — валидация через механическую проверку и ретроспективу.

Чем PASTA отличается от STRIDE и когда она предпочтительнее?
?
PASTA — семиэтапная методология, которая объединяет бизнес-контекст с техническим анализом, включая threat intelligence и симуляцию атак. STRIDE — мнемоника для классификации угроз. PASTA предпочтительнее для крупных организаций, compliance-heavy систем и критичной инфраструктуры, где нужна связь угроз с бизнес-целями.

В чём ключевое различие между STRIDE и LINDDUN?
?
STRIDE фокусируется на безопасности (security), а LINDDUN — на приватности (privacy). Главный парадокс: Non-repudiation в STRIDE желательна (аудит действий), а в LINDDUN — нежелательна (нарушает privacy пользователя). LINDDUN также добавляет Linkability, Identifiability и Unawareness, которых нет в STRIDE.

Какие компоненты входят в DREAD и как рассчитывается итоговый скор?
?
Damage Potential, Reproducibility, Exploitability, Affected Users, Discoverability. Итоговый скор = (D+R+E+A+D)/5. Диапазон 0-3 — Low, 4-6 — Medium, 7-10 — High. Модель критикуют за субъективность и равные веса компонентов.

Что такое Attack Tree и какую ключевую информацию она даёт для приоритизации?
?
Attack Tree — структурированное представление путей достижения атакующим цели с узлами OR (достаточно одного пути) и AND (нужны оба условия). Каждый лист аннотируется стоимостью (cost) и требуемым навыком (skill). Ключевая ценность — нахождение cheapest/easiest attack path, который должен быть приоритетом для митигации.

К каким элементам DFD применяются все шесть категорий STRIDE?
?
Только Process подвержен всем шести категориям STRIDE (S, T, R, I, D, E). External Entity — только Spoofing и Repudiation. Data Store — Tampering, Information Disclosure, DoS и частично Repudiation. Data Flow — Tampering, Information Disclosure, DoS.

Когда threat model нужно обновлять?
?
При добавлении новых features (особенно с новыми data flows), новых интеграциях с третьими сторонами, архитектурных изменениях (новые компоненты, изменение trust boundaries), после security-инцидентов, при новых compliance-требованиях, а также при периодическом ревью минимум раз в год.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Фундамент безопасности | [[security-fundamentals]] | CIA Triad и Defense in Depth — база, на которой строится STRIDE-анализ |
| Мобильные угрозы | [[mobile-security-owasp]] | Конкретный каталог M1-M10 для наполнения threat model мобильных приложений |
| Устойчивость архитектуры | [[architecture-resilience-patterns]] | Circuit Breaker, Bulkhead — контрмеры для митигации Denial of Service |
| Веб-уязвимости | [[web-security-owasp]] | OWASP Top 10 — конкретные угрозы для STRIDE-анализа веб-систем |
| Аутентификация и авторизация | [[authentication-authorization]] | Механизмы защиты от Spoofing и Elevation of Privilege |
| Защита API | [[security-api-protection]] | Практические паттерны защиты API endpoints, выявленных при DFD-анализе |
| Реагирование на инциденты | [[security-incident-response]] | Планирование response на основе идентифицированных в threat model угроз |

---

*Обновлено: 2026-01-29*
*Версия: 1.0*

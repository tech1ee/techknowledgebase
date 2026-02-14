---
title: "Tech Lead: роль, обязанности, навыки"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
reading_time: 32
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
difficulty: intermediate
target-role: [senior, tech-lead]
teaches:
  - Обязанности Tech Lead
  - Различия с EM и Staff
  - Как стать Tech Lead
sources: [staffeng, leaddev, pragmaticengineer, patkua]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[ic-vs-management]]"
  - "[[em-fundamentals]]"
prerequisites:
  - "[[ic-vs-management]]"
---

# Tech Lead: роль, обязанности, навыки

> **TL;DR:** Tech Lead — hybrid роль между IC и management. Отвечает за **техническое направление команды** без formal people management. Это не менеджер, но и не чистый IC. Идеальная роль для тех, кто хочет leadership без полного ухода от кода.
>
> **Главное отличие от EM:** Tech Lead владеет **технической** стороной команды (architecture, quality, tech decisions). EM владеет **people** стороной (hiring, performance, career growth).
>
> **Распространённая ошибка:** Думать что Tech Lead = "лучший кодер в команде". Нет. Tech Lead = тот кто делает команду технически лучше.

---

## Зачем понимать эту роль?

### Типичная ситуация

Ты опытный Senior Engineer. Менеджер говорит: "Мы хотим сделать тебя Tech Lead нового проекта/команды". Без понимания роли:

**Без понимания:**
- Продолжаешь писать код как раньше, только больше
- Или наоборот — уходишь в meetings и перестаёшь кодировать
- Конфликт с EM о границах ответственности
- Команда не понимает, кто за что отвечает

**С пониманием:**
- Чётко разделяешь время: technical leadership + hands-on
- Ясная граница с EM (tech vs people)
- Команда знает к кому идти с какими вопросами
- Развиваешь навыки для следующего уровня

### Статистика

| Метрика | Значение | Источник |
|---------|----------|----------|
| % времени Tech Lead на код | 30-50% | Pragmatic Engineer |
| Tech Leads без formal reports | ~70% | Industry norm |
| Типичный experience для TL | 5-7 лет | Job postings |
| Tech Lead → Staff progression | ~40% | StaffEng |
| Tech Lead → EM progression | ~30% | Industry estimate |

---

## Для кого этот материал

| Роль | Приоритет | Рекомендация |
|------|-----------|--------------|
| **Mid Engineer** | Medium | Понять к чему готовиться |
| **Senior Engineer** | Critical | Часто следующий шаг |
| **New Tech Lead** | Critical | Onboarding в роль |
| **Engineering Manager** | High | Понять partnership с TL |

---

## Определение роли

### Tech Lead — это...

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TECH LEAD: DEFINITION                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                        ┌────────────────┐                               │
│                        │   TECH LEAD    │                               │
│                        └───────┬────────┘                               │
│                                │                                        │
│          ┌─────────────────────┼─────────────────────┐                 │
│          │                     │                     │                 │
│          ▼                     ▼                     ▼                 │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐           │
│   │  Technical  │      │  Technical  │      │  Delivery   │           │
│   │   Vision    │      │  Execution  │      │  Ownership  │           │
│   └─────────────┘      └─────────────┘      └─────────────┘           │
│                                                                          │
│   "Куда идём              "Как делаем           "Что поставляем        │
│    технически?"            правильно?"           в срок?"              │
│                                                                          │
│   • Architecture          • Code review         • Sprint planning      │
│   • Tech decisions        • Standards           • Dependencies         │
│   • Tech debt             • Mentoring           • Risk management      │
│   • Innovation            • Pairing             • Stakeholders         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Что Tech Lead НЕ делает (обычно)

- Performance reviews (это EM)
- Hiring decisions (совместно с EM)
- Career conversations (это EM)
- Salary discussions (это EM)
- Disciplinary actions (это EM)

---

## Tech Lead vs другие роли

### Tech Lead vs Senior Engineer

| Аспект | Senior Engineer | Tech Lead |
|--------|-----------------|-----------|
| **Focus** | Свои задачи и проекты | Успех всей команды |
| **Scope** | Feature/project level | Team/domain level |
| **Meetings** | 20-30% | 40-50% |
| **Coding** | 60-80% | 30-50% |
| **Mentoring** | Occasional | Regular responsibility |
| **Architecture** | Input | Ownership |
| **Stakeholders** | Minimal | Regular interaction |

### Tech Lead vs Engineering Manager

| Аспект | Tech Lead | Engineering Manager |
|--------|-----------|---------------------|
| **Primary focus** | Technology | People |
| **Direct reports** | Нет (обычно) | Да |
| **1-on-1s** | Mentoring (optional) | Performance mgmt (required) |
| **Hiring** | Technical evaluation | Full ownership |
| **Career growth** | Technical guidance | Career planning |
| **Coding** | 30-50% | 0-20% |
| **Performance reviews** | Input | Ownership |

### Tech Lead vs Staff Engineer

| Аспект | Tech Lead | Staff Engineer |
|--------|-----------|----------------|
| **Scope** | One team | Multiple teams / domain |
| **Attachment** | Embedded in team | Cross-team |
| **Delivery** | Responsible for team delivery | Advisory |
| **Meetings** | 40-50% | 30-50% |
| **Architecture** | Team-level | Org-level |
| **Reports to** | EM or Director | Director or VPE |

---

## Обязанности Tech Lead

### 1. Technical Vision (20% времени)

```
TECHNICAL VISION:

□ Определить architecture direction для команды
□ Принимать или facilitate key tech decisions
□ Поддерживать tech roadmap (совместно с Product)
□ Отслеживать tech debt и планировать reduction
□ Исследовать новые технологии (где релевантно)
```

**Пример артефактов:**
- Architecture Decision Records (ADRs)
- Technical roadmap document
- Tech debt inventory

### 2. Technical Execution (30% времени)

```
TECHNICAL EXECUTION:

□ Code review (thoughtful, educational)
□ Pair programming с junior/mid engineers
□ Design review для сложных features
□ Establish coding standards и conventions
□ Hands-on coding на critical paths
```

**Пример дня:**
- 2 часа: code review + feedback
- 1 час: pair programming с junior
- 1 час: design review meeting

### 3. Delivery Ownership (25% времени)

```
DELIVERY:

□ Sprint planning (technical scope)
□ Manage technical dependencies
□ Identify и escalate risks early
□ Unblock team members
□ Communicate с stakeholders (technical status)
```

**Пример:** Product хочет feature X к Q2. Tech Lead:
- Оценивает feasibility
- Предлагает alternatives если нужно
- Разбивает на technical milestones
- Отслеживает progress

### 4. Team Development (15% времени)

```
TEAM DEVELOPMENT:

□ Technical mentoring
□ Knowledge sharing sessions
□ Onboarding новых инженеров (technical)
□ Develop standards и best practices
□ Create learning opportunities
```

**Важно:** Это не people management. Tech Lead помогает команде расти **технически**.

### 5. Hands-on Coding (30-40% времени)

```
CODING:

□ Critical features / foundational code
□ Prototypes для tech decisions
□ Fixing complex bugs
□ Maintaining developer experience
```

**Важно:** Tech Lead должен оставаться technical. Без coding — теряется credibility и ability to make good decisions.

---

## День типичного Tech Lead

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TYPICAL DAY: TECH LEAD                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  08:30  Check Slack/PRs: что требует attention                          │
│                                                                          │
│  09:00  Stand-up: help unblock, identify risks                          │
│                                                                          │
│  09:30  Code review: 2-3 PRs с thoughtful feedback                     │
│         → Focus на архитектуру и обучение, не стиль                    │
│                                                                          │
│  10:30  Deep work: coding на critical feature                           │
│                                                                          │
│  12:00  Lunch                                                           │
│                                                                          │
│  13:00  Design review meeting: new feature architecture                 │
│         → Facilitate discussion, don't dictate                          │
│                                                                          │
│  14:00  Pair programming: help junior с tricky problem                  │
│                                                                          │
│  15:00  Stakeholder sync: technical status update                       │
│                                                                          │
│  15:30  Deep work: ADR for upcoming decision                            │
│                                                                          │
│  17:00  End of day: queue PRs for tomorrow                              │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│  Meetings: ~3.5 hours (35%)                                             │
│  Coding: ~3 hours (30%)                                                 │
│  Review/Mentoring: ~2 hours (20%)                                       │
│  Planning/Admin: ~1.5 hours (15%)                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Ключевые навыки Tech Lead

### Technical Skills

| Навык | Почему важен | Как развивать |
|-------|--------------|---------------|
| **System Design** | Принимать architecture decisions | Practice, читать case studies |
| **Code Review** | Поднимать quality всей команды | Осознанная практика, feedback loops |
| **Debugging** | Помогать команде с complex issues | Hands-on на сложных багах |
| **Tech Breadth** | Оценивать разные подходы | Читать, экспериментировать |

### Leadership Skills

| Навык | Почему важен | Как развивать |
|-------|--------------|---------------|
| **Communication** | Объяснять technical decisions | Писать RFCs, ADRs, документацию |
| **Facilitation** | Эффективные design reviews | Learn meeting facilitation |
| **Mentoring** | Растить команду | Осознанная практика с juniors |
| **Stakeholder Mgmt** | Manage expectations | Regular practice, feedback |

### Soft Skills

| Навык | Почему важен | Как развивать |
|-------|--------------|---------------|
| **Influence w/o Authority** | У тебя нет formal power | Build trust, show results |
| **Patience** | Люди учатся медленнее чем ты делаешь | Conscious practice |
| **Delegation** | Не можешь делать всё сам | Start small, build trust |

---

## Как стать Tech Lead

### Prerequisites

```
MINIMUM REQUIREMENTS:

□ Senior Engineer level (5+ лет опыта)
□ Strong technical skills в domain команды
□ Track record успешной delivery
□ Уважение peers (люди идут к тебе за советом)
□ Communication skills (можешь объяснить сложное)
```

### Path to Tech Lead

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PATH TO TECH LEAD                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STEP 1: Act like Tech Lead before the title                            │
│  ───────────────────────────────────────────                            │
│  • Do thoughtful code reviews                                           │
│  • Help juniors/mids without being asked                                │
│  • Volunteer for complex problems                                       │
│  • Write design docs                                                    │
│                                                                          │
│  STEP 2: Build visibility                                               │
│  ────────────────────────                                               │
│  • Communicate technical decisions clearly                              │
│  • Present at team meetings                                             │
│  • Write documentation others use                                       │
│                                                                          │
│  STEP 3: Talk to your manager                                           │
│  ────────────────────────────                                           │
│  • Express interest in TL role                                          │
│  • Ask for feedback on gaps                                             │
│  • Request stretch opportunities                                        │
│                                                                          │
│  STEP 4: Formal transition                                              │
│  ─────────────────────────                                              │
│  • New project/team lead opportunity                                    │
│  • Or: explicit TL title in current team                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Вопросы к менеджеру

```
"Я хочу расти в Tech Lead роль. Что для этого нужно?"

"Какие gaps ты видишь для TL?"

"Можем ли создать plan для следующих 6 месяцев?"

"Есть ли проекты где я могу попробовать TL responsibilities?"
```

---

## Распространённые ошибки

### Ошибка 1: "Я лучший кодер, значит я Tech Lead"

**Как выглядит:**
Tech Lead пишет весь сложный код сам, не делегирует.

**Почему проблема:**
- Bottleneck на Tech Lead
- Команда не растёт
- При уходе TL — всё ломается

**Как исправить:**
```
ПРАВИЛО: Твоя работа — сделать команду лучше,
         не писать весь код самому.

• Делегируй сложные задачи (с support)
• Учи, а не делай за других
• Твой код: 30-40%, не 80%
```

### Ошибка 2: Микроменеджмент в code review

**Как выглядит:**
Каждый PR получает 50+ комментариев о стиле, именовании.

**Почему проблема:**
- Демотивирует команду
- Замедляет delivery
- Не масштабируется

**Как исправить:**
```
FOCUS CODE REVIEW НА:
• Архитектуру и дизайн
• Потенциальные баги
• Обучение автора

НЕ FOCUS НА:
• Стилистические предпочтения → linter
• Мелочи которые не matter
```

### Ошибка 3: Уход в meetings, забрасывание coding

**Как выглядит:**
Tech Lead тратит 80% на meetings, не пишет код месяцами.

**Почему проблема:**
- Теряется technical judgment
- Потеря credibility в команде
- Не можешь оценить feasibility

**Как исправить:**
```
PROTECT CODING TIME:
• Block calendar для deep work (2-3 часа/день)
• Decline non-essential meetings
• Минимум 30% времени на hands-on
```

### Ошибка 4: Конфликт с EM о responsibilities

**Как выглядит:**
Tech Lead и EM оба пытаются влиять на решения команды без clear boundaries.

**Почему проблема:**
- Confusion в команде
- Политика вместо работы
- Frustrated обе стороны

**Как исправить:**
```
CLEAR BOUNDARIES:

TECH LEAD отвечает за:
• Architecture decisions
• Code quality
• Technical mentoring
• Sprint scope (technical)

EM отвечает за:
• Performance reviews
• Career growth
• Hiring decisions
• Team composition
```

---

## Tech Lead + EM Partnership

### Модели взаимодействия

**Model A: Tech Lead reports to EM (common)**
```
       EM
       │
    Tech Lead
       │
    Engineers
```

**Model B: Tech Lead и EM — peers (also common)**
```
    Director
     /    \
   EM    Tech Lead
    \    /
  Engineers
```

### Как работать эффективно вместе

| Тема | EM владеет | Tech Lead владеет | Совместно |
|------|------------|-------------------|-----------|
| **Hiring** | Process, offer | Technical eval | Interview panel |
| **Performance** | Reviews, PIP | Technical feedback | Calibration |
| **Planning** | Capacity, people | Tech scope | Sprint planning |
| **Growth** | Career paths | Technical skills | Development plans |

### Скрипт: Разговор с EM о boundaries

```
"Давай clarify наши responsibilities чтобы команда
 понимала к кому идти с какими вопросами.

Предлагаю:

Я (Tech Lead) отвечаю за:
- Architecture decisions
- Code quality standards
- Technical mentoring
- Sprint scope estimation

Ты (EM) отвечаешь за:
- Performance reviews
- Career conversations
- Hiring process
- Team composition

Совместно:
- Sprint planning
- Hiring decisions (tech eval + fit)
- Major incidents

Согласен?"
```

---

## Tech Lead → что дальше?

### Опции после Tech Lead

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TECH LEAD: NEXT STEPS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                         Tech Lead                                        │
│                             │                                            │
│            ┌────────────────┼────────────────┐                          │
│            │                │                │                          │
│            ▼                ▼                ▼                          │
│     ┌──────────┐     ┌──────────┐     ┌──────────┐                     │
│     │   Staff  │     │ Engineering│     │  Senior │                     │
│     │ Engineer │     │  Manager  │     │Tech Lead │                     │
│     └──────────┘     └──────────┘     └──────────┘                     │
│                                                                          │
│     IC Track          Mgmt Track       Hybrid Track                     │
│     (больше scope,    (people focus)   (larger team/                   │
│     меньше delivery)                    multiple TLs)                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Decision Framework

| Если тебе нравится... | Рассмотри... |
|-----------------------|--------------|
| Technical problems + broader scope | Staff Engineer |
| People development + team building | Engineering Manager |
| Tech Lead role + larger impact | Senior Tech Lead / Principal |

---

## Checklist: готов ли ты к Tech Lead

```
TECHNICAL READINESS:
□ Могу design'ить features end-to-end
□ Мои code reviews educational, не just критика
□ Peers приходят ко мне за technical советом
□ Понимаю trade-offs в архитектуре
□ Могу объяснить сложное простыми словами

LEADERSHIP READINESS:
□ Комфортно facilitate meetings
□ Могу influence без authority
□ Терпелив с людьми, которые учатся
□ Готов тратить время на чужой рост
□ Могу делегировать (не делать всё сам)

SOFT SKILLS:
□ Хорошие отношения с stakeholders
□ Могу говорить "нет" constructively
□ Справляюсь с ambiguity
□ Принимаю feedback gracefully

15+/15 = Ready for Tech Lead
10-14 = Close, work on gaps
<10 = Focus on Senior excellence first
```

---

## Связанные темы

### Prerequisites
- Опыт Senior Engineer

### Следующие шаги
- [[ic-vs-management]] — выбор дальнейшего пути
- [[staff-roles]] — если выбираешь IC track
- [[em-fundamentals]] — если выбираешь management

### Связи с другими разделами
- [[communication/giving-feedback]] — для code review
- [[communication/technical-presentations]] — для design reviews

---

## Источники

| # | Источник | Тип | Что взято |
|---|----------|-----|-----------|
| 1 | [10 Attributes of a Great Tech Lead](https://betterprogramming.pub/10-admirable-attributes-of-a-great-technical-lead-251d13a8843b) | Article | Core attributes |
| 2 | [Things I've Learnt as Tech Lead](https://minnenratta.wordpress.com/2017/01/25/things-i-have-learnt-as-the-software-engineering-lead-of-a-multinational/) | Article | Real experience |
| 3 | [StaffEng: Tech Lead Archetype](https://staffeng.com/guides/staff-archetypes) | Guide | TL vs Staff |
| 4 | [The Definition of a Tech Lead](https://www.patkua.com/blog/the-definition-of-a-tech-lead/) (Pat Kua) | Article | Role definition |
| 5 | [Pragmatic Engineer: Tech Lead](https://newsletter.pragmaticengineer.com/) | Newsletter | Time allocation |

### Дополнительное чтение
- **The Manager's Path** (Camille Fournier) — глава про Tech Lead
- **Staff Engineer** (Will Larson) — TL как один из archetypes
- **Talking with Tech Leads** (Pat Kua) — интервью с TLs

*Исследование проведено: 2026-01-18*

---

## Связь с другими темами

**[[ic-vs-management]]** — Tech Lead — это часто развилка, после которой инженер выбирает между IC track (Staff Engineer) и Management track (Engineering Manager). Понимание различий между треками помогает Tech Lead осознанно планировать следующий карьерный шаг. Tech Lead роль уникальна тем, что даёт опыт как технического лидерства, так и элементов management, что делает её идеальной "пробной площадкой" перед окончательным выбором.

**[[em-fundamentals]]** — Для Tech Lead, рассматривающего переход в Engineering Manager, em-fundamentals показывает, как изменится ежедневная работа. Если Tech Lead тратит 30-50% на код и 40-50% на meetings, то EM переходит к 0-20% кода и 60-80% meetings. Понимание этих различий и конкретных обязанностей EM (performance reviews, career conversations, hiring ownership) помогает Tech Lead оценить, готов ли он к такому сдвигу фокуса.

## Источники и дальнейшее чтение

- **Camille Fournier, "The Manager's Path" (2017)** — Содержит отдельную главу о роли Tech Lead, включая детальное описание обязанностей, распределения времени и типичных ошибок. Показывает Tech Lead как ступень в карьерной лестнице и объясняет, как эта роль связана с последующим выбором IC или management трека.
- **Will Larson, "Staff Engineer" (2022)** — Описывает Tech Lead как один из четырёх архетипов Staff Engineer (наряду с Architect, Solver и Right Hand). Помогает понять, как роль Tech Lead эволюционирует при расширении scope от одной команды к нескольким.
- **Patrick Lencioni, "The Five Dysfunctions of a Team" (2002)** — Хотя Tech Lead не является формальным менеджером, он значительно влияет на динамику команды. Понимание пяти дисфункций помогает Tech Lead распознавать проблемы в команде и работать с EM над их решением.

---

---

## Проверь себя

> [!question]- Почему утверждение "Tech Lead = лучший кодер в команде" является ошибочным?
> Tech Lead -- это не тот, кто пишет лучший код, а тот, кто делает команду технически лучше. Если TL берёт все сложные задачи себе, он становится bottleneck, команда не растёт, и при его уходе всё ломается. Задача TL -- делегировать, учить и поднимать уровень всей команды.

> [!question]- Tech Lead тратит 80% времени на meetings и не пишет код уже 2 месяца. Какие последствия это создаст?
> Потеря technical judgment (не может оценить feasibility), потеря credibility в команде, невозможность принимать обоснованные architecture decisions. Решение: блокировать 2-3 часа/день для deep work, decline non-essential meetings, поддерживать минимум 30% hands-on.

> [!question]- Как правильно разграничить ответственность между Tech Lead и EM?
> TL отвечает за технологию: architecture decisions, code quality, technical mentoring, sprint scope. EM отвечает за людей: performance reviews, career growth, hiring decisions, team composition. Совместно: sprint planning, hiring (tech eval + fit), major incidents. Чёткие границы предотвращают confusion в команде.

---

## Ключевые карточки

Какие три ключевых области ответственности Tech Lead?
?
1) Technical Vision (архитектура, tech decisions, tech debt), 2) Technical Execution (code review, standards, pair programming), 3) Delivery Ownership (sprint planning, dependencies, risk management). Плюс team development и hands-on coding.

Чем Tech Lead отличается от Staff Engineer?
?
Tech Lead embedded в одну команду с delivery ответственностью. Staff Engineer работает cross-team с advisory ролью. TL scope -- team-level architecture, Staff scope -- org-level architecture. Staff reports to Director/VPE, TL -- to EM or Director.

Какое оптимальное распределение времени Tech Lead?
?
Meetings: ~35%, Coding: ~30%, Review/Mentoring: ~20%, Planning/Admin: ~15%. Критично сохранять минимум 30% на hands-on coding для поддержания credibility и quality of technical decisions.

Какие карьерные пути открываются после Tech Lead?
?
Три основных: 1) Staff Engineer (IC track -- больше scope, меньше delivery), 2) Engineering Manager (management track -- people focus), 3) Senior Tech Lead (hybrid -- larger team, multiple TLs). Выбор зависит от того, что даёт больше энергии.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ic-vs-management]] | Определить дальнейший карьерный путь после TL |
| Углубиться | [[engineering-practices]] | Инженерные практики для поддержания quality |
| Смежная тема | [[giving-feedback]] | Навыки feedback для эффективного code review |
| Обзор | [[leadership-overview]] | Вернуться к карте раздела |

---

[[leadership-overview|← Leadership MOC]] | [[ic-vs-management|IC vs Management →]]

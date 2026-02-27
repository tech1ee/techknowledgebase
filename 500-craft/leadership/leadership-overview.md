---
title: "Tech Leadership: от Tech Lead до CTO"
created: 2026-01-18
modified: 2026-02-13
type: overview
reading_time: 17
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/leadership
  - type/overview
  - level/intermediate
related:
  - "[[cto-vs-vpe]]"
  - "[[ic-vs-management]]"
  - "[[first-90-days]]"
  - "[[one-on-one-meetings]]"
  - "[[hiring-engineers]]"
  - "[[building-engineering-team]]"
  - "[[tech-lead-role]]"
  - "[[scaling-engineering-org]]"
  - "[[tech-debt-management]]"
  - "[[leadership-interviews]]"
---

# Tech Leadership: от Tech Lead до CTO

> **Лидерство в технологиях** — это не просто менеджмент. Это умение создавать условия, в которых инженеры делают лучшую работу в своей жизни. 75% провалов проектов — организационные, не технические.

---

## Теоретические основы

### Лидерство в технологиях: научный контекст

> **Определение:** Technology Leadership — дисциплина на пересечении управления людьми (management), технической экспертизы (engineering) и организационного дизайна (systems thinking). Включает роли от Tech Lead до CTO и охватывает весь спектр от tactical execution до strategic direction.

John Kotter в *"What Leaders Really Do"* (Harvard Business Review, 1990) провёл фундаментальное различие: **Management** — это планирование, организация и контроль (making things run smoothly), **Leadership** — это определение направления, alignment людей и мотивация (driving change). В technology organizations эти функции часто переплетены, что делает роли EM, Tech Lead и CTO уникально сложными.

| Теоретическая основа | Автор | Ключевой вклад |
|---------------------|-------|----------------|
| Management vs Leadership | Kotter, 1990 | Direction + alignment + motivation |
| Servant Leadership | Greenleaf, 1970 | Leader serves the team first |
| Situational Leadership | Hersey & Blanchard, 1969 | Style adapts to situation |
| High Output Management | Andy Grove, 1983 | Manager's output = team's output |
| Psychological Safety | Edmondson, 1999 | Foundation of effective teams |

Andy Grove в *"High Output Management"* (1983) определил output менеджера как output его команды и организации, на которые он влияет. Это определение стало фундаментом engineering management: менеджер создаёт ценность не через собственный код, а через leverage — увеличение эффективности других людей.

---

## Quick Navigation: У меня вопрос про...

| Вопрос | Куда идти |
|--------|-----------|
| "В чём разница CTO и VP Engineering?" | [[cto-vs-vpe]] |
| "Стоит ли переходить в менеджмент?" | [[ic-vs-management]] → [[engineer-manager-pendulum]] |
| "Как провести первые 90 дней CTO/VPE?" | [[first-90-days]] |
| "Как проводить 1-on-1?" | [[one-on-one-meetings]] |
| "Как нанимать инженеров?" | [[hiring-engineers]] → [[interview-process-design]] |
| "Как строить команду с нуля?" | [[building-engineering-team]] |
| "Что такое Tech Lead?" | [[tech-lead-role]] |
| "Как масштабировать организацию?" | [[scaling-engineering-org]] |
| "Как управлять техническим долгом?" | [[tech-debt-management]] |
| "Как готовиться к интервью на EM/CTO?" | [[leadership-interviews]] |

---

## Структура раздела

```
leadership/
├── 00-leadership-overview.md        ← ТЫ ЗДЕСЬ
├── _meta/
│   ├── template-leadership.md       Шаблон для материалов
│   └── learning-path.md             Рекомендуемый путь изучения
├── _resources/
│   └── awesome-lists-index.md       Полный индекс ресурсов (400+ ссылок)
│
├── 01-roles/                        Роли в технологическом лидерстве
│   ├── cto-vs-vpe.md               CTO vs VP Engineering
│   ├── tech-lead-role.md           Tech Lead: обязанности и навыки
│   ├── engineering-manager.md      Engineering Manager
│   ├── staff-roles.md              Staff/Principal Engineer (IC track)
│   ├── ic-vs-management.md         IC Track vs Management Track
│   └── first-90-days.md            Первые 90 дней в роли
│
├── 02-engineering-management/       Основы Engineering Management
│   ├── em-fundamentals.md          Фундамент EM
│   ├── transition-to-management.md От IC к менеджеру
│   ├── one-on-one-meetings.md      1-on-1: структура и вопросы
│   ├── performance-management.md   Performance reviews
│   ├── delegation.md               Делегирование
│   └── manager-readme.md           Manager README
│
├── 03-hiring-recruiting/            Найм и рекрутинг
│   ├── hiring-engineers.md         Как нанимать инженеров
│   ├── interview-process-design.md Дизайн процесса интервью
│   ├── sourcing-candidates.md      Где искать кандидатов
│   ├── making-offers.md            Офферы и переговоры
│   └── leadership-interviews.md    Интервью на EM/Director/CTO
│
├── 04-team-building/                Построение команд
│   ├── building-engineering-team.md Строительство команды
│   ├── team-culture.md             Культура команды
│   ├── team-dynamics.md            Динамика команды
│   ├── onboarding.md               Онбординг инженеров
│   ├── motivation.md               Мотивация команды
│   └── company-handbooks.md        Справочники компаний
│
├── 05-tech-strategy/                Техническая стратегия
│   ├── tech-debt-management.md     Управление техдолгом
│   ├── architecture-decisions.md   Архитектурные решения (ADR)
│   ├── engineering-practices.md    Инженерные практики
│   ├── development-process.md      Процессы разработки
│   └── technical-vision.md         Техническое видение
│
├── 06-organizational-design/        Организационный дизайн
│   ├── scaling-engineering-org.md  Масштабирование организации
│   ├── team-structures.md          Структуры команд
│   ├── engineering-metrics.md      Метрики инженерии
│   ├── okrs-kpis.md                OKRs и KPIs
│   └── agile-practices.md          Agile и методологии
│
├── 07-executive-skills/             Навыки руководителя
│   ├── strategic-thinking.md       Стратегическое мышление
│   ├── stakeholder-management.md   Управление stakeholders
│   ├── executive-communication.md  Коммуникация с руководством
│   ├── budget-planning.md          Планирование бюджета
│   └── crisis-management.md        Кризисный менеджмент
│
└── 08-startup-leadership/           Лидерство в стартапах
    ├── startup-cto.md              CTO в стартапе
    ├── founding-engineer.md        Founding Engineer
    ├── technical-due-diligence.md  Technical Due Diligence
    └── scaling-from-zero.md        От 0 до 100 инженеров
```

---

## 01. Roles — Роли в техническом лидерстве

> Понимание различий между ролями критично для карьерных решений.

| Материал | Статус | Описание |
|----------|--------|----------|
| [[cto-vs-vpe]] | 🟢 | CTO vs VP Engineering: ключевые различия |
| [[tech-lead-role]] | 🟢 | Tech Lead: scope, навыки, expectations |
| [[engineering-manager]] | 🟢 | Engineering Manager: people-focused leadership |
| [[staff-roles]] | 🟢 | Staff/Principal: IC track (связь с career/) |
| [[ic-vs-management]] | 🟢 | Выбор между IC и Management track |
| [[first-90-days]] | 🟢 | Первые 90 дней в новой роли |

**Зачем:** Без понимания ролей легко принять неверное карьерное решение.

---

## 02. Engineering Management — Основы управления

> 70% времени EM — работа с людьми. Это отдельная профессия, не "побочка".

| Материал | Статус | Описание |
|----------|--------|----------|
| [[em-fundamentals]] | 🟢 | Фундамент Engineering Management |
| [[transition-to-management]] | 🟢 | Переход от IC к менеджеру |
| [[one-on-one-meetings]] | 🟢 | 1-on-1: 21 причина проводить, 130+ вопросов |
| [[performance-management]] | 🟢 | Performance reviews без pain |
| [[delegation]] | 🟢 | Делегирование: матрица и антипаттерны |
| [[manager-readme]] | 🟢 | Manager README: как работать со мной |

**Зачем:** EM — одна из самых сложных ролей. 60% новых менеджеров терпят неудачу в первые 2 года.

---

## 03. Hiring & Recruiting — Найм

> Hiring — самое важное, что делает лидер. A-players attract A-players.

| Материал | Статус | Описание |
|----------|--------|----------|
| [[hiring-engineers]] | 🟢 | Полный гайд по найму инженеров |
| [[interview-process-design]] | 🟢 | Дизайн процесса: от sourcing до offer |
| [[sourcing-candidates]] | 🟢 | Где искать кандидатов |
| [[making-offers]] | 🟢 | Офферы, compensation, negotiation |
| [[leadership-interviews]] | 🟢 | Интервью на EM/Director/VP/CTO |

**Зачем:** Плохой найм стоит 1.5-2x годовой зарплаты. Хороший найм — multiplier.

---

## 04. Team Building — Построение команд

> Команда > сумма её членов. Google's Project Aristotle доказал: psychological safety важнее skills.

| Материал | Статус | Описание |
|----------|--------|----------|
| [[building-engineering-team]] | 🟢 | Как строить команду с нуля |
| [[team-culture]] | 🟢 | Культура: Netflix, Valve, GitLab |
| [[team-dynamics]] | 🟢 | Динамика: Tuckman, psychological safety |
| [[onboarding]] | 🟢 | Онбординг: первые 30-60-90 дней |
| [[motivation]] | 🟢 | Мотивация: autonomy, mastery, purpose |
| [[company-handbooks]] | 🟢 | Справочники: Valve, Basecamp, GitLab |

**Зачем:** High-performing teams outperform average teams 5x (Google Research).

---

## 05. Tech Strategy — Техническая стратегия

> CTO/VP Eng должен уметь переводить бизнес-цели в технические решения.

| Материал | Статус | Описание |
|----------|--------|----------|
| [[tech-debt-management]] | 🟢 | Техдолг: метафоры, измерение, приоритизация |
| [[architecture-decisions]] | 🟢 | ADR: документирование решений |
| [[engineering-practices]] | 🟢 | Практики: code review, testing, CI/CD |
| [[development-process]] | 🟢 | Процессы: Git flow, trunk-based |
| [[technical-vision]] | 🟢 | Техническое видение и roadmap |

**Зачем:** Технический долг съедает 25-40% velocity команд.

---

## 06. Organizational Design — Организационный дизайн

> Conway's Law: архитектура системы отражает структуру команды.

| Материал | Статус | Описание |
|----------|--------|----------|
| [[scaling-engineering-org]] | 🟢 | От 10 до 1000 инженеров |
| [[team-structures]] | 🟢 | Структуры: Spotify model, Team Topologies |
| [[engineering-metrics]] | 🟢 | Метрики: DORA, velocity, quality |
| [[okrs-kpis]] | 🟢 | OKRs и KPIs для engineering |
| [[agile-practices]] | 🟢 | Agile: что работает, что нет |

**Зачем:** Неправильная структура = bottlenecks, конфликты, медленный delivery.

---

## 07. Executive Skills — Навыки руководителя

> Senior leadership — другая игра. Stakeholder management важнее coding skills.

| Материал | Статус | Описание |
|----------|--------|----------|
| [[strategic-thinking]] | 🟢 | Стратегическое мышление |
| [[stakeholder-management]] | 🟢 | Управление stakeholders |
| [[executive-communication]] | 🟢 | Коммуникация с C-level |
| [[budget-planning]] | 🟢 | Бюджетирование engineering |
| [[crisis-management]] | 🟢 | Кризисы: outages, layoffs |

**Зачем:** VP+ тратят 80% времени на people и politics, не на tech.

---

## 08. Startup Leadership — Лидерство в стартапах

> Startup CTO — совсем другая роль. Сначала hands-on, потом hiring, потом strategy.

| Материал | Статус | Описание |
|----------|--------|----------|
| [[startup-cto]] | 🟢 | CTO в стартапе: эволюция роли |
| [[founding-engineer]] | 🟢 | Founding Engineer: первые 10 |
| [[technical-due-diligence]] | 🟢 | Due Diligence при инвестициях |
| [[scaling-from-zero]] | 🟢 | От 0 до 100 инженеров |

**Зачем:** 90% стартапов fail. Часто причина — плохое техническое лидерство.

---

## Learning Path

```
LEVEL 1: Foundation (первый месяц)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
► ic-vs-management.md        Понять, твой ли это путь
► em-fundamentals.md         Базовые принципы
► one-on-one-meetings.md     Главный инструмент EM

LEVEL 2: Core Skills (2-3 месяца)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
► transition-to-management.md  Как перейти правильно
► hiring-engineers.md          Самый важный навык
► performance-management.md    Feedback и growth
► team-dynamics.md             Как работают команды

LEVEL 3: Advanced (3-6 месяцев)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
► cto-vs-vpe.md               Понять senior roles
► scaling-engineering-org.md  Рост организации
► tech-debt-management.md     Tech strategy
► engineering-metrics.md      Измерение успеха

LEVEL 4: Executive (ongoing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
► strategic-thinking.md       C-level thinking
► stakeholder-management.md   Politics и influence
► crisis-management.md        Когда всё идёт не так
```

---

## Связи с другими разделами

| Раздел | Связь |
|--------|-------|
| [[communication/]] | Feedback, difficult conversations, presentations |
| [[career/]] | Staff+ engineering, salary negotiation, interviews |
| [[thinking/]] | Mental models, decision-making, cognitive biases |

---

## Ключевые метрики и статистика

```
СТАТИСТИКА TECH LEADERSHIP:

• 60% новых менеджеров fail в первые 2 года
• 70% времени EM = работа с людьми
• 1.5-2x годовой зарплаты = стоимость плохого найма
• 25-40% velocity теряется на техдолг
• 5x — разница между high и average performing teams
• 80% времени VP+ = people и politics, не tech
• 90% стартапов fail (часто из-за tech leadership)
```

---

## Обязательные книги

| Книга | Автор | Для кого |
|-------|-------|----------|
| The Manager's Path | Camille Fournier | Все EM |
| High Output Management | Andy Grove | Все EM |
| An Elegant Puzzle | Will Larson | Senior EM |
| Staff Engineer | Will Larson | Staff+ IC |
| The Five Dysfunctions of a Team | Patrick Lencioni | Team leads |
| Radical Candor | Kim Scott | Все EM |
| Turn the Ship Around! | L. David Marquet | Senior leaders |

---

## Подкасты и ресурсы

| Ресурс | Тип | Фокус |
|--------|-----|-------|
| [Pragmatic Engineer](https://newsletter.pragmaticengineer.com/) | Newsletter | Big Tech insights |
| [LeadDev](https://leaddev.com/) | Conference/Articles | Engineering leadership |
| [Rands Leadership Slack](https://randsinrepose.com/welcome-to-rands-leadership-slack/) | Community | EM community |
| [StaffEng](https://staffeng.com/) | Book/Site | Staff+ IC |
| Manager Tools | Podcast | Management basics |
| The Tech Exec Podcast | Podcast | CTO/VPE |

---

## Статусы материалов

| Статус | Значение | Количество |
|--------|----------|------------|
| 🟢 | Готов и проверен | 30 |
| 🟡 | В разработке | 0 |
| 🔴 | Планируется | 0 |

**Прогресс: 30/30 материалов (100%) ✅**

---

---

## Проверь себя

> [!question]- Почему understanding различий между ролями (CTO, VP Eng, EM, Tech Lead) критично для карьерного развития?
> Без понимания различий легко принять неверное решение: например, пойти в management "ради роста", не осознавая что это career change, а не promotion. Каждая роль требует разных навыков и даёт разный тип impact, поэтому осознанный выбор опирается на self-assessment.

> [!question]- Представь, что команда из 60 инженеров управляется одним CTO-сооснователем. Какие проблемы возникнут и какое решение предложишь?
> При 60 инженерах один лидер не может совмещать стратегию и operations. Нужно разделить роли: CTO фокусируется на технологической стратегии и architecture, а VP Engineering берёт hiring, delivery и people management. Это критическая точка масштабирования.

> [!question]- Какой learning path ты бы рекомендовал новому Engineering Manager и почему именно в таком порядке?
> Сначала ic-vs-management (осознанный выбор трека), потом em-fundamentals (базовые принципы), затем one-on-one-meetings (главный инструмент). Порядок важен: без осознанного выбора новый EM борется с identity shift, без фундамента -- действует хаотично, а 1-on-1 -- это первый практический навык.

---

## Ключевые карточки

Какой % новых менеджеров терпит неудачу в первые 2 года?
?
60% новых менеджеров fail в первые 2 года (DDI Research). Основные причины: отсутствие подготовки к career change, продолжение coding вместо people work, и непонимание новых метрик успеха.

Чем CTO отличается от VP Engineering?
?
CTO отвечает за "что строить" (технологическая стратегия, R&D, инновации, внешнее представительство). VP Engineering отвечает за "как строить" (delivery, процессы, люди, org design). Это peer roles с разным фокусом, а не иерархия.

Что такое psychological safety и почему это фактор #1?
?
Google Project Aristotle определил psychological safety как возможность рисковать без страха наказания. Это фактор #1 эффективных команд, потому что без него люди скрывают ошибки, не предлагают идеи и не дают honest feedback.

Какова стоимость плохого найма?
?
1.5-2x годовой зарплаты сотрудника. Включает прямые затраты (рекрутинг, onboarding), косвенные (потерянное время, снижение морали команды) и opportunity cost (не наняли хорошего кандидата вместо плохого).

Сколько velocity теряется на техдолг?
?
25-40% velocity команд теряется на техдолг. Это делает управление техдолгом критическим навыком для технических лидеров, которые должны балансировать между feature delivery и tech debt reduction.

Что такое Engineer/Manager Pendulum?
?
Концепция Charity Majors о переключении между IC и management треками каждые 3-5 лет. Это не "шаг назад", а накопление разных perspectives, что делает человека более эффективным в обеих ролях.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ic-vs-management]] | Определить свой карьерный трек |
| Углубиться | [[em-fundamentals]] | Фундаментальные принципы Engineering Management |
| Смежная тема | [[communication-styles]] | Навыки коммуникации критичны для любого лидера |
| Обзор | [[leadership-overview]] | Вернуться к карте раздела |

---

*Последнее обновление: 2026-02-13*
*Полный индекс ресурсов: [[_resources/awesome-lists-index]]*

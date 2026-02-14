---
title: "Инженерные практики"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, tech-lead, director]
teaches:
  - code review
  - testing strategy
  - CI/CD practices
sources: [google-engineering, accelerate, dora]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[em-fundamentals]]"
  - "[[development-process]]"
prerequisites:
  - "[[em-fundamentals]]"
reading_time: 7
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Инженерные практики

> **TL;DR:** Практики определяют качество и скорость. DORA metrics: deployment frequency, lead time, MTTR, change failure rate. Code review — не gatekeeping, а knowledge sharing. Testing pyramid: много unit, меньше integration, мало e2e. CI/CD: deploy часто, маленькими частями.

---

## DORA Metrics

```
4 KEY METRICS (Accelerate book):

1. DEPLOYMENT FREQUENCY
   How often deploy to production
   Elite: multiple times/day
   High: weekly-monthly
   Low: monthly-yearly

2. LEAD TIME FOR CHANGES
   Commit → Production
   Elite: <1 hour
   High: 1 day - 1 week
   Low: 1 week - 6 months

3. MEAN TIME TO RESTORE (MTTR)
   Incident → Restored
   Elite: <1 hour
   High: <1 day
   Low: 1 day - 1 week

4. CHANGE FAILURE RATE
   % deploys causing incidents
   Elite: 0-15%
   High: 16-30%
   Low: 46-60%

CORRELATION:
High performers on ALL 4 metrics.
Скорость и стабильность не противоречат.
```

## Code Review

```
PURPOSE:
• Knowledge sharing (primary)
• Bug catching (secondary)
• Code quality (secondary)

BEST PRACTICES:
□ Review within 24 hours
□ Small PRs (<400 lines)
□ Constructive feedback
□ Focus on important, not nitpicks
□ Approve when "good enough"

ANTI-PATTERNS:
✗ Gatekeeping mentality
✗ Rewriting in your style
✗ Blocking for minor issues
✗ PRs sitting for days
✗ Only senior reviews

FRAMEWORK FOR FEEDBACK:
"Nit:" — minor, optional
"Suggestion:" — consider this
"Important:" — should change
"Blocking:" — must change
```

## Testing Strategy

```
TESTING PYRAMID:

         ╱╲        E2E (few)
        ╱  ╲       Slow, flaky, expensive
       ╱────╲
      ╱      ╲     Integration (some)
     ╱        ╲    Test components together
    ╱──────────╲
   ╱            ╲  Unit (many)
  ╱              ╲ Fast, isolated, cheap
 ╱────────────────╲

DISTRIBUTION:
• 70% Unit tests
• 20% Integration tests
• 10% E2E tests

COVERAGE TARGETS:
• New code: 80%+
• Critical paths: 90%+
• Overall: 70%+ (not obsessive)

WHAT TO TEST:
✓ Business logic
✓ Edge cases
✓ Error handling
✓ Integration points

WHAT NOT TO OVER-TEST:
✗ Trivial getters/setters
✗ Framework code
✗ UI styling
```

## CI/CD Practices

```
CONTINUOUS INTEGRATION:
□ Merge to main frequently (daily+)
□ Automated tests on every commit
□ Build should be fast (<10 min)
□ Fix broken builds immediately
□ No long-lived branches

CONTINUOUS DELIVERY:
□ Always deployable main branch
□ Automated deployment pipeline
□ Feature flags for partial releases
□ Easy rollback
□ Staging environment

DEPLOYMENT STRATEGIES:
• Blue-green: instant switch
• Canary: gradual rollout %
• Feature flags: user-level control

MONITORING:
□ Deploy alerts
□ Error rate monitoring
□ Performance monitoring
□ Automated rollback triggers
```

## On-Call Practices

```
ON-CALL EXPECTATIONS:
• Response time: 5-15 minutes
• Runbooks for common issues
• Escalation paths clear
• Blameless culture

ROTATION:
• Weekly rotation typical
• Follow the sun for global
• Compensation for off-hours

POST-INCIDENT:
• Blameless post-mortem
• Document learnings
• Action items tracked
• Share with team
```

---

## Связанные темы

- [[development-process]] — процессы разработки
- [[tech-debt-management]] — управление долгом
- [[engineering-metrics]] — метрики

## Источники

| Источник | Тип |
|----------|-----|
| [Accelerate](https://www.amazon.com/Accelerate-Software-Performing-Technology-Organizations/dp/1942788339) | Book |
| [DORA Research](https://dora.dev/) | Research |
| [Google Engineering Practices](https://google.github.io/eng-practices/) | Guide |

---

## Связь с другими темами

**[[em-fundamentals]]** — Engineering practices — это operationalization фундаментальных принципов EM. Если em-fundamentals говорит о создании условий для эффективной команды, то engineering practices определяет конкретные standards и процессы: DORA metrics как north star, code review для knowledge sharing, testing pyramid для quality. EM отвечает за adoption и evolution этих practices в команде.

**[[development-process]]** — Engineering practices и development process — complementary: practices определяют quality standards (как делаем code review, какая testing strategy), а process определяет workflow (когда deploy, как планируем sprint). Вместе они формируют полную engineering operating model. DORA metrics (deployment frequency, lead time, MTTR, change failure rate) связывают обе области единой measurement framework.

## Источники и дальнейшее чтение

- **Kim et al., "The Phoenix Project" (2016)** — Описывает transformation от broken engineering practices (manual deploys, no testing, siloed knowledge) к DevOps culture через Three Ways. Книга демонстрирует impact engineering practices на business outcomes и показывает, что speed и stability не противоречат друг другу.
- **Camille Fournier, "The Manager's Path" (2017)** — Содержит практические рекомендации по установлению engineering practices в команде, включая как внедрять code review culture, как балансировать tech debt с feature work и как использовать metrics without gaming them.
- **Will Larson, "An Elegant Puzzle" (2019)** — Системный подход к engineering practices: Larson описывает, как practices масштабируются (и ломаются) при росте организации, и предлагает frameworks для их адаптации на каждой стадии роста.


## Проверь себя

> [!question]- DORA metrics: speed и stability не противоречат
> Менеджер утверждает: 'Мы не можем деплоить чаще, потому что это снизит стабильность'. Используя данные DORA из Accelerate book, опровергните этот миф. Какие конкретные practices позволяют одновременно повысить скорость и стабильность?

> [!question]- Code review как knowledge sharing
> В команде code review воспринимается как gatekeeping: один senior блокирует PRs по стилистическим причинам, PRs висят по 3-5 дней. Используя best practices из файла, предложите новую culture of code review с конкретными правилами и feedback framework.

> [!question]- Testing pyramid на практике
> Команда имеет 500 e2e тестов, 50 integration и 20 unit тестов. Suite runs 45 минут. Тесты flaky. Используя testing pyramid, предложите migration plan с конкретными пропорциями и targets.

## Ключевые карточки

Назови 4 DORA metrics и elite benchmarks.
?
1. Deployment Frequency (multiple/day). 2. Lead Time for Changes (<1 hour). 3. MTTR (<1 hour). 4. Change Failure Rate (0-15%). Key insight: high performers excel on ALL 4.

Какое правильное распределение тестов в testing pyramid?
?
70% Unit tests (fast, isolated, cheap), 20% Integration tests (test components together), 10% E2E tests (slow, flaky, expensive).

Назови framework для feedback в code review.
?
'Nit:' — minor, optional. 'Suggestion:' — consider this. 'Important:' — should change. 'Blocking:' — must change.

Каков primary purpose code review?
?
Knowledge sharing (primary), Bug catching (secondary), Code quality (secondary). Review within 24 hours, small PRs (<400 lines), approve when 'good enough'.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[development-process]] | Процессы для practices |
| Углубиться | [[engineering-metrics]] | Метрики для измерения practices |
| Смежная тема | [[ci-cd-pipelines]] | CI/CD pipeline в деталях |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*

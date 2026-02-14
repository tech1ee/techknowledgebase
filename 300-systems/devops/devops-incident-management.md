---
title: "Incident Management: On-call, Runbooks, Post-mortems"
created: 2025-12-22
modified: 2026-02-13
type: concept
status: published
confidence: high
tags:
  - topic/devops
  - sre
  - incidents
  - on-call
  - post-mortem
  - type/concept
  - level/intermediate
related:
  - "[[devops-overview]]"
  - "[[observability]]"
  - "[[security-incident-response]]"
prerequisites:
  - "[[observability]]"
reading_time: 13
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Incident Management: On-call, Runbooks, Post-mortems

> Incidents случаются. Важно как быстро обнаружить, как эффективно решить, и как предотвратить повторение.

---

## TL;DR

- **On-call** — дежурство с чёткой ротацией и эскалацией
- **Runbooks** — документированные процедуры для типичных проблем
- **Incident Response** — structured процесс: detect → respond → resolve → learn
- **Blameless Post-mortems** — фокус на системе, не на людях

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Incident** | Незапланированное прерывание или снижение качества сервиса |
| **Severity** | Уровень критичности (SEV1, SEV2, SEV3) |
| **On-call** | Дежурный инженер, первый responder |
| **Runbook** | Пошаговая инструкция для решения проблемы |
| **MTTR** | Mean Time To Recovery — среднее время восстановления |
| **MTTD** | Mean Time To Detect — среднее время обнаружения |
| **Post-mortem** | Анализ инцидента после его завершения |
| **Incident Commander** | Координатор решения инцидента |

---

## Incident Lifecycle

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      INCIDENT LIFECYCLE                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐     │
│  │ DETECT  │──▶│ RESPOND │──▶│ RESOLVE │──▶│ RECOVER │──▶│  LEARN  │     │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘     │
│       │             │             │             │             │           │
│       ▼             ▼             ▼             ▼             ▼           │
│  • Alerts      • Triage      • Diagnose    • Restore     • Post-         │
│  • Monitoring  • Escalate    • Fix         • Verify      mortem         │
│  • Reports     • Communicate • Mitigate    • Monitor     • Action        │
│                • Incident    • Deploy fix  • Close       items          │
│                  channel                     incident                     │
│                                                                             │
│  ──────────────────────────────────────────────────────────────────────    │
│  TIME        |  MTTD  |    MTTR (Mean Time To Recovery)    |   Review    │
│  ──────────────────────────────────────────────────────────────────────    │
│                                                                             │
│  Goals:                                                                    │
│  • MTTD < 5 min (alerting)                                                │
│  • MTTR < 1 hour (for SEV1)                                               │
│  • Post-mortem within 48 hours                                            │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Severity Levels

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      SEVERITY MATRIX                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SEV1 (Critical)                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Impact: Complete service outage, major data loss                   │   │
│  │  Response: Immediate, all-hands                                     │   │
│  │  Target MTTR: < 1 hour                                              │   │
│  │  Examples:                                                          │   │
│  │  • Production database down                                         │   │
│  │  • Payment processing failed                                        │   │
│  │  • Security breach                                                  │   │
│  │  • Complete site unavailable                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  SEV2 (High)                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Impact: Major feature unavailable, significant degradation         │   │
│  │  Response: Within 30 min, primary on-call + backup                 │   │
│  │  Target MTTR: < 4 hours                                             │   │
│  │  Examples:                                                          │   │
│  │  • Search not working                                               │   │
│  │  • Login issues for subset of users                                │   │
│  │  • API latency > 5x normal                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  SEV3 (Medium)                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Impact: Minor feature issue, workaround available                  │   │
│  │  Response: Next business hours                                      │   │
│  │  Target MTTR: < 24 hours                                            │   │
│  │  Examples:                                                          │   │
│  │  • Non-critical feature broken                                     │   │
│  │  • Elevated error rate (but service functional)                    │   │
│  │  • Internal tool issues                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  SEV4 (Low)                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Impact: Cosmetic, no user impact                                   │   │
│  │  Response: Backlog, normal sprint                                   │   │
│  │  Examples:                                                          │   │
│  │  • UI alignment issue                                               │   │
│  │  • Log verbosity too high                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## On-Call Best Practices

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      ON-CALL STRUCTURE                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ROTATION EXAMPLE                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Week 1    Week 2    Week 3    Week 4    Week 5                    │   │
│  │  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                  │   │
│  │  │Alice│   │ Bob │   │Carol│   │ Dan │   │Alice│  (repeat)        │   │
│  │  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘                  │   │
│  │                                                                      │   │
│  │  Primary on-call: First responder                                  │   │
│  │  Secondary on-call: Backup + escalation                            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ESCALATION PATH                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Alert fires                                                        │   │
│  │       │                                                              │   │
│  │       ▼ (5 min)                                                     │   │
│  │  Page Primary On-call                                               │   │
│  │       │                                                              │   │
│  │       ├── Acknowledged → Investigate                                │   │
│  │       │                                                              │   │
│  │       ▼ (15 min, no ACK)                                           │   │
│  │  Page Secondary On-call                                             │   │
│  │       │                                                              │   │
│  │       ▼ (30 min, SEV1)                                             │   │
│  │  Page Engineering Manager                                           │   │
│  │       │                                                              │   │
│  │       ▼ (1 hour, SEV1)                                             │   │
│  │  Page VP Engineering                                                │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ON-CALL EXPECTATIONS                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  □ Laptop and internet access                                       │   │
│  │  □ Response within 15 minutes                                       │   │
│  │  □ No alcohol impairment                                            │   │
│  │  □ Handoff briefing at rotation change                             │   │
│  │  □ Escalate if unable to resolve in 30 min                         │   │
│  │  □ Document all actions taken                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Runbook Template

```markdown
# Runbook: High Database CPU

## Overview
Database CPU exceeds 80% causing slow queries and potential timeouts.

## Severity
SEV2 (if sustained > 5 min)

## Detection
- Alert: `db_cpu_percent > 80 for 5m`
- Dashboard: Grafana > Database > CPU

## Impact
- Slow API responses (P95 > 2s)
- Potential query timeouts
- User-facing latency

## Quick Diagnosis
```bash
# Check current CPU usage
aws rds describe-db-instances --db-instance-identifier prod-db \
  --query 'DBInstances[0].{CPU:PerformanceInsightsEnabled}'

# Check running queries
psql -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query
         FROM pg_stat_activity
         WHERE state = 'active'
         ORDER BY duration DESC;"

# Check for locks
psql -c "SELECT * FROM pg_locks WHERE NOT granted;"
```

## Resolution Steps

### Step 1: Identify cause
1. Check for long-running queries
2. Check for lock contention
3. Check for unusual traffic spike
4. Check recent deployments

### Step 2: Immediate mitigation
```bash
# Kill long-running query (if safe)
psql -c "SELECT pg_terminate_backend(PID);"

# Enable query timeout
psql -c "SET statement_timeout = '30s';"
```

### Step 3: If traffic spike
```bash
# Scale read replicas (AWS)
aws rds create-db-instance-read-replica \
  --db-instance-identifier prod-db-read-2 \
  --source-db-instance-identifier prod-db

# Enable caching
kubectl scale deployment cache --replicas=5
```

### Step 4: If query performance issue
1. Identify slow query
2. Check EXPLAIN ANALYZE
3. Add missing index or optimize query

## Rollback
If recent deployment caused issue:
```bash
kubectl rollout undo deployment/api
```

## Escalation
- If not resolved in 30 min: Page DBA on-call
- If customer impact > 1 hour: Notify Customer Success

## Post-Incident
- [ ] Update this runbook if steps changed
- [ ] Add missing alert if detection was slow
- [ ] File ticket for long-term fix

## Related
- [Database Performance Dashboard](link)
- [Scaling Guide](link)
- [Query Optimization Guide](link)
```

---

## Incident Response Process

```
┌────────────────────────────────────────────────────────────────────────────┐
│                  INCIDENT RESPONSE WORKFLOW                                 │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ALERT RECEIVED                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Acknowledge alert (stops escalation)                             │   │
│  │  • Quick assessment: What's the impact?                            │   │
│  │  • Determine severity (SEV1/2/3)                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. START INCIDENT                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Create incident channel: #incident-2025-01-15-api-outage        │   │
│  │  • Post initial summary                                             │   │
│  │  • Assign roles:                                                    │   │
│  │    - Incident Commander (IC): Coordinates                          │   │
│  │    - Technical Lead: Investigates                                  │   │
│  │    - Communications: Updates stakeholders                          │   │
│  │  • Start incident timer                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. INVESTIGATE                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Check runbook for this alert                                    │   │
│  │  • Check recent changes (deploys, config)                          │   │
│  │  • Check dashboards and logs                                       │   │
│  │  • Document findings in incident channel                           │   │
│  │  • Time-box investigation (30 min)                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. MITIGATE                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Prioritize restoring service over finding root cause           │   │
│  │  • Options:                                                         │   │
│  │    - Rollback recent deploy                                        │   │
│  │    - Scale up resources                                            │   │
│  │    - Enable fallback/degraded mode                                 │   │
│  │    - Block bad traffic                                             │   │
│  │  • Communicate mitigation to stakeholders                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  5. RESOLVE                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Confirm service restored                                        │   │
│  │  • Monitor for recurrence (30 min)                                 │   │
│  │  • Update status page: Resolved                                    │   │
│  │  • Post final summary to incident channel                          │   │
│  │  • Close incident                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  6. POST-INCIDENT                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Schedule post-mortem (within 48 hours)                          │   │
│  │  • Gather timeline and data                                        │   │
│  │  • Write post-mortem document                                      │   │
│  │  • Review with team                                                 │   │
│  │  • Create action items                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Blameless Post-Mortem

```markdown
# Post-Mortem: API Outage 2025-01-15

## Incident Summary
| Field | Value |
|-------|-------|
| Date | 2025-01-15 |
| Duration | 45 minutes |
| Severity | SEV1 |
| Incident Commander | Alice |
| Author | Bob |

## Executive Summary
On January 15, the API service was unavailable for 45 minutes due to a
misconfigured database connection pool limit. This affected all users
attempting to access the platform.

## Impact
- 45 minutes of complete API unavailability
- ~10,000 failed requests
- ~$15,000 estimated revenue impact
- 150 support tickets

## Timeline (UTC)
| Time | Event |
|------|-------|
| 14:00 | Deploy of connection pool config change |
| 14:15 | First error alerts (ignored as transient) |
| 14:30 | SEV1 declared, incident channel created |
| 14:35 | Root cause identified: pool limit = 5 (should be 50) |
| 14:40 | Config rollback deployed |
| 14:45 | Service restored, monitoring |
| 15:15 | Incident closed |

## Root Cause
A typo in the Terraform configuration reduced the database connection pool
from 50 to 5 connections. Under normal load, connections exhausted quickly
causing all API requests to fail.

```hcl
# The bug:
db_pool_size = 5   # Should have been 50
```

## Contributing Factors
1. Config change was not reviewed by second person
2. Staging environment has lower traffic, didn't catch issue
3. Alert threshold was set too high (10 errors/min vs 5)
4. No automated validation of config values

## What Went Well
- Quick identification of root cause once incident started
- Clear communication in incident channel
- Rollback was fast (5 minutes)

## What Went Wrong
- Alert was ignored for 15 minutes (thought transient)
- No code review for config changes
- Staging didn't reflect production load

## Action Items
| Action | Owner | Priority | Due Date |
|--------|-------|----------|----------|
| Require 2-person review for config changes | Alice | P1 | 2025-01-22 |
| Add validation for pool_size (min=20) | Bob | P1 | 2025-01-22 |
| Lower error alert threshold to 5/min | Carol | P2 | 2025-01-29 |
| Add load testing to staging pipeline | Dan | P2 | 2025-02-05 |
| Document connection pool tuning | Bob | P3 | 2025-02-12 |

## Lessons Learned
- "Small" config changes can have big impact
- Staging should simulate production load for critical tests
- When in doubt, escalate early

---
*This post-mortem is blameless. We focus on systems, not individuals.*
```

---

## Chaos Engineering

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      CHAOS ENGINEERING                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Principle: "Break things on purpose to learn how to build better"        │
│                                                                             │
│  CHAOS EXPERIMENTS                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  1. Network chaos                                                   │   │
│  │     • Latency injection (add 500ms delay)                          │   │
│  │     • Packet loss (drop 10% of packets)                            │   │
│  │     • Network partition (isolate services)                         │   │
│  │                                                                      │   │
│  │  2. Resource chaos                                                  │   │
│  │     • CPU stress (consume 90% CPU)                                 │   │
│  │     • Memory pressure (fill memory)                                │   │
│  │     • Disk fill (exhaust storage)                                  │   │
│  │                                                                      │   │
│  │  3. Application chaos                                               │   │
│  │     • Kill pods/containers                                         │   │
│  │     • Restart services                                             │   │
│  │     • Corrupt responses                                            │   │
│  │                                                                      │   │
│  │  4. Infrastructure chaos                                            │   │
│  │     • Terminate EC2 instances                                      │   │
│  │     • Failover database                                            │   │
│  │     • AZ failure simulation                                        │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  TOOLS                                                                     │
│  • Chaos Monkey (Netflix) - random instance termination                   │
│  • Gremlin - comprehensive chaos platform                                 │
│  • Litmus - Kubernetes-native chaos                                       │
│  • Chaos Mesh - K8s chaos engineering                                     │
│                                                                             │
│  GAME DAYS                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Scheduled chaos experiments with the team                          │   │
│  │                                                                      │   │
│  │  1. Define hypothesis: "System handles DB failover in < 30s"       │   │
│  │  2. Prepare: Monitoring, communication, rollback plan              │   │
│  │  3. Execute: Trigger chaos experiment                               │   │
│  │  4. Observe: Watch metrics, user impact                            │   │
│  │  5. Learn: Document findings, create action items                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Связи

- [[devops-overview]] — DevOps practices
- [[observability]] — мониторинг и алерты
- [[security-incident-response]] — security incidents
- [[architecture-resilience-patterns]] — resilience

---

## Источники

- [Google SRE Book - Incident Management](https://sre.google/sre-book/managing-incidents/)
- [PagerDuty Incident Response Guide](https://response.pagerduty.com/)
- [Atlassian Incident Management](https://www.atlassian.com/incident-management)
- [Gremlin Chaos Engineering](https://www.gremlin.com/)
- "Incident Management for Operations" by Rob Schnepp

---

---

## Проверь себя

> [!question]- Почему "blameless" подход критичен для post-mortem культуры? Что произойдёт без него?
> Если искать виноватых, люди начинают скрывать ошибки, давать меньше информации и избегать рисков. Это создаёт культуру страха, где проблемы замалчиваются до тех пор, пока не станут критическими. Blameless подход фокусируется на системных причинах: "какой процесс позволил ошибке случиться?" вместо "кто виноват?". Человек, допустивший ошибку, часто лучше всех понимает как починить систему, чтобы это не повторилось.

> [!question]- Во время SEV1 инцидента разработчик хочет найти root cause перед восстановлением. Правильно ли это?
> Нет. Приоритет при инциденте: сначала MITIGATION (восстановить сервис), потом root cause. Пользователи не ждут, пока дебажишь. Rollback, scale up, failover -- любое действие для восстановления. Root cause analysis требует времени и ясной головы -- это задача для post-mortem после инцидента. Исключение: security breach, где нужно понять что закрывать.

> [!question]- Сравните game day и реальный инцидент. Зачем проводить chaos engineering если можно просто ждать реальных проблем?
> Game day -- контролируемый эксперимент: hypothesis, подготовка, мониторинг, plan B. Реальный инцидент -- неконтролируемый хаос в 3 AM. Game day позволяет: обнаружить слабые места до того, как они станут проблемой, проверить runbooks, натренировать команду на stress, убедиться что failover работает. Цена обнаружения проблемы на game day -- 0, цена обнаружения в production -- часы downtime и потеря выручки.

> [!question]- On-call rotation показывает > 5 page'ей за смену. Какие это симптомы и что делать?
> Это alert fatigue -- дежурный начинает игнорировать алерты, включая критические. Причины: слишком чувствительные пороги, flaky-алерты, отсутствие автоматического remediation для известных проблем. Решения: пересмотреть пороги алертов, удалить неactionable алерты, автоматизировать типовые remediation (auto-scale, auto-restart), объединить связанные алерты, добавить подавление дубликатов.

---

## Ключевые карточки

Что такое MTTD и MTTR?
?
MTTD (Mean Time To Detect) -- среднее время обнаружения инцидента. MTTR (Mean Time To Recovery) -- среднее время восстановления. Цели: MTTD < 5 мин (хороший alerting), MTTR < 1 час для SEV1.

Какие уровни severity используются в incident management?
?
SEV1 (Critical): полный outage, все руки, MTTR < 1ч. SEV2 (High): крупная фича недоступна, 30 мин response, MTTR < 4ч. SEV3 (Medium): minor issue с workaround, next business hours. SEV4 (Low): cosmetic, backlog.

Какие роли нужны при SEV1 инциденте?
?
Incident Commander (IC) -- координирует, принимает решения. Technical Lead -- расследует и чинит. Communications -- обновляет stakeholders и status page. IC не дебажит сам, а координирует работу других.

Что должен содержать хороший runbook?
?
Overview, Severity, Detection (алерты/симптомы), Impact, Quick Diagnosis (конкретные команды), Resolution Steps (пошагово), Rollback, Escalation. Критерий качества: можно выполнить в 3 AM полусонным инженером.

Что такое Chaos Engineering?
?
Практика намеренного внесения сбоев для проверки устойчивости системы. Эксперименты: latency injection, kill pods, network partition, disk fill. Инструменты: Chaos Monkey (Netflix), Litmus, Chaos Mesh. Проводится на game days.

Какова структура blameless post-mortem?
?
Executive Summary, Impact (время, пользователи, revenue), Timeline (UTC), Root Cause, Contributing Factors, What Went Well, What Went Wrong, Action Items (owner + deadline + priority), Lessons Learned. Фокус на системе, не людях.

Как правильно структурировать on-call rotation?
?
1 неделя на смене, handoff briefing при смене, primary + secondary on-call, эскалация через 15 мин без ACK. Здоровый on-call: < 2 pages/shift, компенсация, day off после тяжёлого дежурства. Red flag: > 5 pages/shift.

Что такое Escalation Path?
?
Цепочка эскалации при инциденте: Alert -> Primary On-call (5 мин) -> Secondary On-call (15 мин, no ACK) -> Engineering Manager (30 мин, SEV1) -> VP Engineering (1 час, SEV1). Каждый уровень подключается если предыдущий не справился.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[observability]] | Мониторинг и алерты -- основа для быстрого обнаружения инцидентов (MTTD) |
| Углубиться | [[security-incident-response]] | Security-специфичные инциденты: breach response, forensics |
| Смежная тема | [[architecture-resilience-patterns]] | Паттерны устойчивости: circuit breaker, bulkhead, retry -- предотвращают инциденты |
| Обзор | [[devops-overview]] | Вернуться к карте раздела DevOps |

*Проверено: 2025-12-22*

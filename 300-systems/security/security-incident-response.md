---
title: "Incident Response: detection, containment, recovery"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/security
  - incident-response
  - forensics
  - detection
  - type/concept
  - level/intermediate
related:
  - "[[security-overview]]"
  - "[[devops-incident-management]]"
  - "[[observability]]"
prerequisites:
  - "[[security-fundamentals]]"
  - "[[threat-modeling]]"
reading_time: 10
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Incident Response: detection, containment, recovery

> Security incident случится. Вопрос — когда и как быстро ты отреагируешь. Подготовка и playbooks критичны.

---

## TL;DR

- **Preparation** — до инцидента: playbooks, tools, team
- **Detection** — обнаружить как можно быстрее
- **Containment** — остановить распространение
- **Eradication** — убрать угрозу полностью
- **Recovery** — восстановить нормальную работу
- **Lessons Learned** — post-mortem, улучшения

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Incident** | Нарушение security policy или угроза |
| **Breach** | Подтверждённый unauthorized access |
| **IOC** | Indicator of Compromise — признак атаки |
| **TTD** | Time to Detect — время до обнаружения |
| **TTR** | Time to Respond — время до реагирования |
| **SIEM** | Security Information and Event Management |
| **Forensics** | Сбор и анализ evidence |
| **Playbook** | Документированная процедура реагирования |
| **Severity** | Критичность инцидента (P1-P4) |

---

## Incident Response Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│              INCIDENT RESPONSE LIFECYCLE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                              │
│  │ PREPARATION  │◀─────────────────────────────────────────┐   │
│  │              │                                          │   │
│  │ • Playbooks  │                                          │   │
│  │ • Tools      │                                          │   │
│  │ • Training   │                                          │   │
│  │ • Team       │                                          │   │
│  └──────┬───────┘                                          │   │
│         │                                                   │   │
│         ▼                                                   │   │
│  ┌──────────────┐                                          │   │
│  │  DETECTION   │                                          │   │
│  │              │                                          │   │
│  │ • Alerts     │                                          │   │
│  │ • Logs       │                                          │   │
│  │ • Reports    │                                          │   │
│  └──────┬───────┘                                          │   │
│         │                                                   │   │
│         ▼                                                   │   │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐  │   │
│  │ CONTAINMENT  │────▶│ ERADICATION  │────▶│  RECOVERY  │  │   │
│  │              │     │              │     │            │  │   │
│  │ • Isolate    │     │ • Remove     │     │ • Restore  │  │   │
│  │ • Block      │     │ • Patch      │     │ • Monitor  │  │   │
│  │ • Preserve   │     │ • Clean      │     │ • Validate │  │   │
│  └──────────────┘     └──────────────┘     └─────┬──────┘  │   │
│                                                   │         │   │
│                                                   ▼         │   │
│                                          ┌──────────────┐   │   │
│                                          │   LESSONS    │   │   │
│                                          │   LEARNED    │───┘   │
│                                          │              │       │
│                                          │ • Post-mortem│       │
│                                          │ • Improve    │       │
│                                          └──────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Preparation (до инцидента)

### Incident Response Team

| Роль | Ответственность |
|------|-----------------|
| **Incident Commander** | Координация, решения |
| **Security Analyst** | Техническое расследование |
| **DevOps/SRE** | Доступ к системам, восстановление |
| **Communications** | Внешние/внутренние коммуникации |
| **Legal** | Compliance, уведомления |
| **Management** | Бизнес-решения, эскалация |

### Playbook Template

```markdown
# Playbook: [Incident Type]

## Severity Classification
- P1: Critical — Production down, data breach
- P2: High — Significant impact, potential breach
- P3: Medium — Limited impact
- P4: Low — Minor issue

## Detection
- Какие алерты/индикаторы?
- Источники данных?
- False positive checks?

## Initial Response
1. [ ] Assess severity
2. [ ] Notify incident commander
3. [ ] Start incident channel (#incident-YYYY-MM-DD)
4. [ ] Begin timeline documentation

## Containment
- [ ] Immediate actions (block IP, disable account)
- [ ] Preserve evidence (logs, snapshots)
- [ ] Limit blast radius

## Investigation
- [ ] Collect logs
- [ ] Analyze attack vector
- [ ] Identify affected systems
- [ ] Determine data impact

## Eradication
- [ ] Remove malware/backdoors
- [ ] Patch vulnerabilities
- [ ] Reset compromised credentials

## Recovery
- [ ] Restore from clean backup
- [ ] Gradual service restoration
- [ ] Enhanced monitoring

## Communication
- Internal: [template]
- External: [template]
- Regulatory: [requirements]

## Post-Incident
- [ ] Timeline
- [ ] Root cause
- [ ] Improvements
- [ ] Update playbook
```

---

## 2. Detection

### Indicators of Compromise (IOCs)

```
┌─────────────────────────────────────────────────────────────────┐
│                    INDICATORS OF COMPROMISE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NETWORK                                                        │
│  • Unusual outbound traffic (data exfiltration)               │
│  • Connections to known malicious IPs                          │
│  • DNS queries to suspicious domains                           │
│  • Unexpected ports open                                       │
│                                                                 │
│  HOST                                                           │
│  • New admin accounts                                          │
│  • Modified system files                                       │
│  • Unexpected processes                                        │
│  • Failed login attempts                                       │
│  • Privilege escalation                                        │
│                                                                 │
│  APPLICATION                                                    │
│  • SQL injection attempts                                      │
│  • Brute force attacks                                        │
│  • API abuse patterns                                         │
│  • Unauthorized data access                                   │
│                                                                 │
│  USER BEHAVIOR                                                  │
│  • Login from unusual location                                │
│  • After-hours access                                         │
│  • Bulk data download                                         │
│  • Impossible travel (login from 2 countries in 1 hour)       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Detection Tools

```yaml
# CloudWatch Alarm (AWS)
Resources:
  RootLoginAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: RootAccountLogin
      MetricName: RootAccountUsage
      Namespace: CloudTrail
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      AlarmActions:
        - !Ref SecurityAlertTopic

  FailedLoginAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighFailedLogins
      MetricName: FailedLoginAttempts
      Threshold: 10
      Period: 300
```

---

## 3. Containment

### Immediate Actions

```bash
# Блокировка IP (AWS WAF)
aws wafv2 update-ip-set \
  --name blocked-ips \
  --scope REGIONAL \
  --addresses "1.2.3.4/32"

# Disable compromised user (AWS)
aws iam update-login-profile \
  --user-name compromised-user \
  --no-password-reset-required
aws iam delete-access-key \
  --user-name compromised-user \
  --access-key-id AKIA...

# Isolate EC2 instance (remove from security group)
aws ec2 modify-instance-attribute \
  --instance-id i-1234567890 \
  --groups sg-isolated-for-forensics

# Snapshot for forensics (BEFORE changes)
aws ec2 create-snapshot \
  --volume-id vol-1234567890 \
  --description "Forensic snapshot - incident 2025-01-15"
```

### Evidence Preservation

```bash
# Log collection
aws logs filter-log-events \
  --log-group-name /aws/lambda/myapp \
  --start-time 1705000000000 \
  --end-time 1705100000000 \
  > incident-logs.json

# CloudTrail events
aws cloudtrail lookup-events \
  --start-time 2025-01-15T00:00:00Z \
  --end-time 2025-01-15T23:59:59Z \
  --lookup-attributes AttributeKey=EventSource,AttributeValue=iam.amazonaws.com \
  > cloudtrail-events.json

# Memory dump (EC2)
# SSH to instance, DON'T reboot (destroys memory)
sudo dd if=/dev/mem of=/evidence/memory.dump bs=1M
```

---

## 4. Communication

### Internal Communication

```markdown
# Incident Update #1

**Time:** 2025-01-15 14:30 UTC
**Severity:** P1 - Critical
**Status:** Containment in progress

## Summary
Unauthorized access detected to production database.

## Impact
- Customer data may be affected
- Service degraded (read-only mode)

## Current Actions
- Database isolated
- Forensic investigation ongoing
- Affected credentials rotated

## Next Update
In 1 hour or on significant change.

## Incident Channel
#incident-2025-01-15
```

### External Communication (если требуется)

```markdown
# Security Incident Notice

We detected unauthorized access to our systems on [DATE].

## What Happened
[Brief description without technical details]

## What Information Was Involved
[Types of data, NOT specific records]

## What We Are Doing
[Actions taken]

## What You Can Do
[Recommended actions for users]

## Contact
[Support information]
```

---

## 5. Post-Incident

### Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]

**Date:** 2025-01-15
**Duration:** 4 hours
**Severity:** P1
**Author:** Security Team

## Executive Summary
Brief description of what happened and impact.

## Timeline
| Time (UTC) | Event |
|------------|-------|
| 14:00 | Alert triggered |
| 14:15 | Incident declared |
| 14:30 | Containment started |
| 16:00 | Root cause identified |
| 18:00 | Recovery complete |

## Root Cause
What was the actual cause?

## Impact
- Data affected: X records
- Downtime: Y hours
- Financial: $Z

## What Went Well
- Fast detection (15 min)
- Effective containment

## What Went Wrong
- Missing monitoring on X
- Slow credential rotation

## Action Items
| Action | Owner | Due Date |
|--------|-------|----------|
| Add monitoring for X | @alice | 2025-01-22 |
| Improve rotation process | @bob | 2025-01-29 |

## Lessons Learned
Key takeaways for the team.
```

---

## Severity Matrix

| Severity | Criteria | Response Time | Examples |
|----------|----------|---------------|----------|
| **P1** | Data breach, production down | 15 min | DB breach, ransomware |
| **P2** | Potential breach, major impact | 1 hour | Suspicious activity, critical vuln |
| **P3** | Limited impact, no breach | 4 hours | Failed attacks, minor vuln |
| **P4** | Minimal impact | 24 hours | Policy violation, recon |

---

## Связи

- [[security-overview]] — карта раздела
- [[devops-incident-management]] — SRE incident management
- [[observability]] — мониторинг и логирование
- [[databases-backup-recovery]] — восстановление данных

---

## Источники

- [NIST Computer Security Incident Handling Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf)
- [SANS Incident Handler's Handbook](https://www.sans.org/white-papers/33901/)
- [AWS Security Incident Response Guide](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/)

---

## Связь с другими темами

[[threat-modeling]] — threat model является входным документом для планирования incident response. Идентифицированные угрозы (через STRIDE, attack trees) определяют, какие playbooks необходимо подготовить заранее, какие индикаторы компрометации мониторить и какие severity levels назначать. После каждого инцидента threat model обновляется на основе lessons learned, создавая цикл непрерывного улучшения. Рекомендуется сначала изучить threat-modeling, затем incident-response.

[[devops-incident-management]] — SRE incident management фокусируется на доступности и производительности, тогда как security incident response — на защите конфиденциальности и целостности. Оба процесса используют схожие структуры (incident commander, communication channels, post-mortem), и их интеграция критична для эффективного реагирования. Понимание обоих подходов позволяет построить единый процесс обработки инцидентов любого типа.

[[observability]] — системы мониторинга и логирования являются фундаментом фазы Detection в incident response lifecycle. SIEM-системы, метрики, distributed tracing и structured logging обеспечивают данные для обнаружения IOC и проведения forensic analysis. Без качественной observability время обнаружения (TTD) инцидента увеличивается на порядки, а расследование становится невозможным.

[[security-secrets-management]] — компрометация секретов является одним из самых распространённых типов инцидентов. Наличие автоматизированной ротации и centralized secrets management значительно сокращает время containment и recovery. Playbooks для credential compromise должны включать процедуры emergency rotation через Vault или cloud-native secrets managers.

[[databases-backup-recovery]] — фаза Recovery в incident response напрямую зависит от стратегии резервного копирования баз данных. Знание RPO/RTO, типов бэкапов (full, incremental, differential) и процедур восстановления критично для минимизации data loss при инциденте. Forensic analysis также может потребовать анализа бэкапов для определения момента компрометации.

---

## Источники и дальнейшее чтение

- Anderson R. (2020). *Security Engineering: A Guide to Building Dependable Distributed Systems.* 3rd Edition. Wiley. — глава по incident response и forensics в контексте проектирования устойчивых систем, включая организационные аспекты реагирования на инциденты.
- Shostack A. (2014). *Threat Modeling: Designing for Security.* Wiley. — связь между моделированием угроз и планированием реагирования: как результаты threat modeling формируют playbooks и приоритеты мониторинга.
- McGraw G. (2006). *Software Security: Building Security In.* Addison-Wesley. — принципы встроенной безопасности, включая подготовку к инцидентам на этапе проектирования и разработки.

---

## Проверь себя

> [!question]- Почему containment выполняется ДО eradication, а не наоборот?
> Потому что eradication без containment позволяет угрозе распространяться дальше, пока ты устраняешь уже обнаруженные проблемы. Containment фиксирует blast radius: изолирует скомпрометированные системы, блокирует вредоносный трафик и сохраняет evidence. Без изоляции атакующий может создать новые backdoors, переместиться латерально и уничтожить следы, делая eradication неэффективной.

> [!question]- Компания обнаружила утечку API-ключей в публичный репозиторий. Опиши шаги containment и recovery, используя принципы из incident response и secrets management.
> Containment: немедленно отозвать скомпрометированные ключи через secrets manager, заблокировать доступ с их использованием, проверить CloudTrail/логи на unauthorized requests. Recovery: сгенерировать новые ключи, обновить их в Vault/Secrets Manager (не в коде), задеплоить сервисы с новыми credentials, включить enhanced monitoring на API endpoints. Из secrets management: внедрить автоматическую ротацию и pre-commit hooks для предотвращения повторных утечек.

> [!question]- Как различается роль observability на фазе Detection и на фазе Post-Incident?
> На фазе Detection observability обеспечивает обнаружение IOC через алерты, SIEM-корреляцию, anomaly detection в метриках и логах — цель найти инцидент как можно быстрее (снижение TTD). На фазе Post-Incident те же данные используются для forensic analysis: построение timeline атаки, определение root cause, оценка blast radius. Также post-mortem выявляет пробелы в мониторинге, которые добавляются как action items.

> [!question]- Почему post-mortem должен быть blameless, и как это влияет на качество будущего реагирования?
> Blameless post-mortem поощряет честное описание ошибок и системных проблем. Если участники боятся наказания, они скрывают детали, из-за чего root cause остаётся неизвестным, а action items поверхностными. Blameless культура приводит к системным улучшениям — обновлению playbooks, автоматизации containment-шагов, улучшению мониторинга — вместо поиска виноватых, что не устраняет структурные причины инцидентов.

---

## Ключевые карточки

Какие 6 фаз Incident Response Lifecycle?
?
Preparation (playbooks, team, tools) -> Detection (алерты, логи) -> Containment (изоляция, блокировка) -> Eradication (удаление угрозы, патчи) -> Recovery (восстановление сервисов) -> Lessons Learned (post-mortem, улучшения).

Что такое IOC и какие 4 категории существуют?
?
IOC (Indicator of Compromise) — признак атаки. Категории: Network (необычный трафик, malicious IPs), Host (новые аккаунты, изменённые файлы), Application (injection, brute force), User Behavior (unusual login location, impossible travel).

Почему evidence preservation выполняется ДО любых изменений?
?
Forensic analysis требует оригинальные данные. Логи могут перезаписаться, memory содержит volatile данные, для legal/compliance нужны нетронутые доказательства. Всегда создавай snapshots перед изменениями.

Какие роли входят в Incident Response Team?
?
Incident Commander (координация), Security Analyst (расследование), DevOps/SRE (доступ к системам, восстановление), Communications (внешние/внутренние коммуникации), Legal (compliance, уведомления), Management (бизнес-решения, эскалация).

Чем отличаются severity levels P1-P4?
?
P1 Critical — data breach, production down (реагирование 15 мин). P2 High — потенциальный breach (1 час). P3 Medium — ограниченное воздействие (4 часа). P4 Low — минимальное воздействие (24 часа).

Что включает blameless post-mortem?
?
Timeline событий, root cause (причина, не симптомы), impact (масштаб), what went well/wrong (честная оценка), action items с owners и deadlines, lessons learned. Фокус на системных улучшениях, а не на поиске виноватых.

Что такое TTD и TTR и почему они критичны?
?
TTD (Time to Detect) — время от начала инцидента до его обнаружения. TTR (Time to Respond) — время от обнаружения до начала реагирования. Чем меньше оба показателя, тем меньше blast radius и ущерб от инцидента.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Контекст раздела | [[security-overview]] | Карта всех тем безопасности и место incident response в общей картине |
| Предпосылка к планированию | [[threat-modeling]] | Результаты threat model определяют какие playbooks и IOC готовить |
| Управление секретами | [[security-secrets-management]] | Credential compromise — частый тип инцидента, нужна ротация и Vault |
| SRE-инциденты | [[devops-incident-management]] | Общие паттерны incident management для доступности и производительности |
| Мониторинг и логирование | [[observability]] | Фундамент фазы Detection: алерты, SIEM, structured logging |
| Восстановление данных | [[databases-backup-recovery]] | Стратегии бэкапов и RPO/RTO для фазы Recovery |
| Базовые принципы | [[security-fundamentals]] | Основы безопасности, на которых строится incident response |

---

*Проверено: 2025-12-22*

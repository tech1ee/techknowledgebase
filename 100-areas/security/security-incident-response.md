---
title: "Incident Response: detection, containment, recovery"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: verified
confidence: high
tags:
  - security
  - incident-response
  - forensics
  - detection
related:
  - "[[security-overview]]"
  - "[[devops-incident-management]]"
  - "[[observability]]"
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

## Проверь себя

<details>
<summary>1. Какие фазы в Incident Response Lifecycle?</summary>

**Ответ:**
1. **Preparation** — до инцидента (playbooks, team, tools)
2. **Detection** — обнаружение инцидента
3. **Containment** — остановка распространения
4. **Eradication** — удаление угрозы
5. **Recovery** — восстановление нормальной работы
6. **Lessons Learned** — post-mortem, улучшения

</details>

<details>
<summary>2. Почему важно сохранить evidence до изменений?</summary>

**Ответ:**
- Forensic analysis требует оригинальные данные
- Логи могут быть перезаписаны
- Memory содержит volatile данные
- Для legal/compliance нужны доказательства
- Понимание attack vector

Создай snapshots ПЕРЕД любыми изменениями.

</details>

<details>
<summary>3. Что включать в post-mortem?</summary>

**Ответ:**
- **Timeline** — точная последовательность событий
- **Root cause** — настоящая причина, не симптомы
- **Impact** — что затронуто, масштаб
- **What went well/wrong** — честная оценка
- **Action items** — конкретные улучшения с owners и deadlines
- **Lessons learned** — что изменим

Без blame, фокус на системных улучшениях.

</details>

<details>
<summary>4. Какие IOCs искать при расследовании?</summary>

**Ответ:**
- **Network:** Необычный трафик, malicious IPs, suspicious DNS
- **Host:** Новые accounts, modified files, unexpected processes
- **Application:** Injection attempts, brute force, API abuse
- **Behavior:** Unusual login location, after-hours access, impossible travel

Коррелируй несколько IOCs для уверенности.

</details>

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

*Проверено: 2025-12-22*

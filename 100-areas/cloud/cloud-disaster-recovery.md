---
title: "Cloud Disaster Recovery: Multi-AZ, Multi-Region, RTO/RPO"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/cloud
  - disaster-recovery
  - high-availability
  - rto
  - rpo
  - type/concept
  - level/intermediate
related:
  - "[[cloud-overview]]"
  - "[[databases-backup-recovery]]"
  - "[[databases-replication-sharding]]"
---

# Cloud Disaster Recovery: Multi-AZ, Multi-Region, RTO/RPO

> DR — не "если", а "когда". Планируй failure, тестируй recovery. Цена простоя vs цена DR инфраструктуры.

---

## TL;DR

- **Multi-AZ** — защита от сбоя датацентра (auto failover)
- **Multi-Region** — защита от сбоя региона (manual/auto failover)
- **RTO** — сколько времени на восстановление
- **RPO** — сколько данных можно потерять
- **4 стратегии:** Backup/Restore → Pilot Light → Warm Standby → Hot Standby

---

## Терминология

| Термин | Значение |
|--------|----------|
| **RTO** | Recovery Time Objective — целевое время восстановления |
| **RPO** | Recovery Point Objective — допустимая потеря данных |
| **Failover** | Переключение на резервную систему |
| **Failback** | Возврат на primary после восстановления |
| **Multi-AZ** | Репликация между Availability Zones |
| **Multi-Region** | Репликация между регионами |
| **Pilot Light** | Минимальная инфраструктура в DR регионе |
| **Warm Standby** | Уменьшенная копия production в DR |
| **Hot Standby** | Полная копия, active-active |

---

## RTO и RPO

```
┌─────────────────────────────────────────────────────────────────┐
│                    RTO и RPO                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Disaster                                                       │
│     │                                                           │
│  ───┼───────────────────────────────────────────────────────▶  │
│     │                                                     time  │
│     │                                                           │
│  ◀──┼──▶                           ◀────────────────────────▶  │
│    RPO                                      RTO                 │
│  Потеря данных                        Время простоя            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ПРИМЕРЫ                              │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Критичность     │  RTO        │  RPO       │  Стоимость │   │
│  ├─────────────────┼─────────────┼────────────┼────────────┤   │
│  │ E-commerce      │  1 hour     │  15 min    │  $$$$      │   │
│  │ SaaS App        │  4 hours    │  1 hour    │  $$$       │   │
│  │ Internal Tool   │  24 hours   │  4 hours   │  $$        │   │
│  │ Dev Environment │  72 hours   │  24 hours  │  $         │   │
│  │ Bank/Trading    │  Minutes    │  0 (zero)  │  $$$$$     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Меньше RTO/RPO = дороже инфраструктура + операции             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Стратегии DR

```
┌─────────────────────────────────────────────────────────────────┐
│                  DR СТРАТЕГИИ                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BACKUP & RESTORE                                              │
│  ─────────────────                                             │
│  • Бэкапы в другой регион                                     │
│  • При disaster — восстановление с нуля                       │
│  • RTO: часы-дни, RPO: часы                                   │
│  • Стоимость: $ (только storage)                              │
│                                                                 │
│  ┌──────────┐         ┌──────────┐                             │
│  │  Primary │ backup  │    S3    │                             │
│  │  Region  │ ──────▶ │  DR Region│                            │
│  └──────────┘         └──────────┘                             │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│                                                                 │
│  PILOT LIGHT                                                   │
│  ───────────                                                   │
│  • Минимальная инфра в DR (только data tier)                  │
│  • При disaster — scale up compute                            │
│  • RTO: минуты-часы, RPO: минуты                              │
│  • Стоимость: $$ (реплицированная DB)                         │
│                                                                 │
│  ┌──────────┐ sync    ┌──────────┐                             │
│  │ Primary  │ ──────▶ │ DR Region│                             │
│  │   All    │ replica │ DB only  │ ← scale up при disaster    │
│  └──────────┘         └──────────┘                             │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│                                                                 │
│  WARM STANDBY                                                  │
│  ─────────────                                                 │
│  • Уменьшенная копия production                               │
│  • При disaster — scale up                                    │
│  • RTO: минуты, RPO: секунды-минуты                           │
│  • Стоимость: $$$ (running infrastructure)                    │
│                                                                 │
│  ┌──────────┐ sync    ┌──────────┐                             │
│  │ Primary  │ ──────▶ │ DR Region│                             │
│  │ 100%     │ replica │   25%    │ ← scale при disaster       │
│  └──────────┘         └──────────┘                             │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│                                                                 │
│  HOT STANDBY (Active-Active)                                   │
│  ───────────────────────────                                   │
│  • Полная копия, обе принимают трафик                         │
│  • При disaster — просто DNS failover                         │
│  • RTO: секунды, RPO: 0                                       │
│  • Стоимость: $$$$ (2x infrastructure)                        │
│                                                                 │
│  ┌──────────┐ sync    ┌──────────┐                             │
│  │ Primary  │ ◀─────▶ │    DR    │                             │
│  │ Active   │ bi-dir  │  Active  │ ← оба принимают трафик     │
│  └──────────┘         └──────────┘                             │
│         ▲                   ▲                                   │
│         └───── Traffic ─────┘                                   │
│              (Global LB)                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## AWS Multi-AZ

### RDS Multi-AZ

```hcl
resource "aws_db_instance" "main" {
  identifier             = "production-db"
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = "db.r6g.large"
  allocated_storage      = 100

  # Multi-AZ
  multi_az               = true

  # Encryption
  storage_encrypted      = true

  # Automatic backups
  backup_retention_period = 7
  backup_window          = "03:00-04:00"

  # Failover происходит автоматически
  # при: сбое instance, сбое AZ, maintenance
}
```

### ELB + Auto Scaling Multi-AZ

```hcl
# ALB across multiple AZs
resource "aws_lb" "main" {
  name               = "production-alb"
  load_balancer_type = "application"
  subnets            = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
    aws_subnet.public_c.id
  ]
}

# Auto Scaling Group across AZs
resource "aws_autoscaling_group" "main" {
  name                = "production-asg"
  min_size            = 2
  max_size            = 10
  desired_capacity    = 3

  vpc_zone_identifier = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
    aws_subnet.private_c.id
  ]

  # Health checks
  health_check_type         = "ELB"
  health_check_grace_period = 300
}
```

---

## AWS Multi-Region DR

### Pilot Light Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   PILOT LIGHT SETUP                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  us-east-1 (Primary)              us-west-2 (DR)               │
│  ┌─────────────────────┐          ┌─────────────────────┐      │
│  │                     │          │                     │      │
│  │  ┌───┐ ┌───┐ ┌───┐  │          │                     │      │
│  │  │EC2│ │EC2│ │EC2│  │          │      (stopped)      │      │
│  │  └───┘ └───┘ └───┘  │          │                     │      │
│  │         │           │          │                     │      │
│  │    ┌────┴────┐      │  async   │    ┌─────────┐      │      │
│  │    │   RDS   │──────┼──replica─┼───▶│   RDS   │      │      │
│  │    │ Primary │      │          │    │ Replica │      │      │
│  │    └─────────┘      │          │    └─────────┘      │      │
│  │         │           │          │                     │      │
│  │    ┌────┴────┐      │  sync    │    ┌─────────┐      │      │
│  │    │   S3    │──────┼──────────┼───▶│   S3    │      │      │
│  │    │         │      │          │    │ Replica │      │      │
│  │    └─────────┘      │          │    └─────────┘      │      │
│  │                     │          │                     │      │
│  └─────────────────────┘          └─────────────────────┘      │
│                                                                 │
│  При disaster:                                                 │
│  1. Promote RDS replica to primary                             │
│  2. Launch EC2 instances (from AMI)                            │
│  3. Update Route 53 to DR region                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Route 53 Failover

```hcl
# Health check for primary
resource "aws_route53_health_check" "primary" {
  fqdn              = "primary.example.com"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30
}

# Primary record (failover routing)
resource "aws_route53_record" "primary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  failover_routing_policy {
    type = "PRIMARY"
  }

  alias {
    name                   = aws_lb.primary.dns_name
    zone_id                = aws_lb.primary.zone_id
    evaluate_target_health = true
  }

  set_identifier  = "primary"
  health_check_id = aws_route53_health_check.primary.id
}

# Secondary record
resource "aws_route53_record" "secondary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  failover_routing_policy {
    type = "SECONDARY"
  }

  alias {
    name                   = aws_lb.secondary.dns_name
    zone_id                = aws_lb.secondary.zone_id
    evaluate_target_health = true
  }

  set_identifier = "secondary"
}
```

---

## DR Testing

```
┌─────────────────────────────────────────────────────────────────┐
│                    DR TESTING                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚠️  Untested DR plan = No DR plan                            │
│                                                                 │
│  TYPES OF TESTS:                                               │
│                                                                 │
│  1. TABLETOP EXERCISE (документация)                          │
│     • Walk through DR plan                                    │
│     • Identify gaps                                           │
│     • No actual failover                                      │
│     • Frequency: quarterly                                    │
│                                                                 │
│  2. PARTIAL FAILOVER                                          │
│     • Failover non-critical components                        │
│     • Test specific services                                  │
│     • Frequency: monthly                                      │
│                                                                 │
│  3. FULL FAILOVER                                             │
│     • Complete switch to DR                                   │
│     • Production traffic                                      │
│     • Measure actual RTO/RPO                                  │
│     • Frequency: annually                                     │
│                                                                 │
│  4. CHAOS ENGINEERING                                          │
│     • Random failure injection                                │
│     • Continuous validation                                   │
│     • Netflix Chaos Monkey style                              │
│                                                                 │
│  DOCUMENT EVERYTHING:                                          │
│  • Runbooks for each scenario                                 │
│  • Contact escalation                                         │
│  • Communication templates                                    │
│  • Post-mortem process                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Checklist

```
□ RTO/RPO определены для каждого сервиса
□ DR стратегия соответствует RTO/RPO
□ Data replication настроен (sync/async)
□ Бэкапы в другом регионе
□ Route 53 health checks настроены
□ AMIs скопированы в DR регион
□ Secrets/configs доступны в DR
□ Runbooks документированы
□ DR тестирование по расписанию
□ Команда обучена процедурам
□ Communication plan готов
□ Failback процедура документирована
```

---

## Проверь себя

<details>
<summary>1. Чем Multi-AZ отличается от Multi-Region?</summary>

**Ответ:**
- **Multi-AZ:** Репликация внутри региона, между датацентрами. Защита от сбоя AZ. Автоматический failover (RDS, ElastiCache). Latency минимальный.

- **Multi-Region:** Репликация между регионами. Защита от сбоя целого региона. Требует manual/scripted failover. Добавляет latency (50-150ms).

Multi-AZ для HA, Multi-Region для DR.

</details>

<details>
<summary>2. Какую стратегию выбрать для RTO=1 hour, RPO=15 min?</summary>

**Ответ:** **Warm Standby** подходит:
- Уменьшенная инфраструктура в DR регионе
- Database с async replication (15 min lag acceptable)
- При disaster: scale up compute, promote DB
- Можно уложиться в 1 hour

Pilot Light тоже возможен, но RTO может быть на границе.

</details>

<details>
<summary>3. Почему важно тестировать DR?</summary>

**Ответ:** Untested DR = No DR. Причины:
- Runbooks устаревают
- Конфигурация drift
- Новые сервисы не покрыты
- Команда забывает процедуры
- Реальный RTO может отличаться от ожидаемого

Виды тестов: tabletop (quarterly), partial failover (monthly), full failover (annually).

</details>

<details>
<summary>4. Что такое RPO=0 и как его достичь?</summary>

**Ответ:** RPO=0 означает zero data loss — никакие данные не должны быть потеряны.

Как достичь:
- Synchronous replication (все writes подтверждаются на обоих регионах)
- Active-Active setup
- Strong consistency

Trade-offs: добавляет latency (cross-region sync), дорого (2x infrastructure), сложнее в управлении.

</details>

---

## Связи

- [[cloud-overview]] — карта раздела
- [[databases-backup-recovery]] — бэкапы БД
- [[databases-replication-sharding]] — репликация
- [[devops-incident-management]] — incident response

---

## Источники

- [AWS Disaster Recovery](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/)
- [AWS Well-Architected: Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/)
- "Release It!" by Michael Nygard — Stability patterns

---

*Проверено: 2025-12-22*

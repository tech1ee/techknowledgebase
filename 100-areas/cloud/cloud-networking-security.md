---
title: "Cloud Networking & Security: VPC, Security Groups, IAM"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/cloud
  - topic/networking
  - topic/security
  - vpc
  - iam
  - type/concept
  - level/intermediate
related:
  - "[[cloud-overview]]"
  - "[[cloud-aws-core-services]]"
  - "[[security-overview]]"
---

# Cloud Networking & Security: VPC, Security Groups, IAM

> Networking и security — фундамент cloud архитектуры. Неправильная конфигурация = data breach. Zero Trust: verify explicitly, least privilege, assume breach.

---

## TL;DR

- **VPC** — изолированная виртуальная сеть в облаке
- **Subnet** — сегмент VPC (public/private)
- **Security Group** — stateful firewall на instance level
- **NACL** — stateless firewall на subnet level
- **IAM** — кто может делать что (identity + permissions)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **VPC** | Virtual Private Cloud — изолированная сеть |
| **Subnet** | Сегмент VPC с CIDR блоком |
| **CIDR** | Classless Inter-Domain Routing (10.0.0.0/16) |
| **Internet Gateway** | Выход в интернет для public subnets |
| **NAT Gateway** | Выход в интернет для private subnets (только outbound) |
| **Route Table** | Правила маршрутизации трафика |
| **Security Group** | Stateful firewall (rules apply both ways) |
| **NACL** | Network ACL — stateless firewall |
| **Peering** | Соединение двух VPC |
| **Transit Gateway** | Hub для соединения множества VPC |

---

## VPC Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VPC (10.0.0.0/16)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────┐      │
│  │    Availability Zone A  │  │    Availability Zone B  │      │
│  │                         │  │                         │      │
│  │  ┌───────────────────┐  │  │  ┌───────────────────┐  │      │
│  │  │  Public Subnet    │  │  │  │  Public Subnet    │  │      │
│  │  │  10.0.1.0/24      │  │  │  │  10.0.2.0/24      │  │      │
│  │  │                   │  │  │  │                   │  │      │
│  │  │  ┌─────────────┐  │  │  │  ┌─────────────┐  │  │      │
│  │  │  │     ALB     │  │  │  │  │     ALB     │  │  │      │
│  │  │  │   (public)  │  │  │  │  │   (public)  │  │  │      │
│  │  │  └─────────────┘  │  │  │  └─────────────┘  │  │      │
│  │  └───────────────────┘  │  │  └───────────────────┘  │      │
│  │           │              │  │           │              │      │
│  │  ┌───────────────────┐  │  │  ┌───────────────────┐  │      │
│  │  │  Private Subnet   │  │  │  │  Private Subnet   │  │      │
│  │  │  10.0.3.0/24      │  │  │  │  10.0.4.0/24      │  │      │
│  │  │                   │  │  │  │                   │  │      │
│  │  │  ┌─────────────┐  │  │  │  ┌─────────────┐  │  │      │
│  │  │  │   EC2 App   │  │  │  │  │   EC2 App   │  │  │      │
│  │  │  └─────────────┘  │  │  │  └─────────────┘  │  │      │
│  │  └───────────────────┘  │  │  └───────────────────┘  │      │
│  │           │              │  │           │              │      │
│  │  ┌───────────────────┐  │  │  ┌───────────────────┐  │      │
│  │  │  DB Subnet        │  │  │  │  DB Subnet        │  │      │
│  │  │  10.0.5.0/24      │  │  │  │  10.0.6.0/24      │  │      │
│  │  │                   │  │  │  │                   │  │      │
│  │  │  ┌─────────────┐  │  │  │  ┌─────────────┐  │  │      │
│  │  │  │   RDS       │  │  │  │  │ RDS Standby │  │  │      │
│  │  │  │  (primary)  │  │  │  │  │             │  │  │      │
│  │  │  └─────────────┘  │  │  │  └─────────────┘  │  │      │
│  │  └───────────────────┘  │  │  └───────────────────┘  │      │
│  │                         │  │                         │      │
│  └─────────────────────────┘  └─────────────────────────┘      │
│                                                                 │
│  Internet Gateway ◄────────► NAT Gateway (для private subnets) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Terraform пример

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "main-vpc"
  }
}

# Public Subnet
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-a"
  }
}

# Private Subnet
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "private-subnet-a"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id
}
```

---

## Security Groups vs NACLs

```
┌─────────────────────────────────────────────────────────────────┐
│              SECURITY GROUPS vs NACLs                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SECURITY GROUPS                   NACLs                        │
│  ────────────────                  ─────                        │
│  • Instance level                  • Subnet level               │
│  • Stateful                        • Stateless                  │
│  • Allow rules only                • Allow + Deny rules         │
│  • All rules evaluated             • Rules evaluated in order   │
│  • Return traffic auto allowed     • Must allow return traffic  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Subnet (NACL)                                          │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  EC2 Instance (Security Group)                    │  │   │
│  │  │  ┌─────────────────────────────────────────────┐  │  │   │
│  │  │  │  Application                                │  │  │   │
│  │  │  └─────────────────────────────────────────────┘  │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Traffic проходит: NACL → Security Group → Instance            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Security Group примеры

```hcl
# Web server security group
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  # HTTP from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS from anywhere
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH only from office
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.0/24"]  # Office IP range
  }

  # All outbound allowed
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Database security group
resource "aws_security_group" "db" {
  name        = "db-sg"
  description = "Security group for database"
  vpc_id      = aws_vpc.main.id

  # PostgreSQL only from app servers
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]  # Reference to web SG
  }

  # No direct outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

---

## IAM: Identity and Access Management

### Principals и Policies

```
┌─────────────────────────────────────────────────────────────────┐
│                        IAM MODEL                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PRINCIPALS (WHO)                                               │
│  ├── Users (люди)                                              │
│  ├── Groups (коллекции users)                                  │
│  ├── Roles (для сервисов и federation)                        │
│  └── Service Accounts (для applications)                      │
│                                                                 │
│  POLICIES (WHAT)                                               │
│  ├── Identity-based (attached to principal)                   │
│  ├── Resource-based (attached to resource)                    │
│  ├── Permissions boundaries (limits)                          │
│  └── SCPs (organization level)                                │
│                                                                 │
│  EVALUATION:                                                    │
│  Explicit Deny > Explicit Allow > Implicit Deny               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Least Privilege Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSpecificS3Bucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-app-bucket/*"
    },
    {
      "Sid": "AllowListBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-app-bucket"
    },
    {
      "Sid": "DenyPublicAccess",
      "Effect": "Deny",
      "Action": [
        "s3:PutBucketPublicAccessBlock",
        "s3:PutBucketPolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

### Assume Role (Cross-Account)

```json
// Trust policy на Role (кто может assume)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:root"  // другой account
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "unique-external-id"
        }
      }
    }
  ]
}
```

---

## Zero Trust Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZERO TRUST PRINCIPLES                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. VERIFY EXPLICITLY                                          │
│     • Authenticate every request                               │
│     • Don't trust network location                             │
│     • Use MFA, device health, location                         │
│                                                                 │
│  2. LEAST PRIVILEGE ACCESS                                     │
│     • Just-in-time access                                      │
│     • Just-enough access                                       │
│     • Risk-based adaptive policies                             │
│                                                                 │
│  3. ASSUME BREACH                                              │
│     • Minimize blast radius (segmentation)                     │
│     • Verify end-to-end encryption                             │
│     • Use analytics for threat detection                       │
│                                                                 │
│  Traditional:                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Perimeter ──────────────── Trusted Network ─────────── │   │
│  │  Firewall                   (everything inside is OK)   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Zero Trust:                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Every request verified:                                │   │
│  │  User ──► Auth ──► Policy ──► Resource                  │   │
│  │           │         │          │                        │   │
│  │        Identity  Context    Encrypted                   │   │
│  │          MFA     Device                                 │   │
│  │                  Location                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Checklist: Cloud Security

```
┌─────────────────────────────────────────────────────────────────┐
│                  SECURITY CHECKLIST                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IDENTITY                                                       │
│  □ MFA on all users, especially root                           │
│  □ No long-lived access keys in code                           │
│  □ Use roles for services                                      │
│  □ Rotate credentials regularly                                │
│  □ Least privilege policies                                    │
│                                                                 │
│  NETWORK                                                        │
│  □ Private subnets for databases                               │
│  □ Security groups minimal ingress                             │
│  □ No 0.0.0.0/0 to sensitive ports                            │
│  □ VPC Flow Logs enabled                                       │
│  □ TLS everywhere (in transit)                                 │
│                                                                 │
│  DATA                                                           │
│  □ Encryption at rest (EBS, S3, RDS)                          │
│  □ S3 buckets not public                                       │
│  □ Database passwords in Secrets Manager                       │
│  □ Backup encryption enabled                                   │
│                                                                 │
│  DETECTION                                                      │
│  □ CloudTrail enabled (all regions)                           │
│  □ GuardDuty enabled                                          │
│  □ Security Hub for compliance                                │
│  □ Alerts on suspicious activity                              │
│                                                                 │
│  COMPLIANCE                                                     │
│  □ SCPs for organization guardrails                           │
│  □ Config rules for drift detection                           │
│  □ Regular security audits                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

<details>
<summary>1. Чем Security Group отличается от NACL?</summary>

**Ответ:**
- **Security Group:** Instance level, stateful (return traffic auto-allowed), only allow rules
- **NACL:** Subnet level, stateless (need explicit return rules), allow + deny, evaluated in order

Security Groups — primary mechanism, NACLs — additional layer.

</details>

<details>
<summary>2. Зачем нужен NAT Gateway?</summary>

**Ответ:** NAT Gateway позволяет instances в private subnet:
- Выходить в интернет (outbound)
- Но не быть доступными из интернета (no inbound)

Use cases: скачивать updates, обращаться к external APIs, но без прямого exposure.

</details>

<details>
<summary>3. Что такое Zero Trust и его принципы?</summary>

**Ответ:** Zero Trust — security model без implicit trust:

1. **Verify explicitly:** Аутентифицируй каждый запрос
2. **Least privilege:** Минимальные права, just-in-time access
3. **Assume breach:** Сегментация, encryption, detection

Противоположность "trusted network" модели.

</details>

<details>
<summary>4. Как реализовать cross-account доступ в AWS?</summary>

**Ответ:**
1. Создать Role в target account
2. Trust policy разрешает assume из source account
3. Permissions policy определяет что можно делать
4. Source account assume role через STS

```
Source Account → sts:AssumeRole → Target Account Role → Access Resources
```

</details>

---

## Связи

- [[cloud-overview]] — карта раздела
- [[security-overview]] — общая безопасность
- [[infrastructure-as-code]] — Terraform для networking
- [[authentication-authorization]] — AuthN/AuthZ

---

## Источники

- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Zero Trust Architecture (NIST)](https://www.nist.gov/publications/zero-trust-architecture)

---

*Проверено: 2025-12-22*

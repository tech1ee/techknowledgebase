---
title: "Secrets Management: Vault, rotation, environment variables"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/security
  - secrets
  - vault
  - credentials
  - type/concept
  - level/intermediate
related:
  - "[[security-overview]]"
  - "[[cloud-aws-core-services]]"
  - "[[devops-overview]]"
prerequisites:
  - "[[security-cryptography-fundamentals]]"
  - "[[security-fundamentals]]"
reading_time: 9
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Secrets Management: Vault, rotation, environment variables

> Секреты в коде = breach waiting to happen. Используй dedicated secrets management. Ротируй регулярно. Audit всё.

---

## TL;DR

- **Никогда:** Секреты в коде, git, логах
- **Environment vars** — лучше чем в коде, но не идеально
- **Secrets Manager** — AWS/GCP/Azure нативные решения
- **Vault** — enterprise, self-hosted, dynamic secrets
- **Rotation** — автоматическая, регулярная

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Secret** | Пароль, API key, certificate, token |
| **Static Secret** | Не меняется пока не ротируешь вручную |
| **Dynamic Secret** | Генерируется по запросу, с TTL |
| **Rotation** | Периодическая смена секрета |
| **Vault** | HashiCorp Vault — enterprise secrets management |
| **Seal/Unseal** | Vault зашифрован в покое, нужен unseal |
| **Lease** | Время жизни dynamic secret |

---

## Плохие практики

```
┌─────────────────────────────────────────────────────────────────┐
│                    ❌ НЕ ДЕЛАЙ ТАК                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Секреты в коде                                             │
│     db_password = "super_secret_123"  # В git навсегда         │
│                                                                 │
│  2. Секреты в .env в репозитории                              │
│     git add .env  # Oops                                       │
│                                                                 │
│  3. Секреты в Docker image                                     │
│     ENV API_KEY=secret  # docker history покажет              │
│                                                                 │
│  4. Секреты в логах                                            │
│     logger.info(f"Connecting with password: {password}")       │
│                                                                 │
│  5. Shared credentials                                         │
│     # Один API key для всех сервисов                          │
│                                                                 │
│  6. Никогда не ротируемые секреты                             │
│     # "Этот пароль с 2018 года, не трогай"                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Иерархия решений

```
┌─────────────────────────────────────────────────────────────────┐
│              SECRETS MANAGEMENT HIERARCHY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WORST ───────────────────────────────────────────────▶ BEST   │
│                                                                 │
│  Hardcoded → .env file → Env vars → Secrets Manager → Vault   │
│     ❌          ❌          ⚠️            ✅              ✅     │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ ENVIRONMENT VARIABLES                                  │    │
│  │ ✅ Не в коде                                            │    │
│  │ ⚠️ Видны в /proc, ps, docker inspect                   │    │
│  │ ⚠️ Нет audit, rotation, access control                 │    │
│  │ → OK для dev, не для production secrets               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ CLOUD SECRETS MANAGER                                  │    │
│  │ ✅ Encryption at rest                                   │    │
│  │ ✅ IAM integration                                      │    │
│  │ ✅ Audit logging                                        │    │
│  │ ✅ Rotation support                                     │    │
│  │ → AWS Secrets Manager, GCP Secret Manager, Azure KV   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ HASHICORP VAULT                                        │    │
│  │ ✅ Dynamic secrets (on-demand credentials)             │    │
│  │ ✅ Fine-grained policies                               │    │
│  │ ✅ Secret versioning                                   │    │
│  │ ✅ Multi-cloud, self-hosted                           │    │
│  │ → Enterprise, complex setups                          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## AWS Secrets Manager

```python
import boto3
import json

# Получить секрет
def get_secret(secret_name: str) -> dict:
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Использование
db_creds = get_secret('prod/database/postgres')
connection = psycopg2.connect(
    host=db_creds['host'],
    user=db_creds['username'],
    password=db_creds['password'],
    database=db_creds['database']
)
```

```bash
# CLI
aws secretsmanager create-secret \
  --name prod/database/postgres \
  --secret-string '{"username":"admin","password":"secret123"}'

# Получить
aws secretsmanager get-secret-value --secret-id prod/database/postgres

# Rotation (Lambda-based)
aws secretsmanager rotate-secret \
  --secret-id prod/database/postgres \
  --rotation-lambda-arn arn:aws:lambda:...
```

### Terraform

```hcl
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "prod/database/postgres"
  recovery_window_in_days = 7

  tags = {
    Environment = "production"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "admin"
    password = random_password.db.result
    host     = aws_db_instance.main.endpoint
  })
}

# Авто-ротация
resource "aws_secretsmanager_secret_rotation" "db_password" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = aws_lambda_function.rotate_secret.arn

  rotation_rules {
    automatically_after_days = 30
  }
}
```

---

## HashiCorp Vault

```
┌─────────────────────────────────────────────────────────────────┐
│                    VAULT ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      VAULT SERVER                       │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              SECRETS ENGINES                    │   │   │
│  │  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │   │   │
│  │  │  │  KV  │ │ AWS  │ │  DB  │ │ PKI  │          │   │   │
│  │  │  │(static)│(dynamic)│(dynamic)│(certs)│        │   │   │
│  │  │  └──────┘ └──────┘ └──────┘ └──────┘          │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                         │                               │   │
│  │  ┌─────────────────────▼───────────────────────────┐   │   │
│  │  │                AUTH METHODS                     │   │   │
│  │  │  Token, LDAP, AWS IAM, Kubernetes, OIDC        │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                         │                               │   │
│  │  ┌─────────────────────▼───────────────────────────┐   │   │
│  │  │                AUDIT LOG                        │   │   │
│  │  │  Every access logged                            │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  STORAGE: Consul, S3, GCS, PostgreSQL                          │
│  ENCRYPTION: Seal keys, auto-unseal (AWS KMS, etc.)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Vault CLI

```bash
# Login
vault login -method=aws role=my-role

# Static secrets (KV)
vault kv put secret/myapp/config api_key=abc123 db_password=secret
vault kv get secret/myapp/config

# Dynamic secrets (Database)
# Vault создаёт временного пользователя PostgreSQL
vault read database/creds/my-role
# Returns: username, password с TTL

# Renew lease
vault lease renew <lease_id>

# Revoke (при компрометации)
vault lease revoke <lease_id>
```

### Dynamic Database Secrets

```hcl
# Vault configuration
resource "vault_database_secret_backend_connection" "postgres" {
  backend       = "database"
  name          = "postgres"
  allowed_roles = ["readonly", "admin"]

  postgresql {
    connection_url = "postgres://vault:password@db.example.com:5432/mydb"
  }
}

resource "vault_database_secret_backend_role" "readonly" {
  backend             = "database"
  name                = "readonly"
  db_name             = vault_database_secret_backend_connection.postgres.name
  creation_statements = [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";"
  ]
  default_ttl         = 3600  # 1 hour
  max_ttl             = 86400 # 24 hours
}
```

```python
# Application получает dynamic credentials
import hvac

client = hvac.Client(url='https://vault.example.com')
client.auth.kubernetes.login(role='myapp', jwt=service_account_token)

# Получить временные DB credentials
creds = client.secrets.database.generate_credentials('readonly')
username = creds['data']['username']
password = creds['data']['password']
# TTL: 1 hour, потом Vault автоматически удалит user из PostgreSQL
```

---

## Kubernetes Secrets

```yaml
# ❌ НЕ ДЕЛАЙ ТАК (base64 — не encryption!)
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: cGFzc3dvcmQxMjM=  # base64, легко декодировать

# ✅ External Secrets Operator (с AWS Secrets Manager)
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: db-secret
  data:
    - secretKey: password
      remoteRef:
        key: prod/database/postgres
        property: password

# ✅ Sealed Secrets (encrypted в git)
# kubeseal шифрует, только controller может расшифровать
```

---

## Rotation Best Practices

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROTATION STRATEGY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. DUAL CREDENTIALS                                           │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ Before rotation:  Key A (active)                    │    │
│     │ During rotation:  Key A + Key B (both work)         │    │
│     │ After rotation:   Key B (active), Key A (revoked)   │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│  2. DYNAMIC SECRETS (Vault)                                    │
│     • Каждый запрос = новые credentials                        │
│     • TTL = 1 hour (auto-expire)                              │
│     • Нет rotation — credentials short-lived                  │
│                                                                 │
│  3. ROTATION SCHEDULE                                          │
│     ┌────────────────────────────────────────────────────┐     │
│     │ Secret Type        │ Rotation Period              │     │
│     ├────────────────────┼──────────────────────────────┤     │
│     │ API Keys           │ 90 days                      │     │
│     │ Database passwords │ 30 days                      │     │
│     │ Service accounts   │ 90 days                      │     │
│     │ TLS certificates   │ Before expiry (auto-renew)   │     │
│     │ After compromise   │ IMMEDIATELY                  │     │
│     └────────────────────┴──────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Связи

- [[security-overview]] — карта раздела
- [[cloud-aws-core-services]] — AWS Secrets Manager
- [[kubernetes-basics]] — Kubernetes secrets
- [[devops-overview]] — secrets в CI/CD

---

## Источники

- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [External Secrets Operator](https://external-secrets.io/)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## Связь с другими темами

[[security-fundamentals]] — управление секретами является практическим применением принципа Confidentiality из CIA Triad. Понимание базовых концепций безопасности (defense in depth, least privilege) определяет архитектуру secrets management: почему нужны отдельные хранилища, зачем ротация, почему environment variables недостаточны. Без фундамента в security-fundamentals сложно оценить, какой уровень защиты секретов адекватен для конкретной системы.

[[cloud-aws-core-services]] — AWS Secrets Manager, AWS KMS и IAM роли являются конкретными инструментами для реализации secrets management в облачной инфраструктуре. Понимание IAM policies, resource-based policies и service-linked roles необходимо для правильной настройки доступа к секретам. Рекомендуется изучить secrets-management для концептуального понимания, а затем aws-core-services для практической реализации.

[[security-incident-response]] — компрометация секретов (leaked API key, exposed database password) — один из самых частых типов инцидентов безопасности. План реагирования должен включать процедуры экстренной ротации секретов, и знание secrets management определяет скорость recovery. Incident response информирует secrets management о необходимости автоматизации ротации и мониторинга доступа.

[[infrastructure-as-code]] — Terraform, Pulumi и другие IaC-инструменты тесно интегрируются с secrets management для безопасного управления credentials инфраструктуры. Правильная интеграция предотвращает хранение секретов в state-файлах и шаблонах. Изучение IaC и secrets management рекомендуется параллельно.

[[docker-for-developers]] — контейнеризация создаёт специфические вызовы для управления секретами: environment variables видны через docker inspect, Kubernetes Secrets кодируются в base64 (не шифруются). Понимание этих ограничений критично для выбора правильного решения (External Secrets Operator, Sealed Secrets, Vault Agent Injector).

---

## Источники и дальнейшее чтение

- Anderson R. (2020). *Security Engineering: A Guide to Building Dependable Distributed Systems.* 3rd Edition. Wiley. — фундаментальное руководство по инженерии безопасности, включая принципы управления ключами и секретами в распределённых системах.
- Stallings W. (2017). *Cryptography and Network Security: Principles and Practice.* 7th Edition. Pearson. — для понимания криптографических основ, на которых строятся механизмы шифрования секретов (AES, KDF, key wrapping).
- McGraw G. (2006). *Software Security: Building Security In.* Addison-Wesley. — принципы безопасной разработки, включая правила работы с credentials и секретами на уровне кода и архитектуры.

---

*Проверено: 2025-12-22*

---

## Проверь себя

> [!question]- Почему dynamic secrets в Vault безопаснее, чем автоматическая ротация статических секретов через AWS Secrets Manager?
> Dynamic secrets генерируются по запросу с коротким TTL (например, 1 час) и автоматически удаляются после истечения lease. Статические секреты, даже при ротации каждые 30 дней, живут всё это время — и в случае компрометации атакующий получает доступ до следующей ротации. С dynamic secrets окно компрометации сужается до минут/часов. Кроме того, каждое приложение получает уникальные credentials, что упрощает аудит и отзыв доступа конкретного потребителя.

> [!question]- Команда использует Kubernetes и хранит секреты как стандартные K8s Secrets (base64). Какую комбинацию инструментов вы бы выбрали для перехода на безопасную схему и почему?
> Оптимальный путь: External Secrets Operator + облачный Secrets Manager (AWS/GCP) или Vault. ESO синхронизирует секреты из внешнего хранилища в K8s Secrets автоматически, обеспечивая encryption at rest, аудит, ротацию и IAM-контроль доступа. Sealed Secrets — альтернатива для хранения зашифрованных секретов в git, но без централизованного управления. Для enterprise-сценариев с мульти-кластерной архитектурой — Vault Agent Injector, который инжектирует секреты напрямую в pod без создания K8s Secret объектов.

> [!question]- Как принцип defense in depth из security-fundamentals проявляется в архитектуре secrets management? Приведите конкретные слои защиты.
> Defense in depth в secrets management реализуется через несколько слоёв: (1) encryption at rest — секреты зашифрованы в хранилище; (2) encryption in transit — TLS при передаче; (3) access control — IAM policies / Vault policies ограничивают кто может читать какие секреты; (4) audit logging — каждый доступ логируется; (5) rotation — даже при компрометации секрет скоро станет недействительным; (6) network segmentation — Vault/Secrets Manager доступен только из определённых сетей. Ни один слой не является достаточным сам по себе — безопасность обеспечивается их совокупностью.

> [!question]- Разработчик случайно закоммитил API-ключ в публичный git-репозиторий. Опишите порядок действий, учитывая что простое удаление коммита недостаточно.
> Порядок действий: (1) Немедленно отозвать/ротировать скомпрометированный ключ — это приоритет номер один; (2) Удалить секрет из истории git через BFG Repo Cleaner или git filter-branch + force push; (3) Учитывать, что старые коммиты на GitHub остаются доступны по SHA даже после force push — при высокой критичности секрета может потребоваться удаление и пересоздание репозитория; (4) Проверить логи на предмет несанкционированного использования ключа; (5) Добавить pre-commit hook (например, detect-secrets, gitleaks) для предотвращения повторных утечек; (6) Добавить паттерн секрета в .gitignore.

---

## Ключевые карточки

Почему environment variables не подходят для production секретов?
?
Они видны через /proc, ps, docker inspect. Нет аудита, контроля доступа и ротации. Для production нужен Secrets Manager или Vault.

Что такое dynamic secrets в HashiCorp Vault?
?
Vault генерирует уникальные credentials по запросу с коротким TTL. После истечения lease Vault автоматически отзывает credentials (например, удаляет временного пользователя БД).

Как работает dual credentials strategy при ротации API ключей?
?
Создаётся новый ключ (Key B) при активном старом (Key A). Приложения переключаются на Key B. После проверки Key A отзывается. Оба ключа работают одновременно в переходный период.

Почему base64 в Kubernetes Secrets — это не шифрование?
?
Base64 — это кодирование, не шифрование. Любой с доступом к etcd или kubectl может декодировать секрет командой base64 -d. Нужен External Secrets Operator, Sealed Secrets или Vault.

Какие secrets engines есть в HashiCorp Vault?
?
KV (статические секреты), AWS (динамические IAM credentials), Database (временные DB-пользователи), PKI (автоматическая генерация TLS-сертификатов). Каждый engine решает свой класс задач.

Какой рекомендуемый период ротации для database passwords и API keys?
?
Database passwords — каждые 30 дней, API keys и service accounts — каждые 90 дней, TLS-сертификаты — до истечения с auto-renew. При компрометации — немедленная ротация.

Как External Secrets Operator решает проблему K8s Secrets?
?
ESO синхронизирует секреты из внешнего хранилища (AWS Secrets Manager, Vault) в Kubernetes, обеспечивая encryption at rest, аудит и автоматическое обновление с заданным refreshInterval.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Фундамент безопасности | [[security-fundamentals]] | Понять CIA Triad и defense in depth — основу архитектуры secrets management |
| Криптография | [[security-cryptography-fundamentals]] | Разобраться в AES, KDF, key wrapping — механизмах шифрования секретов |
| Реагирование на инциденты | [[security-incident-response]] | Отработать процедуры экстренной ротации при утечке секретов |
| AWS облачные сервисы | [[cloud-aws-core-services]] | Практическая реализация Secrets Manager, KMS и IAM ролей |
| Kubernetes | [[kubernetes-basics]] | Понять ограничения K8s Secrets и интеграцию с External Secrets Operator |
| Infrastructure as Code | [[infrastructure-as-code]] | Научиться безопасно управлять секретами в Terraform/Pulumi без утечек в state |
| Контейнеризация | [[docker-for-developers]] | Изучить специфику secrets в контейнерах — docker inspect, multi-stage builds |

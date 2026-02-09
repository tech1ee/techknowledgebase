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

## Проверь себя

<details>
<summary>1. Почему environment variables — не идеальное решение?</summary>

**Ответ:**
- Видны в `/proc/<pid>/environ`
- Видны через `docker inspect`
- Видны в `ps e` (на некоторых системах)
- Нет audit logging
- Нет fine-grained access control
- Нет versioning и rotation

OK для dev, но для production лучше Secrets Manager или Vault.

</details>

<details>
<summary>2. Что такое dynamic secrets в Vault?</summary>

**Ответ:** Vault генерирует credentials по запросу с ограниченным TTL:
- Приложение запрашивает credentials
- Vault создаёт временного пользователя в БД
- Credentials работают ограниченное время (lease)
- После TTL Vault удаляет пользователя

Преимущества: нет долгоживущих credentials, автоматическая ротация.

</details>

<details>
<summary>3. Как правильно ротировать API ключи?</summary>

**Ответ:** Dual credentials strategy:
1. Создать новый ключ (Key B)
2. Обновить приложения на Key B
3. Проверить что Key A не используется
4. Отозвать Key A

Никогда не удаляй старый ключ сразу — сначала убедись что новый работает.

</details>

<details>
<summary>4. Почему base64 в Kubernetes Secrets — не encryption?</summary>

**Ответ:** base64 — это encoding, не encryption:
- `echo "password" | base64` → `cGFzc3dvcmQ=`
- `echo "cGFzc3dvcmQ=" | base64 -d` → `password`

Любой с доступом к etcd или kubectl может прочитать.

Решения:
- Encryption at rest в etcd
- External Secrets Operator
- Sealed Secrets
- Vault integration

</details>

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

*Проверено: 2025-12-22*

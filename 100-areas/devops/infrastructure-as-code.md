---
title: "Infrastructure as Code: Terraform и декларативный подход"
created: 2025-11-24
modified: 2025-11-24
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/devops
  - devops/iac
  - devops/terraform
  - automation/infrastructure
  - type/concept
  - level/intermediate
related:
  - "[[ci-cd-pipelines]]"
  - "[[kubernetes-basics]]"
  - "[[docker-for-developers]]"
prerequisites:
  - "[[docker-for-developers]]"
  - "[[ci-cd-pipelines]]"
---

# Infrastructure as Code: Terraform и декларативный подход

> **Аналогия для понимания:** Infrastructure as Code — это как **чертёж здания** вместо устных инструкций строителям. Раньше: "Построй стену здесь, окно там" — и каждый дом получался разным. С чертежом: точные размеры, материалы, расположение — любой строитель построит идентично. IaC — это чертёж для облачной инфраструктуры: описываешь в коде "нужен сервер такой-то, база данных такая-то" — и Terraform создаёт одинаково каждый раз. Spotify сократила время развёртывания с 14 дней до 5 минут именно благодаря этому подходу.

47 кликов в AWS Console → `terraform apply`. Всё задокументировано в Git. Terraform — multi-cloud декларативный стандарт. State — потенциальная точка отказа, храни в remote backend с блокировкой.

---

## Prerequisites (Что нужно знать заранее)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **Облако (AWS/GCP/Azure)** | Terraform управляет облачными ресурсами — нужно понимать что это | Бесплатные курсы облачных провайдеров |
| **Командная строка** | Terraform — CLI инструмент | Базовый bash/terminal |
| **Git basics** | IaC хранится в репозитории, версионирование | [[git-workflows]] |
| **JSON/YAML** | HCL похож на JSON, понимание структуры данных | 15-минутный туториал |
| **Сеть (basics)** | VPC, subnet, security groups — базовые ресурсы | [[networking-overview]] |

---

## TL;DR (если совсем нет времени)

- **IaC** = инфраструктура описана кодом, хранится в Git, применяется автоматически
- **Terraform** = multi-cloud стандарт (HCL), **Pulumi** = код на Python/Go/TS, **OpenTofu** = open-source форк Terraform
- **Declarative** = описываешь "что хочу", не "как сделать"
- **State** = связь между кодом и реальными ресурсами (КРИТИЧНО защитить!)
- **Netflix** — 300,000 CPU в минутах, **Spotify** — с 14 дней до 5 минут
- **Главные риски**: потеря state, drift (ручные изменения), секреты в state
- **2025 тренд**: OpenTofu растёт (CNCF Sandbox), организации используют 2.6 облака в среднем
- **Начни с**: remote state + блокировка + environments в директориях

---

## Кто использует IaC в production

| Компания | Масштаб | Результат |
|----------|---------|-----------|
| **Netflix** | 300,000 CPU, 1000+ autoscaling groups | Тысячи серверов в минутах, 92% экономия на encoding |
| **Spotify** | 500M+ пользователей, multi-cloud | Развёртывание: 14 дней → 5 минут |
| **Airbnb** | AWS + GCP multi-cloud | Миграция БД с 15 мин downtime, I/O 70→400+ MB/sec |
| **Uber** | Глобальная инфраструктура | Единые стандарты compliance и security |
| **Stripe** | Финтех-масштаб | Аудируемые изменения, SOC 2 compliance |

> **Статистика**: Организации с IaC получают 60% сокращение времени миграции, 70% быстрее деплой, 30% быстрее онбординг новых инженеров.
>
> **Источники**: [Medium: Spotify + Terraform](https://medium.com/@ppraveen2150/how-spotify-scaled-its-infrastructure-and-improved-reliability-with-terraform-0e4b7cb44fa5), [Medium: Companies leveraging Terraform](https://srivastavayushmaan1347.medium.com/how-companies-are-leveraging-terraform-for-real-world-infrastructure-challenges-a-case-study-22e1717b1980)

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **IaC** | Инфраструктура описана кодом | **Чертёж здания**: любой построит одинаково |
| **Declarative** | Описываешь "что хочу", не "как сделать" | **Заказ в ресторане**: "стейк medium" — шеф сам знает как |
| **Imperative** | Описываешь пошаговые инструкции | **Рецепт**: "нарезать лук, обжарить 5 мин..." |
| **State** | Связь между кодом и реальными ресурсами | **Инвентарная книга**: что есть на складе |
| **Provider** | Плагин для работы с облаком | **Переводчик**: Terraform говорит на HCL, AWS — на своём API |
| **Resource** | Единица инфраструктуры (EC2, S3, VPC) | **Кирпич в стене**: базовый строительный блок |
| **Module** | Переиспользуемый набор ресурсов | **Готовый план этажа**: не рисуешь заново каждый раз |
| **Plan** | Показывает что изменится до apply | **Предпросмотр ремонта**: как будет выглядеть |
| **Apply** | Применить изменения к реальной инфраструктуре | **Начать ремонт**: план утверждён, работаем |
| **Remote backend** | Удалённое хранилище state | **Сейф в банке**: важный документ не дома |
| **Drift** | Реальность отличается от кода | **Соседи передвинули забор**: карта не совпадает с местностью |
| **HCL** | HashiCorp Configuration Language | **Архитектурный язык**: специальный язык для чертежей |
| **Terraform Registry** | Каталог готовых модулей | **Каталог типовых проектов домов**: бери и строй |

---

## Проблема: ручное управление инфраструктурой

```
Без IaC:

"Создай сервер для нового проекта"
    ↓
Захожу в AWS Console
    ↓
Кликаю 47 раз
    ↓
"Готово! А какие настройки?"
    ↓
"Не помню, вроде как у того проекта"
    ↓
Через месяц: "Почему prod отличается от staging?"
    ↓
Через год: "Никто не знает как это настроено"

С IaC:

"Создай сервер для нового проекта"
    ↓
git checkout -b new-project
    ↓
Копирую модуль, меняю параметры
    ↓
terraform plan → PR → Review → Merge
    ↓
terraform apply
    ↓
Всё задокументировано в Git
```

---

## Terraform: базовые концепции

### Структура проекта

```
project/
├── main.tf           # Основные ресурсы
├── variables.tf      # Входные переменные
├── outputs.tf        # Выходные значения
├── providers.tf      # Провайдеры (AWS, GCP, etc.)
├── terraform.tfvars  # Значения переменных (НЕ в git если секреты!)
└── modules/
    └── vpc/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

### Базовый пример (AWS EC2)

```hcl
# providers.tf
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

# main.tf
resource "aws_instance" "app" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  tags = {
    Name        = "app-${var.environment}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# outputs.tf
output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IP address"
  value       = aws_instance.app.public_ip
}
```

### Основные команды

```bash
# Инициализация (скачать провайдеры)
terraform init

# Проверка синтаксиса
terraform validate

# Форматирование кода
terraform fmt

# Показать план изменений (ЧТО будет сделано)
terraform plan

# Применить изменения
terraform apply

# Применить без подтверждения (для CI/CD)
terraform apply -auto-approve

# Удалить всё
terraform destroy

# Показать текущее состояние
terraform state list
terraform state show aws_instance.app
```

---

## State: сердце Terraform

```
Что такое state:

┌─────────────────────────────────────────────────────────┐
│ terraform.tfstate                                       │
│                                                         │
│ {                                                       │
│   "resources": [                                        │
│     {                                                   │
│       "type": "aws_instance",                          │
│       "name": "app",                                   │
│       "instances": [{                                  │
│         "attributes": {                                │
│           "id": "i-1234567890abcdef",  ← ID в AWS     │
│           "public_ip": "54.123.45.67"                 │
│         }                                              │
│       }]                                               │
│     }                                                  │
│   ]                                                    │
│ }                                                      │
└─────────────────────────────────────────────────────────┘

State связывает КОД с РЕАЛЬНЫМИ ресурсами
Без state Terraform не знает, что уже создано
```

### Remote State (обязательно для команды)

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"  # Для блокировки
  }
}
```

```
Почему remote state:

Local state:                 Remote state (S3 + DynamoDB):
─────────────────           ─────────────────────────────
• Файл на твоём компе       • Централизованное хранение
• Нельзя работать вместе    • Команда видит одно состояние
• Нет блокировки            • Блокировка при apply
• Потерял файл = проблемы   • Версионирование, бэкапы
```

---

## Модули: переиспользование кода

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.name}-vpc"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnets[count.index]
  availability_zone = var.azs[count.index]

  tags = {
    Name = "${var.name}-public-${count.index + 1}"
  }
}

# modules/vpc/variables.tf
variable "name" {
  type = string
}

variable "environment" {
  type = string
}

variable "cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnets" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "azs" {
  type = list(string)
}

# modules/vpc/outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}
```

```hcl
# Использование модуля
module "vpc" {
  source = "./modules/vpc"

  name        = "my-app"
  environment = "prod"
  cidr_block  = "10.0.0.0/16"
  azs         = ["us-east-1a", "us-east-1b"]
}

# Или из registry
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"
  # ...
}
```

---

## Разделение environments

```
Подход 1: Директории (рекомендуется)

environments/
├── dev/
│   ├── main.tf
│   ├── terraform.tfvars
│   └── backend.tf         # state в dev/
├── staging/
│   ├── main.tf
│   ├── terraform.tfvars
│   └── backend.tf         # state в staging/
└── prod/
    ├── main.tf
    ├── terraform.tfvars
    └── backend.tf         # state в prod/

+ Полная изоляция
+ Разные права доступа
+ Отдельные pipelines
- Дублирование кода (решается модулями)

Подход 2: Workspaces

terraform workspace new dev
terraform workspace new prod
terraform workspace select prod

+ Меньше дублирования
- Один state файл = риск
- Сложнее разграничить права
```

---

## CI/CD интеграция

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    paths:
      - 'terraform/**'
  push:
    branches: [main]
    paths:
      - 'terraform/**'

jobs:
  terraform:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: terraform

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        run: terraform init

      - name: Terraform Format Check
        run: terraform fmt -check

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        run: terraform plan -no-color
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      # Apply только при merge в main
      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## Подводные камни

### Проблема 1: State — единая точка отказа

```
Что может пойти не так:

• State удалён → Terraform не знает что создано
• State повреждён → Частичные apply, drift
• Два apply одновременно → Конфликты, битый state

Защита:
• Remote state с блокировкой (DynamoDB)
• Версионирование S3 bucket
• Регулярные бэкапы
• terraform state pull для локальной копии
```

### Проблема 2: Drift — реальность отличается от кода

```
Кто-то изменил ресурс вручную в консоли
            ↓
Terraform не знает об изменении
            ↓
terraform plan показывает "0 changes"
            ↓
Ложное чувство безопасности

Решения:
• terraform plan -refresh-only  (обновить state)
• Запретить ручные изменения (политика)
• Drift detection в CI (регулярный plan)
```

### Проблема 3: Секреты в state

```
State хранит ВСЕ атрибуты ресурсов, включая:
• Пароли баз данных
• API ключи
• Private keys

State = чувствительные данные!

Защита:
• Encrypt state at rest (S3 encryption)
• Ограничить доступ к bucket
• Не коммитить state в Git (НИКОГДА)
• Использовать secret managers (Vault, AWS Secrets Manager)
```

### Проблема 4: "Terraform hell" при росте

```
Маленький проект:         Большой проект:
─────────────────         ─────────────────
1 main.tf                 500+ ресурсов
Всё просто                terraform plan = 10 минут
                          Один state = страшно менять
                          Blast radius огромный

Решения:
• Разбить на модули
• Разбить state по компонентам
• Terragrunt для DRY
```

---

## Actionable

**Начало:**
```bash
# Установка
brew install terraform  # macOS
# или через tfenv для версий

# Первый проект
mkdir learn-terraform && cd learn-terraform
terraform init
```

**Для существующей инфраструктуры:**
```bash
# Import существующих ресурсов
terraform import aws_instance.app i-1234567890abcdef
```

**Best practices чеклист:**
```
□ Remote state с блокировкой
□ Environments разделены (директории)
□ Модули для переиспользования
□ Версии провайдеров зафиксированы
□ terraform fmt в pre-commit
□ Plan в PR, Apply после merge
□ Секреты в secret manager, не в tfvars
```

---

## Связи

- CI/CD для Terraform: [[ci-cd-pipelines]]
- Terraform для K8s: [[kubernetes-basics]]
- Контейнеры в IaC: [[docker-for-developers]]

---

## Сравнение инструментов IaC (2025)

| Критерий | Terraform | OpenTofu | Pulumi |
|----------|-----------|----------|--------|
| **Язык** | HCL (декларативный) | HCL (100% совместим) | Python, Go, TS, C# |
| **Лицензия** | BSL (ограничения для SaaS) | MPL 2.0 (open source) | Apache 2.0 |
| **Экосистема** | Самая большая (1000+ providers) | Наследует от Terraform | Использует Terraform providers |
| **State** | .tfstate (S3, Terraform Cloud) | .tfstate (совместим) | Stacks (Pulumi Service, S3) |
| **Управление** | HashiCorp (коммерция) | Linux Foundation (CNCF) | Pulumi Inc. |
| **Лучше для** | Enterprise, multi-cloud | Open source проекты | Разработчики (coding-first) |

> **Тренд 2025**: OpenTofu принят в CNCF Sandbox (апрель 2025). Организации используют в среднем 2.6 облачных провайдеров. Hybrid подход — Terraform + Spacelift + Checkov — становится нормой.
>
> **Рекомендация**:
> - **Terraform** — если нужен enterprise support и не SaaS
> - **OpenTofu** — если важна open source свобода и совместимость с Terraform
> - **Pulumi** — если команда предпочитает обычные языки программирования
>
> **Источники**: [Toolshelf: Terraform vs Pulumi vs OpenTofu 2025](https://toolshelf.tech/blog/terraform-vs-pulumi-vs-opentofu-2025-iac-showdown/), [OSFY: How to Choose](https://www.opensourceforu.com/2025/10/how-to-choose-between-terraform-pulumi-and-opentofu/)

---

## Источники

### Официальная документация
- [HashiCorp: Infrastructure as Code Introduction](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/infrastructure-as-code) — проверено 2025-01-03
- [OpenTofu Documentation](https://opentofu.org/docs/) — проверено 2025-01-03
- [Pulumi Docs](https://www.pulumi.com/docs/) — проверено 2025-01-03

### Кейсы компаний
- [Medium: Spotify + Terraform](https://medium.com/@ppraveen2150/how-spotify-scaled-its-infrastructure-and-improved-reliability-with-terraform-0e4b7cb44fa5) — проверено 2025-01-03
- [Medium: Companies leveraging Terraform](https://srivastavayushmaan1347.medium.com/how-companies-are-leveraging-terraform-for-real-world-infrastructure-challenges-a-case-study-22e1717b1980) — проверено 2025-01-03
- [Moldstud: Terraform Case Study](https://moldstud.com/articles/p-achieving-infrastructure-as-code-a-comprehensive-case-study-on-terraform-usage) — проверено 2025-01-03

### Best Practices
- [Spacelift: 20 Terraform Best Practices](https://spacelift.io/blog/terraform-best-practices) — проверено 2025-01-03
- [Spacelift: IaC Tools 2025](https://spacelift.io/blog/infrastructure-as-code-tools) — проверено 2025-01-03
- [Bluelight: Best IaC Tools 2025](https://bluelight.co/blog/best-infrastructure-as-code-tools) — проверено 2025-01-03

### Сравнения инструментов
- [Toolshelf: Terraform vs Pulumi vs OpenTofu 2025](https://toolshelf.tech/blog/terraform-vs-pulumi-vs-opentofu-2025-iac-showdown/) — проверено 2025-01-03
- [OSFY: How to Choose Between Terraform, Pulumi, OpenTofu](https://www.opensourceforu.com/2025/10/how-to-choose-between-terraform-pulumi-and-opentofu/) — проверено 2025-01-03
- [Spacelift: Pulumi vs Terraform](https://spacelift.io/blog/pulumi-vs-terraform) — проверено 2025-01-03

---

**Последняя верификация**: 2025-01-03
**Уровень достоверности**: high

---

*Проверено: 2026-01-09*

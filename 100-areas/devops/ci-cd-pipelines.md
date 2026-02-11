---
title: "CI/CD: автоматизация, которая меняет всё"
created: 2025-11-24
modified: 2025-11-24
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/devops
  - devops/ci-cd
  - automation/pipelines
  - tools/github-actions
  - type/concept
  - level/intermediate
related:
  - "[[docker-for-developers]]"
  - "[[technical-debt]]"
  - "[[git-workflows]]"
prerequisites:
  - "[[git-workflows]]"
  - "[[docker-for-developers]]"
---

# CI/CD: автоматизация, которая меняет всё

> **Аналогия для понимания:** CI/CD — это как **автоматическая линия на заводе Toyota**. Раньше рабочие вручную проверяли каждую деталь, собирали машину, тестировали — и всё это занимало недели. Toyota создала конвейер: деталь движется автоматически, на каждом этапе проверка, брак сразу отбраковывается. Результат: машина сходит с конвейера каждые 60 секунд вместо недель. CI/CD — это тот же конвейер, но для кода: push → автоматическая сборка → автотесты → деплой. Amazon довёл это до совершенства: деплой каждые 11.6 секунд.

Elite команды деплоят в 973× чаще и решают инциденты в 6570× быстрее (State of DevOps 2024). CI/CD — автоматический конвейер: push → build → test → deploy за минуты вместо часов.

---

## Prerequisites (Что нужно знать заранее)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **Git basics** | CI/CD реагирует на git push/merge — без Git не понять триггеры | [[git-workflows]] или любой Git-курс |
| **Командная строка** | Pipeline выполняет bash-команды (npm test, docker build) | Базовый курс Linux/Terminal |
| **Что такое тесты** | CI запускает тесты автоматически — нужно понимать зачем | Unit testing basics |
| **Docker (опционально)** | Многие pipeline используют контейнеры | [[docker-for-developers]] |
| **YAML синтаксис** | Pipeline описывается в YAML-файлах | 15-минутный туториал по YAML |

---

## TL;DR (если совсем нет времени)

- **CI (Continuous Integration)** = автоматический build + тесты при каждом push
- **CD (Continuous Delivery)** = автодеплой на staging + ручной approve для production
- **CD (Continuous Deployment)** = полностью автоматический деплой до production
- **Amazon** деплоит каждые **11.6 секунд**, Netflix — тысячи раз в день
- **DORA метрики**: Deployment Frequency, Lead Time, Change Failure Rate, MTTR
- **Elite команды** vs Low: в 973× чаще деплоят, в 6570× быстрее восстанавливаются
- **Главные анти-паттерны**: монолитные pipelines, sequential тесты, хардкод конфигов
- **Начни с малого**: один YAML файл с `npm ci && npm test` — уже CI

---

## Кто использует CI/CD в production

| Компания | Масштаб | Технологии | Результат |
|----------|---------|------------|-----------|
| **Amazon** | Деплой каждые 11.6 сек | Apollo, Pipelines | 90% сокращение времени от commit до production |
| **Netflix** | Тысячи деплоев/день | Spinnaker, Jenkins | 50M деплоев/год, multi-cloud CD |
| **Google** | Тысячи деплоев/день | Bazel, hermetic builds | 99.99% uptime, monorepo на 2+ млрд строк |
| **Etsy** | 50+ деплоев/день | Custom CD | От 2 деплоев/неделю до 50+/день |
| **Facebook** | Тысячи инженеров | Sandcastle | Trunk-based development, быстрый feedback |

> **Источник**: [All Things Distributed — Apollo](https://www.allthingsdistributed.com/2014/11/apollo-amazon-deployment-engine.html), [CD Foundation — Spinnaker Case Study](https://cd.foundation/case-studies/spinnaker-case-studies/spinnaker-case-study-netflix/)

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **CI (Continuous Integration)** | Автоматический build + тесты при каждом push | **Проверка домашки учителем**: сдал работу → автоматически проверяется → сразу видишь ошибки |
| **CD (Continuous Delivery)** | Автодеплой на staging, ручной approve для prod | **Посылка на почте**: доставлена, но ты должен прийти и забрать (нажать кнопку) |
| **CD (Continuous Deployment)** | Полностью автоматический деплой до production | **Курьерская доставка до двери**: посылка сама приходит к тебе без твоего участия |
| **Pipeline (Пайплайн)** | Последовательность этапов: build → test → deploy | **Конвейер на заводе**: деталь проходит станции одну за другой |
| **Artifact** | Результат сборки (JAR, Docker image, бинарник) | **Готовый продукт**: из сырья (код) получили товар (артефакт) |
| **Stage** | Этап пайплайна (build, test, deploy) | **Станция на конвейере**: сварка, покраска, сборка — разные станции |
| **Job** | Конкретная задача внутри этапа | **Операция на станции**: на станции "покраска" — нанести грунт, нанести краску, высушить |
| **Runner** | Сервер/агент, выполняющий пайплайн | **Рабочий на конвейере**: физически выполняет операции |
| **Trigger** | Событие, запускающее pipeline | **Кнопка "старт" на конвейере**: push в git = нажал кнопку |
| **Cache** | Сохранённые зависимости между запусками | **Инструменты на станции**: не несёшь из кладовки каждый раз, лежат рядом |
| **Matrix build** | Тестирование на разных версиях/ОС параллельно | **Краш-тест на разных моделях**: один тест, много машин одновременно |
| **Flaky test** | Тест, который то падает, то проходит | **Ненадёжный датчик**: иногда пищит без причины |
| **Quality gate** | Порог качества для прохождения дальше | **ОТК на заводе**: брак не пропускают на следующий этап |

---

## Проблема, которую решает CI/CD

Типичный день без CI/CD:

```
09:00  Разработчик закончил фичу
09:30  "Сейчас затестирую локально..."
11:00  "Работает! Мержу в main"
11:05  Build сломался (забыл зависимость)
11:30  Починил, снова мержу
11:35  Тесты падают на CI (работало локально!)
12:00  Обед, разберусь потом
14:00  Наконец замержено
14:15  QA: "На стейджинге не работает"
15:00  Оказалось, конфиг отличается
16:00  Деплой в прод
16:05  Алерты! Откатываем...
       ─────────────────────────
       Итого: 7 часов на одну фичу
```

С CI/CD:

```
09:00  Разработчик закончил фичу
09:01  Push → Pipeline запустился автоматически
09:05  ✓ Lint, ✓ Tests, ✓ Build, ✓ Security scan
09:10  Auto-deploy на staging
09:15  ✓ E2E тесты прошли
09:20  Approve → Auto-deploy в production
09:25  ✓ Мониторинг: всё зелёное
       ─────────────────────────
       Итого: 25 минут
```

---

## CI vs CD: в чём разница

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTINUOUS INTEGRATION (CI)               │
│                                                              │
│   Push → Build → Test → Merge                                │
│     │      │       │       │                                 │
│     ▼      ▼       ▼       ▼                                 │
│   Код   Компиля-  Unit   Интегра-                           │
│   в     ция +    тесты   ция в                              │
│   репо  линтинг          main                               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  CONTINUOUS DELIVERY (CD)                    │
│                                                              │
│   Merge → Stage → Review → Deploy (manual)                   │
│     │       │        │         │                             │
│     ▼       ▼        ▼         ▼                             │
│   Main   Staging   Approve   Production                      │
│   branch  env      button    (по кнопке)                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 CONTINUOUS DEPLOYMENT                        │
│                                                              │
│   Merge → Stage → Deploy (auto)                              │
│     │       │         │                                      │
│     ▼       ▼         ▼                                      │
│   Main   Staging   Production                                │
│   branch  env      (автоматически)                           │
└─────────────────────────────────────────────────────────────┘
```

**Ключевое различие:**
- **Continuous Delivery** — деплой готов, но требует ручного approve
- **Continuous Deployment** — деплой автоматический после всех проверок

---

## GitHub Actions: практический старт

### Базовая структура workflow

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

# Когда запускать
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

# Переменные окружения (глобальные)
env:
  NODE_VERSION: '20'

jobs:
  # Job 1: Проверка кода
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'  # ← Кэширование зависимостей

      - run: npm ci
      - run: npm run lint

  # Job 2: Тесты (параллельно с lint)
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - run: npm ci
      - run: npm test -- --coverage

      # Загрузка coverage отчёта
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  # Job 3: Сборка (после успешных lint и test)
  build:
    needs: [lint, test]  # ← Зависимость
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      # Сохранение артефакта
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/
```

### Matrix builds: тестирование на разных версиях

```yaml
test:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      node-version: [18, 20, 22]
      os: [ubuntu-latest, macos-latest]
    fail-fast: false  # Не останавливать при первой ошибке

  steps:
    - uses: actions/checkout@v4
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
    - run: npm ci
    - run: npm test
```

### Секреты и безопасность

```yaml
deploy:
  runs-on: ubuntu-latest
  environment: production  # ← Требует approve
  steps:
    - name: Deploy to AWS
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |
        aws s3 sync ./dist s3://my-bucket
```

**Критично:** Никогда не хардкодить секреты в workflow файлах!

```yaml
# ❌ НИКОГДА так не делать
env:
  API_KEY: "sk-1234567890abcdef"

# ✅ Только через secrets
env:
  API_KEY: ${{ secrets.API_KEY }}
```

---

## Продвинутые паттерны

### Кэширование зависимостей

```yaml
- name: Cache node modules
  uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

# Эффект: npm ci за 5 сек вместо 45 сек
```

### Conditional jobs

```yaml
deploy:
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  needs: [build, test]
  # ...

# Деплой только при push в main, не при PR
```

### Reusable workflows

```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      deploy_key:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - run: echo "Deploying to ${{ inputs.environment }}"
```

```yaml
# .github/workflows/main.yml
jobs:
  deploy-staging:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
    secrets:
      deploy_key: ${{ secrets.STAGING_KEY }}
```

---

## Security: DevSecOps в pipeline

### Сканирование секретов

```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Полная история для сканирования

    # Gitleaks — поиск секретов в коде
    - name: Gitleaks
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Факт:** В 2024 году более 10 миллионов секретов было обнаружено в публичных репозиториях (GitGuardian Report).

### SAST (Static Application Security Testing)

```yaml
- name: CodeQL Analysis
  uses: github/codeql-action/analyze@v3
  with:
    languages: javascript, typescript
```

### Dependency scanning

```yaml
- name: Dependency Review
  uses: actions/dependency-review-action@v4
  with:
    fail-on-severity: high
```

---

## Quality Gates: не пропускать плохой код

```yaml
quality-gate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    # Проверка покрытия тестами
    - name: Check coverage threshold
      run: |
        COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
        if (( $(echo "$COVERAGE < 80" | bc -l) )); then
          echo "Coverage $COVERAGE% is below 80% threshold"
          exit 1
        fi

    # Проверка размера бандла
    - name: Check bundle size
      run: |
        SIZE=$(stat -f%z dist/main.js)
        MAX_SIZE=500000  # 500KB
        if [ $SIZE -gt $MAX_SIZE ]; then
          echo "Bundle size $SIZE exceeds $MAX_SIZE"
          exit 1
        fi
```

---

## Подводные камни и честная правда

### Проблема 1: Pipeline — это код, который нужно поддерживать

```
Реальность CI/CD:

Написать pipeline:     2 часа
Отладить pipeline:     8 часов
Поддерживать pipeline: бесконечно

Типичные проблемы:
• Flaky tests (то падают, то нет)
• Зависимости между jobs
• Дебаг в CI сложнее, чем локально
• "Works on my machine" никуда не делся
```

### Проблема 2: Ложное чувство безопасности

```
"У нас 100% покрытие и все тесты зелёные"
                    ↓
Но тесты проверяют не то, что важно
                    ↓
Production всё равно падает

Тесты ≠ Качество
Зелёный pipeline ≠ Рабочий продукт
```

### Проблема 3: Self-hosted runners и безопасность

```
Public repo + Self-hosted runner = Риск

Злоумышленник может:
• Создать PR с вредоносным кодом
• Код выполнится на вашем runner'е
• Доступ к вашей инфраструктуре

Решение:
• Public repos → только GitHub-hosted runners
• Self-hosted → только для private repos
• Изолированная среда для runners
```

### Проблема 4: Время выполнения pipeline

```
Типичная эволюция:

Месяц 1:   Pipeline 3 минуты   ✓ Отлично
Месяц 6:   Pipeline 15 минут   → Терпимо
Месяц 12:  Pipeline 45 минут   → Разработчики не ждут
Месяц 18:  Pipeline 90 минут   → Мержат без CI

Решения:
• Параллельные jobs
• Кэширование
• Incremental builds
• Test sharding
```

---

## Метрики успеха

DORA Metrics (DevOps Research and Assessment):

| Метрика | Elite | High | Medium | Low |
|---------|-------|------|--------|-----|
| **Deployment Frequency** | Multiple/day | Weekly | Monthly | <6 months |
| **Lead Time for Changes** | <1 hour | 1 day-1 week | 1-6 months | >6 months |
| **Change Failure Rate** | 0-15% | 16-30% | 31-45% | 46-60% |
| **Time to Restore** | <1 hour | <1 day | 1 day-1 week | >6 months |

**Факт:** Elite команды деплоят в 973 раза чаще и восстанавливаются в 6570 раз быстрее (State of DevOps 2024).

---

## Когда CI/CD НЕ нужен

```
Не инвестируй в CI/CD если:

• Solo-проект на выходных
• Прототип на 2 недели
• Команда 1-2 человека без планов роста
• Нет автотестов (сначала тесты, потом CI)

В этих случаях:
• Ручной деплой быстрее
• Overhead на настройку не окупится
• Лучше потратить время на продукт
```

---

## Actionable: с чего начать

**День 1: Минимальный CI**
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test
```

**Неделя 1: Добавить lint + build**
- ESLint/Prettier
- TypeScript проверки
- Сборка артефактов

**Месяц 1: Security + CD**
- Сканирование зависимостей
- Автодеплой на staging
- Quality gates

**Постоянно:**
- Мониторить время pipeline
- Удалять flaky tests
- Документировать workflow

---

## Связи

- Контейнеризация для CI/CD: [[docker-for-developers]]
- Pipeline как часть системы: [[technical-debt]]
- Стратегии ветвления: [[git-workflows]]
- Архитектура для быстрых деплоев: [[microservices-vs-monolith]]

---

## Сравнение инструментов (2024-2025)

| Критерий | GitHub Actions | GitLab CI | Jenkins |
|----------|----------------|-----------|---------|
| **Простота старта** | ⭐⭐⭐⭐⭐ Очень легко | ⭐⭐⭐⭐ Легко | ⭐⭐ Сложно |
| **Гибкость** | ⭐⭐⭐ Средняя | ⭐⭐⭐⭐ Высокая | ⭐⭐⭐⭐⭐ Максимальная |
| **Безопасность** | ⭐⭐⭐ Базовая | ⭐⭐⭐⭐⭐ Встроенный SAST/DAST | ⭐⭐⭐ Через плагины |
| **Стоимость** | Бесплатно до лимитов | Бесплатно + платные фичи | Бесплатно, но нужен сервер |
| **Экосистема** | 15000+ Actions | Встроено в GitLab | 1800+ плагинов |
| **Лучше для** | GitHub-проекты, стартапы | All-in-one DevOps | Enterprise, on-premise |

> **Совет 2025**: Если код на GitHub — начни с GitHub Actions. Если нужен all-in-one DevSecOps — GitLab CI. Jenkins — только для enterprise с выделенной DevOps-командой.
>
> **Источник**: [Northflank — GitHub Actions vs Jenkins](https://northflank.com/blog/github-actions-vs-jenkins), [Dev.to — CI/CD Tools Comparison](https://dev.to/574n13y/jenkins-vs-github-actions-vs-gitlab-ci-2k35)

---

## Анти-паттерны CI/CD (чего избегать)

| Анти-паттерн | Проблема | Решение |
|--------------|----------|---------|
| **Монолитный pipeline** | 45+ минут на каждый commit, один flaky test блокирует всё | Разбить на параллельные jobs, fail-fast |
| **Sequential тесты** | Тесты идут друг за другом, медленный feedback | Параллельные тесты, test sharding |
| **Хардкод конфигов** | `API_KEY: "sk-123..."` в YAML | Secrets management, environment variables |
| **Игнорирование безопасности** | Уязвимости попадают в production | SAST/DAST, dependency scanning, Gitleaks |
| **Self-hosted runner на public repo** | Злоумышленник запускает код на вашем сервере | Только GitHub-hosted для public repos |
| **Pipeline без мониторинга** | Не знаешь, что pipeline занимает 90 минут | Метрики времени, алерты на degradation |

> **Статистика**: 70% организаций заявляют о наличии CI/CD, но только 24% могут деплоить по требованию (GitLab DevSecOps Report 2024)
>
> **Источник**: [EM360Tech — CI/CD Anti-Patterns](https://em360tech.com/tech-articles/cicd-anti-patterns-whats-slowing-down-your-pipeline)

---

## Источники

### Официальная документация
- [GitHub Actions Documentation](https://docs.github.com/en/actions) — проверено 2025-01-03
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/) — проверено 2025-01-03
- [Spinnaker Official](https://spinnaker.io/) — проверено 2025-01-03

### Кейсы компаний
- [All Things Distributed — Apollo: Amazon's Deployment Engine](https://www.allthingsdistributed.com/2014/11/apollo-amazon-deployment-engine.html) — 50M деплоев/год
- [CD Foundation — Spinnaker Case Study: Netflix](https://cd.foundation/case-studies/spinnaker-case-studies/spinnaker-case-study-netflix/) — проверено 2025-01-03
- [AWS Builders Library — Going Faster with Continuous Delivery](https://aws.amazon.com/builders-library/going-faster-with-continuous-delivery/) — проверено 2025-01-03

### Исследования и отчёты
- [State of DevOps Report 2024](https://puppet.com/resources/state-of-devops-report) — DORA metrics
- [GitLab DevSecOps Report 2024](https://about.gitlab.com/developer-survey/) — проверено 2025-01-03
- [GitGuardian State of Secrets Sprawl 2024](https://www.gitguardian.com/state-of-secrets-sprawl-report-2024) — 10M+ утекших секретов

### Сравнения и best practices
- [Northflank — GitHub Actions vs Jenkins](https://northflank.com/blog/github-actions-vs-jenkins) — проверено 2025-01-03
- [Dev.to — Jenkins vs GitHub Actions vs GitLab CI](https://dev.to/574n13y/jenkins-vs-github-actions-vs-gitlab-ci-2k35) — проверено 2025-01-03
- [EM360Tech — CI/CD Anti-Patterns](https://em360tech.com/tech-articles/cicd-anti-patterns-whats-slowing-down-your-pipeline) — проверено 2025-01-03
- [DZone — Continuous Delivery Patterns](https://dzone.com/refcardz/continuous-delivery-patterns) — проверено 2025-01-03

---

**Последняя верификация**: 2025-01-03
**Уровень достоверности**: high

---

*Проверено: 2026-01-09*

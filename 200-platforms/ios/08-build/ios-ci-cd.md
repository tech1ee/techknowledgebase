---
title: "iOS CI/CD: Xcode Cloud, Fastlane, GitHub Actions"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 121
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/devops
  - level/advanced
related:
  - "[[android-ci-cd]]"
  - "[[ci-cd-pipelines]]"
  - "[[ios-code-signing]]"
prerequisites:
  - "[[ios-xcode-fundamentals]]"
  - "[[ios-code-signing]]"
  - "[[ios-testing]]"
---

# iOS CI/CD: Xcode Cloud, Fastlane, GitHub Actions

## TL;DR

iOS CI/CD автоматизирует сборку, тестирование, подписание и дистрибуцию приложений. Главные сложности: требование macOS для сборки, управление сертификатами и provisioning profiles. Основные инструменты: Xcode Cloud (нативное решение Apple), Fastlane (набор Ruby-скриптов), GitHub Actions (универсальная CI/CD платформа с macOS runners).

## Теоретические основы

> **Continuous Integration / Continuous Delivery** (CI/CD) — практика автоматизации сборки, тестирования и доставки программного обеспечения. CI обеспечивает раннее обнаружение интеграционных ошибок через частые слияния в общую ветку; CD автоматизирует путь от коммита до production-готового артефакта (Humble & Farley, 2010).

### Академический контекст

CI/CD для iOS опирается на общие принципы DevOps и специфику Apple-экосистемы:

| Концепция | Автор / год | Суть | Проявление в iOS CI/CD |
|-----------|-------------|------|------------------------|
| Continuous Integration | Fowler, 2000 | Частая интеграция кода с автоматическими проверками | GitHub Actions / Xcode Cloud запускают build + tests на каждый PR |
| Deployment Pipeline | Humble & Farley, 2010 | Автоматический конвейер: build → test → deploy | Build → Unit Tests → UI Tests → Archive → TestFlight → App Store |
| Infrastructure as Code | Puppet (2005), Terraform (2014) | Конфигурация инфраструктуры как версионируемый код | Fastfile (Ruby DSL), xcconfig, Xcode Cloud workflows |
| Reproducible Builds | Debian initiative, 2013 | Одинаковый результат при одинаковых входных данных | SPM.resolved, Podfile.lock, pinned Xcode version |
| Shift Left Testing | Larry Smith, 2001 | Раннее тестирование в жизненном цикле | Pre-commit hooks, SwiftLint, unit tests на каждый push |

### Уникальные ограничения iOS CI/CD

В отличие от серверной и Android-разработки, iOS CI/CD имеет фундаментальные ограничения:

1. **macOS-only build** — Swift compiler и Xcode SDK работают только на macOS (Apple EULA)
2. **Code signing complexity** — сертификаты + provisioning profiles = состояние вне репозитория
3. **Simulator overhead** — UI-тесты требуют iOS Simulator, который потребляет значительные ресурсы
4. **Apple ID authentication** — upload в App Store Connect требует аутентификации

> **Humble & Farley (2010)**: «The goal of continuous delivery is to make deployments — whether of a large-scale distributed system, a complex production environment, an embedded system, or an app — predictable, routine affairs that can be performed on demand.» Для iOS это означает: один `fastlane release` или Xcode Cloud trigger должен довести код от коммита до TestFlight.

### Связь с CS-фундаментом

- [[ci-cd-pipelines]] — общая теория CI/CD, применимая к любой платформе
- [[ios-code-signing]] — signing как критический этап pipeline
- [[ios-testing]] — тесты как gate в deployment pipeline
- [[ios-app-distribution]] — доставка артефакта до пользователя
- [[android-ci-cd]] — сравнение: iOS (macOS-only) vs Android (Linux-friendly)

---

## Зачем это нужно?

### Проблемы ручной сборки iOS

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Ручной релиз iOS приложения                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Developer Machine                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. git pull                          [5 мин]                │   │
│  │ 2. pod install / spm resolve         [5-15 мин]             │   │
│  │ 3. Найти правильный сертификат       [10-30 мин] 😱         │   │
│  │ 4. Выбрать provisioning profile      [10-20 мин] 😱         │   │
│  │ 5. Archive build                     [15-45 мин]            │   │
│  │ 6. Export IPA                        [5-10 мин]             │   │
│  │ 7. Upload to App Store Connect       [10-30 мин]            │   │
│  │ 8. Заполнить метаданные              [15-30 мин]            │   │
│  │ 9. Submit for Review                 [5 мин]                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Итого: 1.5-3.5 часа ручной работы на каждый релиз!               │
│  + Человеческие ошибки                                             │
│  + "На моей машине работает"                                       │
│  + Зависимость от конкретного разработчика                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Уникальные сложности iOS CI/CD

```
┌─────────────────────────────────────────────────────────────────────┐
│              Почему iOS CI/CD сложнее Android                       │
├───────────────────────────────┬─────────────────────────────────────┤
│           iOS                 │              Android                │
├───────────────────────────────┼─────────────────────────────────────┤
│ Требует macOS                 │ Linux/Windows/macOS                 │
│ Code Signing обязательно      │ Только для release                  │
│ Provisioning Profiles         │ Просто keystore                     │
│ Developer Portal синхронизация│ Нет аналога                         │
│ App Store Connect API сложный │ Play Console API проще              │
│ Xcode версии привязаны к SDK  │ Гибкие версии SDK                   │
│ macOS runners дороже          │ Linux runners дешевые               │
└───────────────────────────────┴─────────────────────────────────────┘
```

### Преимущества автоматизации

1. **Консистентность** - каждая сборка идентична
2. **Скорость** - параллельные сборки, кэширование
3. **Отслеживаемость** - логи каждой сборки
4. **Качество** - автоматические тесты перед релизом
5. **Безопасность** - сертификаты хранятся централизованно
6. **Команда** - любой может сделать релиз

## Аналогии из жизни

### CI/CD Pipeline = Конвейер на заводе

```
┌──────────────────────────────────────────────────────────────────┐
│                    Автомобильный завод                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Детали] → [Сборка] → [Проверка] → [Покраска] → [Готовый авто] │
│     ↓          ↓          ↓           ↓             ↓           │
│  [Код]   → [Build]  → [Test]   → [Sign]     → [Distribute]      │
│                                                                  │
│  Принципы конвейера:                                             │
│  • Каждый этап независим                                         │
│  • Дефект останавливает линию                                    │
│  • Стандартизированные процессы                                  │
│  • Автоматизация рутины                                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Xcode Cloud = Заводской конвейер Apple

```
┌──────────────────────────────────────────────────────────────────┐
│              Xcode Cloud - "Всё включено"                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Apple Developer Program                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌───────────┐ │ │
│  │  │ GitHub  │ → │  Xcode  │ → │TestFlight│ → │App Store │ │ │
│  │  │ GitLab  │   │  Cloud  │   │          │   │          │ │ │
│  │  │Bitbucket│   │         │   │          │   │          │ │ │
│  │  └─────────┘   └─────────┘   └─────────┘   └───────────┘ │ │
│  │                     ↑                                      │ │
│  │            Автоматический signing!                        │ │
│  │            macOS runners включены!                        │ │
│  │            Интеграция с App Store Connect!                │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Как покупка автомобиля у дилера:                               │
│  Всё настроено, гарантия, сервис - но выбор ограничен          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Fastlane = Набор роботов-помощников

```
┌──────────────────────────────────────────────────────────────────┐
│                    Fastlane Tool Suite                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🤖 match     - Робот-охранник сертификатов                      │
│               Синхронизирует certificates между машинами        │
│                                                                  │
│  🤖 gym       - Робот-строитель                                  │
│               Собирает IPA файлы                                │
│                                                                  │
│  🤖 pilot     - Робот-пилот TestFlight                           │
│               Загружает builds и управляет тестерами            │
│                                                                  │
│  🤖 deliver   - Робот-курьер в App Store                         │
│               Загружает метаданные, скриншоты, builds           │
│                                                                  │
│  🤖 scan      - Робот-тестировщик                                │
│               Запускает тесты                                   │
│                                                                  │
│  🤖 snapshot  - Робот-фотограф                                   │
│               Делает скриншоты для всех локалей                 │
│                                                                  │
│  Как умный дом: каждый робот выполняет свою задачу,             │
│  но вместе они автоматизируют всё                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### GitHub Actions = Универсальный конвейер с арендой оборудования

```
┌──────────────────────────────────────────────────────────────────┐
│                   GitHub Actions                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    GitHub Cloud                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │                Available Runners                      │ │ │
│  │  │                                                       │ │ │
│  │  │  [ubuntu-latest]  [windows-latest]  [macos-latest]   │ │ │
│  │  │       $0.008/min       $0.016/min      $0.08/min     │ │ │
│  │  │                                      (10x дороже!)    │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Ваш .github/workflows/ios.yml                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ jobs:                                                      │ │
│  │   build:                                                   │ │
│  │     runs-on: macos-latest  ← Арендуем Mac!                │ │
│  │     steps: ...                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Как аренда строительной техники:                               │
│  Платите только за использование, но настраиваете сами          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Code Signing в CI = Пропускная система на завод

```
┌──────────────────────────────────────────────────────────────────┐
│              Code Signing как система безопасности               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                            │
│  │  CI Server      │                                            │
│  │  (Посетитель)   │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  🔐 Проходная (Code Signing)                                ││
│  │                                                              ││
│  │  ┌─────────────────┐  ┌─────────────────┐                  ││
│  │  │ Certificate     │  │ Provisioning    │                  ││
│  │  │ (Удостоверение) │  │ Profile (Пропуск)│                  ││
│  │  │                 │  │                  │                  ││
│  │  │ Кто ты?         │  │ Куда можно?      │                  ││
│  │  │ Проверка Apple  │  │ Какие устройства │                  ││
│  │  │                 │  │ Какие возможности│                  ││
│  │  └─────────────────┘  └─────────────────┘                  ││
│  └─────────────────────────────────────────────────────────────┘│
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  📱 iOS Device / App Store (Охраняемая территория)         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Без правильных документов - входа нет!                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## CI/CD для iOS: обзор

### Типичный iOS CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    iOS CI/CD Pipeline                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │
│  │         │    │         │    │         │    │         │         │
│  │  CODE   │───▶│  BUILD  │───▶│  TEST   │───▶│  SIGN   │         │
│  │         │    │         │    │         │    │         │         │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘         │
│       │              │              │              │               │
│       │              │              │              │               │
│       ▼              ▼              ▼              ▼               │
│  git push       xcodebuild      xcodebuild    codesign            │
│  PR merge       dependencies    test          + profiles          │
│  tag            compile                                            │
│                                                                     │
│            ┌─────────┐    ┌─────────┐    ┌─────────┐              │
│            │         │    │         │    │         │              │
│       ────▶│ UPLOAD  │───▶│DISTRIBUTE───▶│ NOTIFY  │              │
│            │         │    │         │    │         │              │
│            └─────────┘    └─────────┘    └─────────┘              │
│                 │              │              │                    │
│                 ▼              ▼              ▼                    │
│            altool         TestFlight      Slack                   │
│            App Store      App Store       Email                   │
│            Connect        Review          Teams                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Сравнение инструментов

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Сравнение CI/CD инструментов                       │
├─────────────────┬─────────────────┬─────────────────┬───────────────┤
│                 │  Xcode Cloud    │    Fastlane     │ GitHub Actions│
├─────────────────┼─────────────────┼─────────────────┼───────────────┤
│ Владелец        │ Apple           │ Google (OSS)    │ Microsoft     │
│ Сложность       │ Низкая          │ Средняя         │ Средняя       │
│ Гибкость        │ Ограниченная    │ Высокая         │ Очень высокая │
│ macOS runners   │ Включены        │ Нужны свои      │ Платные       │
│ Code Signing    │ Автоматически   │ match           │ Вручную/match │
│ App Store       │ Интегрировано   │ deliver/pilot   │ Через Fastlane│
│ Бесплатно       │ 25 часов/месяц  │ Да (OSS)        │ 2000 мин/мес  │
│ Self-hosted     │ Нет             │ Да              │ Да            │
│ Кастомизация    │ ci_scripts/     │ Fastfile        │ YAML workflows│
│ Документация    │ Apple Docs      │ Отличная        │ Отличная      │
└─────────────────┴─────────────────┴─────────────────┴───────────────┘
```

### Когда что использовать

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Выбор инструмента                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Xcode Cloud подходит если:                                        │
│  ✓ Простой проект без сложных зависимостей                         │
│  ✓ Команда новичков в CI/CD                                        │
│  ✓ Достаточно 25 часов бесплатных                                  │
│  ✓ Нужна интеграция с App Store "из коробки"                       │
│                                                                     │
│  Fastlane + свой CI подходит если:                                 │
│  ✓ Сложные workflows                                                │
│  ✓ Несколько приложений/targets                                    │
│  ✓ Нужна кастомизация каждого шага                                 │
│  ✓ Есть свои macOS машины                                          │
│                                                                     │
│  GitHub Actions подходит если:                                      │
│  ✓ Код уже на GitHub                                               │
│  ✓ Мультиплатформенные проекты (iOS + Android + Web)               │
│  ✓ Нужны кастомные workflows                                       │
│  ✓ Есть бюджет на macOS runners                                    │
│                                                                     │
│  Комбинация (Fastlane + GitHub Actions) подходит если:             │
│  ✓ Нужна максимальная гибкость                                     │
│  ✓ Хотите переносимость между CI системами                         │
│  ✓ Сложное управление сертификатами                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Xcode Cloud

### Обзор и настройка

Xcode Cloud - это CI/CD сервис от Apple, интегрированный в Xcode и App Store Connect.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Xcode Cloud Architecture                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────┐         ┌────────────────────────────────────┐ │
│  │    Xcode       │         │         Apple Cloud                │ │
│  │  (IDE)         │◀───────▶│                                    │ │
│  │                │         │  ┌──────────────────────────────┐ │ │
│  │  • Configure   │         │  │     Xcode Cloud Runners      │ │ │
│  │  • View builds │         │  │                              │ │ │
│  │  • Manage      │         │  │  • Apple Silicon (M1/M2)     │ │ │
│  │                │         │  │  • Latest macOS & Xcode      │ │ │
│  └────────────────┘         │  │  • Isolated environments     │ │ │
│                             │  │                              │ │ │
│  ┌────────────────┐         │  └──────────────────────────────┘ │ │
│  │  App Store     │         │                                    │ │
│  │  Connect       │◀───────▶│  ┌──────────────────────────────┐ │ │
│  │                │         │  │     Auto Code Signing        │ │ │
│  │  • Workflows   │         │  │                              │ │ │
│  │  • Builds      │         │  │  • Managed certificates      │ │ │
│  │  • TestFlight  │         │  │  • Managed profiles          │ │ │
│  │                │         │  │  • No manual export          │ │ │
│  └────────────────┘         │  │                              │ │ │
│                             │  └──────────────────────────────┘ │ │
│  ┌────────────────┐         │                                    │ │
│  │  Git Provider  │         │                                    │ │
│  │                │────────▶│                                    │ │
│  │  • GitHub      │         │                                    │ │
│  │  • GitLab      │         │                                    │ │
│  │  • Bitbucket   │         │                                    │ │
│  └────────────────┘         └────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Структура Workflow

```yaml
# Xcode Cloud Workflow определяется в UI или xcode-cloud.yml
# Основные компоненты:

# 1. Start Conditions (когда запускать)
# ┌─────────────────────────────────────────────────┐
# │ • Push to branch (main, develop, feature/*)    │
# │ • Pull Request (opened, updated)               │
# │ • Tag (release/*, v*)                          │
# │ • Manual start                                 │
# │ • Schedule (cron-like)                         │
# └─────────────────────────────────────────────────┘

# 2. Environment (где запускать)
# ┌─────────────────────────────────────────────────┐
# │ • macOS version (latest, 14, 13)               │
# │ • Xcode version (latest, 15.0, 14.3)           │
# │ • Environment variables                        │
# └─────────────────────────────────────────────────┘

# 3. Actions (что делать)
# ┌─────────────────────────────────────────────────┐
# │ • Build (scheme, configuration)                │
# │ • Test (scheme, device, OS version)            │
# │ • Analyze                                      │
# │ • Archive                                      │
# └─────────────────────────────────────────────────┘

# 4. Post-Actions (после сборки)
# ┌─────────────────────────────────────────────────┐
# │ • TestFlight Internal Testing                  │
# │ • TestFlight External Testing                  │
# │ • App Store submission                         │
# │ • Notify (Slack webhook)                       │
# └─────────────────────────────────────────────────┘
```

### Custom Scripts (ci_scripts/)

Xcode Cloud поддерживает пользовательские скрипты в папке `ci_scripts/`:

```bash
# ci_scripts/ci_post_clone.sh
# Выполняется после клонирования репозитория

#!/bin/sh

set -e

echo "=== Post Clone Script ==="

# Установка зависимостей
if [ -f "Gemfile" ]; then
    echo "Installing Ruby dependencies..."
    bundle install
fi

# CocoaPods
if [ -f "Podfile" ]; then
    echo "Installing CocoaPods dependencies..."
    pod install
fi

# Homebrew зависимости
if command -v brew &> /dev/null; then
    echo "Installing Homebrew packages..."
    brew install swiftlint
fi

# SwiftGen (если используется)
if [ -f "swiftgen.yml" ]; then
    echo "Running SwiftGen..."
    swiftgen
fi

echo "=== Post Clone Complete ==="
```

```bash
# ci_scripts/ci_pre_xcodebuild.sh
# Выполняется перед сборкой

#!/bin/sh

set -e

echo "=== Pre Build Script ==="

# Установка версии из CI
if [ -n "$CI_BUILD_NUMBER" ]; then
    echo "Setting build number to $CI_BUILD_NUMBER"

    # Обновление Info.plist через PlistBuddy
    /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $CI_BUILD_NUMBER" \
        "$CI_PRIMARY_REPOSITORY_PATH/MyApp/Info.plist"
fi

# Настройка окружения
if [ "$CI_WORKFLOW" = "Production" ]; then
    echo "Configuring for Production..."
    cp Config/Production.xcconfig Config/Active.xcconfig
else
    echo "Configuring for Development..."
    cp Config/Development.xcconfig Config/Active.xcconfig
fi

# Проверка секретов
if [ -z "$API_KEY" ]; then
    echo "Error: API_KEY not set"
    exit 1
fi

echo "=== Pre Build Complete ==="
```

```bash
# ci_scripts/ci_post_xcodebuild.sh
# Выполняется после сборки

#!/bin/sh

set -e

echo "=== Post Build Script ==="

# Отправка уведомления в Slack
if [ "$CI_XCODEBUILD_EXIT_CODE" -eq 0 ]; then
    STATUS="success"
    COLOR="good"
else
    STATUS="failed"
    COLOR="danger"
fi

if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"attachments\": [{
                \"color\": \"$COLOR\",
                \"title\": \"Build $STATUS: $CI_PRODUCT\",
                \"text\": \"Workflow: $CI_WORKFLOW\\nBranch: $CI_BRANCH\\nCommit: $CI_COMMIT\",
                \"footer\": \"Xcode Cloud\"
            }]
        }" \
        "$SLACK_WEBHOOK_URL"
fi

# Загрузка dSYM в Crashlytics (если нужно)
if [ "$STATUS" = "success" ] && [ -n "$FIREBASE_APP_ID" ]; then
    echo "Uploading dSYMs to Firebase..."
    # Firebase CLI upload
fi

echo "=== Post Build Complete ==="
```

### Environment Variables

```
┌─────────────────────────────────────────────────────────────────────┐
│              Xcode Cloud Environment Variables                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Предустановленные переменные:                                      │
│  ├── CI                           = true                            │
│  ├── CI_XCODE_CLOUD               = true                            │
│  ├── CI_BUILD_NUMBER              = 42                              │
│  ├── CI_BUILD_ID                  = abc123                          │
│  ├── CI_WORKFLOW                  = "Release"                       │
│  ├── CI_BRANCH                    = "main"                          │
│  ├── CI_TAG                       = "v1.2.3" (если есть)            │
│  ├── CI_COMMIT                    = "a1b2c3d4..."                   │
│  ├── CI_PULL_REQUEST_NUMBER       = 123 (если PR)                   │
│  ├── CI_PRODUCT                   = "MyApp"                         │
│  ├── CI_PRIMARY_REPOSITORY_PATH   = /Volumes/workspace/...          │
│  ├── CI_DERIVED_DATA_PATH         = /Volumes/...                    │
│  ├── CI_ARCHIVE_PATH              = /Volumes/... (после archive)    │
│  └── CI_XCODEBUILD_EXIT_CODE      = 0 (в post-actions)              │
│                                                                     │
│  Пользовательские переменные (в App Store Connect):                │
│  ├── API_KEY                      = "secret" (секрет)               │
│  ├── SLACK_WEBHOOK_URL            = "https://..." (секрет)          │
│  └── ENVIRONMENT                  = "production"                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Цены и лимиты

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Xcode Cloud Pricing (2026)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  План                    │ Часы/месяц │ Цена                       │
│  ────────────────────────┼────────────┼──────────────────────────── │
│  Included with Program   │ 25         │ $0 (входит в $99/год)      │
│  Small Team              │ 100        │ $14.99/мес                  │
│  Medium Team             │ 250        │ $29.99/мес                  │
│  Large Team              │ 500        │ $49.99/мес                  │
│  Enterprise              │ 1000       │ $99.99/мес                  │
│                                                                     │
│  Лимиты:                                                            │
│  • Максимум 10 concurrent builds                                    │
│  • Artifacts хранятся 30 дней                                       │
│  • Logs хранятся 90 дней                                            │
│  • Поддержка public и private репозиториев                          │
│                                                                     │
│  25 часов в месяц это примерно:                                     │
│  • 50 builds по 30 минут                                            │
│  • 150 builds по 10 минут                                           │
│  • Достаточно для маленькой команды с 1-2 релизами в месяц         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Fastlane

### Обзор инструментов

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Fastlane Tool Suite                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Certificate Management                    │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │   │
│  │  │  match  │  │  cert   │  │  sigh   │                     │   │
│  │  │ ─────── │  │ ─────── │  │ ─────── │                     │   │
│  │  │ Sync    │  │ Create  │  │ Create  │                     │   │
│  │  │ certs & │  │ dev/prod│  │provision│                     │   │
│  │  │profiles │  │ certs   │  │profiles │                     │   │
│  │  └─────────┘  └─────────┘  └─────────┘                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Building & Testing                        │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │   │
│  │  │   gym   │  │  scan   │  │snapshot │                     │   │
│  │  │ ─────── │  │ ─────── │  │ ─────── │                     │   │
│  │  │ Build   │  │ Run     │  │ Take UI │                     │   │
│  │  │ IPA/APP │  │ tests   │  │ screen- │                     │   │
│  │  │         │  │         │  │ shots   │                     │   │
│  │  └─────────┘  └─────────┘  └─────────┘                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Distribution                              │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │   │
│  │  │  pilot  │  │ deliver │  │  supply │                     │   │
│  │  │ ─────── │  │ ─────── │  │ ─────── │                     │   │
│  │  │TestFlight  │ App     │  │ Google  │                     │   │
│  │  │ upload  │  │ Store   │  │ Play    │                     │   │
│  │  │& manage │  │ upload  │  │ (Android)│                    │   │
│  │  └─────────┘  └─────────┘  └─────────┘                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Структура проекта Fastlane

```
my-ios-app/
├── Gemfile                    # Ruby зависимости
├── Gemfile.lock
└── fastlane/
    ├── Appfile                # App идентификаторы
    ├── Fastfile               # Lane definitions
    ├── Matchfile              # match конфигурация
    ├── Gymfile                # gym конфигурация
    ├── Scanfile               # scan конфигурация
    ├── Deliverfile            # deliver конфигурация
    ├── Pluginfile             # Fastlane plugins
    ├── .env                   # Environment variables (НЕ коммитить!)
    ├── .env.default           # Default environment
    ├── metadata/              # App Store metadata
    │   ├── en-US/
    │   │   ├── description.txt
    │   │   ├── keywords.txt
    │   │   └── release_notes.txt
    │   └── ru/
    │       ├── description.txt
    │       ├── keywords.txt
    │       └── release_notes.txt
    └── screenshots/           # App Store screenshots
        ├── en-US/
        └── ru/
```

### Gemfile

```ruby
# Gemfile

source "https://rubygems.org"

# Указываем версию Ruby
ruby ">= 3.0"

# Fastlane
gem "fastlane", "~> 2.225"

# Plugins
plugins_path = File.join(File.dirname(__FILE__), 'fastlane', 'Pluginfile')
eval_gemfile(plugins_path) if File.exist?(plugins_path)
```

```ruby
# fastlane/Pluginfile

# Firebase distribution
gem 'fastlane-plugin-firebase_app_distribution'

# Versioning
gem 'fastlane-plugin-versioning'

# Badge для иконок
gem 'fastlane-plugin-badge'
```

### Appfile

```ruby
# fastlane/Appfile

# App Store Connect credentials
app_identifier("com.mycompany.myapp")
apple_id("developer@mycompany.com")
itc_team_id("123456789")  # App Store Connect Team ID
team_id("ABCD1234EF")     # Apple Developer Portal Team ID

# Можно использовать environment-specific настройки
for_platform :ios do
  for_lane :beta do
    app_identifier("com.mycompany.myapp.beta")
  end

  for_lane :release do
    app_identifier("com.mycompany.myapp")
  end
end
```

### Fastfile - основной файл

```ruby
# fastlane/Fastfile

# Минимальная версия Fastlane
fastlane_version "2.225.0"

# Платформа по умолчанию
default_platform(:ios)

# Переменные
APP_IDENTIFIER = ENV["APP_IDENTIFIER"] || "com.mycompany.myapp"
SCHEME = ENV["SCHEME"] || "MyApp"
PROJECT = "MyApp.xcodeproj"
WORKSPACE = "MyApp.xcworkspace"

platform :ios do

  # =====================================
  # SETUP & PREPARATION
  # =====================================

  desc "Подготовка окружения"
  lane :setup do
    # Установка зависимостей
    cocoapods(
      clean_install: true,
      podfile: "./Podfile"
    )

    # Или SPM
    # sh("xcodebuild -resolvePackageDependencies")
  end

  desc "Синхронизация сертификатов через match"
  lane :sync_certificates do |options|
    type = options[:type] || "development"
    readonly = options[:readonly] || true

    match(
      type: type,
      readonly: readonly,
      app_identifier: APP_IDENTIFIER,
      git_url: ENV["MATCH_GIT_URL"],
      git_branch: "main"
    )
  end

  # =====================================
  # TESTING
  # =====================================

  desc "Запуск всех тестов"
  lane :test do
    scan(
      workspace: WORKSPACE,
      scheme: SCHEME,
      devices: ["iPhone 15 Pro"],
      clean: true,
      code_coverage: true,
      output_directory: "./fastlane/test_output",
      output_types: "html,junit"
    )
  end

  desc "Запуск unit тестов"
  lane :unit_test do
    scan(
      workspace: WORKSPACE,
      scheme: "#{SCHEME}UnitTests",
      devices: ["iPhone 15 Pro"],
      only_testing: ["MyAppUnitTests"]
    )
  end

  desc "Запуск UI тестов"
  lane :ui_test do
    scan(
      workspace: WORKSPACE,
      scheme: "#{SCHEME}UITests",
      devices: ["iPhone 15 Pro", "iPad Pro (12.9-inch)"],
      only_testing: ["MyAppUITests"]
    )
  end

  # =====================================
  # BUILDING
  # =====================================

  desc "Сборка для Development"
  lane :build_dev do
    sync_certificates(type: "development")

    gym(
      workspace: WORKSPACE,
      scheme: SCHEME,
      configuration: "Debug",
      export_method: "development",
      output_directory: "./build",
      output_name: "MyApp-Dev.ipa",
      clean: true
    )
  end

  desc "Сборка для AdHoc"
  lane :build_adhoc do
    sync_certificates(type: "adhoc")

    # Инкремент build number
    increment_build_number(
      build_number: ENV["BUILD_NUMBER"] || Time.now.strftime("%Y%m%d%H%M")
    )

    gym(
      workspace: WORKSPACE,
      scheme: SCHEME,
      configuration: "Release",
      export_method: "ad-hoc",
      output_directory: "./build",
      output_name: "MyApp-AdHoc.ipa",
      include_bitcode: false,
      include_symbols: true
    )
  end

  desc "Сборка для App Store"
  lane :build_release do
    sync_certificates(type: "appstore")

    # Получение версии
    version = get_version_number(
      xcodeproj: PROJECT,
      target: SCHEME
    )

    # Инкремент build number
    increment_build_number(
      build_number: latest_testflight_build_number + 1
    )

    build_number = get_build_number(xcodeproj: PROJECT)

    gym(
      workspace: WORKSPACE,
      scheme: SCHEME,
      configuration: "Release",
      export_method: "app-store",
      output_directory: "./build",
      output_name: "MyApp-#{version}-#{build_number}.ipa",
      include_bitcode: false,
      include_symbols: true,
      export_options: {
        provisioningProfiles: {
          APP_IDENTIFIER => "match AppStore #{APP_IDENTIFIER}"
        }
      }
    )
  end

  # =====================================
  # DISTRIBUTION
  # =====================================

  desc "Загрузка в TestFlight"
  lane :beta do
    # Сначала собираем
    build_release

    # Загружаем в TestFlight
    pilot(
      ipa: "./build/MyApp-#{get_version_number}-#{get_build_number}.ipa",
      skip_waiting_for_build_processing: true,
      distribute_external: false,
      notify_external_testers: false,
      changelog: last_git_commit[:message]
    )

    # Уведомление в Slack
    slack(
      message: "New build uploaded to TestFlight! :rocket:",
      slack_url: ENV["SLACK_WEBHOOK_URL"],
      payload: {
        "Version" => get_version_number,
        "Build" => get_build_number,
        "Git Commit" => last_git_commit[:abbreviated_commit_hash]
      }
    )
  end

  desc "Полный релиз в App Store"
  lane :release do
    # Проверки перед релизом
    ensure_git_status_clean
    ensure_git_branch(branch: "main")

    # Сборка
    build_release

    # Загрузка метаданных и скриншотов
    deliver(
      ipa: lane_context[SharedValues::IPA_OUTPUT_PATH],
      submit_for_review: false,
      automatic_release: false,
      force: true,  # Пропустить HTML report
      metadata_path: "./fastlane/metadata",
      screenshots_path: "./fastlane/screenshots",
      skip_screenshots: false,
      precheck_include_in_app_purchases: false
    )

    # Создание git tag
    version = get_version_number
    build = get_build_number
    add_git_tag(tag: "v#{version}-#{build}")
    push_git_tags

    # Уведомление
    slack(
      message: "App submitted to App Store! :apple:",
      slack_url: ENV["SLACK_WEBHOOK_URL"]
    )
  end

  # =====================================
  # FIREBASE DISTRIBUTION
  # =====================================

  desc "Загрузка в Firebase App Distribution"
  lane :firebase do
    build_adhoc

    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID"],
      ipa_path: "./build/MyApp-AdHoc.ipa",
      groups: "internal-testers",
      release_notes: last_git_commit[:message],
      firebase_cli_token: ENV["FIREBASE_CLI_TOKEN"]
    )
  end

  # =====================================
  # UTILITY LANES
  # =====================================

  desc "Инкремент версии"
  lane :bump do |options|
    type = options[:type] || "patch"  # major, minor, patch

    increment_version_number(
      bump_type: type
    )

    commit_version_bump(
      message: "Bump version to #{get_version_number}",
      xcodeproj: PROJECT
    )
  end

  desc "Регистрация нового устройства"
  lane :register_device do |options|
    device_name = options[:name]
    device_udid = options[:udid]

    register_devices(
      devices: {
        device_name => device_udid
      }
    )

    # Обновляем provisioning profiles
    match(type: "development", force_for_new_devices: true)
    match(type: "adhoc", force_for_new_devices: true)
  end

  desc "Создание скриншотов"
  lane :screenshots do
    capture_screenshots(
      workspace: WORKSPACE,
      scheme: "#{SCHEME}UITests",
      devices: [
        "iPhone 15 Pro Max",
        "iPhone 15 Pro",
        "iPhone SE (3rd generation)",
        "iPad Pro (12.9-inch) (6th generation)"
      ],
      languages: ["en-US", "ru"],
      output_directory: "./fastlane/screenshots",
      clear_previous_screenshots: true
    )

    # Добавление рамок устройств
    frame_screenshots(
      path: "./fastlane/screenshots"
    )
  end

  # =====================================
  # ERROR HANDLING
  # =====================================

  error do |lane, exception, options|
    slack(
      message: "Lane #{lane} failed with error: #{exception.message}",
      slack_url: ENV["SLACK_WEBHOOK_URL"],
      success: false
    )
  end

end
```

### Matchfile

```ruby
# fastlane/Matchfile

# Git репозиторий для хранения сертификатов
git_url(ENV["MATCH_GIT_URL"])
git_branch("main")

# Storage mode
storage_mode("git")  # или "s3", "google_cloud"

# App identifier(s)
app_identifier([
  "com.mycompany.myapp",
  "com.mycompany.myapp.beta",
  "com.mycompany.myapp.widget"
])

# Apple Developer credentials
username(ENV["APPLE_ID"])
team_id(ENV["TEAM_ID"])

# Типы сертификатов
type("development")  # development, adhoc, appstore, enterprise

# Keychain
keychain_name("fastlane_keychain")
keychain_password(ENV["MATCH_KEYCHAIN_PASSWORD"])

# Опции
readonly(true)  # Не создавать новые сертификаты
verbose(true)
force_for_new_devices(false)

# Для CI
clone_branch_directly(true)  # Быстрее клонирование
shallow_clone(true)
```

### Gymfile

```ruby
# fastlane/Gymfile

# Workspace и scheme
workspace("MyApp.xcworkspace")
scheme("MyApp")

# Конфигурация сборки
configuration("Release")

# Метод экспорта
export_method("app-store")  # app-store, ad-hoc, enterprise, development

# Output
output_directory("./build")
output_name("MyApp")

# Archive
archive_path("./build/MyApp.xcarchive")

# Опции
clean(true)
silent(false)

# Export options
include_bitcode(false)
include_symbols(true)

# Для ускорения
skip_package_ipa(false)
skip_archive(false)

# Code signing (если не используется match)
# export_options({
#   provisioningProfiles: {
#     "com.mycompany.myapp" => "MyApp AppStore Profile"
#   }
# })
```

## GitHub Actions для iOS

### Базовый workflow

```yaml
# .github/workflows/ios-ci.yml

name: iOS CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:  # Manual trigger

env:
  SCHEME: "MyApp"
  WORKSPACE: "MyApp.xcworkspace"
  DEVELOPER_DIR: /Applications/Xcode_15.0.app/Contents/Developer

jobs:
  # =====================================
  # BUILD & TEST
  # =====================================
  build-and-test:
    name: Build and Test
    runs-on: macos-14  # macOS Sonoma with M1
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for versioning

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.0.app

      - name: Show Xcode version
        run: xcodebuild -version

      # SPM Cache
      - name: Cache SPM
        uses: actions/cache@v4
        with:
          path: |
            ~/Library/Caches/org.swift.swiftpm
            .build
          key: ${{ runner.os }}-spm-${{ hashFiles('**/Package.resolved') }}
          restore-keys: |
            ${{ runner.os }}-spm-

      # DerivedData Cache
      - name: Cache DerivedData
        uses: actions/cache@v4
        with:
          path: ~/Library/Developer/Xcode/DerivedData
          key: ${{ runner.os }}-derived-data-${{ hashFiles('**/*.xcodeproj/project.pbxproj') }}
          restore-keys: |
            ${{ runner.os }}-derived-data-

      # CocoaPods (если используется)
      - name: Cache CocoaPods
        uses: actions/cache@v4
        with:
          path: Pods
          key: ${{ runner.os }}-pods-${{ hashFiles('**/Podfile.lock') }}
          restore-keys: |
            ${{ runner.os }}-pods-

      - name: Install CocoaPods
        if: hashFiles('Podfile.lock') != ''
        run: |
          gem install cocoapods
          pod install --repo-update

      # Resolve SPM dependencies
      - name: Resolve SPM Dependencies
        run: |
          xcodebuild -resolvePackageDependencies \
            -workspace "${{ env.WORKSPACE }}" \
            -scheme "${{ env.SCHEME }}"

      # Build
      - name: Build for Testing
        run: |
          xcodebuild build-for-testing \
            -workspace "${{ env.WORKSPACE }}" \
            -scheme "${{ env.SCHEME }}" \
            -destination "platform=iOS Simulator,name=iPhone 15 Pro" \
            -configuration Debug \
            CODE_SIGNING_ALLOWED=NO \
            | xcpretty

      # Test
      - name: Run Tests
        run: |
          xcodebuild test-without-building \
            -workspace "${{ env.WORKSPACE }}" \
            -scheme "${{ env.SCHEME }}" \
            -destination "platform=iOS Simulator,name=iPhone 15 Pro" \
            -resultBundlePath TestResults.xcresult \
            | xcpretty

      # Upload test results
      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: TestResults.xcresult
          retention-days: 7

  # =====================================
  # LINT & ANALYZE
  # =====================================
  lint:
    name: SwiftLint
    runs-on: macos-14
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Install SwiftLint
        run: brew install swiftlint

      - name: Run SwiftLint
        run: swiftlint lint --reporter github-actions-logging

  # =====================================
  # BETA RELEASE
  # =====================================
  beta:
    name: TestFlight Beta
    needs: [build-and-test, lint]
    runs-on: macos-14
    timeout-minutes: 45
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.0.app

      # Ruby & Fastlane
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      # Install certificates via match
      - name: Install Certificates
        env:
          MATCH_GIT_URL: ${{ secrets.MATCH_GIT_URL }}
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_BASIC_AUTHORIZATION }}
          FASTLANE_USER: ${{ secrets.APPLE_ID }}
          FASTLANE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
        run: |
          bundle exec fastlane sync_certificates type:appstore readonly:true

      # Build and upload
      - name: Build and Upload to TestFlight
        env:
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          APP_STORE_CONNECT_API_KEY_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY_CONTENT: ${{ secrets.ASC_API_KEY }}
        run: |
          bundle exec fastlane beta

      # Notify
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          fields: repo,message,commit,author,action,eventName,ref,workflow
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Workflow с ручным code signing

```yaml
# .github/workflows/ios-release.yml

name: iOS Release

on:
  push:
    tags:
      - 'v*'  # v1.0.0, v2.1.3, etc.

env:
  SCHEME: "MyApp"
  WORKSPACE: "MyApp.xcworkspace"

jobs:
  release:
    name: Build and Release
    runs-on: macos-14
    timeout-minutes: 60

    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.0.app

      # =====================================
      # CERTIFICATE SETUP (Manual approach)
      # =====================================

      - name: Install Apple Certificate
        env:
          CERTIFICATE_P12: ${{ secrets.DISTRIBUTION_CERTIFICATE_P12 }}
          CERTIFICATE_PASSWORD: ${{ secrets.DISTRIBUTION_CERTIFICATE_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: |
          # Создаём временную директорию
          CERTIFICATE_PATH=$RUNNER_TEMP/certificate.p12
          KEYCHAIN_PATH=$RUNNER_TEMP/app-signing.keychain-db

          # Декодируем сертификат из base64
          echo -n "$CERTIFICATE_P12" | base64 --decode -o $CERTIFICATE_PATH

          # Создаём новый keychain
          security create-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          security set-keychain-settings -lut 21600 $KEYCHAIN_PATH
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH

          # Импортируем сертификат
          security import $CERTIFICATE_PATH \
            -P "$CERTIFICATE_PASSWORD" \
            -A \
            -t cert \
            -f pkcs12 \
            -k $KEYCHAIN_PATH

          # Разрешаем codesign использовать keychain
          security set-key-partition-list \
            -S apple-tool:,apple:,codesign: \
            -s \
            -k "$KEYCHAIN_PASSWORD" \
            $KEYCHAIN_PATH

          # Добавляем keychain в search list
          security list-keychain -d user -s $KEYCHAIN_PATH

      - name: Install Provisioning Profile
        env:
          PROVISIONING_PROFILE: ${{ secrets.APPSTORE_PROVISIONING_PROFILE }}
        run: |
          # Создаём директорию для profiles
          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles

          # Декодируем и устанавливаем profile
          PROFILE_PATH=~/Library/MobileDevice/Provisioning\ Profiles/profile.mobileprovision
          echo -n "$PROVISIONING_PROFILE" | base64 --decode -o "$PROFILE_PATH"

          # Показываем информацию о profile
          security cms -D -i "$PROFILE_PATH" | grep -A1 "Name"

      # =====================================
      # BUILD
      # =====================================

      - name: Get Version from Tag
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Building version: $VERSION"

      - name: Set Build Number
        run: |
          BUILD_NUMBER=${{ github.run_number }}
          agvtool new-version -all $BUILD_NUMBER
          echo "Build number: $BUILD_NUMBER"

      - name: Install Dependencies
        run: |
          gem install cocoapods
          pod install --repo-update

      - name: Build Archive
        run: |
          xcodebuild archive \
            -workspace "${{ env.WORKSPACE }}" \
            -scheme "${{ env.SCHEME }}" \
            -configuration Release \
            -archivePath $RUNNER_TEMP/MyApp.xcarchive \
            -destination "generic/platform=iOS" \
            CODE_SIGN_IDENTITY="Apple Distribution" \
            PROVISIONING_PROFILE_SPECIFIER="MyApp AppStore Profile"

      - name: Export IPA
        run: |
          # Создаём ExportOptions.plist
          cat > $RUNNER_TEMP/ExportOptions.plist << EOF
          <?xml version="1.0" encoding="UTF-8"?>
          <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
          <plist version="1.0">
          <dict>
              <key>method</key>
              <string>app-store</string>
              <key>destination</key>
              <string>upload</string>
              <key>signingStyle</key>
              <string>manual</string>
              <key>provisioningProfiles</key>
              <dict>
                  <key>com.mycompany.myapp</key>
                  <string>MyApp AppStore Profile</string>
              </dict>
          </dict>
          </plist>
          EOF

          xcodebuild -exportArchive \
            -archivePath $RUNNER_TEMP/MyApp.xcarchive \
            -exportPath $RUNNER_TEMP/export \
            -exportOptionsPlist $RUNNER_TEMP/ExportOptions.plist

      # =====================================
      # UPLOAD TO APP STORE CONNECT
      # =====================================

      - name: Upload to App Store Connect
        env:
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          APP_STORE_CONNECT_API_KEY_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY_CONTENT: ${{ secrets.ASC_API_KEY }}
        run: |
          # Создаём API key file
          mkdir -p ~/.appstoreconnect/private_keys
          echo "$APP_STORE_CONNECT_API_KEY_CONTENT" > ~/.appstoreconnect/private_keys/AuthKey_${{ secrets.ASC_KEY_ID }}.p8

          # Загружаем через xcrun altool
          xcrun altool --upload-app \
            --type ios \
            --file "$RUNNER_TEMP/export/MyApp.ipa" \
            --apiKey "${{ secrets.ASC_KEY_ID }}" \
            --apiIssuer "${{ secrets.ASC_ISSUER_ID }}"

      # =====================================
      # CLEANUP
      # =====================================

      - name: Cleanup Keychain
        if: always()
        run: |
          security delete-keychain $RUNNER_TEMP/app-signing.keychain-db || true

      # =====================================
      # CREATE GITHUB RELEASE
      # =====================================

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          name: Release ${{ steps.version.outputs.version }}
          body: |
            ## What's Changed
            - See commit history for details

            ## Installation
            - Download from TestFlight (coming soon)
            - Or from App Store after review
          draft: false
          prerelease: false
          files: |
            $RUNNER_TEMP/export/MyApp.ipa
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Secrets management

```
┌─────────────────────────────────────────────────────────────────────┐
│              GitHub Secrets для iOS CI/CD                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Сертификаты и Signing:                                             │
│  ├── DISTRIBUTION_CERTIFICATE_P12   # base64 encoded .p12          │
│  ├── DISTRIBUTION_CERTIFICATE_PASSWORD                              │
│  ├── APPSTORE_PROVISIONING_PROFILE  # base64 encoded .mobileprovision│
│  └── KEYCHAIN_PASSWORD              # Пароль для временного keychain │
│                                                                     │
│  Match (Fastlane):                                                  │
│  ├── MATCH_GIT_URL                  # URL git репо с сертификатами  │
│  ├── MATCH_PASSWORD                 # Пароль шифрования             │
│  └── MATCH_GIT_BASIC_AUTHORIZATION  # base64(username:token)       │
│                                                                     │
│  Apple Developer:                                                   │
│  ├── APPLE_ID                       # Apple ID email                │
│  ├── APPLE_PASSWORD                 # Пароль Apple ID              │
│  ├── APPLE_APP_SPECIFIC_PASSWORD    # Для 2FA                      │
│  └── TEAM_ID                        # Developer Team ID            │
│                                                                     │
│  App Store Connect API:                                             │
│  ├── ASC_KEY_ID                     # API Key ID                   │
│  ├── ASC_ISSUER_ID                  # Issuer ID                    │
│  └── ASC_API_KEY                    # Private key (.p8 content)    │
│                                                                     │
│  Notifications:                                                     │
│  └── SLACK_WEBHOOK_URL              # Slack incoming webhook       │
│                                                                     │
│  Firebase:                                                          │
│  ├── FIREBASE_APP_ID                # Firebase App ID              │
│  └── FIREBASE_CLI_TOKEN             # firebase login:ci token      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Подготовка secrets

```bash
# Кодирование сертификата в base64
base64 -i Certificates.p12 -o certificate_base64.txt

# Кодирование provisioning profile
base64 -i MyApp_AppStore.mobileprovision -o profile_base64.txt

# Создание MATCH_GIT_BASIC_AUTHORIZATION
echo -n "username:personal_access_token" | base64

# Получение App Store Connect API Key
# 1. App Store Connect → Users and Access → Keys
# 2. Generate new key (Admin role)
# 3. Download .p8 file
# 4. Copy Key ID and Issuer ID
```

## Управление сертификатами в CI

### Match подход (рекомендуется)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Match: Централизованное хранение                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │            Git Repository (encrypted)                         │  │
│  │                                                               │  │
│  │  certificates/                                                │  │
│  │  ├── development/                                             │  │
│  │  │   ├── ABCD1234EF.cer (encrypted)                          │  │
│  │  │   └── ABCD1234EF.p12 (encrypted)                          │  │
│  │  ├── distribution/                                            │  │
│  │  │   ├── ABCD1234EF.cer                                      │  │
│  │  │   └── ABCD1234EF.p12                                      │  │
│  │  └── enterprise/                                              │  │
│  │                                                               │  │
│  │  profiles/                                                    │  │
│  │  ├── development/                                             │  │
│  │  │   └── Development_com.mycompany.myapp.mobileprovision     │  │
│  │  ├── adhoc/                                                   │  │
│  │  │   └── AdHoc_com.mycompany.myapp.mobileprovision           │  │
│  │  └── appstore/                                                │  │
│  │      └── AppStore_com.mycompany.myapp.mobileprovision        │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              │ MATCH_PASSWORD                       │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    CI Server / Developer Machine              │  │
│  │                                                               │  │
│  │  1. git clone (certificates repo)                            │  │
│  │  2. decrypt with MATCH_PASSWORD                              │  │
│  │  3. install to Keychain                                      │  │
│  │  4. install profiles to ~/Library/MobileDevice/...           │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

```ruby
# Инициализация match (один раз)
# fastlane match init

# Создание сертификатов (один раз, команда делает один человек)
# fastlane match development
# fastlane match adhoc
# fastlane match appstore

# Использование в CI (readonly)
lane :setup_signing do
  # Создаём временный keychain
  create_keychain(
    name: "fastlane_keychain",
    password: ENV["MATCH_KEYCHAIN_PASSWORD"],
    default_keychain: true,
    unlock: true,
    timeout: 3600,
    lock_when_sleeps: false
  )

  # Синхронизируем сертификаты
  match(
    type: "appstore",
    readonly: true,  # Важно для CI!
    keychain_name: "fastlane_keychain",
    keychain_password: ENV["MATCH_KEYCHAIN_PASSWORD"],
    git_url: ENV["MATCH_GIT_URL"],
    git_basic_authorization: ENV["MATCH_GIT_BASIC_AUTHORIZATION"]
  )
end
```

### Ручной подход (если match не подходит)

```bash
#!/bin/bash
# scripts/setup-signing.sh

set -euo pipefail

# Переменные
CERTIFICATE_PATH="${RUNNER_TEMP}/certificate.p12"
KEYCHAIN_PATH="${RUNNER_TEMP}/build.keychain"
KEYCHAIN_PASSWORD="${KEYCHAIN_PASSWORD:-$(openssl rand -base64 32)}"
PROFILES_DIR="${HOME}/Library/MobileDevice/Provisioning Profiles"

# Функция cleanup
cleanup() {
    echo "Cleaning up..."
    security delete-keychain "$KEYCHAIN_PATH" 2>/dev/null || true
}
trap cleanup EXIT

# 1. Декодируем сертификат
echo "Decoding certificate..."
echo "$CERTIFICATE_P12_BASE64" | base64 --decode > "$CERTIFICATE_PATH"

# 2. Создаём keychain
echo "Creating keychain..."
security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

# 3. Настраиваем keychain
security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

# 4. Импортируем сертификат
echo "Importing certificate..."
security import "$CERTIFICATE_PATH" \
    -P "$CERTIFICATE_PASSWORD" \
    -A \
    -t cert \
    -f pkcs12 \
    -k "$KEYCHAIN_PATH"

# 5. Разрешаем доступ для codesign
security set-key-partition-list \
    -S apple-tool:,apple:,codesign: \
    -s \
    -k "$KEYCHAIN_PASSWORD" \
    "$KEYCHAIN_PATH"

# 6. Добавляем в search list
security list-keychain -d user -s "$KEYCHAIN_PATH" $(security list-keychains -d user | tr -d '"')

# 7. Устанавливаем provisioning profiles
echo "Installing provisioning profiles..."
mkdir -p "$PROFILES_DIR"

for profile_var in PROVISIONING_PROFILE_DEV PROVISIONING_PROFILE_ADHOC PROVISIONING_PROFILE_APPSTORE; do
    profile_content="${!profile_var:-}"
    if [ -n "$profile_content" ]; then
        # Получаем UUID из profile
        profile_path="${RUNNER_TEMP}/temp.mobileprovision"
        echo "$profile_content" | base64 --decode > "$profile_path"

        uuid=$(/usr/libexec/PlistBuddy -c "Print :UUID" /dev/stdin <<< $(security cms -D -i "$profile_path"))

        # Копируем с правильным именем
        cp "$profile_path" "${PROFILES_DIR}/${uuid}.mobileprovision"
        echo "Installed profile: $uuid"
    fi
done

echo "Signing setup complete!"

# 8. Проверяем установку
echo "Verifying setup..."
security find-identity -v -p codesigning "$KEYCHAIN_PATH"
ls -la "$PROFILES_DIR"
```

### Best practices

```
┌─────────────────────────────────────────────────────────────────────┐
│              Best Practices: Сертификаты в CI                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ DO:                                                             │
│  ├── Используйте match для синхронизации                           │
│  ├── Храните сертификаты в отдельном приватном репозитории         │
│  ├── Используйте readonly mode в CI                                │
│  ├── Создавайте временный keychain для CI                          │
│  ├── Удаляйте keychain после сборки (cleanup)                      │
│  ├── Используйте App Store Connect API Key (не пароль)             │
│  ├── Ротируйте секреты регулярно                                   │
│  └── Используйте минимальные права доступа                         │
│                                                                     │
│  ❌ DON'T:                                                          │
│  ├── Не храните сертификаты в основном репозитории                 │
│  ├── Не используйте один сертификат для dev и prod                 │
│  ├── Не хардкодьте пароли в скриптах                               │
│  ├── Не логируйте секреты (echo $PASSWORD)                         │
│  ├── Не используйте default keychain в CI                          │
│  └── Не давайте всей команде доступ к distribution certificate    │
│                                                                     │
│  Разделение ответственности:                                        │
│  ├── Development: все разработчики                                 │
│  ├── AdHoc: тестировщики + разработчики                            │
│  ├── Distribution: только release manager / CI                     │
│  └── Enterprise: только внутренние билды                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Распространённые ошибки

### Ошибка 1: Хардкод signing настроек

```
❌ Неправильно:
```

```ruby
# Fastfile
gym(
  workspace: "MyApp.xcworkspace",
  scheme: "MyApp",
  codesigning_identity: "iPhone Distribution: My Company (ABCD1234)",
  provisioning_profile_path: "/Users/developer/Desktop/MyApp.mobileprovision"
)
```

```
✅ Правильно:
```

```ruby
# Fastfile
gym(
  workspace: "MyApp.xcworkspace",
  scheme: "MyApp",
  export_method: "app-store",
  export_options: {
    provisioningProfiles: {
      ENV["APP_IDENTIFIER"] => "match AppStore #{ENV['APP_IDENTIFIER']}"
    }
  }
)
```

### Ошибка 2: Отсутствие кэширования

```yaml
# ❌ Неправильно: каждый раз скачиваем всё заново
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - run: pod install            # 5-10 минут каждый раз!
      - run: xcodebuild build       # SPM resolve 3-5 минут
```

```yaml
# ✅ Правильно: используем кэширование
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      # CocoaPods cache
      - uses: actions/cache@v4
        with:
          path: |
            Pods
            ~/.cocoapods
          key: ${{ runner.os }}-pods-${{ hashFiles('Podfile.lock') }}

      # SPM cache
      - uses: actions/cache@v4
        with:
          path: |
            ~/Library/Caches/org.swift.swiftpm
            ~/Library/Developer/Xcode/DerivedData/**/SourcePackages
          key: ${{ runner.os }}-spm-${{ hashFiles('*.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved') }}

      # DerivedData cache
      - uses: actions/cache@v4
        with:
          path: ~/Library/Developer/Xcode/DerivedData
          key: ${{ runner.os }}-dd-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-dd-

      - run: pod install --deployment  # Быстрая установка
      - run: xcodebuild build
```

### Ошибка 3: Секреты в логах

```bash
# ❌ Неправильно: секрет виден в логах
echo "Using password: $CERTIFICATE_PASSWORD"
curl -u "user:$API_KEY" https://api.example.com

# Также неправильно: base64 можно декодировать
echo "Certificate: $CERTIFICATE_P12"
```

```bash
# ✅ Правильно: маскируем секреты
echo "Using password: ***"

# В GitHub Actions секреты автоматически маскируются
# Но будьте осторожны с base64!

# Безопасный вывод
echo "Certificate installed successfully"
echo "API Key ID: ${API_KEY_ID:0:4}****"
```

### Ошибка 4: Неправильный provisioning profile

```
❌ Типичные проблемы:
```

```
┌─────────────────────────────────────────────────────────────────────┐
│  Error: Provisioning profile doesn't match bundle identifier       │
│                                                                     │
│  Причины:                                                           │
│  • Bundle ID в Xcode: com.company.app                              │
│  • Bundle ID в profile: com.company.app.beta                       │
│                                                                     │
│  Или:                                                               │
│  • Profile: Development                                             │
│  • Export method: app-store                                        │
│                                                                     │
│  Или:                                                               │
│  • Profile для: Device build                                       │
│  • Build destination: Simulator                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

```
✅ Правильно:
```

```ruby
# Проверяем соответствие
lane :verify_signing do
  # Получаем bundle id из проекта
  bundle_id = get_app_identifier

  # Проверяем что profile существует и валиден
  profile_path = ENV["sigh_#{bundle_id}_appstore_profile-path"]

  if profile_path.nil? || !File.exist?(profile_path)
    UI.user_error!("Profile not found for #{bundle_id}")
  end

  # Проверяем expiration
  profile_info = `security cms -D -i "#{profile_path}"`
  # Parse and check expiration date...
end
```

### Ошибка 5: Simulator вместо Device build

```yaml
# ❌ Неправильно: собираем для симулятора, потом удивляемся
- name: Build
  run: |
    xcodebuild build \
      -workspace MyApp.xcworkspace \
      -scheme MyApp \
      -destination "platform=iOS Simulator,name=iPhone 15"  # Симулятор!

- name: Archive  # Упадёт или создаст невалидный архив
  run: xcodebuild archive ...
```

```yaml
# ✅ Правильно: для release используем generic device
- name: Build for Testing (Simulator OK)
  run: |
    xcodebuild build-for-testing \
      -destination "platform=iOS Simulator,name=iPhone 15"

- name: Archive (Generic Device)
  run: |
    xcodebuild archive \
      -destination "generic/platform=iOS" \  # Generic!
      -archivePath MyApp.xcarchive
```

### Ошибка 6: Timeout issues

```yaml
# ❌ Неправильно: дефолтный timeout слишком маленький
jobs:
  build:
    runs-on: macos-latest
    # Default timeout: 360 minutes, но отдельные шаги могут быть проблемой
    steps:
      - name: Build  # Может занять 30+ минут
        run: xcodebuild build
```

```yaml
# ✅ Правильно: устанавливаем разумные timeouts
jobs:
  build:
    runs-on: macos-latest
    timeout-minutes: 60  # Весь job

    steps:
      - name: Build
        timeout-minutes: 30  # Конкретный шаг
        run: |
          xcodebuild build \
            -workspace MyApp.xcworkspace \
            -scheme MyApp \
            | xcpretty  # Меньше вывода = быстрее

      - name: Test
        timeout-minutes: 20
        run: xcodebuild test ...
```

```ruby
# Fastlane: отключаем лишний вывод
lane :build do
  gym(
    workspace: "MyApp.xcworkspace",
    scheme: "MyApp",
    silent: true,  # Меньше вывода
    suppress_xcode_output: true
  )
end
```

## Ментальные модели

### Модель 1: Pipeline как водопровод

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Pipeline = Водопровод                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Источник         Трубы           Краны           Потребитель       │
│  (Git)           (Stages)       (Approvals)       (Users)          │
│                                                                     │
│  [Репозиторий]                                                      │
│       │                                                             │
│       ▼                                                             │
│  ═══[Build]═══►═══[Test]═══►═══[Sign]═══►═══[Upload]═══            │
│       │              │            │            │                    │
│       │              │            │            ▼                    │
│   Если протечка  Фильтрация   Проверка    [TestFlight]             │
│   (ошибка) -     (тесты       документов       │                   │
│   всё            падают)      (сертификаты)    ▼                   │
│   останавливается                          [App Store]             │
│                                                                     │
│  Принципы:                                                          │
│  • Вода течёт только вперёд (stages последовательны)               │
│  • Протечка на любом этапе останавливает поток                     │
│  • Каждый кран можно открыть/закрыть (manual approval)             │
│  • Давление (скорость) зависит от ширины труб (runners)            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Модель 2: Сертификаты как паспортная система

```
┌─────────────────────────────────────────────────────────────────────┐
│                Сертификаты = Паспортная система                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Certificate (Паспорт разработчика)                                │
│  ┌───────────────────────────────────┐                             │
│  │ Имя: My Company Ltd               │                             │
│  │ ID: ABCD1234EF                    │                             │
│  │ Выдан: Apple (доверенный орган)   │                             │
│  │ Срок: 1 год                       │                             │
│  │ Права: Подписывать код            │                             │
│  └───────────────────────────────────┘                             │
│                                                                     │
│  Provisioning Profile (Виза)                                       │
│  ┌───────────────────────────────────┐                             │
│  │ Тип: Development / Distribution   │ ← Куда можно               │
│  │ App ID: com.mycompany.myapp       │ ← Какое приложение         │
│  │ Devices: iPhone1, iPhone2...      │ ← Какие устройства         │
│  │ Capabilities: Push, HealthKit     │ ← Какие возможности        │
│  │ Certificate: ABCD1234EF           │ ← Привязка к паспорту      │
│  │ Срок: 1 год                       │                             │
│  └───────────────────────────────────┘                             │
│                                                                     │
│  Проверка на границе (iOS Device / App Store):                     │
│  1. Паспорт валиден? (Certificate не истёк, не отозван)           │
│  2. Виза валидна? (Profile не истёк)                               │
│  3. Виза соответствует паспорту? (Certificate в profile)          │
│  4. Цель поездки разрешена? (App ID, Capabilities match)          │
│  5. Устройство в списке? (Devices - для Development/AdHoc)        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Модель 3: CI/CD как производственная линия Toyota

```
┌─────────────────────────────────────────────────────────────────────┐
│               Toyota Production System → CI/CD                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Принцип Toyota          │  CI/CD эквивалент                       │
│  ────────────────────────┼──────────────────────────────────────── │
│  Jidoka (автономизация)  │  Автоматическая остановка при ошибке   │
│  - Машина сама           │  - Тесты падают = pipeline останавлив. │
│    останавливается       │  - Lint errors = merge blocked         │
│                          │                                         │
│  Andon (сигнал)          │  Notifications                         │
│  - Лампочка над станцией │  - Slack уведомления                   │
│  - Все видят проблему    │  - Email alerts                        │
│                          │                                         │
│  Kanban (визуализация)   │  Pipeline visualization                │
│  - Карточки задач        │  - GitHub Actions UI                   │
│  - WIP limits            │  - Xcode Cloud dashboard               │
│                          │                                         │
│  Heijunka (выравнивание) │  Parallel jobs, caching                │
│  - Равномерная загрузка  │  - Распределение по runners            │
│                          │  - Инкрементальные сборки              │
│                          │                                         │
│  Kaizen (улучшение)      │  Metrics & optimization                │
│  - Постоянное улучшение  │  - Build time tracking                 │
│  - Малые изменения       │  - Flaky test detection                │
│                          │                                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Модель 4: Матрёшка environments

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Environments как матрёшка                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Production                              │   │
│  │  App Store - все пользователи                               │   │
│  │  Максимальное качество, стабильность                        │   │
│  │                                                              │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │                   Staging                             │  │   │
│  │  │  TestFlight External - внешние тестеры                │  │   │
│  │  │  Реальные условия, но ограниченная аудитория         │  │   │
│  │  │                                                       │  │   │
│  │  │  ┌─────────────────────────────────────────────────┐ │  │   │
│  │  │  │                 QA                              │ │  │   │
│  │  │  │  TestFlight Internal - команда QA               │ │  │   │
│  │  │  │  Функциональное тестирование                   │ │  │   │
│  │  │  │                                                 │ │  │   │
│  │  │  │  ┌───────────────────────────────────────────┐ │ │  │   │
│  │  │  │  │              Development                  │ │ │  │   │
│  │  │  │  │  Local builds - разработчики              │ │ │  │   │
│  │  │  │  │  Быстрая итерация, debug                 │ │ │  │   │
│  │  │  │  └───────────────────────────────────────────┘ │ │  │   │
│  │  │  └─────────────────────────────────────────────────┘ │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Каждый слой:                                                       │
│  • Включает все проверки предыдущего                               │
│  • Добавляет свои (более строгие)                                  │
│  • Имеет свой signing (development → adhoc → appstore)             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Модель 5: Fail Fast как пожарная сигнализация

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Fail Fast = Пожарная система                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Здание (Pipeline):                                                 │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  [Датчик 1: Lint]     Первый этаж - компиляция              │   │
│  │  Срабатывает первым   ← Самая быстрая проверка              │   │
│  │                          (секунды)                          │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  [Датчик 2: Build]    Второй этаж - сборка                  │   │
│  │  Проверка компиляции  ← Средняя скорость                    │   │
│  │                          (минуты)                           │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  [Датчик 3: Unit Tests] Третий этаж - логика                │   │
│  │  Проверка бизнес-логики ← Быстрые тесты                     │   │
│  │                           (минуты)                          │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  [Датчик 4: UI Tests]  Четвёртый этаж - UI                  │   │
│  │  Проверка интерфейса   ← Медленные тесты                    │   │
│  │                           (десятки минут)                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Принцип: Срабатывание любого датчика = эвакуация (остановка)      │
│  Чем раньше - тем меньше ущерб (меньше потраченного времени)       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
## Связь с другими темами

**[[ios-code-signing]]** — Code signing является обязательным prerequisite для iOS CI/CD, поскольку каждая автоматизированная сборка требует корректных сертификатов и provisioning profiles. Fastlane match решает проблему синхронизации signing credentials между CI-серверами и разработчиками, храня их в зашифрованном Git-репозитории. Рекомендуется полностью разобраться с code signing вручную, прежде чем автоматизировать этот процесс через CI/CD.

**[[android-ci-cd]]** — Сравнение iOS CI/CD с Android CI/CD выявляет ключевые различия: iOS требует macOS runners (дороже), обязательный code signing (сложнее), привязку к конкретным версиям Xcode, тогда как Android может собираться на Linux с простым keystore. Понимание обоих подходов позволяет строить unified CI/CD pipeline для кросс-платформенных проектов и оптимизировать затраты на инфраструктуру.

**[[ios-app-distribution]]** — CI/CD pipeline автоматизирует процесс дистрибуции, описанный в ios-app-distribution: от архивирования до загрузки в TestFlight и App Store Connect. Без понимания ручного процесса публикации сложно отлаживать проблемы в автоматизированном pipeline. Изучите ручную дистрибуцию для понимания каждого шага, затем переходите к автоматизации через CI/CD.

**[[ios-testing]]** — Тестирование является центральным этапом любого CI/CD pipeline: unit tests, UI tests и snapshot tests запускаются автоматически при каждом push и pull request. Правильная настройка тестового этапа (параллельные тесты, test plans, code coverage) определяет скорость и надёжность всего pipeline. Рекомендуется настроить стратегию тестирования до построения CI/CD pipeline.

## Источники

### Официальная документация
- [Xcode Cloud Documentation](https://developer.apple.com/documentation/xcode/xcode-cloud) - Apple Developer
- [Fastlane Documentation](https://docs.fastlane.tools/) - Fastlane Docs
- [GitHub Actions for iOS](https://docs.github.com/en/actions/deployment/deploying-xcode-applications) - GitHub Docs
- [App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi) - Apple Developer

### Инструменты
- [Fastlane match](https://docs.fastlane.tools/actions/match/) - Certificate management
- [Fastlane gym](https://docs.fastlane.tools/actions/gym/) - Building
- [Fastlane pilot](https://docs.fastlane.tools/actions/pilot/) - TestFlight management

### Best Practices
- [Apple Code Signing Guide](https://developer.apple.com/support/code-signing/) - Apple Support
- [GitHub Actions macOS runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners) - Runner specifications
- [Xcode Cloud Custom Scripts](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts) - Apple Developer

## Источники и дальнейшее чтение

### Теоретические основы
- Humble J., Farley D. (2010). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deploy Automation.* — каноническая книга по CI/CD: deployment pipeline, infrastructure as code, конфигурация как код
- Fowler M. (2000). *Continuous Integration.* — оригинальная статья, определившая практику CI
- Kim G. et al. (2016). *The DevOps Handbook.* — Three Ways of DevOps: flow, feedback, continuous learning

### Практические руководства
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — процесс сборки и подписания iOS-приложений для CI/CD pipeline
- McConnell S. (2004). *Code Complete, 2nd Edition.* — принципы автоматизации сборки и defensive programming

---

## Проверь себя

> [!question]- Почему iOS CI/CD сложнее настроить, чем для Android или веб-приложений?
> 1) Требуется macOS для сборки (нет Linux runners). 2) Code signing: сертификаты и profiles нужно устанавливать на CI машину. 3) Xcode versions: разные проекты требуют разных версий Xcode. 4) Simulator management: тесты запускаются в iOS Simulator, который тяжелый. 5) Apple ID аутентификация для загрузки в App Store Connect. macOS runners дороже Linux.

> [!question]- В чем отличие Xcode Cloud от Fastlane + GitHub Actions, и когда выбирать каждый?
> Xcode Cloud: нативный, интегрирован в Xcode/App Store Connect, автоматический signing, бесплатные минуты, но ограниченная кастомизация и только Apple платформы. Fastlane + GitHub Actions: гибкий, кастомные lanes (ruby), multi-platform, но сложная настройка signing, дорогие macOS runners. Xcode Cloud для простых проектов, Fastlane для enterprise с custom workflows.

> [!question]- Сценарий: Fastlane lane для релиза периодически падает на этапе upload to TestFlight с timeout. Как сделать pipeline надежнее?
> 1) Retry logic: fastlane retry с увеличивающимся интервалом. 2) Разделить build и upload в отдельные шаги (кэшировать IPA). 3) Использовать altool/xcrun notarytool вместо deliver для загрузки. 4) App Store Connect API key вместо Apple ID (надежнее). 5) Проверить сетевые ограничения CI runner. 6) Мониторинг status.apple.com перед upload.

---

## Ключевые карточки

Какие основные инструменты iOS CI/CD?
?
Xcode Cloud (Apple native), Fastlane (Ruby-скрипты: scan, gym, pilot, deliver), GitHub Actions (macOS runners), Bitrise (iOS-ориентированный), Jenkins (self-hosted). Fastlane -- де-факто стандарт для automation, остальные -- для orchestration.

Что такое Fastlane и какие lanes типичны?
?
Набор Ruby-инструментов для автоматизации iOS. Типичные lanes: scan (тесты), gym (сборка IPA), pilot (загрузка TestFlight), deliver (App Store), match (certificates/profiles), snapshot (скриншоты). Fastfile определяет lanes, Matchfile -- signing, Appfile -- metadata.

Как решить проблему code signing на CI?
?
Fastlane Match: certificates/profiles в зашифрованном git repo, CI клонирует и устанавливает. Manual: экспорт .p12 + .mobileprovision, установка через security import и cp. Xcode Cloud: автоматически. API Key: App Store Connect API для загрузки без Apple ID.

Что такое Xcode Cloud?
?
CI/CD сервис Apple, интегрированный в Xcode и App Store Connect. Автоматическая сборка по push/PR/schedule, встроенное signing, TestFlight upload. Бесплатно: 25 часов/месяц. Ограничения: только Apple платформы, базовая кастомизация через ci_scripts/, нет SSH доступа к machine.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-testing]] | Тестирование как основа CI pipeline |
| Углубиться | [[ios-code-signing]] | Глубокое понимание signing для CI |
| Смежная тема | [[android-ci-cd]] | CI/CD Android для сравнения подходов |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |

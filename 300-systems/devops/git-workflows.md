---
title: "Git Workflows: от хаоса к порядку"
created: 2025-11-24
modified: 2026-02-13
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/devops
  - devops/git
  - workflow/branching
  - collaboration/version-control
  - type/concept
  - level/intermediate
related:
  - "[[ci-cd-pipelines]]"
  - "[[technical-debt]]"
prerequisites:
  - "[[kubernetes-basics]]"
reading_time: 12
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Git Workflows: от хаоса к порядку

> **Аналогия для понимания:** Git workflow — это как **правила дорожного движения**. Без правил — хаос: каждый едет как хочет, аварии на каждом перекрёстке (merge conflicts). С правилами — все знают куда ехать, на какой свет остановиться. **Trunk-Based Development** — это скоростное шоссе: все едут в одном направлении, никто не создаёт пробок. **GitFlow** — это сложная развязка с 5 уровнями: надёжно, но легко заблудиться. Google и Facebook выбрали "шоссе" — и деплоят тысячи раз в день.

Чем дольше живёт ветка — тем больнее merge. Trunk-Based Development: ветки < 1 дня, merge несколько раз в день, feature flags для неготовых фич. GitFlow устарел для большинства проектов.

---

## Теоретические основы

> **Git** — распределённая система контроля версий, созданная **Linus Torvalds (2005)** для разработки ядра Linux. **Git workflow** — формализованная стратегия ветвления и слияния, определяющая процесс поставки кода.

### Эволюция branching-моделей

| Год | Модель | Автор | Ключевая идея |
|-----|--------|-------|---------------|
| 2005 | **Centralized** | (SVN-стиль) | Одна ветка, все коммитят туда |
| 2010 | **GitFlow** | Vincent Driessen | 5 типов веток (main, develop, feature, release, hotfix) |
| 2011 | **GitHub Flow** | Scott Chacon | 1 main + feature branches + PR |
| 2015 | **Trunk-Based Development** | Paul Hammant | 1 trunk, ветки < 1 дня, feature flags |
| 2020 | **Ship/Show/Ask** | Rouan Wilsenach | Классификация PR по риску |

### Фундаментальный trade-off

```
Длина жизни ветки ──────────────────────────► Боль при merge
      │                                            │
      │  Trunk-Based: часы                         │  Минимальные конфликты
      │  GitHub Flow: дни                          │  Управляемые конфликты
      │  GitFlow: недели                           │  Сложные merge
      ▼                                            ▼
```

> **Исследование DORA**: команды с trunk-based development имеют **в 2× выше** deployment frequency и **в 3× ниже** change failure rate.

> **См. также**: [[ci-cd-pipelines]] — CI/CD автоматизация, [[gitops-argocd-flux]] — GitOps

---

## Prerequisites (Что нужно знать заранее)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **Git basics** | Commit, push, pull, branch — без этого не понять workflows | git-scm.com или любой Git-курс |
| **Merge vs Rebase** | Понимать разницу между способами объединения веток | Git Pro Book (бесплатно) |
| **Pull Request** | PR — основа code review в любом workflow | GitHub Docs |
| **Конфликты merge** | Придётся разрешать, нужно знать как | Практика + git mergetool |

---

## TL;DR (если совсем нет времени)

- **Trunk-Based Development** = одна main ветка, feature branches живут < 1 дня, feature flags
- **GitHub Flow** = упрощённый вариант: main + короткие feature branches + PR
- **GitFlow** = устаревший для большинства: main + develop + feature + release + hotfix
- **Google** и **Facebook** используют Trunk-Based с 35000+ разработчиков в одном репозитории
- **Правило**: чем дольше живёт ветка, тем больнее merge
- **DORA 2024**: trunk-based development — ключевой enabler для elite-команд
- **Feature flags** = код в main, но фича скрыта для пользователей до готовности
- **Начни с**: GitHub Flow → потом Trunk-Based по мере зрелости команды

---

## Кто использует какой workflow

| Компания | Workflow | Масштаб | Особенности |
|----------|----------|---------|-------------|
| **Google** | Trunk-Based | 35000+ разработчиков, 1 monorepo | Perforce + Git bridge, subset checkout |
| **Facebook** | Trunk-Based | 1 Mercurial trunk для PHP | Автооткат при поломке build |
| **Netflix** | Trunk-Based | Тысячи деплоев/день | Feature flags + canary releases |
| **Spotify** | GitHub Flow | Сотни squad'ов | Автономные команды |
| **Microsoft** | Trunk-Based (Git) | 4000+ инженеров на Windows | Перешли с GitFlow в 2017 |

> **Факт**: В 2024 DORA Report elite-кластер стабилен, а low-performing вырос с 17% до 25% — разрыв увеличивается. Trunk-based — один из ключевых предикторов elite performance.
>
> **Источники**: [Paul Hammant — Google's vs Facebook's TBD](https://paulhammant.com/2014/01/08/googles-vs-facebooks-trunk-based-development/), [DORA Report 2024](https://dora.dev/guides/dora-metrics-four-keys/)

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Trunk (main)** | Основная ветка, "источник правды" | **Главная дорога**: все второстепенные выходят из неё и возвращаются |
| **Feature branch** | Временная ветка для работы над фичей | **Съезд с шоссе**: свернул, сделал дело, вернулся на главную |
| **Merge** | Объединение изменений из ветки в trunk | **Слияние полос**: два потока становятся одним |
| **Merge conflict** | Два человека изменили одно место | **Две машины в одну полосу**: нужно решить, кто первый |
| **Feature flag** | Переключатель: код есть, но фича выключена | **Выключатель света**: провода есть, но свет не горит |
| **Code review** | Проверка кода коллегой перед merge | **Редактор статьи**: проверяет перед публикацией |
| **Pull Request (PR)** | Запрос "посмотрите и влейте мою ветку" | **Заявка на публикацию**: "готово, проверьте" |
| **Rebase** | Переписать историю — как будто начал с нового места | **Перемонтаж видео**: изменить порядок сцен |
| **Squash** | Склеить несколько коммитов в один | **Сжатие файла в архив**: много → одно |
| **Cherry-pick** | Взять конкретный коммит из другой ветки | **Выбрать вишенку**: не всё дерево, а конкретную ягоду |
| **Stacked PRs** | Цепочка зависимых PR (один на другом) | **Многоэтажный торт**: каждый слой зависит от предыдущего |
| **Branch protection** | Правила защиты ветки от прямых push | **Охрана на входе**: нельзя войти без проверки (PR) |

---

## Проблема: merge hell

```
Типичный сценарий без стратегии:

Developer A:   feature/auth ─────────────────────────────────>
Developer B:           feature/payments ─────────────────────>
Developer C:                    feature/notifications ───────>
                                                              │
                                                              ▼
                                                     MERGE DAY
                                                              │
                                                              ▼
                                              💥 Конфликты везде
                                              💥 Сломанные тесты
                                              💥 Неизвестно кто виноват
                                              💥 2 дня на разгребание
```

**Факт:** Чем дольше живёт ветка, тем больнее merge.

---

## Три основные стратегии

### 1️⃣ Trunk-Based Development (рекомендуется)

```
main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━>
       │     │     │     │     │     │     │     │
       └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘
         │     │     │     │     │     │     │     │
      <1 day <1 day              короткие feature branches

Принцип:
• Одна основная ветка (main/trunk)
• Feature branches живут < 1 дня
• Merge в main несколько раз в день
• Feature flags для неготовых фич
```

**Когда использовать:**
- Команды с CI/CD
- Continuous Deployment
- Senior-heavy команды
- Проекты с хорошим тестовым покрытием

**Преимущества:**
```
✓ Минимальные конфликты (маленькие изменения)
✓ Код всегда в deployable состоянии
✓ Быстрая обратная связь
✓ Нет "merge day"
```

**Требования:**
```
□ CI/CD pipeline (обязательно)
□ Автотесты с хорошим покрытием
□ Feature flags инфраструктура
□ Культура code review
□ Trunk protection rules
```

### 2️⃣ GitHub Flow (упрощённый)

```
main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━>
       │           │                 │
       └───────────┤                 │
         feature/X │                 │
                   ▼                 │
                 PR → Review → Merge │
                                     │
                   └─────────────────┤
                     feature/Y       │
                                     ▼
                                   PR → Review → Merge

Принцип:
• main всегда deployable
• Feature branches для каждой фичи
• PR → Review → Merge
• Deploy после merge в main
```

**Когда использовать:**
- Небольшие команды (2-10 человек)
- Веб-приложения
- Continuous Delivery
- Open source проекты

### 3️⃣ GitFlow (legacy, избегать)

```
main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━>
         │                                    ▲
         │                                    │
develop ─┼────────────────────────────────────┼──────────>
         │              │              │      │
         │    feature/A │    feature/B │      │
         │              │              │      │
         │              ▼              ▼      │
         │          merge          merge      │
         │              │              │      │
         │              └──────┬───────┘      │
         │                     │              │
         │               release/1.0          │
         │                     │              │
         └─────────────────────┴──────────────┘
                          tag v1.0

Принцип:
• main — только релизы
• develop — основная разработка
• feature/* — фичи
• release/* — подготовка релиза
• hotfix/* — срочные фиксы
```

**Почему устарел:**
```
❌ Слишком много долгоживущих веток
❌ Сложные merge между develop и main
❌ Не совместим с Continuous Deployment
❌ Overhead для большинства проектов
```

**Когда ещё актуален:**
- Редкие релизы (раз в месяц+)
- Мобильные приложения (App Store review)
- Embedded/hardware с фиксированными версиями

---

## Trunk-Based: практическое руководство

### Короткоживущие ветки

```bash
# Утро: начинаем фичу
git checkout main
git pull origin main
git checkout -b feature/add-user-avatar

# Работаем... (максимум 4-8 часов)

# После обеда: готово к review
git add .
git commit -m "feat: add user avatar upload"
git push origin feature/add-user-avatar
# → Создаём PR

# Вечер: PR approved, мержим
# После merge — ветка удаляется
```

**Правило:** Если ветка живёт > 1 дня, что-то пошло не так.

### Feature Flags

```javascript
// Фича не готова, но код в main
if (featureFlags.isEnabled('new-dashboard')) {
  return <NewDashboard />;
} else {
  return <OldDashboard />;
}

// Включаем для 10% пользователей
featureFlags.enable('new-dashboard', {
  percentage: 10
});

// Полный rollout
featureFlags.enable('new-dashboard', {
  percentage: 100
});

// Убираем флаг, удаляем старый код
```

**Инструменты:**
- LaunchDarkly
- Split.io
- Unleash (open source)
- Flipper (Ruby)

### Защита main ветки

```yaml
# .github/branch-protection.yml (или через UI)
branches:
  - name: main
    protection:
      required_status_checks:
        strict: true
        contexts:
          - "ci/tests"
          - "ci/lint"
      required_pull_request_reviews:
        required_approving_review_count: 1
        dismiss_stale_reviews: true
      enforce_admins: true
```

### Stacked PRs (продвинутый паттерн)

```
Проблема: большая фича не влезает в один PR

Решение: цепочка зависимых PR

main
  │
  └─ PR #1: Database migration (100 строк)
       │
       └─ PR #2: Backend API (150 строк)
            │
            └─ PR #3: Frontend UI (200 строк)

Каждый PR:
• Маленький и focused
• Можно review независимо
• Merge по порядку
```

**Инструменты для stacked PRs:**
- Graphite
- ghstack
- git-branchless

---

## Commit messages: conventional commits

```
Формат:
<type>(<scope>): <description>

[optional body]

[optional footer]

Типы:
feat:     Новая функциональность
fix:      Исправление бага
docs:     Только документация
style:    Форматирование (не меняет логику)
refactor: Рефакторинг (не feat, не fix)
test:     Добавление/изменение тестов
chore:    Обновление зависимостей, конфигов

Примеры:
feat(auth): add OAuth2 login
fix(api): handle null response in user endpoint
docs(readme): update installation instructions
refactor(db): extract connection pooling logic
```

**Почему это важно:**
- Автогенерация CHANGELOG
- Semantic versioning (feat = minor, fix = patch)
- Понятная история для команды

---

## Подводные камни

### Проблема 1: Trunk-Based без CI = хаос

```
Trunk-Based Development предполагает:
• Каждый commit в main — deployable
• Быстрая обратная связь от тестов

Без CI/CD:
• Сломанный main
• Никто не знает, что работает
• Хуже, чем GitFlow

Вывод: Сначала CI/CD, потом Trunk-Based
```

### Проблема 2: Feature Flags — это код

```
Накопление feature flags:

if (flag1) {
  if (flag2) {
    if (flag3) {
      // Невозможно понять что происходит
    }
  }
}

Решение:
• Удалять флаги после полного rollout
• Максимум 2-3 активных флага
• Документировать каждый флаг
• Срок жизни флага (удалить через X)
```

### Проблема 3: "Это займёт 5 минут" → 3 дня

```
Частая ситуация:
"Просто поправлю один файл"
   ↓
Конфликт с изменениями коллеги
   ↓
Нужно разобраться в его коде
   ↓
Нашёл баг в процессе
   ↓
Решил пофиксить
   ↓
3 дня спустя: ветка с 50 изменениями

Правило:
• Один PR = одна вещь
• Нашёл баг → отдельный PR
• Рефакторинг → отдельный PR
```

### Проблема 4: Review bottleneck

```
Trunk-Based требует быстрых review:

PR создан 09:00
           │
           ▼
Review в очереди...
           │
           ▼
Reviewer на митинге...
           │
           ▼
"Посмотрю после обеда"
           │
           ▼
Review 17:00 → PR устарел
           │
           ▼
Конфликты → ещё один день

Решения:
• Приоритет #1: разблокировать коллег
• Маленькие PR = быстрые review
• Review time SLA (< 4 часов)
• Pair programming как альтернатива
```

---

## Git-команды для workflow

### Ежедневные операции

```bash
# Синхронизация с main
git fetch origin
git rebase origin/main

# Или через pull с rebase (настроить глобально)
git config --global pull.rebase true
git pull

# Squash перед merge (если нужно)
git rebase -i HEAD~3  # Объединить 3 коммита
```

### Разрешение конфликтов

```bash
# Rebase и конфликт
git rebase origin/main
# ... conflict ...

# Посмотреть что конфликтует
git status

# Разрешить конфликт в файле, затем
git add <resolved-file>
git rebase --continue

# Или отменить всё
git rebase --abort
```

### Откат изменений

```bash
# Откатить последний commit (сохранить изменения)
git reset --soft HEAD~1

# Откатить merge в main
git revert -m 1 <merge-commit-hash>

# Восстановить удалённую ветку
git reflog  # Найти commit
git checkout -b recovered-branch <commit-hash>
```

---

## Сравнение стратегий

| Аспект | Trunk-Based | GitHub Flow | GitFlow |
|--------|-------------|-------------|---------|
| **Сложность** | Средняя | Низкая | Высокая |
| **Частота деплоя** | Несколько раз в день | Ежедневно | Редко |
| **Размер PR** | Маленький | Средний | Большой |
| **Требования к CI** | Обязательно | Желательно | Опционально |
| **Feature Flags** | Обязательно | Опционально | Редко |
| **Подходит для** | Senior команды | Любые команды | Legacy проекты |

---

## Actionable

**Сегодня:**
- Определи текущую стратегию команды
- Если ветки живут > 3 дней — проблема

**Эта неделя:**
- Настрой branch protection для main
- Добавь шаблон PR с чеклистом
- Договорись о формате commit messages

**Этот месяц:**
- Внедри feature flags для новых фич
- Установи SLA на code review (< 4 часов)
- Переведи долгоживущие ветки на Trunk-Based

---

## Связи

- CI/CD для автоматизации: [[ci-cd-pipelines]]
- Технический долг от плохих merge: [[technical-debt]]

---

## Источники

### Теоретические основы
- Driessen V. (2010). *A Successful Git Branching Model* (GitFlow). — Оригинальная модель 5 типов веток
- Hammant P. (2017). *Trunk-Based Development*. — Формализация TBD с кейсами Google, Facebook

### Официальные ресурсы и исследования
- [Trunk Based Development Official](https://trunkbaseddevelopment.com/) — проверено 2025-01-03
- [DORA Metrics — Four Keys](https://dora.dev/guides/dora-metrics-four-keys/) — проверено 2025-01-03
- [Atlassian: Trunk-Based Development](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development) — проверено 2025-01-03

### Кейсы компаний
- [Paul Hammant — Google's vs Facebook's Trunk-Based Development](https://paulhammant.com/2014/01/08/googles-vs-facebooks-trunk-based-development/) — проверено 2025-01-03
- [Paul Hammant — Trunk-Based Development at Facebook](https://paulhammant.com/2013/03/04/facebook-tbd/) — проверено 2025-01-03

### Сравнения и анализ
- [Toptal: Trunk-Based vs Git Flow](https://www.toptal.com/software/trunk-based-development-git-flow) — проверено 2025-01-03
- [LaunchDarkly: Git Branching vs Trunk-Based](https://launchdarkly.com/blog/git-branching-strategies-vs-trunk-based-development/) — проверено 2025-01-03
- [CircleCI: Trunk-based vs Feature-based Development](https://circleci.com/blog/trunk-vs-feature-based-dev/) — проверено 2025-01-03
- [Mergify: Trunk-Based Development vs Git Flow](https://articles.mergify.com/trunk-based-development-vs-git-flow-when-to-use-which-development-style/) — проверено 2025-01-03

### DORA Report 2024
- [DORA Report 2024 — Throughput and Stability](https://redmonk.com/rstephens/2024/11/26/dora2024/) — проверено 2025-01-03
- [Octopus: Understanding DORA Metrics 2024](https://octopus.com/devops/metrics/dora-metrics/) — проверено 2025-01-03
- [DX Highlights from 2024 DORA Report](https://getdx.com/blog/2024-dora-report/) — проверено 2025-01-03

---

**Последняя верификация**: 2025-01-03
**Уровень достоверности**: high

---

---

## Проверь себя

> [!question]- Почему Trunk-Based Development требует CI/CD, а GitFlow -- нет?
> Trunk-Based Development предполагает, что main всегда находится в deployable состоянии. Каждый коммит должен быть проверен автоматически, потому что ветки живут менее 1 дня и сливаются напрямую в main. Без CI/CD сломанный код попадёт в main незамеченным и заблокирует всю команду. GitFlow использует отдельную develop-ветку как буфер, а релизы готовятся в release-ветке -- ручная проверка возможна из-за более редких интеграций.

> [!question]- Команда жалуется на постоянные merge-конфликты. Какой workflow решит проблему и почему?
> Скорее всего, ветки живут слишком долго (дни или недели). Нужно перейти на Trunk-Based Development или хотя бы GitHub Flow с короткоживущими ветками (< 1 дня). Чем меньше изменения в каждой ветке и чем чаще интеграция, тем меньше шансов на конфликт. Также помогут stacked PRs -- разбиение большой фичи на цепочку маленьких PR.

> [!question]- Сравните подход с feature flags и подход с долгоживущими feature-ветками. В каких ситуациях каждый предпочтительнее?
> Feature flags позволяют держать незаконченный код в main, скрыв его за переключателем. Это лучше для continuous deployment и команд с хорошим тестовым покрытием. Долгоживущие ветки проще для понимания и не требуют инфраструктуры флагов, но создают "merge hell" и задерживают обратную связь. Feature flags предпочтительнее в большинстве случаев, но требуют дисциплины -- флаги нужно удалять после полного rollout, иначе код превратится в лабиринт условий.

> [!question]- Почему GitFlow считается устаревшим для большинства проектов, но всё ещё актуален для мобильной разработки?
> GitFlow создавался для проектов с редкими, запланированными релизами. Веб-приложения сегодня деплоят несколько раз в день -- GitFlow добавляет ненужный overhead. Но мобильные приложения проходят App Store review (дни ожидания), имеют фиксированные версии и требуют hotfix-веток для срочных патчей. В этом контексте GitFlow с его release- и hotfix-ветками всё ещё оправдан.

---

## Ключевые карточки

Что такое Trunk-Based Development?
?
Стратегия разработки с одной основной веткой (main/trunk), где feature branches живут менее 1 дня, а интеграция происходит несколько раз в день. Неготовые фичи скрываются за feature flags.

Чем GitHub Flow отличается от Trunk-Based Development?
?
GitHub Flow -- упрощённый вариант: main + feature branches + Pull Request. Ветки могут жить дольше (дни), обязателен code review через PR. Trunk-Based строже: ветки < 1 дня, feature flags обязательны.

Что такое feature flag?
?
Переключатель в коде, который позволяет включать/выключать функциональность без деплоя. Код есть в main, но фича скрыта от пользователей до готовности. Важно удалять флаги после полного rollout.

Почему длинноживущие ветки вредны?
?
Чем дольше ветка отделена от main, тем больше divergence и сложнее merge. Это приводит к merge-конфликтам, "merge day" и задержке обратной связи. DORA 2024 подтверждает: trunk-based -- ключевой предиктор elite performance.

Что такое Conventional Commits?
?
Формат коммитов: `<type>(<scope>): <description>`. Типы: feat, fix, docs, refactor, test, chore. Позволяет автогенерировать CHANGELOG и semantic versioning (feat = minor, fix = patch).

Что такое Stacked PRs и когда их использовать?
?
Цепочка зависимых Pull Request'ов (один поверх другого). Используются когда большая фича не влезает в один маленький PR. Каждый PR маленький, focused и может быть reviewed независимо.

Какое SLA рекомендуется для code review в Trunk-Based Development?
?
Менее 4 часов. Быстрый review критичен, потому что ветки живут < 1 дня. Задержка review приводит к устареванию PR и конфликтам. Альтернатива -- pair programming.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ci-cd-pipelines]] | Автоматизация build/test/deploy -- основа для Trunk-Based Development |
| Углубиться | [[gitops-argocd-flux]] | GitOps -- следующая эволюция: Git как source of truth для инфраструктуры |
| Смежная тема | [[technical-debt]] | Плохие merge и долгоживущие ветки -- прямой источник технического долга |
| Обзор | [[devops-overview]] | Вернуться к карте раздела DevOps |

*Проверено: 2026-01-09*

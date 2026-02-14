# Tech Knowledge Vault

> Открытая база технических знаний для IT-специалистов: от алгоритмов до архитектуры систем, от мобильной разработки до AI/ML.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Notes](https://img.shields.io/badge/Notes-650+-blue.svg)](#статистика)
[![Zones](https://img.shields.io/badge/Zones-5-green.svg)](#зоны-знаний)

---

## Что это?

**Tech Knowledge Vault** — структурированная база технических знаний, построенная по принципам когнитивной науки. Это не просто коллекция заметок, а **система активного обучения** с:

- **Пятью зонами знаний**: Foundations → Platforms → Systems → AI/ML → Craft
- **30+ точками входа**: роли, концепции, проблемы, решения, гайды сборки
- **Картами навигации (MOC)**: связи между концепциями
- **Научным подходом**: когнитивная нагрузка, интервальное повторение, testing effect
- **Практическими примерами**: код на Kotlin, Swift, Python, SQL
- **Самопроверкой**: 3-5 вопросов "Проверь себя" в каждом файле (Bloom's Apply/Analyze)
- **Flashcards**: 5-10 карточек в SR-совместимом формате для интервального повторения
- **Навигацией "Куда дальше"**: cross-domain ссылки для deeper learning
- **11 учебными маршрутами**: 6 по областям + 5 interleaved (чередование тем)

### Для кого?

- **Android/iOS разработчики** — архитектура, Compose/SwiftUI, производительность
- **Fullstack инженеры** — системный дизайн, базы данных, сети
- **Готовящиеся к интервью** — алгоритмы, паттерны, поведенческие вопросы
- **Tech Lead / Engineering Manager** — лидерство, коммуникация, карьерный рост

---

## Быстрый старт

| Цель | Начать здесь |
|------|--------------|
| **Обзор всего** | [Home.md](900-system/Home.md) — главная панель навигации |
| **Алгоритмы** | [patterns-overview](100-foundations/cs-fundamentals/patterns/patterns-overview.md) — 30+ паттернов |
| **Android** | [android-overview](200-platforms/android/android-overview.md) — Compose, архитектура, Hilt |
| **iOS** | [ios-overview](200-platforms/ios/ios-overview.md) — SwiftUI, UIKit, async/await |
| **AI/ML** | [ai-ml-overview](400-ai-ml/ai-ml-overview-v2.md) — LLM, RAG, агенты |
| **Системный дизайн** | [architecture-overview](300-systems/architecture/architecture-overview.md) |
| **Подготовка к интервью** | [career/](500-craft/career/) — стратегии, вопросы, переговоры |

### Точки входа

| Формат | Что найдёшь |
|--------|-------------|
| **По роли** | [Mobile Developer](900-system/_views/roles/role-mobile-developer.md) · [Tech Lead](900-system/_views/roles/role-tech-lead.md) · [Backend Engineer](900-system/_views/roles/role-backend-engineer.md) · [Interview Candidate](900-system/_views/roles/role-interview-candidate.md) |
| **По концепции** | [Concurrency](900-system/_views/concepts/concept-concurrency-everywhere.md) · [Memory](900-system/_views/concepts/concept-memory-management.md) · [Architecture](900-system/_views/concepts/concept-architecture-patterns.md) · [DI](900-system/_views/concepts/concept-dependency-injection.md) · [Testing](900-system/_views/concepts/concept-testing-strategies.md) · [Build Systems](900-system/_views/concepts/concept-build-systems.md) |
| **По проблеме** | [App Performance](900-system/_views/problems/problem-app-performance.md) · [Interview Prep](900-system/_views/problems/problem-interview-preparation.md) · [Team Not Shipping](900-system/_views/problems/problem-team-not-shipping.md) |
| **Помоги выбрать** | [DI Framework](900-system/_views/decisions/decide-di-framework.md) · [Architecture](900-system/_views/decisions/decide-architecture-pattern.md) · [Database](900-system/_views/decisions/decide-database-approach.md) · [Cross-Platform](900-system/_views/decisions/decide-cross-platform-strategy.md) · [API Style](900-system/_views/decisions/decide-api-style.md) |
| **Построить X** | [Android App](900-system/_views/build-guides/build-production-android-app.md) · [iOS App](900-system/_views/build-guides/build-production-ios-app.md) · [KMP Library](900-system/_views/build-guides/build-kmp-shared-library.md) · [AI Feature](900-system/_views/build-guides/build-ai-powered-feature.md) |
| **К интервью** | [Android Senior](900-system/_views/interview-bundles/interview-android-senior.md) · [System Design](900-system/_views/interview-bundles/interview-system-design.md) · [Behavioral](900-system/_views/interview-bundles/interview-behavioral-leadership.md) |
| **Справочники** | [Maturity Ladder](900-system/_views/maturity-ladder.md) · [Quick Reference](900-system/_views/quick-reference.md) · [Glossary](900-system/_views/glossary-index.md) · [What's New](900-system/_views/whats-new.md) |

---

## Зоны знаний

### 100 — Foundations: Фундамент

> Прежде чем строить — пойми, как работает компьютер.

| Область | Файлов | Описание |
|---------|--------|----------|
| **CS Fundamentals** | 63 | Алгоритмы, структуры данных, 30+ паттернов решения |
| **CS Foundations** | 61 | Memory, compilation, concurrency, type systems |
| **JVM** | 37 | GC, Memory Model, Kotlin internals, Coroutines |
| **Programming** | 12 | Clean Code, SOLID, Design Patterns, Testing |
| **Operating Systems** | 8 | Процессы, память, файловые системы |

### 200 — Platforms: Платформы

> Где твой код работает.

| Область | Файлов | Описание |
|---------|--------|----------|
| **Android** | 70 | Lifecycle, Compose, Architecture Components, Hilt, Performance |
| **Kotlin Multiplatform** | 70 | Shared code, Compose Multiplatform, expect/actual |
| **iOS** | 45 | SwiftUI, UIKit, Concurrency, Core Data, Performance |
| **Cross-platform** | 24 | iOS vs Android сравнения, паттерны миграции |

### 300 — Systems: Проектирование и эксплуатация

> Как строить и поддерживать production-системы.

| Область | Файлов | Описание |
|---------|--------|----------|
| **Networking** | 23 | TCP/IP, HTTP/2/3, DNS, TLS, мобильные сети |
| **Security** | 19 | OWASP, AuthN/AuthZ, мобильная безопасность, криптография |
| **Architecture** | 16 | System Design, микросервисы, API Design, Clean Architecture |
| **Databases** | 16 | SQL, NoSQL, индексы, транзакции, оптимизация |
| **DevOps** | 10 | Docker, Kubernetes, CI/CD, мониторинг |
| **Cloud** | 7 | AWS, GCP, Azure, serverless |

### 400 — AI/ML: Интеллект

> Слой интеллекта.

| Область | Файлов | Описание |
|---------|--------|----------|
| **AI/ML Engineering** | 43 | LLM, RAG, агенты, embeddings, оптимизация |

### 500 — Craft: Мастерство

> Человеческий фактор.

| Область | Файлов | Описание |
|---------|--------|----------|
| **Leadership** | 44 | Менеджмент, 1-1, командная динамика, найм |
| **Career** | 36 | Поиск работы, интервью, переговоры по ЗП |
| **Communication** | 26 | Презентации, письменная коммуникация, конфликты |
| **Thinking** | 22 | Когнитивные модели, обучение, продуктивность |

---

## Алгоритмические паттерны

Полное покрытие паттернов для подготовки к техническим интервью:

### Базовые паттерны
| Паттерн | Сложность | Применение |
|---------|-----------|------------|
| **Two Pointers** | Easy | Отсортированные массивы, палиндромы |
| **Binary Search** | Easy-Medium | Поиск границ, ротированные массивы |
| **Hash Map** | Easy | Частоты, дубликаты, группировка |
| **Sliding Window** | Medium | Подмассивы, подстроки фиксированного размера |

### Продвинутые паттерны
| Паттерн | Сложность | Применение |
|---------|-----------|------------|
| **Fast & Slow Pointers** | Medium | Циклы, middle element, happy number |
| **Cyclic Sort** | Medium | Массивы [1,n], missing/duplicate |
| **DFS/BFS** | Medium | Графы, деревья, кратчайший путь |
| **Backtracking** | Medium | Комбинации, перестановки, Sudoku |
| **Dynamic Programming** | Hard | Оптимизация, knapsack, LCS/LIS |

### Экспертные паттерны
| Паттерн | Сложность | Применение |
|---------|-----------|------------|
| **Top K Elements / Heaps** | Medium | K-й элемент, median в потоке |
| **Union-Find** | Medium-Hard | Связные компоненты, циклы в графе |
| **Trie** | Medium | Автодополнение, prefix search |
| **KMP / Z-function** | Advanced | Pattern matching O(n+m) |
| **Suffix Array / LCP** | Advanced | Все подстроки, LCP queries |
| **Segment Tree** | Hard | Range queries, range updates |

**[Полная карта паттернов ->](100-foundations/cs-fundamentals/patterns/patterns-overview.md)**

---

## Структура репозитория

```
tech/
├── 100-foundations/        # Фундамент (144 файла)
│   ├── cs-fundamentals/    #   Алгоритмы и паттерны (63)
│   ├── cs-foundations/     #   Память, компиляция, типы (61)
│   ├── jvm/                #   JVM, Kotlin, Coroutines (37)
│   ├── programming/        #   Clean Code, SOLID (12)
│   └── operating-systems/  #   ОС (8)
│
├── 200-platforms/          # Платформы (246 файлов)
│   ├── android/            #   Android Development (70)
│   ├── kotlin-multiplatform/ # KMP, Compose MP (70)
│   ├── ios/                #   iOS Development (45)
│   └── cross-platform/    #   iOS vs Android (24)
│
├── 300-systems/            # Проектирование и эксплуатация (91 файл)
│   ├── networking/         #   Сети и протоколы (23)
│   ├── security/           #   OWASP, AuthN/AuthZ, криптография (19)
│   ├── architecture/       #   System Design & Patterns (16)
│   ├── databases/          #   SQL, NoSQL, оптимизация (16)
│   ├── devops/             #   Docker, K8s, CI/CD (10)
│   └── cloud/              #   AWS, GCP, Azure (7)
│
├── 400-ai-ml/              # AI/ML Engineering (43 файла)
│   ├── 01-foundations/     #   LLM, модели, обзоры
│   ├── 02-core-skills/     #   RAG, Embeddings, Prompt Eng.
│   ├── 03-advanced/        #   Agents, MCP, Multimodal
│   ├── 04-agents/          #   Фреймворки, отладка, production
│   ├── 05-production/      #   Cost, Deploy, Monitoring
│   ├── 06-specialized/     #   Mobile AI, Data Prep
│   └── 07-tutorials/       #   Практические проекты
│
├── 500-craft/              # Мастерство (128 файлов)
│   ├── leadership/         #   Лидерство и менеджмент (44)
│   ├── career/             #   Карьера и поиск работы (36)
│   ├── communication/      #   Коммуникация (26)
│   └── thinking/           #   Когнитивистика, обучение (22)
│
├── 800-resources/          # Справочные материалы
│
└── 900-system/             # Система навигации
    ├── Home.md             #   Главная панель
    ├── _MOCs/              #   Карты навигации (21 MOC)
    ├── _views/             #   Точки входа (31 файл)
    ├── _meta/              #   Стандарты контента
    ├── _plans/             #   Планы развития
    └── _templates/         #   Шаблоны заметок
```

---

## Принципы организации

### Зонная архитектура

База организована в 5 семантических зон, каждая из которых — логический этап роста:

```
100 Foundations → 200 Platforms → 300 Systems → 400 AI/ML → 500 Craft
    "Пойми"         "Построй"      "Спроектируй"  "Добавь       "Расти"
                                                    интеллект"
```

### Когнитивный подход

1. **Принцип полноты** — каждый материал отвечает на ПОЧЕМУ, ЧТО, КАК
2. **Когнитивная нагрузка** — 4±1 элемент на секцию (Cowan, 2000)
3. **Прогрессивное раскрытие** — от простого к сложному
4. **Связность** — всё связано ссылками (Zettelkasten)

### Три уровня материалов

| Уровень | Объём | Назначение |
|---------|-------|------------|
| **Overview** | 300-500 строк | Быстрое введение, навигация |
| **Deep-dive** | 1500-2500 строк | Глубокое погружение с примерами |
| **Reference** | Varies | Справочник для быстрого поиска |

---

## Система обучения

Каждый из 650+ файлов содержит встроенные инструменты активного обучения:

### Встроено в Markdown (работает везде)

| Компонент | Формат | Что делает |
|-----------|--------|------------|
| **Проверь себя** | `> [!question]-` callout | 3-5 вопросов с foldable ответами (Bloom's Apply/Analyze) |
| **Ключевые карточки** | `Вопрос\n?\nОтвет` | 5-10 flashcards для Spaced Repetition plugin |
| **Куда дальше** | Таблица wiki-links | Следующий шаг, углубление, смежная тема, обзор |
| **Frontmatter** | YAML поля | `reading_time`, `difficulty`, `study_status`, `mastery` |

### С плагинами Obsidian (рекомендуется)

| Плагин | Что даёт |
|--------|----------|
| **Dataview** | Study Dashboard с прогрессом по областям и SRS-расписанием |
| **Spaced Repetition** | Автоматические flashcards из `Ключевые карточки` секций |

Подробнее: [learning-system-guide](900-system/_meta/learning-system-guide.md) | [recommended-plugins](900-system/_meta/recommended-plugins.md)

### Учебные маршруты

**По областям** (6 путей): Android, iOS, JVM, KMP, CS Fundamentals, CS Foundations

**Интерливинг** (5 путей — чередование тем для лучшего усвоения):
- **Backend Engineer** — Architecture + DB + Security + DevOps + Cloud + Networking
- **Mobile Expert** — Android + iOS + Cross-Platform + KMP
- **Interview Prep** — Алгоритмы + Карьера + System Design
- **Tech Lead** — Leadership + Communication + Architecture
- **Full Stack Foundation** — Programming + DB + Networking + Security + OS + Cloud

Все маршруты: [Home.md](900-system/Home.md) → Учебные маршруты

---

## Использование

### С Obsidian (рекомендуется)

1. Скачайте [Obsidian](https://obsidian.md/)
2. Клонируйте репозиторий: `git clone https://github.com/tech1ee/techknowledgebase.git`
3. Откройте папку как vault в Obsidian
4. Начните с [Home.md](900-system/Home.md)

### Без Obsidian

Все файлы — обычный Markdown, читаемый в любом редакторе или на GitHub.
Вики-ссылки `[[note]]` указывают на файлы в той же папке или по пути.

---

## Статистика

| Метрика | Значение |
|---------|----------|
| **Markdown файлов** | 650+ |
| **Зон знаний** | 5 |
| **Областей знаний** | 20 |
| **Точек входа** | 31 |
| **Алгоритмических паттернов** | 30+ |
| **MOC (карт навигации)** | 21 |
| **Язык контента** | Русский |
| **Язык кода** | English |

---

## Contributing

Нашли ошибку или хотите предложить улучшение?

1. Откройте Issue с описанием
2. Или создайте Pull Request

---

## Лицензия

MIT License — см. [LICENSE](LICENSE)

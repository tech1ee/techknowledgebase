# Tech Knowledge Vault

> Открытая база технических знаний для IT-специалистов: от алгоритмов до архитектуры систем, от мобильной разработки до AI/ML. На русском языке, с кодом на английском.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Notes](https://img.shields.io/badge/Notes-980+-blue.svg)](#статистика)
[![Areas](https://img.shields.io/badge/Areas-13-green.svg)](#области-знаний)

---

## Что это?

**Tech Knowledge Vault** — структурированная база технических знаний, построенная по принципам когнитивной науки. Это не просто коллекция заметок, а **система обучения** с:

- **Тремя уровнями глубины**: Overview → Deep-dive → Reference
- **Картами навигации (MOC)**: связи между концепциями
- **Научным подходом**: когнитивная нагрузка, интервальное повторение
- **Практическими примерами**: код на Kotlin, Swift, Python, SQL

### Для кого?

- **Android/iOS разработчики** — архитектура, Compose/SwiftUI, производительность
- **Fullstack инженеры** — системный дизайн, базы данных, сети
- **Готовящиеся к интервью** — алгоритмы, паттерны, поведенческие вопросы
- **Tech Lead / Engineering Manager** — лидерство, коммуникация, карьерный рост

---

## Быстрый старт

| Цель | Начать здесь |
|------|--------------|
| **Обзор всего** | [Home.md](400-system/Home.md) — главная панель |
| **Алгоритмы** | [patterns-overview](100-areas/cs-fundamentals/patterns/patterns-overview.md) — 30+ паттернов |
| **Android** | [android-overview](100-areas/android/android-overview.md) — Compose, архитектура, Hilt |
| **iOS** | [100-areas/ios/](100-areas/ios/) — SwiftUI, UIKit, async/await |
| **AI/ML** | [ai-ml-overview-v2](100-areas/ai-ml/ai-ml-overview-v2.md) — LLM, RAG, агенты |
| **Системный дизайн** | [architecture-overview](100-areas/architecture/architecture-overview.md) |
| **Подготовка к интервью** | [100-areas/career/](100-areas/career/) — стратегии, вопросы, переговоры |

---

## Области знаний

### Разработка

| Область | Файлов | Описание |
|---------|--------|----------|
| **Android** | 66 | Lifecycle, Compose, Architecture Components, Hilt, Performance |
| **iOS** | 45 | SwiftUI, UIKit, Concurrency, Core Data, Performance |
| **Kotlin Multiplatform** | 37 | Shared code, Compose Multiplatform, expect/actual |
| **Cross-platform** | 24 | iOS vs Android сравнения, паттерны миграции |
| **JVM** | 25 | GC, Memory Model, Kotlin internals, Coroutines |

### Computer Science

| Область | Файлов | Описание |
|---------|--------|----------|
| **CS Fundamentals** | 63 | Алгоритмы, структуры данных, 30+ паттернов решения |
| **Databases** | 16 | SQL, NoSQL, индексы, транзакции, оптимизация |
| **Networking** | 23 | TCP/IP, HTTP/2/3, DNS, TLS, мобильные сети |
| **Operating Systems** | 8 | Процессы, память, файловые системы |

### Инфраструктура

| Область | Файлов | Описание |
|---------|--------|----------|
| **Architecture** | 12 | System Design, микросервисы, DDD, Clean Architecture |
| **DevOps** | 10 | Docker, Kubernetes, CI/CD, мониторинг |
| **Cloud** | 7 | AWS, GCP, Azure, serverless |
| **Security** | 13 | OWASP, мобильная безопасность, криптография |

### AI/ML

| Область | Файлов | Описание |
|---------|--------|----------|
| **AI/ML Engineering** | 43 | LLM, RAG, агенты, embeddings, оптимизация |
| **+ NotebookLM Export** | 30 | Дополнительные справочные материалы |

### Soft Skills & Карьера

| Область | Файлов | Описание |
|---------|--------|----------|
| **Leadership** | 44 | Менеджмент, 1-1, командная динамика, найм |
| **Career** | 37 | Поиск работы, интервью, переговоры по ЗП |
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

**[Полная карта паттернов →](100-areas/cs-fundamentals/patterns/patterns-overview.md)**

---

## Структура репозитория

```
tech/
├── 000-inbox/              # Входящие заметки (очередь обработки)
│
├── 100-areas/              # Основные области знаний (850+ файлов)
│   ├── ai-ml/              # AI/ML Engineering
│   ├── android/            # Android Development
│   ├── architecture/       # System Design & Patterns
│   ├── career/             # Карьера и поиск работы
│   ├── cloud/              # AWS, GCP, Azure
│   ├── communication/      # Коммуникация
│   ├── cross-platform/     # iOS vs Android
│   ├── cs-fundamentals/    # Алгоритмы и паттерны
│   │   └── patterns/       # 30+ алгоритмических паттернов
│   ├── databases/          # SQL, NoSQL, оптимизация
│   ├── devops/             # Docker, K8s, CI/CD
│   ├── ios/                # iOS Development
│   ├── jvm/                # JVM, Kotlin, Coroutines
│   ├── kotlin-multiplatform/
│   ├── leadership/         # Лидерство и менеджмент
│   ├── networking/         # Сети и протоколы
│   ├── operating-systems/  # ОС
│   ├── programming/        # Clean Code, SOLID
│   ├── security/           # OWASP, криптография
│   └── thinking/           # Когнитивистика, обучение
│
├── 200-resources/          # Справочные материалы
│
├── 300-content/            # Проекты и публикации
│   └── it-market-2025/     # Исследование рынка IT
│
├── 400-system/             # Система навигации
│   ├── Home.md             # Главная панель
│   ├── _MOCs/              # Карты навигации по областям
│   ├── _meta/              # Стандарты и шаблоны
│   └── _templates/         # 8 типов шаблонов заметок
│
├── _automation/            # Claude Code интеграция
│   ├── agents/             # AI-агенты для контента
│   └── slash-commands/     # Команды автоматизации
│
└── docs/                   # Исследовательские документы
    └── research/           # 70+ research notes
```

---

## Принципы организации

### Когнитивный подход

База построена на научных принципах обучения:

1. **Принцип полноты** — каждый материал отвечает на ПОЧЕМУ, ЧТО, КАК
2. **Когнитивная нагрузка** — 4±1 элемент на секцию (Miller's Law)
3. **Прогрессивное раскрытие** — от простого к сложному
4. **Связность** — всё связано ссылками (Zettelkasten)

### Три уровня материалов

| Уровень | Объём | Назначение |
|---------|-------|------------|
| **Overview** | 300-500 строк | Быстрое введение, навигация |
| **Deep-dive** | 1500-2500 строк | Глубокое погружение с примерами |
| **Reference** | Varies | Справочник для быстрого поиска |

### Восемь типов контента

1. **Concept** — определение + контекст
2. **Deep-Dive** — полное исследование темы
3. **Reference** — справочник/cheatsheet
4. **Tutorial** — пошаговое руководство
5. **Comparison** — сравнительный анализ
6. **Analysis** — разбор проблемы
7. **Research Log** — ход исследования
8. **Tool** — документация инструмента

---

## Использование

### С Obsidian (рекомендуется)

1. Скачайте [Obsidian](https://obsidian.md/)
2. Клонируйте репозиторий: `git clone https://github.com/tech1ee/techknowledgebase.git`
3. Откройте папку как vault в Obsidian
4. Начните с [Home.md](400-system/Home.md)

### Без Obsidian

Все файлы — обычный Markdown, читаемый в любом редакторе или на GitHub.
Вики-ссылки `[[note]]` указывают на файлы в той же папке или по пути.

---

## Ключевые материалы

### Алгоритмы (must-read)

| Материал | Что внутри |
|----------|------------|
| [patterns-overview](100-areas/cs-fundamentals/patterns/patterns-overview.md) | Карта всех паттернов + как выбрать |
| [two-pointers-pattern](100-areas/cs-fundamentals/patterns/two-pointers-pattern.md) | Two Pointers во всех вариациях |
| [sliding-window-pattern](100-areas/cs-fundamentals/patterns/sliding-window-pattern.md) | Sliding Window + монотонная очередь |
| [binary-search-pattern](100-areas/cs-fundamentals/patterns/binary-search-pattern.md) | Binary Search: границы, ротация |
| [dp-patterns](100-areas/cs-fundamentals/patterns/dp-patterns.md) | DP: knapsack, LCS, grid, intervals |
| [string-algorithms-advanced](100-areas/cs-fundamentals/patterns/string-algorithms-advanced.md) | KMP, Z-function, Suffix Array, Manacher |
| [dfs-bfs-patterns](100-areas/cs-fundamentals/patterns/dfs-bfs-patterns.md) | DFS/BFS, топологическая сортировка |

### Мобильная разработка

| Материал | Что внутри |
|----------|------------|
| [android-overview](100-areas/android/android-overview.md) | Карта Android-разработки |
| [android-compose-architecture](100-areas/android/) | Compose + архитектура |
| [android-dependency-injection](100-areas/android/android-dependency-injection.md) | Hilt, Koin, Manual DI |
| [ios/](100-areas/ios/) | SwiftUI, UIKit, Concurrency |

### Системный дизайн

| Материал | Что внутри |
|----------|------------|
| [architecture-overview](100-areas/architecture/architecture-overview.md) | Карта архитектуры |
| [databases](100-areas/databases/) | SQL vs NoSQL, индексы, шардирование |
| [networking](100-areas/networking/) | HTTP/2/3, TCP, DNS, TLS |

---

## Статистика

| Метрика | Значение |
|---------|----------|
| **Markdown файлов** | 983 |
| **Областей знаний** | 13 основных + 10 дополнительных |
| **Алгоритмических паттернов** | 30+ |
| **Шаблонов контента** | 8 |
| **MOC (карт навигации)** | 10 |
| **Размер** | 384 MB |
| **Язык контента** | Русский |
| **Язык кода** | English |

---

## Обновления

Репозиторий активно развивается. Основные направления:

- [ ] Серия материалов по Dependency Injection (Spring, .NET, Hilt, Koin)
- [ ] Расширение покрытия System Design
- [ ] Материалы по Kotlin Multiplatform
- [ ] Интерактивные примеры кода

**Последнее обновление:** 2026-02-08

---

## Contributing

Нашли ошибку или хотите предложить улучшение?

1. Откройте Issue с описанием
2. Или создайте Pull Request

---

## Автор

Создано для систематизации знаний и подготовки к техническим интервью.

---

## Лицензия

MIT License — см. [LICENSE](LICENSE)

---

<p align="center">
  <b>Звезда на GitHub поддержит развитие проекта!</b>
</p>

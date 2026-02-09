# Tech Knowledge Vault

> Открытая база технических знаний для IT-специалистов: от алгоритмов до архитектуры систем, от мобильной разработки до AI/ML. На русском языке, с кодом на английском.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Notes](https://img.shields.io/badge/Notes-640+-blue.svg)](#статистика)
[![Areas](https://img.shields.io/badge/Areas-20-green.svg)](#области-знаний)

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
| **Обзор всего** | [Home.md](400-system/Home.md) — главная панель навигации |
| **Алгоритмы** | [patterns-overview](100-areas/cs-fundamentals/patterns/patterns-overview.md) — 30+ паттернов |
| **Android** | [android-overview](100-areas/android/android-overview.md) — Compose, архитектура, Hilt |
| **iOS** | [ios-overview](100-areas/ios/ios-overview.md) — SwiftUI, UIKit, async/await |
| **AI/ML** | [ai-ml-overview](100-areas/ai-ml/ai-ml-overview-v2.md) — LLM, RAG, агенты |
| **Системный дизайн** | [architecture-overview](100-areas/architecture/architecture-overview.md) |
| **Подготовка к интервью** | [career/](100-areas/career/) — стратегии, вопросы, переговоры |

---

## Области знаний

### Разработка

| Область | Файлов | Описание |
|---------|--------|----------|
| **Android** | 66 | Lifecycle, Compose, Architecture Components, Hilt, Performance |
| **iOS** | 45 | SwiftUI, UIKit, Concurrency, Core Data, Performance |
| **Kotlin Multiplatform** | 70 | Shared code, Compose Multiplatform, expect/actual |
| **Cross-platform** | 24 | iOS vs Android сравнения, паттерны миграции |
| **JVM** | 37 | GC, Memory Model, Kotlin internals, Coroutines |

### Computer Science

| Область | Файлов | Описание |
|---------|--------|----------|
| **CS Fundamentals** | 63 | Алгоритмы, структуры данных, 30+ паттернов решения |
| **CS Foundations KMP** | 61 | Memory, compilation, concurrency, type systems |
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
| **Programming** | 12 | Clean Code, SOLID, Design Patterns, Testing |

### AI/ML

| Область | Файлов | Описание |
|---------|--------|----------|
| **AI/ML Engineering** | 43 | LLM, RAG, агенты, embeddings, оптимизация |

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

**[Полная карта паттернов ->](100-areas/cs-fundamentals/patterns/patterns-overview.md)**

---

## Структура репозитория

```
tech/
├── 100-areas/              # Основные области знаний (640 файлов)
│   ├── ai-ml/              # AI/ML Engineering (43)
│   ├── android/            # Android Development (66)
│   ├── architecture/       # System Design & Patterns (12)
│   ├── career/             # Карьера и поиск работы (37)
│   ├── cloud/              # AWS, GCP, Azure (7)
│   ├── communication/      # Коммуникация (26)
│   ├── cross-platform/     # iOS vs Android (24)
│   ├── cs-foundations-kmp/  # Низкоуровневые основы (61)
│   ├── cs-fundamentals/    # Алгоритмы и паттерны (63)
│   ├── databases/          # SQL, NoSQL, оптимизация (16)
│   ├── devops/             # Docker, K8s, CI/CD (10)
│   ├── ios/                # iOS Development (45)
│   ├── jvm/                # JVM, Kotlin, Coroutines (37)
│   ├── kotlin-multiplatform/ # KMP, Compose MP (70)
│   ├── leadership/         # Лидерство и менеджмент (44)
│   ├── networking/         # Сети и протоколы (23)
│   ├── operating-systems/  # ОС (8)
│   ├── programming/        # Clean Code, SOLID (12)
│   ├── security/           # OWASP, криптография (13)
│   └── thinking/           # Когнитивистика, обучение (22)
│
├── 200-resources/          # Справочные материалы
│
├── 400-system/             # Система навигации
│   ├── Home.md             # Главная панель
│   ├── _MOCs/              # Карты навигации (21 MOC)
│   ├── _meta/              # Стандарты контента
│   ├── _plans/             # Планы развития
│   └── _templates/         # Шаблоны заметок
│
└── docs/                   # Исследовательские документы
    └── research/           # 70+ research notes
```

---

## Принципы организации

### Когнитивный подход

База построена на научных принципах обучения:

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

## Статистика

| Метрика | Значение |
|---------|----------|
| **Markdown файлов** | 640+ |
| **Областей знаний** | 20 |
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

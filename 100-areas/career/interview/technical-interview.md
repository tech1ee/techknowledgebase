---
title: "Android Technical Interview 2025: полный гайд по раундам"
created: 2025-12-26
modified: 2025-12-26
type: deep-dive
status: published
confidence: high
tags:
  - topic/career
  - type/guide
  - level/advanced
  - interview
related:
  - "[[interview-process]]"
  - "[[coding-challenges]]"
  - "[[system-design-android]]"
  - "[[android-questions]]"
---

# Technical Interview: 4-6 раундов глубокой проверки

Technical interview для Android engineer в FAANG — это 4-6 раундов интенсивной проверки: coding, system design, Android domain, и live coding. Каждый раунд оценивает разные навыки. Google делает упор на coding больше, чем на system design. Meta добавляет отдельные Android-specific раунды. DoorDash и TikTok включают live coding где ты пишешь реальный Android UI. Этот гайд — overview всех технических раундов с навигацией к детальным материалам.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Android fundamentals** | Lifecycle, Compose, Coroutines | [[android-questions]] |
| **DSA basics** | LeetCode-style задачи | [[coding-challenges]] |
| **System Design** | Проектирование мобильных систем | [[system-design-android]] |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Junior** | ⚠️ Читать | Понять процесс заранее |
| **Middle** | ✅ Да | Готовься к первым FAANG |
| **Senior** | ✅ Да | Основная аудитория |

### Терминология для новичков

> 💡 **Technical Interview** = проверка навыков кодинга, системного дизайна и знания предметной области. 4-6 раундов по 45-60 минут.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **DSA** | Data Structures & Algorithms | **Школьная математика** — основа для задач |
| **LLD** | Low-Level Design — детальное проектирование | **Чертёж здания** — каждый кирпич |
| **HLD** | High-Level Design — архитектура | **План города** — где что находится |
| **Live Coding** | Написание кода в реальном времени | **Экзамен у доски** — пишешь пока смотрят |
| **Domain Round** | Глубокая проверка Android | **Экзамен по специальности** |
| **Onsite** | Финальные раунды (remote или на месте) | **Финальный экзамен** |
| **Bar Raiser** | Независимый оценщик в Amazon | **Внешний эксперт** |
| **STAR** | Situation-Task-Action-Result — формат ответа | **Шаблон истории** |
| **Whiteboard** | Решение на доске/экране | **Рисуем решение** |
| **Follow-up** | Усложнение задачи | **"А если...?"** |

---

## Терминология

| Термин | Что это |
|--------|---------|
| **DSA** | Data Structures & Algorithms — алгоритмы |
| **LLD** | Low-Level Design — детальное проектирование |
| **HLD** | High-Level Design — архитектура системы |
| **Live Coding** | Написание реального кода приложения в реальном времени |
| **Domain Round** | Проверка глубокого знания Android |

---

## Структура технических раундов

### Типичный onsite для Senior Android

```
┌─────────────────────────────────────────────────────────────┐
│                    TECHNICAL ROUNDS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Round 1: DSA Coding         ████████████████  45-60 мин   │
│           Algorithms, data structures, LeetCode style      │
│                                                             │
│  Round 2: DSA или Live Coding ████████████████  45-60 мин  │
│           Второй coding или Android UI implementation      │
│                                                             │
│  Round 3: System Design      ████████████████  45-60 мин   │
│           Mobile architecture, offline-first, caching      │
│                                                             │
│  Round 4: Android Domain     ████████████████  45-60 мин   │
│           Lifecycle, Compose, Coroutines, internals        │
│                                                             │
│  (Round 5: Behavioral)       Отдельный материал            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### По компаниям

| Компания | Coding | System Design | Android Domain | Live Coding |
|----------|--------|---------------|----------------|-------------|
| **Google** | 2-3 раунда | 1-2 раунда | Встроено в coding | Редко |
| **Meta** | 2 раунда | 1 раунд | Отдельный раунд | Редко |
| **Amazon** | 2 раунда | 1 раунд | LP-focused | Редко |
| **DoorDash** | 1 раунд | 1 раунд | Отдельный раунд | **Да** |
| **TikTok** | 2 раунда | 1 раунд | Отдельный раунд | **Да** |

---

## Round 1-2: DSA Coding

### Что ожидать

```
Формат: 45 минут
├── 5 мин: Intro, выбор языка (Kotlin/Java)
├── 35-40 мин: 1-2 задачи (Medium-Hard)
└── 5 мин: Вопросы интервьюеру

Среда: CoderPad, Google Docs, или shared IDE
Особенность Google: Google Docs БЕЗ подсветки синтаксиса
```

### Что оценивают

| Критерий | Что смотрят |
|----------|-------------|
| **Problem-solving** | Как подходишь к задаче, разбиваешь на части |
| **Communication** | Объясняешь ход мысли вслух |
| **Code quality** | Читаемость, naming, edge cases |
| **Complexity analysis** | Понимаешь Big O своего решения |
| **Testing** | Проверяешь код на примерах |

### Ключевые паттерны

```
Must know для Android Senior:
├── Two Pointers
├── Sliding Window
├── BFS/DFS (графы, деревья)
├── Binary Search
├── HashMaps
├── Dynamic Programming (основы)
└── Backtracking (основы)

Подробнее → [[coding-challenges]]
```

### Pro Tips

```
✓ Говори вслух — silence = red flag
✓ Уточни constraints перед решением
✓ Начни с brute force, потом оптимизируй
✓ Тестируй на edge cases (empty, single, large)
✓ Анализируй complexity СРАЗУ после решения
```

---

## Round 3: System Design

### Что ожидать

```
Формат: 45-60 минут
├── 5-10 мин: Clarifying questions
├── 10-15 мин: High-level architecture
├── 20-25 мин: Deep dive в компоненты
└── 5-10 мин: Trade-offs, discussion

ВАЖНО: Mobile System Design ≠ Backend System Design
Фокус на клиентской части, не на серверах
```

### Типичные задачи

| Задача | Ключевые аспекты |
|--------|------------------|
| Design Instagram Feed | Pagination, image caching, infinite scroll |
| Design Chat App | Real-time, offline messages, sync |
| Design Offline Note App | Local-first, conflict resolution |
| Design Image Library | Memory/disk cache, LRU, threading |
| Design Video Player | Streaming, quality adaptation |

### Framework для ответа

```
1. REQUIREMENTS (10 мин)
   └── Functional + Non-functional + Constraints

2. HIGH-LEVEL (15 мин)
   ├── UI Layer (Compose/Fragments)
   ├── ViewModel Layer
   ├── Domain Layer (Use Cases)
   ├── Data Layer (Repository)
   └── Data Sources (Local + Remote)

3. DEEP DIVE (20 мин)
   └── Один компонент детально с trade-offs

4. DISCUSSION (10 мин)
   └── Альтернативы, edge cases, масштабирование

Подробнее → [[system-design-android]]
```

### Ключевые темы

```
Mobile-specific:
├── Offline-first architecture
├── Caching strategies (memory + disk)
├── Sync mechanisms
├── Push notifications
├── Battery optimization
└── Network handling (retry, exponential backoff)
```

---

## Round 4: Android Domain

### Что ожидать

```
Формат: 45-60 минут
├── Deep dive в Android fundamentals
├── Discussion о прошлых проектах
├── Конкретные технические вопросы
└── Иногда: написать pseudo-code

Особенность: Многие Big Tech engineers fail этот раунд,
потому что работают только с внутренними абстракциями
и не знают "vanilla Android"
```

### Темы, которые спрашивают

| Категория | Темы |
|-----------|------|
| **Lifecycle** | Activity, Fragment, ViewModel, SavedStateHandle |
| **Compose** | Recomposition, State, Side Effects, remember |
| **Concurrency** | Coroutines, Flow, StateFlow, Dispatchers |
| **Architecture** | MVVM, MVI, Clean Architecture, multi-module |
| **Memory** | Leaks, profiling, WeakReference |
| **Performance** | Startup, ANR, StrictMode, Baseline Profiles |
| **Storage** | Room, DataStore, SharedPreferences migration |

### Пример вопросов

```
Lifecycle:
• What happens when device rotates during network call?
• How does ViewModel survive configuration changes?
• When is onSaveInstanceState called vs onPause?

Compose:
• When does recomposition happen?
• What's the difference between remember and rememberSaveable?
• How to avoid unnecessary recompositions?

Coroutines:
• What happens if child coroutine fails?
• Difference between launch and async?
• How does structured concurrency work?

Подробнее → [[android-questions]]
```

---

## Live Coding Round

### Что ожидать

```
Компании: DoorDash, TikTok, Verkada, некоторые startups

Формат: 60 минут
├── Реальная Android задача (UI или feature)
├── Pair programming с интервьюером
├── Используешь Android Studio или аналог
└── Должен скомпилироваться и работать

Примеры задач:
• Implement a RecyclerView with infinite scroll
• Build a search screen with debouncing
• Create a custom view with touch handling
• Implement image gallery with gestures
```

### Как готовиться

```
1. Practice writing Android code БЕЗ autocomplete
   └── Помни signatures: onCreate, onCreateView, etc.

2. Знай наизусть:
   ├── RecyclerView setup (Adapter, ViewHolder)
   ├── Basic Compose UI (Column, Row, LazyColumn)
   ├── ViewModel + StateFlow pattern
   ├── Retrofit setup
   └── Room database setup

3. Practice pair programming
   └── Pramp, друг, коллега

4. Говори вслух что делаешь
   └── "I'm creating the adapter first, then..."
```

### Чеклист для Live Coding

```
□ Знаю Android Studio shortcuts
□ Могу написать RecyclerView с нуля
□ Могу написать Compose screen с нуля
□ Знаю как подключить Retrofit
□ Могу объяснить каждую строку кода
□ Практиковался без autocomplete
```

---

## Timeline раунда (45 минут)

### Coding Round

```
0:00-0:05   Intro, выбор языка
0:05-0:08   Читаешь задачу, clarifying questions
0:08-0:12   Проговариваешь approach
0:12-0:35   Пишешь код, объясняешь
0:35-0:40   Тестируешь на examples
0:40-0:42   Анализ complexity
0:42-0:45   Вопросы интервьюеру
```

### System Design Round

```
0:00-0:02   Intro
0:02-0:10   Clarifying requirements
0:10-0:25   High-level architecture
0:25-0:42   Deep dive + trade-offs
0:42-0:45   Wrap-up, questions
```

---

## Что делать когда stuck

### Coding

```
Ситуация: Не знаешь как начать
→ "Let me think about the brute force approach first"
→ Начни с самого простого, неоптимального решения

Ситуация: Не работает код
→ "Let me trace through with this example"
→ Dry run по шагам вслух

Ситуация: Не знаешь оптимальное решение
→ "The brute force is O(n²). I'm thinking about
    how to optimize... maybe with a HashMap?"
→ Покажи ход мысли, даже если не дойдёшь
```

### System Design

```
Ситуация: Не уверен в требованиях
→ "Before I proceed, let me clarify..."
→ Лучше спросить, чем предположить неправильно

Ситуация: Не знаешь как спроектировать компонент
→ "I haven't designed this exact component before,
    but here's how I would approach it..."
→ Покажи thinking process
```

---

## Оценка по levels

### Junior (L3-L4)

```
Coding: Solve Medium problems
System Design: Basic understanding, follow guidance
Android: Know fundamentals (Lifecycle, RecyclerView)
Ожидания: Need help, but can contribute
```

### Senior (L5)

```
Coding: Solve Medium-Hard problems
System Design: Lead discussion, propose trade-offs
Android: Deep knowledge, explain WHY things work
Ожидания: Can work independently, mentor others
```

### Staff (L6+)

```
Coding: Solve Hard, discuss alternatives
System Design: Design complex systems, foresee issues
Android: Expert level, shape technical direction
Ожидания: Lead projects, influence team decisions
```

---

## Preparation Timeline

### 2-3 месяца (optimal)

```
Месяц 1: DSA Focus
├── Blind 75 / NeetCode 150
├── 1-2 часа в день
├── Focus on patterns
└── Цель: Medium за 25-30 мин

Месяц 2: System Design + Android
├── 5-10 mobile system design problems
├── Review Android fundamentals
├── Practice explaining architecture
└── Цель: уверенно вести design discussion

Месяц 3: Mock Interviews + Polish
├── 2-3 mocks в неделю
├── Practice all round types
├── Company-specific prep
└── Цель: comfortable в любом раунде
```

### 1 месяц (intensive)

```
Week 1: DSA sprint (Blind 75 core)
Week 2: System Design + Android domain
Week 3: Mocks + weak areas
Week 4: Light practice + rest
```

---

## Ресурсы по раундам

### Coding

| Ресурс | Для чего |
|--------|----------|
| [[coding-challenges]] | Полный гайд по LeetCode |
| [NeetCode](https://neetcode.io) | Структурированные паттерны |
| [LeetCode](https://leetcode.com) | Практика |

### System Design

| Ресурс | Для чего |
|--------|----------|
| [[system-design-android]] | Mobile-specific design |
| [Mobile System Design](https://github.com/weeeBox/mobile-system-design) | Framework |

### Android Domain

| Ресурс | Для чего |
|--------|----------|
| [[android-questions]] | Типичные вопросы |
| [GitHub Android Interview](https://github.com/amitshekhariitbhu/android-interview-questions) | Question bank |

---

## Checklist перед интервью

```
CODING:
□ 100+ LeetCode problems solved
□ Know all major patterns
□ Can solve Medium in 25-30 min
□ Practice в том же environment (CoderPad, etc.)

SYSTEM DESIGN:
□ 5+ mobile designs practiced
□ Know offline-first, caching, sync
□ Can lead 45-min discussion
□ Understand trade-offs

ANDROID DOMAIN:
□ Lifecycle — могу объяснить детально
□ Compose — понимаю recomposition
□ Coroutines — structured concurrency
□ Architecture — MVVM/MVI trade-offs

GENERAL:
□ Practiced mock interviews
□ Can think out loud naturally
□ Know company-specific focus
□ Prepared questions for interviewer
```

---

## Куда дальше

→ [[coding-challenges]] — детальная подготовка к coding
→ [[system-design-android]] — mobile system design
→ [[android-questions]] — Android-specific вопросы
→ [[kotlin-questions]] — Kotlin вопросы
→ [[behavioral-interview]] — behavioral раунд

---

## Источники

- [Prepfully: Google Android Engineer](https://prepfully.com/interview-guides/google-android-engineer)
- [Prepfully: Meta Android Engineer](https://prepfully.com/interview-guides/meta-android-engineer)
- [Medium: How to Ace Android Interview](https://medium.com/@YodgorbekKomilo/how-to-ace-your-android-developer-interview-a-complete-guide-for-algorithms-technical-system-0d6118316524)
- [InterviewBit: Android Interview Questions](https://www.interviewbit.com/android-interview-questions/)
- [GitHub: Android Interview Questions](https://github.com/amitshekhariitbhu/android-interview-questions)

---

*Обновлено: 2025-12-26*

---

*Проверено: 2026-01-09*

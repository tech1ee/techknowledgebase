---
title: "Интерливинг: подготовка к интервью"
created: 2026-02-14
modified: 2026-02-14
type: guide
tags:
  - type/guide
  - navigation
  - learning-path
---

# Интерливинг: подготовка к интервью

> Чередующийся (interleaved) план подготовки к техническому интервью за 8-10 недель.
> Вместо последовательного прохождения тем — смешиваем CS, поведенческие вопросы, архитектуру и платформу.
> Это заставляет мозг активнее переключаться и лучше закреплять материал (см. [[desirable-difficulties]]).

---

## Как пользоваться

- **Темп:** 2-3 файла в день, ~60-90 минут
- **Структура:** 5 рабочих дней в неделю, Review Day каждые 4-5 элементов
- **Review Day:** перечитай заметки недели + реши 2-3 задачи LeetCode по изученным паттернам
- **Чекбоксы:** отмечай `[x]` после прочтения
- **Время:** `(Xm)` — примерное время на чтение файла

> [!tip] Пропуск известного материала
> Если ты уверенно знаешь тему (например, Big O или массивы) — пробеги файл за 5 минут, отметь `[x]` и двигайся дальше. Экономь время для слабых зон.

---

## Фаза 1: Структуры данных + Поведенческая подготовка (Недели 1-3)

> Цель: построить фундамент CS и параллельно освоить soft skills для интервью.

### Неделя 1 — Основы и первое знакомство с процессом

> [!tip] Если Big O и массивы — пройденный этап
> Пропусти первые два файла и начни сразу с [[se-interview-foundation]].

**День 1**
- [ ] [[big-o-complexity]] ⏱ 20m
- [ ] [[se-interview-foundation]] ⏱ 15m

**День 2**
- [ ] [[problem-solving-framework]] ⏱ 15m
- [ ] [[arrays-strings]] ⏱ 25m

**День 3**
- [ ] [[behavioral-interview]] ⏱ 15m
- [ ] [[linked-lists]] ⏱ 20m

**День 4**
- [ ] [[interview-process]] ⏱ 15m
- [ ] [[stacks-queues]] ⏱ 20m

**День 5 — Review Day**
- [ ] Повтори заметки недели (Big O, массивы, связные списки, стеки/очереди)
- [ ] Реши 2-3 задачи LeetCode: Easy из [[leetcode-roadmap]] (массивы, строки)
- [ ] Запиши ответы на 2 поведенческих вопроса из [[behavioral-questions]]

---

### Неделя 2 — Деревья, хеш-таблицы и интервью-процесс

**День 1**
- [ ] [[hash-tables]] ⏱ 20m
- [ ] [[technical-interview]] ⏱ 16m

**День 2**
- [ ] [[trees-binary]] ⏱ 25m
- [ ] [[behavioral-questions]] ⏱ 20m

**День 3**
- [ ] [[heaps-priority-queues]] ⏱ 20m
- [ ] [[coding-challenges]] ⏱ 15m

**День 4**
- [ ] [[graphs]] ⏱ 25m
- [ ] [[ai-interview-preparation]] ⏱ 13m

**День 5 — Review Day**
- [ ] Повтори: хеш-таблицы, деревья, кучи, графы
- [ ] Реши 3 задачи LeetCode: хеш-таблицы (Two Sum, Group Anagrams) + деревья (Invert Tree)
- [ ] Подготовь 2 STAR-истории для поведенческих вопросов

---

### Неделя 3 — Сортировки, поиск и начало алгоритмов

> [!tip] Если сортировки известны
> Сфокусируйся на Quick Sort partitioning и Counting Sort — они чаще всего спрашиваются.

**День 1**
- [ ] [[sorting-algorithms]] ⏱ 25m
- [ ] [[ai-interview-prompts]] ⏱ 13m

**День 2**
- [ ] [[searching-algorithms]] ⏱ 20m
- [ ] [[recursion-fundamentals]] ⏱ 15m

**День 3**
- [ ] [[interview-tracking-system]] ⏱ 10m
- [ ] [[divide-and-conquer]] ⏱ 20m

**День 4**
- [ ] [[greedy-algorithms]] ⏱ 20m
- [ ] [[job-search-strategy]] ⏱ 15m

**День 5 — Review Day**
- [ ] Повтори: сортировки, бинарный поиск, рекурсия, жадные алгоритмы
- [ ] Реши 3 задачи LeetCode: Binary Search (search rotated array), рекурсия (Fibonacci, Power)
- [ ] Запиши 1 STAR-историю про сложный баг или архитектурное решение

---

## Фаза 2: Алгоритмы + Паттерны + System Design (Недели 4-6)

> Цель: освоить ключевые алгоритмы, паттерны решения задач и фундамент system design.

### Неделя 4 — DP, бэктрекинг и первые паттерны

**День 1**
- [ ] [[dynamic-programming]] ⏱ 30m
- [ ] [[patterns-overview]] ⏱ 10m

**День 2**
- [ ] [[backtracking]] ⏱ 20m
- [ ] [[two-pointers-pattern]] ⏱ 15m

**День 3**
- [ ] [[sliding-window-pattern]] ⏱ 15m
- [ ] [[api-design]] ⏱ 30m

**День 4**
- [ ] [[binary-search-pattern]] ⏱ 15m
- [ ] [[graph-algorithms]] ⏱ 25m

**День 5 — Review Day**
- [ ] Повтори: DP (top-down vs bottom-up), бэктрекинг, два указателя, скользящее окно
- [ ] Реши 3 задачи LeetCode: DP Easy/Medium (Climbing Stairs, Coin Change), Two Pointers (Container With Most Water)
- [ ] Нарисуй схему REST API design для знакомого проекта

---

### Неделя 5 — Графовые паттерны и архитектура

> [!tip] Архитектурные файлы длинные
> [[caching-strategies]] — 55 минут. Если времени мало, прочитай секции "When to cache" и "Eviction policies", остальное — потом.

**День 1**
- [ ] [[dfs-bfs-patterns]] ⏱ 20m
- [ ] [[dp-patterns]] ⏱ 20m

**День 2**
- [ ] [[topological-sort-pattern]] ⏱ 15m
- [ ] [[microservices-vs-monolith]] ⏱ 20m

**День 3**
- [ ] [[union-find-pattern]] ⏱ 15m
- [ ] [[caching-strategies]] ⏱ 55m

**День 4**
- [ ] [[monotonic-stack-pattern]] ⏱ 15m
- [ ] [[intervals-pattern]] ⏱ 15m

**День 5 — Review Day**
- [ ] Повтори: DFS/BFS паттерны, topological sort, Union-Find, monotonic stack
- [ ] Реши 3 задачи LeetCode: графы (Course Schedule — topological sort), интервалы (Merge Intervals), monotonic stack (Daily Temperatures)
- [ ] Спроектируй кэширование для мобильного приложения (используй заметки из [[caching-strategies]])

---

### Неделя 6 — Оставшиеся паттерны и распределённые системы

**День 1**
- [ ] [[top-k-elements-pattern]] ⏱ 15m
- [ ] [[k-way-merge-pattern]] ⏱ 15m

**День 2**
- [ ] [[two-heaps-pattern]] ⏱ 15m
- [ ] [[architecture-distributed-systems]] ⏱ 25m

**День 3**
- [ ] [[bit-manipulation]] ⏱ 20m
- [ ] [[databases-fundamentals-complete]] ⏱ 41m

**День 4**
- [ ] [[common-mistakes]] ⏱ 10m
- [ ] [[system-design-android]] ⏱ 15m

**День 5 — Review Day**
- [ ] Повтори: Top K, K-way merge, Two Heaps, bit manipulation, distributed systems
- [ ] Реши 3 задачи LeetCode: Top K (Kth Largest Element), Two Heaps (Find Median from Data Stream), Bit Manipulation (Single Number)
- [ ] Пройди мини system design: спроектируй offline-first мобильное приложение с синхронизацией

---

## Фаза 3: Практика + Мок-интервью + Поиск работы (Недели 7-8)

> Цель: закрепить все паттерны через практику, провести мок-интервью и подготовить резюме.

### Неделя 7 — Интенсив по практике

> [!tip] Переход к практике
> С этой недели акцент смещается с чтения на решение задач. Файлы — для ревизии, основное время — LeetCode.

**День 1**
- [ ] [[leetcode-roadmap]] ⏱ 15m — перечитай, выдели слабые паттерны
- [ ] Реши 3 задачи по слабым паттернам

**День 2**
- [ ] [[mock-interview-guide]] ⏱ 15m
- [ ] Проведи мок-интервью (coding, 45 мин) — используй Pramp или партнёра

**День 3**
- [ ] [[resume-strategy]] ⏱ 15m
- [ ] [[linkedin-optimization]] ⏱ 15m
- [ ] Реши 2 задачи LeetCode Medium

**День 4**
- [ ] [[negotiation]] ⏱ 15m
- [ ] Реши 3 задачи LeetCode (микс паттернов: DP + графы + sliding window)

**День 5 — Review Day**
- [ ] Повтори все паттерны: пройди [[patterns-overview]] и отметь уверенные/неуверенные
- [ ] Реши 2-3 задачи из неуверенных паттернов
- [ ] Обнови резюме и LinkedIn по заметкам из [[resume-strategy]]

---

### Неделя 8 — Финальная шлифовка

**День 1**
- [ ] Проведи полный мок coding интервью (2 задачи за 45 мин)
- [ ] Разбери ошибки, перечитай [[common-mistakes]]

**День 2**
- [ ] Проведи мок system design интервью (30 мин)
- [ ] Перечитай [[architecture-distributed-systems]] и [[caching-strategies]] — ключевые концепции

**День 3**
- [ ] Проведи мок behavioral интервью (30 мин)
- [ ] Перечитай [[behavioral-questions]] — проверь 5 подготовленных STAR-историй

**День 4**
- [ ] Финальная сессия LeetCode: реши 4 задачи Medium на время (15 мин каждая)
- [ ] Перечитай [[negotiation]] — подготовь диапазон зарплаты и аргументы

**День 5 — Финальный Review Day**
- [ ] Пройди весь этот файл сверху вниз — проверь все `[x]`
- [ ] Составь список слабых мест и план доработки
- [ ] Запусти процесс поиска по [[job-search-strategy]]

---

## Бонус: Недели 9-10 (по необходимости)

> Если до интервью есть ещё 2 недели — используй для углубления слабых зон.

### Неделя 9 — Углубление слабых паттернов

**День 1-2**
- [ ] Перерешай задачи, в которых ошибался на мок-интервью
- [ ] Перечитай соответствующие файлы паттернов

**День 3-4**
- [ ] Реши 2 задачи LeetCode Hard (DP + графы)
- [ ] Спроектируй 1 полный system design (чат-приложение или news feed)

**День 5 — Review Day**
- [ ] Мини мок-интервью: 1 coding + 1 behavioral вопрос
- [ ] Запиши уроки

### Неделя 10 — Прединтервью

**День 1-2**
- [ ] Лёгкая практика: 2 задачи Easy/Medium в день (поддержание формы)
- [ ] Перечитай [[se-interview-foundation]] — общий чек-лист

**День 3-4**
- [ ] Повтори STAR-истории вслух
- [ ] Перечитай [[system-design-android]] для платформенных вопросов

**День 5**
- [ ] Отдых. Хороший сон перед интервью важнее ещё одной задачи.

---

## Сводка по файлам

### CS Fundamentals — Структуры данных
| Файл | Время | Неделя |
|------|:-----:|:------:|
| [[big-o-complexity]] | 20m | 1 |
| [[problem-solving-framework]] | 15m | 1 |
| [[arrays-strings]] | 25m | 1 |
| [[linked-lists]] | 20m | 1 |
| [[stacks-queues]] | 20m | 1 |
| [[hash-tables]] | 20m | 2 |
| [[trees-binary]] | 25m | 2 |
| [[heaps-priority-queues]] | 20m | 2 |
| [[graphs]] | 25m | 2 |

### CS Fundamentals — Алгоритмы
| Файл | Время | Неделя |
|------|:-----:|:------:|
| [[sorting-algorithms]] | 25m | 3 |
| [[searching-algorithms]] | 20m | 3 |
| [[recursion-fundamentals]] | 15m | 3 |
| [[divide-and-conquer]] | 20m | 3 |
| [[greedy-algorithms]] | 20m | 3 |
| [[dynamic-programming]] | 30m | 4 |
| [[backtracking]] | 20m | 4 |
| [[graph-algorithms]] | 25m | 4 |

### CS Fundamentals — Паттерны
| Файл | Время | Неделя |
|------|:-----:|:------:|
| [[patterns-overview]] | 10m | 4 |
| [[two-pointers-pattern]] | 15m | 4 |
| [[sliding-window-pattern]] | 15m | 4 |
| [[binary-search-pattern]] | 15m | 4 |
| [[dfs-bfs-patterns]] | 20m | 5 |
| [[dp-patterns]] | 20m | 5 |
| [[topological-sort-pattern]] | 15m | 5 |
| [[union-find-pattern]] | 15m | 5 |
| [[monotonic-stack-pattern]] | 15m | 5 |
| [[intervals-pattern]] | 15m | 5 |
| [[top-k-elements-pattern]] | 15m | 6 |
| [[k-way-merge-pattern]] | 15m | 6 |
| [[two-heaps-pattern]] | 15m | 6 |
| [[bit-manipulation]] | 20m | 6 |

### CS Fundamentals — Интервью
| Файл | Время | Неделя |
|------|:-----:|:------:|
| [[leetcode-roadmap]] | 15m | 7 |
| [[common-mistakes]] | 10m | 6 |
| [[mock-interview-guide]] | 15m | 7 |

### Career — Процесс интервью
| Файл | Время | Неделя |
|------|:-----:|:------:|
| [[se-interview-foundation]] | 15m | 1 |
| [[interview-process]] | 15m | 1 |
| [[technical-interview]] | 16m | 2 |
| [[behavioral-interview]] | 15m | 1 |
| [[coding-challenges]] | 15m | 2 |
| [[negotiation]] | 15m | 7 |
| [[interview-tracking-system]] | 10m | 3 |

### Career — Поведенческие
| Файл | Время | Неделя |
|------|:-----:|:------:|
| [[behavioral-questions]] | 20m | 2 |
| [[ai-interview-preparation]] | 13m | 2 |
| [[ai-interview-prompts]] | 13m | 3 |

### Career — System Design (Архитектура)
| Файл | Время | Неделя |
|------|:-----:|:------:|
| [[api-design]] | 30m | 4 |
| [[microservices-vs-monolith]] | 20m | 5 |
| [[caching-strategies]] | 55m | 5 |
| [[architecture-distributed-systems]] | 25m | 6 |
| [[databases-fundamentals-complete]] | 41m | 6 |
| [[system-design-android]] | 15m | 6 |

### Career — Поиск работы
| Файл | Время | Неделя |
|------|:-----:|:------:|
| [[job-search-strategy]] | 15m | 3 |
| [[resume-strategy]] | 15m | 7 |
| [[linkedin-optimization]] | 15m | 7 |

---

## Общая статистика

| Метрика | Значение |
|---------|----------|
| Всего файлов | 53 |
| Общее время чтения | ~19 часов |
| Review Days | 8 (основных) + 2 (бонус) |
| LeetCode задач (минимум) | ~45-55 |
| Мок-интервью | 4-6 |
| Длительность | 8 недель (+ 2 бонусных) |

---

*Создано: 2026-02-14 | На основе методики interleaved practice из [[desirable-difficulties]] и [[deliberate-practice]]*

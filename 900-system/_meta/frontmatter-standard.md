---
title: "Стандарт Frontmatter"
created: 2026-02-09
modified: 2026-02-13
type: reference
status: published
confidence: high
tags:
  - system/guidelines
  - system/metadata
related:
  - "[[content-types]]"
  - "[[content-levels]]"
  - "[[tag-taxonomy]]"
---

# Стандарт Frontmatter

> Единый формат метаданных для каждого файла в базе знаний.

---

## Обязательные поля

Каждый `.md` файл (кроме README.md) должен содержать YAML frontmatter:

```yaml
---
title: "Читаемое название на русском"
created: YYYY-MM-DD
modified: YYYY-MM-DD
type: <тип контента>
tags:
  - topic/<домен>
  - type/<тип>
  - level/<уровень>
---
```

### Поля

| Поле | Тип | Обязательное | Описание |
|------|-----|:---:|----------|
| `title` | string | да | Человекочитаемое название. Русский язык. |
| `created` | date | да | Дата создания (YYYY-MM-DD) |
| `modified` | date | да | Дата последнего изменения |
| `type` | enum | да | Тип контента (см. таблицу ниже) |
| `tags` | list | да | Минимум 1 тег из `topic/` + 1 из `type/` |
| `status` | enum | нет | Состояние файла |
| `confidence` | enum | нет | Уверенность в актуальности |
| `review_date` | date | нет | Когда проверить актуальность (YYYY-MM-DD) |
| `related` | list | нет | 2-5 связанных файлов как `"[[wikilink]]"` |
| `prerequisites` | list | нет | Файлы, которые нужно прочитать перед этим |
| `reading_time` | number | нет | Время чтения в минутах (слов / 200) |
| `difficulty` | number | нет | Сложность 1-10 внутри уровня (level) |
| `study_status` | enum | нет | Статус изучения (см. таблицу ниже) |
| `mastery` | number | нет | Уровень усвоения 0-5 (self-assessment) |
| `last_reviewed` | date | нет | Дата последнего повторения |
| `next_review` | date | нет | Дата следующего повторения |

---

## Поля для обучения (Learning System)

Эти поля поддерживают систему активного обучения vault. Подробнее: [[learning-system-guide]]

### `reading_time`

Расчётное время чтения в минутах. Вычисляется автоматически: количество слов / 200 слов в минуту.

```yaml
reading_time: 25  # ~5000 слов
```

### `difficulty`

Сложность материала по шкале 1-10 внутри уровня (`level`). Позволяет упорядочить файлы одного уровня от простых к сложным.

```yaml
difficulty: 3   # простой для своего уровня
difficulty: 7   # сложный для своего уровня
```

### `study_status`

Статус изучения файла. Заполняется пользователем по мере обучения.

| Значение | Описание |
|----------|----------|
| `not_started` | Ещё не читал (значение по умолчанию) |
| `reading` | Сейчас читаю / в процессе |
| `reviewed` | Прочитал, прошёл "Проверь себя" |
| `mastered` | Усвоил, могу объяснить другому |

### `mastery`

Самооценка уровня усвоения по шкале Likert 0-5:

| Уровень | Описание |
|:-------:|----------|
| 0 | Не знаю (не читал) |
| 1 | Читал, мало помню |
| 2 | Помню основное |
| 3 | Могу объяснить коллеге |
| 4 | Могу применить на практике |
| 5 | Могу научить другого |

### `last_reviewed` и `next_review`

Даты для интервального повторения (Spaced Repetition). Заполняются пользователем или плагином.

```yaml
last_reviewed: 2026-02-13
next_review: 2026-02-20    # через неделю
```

Рекомендуемый график: 1 день → 3 дня → 1 неделя → 2 недели → 1 месяц. Подробнее: [[spaced-repetition-guide]]

---

## Допустимые значения `type`

| Значение | Когда использовать | Bloom Level |
|----------|-------------------|:-----------:|
| `deep-dive` | Глубокое погружение в тему (1000+ слов) | 4: Analyze |
| `concept` | Объяснение одной концепции (400-800 слов) | 2: Understand |
| `comparison` | Сравнение A vs B с решением | 5: Evaluate |
| `reference` | Справочник, cheat sheet (таблицы, команды) | 1: Remember |
| `tutorial` | Пошаговое руководство с проверками | 3: Apply |
| `guide` | Практическое руководство (шире tutorial) | 3: Apply |
| `overview` | Входная точка в область (~1 на область) | 2: Understand |
| `moc` | Map of Content — навигационный хаб | — |
| `index` | Глобальный индекс (только _index.md) | — |

**Устаревшие значения → замена:**

| Старое | Новое | Почему |
|--------|-------|--------|
| `note` | `concept` | Слишком размытое |
| `practical` | `tutorial` или `guide` | Неспецифичное |
| `Opaque` | `deep-dive` | Нестандартное |
| `textbook` | `deep-dive` | Дублирует |
| `foundational` | `concept` | Дублирует |
| `explainer` | `concept` | По сути то же |
| `system` | — | Убрать, использовать `system/*` тег |

---

## Допустимые значения `status`

| Значение | Описание |
|----------|----------|
| `published` | Готов к чтению, проверен |
| `draft` | В работе, может быть неполным |
| `needs-review` | Требует проверки или обновления |

**Устаревшие значения → замена:**

| Старое | Новое |
|--------|-------|
| `verified` | `published` |
| `complete` | `published` |
| `active` | `published` |
| `evergreen` | `published` |
| `draft \| review \| complete` | `published` |

---

## Допустимые значения `confidence`

| Значение | Описание |
|----------|----------|
| `high` | Проверено в нескольких источниках |
| `medium` | Основано на надёжных источниках, но не перепроверено |
| `low` | Предварительная информация, может быть неточной |

Числовые значения (`4`, `5`) → заменить на текстовые.

---

## Поле `review_date`

Рекомендуется для быстро меняющихся тем. Формат: `review_date: YYYY-MM-DD` -- дата, когда стоит проверить файл на актуальность.

**Когда добавлять:**

| Область | Интервал проверки | Почему |
|---------|:-----------------:|--------|
| AI/ML (модели, инструменты) | 3-6 месяцев | Ландшафт меняется ежемесячно |
| Career (зарплаты, рынок) | 6 месяцев | Данные устаревают быстро |
| Tools & Ecosystem | 6 месяцев | Версии, deprecated API |
| DevOps (CI/CD, облака) | 6-12 месяцев | Новые сервисы и практики |
| Architecture, CS Fundamentals | не нужно | Фундаментальные знания стабильны |

**Пример:**

```yaml
---
title: "AI Tools Ecosystem 2025"
created: 2025-12-15
modified: 2026-01-09
review_date: 2026-06-01
type: reference
confidence: medium
tags:
  - topic/ai-ml
  - type/reference
  - level/intermediate
---
```

Если `review_date` наступил и файл не обновлён, рекомендуется выставить `status: needs-review`.

---

## Формат тегов

Теги используют **namespace формат** с разделителем `/`:

```yaml
tags:
  - topic/android          # Область знаний
  - type/deep-dive         # Тип контента
  - level/intermediate     # Уровень сложности
```

Полная таксономия: [[tag-taxonomy]]

**Миграция:** плоские теги (`android`, `jvm`) → namespace (`topic/android`, `topic/jvm`).

---

## Формат `related`

Связанные файлы указываются как wikilinks в кавычках:

```yaml
related:
  - "[[kotlin-coroutines]]"
  - "[[android-threading]]"
  - "[[jvm-memory-model]]"
```

Правила:
- 2-5 файлов (рабочая память: 4±1)
- Только самые релевантные связи
- Предпочитать файлы из **других** областей (кросс-доменные связи ценнее)

---

## Примеры

### Deep-dive файл

```yaml
---
title: "JVM Garbage Collection: как работает сборка мусора"
created: 2025-11-25
modified: 2026-01-09
type: deep-dive
status: published
confidence: high
tags:
  - topic/jvm
  - type/deep-dive
  - level/intermediate
related:
  - "[[jvm-memory-model]]"
  - "[[android-process-memory]]"
  - "[[kotlin-coroutines]]"
prerequisites:
  - "[[jvm-overview]]"
reading_time: 30
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---
```

### MOC файл

```yaml
---
title: "Android MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/android
  - type/moc
  - navigation
---
```

### Overview файл

```yaml
---
title: "Security: обзор"
created: 2025-12-01
modified: 2026-01-09
type: overview
tags:
  - topic/security
  - type/overview
  - level/beginner
related:
  - "[[architecture-overview]]"
  - "[[networking-overview]]"
---
```

### Comparison файл

```yaml
---
title: "Монолит vs Микросервисы: что выбрать"
created: 2025-12-15
modified: 2026-01-09
type: comparison
status: published
confidence: high
tags:
  - topic/architecture
  - type/comparison
  - level/intermediate
related:
  - "[[api-design]]"
  - "[[docker-for-developers]]"
---
```

---

## Порядок массового обновления

1. MOC файлы (21 шт) — эталон
2. Overview файлы (21 шт)
3. По областям, начиная с крупнейших:
   - android/ (68 файлов)
   - cs-fundamentals/ (63 файла)
   - cs-foundations/ (61 файл)
   - ios/ (47 файлов)
   - leadership/ (44 файла)
   - jvm/ (37 файлов)
   - kmp/ (37 файлов)
   - ai-ml/ (33 файла)
   - career/ (30 файлов)
   - communication/ (26 файлов)
   - cross-platform/ (24 файлов)
   - networking/ (23 файла)
   - Остальные (<15 файлов каждая)
4. docs/research/ (71 файл) — последними

---

## Валидация

Frontmatter корректен, если:

```
[ ] Начинается с --- и заканчивается ---
[ ] title заполнен (не пустой)
[ ] created — валидная дата YYYY-MM-DD
[ ] type — одно из допустимых значений
[ ] tags — минимум 1 тег topic/* и 1 тег type/*
[ ] related — wikilinks в кавычках (если есть)
```

---

## Связанные файлы

- [[tag-taxonomy]] — полная таксономия тегов
- [[content-types]] — структуры для каждого типа контента
- [[content-levels]] — уровни качества (Bloom's Taxonomy)
- [[cognitive-science-rules]] — научные принципы создания контента
- [[learning-system-guide]] — как использовать vault для обучения
- [[spaced-repetition-guide]] — гайд по интервальному повторению

---

*Создано: 2026-02-09 | Обновлено: 2026-02-13 (добавлены поля Learning System)*

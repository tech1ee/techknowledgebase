---
title: "Стандарт Frontmatter"
created: 2026-02-09
modified: 2026-02-09
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
| `related` | list | нет | 2-5 связанных файлов как `"[[wikilink]]"` |
| `prerequisites` | list | нет | Файлы, которые нужно прочитать перед этим |

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
   - cs-foundations-kmp/ (61 файл)
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

---

*Создано: 2026-02-09*

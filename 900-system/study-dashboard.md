---
title: "Study Dashboard: дашборд обучения"
created: 2026-02-13
modified: 2026-02-13
type: reference
status: published
tags:
  - system/guidelines
  - system/metadata
  - navigation
related:
  - "[[learning-system-guide]]"
  - "[[spaced-repetition-guide]]"
  - "[[recommended-plugins]]"
  - "[[Home]]"
---

# Study Dashboard

> Визуальный дашборд прогресса обучения. Требует плагин **Dataview** для отображения таблиц.
> Без Dataview файл показывает code blocks с запросами — это нормально.

---

## Как пользоваться

1. Установи плагин **Dataview** (Settings → Community Plugins → Browse → Dataview)
2. Открой этот файл в Obsidian — таблицы отрисуются автоматически
3. Обновляй `study_status` и `mastery` в frontmatter файлов по мере обучения
4. Заходи сюда раз в день — видишь прогресс и что повторять

---

## Общий прогресс по областям

```dataview
TABLE WITHOUT ID
  split(file.folder, "/")[1] as "Область",
  length(rows) as "Всего",
  length(filter(rows, (r) => r.study_status = "mastered")) as "Освоено",
  length(filter(rows, (r) => r.study_status = "reviewed")) as "На повторении",
  length(filter(rows, (r) => r.study_status = "reading")) as "Читаю",
  round(length(filter(rows, (r) => r.study_status = "mastered" OR r.study_status = "reviewed")) / length(rows) * 100) + "%" as "Прогресс"
FROM "100-foundations" OR "200-platforms" OR "300-systems" OR "400-ai-ml" OR "500-craft"
WHERE type != "moc" AND type != "overview" AND type != "index"
GROUP BY split(file.folder, "/")[0]
SORT length(filter(rows, (r) => r.study_status = "mastered")) / length(rows) DESC
```

---

## Требуют повторения (SRS)

Файлы, у которых наступила дата следующего повторения:

```dataview
TABLE WITHOUT ID
  file.link as "Файл",
  reading_time + " мин" as "Время",
  mastery as "Mastery",
  last_reviewed as "Последний ревью",
  next_review as "Следующий ревью"
FROM "100-foundations" OR "200-platforms" OR "300-systems" OR "400-ai-ml" OR "500-craft"
WHERE next_review != null AND next_review <= date(today)
SORT next_review ASC
LIMIT 15
```

---

## Сейчас читаю

```dataview
TABLE WITHOUT ID
  file.link as "Файл",
  reading_time + " мин" as "Время",
  difficulty as "Сложность",
  split(file.folder, "/")[1] as "Область"
FROM "100-foundations" OR "200-platforms" OR "300-systems" OR "400-ai-ml" OR "500-craft"
WHERE study_status = "reading"
SORT file.mtime DESC
```

---

## Недавно изученное

```dataview
TABLE WITHOUT ID
  file.link as "Файл",
  study_status as "Статус",
  mastery as "Mastery",
  last_reviewed as "Ревью"
FROM "100-foundations" OR "200-platforms" OR "300-systems" OR "400-ai-ml" OR "500-craft"
WHERE last_reviewed != null
SORT last_reviewed DESC
LIMIT 15
```

---

## Ещё не начато (рекомендации)

Файлы с высоким приоритетом, которые ещё не изучены:

```dataview
TABLE WITHOUT ID
  file.link as "Файл",
  reading_time + " мин" as "Время",
  difficulty as "Сложность",
  split(file.folder, "/")[1] as "Область"
FROM "100-foundations" OR "200-platforms" OR "300-systems" OR "400-ai-ml" OR "500-craft"
WHERE study_status = "not_started" AND (type = "deep-dive" OR type = "concept")
SORT difficulty ASC
LIMIT 20
```

---

## Статистика mastery

```dataview
TABLE WITHOUT ID
  mastery as "Уровень Mastery",
  length(rows) as "Файлов"
FROM "100-foundations" OR "200-platforms" OR "300-systems" OR "400-ai-ml" OR "500-craft"
WHERE type != "moc" AND type != "overview" AND type != "index"
GROUP BY mastery
SORT mastery DESC
```

**Шкала mastery:**

| Уровень | Значение |
|:-------:|----------|
| 0 | Не знаю (не читал) |
| 1 | Читал, мало помню |
| 2 | Помню основное |
| 3 | Могу объяснить коллеге |
| 4 | Могу применить на практике |
| 5 | Могу научить другого |

---

## Как обновлять прогресс

После изучения файла обнови его frontmatter:

```yaml
study_status: reviewed    # было: not_started или reading
mastery: 3                # оцени честно (0-5)
last_reviewed: 2026-02-13 # сегодняшняя дата
next_review: 2026-02-20   # через неделю (или по графику SRS)
```

График повторений:
- Первый раз → следующий день
- Второй раз → через 3 дня
- Третий раз → через 1 неделю
- Четвёртый раз → через 2 недели
- Пятый раз → через 1 месяц

Подробнее: [[spaced-repetition-guide]]

---

## Связанные файлы

- [[learning-system-guide]] — как использовать vault для обучения
- [[spaced-repetition-guide]] — подробный гайд по интервальному повторению
- [[recommended-plugins]] — какие плагины установить
- [[Home]] — главная страница vault

---

*Создано: 2026-02-13*

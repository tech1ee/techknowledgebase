# NotebookLM Export

Этот раздел содержит контент базы знаний, оптимизированный для Google NotebookLM.

## Особенности формата

Контент трансформирован из технической документации в **prose-first формат**:

- Код заменён на словесные объяснения
- ASCII диаграммы заменены на описания потоков
- Таблицы преобразованы в сравнительную прозу
- Структура оптимизирована для Audio Overview

## Структура notebooks

| Папка | Тема | Файлов | Для кого |
|-------|------|--------|----------|
| 01-ios-development | iOS разработка | 5 | iOS разработчикам |
| 02-android-development | Android разработка | 5 | Android разработчикам |
| 03-cross-platform | iOS vs Android + KMP | 6 | Мультиплатформенникам |
| 04-cs-theory | Теория CS | 4 | Всем разработчикам |
| 05-backend-infrastructure | Backend и DevOps | 4 | Backend инженерам |
| 06-ai-ml | AI и Machine Learning | 3 | AI инженерам |
| 07-career-growth | Карьера и soft skills | 3 | Всем |
| 08-architecture | Архитектура систем | 3 | Архитекторам |

## Как использовать

### Шаг 1: Создать notebooks в NotebookLM

Создайте 8 отдельных notebooks по темам:
1. iOS Development
2. Android Development
3. Cross-Platform Comparison
4. Computer Science Theory
5. Backend & Infrastructure
6. AI/ML Engineering
7. Career Growth
8. Software Architecture

### Шаг 2: Загрузить файлы

В каждый notebook загрузите соответствующие markdown файлы из папки.

### Шаг 3: Использовать функции NotebookLM

**Audio Overview:**
- Выберите один или несколько sources
- Нажмите "Generate Audio Overview"
- Выберите формат: Deep Dive, Brief, или Lecture

**Chat:**
- Задавайте вопросы по теории
- Запрашивайте сравнения
- Просите объяснить концепции

## Рекомендации

### Для Audio Overview

Лучше работает с отдельными файлами, а не со всеми сразу.
Рекомендуемый порядок для изучения iOS:

1. ios-memory-arc.md — понять ARC
2. ios-lifecycle-architecture.md — понять структуру
3. ios-ui-frameworks.md — SwiftUI vs UIKit
4. ios-async-concurrency.md — concurrency
5. ios-data-build.md — практика

### Для Chat

Примеры полезных вопросов:
- "Объясни разницу между ARC и Garbage Collection"
- "Когда использовать weak, а когда unowned?"
- "Почему iOS использует детерминированный подход к памяти?"
- "Сравни SwiftUI и Compose по философии"

## Источники

Контент создан на основе базы знаний Tech Knowledge Base (515+ файлов).
Оригинальная документация находится в разделах:
- /ios/ — 45 файлов
- /android/ — 46 файлов
- /cross-platform/ — 24 файла
- /cs-fundamentals/ — 57 файлов
- и других

## Обновления

Последнее обновление: 2026-01-12

При обновлении оригинальной базы знаний, экспорт нужно пересоздать.

---
title: "Что нового в базе знаний"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Что нового

История изменений базы знаний.

---

## Февраль 2026

### Реорганизация (2026-02-14)
- Зонная структура: 100-foundations/, 200-platforms/, 300-systems/, 400-ai-ml/, 500-craft/
- 35+ новых навигационных файлов (точки входа)
- Обновлены Dataview-запросы, README, Home
- Добавлены навигационные файлы:
  - **Проблемные гайды (5):** производительность, интервью, команда, архитектура, масштабирование кода
  - **Деревья решений (5):** DI-фреймворк, архитектурный паттерн, база данных, кросс-платформа, стиль API
  - **Гайды сборки (4):** Android-приложение, iOS-приложение, KMP-библиотека, AI-фича
  - **Интервью-бандлы (3):** Android Senior, System Design, Behavioral/Leadership

### Аудит и стандартизация (2026-02-09)
- Frontmatter: 94% (702/750 файлов), было 52%
- 21 MOC покрывает все области
- Навигация: Home.md → 21 MOC → 20 overviews → 640+ content files
- Исправлено: 40 битых ссылок в навигационных файлах
- Удалено: 300-content/ (318 MB), _notebooklm-export/ (214 файлов), main-index.md (дубликат)
- Создано: frontmatter-standard.md, tag-taxonomy.md (topic/type/level namespaces)
- Оставшиеся без frontmatter: 48 файлов (38 research-архивы + 10 шаблонов/README)

---

## Январь 2026

### CS Foundations KMP (2026-01-04 — 2026-01-05)
- 61 файл: memory, compilation, concurrency, type systems, platform interop
- Research-документы для каждого файла
- Связь с KMP: как CS-концепции проявляются в Kotlin Multiplatform

### Kotlin Multiplatform (2026-01-03 — 2026-01-04)
- 70 файлов с research-документами
- 10 разделов: fundamentals, platforms, Compose MP, architecture, libraries, testing, build, migration, advanced, production
- Полное покрытие: от getting started до production checklist

### iOS (2026-01-02 — 2026-01-03)
- 45 файлов
- 9 разделов: fundamentals, SwiftUI, UIKit, concurrency, architecture, data, rendering, build, system
- Параллели с Android для cross-reference

### Communication (2026-01-01 — 2026-01-02)
- 26 файлов
- 8 разделов: fundamentals, listening, feedback, difficult conversations, negotiation, presentations, written, cross-cultural

### Learning Paths (2026-01-05)
- 11 учебных маршрутов
- 6 по областям (Android, iOS, KMP, CS Foundations, CS Fundamentals, JVM)
- 5 interleaved (Mobile Expert, Interview Prep, Backend Engineer, Full-Stack Foundation, Tech Lead)

---

## Декабрь 2025

### Android (2025-12-25 — 2025-12-30)
- Завершение 100+ файлов Android-раздела
- 10 разделов: fundamentals, lifecycle, UI Views, Compose, architecture, DI, async, data, build, quality
- Research-документы для UI и performance

### CS Fundamentals (2025-12-29)
- Data structures: 12 файлов (arrays, linked lists, trees, graphs, heaps, hash tables, etc.)
- Algorithms: 15 файлов (sorting, searching, DP, graphs, etc.)
- Patterns: 16 файлов (sliding window, two pointers, DFS/BFS, etc.)
- Interview prep: LeetCode roadmap, mock interview guide

### Career (2025-12-26 — 2025-12-30)
- Interview preparation: behavioral, coding, system design
- Job search: стратегия, нетворкинг, LinkedIn
- Market analysis: Android market 2025, salary benchmarks
- Regions: Austria, Netherlands, Switzerland, UAE

### Databases (2025-12-30)
- 15 файлов: fundamentals, SQL, NoSQL, mobile, cloud, AI/ML
- Design, optimization, transactions, replication, sharding

---

## Навигация по базе
- [[Home]] — главная страница
- [[android-moc]] — Android
- [[ios-moc]] — iOS
- [[kmp-moc]] — Kotlin Multiplatform
- [[cs-fundamentals-moc]] — CS Fundamentals
- [[ai-engineering-moc]] — AI Engineering
- [[architecture-moc]] — Architecture
- [[leadership-moc]] — Leadership
- [[career-moc]] — Career

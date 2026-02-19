---
title: "Роль: Мобильный разработчик"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Роль: Мобильный разработчик (Android / iOS / KMP)

> Портал для мобильного разработчика. Все ключевые области, приоритеты и порядок изучения.

---

## Основные области

| Область | Файлов | Приоритет | Обзор |
|---------|--------|-----------|-------|
| Android | 70 | **Критический** | [[android-overview]] |
| iOS | 45 | **Критический** | [[ios-overview]] |
| Kotlin Multiplatform | 70 | **Высокий** | [[kmp-overview]] |
| Cross-Platform | 24 | **Высокий** | [[cross-platform-overview]] |
| CS Fundamentals (алгоритмы) | 63 | **Высокий** | [[cs-fundamentals-overview]] |

---

## Поддерживающие области

| Область | Файлов | Зачем мобильнику | Обзор |
|---------|--------|-------------------|-------|
| Architecture | 16 | Паттерны проектирования, API, кеширование | [[architecture-overview]] |
| Security (mobile) | 19 | OWASP Mobile, защита приложений, шифрование | [[security-overview]] |
| Databases (Room/CoreData) | 16 | Локальные БД, миграции, производительность | [[databases-overview]] |
| Networking | 23 | HTTP, WebSocket, оптимизация трафика | [[networking-overview]] |
| JVM / Kotlin | 37 | Корутины, Flow, JVM-внутренности | [[jvm-overview]] |
| Programming (теория) | 12 | SOLID, паттерны, тестирование | [[programming-overview]] |
| CS Foundations (системы) | 23 | Память, компиляция, конкурентность | [[cs-foundations-overview]] |

---

## Области для пропуска (на текущем этапе)

| Область | Когда подключить |
|---------|------------------|
| Cloud (7 файлов) | Когда понадобится backend-компетенция или BaaS |
| DevOps (10 файлов) | Кроме [[ci-cd-pipelines]] и [[android-ci-cd]] / [[ios-ci-cd]] |
| Leadership (44 файла) | Когда перейдёшь на Tech Lead трек -- см. [[role-tech-lead]] |
| AI/ML (44 файла) | Когда понадобится on-device ML или AI-фичи |

---

## Топ-15 файлов для мобильного разработчика

Самые важные файлы из всех областей -- начни с них:

| # | Файл | Область | Почему важно |
|---|------|---------|--------------|
| 1 | [[android-architecture-patterns]] | Android | MVVM, MVI, Clean Architecture |
| 2 | [[kotlin-coroutines]] | JVM/Kotlin | Основа асинхронности в Android/KMP |
| 3 | [[kotlin-flow]] | JVM/Kotlin | Реактивные потоки данных |
| 4 | [[android-compose-internals]] | Android | Как работает Compose под капотом |
| 5 | [[ios-swiftui]] | iOS | Современный UI-фреймворк Apple |
| 6 | [[android-dependency-injection]] | Android | DI -- фундамент тестируемого кода |
| 7 | [[kmp-getting-started]] | KMP | Вход в мультиплатформенную разработку |
| 8 | [[android-app-startup-performance]] | Android | Оптимизация старта приложения |
| 9 | [[android-memory-leaks]] | Android | Утечки памяти -- #1 проблема в продакшене |
| 10 | [[patterns-overview]] | CS Fundamentals | 14 паттернов решения задач |
| 11 | [[solid-principles]] | Programming | Принципы чистого кода |
| 12 | [[android-testing]] | Android | Стратегии тестирования |
| 13 | [[ios-architecture-patterns]] | iOS | MVVM, VIPER, TCA для iOS |
| 14 | [[android-navigation]] | Android | Навигация в Android-приложениях |
| 15 | [[mobile-security-owasp]] | Security | OWASP Mobile Top 10 |

---

## Рекомендуемые траектории обучения

### По платформам

- [[android-learning-path]] -- пошаговый план изучения Android
- [[ios-learning-path]] -- пошаговый план изучения iOS
- [[kmp-learning-path]] -- пошаговый план изучения Kotlin Multiplatform

### Алгоритмы и собеседования

- [[cs-fundamentals-learning-path]] -- алгоритмы и структуры данных

### Комплексный маршрут

- [[interleaved-mobile-expert]] -- интерливинг-маршрут для мобильного эксперта (чередование Android/iOS/KMP/CS)

---

## Порядок изучения для новичка

```
1. Основы языка
   Kotlin: [[kotlin-basics]] → [[kotlin-oop]] → [[kotlin-functional]]
   Swift:  [[ios-overview]] → [[ios-swiftui]]

2. Платформа
   Android: [[android-overview]] → [[android-app-components]] → [[android-activity-lifecycle]]
   iOS:     [[ios-app-components]] → [[ios-viewcontroller-lifecycle]]

3. UI
   Android: [[android-ui-views]] → [[android-compose]]
   iOS:     [[ios-uikit-fundamentals]] → [[ios-swiftui]]

4. Архитектура
   [[android-architecture-patterns]] / [[ios-architecture-patterns]]
   [[android-viewmodel-internals]] / [[ios-viewmodel-patterns]]
   [[android-dependency-injection]] / [[ios-dependency-injection]]

5. Асинхронность
   [[kotlin-coroutines]] → [[kotlin-flow]]
   [[ios-async-await]] → [[ios-combine]]

6. Данные
   [[android-room-deep-dive]] / [[ios-core-data]]
   [[android-networking]] / [[ios-networking]]

7. Качество
   [[android-testing]] / [[ios-testing]]
   [[android-memory-leaks]] → [[android-performance-profiling]]

8. Продвинутое
   [[kmp-getting-started]] → [[kmp-project-structure]]
   [[compose-mp-overview]]

9. Platform Internals (Deep Dive)
   [[android-internals-overview]] → [[android-binder-ipc]] → [[android-boot-process]]
   [[android-art-runtime]] → [[android-system-services]] → [[android-activitythread-internals]]
```

---

## Связанные файлы

- [[Home]] -- главная навигация
- [[maturity-ladder]] -- лестница компетенций мобильного разработчика
- [[quick-reference]] -- топ-30 файлов для быстрого доступа
- [[study-dashboard]] -- дашборд прогресса обучения

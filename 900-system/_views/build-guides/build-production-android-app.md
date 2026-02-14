---
title: "Сборка: Продакшн Android-приложение"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Продакшн Android-приложение

Полный чеклист: от создания проекта до мониторинга в продакшене.

---

## Фаза 1: Настройка проекта

### Структура и конфигурация
- [[android-project-structure]] — структура проекта
- [[android-gradle-fundamentals]] — настройка Gradle
- [[android-dependencies]] — управление зависимостями
- [[android-manifest]] — конфигурация манифеста
- [[android-resources-system]] — ресурсная система

### Архитектура
- [[android-architecture-patterns]] — выбор паттерна (MVVM / MVI / Clean)
- [[android-modularization]] — модульная структура
- [[android-dependency-injection]] — настройка DI
- [[android-hilt-deep-dive]] или [[android-koin-deep-dive]] — конкретный фреймворк

### Чеклист
- [ ] Gradle: version catalog, build variants, signing configs
- [ ] Модули: app, core, feature-*, data-*
- [ ] DI: Hilt/Koin setup
- [ ] .editorconfig, ktlint, detekt

---

## Фаза 2: UI

### Compose
- [[android-compose]] — основы Jetpack Compose
- [[android-compose-internals]] — как работает Compose внутри
- [[android-state-management]] — управление состоянием
- [[android-navigation]] — навигация между экранами
- [[android-animations]] — анимации

### View System (если нужен)
- [[android-ui-views]] — система View
- [[android-recyclerview-internals]] — RecyclerView
- [[android-custom-view-fundamentals]] — кастомные View
- [[android-view-rendering-pipeline]] — pipeline рендеринга

### Чеклист
- [ ] Design system: тема, цвета, типографика, компоненты
- [ ] Навигация: single Activity, Compose Navigation
- [ ] Состояние: StateFlow / State в Compose
- [ ] Адаптивный UI: разные размеры экранов

---

## Фаза 3: Данные

### Хранение
- [[android-data-persistence]] — обзор подходов
- [[android-room-deep-dive]] — Room для структурированных данных
- [[android-datastore-guide]] — DataStore для настроек
- [[android-room-migrations]] — миграции Room
- [[android-room-performance]] — оптимизация запросов

### Сеть
- [[android-networking]] — сетевой слой (Retrofit, OkHttp, Ktor)
- [[android-repository-pattern]] — паттерн Repository

### Чеклист
- [ ] Room: entities, DAOs, database, миграции
- [ ] DataStore: настройки пользователя
- [ ] Networking: Retrofit/Ktor, interceptors, error handling
- [ ] Repository: single source of truth
- [ ] Offline-first стратегия (если нужна)

---

## Фаза 4: Фоновая работа и производительность

### Background
- [[android-background-work]] — WorkManager, AlarmManager, Services
- [[android-service-internals]] — работа с сервисами
- [[android-handler-looper]] — Handler/Looper
- [[android-coroutines-mistakes]] — ошибки с корутинами

### Производительность
- [[android-app-startup-performance]] — оптимизация запуска
- [[android-memory-leaks]] — предотвращение утечек памяти
- [[android-process-memory]] — управление памятью процесса

### Чеклист
- [ ] WorkManager для периодических задач
- [ ] Baseline Profiles для ускорения запуска
- [ ] LeakCanary в debug-сборках
- [ ] StrictMode в debug-сборках

---

## Фаза 5: Качество

### Тестирование
- [[android-testing]] — стратегия тестирования
  - Unit тесты: JUnit, Mockk, Turbine
  - UI тесты: Compose Testing, Espresso
  - Integration тесты: Robolectric

### Безопасность
- [[android-permissions-security]] — разрешения и безопасность
- [[mobile-security-owasp]] — OWASP Mobile Top 10
- [[mobile-app-protection]] — защита приложения
- [[android-proguard-r8]] — обфускация и оптимизация

### Чеклист
- [ ] Unit тесты: покрытие > 70% для domain/data
- [ ] UI тесты: критические сценарии
- [ ] ProGuard/R8: правила, тестирование release-сборки
- [ ] Security: Certificate Pinning, encrypted storage
- [ ] Accessibility: TalkBack, content descriptions

---

## Фаза 6: Сборка и деплой

### Сборка
- [[android-apk-aab]] — форматы APK и AAB
- [[android-compilation-pipeline]] — pipeline компиляции
- [[android-build-evolution]] — эволюция систем сборки

### CI/CD
- [[android-ci-cd]] — CI/CD для Android
- [[git-workflows]] — Git-воркфлоу (trunk-based, GitFlow)

### Чеклист
- [ ] Signing: release keystore, Play App Signing
- [ ] Build variants: debug, staging, release
- [ ] CI: lint, tests, build на каждый PR
- [ ] CD: автоматический деплой в Internal Testing
- [ ] AAB: App Bundle для Play Store

---

## Фаза 7: Мониторинг

### Наблюдаемость
- [[observability]] — мониторинг и observability
- [[android-notifications]] — push-уведомления
- [[android-performance-profiling]] — профилирование

### Чеклист
- [ ] Crash reporting: Firebase Crashlytics
- [ ] Analytics: события, воронки, retention
- [ ] Performance monitoring: ANR, slow renders
- [ ] Push notifications: FCM setup
- [ ] Feature flags: remote config

---

## Связанные материалы
- [[android-overview]] — обзор Android-разработки
- [[android-moc]] — карта знаний Android
- [[android-architecture-evolution]] — эволюция архитектуры
- [[kotlin-overview]] — обзор Kotlin
- [[kotlin-coroutines]] — корутины
- [[kotlin-flow]] — Flow

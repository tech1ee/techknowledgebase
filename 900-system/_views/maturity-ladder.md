---
title: "Лестница компетенций мобильного разработчика"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Лестница компетенций мобильного разработчика

> Самооценка уровня компетенций. 5 уровней от Junior до Principal. Каждый уровень -- чеклист файлов для изучения и проверка знаний.

---

## Как пользоваться

1. Найди свой текущий уровень -- прочитай "Ты можешь" и честно оцени
2. Отмечай `[x]` файлы, которые проработал
3. "Проверка пробелов" -- если не можешь объяснить тему, начни с указанного файла
4. Не перескакивай уровни -- каждый следующий строится на предыдущем

---

## Level 1: Foundation Builder (Junior, 0-1 год)

### Ты можешь:

- Создать простой экран с UI-элементами (кнопки, списки, формы)
- Сделать API-запрос и отобразить данные
- Реализовать простую навигацию между экранами
- Понимать жизненный цикл Activity / UIViewController
- Написать простой unit-тест
- Использовать Git для основных операций

### Файлы для изучения:

**Платформа:**
- [ ] [[android-overview]] -- обзор платформы Android
- [ ] [[android-app-components]] -- компоненты приложения: Activity, Service, Receiver, Provider
- [ ] [[android-activity-lifecycle]] -- жизненный цикл Activity
- [ ] [[android-project-structure]] -- структура Android-проекта
- [ ] [[android-manifest]] -- AndroidManifest.xml
- [ ] [[android-resources-system]] -- ресурсы: layout, drawable, values
- [ ] [[android-ui-views]] -- базовые View и ViewGroup
- [ ] [[android-navigation]] -- навигация между экранами
- [ ] [[ios-overview]] -- обзор платформы iOS
- [ ] [[ios-app-components]] -- компоненты iOS-приложения
- [ ] [[ios-viewcontroller-lifecycle]] -- жизненный цикл UIViewController

**Язык:**
- [ ] [[kotlin-basics]] -- основы Kotlin
- [ ] [[kotlin-oop]] -- ООП в Kotlin
- [ ] [[kotlin-collections]] -- коллекции Kotlin

**Основы CS:**
- [ ] [[arrays-strings]] -- массивы и строки
- [ ] [[hash-tables]] -- хеш-таблицы
- [ ] [[big-o-complexity]] -- анализ сложности
- [ ] [[problem-solving-framework]] -- фреймворк решения задач

**Программирование:**
- [ ] [[clean-code-solid]] -- чистый код и SOLID

### Проверка пробелов:

> Если не можешь объяснить, что происходит при повороте экрана -- начни с [[android-activity-lifecycle]]
> Если не знаешь разницу между `val` и `var` -- начни с [[kotlin-basics]]
> Если путаешь O(n) и O(n^2) -- начни с [[big-o-complexity]]

---

## Level 2: Capable Contributor (Middle, 1-3 года)

### Ты можешь:

- Реализовать фичу от начала до конца (UI + логика + данные + тесты)
- Использовать архитектурный паттерн (MVVM или MVI)
- Работать с локальной базой данных (Room / CoreData)
- Написать интеграционные тесты
- Оптимизировать RecyclerView / List performance
- Понимать dependency injection и использовать DI-фреймворк

### Файлы для изучения:

**Архитектура:**
- [ ] [[android-architecture-patterns]] -- MVVM, MVI, Clean Architecture
- [ ] [[android-viewmodel-internals]] -- ViewModel: как работает под капотом
- [ ] [[android-repository-pattern]] -- паттерн Repository
- [ ] [[ios-architecture-patterns]] -- паттерны архитектуры в iOS
- [ ] [[ios-viewmodel-patterns]] -- ViewModel-паттерны в iOS

**UI:**
- [ ] [[android-compose]] -- Jetpack Compose: основы
- [ ] [[android-recyclerview-internals]] -- RecyclerView: внутренности и оптимизация
- [ ] [[ios-swiftui]] -- SwiftUI: декларативный UI
- [ ] [[ios-uikit-fundamentals]] -- UIKit: фундаментальные концепции

**Данные:**
- [ ] [[android-room-deep-dive]] -- Room: deep dive
- [ ] [[android-networking]] -- Retrofit, OkHttp, сериализация
- [ ] [[ios-core-data]] -- Core Data
- [ ] [[ios-networking]] -- URLSession, Alamofire

**Асинхронность:**
- [ ] [[kotlin-coroutines]] -- Kotlin Coroutines
- [ ] [[kotlin-flow]] -- Kotlin Flow
- [ ] [[ios-async-await]] -- Swift async/await
- [ ] [[android-threading]] -- потоки и конкурентность в Android

**DI:**
- [ ] [[android-dependency-injection]] -- обзор DI в Android
- [ ] [[android-hilt-deep-dive]] -- Hilt: deep dive
- [ ] [[ios-dependency-injection]] -- DI в iOS

**Тестирование:**
- [ ] [[android-testing]] -- стратегии тестирования Android
- [ ] [[ios-testing]] -- тестирование в iOS
- [ ] [[testing-strategies]] -- общие стратегии тестирования

**Паттерны (алгоритмы):**
- [ ] [[patterns-overview]] -- обзор паттернов решения задач
- [ ] [[two-pointers-pattern]] -- два указателя
- [ ] [[sliding-window-pattern]] -- скользящее окно
- [ ] [[binary-search-pattern]] -- бинарный поиск
- [ ] [[dfs-bfs-patterns]] -- DFS и BFS

### Проверка пробелов:

> Если не можешь объяснить разницу между `StateFlow` и `SharedFlow` -- начни с [[kotlin-flow]]
> Если ViewModel переживает поворот экрана, но не знаешь почему -- начни с [[android-viewmodel-internals]]
> Если DI -- "магия" для тебя -- начни с [[dependency-injection-fundamentals]]

---

## Level 3: Independent Expert (Senior, 3-5 лет)

### Ты можешь:

- Проектировать архитектуру нового модуля / приложения
- Оптимизировать производительность (запуск, рендеринг, память)
- Проводить code review и менторить джуниоров
- Решать system design задачи на собеседованиях
- Понимать внутренности фреймворков (Compose, SwiftUI)
- Работать с CI/CD pipeline

### Файлы для изучения:

**Глубокие знания платформы:**
- [ ] [[android-compose-internals]] -- Compose: recomposition, snapshot system
- [ ] [[android-state-management]] -- управление состоянием в Compose
- [ ] [[android-view-rendering-pipeline]] -- rendering pipeline: measure → layout → draw
- [ ] [[android-touch-handling]] -- обработка касаний
- [ ] [[android-window-system]] -- оконная система Android
- [ ] [[ios-view-rendering]] -- рендеринг в iOS
- [ ] [[ios-state-management]] -- управление состоянием SwiftUI

**Производительность:**
- [ ] [[android-app-startup-performance]] -- оптимизация запуска приложения
- [ ] [[android-memory-leaks]] -- утечки памяти: поиск и устранение
- [ ] [[android-performance-profiling]] -- профилирование: Android Studio Profiler
- [ ] [[android-process-memory]] -- процессы и память в Android
- [ ] [[ios-performance-profiling]] -- профилирование в Xcode Instruments
- [ ] [[ios-scroll-performance]] -- производительность скроллинга

**Мультиплатформа:**
- [ ] [[kmp-getting-started]] -- KMP: начало работы
- [ ] [[kmp-project-structure]] -- структура KMP-проекта
- [ ] [[kmp-architecture-patterns]] -- архитектурные паттерны KMP
- [ ] [[compose-mp-overview]] -- Compose Multiplatform

**Build и CI/CD:**
- [ ] [[android-gradle-fundamentals]] -- Gradle: основы
- [ ] [[android-proguard-r8]] -- ProGuard / R8: обфускация и оптимизация
- [ ] [[android-ci-cd]] -- CI/CD для Android
- [ ] [[ios-xcode-fundamentals]] -- Xcode: основы сборки
- [ ] [[ios-ci-cd]] -- CI/CD для iOS

**System Design:**
- [ ] [[system-design-android]] -- system design для мобильных
- [ ] [[architecture-distributed-systems]] -- распределённые системы
- [ ] [[caching-strategies]] -- стратегии кеширования

**Безопасность:**
- [ ] [[mobile-security-owasp]] -- OWASP Mobile Top 10
- [ ] [[mobile-app-protection]] -- защита мобильных приложений
- [ ] [[android-permissions-security]] -- разрешения и безопасность Android

**Продвинутые паттерны:**
- [ ] [[dp-patterns]] -- Dynamic Programming паттерны
- [ ] [[graph-algorithms]] -- алгоритмы на графах
- [ ] [[topological-sort-pattern]] -- топологическая сортировка

### Проверка пробелов:

> Если не можешь объяснить, почему Compose перерисовывает лишнее -- начни с [[android-compose-internals]]
> Если не знаешь, как найти утечку памяти в продакшене -- начни с [[android-memory-leaks]]
> Если system design вызывает страх -- начни с [[system-design-android]]

---

## Level 4: Technical Leader (Staff, 5-8 лет)

### Ты можешь:

- Влиять на архитектурные решения на уровне нескольких команд
- Принимать решения о технологическом стеке
- Проводить технические презентации для нетехнической аудитории
- Менторить Senior-разработчиков
- Управлять техническим долгом как стратегией
- Вести cross-team инициативы

### Файлы для изучения:

**Лидерство:**
- [ ] [[tech-lead-role]] -- роль техлида
- [ ] [[ic-vs-management]] -- IC vs менеджмент
- [ ] [[architecture-decisions]] -- ADR: принятие архитектурных решений
- [ ] [[technical-vision]] -- формулирование технического видения
- [ ] [[tech-debt-management]] -- управление техническим долгом
- [ ] [[delegation]] -- делегирование
- [ ] [[one-on-one-meetings]] -- проведение 1:1
- [ ] [[staff-plus-engineering]] -- Staff+ Engineering

**Коммуникация:**
- [ ] [[stakeholder-management]] -- работа со стейкхолдерами
- [ ] [[technical-presentations]] -- технические презентации
- [ ] [[conflict-resolution]] -- разрешение конфликтов
- [ ] [[giving-feedback]] -- обратная связь
- [ ] [[executive-communication]] -- коммуникация с руководством

**Глубокие системные знания:**
- [ ] [[android-compilation-pipeline]] -- конвейер компиляции Android
- [ ] [[android-modularization]] -- модуляризация приложения
- [ ] [[ios-compilation-pipeline]] -- конвейер компиляции iOS
- [ ] [[ios-modularization]] -- модуляризация iOS-приложения
- [ ] [[kmp-gradle-deep-dive]] -- Gradle для KMP: deep dive

**Мышление:**
- [ ] [[mental-models]] -- ментальные модели
- [ ] [[systems-thinking]] -- системное мышление
- [ ] [[deep-work]] -- глубокая работа
- [ ] [[cognitive-biases]] -- когнитивные искажения

**Команда:**
- [ ] [[hiring-engineers]] -- найм инженеров
- [ ] [[building-engineering-team]] -- построение команды
- [ ] [[team-culture]] -- культура команды
- [ ] [[onboarding]] -- онбординг

### Проверка пробелов:

> Если не можешь обосновать архитектурное решение документом -- начни с [[architecture-decisions]]
> Если 1:1 -- "как дела?" и молчание -- начни с [[one-on-one-meetings]]
> Если не можешь объяснить CTO, зачем нужен рефакторинг -- начни с [[stakeholder-management]]

---

## Level 5: Organizational Strategist (Principal+, 8+ лет)

### Ты можешь:

- Определять техническую стратегию на уровне организации
- Влиять на продуктовую стратегию через технические возможности
- Формировать инженерную культуру
- Масштабировать команды и процессы
- Принимать решения с неполной информацией и высокой неопределённостью
- Управлять бюджетом и ресурсами

### Файлы для изучения:

**Стратегия и организация:**
- [ ] [[cto-vs-vpe]] -- CTO vs VP Engineering
- [ ] [[scaling-engineering-org]] -- масштабирование инженерной организации
- [ ] [[team-structures]] -- структуры команд
- [ ] [[engineering-metrics]] -- метрики инженерии (DORA, SPACE)
- [ ] [[okrs-kpis]] -- OKR и KPI
- [ ] [[budget-planning]] -- планирование бюджета
- [ ] [[strategic-thinking]] -- стратегическое мышление

**Startup / Scale-up:**
- [ ] [[startup-cto]] -- роль CTO в стартапе
- [ ] [[scaling-from-zero]] -- масштабирование с нуля
- [ ] [[founding-engineer]] -- founding engineer
- [ ] [[technical-due-diligence]] -- техническая due diligence

**Кризис и влияние:**
- [ ] [[crisis-management]] -- управление кризисами
- [ ] [[executive-communication]] -- коммуникация на уровне C-level
- [ ] [[negotiation-fundamentals]] -- переговоры
- [ ] [[stakeholder-negotiation]] -- переговоры со стейкхолдерами

**Процессы:**
- [ ] [[development-process]] -- организация процессов разработки
- [ ] [[engineering-practices]] -- инженерные практики
- [ ] [[agile-practices]] -- Agile-практики
- [ ] [[performance-management]] -- управление производительностью

**Найм и рост:**
- [ ] [[interview-process-design]] -- дизайн интервью-процесса
- [ ] [[making-offers]] -- формирование офферов
- [ ] [[sourcing-candidates]] -- поиск кандидатов
- [ ] [[leadership-interviews]] -- собеседования на лидерские позиции
- [ ] [[motivation]] -- мотивация инженеров

### Проверка пробелов:

> Если не можешь сформулировать техническую стратегию на год -- начни с [[technical-vision]]
> Если не знаешь, как масштабировать команду с 5 до 50 -- начни с [[scaling-engineering-org]]
> Если бюджет -- terra incognita -- начни с [[budget-planning]]

---

## Общий прогресс

| Уровень | Файлов | Ты здесь? |
|---------|--------|-----------|
| Level 1: Foundation Builder | 19 | |
| Level 2: Capable Contributor | 26 | |
| Level 3: Independent Expert | 27 | |
| Level 4: Technical Leader | 25 | |
| Level 5: Organizational Strategist | 21 | |
| **Итого** | **118** | |

---

## Связанные файлы

- [[Home]] -- главная навигация
- [[role-mobile-developer]] -- портал мобильного разработчика
- [[role-tech-lead]] -- портал техлида
- [[quick-reference]] -- топ-30 файлов
- [[study-dashboard]] -- дашборд прогресса обучения

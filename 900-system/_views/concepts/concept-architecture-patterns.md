---
title: "Архитектурные паттерны: сквозной концепт"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
  - cross-cutting
---

# Архитектурные паттерны: сквозной концепт

> Как MVC, MVVM, MVI и Clean Architecture реализуются на Android, iOS и в кроссплатформенных проектах — общие принципы и платформенные различия.

## Сравнительная матрица

| Платформа | Доминирующий паттерн | Навигация | State Management | Модуляризация | Ключевые файлы |
|---|---|---|---|---|---|
| Android | MVVM + Clean Architecture | Navigation Component / Type-safe | ViewModel + StateFlow | Gradle modules | [[android-architecture-patterns]], [[android-modularization]] |
| iOS | MVVM + SwiftUI / VIPER (UIKit) | NavigationStack / Coordinator | @Observable / Combine | SPM / Xcode targets | [[ios-architecture-patterns]], [[ios-modularization]] |
| KMP | MVI / MVVM (shared) | Decompose / Voyager | shared ViewModel + Flow | Gradle KMP modules | [[kmp-architecture-patterns]], [[kmp-state-management]] |
| Cross-Platform | Зависит от фреймворка | Platform-specific + shared | Shared state layer | Feature modules | [[cross-architecture]], [[cross-state-management]] |
| Общая теория | SOLID + Clean Architecture | Dependency Rule | Unidirectional Data Flow | Package by feature | [[architecture-overview]], [[solid-principles]] |

## Android

- [[android-architecture-patterns]] — MVC → MVP → MVVM → MVI: эволюция и мотивация каждого перехода, AAC как стандарт Google
- [[android-architecture-evolution]] — историческая перспектива: от God Activity к многомодульным Clean Architecture проектам
- [[android-viewmodel-internals]] — как ViewModel переживает Configuration Change, связь с ViewModelStore и SavedStateHandle
- [[android-repository-pattern]] — единый источник данных: абстракция над сетью, кэшем и БД, стратегии кэширования
- [[android-modularization]] — app/feature/core модули, зависимости, navigation между модулями, build time оптимизация

## iOS

- [[ios-architecture-patterns]] — MVC (Apple) → MVVM → VIPER → TCA: как SwiftUI изменил подход к архитектуре
- [[ios-architecture-evolution]] — от Massive View Controller к Composable Architecture, влияние декларативного UI
- [[ios-viewmodel-patterns]] — @Observable vs ObservableObject, property wrappers (@State, @Binding, @Environment), их роль в архитектуре
- [[ios-repository-pattern]] — абстракция данных: протоколы, async/await в data layer, Core Data vs SwiftData
- [[ios-modularization]] — Swift Package Manager, Xcode targets, micro-features, управление зависимостями между модулями

## KMP

- [[kmp-architecture-patterns]] — shared ViewModel, expect/actual для платформенных различий, Clean Architecture в мультиплатформенном контексте
- [[kmp-state-management]] — общее состояние через Kotlin Flow, интеграция с Compose и SwiftUI, однонаправленный поток данных
- [[kmp-navigation]] — Decompose, Voyager, Appyx: как реализовать навигацию в shared-коде без привязки к платформе

## Cross-Platform

- [[cross-architecture]] — общие архитектурные принципы для кроссплатформенной разработки, границы shared-кода
- [[cross-state-management]] — паттерны управления состоянием: Redux-like, MVI, MVVM+ в контексте нескольких платформ
- [[cross-navigation]] — навигация как архитектурное решение: deep links, back stack management, platform conventions

## Общая теория

- [[architecture-overview]] — фундаментальные принципы: separation of concerns, dependency inversion, boundaries
- [[solid-principles]] — SOLID-принципы как основа всех архитектурных решений на всех платформах
- [[design-patterns-overview]] — GoF-паттерны и их применение в мобильной разработке: Strategy, Observer, Factory, Builder

## Глубинные паттерны

Все мобильные платформы пришли к одной и той же базовой архитектуре: **UI Layer → Domain Layer → Data Layer** с однонаправленным потоком данных. Android ViewModel + StateFlow, iOS @Observable + SwiftUI, KMP shared ViewModel + Flow — все реализуют один паттерн: состояние хранится в ViewModel, UI подписывается на изменения, действия пользователя обрабатываются через интенты/события. Разница только в синтаксисе и механизме подписки.

**Модуляризация** решает одну и ту же проблему на всех платформах — время сборки и зона ответственности команды. Android использует Gradle modules, iOS — SPM packages или Xcode targets, KMP — Gradle multiplatform modules. Паттерн «feature module зависит от core, но не от других feature» универсален. Ключевое отличие — Android Gradle позволяет более гибкую настройку (api vs implementation), тогда как SPM проще, но менее выразителен.

Навигация — наиболее платформенно-зависимая часть архитектуры. Android имеет жёсткий back stack с системной кнопкой «Назад», iOS — UINavigationController/NavigationStack с swipe-to-back. KMP-библиотеки (Decompose, Voyager) абстрагируют навигацию в shared-код, но неизбежно теряют часть платформенного поведения. Это классический trade-off кроссплатформенной разработки: больше shared-кода vs более нативный UX.

## Для интервью

> [!tip] Ключевые вопросы
> - Чем MVVM отличается от MVI? В каких случаях MVI предпочтительнее?
> - Как ViewModel на Android переживает поворот экрана? Какой аналог этого механизма в iOS?
> - Почему Clean Architecture выделяет Domain Layer без зависимостей от фреймворков? Как это помогает в KMP?
> - Опишите стратегию модуляризации для приложения с 5 командами. Какие типы модулей вы создадите?
> - Как бы вы организовали навигацию в KMP-проекте, чтобы сохранить нативное поведение на обеих платформах?

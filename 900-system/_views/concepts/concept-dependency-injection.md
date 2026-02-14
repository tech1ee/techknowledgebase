---
title: "Внедрение зависимостей: сквозной концепт"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
  - cross-cutting
---

# Внедрение зависимостей: сквозной концепт

> Как принцип инверсии зависимостей реализуется на Android, iOS и в кроссплатформенных проектах — от compile-time генерации до runtime-контейнеров.

## Сравнительная матрица

| Платформа | Основной фреймворк | Тип DI | Генерация кода | Scoping | Ключевые файлы |
|---|---|---|---|---|---|
| Android | Hilt (Dagger) | Compile-time | KSP / KAPT | Component hierarchy | [[android-hilt-deep-dive]], [[android-dagger-deep-dive]] |
| Android (альт.) | Koin / Kodein | Runtime | Нет | Module-based | [[android-koin-deep-dive]], [[android-kodein-deep-dive]] |
| Android (новое) | kotlin-inject / Metro | Compile-time (KSP) | KSP | Component-based | [[android-kotlin-inject-deep-dive]], [[android-metro-deep-dive]] |
| iOS | Ручной DI / Swinject | Runtime / Manual | Нет | Protocol-based | [[ios-dependency-injection]] |
| KMP | Koin / kotlin-inject | Runtime / Compile-time | KSP (опционально) | Shared + platform | [[kmp-di-patterns]] |
| Cross-Platform | Абстракция контейнера | Зависит от фреймворка | Зависит от выбора | Platform-aware | [[cross-dependency-injection]] |
| Теория | Принцип DIP (SOLID) | Концептуальный | N/A | Lifetime management | [[dependency-injection-fundamentals]] |

## Android

- [[android-dependency-injection]] — обзор подходов: зачем DI на Android, проблема создания зависимостей в Activity/Fragment, Service Locator vs DI
- [[android-hilt-deep-dive]] — стандарт Google: аннотации @HiltAndroidApp, @Inject, @Module, компонентная иерархия привязанная к жизненному циклу Android
- [[android-dagger-deep-dive]] — Dagger 2 под капотом: генерация кода, Component, Subcomponent, @Scope, multibinding, AssistedInject
- [[android-koin-deep-dive]] — Service Locator на Kotlin DSL: module { }, single { }, factory { }, без генерации кода, быстрая настройка
- [[android-kodein-deep-dive]] — Kodein-DI: binding DSL, multiplatform-поддержка, scoped instances, контекстные модули
- [[android-kotlin-inject-deep-dive]] — kotlin-inject: compile-time DI на KSP, вдохновлённый Dagger но с Kotlin-first синтаксисом
- [[android-metro-deep-dive]] — Metro: следующее поколение compile-time DI, интеграция с Circuit и Molecule
- [[android-manual-di-alternatives]] — ручной DI: Application-level factory, Constructor Injection без фреймворков, когда это оправдано

## iOS

- [[ios-dependency-injection]] — DI в экосистеме Apple: Composition Root, Protocol-oriented DI, @Environment в SwiftUI, Swinject, Factory, когда фреймворк не нужен

## KMP

- [[kmp-di-patterns]] — DI в мультиплатформенном контексте: Koin как мультиплатформенный стандарт, kotlin-inject для shared-кода, expect/actual для платформенных зависимостей

## Cross-Platform

- [[cross-dependency-injection]] — общие паттерны DI в кроссплатформенных проектах: абстракция контейнера, разделение shared/platform зависимостей

## Теория

- [[dependency-injection-fundamentals]] — принцип инверсии зависимостей (DIP), IoC-контейнеры, Constructor vs Property vs Method injection, lifetime management

## Глубинные паттерны

На Android DI прошёл уникальную эволюцию: **Dagger 1 (reflection) → Dagger 2 (compile-time) → Hilt (convention over configuration) → kotlin-inject / Metro (Kotlin-native)**. Каждый шаг убирал boilerplate и добавлял безопасность. Hilt привязал скоупы к Android-компонентам (SingletonComponent, ActivityComponent, FragmentComponent), что элегантно решило проблему lifetime management. Но за эту магию платишь сложностью сборки и временем компиляции.

iOS пошла другим путём: **в экосистеме Apple нет доминирующего DI-фреймворка**. Многие iOS-команды используют ручной DI через Composition Root или Protocol-based injection. SwiftUI усилил эту тенденцию — @Environment и @EnvironmentObject предоставляют встроенный механизм передачи зависимостей через дерево view. Swinject существует, но не стал стандартом, как Hilt на Android.

В KMP-проектах выбор DI-фреймворка становится архитектурным решением. **Koin** работает на всех платформах (JVM, iOS, JS) без генерации кода, что делает его самым простым вариантом. **kotlin-inject** даёт compile-time безопасность, но требует KSP на каждой платформе. Ключевой паттерн — разделение: shared-модуль определяет интерфейсы зависимостей, а platform-модули предоставляют реализации через expect/actual или platform-specific модули DI.

## Для интервью

> [!tip] Ключевые вопросы
> - В чём разница между compile-time DI (Dagger/Hilt) и runtime DI (Koin)? Какие trade-offs у каждого подхода?
> - Как Hilt Component hierarchy связана с жизненным циклом Android-компонентов? Что происходит при повороте экрана?
> - Почему в iOS-экосистеме нет стандартного DI-фреймворка, как Hilt на Android? Как SwiftUI решает проблему передачи зависимостей?
> - Как организовать DI в KMP-проекте, где shared-код используется на Android и iOS?
> - Когда ручной DI (Manual DI) предпочтительнее фреймворка? Приведите критерии для принятия решения.

---
title: "Тестирование: сквозной концепт"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
  - cross-cutting
---

# Тестирование: сквозной концепт

> Как стратегии тестирования реализуются на Android, iOS и в кроссплатформенных проектах — от unit-тестов до E2E, от пирамиды тестов до testing trophy.

## Сравнительная матрица

| Платформа | Unit-тесты | UI-тесты | Фреймворк | Мocking | Особенность | Ключевые файлы |
|---|---|---|---|---|---|---|
| Android | JUnit 5 + Turbine | Espresso / Compose Testing | JUnit + AndroidX Test | MockK / Mockito-Kotlin | Robolectric для JVM-тестов без эмулятора | [[android-testing]] |
| iOS | XCTest + Quick/Nimble | XCUITest | XCTest | Protocol Mocks / OCMock | Тесная интеграция с Xcode, snapshot testing | [[ios-testing]] |
| KMP | kotlin.test | Compose Multiplatform Test | kotlin.test + expect/actual | MockK (JVM) / manual | Общие тесты для shared-кода | [[kmp-testing-strategies]], [[kmp-unit-testing]] |
| Cross-Platform | Platform-specific | Appium / Maestro | Зависит от фреймворка | Platform-specific | E2E через единый инструмент | [[cross-testing]] |
| Теория | Пирамида тестов | Testing Trophy | Концептуальное | Виды test doubles | Стратегия определяет ROI | [[testing-fundamentals]] |

## Android

- [[android-testing]] — полная стратегия: пирамида тестов на Android, JUnit + MockK для unit, Espresso для UI, Robolectric для быстрых интеграционных тестов, Compose Testing API, Hilt Testing, Test Fixtures, CI-интеграция

## iOS

- [[ios-testing]] — тестирование в экосистеме Apple: XCTest как стандарт, XCUITest для UI, Swift Testing (новый фреймворк), snapshot testing, performance tests, Test Plans в Xcode, protocol-based mocking vs OCMock

## KMP

- [[kmp-testing-strategies]] — стратегия тестирования мультиплатформенного проекта: что тестировать в commonTest, что в platform-specific, соотношение shared и platform тестов
- [[kmp-unit-testing]] — kotlin.test API, expect/actual для test utilities, assertion-библиотеки, тестирование корутин в common-коде
- [[kmp-integration-testing]] — интеграционные тесты в KMP: тестирование Ktor-клиента, SQLDelight queries, DI-конфигурации на каждой платформе

## Cross-Platform

- [[cross-testing]] — тестирование кроссплатформенных приложений: Maestro для E2E, Appium, screenshot testing, стратегия покрытия shared vs platform кода

## Общая теория

- [[testing-fundamentals]] — фундаментальные концепции: пирамида тестов vs Testing Trophy, TDD, BDD, виды test doubles (mock, stub, spy, fake), метрики качества тестов, flaky tests

## Глубинные паттерны

Все платформы разделяют базовую пирамиду тестов: **много unit-тестов → меньше интеграционных → минимум E2E**. Но реализация существенно отличается. Android уникален наличием **Robolectric** — возможностью запускать Android-специфичный код на JVM без эмулятора, что радикально ускоряет обратную связь. iOS не имеет аналога: XCTest всегда требует симулятор (или устройство), что делает CI дороже. KMP добавляет новое измерение — **commonTest** позволяет писать тесты один раз для всех платформ, но только для shared-логики.

Подход к мокированию — одно из ключевых различий. Android-экосистема богата библиотеками (MockK, Mockito-Kotlin) благодаря рефлексии и возможностям JVM. iOS использует protocol-based подход — создание mock-объектов через реализацию протоколов, что требует больше boilerplate, но делает тесты более явными. В KMP MockK работает только для JVM-таргета; для остальных платформ приходится использовать manual fakes или expect/actual для test doubles.

**Compose Testing API** и **Swift Testing** — новые поколения инструментов на обеих платформах. Compose Testing позволяет тестировать UI как функции (семантические деревья вместо ID-based поиска). Swift Testing (с 2024) привносит макросы (#expect, #require) и лучшую интеграцию с async/await. Оба подхода движутся к более декларативному тестированию, отражая общий тренд в UI-фреймворках.

## Для интервью

> [!tip] Ключевые вопросы
> - Как вы определяете соотношение unit/integration/E2E тестов в мобильном проекте? Чем мобильная пирамида отличается от backend?
> - Что такое Robolectric и какую проблему он решает? Почему iOS не имеет аналога?
> - Как протестировать ViewModel, которая использует корутины и Flow? Какие инструменты нужны (Turbine, TestDispatcher)?
> - Как организовать тестирование в KMP-проекте? Что пишется в commonTest, а что в platform-specific тестах?
> - Когда mock оправдан, а когда лучше использовать fake? Приведите примеры из мобильной разработки.

---
title: "Programming MOC"
created: 2025-12-22
modified: 2026-02-19
type: moc
status: published
tags:
  - type/moc
  - topic/programming
---

# Programming MOC

> Карта содержимого раздела Programming Foundations — 29 файлов в 7 пакетах

---

## 01 — Принципы проектирования

- [[oop-fundamentals]] — Инкапсуляция, наследование, полиморфизм, абстракция
- [[solid-principles]] — 5 принципов SOLID: SRP, OCP, LSP, ISP, DIP
- [[clean-code]] — Именование, функции, комментарии, форматирование кода
- [[dry-kiss-yagni]] — Баланс между переиспользованием и простотой
- [[composition-vs-inheritance]] — Композиция, наследование, делегирование: когда что выбирать
- [[coupling-cohesion]] — Связанность и сцепленность как метрики качества модулей

---

## 02 — Паттерны проектирования

- [[design-patterns-overview]] — Классификация GoF-паттернов и критерии выбора
- [[singleton-pattern]] — Единственный экземпляр: object в Kotlin, thread-safety, DI-альтернативы
- [[factory-pattern]] — Создание объектов без привязки к конкретным классам
- [[builder-pattern]] — Пошаговое построение сложных объектов
- [[strategy-pattern]] — Взаимозаменяемые алгоритмы через общий интерфейс
- [[observer-pattern]] — Реактивное оповещение подписчиков об изменениях
- [[decorator-pattern]] — Динамическое добавление поведения без наследования
- [[adapter-pattern]] — Мост между несовместимыми интерфейсами
- [[state-pattern]] — Поведение объекта, зависящее от внутреннего состояния

---

## 03 — Качество кода

- [[code-smells]] — Каталог запахов кода: Long Method, God Class, Feature Envy и другие
- [[refactoring-catalog]] — Систематические техники рефакторинга: Extract, Move, Inline
- [[legacy-code-strategies]] — Стратегии работы с legacy: Strangler Fig, характеризующие тесты

---

## 04 — Тестирование

- [[testing-fundamentals]] — Пирамида тестов, Unit/Integration/E2E, паттерн AAA
- [[tdd-practice]] — Цикл Red-Green-Refactor: когда TDD помогает и когда мешает
- [[mocking-strategies]] — Mocks, stubs, fakes: техники изоляции зависимостей

---

## 05 — Обработка ошибок

- [[error-handling]] — Exceptions vs Result, fail-fast, defensive programming
- [[resilience-patterns]] — Circuit Breaker, Retry, Timeout, Bulkhead, Fallback

---

## 06 — Парадигмы программирования

- [[functional-programming]] — Чистые функции, иммутабельность, функции высшего порядка в Kotlin
- [[concurrency-fundamentals]] — Потоки, синхронизация, модели конкурентности

---

## 07 — Инструменты и теория

- [[type-systems-theory]] — Статическая vs динамическая типизация, type inference, generics
- [[build-systems-theory]] — Инкрементальная сборка, task graph, кэширование артефактов
- [[dependency-resolution]] — Разрешение зависимостей, конфликты версий, lock-файлы
- [[module-systems]] — Модульность: пакеты, visibility, границы модулей

---

## Ключевые концепции раздела

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| SOLID | 5 принципов гибкого ООП-дизайна | [[solid-principles]] |
| Composition over Inheritance | Предпочитай композицию наследованию | [[composition-vs-inheritance]] |
| Coupling & Cohesion | Слабая связанность + высокая сцепленность = хороший модуль | [[coupling-cohesion]] |
| GoF Patterns | 23 классических паттерна: Creational, Structural, Behavioral | [[design-patterns-overview]] |
| Strategy | Взаимозаменяемые алгоритмы без if/else | [[strategy-pattern]] |
| Observer | Pub/Sub: реакция на события без жёсткой связи | [[observer-pattern]] |
| Code Smells | Индикаторы проблем: Long Method, God Class, Feature Envy | [[code-smells]] |
| Refactoring | Улучшение структуры без изменения поведения | [[refactoring-catalog]] |
| Test Pyramid | Много unit, меньше integration, мало E2E | [[testing-fundamentals]] |
| TDD | Red-Green-Refactor: тесты до кода | [[tdd-practice]] |
| Circuit Breaker | Защита от каскадных сбоев в распределённых системах | [[resilience-patterns]] |
| Pure Functions | Детерминированные функции без побочных эффектов | [[functional-programming]] |
| Type Safety | Компилятор как первая линия обороны от ошибок | [[type-systems-theory]] |

---

## Статистика

| Метрика | Значение |
|---------|----------|
| Всего файлов | 29 |
| Пакетов | 7 |
| Язык примеров | Kotlin |
| Последнее обновление | 2026-02-19 |

---

## Связанные MOC

- [[jvm-moc]] — JVM-платформа: память, GC, JIT, байткод
- [[kotlin-moc]] — Kotlin: синтаксис, корутины, Flow, advanced features
- [[architecture-moc]] — Архитектурные паттерны уровнем выше
- [[android-moc]] — Android-платформа: применение принципов на практике

---

## Навигация

- [[programming-overview]] — Обзор раздела с описаниями и рекомендуемым порядком чтения
- [[Home]] — Главная карта знаний
- [[cs-fundamentals-overview]] — CS Fundamentals: алгоритмы, структуры данных

---

*Создано: 2025-12-22 | Обновлено: 2026-02-19*

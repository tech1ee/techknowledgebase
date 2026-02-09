---
title: "Research Report: SQLDelight in KMP"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: SQLDelight in KMP

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

SQLDelight 2.2.1 — библиотека от Cash App (Block), генерирует типобезопасные Kotlin API из SQL-запросов. Compile-time verification схемы. Drivers: AndroidSqliteDriver, NativeSqliteDriver, JdbcSqliteDriver. Flow extensions для реактивных запросов (asFlow + mapToList). Миграции через .sqm файлы с автоматическим версионированием. Room KMP 2.7.0+ появился как альтернатива, но SQLDelight — более mature для KMP.

## Key Findings

1. **SQL-first Approach**
   - Пишешь SQL напрямую в .sq файлах
   - Генерируются typesafe Kotlin методы
   - Compile-time verification

2. **Multiplatform Drivers**
   - Android: AndroidSqliteDriver
   - iOS/Native: NativeSqliteDriver
   - JVM: JdbcSqliteDriver
   - JS: web-worker-driver

3. **Flow Extensions**
   - asFlow() превращает Query в Flow
   - mapToList(), mapToOne(), mapToOneOrNull()
   - Автоматически эмитит при изменениях в БД

4. **Migration System**
   - .sqm файлы (1.sqm, 2.sqm...)
   - Версия = кол-во .sqm + 1
   - verifyMigrations для CI

5. **SQLDelight vs Room KMP**
   - SQLDelight: native KMP support, SQL-first
   - Room: DAO-first, Jetpack integration
   - Выбор зависит от опыта команды

## Community Sentiment

### Positive
- Cash App создали и используют в production
- Compile-time SQL verification
- Excellent KMP support
- Flow integration works well

### Negative
- No onCreate callback (как в Room)
- Миграции требуют .sqm + обновление .sq
- iOS требует -lsqlite3 linker flag
- Структура папок должна точно совпадать с packageName

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [SQLDelight docs](https://sqldelight.github.io/sqldelight/) | Official | 0.95 | Complete reference |
| 2 | [Multiplatform SQLite](https://sqldelight.github.io/sqldelight/2.0.2/multiplatform_sqlite/) | Official | 0.95 | KMP setup |
| 3 | [Migrations](https://sqldelight.github.io/sqldelight/2.0.2/multiplatform_sqlite/migrations/) | Official | 0.95 | Migration guide |
| 4 | [Coroutines Extensions](https://sqldelight.github.io/sqldelight/2.0.2/android_sqlite/coroutines/) | Official | 0.95 | Flow support |
| 5 | [Cash App Case Study](https://blog.jetbrains.com/kotlin/2021/03/cash-app-case-study/) | Blog | 0.90 | Production usage |
| 6 | [SQLDelight vs Room](https://medium.com/@muralivitt/database-solutions-for-kmp-cmp-sqldelight-vs-room-ea9a52c7bce7) | Blog | 0.80 | Comparison |
| 7 | [In-Memory Testing](https://akjaw.com/kotlin-multiplatform-testing-sqldelight-integration-ios-android/) | Blog | 0.85 | Testing patterns |


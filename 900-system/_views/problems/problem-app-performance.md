---
title: "Диагностика: Мое приложение тормозит"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Мое приложение тормозит

Диагностическое руководство для проблем производительности мобильных приложений.

---

## Таблица симптомов

| Симптом | Вероятная причина | Начни отсюда |
|---------|------------------|--------------|
| Медленный запуск (cold start > 1с) | Тяжелая инициализация, лишние зависимости | [[android-app-startup-performance]] |
| Подергивания UI (jank, dropped frames) | Тяжелые операции на main thread | [[android-view-rendering-pipeline]] |
| Медленные API-вызовы | Сеть, сериализация, отсутствие кеша | [[android-networking]], [[network-latency-optimization]] |
| Память постоянно растет | Утечки памяти, неочищенные подписки | [[android-memory-leaks]] |
| Медленные запросы к БД | Отсутствие индексов, N+1, большие транзакции | [[android-room-performance]] |
| Анимации не плавные | Сложная иерархия View, overdraw | [[android-animations]] |
| Приложение убивается системой | OOM, утечки, тяжелый background | [[android-process-memory]] |

---

## Инструменты диагностики

### Android
- **Android Profiler** (CPU, Memory, Network) — [[android-performance-profiling]]
- **Layout Inspector** — анализ иерархии View
- **StrictMode** — обнаружение операций на main thread
- **LeakCanary** — автоматический поиск утечек памяти

### iOS
- **Instruments** (Time Profiler, Allocations, Leaks) — [[ios-performance-profiling]]
- **Xcode Memory Graph** — визуализация retain cycles

### Backend/Infrastructure
- **Observability stack** — [[observability]]
- **APM** — трейсинг запросов end-to-end

---

## Исправления по слоям

### UI слой
1. Переместить тяжелые вычисления из main thread
2. Использовать `LazyColumn`/`LazyRow` вместо `Column`/`Row` для списков
3. Минимизировать recomposition в Compose — [[android-compose-internals]]
4. Оптимизировать иерархию View — [[android-view-rendering-pipeline]]

### Слой данных
1. Добавить индексы в Room — [[android-room-performance]]
2. Использовать пагинацию для больших наборов данных
3. Кеширование на уровне Repository — [[android-repository-pattern]]
4. Правильный выбор хранилища — [[android-data-persistence]]

### Сетевой слой
1. Кеширование HTTP-ответов (OkHttp cache, ETags)
2. Сжатие (gzip, протоколы)
3. Параллельные запросы где возможно
4. Оптимизация сериализации — [[android-networking]]
5. Общие принципы — [[network-latency-optimization]]

### Инфраструктура
1. Профилирование сборки — [[android-gradle-fundamentals]]
2. R8/ProGuard оптимизация — [[android-proguard-r8]]
3. Baseline Profiles для ускорения запуска
4. CI/CD метрики производительности — [[android-ci-cd]]

---

## Порядок действий

```
1. Измерь (профайлер) → определи bottleneck
2. Установи baseline метрики
3. Исправь самый критичный слой
4. Измерь снова → сравни с baseline
5. Повтори для следующего bottleneck
```

---

## Связанные материалы
- [[android-app-startup-performance]] — оптимизация запуска
- [[android-memory-leaks]] — утечки памяти
- [[android-performance-profiling]] — профилирование Android
- [[ios-performance-profiling]] — профилирование iOS
- [[performance-optimization]] — общие принципы оптимизации
- [[observability]] — мониторинг в продакшене

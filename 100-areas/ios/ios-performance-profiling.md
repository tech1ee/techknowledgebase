---
title: "iOS Performance Profiling: Instruments, Time Profiler, Memory Graph"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/performance
  - level/advanced
---

## TL;DR

Instruments - это мощный комплекс профайлинг-инструментов Apple для анализа производительности, памяти, графики и сетевых операций iOS-приложений. Time Profiler показывает, где CPU тратит время, Memory Graph выявляет retain cycles и утечки, а Core Animation instrument измеряет FPS и находит проблемы рендеринга. В продакшене MetricKit собирает метрики с реальных устройств пользователей без влияния на производительность.

---

## Зачем это нужно?

**Реальное влияние производительности на бизнес:**

| Метрика | Влияние на пользователей |
|---------|--------------------------|
| Время запуска > 400ms | -25% конверсии первого экрана |
| FPS < 60 при скролле | -40% оценок в App Store |
| Memory > 1.5GB | Jetsam kills на старых устройствах |
| Battery drain > 5%/час | Удаление приложения в течение недели |
| Hang > 500ms | App Store отклоняет приложение |

**Статистика из реальных проектов:**
- 53% пользователей удаляют приложение после 3+ секунд загрузки
- Каждые 100ms задержки UI = -7% вовлечённости
- Приложения с memory leaks теряют до 30% DAU за месяц
- Apple отклоняет ~15% обновлений из-за performance regression

**Критические пороги для App Store Review:**
```
Время запуска: < 400ms до first render
Hang Rate: < 0.1% сессий с зависаниями > 500ms
Memory Footprint: < 50MB для виджетов, < 200MB baseline для apps
Crash Rate: < 0.1% сессий
```

---

## Аналогии из жизни

### 1. Instruments = Медицинское обследование

```
Instruments - это полный чекап в клинике:

┌─────────────────────────────────────────────────────────────┐
│  КЛИНИКА ПРОФИЛАКТИКИ (Instruments.app)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  МРТ (System Trace)                                          │
│  ├─ Видит ВСЁ, что происходит внутри                        │
│  ├─ Показывает каждый орган и процесс                       │
│  └─ Очень детально, но долго анализировать                  │
│                                                               │
│  Анализ крови (Memory)                                       │
│  ├─ Allocations: сколько "клеток" создано                   │
│  ├─ Leaks: "мёртвые клетки" не выводятся                    │
│  └─ Memory Graph: "родственные связи" между органами        │
│                                                               │
│  Кардиограмма (Time Profiler)                                │
│  ├─ Пульс = CPU usage                                        │
│  ├─ Аритмия = неравномерная нагрузка                        │
│  └─ Тахикардия = CPU перегружен                             │
│                                                               │
│  Рентген (Core Animation)                                    │
│  ├─ Видит "кости" UI - слои рендеринга                      │
│  ├─ Находит "переломы" - offscreen rendering                │
│  └─ Показывает "нагрузку" на графическую систему            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2. Time Profiler = Секундомер на каждом сотруднике

```
Представьте офис, где у каждого сотрудника персональный секундомер:

     CEO (main thread)
     ┌──────────────────────┐
     │ 09:00-09:05 Планёрка │ ← viewDidLoad (5 сек!)
     │ 09:05-09:07 Email    │ ← layoutSubviews
     │ 09:07-09:30 Звонки   │ ← API запросы (ПРОБЛЕМА!)
     │ 09:30-09:31 Обед     │ ← свободное время CPU
     └──────────────────────┘

Time Profiler показывает:
- Кто работает дольше всех (hottest functions)
- Кто тратит время впустую (blocking operations)
- Где очередь из задач (thread contention)

"Почему CEO тратит 23 минуты на звонки?"
= "Почему main thread блокируется на сетевых запросах?"
```

### 3. Memory Graph = Семейное дерево объектов

```
Объекты связаны "родственными" отношениями:

                    ┌─────────────┐
                    │  AppDelegate│ Прадедушка
                    │   (root)    │
                    └──────┬──────┘
                           │ strong
              ┌────────────┴────────────┐
              │                          │
        ┌─────┴─────┐              ┌─────┴─────┐
        │ RootVC    │              │ DataStore │
        │ (дедушка) │              │ (дедушка) │
        └─────┬─────┘              └───────────┘
              │ strong
        ┌─────┴─────┐
        │ ChildVC   │ ← Retain Cycle!
        │ (папа)    │◄─────────────┐
        └─────┬─────┘              │ strong (!)
              │ strong             │
        ┌─────┴─────┐              │
        │ Closure   ├──────────────┘
        │ (ребёнок) │ captures self
        └───────────┘

Memory Graph показывает:
- Кто кого "держит" (strong references)
- Кто "завис" без родителей (orphaned objects)
- Где "взаимные обязательства" (retain cycles)
```

### 4. Allocations = Журнал покупок и выбрасывания вещей

```
Представьте журнал домашних покупок:

ЖУРНАЛ ALLOCATIONS:
┌─────────────────────────────────────────────────────────────┐
│ Время    │ Действие  │ Предмет        │ Цена   │ Осталось  │
├──────────┼───────────┼────────────────┼────────┼───────────┤
│ 09:00:01 │ Купил     │ UIImageView    │ 4 MB   │ 4 MB      │
│ 09:00:02 │ Купил     │ Data (фото)    │ 12 MB  │ 16 MB     │
│ 09:00:05 │ Выбросил  │ UIImageView    │ -4 MB  │ 12 MB     │
│ 09:00:05 │ Выбросил  │ Data (фото)    │ -12 MB │ 0 MB      │
│ 09:01:00 │ Купил     │ UIView (100x)  │ 50 MB  │ 50 MB     │
│ 09:01:01 │ Купил     │ CALayer (100x) │ 30 MB  │ 80 MB     │
│ 09:02:00 │ ???       │ ???            │ ???    │ 80 MB     │ ← Ничего не выбросили!
└─────────────────────────────────────────────────────────────┘

Здоровый паттерн: "Купил → Использовал → Выбросил"
Утечка: "Купил → ... → Купил → ... → Никогда не выбрасываю"
```

### 5. Leaks = Вещи, которые забыли выбросить

```
Квартира с накопительством:

Каждый месяц покупаете газету, но никогда не выбрасываете:

Январь:  [Газета] ──────────────────────────────► 1 шт, 100г
Февраль: [Газета][Газета] ──────────────────────► 2 шт, 200г
...
Декабрь: [Газета x12] ─────────────────────────► 12 шт, 1.2 кг
...
Год 10:  [Газета x120] ────────────────────────► 12 кг → ПРОБЛЕМА!

Leaks instrument находит:
- Объекты без "хозяина" (orphaned allocations)
- Объекты в круговой поруке (retain cycles)
- Объекты, созданные, но никогда не освобождённые

class ViewModel {
    var closure: (() -> Void)?

    func setup() {
        closure = {
            self.doWork() // ← "Газета" которую забыли выбросить
        }
    }
}
```

---

## Обзор инструментов профилирования

```
┌─────────────────────────────────────────────────────────────────────┐
│  ЭКОСИСТЕМА ПРОФИЛИРОВАНИЯ iOS                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  INSTRUMENTS.app (System-Level Profiling)                    │   │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────────┐ │   │
│  │  │  Time   │ │ Memory   │ │ Core    │ │    Network       │ │   │
│  │  │Profiler │ │ Graph    │ │Animation│ │    Profiler      │ │   │
│  │  └────┬────┘ └────┬─────┘ └────┬────┘ └────────┬─────────┘ │   │
│  │       │           │            │               │            │   │
│  │  CPU Sampling  Allocations  FPS Counter   Request Timing   │   │
│  │  Call Trees    Leaks        Layer Debug   Payload Size     │   │
│  │  Thread State  Zombies      GPU Usage     Latency         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  XCODE DEBUGGER (Visual & Quick)                             │   │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │   │
│  │  │   Memory   │  │    Debug     │  │   View Hierarchy   │  │   │
│  │  │   Graph    │  │   Gauges     │  │     Debugger       │  │   │
│  │  │  Debugger  │  │              │  │                    │  │   │
│  │  └─────┬──────┘  └──────┬───────┘  └─────────┬──────────┘  │   │
│  │        │                │                    │              │   │
│  │  Retain Cycles    CPU/Memory/Disk     3D Layer View       │   │
│  │  Reference Graph  Quick Glance         Constraint Debug    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  CONSOLE.app & os_log (Logging)                              │   │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │   │
│  │  │ os_signpost│  │   os_log     │  │   Console.app      │  │   │
│  │  │   Points   │  │   Unified    │  │     Viewer         │  │   │
│  │  └─────┬──────┘  └──────┬───────┘  └─────────┬──────────┘  │   │
│  │        │                │                    │              │   │
│  │  Custom Intervals   Structured Logs     Filter & Search   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  METRICKIT (Production Monitoring)                           │   │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │   │
│  │  │    CPU     │  │   Memory     │  │      Hang          │  │   │
│  │  │  Metrics   │  │   Metrics    │  │   Diagnostics      │  │   │
│  │  └─────┬──────┘  └──────┬───────┘  └─────────┬──────────┘  │   │
│  │        │                │                    │              │   │
│  │  Real Users        Peak/Average         > 500ms hangs     │   │
│  │  24h Reports       Jetsam Events        Stack Traces      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

Когда использовать:

┌──────────────────┬────────────────────────────────────────────────┐
│ Задача           │ Инструмент                                     │
├──────────────────┼────────────────────────────────────────────────┤
│ UI лагает        │ Time Profiler → Core Animation                 │
│ Память растёт    │ Allocations → Memory Graph                     │
│ Retain cycle     │ Memory Graph Debugger (Xcode)                  │
│ Crash в проде    │ MetricKit + Crash Logs                         │
│ Slow startup     │ App Launch template                            │
│ Network issues   │ Network instrument + Charles Proxy             │
│ Battery drain    │ Energy Log + MetricKit                         │
└──────────────────┴────────────────────────────────────────────────┘
```

---

## Time Profiler

### Как запустить

```
1. Xcode → Product → Profile (⌘ + I)
   или
   Запустить Instruments.app напрямую

2. Выбрать Time Profiler template

3. Выбрать устройство и приложение

4. Нажать Record (красная кнопка)

5. Воспроизвести проблемный сценарий

6. Нажать Stop

7. Анализировать Call Tree
```

### Интерфейс Time Profiler

```
┌─────────────────────────────────────────────────────────────────────┐
│  Time Profiler - MyApp.app                                          │
├─────────────────────────────────────────────────────────────────────┤
│ [Record] [Pause] [Stop]        CPU: [████████░░] 78%                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  TIMELINE (Временная шкала CPU загрузки)                            │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │     ▄▄█▄                    ▄▄▄█████▄▄▄                         ││
│  │ ▄▄▄█████▄                 ▄████████████▄▄                       ││
│  │████████████▄▄▄▄▄▄▄▄▄▄▄▄▄██████████████████▄▄                   ││
│  │─────────────────────────────────────────────────────────────────││
│  │ 0s        5s        10s       15s       20s       25s           ││
│  └─────────────────────────────────────────────────────────────────┘│
│        ▲                           ▲                                 │
│        │                           └── Пик CPU - это наша проблема! │
│        └── Начало записи                                            │
│                                                                       │
│  CALL TREE (Дерево вызовов)                                         │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Weight   Self Weight   Symbol                                   ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ 78.5%    0.0%         start                                     ││
│  │ └ 78.5%  0.0%         main                                      ││
│  │   └ 78.5% 0.0%        UIApplicationMain                         ││
│  │     └ 75.2% 0.0%      -[AppDelegate application:didFinish...]   ││
│  │       └ 72.1% 0.0%    -[DataManager loadAllData]               ││
│  │         └ 70.8% 68.2% parseJSONSynchronously  ← ПРОБЛЕМА!      ││
│  │           └ 2.3% 2.3%  JSONDecoder.decode                       ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  OPTIONS                                                             │
│  ☑ Separate by Thread    ☑ Hide System Libraries                   │
│  ☑ Invert Call Tree      ☐ Top Functions                           │
│  ☐ Hide Missing Symbols  ☐ Flatten Recursion                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Чтение Call Tree

```
Понимание колонок:

Weight (78.5%)
├─ Общее время в этой функции И всех вызванных из неё
└─ Включает всё поддерево

Self Weight (68.2%)
├─ Время ТОЛЬКО в этой функции
└─ Не включает вызовы других функций

Пример:
func outer() {           // Weight: 100%, Self: 10%
    doWork()             // 10% времени тут
    inner()              // вызываем inner
}

func inner() {           // Weight: 90%, Self: 90%
    heavyComputation()   // 90% времени тут
}

Правило: Ищите высокий Self Weight - это реальные проблемы!
```

### Опции Call Tree

```swift
// Separate by Thread - разделяет по потокам
// Полезно для поиска проблем на main thread

// Invert Call Tree - показывает "снизу вверх"
// ДО (обычный вид):
main
└─ loadData
   └─ parseJSON
      └─ ПРОБЛЕМА: decode()  68%

// ПОСЛЕ (inverted):
ПРОБЛЕМА: decode()           68%
└─ called by parseJSON
   └─ called by loadData
      └─ called by main

// Invert полезен для быстрого поиска "горячих" функций

// Hide System Libraries - скрывает Apple код
// Видите только СВОЙ код - легче анализировать

// Top Functions - группирует по функциям
// Вместо дерева - плоский список самых тяжёлых
```

### Типичные проблемы и решения

```swift
// ❌ ПРОБЛЕМА 1: Синхронная работа на main thread
class BadViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Time Profiler покажет 70%+ CPU на main thread
        let data = try! Data(contentsOf: largeFileURL)  // БЛОКИРУЕТ!
        let parsed = try! JSONDecoder().decode([Item].self, from: data)
        tableView.reloadData()
    }
}

// ✅ РЕШЕНИЕ: Асинхронная загрузка
class GoodViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        Task {
            let data = try await URLSession.shared.data(from: largeFileURL)
            let parsed = try JSONDecoder().decode([Item].self, from: data.0)
            await MainActor.run {
                tableView.reloadData()
            }
        }
    }
}

// ❌ ПРОБЛЕМА 2: Лишние вычисления в цикле
func processItems(_ items: [Item]) {
    for item in items {
        // Time Profiler покажет этот код в каждой итерации
        let formatter = DateFormatter()  // Создаём 1000 раз!
        formatter.dateStyle = .medium
        item.displayDate = formatter.string(from: item.date)
    }
}

// ✅ РЕШЕНИЕ: Переиспользование объектов
func processItems(_ items: [Item]) {
    let formatter = DateFormatter()  // Создаём 1 раз
    formatter.dateStyle = .medium

    for item in items {
        item.displayDate = formatter.string(from: item.date)
    }
}

// ❌ ПРОБЛЕМА 3: Регулярные выражения в цикле
func filterTexts(_ texts: [String]) -> [String] {
    texts.filter { text in
        // Компиляция regex на каждой итерации!
        let regex = try! NSRegularExpression(pattern: "\\d{3}-\\d{4}")
        return regex.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)) != nil
    }
}

// ✅ РЕШЕНИЕ: Компиляция regex один раз
func filterTexts(_ texts: [String]) -> [String] {
    let regex = try! NSRegularExpression(pattern: "\\d{3}-\\d{4}")
    return texts.filter { text in
        regex.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)) != nil
    }
}
```

---

## Memory Debugging

### Allocations Instrument

```
┌─────────────────────────────────────────────────────────────────────┐
│  Allocations - MyApp.app                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  MEMORY TIMELINE                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                                   ▄▄▄▄                          ││
│  │                              ▄▄▄██████                          ││
│  │  Persistent: 45 MB     ▄▄▄█████████████                        ││
│  │                    ▄▄██████████████████▄▄                       ││
│  │  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄████████████████████████████                    ││
│  │─────────────────────────────────────────────────────────────────││
│  │ 0s          10s          20s          30s          40s          ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                 ▲                                    │
│                                 └── Memory только растёт = LEAK!    │
│                                                                       │
│  ALLOCATIONS LIST                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Category              Persistent   #Persistent   #Transient     ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ All Heap Allocations     45.2 MB      15,234        892,445     ││
│  │ └ Malloc 4.00 KB          8.1 MB       2,089         45,234     ││
│  │ └ Malloc 16.00 KB        12.3 MB         789         12,456     ││
│  │ └ __NSArrayM              5.6 MB       1,245         34,567     ││
│  │ └ _UIImageContent        15.2 MB          45 ← ПРОБЛЕМА!        ││
│  │ └ NSConcreteData          4.0 MB         234         56,789     ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  Persistent = живут сейчас                                          │
│  Transient = были созданы и освобождены                             │
│                                                                       │
│  DETAIL VIEW (при выборе категории)                                 │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Address      Size    Responsible Library    Responsible Caller  ││
│  │ 0x7fff1234   4 KB    MyApp                  loadImage(_:)       ││
│  │ 0x7fff5678   4 KB    MyApp                  loadImage(_:)       ││
│  │ ...                                                              ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Leaks Instrument

```
┌─────────────────────────────────────────────────────────────────────┐
│  Leaks - MyApp.app                                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  LEAKS TIMELINE                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    ❌          ❌              ❌                ││
│  │                    │           │               │                 ││
│  │─────────────────────────────────────────────────────────────────││
│  │ 0s          10s          20s          30s          40s          ││
│  └─────────────────────────────────────────────────────────────────┘│
│             ▲                                                        │
│             └── Красные ❌ = обнаруженные утечки в этот момент       │
│                                                                       │
│  LEAKS LIST                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Leaked Object                    Size      Count                 ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ ✖ MyViewController              256 B         3                  ││
│  │ ✖ MyClosure (context)           128 B         3                  ││
│  │ ✖ NSMutableArray                 64 B         6                  ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  CYCLES & ROOTS (при выборе leaked object)                          │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                                                                   ││
│  │  ┌──────────────────┐     strong     ┌────────────────┐         ││
│  │  │ MyViewController │───────────────►│   Closure      │         ││
│  │  │    (leaked)      │                │   (leaked)     │         ││
│  │  │                  │◄───────────────│                │         ││
│  │  └──────────────────┘   captures     └────────────────┘         ││
│  │                          self                                    ││
│  │                                                                   ││
│  │  RETAIN CYCLE DETECTED!                                          ││
│  │                                                                   ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Memory Graph Debugger (Xcode)

```
Запуск: Debug → Debug Memory Graph (во время работы приложения)
Или: кнопка с тремя кружками в Debug Navigator

┌─────────────────────────────────────────────────────────────────────┐
│  Memory Graph Debugger                                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  LEFT PANEL (Object List)                                            │
│  ┌────────────────────────┐                                          │
│  │ ⚠️ 3 Issues            │ ← Проблемы (retain cycles)              │
│  │                        │                                          │
│  │ Filter: ___________    │                                          │
│  │                        │                                          │
│  │ ▼ MyApp               │                                          │
│  │   ├ AppDelegate    1  │                                          │
│  │   ├ MainVC         1  │                                          │
│  │   ├ DetailVC       3  │ ← Почему 3? Должен быть 1!              │
│  │   ├ DataManager    1  │                                          │
│  │   └ ViewModel      5  │ ← Утечка ViewModels!                     │
│  │                        │                                          │
│  │ ▼ System              │                                          │
│  │   ├ UIView       245  │                                          │
│  │   ├ CALayer      312  │                                          │
│  │   └ ...               │                                          │
│  └────────────────────────┘                                          │
│                                                                       │
│  CENTER PANEL (Graph Visualization)                                  │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                                                                   ││
│  │                   ┌──────────────┐                               ││
│  │                   │  DetailVC    │                               ││
│  │                   │   0x7f8a1    │                               ││
│  │                   └──────┬───────┘                               ││
│  │                          │ viewModel (strong)                    ││
│  │                          ▼                                        ││
│  │                   ┌──────────────┐                               ││
│  │                   │  ViewModel   │                               ││
│  │         ┌────────►│   0x7f8a2    │◄────────┐                     ││
│  │         │         └──────┬───────┘         │                     ││
│  │         │                │                 │                     ││
│  │         │ delegate       │ onComplete      │                     ││
│  │         │ (strong!)      │ (closure)       │                     ││
│  │         │                ▼                 │ captures            ││
│  │         │         ┌──────────────┐         │ self                ││
│  │         └─────────│   Closure    │─────────┘                     ││
│  │                   │   0x7f8a3    │                               ││
│  │                   └──────────────┘                               ││
│  │                                                                   ││
│  │         ═══════════════════════════                              ││
│  │         RETAIN CYCLE: DetailVC → ViewModel → Closure → DetailVC ││
│  │         ═══════════════════════════                              ││
│  │                                                                   ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  RIGHT PANEL (Object Details)                                        │
│  ┌────────────────────────┐                                          │
│  │ DetailVC               │                                          │
│  │ Address: 0x7f8a12340   │                                          │
│  │ Size: 256 bytes        │                                          │
│  │                        │                                          │
│  │ References TO:         │                                          │
│  │  • viewModel (strong)  │                                          │
│  │  • view (strong)       │                                          │
│  │                        │                                          │
│  │ References FROM:       │                                          │
│  │  • Closure (strong) ⚠️ │ ← ПРОБЛЕМА!                             │
│  │  • UINavigationVC      │                                          │
│  └────────────────────────┘                                          │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Исправление Retain Cycles

```swift
// ❌ ПРОБЛЕМА: Retain Cycle в closure
class DetailViewController: UIViewController {
    var viewModel: ViewModel!

    override func viewDidLoad() {
        super.viewDidLoad()

        viewModel.onComplete = {
            // self захватывается strong по умолчанию!
            self.showSuccess()  // DetailVC → ViewModel → Closure → DetailVC
        }
    }
}

// ✅ РЕШЕНИЕ 1: [weak self]
class DetailViewController: UIViewController {
    var viewModel: ViewModel!

    override func viewDidLoad() {
        super.viewDidLoad()

        viewModel.onComplete = { [weak self] in
            guard let self = self else { return }
            self.showSuccess()
        }
    }
}

// ✅ РЕШЕНИЕ 2: [unowned self] (если точно знаем lifecycle)
class DetailViewController: UIViewController {
    var viewModel: ViewModel!

    override func viewDidLoad() {
        super.viewDidLoad()

        viewModel.onComplete = { [unowned self] in
            // Если closure вызовется после deinit → краш!
            self.showSuccess()
        }
    }
}

// ❌ ПРОБЛЕМА: Delegate strong reference
class ViewModel {
    var delegate: ViewModelDelegate?  // strong по умолчанию!
}

class DetailVC: UIViewController, ViewModelDelegate {
    var viewModel = ViewModel()

    override func viewDidLoad() {
        super.viewDidLoad()
        viewModel.delegate = self  // CYCLE: DetailVC → ViewModel → DetailVC
    }
}

// ✅ РЕШЕНИЕ: weak delegate
class ViewModel {
    weak var delegate: ViewModelDelegate?  // weak!
}

// ❌ ПРОБЛЕМА: Timer retain cycle
class TimerViewController: UIViewController {
    var timer: Timer?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Timer держит target (self) strong!
        timer = Timer.scheduledTimer(
            timeInterval: 1.0,
            target: self,
            selector: #selector(tick),
            userInfo: nil,
            repeats: true
        )
    }

    @objc func tick() { /* ... */ }

    // deinit никогда не вызовется - Timer держит self!
}

// ✅ РЕШЕНИЕ: Invalidate timer или использовать closure-based timer
class TimerViewController: UIViewController {
    var timer: Timer?

    override func viewDidLoad() {
        super.viewDidLoad()

        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.tick()
        }
    }

    func tick() { /* ... */ }

    deinit {
        timer?.invalidate()
    }
}
```

---

## Core Animation Instrument

### Запуск и интерфейс

```
1. Instruments → Core Animation template
2. Выбрать устройство (реальное, не симулятор!)
3. Record и взаимодействовать с UI

┌─────────────────────────────────────────────────────────────────────┐
│  Core Animation - MyApp.app                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  FPS TIMELINE                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ 60 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─    ││
│  │ 55 ████████████████████                    ████████████████████ ││
│  │ 50                     ████                                      ││
│  │ 45                         ████                                  ││
│  │ 40                             ████████                          ││
│  │ 30                                     ████ ← ПРОБЛЕМА: 30 FPS  ││
│  │─────────────────────────────────────────────────────────────────││
│  │ 0s          2s          4s          6s          8s              ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  DEBUG OPTIONS (в Xcode: Debug → View Debugging → Rendering)        │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ ☑ Color Blended Layers (показывает alpha blending)             ││
│  │ ☑ Color Offscreen-Rendered (желтый = offscreen rendering)      ││
│  │ ☐ Color Hits Green and Misses Red (кэш растеризации)           ││
│  │ ☐ Color Copied Images (изображения копируются для GPU)         ││
│  │ ☐ Color Misaligned Images (не выровненные изображения)         ││
│  │ ☐ Flash Updated Regions (моргают обновлённые области)          ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Debug Options объяснение

```
COLOR BLENDED LAYERS
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  Зелёный = непрозрачный слой (быстро)                               │
│  Красный = полупрозрачный слой (GPU делает blending)                │
│                                                                       │
│  ┌───────────────────────────┐                                       │
│  │ ██████████████████████████│ ← Зелёный: backgroundColor = .white  │
│  │ ██████████████████████████│                                       │
│  │ ██████▓▓▓▓▓▓▓▓▓▓▓▓████████│ ← Красный: alpha = 0.8               │
│  │ ██████▓▓▓▓▓▓▓▓▓▓▓▓████████│   (GPU смешивает с фоном)            │
│  │ ██████████████████████████│                                       │
│  └───────────────────────────┘                                       │
│                                                                       │
│  Исправление:                                                        │
│  label.backgroundColor = .white  // Убрать прозрачность              │
│  view.isOpaque = true            // Пометить как непрозрачный        │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

COLOR OFFSCREEN-RENDERED
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  Жёлтый = слой рендерится offscreen (дорого!)                       │
│                                                                       │
│  Причины offscreen rendering:                                        │
│  • cornerRadius + masksToBounds                                      │
│  • shadow без shadowPath                                             │
│  • mask property                                                      │
│  • allowsGroupOpacity                                                │
│                                                                       │
│  ┌───────────────────────────┐                                       │
│  │ ┌───────────────────────┐ │                                       │
│  │ │ ░░░░░░░░░░░░░░░░░░░░░│ │ ← Жёлтый: cornerRadius = 10           │
│  │ │ ░░░░░░░░░░░░░░░░░░░░░│ │           masksToBounds = true        │
│  │ │ ░░░░░░░░░░░░░░░░░░░░░│ │                                        │
│  │ └───────────────────────┘ │                                       │
│  └───────────────────────────┘                                       │
│                                                                       │
│  Исправление:                                                        │
│  // Для cornerRadius                                                 │
│  view.layer.cornerRadius = 10                                        │
│  view.layer.cornerCurve = .continuous  // iOS 13+                    │
│  view.clipsToBounds = true                                           │
│  // ИЛИ использовать prerendered images                              │
│                                                                       │
│  // Для shadow - ВСЕГДА указывать shadowPath!                        │
│  view.layer.shadowPath = UIBezierPath(                               │
│      roundedRect: bounds,                                            │
│      cornerRadius: 10                                                │
│  ).cgPath                                                            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

COLOR HITS GREEN AND MISSES RED
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  Показывает эффективность shouldRasterize                           │
│  Зелёный = кэш используется (хорошо)                                │
│  Красный = кэш пересоздаётся (плохо)                                │
│                                                                       │
│  Когда использовать rasterization:                                  │
│  • Сложный статичный контент                                        │
│  • Не анимируется                                                    │
│  • Не меняет размер                                                  │
│                                                                       │
│  view.layer.shouldRasterize = true                                   │
│  view.layer.rasterizationScale = UIScreen.main.scale                │
│                                                                       │
│  ⚠️ Если всё красное - отключите rasterization!                     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Оптимизация рендеринга

```swift
// ❌ ПРОБЛЕМА: Offscreen rendering для каждой ячейки
class BadCell: UITableViewCell {
    override func awakeFromNib() {
        super.awakeFromNib()

        // Каждый кадр при скролле: offscreen render!
        imageView?.layer.cornerRadius = 20
        imageView?.layer.masksToBounds = true

        // Shadow без path = offscreen render!
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOpacity = 0.3
        layer.shadowRadius = 5
    }
}

// ✅ РЕШЕНИЕ: Оптимизированная ячейка
class GoodCell: UITableViewCell {
    override func awakeFromNib() {
        super.awakeFromNib()

        // Используем prerendered круглое изображение
        // ИЛИ для iOS 13+:
        imageView?.layer.cornerRadius = 20
        imageView?.layer.cornerCurve = .continuous
        imageView?.clipsToBounds = true

        // Shadow с path = GPU рисует напрямую
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOpacity = 0.3
        layer.shadowRadius = 5
    }

    override func layoutSubviews() {
        super.layoutSubviews()

        // Обновляем shadowPath при изменении размера
        layer.shadowPath = UIBezierPath(rect: bounds).cgPath
    }
}

// ❌ ПРОБЛЕМА: Прозрачные слои при скролле
class BadScrollCell: UICollectionViewCell {
    let label = UILabel()

    override init(frame: CGRect) {
        super.init(frame: frame)

        label.backgroundColor = .clear  // Alpha blending на каждый кадр!
    }
}

// ✅ РЕШЕНИЕ: Непрозрачный фон
class GoodScrollCell: UICollectionViewCell {
    let label = UILabel()

    override init(frame: CGRect) {
        super.init(frame: frame)

        label.backgroundColor = .white
        label.isOpaque = true
    }
}
```

---

## Network Profiling

### Network Instrument

```
┌─────────────────────────────────────────────────────────────────────┐
│  Network - MyApp.app                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  CONNECTIONS TIMELINE                                                │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Connection 1: api.myapp.com                                      ││
│  │ ├───┤ DNS  ├───┤ TCP ├───┤ TLS ├─────────┤ Transfer ├───┤     ││
│  │  10ms      15ms      45ms         250ms                         ││
│  │                                                                   ││
│  │ Connection 2: cdn.myapp.com                                      ││
│  │ ├─┤ DNS ├─┤ TCP ├─┤ TLS ├────────────────┤ Transfer ├────┤     ││
│  │  5ms     10ms    30ms            800ms (большой файл)           ││
│  │                                                                   ││
│  │ Connection 3: api.myapp.com (reused)                            ││
│  │                   ├─────────────┤ Transfer ├───┤                ││
│  │                        150ms (keep-alive!)                       ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  REQUEST DETAILS                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ URL         │ Method │ Status │ Size    │ Duration │ Timing    ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ /api/users  │ GET    │ 200    │ 45 KB   │ 320ms    │ DNS: 10ms ││
│  │             │        │        │         │          │ TCP: 15ms ││
│  │             │        │        │         │          │ TLS: 45ms ││
│  │             │        │        │         │          │ Req: 5ms  ││
│  │             │        │        │         │          │ Res: 245ms││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ /images/bg  │ GET    │ 200    │ 2.5 MB  │ 850ms    │ Cached:No ││
│  │ /api/feed   │ POST   │ 201    │ 128 KB  │ 180ms    │ Reused:Yes││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  PAYLOAD INSPECTION (при выборе запроса)                            │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Request Headers:                                                 ││
│  │   Content-Type: application/json                                 ││
│  │   Authorization: Bearer ***                                      ││
│  │                                                                   ││
│  │ Response Body:                                                   ││
│  │   { "users": [...], "total": 100, "page": 1 }                   ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Анализ сетевых проблем

```swift
// ❌ ПРОБЛЕМА 1: Последовательные запросы вместо параллельных
class BadNetworkManager {
    func loadData() async throws {
        // 3 запроса последовательно = сумма времени
        let users = try await fetchUsers()      // 200ms
        let posts = try await fetchPosts()      // 300ms
        let comments = try await fetchComments() // 150ms
        // Итого: 650ms
    }
}

// ✅ РЕШЕНИЕ: Параллельные запросы
class GoodNetworkManager {
    func loadData() async throws {
        // 3 запроса параллельно = максимальное время
        async let users = fetchUsers()      // 200ms ┐
        async let posts = fetchPosts()      // 300ms ├→ Итого: 300ms
        async let comments = fetchComments() // 150ms ┘

        let (u, p, c) = try await (users, posts, comments)
    }
}

// ❌ ПРОБЛЕМА 2: Нет HTTP/2 multiplexing
// Каждый запрос создаёт новое соединение

// ✅ РЕШЕНИЕ: Настроить URLSession для переиспользования
let config = URLSessionConfiguration.default
config.httpMaximumConnectionsPerHost = 6
config.timeoutIntervalForRequest = 30
config.urlCache = URLCache(
    memoryCapacity: 50 * 1024 * 1024,  // 50 MB
    diskCapacity: 100 * 1024 * 1024     // 100 MB
)

// ❌ ПРОБЛЕМА 3: Большие изображения без сжатия
// Network instrument показывает 2MB на каждую картинку

// ✅ РЕШЕНИЕ: Запрашивать нужный размер
func imageURL(for size: CGSize, scale: CGFloat) -> URL {
    let width = Int(size.width * scale)
    let height = Int(size.height * scale)
    return URL(string: "https://api.com/image?w=\(width)&h=\(height)")!
}
```

---

## MetricKit (Production)

### Настройка MXMetricManager

```swift
import MetricKit

class MetricsManager: NSObject, MXMetricManagerSubscriber {

    static let shared = MetricsManager()

    private override init() {
        super.init()
    }

    func start() {
        let manager = MXMetricManager.shared
        manager.add(self)

        // Получить прошлые отчёты сразу при запуске
        if let pastPayloads = manager.pastPayloads as? [MXMetricPayload] {
            for payload in pastPayloads {
                processPayload(payload)
            }
        }
    }

    // MARK: - MXMetricManagerSubscriber

    // Вызывается раз в ~24 часа с агрегированными метриками
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            processPayload(payload)
        }
    }

    // Вызывается для диагностики (hangs, crashes)
    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            processDiagnostic(payload)
        }
    }

    // MARK: - Processing

    private func processPayload(_ payload: MXMetricPayload) {
        // CPU метрики
        if let cpuMetrics = payload.cpuMetrics {
            let cumulativeCPU = cpuMetrics.cumulativeCPUTime
            let cpuInstructions = cpuMetrics.cumulativeCPUInstructions

            print("CPU Time: \(cumulativeCPU)")
            print("Instructions: \(cpuInstructions)")

            // Отправить в аналитику
            Analytics.track("cpu_metrics", properties: [
                "cumulative_time": cumulativeCPU.value,
                "instructions": cpuInstructions.value
            ])
        }

        // Memory метрики
        if let memoryMetrics = payload.memoryMetrics {
            let peakMemory = memoryMetrics.peakMemoryUsage
            let averageMemory = memoryMetrics.averageSuspendedMemory

            print("Peak Memory: \(peakMemory)")
            print("Average Suspended: \(averageMemory)")

            // Предупреждение о высоком потреблении
            if peakMemory.averageMeasurement.doubleValue(for: .megabytes) > 500 {
                Analytics.track("high_memory_usage", properties: [
                    "peak_mb": peakMemory.averageMeasurement.doubleValue(for: .megabytes)
                ])
            }
        }

        // Disk метрики
        if let diskMetrics = payload.diskIOMetrics {
            print("Disk Writes: \(diskMetrics.cumulativeLogicalWrites)")
        }

        // App Launch метрики (iOS 15.2+)
        if #available(iOS 15.2, *) {
            if let launchMetrics = payload.applicationLaunchMetrics {
                let histogrammedTimeToFirstDraw = launchMetrics.histogrammedTimeToFirstDraw

                // Анализ времени запуска
                print("Launch Times: \(histogrammedTimeToFirstDraw)")
            }
        }

        // Hang метрики
        if let responsiveMetrics = payload.applicationResponsivenessMetrics {
            let hangTime = responsiveMetrics.histogrammedApplicationHangTime
            print("Hang Time Distribution: \(hangTime)")
        }
    }

    private func processDiagnostic(_ payload: MXDiagnosticPayload) {
        // Hang диагностика
        if let hangDiagnostics = payload.hangDiagnostics {
            for hang in hangDiagnostics {
                print("Hang Duration: \(hang.hangDuration)")

                // Stack trace зависания
                if let callStackTree = hang.callStackTree {
                    let jsonData = callStackTree.jsonRepresentation()
                    // Отправить в Crashlytics/Sentry
                    CrashReporter.reportHang(
                        duration: hang.hangDuration,
                        stackTrace: jsonData
                    )
                }
            }
        }

        // Crash диагностика
        if let crashDiagnostics = payload.crashDiagnostics {
            for crash in crashDiagnostics {
                print("Crash Signal: \(crash.signal)")
                print("Exception Type: \(crash.exceptionType)")

                if let stackTree = crash.callStackTree {
                    CrashReporter.reportCrash(
                        signal: crash.signal,
                        exception: crash.exceptionType,
                        stackTrace: stackTree.jsonRepresentation()
                    )
                }
            }
        }

        // Disk Write диагностика (iOS 14+)
        if let diskWriteDiagnostics = payload.diskWriteExceptionDiagnostics {
            for diagnostic in diskWriteDiagnostics {
                print("Excessive Disk Writes: \(diagnostic.totalWritesCaused)")

                if let stackTree = diagnostic.callStackTree {
                    Analytics.track("excessive_disk_writes", properties: [
                        "total_writes": diagnostic.totalWritesCaused.value,
                        "stack": String(data: stackTree.jsonRepresentation(), encoding: .utf8) ?? ""
                    ])
                }
            }
        }
    }
}

// Использование в AppDelegate
@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        MetricsManager.shared.start()

        return true
    }
}
```

### Custom Metrics с os_signpost

```swift
import os.signpost

extension OSLog {
    static let performance = OSLog(
        subsystem: Bundle.main.bundleIdentifier ?? "com.myapp",
        category: "Performance"
    )
}

class ImageLoader {
    private let signpostID = OSSignpostID(log: .performance)

    func loadImage(url: URL) async throws -> UIImage {
        // Начало измерения
        os_signpost(
            .begin,
            log: .performance,
            name: "Image Load",
            signpostID: signpostID,
            "URL: %{public}@", url.absoluteString
        )

        defer {
            // Конец измерения (всегда выполнится)
            os_signpost(
                .end,
                log: .performance,
                name: "Image Load",
                signpostID: signpostID
            )
        }

        let (data, _) = try await URLSession.shared.data(from: url)

        guard let image = UIImage(data: data) else {
            throw ImageError.invalidData
        }

        return image
    }
}

// В Instruments: выбрать os_signpost instrument
// Увидите интервалы "Image Load" с URL и длительностью
```

### Анализ MetricKit данных

```
Типичные метрики и их пороги:

┌─────────────────────────────────────────────────────────────────────┐
│  МЕТРИКА                    │  ХОРОШО    │  ВНИМАНИЕ  │  ПРОБЛЕМА   │
├─────────────────────────────────────────────────────────────────────┤
│  Time to First Draw         │  < 400ms   │  400-800ms │  > 800ms    │
│  Resume Time                 │  < 100ms   │  100-200ms │  > 200ms    │
│  Peak Memory Usage           │  < 200MB   │  200-500MB │  > 500MB    │
│  Average Suspended Memory    │  < 50MB    │  50-100MB  │  > 100MB    │
│  Hang Rate (> 500ms)        │  < 0.1%    │  0.1-0.5%  │  > 0.5%     │
│  Cumulative CPU Time / Hour  │  < 60 sec  │  60-180s   │  > 180 sec  │
│  Disk Writes / Hour          │  < 100 MB  │  100-500MB │  > 500 MB   │
└─────────────────────────────────────────────────────────────────────┘

Интерпретация гистограмм:

Histogram: Time to First Draw
┌─────────────────────────────────────────────────────────────────────┐
│  Bucket         │ Count │ Percentage │ Visualization               │
├─────────────────────────────────────────────────────────────────────┤
│  0-100ms        │  450  │    45%     │ ████████████████████        │
│  100-200ms      │  300  │    30%     │ ████████████████            │
│  200-400ms      │  150  │    15%     │ ██████████                  │
│  400-800ms      │   70  │     7%     │ ████                        │
│  800ms-2s       │   25  │   2.5%     │ ██                          │
│  > 2s           │    5  │   0.5%     │ █ ← Исследовать эти случаи! │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Распространённые ошибки

### 1. Профилирование на симуляторе

```swift
// ❌ ОШИБКА: Профилирование Core Animation на симуляторе
// Симулятор использует CPU для рендеринга вместо GPU
// Результаты не отражают реальную производительность

// Instruments покажет:
// - Simulator: 15 FPS (всё "плохо")
// - Real device: 60 FPS (на самом деле норма)

// ✅ ПРАВИЛЬНО: Всегда профилировать на реальном устройстве
// Особенно для:
// - Core Animation
// - GPU Usage
// - Metal Performance
// - Thermal State

// Для Memory можно использовать симулятор,
// но memory pressure отличается от реальных устройств
```

### 2. Профилирование Debug билда

```swift
// ❌ ОШИБКА: Профилирование с Debug конфигурацией
// Debug содержит:
// - Отключенные оптимизации (-Onone)
// - Debug символы
// - Assertions и preconditions
// - Sanitizers (Address, Thread)

// Результат: код работает в 2-10 раз медленнее!

// ✅ ПРАВИЛЬНО: Profile конфигурация (Release + Debug Info)
// Xcode → Product → Profile (⌘I) автоматически использует Release

// Для ручного запуска:
// Edit Scheme → Profile → Build Configuration → Release
// + Debug Information Format → DWARF with dSYM File
```

### 3. Игнорирование Heaviest Stack Trace

```swift
// ❌ ОШИБКА: Смотреть только на Top Functions
// Top Functions показывает отдельные функции вне контекста

// Пример:
// Top Functions:
// 1. String.init(data:encoding:) - 25%
// 2. JSONDecoder.decode - 20%
// 3. Array.append - 15%

// Это не говорит, ОТКУДА вызываются эти функции!

// ✅ ПРАВИЛЬНО: Использовать Heaviest Stack Trace
// Показывает полный путь вызовов:
//
// loadAllData() →
//   parseResponse() →
//     JSONDecoder.decode() →
//       String.init(data:encoding:)
//
// Теперь понятно: проблема в loadAllData(), а не в String!
```

### 4. Не фильтрация системных библиотек

```swift
// ❌ ОШИБКА: Анализировать весь Call Tree включая Apple код
// 80% времени - это UIKit, Foundation, libsystem
// Вы не можете их оптимизировать!

// ✅ ПРАВИЛЬНО: Включить "Hide System Libraries"
// Показывает только ВАШ код
// Видно, какие ВАШИ функции вызывают медленные системные

// ✅ ТАКЖЕ ПОЛЕЗНО: "Invert Call Tree"
// Показывает "снизу вверх" - от медленных функций к вызывающему коду

// Call Tree Options для анализа:
// ☑ Separate by Thread
// ☑ Invert Call Tree
// ☑ Hide System Libraries
// ☑ Top Functions
```

### 5. Пропуск warmup при профилировании

```swift
// ❌ ОШИБКА: Сразу записывать после запуска
// Первые секунды включают:
// - JIT компиляцию (для Swift)
// - Загрузку dylibs
// - Инициализацию кэшей
// - First-run специфичный код

// Результат: искажённые данные о "нормальной" работе

// ✅ ПРАВИЛЬНО: Разогрев перед записью
// 1. Запустить приложение
// 2. Выполнить сценарий 1-2 раза без записи
// 3. Начать запись
// 4. Выполнить сценарий для измерения

// Для автоматизации:
func profileWithWarmup() {
    // Разогрев
    for _ in 0..<3 {
        performScenario()
    }

    // Сигнал для начала записи
    os_signpost(.event, log: .performance, name: "Start Recording")

    // Измеряемый сценарий
    performScenario()

    os_signpost(.event, log: .performance, name: "End Recording")
}
```

### 6. Не использование Memory Graph для retain cycles

```swift
// ❌ ОШИБКА: Искать retain cycles только через Leaks instrument
// Leaks находит только "orphaned" объекты
// Retain cycles с root reference НЕ показываются как leaks!

// Пример:
class RootVC: UIViewController {
    var child: ChildVC?  // strong
}

class ChildVC: UIViewController {
    var parent: RootVC?  // strong - CYCLE!
}

// RootVC держит ChildVC, ChildVC держит RootVC
// Но RootVC доступен из UIWindow → это не "leak" для Leaks instrument!

// ✅ ПРАВИЛЬНО: Использовать Memory Graph Debugger
// Xcode → Debug → Debug Memory Graph
// Показывает ВСЕ ссылки, включая cycles с root references

// Признаки retain cycle в Memory Graph:
// 1. Объект существует, хотя VC уже dismissed
// 2. Количество экземпляров растёт при навигации back/forth
// 3. deinit не вызывается при уходе с экрана
```

---

## Ментальные модели

### 1. Модель "Бутылочного горлышка"

```
Производительность определяется самым узким местом:

           ┌─────────────────────────────────────────────────┐
           │          ПОТОК ОБРАБОТКИ ДАННЫХ                  │
           └─────────────────────────────────────────────────┘

                    ║║║║║║║║║║║║║║║
                    ╔══════════════╗
          Network   ║   150 Mbps   ║  ← Широкое горлышко
                    ╚══════════════╝
                    ╔══════════════╗
           Parse    ║    JSON      ║  ← Среднее
                    ╚══════════════╝
                    ╔════╗
          Decode    ║IMG ║  ← УЗКОЕ МЕСТО! (Main Thread)
                    ╚════╝
                    ╔══════════════╗
          Display   ║   60 FPS     ║  ← Широкое
                    ╚══════════════╝

Правило: Оптимизировать нужно ТОЛЬКО бутылочное горлышко.
         Ускорение других частей не даст эффекта!

Применение к профилированию:
1. Time Profiler → найти самую "толстую" функцию
2. Оптимизировать ТОЛЬКО её
3. Повторить профилирование
4. Теперь горлышко сместится → оптимизировать новое
```

### 2. Модель "Водяного бака" для памяти

```
Память как бак с водой:

                    ┌───────────────────────────────────┐
      Max Memory →  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Jetsam KILL
  (1.5 GB)          │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
                    │                                   │
      Warning →     │═══════════════════════════════════│ ← Memory Warning
  (1.2 GB)          │███████████████████████████████████│
                    │███████████████████████████████████│
                    │█████████████████████████████░░░░░░│
                    │██████████████████████░░░░░░░░░░░░░│
      Current →     │█████████████████░░░░░░░░░░░░░░░░░░│ ← 800 MB используется
                    │████████████░░░░░░░░░░░░░░░░░░░░░░░│
                    │███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
      Baseline →    │███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← 200 MB постоянная память
                    └───────────────────────────────────┘

ПРИТОКИ воды (allocations):
┌──────────────────────────┐
│ • Загрузка изображений    │ ← Самый большой приток
│ • Создание view controllers│
│ • Кэширование данных       │
│ • Временные буферы         │
└──────────────────────────┘

СТОКИ воды (deallocations):
┌──────────────────────────┐
│ • ARC освобождение        │ ← Автоматический сток
│ • Cache eviction          │
│ • didReceiveMemoryWarning │ ← Аварийный сток
└──────────────────────────┘

ЗАСОРЫ (leaks/retain cycles):
┌──────────────────────────┐
│ • Retain cycles          │ ← Вода не уходит
│ • Strong delegates       │
│ • Closure captures       │
│ • NotificationCenter     │
│   observers              │
└──────────────────────────┘

Здоровое приложение: уровень колеблется около 400-600 MB
Проблемное приложение: уровень только растёт → переполнение
```

### 3. Модель "60 FPS бюджета"

```
Каждый кадр = 16.67 мс бюджета

Бюджет одного кадра при 60 FPS:
┌─────────────────────────────────────────────────────────────┐
│                    16.67 мс на всё                          │
├─────────────────────────────────────────────────────────────┤
│ Input │ Layout │  Draw  │ Commit │ Render │ Display │ Idle │
│  1ms  │  3ms   │  4ms   │  2ms   │  5ms   │  0.5ms  │ 1ms  │
│  ▓▓   │ ▓▓▓▓▓▓ │ ▓▓▓▓▓▓▓│ ▓▓▓▓   │ ▓▓▓▓▓▓▓│ ▓       │ ▓▓   │
└─────────────────────────────────────────────────────────────┘
                                                        ✅ 16ms OK

Проблема: Layout занимает слишком много времени
┌─────────────────────────────────────────────────────────────────────┐
│                    16.67 мс бюджет                              │
├─────────────────────────────────────────────────────────────────────┤
│ Input │    Layout (Auto Layout hell)    │ Draw │ Commit │ Render...
│  1ms  │          12ms                   │ 4ms  │  2ms   │ ...
│  ▓▓   │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │▓▓▓▓▓▓│ ▓▓▓▓   │ ▓▓▓▓▓▓
└─────────────────────────────────────────────────────────────────────┘
│                                                     ПРЕВЫШЕН → 24ms
│                                                     ❌ Dropped frame!

Правила бюджетирования:
1. Layout: < 4ms (Auto Layout complexity)
2. Draw: < 4ms (Custom drawing, text rendering)
3. Main Thread: < 10ms (оставить время на commit/render)
4. Offscreen: 0ms идеально (избегать масок, теней без path)

Если превышаете бюджет:
- 30 FPS = 33ms кадр = "заметные подёргивания"
- 20 FPS = 50ms кадр = "приложение лагает"
- 10 FPS = 100ms кадр = "приложение зависло"
```

### 4. Модель "Горячих путей"

```
Код выполняется с разной частотой:

┌─────────────────────────────────────────────────────────────────┐
│                    КОД ПРИЛОЖЕНИЯ                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ❄️ ХОЛОДНЫЙ ПУТЬ (редко, при запуске)                          │
│  ┌──────────────────────────────────────┐                        │
│  │ • application:didFinishLaunching     │ 1 раз за сессию       │
│  │ • Database migration                  │ 1 раз при обновлении  │
│  │ • Initial sync                        │ 1 раз при входе       │
│  └──────────────────────────────────────┘                        │
│                                                                   │
│  🌡️ ТЁПЛЫЙ ПУТЬ (умеренно, при навигации)                       │
│  ┌──────────────────────────────────────┐                        │
│  │ • viewDidLoad                         │ При переходе на экран │
│  │ • API запросы                         │ При обновлении        │
│  │ • Image loading                       │ При скролле           │
│  └──────────────────────────────────────┘                        │
│                                                                   │
│  🔥 ГОРЯЧИЙ ПУТЬ (постоянно, 60 раз/сек)                        │
│  ┌──────────────────────────────────────┐                        │
│  │ • cellForRow (при скролле)           │ 60 FPS × N ячеек      │
│  │ • layoutSubviews                      │ 60 FPS × M views      │
│  │ • scrollViewDidScroll                 │ 60 FPS постоянно      │
│  │ • CADisplayLink callback              │ 60/120 FPS            │
│  └──────────────────────────────────────┘                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

ПРАВИЛО ОПТИМИЗАЦИИ:
- Холодный путь: можно "дорогие" операции
- Тёплый путь: кэширование и асинхронность
- Горячий путь: КАЖДАЯ микросекунда критична!

В Time Profiler горячие пути будут показывать
высокий Weight даже для "простых" функций,
потому что они вызываются тысячи раз.

func cellForRow(...) {
    let formatter = DateFormatter()  // 💀 В горячем пути!
    // Создаётся 1000 раз при скролле
}

func cellForRow(...) {
    let formatted = cachedFormatter.string(from: date)  // ✅
    // Переиспользуется
}
```

### 5. Модель "Производитель-Потребитель"

```
Асинхронные операции как конвейер:

                    PRODUCER                      CONSUMER
                  (Background)                  (Main Thread)

        ┌───────────────────────────────┐    ┌─────────────────┐
        │                               │    │                 │
   ──►  │  Download → Parse → Transform │──►│     UI Update   │
        │                               │    │                 │
        └───────────────────────────────┘    └─────────────────┘


ПРОБЛЕМА 1: Producer быстрее Consumer (UI перегружен)

        ┌───────────────────────────────┐    ┌─────────────────┐
   ══►  │ ████████████████████████████ │══►│ ▓▓▓▓▓▓          │
        │   (загружает 100 картинок)    │    │ (UI не успевает)│
        └───────────────────────────────┘    └─────────────────┘

        Симптом: Main Thread 100%, UI freezes
        Решение: Throttling, batching updates


ПРОБЛЕМА 2: Consumer быстрее Producer (пустой UI)

        ┌───────────────────────────────┐    ┌─────────────────┐
   ─►   │ ▓▓                            │─►│ ████████████████│
        │   (медленный сервер)          │    │   (ждёт данные)  │
        └───────────────────────────────┘    └─────────────────┘

        Симптом: Долгие спиннеры, пустые экраны
        Решение: Prefetching, caching, optimistic UI


ПРОБЛЕМА 3: Затор между Producer и Consumer

        ┌───────────────────────────────┐ X ┌─────────────────┐
   ══►  │ ████████████████████████████ │ X │                 │
        │   (много данных)              │ X │ (Main занят)    │
        └───────────────────────────────┘ X └─────────────────┘
                                         ▲
                                    Очередь переполнена!

        Симптом: Memory рост, eventual crash
        Решение: Backpressure, queue limits

Network Profiler показывает Producer
Time Profiler показывает Consumer
Memory показывает затор между ними
```

---

## Проверь себя

### Вопрос 1: Time Profiler показывает высокую нагрузку

```
Time Profiler показывает:

Weight   Self Weight   Symbol
85.2%    0.0%          -[ViewController viewDidLoad]
└ 82.1%  78.5%         -[DataManager loadAllData]
  └ 3.6%  3.6%         JSONDecoder.decode

Какая функция - реальная проблема и почему?
```

<details>
<summary>Ответ</summary>

**Проблема в `loadAllData`**, потому что:

1. **Self Weight = 78.5%** - это время, проведённое ВНУТРИ функции, не включая вызовы других функций

2. `viewDidLoad` имеет Self Weight = 0%, значит он просто вызывает другие функции, сам не делает работу

3. `JSONDecoder.decode` имеет только 3.6% - это Apple код, который мы не можем оптимизировать

4. 78.5% в `loadAllData` означает, что там происходит тяжёлая синхронная операция (вероятно, чтение файла или блокирующий сетевой запрос)

**Решение**: Сделать `loadAllData` асинхронной операцией на background queue

</details>

### Вопрос 2: Memory Graph показывает retain cycle

```swift
class ProfileVC: UIViewController {
    var viewModel: ProfileViewModel!

    override func viewDidLoad() {
        super.viewDidLoad()

        viewModel.onUpdate = {
            self.updateUI()
        }
    }

    func updateUI() {
        // обновление UI
    }

    deinit {
        print("ProfileVC deinit") // Никогда не вызывается!
    }
}

class ProfileViewModel {
    var onUpdate: (() -> Void)?
}
```

Что вызывает retain cycle и как исправить?

<details>
<summary>Ответ</summary>

**Причина retain cycle:**

```
ProfileVC ──strong──► ProfileViewModel
    ▲                        │
    │                        │ onUpdate closure
    │                        ▼
    └────────strong────── Closure (captures self)
```

1. `ProfileVC` держит `viewModel` как strong property
2. `viewModel.onUpdate` - это closure, которая захватывает `self` (ProfileVC) как strong по умолчанию
3. Круг замкнулся: VC → VM → Closure → VC

**Решения:**

```swift
// Решение 1: [weak self] в closure
viewModel.onUpdate = { [weak self] in
    self?.updateUI()
}

// Решение 2: [unowned self] если уверены в lifecycle
viewModel.onUpdate = { [unowned self] in
    self.updateUI()  // Краш если VC уже deallocated
}

// Решение 3: Обнулить closure в deinit (если [weak self] нельзя)
deinit {
    viewModel.onUpdate = nil
}
```

Рекомендуется **Решение 1** с `[weak self]` как самое безопасное.

</details>

### Вопрос 3: Core Animation показывает жёлтые слои

```swift
class ProductCell: UICollectionViewCell {
    let imageView = UIImageView()
    let shadowView = UIView()

    override init(frame: CGRect) {
        super.init(frame: frame)

        imageView.layer.cornerRadius = 12
        imageView.layer.masksToBounds = true

        shadowView.layer.shadowColor = UIColor.black.cgColor
        shadowView.layer.shadowOpacity = 0.2
        shadowView.layer.shadowRadius = 8
        shadowView.layer.shadowOffset = CGSize(width: 0, height: 4)
    }
}
```

Color Offscreen-Rendered Yellow показывает жёлтые слои на каждой ячейке. Как оптимизировать?

<details>
<summary>Ответ</summary>

**Проблемы:**

1. `cornerRadius + masksToBounds` = offscreen rendering для каждого кадра
2. `shadow без shadowPath` = GPU вычисляет форму тени каждый кадр

**Оптимизированное решение:**

```swift
class ProductCell: UICollectionViewCell {
    let imageView = UIImageView()
    let shadowView = UIView()

    override init(frame: CGRect) {
        super.init(frame: frame)

        // Для cornerRadius: использовать cornerCurve (iOS 13+)
        imageView.layer.cornerRadius = 12
        imageView.layer.cornerCurve = .continuous
        imageView.clipsToBounds = true
        // Или: предварительно скруглять изображения на background thread

        // Настройка тени (без shadowPath пока)
        shadowView.layer.shadowColor = UIColor.black.cgColor
        shadowView.layer.shadowOpacity = 0.2
        shadowView.layer.shadowRadius = 8
        shadowView.layer.shadowOffset = CGSize(width: 0, height: 4)
    }

    override func layoutSubviews() {
        super.layoutSubviews()

        // КРИТИЧНО: установить shadowPath после layout
        shadowView.layer.shadowPath = UIBezierPath(
            roundedRect: shadowView.bounds,
            cornerRadius: 12
        ).cgPath
    }

    // Альтернатива для статичного контента:
    func enableRasterization() {
        // Кэшировать отрендеренный слой
        layer.shouldRasterize = true
        layer.rasterizationScale = UIScreen.main.scale
        // Используйте только если контент НЕ меняется часто!
    }
}
```

После оптимизации жёлтые слои должны исчезнуть.

</details>

### Вопрос 4: MetricKit показывает hangs

```
MXHangDiagnostic:
- hangDuration: 2.5 seconds
- callStackTree:
    main
    └─ UIApplicationMain
       └─ -[AppDelegate application:didFinishLaunchingWithOptions:]
          └─ -[DatabaseManager synchronousMigration]
             └─ sqlite3_exec
```

Что показывает этот stack trace и как исправить?

<details>
<summary>Ответ</summary>

**Анализ:**

1. **Hang 2.5 секунды** на main thread - это серьёзная проблема (порог Apple: 500ms)

2. **Место зависания**: `synchronousMigration` в `application:didFinishLaunchingWithOptions:`

3. **Причина**: Синхронная миграция базы данных блокирует main thread при запуске приложения

**Влияние:**
- Пользователь видит замороженный launch screen 2.5 секунды
- Apple может отклонить обновление (hang rate > 0.1%)
- Плохие отзывы: "Приложение зависает при запуске"

**Исправление:**

```swift
// ❌ БЫЛО: Синхронная миграция на main thread
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: ...) -> Bool {
    DatabaseManager.shared.synchronousMigration() // 2.5 sec hang!
    return true
}

// ✅ СТАЛО: Асинхронная миграция + UI состояние "загрузка"
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: ...) -> Bool {

    // Показать loading UI
    window?.rootViewController = LoadingViewController()

    // Миграция в background
    Task.detached(priority: .userInitiated) {
        await DatabaseManager.shared.migrateAsync()

        await MainActor.run {
            // Переключить на main UI после миграции
            self.window?.rootViewController = MainTabBarController()
        }
    }

    return true
}

// Или с комбинированным подходом:
func application(...) -> Bool {
    // Быстрая проверка: нужна ли миграция?
    if DatabaseManager.shared.needsMigration {
        showMigrationUI()
        performBackgroundMigration()
    } else {
        showMainUI() // Мгновенный запуск
    }
    return true
}
```

</details>

---

## Связанные темы

### Prerequisites (Изучить сначала)

```
[[ios-view-rendering]]
├─ Как работает render loop
├─ CALayer и композитинг
└─ Понимание offscreen rendering

[[ios-process-memory]]
├─ ARC и reference counting
├─ Strong/weak/unowned
└─ Retain cycles
```

### Next Steps (Изучить далее)

```
[[ios-scroll-performance]]
├─ Cell prefetching
├─ Image caching strategies
└─ Diffable data sources

[[ios-app-launch-optimization]]
├─ Cold vs warm launch
├─ dyld и linking
└─ Pre-main optimization
```

### Related Topics

```
[[ios-debugging]]
├─ LLDB и breakpoints
├─ Debug View Hierarchy
└─ Console и logs

[[ios-energy-profiling]]
├─ Energy Impact
├─ Location & Networking
└─ Background modes

[[swift-performance]]
├─ Value types vs reference types
├─ Copy-on-write
└─ Compiler optimizations
```

---

## Источники

### Официальная документация

- [Instruments User Guide](https://developer.apple.com/documentation/xcode/instruments) - Apple Documentation
- [MetricKit Framework](https://developer.apple.com/documentation/metrickit) - Apple Documentation
- [Improving Your App's Performance](https://developer.apple.com/documentation/xcode/improving-your-app-s-performance) - Apple Documentation

### WWDC Sessions

- [WWDC 2023: Analyze hangs with Instruments](https://developer.apple.com/videos/play/wwdc2023/10248/)
- [WWDC 2022: Track down hangs with Xcode and on-device detection](https://developer.apple.com/videos/play/wwdc2022/10082/)
- [WWDC 2021: Understand and eliminate hangs from your app](https://developer.apple.com/videos/play/wwdc2021/10258/)
- [WWDC 2020: What's new in MetricKit](https://developer.apple.com/videos/play/wwdc2020/10081/)
- [WWDC 2019: Getting Started with Instruments](https://developer.apple.com/videos/play/wwdc2019/411/)
- [WWDC 2019: Developing a Great Profiling Experience](https://developer.apple.com/videos/play/wwdc2019/414/)
- [WWDC 2018: Practical Approaches to Great App Performance](https://developer.apple.com/videos/play/wwdc2018/407/)
- [WWDC 2018: iOS Memory Deep Dive](https://developer.apple.com/videos/play/wwdc2018/416/)

### Дополнительные ресурсы

- [Advanced Memory Management Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/MemoryMgmt/Articles/MemoryMgmt.html) - Apple Archives
- [Core Animation Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreAnimation_guide/Introduction/Introduction.html) - Apple Archives

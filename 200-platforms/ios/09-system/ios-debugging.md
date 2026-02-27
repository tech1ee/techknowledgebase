---
title: "iOS Debugging: LLDB, breakpoints, crash analysis"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 69
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/debugging
  - level/intermediate
related:
  - "[[ios-performance-profiling]]"
  - "[[android-performance-profiling]]"
  - "[[jvm-production-debugging]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-xcode-fundamentals]]"
---

# iOS Debugging: LLDB, breakpoints, crash analysis

## TL;DR

iOS debugging охватывает мощный набор инструментов: LLDB для интерактивной отладки, breakpoints для остановки выполнения, view debugging для UI-проблем и sanitizers для поиска ошибок памяти. Мастерство отладки превращает часы поиска багов в минуты целенаправленной диагностики. Crash analysis и symbolication позволяют понять причины падений даже в production-сборках.

---

## Зачем это нужно?

**Экономия времени** — опытный отладчик находит баг за 10 минут там, где новичок потратит 3 часа с print-statements.

**Понимание системы** — debugging раскрывает внутреннюю работу приложения: как данные текут через слои, когда вызываются методы, как меняется состояние.

**Production-готовность** — умение читать crash logs и символизировать стеки означает способность чинить баги, которые видят только пользователи.

**Сложные баги** — race conditions, memory corruption, layout issues невозможно найти print-ами. Нужны специализированные инструменты.

---

## Теоретические основы

> **Debugging** — процесс обнаружения, локализации и устранения дефектов в программном обеспечении. Термин приписывают Грейс Хоппер (1947), обнаружившей моль в реле компьютера Harvard Mark II. Современный debugging в iOS основан на LLDB — отладчике из проекта LLVM, реализующем модель **stop-the-world inspection**: приостановка процесса для анализа его состояния.

### Академический контекст

Debugging в iOS использует фундаментальные техники отладки:

| Концепция | Автор / год | Суть | Проявление в iOS |
|-----------|-------------|------|-------------------|
| Breakpoint | Первые отладчики, 1960-е | Остановка выполнения в заданной точке | LLDB breakpoints (line, symbolic, conditional, exception) |
| Watchpoint | Hardware debugging | Остановка при изменении значения памяти | LLDB watchpoint set variable, hardware-accelerated |
| Symbolic Debugging | DWARF format, 1992 | Маппинг машинного кода на исходный код | dSYM файлы для symbolication crash logs |
| Post-mortem Debugging | Core dumps, 1960-е | Анализ состояния после краша | Crash logs, symbolication, MetricKit |
| Sanitizers | Google, 2010-е | Инструментация кода для обнаружения ошибок | ASan (Address), TSan (Thread), UBSan (Undefined Behavior) |

### Инструменты отладки в iOS

| Инструмент | Тип | Что находит | Overhead |
|-----------|-----|-------------|----------|
| LLDB | Interactive debugger | Любые баги через inspection | Замедление ~2x |
| Address Sanitizer (ASan) | Runtime instrumentation | Use-after-free, buffer overflow | ~2x memory, ~2x speed |
| Thread Sanitizer (TSan) | Runtime instrumentation | Data races, deadlocks | ~5-10x speed |
| Memory Graph Debugger | Snapshot analysis | Retain cycles, leaks | Минимальный |
| View Debugger | UI inspection | Layout issues, clipping, z-order | Минимальный |

> **Закон Луковски**: «Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it» (Brian Kernighan, *The Elements of Programming Style*, 1974). Это мотивирует написание простого, явного кода вместо «умных» однострочников.

### Связь с CS-фундаментом

- [[ios-performance-profiling]] — Instruments как дополнение к debugging (профилирование vs отладка)
- [[ios-compilation-pipeline]] — dSYM генерируется при компиляции; DWARF debug info
- [[ios-threading-fundamentals]] — TSan для поиска race conditions в многопоточном коде
- [[ios-process-memory]] — ASan для поиска ошибок работы с памятью
- [[jvm-production-debugging]] — сравнение: LLDB vs JDB/IntelliJ debugger

---

## Аналогии из жизни

### LLDB = Детектив на месте преступления

```
┌─────────────────────────────────────────────────────────┐
│                  МЕСТО ПРЕСТУПЛЕНИЯ                      │
│  ┌─────┐                                                │
│  │ 🔍  │  Детектив может:                               │
│  └─────┘  • Остановить время (breakpoint)              │
│           • Осмотреть улики (po, p, v)                 │
│           • Проследить путь (backtrace)                │
│           • Изменить улики для эксперимента (expr)     │
│           • Поставить ловушку (watchpoint)             │
└─────────────────────────────────────────────────────────┘
```

LLDB — это детектив, который может "заморозить" время в момент преступления (краша), осмотреть все улики (переменные), опросить свидетелей (стек вызовов) и даже провести эксперименты (изменить значения на лету).

### Breakpoint = Стоп-кран в поезде

Поезд (программа) мчится по рельсам. Стоп-кран (breakpoint) мгновенно останавливает его в нужной точке. Можно выйти, осмотреться, проверить груз (состояние), а потом продолжить движение.

### Stack Trace = Хлебные крошки Гензеля

```
main() → AppDelegate → ViewController → loadData() → parseJSON() → 💥 CRASH
  ↑         ↑              ↑               ↑            ↑
  🍞        🍞             🍞              🍞           🍞
```

Каждый вызов функции оставляет "крошку". Когда происходит краш, мы можем пройти по крошкам назад и найти, откуда пришли.

### Watchpoint = Сигнализация на двери

Вместо того чтобы постоянно проверять, открыта ли дверь, ставим сигнализацию. Она сработает автоматически, когда кто-то тронет дверь (изменит переменную).

### Symbolic Breakpoint = Ловушка на имя

Не знаем, где именно вор (баг), но знаем его имя (название метода). Ставим ловушку на это имя — и поймаем его в любом месте программы: `objc_exception_throw`, `swift_willThrow`.

---

## LLDB Fundamentals

### Архитектура отладки

```
┌──────────────────────────────────────────────────────────────┐
│                         Xcode IDE                            │
│  ┌────────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │ Debug Navigator│  │ Variables View  │  │ Console (LLDB)│ │
│  └───────┬────────┘  └────────┬────────┘  └───────┬───────┘ │
└──────────┼─────────────────────┼──────────────────┼──────────┘
           │                     │                  │
           └─────────────────────┼──────────────────┘
                                 ▼
                    ┌────────────────────────┐
                    │      LLDB Debugger     │
                    │  ┌──────────────────┐  │
                    │  │ Command Interpreter│ │
                    │  └────────┬─────────┘  │
                    │           ▼            │
                    │  ┌──────────────────┐  │
                    │  │  Debug Server    │  │
                    │  │  (debugserver)   │  │
                    │  └────────┬─────────┘  │
                    └───────────┼────────────┘
                                ▼
                    ┌────────────────────────┐
                    │   Target Process       │
                    │   (Your App)           │
                    │  ┌──────────────────┐  │
                    │  │ Threads, Memory, │  │
                    │  │ Registers, Stack │  │
                    │  └──────────────────┘  │
                    └────────────────────────┘
```

### Основные команды LLDB

#### Печать значений: po, p, v

```
┌─────────────────────────────────────────────────────────────┐
│ Команда │ Что делает              │ Скорость │ Побочки     │
├─────────────────────────────────────────────────────────────┤
│ v       │ Читает из памяти        │ Быстро   │ Нет         │
│ p       │ Компилирует выражение   │ Средне   │ Возможны    │
│ po      │ p + description         │ Медленно │ Вызов кода  │
└─────────────────────────────────────────────────────────────┘
```

```lldb
# v (frame variable) — самый быстрый, без побочных эффектов
(lldb) v user
(User) user = {
  name = "Alice"
  age = 25
}

# v с путём к свойству
(lldb) v user.name
(String) user.name = "Alice"

# p (print) — компилирует выражение
(lldb) p user.name.count
(Int) $0 = 5

# p с вычислениями
(lldb) p user.age * 2
(Int) $1 = 50

# po (print object) — вызывает debugDescription
(lldb) po user
User(name: "Alice", age: 25, verified: true)

# po для коллекций
(lldb) po users.map { $0.name }
["Alice", "Bob", "Charlie"]
```

#### Expression — изменение на лету

```lldb
# Изменить значение переменной
(lldb) expression user.name = "Bob"

# Сокращённая форма
(lldb) e user.age = 30

# Вызвать метод
(lldb) e user.validate()

# Создать временную переменную
(lldb) e let temp = user.name.uppercased()
(lldb) po temp
"ALICE"

# Изменить UI (полезно для отладки)
(lldb) e view.backgroundColor = UIColor.red
(lldb) e CATransaction.flush()  // Применить изменения
```

#### Backtrace — стек вызовов

```lldb
# Полный стек
(lldb) bt
* thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
  * frame #0: 0x1234 MyApp`ViewController.loadData() at ViewController.swift:45
    frame #1: 0x5678 MyApp`ViewController.viewDidLoad() at ViewController.swift:20
    frame #2: 0x9abc UIKitCore`-[UIViewController _sendViewDidLoadWithAppearanceProxyObjectTaggingEnabled]
    frame #3: 0xdef0 UIKitCore`-[UIViewController loadViewIfRequired]
    ...

# Ограничить глубину
(lldb) bt 5

# Стек всех потоков
(lldb) bt all
```

#### Frame — навигация по стеку

```lldb
# Выбрать фрейм по номеру
(lldb) frame select 2
(lldb) f 2  # Сокращённо

# Информация о текущем фрейме
(lldb) frame info

# Переменные в текущем фрейме
(lldb) frame variable
(lldb) fr v  # Сокращённо

# Подняться/спуститься по стеку
(lldb) up
(lldb) down
```

#### Register — работа с регистрами

```lldb
# Все регистры
(lldb) register read

# Конкретный регистр
(lldb) register read x0

# На ARM64: x0 = return value / first argument
(lldb) register read x0 x1 x2

# Записать в регистр (осторожно!)
(lldb) register write x0 42
```

### Полезные LLDB алиасы

```lldb
# В ~/.lldbinit можно добавить:
command alias poc expression -l objc -O --
command alias pjson expression print(String(data: try! JSONSerialization.data(withJSONObject: %1, options: .prettyPrinted), encoding: .utf8)!)
```

---

## Breakpoints

### Типы breakpoints

```
┌─────────────────────────────────────────────────────────────┐
│                    ВИДЫ BREAKPOINTS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ● Line Breakpoint      → Конкретная строка кода           │
│  ◐ Conditional          → Срабатывает при условии          │
│  ◈ Symbolic             → По имени функции/метода          │
│  ⚡ Exception           → При выбросе исключения           │
│  ◉ Runtime Issue        → Memory/Thread issues             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Regular Breakpoints

```swift
// Кликнуть на номер строки в Xcode
// или через LLDB:

func processUser(_ user: User) {
    let validated = user.validate()  // ← Breakpoint здесь
    saveToDatabase(validated)
}
```

```lldb
# Установить по файлу и строке
(lldb) breakpoint set --file ViewController.swift --line 45
(lldb) b ViewController.swift:45  # Сокращённо

# Установить по имени функции
(lldb) b processUser

# Список всех breakpoints
(lldb) breakpoint list
(lldb) br l

# Удалить breakpoint
(lldb) breakpoint delete 1
(lldb) br del 1

# Временно отключить
(lldb) breakpoint disable 1
(lldb) br dis 1
```

### Conditional Breakpoints

```swift
// Срабатывает только когда user.id == 42
for user in users {
    processUser(user)  // ← Conditional breakpoint
}
```

```lldb
# Через LLDB
(lldb) breakpoint set -f ViewController.swift -l 50 -c "user.id == 42"

# Изменить условие существующего
(lldb) breakpoint modify -c "count > 100" 1
```

**В Xcode:** ПКМ на breakpoint → Edit Breakpoint → Condition

```
┌─────────────────────────────────────────┐
│ Edit Breakpoint                         │
├─────────────────────────────────────────┤
│ Condition: user.name == "admin"         │
│ Ignore: 10 times before stopping        │
│ Action: Log Message / Sound / Command   │
│ Options: ☑ Automatically continue       │
└─────────────────────────────────────────┘
```

### Symbolic Breakpoints

```
┌─────────────────────────────────────────────────────────────┐
│              ВАЖНЫЕ SYMBOLIC BREAKPOINTS                    │
├─────────────────────────────────────────────────────────────┤
│ Symbol                      │ Когда срабатывает             │
├─────────────────────────────────────────────────────────────┤
│ objc_exception_throw        │ ObjC exception thrown         │
│ swift_willThrow             │ Swift error will be thrown    │
│ UIViewAlertForUnsatisfiable │ Auto Layout конфликт          │
│   ConstraintsOnMain         │                               │
│ -[UIApplication main]       │ Запуск приложения             │
│ malloc_error_break          │ Ошибка аллокации памяти       │
│ _swift_runtime_on_report    │ Swift runtime error           │
└─────────────────────────────────────────────────────────────┘
```

```lldb
# Symbolic breakpoint через LLDB
(lldb) breakpoint set -n objc_exception_throw
(lldb) br s -n swift_willThrow

# На метод класса
(lldb) br s -n "-[UIViewController viewDidLoad]"

# Regex для имени
(lldb) breakpoint set --func-regex ".*viewDidLoad.*"
```

### Exception Breakpoints

**В Xcode:** Debug Navigator → + → Exception Breakpoint

```
┌─────────────────────────────────────────┐
│ Exception Breakpoint                    │
├─────────────────────────────────────────┤
│ Exception: All / Objective-C / C++      │
│ Break: On Throw / On Catch              │
│ Action: po $arg1 (для ObjC exceptions)  │
└─────────────────────────────────────────┘
```

```lldb
# Все ObjC exceptions
(lldb) breakpoint set -E objc

# При throw (не catch)
(lldb) breakpoint set -E objc -w 0

# Swift errors
(lldb) breakpoint set -n swift_willThrow
```

### Breakpoint Actions

```
┌─────────────────────────────────────────────────────────────┐
│                   BREAKPOINT ACTIONS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📝 Log Message    → Печать без остановки                  │
│     "User: @user.name@, ID: @user.id@"                     │
│                                                             │
│  🔊 Sound          → Звуковой сигнал                       │
│                                                             │
│  🖥  Shell Command  → Запуск скрипта                        │
│                                                             │
│  ⌨️  Debugger Cmd   → LLDB команда                          │
│     "po user"                                               │
│                                                             │
│  ☑️  Auto-continue  → Не останавливаться                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

```lldb
# Breakpoint с командой
(lldb) breakpoint set -f ViewController.swift -l 45
(lldb) breakpoint command add 1
> po user
> bt 3
> continue
> DONE

# Breakpoint с автопродолжением (logging)
(lldb) breakpoint set -f ViewController.swift -l 45 -o true
(lldb) breakpoint command add 1
> po "Reached line 45 with user: \(user.name)"
> DONE
```

---

## Watchpoints

### Что такое watchpoint

```
┌─────────────────────────────────────────────────────────────┐
│                      WATCHPOINT                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Обычный breakpoint:  "Остановись на строке 45"           │
│                                                             │
│   Watchpoint:          "Остановись когда эта                │
│                         переменная изменится"               │
│                                                             │
│   ┌─────────┐          ┌─────────┐                         │
│   │ counter │    →     │ counter │                         │
│   │   = 5   │  WRITE   │   = 6   │  ⚡ STOP!               │
│   └─────────┘          └─────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Когда использовать

- Переменная меняется, но непонятно откуда
- Свойство неожиданно становится nil
- Отслеживание записи в конкретный адрес памяти
- Поиск race conditions (кто меняет состояние?)

### Установка watchpoints

```lldb
# На переменную (нужно быть на breakpoint где она видна)
(lldb) watchpoint set variable user.name
(lldb) w s v user.name  # Сокращённо

# На адрес памяти
(lldb) watchpoint set expression -- &user.age
(lldb) w s e -- 0x7fff5fbff8c0

# Типы watchpoints
(lldb) watchpoint set variable -w read user.name      # При чтении
(lldb) watchpoint set variable -w write user.name     # При записи (default)
(lldb) watchpoint set variable -w read_write user.name # Оба

# Список watchpoints
(lldb) watchpoint list

# Удалить
(lldb) watchpoint delete 1
```

### Пример использования

```swift
class GameState {
    var score: Int = 0  // Кто-то меняет score неожиданно!
}

// В LLDB когда остановились на breakpoint:
// (lldb) w s v gameState.score
// Теперь при любом изменении score — автостоп
```

```
Watchpoint 1 hit:
old value: 100
new value: 0
    frame #0: 0x1234 MyApp`resetGame() at GameManager.swift:78
    frame #1: 0x5678 MyApp`buttonTapped() at ViewController.swift:34
```

---

## View Debugging

### Debug View Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                DEBUG VIEW HIERARCHY                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Debug → View Debugging → Capture View Hierarchy            │
│                    или                                      │
│  Кнопка 📐 в Debug bar                                      │
│                                                             │
│  ┌──────────────────────────────────────┐                  │
│  │         3D View Hierarchy            │                  │
│  │                                       │                  │
│  │    ┌─────────────────┐               │                  │
│  │    │    UIWindow     │ ←── Слой 1    │                  │
│  │    └────────┬────────┘               │                  │
│  │             │                         │                  │
│  │    ┌────────┴────────┐               │                  │
│  │    │ UIViewController│ ←── Слой 2    │                  │
│  │    │      .view      │               │                  │
│  │    └────────┬────────┘               │                  │
│  │             │                         │                  │
│  │    ┌────────┴────────┐               │                  │
│  │    │   UITableView   │ ←── Слой 3    │                  │
│  │    └─────────────────┘               │                  │
│  │                                       │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Constraint Debugging

```swift
// Symbolic breakpoint для Auto Layout проблем:
// UIViewAlertForUnsatisfiableConstraintsOnMain

// Или в коде:
UserDefaults.standard.set(true, forKey: "_UIConstraintBasedLayoutLogUnsatisfiable")
```

```
┌─────────────────────────────────────────────────────────────┐
│ CONSOLE OUTPUT: Unsatisfiable Constraints                   │
├─────────────────────────────────────────────────────────────┤
│ Unable to simultaneously satisfy constraints:               │
│   NSLayoutConstraint:0x600 H:[UILabel:0x123(100)]          │
│   NSLayoutConstraint:0x601 H:[UILabel:0x123(200)]          │
│                                                             │
│ Will attempt to recover by breaking constraint:             │
│   NSLayoutConstraint:0x600 H:[UILabel:0x123(100)]          │
│                                                             │
│ 💡 Add UIViewLayoutFeedbackLoopDebuggingThreshold           │
│    to Arguments in scheme                                   │
└─────────────────────────────────────────────────────────────┘
```

### LLDB команды для UI

```lldb
# Напечатать иерархию view
(lldb) expression -l objc -O -- [UIWindow.keyWindow recursiveDescription]

# Найти view по адресу
(lldb) e let $view = unsafeBitCast(0x7f8123456789, to: UIView.self)
(lldb) po $view

# Изменить и увидеть результат
(lldb) e $view.backgroundColor = UIColor.red
(lldb) e CATransaction.flush()

# Constraint debugging
(lldb) expression -l objc -O -- [0x7f8123456789 constraintsAffectingLayoutForAxis:0]
(lldb) expression -l objc -O -- [0x7f8123456789 _autolayoutTrace]
```

### View Debugging в LLDB

```lldb
# Кастомный скрипт для печати view hierarchy
command regex -- pv 's/(.+)/expression -l objc -O -- [%1 recursiveDescription]/'

# Использование
(lldb) pv self.view
```

---

## Memory Debugging

### Sanitizers

```
┌─────────────────────────────────────────────────────────────┐
│                      SANITIZERS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ASan (Address Sanitizer)                                   │
│  ├── Buffer overflow                                        │
│  ├── Use-after-free                                         │
│  ├── Use-after-return                                       │
│  └── Double free                                            │
│                                                             │
│  TSan (Thread Sanitizer)                                    │
│  ├── Data races                                             │
│  ├── Thread leaks                                           │
│  └── Deadlocks                                              │
│                                                             │
│  UBSan (Undefined Behavior Sanitizer)                       │
│  ├── Integer overflow                                       │
│  ├── Null pointer dereference                               │
│  ├── Misaligned pointer                                     │
│  └── Invalid shift                                          │
│                                                             │
│  ⚠️  ASan и TSan несовместимы! Только один за раз.          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Включение Sanitizers

**Xcode:** Scheme → Edit Scheme → Run → Diagnostics

```
┌─────────────────────────────────────────┐
│ Diagnostics                             │
├─────────────────────────────────────────┤
│ Runtime Sanitization:                   │
│   ☑ Address Sanitizer                   │
│   ☐ Thread Sanitizer                    │
│   ☑ Undefined Behavior Sanitizer        │
│                                         │
│ Memory Management:                      │
│   ☑ Malloc Stack Logging               │
│   ☑ Malloc Guard Edges                  │
└─────────────────────────────────────────┘
```

### Memory Graph Debugger

```
┌─────────────────────────────────────────────────────────────┐
│              MEMORY GRAPH DEBUGGER                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Debug → View Debugging → Capture Memory Graph              │
│                    или                                      │
│  Кнопка 🔗 в Debug bar                                      │
│                                                             │
│  Показывает:                                                │
│  • Все живые объекты                                        │
│  • Reference graph (кто держит кого)                        │
│  • Retain cycles (⚠️ фиолетовые warnings)                   │
│  • Leaked memory                                            │
│                                                             │
│       ┌──────────┐         ┌──────────┐                    │
│       │ Object A │────────→│ Object B │                    │
│       └──────────┘         └─────┬────┘                    │
│            ↑                     │                          │
│            └─────────────────────┘                          │
│                 RETAIN CYCLE ⚠️                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Malloc Stack Logging

```lldb
# После включения в Diagnostics:
(lldb) command script import lldb.macosx.heap

# Найти кто аллоцировал объект
(lldb) malloc_info --stack-history 0x7f8123456789

# История malloc для адреса
(lldb) memory history 0x7f8123456789
```

---

## Crash Analysis

### Анатомия crash log

```
┌─────────────────────────────────────────────────────────────┐
│                    CRASH LOG STRUCTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Header                                                  │
│     • Process, Bundle ID, Version                           │
│     • OS Version, Device Model                              │
│     • Date/Time                                             │
│                                                             │
│  2. Exception Information                                   │
│     • Exception Type: EXC_BAD_ACCESS (SIGSEGV)             │
│     • Exception Subtype: KERN_INVALID_ADDRESS              │
│     • Termination Reason                                    │
│                                                             │
│  3. Triggered Thread                                        │
│     • Thread N Crashed:                                     │
│     • Stack frames                                          │
│                                                             │
│  4. All Threads                                             │
│     • Thread 0, 1, 2... stacks                             │
│                                                             │
│  5. Binary Images                                           │
│     • Loaded libraries with addresses                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Типы крашей

```
┌─────────────────────────────────────────────────────────────┐
│ Exception Type         │ Причина                            │
├─────────────────────────────────────────────────────────────┤
│ EXC_BAD_ACCESS         │ Доступ к невалидной памяти         │
│ EXC_BAD_INSTRUCTION    │ Невалидная инструкция CPU          │
│ EXC_ARITHMETIC         │ Деление на ноль                    │
│ EXC_CRASH (SIGKILL)    │ Убит системой (watchdog, OOM)      │
│ EXC_CRASH (SIGABRT)    │ Программа сама вызвала abort()     │
└─────────────────────────────────────────────────────────────┘
```

### Symbolication

```
┌─────────────────────────────────────────────────────────────┐
│              ДО СИМВОЛИЗАЦИИ                                │
├─────────────────────────────────────────────────────────────┤
│ Thread 0 Crashed:                                           │
│ 0   MyApp    0x100012345  0x100000000 + 74565              │
│ 1   MyApp    0x100023456  0x100000000 + 144470             │
│ 2   UIKit    0x180123456  0x180000000 + 1193046            │
├─────────────────────────────────────────────────────────────┤
│              ПОСЛЕ СИМВОЛИЗАЦИИ                             │
├─────────────────────────────────────────────────────────────┤
│ Thread 0 Crashed:                                           │
│ 0   MyApp    ViewController.buttonTapped(_:) (line 45)     │
│ 1   MyApp    NetworkManager.fetchData() (line 123)         │
│ 2   UIKit    -[UIControl sendAction:to:forEvent:]          │
└─────────────────────────────────────────────────────────────┘
```

### dSYM файлы

```
┌─────────────────────────────────────────────────────────────┐
│                     dSYM WORKFLOW                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Build (Release)                                            │
│       │                                                     │
│       ├──→ MyApp.app (stripped binary)                     │
│       │                                                     │
│       └──→ MyApp.app.dSYM (debug symbols)                  │
│                 │                                           │
│                 │  UUID должен совпадать!                   │
│                 ▼                                           │
│            Symbolication                                    │
│                 │                                           │
│                 ▼                                           │
│         Readable Stack Trace                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

```bash
# Найти UUID бинарника
dwarfdump --uuid MyApp.app/MyApp

# Найти UUID dSYM
dwarfdump --uuid MyApp.app.dSYM

# Символизировать вручную
atos -arch arm64 -o MyApp.app.dSYM/Contents/Resources/DWARF/MyApp -l 0x100000000 0x100012345

# Символизировать весь crash log
symbolicatecrash crash.ips MyApp.app.dSYM > symbolicated.crash
```

### Crash Organizer в Xcode

```
Window → Organizer → Crashes

┌─────────────────────────────────────────────────────────────┐
│                    CRASH ORGANIZER                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Top Crash: ViewController.swift:45                      │
│     Occurrences: 1,234                                      │
│     Affected Users: 567                                     │
│                                                             │
│  📊 Second Crash: NetworkManager.swift:123                  │
│     Occurrences: 456                                        │
│     Affected Users: 234                                     │
│                                                             │
│  [Open in Project] → Переход прямо к строке кода           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Third-party инструменты

```
┌─────────────────────────────────────────────────────────────┐
│                CRASH REPORTING SERVICES                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Firebase Crashlytics                                       │
│  ├── Бесплатно                                              │
│  ├── Real-time alerts                                       │
│  ├── Автосимволизация                                       │
│  └── Breadcrumbs                                            │
│                                                             │
│  Sentry                                                     │
│  ├── Performance monitoring                                 │
│  ├── Release health                                         │
│  └── Issue grouping                                         │
│                                                             │
│  Bugsnag                                                    │
│  ├── Stability score                                        │
│  └── User feedback                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Console и Logging

### print vs debugPrint

```swift
struct User {
    let name: String
    let age: Int
}

let user = User(name: "Alice", age: 25)

print(user)
// User(name: "Alice", age: 25)

debugPrint(user)
// MyApp.User(name: "Alice", age: 25)

// debugPrint показывает полное имя типа с модулем
// Полезно для disambiguation
```

### os_log и Logger (iOS 14+)

```swift
import os

// Старый API (iOS 10+)
let log = OSLog(subsystem: "com.myapp", category: "networking")
os_log("Request started: %{public}@", log: log, type: .info, url.absoluteString)

// Новый API (iOS 14+)
let logger = Logger(subsystem: "com.myapp", category: "networking")

// Уровни логирования
logger.trace("Verbose debug info")           // Не сохраняется
logger.debug("Debug info")                    // Не сохраняется в Release
logger.info("Informational message")          // Сохраняется
logger.notice("Important but not error")      // Сохраняется
logger.warning("Warning")                     // Сохраняется
logger.error("Error occurred")                // Сохраняется
logger.fault("Critical fault")                // Сохраняется + stack trace
logger.critical("Critical system error")      // Сохраняется + stack trace

// Privacy
logger.info("User: \(username, privacy: .private)")  // Скрыто в логах
logger.info("Count: \(count, privacy: .public)")     // Видно в логах
```

### Console.app

```
┌─────────────────────────────────────────────────────────────┐
│                     CONSOLE.APP                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Devices (sidebar):                                         │
│  └── iPhone (физический или симулятор)                      │
│                                                             │
│  Фильтры:                                                   │
│  • Process: MyApp                                           │
│  • Subsystem: com.myapp                                     │
│  • Category: networking                                     │
│  • Message: contains "error"                                │
│                                                             │
│  Важно: Include Info/Debug Messages для полных логов        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Unified Logging System

```
┌─────────────────────────────────────────────────────────────┐
│             UNIFIED LOGGING ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  App Code                                                   │
│      │                                                      │
│      ▼                                                      │
│  os_log() / Logger                                          │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────────┐                               │
│  │   Unified Log System    │                               │
│  │  ┌───────────────────┐  │                               │
│  │  │ In-Memory Buffer  │  │ ← Быстрый ring buffer         │
│  │  └─────────┬─────────┘  │                               │
│  │            ▼            │                               │
│  │  ┌───────────────────┐  │                               │
│  │  │ Persistent Store  │  │ ← .info и выше               │
│  │  └───────────────────┘  │                               │
│  └─────────────────────────┘                               │
│            │                                                │
│            ▼                                                │
│    Console.app / log CLI                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

```bash
# CLI для чтения логов
log stream --predicate 'subsystem == "com.myapp"'

# С фильтром по уровню
log stream --predicate 'subsystem == "com.myapp"' --level debug

# Экспорт в файл
log collect --device --output logs.logarchive
```

---

## Распространённые ошибки

### 1. Избыточные print-statements вместо breakpoints

```swift
// ❌ ПЛОХО: Загрязняет код, нужно перекомпилировать
func processData(_ data: Data) {
    print("DEBUG: processData called")
    print("DEBUG: data size = \(data.count)")
    let result = parse(data)
    print("DEBUG: result = \(result)")
    print("DEBUG: processing complete")
}

// ✅ ХОРОШО: Breakpoint с log action и auto-continue
// Нет изменений в коде
// В Xcode: breakpoint → Edit → Action: Log Message
// "@data.count@ bytes received" + Auto-continue
```

### 2. Игнорирование conditional breakpoints в циклах

```swift
// ❌ ПЛОХО: Breakpoint срабатывает 10000 раз
for user in users {  // ← Обычный breakpoint
    processUser(user)
}
// Приходится жать Continue тысячи раз

// ✅ ХОРОШО: Conditional breakpoint
// Condition: user.id == 42
// или
// Condition: $hitCount == 1000
// или
// Ignore: 999 (остановиться на 1000-й итерации)
```

### 3. Не использование Exception breakpoint

```swift
// ❌ ПЛОХО: Краш где-то в глубине без контекста
// Thread 1: EXC_BAD_ACCESS
// (уже поздно, стек размотан)

// ✅ ХОРОШО: Exception breakpoint ловит момент throw
// Breakpoints Navigator → + → Exception Breakpoint
// Exception: All, Break: On Throw
// Теперь видим точное место исключения ДО размотки стека
```

### 4. Забывают про Memory Graph при утечках

```swift
// ❌ ПЛОХО: Пытаются найти retain cycle print-ами
class ViewController {
    var closure: (() -> Void)?

    func setup() {
        print("setup called")
        closure = {
            print("closure called")
            self.doSomething()  // Retain cycle!
        }
        print("setup complete")
    }

    deinit {
        print("deinit called")  // Никогда не вызовется
    }
}

// ✅ ХОРОШО: Memory Graph Debugger
// Debug → View Debugging → Capture Memory Graph
// Увидим retain cycle: ViewController → closure → ViewController
```

### 5. Не символизируют crash logs

```
// ❌ ПЛОХО: Пытаются понять несимволизированный crash
// Thread 0:
// 0   MyApp  0x100012345  0x100000000 + 74565
// "Что??? Какой-то адрес..."

// ✅ ХОРОШО: Символизация
// 1. Найти dSYM для этой версии
// 2. atos или symbolicatecrash
// 3. Получить читаемый стек:
//    ViewController.buttonTapped(_:) at ViewController.swift:45
```

### 6. Использование `po` для всего подряд

```lldb
# ❌ ПЛОХО: po медленный и имеет побочные эффекты
(lldb) po array.count  # Компилирует, вызывает код
(lldb) po dict.keys    # Может изменить состояние

# ✅ ХОРОШО: Использовать правильную команду
(lldb) v array          # Быстро, без побочек
(lldb) p array.count    # Когда нужно вычисление
(lldb) po customObject  # Только для debugDescription
```

---

## Ментальные модели

### 1. Модель "Временнóй путешественник"

```
┌─────────────────────────────────────────────────────────────┐
│              ВРЕМЕННОЙ ПУТЕШЕСТВЕННИК                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Debugger = машина времени для кода                         │
│                                                             │
│  Прошлое          Настоящее        Будущее                  │
│  (backtrace)      (breakpoint)     (step over/into)         │
│                                                             │
│  ←───────────────── ● ─────────────────→                    │
│                     │                                       │
│  frame select 5     │   step / next / continue              │
│  (куда пришли)      │   (куда идём)                         │
│                                                             │
│  Можно:                                                     │
│  • Смотреть что было (backtrace, frame select)             │
│  • Изменять настоящее (expression)                         │
│  • Влиять на будущее (изменить переменные и continue)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Модель "Слои луковицы"

```
┌─────────────────────────────────────────────────────────────┐
│                   СЛОИ ОТЛАДКИ                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│        ┌─────────────────────────────────┐                 │
│        │      1. Logging (print)         │  Самый внешний  │
│        │  ┌─────────────────────────┐    │  Грубый обзор   │
│        │  │   2. Breakpoints        │    │                 │
│        │  │  ┌───────────────────┐  │    │                 │
│        │  │  │ 3. LLDB commands  │  │    │  Детальный      │
│        │  │  │  ┌─────────────┐  │  │    │  контроль       │
│        │  │  │  │4. Registers │  │  │    │                 │
│        │  │  │  │   Memory    │  │  │    │  Самый глубокий │
│        │  │  │  └─────────────┘  │  │    │  Уровень CPU    │
│        │  │  └───────────────────┘  │    │                 │
│        │  └─────────────────────────┘    │                 │
│        └─────────────────────────────────┘                 │
│                                                             │
│  Начинай с внешнего слоя, углубляйся по необходимости      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Модель "Детектив"

```
Этапы расследования:

1. МЕСТО ПРЕСТУПЛЕНИЯ (crash location)
   → Где именно упало? (crash log, exception breakpoint)

2. СВИДЕТЕЛИ (stack trace)
   → Кто вызывал? Откуда пришли?

3. УЛИКИ (variables)
   → Какое состояние было в момент падения?

4. МОТИВ (root cause)
   → Почему это состояние возникло?

5. РЕКОНСТРУКЦИЯ (reproduce)
   → Можем ли воспроизвести?

6. ПРЕДОТВРАЩЕНИЕ (fix)
   → Как не допустить повторения?
```

### 4. Модель "Научный метод"

```
┌─────────────────────────────────────────────────────────────┐
│               НАУЧНЫЙ МЕТОД ОТЛАДКИ                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. НАБЛЮДЕНИЕ                                              │
│     └─→ Что именно происходит? (симптомы)                  │
│                                                             │
│  2. ГИПОТЕЗА                                                │
│     └─→ Почему это может происходить? (теория)             │
│                                                             │
│  3. ЭКСПЕРИМЕНТ                                             │
│     └─→ Как проверить гипотезу? (breakpoint, watchpoint)   │
│                                                             │
│  4. АНАЛИЗ                                                  │
│     └─→ Подтвердилась гипотеза? (изучение данных)          │
│                                                             │
│  5. ВЫВОД                                                   │
│     └─→ Новая гипотеза или решение                         │
│                                                             │
│  ⚠️ Меняй только ОДНУ вещь за раз!                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5. Модель "Минимальный воспроизводимый пример"

```
Когда баг непонятен:

Исходный код (сложный)
        │
        ▼
Убираем код пока баг есть
        │
        ▼
Минимальный код где баг воспроизводится
        │
        ▼
Понимание причины становится очевидным

Правило: Если не можешь воспроизвести — не можешь починить
```

## Связь с другими темами

**[[ios-performance-profiling]]** — профилирование производительности является естественным продолжением отладки. Если debugging помогает найти и исправить конкретный баг, то Instruments и профайлинг позволяют обнаружить системные проблемы: утечки памяти, bottleneck-и CPU и dropped frames. Владение обоими навыками превращает разработчика в специалиста, способного не только чинить баги, но и предотвращать их. Рекомендуется сначала освоить LLDB и breakpoints из текущей статьи, а затем перейти к Instruments.

**[[android-performance-profiling]]** — Android использует принципиально иные инструменты отладки (Android Studio Debugger, Logcat, Profiler), но концептуально процесс аналогичен: breakpoints, стек вызовов, memory analysis. Сравнение двух платформ углубляет понимание того, какие подходы к debugging универсальны (научный метод, watchpoints), а какие специфичны для платформы (LLDB vs ADB, dSYM vs ProGuard mapping). Полезно для кросс-платформенных разработчиков.

**[[jvm-production-debugging]]** — JVM-отладка предоставляет другой набор инструментов (JDB, remote debugging, heap dumps), но разделяет общие принципы с iOS debugging: анализ crash logs, профилирование памяти, поиск race conditions. Понимание JVM-подходов обогащает арсенал отладочных стратегий и помогает работать с серверной частью мобильных приложений. Рекомендуется к изучению после освоения iOS debugging для расширения кругозора.

---

## Источники и дальнейшее чтение

### Теоретические основы
- Kernighan B., Plauger P. (1974). *The Elements of Programming Style.* — принципы написания отлаживаемого кода, знаменитая цитата о debugging
- Zeller A. (2009). *Why Programs Fail: A Guide to Systematic Debugging.* — научный подход к отладке: delta debugging, cause-effect chains
- Seward J., Nethercote N. (2005). *Using Valgrind to Detect Undefined Value Errors with Bit-Precision.* — теория runtime instrumentation для sanitizers

### Практические руководства
- Wenderlich Team (2023). *Advanced Apple Debugging & Reverse Engineering.* — LLDB, обратная инженерия, продвинутые техники отладки
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — Xcode debugger, console, crash analysis
- Eidhof C. et al. (2019). *Advanced Swift.* — unsafe-операции, работа с памятью, причины EXC_BAD_ACCESS

### Официальная документация
- [LLDB Documentation](https://lldb.llvm.org/use/tutorial.html) — официальный tutorial
- [Apple Debugging Documentation](https://developer.apple.com/documentation/xcode/debugging)
- [Unified Logging](https://developer.apple.com/documentation/os/logging)

### WWDC Sessions
- **WWDC 2018** — [Advanced Debugging with Xcode and LLDB](https://developer.apple.com/videos/play/wwdc2018/412/)
- **WWDC 2019** — [LLDB: Beyond "po"](https://developer.apple.com/videos/play/wwdc2019/429/)
- **WWDC 2020** — [Explore logging in Swift](https://developer.apple.com/videos/play/wwdc2020/10168/)
- **WWDC 2021** — [Understand and eliminate hangs from your app](https://developer.apple.com/videos/play/wwdc2021/10258/)
- **WWDC 2022** — [Debug Swift debugging with LLDB](https://developer.apple.com/videos/play/wwdc2022/110370/)

---

## Проверь себя

> [!question]- Почему LLDB `po` команда иногда показывает неправильные значения в Release-сборке, и какая альтернатива?
> В Release-сборке оптимизатор может удалить или переместить переменные, и LLDB не может найти их значения. po (print object) вызывает description, что может не работать без debug info. Альтернативы: `v` (frame variable) -- быстрее и надежнее, не выполняет код. `p` (expression) -- вычисляет выражение. Для Release: добавить -Xfrontend -serialize-debugging-options.

> [!question]- Как Xcode View Debugging помогает найти проблемы с Auto Layout, и какие типичные проблемы оно выявляет?
> Debug -> View Debugging -> Capture View Hierarchy: показывает 3D-иерархию view. Выявляет: ambiguous constraints (фиолетовые warnings), overlapping views, hidden views, неправильные z-order, clipped content, transparent backgrounds. Также показывает constraint details для каждого view и позволяет навигировать к коду constraint.

> [!question]- Сценарий: приложение крэшится у пользователей, но вы не можете воспроизвести. Crash log показывает EXC_BAD_ACCESS. Как найти причину?
> 1) Symbolicate crash log (dSYM файлы). 2) Включить Address Sanitizer (ASan) -- находит use-after-free, buffer overflow. 3) Включить Zombie Objects -- NSZombie показывает обращения к деаллоцированным объектам. 4) Проверить Thread Sanitizer (TSan) для data races. 5) Проанализировать backtrace -- какой объект и метод вызвал crash. 6) Добавить breadcrumbs через os_log.

---

## Ключевые карточки

Какие основные команды LLDB?
?
po (print object, вызывает description), p (evaluate expression), v (frame variable, без кода), bt (backtrace), n (step over), s (step into), c (continue), breakpoint set, watchpoint set, thread list. expr для модификации переменных в runtime.

Что такое symbolication и зачем нужны dSYM файлы?
?
Symbolication -- преобразование memory addresses в crash log в имена функций, файлы и номера строк. dSYM (Debug Symbols) содержит маппинг. Без dSYM crash log нечитаем (только hex-адреса). Архивировать dSYM при каждом релизе. Xcode автоматически символицирует при наличии dSYM.

Какие Sanitizers доступны в Xcode?
?
Address Sanitizer (ASan): use-after-free, buffer overflow, stack overflow. Thread Sanitizer (TSan): data races, threading issues. Undefined Behavior Sanitizer (UBSan): integer overflow, null pointer dereference. Memory Graph: retain cycles, leaks. Включаются в Scheme -> Diagnostics.

Что такое conditional breakpoint и когда он полезен?
?
Breakpoint с условием: останавливается только когда условие истинно (index == 42, error != nil). Полезен для: отладки конкретной итерации цикла, ловли специфичного состояния, избежания ручного пропуска. Также: action breakpoints (po variable), symbolic breakpoints (-[UIView layoutSubviews]).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-performance-profiling]] | Профилирование для поиска performance-багов |
| Углубиться | [[ios-concurrency-mistakes]] | Типичные concurrency-баги и их отладка |
| Смежная тема | [[jvm-production-debugging]] | Отладка в JVM для кросс-платформенного контекста |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |

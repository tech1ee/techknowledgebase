---
title: "Внутреннее устройство Jetpack Compose"
created: 2025-12-25
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [gap-buffer, tree-diffing, memoization, snapshot-isolation, functional-programming, immutability]
tags:
  - topic/android
  - topic/compose
  - type/deep-dive
  - level/expert
related:
  - "[[android-compose]]"
  - "[[android-view-rendering-pipeline]]"
  - "[[android-performance-profiling]]"
  - "[[android-state-management]]"
prerequisites:
  - "[[android-compose]]"
  - "[[android-state-management]]"
  - "[[android-view-rendering-pipeline]]"
---

# Jetpack Compose Internals

---

## Зачем это нужно (Проблема → Решение)

> **Проблема:** Compose выглядит как "магия" — функции вызываются, UI появляется, state меняется, всё обновляется. Но без понимания internals:
> - Непонятно почему composable перерисовывается "просто так"
> - Непонятно почему List вызывает проблемы производительности
> - Непонятно когда использовать `remember` vs `derivedStateOf`
> - Непонятно почему анимации тормозят
>
> **Решение:** Понимание трёх вещей объясняет 90% поведения Compose:
> 1. **Compiler Plugin** — что добавляется к вашим функциям
> 2. **Slot Table** — как Compose хранит состояние между recompositions
> 3. **Three Phases** — composition → layout → draw и как skip каждую фазу

**Compose — это не декларативный фреймворк. Это compiler trick + умное кэширование.**

Понимание internals критично для:
- Диагностики performance issues без гадания
- Осознанного выбора между remember/derivedStateOf/rememberUpdatedState
- Понимания почему @Stable/@Immutable влияют на skipping
- Написания production-ready кода, а не StackOverflow-копипасты

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Compose basics | Знать что такое @Composable, State, remember | [[android-compose]] |
| Kotlin lambdas | Compose активно использует lambdas и inline | [[kotlin-functions]] |
| **CS: Memoization** | remember — это memoization | [[cs-functional-programming]] |
| **CS: Gap Buffer** | Slot Table — это Gap Buffer | [[cs-data-structures]] |
| **CS: Tree diffing** | Recomposition — это diffing UI дерева | [[cs-algorithms]] |
| **CS: Snapshot isolation** | Изоляция изменений state между потоками | [[cs-concurrency]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Composition** | Процесс выполнения @Composable функций и построения UI дерева | Шеф составляет меню — ЧТО готовить |
| **Recomposition** | Повторное выполнение composable при изменении state | Обновление меню — только изменённые блюда |
| **Slot Table** | Gap Buffer для хранения состояния композиции | Записная книжка с закладкой — быстрый доступ к текущей позиции |
| **Composer** | Runtime объект, управляющий composition | Дирижёр оркестра — координирует всех |
| **Skipping** | Пропуск recomposition при неизменных параметрах | "Блюдо не изменилось — не перезаказываем" |
| **Stability** | Свойство типа, позволяющее Compose определить изменения | "Этот ингредиент гарантированно такой же" |
| **Snapshot** | Механизм изоляции и отслеживания изменений state | Git snapshot — изолированная версия данных |
| **LayoutNode** | Внутренний узел UI дерева Compose | Ячейка таблицы в Excel |
| **RestartScope** | Область кода, которая может быть перезапущена | "Точка сохранения" в игре |
| **Applier** | Применяет изменения к реальному UI | Официант несёт блюдо от кухни к столу |
| **Changed flags** | Битовая маска изменённых параметров | Checklist — что изменилось |
| **Movable content** | Контент, который можно переместить без пересоздания | Перетаскивание виджета на рабочем столе |

---

## ПОЧЕМУ: Зачем понимать Compose Internals

### Проблемы без понимания

```kotlin
// Почему composable recompose каждый раз?
// Почему List как параметр вызывает проблемы?
// Почему UI тормозит при скролле?
// Когда использовать derivedStateOf vs remember(key)?
```

### Когда знания критичны

| Сценарий | Почему важно |
|----------|--------------|
| Оптимизация производительности | Понимание skipping, stability |
| Debugging recomposition | Знание фаз рендеринга |
| Сложные state flows | Snapshot system, derivedStateOf |
| Multi-module архитектура | Stability across modules |
| Анимации | Phase-based оптимизация |

### Аналогия: Кухня ресторана

```
Composition = Шеф составляет меню (ЧТО готовить)
Layout = Су-шеф распределяет по станциям (ГДЕ готовить)
Drawing = Повара готовят блюда (КАК готовить)

Recomposition = Изменился заказ → шеф обновляет ТОЛЬКО изменённую часть меню
Skipping = Блюдо не изменилось → не перезаказываем ингредиенты
```

---

## Почему Compose использует именно такую архитектуру?

### Проблема 1: Декларативный UI требует "перерисовки" при каждом изменении

**В императивном View:**
```kotlin
// Изменился один текст → меняем один TextView
textView.text = newValue
```

**В наивном декларативном UI:**
```kotlin
// Изменился один текст → пересоздаём ВСЁ дерево
fun render(state: State) = buildTree {
    Column {
        Text(state.title)      // Пересоздаётся
        Text(state.subtitle)   // Пересоздаётся (хотя не изменился!)
        Button(...)            // Пересоздаётся
    }
}
```

**Решение Compose — Positional Memoization:**
- Compose запоминает результаты по позиции в коде
- При recomposition сравнивает параметры
- Если параметры не изменились → skip, использовать закэшированное

```kotlin
@Composable
fun MyScreen(state: State) {
    Column {
        Text(state.title)      // Params changed → recompose
        Text(state.subtitle)   // Params same → SKIP
        Button(...)            // Params same → SKIP
    }
}
```

### Проблема 2: Функции не имеют состояния

**Обычная функция:**
```kotlin
fun counter(): Int {
    var count = 0    // Создаётся заново при каждом вызове!
    count++
    return count     // Всегда 1
}
```

**Решение — Slot Table:**
- Compose сохраняет состояние "снаружи" функции
- При повторном вызове достаёт из Slot Table
- Функция "stateless", но Compose добавляет state

```kotlin
@Composable
fun Counter() {
    // remember сохраняет в Slot Table
    var count by remember { mutableStateOf(0) }
    count++  // Теперь работает!
}
```

### Проблема 3: Как узнать ЧТО изменилось?

**Наивный подход — always recompose:**
```kotlin
// Вызывать всё дерево при любом изменении = O(n) каждый frame
```

**Решение — Snapshot System:**
1. State обёрнут в `mutableStateOf`
2. При чтении state регистрируется "кто читал"
3. При изменении state уведомляются только читатели
4. Recomposition только для затронутых composables

```kotlin
@Composable
fun Parent() {
    var name by remember { mutableStateOf("John") }  // State
    var age by remember { mutableStateOf(25) }       // State

    NameDisplay(name)   // Читает name → подписан на name
    AgeDisplay(age)     // Читает age → подписан на age
}

// Если изменится name:
// - NameDisplay recomposes
// - AgeDisplay НЕ recomposes (не читает name)
```

### Проблема 4: Определение равенства параметров

**Проблема:**
```kotlin
@Composable
fun UserCard(user: User) { }

// При recomposition:
// user === previousUser?  ← Как проверить?
```

**Решение — Stability система:**

| Стабильность | Как определяется | Skipping |
|--------------|------------------|----------|
| **Primitive** | Int, String, etc. | `==` сравнение |
| **@Stable** | Компилятор доверяет equals() | `equals()` сравнение |
| **@Immutable** | Никогда не меняется | `equals()` сравнение |
| **Unstable** | List, var fields | Без Strong Skipping: ВСЕГДА recompose |

```kotlin
// ✅ Stable — data class с val fields
data class User(val name: String)

// ❌ Unstable — List (mutable interface)
data class Users(val list: List<User>)

// ✅ Stable через аннотацию
@Immutable
data class Users(val list: List<User>)
```

### Проблема 5: Gap Buffer vs Tree для хранения состояния

**Почему не Tree:**
```
Tree traversal: O(log n) для доступа к узлу
UI рендеринг: последовательный обход сверху вниз
Частый паттерн: вставка/удаление в текущей позиции
```

**Почему Gap Buffer:**
```
┌───────────────────────────────────────────────────────┐
│         GAP BUFFER — идеально для последовательного   │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Чтение текущей позиции: O(1)                         │
│  Вставка в текущей позиции: O(1)                      │
│  Последовательный обход: O(n)                         │
│                                                       │
│  Composition идёт сверху вниз → идеальный match!      │
│                                                       │
│  Text editors используют Gap Buffer:                  │
│  - Emacs, VS Code cursor movement                     │
│  - Compose Slot Table                                 │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Архитектурные trade-offs

```
┌─────────────────────────────────────────────────────────────────────┐
│                  COMPOSE DESIGN DECISIONS                            │
├─────────────────────────────────────────────────────────────────────┤
│ Выбор                  │ Плюсы               │ Минусы              │
├────────────────────────┼─────────────────────┼─────────────────────┤
│ Compiler plugin        │ Zero runtime cost   │ Complex tooling     │
│                        │ для трансформаций   │ Magic для новичков  │
├────────────────────────┼─────────────────────┼─────────────────────┤
│ Gap Buffer (Slot Table)│ O(1) sequential ops │ Не random access    │
│                        │ Memory efficient    │                     │
├────────────────────────┼─────────────────────┼─────────────────────┤
│ Snapshot isolation     │ Thread-safe state   │ Overhead на state   │
│                        │ Fine-grained updates│                     │
├────────────────────────┼─────────────────────┼─────────────────────┤
│ Stability inference    │ Auto skipping       │ False positives     │
│                        │                     │ (unstable when ok)  │
├────────────────────────┼─────────────────────┼─────────────────────┤
│ Positional memoization │ No explicit keys    │ Conditional problems│
│                        │                     │ (if/else issues)    │
└────────────────────────┴─────────────────────┴─────────────────────┘
```

---

## ЧТО: Архитектура Compose

### Compiler Plugin Transformation

```kotlin
// ВАШ КОД
@Composable
fun Greeting(name: String) {
    Text("Hello, $name")
}

// ПОСЛЕ КОМПИЛЯЦИИ (упрощённо)
fun Greeting(
    name: String,
    $composer: Composer,      // Связь с Runtime
    $changed: Int             // Битовая маска изменений
) {
    $composer.startRestartGroup(0x12345)  // Уникальный ключ

    // Проверка: можно ли пропустить?
    if ($changed and 0b0001 == 0 && $composer.skipping) {
        $composer.skipToGroupEnd()
    } else {
        // Выполняем тело функции
        Text("Hello, $name", $composer, 0)
    }

    // Регистрируем scope для recomposition
    $composer.endRestartGroup()?.updateScope { nc, _ ->
        Greeting(name, nc, $changed or 0b0001)
    }
}
```

**Что добавляет компилятор:**

| Элемент | Назначение |
|---------|------------|
| `$composer` | Доступ к Slot Table, управление groups |
| `$changed` | 3 бита на параметр: stable + 2 бита состояния |
| `startRestartGroup` | Начало restartable scope |
| Skipping logic | Проверка параметров для skip |
| `updateScope` | Lambda для повторного вызова при recomposition |

### Slot Table (Gap Buffer)

```
Slot Table хранит ВСЁ состояние composition:

┌──────┬──────┬──────┬─────────────┬──────┬──────┬──────┐
│ G1   │ S1   │ R1   │  ← GAP →    │ G2   │ S2   │ R2   │
└──────┴──────┴──────┴─────────────┴──────┴──────┴──────┘
   ↑                                   ↑
   Текущая позиция                  Следующие данные

G = Group (identity composable)
S = State (remembered values)
R = References (CompositionLocals)
```

**Почему Gap Buffer:**
- Последовательный обход: O(1) read
- Вставка в текущей позиции: O(1)
- Gap перемещается только при структурных изменениях

```kotlin
// remember использует Slot Table
val count = remember { mutableStateOf(0) }
// → Сохраняется в slot при первой composition
// → Читается из slot при recomposition
```

### Три фазы рендеринга

```
┌─────────────────────────────────────────────────────────────┐
│                     COMPOSITION                              │
│  "ЧТО показать"                                              │
│                                                              │
│  • Выполняются @Composable функции                           │
│  • Строится UI дерево (LayoutNodes)                          │
│  • Вызываются remember, state reads                          │
│  • Определяется структура UI                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        LAYOUT                                │
│  "ГДЕ разместить"                                            │
│                                                              │
│  Measurement: parent → children → sizes                      │
│  Placement: позиционирование в 2D координатах                │
│                                                              │
│  Single pass O(n) — каждый node 1 раз!                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       DRAWING                                │
│  "КАК нарисовать"                                            │
│                                                              │
│  • Top-to-bottom traversal                                   │
│  • Canvas draw commands                                      │
│  • Рисование в буфер                                         │
└─────────────────────────────────────────────────────────────┘
```

### Phase Skipping — ключ к производительности

```kotlin
// ❌ State read в COMPOSITION → полная recomposition
@Composable
fun BadExample(scrollState: ScrollState) {
    val offset = scrollState.value  // Read в composition!
    Box(Modifier.offset(y = offset.dp))
}

// ✅ State read в LAYOUT → только layout + draw
@Composable
fun GoodExample(scrollState: ScrollState) {
    Box(
        Modifier.offset {
            IntOffset(0, scrollState.value)  // Read в layout phase
        }
    )
}

// ✅✅ State read в DRAWING → только draw
@Composable
fun BestExample(color: State<Color>) {
    Box(
        Modifier.drawBehind {
            drawRect(color.value)  // Read в draw phase
        }
    )
}
```

---

## КАК: Практические паттерны

### 1. remember — кэширование между recompositions

```kotlin
@Composable
fun ExpensiveCalculation(items: List<Item>) {
    // ❌ Пересчитывается каждую recomposition
    val sorted = items.sortedBy { it.name }

    // ✅ Пересчитывается только при изменении items
    val sorted = remember(items) {
        items.sortedBy { it.name }
    }

    // ✅ Объект создаётся один раз
    val formatter = remember { DateFormatter() }
}
```

### 2. derivedStateOf — distinctUntilChanged

```kotlin
@Composable
fun ListWithFab(items: List<Item>) {
    val listState = rememberLazyListState()

    // ❌ showButton меняется при КАЖДОМ scroll event
    val showButton = listState.firstVisibleItemIndex > 0

    // ✅ showButton меняется только при переходе 0↔1+
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }

    // Recomposition только когда showButton РЕАЛЬНО меняется
    AnimatedVisibility(visible = showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}
```

**Когда использовать:**
| Сценарий | Решение |
|----------|---------|
| Input меняется часто, output редко | `derivedStateOf` |
| Нужен новый расчёт при смене ключа | `remember(key)` |
| Фильтрация большого списка | `derivedStateOf` |
| Scroll position → boolean | `derivedStateOf` |

### 3. Stability и Skipping

```kotlin
// ✅ STABLE — все поля immutable
data class User(
    val id: String,
    val name: String
)

// ❌ UNSTABLE — var field
data class MutableUser(
    val id: String,
    var name: String  // var = unstable
)

// ❌ UNSTABLE — List не гарантированно immutable
data class UserList(
    val users: List<User>  // List = unstable
)

// ✅ STABLE через аннотацию
@Immutable
data class UserList(
    val users: List<User>  // Теперь stable
)

// ✅ STABLE через kotlinx.collections.immutable
data class UserList(
    val users: ImmutableList<User>  // ImmutableList = stable
)
```

### 4. Strong Skipping Mode (Kotlin 2.0.20+)

```kotlin
// Без Strong Skipping:
// Unstable параметр → ВСЕГДА recompose

// С Strong Skipping:
// Проверяется === (reference equality)

@Composable
fun Parent() {
    // Один и тот же instance → Child skipped
    val list = remember { mutableListOf(1, 2, 3) }

    Child(list)  // Skips если list === previousList
}

@Composable
fun Child(items: List<Int>) {
    // Даже List теперь может skip!
    items.forEach { Text("$it") }
}
```

**Включение Strong Skipping:**
```kotlin
// build.gradle.kts
composeCompiler {
    enableStrongSkipping = true  // Default в Kotlin 2.0.20+
}
```

### 5. Side Effects

```kotlin
@Composable
fun UserProfile(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }

    // LaunchedEffect — coroutine привязанный к composition lifecycle
    LaunchedEffect(userId) {  // Перезапускается при смене userId
        user = repository.getUser(userId)
    }

    // DisposableEffect — setup/cleanup без coroutine
    DisposableEffect(Unit) {
        val listener = analytics.addScreenListener("profile")
        onDispose {
            listener.remove()  // Cleanup при выходе из composition
        }
    }

    // SideEffect — после КАЖДОЙ успешной recomposition
    SideEffect {
        analytics.logScreenView("profile")
    }

    user?.let { ProfileContent(it) }
}
```

**Выбор Side Effect:**

| Effect | Когда | Suspend? | Cleanup? |
|--------|-------|----------|----------|
| `LaunchedEffect(key)` | Async операции | ✅ | Auto cancel |
| `DisposableEffect(key)` | Listeners, resources | ❌ | `onDispose` |
| `SideEffect` | Sync после recomposition | ❌ | ❌ |
| `rememberUpdatedState` | Capture latest value | - | - |

### 6. rememberUpdatedState — избежать restart effect

```kotlin
@Composable
fun Timer(onTick: () -> Unit) {
    // ❌ LaunchedEffect перезапустится при каждом новом onTick
    LaunchedEffect(onTick) {
        while (true) {
            delay(1000)
            onTick()
        }
    }

    // ✅ Effect НЕ перезапускается, но использует актуальный callback
    val currentOnTick by rememberUpdatedState(onTick)
    LaunchedEffect(Unit) {
        while (true) {
            delay(1000)
            currentOnTick()  // Всегда актуальная версия
        }
    }
}
```

### 7. Lambda-based Modifiers для performance

```kotlin
@Composable
fun AnimatedBox(progress: Float) {
    // ❌ Recomposition при каждом изменении progress
    Box(
        Modifier
            .offset(x = (progress * 100).dp)
            .alpha(progress)
    )

    // ✅ Только layout/draw, без recomposition
    Box(
        Modifier
            .offset { IntOffset((progress * 100).roundToInt(), 0) }
            .graphicsLayer { alpha = progress }
    )
}
```

### 8. keys в LazyColumn

```kotlin
@Composable
fun ItemList(items: List<Item>) {
    LazyColumn {
        // ❌ Без key — Compose не знает identity
        items(items) { item ->
            ItemCard(item)  // Может перерисовать всё при reorder
        }

        // ✅ С key — правильное отслеживание identity
        items(
            items = items,
            key = { it.id }  // Stable identity
        ) { item ->
            ItemCard(item)  // Анимации работают, минимум recomposition
        }
    }
}
```

### 9. Modifier Chain — порядок важен

```kotlin
// Padding СНАРУЖИ background
Box(
    Modifier
        .padding(16.dp)      // 1. Сначала padding
        .background(Red)     // 2. Потом background
)
// Результат: красный прямоугольник с отступом от краёв

// Padding ВНУТРИ background
Box(
    Modifier
        .background(Red)     // 1. Сначала background
        .padding(16.dp)      // 2. Потом padding
)
// Результат: красный прямоугольник во весь размер, контент с отступом
```

```kotlin
// Clickable СНАРУЖИ clip
Box(
    Modifier
        .clip(CircleShape)
        .clickable { }  // Клик только в круге
)

// Clickable ВНУТРИ clip
Box(
    Modifier
        .clickable { }
        .clip(CircleShape)  // Клик в прямоугольнике, отображение в круге
)
```

### 10. CompositionLocal — implicit параметры

```kotlin
// Определение
val LocalAppTheme = compositionLocalOf<AppTheme> {
    error("No theme provided")
}

// Провайдер
@Composable
fun App() {
    val theme = remember { AppTheme.Dark }

    CompositionLocalProvider(LocalAppTheme provides theme) {
        // Все дети получают доступ к theme
        MainScreen()
    }
}

// Использование (на любой глубине)
@Composable
fun DeepNestedComponent() {
    val theme = LocalAppTheme.current
    Box(Modifier.background(theme.backgroundColor))
}
```

---

## КОГДА НЕ оптимизировать

### Преждевременная оптимизация

```kotlin
// ❌ Не делайте это "на всякий случай"
@Immutable
data class SimpleData(val name: String)  // Уже stable!

// ❌ Не используйте derivedStateOf для простых случаев
val count by remember { derivedStateOf { items.size } }
// ✅ Просто
val count = items.size
```

### Когда stability не важна

| Сценарий | Нужна ли оптимизация |
|----------|---------------------|
| Редкие recompositions | Нет |
| Simple screens | Нет |
| Профилировщик не показывает проблем | Нет |
| Composable не в hot path (scroll) | Редко |

### Layout Inspector — проверяй перед оптимизацией

```
Android Studio → Tools → Layout Inspector → Compose tab

Смотри:
- Recomposition count
- Skipped count
- Красные индикаторы = частые recomposition
```

---

## Типичные ошибки

### 1. Забыть remember

```kotlin
// ❌ Новый DateFormatter каждую recomposition
@Composable
fun DateDisplay(timestamp: Long) {
    val formatter = SimpleDateFormat("dd.MM.yyyy")  // NEW каждый раз!
    Text(formatter.format(Date(timestamp)))
}

// ✅ Один formatter на весь lifecycle
@Composable
fun DateDisplay(timestamp: Long) {
    val formatter = remember { SimpleDateFormat("dd.MM.yyyy") }
    Text(formatter.format(Date(timestamp)))
}
```

### 2. List/Map как параметр

```kotlin
// ❌ List unstable → всегда recompose
@Composable
fun UserList(users: List<User>) { }

// ✅ Решение 1: @Immutable wrapper
@Immutable
data class UserListWrapper(val users: List<User>)

// ✅ Решение 2: ImmutableList
@Composable
fun UserList(users: ImmutableList<User>) { }

// ✅ Решение 3: Strong Skipping (если включён)
// List skip если === previous
```

### 3. Backward writes

```kotlin
// ❌ Запись state после чтения = infinite loop
@Composable
fun BadCounter() {
    var count by remember { mutableStateOf(0) }

    Text("Count: $count")  // Read

    count++  // Write ПОСЛЕ read = backward write!
}

// ✅ Правильно — write через event
@Composable
fun GoodCounter() {
    var count by remember { mutableStateOf(0) }

    Text("Count: $count")

    Button(onClick = { count++ }) {  // Write в callback
        Text("Increment")
    }
}
```

### 4. ViewModel в composable

```kotlin
// ❌ Новый ViewModel каждую recomposition
@Composable
fun Screen() {
    val viewModel = UserViewModel()  // NEW каждый раз!
}

// ✅ Через viewModel()
@Composable
fun Screen(viewModel: UserViewModel = viewModel()) {
    // Правильный lifecycle
}
```

### 5. State read в composition для scroll

```kotlin
// ❌ Recomposition КАЖДЫЙ frame при скролле
@Composable
fun ParallaxImage(scrollState: ScrollState) {
    val offset = scrollState.value / 2  // Read в composition
    Image(
        modifier = Modifier.offset(y = offset.dp)
    )
}

// ✅ Read в layout phase
@Composable
fun ParallaxImage(scrollState: ScrollState) {
    Image(
        modifier = Modifier.offset {
            IntOffset(0, scrollState.value / 2)  // Layout phase
        }
    )
}
```

---

## Инструменты отладки

### Layout Inspector (Compose)

```
Tools → Layout Inspector → Выбрать процесс

Compose tab:
- Recomposition count (сколько раз)
- Skip count (сколько пропущено)
- Красный = частые recompositions
- Зелёный = много skips
```

### Compose Compiler Reports

```kotlin
// build.gradle.kts
composeCompiler {
    reportsDestination = layout.buildDirectory.dir("compose_reports")
    metricsDestination = layout.buildDirectory.dir("compose_metrics")
}

// Запуск
./gradlew assembleRelease

// Анализ файлов:
// - *-classes.txt — stability каждого класса
// - *-composables.txt — restartable/skippable каждого composable
```

### Composition Tracing (API 30+)

```kotlin
// В коде
trace("MyComposable") {
    // Composable code
}

// Видно в Perfetto/Systrace
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Compose перерисовывает всё при любом изменении" | **Нет.** Compose использует positional memoization и skipping. Recomposition происходит только для composables, которые читают изменённый state. Если параметры stable и не изменились — composable пропускается. |
| "remember кэширует навсегда" | remember привязан к composition lifecycle. Если composable выходит из composition — cached value теряется. Для persist между sessions нужен rememberSaveable или persistent storage. |
| "@Composable — это React component" | **Нет.** @Composable функция выполняется каждый раз при recomposition. Это не объект, а функция. State хранится в Slot Table, не в instance. Более похоже на React Hooks, чем на class components. |
| "List всегда unstable" | С **Strong Skipping Mode** (Kotlin 2.0.20+) List может skip если === предыдущему instance. Без Strong Skipping — да, List считается unstable и вызывает recomposition. ImmutableList из kotlinx.collections.immutable всегда stable. |
| "derivedStateOf — замена remember(key)" | **Разное назначение.** `remember(key)` пересчитывает при смене key. `derivedStateOf` пересчитывает при изменении state внутри блока, но уведомляет только при смене результата (distinctUntilChanged). |
| "Нужно везде ставить @Stable/@Immutable" | **Преждевременная оптимизация.** Компилятор сам определяет stability для data classes с val fields. Аннотации нужны только когда inference не работает (multi-module, collections). Сначала профилируй. |
| "LazyColumn быстрее Column для любого списка" | Для маленьких списков (< 10 элементов) Column может быть быстрее — нет overhead на lazy loading. LazyColumn важен для больших/бесконечных списков с recycling. |
| "Compose медленнее View" | В production режиме Compose сравним или быстрее. Debug mode медленнее из-за assertions. Strong Skipping + правильная stability = меньше work чем View invalidation. |
| "Side effects — это плохо" | Side effects — это инструмент. LaunchedEffect для async, DisposableEffect для cleanup, SideEffect для sync callbacks. Плохо — side effects в composition phase напрямую (без wrappers). |
| "Modifier.graphicsLayer — просто для анимаций" | graphicsLayer создаёт отдельный RenderNode (hardware layer). Изменения внутри graphicsLayer не требуют relayout — только redraw. Используйте для любых частых изменений (scroll parallax, alpha changes). |

---

## CS-фундамент

| CS-концепция | Применение в Compose |
|--------------|---------------------|
| **Memoization** | `remember` — кэширование результатов функций по inputs. Slot Table хранит memoized values. Positional memoization = кэш по позиции в коде, не по ключу. |
| **Gap Buffer** | Slot Table — Gap Buffer для хранения composition state. O(1) sequential access идеален для top-down UI traversal. Вставка/удаление в текущей позиции O(1). |
| **Tree diffing** | Recomposition = сравнение нового дерева со старым. Но благодаря positional memoization, diffing не нужен для stable composables — они просто skip. |
| **Snapshot isolation** | Database concept в UI: каждый frame видит consistent snapshot state. Изменения накапливаются и применяются атомарно. Thread-safe без locks для reads. |
| **Functional programming** | Composables = pure functions с side effects через explicit APIs (LaunchedEffect, SideEffect). State hoisting = lifting state up. Unidirectional data flow. |
| **Immutability** | @Immutable обещает что объект никогда не изменится. Compose полагается на это для skipping. Mutable objects (List, var) = unstable = не skip. |
| **Reactive programming** | State = Observable. При изменении state автоматически уведомляются subscribers (composables которые читали state). Push-based updates. |
| **DAG (Directed Acyclic Graph)** | Composition = DAG где nodes = composables, edges = вызовы. Recomposition распространяется по графу от изменённого state к затронутым composables. |
| **Coroutines / Structured concurrency** | LaunchedEffect автоматически cancel при выходе из composition. CoroutineScope привязан к lifecycle. Structured concurrency гарантирует cleanup. |
| **Observer pattern** | SnapshotStateObserver отслеживает какие composables читали какой state. При изменении state уведомляет только affected observers. Fine-grained invalidation. |

---

## Куда дальше (Навигация)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LEARNING PATH                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  → Если новичок в Compose:                                          │
│    [[android-compose]] — basics, syntax, основные концепции         │
│    [[android-state-management]] — state hoisting, ViewModel         │
│                                                                     │
│  → Если хочешь оптимизировать performance:                          │
│    [[android-performance-profiling]] — Layout Inspector, Perfetto   │
│    [[android-view-rendering-pipeline]] — сравнение с View system    │
│                                                                     │
│  → Если хочешь понять animation internals:                          │
│    Modifier.graphicsLayer — hardware layers                         │
│    animateXAsState — state-based animations                         │
│                                                                     │
│  → Смежные темы:                                                    │
│    [[android-custom-view-fundamentals]] — когда нужен custom        │
│    [[kotlin-coroutines]] — для понимания LaunchedEffect             │
│    [[android-architecture-patterns]] — MVVM/MVI с Compose           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Связь с другими темами

**[[android-compose]]** — основы Compose UI (composable functions, state, modifiers, layouts) являются обязательным prerequisite. Internals объясняют, ПОЧЕМУ Compose работает так, как описано в basics: почему remember сохраняет значения (Slot Table), почему @Stable влияет на recomposition (Compose Compiler), и почему порядок вызовов composables важен (positional memoization).

**[[android-view-rendering-pipeline]]** — сравнение View rendering pipeline (measure -> layout -> draw) с Compose three-phase rendering (Composition -> Layout -> Drawing) показывает принципиальные различия: Compose выполняет phases независимо и может пропускать фазы (например, при изменении цвета пропускается Composition и Layout). Понимание обоих подходов важно для migration и interop.

**[[android-state-management]]** — Snapshot System в Compose internals является фундаментом state management. MutableState, derivedStateOf и snapshotFlow работают через Snapshot isolation (аналог MVCC в базах данных), что объясняет thread safety и automatic recomposition tracking. Изучение state patterns помогает избежать ненужных recompositions.

**[[android-performance-profiling]]** — Layout Inspector, Compose compiler reports (stability diagnostics), и Perfetto traces — основные инструменты для диагностики проблем производительности Compose. Recomposition counter, stability annotations (@Stable, @Immutable) и Strong Skipping Mode видны через эти инструменты. Профилирование необходимо для оптимизации Compose UI.

---

## Проверь себя

1. Что добавляет Compose Compiler к @Composable функции?
2. Что такое Slot Table и зачем нужен Gap Buffer?
3. Назовите три фазы рендеринга Compose.
4. Чем derivedStateOf отличается от remember(key)?
5. Почему List как параметр вызывает проблемы со skipping?
6. Что такое Strong Skipping Mode?
7. Когда использовать LaunchedEffect vs DisposableEffect?
8. Как порядок модификаторов влияет на результат?
9. Что такое positional memoization?
10. Как Snapshot System отслеживает изменения state?

---

## Источники и дальнейшее чтение

**Книги:**
- Moskala M. (2021). Effective Kotlin. — лучшие практики Kotlin: immutability, sealed classes, inline functions — паттерны, лежащие в основе Compose internals
- Moskala M. (2022). Kotlin Coroutines: Deep Dive. — корутины и их роль в Compose: LaunchedEffect использует coroutines, Snapshot System интегрирован с structured concurrency
- Meier R. (2022). Professional Android, 4th Edition. — комплексное руководство по Android-разработке, включая Compose fundamentals и architecture

**Веб-ресурсы:**
- [Android Developers — Compose Phases](https://developer.android.com/develop/ui/compose/phases)
- [Android Developers — Side Effects](https://developer.android.com/develop/ui/compose/side-effects)
- [Android Developers — Stability](https://developer.android.com/develop/ui/compose/performance/stability)
- [Android Developers — Best Practices](https://developer.android.com/develop/ui/compose/performance/bestpractices)
- [Medium — derivedStateOf](https://medium.com/androiddevelopers/jetpack-compose-when-should-i-use-derivedstateof-63ce7954c11b)
- [Medium — Stability Explained](https://medium.com/androiddevelopers/jetpack-compose-stability-explained-79c10db270c8)
- [Jorge Castillo — Compose Internals Book](https://jorgecastillo.dev/book/)
- [Compose Compiler Plugin — Playground](https://foso.github.io/Jetpack-Compose-Playground/general/compiler_plugin/)
- [droidcon — Compose Stability Analyzer](https://www.droidcon.com/2025/12/08/compose-stability-analyzer-real-time-stability-insights-for-jetpack-compose/)

---

*Проверено: 2026-01-09 | На основе официальной документации и deep research*

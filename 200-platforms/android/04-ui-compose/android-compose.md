---
title: "Jetpack Compose: декларативный UI"
created: 2025-12-17
modified: 2026-02-13
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/compose
  - topic/ui
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-threading]]"
  - "[[android-architecture-patterns]]"
  - "[[kotlin-basics]]"
  - "[[kotlin-functional]]"
  - "[[android-compose-internals]]"
cs-foundations: [declarative-programming, functional-ui, immutability, tree-diffing]
prerequisites:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
reading_time: 34
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Jetpack Compose: декларативный UI

Jetpack Compose — современный UI toolkit для Android, заменяющий XML layouts и View system. Вместо императивного описания "как" изменить UI, Compose использует декларативный подход "что" должно отображаться. UI автоматически обновляется при изменении state.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android-приложений
> - [[kotlin-basics]] — Kotlin обязателен для Compose
> - Понимание декларативного vs императивного программирования (полезно)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Composable** | Функция с аннотацией @Composable, описывающая UI |
| **Recomposition** | Перевызов composable при изменении state |
| **State** | Данные, влияющие на UI |
| **State hoisting** | Подъём state в родительский composable |
| **Modifier** | Декорирование composable (размер, padding, click) |
| **Slot API** | Передача UI как параметра-lambda |
| **Side Effect** | Операция вне композиции (запрос данных, навигация) |

---

## Настройка (2024-2025)

```kotlin
// build.gradle.kts (app)
plugins {
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21"
}

android {
    buildFeatures {
        compose = true
    }
}

dependencies {
    // BOM управляет версиями всех Compose библиотек
    val composeBom = platform("androidx.compose:compose-bom:2024.12.01")
    implementation(composeBom)

    // Core
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    debugImplementation("androidx.compose.ui:ui-tooling")

    // Integration
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("androidx.navigation:navigation-compose:2.8.5")

    // Hilt (опционально)
    implementation("androidx.hilt:hilt-navigation-compose:1.3.0")
}
```

**Что нового в 2024-2025:**
- **Kotlin 2.0** — новый Compose Compiler Plugin (встроен в Kotlin)
- **Strong Skipping Mode** — включён по умолчанию с Kotlin 2.0.20
- **Compose BOM 2024.12** — стабильная версия всех библиотек
- **Material 3** — актуальная версия дизайн-системы

---

## Declarative vs Imperative UI

### Imperative (View system)

```kotlin
// XML: описание структуры
<TextView
    android:id="@+id/counter"
    android:text="0" />
<Button
    android:id="@+id/button"
    android:text="Increment" />

// Kotlin: изменение состояния
var count = 0
button.setOnClickListener {
    count++
    counterTextView.text = count.toString()  // Императивное обновление
}
```

**Проблемы:**
- UI и state рассинхронизируются (забыли обновить View)
- Сложно отслеживать, кто и когда меняет View
- Много boilerplate (findViewById, nullability)

### Declarative (Compose)

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")  // Автоматически обновится
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Принцип:** UI = f(state). Изменился state → UI перерисовывается.

### Почему declarative лучше для UI

**Проблема императивного подхода: несинхронизация state и UI**

```kotlin
// Императивный код: 5 мест где нужно обновить UI
class ProfileActivity : AppCompatActivity() {
    private var user: User? = null

    fun loadUser() {
        showLoading()  // 1. Показать loading
        api.getUser { result ->
            hideLoading()  // 2. Скрыть loading
            when (result) {
                is Success -> {
                    user = result.data
                    nameTextView.text = user.name     // 3. Обновить имя
                    emailTextView.text = user.email   // 4. Обновить email
                    avatarView.load(user.avatarUrl)   // 5. Загрузить аватар
                }
                is Error -> {
                    errorView.text = result.message   // 6. Показать ошибку
                    errorView.visibility = VISIBLE    // 7. Сделать видимым
                }
            }
        }
    }

    // Проблема: что если забыли hideLoading() в одном месте?
    // Проблема: что если user изменился пока загружался аватар?
    // Проблема: что если нужно добавить новое поле — сколько мест менять?
}
```

**Декларативный подход: один источник истины**

```kotlin
@Composable
fun ProfileScreen(viewModel: ProfileViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // UI = f(state) — ВСЕГДА синхронизированы
    when (state) {
        is Loading -> CircularProgressIndicator()
        is Success -> UserProfile(state.user)
        is Error -> ErrorMessage(state.message)
    }
    // Добавить поле? Измени data class — UI обновится автоматически
}
```

### Конкретные преимущества Compose

| Проблема View System | Решение в Compose |
|---------------------|-------------------|
| findViewById + null checks | Нет ID, нет null |
| XML + Kotlin = 2 языка | Только Kotlin |
| Забыли обновить View | Автоматический recomposition |
| Сложная анимация | `animate*AsState` в одну строку |
| Кастомные View требуют Java | Обычные Kotlin функции |
| RecyclerView boilerplate | LazyColumn в 10 строк |
| Fragment lifecycle hell | Простые composable функции |

### Недостатки Compose

Compose не идеален, важно понимать trade-offs:

1. **Кривая обучения.** Новая ментальная модель. Разработчики с опытом View System переучиваются 2-4 недели.

2. **Recomposition может быть дорогим.** Если не понимаешь как работает — легко создать performance проблемы:
   ```kotlin
   // ПЛОХО: создаёт новый объект каждую recomposition
   Button(onClick = { viewModel.onClick() }) // Lambda создаётся заново

   // ХОРОШО: remember lambda
   val onClick = remember { { viewModel.onClick() } }
   Button(onClick = onClick)
   ```

3. **Сложная отладка.** Stack trace показывает Compose internals, не ваш код. Layout Inspector нужно учиться использовать.

4. **Интеграция с View.** Старые библиотеки (MapView, WebView, ExoPlayer) требуют AndroidView wrapper:
   ```kotlin
   AndroidView(
       factory = { context -> MapView(context) },
       update = { mapView -> mapView.setLocation(location) }
   )
   ```

5. **Размер APK.** Compose добавляет ~2-5MB к размеру приложения.

## Когда НЕ использовать Compose

### Ситуации где View system может быть лучше

**1. Существующий большой проект на Views:**
- Миграция требует времени и ресурсов
- Compose и Views можно смешивать, но это усложняет код
- ROI миграции не всегда положительный

**2. Специфические компоненты:**
- WebView, MapView, VideoView — нативные View, оборачивание в Compose добавляет complexity
- Custom View с complex rendering logic — может потребовать AndroidView wrapper

**3. Команда без Kotlin-экспертизы:**
- Compose требует хорошего понимания Kotlin (lambda, reified, delegates)
- Обучение команды — инвестиция

**4. Performance-критичные списки:**
- LazyColumn для 99% случаев достаточен
- Но RecyclerView с оптимизированными ViewHolders может быть быстрее в edge cases

### Признаки неправильного использования Compose

| Симптом | Проблема |
|---------|----------|
| Постоянные recomposition | State management неправильный |
| remember{} везде | Скорее всего нужен ViewModel |
| @Composable функции >100 строк | Нарушение single responsibility |
| Много derivedStateOf | Возможно overcomplicated state |

### Почему Google выбрал декларативный подход

1. **Индустрия движется туда:** React (2013), Flutter (2017), SwiftUI (2019) — все используют declarative UI. Это не эксперимент, а проверенный подход.

2. **View System устарел:** Создан в 2008 году, наследует проблемы архитектуры того времени. Compose написан с нуля с учётом современных требований.

3. **Kotlin-first:** View System создавался для Java. Compose использует все возможности Kotlin: lambdas, extension functions, coroutines.

4. **Multiplatform:** Compose может работать на Desktop, Web, iOS (через Compose Multiplatform). View System — только Android.

---

## Composable функции

### Основы

```kotlin
@Composable
fun Greeting(name: String) {
    Text("Hello, $name!")
}

// Использование
@Composable
fun MyScreen() {
    Greeting(name = "World")
}
```

**Правила composable:**
1. Аннотация `@Composable`
2. Можно вызывать только из других composable
3. Нет возвращаемого значения (описывают UI, не создают)
4. Могут быть вызваны много раз (recomposition)

### Базовые composables

```kotlin
@Composable
fun BasicExamples() {
    // Текст
    Text(
        text = "Hello",
        fontSize = 24.sp,
        fontWeight = FontWeight.Bold,
        color = Color.Blue
    )

    // Кнопка
    Button(onClick = { /* действие */ }) {
        Text("Click me")
    }

    // Поле ввода
    var text by remember { mutableStateOf("") }
    TextField(
        value = text,
        onValueChange = { text = it },
        label = { Text("Enter name") }
    )

    // Изображение
    Image(
        painter = painterResource(R.drawable.icon),
        contentDescription = "Icon"
    )

    // Иконка
    Icon(
        imageVector = Icons.Default.Favorite,
        contentDescription = "Favorite"
    )
}
```

### Layouts

```kotlin
@Composable
fun LayoutExamples() {
    // Вертикальный список
    Column {
        Text("First")
        Text("Second")
        Text("Third")
    }

    // Горизонтальный список
    Row {
        Text("Left")
        Spacer(Modifier.width(8.dp))
        Text("Right")
    }

    // Наложение элементов
    Box {
        Image(painter = painterResource(R.drawable.bg), "")
        Text("Overlay text")
    }

    // Сложный layout с constraints
    ConstraintLayout {
        val (button, text) = createRefs()

        Button(
            onClick = { },
            modifier = Modifier.constrainAs(button) {
                top.linkTo(parent.top, margin = 16.dp)
            }
        ) { Text("Button") }

        Text(
            text = "Text below button",
            modifier = Modifier.constrainAs(text) {
                top.linkTo(button.bottom, margin = 8.dp)
            }
        )
    }
}
```

---

## Modifier: декорирование UI

Modifier определяет размер, внешний вид и поведение composable:

```kotlin
@Composable
fun ModifierExample() {
    Text(
        text = "Styled Text",
        modifier = Modifier
            .fillMaxWidth()              // Занять всю ширину
            .padding(16.dp)              // Внутренний отступ
            .background(Color.LightGray) // Фон
            .clickable { /* клик */ }    // Обработка клика
            .border(1.dp, Color.Black)   // Граница
    )
}
```

**Порядок важен:**
```kotlin
// Разный результат!
Modifier.padding(16.dp).background(Color.Red)  // Padding внутри цветной области
Modifier.background(Color.Red).padding(16.dp)  // Padding снаружи цветной области
```

### Частые модификаторы

```kotlin
// Размеры
Modifier.width(100.dp)
Modifier.height(50.dp)
Modifier.size(100.dp)  // width = height
Modifier.fillMaxWidth()
Modifier.fillMaxHeight()
Modifier.fillMaxSize()
Modifier.wrapContentSize()

// Отступы
Modifier.padding(16.dp)  // Все стороны
Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
Modifier.padding(start = 8.dp, top = 16.dp)

// Оформление
Modifier.background(Color.Blue)
Modifier.background(Color.Blue, RoundedCornerShape(8.dp))
Modifier.border(1.dp, Color.Black, RoundedCornerShape(8.dp))
Modifier.clip(CircleShape)
Modifier.shadow(4.dp, RoundedCornerShape(8.dp))

// Взаимодействие
Modifier.clickable { }
Modifier.scrollable(state, Orientation.Vertical)
```

---

## State: сердце Compose

### remember и mutableStateOf

```kotlin
@Composable
fun Counter() {
    // remember: сохранить значение между recomposition
    // mutableStateOf: создать observable state
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**Без remember:**
```kotlin
// ПЛОХО: count сбрасывается при каждой recomposition
var count by mutableStateOf(0)  // Каждый раз 0!
```

### rememberSaveable: пережить config change

```kotlin
@Composable
fun CounterSurvivesRotation() {
    // rememberSaveable: сохранить при повороте экрана
    var count by rememberSaveable { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

### State Hoisting

Подъём state в родительский composable для переиспользования:

```kotlin
// ПЛОХО: state внутри, нельзя контролировать снаружи
@Composable
fun NameInput() {
    var name by remember { mutableStateOf("") }
    TextField(value = name, onValueChange = { name = it })
}

// ХОРОШО: state hoisting
@Composable
fun NameInput(
    name: String,               // State
    onNameChange: (String) -> Unit  // Event
) {
    TextField(value = name, onValueChange = onNameChange)
}

// Использование
@Composable
fun Screen() {
    var name by remember { mutableStateOf("") }
    NameInput(name = name, onNameChange = { name = it })

    // Можем использовать name в другом месте
    Text("Hello, $name")
}
```

**Паттерн:** State вниз, Events вверх.

---

## Recomposition: когда UI обновляется

### Что вызывает recomposition

```kotlin
@Composable
fun Example() {
    var count by remember { mutableStateOf(0) }

    // Изменение count вызовет recomposition этого composable
    Text("Count: $count")

    Button(onClick = {
        count++  // Триггер recomposition
    }) {
        Text("Increment")
    }
}
```

### Smart Recomposition

Compose перерисовывает только то, что изменилось:

```kotlin
@Composable
fun Parent() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Только этот Text перерисуется при изменении count
        Text("Count: $count")

        // Этот composable НЕ перерисуется (не зависит от count)
        ExpensiveComposable()

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

### Стабильность и skipping

Compose пропускает recomposition если параметры не изменились:

```kotlin
// Stable: Compose может пропустить recomposition
data class User(val id: Int, val name: String)

// Unstable: всегда recomposition (List mutable снаружи)
data class UserList(val users: List<User>)

// Решение: @Immutable или @Stable аннотации
@Immutable
data class UserList(val users: List<User>)
```

### Strong Skipping Mode (Kotlin 2.0.20+)

**До Strong Skipping:**
```kotlin
// List всегда unstable → UserList ВСЕГДА recomposes
@Composable
fun UserList(users: List<User>) {
    // Вызывается каждый раз, даже если users не изменился
}
```

**С Strong Skipping (default в Kotlin 2.0.20+):**
```kotlin
// Проверяется reference equality (===)
@Composable
fun UserList(users: List<User>) {
    // Skip если users === предыдущий instance
    // Recompose только если reference изменилась
}

// Это работает если сохраняете reference:
val users = remember { mutableListOf(1, 2, 3) }
UserList(users)  // Skips — same reference
```

**Таблица стабильности:**

| Тип | Stable? | Skipping (Strong Mode) |
|-----|---------|------------------------|
| `Int, String, Boolean` | ✅ | Skip по `equals()` |
| `data class` (immutable fields) | ✅ | Skip по `equals()` |
| `List, Map, Set` | ❌ | Skip по `===` reference |
| `class` с `var` | ❌ | Skip по `===` reference |
| `@Immutable data class` | ✅ | Skip по `equals()` |

**Рекомендация:** используйте `kotlinx.collections.immutable` для стабильных коллекций:
```kotlin
// build.gradle.kts
implementation("org.jetbrains.kotlinx:kotlinx-collections-immutable:0.3.7")

// Код
import kotlinx.collections.immutable.ImmutableList

@Composable
fun UserList(users: ImmutableList<User>) {  // Stable!
    // Skip по equals()
}
```

---

## Side Effects

### LaunchedEffect

Для операций при входе в composition:

```kotlin
@Composable
fun UserProfile(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }

    // Запустится при первой composition и при изменении userId
    LaunchedEffect(userId) {
        user = repository.getUser(userId)
    }

    user?.let {
        Text("Name: ${it.name}")
    }
}
```

### rememberCoroutineScope

Для запуска coroutines по событию:

```kotlin
@Composable
fun SubmitButton() {
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            repository.submit()
        }
    }) {
        Text("Submit")
    }
}
```

### DisposableEffect

Для cleanup при выходе из composition:

```kotlin
@Composable
fun LifecycleObserver(lifecycleOwner: LifecycleOwner) {
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            Log.d("Lifecycle", "Event: $event")
        }
        lifecycleOwner.lifecycle.addObserver(observer)

        // Cleanup
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }
}
```

### SideEffect

Для синхронизации с non-Compose кодом:

```kotlin
@Composable
fun Analytics(screenName: String) {
    // Вызывается после каждой успешной recomposition
    SideEffect {
        analytics.trackScreen(screenName)
    }
}
```

### rememberUpdatedState

Для захвата последнего значения без перезапуска effect:

```kotlin
@Composable
fun Timer(onTimeout: () -> Unit) {
    // Проблема: если onTimeout изменится, LaunchedEffect не перезапустится
    // (Unit как ключ = никогда не перезапускать)

    // Решение: rememberUpdatedState
    val currentOnTimeout by rememberUpdatedState(onTimeout)

    LaunchedEffect(Unit) {
        delay(5000)
        currentOnTimeout()  // Всегда вызывает актуальный callback
    }
}
```

---

## derivedStateOf: distinctUntilChanged для Compose

```kotlin
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()

    // ❌ ПЛОХО: recomposition при КАЖДОМ scroll событии
    val showButton = listState.firstVisibleItemIndex > 0

    // ✅ ХОРОШО: recomposition только когда showButton МЕНЯЕТСЯ
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }

    LazyColumn(state = listState) {
        items(100) { index ->
            Text("Item $index")
        }
    }

    // Кнопка "наверх" показывается только когда прокрутили
    AnimatedVisibility(visible = showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) {
            Icon(Icons.Default.KeyboardArrowUp, "Scroll to top")
        }
    }
}
```

**Когда использовать derivedStateOf:**
- Input меняется чаще чем output
- Пример: scroll position → show/hide button (много scroll events, редко меняется boolean)

**Когда НЕ использовать:**
- Input и output меняются с одинаковой частотой
- Простые трансформации без фильтрации

---

## Phase Skipping: оптимизация рендеринга

Compose имеет три фазы: **Composition → Layout → Drawing**.
Читайте state в правильной фазе для оптимизации:

```kotlin
@Composable
fun OptimizedScroll() {
    val scrollState = rememberScrollState()

    // ❌ ПЛОХО: читаем в Composition → recomposition каждый frame
    val offset = scrollState.value
    Box(Modifier.offset(y = offset.dp))

    // ✅ ХОРОШО: читаем в Layout → только layout + draw, без recomposition
    Box(
        Modifier.offset {
            IntOffset(0, scrollState.value)  // Lambda читает в layout phase
        }
    )

    // ✅ ЛУЧШЕ для цвета: читаем в Draw → только draw
    Box(
        Modifier.drawBehind {
            drawRect(color = if (scrollState.value > 100) Color.Red else Color.Blue)
        }
    )
}
```

**Таблица phase skipping:**

| Где читаем state | Что перезапускается | Когда использовать |
|------------------|--------------------|--------------------|
| Composition | Composition + Layout + Draw | Структурные изменения UI |
| Layout lambda | Layout + Draw | Позиция, размер |
| Draw lambda | Только Draw | Цвет, alpha, визуальные эффекты |

---

## Списки: LazyColumn/LazyRow

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        // Заголовок
        item {
            Text("Users", style = MaterialTheme.typography.headlineMedium)
        }

        // Список элементов
        items(
            items = users,
            key = { it.id }  // Важно для стабильности!
        ) { user ->
            UserCard(user)
        }

        // Footer
        item {
            Text("End of list")
        }
    }
}

@Composable
fun UserCard(user: User) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Text(
            text = user.name,
            modifier = Modifier.padding(16.dp)
        )
    }
}
```

**Важно:** Всегда указывайте `key` для стабильной recomposition.

---

## Интеграция с ViewModel

```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (uiState) {
        is UiState.Loading -> {
            CircularProgressIndicator()
        }
        is UiState.Success -> {
            UserList(users = (uiState as UiState.Success).users)
        }
        is UiState.Error -> {
            Text("Error: ${(uiState as UiState.Error).message}")
            Button(onClick = { viewModel.retry() }) {
                Text("Retry")
            }
        }
    }
}
```

**collectAsStateWithLifecycle** автоматически:
- Собирает Flow
- Учитывает lifecycle (pause/resume collection)
- Конвертирует в Compose State

---

## Навигация

```kotlin
// Определение навигации
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onUserClick = { userId ->
                    navController.navigate("user/$userId")
                }
            )
        }

        composable(
            route = "user/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
            UserScreen(userId = userId)
        }
    }
}
```

---

## Чеклист

```
□ State hoisting: state вверх, events вниз
□ remember для сохранения state между recomposition
□ rememberSaveable для сохранения при config change
□ key в LazyColumn/LazyRow для стабильности
□ Modifier.clickable вместо onClick где возможно
□ collectAsStateWithLifecycle для Flow
□ LaunchedEffect для side effects с lifecycle
□ @Immutable/@Stable для data classes где нужно
□ Избегать создания объектов в composition
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Compose полностью заменил View system" | Неправильно. Compose работает ПОВЕРХ View system. ComposeView — это View. Canvas в Compose — тот же android.graphics.Canvas. Interop (AndroidView, ComposeView) позволяет смешивать системы. Для некоторых задач (MapView, WebView, Camera) всё ещё нужны View |
| "Recomposition = полная перерисовка UI" | Нет. Recomposition — только ПЕРЕВЫЗОВ composable функций. Drawing происходит отдельно и только если Layout изменился. Compose умеет skip неизменённые composables благодаря Positional Memoization |
| "remember сохраняет при повороте экрана" | Нет! `remember{}` сохраняет только между recomposition. При configuration change (поворот) Activity пересоздаётся → Composition пересоздаётся → remember теряется. Для сохранения нужен `rememberSaveable{}` |
| "State нужно всегда поднимать в ViewModel" | Не всегда. UI-only state (scroll position, animation state, focus) может жить в Composable. В ViewModel — только business/screen state. Чрезмерный hoisting усложняет код без пользы |
| "LaunchedEffect запускается один раз" | Зависит от key. `LaunchedEffect(Unit)` — да, один раз. `LaunchedEffect(userId)` — перезапустится при изменении userId. Без понимания key легко получить утечки или пропущенные обновления |
| "derivedStateOf нужен для всех вычислений" | Нет! derivedStateOf нужен только когда входных изменений БОЛЬШЕ, чем выходных. Например, фильтрация списка при каждом нажатии клавиши. Для простых преобразований derivedStateOf добавляет overhead |
| "Modifier.clickable и onClick одинаковы" | Разная семантика. Button с onClick — семантически кнопка (accessibility, ripple, enabled state). Modifier.clickable — generic clickable area. Для кнопок используй Button, для кастомных элементов — Modifier.clickable |
| "key в LazyColumn не важен" | Критически важен! Без стабильного key при изменении списка Compose не может правильно сопоставить items. Результат: потеря состояния (scroll, animation), лишние recomposition, UI глюки |
| "@Stable/@Immutable нужны везде" | Нет. С Strong Skipping Mode (Compose 1.7+) data class без аннотаций автоматически считается stable если все поля stable. Аннотации нужны для: классов с var, классов из других модулей, интерфейсов |
| "Compose медленнее View system" | При правильном использовании — сравнимая производительность. Проблемы возникают от: создания объектов в composition, нестабильных лямбд, отсутствия key, избыточных recomposition. Layout Inspector показывает проблемы |

---

## CS-фундамент

| CS-концепция | Как применяется в Compose |
|--------------|---------------------------|
| **Functional Programming** | Composable функции — чистые функции без side effects. UI = f(state). Тот же state → тот же UI. Immutability входных данных обеспечивает предсказуемость |
| **Memoization** | Positional Memoization — кэширование результатов composable на основе позиции в дереве + параметров. Если параметры не изменились → skip recomposition. remember{} — explicit memoization |
| **Structural Equality** | Compose сравнивает параметры через equals() для определения необходимости recomposition. @Stable обещает корректную реализацию equals(). Неправильный equals() ломает skipping |
| **Unidirectional Data Flow** | State flows down (от parent к child), Events flow up (от child к parent через callbacks). Single source of truth. Предсказуемость состояния, проще debugging |
| **Declarative Programming** | Описываем ЧТО показать, не КАК. Нет императивных view.setText(). Compose сам вычисляет минимальный diff и применяет изменения |
| **Tree Diffing** | Slot Table хранит UI tree. При recomposition Compose сравнивает новое и старое дерево, применяя минимальные изменения. Аналог Virtual DOM в React |
| **Reactive Programming** | State<T> — observable pattern. Подписка через чтение в composition. Изменение state автоматически триггерит recomposition подписчиков. Push-based реактивность |
| **Coroutines / Structured Concurrency** | LaunchedEffect, rememberCoroutineScope связаны с lifecycle. Отмена при выходе из composition. Structured concurrency предотвращает утечки |
| **Scope Functions** | Modifier chain использует fluent interface. Trailing lambda DSL для декларативного описания UI. Extension functions для composables |
| **Inversion of Control** | Compose runtime управляет жизненным циклом composition. Мы описываем UI, framework решает когда и как обновлять. CompositionLocal — DI для implicit параметров |

---

## Связь с другими темами

**[[android-overview]]** — Activity и Fragment являются хостами для Compose UI через setContent {}. Понимание Android-платформы и компонентной модели необходимо для правильной интеграции Compose в существующие приложения. Compose не заменяет Activity — он работает внутри неё.

**[[android-activity-lifecycle]]** — Compose composition привязан к lifecycle хоста (Activity/Fragment). LaunchedEffect, DisposableEffect и rememberCoroutineScope автоматически отменяются при уничтожении lifecycle owner. Понимание lifecycle объясняет, почему collectAsStateWithLifecycle() предпочтительнее collectAsState() — он останавливает collection когда UI не виден.

**[[android-architecture-patterns]]** — MVI (Model-View-Intent) идеально сочетается с Compose благодаря unidirectional data flow: state flows down через параметры composable, events flow up через callback lambdas. ViewModel предоставляет StateFlow для UI state, а Compose подписывается через collectAsStateWithLifecycle(). Изучайте архитектурные паттерны параллельно с Compose.

**[[kotlin-flow]]** — Flow и StateFlow являются основным механизмом reactive state management в Compose. collectAsState()/collectAsStateWithLifecycle() конвертируют Flow в Compose State, triggering recomposition при новых значениях. Понимание cold/hot flows, operators и backpressure необходимо для эффективного Compose UI.

**[[android-compose-internals]]** — глубокое погружение в архитектуру Compose (Compiler Plugin, Slot Table, Snapshot System). Объясняет, КАК работает recomposition, почему @Stable и @Immutable влияют на производительность, и как Gap Buffer оптимизирует tree updates. Рекомендуется после освоения Compose basics для оптимизации и debugging.

**[[android-ui-views]]** — классическая View system может сосуществовать с Compose через ComposeView (Compose в View hierarchy) и AndroidView (View в Compose). Понимание обоих подходов необходимо для постепенной миграции существующих приложений на Compose.

---

## Источники и дальнейшее чтение

**Книги:**
- Meier R. (2022). Professional Android, 4th Edition. — комплексное руководство по Android-разработке, включая Compose UI и интеграцию с Android ecosystem
- Moskala M. (2021). Effective Kotlin. — лучшие практики Kotlin (lambdas, DSL, immutability), являющиеся фундаментом Compose API design
- Leiva A. (2017). Kotlin for Android Developers. — Kotlin-first Android разработка, базовые языковые конструкции для понимания Compose syntax

**Официальная документация:**
- [Jetpack Compose Documentation](https://developer.android.com/develop/ui/compose/documentation) — официальная документация
- [Compose Performance](https://developer.android.com/develop/ui/compose/performance) — оптимизация производительности
- [Compose Phases](https://developer.android.com/develop/ui/compose/phases) — три фазы рендеринга
- [Side Effects](https://developer.android.com/develop/ui/compose/side-effects) — LaunchedEffect, DisposableEffect
- [Stability Explained](https://medium.com/androiddevelopers/jetpack-compose-stability-explained-79c10db270c8) — @Stable, Strong Skipping

**Практические ресурсы:**
- [Jetpack Compose Basics Codelab](https://developer.android.com/codelabs/jetpack-compose-basics) — практический codelab
- [Official Compose Samples](https://github.com/android/compose-samples) — примеры от Google
- [derivedStateOf Usage](https://medium.com/androiddevelopers/jetpack-compose-when-should-i-use-derivedstateof-63ce7954c11b) — когда использовать

---

---

## Проверь себя

> [!question]- Почему Compose использует декларативный подход вместо императивного (XML + findViewById)?
> Императивный подход требует ручной синхронизации UI и данных: при изменении данных нужно найти View и обновить его. Это приводит к багам при несоответствии состояний. Декларативный подход описывает UI как функцию от state: UI = f(state). При изменении state Compose автоматически перекомпонует только изменившиеся части. Меньше кода, меньше багов.

> [!question]- Сценарий: LazyColumn с 1000 элементов тормозит при скролле. DiffUtil нет в Compose. Как Compose оптимизирует это?
> LazyColumn использует key() для идентификации элементов. Compose пропускает recomposition для элементов с неизменившимся state через smart recomposition. Для оптимизации: 1) Использовать key(item.id) вместо индекса. 2) Сделать item data classes stable (val, не var). 3) Использовать derivedStateOf для вычисляемых значений. 4) Избегать тяжелых операций в composable.

> [!question]- Почему в Compose нельзя использовать var counter = 0 для хранения состояния?
> Composable функции могут вызываться многократно при recomposition. Локальная переменная пересоздается при каждом вызове, теряя значение. remember {} сохраняет значение через recomposition в SlotTable. mutableStateOf() дополнительно уведомляет Compose об изменении для запуска recomposition.


---

## Ключевые карточки

Что такое recomposition в Compose?
?
Повторный вызов composable-функции при изменении state. Compose отслеживает какие state читает каждая функция и перевызывает ТОЛЬКО те, чьи inputs изменились. Аналог invalidate() в View system, но более гранулярный.

Чем remember отличается от rememberSaveable?
?
remember сохраняет значение через recomposition, но теряет при recreation (rotation). rememberSaveable сохраняет через process death/rotation используя SavedInstanceState. Для примитивов работает автоматически, для объектов нужен Saver.

Что такое Modifier в Compose?
?
Цепочка декораций для composable: размер, padding, click, background. Порядок важен: Modifier.padding(16.dp).background(Color.Red) отличается от Modifier.background(Color.Red).padding(16.dp). Аналог XML атрибутов, но composable.

Что такое Side Effect в Compose?
?
Операция, выходящая за scope composable (сеть, БД, логирование). LaunchedEffect -- запуск корутины привязанной к composition. DisposableEffect -- с cleanup. SideEffect -- каждую recomposition.

Что такое CompositionLocal?
?
Механизм implicit передачи данных по дереву composition. Аналог Context в React. LocalContext, LocalLifecycleOwner -- стандартные. Создается через compositionLocalOf() или staticCompositionLocalOf().

Чем Compose Navigation отличается от Fragment Navigation?
?
Compose Navigation: навигация между composable функциями, type-safe аргументы (с Navigation 2.8+), нет Fragment lifecycle overhead. Состояние сохраняется через rememberSaveable. BackStack управляется NavController.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-compose-internals]] | Как Compose работает под капотом: SlotTable, Compiler Plugin |
| Углубиться | [[android-state-management]] | Управление состоянием: StateFlow + Compose State |
| Смежная тема | [[ios-swiftui]] | SwiftUI -- декларативный UI в iOS, сравнение с Compose |
| Обзор | [[android-overview]] | Вернуться к карте раздела |


*Проверено: 2026-01-09 | Compose BOM 2024.12, Kotlin 2.0.21 | На основе официальной документации Android*

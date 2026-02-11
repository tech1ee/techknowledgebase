---
title: "View System: XML Layouts, ViewBinding, RecyclerView"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [view-hierarchy, object-pooling, adapter-pattern, layout-inflation]
tags:
  - topic/android
  - topic/ui
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-compose]]"
  - "[[android-threading]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
---

# View System: XML Layouts, ViewBinding, RecyclerView

View System — традиционный способ создания UI в Android. Хотя Jetpack Compose постепенно заменяет его, View System остаётся в миллионах существующих приложений и важен для понимания архитектуры Android UI.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android платформы и её компонентов
> - [[android-activity-lifecycle]] — Activity как host для Views, понимание когда View создаются и уничтожаются
> - Понимание XML разметки — синтаксис, атрибуты, вложенность элементов

---

## Терминология

| Термин | Значение |
|--------|----------|
| **View** | Базовый UI элемент (кнопка, текст, изображение) |
| **ViewGroup** | Контейнер для других View (Layout) |
| **Layout** | XML файл описывающий иерархию View |
| **ViewBinding** | Type-safe доступ к View без findViewById |
| **RecyclerView** | Эффективный список с переиспользованием элементов |
| **Adapter** | Связывает данные с View в списке |
| **LayoutInflater** | Создаёт View из XML |

---

## Почему View System устроен именно так?

### Проблема: как описать UI

UI приложения — это дерево элементов. Как его описать?

**Вариант 1: Код (императивный)**
```kotlin
// ❌ Императивное создание UI в коде
val layout = LinearLayout(context).apply {
    orientation = LinearLayout.VERTICAL
    layoutParams = ViewGroup.LayoutParams(MATCH_PARENT, MATCH_PARENT)
}

val textView = TextView(context).apply {
    text = "Hello"
    textSize = 18f
    layoutParams = LinearLayout.LayoutParams(WRAP_CONTENT, WRAP_CONTENT)
}

val button = Button(context).apply {
    text = "Click me"
    layoutParams = LinearLayout.LayoutParams(WRAP_CONTENT, WRAP_CONTENT).apply {
        topMargin = 16.dp
    }
}

layout.addView(textView)
layout.addView(button)
setContentView(layout)
```
**Проблемы:**
- Много boilerplate кода
- Сложно визуализировать структуру
- Нет preview в IDE
- Смешивание логики и представления

**Вариант 2: XML (декларативный)**
```xml
<!-- ✅ Декларативное описание в XML -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello"
        android:textSize="18sp" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="Click me" />

</LinearLayout>
```
**Преимущества:**
- Чистое разделение UI и логики
- Visual preview в Android Studio
- Легко читать структуру
- Дизайнеры могут работать с XML

### Почему не HTML/CSS?

| Критерий | HTML/CSS | Android XML |
|----------|----------|-------------|
| **Рендеринг** | Браузер (медленный) | Native (быстрый) |
| **Позиционирование** | Box model, float, flex | ConstraintLayout, LinearLayout |
| **Производительность** | Repaint весь DOM | Invalidate только изменённое |
| **Доступ из кода** | JavaScript + DOM API | ViewBinding / findViewById |
| **Styling** | CSS файлы | styles.xml, themes |

Android выбрал XML потому что:
1. Типизированные атрибуты (IDE подсказки, валидация)
2. Compile-time проверка ресурсов (@id, @string)
3. Оптимизация при сборке (binary XML)
4. Интеграция с ресурсной системой Android

### Недостатки View System (почему появился Compose)

1. **Mutable state:** View хранят своё состояние, сложно синхронизировать
2. **Двойная работа:** XML описывает структуру, код — поведение
3. **findViewById:** Runtime ошибки при опечатках
4. **Глубокая иерархия:** Вложенные layouts = медленный рендеринг
5. **Сложное обновление:** Нужно вручную обновлять каждый View

---

## XML Layouts

### Основные Layout контейнеры

```xml
<!-- LinearLayout: элементы в линию (вертикально или горизонтально) -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">
    <!-- Дети располагаются сверху вниз -->
</LinearLayout>

<!-- FrameLayout: элементы друг на друге (стек) -->
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <!-- Последний ребёнок сверху -->
</FrameLayout>

<!-- ConstraintLayout: гибкое позиционирование через constraints -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/title"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### Почему ConstraintLayout — стандарт

```
┌─────────────────────────────────────────────────────────────────┐
│                 ИЕРАРХИЯ LAYOUTS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Старый подход (вложенные layouts):                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ LinearLayout                                             │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │ LinearLayout                                     │    │   │
│  │  │  ┌─────────────────────────────────────────┐    │    │   │
│  │  │  │ RelativeLayout                           │    │    │   │
│  │  │  │  ┌─────────────┐  ┌─────────────┐       │    │    │   │
│  │  │  │  │  TextView   │  │   Button    │       │    │    │   │
│  │  │  │  └─────────────┘  └─────────────┘       │    │    │   │
│  │  │  └─────────────────────────────────────────┘    │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│  Глубина = 4 уровня → 4 прохода measure/layout                 │
│                                                                 │
│  ConstraintLayout (плоская иерархия):                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ConstraintLayout                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐                       │   │
│  │  │  TextView   │  │   Button    │  (constraints между)  │   │
│  │  └─────────────┘  └─────────────┘                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│  Глубина = 1 уровень → 1-2 прохода measure/layout              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ViewBinding: type-safe доступ к View

### Проблема: findViewById

```kotlin
// ❌ findViewById — проблемы
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Проблема 1: Опечатка в ID — crash в runtime
        val textView = findViewById<TextView>(R.id.tetxView)  // CRASH!

        // Проблема 2: Неправильный тип — crash в runtime
        val button = findViewById<Button>(R.id.textView)  // ClassCastException!

        // Проблема 3: View из другого layout — null или crash
        val otherView = findViewById<TextView>(R.id.viewFromOtherLayout)  // null

        // Проблема 4: Nullable — нужны null checks везде
        textView?.text = "Hello"
    }
}
```

### Решение: ViewBinding

```kotlin
// build.gradle.kts
android {
    buildFeatures {
        viewBinding = true
    }
}
```

```kotlin
// ✅ ViewBinding — compile-time safety
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Type-safe! IDE автокомплит, compile-time проверка
        binding.textView.text = "Hello"
        binding.button.setOnClickListener {
            // ...
        }

        // Опечатка? Не скомпилируется!
        // binding.tetxView  // ❌ Unresolved reference
    }
}
```

### ViewBinding в Fragment

```kotlin
class MyFragment : Fragment() {

    // Важно: nullable потому что view может быть уничтожен
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.textView.text = "Hello from Fragment"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // ВАЖНО: очищаем binding чтобы избежать memory leak
        _binding = null
    }
}
```

---

## RecyclerView: эффективные списки

### Почему не ListView

```
┌─────────────────────────────────────────────────────────────────┐
│              ListView vs RecyclerView                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ListView (старый подход):                                      │
│  ┌─────────────────┐                                            │
│  │    Item 1       │ ← View создан                              │
│  ├─────────────────┤                                            │
│  │    Item 2       │ ← View создан                              │
│  ├─────────────────┤                                            │
│  │    Item 3       │ ← View создан                              │
│  ├─────────────────┤                                            │
│  │    Item 4       │ ← View создан                              │
│  └─────────────────┘                                            │
│        ↓ scroll                                                  │
│  Item 1 уничтожен, Item 5 создан заново                         │
│  1000 items = 1000 созданий View (медленно!)                    │
│                                                                 │
│  RecyclerView (переиспользование):                              │
│  ┌─────────────────┐                                            │
│  │    Item 1       │ ← ViewHolder A                             │
│  ├─────────────────┤                                            │
│  │    Item 2       │ ← ViewHolder B                             │
│  ├─────────────────┤                                            │
│  │    Item 3       │ ← ViewHolder C                             │
│  ├─────────────────┤                                            │
│  │    Item 4       │ ← ViewHolder D                             │
│  └─────────────────┘                                            │
│        ↓ scroll                                                  │
│  ViewHolder A переиспользуется для Item 5                       │
│  1000 items = ~10 ViewHolder (только видимые + буфер)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Базовая реализация

```kotlin
// Data class
data class User(val id: Long, val name: String, val email: String)

// ViewHolder — держит ссылки на View
class UserViewHolder(
    private val binding: ItemUserBinding
) : RecyclerView.ViewHolder(binding.root) {

    fun bind(user: User) {
        binding.nameTextView.text = user.name
        binding.emailTextView.text = user.email
    }
}

// Adapter — создаёт ViewHolder и привязывает данные
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {

    private var users: List<User> = emptyList()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return UserViewHolder(binding)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(users[position])
    }

    override fun getItemCount(): Int = users.size

    fun submitList(newUsers: List<User>) {
        users = newUsers
        notifyDataSetChanged()  // Неэффективно! Используйте DiffUtil
    }
}

// В Activity/Fragment
binding.recyclerView.apply {
    layoutManager = LinearLayoutManager(context)
    adapter = userAdapter
}
```

### ListAdapter с DiffUtil

```kotlin
// ✅ Правильный подход — автоматический diff
class UserAdapter : ListAdapter<User, UserViewHolder>(UserDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return UserViewHolder(binding)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
        return oldItem.id == newItem.id  // Один и тот же item?
    }

    override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
        return oldItem == newItem  // Содержимое изменилось?
    }
}

// Использование
userAdapter.submitList(newUsers)  // Автоматически вычислит diff и анимирует
```

### Click handling

```kotlin
class UserAdapter(
    private val onItemClick: (User) -> Unit,
    private val onDeleteClick: (User) -> Unit
) : ListAdapter<User, UserViewHolder>(UserDiffCallback()) {

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        val user = getItem(position)
        holder.bind(user)

        holder.itemView.setOnClickListener {
            onItemClick(user)
        }

        holder.binding.deleteButton.setOnClickListener {
            onDeleteClick(user)
        }
    }
}

// Использование
val adapter = UserAdapter(
    onItemClick = { user -> navigateToDetail(user) },
    onDeleteClick = { user -> viewModel.deleteUser(user) }
)
```

---

## View Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIEW LIFECYCLE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Создание:                                                      │
│  ┌─────────────┐                                                │
│  │ Constructor │ ← View создан, но не измерен                   │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ onAttached  │ ← View добавлен в window                       │
│  │ ToWindow    │                                                │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │  onMeasure  │ ← Вычисление размеров (может вызваться         │
│  │             │   несколько раз!)                              │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │  onLayout   │ ← Позиционирование дочерних элементов          │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │   onDraw    │ ← Отрисовка на Canvas                          │
│  └─────────────┘                                                │
│                                                                 │
│  Обновление:                                                    │
│  invalidate() → onDraw (только перерисовка)                     │
│  requestLayout() → onMeasure → onLayout → onDraw (полный цикл) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Распространённые ошибки

### 1. Работа с View до onViewCreated

```kotlin
// ❌ ПЛОХО
class MyFragment : Fragment(R.layout.fragment_my) {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // View ещё не создан!
        binding.textView.text = "Hello"  // CRASH: NullPointerException
    }
}

// ✅ ХОРОШО
class MyFragment : Fragment(R.layout.fragment_my) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // View готов
        binding.textView.text = "Hello"
    }
}
```

### 2. Memory leak через binding в Fragment

```kotlin
// ❌ ПЛОХО: binding не очищается
class MyFragment : Fragment() {
    private lateinit var binding: FragmentMyBinding  // Утечка!

    override fun onDestroyView() {
        super.onDestroyView()
        // binding держит ссылку на destroyed view
    }
}

// ✅ ХОРОШО
class MyFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // Освобождаем ссылку
    }
}
```

### 3. Обновление UI не из Main Thread

```kotlin
// ❌ CRASH: Only the original thread can touch its views
thread {
    val data = loadData()
    binding.textView.text = data  // CalledFromWrongThreadException
}

// ✅ ХОРОШО
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) { loadData() }
    binding.textView.text = data  // OK, мы на Main Thread
}
```

---

## Когда View System vs Compose

### Decision Matrix

**View System лучше когда:**
- Поддержка существующего кодбазы с миллионами строк View-кода
- Команда не готова к обучению новой парадигме (декларативный UI)
- Нужна максимальная совместимость с древними версиями Android (API 16+)
- Критичен размер APK (каждый мегабайт важен)
- Используете библиотеки без Compose-версий (Maps, WebView, Camera)
- Нужен точный контроль над рендерингом через Canvas и onDraw

**Compose лучше когда:**
- Новый проект или новая фича в существующем
- UI часто меняется в зависимости от состояния (динамические формы, dashboards)
- Хотите быстрее писать UI код (меньше boilerplate)
- Команда знакома с React/Flutter/SwiftUI (похожие концепции)
- Нужны сложные анимации и transitions (проще API)
- Хотите единый код для Android и Desktop (Compose Multiplatform)

**Можно смешивать когда:**
- Постепенная миграция: экраны на Compose, старые — на Views
- `AndroidView` в Compose для интеграции View-виджетов (MapView, AdView)
- `ComposeView` в XML для внедрения Compose в существующий экран
- Переиспользование Custom Views в Compose (обернуть в AndroidView)

**Реальный пример:** Большое приложение может использовать Compose для новых фич, сохраняя Views для сложных экранов где уже работает стабильный код.

---

## Проверь себя

Прежде чем двигаться дальше, убедись что понимаешь ключевые концепции:

**1. Что такое View lifecycle (measure, layout, draw)?**
<details>
<summary>Ответ</summary>

View проходит 3 фазы рендеринга:
- **onMeasure()** — View вычисляет свой размер на основе constraints от родителя. Может вызваться несколько раз (например, при вложенных LinearLayout с weight).
- **onLayout()** — ViewGroup позиционирует своих детей. Каждому ребёнку назначается конкретная позиция (left, top, right, bottom).
- **onDraw()** — View рисует себя на Canvas. Здесь происходит actual отрисовка пикселей.

**Важно:** `invalidate()` запускает только onDraw, `requestLayout()` — весь цикл заново.
</details>

**2. Чем ConstraintLayout лучше вложенных LinearLayout?**
<details>
<summary>Ответ</summary>

**Производительность:** Вложенные LinearLayout создают глубокую иерархию. Каждый уровень — это проход measure/layout. Глубина 5 = 5 проходов. ConstraintLayout держит всех детей на одном уровне = 1-2 прохода.

**Пример:** Экран с аватаром, именем, email, кнопкой.
- LinearLayout: vertical → horizontal (avatar + text vertical) → button = 3 уровня
- ConstraintLayout: все 4 элемента на одном уровне с constraints между ними = 1 уровень

**Бонус:** Гибкость без вложенности. Можно центрировать, выравнивать, создавать chains без дополнительных контейнеров.
</details>

**3. Как работает RecyclerView и ViewHolder pattern?**
<details>
<summary>Ответ</summary>

**Проблема:** Список из 1000 элементов. Создавать 1000 View? Медленно и жрёт память.

**Решение:** ViewHolder pattern.
- RecyclerView создаёт ViewHolder только для видимых элементов (~10-15 штук).
- При скролле ViewHolder для ушедшего элемента переиспользуется для нового.
- `onCreateViewHolder()` вызывается редко (только создание).
- `onBindViewHolder()` вызывается часто (обновление данных).

**Аналогия:** Театр на 100 мест. Спектакли на 1000 человек. Не строить 1000 кресел — пускать партиями по 100, переиспользуя места.
</details>

**4. Почему invalidate() не перерисовывает View сразу?**
<details>
<summary>Ответ</summary>

**Оптимизация batching:** Android собирает все `invalidate()` вызовы и перерисовывает View один раз в следующем frame (~16ms).

**Пример:**
```kotlin
textView.text = "Hello"     // invalidate()
textView.textSize = 20f     // invalidate()
textView.setTextColor(RED)  // invalidate()
// Не 3 перерисовки, а 1 через 16ms
```

**Почему так:** 60 FPS = 16ms на frame. Все UI изменения внутри frame batch'атся и рисуются вместе. Это предотвращает мерцание и сохраняет производительность.

**Важно:** Если нужна немедленная перерисовка (редко), есть `postInvalidate()` или `invalidate()` + ручной вызов draw, но обычно это anti-pattern.
</details>

---

## Чеклист

```
□ Используем ConstraintLayout для плоской иерархии
□ ViewBinding вместо findViewById
□ RecyclerView с ListAdapter и DiffUtil для списков
□ Очищаем binding в onDestroyView для Fragment
□ Обновляем UI только на Main Thread
□ Не обращаемся к View до onViewCreated
□ Используем dp для размеров, sp для текста
□ Тестируем на разных размерах экрана
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "View System устарел, нужен только Compose" | View System будет поддерживаться много лет. Миллионы приложений его используют. Compose — альтернатива, не замена. Interop между ними работает отлично |
| "findViewById медленный" | findViewById O(n) по количеству Views, но в типичных layouts это ~10-50 Views. ViewBinding быстрее (generated code), но findViewById не bottleneck |
| "LinearLayout быстрее ConstraintLayout" | Для 2-3 Views — да. Для 5+ Views ConstraintLayout часто быстрее благодаря плоской иерархии. Nested LinearLayout хуже обоих |
| "RecyclerView всегда лучше ListView" | RecyclerView гибче и эффективнее для сложных layouts. Но для простых статичных списков из 5-10 элементов LinearLayout проще |
| "ViewBinding = DataBinding" | ViewBinding только генерирует type-safe references. DataBinding добавляет: binding expressions в XML, two-way binding, LiveData observing. ViewBinding проще и быстрее |
| "dp одинаков на всех экранах" | dp = density-independent pixel. Физический размер примерно одинаков (160dp ≈ 1 inch), но на разных density это разное количество pixels |
| "wrap_content дешёвый" | wrap_content требует измерения детей (или контента) чтобы определить размер. В сложных layouts может вызвать multiple measure passes |
| "View.post() безопасен для UI" | post() добавляет Runnable в message queue. Если View detached, Runnable всё равно выполнится и может крашнуть. Используйте lifecycleScope или проверяйте isAttachedToWindow |
| "setVisibility(GONE) = удаление" | GONE скрывает View и исключает из layout, но View остаётся в иерархии и памяти. Для полного удаления: parent.removeView(child) |
| "RecyclerView автоматически оптимален" | RecyclerView эффективен при правильном использовании: стабильные ID, DiffUtil, избегание notifyDataSetChanged(), правильный ViewHolder без allocations в onBindViewHolder |

---

## CS-фундамент

| CS-концепция | Применение в Android Views |
|--------------|---------------------------|
| **Composite Pattern** | ViewGroup — composite: содержит children Views. View — leaf. Одинаковый interface (measure, layout, draw) для обоих |
| **Observer Pattern** | OnClickListener, TextWatcher — observers. View — subject. setOnClickListener регистрирует observer |
| **Object Pool** | RecyclerView.RecycledViewPool — object pool для ViewHolders. Избегает allocation/GC overhead при scrolling |
| **Dirty Flag Pattern** | invalidate() устанавливает dirty flag. На следующем frame только dirty Views перерисовываются |
| **Layout Algorithm** | Measure pass: constraint propagation (parent → child). Layout pass: position assignment. Draw pass: rendering |
| **Density Independence** | dp абстрагирует physical pixels. Формула: px = dp × (dpi / 160). Separation of concerns: design vs hardware |
| **ViewHolder Pattern** | ViewHolder хранит references на child Views. findViewByI cached. Избегает повторных traversals |
| **Adapter Pattern** | RecyclerView.Adapter адаптирует data (List) к View representation (ViewHolder). Decoupling data и presentation |
| **Two-Phase Commit** | Measure phase = proposal (желаемые размеры). Layout phase = commit (фактические позиции). Separation для flexibility |
| **Message Queue** | View.post() добавляет Runnable в Looper message queue. Handler pattern для thread-safe UI updates |

---

## Связь с другими темами

### [[android-overview]]
View System — центральная часть UI-подсистемы Android, связанная практически со всеми аспектами платформы. Карта Android раздела показывает, как View System пересекается с lifecycle, threading, state management и navigation. Понимание общей архитектуры платформы помогает увидеть, почему View System спроектирован именно так и какие ограничения он накладывает. Начните с overview для контекста.

### [[android-activity-lifecycle]]
View существуют внутри Activity и Fragment, поэтому их lifecycle неразрывно связан. ViewBinding безопасно использовать только между onCreateView() и onDestroyView(), иначе — memory leaks или crashes. Понимание lifecycle критично для правильной работы с findViewById, ViewBinding и RecyclerView.Adapter. Без этого знания типичные ошибки: NullPointerException при обращении к View после onDestroyView() в Fragment.

### [[android-compose]]
Compose — современная декларативная UI-система, постепенно заменяющая View System. Понимание обеих систем важно: миллионы существующих приложений используют Views, а migration и interop (ComposeView, AndroidView) требуют знания обоих подходов. Compose устраняет многие проблемы View System (boilerplate, findViewById, XML parsing), но под капотом использует тот же rendering pipeline. Изучите View System для фундамента, затем Compose для нового кода.

### [[android-threading]]
View можно модифицировать только из Main Thread — нарушение этого правила приводит к CalledFromWrongThreadException. RecyclerView.Adapter.notifyDataSetChanged() и View.invalidate() должны вызываться из Main Thread. Корутины с Dispatchers.Main, View.post() и Handler решают эту проблему. Понимание threading критично для безопасной работы с UI.

---

## Источники

- [Layouts - Android Developers](https://developer.android.com/develop/ui/views/layout/declaring-layout) — официальная документация по layouts
- [View Binding - Android Developers](https://developer.android.com/topic/libraries/view-binding) — ViewBinding
- [RecyclerView - Android Developers](https://developer.android.com/develop/ui/views/layout/recyclerview) — RecyclerView и Adapter
- [ConstraintLayout - Android Developers](https://developer.android.com/develop/ui/views/layout/constraint-layout) — ConstraintLayout

## Источники и дальнейшее чтение

- **Phillips B. et al. (2022). Android Programming: The Big Nerd Ranch Guide.** — Лучшее пошаговое введение в View System: layouts, RecyclerView, ViewBinding, ConstraintLayout. Каждая глава строит реальное приложение, что помогает закрепить концепции на практике.
- **Meier R. (2022). Professional Android.** — Глубокое покрытие View hierarchy, custom views, RecyclerView optimization и integration с Architecture Components. Подходит для перехода от базового понимания к production-level знаниям.
- **Vasavada N. (2019). Android Internals.** — Внутреннее устройство LayoutInflater, View rendering pipeline и window system. Объясняет, как XML превращается в объекты View и как они размещаются на экране. Для тех, кто хочет понять «под капотом».

---

*Проверено: 2026-01-09 | Обновлено с 18 | На основе официальной документации Android*


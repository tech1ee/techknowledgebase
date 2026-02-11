---
title: "Custom Views: основы создания"
created: 2025-12-25
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [oop-inheritance, composition-pattern, coordinate-system, event-handling]
research: "[[2025-12-25-android-custom-views]]"
tags:
  - topic/android
  - topic/ui
  - type/deep-dive
  - level/advanced
related:
  - "[[android-ui-views]]"
  - "[[android-compose]]"
  - "[[android-view-measurement]]"
  - "[[android-canvas-drawing]]"
  - "[[android-touch-handling]]"
---

# Custom Views: основы создания

Custom View — это собственный UI-компонент, созданный расширением базового класса `View` или его наследников. Это единственный способ получить полный контроль над отрисовкой и обработкой взаимодействий, когда стандартные компоненты не подходят.

> **Prerequisites:**
> - [[android-ui-views]] — понимание View-иерархии Android
> - [[kotlin-basics]] — Kotlin синтаксис (особенно @JvmOverloads)
> - Базовое понимание жизненного цикла Android-компонентов

---

## Терминология

| Термин | Значение |
|--------|----------|
| **View** | Базовый класс всех UI-элементов в Android |
| **ViewGroup** | View, который может содержать дочерние View (контейнер) |
| **AttributeSet** | Коллекция XML-атрибутов, переданных View при создании |
| **Styleable** | Набор кастомных атрибутов, объявленных в attrs.xml |
| **TypedArray** | Массив типизированных значений атрибутов |
| **invalidate()** | Запрос перерисовки View (вызывает onDraw) |
| **requestLayout()** | Запрос пересчёта размеров и позиции View |
| **MeasureSpec** | Спецификация размера от родителя (mode + size) |

---

## ПОЧЕМУ: Когда нужен Custom View

### Проблема: ограничения стандартных компонентов

Стандартные View покрывают 90% случаев. Но иногда нужно:

```kotlin
// Хотим круговой прогресс с кастомной анимацией
// ProgressBar не даёт достаточно контроля

// Хотим график с интерактивными точками
// Нет готового компонента в SDK

// Хотим уникальный slider с несколькими thumb
// SeekBar поддерживает только один
```

### Когда создавать Custom View

| Ситуация | Решение |
|----------|---------|
| Уникальная визуализация (графики, диаграммы) | Custom View |
| Сложная интерактивность (жесты, multi-touch) | Custom View |
| Переиспользуемый компонент с особой логикой | Custom View |
| Простая кастомизация цвета/размера | Стандартный View + стили |
| Новый проект на Compose | Compose Canvas |
| Комбинация существующих View | Compound View (ViewGroup) |

### Аналогия: Конструктор vs Скульптура

> **Стандартные View** — это конструктор LEGO. Собираешь из готовых блоков.
> **Custom View** — это скульптура. Лепишь из глины что угодно, но нужно понимать анатомию.

**Compound View** (ViewGroup с детьми) — промежуточный вариант: группируешь блоки LEGO в новый переиспользуемый блок.

---

## ЧТО: Анатомия Custom View

### Четыре конструктора View

Android View имеет 4 конструктора, каждый добавляет параметр:

```kotlin
// 1. Для создания из кода
View(context: Context)

// 2. ОБЯЗАТЕЛЬНЫЙ для XML inflation — без него View не создастся из layout
View(context: Context, attrs: AttributeSet?)

// 3. Для применения стиля из темы
View(context: Context, attrs: AttributeSet?, defStyleAttr: Int)

// 4. API 21+ — fallback стиль, если нет в теме
View(context: Context, attrs: AttributeSet?, defStyleAttr: Int, defStyleRes: Int)
```

**Правило:** Второй конструктор обязателен. Без него XML-парсер не сможет создать View.

### Kotlin-решение: @JvmOverloads

```kotlin
// ПРАВИЛЬНО: @JvmOverloads генерирует все 3 конструктора
class CircularProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,        // Для XML inflation
    defStyleAttr: Int = 0               // Для theming
) : View(context, attrs, defStyleAttr) {

    init {
        // Инициализация: чтение атрибутов, создание Paint и т.д.
    }
}
```

**Почему @JvmOverloads работает:**
- Kotlin генерирует 3 Java-конструктора из одного
- XML inflater находит конструктор с `(Context, AttributeSet)`
- Программное создание использует `(Context)`

### defStyleAttr vs defStyleRes — приоритет атрибутов

Когда View читает атрибут (например, цвет), Android ищет значение в таком порядке:

```
1. XML-атрибут в layout         ← Высший приоритет
   android:background="@color/red"

2. style="" в XML
   style="@style/MyViewStyle"

3. defStyleAttr (из темы)
   <item name="circularProgressStyle">@style/Widget.CircularProgress</item>

4. defStyleRes (fallback)
   R.style.Widget_CircularProgress_Default

5. Базовые значения темы        ← Низший приоритет
```

### Жизненный цикл View

```
┌─────────────────────────────────────────────────────────────────┐
│                     LIFECYCLE ПОРЯДОК                            │
├─────────────────────────────────────────────────────────────────┤
│  Constructor                                                     │
│       ↓                                                          │
│  onFinishInflate()     ← Все дети из XML созданы                │
│       ↓                                                          │
│  onAttachedToWindow()  ← View добавлен в window                 │
│       ↓                                                          │
│  onMeasure()           ← Определение размера                    │
│       ↓                                                          │
│  onSizeChanged()       ← Размер изменился (первый раз или потом)│
│       ↓                                                          │
│  onLayout()            ← Позиционирование (для ViewGroup)       │
│       ↓                                                          │
│  onDraw()              ← Отрисовка на Canvas                    │
│       ↓                                                          │
│  [Взаимодействие пользователя: touch, keyboard]                 │
│       ↓                                                          │
│  onDetachedFromWindow() ← View удалён из window                 │
└─────────────────────────────────────────────────────────────────┘
```

### Ключевые callbacks

```kotlin
class CircularProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var animator: ValueAnimator? = null

    // ═══════════════════════════════════════════════════════════════
    // onAttachedToWindow: View добавлен в иерархию
    // ЗДЕСЬ: подписки, старт анимаций, регистрация listeners
    // ═══════════════════════════════════════════════════════════════
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        startAnimation()
    }

    // ═══════════════════════════════════════════════════════════════
    // onDetachedFromWindow: View удалён из иерархии
    // КРИТИЧЕСКИ ВАЖНО: очистка ресурсов, отмена анимаций, отписки
    // Без этого — MEMORY LEAK
    // ═══════════════════════════════════════════════════════════════
    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
        animator = null
    }

    // ═══════════════════════════════════════════════════════════════
    // onSizeChanged: размер View изменился
    // ЗДЕСЬ: пересчёт зависимых от размера значений (центр, радиус)
    // ═══════════════════════════════════════════════════════════════
    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        centerX = w / 2f
        centerY = h / 2f
        radius = minOf(w, h) / 2f - strokeWidth
    }
}
```

### invalidate() vs requestLayout()

| Метод | Что вызывает | Когда использовать | Стоимость |
|-------|-------------|-------------------|-----------|
| `invalidate()` | Только `onDraw()` | Изменился цвет, прогресс, визуальное состояние | Дёшево |
| `requestLayout()` | `onMeasure()` + `onLayout()` + `onDraw()` | Изменился размер контента | Дорого |

**Аналогия:**
> `invalidate()` — перекрасить комнату (стены на месте)
> `requestLayout()` — перепланировка квартиры (ломаем стены, меряем заново)

```kotlin
var progress: Float = 0f
    set(value) {
        field = value.coerceIn(0f, 1f)
        invalidate()  // Только перерисовка — размер не меняется
    }

var strokeWidth: Float = 10f
    set(value) {
        field = value
        requestLayout()  // Толщина линии влияет на intrinsic size
    }
```

**ВАЖНО:** `requestLayout()` проходит ВСЮ иерархию View — от вашего View до корня. Это дорого. Избегайте частых вызовов.

---

## КАК: Практическая реализация

### Шаг 1: Объявление styleable атрибутов

`res/values/attrs.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Объявляем набор атрибутов для нашего View -->
    <declare-styleable name="CircularProgressView">
        <!-- format указывает тип значения -->
        <attr name="cpv_progress" format="float" />
        <attr name="cpv_progressColor" format="color" />
        <attr name="cpv_trackColor" format="color" />
        <attr name="cpv_strokeWidth" format="dimension" />
        <attr name="cpv_animationDuration" format="integer" />
    </declare-styleable>
</resources>
```

**Префикс `cpv_`** — конвенция для избежания конфликтов с другими библиотеками.

### Шаг 2: Чтение атрибутов в конструкторе

```kotlin
class CircularProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // Paint-объекты создаём ОДИН раз в конструкторе, не в onDraw()
    private val trackPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG)

    // Значения по умолчанию
    private var progressColor: Int = Color.BLUE
    private var trackColor: Int = Color.LTGRAY
    private var strokeWidth: Float = 10f.dpToPx()

    var progress: Float = 0f
        set(value) {
            field = value.coerceIn(0f, 1f)
            invalidate()
        }

    init {
        // ═══════════════════════════════════════════════════════════════
        // КРИТИЧЕСКИ ВАЖНО: TypedArray MUST be recycled
        // Без recycle() — memory leak, объект остаётся в пуле
        // ═══════════════════════════════════════════════════════════════
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.CircularProgressView,
            defStyleAttr,
            0  // defStyleRes — fallback стиль
        ).apply {
            try {
                // getColor, getDimension, getFloat — читаем типизированные значения
                progressColor = getColor(
                    R.styleable.CircularProgressView_cpv_progressColor,
                    Color.BLUE  // default, если атрибут не задан
                )
                trackColor = getColor(
                    R.styleable.CircularProgressView_cpv_trackColor,
                    Color.LTGRAY
                )
                strokeWidth = getDimension(
                    R.styleable.CircularProgressView_cpv_strokeWidth,
                    10f.dpToPx()
                )
                progress = getFloat(
                    R.styleable.CircularProgressView_cpv_progress,
                    0f
                )
            } finally {
                // ОБЯЗАТЕЛЬНО! Без этого — утечка памяти
                recycle()
            }
        }

        // Настраиваем Paint после чтения атрибутов
        setupPaints()
    }

    private fun setupPaints() {
        trackPaint.apply {
            style = Paint.Style.STROKE
            strokeWidth = this@CircularProgressView.strokeWidth
            color = trackColor
            strokeCap = Paint.Cap.ROUND
        }

        progressPaint.apply {
            style = Paint.Style.STROKE
            strokeWidth = this@CircularProgressView.strokeWidth
            color = progressColor
            strokeCap = Paint.Cap.ROUND
        }
    }

    // Extension для конвертации dp в px
    private fun Float.dpToPx(): Float =
        this * resources.displayMetrics.density
}
```

### Шаг 3: Измерение (onMeasure)

```kotlin
// ═══════════════════════════════════════════════════════════════
// onMeasure: определяем размер View
// ПРАВИЛО: ВСЕГДА вызывать setMeasuredDimension() в конце
// ═══════════════════════════════════════════════════════════════
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // MeasureSpec содержит mode и size от родителя
    val desiredSize = (100f.dpToPx() + strokeWidth * 2).toInt()

    val width = resolveSize(desiredSize, widthMeasureSpec)
    val height = resolveSize(desiredSize, heightMeasureSpec)

    // Для круга берём минимальный размер
    val size = minOf(width, height)

    // ОБЯЗАТЕЛЬНО вызвать — иначе IllegalStateException
    setMeasuredDimension(size, size)
}

// ═══════════════════════════════════════════════════════════════
// MeasureSpec режимы:
// EXACTLY   — родитель указал точный размер (match_parent или 100dp)
// AT_MOST   — максимальный размер (wrap_content)
// UNSPECIFIED — нет ограничений (ScrollView)
// ═══════════════════════════════════════════════════════════════
private fun resolveSizeManual(desiredSize: Int, measureSpec: Int): Int {
    val mode = MeasureSpec.getMode(measureSpec)
    val size = MeasureSpec.getSize(measureSpec)

    return when (mode) {
        MeasureSpec.EXACTLY -> size                       // Точный размер от родителя
        MeasureSpec.AT_MOST -> minOf(desiredSize, size)   // Не больше родителя
        else -> desiredSize                               // Желаемый размер
    }
}
```

### Шаг 4: Отрисовка (onDraw)

```kotlin
// Создаём RectF ОДИН раз, переиспользуем
private val arcRect = RectF()
private var centerX = 0f
private var centerY = 0f
private var radius = 0f

override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
    super.onSizeChanged(w, h, oldw, oldh)

    // Пересчитываем при изменении размера
    centerX = w / 2f
    centerY = h / 2f
    radius = minOf(w, h) / 2f - strokeWidth / 2f

    // Обновляем RectF для drawArc
    arcRect.set(
        centerX - radius,
        centerY - radius,
        centerX + radius,
        centerY + radius
    )
}

// ═══════════════════════════════════════════════════════════════
// onDraw: отрисовка на Canvas
// КРИТИЧЕСКИ ВАЖНО: НЕ создавать объекты здесь!
// Вызывается 60 раз/сек при анимации — allocations = jank
// ═══════════════════════════════════════════════════════════════
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Фоновая дорожка (полный круг)
    canvas.drawCircle(centerX, centerY, radius, trackPaint)

    // Прогресс (дуга)
    // startAngle: -90 = 12 часов
    // sweepAngle: угол дуги (progress * 360)
    val sweepAngle = progress * 360f
    canvas.drawArc(
        arcRect,
        -90f,           // Начинаем сверху
        sweepAngle,     // Угол заполнения
        false,          // useCenter = false для дуги
        progressPaint
    )
}
```

### Шаг 5: Использование в XML

`res/layout/activity_main.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Полное имя класса с пакетом -->
    <com.example.views.CircularProgressView
        android:id="@+id/progressView"
        android:layout_width="100dp"
        android:layout_height="100dp"
        app:cpv_progress="0.75"
        app:cpv_progressColor="@color/primary"
        app:cpv_trackColor="@color/surface_variant"
        app:cpv_strokeWidth="8dp" />

</LinearLayout>
```

### Шаг 6: Программное управление

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var progressView: CircularProgressView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        progressView = findViewById(R.id.progressView)

        // Анимация прогресса
        ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 2000
            interpolator = DecelerateInterpolator()
            addUpdateListener { animator ->
                progressView.progress = animator.animatedValue as Float
            }
            start()
        }
    }
}
```

---

## КАК: Accessibility

### Минимальные требования для TalkBack

```kotlin
class CircularProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    init {
        // Указываем, что View представляет прогресс
        ViewCompat.setAccessibilityDelegate(this, object : AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                // Тип контента для screen reader
                info.className = "android.widget.ProgressBar"
                // Информация о прогрессе
                info.contentDescription = "Прогресс: ${(progress * 100).toInt()}%"
            }
        })
    }

    var progress: Float = 0f
        set(value) {
            field = value.coerceIn(0f, 1f)
            invalidate()
            // ═══════════════════════════════════════════════════════════════
            // ВАЖНО: уведомляем accessibility services об изменении
            // Без этого TalkBack не узнает о новом значении
            // ═══════════════════════════════════════════════════════════════
            announceForAccessibility("Прогресс: ${(progress * 100).toInt()}%")
        }
}
```

### Обработка кликов с accessibility

```kotlin
// Если View кликабельный
init {
    isClickable = true
    isFocusable = true  // Для keyboard navigation
}

// ═══════════════════════════════════════════════════════════════
// ОБЯЗАТЕЛЬНО: переопределить performClick для accessibility
// Accessibility services вызывают performClick, не onTouchEvent
// ═══════════════════════════════════════════════════════════════
override fun performClick(): Boolean {
    super.performClick()  // ОБЯЗАТЕЛЬНО вызвать super
    // Логика клика
    toggleState()
    return true
}

override fun onTouchEvent(event: MotionEvent): Boolean {
    if (event.action == MotionEvent.ACTION_UP) {
        performClick()  // Делегируем в performClick
    }
    return super.onTouchEvent(event)
}
```

---

## КАК: Избежать Memory Leaks

### Типичные ошибки и исправления

```kotlin
class LeakyView(context: Context) : View(context) {

    // ❌ ПЛОХО: Handler держит ссылку на View
    private val handler = Handler(Looper.getMainLooper())

    // ❌ ПЛОХО: Anonymous class держит ссылку на outer View
    private val runnable = Runnable {
        // Если View уничтожен, а runnable ещё в очереди —
        // View не соберётся GC
        invalidate()
    }

    fun startUpdates() {
        handler.postDelayed(runnable, 1000)
    }

    // ❌ ПЛОХО: не очищаем в onDetachedFromWindow
}

// ═══════════════════════════════════════════════════════════════
// ПРАВИЛЬНАЯ РЕАЛИЗАЦИЯ
// ═══════════════════════════════════════════════════════════════
class SafeView(context: Context) : View(context) {

    private val handler = Handler(Looper.getMainLooper())
    private var animator: ValueAnimator? = null

    // Runnable как val, чтобы иметь ссылку для удаления
    private val updateRunnable = Runnable {
        // Проверяем, что View ещё attached
        if (isAttachedToWindow) {
            invalidate()
            handler.postDelayed(updateRunnable, 1000)
        }
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        handler.post(updateRunnable)
        animator?.start()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // ✅ КРИТИЧЕСКИ ВАЖНО: очищаем ВСЕ ресурсы
        handler.removeCallbacksAndMessages(null)
        animator?.cancel()
        animator = null
    }
}
```

### Чеклист безопасности

- [ ] `TypedArray.recycle()` вызван в finally
- [ ] `Handler.removeCallbacksAndMessages(null)` в onDetachedFromWindow
- [ ] `Animator.cancel()` в onDetachedFromWindow
- [ ] Нет static ссылок на View
- [ ] Listeners отписаны в onDetachedFromWindow
- [ ] Нет allocations в onDraw()

---

## КОГДА НЕ использовать Custom View

### 1. Compose Canvas — для новых проектов

```kotlin
// Compose: тот же circular progress в 20 строк вместо 200
@Composable
fun CircularProgress(
    progress: Float,
    modifier: Modifier = Modifier,
    color: Color = MaterialTheme.colorScheme.primary,
    trackColor: Color = MaterialTheme.colorScheme.surfaceVariant
) {
    Canvas(modifier = modifier.size(100.dp)) {
        val strokeWidth = 8.dp.toPx()
        val radius = size.minDimension / 2 - strokeWidth / 2

        // Track
        drawCircle(
            color = trackColor,
            radius = radius,
            style = Stroke(strokeWidth)
        )

        // Progress
        drawArc(
            color = color,
            startAngle = -90f,
            sweepAngle = progress * 360f,
            useCenter = false,
            style = Stroke(strokeWidth, cap = StrokeCap.Round)
        )
    }
}
```

**Преимущества Compose Canvas:**
- Меньше boilerplate (нет конструкторов, attrs)
- Встроенная accessibility через semantics {}
- Автоматическое управление lifecycle
- Preview в Android Studio

### 2. Compound View — для комбинации существующих

Если нужно объединить несколько стандартных View:

```kotlin
// Вместо custom View с нуля
class LabeledSwitch @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : LinearLayout(context, attrs) {

    private val label: TextView
    private val switch: SwitchCompat

    init {
        orientation = HORIZONTAL
        inflate(context, R.layout.labeled_switch, this)

        label = findViewById(R.id.label)
        switch = findViewById(R.id.switch_view)
    }
}
```

### 3. Shape Drawable — для простой графики

```xml
<!-- Вместо custom View для простого круга -->
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="oval">
    <solid android:color="@color/primary" />
    <size android:width="100dp" android:height="100dp" />
</shape>
```

### Таблица выбора

| Задача | Решение |
|--------|---------|
| Уникальная графика с анимацией | Custom View |
| Сложные жесты (pinch, swipe) | Custom View |
| Переиспользование в legacy-проекте | Custom View |
| Новый проект на Compose | Compose Canvas |
| Комбинация TextView + Button + Image | Compound View |
| Простые фигуры (круги, прямоугольники) | Shape Drawable |
| Кастомный фон | Layer-list Drawable |

---

## Проверь себя

1. **Какой конструктор ОБЯЗАТЕЛЕН для создания View из XML?**
   - `View(Context, AttributeSet)` — XML inflater ищет именно его

2. **Когда вызывать invalidate(), а когда requestLayout()?**
   - `invalidate()` — только визуальные изменения (цвет, прогресс)
   - `requestLayout()` — изменения размера (содержимое, толщина линии)

3. **Почему важно вызывать TypedArray.recycle()?**
   - TypedArray берётся из пула, без recycle() — memory leak

4. **Что будет, если не очистить Handler в onDetachedFromWindow?**
   - Memory leak: Handler держит ссылку на View через Runnable

5. **Почему нельзя создавать объекты в onDraw()?**
   - onDraw() вызывается 60 раз/сек, allocations = GC = jank (frame drops)

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Нужен только конструктор с Context" | Для XML inflation нужен конструктор с AttributeSet. @JvmOverloads помогает, но понимание 4 конструкторов важно для правильной стилизации |
| "Custom View всегда лучше готовых" | Custom View требует: implementation, testing, maintenance, accessibility. Для простых задач — compound views или Drawables эффективнее |
| "onDraw() вызывается редко" | onDraw() может вызываться 60-120 раз/сек при анимациях и скролле. Любые allocations в onDraw = GC pressure = jank |
| "invalidate() = немедленная перерисовка" | invalidate() помечает View dirty. Перерисовка происходит на следующем VSYNC (~16ms). Можно вызвать invalidate() 100 раз — будет 1 redraw |
| "requestLayout() только для размеров" | requestLayout() триггерит measure + layout для View И всех ancestors. Дорогая операция, особенно в глубоких иерархиях |
| "Можно игнорировать onAttach/onDetach" | onAttachedToWindow/onDetachedFromWindow — критичны для: listener registration, animator start/stop, resource cleanup. Иначе — memory leaks |
| "TypedArray.recycle() опционален" | TypedArray из пула объектов. Без recycle() — объект не возвращается в пул → постепенно растёт memory usage |
| "Accessibility — опционально" | Accessibility обязателен по закону во многих странах. contentDescription, focusable, accessibilityDelegate должны быть настроены |
| "Hardware Layer бесплатный" | Hardware Layer = GPU texture = видеопамять (width × height × 4 bytes). На full-screen View это 8+ MB. Используйте только для сложных animations |
| "Canvas.save()/restore() не нужны" | save()/restore() критичны для изоляции transformations. Без них rotate/translate/scale влияют на ВСЁ последующее рисование |

---

## CS-фундамент

| CS-концепция | Применение в Custom Views |
|--------------|--------------------------|
| **Template Method Pattern** | onMeasure(), onLayout(), onDraw() — template methods. Subclasses override для custom behavior. Framework вызывает в определённом порядке |
| **State Machine** | View имеет state: pressed, focused, selected, enabled. setPressed()/setSelected() меняют state. Drawable state list реагирует на изменения |
| **Object Pool** | TypedArray использует object pool. obtainStyledAttributes() берёт из пула, recycle() возвращает. Избегает allocations |
| **Decorator Pattern** | Paint decorates drawing operations: color, style, shader, path effects. Один Paint может применяться к разным shapes |
| **Command Pattern** | Canvas operations (drawRect, drawPath) — commands. Hardware acceleration записывает их в Display List для deferred execution |
| **Coordinate Transformation** | Canvas.translate/rotate/scale — affine transformations. Matrix multiplication под капотом. save()/restore() stack для isolation |
| **Retained Mode vs Immediate Mode** | Canvas — immediate mode (draw now). Display List — retained mode (record, replay). HW acceleration использует оба |
| **Lifecycle Management** | onAttach → measuring → layout → draw → onDetach. Resources acquired в onAttach, released в onDetach. RAII-like pattern |
| **Invalidation Protocol** | invalidate() = "я изменился визуально". requestLayout() = "мой размер изменился". Framework batches и optimizes updates |
| **Accessibility Tree** | AccessibilityNodeInfo формирует дерево для screen readers. Custom Views должны предоставлять: role, name, value, actions |

---

## Связанные материалы

| Материал | Зачем изучать |
|----------|---------------|
| [[android-view-measurement]] | Глубже про onMeasure, MeasureSpec, кастомные ViewGroup |
| [[android-canvas-drawing]] | Canvas API: paths, gradients, shaders, hardware acceleration |
| [[android-touch-handling]] | onTouchEvent, GestureDetector, multi-touch |
| [[android-compose]] | Современная альтернатива — Compose Canvas |
| [[android-ui-views]] | View hierarchy, layout inflation, основы |

---

## Источники

| Источник | Тип | Вклад |
|----------|-----|-------|
| [Create a view class - Android Developers](https://developer.android.com/develop/ui/views/layout/custom-views/create-view) | Official | Constructors, AttributeSet |
| [Deep dive into View constructors - Dan Lew](https://blog.danlew.net/2016/07/19/a-deep-dive-into-android-view-constructors/) | Expert Blog | defStyleAttr vs defStyleRes |
| [View Lifecycle - ProAndroidDev](https://proandroiddev.com/the-life-cycle-of-a-view-in-android-6a2c4665b95e) | Technical | Lifecycle order |
| [Optimize custom view - Android Developers](https://developer.android.com/develop/ui/views/layout/custom-views/optimizing-view) | Official | Performance optimization |
| [Make custom views accessible - Android Developers](https://developer.android.com/guide/topics/ui/accessibility/custom-views) | Official | Accessibility requirements |
| [Android leak pattern: subscriptions in views - Square](https://developer.squareup.com/blog/android-leak-pattern-subscriptions-in-views/) | Expert Blog | Memory leak patterns |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

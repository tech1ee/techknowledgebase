---
title: "Конвейер рендеринга View в Android"
created: 2025-12-25
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [rendering-pipeline, gpu-acceleration, vsync, double-buffering]
tags:
  - topic/android
  - topic/rendering
  - topic/performance
  - type/deep-dive
  - level/advanced
related:
  - "[[android-compose-internals]]"
  - "[[android-performance-profiling]]"
  - "[[android-ui-views]]"
  - "[[android-graphics-apis]]"
  - "[[android-animations]]"
  - "[[android-window-system]]"
prerequisites:
  - "[[android-ui-views]]"
  - "[[android-activity-lifecycle]]"
---

# Android View Rendering Pipeline

## Терминология

| Термин | Значение |
|--------|----------|
| **VSYNC** | Vertical Synchronization — сигнал синхронизации с частотой обновления дисплея |
| **Choreographer** | Системный компонент, координирующий рендеринг по VSYNC |
| **RenderThread** | Отдельный поток для отправки команд на GPU |
| **Display List** | Закэшированный список команд рисования View |
| **Hardware Layer** | Кэш View в виде GPU текстуры |
| **Overdraw** | Многократное рисование одного пикселя за кадр |
| **Jank** | Пропуск кадров, вызывающий заикания UI |
| **Frame Budget** | Время на рендеринг одного кадра (16.67ms при 60Hz) |

---

## ПОЧЕМУ: Зачем понимать Rendering Pipeline

### Проблемы без понимания

```kotlin
// Почему UI "дёргается"?
// Почему анимация не плавная?
// Почему скролл тормозит?
// Почему батарея быстро садится?
```

### Когда знания критичны

| Сценарий | Почему важно |
|----------|--------------|
| Сложные анимации | Hardware layers vs software rendering |
| Custom Views | Правильный onDraw(), избежание allocations |
| RecyclerView с медиа | Bitmap loading, overdraw |
| Игры/графика | Frame pacing, GPU utilization |
| Отладка jank | Profile GPU Rendering, Perfetto |

### Аналогия: Конвейер на заводе

```
Заказ (Input) → Проектирование (Measure/Layout) → Сборка (Draw) →
→ Упаковка (Sync) → Доставка (GPU) → Витрина (Display)

Если любой этап задерживается > 16ms — клиент не получает товар вовремя
```

---

## ЧТО: Как работает Rendering Pipeline

### Общая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                          VSYNC Signal                            │
│                         (каждые 16.67ms)                         │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Choreographer                            │
│              "Дирижёр" — координирует всё по VSYNC               │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                          UI Thread                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Input   │→ │Animation │→ │ Measure/ │→ │   Draw   │        │
│  │ Handling │  │          │  │  Layout  │  │(Display  │        │
│  │          │  │          │  │          │  │  Lists)  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                        RenderThread                              │
│  ┌────────────┐  ┌────────────────┐  ┌──────────────┐          │
│  │Sync/Upload │→ │ Issue Commands │→ │ Swap Buffers │          │
│  │ (Bitmaps)  │  │   (OpenGL ES)  │  │              │          │
│  └────────────┘  └────────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                             GPU                                  │
│                    Rasterization → Pixels                        │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                        SurfaceFlinger                            │
│              Композитинг всех Surface → Display                  │
└─────────────────────────────────────────────────────────────────┘
```

### Frame Budget

| Refresh Rate | Frame Budget | Типичные устройства |
|--------------|--------------|---------------------|
| 60 Hz | 16.67 ms | Большинство устройств |
| 90 Hz | 11.11 ms | OnePlus, некоторые Samsung |
| 120 Hz | 8.33 ms | Flagship 2023+ |

**Реальность:** Приложению доступно ~10-12ms, остальное — системные процессы.

### Pipeline Stages в деталях

#### 1. Input Handling (Orange)

```kotlin
// Обработка touch событий
override fun onTouchEvent(event: MotionEvent): Boolean {
    // Этот код выполняется в Input Handling фазе
    when (event.action) {
        MotionEvent.ACTION_DOWN -> startDrag()
        MotionEvent.ACTION_MOVE -> updatePosition()
    }
    return true
}
```

**Проблема:** RecyclerView inflate views при scroll → высокий Input bar.

#### 2. Animation (Red)

```kotlin
// ObjectAnimator, ViewPropertyAnimator, Transition
view.animate()
    .translationX(100f)
    .setDuration(300)
    .start()

// Каждый кадр: вычисление текущего значения анимации
```

**Проблема:** Много одновременных анимаций → высокий Animation bar.

#### 3. Measure/Layout (Yellow)

```kotlin
// Traversal: measure → layout для изменённых View
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Вычисление размеров
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    // Позиционирование детей
}
```

**Проблемы:**
- Глубокая иерархия → exponential passes
- Double taxation (RelativeLayout внутри RelativeLayout)
- `requestLayout()` во время layout

#### 4. Draw (Green)

```kotlin
override fun onDraw(canvas: Canvas) {
    // Команды рисования → Display List
    canvas.drawRect(rect, paint)
    canvas.drawText(text, x, y, textPaint)
}
```

**Проблемы:**
- Allocations в onDraw() → GC pauses
- Сложная логика → долгое создание Display List
- Частые invalidate() → постоянное пересоздание

#### 5. Sync/Upload (Purple)

```kotlin
// Загрузка bitmap из CPU памяти в GPU
imageView.setImageBitmap(largeBitmap)

// Bitmap 4096x4096 = 64MB → долгая загрузка на GPU
```

**Решение:** `prepareToDraw()` для предзагрузки.

#### 6. Issue Commands (Dark Blue)

```kotlin
// НЕЭФФЕКТИВНО — много draw calls
for (i in 0 until 1000) {
    canvas.drawPoint(points[i].x, points[i].y, paint)
}

// ЭФФЕКТИВНО — один draw call
canvas.drawPoints(pointsArray, paint)
```

#### 7. Swap Buffers (Light Green)

GPU работает параллельно с CPU. Высокий Swap Buffers = GPU перегружен.

---

## КАК: Практические оптимизации

### 1. Оптимизация onDraw()

```kotlin
class OptimizedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    // ✅ Создаём объекты ОДИН раз
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    private val rect = RectF()
    private val path = Path()

    // ❌ НИКОГДА не делайте так
    // private fun createPaint() = Paint()  // allocation каждый вызов

    override fun onDraw(canvas: Canvas) {
        // ✅ Переиспользуем объекты
        rect.set(0f, 0f, width.toFloat(), height.toFloat())
        canvas.drawRect(rect, paint)

        // ✅ clipRect для оптимизации
        canvas.save()
        canvas.clipRect(dirtyRect)
        // Рисуем только в dirty области
        canvas.restore()
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        // ✅ Пересчитываем path при изменении размера, не в onDraw
        path.reset()
        path.addRoundRect(rect, cornerRadius, cornerRadius, Path.Direction.CW)
    }
}
```

### 2. Hardware Layers для анимаций

```kotlin
class AnimatedCard(context: Context) : CardView(context) {

    fun animateFlip() {
        // ✅ Включаем hardware layer ДО анимации
        setLayerType(LAYER_TYPE_HARDWARE, null)

        animate()
            .rotationY(180f)
            .setDuration(300)
            .withEndAction {
                // ✅ ОБЯЗАТЕЛЬНО отключаем после анимации
                setLayerType(LAYER_TYPE_NONE, null)
            }
            .start()
    }

    // Альтернатива с withLayer() (API 16+)
    fun animateSlide() {
        animate()
            .translationX(200f)
            .withLayer()  // Автоматически вкл/выкл hardware layer
            .start()
    }
}

// Когда hardware layer помогает:
// ✅ translation, rotation, scale, alpha анимации
// ✅ View не изменяется во время анимации

// Когда НЕ помогает (и вредит):
// ❌ View часто invalidate() во время анимации
// ❌ Очень большие View (много GPU памяти)
// ❌ Забыли отключить после анимации
```

### 3. Уменьшение Overdraw

```kotlin
// Проверка: Settings → Developer Options → Debug GPU Overdraw

// ❌ ПЛОХО — три слоя background
<LinearLayout android:background="@color/white">      <!-- 1x -->
    <FrameLayout android:background="@color/white">   <!-- 2x -->
        <TextView android:background="@color/white"/> <!-- 3x -->
    </FrameLayout>
</LinearLayout>

// ✅ ХОРОШО — один background
<LinearLayout android:background="@color/white">
    <FrameLayout>  <!-- no background -->
        <TextView/>  <!-- no background -->
    </FrameLayout>
</LinearLayout>
```

```kotlin
// В Activity — убираем window background если есть свой
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Если layout уже имеет background
    window.setBackgroundDrawable(null)
}
```

```xml
<!-- Или в теме -->
<style name="AppTheme" parent="Theme.Material3.Light">
    <item name="android:windowBackground">@null</item>
</style>
```

### 4. Flat View Hierarchy

```xml
<!-- ❌ ПЛОХО — глубокая иерархия -->
<LinearLayout>
    <LinearLayout>
        <RelativeLayout>
            <FrameLayout>
                <TextView/>
            </FrameLayout>
        </RelativeLayout>
    </LinearLayout>
</LinearLayout>

<!-- ✅ ХОРОШО — ConstraintLayout -->
<androidx.constraintlayout.widget.ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"/>
</androidx.constraintlayout.widget.ConstraintLayout>
```

```xml
<!-- ✅ merge для include -->
<!-- reusable_header.xml -->
<merge xmlns:android="http://schemas.android.com/apk/res/android">
    <ImageView android:id="@+id/icon"/>
    <TextView android:id="@+id/title"/>
</merge>

<!-- Использование -->
<ConstraintLayout>
    <include layout="@layout/reusable_header"/>
</ConstraintLayout>
```

### 5. Правильный invalidate()

```kotlin
class ProgressView(context: Context) : View(context) {

    var progress: Float = 0f
        set(value) {
            if (field != value) {
                field = value
                // ✅ Инвалидируем только изменённую область
                invalidate(progressRect)
                // Или полностью, если нужно
                // invalidate()
            }
        }

    // ❌ НЕ вызывайте requestLayout() если размер не меняется
    // requestLayout() → measure + layout + draw (дорого!)

    // ✅ invalidate() → только draw (дёшево)
}
```

### 6. Bitmap оптимизация

```kotlin
// ❌ ПЛОХО — загружаем 4096x4096 для 100x100 ImageView
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.huge_image)

// ✅ ХОРОШО — масштабируем при загрузке
fun decodeSampledBitmap(
    res: Resources,
    resId: Int,
    reqWidth: Int,
    reqHeight: Int
): Bitmap {
    val options = BitmapFactory.Options().apply {
        inJustDecodeBounds = true
    }
    BitmapFactory.decodeResource(res, resId, options)

    options.inSampleSize = calculateInSampleSize(options, reqWidth, reqHeight)
    options.inJustDecodeBounds = false

    return BitmapFactory.decodeResource(res, resId, options)
}

// ✅ ЛУЧШЕ — используйте Glide/Coil
Glide.with(context)
    .load(imageUrl)
    .override(100, 100)  // Автоматическое масштабирование
    .into(imageView)
```

### 7. prepareToDraw() для предзагрузки

```kotlin
// Bitmap загружается на GPU при первом draw
// Это может вызвать jank

// ✅ Предзагрузка до показа
bitmap.prepareToDraw()

// Или для Drawable
drawable.callback = object : Drawable.Callback {
    override fun invalidateDrawable(who: Drawable) {}
    override fun scheduleDrawable(who: Drawable, what: Runnable, `when`: Long) {}
    override fun unscheduleDrawable(who: Drawable, what: Runnable) {}
}
(drawable as? BitmapDrawable)?.bitmap?.prepareToDraw()
```

### 8. RecyclerView оптимизации

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<ViewHolder>() {

    init {
        // ✅ Стабильные ID для эффективного diff
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long {
        return items[position].id
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // ❌ НЕ вызывайте requestLayout() здесь
        // ❌ НЕ загружайте большие bitmap синхронно

        // ✅ Используйте Glide/Coil для изображений
        Glide.with(holder.itemView)
            .load(items[position].imageUrl)
            .into(holder.imageView)
    }
}

// В Activity/Fragment
recyclerView.apply {
    // ✅ Фиксированный размер если возможно
    setHasFixedSize(true)

    // ✅ Prefetch для плавного скролла
    layoutManager = LinearLayoutManager(context).apply {
        initialPrefetchItemCount = 4
    }

    // ✅ View pool для разных типов
    recycledViewPool.setMaxRecycledViews(VIEW_TYPE_IMAGE, 10)
}
```

---

## Инструменты диагностики

### Profile GPU Rendering

```
Settings → Developer Options → Profile GPU Rendering → On screen as bars
```

| Цвет | Стадия | Что проверять |
|------|--------|---------------|
| Orange | Input | Touch handlers, RecyclerView scroll |
| Red | Animation | Количество анимаций |
| Yellow | Measure/Layout | View hierarchy depth |
| Green | Draw | onDraw() complexity |
| Purple | Sync/Upload | Bitmap sizes |
| Dark Blue | Issue Commands | Draw call count |
| Light Green | Swap Buffers | GPU load |

**Зелёная линия = 16ms.** Всё выше — потенциальный jank.

### Debug GPU Overdraw

```
Settings → Developer Options → Debug GPU Overdraw → Show overdraw areas
```

| Цвет | Overdraw | Действие |
|------|----------|----------|
| True color | 0x | Идеально |
| Blue | 1x | Нормально |
| Green | 2x | Стоит оптимизировать |
| Pink | 3x | Нужно оптимизировать |
| Red | 4x+ | Критично |

### Layout Inspector

Android Studio → Tools → Layout Inspector

- Визуализация view hierarchy
- Поиск лишних слоёв
- Проверка overdraw

### Perfetto / Systrace

```bash
# Capture systrace
python systrace.py -o trace.html sched freq idle am wm gfx view

# Или через Android Studio
Profiler → CPU → System Trace
```

Что искать в trace:
- `Choreographer#doFrame` — начало кадра
- `measure`, `layout`, `draw` — стадии traversal
- `syncFrameState` — sync с RenderThread
- `DrawFrame` — работа RenderThread

---

## КОГДА НЕ оптимизировать

### Преждевременная оптимизация

```kotlin
// ❌ Не нужно если нет проблемы
// Сначала измерьте, потом оптимизируйте

// Profile GPU Rendering показывает < 16ms?
// Debug GPU Overdraw показывает синий/зелёный?
// Пользователи не жалуются на jank?
// → Не трогайте!
```

### Современные устройства

| Сценарий | Нужна ли оптимизация |
|----------|---------------------|
| High-end 120Hz | Overdraw 2x терпим |
| Mid-range 60Hz | Нужна оптимизация |
| Low-end | Критична каждая ms |

### Compose

Jetpack Compose имеет другой rendering pipeline:
- Нет View hierarchy
- Автоматический skip recomposition
- Меньше overdraw по умолчанию

```kotlin
// Compose — rendering оптимизирован из коробки
@Composable
fun MyScreen() {
    Column {
        Text("Hello")  // Рисуется напрямую, без View overhead
    }
}
```

---

## Типичные ошибки

### 1. Allocations в onDraw()

```kotlin
// ❌ GC pause каждые несколько кадров
override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // NEW OBJECT!
    val rect = Rect()    // NEW OBJECT!
}

// ✅ Создаём один раз
private val paint = Paint()
private val rect = Rect()
```

### 2. Забыли отключить Hardware Layer

```kotlin
// ❌ Memory leak
view.setLayerType(LAYER_TYPE_HARDWARE, null)
view.animate().translationX(100f).start()
// Забыли setLayerType(NONE) после анимации

// ✅ withEndAction или withLayer()
view.animate()
    .translationX(100f)
    .withLayer()  // Автоматически
    .start()
```

### 3. requestLayout() в onLayout()

```kotlin
// ❌ Бесконечный цикл
override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    child.requestLayout()  // НИКОГДА!
}
```

### 4. Большие bitmap без sampling

```kotlin
// ❌ 64MB bitmap для 48x48 ImageView
imageView.setImageResource(R.drawable.photo_4096x4096)

// ✅ Правильный размер
Glide.with(this).load(R.drawable.photo).override(48, 48).into(imageView)
```

### 5. Глубокая иерархия с weights

```xml
<!-- ❌ Double taxation nightmare -->
<LinearLayout android:weightSum="3">
    <LinearLayout android:layout_weight="1" android:weightSum="2">
        <View android:layout_weight="1"/>
        <View android:layout_weight="1"/>
    </LinearLayout>
</LinearLayout>

<!-- ✅ ConstraintLayout с chains -->
<ConstraintLayout>
    <View app:layout_constraintHorizontal_chainStyle="spread"/>
</ConstraintLayout>
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "UI Thread = RenderThread" | UI Thread (main) обрабатывает: input, measure, layout, записывает Display List. RenderThread выполняет GPU commands. Они работают параллельно через triple buffering |
| "60 FPS всегда достаточно" | На 120Hz дисплеях (многие современные телефоны) 60 FPS = jank. Target должен соответствовать refresh rate устройства. Используйте Display.getRefreshRate() |
| "invalidate() вызывает полный redraw" | invalidate() помечает View dirty. Только dirty Views будут redraw. Hardware layer позволяет skip redraw совсем |
| "Hardware Acceleration автоматическая" | HW Acceleration enabled по умолчанию с API 14, но некоторые операции fallback на software. Проверяйте canvas.isHardwareAccelerated() |
| "GPU всегда быстрее CPU" | GPU быстрее для параллельных операций (тысячи pixels одновременно). Для простых операций CPU может быть быстрее из-за overhead GPU setup |
| "Overdraw безвреден" | 2x overdraw = GPU рисует каждый pixel дважды. На сложных layouts может быть 4-5x overdraw. Debug GPU Overdraw визуализирует проблему |
| "VSYNC — это ограничение" | VSYNC синхронизирует buffer swap с display refresh. Без VSYNC — tearing (разрыв кадра). Это feature, не limitation |
| "Hardware Layer = free performance" | Hardware Layer требует GPU memory (width × height × 4 bytes). Полезен для complex views с простыми анимациями. Вреден для часто меняющегося контента |
| "requestLayout() дешёвый" | requestLayout() триггерит measure + layout всей иерархии от root. На глубоких деревьях = significant overhead. Используйте только когда размер действительно меняется |
| "Compose рендерит по-другому" | Compose использует тот же rendering pipeline: Composition → Layout → Draw → RenderThread → GPU. Оптимизации те же (skipping, caching) |

---

## CS-фундамент

| CS-концепция | Применение в View Rendering Pipeline |
|--------------|-------------------------------------|
| **Double/Triple Buffering** | UI Thread пишет в buffer N, RenderThread рисует buffer N-1, Display показывает buffer N-2. Предотвращает tearing и позволяет parallel execution |
| **VSYNC Signal** | Vertical synchronization signal от display hardware. Choreographer использует VSYNC для scheduling frame work. Frame deadline = VSYNC interval |
| **Display List / Recording** | Canvas operations записываются в Display List (RenderNode), не выполняются сразу. Позволяет replay, caching, GPU acceleration |
| **Tree Traversal** | Measure/Layout/Draw проходят View hierarchy depth-first. Порядок: parent before children (measure), children before parent (размер зависит от детей) |
| **Dirty Region Tracking** | Система отслеживает "dirty" (изменённые) области. Только dirty regions перерисовываются. Оптимизация bandwidth |
| **Z-Ordering** | Views рисуются в z-order (elevation, translationZ). Позднее нарисованное = поверх. Shadow rendering для elevated views |
| **Texture Upload** | Bitmap → GPU texture требует upload через GL/Vulkan. Large bitmaps = slow upload. Async texture loading решает проблему |
| **Framebuffer** | GPU рисует в framebuffer (off-screen memory). На VSYNC framebuffer swap показывает результат на display |
| **Jank Detection** | Frame считается janky если превышает VSYNC interval. FrameMetrics API даёт per-frame timing. Perfetto показывает детали |
| **Parallel Execution** | UI Thread и RenderThread работают параллельно. UI готовит следующий frame пока RenderThread рисует текущий. Pipeline parallelism |

---

## Связанные материалы

| Материал | Зачем смотреть |
|----------|----------------|
| [android-custom-view-fundamentals.md](android-custom-view-fundamentals.md) | invalidate vs requestLayout |
| [android-canvas-drawing.md](android-canvas-drawing.md) | Оптимизация onDraw() |
| [android-view-measurement.md](android-view-measurement.md) | Double taxation |
| [android-performance-profiling.md](android-performance-profiling.md) | Глубокий анализ |
| [[android-graphics-apis]] | OpenGL, Vulkan — GPU rendering APIs |
| [[android-animations]] | Choreographer, frame scheduling для анимаций |
| [[android-window-system]] | Surface, SurfaceFlinger — куда попадают кадры |

---

## Проверь себя

1. Сколько времени на кадр при 60Hz? При 120Hz?
2. Что делает Choreographer?
3. Какая разница между UI Thread и RenderThread?
4. Когда hardware layer помогает, а когда вредит?
5. Что означает красный цвет в Debug GPU Overdraw?
6. Почему нельзя создавать объекты в onDraw()?
7. Как Profile GPU Rendering помогает найти bottleneck?

---

## Связь с другими темами

### [[android-compose-internals]]
Compose использует собственный rendering pipeline (Composition → Layout → Drawing), который отличается от View-based pipeline. Однако оба подхода в итоге рисуют через те же Canvas/RenderNode и проходят через RenderThread и SurfaceFlinger. Понимание View rendering pipeline помогает осознать, какие оптимизации Compose делает автоматически (skip, recomposition) и почему interop между View и Compose может вызвать performance issues.

### [[android-performance-profiling]]
Profiling — практическое применение знаний о rendering pipeline. Systrace/Perfetto показывают timing каждой фазы (measure, layout, draw, sync, GPU), Profile GPU Rendering визуализирует frame budget. Без понимания pipeline невозможно интерпретировать результаты profiling tools. Рекомендуется изучить pipeline теоретически, затем закрепить через profiling реального приложения.

### [[android-ui-views]]
View System — потребитель rendering pipeline: каждая View проходит через measure → layout → draw. Знание View hierarchy (depth, overdraw, nested weights) напрямую влияет на rendering performance. Глубокие иерархии увеличивают время traversal, а overdraw тратит GPU-ресурсы на невидимые пиксели. Изучите View System перед rendering pipeline для понимания контекста.

### [[android-graphics-apis]]
Graphics APIs (Canvas, Paint, Path, Shader, RenderEffect) — инструменты, используемые в draw-фазе rendering pipeline. Canvas преобразуется в Display List (набор GPU-команд), который кэшируется в RenderNode. Hardware Layers кэшируют результат draw в GPU-текстуру для ускорения анимаций. Понимание graphics APIs объясняет, что происходит внутри onDraw() и как оптимизировать отрисовку.

### [[android-animations]]
Анимации — главный потребитель rendering pipeline: каждый кадр анимации проходит полный цикл invalidate → measure → layout → draw. Property animations (ValueAnimator, ObjectAnimator) изменяют свойства View и вызывают invalidate(). Hardware Layer animations обновляют только GPU-трансформацию без перерисовки, обеспечивая 60fps. Понимание rendering pipeline критично для создания плавных анимаций.

### [[android-window-system]]
Window System определяет Surface — конечный target рендеринга. Каждое окно (Activity, Dialog, Toast) имеет свой Surface, в который View tree рисует через RenderThread. SurfaceFlinger композитит все Surface в финальное изображение. Понимание window system объясняет, как rendering pipeline связан с compositor и VSYNC.

---

## Источники

- [Android Developers — Profile GPU Rendering](https://developer.android.com/topic/performance/rendering/profile-gpu)
- [Android Developers — Reduce Overdraw](https://developer.android.com/topic/performance/rendering/overdraw)
- [Android Developers — Slow Rendering](https://developer.android.com/topic/performance/vitals/render)
- [AOSP — Graphics Architecture](https://source.android.com/docs/core/graphics/architecture)
- [AOSP — VSYNC](https://source.android.com/docs/core/graphics/implement-vsync)
- [Perfetto — FrameTimeline](https://perfetto.dev/docs/data-sources/frametimeline)
- [Dan Lew — Hardware Layers](https://blog.danlew.net/2015/10/20/using-hardware-layers-to-improve-animation-performance/)

## Источники и дальнейшее чтение

- **Vasavada N. (2019). Android Internals.** — Глубокое описание ViewRootImpl, Choreographer, RenderThread и SurfaceFlinger. Единственный ресурс, подробно объясняющий полный путь от invalidate() до пикселей на экране. Обязательна для понимания rendering internals.
- **Meier R. (2022). Professional Android.** — Практическое покрытие rendering optimization: overdraw reduction, layout hierarchy flattening, hardware layer usage. Связывает теорию rendering pipeline с реальными оптимизациями в production-приложениях.
- **Phillips B. et al. (2022). Android Programming: The Big Nerd Ranch Guide.** — Введение в custom drawing, Canvas API и анимации с учётом rendering performance. Помогает понять draw-фазу pipeline через практические проекты.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

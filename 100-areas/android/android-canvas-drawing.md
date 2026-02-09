---
title: "Canvas Drawing: отрисовка на Canvas"
created: 2025-12-25
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [2d-graphics, coordinate-transformation, rasterization, paint-model]
research: "[[2025-12-25-android-canvas-drawing]]"
tags:
  - android
  - canvas
  - paint
  - drawing
  - graphics
  - performance
related:
  - "[[android-custom-view-fundamentals]]"
  - "[[android-view-measurement]]"
  - "[[android-view-rendering-pipeline]]"
  - "[[android-touch-handling]]"
  - "[[android-graphics-apis]]"
---

# Canvas Drawing: отрисовка на Canvas

Canvas — это 2D поверхность для рисования, предоставляющая методы для отрисовки фигур, текста, изображений и путей. Вместе с классом Paint они образуют основу графической системы Android: Canvas определяет ЧТО рисовать, Paint — КАК рисовать.

> **Prerequisites:**
> - [[android-custom-view-fundamentals]] — базовые концепции Custom Views
> - [[android-view-measurement]] — onMeasure и размеры View
> - Понимание жизненного цикла View

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Canvas** | 2D поверхность для рисования (ЧТО рисовать) |
| **Paint** | Настройки отрисовки (КАК рисовать: цвет, стиль, эффекты) |
| **Path** | Последовательность геометрических операций для сложных фигур |
| **Shader** | Заполнение градиентом или текстурой |
| **PorterDuff** | Режимы композитинга (комбинирования пикселей) |
| **Hardware Acceleration** | Отрисовка через GPU |
| **Layer Type** | Режим кэширования отрисовки |

---

## ПОЧЕМУ: Зачем понимать Canvas

### Проблема: стандартные View не подходят

```kotlin
// Нужен кастомный график
// Нужен индикатор прогресса уникальной формы
// Нужна интерактивная диаграмма
// Нужен игровой персонаж

// Стандартные View не дают такого контроля
// Canvas — единственный способ нарисовать что угодно
```

### Когда использовать Canvas

| Задача | Решение |
|--------|---------|
| Графики, диаграммы | Canvas + Path |
| Кастомный progress indicator | Canvas + drawArc |
| Игровая графика | Canvas + Bitmap |
| Рисование пользователем | Canvas + Path + touch events |
| Анимированные эффекты | Canvas + ValueAnimator |
| Простой фон | Shape Drawable (без Canvas) |
| Готовая иконка | VectorDrawable (без Canvas) |

### Аналогия: Художник

> **Canvas** — это холст художника
> **Paint** — это кисть с краской
> **Path** — это карандашный набросок перед покраской
> **Shader** — это специальная краска (градиент, текстура)

---

## ЧТО: Canvas и Paint

### Canvas — методы рисования

```kotlin
// Примитивы
canvas.drawRect(left, top, right, bottom, paint)
canvas.drawRoundRect(rectF, radiusX, radiusY, paint)
canvas.drawCircle(centerX, centerY, radius, paint)
canvas.drawOval(rectF, paint)
canvas.drawArc(rectF, startAngle, sweepAngle, useCenter, paint)
canvas.drawLine(startX, startY, stopX, stopY, paint)

// Текст
canvas.drawText(text, x, y, paint)

// Изображения
canvas.drawBitmap(bitmap, left, top, paint)
canvas.drawBitmap(bitmap, srcRect, dstRect, paint)

// Сложные формы
canvas.drawPath(path, paint)
```

### Paint — настройки отрисовки

```kotlin
// Базовые настройки
paint.color = Color.BLUE
paint.alpha = 128  // 0-255
paint.isAntiAlias = true  // Сглаживание краёв

// Стиль заливки
paint.style = Paint.Style.FILL          // Только заливка
paint.style = Paint.Style.STROKE        // Только обводка
paint.style = Paint.Style.FILL_AND_STROKE  // Оба

// Настройки обводки
paint.strokeWidth = 4f
paint.strokeCap = Paint.Cap.ROUND    // Круглые концы
paint.strokeJoin = Paint.Join.ROUND  // Круглые соединения

// Текст
paint.textSize = 48f
paint.typeface = Typeface.DEFAULT_BOLD
paint.textAlign = Paint.Align.CENTER
```

### Paint.Style — три режима

```
┌─────────────────────────────────────────────────────────────────┐
│  FILL              STROKE            FILL_AND_STROKE            │
│  ┌────────┐        ┌────────┐        ┌────────┐                 │
│  │████████│        │        │        │████████│                 │
│  │████████│        │        │        │████████│                 │
│  │████████│        │        │        │████████│                 │
│  └────────┘        └────────┘        └────────┘                 │
│  Заливка           Только контур     Заливка + контур           │
└─────────────────────────────────────────────────────────────────┘
```

---

## КАК: Практическая отрисовка

### Circular Progress Indicator

```kotlin
class CircularProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // ═══════════════════════════════════════════════════════════════
    // КРИТИЧНО: Создаём Paint объекты ОДИН раз в конструкторе
    // НЕ в onDraw() — иначе GC каждые N кадров = jank
    // ═══════════════════════════════════════════════════════════════
    private val trackPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 12f.dpToPx()
        strokeCap = Paint.Cap.ROUND
        color = Color.LTGRAY
    }

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 12f.dpToPx()
        strokeCap = Paint.Cap.ROUND
        color = Color.BLUE
    }

    // Переиспользуемые объекты
    private val arcRect = RectF()

    var progress: Float = 0f
        set(value) {
            field = value.coerceIn(0f, 1f)
            invalidate()  // Запрос перерисовки
        }

    // ═══════════════════════════════════════════════════════════════
    // onSizeChanged: пересчитываем зависимые от размера значения
    // Вызывается при изменении размера, НЕ при каждой отрисовке
    // ═══════════════════════════════════════════════════════════════
    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)

        val strokeWidth = trackPaint.strokeWidth
        val padding = strokeWidth / 2

        // Вычисляем RectF для дуги один раз
        arcRect.set(
            padding + paddingLeft,
            padding + paddingTop,
            w - padding - paddingRight,
            h - padding - paddingBottom
        )
    }

    // ═══════════════════════════════════════════════════════════════
    // onDraw: ТОЛЬКО рисование, никаких вычислений и allocations
    // Вызывается до 60 раз/сек при анимации
    // ═══════════════════════════════════════════════════════════════
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Фоновая дорожка (полная окружность)
        canvas.drawArc(arcRect, 0f, 360f, false, trackPaint)

        // Прогресс (дуга от 12 часов по часовой стрелке)
        val sweepAngle = progress * 360f
        canvas.drawArc(arcRect, -90f, sweepAngle, false, progressPaint)
    }

    private fun Float.dpToPx() = this * resources.displayMetrics.density
}
```

### drawArc параметры

```
┌─────────────────────────────────────────────────────────────────┐
│  drawArc(rectF, startAngle, sweepAngle, useCenter, paint)       │
│                                                                 │
│            -90° (top)                                           │
│               │                                                 │
│      180° ────┼──── 0° (right)                                  │
│               │                                                 │
│             90° (bottom)                                        │
│                                                                 │
│  startAngle: угол начала (0° = 3 часа, -90° = 12 часов)        │
│  sweepAngle: угол дуги (положительный = по часовой)            │
│  useCenter: true = pie chart, false = arc                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## КАК: Path — сложные формы

### Методы Path

```kotlin
val path = Path()

// Начать новый контур
path.moveTo(x, y)

// Линия от текущей точки
path.lineTo(x, y)

// Квадратичная кривая Безье (1 контрольная точка)
path.quadTo(controlX, controlY, endX, endY)

// Кубическая кривая Безье (2 контрольные точки)
path.cubicTo(control1X, control1Y, control2X, control2Y, endX, endY)

// Дуга
path.arcTo(rectF, startAngle, sweepAngle)

// Замкнуть путь (соединить с началом)
path.close()
```

### Пример: Сердце

```kotlin
class HeartView(context: Context) : View(context) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.RED
    }

    // Переиспользуемый Path
    private val heartPath = Path()

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)

        // Пересчитываем путь при изменении размера
        heartPath.reset()

        val centerX = w / 2f
        val topY = h * 0.3f
        val bottomY = h * 0.85f

        heartPath.moveTo(centerX, bottomY)  // Низ сердца

        // Левая половина (кубическая кривая)
        heartPath.cubicTo(
            w * 0.1f, h * 0.5f,   // Контрольная точка 1
            w * 0.15f, h * 0.15f, // Контрольная точка 2
            centerX, topY          // Конечная точка
        )

        // Правая половина
        heartPath.cubicTo(
            w * 0.85f, h * 0.15f,
            w * 0.9f, h * 0.5f,
            centerX, bottomY
        )
    }

    override fun onDraw(canvas: Canvas) {
        canvas.drawPath(heartPath, paint)
    }
}
```

---

## КАК: Shader'ы — градиенты и текстуры

### LinearGradient

```kotlin
private lateinit var gradientPaint: Paint

override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
    super.onSizeChanged(w, h, oldw, oldh)

    // Горизонтальный градиент
    val gradient = LinearGradient(
        0f, 0f,                    // Начальная точка
        w.toFloat(), 0f,           // Конечная точка
        Color.RED, Color.BLUE,     // Цвета
        Shader.TileMode.CLAMP      // Режим заполнения
    )

    gradientPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        shader = gradient
    }
}

override fun onDraw(canvas: Canvas) {
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), gradientPaint)
}
```

### RadialGradient

```kotlin
val radialGradient = RadialGradient(
    centerX, centerY,           // Центр
    radius,                     // Радиус
    Color.WHITE, Color.BLACK,   // Цвета (центр → край)
    Shader.TileMode.CLAMP
)
paint.shader = radialGradient
canvas.drawCircle(centerX, centerY, radius, paint)
```

### BitmapShader — круглые изображения

```kotlin
// Создаём shader из bitmap
val bitmapShader = BitmapShader(
    bitmap,
    Shader.TileMode.CLAMP,
    Shader.TileMode.CLAMP
)

private val circlePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
    shader = bitmapShader
}

override fun onDraw(canvas: Canvas) {
    // Рисуем круг, заполненный bitmap'ом
    canvas.drawCircle(centerX, centerY, radius, circlePaint)
}
```

### TileMode — режимы заполнения

| Mode | Описание |
|------|----------|
| `CLAMP` | Растягивает крайние пиксели |
| `REPEAT` | Повторяет паттерн |
| `MIRROR` | Зеркально отражает |

---

## КАК: PorterDuff — композитинг

### Основные режимы

```kotlin
// PorterDuff комбинирует два изображения:
// DST (destination) — уже нарисованное
// SRC (source) — то, что рисуем сейчас

paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN)
```

| Mode | Результат |
|------|-----------|
| `SRC` | Только SRC (игнорирует DST) |
| `DST` | Только DST (игнорирует SRC) |
| `SRC_OVER` | SRC поверх DST (default) |
| `DST_OVER` | DST поверх SRC |
| `SRC_IN` | SRC только где есть DST |
| `DST_IN` | DST только где есть SRC |
| `SRC_OUT` | SRC только где НЕТ DST |
| `CLEAR` | Очищает пиксели |

### Пример: Круглое изображение через PorterDuff

```kotlin
override fun onDraw(canvas: Canvas) {
    // ВАЖНО: нужен off-screen buffer для PorterDuff
    val layer = canvas.saveLayer(0f, 0f, width.toFloat(), height.toFloat(), null)

    // DST: рисуем круг
    canvas.drawCircle(centerX, centerY, radius, circlePaint)

    // Применяем режим
    imagePaint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN)

    // SRC: рисуем изображение
    canvas.drawBitmap(bitmap, 0f, 0f, imagePaint)

    // Сбрасываем режим
    imagePaint.xfermode = null

    canvas.restoreToCount(layer)
}
```

---

## КАК: Hardware Acceleration

### Уровни контроля

```kotlin
// 1. Application level (AndroidManifest.xml)
<application android:hardwareAccelerated="true">

// 2. Activity level
<activity android:hardwareAccelerated="false">

// 3. View level — только отключение
view.setLayerType(View.LAYER_TYPE_SOFTWARE, null)
```

### Неподдерживаемые операции

| Операция | Статус |
|----------|--------|
| `clipPath()` | API 18+ |
| `drawPicture()` | API 23+ |
| `setMaskFilter()` | Не поддерживается |
| `drawVertices()` | API 29+ |

### Проверка режима

```kotlin
override fun onDraw(canvas: Canvas) {
    if (canvas.isHardwareAccelerated) {
        // GPU rendering
    } else {
        // Software rendering
    }
}
```

---

## КАК: Performance Optimization

### Правило #1: НЕ создавать объекты в onDraw()

```kotlin
// ❌ ПЛОХО — allocation на каждый frame
override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // НИКОГДА!
    val rect = Rect(0, 0, 100, 100)  // НИКОГДА!
    canvas.drawRect(rect, paint)
}

// ✅ ХОРОШО — создаём один раз
private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
private val rect = Rect()

override fun onDraw(canvas: Canvas) {
    rect.set(0, 0, 100, 100)  // Переиспользуем
    canvas.drawRect(rect, paint)
}
```

### clipRect — рисовать только видимое

```kotlin
override fun onDraw(canvas: Canvas) {
    // Сохраняем состояние canvas
    canvas.save()

    // Ограничиваем область рисования
    canvas.clipRect(visibleRect)

    // Всё за пределами visibleRect игнорируется
    drawComplexContent(canvas)

    // Восстанавливаем состояние
    canvas.restore()
}
```

### quickReject — проверка без рисования

```kotlin
override fun onDraw(canvas: Canvas) {
    for (item in items) {
        // Проверяем, виден ли объект
        if (canvas.quickReject(item.bounds, Canvas.EdgeType.AA)) {
            // Объект полностью за пределами видимой области
            // Пропускаем дорогое рисование
            continue
        }
        drawItem(canvas, item)
    }
}
```

### Layer Types — кэширование

```kotlin
// Hardware layer — для анимаций (alpha, rotation, translation)
view.setLayerType(View.LAYER_TYPE_HARDWARE, null)

ObjectAnimator.ofFloat(view, "rotationY", 180f).apply {
    addListener(object : AnimatorListenerAdapter() {
        override fun onAnimationEnd(animation: Animator) {
            // ВАЖНО: отключить после анимации (экономит GPU память)
            view.setLayerType(View.LAYER_TYPE_NONE, null)
        }
    })
    start()
}
```

### Bitmap caching — для статического контента

```kotlin
class CachedView(context: Context) : View(context) {

    private var cacheBitmap: Bitmap? = null
    private var isCacheValid = false

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        cacheBitmap?.recycle()
        cacheBitmap = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        isCacheValid = false
    }

    override fun onDraw(canvas: Canvas) {
        if (!isCacheValid) {
            // Рисуем в кэш только когда нужно
            val cacheCanvas = Canvas(cacheBitmap!!)
            drawComplexContent(cacheCanvas)
            isCacheValid = true
        }
        // Быстро отрисовываем кэш
        canvas.drawBitmap(cacheBitmap!!, 0f, 0f, null)
    }

    fun invalidateCache() {
        isCacheValid = false
        invalidate()
    }
}
```

---

## КОГДА НЕ использовать Canvas

### 1. Compose Canvas — для новых проектов

```kotlin
@Composable
fun CircularProgress(progress: Float) {
    Canvas(modifier = Modifier.size(100.dp)) {
        val strokeWidth = 8.dp.toPx()

        // Фон
        drawArc(
            color = Color.LightGray,
            startAngle = 0f,
            sweepAngle = 360f,
            useCenter = false,
            style = Stroke(strokeWidth)
        )

        // Прогресс
        drawArc(
            color = Color.Blue,
            startAngle = -90f,
            sweepAngle = progress * 360f,
            useCenter = false,
            style = Stroke(strokeWidth, cap = StrokeCap.Round)
        )
    }
}
```

### 2. VectorDrawable — для иконок

```xml
<!-- res/drawable/ic_star.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFD700"
        android:pathData="M12,2l3,7h7l-5.5,4.5l2,7.5l-6.5,-4.5l-6.5,4.5l2,-7.5l-5.5,-4.5h7z"/>
</vector>
```

### 3. Shape Drawable — для простых фигур

```xml
<!-- res/drawable/rounded_rect.xml -->
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#FF0000"/>
    <corners android:radius="16dp"/>
</shape>
```

---

## Проверь себя

1. **В чём разница между Canvas и Paint?**
   - Canvas = ЧТО рисовать (методы рисования)
   - Paint = КАК рисовать (стиль, цвет, эффекты)

2. **Почему нельзя создавать Paint в onDraw()?**
   - onDraw() вызывается до 60 раз/сек, allocations = GC = jank

3. **Когда использовать LAYER_TYPE_SOFTWARE?**
   - Когда используете операции, не поддерживаемые hardware acceleration

4. **Как работает quickReject?**
   - Проверяет, находится ли объект за пределами видимой области без рисования

5. **Зачем нужен saveLayer для PorterDuff?**
   - PorterDuff требует off-screen buffer для правильного композитинга

---

## ПОЧЕМУ: Глубокое понимание Canvas

### Почему Hardware Acceleration не поддерживает все операции?

**GPU vs CPU для 2D рисования:**

```kotlin
// GPU оптимизирован для:
// - Текстурированные треугольники (meshes)
// - Matrix transformations
// - Blending (alpha compositing)
// - Shader programs

// GPU НЕ оптимизирован для:
// - Произвольные path operations
// - Некоторые PorterDuff modes
// - clipPath() с complex paths
// - drawBitmapMesh()

// При HW acceleration unsupported операции:
// - Либо fallback на software (медленно)
// - Либо некорректный результат
// - Либо просто не рисуются
```

**Как Android рисует с HW acceleration:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Drawing Pipeline с Hardware Acceleration:                        │
│                                                                 │
│ View.onDraw(canvas)                                              │
│      │                                                          │
│      ▼                                                          │
│ Canvas записывает операции в Display List                        │
│      │                                                          │
│      ▼                                                          │
│ RenderThread обрабатывает Display List                          │
│      │                                                          │
│      ▼                                                          │
│ OpenGL/Vulkan команды → GPU                                      │
│      │                                                          │
│      ▼                                                          │
│ Пиксели на экране                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Почему нельзя создавать объекты в onDraw()?

**GC pressure при 60 FPS:**

```kotlin
// 60 FPS = onDraw() вызывается 60 раз/сек
// Если каждый вызов создаёт объекты:

override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // ❌ Аллокация каждый frame!
    val rect = RectF(0f, 0f, width.toFloat(), height.toFloat())  // ❌
    // ...
}

// За 1 секунду: 60 × (Paint + RectF + ...) = сотни объектов
// За 1 минуту: тысячи объектов → GC → jank!

// Dalvik (старые устройства): stop-the-world GC = заметные паузы
// ART (современные): concurrent GC, но всё равно overhead
```

**Правильный подход:**

```kotlin
class OptimizedView(context: Context) : View(context) {
    // Создаём ОДИН раз — переиспользуем многократно
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.RED
        style = Paint.Style.FILL
    }
    private val rect = RectF()  // Mutable rect для reuse
    private val path = Path()

    override fun onDraw(canvas: Canvas) {
        // Обновляем mutable объекты, не создаём новые
        rect.set(0f, 0f, width.toFloat(), height.toFloat())
        path.reset()  // Очищаем вместо new Path()

        canvas.drawRect(rect, paint)
    }
}
```

### Почему saveLayer() медленный?

**Off-screen buffer:**

```kotlin
// saveLayer() создаёт temporary bitmap в памяти:
// 1. Аллоцирует buffer размером с canvas/bounds
// 2. Все последующие операции рисуются в buffer
// 3. При restore() buffer composited на main canvas

// Память для full-screen layer:
// 1080 × 1920 × 4 bytes (ARGB) = 8.3 MB за ОДИН layer!

// Несколько layers = несколько буферов
canvas.saveLayer(bounds, null)           // Buffer 1: 8.3 MB
    canvas.saveLayer(smallerBounds, null)  // Buffer 2: varies
        // Drawing...
    canvas.restore()
canvas.restore()
```

**Когда saveLayer необходим:**

```kotlin
// PorterDuff compositing требует off-screen buffer
// Без него — некорректный результат

// ПРАВИЛЬНО (но медленно):
canvas.saveLayer(bounds, null)
canvas.drawCircle(...)
paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.DST_OUT)
canvas.drawCircle(...)
paint.xfermode = null
canvas.restore()
```

### Почему Path дорогой?

**Path internals:**

```kotlin
// Path хранит список команд:
path.moveTo(0f, 0f)     // Command: MOVE_TO
path.lineTo(100f, 0f)   // Command: LINE_TO
path.quadTo(...)        // Command: QUAD_TO
path.cubicTo(...)       // Command: CUBIC_TO

// При рисовании:
// 1. Path преобразуется в vertices
// 2. Vertices отправляются на GPU
// 3. GPU рисует triangles

// Complex path с сотнями команд = много вычислений
// Особенно при animations — пересчёт каждый frame
```

**Оптимизация Path:**

```kotlin
// Cache path, обновляй только при изменении
private var pathCached = false
private val cachedPath = Path()

override fun onDraw(canvas: Canvas) {
    if (!pathCached) {
        cachedPath.reset()
        buildComplexPath(cachedPath)  // Дорогая операция
        pathCached = true
    }
    canvas.drawPath(cachedPath, paint)
}

fun updateData() {
    pathCached = false  // Invalidate cache
    invalidate()
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Hardware Acceleration всегда быстрее" | HW Acceleration быстрее для ПОДДЕРЖИВАЕМЫХ операций. clipPath с complex paths, некоторые PorterDuff modes могут быть медленнее или некорректны. Проверяйте specific operations |
| "Paint можно создавать где угодно" | Paint в onDraw = allocation 60 раз/сек = GC pressure = jank. Создавайте Paint как поле класса и переиспользуйте |
| "saveLayer безопасен" | saveLayer создаёт off-screen buffer = значительный memory overhead. Full-screen layer = 8+ MB. Используйте только когда необходимо (PorterDuff compositing) |
| "invalidate() сразу вызывает onDraw()" | invalidate() помечает View dirty. onDraw() вызывается на следующем VSYNC (через Choreographer). Множественные invalidate() батчатся |
| "Canvas.rotate() поворачивает объект" | rotate() трансформирует COORDINATE SYSTEM, не объект. Последующие drawing operations используют rotated coordinates |
| "drawBitmap дешёвый" | drawBitmap может быть дорогим: scaling (особенно без HW), memory access, blending. Используйте правильный Bitmap.Config (RGB_565 vs ARGB_8888) |
| "Path можно модифицировать in-place" | Path можно модифицировать, но это invalidates internal caches. Для частых изменений рассмотрите пересоздание или использование path.reset() |
| "clipRect — простая операция" | clipRect O(1), но clipPath может быть O(n) где n = количество path segments. Complex clipping = performance hit |
| "Compose Canvas совсем другой" | Compose Canvas построен на тех же примитивах (android.graphics.Canvas под капотом). Те же ограничения HW acceleration, те же оптимизации |
| "Anti-aliasing незаметен" | Anti-aliasing (Paint.ANTI_ALIAS_FLAG) делает edges smooth, но добавляет overhead. Для pixel-perfect graphics или высокой производительности можно отключить |

---

## CS-фундамент

| CS-концепция | Применение в Canvas Drawing |
|--------------|----------------------------|
| **Immediate Mode Rendering** | Canvas использует immediate mode: команды рисования выполняются сразу (или записываются в display list). Контраст с retained mode (Scene Graph) |
| **Transformation Matrices** | Canvas.translate/rotate/scale применяют 3x3 affine transformation matrix. Все операции — matrix multiplication |
| **Compositing (Porter-Duff)** | PorterDuff modes реализуют alpha compositing algorithms. 12+ modes для разных blend операций (SRC_OVER, DST_OUT, etc.) |
| **Rasterization** | Vector graphics (Path) преобразуются в pixels через rasterization. Anti-aliasing = supersampling для smooth edges |
| **Double Buffering** | Android использует double/triple buffering. Drawing идёт в back buffer, swap на VSYNC. Предотвращает tearing |
| **GPU Pipeline** | HW accelerated drawing: Canvas → Display List → RenderThread → OpenGL/Vulkan → GPU → Framebuffer |
| **Memory Management** | Bitmap memory: width × height × bytes_per_pixel. ARGB_8888 = 4 bytes, RGB_565 = 2 bytes. Trade-off quality vs memory |
| **Clipping Algorithms** | clipRect использует axis-aligned bounding box. clipPath может использовать Sutherland-Hodgman для polygon clipping |
| **Path Tessellation** | Curves (quadTo, cubicTo) tessellated в line segments для rendering. More segments = smoother curves = more vertices |
| **Object Pooling** | Reusing Paint, Path, RectF objects избегает allocations. Classic object pool pattern для performance |

---

## Связанные материалы

| Материал | Зачем изучать |
|----------|---------------|
| [[android-custom-view-fundamentals]] | Основы Custom Views, конструкторы, lifecycle |
| [[android-view-measurement]] | onMeasure перед onDraw |
| [[android-touch-handling]] | Интерактивность для Canvas |
| [[android-view-rendering-pipeline]] | Как Canvas превращается в пиксели |
| [[android-compose]] | Compose Canvas — современная альтернатива |
| [[android-graphics-apis]] | OpenGL, Vulkan — низкоуровневые Graphics APIs |

---

## Источники

| Источник | Тип | Вклад |
|----------|-----|-------|
| [Create a custom drawing](https://developer.android.com/develop/ui/views/layout/custom-views/custom-drawing) | Official | Canvas/Paint basics |
| [Hardware acceleration](https://developer.android.com/develop/ui/views/graphics/hardware-accel) | Official | HW accel limits |
| [Canvas API](https://developer.android.com/reference/android/graphics/Canvas) | Official | Drawing methods |
| [PorterDuff.Mode](https://developer.android.com/reference/android/graphics/PorterDuff.Mode) | Official | Blending modes |
| [Clipping Canvas Objects](https://developer.android.com/codelabs/advanced-android-kotlin-training-clipping-canvas-objects) | Official | clipRect, quickReject |
| [Creating Effects with Shaders](https://developer.android.com/codelabs/advanced-android-kotlin-training-shaders) | Official | Shader examples |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

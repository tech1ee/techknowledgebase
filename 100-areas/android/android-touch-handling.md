---
title: "Android Touch Handling"
created: 2025-01-15
modified: 2026-01-05
cs-foundations: [event-dispatching, hit-testing, gesture-recognition, event-bubbling]
tags:
  - android
  - touch
  - gestures
  - motionevent
  - compose
related:
  - "[[android-custom-view-fundamentals]]"
  - "[[android-compose]]"
  - "[[android-view-rendering-pipeline]]"
---

# Android Touch Handling

> Полное руководство по обработке касаний: от MotionEvent до Compose pointerInput

---

## Зачем это нужно

**Проблема:** Touch handling — один из самых запутанных аспектов Android. Типичные баги:
- **Кнопка не кликается** внутри ScrollView — родитель перехватывает события
- **Вложенные RecyclerView конфликтуют** — два списка "борются" за scroll
- **Жест свайпа не работает** — неправильные return values в onTouchEvent
- **View "залипает"** — не обработали ACTION_CANCEL

**Почему это сложно:**
- 3 метода (dispatchTouchEvent, onInterceptTouchEvent, onTouchEvent) с неочевидным взаимодействием
- Return values (true/false) критически влияют на поведение
- Multi-touch добавляет pointer index vs pointer ID путаницу
- Nested scrolling требует отдельного понимания

**Что даёт понимание:**
- Создание custom gestures (swipe-to-dismiss, pinch-to-zoom)
- Решение конфликтов прокрутки (ViewPager внутри RecyclerView)
- Interactive views (seekbar, drag-drop, custom slider)
- Отладка "почему не кликается"

**View vs Compose:**
- View: низкоуровневый контроль, больше boilerplate, полная гибкость
- Compose: декларативный API (pointerInput, detectTapGestures), проще для 90% случаев

---

## Терминология

| Термин | Значение |
|--------|----------|
| **MotionEvent** | Класс, представляющий touch событие (координаты, action, pointer) |
| **Touch Slop** | Минимальное расстояние для распознавания drag (~16dp) |
| **Pointer Index** | Позиция пальца в массиве MotionEvent (меняется между событиями) |
| **Pointer ID** | Уникальный идентификатор пальца (постоянный на протяжении жеста) |
| **onInterceptTouchEvent** | Метод ViewGroup для перехвата событий у детей |
| **Nested Scrolling** | Механизм координации прокрутки между parent/child |

---

## Аналогия: Почтовая система

```
Touch Event = Письмо

dispatchTouchEvent() = Почтовое отделение (маршрутизация)
onInterceptTouchEvent() = Проверка на границе (можно перехватить)
onTouchEvent() = Конечный получатель (обработка)

ACTION_CANCEL = "Письмо отозвано отправителем"
```

---

## Touch Event System (View)

### Три метода обработки

```
┌─────────────────────────────────────────────────────────────┐
│                      Activity                                │
│  dispatchTouchEvent() → начало маршрутизации                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     ViewGroup (Parent)                       │
│  dispatchTouchEvent()                                        │
│       ↓                                                      │
│  onInterceptTouchEvent() ──true──→ parent.onTouchEvent()    │
│       ↓ false                                                │
│  child.dispatchTouchEvent()                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       View (Child)                           │
│  dispatchTouchEvent()                                        │
│       ↓                                                      │
│  onTouchEvent() ──false──→ parent.onTouchEvent()            │
│       ↓ true                                                 │
│  "Событие обработано"                                        │
└─────────────────────────────────────────────────────────────┘
```

### MotionEvent Actions

| Action | Когда | Что делать |
|--------|-------|------------|
| `ACTION_DOWN` | Первый палец | Сохранить начальные координаты, вернуть true |
| `ACTION_MOVE` | Любой палец двигается | Обновить позицию, проверить threshold |
| `ACTION_UP` | Последний палец | Завершить жест, очистить состояние |
| `ACTION_CANCEL` | Родитель перехватил | Сбросить состояние как при UP |
| `ACTION_POINTER_DOWN` | Второй+ палец | Обновить multi-touch состояние |
| `ACTION_POINTER_UP` | Не последний палец поднят | Обновить активный pointer |

### Return Values — КРИТИЧЕСКИ ВАЖНО

```kotlin
// onTouchEvent return values
return true   // "Я обработал событие, не передавай выше"
return false  // "Я не обработал, передай родителю"

// onInterceptTouchEvent return values
return true   // "Перехватываю! Ребёнок получит ACTION_CANCEL"
return false  // "Пропускаю к ребёнку"
```

**ПРАВИЛО:** Если вернуть false в ACTION_DOWN, вы НЕ получите последующие MOVE и UP!

### Multi-touch: Index vs ID

```kotlin
// НЕПРАВИЛЬНО — index меняется между событиями
val x = event.getX(0)  // Может быть другой палец!

// ПРАВИЛЬНО — ID постоянен на протяжении жеста
class TouchTracker {
    private var activePointerId = INVALID_POINTER_ID

    fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                // Сохраняем ID первого пальца
                activePointerId = event.getPointerId(0)
            }
            MotionEvent.ACTION_MOVE -> {
                // Находим index по сохранённому ID
                val pointerIndex = event.findPointerIndex(activePointerId)
                if (pointerIndex != -1) {
                    val x = event.getX(pointerIndex)
                    val y = event.getY(pointerIndex)
                }
            }
            MotionEvent.ACTION_POINTER_UP -> {
                // Если активный палец поднят — переключаемся на другой
                val actionIndex = event.actionIndex
                val pointerId = event.getPointerId(actionIndex)
                if (pointerId == activePointerId) {
                    // Выбираем следующий палец
                    val newIndex = if (actionIndex == 0) 1 else 0
                    activePointerId = event.getPointerId(newIndex)
                }
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                activePointerId = INVALID_POINTER_ID
            }
        }
        return true
    }

    companion object {
        private const val INVALID_POINTER_ID = -1
    }
}
```

---

## КАК: Практические примеры

### 1. Базовый onTouchEvent

```kotlin
class DraggableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    // Состояние — создаём один раз, не в onTouchEvent!
    private var lastTouchX = 0f
    private var lastTouchY = 0f
    private var isDragging = false

    // Системный порог для drag
    private val touchSlop = ViewConfiguration.get(context).scaledTouchSlop

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                // Сохраняем начальную позицию
                lastTouchX = event.x
                lastTouchY = event.y
                isDragging = false
                return true  // ВАЖНО: возвращаем true для получения MOVE/UP
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastTouchX
                val dy = event.y - lastTouchY

                // Проверяем превышение порога touch slop
                if (!isDragging) {
                    if (abs(dx) > touchSlop || abs(dy) > touchSlop) {
                        isDragging = true
                    }
                }

                if (isDragging) {
                    // Перемещаем view
                    translationX += dx
                    translationY += dy
                    lastTouchX = event.x
                    lastTouchY = event.y
                }
                return true
            }

            MotionEvent.ACTION_UP -> {
                isDragging = false
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                // ВАЖНО: обрабатываем отмену так же, как UP
                isDragging = false
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### 2. onInterceptTouchEvent для ViewGroup

```kotlin
class HorizontalScrollContainer @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private val touchSlop = ViewConfiguration.get(context).scaledTouchSlop
    private var initialX = 0f
    private var initialY = 0f
    private var isScrolling = false

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        when (ev.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                // Запоминаем начальную точку, не перехватываем
                initialX = ev.x
                initialY = ev.y
                isScrolling = false
                return false
            }

            MotionEvent.ACTION_MOVE -> {
                if (isScrolling) {
                    return true  // Уже скроллим — продолжаем перехватывать
                }

                val dx = abs(ev.x - initialX)
                val dy = abs(ev.y - initialY)

                // Перехватываем только горизонтальное движение
                if (dx > touchSlop && dx > dy) {
                    isScrolling = true
                    // Ребёнок получит ACTION_CANCEL
                    return true
                }
                return false
            }

            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                isScrolling = false
                return false
            }
        }
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Обрабатываем горизонтальный скролл
        when (event.actionMasked) {
            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - initialX
                scrollBy(-dx.toInt(), 0)
                initialX = event.x
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                isScrolling = false
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### 3. GestureDetector для стандартных жестов

```kotlin
class GestureAwareView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    // Детектор жестов
    private val gestureDetector = GestureDetectorCompat(context,
        object : GestureDetector.SimpleOnGestureListener() {

            // ОБЯЗАТЕЛЬНО вернуть true — иначе другие жесты не сработают!
            override fun onDown(e: MotionEvent): Boolean = true

            override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
                // Одиночный тап (после проверки, что это не double tap)
                performClick()
                return true
            }

            override fun onDoubleTap(e: MotionEvent): Boolean {
                // Двойной тап
                toggleZoom()
                return true
            }

            override fun onLongPress(e: MotionEvent) {
                // Долгое нажатие
                showContextMenu()
            }

            override fun onScroll(
                e1: MotionEvent?,
                e2: MotionEvent,
                distanceX: Float,
                distanceY: Float
            ): Boolean {
                // distanceX/Y — смещение С ПРОШЛОГО события (не от начала!)
                scrollBy(distanceX.toInt(), distanceY.toInt())
                return true
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                // velocityX/Y в пикселях/секунду
                startFlingAnimation(velocityX, velocityY)
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }

    private fun toggleZoom() { /* ... */ }
    private fun showContextMenu() { /* ... */ }
    private fun startFlingAnimation(vx: Float, vy: Float) { /* ... */ }
}
```

### 4. ScaleGestureDetector для pinch-to-zoom

```kotlin
class ZoomableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var scaleFactor = 1f
    private val minScale = 0.5f
    private val maxScale = 5f

    private val scaleDetector = ScaleGestureDetector(context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {

            override fun onScale(detector: ScaleGestureDetector): Boolean {
                // detector.scaleFactor — множитель относительно прошлого события
                scaleFactor *= detector.scaleFactor

                // Ограничиваем масштаб
                scaleFactor = scaleFactor.coerceIn(minScale, maxScale)

                // Центр масштабирования
                pivotX = detector.focusX
                pivotY = detector.focusY

                scaleX = scaleFactor
                scaleY = scaleFactor

                return true
            }

            override fun onScaleBegin(detector: ScaleGestureDetector): Boolean {
                // Вернуть true для начала отслеживания
                return true
            }

            override fun onScaleEnd(detector: ScaleGestureDetector) {
                // Анимация snap-to-grid, если нужно
            }
        }
    )

    private val gestureDetector = GestureDetectorCompat(context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent) = true

            override fun onDoubleTap(e: MotionEvent): Boolean {
                // Double tap для toggle zoom
                scaleFactor = if (scaleFactor > 1f) 1f else 2f
                scaleX = scaleFactor
                scaleY = scaleFactor
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // ВАЖНО: оба детектора должны получить событие
        var handled = scaleDetector.onTouchEvent(event)
        handled = gestureDetector.onTouchEvent(event) || handled
        return handled || super.onTouchEvent(event)
    }
}
```

### 5. VelocityTracker для fling

```kotlin
class FlingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var velocityTracker: VelocityTracker? = null
    private val minFlingVelocity = ViewConfiguration.get(context).scaledMinimumFlingVelocity
    private val maxFlingVelocity = ViewConfiguration.get(context).scaledMaximumFlingVelocity

    private var lastX = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                // Создаём или сбрасываем трекер
                velocityTracker?.recycle()
                velocityTracker = VelocityTracker.obtain()
                velocityTracker?.addMovement(event)
                lastX = event.x
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                velocityTracker?.addMovement(event)

                // Перемещаем view
                val dx = event.x - lastX
                translationX += dx
                lastX = event.x
                return true
            }

            MotionEvent.ACTION_UP -> {
                velocityTracker?.let { tracker ->
                    tracker.addMovement(event)

                    // ВАЖНО: вычисляем скорость ДО recycle
                    tracker.computeCurrentVelocity(1000, maxFlingVelocity.toFloat())
                    val velocityX = tracker.xVelocity

                    // Проверяем порог для fling
                    if (abs(velocityX) > minFlingVelocity) {
                        startFling(velocityX)
                    }

                    tracker.recycle()
                }
                velocityTracker = null
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                velocityTracker?.recycle()
                velocityTracker = null
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    private fun startFling(velocity: Float) {
        // Используем OverScroller или физическую анимацию
        animate()
            .translationXBy(velocity * 0.5f)
            .setDuration(300)
            .setInterpolator(DecelerateInterpolator())
            .start()
    }
}
```

### 6. requestDisallowInterceptTouchEvent — защита от перехвата

```kotlin
class ChildScrollView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val touchSlop = ViewConfiguration.get(context).scaledTouchSlop
    private var initialY = 0f
    private var isScrolling = false

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                initialY = event.y
                isScrolling = false
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                val dy = abs(event.y - initialY)

                if (!isScrolling && dy > touchSlop) {
                    isScrolling = true
                    // Запрещаем родителю перехватывать
                    parent.requestDisallowInterceptTouchEvent(true)
                }

                if (isScrolling) {
                    // Обрабатываем скролл
                    scrollBy(0, (initialY - event.y).toInt())
                    initialY = event.y
                }
                return true
            }

            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                isScrolling = false
                // Разрешаем родителю перехватывать снова
                parent.requestDisallowInterceptTouchEvent(false)
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### 7. TouchDelegate — расширение touch области

```kotlin
class TouchDelegateExample : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val parentView = findViewById<View>(R.id.parent)
        val smallButton = findViewById<Button>(R.id.small_button)

        // ВАЖНО: используем post для гарантии завершения layout
        parentView.post {
            val rect = Rect()
            smallButton.getHitRect(rect)

            // Расширяем touch область на 48dp во все стороны
            val extraSpace = (48 * resources.displayMetrics.density).toInt()
            rect.inset(-extraSpace, -extraSpace)

            parentView.touchDelegate = TouchDelegate(rect, smallButton)
        }
    }
}
```

### 8. Swipe-to-Dismiss View

```kotlin
class SwipeToDismissView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private val touchSlop = ViewConfiguration.get(context).scaledTouchSlop
    private val dismissThreshold = 0.4f  // 40% ширины для dismiss

    private var initialX = 0f
    private var isSwiping = false
    private var velocityTracker: VelocityTracker? = null

    var onDismissListener: (() -> Unit)? = null

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        when (ev.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                initialX = ev.x
                isSwiping = false
                velocityTracker?.recycle()
                velocityTracker = VelocityTracker.obtain()
                velocityTracker?.addMovement(ev)
            }
            MotionEvent.ACTION_MOVE -> {
                velocityTracker?.addMovement(ev)
                val dx = ev.x - initialX
                if (abs(dx) > touchSlop) {
                    isSwiping = true
                    return true  // Перехватываем
                }
            }
        }
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        velocityTracker?.addMovement(event)

        when (event.actionMasked) {
            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - initialX
                // Сопротивление при свайпе в "неправильную" сторону
                val translationAmount = if (dx > 0) dx else dx * 0.3f
                translationX = translationAmount

                // Fade out при свайпе
                alpha = 1f - abs(translationX) / width * 0.5f
                return true
            }

            MotionEvent.ACTION_UP -> {
                velocityTracker?.computeCurrentVelocity(1000)
                val velocityX = velocityTracker?.xVelocity ?: 0f

                val dismissByDistance = abs(translationX) > width * dismissThreshold
                val dismissByVelocity = abs(velocityX) > 1000f &&
                    (velocityX > 0) == (translationX > 0)

                if (dismissByDistance || dismissByVelocity) {
                    animateDismiss(velocityX > 0)
                } else {
                    animateReturn()
                }

                velocityTracker?.recycle()
                velocityTracker = null
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                animateReturn()
                velocityTracker?.recycle()
                velocityTracker = null
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    private fun animateDismiss(toRight: Boolean) {
        val targetX = if (toRight) width.toFloat() else -width.toFloat()
        animate()
            .translationX(targetX)
            .alpha(0f)
            .setDuration(200)
            .withEndAction { onDismissListener?.invoke() }
            .start()
    }

    private fun animateReturn() {
        animate()
            .translationX(0f)
            .alpha(1f)
            .setDuration(200)
            .start()
    }
}
```

---

## КОГДА НЕ использовать raw touch handling

### Используйте готовые решения

| Задача | Решение |
|--------|---------|
| Tap, long press, fling | `GestureDetector` |
| Pinch-to-zoom | `ScaleGestureDetector` |
| Свайп страниц | `ViewPager2` |
| Drag-drop | `ItemTouchHelper` |
| Вложенный скролл | `NestedScrollView`, `RecyclerView` |
| Swipe-to-dismiss | `ItemTouchHelper.SimpleCallback` |
| Pull-to-refresh | `SwipeRefreshLayout` |

### Compose Touch API — проще

```kotlin
// Compose — декларативный подход
@Composable
fun DraggableBox() {
    var offsetX by remember { mutableStateOf(0f) }
    var offsetY by remember { mutableStateOf(0f) }

    Box(
        Modifier
            .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
            .pointerInput(Unit) {
                detectDragGestures { change, dragAmount ->
                    change.consume()
                    offsetX += dragAmount.x
                    offsetY += dragAmount.y
                }
            }
    )
}
```

### Когда всё-таки нужен raw touch

- Сложные multi-touch жесты (3+ пальца)
- Игры с кастомным управлением
- Рисование (Canvas + touch)
- Интеграция с C++/NDK

---

## Типичные ошибки

### 1. Return false в ACTION_DOWN

```kotlin
// НЕПРАВИЛЬНО — не получим MOVE и UP
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.actionMasked) {
        MotionEvent.ACTION_DOWN -> {
            saveInitialPosition(event)
            return false  // БАГ!
        }
    }
}

// ПРАВИЛЬНО
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.actionMasked) {
        MotionEvent.ACTION_DOWN -> {
            saveInitialPosition(event)
            return true  // Получим все последующие события
        }
    }
}
```

### 2. Игнорирование ACTION_CANCEL

```kotlin
// НЕПРАВИЛЬНО — состояние "зависает"
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.actionMasked) {
        MotionEvent.ACTION_DOWN -> isPressed = true
        MotionEvent.ACTION_UP -> isPressed = false
        // ACTION_CANCEL не обработан!
    }
}

// ПРАВИЛЬНО
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.actionMasked) {
        MotionEvent.ACTION_DOWN -> isPressed = true
        MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
            isPressed = false  // Сбрасываем и при cancel
        }
    }
}
```

### 3. getActionIndex() в ACTION_MOVE

```kotlin
// НЕПРАВИЛЬНО — всегда возвращает 0
val index = event.actionIndex  // 0 для ACTION_MOVE
val x = event.getX(index)

// ПРАВИЛЬНО — используем сохранённый pointer ID
val index = event.findPointerIndex(activePointerId)
if (index != -1) {
    val x = event.getX(index)
}
```

### 4. VelocityTracker без recycle

```kotlin
// НЕПРАВИЛЬНО — memory leak
private var velocityTracker = VelocityTracker.obtain()

// ПРАВИЛЬНО
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.actionMasked) {
        MotionEvent.ACTION_DOWN -> {
            velocityTracker?.recycle()
            velocityTracker = VelocityTracker.obtain()
        }
        MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
            velocityTracker?.recycle()
            velocityTracker = null
        }
    }
}
```

### 5. computeCurrentVelocity после ACTION_UP

```kotlin
// НЕПРАВИЛЬНО — скорость будет 0
MotionEvent.ACTION_UP -> {
    val velocity = velocityTracker?.xVelocity  // 0!
}

// ПРАВИЛЬНО — вычисляем ДО UP или сразу после addMovement
MotionEvent.ACTION_UP -> {
    velocityTracker?.addMovement(event)
    velocityTracker?.computeCurrentVelocity(1000)
    val velocity = velocityTracker?.xVelocity  // Корректное значение
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "onTouchEvent вызывается всегда" | onTouchEvent вызывается только если View declared interest в событии (вернул true в ACTION_DOWN). False в DOWN = View больше не получит события этого gesture |
| "Parent всегда получает события первым" | Parent получает onInterceptTouchEvent первым, но onTouchEvent идёт снизу вверх: ребёнок → родитель. Intercept и handle — разные фазы |
| "requestDisallowInterceptTouchEvent работает навсегда" | requestDisallowInterceptTouchEvent действует только до конца текущего gesture (до ACTION_UP/CANCEL). После этого флаг сбрасывается |
| "Pointer ID = pointer index" | ID стабилен для пальца на протяжении gesture, index может меняться при поднятии других пальцев. Всегда используй getPointerId() для tracking |
| "GestureDetector обрабатывает всё" | GestureDetector не обрабатывает: multi-touch, pinch, rotation, custom gestures. Для них нужны ScaleGestureDetector или custom implementation |
| "VelocityTracker автоматически отслеживает" | VelocityTracker нужно вручную: obtain(), addMovement() для каждого event, computeCurrentVelocity() перед чтением, recycle() |
| "ACTION_CANCEL — это ошибка" | ACTION_CANCEL — нормальное событие при intercept родителем. View должен корректно очищать состояние, анимации, highlights |
| "Touch slop не важен" | Touch slop (ViewConfiguration.getScaledTouchSlop) — минимальное расстояние для scroll/drag. Без него случайные микро-движения будут интерпретироваться как gestures |
| "Compose не использует View touch system" | Compose использует свою pointer input систему, но она построена на тех же принципах: propagation, consumption, gestures. pointerInput {} аналогичен onTouchEvent |
| "Nested scrolling сложный" | Nested scrolling — протокол координации. NestedScrollingChild сообщает parent о намерении scroll, parent решает сколько consume. В Compose — nestedScroll modifier |

---

## CS-фундамент

| CS-концепция | Применение в Touch Handling |
|--------------|----------------------------|
| **Event Propagation** | Touch events propagate по View hierarchy: capture phase (top-down, intercept) → bubble phase (bottom-up, handle). Паттерн из DOM events |
| **Chain of Responsibility** | Каждый View решает: обработать или передать дальше. First handler wins, остальные не получают event |
| **State Machine** | Gesture recognition — finite state machine: IDLE → PRESSED → DRAGGING → RELEASED. Transitions на основе events и thresholds |
| **Coordinate Systems** | Transformation между coordinate systems: screen → window → view → content. getX() vs getRawX() — разные systems |
| **Hit Testing** | Определение какой View под точкой касания. Алгоритм: recursive traversal, bounds check, z-order (последний рисуется = первый получает) |
| **Velocity Estimation** | VelocityTracker использует least squares regression для estimation velocity по истории точек. Сглаживает jitter |
| **Event Coalescing** | Система объединяет быстрые touch events в batches (getHistorySize). Batch processing для efficiency |
| **Gesture Recognition** | Pattern matching на последовательности events: tap = down + up (быстро), long press = down + delay, swipe = down + move (> slop) + up |
| **Concurrent State** | Multi-touch требует tracking multiple concurrent state machines (по одному на pointer). Pointer ID — identifier для correlation |
| **Delegation Pattern** | GestureDetector, ScaleGestureDetector — delegation gesture recognition. View делегирует detection, сам обрабатывает results |

---

## Связанные материалы

| Материал | Зачем смотреть |
|----------|----------------|
| [android-custom-view-fundamentals.md](android-custom-view-fundamentals.md) | Жизненный цикл View, где размещать touch логику |
| [android-canvas-drawing.md](android-canvas-drawing.md) | Рисование + touch = интерактивный Canvas |
| [android-view-measurement.md](android-view-measurement.md) | Как размеры влияют на touch области |
| [android-ui-views.md](android-ui-views.md) | Системные view с готовой touch обработкой |

---

## Проверь себя

1. Что произойдёт, если onTouchEvent вернёт false в ACTION_DOWN?
2. Какой action получит ребёнок, когда родитель начинает перехватывать?
3. Чем pointer index отличается от pointer ID?
4. Почему onDown() в GestureDetector должен возвращать true?
5. Когда нужно вызывать computeCurrentVelocity() — до или после ACTION_UP?
6. Как ребёнок может запретить родителю перехватывать события?

---

## Источники

- [Android Developers — Manage touch events in ViewGroup](https://developer.android.com/develop/ui/views/touch-and-input/gestures/viewgroup)
- [Android Developers — Handle multi-touch gestures](https://developer.android.com/develop/ui/views/touch-and-input/gestures/multi)
- [Android Developers — Detect common gestures](https://developer.android.com/develop/ui/views/touch-and-input/gestures/detector)
- [Android Developers — Track touch movements](https://developer.android.com/develop/ui/views/touch-and-input/gestures/movement)
- [droidcon — Android Touch System](https://www.droidcon.com/2022/02/11/android-touch-system-part-1-touch-functions-and-the-view-hierarchy/)
- [Android Design Patterns — Nested Scrolling](https://www.androiddesignpatterns.com/2018/01/experimenting-with-nested-scrolling.html)

---

*Проверено: 2026-01-09 | На основе официальной документации Android*

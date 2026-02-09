---
title: "View Measurement: onMeasure и MeasureSpec"
created: 2025-12-25
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [constraint-solving, tree-traversal, layout-algorithm, memoization]
research: "[[2025-12-25-android-view-measurement]]"
tags:
  - android
  - view
  - measurement
  - viewgroup
  - layout
  - performance
related:
  - "[[android-custom-view-fundamentals]]"
  - "[[android-ui-views]]"
  - "[[android-view-rendering-pipeline]]"
---

# View Measurement: onMeasure и MeasureSpec

View Measurement — первый этап rendering pipeline, определяющий размеры всех View в иерархии. Без правильного измерения View либо занимает неверный размер, либо не отображается вовсе. Для ViewGroup это ещё сложнее: нужно измерить детей, учесть их margins, и только потом определить собственный размер.

> **Prerequisites:**
> - [[android-custom-view-fundamentals]] — базовое понимание Custom Views
> - [[android-ui-views]] — View hierarchy и LayoutParams
> - Понимание rendering pipeline (measure → layout → draw)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **MeasureSpec** | Compound integer: mode (2 бита) + size (30 бит) |
| **EXACTLY** | Точный размер от родителя (match_parent, 100dp) |
| **AT_MOST** | Максимальный размер (wrap_content) |
| **UNSPECIFIED** | Нет ограничений (ScrollView) |
| **setMeasuredDimension()** | Метод для установки результата измерения |
| **measureChild()** | Измерение ребёнка без учёта его margins |
| **measureChildWithMargins()** | Измерение ребёнка с учётом margins |
| **Double Taxation** | Многократные проходы measure/layout |
| **resolveSize()** | Helper для применения constraints к желаемому размеру |

---

## ПОЧЕМУ: Глубокое понимание системы измерений

### Почему MeasureSpec упакован в int, а не в отдельный класс?

**Историческая и performance причина:** Android был создан для устройств с ограниченными ресурсами (2008 год — 128MB RAM типичный смартфон). Каждый View в иерархии проходит измерение, а создание объектов на heap создаёт GC pressure.

```kotlin
// Если бы MeasureSpec был классом:
class MeasureSpec(val mode: Mode, val size: Int)  // 16+ байт на объект

// При иерархии 100 Views × 2 dimension (width + height):
// 200 аллокаций × 16 байт = 3200 байт мусора за ОДИН проход measure

// Реальность: primitive int = 4 байта на stack, нет аллокаций
val measureSpec: Int = MeasureSpec.makeMeasureSpec(size, mode)
```

**Bit-packing layout:**
```
┌────────────────────────────────────────────────────────────┐
│ MeasureSpec (32-bit integer):                              │
│                                                            │
│ ┌──────────┬───────────────────────────────────────────┐   │
│ │ Mode     │                  Size                     │   │
│ │ (2 bits) │               (30 bits)                   │   │
│ └──────────┴───────────────────────────────────────────┘   │
│                                                            │
│ Mode bits:                                                 │
│ - 00: UNSPECIFIED (0 << 30)                                │
│ - 01: EXACTLY     (1 << 30)                                │
│ - 10: AT_MOST     (2 << 30)                                │
│                                                            │
│ Size: максимум 2^30 - 1 = 1,073,741,823 пикселей          │
│       (~35,791 дюймов при 30,000 dpi)                      │
└────────────────────────────────────────────────────────────┘
```

30 бит для size означает максимум ~1 миллиард пикселей. Даже 8K дисплей (7680×4320) — это всего 33 миллиона пикселей, так что запаса хватает на десятилетия.

### Почему onMeasure вызывается несколько раз?

**Причина 1: Constraint solving требует итераций**

View hierarchy — это система constraints (ограничений). Родитель не знает, сколько места нужно детям, пока не спросит. Дети не знают точный размер, пока родитель не скажет constraints.

```kotlin
// Пример: LinearLayout с weights
// Проход 1: измеряем без weights, считаем "лишнее" место
// Проход 2: распределяем лишнее место по weights

// RelativeLayout ещё сложнее:
// Проход 1: измеряем View, которые не зависят от других
// Проход 2: измеряем View, которые зависят от первых
```

**Причина 2: Parent может изменить решение**

```kotlin
// Parent спрашивает ребёнка: "сколько тебе нужно при AT_MOST 500px?"
// Ребёнок отвечает: "мне нужно 300px"
// Parent: "окей, тогда я дам тебе EXACTLY 300px"
// → второй вызов onMeasure с другим MeasureSpec

// Это нормально и не является ошибкой!
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Можно вызываться 2-3 раза за один layout pass
    // НЕ храни состояние между вызовами!
}
```

**Причина 3: requestLayout() триггерит полный re-measure**

```kotlin
fun updateContent(newData: Data) {
    this.data = newData
    // Размер может измениться → нужен re-measure
    requestLayout()  // invalidate + measure + layout
}
```

### Почему UNSPECIFIED существует и когда используется?

**Проблема:** ScrollView не знает, насколько длинный контент внутри. Если он скажет ребёнку "максимум 800px" (AT_MOST), ребёнок ограничится этим размером. Но контент может быть 5000px!

```kotlin
// ScrollView измеряет ребёнка с UNSPECIFIED:
child.measure(
    MeasureSpec.makeMeasureSpec(widthSize, MeasureSpec.EXACTLY),
    MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)  // ← нет ограничения по высоте
)

// Ребёнок получает свободу определить собственную высоту
// → RecyclerView может сказать "мне нужно 5000px"
// → ScrollView делает scrollable контент
```

**Важно для Custom View:**
```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val heightMode = MeasureSpec.getMode(heightMeasureSpec)
    val desiredHeight = calculateContentHeight()

    val finalHeight = when (heightMode) {
        MeasureSpec.EXACTLY -> MeasureSpec.getSize(heightMeasureSpec)
        MeasureSpec.AT_MOST -> minOf(desiredHeight, MeasureSpec.getSize(heightMeasureSpec))
        MeasureSpec.UNSPECIFIED -> desiredHeight  // ← Свобода! Берём желаемый размер
        else -> desiredHeight
    }

    setMeasuredDimension(width, finalHeight)
}
```

### Почему getMeasuredWidth() ≠ getWidth()?

**Жизненный цикл значений:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Timeline:                                                       │
│                                                                 │
│ onMeasure()                   onLayout()                        │
│      │                            │                             │
│      ▼                            ▼                             │
│ setMeasuredDimension(200, 100)   layout(0, 0, 200, 100)         │
│      │                            │                             │
│      ▼                            ▼                             │
│ getMeasuredWidth() = 200      getWidth() = 200                  │
│ getWidth() = 0 (!)            getWidth() = 200 ✓                │
│                                                                 │
│ getMeasuredWidth() — результат ИЗМЕРЕНИЯ (желаемый размер)      │
│ getWidth() — результат LAYOUT (фактический размер)              │
│                                                                 │
│ Обычно равны, но parent может дать другой размер в layout()!    │
└─────────────────────────────────────────────────────────────────┘
```

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    setMeasuredDimension(200, 100)

    Log.d("Size", "measured: ${measuredWidth}x${measuredHeight}")  // 200x100
    Log.d("Size", "actual: ${width}x${height}")                    // 0x0 ← ещё не layout!
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    Log.d("Size", "measured: ${measuredWidth}x${measuredHeight}")  // 200x100
    Log.d("Size", "actual: ${width}x${height}")                    // r-l x b-t
}
```

---

### Проблема: View не отображается или имеет неверный размер

```kotlin
// Частая проблема: View возвращает 0 размер
val width = customView.width  // 0 — почему?
// Потому что измерение ещё не произошло!

// Другая проблема: wrap_content = match_parent
class BadView(context: Context) : View(context) {
    // Без переопределения onMeasure:
    // - default размер = 100x100 (не то, что ожидали)
    // - wrap_content работает как match_parent
}
```

### Когда нужно понимать измерения

| Ситуация | Почему важно |
|----------|--------------|
| Custom View с динамическим контентом | Определить размер на основе контента |
| Custom ViewGroup (FlowLayout, Grid) | Измерить детей, рассчитать позиции |
| Performance проблемы (jank) | Понять double taxation |
| wrap_content не работает | Дефолтный onMeasure не знает реальный размер |
| View внутри ScrollView | Понять UNSPECIFIED mode |

### Аналогия: Строительство дома

> **MeasureSpec** — это требования заказчика:
> - **EXACTLY**: "Комната должна быть ровно 20м²"
> - **AT_MOST**: "Комната может быть до 20м², но не больше"
> - **UNSPECIFIED**: "Сделай комнату такой, какая нужна"
>
> **onMeasure** — это архитектор, который смотрит на требования и решает реальный размер.

---

## ЧТО: Как работает измерение

### MeasureSpec — 3 режима

MeasureSpec — это compound integer, содержащий mode и size:

```kotlin
// MeasureSpec = mode (2 старших бита) + size (30 бит)
val widthMode = MeasureSpec.getMode(widthMeasureSpec)
val widthSize = MeasureSpec.getSize(widthMeasureSpec)
```

| Mode | XML атрибут | Значение |
|------|-------------|----------|
| **EXACTLY** | `match_parent`, `100dp` | View ДОЛЖЕН использовать этот размер |
| **AT_MOST** | `wrap_content` | View может быть МЕНЬШЕ этого размера |
| **UNSPECIFIED** | ScrollView child | View решает сам, нет ограничений |

### Откуда приходит MeasureSpec

```
┌─────────────────────────────────────────────────────────────────┐
│  РОДИТЕЛЬ решает MeasureSpec для ребёнка на основе:             │
│                                                                 │
│  1. Собственного размера (сколько места есть)                   │
│  2. LayoutParams ребёнка (что ребёнок хочет)                    │
│                                                                 │
│  ┌─────────────────┬─────────────┬──────────────────────┐       │
│  │ LayoutParams    │ Parent mode │ Child mode           │       │
│  ├─────────────────┼─────────────┼──────────────────────┤       │
│  │ MATCH_PARENT    │ EXACTLY     │ EXACTLY (parent size)│       │
│  │ MATCH_PARENT    │ AT_MOST     │ AT_MOST (parent size)│       │
│  │ WRAP_CONTENT    │ EXACTLY     │ AT_MOST (parent size)│       │
│  │ WRAP_CONTENT    │ AT_MOST     │ AT_MOST (parent size)│       │
│  │ 100dp           │ любой       │ EXACTLY (100dp)      │       │
│  └─────────────────┴─────────────┴──────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### setMeasuredDimension() — контракт

**ОБЯЗАТЕЛЬНО** вызвать в конце `onMeasure()`:

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // ... логика измерения ...

    // ОБЯЗАТЕЛЬНО! Без этого — IllegalStateException
    setMeasuredDimension(calculatedWidth, calculatedHeight)
}
```

После вызова доступны:
- `getMeasuredWidth()` — измеренная ширина
- `getMeasuredHeight()` — измеренная высота

**ВАЖНО:** `getWidth()` и `getHeight()` возвращают 0 в onMeasure! Они устанавливаются только после `layout()`.

### resolveSize() — helper для constraints

```kotlin
// resolveSize применяет MeasureSpec к желаемому размеру
val finalWidth = resolveSize(desiredWidth, widthMeasureSpec)

// Эквивалентно:
val finalWidth = when (MeasureSpec.getMode(widthMeasureSpec)) {
    MeasureSpec.EXACTLY -> MeasureSpec.getSize(widthMeasureSpec)
    MeasureSpec.AT_MOST -> minOf(desiredWidth, MeasureSpec.getSize(widthMeasureSpec))
    else -> desiredWidth  // UNSPECIFIED
}
```

---

## КАК: Реализация onMeasure

### Простой Custom View

```kotlin
class CircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var radius = 50f.dpToPx()

    // ═══════════════════════════════════════════════════════════════
    // onMeasure: определяем размер View
    // КОНТРАКТ: ВСЕГДА вызвать setMeasuredDimension() в конце
    // ═══════════════════════════════════════════════════════════════
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // 1. Определяем желаемый размер (диаметр + padding)
        val desiredSize = (radius * 2 + paddingLeft + paddingRight).toInt()

        // 2. Применяем constraints от родителя
        val width = resolveSize(desiredSize, widthMeasureSpec)
        val height = resolveSize(desiredSize, heightMeasureSpec)

        // 3. Для круга берём минимальный размер
        val size = minOf(width, height)

        // 4. ОБЯЗАТЕЛЬНО вызываем — иначе crash
        setMeasuredDimension(size, size)
    }
}
```

### Детальная обработка MeasureSpec

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Декодируем MeasureSpec
    val widthMode = MeasureSpec.getMode(widthMeasureSpec)
    val widthSize = MeasureSpec.getSize(widthMeasureSpec)
    val heightMode = MeasureSpec.getMode(heightMeasureSpec)
    val heightSize = MeasureSpec.getSize(heightMeasureSpec)

    // Вычисляем желаемый размер на основе контента
    val desiredWidth = calculateContentWidth() + paddingLeft + paddingRight
    val desiredHeight = calculateContentHeight() + paddingTop + paddingBottom

    // Применяем constraints
    val finalWidth = when (widthMode) {
        MeasureSpec.EXACTLY -> widthSize        // Родитель сказал точный размер
        MeasureSpec.AT_MOST -> minOf(desiredWidth, widthSize)  // Не больше родителя
        else -> desiredWidth                     // UNSPECIFIED — сколько хотим
    }

    val finalHeight = when (heightMode) {
        MeasureSpec.EXACTLY -> heightSize
        MeasureSpec.AT_MOST -> minOf(desiredHeight, heightSize)
        else -> desiredHeight
    }

    setMeasuredDimension(finalWidth, finalHeight)
}
```

---

## КАК: Custom ViewGroup

### measureChild vs measureChildWithMargins

| Метод | Учитывает margins ребёнка | Требует |
|-------|--------------------------|---------|
| `measureChild()` | Нет | `LayoutParams` |
| `measureChildWithMargins()` | Да | `MarginLayoutParams` |

```kotlin
// measureChild — НЕ учитывает margins
measureChild(child, widthMeasureSpec, heightMeasureSpec)
// child.measuredWidth = размер контента

// measureChildWithMargins — учитывает margins
measureChildWithMargins(child, widthMeasureSpec, 0, heightMeasureSpec, 0)
// child.measuredWidth = размер контента (margins вычтены из доступного места)
```

### Поддержка MarginLayoutParams

```kotlin
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    // ═══════════════════════════════════════════════════════════════
    // ОБЯЗАТЕЛЬНО для поддержки layout_margin в XML
    // Без этого layout_marginLeft/Right/Top/Bottom игнорируются!
    // ═══════════════════════════════════════════════════════════════
    override fun generateLayoutParams(attrs: AttributeSet?): LayoutParams {
        return MarginLayoutParams(context, attrs)
    }

    override fun generateLayoutParams(p: LayoutParams?): LayoutParams {
        return MarginLayoutParams(p)
    }

    override fun generateDefaultLayoutParams(): LayoutParams {
        return MarginLayoutParams(
            LayoutParams.WRAP_CONTENT,
            LayoutParams.WRAP_CONTENT
        )
    }

    override fun checkLayoutParams(p: LayoutParams?): Boolean {
        return p is MarginLayoutParams
    }
}
```

### FlowLayout — полная реализация

```kotlin
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    private var horizontalSpacing = 8.dpToPx().toInt()
    private var verticalSpacing = 8.dpToPx().toInt()

    // ═══════════════════════════════════════════════════════════════
    // onMeasure для ViewGroup:
    // 1. Измерить всех детей
    // 2. Рассчитать собственный размер на основе детей
    // 3. Вызвать setMeasuredDimension
    // ═══════════════════════════════════════════════════════════════
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val maxWidth = MeasureSpec.getSize(widthMeasureSpec) - paddingLeft - paddingRight

        var currentRowWidth = 0
        var currentRowHeight = 0
        var totalHeight = 0
        var maxRowWidth = 0

        // Проходим по всем детям
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            // Измеряем ребёнка с учётом margins
            measureChildWithMargins(child, widthMeasureSpec, 0, heightMeasureSpec, 0)

            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            // Проверяем, помещается ли в текущую строку
            if (currentRowWidth + childWidth > maxWidth && currentRowWidth > 0) {
                // Переносим на новую строку
                maxRowWidth = maxOf(maxRowWidth, currentRowWidth - horizontalSpacing)
                totalHeight += currentRowHeight + verticalSpacing
                currentRowWidth = 0
                currentRowHeight = 0
            }

            currentRowWidth += childWidth + horizontalSpacing
            currentRowHeight = maxOf(currentRowHeight, childHeight)
        }

        // Добавляем последнюю строку
        maxRowWidth = maxOf(maxRowWidth, currentRowWidth - horizontalSpacing)
        totalHeight += currentRowHeight

        // Добавляем padding
        val finalWidth = maxRowWidth + paddingLeft + paddingRight
        val finalHeight = totalHeight + paddingTop + paddingBottom

        // Применяем constraints и устанавливаем размер
        setMeasuredDimension(
            resolveSize(finalWidth, widthMeasureSpec),
            resolveSize(finalHeight, heightMeasureSpec)
        )
    }

    // ═══════════════════════════════════════════════════════════════
    // onLayout: позиционируем детей
    // Вызывается ПОСЛЕ onMeasure, размеры детей уже известны
    // ═══════════════════════════════════════════════════════════════
    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        val maxWidth = width - paddingLeft - paddingRight

        var currentLeft = paddingLeft
        var currentTop = paddingTop
        var currentRowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth
            val childHeight = child.measuredHeight
            val totalChildWidth = childWidth + lp.leftMargin + lp.rightMargin

            // Проверяем, помещается ли
            if (currentLeft + totalChildWidth > paddingLeft + maxWidth && currentLeft > paddingLeft) {
                currentLeft = paddingLeft
                currentTop += currentRowHeight + verticalSpacing
                currentRowHeight = 0
            }

            // Позиционируем ребёнка
            val childLeft = currentLeft + lp.leftMargin
            val childTop = currentTop + lp.topMargin

            child.layout(
                childLeft,
                childTop,
                childLeft + childWidth,
                childTop + childHeight
            )

            currentLeft += totalChildWidth + horizontalSpacing
            currentRowHeight = maxOf(currentRowHeight, childHeight + lp.topMargin + lp.bottomMargin)
        }
    }

    override fun generateLayoutParams(attrs: AttributeSet?) = MarginLayoutParams(context, attrs)
    override fun generateLayoutParams(p: LayoutParams?) = MarginLayoutParams(p)
    override fun generateDefaultLayoutParams() = MarginLayoutParams(WRAP_CONTENT, WRAP_CONTENT)
    override fun checkLayoutParams(p: LayoutParams?) = p is MarginLayoutParams

    private fun Float.dpToPx() = this * resources.displayMetrics.density
}
```

---

## КАК: Performance — избежать Double Taxation

### Что такое Double Taxation

**Double Taxation** — когда framework выполняет measure/layout несколько раз:

```
┌─────────────────────────────────────────────────────────────────┐
│  НОРМАЛЬНЫЙ ПРОХОД:                                             │
│  Parent.measure() → Child1.measure() → Child2.measure() → DONE  │
│                                                                 │
│  DOUBLE TAXATION:                                               │
│  Parent.measure() → Child1.measure() → Child2.measure()         │
│       ↓                                                         │
│  Parent.measure() → Child1.measure() → Child2.measure() → DONE  │
│                                                                 │
│  В глубоких иерархиях: 2^depth проходов!                        │
└─────────────────────────────────────────────────────────────────┘
```

### Layouts, вызывающие Double Taxation

| Layout | Когда происходит |
|--------|-----------------|
| `RelativeLayout` | Почти всегда (для relative positioning) |
| `LinearLayout` horizontal | При использовании weights |
| `LinearLayout` vertical | С `measureWithLargestChild` |
| `GridLayout` | С weights или Gravity |

### Решение: ConstraintLayout

```xml
<!-- ПЛОХО: вложенные layouts = double taxation умножается -->
<LinearLayout android:orientation="vertical">
    <LinearLayout android:orientation="horizontal">
        <RelativeLayout>
            <!-- 3 уровня × 2 прохода = 8 проходов measure -->
        </RelativeLayout>
    </LinearLayout>
</LinearLayout>

<!-- ХОРОШО: плоская иерархия с ConstraintLayout -->
<ConstraintLayout>
    <!-- 1 уровень = 1 проход measure -->
    <View app:layout_constraintTop_toTopOf="parent" />
    <View app:layout_constraintStart_toEndOf="@id/other" />
</ConstraintLayout>
```

### Рейтинг layouts по эффективности

1. **FrameLayout** — самый быстрый (1 проход, простое позиционирование)
2. **ConstraintLayout** — эффективен для сложных layouts (1-2 прохода)
3. **LinearLayout без weights** — быстрый (1 проход)
4. **LinearLayout с weights** — медленнее (2 прохода)
5. **RelativeLayout** — медленный (2+ прохода)

### Custom ViewGroup — лучшая производительность

Для специфичных layouts custom ViewGroup эффективнее:

```kotlin
// Custom ViewGroup знает структуру детей
// → может измерить за 1 проход
// → нет double taxation
// → оптимальная производительность

class OptimizedGridLayout : ViewGroup {
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Знаем, что все дети одинакового размера
        // → измеряем только первого, остальные получают тот же размер
        measureChild(getChildAt(0), widthMeasureSpec, heightMeasureSpec)
        val childSize = getChildAt(0).measuredWidth

        // Быстрый расчёт собственного размера
        val columns = 3
        val rows = ceil(childCount / 3.0).toInt()
        setMeasuredDimension(
            childSize * columns,
            childSize * rows
        )
    }
}
```

---

## КОГДА НЕ: Ограничения и альтернативы

### 1. NestedScrollView + wrap_content = проблемы

```kotlin
// ПРОБЛЕМА: NestedScrollView передаёт UNSPECIFIED детям
// RecyclerView с wrap_content создаёт ВСЕ item'ы сразу

// ❌ ПЛОХО
<NestedScrollView>
    <RecyclerView
        android:layout_height="wrap_content" />
    <!-- Все item'ы в памяти = нет recycling = memory issues -->
</NestedScrollView>

// ✅ ХОРОШО: фиксированная высота или ConcatAdapter
<RecyclerView
    android:layout_height="match_parent">
    <!-- Header/Footer через ConcatAdapter -->
</RecyclerView>
```

### 2. Compose — проще и быстрее

```kotlin
// В Compose: intrinsic measurements встроены
@Composable
fun FlowRow(content: @Composable () -> Unit) {
    Layout(content = content) { measurables, constraints ->
        // Измерение детей
        val placeables = measurables.map { it.measure(constraints) }

        // Расчёт позиций
        layout(width, height) {
            placeables.forEach { it.place(x, y) }
        }
    }
}

// Или готовый FlowRow из accompanist/compose-foundation
FlowRow {
    chips.forEach { Chip(it) }
}
```

### 3. Когда достаточно ConstraintLayout

Не пишите custom ViewGroup если:
- Задача решается ConstraintLayout + Barrier/Guideline
- Нет специфических performance требований
- Layout не будет переиспользоваться

---

## Проверь себя

1. **Что произойдёт, если не вызвать setMeasuredDimension()?**
   - `IllegalStateException` — это обязательный контракт onMeasure

2. **В чём разница между EXACTLY и AT_MOST?**
   - EXACTLY: View ДОЛЖЕН использовать указанный размер
   - AT_MOST: View может быть МЕНЬШЕ указанного размера

3. **Почему measureChildWithMargins требует MarginLayoutParams?**
   - Он вычитает margins из доступного места, нужны значения margins

4. **Что такое double taxation и как его избежать?**
   - Многократные проходы measure. Решение: ConstraintLayout или custom ViewGroup

5. **Почему getWidth() возвращает 0 в onMeasure?**
   - getWidth() устанавливается в layout(), а onMeasure вызывается раньше. Используйте getMeasuredWidth()

---

## Intrinsic Measurements: Chicken-and-Egg Problem

### Проблема: циклическая зависимость размеров

```kotlin
// Классическая проблема: TableRow
// - Каждая ячейка хочет знать ширину столбца (чтобы центрироваться)
// - Ширина столбца зависит от самой широкой ячейки
// - Но самая широкая ячейка неизвестна до измерения всех!

// Решение: Intrinsic Dimensions
// Спрашиваем View: "какой минимальный/максимальный размер тебе нужен?"
```

### getMinimumWidth/Height и Intrinsic Size

```kotlin
// View предоставляет intrinsic размеры:
view.minimumWidth      // Минимальная ширина (из XML или setMinimumWidth)
view.minimumHeight     // Минимальная высота

// ImageView имеет intrinsic size от Drawable:
imageView.drawable?.intrinsicWidth   // Размер картинки в пикселях
imageView.drawable?.intrinsicHeight
```

### Compose: встроенная поддержка Intrinsic Measurements

```kotlin
@Composable
fun IntrinsicExample() {
    Row(modifier = Modifier.height(IntrinsicSize.Min)) {
        // Все дети получают минимально необходимую высоту
        // Решает chicken-and-egg problem декларативно
        Text("Short")
        Divider(
            modifier = Modifier
                .fillMaxHeight()  // Заполнит высоту Row
                .width(1.dp)
        )
        Text("Longer text here")
    }
}
```

### Custom View с Intrinsic Support

```kotlin
class AspectRatioImageView(context: Context) : ImageView(context) {
    private val aspectRatio = 16f / 9f

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val heightMode = MeasureSpec.getMode(heightMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)
        val heightSize = MeasureSpec.getSize(heightMeasureSpec)

        val (width, height) = when {
            // Ширина известна → высота по aspect ratio
            widthMode == MeasureSpec.EXACTLY -> {
                widthSize to (widthSize / aspectRatio).toInt()
            }
            // Высота известна → ширина по aspect ratio
            heightMode == MeasureSpec.EXACTLY -> {
                (heightSize * aspectRatio).toInt() to heightSize
            }
            // Оба wrap_content → используем intrinsic size drawable
            else -> {
                val intrinsicWidth = drawable?.intrinsicWidth ?: 100
                val intrinsicHeight = drawable?.intrinsicHeight ?: 100
                intrinsicWidth to intrinsicHeight
            }
        }

        setMeasuredDimension(
            resolveSize(width, widthMeasureSpec),
            resolveSize(height, heightMeasureSpec)
        )
    }
}
```

---

## Advanced: Measure Cache и Optimization

### Как View кэширует измерения

```kotlin
// View хранит последний MeasureSpec и результат:
private var mOldWidthMeasureSpec: Int = 0
private var mOldHeightMeasureSpec: Int = 0

// При повторном measure с тем же spec:
fun measure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val cacheIndex = if (forceLayout) -1 else
        mMeasureCache?.indexOfKey(key) ?: -1

    if (cacheIndex >= 0) {
        // Cache hit! Используем закэшированный размер
        setMeasuredDimensionRaw(cachedWidth, cachedHeight)
        return
    }

    // Cache miss — вызываем onMeasure
    onMeasure(widthMeasureSpec, heightMeasureSpec)
}
```

### Когда кэш инвалидируется

| Событие | Инвалидация |
|---------|-------------|
| `requestLayout()` | Полная инвалидация |
| `setLayoutParams()` | Полная инвалидация |
| Parent изменил constraints | Новый MeasureSpec = cache miss |
| `forceLayout()` | Принудительный re-measure |

### Профилирование measure performance

```kotlin
// Systrace для анализа measure time
Debug.startMethodTracing("measure_trace")
rootView.measure(widthSpec, heightSpec)
Debug.stopMethodTracing()

// Layout Inspector показывает:
// - Количество measure passes
// - Время каждого View
// - Double taxation hotspots
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "onMeasure вызывается один раз" | onMeasure может вызываться 2-5+ раз за один layout pass. RelativeLayout, LinearLayout с weights, и сложные иерархии провоцируют множественные вызовы. Не храните mutable state между вызовами! |
| "getMeasuredWidth() = getWidth() всегда" | getMeasuredWidth() — желаемый размер после measure. getWidth() — фактический размер после layout. Parent может дать другой размер! В onMeasure getWidth() = 0 |
| "WRAP_CONTENT означает 'минимальный размер'" | WRAP_CONTENT передаётся как AT_MOST с размером родителя. View может взять ВЕСЬ доступный размер если не переопределит onMeasure. Default implementation View = 100x100 |
| "MeasureSpec — это класс" | MeasureSpec — primitive int с bit-packed mode и size. Создан для zero-allocation performance на старых устройствах. Макс size = 2^30 пикселей |
| "setMeasuredDimension можно не вызывать" | Обязательный контракт! Без вызова — IllegalStateException. Родитель полагается на measuredWidth/Height для layout |
| "Вложенные LinearLayout — нормально" | Каждый уровень LinearLayout с weights удваивает measure passes. 5 уровней = 32 прохода. Используйте ConstraintLayout или custom ViewGroup |
| "ConstraintLayout всегда быстрее" | Для простых layouts (2-3 View) FrameLayout/LinearLayout быстрее. ConstraintLayout имеет overhead на solver. Оптимален для 5+ Views с complex constraints |
| "Custom ViewGroup сложно писать" | Базовый ViewGroup требует ~50 строк кода. generateLayoutParams(), onMeasure(), onLayout(). FlowLayout — хороший учебный пример |
| "requestLayout() — дорогая операция" | requestLayout() только помечает View dirty. Фактическая работа откладывается до следующего VSYNC. Но чрезмерные вызовы всё равно создают overhead |
| "resolveSize() обязателен" | resolveSize() — helper, не requirement. Можно обрабатывать MeasureSpec вручную. Но helper уменьшает boilerplate и ошибки |

---

## CS-фундамент

| CS-концепция | Применение в View Measurement |
|--------------|------------------------------|
| **Constraint Satisfaction Problem** | View measurement — это CSP: каждый View имеет constraints (MeasureSpec), нужно найти размеры, удовлетворяющие всем. ConstraintLayout использует Cassowary algorithm для решения |
| **Tree Traversal (DFS)** | Measure проходит иерархию depth-first: родитель → дети → родитель (постфиксный обход). Каждый узел измеряется после всех детей |
| **Memoization / Caching** | View кэширует результат measure для того же MeasureSpec. Cache key = widthSpec + heightSpec. Избегает повторных вычислений |
| **Bit Manipulation** | MeasureSpec использует bit packing: 2 бита mode + 30 бит size в одном int. Экономит память и GC pressure |
| **Two-Pass Algorithm** | Некоторые layouts (RelativeLayout, LinearLayout с weights) требуют двух проходов: первый для сбора constraints, второй для финального размера |
| **Fixed-Point Iteration** | Double taxation — это итеративное приближение к решению. Каждый проход уточняет размеры пока система не сойдётся |
| **Layout Algorithm** | onLayout использует результаты measurement для positioning. Box model: content + padding + margin. Coordinate system: top-left origin |
| **Separation of Concerns** | Три фазы разделены: measure (размер), layout (позиция), draw (отрисовка). Каждая фаза имеет свой lifecycle callback |
| **Lazy Evaluation** | measure/layout откладываются до VSYNC (Choreographer). Батчинг множества requestLayout() в один проход |
| **Contract Programming** | setMeasuredDimension() — обязательный контракт onMeasure. Нарушение контракта = runtime exception. Design by Contract pattern |

---

## Связанные материалы

| Материал | Зачем изучать |
|----------|---------------|
| [[android-custom-view-fundamentals]] | Базовые концепции Custom Views |
| [[android-canvas-drawing]] | Как рисовать после измерения |
| [[android-view-rendering-pipeline]] | Полный цикл measure → layout → draw |
| [[android-compose]] | Современная альтернатива с Layout composable |

---

## Источники

| Источник | Тип | Вклад |
|----------|-----|-------|
| [How Android draws views](https://developer.android.com/guide/topics/ui/how-android-draws) | Official | Measure/Layout/Draw pipeline |
| [View.MeasureSpec](https://developer.android.com/reference/android/view/View.MeasureSpec) | Official | MeasureSpec modes |
| [Performance and view hierarchies](https://developer.android.com/topic/performance/rendering/optimizing-view-hierarchies) | Official | Double taxation |
| [Custom View: mastering onMeasure](https://medium.com/@quiro91/custom-view-mastering-onmeasure-a0a0bb11784d) | Expert Blog | onMeasure best practices |
| [ViewGroup.MarginLayoutParams](https://developer.android.com/reference/android/view/ViewGroup.MarginLayoutParams) | Official | MarginLayoutParams API |
| [The Life Cycle of a View](https://proandroiddev.com/the-life-cycle-of-a-view-in-android-6a2c4665b95e) | Technical | View lifecycle |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

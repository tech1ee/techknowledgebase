---
title: "Cross-Platform: Graphics — Core Animation vs RenderThread"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - graphics
  - rendering
  - animation
  - type/comparison
  - level/intermediate
reading_time: 37
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-memory-management]]"
related:
  - "[[ios-graphics-fundamentals]]"
  - "[[android-graphics-apis]]"
  - "[[ios-view-rendering]]"
---

# Cross-Platform: Graphics — Core Animation vs RenderThread

## TL;DR

| Аспект | iOS (Core Animation) | Android (RenderThread/Skia) |
|--------|---------------------|----------------------------|
| **Rendering Engine** | Core Animation + Metal | RenderThread + Skia + Vulkan/OpenGL |
| **Отдельный поток** | Render Server (отдельный процесс) | RenderThread (отдельный поток) |
| **Модель композиции** | Layer-based (CALayer) | View-based + RenderNode |
| **Implicit animations** | Да, встроены в систему | Нет, требуют явного кода |
| **Display refresh** | CADisplayLink | Choreographer |
| **Offscreen rendering** | Дорого (layer rasterization) | Дорого (saveLayer) |
| **120fps поддержка** | ProMotion (адаптивная) | Зависит от OEM |
| **GPU API** | Metal | Vulkan / OpenGL ES |
| **Основная метрика** | Frame drop в Instruments | Jank в Perfetto/Systrace |

---


## Теоретические основы

### Формальное определение

> **Графический рендеринг** — процесс преобразования описания сцены (scene graph) в растровое изображение на экране устройства, включающий layout, paint и compositing (Foley et al., 1990, Computer Graphics: Principles and Practice).

### Rendering Pipeline мобильных платформ

| Этап | iOS (Core Animation) | Android (RenderThread) |
|------|---------------------|----------------------|
| **Layout** | Auto Layout (Cassowary) | Measure → Layout (View tree) |
| **Paint** | Core Graphics (Quartz 2D) | Canvas (Skia) |
| **Compositing** | Core Animation (GPU) | RenderThread (GPU) |
| **Display** | CADisplayLink (ProMotion) | Choreographer (VSYNC) |

### GPU Compositing Model

Обе платформы используют **GPU-accelerated compositing**:

```
UI Thread: Layout + Paint → Layers
GPU Thread: Composite Layers → Frame Buffer → Display
```

Ключевой принцип — **layer isolation**: изменение одного слоя не требует перерисовки остальных. iOS Core Animation и Android RenderThread оптимизируют это по-разному.

### Кросс-платформенные rendering engine'ы

| Engine | Используется в | Модель | Плюсы | Минусы |
|--------|---------------|--------|-------|--------|
| **Skia** | Flutter, Android, Chrome | Canvas-based | Единый рендеринг | Не нативный look |
| **Impeller** | Flutter (iOS) | Metal-first | Нет shader compilation jank | Новый, менее зрелый |
| **Skiko** | Compose MP | Skia wrapper for Kotlin | Compose API | Binary size overhead |
| **Native** | KMP + native UI | Platform renderer | Нативный look & feel | Разный код для UI |

> **CS-фундамент:** Рендеринг связан с [[cross-ui-declarative]] (что рендерим) и [[cross-performance-profiling]] (как измеряем). Теоретическая база — Computer Graphics (Foley et al., 1990), GPU Pipeline (Akenine-Möller et al., 2018).

## Архитектура Rendering Pipeline

### iOS: Core Animation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Thread                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Layout Pass │ -> │ Display Pass│ -> │ Commit Transaction  │  │
│  │ (layoutSub- │    │ (draw(_:))  │    │ (отправка в Render  │  │
│  │  views)     │    │             │    │  Server)            │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Render Server (отдельный процесс)            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Decode      │ -> │ Render      │ -> │ Display (VSync)     │  │
│  │ (распаковка │    │ (растеризация│   │ (вывод на экран)    │  │
│  │  данных)    │    │  + композит) │   │                     │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевые особенности iOS:**
- Render Server — отдельный системный процесс (`backboardd`)
- Анимации выполняются без участия Main Thread после commit
- CALayer — основной примитив композиции
- Implicit animations работают автоматически при изменении свойств

### Android: RenderThread Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Thread (UI Thread)                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Measure     │ -> │ Layout      │ -> │ Draw (запись в      │  │
│  │ (измерение) │    │ (позициони- │    │  DisplayList)       │  │
│  │             │    │  рование)   │    │                     │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RenderThread (с Android 5.0)                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Sync        │ -> │ Draw        │ -> │ Swap (отправка      │  │
│  │ (синхрони-  │    │ (Skia рас-  │    │  в SurfaceFlinger)  │  │
│  │  зация)     │    │  теризация) │    │                     │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              SurfaceFlinger (системный процесс)                  │
│         Композиция всех Surface + вывод на дисплей              │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевые особенности Android:**
- RenderThread работает в том же процессе, но отдельном потоке
- DisplayList (RenderNode) — оптимизированное представление draw-команд
- Skia — универсальный 2D rendering engine
- Vulkan/OpenGL ES используется для GPU-ускорения

---

## Core Animation vs RenderThread: Глубокое сравнение

### Модель слоёв

**iOS — CALayer:**
```swift
// Каждый UIView имеет backing CALayer
let layer = view.layer

// Свойства layer анимируются автоматически
layer.cornerRadius = 16
layer.shadowOpacity = 0.3
layer.shadowOffset = CGSize(width: 0, height: 4)

// Explicit animation
let animation = CABasicAnimation(keyPath: "transform.rotation")
animation.toValue = CGFloat.pi * 2
animation.duration = 1.0
layer.add(animation, forKey: "rotation")
```

**Android — RenderNode:**
```kotlin
// RenderNode создаётся автоматически для hardware-accelerated View
// Доступ через View.updateDisplayListIfDirty() — internal

// Animatable properties через View
view.translationX = 100f
view.alpha = 0.5f
view.rotation = 45f

// Или через ObjectAnimator
ObjectAnimator.ofFloat(view, "translationX", 0f, 100f).apply {
    duration = 300
    start()
}
```

### Offscreen Rendering

**iOS — когда срабатывает:**
```swift
// 🔴 Вызывает offscreen rendering:
layer.cornerRadius = 10
layer.masksToBounds = true  // В комбинации с cornerRadius!

layer.shadowPath = nil  // Без shadowPath
layer.shadowOpacity = 0.5

layer.shouldRasterize = true  // Если контент меняется

layer.mask = someMaskLayer

// ✅ Оптимизации:
// 1. Установить shadowPath явно
layer.shadowPath = UIBezierPath(roundedRect: bounds, cornerRadius: 10).cgPath

// 2. Использовать cornerRadius без masksToBounds если возможно
// 3. Использовать pre-rendered images для сложных форм
```

**Android — когда срабатывает:**
```kotlin
// 🔴 Вызывает offscreen rendering (saveLayer):
view.alpha = 0.5f  // Если есть overlapping children

canvas.saveLayer(bounds, paint)  // Явный saveLayer

// clipPath на complex path
canvas.clipPath(complexPath)

// 🔴 ViewOutlineProvider с complex shape
view.outlineProvider = object : ViewOutlineProvider() {
    override fun getOutline(view: View, outline: Outline) {
        // Сложный outline без convex path
    }
}

// ✅ Оптимизации:
// 1. Использовать View.LAYER_TYPE_HARDWARE для статичного контента
view.setLayerType(View.LAYER_TYPE_HARDWARE, null)

// 2. Установить hasOverlappingRendering = false если нет перекрытий
override fun hasOverlappingRendering() = false

// 3. Использовать Outline.setRoundRect() вместо setPath()
```

---

## 60fps и 120fps: Требования и реальность

### Временные бюджеты

| Refresh Rate | Frame Budget | Реальный бюджет* |
|--------------|--------------|------------------|
| 60 Hz | 16.67 ms | ~12-14 ms |
| 90 Hz | 11.11 ms | ~8-9 ms |
| 120 Hz | 8.33 ms | ~6-7 ms |

*Учитывая overhead системы и VSync

### iOS ProMotion

```swift
// Адаптивная частота кадров
// CADisplayLink автоматически адаптируется

let displayLink = CADisplayLink(target: self, selector: #selector(update))

// iOS 15+: предпочтительный frame rate
displayLink.preferredFrameRateRange = CAFrameRateRange(
    minimum: 60,
    maximum: 120,
    preferred: 120
)

displayLink.add(to: .main, forMode: .common)

@objc func update(_ displayLink: CADisplayLink) {
    // actualFrameRate показывает реальную частоту
    let fps = 1.0 / (displayLink.targetTimestamp - displayLink.timestamp)

    // Адаптируйте логику под текущий fps
    let delta = displayLink.targetTimestamp - displayLink.timestamp
    updateAnimation(delta: delta)
}
```

### Android Variable Refresh Rate

```kotlin
// Choreographer — единственный правильный способ синхронизации
val choreographer = Choreographer.getInstance()

choreographer.postFrameCallback(object : Choreographer.FrameCallback {
    override fun doFrame(frameTimeNanos: Long) {
        // frameTimeNanos — точное время начала кадра

        val deltaSeconds = (frameTimeNanos - lastFrameTime) / 1_000_000_000.0
        updateAnimation(deltaSeconds)

        lastFrameTime = frameTimeNanos
        choreographer.postFrameCallback(this)
    }
})

// Android 11+: Frame Rate API
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
    window.attributes = window.attributes.apply {
        preferredDisplayModeId = findHighRefreshRateMode()
    }
}
```

---

## Animation APIs: Сравнение

### Implicit vs Explicit

| Тип | iOS | Android |
|-----|-----|---------|
| **Implicit** | Встроено в CALayer | Нет |
| **Explicit declarative** | SwiftUI animations | Jetpack Compose animations |
| **Explicit imperative** | UIView.animate, CAAnimation | ObjectAnimator, ValueAnimator |
| **Physics-based** | UISpringTimingParameters | SpringAnimation (Jetpack) |
| **Interruptible** | Да, с iOS 10 | Да, с ValueAnimator |

### SwiftUI vs Compose: Animation APIs

**SwiftUI:**
```swift
struct AnimatedView: View {
    @State private var isExpanded = false

    var body: some View {
        VStack {
            Rectangle()
                .fill(.blue)
                .frame(height: isExpanded ? 200 : 100)
                // Implicit animation
                .animation(.spring(response: 0.3, dampingFraction: 0.7), value: isExpanded)

            Button("Toggle") {
                isExpanded.toggle()
            }
        }
    }
}

// Explicit animation
withAnimation(.easeInOut(duration: 0.3)) {
    isExpanded.toggle()
}

// Transaction для fine-grained control
var transaction = Transaction(animation: .spring())
transaction.disablesAnimations = shouldDisable
withTransaction(transaction) {
    isExpanded.toggle()
}
```

**Jetpack Compose:**
```kotlin
@Composable
fun AnimatedView() {
    var isExpanded by remember { mutableStateOf(false) }

    // animateDpAsState — implicit-like API
    val height by animateDpAsState(
        targetValue = if (isExpanded) 200.dp else 100.dp,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        )
    )

    Column {
        Box(
            Modifier
                .fillMaxWidth()
                .height(height)
                .background(Color.Blue)
        )

        Button(onClick = { isExpanded = !isExpanded }) {
            Text("Toggle")
        }
    }
}

// Более сложные анимации
val transition = updateTransition(isExpanded, label = "expand")
val height by transition.animateDp(label = "height") { expanded ->
    if (expanded) 200.dp else 100.dp
}
val alpha by transition.animateFloat(label = "alpha") { expanded ->
    if (expanded) 1f else 0.5f
}
```

---

## 6 Ошибок, Убивающих Performance

### Ошибка 1: Layout во время анимации

**iOS:**
```swift
// 🔴 ПЛОХО: вызывает layout на каждом кадре
UIView.animate(withDuration: 0.3) {
    self.view.frame.size.width = 200  // Triggers layout!
    self.view.layoutIfNeeded()  // Expensive!
}

// ✅ ХОРОШО: анимируйте transform
UIView.animate(withDuration: 0.3) {
    self.view.transform = CGAffineTransform(scaleX: 1.5, y: 1.5)
}
```

**Android:**
```kotlin
// 🔴 ПЛОХО: requestLayout() на каждом кадре
ValueAnimator.ofInt(100, 200).apply {
    addUpdateListener {
        view.layoutParams.width = it.animatedValue as Int
        view.requestLayout()  // Triggers full measure/layout!
    }
    start()
}

// ✅ ХОРОШО: используйте scaleX/scaleY
ObjectAnimator.ofFloat(view, "scaleX", 1f, 1.5f).start()
```

### Ошибка 2: Создание объектов в draw/render

**iOS:**
```swift
// 🔴 ПЛОХО
override func draw(_ rect: CGRect) {
    let path = UIBezierPath(roundedRect: bounds, cornerRadius: 10)  // Allocation!
    let color = UIColor(red: 0.5, green: 0.5, blue: 0.5, alpha: 1)  // Allocation!
    color.setFill()
    path.fill()
}

// ✅ ХОРОШО: кэшируйте объекты
private let path = UIBezierPath()
private let fillColor = UIColor.gray

override func draw(_ rect: CGRect) {
    path.removeAllPoints()
    path.append(UIBezierPath(roundedRect: bounds, cornerRadius: 10))
    fillColor.setFill()
    path.fill()
}
```

**Android:**
```kotlin
// 🔴 ПЛОХО
override fun onDraw(canvas: Canvas) {
    val paint = Paint().apply {  // Allocation каждый кадр!
        color = Color.BLUE
        style = Paint.Style.FILL
    }
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}

// ✅ ХОРОШО
private val paint = Paint().apply {
    color = Color.BLUE
    style = Paint.Style.FILL
}

override fun onDraw(canvas: Canvas) {
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
}
```

### Ошибка 3: Блокировка Main Thread I/O операциями

**iOS:**
```swift
// 🔴 ПЛОХО: синхронная загрузка изображения
func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
    let image = UIImage(contentsOfFile: imagePath)  // Blocks main thread!
    cell.imageView?.image = image
    return cell
}

// ✅ ХОРОШО: асинхронная загрузка
func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)

    Task {
        let image = await loadImage(from: imagePath)
        await MainActor.run {
            cell.imageView?.image = image
        }
    }
    return cell
}
```

**Android:**
```kotlin
// 🔴 ПЛОХО
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val bitmap = BitmapFactory.decodeFile(imagePath)  // Blocks UI thread!
    holder.imageView.setImageBitmap(bitmap)
}

// ✅ ХОРОШО: используйте Coil/Glide или coroutines
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    holder.imageView.load(imagePath) {
        crossfade(true)
        placeholder(R.drawable.placeholder)
    }
}
```

### Ошибка 4: Избыточная прозрачность и overdraw

**iOS:**
```swift
// 🔴 ПЛОХО: прозрачный backgroundColor
view.backgroundColor = .clear  // Causes blending

// Множество полупрозрачных слоёв
layer1.opacity = 0.8
layer2.opacity = 0.8  // Overdraw!
layer3.opacity = 0.8  // Overdraw!

// ✅ ХОРОШО
view.backgroundColor = .white  // Opaque
view.isOpaque = true

// Объединяйте слои где возможно
// Используйте Instruments → Core Animation → Color Blended Layers
```

**Android:**
```kotlin
// 🔴 ПЛОХО
<LinearLayout
    android:background="@color/white">
    <FrameLayout
        android:background="@color/white">  <!-- Overdraw! -->
        <ImageView
            android:background="@color/white"/>  <!-- Overdraw! -->
    </FrameLayout>
</LinearLayout>

// ✅ ХОРОШО
// Developer Options → Debug GPU Overdraw
// Убирайте лишние backgrounds
// Используйте android:background="@null" или Theme.windowBackground
```

### Ошибка 5: Неправильное использование shouldRasterize / LAYER_TYPE_HARDWARE

**iOS:**
```swift
// 🔴 ПЛОХО: rasterize для меняющегося контента
layer.shouldRasterize = true
layer.rasterizationScale = UIScreen.main.scale
// Контент постоянно обновляется → перерастеризация каждый кадр!

// ✅ ХОРОШО: только для статичного сложного контента
complexStaticLayer.shouldRasterize = true
complexStaticLayer.rasterizationScale = UIScreen.main.scale

// При изменении отключайте
func updateContent() {
    complexStaticLayer.shouldRasterize = false
    // ... update
    complexStaticLayer.shouldRasterize = true
}
```

**Android:**
```kotlin
// 🔴 ПЛОХО: hardware layer для анимирующегося контента
view.setLayerType(View.LAYER_TYPE_HARDWARE, null)
ObjectAnimator.ofFloat(view, "rotation", 0f, 360f).start()
// Layer пересоздаётся каждый кадр!

// ✅ ХОРОШО: включайте layer только на время анимации
view.setLayerType(View.LAYER_TYPE_HARDWARE, null)
ObjectAnimator.ofFloat(view, "rotation", 0f, 360f).apply {
    addListener(object : AnimatorListenerAdapter() {
        override fun onAnimationEnd(animation: Animator) {
            view.setLayerType(View.LAYER_TYPE_NONE, null)
        }
    })
    start()
}
```

### Ошибка 6: Игнорирование clipsToBounds/clipChildren

**iOS:**
```swift
// 🔴 ПЛОХО: clipsToBounds = true везде
containerView.clipsToBounds = true  // Может вызвать offscreen rendering

// ✅ ХОРОШО: используйте только где необходимо
// Если дочерние view не выходят за границы — не нужен
containerView.clipsToBounds = false
```

**Android:**
```kotlin
// 🔴 ПЛОХО в XML
<FrameLayout
    android:clipChildren="true"
    android:clipToPadding="true">

// ✅ ХОРОШО: отключайте если не нужно
<FrameLayout
    android:clipChildren="false"
    android:clipToPadding="false">
```

---

## 3 Mental Models

### Mental Model 1: "Render Pipeline как Конвейер"

```
                    iOS                          Android
                     │                              │
    ┌────────────────┴────────────────┐  ┌────────┴────────────┐
    │         PREPARATION             │  │     PREPARATION     │
    │  • layoutSubviews()             │  │  • onMeasure()      │
    │  • draw(_:) → записываем        │  │  • onLayout()       │
    │    команды в layer              │  │  • onDraw() →       │
    │                                 │  │    DisplayList      │
    └─────────────┬───────────────────┘  └──────────┬──────────┘
                  │                                  │
                  ▼                                  ▼
    ┌────────────────────────────────┐  ┌───────────────────────┐
    │         COMMIT                 │  │        SYNC           │
    │  • CATransaction.commit()      │  │  • DisplayList →      │
    │  • Layer tree → Render Server  │  │    RenderThread       │
    └─────────────┬──────────────────┘  └──────────┬────────────┘
                  │                                 │
                  ▼                                 ▼
    ┌────────────────────────────────┐  ┌───────────────────────┐
    │         RENDER                 │  │       RENDER          │
    │  • Decode → Draw → Display     │  │  • Skia → GPU → Swap  │
    │  • В отдельном процессе        │  │  • В отдельном потоке │
    └────────────────────────────────┘  └───────────────────────┘
```

**Ключевой инсайт:** После commit/sync анимации выполняются независимо от Main/UI Thread. Это значит:
- Тяжёлая работа на main thread не влияет на уже запущенные анимации
- НО! Если main thread заблокирован во время commit — кадр пропущен

### Mental Model 2: "Три типа View Properties"

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYOUT PROPERTIES                            │
│  • frame, bounds, center (iOS)                                  │
│  • width, height, margins (Android)                             │
│  • Изменение → invalidate layout → дорого                       │
│  • Избегать анимации если возможно                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DRAWING PROPERTIES                           │
│  • backgroundColor, borderColor                                 │
│  • Изменение → redraw → средняя стоимость                       │
│  • Кэшируйте сложные отрисовки                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMPOSITING PROPERTIES                       │
│  • transform, alpha, position (layer)                           │
│  • translationX/Y, rotation, scaleX/Y (Android)                 │
│  • Изменение → только compositor → дёшево!                      │
│  • ВСЕГДА предпочитайте для анимаций                            │
└─────────────────────────────────────────────────────────────────┘
```

**Правило:** Анимируйте только compositing properties (transform, alpha) когда возможно.

### Mental Model 3: "Frame Budget распределение"

```
16.67ms (60fps) Budget:
┌────────────────────────────────────────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│ Input │ Animation │ Layout │ Paint │ Composite │ IDLE (buffer)│
│ 1-2ms │   2-3ms   │ 2-4ms  │ 2-4ms │   2-3ms   │    3-5ms    │
└────────────────────────────────────────────────────────────────┘

Где теряем время:

🔴 Layout Thrashing (iOS: layoutIfNeeded, Android: requestLayout)
   └─ Может занять 10-15ms на сложных иерархиях

🔴 Expensive Paint (custom draw, large images)
   └─ 5-10ms при неоптимальном коде

🔴 Offscreen Rendering (masks, shadows, clips)
   └─ +5-15ms на каждый offscreen pass

🔴 Main Thread Blocking (I/O, JSON parsing)
   └─ Блокирует весь pipeline
```

**Правило 16/8:** На 60fps у вас 16ms, но реально ~12ms. На 120fps — 8ms, реально ~6ms. Планируйте с запасом.

---

## Quiz: Проверь понимание

### Вопрос 1: Offscreen Rendering

Какая комбинация свойств в iOS вызывает offscreen rendering?

```swift
// Вариант A
layer.cornerRadius = 10
layer.backgroundColor = UIColor.white.cgColor

// Вариант B
layer.cornerRadius = 10
layer.masksToBounds = true
layer.backgroundColor = UIColor.white.cgColor

// Вариант C
layer.shadowOffset = CGSize(width: 0, height: 2)
layer.shadowRadius = 4
layer.shadowOpacity = 0.3
layer.shadowPath = UIBezierPath(rect: bounds).cgPath
```

<details>
<summary>Ответ</summary>

**Вариант B** вызывает offscreen rendering.

- **A**: `cornerRadius` без `masksToBounds` не вызывает offscreen — углы просто закругляются визуально
- **B**: Комбинация `cornerRadius + masksToBounds = true` требует offscreen pass для clipping
- **C**: Shadow с явно заданным `shadowPath` НЕ вызывает offscreen — путь уже вычислен

</details>

### Вопрос 2: Animation Performance

Какой код будет наиболее производительным для анимации увеличения view в 2 раза?

```swift
// Вариант A
UIView.animate(withDuration: 0.3) {
    self.view.frame.size = CGSize(
        width: self.view.frame.width * 2,
        height: self.view.frame.height * 2
    )
}

// Вариант B
UIView.animate(withDuration: 0.3) {
    self.view.transform = CGAffineTransform(scaleX: 2, y: 2)
}

// Вариант C
let animation = CABasicAnimation(keyPath: "bounds.size")
animation.toValue = CGSize(width: view.bounds.width * 2, height: view.bounds.height * 2)
animation.duration = 0.3
view.layer.add(animation, forKey: "resize")
```

<details>
<summary>Ответ</summary>

**Вариант B** — наиболее производительный.

- **A**: Изменение `frame.size` вызывает layout pass → дорого
- **B**: `transform` — compositing property, обрабатывается только compositor → дёшево
- **C**: Анимация `bounds.size` также вызывает layout → дорого

Transform масштабирует уже отрендеренный layer без перерасчёта layout.

</details>

### Вопрос 3: Android RenderThread

Что произойдёт с запущенной ObjectAnimator анимацией, если UI Thread заблокируется на 500ms?

```kotlin
ObjectAnimator.ofFloat(view, "translationX", 0f, 500f).apply {
    duration = 1000
    start()
}

// После старта анимации:
Thread.sleep(500)  // Блокируем UI Thread
```

<details>
<summary>Ответ</summary>

**Анимация продолжит выполняться плавно**, но с нюансами:

1. **RenderThread** выполняет отрисовку независимо от UI Thread
2. `translationX` — это RenderNode property, анимируется на RenderThread
3. Анимация будет выглядеть плавной для пользователя

**НО:**
- Если анимация требует callback на UI Thread (например, `onAnimationUpdate`), callbacks не вызовутся пока поток заблокирован
- После разблокировки может произойти "прыжок" если анимация использует интерполяцию на UI Thread

Это главное преимущество RenderThread, добавленного в Android 5.0 (Lollipop).

</details>

---

## Инструменты профилирования

### iOS

| Инструмент | Что показывает |
|------------|----------------|
| **Instruments → Core Animation** | Frame rate, offscreen rendering, blended layers |
| **Instruments → Time Profiler** | CPU usage по методам |
| **Instruments → Animation Hitches** | Конкретные hitches с причинами |
| **Xcode Debug → View Debugging** | Иерархия слоёв, свойства |
| **CALayer debug options** | Color blended layers, offscreen-rendered |

### Android

| Инструмент | Что показывает |
|------------|----------------|
| **Perfetto / Systrace** | Детальный анализ frame timing |
| **GPU Profiler (AGI)** | GPU workload, render passes |
| **Layout Inspector** | Иерархия view, properties |
| **Developer Options → GPU Overdraw** | Визуализация overdraw |
| **Developer Options → Profile HWUI** | Frame time bars на экране |

---

## Связь с другими темами

[[ios-graphics-fundamentals]] — Графическая подсистема iOS построена на Core Animation (CALayer), Core Graphics (Quartz 2D) и Metal. Заметка разбирает layer tree (model, presentation, render), implicit vs explicit animations, offscreen rendering и compositing. Понимание iOS graphics необходимо для оптимизации производительности: shadowPath вместо shadow, shouldRasterize для сложных иерархий, drawsAsynchronously для тяжёлого рендеринга. Это основа для сравнения с Android RenderThread.

[[android-graphics-apis]] — Android rendering pipeline включает measure → layout → draw → RenderThread → GPU. Заметка объясняет Hardware Acceleration, RenderNode, DisplayList, VSync и Choreographer. Особое внимание уделено Compose rendering: Skia backend, composition, layout и drawing phases. Сравнение с iOS Core Animation показывает, как обе платформы решают проблему 60fps рендеринга, но разными архитектурными подходами.

[[ios-view-rendering]] — Детальный разбор iOS rendering pipeline: от Auto Layout constraint solving через Core Animation commit transaction до GPU compositing. Заметка объясняет, почему некоторые операции вызывают offscreen rendering (cornerRadius + masksToBounds, shadow без shadowPath) и как это влияет на производительность. Эти знания дополняют графический слой конкретными рекомендациями по оптимизации UI на iOS.

---

## Источники и дальнейшее чтение

### Теоретические основы

- **Foley J. et al. (1990).** *Computer Graphics: Principles and Practice.* 2nd ed. — Теория rendering pipeline: layout, paint, compositing.
- **Akenine-Möller T. et al. (2018).** *Real-Time Rendering.* 4th ed. — GPU pipeline и compositing model.

### Практические руководства

- [Core Animation Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreAnimation_guide/) — iOS rendering.
- [Android Hardware Acceleration](https://developer.android.com/topic/performance/hardware-accel) — Android rendering.

---

## Резюме

**Для iOS разработчиков:**
1. Используйте transform вместо frame для анимаций
2. Всегда задавайте shadowPath для теней
3. Избегайте cornerRadius + masksToBounds комбинации
4. Профилируйте с Color Blended Layers в Instruments

**Для Android разработчиков:**
1. Анимируйте translationX/Y, rotation, scale, alpha — они на RenderThread
2. Избегайте requestLayout() во время анимаций
3. Используйте hasOverlappingRendering() = false где возможно
4. Проверяйте GPU Overdraw в Developer Options

**Универсальные правила:**
1. Compositing properties > Drawing properties > Layout properties
2. Кэшируйте объекты в draw методах
3. Никогда не блокируйте main/UI thread
4. Используйте профилировщики до того, как возникнут проблемы

---

## Проверь себя

> [!question]- Почему iOS использует Core Animation (отдельный render server process), а Android -- RenderThread (поток внутри процесса приложения)? Какие последствия у каждого подхода?
> iOS: render server (backboardd) -- отдельный процесс с более высоким приоритетом, который продолжает анимации даже если main thread заблокирован. Это обеспечивает 60fps для implicit animations (opacity, transform) без вмешательства приложения. Android: RenderThread -- отдельный поток внутри process приложения. Он обрабатывает DisplayList команды и может продолжать hardware-accelerated анимации. Следствие: iOS implicit animations "бесплатнее" для разработчика, но сложнее кастомизировать; Android требует явного использования hardware layer для smooth анимаций.

> [!question]- Сценарий: при скролле списка с закруглёнными углами и тенями на iOS fps падает до 30. Какие причины и оптимизации применить?
> Причины: 1) cornerRadius + masksToBounds вызывает offscreen rendering -- GPU создаёт дополнительный буфер. 2) shadow без shadowPath заставляет Core Animation вычислять path из содержимого каждый кадр. 3) Каждая ячейка создаёт два offscreen pass (маска + тень). Оптимизации: задать shadowPath явно (UIBezierPath), использовать shouldRasterize=true для статичных ячеек (кэширует bitmap), разделить тень и контент на разные CALayer (тень на нижнем, контент с cornerRadius на верхнем), использовать continuous corner curve вместо circular.

> [!question]- Почему анимации transform/alpha считаются "дешёвыми" на обеих платформах, а layout-анимации -- "дорогими"?
> Transform и alpha -- compositing properties: они применяются к уже отрисованному bitmap слоя на GPU, не требуют перерисовки содержимого. Layout-анимации (frame, size) требуют: 1) пересчёт constraints/measure, 2) перерасположение дочерних views, 3) перерисовку содержимого, 4) compositing -- все 4 фазы pipeline вместо одной. На iOS compositing выполняется в render server, на Android -- в RenderThread, обеспечивая 60fps для таких анимаций даже при загруженном main thread.

> [!question]- Как Metal (iOS) и Vulkan (Android) изменили подход к графическому рендерингу по сравнению с OpenGL ES?
> Metal и Vulkan -- low-level GPU APIs с явным управлением ресурсами: command buffers, pipeline state objects, explicit synchronization. OpenGL ES скрывал это за driver-side оптимизациями (driver overhead). Metal/Vulkan дают: меньше CPU overhead (тоньше driver layer), предсказуемую производительность, multi-threaded command encoding. Trade-off: значительно сложнее в использовании. Для UI-фреймворков это прозрачно: Core Animation/Skia используют Metal/Vulkan внутри, разработчик работает с высокоуровневым API.

---

## Ключевые карточки

Чем отличается rendering pipeline iOS от Android?
?
iOS: Core Animation (CALayer tree) -> commit transaction -> render server (backboardd, отдельный процесс) -> GPU compositing. Android: measure -> layout -> draw (Canvas) -> RenderThread (DisplayList) -> GPU compositing. Ключевое: iOS использует отдельный процесс для рендеринга, Android -- отдельный поток. Оба: hardware acceleration по умолчанию.

Что такое offscreen rendering на iOS и почему его нужно избегать?
?
Offscreen rendering -- GPU создаёт дополнительный буфер для эффектов, которые нельзя применить за один проход (cornerRadius+masksToBounds, shadow без shadowPath, group opacity). Каждый offscreen pass удваивает стоимость рендеринга слоя. Решения: задать shadowPath, использовать shouldRasterize для статичного контента, разделять shadow и mask на разные layers.

Какие свойства анимации выполняются на GPU без участия CPU?
?
Compositing properties: transform (translation, rotation, scale), opacity/alpha, backgroundColor. Они применяются к bitmap слоя и не требуют перерисовки. На iOS -- Core Animation implicit animations. На Android -- RenderThread hardware-accelerated animations (translationX/Y, rotation, scaleX/Y, alpha). Layout properties (frame, bounds, constraints) требуют CPU.

Что такое VSync и Choreographer на Android?
?
VSync -- сигнал синхронизации с частотой обновления дисплея (60/120 Hz). Choreographer -- координатор, который привязывает input, animation и drawing callbacks к VSync. При пропуске VSync frame отображается на следующем цикле (jank). Аналог на iOS: CADisplayLink привязывает обновления к display refresh rate.

Как Skia используется в Jetpack Compose и Flutter?
?
Skia -- 2D graphics library от Google. Compose использует Skia через Android Canvas API (hardware-accelerated). Flutter использует собственный Skia renderer, минуя платформенные UI frameworks полностью. Compose Multiplatform на iOS также рендерит через Skia (или Metal backend), обеспечивая pixel-perfect consistency. Skia абстрагирует GPU backends (OpenGL, Vulkan, Metal).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-performance-profiling]] | Профилирование графической производительности на обеих платформах |
| Углубиться | [[ios-view-rendering]] | Детальный разбор iOS rendering pipeline из раздела iOS |
| Смежная тема | [[android-graphics-apis]] | Android rendering pipeline из раздела Android |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |

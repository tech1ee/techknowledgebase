---
title: "Анимации Android: от ValueAnimator до Compose Transition"
created: 2026-02-09
modified: 2026-02-13
type: deep-dive
status: published
area: android
tags:
  - topic/android
  - topic/ui
  - topic/animations
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-view-rendering-pipeline]]"
  - "[[android-handler-looper]]"
  - "[[android-compose-internals]]"
  - "[[android-custom-view-fundamentals]]"
  - "[[android-app-startup-performance]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-ui-views]]"
reading_time: 95
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Android Animations — от ValueAnimator до Compose Transition

## Зачем это нужно

**Проблема:** Анимации — ключевой элемент пользовательского опыта. Без них UI кажется "мёртвым". Но плохие анимации хуже отсутствия анимаций: дропнутые кадры, рывки, неестественное движение.

**Решение:** Android предоставляет три поколения animation API: View Animation (legacy), Property Animation (основной для View system), Compose Animation (декларативный). Понимание внутреннего устройства — от Choreographer и VSYNC до spring physics — позволяет создавать плавные 60/120fps анимации.

**Ключевой инсайт:** Все анимации в Android работают через Choreographer — он синхронизирует обновления с VSYNC сигналом дисплея. Пропущенный кадр = 16.6ms (60Hz) или 8.3ms (120Hz) задержка, заметная пользователю.

```
Choreographer получает VSYNC сигнал (каждые 16.6ms при 60Hz)
→ Animation frame callback
→ Вычисляет новое значение (interpolator/spring)
→ Обновляет свойство View/Compose
→ invalidate() → measure/layout/draw
→ Surface → SurfaceFlinger → Display
```

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| View Rendering Pipeline | Как measure/layout/draw рисуют кадр | `[[android-view-rendering-pipeline]]` |
| Handler/Looper | Choreographer работает через Handler | `[[android-handler-looper]]` |
| Compose Internals | Recomposition и Snapshot State | `[[android-compose-internals]]` |
| Custom Views | Canvas drawing для кастомных анимаций | `[[android-custom-view-fundamentals]]` |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Choreographer** | Системный компонент, синхронизирующий анимации с VSYNC | Дирижёр оркестра — задаёт темп |
| **VSYNC** | Vertical Sync — сигнал обновления дисплея | Метроном — "пора рисовать новый кадр" |
| **ValueAnimator** | Генерирует значения от start до end по timeline | Таймер, который считает промежуточные значения |
| **ObjectAnimator** | ValueAnimator + автоматическое применение к свойству | Робот-рука, двигающая объект по траектории |
| **Interpolator** | Функция, определяющая скорость изменения | Характер движения: плавно, резко, с отскоком |
| **TypeEvaluator** | Вычисляет промежуточные значения между start и end | Калькулятор "где объект между точкой A и B" |
| **PropertyValuesHolder** | Набор свойств для анимации одного объекта | Пульт управления с несколькими ручками |
| **AnimatorSet** | Последовательность/параллельность анимаций | Партитура — кто когда играет |
| **MotionLayout** | XML-based анимации между constraint sets | Режиссёр сцены — описывает начало и конец |
| **Spring Animation** | Физически-основанная пружинная анимация | Реальная пружина с массой и жёсткостью |
| **animateAsState** | Compose: анимация state-driven значений | Автопилот — сам анимирует изменения |
| **Transition** | Compose: координация нескольких анимаций | Хореограф — синхронизирует движения группы |

---

## 1. Три поколения Android Animation

### 1.1 ЧТО это

```
┌──────────────────────────────────────────────────────────────┐
│          ТРИ ПОКОЛЕНИЯ АНИМАЦИИ В ANDROID                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Gen 1: View Animation (android.view.animation)             │
│  ┌──────────────────────────────────────────────────┐       │
│  │ • AlphaAnimation, TranslateAnimation,            │       │
│  │   ScaleAnimation, RotateAnimation                │       │
│  │ • AnimationSet                                    │       │
│  │ • XML: res/anim/                                  │       │
│  │                                                   │       │
│  │ ⚠ НЕ меняет реальные свойства View!              │       │
│  │ ⚠ Только визуальная трансформация (matrix)        │       │
│  │ ⚠ Click target остаётся на СТАРОМ месте           │       │
│  │                                                   │       │
│  │ Статус: LEGACY (не используйте для нового кода)  │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Gen 2: Property Animation (android.animation)              │
│  ┌──────────────────────────────────────────────────┐       │
│  │ • ValueAnimator, ObjectAnimator                   │       │
│  │ • AnimatorSet, AnimatorInflater                   │       │
│  │ • Физика: SpringAnimation, FlingAnimation         │       │
│  │ • MotionLayout (ConstraintLayout)                 │       │
│  │                                                   │       │
│  │ ✅ Меняет РЕАЛЬНЫЕ свойства View                  │       │
│  │ ✅ Работает с любым объектом (не только View)     │       │
│  │ ✅ Extensible: custom Interpolator, TypeEvaluator │       │
│  │                                                   │       │
│  │ Статус: ОСНОВНОЙ для View system                  │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Gen 3: Compose Animation                                    │
│  ┌──────────────────────────────────────────────────┐       │
│  │ • animateXxxAsState, AnimatedVisibility           │       │
│  │ • AnimatedContent, Crossfade                      │       │
│  │ • Transition, InfiniteTransition                  │       │
│  │ • animateContentSize                              │       │
│  │ • Animatable (low-level)                          │       │
│  │                                                   │       │
│  │ ✅ Декларативный                                  │       │
│  │ ✅ Корутины-based (suspend)                       │       │
│  │ ✅ Автоматическая отмена при recomposition        │       │
│  │ ✅ Gesture-driven анимации                        │       │
│  │                                                   │       │
│  │ Статус: ОСНОВНОЙ для Compose                      │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 ПОЧЕМУ View Animation плох

```kotlin
// ❌ View Animation: перемещает ВИЗУАЛЬНО, но НЕ меняет свойства
val anim = TranslateAnimation(0f, 300f, 0f, 0f)
anim.duration = 500
anim.fillAfter = true // Визуально остаётся на новом месте
button.startAnimation(anim)

// ПРОБЛЕМА: button.x всё ещё = 0!
// Клик на "новом" месте НЕ РАБОТАЕТ
// Клик на "старом" месте РАБОТАЕТ (невидимая кнопка)

// ✅ Property Animation: перемещает РЕАЛЬНО
ObjectAnimator.ofFloat(button, "translationX", 0f, 300f).apply {
    duration = 500
    start()
}
// button.translationX == 300f → клик работает правильно
```

---

## 2. Choreographer и VSYNC — сердце анимаций

### 2.1 ЧТО это

Choreographer — синглтон (один на Looper), который принимает callbacks, привязанные к VSYNC сигналу дисплея.

### 2.2 КАК РАБОТАЕТ

```
┌──────────────────────────────────────────────────────────────┐
│          CHOREOGRAPHER & VSYNC PIPELINE                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Display Hardware                                            │
│  ┌────────────────────┐                                     │
│  │ VSYNC signal        │  каждые 16.6ms (60Hz)              │
│  │ │                   │  или 8.3ms (120Hz)                  │
│  └─┼──────────────────┘                                     │
│    │                                                         │
│    ▼                                                         │
│  SurfaceFlinger → sends VSYNC to app process                │
│    │                                                         │
│    ▼                                                         │
│  Choreographer (main thread)                                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │ doFrame(frameTimeNanos) {                         │       │
│  │   // 1. INPUT callbacks (touch events)            │       │
│  │   doCallbacks(CALLBACK_INPUT)                     │       │
│  │                                                   │       │
│  │   // 2. ANIMATION callbacks                       │       │
│  │   doCallbacks(CALLBACK_ANIMATION)                 │       │
│  │   //  ↑ ValueAnimator.doAnimationFrame()          │       │
│  │   //  ↑ Spring/Fling animation updates            │       │
│  │                                                   │       │
│  │   // 3. INSETS callbacks                          │       │
│  │   doCallbacks(CALLBACK_INSETS_ANIMATION)           │       │
│  │                                                   │       │
│  │   // 4. TRAVERSAL callbacks                       │       │
│  │   doCallbacks(CALLBACK_TRAVERSAL)                 │       │
│  │   //  ↑ ViewRootImpl.performTraversals()          │       │
│  │   //  ↑ measure → layout → draw                   │       │
│  │                                                   │       │
│  │   // 5. COMMIT callbacks                          │       │
│  │   doCallbacks(CALLBACK_COMMIT)                    │       │
│  │ }                                                 │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ПОРЯДОК КРИТИЧЕН:                                           │
│  Input → Animation (обновляет значения) →                   │
│  → Traversal (рисует кадр с новыми значениями)              │
│                                                              │
│  Если animation callback > 16.6ms → пропущен кадр (jank)   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 КАК ValueAnimator использует Choreographer

```
┌──────────────────────────────────────────────────────────────┐
│       ValueAnimator ВНУТРЕННИЙ МЕХАНИЗМ                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  animator.start()                                            │
│  │                                                           │
│  ├─→ AnimationHandler.addAnimationFrameCallback(this)        │
│  │   │                                                       │
│  │   ├─→ Choreographer.postFrameCallback(mFrameCallback)     │
│  │   │   // Подписка на СЛЕДУЮЩИЙ VSYNC                      │
│  │   │                                                       │
│  │   └─→ На каждый VSYNC:                                    │
│  │       │                                                   │
│  │       ├─→ doAnimationFrame(frameTime)                     │
│  │       │   │                                               │
│  │       │   ├─→ fraction = (frameTime - startTime) / dur    │
│  │       │   │   // Линейная доля времени [0..1]             │
│  │       │   │                                               │
│  │       │   ├─→ fraction = interpolator.getInterpolation(f) │
│  │       │   │   // Нелинейная трансформация                 │
│  │       │   │   // AccelerateDecelerate: 3t²-2t³            │
│  │       │   │                                               │
│  │       │   ├─→ value = evaluator.evaluate(fraction, s, e)  │
│  │       │   │   // FloatEvaluator: s + fraction*(e-s)       │
│  │       │   │                                               │
│  │       │   └─→ notifyListeners(value)                      │
│  │       │       // AnimatorUpdateListener.onAnimationUpdate  │
│  │       │                                                   │
│  │       └─→ Если не закончилась:                            │
│  │           Choreographer.postFrameCallback(mFrameCallback) │
│  │           // Подписка на СЛЕДУЮЩИЙ VSYNC                  │
│  │                                                           │
│  └─→ По окончании:                                           │
│      removeCallback() + onAnimationEnd()                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Property Animation — ValueAnimator и ObjectAnimator

### 3.1 ValueAnimator — генератор значений

```kotlin
// ValueAnimator генерирует значения, но НЕ применяет их
val animator = ValueAnimator.ofFloat(0f, 1f).apply {
    duration = 300
    interpolator = DecelerateInterpolator()

    addUpdateListener { animation ->
        val value = animation.animatedValue as Float
        // Ручное применение
        view.alpha = value
        view.scaleX = 1f + value * 0.2f
        view.scaleY = 1f + value * 0.2f
    }

    addListener(object : AnimatorListenerAdapter() {
        override fun onAnimationStart(animation: Animator) {
            // Начало анимации
        }
        override fun onAnimationEnd(animation: Animator) {
            // Конец анимации — cleanup
        }
    })
}

animator.start()
```

```kotlin
// ValueAnimator с кастомным TypeEvaluator
// Анимация цвета через HSV (а не линейно через ARGB)
val colorAnimator = ValueAnimator.ofObject(
    HsvEvaluator(), // кастомный evaluator
    Color.RED,
    Color.BLUE
).apply {
    duration = 1000
    addUpdateListener {
        view.setBackgroundColor(it.animatedValue as Int)
    }
}

class HsvEvaluator : TypeEvaluator<Int> {
    private val startHsv = FloatArray(3)
    private val endHsv = FloatArray(3)

    override fun evaluate(fraction: Float, startValue: Int, endValue: Int): Int {
        Color.colorToHSV(startValue, startHsv)
        Color.colorToHSV(endValue, endHsv)

        // Интерполяция в HSV пространстве (более натуральные переходы)
        val h = startHsv[0] + (endHsv[0] - startHsv[0]) * fraction
        val s = startHsv[1] + (endHsv[1] - startHsv[1]) * fraction
        val v = startHsv[2] + (endHsv[2] - startHsv[2]) * fraction

        return Color.HSVToColor(floatArrayOf(h, s, v))
    }
}
```

### 3.2 ObjectAnimator — автоматическое применение

```kotlin
// ObjectAnimator автоматически применяет значения к свойству
// Использует reflection или Property объект

// Через строку (reflection — медленнее)
ObjectAnimator.ofFloat(view, "translationX", 0f, 200f).apply {
    duration = 300
    start()
}

// Через Property объект (без reflection — быстрее)
ObjectAnimator.ofFloat(view, View.TRANSLATION_X, 0f, 200f).apply {
    duration = 300
    start()
}

// Стандартные Property объекты View:
// View.ALPHA, View.TRANSLATION_X/Y/Z,
// View.SCALE_X/Y, View.ROTATION, View.ROTATION_X/Y
```

```kotlin
// PropertyValuesHolder — несколько свойств одновременно
val scaleX = PropertyValuesHolder.ofFloat(View.SCALE_X, 1f, 1.2f, 1f)
val scaleY = PropertyValuesHolder.ofFloat(View.SCALE_Y, 1f, 1.2f, 1f)
val alpha = PropertyValuesHolder.ofFloat(View.ALPHA, 1f, 0.7f, 1f)

ObjectAnimator.ofPropertyValuesHolder(view, scaleX, scaleY, alpha).apply {
    duration = 400
    interpolator = OvershootInterpolator(2f)
    start()
}
```

### 3.3 AnimatorSet — оркестрация

```kotlin
// AnimatorSet — последовательные и параллельные анимации
val fadeIn = ObjectAnimator.ofFloat(view, View.ALPHA, 0f, 1f)
val slideUp = ObjectAnimator.ofFloat(view, View.TRANSLATION_Y, 100f, 0f)
val scaleUp = ObjectAnimator.ofFloat(view, View.SCALE_X, 0.8f, 1f)

AnimatorSet().apply {
    // Параллельно: fadeIn + slideUp
    // Затем: scaleUp
    play(fadeIn).with(slideUp)
    play(scaleUp).after(fadeIn)

    duration = 400
    interpolator = FastOutSlowInInterpolator()
    start()
}

// Или через playSequentially/playTogether
AnimatorSet().apply {
    playTogether(fadeIn, slideUp) // все одновременно
    // playSequentially(fadeIn, slideUp, scaleUp) // друг за другом
    start()
}
```

### 3.4 ViewPropertyAnimator — fluent API

```kotlin
// ViewPropertyAnimator — самый удобный API для View анимаций
view.animate()
    .alpha(1f)
    .translationY(0f)
    .scaleX(1f)
    .scaleY(1f)
    .setDuration(300)
    .setInterpolator(FastOutSlowInInterpolator())
    .setStartDelay(100)
    .withStartAction {
        // Перед анимацией
        view.visibility = View.VISIBLE
    }
    .withEndAction {
        // После анимации
    }
    .start()

// ViewPropertyAnimator:
// ✅ Автоматически использует hardware layer (GPU ускорение)
// ✅ Объединяет несколько свойств в один invalidate()
// ✅ Автоматическая отмена при новом вызове animate()
// ✅ Нет allocation (нет ObjectAnimator объектов)
```

---

## 4. Interpolators — характер движения

### 4.1 ЧТО это

Interpolator преобразует линейную долю времени [0..1] в нелинейную кривую. Определяет "характер" движения.

### 4.2 Стандартные Interpolators

```
┌──────────────────────────────────────────────────────────────┐
│           СТАНДАРТНЫЕ INTERPOLATORS                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  LinearInterpolator         AccelerateInterpolator           │
│  f(t) = t                   f(t) = t²                        │
│  │      ╱                   │         ╱                      │
│  │    ╱                     │       ╱                        │
│  │  ╱                       │     ╱                          │
│  │╱                         │  ╱╱                            │
│  └──────                    └──────                          │
│  Равномерно                 Разгон (медленно→быстро)         │
│                                                              │
│  DecelerateInterpolator     AccelerateDecelerate             │
│  f(t) = 1-(1-t)²           f(t) = cos((t+1)π)/2+0.5        │
│  │  ╱╱                     │     ╱──╱                        │
│  │╱                         │   ╱    │                       │
│  │                          │ ╱      │                       │
│  │                          │╱       │                       │
│  └──────                    └──────                          │
│  Торможение (быстро→медл.)  Разгон→торможение               │
│                                                              │
│  OvershootInterpolator      BounceInterpolator               │
│  │    ╱╲                    │                  ╱╲            │
│  │  ╱    ╲╱                 │      ╱╲   ╱╲ ╱    ╲           │
│  │╱                         │  ╱╲╱    ╲╱                     │
│  │                          │╱                               │
│  └──────                    └──────                          │
│  Перелёт + возврат          Отскок (мячик)                   │
│                                                              │
│  AnticipateInterpolator     AnticipateOvershoot              │
│  │                          │                                │
│  │         ╱                │          ╱╲                    │
│  │       ╱                  │        ╱    ╲╱                 │
│  │╲   ╱                     │╲    ╱                          │
│  │  ╲╱                      │  ╲╱                            │
│  └──────                    └──────                          │
│  Замах + движение           Замах + перелёт + возврат        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 Material Motion Interpolators

```kotlin
// Material Design 3 рекомендует:

// Стандартный (для большинства UI анимаций)
// "emphasized" — быстрое начало, плавное торможение
val standardInterpolator = FastOutSlowInInterpolator()
// Кубическая Безье: (0.4, 0.0, 0.2, 1.0)

// Entering (элемент появляется)
val enterInterpolator = LinearOutSlowInInterpolator()
// Безье: (0.0, 0.0, 0.2, 1.0) — начинает с полной скорости, тормозит

// Exiting (элемент уходит)
val exitInterpolator = FastOutLinearInInterpolator()
// Безье: (0.4, 0.0, 1.0, 1.0) — разгоняется и уходит

// Пример: Material shared element transition
ObjectAnimator.ofFloat(view, View.TRANSLATION_X, 0f, 300f).apply {
    duration = 300 // Material standard duration
    interpolator = FastOutSlowInInterpolator()
    start()
}
```

### 4.4 Кастомный Interpolator

```kotlin
// Кастомный Interpolator через Безье кривую
class CubicBezierInterpolator(
    private val cx1: Float, private val cy1: Float,
    private val cx2: Float, private val cy2: Float
) : Interpolator {
    override fun getInterpolation(input: Float): Float {
        // Численное решение кубической Безье
        var t = input
        // Newton-Raphson для нахождения t по x
        repeat(8) {
            val x = bezierX(t) - input
            if (abs(x) < 1e-6) return@repeat
            val dx = bezierDx(t)
            if (abs(dx) < 1e-6) return@repeat
            t -= x / dx
        }
        return bezierY(t)
    }

    private fun bezierX(t: Float): Float {
        val mt = 1 - t
        return 3 * mt * mt * t * cx1 + 3 * mt * t * t * cx2 + t * t * t
    }

    private fun bezierY(t: Float): Float {
        val mt = 1 - t
        return 3 * mt * mt * t * cy1 + 3 * mt * t * t * cy2 + t * t * t
    }

    private fun bezierDx(t: Float): Float {
        val mt = 1 - t
        return 3 * mt * mt * cx1 + 6 * mt * t * (cx2 - cx1) + 3 * t * t * (1 - cx2)
    }
}

// Использование
val customInterp = CubicBezierInterpolator(0.25f, 0.1f, 0.25f, 1.0f)
```

---

## 5. Physics-based Animation — пружины и инерция

### 5.1 ЧТО это

Физические анимации не имеют фиксированной длительности. Они заканчиваются когда физическая модель достигает равновесия. Это выглядит натуральнее чем time-based анимации.

### 5.2 ПОЧЕМУ это важно

```
┌──────────────────────────────────────────────────────────────┐
│     TIME-BASED vs PHYSICS-BASED                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Time-based (300ms AccelerateDecelerate):                    │
│  ┌──────────────────────────────────────┐                   │
│  │ Всегда 300ms, независимо от velocity │                   │
│  │ Резкий переход если скорость ≠ 0     │                   │
│  │ "Неестественное" ощущение            │                   │
│  └──────────────────────────────────────┘                   │
│                                                              │
│  Physics-based (Spring, damping=0.7):                        │
│  ┌──────────────────────────────────────┐                   │
│  │ Длительность зависит от velocity     │                   │
│  │ Плавный переход от gesture velocity  │                   │
│  │ "Физически реальное" ощущение        │                   │
│  │ Может быть прервана без рывка       │                   │
│  └──────────────────────────────────────┘                   │
│                                                              │
│  Применение: drag-and-drop, fling, swipe-to-dismiss,        │
│  pull-to-refresh, любые gesture-driven анимации              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 5.3 SpringAnimation

```kotlin
// Spring Animation — пружина с затуханием
val springAnim = SpringAnimation(view, DynamicAnimation.TRANSLATION_X, 0f).apply {
    spring = SpringForce(0f).apply {
        // Жёсткость: насколько быстро пружина возвращается
        stiffness = SpringForce.STIFFNESS_MEDIUM // 1500f

        // Коэффициент затухания: как быстро колебания прекращаются
        dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY // 0.5f
    }
}

// Запуск с начальной скоростью (от gesture)
springAnim.setStartVelocity(velocityTracker.xVelocity)
springAnim.start()
```

```
Spring Animation параметры:

ЖЁСТКОСТЬ (stiffness):
┌─────────────────────────────────────────────┐
│ VERY_LOW (200f)   — мягкая, медленная       │
│ LOW (500f)        — умеренно мягкая          │
│ MEDIUM (1500f)    — стандартная               │
│ HIGH (10000f)     — жёсткая, быстрая         │
└─────────────────────────────────────────────┘

ЗАТУХАНИЕ (dampingRatio):
┌─────────────────────────────────────────────┐
│ 0.0                — без затухания           │
│                     (бесконечные колебания)   │
│ BOUNCY (0.2f)      — много отскоков          │
│ MEDIUM_BOUNCY(0.5f)— умеренные отскоки       │
│ LOW_BOUNCY (0.75f) — минимальные отскоки     │
│ NO_BOUNCY (1.0f)   — без отскоков            │
│                     (критическое затухание)   │
│ > 1.0              — перезатухание            │
│                     (медленный возврат)       │
└─────────────────────────────────────────────┘
```

### 5.4 FlingAnimation

```kotlin
// Fling Animation — инерционное движение с трением
val flingAnim = FlingAnimation(view, DynamicAnimation.TRANSLATION_X).apply {
    // Начальная скорость из gesture
    setStartVelocity(velocityTracker.xVelocity)

    // Трение: как быстро замедляется
    friction = 1.5f // по умолчанию 1.0

    // Границы
    setMinValue(0f)
    setMaxValue(maxTranslation)
}

flingAnim.start()

// Chained animations: fling → spring (snap to position)
flingAnim.addEndListener { _, _, value, velocity ->
    // Когда fling заканчивается — spring к ближайшей позиции
    val targetPosition = snapToNearestPosition(value)
    SpringAnimation(view, DynamicAnimation.TRANSLATION_X, targetPosition).apply {
        setStartVelocity(velocity) // Передаём скорость от fling
        spring = SpringForce(targetPosition).apply {
            stiffness = SpringForce.STIFFNESS_MEDIUM
            dampingRatio = SpringForce.DAMPING_RATIO_NO_BOUNCY
        }
        start()
    }
}
```

### 5.5 Gesture → Physics Animation

```kotlin
// Полный пример: drag + fling/spring
class DraggableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val velocityTracker = VelocityTracker.obtain()
    private var springAnimX: SpringAnimation? = null
    private var springAnimY: SpringAnimation? = null

    private val gestureDetector = GestureDetectorCompat(context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onScroll(
                e1: MotionEvent?, e2: MotionEvent,
                distanceX: Float, distanceY: Float
            ): Boolean {
                // Перемещение за пальцем
                translationX -= distanceX
                translationY -= distanceY
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        velocityTracker.addMovement(event)
        gestureDetector.onTouchEvent(event)

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Отменяем текущие анимации
                springAnimX?.cancel()
                springAnimY?.cancel()
            }
            MotionEvent.ACTION_UP -> {
                velocityTracker.computeCurrentVelocity(1000)

                // Spring обратно к (0, 0) с начальной скоростью от gesture
                springAnimX = SpringAnimation(this, TRANSLATION_X, 0f).apply {
                    setStartVelocity(velocityTracker.xVelocity)
                    spring = SpringForce(0f).apply {
                        stiffness = SpringForce.STIFFNESS_LOW
                        dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                    }
                    start()
                }
                springAnimY = SpringAnimation(this, TRANSLATION_Y, 0f).apply {
                    setStartVelocity(velocityTracker.yVelocity)
                    spring = SpringForce(0f).apply {
                        stiffness = SpringForce.STIFFNESS_LOW
                        dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                    }
                    start()
                }
            }
        }
        return true
    }
}
```

---

## 6. MotionLayout — декларативные анимации

### 6.1 ЧТО это

MotionLayout = ConstraintLayout + анимации. Описывает начальное и конечное состояние (ConstraintSet) и переход между ними. Управляется progress [0..1] или gesture.

### 6.2 КАК РАБОТАЕТ

```
┌──────────────────────────────────────────────────────────────┐
│           MOTIONLAYOUT ARCHITECTURE                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Layout XML:                                                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │ <MotionLayout                                     │       │
│  │     app:layoutDescription="@xml/scene">           │       │
│  │     <ImageView android:id="@+id/avatar" />        │       │
│  │     <TextView android:id="@+id/title" />          │       │
│  │ </MotionLayout>                                   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  MotionScene XML (res/xml/scene.xml):                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │ <MotionScene>                                     │       │
│  │   <Transition                                     │       │
│  │     motion:constraintSetStart="@id/start"         │       │
│  │     motion:constraintSetEnd="@id/end">            │       │
│  │                                                   │       │
│  │     <OnSwipe                                      │       │
│  │       motion:touchAnchorId="@id/avatar"           │       │
│  │       motion:dragDirection="dragUp" />             │       │
│  │                                                   │       │
│  │     <KeyFrameSet>                                 │       │
│  │       <KeyPosition ... />                         │       │
│  │       <KeyAttribute ... />                        │       │
│  │     </KeyFrameSet>                                │       │
│  │   </Transition>                                   │       │
│  │                                                   │       │
│  │   <ConstraintSet android:id="@+id/start">        │       │
│  │     <Constraint android:id="@id/avatar"           │       │
│  │       layout_width="120dp" ... />                 │       │
│  │   </ConstraintSet>                                │       │
│  │                                                   │       │
│  │   <ConstraintSet android:id="@+id/end">          │       │
│  │     <Constraint android:id="@id/avatar"           │       │
│  │       layout_width="40dp" ... />                  │       │
│  │   </ConstraintSet>                                │       │
│  │ </MotionScene>                                    │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Результат:                                                  │
│  Свайп вверх → avatar плавно уменьшается с 120dp до 40dp   │
│  MotionLayout интерполирует ВСЕ constraint параметры        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 6.3 КАК ПРИМЕНЯТЬ — Collapsing Toolbar

```xml
<!-- res/layout/fragment_profile.xml -->
<androidx.constraintlayout.motion.widget.MotionLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    app:layoutDescription="@xml/scene_profile">

    <ImageView
        android:id="@+id/header_image"
        android:layout_width="match_parent"
        android:layout_height="250dp"
        android:scaleType="centerCrop" />

    <ImageView
        android:id="@+id/avatar"
        android:layout_width="100dp"
        android:layout_height="100dp" />

    <TextView
        android:id="@+id/username"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="24sp" />

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/content_list"
        android:layout_width="match_parent"
        android:layout_height="0dp" />

</androidx.constraintlayout.motion.widget.MotionLayout>
```

```xml
<!-- res/xml/scene_profile.xml -->
<MotionScene xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:motion="http://schemas.android.com/apk/res-auto">

    <Transition
        motion:constraintSetStart="@id/expanded"
        motion:constraintSetEnd="@id/collapsed"
        motion:duration="300">

        <!-- Управление через скролл RecyclerView -->
        <OnSwipe
            motion:touchAnchorId="@id/content_list"
            motion:touchAnchorSide="top"
            motion:dragDirection="dragUp" />

        <!-- Промежуточные ключевые кадры -->
        <KeyFrameSet>
            <!-- На 50% перехода: alpha header = 0 -->
            <KeyAttribute
                android:alpha="0"
                motion:framePosition="50"
                motion:motionTarget="@id/header_image" />

            <!-- На 30%: avatar начинает двигаться к toolbar -->
            <KeyPosition
                motion:framePosition="30"
                motion:keyPositionType="parentRelative"
                motion:percentX="0.1"
                motion:motionTarget="@id/avatar" />
        </KeyFrameSet>
    </Transition>

    <!-- Начальное состояние: развёрнутый header -->
    <ConstraintSet android:id="@+id/expanded">
        <Constraint android:id="@id/header_image"
            android:layout_width="match_parent"
            android:layout_height="250dp"
            android:alpha="1"
            motion:layout_constraintTop_toTopOf="parent" />

        <Constraint android:id="@id/avatar"
            android:layout_width="100dp"
            android:layout_height="100dp"
            motion:layout_constraintBottom_toBottomOf="@id/header_image"
            motion:layout_constraintStart_toStartOf="parent"
            android:layout_marginStart="16dp"
            android:layout_marginBottom="-50dp" />

        <Constraint android:id="@id/username"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="24sp"
            motion:layout_constraintTop_toBottomOf="@id/avatar"
            motion:layout_constraintStart_toStartOf="parent"
            android:layout_marginTop="16dp"
            android:layout_marginStart="16dp" />
    </ConstraintSet>

    <!-- Конечное состояние: свёрнутый toolbar -->
    <ConstraintSet android:id="@+id/collapsed">
        <Constraint android:id="@id/header_image"
            android:layout_width="match_parent"
            android:layout_height="56dp"
            android:alpha="0"
            motion:layout_constraintTop_toTopOf="parent" />

        <Constraint android:id="@id/avatar"
            android:layout_width="36dp"
            android:layout_height="36dp"
            motion:layout_constraintTop_toTopOf="parent"
            motion:layout_constraintStart_toStartOf="parent"
            android:layout_marginTop="10dp"
            android:layout_marginStart="16dp" />

        <Constraint android:id="@id/username"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="16sp"
            motion:layout_constraintTop_toTopOf="parent"
            motion:layout_constraintStart_toEndOf="@id/avatar"
            android:layout_marginTop="16dp"
            android:layout_marginStart="12dp" />
    </ConstraintSet>
</MotionScene>
```

### 6.4 Программное управление MotionLayout

```kotlin
// Программное управление progress
motionLayout.progress = 0.5f // 50% перехода

// Программная анимация
motionLayout.transitionToEnd()   // анимировать к end state
motionLayout.transitionToStart() // анимировать к start state
motionLayout.setTransitionDuration(500) // изменить длительность

// Listener
motionLayout.setTransitionListener(object : MotionLayout.TransitionListener {
    override fun onTransitionStarted(layout: MotionLayout, startId: Int, endId: Int) {}
    override fun onTransitionChange(layout: MotionLayout, startId: Int, endId: Int, progress: Float) {
        // progress: 0.0 → 1.0
        // Можно синхронизировать другие элементы
        toolbar.alpha = 1f - progress
    }
    override fun onTransitionCompleted(layout: MotionLayout, currentId: Int) {}
    override fun onTransitionTrigger(layout: MotionLayout, triggerId: Int, positive: Boolean, progress: Float) {}
})
```

---

## 7. Compose Animation — декларативные анимации

### 7.1 Обзор Compose Animation API

```
┌──────────────────────────────────────────────────────────────┐
│          COMPOSE ANIMATION API HIERARCHY                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  HIGH-LEVEL (декларативные, простые):                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │ AnimatedVisibility — появление/исчезновение       │       │
│  │ AnimatedContent    — переход между content        │       │
│  │ Crossfade          — кроссфейд между content      │       │
│  │ animateContentSize — анимация размера             │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  MID-LEVEL (state-driven):                                   │
│  ┌──────────────────────────────────────────────────┐       │
│  │ animate*AsState   — анимация одного значения      │       │
│  │   animateDpAsState                                │       │
│  │   animateColorAsState                             │       │
│  │   animateFloatAsState                             │       │
│  │                                                   │       │
│  │ updateTransition  — координация нескольких         │       │
│  │ InfiniteTransition— бесконечные анимации          │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  LOW-LEVEL (императивные, полный контроль):                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Animatable        — корутины-based, suspend       │       │
│  │ AnimationState    — хранение состояния            │       │
│  │ TargetBasedAnimation — расчёт значений            │       │
│  │ DecayAnimation    — физика затухания              │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ПРАВИЛО ВЫБОРА:                                             │
│  Начинайте с HIGH-LEVEL → если не хватает → MID-LEVEL       │
│  → если нужен полный контроль → LOW-LEVEL                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 7.2 animateAsState — простейшая анимация

```kotlin
// animate*AsState — автоматическая анимация при изменении target
@Composable
fun ExpandableCard(isExpanded: Boolean) {
    // При изменении isExpanded — значения анимируются автоматически
    val cardHeight by animateDpAsState(
        targetValue = if (isExpanded) 300.dp else 80.dp,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "cardHeight" // для инспектора анимаций
    )

    val backgroundColor by animateColorAsState(
        targetValue = if (isExpanded)
            MaterialTheme.colorScheme.primaryContainer
        else
            MaterialTheme.colorScheme.surface,
        animationSpec = tween(durationMillis = 300),
        label = "backgroundColor"
    )

    val cornerRadius by animateDpAsState(
        targetValue = if (isExpanded) 16.dp else 8.dp,
        label = "cornerRadius"
    )

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(cardHeight),
        shape = RoundedCornerShape(cornerRadius),
        colors = CardDefaults.cardColors(containerColor = backgroundColor)
    ) {
        // Контент карточки
    }
}
```

### 7.3 AnimatedVisibility

```kotlin
@Composable
fun NotificationBanner(isVisible: Boolean) {
    AnimatedVisibility(
        visible = isVisible,
        enter = slideInVertically(
            initialOffsetY = { fullHeight -> -fullHeight } // Сверху
        ) + fadeIn(
            animationSpec = tween(durationMillis = 300)
        ),
        exit = slideOutVertically(
            targetOffsetY = { fullHeight -> -fullHeight }
        ) + fadeOut()
    ) {
        // Этот контент анимируется при появлении/исчезновении
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        ) {
            Text(
                text = "Новое уведомление!",
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}

// Доступные enter transitions:
// fadeIn(), slideInVertically(), slideInHorizontally(),
// expandVertically(), expandHorizontally(), expandIn(),
// scaleIn()
//
// Комбинируются через +
// enter = fadeIn() + slideInVertically() + scaleIn()
```

### 7.4 AnimatedContent — переход между содержимым

```kotlin
@Composable
fun CounterDisplay(count: Int) {
    AnimatedContent(
        targetState = count,
        transitionSpec = {
            // Определяем анимацию на основе направления изменения
            if (targetState > initialState) {
                // Увеличение: новое число снизу, старое вверх
                (slideInVertically { height -> height } + fadeIn())
                    .togetherWith(
                        slideOutVertically { height -> -height } + fadeOut()
                    )
            } else {
                // Уменьшение: новое число сверху, старое вниз
                (slideInVertically { height -> -height } + fadeIn())
                    .togetherWith(
                        slideOutVertically { height -> height } + fadeOut()
                    )
            }.using(
                SizeTransform(clip = false)
            )
        },
        label = "counter"
    ) { targetCount ->
        Text(
            text = "$targetCount",
            style = MaterialTheme.typography.displayLarge
        )
    }
}
```

### 7.5 updateTransition — координация анимаций

```kotlin
enum class CardState { Collapsed, Expanded }

@Composable
fun AnimatedCard(cardState: CardState) {
    // updateTransition координирует несколько анимаций
    // с ОДНИМ lifecycle и одним state
    val transition = updateTransition(
        targetState = cardState,
        label = "cardTransition"
    )

    val height by transition.animateDp(
        transitionSpec = {
            when {
                CardState.Collapsed isTransitioningTo CardState.Expanded ->
                    spring(stiffness = Spring.StiffnessLow)
                else ->
                    spring(stiffness = Spring.StiffnessMedium)
            }
        },
        label = "height"
    ) { state ->
        when (state) {
            CardState.Collapsed -> 80.dp
            CardState.Expanded -> 300.dp
        }
    }

    val color by transition.animateColor(
        label = "color"
    ) { state ->
        when (state) {
            CardState.Collapsed -> Color.LightGray
            CardState.Expanded -> Color.White
        }
    }

    val elevation by transition.animateDp(
        label = "elevation"
    ) { state ->
        when (state) {
            CardState.Collapsed -> 2.dp
            CardState.Expanded -> 8.dp
        }
    }

    // Все три значения анимируются синхронно!
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(height),
        elevation = CardDefaults.cardElevation(defaultElevation = elevation),
        colors = CardDefaults.cardColors(containerColor = color)
    ) {
        // Контент
    }
}
```

### 7.6 InfiniteTransition — бесконечные анимации

```kotlin
@Composable
fun PulsingDot() {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")

    val scale by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = 800,
                easing = FastOutSlowInEasing
            ),
            repeatMode = RepeatMode.Reverse // Туда-обратно
        ),
        label = "scale"
    )

    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )

    Box(
        modifier = Modifier
            .size(20.dp)
            .scale(scale)
            .alpha(alpha)
            .background(Color.Red, CircleShape)
    )
}
```

### 7.7 Animatable — низкоуровневый контроль

```kotlin
@Composable
fun DraggableBox() {
    val offsetX = remember { Animatable(0f) }
    val offsetY = remember { Animatable(0f) }

    Box(
        modifier = Modifier
            .offset {
                IntOffset(offsetX.value.roundToInt(), offsetY.value.roundToInt())
            }
            .size(100.dp)
            .background(Color.Blue, RoundedCornerShape(16.dp))
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragEnd = {
                        // Spring обратно к нулю
                        // Используем корутины!
                        scope.launch {
                            launch {
                                offsetX.animateTo(
                                    targetValue = 0f,
                                    animationSpec = spring(
                                        dampingRatio = Spring.DampingRatioMediumBouncy,
                                        stiffness = Spring.StiffnessLow
                                    )
                                )
                            }
                            launch {
                                offsetY.animateTo(
                                    targetValue = 0f,
                                    animationSpec = spring(
                                        dampingRatio = Spring.DampingRatioMediumBouncy,
                                        stiffness = Spring.StiffnessLow
                                    )
                                )
                            }
                        }
                    }
                ) { change, dragAmount ->
                    change.consume()
                    // Мгновенное перемещение (snap, не анимация)
                    scope.launch {
                        offsetX.snapTo(offsetX.value + dragAmount.x)
                        offsetY.snapTo(offsetY.value + dragAmount.y)
                    }
                }
            }
    )
}

// Animatable ключевые методы:
// .snapTo(value)           — мгновенное перемещение
// .animateTo(target, spec) — анимация к цели (suspend!)
// .animateDecay(velocity, spec) — физическое затухание
// .stop()                  — остановка
// .value                   — текущее значение
// .velocity                — текущая скорость
// .isRunning               — анимируется ли
```

### 7.8 animationSpec — спецификации анимации

```kotlin
// tween — time-based с easing
tween<Float>(
    durationMillis = 300,
    delayMillis = 0,
    easing = FastOutSlowInEasing // = AccelerateDecelerateInterpolator
)

// spring — физическая пружина (рекомендуется!)
spring<Float>(
    dampingRatio = Spring.DampingRatioMediumBouncy, // 0.5f
    stiffness = Spring.StiffnessLow,                // 200f
    visibilityThreshold = 0.1f                      // когда считать завершённой
)

// keyframes — ключевые кадры
keyframes<Float> {
    durationMillis = 500
    0f at 0 using LinearEasing            // 0ms: значение 0
    0.5f at 150 using FastOutSlowInEasing // 150ms: значение 0.5
    0.8f at 300 using LinearEasing        // 300ms: значение 0.8
    1f at 500                              // 500ms: значение 1
}

// repeatable — повторяемая
repeatable<Float>(
    iterations = 3,
    animation = tween(300),
    repeatMode = RepeatMode.Reverse
)

// infiniteRepeatable — бесконечная
infiniteRepeatable<Float>(
    animation = tween(1000),
    repeatMode = RepeatMode.Restart
)

// snap — мгновенное изменение (без анимации)
snap<Float>(delayMillis = 100)
```

---

## 8. Shared Element Transition

### 8.1 Compose Shared Element (API 34+, compose-animation 1.7+)

```kotlin
// SharedTransitionLayout — контейнер для shared elements
@Composable
fun ProductListScreen(
    onProductClick: (Product) -> Unit
) {
    SharedTransitionLayout {
        AnimatedContent(targetState = selectedProduct) { product ->
            if (product == null) {
                // Список
                LazyColumn {
                    items(products) { item ->
                        ProductCard(
                            product = item,
                            sharedTransitionScope = this@SharedTransitionLayout,
                            animatedVisibilityScope = this@AnimatedContent,
                            onClick = { onProductClick(item) }
                        )
                    }
                }
            } else {
                // Детали
                ProductDetail(
                    product = product,
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this@AnimatedContent,
                )
            }
        }
    }
}

@Composable
fun ProductCard(
    product: Product,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope,
    onClick: () -> Unit
) {
    with(sharedTransitionScope) {
        Card(onClick = onClick) {
            Image(
                painter = rememberAsyncImagePainter(product.imageUrl),
                contentDescription = null,
                modifier = Modifier
                    .sharedElement(
                        state = rememberSharedContentState(key = "image-${product.id}"),
                        animatedVisibilityScope = animatedVisibilityScope,
                    )
                    .size(80.dp)
            )
            Text(
                text = product.name,
                modifier = Modifier
                    .sharedBounds(
                        sharedContentState = rememberSharedContentState(key = "title-${product.id}"),
                        animatedVisibilityScope = animatedVisibilityScope,
                    )
            )
        }
    }
}
```

---

## 9. Оптимизация анимаций — 60/120 fps

### 9.1 Правила производительных анимаций

```
┌──────────────────────────────────────────────────────────────┐
│           ОПТИМИЗАЦИЯ АНИМАЦИЙ                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ПРАВИЛО 1: Анимируйте "дешёвые" свойства                   │
│  ┌──────────────────────────────────────────────────┐       │
│  │ ДЕШЁВЫЕ (только draw, без layout):               │       │
│  │ • alpha                                           │       │
│  │ • translationX/Y                                  │       │
│  │ • scaleX/Y                                        │       │
│  │ • rotation/rotationX/Y                            │       │
│  │ → Эти свойства обрабатываются GPU                 │       │
│  │ → НЕ вызывают requestLayout()                     │       │
│  │                                                   │       │
│  │ ДОРОГИЕ (вызывают layout):                        │       │
│  │ • width/height                                    │       │
│  │ • padding/margin                                  │       │
│  │ • textSize                                        │       │
│  │ → Вызывают measure + layout всего поддерева      │       │
│  │ → Могут вызвать jank на сложных layouts           │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ПРАВИЛО 2: Hardware Layer для View анимаций                │
│  ┌──────────────────────────────────────────────────┐       │
│  │ view.setLayerType(View.LAYER_TYPE_HARDWARE, null) │       │
│  │ // View рисуется в текстуру GPU                   │       │
│  │ // Трансформации (translate/scale/rotate/alpha)   │       │
│  │ // применяются к текстуре — мгновенно             │       │
│  │                                                   │       │
│  │ ViewPropertyAnimator делает это АВТОМАТИЧЕСКИ!    │       │
│  │ view.animate().alpha(0f) // hardware layer ON      │       │
│  │                                                   │       │
│  │ ⚠ Не забудьте снять layer после анимации:         │       │
│  │ .withEndAction {                                  │       │
│  │     view.setLayerType(LAYER_TYPE_NONE, null)      │       │
│  │ }                                                 │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ПРАВИЛО 3: Compose — используйте Modifier.graphicsLayer   │
│  ┌──────────────────────────────────────────────────┐       │
│  │ // graphicsLayer НЕ вызывает recomposition!       │       │
│  │ Modifier.graphicsLayer {                          │       │
│  │     alpha = animatedAlpha.value                   │       │
│  │     translationX = animatedX.value                │       │
│  │     scaleX = animatedScale.value                  │       │
│  │ }                                                 │       │
│  │                                                   │       │
│  │ // vs Modifier.offset { } — тоже без recomposition│       │
│  │ // vs Modifier.alpha(value) — ВЫЗЫВАЕТ recomp!    │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 Compose: избегайте recomposition в анимациях

```kotlin
// ❌ ПЛОХО: каждый кадр анимации = recomposition
@Composable
fun BadAnimation(isVisible: Boolean) {
    val alpha by animateFloatAsState(
        targetValue = if (isVisible) 1f else 0f,
        label = "alpha"
    )

    // alpha читается в Composition scope →
    // каждое изменение alpha вызывает recomposition
    Box(
        modifier = Modifier
            .size(100.dp)
            .alpha(alpha) // ← Modifier.alpha() = recomposition!
            .background(Color.Red)
    )
}

// ✅ ХОРОШО: анимация в draw phase, без recomposition
@Composable
fun GoodAnimation(isVisible: Boolean) {
    val alpha by animateFloatAsState(
        targetValue = if (isVisible) 1f else 0f,
        label = "alpha"
    )

    Box(
        modifier = Modifier
            .size(100.dp)
            .graphicsLayer {
                // Читаем alpha в graphicsLayer lambda →
                // это draw phase, НЕ composition phase
                this.alpha = alpha
            }
            .background(Color.Red)
    )
}

// ✅ ЕЩУКЁ ЛУЧШЕ: используйте lambda-based modifiers
@Composable
fun BestAnimation(isVisible: Boolean) {
    val alpha by animateFloatAsState(
        targetValue = if (isVisible) 1f else 0f,
        label = "alpha"
    )

    Box(
        modifier = Modifier
            .size(100.dp)
            .drawBehind {
                // Draw phase — читаем alpha без recomposition
                drawRect(Color.Red, alpha = alpha)
            }
    )
}
```

### 9.3 Обнаружение jank

```kotlin
// Debug: подсветка recomposition (Compose 1.4+)
// В build.gradle:
// composeCompiler {
//     metricsDestination = project.layout.buildDirectory.dir("compose-metrics")
//     reportsDestination = project.layout.buildDirectory.dir("compose-reports")
// }

// Debug: включить recomposition count overlay
// В Developer Options → "Show recomposition counts"

// В коде: SideEffect для отслеживания recomposition
@Composable
fun DebugRecomposition(label: String) {
    if (BuildConfig.DEBUG) {
        val recompCount = remember { mutableIntStateOf(0) }
        SideEffect {
            recompCount.intValue++
            Log.d("Recomp", "$label: ${recompCount.intValue}")
        }
    }
}
```

---

## 10. Frame scheduling и Variable Refresh Rate

### 10.1 Современные дисплеи

```
┌──────────────────────────────────────────────────────────────┐
│      VARIABLE REFRESH RATE (VRR) DISPLAYS                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  60Hz:  16.6ms на кадр   ← бюджет                           │
│  90Hz:  11.1ms на кадр   ← Pixel 4, Galaxy S20              │
│  120Hz:  8.3ms на кадр   ← современные флагманы             │
│                                                              │
│  Adaptive refresh rate (Android 11+):                         │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Если нет анимации → 60Hz (экономия батареи)      │       │
│  │ Если есть анимация → 120Hz (плавность)            │       │
│  │ Если скролл → 120Hz                               │       │
│  │ Если статичный экран → 1Hz (LTPO displays)        │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Для разработчика:                                           │
│  • Анимации АВТОМАТИЧЕСКИ используют max refresh rate       │
│  • Не хардкодьте 16ms в расчётах!                           │
│  • Используйте Choreographer frameTimeNanos                  │
│  • Compose animations уже оптимизированы для VRR            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 11. Shared Element Transitions

### 11.1. Shared Element в View System

```kotlin
// SHARED ELEMENT TRANSITION МЕЖДУ ACTIVITIES

// Activity A (источник):
class ListActivity : AppCompatActivity() {

    fun onItemClick(item: Item, imageView: ImageView) {
        val intent = Intent(this, DetailActivity::class.java).apply {
            putExtra("item_id", item.id)
        }

        // Определяем shared element
        val options = ActivityOptions.makeSceneTransitionAnimation(
            this,
            Pair(imageView, "shared_image"),  // View и transitionName
            Pair(titleView, "shared_title")
        )

        startActivity(intent, options.toBundle())
    }
}

// В layout Activity A:
// <ImageView
//     android:id="@+id/image"
//     android:transitionName="shared_image" />

// Activity B (target):
class DetailActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Отложить transition пока изображение не загрузится
        postponeEnterTransition()

        setContentView(R.layout.activity_detail)

        // Загружаем изображение
        Glide.with(this)
            .load(imageUrl)
            .listener(object : RequestListener<Drawable> {
                override fun onResourceReady(...): Boolean {
                    // Изображение загружено — запускаем transition
                    startPostponedEnterTransition()
                    return false
                }
                override fun onLoadFailed(...): Boolean {
                    startPostponedEnterTransition()  // Запускаем даже при ошибке!
                    return false
                }
            })
            .into(imageView)
    }
}

// В layout Activity B:
// <ImageView
//     android:id="@+id/detail_image"
//     android:transitionName="shared_image" />  <!-- Тот же transitionName! -->
```

### 11.2. Shared Element в Navigation Component

```kotlin
// FRAGMENT-TO-FRAGMENT SHARED ELEMENT

// Fragment A:
class ListFragment : Fragment() {

    fun navigateToDetail(item: Item, imageView: ImageView) {
        // transitionName должен быть уникальным для каждого item
        imageView.transitionName = "image_${item.id}"

        val extras = FragmentNavigatorExtras(
            imageView to "shared_image_${item.id}"
        )

        val action = ListFragmentDirections.actionToDetail(item.id)
        findNavController().navigate(action, extras)
    }
}

// Fragment B:
class DetailFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Настройка transition
        sharedElementEnterTransition = TransitionInflater.from(requireContext())
            .inflateTransition(R.transition.shared_image_transition)

        // Или программно:
        sharedElementEnterTransition = TransitionSet().apply {
            addTransition(ChangeBounds())
            addTransition(ChangeTransform())
            addTransition(ChangeImageTransform())
            duration = 300
            interpolator = FastOutSlowInInterpolator()
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Отложить transition
        postponeEnterTransition()

        // Установить transitionName
        val itemId = arguments?.getLong("item_id")
        binding.imageView.transitionName = "shared_image_$itemId"

        // Загрузить изображение и запустить transition
        viewLifecycleOwner.lifecycleScope.launch {
            loadImage()
            startPostponedEnterTransition()
        }
    }
}
```

### 11.3. Shared Element в Compose (Navigation 2.8+)

```kotlin
// COMPOSE SHARED ELEMENT (Experimental в Navigation 2.8+)

@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun AppNavigation() {
    SharedTransitionLayout {  // Обёртка для shared elements
        NavHost(navController, startDestination = "list") {

            composable("list") {
                ListScreen(
                    onItemClick = { item ->
                        navController.navigate("detail/${item.id}")
                    },
                    animatedVisibilityScope = this@composable
                )
            }

            composable("detail/{itemId}") { backStackEntry ->
                val itemId = backStackEntry.arguments?.getString("itemId")
                DetailScreen(
                    itemId = itemId,
                    animatedVisibilityScope = this@composable
                )
            }
        }
    }
}

@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedTransitionScope.ListScreen(
    onItemClick: (Item) -> Unit,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    LazyColumn {
        items(items) { item ->
            ItemCard(
                item = item,
                modifier = Modifier
                    .sharedElement(
                        state = rememberSharedContentState(key = "image-${item.id}"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
                    .clickable { onItemClick(item) }
            )
        }
    }
}

@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedTransitionScope.DetailScreen(
    itemId: String?,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    val item = remember(itemId) { getItem(itemId) }

    Column {
        AsyncImage(
            model = item.imageUrl,
            contentDescription = null,
            modifier = Modifier
                .sharedElement(
                    state = rememberSharedContentState(key = "image-${item.id}"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
                .fillMaxWidth()
                .height(300.dp)
        )

        Text(
            text = item.title,
            modifier = Modifier.sharedBounds(
                sharedContentState = rememberSharedContentState(key = "title-${item.id}"),
                animatedVisibilityScope = animatedVisibilityScope
            )
        )
    }
}
```

---

## 12. Gesture-Driven Animations

### 12.1. Интеграция жестов и анимаций

```kotlin
// GESTURE + ANIMATION INTEGRATION

class SwipeToDeleteViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

    private var startX = 0f
    private val deleteThreshold = itemView.width * 0.4f

    init {
        itemView.setOnTouchListener { view, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    startX = event.rawX
                    true
                }

                MotionEvent.ACTION_MOVE -> {
                    val deltaX = event.rawX - startX
                    // Применяем перемещение напрямую (без анимации)
                    view.translationX = deltaX.coerceIn(-view.width.toFloat(), 0f)
                    true
                }

                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    val deltaX = event.rawX - startX
                    val velocity = calculateVelocity()  // От VelocityTracker

                    if (abs(deltaX) > deleteThreshold || abs(velocity) > 1000f) {
                        // Удаление: анимация с текущей скоростью
                        animateDelete(velocity)
                    } else {
                        // Возврат: spring анимация
                        animateReturn(velocity)
                    }
                    true
                }

                else -> false
            }
        }
    }

    private fun animateDelete(velocity: Float) {
        // Fling анимация с текущей скоростью
        FlingAnimation(itemView, DynamicAnimation.TRANSLATION_X).apply {
            setStartVelocity(velocity)
            friction = 1.5f
            setMinValue(-itemView.width.toFloat())
            setMaxValue(0f)
            addEndListener { _, _, _, _ ->
                onItemDeleted(adapterPosition)
            }
        }.start()
    }

    private fun animateReturn(velocity: Float) {
        // Spring анимация с передачей скорости
        SpringAnimation(itemView, DynamicAnimation.TRANSLATION_X, 0f).apply {
            setStartVelocity(velocity)  // Плавный переход от gesture
            spring.dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
            spring.stiffness = SpringForce.STIFFNESS_LOW
        }.start()
    }
}
```

### 12.2. Gesture + Animation в Compose

```kotlin
// COMPOSE: SWIPEABLE + ANIMATION

@OptIn(ExperimentalMaterialApi::class)
@Composable
fun SwipeToDeleteItem(
    onDelete: () -> Unit,
    content: @Composable () -> Unit
) {
    val dismissState = rememberDismissState(
        confirmValueChange = { dismissValue ->
            if (dismissValue == DismissValue.DismissedToStart) {
                onDelete()
                true
            } else false
        }
    )

    SwipeToDismiss(
        state = dismissState,
        directions = setOf(DismissDirection.EndToStart),
        background = {
            // Фон при свайпе
            val color by animateColorAsState(
                targetValue = when (dismissState.targetValue) {
                    DismissValue.DismissedToStart -> Color.Red
                    else -> Color.LightGray
                },
                label = "background"
            )

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(color)
                    .padding(16.dp),
                contentAlignment = Alignment.CenterEnd
            ) {
                Icon(Icons.Default.Delete, "Delete")
            }
        },
        dismissContent = {
            content()
        }
    )
}

// ADVANCED: Draggable + Spring
@Composable
fun DraggableCard() {
    var offsetX by remember { mutableFloatStateOf(0f) }
    var offsetY by remember { mutableFloatStateOf(0f) }

    // Coroutine-based spring animation
    val coroutineScope = rememberCoroutineScope()
    val animatableX = remember { Animatable(0f) }
    val animatableY = remember { Animatable(0f) }

    Box(
        modifier = Modifier
            .offset { IntOffset(animatableX.value.roundToInt(), animatableY.value.roundToInt()) }
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragEnd = {
                        // При отпускании — spring анимация к исходной позиции
                        coroutineScope.launch {
                            launch {
                                animatableX.animateTo(
                                    targetValue = 0f,
                                    animationSpec = spring(
                                        dampingRatio = Spring.DampingRatioMediumBouncy,
                                        stiffness = Spring.StiffnessLow
                                    )
                                )
                            }
                            launch {
                                animatableY.animateTo(
                                    targetValue = 0f,
                                    animationSpec = spring(
                                        dampingRatio = Spring.DampingRatioMediumBouncy,
                                        stiffness = Spring.StiffnessLow
                                    )
                                )
                            }
                        }
                    },
                    onDrag = { change, dragAmount ->
                        change.consume()
                        // Мгновенно обновляем позицию (без анимации)
                        coroutineScope.launch {
                            animatableX.snapTo(animatableX.value + dragAmount.x)
                            animatableY.snapTo(animatableY.value + dragAmount.y)
                        }
                    }
                )
            }
            .size(100.dp)
            .background(Color.Blue, RoundedCornerShape(8.dp))
    )
}
```

---

## 13. Lottie Animations

### 13.1. Интеграция Lottie

```kotlin
// LOTTIE ANIMATION INTEGRATION

// build.gradle:
// implementation "com.airbnb.android:lottie:6.3.0"
// implementation "com.airbnb.android:lottie-compose:6.3.0"

// View system:
class LottieActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val animationView = LottieAnimationView(this).apply {
            // Из assets:
            setAnimation("animation.json")

            // Или из raw:
            setAnimation(R.raw.animation)

            // Или из URL:
            setAnimationFromUrl("https://example.com/animation.json")

            // Настройки:
            repeatCount = LottieDrawable.INFINITE
            repeatMode = LottieDrawable.RESTART
            speed = 1.5f  // 1.5x скорость

            // Listeners:
            addAnimatorListener(object : Animator.AnimatorListener {
                override fun onAnimationStart(animation: Animator) { }
                override fun onAnimationEnd(animation: Animator) { }
                override fun onAnimationCancel(animation: Animator) { }
                override fun onAnimationRepeat(animation: Animator) { }
            })

            addAnimatorUpdateListener { animator ->
                val progress = animator.animatedFraction
                // 0.0 → 1.0
            }
        }

        animationView.playAnimation()
    }
}

// COMPOSE:
@Composable
fun LottieAnimation(
    @RawRes animationResId: Int,
    isPlaying: Boolean = true,
    restartOnPlay: Boolean = false
) {
    val composition by rememberLottieComposition(
        LottieCompositionSpec.RawRes(animationResId)
    )

    val progress by animateLottieCompositionAsState(
        composition = composition,
        isPlaying = isPlaying,
        restartOnPlay = restartOnPlay,
        iterations = LottieConstants.IterateForever,
        speed = 1f
    )

    LottieAnimation(
        composition = composition,
        progress = { progress },
        modifier = Modifier.size(200.dp)
    )
}

// INTERACTIVE LOTTIE:
@Composable
fun InteractiveLottie() {
    val composition by rememberLottieComposition(
        LottieCompositionSpec.RawRes(R.raw.toggle)
    )

    var isChecked by remember { mutableStateOf(false) }

    // Анимация от 0 до 0.5 (unchecked) или от 0.5 до 1 (checked)
    val progress by animateFloatAsState(
        targetValue = if (isChecked) 1f else 0f,
        animationSpec = tween(500),
        label = "lottie_progress"
    )

    LottieAnimation(
        composition = composition,
        progress = { progress },
        modifier = Modifier
            .size(48.dp)
            .clickable { isChecked = !isChecked }
    )
}
```

### 13.2. Оптимизация Lottie

```kotlin
// LOTTIE PERFORMANCE OPTIMIZATION

// 1. Кэширование композиции
object LottieCache {
    private val cache = LruCache<Int, LottieComposition>(10)

    fun getOrLoad(context: Context, @RawRes resId: Int): LottieComposition? {
        return cache.get(resId) ?: run {
            val composition = LottieCompositionFactory
                .fromRawResSync(context, resId)
                .value
            composition?.let { cache.put(resId, it) }
            composition
        }
    }
}

// 2. Hardware acceleration
lottieAnimationView.apply {
    // Включить hardware layer для лучшей производительности
    setRenderMode(RenderMode.HARDWARE)

    // Или автоматический выбор:
    setRenderMode(RenderMode.AUTOMATIC)
}

// 3. Уменьшение размера
lottieAnimationView.apply {
    // Не масштабировать выше native resolution
    scaleType = ImageView.ScaleType.CENTER_INSIDE

    // Ограничить frame rate для экономии батареи
    setMaxFrame(30)  // max 30 fps
}

// 4. Prefetch в background
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Предзагрузка Lottie анимаций в background
        lifecycleScope.launch(Dispatchers.IO) {
            listOf(R.raw.loading, R.raw.success, R.raw.error).forEach { resId ->
                LottieCompositionFactory.fromRawRes(this@MyApplication, resId)
            }
        }
    }
}
```

---

## 14. Animation Testing

### 14.1. Unit Testing анимаций

```kotlin
// ТЕСТИРОВАНИЕ ANIMATOR VALUES

class AnimationTest {

    @Test
    fun `ValueAnimator interpolates correctly`() {
        val values = mutableListOf<Float>()

        val animator = ValueAnimator.ofFloat(0f, 100f).apply {
            duration = 1000
            interpolator = LinearInterpolator()
            addUpdateListener { values.add(it.animatedValue as Float) }
        }

        // В тестах нужно manually advance time
        animator.start()

        // Используем TestRule для контроля времени
        ShadowLooper.runUiThreadTasksIncludingDelayedTasks()

        // Проверяем конечное значение
        assertEquals(100f, values.last(), 0.01f)
    }
}
```

### 14.2. UI Testing с Espresso

```kotlin
// ESPRESSO: ОЖИДАНИЕ ЗАВЕРШЕНИЯ АНИМАЦИИ

class AnimationUITest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Before
    fun disableAnimations() {
        // Отключить системные анимации для стабильных тестов
        // Settings → Developer Options → Animation scale = 0x
        // Или программно через UiAutomator
    }

    @Test
    fun animationCompletes() {
        // Кликаем кнопку которая запускает анимацию
        onView(withId(R.id.animate_button)).perform(click())

        // Ждём IdlingResource (если используется)
        IdlingRegistry.getInstance().register(animationIdlingResource)

        // Проверяем конечное состояние
        onView(withId(R.id.animated_view))
            .check(matches(withAlpha(1.0f)))
    }
}

// CUSTOM IDLING RESOURCE ДЛЯ АНИМАЦИЙ:
class AnimatorIdlingResource(private val animator: Animator) : IdlingResource {

    private var resourceCallback: IdlingResource.ResourceCallback? = null

    init {
        animator.addListener(object : AnimatorListenerAdapter() {
            override fun onAnimationEnd(animation: Animator) {
                resourceCallback?.onTransitionToIdle()
            }
        })
    }

    override fun getName() = "AnimatorIdlingResource"

    override fun isIdleNow() = !animator.isRunning

    override fun registerIdleTransitionCallback(callback: IdlingResource.ResourceCallback) {
        resourceCallback = callback
    }
}
```

### 14.3. Compose Animation Testing

```kotlin
// COMPOSE UI TESTING

class ComposeAnimationTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `animated visibility shows content`() {
        var isVisible by mutableStateOf(false)

        composeTestRule.setContent {
            AnimatedVisibility(visible = isVisible) {
                Text("Content", modifier = Modifier.testTag("content"))
            }
        }

        // Изначально не видно
        composeTestRule.onNodeWithTag("content").assertDoesNotExist()

        // Показываем
        isVisible = true

        // Ждём завершения анимации
        composeTestRule.waitForIdle()

        // Теперь видно
        composeTestRule.onNodeWithTag("content").assertIsDisplayed()
    }

    @Test
    fun `animation values update correctly`() {
        var targetValue by mutableStateOf(0f)
        var currentValue by mutableStateOf(0f)

        composeTestRule.setContent {
            val animatedValue by animateFloatAsState(
                targetValue = targetValue,
                animationSpec = tween(1000),
                label = "test"
            )

            LaunchedEffect(animatedValue) {
                currentValue = animatedValue
            }

            Text("Value: $animatedValue")
        }

        // Меняем target
        targetValue = 100f

        // Ждём завершения анимации (advance time)
        composeTestRule.mainClock.advanceTimeBy(1000)
        composeTestRule.waitForIdle()

        // Проверяем
        assertEquals(100f, currentValue, 0.01f)
    }
}
```

---

## 15. Animation Best Practices Summary

```
ANIMATION BEST PRACTICES CHECKLIST:

┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [ ] Используйте hardware-accelerated properties:               │
│     translationX/Y, rotation, scale, alpha                      │
│                                                                 │
│ [ ] Избегайте анимации layout properties:                       │
│     width, height, margins, padding                             │
│                                                                 │
│ [ ] В Compose: graphicsLayer{} вместо Modifier.alpha()         │
│                                                                 │
│ [ ] Включите hardware layer для сложных View:                  │
│     view.setLayerType(LAYER_TYPE_HARDWARE, null)               │
│     После анимации: LAYER_TYPE_NONE                            │
│                                                                 │
│ [ ] Проверяйте jank в GPU Profiler                             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    UX GUIDELINES                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [ ] Длительность: 150-300ms для большинства анимаций          │
│     > 300ms только для сложных transitions                      │
│                                                                 │
│ [ ] Используйте FastOutSlowIn (ease-in-out) по умолчанию       │
│                                                                 │
│ [ ] Spring анимации для gesture-driven UI                      │
│                                                                 │
│ [ ] Stagger анимации для списков (delay между items)           │
│                                                                 │
│ [ ] Respect user preference: Reduce Motion                      │
│     if (ViewConfiguration.get(ctx).isReduceMotionEnabled())    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    CODE QUALITY                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [ ] Отменяйте анимации в onDestroy/onDispose                   │
│                                                                 │
│ [ ] Используйте AnimatorSet для связанных анимаций             │
│                                                                 │
│ [ ] Тестируйте на low-end устройствах                          │
│                                                                 │
│ [ ] Профилируйте с Perfetto для сложных анимаций               │
│                                                                 │
│ [ ] Документируйте animation specs в design system             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "View Animation и Property Animation — одно и то же" | View Animation НЕ меняет реальные свойства View; Property Animation — меняет. Click target остаётся на старом месте с View Animation |
| "Анимация 300ms всегда лучше" | Физические анимации (spring) не имеют фиксированной длительности и выглядят натуральнее; 300ms — разумный default только для time-based |
| "Hardware layer ускоряет всё" | Hardware layer ускоряет трансформации (translate/rotate/scale/alpha), но занимает GPU память. Для сложных View с частой перерисовкой — может быть медленнее |
| "Compose анимации быстрее View анимаций" | Compose animations проходят через тот же Choreographer; преимущество в отсутствии inflation, но первая composition дороже |
| "Modifier.alpha() и graphicsLayer{alpha=} — одинаковы" | Modifier.alpha() вызывает recomposition при изменении, graphicsLayer — нет (работает в draw phase) |
| "Больше анимаций = лучше UX" | Избыточные анимации раздражают; анимации должны нести смысл (направление, связь, обратная связь) |
| "Interpolator не важен" | Interpolator определяет "характер" движения; линейная анимация кажется роботизированной; Material рекомендует FastOutSlowIn |
| "MotionLayout заменяет Property Animation" | MotionLayout — для сложных layout transitions; Property Animation — для простых трансформаций. Они дополняют друг друга |

---

## CS-фундамент

| Концепция | Применение в Animation |
|-----------|----------------------|
| **Параметрические кривые** | Interpolators: кубические кривые Безье определяют характер движения |
| **Дифференциальные уравнения** | SpringAnimation: решение уравнения затухающих колебаний (damped harmonic oscillator) |
| **Frame scheduling** | Choreographer: VSYNC-синхронизация, double/triple buffering для плавности |
| **Observer pattern** | AnimatorUpdateListener, TransitionListener — уведомления об изменениях |
| **State machine** | Animator states (RUNNING, PAUSED, ENDED), MotionLayout transition states |
| **Interpolation** | TypeEvaluator: линейная интерполяция между значениями; HSV vs RGB для цветов |
| **Корутины** | Compose Animatable: suspend-based API для последовательных/параллельных анимаций |

---

## Связь с другими темами

**[[android-view-rendering-pipeline]]** — rendering pipeline (measure/layout/draw) отвечает за отрисовку каждого кадра анимации. Понимание того, как работает invalidate(), VSYNC и SurfaceFlinger, объясняет, почему анимации иногда дёргаются и как оптимизировать перерисовку. Рекомендуется изучить rendering pipeline до глубокого погружения в анимации.

**[[android-handler-looper]]** — Choreographer, центральный компонент системы анимации, работает через Handler/Looper на main thread. Каждый кадр анимации планируется как callback в Choreographer, который привязан к VSYNC сигналу. Понимание механизма message queue помогает диагностировать jank и пропущенные кадры.

**[[android-compose-internals]]** — Compose использует собственную систему анимации, основанную на Snapshot State и recomposition. В отличие от View animations, Compose оптимизирует обновления через three-phase rendering (Composition, Layout, Drawing), что позволяет пропускать ненужные фазы. Изучайте после освоения View animations для сравнения подходов.

**[[android-custom-view-fundamentals]]** — Canvas drawing является основой для создания кастомных анимированных View. При реализации сложных анимаций (графики, диаграммы, игровые элементы) необходимо рисовать непосредственно на Canvas через onDraw(), комбинируя ValueAnimator с ручной отрисовкой.

**[[android-app-startup-performance]]** — Choreographer frame scheduling, используемый анимациями, тот же механизм, что управляет рендерингом при старте приложения. Perfetto и systrace — ключевые инструменты для анализа jank в анимациях, показывающие точное время каждой фазы кадра.

**[[android-performance-profiling]]** — GPU rendering profiler и frame timing tools позволяют визуализировать производительность анимаций в реальном времени. Overlay GPU overdraw, Profile GPU Rendering bars и Layout Inspector — необходимые инструменты для оптимизации анимаций до стабильных 60/120fps.

---

## Источники и дальнейшее чтение

**Книги:**
- Meier R. (2022). Professional Android, 4th Edition. — комплексное руководство по Android-разработке, включая Property Animation и оптимизацию UI
- Phillips B. et al. (2022). Android Programming: The Big Nerd Ranch Guide, 5th Edition. — практический учебник с примерами реализации анимаций
- Moskala M. (2021). Effective Kotlin. — лучшие практики Kotlin, включая DSL-паттерны, применяемые в Compose Animation API

**Веб-ресурсы:**
1. **[Property Animation Overview](https://developer.android.com/develop/ui/views/animations/prop-animation)** — docs — Официальный гайд по Property Animation
2. **[Compose Animation](https://developer.android.com/develop/ui/compose/animation/introduction)** — docs — Compose Animation документация
3. **[Physics-based Animation](https://developer.android.com/develop/ui/views/animations/physics-based-motion)** — docs — SpringAnimation и FlingAnimation
4. **[MotionLayout](https://developer.android.com/develop/ui/views/animations/motionlayout)** — docs — MotionLayout руководство
5. **[Choreographer.java — AOSP](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/view/Choreographer.java)** — source — Исходный код Choreographer
6. **[Compose Animation Codelab](https://developer.android.com/codelabs/jetpack-compose-animation)** — codelab — Практическое руководство
7. **[Material Motion](https://m3.material.io/styles/motion/overview)** — docs — Material Design 3 motion guidelines
8. **[Shared Element Transitions in Compose](https://developer.android.com/develop/ui/compose/animation/shared-elements)** — docs — Shared Element API
9. **[Understanding Choreographer — YouTube](https://www.youtube.com/watch?v=1YfRhpDj4ew)** — video — Внутреннее устройство Choreographer
10. **[Jank-free animations — Android Dev Summit](https://www.youtube.com/results?search_query=android+dev+summit+animations+jank+free)** — video — Оптимизация анимаций

---

## Проверь себя

> [!question]- Почему Property Animation предпочтительнее View Animation и когда View Animation все еще уместна?
> View Animation изменяет только визуальное представление -- View рисуется в новом месте, но touch target остается на старом. Property Animation реально изменяет свойства View (translationX, alpha). View Animation уместна для: window transitions, Activity переходы, и когда нужна только визуальная анимация без интерактивности.

> [!question]- Сценарий: анимация пружины (spring) выглядит нереалистично. Какие параметры настроить?
> Spring physics определяется двумя параметрами: stiffness (жесткость -- скорость возврата, STIFFNESS_LOW/MEDIUM/HIGH) и dampingRatio (затухание -- количество колебаний, DAMPING_RATIO_NO_BOUNCY/LOW/MEDIUM/HIGH). Нереалистичная анимация обычно имеет слишком высокую stiffness или неправильный damping. Для natural feel: STIFFNESS_LOW + DAMPING_RATIO_LOW_BOUNCY.


---

## Ключевые карточки

Какие типы анимаций есть в Android?
?
View Animation (tween, XML, только визуальное), Property Animation (ObjectAnimator, реальное изменение свойств), Transition Framework (shared element, scene), Compose Animation (animate*AsState, AnimatedVisibility), Physics-based (spring, fling).

Что такое Choreographer и его роль в анимациях?
?
Системный компонент для синхронизации анимаций с VSYNC. Анимации регистрируют callback через Choreographer.postFrameCallback(). На каждом VSYNC вычисляется новое значение анимации и применяется к View.

Что такое Interpolator?
?
Функция, определяющая темп анимации: LinearInterpolator (равномерно), AccelerateDecelerateInterpolator (ускорение-замедление), OvershootInterpolator (с перелетом), BounceInterpolator (с отскоком). В Compose -- Easing функции.

Как работает SharedElementTransition?
?
Анимирует View между двумя Activity/Fragment, создавая иллюзию перемещения элемента. Система: 1) Capture start bounds, 2) Start destination, 3) Capture end bounds, 4) Animate from start to end. Требует transitionName на обоих View.

Что такое MotionLayout?
?
ConstraintLayout с поддержкой анимаций между ConstraintSet. Определяет start/end состояния и transition между ними. Поддерживает touch-driven анимации, keyframes, custom attributes. Замена CoordinatorLayout для сложных анимаций.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-compose]] | Анимации в Compose -- animate*AsState |
| Углубиться | [[android-view-rendering-pipeline]] | Как Choreographer синхронизирует анимации |
| Смежная тема | [[ios-custom-views]] | Core Animation в iOS |
| Обзор | [[android-overview]] | Вернуться к карте раздела |


---
title: "iOS View Rendering: render loop, layers, off-screen rendering"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/rendering
  - level/advanced
related:
  - "[[android-view-rendering-pipeline]]"
  - "[[ios-graphics-fundamentals]]"
  - "[[cross-graphics-rendering]]"
prerequisites:
  - "[[ios-uikit-fundamentals]]"
  - "[[ios-graphics-fundamentals]]"
  - "[[ios-viewcontroller-lifecycle]]"
---

# iOS View Rendering: Render Loop, Layers, Off-Screen Rendering

## TL;DR

Рендеринг в iOS происходит через **Render Loop** - конвейер из трёх фаз (Layout, Display, Commit), который синхронизирован с VSync дисплея (60Hz = 16.67ms, 120Hz = 8.33ms). UIView рисуется на backing store через Core Animation, затем слои отправляются в **Render Server** (backboardd) - отдельный процесс, который композирует их на GPU. Производительность убивают **off-screen rendering** (маски, тени, clipsToBounds + cornerRadius) и **color blended layers** (прозрачные фоны), которые форсируют дополнительные проходы рендеринга на GPU.

**Ключевые концепции:**
- 16.67ms бюджет на кадр при 60fps (8.33ms для ProMotion 120Hz)
- Render Server работает в отдельном процессе для стабильности
- Off-screen rendering = context switch на GPU = потеря производительности
- layoutSubviews / draw(_:) вызываются по запросу, не каждый кадр
- CATransaction группирует изменения для atomic commit

---

## Зачем это нужно?

**Проблема:** Пользователи ожидают butter-smooth 60fps UI. Каждый пропущенный кадр (frame drop) = визуальный "заикание" (jank). Один кадр при 60fps = 16.67ms на всё: обработку событий, layout, отрисовку, GPU композицию. Превысил бюджет - потерял кадр.

**Решение:** Понимание Render Loop позволяет:
- Знать, что оптимизировать (bottleneck на CPU или GPU?)
- Избегать триггеров off-screen rendering
- Правильно использовать setNeedsLayout vs layoutIfNeeded
- Группировать изменения в CATransaction
- Профилировать через Instruments (Core Animation, GPU profiler)

**Преимущества:**
- Стабильные 60/120fps даже на сложных экранах
- Понимание, почему scroll "дёргается"
- Способность диагностировать rendering issues
- Оптимизация battery life (GPU - главный потребитель энергии)

---

## Аналогии из жизни

### 1. Render Loop = Конвейер сборки автомобилей

```
┌────────────────────────────────────────────────────────────────────┐
│  АВТОМОБИЛЬНЫЙ ЗАВОД (Render Loop)                                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  КОНВЕЙЕР работает СТРОГО по расписанию (каждые 16.67ms)          │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │ ЧЕРТЁЖ   │ → │ ПОКРАСКА │ → │ ОТПРАВКА │ → │ СБОРКА   │        │
│  │ (Layout) │   │ (Display)│   │ (Commit) │   │ (Render) │        │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘        │
│                                                                     │
│  Свисток! ────────────────────────────────────────────────────►    │
│  (VSync)     Если не успели - машина уходит без части деталей!    │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

Конвейер не ждёт. VSync - это неумолимый свисток каждые 16.67ms. Не успел - пропустил машину (frame drop).

### 2. Layout Pass = Чертёж где что стоит

```
┌─────────────────────────────────────────┐
│  АРХИТЕКТОР (Auto Layout Engine)        │
│                                          │
│  "Button на 20pt от края,               │
│   Label под ним,                        │
│   Image заполняет оставшееся"           │
│                                          │
│  → Считает конкретные координаты:       │
│    Button: (20, 100, 100, 44)           │
│    Label:  (20, 152, 100, 21)           │
│    Image:  (0, 181, 375, 500)           │
└─────────────────────────────────────────┘
```

Layout Pass определяет frame каждого view - где он находится и какого размера.

### 3. Display Pass = Покраска деталей

```
┌─────────────────────────────────────────┐
│  МАЛЯР (Core Graphics / draw(_:))       │
│                                          │
│  Берёт деталь (backing store bitmap)    │
│  и красит её:                           │
│                                          │
│  - Заливает фон синим                   │
│  - Рисует текст "Hello"                 │
│  - Добавляет обводку                    │
│                                          │
│  Результат: готовый bitmap в памяти     │
└─────────────────────────────────────────┘
```

Display Pass растеризует содержимое view в bitmap (backing store).

### 4. Commit = Отправка на сборку (в Render Server)

```
┌─────────────────────────────────────────┐
│  ЛОГИСТ (CATransaction)                 │
│                                          │
│  Собирает все детали (layer tree):      │
│  - View A с позицией X, bitmap B        │
│  - View C с transform, shadow           │
│  - View D с mask, opacity               │
│                                          │
│  Упаковывает в грузовик (IPC message)   │
│  и отправляет в цех сборки              │
│  (Render Server / backboardd)           │
└─────────────────────────────────────────┘
```

Commit сериализует layer tree и отправляет через IPC в отдельный процесс.

### 5. VSync = Свисток конвейера

```
┌─────────────────────────────────────────┐
│  СВИСТОК МАСТЕРА (VSync Signal)         │
│                                          │
│  Каждые 16.67ms (60Hz):                 │
│  "СВИИИИСТОК! Следующий кадр!"          │
│                                          │
│  Каждые 8.33ms (120Hz ProMotion):       │
│  "СВИИИИСТОК! Быстрее!"                 │
│                                          │
│  Не успел подготовить кадр?             │
│  Дисплей показывает старый = jank!      │
└─────────────────────────────────────────┘
```

VSync (Vertical Synchronization) - аппаратный сигнал синхронизации с частотой обновления дисплея.

---

## The Render Loop

### Полная диаграмма цикла рендеринга

```
iOS RENDER LOOP - 60fps = 16.67ms на кадр
═══════════════════════════════════════════════════════════════════════

         APP PROCESS                    │   RENDER SERVER (backboardd)
         ═══════════════                │   ══════════════════════════
                                        │
  ┌─────────────────────────┐           │
  │     EVENT LOOP          │           │
  │  (RunLoop iteration)    │           │
  └───────────┬─────────────┘           │
              │                         │
              ▼                         │
  ┌─────────────────────────┐           │
  │    HANDLE EVENTS        │           │
  │  • Touch events         │           │
  │  • Timer callbacks      │           │
  │  • GCD dispatches       │           │
  │  • Network callbacks    │           │
  └───────────┬─────────────┘           │
              │                         │
              ▼                         │
  ┌─────────────────────────┐           │
  │    LAYOUT PASS          │ ← setNeedsLayout / layoutIfNeeded
  │  • updateConstraints()  │           │
  │  • layoutSubviews()     │           │
  │  • Calculate frames     │           │
  └───────────┬─────────────┘           │
              │                         │
              ▼                         │
  ┌─────────────────────────┐           │
  │    DISPLAY PASS         │ ← setNeedsDisplay
  │  • draw(_:)             │           │
  │  • Rasterize to bitmap  │           │
  │  • Update backing store │           │
  └───────────┬─────────────┘           │
              │                         │
              ▼                         │
  ┌─────────────────────────┐           │   ┌─────────────────────┐
  │  COMMIT TRANSACTION     │──────────────▶│  DECODE LAYER TREE  │
  │  • Encode layer tree    │    IPC     │  │  • Deserialize      │
  │  • Send to render server│   (Mach)   │  │  • Build render tree│
  └─────────────────────────┘           │   └──────────┬──────────┘
                                        │              │
        ┌ ─ ─ ─ ─ ─ ─ ─ ─ ┐             │              ▼
          App может начать              │   ┌─────────────────────┐
        │ следующий кадр   │            │   │  GPU COMPOSITION    │
          пока GPU рисует              │   │  • Composite layers │
        └ ─ ─ ─ ─ ─ ─ ─ ─ ┘             │   │  • Apply transforms │
                                        │   │  • Blend colors     │
                                        │   └──────────┬──────────┘
                                        │              │
                                        │              ▼
                                        │   ┌─────────────────────┐
                                        │   │     DISPLAY         │
                                        │   │  • VSync signal     │
                                        │   │  • Swap buffers     │
                                        │   │  • Show on screen   │
                                        │   └─────────────────────┘

═══════════════════════════════════════════════════════════════════════
TIMING CONSTRAINTS:
• 60fps:  16.67ms total = ~12ms app + ~4ms render server
• 120fps:  8.33ms total = ~6ms app + ~2ms render server
• ProMotion: динамически 24-120Hz в зависимости от контента
═══════════════════════════════════════════════════════════════════════
```

### Временная шкала одного кадра

```
ONE FRAME TIMELINE (60fps = 16.67ms)
═══════════════════════════════════════════════════════════════════════

   0ms                    8ms                    16.67ms
   │                       │                       │
   ▼                       ▼                       ▼
   ┌───────────────────────┬───────────────────────┐
   │      APP PROCESS      │    RENDER SERVER      │
   │      (~8-12ms)        │      (~4-8ms)         │
   └───────────────────────┴───────────────────────┘
   │                                               │
   │◄─────────────── BUDGET: 16.67ms ────────────►│
   │                                               │
   ▼                                               ▼
 VSync                                           VSync
 (frame N)                                    (frame N+1)

   ЕСЛИ ПРЕВЫСИЛИ БЮДЖЕТ:
   ┌───────────────────────┬──────────────────────────┐
   │      APP PROCESS      │     RENDER SERVER        │
   │      (15ms!)          │       (6ms)              │
   └───────────────────────┴──────────────────────────┘
                                                   │
                                                   ▼
                                            ┌─────────┐
                                            │ FRAME   │
                                            │ DROP!   │
                                            │ (jank)  │
                                            └─────────┘
```

---

## Layout Pass

### Когда срабатывает Layout Pass

```
LAYOUT PASS TRIGGERS
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────┐
  │                    DIRTY FLAGS SYSTEM                           │
  │                                                                  │
  │  ┌──────────────────┐     ┌──────────────────┐                 │
  │  │  setNeedsLayout()│     │layoutIfNeeded()  │                 │
  │  │  ─────────────── │     │────────────────  │                 │
  │  │  Ставит флаг     │     │Немедленный layout│                 │
  │  │  "нужен layout"  │     │если флаг стоит   │                 │
  │  │  (async)         │     │(sync)            │                 │
  │  └─────────┬────────┘     └────────┬─────────┘                 │
  │            │                       │                            │
  │            └───────────┬───────────┘                            │
  │                        ▼                                        │
  │            ┌───────────────────────┐                           │
  │            │   layoutSubviews()    │                           │
  │            │   (вызывается системой)│                           │
  │            └───────────────────────┘                           │
  └─────────────────────────────────────────────────────────────────┘

  АВТОМАТИЧЕСКИЕ ТРИГГЕРЫ:
  • Изменение bounds/frame view
  • Добавление/удаление subview
  • Изменение constraints
  • Вращение устройства
  • safeAreaInsets изменились
```

### Порядок вызовов в Layout Pass

```
LAYOUT PASS ORDER
═══════════════════════════════════════════════════════════════════════

  1. UPDATE CONSTRAINTS (снизу вверх - от leaves к root)
     ┌─────────────────────────────────────────────────────┐
     │                                                      │
     │         RootView                                    │
     │            ▲                                         │
     │            │ 3. updateConstraints()                 │
     │    ┌───────┴───────┐                                │
     │    │               │                                │
     │    ▼               ▼                                │
     │ ChildA          ChildB                              │
     │    ▲               ▲                                │
     │    │ 2.            │ 2. updateConstraints()        │
     │    │               │                                │
     │ Leaf1           Leaf2                               │
     │    ▲               ▲                                │
     │    │ 1.            │ 1. updateConstraints()        │
     └─────────────────────────────────────────────────────┘

  2. LAYOUT SUBVIEWS (сверху вниз - от root к leaves)
     ┌─────────────────────────────────────────────────────┐
     │                                                      │
     │         RootView                                    │
     │            │                                         │
     │            │ 1. layoutSubviews()                    │
     │    ┌───────▼───────┐                                │
     │    │               │                                │
     │    │               │                                │
     │ ChildA          ChildB                              │
     │    │               │                                │
     │    │ 2.            │ 2. layoutSubviews()           │
     │    │               │                                │
     │ Leaf1           Leaf2                               │
     │    │               │                                │
     │    ▼ 3.            ▼ 3. layoutSubviews()           │
     └─────────────────────────────────────────────────────┘
```

### Код: правильное использование Layout Pass

```swift
// MARK: - Layout Pass API

class CustomView: UIView {

    // MARK: - Constraints Phase

    // ✅ Переопределяем для динамических constraints
    override func updateConstraints() {
        // Вызывается снизу-вверх (от leaves к root)
        // Изменяем constraints здесь

        if needsCompactLayout {
            stackView.axis = .vertical
            imageHeightConstraint.constant = 100
        } else {
            stackView.axis = .horizontal
            imageHeightConstraint.constant = 200
        }

        // ВАЖНО: вызвать super в конце!
        super.updateConstraints()
    }

    // MARK: - Layout Phase

    // ✅ Переопределяем для manual layout или post-constraint adjustments
    override func layoutSubviews() {
        // Вызывается сверху-вниз (от root к leaves)
        super.layoutSubviews() // ВАЖНО: вызвать super первым!

        // После super все subviews имеют правильные frames
        // Здесь можно делать финальные корректировки

        gradientLayer.frame = bounds
        shadowLayer.shadowPath = UIBezierPath(
            roundedRect: bounds,
            cornerRadius: layer.cornerRadius
        ).cgPath
    }

    // MARK: - Triggering Layout

    func configureForState(_ state: ViewState) {
        self.state = state

        // ❌ ПЛОХО: вызывать layoutSubviews() напрямую
        // layoutSubviews() // НЕ ДЕЛАТЬ!

        // ✅ ХОРОШО: пометить что нужен layout (async)
        setNeedsLayout()

        // ✅ Если нужен немедленный layout (sync)
        // layoutIfNeeded()
    }

    // MARK: - Анимация с layoutIfNeeded

    func animateExpansion() {
        // 1. Изменяем constraint
        heightConstraint.constant = 200

        // 2. Анимируем layout
        UIView.animate(withDuration: 0.3) {
            self.layoutIfNeeded() // Форсирует layout внутри анимации
        }
    }
}
```

### Auto Layout Engine

```
AUTO LAYOUT ENGINE (Cassowary Algorithm)
═══════════════════════════════════════════════════════════════════════

  INPUT: Набор constraints (линейные уравнения)
  ┌─────────────────────────────────────────────────────────────────┐
  │  button.leading = superview.leading + 16                        │
  │  button.trailing = superview.trailing - 16                      │
  │  button.height = 44                                             │
  │  button.top = label.bottom + 8                                  │
  │  label.centerX = superview.centerX                              │
  └─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │               CASSOWARY SIMPLEX SOLVER                          │
  │                                                                  │
  │  • Преобразует constraints в систему линейных уравнений        │
  │  • Решает систему с приоритетами (required, high, low)         │
  │  • Инкрементальные обновления (не пересчитывает всё)           │
  │  • Complexity: O(n) для типичных изменений                     │
  └─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  OUTPUT: Конкретные frames
  ┌─────────────────────────────────────────────────────────────────┐
  │  button.frame = (16, 108, 343, 44)                              │
  │  label.frame = (137, 79, 100, 21)                               │
  └─────────────────────────────────────────────────────────────────┘
```

---

## Display Pass

### Когда срабатывает Display Pass

```
DISPLAY PASS TRIGGERS
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────┐
  │                       BACKING STORE                             │
  │                                                                  │
  │  UIView содержит CALayer, который имеет backing store -         │
  │  bitmap в памяти с отрисованным содержимым view                 │
  │                                                                  │
  │  ┌─────────────────────┐                                        │
  │  │      UIView         │                                        │
  │  │  ┌───────────────┐  │                                        │
  │  │  │   CALayer     │  │                                        │
  │  │  │  ┌─────────┐  │  │                                        │
  │  │  │  │ Backing │  │  │  ← Bitmap в GPU памяти                │
  │  │  │  │ Store   │  │  │                                        │
  │  │  │  └─────────┘  │  │                                        │
  │  │  └───────────────┘  │                                        │
  │  └─────────────────────┘                                        │
  └─────────────────────────────────────────────────────────────────┘

  ТРИГГЕРЫ setNeedsDisplay():
  • Изменение bounds (если contentMode != .scaleToFill)
  • Изменение содержимого (текст, изображение)
  • Явный вызов setNeedsDisplay()

  НЕ ВЫЗЫВАЮТ перерисовку:
  • Изменение frame (только position, не bounds)
  • Изменение transform
  • Изменение alpha, hidden
  • Изменение backgroundColor (если не custom draw)
```

### Код: Custom Drawing

```swift
// MARK: - Display Pass API

class GradientProgressView: UIView {

    var progress: CGFloat = 0 {
        didSet {
            // ✅ Помечаем что нужна перерисовка
            setNeedsDisplay()
        }
    }

    // ✅ draw(_:) вызывается системой когда нужна перерисовка
    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext() else { return }

        // Фон
        context.setFillColor(UIColor.systemGray5.cgColor)
        context.fill(rect)

        // Прогресс с градиентом
        let progressRect = CGRect(
            x: 0,
            y: 0,
            width: rect.width * progress,
            height: rect.height
        )

        let colors = [UIColor.systemBlue.cgColor, UIColor.systemPurple.cgColor]
        let gradient = CGGradient(
            colorsSpace: CGColorSpaceCreateDeviceRGB(),
            colors: colors as CFArray,
            locations: [0, 1]
        )!

        context.clip(to: progressRect)
        context.drawLinearGradient(
            gradient,
            start: .zero,
            end: CGPoint(x: rect.width, y: 0),
            options: []
        )
    }

    // MARK: - Content Mode

    override var contentMode: UIView.ContentMode {
        didSet {
            // ❌ ПЛОХО: .scaleToFill растягивает backing store без перерисовки
            // ✅ ХОРОШО: .redraw вызывает draw(_:) при изменении bounds
            if contentMode == .redraw {
                // Правильно для custom drawing views
            }
        }
    }
}

// MARK: - Когда НЕ использовать custom draw

class EfficientView: UIView {

    // ✅ Для простых случаев используем layer properties
    func setupAppearance() {
        // Это НЕ требует custom draw
        backgroundColor = .systemBackground
        layer.cornerRadius = 12
        layer.borderWidth = 1
        layer.borderColor = UIColor.separator.cgColor

        // Для градиента - CAGradientLayer вместо draw()
        let gradient = CAGradientLayer()
        gradient.colors = [UIColor.red.cgColor, UIColor.blue.cgColor]
        gradient.frame = bounds
        layer.insertSublayer(gradient, at: 0)
    }
}
```

### Backing Store и память

```
BACKING STORE MEMORY
═══════════════════════════════════════════════════════════════════════

  РАСЧЁТ ПАМЯТИ:

  iPhone 15 Pro Max: 2796 x 1290 @ 3x = 430 x 932 points
  Full-screen backing store = 2796 × 1290 × 4 bytes (RGBA) = ~14.4 MB

  ┌─────────────────────────────────────────────────────────────────┐
  │  View Size    │  @2x Memory   │  @3x Memory   │  Notes         │
  ├───────────────┼───────────────┼───────────────┼────────────────┤
  │  100×100 pt   │   160 KB      │   360 KB      │  Small view    │
  │  375×667 pt   │   4.0 MB      │   9.0 MB      │  Full screen   │
  │  1000×1000 pt │   16 MB       │   36 MB       │  Large canvas  │
  └─────────────────────────────────────────────────────────────────┘

  ОПТИМИЗАЦИИ:
  • opaque = true → нет alpha channel → 25% меньше памяти (RGB vs RGBA)
  • drawsAsynchronously = true → отрисовка на background thread
  • Не создавать backing store для container views (clearsContextBeforeDrawing)
```

---

## Commit Transaction

### CATransaction

```
CATRANSACTION - ATOMIC COMMIT
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────┐
  │                    IMPLICIT TRANSACTION                         │
  │                                                                  │
  │  // Каждое изменение layer property создаёт implicit transaction │
  │  view.layer.opacity = 0.5  // ← implicit transaction start     │
  │  view.layer.position = CGPoint(x: 100, y: 100)                 │
  │  view.layer.transform = CATransform3DMakeScale(2, 2, 1)        │
  │  // ← implicit transaction commit at end of run loop           │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │                    EXPLICIT TRANSACTION                         │
  │                                                                  │
  │  CATransaction.begin()                                          │
  │  CATransaction.setAnimationDuration(0.5)                        │
  │  CATransaction.setDisableActions(true) // Без анимации         │
  │                                                                  │
  │  view1.layer.opacity = 0                                        │
  │  view2.layer.position = newPosition                             │
  │  view3.layer.transform = rotation                               │
  │                                                                  │
  │  CATransaction.setCompletionBlock {                             │
  │      print("Все изменения применены")                           │
  │  }                                                               │
  │                                                                  │
  │  CATransaction.commit()                                         │
  └─────────────────────────────────────────────────────────────────┘
```

### Encoding Layer Tree

```
LAYER TREE ENCODING
═══════════════════════════════════════════════════════════════════════

  APP PROCESS                           RENDER SERVER
  ┌─────────────────────────┐           ┌─────────────────────────┐
  │                         │           │                         │
  │  LAYER TREE (Model)     │   IPC     │  RENDER TREE (Shadow)   │
  │  ┌───────────────┐      │  ═════►   │  ┌───────────────┐      │
  │  │  CALayer      │      │  Mach     │  │  Copy of      │      │
  │  │  ├─ position  │      │  message  │  │  layer data   │      │
  │  │  ├─ bounds    │      │           │  │  for GPU      │      │
  │  │  ├─ transform │      │           │  │               │      │
  │  │  ├─ contents  │      │           │  │               │      │
  │  │  └─ sublayers │      │           │  │               │      │
  │  │      ├─ ...   │      │           │  │               │      │
  │  │      └─ ...   │      │           │  │               │      │
  │  └───────────────┘      │           │  └───────────────┘      │
  │                         │           │                         │
  └─────────────────────────┘           └─────────────────────────┘

  КОДИРУЕМЫЕ ДАННЫЕ:
  • Geometry: position, bounds, anchorPoint, transform
  • Visual: backgroundColor, borderColor, shadowColor
  • Content: contents (CGImage reference), contentsRect
  • Hierarchy: sublayers, mask, superlayer reference
  • Effects: filters, compositingFilter, opacity
```

### Код: работа с CATransaction

```swift
// MARK: - CATransaction Examples

class TransactionExamples {

    // MARK: - Отключение implicit animations

    func moveWithoutAnimation(view: UIView, to point: CGPoint) {
        // ❌ Это создаст анимацию (implicit animation)
        // view.layer.position = point

        // ✅ Отключаем анимацию через transaction
        CATransaction.begin()
        CATransaction.setDisableActions(true)
        view.layer.position = point
        CATransaction.commit()

        // ✅ Альтернатива: UIView.performWithoutAnimation
        UIView.performWithoutAnimation {
            view.layer.position = point
        }
    }

    // MARK: - Custom animation duration

    func animateWithCustomDuration(layer: CALayer) {
        CATransaction.begin()
        CATransaction.setAnimationDuration(1.0)
        CATransaction.setAnimationTimingFunction(
            CAMediaTimingFunction(name: .easeInEaseOut)
        )

        layer.opacity = 0
        layer.transform = CATransform3DMakeScale(0.5, 0.5, 1)

        CATransaction.commit()
    }

    // MARK: - Completion handler

    func animateWithCompletion(layer: CALayer) {
        CATransaction.begin()
        CATransaction.setCompletionBlock { [weak self] in
            // Вызывается когда ВСЕ анимации в transaction завершены
            self?.onAnimationComplete()
        }

        let animation = CABasicAnimation(keyPath: "position")
        animation.toValue = CGPoint(x: 200, y: 200)
        animation.duration = 0.5
        layer.add(animation, forKey: "move")

        CATransaction.commit()
    }

    // MARK: - Nested transactions

    func nestedTransactions(layers: [CALayer]) {
        CATransaction.begin()
        CATransaction.setAnimationDuration(1.0)

        layers[0].opacity = 0.5

        // Nested transaction с другим duration
        CATransaction.begin()
        CATransaction.setAnimationDuration(0.3)
        layers[1].opacity = 0.5 // Эта анимация 0.3s
        CATransaction.commit()

        layers[2].opacity = 0.5 // Эта анимация 1.0s

        CATransaction.commit()
    }
}
```

---

## Render Server (backboardd)

### Архитектура Render Server

```
RENDER SERVER ARCHITECTURE
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────┐
  │                        iOS SYSTEM                               │
  │                                                                  │
  │  ┌──────────────────────┐        ┌──────────────────────┐      │
  │  │     APP PROCESS      │        │     APP PROCESS      │      │
  │  │    (Your App)        │        │    (Other App)       │      │
  │  │                      │        │                      │      │
  │  │  ┌────────────────┐  │        │  ┌────────────────┐  │      │
  │  │  │  Core Animation│  │        │  │  Core Animation│  │      │
  │  │  │  Layer Tree    │  │        │  │  Layer Tree    │  │      │
  │  │  └───────┬────────┘  │        │  └───────┬────────┘  │      │
  │  └──────────┼───────────┘        └──────────┼───────────┘      │
  │             │ IPC (Mach)                     │ IPC              │
  │             │                                │                  │
  │             └────────────────┬───────────────┘                  │
  │                              │                                  │
  │                              ▼                                  │
  │  ┌─────────────────────────────────────────────────────────┐   │
  │  │                  RENDER SERVER                          │   │
  │  │                  (backboardd)                           │   │
  │  │                                                          │   │
  │  │  ┌──────────────────────────────────────────────────┐   │   │
  │  │  │              RENDER TREE                         │   │   │
  │  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │   │   │
  │  │  │  │ App 1   │  │ App 2   │  │ System  │          │   │   │
  │  │  │  │ Layers  │  │ Layers  │  │ UI      │          │   │   │
  │  │  │  └─────────┘  └─────────┘  └─────────┘          │   │   │
  │  │  └──────────────────────────────────────────────────┘   │   │
  │  │                          │                              │   │
  │  │                          ▼                              │   │
  │  │  ┌──────────────────────────────────────────────────┐   │   │
  │  │  │              GPU COMPOSITOR                      │   │   │
  │  │  │  • Metal-based rendering                         │   │   │
  │  │  │  • Layer composition                             │   │   │
  │  │  │  • Transform application                         │   │   │
  │  │  │  • Blending operations                           │   │   │
  │  │  └──────────────────────────────────────────────────┘   │   │
  │  │                          │                              │   │
  │  │                          ▼                              │   │
  │  │  ┌──────────────────────────────────────────────────┐   │   │
  │  │  │              DISPLAY OUTPUT                      │   │   │
  │  │  │  • VSync synchronization                         │   │   │
  │  │  │  • Frame buffer swap                             │   │   │
  │  │  └──────────────────────────────────────────────────┘   │   │
  │  └─────────────────────────────────────────────────────────┘   │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

### Почему отдельный процесс?

```
WHY SEPARATE PROCESS?
═══════════════════════════════════════════════════════════════════════

  1. STABILITY (Стабильность)
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  Если ваше приложение крашится:                                 │
  │                                                                  │
  │  ┌──────────────┐              ┌──────────────────────────┐    │
  │  │   APP        │   crash!     │    RENDER SERVER         │    │
  │  │   PROCESS    │ ──────X──►   │    продолжает работать   │    │
  │  │              │              │    показывает последний  │    │
  │  └──────────────┘              │    кадр или анимацию    │    │
  │                                └──────────────────────────┘    │
  │                                                                  │
  │  Пользователь видит плавный переход вместо замороженного UI    │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  2. PERFORMANCE (Производительность)
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  Frame N:                      Frame N+1:                       │
  │  ┌──────────────┐              ┌──────────────────────────┐    │
  │  │   APP        │              │    APP готовит           │    │
  │  │   commit     │              │    следующий кадр        │    │
  │  └──────┬───────┘              │    ПАРАЛЛЕЛЬНО!          │    │
  │         │                      └──────────────────────────┘    │
  │         ▼                                                       │
  │  ┌──────────────────────────┐                                  │
  │  │    RENDER SERVER         │                                  │
  │  │    рендерит кадр N       │                                  │
  │  └──────────────────────────┘                                  │
  │                                                                  │
  │  App CPU и GPU работают параллельно = больше времени на кадр   │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  3. ANIMATION INDEPENDENCE (Независимость анимаций)
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  CABasicAnimation продолжает работать даже если main thread    │
  │  заблокирован:                                                  │
  │                                                                  │
  │  ┌──────────────┐              ┌──────────────────────────┐    │
  │  │   APP        │   blocked    │    RENDER SERVER         │    │
  │  │   doing      │              │    крутит spinner        │    │
  │  │   heavy work │              │    анимирует transition  │    │
  │  └──────────────┘              │    без участия app       │    │
  │                                └──────────────────────────┘    │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

---

## Off-Screen Rendering

### Что вызывает Off-Screen Rendering

```
OFF-SCREEN RENDERING TRIGGERS
═══════════════════════════════════════════════════════════════════════

  NORMAL RENDERING:                OFF-SCREEN RENDERING:
  ┌────────────────────┐           ┌────────────────────┐
  │                    │           │                    │
  │  Layer → GPU →     │           │  Layer → Off-screen│
  │  Frame Buffer      │           │  Buffer → GPU →    │
  │                    │           │  Frame Buffer      │
  │  (1 pass)          │           │  (2+ passes)       │
  │                    │           │                    │
  └────────────────────┘           └────────────────────┘

  ТРИГГЕРЫ OFF-SCREEN RENDERING:

  ┌─────────────────────────────────────────────────────────────────┐
  │  TRIGGER                    │  SEVERITY  │  NOTES               │
  ├─────────────────────────────┼────────────┼──────────────────────┤
  │  cornerRadius + clipsToBounds│  HIGH     │  Самый частый        │
  │  + masksToBounds            │            │  источник проблем    │
  ├─────────────────────────────┼────────────┼──────────────────────┤
  │  mask (CALayer.mask)        │  HIGH      │  Всегда off-screen   │
  ├─────────────────────────────┼────────────┼──────────────────────┤
  │  shadow без shadowPath      │  HIGH      │  GPU считает форму   │
  ├─────────────────────────────┼────────────┼──────────────────────┤
  │  group opacity              │  MEDIUM    │  allowsGroupOpacity  │
  │  (opacity < 1 + subviews)   │            │                      │
  ├─────────────────────────────┼────────────┼──────────────────────┤
  │  shouldRasterize = true     │  VARIES    │  Может помочь или    │
  │                             │            │  навредить           │
  ├─────────────────────────────┼────────────┼──────────────────────┤
  │  edge antialiasing          │  LOW       │  allowsEdgeAntialiasing│
  └─────────────────────────────┴────────────┴──────────────────────┘
```

### Off-Screen Rendering детально

```
OFF-SCREEN RENDERING MECHANICS
═══════════════════════════════════════════════════════════════════════

  ПРИМЕР: cornerRadius + clipsToBounds

  БЕЗ clipsToBounds (нет off-screen):
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  layer.cornerRadius = 10                                        │
  │  layer.clipsToBounds = false                                    │
  │                                                                  │
  │  ┌─────────────────────┐                                        │
  │  │╭───────────────────╮│  GPU просто рисует                    │
  │  ││                   ││  прямоугольник с                      │
  │  ││   Content         ││  закруглёнными углами                 │
  │  ││   может выходить  ││  (background layer)                   │
  │  ││   за границы!     ││                                        │
  │  │╰───────────────────╯│                                        │
  │  └─────────────────────┘                                        │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  С clipsToBounds (off-screen rendering!):
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  layer.cornerRadius = 10                                        │
  │  layer.clipsToBounds = true  // ← ПРОБЛЕМА!                    │
  │                                                                  │
  │  PASS 1: Создаём off-screen buffer                             │
  │  ┌─────────────────────┐                                        │
  │  │                     │  Рисуем ВСЕ sublayers                 │
  │  │   ┌───────────────┐ │  во временный буфер                   │
  │  │   │   Image       │ │                                        │
  │  │   └───────────────┘ │                                        │
  │  │   ┌───────────────┐ │                                        │
  │  │   │   Label       │ │                                        │
  │  │   └───────────────┘ │                                        │
  │  └─────────────────────┘                                        │
  │                                                                  │
  │  PASS 2: Применяем mask и копируем в frame buffer              │
  │  ╭─────────────────────╮                                        │
  │  │╭───────────────────╮│  Обрезаем по rounded rect             │
  │  ││   Final Result    ││  и копируем в основной                │
  │  │╰───────────────────╯│  frame buffer                         │
  │  ╰─────────────────────╯                                        │
  │                                                                  │
  │  CONTEXT SWITCH на GPU = ~1ms задержки!                        │
  └─────────────────────────────────────────────────────────────────┘
```

### Как избежать Off-Screen Rendering

```swift
// MARK: - Off-Screen Rendering Solutions

class OptimizedView: UIView {

    // MARK: - ❌ ПРОБЛЕМА: cornerRadius + clipsToBounds

    func badCornerRadius() {
        imageView.layer.cornerRadius = 20
        imageView.clipsToBounds = true  // ← OFF-SCREEN!
    }

    // MARK: - ✅ РЕШЕНИЕ 1: Только cornerRadius (без clipsToBounds)

    func goodCornerRadiusBackground() {
        // Работает если нет sublayers, выходящих за границы
        containerView.layer.cornerRadius = 20
        containerView.backgroundColor = .systemBackground
        // clipsToBounds = false (по умолчанию)
    }

    // MARK: - ✅ РЕШЕНИЕ 2: Pre-rendered rounded image

    func preRenderRoundedImage(image: UIImage, radius: CGFloat) -> UIImage {
        let rect = CGRect(origin: .zero, size: image.size)

        UIGraphicsBeginImageContextWithOptions(image.size, false, image.scale)
        defer { UIGraphicsEndImageContext() }

        UIBezierPath(roundedRect: rect, cornerRadius: radius).addClip()
        image.draw(in: rect)

        return UIGraphicsGetImageFromCurrentImageContext()!
    }

    // MARK: - ❌ ПРОБЛЕМА: Shadow без shadowPath

    func badShadow() {
        view.layer.shadowColor = UIColor.black.cgColor
        view.layer.shadowOffset = CGSize(width: 0, height: 2)
        view.layer.shadowRadius = 4
        view.layer.shadowOpacity = 0.3
        // shadowPath = nil → GPU вычисляет форму тени = OFF-SCREEN!
    }

    // MARK: - ✅ РЕШЕНИЕ: Указать shadowPath

    func goodShadow() {
        view.layer.shadowColor = UIColor.black.cgColor
        view.layer.shadowOffset = CGSize(width: 0, height: 2)
        view.layer.shadowRadius = 4
        view.layer.shadowOpacity = 0.3

        // ✅ Указываем путь тени явно
        view.layer.shadowPath = UIBezierPath(
            roundedRect: view.bounds,
            cornerRadius: view.layer.cornerRadius
        ).cgPath
    }

    // ✅ Обновляем shadowPath при изменении размера
    override func layoutSubviews() {
        super.layoutSubviews()
        layer.shadowPath = UIBezierPath(
            roundedRect: bounds,
            cornerRadius: layer.cornerRadius
        ).cgPath
    }

    // MARK: - ✅ РЕШЕНИЕ: shouldRasterize для статичного контента

    func rasterizeStaticContent() {
        // Для view которые НЕ меняются часто
        complexView.layer.shouldRasterize = true
        complexView.layer.rasterizationScale = UIScreen.main.scale

        // GPU кэширует отрисованный результат
        // ⚠️ НЕ использовать для анимируемого контента!
    }

    // MARK: - ✅ iOS 13+: cornerCurve

    func modernCornerRadius() {
        if #available(iOS 13.0, *) {
            // Continuous curve как в системных приложениях Apple
            view.layer.cornerCurve = .continuous
            view.layer.cornerRadius = 20
        }
    }

    // MARK: - ❌ ПРОБЛЕМА: mask layer

    func badMask() {
        let maskLayer = CAShapeLayer()
        maskLayer.path = customPath.cgPath
        view.layer.mask = maskLayer  // ← ВСЕГДА OFF-SCREEN!
    }

    // MARK: - ✅ РЕШЕНИЕ: Pre-render masked content

    func preRenderMaskedContent() -> UIImage {
        let renderer = UIGraphicsImageRenderer(size: bounds.size)
        return renderer.image { context in
            customPath.addClip()
            contentLayer.render(in: context.cgContext)
        }
    }
}
```

### Дебаг Off-Screen Rendering

```
DEBUG OFF-SCREEN RENDERING
═══════════════════════════════════════════════════════════════════════

  SIMULATOR DEBUG OPTIONS:
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  Debug Menu → Color Off-screen Rendered                         │
  │                                                                  │
  │  ┌─────────────────────────────────────────────────────────┐   │
  │  │                                                          │   │
  │  │   ┌──────────────────────────────────────────────────┐  │   │
  │  │   │ YELLOW = Off-screen rendered                    │  │   │
  │  │   │ (этот view замедляет рендеринг)                │  │   │
  │  │   └──────────────────────────────────────────────────┘  │   │
  │  │                                                          │   │
  │  │   ┌──────────────────────────────────────────────────┐  │   │
  │  │   │ GREEN = Cached (shouldRasterize)                │  │   │
  │  │   │ (закэшировано, OK)                              │  │   │
  │  │   └──────────────────────────────────────────────────┘  │   │
  │  │                                                          │   │
  │  └─────────────────────────────────────────────────────────┘   │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  INSTRUMENTS - Core Animation:
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  Instruments → Core Animation → Recording Options:              │
  │                                                                  │
  │  ☑ Color Offscreen-Rendered Yellow                             │
  │  ☑ Color Hits Green and Misses Red (для shouldRasterize)       │
  │  ☑ Flash Updated Regions                                        │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

---

## Color Blended Layers

### Что такое Color Blending

```
COLOR BLENDED LAYERS
═══════════════════════════════════════════════════════════════════════

  BLENDING = GPU вычисляет итоговый цвет пикселя из нескольких слоёв

  БЕЗ BLENDING (opaque):             С BLENDING (transparent):
  ┌────────────────────────┐         ┌────────────────────────┐
  │                        │         │                        │
  │   Layer A              │         │   Layer A (alpha 0.8)  │
  │   ┌──────────────┐     │         │   ┌──────────────┐     │
  │   │  Solid Red   │     │         │   │  Red α=0.8   │     │
  │   │  R=255       │     │         │   │              │     │
  │   │  Final=Red   │     │         │   └──────┬───────┘     │
  │   └──────────────┘     │         │          │ blend       │
  │                        │         │          ▼             │
  │   GPU: копирует        │         │   Layer B              │
  │   пиксели напрямую     │         │   ┌──────────────┐     │
  │                        │         │   │  Blue        │     │
  │                        │         │   │              │     │
  │                        │         │   │  Final=      │     │
  │                        │         │   │  0.8*Red +   │     │
  │                        │         │   │  0.2*Blue    │     │
  │                        │         │   └──────────────┘     │
  │                        │         │                        │
  │   Cost: 1x             │         │   Cost: 2x+ на пиксель│
  └────────────────────────┘         └────────────────────────┘

  ФОРМУЛА BLENDING:
  FinalColor = SourceColor × SourceAlpha + DestColor × (1 - SourceAlpha)

  Для каждого пикселя! При 1920×1080 = 2 073 600 вычислений на слой!
```

### Источники Color Blending

```
COLOR BLENDING SOURCES
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────┐
  │  SOURCE                      │  FIX                            │
  ├──────────────────────────────┼─────────────────────────────────┤
  │  backgroundColor = nil       │  Set opaque background color    │
  │  backgroundColor = .clear    │  Set opaque background color    │
  ├──────────────────────────────┼─────────────────────────────────┤
  │  UILabel (по умолчанию       │  label.backgroundColor =        │
  │  transparent background)     │  .systemBackground              │
  │                              │  label.isOpaque = true          │
  ├──────────────────────────────┼─────────────────────────────────┤
  │  PNG с alpha channel         │  Использовать JPEG или          │
  │                              │  PNG без прозрачности           │
  ├──────────────────────────────┼─────────────────────────────────┤
  │  layer.opacity < 1           │  Избегать где возможно         │
  ├──────────────────────────────┼─────────────────────────────────┤
  │  UIVisualEffectView          │  Минимизировать использование  │
  └──────────────────────────────┴─────────────────────────────────┘
```

### Дебаг Color Blending

```
DEBUG COLOR BLENDED LAYERS
═══════════════════════════════════════════════════════════════════════

  SIMULATOR DEBUG OPTIONS:
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  Debug Menu → Color Blended Layers                              │
  │                                                                  │
  │  ┌─────────────────────────────────────────────────────────┐   │
  │  │                                                          │   │
  │  │   ┌──────────────────────────────────────────────────┐  │   │
  │  │   │ GREEN = Opaque (оптимально)                     │  │   │
  │  │   │ Нет blending, GPU копирует напрямую            │  │   │
  │  │   └──────────────────────────────────────────────────┘  │   │
  │  │                                                          │   │
  │  │   ┌──────────────────────────────────────────────────┐  │   │
  │  │   │ RED = Blended (требует оптимизации)             │  │   │
  │  │   │ GPU вычисляет итоговый цвет каждого пикселя    │  │   │
  │  │   └──────────────────────────────────────────────────┘  │   │
  │  │                                                          │   │
  │  └─────────────────────────────────────────────────────────┘   │
  │                                                                  │
  │  ЦЕЛЬ: Максимум зелёного, минимум красного                     │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

### Код: оптимизация Color Blending

```swift
// MARK: - Color Blending Optimization

class OptimizedTableViewCell: UITableViewCell {

    private let titleLabel = UILabel()
    private let subtitleLabel = UILabel()
    private let avatarImageView = UIImageView()

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupOptimizedViews()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    private func setupOptimizedViews() {
        // ✅ Opaque background для cell
        contentView.backgroundColor = .systemBackground
        contentView.isOpaque = true

        // ✅ Opaque labels
        titleLabel.backgroundColor = .systemBackground
        titleLabel.isOpaque = true

        subtitleLabel.backgroundColor = .systemBackground
        subtitleLabel.isOpaque = true

        // ✅ Opaque image view
        avatarImageView.backgroundColor = .systemGray5
        avatarImageView.isOpaque = true

        // Добавляем subviews
        [titleLabel, subtitleLabel, avatarImageView].forEach {
            contentView.addSubview($0)
        }
    }

    // MARK: - ❌ vs ✅ Comparison

    func badSetup() {
        // ❌ Все views blended (красные в debug)
        titleLabel.backgroundColor = .clear      // Blended!
        subtitleLabel.backgroundColor = nil      // Blended!
        avatarImageView.backgroundColor = .clear // Blended!
    }

    func goodSetup() {
        // ✅ Все views opaque (зелёные в debug)
        let bg = UIColor.systemBackground

        titleLabel.backgroundColor = bg
        titleLabel.isOpaque = true

        subtitleLabel.backgroundColor = bg
        subtitleLabel.isOpaque = true

        avatarImageView.backgroundColor = bg
        avatarImageView.isOpaque = true
        avatarImageView.layer.masksToBounds = true
    }
}

// MARK: - Оптимизация для динамических фонов

extension UILabel {
    /// Создаёт opaque label с учётом цвета родителя
    static func makeOpaque(on backgroundColor: UIColor) -> UILabel {
        let label = UILabel()
        label.backgroundColor = backgroundColor
        label.isOpaque = true
        return label
    }
}
```

---

## Распространённые ошибки

### Ошибка 1: Блокировка main thread во время layout

```swift
// ❌ ПЛОХО: Синхронная загрузка изображения в layoutSubviews
class BadImageCell: UITableViewCell {
    override func layoutSubviews() {
        super.layoutSubviews()

        // ❌ Блокирует main thread = frame drop
        let data = try? Data(contentsOf: imageURL!)
        imageView?.image = UIImage(data: data!)
    }
}

// ✅ ХОРОШО: Асинхронная загрузка, кэширование
class GoodImageCell: UITableViewCell {
    private var currentURL: URL?

    func configure(with url: URL) {
        currentURL = url
        imageView?.image = nil  // placeholder

        // Асинхронная загрузка
        ImageCache.shared.load(url) { [weak self] image in
            guard self?.currentURL == url else { return }
            self?.imageView?.image = image
        }
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        // Только layout, никакой загрузки!
    }
}
```

### Ошибка 2: Частый вызов layoutIfNeeded в цикле

```swift
// ❌ ПЛОХО: layoutIfNeeded на каждой итерации
func badUpdateConstraints(items: [Item]) {
    for (index, item) in items.enumerated() {
        let view = views[index]
        view.widthConstraint.constant = item.width
        view.layoutIfNeeded()  // ❌ N раз layout pass!
    }
}

// ✅ ХОРОШО: Один layout pass после всех изменений
func goodUpdateConstraints(items: [Item]) {
    for (index, item) in items.enumerated() {
        let view = views[index]
        view.widthConstraint.constant = item.width
    }
    // Один layout pass для всех изменений
    containerView.layoutIfNeeded()
}
```

### Ошибка 3: cornerRadius + clipsToBounds без необходимости

```swift
// ❌ ПЛОХО: Off-screen rendering без необходимости
class BadCardView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)

        layer.cornerRadius = 12
        clipsToBounds = true  // ❌ Off-screen!
        backgroundColor = .systemBackground
    }
}

// ✅ ХОРОШО: cornerRadius без clipsToBounds когда нет overflow
class GoodCardView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)

        layer.cornerRadius = 12
        // clipsToBounds = false по умолчанию
        // Работает если subviews не выходят за bounds
        backgroundColor = .systemBackground
    }
}

// ✅ ХОРОШО: Для image - pre-render rounded
class GoodImageView: UIImageView {
    func setRoundedImage(_ image: UIImage, radius: CGFloat) {
        self.image = image.roundedImage(radius: radius)
        // Без clipsToBounds, без cornerRadius на layer
    }
}
```

### Ошибка 4: Тень без shadowPath

```swift
// ❌ ПЛОХО: GPU вычисляет shadowPath
class BadShadowView: UIView {
    func setupShadow() {
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0, height: 4)
        layer.shadowRadius = 8
        layer.shadowOpacity = 0.2
        // shadowPath = nil → Off-screen rendering!
    }
}

// ✅ ХОРОШО: Явный shadowPath
class GoodShadowView: UIView {
    func setupShadow() {
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0, height: 4)
        layer.shadowRadius = 8
        layer.shadowOpacity = 0.2
        updateShadowPath()
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        updateShadowPath()
    }

    private func updateShadowPath() {
        layer.shadowPath = UIBezierPath(
            roundedRect: bounds,
            cornerRadius: layer.cornerRadius
        ).cgPath
    }
}
```

### Ошибка 5: Анимация не-animatable properties

```swift
// ❌ ПЛОХО: Пытаемся анимировать через UIView.animate
func badAnimation() {
    UIView.animate(withDuration: 0.3) {
        // ❌ Эти properties НЕ animatable через UIView.animate
        self.label.text = "New Text"  // Не анимируется
        self.tableView.reloadData()   // Не анимируется
    }
}

// ✅ ХОРОШО: Анимируем правильные properties
func goodAnimation() {
    UIView.animate(withDuration: 0.3) {
        // ✅ Animatable properties
        self.view.alpha = 0.5
        self.view.transform = CGAffineTransform(scaleX: 1.1, y: 1.1)
        self.view.backgroundColor = .red
        self.constraint.constant = 100
        self.view.layoutIfNeeded()  // Для constraint анимации
    }
}

// ✅ Для text изменений - используем transition
func animateTextChange() {
    UIView.transition(
        with: label,
        duration: 0.3,
        options: .transitionCrossDissolve
    ) {
        self.label.text = "New Text"
    }
}
```

### Ошибка 6: Избыточные setNeedsDisplay

```swift
// ❌ ПЛОХО: setNeedsDisplay на каждое изменение
class BadProgressView: UIView {
    var progress: CGFloat = 0 {
        didSet {
            // ❌ Если меняется 60 раз в секунду - 60 перерисовок!
            setNeedsDisplay()
        }
    }
}

// ✅ ХОРОШО: Throttle или использовать CALayer
class GoodProgressView: UIView {
    private let progressLayer = CAShapeLayer()

    var progress: CGFloat = 0 {
        didSet {
            // ✅ CALayer не требует перерисовки backing store
            CATransaction.begin()
            CATransaction.setDisableActions(true)
            progressLayer.strokeEnd = progress
            CATransaction.commit()
        }
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        layer.addSublayer(progressLayer)
        progressLayer.strokeColor = UIColor.systemBlue.cgColor
        progressLayer.fillColor = nil
        progressLayer.lineWidth = 4
    }

    required init?(coder: NSCoder) { fatalError() }

    override func layoutSubviews() {
        super.layoutSubviews()
        progressLayer.path = UIBezierPath(
            arcCenter: CGPoint(x: bounds.midX, y: bounds.midY),
            radius: bounds.width / 2 - 2,
            startAngle: -.pi / 2,
            endAngle: .pi * 3 / 2,
            clockwise: true
        ).cgPath
    }
}
```

---

## Ментальные модели

### Модель 1: Render Loop как железнодорожное расписание

```
МЕНТАЛЬНАЯ МОДЕЛЬ: ЖЕЛЕЗНАЯ ДОРОГА
═══════════════════════════════════════════════════════════════════════

  VSync = поезд, отправляющийся СТРОГО по расписанию каждые 16.67ms

  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  СТАНЦИЯ "КАДР N"          СТАНЦИЯ "КАДР N+1"                   │
  │        │                          │                             │
  │        │    ← 16.67ms →           │                             │
  │        │                          │                             │
  │   🚂═══════════════════════════════════════════════════🚂       │
  │   ПОЕЗД N                        ПОЕЗД N+1                      │
  │                                                                  │
  │   Если ваш "пассажир" (кадр) опоздал на поезд:                 │
  │   → Он ждёт следующий = frame drop = jank                      │
  │                                                                  │
  │   ✅ ХОРОШО: Пассажир приходит заранее                          │
  │   ❌ ПЛОХО: Пассажир опоздал → ждёт следующий поезд            │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ПРИМЕНЕНИЕ:
  • Профилируйте: укладываетесь ли вы в 16.67ms?
  • Сложные операции делите на части (несколько "поездов")
  • Тяжёлую работу выносите на background thread
```

### Модель 2: GPU как дорогой принтер

```
МЕНТАЛЬНАЯ МОДЕЛЬ: GPU = ПРИНТЕР
═══════════════════════════════════════════════════════════════════════

  GPU - как очень быстрый принтер, но:
  • Каждый контекст switch = новый лист бумаги
  • Off-screen rendering = печать на черновик, потом копирование
  • Blending = печать полупрозрачными чернилами (дороже)

  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  OPAQUE LAYER:                OFF-SCREEN LAYER:                 │
  │  ┌─────────────┐              ┌─────────────┐                   │
  │  │             │              │   DRAFT     │                   │
  │  │  DIRECT     │              │   PAPER     │                   │
  │  │  PRINT      │              │   ↓         │                   │
  │  │  ↓          │              │   COPY      │                   │
  │  │  DONE!      │              │   ↓         │                   │
  │  └─────────────┘              │   FINAL     │                   │
  │                               └─────────────┘                   │
  │  Cost: 1x                     Cost: 2-3x                        │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ПРИМЕНЕНИЕ:
  • Минимизируйте "черновики" (off-screen rendering)
  • Используйте "непрозрачные чернила" (opaque backgrounds)
  • Кэшируйте "копии" где возможно (shouldRasterize)
```

### Модель 3: Layout как GPS навигация

```
МЕНТАЛЬНАЯ МОДЕЛЬ: LAYOUT = GPS
═══════════════════════════════════════════════════════════════════════

  Auto Layout = GPS с ограничениями:
  • Constraints = "не ближе 16pt от края", "по центру экрана"
  • Layout pass = GPS пересчитывает маршрут
  • layoutIfNeeded = "покажи маршрут СЕЙЧАС"
  • setNeedsLayout = "пересчитай маршрут когда будет время"

  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  CONSTRAINTS:                                                    │
  │  "Button в 20pt от правого края"                                │
  │  "Label под Button с отступом 8pt"                              │
  │                                                                  │
  │                    ↓ Cassowary Solver                           │
  │                                                                  │
  │  FRAMES (конкретные координаты):                                │
  │  Button: (255, 100, 100, 44)                                    │
  │  Label: (255, 152, 100, 21)                                     │
  │                                                                  │
  │  Как GPS: "поверни направо через 100 метров"                   │
  │           превращается в конкретные GPS координаты              │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ПРИМЕНЕНИЕ:
  • Conflicting constraints = GPS не может построить маршрут
  • Priority = какое ограничение важнее при конфликте
  • intrinsicContentSize = "минимальный размер чтобы всё поместилось"
```

### Модель 4: Render Server как отдельная кухня

```
МЕНТАЛЬНАЯ МОДЕЛЬ: РЕСТОРАН
═══════════════════════════════════════════════════════════════════════

  App Process = зал ресторана (принимает заказы, общается с клиентами)
  Render Server = кухня в подвале (готовит блюда)

  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  ЗАЛ (App Process):                                             │
  │  • Официант принимает заказ (user events)                       │
  │  • Записывает в бланк (CATransaction)                           │
  │  • Спускает лифтом на кухню (IPC)                              │
  │                                                                  │
  │  КУХНЯ (Render Server):                                         │
  │  • Готовит блюда (GPU composition)                              │
  │  • Не зависит от зала (crash isolation)                        │
  │  • Работает параллельно (performance)                           │
  │                                                                  │
  │  ПРЕИМУЩЕСТВА:                                                  │
  │  • Если официант упал - кухня продолжает работать               │
  │  • Зал может принимать новые заказы пока готовятся старые      │
  │  • Анимация на тарелке (CABasicAnimation) продолжается         │
  │    даже если официант занят                                     │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘
```

### Модель 5: Off-Screen как фотокопия

```
МЕНТАЛЬНАЯ МОДЕЛЬ: ФОТОКОПИЯ
═══════════════════════════════════════════════════════════════════════

  Обычный рендеринг = напечатать документ
  Off-screen rendering = напечатать, отксерить, вырезать форму, наклеить

  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  ОБЫЧНО:                     OFF-SCREEN:                        │
  │  ┌─────────────┐             ┌─────────────┐                    │
  │  │ PRINT       │             │ PRINT       │                    │
  │  │    ↓        │             │    ↓        │                    │
  │  │ DONE        │             │ XEROX       │                    │
  │  └─────────────┘             │    ↓        │                    │
  │                              │ CUT SHAPE   │                    │
  │  Время: T                    │    ↓        │                    │
  │                              │ PASTE       │                    │
  │                              └─────────────┘                    │
  │                              Время: 3T+                         │
  │                                                                  │
  │  cornerRadius + clipsToBounds = "вырежи по контуру"            │
  │  mask = "наложи трафарет и вырежи"                             │
  │  shadow без path = "обведи тень по контуру фигуры"             │
  │                                                                  │
  └─────────────────────────────────────────────────────────────────┘

  ПРИМЕНЕНИЕ:
  • Избегайте "ксерокопий" где возможно
  • Pre-render если контент статичный
  • Кэшируйте "вырезанные" изображения
```

---

## Проверь себя

### Вопрос 1: Timing Budget

**Вопрос:** У вас iPhone 15 Pro с ProMotion дисплеем на 120Hz. Сколько миллисекунд у вас есть на подготовку одного кадра?

<details>
<summary><b>Ответ</b></summary>

**8.33ms** (1000ms / 120fps = 8.33ms)

При этом:
- ~4-6ms на app process (layout, display, commit)
- ~2-4ms на render server (GPU composition)

Это в 2 раза меньше чем стандартные 16.67ms для 60fps, поэтому на ProMotion устройствах оптимизация особенно критична.

ProMotion может динамически менять refresh rate (24-120Hz) в зависимости от контента, но если ваша анимация рассчитана на 120fps, нужно укладываться в 8.33ms.

</details>

### Вопрос 2: Layout Pass Order

**Вопрос:** В каком порядке вызываются методы layout pass? Расположите в правильной последовательности:
- layoutSubviews() на RootView
- updateConstraints() на ChildView
- layoutSubviews() на ChildView
- updateConstraints() на RootView

<details>
<summary><b>Ответ</b></summary>

Правильный порядок:

1. **updateConstraints() на ChildView** (снизу вверх)
2. **updateConstraints() на RootView** (снизу вверх)
3. **layoutSubviews() на RootView** (сверху вниз)
4. **layoutSubviews() на ChildView** (сверху вниз)

Запомнить: **Constraints снизу-вверх, Layout сверху-вниз**

Это потому что:
- Constraints: дочерние views сначала определяют свои требования, потом родители
- Layout: родители сначала определяют свой frame, потом позиционируют детей

</details>

### Вопрос 3: Off-Screen Rendering

**Вопрос:** Какой из этих вариантов НЕ вызывает off-screen rendering?

A) `layer.cornerRadius = 10` + `clipsToBounds = true`
B) `layer.mask = maskLayer`
C) `layer.shadowOpacity = 0.5` + `layer.shadowPath = path`
D) `layer.shadowOpacity = 0.5` (без shadowPath)

<details>
<summary><b>Ответ</b></summary>

**C) layer.shadowOpacity = 0.5 + layer.shadowPath = path**

Объяснение:
- A) ❌ cornerRadius + clipsToBounds = off-screen (GPU должен обрезать содержимое)
- B) ❌ mask = всегда off-screen (GPU применяет маску)
- **C) ✅ shadow с shadowPath = НЕТ off-screen** (GPU знает форму тени, не вычисляет)
- D) ❌ shadow без shadowPath = off-screen (GPU должен вычислить форму тени)

Ключевой insight: Указание shadowPath даёт GPU готовый путь тени, и ему не нужно анализировать форму layer для вычисления тени.

</details>

### Вопрос 4: setNeedsLayout vs layoutIfNeeded

**Вопрос:** Вы хотите анимировать изменение constraint. Какой код правильный?

```swift
// Вариант A
heightConstraint.constant = 200
setNeedsLayout()
UIView.animate(withDuration: 0.3) {
    // ничего
}

// Вариант B
UIView.animate(withDuration: 0.3) {
    self.heightConstraint.constant = 200
    self.setNeedsLayout()
}

// Вариант C
heightConstraint.constant = 200
UIView.animate(withDuration: 0.3) {
    self.layoutIfNeeded()
}
```

<details>
<summary><b>Ответ</b></summary>

**Вариант C** - правильный!

```swift
heightConstraint.constant = 200
UIView.animate(withDuration: 0.3) {
    self.layoutIfNeeded()
}
```

Объяснение:
- **A)** Неправильно: setNeedsLayout только помечает view, анимация пустая
- **B)** Неправильно: изменение constraint внутри animate block не анимируется
- **C)** Правильно:
  1. Изменяем constraint ДО animation block
  2. layoutIfNeeded() ВНУТРИ animation block форсирует layout
  3. Core Animation интерполирует разницу между старым и новым frame

Паттерн: **Change constraint → Animate layoutIfNeeded()**

</details>

---

## Связанные темы

### Prerequisites (Необходимые знания)
- [[ios-graphics-fundamentals]] - Основы Core Graphics, координатные системы
- [[ios-uikit-fundamentals]] - UIView, CALayer базовые концепции
- [[ios-viewcontroller-lifecycle]] - Lifecycle и когда происходит layout

### Next Steps (Следующие темы)
- [[ios-performance-profiling]] - Instruments, Time Profiler, Core Animation profiler
- [[ios-scroll-performance]] - Оптимизация UITableView/UICollectionView
- [[ios-animation-deep-dive]] - CAAnimation, UIViewPropertyAnimator

### Related Topics (Связанные темы)
- [[android-view-rendering-pipeline]] - Сравнение с Android Choreographer/VSYNC
- [[ios-metal-basics]] - Low-level GPU programming на iOS
- [[ios-core-animation]] - CALayer hierarchy и advanced animations

---

## Источники

### WWDC Sessions
- **WWDC 2012 - iOS App Performance: Responsiveness** - Основы render loop
- **WWDC 2014 - Advanced Graphics and Animations for iOS Apps** - Off-screen rendering, optimizations
- **WWDC 2015 - Building Responsive and Efficient Apps with GCD** - Main thread performance
- **WWDC 2018 - iOS Memory Deep Dive** - Backing store memory management
- **WWDC 2019 - Optimizing App Launch** - Pre-warming и render server
- **WWDC 2021 - Demystify SwiftUI** - SwiftUI render model comparison
- **WWDC 2022 - Eliminate hangs from your app** - Main thread blocking detection

### Apple Documentation
- [Core Animation Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreAnimation_guide/)
- [Drawing and Printing Guide for iOS](https://developer.apple.com/library/archive/documentation/2DDrawing/Conceptual/DrawingPrintingiOS/)
- [Auto Layout Guide](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/)

### Technical Resources
- **iOS Internals by Jonathan Levin** - backboardd, render server details
- **objc.io Issue #3: Views** - Глубокое погружение в rendering
- **AsyncDisplayKit (Texture)** - Alternative rendering approach by Facebook

### Tools
- **Instruments > Core Animation** - Профилирование rendering
- **Simulator > Debug > Color Blended Layers** - Визуализация blending
- **Simulator > Debug > Color Off-screen Rendered** - Визуализация off-screen
- **MetricKit** - Production rendering metrics

---

## Связь с другими темами

- **[[android-view-rendering-pipeline]]** — Android использует аналогичный конвейер рендеринга с Choreographer вместо CADisplayLink и RenderThread вместо Render Server (backboardd). Сравнение двух платформ показывает общие принципы: обе системы работают с VSync-синхронизацией, GPU-композицией слоёв и бюджетом времени на кадр. Понимание различий помогает при оптимизации кросс-платформенных приложений.

- **[[ios-graphics-fundamentals]]** — Core Graphics, Core Animation и Metal составляют графический стек iOS, на котором базируется весь render loop. Понимание координатных систем, CGContext, CALayer properties и их взаимосвязи с backing store критично для оптимизации отрисовки. Без знания этих основ невозможно эффективно диагностировать проблемы с off-screen rendering и color blending.

- **[[cross-graphics-rendering]]** — Кросс-платформенное сравнение графических подсистем iOS (Core Animation + Metal), Android (Skia + Vulkan) и desktop (OpenGL/Vulkan) раскрывает общие паттерны GPU-рендеринга: двойная буферизация, layer compositing, аппаратное ускорение. Эти знания помогают принимать архитектурные решения при выборе между нативным и кросс-платформенным UI.

---

## Источники и дальнейшее чтение

- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — Подробно объясняет иерархию UIView/CALayer, backing store, implicit и explicit анимации через CATransaction, что является основой для понимания render loop и оптимизации отрисовки.

- Eidhof C., Airspeed Velocity, Javier N. (2019). *Advanced Swift.* — Углублённое понимание Swift performance, включая работу с памятью и value/reference types, что напрямую влияет на эффективность layout pass и backing store allocation.

- Keur C., Hillegass A. (2020). *iOS Programming: The Big Nerd Ranch Guide.* — Практические примеры работы с Auto Layout, Core Animation и профилированием через Instruments, с пошаговыми упражнениями по оптимизации rendering performance.

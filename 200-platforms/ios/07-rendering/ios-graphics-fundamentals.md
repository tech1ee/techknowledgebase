---
title: "iOS Graphics Fundamentals: Core Graphics, Core Animation, Metal"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 121
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/graphics
  - level/intermediate
related:
  - "[[android-graphics-apis]]"
  - "[[ios-view-rendering]]"
  - "[[cross-graphics-rendering]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-uikit-fundamentals]]"
---

## TL;DR

iOS имеет многоуровневый графический стек: **Core Graphics** (Quartz 2D) для 2D-рисования на CPU, **Core Animation** для аппаратно-ускоренной композиции слоёв на GPU, и **Metal** для низкоуровневого доступа к графическому процессору. Понимание этого стека критично для создания плавного UI (60/120 fps) и эффективного использования ресурсов устройства.

Ключевой принцип: **чем выше уровень абстракции, тем меньше контроля, но проще использование**. UIKit/SwiftUI работают поверх Core Animation, который автоматически оптимизирует отрисовку через GPU.

## Зачем это нужно?

**Реальные проблемы, которые решает понимание графического стека:**

1. **Performance drops** - 60% проблем производительности UI связаны с неправильным использованием графических API (Instagram Engineering, 2024)

2. **Battery drain** - GPU rendering в 10-100x энергоэффективнее CPU rendering для одних и тех же операций (Apple WWDC 2023)

3. **Jank & stuttering** - каждый пропущенный кадр (>16.67ms при 60fps) виден пользователю как "дёрганье"

4. **Memory pressure** - неоптимизированные layer trees могут потреблять гигабайты VRAM

5. **Offscreen rendering** - одна из самых частых причин dropped frames, требует понимания внутренней работы системы

**Когда это особенно критично:**

- Custom UI components (не стандартные кнопки/лейблы)
- Сложные анимации и переходы
- Работа с изображениями и видео
- Игры и AR/VR приложения
- Приложения с real-time графикой

## Аналогии из жизни

### 1. Core Graphics = Художник с кистью (CPU, 2D)

```
┌─────────────────────────────────────────────────────────┐
│                    МАСТЕРСКАЯ ХУДОЖНИКА                  │
│                                                          │
│   Художник (CPU) берёт кисть и краски                   │
│   Рисует КАЖДЫЙ пиксель вручную                         │
│   Медленно, но полный контроль                          │
│                                                          │
│   ┌─────────┐    ┌─────────┐                            │
│   │ Кисть   │ →  │ Холст   │  = CGContext + CGPath      │
│   │(CGPath) │    │(Bitmap) │                            │
│   └─────────┘    └─────────┘                            │
│                                                          │
│   Результат: растровое изображение в памяти             │
└─────────────────────────────────────────────────────────┘

Аналогия: художник не может рисовать несколько картин
одновременно. CPU рисует последовательно, пиксель за пикселем.
```

### 2. Core Animation = Аниматор с марионетками (GPU layers)

```
┌─────────────────────────────────────────────────────────┐
│              ТЕАТР МАРИОНЕТОК                            │
│                                                          │
│   Марионетки (CALayer) уже готовы                       │
│   Аниматор только дёргает за ниточки:                   │
│   - Позиция (position)                                  │
│   - Размер (bounds)                                     │
│   - Поворот (transform)                                 │
│   - Прозрачность (opacity)                              │
│                                                          │
│      ┌───┐   ┌───┐   ┌───┐                              │
│      │ L │   │ L │   │ L │  ← Готовые текстуры в GPU    │
│      │ a │   │ a │   │ a │                              │
│      │ y │   │ y │   │ y │                              │
│      │ e │   │ e │   │ e │                              │
│      │ r │   │ r │   │ r │                              │
│      │ 1 │   │ 2 │   │ 3 │                              │
│      └─┬─┘   └─┬─┘   └─┬─┘                              │
│        │       │       │                                │
│        └───────┼───────┘                                │
│                │                                        │
│            GPU Compositor                               │
└─────────────────────────────────────────────────────────┘

Аналогия: марионетки (слои) уже нарисованы.
Движение = просто изменение их положения на сцене.
GPU делает это параллельно для тысяч слоёв.
```

### 3. Metal = Прямой доступ к краскам и холсту (low-level GPU)

```
┌─────────────────────────────────────────────────────────┐
│           ПРОМЫШЛЕННЫЙ ПРИНТЕР                           │
│                                                          │
│   Вы программируете каждую головку принтера             │
│   напрямую (shaders)                                    │
│                                                          │
│   ┌─────────────────────────────────────┐               │
│   │ MTLDevice       │ MTLCommandQueue   │               │
│   │ (принтер)       │ (очередь заданий) │               │
│   └────────┬────────┴───────────────────┘               │
│            │                                            │
│            ▼                                            │
│   ┌─────────────────────────────────────┐               │
│   │ MTLRenderPipeline                   │               │
│   │ (программа печати = шейдеры)        │               │
│   └─────────────────────────────────────┘               │
│                                                          │
│   Максимальный контроль, максимальная сложность         │
└─────────────────────────────────────────────────────────┘

Аналогия: вместо готовых кистей вы сами смешиваете
пигменты и программируете движение валиков принтера.
```

### 4. CALayer = Лист бумаги (содержит рисунок)

```
┌─────────────────────────────────────────────────────────┐
│               СТОПКА ПРОЗРАЧНЫХ ЛИСТОВ                   │
│                                                          │
│   Каждый лист (CALayer) имеет:                          │
│   - Рисунок (contents = CGImage/texture)                │
│   - Размер и позицию (bounds, position)                 │
│   - Прозрачность (opacity)                              │
│   - Эффекты (shadow, cornerRadius, mask)                │
│                                                          │
│        ┌─────────────┐  ← Layer 3 (opacity: 0.8)        │
│       ┌┴────────────┐│                                  │
│      ┌┴────────────┐││  ← Layer 2 (shadow)              │
│      │  Content    │││                                  │
│      │  (Bitmap)   │││  ← Layer 1 (cornerRadius)        │
│      └─────────────┴┴┘                                  │
│                                                          │
│   Листы накладываются друг на друга = compositing       │
└─────────────────────────────────────────────────────────┘

Ключевое: сам рисунок НЕ перерисовывается при анимации!
Только положение/свойства листа меняются.
```

### 5. Compositor = Режиссёр монтажа (собирает слои в кадр)

```
┌─────────────────────────────────────────────────────────┐
│            МОНТАЖНАЯ СТУДИЯ (Render Server)              │
│                                                          │
│   Входные материалы         Финальный кадр              │
│   (Layer Trees)             (что видит пользователь)    │
│                                                          │
│   ┌───┐ ┌───┐ ┌───┐              ┌──────────────┐       │
│   │ A │ │ B │ │ C │    ────►     │              │       │
│   └───┘ └───┘ └───┘              │   Готовый    │       │
│                                  │    кадр      │       │
│   Режиссёр (GPU):               │   60/120 fps  │       │
│   1. Сортирует по z-order       │              │       │
│   2. Применяет transforms       └──────────────┘       │
│   3. Рассчитывает прозрачность                         │
│   4. Выводит на экран                                  │
│                                                          │
│   Всё за 8.33ms (120fps) или 16.67ms (60fps)           │
└─────────────────────────────────────────────────────────┘

Аналогия: режиссёр НЕ снимает сцены заново.
Он берёт готовые кадры и склеивает их в фильм.
```

## Графический стек iOS

### Полная архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ПРИЛОЖЕНИЕ (App Process)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    SwiftUI / UIKit                           │   │
│   │         (Высокоуровневые UI компоненты)                     │   │
│   │                                                              │   │
│   │   Text, Button, Image, View, UILabel, UIButton, UIImageView │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Core Animation                            │   │
│   │              (CALayer tree management)                       │   │
│   │                                                              │   │
│   │   CALayer, CAShapeLayer, CAGradientLayer, CATextLayer       │   │
│   │   Implicit/Explicit animations, CATransaction               │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                    │                       │                         │
│                    ▼                       ▼                         │
│   ┌────────────────────────┐   ┌────────────────────────────────┐   │
│   │    Core Graphics       │   │         Metal                   │   │
│   │   (Quartz 2D - CPU)    │   │     (Low-level GPU API)         │   │
│   │                        │   │                                 │   │
│   │   CGContext, CGPath    │   │   MTLDevice, Shaders            │   │
│   │   CGImage, PDF         │   │   Compute, Render Pipelines     │   │
│   └────────────────────────┘   └────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    IPC (Mach messages)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     RENDER SERVER (Separate Process)                 │
│                        SpringBoard / backboardd                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                  Metal (Compositor)                          │   │
│   │                                                              │   │
│   │   1. Получает serialized layer tree                         │   │
│   │   2. Загружает текстуры в GPU                               │   │
│   │   3. Выполняет compositing                                  │   │
│   │   4. Применяет анимации (interpolation)                     │   │
│   │   5. Выводит на дисплей                                     │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                              HARDWARE                                │
│                                                                      │
│   ┌──────────────────┐        ┌─────────────────────────────────┐   │
│   │       GPU        │   ──►  │         Display                  │   │
│   │  (Apple Silicon) │        │   60Hz / 120Hz ProMotion         │   │
│   └──────────────────┘        └─────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Поток данных при отрисовке кадра

```
┌─────────────────────────────────────────────────────────────────┐
│                    ОДИН КАДР (16.67ms @ 60fps)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LAYOUT PHASE (Main Thread)                     ~2-5ms       │
│     ┌────────────────────────────────────────┐                  │
│     │ - layoutSubviews()                      │                  │
│     │ - Auto Layout constraint solving        │                  │
│     │ - View positioning                      │                  │
│     └────────────────────────────────────────┘                  │
│                         │                                        │
│                         ▼                                        │
│  2. DISPLAY PHASE (Main Thread)                    ~1-10ms      │
│     ┌────────────────────────────────────────┐                  │
│     │ - draw(_ rect:) calls                   │                  │
│     │ - Core Graphics rendering (if needed)   │                  │
│     │ - Layer contents update                 │                  │
│     └────────────────────────────────────────┘                  │
│                         │                                        │
│                         ▼                                        │
│  3. COMMIT PHASE (Main Thread)                     ~0.5-2ms     │
│     ┌────────────────────────────────────────┐                  │
│     │ - Layer tree serialization              │                  │
│     │ - Send to Render Server via IPC         │                  │
│     └────────────────────────────────────────┘                  │
│                         │                                        │
│                         ▼                                        │
│  4. RENDER PHASE (Render Server + GPU)             ~2-8ms       │
│     ┌────────────────────────────────────────┐                  │
│     │ - Decode layer tree                     │                  │
│     │ - Prepare textures                      │                  │
│     │ - GPU compositing                       │                  │
│     │ - VSync and display                     │                  │
│     └────────────────────────────────────────┘                  │
│                                                                  │
│  TOTAL BUDGET: 16.67ms (60fps) / 8.33ms (120fps)               │
└─────────────────────────────────────────────────────────────────┘
```

## Core Graphics (Quartz 2D)

### Что такое Core Graphics

Core Graphics - это низкоуровневый 2D-рендеринг движок на базе CPU. Все операции выполняются последовательно на главном потоке (или указанном background thread).

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORE GRAPHICS PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐                                              │
│   │  CGContext   │  ← Контекст рисования (bitmap, PDF, etc.)    │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │   CGPath     │  ← Геометрия (линии, кривые, формы)          │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │  CGColor /   │  ← Заливка и обводка                         │
│   │  CGGradient  │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │   Bitmap     │  ← Результат в памяти                        │
│   │   Buffer     │                                              │
│   └──────────────┘                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Основные классы

```swift
// CGContext - холст для рисования
// Может быть bitmap context, PDF context, etc.

// Пример: создание bitmap context
let width = 100
let height = 100
let bitsPerComponent = 8
let bytesPerRow = width * 4 // RGBA

guard let context = CGContext(
    data: nil,                           // Память выделяется автоматически
    width: width,
    height: height,
    bitsPerComponent: bitsPerComponent,
    bytesPerRow: bytesPerRow,
    space: CGColorSpaceCreateDeviceRGB(),
    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
) else { return }

// CGPath - геометрические фигуры
let path = CGMutablePath()
path.move(to: CGPoint(x: 10, y: 10))       // Переместить "перо"
path.addLine(to: CGPoint(x: 90, y: 10))    // Линия
path.addLine(to: CGPoint(x: 50, y: 90))    // Ещё линия
path.closeSubpath()                         // Замкнуть контур

// CGColor - цвета
let fillColor = CGColor(red: 1.0, green: 0.0, blue: 0.0, alpha: 1.0)
let strokeColor = CGColor(red: 0.0, green: 0.0, blue: 0.0, alpha: 1.0)

// Рисуем
context.setFillColor(fillColor)
context.setStrokeColor(strokeColor)
context.setLineWidth(2.0)
context.addPath(path)
context.drawPath(using: .fillStroke)  // Заливка + обводка

// Получаем CGImage
let image = context.makeImage()
```

### Рисование в UIView

```swift
class CustomShapeView: UIView {

    // ВАЖНО: draw вызывается на main thread
    // Тяжёлые операции здесь = dropped frames
    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext() else { return }

        // 1. Рисуем градиентный фон
        let colors = [
            UIColor.systemBlue.cgColor,
            UIColor.systemPurple.cgColor
        ]

        guard let gradient = CGGradient(
            colorsSpace: CGColorSpaceCreateDeviceRGB(),
            colors: colors as CFArray,
            locations: [0.0, 1.0]
        ) else { return }

        context.drawLinearGradient(
            gradient,
            start: CGPoint(x: 0, y: 0),
            end: CGPoint(x: bounds.width, y: bounds.height),
            options: []
        )

        // 2. Рисуем кастомную форму
        let path = createStarPath(in: bounds)

        context.addPath(path)
        context.setFillColor(UIColor.white.cgColor)
        context.fillPath()

        // 3. Добавляем обводку
        context.addPath(path)
        context.setStrokeColor(UIColor.black.cgColor)
        context.setLineWidth(2.0)
        context.strokePath()
    }

    private func createStarPath(in rect: CGRect) -> CGPath {
        let path = CGMutablePath()
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let outerRadius = min(rect.width, rect.height) / 2 - 10
        let innerRadius = outerRadius * 0.4
        let points = 5

        for i in 0..<(points * 2) {
            let radius = i.isMultiple(of: 2) ? outerRadius : innerRadius
            let angle = CGFloat(i) * .pi / CGFloat(points) - .pi / 2

            let point = CGPoint(
                x: center.x + radius * cos(angle),
                y: center.y + radius * sin(angle)
            )

            if i == 0 {
                path.move(to: point)
            } else {
                path.addLine(to: point)
            }
        }

        path.closeSubpath()
        return path
    }
}
```

### Когда использовать Core Graphics

```
┌─────────────────────────────────────────────────────────────────┐
│                КОГДА ИСПОЛЬЗОВАТЬ CORE GRAPHICS                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✅ ИСПОЛЬЗУЙТЕ:                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Сложные кастомные формы (графики, диаграммы)             │ │
│  │ • Генерация PDF документов                                  │ │
│  │ • Редактирование изображений (пиксельные операции)         │ │
│  │ • Создание паттернов и текстур                             │ │
│  │ • Рисование в background thread для кэширования            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ❌ НЕ ИСПОЛЬЗУЙТЕ:                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Анимации (используйте Core Animation)                    │ │
│  │ • Простые формы (используйте CAShapeLayer)                 │ │
│  │ • Тени и скругления (используйте layer properties)         │ │
│  │ • Real-time rendering (используйте Metal)                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ПРОИЗВОДИТЕЛЬНОСТЬ:                                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • CPU-bound - блокирует поток                              │ │
│  │ • Пересоздание bitmap каждый draw() - дорого               │ │
│  │ • Используйте shouldRasterize для кэширования              │ │
│  │ • Рисуйте в background и присваивайте layer.contents       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Оптимизация Core Graphics

```swift
class OptimizedDrawingView: UIView {

    // Кэш отрисованного изображения
    private var cachedImage: UIImage?
    private var needsRedraw = true

    // Вызываем при изменении данных
    func setNeedsRedraw() {
        needsRedraw = true
        setNeedsDisplay()
    }

    override func draw(_ rect: CGRect) {
        // Если кэш актуален - используем его
        if !needsRedraw, let cached = cachedImage {
            cached.draw(in: bounds)
            return
        }

        // Рисуем в background-safe контексте
        let format = UIGraphicsImageRendererFormat()
        format.scale = UIScreen.main.scale
        format.opaque = false

        let renderer = UIGraphicsImageRenderer(
            size: bounds.size,
            format: format
        )

        cachedImage = renderer.image { context in
            // Все тяжёлые операции рисования здесь
            drawComplexContent(in: context.cgContext)
        }

        cachedImage?.draw(in: bounds)
        needsRedraw = false
    }

    private func drawComplexContent(in context: CGContext) {
        // Ваш код рисования
    }
}

// Ещё лучше: рисовать в background thread
extension OptimizedDrawingView {

    func redrawInBackground() {
        let size = bounds.size
        let scale = UIScreen.main.scale

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            let format = UIGraphicsImageRendererFormat()
            format.scale = scale

            let renderer = UIGraphicsImageRenderer(size: size, format: format)

            let image = renderer.image { context in
                self?.drawComplexContent(in: context.cgContext)
            }

            DispatchQueue.main.async {
                // Присваиваем напрямую в layer.contents - быстрее чем draw()
                self?.layer.contents = image.cgImage
            }
        }
    }
}
```

## Core Animation

### Архитектура CALayer

```
┌─────────────────────────────────────────────────────────────────┐
│                      CALayer ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  UIView ────────────────────────────────────────────────────►   │
│     │                                                            │
│     │  .layer (backing layer)                                    │
│     ▼                                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        CALayer                            │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                           │   │
│  │  Geometry:                  Visual:                       │   │
│  │  ├─ bounds                  ├─ contents (CGImage)         │   │
│  │  ├─ position               ├─ backgroundColor             │   │
│  │  ├─ anchorPoint            ├─ borderWidth/Color           │   │
│  │  ├─ transform              ├─ cornerRadius                │   │
│  │  └─ frame (derived)        ├─ shadowColor/Offset/Radius   │   │
│  │                             ├─ opacity                     │   │
│  │                             └─ mask                        │   │
│  │                                                           │   │
│  │  Hierarchy:                 Animation:                    │   │
│  │  ├─ sublayers[]            ├─ animations{}                │   │
│  │  ├─ superlayer             └─ actions{}                   │   │
│  │  └─ mask                                                  │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  LAYER TYPES:                                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │   CALayer      │  │  CAShapeLayer  │  │CAGradientLayer │     │
│  │   (base)       │  │   (paths)      │  │  (gradients)   │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │  CATextLayer   │  │CATiledLayer    │  │CAEmitterLayer  │     │
│  │   (text)       │  │(large images)  │  │  (particles)   │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Model Layer vs Presentation Layer

```
┌─────────────────────────────────────────────────────────────────┐
│              MODEL vs PRESENTATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   MODEL LAYER                    PRESENTATION LAYER              │
│   (layer)                        (layer.presentation())          │
│                                                                  │
│   ┌───────────────┐              ┌───────────────┐              │
│   │ position:     │              │ position:     │              │
│   │ (100, 100)    │              │ (150, 100)    │ ← Текущее    │
│   │               │   Animation  │               │   значение   │
│   │ Final state   │   ─────────► │ Current state │   на экране  │
│   │               │              │               │              │
│   └───────────────┘              └───────────────┘              │
│                                                                  │
│   // Получение текущего видимого значения                       │
│   let currentPosition = layer.presentation()?.position          │
│                                                                  │
│   // Model layer всегда хранит конечное значение                │
│   // Presentation layer интерполирует во время анимации         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implicit Animations (Неявные анимации)

```swift
// Для standalone CALayer (НЕ backing layer UIView)
// изменение animatable свойств АВТОМАТИЧЕСКИ анимируется

let layer = CALayer()
layer.frame = CGRect(x: 0, y: 0, width: 100, height: 100)
layer.backgroundColor = UIColor.red.cgColor
view.layer.addSublayer(layer)

// Это вызовет плавную анимацию 0.25 сек
layer.position = CGPoint(x: 200, y: 200)  // Автоматическая анимация!
layer.backgroundColor = UIColor.blue.cgColor  // И это тоже!

// Отключение implicit animations
CATransaction.begin()
CATransaction.setDisableActions(true)  // Отключаем
layer.position = CGPoint(x: 300, y: 300)  // Мгновенное изменение
CATransaction.commit()

// Настройка implicit animations
CATransaction.begin()
CATransaction.setAnimationDuration(1.0)
CATransaction.setAnimationTimingFunction(
    CAMediaTimingFunction(name: .easeInEaseOut)
)
layer.opacity = 0.5
CATransaction.commit()
```

### Explicit Animations (Явные анимации)

```swift
// CABasicAnimation - базовая анимация одного свойства
let positionAnimation = CABasicAnimation(keyPath: "position")
positionAnimation.fromValue = CGPoint(x: 50, y: 50)
positionAnimation.toValue = CGPoint(x: 250, y: 250)
positionAnimation.duration = 1.0
positionAnimation.timingFunction = CAMediaTimingFunction(name: .easeOut)

// ВАЖНО: анимация не меняет model layer!
// Нужно установить конечное значение вручную
layer.position = CGPoint(x: 250, y: 250)  // Установить до анимации
layer.add(positionAnimation, forKey: "positionAnimation")

// CAKeyframeAnimation - анимация по ключевым кадрам
let pathAnimation = CAKeyframeAnimation(keyPath: "position")
let path = CGMutablePath()
path.move(to: CGPoint(x: 50, y: 50))
path.addCurve(
    to: CGPoint(x: 250, y: 250),
    control1: CGPoint(x: 150, y: 0),
    control2: CGPoint(x: 150, y: 300)
)
pathAnimation.path = path
pathAnimation.duration = 2.0
layer.add(pathAnimation, forKey: "pathAnimation")

// CAAnimationGroup - группа анимаций
let fadeAnimation = CABasicAnimation(keyPath: "opacity")
fadeAnimation.fromValue = 1.0
fadeAnimation.toValue = 0.5

let scaleAnimation = CABasicAnimation(keyPath: "transform.scale")
scaleAnimation.fromValue = 1.0
scaleAnimation.toValue = 1.5

let group = CAAnimationGroup()
group.animations = [fadeAnimation, scaleAnimation]
group.duration = 1.0
layer.add(group, forKey: "groupAnimation")

// CASpringAnimation - пружинная анимация (iOS 9+)
let springAnimation = CASpringAnimation(keyPath: "position.x")
springAnimation.fromValue = layer.position.x
springAnimation.toValue = layer.position.x + 100
springAnimation.damping = 5.0        // Затухание
springAnimation.stiffness = 100.0    // Жёсткость пружины
springAnimation.mass = 1.0           // Масса
springAnimation.initialVelocity = 0
springAnimation.duration = springAnimation.settlingDuration
layer.add(springAnimation, forKey: "spring")
```

### CATransaction для группировки

```swift
// CATransaction группирует изменения в одну транзакцию
CATransaction.begin()

// Настройки транзакции
CATransaction.setAnimationDuration(0.5)
CATransaction.setAnimationTimingFunction(
    CAMediaTimingFunction(name: .easeInEaseOut)
)

// Callback по завершению
CATransaction.setCompletionBlock {
    print("Все анимации в транзакции завершены")
}

// Все эти изменения анимируются синхронно
layer1.position = newPosition1
layer2.opacity = 0.5
layer3.transform = CATransform3DMakeScale(1.5, 1.5, 1.0)

CATransaction.commit()

// Вложенные транзакции
CATransaction.begin()
CATransaction.setAnimationDuration(1.0)

layer1.position = position1

CATransaction.begin()  // Вложенная транзакция
CATransaction.setAnimationDuration(0.5)  // Другая длительность
layer2.position = position2
CATransaction.commit()  // Завершить вложенную

CATransaction.commit()  // Завершить внешнюю
```

### Специализированные слои

```swift
// CAShapeLayer - для векторных форм
let shapeLayer = CAShapeLayer()
shapeLayer.path = UIBezierPath(roundedRect: bounds, cornerRadius: 10).cgPath
shapeLayer.fillColor = UIColor.blue.cgColor
shapeLayer.strokeColor = UIColor.white.cgColor
shapeLayer.lineWidth = 2.0

// Анимация strokeEnd для эффекта рисования
shapeLayer.strokeEnd = 0  // Начальное состояние
let drawAnimation = CABasicAnimation(keyPath: "strokeEnd")
drawAnimation.fromValue = 0
drawAnimation.toValue = 1
drawAnimation.duration = 2.0
shapeLayer.strokeEnd = 1
shapeLayer.add(drawAnimation, forKey: "draw")

// CAGradientLayer - для градиентов
let gradientLayer = CAGradientLayer()
gradientLayer.frame = view.bounds
gradientLayer.colors = [
    UIColor.systemBlue.cgColor,
    UIColor.systemPurple.cgColor
]
gradientLayer.startPoint = CGPoint(x: 0, y: 0)
gradientLayer.endPoint = CGPoint(x: 1, y: 1)
gradientLayer.locations = [0.0, 1.0]

// CAReplicatorLayer - для повторяющихся элементов
let replicatorLayer = CAReplicatorLayer()
replicatorLayer.instanceCount = 10
replicatorLayer.instanceDelay = 0.1  // Задержка между копиями
replicatorLayer.instanceTransform = CATransform3DMakeTranslation(30, 0, 0)
replicatorLayer.instanceAlphaOffset = -0.1  // Уменьшение opacity

let dotLayer = CALayer()
dotLayer.frame = CGRect(x: 0, y: 0, width: 20, height: 20)
dotLayer.backgroundColor = UIColor.red.cgColor
dotLayer.cornerRadius = 10

replicatorLayer.addSublayer(dotLayer)

// CAEmitterLayer - для частиц
let emitterLayer = CAEmitterLayer()
emitterLayer.emitterPosition = CGPoint(x: view.bounds.midX, y: 0)
emitterLayer.emitterSize = CGSize(width: view.bounds.width, height: 1)
emitterLayer.emitterShape = .line

let cell = CAEmitterCell()
cell.birthRate = 50
cell.lifetime = 5.0
cell.velocity = 100
cell.velocityRange = 50
cell.emissionLongitude = .pi  // Вниз
cell.scale = 0.1
cell.scaleRange = 0.05
cell.contents = UIImage(named: "snowflake")?.cgImage

emitterLayer.emitterCells = [cell]
```

## Metal

### Что такое Metal

```
┌─────────────────────────────────────────────────────────────────┐
│                         METAL OVERVIEW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Metal - это низкоуровневый API для прямого доступа к GPU.      │
│  Заменил OpenGL ES начиная с iOS 8 (2014).                       │
│                                                                  │
│  ПРЕИМУЩЕСТВА:                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • До 10x меньше CPU overhead по сравнению с OpenGL ES      │ │
│  │ • Явное управление памятью GPU                             │ │
│  │ • Pre-compiled shaders                                     │ │
│  │ • Multi-threaded command encoding                          │ │
│  │ • Unified memory architecture (Apple Silicon)              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ИСПОЛЬЗОВАНИЕ:                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Игры (Unity, Unreal Engine используют Metal)             │ │
│  │ • Machine Learning (Core ML использует Metal)              │ │
│  │ • Image/Video processing                                   │ │
│  │ • AR/VR (ARKit, RealityKit)                                │ │
│  │ • Compute shaders                                          │ │
│  │ • Pro apps (Final Cut Pro, Logic Pro)                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Архитектура Metal

```
┌─────────────────────────────────────────────────────────────────┐
│                      METAL ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                      MTLDevice                            │  │
│   │           (GPU - физическое устройство)                   │  │
│   └─────────────────────────┬────────────────────────────────┘  │
│                             │                                    │
│              ┌──────────────┴──────────────┐                    │
│              │                             │                    │
│              ▼                             ▼                    │
│   ┌─────────────────────┐      ┌─────────────────────┐         │
│   │  MTLCommandQueue    │      │   MTLLibrary        │         │
│   │  (очередь команд)   │      │   (shader library)  │         │
│   └──────────┬──────────┘      └──────────┬──────────┘         │
│              │                            │                     │
│              ▼                            ▼                     │
│   ┌─────────────────────┐      ┌─────────────────────┐         │
│   │MTLCommandBuffer     │      │   MTLFunction       │         │
│   │(буфер команд)       │      │   (shader function) │         │
│   └──────────┬──────────┘      └──────────┬──────────┘         │
│              │                            │                     │
│              ▼                            ▼                     │
│   ┌─────────────────────┐      ┌─────────────────────┐         │
│   │MTLRenderCommand     │◄────►│MTLRenderPipeline    │         │
│   │Encoder              │      │State                │         │
│   │(encoder команд      │      │(состояние пайплайна)│         │
│   │рендеринга)          │      │                     │         │
│   └──────────┬──────────┘      └─────────────────────┘         │
│              │                                                  │
│              ▼                                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   MTLTexture / MTLBuffer                 │  │
│   │                   (GPU ресурсы)                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Базовый пример Metal

```swift
import Metal
import MetalKit

class MetalRenderer: NSObject, MTKViewDelegate {

    // Основные объекты Metal
    private let device: MTLDevice
    private let commandQueue: MTLCommandQueue
    private var pipelineState: MTLRenderPipelineState?
    private var vertexBuffer: MTLBuffer?

    init?(metalView: MTKView) {
        // 1. Получаем GPU устройство
        guard let device = MTLCreateSystemDefaultDevice() else {
            print("Metal не поддерживается на этом устройстве")
            return nil
        }
        self.device = device

        // 2. Создаём очередь команд
        guard let queue = device.makeCommandQueue() else {
            return nil
        }
        self.commandQueue = queue

        super.init()

        // 3. Настраиваем MTKView
        metalView.device = device
        metalView.delegate = self
        metalView.clearColor = MTLClearColor(
            red: 0.0, green: 0.0, blue: 0.0, alpha: 1.0
        )

        // 4. Создаём pipeline
        setupPipeline()

        // 5. Загружаем данные
        setupVertexBuffer()
    }

    private func setupPipeline() {
        // Загружаем шейдеры из default library
        guard let library = device.makeDefaultLibrary() else { return }

        let vertexFunction = library.makeFunction(name: "vertex_main")
        let fragmentFunction = library.makeFunction(name: "fragment_main")

        // Создаём descriptor пайплайна
        let pipelineDescriptor = MTLRenderPipelineDescriptor()
        pipelineDescriptor.vertexFunction = vertexFunction
        pipelineDescriptor.fragmentFunction = fragmentFunction
        pipelineDescriptor.colorAttachments[0].pixelFormat = .bgra8Unorm

        // Компилируем pipeline state
        do {
            pipelineState = try device.makeRenderPipelineState(
                descriptor: pipelineDescriptor
            )
        } catch {
            print("Ошибка создания pipeline: \(error)")
        }
    }

    private func setupVertexBuffer() {
        // Треугольник: позиция (x, y, z, w) + цвет (r, g, b, a)
        let vertices: [Float] = [
            // Позиция           // Цвет
             0.0,  0.5, 0.0, 1.0,   1.0, 0.0, 0.0, 1.0,  // Верхняя вершина (красная)
            -0.5, -0.5, 0.0, 1.0,   0.0, 1.0, 0.0, 1.0,  // Левая нижняя (зелёная)
             0.5, -0.5, 0.0, 1.0,   0.0, 0.0, 1.0, 1.0   // Правая нижняя (синяя)
        ]

        vertexBuffer = device.makeBuffer(
            bytes: vertices,
            length: vertices.count * MemoryLayout<Float>.stride,
            options: .storageModeShared  // Shared memory на Apple Silicon
        )
    }

    // MTKViewDelegate - вызывается каждый кадр
    func draw(in view: MTKView) {
        guard let pipelineState = pipelineState,
              let vertexBuffer = vertexBuffer,
              let renderPassDescriptor = view.currentRenderPassDescriptor,
              let drawable = view.currentDrawable else {
            return
        }

        // Создаём command buffer для этого кадра
        guard let commandBuffer = commandQueue.makeCommandBuffer() else {
            return
        }

        // Создаём render encoder
        guard let renderEncoder = commandBuffer.makeRenderCommandEncoder(
            descriptor: renderPassDescriptor
        ) else {
            return
        }

        // Настраиваем encoder
        renderEncoder.setRenderPipelineState(pipelineState)
        renderEncoder.setVertexBuffer(vertexBuffer, offset: 0, index: 0)

        // Рисуем треугольник
        renderEncoder.drawPrimitives(
            type: .triangle,
            vertexStart: 0,
            vertexCount: 3
        )

        renderEncoder.endEncoding()

        // Показываем результат
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }

    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        // Обработка изменения размера
    }
}
```

### Metal Shaders (MSL - Metal Shading Language)

```metal
// Shaders.metal

#include <metal_stdlib>
using namespace metal;

// Структура входных данных вершины
struct VertexIn {
    float4 position [[attribute(0)]];
    float4 color [[attribute(1)]];
};

// Структура выходных данных вершинного шейдера
struct VertexOut {
    float4 position [[position]];  // Обязательное поле
    float4 color;
};

// Вершинный шейдер - вызывается для каждой вершины
vertex VertexOut vertex_main(
    const device VertexIn* vertices [[buffer(0)]],
    uint vertexID [[vertex_id]]
) {
    VertexOut out;
    out.position = vertices[vertexID].position;
    out.color = vertices[vertexID].color;
    return out;
}

// Фрагментный шейдер - вызывается для каждого пикселя
fragment float4 fragment_main(VertexOut in [[stage_in]]) {
    return in.color;  // Возвращаем интерполированный цвет
}

// Compute shader пример - параллельная обработка
kernel void compute_example(
    texture2d<float, access::read> inTexture [[texture(0)]],
    texture2d<float, access::write> outTexture [[texture(1)]],
    uint2 gid [[thread_position_in_grid]]
) {
    // Простой эффект инверсии цветов
    float4 color = inTexture.read(gid);
    float4 inverted = float4(1.0 - color.rgb, color.a);
    outTexture.write(inverted, gid);
}
```

### Metal vs OpenGL ES

```
┌─────────────────────────────────────────────────────────────────┐
│                   METAL vs OPENGL ES                             │
├──────────────────────┬──────────────────────────────────────────┤
│       METAL          │              OPENGL ES                    │
├──────────────────────┼──────────────────────────────────────────┤
│                      │                                          │
│ Apple-only           │ Cross-platform                           │
│                      │                                          │
│ Low-level, explicit  │ High-level, implicit                     │
│ state management     │ state machine                            │
│                      │                                          │
│ Pre-compiled shaders │ Runtime shader compilation               │
│ (faster startup)     │ (slower startup)                         │
│                      │                                          │
│ Multi-threaded       │ Single-threaded                          │
│ command encoding     │ command submission                       │
│                      │                                          │
│ Explicit memory      │ Driver-managed memory                    │
│ management           │                                          │
│                      │                                          │
│ ~10x less CPU        │ High CPU overhead                        │
│ overhead             │                                          │
│                      │                                          │
│ Unified graphics     │ Separate compute                         │
│ + compute            │                                          │
│                      │                                          │
│ iOS 8+ / macOS 10.11+│ Deprecated on Apple platforms            │
│                      │ (iOS 12, macOS 10.14)                    │
│                      │                                          │
└──────────────────────┴──────────────────────────────────────────┘

Рекомендация Apple: всегда используйте Metal для новых проектов.
OpenGL ES код следует мигрировать на Metal.
```

## Render Server

### Архитектура Render Server

```
┌─────────────────────────────────────────────────────────────────┐
│                    RENDER SERVER ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Render Server - это ОТДЕЛЬНЫЙ процесс (SpringBoard/backboardd) │
│  который выполняет финальный рендеринг и композицию.            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     APP PROCESS                              ││
│  │                                                              ││
│  │   ┌────────────────────────────────────────────────────────┐││
│  │   │            Core Animation                               │││
│  │   │                                                         │││
│  │   │  1. Управляет layer tree                               │││
│  │   │  2. Рассчитывает layout                                │││
│  │   │  3. Сериализует layer tree                             │││
│  │   │  4. Отправляет через IPC                               │││
│  │   └────────────────────────────────────────────────────────┘││
│  └───────────────────────────┬─────────────────────────────────┘│
│                              │                                   │
│                    IPC (Mach messages)                          │
│                              │                                   │
│  ┌───────────────────────────▼─────────────────────────────────┐│
│  │                   RENDER SERVER PROCESS                      ││
│  │                   (SpringBoard / backboardd)                 ││
│  │                                                              ││
│  │   ┌────────────────────────────────────────────────────────┐││
│  │   │  1. Десериализует layer trees от ВСЕХ приложений       │││
│  │   │  2. Управляет GPU ресурсами                            │││
│  │   │  3. Выполняет композицию слоёв                         │││
│  │   │  4. Интерполирует анимации между кадрами               │││
│  │   │  5. Синхронизирует с VSync дисплея                     │││
│  │   │  6. Отправляет финальный кадр на экран                 │││
│  │   └────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ПОЧЕМУ ОТДЕЛЬНЫЙ ПРОЦЕСС?                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Изоляция: краш приложения не убивает весь UI             │ │
│  │ • Приоритет: рендеринг имеет высший приоритет              │ │
│  │ • Эффективность: один процесс управляет GPU                │ │
│  │ • Безопасность: приложения не имеют прямого доступа к GPU  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Tree Serialization

```
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER TREE COMMIT PROCESS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FRAME N (16.67ms @ 60fps)                                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PHASE 1: Layout (Main Thread)                 ~5ms       │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ layoutSubviews() для всех dirty views              │  │   │
│  │  │ Auto Layout constraint solving                     │  │   │
│  │  │ Обновление frame/bounds слоёв                      │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PHASE 2: Display (Main Thread)               ~3ms        │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ draw(_ rect:) для views, требующих перерисовки     │  │   │
│  │  │ Core Graphics rendering (если нужно)               │  │   │
│  │  │ Обновление layer.contents                          │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PHASE 3: Commit (Main Thread → Render Server) ~2ms       │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ CA::Transaction::commit()                          │  │   │
│  │  │ Сериализация layer tree:                           │  │   │
│  │  │   - Layer hierarchy                                │  │   │
│  │  │   - Geometry (bounds, position, transform)         │  │   │
│  │  │   - Contents (textures, images)                    │  │   │
│  │  │   - Visual properties (opacity, masks, etc.)       │  │   │
│  │  │   - Animations                                     │  │   │
│  │  │ Отправка через XPC/Mach messages                   │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│              ─────────────┼────────────── IPC                    │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PHASE 4: Render (Render Server + GPU)        ~6ms        │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ Десериализация layer tree                          │  │   │
│  │  │ Подготовка текстур (upload to GPU if needed)       │  │   │
│  │  │ Интерполяция анимаций                              │  │   │
│  │  │ GPU compositing                                    │  │   │
│  │  │ VSync wait                                         │  │   │
│  │  │ Display                                            │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ВАЖНО: Если Main Thread не успевает за 16.67ms,                │
│  Render Server продолжает показывать интерполированные          │
│  анимации, но новые изменения UI не появятся.                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 60fps vs 120fps (ProMotion)

```
┌─────────────────────────────────────────────────────────────────┐
│                  FRAME TIMING BUDGETS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  60fps (стандартные дисплеи)                                    │
│  ────────────────────────────                                   │
│  Frame budget: 16.67ms                                          │
│                                                                  │
│  ├────────┬───────┬───────┬──────────────────┤                  │
│  0ms     5ms    10ms    16.67ms                                 │
│  │ Layout │Display│Commit │    Render        │                  │
│  │        │       │       │    Server        │                  │
│  └────────┴───────┴───────┴──────────────────┘                  │
│                                                                  │
│                                                                  │
│  120fps (ProMotion - iPhone 13 Pro+, iPad Pro)                  │
│  ────────────────────────────────────────────                   │
│  Frame budget: 8.33ms (В 2 РАЗА МЕНЬШЕ!)                        │
│                                                                  │
│  ├────┬────┬───┬─────────┤                                      │
│  0ms  2ms  4ms  8.33ms                                          │
│  │Lay │Disp│Com│ Render  │                                      │
│  │out │lay │mit│ Server  │                                      │
│  └────┴────┴───┴─────────┘                                      │
│                                                                  │
│  ProMotion динамически переключается между 10-120Hz             │
│  в зависимости от контента:                                     │
│  • Статичный контент: 10-24Hz (экономия батареи)               │
│  • Скроллинг: 120Hz (плавность)                                │
│  • Видео: подстраивается под частоту видео (24/30/60fps)       │
│                                                                  │
│  CADisplayLink.preferredFrameRateRange позволяет                │
│  указать предпочтительный диапазон частоты.                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

```swift
// Настройка CADisplayLink для ProMotion
let displayLink = CADisplayLink(target: self, selector: #selector(update))

// iOS 15+: указываем предпочтительный диапазон
if #available(iOS 15.0, *) {
    displayLink.preferredFrameRateRange = CAFrameRateRange(
        minimum: 60,       // Минимум 60 fps
        maximum: 120,      // Максимум 120 fps
        preferred: 120     // Предпочтительно 120 fps
    )
}

displayLink.add(to: .main, forMode: .common)

@objc func update(displayLink: CADisplayLink) {
    // Время с последнего кадра
    let deltaTime = displayLink.targetTimestamp - displayLink.timestamp

    // Обновляем анимации
    updateAnimations(deltaTime: deltaTime)
}
```

## Распространённые ошибки

### 1. Рисование на Main Thread без необходимости

```swift
// ❌ ПЛОХО: тяжёлая отрисовка блокирует UI
class BadChartView: UIView {
    override func draw(_ rect: CGRect) {
        // 10000 точек данных рисуются на main thread
        for i in 0..<10000 {
            let path = UIBezierPath()
            path.move(to: calculatePoint(i))
            path.addLine(to: calculatePoint(i + 1))
            path.stroke()
        }
    }
    // Результат: UI freezes на 100-500ms при каждом обновлении
}

// ✅ ХОРОШО: рисуем в background, результат кэшируем
class GoodChartView: UIView {
    private var cachedImage: UIImage?

    func updateChart(with data: [DataPoint]) {
        // Рисуем в background thread
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let renderer = UIGraphicsImageRenderer(size: self.bounds.size)
            let image = renderer.image { context in
                self.drawChart(data: data, in: context.cgContext)
            }

            DispatchQueue.main.async {
                // Присваиваем напрямую в layer - быстрее чем setNeedsDisplay
                self.layer.contents = image.cgImage
            }
        }
    }

    private func drawChart(data: [DataPoint], in context: CGContext) {
        // Вся тяжёлая отрисовка здесь
    }
}
```

### 2. Слишком много слоёв

```swift
// ❌ ПЛОХО: каждый элемент - отдельный слой
class BadCellView: UIView {
    func setup() {
        for i in 0..<100 {
            let label = UILabel()
            label.layer.cornerRadius = 5
            label.layer.masksToBounds = true
            label.layer.shadowColor = UIColor.black.cgColor
            label.layer.shadowOffset = CGSize(width: 0, height: 2)
            label.layer.shadowOpacity = 0.3
            addSubview(label)
        }
        // Результат: 100+ layers с shadows = severe performance hit
    }
}

// ✅ ХОРОШО: объединяем в меньшее количество слоёв
class GoodCellView: UIView {
    private let containerLayer = CALayer()

    func setup() {
        // Один слой для всего контента
        containerLayer.shouldRasterize = true
        containerLayer.rasterizationScale = UIScreen.main.scale
        layer.addSublayer(containerLayer)

        // Тень на контейнере, а не на каждом элементе
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0, height: 2)
        layer.shadowOpacity = 0.3
        layer.shadowPath = UIBezierPath(
            roundedRect: bounds,
            cornerRadius: 10
        ).cgPath  // Критично для производительности!
    }
}
```

### 3. Offscreen Rendering

```swift
// ❌ ПЛОХО: cornerRadius + masksToBounds = offscreen rendering
class BadCardView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)
        layer.cornerRadius = 10
        layer.masksToBounds = true  // Вызывает offscreen rendering!

        let imageView = UIImageView(image: UIImage(named: "photo"))
        addSubview(imageView)
        // GPU должен отрисовать в отдельный буфер, потом обрезать
    }
}

// ✅ ХОРОШО: используем contentsRect или готовим изображение заранее
class GoodCardView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)

        // Вариант 1: cornerRadius без masksToBounds (если фон solid)
        layer.cornerRadius = 10
        layer.backgroundColor = UIColor.white.cgColor
        // Содержимое выходит за границы, но фон скругляется

        // Вариант 2: Скругляем изображение заранее
        if let image = UIImage(named: "photo") {
            let roundedImage = image.roundedImage(cornerRadius: 10)
            let imageView = UIImageView(image: roundedImage)
            addSubview(imageView)
        }
    }
}

extension UIImage {
    func roundedImage(cornerRadius: CGFloat) -> UIImage {
        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { context in
            let rect = CGRect(origin: .zero, size: size)
            UIBezierPath(roundedRect: rect, cornerRadius: cornerRadius).addClip()
            draw(in: rect)
        }
    }
}
```

### 4. Неправильное использование shouldRasterize

```swift
// ❌ ПЛОХО: rasterize на анимируемых слоях
class BadAnimatedView: UIView {
    func animatePosition() {
        layer.shouldRasterize = true  // Rasterize ПЕРЕД анимацией

        UIView.animate(withDuration: 0.5) {
            self.center = CGPoint(x: 200, y: 200)
        }
        // Проблема: растровый кэш не нужен при простом изменении position
    }
}

// ❌ ПЛОХО: rasterize без правильного scale
class BadScaleView: UIView {
    func setup() {
        layer.shouldRasterize = true
        // rasterizationScale по умолчанию = 1.0
        // На Retina дисплее (scale = 2 или 3) будет размыто!
    }
}

// ✅ ХОРОШО: rasterize для сложных статичных слоёв
class GoodComplexView: UIView {
    func setup() {
        // Сложная иерархия слоёв, которая не меняется
        layer.shouldRasterize = true
        layer.rasterizationScale = UIScreen.main.scale  // Важно!

        // Теперь весь слой кэшируется как одна текстура
        // GPU просто применяет transform/opacity к этой текстуре
    }

    func onDataChange() {
        // При изменении данных временно отключаем rasterization
        layer.shouldRasterize = false
        updateContent()
        layer.shouldRasterize = true
    }
}
```

### 5. Неправильные blend modes

```swift
// ❌ ПЛОХО: прозрачные слои поверх друг друга
class BadLayeredView: UIView {
    func setup() {
        for i in 0..<10 {
            let view = UIView()
            view.backgroundColor = UIColor.red.withAlphaComponent(0.1)
            // 10 полупрозрачных слоёв = 10 blend operations на GPU
            addSubview(view)
        }
    }
}

// ✅ ХОРОШО: используем opaque где возможно
class GoodLayeredView: UIView {
    func setup() {
        backgroundColor = UIColor.white  // Opaque background

        let overlayView = UIView()
        overlayView.backgroundColor = UIColor.red.withAlphaComponent(0.1)
        overlayView.isOpaque = false  // Явно указываем
        addSubview(overlayView)

        // Opaque views быстрее - GPU не нужно blending
    }

    // Для CALayer
    func setupLayers() {
        let layer = CALayer()
        layer.isOpaque = true  // Говорим GPU что слой непрозрачный
        layer.backgroundColor = UIColor.white.cgColor
        self.layer.addSublayer(layer)
    }
}
```

### 6. Тень без shadowPath

```swift
// ❌ ПЛОХО: тень без явного пути
class BadShadowView: UIView {
    func setup() {
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0, height: 4)
        layer.shadowRadius = 10
        layer.shadowOpacity = 0.3
        // БЕЗ shadowPath!
        // GPU вычисляет тень по содержимому слоя каждый кадр
        // Очень дорого для сложных форм!
    }
}

// ✅ ХОРОШО: явный shadowPath
class GoodShadowView: UIView {
    func setup() {
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0, height: 4)
        layer.shadowRadius = 10
        layer.shadowOpacity = 0.3

        // Явный путь тени - GPU не нужно вычислять
        layer.shadowPath = UIBezierPath(
            roundedRect: bounds,
            cornerRadius: layer.cornerRadius
        ).cgPath
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        // Обновляем shadowPath при изменении размера
        layer.shadowPath = UIBezierPath(
            roundedRect: bounds,
            cornerRadius: layer.cornerRadius
        ).cgPath
    }
}
```

## Ментальные модели

### 1. Модель "Театральная постановка"

```
┌─────────────────────────────────────────────────────────────────┐
│              ТЕАТРАЛЬНАЯ ПОСТАНОВКА = iOS RENDERING              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ЗАКУЛИСЬЕ (App Process)          СЦЕНА (Render Server)        │
│  ═══════════════════════          ═════════════════════          │
│                                                                  │
│  ┌─────────────────────┐          ┌─────────────────────┐       │
│  │ Художник-декоратор  │   IPC    │    Режиссёр         │       │
│  │ (Core Graphics)     │────────► │    (Compositor)     │       │
│  │                     │          │                     │       │
│  │ Создаёт декорации   │          │ Расставляет         │       │
│  │ (textures)          │          │ декорации на сцене  │       │
│  └─────────────────────┘          └─────────────────────┘       │
│                                                                  │
│  ┌─────────────────────┐          ┌─────────────────────┐       │
│  │ Кукловод            │   IPC    │    Свет             │       │
│  │ (Core Animation)    │────────► │    (GPU)            │       │
│  │                     │          │                     │       │
│  │ Управляет           │          │ Освещает сцену      │       │
│  │ марионетками        │          │ 60/120 раз в сек    │       │
│  └─────────────────────┘          └─────────────────────┘       │
│                                                                  │
│  ПРАВИЛО: Чем меньше передаётся из закулисья на сцену,          │
│  тем быстрее спектакль (меньше данных через IPC).               │
│                                                                  │
│  Анимации марионеток выполняются НА СЦЕНЕ (GPU),                │
│  не требуя постоянного участия закулисья (CPU).                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Модель "Конвейер"

```
┌─────────────────────────────────────────────────────────────────┐
│            КОНВЕЙЕР = RENDERING PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Каждый кадр - это продукт на конвейере                         │
│                                                                  │
│  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐           │
│  │     │    │     │    │     │    │     │    │     │           │
│  │Frame│───►│Frame│───►│Frame│───►│Frame│───►│Frame│───► Display│
│  │ N-2 │    │ N-1 │    │  N  │    │ N+1 │    │ N+2 │           │
│  │     │    │     │    │     │    │     │    │     │           │
│  └─────┘    └─────┘    └─────┘    └─────┘    └─────┘           │
│  16.67ms    16.67ms    16.67ms    16.67ms    16.67ms           │
│                                                                  │
│  СТАНЦИИ КОНВЕЙЕРА:                                             │
│  ═══════════════════                                             │
│                                                                  │
│  1. Layout     - Замеряем и позиционируем детали                │
│  2. Display    - Красим детали (если нужно)                     │
│  3. Commit     - Упаковываем и отправляем                       │
│  4. Render     - Собираем финальный продукт                     │
│                                                                  │
│  ЕСЛИ станция не успевает за 16.67ms:                           │
│  - Продукт (кадр) пропускается                                  │
│  - Пользователь видит "дёрганье"                                │
│  - Метрика: dropped frames                                      │
│                                                                  │
│  ОПТИМИЗАЦИЯ:                                                    │
│  - Уменьшить работу на каждой станции                           │
│  - Кэшировать результаты (shouldRasterize)                      │
│  - Параллелить где возможно (background drawing)                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Модель "Слои стекла"

```
┌─────────────────────────────────────────────────────────────────┐
│              СЛОИ СТЕКЛА = CALayer COMPOSITING                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Представьте стопку прозрачных стёкол:                          │
│                                                                  │
│       Глаз пользователя                                         │
│            │                                                     │
│            ▼                                                     │
│  ┌─────────────────────┐  Layer 4: Overlay (z = 3)              │
│  │    🔘 Button        │  opacity: 0.9                          │
│  ├─────────────────────┤                                        │
│  │                     │  Layer 3: Content (z = 2)              │
│  │    📝 Text          │  opacity: 1.0                          │
│  ├─────────────────────┤                                        │
│  │                     │  Layer 2: Image (z = 1)                │
│  │    🖼️ Photo         │  opacity: 1.0                          │
│  ├─────────────────────┤                                        │
│  │                     │  Layer 1: Background (z = 0)           │
│  │    ██████████       │  opacity: 1.0, isOpaque: true          │
│  └─────────────────────┘                                        │
│                                                                  │
│  ПРАВИЛА COMPOSITING:                                            │
│  ═══════════════════════                                         │
│                                                                  │
│  1. GPU обрабатывает слои СНИЗУ ВВЕРХ                           │
│  2. Для каждого пикселя: смешивает цвета слоёв                  │
│  3. isOpaque = true: не нужно смотреть на слои ниже             │
│  4. Меньше прозрачности = меньше работы GPU                     │
│                                                                  │
│  ANTI-PATTERN:                                                   │
│  ══════════════                                                  │
│  10 полупрозрачных слоёв друг над другом                        │
│  = 10 blend операций на каждый пиксель                          │
│  = медленно!                                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Модель "Почтовая служба"

```
┌─────────────────────────────────────────────────────────────────┐
│          ПОЧТОВАЯ СЛУЖБА = IPC С RENDER SERVER                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  APP PROCESS                          RENDER SERVER              │
│  (Отправитель)                        (Получатель)               │
│                                                                  │
│  ┌────────────────┐                   ┌────────────────┐        │
│  │                │                   │                │        │
│  │   Упаковываем  │                   │  Распаковываем │        │
│  │   Layer Tree   │ ═══ ПОЧТА ══════► │  Layer Tree    │        │
│  │   в посылку    │   (IPC/Mach)      │  и рендерим    │        │
│  │                │                   │                │        │
│  └────────────────┘                   └────────────────┘        │
│                                                                  │
│  ЧТО ОТПРАВЛЯЕТСЯ:                                              │
│  ═════════════════                                               │
│  ├─ Иерархия слоёв (кто чей parent)                             │
│  ├─ Геометрия (bounds, position, transform)                     │
│  ├─ Содержимое (textures, images) - ДОРОГО!                     │
│  ├─ Визуальные свойства (opacity, cornerRadius)                 │
│  └─ Описание анимаций (от/до, timing)                           │
│                                                                  │
│  ОПТИМИЗАЦИИ:                                                    │
│  ═════════════                                                   │
│                                                                  │
│  1. Большие текстуры = большие посылки = медленно               │
│     → Уменьшайте размер изображений                             │
│                                                                  │
│  2. Много слоёв = много данных                                  │
│     → Объединяйте слои (shouldRasterize)                        │
│                                                                  │
│  3. Частые изменения contents = частые отправки                 │
│     → Кэшируйте что можете                                      │
│                                                                  │
│  4. Анимации отправляются ОДИН РАЗ                              │
│     → Render Server интерполирует сам                           │
│     → Это почему Core Animation анимации не блокируют UI        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Модель "Бюджет времени"

```
┌─────────────────────────────────────────────────────────────────┐
│              БЮДЖЕТ ВРЕМЕНИ = FRAME BUDGET                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  У вас есть 16.67ms (60fps) или 8.33ms (120fps) на кадр         │
│                                                                  │
│  Это как дневной бюджет денег:                                  │
│                                                                  │
│  БЮДЖЕТ 16.67ms                                                 │
│  ═══════════════                                                 │
│  ├── Layout:        5ms   ████████░░░░░░░░░░░░░░░░░░░░░         │
│  ├── Display:       3ms   ░░░░░░░░███░░░░░░░░░░░░░░░░░░         │
│  ├── Commit:        2ms   ░░░░░░░░░░░██░░░░░░░░░░░░░░░░         │
│  ├── Render:        5ms   ░░░░░░░░░░░░░████████░░░░░░░░         │
│  └── Запас:        1.67ms ░░░░░░░░░░░░░░░░░░░░░█░░░░░░░         │
│                           0        8        16.67              │
│                                                                  │
│  ПЕРЕРАСХОД БЮДЖЕТА:                                            │
│  ════════════════════                                            │
│                                                                  │
│  Если Layout занял 10ms:                                        │
│  ├── Layout:       10ms   ████████████████████░░░░░░░░░         │
│  ├── Display:       3ms   ░░░░░░░░░░░░░░░░░░░░███░░░░░░         │
│  ├── Commit:        2ms   ░░░░░░░░░░░░░░░░░░░░░░░██░░░░         │
│  ├── Render:        5ms   ░░░░░░░░░░░░░░░░░░░░░░░░░███X│← КАДР  │
│  └── ИТОГО:        20ms   ───────────────────────────X│ ПРОПУЩЕН│
│                           0        8       16.67   20          │
│                                                                  │
│  РЕЗУЛЬТАТ: dropped frame, пользователь видит "заикание"        │
│                                                                  │
│  КАК ЭКОНОМИТЬ БЮДЖЕТ:                                          │
│  ═════════════════════                                           │
│  • Меньше Auto Layout constraints                                │
│  • Кэшировать результаты draw()                                 │
│  • Использовать shouldRasterize для сложных слоёв              │
│  • Рисовать в background thread                                 │
│  • Избегать offscreen rendering                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
## Связь с другими темами

**[[android-graphics-apis]]** — Android использует аналогичный многоуровневый графический стек (Canvas/View для 2D, RenderThread для аппаратной композиции, Vulkan/OpenGL ES для низкоуровневого GPU-доступа), но с ключевыми отличиями в архитектуре рендеринга. Сравнение двух платформ помогает понять универсальные концепции GPU-ускорения (текстуры, шейдеры, double buffering) и платформо-специфичные оптимизации. Особенно полезно для кросс-платформенных проектов, где нужно оптимизировать отрисовку на обоих платформах.

**[[ios-view-rendering]]** — если данная статья описывает графические API на уровне фреймворков (Core Graphics, Core Animation, Metal), то ios-view-rendering погружается в конкретный процесс превращения UIView/SwiftUI View в пиксели на экране: render loop, commit transaction, layout-display-prepare-commit цикл. Понимание rendering pipeline необходимо для диагностики проблем производительности UI. Рекомендуется изучать после освоения основ графического стека из текущей статьи.

**[[cross-graphics-rendering]]** — кросс-платформенное сравнение графических подходов (iOS Core Animation vs Android RenderThread vs Flutter Skia vs Compose) раскрывает общие принципы и trade-offs графических систем. Эта статья помогает оценить, какие оптимизации универсальны (избегание offscreen rendering, минимизация overdraw), а какие специфичны для конкретной платформы. Рекомендуется после уверенного освоения iOS-специфичных графических API.

---

## Источники и дальнейшее чтение

### Книги
- Lockwood N. (2014). *iOS Core Animation: Advanced Techniques.* — наиболее детальный разбор Core Animation, включая implicit/explicit анимации, layer geometry, offscreen rendering и производительность; обязательна для глубокого освоения графики iOS.
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — содержит практические примеры использования Core Graphics и работы с CGContext, объясняет связь между UIKit и графическим стеком; хорошая отправная точка.
- Keur C., Hillegass A. (2020). *iOS Programming: Big Nerd Ranch Guide.* — главы по рисованию и анимации дают практическое понимание работы с Core Graphics в контексте UIKit-приложений.

### Документация
- [Core Animation Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreAnimation_guide/Introduction/Introduction.html)
- [Quartz 2D Programming Guide](https://developer.apple.com/library/archive/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d/Introduction/Introduction.html)
- [Metal Programming Guide](https://developer.apple.com/documentation/metal)

### WWDC Sessions
- **WWDC 2014** - "Working with Metal: Overview"
- **WWDC 2015** - "Advanced Graphics and Animations for iOS Apps"
- **WWDC 2018** - "Metal for Accelerating Machine Learning"
- **WWDC 2021** - "Discover Metal debugging, profiling, and asset creation tools"
- **WWDC 2023** - "Build spatial experiences with RealityKit"

---

## Проверь себя

> [!question]- Почему Core Animation работает на GPU, а Core Graphics на CPU, и когда эта разница критична?
> Core Animation оперирует слоями (CALayer) как текстурами на GPU -- композиция, трансформации, альфа-блендинг аппаратно ускорены. Core Graphics (Quartz 2D) рисует пиксели на CPU в bitmap-контекст, что медленнее, но дает полный контроль над каждым пикселем. Критично для: Core Graphics нужен для кастомного рисования (графики, сложные формы), Core Animation -- для анимаций и композиции стандартных элементов.

> [!question]- В чем разница между UIView.layer.cornerRadius с masksToBounds и создании CAShapeLayer с округленным path?
> cornerRadius + masksToBounds вызывает off-screen rendering (дополнительный проход GPU), потому что GPU должен отрисовать содержимое, затем обрезать. CAShapeLayer с path обрезает на этапе растеризации без off-screen pass. Альтернатива: layer.cornerRadius без masksToBounds + непрозрачный backgroundColor, если содержимое не выходит за границы.

> [!question]- Сценарий: ваше приложение отображает ленту с аватарами (круглые изображения). Instruments показывает off-screen rendering. Как оптимизировать?
> 1) Предварительно обрезать изображения в круг на CPU (Core Graphics) в фоне. 2) Использовать layer.shouldRasterize = true (кэшировать результат, но следить за масштабом). 3) Вместо masksToBounds: добавить overlay с "дыркой". 4) В SwiftUI: .clipShape(Circle()) оптимизирован лучше, чем UIKit cornerRadius. 5) AsyncImage с предобработкой на загрузке.

---

## Ключевые карточки

Какие уровни графического стека iOS?
?
UIKit/SwiftUI (высокий уровень) -> Core Animation (CALayer, GPU-ускоренная композиция) -> Core Graphics (Quartz 2D, CPU-рисование) -> Metal (низкоуровневый GPU). Каждый уровень добавляет абстракцию. UIKit/SwiftUI для большинства задач, Metal для игр и ML.

Что такое CALayer и как он связан с UIView?
?
Каждый UIView имеет backing CALayer (layer property). UIView -- обертка для обработки событий и Auto Layout. CALayer хранит визуальное содержимое (bitmap), трансформации, анимации. Можно добавлять sublayers без subviews для легковесной отрисовки.

Чем Core Graphics отличается от Core Animation?
?
Core Graphics: imperative 2D рисование на CPU, работает с CGContext, рисует paths/shapes/text/images попиксельно. Core Animation: декларативная анимация и композиция CALayer на GPU, работает с property-based анимациями (transform, opacity, position). CG для контента, CA для компоновки и анимации.

Что такое Metal и когда его использовать?
?
Низкоуровневый GPU API от Apple (замена OpenGL ES). Прямой доступ к GPU: шейдеры, command buffers, render pipelines. Для: игр, ML inference, AR (RealityKit), обработки видео/изображений, кастомных визуализаций. Не нужен для стандартного UI.

Что такое off-screen rendering и почему оно медленное?
?
GPU создает временный framebuffer для промежуточного результата (маска, тень, clipsToBounds). Переключение контекста GPU дорогое. Каждый off-screen pass удваивает работу для затронутого слоя. Инструмент: Color Offscreen-Rendered Yellow в Simulator Debug.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-view-rendering]] | Render loop, layers и оптимизация отрисовки |
| Углубиться | [[ios-performance-profiling]] | Instruments для профилирования графики |
| Смежная тема | [[android-graphics-apis]] | Графический стек Android для сравнения |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |

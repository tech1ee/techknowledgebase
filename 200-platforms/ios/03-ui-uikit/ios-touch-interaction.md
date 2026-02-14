---
title: "Обработка касаний в iOS"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 82
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
area: ios
tags:
  - topic/ios
  - topic/swift
  - topic/ui
  - type/deep-dive
  - level/advanced
related:
  - "[[ios-uikit-fundamentals]]"
  - "[[ios-custom-views]]"
  - "[[android-touch-handling]]"
prerequisites:
  - "[[ios-uikit-fundamentals]]"
  - "[[ios-custom-views]]"
---

## TL;DR

Touch interaction в iOS реализуется через две парадигмы: **UIKit** использует императивную модель с responder chain и gesture recognizers, а **SwiftUI** предлагает декларативный подход через gesture modifiers. UIKit дает низкоуровневый контроль через UITouch и hit testing, SwiftUI упрощает через композицию жестов и @GestureState. Обе системы поддерживают multi-touch, custom gestures и сложные взаимодействия.

## Зачем это нужно?

**Проблема:** Каждое мобильное приложение требует интуитивного взаимодействия с пользователем через касания, жесты и multi-touch. Без понимания touch handling невозможно создать responsive UI, обработать сложные жесты (drag, pinch, rotate) или решить конфликты между перекрывающимися интерактивными элементами.

**Решение:** iOS предоставляет мощную систему обработки касаний:
- **UIKit:** Responder chain для routing событий, hit testing для определения view, UIGestureRecognizer для распознавания паттернов
- **SwiftUI:** Декларативные gesture modifiers, @GestureState для управления состоянием, композиция жестов

**Преимущества:**
- Автоматический routing через responder chain
- Готовые recognizers для стандартных жестов
- Поддержка multi-touch из коробки
- Возможность создания custom gestures
- Разрешение конфликтов между жестами

## Жизненные аналогии

### 1. Responder Chain как почтовая система
```
┌─────────────────────────────────────┐
│  Письмо приходит на адрес (UIView) │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ View не обработала?          │  │
│  │ → Передает родителю          │  │
│  │   → Супервью                 │  │
│  │     → ViewController         │  │
│  │       → Window               │  │
│  │         → UIApplication      │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```
Как письмо поднимается по инстанциям, если адресат не может его обработать.

### 2. Hit Testing как прицел снайпера
Когда палец касается экрана, система ищет самый "верхний" view под точкой касания, как снайпер ищет цель через прицел - проверяет от самого глубокого child view к родителям.

### 3. Gesture Recognizer как переводчик языка жестов
UIGestureRecognizer переводит последовательность низкоуровневых touch events в высокоуровневые действия (tap, swipe, pinch) - как переводчик превращает знаки в понятные команды.

### 4. @GestureState как временная записная книжка
@GestureState хранит данные только во время жеста и автоматически сбрасывается - как временная записная книжка, которая стирается после завершения задачи.

## Архитектура Touch Handling

### UIKit Responder Chain

```
Touch Event Flow:
════════════════════════════════════════════════════════════════

1. HIT TESTING (поиск view)
   ┌─────────────────────────────────────────┐
   │         UIWindow                        │
   │  ┌───────────────────────────────────┐  │
   │  │      UIViewController.view        │  │
   │  │  ┌─────────────────────────────┐  │  │
   │  │  │      Container View         │  │  │
   │  │  │  ┌───────────────────────┐  │  │  │
   │  │  │  │   Target View (✓)     │  │  │  │
   │  │  │  └───────────────────────┘  │  │  │
   │  │  └─────────────────────────────┘  │  │
   │  └───────────────────────────────────┘  │
   │            ▲                             │
   │            │ hitTest(_:with:)            │
   │            │ point(inside:with:)         │
   └────────────┴─────────────────────────────┘

2. RESPONDER CHAIN (обработка event)
   ┌─────────────────────────────────────────┐
   │  Target View                            │
   │    │ touchesBegan(_:with:)              │
   │    ▼                                     │
   │  Superview                              │
   │    │ если не handled                    │
   │    ▼                                     │
   │  UIViewController                       │
   │    │                                     │
   │    ▼                                     │
   │  UIWindow                               │
   │    │                                     │
   │    ▼                                     │
   │  UIApplication                          │
   │    │                                     │
   │    ▼                                     │
   │  AppDelegate                            │
   └─────────────────────────────────────────┘

3. GESTURE RECOGNIZER FLOW
   ┌─────────────────────────────────────────┐
   │  Touch Event                            │
   │    │                                     │
   │    ├─► Gesture Recognizers (parallel)   │
   │    │     │                               │
   │    │     ├─► TapGesture (state: .began) │
   │    │     ├─► PanGesture (analyzing...)  │
   │    │     └─► LongPress (waiting...)     │
   │    │                                     │
   │    └─► View (touchesBegan) [delayed]    │
   │                                          │
   │  Winner: TapGesture → .recognized       │
   │  Losers: PanGesture → .failed           │
   │  View:   touchesCancelled (if gesture)  │
   └─────────────────────────────────────────┘
```

### SwiftUI Gesture Recognition

```
SwiftUI Gesture Composition:
════════════════════════════════════════════════════════════════

1. SINGLE GESTURE
   ┌──────────────────────────────────┐
   │  View                            │
   │    .gesture(DragGesture())       │
   │       │                          │
   │       ├─► .updating() ──────┐    │
   │       │   @GestureState     │    │
   │       │   (transient)       │    │
   │       │                     │    │
   │       ├─► .onChanged() ─────┤    │
   │       │   (during drag)     │    │
   │       │                     │    │
   │       └─► .onEnded() ───────┘    │
   │           (completion)           │
   └──────────────────────────────────┘

2. SIMULTANEOUS GESTURES
   ┌──────────────────────────────────┐
   │  View                            │
   │    .simultaneousGesture(         │
   │      DragGesture() +             │
   │      MagnificationGesture()      │
   │    )                             │
   │      │                           │
   │      ├──► Both can recognize    │
   │      │     at same time          │
   │      │                           │
   │      ├──► Example: Map          │
   │      └──► (pan + pinch)          │
   └──────────────────────────────────┘

3. GESTURE PRIORITY
   ┌──────────────────────────────────┐
   │  Priority Layers (bottom→top):   │
   │                                   │
   │  [3] .highPriorityGesture()      │
   │      ▲ Wins over all             │
   │      │                            │
   │  [2] .gesture()                  │
   │      ▲ Default priority          │
   │      │                            │
   │  [1] .simultaneousGesture()      │
   │      ▲ Lowest priority           │
   └──────────────────────────────────┘

4. SEQUENCED GESTURES
   ┌──────────────────────────────────┐
   │  LongPressGesture()              │
   │    .sequenced(before:            │
   │      DragGesture()               │
   │    )                             │
   │      │                           │
   │      ├─► 1. Long press first    │
   │      │     (.recognized)         │
   │      │                           │
   │      └─► 2. Then drag starts    │
   │            (sequential)          │
   └──────────────────────────────────┘
```

## UIKit Touch Handling

### Основы UITouch и Touch Phases

```swift
// ✅ ПРАВИЛЬНО: Обработка всех фаз касания
class CustomDrawingView: UIView {
    private var currentPath: UIBezierPath?
    private var points: [CGPoint] = []

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let point = touch.location(in: self)

        // Начинаем новый путь
        currentPath = UIBezierPath()
        currentPath?.move(to: point)
        points = [point]

        print("Touch began at: \(point)")
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first,
              let path = currentPath else { return }

        let point = touch.location(in: self)
        path.addLine(to: point)
        points.append(point)

        // Перерисовываем
        setNeedsDisplay()
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let point = touch.location(in: self)

        print("Touch ended at: \(point)")
        print("Total points: \(points.count)")

        // Сохраняем финальный путь
        finalizePath()
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        // ВАЖНО: Обязательно обрабатываем отмену
        // (звонок, уведомление, gesture recognizer)
        print("Touch cancelled - cleaning up")
        currentPath = nil
        points.removeAll()
        setNeedsDisplay()
    }

    private func finalizePath() {
        // Сохранение пути в persistent storage
        currentPath = nil
    }
}
```

### Hit Testing и Responder Chain

```swift
// ✅ ПРАВИЛЬНО: Custom hit testing для complex layouts
class PassThroughView: UIView {
    var hitTestViews: [UIView] = []

    override func hitTest(_ point: CGPoint, with event: UIEvent?) -> UIView? {
        // Проверяем специальные subviews первыми
        for subview in hitTestViews {
            let convertedPoint = convert(point, to: subview)
            if let hitView = subview.hitTest(convertedPoint, with: event) {
                return hitView
            }
        }

        // Для остальных - стандартное поведение
        let hitView = super.hitTest(point, with: event)

        // Если попали в self, но не в subviews - пропускаем
        if hitView == self {
            return nil
        }

        return hitView
    }

    override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
        // Custom shape hit testing (например, круг)
        let center = CGPoint(x: bounds.width / 2, y: bounds.height / 2)
        let radius = min(bounds.width, bounds.height) / 2
        let distance = hypot(point.x - center.x, point.y - center.y)

        return distance <= radius
    }
}

// ✅ ПРАВИЛЬНО: Расширение responder chain
class CustomButton: UIButton {
    var onTouchAction: ((CustomButton) -> Void)?

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesBegan(touches, with: event)
        onTouchAction?(self)

        // Можно прервать responder chain
        // Не вызывая super, событие не пойдет дальше
    }

    // Пример расширения responder chain
    override var next: UIResponder? {
        // Можно переопределить next responder
        // для custom routing logic
        return customNextResponder ?? super.next
    }

    var customNextResponder: UIResponder?
}
```

### UIGestureRecognizer - Стандартные жесты

```swift
// ✅ ПРАВИЛЬНО: Настройка gesture recognizers
class InteractiveImageView: UIView {
    private let imageView = UIImageView()
    private var currentScale: CGFloat = 1.0
    private var currentRotation: CGFloat = 0
    private var currentTranslation: CGPoint = .zero

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupGestures()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupGestures()
    }

    private func setupGestures() {
        // 1. TAP GESTURE
        let tapGesture = UITapGestureRecognizer(
            target: self,
            action: #selector(handleTap)
        )
        tapGesture.numberOfTapsRequired = 1
        tapGesture.numberOfTouchesRequired = 1
        addGestureRecognizer(tapGesture)

        // 2. DOUBLE TAP GESTURE
        let doubleTapGesture = UITapGestureRecognizer(
            target: self,
            action: #selector(handleDoubleTap)
        )
        doubleTapGesture.numberOfTapsRequired = 2

        // Single tap ждет double tap fail
        tapGesture.require(toFail: doubleTapGesture)
        addGestureRecognizer(doubleTapGesture)

        // 3. LONG PRESS GESTURE
        let longPressGesture = UILongPressGestureRecognizer(
            target: self,
            action: #selector(handleLongPress)
        )
        longPressGesture.minimumPressDuration = 0.5
        longPressGesture.allowableMovement = 10 // pixels
        addGestureRecognizer(longPressGesture)

        // 4. PAN GESTURE
        let panGesture = UIPanGestureRecognizer(
            target: self,
            action: #selector(handlePan)
        )
        panGesture.minimumNumberOfTouches = 1
        panGesture.maximumNumberOfTouches = 1
        addGestureRecognizer(panGesture)

        // 5. PINCH GESTURE
        let pinchGesture = UIPinchGestureRecognizer(
            target: self,
            action: #selector(handlePinch)
        )
        addGestureRecognizer(pinchGesture)

        // 6. ROTATION GESTURE
        let rotationGesture = UIRotationGestureRecognizer(
            target: self,
            action: #selector(handleRotation)
        )
        addGestureRecognizer(rotationGesture)

        // 7. SWIPE GESTURE
        let swipeGesture = UISwipeGestureRecognizer(
            target: self,
            action: #selector(handleSwipe)
        )
        swipeGesture.direction = [.left, .right]
        swipeGesture.numberOfTouchesRequired = 1
        addGestureRecognizer(swipeGesture)

        // Pan не должен мешать swipe
        panGesture.require(toFail: swipeGesture)

        // Pinch и rotation работают одновременно
        pinchGesture.delegate = self
        rotationGesture.delegate = self

        isUserInteractionEnabled = true
        isMultipleTouchEnabled = true
    }

    @objc private func handleTap(_ gesture: UITapGestureRecognizer) {
        let location = gesture.location(in: self)
        print("Tap at: \(location)")

        // Анимация feedback
        UIView.animate(withDuration: 0.1, animations: {
            self.alpha = 0.5
        }) { _ in
            UIView.animate(withDuration: 0.1) {
                self.alpha = 1.0
            }
        }
    }

    @objc private func handleDoubleTap(_ gesture: UITapGestureRecognizer) {
        // Reset transform
        UIView.animate(withDuration: 0.3, delay: 0, usingSpringWithDamping: 0.7,
                       initialSpringVelocity: 0.5) {
            self.imageView.transform = .identity
            self.currentScale = 1.0
            self.currentRotation = 0
        }
    }

    @objc private func handleLongPress(_ gesture: UILongPressGestureRecognizer) {
        switch gesture.state {
        case .began:
            print("Long press began")
            // Haptic feedback
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()

            UIView.animate(withDuration: 0.2) {
                self.transform = CGAffineTransform(scaleX: 0.95, y: 0.95)
            }

        case .ended, .cancelled:
            print("Long press ended")
            UIView.animate(withDuration: 0.2) {
                self.transform = .identity
            }

        default:
            break
        }
    }

    @objc private func handlePan(_ gesture: UIPanGestureRecognizer) {
        let translation = gesture.translation(in: superview)

        switch gesture.state {
        case .began:
            currentTranslation = imageView.center

        case .changed:
            imageView.center = CGPoint(
                x: currentTranslation.x + translation.x,
                y: currentTranslation.y + translation.y
            )

        case .ended:
            // Velocity для momentum
            let velocity = gesture.velocity(in: superview)
            let magnitude = sqrt(pow(velocity.x, 2) + pow(velocity.y, 2))

            if magnitude > 1000 {
                // Продолжаем движение с затуханием
                let finalPoint = CGPoint(
                    x: imageView.center.x + velocity.x * 0.1,
                    y: imageView.center.y + velocity.y * 0.1
                )

                UIView.animate(withDuration: 0.5, delay: 0,
                               usingSpringWithDamping: 0.8,
                               initialSpringVelocity: magnitude / 1000) {
                    self.imageView.center = finalPoint
                }
            }

        default:
            break
        }
    }

    @objc private func handlePinch(_ gesture: UIPinchGestureRecognizer) {
        switch gesture.state {
        case .began:
            currentScale = imageView.transform.a

        case .changed:
            let newScale = currentScale * gesture.scale
            // Ограничиваем масштаб
            let clampedScale = min(max(newScale, 0.5), 3.0)

            var transform = imageView.transform
            transform.a = clampedScale
            transform.d = clampedScale
            imageView.transform = transform

        case .ended:
            currentScale = imageView.transform.a

        default:
            break
        }
    }

    @objc private func handleRotation(_ gesture: UIRotationGestureRecognizer) {
        switch gesture.state {
        case .began:
            currentRotation = atan2(imageView.transform.b, imageView.transform.a)

        case .changed:
            let newRotation = currentRotation + gesture.rotation

            var transform = imageView.transform
            let scale = sqrt(transform.a * transform.a + transform.b * transform.b)
            transform.a = scale * cos(newRotation)
            transform.b = scale * sin(newRotation)
            transform.c = -scale * sin(newRotation)
            transform.d = scale * cos(newRotation)
            imageView.transform = transform

        case .ended:
            currentRotation = atan2(imageView.transform.b, imageView.transform.a)

        default:
            break
        }
    }

    @objc private func handleSwipe(_ gesture: UISwipeGestureRecognizer) {
        let direction = gesture.direction
        print("Swiped: \(direction)")

        // Анимация в зависимости от направления
        let translation: CGAffineTransform
        switch direction {
        case .left:
            translation = CGAffineTransform(translationX: -50, y: 0)
        case .right:
            translation = CGAffineTransform(translationX: 50, y: 0)
        default:
            return
        }

        UIView.animateKeyframes(withDuration: 0.4, delay: 0) {
            UIView.addKeyframe(withRelativeStartTime: 0, relativeDuration: 0.5) {
                self.imageView.transform = translation
            }
            UIView.addKeyframe(withRelativeStartTime: 0.5, relativeDuration: 0.5) {
                self.imageView.transform = .identity
            }
        }
    }
}

// Делегат для одновременных жестов
extension InteractiveImageView: UIGestureRecognizerDelegate {
    func gestureRecognizer(
        _ gestureRecognizer: UIGestureRecognizer,
        shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer
    ) -> Bool {
        // Pinch и rotation работают вместе
        return (gestureRecognizer is UIPinchGestureRecognizer &&
                otherGestureRecognizer is UIRotationGestureRecognizer) ||
               (gestureRecognizer is UIRotationGestureRecognizer &&
                otherGestureRecognizer is UIPinchGestureRecognizer)
    }
}
```

### Custom Gesture Recognizer

```swift
// ✅ ПРАВИЛЬНО: Custom gesture recognizer
class CircleGestureRecognizer: UIGestureRecognizer {
    private var touchPath: [CGPoint] = []
    private var startPoint: CGPoint?

    // Параметры распознавания круга
    var requiredPoints: Int = 20
    var allowedDeviation: CGFloat = 50

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent) {
        super.touchesBegan(touches, with: event)

        guard let touch = touches.first,
              let view = view else { return }

        startPoint = touch.location(in: view)
        touchPath = [startPoint!]
        state = .began
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent) {
        super.touchesMoved(touches, with: event)

        guard let touch = touches.first,
              let view = view else { return }

        let point = touch.location(in: view)
        touchPath.append(point)

        state = .changed

        // Проверяем, образует ли путь круг
        if touchPath.count >= requiredPoints {
            checkForCircle()
        }
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent) {
        super.touchesEnded(touches, with: event)

        if state == .changed {
            checkForCircle()
        }

        if state == .changed {
            state = .failed
        }

        reset()
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent) {
        super.touchesCancelled(touches, with: event)
        state = .cancelled
        reset()
    }

    override func reset() {
        super.reset()
        touchPath.removeAll()
        startPoint = nil
    }

    private func checkForCircle() {
        guard let start = startPoint,
              touchPath.count >= requiredPoints else { return }

        // Проверяем, вернулись ли к началу
        let endPoint = touchPath.last!
        let distanceToStart = hypot(endPoint.x - start.x, endPoint.y - start.y)

        if distanceToStart > allowedDeviation {
            return
        }

        // Вычисляем центр и радиус
        let center = calculateCenter()
        let radius = calculateAverageRadius(center: center)

        // Проверяем, что все точки примерно на одном расстоянии от центра
        let deviations = touchPath.map { point in
            let distance = hypot(point.x - center.x, point.y - center.y)
            return abs(distance - radius)
        }

        let averageDeviation = deviations.reduce(0, +) / CGFloat(deviations.count)

        if averageDeviation < allowedDeviation {
            state = .recognized
        }
    }

    private func calculateCenter() -> CGPoint {
        let sumX = touchPath.reduce(0) { $0 + $1.x }
        let sumY = touchPath.reduce(0) { $0 + $1.y }
        return CGPoint(
            x: sumX / CGFloat(touchPath.count),
            y: sumY / CGFloat(touchPath.count)
        )
    }

    private func calculateAverageRadius(center: CGPoint) -> CGFloat {
        let distances = touchPath.map { point in
            hypot(point.x - center.x, point.y - center.y)
        }
        return distances.reduce(0, +) / CGFloat(distances.count)
    }
}

// Использование
class DrawingViewController: UIViewController {
    private let drawingView = UIView()

    override func viewDidLoad() {
        super.viewDidLoad()

        let circleGesture = CircleGestureRecognizer(
            target: self,
            action: #selector(handleCircle)
        )
        circleGesture.requiredPoints = 25
        circleGesture.allowedDeviation = 40

        drawingView.addGestureRecognizer(circleGesture)
    }

    @objc private func handleCircle(_ gesture: CircleGestureRecognizer) {
        print("Circle detected!")

        // Визуальный feedback
        let checkmark = UIImageView(image: UIImage(systemName: "checkmark.circle.fill"))
        checkmark.tintColor = .systemGreen
        checkmark.frame.size = CGSize(width: 50, height: 50)
        checkmark.center = drawingView.center
        checkmark.alpha = 0

        drawingView.addSubview(checkmark)

        UIView.animate(withDuration: 0.3, animations: {
            checkmark.alpha = 1
            checkmark.transform = CGAffineTransform(scaleX: 1.5, y: 1.5)
        }) { _ in
            UIView.animate(withDuration: 0.2, delay: 0.5) {
                checkmark.alpha = 0
            } completion: { _ in
                checkmark.removeFromSuperview()
            }
        }
    }
}
```

### Multi-Touch Handling

```swift
// ✅ ПРАВИЛЬНО: Multi-touch обработка
class MultiTouchDrawingView: UIView {
    private var activeTouches: [UITouch: UIBezierPath] = [:]
    private var touchColors: [UITouch: UIColor] = [:]

    private let colors: [UIColor] = [
        .systemRed, .systemBlue, .systemGreen,
        .systemOrange, .systemPurple
    ]

    override init(frame: CGRect) {
        super.init(frame: frame)
        // ВАЖНО: Включаем multi-touch
        isMultipleTouchEnabled = true
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        isMultipleTouchEnabled = true
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        for touch in touches {
            let point = touch.location(in: self)

            // Создаем новый путь для каждого касания
            let path = UIBezierPath()
            path.move(to: point)
            path.lineWidth = 3.0

            activeTouches[touch] = path

            // Назначаем цвет
            let colorIndex = activeTouches.count % colors.count
            touchColors[touch] = colors[colorIndex]

            print("Touch \(touch.hash) began at \(point)")
        }

        setNeedsDisplay()
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        for touch in touches {
            guard let path = activeTouches[touch] else { continue }

            let point = touch.location(in: self)
            path.addLine(to: point)

            // Можно получить дополнительные свойства
            let force = touch.force // 3D Touch (старые устройства)
            let majorRadius = touch.majorRadius

            print("Touch \(touch.hash) moved: force=\(force), radius=\(majorRadius)")
        }

        setNeedsDisplay()
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        for touch in touches {
            activeTouches.removeValue(forKey: touch)
            touchColors.removeValue(forKey: touch)

            print("Touch \(touch.hash) ended")
        }

        setNeedsDisplay()
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        // Очищаем все касания
        for touch in touches {
            activeTouches.removeValue(forKey: touch)
            touchColors.removeValue(forKey: touch)
        }

        setNeedsDisplay()
    }

    override func draw(_ rect: CGRect) {
        super.draw(rect)

        guard let context = UIGraphicsGetCurrentContext() else { return }

        // Рисуем каждый активный путь своим цветом
        for (touch, path) in activeTouches {
            if let color = touchColors[touch] {
                context.setStrokeColor(color.cgColor)
                context.setLineWidth(3.0)
                context.setLineCap(.round)
                context.addPath(path.cgPath)
                context.strokePath()
            }
        }
    }
}

// Пример с multi-touch жестами
class TwoFingerRotationView: UIView {
    private var firstTouch: UITouch?
    private var secondTouch: UITouch?
    private var initialAngle: CGFloat = 0
    private var currentRotation: CGFloat = 0

    override init(frame: CGRect) {
        super.init(frame: frame)
        isMultipleTouchEnabled = true
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        isMultipleTouchEnabled = true
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        if firstTouch == nil, let touch = touches.first {
            firstTouch = touch
        } else if secondTouch == nil, let touch = touches.first(where: { $0 != firstTouch }) {
            secondTouch = touch

            // Вычисляем начальный угол между двумя пальцами
            if let first = firstTouch, let second = secondTouch {
                initialAngle = angleBetweenTouches(first, second)
            }
        }
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let first = firstTouch,
              let second = secondTouch else { return }

        let currentAngle = angleBetweenTouches(first, second)
        let rotation = currentAngle - initialAngle

        // Применяем вращение
        transform = CGAffineTransform(rotationAngle: currentRotation + rotation)
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        if touches.contains(firstTouch!) {
            firstTouch = nil
            currentRotation = atan2(transform.b, transform.a)
        }

        if let second = secondTouch, touches.contains(second) {
            secondTouch = nil
            currentRotation = atan2(transform.b, transform.a)
        }
    }

    private func angleBetweenTouches(_ touch1: UITouch, _ touch2: UITouch) -> CGFloat {
        let point1 = touch1.location(in: superview)
        let point2 = touch2.location(in: superview)

        return atan2(point2.y - point1.y, point2.x - point1.x)
    }
}
```

## SwiftUI Gesture Handling

### Базовые жесты

```swift
// ✅ ПРАВИЛЬНО: SwiftUI базовые жесты
struct BasicGesturesView: View {
    @State private var tapCount = 0
    @State private var isPressed = false
    @State private var offset = CGSize.zero
    @State private var scale: CGFloat = 1.0
    @State private var rotation: Angle = .zero

    var body: some View {
        VStack(spacing: 40) {
            // 1. TAP GESTURE
            Circle()
                .fill(Color.blue)
                .frame(width: 100, height: 100)
                .overlay(
                    Text("\(tapCount)")
                        .foregroundColor(.white)
                        .font(.title)
                )
                .onTapGesture(count: 2) {
                    // Double tap
                    tapCount = 0
                }
                .onTapGesture {
                    // Single tap
                    tapCount += 1
                }

            // 2. LONG PRESS GESTURE
            RoundedRectangle(cornerRadius: 20)
                .fill(isPressed ? Color.green : Color.gray)
                .frame(width: 200, height: 100)
                .overlay(
                    Text(isPressed ? "Pressed!" : "Long Press Me")
                        .foregroundColor(.white)
                )
                .scaleEffect(isPressed ? 0.95 : 1.0)
                .onLongPressGesture(
                    minimumDuration: 0.5,
                    maximumDistance: 50
                ) {
                    // onEnded
                    isPressed = false
                } onPressingChanged: { pressing in
                    // onChanged
                    withAnimation(.spring(response: 0.3)) {
                        isPressed = pressing
                    }
                }

            // 3. DRAG GESTURE
            RoundedRectangle(cornerRadius: 15)
                .fill(Color.orange)
                .frame(width: 150, height: 150)
                .offset(offset)
                .gesture(
                    DragGesture()
                        .onChanged { value in
                            offset = value.translation
                        }
                        .onEnded { value in
                            // Momentum animation
                            withAnimation(.interpolatingSpring(
                                mass: 1.0,
                                stiffness: 50,
                                damping: 10,
                                initialVelocity: 5
                            )) {
                                offset = .zero
                            }
                        }
                )

            // 4. MAGNIFICATION GESTURE (Pinch)
            Image(systemName: "star.fill")
                .font(.system(size: 50))
                .foregroundColor(.yellow)
                .scaleEffect(scale)
                .gesture(
                    MagnificationGesture()
                        .onChanged { value in
                            scale = value.magnitude
                        }
                        .onEnded { value in
                            withAnimation(.spring()) {
                                scale = min(max(value.magnitude, 0.5), 3.0)
                            }
                        }
                )

            // 5. ROTATION GESTURE
            Rectangle()
                .fill(LinearGradient(
                    colors: [.purple, .pink],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                ))
                .frame(width: 120, height: 120)
                .rotationEffect(rotation)
                .gesture(
                    RotationGesture()
                        .onChanged { angle in
                            rotation = angle
                        }
                        .onEnded { angle in
                            // Snap to nearest 90 degrees
                            let degrees = angle.degrees
                            let snapped = round(degrees / 90) * 90
                            withAnimation(.spring()) {
                                rotation = Angle(degrees: snapped)
                            }
                        }
                )
        }
        .padding()
    }
}
```

### @GestureState для временного состояния

```swift
// ✅ ПРАВИЛЬНО: @GestureState для transient state
struct GestureStateExample: View {
    @GestureState private var dragOffset = CGSize.zero
    @GestureState private var isLongPressing = false
    @GestureState private var magnification: CGFloat = 1.0

    @State private var permanentOffset = CGSize.zero
    @State private var permanentScale: CGFloat = 1.0

    var body: some View {
        VStack(spacing: 50) {
            // Пример 1: Drag с автовозвратом
            Circle()
                .fill(Color.blue)
                .frame(width: 100, height: 100)
                .offset(dragOffset)
                .gesture(
                    DragGesture()
                        .updating($dragOffset) { value, state, transaction in
                            // state автоматически сбросится в .zero после жеста
                            state = value.translation

                            // transaction позволяет настроить анимацию
                            transaction.animation = .spring()
                        }
                )
                .overlay(
                    Text("Auto-returns")
                        .font(.caption)
                        .offset(y: 70)
                )

            // Пример 2: Drag с сохранением позиции
            Circle()
                .fill(Color.green)
                .frame(width: 100, height: 100)
                .offset(x: permanentOffset.width, y: permanentOffset.height)
                .gesture(
                    DragGesture()
                        .updating($dragOffset) { value, state, transaction in
                            state = value.translation
                        }
                        .onEnded { value in
                            // Сохраняем финальную позицию в @State
                            permanentOffset.width += value.translation.width
                            permanentOffset.height += value.translation.height
                        }
                )
                .overlay(
                    Text("Stays in place")
                        .font(.caption)
                        .offset(y: 70)
                )

            // Пример 3: Long press с visual feedback
            RoundedRectangle(cornerRadius: 20)
                .fill(isLongPressing ? Color.red : Color.gray)
                .frame(width: 200, height: 100)
                .scaleEffect(isLongPressing ? 0.9 : 1.0)
                .gesture(
                    LongPressGesture(minimumDuration: 0.5)
                        .updating($isLongPressing) { currentState, state, transaction in
                            state = currentState
                            transaction.animation = .easeInOut(duration: 0.2)
                        }
                        .onEnded { _ in
                            print("Long press completed!")
                        }
                )

            // Пример 4: Pinch с limits
            Image(systemName: "photo")
                .font(.system(size: 60))
                .scaleEffect(permanentScale * magnification)
                .gesture(
                    MagnificationGesture()
                        .updating($magnification) { value, state, transaction in
                            state = value.magnitude
                        }
                        .onEnded { value in
                            // Применяем с ограничениями
                            let newScale = permanentScale * value.magnitude
                            permanentScale = min(max(newScale, 0.5), 3.0)
                        }
                )
        }
    }
}
```

### Композиция жестов

```swift
// ✅ ПРАВИЛЬНО: Одновременные и последовательные жесты
struct GestureCompositionView: View {
    @GestureState private var dragOffset = CGSize.zero
    @GestureState private var magnification: CGFloat = 1.0
    @GestureState private var rotation: Angle = .zero
    @GestureState private var isDetectingLongPress = false

    @State private var currentPosition = CGSize.zero
    @State private var currentScale: CGFloat = 1.0
    @State private var currentRotation: Angle = .zero

    var body: some View {
        VStack(spacing: 60) {
            // 1. SIMULTANEOUS GESTURES - работают одновременно
            Text("Pinch + Rotate")
                .font(.title)
                .padding(40)
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(20)
                .scaleEffect(currentScale * magnification)
                .rotationEffect(currentRotation + rotation)
                .gesture(
                    SimultaneousGesture(
                        MagnificationGesture()
                            .updating($magnification) { value, state, _ in
                                state = value.magnitude
                            }
                            .onEnded { value in
                                currentScale *= value.magnitude
                            },
                        RotationGesture()
                            .updating($rotation) { value, state, _ in
                                state = value
                            }
                            .onEnded { value in
                                currentRotation += value
                            }
                    )
                )

            // 2. SEQUENCED GESTURES - последовательное выполнение
            Text("Long Press → Drag")
                .font(.title2)
                .padding(30)
                .background(isDetectingLongPress ? Color.green : Color.orange)
                .foregroundColor(.white)
                .cornerRadius(15)
                .offset(x: currentPosition.width + dragOffset.width,
                        y: currentPosition.height + dragOffset.height)
                .scaleEffect(isDetectingLongPress ? 0.95 : 1.0)
                .gesture(
                    LongPressGesture(minimumDuration: 0.5)
                        .updating($isDetectingLongPress) { value, state, _ in
                            state = value
                        }
                        .sequenced(before: DragGesture())
                        .updating($dragOffset) { value, state, transaction in
                            // value имеет тип SequenceGesture<LongPressGesture, DragGesture>.Value
                            switch value {
                            case .second(true, let drag):
                                // Long press завершен, идет drag
                                state = drag?.translation ?? .zero
                            default:
                                break
                            }
                        }
                        .onEnded { value in
                            guard case .second(true, let drag?) = value else { return }
                            currentPosition.width += drag.translation.width
                            currentPosition.height += drag.translation.height
                        }
                )

            // 3. EXCLUSIVE GESTURES - только один работает
            Text("Drag OR Long Press")
                .font(.title2)
                .padding(30)
                .background(Color.purple)
                .foregroundColor(.white)
                .cornerRadius(15)
                .gesture(
                    ExclusiveGesture(
                        DragGesture(minimumDistance: 20)
                            .onChanged { _ in
                                print("Dragging...")
                            },
                        LongPressGesture(minimumDuration: 1.0)
                            .onEnded { _ in
                                print("Long pressed!")
                            }
                    )
                )

            // 4. COMPLEX COMPOSITION - все вместе
            ComplexGestureView()
        }
        .padding()
    }
}

struct ComplexGestureView: View {
    @State private var offset = CGSize.zero
    @State private var scale: CGFloat = 1.0
    @State private var rotation: Angle = .zero

    @GestureState private var gestureOffset = CGSize.zero
    @GestureState private var gestureScale: CGFloat = 1.0
    @GestureState private var gestureRotation: Angle = .zero

    var body: some View {
        RoundedRectangle(cornerRadius: 25)
            .fill(
                LinearGradient(
                    colors: [.pink, .purple, .blue],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .frame(width: 150, height: 150)
            .scaleEffect(scale * gestureScale)
            .rotationEffect(rotation + gestureRotation)
            .offset(
                x: offset.width + gestureOffset.width,
                y: offset.height + gestureOffset.height
            )
            .gesture(
                SimultaneousGesture(
                    SimultaneousGesture(
                        MagnificationGesture()
                            .updating($gestureScale) { value, state, _ in
                                state = value.magnitude
                            }
                            .onEnded { value in
                                scale *= value.magnitude
                            },
                        RotationGesture()
                            .updating($gestureRotation) { value, state, _ in
                                state = value
                            }
                            .onEnded { value in
                                rotation += value
                            }
                    ),
                    DragGesture()
                        .updating($gestureOffset) { value, state, _ in
                            state = value.translation
                        }
                        .onEnded { value in
                            offset.width += value.translation.width
                            offset.height += value.translation.height
                        }
                )
            )
            .overlay(
                Text("Multi-gesture")
                    .font(.caption)
                    .foregroundColor(.white)
            )
    }
}
```

### Приоритеты жестов

```swift
// ✅ ПРАВИЛЬНО: Управление приоритетами жестов
struct GesturePriorityView: View {
    @State private var cardOffset = CGSize.zero
    @State private var buttonTapped = false

    var body: some View {
        VStack(spacing: 40) {
            // Проблема: кнопка внутри draggable card
            Text("Priority Management")
                .font(.title)

            // 1. LOW PRIORITY - simultaneousGesture (фоновый)
            VStack {
                Text("Lowest Priority")
                    .font(.headline)

                RoundedRectangle(cornerRadius: 15)
                    .fill(Color.blue.opacity(0.3))
                    .frame(width: 200, height: 100)
                    .overlay(
                        Button("Tap Me") {
                            print("Button tapped!")
                        }
                        .buttonStyle(.borderedProminent)
                    )
                    .simultaneousGesture(
                        DragGesture()
                            .onChanged { value in
                                print("Background drag: \(value.translation)")
                            }
                    )
                    .overlay(
                        Text("Button wins, drag also works")
                            .font(.caption)
                            .offset(y: 65)
                    )
            }

            // 2. NORMAL PRIORITY - .gesture (стандартный)
            VStack {
                Text("Normal Priority")
                    .font(.headline)

                RoundedRectangle(cornerRadius: 15)
                    .fill(Color.green.opacity(0.3))
                    .frame(width: 200, height: 100)
                    .overlay(
                        Button("Tap Me") {
                            print("Button tapped!")
                        }
                        .buttonStyle(.borderedProminent)
                    )
                    .gesture(
                        DragGesture()
                            .onChanged { value in
                                print("Normal drag: \(value.translation)")
                            }
                    )
                    .overlay(
                        Text("Gesture wins over button")
                            .font(.caption)
                            .offset(y: 65)
                    )
            }

            // 3. HIGH PRIORITY - .highPriorityGesture (приоритетный)
            VStack {
                Text("High Priority")
                    .font(.headline)

                RoundedRectangle(cornerRadius: 15)
                    .fill(Color.red.opacity(0.3))
                    .frame(width: 200, height: 100)
                    .overlay(
                        Button("Try to Tap") {
                            print("Button tapped!")
                        }
                        .buttonStyle(.borderedProminent)
                    )
                    .highPriorityGesture(
                        DragGesture(minimumDistance: 0)
                            .onChanged { value in
                                print("High priority drag: \(value.translation)")
                            }
                    )
                    .overlay(
                        Text("Gesture blocks everything")
                            .font(.caption)
                            .offset(y: 65)
                    )
            }

            // 4. ПРАВИЛЬНОЕ РЕШЕНИЕ - комбинация подходов
            CardWithButtonView()
        }
        .padding()
    }
}

struct CardWithButtonView: View {
    @State private var cardOffset = CGSize.zero
    @State private var buttonPressed = false
    @GestureState private var dragState = DragState.inactive

    enum DragState {
        case inactive
        case dragging(translation: CGSize)

        var translation: CGSize {
            switch self {
            case .inactive:
                return .zero
            case .dragging(let translation):
                return translation
            }
        }

        var isDragging: Bool {
            switch self {
            case .inactive:
                return false
            case .dragging:
                return true
            }
        }
    }

    var body: some View {
        VStack {
            Text("Correct Solution")
                .font(.headline)

            ZStack {
                RoundedRectangle(cornerRadius: 20)
                    .fill(Color.orange.opacity(0.3))
                    .frame(width: 250, height: 150)

                VStack(spacing: 20) {
                    Text("Drag card anywhere")
                        .font(.subheadline)

                    Button(action: {
                        buttonPressed.toggle()
                        print("Button works! \(buttonPressed)")
                    }) {
                        Text(buttonPressed ? "Pressed!" : "Button Works")
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    // Кнопка блокирует gesture родителя
                    .gesture(
                        TapGesture()
                            .onEnded { _ in
                                buttonPressed.toggle()
                            }
                    )
                }
            }
            .offset(
                x: cardOffset.width + dragState.translation.width,
                y: cardOffset.height + dragState.translation.height
            )
            .scaleEffect(dragState.isDragging ? 1.05 : 1.0)
            .animation(.spring(response: 0.3), value: dragState.isDragging)
            // simultaneousGesture не блокирует кнопку
            .simultaneousGesture(
                DragGesture()
                    .updating($dragState) { value, state, _ in
                        state = .dragging(translation: value.translation)
                    }
                    .onEnded { value in
                        cardOffset.width += value.translation.width
                        cardOffset.height += value.translation.height
                    }
            )

            Text("Drag works + Button works")
                .font(.caption)
                .padding(.top, 5)
        }
    }
}
```

### Custom SwiftUI Gestures

```swift
// ✅ ПРАВИЛЬНО: Создание custom gesture в SwiftUI
struct ShakeGesture: Gesture {
    typealias Value = Bool

    let minimumShakes: Int
    let shakeThreshold: CGFloat

    init(minimumShakes: Int = 3, shakeThreshold: CGFloat = 50) {
        self.minimumShakes = minimumShakes
        self.shakeThreshold = shakeThreshold
    }

    func body(content: Content) -> some Gesture {
        DragGesture(minimumDistance: 0)
            .onChanged { _ in }
            .onEnded { _ in }
    }
}

// Более практичный пример - двойной drag gesture
struct DoubleDragGesture: Gesture {
    typealias Value = CGSize

    @State private var firstDragCompleted = false
    @State private var firstDragTranslation = CGSize.zero

    var body: some Gesture {
        DragGesture()
            .onEnded { value in
                if !firstDragCompleted {
                    firstDragCompleted = true
                    firstDragTranslation = value.translation
                }
            }
    }
}

// Practical example: направленный drag (только horizontal или vertical)
struct DirectionalDragGesture: Gesture {
    enum Direction {
        case horizontal
        case vertical
    }

    let direction: Direction

    typealias Value = DragGesture.Value

    var body: some Gesture {
        DragGesture()
    }
}

struct DirectionalDragView: View {
    @State private var horizontalOffset: CGFloat = 0
    @State private var verticalOffset: CGFloat = 0

    var body: some View {
        VStack(spacing: 50) {
            // Только horizontal drag
            RoundedRectangle(cornerRadius: 15)
                .fill(Color.blue)
                .frame(width: 200, height: 80)
                .offset(x: horizontalOffset)
                .gesture(
                    DragGesture()
                        .onChanged { value in
                            // Фильтруем только horizontal movement
                            if abs(value.translation.width) > abs(value.translation.height) {
                                horizontalOffset = value.translation.width
                            }
                        }
                        .onEnded { _ in
                            withAnimation(.spring()) {
                                horizontalOffset = 0
                            }
                        }
                )
                .overlay(
                    Text("Horizontal Only")
                        .foregroundColor(.white)
                )

            // Только vertical drag
            RoundedRectangle(cornerRadius: 15)
                .fill(Color.green)
                .frame(width: 80, height: 200)
                .offset(y: verticalOffset)
                .gesture(
                    DragGesture()
                        .onChanged { value in
                            // Фильтруем только vertical movement
                            if abs(value.translation.height) > abs(value.translation.width) {
                                verticalOffset = value.translation.height
                            }
                        }
                        .onEnded { _ in
                            withAnimation(.spring()) {
                                verticalOffset = 0
                            }
                        }
                )
                .overlay(
                    Text("Vertical\nOnly")
                        .foregroundColor(.white)
                        .multilineTextAlignment(.center)
                )
        }
    }
}
```

## Типичные ошибки

### ❌ Ошибка 1: Забыли touchesCancelled

```swift
// ❌ НЕПРАВИЛЬНО: Не обрабатываем отмену
class BadDrawingView: UIView {
    var currentPath: UIBezierPath?

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        currentPath = UIBezierPath()
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        savePath(currentPath)
        currentPath = nil
    }

    // Нет touchesCancelled - путь "висит" при звонке/уведомлении
}

// ✅ ПРАВИЛЬНО: Всегда обрабатываем cancellation
class GoodDrawingView: UIView {
    var currentPath: UIBezierPath?

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        currentPath = UIBezierPath()
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        finalizePath()
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        // ОБЯЗАТЕЛЬНО очищаем состояние
        currentPath = nil
        setNeedsDisplay()
    }

    private func finalizePath() {
        savePath(currentPath)
        currentPath = nil
    }
}
```

### ❌ Ошибка 2: Не включили multi-touch

```swift
// ❌ НЕПРАВИЛЬНО: Забыли включить multi-touch
class BadMultiTouchView: UIView {
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        // touches.count всегда 1, даже при нескольких пальцах
        print("Touches: \(touches.count)") // Always 1!
    }
}

// ✅ ПРАВИЛЬНО: Явно включаем multi-touch
class GoodMultiTouchView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)
        isMultipleTouchEnabled = true // ВАЖНО!
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        isMultipleTouchEnabled = true
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        print("Touches: \(touches.count)") // Может быть > 1

        // Обрабатываем все касания
        for touch in touches {
            handleTouch(touch)
        }
    }
}
```

### ❌ Ошибка 3: Конфликт gesture recognizers

```swift
// ❌ НЕПРАВИЛЬНО: Gesture recognizers конфликтуют
class BadGestureView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)

        let tap = UITapGestureRecognizer(target: self, action: #selector(handleTap))
        addGestureRecognizer(tap)

        let doubleTap = UITapGestureRecognizer(target: self, action: #selector(handleDoubleTap))
        doubleTap.numberOfTapsRequired = 2
        addGestureRecognizer(doubleTap)

        // Проблема: single tap срабатывает раньше double tap
    }

    @objc func handleTap() {
        print("Tap") // Срабатывает всегда, даже при double tap
    }

    @objc func handleDoubleTap() {
        print("Double tap") // Редко срабатывает
    }
}

// ✅ ПРАВИЛЬНО: Настраиваем зависимости
class GoodGestureView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)

        let tap = UITapGestureRecognizer(target: self, action: #selector(handleTap))
        let doubleTap = UITapGestureRecognizer(target: self, action: #selector(handleDoubleTap))
        doubleTap.numberOfTapsRequired = 2

        // Single tap ждет, пока double tap не провалится
        tap.require(toFail: doubleTap)

        addGestureRecognizer(tap)
        addGestureRecognizer(doubleTap)
    }

    @objc func handleTap() {
        print("Tap") // Только после проверки double tap
    }

    @objc func handleDoubleTap() {
        print("Double tap") // Работает корректно
    }
}
```

### ❌ Ошибка 4: Неправильный приоритет SwiftUI жестов

```swift
// ❌ НЕПРАВИЛЬНО: Кнопка не работает из-за gesture
struct BadPriorityView: View {
    @State private var offset = CGSize.zero

    var body: some View {
        VStack {
            Button("Tap Me") {
                print("Button tapped")
            }
        }
        .gesture(
            DragGesture(minimumDistance: 0) // minimumDistance: 0 блокирует все
                .onChanged { value in
                    offset = value.translation
                }
        )
        // Кнопка не работает - gesture перехватывает все касания
    }
}

// ✅ ПРАВИЛЬНО: Используем simultaneousGesture или минимальное расстояние
struct GoodPriorityView: View {
    @State private var offset = CGSize.zero

    var body: some View {
        VStack {
            Button("Tap Me") {
                print("Button tapped") // Работает!
            }
        }
        .simultaneousGesture(
            DragGesture(minimumDistance: 10) // Даем кнопке шанс
                .onChanged { value in
                    offset = value.translation
                }
        )
        // Или используем .gesture() с разумным minimumDistance
    }
}
```

### ❌ Ошибка 5: Забыли @GestureState для временного состояния

```swift
// ❌ НЕПРАВИЛЬНО: @State для transient gesture data
struct BadGestureStateView: View {
    @State private var dragOffset = CGSize.zero // Не сбрасывается

    var body: some View {
        Circle()
            .offset(dragOffset)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        dragOffset = value.translation
                    }
                    // Забыли onEnded - offset не сбрасывается
            )
        // Проблема: при отмене жеста offset остается
    }
}

// ✅ ПРАВИЛЬНО: @GestureState автоматически сбрасывается
struct GoodGestureStateView: View {
    @GestureState private var dragOffset = CGSize.zero
    @State private var position = CGSize.zero

    var body: some View {
        Circle()
            .offset(
                x: position.width + dragOffset.width,
                y: position.height + dragOffset.height
            )
            .gesture(
                DragGesture()
                    .updating($dragOffset) { value, state, transaction in
                        state = value.translation
                        // state автоматически .zero после жеста
                    }
                    .onEnded { value in
                        // Сохраняем финальную позицию в @State
                        position.width += value.translation.width
                        position.height += value.translation.height
                    }
            )
    }
}
```

### ❌ Ошибка 6: Неправильный hit testing

```swift
// ❌ НЕПРАВИЛЬНО: Некорректная логика hit testing
class BadHitTestView: UIView {
    override func hitTest(_ point: CGPoint, with event: UIEvent?) -> UIView? {
        // Забыли проверить базовые условия
        let hitView = super.hitTest(point, with: event)

        // Всегда возвращаем self - блокируем subviews
        return self
    }
}

// ✅ ПРАВИЛЬНО: Правильная последовательность проверок
class GoodHitTestView: UIView {
    override func hitTest(_ point: CGPoint, with event: UIEvent?) -> UIView? {
        // 1. Проверяем базовые условия
        guard isUserInteractionEnabled,
              !isHidden,
              alpha >= 0.01 else {
            return nil
        }

        // 2. Проверяем, попадает ли точка в bounds
        guard self.point(inside: point, with: event) else {
            return nil
        }

        // 3. Ищем в subviews (reverse order - сверху вниз)
        for subview in subviews.reversed() {
            let convertedPoint = convert(point, to: subview)
            if let hitView = subview.hitTest(convertedPoint, with: event) {
                return hitView
            }
        }

        // 4. Если ничего не нашли в subviews, возвращаем self
        return self
    }

    override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
        // Custom hit area (например, увеличенная для маленькой кнопки)
        let expandedBounds = bounds.insetBy(dx: -10, dy: -10)
        return expandedBounds.contains(point)
    }
}
```

## Ментальные модели

### 1. Responder Chain как эскалация проблемы

```
Сотрудник → Менеджер → Директор → CEO
   View   →  SuperView → ViewController → Window → Application

Каждый уровень может:
- Обработать событие (solved)
- Передать выше (escalate)
- Проигнорировать (не вызывать super)
```

### 2. Gesture Recognition как нейронная сеть

```
Raw Touch Input → Feature Extraction → Pattern Recognition → Action
    UITouch     →  движение, время  →  Tap/Pan/Pinch?  →  Callback

Gesture recognizer анализирует последовательность
касаний и распознает паттерны, как мозг
распознает образы.
```

### 3. @GestureState как стек вызовов функций

```
function dragItem() {
    let tempOffset = 0  // @GestureState

    while (dragging) {
        tempOffset = calculateOffset()
        render()
    }

    // tempOffset автоматически очищается при выходе
}

@GestureState живет только во время жеста,
как локальная переменная в scope функции.
```

### 4. Hit Testing как Z-Index поиск

```
          [View C]  ← начинаем отсюда (top)
              ↓
    [View B]        ← если не нашли
        ↓
[View A]            ← если не нашли
    ↓
Background          ← последний шанс

Ищем "самый верхний" view под точкой,
обходя дерево в обратном порядке (reverse).
```

---

## Проверь себя

> [!question]- Как iOS определяет, какой view должен получить touch event, если несколько views перекрываются?
> Через hit testing: hitTest(_:with:) обходит view hierarchy в обратном порядке (от последнего subview к первому). Для каждого view вызывается point(inside:with:). Первый view, содержащий точку касания и имеющий isUserInteractionEnabled = true, становится first responder.

> [!question]- Почему gesture recognizer может "съедать" touch events у subviews?
> По умолчанию cancelsTouchesInView = true: когда gesture recognizer распознаёт жест, он отменяет touches для view. delaysTouchesBegan = false: touches доставляются сразу, но могут быть отменены. Для одновременной работы используйте gestureRecognizerShouldRecognizeSimultaneously.

> [!question]- Чем отличается обработка жестов в SwiftUI от UIKit?
> UIKit: императивный -- создаёте UIGestureRecognizer, добавляете к view, реагируете на state changes через target-action. SwiftUI: декларативный -- .gesture(DragGesture()), @GestureState для состояния, композиция через .simultaneously и .sequenced. SwiftUI автоматически управляет lifecycle жестов.

---

## Ключевые карточки

Что такое Responder Chain в iOS?
?
Цепочка объектов (UIResponder), через которую передаются необработанные события. View -> ViewController -> Parent VC -> Window -> Application -> AppDelegate. Если объект не обработал event, он передаётся дальше по цепочке.

Как работает hit testing?
?
hitTest(_:with:) обходит view hierarchy в обратном порядке subviews. Для каждого view проверяется: isUserInteractionEnabled, alpha > 0.01, isHidden == false, point(inside:). Возвращает самый "глубокий" view, содержащий точку.

Какие gesture recognizers есть в UIKit?
?
UITapGestureRecognizer (tap), UIPanGestureRecognizer (drag), UIPinchGestureRecognizer (pinch), UIRotationGestureRecognizer (rotation), UILongPressGestureRecognizer (long press), UISwipeGestureRecognizer (swipe). Можно создавать custom.

Что такое @GestureState в SwiftUI?
?
Property wrapper для хранения промежуточного состояния жеста. Автоматически сбрасывается в начальное значение при завершении жеста. Используется с .updating() modifier. Пример: @GestureState var dragOffset: CGSize = .zero.

Как обеспечить одновременную работу нескольких жестов?
?
UIKit: реализовать UIGestureRecognizerDelegate.gestureRecognizer(_:shouldRecognizeSimultaneouslyWith:). SwiftUI: .simultaneously(with:) для параллельных жестов, .sequenced(before:) для последовательных.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-accessibility]] | Обеспечить accessibility для touch interactions |
| Углубиться | [[ios-view-rendering]] | Понять как touch events связаны с render loop |
| Смежная тема | [[android-touch-handling]] | Сравнить Responder Chain с Android touch dispatch |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |
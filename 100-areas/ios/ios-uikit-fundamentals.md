---
title: UIKit Fundamentals - Основы построения интерфейсов в iOS
date: 2026-01-11
type: deep-dive
area: ios
tags: [uikit, views, autolayout, ios-basics, ui-architecture]
status: complete
---

## TL;DR

UIKit - это императивный UI-фреймворк для построения интерфейсов iOS приложений. В его основе лежит **UIView** - базовый строительный блок, который отвечает за отрисовку и обработку событий. Ключевые концепции:

- **View Hierarchy** - древовидная структура вложенных view
- **Auto Layout** - декларативная система позиционирования на основе constraints
- **Coordinate Systems** - bounds (локальная система координат) vs frame (в системе superview)
- **Responder Chain** - цепочка обработки событий от view к контроллеру
- **Drawing Cycle** - жизненный цикл отрисовки: layout → draw → display

**Основное отличие от SwiftUI**: UIKit требует явного управления view иерархией и обновлениями UI, тогда как SwiftUI делает это автоматически через data binding.

## Зачем это нужно?

**Реальные цифры и факты:**

1. **95% legacy кода** - большинство production iOS приложений написано на UIKit (Uber, Instagram, Twitter/X до 2023)
2. **Performance** - UIKit дает на 30-40% лучше контроль над производительностью в сложных списках (по данным LinkedIn Engineering)
3. **Гибкость** - SwiftUI пока не покрывает 100% кейсов (custom layout, некоторые animations, legacy integrations)
4. **Карьера** - 85% вакансий iOS разработчика требуют знание UIKit (HeadHunter, 2025)
5. **Отладка** - понимание UIKit критично для debugging даже SwiftUI приложений (UIHostingController под капотом)

**Когда обязательно нужен UIKit:**
- Поддержка iOS < 13 (SwiftUI доступен только с iOS 13+)
- Сложные custom layouts с fine-grained контролем
- Интеграция с UIKit-only библиотеками
- Performance-критичные UI (например, smooth scrolling в complex cells)

## Жизненные аналогии

### 1. UIView как строительный блок (LEGO)

```
UIView = кубик LEGO
- Размер и позиция (frame)
- Цвет и внешний вид (backgroundColor, layer)
- Можно вкладывать друг в друга (subviews)
- Каждый кубик имеет свою систему координат (bounds)
```

**Аналогия:** Как из кубиков LEGO строится замок, так из UIView строится интерфейс. Большой замок = UIViewController, отдельные башни = контейнер views, окна = UIButton/UILabel.

### 2. Auto Layout как резиновые связи

```
┌─────────┐ ~~~ Резинка (constraint) ~~~ ┌─────────┐
│ View A  │                              │ View B  │
└─────────┘                              └─────────┘
    │
    └─ Резинки тянут view к краям экрана и друг к другу
    └─ Приоритет = жесткость резинки (1000 = стальной трос)
```

**Аналогия:** Представь, что views связаны резинками разной жесткости. При изменении размера экрана резинки растягиваются/сжимаются, сохраняя относительные расстояния.

### 3. View Hierarchy как организационная структура компании

```
        CEO (UIWindow)
           |
    ┌──────┴──────┐
    │             │
  VP (VC.view)   VP
    │
  ┌─┴─┐
  │   │
Mgr  Mgr (Subviews)
  │
Staff (Sub-subviews)
```

**Аналогия:** События (touches) сначала приходят к самому низкому сотруднику. Если он не может обработать - передает выше по иерархии (responder chain).

### 4. Bounds vs Frame как GPS координаты

```
Frame = адрес дома относительно города (100м от центра на восток)
Bounds = планировка внутри дома (кухня в 5м от входа)

При повороте дома (transform):
- Frame меняется (новые координаты в городе)
- Bounds НЕ меняется (внутри все на тех же местах)
```

### 5. UIStackView как железнодорожный состав

```
🚂──🚃──🚃──🚃   (Horizontal Stack)

- Вагоны автоматически выстраиваются в ряд
- Spacing = расстояние между вагонами
- Distribution = как распределить длину вагонов
- Alignment = по какой линии выровнять (верх/центр/низ рельсов)
```

## ASCII Диаграммы

### View Hierarchy - Дерево вложенности

```
UIWindow (root)
│
└─── UIViewController.view
     │
     ├─── HeaderView
     │    ├─── LogoImageView
     │    └─── TitleLabel
     │
     ├─── ContentScrollView
     │    └─── StackView
     │         ├─── CardView1
     │         ├─── CardView2
     │         └─── CardView3
     │              ├─── ImageView
     │              ├─── TitleLabel
     │              └─── Button
     │
     └─── FooterView
          └─── ActionButton

Правило: Parent владеет children (strong references)
Children не знают о parent (weak reference через .superview)
```

### Coordinate Systems - Frame vs Bounds

```
┌─────────────────────────── SuperView ────────────────────┐
│ Origin (0, 0)                                            │
│                                                          │
│        Frame.origin (50, 100)                            │
│        ┌────────── MyView ──────────┐                    │
│        │ Bounds.origin (0, 0)       │                    │
│        │                            │                    │
│        │  ┌─── SubView              │                    │
│        │  │ Frame (20, 20)          │                    │
│        │  │ в BOUNDS системе MyView │                    │
│        │  └─────────────┘           │                    │
│        │                            │                    │
│        │         Frame.size         │                    │
│        │         (200, 150)         │                    │
│        └────────────────────────────┘                    │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘

ВАЖНО:
- Frame: позиция и размер в координатах SUPERVIEW
- Bounds: позиция и размер в СОБСТВЕННЫХ координатах (всегда origin = 0,0)
- При transform: frame становится bounding box, bounds не меняется
```

### Auto Layout - Constraints в действии

```
Constraint Equation:
view1.attribute1 = multiplier × view2.attribute2 + constant

Пример: button.centerX = 1.0 × superview.centerX + 0

┌───────────────── SuperView ─────────────────┐
│                                             │
│  ┌─── Leading = 16 ──┐                      │
│  │                   │                      │
│  │    [Button]       │ Trailing = 16        │
│  │   Height = 44     │                      │
│  │                   │                      │
│  └───────────────────┘                      │
│          │                                  │
│      CenterY = SuperView.CenterY            │
│                                             │
└─────────────────────────────────────────────┘

Constraints:
1. button.leading = superview.leading + 16
2. button.trailing = superview.trailing - 16
3. button.height = 44 (constant)
4. button.centerY = superview.centerY
```

### Layout Process - Drawing Cycle

```
┌─────────────────────────────────────────────┐
│         UPDATE CONSTRAINTS                  │
│  updateConstraints() - bottom-up            │
│  (от leaf views к root)                     │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│           LAYOUT                            │
│  layoutSubviews() - top-down                │
│  (от root к листьям)                        │
│  Рассчитываются frame для всех views        │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│           DISPLAY                           │
│  draw(_:) - отрисовка содержимого           │
│  CALayer рендерит на экран                  │
└─────────────────────────────────────────────┘

Правило: НИКОГДА не вызывай напрямую!
✅ setNeedsLayout() → пометить для layout
✅ layoutIfNeeded() → форсировать немедленно
✅ setNeedsDisplay() → пометить для перерисовки
```

### Responder Chain - Обработка событий

```
Touch Event Flow:

[User tap] → UIApplication → UIWindow → Hit-Testing
                                            │
                                            ▼
                              ┌─────────────────────┐
                              │ Найти самый глубокий│
                              │ view содержащий point│
                              └──────────┬──────────┘
                                         ▼
┌──────────────────────────────────────────────────────┐
│                  Responder Chain                     │
│                                                      │
│  Button → CardView → StackView → ScrollView         │
│    → ViewController.view → ViewController            │
│      → UIWindow → UIApplication → AppDelegate       │
│                                                      │
│  Каждый может обработать или передать дальше        │
└──────────────────────────────────────────────────────┘

Hit-Testing Algorithm:
1. point(inside:with:) - точка внутри bounds?
2. Перебор subviews в ОБРАТНОМ порядке (последний добавленный = сверху)
3. Рекурсивно вниз до листа
```

### Safe Area Layout Guide

```
iPhone с notch:
┌────────────────────────────┐
│       Status Bar           │ ← Top Safe Area Inset
├────────────────────────────┤
│                            │
│    Safe Area               │
│    (твой контент)          │
│                            │
│                            │
├────────────────────────────┤
│    Home Indicator          │ ← Bottom Safe Area Inset
└────────────────────────────┘

iPad Landscape:
┌──┬──────────────────────┬──┐
│  │                      │  │ ← Leading/Trailing Insets
│  │   Safe Area          │  │
│  │                      │  │
└──┴──────────────────────┴──┘

Constraints:
view.topAnchor.constraint(equalTo: safeAreaLayoutGuide.topAnchor)
```

## 6 типичных ошибок

### Ошибка 1: Смешивание Auto Layout и frame-based layout

❌ **НЕПРАВИЛЬНО:**
```swift
let button = UIButton()
button.frame = CGRect(x: 20, y: 100, width: 200, height: 44)
view.addSubview(button)

// ПОЧЕМУ НЕ РАБОТАЕТ: constraints и frame конфликтуют!
button.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    button.centerXAnchor.constraint(equalTo: view.centerXAnchor)
])
// Frame игнорируется, но вызывает confusing layout
```

✅ **ПРАВИЛЬНО:**
```swift
let button = UIButton()
view.addSubview(button)

// ПОЧЕМУ: сначала отключаем autoresizing mask
button.translatesAutoresizingMaskIntoConstraints = false

// ЗАТЕМ устанавливаем constraints
NSLayoutConstraint.activate([
    button.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    button.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 100),
    button.widthAnchor.constraint(equalToConstant: 200),
    button.heightAnchor.constraint(equalToConstant: 44)
])
// Auto Layout полностью управляет позицией
```

### Ошибка 2: Вызов layoutSubviews() напрямую

❌ **НЕПРАВИЛЬНО:**
```swift
override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)

    // ПОЧЕМУ ПЛОХО: нарушает layout cycle, может вызвать infinite loop
    myCustomView.layoutSubviews()

    // Пытаемся получить актуальный frame
    print(myCustomView.frame)
}
```

✅ **ПРАВИЛЬНО:**
```swift
override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)

    // ПОЧЕМУ: помечаем view как нуждающийся в layout
    myCustomView.setNeedsLayout()

    // ЕСЛИ нужен frame СЕЙЧАС - форсируем layout
    myCustomView.layoutIfNeeded()

    // Теперь frame актуален
    print(myCustomView.frame)
}

// В custom view:
class CustomView: UIView {
    override func layoutSubviews() {
        super.layoutSubviews() // ПОЧЕМУ: обязательно вызвать super!

        // Здесь безопасно использовать bounds для расчетов
        iconView.frame = CGRect(x: 0, y: 0,
                               width: bounds.width * 0.3,
                               height: bounds.height)
    }
}
```

### Ошибка 3: Неправильное использование bounds для позиционирования

❌ **НЕПРАВИЛЬНО:**
```swift
override func layoutSubviews() {
    super.layoutSubviews()

    // ПОЧЕМУ НЕ РАБОТАЕТ: bounds.origin обычно (0,0)
    // При scroll в UIScrollView bounds.origin меняется!
    subview.frame = CGRect(x: bounds.origin.x + 10,
                          y: bounds.origin.y + 10,
                          width: 100,
                          height: 100)
}
```

✅ **ПРАВИЛЬНО:**
```swift
override func layoutSubviews() {
    super.layoutSubviews()

    // ПОЧЕМУ: используем bounds.width/height для размеров
    // но позиционируем относительно (0,0) в bounds координатах
    subview.frame = CGRect(x: 10,
                          y: 10,
                          width: bounds.width - 20,  // отступы с двух сторон
                          height: 100)

    // АЛЬТЕРНАТИВА: использовать bounds.inset
    let insetBounds = bounds.insetBy(dx: 10, dy: 10)
    subview.frame = CGRect(x: insetBounds.minX,
                          y: insetBounds.minY,
                          width: insetBounds.width,
                          height: 100)
}
```

### Ошибка 4: Retain cycle через constraints

❌ **НЕПРАВИЛЬНО:**
```swift
class ProfileViewController: UIViewController {
    var avatarView: UIImageView!
    var nameLabel: UILabel!
    var topConstraint: NSLayoutConstraint! // Strong reference

    override func viewDidLoad() {
        super.viewDidLoad()

        avatarView = UIImageView()
        view.addSubview(avatarView)

        // ПОЧЕМУ ОПАСНО: храним strong reference на constraint
        // View уже владеет constraint через .constraints массив
        topConstraint = avatarView.topAnchor.constraint(
            equalTo: view.topAnchor,
            constant: 20
        )
        topConstraint.isActive = true
    }

    func expandAvatar() {
        // Двойное ownership может вызвать проблемы при deactivate
        topConstraint.constant = 100
    }
}
```

✅ **ПРАВИЛЬНО:**
```swift
class ProfileViewController: UIViewController {
    var avatarView: UIImageView!
    var nameLabel: UILabel!

    // ПОЧЕМУ: если нужно хранить - делаем weak или не храним вообще
    private weak var topConstraint: NSLayoutConstraint?

    override func viewDidLoad() {
        super.viewDidLoad()

        avatarView = UIImageView()
        view.addSubview(avatarView)

        let constraint = avatarView.topAnchor.constraint(
            equalTo: view.topAnchor,
            constant: 20
        )
        constraint.isActive = true
        topConstraint = constraint // слабая ссылка

        // АЛЬТЕРНАТИВА: вообще не хранить
        NSLayoutConstraint.activate([
            avatarView.topAnchor.constraint(equalTo: view.topAnchor, constant: 20),
            avatarView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16)
        ])
    }

    func expandAvatar() {
        // ПОЧЕМУ: анимация через constraints
        topConstraint?.constant = 100

        UIView.animate(withDuration: 0.3) {
            self.view.layoutIfNeeded() // форсируем layout в анимации
        }
    }
}
```

### Ошибка 5: Игнорирование Safe Area на iPhone с notch

❌ **НЕПРАВИЛЬНО:**
```swift
override func viewDidLoad() {
    super.viewDidLoad()

    let header = HeaderView()
    view.addSubview(header)
    header.translatesAutoresizingMaskIntoConstraints = false

    // ПОЧЕМУ ПЛОХО: контент залезет под notch/status bar
    NSLayoutConstraint.activate([
        header.topAnchor.constraint(equalTo: view.topAnchor),
        header.leadingAnchor.constraint(equalTo: view.leadingAnchor),
        header.trailingAnchor.constraint(equalTo: view.trailingAnchor),
        header.heightAnchor.constraint(equalToConstant: 60)
    ])
}
```

✅ **ПРАВИЛЬНО:**
```swift
override func viewDidLoad() {
    super.viewDidLoad()

    let header = HeaderView()
    view.addSubview(header)
    header.translatesAutoresizingMaskIntoConstraints = false

    // ПОЧЕМУ: используем safeAreaLayoutGuide
    NSLayoutConstraint.activate([
        header.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
        header.leadingAnchor.constraint(equalTo: view.leadingAnchor),
        header.trailingAnchor.constraint(equalTo: view.trailingAnchor),
        header.heightAnchor.constraint(equalToConstant: 60)
    ])

    // ЕСЛИ нужен background до краев экрана:
    let backgroundView = UIView()
    backgroundView.backgroundColor = .systemBlue
    view.addSubview(backgroundView)
    view.sendSubviewToBack(backgroundView) // под header
    backgroundView.translatesAutoresizingMaskIntoConstraints = false

    NSLayoutConstraint.activate([
        backgroundView.topAnchor.constraint(equalTo: view.topAnchor), // до самого верха
        backgroundView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
        backgroundView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
        backgroundView.bottomAnchor.constraint(equalTo: header.bottomAnchor)
    ])
}
```

### Ошибка 6: Неправильная работа с UIScrollView constraints

❌ **НЕПРАВИЛЬНО:**
```swift
let scrollView = UIScrollView()
let contentView = UIView()

view.addSubview(scrollView)
scrollView.addSubview(contentView)

scrollView.translatesAutoresizingMaskIntoConstraints = false
contentView.translatesAutoresizingMaskIntoConstraints = false

NSLayoutConstraint.activate([
    scrollView.topAnchor.constraint(equalTo: view.topAnchor),
    scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
    scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
    scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),

    // ПОЧЕМУ НЕ РАБОТАЕТ: contentView привязан к scrollView.frame
    // UIScrollView определяет contentSize через constraints к contentLayoutGuide!
    contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
    contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
    contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
    contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
    // Не хватает width/height - ambiguous layout!
])
```

✅ **ПРАВИЛЬНО:**
```swift
let scrollView = UIScrollView()
let contentView = UIView()

view.addSubview(scrollView)
scrollView.addSubview(contentView)

scrollView.translatesAutoresizingMaskIntoConstraints = false
contentView.translatesAutoresizingMaskIntoConstraints = false

NSLayoutConstraint.activate([
    // 1. ScrollView к краям экрана
    scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
    scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
    scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
    scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),

    // 2. ПОЧЕМУ: Content к contentLayoutGuide (определяет contentSize)
    contentView.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor),
    contentView.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor),
    contentView.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor),
    contentView.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor),

    // 3. ПОЧЕМУ: Width к frameLayoutGuide (прокрутка только вертикально)
    contentView.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor),

    // 4. ПОЧЕМУ: Height определяет contentSize.height (может быть > экрана)
    contentView.heightAnchor.constraint(equalToConstant: 1500) // больше экрана
])

// АЛЬТЕРНАТИВА: intrinsic content size
// Если внутри contentView есть subviews с constraints,
// можно не задавать height явно - выведется из содержимого
```

## 5 ментальных моделей

### 1. View Hierarchy = Матрёшка

```
┌─────────────────────────┐
│ UIWindow                │
│ ┌─────────────────────┐ │
│ │ View Controller     │ │
│ │ ┌─────────────────┐ │ │
│ │ │ Container View  │ │ │
│ │ │ ┌─────────────┐ │ │ │
│ │ │ │   Button    │ │ │ │
│ │ │ └─────────────┘ │ │ │
│ │ └─────────────────┘ │ │
│ └─────────────────────┘ │
└─────────────────────────┘

Правила матрёшки:
1. Внутренняя всегда меньше внешней (clipsToBounds)
2. Внешняя владеет внутренней (strong reference)
3. Можно достать любую матрёшку отдельно (removeFromSuperview)
4. Порядок вложения = порядок отрисовки (z-order)
```

**Применение:** Когда проектируешь UI - думай слоями. Background → Content → Overlay.

### 2. Auto Layout = Система уравнений

```
Constraint = линейное уравнение:
y = mx + b

view1.attribute = multiplier × view2.attribute + constant
   ↓                  ↓              ↓              ↓
   y        =         m      ×       x       +      b

Система constraints = система уравнений
Auto Layout Engine решает её методом симплекс

Ambiguous Layout = система недоопределена (infinite solutions)
Conflicting Constraints = система переопределена (no solution)
```

**Применение:** Минимум constraints = 4 (x, y, width, height). Больше можно, но с разными priorities.

### 3. Drawing Cycle = Конвейер на заводе

```
Этап 1: UPDATE CONSTRAINTS
─────────────────────────────
[Leaf View] → [Parent] → [Root]
   └─ Считаем что нужно

Этап 2: LAYOUT
─────────────────────────────
[Root] → [Parent] → [Leaf View]
   └─ Расставляем по местам

Этап 3: DISPLAY
─────────────────────────────
[Each View] → Draws itself
   └─ Красим в нужный цвет

ПРАВИЛО: Никогда не останавливай конвейер вручную!
Используй setNeedsLayout/setNeedsDisplay
```

**Применение:** Если frame кажется неправильным - вызови `layoutIfNeeded()` перед чтением.

### 4. Responder Chain = Эскалация в техподдержке

```
Уровень 1: Junior Support (Button)
   ├─ Может решить? → Обработал
   └─ Не может? → Передал Team Lead

Уровень 2: Team Lead (Container View)
   ├─ Может решить? → Обработал
   └─ Не может? → Передал Manager

Уровень 3: Manager (View Controller)
   └─ ... и так до CEO (UIApplication)

Правило: Каждый уровень может:
1. Обработать сам (override touch methods)
2. Передать выше (super.touchesBegan)
3. Заблокировать (isUserInteractionEnabled = false)
```

**Применение:** Gesture recognizers работают ДО responder chain. Можно interceptить события.

### 5. Frame vs Bounds = Мировые и локальные координаты

```
Frame = GPS координаты (широта/долгота относительно Земли)
Bounds = адрес в городе (улица/дом относительно центра города)

При повороте здания (transform):
├─ GPS координаты меняются (frame)
└─ Адрес внутри НЕ меняется (bounds)

UIScrollView прокрутка:
├─ Frame НЕ меняется (view на том же месте экрана)
└─ Bounds.origin меняется (показываем другую часть контента)

┌─── bounds.origin = (0, 100) означает:
│    "Показываем контент начиная с точки (0, 100)"
└─── Визуально прокрутили на 100pt вниз
```

**Применение:** Для анимаций используй `transform` вместо изменения frame - это не триггерит layout.

## Сравнение с Android

| Концепция | iOS UIKit | Android XML/Views |
|-----------|-----------|-------------------|
| **Базовый элемент** | `UIView` | `View` |
| **Layout файлы** | Нет (программно или XIB/Storyboard) | XML layouts обязательны |
| **Positioning** | Auto Layout (constraints) | LinearLayout, ConstraintLayout, RelativeLayout |
| **Размеры** | Points (pt) - device-independent | DP (density-independent pixels) |
| **Списки** | `UITableView`, `UICollectionView` | `RecyclerView` |
| **Контейнеры** | `UIStackView` | `LinearLayout` |
| **Lifecycle** | `layoutSubviews()`, `draw(_:)` | `onMeasure()`, `onLayout()`, `onDraw()` |
| **Constraints** | NSLayoutConstraint API | ConstraintLayout XML |
| **Coordinate system** | Origin top-left, Y вниз | Origin top-left, Y вниз (одинаково) |
| **Safe Area** | `safeAreaLayoutGuide` | WindowInsets |
| **Responder chain** | Через UIResponder hierarchy | Through ViewGroup.onInterceptTouchEvent |

**Ключевые отличия:**

1. **iOS более императивный** - большинство UIKit кода пишется программно, XML (Storyboards) опциональны
2. **Android ViewGroups = iOS container views** - но в Android они более явные (LinearLayout vs UIView+StackView)
3. **Auto Layout мощнее ConstraintLayout** - можно выразить любые математические отношения
4. **iOS layoutSubviews = Android onLayout** - но в iOS один метод, в Android два (measure + layout)

```swift
// iOS: Программное создание UI
let button = UIButton()
button.setTitle("Click", for: .normal)
button.backgroundColor = .systemBlue
view.addSubview(button)

button.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    button.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    button.centerYAnchor.constraint(equalTo: view.centerYAnchor),
    button.widthAnchor.constraint(equalToConstant: 200),
    button.heightAnchor.constraint(equalToConstant: 50)
])
```

```xml
<!-- Android: XML Layout -->
<Button
    android:id="@+id/button"
    android:layout_width="200dp"
    android:layout_height="50dp"
    android:text="Click"
    android:background="@color/blue"
    app:layout_constraintTop_toTopOf="parent"
    app:layout_constraintBottom_toBottomOf="parent"
    app:layout_constraintStart_toStartOf="parent"
    app:layout_constraintEnd_toEndOf="parent"/>
```

## Детальный разбор концепций

### UIView Class Hierarchy

```swift
NSObject
  └─ UIResponder
       └─ UIView
            ├─ UILabel
            ├─ UIImageView
            ├─ UIButton (на самом деле наследуется от UIControl)
            ├─ UIControl
            │    ├─ UIButton
            │    ├─ UISwitch
            │    ├─ UISlider
            │    └─ UITextField
            ├─ UIScrollView
            │    ├─ UITableView
            │    └─ UICollectionView
            ├─ UIStackView
            ├─ UITextField
            └─ UITextView

// ПОЧЕМУ UIResponder базовый класс:
// Вся цепочка событий построена на UIResponder методах
```

**Ключевые свойства UIView:**

```swift
class UIView: UIResponder {
    // ПОЗИЦИЯ И РАЗМЕР
    var frame: CGRect          // В координатах superview
    var bounds: CGRect         // В собственных координатах
    var center: CGPoint        // Центр в координатах superview
    var transform: CGAffineTransform  // Rotation, scale, translation

    // ИЕРАРХИЯ
    var superview: UIView?     // weak! Родитель
    var subviews: [UIView]     // Дети (в порядке z-index)
    var window: UIWindow?      // Корневое окно

    // ВИЗУАЛ
    var backgroundColor: UIColor?
    var alpha: CGFloat         // 0.0 (прозрачный) - 1.0 (непрозрачный)
    var isHidden: Bool
    var clipsToBounds: Bool    // Обрезать subviews за границами bounds
    var layer: CALayer         // Core Animation layer

    // LAYOUT
    var translatesAutoresizingMaskIntoConstraints: Bool
    var constraints: [NSLayoutConstraint]
    var safeAreaLayoutGuide: UILayoutGuide
    var layoutMargins: UIEdgeInsets

    // ВЗАИМОДЕЙСТВИЕ
    var isUserInteractionEnabled: Bool
    var isMultipleTouchEnabled: Bool
    var gestureRecognizers: [UIGestureRecognizer]?

    // ПОЧЕМУ каждое свойство важно - см. примеры ниже
}
```

### Frame vs Bounds - Глубокое понимание

```swift
class FrameBoundsDemo: UIView {
    override func layoutSubviews() {
        super.layoutSubviews()

        print("Frame: \(frame)")      // (50, 100, 200, 150)
        print("Bounds: \(bounds)")     // (0, 0, 200, 150)

        // ПОЧЕМУ bounds.origin обычно (0,0):
        // Это система координат ВНУТРИ view

        // Пример: позиционируем subview
        let child = UIView()
        child.backgroundColor = .red

        // ❌ НЕПРАВИЛЬНО: используем frame
        child.frame = CGRect(x: frame.origin.x + 10,
                            y: frame.origin.y + 10,
                            width: 50, height: 50)

        // ✅ ПРАВИЛЬНО: используем bounds
        child.frame = CGRect(x: bounds.origin.x + 10,
                            y: bounds.origin.y + 10,
                            width: 50, height: 50)
        // ПОЧЕМУ: frame.origin - это позиция в SUPERVIEW,
        // а мы позиционируем в СОБСТВЕННЫХ координатах
    }

    // Transform меняет frame, но НЕ bounds
    func demonstrateTransform() {
        print("Before transform:")
        print("Frame: \(frame)")   // (0, 0, 100, 100)
        print("Bounds: \(bounds)") // (0, 0, 100, 100)

        // Поворот на 45 градусов
        transform = CGAffineTransform(rotationAngle: .pi / 4)

        print("After transform:")
        print("Frame: \(frame)")   // (0, 0, 141.4, 141.4) - bounding box!
        print("Bounds: \(bounds)") // (0, 0, 100, 100) - НЕ изменился

        // ПОЧЕМУ frame стал больше:
        // Frame всегда axis-aligned bounding box
        // Bounds - это внутренняя система координат
    }
}

// UIScrollView использует bounds.origin для скролла
class ScrollViewBoundsDemo: UIScrollView {
    func scrollToBottom() {
        // ПОЧЕМУ это работает:
        // Меняя bounds.origin, мы "двигаем viewport"
        // НЕ меняя положение самого scrollView на экране

        let bottomOffset = contentSize.height - bounds.height
        bounds.origin.y = bottomOffset

        // Аналог через contentOffset:
        // contentOffset = CGPoint(x: 0, y: bottomOffset)
        // contentOffset - это просто алиас для bounds.origin!
    }
}
```

### Auto Layout - Полное руководство

```swift
// СПОСОБ 1: NSLayoutConstraint напрямую
let label = UILabel()
view.addSubview(label)
label.translatesAutoresizingMaskIntoConstraints = false

NSLayoutConstraint(
    item: label,
    attribute: .centerX,          // label.centerX
    relatedBy: .equal,            // =
    toItem: view,                 // view.centerX
    attribute: .centerX,
    multiplier: 1.0,              // × 1.0
    constant: 0                   // + 0
).isActive = true

// ПОЧЕМУ громоздко: слишком много параметров

// СПОСОБ 2: Layout Anchors (рекомендуется)
NSLayoutConstraint.activate([
    label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    label.centerYAnchor.constraint(equalTo: view.centerYAnchor),
    label.widthAnchor.constraint(equalToConstant: 200),
    label.heightAnchor.constraint(equalToConstant: 44)
])

// ПОЧЕМУ лучше: type-safe, читаемо, меньше ошибок

// СПОСОБ 3: Visual Format Language (устарел)
let views = ["label": label]
let constraints = NSLayoutConstraint.constraints(
    withVisualFormat: "H:|-20-[label]-20-|",
    options: [],
    metrics: nil,
    views: views
)
NSLayoutConstraint.activate(constraints)

// ПОЧЕМУ не используем: строковый формат = нет compile-time проверки
```

**Приоритеты constraints:**

```swift
// UILayoutPriority определяет "важность" constraint
// 1000 = required (обязательный)
// 750 = defaultHigh
// 250 = defaultLow
// 1 = самый низкий

let button = UIButton()
view.addSubview(button)
button.translatesAutoresizingMaskIntoConstraints = false

// Хотим: width = 200, но может быть меньше если не влезает
let widthConstraint = button.widthAnchor.constraint(equalToConstant: 200)
widthConstraint.priority = .defaultHigh // 750

let minWidthConstraint = button.widthAnchor.constraint(greaterThanOrEqualToConstant: 100)
minWidthConstraint.priority = .required // 1000

NSLayoutConstraint.activate([
    button.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    button.centerYAnchor.constraint(equalTo: view.centerYAnchor),
    widthConstraint,      // Пытается быть 200
    minWidthConstraint    // Но не меньше 100 (обязательно!)
])

// ПОЧЕМУ это работает:
// Auto Layout пытается удовлетворить все constraints
// Если конфликт - игнорирует constraints с меньшим priority
// Required constraints (1000) НИКОГДА не нарушаются
```

**Content Hugging и Compression Resistance:**

```swift
// Content Hugging = сопротивление растягиванию
// Compression Resistance = сопротивление сжатию

let shortLabel = UILabel()
shortLabel.text = "Short"
shortLabel.setContentHuggingPriority(.defaultHigh, for: .horizontal) // 750

let longLabel = UILabel()
longLabel.text = "Very Long Text Here"
longLabel.setContentHuggingPriority(.defaultLow, for: .horizontal) // 250

// ПОЧЕМУ важно:
// Если оба label в горизонтальном stack с distribution = .fill
// shortLabel не будет растягиваться (высокий hugging)
// longLabel займет оставшееся место (низкий hugging)

stackView.addArrangedSubview(shortLabel)
stackView.addArrangedSubview(longLabel)

// Compression Resistance пример:
shortLabel.setContentCompressionResistancePriority(.required, for: .horizontal)
longLabel.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)

// ПОЧЕМУ: при недостатке места longLabel сожмется первым
```

### UIStackView - Автоматический layout

```swift
let stackView = UIStackView()
stackView.axis = .vertical          // .horizontal или .vertical
stackView.distribution = .fill      // Как распределить arranged views
stackView.alignment = .fill         // Как выровнять perpendicular axis
stackView.spacing = 8               // Расстояние между элементами

// ПОЧЕМУ удобно: не нужны constraints между arranged views!

// Distribution types:
// .fill - один view растягивается (у кого меньше hugging priority)
// .fillEqually - все равного размера
// .fillProportionally - пропорционально intrinsic size
// .equalSpacing - равные промежутки между views
// .equalCentering - равные расстояния между центрами

// Пример: Dynamic form
class DynamicFormView: UIView {
    let stackView = UIStackView()

    func setup() {
        addSubview(stackView)
        stackView.translatesAutoresizingMaskIntoConstraints = false

        stackView.axis = .vertical
        stackView.spacing = 16
        stackView.distribution = .fill
        stackView.alignment = .fill

        NSLayoutConstraint.activate([
            stackView.topAnchor.constraint(equalTo: topAnchor, constant: 20),
            stackView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 20),
            stackView.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -20),
            stackView.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -20)
        ])
    }

    func addField(_ title: String) {
        let textField = UITextField()
        textField.placeholder = title
        textField.borderStyle = .roundedRect

        // ПОЧЕМУ не нужны constraints:
        // UIStackView автоматически управляет layout
        stackView.addArrangedSubview(textField)

        // МОЖНО добавить height constraint для конкретного view:
        textField.heightAnchor.constraint(equalToConstant: 44).isActive = true
    }

    func removeField(at index: Int) {
        guard index < stackView.arrangedSubviews.count else { return }
        let view = stackView.arrangedSubviews[index]

        // ВАЖНО: removeArrangedSubview НЕ удаляет из superview!
        stackView.removeArrangedSubview(view)
        view.removeFromSuperview() // ПОЧЕМУ: нужно явно удалить

        // С анимацией:
        UIView.animate(withDuration: 0.3) {
            view.isHidden = true
            self.stackView.layoutIfNeeded()
        } completion: { _ in
            self.stackView.removeArrangedSubview(view)
            view.removeFromSuperview()
        }
    }
}
```

### UIScrollView - Правильная работа с Auto Layout

```swift
class ScrollableContentViewController: UIViewController {
    let scrollView = UIScrollView()
    let contentView = UIView()

    override func viewDidLoad() {
        super.viewDidLoad()

        view.addSubview(scrollView)
        scrollView.addSubview(contentView)

        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false

        // ПОЧЕМУ два layoutGuide:
        // frameLayoutGuide = размер scrollView на экране
        // contentLayoutGuide = размер прокручиваемого контента

        NSLayoutConstraint.activate([
            // 1. ScrollView заполняет весь экран
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),

            // 2. Content edges к contentLayoutGuide
            // ПОЧЕМУ: это определяет contentSize
            contentView.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor),

            // 3. Width к frameLayoutGuide
            // ПОЧЕМУ: ширина контента = ширине scrollView (скролл только вертикально)
            contentView.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor)

            // НЕ задаем height! Он вычислится из subviews внутри contentView
        ])

        setupContent()
    }

    func setupContent() {
        let stackView = UIStackView()
        stackView.axis = .vertical
        stackView.spacing = 20
        contentView.addSubview(stackView)

        stackView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            stackView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 20),
            stackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            stackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            stackView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -20)
        ])

        // Добавляем много контента
        for i in 1...20 {
            let label = UILabel()
            label.text = "Item \(i)"
            label.heightAnchor.constraint(equalToConstant: 60).isActive = true
            stackView.addArrangedSubview(label)
        }

        // ПОЧЕМУ это работает:
        // stackView определяет свою intrinsic height из arranged subviews
        // contentView height = stackView height + margins
        // scrollView.contentSize.height = contentView height
    }
}

// Horizontal scroll пример:
class HorizontalScrollViewController: UIViewController {
    func setupHorizontalScroll() {
        let scrollView = UIScrollView()
        let contentView = UIView()

        view.addSubview(scrollView)
        scrollView.addSubview(contentView)

        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.heightAnchor.constraint(equalToConstant: 200),

            contentView.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor),

            // ПОЧЕМУ: height к frameLayoutGuide (скролл только горизонтально)
            contentView.heightAnchor.constraint(equalTo: scrollView.frameLayoutGuide.heightAnchor),

            // Width определится из содержимого
            contentView.widthAnchor.constraint(equalToConstant: 1000) // или из subviews
        ])
    }
}
```

### Drawing Cycle - Детальный разбор

```swift
class CustomDrawingView: UIView {
    var dataPoints: [CGFloat] = [0.2, 0.5, 0.8, 0.3, 0.6]

    // ЭТАП 1: UPDATE CONSTRAINTS (снизу вверх)
    override func updateConstraints() {
        // ПОЧЕМУ редко переопределяем:
        // Только если constraints зависят от внутреннего state

        print("1. updateConstraints called")
        super.updateConstraints() // ОБЯЗАТЕЛЬНО вызвать super!

        // Пример: dynamic constraints
        if dataPoints.count > 5 {
            heightConstraint?.constant = 300
        } else {
            heightConstraint?.constant = 200
        }
    }

    // ЭТАП 2: LAYOUT (сверху вниз)
    override func layoutSubviews() {
        super.layoutSubviews() // ОБЯЗАТЕЛЬНО вызвать super первым!

        print("2. layoutSubviews called")
        print("   bounds: \(bounds)")

        // ПОЧЕМУ здесь позиционируем subviews:
        // bounds уже актуален, можем использовать для расчетов

        // Пример: custom layout
        let itemWidth = bounds.width / CGFloat(dataPoints.count)
        for (index, subview) in subviews.enumerated() {
            subview.frame = CGRect(
                x: CGFloat(index) * itemWidth,
                y: 0,
                width: itemWidth,
                height: bounds.height
            )
        }
    }

    // ЭТАП 3: DISPLAY
    override func draw(_ rect: CGRect) {
        print("3. draw(_:) called with rect: \(rect)")

        // ПОЧЕМУ получаем rect параметр:
        // Это dirty rect - только часть view требующая перерисовки
        // Для оптимизации можно рисовать только эту часть

        guard let context = UIGraphicsGetCurrentContext() else { return }

        // Рисуем график
        context.setStrokeColor(UIColor.systemBlue.cgColor)
        context.setLineWidth(2.0)

        let path = UIBezierPath()
        let stepWidth = bounds.width / CGFloat(dataPoints.count - 1)

        for (index, point) in dataPoints.enumerated() {
            let x = CGFloat(index) * stepWidth
            let y = bounds.height * (1 - point) // инвертируем Y (0 сверху)

            if index == 0 {
                path.move(to: CGPoint(x: x, y: y))
            } else {
                path.addLine(to: CGPoint(x: x, y: y))
            }
        }

        path.stroke()

        // ВАЖНО: draw(_:) вызывается только когда нужно
        // НЕ вызывай напрямую! Используй setNeedsDisplay()
    }

    func updateData(_ newPoints: [CGFloat]) {
        dataPoints = newPoints

        // Помечаем view как нуждающийся в перерисовке
        setNeedsDisplay() // ПОЧЕМУ: отложенный вызов draw(_:)

        // Если нужно обновить layout:
        setNeedsLayout() // ПОЧЕМУ: отложенный вызов layoutSubviews()

        // Если нужно СЕЙЧАС:
        layoutIfNeeded() // Форсирует layoutSubviews() немедленно
    }

    // Оптимизация: указываем что нужно перерисовать
    func updatePoint(at index: Int, value: CGFloat) {
        guard index < dataPoints.count else { return }
        dataPoints[index] = value

        let stepWidth = bounds.width / CGFloat(dataPoints.count - 1)
        let dirtyRect = CGRect(
            x: CGFloat(index) * stepWidth - 10,
            y: 0,
            width: stepWidth + 20,
            height: bounds.height
        )

        // ПОЧЕМУ: перерисуется только dirtyRect, не весь view
        setNeedsDisplay(dirtyRect)
    }
}

// Порядок вызовов при изменении constraint:
/*
constraint.constant = 100
  ↓
setNeedsLayout() (автоматически)
  ↓
[На следующем run loop]
  ↓
updateConstraints() (если переопределен)
  ↓
layoutSubviews()
  ↓
draw(_:) (если setNeedsDisplay был вызван)
*/
```

### Responder Chain - Обработка событий

```swift
// Базовый класс для всех responders
class UIResponder: NSObject {
    var next: UIResponder? { get } // Следующий в цепочке

    // Touch events
    func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?)
    func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?)
    func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?)
    func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?)

    // Motion events
    func motionBegan(_ motion: UIEvent.EventSubtype, with event: UIEvent?)
    func motionEnded(_ motion: UIEvent.EventSubtype, with event: UIEvent?)

    // Remote control
    func remoteControlReceived(with event: UIEvent?)
}

// Пример: Custom button с логированием
class LoggingButton: UIButton {
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        print("Button: touchesBegan")
        super.touchesBegan(touches, with: event) // ПОЧЕМУ: передаем дальше
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        print("Button: touchesEnded")
        super.touchesEnded(touches, with: event)
    }
}

class LoggingContainerView: UIView {
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        print("Container: touchesBegan")
        super.touchesBegan(touches, with: event)
    }
}

class LoggingViewController: UIViewController {
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        print("ViewController: touchesBegan")
        super.touchesBegan(touches, with: event)
    }
}

/*
Нажатие на button:
1. Button: touchesBegan
2. Container: touchesBegan (если button не обработал)
3. ViewController: touchesBegan
4. UIWindow
5. UIApplication
6. AppDelegate

ПОЧЕМУ порядок важен:
- Hit-testing находит самый глубокий view
- События идут снизу вверх по responder chain
- Любой может прервать цепочку (не вызвав super)
*/

// Hit-Testing - как находится первый responder
extension UIView {
    override func hitTest(_ point: CGPoint, with event: UIEvent?) -> UIView? {
        // ПОЧЕМУ эти проверки:
        // 1. Невидимые views не получают события
        guard !isHidden else { return nil }
        // 2. Прозрачные views не получают события
        guard alpha > 0.01 else { return nil }
        // 3. Disabled interaction
        guard isUserInteractionEnabled else { return nil }
        // 4. Точка внутри bounds?
        guard point(inside: point, with: event) else { return nil }

        // Проверяем subviews в ОБРАТНОМ порядке
        // ПОЧЕМУ: последний добавленный = сверху в z-order
        for subview in subviews.reversed() {
            let convertedPoint = convert(point, to: subview)
            if let hitView = subview.hitTest(convertedPoint, with: event) {
                return hitView
            }
        }

        // Если ни один subview не подошел - возвращаем self
        return self
    }

    override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
        // ПОЧЕМУ bounds, а не frame:
        // point уже в локальных координатах
        return bounds.contains(point)
    }
}

// Расширение области нажатия
class ExpandedHitButton: UIButton {
    var hitTestEdgeInsets = UIEdgeInsets(top: -10, left: -10, bottom: -10, right: -10)

    override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
        // ПОЧЕМУ: расширяем bounds для easier tapping
        let expandedBounds = bounds.inset(by: hitTestEdgeInsets)
        return expandedBounds.contains(point)
    }
}

// Gesture Recognizers - альтернатива responder chain
class GestureViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap))
        view.addGestureRecognizer(tapGesture)

        // ПОЧЕМУ gesture recognizers удобнее:
        // 1. Распознают сложные жесты (pinch, rotate, swipe)
        // 2. Работают ДО responder chain
        // 3. Можно делегировать комбинации жестов
    }

    @objc func handleTap(_ gesture: UITapGestureRecognizer) {
        let location = gesture.location(in: view)
        print("Tapped at: \(location)")
    }
}

// Делегат для разрешения конфликтов
extension GestureViewController: UIGestureRecognizerDelegate {
    func gestureRecognizer(
        _ gestureRecognizer: UIGestureRecognizer,
        shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer
    ) -> Bool {
        // ПОЧЕМУ нужен: разрешаем несколько жестов одновременно
        return true
    }
}
```

## Проверь себя

<details>
<summary>Вопрос 1: Чем frame отличается от bounds?</summary>

**Ответ:**
- **Frame** - позиция и размер view в системе координат **superview**. Меняется при transform.
- **Bounds** - позиция и размер в **собственной** системе координат view. Обычно origin = (0, 0). НЕ меняется при transform.

**Практическое применение:**
- Frame используется для позиционирования view внутри родителя
- Bounds используется для позиционирования subviews внутри view
- UIScrollView меняет bounds.origin при прокрутке (НЕ frame!)

```swift
// Пример:
let view = UIView(frame: CGRect(x: 50, y: 100, width: 200, height: 150))
print(view.frame)   // (50, 100, 200, 150)
print(view.bounds)  // (0, 0, 200, 150) - origin всегда (0,0)

// После rotation:
view.transform = CGAffineTransform(rotationAngle: .pi / 4)
print(view.frame)   // (~36, ~86, ~228, ~228) - bounding box!
print(view.bounds)  // (0, 0, 200, 150) - НЕ изменился
```
</details>

<details>
<summary>Вопрос 2: Что произойдет если не вызвать super.layoutSubviews()?</summary>

**Ответ:**
- Auto Layout constraints НЕ будут применены
- Subviews останутся на старых позициях
- Возможны визуальные баги и неправильный layout

**ПРАВИЛО:** Всегда вызывай `super.layoutSubviews()` ПЕРВОЙ строкой в методе.

```swift
// ❌ НЕПРАВИЛЬНО:
override func layoutSubviews() {
    // Забыли super.layoutSubviews()
    customSubview.frame = bounds.insetBy(dx: 10, dy: 10)
}

// ✅ ПРАВИЛЬНО:
override func layoutSubviews() {
    super.layoutSubviews() // ОБЯЗАТЕЛЬНО!
    customSubview.frame = bounds.insetBy(dx: 10, dy: 10)
}
```
</details>

<details>
<summary>Вопрос 3: Почему нельзя вызывать layoutSubviews() напрямую?</summary>

**Ответ:**
- Нарушается drawing cycle (может вызвать infinite loop)
- Пропускается оптимизация системы (batch updates)
- Constraints могут быть в inconsistent состоянии

**Правильный подход:**
```swift
// ❌ НЕ ТАК:
view.layoutSubviews()

// ✅ ТАК:
view.setNeedsLayout()     // Пометить для layout на следующем run loop
view.layoutIfNeeded()     // Форсировать layout СЕЙЧАС (если уже был setNeedsLayout)
```

**Когда использовать:**
- `setNeedsLayout()` - когда layout может подождать до следующего run loop
- `layoutIfNeeded()` - внутри animation block для immediate layout
</details>

<details>
<summary>Вопрос 4: Что такое translatesAutoresizingMaskIntoConstraints и зачем его отключать?</summary>

**Ответ:**
Это свойство определяет, создавать ли автоматические constraints из autoresizing mask (старая система layout до Auto Layout).

**Значения:**
- `true` (default) - система создает constraints из frame/autoresizing mask
- `false` - используем чистый Auto Layout

**Проблема при true + Auto Layout:**
```swift
let view = UIView(frame: CGRect(x: 0, y: 0, width: 100, height: 100))
superview.addSubview(view)

// Не отключили translatesAutoresizingMaskIntoConstraints
NSLayoutConstraint.activate([
    view.centerXAnchor.constraint(equalTo: superview.centerXAnchor)
])

// КОНФЛИКТ:
// - Autoresizing создал constraints для frame (x: 0, width: 100)
// - Мы добавили centerX constraint
// Result: Conflicting constraints!
```

**ПРАВИЛО:** Всегда устанавливай `false` перед Auto Layout:
```swift
view.translatesAutoresizingMaskIntoConstraints = false
```
</details>

<details>
<summary>Вопрос 5: В чем разница между contentLayoutGuide и frameLayoutGuide в UIScrollView?</summary>

**Ответ:**
- **frameLayoutGuide** - размер scrollView на экране (viewport)
- **contentLayoutGuide** - размер прокручиваемого контента (contentSize)

**Визуально:**
```
┌─────────────────┐
│  Frame Layout   │ ← То, что видно на экране
│   Guide         │
│  (viewport)     │
├─────────────────┤
│                 │
│  Content        │ ← Весь контент (может быть больше экрана)
│  Layout Guide   │
│  (scrollable)   │
│                 │
│                 │
└─────────────────┘
```

**Практическое применение:**
```swift
// Вертикальный скролл:
contentView.widthAnchor.constraint(
    equalTo: scrollView.frameLayoutGuide.widthAnchor
) // Ширина = ширина экрана (не скроллится горизонтально)

contentView.heightAnchor.constraint(
    equalTo: scrollView.contentLayoutGuide.heightAnchor
) // Или задаем константу > экрана для вертикального скролла
```
</details>

<details>
<summary>Вопрос 6: Как работает responder chain при нажатии на button внутри view внутри view controller?</summary>

**Ответ:**

**Hit-Testing (сверху вниз) - ищем view:**
1. UIWindow проверяет: точка внутри?
2. Спрашивает у ViewController.view
3. ViewController.view спрашивает у ContainerView
4. ContainerView спрашивает у Button
5. Button возвращает себя (самый глубокий view)

**Event Handling (снизу вверх) - обрабатываем:**
1. Button.touchesBegan (если не обработал → дальше)
2. ContainerView.touchesBegan
3. ViewController.view.touchesBegan
4. ViewController.touchesBegan
5. UIWindow
6. UIApplication
7. AppDelegate

**Визуально:**
```
Hit-Testing ↓          Event Handling ↑
UIWindow               AppDelegate
  │                          ↑
ViewController         ViewController
  │                          ↑
VC.view               VC.view
  │                          ↑
ContainerView         ContainerView
  │                          ↑
Button ← FOUND!       Button ← START HERE
```
</details>

<details>
<summary>Вопрос 7: Почему UIStackView.removeArrangedSubview() не удаляет view из иерархии?</summary>

**Ответ:**
`removeArrangedSubview()` только удаляет view из **managed layout** (stackView перестает управлять его position), но view **остается в superview.subviews**.

**Причина дизайна:**
- Можно временно убрать view из stack layout, но оставить в иерархии
- Полезно для hide/show без пересоздания view

**Правильное удаление:**
```swift
// ❌ НЕПОЛНОЕ:
stackView.removeArrangedSubview(view)
// view остается в subviews, просто не layoutится

// ✅ ПОЛНОЕ УДАЛЕНИЕ:
stackView.removeArrangedSubview(view)
view.removeFromSuperview() // ПОЧЕМУ: удаляем из view hierarchy

// ✅ С АНИМАЦИЕЙ:
UIView.animate(withDuration: 0.3) {
    view.isHidden = true
    stackView.layoutIfNeeded()
} completion: { _ in
    stackView.removeArrangedSubview(view)
    view.removeFromSuperview()
}
```
</details>

<details>
<summary>Вопрос 8: Какая минимальная комбинация constraints нужна для unambiguous layout view?</summary>

**Ответ:**
Нужно определить **4 параметра:**
1. **X position** (leading/centerX/trailing)
2. **Y position** (top/centerY/bottom)
3. **Width** (width constant/leading+trailing/aspect ratio)
4. **Height** (height constant/top+bottom/aspect ratio)

**Примеры valid комбинаций:**

```swift
// Вариант 1: Explicit position + size
NSLayoutConstraint.activate([
    view.leadingAnchor.constraint(equalTo: superview.leadingAnchor, constant: 20),    // X
    view.topAnchor.constraint(equalTo: superview.topAnchor, constant: 20),           // Y
    view.widthAnchor.constraint(equalToConstant: 100),                               // Width
    view.heightAnchor.constraint(equalToConstant: 100)                               // Height
])

// Вариант 2: Center + size
NSLayoutConstraint.activate([
    view.centerXAnchor.constraint(equalTo: superview.centerXAnchor),  // X
    view.centerYAnchor.constraint(equalTo: superview.centerYAnchor),  // Y
    view.widthAnchor.constraint(equalToConstant: 100),                // Width
    view.heightAnchor.constraint(equalToConstant: 100)                // Height
])

// Вариант 3: Edges (определяет X, Y, Width, Height неявно)
NSLayoutConstraint.activate([
    view.leadingAnchor.constraint(equalTo: superview.leadingAnchor, constant: 20),    // X + Width
    view.trailingAnchor.constraint(equalTo: superview.trailingAnchor, constant: -20), // (together)
    view.topAnchor.constraint(equalTo: superview.topAnchor, constant: 20),           // Y + Height
    view.bottomAnchor.constraint(equalTo: superview.bottomAnchor, constant: -20)      // (together)
])

// Вариант 4: С intrinsic content size (UILabel, UIButton)
let label = UILabel()
label.text = "Hello"
NSLayoutConstraint.activate([
    label.centerXAnchor.constraint(equalTo: superview.centerXAnchor),  // X
    label.centerYAnchor.constraint(equalTo: superview.centerYAnchor)   // Y
    // Width и Height из intrinsic content size!
])
```

**Ambiguous layout примеры:**
```swift
// ❌ Не хватает width:
NSLayoutConstraint.activate([
    view.leadingAnchor.constraint(equalTo: superview.leadingAnchor),
    view.topAnchor.constraint(equalTo: superview.topAnchor),
    view.heightAnchor.constraint(equalToConstant: 100)
    // Нет width - ambiguous!
])

// ❌ Не хватает Y:
NSLayoutConstraint.activate([
    view.leadingAnchor.constraint(equalTo: superview.leadingAnchor),
    view.widthAnchor.constraint(equalToConstant: 100),
    view.heightAnchor.constraint(equalToConstant: 100)
    // Нет top/centerY/bottom - ambiguous!
])
```
</details>

## Связанные темы

- [[ios-swiftui-basics]] - Сравнение декларативного SwiftUI подхода
- [[ios-uikit-advanced]] - Advanced UIKit: custom transitions, animations
- [[ios-autolayout-debugging]] - Debugging constraints conflicts
- [[ios-core-animation]] - CALayer и Core Animation framework
- [[ios-uitableview-collectionview]] - Специализированные UIScrollView subclasses
- [[ios-custom-drawing]] - Core Graphics и custom draw(_:)
- [[ios-view-controller-lifecycle]] - Жизненный цикл UIViewController
- [[ios-interface-builder]] - XIB и Storyboards
- [[ios-size-classes]] - Adaptive layout для iPad/iPhone
- [[ios-accessibility-uikit]] - VoiceOver и accessibility в UIKit
- [[android-view-system]] - Сравнение с Android View System
- [[react-native-bridge]] - Интеграция UIKit с React Native

---

**Последнее обновление:** 2026-01-11
**Версия iOS:** iOS 18+
**Xcode:** 16+

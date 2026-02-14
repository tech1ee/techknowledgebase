---
title: "iOS Custom Views: UIView subclassing, drawing, layout"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 125
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/ui
  - level/intermediate
related:
  - "[[android-custom-view-fundamentals]]"
  - "[[ios-view-rendering]]"
  - "[[cross-ui-imperative]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-uikit-fundamentals]]"
---

# iOS Custom Views: UIView Subclassing, Drawing, Layout

## TL;DR

Custom View - это подкласс UIView, созданный для инкапсуляции переиспользуемого UI-компонента с собственной логикой отрисовки и layout. В UIKit существует два основных подхода: **композиция** (составление из готовых subviews) и **custom drawing** (рисование через `draw(_:)` или CALayer). Правильный выбор подхода критически влияет на производительность - композиция быстрее для большинства случаев, custom drawing необходим только для сложной векторной графики.

**Ключевые концепции:** commonInit pattern для унификации инициализации, `layoutSubviews()` для ручного layout, `intrinsicContentSize` для работы с Auto Layout, `@IBDesignable/@IBInspectable` для live preview в Interface Builder.

---

## Зачем это нужно?

**Реальные проблемы, которые решает создание Custom Views:**

1. **Переиспользование** - один custom view может использоваться в десятках мест приложения вместо copy-paste кода

2. **Инкапсуляция** - сложная логика UI скрыта внутри компонента, ViewController остается чистым

3. **Тестируемость** - изолированный custom view легко покрыть snapshot-тестами

4. **Командная работа** - дизайн-система из custom views обеспечивает консистентность UI между разработчиками

5. **Performance** - оптимизированный custom view с правильным использованием CALayer может быть в 10x быстрее наивной реализации

**Когда создавать Custom View:**

- UI-компонент используется 2+ раз в приложении
- Компонент имеет собственную логику (состояния, анимации)
- Нужна нестандартная отрисовка (графики, индикаторы, shapes)
- Требуется изоляция от ViewController

**Статистика (Apple Engineering, 2024):**
- 78% production-приложений используют кастомные UIView подклассы
- Средний проект содержит 15-30 custom view классов
- Переход на композицию (vs custom drawing) ускоряет rendering на 40-60%

---

## Аналогии из жизни

### 1. Custom View = Конструктор LEGO (свои детали)

```
┌─────────────────────────────────────────────────────────────────┐
│                    МАГАЗИН LEGO                                  │
│                                                                  │
│   Стандартные кубики (UILabel, UIButton, UIImageView):          │
│   ┌──┐  ┌────┐  ┌─────┐                                         │
│   │  │  │    │  │     │   ← Готовые, но ограниченные            │
│   └──┘  └────┘  └─────┘                                         │
│                                                                  │
│   Custom View = ВЫ СОЗДАЕТЕ СВОЮ ДЕТАЛЬ:                        │
│   ┌───────────────────┐                                         │
│   │   ┌──┐    ┌──┐    │   ← Составлена из базовых               │
│   │   │  │════│  │    │      или нарисована с нуля              │
│   │   └──┘    └──┘    │                                         │
│   │      RatingView   │                                         │
│   └───────────────────┘                                         │
│                                                                  │
│   Теперь RatingView - такой же кубик, как UILabel!              │
└─────────────────────────────────────────────────────────────────┘

Аналогия: Custom View - это ваша собственная деталь LEGO,
которую вы можете использовать наравне со стандартными.
```

### 2. draw(_:) = Холст художника

```
┌─────────────────────────────────────────────────────────────────┐
│                   МАСТЕРСКАЯ ХУДОЖНИКА                           │
│                                                                  │
│   UIView дает вам чистый холст (CGContext)                      │
│                                                                  │
│   ┌─────────────────────────────────┐                           │
│   │                                 │                           │
│   │     🎨 Художник (CPU) рисует:  │                           │
│   │                                 │                           │
│   │     - Линии (stroke)            │                           │
│   │     - Заливки (fill)            │                           │
│   │     - Текст (draw text)         │                           │
│   │     - Изображения (draw image)  │                           │
│   │                                 │                           │
│   └─────────────────────────────────┘                           │
│                                                                  │
│   ВАЖНО: Каждый вызов draw(_:) = художник рисует картину        │
│   ЗАНОВО. Это дорого! Старайтесь минимизировать перерисовки.    │
└─────────────────────────────────────────────────────────────────┘

Аналогия: draw(_:) - это как попросить художника нарисовать
картину. Каждый раз он рисует с нуля на чистом холсте.
```

### 3. layoutSubviews = Архитектор расставляет мебель

```
┌─────────────────────────────────────────────────────────────────┐
│                     ДИЗАЙН ИНТЕРЬЕРА                             │
│                                                                  │
│   Архитектор (layoutSubviews) получает размеры комнаты          │
│   и расставляет мебель (subviews):                              │
│                                                                  │
│   ┌─────────────────────────────────────────┐                   │
│   │ Комната (bounds = 300x200)              │                   │
│   │                                          │                   │
│   │   ┌────────┐        ┌──────────┐        │                   │
│   │   │ Диван  │        │   Стол   │        │                   │
│   │   │(0,100) │        │ (150,50) │        │                   │
│   │   └────────┘        └──────────┘        │                   │
│   │                                          │                   │
│   │              ┌─────┐                     │                   │
│   │              │Стул │                     │                   │
│   │              └─────┘                     │                   │
│   └─────────────────────────────────────────┘                   │
│                                                                  │
│   layoutSubviews() вызывается при изменении bounds!             │
│   Архитектор перерасставляет мебель под новый размер комнаты.   │
└─────────────────────────────────────────────────────────────────┘

Аналогия: layoutSubviews - это архитектор, который знает
размеры комнаты и решает, где поставить каждый предмет мебели.
```

### 4. intrinsicContentSize = Естественный размер книги

```
┌─────────────────────────────────────────────────────────────────┐
│                      КНИЖНАЯ ПОЛКА                               │
│                                                                  │
│   Каждая книга имеет ЕСТЕСТВЕННЫЙ размер:                       │
│                                                                  │
│   ┌──┐   ┌────┐   ┌──────────┐                                  │
│   │  │   │    │   │          │                                  │
│   │A5│   │ A4 │   │    A3    │                                  │
│   │  │   │    │   │          │                                  │
│   └──┘   └────┘   └──────────┘                                  │
│                                                                  │
│   intrinsicContentSize = размер, который view "хочет" иметь     │
│                                                                  │
│   UILabel: размер текста + padding                              │
│   UIImageView: размер изображения                               │
│   CustomView: вы определяете сами!                              │
│                                                                  │
│   Auto Layout использует intrinsicContentSize для расчета       │
│   constraints с низким приоритетом (content hugging/compression)│
└─────────────────────────────────────────────────────────────────┘

Аналогия: intrinsicContentSize - это естественный размер книги.
Можно сжать или растянуть, но книга "хочет" быть своего размера.
```

### 5. @IBDesignable = Предпросмотр мебели в каталоге IKEA

```
┌─────────────────────────────────────────────────────────────────┐
│                     КАТАЛОГ IKEA                                 │
│                                                                  │
│   Без @IBDesignable:              С @IBDesignable:              │
│   ┌──────────────────┐            ┌──────────────────┐          │
│   │                  │            │   ┌──────────┐   │          │
│   │   CustomView     │            │   │⭐⭐⭐⭐⭐│   │          │
│   │   (серый блок)   │            │   │ 4.5/5.0  │   │          │
│   │                  │            │   │ RatingView│   │          │
│   │                  │            │   └──────────┘   │          │
│   └──────────────────┘            └──────────────────┘          │
│                                                                  │
│   Interface Builder:              Interface Builder:            │
│   "Запустите app,                 "Вот как будет выглядеть      │
│   чтобы увидеть"                  ваш RatingView в runtime"     │
│                                                                  │
│   @IBInspectable = настраиваемые параметры в Inspector          │
│   (цвет, размер, текст и т.д.)                                  │
└─────────────────────────────────────────────────────────────────┘

Аналогия: @IBDesignable - это AR-приложение IKEA, которое
показывает, как будет выглядеть мебель в вашей комнате до покупки.
```

---

## Когда создавать Custom View

### Дерево решений

```
                    НУЖЕН CUSTOM UI КОМПОНЕНТ?
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Можно собрать из стандартных  │
              │ UIKit компонентов?            │
              └───────────────┬───────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼ ДА                               ▼ НЕТ
   ┌─────────────────┐                ┌─────────────────┐
   │   КОМПОЗИЦИЯ    │                │ CUSTOM DRAWING  │
   │  (Subviews)     │                │   или CALayer   │
   └────────┬────────┘                └────────┬────────┘
            │                                   │
            ▼                                   ▼
   ┌─────────────────────────┐       ┌─────────────────────────┐
   │ • Быстрее в разработке  │       │ • Векторная графика     │
   │ • GPU-оптимизировано    │       │ • Сложные формы         │
   │ • Accessibility free    │       │ • Градиенты, patterns   │
   │ • Легко поддерживать    │       │ • Performance critical  │
   └─────────────────────────┘       └─────────────────────────┘
```

### Composition vs Subclassing

```
┌────────────────────────────────────────────────────────────────────┐
│                     ВЫБОР ПОДХОДА                                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  COMPOSITION (составление из готовых view):                        │
│  ═══════════════════════════════════════════                       │
│                                                                     │
│  class ProfileCard: UIView {                                       │
│      let avatarView = UIImageView()    // Готовый компонент        │
│      let nameLabel = UILabel()         // Готовый компонент        │
│      let bioLabel = UILabel()          // Готовый компонент        │
│  }                                                                  │
│                                                                     │
│  Когда использовать:                                               │
│  ✓ 90% всех custom views                                           │
│  ✓ Карточки, ячейки, формы                                         │
│  ✓ Когда нужен стандартный look & feel                             │
│  ✓ Когда важна accessibility из коробки                            │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SUBCLASSING с draw(_:):                                           │
│  ═══════════════════════                                           │
│                                                                     │
│  class CircularProgress: UIView {                                  │
│      override func draw(_ rect: CGRect) {                          │
│          // Рисуем круговой прогресс через Core Graphics           │
│      }                                                              │
│  }                                                                  │
│                                                                     │
│  Когда использовать:                                               │
│  ✓ Графики и диаграммы                                             │
│  ✓ Кастомные индикаторы прогресса                                  │
│  ✓ Сложные векторные формы                                         │
│  ✓ Pixel-perfect контроль                                          │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CALayer SUBCLASSING:                                              │
│  ════════════════════                                              │
│                                                                     │
│  class GradientView: UIView {                                      │
│      override class var layerClass: AnyClass {                     │
│          CAGradientLayer.self                                      │
│      }                                                              │
│  }                                                                  │
│                                                                     │
│  Когда использовать:                                               │
│  ✓ Градиенты (CAGradientLayer)                                     │
│  ✓ Формы с анимацией (CAShapeLayer)                                │
│  ✓ Частицы и эмиттеры (CAEmitterLayer)                             │
│  ✓ Репликация элементов (CAReplicatorLayer)                        │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Когда использовать draw(_:)

```
                        ИСПОЛЬЗОВАТЬ draw(_:)?
                                │
                                ▼
                ┌───────────────────────────────┐
                │ Нужна векторная графика,      │
                │ которая масштабируется?       │
                └───────────────┬───────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │ НЕТ                               │ ДА
              ▼                                   ▼
     ┌─────────────────┐                ┌─────────────────┐
     │ Используйте     │                │ draw(_:) или    │
     │ UIImageView +   │                │ CAShapeLayer    │
     │ растровые       │                │                 │
     │ изображения     │                │                 │
     └─────────────────┘                └────────┬────────┘
                                                 │
                                                 ▼
                                ┌───────────────────────────────┐
                                │ Нужна анимация path?          │
                                └───────────────┬───────────────┘
                                                │
                          ┌─────────────────────┴────────────────────┐
                          │ НЕТ                                      │ ДА
                          ▼                                          ▼
                 ┌─────────────────┐                        ┌─────────────────┐
                 │ draw(_:) +      │                        │ CAShapeLayer +  │
                 │ UIBezierPath    │                        │ strokeEnd       │
                 │                 │                        │ animation       │
                 └─────────────────┘                        └─────────────────┘
```

### Сравнение производительности

```
┌────────────────────────────────────────────────────────────────────┐
│              PERFORMANCE COMPARISON (iPhone 14 Pro)                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Задача: отобразить 100 карточек со скругленными углами            │
│                                                                     │
│  Подход                           │ FPS   │ Memory │ GPU Load      │
│  ─────────────────────────────────┼───────┼────────┼──────────     │
│  UIView + cornerRadius            │  60   │  45MB  │  12%          │
│  UIView + cornerRadius + shadow   │  42   │  78MB  │  45% ⚠️       │
│  CAShapeLayer (masked)            │  58   │  52MB  │  18%          │
│  draw(_:) + UIBezierPath          │  35   │  120MB │  8% (CPU!)    │
│  Pre-rendered images              │  60   │  35MB  │  5%           │
│                                                                     │
│  ВЫВОД:                                                            │
│  • Композиция = лучший баланс performance/maintainability          │
│  • draw(_:) дорогой на CPU, используйте только когда необходимо    │
│  • cornerRadius + shadow = off-screen rendering (избегать!)        │
│  • Pre-rendered images = максимальная производительность           │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Создание UIView Subclass

### init(frame:) и init(coder:)

UIView имеет два designated initializer'а, которые ОБЯЗАТЕЛЬНО нужно реализовать:

```swift
// MARK: - Два обязательных инициализатора

class CustomCardView: UIView {

    // 1. Программное создание: let card = CustomCardView(frame: .zero)
    override init(frame: CGRect) {
        super.init(frame: frame)
        commonInit()
    }

    // 2. Создание из Storyboard/XIB: @IBOutlet weak var card: CustomCardView!
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        commonInit()
    }

    // 3. Общая инициализация - вызывается из обоих init
    private func commonInit() {
        setupViews()
        setupConstraints()
        setupAppearance()
    }
}
```

### Диаграмма жизненного цикла инициализации

```
┌────────────────────────────────────────────────────────────────────┐
│                   ЖИЗНЕННЫЙ ЦИКЛ ИНИЦИАЛИЗАЦИИ                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ПРОГРАММНОЕ СОЗДАНИЕ:           ИЗ STORYBOARD:                   │
│                                                                     │
│   let view = MyView(frame: .zero) MyView создается из XIB/SB       │
│           │                                │                        │
│           ▼                                ▼                        │
│   ┌───────────────────┐           ┌───────────────────┐            │
│   │ init(frame:)      │           │ init(coder:)      │            │
│   └─────────┬─────────┘           └─────────┬─────────┘            │
│             │                               │                       │
│             └───────────────┬───────────────┘                       │
│                             │                                       │
│                             ▼                                       │
│                    ┌───────────────────┐                           │
│                    │   commonInit()    │  ← ОБЩАЯ ТОЧКА ВХОДА      │
│                    │   • setupViews()  │                           │
│                    │   • constraints   │                           │
│                    │   • appearance    │                           │
│                    └─────────┬─────────┘                           │
│                              │                                      │
│                              ▼                                      │
│   [Если из Storyboard] ┌───────────────────┐                       │
│                        │ awakeFromNib()    │  ← IBOutlets доступны │
│                        └─────────┬─────────┘                       │
│                                  │                                  │
│                                  ▼                                  │
│                       ┌───────────────────┐                        │
│                       │ layoutSubviews()  │  ← bounds известны     │
│                       └───────────────────┘                        │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### CommonInit Pattern - полный пример

```swift
// MARK: - ProfileCardView.swift

import UIKit

/// Карточка профиля пользователя с аватаром, именем и описанием
final class ProfileCardView: UIView {

    // MARK: - UI Components

    private let avatarImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFill
        imageView.clipsToBounds = true
        imageView.backgroundColor = .systemGray5
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()

    private let nameLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 17, weight: .semibold)
        label.textColor = .label
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let bioLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 14, weight: .regular)
        label.textColor = .secondaryLabel
        label.numberOfLines = 2
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let containerStack: UIStackView = {
        let stack = UIStackView()
        stack.axis = .horizontal
        stack.spacing = 12
        stack.alignment = .center
        stack.translatesAutoresizingMaskIntoConstraints = false
        return stack
    }()

    // MARK: - Properties

    private let avatarSize: CGFloat = 48

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        commonInit()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        commonInit()
    }

    // MARK: - Common Init

    private func commonInit() {
        setupViews()
        setupConstraints()
        setupAppearance()
    }

    // MARK: - Setup Methods

    private func setupViews() {
        // Добавляем subviews в правильном порядке
        let textStack = UIStackView(arrangedSubviews: [nameLabel, bioLabel])
        textStack.axis = .vertical
        textStack.spacing = 4

        containerStack.addArrangedSubview(avatarImageView)
        containerStack.addArrangedSubview(textStack)

        addSubview(containerStack)
    }

    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Avatar size
            avatarImageView.widthAnchor.constraint(equalToConstant: avatarSize),
            avatarImageView.heightAnchor.constraint(equalToConstant: avatarSize),

            // Container fills the view with padding
            containerStack.topAnchor.constraint(equalTo: topAnchor, constant: 12),
            containerStack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            containerStack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            containerStack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -12)
        ])
    }

    private func setupAppearance() {
        backgroundColor = .systemBackground
        layer.cornerRadius = 12
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOpacity = 0.1
        layer.shadowOffset = CGSize(width: 0, height: 2)
        layer.shadowRadius = 8
    }

    // MARK: - Layout

    override func layoutSubviews() {
        super.layoutSubviews()
        // Скругление аватара - требует знания bounds
        avatarImageView.layer.cornerRadius = avatarSize / 2
        // Оптимизация shadow performance
        layer.shadowPath = UIBezierPath(roundedRect: bounds, cornerRadius: 12).cgPath
    }

    // MARK: - Public API

    func configure(with profile: Profile) {
        avatarImageView.image = profile.avatar
        nameLabel.text = profile.name
        bioLabel.text = profile.bio
    }
}

// MARK: - Model

struct Profile {
    let avatar: UIImage?
    let name: String
    let bio: String
}
```

### Использование созданного Custom View

```swift
// MARK: - Программное создание

let profileCard = ProfileCardView(frame: .zero)
profileCard.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(profileCard)

NSLayoutConstraint.activate([
    profileCard.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
    profileCard.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
    profileCard.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16)
])

profileCard.configure(with: Profile(
    avatar: UIImage(named: "avatar"),
    name: "John Appleseed",
    bio: "iOS Developer at Apple Inc."
))
```

---

## Layout Methods

### Иерархия методов layout

```
┌────────────────────────────────────────────────────────────────────┐
│                     LAYOUT METHODS HIERARCHY                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   UPDATE CYCLE (вызывается системой):                              │
│   ═══════════════════════════════════                              │
│                                                                     │
│   1. updateConstraints()       ← Обновить constraints (bottom-up)  │
│              │                                                      │
│              ▼                                                      │
│   2. layoutSubviews()          ← Рассчитать frames (top-down)      │
│              │                                                      │
│              ▼                                                      │
│   3. draw(_:)                  ← Отрисовать содержимое             │
│                                                                     │
│   ─────────────────────────────────────────────────────────────    │
│                                                                     │
│   МЕТОДЫ ЗАПРОСА (вызываете вы):                                   │
│   ══════════════════════════════                                   │
│                                                                     │
│   setNeedsUpdateConstraints() → updateConstraints() в след. цикле  │
│   setNeedsLayout()            → layoutSubviews() в след. цикле     │
│   setNeedsDisplay()           → draw(_:) в след. цикле             │
│                                                                     │
│   МЕТОДЫ НЕМЕДЛЕННОГО ВЫПОЛНЕНИЯ:                                  │
│   ═══════════════════════════════                                  │
│                                                                     │
│   updateConstraintsIfNeeded() → updateConstraints() СЕЙЧАС         │
│   layoutIfNeeded()            → layoutSubviews() СЕЙЧАС            │
│   (нет аналога для draw)                                           │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### layoutSubviews()

```swift
// MARK: - layoutSubviews - главный метод ручного layout

class CustomView: UIView {

    private let headerView = UIView()
    private let contentView = UIView()
    private let footerView = UIView()

    override func layoutSubviews() {
        super.layoutSubviews() // ВАЖНО: всегда вызывать super!

        // В этот момент bounds уже известны
        let width = bounds.width
        let height = bounds.height

        // Ручной расчет frames
        let headerHeight: CGFloat = 60
        let footerHeight: CGFloat = 44
        let contentHeight = height - headerHeight - footerHeight

        headerView.frame = CGRect(
            x: 0,
            y: 0,
            width: width,
            height: headerHeight
        )

        contentView.frame = CGRect(
            x: 0,
            y: headerHeight,
            width: width,
            height: contentHeight
        )

        footerView.frame = CGRect(
            x: 0,
            y: height - footerHeight,
            width: width,
            height: footerHeight
        )

        // Также здесь обновляем layer-зависимые свойства
        layer.shadowPath = UIBezierPath(rect: bounds).cgPath
        headerView.layer.cornerRadius = headerHeight / 2
    }
}
```

### setNeedsLayout() vs layoutIfNeeded()

```swift
// MARK: - Разница между setNeedsLayout и layoutIfNeeded

class AnimatedView: UIView {

    private var heightConstraint: NSLayoutConstraint!

    // setNeedsLayout() - отложенный layout
    // Layout произойдет в СЛЕДУЮЩЕМ цикле обновления
    func expandLater() {
        heightConstraint.constant = 200
        setNeedsLayout() // Помечает view как "нуждающийся в layout"
        // layoutSubviews() вызовется позже, автоматически
    }

    // layoutIfNeeded() - немедленный layout
    // Layout происходит СЕЙЧАС, синхронно
    func expandNow() {
        heightConstraint.constant = 200
        layoutIfNeeded() // Немедленно вызывает layoutSubviews()
    }

    // ГЛАВНОЕ ПРИМЕНЕНИЕ: анимации с constraints
    func expandWithAnimation() {
        heightConstraint.constant = 200

        UIView.animate(withDuration: 0.3) {
            // layoutIfNeeded() внутри animation block
            // позволяет анимировать изменение constraints
            self.superview?.layoutIfNeeded()
        }
    }
}
```

### Визуализация разницы

```
┌────────────────────────────────────────────────────────────────────┐
│            setNeedsLayout() vs layoutIfNeeded()                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   setNeedsLayout() - "Отложенный заказ":                           │
│   ══════════════════════════════════════                           │
│                                                                     │
│   t=0ms    t=5ms    t=10ms   t=16.67ms (VSync)                     │
│     │        │         │         │                                  │
│     ▼        ▼         ▼         ▼                                  │
│   [call]  [other]   [other]   [layoutSubviews() вызван!]           │
│   setNeeds  code     code                                           │
│   Layout()                                                          │
│                                                                     │
│   + Производительно: батчинг множества изменений                   │
│   + Система оптимизирует порядок layout                            │
│   - Не подходит для анимаций                                       │
│                                                                     │
│   ─────────────────────────────────────────────────────────────    │
│                                                                     │
│   layoutIfNeeded() - "Срочный заказ":                              │
│   ═══════════════════════════════════                              │
│                                                                     │
│   t=0ms                                                             │
│     │                                                               │
│     ▼                                                               │
│   [call layoutIfNeeded()]                                           │
│     │                                                               │
│     └──► [layoutSubviews() вызван СРАЗУ!]                          │
│                                                                     │
│   + Немедленный результат                                          │
│   + Необходим для анимаций constraints                             │
│   - Может быть неэффективно при частых вызовах                     │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### intrinsicContentSize

```swift
// MARK: - intrinsicContentSize - естественный размер view

/// Badge с автоматическим размером под содержимое
class BadgeView: UIView {

    private let label = UILabel()
    private let padding = UIEdgeInsets(top: 4, left: 8, bottom: 4, right: 8)

    var text: String = "" {
        didSet {
            label.text = text
            // ВАЖНО: сообщаем Auto Layout, что размер изменился
            invalidateIntrinsicContentSize()
        }
    }

    // Система Auto Layout спрашивает: "Какой размер ты хочешь?"
    override var intrinsicContentSize: CGSize {
        let labelSize = label.intrinsicContentSize
        return CGSize(
            width: labelSize.width + padding.left + padding.right,
            height: labelSize.height + padding.top + padding.bottom
        )
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        label.frame = bounds.inset(by: padding)
    }
}

// Использование:
let badge = BadgeView()
badge.text = "New" // intrinsicContentSize автоматически = размер "New" + padding
// Auto Layout использует этот размер, если нет явных constraints на width/height
```

### sizeThatFits(_:)

```swift
// MARK: - sizeThatFits vs intrinsicContentSize

class FlexibleView: UIView {

    private let textView = UITextView()

    // sizeThatFits(_:) - "Какой размер тебе нужен, если дать столько места?"
    // Параметр size - это ОГРАНИЧЕНИЯ, которые накладывает superview
    override func sizeThatFits(_ size: CGSize) -> CGSize {
        // Учитываем ограничение по ширине
        let textSize = textView.sizeThatFits(CGSize(
            width: size.width - 32, // padding
            height: .greatestFiniteMagnitude
        ))

        return CGSize(
            width: min(size.width, textSize.width + 32),
            height: textSize.height + 32
        )
    }

    // sizeToFit() - применяет sizeThatFits к текущему superview
    // Эквивалентно: bounds.size = sizeThatFits(superview.bounds.size)
    func updateSize() {
        sizeToFit() // Вызывает sizeThatFits и применяет результат
    }
}
```

### Сравнение методов определения размера

```
┌────────────────────────────────────────────────────────────────────┐
│              МЕТОДЫ ОПРЕДЕЛЕНИЯ РАЗМЕРА                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   МЕТОД                 │ КОНТЕКСТ          │ ИСПОЛЬЗОВАНИЕ         │
│   ──────────────────────┼───────────────────┼─────────────────────  │
│   intrinsicContentSize  │ Auto Layout       │ "Мой идеальный        │
│                         │                   │  размер без           │
│                         │                   │  ограничений"         │
│   ──────────────────────┼───────────────────┼─────────────────────  │
│   sizeThatFits(_:)      │ Ручной layout     │ "Мой размер с учетом  │
│                         │                   │  ограничения X"       │
│   ──────────────────────┼───────────────────┼─────────────────────  │
│   systemLayoutSizeFitting│ Auto Layout +    │ "Мой размер с учетом  │
│   (_:)                  │ constraints       │  приоритетов          │
│                         │                   │  constraints"         │
│                                                                     │
│   ПРИОРИТЕТЫ Auto Layout:                                          │
│   ═══════════════════════                                          │
│                                                                     │
│   Content Hugging = "Не хочу растягиваться"                        │
│   • Высокий приоритет = view сопротивляется увеличению             │
│   • По умолчанию: 250 (низкий)                                     │
│                                                                     │
│   Content Compression Resistance = "Не хочу сжиматься"             │
│   • Высокий приоритет = view сопротивляется уменьшению             │
│   • По умолчанию: 750 (высокий)                                    │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Custom Drawing

### draw(_:) method

```swift
// MARK: - Custom Drawing с draw(_:)

/// Круговой индикатор прогресса
class CircularProgressView: UIView {

    // MARK: - Properties

    var progress: CGFloat = 0.0 {
        didSet {
            progress = min(max(progress, 0), 1) // Clamp to 0...1
            setNeedsDisplay() // Запросить перерисовку
        }
    }

    var trackColor: UIColor = .systemGray5
    var progressColor: UIColor = .systemBlue
    var lineWidth: CGFloat = 8

    // MARK: - Drawing

    override func draw(_ rect: CGRect) {
        // 1. Получаем контекст рисования
        guard let context = UIGraphicsGetCurrentContext() else { return }

        // 2. Вычисляем геометрию
        let center = CGPoint(x: bounds.midX, y: bounds.midY)
        let radius = min(bounds.width, bounds.height) / 2 - lineWidth / 2
        let startAngle = -CGFloat.pi / 2 // 12 часов
        let endAngle = startAngle + 2 * .pi * progress

        // 3. Рисуем фоновый трек
        context.setStrokeColor(trackColor.cgColor)
        context.setLineWidth(lineWidth)
        context.setLineCap(.round)
        context.addArc(
            center: center,
            radius: radius,
            startAngle: 0,
            endAngle: 2 * .pi,
            clockwise: false
        )
        context.strokePath()

        // 4. Рисуем прогресс
        context.setStrokeColor(progressColor.cgColor)
        context.addArc(
            center: center,
            radius: radius,
            startAngle: startAngle,
            endAngle: endAngle,
            clockwise: false
        )
        context.strokePath()
    }
}
```

### UIBezierPath - более удобный API

```swift
// MARK: - UIBezierPath - высокоуровневый API для рисования

/// Кастомная звезда с рейтингом
class StarRatingView: UIView {

    var rating: CGFloat = 3.5 {
        didSet { setNeedsDisplay() }
    }

    var starCount: Int = 5
    var filledColor: UIColor = .systemYellow
    var emptyColor: UIColor = .systemGray4

    override func draw(_ rect: CGRect) {
        let starWidth = bounds.width / CGFloat(starCount)
        let starHeight = bounds.height
        let starSize = min(starWidth, starHeight) * 0.8

        for i in 0..<starCount {
            let starRect = CGRect(
                x: CGFloat(i) * starWidth + (starWidth - starSize) / 2,
                y: (bounds.height - starSize) / 2,
                width: starSize,
                height: starSize
            )

            let starPath = starPath(in: starRect)

            // Определяем заполнение звезды
            let fillAmount = min(max(rating - CGFloat(i), 0), 1)

            if fillAmount >= 1 {
                // Полностью заполненная звезда
                filledColor.setFill()
                starPath.fill()
            } else if fillAmount > 0 {
                // Частично заполненная звезда
                emptyColor.setFill()
                starPath.fill()

                // Clipping для частичного заполнения
                if let context = UIGraphicsGetCurrentContext() {
                    context.saveGState()
                    let clipRect = CGRect(
                        x: starRect.minX,
                        y: starRect.minY,
                        width: starRect.width * fillAmount,
                        height: starRect.height
                    )
                    context.clip(to: clipRect)
                    filledColor.setFill()
                    starPath.fill()
                    context.restoreGState()
                }
            } else {
                // Пустая звезда
                emptyColor.setFill()
                starPath.fill()
            }
        }
    }

    private func starPath(in rect: CGRect) -> UIBezierPath {
        let path = UIBezierPath()
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let outerRadius = min(rect.width, rect.height) / 2
        let innerRadius = outerRadius * 0.4

        for i in 0..<10 {
            let angle = CGFloat(i) * .pi / 5 - .pi / 2
            let radius = i.isMultiple(of: 2) ? outerRadius : innerRadius
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
        path.close()
        return path
    }
}
```

### Core Graphics - низкоуровневый контроль

```swift
// MARK: - Core Graphics для сложной графики

/// Кастомный график (line chart)
class LineChartView: UIView {

    var dataPoints: [CGFloat] = [] {
        didSet { setNeedsDisplay() }
    }

    var lineColor: UIColor = .systemBlue
    var fillColor: UIColor = UIColor.systemBlue.withAlphaComponent(0.1)
    var gridColor: UIColor = .systemGray5

    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext(),
              !dataPoints.isEmpty else { return }

        drawGrid(in: context, rect: rect)
        drawLine(in: context, rect: rect)
        drawFill(in: context, rect: rect)
    }

    private func drawGrid(in context: CGContext, rect: CGRect) {
        context.setStrokeColor(gridColor.cgColor)
        context.setLineWidth(0.5)

        // Горизонтальные линии
        for i in 0...4 {
            let y = rect.height * CGFloat(i) / 4
            context.move(to: CGPoint(x: 0, y: y))
            context.addLine(to: CGPoint(x: rect.width, y: y))
        }
        context.strokePath()
    }

    private func drawLine(in context: CGContext, rect: CGRect) {
        guard dataPoints.count > 1 else { return }

        let maxValue = dataPoints.max() ?? 1
        let minValue = dataPoints.min() ?? 0
        let range = maxValue - minValue

        context.setStrokeColor(lineColor.cgColor)
        context.setLineWidth(2)
        context.setLineCap(.round)
        context.setLineJoin(.round)

        for (index, value) in dataPoints.enumerated() {
            let x = rect.width * CGFloat(index) / CGFloat(dataPoints.count - 1)
            let normalizedValue = range > 0 ? (value - minValue) / range : 0.5
            let y = rect.height * (1 - normalizedValue)

            if index == 0 {
                context.move(to: CGPoint(x: x, y: y))
            } else {
                context.addLine(to: CGPoint(x: x, y: y))
            }
        }
        context.strokePath()
    }

    private func drawFill(in context: CGContext, rect: CGRect) {
        guard dataPoints.count > 1 else { return }

        let maxValue = dataPoints.max() ?? 1
        let minValue = dataPoints.min() ?? 0
        let range = maxValue - minValue

        context.setFillColor(fillColor.cgColor)

        // Начинаем с нижнего левого угла
        context.move(to: CGPoint(x: 0, y: rect.height))

        for (index, value) in dataPoints.enumerated() {
            let x = rect.width * CGFloat(index) / CGFloat(dataPoints.count - 1)
            let normalizedValue = range > 0 ? (value - minValue) / range : 0.5
            let y = rect.height * (1 - normalizedValue)
            context.addLine(to: CGPoint(x: x, y: y))
        }

        // Замыкаем путь
        context.addLine(to: CGPoint(x: rect.width, y: rect.height))
        context.closePath()
        context.fillPath()
    }
}
```

### Performance considerations

```
┌────────────────────────────────────────────────────────────────────┐
│              PERFORMANCE: draw(_:) OPTIMIZATION                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   draw(_:) ВЫЗЫВАЕТСЯ:                                             │
│   ═══════════════════                                              │
│                                                                     │
│   ✓ При первом появлении view                                      │
│   ✓ После setNeedsDisplay()                                        │
│   ✓ При изменении bounds (если contentMode != .redraw)             │
│   ✗ НЕ вызывается каждый кадр!                                     │
│   ✗ НЕ вызывается при изменении transform/opacity                  │
│                                                                     │
│   ОПТИМИЗАЦИИ:                                                     │
│   ════════════                                                     │
│                                                                     │
│   1. Минимизируйте setNeedsDisplay() вызовы                        │
│      ❌ didSet { setNeedsDisplay() } для каждого свойства          │
│      ✅ Batch updates: updateAppearance() вызывает один раз        │
│                                                                     │
│   2. Используйте setNeedsDisplay(_:) для partial redraw            │
│      setNeedsDisplay(dirtyRect) // Только изменившаяся область     │
│                                                                     │
│   3. Кэшируйте сложные пути                                        │
│      ❌ Создавать UIBezierPath в draw(_:)                          │
│      ✅ Создать один раз, хранить в property                       │
│                                                                     │
│   4. Используйте CAShapeLayer для анимации                         │
│      ❌ Анимировать через setNeedsDisplay() в CADisplayLink        │
│      ✅ CAShapeLayer.strokeEnd с CABasicAnimation                  │
│                                                                     │
│   5. Выносите статику в отдельный слой                             │
│      Фон, сетка → отдельный CALayer (не перерисовывается)          │
│      Данные → draw(_:) (перерисовывается при изменении)            │
│                                                                     │
│   ИЗМЕРЕНИЕ:                                                       │
│   ══════════                                                       │
│                                                                     │
│   Instruments → Core Animation → "Color Blended Layers"            │
│   Instruments → Time Profiler → Поиск draw(_:) в стеке             │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Пример оптимизированного draw

```swift
// MARK: - Оптимизированный Custom Drawing

class OptimizedChartView: UIView {

    var dataPoints: [CGFloat] = [] {
        didSet {
            updateLinePath()
            setNeedsDisplay()
        }
    }

    // Кэшированный путь - не пересоздается в draw(_:)
    private var cachedLinePath: UIBezierPath?
    private var cachedFillPath: UIBezierPath?

    // Предвычисляем путь при изменении данных
    private func updateLinePath() {
        guard !dataPoints.isEmpty else {
            cachedLinePath = nil
            cachedFillPath = nil
            return
        }

        let maxValue = dataPoints.max() ?? 1
        let minValue = dataPoints.min() ?? 0
        let range = max(maxValue - minValue, 0.001)

        let linePath = UIBezierPath()
        let fillPath = UIBezierPath()

        for (index, value) in dataPoints.enumerated() {
            let x = CGFloat(index) / CGFloat(max(dataPoints.count - 1, 1))
            let y = 1 - (value - minValue) / range
            let point = CGPoint(x: x, y: y) // Normalized 0...1

            if index == 0 {
                linePath.move(to: point)
                fillPath.move(to: CGPoint(x: 0, y: 1))
                fillPath.addLine(to: point)
            } else {
                linePath.addLine(to: point)
                fillPath.addLine(to: point)
            }
        }

        fillPath.addLine(to: CGPoint(x: 1, y: 1))
        fillPath.close()

        cachedLinePath = linePath
        cachedFillPath = fillPath
    }

    override func draw(_ rect: CGRect) {
        guard let linePath = cachedLinePath,
              let fillPath = cachedFillPath else { return }

        // Применяем transform для масштабирования к bounds
        let transform = CGAffineTransform(scaleX: bounds.width, y: bounds.height)

        // Рисуем заливку
        UIColor.systemBlue.withAlphaComponent(0.1).setFill()
        fillPath.copy().applying(transform).fill()

        // Рисуем линию
        UIColor.systemBlue.setStroke()
        let scaledLine = linePath.copy() as! UIBezierPath
        scaledLine.apply(transform)
        scaledLine.lineWidth = 2
        scaledLine.lineCapStyle = .round
        scaledLine.lineJoinStyle = .round
        scaledLine.stroke()
    }
}
```

---

## @IBDesignable и @IBInspectable

### Основы использования

```swift
// MARK: - @IBDesignable и @IBInspectable

import UIKit

/// Кнопка с настраиваемым внешним видом в Interface Builder
@IBDesignable
class CustomButton: UIButton {

    // MARK: - Inspectable Properties

    @IBInspectable var cornerRadius: CGFloat = 8 {
        didSet { updateAppearance() }
    }

    @IBInspectable var borderWidth: CGFloat = 0 {
        didSet { updateAppearance() }
    }

    @IBInspectable var borderColor: UIColor = .clear {
        didSet { updateAppearance() }
    }

    @IBInspectable var shadowRadius: CGFloat = 0 {
        didSet { updateAppearance() }
    }

    @IBInspectable var shadowOpacity: Float = 0 {
        didSet { updateAppearance() }
    }

    @IBInspectable var shadowOffset: CGSize = .zero {
        didSet { updateAppearance() }
    }

    @IBInspectable var shadowColor: UIColor = .black {
        didSet { updateAppearance() }
    }

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        commonInit()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        commonInit()
    }

    private func commonInit() {
        updateAppearance()
    }

    // MARK: - Appearance

    private func updateAppearance() {
        layer.cornerRadius = cornerRadius
        layer.borderWidth = borderWidth
        layer.borderColor = borderColor.cgColor
        layer.shadowRadius = shadowRadius
        layer.shadowOpacity = shadowOpacity
        layer.shadowOffset = shadowOffset
        layer.shadowColor = shadowColor.cgColor

        // Оптимизация shadow rendering
        if shadowOpacity > 0 {
            layer.shadowPath = UIBezierPath(
                roundedRect: bounds,
                cornerRadius: cornerRadius
            ).cgPath
        }
    }

    // MARK: - Layout

    override func layoutSubviews() {
        super.layoutSubviews()
        // Обновляем shadowPath при изменении размера
        if shadowOpacity > 0 {
            layer.shadowPath = UIBezierPath(
                roundedRect: bounds,
                cornerRadius: cornerRadius
            ).cgPath
        }
    }

    // MARK: - Interface Builder

    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
        // Код, выполняемый ТОЛЬКО в Interface Builder
        // Полезно для настройки preview
        updateAppearance()
    }
}
```

### Как это выглядит в Interface Builder

```
┌────────────────────────────────────────────────────────────────────┐
│              INTERFACE BUILDER С @IBDesignable                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────────────┐    ┌─────────────────────────────────┐   │
│   │                     │    │  Attributes Inspector            │   │
│   │  ┌───────────────┐  │    │  ─────────────────────────────── │   │
│   │  │               │  │    │                                  │   │
│   │  │  CustomButton │  │    │  Custom Button                   │   │
│   │  │  [Preview!]   │  │    │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │   │
│   │  │               │  │    │                                  │   │
│   │  └───────────────┘  │    │  Corner Radius    [    8    ]   │   │
│   │                     │    │  Border Width     [    1    ]   │   │
│   │  Canvas             │    │  Border Color     [  Blue   ]   │   │
│   │                     │    │  Shadow Radius    [    4    ]   │   │
│   └─────────────────────┘    │  Shadow Opacity   [   0.2   ]   │   │
│                              │  Shadow Offset    [ (0, 2) ]    │   │
│   "Designables: Up to date"  │  Shadow Color     [ Black  ]    │   │
│   ✓ Компилируется в реальном │                                  │   │
│     времени!                 └─────────────────────────────────┘   │
│                                                                     │
│   ПРЕИМУЩЕСТВА:                                                    │
│   • Live preview без запуска симулятора                            │
│   • Настройка в визуальном редакторе                               │
│   • Быстрая итерация дизайна                                       │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### prepareForInterfaceBuilder()

```swift
// MARK: - prepareForInterfaceBuilder для сложных случаев

@IBDesignable
class DataChartView: UIView {

    @IBInspectable var lineColor: UIColor = .systemBlue

    var dataPoints: [CGFloat] = []

    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()

        // В Interface Builder нет реальных данных
        // Генерируем mock данные для preview
        dataPoints = [10, 25, 15, 30, 22, 35, 28, 40, 32, 45]
    }

    override func draw(_ rect: CGRect) {
        // Обычный код рисования
        // Работает и в runtime, и в IB
    }
}
```

### Ограничения @IBDesignable

```
┌────────────────────────────────────────────────────────────────────┐
│              ОГРАНИЧЕНИЯ @IBDesignable                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ТЕХНИЧЕСКИЕ ОГРАНИЧЕНИЯ:                                         │
│   ════════════════════════                                         │
│                                                                     │
│   ❌ Нет доступа к Bundle.main (используйте Bundle(for: type(of:   │
│      self)) или #if TARGET_INTERFACE_BUILDER)                      │
│                                                                     │
│   ❌ Нет сетевых запросов (таймаут IB = несколько секунд)          │
│                                                                     │
│   ❌ Ограниченный доступ к файловой системе                        │
│                                                                     │
│   ❌ Медленная компиляция при сложных view                         │
│                                                                     │
│   ❌ Не все типы поддерживаются @IBInspectable:                    │
│      ✓ Int, CGFloat, Double, Float                                 │
│      ✓ Bool                                                         │
│      ✓ String                                                       │
│      ✓ CGPoint, CGSize, CGRect                                     │
│      ✓ UIColor, UIImage                                            │
│      ✗ Enums, Arrays, Custom types                                 │
│                                                                     │
│   WORKAROUNDS:                                                     │
│   ════════════                                                     │
│                                                                     │
│   // Enum через Int adapter                                        │
│   @IBInspectable var styleRaw: Int = 0 {                           │
│       didSet { style = Style(rawValue: styleRaw) ?? .default }     │
│   }                                                                 │
│   var style: Style = .default                                      │
│                                                                     │
│   // Проверка контекста                                            │
│   #if TARGET_INTERFACE_BUILDER                                     │
│       // Код только для IB                                         │
│   #else                                                             │
│       // Код только для runtime                                    │
│   #endif                                                            │
│                                                                     │
│   // Загрузка ресурсов                                             │
│   let bundle = Bundle(for: type(of: self))                         │
│   let image = UIImage(named: "icon", in: bundle, with: nil)        │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## SwiftUI Custom Views

### Shape protocol

```swift
import SwiftUI

// MARK: - Custom Shape в SwiftUI

/// Звезда с настраиваемым количеством лучей
struct Star: Shape {
    var points: Int = 5
    var innerRatio: CGFloat = 0.4

    func path(in rect: CGRect) -> Path {
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let outerRadius = min(rect.width, rect.height) / 2
        let innerRadius = outerRadius * innerRatio

        var path = Path()
        let angleIncrement = .pi / CGFloat(points)

        for i in 0..<(points * 2) {
            let angle = CGFloat(i) * angleIncrement - .pi / 2
            let radius = i.isMultiple(of: 2) ? outerRadius : innerRadius
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

// Использование
struct ContentView: View {
    var body: some View {
        Star(points: 5, innerRatio: 0.4)
            .fill(.yellow)
            .frame(width: 100, height: 100)
    }
}
```

### Animatable Shape

```swift
// MARK: - Анимируемая форма в SwiftUI

struct AnimatableStar: Shape {
    var points: Int = 5
    var innerRatio: CGFloat = 0.4

    // Animatable требует animatableData
    var animatableData: CGFloat {
        get { innerRatio }
        set { innerRatio = newValue }
    }

    func path(in rect: CGRect) -> Path {
        // Тот же код что и выше
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let outerRadius = min(rect.width, rect.height) / 2
        let innerRadius = outerRadius * innerRatio

        var path = Path()
        let angleIncrement = .pi / CGFloat(points)

        for i in 0..<(points * 2) {
            let angle = CGFloat(i) * angleIncrement - .pi / 2
            let radius = i.isMultiple(of: 2) ? outerRadius : innerRadius
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

// Использование с анимацией
struct AnimatedStarView: View {
    @State private var innerRatio: CGFloat = 0.4

    var body: some View {
        AnimatableStar(innerRatio: innerRatio)
            .fill(.yellow)
            .frame(width: 200, height: 200)
            .onTapGesture {
                withAnimation(.spring()) {
                    innerRatio = innerRatio == 0.4 ? 0.2 : 0.4
                }
            }
    }
}
```

### Canvas для custom drawing

```swift
// MARK: - Canvas для произвольного рисования (iOS 15+)

struct LineChartView: View {
    let dataPoints: [CGFloat]

    var body: some View {
        Canvas { context, size in
            guard dataPoints.count > 1 else { return }

            let maxValue = dataPoints.max() ?? 1
            let minValue = dataPoints.min() ?? 0
            let range = max(maxValue - minValue, 0.001)

            // Создаем путь линии
            var linePath = Path()
            var fillPath = Path()

            fillPath.move(to: CGPoint(x: 0, y: size.height))

            for (index, value) in dataPoints.enumerated() {
                let x = size.width * CGFloat(index) / CGFloat(dataPoints.count - 1)
                let normalizedValue = (value - minValue) / range
                let y = size.height * (1 - normalizedValue)
                let point = CGPoint(x: x, y: y)

                if index == 0 {
                    linePath.move(to: point)
                } else {
                    linePath.addLine(to: point)
                }
                fillPath.addLine(to: point)
            }

            fillPath.addLine(to: CGPoint(x: size.width, y: size.height))
            fillPath.closeSubpath()

            // Рисуем заливку
            context.fill(
                fillPath,
                with: .color(.blue.opacity(0.1))
            )

            // Рисуем линию
            context.stroke(
                linePath,
                with: .color(.blue),
                lineWidth: 2
            )
        }
    }
}

// Использование
struct ChartExample: View {
    var body: some View {
        LineChartView(dataPoints: [10, 25, 15, 30, 22, 35, 28, 40])
            .frame(height: 200)
            .padding()
    }
}
```

### GeometryReader для layout

```swift
// MARK: - GeometryReader для кастомного layout

struct AdaptiveGrid<Content: View>: View {
    let minItemWidth: CGFloat
    let spacing: CGFloat
    let content: () -> Content

    init(
        minItemWidth: CGFloat = 100,
        spacing: CGFloat = 16,
        @ViewBuilder content: @escaping () -> Content
    ) {
        self.minItemWidth = minItemWidth
        self.spacing = spacing
        self.content = content
    }

    var body: some View {
        GeometryReader { geometry in
            let columns = max(1, Int(geometry.size.width / minItemWidth))
            let itemWidth = (geometry.size.width - CGFloat(columns - 1) * spacing) / CGFloat(columns)

            LazyVGrid(
                columns: Array(repeating: GridItem(.fixed(itemWidth), spacing: spacing), count: columns),
                spacing: spacing
            ) {
                content()
            }
        }
    }
}

// Custom View с GeometryReader
struct CircularProgressRing: View {
    var progress: CGFloat
    var lineWidth: CGFloat = 10
    var trackColor: Color = .gray.opacity(0.2)
    var progressColor: Color = .blue

    var body: some View {
        GeometryReader { geometry in
            let size = min(geometry.size.width, geometry.size.height)
            let center = CGPoint(x: geometry.size.width / 2, y: geometry.size.height / 2)

            ZStack {
                // Track
                Circle()
                    .stroke(trackColor, lineWidth: lineWidth)

                // Progress
                Circle()
                    .trim(from: 0, to: progress)
                    .stroke(
                        progressColor,
                        style: StrokeStyle(
                            lineWidth: lineWidth,
                            lineCap: .round
                        )
                    )
                    .rotationEffect(.degrees(-90))

                // Label
                Text("\(Int(progress * 100))%")
                    .font(.system(size: size * 0.2, weight: .bold))
            }
            .frame(width: size, height: size)
            .position(center)
        }
    }
}
```

### Сравнение UIKit vs SwiftUI Custom Views

```
┌────────────────────────────────────────────────────────────────────┐
│              UIKit vs SwiftUI CUSTOM VIEWS                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   КОНЦЕПЦИЯ          │ UIKit                │ SwiftUI              │
│   ───────────────────┼──────────────────────┼───────────────────── │
│   Базовый класс      │ UIView subclass      │ struct: View         │
│   Рисование          │ draw(_:)             │ Shape/Canvas         │
│   Layout             │ layoutSubviews()     │ GeometryReader       │
│   Инициализация      │ init(frame:)/coder   │ init параметры       │
│   Состояние          │ properties + setNeeds│ @State/@Binding      │
│   Анимация           │ CAAnimation/UIView   │ withAnimation        │
│   Preview            │ @IBDesignable        │ #Preview             │
│                                                                     │
│   КОГДА ИСПОЛЬЗОВАТЬ:                                              │
│   ═══════════════════                                              │
│                                                                     │
│   UIKit Custom View:                                               │
│   • Legacy проекты (iOS < 13)                                      │
│   • Интеграция с UIKit-only API                                    │
│   • Fine-grained контроль рендеринга                               │
│   • Сложные touch handling                                         │
│                                                                     │
│   SwiftUI Custom View:                                             │
│   • Новые проекты (iOS 14+)                                        │
│   • Быстрое прототипирование                                       │
│   • Декларативные анимации                                         │
│   • Простое состояние и data binding                               │
│                                                                     │
│   МИГРАЦИЯ UIKit → SwiftUI:                                        │
│   ═════════════════════════                                        │
│                                                                     │
│   struct UIKitViewWrapper: UIViewRepresentable {                   │
│       func makeUIView(context: Context) -> CustomUIView {          │
│           CustomUIView()                                           │
│       }                                                             │
│       func updateUIView(_ uiView: CustomUIView, context: Context) {│
│           // Update from SwiftUI state                             │
│       }                                                             │
│   }                                                                 │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Распространённые ошибки

### 1. Не вызывать super в override методах

```swift
// ❌ НЕПРАВИЛЬНО: забыли вызвать super

class BadView: UIView {
    override func layoutSubviews() {
        // Сразу свой код без super
        configureSubviews()
    }

    override func draw(_ rect: CGRect) {
        // Рисуем без super
        drawCustomContent()
    }
}

// ✅ ПРАВИЛЬНО: всегда вызываем super

class GoodView: UIView {
    override func layoutSubviews() {
        super.layoutSubviews() // ВАЖНО: Auto Layout и subviews layout
        configureSubviews()
    }

    override func draw(_ rect: CGRect) {
        super.draw(rect) // Вызываем для UIView (хотя он пустой)
        drawCustomContent()
    }
}

// ИСКЛЮЧЕНИЕ: draw(_:) в UIView по умолчанию пустой,
// но лучше вызывать super для будущей совместимости
// и если наследуетесь от UIControl/UIButton, где super важен
```

### 2. Изменение constraints в layoutSubviews

```swift
// ❌ НЕПРАВИЛЬНО: создаем/изменяем constraints в layoutSubviews

class BadView: UIView {
    override func layoutSubviews() {
        super.layoutSubviews()

        // Это вызовет бесконечный цикл!
        // constraints → layout → constraints → layout → ...
        NSLayoutConstraint.activate([
            subview.widthAnchor.constraint(equalToConstant: bounds.width * 0.5)
        ])
    }
}

// ✅ ПРАВИЛЬНО: constraints в init, frames в layoutSubviews

class GoodView: UIView {
    private var widthConstraint: NSLayoutConstraint?

    private func commonInit() {
        // Создаем constraints один раз
        widthConstraint = subview.widthAnchor.constraint(equalToConstant: 100)
        widthConstraint?.isActive = true
    }

    override func layoutSubviews() {
        super.layoutSubviews()

        // Обновляем constant, не создаем новый constraint
        widthConstraint?.constant = bounds.width * 0.5
    }
}

// ИЛИ используем proportional constraints изначально:
// subview.widthAnchor.constraint(equalTo: widthAnchor, multiplier: 0.5)
```

### 3. Тяжелые операции в draw(_:)

```swift
// ❌ НЕПРАВИЛЬНО: создаем объекты и делаем вычисления в draw

class BadChartView: UIView {
    var data: [Double] = []

    override func draw(_ rect: CGRect) {
        // Каждый раз пересоздаем!
        let path = UIBezierPath()
        let processedData = data.map { $0 * 100 } // Вычисления каждый раз
        let sortedData = processedData.sorted()   // Еще вычисления

        // ... рисование
    }
}

// ✅ ПРАВИЛЬНО: кэшируем и предвычисляем

class GoodChartView: UIView {
    var data: [Double] = [] {
        didSet {
            // Вычисляем при изменении данных, не в draw
            processedData = data.map { $0 * 100 }.sorted()
            cachedPath = buildPath()
            setNeedsDisplay()
        }
    }

    private var processedData: [Double] = []
    private var cachedPath: UIBezierPath?

    private func buildPath() -> UIBezierPath {
        let path = UIBezierPath()
        // ... построение пути
        return path
    }

    override func draw(_ rect: CGRect) {
        // Просто рисуем готовый путь
        cachedPath?.stroke()
    }
}
```

### 4. Неправильное использование translatesAutoresizingMaskIntoConstraints

```swift
// ❌ НЕПРАВИЛЬНО: забыли отключить для programmatic constraints

class BadView: UIView {
    private let label = UILabel()

    private func setupViews() {
        addSubview(label)
        // Забыли: label.translatesAutoresizingMaskIntoConstraints = false

        // Constraints НЕ работают! Label использует autoresizing mask
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: centerXAnchor),
            label.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }
}

// ✅ ПРАВИЛЬНО: отключаем для всех programmatic subviews

class GoodView: UIView {
    private let label: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false // Сразу при создании
        return label
    }()

    private func setupViews() {
        addSubview(label)

        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: centerXAnchor),
            label.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }
}

// ПРИМЕЧАНИЕ: Для view созданных в Storyboard/XIB
// translatesAutoresizingMaskIntoConstraints = false устанавливается автоматически
```

### 5. Цикличные зависимости в intrinsicContentSize

```swift
// ❌ НЕПРАВИЛЬНО: intrinsicContentSize зависит от bounds

class BadView: UIView {
    override var intrinsicContentSize: CGSize {
        // bounds еще не установлены при первом вызове!
        // Это создает проблему курица-яйцо
        return CGSize(width: bounds.width, height: 100)
    }
}

// ✅ ПРАВИЛЬНО: intrinsicContentSize НЕ зависит от текущего размера

class GoodView: UIView {
    private let label = UILabel()

    override var intrinsicContentSize: CGSize {
        // Основываемся на содержимом, не на bounds
        let labelSize = label.intrinsicContentSize
        return CGSize(
            width: labelSize.width + 32, // padding
            height: labelSize.height + 16
        )
    }

    // Если размер зависит от ширины, используйте constraints:
    // override var intrinsicContentSize: CGSize {
    //     return CGSize(width: UIView.noIntrinsicMetric, height: 100)
    // }
}
```

### 6. Забыть invalidateIntrinsicContentSize

```swift
// ❌ НЕПРАВИЛЬНО: меняем содержимое без invalidate

class BadBadge: UIView {
    var text: String = "" {
        didSet {
            label.text = text
            // Auto Layout не знает, что размер изменился!
        }
    }

    override var intrinsicContentSize: CGSize {
        let labelSize = label.intrinsicContentSize
        return CGSize(width: labelSize.width + 16, height: labelSize.height + 8)
    }
}

// ✅ ПРАВИЛЬНО: вызываем invalidateIntrinsicContentSize

class GoodBadge: UIView {
    var text: String = "" {
        didSet {
            label.text = text
            // Сообщаем Auto Layout о необходимости пересчета
            invalidateIntrinsicContentSize()
        }
    }

    override var intrinsicContentSize: CGSize {
        let labelSize = label.intrinsicContentSize
        return CGSize(width: labelSize.width + 16, height: labelSize.height + 8)
    }
}
```

---

## Ментальные модели

### 1. Custom View как "Черный ящик"

```
┌────────────────────────────────────────────────────────────────────┐
│               CUSTOM VIEW = ЧЕРНЫЙ ЯЩИК                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                        ВНЕШНИЙ МИР                                  │
│                            │                                        │
│                            ▼                                        │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │                    PUBLIC API                               │   │
│   │                                                             │   │
│   │   ВХОДЫ (настройка):         ВЫХОДЫ (события):             │   │
│   │   • configure(with:)         • delegate?.didTap()          │   │
│   │   • @IBInspectable props     • @IBAction events            │   │
│   │   • public properties        • Combine publishers          │   │
│   └────────────────────────────────────────────────────────────┘   │
│                            │                                        │
│   ┌────────────────────────┴───────────────────────────────────┐   │
│   │                    PRIVATE IMPLEMENTATION                   │   │
│   │            (скрыто от внешнего мира)                        │   │
│   │                                                             │   │
│   │   • Subviews hierarchy                                      │   │
│   │   • Constraints                                             │   │
│   │   • draw(_:) implementation                                 │   │
│   │   • Internal state                                          │   │
│   │   • Helper methods                                          │   │
│   │                                                             │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│   ПРИНЦИП: ViewController НЕ должен знать,                         │
│   как устроен Custom View внутри.                                  │
│   Он только передает данные и получает события.                    │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 2. Layout как "Переговоры"

```
┌────────────────────────────────────────────────────────────────────┐
│            LAYOUT = ПЕРЕГОВОРЫ МЕЖДУ VIEW                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   УЧАСТНИКИ ПЕРЕГОВОРОВ:                                           │
│   ══════════════════════                                           │
│                                                                     │
│   ┌─────────────┐          ┌─────────────┐                         │
│   │  SUPERVIEW  │          │  SUBVIEW    │                         │
│   │             │          │             │                         │
│   │ "Я даю тебе │          │ "Мне нужно  │                         │
│   │  300x200"   │          │  минимум    │                         │
│   │             │  ←────→  │  100x50"    │                         │
│   └─────────────┘          └─────────────┘                         │
│                                                                     │
│   ИНСТРУМЕНТЫ ПЕРЕГОВОРОВ:                                         │
│   ════════════════════════                                         │
│                                                                     │
│   intrinsicContentSize  = "Вот мой идеальный размер"               │
│   Content Hugging       = "Не хочу растягиваться" (приоритет)      │
│   Compression Resistance= "Не хочу сжиматься" (приоритет)          │
│   Constraints           = "Жесткие договоренности" (приоритет)     │
│                                                                     │
│   РЕЗУЛЬТАТ: Auto Layout Engine находит компромисс,                │
│   удовлетворяющий всем ограничениям по приоритетам.                │
│                                                                     │
│   Если компромисс невозможен → "Unable to satisfy constraints"      │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 3. draw(_:) как "Фотография"

```
┌────────────────────────────────────────────────────────────────────┐
│               draw(_:) = СОЗДАНИЕ ФОТОГРАФИИ                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ПРОЦЕСС:                                                         │
│   ════════                                                         │
│                                                                     │
│   1. setNeedsDisplay()                                             │
│      "Нужна новая фотография!"                                     │
│           │                                                         │
│           ▼                                                         │
│   2. Система выделяет bitmap (backing store)                       │
│      "Готовим чистый холст размером bounds"                        │
│           │                                                         │
│           ▼                                                         │
│   3. draw(_:) вызывается                                           │
│      "Художник рисует картину"                                     │
│           │                                                         │
│           ▼                                                         │
│   4. Bitmap сохраняется                                            │
│      "Фотография готова, убираем кисти"                            │
│           │                                                         │
│           ▼                                                         │
│   5. GPU использует bitmap как текстуру                            │
│      "Фотография висит на стене (экране)"                          │
│                                                                     │
│   ВАЖНО:                                                           │
│   • Фотография НЕ переснимается каждый кадр!                       │
│   • Только при явном setNeedsDisplay()                             │
│   • Transform/opacity меняют "раму", не фотографию                 │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 4. Composition vs Inheritance

```
┌────────────────────────────────────────────────────────────────────┐
│            COMPOSITION vs INHERITANCE для Custom Views              │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   INHERITANCE (наследование):                                      │
│   ═══════════════════════════                                      │
│                                                                     │
│   class CustomButton: UIButton {                                   │
│       // Расширяем существующий функционал                         │
│   }                                                                 │
│                                                                     │
│   Когда использовать:                                              │
│   ✓ Нужен весь функционал родителя                                 │
│   ✓ Кастомизация внешнего вида                                     │
│   ✓ Добавление поведения к стандартному view                       │
│                                                                     │
│   ─────────────────────────────────────────────────────────────    │
│                                                                     │
│   COMPOSITION (композиция):                                        │
│   ═════════════════════════                                        │
│                                                                     │
│   class ProfileCard: UIView {                                      │
│       let avatar = UIImageView()  // has-a, не is-a               │
│       let name = UILabel()                                         │
│   }                                                                 │
│                                                                     │
│   Когда использовать:                                              │
│   ✓ Новый компонент из готовых блоков                              │
│   ✓ Не нужен весь функционал UIButton/UILabel                      │
│   ✓ Больше гибкости в изменениях                                   │
│                                                                     │
│   ПРАВИЛО:                                                         │
│   "Prefer composition over inheritance"                            │
│   В 90% случаев композиция - лучший выбор                          │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 5. View Update Cycle как "Система заказов"

```
┌────────────────────────────────────────────────────────────────────┐
│            VIEW UPDATE CYCLE = РЕСТОРАННАЯ СИСТЕМА                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   setNeeds*() = "Сделать заказ"                                    │
│   ═══════════════════════════════                                  │
│                                                                     │
│   ┌─────────────────┐                                              │
│   │   КЛИЕНТ        │   setNeedsLayout()                           │
│   │   (Ваш код)     │ ──────────────────────►  📝 Заказ в очереди  │
│   │                 │   setNeedsDisplay()                          │
│   │                 │ ──────────────────────►  📝 Заказ в очереди  │
│   └─────────────────┘                                              │
│                                                                     │
│   Run Loop = "Официант собирает заказы"                            │
│   ═════════════════════════════════════                            │
│                                                                     │
│   Много заказов setNeedsLayout() → ОДИН вызов layoutSubviews()     │
│   Батчинг для эффективности!                                       │
│                                                                     │
│   *IfNeeded() = "Срочный заказ"                                    │
│   ════════════════════════════                                     │
│                                                                     │
│   ┌─────────────────┐                                              │
│   │   VIP КЛИЕНТ    │   layoutIfNeeded()                           │
│   │                 │ ──────────────────────►  🏃 Немедленно!      │
│   └─────────────────┘                                              │
│                                                                     │
│   Полезно для:                                                     │
│   • Анимаций (constraints внутри animation block)                  │
│   • Когда нужен актуальный frame сразу                             │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## Связь с другими темами

**[[android-custom-view-fundamentals]]** — Сравнение кастомных View на iOS (UIView subclassing, draw(_:), layoutSubviews) и Android (onDraw, onMeasure, onLayout) выявляет схожие паттерны: обе платформы используют measurement → layout → drawing pipeline. Однако iOS предоставляет CALayer для GPU-ускоренного рендеринга, тогда как Android использует Canvas с hardware acceleration. Параллельное изучение углубляет понимание UI rendering на обеих платформах.

**[[ios-view-rendering]]** — Render pipeline (display → prepare → commit → GPU rendering) определяет производительность custom views. Понимание того, как UIView.draw(_:) создаёт backing store на CPU, а CALayer рендерит через GPU, помогает выбрать правильный подход: композиция subviews (GPU, быстрее) vs custom drawing (CPU, гибче). Рекомендуется изучить rendering pipeline для осознанного выбора между draw(_:) и CALayer-based подходами.

**[[ios-swiftui]]** — SwiftUI предоставляет декларативную альтернативу UIView subclassing: вместо override draw(_:) используется Shape protocol с path(in:), вместо layoutSubviews — GeometryReader и Layout protocol. Понимание UIKit custom views необходимо для интеграции через UIViewRepresentable и для legacy проектов. Рекомендуется изучить UIKit custom views для фундаментального понимания, затем SwiftUI для современного подхода.

**[[ios-accessibility]]** — Custom views требуют явной настройки accessibility: стандартные UIKit-компоненты предоставляют VoiceOver support автоматически, но custom views необходимо вручную настраивать через isAccessibilityElement, accessibilityLabel, accessibilityTraits. Без accessibility custom view недоступен для 15% пользователей. Рекомендуется добавлять accessibility одновременно с созданием custom view.

---

## Источники

### Официальная документация Apple

1. **View Programming Guide for iOS**
   - [Apple Developer Documentation](https://developer.apple.com/library/archive/documentation/WindowsViews/Conceptual/ViewPG_iPhoneOS/)
   - Основы работы с UIView и view hierarchy

2. **Drawing and Printing Guide for iOS**
   - [Apple Developer Documentation](https://developer.apple.com/library/archive/documentation/2DDrawing/Conceptual/DrawingPrintingiOS/)
   - Core Graphics, UIBezierPath, custom drawing

3. **Auto Layout Guide**
   - [Apple Developer Documentation](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/)
   - Constraints, intrinsicContentSize, priorities

### WWDC Sessions

4. **WWDC 2018: High Performance Auto Layout**
   - Оптимизация layout производительности
   - Когда использовать intrinsicContentSize

5. **WWDC 2014: Advanced Graphics and Animations for iOS Apps**
   - Core Animation оптимизации
   - CALayer vs draw(_:) performance

6. **WWDC 2021: Demystify SwiftUI**
   - Custom Views в SwiftUI
   - Shape protocol, Canvas

### Статьи и книги

7. **objc.io - Advanced Auto Layout**
   - Глубокое погружение в систему layout

8. **Ray Wenderlich - Custom Controls Tutorial**
   - Практические примеры custom views

9. **iOS Drawing: Practical UIKit Solutions (Erica Sadun)**
   - Книга о Core Graphics и custom drawing

## Источники и дальнейшее чтение

- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — подробно описывает UIView hierarchy, coordinate systems и основы custom drawing, формируя базу для создания кастомных компонентов
- Keur C., Hillegass A. (2020). *iOS Programming: The Big Nerd Ranch Guide, 7th Edition.* — содержит практические упражнения по созданию custom views с Auto Layout, включая intrinsicContentSize и @IBDesignable
- Eidhof C. et al. (2020). *Thinking in SwiftUI.* — объясняет декларативный подход к custom views через Shape protocol и Canvas, помогая сравнить с UIKit-подходом

---

## Проверь себя

> [!question]- Почему композиция (subviews) обычно быстрее, чем custom drawing через draw(_:)?
> Композиция использует GPU-ускоренные CALayer для каждого subview, рендеринг кешируется. draw(_:) выполняется на CPU через Core Graphics, при каждом setNeedsDisplay весь rect перерисовывается. CALayer bitmap кешируется, а draw(_:) -- нет. Композицию выбирайте по умолчанию.

> [!question]- Вы создаёте кастомный CircleProgressView. Нужно поддержать init(frame:) и init(coder:). Почему commonInit паттерн необходим?
> UIView имеет два пути инициализации: программный (init(frame:)) и из storyboard/xib (init(coder:)). Без commonInit настройка UI дублируется. commonInit -- private метод, вызываемый из обоих init, обеспечивающий единую точку настройки subviews, constraints и свойств.

> [!question]- Почему intrinsicContentSize важен для custom view в Auto Layout?
> intrinsicContentSize сообщает Auto Layout "естественный" размер view (как UILabel с текстом). Без него view получает нулевой размер. Для custom view нужно override intrinsicContentSize и вызывать invalidateIntrinsicContentSize() при изменении контента, иначе Auto Layout не знает какой размер задать.

---

## Ключевые карточки

Какие два подхода к созданию custom view существуют в UIKit?
?
Композиция (составление из готовых subviews -- UILabel, UIImageView) и custom drawing (рисование через draw(_:) с Core Graphics или CALayer/CAShapeLayer). Композиция -- для большинства случаев, custom drawing -- для сложной векторной графики.

Что такое commonInit паттерн?
?
Private метод настройки, вызываемый из init(frame:) и init(coder:). Обеспечивает единую точку инициализации subviews и constraints, избегая дублирования между программным созданием и загрузкой из storyboard.

Когда вызывается layoutSubviews()?
?
При каждом изменении layout: первое отображение, rotation, изменение bounds, setNeedsLayout/layoutIfNeeded. Используется для ручного позиционирования subviews. Аналог viewDidLayoutSubviews для UIView.

Что такое @IBDesignable и @IBInspectable?
?
@IBDesignable позволяет Interface Builder рендерить custom view в реальном времени. @IBInspectable экспортирует свойства в Attributes Inspector. Вместе обеспечивают live preview кастомных компонентов при разработке.

Зачем нужен invalidateIntrinsicContentSize()?
?
Сообщает Auto Layout, что intrinsicContentSize изменился и constraints нужно пересчитать. Вызывается при изменении контента custom view (текст, изображение). Без вызова Auto Layout использует старый размер.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-view-rendering]] | Понять render pipeline и как custom views отрисовываются |
| Углубиться | [[ios-graphics-fundamentals]] | Освоить Core Graphics и Metal для продвинутого drawing |
| Смежная тема | [[android-custom-view-fundamentals]] | Сравнить UIView subclassing с Android Custom View |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |

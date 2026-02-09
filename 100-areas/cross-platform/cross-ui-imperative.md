---
title: "Cross-Platform: Imperative UI — UIKit vs Android Views"
created: 2026-01-11
type: comparison
tags: [cross-platform, uikit, android-views, ui]
---

# Imperative UI: UIKit vs Android Views

## TL;DR

| Аспект | UIKit (iOS) | Android Views |
|--------|-------------|---------------|
| **Базовый класс** | `UIView` | `View` |
| **Контейнер** | `UIViewController` | `Activity` / `Fragment` |
| **Разметка** | Storyboard / XIB / код | XML / код |
| **Система лейаутов** | Auto Layout (constraints) | ConstraintLayout / LinearLayout / etc. |
| **Списки** | `UITableView` / `UICollectionView` | `RecyclerView` |
| **Переиспользование ячеек** | `dequeueReusableCell` | `ViewHolder` pattern |
| **Жизненный цикл** | `viewDidLoad`, `viewWillAppear`... | `onCreate`, `onResume`... |
| **Обработка касаний** | `UIGestureRecognizer` / `touchesBegan` | `OnTouchListener` / `GestureDetector` |
| **Анимации** | `UIView.animate` / Core Animation | `ObjectAnimator` / `ViewPropertyAnimator` |
| **Темы и стили** | `UIAppearance` | `styles.xml` / `themes.xml` |
| **Навигация** | `UINavigationController` | `NavController` / Intent |
| **Биндинг данных** | Ручной / RxSwift / Combine | ViewBinding / DataBinding |

---

## 1. Почему Imperative UI всё ещё актуален

### Легаси-код никуда не денется

```
Реальность индустрии:
├── 70%+ существующих iOS-приложений используют UIKit
├── 80%+ Android-приложений написаны на Views
├── Миграция на SwiftUI/Compose занимает годы
└── Многие компании не планируют полную миграцию
```

### Производительность в критичных сценариях

```swift
// UIKit: прямой контроль над rendering pipeline
class CustomDrawingView: UIView {
    override func draw(_ rect: CGRect) {
        // Прямой доступ к Core Graphics
        guard let context = UIGraphicsGetCurrentContext() else { return }

        // Оптимизированная отрисовка без overhead декларативного UI
        context.setFillColor(UIColor.red.cgColor)
        context.fill(rect)
    }
}
```

```kotlin
// Android: Custom View с прямым доступом к Canvas
class CustomDrawingView(context: Context) : View(context) {
    private val paint = Paint().apply {
        color = Color.RED
        style = Paint.Style.FILL
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Прямой контроль над отрисовкой
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    }
}
```

### Зрелость экосистемы

| Критерий | Imperative UI | Declarative UI |
|----------|---------------|----------------|
| Документация | Обширная, проверенная временем | Растущая, но с пробелами |
| Stack Overflow | Миллионы ответов | Тысячи ответов |
| Библиотеки | Огромный выбор | Ограниченный выбор |
| Инструменты отладки | Зрелые (View Debugger, Layout Inspector) | Развивающиеся |
| Edge cases | Хорошо задокументированы | Часто неизвестны |

### Когда imperative UI — правильный выбор

```
✅ Сложные кастомные анимации
✅ Игры и графические приложения
✅ Приложения с интенсивной работой со списками
✅ Интеграция с legacy-кодом
✅ Низкоуровневый контроль над UI
✅ Команда с глубокой экспертизой в UIKit/Views
```

---

## 2. Пять ключевых аналогий

### Аналогия 1: View = UIView

```swift
// iOS: UIView — базовый строительный блок
let view = UIView(frame: CGRect(x: 0, y: 0, width: 100, height: 100))
view.backgroundColor = .blue
view.layer.cornerRadius = 8
view.clipsToBounds = true
parentView.addSubview(view)
```

```kotlin
// Android: View — базовый строительный блок
val view = View(context).apply {
    layoutParams = ViewGroup.LayoutParams(100.dp, 100.dp)
    setBackgroundColor(Color.BLUE)
    background = GradientDrawable().apply {
        cornerRadius = 8f.dp
    }
}
parentView.addView(view)
```

### Аналогия 2: Activity/Fragment = UIViewController

```swift
// iOS: UIViewController управляет экраном
class ProfileViewController: UIViewController {

    private let profileImageView = UIImageView()
    private let nameLabel = UILabel()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupViews()
        loadData()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        refreshData()
    }

    private func setupViews() {
        view.addSubview(profileImageView)
        view.addSubview(nameLabel)
    }
}
```

```kotlin
// Android: Activity/Fragment управляет экраном
class ProfileActivity : AppCompatActivity() {

    private lateinit var profileImageView: ImageView
    private lateinit var nameLabel: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)
        setupViews()
        loadData()
    }

    override fun onResume() {
        super.onResume()
        refreshData()
    }

    private fun setupViews() {
        profileImageView = findViewById(R.id.profileImageView)
        nameLabel = findViewById(R.id.nameLabel)
    }
}
```

### Аналогия 3: LinearLayout = UIStackView

```swift
// iOS: UIStackView для линейного расположения
let stackView = UIStackView()
stackView.axis = .vertical
stackView.spacing = 16
stackView.alignment = .fill
stackView.distribution = .fillEqually

stackView.addArrangedSubview(button1)
stackView.addArrangedSubview(button2)
stackView.addArrangedSubview(button3)
```

```xml
<!-- Android: LinearLayout для линейного расположения -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:gravity="center">

    <Button
        android:id="@+id/button1"
        android:layout_width="match_parent"
        android:layout_height="48dp" />

    <Button
        android:id="@+id/button2"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:layout_marginTop="16dp" />

    <Button
        android:id="@+id/button3"
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:layout_marginTop="16dp" />
</LinearLayout>
```

### Аналогия 4: ConstraintLayout = Auto Layout

```swift
// iOS: Auto Layout constraints
let blueView = UIView()
blueView.backgroundColor = .blue
blueView.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(blueView)

NSLayoutConstraint.activate([
    blueView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    blueView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
    blueView.widthAnchor.constraint(equalToConstant: 200),
    blueView.heightAnchor.constraint(equalToConstant: 100)
])
```

```xml
<!-- Android: ConstraintLayout constraints -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <View
        android:id="@+id/blueView"
        android:layout_width="200dp"
        android:layout_height="100dp"
        android:background="@color/blue"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### Аналогия 5: Intent = Segue/Navigation

```swift
// iOS: Навигация между экранами
// Программная навигация
let detailVC = DetailViewController()
detailVC.itemId = selectedItem.id
navigationController?.pushViewController(detailVC, animated: true)

// Или через Storyboard segue
override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
    if let detailVC = segue.destination as? DetailViewController {
        detailVC.itemId = selectedItem.id
    }
}
```

```kotlin
// Android: Навигация между экранами
// Intent для перехода между Activity
val intent = Intent(this, DetailActivity::class.java).apply {
    putExtra("ITEM_ID", selectedItem.id)
}
startActivity(intent)

// Или Navigation Component
findNavController().navigate(
    R.id.action_list_to_detail,
    bundleOf("itemId" to selectedItem.id)
)
```

---

## 3. View Hierarchies: UIView vs View

### Иерархия классов

```
iOS UIKit:                          Android Views:

UIResponder                         Object
    └── UIView                          └── View
            ├── UIControl                       ├── TextView
            │       ├── UIButton                │       └── EditText
            │       ├── UITextField             │       └── Button
            │       ├── UISwitch                ├── ImageView
            │       └── UISlider                ├── ViewGroup
            ├── UILabel                         │       ├── LinearLayout
            ├── UIImageView                     │       ├── FrameLayout
            ├── UIScrollView                    │       ├── RelativeLayout
            │       ├── UITableView             │       ├── ConstraintLayout
            │       └── UICollectionView        │       └── RecyclerView
            └── UIStackView                     └── ProgressBar
```

### Создание кастомного View

```swift
// iOS: Кастомный UIView
class GradientView: UIView {

    private var gradientLayer: CAGradientLayer?

    var colors: [UIColor] = [.blue, .purple] {
        didSet { updateGradient() }
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupGradient()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupGradient()
    }

    private func setupGradient() {
        let gradient = CAGradientLayer()
        gradient.startPoint = CGPoint(x: 0, y: 0)
        gradient.endPoint = CGPoint(x: 1, y: 1)
        layer.insertSublayer(gradient, at: 0)
        gradientLayer = gradient
        updateGradient()
    }

    private func updateGradient() {
        gradientLayer?.colors = colors.map { $0.cgColor }
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        gradientLayer?.frame = bounds
    }
}
```

```kotlin
// Android: Кастомный View
class GradientView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    var colors: IntArray = intArrayOf(Color.BLUE, Color.MAGENTA)
        set(value) {
            field = value
            updateGradient()
        }

    private var gradientDrawable: GradientDrawable? = null

    init {
        setupGradient()
    }

    private fun setupGradient() {
        gradientDrawable = GradientDrawable(
            GradientDrawable.Orientation.TL_BR,
            colors
        )
        background = gradientDrawable
    }

    private fun updateGradient() {
        gradientDrawable?.colors = colors
        invalidate()
    }
}
```

### Жизненный цикл View

```swift
// iOS: Жизненный цикл UIView
class LifecycleView: UIView {

    // 1. Инициализация
    override init(frame: CGRect) {
        super.init(frame: frame)
        // Начальная настройка
    }

    // 2. Добавление в иерархию
    override func didMoveToSuperview() {
        super.didMoveToSuperview()
        if superview != nil {
            // View добавлен в иерархию
        } else {
            // View удалён из иерархии
        }
    }

    // 3. Layout
    override func layoutSubviews() {
        super.layoutSubviews()
        // Обновление позиций subviews
    }

    // 4. Отрисовка
    override func draw(_ rect: CGRect) {
        // Кастомная отрисовка
    }
}
```

```kotlin
// Android: Жизненный цикл View
class LifecycleView(context: Context) : View(context) {

    // 1. Инициализация в конструкторе
    init {
        // Начальная настройка
    }

    // 2. Добавление в иерархию
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // View добавлен в иерархию
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // View удалён из иерархии
    }

    // 3. Измерение
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
        // Определение размеров
    }

    // 4. Layout
    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        super.onLayout(changed, left, top, right, bottom)
        // Позиционирование children
    }

    // 5. Отрисовка
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Кастомная отрисовка
    }
}
```

---

## 4. Layout Systems: Auto Layout vs ConstraintLayout

### Философия подхода

| Аспект | Auto Layout (iOS) | ConstraintLayout (Android) |
|--------|-------------------|----------------------------|
| Основа | Система линейных уравнений (Cassowary) | Система constraints с оптимизацией |
| Приоритеты | 1-1000 (required = 1000) | Нет числовых приоритетов |
| Chains | Нет нативной поддержки | Встроенные chains |
| Guidelines | Нет | Есть (vertical/horizontal) |
| Barriers | Нет | Есть |
| Groups | Нет | Есть |
| Aspect Ratio | Через constraints | Встроенная поддержка |

### Сравнение синтаксиса

```swift
// iOS: Auto Layout программно
class LayoutViewController: UIViewController {

    private let headerView = UIView()
    private let contentView = UIView()
    private let footerView = UIView()

    override func viewDidLoad() {
        super.viewDidLoad()

        [headerView, contentView, footerView].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            view.addSubview($0)
        }

        headerView.backgroundColor = .systemBlue
        contentView.backgroundColor = .systemGray6
        footerView.backgroundColor = .systemGreen

        NSLayoutConstraint.activate([
            // Header: top, full width, fixed height
            headerView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            headerView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            headerView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            headerView.heightAnchor.constraint(equalToConstant: 60),

            // Content: between header and footer
            contentView.topAnchor.constraint(equalTo: headerView.bottomAnchor),
            contentView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: footerView.topAnchor),

            // Footer: bottom, full width, fixed height
            footerView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
            footerView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            footerView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            footerView.heightAnchor.constraint(equalToConstant: 50)
        ])
    }
}
```

```xml
<!-- Android: ConstraintLayout в XML -->
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Header: top, full width, fixed height -->
    <View
        android:id="@+id/headerView"
        android:layout_width="0dp"
        android:layout_height="60dp"
        android:background="@color/blue"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <!-- Content: between header and footer -->
    <View
        android:id="@+id/contentView"
        android:layout_width="0dp"
        android:layout_height="0dp"
        android:background="@color/gray"
        app:layout_constraintTop_toBottomOf="@id/headerView"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintBottom_toTopOf="@id/footerView" />

    <!-- Footer: bottom, full width, fixed height -->
    <View
        android:id="@+id/footerView"
        android:layout_width="0dp"
        android:layout_height="50dp"
        android:background="@color/green"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### Продвинутые возможности ConstraintLayout

```xml
<!-- Android: Chains, Guidelines, Barriers -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Guideline: вертикальная линия на 30% ширины -->
    <androidx.constraintlayout.widget.Guideline
        android:id="@+id/guideline"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        app:layout_constraintGuide_percent="0.3" />

    <!-- Chain: горизонтальное распределение кнопок -->
    <Button
        android:id="@+id/btn1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="One"
        app:layout_constraintHorizontal_chainStyle="spread"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toStartOf="@id/btn2"
        app:layout_constraintTop_toTopOf="parent" />

    <Button
        android:id="@+id/btn2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Two"
        app:layout_constraintStart_toEndOf="@id/btn1"
        app:layout_constraintEnd_toStartOf="@id/btn3"
        app:layout_constraintTop_toTopOf="parent" />

    <Button
        android:id="@+id/btn3"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Three"
        app:layout_constraintStart_toEndOf="@id/btn2"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <!-- Barrier: граница справа от самого широкого элемента -->
    <androidx.constraintlayout.widget.Barrier
        android:id="@+id/barrier"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:barrierDirection="end"
        app:constraint_referenced_ids="label1,label2,label3" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

---

## 5. XML vs Storyboards vs Programmatic

### Сравнение подходов

| Критерий | Storyboard/XIB | Android XML | Программный код |
|----------|----------------|-------------|-----------------|
| **Визуальный редактор** | Да | Да | Нет |
| **Merge conflicts** | Сложные | Умеренные | Простые |
| **Переиспользование** | Низкое | Высокое (include) | Очень высокое |
| **Производительность** | Overhead при загрузке | Inflation overhead | Лучшая |
| **Type safety** | Нет (runtime crashes) | Нет (runtime crashes) | Да |
| **Рефакторинг** | Сложный | Умеренный | Простой |
| **Командная работа** | Проблематичная | Нормальная | Хорошая |

### Storyboard (iOS)

```swift
// Загрузка ViewController из Storyboard
let storyboard = UIStoryboard(name: "Main", bundle: nil)
let vc = storyboard.instantiateViewController(withIdentifier: "ProfileVC")
    as! ProfileViewController

// Segue в Storyboard (определяется визуально)
// Подготовка данных
override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
    if segue.identifier == "showDetail" {
        let detailVC = segue.destination as! DetailViewController
        detailVC.item = selectedItem
    }
}
```

### XML Layout (Android)

```xml
<!-- res/layout/activity_profile.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <!-- Include переиспользуемого компонента -->
    <include layout="@layout/component_header" />

    <ImageView
        android:id="@+id/profileImage"
        android:layout_width="120dp"
        android:layout_height="120dp"
        android:layout_gravity="center_horizontal" />

    <TextView
        android:id="@+id/nameText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center_horizontal"
        android:textSize="24sp" />

</LinearLayout>
```

```kotlin
// Использование XML layout
class ProfileActivity : AppCompatActivity() {

    private lateinit var binding: ActivityProfileBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ViewBinding (рекомендуемый способ)
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.nameText.text = "John Doe"
        binding.profileImage.setImageResource(R.drawable.avatar)
    }
}
```

### Программный подход

```swift
// iOS: Полностью программный UI
class ProgrammaticViewController: UIViewController {

    private lazy var profileImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFill
        imageView.clipsToBounds = true
        imageView.layer.cornerRadius = 60
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()

    private lazy var nameLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 24, weight: .bold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private lazy var actionButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Edit Profile", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 16, weight: .medium)
        button.addTarget(self, action: #selector(editTapped), for: .touchUpInside)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
    }

    private func setupUI() {
        view.backgroundColor = .systemBackground
        [profileImageView, nameLabel, actionButton].forEach {
            view.addSubview($0)
        }
    }

    private func setupConstraints() {
        NSLayoutConstraint.activate([
            profileImageView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            profileImageView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 40),
            profileImageView.widthAnchor.constraint(equalToConstant: 120),
            profileImageView.heightAnchor.constraint(equalToConstant: 120),

            nameLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            nameLabel.topAnchor.constraint(equalTo: profileImageView.bottomAnchor, constant: 16),

            actionButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            actionButton.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 24)
        ])
    }

    @objc private func editTapped() {
        // Handle tap
    }
}
```

```kotlin
// Android: Полностью программный UI
class ProgrammaticActivity : AppCompatActivity() {

    private lateinit var profileImageView: ImageView
    private lateinit var nameTextView: TextView
    private lateinit var actionButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val rootLayout = ConstraintLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
        }

        profileImageView = ImageView(this).apply {
            id = View.generateViewId()
            scaleType = ImageView.ScaleType.CENTER_CROP
            layoutParams = ConstraintLayout.LayoutParams(120.dp, 120.dp)
        }

        nameTextView = TextView(this).apply {
            id = View.generateViewId()
            textSize = 24f
            setTypeface(typeface, Typeface.BOLD)
            gravity = Gravity.CENTER
            layoutParams = ConstraintLayout.LayoutParams(
                ConstraintLayout.LayoutParams.WRAP_CONTENT,
                ConstraintLayout.LayoutParams.WRAP_CONTENT
            )
        }

        actionButton = Button(this).apply {
            id = View.generateViewId()
            text = "Edit Profile"
            setOnClickListener { editTapped() }
            layoutParams = ConstraintLayout.LayoutParams(
                ConstraintLayout.LayoutParams.WRAP_CONTENT,
                ConstraintLayout.LayoutParams.WRAP_CONTENT
            )
        }

        rootLayout.addView(profileImageView)
        rootLayout.addView(nameTextView)
        rootLayout.addView(actionButton)

        setupConstraints(rootLayout)
        setContentView(rootLayout)
    }

    private fun setupConstraints(layout: ConstraintLayout) {
        ConstraintSet().apply {
            clone(layout)

            // Profile image
            connect(profileImageView.id, ConstraintSet.TOP, ConstraintSet.PARENT_ID, ConstraintSet.TOP, 40.dp)
            connect(profileImageView.id, ConstraintSet.START, ConstraintSet.PARENT_ID, ConstraintSet.START)
            connect(profileImageView.id, ConstraintSet.END, ConstraintSet.PARENT_ID, ConstraintSet.END)

            // Name
            connect(nameTextView.id, ConstraintSet.TOP, profileImageView.id, ConstraintSet.BOTTOM, 16.dp)
            connect(nameTextView.id, ConstraintSet.START, ConstraintSet.PARENT_ID, ConstraintSet.START)
            connect(nameTextView.id, ConstraintSet.END, ConstraintSet.PARENT_ID, ConstraintSet.END)

            // Button
            connect(actionButton.id, ConstraintSet.TOP, nameTextView.id, ConstraintSet.BOTTOM, 24.dp)
            connect(actionButton.id, ConstraintSet.START, ConstraintSet.PARENT_ID, ConstraintSet.START)
            connect(actionButton.id, ConstraintSet.END, ConstraintSet.PARENT_ID, ConstraintSet.END)

            applyTo(layout)
        }
    }

    private fun editTapped() {
        // Handle tap
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
```

---

## 6. RecyclerView vs UITableView/UICollectionView

### Архитектура переиспользования ячеек

```
iOS UITableView:                    Android RecyclerView:

┌─────────────────────┐            ┌─────────────────────┐
│  UITableView        │            │  RecyclerView       │
│  ├── DataSource     │            │  ├── Adapter        │
│  │   └── cellForRow │            │  │   └── onBind     │
│  ├── Delegate       │            │  ├── ViewHolder     │
│  │   └── didSelect  │            │  │   └── itemView   │
│  └── Cell Reuse     │            │  └── LayoutManager  │
│      └── dequeue    │            │      └── Linear/Grid│
└─────────────────────┘            └─────────────────────┘
```

### UITableView (iOS)

```swift
// iOS: UITableView с переиспользованием ячеек
class ContactsViewController: UIViewController {

    private var contacts: [Contact] = []

    private lazy var tableView: UITableView = {
        let table = UITableView(frame: .zero, style: .plain)
        table.register(ContactCell.self, forCellReuseIdentifier: ContactCell.reuseIdentifier)
        table.dataSource = self
        table.delegate = self
        table.translatesAutoresizingMaskIntoConstraints = false
        return table
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupTableView()
        loadContacts()
    }

    private func setupTableView() {
        view.addSubview(tableView)
        NSLayoutConstraint.activate([
            tableView.topAnchor.constraint(equalTo: view.topAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
    }
}

extension ContactsViewController: UITableViewDataSource {

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return contacts.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(
            withIdentifier: ContactCell.reuseIdentifier,
            for: indexPath
        ) as! ContactCell

        let contact = contacts[indexPath.row]
        cell.configure(with: contact)
        return cell
    }
}

extension ContactsViewController: UITableViewDelegate {

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let contact = contacts[indexPath.row]
        showContactDetail(contact)
    }
}

// Кастомная ячейка
class ContactCell: UITableViewCell {

    static let reuseIdentifier = "ContactCell"

    private let avatarImageView = UIImageView()
    private let nameLabel = UILabel()
    private let emailLabel = UILabel()

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupViews()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    private func setupViews() {
        [avatarImageView, nameLabel, emailLabel].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            contentView.addSubview($0)
        }

        avatarImageView.layer.cornerRadius = 20
        avatarImageView.clipsToBounds = true

        nameLabel.font = .systemFont(ofSize: 16, weight: .semibold)
        emailLabel.font = .systemFont(ofSize: 14)
        emailLabel.textColor = .secondaryLabel

        NSLayoutConstraint.activate([
            avatarImageView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            avatarImageView.centerYAnchor.constraint(equalTo: contentView.centerYAnchor),
            avatarImageView.widthAnchor.constraint(equalToConstant: 40),
            avatarImageView.heightAnchor.constraint(equalToConstant: 40),

            nameLabel.leadingAnchor.constraint(equalTo: avatarImageView.trailingAnchor, constant: 12),
            nameLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 12),
            nameLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),

            emailLabel.leadingAnchor.constraint(equalTo: nameLabel.leadingAnchor),
            emailLabel.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 4),
            emailLabel.trailingAnchor.constraint(equalTo: nameLabel.trailingAnchor),
            emailLabel.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -12)
        ])
    }

    func configure(with contact: Contact) {
        avatarImageView.image = contact.avatar
        nameLabel.text = contact.name
        emailLabel.text = contact.email
    }

    override func prepareForReuse() {
        super.prepareForReuse()
        avatarImageView.image = nil
        nameLabel.text = nil
        emailLabel.text = nil
    }
}
```

### RecyclerView (Android)

```kotlin
// Android: RecyclerView с ViewHolder паттерном
class ContactsActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private val contactsAdapter = ContactsAdapter { contact ->
        showContactDetail(contact)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_contacts)

        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.apply {
            layoutManager = LinearLayoutManager(this@ContactsActivity)
            adapter = contactsAdapter

            // Оптимизации
            setHasFixedSize(true)
            itemAnimator = DefaultItemAnimator()
        }

        loadContacts()
    }

    private fun loadContacts() {
        // Загрузка данных
        contactsAdapter.submitList(contacts)
    }
}

// Adapter с ListAdapter для DiffUtil
class ContactsAdapter(
    private val onItemClick: (Contact) -> Unit
) : ListAdapter<Contact, ContactsAdapter.ContactViewHolder>(ContactDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ContactViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_contact, parent, false)
        return ContactViewHolder(view, onItemClick)
    }

    override fun onBindViewHolder(holder: ContactViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ContactViewHolder(
        itemView: View,
        private val onItemClick: (Contact) -> Unit
    ) : RecyclerView.ViewHolder(itemView) {

        private val avatarImageView: ImageView = itemView.findViewById(R.id.avatarImageView)
        private val nameTextView: TextView = itemView.findViewById(R.id.nameTextView)
        private val emailTextView: TextView = itemView.findViewById(R.id.emailTextView)

        private var currentContact: Contact? = null

        init {
            itemView.setOnClickListener {
                currentContact?.let(onItemClick)
            }
        }

        fun bind(contact: Contact) {
            currentContact = contact
            avatarImageView.setImageDrawable(contact.avatar)
            nameTextView.text = contact.name
            emailTextView.text = contact.email
        }
    }
}

// DiffUtil для эффективного обновления
class ContactDiffCallback : DiffUtil.ItemCallback<Contact>() {

    override fun areItemsTheSame(oldItem: Contact, newItem: Contact): Boolean {
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: Contact, newItem: Contact): Boolean {
        return oldItem == newItem
    }
}
```

```xml
<!-- res/layout/item_contact.xml -->
<?xml version="1.0" encoding="utf-8"?>
<ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:padding="16dp">

    <ImageView
        android:id="@+id/avatarImageView"
        android:layout_width="40dp"
        android:layout_height="40dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent" />

    <TextView
        android:id="@+id/nameTextView"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="12dp"
        android:textSize="16sp"
        android:textStyle="bold"
        app:layout_constraintStart_toEndOf="@id/avatarImageView"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/emailTextView"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="12dp"
        android:layout_marginTop="4dp"
        android:textSize="14sp"
        android:textColor="@color/secondary_text"
        app:layout_constraintStart_toEndOf="@id/avatarImageView"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toBottomOf="@id/nameTextView" />

</ConstraintLayout>
```

---

## 7. Touch Handling

### Система обработки касаний

```
iOS Touch Handling:                 Android Touch Handling:

UIResponder chain:                  ViewGroup dispatch:
┌────────────────────┐              ┌────────────────────┐
│ UIApplication      │              │ Activity           │
│      ↓             │              │      ↓             │
│ UIWindow           │              │ ViewGroup          │
│      ↓             │              │ dispatchTouchEvent │
│ UIViewController   │              │      ↓             │
│      ↓             │              │ onInterceptTouch   │
│ UIView (hitTest)   │              │      ↓             │
│      ↓             │              │ Child View         │
│ touchesBegan/Moved │              │ onTouchEvent       │
└────────────────────┘              └────────────────────┘
```

### Gesture Recognizers (iOS)

```swift
// iOS: UIGestureRecognizer
class GestureViewController: UIViewController {

    private let targetView = UIView()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupGestures()
    }

    private func setupGestures() {
        // Tap gesture
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        tapGesture.numberOfTapsRequired = 1
        targetView.addGestureRecognizer(tapGesture)

        // Double tap
        let doubleTapGesture = UITapGestureRecognizer(target: self, action: #selector(handleDoubleTap(_:)))
        doubleTapGesture.numberOfTapsRequired = 2
        targetView.addGestureRecognizer(doubleTapGesture)

        // Single tap должен ждать провала double tap
        tapGesture.require(toFail: doubleTapGesture)

        // Long press
        let longPressGesture = UILongPressGestureRecognizer(target: self, action: #selector(handleLongPress(_:)))
        longPressGesture.minimumPressDuration = 0.5
        targetView.addGestureRecognizer(longPressGesture)

        // Pan (drag)
        let panGesture = UIPanGestureRecognizer(target: self, action: #selector(handlePan(_:)))
        targetView.addGestureRecognizer(panGesture)

        // Pinch (zoom)
        let pinchGesture = UIPinchGestureRecognizer(target: self, action: #selector(handlePinch(_:)))
        targetView.addGestureRecognizer(pinchGesture)

        // Rotation
        let rotationGesture = UIRotationGestureRecognizer(target: self, action: #selector(handleRotation(_:)))
        targetView.addGestureRecognizer(rotationGesture)

        // Pinch и rotation могут работать одновременно
        pinchGesture.delegate = self
        rotationGesture.delegate = self
    }

    @objc private func handleTap(_ gesture: UITapGestureRecognizer) {
        let location = gesture.location(in: targetView)
        print("Tap at: \(location)")
    }

    @objc private func handleDoubleTap(_ gesture: UITapGestureRecognizer) {
        print("Double tap!")
    }

    @objc private func handleLongPress(_ gesture: UILongPressGestureRecognizer) {
        switch gesture.state {
        case .began:
            print("Long press began")
        case .ended:
            print("Long press ended")
        default:
            break
        }
    }

    @objc private func handlePan(_ gesture: UIPanGestureRecognizer) {
        let translation = gesture.translation(in: view)

        if let view = gesture.view {
            view.center = CGPoint(
                x: view.center.x + translation.x,
                y: view.center.y + translation.y
            )
        }

        gesture.setTranslation(.zero, in: view)
    }

    @objc private func handlePinch(_ gesture: UIPinchGestureRecognizer) {
        if let view = gesture.view {
            view.transform = view.transform.scaledBy(x: gesture.scale, y: gesture.scale)
        }
        gesture.scale = 1.0
    }

    @objc private func handleRotation(_ gesture: UIRotationGestureRecognizer) {
        if let view = gesture.view {
            view.transform = view.transform.rotated(by: gesture.rotation)
        }
        gesture.rotation = 0
    }
}

extension GestureViewController: UIGestureRecognizerDelegate {
    func gestureRecognizer(
        _ gestureRecognizer: UIGestureRecognizer,
        shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer
    ) -> Bool {
        return true
    }
}
```

### Touch Listeners (Android)

```kotlin
// Android: Touch handling
class GestureActivity : AppCompatActivity() {

    private lateinit var targetView: View
    private lateinit var gestureDetector: GestureDetectorCompat
    private lateinit var scaleGestureDetector: ScaleGestureDetector

    private var scaleFactor = 1f
    private var lastX = 0f
    private var lastY = 0f

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_gesture)

        targetView = findViewById(R.id.targetView)
        setupGestureDetectors()
        setupTouchListener()
    }

    private fun setupGestureDetectors() {
        // GestureDetector для tap, double tap, long press, fling
        gestureDetector = GestureDetectorCompat(this, object : GestureDetector.SimpleOnGestureListener() {

            override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
                Log.d("Gesture", "Single tap at: ${e.x}, ${e.y}")
                return true
            }

            override fun onDoubleTap(e: MotionEvent): Boolean {
                Log.d("Gesture", "Double tap!")
                return true
            }

            override fun onLongPress(e: MotionEvent) {
                Log.d("Gesture", "Long press!")
            }

            override fun onScroll(
                e1: MotionEvent?,
                e2: MotionEvent,
                distanceX: Float,
                distanceY: Float
            ): Boolean {
                targetView.translationX -= distanceX
                targetView.translationY -= distanceY
                return true
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                Log.d("Gesture", "Fling! velocity: $velocityX, $velocityY")
                return true
            }
        })

        // ScaleGestureDetector для pinch zoom
        scaleGestureDetector = ScaleGestureDetector(this, object : ScaleGestureDetector.SimpleOnScaleGestureListener() {

            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                scaleFactor = scaleFactor.coerceIn(0.1f, 10f)

                targetView.scaleX = scaleFactor
                targetView.scaleY = scaleFactor
                return true
            }
        })
    }

    private fun setupTouchListener() {
        targetView.setOnTouchListener { view, event ->
            // Передаём событие в gesture detectors
            gestureDetector.onTouchEvent(event)
            scaleGestureDetector.onTouchEvent(event)
            true
        }
    }
}

// Кастомный View с обработкой касаний
class TouchableView(context: Context, attrs: AttributeSet?) : View(context, attrs) {

    private var lastTouchX = 0f
    private var lastTouchY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                lastTouchX = event.x
                lastTouchY = event.y
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastTouchX
                val dy = event.y - lastTouchY

                translationX += dx
                translationY += dy

                // Не обновляем lastTouch, т.к. translation изменилась
                return true
            }

            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                // Обработка завершения касания
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

---

## 8. Шесть типичных ошибок

### Ошибка 1: Забыли translatesAutoresizingMaskIntoConstraints

```swift
// iOS: НЕПРАВИЛЬНО
let label = UILabel()
label.text = "Hello"
view.addSubview(label)

NSLayoutConstraint.activate([
    label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
])
// Constraints конфликтуют с autoresizing mask!

// iOS: ПРАВИЛЬНО
let label = UILabel()
label.text = "Hello"
label.translatesAutoresizingMaskIntoConstraints = false // Обязательно!
view.addSubview(label)

NSLayoutConstraint.activate([
    label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
])
```

```kotlin
// Android: Аналогичная проблема с programmatic layout
// НЕПРАВИЛЬНО - layoutParams не установлены
val textView = TextView(context)
textView.text = "Hello"
constraintLayout.addView(textView)
// View не имеет constraints!

// ПРАВИЛЬНО
val textView = TextView(context).apply {
    id = View.generateViewId() // Нужен ID для constraints
    text = "Hello"
    layoutParams = ConstraintLayout.LayoutParams(
        ConstraintLayout.LayoutParams.WRAP_CONTENT,
        ConstraintLayout.LayoutParams.WRAP_CONTENT
    )
}
constraintLayout.addView(textView)

ConstraintSet().apply {
    clone(constraintLayout)
    connect(textView.id, ConstraintSet.START, ConstraintSet.PARENT_ID, ConstraintSet.START)
    connect(textView.id, ConstraintSet.END, ConstraintSet.PARENT_ID, ConstraintSet.END)
    connect(textView.id, ConstraintSet.TOP, ConstraintSet.PARENT_ID, ConstraintSet.TOP)
    connect(textView.id, ConstraintSet.BOTTOM, ConstraintSet.PARENT_ID, ConstraintSet.BOTTOM)
    applyTo(constraintLayout)
}
```

### Ошибка 2: Обновление UI не на main thread

```swift
// iOS: НЕПРАВИЛЬНО
DispatchQueue.global().async {
    let data = self.fetchData()
    self.tableView.reloadData() // Crash или undefined behavior!
}

// iOS: ПРАВИЛЬНО
DispatchQueue.global().async {
    let data = self.fetchData()
    DispatchQueue.main.async {
        self.data = data
        self.tableView.reloadData() // OK - main thread
    }
}
```

```kotlin
// Android: НЕПРАВИЛЬНО
thread {
    val data = fetchData()
    recyclerView.adapter?.notifyDataSetChanged() // CalledFromWrongThreadException!
}

// Android: ПРАВИЛЬНО
lifecycleScope.launch(Dispatchers.IO) {
    val data = fetchData()
    withContext(Dispatchers.Main) {
        adapter.submitList(data) // OK - main thread
    }
}

// Или с Handler
thread {
    val data = fetchData()
    runOnUiThread {
        adapter.submitList(data)
    }
}
```

### Ошибка 3: Memory leak в closure/listener

```swift
// iOS: НЕПРАВИЛЬНО - retain cycle
class ProfileViewController: UIViewController {

    private var viewModel: ProfileViewModel!

    override func viewDidLoad() {
        super.viewDidLoad()

        // self захватывается сильной ссылкой
        viewModel.onDataLoaded = { data in
            self.updateUI(with: data) // Retain cycle!
        }
    }
}

// iOS: ПРАВИЛЬНО - weak self
class ProfileViewController: UIViewController {

    private var viewModel: ProfileViewModel!

    override func viewDidLoad() {
        super.viewDidLoad()

        viewModel.onDataLoaded = { [weak self] data in
            self?.updateUI(with: data) // OK - weak reference
        }
    }
}
```

```kotlin
// Android: НЕПРАВИЛЬНО - утечка через анонимный класс
class ProfileActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Анонимный класс держит ссылку на Activity
        val handler = Handler(Looper.getMainLooper())
        handler.postDelayed(object : Runnable {
            override fun run() {
                updateUI() // Activity может быть уже уничтожена!
            }
        }, 10000)
    }
}

// Android: ПРАВИЛЬНО - WeakReference или lifecycle-aware
class ProfileActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Используем lifecycleScope - автоматическая отмена
        lifecycleScope.launch {
            delay(10000)
            updateUI() // Безопасно - отменится при destroy
        }
    }
}
```

### Ошибка 4: Неправильное переиспользование ячеек

```swift
// iOS: НЕПРАВИЛЬНО - состояние не сбрасывается
class BadCell: UITableViewCell {

    private let checkmarkView = UIImageView()

    func configure(with item: Item) {
        textLabel?.text = item.title

        if item.isCompleted {
            checkmarkView.isHidden = false
        }
        // Забыли else! Checkmark останется от предыдущей ячейки
    }
}

// iOS: ПРАВИЛЬНО - всегда сбрасываем состояние
class GoodCell: UITableViewCell {

    private let checkmarkView = UIImageView()

    override func prepareForReuse() {
        super.prepareForReuse()
        checkmarkView.isHidden = true
        textLabel?.text = nil
        imageView?.image = nil
    }

    func configure(with item: Item) {
        textLabel?.text = item.title
        checkmarkView.isHidden = !item.isCompleted
    }
}
```

```kotlin
// Android: НЕПРАВИЛЬНО - состояние не сбрасывается
class BadViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

    private val checkmarkView: ImageView = itemView.findViewById(R.id.checkmark)

    fun bind(item: Item) {
        itemView.findViewById<TextView>(R.id.title).text = item.title

        if (item.isCompleted) {
            checkmarkView.visibility = View.VISIBLE
        }
        // Забыли else! Checkmark останется от предыдущей ячейки
    }
}

// Android: ПРАВИЛЬНО - всегда сбрасываем состояние
class GoodViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {

    private val titleView: TextView = itemView.findViewById(R.id.title)
    private val checkmarkView: ImageView = itemView.findViewById(R.id.checkmark)

    fun bind(item: Item) {
        titleView.text = item.title
        checkmarkView.visibility = if (item.isCompleted) View.VISIBLE else View.GONE
    }

    fun unbind() {
        // Вызывается из onViewRecycled в Adapter
        titleView.text = null
        checkmarkView.visibility = View.GONE
    }
}
```

### Ошибка 5: Layout в цикле

```swift
// iOS: НЕПРАВИЛЬНО - layoutIfNeeded в цикле
func updateAllViews() {
    for (index, view) in subviews.enumerated() {
        view.frame.origin.y = CGFloat(index * 50)
        view.layoutIfNeeded() // Каждый вызов пересчитывает весь layout!
    }
}

// iOS: ПРАВИЛЬНО - один layout pass в конце
func updateAllViews() {
    for (index, view) in subviews.enumerated() {
        view.frame.origin.y = CGFloat(index * 50)
    }
    setNeedsLayout() // Помечаем для пересчёта
    layoutIfNeeded() // Один пересчёт в конце
}
```

```kotlin
// Android: НЕПРАВИЛЬНО - requestLayout в цикле
fun updateAllViews() {
    for ((index, view) in children.withIndex()) {
        val params = view.layoutParams as MarginLayoutParams
        params.topMargin = index * 50.dp
        view.layoutParams = params // Каждый раз вызывает requestLayout!
    }
}

// Android: ПРАВИЛЬНО - batch update
fun updateAllViews() {
    // Отключаем layout на время обновления
    suppressLayout(true)

    for ((index, view) in children.withIndex()) {
        val params = view.layoutParams as MarginLayoutParams
        params.topMargin = index * 50.dp
        view.layoutParams = params
    }

    suppressLayout(false)
    requestLayout() // Один пересчёт
}
```

### Ошибка 6: findViewById каждый раз

```swift
// iOS: НЕПРАВИЛЬНО (с Storyboard) - поиск каждый раз
class BadViewController: UIViewController {

    func updateTitle(_ text: String) {
        // Каждый вызов ищет view в иерархии
        if let label = view.viewWithTag(100) as? UILabel {
            label.text = text
        }
    }
}

// iOS: ПРАВИЛЬНО - IBOutlet или lazy property
class GoodViewController: UIViewController {

    @IBOutlet weak var titleLabel: UILabel!

    // Или программно с lazy
    private lazy var titleLabel: UILabel = {
        let label = UILabel()
        // настройка...
        return label
    }()

    func updateTitle(_ text: String) {
        titleLabel.text = text
    }
}
```

```kotlin
// Android: НЕПРАВИЛЬНО - findViewById каждый раз
class BadActivity : AppCompatActivity() {

    fun updateTitle(text: String) {
        // Каждый вызов ищет view в иерархии (O(n))
        findViewById<TextView>(R.id.titleText).text = text
    }
}

// Android: ПРАВИЛЬНО - ViewBinding или кэширование
class GoodActivity : AppCompatActivity() {

    // ViewBinding - рекомендуемый способ
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }

    fun updateTitle(text: String) {
        binding.titleText.text = text // Прямой доступ, без поиска
    }
}
```

---

## 9. Когда использовать Imperative vs Declarative UI

### Матрица принятия решений

| Сценарий | Imperative | Declarative | Причина |
|----------|:----------:|:-----------:|---------|
| Новый проект | - | + | Современный подход, меньше boilerplate |
| Legacy codebase | + | - | Совместимость, постепенная миграция |
| Сложные анимации | + | +/- | Больше контроля в imperative |
| Простые формы | - | + | Проще в декларативном стиле |
| Кастомная отрисовка | + | - | Прямой доступ к Canvas/CoreGraphics |
| Сложные списки | +/- | +/- | Зависит от требований |
| Быстрое прототипирование | - | + | Меньше кода, быстрее итерации |
| Performance-critical | + | - | Меньше overhead |

### Hybrid подход

```swift
// iOS: SwiftUI с UIKit компонентами
import SwiftUI

struct HybridView: View {
    var body: some View {
        VStack {
            Text("SwiftUI Header")
                .font(.title)

            // UIKit view в SwiftUI
            CustomUIKitView()
                .frame(height: 200)

            Button("SwiftUI Button") {
                // action
            }
        }
    }
}

// UIViewRepresentable для интеграции UIKit
struct CustomUIKitView: UIViewRepresentable {

    func makeUIView(context: Context) -> CustomDrawingView {
        return CustomDrawingView()
    }

    func updateUIView(_ uiView: CustomDrawingView, context: Context) {
        // Обновление при изменении state
    }
}
```

```kotlin
// Android: Compose с Android Views
@Composable
fun HybridScreen() {
    Column {
        Text(
            text = "Compose Header",
            style = MaterialTheme.typography.h4
        )

        // Android View в Compose
        AndroidView(
            factory = { context ->
                CustomDrawingView(context).apply {
                    // Настройка View
                }
            },
            modifier = Modifier.height(200.dp),
            update = { view ->
                // Обновление при рекомпозиции
            }
        )

        Button(onClick = { /* action */ }) {
            Text("Compose Button")
        }
    }
}
```

### Рекомендации по миграции

```
Стратегия постепенной миграции:

1. Новые экраны → Declarative
   └── SwiftUI / Jetpack Compose

2. Простые существующие экраны → Refactor
   └── Низкий риск, быстрый результат

3. Сложные экраны → Hybrid
   └── Compose/SwiftUI wrapper вокруг imperative

4. Критичные компоненты → Оставить
   └── Если работает и оптимизировано - не трогать
```

---

## 10. Проверь себя

### Вопрос 1
Какой аналог `UIViewController` в Android?

<details>
<summary>Ответ</summary>

`Activity` или `Fragment`. Activity управляет полным экраном приложения, Fragment - переиспользуемой частью UI внутри Activity. В современной архитектуре предпочтительнее использовать Single Activity + Fragments или Jetpack Compose.
</details>

### Вопрос 2
Почему важно вызывать `translatesAutoresizingMaskIntoConstraints = false` в iOS?

<details>
<summary>Ответ</summary>

По умолчанию UIKit автоматически создаёт constraints на основе `autoresizingMask`. Если вы добавляете свои constraints без отключения этого поведения, возникает конфликт между автоматически созданными и вашими constraints, что приводит к ошибкам layout или неожиданному поведению.
</details>

### Вопрос 3
В чём разница между `RecyclerView.ViewHolder` и `UITableViewCell`?

<details>
<summary>Ответ</summary>

- `UITableViewCell` - это сама ячейка (View), которая переиспользуется через `dequeueReusableCell`.
- `ViewHolder` - это паттерн для кэширования ссылок на views внутри ячейки. В RecyclerView ViewHolder обязателен и является отдельным классом, тогда как в UITableView подобное кэширование опционально и делается внутри самой ячейки.
</details>

### Вопрос 4
Как избежать retain cycle в iOS closure?

<details>
<summary>Ответ</summary>

Использовать `[weak self]` или `[unowned self]` в capture list:
```swift
viewModel.onComplete = { [weak self] result in
    self?.handleResult(result)
}
```
`weak` создаёт опциональную слабую ссылку (может стать nil), `unowned` создаёт неопциональную слабую ссылку (crash если объект освобождён).
</details>

### Вопрос 5
Какой аналог `UIGestureRecognizer` в Android?

<details>
<summary>Ответ</summary>

`GestureDetector` и `GestureDetectorCompat` для базовых жестов (tap, double tap, long press, scroll, fling), `ScaleGestureDetector` для pinch zoom, и `OnTouchListener` для низкоуровневой обработки касаний. В отличие от iOS, где gesture recognizers добавляются к view, в Android обычно создаётся один detector и события передаются в него из `onTouchEvent`.
</details>

### Вопрос 6
Почему нельзя обновлять UI из background thread?

<details>
<summary>Ответ</summary>

UIKit и Android Views не являются thread-safe. Обновление UI из background thread может привести к:
- Race conditions и повреждению данных
- Crash приложения
- Визуальным артефактам
- Неопределённому поведению

В iOS используйте `DispatchQueue.main.async`, в Android - `runOnUiThread`, `Handler(Looper.getMainLooper())`, или coroutines с `Dispatchers.Main`.
</details>

### Вопрос 7
Что такое ConstraintLayout chains и есть ли аналог в iOS?

<details>
<summary>Ответ</summary>

Chains в ConstraintLayout позволяют группировать views и распределять их горизонтально или вертикально с различными стилями (spread, spread_inside, packed). В чистом Auto Layout прямого аналога нет, но похожее поведение можно получить через `UIStackView` с различными настройками `distribution` (fill, fillEqually, fillProportionally, equalSpacing, equalCentering).
</details>

### Вопрос 8
Зачем нужен `prepareForReuse()` в UITableViewCell?

<details>
<summary>Ответ</summary>

`prepareForReuse()` вызывается перед переиспользованием ячейки для нового элемента. В этом методе нужно сбросить состояние ячейки (очистить текст, изображения, скрыть элементы), чтобы избежать отображения данных от предыдущего использования. В Android аналогичную роль играет `onViewRecycled()` в Adapter.
</details>

---

## 11. Связанные заметки

- [[ios-uikit-fundamentals]] — Основы UIKit: views, controllers, lifecycle
- [[android-ui-views]] — Android View system: layouts, custom views, touch handling
- [[cross-ui-declarative]] — Сравнение SwiftUI и Jetpack Compose
- [[mobile-architecture-patterns]] — MVP, MVVM, MVI для мобильных приложений
- [[mobile-performance-optimization]] — Оптимизация производительности UI

---
title: "iOS Scroll Performance: UITableView, UICollectionView, cell reuse"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 80
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/performance
  - level/intermediate
related:
  - "[[android-recyclerview-internals]]"
  - "[[ios-view-rendering]]"
  - "[[performance-optimization]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-uikit-fundamentals]]"
---

# iOS Scroll Performance

## TL;DR

Производительность скролла в iOS критически зависит от трёх факторов: переиспользования ячеек (cell reuse), предзагрузки данных (prefetching) и минимизации работы в `cellForRowAt`. Если скролл "дёргается" — это значит, что main thread не успевает отрисовать кадры за 16.67мс (60 FPS) или 8.33мс (120 FPS на ProMotion).

---

## Зачем это нужно?

Плавный скролл — это **первое впечатление** пользователя о качестве приложения:

| Метрика | Восприятие пользователем |
|---------|-------------------------|
| 60 FPS (16.67мс/кадр) | Плавно, комфортно |
| 45-50 FPS | Заметные микро-подтормаживания |
| < 30 FPS | "Приложение тормозит", негативные отзывы |
| ProMotion 120 FPS | Ультра-плавно, 8.33мс/кадр |

**Статистика восприятия:**
- 53% пользователей удаляют приложение с плохой производительностью
- Задержка в 100мс воспринимается как "что-то не так"
- Задержка в 1 секунду прерывает поток мыслей пользователя

```
┌─────────────────────────────────────────────────────────────┐
│                    Frame Budget                              │
├─────────────────────────────────────────────────────────────┤
│  60 FPS:  |████████████████| 16.67ms на всё                 │
│ 120 FPS:  |████████|         8.33ms — в 2 раза меньше!      │
│                                                              │
│  Что должно уложиться:                                       │
│  • Layout ячеек                                              │
│  • Загрузка изображений                                      │
│  • Биндинг данных                                            │
│  • Отрисовка теней, скруглений                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Теоретические основы

> **Определение:** Виртуализация списков (list virtualization) — техника оптимизации, при которой в памяти и в DOM/view hierarchy существуют только видимые элементы списка, а данные за пределами viewport загружаются по требованию. Впервые формализована как «объектный пул» (object pool pattern) в контексте UI.

### Паттерн Object Pool и Cell Reuse

UITableView/UICollectionView реализуют паттерн **Object Pool** (GoF-adjacent, Gamma, 1994):

| Концепция | Теория | Реализация в iOS |
|-----------|--------|-----------------|
| Object Pool | Переиспользование дорогих объектов вместо создания новых | `dequeueReusableCell(withIdentifier:)` |
| Flyweight | Разделение intrinsic (shared) и extrinsic (unique) state | Cell class (shared) + данные модели (unique) |
| Prefetching | Предзагрузка данных до момента отображения | `UITableViewDataSourcePrefetching` (iOS 10+) |

### Frame Budget и Human Perception

> **Закон Вебера-Фехнера (1860):** Восприятие изменений в сенсорном стимуле логарифмически зависит от интенсивности стимула. Применительно к UI: падение с 60 FPS до 30 FPS воспринимается как катастрофическое, тогда как с 120 FPS до 90 FPS — как незначительное.

| Target FPS | Frame budget | Устройства | Восприятие |
|------------|-------------|-----------|-----------|
| 60 FPS | 16.67 мс | Стандартные iPhone/iPad | Плавно |
| 120 FPS | 8.33 мс | ProMotion (iPhone 13 Pro+) | Ультра-плавно |
| < 30 FPS | > 33.33 мс | — | Видимые рывки (jank) |

### Diffable Data Sources: теоретическая основа

NSDiffableDataSourceSnapshot использует алгоритм *edit distance* (Wagner & Fischer, 1974) для вычисления минимального набора операций (insert, delete, move) между двумя состояниями списка. Это гарантирует корректные анимации без ручного управления beginUpdates/endUpdates.

### Связь с CS-фундаментом

- [[ios-view-rendering]] — render pipeline и compositing
- [[android-recyclerview-internals]] — аналогичная виртуализация в Android
- [[performance-optimization]] — общие принципы оптимизации производительности

---

## Аналогии из жизни

### 1. Cell Reuse = Тарелки в ресторане 🍽️

Ресторан не покупает новую тарелку для каждого гостя. Грязные тарелки моют и используют снова.

```
┌─────────────────────────────────────────────────────────────┐
│  Посетитель 1    Посетитель 2    Посетитель 3              │
│      ↓               ↓               ↓                      │
│   [Тарелка]  →   [Моют]   →   [Тарелка]  →   [Моют]   →    │
│                                                              │
│  То же самое:                                                │
│  [Ячейка A]  → [prepareForReuse] → [Ячейка A с новыми данными]│
└─────────────────────────────────────────────────────────────┘
```

### 2. Prefetching = Официант несёт следующие блюда заранее

Пока вы едите первое, официант уже готовит второе на кухне. Не ждёт, пока вы попросите.

```
┌─────────────────────────────────────────────────────────────┐
│   Вы видите:     │   Уже готовится:                         │
│   ┌─────────┐    │   ┌─────────┐                            │
│   │ Ячейка 1│    │   │ Ячейка 5│ ← prefetchRowsAt           │
│   │ Ячейка 2│    │   │ Ячейка 6│                            │
│   │ Ячейка 3│    │   │ Ячейка 7│                            │
│   │ Ячейка 4│    │   └─────────┘                            │
│   └─────────┘    │                                          │
└─────────────────────────────────────────────────────────────┘
```

### 3. Estimated Height = Примерный размер порции в меню

Меню говорит "порция ~300г", чтобы вы понимали сколько заказывать. Точный вес узнаете когда принесут.

```
┌─────────────────────────────────────────────────────────────┐
│  estimatedRowHeight = 80  ← "Примерно такой высоты"         │
│                                                              │
│  Зачем: система заранее знает размер scrollView             │
│  Без этого: прыгающий scroll indicator, дёрганье            │
└─────────────────────────────────────────────────────────────┘
```

### 4. Self-Sizing Cells = Тарелка подстраивается под еду

Представьте тарелку, которая автоматически растягивается под размер блюда.

```
┌─────────────────────────────────────────────────────────────┐
│  "Привет"           →  ┌──────────────┐                     │
│                        │ Привет       │  height: 44         │
│                        └──────────────┘                     │
│                                                              │
│  "Очень длинный     →  ┌──────────────┐                     │
│   текст на          │  │ Очень длинный│                     │
│   несколько строк"  │  │ текст на     │  height: 88         │
│                        │ несколько    │                     │
│                        │ строк        │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### 5. Diffable Data Source = Официант знает что изменилось в заказе

Вместо "переделай весь заказ", официант знает: "добавь десерт, убери суп".

```
┌─────────────────────────────────────────────────────────────┐
│  Старый способ (reloadData):                                │
│  "Забудь всё, вот новый заказ целиком"                      │
│                                                              │
│  Diffable Data Source:                                       │
│  "Строка 3 удалена, строка 7 добавлена, строка 2 изменена"  │
│  → Анимированные изменения, без мерцания                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Архитектура скролла

### Как работает UIScrollView

```
┌─────────────────────────────────────────────────────────────────────┐
│                         UIScrollView                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      contentSize                               │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │                                                          │  │  │
│  │  │                    Невидимая область                     │  │  │
│  │  │                                                          │  │  │
│  │  ├──────────────────────────────────────────────────────────┤  │  │
│  │  │ ╔══════════════════════════════════════════════════════╗ │  │  │
│  │  │ ║              Видимая область (bounds)                ║ │  │  │
│  │  │ ║  contentOffset.y = 200                               ║ │  │  │
│  │  │ ║                                                      ║ │  │  │
│  │  │ ║  ┌────────────────────────────────────────────────┐  ║ │  │  │
│  │  │ ║  │ Cell (reused)                                  │  ║ │  │  │
│  │  │ ║  ├────────────────────────────────────────────────┤  ║ │  │  │
│  │  │ ║  │ Cell (reused)                                  │  ║ │  │  │
│  │  │ ║  ├────────────────────────────────────────────────┤  ║ │  │  │
│  │  │ ║  │ Cell (reused)                                  │  ║ │  │  │
│  │  │ ║  └────────────────────────────────────────────────┘  ║ │  │  │
│  │  │ ╚══════════════════════════════════════════════════════╝ │  │  │
│  │  ├──────────────────────────────────────────────────────────┤  │  │
│  │  │                                                          │  │  │
│  │  │                    Невидимая область                     │  │  │
│  │  │                                                          │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Жизненный цикл ячейки

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Cell Lifecycle                                   │
│                                                                      │
│   ┌──────────┐    ┌──────────────┐    ┌─────────────┐               │
│   │ Reuse    │───→│ cellForRowAt │───→│  Visible    │               │
│   │ Pool     │    │   configure  │    │  on screen  │               │
│   └──────────┘    └──────────────┘    └─────────────┘               │
│        ↑                                      │                      │
│        │                                      │ scrolled             │
│        │                                      │ off screen           │
│        │          ┌────────────────┐          ↓                      │
│        └──────────│prepareForReuse │←─────────┘                      │
│                   └────────────────┘                                 │
│                                                                      │
│   Reuse Pool: [Cell] [Cell] [Cell] — готовые к использованию        │
└─────────────────────────────────────────────────────────────────────┘
```

### UITableView vs UICollectionView

```
┌────────────────────────────┬────────────────────────────────────────┐
│       UITableView          │         UICollectionView               │
├────────────────────────────┼────────────────────────────────────────┤
│ ┌────────────────────────┐ │ ┌──────┐ ┌──────┐ ┌──────┐           │
│ │ Строка 1               │ │ │ Item │ │ Item │ │ Item │           │
│ ├────────────────────────┤ │ ├──────┤ ├──────┤ ├──────┤           │
│ │ Строка 2               │ │ │ Item │ │ Item │ │ Item │           │
│ ├────────────────────────┤ │ ├──────┤ ├──────┤ ├──────┤           │
│ │ Строка 3               │ │ │ Item │ │ Item │ │ Item │           │
│ └────────────────────────┘ │ └──────┘ └──────┘ └──────┘           │
│                            │                                        │
│ • Одна колонка            │ • Любой layout                          │
│ • Простой API             │ • Compositional Layout (iOS 13+)        │
│ • Встроенные стили        │ • UICollectionViewFlowLayout            │
│ • Секции и headers        │ • Diffable Data Source                  │
└────────────────────────────┴────────────────────────────────────────┘
```

---

## Cell Reuse

### Как работает переиспользование

```swift
// Регистрация ячейки
tableView.register(MyCell.self, forCellReuseIdentifier: "MyCell")

// Получение ячейки из пула
func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {

    // dequeueReusableCell:
    // 1. Ищет ячейку в reuse pool
    // 2. Если нет — создаёт новую
    // 3. Вызывает prepareForReuse() перед возвратом
    let cell = tableView.dequeueReusableCell(
        withIdentifier: "MyCell",
        for: indexPath
    ) as! MyCell

    // Конфигурируем с новыми данными
    cell.configure(with: items[indexPath.row])

    return cell
}
```

### ReuseIdentifier — ключ к правильному переиспользованию

```swift
// Разные типы ячеек = разные идентификаторы
enum CellIdentifier {
    static let text = "TextCell"
    static let image = "ImageCell"
    static let video = "VideoCell"
}

// Регистрация
tableView.register(TextCell.self, forCellReuseIdentifier: CellIdentifier.text)
tableView.register(ImageCell.self, forCellReuseIdentifier: CellIdentifier.image)
tableView.register(VideoCell.self, forCellReuseIdentifier: CellIdentifier.video)

// Использование
func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {

    let item = items[indexPath.row]

    switch item.type {
    case .text:
        let cell = tableView.dequeueReusableCell(
            withIdentifier: CellIdentifier.text,
            for: indexPath
        ) as! TextCell
        cell.configure(with: item)
        return cell

    case .image:
        let cell = tableView.dequeueReusableCell(
            withIdentifier: CellIdentifier.image,
            for: indexPath
        ) as! ImageCell
        cell.configure(with: item)
        return cell

    case .video:
        let cell = tableView.dequeueReusableCell(
            withIdentifier: CellIdentifier.video,
            for: indexPath
        ) as! VideoCell
        cell.configure(with: item)
        return cell
    }
}
```

### prepareForReuse() — сброс состояния

```swift
class ImageCell: UITableViewCell {

    private let thumbnailImageView = UIImageView()
    private let titleLabel = UILabel()
    private var imageLoadTask: Task<Void, Never>?

    override func prepareForReuse() {
        super.prepareForReuse()

        // ВАЖНО: Отменяем незавершённые операции
        imageLoadTask?.cancel()
        imageLoadTask = nil

        // Сбрасываем визуальное состояние
        thumbnailImageView.image = nil
        titleLabel.text = nil

        // Сбрасываем любые анимации
        thumbnailImageView.layer.removeAllAnimations()

        // НЕ сбрасывайте здесь:
        // - Constraints (они переиспользуются)
        // - Subviews (они уже добавлены)
        // - Делегаты (установите в configure)
    }

    func configure(with item: Item) {
        titleLabel.text = item.title

        // Новая загрузка изображения
        imageLoadTask = Task {
            if let image = await ImageLoader.load(item.imageURL) {
                // Проверяем что задача не отменена
                guard !Task.isCancelled else { return }
                thumbnailImageView.image = image
            }
        }
    }
}
```

### Распространённые ошибки Cell Reuse

```swift
// ❌ ПЛОХО: Условная логика без else
override func prepareForReuse() {
    super.prepareForReuse()
}

func configure(with item: Item) {
    if item.isSpecial {
        backgroundColor = .yellow  // Установили для special
    }
    // Забыли сбросить для обычных — жёлтый фон "протечёт"
}

// ✅ ХОРОШО: Всегда явно устанавливаем все свойства
func configure(with item: Item) {
    backgroundColor = item.isSpecial ? .yellow : .white
}

// ❌ ПЛОХО: Добавление subview в configure
func configure(with item: Item) {
    let badge = BadgeView()  // Создаётся каждый раз!
    contentView.addSubview(badge)  // Накапливаются!
}

// ✅ ХОРОШО: Subviews создаются один раз в init
class MyCell: UITableViewCell {
    private let badge = BadgeView()

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        contentView.addSubview(badge)  // Один раз
    }

    func configure(with item: Item) {
        badge.isHidden = !item.showBadge
    }
}
```

---

## Self-Sizing Cells

### Настройка автоматической высоты

```swift
// UITableView
tableView.rowHeight = UITableView.automaticDimension
tableView.estimatedRowHeight = 80  // Примерная высота!

// UICollectionView с Flow Layout
if let layout = collectionView.collectionViewLayout as? UICollectionViewFlowLayout {
    layout.estimatedItemSize = UICollectionViewFlowLayout.automaticSize
}
```

### Правильные constraints для self-sizing

```swift
class SelfSizingCell: UITableViewCell {

    private let titleLabel = UILabel()
    private let bodyLabel = UILabel()

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }

    private func setupUI() {
        // Многострочные лейблы
        titleLabel.numberOfLines = 0
        bodyLabel.numberOfLines = 0

        // Добавляем в contentView, НЕ в self
        contentView.addSubview(titleLabel)
        contentView.addSubview(bodyLabel)

        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        bodyLabel.translatesAutoresizingMaskIntoConstraints = false

        // КРИТИЧНО: Полная цепочка constraints от top до bottom
        NSLayoutConstraint.activate([
            // Title привязан к верху
            titleLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 16),
            titleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            titleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),

            // Body под title
            bodyLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            bodyLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            bodyLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),

            // Body привязан к низу — ОБЯЗАТЕЛЬНО!
            bodyLabel.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -16)
        ])
    }

    required init?(coder: NSCoder) { fatalError() }
}
```

### Диаграмма constraints для self-sizing

```
┌─────────────────────────────────────────────────────────────────────┐
│                        contentView                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ TOP (16pt)                                                     │  │
│  │ ┌─────────────────────────────────────────────────────────┐   │  │
│  │ │ titleLabel                                               │   │  │
│  │ │ (numberOfLines = 0)                                      │   │  │
│  │ └─────────────────────────────────────────────────────────┘   │  │
│  │ SPACING (8pt)                                                  │  │
│  │ ┌─────────────────────────────────────────────────────────┐   │  │
│  │ │ bodyLabel                                                │   │  │
│  │ │ (numberOfLines = 0)                                      │   │  │
│  │ │ Может быть любой высоты!                                 │   │  │
│  │ └─────────────────────────────────────────────────────────┘   │  │
│  │ BOTTOM (16pt)                                                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Цепочка: top → titleLabel → bodyLabel → bottom                     │
│  Высота определяется контентом!                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Почему estimatedRowHeight важен

```swift
// ❌ ПЛОХО: Нет estimated height
tableView.rowHeight = UITableView.automaticDimension
// Результат: iOS вычисляет ВСЕ высоты заранее = тормоза при загрузке

// ✅ ХОРОШО: С estimated height
tableView.rowHeight = UITableView.automaticDimension
tableView.estimatedRowHeight = 80
// Результат: iOS использует 80 для невидимых,
//           вычисляет реальную только для видимых
```

```
┌─────────────────────────────────────────────────────────────────────┐
│  1000 ячеек, разная высота                                          │
│                                                                      │
│  Без estimatedRowHeight:                                             │
│  [Вычислить][Вычислить][Вычислить]...[Вычислить] = 1000 вычислений  │
│  Время загрузки: ~2-3 секунды                                        │
│                                                                      │
│  С estimatedRowHeight = 80:                                          │
│  [80][80][80]...[Вычислить видимые ~10] = 10 вычислений             │
│  Время загрузки: мгновенно                                           │
│                                                                      │
│  Scroll indicator может "прыгать", но это лучше чем тормоза!        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Prefetching

### UITableViewDataSourcePrefetching

```swift
class FeedViewController: UIViewController {

    private let tableView = UITableView()
    private var items: [FeedItem] = []
    private let imageLoader = ImageLoader()

    override func viewDidLoad() {
        super.viewDidLoad()

        tableView.dataSource = self
        tableView.prefetchDataSource = self  // Включаем prefetching
    }
}

extension FeedViewController: UITableViewDataSourcePrefetching {

    // Вызывается когда ячейки СКОРО появятся на экране
    func tableView(_ tableView: UITableView,
                   prefetchRowsAt indexPaths: [IndexPath]) {

        for indexPath in indexPaths {
            let item = items[indexPath.row]

            // Начинаем загрузку изображений заранее
            imageLoader.prefetch(url: item.imageURL)
        }
    }

    // Вызывается когда пользователь изменил направление скролла
    // или ячейки больше не понадобятся
    func tableView(_ tableView: UITableView,
                   cancelPrefetchingForRowsAt indexPaths: [IndexPath]) {

        for indexPath in indexPaths {
            let item = items[indexPath.row]

            // Отменяем ненужные загрузки
            imageLoader.cancelPrefetch(url: item.imageURL)
        }
    }
}
```

### Диаграмма prefetching

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Prefetching Timeline                              │
│                                                                      │
│  Скролл вниз ↓                                                       │
│                                                                      │
│  ┌─────────────────────────────────────────┐                        │
│  │ Ячейка 1  [Видима]                      │                        │
│  │ Ячейка 2  [Видима]                      │                        │
│  │ Ячейка 3  [Видима]                      │                        │
│  │ Ячейка 4  [Видима]                      │                        │
│  └─────────────────────────────────────────┘                        │
│  - - - - - - - - - - - - - - - - - - - - - - - edge of screen       │
│  │ Ячейка 5  [prefetchRowsAt вызван]       │ ← загрузка началась    │
│  │ Ячейка 6  [prefetchRowsAt вызван]       │                        │
│  │ Ячейка 7  [prefetchRowsAt вызван]       │                        │
│  │ Ячейка 8  [prefetchRowsAt вызван]       │                        │
│                                                                      │
│  Если пользователь резко скроллит обратно ↑:                        │
│  → cancelPrefetchingForRowsAt для 5, 6, 7, 8                        │
│  → prefetchRowsAt для 0 (если была бы выше)                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Стратегии загрузки изображений

```swift
class ImageLoader {

    private var prefetchTasks: [URL: Task<UIImage?, Never>] = [:]
    private let cache = NSCache<NSURL, UIImage>()

    // Prefetch: начинаем загрузку, кэшируем результат
    func prefetch(url: URL) {
        guard prefetchTasks[url] == nil else { return }
        guard cache.object(forKey: url as NSURL) == nil else { return }

        prefetchTasks[url] = Task {
            do {
                let (data, _) = try await URLSession.shared.data(from: url)
                if let image = UIImage(data: data) {
                    cache.setObject(image, forKey: url as NSURL)
                    return image
                }
            } catch {
                // Ошибка prefetch — не критично
            }
            return nil
        }
    }

    // Отмена prefetch
    func cancelPrefetch(url: URL) {
        prefetchTasks[url]?.cancel()
        prefetchTasks[url] = nil
    }

    // Загрузка для отображения (с учётом кэша и prefetch)
    func load(url: URL) async -> UIImage? {
        // Проверяем кэш
        if let cached = cache.object(forKey: url as NSURL) {
            return cached
        }

        // Ждём prefetch если он уже идёт
        if let prefetchTask = prefetchTasks[url] {
            return await prefetchTask.value
        }

        // Загружаем напрямую
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            if let image = UIImage(data: data) {
                cache.setObject(image, forKey: url as NSURL)
                return image
            }
        } catch {
            return nil
        }
        return nil
    }
}
```

---

## Diffable Data Source

### Основы NSDiffableDataSourceSnapshot

```swift
// Определяем типы для секций и элементов
enum Section: Hashable {
    case featured
    case regular
}

struct Item: Hashable {
    let id: UUID
    let title: String
    let subtitle: String

    // Hashable на основе id
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }

    static func == (lhs: Item, rhs: Item) -> Bool {
        lhs.id == rhs.id
    }
}

class FeedViewController: UIViewController {

    private var dataSource: UITableViewDiffableDataSource<Section, Item>!
    private let tableView = UITableView()

    override func viewDidLoad() {
        super.viewDidLoad()
        configureDataSource()
    }

    private func configureDataSource() {
        dataSource = UITableViewDiffableDataSource<Section, Item>(
            tableView: tableView
        ) { tableView, indexPath, item in

            let cell = tableView.dequeueReusableCell(
                withIdentifier: "Cell",
                for: indexPath
            )
            cell.textLabel?.text = item.title
            cell.detailTextLabel?.text = item.subtitle
            return cell
        }
    }

    // Применение изменений
    func updateData(featured: [Item], regular: [Item]) {
        var snapshot = NSDiffableDataSourceSnapshot<Section, Item>()

        snapshot.appendSections([.featured, .regular])
        snapshot.appendItems(featured, toSection: .featured)
        snapshot.appendItems(regular, toSection: .regular)

        // animatingDifferences: true = плавные анимации
        dataSource.apply(snapshot, animatingDifferences: true)
    }
}
```

### Анимированные изменения

```swift
// Добавление нового элемента
func addItem(_ item: Item, after existingItem: Item) {
    var snapshot = dataSource.snapshot()
    snapshot.insertItems([item], afterItem: existingItem)
    dataSource.apply(snapshot, animatingDifferences: true)
}

// Удаление элемента
func removeItem(_ item: Item) {
    var snapshot = dataSource.snapshot()
    snapshot.deleteItems([item])
    dataSource.apply(snapshot, animatingDifferences: true)
}

// Обновление элемента (iOS 15+)
func updateItem(_ item: Item) {
    var snapshot = dataSource.snapshot()
    snapshot.reconfigureItems([item])  // Не пересоздаёт ячейку, только обновляет
    dataSource.apply(snapshot, animatingDifferences: true)
}

// Перемещение элемента
func moveItem(_ item: Item, after other: Item) {
    var snapshot = dataSource.snapshot()
    snapshot.moveItem(item, afterItem: other)
    dataSource.apply(snapshot, animatingDifferences: true)
}
```

### Section Snapshots (iOS 14+)

```swift
// Для иерархических данных (expandable sections)
struct OutlineItem: Hashable {
    let id: UUID
    let title: String
    let children: [OutlineItem]
}

func applySnapshot(items: [OutlineItem]) {
    var sectionSnapshot = NSDiffableDataSourceSectionSnapshot<OutlineItem>()

    func addItems(_ items: [OutlineItem], to parent: OutlineItem?) {
        sectionSnapshot.append(items, to: parent)
        for item in items where !item.children.isEmpty {
            addItems(item.children, to: item)
        }
    }

    addItems(items, to: nil)

    // Применяем к конкретной секции
    dataSource.apply(sectionSnapshot, to: .main, animatingDifferences: true)
}
```

### Преимущества Diffable Data Source

```
┌─────────────────────────────────────────────────────────────────────┐
│  Старый способ (reloadData)        vs    Diffable Data Source       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  reloadData():                          apply(snapshot):             │
│  • Перерисовывает ВСЁ                  • Только изменённые ячейки   │
│  • Нет анимаций                        • Автоматические анимации    │
│  • Мерцание экрана                     • Плавные переходы           │
│  • Ручной tracking изменений          • Автоматический diff         │
│  • Crashes при несовпадении           • Безопасно, нет crashes      │
│                                                                      │
│  func update() {                       func update() {               │
│    // 😰 Надо синхронизировать!        var snap = snapshot()         │
│    tableView.beginUpdates()             snap.deleteItems([old])      │
│    items.remove(at: 0)                  snap.appendItems([new])      │
│    tableView.deleteRows(...)            apply(snap)  // Done!        │
│    items.append(new)                   }                             │
│    tableView.insertRows(...)                                         │
│    tableView.endUpdates()                                            │
│    // 💥 Crash если ошибка!                                          │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## UICollectionView Compositional Layout

### Современный подход к layout (iOS 13+)

```swift
func createLayout() -> UICollectionViewLayout {

    // Item
    let itemSize = NSCollectionLayoutSize(
        widthDimension: .fractionalWidth(1.0),
        heightDimension: .estimated(100)
    )
    let item = NSCollectionLayoutItem(layoutSize: itemSize)

    // Group
    let groupSize = NSCollectionLayoutSize(
        widthDimension: .fractionalWidth(1.0),
        heightDimension: .estimated(100)
    )
    let group = NSCollectionLayoutGroup.vertical(
        layoutSize: groupSize,
        subitems: [item]
    )

    // Section
    let section = NSCollectionLayoutSection(group: group)
    section.interGroupSpacing = 10
    section.contentInsets = NSDirectionalEdgeInsets(
        top: 10, leading: 16, bottom: 10, trailing: 16
    )

    return UICollectionViewCompositionalLayout(section: section)
}
```

### Сложный layout: Grid + List + Carousel

```swift
func createComplexLayout() -> UICollectionViewLayout {

    return UICollectionViewCompositionalLayout { sectionIndex, environment in

        switch sectionIndex {
        case 0:
            // Carousel (горизонтальный скролл)
            return self.createCarouselSection()
        case 1:
            // Grid 2x2
            return self.createGridSection()
        default:
            // List
            return self.createListSection()
        }
    }
}

private func createCarouselSection() -> NSCollectionLayoutSection {
    let itemSize = NSCollectionLayoutSize(
        widthDimension: .fractionalWidth(1.0),
        heightDimension: .fractionalHeight(1.0)
    )
    let item = NSCollectionLayoutItem(layoutSize: itemSize)

    let groupSize = NSCollectionLayoutSize(
        widthDimension: .fractionalWidth(0.85),
        heightDimension: .absolute(200)
    )
    let group = NSCollectionLayoutGroup.horizontal(
        layoutSize: groupSize,
        subitems: [item]
    )

    let section = NSCollectionLayoutSection(group: group)
    section.orthogonalScrollingBehavior = .groupPagingCentered
    section.interGroupSpacing = 16

    return section
}

private func createGridSection() -> NSCollectionLayoutSection {
    let itemSize = NSCollectionLayoutSize(
        widthDimension: .fractionalWidth(0.5),
        heightDimension: .fractionalWidth(0.5)
    )
    let item = NSCollectionLayoutItem(layoutSize: itemSize)
    item.contentInsets = NSDirectionalEdgeInsets(
        top: 4, leading: 4, bottom: 4, trailing: 4
    )

    let groupSize = NSCollectionLayoutSize(
        widthDimension: .fractionalWidth(1.0),
        heightDimension: .fractionalWidth(0.5)
    )
    let group = NSCollectionLayoutGroup.horizontal(
        layoutSize: groupSize,
        subitem: item,
        count: 2
    )

    return NSCollectionLayoutSection(group: group)
}
```

### List Configuration (iOS 14+)

```swift
// UICollectionView как UITableView — лучше обоих миров!
func createListLayout() -> UICollectionViewLayout {

    var config = UICollectionLayoutListConfiguration(appearance: .insetGrouped)
    config.showsSeparators = true
    config.headerMode = .supplementary

    // Swipe actions
    config.trailingSwipeActionsConfigurationProvider = { indexPath in
        let deleteAction = UIContextualAction(
            style: .destructive,
            title: "Delete"
        ) { action, view, completion in
            // Handle delete
            completion(true)
        }
        return UISwipeActionsConfiguration(actions: [deleteAction])
    }

    return UICollectionViewCompositionalLayout.list(using: config)
}
```

### Преимущества Compositional Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Compositional Layout Benefits                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Декларативный синтаксис                                          │
│     • Описываем ЧТО хотим, не КАК                                    │
│     • Нет delegate методов для размеров                              │
│                                                                      │
│  2. Композиция                                                        │
│     • Item → Group → Section → Layout                                │
│     • Переиспользуемые компоненты                                    │
│                                                                      │
│  3. Производительность                                                │
│     • Оптимизировано Apple                                           │
│     • Self-sizing из коробки                                         │
│     • Orthogonal scrolling без вложенных scroll views                │
│                                                                      │
│  4. Гибкость                                                          │
│     • Разные layouts для разных секций                               │
│     • Adaptive layouts с environment                                  │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Header                                                         │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │ [Carousel → → →]                    ← orthogonalScrolling     │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │ [Grid] [Grid]                                                  │  │
│  │ [Grid] [Grid]                       ← fractionalWidth(0.5)    │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │ [List item                        ]                            │  │
│  │ [List item                        ] ← .list(using: config)    │  │
│  │ [List item                        ]                            │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## SwiftUI List Performance

### LazyVStack vs List

```swift
// List — рекомендуется для большинства случаев
struct ContentView: View {
    let items: [Item]

    var body: some View {
        List(items) { item in
            ItemRow(item: item)
        }
    }
}

// LazyVStack — для кастомного дизайна
struct CustomListView: View {
    let items: [Item]

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 0) {  // LAZY — не создаёт все view сразу
                ForEach(items) { item in
                    ItemRow(item: item)
                }
            }
        }
    }
}

// ❌ ПЛОХО: VStack создаёт ВСЕ view сразу
struct BadListView: View {
    let items: [Item]  // 10000 items

    var body: some View {
        ScrollView {
            VStack {  // 💀 Создаст 10000 views при загрузке!
                ForEach(items) { item in
                    ItemRow(item: item)
                }
            }
        }
    }
}
```

### .id() для identity

```swift
struct Item: Identifiable {
    let id: UUID  // Стабильный идентификатор
    var title: String
    var count: Int
}

// SwiftUI использует id для определения identity
List(items) { item in
    ItemRow(item: item)
}

// Эквивалентно:
List(items, id: \.id) { item in
    ItemRow(item: item)
}

// ❌ ПЛОХО: Нестабильный id
List(items, id: \.title) { item in  // Если title изменится — view пересоздаётся!
    ItemRow(item: item)
}

// ❌ ПЛОХО: Индекс как id
ForEach(Array(items.enumerated()), id: \.offset) { index, item in
    ItemRow(item: item)  // При удалении элемента — всё сломается
}
```

### @StateObject vs @ObservedObject в ячейках

```swift
// ❌ ПЛОХО: @StateObject в ячейке List
struct ItemRow: View {
    let itemId: UUID
    @StateObject private var viewModel = ItemViewModel()  // Создаётся для каждой ячейки!

    var body: some View {
        Text(viewModel.title)
            .onAppear {
                viewModel.load(id: itemId)
            }
    }
}

// ✅ ХОРОШО: ViewModel передаётся извне
struct ItemRow: View {
    @ObservedObject var viewModel: ItemViewModel

    var body: some View {
        Text(viewModel.title)
    }
}

// В родительском view:
struct ContentView: View {
    @StateObject private var store = ItemStore()

    var body: some View {
        List(store.items) { item in
            ItemRow(viewModel: store.viewModel(for: item))
        }
    }
}
```

### Оптимизация SwiftUI List

```swift
struct OptimizedList: View {
    let items: [Item]

    var body: some View {
        List(items) { item in
            ItemRow(item: item)
                .listRowInsets(EdgeInsets())  // Убираем padding если не нужен
                .listRowSeparator(.hidden)     // Убираем разделители
        }
        .listStyle(.plain)
        .scrollContentBackground(.hidden)  // iOS 16+ для кастомного фона
    }
}

// Для очень длинных списков
struct LargeList: View {
    @State private var items: [Item] = []

    var body: some View {
        List(items) { item in
            ItemRow(item: item)
        }
        .task {
            // Загружаем данные асинхронно
            items = await loadItems()
        }
    }
}
```

---

## Распространённые ошибки

### 1. Тяжёлые вычисления в cellForRowAt

```swift
// ❌ ПЛОХО: Вычисления в cellForRowAt блокируют main thread
func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)

    let item = items[indexPath.row]

    // 💀 Форматирование даты — дорогая операция!
    let formatter = DateFormatter()
    formatter.dateStyle = .long
    formatter.timeStyle = .short
    cell.detailTextLabel?.text = formatter.string(from: item.date)

    // 💀 Attributed string computation
    let attributed = NSMutableAttributedString(string: item.longText)
    // ... сложные атрибуты
    cell.textLabel?.attributedText = attributed

    return cell
}

// ✅ ХОРОШО: Предвычисляем при создании модели
struct Item {
    let title: String
    let date: Date

    // Предвычисленные значения
    let formattedDate: String
    let attributedTitle: NSAttributedString

    init(title: String, date: Date) {
        self.title = title
        self.date = date

        // Один раз при создании
        let formatter = DateFormatter()
        formatter.dateStyle = .long
        self.formattedDate = formatter.string(from: date)

        self.attributedTitle = Self.computeAttributedTitle(title)
    }
}

func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
    let item = items[indexPath.row]

    // Просто присваиваем готовые значения
    cell.textLabel?.attributedText = item.attributedTitle
    cell.detailTextLabel?.text = item.formattedDate

    return cell
}
```

### 2. Загрузка изображений в main thread

```swift
// ❌ ПЛОХО: Блокирует UI
func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)

    let imageURL = items[indexPath.row].imageURL

    // 💀 Синхронная загрузка!
    if let data = try? Data(contentsOf: imageURL) {
        cell.imageView?.image = UIImage(data: data)
    }

    return cell
}

// ✅ ХОРОШО: Асинхронная загрузка с проверкой
class ImageCell: UITableViewCell {
    private var currentURL: URL?
    private var loadTask: Task<Void, Never>?

    override func prepareForReuse() {
        super.prepareForReuse()
        loadTask?.cancel()
        imageView?.image = nil
        currentURL = nil
    }

    func configure(with url: URL) {
        currentURL = url

        loadTask = Task {
            // Загружаем в background
            guard let image = await ImageLoader.shared.load(url: url) else { return }

            // Проверяем что ячейка всё ещё показывает этот URL
            guard currentURL == url, !Task.isCancelled else { return }

            // Обновляем UI в main thread
            imageView?.image = image
        }
    }
}
```

### 3. Отсутствие prefetching

```swift
// ❌ ПЛОХО: Загрузка только когда ячейка появляется
func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath) as! ImageCell

    // Загрузка начинается только сейчас
    cell.loadImage(from: items[indexPath.row].imageURL)

    return cell
}

// ✅ ХОРОШО: Prefetching + кэширование
extension ViewController: UITableViewDataSourcePrefetching {

    func tableView(_ tableView: UITableView,
                   prefetchRowsAt indexPaths: [IndexPath]) {
        let urls = indexPaths.map { items[$0.row].imageURL }
        imageLoader.prefetch(urls: urls)
    }

    func tableView(_ tableView: UITableView,
                   cancelPrefetchingForRowsAt indexPaths: [IndexPath]) {
        let urls = indexPaths.map { items[$0.row].imageURL }
        imageLoader.cancelPrefetch(urls: urls)
    }
}
```

### 4. Неправильный estimatedRowHeight

```swift
// ❌ ПЛОХО: Слишком маленький estimated height
tableView.estimatedRowHeight = 10  // Реальная высота ~150

// Результат: scroll indicator прыгает, возможны проблемы с scrollToRow

// ❌ ПЛОХО: Слишком большой estimated height
tableView.estimatedRowHeight = 500  // Реальная высота ~50

// Результат: неправильный contentSize, проблемы с layout

// ✅ ХОРОШО: Близко к средней реальной высоте
tableView.estimatedRowHeight = 120  // Средняя высота ячеек ~100-150
```

### 5. Неправильное переиспользование ячеек

```swift
// ❌ ПЛОХО: Не сбрасываем состояние
class ToggleCell: UITableViewCell {
    let toggle = UISwitch()

    func configure(isOn: Bool) {
        // Только если isOn = true, включаем
        if isOn {
            toggle.isOn = true
        }
        // Если isOn = false — toggle остаётся в предыдущем состоянии!
    }
}

// ✅ ХОРОШО: Явно устанавливаем все свойства
class ToggleCell: UITableViewCell {
    let toggle = UISwitch()

    override func prepareForReuse() {
        super.prepareForReuse()
        toggle.isOn = false  // Сброс к default
    }

    func configure(isOn: Bool) {
        toggle.isOn = isOn  // Всегда явно устанавливаем
    }
}
```

### 6. Дорогие тени и скругления

```swift
// ❌ ПЛОХО: Offscreen rendering каждый кадр
cell.layer.shadowColor = UIColor.black.cgColor
cell.layer.shadowOffset = CGSize(width: 0, height: 2)
cell.layer.shadowRadius = 4
cell.layer.shadowOpacity = 0.2
// Нет shadowPath = пересчёт тени каждый кадр!

cell.layer.cornerRadius = 12
cell.layer.masksToBounds = true  // Clipping = дорого

// ✅ ХОРОШО: Оптимизированные тени
cell.layer.shadowColor = UIColor.black.cgColor
cell.layer.shadowOffset = CGSize(width: 0, height: 2)
cell.layer.shadowRadius = 4
cell.layer.shadowOpacity = 0.2
cell.layer.shadowPath = UIBezierPath(
    roundedRect: cell.bounds,
    cornerRadius: 12
).cgPath  // Предвычисленный path!

// Для cornerRadius без clipping
cell.layer.cornerRadius = 12
cell.layer.masksToBounds = false  // Не clipпим

// Или используем CAShapeLayer для сложных форм
let maskLayer = CAShapeLayer()
maskLayer.path = UIBezierPath(
    roundedRect: bounds,
    cornerRadius: 12
).cgPath
cell.layer.mask = maskLayer

// ✅ ЛУЧШЕ: shouldRasterize для статичного контента
cell.layer.shouldRasterize = true
cell.layer.rasterizationScale = UIScreen.main.scale
```

---

## Ментальные модели

### 1. "16 миллисекунд или смерть"

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Frame Budget Mental Model                         │
│                                                                      │
│  Каждые 16.67мс (60 FPS) или 8.33мс (120 FPS):                      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │ 0ms        8ms        16ms       │                          │     │
│  │ |──────────|──────────|          │                          │     │
│  │ ├─Layout───┼─Draw─────┤ ✅ OK    │ Smooth 60 FPS           │     │
│  │ ├─Layout───────────────┼─Draw────┤ ⚠️ Dropped frame        │     │
│  │ ├─Layout─────────────────────────┼─────┤ 💀 Jank!          │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Правило: cellForRowAt должен выполняться < 1-2ms                   │
│  Всё остальное — в background или предвычислено                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. "Конвейер ячеек"

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Cell Conveyor Belt                                │
│                                                                      │
│  Представьте конвейер на заводе:                                     │
│                                                                      │
│     ┌────┐   ┌────┐   ┌────┐                                        │
│  ───│Cell│───│Cell│───│Cell│───→ Visible на экране                  │
│     └────┘   └────┘   └────┘                                        │
│        ↑                                                             │
│        │ dequeue                                                     │
│        │                                                             │
│     ┌──┴──────────────────┐                                         │
│     │    Reuse Pool       │  ← Ячейки ждут переиспользования        │
│     │  [Cell] [Cell] [Cell]│                                         │
│     └─────────────────────┘                                          │
│        ↑                                                             │
│        │ prepareForReuse                                             │
│        │                                                             │
│     ┌────┐   ┌────┐   ┌────┐                                        │
│  ←──│Cell│───│Cell│───│Cell│─── Ушли за экран                       │
│     └────┘   └────┘   └────┘                                        │
│                                                                      │
│  Ячейка никогда не уничтожается — только моется и переиспользуется  │
└─────────────────────────────────────────────────────────────────────┘
```

### 3. "Окно видимости"

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Visibility Window                                 │
│                                                                      │
│  Данные: [0][1][2][3][4][5][6][7][8][9][10][11][12]...              │
│                     ↑                                                │
│                     │                                                │
│           ┌─────────┴─────────┐                                      │
│           │   Visible Window   │                                     │
│           │    [3][4][5][6]    │                                     │
│           └───────────────────┘                                      │
│                                                                      │
│  Пользователь видит только 4 ячейки, но:                            │
│  • Prefetch готовит [7][8][9]                                       │
│  • Reuse pool хранит [0][1][2] для переиспользования                │
│                                                                      │
│  При скролле окно двигается:                                         │
│  [4][5][6][7] → prefetch [8][9][10]                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 4. "Diff как Git"

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Diffable = Git for UI                             │
│                                                                      │
│  Как Git diff показывает изменения в коде,                           │
│  Diffable Data Source показывает изменения в данных:                │
│                                                                      │
│  Старый snapshot:        Новый snapshot:                             │
│  ┌──────────────┐        ┌──────────────┐                           │
│  │ Item A       │        │ Item A       │  ← без изменений          │
│  │ Item B       │   →    │ Item B       │  ← без изменений          │
│  │ Item C       │        │ Item D       │  ← ДОБАВЛЕН               │
│  │ Item E       │        │ Item C       │  ← перемещён              │
│  └──────────────┘        │ Item E       │  ← без изменений          │
│                          └──────────────┘                           │
│                                                                      │
│  Diff: +Item D, move Item C after Item B                            │
│  → Только эти изменения анимируются!                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 5. "Estimated = Бюджет"

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Estimated Height = Budget                         │
│                                                                      │
│  Как бюджет на ремонт:                                               │
│  • Оценка: 100,000₽                                                  │
│  • Реальность: может быть 80,000₽ или 150,000₽                      │
│                                                                      │
│  estimatedRowHeight = 80:                                            │
│  • iOS думает: contentSize = 80 * 1000 = 80,000pt                   │
│  • Реально: может быть 50,000pt или 120,000pt                       │
│                                                                      │
│  Зачем нужно:                                                        │
│  • Scroll indicator показывает примерную позицию                    │
│  • scrollToRow работает быстро                                       │
│  • Не нужно вычислять 1000 высот заранее                            │
│                                                                      │
│  Компромисс: точность scroll indicator vs скорость загрузки        │
└─────────────────────────────────────────────────────────────────────┘
```

## Связь с другими темами

**[[android-recyclerview-internals]]** — Android RecyclerView решает те же задачи (cell reuse, prefetching, diffing), но с другой архитектурой: ViewHolder pattern vs UITableViewCell reuse, DiffUtil vs NSDiffableDataSourceSnapshot, ItemDecoration vs UICollectionViewFlowLayout. Сравнение двух подходов раскрывает универсальные принципы производительности скролла (минимизация работы в onBindViewHolder/cellForRowAt, асинхронная загрузка изображений) и платформо-специфичные оптимизации. Обязательно для кросс-платформенных разработчиков.

**[[ios-view-rendering]]** — производительность скролла напрямую зависит от rendering pipeline: каждая ячейка проходит через layout-display-prepare-commit цикл, и если суммарное время превышает frame budget (16.67ms при 60 FPS), происходит dropped frame. Понимание offscreen rendering, blending и rasterization помогает диагностировать причины jank-а в списках. Рекомендуется как обязательный prerequisite перед оптимизацией скролла.

**[[ios-performance-profiling]]** — Instruments (Core Animation instrument, Time Profiler, Allocations) является основным инструментом для диагностики проблем скролла: Color Blended Layers показывает overdraw, Color Offscreen-Rendered выделяет дорогие операции рендеринга, а Time Profiler выявляет bottleneck-и в cellForRowAt. Без владения Instruments оптимизация скролла сводится к гаданию.

---

## Источники и дальнейшее чтение

### Теоретические основы
- Wagner R. A., Fischer M. J. (1974). *The String-to-String Correction Problem.* JACM — алгоритм edit distance (основа Diffable Data Sources)
- Gamma E. et al. (1994). *Design Patterns.* Addison-Wesley — Object Pool, Flyweight patterns
- Weber E. H. (1834). *De Pulsu, Resorptione, Auditu Et Tactu.* — закон восприятия изменений (применим к FPS drops)

### Практические руководства
- Keur C., Hillegass A. (2020). *iOS Programming: Big Nerd Ranch Guide.* — UITableView, UICollectionView, cell reuse
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — Diffable Data Sources, Compositional Layout
- WWDC 2021: [Make blazing fast lists and collection views](https://developer.apple.com/videos/play/wwdc2021/10252/)

### WWDC Sessions

| Год | Сессия | Тема |
|-----|--------|------|
| 2019 | [Advances in Collection View Layout](https://developer.apple.com/videos/play/wwdc2019/215/) | Compositional Layout |
| 2019 | [Advances in UI Data Sources](https://developer.apple.com/videos/play/wwdc2019/220/) | Diffable Data Source |
| 2020 | [Advances in Diffable Data Sources](https://developer.apple.com/videos/play/wwdc2020/10045/) | Section Snapshots |
| 2021 | [Make blazing fast lists and collection views](https://developer.apple.com/videos/play/wwdc2021/10252/) | Cell Configuration |

### Apple Documentation

- [UITableView](https://developer.apple.com/documentation/uikit/uitableview)
- [UICollectionView](https://developer.apple.com/documentation/uikit/uicollectionview)
- [UICollectionViewCompositionalLayout](https://developer.apple.com/documentation/uikit/uicollectionviewcompositionallayout)
- [Prefetching Collection View Data](https://developer.apple.com/documentation/uikit/uicollectionviewdatasourceprefetching)

---

## Проверь себя

> [!question]- Почему dequeueReusableCell критически важен для производительности скролла?
> Без cell reuse для списка из 10000 элементов создастся 10000 UITableViewCell в памяти. С reuse создаётся только ~15 ячеек (видимые + буфер). dequeueReusableCell переиспользует ячейки, вышедшие за экран, для новых данных. Это экономит память и время инициализации.

> [!question]- Скролл дёргается при быстром пролистывании ленты с изображениями. Назовите 3 вероятных причины.
> 1) Загрузка/декодирование изображений на main thread (нужно async декодирование на background queue). 2) Отсутствие кеширования (каждый раз скачивание заново). 3) Сложный layout в cellForRowAt -- Auto Layout пересчёт или тяжёлые shadow/cornerRadius без shouldRasterize.

> [!question]- Почему prefetchDataSource улучшает UX при бесконечном скролле?
> UICollectionViewDataSourcePrefetching вызывает prefetchItemsAt для ячеек, которые скоро появятся. Это позволяет начать загрузку данных/изображений заранее, до того как ячейка станет видимой. Пользователь видит уже загруженный контент вместо placeholder.

---

## Ключевые карточки

Как работает cell reuse в UITableView/UICollectionView?
?
register(_:forCellReuseIdentifier:) регистрирует тип ячейки. dequeueReusableCell(withIdentifier:for:) возвращает переиспользованную или новую ячейку. prepareForReuse() вызывается перед повторным использованием для очистки состояния.

Какое время на один кадр при 60/120 FPS?
?
60 FPS = 16.67ms на кадр, 120 FPS (ProMotion) = 8.33ms. Всё, что выполняется в cellForRowAt, layoutSubviews и draw(_:), должно укладываться в этот бюджет. Превышение = dropped frames = jank.

Что такое Self-Sizing Cells?
?
Ячейки, которые автоматически определяют высоту через Auto Layout. Требуется tableView.rowHeight = UITableView.automaticDimension и estimatedRowHeight. Constraints внутри ячейки должны полностью определять высоту от top до bottom contentView.

Как оптимизировать тени и скругления для скролла?
?
layer.shadowPath = UIBezierPath вместо dynamic shadow calculation. layer.shouldRasterize = true для кеширования. cornerRadius через layer.cornerCurve = .continuous. Избегать masksToBounds + shadow одновременно (вызывает off-screen rendering).

Что такое Compositional Layout?
?
UICollectionViewCompositionalLayout (iOS 13+) -- декларативный layout из Item -> Group -> Section. Поддерживает orthogonal scrolling, estimated sizes, supplementary views. Заменяет UICollectionViewFlowLayout для сложных layouts.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-view-rendering]] | Понять render pipeline для оптимизации |
| Углубиться | [[ios-performance-profiling]] | Использовать Instruments для диагностики jank |
| Смежная тема | [[android-recyclerview-internals]] | Сравнить RecyclerView с UICollectionView |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |

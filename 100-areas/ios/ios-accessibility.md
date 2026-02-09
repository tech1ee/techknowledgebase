---
title: "Доступность iOS-приложений"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
area: ios
tags:
  - topic/ios
  - topic/swift
  - topic/accessibility
  - type/deep-dive
  - level/intermediate
related:
  - "[[ios-swiftui]]"
  - "[[ios-uikit-fundamentals]]"
---

# iOS Accessibility: Разработка доступных приложений

## TL;DR

iOS accessibility — это набор API и практик для создания приложений, доступных всем пользователям независимо от их физических возможностей. Включает поддержку VoiceOver (скринридер), Dynamic Type (масштабирование текста), цветовых контрастов, управления жестами и других вспомогательных технологий. Apple предоставляет мощные инструменты как для UIKit, так и для SwiftUI.

**Ключевые компоненты:**
- VoiceOver — озвучивание интерфейса для незрячих пользователей
- Dynamic Type — адаптивные размеры текста
- Цветовые контрасты и режимы повышенной контрастности
- Reduce Motion — уменьшение анимаций при чувствительности к движению
- Switch Control и Voice Control — альтернативные методы управления

## Зачем это нужно?

### Статистика и влияние

**Масштаб проблемы:**
- **15% населения планеты** (более 1 миллиарда человек) имеют ту или иную форму инвалидности
- **253 миллиона** людей живут с нарушениями зрения
- **466 миллионов** человек имеют проблемы со слухом
- **8% мужчин** и **0.5% женщин** страдают дальтонизмом
- **35% пользователей iOS** используют Dynamic Type в настройках

**Бизнес-причины:**
- Расширение аудитории на 15%+ потенциальных пользователей
- Требование законодательства (ADA в США, EU Web Accessibility Directive)
- Улучшение рейтинга в App Store (Apple продвигает accessible apps)
- Повышение общего UX для всех пользователей (curb-cut effect)

**Технические причины:**
- App Store может отклонить приложения с критическими проблемами доступности
- Лучшая структура кода и архитектура (семантическая разметка)
- Автоматизированное UI тестирование становится проще

### Curb-Cut Effect

Решения для людей с ограниченными возможностями улучшают опыт для всех:
- **Пониженные бордюры** (curb cuts) — созданы для инвалидных колясок, но полезны родителям с колясками, велосипедистам, путешественникам с чемоданами
- **Dynamic Type** — помогает людям с плохим зрением, но также удобен для чтения в движущемся транспорте
- **Voice Control** — критичен для людей с двигательными нарушениями, но полезен при вождении или готовке

## Жизненные аналогии

### 1. Библиотека для всех

Представьте библиотеку, где:
- **Книги** — ваши UI элементы
- **Таблички с названиями** — `accessibilityLabel`
- **Система каталогов** — порядок `accessibilityElements`
- **Аудиокниги** — VoiceOver озвучивание

Плохая библиотека: книги без названий, случайный порядок, нет навигации.
Хорошая библиотека: четкие ярлыки, логичная структура, альтернативные форматы.

### 2. Дорожные знаки

UI элементы — это дорожные знаки:
- **Форма знака** — `accessibilityTraits` (кнопка, заголовок, изображение)
- **Текст на знаке** — `accessibilityLabel`
- **Дополнительная информация** — `accessibilityHint`
- **Расстояние до объекта** — `accessibilityValue`

Без accessibility — как езда по городу без знаков: можно добраться, но сложно.

### 3. Универсальный пульт

Accessibility API — это универсальный пульт управления:
- **VoiceOver** — голосовое управление
- **Switch Control** — одна кнопка для всего
- **Voice Control** — команды голосом
- **Клавиатура** — табуляция между элементами

Хорошее приложение работает с любым "пультом", не только с сенсорным экраном.

### 4. Ресторанное меню

Меню ресторана = ваш интерфейс:
- **Крупный шрифт** — Dynamic Type
- **Описания блюд** — accessibility hints
- **Картинки** — должны иметь текстовые описания
- **Цветовые маркеры** (острота) — не полагаться только на цвет

Хорошее меню понятно всем: детям, пожилым, иностранцам, людям с нарушениями зрения.

## UIKit Accessibility: Полное руководство

### Базовые свойства доступности

```swift
// Базовая настройка доступности для UIView
class ProfileButton: UIButton {
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupAccessibility()
    }

    func setupAccessibility() {
        // Элемент должен быть доступен для VoiceOver
        isAccessibilityElement = true

        // Метка — что это за элемент (озвучивается VoiceOver)
        accessibilityLabel = "Профиль пользователя"

        // Подсказка — что произойдет при активации (опционально)
        accessibilityHint = "Открывает настройки профиля"

        // Черты — тип элемента (кнопка, заголовок, etc)
        accessibilityTraits = .button

        // Значение — текущее состояние (для динамических элементов)
        // accessibilityValue = "Подключен"
    }

    func updateUserStatus(_ status: String) {
        // Обновление значения при изменении состояния
        accessibilityValue = status
    }
}
```

### Группировка элементов

```swift
// Группировка связанных элементов
class UserCardView: UIView {
    let avatarImageView = UIImageView()
    let nameLabel = UILabel()
    let roleLabel = UILabel()
    let statusBadge = UIView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupSubviews()
        setupAccessibility()
    }

    private func setupAccessibility() {
        // Вся карточка — один accessibility элемент
        isAccessibilityElement = true
        accessibilityTraits = .button

        // Субвью не должны быть отдельными элементами
        avatarImageView.isAccessibilityElement = false
        nameLabel.isAccessibilityElement = false
        roleLabel.isAccessibilityElement = false
        statusBadge.isAccessibilityElement = false

        // Комбинированная метка со всей информацией
        updateAccessibilityLabel()
    }

    func configure(name: String, role: String, status: String) {
        nameLabel.text = name
        roleLabel.text = role
        updateAccessibilityLabel()
    }

    private func updateAccessibilityLabel() {
        let name = nameLabel.text ?? ""
        let role = roleLabel.text ?? ""
        let status = getStatusDescription()

        accessibilityLabel = "\(name), \(role), \(status)"
        accessibilityHint = "Нажмите, чтобы открыть профиль"
    }

    private func getStatusDescription() -> String {
        // Преобразование визуального статуса в описание
        return "в сети" // или "не в сети", "отошел"
    }
}
```

### Контейнеры и порядок элементов

```swift
// Кастомный порядок navigation для VoiceOver
class CustomLayoutView: UIView {
    let headerLabel = UILabel()
    let primaryButton = UIButton()
    let secondaryButton = UIButton()
    let footerLabel = UILabel()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupSubviews()
        setupAccessibility()
    }

    private func setupAccessibility() {
        // Эта вьюха — контейнер accessibility элементов
        isAccessibilityElement = false

        // Явно определяем порядок навигации VoiceOver
        // По умолчанию — слева направо, сверху вниз
        // Но иногда логический порядок отличается от визуального
        accessibilityElements = [
            headerLabel,
            primaryButton,
            secondaryButton,
            footerLabel
        ]

        // Настройка индивидуальных элементов
        headerLabel.accessibilityTraits = .header
        primaryButton.accessibilityHint = "Главное действие"
        secondaryButton.accessibilityHint = "Дополнительное действие"
    }
}
```

### Dynamic Type поддержка

```swift
// Адаптивные шрифты с UIKit
class ArticleViewController: UIViewController {
    let titleLabel = UILabel()
    let bodyTextView = UITextView()
    let timestampLabel = UILabel()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupDynamicType()

        // Подписка на изменения размера текста
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleContentSizeChange),
            name: UIContentSizeCategory.didChangeNotification,
            object: nil
        )
    }

    private func setupDynamicType() {
        // Использование предпочтительных шрифтов
        titleLabel.font = UIFont.preferredFont(forTextStyle: .title1)
        titleLabel.adjustsFontForContentSizeCategory = true

        bodyTextView.font = UIFont.preferredFont(forTextStyle: .body)
        bodyTextView.adjustsFontForContentSizeCategory = true

        timestampLabel.font = UIFont.preferredFont(forTextStyle: .caption1)
        timestampLabel.adjustsFontForContentSizeCategory = true

        // Важно: включить многострочность
        titleLabel.numberOfLines = 0

        // Для кастомных шрифтов
        setupCustomDynamicFont()
    }

    private func setupCustomDynamicFont() {
        // Масштабирование кастомного шрифта
        let customFont = UIFont(name: "CustomFont-Bold", size: 17) ?? .systemFont(ofSize: 17)
        let scaledFont = UIFontMetrics(forTextStyle: .body).scaledFont(for: customFont)

        // Применение
        // someLabel.font = scaledFont
    }

    @objc private func handleContentSizeChange() {
        // Обновление layout при изменении размера текста
        view.setNeedsLayout()
        view.layoutIfNeeded()
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
```

### Кастомные Actions

```swift
// Дополнительные действия для VoiceOver
class MessageCell: UITableViewCell {
    let messageLabel = UILabel()
    let timestampLabel = UILabel()

    var onReply: (() -> Void)?
    var onDelete: (() -> Void)?
    var onForward: (() -> Void)?

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupAccessibility()
    }

    private func setupAccessibility() {
        isAccessibilityElement = true
        accessibilityTraits = .button

        // Кастомные действия для VoiceOver
        // Пользователь может свайпнуть вверх/вниз для выбора действия
        accessibilityCustomActions = [
            UIAccessibilityCustomAction(
                name: "Ответить",
                target: self,
                selector: #selector(handleReply)
            ),
            UIAccessibilityCustomAction(
                name: "Переслать",
                target: self,
                selector: #selector(handleForward)
            ),
            UIAccessibilityCustomAction(
                name: "Удалить",
                target: self,
                selector: #selector(handleDelete)
            )
        ]
    }

    @objc private func handleReply() -> Bool {
        onReply?()
        return true // true = действие выполнено успешно
    }

    @objc private func handleForward() -> Bool {
        onForward?()
        return true
    }

    @objc private func handleDelete() -> Bool {
        onDelete?()
        return true
    }

    func configure(message: String, timestamp: String) {
        messageLabel.text = message
        timestampLabel.text = timestamp

        accessibilityLabel = "Сообщение: \(message), отправлено \(timestamp)"
        accessibilityHint = "Доступны действия: ответить, переслать, удалить"
    }
}
```

### Accessibility Notifications

```swift
// Уведомление VoiceOver о динамических изменениях
class LoadingViewController: UIViewController {
    let loadingIndicator = UIActivityIndicatorView()
    let statusLabel = UILabel()

    func startLoading() {
        loadingIndicator.startAnimating()
        statusLabel.text = "Загрузка данных..."

        // Объявление об изменении экрана
        UIAccessibility.post(
            notification: .screenChanged,
            argument: statusLabel
        )
    }

    func finishLoading(items: [String]) {
        loadingIndicator.stopAnimating()
        statusLabel.text = "Загружено \(items.count) элементов"

        // Объявление о важном изменении
        UIAccessibility.post(
            notification: .announcement,
            argument: "Загрузка завершена. Найдено \(items.count) элементов"
        )
    }

    func showError(_ error: String) {
        statusLabel.text = error

        // Объявление с более высоким приоритетом
        UIAccessibility.post(
            notification: .announcement,
            argument: "Ошибка: \(error)"
        )

        // Вибрация для привлечения внимания
        UINotificationFeedbackGenerator().notificationOccurred(.error)
    }
}
```

## SwiftUI Accessibility: Полное руководство

### Базовые модификаторы

```swift
// Основные accessibility модификаторы в SwiftUI
struct ProfileButton: View {
    let userName: String
    let isOnline: Bool

    var body: some View {
        HStack {
            Circle()
                .fill(isOnline ? Color.green : Color.gray)
                .frame(width: 12, height: 12)

            Text(userName)
                .font(.headline)

            Image(systemName: "chevron.right")
                .font(.caption)
        }
        .padding()
        .background(Color.secondary.opacity(0.1))
        .cornerRadius(12)
        // Объединение всех элементов в один accessibility элемент
        .accessibilityElement(children: .combine)
        // Метка — что это за элемент
        .accessibilityLabel("Профиль пользователя \(userName)")
        // Значение — текущее состояние
        .accessibilityValue(isOnline ? "в сети" : "не в сети")
        // Подсказка — что произойдет
        .accessibilityHint("Открывает настройки профиля")
        // Черты — тип элемента
        .accessibilityAddTraits(.isButton)
    }
}

// Пример использования
struct ProfileView: View {
    var body: some View {
        VStack {
            ProfileButton(userName: "Анна Иванова", isOnline: true)
            ProfileButton(userName: "Петр Сидоров", isOnline: false)
        }
    }
}
```

### Группировка и иерархия

```swift
// Управление accessibility иерархией
struct UserCard: View {
    let user: User

    var body: some View {
        HStack(spacing: 16) {
            // Аватар
            AsyncImage(url: user.avatarURL) { image in
                image.resizable()
            } placeholder: {
                Color.gray
            }
            .frame(width: 60, height: 60)
            .clipShape(Circle())
            // Аватар — декоративный, не нужен для VoiceOver
            .accessibilityHidden(true)

            VStack(alignment: .leading, spacing: 4) {
                Text(user.name)
                    .font(.headline)

                Text(user.role)
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                HStack {
                    Image(systemName: "star.fill")
                        .foregroundColor(.yellow)
                    Text("\(user.rating, specifier: "%.1f")")
                        .font(.caption)
                }
            }
        }
        .padding()
        // Вся карточка — один accessibility элемент
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("""
            \(user.name), \(user.role), \
            рейтинг \(user.rating, specifier: "%.1f") из 5
            """)
        .accessibilityAddTraits(.isButton)
        .accessibilityHint("Открывает профиль пользователя")
    }
}

struct User {
    let name: String
    let role: String
    let rating: Double
    let avatarURL: URL
}
```

### Кастомные Actions

```swift
// SwiftUI accessibility actions
struct MessageRow: View {
    let message: Message

    @State private var showReplySheet = false
    @State private var showDeleteAlert = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(message.sender)
                .font(.headline)

            Text(message.text)
                .font(.body)

            Text(message.timestamp)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color.secondary.opacity(0.1))
        .cornerRadius(12)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("""
            Сообщение от \(message.sender): \(message.text), \
            отправлено \(message.timestamp)
            """)
        // Кастомные действия для VoiceOver
        .accessibilityAction(named: "Ответить") {
            showReplySheet = true
        }
        .accessibilityAction(named: "Переслать") {
            forwardMessage()
        }
        .accessibilityAction(named: "Удалить") {
            showDeleteAlert = true
        }
        .sheet(isPresented: $showReplySheet) {
            ReplyView(message: message)
        }
        .alert("Удалить сообщение?", isPresented: $showDeleteAlert) {
            Button("Удалить", role: .destructive) {
                deleteMessage()
            }
            Button("Отмена", role: .cancel) {}
        }
    }

    private func forwardMessage() {
        // Логика пересылки
    }

    private func deleteMessage() {
        // Логика удаления
    }
}

struct Message {
    let sender: String
    let text: String
    let timestamp: String
}
```

### Dynamic Type с @ScaledMetric

```swift
// Адаптивные размеры с @ScaledMetric
struct ArticleView: View {
    // Базовый размер: 16pt, автоматически масштабируется
    @ScaledMetric(relativeTo: .body) var iconSize: CGFloat = 24
    @ScaledMetric(relativeTo: .title1) var headerSpacing: CGFloat = 20

    let article: Article

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: headerSpacing) {
                // Заголовок с Dynamic Type
                Text(article.title)
                    .font(.title)
                    .fontWeight(.bold)

                // Метаданные
                HStack {
                    Image(systemName: "clock")
                        .frame(width: iconSize, height: iconSize)

                    Text(article.readingTime)
                        .font(.subheadline)

                    Spacer()

                    Image(systemName: "bookmark")
                        .frame(width: iconSize, height: iconSize)
                }
                .foregroundColor(.secondary)

                Divider()

                // Основной текст
                Text(article.content)
                    .font(.body)
                    .lineSpacing(8)
            }
            .padding()
        }
        // Важно: поддержка Dynamic Type включена по умолчанию
        // для системных шрифтов в SwiftUI
    }
}

// Кастомный шрифт с Dynamic Type
struct CustomFontView: View {
    var body: some View {
        Text("Кастомный шрифт")
            .font(.custom("CustomFont-Bold", size: 17, relativeTo: .body))
        // relativeTo: .body означает, что размер будет масштабироваться
        // относительно настроек пользователя для body text
    }
}

struct Article {
    let title: String
    let readingTime: String
    let content: String
}
```

### AccessibilityFocusState

```swift
// Управление фокусом VoiceOver
struct LoginView: View {
    @State private var username = ""
    @State private var password = ""
    @State private var errorMessage = ""
    @State private var showError = false

    // Управление VoiceOver фокусом
    @AccessibilityFocusState private var isErrorFocused: Bool

    var body: some View {
        VStack(spacing: 20) {
            TextField("Имя пользователя", text: $username)
                .textFieldStyle(.roundedBorder)
                .textContentType(.username)
                .accessibilityLabel("Имя пользователя")

            SecureField("Пароль", text: $password)
                .textFieldStyle(.roundedBorder)
                .textContentType(.password)
                .accessibilityLabel("Пароль")

            if showError {
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.red)
                    Text(errorMessage)
                        .foregroundColor(.red)
                }
                .padding()
                .background(Color.red.opacity(0.1))
                .cornerRadius(8)
                // Привязка фокуса VoiceOver к сообщению об ошибке
                .accessibilityFocused($isErrorFocused)
                .accessibilityAddTraits(.isStaticText)
            }

            Button("Войти") {
                login()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }

    private func login() {
        // Валидация
        if username.isEmpty || password.isEmpty {
            errorMessage = "Заполните все поля"
            showError = true

            // Перемещение фокуса VoiceOver на сообщение об ошибке
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                isErrorFocused = true
            }
            return
        }

        // Логика входа...
    }
}
```

### Accessibility Rotors

```swift
// Кастомные роторы для быстрой навигации
struct LongArticleView: View {
    let article: LongArticle

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text(article.title)
                        .font(.largeTitle)
                        .id("title")
                        .accessibilityAddTraits(.isHeader)

                    ForEach(article.sections) { section in
                        VStack(alignment: .leading, spacing: 12) {
                            Text(section.heading)
                                .font(.title2)
                                .fontWeight(.semibold)
                                .id(section.id)
                                .accessibilityAddTraits(.isHeader)

                            Text(section.content)
                                .font(.body)

                            if let image = section.image {
                                Image(image)
                                    .resizable()
                                    .scaledToFit()
                                    .accessibilityLabel(section.imageDescription ?? "")
                            }
                        }
                    }
                }
                .padding()
            }
            // Кастомный ротор для навигации по заголовкам
            .accessibilityRotor("Заголовки") {
                AccessibilityRotorEntry("Название статьи", id: "title")

                ForEach(article.sections) { section in
                    AccessibilityRotorEntry(section.heading, id: section.id)
                }
            }
            // Ротор для навигации по изображениям
            .accessibilityRotor("Изображения") {
                ForEach(article.sections.filter { $0.image != nil }) { section in
                    AccessibilityRotorEntry(
                        section.imageDescription ?? "Изображение",
                        id: section.id
                    )
                }
            }
        }
    }
}

struct LongArticle {
    let title: String
    let sections: [Section]

    struct Section: Identifiable {
        let id: String
        let heading: String
        let content: String
        let image: String?
        let imageDescription: String?
    }
}
```

### Reduce Motion поддержка

```swift
// Адаптация анимаций для Reduce Motion
struct AnimatedButton: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var isPressed = false

    var body: some View {
        Button("Нажми меня") {
            handlePress()
        }
        .scaleEffect(isPressed ? 0.95 : 1.0)
        .animation(
            reduceMotion ? .none : .spring(response: 0.3, dampingFraction: 0.6),
            value: isPressed
        )
    }

    private func handlePress() {
        isPressed = true

        // Обратная связь через вибрацию (не зависит от Reduce Motion)
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            isPressed = false
        }
    }
}

// Альтернативный контент при Reduce Motion
struct LoadingView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    var body: some View {
        Group {
            if reduceMotion {
                // Статичный индикатор
                Image(systemName: "hourglass")
                    .font(.largeTitle)
                    .foregroundColor(.secondary)
            } else {
                // Анимированный индикатор
                ProgressView()
                    .scaleEffect(1.5)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityLabel("Загрузка")
    }
}
```

## Цвета и контрастность

### UIKit: Semantic Colors

```swift
// Использование системных цветов с поддержкой Dark Mode
class ThemedView: UIView {
    let titleLabel = UILabel()
    let subtitleLabel = UILabel()
    let containerView = UIView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupColors()
    }

    private func setupColors() {
        // Системные цвета автоматически адаптируются к Dark Mode
        backgroundColor = .systemBackground

        // Метки
        titleLabel.textColor = .label // Основной текст
        subtitleLabel.textColor = .secondaryLabel // Вторичный текст

        // Контейнеры
        containerView.backgroundColor = .secondarySystemBackground

        // Кастомные цвета с поддержкой Dark Mode
        let customColor = UIColor { traitCollection in
            switch traitCollection.userInterfaceStyle {
            case .dark:
                return UIColor(red: 0.2, green: 0.2, blue: 0.2, alpha: 1.0)
            default:
                return UIColor(red: 0.95, green: 0.95, blue: 0.95, alpha: 1.0)
            }
        }

        // Проверка контрастности
        checkColorContrast()
    }

    private func checkColorContrast() {
        // WCAG требует контраст минимум 4.5:1 для обычного текста
        // и 3:1 для крупного текста (18pt+ или 14pt+ bold)

        // Для критичных UI элементов используйте высококонтрастные цвета
        let highContrastEnabled = UIAccessibility.isDarkerSystemColorsEnabled

        if highContrastEnabled {
            // Увеличение контрастности при включенном режиме
            titleLabel.textColor = .label
            containerView.backgroundColor = .tertiarySystemBackground
        }
    }

    override func traitCollectionDidChange(_ previousTraitCollection: UITraitCollection?) {
        super.traitCollectionDidChange(previousTraitCollection)

        // Обновление при изменении темы или контрастности
        if traitCollection.hasDifferentColorAppearance(comparedTo: previousTraitCollection) {
            setupColors()
        }
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
```

### SwiftUI: Adaptive Colors

```swift
// Адаптивные цвета в SwiftUI
struct ThemedCard: View {
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.colorSchemeContrast) var contrast

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Заголовок")
                .font(.headline)
                .foregroundColor(.primary) // Автоматически адаптируется

            Text("Описание")
                .font(.body)
                .foregroundColor(.secondary)

            HStack {
                Image(systemName: "star.fill")
                    .foregroundColor(.yellow)

                Text("4.8")
                    .foregroundColor(ratingColor)
            }
        }
        .padding()
        .background(cardBackground)
        .cornerRadius(12)
        .shadow(
            color: shadowColor,
            radius: contrast == .increased ? 0 : 8
        )
    }

    // Адаптивный фон карточки
    private var cardBackground: Color {
        switch contrast {
        case .increased:
            // Повышенный контраст — более явное разделение
            return colorScheme == .dark ? Color.black : Color.white
        default:
            return Color(uiColor: .secondarySystemBackground)
        }
    }

    // Цвет рейтинга с учетом контрастности
    private var ratingColor: Color {
        contrast == .increased ? .primary : .orange
    }

    // Тень только при стандартном контрасте
    private var shadowColor: Color {
        contrast == .increased ? .clear : Color.black.opacity(0.1)
    }
}

// Кастомные цвета с Asset Catalog
struct BrandedButton: View {
    var body: some View {
        Button("Главная кнопка") {
            // Действие
        }
        .padding()
        .background(
            // Цвет из Assets.xcassets с поддержкой Dark Mode
            Color("BrandPrimary")
        )
        .foregroundColor(
            Color("BrandTextOnPrimary")
        )
        .cornerRadius(12)
    }
}

// Проверка дальтонизма
struct ColorBlindFriendlyChart: View {
    let data: [DataPoint]

    var body: some View {
        HStack(spacing: 8) {
            ForEach(data) { point in
                VStack {
                    Rectangle()
                        .fill(point.color)
                        .frame(width: 40)
                        .frame(height: CGFloat(point.value) * 2)

                    // Не полагаемся только на цвет — добавляем паттерн
                    if point.isImportant {
                        Image(systemName: "star.fill")
                            .foregroundColor(.yellow)
                    }

                    Text(point.label)
                        .font(.caption)
                }
                // Accessibility: описание включает цвет И значение
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(point.label): \(point.value)")
            }
        }
    }
}

struct DataPoint: Identifiable {
    let id = UUID()
    let label: String
    let value: Int
    let color: Color
    let isImportant: Bool
}
```

## 6 типичных ошибок

### ❌ Ошибка 1: Кнопки без меток

```swift
// UIKit — ПЛОХО
class BadButtonExample: UIButton {
    override init(frame: CGRect) {
        super.init(frame: frame)
        setImage(UIImage(systemName: "gear"), for: .normal)
        // accessibilityLabel не установлен!
        // VoiceOver скажет просто "button" без описания
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// SwiftUI — ПЛОХО
struct BadButtonExampleSwiftUI: View {
    var body: some View {
        Button(action: openSettings) {
            Image(systemName: "gear")
        }
        // Без метки — VoiceOver не поймет назначение
    }

    func openSettings() {}
}
```

```swift
// ✅ UIKit — ХОРОШО
class GoodButtonExample: UIButton {
    override init(frame: CGRect) {
        super.init(frame: frame)
        setImage(UIImage(systemName: "gear"), for: .normal)

        // Явная метка для VoiceOver
        accessibilityLabel = "Настройки"
        accessibilityHint = "Открывает экран настроек приложения"
        accessibilityTraits = .button
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// ✅ SwiftUI — ХОРОШО
struct GoodButtonExampleSwiftUI: View {
    var body: some View {
        Button(action: openSettings) {
            Image(systemName: "gear")
        }
        .accessibilityLabel("Настройки")
        .accessibilityHint("Открывает экран настроек приложения")
    }

    func openSettings() {}
}
```

### ❌ Ошибка 2: Декоративные элементы как accessibility элементы

```swift
// UIKit — ПЛОХО
class BadCardView: UIView {
    let iconImageView = UIImageView()
    let titleLabel = UILabel()
    let descriptionLabel = UILabel()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupSubviews()

        // Все элементы доступны для VoiceOver
        // VoiceOver озвучит: "Image, Title, Description"
        // вместо одного логического элемента
        iconImageView.isAccessibilityElement = true
        titleLabel.isAccessibilityElement = true
        descriptionLabel.isAccessibilityElement = true
    }

    func setupSubviews() {
        // Добавление subviews...
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// SwiftUI — ПЛОХО
struct BadCardViewSwiftUI: View {
    var body: some View {
        HStack {
            Image(systemName: "star.fill")
                // Декоративная иконка доступна для VoiceOver

            VStack(alignment: .leading) {
                Text("Заголовок")
                Text("Описание")
            }
        }
        // VoiceOver будет озвучивать каждый элемент отдельно
    }
}
```

```swift
// ✅ UIKit — ХОРОШО
class GoodCardView: UIView {
    let iconImageView = UIImageView()
    let titleLabel = UILabel()
    let descriptionLabel = UILabel()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupSubviews()
        setupAccessibility()
    }

    private func setupAccessibility() {
        // Вся карточка — один accessibility элемент
        isAccessibilityElement = true
        accessibilityTraits = .button

        // Субвью — НЕ accessibility элементы
        iconImageView.isAccessibilityElement = false
        titleLabel.isAccessibilityElement = false
        descriptionLabel.isAccessibilityElement = false

        // Комбинированная метка
        updateAccessibilityLabel()
    }

    func configure(title: String, description: String) {
        titleLabel.text = title
        descriptionLabel.text = description
        updateAccessibilityLabel()
    }

    private func updateAccessibilityLabel() {
        accessibilityLabel = """
            \(titleLabel.text ?? ""), \(descriptionLabel.text ?? "")
            """
    }

    func setupSubviews() {
        // Добавление subviews...
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// ✅ SwiftUI — ХОРОШО
struct GoodCardViewSwiftUI: View {
    let title: String
    let description: String

    var body: some View {
        HStack {
            Image(systemName: "star.fill")
                .accessibilityHidden(true) // Декоративный элемент

            VStack(alignment: .leading) {
                Text(title)
                Text(description)
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title), \(description)")
        .accessibilityAddTraits(.isButton)
    }
}
```

### ❌ Ошибка 3: Фиксированные размеры текста

```swift
// UIKit — ПЛОХО
class BadTextLabel: UILabel {
    override init(frame: CGRect) {
        super.init(frame: frame)

        // Фиксированный размер шрифта
        font = UIFont.systemFont(ofSize: 17)
        // Не масштабируется при изменении настроек Dynamic Type
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// SwiftUI — ПЛОХО
struct BadTextView: View {
    var body: some View {
        Text("Текст")
            .font(.system(size: 17))
        // Фиксированный размер — не адаптируется
    }
}
```

```swift
// ✅ UIKit — ХОРОШО
class GoodTextLabel: UILabel {
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupDynamicType()
    }

    private func setupDynamicType() {
        // Предпочтительный шрифт — автоматически масштабируется
        font = UIFont.preferredFont(forTextStyle: .body)
        adjustsFontForContentSizeCategory = true

        // Многострочность для больших размеров текста
        numberOfLines = 0
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// ✅ SwiftUI — ХОРОШО
struct GoodTextView: View {
    var body: some View {
        Text("Текст")
            .font(.body) // Системный стиль — автоматически масштабируется

        // Или для кастомного шрифта:
        Text("Кастомный текст")
            .font(.custom("MyFont-Regular", size: 17, relativeTo: .body))
    }
}
```

### ❌ Ошибка 4: Информация только через цвет

```swift
// UIKit — ПЛОХО
class BadStatusIndicator: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)

        // Статус передается ТОЛЬКО цветом
        backgroundColor = .green // "Все хорошо"
        // Люди с дальтонизмом не различат разницу между
        // красным (ошибка) и зеленым (успех)

        layer.cornerRadius = 8
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// SwiftUI — ПЛОХО
struct BadStatusView: View {
    let isSuccess: Bool

    var body: some View {
        Circle()
            .fill(isSuccess ? Color.green : Color.red)
            .frame(width: 20, height: 20)
        // Только цвет — недостаточно информации
    }
}
```

```swift
// ✅ UIKit — ХОРОШО
class GoodStatusIndicator: UIView {
    let iconImageView = UIImageView()
    let statusLabel = UILabel()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupSubviews()
    }

    func setStatus(isSuccess: Bool) {
        // Цвет + иконка + текст
        if isSuccess {
            backgroundColor = .systemGreen
            iconImageView.image = UIImage(systemName: "checkmark.circle.fill")
            statusLabel.text = "Успешно"
            accessibilityLabel = "Статус: успешно"
        } else {
            backgroundColor = .systemRed
            iconImageView.image = UIImage(systemName: "xmark.circle.fill")
            statusLabel.text = "Ошибка"
            accessibilityLabel = "Статус: ошибка"
        }

        iconImageView.tintColor = .white
        statusLabel.textColor = .white

        // Accessibility
        isAccessibilityElement = true
        accessibilityTraits = .staticText
    }

    private func setupSubviews() {
        addSubview(iconImageView)
        addSubview(statusLabel)
        // Layout...
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// ✅ SwiftUI — ХОРОШО
struct GoodStatusView: View {
    let isSuccess: Bool

    var body: some View {
        HStack {
            // Иконка + цвет + текст
            Image(systemName: isSuccess ? "checkmark.circle.fill" : "xmark.circle.fill")
                .foregroundColor(isSuccess ? .green : .red)

            Text(isSuccess ? "Успешно" : "Ошибка")
                .fontWeight(.medium)
        }
        .padding(8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(isSuccess ? Color.green.opacity(0.1) : Color.red.opacity(0.1))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Статус: \(isSuccess ? "успешно" : "ошибка")")
    }
}
```

### ❌ Ошибка 5: Игнорирование обновлений состояния

```swift
// UIKit — ПЛОХО
class BadLoadingView: UIViewController {
    let statusLabel = UILabel()
    let loadingIndicator = UIActivityIndicatorView()

    func startLoading() {
        loadingIndicator.startAnimating()
        statusLabel.text = "Загрузка..."

        // VoiceOver не узнает об изменении состояния!
        // Пользователь не поймет, что началась загрузка
    }

    func finishLoading() {
        loadingIndicator.stopAnimating()
        statusLabel.text = "Готово"

        // VoiceOver не узнает о завершении
    }
}

// SwiftUI — ПЛОХО
struct BadLoadingViewSwiftUI: View {
    @State private var isLoading = false

    var body: some View {
        VStack {
            if isLoading {
                ProgressView()
                Text("Загрузка...")
            } else {
                Text("Готово")
            }
        }
        // VoiceOver не получит уведомление об изменении
    }
}
```

```swift
// ✅ UIKit — ХОРОШО
class GoodLoadingView: UIViewController {
    let statusLabel = UILabel()
    let loadingIndicator = UIActivityIndicatorView()

    func startLoading() {
        loadingIndicator.startAnimating()
        statusLabel.text = "Загрузка..."

        // Уведомление VoiceOver об изменении
        UIAccessibility.post(
            notification: .announcement,
            argument: "Начата загрузка данных"
        )

        // Или переключение фокуса на новый элемент
        UIAccessibility.post(
            notification: .screenChanged,
            argument: statusLabel
        )
    }

    func finishLoading(itemCount: Int) {
        loadingIndicator.stopAnimating()
        statusLabel.text = "Загружено \(itemCount) элементов"

        // Объявление о завершении
        UIAccessibility.post(
            notification: .announcement,
            argument: "Загрузка завершена. Найдено \(itemCount) элементов"
        )

        // Тактильная обратная связь
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
    }
}

// ✅ SwiftUI — ХОРОШО
struct GoodLoadingViewSwiftUI: View {
    @State private var isLoading = false
    @State private var itemCount = 0
    @AccessibilityFocusState private var isStatusFocused: Bool

    var body: some View {
        VStack {
            if isLoading {
                ProgressView()
                Text("Загрузка...")
                    .accessibilityFocused($isStatusFocused)
            } else {
                Text("Загружено \(itemCount) элементов")
                    .accessibilityFocused($isStatusFocused)
            }
        }
        .onChange(of: isLoading) { _, newValue in
            if newValue {
                // Фокус на индикаторе загрузки
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                    isStatusFocused = true
                }
            }
        }
        .onChange(of: itemCount) { _, newCount in
            if !isLoading && newCount > 0 {
                // Объявление о результатах
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                    isStatusFocused = true
                }
            }
        }
    }
}
```

### ❌ Ошибка 6: Игнорирование Reduce Motion

```swift
// UIKit — ПЛОХО
class BadAnimatedButton: UIButton {
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesBegan(touches, with: event)

        // Сложная анимация без учета Reduce Motion
        UIView.animate(
            withDuration: 0.3,
            delay: 0,
            usingSpringWithDamping: 0.5,
            initialSpringVelocity: 0.5,
            options: [],
            animations: {
                self.transform = CGAffineTransform(scaleX: 1.2, y: 1.2)
            }
        )
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesEnded(touches, with: event)

        UIView.animate(
            withDuration: 0.5,
            delay: 0,
            usingSpringWithDamping: 0.3,
            initialSpringVelocity: 1.0,
            options: [],
            animations: {
                self.transform = .identity
            }
        )
    }
}

// SwiftUI — ПЛОХО
struct BadAnimatedCard: View {
    @State private var isExpanded = false

    var body: some View {
        VStack {
            Text("Карточка")
        }
        .frame(height: isExpanded ? 200 : 100)
        .animation(.spring(response: 0.6, dampingFraction: 0.4), value: isExpanded)
        // Пружинная анимация может вызывать дискомфорт
        .onTapGesture {
            isExpanded.toggle()
        }
    }
}
```

```swift
// ✅ UIKit — ХОРОШО
class GoodAnimatedButton: UIButton {
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesBegan(touches, with: event)

        let reduceMotion = UIAccessibility.isReduceMotionEnabled

        if reduceMotion {
            // Простая мгновенная обратная связь
            alpha = 0.7

            // Тактильная обратная связь вместо анимации
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        } else {
            // Стандартная анимация
            UIView.animate(
                withDuration: 0.2,
                animations: {
                    self.transform = CGAffineTransform(scaleX: 0.95, y: 0.95)
                }
            )
        }
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesEnded(touches, with: event)

        let reduceMotion = UIAccessibility.isReduceMotionEnabled

        if reduceMotion {
            alpha = 1.0
        } else {
            UIView.animate(
                withDuration: 0.2,
                animations: {
                    self.transform = .identity
                }
            )
        }
    }
}

// ✅ SwiftUI — ХОРОШО
struct GoodAnimatedCard: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var isExpanded = false

    var body: some View {
        VStack {
            Text("Карточка")
        }
        .frame(height: isExpanded ? 200 : 100)
        .animation(
            reduceMotion ? .none : .easeInOut(duration: 0.3),
            value: isExpanded
        )
        .onTapGesture {
            isExpanded.toggle()

            // Тактильная обратная связь при Reduce Motion
            if reduceMotion {
                let generator = UIImpactFeedbackGenerator(style: .medium)
                generator.impactOccurred()
            }
        }
    }
}
```

## Ментальные модели

### 1. Accessibility Tree — параллельная структура UI

Думайте об accessibility как о параллельном дереве элементов:

```
Visual Tree:              Accessibility Tree:
┌─────────────┐          ┌──────────────────────┐
│  Container  │          │   Container          │
│  ┌────┬────┐│          │   ├─ Button: "Save"  │
│  │Icon│Text││    →     │   ├─ Label: "Title"  │
│  └────┴────┘│          │   └─ Value: "Draft"  │
└─────────────┘          └──────────────────────┘
```

**Принципы:**
- Визуальное дерево ≠ accessibility дерево
- Некоторые элементы визуальны, но не нужны для accessibility (декорации)
- Некоторые элементы нужны для accessibility, но невизуальны (hints)
- Контролируйте оба дерева явно

### 2. Progressive Enhancement — слои доступности

Accessibility — это не "включить/выключить", а слои улучшений:

```
Уровень 1: Базовый
├─ Все интерактивные элементы имеют метки
├─ Логический порядок навигации
└─ Текст масштабируется

Уровень 2: Расширенный
├─ Hints для сложных действий
├─ Кастомные actions
├─ Ротры для навигации
└─ Семантические traits

Уровень 3: Оптимальный
├─ Live regions для обновлений
├─ Управление фокусом
├─ Альтернативный контент при Reduce Motion
└─ Адаптация под увеличенный контраст
```

Начинайте с уровня 1, постепенно добавляя улучшения.

### 3. POUR принципы (W3C)

**Perceivable (Воспринимаемый):**
- Текстовые альтернативы изображений
- Цветовой контраст минимум 4.5:1
- Не полагайтесь только на цвет

**Operable (Управляемый):**
- Все функции доступны с клавиатуры/VoiceOver
- Достаточное время для взаимодействия
- Нет мигающего контента >3 раз в секунду

**Understandable (Понятный):**
- Понятный язык и термины
- Предсказуемое поведение
- Помощь при ошибках

**Robust (Надежный):**
- Совместимость с вспомогательными технологиями
- Валидная семантическая разметка
- Корректные accessibility traits

### 4. Shift-Left Testing — доступность с первого дня

Традиционный подход:
```
Design → Develop → Test Accessibility → Fix → Ship
                        ↑
                   Проблемы находятся поздно
```

Shift-Left подход:
```
Design with A11y → Develop with A11y → Validate → Ship
   ↓                    ↓                  ↓
Wireframes        Code review        Automated tests
с labels          с VoiceOver        с Accessibility Inspector
```

**Практика:**
- Accessibility labels в дизайн-макетах
- Code review проверяет accessibility
- CI/CD включает accessibility тесты
- Регулярное тестирование с VoiceOver

## Чеклист тестирования

### Базовая проверка (must-have)

- [ ] **VoiceOver Navigation**
  - Включить VoiceOver (Settings → Accessibility → VoiceOver)
  - Свайп вправо/влево — все элементы озвучены понятно
  - Двойной тап — все кнопки активируются
  - Порядок навигации логичен (сверху вниз, слева направо)

- [ ] **Dynamic Type**
  - Settings → Display & Brightness → Text Size
  - Протестировать минимальный (XS) и максимальный (XXXL) размеры
  - Текст не обрезается, layout адаптируется
  - Иконки масштабируются с @ScaledMetric

- [ ] **Color & Contrast**
  - Settings → Accessibility → Display → Increase Contrast
  - Все элементы UI остаются различимыми
  - Проверить с Accessibility Inspector (Xcode → Color Contrast)
  - Минимальный контраст 4.5:1 для текста, 3:1 для UI элементов

- [ ] **Reduce Motion**
  - Settings → Accessibility → Motion → Reduce Motion
  - Анимации отключены или упрощены
  - Функциональность сохраняется без анимаций
  - Альтернативная обратная связь (вибрация)

### Продвинутая проверка

- [ ] **Switch Control**
  - Settings → Accessibility → Switch Control
  - Все элементы доступны через последовательную навигацию
  - Группировка элементов логична

- [ ] **Voice Control**
  - Settings → Accessibility → Voice Control
  - Команды "Tap [label]" работают для всех кнопок
  - Элементы имеют уникальные понятные имена

- [ ] **Dark Mode**
  - Settings → Display & Brightness → Dark
  - Цвета адаптируются корректно
  - Контраст сохраняется в обоих режимах

- [ ] **Landscape Orientation**
  - Повернуть устройство
  - Layout адаптируется
  - Accessibility labels не меняются

- [ ] **Accessibility Inspector (Xcode)**
  - Xcode → Open Developer Tool → Accessibility Inspector
  - Audit → Run Audit
  - Исправить все ошибки и предупреждения

### Автоматизированное тестирование

```swift
// XCTest UI Testing с accessibility
class AccessibilityUITests: XCTestCase {
    func testVoiceOverNavigation() {
        let app = XCUIApplication()
        app.launch()

        // Проверка наличия accessibility labels
        XCTAssertTrue(app.buttons["Настройки"].exists)
        XCTAssertTrue(app.staticTexts["Добро пожаловать"].exists)

        // Проверка traits
        let settingsButton = app.buttons["Настройки"]
        XCTAssertTrue(settingsButton.isAccessibilityElement)
    }

    func testDynamicType() {
        let app = XCUIApplication()

        // Тестирование с разными размерами текста
        app.launchArguments = ["-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryXXXL"]
        app.launch()

        // Проверка, что UI не ломается при больших размерах
        XCTAssertTrue(app.staticTexts["Title"].exists)
    }

    func testColorContrast() {
        let app = XCUIApplication()
        app.launchArguments = ["-UIAccessibilityDarkerSystemColorsEnabled", "YES"]
        app.launch()

        // Проверка UI при повышенной контрастности
        // Все элементы должны быть видимы
    }
}
```

### Инструменты для тестирования

**Xcode:**
- **Accessibility Inspector** — инспекция элементов, аудит, эмуляция настроек
- **Environment Overrides** — быстрое переключение Dynamic Type, Dark Mode
- **Simulator** — тестирование на разных устройствах

**Устройство:**
- **Accessibility Shortcut** — тройное нажатие Home/Power для VoiceOver
- **Settings → Accessibility** — все настройки доступности

**Сторонние инструменты:**
- **Contrast** (Mac app) — проверка цветового контраста
- **Color Oracle** — симуляция дальтонизма
- **Stark** (Figma plugin) — проверка контраста в дизайне

## Связанные темы

- [[ios-swiftui]] — декларативный UI фреймворк с встроенной accessibility
- [[ios-uikit]] — императивный UI фреймворк с мощными accessibility API
- [[ios-testing]] — автоматизированное тестирование accessibility
- [[ios-design-system]] — семантические токены для доступных интерфейсов
- [[ios-localization]] — локализация и адаптация для разных регионов
- [[ios-dark-mode]] — адаптивные темы и цветовые схемы
- [[ios-animations]] — анимации с учетом Reduce Motion
- [[ios-voiceover]] — глубокое погружение в VoiceOver API
- [[ios-wcag]] — Web Content Accessibility Guidelines для iOS
- [[ios-inclusive-design]] — философия инклюзивного дизайна

---

**Источники:**
- [Apple Human Interface Guidelines — Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [WWDC — Design for Everyone](https://developer.apple.com/videos/accessibility/)
- [W3C WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- [Apple Accessibility Documentation](https://developer.apple.com/documentation/accessibility)

**Статистика:**
- WHO Global Report on Disability (2021)
- Apple Accessibility Features Usage Report (2025)
- WebAIM Screen Reader Survey (2024)

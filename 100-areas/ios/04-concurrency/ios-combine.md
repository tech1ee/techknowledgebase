---
title: "Combine Framework: реактивное программирование в iOS"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/reactive
  - type/deep-dive
  - level/advanced
related:
  - "[[kotlin-flow]]"
  - "[[swift-concurrency]]"
  - "[[async-await]]"
prerequisites:
  - "[[ios-threading-fundamentals]]"
  - "[[ios-state-management]]"
---

# Combine Framework - Реактивное программирование в iOS

## TL;DR

Combine - это декларативный Swift фреймворк от Apple для обработки асинхронных событий с помощью комбинирования операторов. Представьте конвейер завода: данные (сырьё) поступают от Publisher, проходят через Operators (обработка), и попадают к Subscriber (готовый продукт). Combine автоматически управляет lifecycle, backpressure и memory management через AnyCancellable.

**Аналогия**: Combine как водопроводная система - Publisher это кран, Operators это фильтры и трубы, Subscriber это ваша чашка. Вода течёт по трубам, очищается фильтрами, и вы контролируете поток краном (Demand).

```
Publisher → [Operators] → Subscriber
   🚰    →  [🔧 🔧 🔧] →     🥤
  (кран)   (обработка)    (чашка)
```

---

## Основные концепции

### Publishers и Subscribers Protocol

**Publisher** - источник значений, который может генерировать элементы определённого типа и завершиться (с успехом или ошибкой).

```
        Publisher<Output, Failure>
              |
              | emit values
              ↓
    ┌─────────────────────┐
    │   Value Stream      │
    │  ○ → ○ → ○ → ◉     │
    │  (values) (complete) │
    └─────────────────────┘
              |
              | subscribe
              ↓
        Subscriber<Input, Failure>
```

**Subscriber** - получатель значений, который запрашивает определённое количество элементов (Demand).

```swift
// Publisher protocol (упрощённо)
protocol Publisher {
    associatedtype Output
    associatedtype Failure: Error

    func receive<S: Subscriber>(subscriber: S)
        where S.Input == Output, S.Failure == Failure
}

// Subscriber protocol (упрощённо)
protocol Subscriber {
    associatedtype Input
    associatedtype Failure: Error

    func receive(subscription: Subscription)
    func receive(_ input: Input) -> Subscribers.Demand
    func receive(completion: Subscribers.Completion<Failure>)
}
```

### Жизненный цикл подписки

```
┌──────────┐                    ┌────────────┐
│Publisher │                    │ Subscriber │
└────┬─────┘                    └─────┬──────┘
     │                                │
     │◄───── subscribe(subscriber) ───┤
     │                                │
     ├──── send(subscription) ───────►│
     │                                │
     │◄──── request(.unlimited) ──────┤
     │                                │
     ├──────── send(value) ──────────►│
     ├──────── send(value) ──────────►│
     ├──────── send(value) ──────────►│
     │                                │
     ├──── send(.finished) ──────────►│
     │                                │
```

---

## Встроенные Publishers

### Just - Единичное значение

Публикует одно значение и сразу завершается. Никогда не падает (Failure = Never).

```swift
let publisher = Just(42)

publisher
    .sink { value in
        print("Получено: \(value)")
    }
// Output: Получено: 42

// Практический пример: дефолтное значение
func loadUserSettings() -> AnyPublisher<Settings, Error> {
    URLSession.shared
        .dataTaskPublisher(for: settingsURL)
        .tryMap { try JSONDecoder().decode(Settings.self, from: $0.data) }
        .catch { _ in Just(Settings.default) } // fallback
        .eraseToAnyPublisher()
}
```

### Future - Асинхронная операция

Выполняет closure один раз и публикует результат. Идеально для callback-based API.

```swift
func fetchUserProfile(id: String) -> AnyPublisher<User, Error> {
    Future<User, Error> { promise in
        // Legacy API с callback
        LegacyAPI.getUser(id: id) { result in
            switch result {
            case .success(let user):
                promise(.success(user))
            case .failure(let error):
                promise(.failure(error))
            }
        }
    }
    .eraseToAnyPublisher()
}

// Использование
fetchUserProfile(id: "123")
    .sink(
        receiveCompletion: { completion in
            if case .failure(let error) = completion {
                print("Ошибка: \(error)")
            }
        },
        receiveValue: { user in
            print("Пользователь: \(user.name)")
        }
    )
```

### Deferred - Ленивое создание

Создаёт Publisher только при подписке. Полезно для повторяющихся запросов.

```swift
// БЕЗ Deferred - создаётся сразу
let eagerPublisher = URLSession.shared
    .dataTaskPublisher(for: url) // запрос уходит СЕЙЧАС

// С Deferred - создаётся при подписке
let lazyPublisher = Deferred {
    URLSession.shared
        .dataTaskPublisher(for: url) // запрос уходит при .sink
}

// Практический пример: retry с новым timestamp
func fetchWithTimestamp() -> AnyPublisher<Data, Error> {
    Deferred {
        let timestamp = Date().timeIntervalSince1970
        let urlWithTimestamp = URL(string: "https://api.com/data?t=\(timestamp)")!
        return URLSession.shared.dataTaskPublisher(for: urlWithTimestamp)
            .map(\.data)
            .mapError { $0 as Error }
    }
    .eraseToAnyPublisher()
}

fetchWithTimestamp()
    .retry(3) // каждый retry получит НОВЫЙ timestamp
```

### PassthroughSubject - Транзитная передача

Передаёт значения подписчикам без хранения текущего значения.

```swift
class SearchViewModel: ObservableObject {
    private let searchSubject = PassthroughSubject<String, Never>()
    @Published var results: [SearchResult] = []
    private var cancellables = Set<AnyCancellable>()

    init() {
        searchSubject
            .debounce(for: 0.3, scheduler: DispatchQueue.main)
            .removeDuplicates()
            .flatMap { query -> AnyPublisher<[SearchResult], Never> in
                self.performSearch(query: query)
                    .catch { _ in Just([]) }
                    .eraseToAnyPublisher()
            }
            .assign(to: &$results)
    }

    func search(query: String) {
        searchSubject.send(query)
    }

    private func performSearch(query: String) -> AnyPublisher<[SearchResult], Error> {
        // API call
    }
}

// SwiftUI Usage
struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()
    @State private var searchText = ""

    var body: some View {
        List(viewModel.results) { result in
            Text(result.title)
        }
        .searchable(text: $searchText)
        .onChange(of: searchText) { newValue in
            viewModel.search(query: newValue)
        }
    }
}
```

### CurrentValueSubject - С текущим значением

Хранит и публикует текущее значение. Новые подписчики сразу получают последнее значение.

```swift
class AuthenticationManager: ObservableObject {
    @Published var isAuthenticated = false

    // Хранит текущий токен
    private let tokenSubject = CurrentValueSubject<String?, Never>(nil)
    private var cancellables = Set<AnyCancellable>()

    var currentToken: String? {
        tokenSubject.value // можно читать текущее значение
    }

    init() {
        // При изменении токена обновляем статус аутентификации
        tokenSubject
            .map { $0 != nil }
            .assign(to: &$isAuthenticated)
    }

    func login(token: String) {
        tokenSubject.send(token)
    }

    func logout() {
        tokenSubject.send(nil)
    }

    // Любой запрос может использовать актуальный токен
    func makeAuthenticatedRequest<T: Decodable>(
        _ endpoint: URL
    ) -> AnyPublisher<T, Error> {
        tokenSubject
            .compactMap { $0 } // фильтруем nil
            .first() // берём первое значение
            .flatMap { token -> AnyPublisher<T, Error> in
                var request = URLRequest(url: endpoint)
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

                return URLSession.shared
                    .dataTaskPublisher(for: request)
                    .tryMap { try JSONDecoder().decode(T.self, from: $0.data) }
                    .eraseToAnyPublisher()
            }
            .eraseToAnyPublisher()
    }
}
```

---

## Операторы (Operators)

### Трансформация: map, flatMap, compactMap

```swift
// map - преобразует каждое значение
[1, 2, 3].publisher
    .map { $0 * 2 }
    .sink { print($0) }
// Output: 2, 4, 6

// compactMap - фильтрует nil
["1", "abc", "3"].publisher
    .compactMap { Int($0) }
    .sink { print($0) }
// Output: 1, 3

// flatMap - преобразует в Publisher и объединяет
struct User {
    let id: String
    let name: String
}

func fetchUser(id: String) -> AnyPublisher<User, Error> { /*...*/ }
func fetchPosts(userId: String) -> AnyPublisher<[Post], Error> { /*...*/ }

// Получить посты для пользователя
fetchUser(id: "123")
    .flatMap { user in
        fetchPosts(userId: user.id)
            .map { posts in (user, posts) }
    }
    .sink(
        receiveCompletion: { _ in },
        receiveValue: { user, posts in
            print("\(user.name) имеет \(posts.count) постов")
        }
    )
```

**Различие map vs flatMap**:
```
┌─────────┐
│  map    │  Input → Output (простое преобразование)
└─────────┘  1 → "1", 2 → "2", 3 → "3"

┌──────────┐
│ flatMap  │  Input → Publisher<Output> (асинхронное преобразование)
└──────────┘  1 → Publisher([1,2]), 2 → Publisher([3,4])
              Result: [1,2,3,4] (объединяет все publishers)
```

### Фильтрация: filter, removeDuplicates

```swift
// filter - пропускает только подходящие значения
[1, 2, 3, 4, 5].publisher
    .filter { $0 % 2 == 0 }
    .sink { print($0) }
// Output: 2, 4

// removeDuplicates - убирает последовательные дубликаты
["a", "a", "b", "b", "b", "c", "a"].publisher
    .removeDuplicates()
    .sink { print($0) }
// Output: "a", "b", "c", "a"

// Практический пример: фильтрация пользовательского ввода
class FormViewModel: ObservableObject {
    @Published var email = ""
    @Published var isEmailValid = false

    private var cancellables = Set<AnyCancellable>()

    init() {
        $email
            .removeDuplicates() // избегаем лишних проверок
            .map { email in
                let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
                return NSPredicate(format: "SELF MATCHES %@", emailRegex)
                    .evaluate(with: email)
            }
            .assign(to: &$isEmailValid)
    }
}
```

### Временные операторы: debounce, throttle, delay

```swift
// debounce - ждёт паузу перед отправкой
searchTextField.publisher
    .debounce(for: 0.5, scheduler: RunLoop.main)
    .sink { query in
        // Выполнится только когда пользователь перестанет печатать на 0.5 сек
        performSearch(query)
    }

// throttle - ограничивает частоту (первое или последнее значение в интервале)
locationUpdates
    .throttle(for: 1.0, scheduler: RunLoop.main, latest: true)
    .sink { location in
        // Максимум одно обновление в секунду
        updateMap(location)
    }

// delay - задерживает все значения
Just("Hello")
    .delay(for: 2.0, scheduler: RunLoop.main)
    .sink { print($0) } // выведет через 2 секунды
```

**Визуальное сравнение**:
```
Input:     ●──●●──●●●────●──●──●
                              time →

debounce:  ─────────●─────────────●
           (ждёт паузу)

throttle:  ●────────●────────────●
           (первое в интервале)
```

### Комбинирование: merge, combineLatest, zip

```swift
// merge - объединяет несколько publishers одного типа
let publisher1 = PassthroughSubject<Int, Never>()
let publisher2 = PassthroughSubject<Int, Never>()

publisher1
    .merge(with: publisher2)
    .sink { print($0) }

publisher1.send(1) // Output: 1
publisher2.send(2) // Output: 2
publisher1.send(3) // Output: 3

// combineLatest - комбинирует последние значения
let username = PassthroughSubject<String, Never>()
let password = PassthroughSubject<String, Never>()

username
    .combineLatest(password)
    .map { username, password in
        username.count >= 3 && password.count >= 6
    }
    .sink { isValid in
        submitButton.isEnabled = isValid
    }

username.send("ab")   // не выведет (password не было)
password.send("123")  // Output: false (ab.count < 3)
username.send("abc")  // Output: false (123.count < 6)
password.send("123456") // Output: true

// zip - ждёт пары значений
let numbers = [1, 2, 3].publisher
let letters = ["A", "B", "C"].publisher

numbers
    .zip(letters)
    .sink { print("\($0) - \($1)") }
// Output:
// 1 - A
// 2 - B
// 3 - C
```

**Визуализация**:
```
Publisher1: ─1───────2─────3───►
Publisher2: ───A──B─────C──────►

merge:      ─1─A─────2B────3C──►
            (все события по порядку)

combineLatest: ──(1,A)(2,A)(2,B)(2,C)(3,C)──►
               (комбинации последних)

zip:        ───(1,A)──(2,B)──(3,C)──►
            (строгие пары)
```

### Практический пример: параллельная загрузка

```swift
struct DashboardData {
    let user: User
    let notifications: [Notification]
    let stats: Stats
}

func loadDashboard() -> AnyPublisher<DashboardData, Error> {
    let userPublisher = fetchUser()
    let notificationsPublisher = fetchNotifications()
    let statsPublisher = fetchStats()

    return Publishers.Zip3(
        userPublisher,
        notificationsPublisher,
        statsPublisher
    )
    .map { user, notifications, stats in
        DashboardData(
            user: user,
            notifications: notifications,
            stats: stats
        )
    }
    .eraseToAnyPublisher()
}

// Использование в SwiftUI
class DashboardViewModel: ObservableObject {
    @Published var dashboardData: DashboardData?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private var cancellables = Set<AnyCancellable>()

    func load() {
        isLoading = true

        loadDashboard()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] data in
                    self?.dashboardData = data
                }
            )
            .store(in: &cancellables)
    }
}
```

---

## Обработка ошибок

### catch - Обработать ошибку и продолжить

```swift
func fetchImage(url: URL) -> AnyPublisher<UIImage, Never> {
    URLSession.shared
        .dataTaskPublisher(for: url)
        .map { UIImage(data: $0.data) ?? UIImage() }
        .catch { error -> Just<UIImage> in
            print("Ошибка загрузки: \(error)")
            return Just(UIImage(systemName: "photo")!) // placeholder
        }
        .eraseToAnyPublisher()
}

// Цепочка с fallback
fetchImageFromCache(id: "123")
    .catch { _ in fetchImageFromServer(id: "123") }
    .catch { _ in Just(defaultImage) }
    .sink { image in
        imageView.image = image
    }
```

### retry - Повторная попытка

```swift
func fetchDataWithRetry() -> AnyPublisher<Data, Error> {
    URLSession.shared
        .dataTaskPublisher(for: url)
        .map(\.data)
        .retry(3) // повторить до 3 раз при ошибке
        .eraseToAnyPublisher()
}

// Retry с задержкой (кастомный оператор)
extension Publisher {
    func retry<S: Scheduler>(
        _ times: Int,
        withDelay delay: S.SchedulerTimeType.Stride,
        scheduler: S
    ) -> AnyPublisher<Output, Failure> {
        self.catch { error -> AnyPublisher<Output, Failure> in
            if times > 0 {
                return Just(())
                    .delay(for: delay, scheduler: scheduler)
                    .flatMap { _ in
                        self.retry(times - 1, withDelay: delay, scheduler: scheduler)
                    }
                    .eraseToAnyPublisher()
            } else {
                return Fail(error: error).eraseToAnyPublisher()
            }
        }
        .eraseToAnyPublisher()
    }
}

// Использование
fetchData()
    .retry(3, withDelay: .seconds(2), scheduler: DispatchQueue.main)
```

### mapError - Преобразование типа ошибки

```swift
enum NetworkError: Error {
    case invalidResponse
    case decodingFailed
    case serverError(Int)
}

func fetchUser(id: String) -> AnyPublisher<User, NetworkError> {
    URLSession.shared
        .dataTaskPublisher(for: userURL)
        .mapError { _ in NetworkError.invalidResponse }
        .tryMap { data, response -> Data in
            guard let httpResponse = response as? HTTPURLResponse,
                  200..<300 ~= httpResponse.statusCode else {
                throw NetworkError.serverError(
                    (response as? HTTPURLResponse)?.statusCode ?? 0
                )
            }
            return data
        }
        .decode(type: User.self, decoder: JSONDecoder())
        .mapError { error in
            if error is DecodingError {
                return NetworkError.decodingFailed
            }
            return error as? NetworkError ?? .invalidResponse
        }
        .eraseToAnyPublisher()
}
```

---

## Backpressure и Demand

**Backpressure** - механизм контроля потока данных, когда Subscriber указывает сколько значений он готов обработать.

```swift
class CustomSubscriber: Subscriber {
    typealias Input = Int
    typealias Failure = Never

    func receive(subscription: Subscription) {
        // Запросить только 3 значения
        subscription.request(.max(3))
    }

    func receive(_ input: Int) -> Subscribers.Demand {
        print("Получено: \(input)")

        if input % 2 == 0 {
            // Запросить ещё одно при чётном
            return .max(1)
        } else {
            // Не запрашивать новые
            return .none
        }
    }

    func receive(completion: Subscribers.Completion<Never>) {
        print("Завершено")
    }
}

// Визуализация Demand
let publisher = (1...10).publisher
let subscriber = CustomSubscriber()

publisher.subscribe(subscriber)
```

**Demand пример**:
```
Initial request: .max(3)

Publisher:  1 → 2 → 3 → 4 → 5 → 6 ...
            ↓   ↓   ↓   ↓   ↓   ↓
Demand:     3   2   3   2   3   2 ...
           (3) (2+1) (2+1) ...
```

### Практический пример: батчинг

```swift
extension Publisher {
    func batch(size: Int) -> AnyPublisher<[Output], Failure> {
        self.collect(size)
            .eraseToAnyPublisher()
    }
}

// Загрузка по 10 элементов
dataStream
    .batch(size: 10)
    .sink { batch in
        processBatch(batch) // обрабатываем по 10 элементов
    }
```

---

## AnyCancellable и управление памятью

### Отмена подписок

```swift
class NewsViewModel: ObservableObject {
    @Published var articles: [Article] = []

    // Хранение подписок
    private var cancellables = Set<AnyCancellable>()

    func loadNews() {
        fetchNews()
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { [weak self] articles in
                    self?.articles = articles
                }
            )
            .store(in: &cancellables) // автоматическая отмена при deinit
    }

    func cancelAll() {
        cancellables.removeAll() // отменить все подписки
    }

    deinit {
        // cancellables автоматически отменятся
        print("NewsViewModel deinitialized")
    }
}
```

### Ручная отмена

```swift
class SearchViewController: UIViewController {
    private var searchCancellable: AnyCancellable?

    func searchButtonTapped() {
        // Отменить предыдущий поиск
        searchCancellable?.cancel()

        searchCancellable = performSearch()
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { results in
                    self.updateUI(with: results)
                }
            )
    }
}
```

### Утечки памяти и retain cycles

```swift
// ❌ НЕПРАВИЛЬНО - retain cycle
class ProfileViewModel {
    var cancellables = Set<AnyCancellable>()

    func loadProfile() {
        fetchProfile()
            .sink { profile in
                self.updateUI(profile) // strong self
            }
            .store(in: &cancellables)
    }
}

// ✅ ПРАВИЛЬНО - weak self
class ProfileViewModel {
    var cancellables = Set<AnyCancellable>()

    func loadProfile() {
        fetchProfile()
            .sink { [weak self] profile in
                self?.updateUI(profile)
            }
            .store(in: &cancellables)
    }
}

// ✅ ПРАВИЛЬНО - assign автоматически использует weak
class ProfileViewModel: ObservableObject {
    @Published var profile: Profile?
    var cancellables = Set<AnyCancellable>()

    func loadProfile() {
        fetchProfile()
            .assign(to: &$profile) // безопасно, использует weak
    }
}
```

---

## assign(to:) для @Published привязки

### Современный синтаксис (iOS 14+)

```swift
class WeatherViewModel: ObservableObject {
    @Published var temperature: Double = 0
    @Published var conditions: String = ""
    @Published var isLoading = false

    private var cancellables = Set<AnyCancellable>()

    func loadWeather() {
        isLoading = true

        fetchWeather()
            .map(\.temperature)
            .assign(to: &$temperature) // автоматически weak, не нужен store(in:)

        fetchWeather()
            .map(\.conditions)
            .assign(to: &$conditions)

        fetchWeather()
            .map { _ in false }
            .assign(to: &$isLoading)
    }
}
```

### Устаревший синтаксис (iOS 13)

```swift
class WeatherViewModel: ObservableObject {
    @Published var temperature: Double = 0
    private var cancellables = Set<AnyCancellable>()

    func loadWeather() {
        fetchWeather()
            .map(\.temperature)
            .assign(to: \.temperature, on: self) // требует weak/unowned
            .store(in: &cancellables)
    }
}
```

### Комплексный пример: форма регистрации

```swift
class RegistrationViewModel: ObservableObject {
    // Input
    @Published var username = ""
    @Published var email = ""
    @Published var password = ""
    @Published var confirmPassword = ""

    // Output
    @Published var isUsernameValid = false
    @Published var isEmailValid = false
    @Published var isPasswordValid = false
    @Published var passwordsMatch = false
    @Published var canSubmit = false

    private var cancellables = Set<AnyCancellable>()

    init() {
        // Валидация username
        $username
            .map { $0.count >= 3 }
            .assign(to: &$isUsernameValid)

        // Валидация email
        $email
            .map { email in
                let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
                return NSPredicate(format: "SELF MATCHES %@", emailRegex)
                    .evaluate(with: email)
            }
            .assign(to: &$isEmailValid)

        // Валидация password
        $password
            .map { $0.count >= 8 }
            .assign(to: &$isPasswordValid)

        // Проверка совпадения паролей
        Publishers.CombineLatest($password, $confirmPassword)
            .map { password, confirm in
                !password.isEmpty && password == confirm
            }
            .assign(to: &$passwordsMatch)

        // Общая валидация формы
        Publishers.CombineLatest4(
            $isUsernameValid,
            $isEmailValid,
            $isPasswordValid,
            $passwordsMatch
        )
        .map { $0 && $1 && $2 && $3 }
        .assign(to: &$canSubmit)
    }
}

// SwiftUI View
struct RegistrationView: View {
    @StateObject private var viewModel = RegistrationViewModel()

    var body: some View {
        Form {
            TextField("Username", text: $viewModel.username)
                .overlay(alignment: .trailing) {
                    if viewModel.isUsernameValid {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                    }
                }

            TextField("Email", text: $viewModel.email)
                .textContentType(.emailAddress)
                .keyboardType(.emailAddress)

            SecureField("Password", text: $viewModel.password)
            SecureField("Confirm Password", text: $viewModel.confirmPassword)

            Button("Register") {
                submitRegistration()
            }
            .disabled(!viewModel.canSubmit)
        }
    }
}
```

---

## Интеграция с URLSession

### Базовый GET запрос

```swift
struct Post: Codable, Identifiable {
    let id: Int
    let title: String
    let body: String
}

func fetchPosts() -> AnyPublisher<[Post], Error> {
    let url = URL(string: "https://jsonplaceholder.typicode.com/posts")!

    return URLSession.shared
        .dataTaskPublisher(for: url)
        .map(\.data)
        .decode(type: [Post].self, decoder: JSONDecoder())
        .receive(on: DispatchQueue.main)
        .eraseToAnyPublisher()
}

// Использование
fetchPosts()
    .sink(
        receiveCompletion: { completion in
            switch completion {
            case .finished:
                print("Загрузка завершена")
            case .failure(let error):
                print("Ошибка: \(error)")
            }
        },
        receiveValue: { posts in
            print("Получено \(posts.count) постов")
        }
    )
    .store(in: &cancellables)
```

### POST запрос с телом

```swift
struct CreatePostRequest: Encodable {
    let title: String
    let body: String
    let userId: Int
}

func createPost(request: CreatePostRequest) -> AnyPublisher<Post, Error> {
    let url = URL(string: "https://jsonplaceholder.typicode.com/posts")!
    var urlRequest = URLRequest(url: url)
    urlRequest.httpMethod = "POST"
    urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

    return Just(request)
        .encode(encoder: JSONEncoder())
        .mapError { $0 as Error }
        .flatMap { data -> AnyPublisher<Post, Error> in
            urlRequest.httpBody = data

            return URLSession.shared
                .dataTaskPublisher(for: urlRequest)
                .tryMap { output in
                    guard let response = output.response as? HTTPURLResponse,
                          200..<300 ~= response.statusCode else {
                        throw URLError(.badServerResponse)
                    }
                    return output.data
                }
                .decode(type: Post.self, decoder: JSONDecoder())
                .eraseToAnyPublisher()
        }
        .eraseToAnyPublisher()
}
```

### Сервис с переиспользуемой логикой

```swift
enum APIError: Error {
    case invalidURL
    case requestFailed(Error)
    case invalidResponse
    case decodingFailed(Error)
}

class APIService {
    private let baseURL = "https://api.example.com"
    private let session: URLSession

    init(session: URLSession = .shared) {
        self.session = session
    }

    func request<T: Decodable>(
        endpoint: String,
        method: String = "GET",
        body: Data? = nil,
        headers: [String: String] = [:]
    ) -> AnyPublisher<T, APIError> {
        guard let url = URL(string: baseURL + endpoint) else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.httpBody = body

        headers.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }

        return session
            .dataTaskPublisher(for: request)
            .mapError { APIError.requestFailed($0) }
            .tryMap { output in
                guard let response = output.response as? HTTPURLResponse,
                      200..<300 ~= response.statusCode else {
                    throw APIError.invalidResponse
                }
                return output.data
            }
            .decode(type: T.self, decoder: JSONDecoder())
            .mapError { error in
                if let apiError = error as? APIError {
                    return apiError
                }
                return APIError.decodingFailed(error)
            }
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

// Использование
class UserRepository {
    private let api = APIService()

    func fetchUsers() -> AnyPublisher<[User], APIError> {
        api.request(endpoint: "/users")
    }

    func createUser(_ user: User) -> AnyPublisher<User, APIError> {
        let encoder = JSONEncoder()
        let body = try? encoder.encode(user)

        return api.request(
            endpoint: "/users",
            method: "POST",
            body: body,
            headers: ["Content-Type": "application/json"]
        )
    }
}
```

---

## Интеграция с NotificationCenter

### Подписка на уведомления

```swift
extension NotificationCenter {
    func publisher(for name: Notification.Name) -> AnyPublisher<Notification, Never> {
        self.publisher(for: name, object: nil)
            .eraseToAnyPublisher()
    }
}

class KeyboardManager: ObservableObject {
    @Published var keyboardHeight: CGFloat = 0
    private var cancellables = Set<AnyCancellable>()

    init() {
        // Клавиатура появляется
        NotificationCenter.default
            .publisher(for: UIResponder.keyboardWillShowNotification)
            .compactMap { notification in
                (notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? NSValue)?
                    .cgRectValue.height
            }
            .assign(to: &$keyboardHeight)

        // Клавиатура скрывается
        NotificationCenter.default
            .publisher(for: UIResponder.keyboardWillHideNotification)
            .map { _ in CGFloat(0) }
            .assign(to: &$keyboardHeight)
    }
}

// SwiftUI использование
struct ContentView: View {
    @StateObject private var keyboardManager = KeyboardManager()

    var body: some View {
        VStack {
            TextField("Enter text", text: .constant(""))
        }
        .padding(.bottom, keyboardManager.keyboardHeight)
        .animation(.default, value: keyboardManager.keyboardHeight)
    }
}
```

### Кастомные уведомления

```swift
extension Notification.Name {
    static let userDidLogin = Notification.Name("userDidLogin")
    static let userDidLogout = Notification.Name("userDidLogout")
}

class SessionManager: ObservableObject {
    @Published var isLoggedIn = false
    private var cancellables = Set<AnyCancellable>()

    init() {
        // Отслеживаем логин
        NotificationCenter.default
            .publisher(for: .userDidLogin)
            .map { _ in true }
            .assign(to: &$isLoggedIn)

        // Отслеживаем логаут
        NotificationCenter.default
            .publisher(for: .userDidLogout)
            .map { _ in false }
            .assign(to: &$isLoggedIn)
    }
}

// Отправка уведомлений
func performLogin() {
    // ... логика логина
    NotificationCenter.default.post(name: .userDidLogin, object: nil)
}

func performLogout() {
    // ... логика логаута
    NotificationCenter.default.post(name: .userDidLogout, object: nil)
}
```

---

## Планирование (Scheduling)

### receive(on:) - Получение на определённой очереди

```swift
// Загрузка в background, обновление UI в main
fetchDataFromNetwork()
    .receive(on: DispatchQueue.main) // переключаемся на main
    .sink { [weak self] data in
        self?.updateUI(with: data) // безопасно обновлять UI
    }
    .store(in: &cancellables)
```

### subscribe(on:) - Подписка на определённой очереди

```swift
// Тяжёлая операция декодирования в background
URLSession.shared
    .dataTaskPublisher(for: url)
    .subscribe(on: DispatchQueue.global(qos: .background)) // подписка в background
    .map(\.data)
    .decode(type: HeavyModel.self, decoder: JSONDecoder())
    .receive(on: DispatchQueue.main) // результат в main
    .sink { model in
        updateUI(model)
    }
```

### Различие receive(on:) vs subscribe(on:)

```
Original Queue: [Main]

Publisher Creation → Subscription → Operators → Sink
     [Main]            [Main]        [Main]    [Main]

С subscribe(on: background):

Publisher Creation → Subscription → Operators → Sink
     [Main]          [Background]  [Background] [Background]
                          ↑
                    перемещает всю цепочку

С receive(on: main):

Publisher Creation → Subscription → Operators → receive(on:) → Sink
  [Background]      [Background]  [Background]   [Main]      [Main]
                                                    ↑
                                            перемещает только после
```

### Практический пример

```swift
class ImageLoader: ObservableObject {
    @Published var image: UIImage?
    @Published var isLoading = false

    private var cancellables = Set<AnyCancellable>()

    func loadImage(from url: URL) {
        isLoading = true

        URLSession.shared
            .dataTaskPublisher(for: url)
            .subscribe(on: DispatchQueue.global(qos: .userInitiated)) // загрузка в background
            .map(\.data)
            .compactMap { UIImage(data: $0) } // декодирование в background
            .receive(on: DispatchQueue.main) // результат в main thread
            .sink(
                receiveCompletion: { [weak self] _ in
                    self?.isLoading = false
                },
                receiveValue: { [weak self] image in
                    self?.image = image
                }
            )
            .store(in: &cancellables)
    }
}
```

---

## Отладка (Debugging)

### print() - Вывод значений

```swift
fetchData()
    .print("📊 Data Stream") // добавляет префикс к логам
    .sink { value in
        // ...
    }

// Output:
// 📊 Data Stream: receive subscription: (DataTaskPublisher)
// 📊 Data Stream: request unlimited
// 📊 Data Stream: receive value: (Data)
// 📊 Data Stream: receive finished
```

### handleEvents() - Перехват событий lifecycle

```swift
fetchUser(id: "123")
    .handleEvents(
        receiveSubscription: { subscription in
            print("🔵 Подписка создана")
        },
        receiveRequest: { demand in
            print("🔵 Запрошено значений: \(demand)")
        },
        receiveCancel: {
            print("🔵 Подписка отменена")
        },
        receiveOutput: { user in
            print("🔵 Получен user: \(user.name)")
        },
        receiveCompletion: { completion in
            print("🔵 Завершено: \(completion)")
        }
    )
    .sink(
        receiveCompletion: { _ in },
        receiveValue: { user in
            updateUI(user)
        }
    )
```

### breakpoint() - Останов при условии

```swift
searchQuery
    .breakpoint(
        receiveOutput: { query in
            query.isEmpty // остановить если пустой запрос
        }
    )
    .sink { query in
        performSearch(query)
    }
```

### Кастомный оператор для логирования

```swift
extension Publisher {
    func log(_ prefix: String = "") -> AnyPublisher<Output, Failure> {
        handleEvents(
            receiveSubscription: { _ in
                print("[\(prefix)] Subscribed")
            },
            receiveOutput: { output in
                print("[\(prefix)] Output: \(output)")
            },
            receiveCompletion: { completion in
                switch completion {
                case .finished:
                    print("[\(prefix)] Completed successfully")
                case .failure(let error):
                    print("[\(prefix)] Failed with error: \(error)")
                }
            },
            receiveCancel: {
                print("[\(prefix)] Cancelled")
            }
        )
        .eraseToAnyPublisher()
    }
}

// Использование
fetchData()
    .log("API Call")
    .map { processData($0) }
    .log("Processing")
    .sink { result in
        updateUI(result)
    }
```

---

## Combine vs async/await: когда использовать каждый

### async/await - для простых асинхронных операций

```swift
// ✅ async/await: простая последовательность
func fetchUserProfile() async throws -> Profile {
    let user = try await fetchUser()
    let posts = try await fetchPosts(userId: user.id)
    let avatar = try await fetchAvatar(userId: user.id)

    return Profile(user: user, posts: posts, avatar: avatar)
}

// ❌ Combine: излишне сложно для простой последовательности
func fetchUserProfile() -> AnyPublisher<Profile, Error> {
    fetchUser()
        .flatMap { user in
            Publishers.Zip(
                fetchPosts(userId: user.id),
                fetchAvatar(userId: user.id)
            )
            .map { posts, avatar in
                Profile(user: user, posts: posts, avatar: avatar)
            }
        }
        .eraseToAnyPublisher()
}
```

### Combine - для реактивных потоков данных

```swift
// ✅ Combine: идеально для реактивности
class SearchViewModel: ObservableObject {
    @Published var searchQuery = ""
    @Published var results: [Result] = []

    init() {
        $searchQuery
            .debounce(for: 0.3, scheduler: RunLoop.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .flatMap { query in
                self.search(query)
                    .catch { _ in Just([]) }
            }
            .assign(to: &$results)
    }
}

// ❌ async/await: не подходит для реактивности
// Нужен ручной Timer, нет автоматического debounce
```

### Когда использовать Combine

1. **Реактивные UI биндинги** (@Published, assign(to:))
2. **Множественные события** (клики, ввод текста, таймеры)
3. **Комбинирование потоков** (combineLatest, merge, zip)
4. **Обработка потоков** (debounce, throttle, distinctUntilChanged)
5. **Отмена операций** (AnyCancellable)

### Когда использовать async/await

1. **Простые последовательные запросы**
2. **Одноразовые асинхронные операции**
3. **Чтение/запись файлов**
4. **Простые сетевые запросы без реактивности**
5. **Миграция с callback-based кода**

### Гибридный подход

```swift
// Combine для UI, async/await для сети
class ProfileViewModel: ObservableObject {
    @Published var profile: Profile?
    @Published var isLoading = false

    private var cancellables = Set<AnyCancellable>()

    func loadProfile() {
        isLoading = true

        // async/await функция обёрнутая в Combine
        Future { promise in
            Task {
                do {
                    let profile = try await self.fetchProfileAsync()
                    promise(.success(profile))
                } catch {
                    promise(.failure(error))
                }
            }
        }
        .receive(on: DispatchQueue.main)
        .sink(
            receiveCompletion: { [weak self] _ in
                self?.isLoading = false
            },
            receiveValue: { [weak self] profile in
                self?.profile = profile
            }
        )
        .store(in: &cancellables)
    }

    // Простая async функция
    private func fetchProfileAsync() async throws -> Profile {
        let user = try await fetchUser()
        let stats = try await fetchStats(userId: user.id)
        return Profile(user: user, stats: stats)
    }
}

// Конвертация async/await в Publisher
extension Future where Failure == Error {
    convenience init(operation: @escaping () async throws -> Output) {
        self.init { promise in
            Task {
                do {
                    let result = try await operation()
                    promise(.success(result))
                } catch {
                    promise(.failure(error))
                }
            }
        }
    }
}

// Использование
Future {
    try await someAsyncFunction()
}
.sink(
    receiveCompletion: { _ in },
    receiveValue: { value in
        print(value)
    }
)
```

---

## Сравнение с Kotlin Flow

См. также: [[kotlin-flow]]

| Аспект | Combine (Swift) | Kotlin Flow |
|--------|----------------|-------------|
| **Publisher** | `Publisher<Output, Failure>` | `Flow<T>` |
| **Холодный поток** | `Deferred { }` | `flow { emit() }` |
| **Горячий поток** | `PassthroughSubject` | `MutableSharedFlow` |
| **С состоянием** | `CurrentValueSubject` | `MutableStateFlow` |
| **Map** | `.map { }` | `.map { }` |
| **Filter** | `.filter { }` | `.filter { }` |
| **FlatMap** | `.flatMap { }` | `.flatMapConcat { }` |
| **Debounce** | `.debounce(for:)` | `.debounce(timeout)` |
| **CombineLatest** | `.combineLatest()` | `.combine()` |
| **Zip** | `.zip()` | `.zip()` |
| **Error handling** | `.catch { }` | `.catch { }` |
| **Threading** | `.receive(on:)` | `.flowOn()` |
| **Collection** | `.collect()` | `.toList()` |
| **Отмена** | `AnyCancellable` | `Job.cancel()` |

### Пример миграции Kotlin → Swift

```kotlin
// Kotlin Flow
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")
    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { query ->
            if (query.isEmpty()) {
                flowOf(emptyList())
            } else {
                searchRepository.search(query)
                    .catch { emit(emptyList()) }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

```swift
// Swift Combine
class SearchViewModel: ObservableObject {
    @Published var searchQuery = ""
    @Published var searchResults: [Result] = []

    private var cancellables = Set<AnyCancellable>()

    init() {
        $searchQuery
            .debounce(for: 0.3, scheduler: DispatchQueue.main)
            .removeDuplicates()
            .flatMap { query -> AnyPublisher<[Result], Never> in
                if query.isEmpty {
                    return Just([]).eraseToAnyPublisher()
                } else {
                    return self.searchRepository.search(query)
                        .catch { _ in Just([]) }
                        .eraseToAnyPublisher()
                }
            }
            .assign(to: &$searchResults)
    }
}
```

---

## 6 типичных ошибок

### ❌ 1. Забыть store(in:) - подписка отменяется сразу

```swift
// ❌ НЕПРАВИЛЬНО
func loadData() {
    fetchData()
        .sink { data in
            self.updateUI(data)
        }
    // Подписка отменится сразу, sink вернёт AnyCancellable который deinit
}

// ✅ ПРАВИЛЬНО
class ViewModel {
    private var cancellables = Set<AnyCancellable>()

    func loadData() {
        fetchData()
            .sink { [weak self] data in
                self?.updateUI(data)
            }
            .store(in: &cancellables) // сохраняем подписку
    }
}
```

### ❌ 2. Retain cycle с self в замыканиях

```swift
// ❌ НЕПРАВИЛЬНО
class ProfileViewModel {
    func loadProfile() {
        fetchProfile()
            .sink { profile in
                self.profile = profile // strong self
            }
            .store(in: &cancellables)
    }
}

// ✅ ПРАВИЛЬНО - weak self
class ProfileViewModel {
    func loadProfile() {
        fetchProfile()
            .sink { [weak self] profile in
                self?.profile = profile
            }
            .store(in: &cancellables)
    }
}

// ✅ ПРАВИЛЬНО - assign (автоматически weak)
class ProfileViewModel: ObservableObject {
    @Published var profile: Profile?

    func loadProfile() {
        fetchProfile()
            .assign(to: &$profile) // безопасно
    }
}
```

### ❌ 3. Не переключиться на main thread для UI

```swift
// ❌ НЕПРАВИЛЬНО
URLSession.shared
    .dataTaskPublisher(for: url)
    .sink { [weak self] output in
        // Выполнится в background thread!
        self?.imageView.image = UIImage(data: output.data) // CRASH
    }

// ✅ ПРАВИЛЬНО
URLSession.shared
    .dataTaskPublisher(for: url)
    .receive(on: DispatchQueue.main) // переключаемся на main
    .sink { [weak self] output in
        self?.imageView.image = UIImage(data: output.data)
    }
```

### ❌ 4. Игнорировать ошибки - pipeline прерывается

```swift
// ❌ НЕПРАВИЛЬНО
searchSubject
    .flatMap { query in
        self.search(query) // если упадёт, весь pipeline умрёт
    }
    .sink { results in
        self.updateResults(results)
    }

// ✅ ПРАВИЛЬНО - обработать ошибку
searchSubject
    .flatMap { query in
        self.search(query)
            .catch { error in
                print("Ошибка: \(error)")
                return Just([]) // продолжить с пустым массивом
            }
    }
    .sink { results in
        self.updateResults(results)
    }

// ✅ ПРАВИЛЬНО - replaceError
searchSubject
    .flatMap { query in
        self.search(query)
            .replaceError(with: []) // заменить ошибку значением
    }
    .sink { results in
        self.updateResults(results)
    }
```

### ❌ 5. Создавать Publisher каждый раз вместо переиспользования

```swift
// ❌ НЕПРАВИЛЬНО - создаёт новый запрос каждый раз
func getUser() -> AnyPublisher<User, Error> {
    URLSession.shared
        .dataTaskPublisher(for: userURL)
        .map(\.data)
        .decode(type: User.self, decoder: JSONDecoder())
        .eraseToAnyPublisher()
}

// Каждый вызов = новый запрос
getUser().sink { user1 in }
getUser().sink { user2 in } // второй запрос!

// ✅ ПРАВИЛЬНО - share() для переиспользования
class UserService {
    private var userPublisher: AnyPublisher<User, Error>?

    func getUser() -> AnyPublisher<User, Error> {
        if let publisher = userPublisher {
            return publisher
        }

        let publisher = URLSession.shared
            .dataTaskPublisher(for: userURL)
            .map(\.data)
            .decode(type: User.self, decoder: JSONDecoder())
            .share() // делится результатом между подписчиками
            .eraseToAnyPublisher()

        userPublisher = publisher
        return publisher
    }
}

// ✅ ПРАВИЛЬНО - multicast для горячего потока
let sharedPublisher = URLSession.shared
    .dataTaskPublisher(for: url)
    .map(\.data)
    .multicast { PassthroughSubject<Data, URLError>() }

// Подписаться несколько раз
sharedPublisher.sink { data1 in }
sharedPublisher.sink { data2 in }

// Запустить ОДИН запрос для всех
sharedPublisher.connect()
```

### ❌ 6. Путать subscribe(on:) и receive(on:)

```swift
// ❌ НЕПРАВИЛЬНО - receive(on:) не влияет на подписку
URLSession.shared
    .dataTaskPublisher(for: url)
    .receive(on: DispatchQueue.global()) // работа всё равно в main
    .map { heavyProcessing($0.data) } // выполнится в main!
    .receive(on: DispatchQueue.main)
    .sink { result in updateUI(result) }

// ✅ ПРАВИЛЬНО - subscribe(on:) для фоновой подписки
URLSession.shared
    .dataTaskPublisher(for: url)
    .subscribe(on: DispatchQueue.global()) // подписка в background
    .map { heavyProcessing($0.data) } // выполнится в background
    .receive(on: DispatchQueue.main) // результат в main
    .sink { result in updateUI(result) }
```

---

## Практический пример: комплексное приложение

```swift
// MARK: - Models
struct Article: Codable, Identifiable {
    let id: Int
    let title: String
    let content: String
    let author: String
    let publishedAt: Date
}

// MARK: - API Service
class NewsAPIService {
    private let baseURL = "https://api.news.com"

    func fetchArticles(category: String) -> AnyPublisher<[Article], Error> {
        let url = URL(string: "\(baseURL)/articles?category=\(category)")!

        return URLSession.shared
            .dataTaskPublisher(for: url)
            .subscribe(on: DispatchQueue.global(qos: .userInitiated))
            .tryMap { output in
                guard let response = output.response as? HTTPURLResponse,
                      200..<300 ~= response.statusCode else {
                    throw URLError(.badServerResponse)
                }
                return output.data
            }
            .decode(type: [Article].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }

    func searchArticles(query: String) -> AnyPublisher<[Article], Error> {
        let url = URL(string: "\(baseURL)/search?q=\(query)")!

        return URLSession.shared
            .dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [Article].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

// MARK: - ViewModel
class NewsViewModel: ObservableObject {
    // Output
    @Published var articles: [Article] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var searchResults: [Article] = []

    // Input
    @Published var selectedCategory = "technology"
    @Published var searchQuery = ""

    private let apiService = NewsAPIService()
    private var cancellables = Set<AnyCancellable>()

    init() {
        setupCategoryBinding()
        setupSearchBinding()
        setupErrorHandling()
    }

    private func setupCategoryBinding() {
        $selectedCategory
            .removeDuplicates()
            .flatMap { [weak self] category -> AnyPublisher<[Article], Never> in
                guard let self = self else {
                    return Just([]).eraseToAnyPublisher()
                }

                self.isLoading = true

                return self.apiService
                    .fetchArticles(category: category)
                    .catch { [weak self] error -> Just<[Article]> in
                        self?.errorMessage = error.localizedDescription
                        return Just([])
                    }
                    .handleEvents(receiveOutput: { [weak self] _ in
                        self?.isLoading = false
                    })
                    .eraseToAnyPublisher()
            }
            .assign(to: &$articles)
    }

    private func setupSearchBinding() {
        $searchQuery
            .debounce(for: 0.5, scheduler: DispatchQueue.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .flatMap { [weak self] query -> AnyPublisher<[Article], Never> in
                guard let self = self else {
                    return Just([]).eraseToAnyPublisher()
                }

                return self.apiService
                    .searchArticles(query: query)
                    .catch { _ in Just([]) }
                    .eraseToAnyPublisher()
            }
            .assign(to: &$searchResults)
    }

    private func setupErrorHandling() {
        // Автоматически очищать ошибку через 5 секунд
        $errorMessage
            .compactMap { $0 }
            .delay(for: 5.0, scheduler: DispatchQueue.main)
            .map { _ in nil }
            .assign(to: &$errorMessage)
    }

    func refresh() {
        selectedCategory = selectedCategory // триггерим перезагрузку
    }
}

// MARK: - SwiftUI View
struct NewsView: View {
    @StateObject private var viewModel = NewsViewModel()

    var body: some View {
        NavigationView {
            VStack {
                // Категории
                Picker("Category", selection: $viewModel.selectedCategory) {
                    Text("Technology").tag("technology")
                    Text("Business").tag("business")
                    Text("Sports").tag("sports")
                }
                .pickerStyle(.segmented)
                .padding()

                // Список статей
                if viewModel.isLoading {
                    ProgressView()
                } else {
                    List(viewModel.articles) { article in
                        ArticleRow(article: article)
                    }
                    .refreshable {
                        viewModel.refresh()
                    }
                }
            }
            .searchable(text: $viewModel.searchQuery)
            .navigationTitle("News")
            .alert("Error", isPresented: .constant(viewModel.errorMessage != nil)) {
                Button("OK") {
                    viewModel.errorMessage = nil
                }
            } message: {
                Text(viewModel.errorMessage ?? "")
            }
        }
    }
}

struct ArticleRow: View {
    let article: Article

    var body: some View {
        VStack(alignment: .leading) {
            Text(article.title)
                .font(.headline)
            Text(article.author)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }
}
```

---

## Резюме

**Combine** - мощный инструмент для реактивного программирования в iOS. Используйте его для:

- Реактивных UI биндингов с `@Published` и `assign(to:)`
- Обработки множественных событий с операторами (`debounce`, `throttle`, `combineLatest`)
- Комбинирования асинхронных операций с `flatMap`, `zip`, `merge`
- Управления backpressure через `Demand`
- Автоматической отмены через `AnyCancellable`

**Ключевые правила**:
1. Всегда используйте `store(in:)` для сохранения подписок
2. Используйте `[weak self]` для избежания retain cycles
3. Переключайтесь на `main` thread через `receive(on:)` для UI
4. Обрабатывайте ошибки с `catch` или `replaceError`
5. Комбинируйте с `async/await` для гибридного подхода
6. Используйте `share()` для переиспользования результатов

Combine идеально подходит для реактивных UI, а `async/await` - для простых последовательных операций. Комбинируйте оба подхода для максимальной эффективности.

## Связь с другими темами

**[[kotlin-flow]]** — Kotlin Flow является прямым аналогом Combine на платформе Android/KMP, предоставляя реактивные потоки данных с операторами (map, filter, flatMapLatest). Сравнение Combine Publishers с Kotlin Flow помогает понять общие принципы реактивного программирования и упрощает переход между платформами. Рекомендуется изучать параллельно для формирования кросс-платформенного мышления.

**[[ios-async-await]]** — Async/await и Combine решают смежные задачи, но с разными подходами: async/await предлагает линейный императивный стиль для последовательных операций, тогда как Combine предоставляет декларативные реактивные цепочки для потоков событий. AsyncSequence/AsyncStream частично перекрывают функциональность Combine, но для сложных UI-биндингов (debounce, combineLatest, throttle) Combine остаётся предпочтительным. Изучите async/await для базовой асинхронности, затем Combine для реактивных паттернов.

**[[ios-state-management]]** — Combine является движком реактивного state management в SwiftUI через @Published, ObservableObject и onReceive. Понимание Combine Publishers и Subscribers объясняет, как SwiftUI автоматически перерисовывает View при изменении @Published свойств ViewModel. Рекомендуется изучить Combine перед глубоким погружением в state management для понимания механизма data flow.

**[[ios-architecture-patterns]]** — Combine является ключевым компонентом MVVM-архитектуры на iOS, обеспечивая data binding между View и ViewModel без явных callbacks. В Clean Architecture Combine используется для реактивной передачи данных между слоями (Domain → Presentation), а в TCA — для Side Effects через Effect type. Понимание Combine необходимо для реализации любого современного архитектурного паттерна на iOS.

## Источники и дальнейшее чтение

- Eidhof C. et al. (2019). *Advanced Swift.* — продвинутые паттерны Swift (generics, protocol extensions), которые активно используются в Combine для создания кастомных Publishers и Operators
- Sundell J. (2022). *Swift by Sundell.* — практические примеры использования Combine в реальных проектах, включая интеграцию с async/await и SwiftUI
- Eidhof C. et al. (2020). *Thinking in SwiftUI.* — объясняет ментальную модель data flow в SwiftUI и роль Combine в реактивном обновлении UI

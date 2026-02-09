---
title: "Cross-Platform: Modern Concurrency — async/await vs Coroutines"
created: 2026-01-11
modified: 2026-01-11
type: comparison
status: published
tags:
  - type/comparison
  - topic/concurrency
  - topic/async-await
  - topic/coroutines
---

# Современная конкурентность: Swift async/await vs Kotlin Coroutines

## TL;DR: Сравнительная таблица

| Характеристика | Swift async/await | Kotlin Coroutines |
|----------------|-------------------|-------------------|
| **Появление** | Swift 5.5 (2021) | Kotlin 1.3 (2018) |
| **Ключевое слово функции** | `async` | `suspend` |
| **Ожидание результата** | `await` | неявно (suspend) |
| **Запуск задачи** | `Task { }` | `launch { }` / `async { }` |
| **Параллельное выполнение** | `async let` | `async { }` |
| **Изоляция состояния** | `actor` | `Mutex` / `Channel` |
| **Главный поток** | `@MainActor` | `Dispatchers.Main` |
| **Структурированная конкурентность** | `TaskGroup` | `coroutineScope` |
| **Отмена** | Автоматическая через Task | Автоматическая через Job |
| **Обработка ошибок** | `throws` / `try await` | `try-catch` / `runCatching` |
| **Многоплатформенность** | Только Apple | KMP (iOS, Android, Desktop, Web) |
| **Интеграция с реактивными потоками** | Combine | Flow |

---

## Почему обе платформы пришли к похожему решению?

### Проблема: Callback Hell и управление потоками

До появления современных решений для конкурентности разработчики сталкивались с одними и теми же проблемами на обеих платформах.

**Swift (до async/await):**

```swift
// Callback hell — вложенные замыкания
func loadUserProfile(userId: String, completion: @escaping (Result<UserProfile, Error>) -> Void) {
    fetchUser(userId: userId) { userResult in
        switch userResult {
        case .success(let user):
            fetchAvatar(url: user.avatarUrl) { avatarResult in
                switch avatarResult {
                case .success(let avatar):
                    fetchPosts(userId: userId) { postsResult in
                        switch postsResult {
                        case .success(let posts):
                            let profile = UserProfile(user: user, avatar: avatar, posts: posts)
                            completion(.success(profile))
                        case .failure(let error):
                            completion(.failure(error))
                        }
                    }
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        case .failure(let error):
            completion(.failure(error))
        }
    }
}
```

**Kotlin (до Coroutines):**

```kotlin
// Callback hell — вложенные колбэки
fun loadUserProfile(userId: String, callback: (Result<UserProfile>) -> Unit) {
    fetchUser(userId) { userResult ->
        userResult.onSuccess { user ->
            fetchAvatar(user.avatarUrl) { avatarResult ->
                avatarResult.onSuccess { avatar ->
                    fetchPosts(userId) { postsResult ->
                        postsResult.onSuccess { posts ->
                            val profile = UserProfile(user, avatar, posts)
                            callback(Result.success(profile))
                        }.onFailure { callback(Result.failure(it)) }
                    }
                }.onFailure { callback(Result.failure(it)) }
            }
        }.onFailure { callback(Result.failure(it)) }
    }
}
```

### Проблемы традиционного подхода

1. **Нечитаемый код** — «пирамида смерти» из вложенных callback-ов
2. **Сложная обработка ошибок** — каждый уровень требует отдельной обработки
3. **Утечки памяти** — легко забыть о слабых ссылках в замыканиях
4. **Сложность отмены** — нет стандартного механизма отмены операций
5. **Race conditions** — сложно синхронизировать доступ к общему состоянию
6. **Сложность тестирования** — асинхронные тесты сложнее писать и поддерживать

### Решение: Structured Concurrency

Обе платформы пришли к концепции **структурированной конкурентности**, которая решает эти проблемы:

- Линейный, читаемый код вместо вложенных callback-ов
- Автоматическое распространение отмены
- Гарантированное завершение дочерних задач перед родительской
- Прозрачная обработка ошибок

### Хронология развития

```
2017: Kotlin 1.1 — экспериментальные корутины
2018: Kotlin 1.3 — стабильные корутины
2019: Kotlin Flow — реактивные потоки на корутинах
2020: Swift Concurrency Manifesto опубликован
2021: Swift 5.5 — async/await, actors, structured concurrency
2022: Kotlin 1.6 — улучшенная интеграция с Native
2023: Swift 5.9 — улучшения actors и isolation
2024: Kotlin 2.0 — K2 компилятор с улучшенной поддержкой корутин
```

---

## Интуиция: 5 аналогий для понимания конкурентности

### Аналогия 1: async функция = ресторан с официантом

**Концепция:** Асинхронная функция не блокирует поток выполнения, как официант не стоит у вашего столика, пока готовится еда.

```swift
// Swift: официант (поток) принимает заказ и уходит к другим столикам
func orderDinner() async throws -> Dinner {
    let appetizer = try await kitchen.prepareAppetizer()  // Официант ушёл
    let mainCourse = try await kitchen.prepareMainCourse() // Вернулся с закуской
    let dessert = try await kitchen.prepareDessert()       // Принёс основное
    return Dinner(appetizer, mainCourse, dessert)          // Принёс десерт
}
```

```kotlin
// Kotlin: официант (поток) принимает заказ и уходит к другим столикам
suspend fun orderDinner(): Dinner {
    val appetizer = kitchen.prepareAppetizer()  // Официант ушёл
    val mainCourse = kitchen.prepareMainCourse() // Вернулся с закуской
    val dessert = kitchen.prepareDessert()       // Принёс основное
    return Dinner(appetizer, mainCourse, dessert) // Принёс десерт
}
```

**Ключевой инсайт:** Пока готовится еда (выполняется I/O операция), официант (поток) обслуживает другие столики (выполняет другие задачи).

### Аналогия 2: await = ждём заказ, но можем отменить

**Концепция:** `await` — это точка приостановки, где мы можем:
- Дождаться результата
- Отменить ожидание
- Получить ошибку

```swift
// Swift: можем отменить заказ в любой момент ожидания
let task = Task {
    do {
        let dinner = try await orderDinner()
        print("Ужин готов: \(dinner)")
    } catch {
        print("Заказ отменён или ошибка: \(error)")
    }
}

// Передумали ужинать
task.cancel()
```

```kotlin
// Kotlin: можем отменить заказ в любой момент ожидания
val job = lifecycleScope.launch {
    try {
        val dinner = orderDinner()
        println("Ужин готов: $dinner")
    } catch (e: CancellationException) {
        println("Заказ отменён")
    } catch (e: Exception) {
        println("Ошибка: ${e.message}")
    }
}

// Передумали ужинать
job.cancel()
```

### Аналогия 3: Task/launch = запустить нового официанта

**Концепция:** `Task` в Swift и `launch` в Kotlin — это найм нового официанта для параллельного обслуживания.

```swift
// Swift: три официанта работают параллельно
func serveTable() async throws -> [Dish] {
    async let appetizer = kitchen.prepareAppetizer()
    async let mainCourse = kitchen.prepareMainCourse()
    async let dessert = kitchen.prepareDessert()

    // Все три блюда готовятся одновременно
    return try await [appetizer, mainCourse, dessert]
}
```

```kotlin
// Kotlin: три официанта работают параллельно
suspend fun serveTable(): List<Dish> = coroutineScope {
    val appetizer = async { kitchen.prepareAppetizer() }
    val mainCourse = async { kitchen.prepareMainCourse() }
    val dessert = async { kitchen.prepareDessert() }

    // Все три блюда готовятся одновременно
    listOf(appetizer.await(), mainCourse.await(), dessert.await())
}
```

### Аналогия 4: Actor/Mutex = один повар на кухне

**Концепция:** Actor (Swift) или Mutex (Kotlin) гарантирует, что только один «повар» работает с состоянием в каждый момент времени.

```swift
// Swift: actor — только один может готовить одновременно
actor Kitchen {
    private var ingredients: [String: Int] = [:]

    func useIngredient(_ name: String, amount: Int) -> Bool {
        guard let available = ingredients[name], available >= amount else {
            return false
        }
        ingredients[name] = available - amount
        return true
    }

    func restockIngredient(_ name: String, amount: Int) {
        ingredients[name, default: 0] += amount
    }
}

// Безопасный доступ из любого потока
let kitchen = Kitchen()
Task {
    let success = await kitchen.useIngredient("tomato", amount: 2)
}
```

```kotlin
// Kotlin: Mutex — только один может готовить одновременно
class Kitchen {
    private val mutex = Mutex()
    private val ingredients = mutableMapOf<String, Int>()

    suspend fun useIngredient(name: String, amount: Int): Boolean = mutex.withLock {
        val available = ingredients[name] ?: 0
        if (available >= amount) {
            ingredients[name] = available - amount
            true
        } else {
            false
        }
    }

    suspend fun restockIngredient(name: String, amount: Int) = mutex.withLock {
        ingredients[name] = (ingredients[name] ?: 0) + amount
    }
}

// Безопасный доступ из любой корутины
val kitchen = Kitchen()
lifecycleScope.launch {
    val success = kitchen.useIngredient("tomato", 2)
}
```

### Аналогия 5: Structured concurrency = все официанты уходят когда ресторан закрывается

**Концепция:** Когда родительская задача завершается или отменяется, все дочерние задачи автоматически завершаются.

```swift
// Swift: когда TaskGroup завершается, все задачи внутри гарантированно завершены
func closeRestaurant() async {
    await withTaskGroup(of: Void.self) { group in
        for table in tables {
            group.addTask {
                await table.finishService()  // Каждый столик обслуживается
            }
        }
        // Когда TaskGroup выходит из scope, все официанты закончили работу
    }
    print("Ресторан закрыт, все ушли домой")
}
```

```kotlin
// Kotlin: когда coroutineScope завершается, все корутины внутри гарантированно завершены
suspend fun closeRestaurant() {
    coroutineScope {
        tables.forEach { table ->
            launch {
                table.finishService()  // Каждый столик обслуживается
            }
        }
        // Когда coroutineScope выходит из scope, все официанты закончили работу
    }
    println("Ресторан закрыт, все ушли домой")
}
```

---

## Синтаксис и семантика

### Swift async/await

**Объявление асинхронной функции:**

```swift
// Базовый синтаксис async функции
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.invalidResponse
    }

    return try JSONDecoder().decode(User.self, from: data)
}

// Вызов async функции
Task {
    do {
        let user = try await fetchUser(id: "123")
        print("Пользователь: \(user.name)")
    } catch {
        print("Ошибка: \(error)")
    }
}
```

**Параллельное выполнение с async let:**

```swift
// async let для параллельного выполнения
func loadDashboard(userId: String) async throws -> Dashboard {
    async let user = fetchUser(id: userId)
    async let posts = fetchPosts(userId: userId)
    async let notifications = fetchNotifications(userId: userId)

    // Все три запроса выполняются параллельно
    return try await Dashboard(
        user: user,
        posts: posts,
        notifications: notifications
    )
}
```

**TaskGroup для динамического количества задач:**

```swift
// TaskGroup для обработки массива
func fetchAllUsers(ids: [String]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in ids {
            group.addTask {
                try await fetchUser(id: id)
            }
        }

        var users: [User] = []
        for try await user in group {
            users.append(user)
        }
        return users
    }
}
```

### Kotlin Coroutines

**Объявление suspend функции:**

```kotlin
// Базовый синтаксис suspend функции
suspend fun fetchUser(id: String): User {
    val response = httpClient.get("https://api.example.com/users/$id")

    if (response.status != HttpStatusCode.OK) {
        throw NetworkException("Invalid response: ${response.status}")
    }

    return response.body()
}

// Вызов suspend функции
lifecycleScope.launch {
    try {
        val user = fetchUser("123")
        println("Пользователь: ${user.name}")
    } catch (e: Exception) {
        println("Ошибка: ${e.message}")
    }
}
```

**Параллельное выполнение с async:**

```kotlin
// async для параллельного выполнения
suspend fun loadDashboard(userId: String): Dashboard = coroutineScope {
    val user = async { fetchUser(userId) }
    val posts = async { fetchPosts(userId) }
    val notifications = async { fetchNotifications(userId) }

    // Все три запроса выполняются параллельно
    Dashboard(
        user = user.await(),
        posts = posts.await(),
        notifications = notifications.await()
    )
}
```

**coroutineScope для динамического количества задач:**

```kotlin
// coroutineScope для обработки массива
suspend fun fetchAllUsers(ids: List<String>): List<User> = coroutineScope {
    ids.map { id ->
        async { fetchUser(id) }
    }.awaitAll()
}
```

---

## Ключевые различия

| Аспект | Swift | Kotlin |
|--------|-------|--------|
| **Ключевое слово для функции** | `async` (в сигнатуре) | `suspend` (в сигнатуре) |
| **Ключевое слово ожидания** | `await` (явно перед вызовом) | Неявно (просто вызываем) |
| **Запуск новой задачи** | `Task { }` | `launch { }` |
| **Параллельный запуск с результатом** | `async let` | `async { }` + `.await()` |
| **Изоляция состояния** | `actor` (встроено в язык) | `Mutex` / `Channel` (библиотека) |
| **Группа задач** | `TaskGroup` | `coroutineScope` |
| **Главный поток** | `@MainActor` | `Dispatchers.Main` |
| **Обработка ошибок** | `throws` / `try await` | `try-catch` блоки |
| **Контекст выполнения** | Автоматически определяется | Явно через `CoroutineContext` |
| **Отмена** | `task.cancel()` | `job.cancel()` |
| **Проверка отмены** | `Task.checkCancellation()` | `ensureActive()` |
| **Таймаут** | `Task.sleep(for:)` + отмена | `withTimeout { }` |

### Детальное сравнение запуска задач

**Swift:**

```swift
// Detached task — не наследует контекст
Task.detached {
    await someAsyncWork()
}

// Regular task — наследует actor context
Task {
    await someAsyncWork()
}

// Task с приоритетом
Task(priority: .high) {
    await urgentWork()
}
```

**Kotlin:**

```kotlin
// launch — fire-and-forget, наследует контекст
launch {
    someAsyncWork()
}

// async — возвращает Deferred с результатом
val result = async {
    someAsyncWork()
}
result.await()

// Явный диспетчер
launch(Dispatchers.IO) {
    heavyIOWork()
}

// Новый scope без наследования Job
launch(Job()) {
    independentWork()
}
```

---

## Actors vs Channels

### Swift Actors — изолированное состояние

Actor в Swift — это reference type, который гарантирует последовательный доступ к своему состоянию:

```swift
// Определение actor
actor BankAccount {
    private(set) var balance: Decimal
    private var transactions: [Transaction] = []

    init(initialBalance: Decimal) {
        self.balance = initialBalance
    }

    // Методы actor автоматически изолированы
    func deposit(_ amount: Decimal) {
        balance += amount
        transactions.append(Transaction(type: .deposit, amount: amount))
    }

    func withdraw(_ amount: Decimal) throws {
        guard balance >= amount else {
            throw BankError.insufficientFunds
        }
        balance -= amount
        transactions.append(Transaction(type: .withdrawal, amount: amount))
    }

    // nonisolated — не требует await для доступа
    nonisolated var accountId: String {
        "ACC-\(ObjectIdentifier(self).hashValue)"
    }
}

// Использование actor
let account = BankAccount(initialBalance: 1000)

Task {
    await account.deposit(500)
    let currentBalance = await account.balance
    print("Баланс: \(currentBalance)")
}

// Несколько задач безопасно работают с одним account
Task {
    try await account.withdraw(200)
}

Task {
    await account.deposit(100)
}
```

### Kotlin — Mutex и Channels

В Kotlin нет встроенных actors, но есть примитивы синхронизации:

**Mutex — взаимное исключение:**

```kotlin
class BankAccount(initialBalance: BigDecimal) {
    private val mutex = Mutex()
    private var _balance = initialBalance
    private val transactions = mutableListOf<Transaction>()

    val balance: BigDecimal
        get() = _balance

    suspend fun deposit(amount: BigDecimal) = mutex.withLock {
        _balance += amount
        transactions.add(Transaction(TransactionType.DEPOSIT, amount))
    }

    suspend fun withdraw(amount: BigDecimal) = mutex.withLock {
        if (_balance < amount) {
            throw InsufficientFundsException()
        }
        _balance -= amount
        transactions.add(Transaction(TransactionType.WITHDRAWAL, amount))
    }
}

// Использование
val account = BankAccount(BigDecimal("1000"))

lifecycleScope.launch {
    account.deposit(BigDecimal("500"))
    println("Баланс: ${account.balance}")
}

// Несколько корутин безопасно работают с одним account
lifecycleScope.launch { account.withdraw(BigDecimal("200")) }
lifecycleScope.launch { account.deposit(BigDecimal("100")) }
```

**Channel — коммуникация между корутинами:**

```kotlin
// Channel как actor pattern
sealed class AccountCommand {
    data class Deposit(val amount: BigDecimal, val response: CompletableDeferred<Unit>) : AccountCommand()
    data class Withdraw(val amount: BigDecimal, val response: CompletableDeferred<Result<Unit>>) : AccountCommand()
    data class GetBalance(val response: CompletableDeferred<BigDecimal>) : AccountCommand()
}

fun CoroutineScope.bankAccountActor(initialBalance: BigDecimal): SendChannel<AccountCommand> {
    return actor {
        var balance = initialBalance

        for (command in channel) {
            when (command) {
                is AccountCommand.Deposit -> {
                    balance += command.amount
                    command.response.complete(Unit)
                }
                is AccountCommand.Withdraw -> {
                    if (balance >= command.amount) {
                        balance -= command.amount
                        command.response.complete(Result.success(Unit))
                    } else {
                        command.response.complete(Result.failure(InsufficientFundsException()))
                    }
                }
                is AccountCommand.GetBalance -> {
                    command.response.complete(balance)
                }
            }
        }
    }
}

// Использование
val accountChannel = scope.bankAccountActor(BigDecimal("1000"))

scope.launch {
    val response = CompletableDeferred<Unit>()
    accountChannel.send(AccountCommand.Deposit(BigDecimal("500"), response))
    response.await()

    val balanceResponse = CompletableDeferred<BigDecimal>()
    accountChannel.send(AccountCommand.GetBalance(balanceResponse))
    println("Баланс: ${balanceResponse.await()}")
}
```

### Сравнение подходов

| Аспект | Swift Actor | Kotlin Mutex | Kotlin Channel/Actor |
|--------|-------------|--------------|---------------------|
| **Синтаксис** | Встроен в язык | Библиотека | Библиотека |
| **Изоляция** | Автоматическая | Ручная | Ручная |
| **Reentrancy** | Да (с осторожностью) | Нет | Нет |
| **Производительность** | Оптимизировано компилятором | Хорошая | Хорошая |
| **Гибкость** | Ограниченная | Высокая | Высокая |
| **Сложность** | Низкая | Средняя | Высокая |

---

## Structured Concurrency — структурированная конкурентность

### Иерархия задач в Swift

```swift
// Пример иерархии задач
func processOrder(order: Order) async throws -> Receipt {
    // Родительская задача
    try await withThrowingTaskGroup(of: ProcessedItem.self) { group in
        // Дочерние задачи
        for item in order.items {
            group.addTask {
                // Внучатые задачи создаются внутри
                try await processItem(item)
            }
        }

        var processedItems: [ProcessedItem] = []
        for try await processed in group {
            processedItems.append(processed)
        }

        return Receipt(items: processedItems)
    }
}

// Отмена распространяется вниз по иерархии
func processItem(_ item: OrderItem) async throws -> ProcessedItem {
    // Проверяем, не отменена ли задача
    try Task.checkCancellation()

    async let validated = validateItem(item)
    async let priced = calculatePrice(item)

    // Если родительская задача отменена, эти тоже отменятся
    return try await ProcessedItem(
        item: validated,
        price: priced
    )
}
```

### coroutineScope в Kotlin

```kotlin
// Пример иерархии корутин
suspend fun processOrder(order: Order): Receipt = coroutineScope {
    // Все дочерние корутины привязаны к этому scope
    val processedItems = order.items.map { item ->
        async {
            // Внучатые корутины создаются внутри
            processItem(item)
        }
    }.awaitAll()

    Receipt(processedItems)
}

// Отмена распространяется вниз по иерархии
suspend fun processItem(item: OrderItem): ProcessedItem = coroutineScope {
    // Проверяем, не отменена ли корутина
    ensureActive()

    val validated = async { validateItem(item) }
    val priced = async { calculatePrice(item) }

    // Если родительская корутина отменена, эти тоже отменятся
    ProcessedItem(
        item = validated.await(),
        price = priced.await()
    )
}
```

### Гарантии структурированной конкурентности

**Swift:**

```swift
// TaskGroup гарантирует завершение всех задач
func safeBatchProcess() async throws {
    try await withThrowingTaskGroup(of: Void.self) { group in
        for i in 0..<100 {
            group.addTask {
                try await processItem(i)
            }
        }
        // Здесь ВСЕ задачи гарантированно завершены или отменены
    }
    print("Все задачи завершены") // Это выполнится только после завершения всех
}

// Unstructured Task — нет гарантий
func unsafeBatchProcess() {
    for i in 0..<100 {
        Task {
            await processItem(i)
            // Эти задачи могут пережить родительский контекст!
        }
    }
    print("Задачи запущены, но не обязательно завершены")
}
```

**Kotlin:**

```kotlin
// coroutineScope гарантирует завершение всех корутин
suspend fun safeBatchProcess() {
    coroutineScope {
        repeat(100) { i ->
            launch {
                processItem(i)
            }
        }
        // Здесь ВСЕ корутины гарантированно завершены или отменены
    }
    println("Все задачи завершены") // Это выполнится только после завершения всех
}

// GlobalScope — нет гарантий (антипаттерн!)
fun unsafeBatchProcess() {
    repeat(100) { i ->
        GlobalScope.launch {
            processItem(i)
            // Эти корутины могут пережить родительский контекст!
        }
    }
    println("Задачи запущены, но не обязательно завершены")
}
```

### Распространение отмены

**Swift:**

```swift
// Отмена родителя отменяет детей
func fetchWithTimeout() async throws -> Data {
    let task = Task {
        try await withThrowingTaskGroup(of: Data.self) { group in
            group.addTask {
                try await fetchFromServer1()
            }
            group.addTask {
                try await fetchFromServer2()
            }

            // Возвращаем первый результат
            guard let first = try await group.next() else {
                throw FetchError.noData
            }

            // Отменяем остальные задачи
            group.cancelAll()

            return first
        }
    }

    // Таймаут через 5 секунд
    Task {
        try await Task.sleep(for: .seconds(5))
        task.cancel() // Это отменит все дочерние задачи
    }

    return try await task.value
}
```

**Kotlin:**

```kotlin
// Отмена родителя отменяет детей
suspend fun fetchWithTimeout(): Data = withTimeout(5.seconds) {
    coroutineScope {
        val result1 = async { fetchFromServer1() }
        val result2 = async { fetchFromServer2() }

        // select возвращает первый результат
        select {
            result1.onAwait { it }
            result2.onAwait { it }
        }.also {
            // Отменяем остальные корутины
            coroutineContext.cancelChildren()
        }
    }
}
```

---

## Main Thread / Main Actor

### Swift @MainActor

```swift
// Класс, изолированный на главном потоке
@MainActor
class ProfileViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var error: Error?

    func loadUser(id: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            // fetchUser выполняется в фоне
            user = try await UserService.fetchUser(id: id)
        } catch {
            self.error = error
        }
    }
}

// Использование в SwiftUI
struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let user = viewModel.user {
                Text(user.name)
            } else if let error = viewModel.error {
                Text("Error: \(error.localizedDescription)")
            }
        }
        .task {
            await viewModel.loadUser(id: "123")
        }
    }
}

// Явный переход на MainActor
func processInBackground() async {
    let data = await heavyComputation() // Фоновый поток

    await MainActor.run {
        // Гарантированно главный поток
        updateUI(with: data)
    }
}
```

### Kotlin Dispatchers.Main

```kotlin
// ViewModel с MainScope
class ProfileViewModel : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableSharedFlow<Throwable>()
    val error: SharedFlow<Throwable> = _error.asSharedFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                // fetchUser выполняется с Dispatchers.IO внутри
                _user.value = UserService.fetchUser(id)
            } catch (e: Exception) {
                _error.emit(e)
            } finally {
                _isLoading.value = false
            }
        }
    }
}

// Использование в Compose
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = viewModel()) {
    val user by viewModel.user.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadUser("123")
    }

    when {
        isLoading -> CircularProgressIndicator()
        user != null -> Text(user!!.name)
    }
}

// Явный переход на Main dispatcher
suspend fun processInBackground() {
    val data = withContext(Dispatchers.Default) {
        heavyComputation() // Фоновый поток
    }

    withContext(Dispatchers.Main) {
        // Гарантированно главный поток
        updateUI(data)
    }
}
```

### Сравнение подходов к главному потоку

| Аспект | Swift @MainActor | Kotlin Dispatchers.Main |
|--------|------------------|-------------------------|
| **Объявление** | `@MainActor class` | `launch(Dispatchers.Main)` |
| **Проверка компилятором** | Да, строгая | Нет |
| **Переход на main** | `await MainActor.run { }` | `withContext(Dispatchers.Main) { }` |
| **В UI фреймворке** | SwiftUI автоматически | Compose — `LaunchedEffect` |
| **Ошибки в runtime** | Редко | Возможны |

---

## KMP: Coroutines everywhere

### Корутины на iOS через KMP

Kotlin Multiplatform позволяет использовать корутины на всех платформах, включая iOS:

```kotlin
// shared/src/commonMain/kotlin/UserRepository.kt
class UserRepository(
    private val api: UserApi,
    private val database: UserDatabase
) {
    // suspend функции работают на всех платформах
    suspend fun getUser(id: String): User {
        return database.getUser(id) ?: api.fetchUser(id).also { user ->
            database.saveUser(user)
        }
    }

    // Flow работает на всех платформах
    fun observeUsers(): Flow<List<User>> = database.observeAllUsers()
}
```

### Dispatchers.Main на iOS

```kotlin
// shared/src/iosMain/kotlin/Dispatchers.kt
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.MainCoroutineDispatcher
import platform.darwin.dispatch_async
import platform.darwin.dispatch_get_main_queue

// Dispatchers.Main на iOS использует dispatch_get_main_queue()
actual val Dispatchers.Main: MainCoroutineDispatcher
    get() = NsQueueDispatcher(dispatch_get_main_queue())

// Использование в iOS-specific коде
class IosUserViewModel(
    private val repository: UserRepository
) {
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    fun loadUser(id: String, onResult: (User?) -> Unit) {
        scope.launch {
            try {
                val user = repository.getUser(id)
                onResult(user)  // Вызывается на main queue
            } catch (e: Exception) {
                onResult(null)
            }
        }
    }

    fun cancel() {
        scope.cancel()
    }
}
```

### Flow to Combine bridging с SKIE

SKIE (Swift Kotlin Interface Enhancer) делает Kotlin корутины и Flow нативными для Swift:

```kotlin
// shared/src/commonMain/kotlin/UserRepository.kt
class UserRepository {
    // Flow автоматически конвертируется в AsyncSequence
    fun observeUsers(): Flow<List<User>> = flow {
        while (true) {
            emit(fetchUsers())
            delay(30.seconds)
        }
    }

    // suspend функции становятся async в Swift
    suspend fun getUser(id: String): User = api.fetchUser(id)
}
```

```swift
// iOS Swift код — использование Kotlin Flow как AsyncSequence
import Shared
import SKIE

class UsersViewController: UIViewController {
    private let repository = UserRepository()
    private var observationTask: Task<Void, Never>?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Flow стал AsyncSequence благодаря SKIE
        observationTask = Task {
            for await users in repository.observeUsers() {
                updateUI(with: users)
            }
        }
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        observationTask?.cancel()
    }

    private func loadUser() async {
        // suspend функция стала async
        do {
            let user = try await repository.getUser(id: "123")
            updateUI(with: user)
        } catch {
            showError(error)
        }
    }
}
```

### Без SKIE — ручная конвертация

```swift
// Без SKIE — нужны обёртки
import Shared

class UsersViewController: UIViewController {
    private let repository = UserRepository()
    private var flowJob: Kotlinx_coroutines_coreJob?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Ручная подписка на Flow
        flowJob = repository.observeUsers().collect(
            collector: FlowCollector { [weak self] users in
                self?.updateUI(with: users as! [User])
                return KotlinUnit()
            },
            completionHandler: { error in
                if let error = error {
                    print("Flow error: \(error)")
                }
            }
        )
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        flowJob?.cancel(cause: nil)
    }
}
```

---

## 6 типичных ошибок в асинхронном коде

### Ошибка 1: Fire-and-forget задачи

**Swift — неправильно:**

```swift
class ImageLoader {
    func preloadImages(_ urls: [URL]) {
        for url in urls {
            Task {
                // Эти задачи никак не отслеживаются!
                // Они продолжат выполняться даже если ImageLoader уничтожен
                await downloadImage(url)
            }
        }
    }
}
```

**Swift — правильно:**

```swift
class ImageLoader {
    private var preloadTasks: [Task<Void, Never>] = []

    func preloadImages(_ urls: [URL]) async {
        await withTaskGroup(of: Void.self) { group in
            for url in urls {
                group.addTask {
                    await self.downloadImage(url)
                }
            }
        }
    }

    // Или с возможностью отмены
    func preloadImagesWithCancellation(_ urls: [URL]) {
        preloadTasks = urls.map { url in
            Task {
                await downloadImage(url)
            }
        }
    }

    func cancelPreloading() {
        preloadTasks.forEach { $0.cancel() }
        preloadTasks.removeAll()
    }
}
```

**Kotlin — неправильно:**

```kotlin
class ImageLoader {
    fun preloadImages(urls: List<String>) {
        urls.forEach { url ->
            GlobalScope.launch {
                // Эти корутины никак не отслеживаются!
                // Они продолжат выполняться даже если ImageLoader уничтожен
                downloadImage(url)
            }
        }
    }
}
```

**Kotlin — правильно:**

```kotlin
class ImageLoader(
    private val scope: CoroutineScope
) {
    private var preloadJob: Job? = null

    fun preloadImages(urls: List<String>) {
        preloadJob = scope.launch {
            urls.map { url ->
                async { downloadImage(url) }
            }.awaitAll()
        }
    }

    fun cancelPreloading() {
        preloadJob?.cancel()
    }
}
```

### Ошибка 2: Неправильный dispatcher/actor

**Swift — неправильно:**

```swift
// Обновление UI не на главном потоке
func loadAndDisplay() async {
    let image = await downloadImage()
    imageView.image = image  // CRASH или undefined behavior!
}
```

**Swift — правильно:**

```swift
@MainActor
func loadAndDisplay() async {
    let image = await downloadImage()
    imageView.image = image  // Безопасно — мы на MainActor
}

// Или явно
func loadAndDisplay() async {
    let image = await downloadImage()
    await MainActor.run {
        imageView.image = image
    }
}
```

**Kotlin — неправильно:**

```kotlin
// Обновление UI не на главном потоке
suspend fun loadAndDisplay() {
    val image = downloadImage()  // Может быть на IO dispatcher
    imageView.setImageBitmap(image)  // CRASH!
}
```

**Kotlin — правильно:**

```kotlin
suspend fun loadAndDisplay() {
    val image = withContext(Dispatchers.IO) {
        downloadImage()
    }
    withContext(Dispatchers.Main) {
        imageView.setImageBitmap(image)
    }
}
```

### Ошибка 3: Игнорирование отмены

**Swift — неправильно:**

```swift
func processLargeFile() async throws -> ProcessedData {
    var results: [ProcessedChunk] = []

    for chunk in file.chunks {
        // Долгая операция без проверки отмены
        let processed = await processChunk(chunk)
        results.append(processed)
    }

    return ProcessedData(chunks: results)
}
```

**Swift — правильно:**

```swift
func processLargeFile() async throws -> ProcessedData {
    var results: [ProcessedChunk] = []

    for chunk in file.chunks {
        // Проверяем отмену перед каждой итерацией
        try Task.checkCancellation()

        let processed = await processChunk(chunk)
        results.append(processed)
    }

    return ProcessedData(chunks: results)
}
```

**Kotlin — неправильно:**

```kotlin
suspend fun processLargeFile(): ProcessedData {
    val results = mutableListOf<ProcessedChunk>()

    for (chunk in file.chunks) {
        // Долгая операция без проверки отмены
        val processed = processChunk(chunk)
        results.add(processed)
    }

    return ProcessedData(results)
}
```

**Kotlin — правильно:**

```kotlin
suspend fun processLargeFile(): ProcessedData {
    val results = mutableListOf<ProcessedChunk>()

    for (chunk in file.chunks) {
        // Проверяем отмену перед каждой итерацией
        ensureActive()

        val processed = processChunk(chunk)
        results.add(processed)
    }

    return ProcessedData(results)
}
```

### Ошибка 4: Race conditions

**Swift — неправильно:**

```swift
class Counter {
    var value = 0

    func increment() async {
        // Race condition! Несколько задач могут читать одно значение
        let current = value
        // ... какая-то работа ...
        value = current + 1
    }
}

// Использование
let counter = Counter()
await withTaskGroup(of: Void.self) { group in
    for _ in 0..<1000 {
        group.addTask { await counter.increment() }
    }
}
print(counter.value)  // Может быть меньше 1000!
```

**Swift — правильно:**

```swift
actor Counter {
    private(set) var value = 0

    func increment() {
        // Actor гарантирует последовательный доступ
        value += 1
    }
}

// Использование
let counter = Counter()
await withTaskGroup(of: Void.self) { group in
    for _ in 0..<1000 {
        group.addTask { await counter.increment() }
    }
}
print(await counter.value)  // Всегда 1000
```

**Kotlin — неправильно:**

```kotlin
class Counter {
    var value = 0

    suspend fun increment() {
        // Race condition!
        val current = value
        delay(1)  // Симуляция работы
        value = current + 1
    }
}

// Использование
val counter = Counter()
coroutineScope {
    repeat(1000) {
        launch { counter.increment() }
    }
}
println(counter.value)  // Может быть меньше 1000!
```

**Kotlin — правильно:**

```kotlin
class Counter {
    private val mutex = Mutex()
    private var _value = 0
    val value: Int get() = _value

    suspend fun increment() = mutex.withLock {
        _value += 1
    }
}

// Или с AtomicInteger для простых случаев
class AtomicCounter {
    private val _value = atomic(0)
    val value: Int get() = _value.value

    fun increment() {
        _value.incrementAndGet()
    }
}
```

### Ошибка 5: Блокировка в async контексте

**Swift — неправильно:**

```swift
func fetchData() async -> Data {
    // Thread.sleep блокирует поток кооперативного пула!
    Thread.sleep(forTimeInterval: 1.0)
    return Data()
}
```

**Swift — правильно:**

```swift
func fetchData() async throws -> Data {
    // Task.sleep не блокирует поток
    try await Task.sleep(for: .seconds(1))
    return Data()
}
```

**Kotlin — неправильно:**

```kotlin
suspend fun fetchData(): ByteArray {
    // Thread.sleep блокирует поток!
    Thread.sleep(1000)
    return ByteArray(0)
}
```

**Kotlin — правильно:**

```kotlin
suspend fun fetchData(): ByteArray {
    // delay не блокирует поток
    delay(1000)
    return ByteArray(0)
}

// Если нужно выполнить блокирующий код
suspend fun fetchDataBlocking(): ByteArray = withContext(Dispatchers.IO) {
    // Блокирующая операция на IO dispatcher
    blockingNetworkCall()
}
```

### Ошибка 6: Утечки памяти из-за захвата self

**Swift — неправильно:**

```swift
class DataLoader {
    var data: Data?

    func loadData() {
        Task {
            // Сильная ссылка на self — потенциальная утечка
            self.data = await fetchData()
        }
    }
}
```

**Swift — правильно:**

```swift
class DataLoader {
    var data: Data?
    private var loadTask: Task<Void, Never>?

    func loadData() {
        loadTask = Task { [weak self] in
            let data = await fetchData()
            self?.data = data  // Слабая ссылка
        }
    }

    deinit {
        loadTask?.cancel()
    }
}
```

**Kotlin — неправильно:**

```kotlin
class DataLoader {
    var data: ByteArray? = null

    fun loadData(scope: CoroutineScope) {
        scope.launch {
            // Сильная ссылка через this@DataLoader
            this@DataLoader.data = fetchData()
        }
    }
}
```

**Kotlin — правильно:**

```kotlin
class DataLoader {
    var data: ByteArray? = null
    private var loadJob: Job? = null

    fun loadData(scope: CoroutineScope) {
        loadJob = scope.launch {
            val result = fetchData()
            // Безопасное присваивание
            data = result
        }
    }

    fun cancel() {
        loadJob?.cancel()
    }
}

// Или с lifecycle-aware scope в Android
class DataLoaderViewModel : ViewModel() {
    var data: ByteArray? = null

    fun loadData() {
        viewModelScope.launch {
            // viewModelScope автоматически отменяется при onCleared()
            data = fetchData()
        }
    }
}
```

---

## Ментальные модели

### Suspension Points = остановки в дороге

Представьте async функцию как поездку на автомобиле:

```
┌─────────────────────────────────────────────────────────────┐
│                    ASYNC ФУНКЦИЯ                            │
│                                                             │
│  [Старт] ──► работа ──► [await] ──► работа ──► [await] ──► [Финиш]
│                            │                       │        │
│                       Остановка               Остановка     │
│                       на заправку             на обед       │
│                                                             │
│  Во время остановки машина (поток) может уехать            │
│  и вернуться позже!                                         │
└─────────────────────────────────────────────────────────────┘
```

**Swift:**

```swift
func roadTrip() async throws -> Destination {
    let fuel = try await refuel()        // Остановка 1: заправка
    // Поток мог смениться!
    let food = try await grabLunch()     // Остановка 2: обед
    // Поток мог опять смениться!
    return try await arriveAt(destination)
}
```

**Kotlin:**

```kotlin
suspend fun roadTrip(): Destination {
    val fuel = refuel()        // Остановка 1: заправка
    // Поток мог смениться!
    val food = grabLunch()     // Остановка 2: обед
    // Поток мог опять смениться!
    return arriveAt(destination)
}
```

### Structured Concurrency = генеалогическое древо

```
                    ┌─────────────────┐
                    │   Прародитель   │
                    │  (Main Scope)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
       │  Родитель 1 │ │ Родитель 2│ │  Родитель 3 │
       │  (Task 1)   │ │ (Task 2)  │ │  (Task 3)   │
       └──────┬──────┘ └───────────┘ └──────┬──────┘
              │                             │
       ┌──────┴──────┐               ┌──────┴──────┐
       │             │               │             │
  ┌────▼────┐  ┌─────▼────┐    ┌─────▼────┐  ┌─────▼────┐
  │ Ребёнок │  │ Ребёнок  │    │ Ребёнок  │  │ Ребёнок  │
  │   1.1   │  │   1.2    │    │   3.1    │  │   3.2    │
  └─────────┘  └──────────┘    └──────────┘  └──────────┘

  Правила:
  ✓ Отмена прародителя → отмена всех потомков
  ✓ Ошибка ребёнка → распространяется к родителю
  ✓ Родитель не завершится пока живы дети
```

**Swift:**

```swift
// Генеалогическое древо задач
func familyTree() async throws {
    try await withThrowingTaskGroup(of: Void.self) { group in
        // Родитель 1 с детьми
        group.addTask {
            try await withThrowingTaskGroup(of: Void.self) { children in
                children.addTask { try await child1_1() }
                children.addTask { try await child1_2() }
            }
        }

        // Родитель 2 без детей
        group.addTask { try await parent2() }

        // Родитель 3 с детьми
        group.addTask {
            try await withThrowingTaskGroup(of: Void.self) { children in
                children.addTask { try await child3_1() }
                children.addTask { try await child3_2() }
            }
        }
    }
    // Все завершены или отменены
}
```

**Kotlin:**

```kotlin
// Генеалогическое древо корутин
suspend fun familyTree() = coroutineScope {
    // Родитель 1 с детьми
    launch {
        coroutineScope {
            launch { child1_1() }
            launch { child1_2() }
        }
    }

    // Родитель 2 без детей
    launch { parent2() }

    // Родитель 3 с детьми
    launch {
        coroutineScope {
            launch { child3_1() }
            launch { child3_2() }
        }
    }

    // Все завершены или отменены
}
```

### Actor = однопоточный остров

```
┌─────────────────────────────────────────────────────────────┐
│                         ОКЕАН                               │
│                    (многопоточный мир)                      │
│                                                             │
│    Task1 ─────────┐                                         │
│                   │                                         │
│    Task2 ─────────┼───► ┌───────────────────────────┐       │
│                   │     │        ОСТРОВ             │       │
│    Task3 ─────────┘     │        (Actor)            │       │
│                         │                           │       │
│                         │   ┌─────────────────┐     │       │
│                  Мост   │   │  Изолированное  │     │       │
│                 (await) │   │   состояние     │     │       │
│                         │   │                 │     │       │
│                         │   │  var balance    │     │       │
│                         │   │  var history    │     │       │
│                         │   └─────────────────┘     │       │
│                         │                           │       │
│                         │   Только один посетитель  │       │
│                         │   на острове одновременно │       │
│                         └───────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Swift:**

```swift
actor Island {
    // Изолированное состояние — только actor имеет доступ
    private var treasure: [Gold] = []
    private var visitors: [Visitor] = []

    // Любой метод actor выполняется атомарно
    func addTreasure(_ gold: Gold) {
        treasure.append(gold)
    }

    func takeTreasure() -> Gold? {
        treasure.popLast()
    }

    // nonisolated — безопасно без await
    nonisolated var islandName: String { "Treasure Island" }
}

// Из океана (многопоточного мира) нужен мост (await)
let island = Island()

Task {
    await island.addTreasure(Gold(weight: 100))
    // Мы пересекли мост, сделали дело, вернулись
}

Task {
    if let gold = await island.takeTreasure() {
        // Гарантированно получили золото атомарно
    }
}
```

**Kotlin (эмуляция через Mutex):**

```kotlin
class Island {
    private val mutex = Mutex()

    // Изолированное состояние
    private val treasure = mutableListOf<Gold>()
    private val visitors = mutableListOf<Visitor>()

    // Любой метод с mutex выполняется атомарно
    suspend fun addTreasure(gold: Gold) = mutex.withLock {
        treasure.add(gold)
    }

    suspend fun takeTreasure(): Gold? = mutex.withLock {
        treasure.removeLastOrNull()
    }

    // Без suspend — безопасно без mutex
    val islandName: String = "Treasure Island"
}

// Использование аналогично Swift actor
val island = Island()

scope.launch {
    island.addTreasure(Gold(weight = 100))
}

scope.launch {
    val gold = island.takeTreasure()
    gold?.let { println("Получили золото: ${it.weight}") }
}
```

---

## Проверь себя

### Вопрос 1: Понимание async/await

**Что выведет следующий код?**

**Swift:**
```swift
func test() async {
    print("1")
    async let a = fetchA()  // fetchA() prints "A" and returns "a"
    async let b = fetchB()  // fetchB() prints "B" and returns "b"
    print("2")
    let results = await [a, b]
    print("3: \(results)")
}
```

**Kotlin:**
```kotlin
suspend fun test() {
    println("1")
    coroutineScope {
        val a = async { fetchA() }  // fetchA() prints "A" and returns "a"
        val b = async { fetchB() }  // fetchB() prints "B" and returns "b"
        println("2")
        val results = listOf(a.await(), b.await())
        println("3: $results")
    }
}
```

<details>
<summary>Ответ</summary>

**Вывод:**
```
1
2
A (или B — порядок не определён)
B (или A)
3: [a, b]
```

**Объяснение:**
- `1` выводится первым
- `async let` / `async { }` запускают задачи, но не ждут их
- `2` выводится сразу после запуска задач
- `A` и `B` выводятся параллельно в неопределённом порядке
- `3` выводится после завершения обеих задач

</details>

### Вопрос 2: Отмена и structured concurrency

**Что произойдёт при отмене task/job?**

**Swift:**
```swift
let task = Task {
    try await withThrowingTaskGroup(of: Void.self) { group in
        group.addTask { try await longOperation1() }
        group.addTask { try await longOperation2() }
    }
}

// Через 1 секунду:
task.cancel()
```

**Kotlin:**
```kotlin
val job = scope.launch {
    coroutineScope {
        launch { longOperation1() }
        launch { longOperation2() }
    }
}

// Через 1 секунду:
job.cancel()
```

<details>
<summary>Ответ</summary>

**Произойдёт:**
1. Отмена `task`/`job` распространится на все дочерние задачи
2. `longOperation1()` и `longOperation2()` получат сигнал отмены
3. Если они проверяют отмену (`Task.checkCancellation()` / `ensureActive()`), они прервутся
4. `TaskGroup` / `coroutineScope` завершится с `CancellationError`

**Ключевой момент:** Structured concurrency гарантирует, что отмена родителя отменяет всех детей.

</details>

### Вопрос 3: Actor isolation

**Скомпилируется ли этот код?**

**Swift:**
```swift
actor Counter {
    var value = 0
}

let counter = Counter()

// Вариант A:
counter.value += 1

// Вариант B:
Task {
    counter.value += 1
}

// Вариант C:
Task {
    await counter.value += 1
}
```

<details>
<summary>Ответ</summary>

**Не скомпилируется ни один вариант!**

- **Вариант A:** Доступ к actor требует `await`
- **Вариант B:** Нет `await` перед обращением к actor
- **Вариант C:** `+=` — это read-modify-write, нельзя сделать атомарно через await

**Правильное решение:**
```swift
actor Counter {
    var value = 0

    func increment() {
        value += 1
    }
}

let counter = Counter()
Task {
    await counter.increment()  // Это работает!
}
```

</details>

### Вопрос 4: Dispatchers и потоки

**На каком потоке выполняется код?**

**Kotlin:**
```kotlin
suspend fun mystery() {
    println("1: ${Thread.currentThread().name}")

    withContext(Dispatchers.IO) {
        println("2: ${Thread.currentThread().name}")
    }

    println("3: ${Thread.currentThread().name}")

    withContext(Dispatchers.Main) {
        println("4: ${Thread.currentThread().name}")
    }

    println("5: ${Thread.currentThread().name}")
}

// Вызов из Main потока:
MainScope().launch {
    mystery()
}
```

<details>
<summary>Ответ</summary>

**Вывод:**
```
1: main
2: DefaultDispatcher-worker-X (какой-то IO поток)
3: main
4: main
5: main
```

**Объяснение:**
- `1` — мы на Main, потому что вызвали из MainScope
- `2` — переключились на IO dispatcher
- `3` — вернулись на Main (withContext восстанавливает контекст)
- `4` — явно на Main
- `5` — остаёмся на Main

**Ключевой момент:** `withContext` не только переключает на указанный dispatcher, но и возвращает на исходный после завершения блока.

</details>

---

## Связанные темы

- [[ios-async-await]] — Глубокое погружение в Swift async/await
- [[kotlin-coroutines]] — Полное руководство по Kotlin Coroutines
- [[ios-combine]] — Reactive programming в Swift с Combine
- [[kotlin-flow]] — Kotlin Flow и реактивные потоки
- [[cross-reactive-streams]] — Сравнение Combine vs Flow
- [[kmp-concurrency]] — Конкурентность в Kotlin Multiplatform
- [[swift-actors]] — Actor model в Swift
- [[kotlin-channels]] — Channels и actor pattern в Kotlin

---

## Источники

### Официальная документация

1. **Swift Concurrency**
   - [Swift Evolution: Concurrency](https://github.com/apple/swift-evolution/blob/main/proposals/0296-async-await.md)
   - [Swift Concurrency — The Swift Programming Language](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
   - [WWDC21: Meet async/await in Swift](https://developer.apple.com/videos/play/wwdc2021/10132/)
   - [WWDC21: Protect mutable state with Swift actors](https://developer.apple.com/videos/play/wwdc2021/10133/)

2. **Kotlin Coroutines**
   - [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
   - [Structured Concurrency in Kotlin](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
   - [Kotlin Flow](https://kotlinlang.org/docs/flow.html)
   - [Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

### Статьи и туториалы

3. **Сравнительные материалы**
   - [Comparing Swift's async/await with Kotlin Coroutines](https://www.swiftbysundell.com)
   - [From Callbacks to Coroutines: Kotlin vs Swift](https://proandroiddev.com)
   - [Modern Concurrency on Mobile Platforms](https://medium.com)

4. **Глубокое погружение**
   - [Understanding Swift Actors](https://www.hackingwithswift.com/swift/5.5/actors)
   - [Kotlin Coroutines Deep Dive — Marcin Moskala](https://leanpub.com/coroutines)
   - [Swift Concurrency Manifesto](https://gist.github.com/lattner/31ed37682ef1576b16bca1432ea9f782)

### Инструменты и библиотеки

5. **KMP и кросс-платформа**
   - [SKIE — Swift Kotlin Interface Enhancer](https://skie.touchlab.co)
   - [KMP-NativeCoroutines](https://github.com/nicklockwood/KMP-NativeCoroutines)
   - [Kotlin Multiplatform Mobile](https://kotlinlang.org/docs/multiplatform-mobile-getting-started.html)

---

## Итоги

Современная конкурентность в Swift и Kotlin решает одни и те же проблемы похожими способами:

| Проблема | Swift решение | Kotlin решение |
|----------|---------------|----------------|
| Callback hell | async/await | suspend functions |
| Thread management | Task, TaskGroup | launch, coroutineScope |
| Race conditions | actor | Mutex, Channel |
| Main thread safety | @MainActor | Dispatchers.Main |
| Cancellation | Structured concurrency | Structured concurrency |

**Ключевые выводы:**

1. **Structured concurrency** — главная концепция обеих платформ
2. **Actor model** встроен в Swift, эмулируется в Kotlin через Mutex/Channel
3. **KMP** позволяет использовать корутины на iOS через Swift interop
4. **Обе системы** требуют явной обработки отмены и понимания точек приостановки

Выбор между платформами определяется экосистемой, а не качеством concurrency model — обе достаточно мощные и выразительные для современных мобильных приложений.

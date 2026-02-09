---
title: "SwiftData: современная персистентность в iOS"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/data
  - type/deep-dive
  - level/intermediate
related:
  - "[[ios-core-data]]"
  - "[[ios-swiftui]]"
  - "[[ios-cloudkit]]"
---

## TL;DR

**SwiftData** — современный фреймворк персистентности от Apple (iOS 17+), который использует макросы Swift для декларативного описания моделей данных. Заменяет Core Data с более простым API, полной интеграцией SwiftUI, и автоматической схемой без NSManagedObject.

**Главные преимущества**: чистый Swift-синтаксис, @Query для реактивного связывания, автоматическая миграция схемы, CloudKit-синхронизация из коробки, меньше boilerplate-кода.

**Используй SwiftData когда**: новый проект на iOS 17+, простые/средние модели данных, SwiftUI-приоритет, нужна CloudKit-синхронизация. Core Data для: сложные миграции, legacy-код, iOS <17, специфичные Core Data фичи.

---

## Философия и Обзор

### Аналогия: SwiftData как Современный Архив

Представь **Core Data** как традиционную библиотеку с картотекой:
- Нужно заполнять карточки вручную (NSManagedObject)
- Сложные правила каталогизации (NSEntityDescription, NSPersistentContainer)
- Требуется библиотекарь для каждого запроса (NSFetchRequest)

**SwiftData** — это умная библиотека с AI:
- Книги регистрируются автоматически по обложке (@Model)
- Просто говоришь "найди все книги автора X" (@Query)
- Автоматическая синхронизация между филиалами (CloudKit)

```
┌─────────────────────────────────────────────────────────┐
│                    SwiftData Stack                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  SwiftUI Views                                          │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │  @Query      │  │  @Bindable   │                    │
│  │  автофетч    │  │  реактивность│                    │
│  └──────┬───────┘  └──────┬───────┘                    │
│         │                  │                             │
│         v                  v                             │
│  ┌─────────────────────────────────┐                    │
│  │      ModelContext               │                    │
│  │  (управление объектами)         │                    │
│  └─────────────┬───────────────────┘                    │
│                │                                         │
│                v                                         │
│  ┌─────────────────────────────────┐                    │
│  │      ModelContainer             │                    │
│  │  (хранилище + конфигурация)     │                    │
│  └─────────────┬───────────────────┘                    │
│                │                                         │
│                v                                         │
│  ┌─────────────────────────────────┐                    │
│  │      SQLite / CloudKit          │                    │
│  │  (физическое хранилище)         │                    │
│  └─────────────────────────────────┘                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Ключевые Концепции

**@Model Macro** — превращает обычный Swift-класс в персистентную модель:
- Автоматическая генерация схемы
- Наблюдаемые свойства (Observable)
- Поддержка relationships и constraints

**ModelContainer** — хранилище данных:
- Настройка persistence (in-memory, file, CloudKit)
- Управление схемой и миграциями
- Внедряется в SwiftUI через `.modelContainer()`

**ModelContext** — аналог NSManagedObjectContext:
- Управление изменениями (insert, delete, save)
- Транзакции и undo/redo
- Автоматически доступен в SwiftUI через Environment

**@Query** — декларативный фетчинг для SwiftUI:
- Автоматическое обновление view при изменениях
- Predicates, sorting, filtering
- Zero boilerplate для типовых запросов

---

## @Model: Определение Схемы

### Базовая Модель

```swift
import SwiftData
import Foundation

@Model
final class Book {
    var title: String
    var author: String
    var publishedYear: Int
    var isbn: String?
    var coverImage: Data?
    var createdAt: Date

    init(title: String, author: String, publishedYear: Int, isbn: String? = nil) {
        self.title = title
        self.author = author
        self.publishedYear = publishedYear
        self.isbn = isbn
        self.createdAt = Date()
    }
}
```

**Автоматическое поведение:**
- Все stored properties становятся персистентными
- Поддержка Optional типов
- Codable support из коробки
- Observable для SwiftUI reactivity

### Поддерживаемые Типы

```swift
@Model
final class SupportedTypes {
    // Примитивы
    var string: String
    var int: Int
    var double: Double
    var bool: Bool
    var decimal: Decimal

    // Foundation типы
    var date: Date
    var url: URL
    var uuid: UUID
    var data: Data

    // Optional
    var optionalString: String?

    // Collections (с ограничениями)
    var tags: [String]  // Массив примитивов

    // Enum с RawRepresentable
    var status: BookStatus

    // Relationships
    var author: Author?
    var reviews: [Review]

    init() {
        self.string = ""
        self.int = 0
        self.double = 0.0
        self.bool = false
        self.decimal = 0
        self.date = Date()
        self.url = URL(string: "https://example.com")!
        self.uuid = UUID()
        self.data = Data()
        self.tags = []
        self.status = .available
    }
}

enum BookStatus: String, Codable {
    case available
    case borrowed
    case reserved
}
```

---

## @Attribute: Кастомизация Свойств

### Уникальность и Индексы

```swift
@Model
final class User {
    @Attribute(.unique) var email: String
    @Attribute(.unique) var username: String

    var fullName: String
    var registeredAt: Date

    init(email: String, username: String, fullName: String) {
        self.email = email
        self.username = username
        self.fullName = fullName
        self.registeredAt = Date()
    }
}
```

**@Attribute(.unique)**:
- Гарантирует уникальность значения
- Автоматически создает индекс
- Используется для upsert-операций

### Внешнее Хранение (externalStorage)

```swift
@Model
final class VideoFile {
    var title: String

    // Большие данные хранятся отдельно от SQLite
    @Attribute(.externalStorage) var videoData: Data?
    @Attribute(.externalStorage) var thumbnail: Data?

    var duration: TimeInterval
    var uploadedAt: Date

    init(title: String, videoData: Data?, duration: TimeInterval) {
        self.title = title
        self.videoData = videoData
        self.duration = duration
        self.uploadedAt = Date()
    }
}
```

**Когда использовать .externalStorage:**
- Файлы > 100KB (images, videos, documents)
- Улучшает производительность SQLite
- Автоматическая очистка при удалении модели

### Transient Properties (Не Персистентные)

```swift
@Model
final class Article {
    var title: String
    var content: String
    var publishedAt: Date

    // Не сохраняется в базу
    @Transient var isNew: Bool {
        Date().timeIntervalSince(publishedAt) < 86400 // 24 часа
    }

    // Вычисляемое свойство с backing storage
    @Transient var wordCount: Int = 0

    init(title: String, content: String) {
        self.title = title
        self.content = content
        self.publishedAt = Date()
        self.wordCount = content.split(separator: " ").count
    }
}
```

### Оригинальное Имя (originalName)

```swift
@Model
final class Product {
    // Переименовываем свойство, но в БД остается старое имя
    @Attribute(originalName: "product_name") var name: String
    @Attribute(originalName: "product_price") var price: Decimal

    init(name: String, price: Decimal) {
        self.name = name
        self.price = price
    }
}
```

**Сценарии использования:**
- Миграция с Core Data (сохраняем совместимость)
- Рефакторинг без пересоздания базы
- Соответствие backend naming conventions

---

## Relationships: Связи Между Моделями

### One-to-Many: Автор и Книги

```swift
@Model
final class Author {
    var name: String
    var biography: String
    var bornDate: Date

    // One-to-Many: один автор — много книг
    @Relationship(deleteRule: .cascade, inverse: \Book.author)
    var books: [Book]

    init(name: String, biography: String, bornDate: Date) {
        self.name = name
        self.biography = biography
        self.bornDate = bornDate
        self.books = []
    }
}

@Model
final class Book {
    var title: String
    var publishedYear: Int

    // Many-to-One: много книг — один автор
    var author: Author?

    init(title: String, publishedYear: Int) {
        self.title = title
        self.publishedYear = publishedYear
    }
}
```

### Delete Rules

```swift
@Model
final class Library {
    var name: String

    // .cascade: при удалении библиотеки удаляются все книги
    @Relationship(deleteRule: .cascade)
    var books: [Book]

    // .nullify: при удалении библиотеки member.library = nil
    @Relationship(deleteRule: .nullify)
    var members: [Member]

    // .deny: нельзя удалить, если есть loans
    @Relationship(deleteRule: .deny)
    var loans: [Loan]

    init(name: String) {
        self.name = name
        self.books = []
        self.members = []
        self.loans = []
    }
}
```

**Delete Rules:**
- `.cascade` — удалить связанные объекты
- `.nullify` (default) — обнулить связь
- `.deny` — запретить удаление если есть связи
- `.noAction` — не делать ничего (осторожно!)

### Many-to-Many: Студенты и Курсы

```swift
@Model
final class Student {
    var name: String
    var studentID: String

    // Many-to-Many через массив
    @Relationship(inverse: \Course.students)
    var courses: [Course]

    init(name: String, studentID: String) {
        self.name = name
        self.studentID = studentID
        self.courses = []
    }
}

@Model
final class Course {
    var title: String
    var courseCode: String

    @Relationship(inverse: \Student.courses)
    var students: [Student]

    init(title: String, courseCode: String) {
        self.title = title
        self.courseCode = courseCode
        self.students = []
    }
}

// Использование
let student = Student(name: "Alice", studentID: "12345")
let course = Course(title: "iOS Development", courseCode: "CS101")

student.courses.append(course)  // Автоматически обновляет course.students
context.insert(student)
context.insert(course)
```

### Inverse Relationships

```swift
@Model
final class Post {
    var title: String
    var content: String

    // Указываем обратную связь через KeyPath
    @Relationship(inverse: \Comment.post)
    var comments: [Comment]

    init(title: String, content: String) {
        self.title = title
        self.content = content
        self.comments = []
    }
}

@Model
final class Comment {
    var text: String
    var createdAt: Date

    // SwiftData автоматически управляет обратной связью
    var post: Post?

    init(text: String) {
        self.text = text
        self.createdAt = Date()
    }
}
```

---

## ModelContainer: Настройка Хранилища

### Базовая Конфигурация в SwiftUI

```swift
import SwiftUI
import SwiftData

@main
struct BookLibraryApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Book.self, Author.self])
    }
}
```

### Продвинутая Конфигурация

```swift
@main
struct BookLibraryApp: App {
    let container: ModelContainer

    init() {
        let schema = Schema([
            Book.self,
            Author.self,
            Review.self
        ])

        let configuration = ModelConfiguration(
            schema: schema,
            url: URL.documentsDirectory.appending(path: "library.store"),
            allowsSave: true,
            cloudKitDatabase: .automatic  // CloudKit sync
        )

        do {
            container = try ModelContainer(
                for: schema,
                configurations: [configuration]
            )
        } catch {
            fatalError("Failed to configure ModelContainer: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(container)
    }
}
```

### In-Memory Storage (Для Тестов)

```swift
// Preview или Unit-тесты
@MainActor
func createPreviewContainer() -> ModelContainer {
    let schema = Schema([Book.self, Author.self])
    let configuration = ModelConfiguration(
        schema: schema,
        isStoredInMemoryOnly: true  // Не сохраняется на диск
    )

    let container = try! ModelContainer(
        for: schema,
        configurations: [configuration]
    )

    // Заполняем моками
    let context = container.mainContext
    let author = Author(name: "Sample Author", biography: "", bornDate: Date())
    let book = Book(title: "Sample Book", publishedYear: 2024)
    book.author = author

    context.insert(author)
    context.insert(book)

    return container
}

// Использование в Preview
#Preview {
    ContentView()
        .modelContainer(createPreviewContainer())
}
```

### Множественные Хранилища

```swift
@main
struct MultiStoreApp: App {
    let userContainer: ModelContainer
    let cacheContainer: ModelContainer

    init() {
        // Основное хранилище с CloudKit
        userContainer = try! ModelContainer(
            for: [User.self, Settings.self],
            configurations: [
                ModelConfiguration(
                    cloudKitDatabase: .automatic
                )
            ]
        )

        // Кеш без CloudKit
        cacheContainer = try! ModelContainer(
            for: [CachedImage.self, TempData.self],
            configurations: [
                ModelConfiguration(
                    url: URL.cachesDirectory.appending(path: "cache.store"),
                    cloudKitDatabase: .none
                )
            ]
        )
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .modelContainer(userContainer)
                .environment(\.cacheContainer, cacheContainer)
        }
    }
}
```

---

## ModelContext: Управление Данными

### Получение Context в SwiftUI

```swift
struct BookListView: View {
    // Автоматически из Environment (через .modelContainer)
    @Environment(\.modelContext) private var context

    @Query private var books: [Book]

    var body: some View {
        List {
            ForEach(books) { book in
                Text(book.title)
            }
        }
        .toolbar {
            Button("Add") {
                addBook()
            }
        }
    }

    private func addBook() {
        let newBook = Book(
            title: "New Book",
            author: "Unknown",
            publishedYear: 2024
        )
        context.insert(newBook)

        // Автосохранение или явный save
        try? context.save()
    }
}
```

### CRUD Операции

```swift
class BookService {
    let context: ModelContext

    init(context: ModelContext) {
        self.context = context
    }

    // Create
    func addBook(title: String, author: String, year: Int) throws {
        let book = Book(title: title, author: author, publishedYear: year)
        context.insert(book)
        try context.save()
    }

    // Read (через @Query в SwiftUI или FetchDescriptor)
    func fetchBooks() throws -> [Book] {
        let descriptor = FetchDescriptor<Book>(
            sortBy: [SortDescriptor(\.title)]
        )
        return try context.fetch(descriptor)
    }

    // Update
    func updateBook(_ book: Book, newTitle: String) throws {
        book.title = newTitle
        try context.save()  // Изменения автоматически отслеживаются
    }

    // Delete
    func deleteBook(_ book: Book) throws {
        context.delete(book)
        try context.save()
    }

    // Batch Delete
    func deleteAllBooks() throws {
        try context.delete(model: Book.self)
        try context.save()
    }
}
```

### Autosave и Manual Save

```swift
// Настройка autosave
context.autosaveEnabled = true  // Default: true в SwiftUI

// Проверка изменений
if context.hasChanges {
    try context.save()
}

// Rollback изменений
context.rollback()

// Проверка вставленных/удаленных
let inserted = context.insertedModelsArray
let deleted = context.deletedModelsArray
```

### Undo/Redo Manager

```swift
struct EditBookView: View {
    @Environment(\.modelContext) private var context
    @Bindable var book: Book

    var body: some View {
        Form {
            TextField("Title", text: $book.title)
            TextField("Author", text: $book.author)
        }
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Button("Undo") {
                    context.undoManager?.undo()
                }
                .disabled(!(context.undoManager?.canUndo ?? false))

                Button("Redo") {
                    context.undoManager?.redo()
                }
                .disabled(!(context.undoManager?.canRedo ?? false))
            }
        }
    }
}
```

---

## @Query: Декларативный Фетчинг в SwiftUI

### Базовое Использование

```swift
struct BookListView: View {
    // Простейший запрос — все книги
    @Query private var books: [Book]

    var body: some View {
        List(books) { book in
            VStack(alignment: .leading) {
                Text(book.title)
                    .font(.headline)
                Text(book.author)
                    .font(.subheadline)
            }
        }
    }
}
```

### Сортировка

```swift
struct SortedBooksView: View {
    // Сортировка по году (убывание)
    @Query(sort: \Book.publishedYear, order: .reverse)
    private var books: [Book]

    // Множественная сортировка
    @Query(sort: [
        SortDescriptor(\Book.author),
        SortDescriptor(\Book.publishedYear, order: .reverse)
    ])
    private var booksByAuthorAndYear: [Book]

    var body: some View {
        List(books) { book in
            Text("\(book.title) (\(book.publishedYear))")
        }
    }
}
```

### Фильтрация с #Predicate

```swift
struct RecentBooksView: View {
    // Книги за последние 5 лет
    @Query(filter: #Predicate<Book> { book in
        book.publishedYear >= 2020
    })
    private var recentBooks: [Book]

    var body: some View {
        List(recentBooks) { book in
            Text(book.title)
        }
    }
}
```

### Динамические Запросы

```swift
struct FilteredBooksView: View {
    @State private var searchText = ""
    @State private var minimumYear = 2000

    var body: some View {
        BookQueryView(searchText: searchText, minimumYear: minimumYear)
            .searchable(text: $searchText)
            .toolbar {
                Picker("Year", selection: $minimumYear) {
                    Text("2000+").tag(2000)
                    Text("2010+").tag(2010)
                    Text("2020+").tag(2020)
                }
            }
    }
}

struct BookQueryView: View {
    let searchText: String
    let minimumYear: Int

    // @Query пересоздается при изменении init-параметров
    init(searchText: String, minimumYear: Int) {
        self.searchText = searchText
        self.minimumYear = minimumYear

        let predicate = #Predicate<Book> { book in
            (searchText.isEmpty || book.title.localizedStandardContains(searchText)) &&
            book.publishedYear >= minimumYear
        }

        _books = Query(
            filter: predicate,
            sort: [SortDescriptor(\.title)]
        )
    }

    @Query private var books: [Book]

    var body: some View {
        List(books) { book in
            VStack(alignment: .leading) {
                Text(book.title)
                Text("\(book.publishedYear)")
                    .font(.caption)
            }
        }
    }
}
```

### Animation с @Query

```swift
struct AnimatedBookList: View {
    @Query(sort: \.createdAt, order: .reverse, animation: .default)
    private var books: [Book]

    @Environment(\.modelContext) private var context

    var body: some View {
        List {
            ForEach(books) { book in
                BookRow(book: book)
            }
            .onDelete(perform: deleteBooks)
        }
        .animation(.default, value: books.count)
    }

    private func deleteBooks(at offsets: IndexSet) {
        for index in offsets {
            context.delete(books[index])
        }
    }
}
```

---

## #Predicate: Продвинутая Фильтрация

### Базовые Операторы

```swift
// Равенство
#Predicate<Book> { $0.author == "Tolkien" }

// Сравнение
#Predicate<Book> { $0.publishedYear > 2000 }
#Predicate<Book> { $0.publishedYear >= 2000 && $0.publishedYear <= 2010 }

// Строки
#Predicate<Book> { $0.title.localizedStandardContains("Swift") }
#Predicate<Book> { $0.title.starts(with: "iOS") }

// Optional
#Predicate<Book> { $0.isbn != nil }

// Массивы
#Predicate<Author> { $0.books.count > 5 }
```

### Комбинирование Условий

```swift
struct ComplexQueryView: View {
    @Query(filter: #Predicate<Book> { book in
        // AND
        book.publishedYear >= 2020 &&
        book.author.contains("Martin") &&
        book.isbn != nil
    })
    private var recentMartinBooks: [Book]

    @Query(filter: #Predicate<Book> { book in
        // OR (через ||)
        book.author == "Tolkien" || book.author == "Lewis"
    })
    private var fantasyAuthors: [Book]

    @Query(filter: #Predicate<Book> { book in
        // NOT
        !(book.publishedYear < 2000)
    })
    private var modernBooks: [Book]

    var body: some View {
        Text("Complex queries")
    }
}
```

### Relationships в Predicate

```swift
// Фильтрация через relationship
@Query(filter: #Predicate<Book> { book in
    book.author?.name == "Stephen King"
})
private var kingBooks: [Book]

// Проверка наличия связей
@Query(filter: #Predicate<Author> { author in
    !author.books.isEmpty  // Авторы с книгами
})
private var authorsWithBooks: [Author]

// Сложные вложенные условия
@Query(filter: #Predicate<Author> { author in
    author.books.contains(where: { $0.publishedYear > 2020 })
})
private var authorsWithRecentBooks: [Author]
```

### Date Filtering

```swift
struct DateFilterView: View {
    let oneWeekAgo = Calendar.current.date(byAdding: .day, value: -7, to: Date())!

    var body: some View {
        RecentArticlesView(sinceDate: oneWeekAgo)
    }
}

struct RecentArticlesView: View {
    let sinceDate: Date

    init(sinceDate: Date) {
        self.sinceDate = sinceDate

        _articles = Query(filter: #Predicate<Article> { article in
            article.publishedAt >= sinceDate
        }, sort: \.publishedAt, order: .reverse)
    }

    @Query private var articles: [Article]

    var body: some View {
        List(articles) { article in
            Text(article.title)
        }
    }
}
```

### Ограничения #Predicate (2025)

**Не поддерживаются:**
- Регулярные выражения
- Case-insensitive сравнение (кроме `.localizedStandardContains`)
- Вложенные KeyPaths глубже 1 уровня
- Агрегатные функции (SUM, AVG)
- Subqueries

**Workaround:**
```swift
// ❌ Не работает: вложенный relationship
#Predicate<Book> { book in
    book.author?.publisher?.name == "Penguin"
}

// ✅ Фильтруем в Swift
@Query private var allBooks: [Book]

var penguinBooks: [Book] {
    allBooks.filter { $0.author?.publisher?.name == "Penguin" }
}
```

---

## Migrations: Версионирование Схемы

### Простая Миграция (Автоматическая)

Для совместимых изменений SwiftData мигрирует автоматически:

```swift
// Версия 1
@Model
final class Book {
    var title: String
    var author: String

    init(title: String, author: String) {
        self.title = title
        self.author = author
    }
}

// Версия 2 — добавили свойства (легкая миграция)
@Model
final class Book {
    var title: String
    var author: String
    var publishedYear: Int  // Новое свойство
    var isbn: String?       // Новое optional свойство

    init(title: String, author: String, publishedYear: Int = 2024) {
        self.title = title
        self.author = author
        self.publishedYear = publishedYear
    }
}
```

**Автоматические миграции работают для:**
- Добавление новых optional свойств
- Добавление новых свойств с default значениями
- Удаление свойств
- Переименование через `@Attribute(originalName:)`

### VersionedSchema: Явная Версионность

```swift
import SwiftData

enum LibrarySchemaV1: VersionedSchema {
    static var versionIdentifier: Schema.Version = .init(1, 0, 0)

    static var models: [any PersistentModel.Type] {
        [Book.self, Author.self]
    }

    @Model
    final class Book {
        var title: String
        var authorName: String  // Просто строка

        init(title: String, authorName: String) {
            self.title = title
            self.authorName = authorName
        }
    }

    @Model
    final class Author {
        var name: String
        init(name: String) {
            self.name = name
        }
    }
}

enum LibrarySchemaV2: VersionedSchema {
    static var versionIdentifier: Schema.Version = .init(2, 0, 0)

    static var models: [any PersistentModel.Type] {
        [Book.self, Author.self]
    }

    @Model
    final class Book {
        var title: String
        var publishedYear: Int

        // Теперь relationship вместо строки
        var author: Author?

        init(title: String, publishedYear: Int) {
            self.title = title
            self.publishedYear = publishedYear
        }
    }

    @Model
    final class Author {
        var name: String
        @Relationship(deleteRule: .cascade) var books: [Book]

        init(name: String) {
            self.name = name
            self.books = []
        }
    }
}
```

### SchemaMigrationPlan: Кастомная Логика

```swift
enum LibraryMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [LibrarySchemaV1.self, LibrarySchemaV2.self]
    }

    static var stages: [MigrationStage] {
        [migrateV1toV2]
    }

    static let migrateV1toV2 = MigrationStage.custom(
        fromVersion: LibrarySchemaV1.self,
        toVersion: LibrarySchemaV2.self,
        willMigrate: { context in
            // Pre-migration: создаем Author объекты из authorName
            let books = try context.fetch(FetchDescriptor<LibrarySchemaV1.Book>())

            // Собираем уникальные имена авторов
            let authorNames = Set(books.map { $0.authorName })

            // Создаем Author объекты
            var authorsDict: [String: LibrarySchemaV2.Author] = [:]
            for name in authorNames {
                let author = LibrarySchemaV2.Author(name: name)
                context.insert(author)
                authorsDict[name] = author
            }

            try context.save()
        },
        didMigrate: { context in
            // Post-migration: связываем книги с авторами
            let books = try context.fetch(FetchDescriptor<LibrarySchemaV2.Book>())
            let authors = try context.fetch(FetchDescriptor<LibrarySchemaV2.Author>())

            // Создаем словарь авторов по имени
            let authorsDict = Dictionary(
                uniqueKeysWithValues: authors.map { ($0.name, $0) }
            )

            // Устанавливаем relationships
            for book in books {
                // В V2 нет authorName, но можем получить через private API
                // или сохранить mapping в willMigrate
                if let author = authorsDict[book.author?.name ?? ""] {
                    book.author = author
                }
            }

            try context.save()
        }
    )
}

// Использование в App
@main
struct LibraryApp: App {
    let container: ModelContainer

    init() {
        do {
            container = try ModelContainer(
                for: LibrarySchemaV2.Book.self, LibrarySchemaV2.Author.self,
                migrationPlan: LibraryMigrationPlan.self
            )
        } catch {
            fatalError("Migration failed: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(container)
    }
}
```

### Lightweight vs Custom Migrations

```
┌────────────────────────────────────────────────────┐
│         Migration Decision Tree                    │
├────────────────────────────────────────────────────┤
│                                                     │
│  Изменение схемы?                                  │
│         │                                           │
│         ├─ Добавить Optional/Default свойство?     │
│         │        └─> Lightweight (Автоматически)   │
│         │                                           │
│         ├─ Переименовать свойство?                 │
│         │        └─> @Attribute(originalName:)     │
│         │                                           │
│         ├─ Удалить свойство?                       │
│         │        └─> Lightweight (Автоматически)   │
│         │                                           │
│         ├─ Изменить тип свойства?                  │
│         │        └─> Custom Migration              │
│         │                                           │
│         ├─ Добавить/изменить relationship?         │
│         │        └─> Custom Migration              │
│         │                                           │
│         └─ Трансформация данных?                   │
│                  └─> Custom Migration              │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## Background Operations: ModelActor

### Проблема Main Thread Blocking

```swift
// ❌ ПЛОХО: блокирует UI при большом импорте
struct ImportView: View {
    @Environment(\.modelContext) private var context
    @State private var isImporting = false

    var body: some View {
        Button("Import 10000 books") {
            isImporting = true
            importBooks()  // Блокирует UI!
            isImporting = false
        }
        .disabled(isImporting)
    }

    func importBooks() {
        for i in 1...10000 {
            let book = Book(
                title: "Book \(i)",
                author: "Author \(i)",
                publishedYear: 2024
            )
            context.insert(book)
        }
        try? context.save()
    }
}
```

### ModelActor: Background Context

```swift
import SwiftData

@ModelActor
actor BookImporter {
    // ModelActor автоматически создает background ModelContext

    func importBooks(from jsonData: Data) async throws {
        let decoder = JSONDecoder()
        let bookData = try decoder.decode([BookDTO].self, from: jsonData)

        for dto in bookData {
            let book = Book(
                title: dto.title,
                author: dto.author,
                publishedYear: dto.year
            )
            modelContext.insert(book)

            // Периодический save для больших батчей
            if bookData.firstIndex(of: dto)! % 100 == 0 {
                try modelContext.save()
            }
        }

        // Финальный save
        try modelContext.save()
    }

    func cleanupOldBooks() async throws {
        let tenYearsAgo = Calendar.current.date(byAdding: .year, value: -10, to: Date())!

        let descriptor = FetchDescriptor<Book>(
            predicate: #Predicate { $0.publishedYear < tenYearsAgo.year }
        )

        let oldBooks = try modelContext.fetch(descriptor)

        for book in oldBooks {
            modelContext.delete(book)
        }

        try modelContext.save()
    }
}

// Использование из SwiftUI
struct ImportView: View {
    @State private var importer: BookImporter?
    @State private var isImporting = false

    var body: some View {
        Button("Import Books") {
            Task {
                isImporting = true
                defer { isImporting = false }

                guard let importer else { return }

                do {
                    let data = try await loadBookData()
                    try await importer.importBooks(from: data)
                } catch {
                    print("Import failed: \(error)")
                }
            }
        }
        .disabled(isImporting)
        .task {
            // Создаем actor с доступом к container
            importer = BookImporter(modelContainer: /* your container */)
        }
    }

    func loadBookData() async throws -> Data {
        // Load from network/file
        Data()
    }
}
```

### Background Processing Best Practices

```swift
@ModelActor
actor DataProcessor {
    private let batchSize = 100

    func processBulkOperation<T: PersistentModel>(
        _ items: [T],
        process: (T) async throws -> Void
    ) async throws {
        var processed = 0

        for item in items {
            try await process(item)
            processed += 1

            // Батч-сохранение
            if processed % batchSize == 0 {
                try modelContext.save()
                print("Processed \(processed)/\(items.count)")
            }
        }

        // Финальный save для остатка
        if processed % batchSize != 0 {
            try modelContext.save()
        }
    }

    func fetchAndProcess() async throws {
        let descriptor = FetchDescriptor<Book>(
            sortBy: [SortDescriptor(\.createdAt)]
        )

        let books = try modelContext.fetch(descriptor)

        try await processBulkOperation(books) { book in
            // Какая-то тяжелая обработка
            book.processedAt = Date()
        }
    }
}
```

---

## CloudKit Integration

### Базовая Настройка

**1. Enable CloudKit Capability:**
```
Xcode → Target → Signing & Capabilities → + Capability → iCloud
  ✓ CloudKit
  → Containers: выбрать/создать контейнер
```

**2. Настройка ModelContainer:**
```swift
@main
struct CloudSyncApp: App {
    let container: ModelContainer

    init() {
        let schema = Schema([Book.self, Author.self])

        let configuration = ModelConfiguration(
            schema: schema,
            // Автоматическая CloudKit-синхронизация
            cloudKitDatabase: .automatic
        )

        container = try! ModelContainer(
            for: schema,
            configurations: [configuration]
        )
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(container)
    }
}
```

**Опции cloudKitDatabase:**
- `.automatic` — синхронизация с private database (рекомендуется)
- `.private(containerIdentifier)` — явный private container
- `.none` — без CloudKit (локально)

### Мониторинг Синхронизации

```swift
struct SyncStatusView: View {
    @Environment(\.modelContext) private var context
    @State private var isSyncing = false
    @State private var syncError: Error?

    var body: some View {
        VStack {
            if isSyncing {
                ProgressView("Syncing with iCloud...")
            }

            if let error = syncError {
                Text("Sync error: \(error.localizedDescription)")
                    .foregroundStyle(.red)
            }

            Button("Check Sync Status") {
                checkSyncStatus()
            }
        }
        .task {
            observeCloudKitChanges()
        }
    }

    func checkSyncStatus() {
        // SwiftData автоматически синхронизирует
        // Проверка через NSPersistentCloudKitContainer (если нужно)
        Task {
            isSyncing = true
            try? await Task.sleep(for: .seconds(2))
            isSyncing = false
        }
    }

    func observeCloudKitChanges() {
        // Подписка на изменения (через Combine/AsyncSequence)
        // SwiftData автоматически обновляет @Query views
    }
}
```

### Конфликты и Разрешение

SwiftData автоматически разрешает конфликты по стратегии **"последний пишущий выигрывает"** (last-writer-wins).

```swift
// Кастомная логика разрешения (если нужно)
@Model
final class SyncableDocument {
    var title: String
    var content: String
    var modifiedAt: Date
    var syncVersion: Int

    init(title: String, content: String) {
        self.title = title
        self.content = content
        self.modifiedAt = Date()
        self.syncVersion = 1
    }

    // Метод для ручного merge
    func mergeConflict(with remote: SyncableDocument) {
        // Выбираем более свежую версию
        if remote.modifiedAt > self.modifiedAt {
            self.title = remote.title
            self.content = remote.content
            self.modifiedAt = remote.modifiedAt
        }
        self.syncVersion = max(self.syncVersion, remote.syncVersion) + 1
    }
}
```

### Testing с CloudKit

```swift
// Development: используем .none для тестов
@MainActor
func createTestContainer() -> ModelContainer {
    let config = ModelConfiguration(
        isStoredInMemoryOnly: true,
        cloudKitDatabase: .none  // Без CloudKit в тестах
    )

    return try! ModelContainer(
        for: Book.self,
        configurations: [config]
    )
}

// Unit Test
@Test func testBookCreation() async throws {
    let container = await createTestContainer()
    let context = container.mainContext

    let book = Book(title: "Test", author: "Author", publishedYear: 2024)
    context.insert(book)
    try context.save()

    let fetched = try context.fetch(FetchDescriptor<Book>())
    #expect(fetched.count == 1)
    #expect(fetched.first?.title == "Test")
}
```

### Ограничения CloudKit в SwiftData

**Не синхронизируются:**
- `@Attribute(.externalStorage)` данные > 10MB
- Transient properties
- Computed properties

**Ограничения:**
- Требуется iCloud аккаунт
- Квоты CloudKit (бесплатный tier ограничен)
- Нельзя смешивать CloudKit Record Zones из Core Data

---

## SwiftData vs Core Data: Детальное Сравнение

### Таблица Сравнения

| Аспект | SwiftData | Core Data |
|--------|-----------|-----------|
| **Минимальная iOS** | iOS 17+ | iOS 3+ |
| **Язык** | Pure Swift | Objective-C roots |
| **Модели** | `@Model` macro | `NSManagedObject` subclass |
| **Схема** | Автоматическая из кода | .xcdatamodel file |
| **Fetching** | `@Query` + `#Predicate` | `NSFetchRequest` + `NSPredicate` |
| **Context** | `ModelContext` | `NSManagedObjectContext` |
| **Container** | `ModelContainer` | `NSPersistentContainer` |
| **SwiftUI Integration** | Нативная (Observable) | Через `@FetchRequest` |
| **Type Safety** | Compile-time | Runtime |
| **Boilerplate** | Минимальный | Много |
| **Migrations** | Автоматические + Custom | Всегда явные |
| **CloudKit Sync** | Встроенный (`cloudKitDatabase`) | `NSPersistentCloudKitContainer` |
| **Background Operations** | `@ModelActor` | Custom queues + contexts |
| **Undo/Redo** | `UndoManager` support | Полная поддержка |
| **Batch Operations** | Ограниченные | Полные (batch insert/update/delete) |
| **Fetched Properties** | Нет | Да |
| **Abstract Entities** | Нет | Да |
| **Configurations** | Упрощенные | Гибкие (multiple stores) |
| **Debugging** | Instruments + Logs | Множество инструментов |
| **Community/Resources** | Новый (2023+) | Mature (15+ лет) |
| **Performance** | Сравнимая | Оптимизированная |

### Примеры Кода

#### Определение Модели

**SwiftData:**
```swift
@Model
final class Book {
    var title: String
    var author: String
    var publishedYear: Int

    @Relationship(deleteRule: .cascade)
    var reviews: [Review]

    init(title: String, author: String, publishedYear: Int) {
        self.title = title
        self.author = author
        self.publishedYear = publishedYear
        self.reviews = []
    }
}
```

**Core Data:**
```swift
// NSManagedObject subclass (generated)
@objc(Book)
public class Book: NSManagedObject {
    @NSManaged public var title: String
    @NSManaged public var author: String
    @NSManaged public var publishedYear: Int16
    @NSManaged public var reviews: NSSet?
}

extension Book {
    @objc(addReviewsObject:)
    @NSManaged public func addToReviews(_ value: Review)

    @objc(removeReviewsObject:)
    @NSManaged public func removeFromReviews(_ value: Review)
}
```

#### Фетчинг в SwiftUI

**SwiftData:**
```swift
struct BookListView: View {
    @Query(sort: \.title) private var books: [Book]

    var body: some View {
        List(books) { book in
            Text(book.title)
        }
    }
}
```

**Core Data:**
```swift
struct BookListView: View {
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \Book.title, ascending: true)]
    )
    private var books: FetchedResults<Book>

    var body: some View {
        List(books) { book in
            Text(book.title ?? "")
        }
    }
}
```

#### Предикаты

**SwiftData:**
```swift
@Query(filter: #Predicate<Book> { book in
    book.publishedYear >= 2020 && book.author.contains("Martin")
})
private var recentBooks: [Book]
```

**Core Data:**
```swift
@FetchRequest(
    sortDescriptors: [],
    predicate: NSPredicate(
        format: "publishedYear >= %d AND author CONTAINS %@",
        2020, "Martin"
    )
)
private var recentBooks: FetchedResults<Book>
```

---

## Когда Выбирать SwiftData vs Core Data

### Выбирай SwiftData если:

✅ **Новый проект на iOS 17+**
- Нет legacy-кода
- Не нужна поддержка старых iOS

✅ **SwiftUI-first приложение**
- Основной UI на SwiftUI
- Нужна реактивность из коробки

✅ **Простая/средняя сложность данных**
- Стандартные relationships
- Типовые миграции
- CRUD-операции

✅ **Нужен быстрый старт**
- Меньше boilerplate
- Автоматические миграции
- Простой CloudKit-sync

✅ **Хочешь современный API**
- Type-safe predicates
- Macro-based models
- Swift Concurrency

### Выбирай Core Data если:

✅ **Требуется iOS < 17**
- Поддержка iOS 13-16
- Широкая совместимость

✅ **Сложные требования к данным**
- Abstract entities
- Fetched properties
- Complex batch operations

✅ **Legacy-проект**
- Уже есть Core Data stack
- Миграция на SwiftData не оправдана

✅ **Нужны продвинутые фичи**
- Multiple persistent stores
- Custom migration с NSEntityMigrationPolicy
- Детальный контроль над faulting

✅ **Enterprise/Production-critical**
- 15+ лет battle-tested
- Больше ресурсов/документации
- Известные edge cases

### Гибридный Подход

```swift
// Можно использовать оба в одном приложении
@main
struct HybridApp: App {
    // SwiftData для новых фич
    let swiftDataContainer = try! ModelContainer(for: NewFeature.self)

    // Core Data для legacy
    let coreDataContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "LegacyModel")
        container.loadPersistentStores { _, error in
            if let error { fatalError("Core Data error: \(error)") }
        }
        return container
    }()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .modelContainer(swiftDataContainer)
                .environment(\.managedObjectContext, coreDataContainer.viewContext)
        }
    }
}
```

---

## Migration: Core Data → SwiftData

### Стратегия Миграции

```
┌──────────────────────────────────────────────────┐
│       Core Data → SwiftData Migration            │
├──────────────────────────────────────────────────┤
│                                                   │
│  Phase 1: Dual Stack (Параллельная работа)       │
│  ┌──────────────┐      ┌──────────────┐         │
│  │  Core Data   │      │  SwiftData   │         │
│  │  (legacy)    │◄────►│  (new)       │         │
│  └──────────────┘      └──────────────┘         │
│         │                      │                  │
│         v                      v                  │
│    Old Views            New Views                │
│                                                   │
│  Phase 2: Data Transfer                          │
│  ┌──────────────┐                                │
│  │  Migration   │──────► SwiftData               │
│  │  Script      │        (primary)               │
│  └──────────────┘                                │
│                                                   │
│  Phase 3: Deprecation                            │
│  ┌──────────────┐                                │
│  │  SwiftData   │ (only)                         │
│  │  (production)│                                │
│  └──────────────┘                                │
│                                                   │
└──────────────────────────────────────────────────┘
```

### Пошаговая Миграция

**Step 1: Создай SwiftData модели (параллельно)**

```swift
// Core Data (существующая)
// Book+CoreDataClass.swift (generated)
@objc(Book)
public class CDBook: NSManagedObject {
    @NSManaged public var title: String?
    @NSManaged public var author: String?
}

// SwiftData (новая)
@Model
final class Book {
    var title: String
    var author: String

    init(title: String, author: String) {
        self.title = title
        self.author = author
    }
}
```

**Step 2: Dual Container Setup**

```swift
@main
struct MigrationApp: App {
    // Старый Core Data
    let coreDataStack = CoreDataStack.shared

    // Новый SwiftData
    let swiftDataContainer = try! ModelContainer(for: Book.self)

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, coreDataStack.context)
                .modelContainer(swiftDataContainer)
        }
    }
}
```

**Step 3: Data Migration Script**

```swift
@ModelActor
actor CoreDataToSwiftDataMigrator {
    private let coreDataContext: NSManagedObjectContext

    init(modelContainer: ModelContainer, coreDataContext: NSManagedObjectContext) {
        self.modelExecutor = DefaultSerialModelExecutor(modelContext: ModelContext(modelContainer))
        self.coreDataContext = coreDataContext
    }

    func migrateBooks() async throws {
        let fetchRequest: NSFetchRequest<CDBook> = CDBook.fetchRequest()

        let cdBooks = try await coreDataContext.perform {
            try self.coreDataContext.fetch(fetchRequest)
        }

        print("Migrating \(cdBooks.count) books...")

        for cdBook in cdBooks {
            let book = Book(
                title: cdBook.title ?? "Untitled",
                author: cdBook.author ?? "Unknown"
            )

            modelContext.insert(book)

            // Батч-сохранение
            if cdBooks.firstIndex(of: cdBook)! % 100 == 0 {
                try modelContext.save()
            }
        }

        try modelContext.save()
        print("Migration complete!")
    }

    func verifyMigration() async throws -> Bool {
        let cdCount = try await coreDataContext.perform {
            try self.coreDataContext.count(for: CDBook.fetchRequest())
        }

        let sdCount = try modelContext.fetchCount(FetchDescriptor<Book>())

        return cdCount == sdCount
    }
}

// Использование
struct MigrationView: View {
    @State private var isMigrating = false
    @State private var migrationStatus = ""

    var body: some View {
        VStack {
            Text(migrationStatus)

            Button("Start Migration") {
                Task {
                    isMigrating = true
                    defer { isMigrating = false }

                    do {
                        let migrator = CoreDataToSwiftDataMigrator(
                            modelContainer: /* ... */,
                            coreDataContext: /* ... */
                        )

                        try await migrator.migrateBooks()

                        let verified = try await migrator.verifyMigration()
                        migrationStatus = verified ? "✅ Success" : "❌ Failed"
                    } catch {
                        migrationStatus = "Error: \(error)"
                    }
                }
            }
            .disabled(isMigrating)
        }
    }
}
```

**Step 4: Постепенная Замена Views**

```swift
// Старый view (Core Data)
struct OldBookListView: View {
    @FetchRequest(sortDescriptors: [])
    private var books: FetchedResults<CDBook>

    var body: some View {
        List(books) { book in
            Text(book.title ?? "")
        }
    }
}

// Новый view (SwiftData)
struct NewBookListView: View {
    @Query(sort: \.title) private var books: [Book]

    var body: some View {
        List(books) { book in
            Text(book.title)
        }
    }
}

// Feature flag для переключения
struct BookListView: View {
    @AppStorage("useSwiftData") private var useSwiftData = false

    var body: some View {
        if useSwiftData {
            NewBookListView()
        } else {
            OldBookListView()
        }
    }
}
```

---

## Limitations и Best Practices (2025)

### Текущие Ограничения SwiftData

**1. iOS 17+ Only**
```swift
// ❌ Не доступно на iOS 16
// Workaround: используй Core Data для backward compatibility
```

**2. Ограниченные Predicates**
```swift
// ❌ Нет регулярных выражений
#Predicate<Book> { $0.title.matches(/\d+/) }  // Не работает

// ✅ Workaround: фильтруй в Swift
@Query private var allBooks: [Book]
var numberedBooks: [Book] {
    allBooks.filter { $0.title.contains(/\d+/) }
}
```

**3. Нет Abstract Entities**
```swift
// ❌ Core Data abstract entity
// SwiftData: используй протоколы + конкретные модели

protocol Publishable {
    var publishedAt: Date { get }
}

@Model
final class Article: Publishable {
    var title: String
    var publishedAt: Date
}

@Model
final class Video: Publishable {
    var title: String
    var publishedAt: Date
}
```

**4. Ограничения @Query**
```swift
// ❌ Нельзя менять predicate динамически
@Query private var books: [Book]

func updateFilter(author: String) {
    // Нельзя изменить существующий @Query
}

// ✅ Workaround: пересоздавай view с новым init
FilteredBooksView(author: selectedAuthor)
```

**5. Нет Batch Operations (как в Core Data)**
```swift
// ❌ Нет NSBatchDeleteRequest эквивалента
// Нужно удалять в цикле

@ModelActor
actor BatchDeleter {
    func deleteAll() async throws {
        let books = try modelContext.fetch(FetchDescriptor<Book>())
        for book in books {
            modelContext.delete(book)
        }
        try modelContext.save()
    }
}
```

### Best Practices

**1. Используй @Attribute правильно**
```swift
@Model
final class User {
    // ✅ Unique для идентификаторов
    @Attribute(.unique) var email: String

    // ✅ externalStorage для больших файлов
    @Attribute(.externalStorage) var profileImage: Data?

    // ✅ originalName для миграций
    @Attribute(originalName: "user_name") var username: String

    init(email: String, username: String) {
        self.email = email
        self.username = username
    }
}
```

**2. Оптимизируй Relationships**
```swift
@Model
final class Author {
    var name: String

    // ✅ Указывай inverse для двунаправленных связей
    @Relationship(deleteRule: .cascade, inverse: \Book.author)
    var books: [Book]

    // ✅ Используй правильный deleteRule
    @Relationship(deleteRule: .nullify)
    var followers: [User]

    init(name: String) {
        self.name = name
        self.books = []
        self.followers = []
    }
}
```

**3. Background Operations**
```swift
// ✅ Используй @ModelActor для тяжелых операций
@ModelActor
actor DataImporter {
    func importLargeDataset() async throws {
        // Background context автоматически
        for item in largeDataset {
            let model = MyModel(data: item)
            modelContext.insert(model)

            if largeDataset.firstIndex(of: item)! % 100 == 0 {
                try modelContext.save()
            }
        }
    }
}

// ❌ Не блокируй main thread
func importOnMainThread() {
    for _ in 1...10000 {
        context.insert(Book(...))  // UI замерзнет
    }
}
```

**4. Testing Strategy**
```swift
// ✅ In-memory для тестов
@MainActor
func createTestContainer() -> ModelContainer {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    return try! ModelContainer(for: Book.self, configurations: [config])
}

// ✅ Используй Swift Testing
@Test func bookCreation() async throws {
    let container = await createTestContainer()
    let context = container.mainContext

    let book = Book(title: "Test", author: "Author", publishedYear: 2024)
    context.insert(book)
    try context.save()

    let fetched = try context.fetch(FetchDescriptor<Book>())
    #expect(fetched.count == 1)
}
```

**5. CloudKit Considerations**
```swift
// ✅ Обрабатывай оффлайн-режим
@Model
final class SyncableNote {
    var content: String
    var createdAt: Date
    var isSynced: Bool = false  // Track sync status

    init(content: String) {
        self.content = content
        self.createdAt = Date()
    }
}

// ✅ Не полагайся на мгновенную синхронизацию
// CloudKit синхронизирует асинхронно
```

---

## 6 Типичных Ошибок

### Ошибка 1: Изменение Модели без Миграции

❌ **Плохо:**
```swift
// Версия 1
@Model
final class Book {
    var title: String
    var author: String
}

// Версия 2 - изменили тип без миграции
@Model
final class Book {
    var title: String
    var author: Author  // Теперь relationship вместо String - crash!
}
```

✅ **Хорошо:**
```swift
// Используй VersionedSchema + SchemaMigrationPlan
enum BookSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Book.self] }

    @Model
    final class Book {
        var title: String
        var author: String
    }
}

enum BookSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [Book.self, Author.self] }

    @Model
    final class Book {
        var title: String
        var author: Author?  // Relationship
    }

    @Model
    final class Author {
        var name: String
        var books: [Book]
    }
}

enum BookMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [BookSchemaV1.self, BookSchemaV2.self]
    }

    static var stages: [MigrationStage] {
        [MigrationStage.custom(
            fromVersion: BookSchemaV1.self,
            toVersion: BookSchemaV2.self,
            willMigrate: { context in
                // Создай Author объекты из строк
            },
            didMigrate: nil
        )]
    }
}
```

### Ошибка 2: Блокировка Main Thread

❌ **Плохо:**
```swift
struct ImportView: View {
    @Environment(\.modelContext) private var context

    func importBooks(_ books: [BookDTO]) {
        // Блокирует UI при больших данных
        for book in books {
            let newBook = Book(
                title: book.title,
                author: book.author,
                publishedYear: book.year
            )
            context.insert(newBook)
        }
        try? context.save()  // Долгая операция на main thread
    }
}
```

✅ **Хорошо:**
```swift
@ModelActor
actor BookImporter {
    func importBooks(_ books: [BookDTO]) async throws {
        // Background context автоматически
        for (index, book) in books.enumerated() {
            let newBook = Book(
                title: book.title,
                author: book.author,
                publishedYear: book.year
            )
            modelContext.insert(newBook)

            // Батч-сохранение каждые 100 записей
            if index % 100 == 0 {
                try modelContext.save()
            }
        }
        try modelContext.save()
    }
}

struct ImportView: View {
    @State private var importer: BookImporter?

    func importBooks(_ books: [BookDTO]) {
        Task {
            guard let importer else { return }
            try? await importer.importBooks(books)
        }
    }
}
```

### Ошибка 3: Неправильное Использование @Query

❌ **Плохо:**
```swift
struct BooksView: View {
    @Query private var books: [Book]
    @State private var searchText = ""

    var filteredBooks: [Book] {
        // Фильтруем после fetcha - неэффективно!
        books.filter { $0.title.contains(searchText) }
    }

    var body: some View {
        List(filteredBooks) { book in
            Text(book.title)
        }
        .searchable(text: $searchText)
    }
}
```

✅ **Хорошо:**
```swift
struct BooksView: View {
    @State private var searchText = ""

    var body: some View {
        // Передаем searchText в отдельный view
        FilteredBooksView(searchText: searchText)
            .searchable(text: $searchText)
    }
}

struct FilteredBooksView: View {
    let searchText: String

    init(searchText: String) {
        self.searchText = searchText

        // @Query с predicate на уровне базы
        let predicate = #Predicate<Book> { book in
            searchText.isEmpty || book.title.localizedStandardContains(searchText)
        }

        _books = Query(filter: predicate, sort: \.title)
    }

    @Query private var books: [Book]

    var body: some View {
        List(books) { book in
            Text(book.title)
        }
    }
}
```

### Ошибка 4: Забыли Inverse Relationship

❌ **Плохо:**
```swift
@Model
final class Author {
    var name: String
    var books: [Book]  // Нет inverse - SwiftData не знает о связи

    init(name: String) {
        self.name = name
        self.books = []
    }
}

@Model
final class Book {
    var title: String
    var author: Author?

    init(title: String) {
        self.title = title
    }
}

// Использование
let author = Author(name: "Tolkien")
let book = Book(title: "LOTR")
author.books.append(book)  // book.author остается nil!
```

✅ **Хорошо:**
```swift
@Model
final class Author {
    var name: String

    // Указываем inverse relationship
    @Relationship(inverse: \Book.author)
    var books: [Book]

    init(name: String) {
        self.name = name
        self.books = []
    }
}

@Model
final class Book {
    var title: String
    var author: Author?

    init(title: String) {
        self.title = title
    }
}

// Использование
let author = Author(name: "Tolkien")
let book = Book(title: "LOTR")
author.books.append(book)  // book.author автоматически = author ✅
```

### Ошибка 5: Неправильный Delete Rule

❌ **Плохо:**
```swift
@Model
final class User {
    var name: String

    // Default deleteRule: .nullify
    @Relationship var posts: [Post]

    init(name: String) {
        self.name = name
        self.posts = []
    }
}

@Model
final class Post {
    var content: String
    var user: User?
}

// Удаляем пользователя
context.delete(user)
// Проблема: posts остались, но post.user = nil
// Осиротевшие посты без владельца
```

✅ **Хорошо:**
```swift
@Model
final class User {
    var name: String

    // Cascade: удаляем посты вместе с пользователем
    @Relationship(deleteRule: .cascade, inverse: \Post.user)
    var posts: [Post]

    init(name: String) {
        self.name = name
        self.posts = []
    }
}

@Model
final class Post {
    var content: String
    var user: User?
}

// Удаляем пользователя
context.delete(user)
// Все posts автоматически удаляются ✅
```

**Delete Rules по сценариям:**
```swift
// .cascade - удалить зависимые (parent-child)
@Relationship(deleteRule: .cascade) var comments: [Comment]

// .nullify - обнулить связь (independent entities)
@Relationship(deleteRule: .nullify) var followers: [User]

// .deny - запретить удаление если есть связи (important dependencies)
@Relationship(deleteRule: .deny) var activeOrders: [Order]
```

### Ошибка 6: Забыли @Attribute(.externalStorage)

❌ **Плохо:**
```swift
@Model
final class Photo {
    var title: String
    var imageData: Data  // Большие изображения в SQLite - медленно!
    var thumbnailData: Data

    init(title: String, imageData: Data, thumbnail: Data) {
        self.title = title
        self.imageData = imageData
        self.thumbnailData = thumbnail
    }
}

// Проблема:
// - SQLite файл раздувается (GB)
// - Медленные queries даже без доступа к imageData
// - Проблемы с памятью при fetch большого количества
```

✅ **Хорошо:**
```swift
@Model
final class Photo {
    var title: String

    // Большие данные хранятся отдельно
    @Attribute(.externalStorage) var imageData: Data?
    @Attribute(.externalStorage) var thumbnailData: Data?

    // Метаданные остаются в SQLite (быстрый поиск)
    var width: Int
    var height: Int
    var takenAt: Date

    init(title: String, imageData: Data?, thumbnail: Data?, width: Int, height: Int) {
        self.title = title
        self.imageData = imageData
        self.thumbnailData = thumbnail
        self.width = width
        self.height = height
        self.takenAt = Date()
    }
}

// Преимущества:
// ✅ SQLite остается компактным
// ✅ Быстрые queries по метаданным
// ✅ Данные загружаются по требованию (lazy)
// ✅ Автоматическая очистка при delete
```

---

## ASCII: SwiftData Lifecycle

```
┌────────────────────────────────────────────────────────────┐
│              SwiftData Object Lifecycle                     │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Creation                                                │
│     let book = Book(...)                                    │
│     ┌─────────────┐                                         │
│     │  Transient  │  (не в context)                         │
│     └──────┬──────┘                                         │
│            │                                                 │
│            │ context.insert(book)                            │
│            v                                                 │
│     ┌─────────────┐                                         │
│     │  Inserted   │  (в context, не в БД)                   │
│     └──────┬──────┘                                         │
│            │                                                 │
│            │ context.save()                                  │
│            v                                                 │
│     ┌─────────────┐                                         │
│     │   Saved     │  (в БД)                                 │
│     └──────┬──────┘                                         │
│            │                                                 │
│  2. Modification                                            │
│     book.title = "New"                                      │
│            │                                                 │
│            v                                                 │
│     ┌─────────────┐                                         │
│     │  Modified   │  (изменения в context)                  │
│     └──────┬──────┘                                         │
│            │                                                 │
│            │ context.save()                                  │
│            v                                                 │
│     ┌─────────────┐                                         │
│     │   Saved     │  (обновлено в БД)                       │
│     └──────┬──────┘                                         │
│            │                                                 │
│  3. Deletion                                                │
│     context.delete(book)                                    │
│            │                                                 │
│            v                                                 │
│     ┌─────────────┐                                         │
│     │   Deleted   │  (помечен для удаления)                 │
│     └──────┬──────┘                                         │
│            │                                                 │
│            │ context.save()                                  │
│            v                                                 │
│     ┌─────────────┐                                         │
│     │   Purged    │  (удалено из БД)                        │
│     └─────────────┘                                         │
│                                                             │
│  Rollback в любой момент:                                   │
│     context.rollback() → возврат к Saved состоянию          │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## Заключение

**SwiftData** — это современный шаг вперед для iOS-персистентности, который упрощает типовые задачи и естественно интегрируется с SwiftUI. Хотя у него есть ограничения по сравнению с Core Data, для большинства новых проектов на iOS 17+ это отличный выбор.

**Ключевые выводы:**
- Используй `@Model` для простого определения схемы
- `@Query` делает фетчинг в SwiftUI тривиальным
- `#Predicate` — type-safe альтернатива NSPredicate
- `@ModelActor` для background-операций без боли
- CloudKit-синхронизация работает из коробки
- Миграции упростились, но сложные случаи требуют VersionedSchema
- Core Data все еще нужен для legacy/complex случаев

**Рекомендации на 2025-2026:**
- Новые проекты → SwiftData (если iOS 17+)
- Legacy проекты → оставайся на Core Data
- Гибридный подход возможен для постепенной миграции

Related: [[ios-core-data]], [[ios-swiftui]], [[ios-cloudkit]], [[ios-combine]]

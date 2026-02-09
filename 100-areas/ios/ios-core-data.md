---
title: "Core Data: персистентность данных в iOS"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/data
  - type/deep-dive
  - level/advanced
related:
  - "[[ios-data-persistence]]"
  - "[[ios-swiftdata]]"
---

# Core Data: Персистентность данных в iOS

## TL;DR

Core Data — это объектно-графовый фреймворк от Apple для управления объектной моделью приложения с поддержкой персистентности. Это не просто ORM, а полноценный граф объектов с отслеживанием изменений, валидацией, ленивой загрузкой и миграциями схемы. Идеально подходит для сложных объектных моделей с взаимосвязями, undo/redo, синхронизацией с iCloud через CloudKit.

**Ключевое отличие от SQLite напрямую**: Core Data управляет графом объектов в памяти, SQLite — это просто деталь реализации персистентного хранилища.

## Аналогия: Библиотечная система

```
Core Data Stack = Библиотечная система
├─ NSPersistentContainer      → Здание библиотеки (инфраструктура)
├─ NSManagedObjectModel        → Каталожная система (схема данных)
├─ NSPersistentStoreCoordinator → Главный библиотекарь (координатор хранилищ)
├─ NSPersistentStore           → Архив книг (физическое хранилище)
└─ NSManagedObjectContext      → Читальный зал (рабочее пространство)
   └─ NSManagedObject          → Книга на вашем столе (объект в памяти)

Правило библиотеки: каждый читальный зал (context) привязан к одному потоку.
Чтобы работать параллельно — открываем несколько читальных залов (background contexts).
```

## Архитектура Core Data Stack

### Компоненты стека

```
┌─────────────────────────────────────────────────┐
│         Your App (SwiftUI/UIKit Views)          │
└────────────────┬────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │ Main Context   │ ← UI Thread (viewContext)
         │ (NSManagedObj  │
         │  Context)      │
         └───────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│ BG    │   │ BG    │   │ BG    │ ← Background Threads
│Context│   │Context│   │Context│
└───┬───┘   └───┬───┘   └───┬───┘
    │           │           │
    └───────────┼───────────┘
                │
    ┌───────────▼──────────────┐
    │ NSPersistentStore        │
    │ Coordinator              │ ← Координатор доступа
    └───────────┬──────────────┘
                │
    ┌───────────▼──────────────┐
    │ NSPersistentStore        │
    │ (SQLite / Binary / XML)  │ ← Физическое хранилище
    └──────────────────────────┘
```

### Базовая настройка NSPersistentContainer

```swift
import CoreData

// MARK: - Singleton Core Data Stack
class PersistenceController {
    static let shared = PersistenceController()

    // Preview для SwiftUI Canvas
    static var preview: PersistenceController = {
        let controller = PersistenceController(inMemory: true)
        let context = controller.container.viewContext

        // Создаем тестовые данные
        for i in 0..<10 {
            let item = Item(context: context)
            item.timestamp = Date()
            item.title = "Item \(i)"
        }

        do {
            try context.save()
        } catch {
            let nsError = error as NSError
            fatalError("Preview error: \(nsError), \(nsError.userInfo)")
        }

        return controller
    }()

    let container: NSPersistentContainer

    // In-memory для тестов, SQLite для продакшена
    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "MyAppModel")

        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }

        container.loadPersistentStores { description, error in
            if let error = error {
                // В продакшене: логировать и обрабатывать gracefully
                fatalError("Core Data store failed to load: \(error.localizedDescription)")
            }
        }

        // Автоматическое слияние изменений из родительского контекста
        container.viewContext.automaticallyMergesChangesFromParent = true

        // Объекты становятся временными после удаления
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }

    // Сохранение с обработкой ошибок
    func save() {
        let context = container.viewContext

        if context.hasChanges {
            do {
                try context.save()
            } catch {
                let nsError = error as NSError
                print("Core Data save error: \(nsError), \(nsError.userInfo)")
                // В продакшене: показать alert или retry логику
            }
        }
    }
}
```

## NSManagedObject и дизайн сущностей

### Создание Data Model (.xcdatamodeld)

1. **File → New → Data Model** в Xcode
2. Добавляем Entity → создаем атрибуты и relationships
3. Editor → Create NSManagedObject Subclass

### Пример модели данных

```
┌─────────────────────┐         ┌─────────────────────┐
│      Author         │         │       Book          │
├─────────────────────┤         ├─────────────────────┤
│ name: String        │◄───────►│ title: String       │
│ birthDate: Date     │ books   │ publishedDate: Date │
│ country: String     │ author  │ isbn: String        │
└─────────────────────┘         │ pageCount: Int16    │
                                └─────────────────────┘
                                         │
                                         │ tags
                                         │ (many-to-many)
                                         ▼
                                ┌─────────────────────┐
                                │       Tag           │
                                ├─────────────────────┤
                                │ name: String        │
                                │ color: String       │
                                └─────────────────────┘
```

### NSManagedObject Subclass (Swift 6)

```swift
import Foundation
import CoreData

@objc(Book)
public class Book: NSManagedObject, Identifiable {
    @NSManaged public var id: UUID
    @NSManaged public var title: String
    @NSManaged public var publishedDate: Date
    @NSManaged public var isbn: String?
    @NSManaged public var pageCount: Int16
    @NSManaged public var createdAt: Date
    @NSManaged public var updatedAt: Date

    // Relationships
    @NSManaged public var author: Author?
    @NSManaged public var tags: Set<Tag>?

    // Computed properties
    public var formattedPublishDate: String {
        publishedDate.formatted(date: .abbreviated, time: .omitted)
    }

    public var isLongBook: Bool {
        pageCount > 500
    }
}

// MARK: - Lifecycle Methods
extension Book {
    public override func awakeFromInsert() {
        super.awakeFromInsert()
        setPrimitiveValue(Date(), forKey: "createdAt")
        setPrimitiveValue(Date(), forKey: "updatedAt")
        setPrimitiveValue(UUID(), forKey: "id")
    }

    public override func willSave() {
        super.willSave()
        setPrimitiveValue(Date(), forKey: "updatedAt")
    }
}

// MARK: - Fetch Requests
extension Book {
    @nonobjc public class func fetchRequest() -> NSFetchRequest<Book> {
        return NSFetchRequest<Book>(entityName: "Book")
    }

    static func booksByAuthor(_ author: Author) -> NSFetchRequest<Book> {
        let request = fetchRequest()
        request.predicate = NSPredicate(format: "author == %@", author)
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Book.publishedDate, ascending: false)]
        return request
    }

    static func recentBooks(limit: Int = 10) -> NSFetchRequest<Book> {
        let request = fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Book.createdAt, ascending: false)]
        request.fetchLimit = limit
        return request
    }
}
```

### Валидация данных

```swift
extension Book {
    public override func validateForInsert() throws {
        try super.validateForInsert()
        try validateTitle()
        try validatePageCount()
    }

    public override func validateForUpdate() throws {
        try super.validateForUpdate()
        try validateTitle()
        try validatePageCount()
    }

    private func validateTitle() throws {
        guard !title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw ValidationError.emptyTitle
        }

        guard title.count <= 200 else {
            throw ValidationError.titleTooLong
        }
    }

    private func validatePageCount() throws {
        guard pageCount > 0 else {
            throw ValidationError.invalidPageCount
        }
    }
}

enum ValidationError: LocalizedError {
    case emptyTitle
    case titleTooLong
    case invalidPageCount

    var errorDescription: String? {
        switch self {
        case .emptyTitle: return "Book title cannot be empty"
        case .titleTooLong: return "Book title must be less than 200 characters"
        case .invalidPageCount: return "Page count must be greater than 0"
        }
    }
}
```

## Relationships: связи между сущностями

### One-to-Many (Один ко многим)

```swift
// Author (1) ←──→ (N) Books
// Delete Rule: Cascade (при удалении автора удаляются его книги)

@objc(Author)
public class Author: NSManagedObject {
    @NSManaged public var name: String
    @NSManaged public var birthDate: Date
    @NSManaged public var books: Set<Book>?

    // Type-safe helpers
    public var booksArray: [Book] {
        let set = books ?? []
        return set.sorted { $0.publishedDate > $1.publishedDate }
    }

    public func addBook(_ book: Book) {
        var currentBooks = books ?? []
        currentBooks.insert(book)
        books = currentBooks
        book.author = self
    }

    public func removeBook(_ book: Book) {
        books?.remove(book)
        book.author = nil
    }
}

// Использование
let context = PersistenceController.shared.container.viewContext

let author = Author(context: context)
author.name = "Isaac Asimov"
author.birthDate = DateComponents(calendar: .current, year: 1920, month: 1, day: 2).date!

let book1 = Book(context: context)
book1.title = "Foundation"
book1.publishedDate = DateComponents(calendar: .current, year: 1951).date!
book1.pageCount = 255

let book2 = Book(context: context)
book2.title = "I, Robot"
book2.publishedDate = DateComponents(calendar: .current, year: 1950).date!
book2.pageCount = 224

author.addBook(book1)
author.addBook(book2)

try? context.save()
```

### Many-to-Many (Многие ко многим)

```swift
// Book (N) ←──→ (N) Tag
// Delete Rule: Nullify (при удалении тега, книги остаются)

@objc(Tag)
public class Tag: NSManagedObject {
    @NSManaged public var name: String
    @NSManaged public var color: String
    @NSManaged public var books: Set<Book>?

    public var booksArray: [Book] {
        let set = books ?? []
        return set.sorted { $0.title < $1.title }
    }
}

extension Book {
    public func addTag(_ tag: Tag) {
        var currentTags = tags ?? []
        currentTags.insert(tag)
        tags = currentTags

        var tagBooks = tag.books ?? []
        tagBooks.insert(self)
        tag.books = tagBooks
    }

    public func removeTag(_ tag: Tag) {
        tags?.remove(tag)
        tag.books?.remove(self)
    }

    public var tagsArray: [Tag] {
        let set = tags ?? []
        return set.sorted { $0.name < $1.name }
    }
}

// Использование
let sciFiTag = Tag(context: context)
sciFiTag.name = "Sci-Fi"
sciFiTag.color = "#3498db"

let classicTag = Tag(context: context)
classicTag.name = "Classic"
classicTag.color = "#e74c3c"

book1.addTag(sciFiTag)
book1.addTag(classicTag)
book2.addTag(sciFiTag)

try? context.save()
```

### Delete Rules

```
Cascade   → При удалении источника удаляются все связанные объекты
Nullify   → При удалении источника связь обнуляется (default)
Deny      → Запрещает удаление если есть связанные объекты
No Action → Не делает ничего (опасно, может нарушить целостность)

Example:
Author --[Cascade]--> Books  (удалил автора → удалились книги)
Book   --[Nullify]--> Tags   (удалил книгу → теги остались)
```

## Fetch Requests: запросы данных

### NSFetchRequest с NSPredicate

```swift
import CoreData

// MARK: - Базовый fetch request
func fetchAllBooks(context: NSManagedObjectContext) -> [Book] {
    let request = Book.fetchRequest()
    request.sortDescriptors = [NSSortDescriptor(keyPath: \Book.title, ascending: true)]

    do {
        return try context.fetch(request)
    } catch {
        print("Fetch failed: \(error)")
        return []
    }
}

// MARK: - Filtering с NSPredicate
func fetchBooksByAuthorName(_ name: String, context: NSManagedObjectContext) -> [Book] {
    let request = Book.fetchRequest()

    // Используем keyPath для type-safety
    request.predicate = NSPredicate(format: "%K == %@",
                                   #keyPath(Book.author.name), name)
    request.sortDescriptors = [NSSortDescriptor(keyPath: \Book.publishedDate, ascending: false)]

    return (try? context.fetch(request)) ?? []
}

// MARK: - Compound predicates
func fetchSciFiBooksAfter2000(context: NSManagedObjectContext) -> [Book] {
    let request = Book.fetchRequest()

    let yearPredicate = NSPredicate(format: "%K > %@",
                                   #keyPath(Book.publishedDate),
                                   DateComponents(calendar: .current, year: 2000, month: 1, day: 1).date! as NSDate)

    let tagPredicate = NSPredicate(format: "ANY %K.name == %@",
                                  #keyPath(Book.tags),
                                  "Sci-Fi")

    request.predicate = NSCompoundPredicate(andPredicateWithSubpredicates: [
        yearPredicate,
        tagPredicate
    ])

    return (try? context.fetch(request)) ?? []
}

// MARK: - Aggregate functions
func countBooksByAuthor(_ author: Author, context: NSManagedObjectContext) -> Int {
    let request = Book.fetchRequest()
    request.predicate = NSPredicate(format: "author == %@", author)

    return (try? context.count(for: request)) ?? 0
}

// MARK: - Property fetching (оптимизация)
func fetchBookTitlesOnly(context: NSManagedObjectContext) -> [String] {
    let request = Book.fetchRequest()
    request.resultType = .dictionaryResultType
    request.propertiesToFetch = ["title"]
    request.returnsDistinctResults = true

    guard let results = try? context.fetch(request) as? [[String: Any]] else {
        return []
    }

    return results.compactMap { $0["title"] as? String }
}

// MARK: - Batch size для больших результатов
func fetchBooksInBatches(context: NSManagedObjectContext) -> [Book] {
    let request = Book.fetchRequest()
    request.fetchBatchSize = 20 // Загружаем по 20 объектов
    request.sortDescriptors = [NSSortDescriptor(keyPath: \Book.title, ascending: true)]

    return (try? context.fetch(request)) ?? []
}
```

### Расширенные NSPredicate примеры

```swift
// MARK: - Строковые операции
// BEGINSWITH, ENDSWITH, CONTAINS, LIKE, MATCHES

// Case-insensitive поиск
let searchPredicate = NSPredicate(format: "title CONTAINS[cd] %@", "foundation")

// Wildcard паттерн
let wildcardPredicate = NSPredicate(format: "title LIKE %@", "*Robot*")

// Regex
let regexPredicate = NSPredicate(format: "isbn MATCHES %@", "\\d{3}-\\d{10}")

// MARK: - Диапазоны
let rangePredicate = NSPredicate(format: "pageCount BETWEEN %@", [100, 500])

// MARK: - Collections
let authorsPredicate = NSPredicate(format: "author.name IN %@",
                                  ["Isaac Asimov", "Arthur C. Clarke", "Robert Heinlein"])

// ANY для to-many relationships
let hasTagPredicate = NSPredicate(format: "ANY tags.name == %@", "Sci-Fi")

// ALL для всех элементов
let allTagsPredicate = NSPredicate(format: "ALL tags.color == %@", "#3498db")

// MARK: - Subqueries (подзапросы)
let subqueryPredicate = NSPredicate(
    format: "SUBQUERY(books, $book, $book.pageCount > 300).@count > 5"
)
// Авторы, у которых более 5 книг длиннее 300 страниц

// MARK: - Функции агрегации
let avgPredicate = NSPredicate(format: "books.@avg.pageCount > 400")
let sumPredicate = NSPredicate(format: "books.@sum.pageCount > 2000")
let minPredicate = NSPredicate(format: "books.@min.publishedDate < %@", someDate as NSDate)
```

## @FetchRequest в SwiftUI

### Базовое использование

```swift
import SwiftUI
import CoreData

struct BookListView: View {
    @Environment(\.managedObjectContext) private var viewContext

    // Автоматическое обновление при изменениях
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \Book.title, ascending: true)],
        animation: .default
    )
    private var books: FetchedResults<Book>

    var body: some View {
        NavigationStack {
            List {
                ForEach(books) { book in
                    BookRow(book: book)
                }
                .onDelete(perform: deleteBooks)
            }
            .navigationTitle("Books")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button(action: addBook) {
                        Label("Add Book", systemImage: "plus")
                    }
                }
            }
        }
    }

    private func addBook() {
        withAnimation {
            let newBook = Book(context: viewContext)
            newBook.title = "New Book"
            newBook.publishedDate = Date()
            newBook.pageCount = 0

            try? viewContext.save()
        }
    }

    private func deleteBooks(offsets: IndexSet) {
        withAnimation {
            offsets.map { books[$0] }.forEach(viewContext.delete)
            try? viewContext.save()
        }
    }
}

struct BookRow: View {
    @ObservedObject var book: Book

    var body: some View {
        VStack(alignment: .leading) {
            Text(book.title)
                .font(.headline)

            if let author = book.author {
                Text(author.name)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Text(book.formattedPublishDate)
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
    }
}
```

### Динамические @FetchRequest

```swift
struct FilteredBookListView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @State private var searchText = ""
    @State private var filterTag: Tag?

    var body: some View {
        FilteredBookList(searchText: searchText, filterTag: filterTag)
            .searchable(text: $searchText, prompt: "Search books")
    }
}

struct FilteredBookList: View {
    @FetchRequest private var books: FetchedResults<Book>

    init(searchText: String, filterTag: Tag?) {
        var predicates: [NSPredicate] = []

        if !searchText.isEmpty {
            predicates.append(
                NSPredicate(format: "title CONTAINS[cd] %@", searchText)
            )
        }

        if let tag = filterTag {
            predicates.append(
                NSPredicate(format: "ANY tags == %@", tag)
            )
        }

        let compoundPredicate = predicates.isEmpty ? nil :
            NSCompoundPredicate(andPredicateWithSubpredicates: predicates)

        _books = FetchRequest(
            sortDescriptors: [NSSortDescriptor(keyPath: \Book.title, ascending: true)],
            predicate: compoundPredicate,
            animation: .default
        )
    }

    var body: some View {
        List(books) { book in
            BookRow(book: book)
        }
    }
}
```

### @SectionedFetchRequest (группировка)

```swift
import SwiftUI
import CoreData

struct GroupedBooksView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @SectionedFetchRequest<String, Book>(
        sectionIdentifier: \.author?.name ?? "Unknown",
        sortDescriptors: [
            SortDescriptor(\.author?.name, order: .forward),
            SortDescriptor(\.title, order: .forward)
        ],
        animation: .default
    )
    private var booksByAuthor: SectionedFetchResults<String, Book>

    var body: some View {
        List {
            ForEach(booksByAuthor) { section in
                Section(header: Text(section.id)) {
                    ForEach(section) { book in
                        BookRow(book: book)
                    }
                }
            }
        }
        .navigationTitle("Books by Author")
    }
}
```

## Background Context и многопоточность

### Правила конкурентности

```
ЗОЛОТОЕ ПРАВИЛО:
┌──────────────────────────────────────────────────┐
│ Один NSManagedObjectContext = Один поток/очередь │
│ НИКОГДА не передавайте NSManagedObject между      │
│ контекстами напрямую!                             │
└──────────────────────────────────────────────────┘

Правильно: передавать ObjectID
Неправильно: передавать NSManagedObject
```

### performBackgroundTask для разовых операций

```swift
import CoreData

// MARK: - Разовая фоновая операция
func importBooksInBackground(bookData: [[String: Any]]) {
    let container = PersistenceController.shared.container

    container.performBackgroundTask { backgroundContext in
        // Этот контекст работает на background queue
        backgroundContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy

        for data in bookData {
            let book = Book(context: backgroundContext)
            book.title = data["title"] as? String ?? ""
            book.pageCount = Int16(data["pageCount"] as? Int ?? 0)
            // ... заполнение данных
        }

        do {
            try backgroundContext.save()
            print("✅ Imported \(bookData.count) books")
        } catch {
            print("❌ Import failed: \(error)")
        }

        // Контекст автоматически уничтожается после завершения блока
    }
}
```

### newBackgroundContext для долгосрочных операций

```swift
// MARK: - Создание persistent background context
class BookSyncService {
    private let container: NSPersistentContainer
    private lazy var backgroundContext: NSManagedObjectContext = {
        let context = container.newBackgroundContext()
        context.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        context.automaticallyMergesChangesFromParent = true
        return context
    }()

    init(container: NSPersistentContainer) {
        self.container = container
    }

    func syncBooks(from api: [APIBook]) async throws {
        try await backgroundContext.perform {
            for apiBook in api {
                let request = Book.fetchRequest()
                request.predicate = NSPredicate(format: "isbn == %@", apiBook.isbn)

                let existingBook = try? self.backgroundContext.fetch(request).first
                let book = existingBook ?? Book(context: self.backgroundContext)

                book.title = apiBook.title
                book.isbn = apiBook.isbn
                book.pageCount = Int16(apiBook.pageCount)
                // ... обновление данных
            }

            try self.backgroundContext.save()
        }
    }
}
```

### Child Context Pattern

```swift
// MARK: - Parent-Child Context для временных изменений
class BookEditorViewModel: ObservableObject {
    let book: Book
    private let parentContext: NSManagedObjectContext

    // Дочерний контекст для редактирования
    private(set) lazy var editContext: NSManagedObjectContext = {
        let context = NSManagedObjectContext(concurrencyType: .mainQueueConcurrencyType)
        context.parent = parentContext
        return context
    }()

    // Книга в дочернем контексте
    private(set) lazy var editableBook: Book = {
        editContext.object(with: book.objectID) as! Book
    }()

    init(book: Book, context: NSManagedObjectContext) {
        self.book = book
        self.parentContext = context
    }

    // Сохранить изменения → пробросить в родительский контекст
    func save() throws {
        guard editContext.hasChanges else { return }

        try editContext.save()

        // Теперь сохраняем родительский контекст
        if parentContext.hasChanges {
            try parentContext.save()
        }
    }

    // Отменить все изменения
    func cancel() {
        editContext.rollback()
    }
}

// Использование в SwiftUI
struct BookEditorView: View {
    @StateObject private var viewModel: BookEditorViewModel
    @Environment(\.dismiss) private var dismiss

    init(book: Book, context: NSManagedObjectContext) {
        _viewModel = StateObject(wrappedValue: BookEditorViewModel(book: book, context: context))
    }

    var body: some View {
        Form {
            TextField("Title", text: $viewModel.editableBook.title)
            // ... другие поля
        }
        .navigationTitle("Edit Book")
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Cancel") {
                    viewModel.cancel()
                    dismiss()
                }
            }

            ToolbarItem(placement: .confirmationAction) {
                Button("Save") {
                    try? viewModel.save()
                    dismiss()
                }
            }
        }
    }
}
```

### Notification-based синхронизация

```swift
import Combine

class CoreDataObserver {
    private var cancellables = Set<AnyCancellable>()
    private let viewContext: NSManagedObjectContext

    init(context: NSManagedObjectContext) {
        self.viewContext = context
        observeContextChanges()
    }

    private func observeContextChanges() {
        // Слушаем изменения из других контекстов
        NotificationCenter.default.publisher(
            for: .NSManagedObjectContextDidSave,
            object: nil
        )
        .sink { [weak self] notification in
            guard let self = self,
                  let context = notification.object as? NSManagedObjectContext,
                  context !== self.viewContext,
                  context.persistentStoreCoordinator == self.viewContext.persistentStoreCoordinator
            else { return }

            // Мержим изменения в главный контекст
            self.viewContext.perform {
                self.viewContext.mergeChanges(fromContextDidSave: notification)
            }
        }
        .store(in: &cancellables)
    }
}
```

## Миграции: Lightweight vs Heavyweight

### Lightweight Migration (автоматическая)

```swift
// Поддерживаемые изменения:
// ✅ Добавление нового атрибута с default значением
// ✅ Удаление атрибута
// ✅ Переименование атрибута (с Renaming ID)
// ✅ Изменение опциональности атрибута
// ✅ Добавление/удаление relationship
// ✅ Добавление/удаление entity
// ✅ Изменение hierarchy (добавление parent entity)

// Включение lightweight migration
let container = NSPersistentContainer(name: "MyAppModel")

let description = container.persistentStoreDescriptions.first
description?.shouldMigrateStoreAutomatically = true
description?.shouldInferMappingModelAutomatically = true

container.loadPersistentStores { description, error in
    if let error = error {
        fatalError("Failed to load Core Data: \(error)")
    }
}
```

### Versioning моделей

```
1. Editor → Add Model Version (в .xcdatamodeld)
2. Создается MyAppModel v2.xcdatamodel
3. Делаем изменения в v2
4. Выбираем v2 как Current Model Version (Inspector panel)

MyAppModel.xcdatamodeld/
├── MyAppModel.xcdatamodel         ← v1
├── MyAppModel v2.xcdatamodel      ← v2 (current)
└── .xccurrentversion              ← указывает на текущую версию
```

### Heavyweight Migration (кастомная)

```swift
import CoreData

// MARK: - Mapping Model для сложных миграций
// Создать: File → New → Mapping Model

// Пример: миграция полного имени → firstName + lastName

// 1. Создаем NSEntityMigrationPolicy subclass
class AuthorMigrationPolicy: NSEntityMigrationPolicy {
    override func createDestinationInstances(
        forSource sInstance: NSManagedObject,
        in mapping: NSEntityMapping,
        manager: NSMigrationManager
    ) throws {
        try super.createDestinationInstances(forSource: sInstance, in: mapping, manager: manager)

        guard let destinationInstances = manager.destinationInstances(
            forEntityMappingName: mapping.name,
            sourceInstances: [sInstance]
        ).first else { return }

        // Разделяем fullName на firstName и lastName
        if let fullName = sInstance.value(forKey: "fullName") as? String {
            let components = fullName.split(separator: " ", maxSplits: 1)

            destinationInstances.setValue(String(components.first ?? ""), forKey: "firstName")
            destinationInstances.setValue(
                components.count > 1 ? String(components[1]) : "",
                forKey: "lastName"
            )
        }
    }
}

// 2. В Mapping Model указываем Custom Policy: AuthorMigrationPolicy

// 3. Прогрессивная миграция (v1 → v2 → v3)
class MigrationManager {
    static func migrateStoreIfNeeded(at storeURL: URL, to model: NSManagedObjectModel) throws {
        let metadata = try NSPersistentStoreCoordinator.metadataForPersistentStore(
            ofType: NSSQLiteStoreType,
            at: storeURL
        )

        guard !model.isConfiguration(withName: nil, compatibleWithStoreMetadata: metadata) else {
            print("✅ Store is already compatible")
            return
        }

        print("⚠️ Migration needed")

        // Находим цепочку миграций v1 → v2 → v3
        let migrationSteps = try findMigrationSteps(from: metadata, to: model)

        for step in migrationSteps {
            try performMigration(step: step, at: storeURL)
        }
    }

    private static func performMigration(step: MigrationStep, at storeURL: URL) throws {
        let manager = NSMigrationManager(sourceModel: step.sourceModel, destinationModel: step.destinationModel)

        let tempURL = storeURL.deletingLastPathComponent()
            .appendingPathComponent("migration_temp.sqlite")

        try manager.migrateStore(
            from: storeURL,
            sourceType: NSSQLiteStoreType,
            options: nil,
            with: step.mappingModel,
            toDestinationURL: tempURL,
            destinationType: NSSQLiteStoreType,
            destinationOptions: nil
        )

        // Заменяем старый store новым
        let fileManager = FileManager.default
        try fileManager.removeItem(at: storeURL)
        try fileManager.moveItem(at: tempURL, to: storeURL)

        print("✅ Migration step completed")
    }
}

struct MigrationStep {
    let sourceModel: NSManagedObjectModel
    let destinationModel: NSManagedObjectModel
    let mappingModel: NSMappingModel
}
```

## Core Data + CloudKit синхронизация

### NSPersistentCloudKitContainer

```swift
import CoreData
import CloudKit

class CloudPersistenceController {
    static let shared = CloudPersistenceController()

    let container: NSPersistentCloudKitContainer

    init() {
        container = NSPersistentCloudKitContainer(name: "MyAppModel")

        guard let description = container.persistentStoreDescriptions.first else {
            fatalError("No store description found")
        }

        // Включаем CloudKit синхронизацию
        description.cloudKitContainerOptions = NSPersistentCloudKitContainerOptions(
            containerIdentifier: "iCloud.com.yourcompany.yourapp"
        )

        // History tracking обязателен для CloudKit
        description.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)
        description.setOption(true as NSNumber, forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)

        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("CloudKit setup failed: \(error)")
            }
        }

        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy

        observeCloudKitChanges()
    }

    private func observeCloudKitChanges() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleRemoteChange),
            name: .NSPersistentStoreRemoteChange,
            object: container.persistentStoreCoordinator
        )
    }

    @objc private func handleRemoteChange(_ notification: Notification) {
        print("☁️ CloudKit remote change received")
        // Автоматически мержится благодаря automaticallyMergesChangesFromParent
    }
}
```

### CloudKit Configuration в Data Model

```
1. Выбираем Entity → Inspector → Cloud Kit
2. Включаем "Use for CloudKit"
3. Настраиваем:
   - Recordable: YES (синхронизируется с CloudKit)
   - Zone: Private (private database) / Shared (shared database)

⚠️ Ограничения:
- Ordered relationships НЕ поддерживаются
- Transformable атрибуты должны использовать NSSecureUnarchiveFromDataTransformer
- Abstract entities не синхронизируются
```

### Sharing с CloudKit (iOS 15+)

```swift
import SwiftUI
import CoreData

struct BookDetailView: View {
    @ObservedObject var book: Book
    @Environment(\.managedObjectContext) private var viewContext

    @State private var showShareSheet = false

    var body: some View {
        VStack {
            Text(book.title)
                .font(.title)

            Button("Share Book") {
                showShareSheet = true
            }
        }
        .sheet(isPresented: $showShareSheet) {
            CloudSharingView(book: book)
        }
    }
}

struct CloudSharingView: UIViewControllerRepresentable {
    let book: Book

    func makeUIViewController(context: Context) -> UICloudSharingController {
        let container = PersistenceController.shared.container
        let share = CKShare(rootRecord: book.objectID)

        share[CKShare.SystemFieldKey.title] = book.title as CKRecordValue

        let controller = UICloudSharingController(
            share: share,
            container: container.persistentStoreCoordinator.cloudKitContainer!
        )

        controller.delegate = context.coordinator
        return controller
    }

    func updateUIViewController(_ uiViewController: UICloudSharingController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    class Coordinator: NSObject, UICloudSharingControllerDelegate {
        func cloudSharingController(
            _ csc: UICloudSharingController,
            failedToSaveShareWithError error: Error
        ) {
            print("❌ Failed to share: \(error)")
        }

        func itemTitle(for csc: UICloudSharingController) -> String? {
            "Share Book"
        }
    }
}
```

## Оптимизация производительности

### Batch Operations

```swift
import CoreData

// MARK: - Batch Insert (iOS 13+)
func batchInsertBooks(_ books: [[String: Any]], context: NSManagedObjectContext) {
    let batchInsert = NSBatchInsertRequest(entityName: "Book") { (managedObject: NSManagedObject) -> Bool in
        guard let book = books.first else { return true }

        managedObject.setValue(book["title"], forKey: "title")
        managedObject.setValue(book["pageCount"], forKey: "pageCount")
        managedObject.setValue(Date(), forKey: "createdAt")
        managedObject.setValue(UUID(), forKey: "id")

        books.removeFirst()
        return books.isEmpty
    }

    do {
        try context.execute(batchInsert)
    } catch {
        print("❌ Batch insert failed: \(error)")
    }
}

// MARK: - Batch Update
func batchUpdateOldBooks(context: NSManagedObjectContext) {
    let batchUpdate = NSBatchUpdateRequest(entityName: "Book")
    batchUpdate.predicate = NSPredicate(format: "publishedDate < %@",
                                       DateComponents(calendar: .current, year: 1950).date! as NSDate)
    batchUpdate.propertiesToUpdate = ["isClassic": true]
    batchUpdate.resultType = .updatedObjectIDsResultType

    do {
        let result = try context.execute(batchUpdate) as? NSBatchUpdateResult
        let objectIDs = result?.result as? [NSManagedObjectID] ?? []

        // Обновляем объекты в памяти
        let changes = [NSUpdatedObjectsKey: objectIDs]
        NSManagedObjectContext.mergeChanges(fromRemoteContextSave: changes, into: [context])

        print("✅ Updated \(objectIDs.count) books")
    } catch {
        print("❌ Batch update failed: \(error)")
    }
}

// MARK: - Batch Delete
func batchDeleteOldBooks(context: NSManagedObjectContext) {
    let fetchRequest = Book.fetchRequest()
    fetchRequest.predicate = NSPredicate(format: "createdAt < %@",
                                        Calendar.current.date(byAdding: .year, value: -5, to: Date())! as NSDate)

    let batchDelete = NSBatchDeleteRequest(fetchRequest: fetchRequest as! NSFetchRequest<NSFetchRequestResult>)
    batchDelete.resultType = .resultTypeObjectIDs

    do {
        let result = try context.execute(batchDelete) as? NSBatchDeleteResult
        let objectIDs = result?.result as? [NSManagedObjectID] ?? []

        // Мержим удаления в контекст
        let changes = [NSDeletedObjectsKey: objectIDs]
        NSManagedObjectContext.mergeChanges(fromRemoteContextSave: changes, into: [context])

        print("✅ Deleted \(objectIDs.count) old books")
    } catch {
        print("❌ Batch delete failed: \(error)")
    }
}
```

### Faulting и Prefetching

```swift
// MARK: - Faulting (ленивая загрузка)
/*
Fault = "заглушка" объекта, данные не загружены из SQLite
При обращении к атрибуту → автоматический fetch из базы

┌──────────────────┐
│ Book (Fault)     │  ← Только ObjectID в памяти
├──────────────────┤
│ id: UUID         │
│ title: <fault>   │  ← Не загружено
│ author: <fault>  │  ← Не загружено
└──────────────────┘

После book.title:
┌──────────────────┐
│ Book (Realized)  │  ← Полный объект в памяти
├──────────────────┤
│ id: UUID         │
│ title: "Foundation"  ← Загружено из SQLite
│ author: <fault>      ← Relationship все еще fault
└──────────────────┘
*/

// MARK: - Prefetching для оптимизации relationships
func fetchBooksWithAuthors(context: NSManagedObjectContext) -> [Book] {
    let request = Book.fetchRequest()
    request.sortDescriptors = [NSSortDescriptor(keyPath: \Book.title, ascending: true)]

    // Загружаем author сразу, избегая N+1 проблемы
    request.relationshipKeyPathsForPrefetching = ["author", "tags"]

    return (try? context.fetch(request)) ?? []
}

// БЕЗ prefetching (N+1 query):
// SELECT * FROM Book                      -- 1 запрос
// SELECT * FROM Author WHERE id = ?       -- 100 запросов (для каждой книги)
// Итого: 101 SQL запрос

// С prefetching:
// SELECT * FROM Book                      -- 1 запрос
// SELECT * FROM Author WHERE id IN (...)  -- 1 запрос
// Итого: 2 SQL запроса

// MARK: - Returning Objects as Faults
func fetchBookIDsOnly(context: NSManagedObjectContext) -> [Book] {
    let request = Book.fetchRequest()
    request.returnsObjectsAsFaults = true  // Не загружаем атрибуты сразу
    request.propertiesToFetch = []

    return (try? context.fetch(request)) ?? []
}
```

### NSFetchedResultsController (UIKit)

```swift
import UIKit
import CoreData

class BooksTableViewController: UITableViewController {
    private let context: NSManagedObjectContext
    private lazy var fetchedResultsController: NSFetchedResultsController<Book> = {
        let request = Book.fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(keyPath: \Book.author?.name, ascending: true),
            NSSortDescriptor(keyPath: \Book.title, ascending: true)
        ]
        request.fetchBatchSize = 20

        let controller = NSFetchedResultsController(
            fetchRequest: request,
            managedObjectContext: context,
            sectionNameKeyPath: #keyPath(Book.author.name),  // Секции по автору
            cacheName: "BooksCache"
        )

        controller.delegate = self
        return controller
    }()

    init(context: NSManagedObjectContext) {
        self.context = context
        super.init(style: .plain)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()

        do {
            try fetchedResultsController.performFetch()
        } catch {
            print("Fetch failed: \(error)")
        }
    }

    // MARK: - Table View Data Source
    override func numberOfSections(in tableView: UITableView) -> Int {
        fetchedResultsController.sections?.count ?? 0
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        fetchedResultsController.sections?[section].numberOfObjects ?? 0
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "BookCell", for: indexPath)
        let book = fetchedResultsController.object(at: indexPath)

        var config = cell.defaultContentConfiguration()
        config.text = book.title
        config.secondaryText = book.author?.name
        cell.contentConfiguration = config

        return cell
    }

    override func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        fetchedResultsController.sections?[section].name
    }
}

// MARK: - NSFetchedResultsControllerDelegate
extension BooksTableViewController: NSFetchedResultsControllerDelegate {
    func controllerWillChangeContent(_ controller: NSFetchedResultsController<NSFetchRequestResult>) {
        tableView.beginUpdates()
    }

    func controller(
        _ controller: NSFetchedResultsController<NSFetchRequestResult>,
        didChange anObject: Any,
        at indexPath: IndexPath?,
        for type: NSFetchedResultsChangeType,
        newIndexPath: IndexPath?
    ) {
        switch type {
        case .insert:
            tableView.insertRows(at: [newIndexPath!], with: .automatic)
        case .delete:
            tableView.deleteRows(at: [indexPath!], with: .automatic)
        case .update:
            tableView.reloadRows(at: [indexPath!], with: .automatic)
        case .move:
            tableView.deleteRows(at: [indexPath!], with: .automatic)
            tableView.insertRows(at: [newIndexPath!], with: .automatic)
        @unknown default:
            break
        }
    }

    func controllerDidChangeContent(_ controller: NSFetchedResultsController<NSFetchRequestResult>) {
        tableView.endUpdates()
    }
}
```

## Отладка и диагностика

### SQL Debug Logging

```swift
// В схеме запуска Xcode:
// Edit Scheme → Run → Arguments → Arguments Passed On Launch

// Уровень 1: Базовый SQL
-com.apple.CoreData.SQLDebug 1

// Уровень 2: Детальный SQL с параметрами
-com.apple.CoreData.SQLDebug 2

// Уровень 3: Полный trace с binding values
-com.apple.CoreData.SQLDebug 3

// Вывод в консоль:
/*
CoreData: sql: SELECT 0, t0.Z_PK, t0.Z_OPT, t0.ZTITLE, t0.ZPAGECOUNT, t0.ZAUTHOR
FROM ZBOOK t0
WHERE  t0.ZTITLE LIKE ?
ORDER BY t0.ZTITLE
CoreData: annotation: sql connection fetch time: 0.0012s
CoreData: annotation: total fetch execution time: 0.0025s for 15 rows.
*/
```

### Core Data Instruments

```
Xcode → Product → Profile → выбираем:

1. Core Data (общий профиль)
   - Fetches: количество и время fetch запросов
   - Saves: количество сохранений
   - Faults: сколько faults было fired
   - Cache Misses: промахи row cache

2. Time Profiler
   - Находим горячие точки в Core Data коде
   - -[NSManagedObjectContext save:]
   - -[NSPersistentStoreCoordinator executeRequest:]

3. Allocations
   - NSManagedObject instances
   - Утечки памяти в relationships
   - Retain cycles через contexts
```

### Persistent History Tracking

```swift
// Включаем history tracking
let description = container.persistentStoreDescriptions.first
description?.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)

// Читаем историю изменений
func fetchPersistentHistory(since date: Date, context: NSManagedObjectContext) throws {
    let historyRequest = NSPersistentHistoryChangeRequest.fetchHistory(after: date)

    guard let historyResult = try context.execute(historyRequest) as? NSPersistentHistoryResult,
          let transactions = historyResult.result as? [NSPersistentHistoryTransaction]
    else { return }

    for transaction in transactions {
        print("📝 Transaction by \(transaction.author ?? "unknown") at \(transaction.timestamp)")

        for change in transaction.changes ?? [] {
            switch change.changeType {
            case .insert:
                print("  ➕ Inserted: \(change.changedObjectID)")
            case .update:
                print("  ✏️ Updated: \(change.changedObjectID)")
            case .delete:
                print("  🗑️ Deleted: \(change.changedObjectID)")
            @unknown default:
                break
            }
        }
    }

    // Очистка старой истории (performance)
    let purgeRequest = NSPersistentHistoryChangeRequest.deleteHistory(before: date)
    try context.execute(purgeRequest)
}
```

### Validating Data Model

```swift
// MARK: - Проверка целостности модели при старте
func validateDataModel() throws {
    let modelURL = Bundle.main.url(forResource: "MyAppModel", withExtension: "momd")!
    let model = NSManagedObjectModel(contentsOf: modelURL)!

    // Проверяем все entities
    for entity in model.entities {
        print("✅ Entity: \(entity.name ?? "unknown")")

        // Проверяем атрибуты
        for (name, attribute) in entity.attributesByName {
            guard let type = attribute.attributeType else { continue }
            print("  - \(name): \(type)")

            if attribute.isOptional && attribute.defaultValue != nil {
                print("    ⚠️ Optional with default value - возможна ошибка")
            }
        }

        // Проверяем relationships
        for (name, relationship) in entity.relationshipsByName {
            print("  → \(name) to \(relationship.destinationEntity?.name ?? "?")")

            if let inverse = relationship.inverseRelationship {
                print("    ← inverse: \(inverse.name)")
            } else {
                print("    ⚠️ No inverse relationship - может привести к ошибкам")
            }
        }
    }
}
```

## 6 критических ошибок

### ❌ Ошибка 1: Передача NSManagedObject между потоками

```swift
// ❌ НЕПРАВИЛЬНО: передаем объект напрямую
func updateBookInBackground(book: Book) {
    DispatchQueue.global().async {
        book.title = "Updated Title"  // ☠️ CRASH! Context не привязан к этому потоку
    }
}

// ✅ ПРАВИЛЬНО: передаем ObjectID
func updateBookInBackground(bookID: NSManagedObjectID) {
    let container = PersistenceController.shared.container

    container.performBackgroundTask { backgroundContext in
        guard let book = try? backgroundContext.existingObject(with: bookID) as? Book else {
            return
        }

        book.title = "Updated Title"
        try? backgroundContext.save()
    }
}

// Использование:
let bookID = book.objectID
updateBookInBackground(bookID: bookID)
```

### ❌ Ошибка 2: Забыли inverse relationship

```swift
// ❌ НЕПРАВИЛЬНО: односторонняя связь
/*
Data Model:
Book.author → Author (no inverse)

Проблемы:
- Core Data не может поддерживать целостность
- При удалении Author книги останутся с dangling reference
- Фоновая синхронизация может сломаться
*/

// ✅ ПРАВИЛЬНО: двусторонняя связь
/*
Data Model:
Book.author ←→ Author.books

Author.books inverse: book.author
Book.author inverse: author.books
Delete Rule: Cascade (автор) / Nullify (книга)
*/

// В коде это прозрачно работает:
let author = Author(context: context)
let book = Book(context: context)

book.author = author
// Core Data автоматически делает: author.books.insert(book)

author.removeFromBooks(book)
// Core Data автоматически делает: book.author = nil
```

### ❌ Ошибка 3: Не используем batch operations для больших объемов

```swift
// ❌ НЕПРАВИЛЬНО: загружаем все в память
func deleteAllOldBooks(context: NSManagedObjectContext) {
    let request = Book.fetchRequest()
    request.predicate = NSPredicate(format: "createdAt < %@", someOldDate as NSDate)

    let books = try? context.fetch(request)  // Загрузили 10,000 объектов в память

    books?.forEach { context.delete($0) }  // Медленно, много памяти
    try? context.save()
}

// ✅ ПРАВИЛЬНО: используем NSBatchDeleteRequest
func deleteAllOldBooksEfficiently(context: NSManagedObjectContext) {
    let fetchRequest = Book.fetchRequest()
    fetchRequest.predicate = NSPredicate(format: "createdAt < %@", someOldDate as NSDate)

    let batchDelete = NSBatchDeleteRequest(
        fetchRequest: fetchRequest as! NSFetchRequest<NSFetchRequestResult>
    )
    batchDelete.resultType = .resultTypeObjectIDs

    do {
        let result = try context.execute(batchDelete) as? NSBatchDeleteResult
        let objectIDs = result?.result as? [NSManagedObjectID] ?? []

        // Обновляем контекст
        let changes = [NSDeletedObjectsKey: objectIDs]
        NSManagedObjectContext.mergeChanges(fromRemoteContextSave: changes, into: [context])

        print("✅ Deleted \(objectIDs.count) books efficiently")
    } catch {
        print("❌ Batch delete failed: \(error)")
    }
}

// Производительность:
// ❌ Старый способ: 10,000 объектов = ~5-10 секунд, 100+ MB памяти
// ✅ Batch delete: 10,000 объектов = ~0.5 секунд, <10 MB памяти
```

### ❌ Ошибка 4: Сохранение на каждое изменение

```swift
// ❌ НЕПРАВИЛЬНО: сохраняем в цикле
func importBooks(_ books: [APIBook], context: NSManagedObjectContext) {
    for apiBook in books {
        let book = Book(context: context)
        book.title = apiBook.title
        book.pageCount = Int16(apiBook.pageCount)

        try? context.save()  // ☠️ ОЧЕНЬ медленно!
    }
}

// SQLite fsync на каждое сохранение:
// 1000 книг × 10ms = 10 секунд

// ✅ ПРАВИЛЬНО: batch сохранение
func importBooksEfficiently(_ books: [APIBook], context: NSManagedObjectContext) {
    for apiBook in books {
        let book = Book(context: context)
        book.title = apiBook.title
        book.pageCount = Int16(apiBook.pageCount)
    }

    // Одно сохранение для всех изменений
    do {
        try context.save()
        print("✅ Imported \(books.count) books")
    } catch {
        print("❌ Import failed: \(error)")
    }
}

// 1000 книг × 0.01ms + 1 fsync × 10ms = 20ms
// Ускорение в 500 раз!

// ✅ ЕЩЕ ЛУЧШЕ: NSBatchInsertRequest (iOS 13+)
func importBooksSuperFast(_ books: [APIBook], context: NSManagedObjectContext) {
    var index = 0

    let batchInsert = NSBatchInsertRequest(
        entityName: "Book",
        dictionaryHandler: { dict in
            guard index < books.count else { return true }

            dict["title"] = books[index].title
            dict["pageCount"] = books[index].pageCount
            dict["id"] = UUID()
            dict["createdAt"] = Date()

            index += 1
            return false
        }
    )

    try? context.execute(batchInsert)
}
```

### ❌ Ошибка 5: Неправильная настройка @FetchRequest

```swift
// ❌ НЕПРАВИЛЬНО: без сортировки
struct BookListView: View {
    @FetchRequest(entity: Book.entity(), sortDescriptors: [])
    private var books: FetchedResults<Book>

    var body: some View {
        List(books) { book in  // ⚠️ Порядок случайный и нестабильный
            Text(book.title)
        }
    }
}

// ❌ НЕПРАВИЛЬНО: изменяемый predicate без reconstruction
struct SearchableBooksView: View {
    @FetchRequest(sortDescriptors: [SortDescriptor(\.title)])
    private var books: FetchedResults<Book>

    @State private var searchText = ""

    var filteredBooks: [Book] {
        if searchText.isEmpty {
            return Array(books)
        } else {
            return books.filter { $0.title.contains(searchText) }  // ❌ Фильтрация в памяти!
        }
    }

    var body: some View {
        List(filteredBooks) { book in
            Text(book.title)
        }
        .searchable(text: $searchText)
    }
}

// ✅ ПРАВИЛЬНО: стабильная сортировка
struct BookListView: View {
    @FetchRequest(
        sortDescriptors: [
            SortDescriptor(\.title, order: .forward),
            SortDescriptor(\.id, order: .forward)  // Для стабильности при одинаковых title
        ]
    )
    private var books: FetchedResults<Book>

    var body: some View {
        List(books) { book in
            Text(book.title)
        }
    }
}

// ✅ ПРАВИЛЬНО: динамический predicate через separate view
struct SearchableBooksView: View {
    @State private var searchText = ""

    var body: some View {
        BookList(searchText: searchText)
            .searchable(text: $searchText)
    }
}

struct BookList: View {
    let searchText: String

    @FetchRequest private var books: FetchedResults<Book>

    init(searchText: String) {
        let predicate = searchText.isEmpty ? nil :
            NSPredicate(format: "title CONTAINS[cd] %@", searchText)

        _books = FetchRequest(
            sortDescriptors: [SortDescriptor(\.title)],
            predicate: predicate
        )
    }

    var body: some View {
        List(books) { book in
            Text(book.title)
        }
    }
}
```

### ❌ Ошибка 6: Retain cycles через closures

```swift
// ❌ НЕПРАВИЛЬНО: strong reference cycle
class BookViewModel: ObservableObject {
    @Published var books: [Book] = []
    private let context: NSManagedObjectContext

    init(context: NSManagedObjectContext) {
        self.context = context
        observeChanges()
    }

    private func observeChanges() {
        NotificationCenter.default.addObserver(
            forName: .NSManagedObjectContextDidSave,
            object: context,
            queue: .main
        ) { notification in
            self.fetchBooks()  // ☠️ Strong capture of self → memory leak
        }
    }

    private func fetchBooks() {
        let request = Book.fetchRequest()
        books = (try? context.fetch(request)) ?? []
    }
}

// ✅ ПРАВИЛЬНО: weak self
class BookViewModel: ObservableObject {
    @Published var books: [Book] = []
    private let context: NSManagedObjectContext
    private var observer: NSObjectProtocol?

    init(context: NSManagedObjectContext) {
        self.context = context
        observeChanges()
    }

    deinit {
        if let observer = observer {
            NotificationCenter.default.removeObserver(observer)
        }
    }

    private func observeChanges() {
        observer = NotificationCenter.default.addObserver(
            forName: .NSManagedObjectContextDidSave,
            object: context,
            queue: .main
        ) { [weak self] notification in
            self?.fetchBooks()  // ✅ Weak capture
        }
    }

    private func fetchBooks() {
        let request = Book.fetchRequest()
        books = (try? context.fetch(request)) ?? []
    }
}

// ✅ ЕЩЕ ЛУЧШЕ: Combine publisher
import Combine

class BookViewModel: ObservableObject {
    @Published var books: [Book] = []
    private let context: NSManagedObjectContext
    private var cancellables = Set<AnyCancellable>()

    init(context: NSManagedObjectContext) {
        self.context = context
        observeChanges()
    }

    private func observeChanges() {
        NotificationCenter.default.publisher(for: .NSManagedObjectContextDidSave, object: context)
            .sink { [weak self] _ in
                self?.fetchBooks()
            }
            .store(in: &cancellables)
    }

    private func fetchBooks() {
        let request = Book.fetchRequest()
        books = (try? context.fetch(request)) ?? []
    }
}
```

## Когда использовать Core Data vs альтернативы

### Decision Tree

```
Нужна персистентность данных?
├─ Простой key-value store?
│  └─ ✅ UserDefaults / Keychain
│
├─ Сложная объектная модель с relationships?
│  ├─ Нужна синхронизация с iCloud?
│  │  └─ ✅ Core Data + CloudKit
│  │
│  ├─ Много связей, граф объектов, undo/redo?
│  │  └─ ✅ Core Data (NSPersistentContainer)
│  │
│  └─ Простая структура, но нужен SQL контроль?
│     └─ ⚠️ SQLite.swift / GRDB.swift
│
├─ Только iOS 17+, простая модель?
│  └─ ✅ SwiftData (новый API поверх Core Data)
│
├─ Реактивные данные, real-time sync?
│  └─ ✅ Realm / Firebase Firestore
│
└─ Документо-ориентированная БД?
   └─ ⚠️ Couchbase Lite
```

### Сравнение: Core Data vs Room (Android)

См. также: [[database-design-optimization]]

```
┌─────────────────────┬──────────────────────┬──────────────────────┐
│ Аспект              │ Core Data (iOS)      │ Room (Android)       │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Архитектура         │ Object Graph         │ ORM над SQLite       │
│                     │ + Persistence        │                      │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Схема данных        │ .xcdatamodeld        │ @Entity annotations  │
│                     │ (visual editor)      │ (code-first)         │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Query язык          │ NSPredicate          │ SQL (@Query)         │
│                     │ (строковый DSL)      │ (compile-time check) │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Relationships       │ Automatic            │ Manual @Relation     │
│                     │ (inverse tracking)   │ (explicit joins)     │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Ленивая загрузка    │ Faulting             │ @Ignore + lazy load  │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Миграции            │ Lightweight +        │ Migration classes    │
│                     │ Mapping Models       │ (explicit SQL)       │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Потоки/корутины     │ NSManagedObject      │ Suspend functions    │
│                     │ Context per thread   │ + Flow<List<T>>      │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ UI Integration      │ @FetchRequest        │ LiveData / Flow      │
│                     │ (SwiftUI native)     │ (observable)         │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Cloud Sync          │ NSPersistentCloud    │ Firebase / Custom    │
│                     │ KitContainer (iCloud)│ (third-party)        │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Batch Operations    │ NSBatchInsert/       │ @Insert @Update      │
│                     │ Update/Delete        │ (list-based)         │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Type Safety         │ Runtime (NSPredicate)│ Compile-time (@Query)│
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Learning Curve      │ Средний-высокий      │ Низкий-средний       │
│                     │ (концепция графа)    │ (знакомый SQL)       │
└─────────────────────┴──────────────────────┴──────────────────────┘
```

### Code Comparison: CRUD операции

```swift
// ========================================
// CORE DATA (iOS)
// ========================================

// CREATE
let book = Book(context: context)
book.id = UUID()
book.title = "Foundation"
book.pageCount = 255
try? context.save()

// READ
let request = Book.fetchRequest()
request.predicate = NSPredicate(format: "pageCount > %d", 200)
request.sortDescriptors = [NSSortDescriptor(keyPath: \Book.title, ascending: true)]
let books = try? context.fetch(request)

// UPDATE
book.title = "Foundation (Updated)"
try? context.save()

// DELETE
context.delete(book)
try? context.save()

// RELATIONSHIPS
let author = Author(context: context)
author.name = "Isaac Asimov"
book.author = author  // Автоматически: author.books.insert(book)
try? context.save()

// ========================================
// ROOM (Android/Kotlin)
// ========================================

// Entities
@Entity(tableName = "books")
data class Book(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val title: String,
    val pageCount: Int,
    val authorId: String?
)

@Entity(tableName = "authors")
data class Author(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val name: String
)

// Relationship (manual join)
data class BookWithAuthor(
    @Embedded val book: Book,
    @Relation(
        parentColumn = "authorId",
        entityColumn = "id"
    )
    val author: Author?
)

// DAO (Data Access Object)
@Dao
interface BookDao {
    // CREATE
    @Insert
    suspend fun insert(book: Book)

    // READ
    @Query("SELECT * FROM books WHERE pageCount > :minPages ORDER BY title ASC")
    fun getBooksWithMinPages(minPages: Int): Flow<List<Book>>

    // UPDATE
    @Update
    suspend fun update(book: Book)

    // DELETE
    @Delete
    suspend fun delete(book: Book)

    // RELATIONSHIPS
    @Transaction
    @Query("SELECT * FROM books")
    fun getBooksWithAuthors(): Flow<List<BookWithAuthor>>
}

// Usage
val book = Book(title = "Foundation", pageCount = 255, authorId = author.id)
bookDao.insert(book)

// Observe changes (like @FetchRequest)
bookDao.getBooksWithMinPages(200).collect { books ->
    // Update UI
}
```

### Рекомендации выбора

**Выбирай Core Data если:**
- Сложный граф объектов с многими relationships
- Нужна автоматическая синхронизация с iCloud
- Важны фичи: undo/redo, change tracking, validation
- Приложение только для Apple экосистемы
- Работаешь с большими объемами связанных данных

**Выбирай Room если:**
- Android-приложение или кросс-платформа (Flutter/React Native)
- Нужен строгий SQL контроль
- Команда знакома с SQL и ORM паттернами
- Требуется compile-time проверка запросов
- Простая структура данных без сложных relationships

**Выбирай SwiftData если:**
- iOS 17+ минимальная версия
- Нужен современный Swift-first API
- Работаешь только со SwiftUI
- Хочешь макросы Swift вместо .xcdatamodeld

**Выбирай Realm если:**
- Нужна real-time sync между устройствами
- Кросс-платформенное приложение (iOS/Android)
- Mobile-first БД с offline-first подходом
- Очень быстрые запросы критичны

## Полный пример: BookStore App

```swift
// MARK: - Models
import CoreData

@objc(Book)
public class Book: NSManagedObject, Identifiable {
    @NSManaged public var id: UUID
    @NSManaged public var title: String
    @NSManaged public var isbn: String?
    @NSManaged public var pageCount: Int16
    @NSManaged public var publishedDate: Date
    @NSManaged public var createdAt: Date
    @NSManaged public var updatedAt: Date

    @NSManaged public var author: Author?
    @NSManaged public var tags: Set<Tag>?

    public override func awakeFromInsert() {
        super.awakeFromInsert()
        id = UUID()
        createdAt = Date()
        updatedAt = Date()
    }

    public override func willSave() {
        super.willSave()
        updatedAt = Date()
    }
}

@objc(Author)
public class Author: NSManagedObject, Identifiable {
    @NSManaged public var id: UUID
    @NSManaged public var name: String
    @NSManaged public var birthDate: Date
    @NSManaged public var books: Set<Book>?

    public var booksArray: [Book] {
        (books ?? []).sorted { $0.title < $1.title }
    }
}

@objc(Tag)
public class Tag: NSManagedObject, Identifiable {
    @NSManaged public var name: String
    @NSManaged public var color: String
    @NSManaged public var books: Set<Book>?
}

// MARK: - SwiftUI App
import SwiftUI

@main
struct BookStoreApp: App {
    let persistenceController = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}

struct ContentView: View {
    @Environment(\.managedObjectContext) private var viewContext

    var body: some View {
        TabView {
            BookListView()
                .tabItem {
                    Label("Books", systemImage: "book")
                }

            AuthorListView()
                .tabItem {
                    Label("Authors", systemImage: "person.2")
                }
        }
    }
}

// MARK: - Book List View
struct BookListView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @State private var searchText = ""

    var body: some View {
        NavigationStack {
            FilteredBookList(searchText: searchText)
                .navigationTitle("Books")
                .searchable(text: $searchText)
                .toolbar {
                    ToolbarItem(placement: .primaryAction) {
                        NavigationLink {
                            AddBookView()
                        } label: {
                            Label("Add", systemImage: "plus")
                        }
                    }
                }
        }
    }
}

struct FilteredBookList: View {
    @Environment(\.managedObjectContext) private var viewContext
    @FetchRequest private var books: FetchedResults<Book>

    init(searchText: String) {
        let predicate = searchText.isEmpty ? nil :
            NSPredicate(format: "title CONTAINS[cd] %@ OR author.name CONTAINS[cd] %@",
                       searchText, searchText)

        _books = FetchRequest(
            sortDescriptors: [
                SortDescriptor(\.title, order: .forward)
            ],
            predicate: predicate,
            animation: .default
        )
    }

    var body: some View {
        List {
            ForEach(books) { book in
                NavigationLink {
                    BookDetailView(book: book)
                } label: {
                    BookRowView(book: book)
                }
            }
            .onDelete(perform: deleteBooks)
        }
    }

    private func deleteBooks(at offsets: IndexSet) {
        withAnimation {
            offsets.map { books[$0] }.forEach(viewContext.delete)
            try? viewContext.save()
        }
    }
}

struct BookRowView: View {
    @ObservedObject var book: Book

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(book.title)
                .font(.headline)

            if let author = book.author {
                Text(author.name)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            HStack {
                Text("\(book.pageCount) pages")
                    .font(.caption)

                Spacer()

                Text(book.publishedDate.formatted(date: .abbreviated, time: .omitted))
                    .font(.caption)
            }
            .foregroundStyle(.tertiary)
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Add Book View
struct AddBookView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss

    @State private var title = ""
    @State private var pageCount = ""
    @State private var selectedAuthor: Author?

    @FetchRequest(
        sortDescriptors: [SortDescriptor(\.name)],
        animation: .default
    )
    private var authors: FetchedResults<Author>

    var body: some View {
        Form {
            Section("Book Details") {
                TextField("Title", text: $title)
                TextField("Page Count", text: $pageCount)
                    .keyboardType(.numberPad)
            }

            Section("Author") {
                Picker("Select Author", selection: $selectedAuthor) {
                    Text("None").tag(nil as Author?)
                    ForEach(authors) { author in
                        Text(author.name).tag(author as Author?)
                    }
                }
            }
        }
        .navigationTitle("Add Book")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Cancel") {
                    dismiss()
                }
            }

            ToolbarItem(placement: .confirmationAction) {
                Button("Save") {
                    saveBook()
                }
                .disabled(title.isEmpty || pageCount.isEmpty)
            }
        }
    }

    private func saveBook() {
        let book = Book(context: viewContext)
        book.title = title
        book.pageCount = Int16(pageCount) ?? 0
        book.publishedDate = Date()
        book.author = selectedAuthor

        try? viewContext.save()
        dismiss()
    }
}
```

## Дополнительные ресурсы

### Apple Documentation
- [Core Data Programming Guide](https://developer.apple.com/documentation/coredata)
- [NSPersistentContainer](https://developer.apple.com/documentation/coredata/nspersistentcontainer)
- [Using Core Data with CloudKit](https://developer.apple.com/documentation/coredata/mirroring_a_core_data_store_with_cloudkit)

### WWDC Sessions
- WWDC 2023: "What's new in Core Data"
- WWDC 2019: "Using Core Data with CloudKit"
- WWDC 2020: "Sync a Core Data store with the CloudKit public database"

### Open Source примеры
- [Core Data example by Apple](https://developer.apple.com/documentation/coredata/loading_and_displaying_a_large_data_feed)

---

*Последнее обновление: 2026-01-11*

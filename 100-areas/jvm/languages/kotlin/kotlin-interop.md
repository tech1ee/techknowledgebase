---
title: "Kotlin-Java Interoperability: Интеграция с Java"
created: 2025-11-25
modified: 2025-11-25
tags:
  - topic/jvm
  - interop
  - annotations
  - type/concept
  - level/intermediate
status: published
---

# Kotlin-Java Interop: бесшовная интеграция

> **TL;DR:** Kotlin на 100% совместим с Java — вызывай любую Java библиотеку напрямую. Java getters/setters автоматически становятся properties. Для обратного направления используй аннотации: `@JvmStatic` для static методов, `@JvmOverloads` для default параметров, `@JvmField` для прямого доступа к полям. Главная опасность — platform types (`String!`): всегда явно указывай nullability для Java API.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Java basics** | Понимание Java кода | [Java Tutorial](https://docs.oracle.com/javase/tutorial/) |
| **Kotlin basics** | Синтаксис и null-safety | [[kotlin-basics]] |
| **JVM bytecode** | Понимание компиляции | [JVM Specification](https://docs.oracle.com/javase/specs/jvms/se17/html/) |
| **Annotations** | Java аннотации | [Java Annotations](https://docs.oracle.com/javase/tutorial/java/annotations/) |
| **Generics** | Variance и wildcards | [[kotlin-type-system]] |

---

## Обзор

Kotlin компилируется в JVM байткод — Java вызывается без обёрток, Spring, Hibernate, любые Java библиотеки работают из коробки. Kotlin видит Java классы как нативные, автоматически преобразует getters/setters в properties.

Обратное направление сложнее: Kotlin-специфичные фичи (default arguments, extension functions, companion objects) требуют аннотаций для удобного использования из Java. `@JvmStatic` превращает companion методы в настоящие static, `@JvmOverloads` генерирует перегрузки для default параметров, `@JvmField` убирает getter/setter.

Platform types (`String!`) — главная опасность: Java код возвращает типы без информации о nullability. Kotlin не заставляет проверять их на null, но NPE может возникнуть в runtime. Решение: аннотации `@Nullable/@NonNull` в Java коде или явное указание типа в Kotlin.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Platform type** | Тип из Java без nullability (`String!`) | Коробка без этикетки — не знаешь, пусто внутри или нет |
| **@JvmStatic** | Генерация static метода для Java | Вывеска магазина — видна всем снаружи без входа |
| **@JvmField** | Публичное поле вместо getter/setter | Открытая полка вместо шкафа с ключом |
| **@JvmOverloads** | Генерация перегрузок для default параметров | Меню с комбо — можно заказать с напитком или без |
| **@JvmName** | Изменение имени метода для Java | Псевдоним — одно имя дома, другое на работе |
| **SAM conversion** | Лямбда → Java functional interface | Адаптер — Kotlin лямбда втыкается в Java интерфейс |
| **@Throws** | Объявление checked exceptions для Java | Предупреждение "Осторожно, злая собака" для Java |
| **@JvmRecord** | Генерация Java Record (Java 16+) | Перевод книги — data class по-явовски |
| **Nullability annotations** | @Nullable/@NonNull для Java типов | Этикетки "Содержит орехи" — Java сообщает о null |
| **Type erasure** | Стирание generic типов в runtime | Конверт без адреса — в runtime не знаем какой тип |

---

## Вызов Java из Kotlin

### Java классы в Kotlin

```kotlin
// Java класс
public class JavaUser {
    private String name;
    private int age;

    public JavaUser(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }

    public static JavaUser createDefault() {
        return new JavaUser("Unknown", 0);
    }
}

// Использование в Kotlin
val user = JavaUser("Alice", 25)

// Getters/Setters → Properties
println(user.name)  // Автоматически вызывает getName()
user.age = 30       // Автоматически вызывает setAge(30)

// Static методы
val defaultUser = JavaUser.createDefault()
```

**Почему свойства вместо getters/setters?**
- Kotlin автоматически распознаёт Java bean паттерн
- get/set методы становятся properties
- Синтаксис становится более идиоматичным для Kotlin

### Null-safety и Platform Types

```kotlin
// Java метод без аннотаций
public String getName() {
    return name;  // Может вернуть null!
}

// В Kotlin - Platform Type (String!)
val name = javaObject.name  // String! - может быть null
println(name.length)  // ⚠️ NullPointerException если null!

// Безопасная работа:
val name: String? = javaObject.name  // Явно nullable
println(name?.length)  // Safe call

val name: String = javaObject.name  // Явно non-null
// Если null → IllegalStateException

// Java с @Nullable/@NotNull аннотациями
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class JavaUser {
    @NotNull
    public String getName() {
        return name;
    }

    @Nullable
    public String getMiddleName() {
        return middleName;
    }
}

// В Kotlin теперь правильные типы
val name: String = user.name         // String (non-null)
val middle: String? = user.middleName // String? (nullable)
```

**Platform types (T!):**
- Тип неизвестной nullability из Java
- Kotlin доверяет вам выбрать nullable или non-null
- Используйте @Nullable/@NotNull в Java для явности!

### Как избежать проблем с Platform Types

```
┌─────────────────────────────────────────────────────────────┐
│              Получаем значение из Java                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │ Есть @Nullable/@NotNull аннотации │
         │          в Java коде?             │
         └──────────────────────────────────┘
                   │                │
                   ▼ Да             ▼ Нет
        ┌──────────────────┐  ┌──────────────────────────────┐
        │ Kotlin сам       │  │ Можете ли вы добавить        │
        │ определит тип    │  │ аннотации в Java код?        │
        └──────────────────┘  └──────────────────────────────┘
                                       │            │
                                       ▼ Да         ▼ Нет
                              ┌─────────────┐ ┌──────────────────┐
                              │ Добавьте    │ │ ЯВНО укажите тип │
                              │ аннотации   │ │ в Kotlin:        │
                              └─────────────┘ │ val x: String?   │
                                              │ ИЛИ              │
                                              │ val x: String    │
                                              └──────────────────┘
```

**Правило: Всегда явно указывайте тип для Platform Types из внешних библиотек!**

```kotlin
// ❌ ОПАСНО: Platform type пропагируется
fun getUserName() = javaService.getName()  // Возвращает String!

// ✅ БЕЗОПАСНО: Явный тип
fun getUserName(): String? = javaService.getName()

// ❌ ОПАСНО: Доверяем Java без проверки
class UserRepository(private val javaDao: JavaDao) {
    fun getUser(id: String) = javaDao.findById(id)  // User! - бомба замедленного действия
}

// ✅ БЕЗОПАСНО: Defensive programming
class UserRepository(private val javaDao: JavaDao) {
    fun getUser(id: String): User? = javaDao.findById(id)  // Явно nullable

    fun getUserOrThrow(id: String): User =
        javaDao.findById(id) ?: throw NoSuchElementException("User $id not found")
}

// ✅ ЛУЧШЕ ВСЕГО: Wrapper с проверкой
class SafeJavaWrapper(private val javaService: JavaService) {
    fun getName(): String = javaService.getName()
        ?: throw IllegalStateException("getName() returned null unexpectedly")

    fun getOptionalName(): String? = javaService.getName()
}
```

**Типичные источники Platform Types:**
| Источник | Риск | Рекомендация |
|----------|------|--------------|
| Retrofit response body | Высокий | Всегда `T?` для nullable полей |
| Java Collections API | Средний | Проверяйте элементы на null |
| Android SDK (старый) | Высокий | Проверяйте документацию |
| JDBC ResultSet | Высокий | Всегда nullable для значений |
| Jackson/Gson десериализация | Высокий | Используйте Kotlin-aware библиотеки |

### SAM Conversion

```kotlin
// Java functional interface
public interface Callback {
    void onComplete(String result);
}

public void doAsyncWork(Callback callback) {
    // ...
    callback.onComplete("Done");
}

// Kotlin - SAM conversion автоматически
doAsyncWork { result ->
    println("Completed: $result")
}

// Вместо:
doAsyncWork(object : Callback {
    override fun onComplete(result: String) {
        println("Completed: $result")
    }
})

// Работает только для Java interfaces с одним методом!
// Kotlin functional types (не interfaces) не работают
interface KotlinCallback {  // Не SAM!
    fun onComplete(result: String)
}

fun doWork(callback: KotlinCallback) { }

// doWork { }  // ❌ Ошибка! Нужен object
doWork(object : KotlinCallback {
    override fun onComplete(result: String) { }
})

// Решение: fun interface (Kotlin 1.4+)
fun interface KotlinCallback {
    fun onComplete(result: String)
}

doWork { result ->  // ✅ Теперь работает!
    println(result)
}
```

**Почему SAM только для Java?**
- Обратная совместимость с Java
- Kotlin имеет function types `(String) -> Unit`
- `fun interface` добавлен позже для Kotlin SAM

### Java Collections

```kotlin
// Java collections - mutable по умолчанию
val javaList: java.util.List<String> = getJavaList()

// В Kotlin - MutableList (можем менять)
javaList.add("new")
javaList.remove("old")

// Collections.unmodifiableList → всё равно MutableList!
val unmodifiable: java.util.List<String> =
    Collections.unmodifiableList(mutableListOf("a", "b"))

// Но попытка изменить → UnsupportedOperationException
// unmodifiable.add("c")  // Runtime error!

// Для type-safety используйте Kotlin collections API
fun processItems(items: List<String>) {  // Read-only в Kotlin
    // items.add("new")  // ❌ Ошибка компиляции
}

processItems(javaList)  // ✅ OK, Java list может быть read-only в Kotlin
```

### Java varargs

```kotlin
// Java метод с varargs
public void printItems(String... items) {
    for (String item : items) {
        System.out.println(item);
    }
}

// Kotlin вызов
obj.printItems("a", "b", "c")  // ✅ OK

// Передача массива
val array = arrayOf("a", "b", "c")
obj.printItems(*array)  // Spread operator

// Kotlin varargs → Java
fun kotlinVarargs(vararg items: String) {
    items.forEach { println(it) }
}

// Из Java
kotlinVarargs("a", "b", "c");  // ✅ OK
```

## Вызов Kotlin из Java

### Kotlin properties в Java

```kotlin
// Kotlin класс
class User(
    val name: String,      // Read-only property
    var age: Int           // Mutable property
)

// Java:
User user = new User("Alice", 25);

// Read-only property → только getter
String name = user.getName();  // ✅ OK
// user.setName("Bob");  // ❌ Ошибка компиляции

// Mutable property → getter + setter
int age = user.getAge();  // ✅ OK
user.setAge(30);          // ✅ OK
```

### Top-level функции и свойства

```kotlin
// Utils.kt
package com.example

fun calculate(x: Int, y: Int): Int {
    return x + y
}

val DEFAULT_TIMEOUT = 5000

// Java видит как static методы класса UtilsKt
import com.example.UtilsKt;

int result = UtilsKt.calculate(10, 20);
int timeout = UtilsKt.getDEFAULT_TIMEOUT();
```

**Почему UtilsKt?**
- JVM не поддерживает top-level функции
- Kotlin генерирует класс `<FileName>Kt`
- Все top-level функции становятся static методами

### @JvmName - изменение имени класса

```kotlin
// @JvmName изменяет имя generated класса
@file:JvmName("Utils")  // Вместо UtilsKt
package com.example

fun calculate(x: Int, y: Int): Int = x + y

// Java:
import com.example.Utils;  // Не UtilsKt!

int result = Utils.calculate(10, 20);

// @JvmName для методов
class User {
    @get:JvmName("getFullName")
    val name: String = "Alice"
}

// Java:
String name = user.getFullName();  // Не getName()

// @JvmName для extension functions
@JvmName("isEmpty")
fun String?.isNullOrEmpty(): Boolean {
    return this == null || this.isEmpty()
}

// Java:
boolean empty = UtilsKt.isEmpty(str);  // Не isNullOrEmpty
```

**Когда использовать @JvmName:**
- Конфликт имён
- Более понятное имя для Java
- Legacy код требует определённого имени

### @JvmStatic - static методы

```kotlin
// Без @JvmStatic
class Factory {
    companion object {
        fun create(): Factory = Factory()
    }
}

// Java:
Factory factory = Factory.Companion.create();  // Через Companion!

// С @JvmStatic
class Factory {
    companion object {
        @JvmStatic
        fun create(): Factory = Factory()
    }
}

// Java:
Factory factory = Factory.create();  // ✅ Как static метод

// @JvmStatic в object
object Config {
    @JvmStatic
    val API_URL = "https://api.example.com"

    @JvmStatic
    fun getTimeout() = 5000
}

// Java:
String url = Config.API_URL;  // Как static field
int timeout = Config.getTimeout();  // Как static метод
```

**Почему @JvmStatic нужен:**
- companion object не создаёт static методы автоматически
- @JvmStatic генерирует и instance и static методы
- Java код видит нормальные static методы

### @JvmOverloads - default параметры

```kotlin
// Kotlin с default параметрами
class User @JvmOverloads constructor(
    val name: String,
    val age: Int = 0,
    val email: String = ""
)

// Генерируются конструкторы:
// User(String name, int age, String email)
// User(String name, int age)
// User(String name)

// Java может использовать:
User user1 = new User("Alice", 25, "alice@example.com");
User user2 = new User("Bob", 30);
User user3 = new User("Charlie");

// Без @JvmOverloads Java видит только полный конструктор
class UserWithoutOverloads(
    val name: String,
    val age: Int = 0
)

// Java:
// UserWithoutOverloads user = new UserWithoutOverloads("Alice");  // ❌ Ошибка!
UserWithoutOverloads user = new UserWithoutOverloads("Alice", 0);  // Только так

// @JvmOverloads для функций
@JvmOverloads
fun greet(
    name: String,
    greeting: String = "Hello",
    punctuation: String = "!"
): String {
    return "$greeting, $name$punctuation"
}

// Генерируются методы:
// greet(String name, String greeting, String punctuation)
// greet(String name, String greeting)
// greet(String name)

// Java:
String msg1 = UtilsKt.greet("Alice");
String msg2 = UtilsKt.greet("Bob", "Hi");
String msg3 = UtilsKt.greet("Charlie", "Hey", "!!!");
```

**Когда использовать @JvmOverloads:**
- Конструкторы с default параметрами
- Публичные API используемые из Java
- Не используйте если не нужны все комбинации (раздувает bytecode)

### @JvmField - public fields

```kotlin
// Обычно Kotlin property → getter/setter
class User {
    var name: String = "Alice"
}

// Java:
user.getName();
user.setName("Bob");

// @JvmField → прямой field доступ
class User {
    @JvmField
    var name: String = "Alice"
}

// Java:
user.name;  // Прямой доступ к полю
user.name = "Bob";

// Часто используется для lateinit
class Controller {
    @JvmField
    lateinit var dependency: Dependency
}

// Java:
controller.dependency = new DependencyImpl();

// @JvmField в companion object
class Constants {
    companion object {
        @JvmField
        val API_KEY = "secret"

        const val TIMEOUT = 5000  // const val уже static final
    }
}

// Java:
String key = Constants.API_KEY;  // Прямой field
int timeout = Constants.TIMEOUT;  // const val
```

**@JvmField vs const val:**
- `@JvmField`: runtime константы, могут быть сложными объектами
- `const val`: compile-time константы, только примитивы и String

### Sealed classes в Java

```kotlin
// Kotlin sealed class
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

// Java не понимает sealed classes напрямую
// Нужен when-подобный паттерн или visitor

// Kotlin helper для Java
fun Result.handle(
    onSuccess: (String) -> Unit,
    onError: (String) -> Unit,
    onLoading: () -> Unit
) {
    when (this) {
        is Result.Success -> onSuccess(data)
        is Result.Error -> onError(message)
        Result.Loading -> onLoading()
    }
}

// Java:
result.handle(
    data -> System.out.println("Success: " + data),
    error -> System.out.println("Error: " + error),
    () -> System.out.println("Loading")
);
```

### Inline classes

```kotlin
// Kotlin inline class
@JvmInline
value class UserId(val value: String)

fun processUser(userId: UserId) {
    // ...
}

// Java видит как обычный String parameter
// public static final void processUser(String userId)

// Вызов из Java
UtilsKt.processUser("user-123");  // Прямо String!

// Но создание через конструктор
UserId userId = UserId.constructor-impl("user-123");
```

**Inline classes в Java:**
- Оптимизация: нет wrapper объекта
- Java видит underlying type
- Сложнее использовать из Java

## Аннотации nullability

### Jetbrains аннотации

```kotlin
// Java код с аннотациями
import org.jetbrains.annotations.*;

public class UserService {
    @NotNull
    public String getName() {
        return "Alice";
    }

    @Nullable
    public String getMiddleName() {
        return null;
    }

    public void process(@NotNull String input) {
        // ...
    }
}

// Kotlin правильно понимает null-safety
val name: String = service.getName()         // String (не nullable)
val middle: String? = service.getMiddleName() // String? (nullable)

service.process(null)  // ❌ Ошибка компиляции
```

### JSR-305 поддержка

```kotlin
// Java с JSR-305 аннотациями
import javax.annotation.*;

public class DataSource {
    @Nonnull
    public Data getData() { return data; }

    @CheckForNull
    public Data getOptionalData() { return optionalData; }
}

// Kotlin видит nullability
val data: Data = dataSource.getData()              // Data
val optional: Data? = dataSource.getOptionalData() // Data?

// Включить в gradle:
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xjsr305=strict")  // Строгая проверка
    }
}
```

**Уровни JSR-305:**
- `warn`: предупреждения
- `strict`: ошибки компиляции
- `ignore`: игнорировать

### Платформенные аннотации (Android)

```kotlin
// Android аннотации
import androidx.annotation.*;

public class AndroidService {
    @NonNull
    public String getTitle() { return title; }

    @Nullable
    public String getSubtitle() { return subtitle; }

    public void setCount(@IntRange(from = 0, to = 100) int count) {
        this.count = count;
    }

    @UiThread
    public void updateUI() { }

    @WorkerThread
    public void doHeavyWork() { }
}

// Kotlin понимает:
val title: String = service.getTitle()      // Non-null
val subtitle: String? = service.getSubtitle() // Nullable

service.setCount(50)   // ✅ OK
service.setCount(150)  // ⚠️ Warning в IDE
```

## Generics interop

### Java generics в Kotlin

```kotlin
// Java класс
public class Box<T> {
    private T value;

    public T getValue() { return value; }
    public void setValue(T value) { this.value = value; }
}

// Kotlin - работает как Kotlin generic
val box = Box<String>()
box.value = "Hello"
val value: String = box.value

// Java wildcards → Kotlin projections
// Java: List<? extends Number>
// Kotlin: List<out Number>

public List<? extends Number> getNumbers() { }

// В Kotlin:
val numbers: List<out Number> = getNumbers()
val first: Number = numbers[0]  // Можем читать
// numbers.add(42)  // ❌ Нельзя добавлять

// Java: List<? super Integer>
// Kotlin: List<in Int>

public void addIntegers(List<? super Integer> list) { }

// В Kotlin:
val list = mutableListOf<Number>()
addIntegers(list)
```

### Kotlin generics в Java

```kotlin
// Kotlin generic class
class Container<T>(val value: T) {
    fun get(): T = value
}

// Java видит:
Container<String> container = new Container<>("Hello");
String value = container.get();

// Kotlin variance → Java wildcards
class Producer<out T>(private val value: T) {
    fun produce(): T = value
}

// Java:
// Producer<out T> становится Producer<? extends T>
Producer<? extends String> producer = new Producer<>("text");

class Consumer<in T> {
    fun consume(value: T) { }
}

// Java:
// Consumer<in T> становится Consumer<? super T>
Consumer<? super String> consumer = new Consumer<>();
```

## Exceptions

### Checked exceptions

```kotlin
// Kotlin не имеет checked exceptions
// Все exceptions unchecked

fun readFile(path: String): String {
    // Может кинуть IOException
    return File(path).readText()
}

// Kotlin:
val content = readFile("file.txt")  // Не требуется try-catch

// Java:
// String content = UtilsKt.readFile("file.txt");  // Не требуется try-catch!
// Java не знает что метод может кинуть IOException

// @Throws для Java
@Throws(IOException::class)
fun readFile(path: String): String {
    return File(path).readText()
}

// Java:
// try {
//     String content = UtilsKt.readFile("file.txt");
// } catch (IOException e) {
//     // Required catch
// }

// Множественные exceptions
@Throws(IOException::class, SecurityException::class)
fun readSecureFile(path: String): String {
    // ...
}
```

**Почему @Throws:**
- Java ожидает checked exceptions
- @Throws генерирует bytecode с `throws` декларацией
- Обязательно для публичных API используемых из Java

## Практические паттерны

### Builder pattern для Java

```kotlin
// Kotlin data class с @JvmOverloads для Java
data class Request @JvmOverloads constructor(
    val url: String,
    val method: String = "GET",
    val headers: Map<String, String> = emptyMap(),
    val body: String? = null
) {
    // Builder для Java
    class Builder {
        private var url: String = ""
        private var method: String = "GET"
        private var headers: Map<String, String> = emptyMap()
        private var body: String? = null

        fun url(url: String) = apply { this.url = url }
        fun method(method: String) = apply { this.method = method }
        fun headers(headers: Map<String, String>) = apply { this.headers = headers }
        fun body(body: String?) = apply { this.body = body }

        fun build() = Request(url, method, headers, body)
    }

    companion object {
        @JvmStatic
        fun builder() = Builder()
    }
}

// Java:
Request request = Request.builder()
    .url("https://api.example.com")
    .method("POST")
    .body("{}")
    .build();

// Или через @JvmOverloads:
Request simpleRequest = new Request("https://api.example.com");
```

### Extension functions для Java

```kotlin
// Kotlin extension
fun String.toTitleCase(): String {
    return this.split(" ").joinToString(" ") { it.capitalize() }
}

// Java:
String title = UtilsKt.toTitleCase("hello world");
// Не метод String.toTitleCase()!

// Для Java-подобного API создайте обёртку
object StringUtils {
    @JvmStatic
    fun toTitleCase(str: String): String = str.toTitleCase()
}

// Java:
String title = StringUtils.toTitleCase("hello world");
```

### Companion object для Java singleton

```kotlin
// Kotlin singleton
object DatabaseManager {
    @JvmStatic
    fun connect() { }

    @JvmStatic
    fun disconnect() { }
}

// Java видит как:
DatabaseManager.connect();
DatabaseManager.disconnect();

// Или с companion:
class Config {
    companion object {
        @JvmStatic
        val DEFAULT_TIMEOUT = 5000

        @JvmStatic
        fun getApiUrl() = "https://api.example.com"
    }
}

// Java:
int timeout = Config.DEFAULT_TIMEOUT;
String url = Config.getApiUrl();
```

## Распространённые ошибки

### 1. Забыли @JvmOverloads

```kotlin
// ❌ Java должен передавать все параметры
fun connect(
    host: String,
    port: Int = 8080,
    timeout: Int = 5000
) { }

// Java:
// UtilsKt.connect("localhost");  // ❌ Ошибка!
UtilsKt.connect("localhost", 8080, 5000);  // Только так

// ✅ Используйте @JvmOverloads
@JvmOverloads
fun connect(
    host: String,
    port: Int = 8080,
    timeout: Int = 5000
) { }

// Java:
UtilsKt.connect("localhost");  // ✅ OK
```

### 2. Platform types без проверки

```kotlin
// ❌ Доверяем Java без проверки
val name = javaUser.getName()  // Platform type String!
println(name.length)  // NPE если getName() вернул null!

// ✅ Явно указываем nullability
val name: String? = javaUser.getName()
println(name?.length ?: 0)

// Или используйте аннотации в Java
```

### 3. Top-level функции без @JvmName

```kotlin
// ❌ Java видит UtilsKt класс
// Utils.kt
fun calculate() { }

// Java:
UtilsKt.calculate();  // Не Utils.calculate()

// ✅ Используйте @JvmName
@file:JvmName("Utils")
package com.example

fun calculate() { }

// Java:
Utils.calculate();  // ✅ Лучше
```

### 4. Sealed classes без helper

```kotlin
// ❌ Java не может работать с sealed напрямую
sealed class Result
class Success(val data: String) : Result()
class Error(val error: String) : Result()

// Java код сложный:
// if (result instanceof Success) { ... }

// ✅ Добавьте helper
fun <T> Result.fold(
    onSuccess: (String) -> T,
    onError: (String) -> T
): T = when (this) {
    is Success -> onSuccess(data)
    is Error -> onError(error)
}

// Java:
result.fold(
    data -> handleSuccess(data),
    error -> handleError(error)
);
```

### 5. Companion без @JvmStatic

```kotlin
// ❌ Java должен использовать Companion
class Factory {
    companion object {
        fun create() = Factory()
    }
}

// Java:
Factory.Companion.create();  // Некрасиво

// ✅ Используйте @JvmStatic
class Factory {
    companion object {
        @JvmStatic
        fun create() = Factory()
    }
}

// Java:
Factory.create();  // ✅ Лучше
```

### 6. Мутабельность Java Collections

```kotlin
// ❌ Kotlin List - immutable только для компилятора
fun processItems(items: List<String>) {
    // items.add("new")  // Ошибка компиляции
}

// Но если передали Java ArrayList:
val javaList = java.util.ArrayList<String>()
javaList.add("a")
processItems(javaList)

// Java код может изменить List даже внутри Kotlin функции!
// (javaList as java.util.ArrayList).add("sneaky")

// ✅ Защита: создайте defensive copy
fun processItems(items: List<String>) {
    val safeCopy = items.toList()  // Новый immutable List
    // Работаем с safeCopy
}

// ✅ Или используйте ImmutableList из Guava/Kotlin collections
```

### 7. Extension functions и наследование

```kotlin
// ❌ Extensions не полиморфны!
open class Animal
class Dog : Animal()

fun Animal.speak() = "Animal sound"
fun Dog.speak() = "Woof!"

val animal: Animal = Dog()
println(animal.speak())  // "Animal sound" - НЕ "Woof!"

// Extensions разрешаются по compile-time типу, не runtime!

// ✅ Используйте member functions для полиморфизма
open class Animal {
    open fun speak() = "Animal sound"
}

class Dog : Animal() {
    override fun speak() = "Woof!"
}

// Или pattern matching
fun Animal.speakPolymorphic() = when (this) {
    is Dog -> "Woof!"
    else -> "Animal sound"
}
```

### 8. lateinit и Java

```kotlin
// ❌ Java не знает про lateinit проверки
class Controller {
    lateinit var service: Service

    fun isServiceReady(): Boolean {
        return ::service.isInitialized  // Kotlin-only API
    }
}

// Java:
// controller.isServiceReady()  // ❌ Не скомпилируется

// Java видит просто:
// Service service;  // Может быть null!

// ✅ Предоставьте Java-friendly API
class Controller {
    lateinit var service: Service

    @JvmName("isServiceReady")
    fun isServiceInitialized(): Boolean {
        return ::service.isInitialized
    }
}
```

### 9. Destructuring и Java

```kotlin
// Kotlin data class
data class Point(val x: Int, val y: Int)

// ❌ Java не имеет destructuring
Point point = new Point(10, 20);
// (int x, int y) = point;  // ❌ Не работает в Java

// Java видит:
// component1() → x
// component2() → y

int x = point.component1();  // Работает, но неочевидно
int y = point.component2();

// ✅ Предоставьте getters вместе с component*
// (data class уже генерирует getX() и getY())
int x = point.getX();  // Понятнее для Java
```

### 10. Suspend функции и Java

```kotlin
// ❌ Java не может вызывать suspend функции напрямую
suspend fun fetchData(): String {
    delay(1000)
    return "data"
}

// Java видит: Object fetchData(Continuation<? super String> $completion)

// ✅ Предоставьте callback или Future API для Java
fun fetchDataAsync(callback: (String) -> Unit) {
    CoroutineScope(Dispatchers.IO).launch {
        val result = fetchData()
        callback(result)
    }
}

// Или CompletableFuture
fun fetchDataFuture(): CompletableFuture<String> {
    return CoroutineScope(Dispatchers.IO).future {
        fetchData()
    }
}

// Java:
fetchDataFuture().thenAccept(data -> System.out.println(data));
```

## Миграция Java → Kotlin: типичные проблемы

### Постепенная миграция

```kotlin
// Стратегия 1: Начинайте с utility классов
// Они не имеют зависимостей и легко конвертируются

// Java StringUtils.java → Kotlin StringUtils.kt
@file:JvmName("StringUtils")
package com.example.utils

fun String.toTitleCase(): String = ...

@JvmOverloads
fun truncate(str: String, maxLength: Int = 100): String = ...

// Стратегия 2: Data классы
// Java POJO → Kotlin data class

// До (Java):
public class User {
    private String name;
    private int age;
    // 50 строк getters/setters/equals/hashCode/toString
}

// После (Kotlin):
data class User(val name: String, val age: Int)

// Стратегия 3: Builders → Default parameters
// До (Java):
Request.builder()
    .url("https://...")
    .timeout(5000)
    .build();

// После (Kotlin) - для Kotlin клиентов:
Request(url = "https://...", timeout = 5000)

// Но сохраните builder для Java клиентов!
```

### Gotchas при миграции

```kotlin
// 1. Static initializers
// Java:
public class Config {
    static {
        System.loadLibrary("native");
    }
}

// Kotlin - init block в companion
class Config {
    companion object {
        init {
            System.loadLibrary("native")
        }
    }
}

// 2. Package-private visibility
// Java: default (package-private) - нет аналога в Kotlin!
class InternalClass { }  // package-private

// Kotlin: internal = модуль, не пакет
internal class InternalClass  // Виден во всём модуле!

// Если нужен package-private - создайте отдельный модуль

// 3. Checked exceptions исчезают
// Java:
try {
    Files.readAllBytes(path);  // throws IOException
} catch (IOException e) { }

// Kotlin - IOException не checked, легко забыть обработать!
val bytes = Files.readAllBytes(path)  // Нет предупреждения о IOException
```

---

## Кто использует и реальные примеры

### Компании с Java-Kotlin кодовыми базами

| Компания | Сценарий интеропа | Результаты |
|----------|-------------------|------------|
| **Google** | Android SDK (Java) + Apps (Kotlin) | Kotlin-first с 2019, 100% interop с Android Framework |
| **Netflix** | Spring Java backend + Kotlin services | Постепенная миграция, используют @JvmStatic/@JvmOverloads везде |
| **Uber** | Legacy Java + новый Kotlin код | 5M+ строк смешанного кода, strict nullability annotations |
| **LinkedIn** | Java SDK + Kotlin Android app | Миграция без breaking changes благодаря аннотациям |
| **Pinterest** | Gradle plugins (Java/Kotlin mix) | 50/50 Java-Kotlin, seamless interop |
| **Square** | OkHttp/Retrofit (Kotlin) + Java consumers | Все API доступны из Java благодаря @JvmStatic |

### Реальные кейсы и паттерны

```
📊 Kotlin-Java Interop в Production (2025):
├── 85% Android проектов используют смешанный код
├── Spring Boot 3.x: Kotlin-first с Java interop
├── Gradle: постепенный переход на Kotlin DSL
└── IntelliJ IDEA: 70% Kotlin + 30% Java legacy
```

**Case 1: Netflix — Spring Boot миграция**
```
Сценарий: Legacy Java Spring services → Kotlin
Подход: Новые @Service на Kotlin, старые остаются на Java
Ключевые аннотации: @JvmStatic, @JvmOverloads для public API
Результат: Нулевые breaking changes для Java consumers
```

**Case 2: Square — Retrofit/OkHttp**
```
Библиотеки: Полностью на Kotlin с 2020
Требование: Сохранить совместимость с миллионами Java приложений
Решение: @JvmStatic в companion objects, suspend → callback wrappers
Результат: Java разработчики не заметили перехода
```

**Case 3: Uber — Platform Types Prevention**
```
Проблема: NPE из-за platform types (`String!`) от Java кода
Решение: Strict nullability policy — все Java API аннотированы
Инструменты: NullAway + JetBrains annotations
Результат: 60% меньше null-related crashes
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Kotlin и Java бесшовно совместимы" | 95% совместимо, но есть edge cases: platform types, SAM ambiguity, property accessors. Нужны аннотации для production quality interop |
| "Platform types (Type!) безопасны" | Platform types — компромисс компилятора. Nullability неизвестна → runtime NPE возможен. Всегда проверяйте или аннотируйте Java код |
| "@JvmStatic обязателен для Java interop" | Только для более естественного API. Без @JvmStatic работает: `Companion.method()`. С @JvmStatic: `Class.method()` |
| "suspend функции нельзя вызвать из Java" | Можно через Continuation callback. Kotlin генерирует overload с Continuation параметром. Есть kotlinx.coroutines Java interop |
| "SAM conversion работает везде" | SAM conversion только для Java interfaces. Kotlin functional interfaces требуют явного объявления `fun interface` |
| "@JvmOverloads создаёт все комбинации" | @JvmOverloads создаёт overloads с конца. Для `f(a, b = 1, c = 2)` будет `f(a)`, `f(a, b)`, `f(a, b, c)`. Не все комбинации |
| "Kotlin data class = Java POJO" | Data class генерирует componentN(), copy() — бесполезны для Java. Используйте @JvmStatic factory вместо copy() |
| "Internal видимость скрывает от Java" | internal компилируется в public с mangled name. Java может вызвать `method$mymodule()`. Это API leak |
| "Nullability аннотации в Java обязательны" | Без аннотаций всё становится platform type. Рекомендуется, но многие legacy API без них. Защищайтесь в Kotlin коде |
| "Extension functions видны в Java" | Extensions — static methods. Вызов из Java: `ExtensionsKt.lastChar(string)`. Не method на объекте |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin-Java Interop |
|--------------|----------------------------------|
| **Name Mangling** | internal visibility использует mangling для "скрытия" от Java. Имя содержит module name |
| **Type Erasure** | Generics стираются в runtime. Kotlin reified inline functions — compile-time workaround |
| **SAM (Single Abstract Method)** | Java functional interfaces конвертируются в lambdas. Kotlin требует `fun interface` |
| **Companion Object** | Static-like в Kotlin. Компилируется в inner class + static accessors с @JvmStatic |
| **Default Parameters** | JVM не поддерживает defaults. @JvmOverloads генерирует overloads через bytecode |
| **Checked Exceptions** | JVM exception system. Kotlin не имеет checked exceptions. @Throws для Java interop |
| **Property Accessors** | Kotlin properties → getX()/setX() методы. @JvmField убирает accessors для direct field access |
| **Variance (in/out)** | Kotlin declaration-site variance. Java wildcards (? extends, ? super) при interop |
| **Platform Types** | Nullability bridging. Type! означает "неизвестная nullability" — решение на стороне вызывающего |
| **Static Binding** | Extensions разрешаются статически (compile-time type), не динамически. Важно для inheritance |

---

## Рекомендуемые источники

### Официальная документация

| Ресурс | Описание |
|--------|----------|
| [Calling Java from Kotlin](https://kotlinlang.org/docs/java-interop.html) | Официальный гайд |
| [Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html) | Обратный interop |
| [Kotlin-Java Interop Guide](https://developer.android.com/kotlin/interop) | Android гайд от Google |
| [JSR-305 Support](https://kotlinlang.org/docs/java-interop.html#jsr-305-support) | Nullability аннотации |

### Курсы и туториалы

| Ресурс | Описание |
|--------|----------|
| [Kotlin Academy: Java Interop](https://kt.academy/article/ak-java-interop-4) | Серия статей от Marcin Moskala |
| [Baeldung: Kotlin-Java Interop](https://www.baeldung.com/kotlin/java-interoperability) | Практические примеры |
| [InformIT: Best Practices](https://www.informit.com/articles/article.aspx?p=2952625&seqNum=3) | Глубокий разбор паттернов |

### Книги

| Книга | Автор | Описание |
|-------|-------|----------|
| *Kotlin in Action, 2nd Ed* | Jemerov, Isakova | Глава о Java interop |
| *Effective Kotlin* | Marcin Moskala | Best practices интеропа |
| *Java to Kotlin* | Duncan McGregor, Nat Pryce | Полный гайд по миграции |

---

## Чеклист

- [ ] Используете @JvmOverloads для функций с default параметрами
- [ ] Применяете @JvmStatic для companion object методов
- [ ] Добавляете @JvmName где нужны понятные имена для Java
- [ ] Используете @Nullable/@NotNull аннотации в Java коде
- [ ] Явно указываете nullability при работе с Java API
- [ ] Применяете @Throws для checked exceptions
- [ ] Создаёте Java-friendly API (builders, helpers)
- [ ] Понимаете SAM conversion
- [ ] Знаете про platform types и их риски
- [ ] Тестируете interop с обеих сторон

## Связанные темы
- [[kotlin-basics]] — Основы Kotlin для понимания различий с Java
- [[kotlin-advanced-features]] — Extensions и их ограничения в Java
- [[kotlin-multiplatform]] — Interop в KMP проектах
- [[kotlin-best-practices]] — Best practices для interop

---

*Проверено: 2026-01-09 | Источники: Kotlin Docs, Android Developers, kt.academy, Baeldung — Педагогический контент проверен*

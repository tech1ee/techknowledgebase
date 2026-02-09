---
title: "Reflection API: Интроспекция и динамическое поведение в Java"
created: 2025-11-25
modified: 2025-11-25
tags:
  - topic/jvm
  - reflection
  - introspection
  - dynamic-proxy
  - type/concept
  - level/advanced
type: concept
status: published
area: programming
confidence: high
sources:
  - "Java Language Specification: Chapter 12 - Execution (Reflection)"
  - "Effective Java" by Joshua Bloch (3rd Edition, 2018)
  - "Java Reflection in Action" by Ira R. Forman (2004)
  - Oracle Java Reflection Documentation
---

# Reflection API: Интроспекция и динамическое поведение в Java

> Reflection — способность программы исследовать и модифицировать свою структуру во время выполнения. Как Java "смотрит на себя в зеркало"?

---

## TL;DR

**Reflection API позволяет программе анализировать и изменять себя во время выполнения.**

Ключевые возможности:
- **Introspection** — получить информацию о классах, методах, полях
- **Dynamic invocation** — вызывать методы по строковому имени
- **Dynamic creation** — создавать объекты без `new`
- **Access modification** — обходить `private` через `setAccessible()`
- **Dynamic Proxies** — создавать классы на лету

Где используется:
- Frameworks (Spring, Hibernate)
- Serialization (JSON, XML)
- Testing (Mockito, JUnit)
- ORM, Dependency Injection

Компромиссы:
- ✅ Гибкость, динамическое поведение
- ❌ Медленно (10-100x медленнее прямого вызова)
- ❌ Нарушает инкапсуляцию
- ❌ Проблемы с безопасностью

---

## Что такое Reflection?

### Концепция

**Reflection (рефлексия) — способность программы исследовать свою структуру.**

```
Обычная программа:
  ┌─────────────┐
  │ Source Code │ → компилируется → выполняется
  └─────────────┘

Программа с Reflection:
  ┌─────────────┐
  │ Source Code │ → компилируется → выполняется
  └─────────────┘                        │
         ▲                               │
         │                               │
         └───────── может анализировать──┘
                    свою структуру
```

**Метафора:** Reflection = зеркало для программы.
- Обычный код: "Я делаю X"
- Reflection: "Кто я? Что у меня есть? Что я могу делать?"

---

### Проблема: Статическое связывание

**В Java всё статически типизировано:**

```java
User user = new User("Alice", 30);
String name = user.getName();  // Компилятор знает: getName() существует

// Что если имя метода приходит из конфига?
String methodName = config.get("getter");  // "getName"

// Нельзя написать: user.methodName()
// Компилятор не знает, что methodName = "getName"
```

**Без Reflection невозможно:**
- Вызвать метод по строковому имени
- Создать объект класса, имя которого в String
- Получить список методов класса
- Обойти `private` доступ

---

### Решение: Reflection API

```java
// 1. Получить Class объект
Class<?> clazz = Class.forName("com.example.User");

// 2. Создать instance без new
Object user = clazz.getDeclaredConstructor(String.class, int.class)
                   .newInstance("Alice", 30);

// 3. Получить метод по имени
Method method = clazz.getMethod("getName");

// 4. Вызвать метод динамически
String name = (String) method.invoke(user);

System.out.println(name);  // → "Alice"
```

**Всё работает динамически — компилятор не проверяет!**

---

## Class API: Получение метаданных класса

### Три способа получить Class объект

```java
public class User {
    private String name;
    private int age;

    public String getName() { return name; }
}
```

**1. Через .class литерал (compile-time)**

```java
Class<User> clazz = User.class;
// Тип известен статически: Class<User>
```

**2. Через getClass() на instance**

```java
User user = new User();
Class<?> clazz = user.getClass();
// Тип неизвестен: Class<?>
```

**3. Через Class.forName() по строковому имени**

```java
Class<?> clazz = Class.forName("com.example.User");
// Полностью динамически — имя может быть из конфига
```

---

### Class API: Ключевые методы

```java
Class<?> clazz = User.class;

// Имя класса
String simpleName = clazz.getSimpleName();        // "User"
String fullName = clazz.getName();                // "com.example.User"
String canonical = clazz.getCanonicalName();      // "com.example.User"

// Superclass и interfaces
Class<?> superclass = clazz.getSuperclass();      // Object.class
Class<?>[] interfaces = clazz.getInterfaces();    // []

// Modifiers
int modifiers = clazz.getModifiers();
boolean isPublic = Modifier.isPublic(modifiers);  // true
boolean isFinal = Modifier.isFinal(modifiers);    // false

// Package
Package pkg = clazz.getPackage();                 // com.example

// Annotations
Annotation[] annotations = clazz.getAnnotations();
```

---

## Introspection: Исследование структуры класса

### Получение полей (Fields)

```java
public class User {
    private String name;
    private int age;
    public static final String DEFAULT_NAME = "Unknown";
}

Class<?> clazz = User.class;

// getFields() — только public поля
Field[] publicFields = clazz.getFields();
// → [DEFAULT_NAME]

// getDeclaredFields() — ВСЕ поля (включая private)
Field[] allFields = clazz.getDeclaredFields();
// → [name, age, DEFAULT_NAME]

// Получить конкретное поле по имени
Field nameField = clazz.getDeclaredField("name");

// Метаданные поля
String fieldName = nameField.getName();           // "name"
Class<?> fieldType = nameField.getType();         // String.class
int modifiers = nameField.getModifiers();
boolean isPrivate = Modifier.isPrivate(modifiers); // true
```

---

### Получение методов (Methods)

```java
public class User {
    public String getName() { return name; }
    private void validateAge(int age) { ... }
    public static User create(String name) { ... }
}

Class<?> clazz = User.class;

// getMethods() — public методы (включая inherited)
Method[] publicMethods = clazz.getMethods();
// → [getName(), toString(), equals(), hashCode(), ...]

// getDeclaredMethods() — ВСЕ методы (только этого класса)
Method[] allMethods = clazz.getDeclaredMethods();
// → [getName(), validateAge(), create()]

// Получить конкретный метод
Method getNameMethod = clazz.getMethod("getName");

// Метаданные метода
String methodName = getNameMethod.getName();      // "getName"
Class<?> returnType = getNameMethod.getReturnType(); // String.class
Class<?>[] params = getNameMethod.getParameterTypes(); // []
int modifiers = getNameMethod.getModifiers();
boolean isPublic = Modifier.isPublic(modifiers);  // true
```

---

### Получение конструкторов (Constructors)

```java
public class User {
    public User() { }
    public User(String name) { this.name = name; }
    private User(String name, int age) { ... }
}

Class<?> clazz = User.class;

// getConstructors() — только public
Constructor<?>[] publicCtors = clazz.getConstructors();
// → [User(), User(String)]

// getDeclaredConstructors() — ВСЕ конструкторы
Constructor<?>[] allCtors = clazz.getDeclaredConstructors();
// → [User(), User(String), User(String, int)]

// Получить конкретный конструктор
Constructor<?> ctor = clazz.getConstructor(String.class);

// Метаданные
Class<?>[] params = ctor.getParameterTypes();     // [String.class]
```

---

## Dynamic Invocation: Вызовы во время выполнения

### Создание объектов через Reflection

```java
Class<?> clazz = User.class;

// 1. Через конструктор без параметров (deprecated в Java 9+)
User user1 = (User) clazz.newInstance();  // Устарело!

// 2. Через Constructor.newInstance() (правильный способ)
Constructor<?> ctor = clazz.getConstructor(String.class, int.class);
User user2 = (User) ctor.newInstance("Alice", 30);
```

**Важно:** `Class.newInstance()` deprecated, потому что:
- Не работает с конструкторами с параметрами
- Проглатывает checked exceptions
- Требует no-arg constructor

**Всегда используй `Constructor.newInstance()`!**

---

### Вызов методов через Reflection

```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    private int multiply(int a, int b) {
        return a * b;
    }
}

// Создать instance
Calculator calc = new Calculator();

// Получить метод
Method addMethod = Calculator.class.getMethod("add", int.class, int.class);

// Вызвать метод
Object result = addMethod.invoke(calc, 5, 10);
System.out.println(result);  // → 15
```

**Для private метода:**

```java
Method multiplyMethod = Calculator.class.getDeclaredMethod("multiply",
                                                            int.class, int.class);

// Private метод! Нужен setAccessible()
multiplyMethod.setAccessible(true);

Object result = multiplyMethod.invoke(calc, 5, 10);
System.out.println(result);  // → 50
```

---

### Чтение и изменение полей

```java
public class User {
    private String name = "Alice";
    private int age = 30;
}

User user = new User();
Class<?> clazz = user.getClass();

// Получить поле
Field nameField = clazz.getDeclaredField("name");

// Private поле! Нужен setAccessible()
nameField.setAccessible(true);

// Прочитать значение
String name = (String) nameField.get(user);
System.out.println(name);  // → "Alice"

// Изменить значение
nameField.set(user, "Bob");

String newName = (String) nameField.get(user);
System.out.println(newName);  // → "Bob"
```

**Типы полей:**

```java
// Примитивы
Field ageField = clazz.getDeclaredField("age");
ageField.setAccessible(true);

int age = ageField.getInt(user);  // Без boxing
ageField.setInt(user, 35);

// Альтернатива (с boxing)
int age2 = (int) ageField.get(user);
```

---

## Dynamic Proxies: Создание классов на лету

### Концепция

**Dynamic Proxy — класс, созданный JVM во время выполнения.**

```
Обычный класс:
  UserService.java → javac → UserService.class → JVM загружает

Dynamic Proxy:
  Нет .java файла!
  JVM создаёт класс во время выполнения:
    Proxy.newProxyInstance() → JVM генерирует класс
```

---

### Пример: Logging Proxy

```java
// Interface
public interface UserService {
    User getUser(Long id);
    void saveUser(User user);
}

// Реализация
public class UserServiceImpl implements UserService {
    @Override
    public User getUser(Long id) {
        System.out.println("Fetching user " + id);
        return new User(id, "Alice");
    }

    @Override
    public void saveUser(User user) {
        System.out.println("Saving user " + user);
    }
}
```

**Создаём Logging Proxy:**

```java
UserService realService = new UserServiceImpl();

// InvocationHandler — перехватывает все вызовы методов
InvocationHandler handler = new InvocationHandler() {
    @Override
    public Object invoke(Object proxy, Method method, Object[] args)
            throws Throwable {
        // Before
        System.out.println("[LOG] Calling: " + method.getName());
        System.out.println("[LOG] Args: " + Arrays.toString(args));

        // Вызов реального метода
        Object result = method.invoke(realService, args);

        // After
        System.out.println("[LOG] Result: " + result);

        return result;
    }
};

// Создать proxy
UserService proxy = (UserService) Proxy.newProxyInstance(
    UserService.class.getClassLoader(),    // ClassLoader
    new Class<?>[] { UserService.class },  // Interfaces
    handler                                 // InvocationHandler
);

// Использование
User user = proxy.getUser(1L);
```

**Output:**
```
[LOG] Calling: getUser
[LOG] Args: [1]
Fetching user 1
[LOG] Result: User(id=1, name=Alice)
```

**Каждый вызов метода proxy перехватывается InvocationHandler!**

---

### Архитектура Dynamic Proxy

```
┌────────────────────────────────────────────────────┐
│  Client Code                                       │
│    proxy.getUser(1L)                               │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────┐
│  Dynamic Proxy (сгенерирован JVM)                  │
│  class $Proxy0 implements UserService {            │
│      private InvocationHandler h;                  │
│                                                     │
│      public User getUser(Long id) {                │
│          Method m = UserService.class              │
│                     .getMethod("getUser", Long);   │
│          return (User) h.invoke(this, m, [id]);    │
│      }                                              │
│  }                                                  │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────┐
│  InvocationHandler                                 │
│    invoke(proxy, method, args)                     │
│      - Logging                                     │
│      - Transaction management                      │
│      - Security checks                             │
│      - Caching                                     │
│      - Retry logic                                 │
│      → method.invoke(realService, args)            │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────┐
│  Real Service Implementation                       │
│    UserServiceImpl.getUser(1L)                     │
└────────────────────────────────────────────────────┘
```

---

### Реальный пример: Spring AOP

**Spring использует Dynamic Proxies для AOP:**

```java
@Service
public class UserService {

    @Transactional  // Spring создаёт proxy для управления транзакциями
    public void saveUser(User user) {
        userRepository.save(user);
    }
}

// За кулисами Spring:
UserService realService = new UserService();

InvocationHandler handler = (proxy, method, args) -> {
    if (method.isAnnotationPresent(Transactional.class)) {
        // Start transaction
        Transaction tx = transactionManager.getTransaction();
        try {
            Object result = method.invoke(realService, args);
            tx.commit();  // Commit на успехе
            return result;
        } catch (Exception e) {
            tx.rollback();  // Rollback на ошибке
            throw e;
        }
    } else {
        return method.invoke(realService, args);
    }
};

UserService proxy = (UserService) Proxy.newProxyInstance(...);
applicationContext.registerBean("userService", proxy);
```

**Spring возвращает proxy, а не реальный объект!**

---

## Annotations через Reflection

### Чтение аннотаций

```java
@Retention(RetentionPolicy.RUNTIME)  // Важно!
@Target(ElementType.METHOD)
public @interface Cacheable {
    int ttl() default 60;
    String key() default "";
}

public class UserService {
    @Cacheable(ttl = 300, key = "user:{id}")
    public User getUser(Long id) {
        return database.findUser(id);
    }
}
```

**Получить аннотации через Reflection:**

```java
Class<?> clazz = UserService.class;
Method method = clazz.getMethod("getUser", Long.class);

// Проверить наличие аннотации
boolean isCacheable = method.isAnnotationPresent(Cacheable.class);

// Получить аннотацию
Cacheable cacheable = method.getAnnotation(Cacheable.class);

if (cacheable != null) {
    int ttl = cacheable.ttl();      // 300
    String key = cacheable.key();   // "user:{id}"

    System.out.println("Cache TTL: " + ttl);
    System.out.println("Cache Key: " + key);
}
```

**Все аннотации метода:**

```java
Annotation[] annotations = method.getAnnotations();
for (Annotation annotation : annotations) {
    System.out.println(annotation);
}
```

---

### Пример: Валидация через аннотации

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface NotNull {
    String message() default "Field cannot be null";
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface Min {
    int value();
    String message() default "Value too small";
}

public class User {
    @NotNull(message = "Name is required")
    private String name;

    @Min(value = 18, message = "Must be 18+")
    private int age;
}
```

**Validator через Reflection:**

```java
public class Validator {
    public static void validate(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();

        for (Field field : clazz.getDeclaredFields()) {
            field.setAccessible(true);
            Object value = field.get(obj);

            // Check @NotNull
            if (field.isAnnotationPresent(NotNull.class)) {
                if (value == null) {
                    NotNull annotation = field.getAnnotation(NotNull.class);
                    throw new Exception(annotation.message());
                }
            }

            // Check @Min
            if (field.isAnnotationPresent(Min.class)) {
                Min annotation = field.getAnnotation(Min.class);
                if (value instanceof Integer) {
                    int intValue = (int) value;
                    if (intValue < annotation.value()) {
                        throw new Exception(annotation.message());
                    }
                }
            }
        }
    }
}

// Использование
User user = new User(null, 15);
Validator.validate(user);  // Exception: Name is required
```

---

## Performance: Насколько медленно Reflection?

### Benchmark

```java
public class User {
    private String name = "Alice";
    public String getName() { return name; }
}

User user = new User();

// 1. Прямой вызов
long start = System.nanoTime();
for (int i = 0; i < 1_000_000; i++) {
    String name = user.getName();
}
long directTime = System.nanoTime() - start;

// 2. Reflection без кэширования
start = System.nanoTime();
for (int i = 0; i < 1_000_000; i++) {
    Method method = User.class.getMethod("getName");
    String name = (String) method.invoke(user);
}
long reflectionTime = System.nanoTime() - start;

// 3. Reflection с кэшированием
Method cachedMethod = User.class.getMethod("getName");
start = System.nanoTime();
for (int i = 0; i < 1_000_000; i++) {
    String name = (String) cachedMethod.invoke(user);
}
long cachedReflectionTime = System.nanoTime() - start;

System.out.println("Direct:              " + directTime / 1_000_000 + " ms");
System.out.println("Reflection (no cache): " + reflectionTime / 1_000_000 + " ms");
System.out.println("Reflection (cached):   " + cachedReflectionTime / 1_000_000 + " ms");
```

**Результаты:**
```
Direct:                2 ms    (baseline)
Reflection (no cache): 450 ms  (225x медленнее!)
Reflection (cached):   15 ms   (7.5x медленнее)
```

**Выводы:**
- Reflection **значительно медленнее** прямого вызова
- Получение Method/Field объекта — дорогая операция
- **Кэшируй Method/Field объекты!**
- Даже с кэшем Reflection в 7-10x медленнее

---

### Почему медленно?

**Прямой вызов (compile-time):**
```java
String name = user.getName();
// Компилируется в:
// invokevirtual User.getName()
// → прямой вызов в vtable (1-2 инструкции)
```

**Reflection (runtime):**
```java
Method method = clazz.getMethod("getName");
String name = (String) method.invoke(user);

// Что происходит:
// 1. Lookup метода по имени (медленно!)
//    - Проход по всем методам класса
//    - String сравнение имён
//    - Проверка parameter types
// 2. Security checks (setAccessible?)
// 3. Boxing/unboxing аргументов (Object[])
// 4. Native метод invoke() (JNI call)
// 5. Проверка типов во время выполнения
// 6. Exception handling
// 7. Unboxing результата
```

---

## Security: setAccessible() и проблемы

### Обход инкапсуляции

```java
public class BankAccount {
    private double balance = 1000.0;

    public double getBalance() {
        // Security check
        if (!hasPermission()) {
            throw new SecurityException("Access denied");
        }
        return balance;
    }
}

BankAccount account = new BankAccount();

// Через public метод — Security check
account.getBalance();  // Security check!

// Через Reflection — обходим Security!
Field balanceField = BankAccount.class.getDeclaredField("balance");
balanceField.setAccessible(true);  // Обход private!
double balance = balanceField.getDouble(account);
System.out.println(balance);  // → 1000.0 (без security check!)

// Можно даже изменить!
balanceField.setDouble(account, 999999.0);
```

**Reflection нарушает инкапсуляцию!**

---

### SecurityManager и Reflection

```java
// Установить SecurityManager
System.setSecurityManager(new SecurityManager());

// Теперь setAccessible() требует permission
try {
    Field field = BankAccount.class.getDeclaredField("balance");
    field.setAccessible(true);  // SecurityException!
} catch (SecurityException e) {
    System.err.println("Access denied: " + e.getMessage());
}
```

**Security Policy:**
```
grant {
    permission java.lang.reflect.ReflectPermission "suppressAccessChecks";
};
```

**Важно:** SecurityManager deprecated в Java 17 и будет удалён.

---

## Когда использовать Reflection

### ✅ Подходящие случаи

**1. Frameworks и библиотеки**

```java
// Spring Dependency Injection
@Autowired
private UserService userService;  // Spring использует Reflection для injection

// Hibernate ORM
@Entity
public class User { ... }  // Hibernate читает аннотации через Reflection
```

**2. Serialization/Deserialization**

```java
// Jackson JSON
ObjectMapper mapper = new ObjectMapper();
User user = mapper.readValue(json, User.class);
// Jackson использует Reflection для создания объекта

// XML, YAML, Protobuf — аналогично
```

**3. Testing Frameworks**

```java
// JUnit — находит тесты через Reflection
@Test
public void testGetUser() { ... }

// Mockito — создаёт mocks через Reflection
@Mock
private UserRepository userRepository;
```

**4. Plugin Systems**

```java
// Загрузка плагинов по имени класса
String pluginClassName = config.get("plugin.class");
Class<?> pluginClass = Class.forName(pluginClassName);
Plugin plugin = (Plugin) pluginClass.getDeclaredConstructor().newInstance();
```

---

### ❌ Когда НЕ использовать

**1. Performance-critical код**
```java
// ПЛОХО: Reflection в hot path
for (int i = 0; i < 1_000_000; i++) {
    Method method = clazz.getMethod("process");
    method.invoke(obj);
}

// ХОРОШО: Прямой вызов
for (int i = 0; i < 1_000_000; i++) {
    obj.process();
}
```

**2. Когда есть альтернативы**
```java
// ПЛОХО: Reflection для полиморфизма
if (type.equals("user")) {
    Method m = UserService.class.getMethod("process");
    m.invoke(service);
} else if (type.equals("order")) {
    Method m = OrderService.class.getMethod("process");
    m.invoke(service);
}

// ХОРОШО: Интерфейсы и полиморфизм
interface Service {
    void process();
}

Service service = getService(type);
service.process();
```

**3. Когда нужна type safety**
```java
// ПЛОХО: Reflection → нет compile-time проверок
Method method = clazz.getMethod("getName");  // Опечатка? Узнаем в runtime!

// ХОРОШО: Прямой вызов
String name = user.getName();  // Ошибка в compile-time
```

---

## Альтернативы Reflection

### MethodHandles API (Java 7+)

**Более быстрая альтернатива Reflection.**

```java
public class User {
    private String name = "Alice";
    public String getName() { return name; }
}

User user = new User();

// Reflection
Method method = User.class.getMethod("getName");
String name1 = (String) method.invoke(user);

// MethodHandles (быстрее!)
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodType methodType = MethodType.methodType(String.class);
MethodHandle getNameHandle = lookup.findVirtual(User.class, "getName", methodType);
String name2 = (String) getNameHandle.invoke(user);
```

**Преимущества MethodHandles:**
- Быстрее (JIT может оптимизировать лучше)
- Type-safe (MethodType проверяется)
- Лучше интегрируется с invokedynamic

**Недостатки:**
- Более сложный API
- Меньше flexibility

---

### Bytecode Generation (ASM, ByteBuddy)

**Генерация байткода вместо Reflection.**

```java
// Вместо Reflection для создания Proxy:
InvocationHandler handler = ...;
UserService proxy = (UserService) Proxy.newProxyInstance(...);

// ByteBuddy (быстрее):
UserService proxy = new ByteBuddy()
    .subclass(UserService.class)
    .method(any())
    .intercept(InvocationHandlerAdapter.of(handler))
    .make()
    .load(getClass().getClassLoader())
    .getLoaded()
    .getDeclaredConstructor()
    .newInstance();
```

**Преимущества:**
- Производительность как у обычного кода
- Нет overhead Reflection

**Недостатки:**
- Сложность
- Больше памяти (генерируются классы)

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Reflection медленный — избегай всегда" | Reflection в 7-100x медленнее direct call, но для редких операций (startup, config) это OK. Проблема — hot paths |
| "setAccessible(true) опасен" | Опасен если код выполняется в untrusted environment. В обычных приложениях Security Manager выключен — risks ограничены |
| "Reflection нарушает инкапсуляцию" | Технически да, но это controlled violation. Фреймворки (Spring, Hibernate) используют его осознанно для DI/ORM |
| "getDeclaredMethod включает inherited методы" | getDeclaredMethod — только declared в этом классе. getMethod — public включая inherited. Названия путают |
| "Method/Field объекты дешёвые" | Получение Method/Field — дорогая операция. Кэшируйте их для повторного использования в field |
| "JPMS полностью блокирует Reflection" | JPMS requires opens directive для reflection. Без opens — IllegalAccessError. Но --add-opens workaround существует |
| "Kotlin и Java Reflection одинаковы" | Kotlin имеет свой kotlin-reflect с KClass, KFunction. Java reflection видит Kotlin код как Java (companion = static и т.д.) |
| "Dynamic Proxy работает с классами" | Proxy.newProxyInstance работает только с interfaces. Для классов нужен ByteBuddy, CGLIB или Javassist |
| "Annotation.class хранит runtime info" | Только @Retention(RUNTIME) аннотации доступны в runtime. SOURCE/CLASS retention стираются |
| "MethodHandles полностью заменяют Reflection" | MethodHandles быстрее для вызовов, но менее flexible. Нет introspection API как в Reflection |

---

## CS-фундамент

| CS-концепция | Применение в Java Reflection |
|--------------|------------------------------|
| **Introspection** | Reflection = runtime introspection. Программа исследует собственную структуру: классы, методы, поля |
| **Metaprogramming** | Код, который работает с кодом как данными. Reflection — runtime metaprogramming в Java |
| **Dynamic Dispatch** | Method.invoke() реализует dynamic dispatch — метод выбирается в runtime по объекту |
| **Proxy Pattern** | Dynamic Proxy реализует GoF Proxy. Один handler для всех методов interface |
| **Type Reification** | Java generics erased, но Class<T> reified. Reflection работает с runtime types |
| **Access Control** | setAccessible обходит Java access modifiers. SecurityManager контролировал это (deprecated в Java 17) |
| **Method Lookup** | getDeclaredMethod vs getMethod — разные алгоритмы поиска. Inherited vs declared resolution |
| **Invocation Overhead** | Method.invoke добавляет boxing, array allocation, security checks. MethodHandles оптимизирует это |
| **Lazy Loading** | Reflection enables lazy class loading — класс загружается только при первом использовании |
| **Duck Typing (runtime)** | Через reflection можно реализовать duck typing — вызов метода по имени без compile-time типа |

---

## Связанные темы

- [[jvm-class-loader-deep-dive]] — Как ClassLoader загружает классы, используемые в Reflection
- [[jvm-basics-history]] — Как байткод обеспечивает Reflection возможности
- [[jvm-annotations-processing]] — Compile-time обработка аннотаций vs Runtime Reflection
- [[jvm-instrumentation-agents]] — Bytecode instrumentation как альтернатива Reflection
- [[jvm-bytecode-manipulation]] — ASM, ByteBuddy для генерации кода без Reflection
- [[jvm-security-model]] — SecurityManager и контроль доступа к Reflection
- [[java-modern-features]] — Method References, Lambdas как альтернативы Reflection

---

## Чеклист: Reflection API

**Базовое понимание:**
- [ ] Понимаю концепцию Reflection (introspection)
- [ ] Знаю три способа получить Class объект
- [ ] Умею получать Fields, Methods, Constructors
- [ ] Понимаю разницу getXxx() vs getDeclaredXxx()

**Dynamic Invocation:**
- [ ] Умею вызывать методы через Method.invoke()
- [ ] Умею читать/изменять поля через Field.get/set()
- [ ] Знаю про setAccessible() и его последствия
- [ ] Понимаю, зачем нужно кэшировать Method/Field объекты

**Dynamic Proxies:**
- [ ] Понимаю концепцию Dynamic Proxy
- [ ] Умею создавать proxy через Proxy.newProxyInstance()
- [ ] Знаю, как работает InvocationHandler
- [ ] Понимаю, как Spring использует proxies для AOP

**Production:**
- [ ] Знаю о performance overhead Reflection (7-100x медленнее)
- [ ] Понимаю проблемы безопасности (setAccessible)
- [ ] Знаю альтернативы (MethodHandles, bytecode generation)
- [ ] Умею читать аннотации через Reflection

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

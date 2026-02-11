---
title: "JVM Annotations & Processing - Метапрограммирование на compile-time"
created: 2025-11-25
modified: 2026-01-02
tags:
  - topic/jvm
  - annotations
  - apt
  - metaprogramming
  - lombok
  - code-generation
  - compiler
  - mapstruct
  - type/concept
  - level/advanced
type: concept
status: published
area: programming
confidence: high
sources:
  - "https://jcp.org/en/jsr/detail?id=175"
  - "https://en.wikipedia.org/wiki/Java_annotation"
  - "https://blog.tidelift.com/project-lombok-core-maintainer-reinier-zwitserloot-shares-his-open-source-journey"
  - "https://objectcomputing.com/resources/publications/sett/january-2010-reducing-boilerplate-code-with-project-lombok"
  - "https://projectlombok.org/"
  - "https://mapstruct.org/"
  - "https://docs.oracle.com/javase/8/docs/api/javax/annotation/processing/Processor.html"
prerequisites:
  - "[[jvm-basics-history]]"
  - "[[jvm-class-loader-deep-dive]]"
  - "[[jvm-reflection-api]]"
related:
  - "[[jvm-reflection-api]]"
  - "[[jvm-bytecode-manipulation]]"
  - "[[jvm-service-loader-spi]]"
---

# JVM Annotations & Processing

## Prerequisites (Что нужно знать перед изучением)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **Базовый Java** | Классы, интерфейсы, наследование | Любой курс по Java |
| **Reflection API** | Понимание runtime анализа классов | [[jvm-reflection-api]] |
| **Компилятор javac** | Понимание процесса компиляции | [[jvm-basics-history]] |
| **Generics** | Типы в аннотациях используют generics | Java Generics Tutorial |
| **Build tools** | Maven/Gradle для интеграции | [[maven-gradle-basics]] |

---

## Почему появились аннотации? (История)

### Аналогия: Аннотации как стикеры

> **Представьте:** У вас есть документы (Java код). Раньше, чтобы пометить документ как "важный" или "для архива", приходилось переписывать его или добавлять специальный текст внутрь. Аннотации — это как цветные стикеры: вы клеите их на документ, не меняя содержимое. Стикер может сказать "обработать автоматически", "отправить в отдел X", или "особые требования".

### История создания (JSR-175)

**До 2004 года: Ad-hoc решения**

Java использовала разрозненные механизмы для метаданных:
- `transient` модификатор — "не сериализовать это поле"
- `@deprecated` в Javadoc — "метод устарел"
- XML-конфигурация (EJB 2.x) — огромные XML файлы отдельно от кода

> *"Существует растущая тенденция аннотировать поля, методы и классы атрибутами, указывающими на особую обработку. Существующие механизмы адекватны для простых случаев, но становятся всё более неудобными для сложных."*
> — JSR-175 Specification (2002)

**2004: Java 5 (JSR-175) — Рождение аннотаций**

JSR-175 был представлен в Java Community Process в 2002 и одобрен в сентябре 2004:

- Стандартный синтаксис `@AnnotationName`
- Retention policies (SOURCE, CLASS, RUNTIME)
- Target types (TYPE, METHOD, FIELD, etc.)
- Built-in аннотации: `@Override`, `@Deprecated`, `@SuppressWarnings`

**2006: Java 6 (JSR-269) — Annotation Processing API**

APT (Annotation Processing Tool) интегрирован в `javac`:
- Compile-time обработка аннотаций
- Генерация исходного кода
- Pluggable processors

### 2009: Lombok — "Boilerplate Busters"

Reinier Zwitserloot и Roel Spilker создали Project Lombok:

> *"Lombok — это не язык программирования; он делает общий boilerplate лёгким для вас."*
> — Reinier Zwitserloot, создатель Lombok

**Почему назвали "Lombok"?** Остров Ломбок находится к востоку от Явы (Java) в Индонезии. "Lombok" по-индонезийски значит "чили" — отсюда слоган "Spicing up your Java" (Приправляем вашу Java).

**Технический "хак" Lombok:**

> *"Это полный хак. Использование non-public API. Presumptuous casting (зная, что annotation processor в javac получит JavacAnnotationProcessor, внутреннюю реализацию). На Eclipse ещё хуже — java agent внедряет код в классы парсера Eclipse, что абсолютно off limits. Если бы можно было сделать то, что делает Lombok, стандартным API, я бы так и сделал, но нельзя."*
> — Reinier Zwitserloot

### Timeline

```
2002        2004        2006        2009        2014        2018
  │           │           │           │           │           │
  ▼           ▼           ▼           ▼           ▼           ▼
JSR-175    Java 5      Java 6      Lombok     MapStruct   Kotlin
Proposal  Annotations  APT/JSR-269  Release    1.0        (KAPT→KSP)
          @Override    javac                  Type-safe
          @Deprecated  integration            mappers
```

---

## Терминология для новичков

| Термин | Что это простыми словами | Аналогия |
|--------|-------------------------|----------|
| **Annotation** | Метаданные, прикреплённые к коду | Стикер на документе |
| **Retention** | Когда аннотация доступна | Срок годности стикера |
| **SOURCE** | Только в исходном коде | Стикер отклеивается при печати |
| **CLASS** | В .class, но не в runtime | Стикер виден на копии, но не читается машиной |
| **RUNTIME** | Доступна через reflection | Стикер с QR-кодом, который можно сканировать |
| **Target** | Где можно использовать аннотацию | На какие документы можно клеить стикер |
| **Annotation Processor** | Программа, обрабатывающая аннотации | Робот, сортирующий документы по стикерам |
| **APT** | Annotation Processing Tool | Конвейер для роботов-сортировщиков |
| **Code Generation** | Создание нового кода на основе аннотаций | Робот пишет дополнительные документы |
| **Reflection** | Анализ кода во время выполнения | Рентген для программы |
| **Boilerplate** | Повторяющийся шаблонный код | Формальные фразы в письмах |
| **Meta-annotation** | Аннотация для аннотаций | Инструкция для создания стикеров |
| **Functional Interface** | Интерфейс с одним методом | Розетка с одним слотом |
| **Processing Round** | Один проход обработки аннотаций | Один круг на конвейере |

---

## TL;DR

**Аннотации** — это метаданные, которые можно обрабатывать на **compile-time** или **runtime** для генерации кода, валидации или модификации поведения. **Annotation Processing Tool (APT)** позволяет писать код, который пишет код (метапрограммирование).

**Ключевые концепции:**
- **Runtime аннотации** (@Retention(RUNTIME)) — читаются через рефлексию
- **Compile-time аннотации** (@Retention(SOURCE)) — обрабатываются компилятором
- **Annotation Processors** наследуют AbstractProcessor для генерации кода
- **Популярные инструменты:** Lombok (уменьшение boilerplate), MapStruct (маппинг), Dagger (DI)

**Когда использовать:**
- ✅ Сокращение boilerplate кода (getters, setters, builders)
- ✅ Генерация type-safe кода (mappers, validators)
- ✅ Проверки на compile-time
- ✅ Создание DSL и фреймворков

**Когда НЕ использовать:**
- ❌ Сложная бизнес-логика (используйте обычный код)
- ❌ Код зависит от runtime данных (конфигурация из файла)
- ❌ Нужна гибкость без перекомпиляции
- ❌ Простые задачи (проще написать 10 строк руками)

---

## Проблема: Boilerplate и Type Safety

### Традиционный подход

**Без аннотаций — 50 строк для простого POJO:**
```java
public class User {
    private Long id;
    private String name;
    private String email;

    public User() {}

    public User(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }

    // 15+ строк геттеров/сеттеров
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    // ...

    // 15+ строк equals(), hashCode(), toString()
}
```

**С Lombok — 5 строк:**
```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    private Long id;
    private String name;
    private String email;
}
```

---

## Основы аннотаций

### Retention Policy

**@Retention** определяет, когда аннотация доступна:

```java
// SOURCE: Отбрасывается компилятором (@Override, @SuppressWarnings)
@Retention(RetentionPolicy.SOURCE)
@interface CompileTimeOnly { }

// CLASS: В .class файле, но не доступна в runtime (по умолчанию)
@Retention(RetentionPolicy.CLASS)
@interface BytecodeMetadata { }

// RUNTIME: Доступна через reflection в runtime
@Retention(RetentionPolicy.RUNTIME)
@interface RuntimeConfig {
    String name();
    int priority() default 0;
}
```

**Жизненный цикл:**
```
Source Code (@Override)
      ↓ Компиляция
.class file (CLASS annotations)
      ↓ Загрузка
Runtime (RUNTIME annotations доступны через reflection)
```

### Target Types

**@Target** ограничивает где можно использовать аннотацию:

```java
@Target(ElementType.TYPE)           // Classes, interfaces, enums
@interface Entity {}

@Target(ElementType.FIELD)          // Поля
@interface Column {}

@Target(ElementType.METHOD)         // Методы
@interface Transactional {}

@Target(ElementType.PARAMETER)      // Параметры методов
@interface Valid {}

@Target(ElementType.TYPE_USE)       // Любое использование типа (Java 8+)
@interface NonNull {}

// Несколько целей
@Target({ElementType.TYPE, ElementType.METHOD})
@interface Documented {}
```

### Создание кастомной аннотации

```java
/**
 * Маркирует метод для мониторинга производительности
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Monitored {
    String value() default "";           // Имя метрики
    long thresholdMs() default 1000;     // Порог предупреждения
    LogLevel level() default LogLevel.WARN;

    enum LogLevel { DEBUG, INFO, WARN, ERROR }
}

// Использование
public class UserService {
    @Monitored(value = "user.fetch", thresholdMs = 500)
    public User getUser(Long id) {
        return userRepository.findById(id);
    }
}
```

---

## Runtime Annotation Processing

### Обработка через рефлексию

```java
public class AnnotationInspector {
    public static void inspectClass(Class<?> clazz) {
        // Аннотации класса
        if (clazz.isAnnotationPresent(Entity.class)) {
            Entity entity = clazz.getAnnotation(Entity.class);
            System.out.println("Entity: " + entity.name());
        }

        // Аннотации полей
        for (Field field : clazz.getDeclaredFields()) {
            if (field.isAnnotationPresent(Column.class)) {
                Column column = field.getAnnotation(Column.class);
                System.out.println("Field: " + field.getName() +
                                 " -> Column: " + column.name());
            }
        }

        // Аннотации методов
        for (Method method : clazz.getDeclaredMethods()) {
            if (method.isAnnotationPresent(Monitored.class)) {
                Monitored m = method.getAnnotation(Monitored.class);
                System.out.println("Method: " + method.getName() +
                                 ", threshold: " + m.thresholdMs() + "ms");
            }
        }
    }
}
```

### Dynamic Proxy для AOP

```java
public class MonitoringProxy implements InvocationHandler {
    private final Object target;

    public static <T> T create(T target) {
        return (T) Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            new MonitoringProxy(target)
        );
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args)
            throws Throwable {
        Monitored annotation = method.getAnnotation(Monitored.class);
        if (annotation == null) {
            return method.invoke(target, args);
        }

        // Мониторинг выполнения
        long start = System.nanoTime();
        try {
            Object result = method.invoke(target, args);
            long duration = TimeUnit.NANOSECONDS.toMillis(
                System.nanoTime() - start
            );

            if (duration > annotation.thresholdMs()) {
                System.err.printf("[%s] Slow method %s: %dms%n",
                    annotation.level(), method.getName(), duration);
            }
            return result;
        } catch (InvocationTargetException e) {
            throw e.getCause();
        }
    }
}

// Использование
UserService service = MonitoringProxy.create(new UserServiceImpl());
service.getUser(123L);  // Автоматически мониторится
```

---

## Compile-Time Annotation Processing (APT)

### Аналогия: APT как сортировочный конвейер на почте

> **Представьте:** Почтовое отделение (компилятор) получает письма (исходный код). На некоторых письмах наклеены стикеры (аннотации): "доставить экспресс", "требует подпись", "отправить копию в архив". Сортировочный конвейер (APT) проходит по всем письмам, читает стикеры и выполняет действия: генерирует квитанции (новые файлы), отправляет копии (сгенерированный код). Конвейер работает в несколько проходов (rounds): после первого прохода появились новые письма (сгенерированные файлы) — конвейер проходит ещё раз, пока новых писем не останется.

### Архитектура процессора

```
┌─────────────────────────────────────────┐
│         Java Compiler (javac)           │
│                                         │
│  Source Files (.java)                   │
│         ↓                               │
│  Parser (AST Creation)                  │
│         ↓                               │
│  ┌───────────────────────────────────┐  │
│  │ Annotation Processing Rounds      │  │
│  │                                   │  │
│  │ Round 1: Process @Entity          │  │
│  │          Generate DAO classes     │  │
│  │                                   │  │
│  │ Round 2: Process generated files  │  │
│  │                                   │  │
│  │ Round N: No new files → stop      │  │
│  └───────────────────────────────────┘  │
│         ↓                               │
│  Bytecode Generation (.class files)     │
└─────────────────────────────────────────┘
```

### Реализация AbstractProcessor

```java
import javax.annotation.processing.*;
import javax.lang.model.element.*;
import javax.tools.JavaFileObject;
import java.io.PrintWriter;
import java.util.Set;

@SupportedAnnotationTypes("com.example.AutoBuilder")
@SupportedSourceVersion(SourceVersion.RELEASE_17)
public class BuilderProcessor extends AbstractProcessor {

    private Messager messager;
    private Filer filer;

    @Override
    public void init(ProcessingEnvironment processingEnv) {
        super.init(processingEnv);
        this.messager = processingEnv.getMessager();
        this.filer = processingEnv.getFiler();
    }

    @Override
    public boolean process(Set<? extends TypeElement> annotations,
                          RoundEnvironment roundEnv) {

        // Найти все классы с @AutoBuilder
        for (Element element : roundEnv.getElementsAnnotatedWith(AutoBuilder.class)) {
            if (element.getKind() != ElementKind.CLASS) {
                messager.printMessage(Diagnostic.Kind.ERROR,
                    "@AutoBuilder only for classes", element);
                continue;
            }

            TypeElement typeElement = (TypeElement) element;
            try {
                generateBuilder(typeElement);
            } catch (IOException e) {
                messager.printMessage(Diagnostic.Kind.ERROR,
                    "Failed to generate: " + e.getMessage(), element);
            }
        }

        return true;  // Аннотации обработаны
    }

    private void generateBuilder(TypeElement typeElement) throws IOException {
        String className = typeElement.getSimpleName().toString();
        String packageName = processingEnv.getElementUtils()
            .getPackageOf(typeElement).toString();

        // Создать новый source файл
        JavaFileObject builderFile = filer.createSourceFile(
            packageName + "." + className + "Builder"
        );

        try (PrintWriter out = new PrintWriter(builderFile.openWriter())) {
            // Генерация builder класса
            out.println("package " + packageName + ";");
            out.println();
            out.println("public class " + className + "Builder {");

            // Поля и методы для каждого поля оригинального класса
            for (Element enclosed : typeElement.getEnclosedElements()) {
                if (enclosed.getKind() == ElementKind.FIELD) {
                    VariableElement field = (VariableElement) enclosed;
                    String fieldName = field.getSimpleName().toString();
                    String fieldType = field.asType().toString();

                    out.println("    private " + fieldType + " " + fieldName + ";");
                    out.println("    public " + className + "Builder " + fieldName +
                               "(" + fieldType + " " + fieldName + ") {");
                    out.println("        this." + fieldName + " = " + fieldName + ";");
                    out.println("        return this;");
                    out.println("    }");
                }
            }

            // build() метод
            out.println("    public " + className + " build() {");
            out.println("        return new " + className + "(...);");
            out.println("    }");
            out.println("}");
        }
    }
}
```

### Регистрация процессора

**META-INF/services/javax.annotation.processing.Processor:**
```
com.example.BuilderProcessor
```

Или использовать **Google AutoService:**
```java
@AutoService(Processor.class)
@SupportedAnnotationTypes("com.example.AutoBuilder")
public class BuilderProcessor extends AbstractProcessor { }
```

---

## Lombok Deep Dive

### Основные аннотации

```java
// @Getter/@Setter - Генерация геттеров/сеттеров
@Getter @Setter
public class User {
    private Long id;
    private String name;

    @Setter(AccessLevel.PRIVATE)  // Private setter
    private String password;
}

// @ToString - Генерация toString()
@ToString(exclude = "password")  // Исключить чувствительные поля
public class User {
    private Long id;
    private String name;
    private String password;
}

// @EqualsAndHashCode - Генерация equals() и hashCode()
@EqualsAndHashCode(of = {"id"})  // Только id
public class User {
    private Long id;
    private String name;
}

// @Data - Комбинация @Getter, @Setter, @ToString, @EqualsAndHashCode
@Data
public class User {
    private Long id;
    private String name;
}

// @Value - Immutable версия @Data
@Value  // Все поля private final, нет setters
public class Point {
    double x;
    double y;
}
```

### Builder Pattern

```java
@Builder
public class User {
    private Long id;
    private String name;
    private String email;

    @Singular  // Добавляет методы для коллекций
    private List<String> roles;
}

// Использование
User user = User.builder()
    .id(1L)
    .name("John Doe")
    .email("john@example.com")
    .role("ADMIN")      // Singular method
    .role("USER")       // Добавляет в коллекцию
    .build();

// Копирование с изменениями
@Builder(toBuilder = true)
public class User {
    private String name;
    private int age;
}

User updated = existingUser.toBuilder().age(31).build();
```

### Конструкторы

```java
// @NoArgsConstructor - Конструктор без параметров
@NoArgsConstructor(force = true)  // final поля = null/0
public class User {
    private final Long id;
}

// @AllArgsConstructor - Конструктор со всеми полями
@AllArgsConstructor
public class User {
    private Long id;
    private String name;
}

// @RequiredArgsConstructor - Конструктор для final/@NonNull полей
@RequiredArgsConstructor
public class UserService {
    private final UserRepository repository;  // Обязательное
    @NonNull private final Logger logger;     // Обязательное
    private String optionalConfig;            // Не включается
}
```

### Продвинутые возможности

```java
// @SneakyThrows - Оборачивает checked exceptions
@SneakyThrows(IOException.class)
public String readFile(String path) {
    return Files.readString(Path.of(path));
    // Не нужен try-catch
}

// @Synchronized - Thread-safe методы
public class Counter {
    private int count = 0;

    @Synchronized  // Использует private lock
    public void increment() {
        count++;
    }
}

// @Cleanup - Автоматическое закрытие ресурсов
public void processFile(String path) {
    @Cleanup InputStream in = new FileInputStream(path);
    // Автоматически вызовется in.close()
    byte[] data = in.readAllBytes();
}

// @With - Immutable setters (возвращают новый экземпляр)
@Value
@With
public class Point {
    double x;
    double y;
}

Point p1 = new Point(1.0, 2.0);
Point p2 = p1.withX(5.0);  // Новый экземпляр с x=5.0
```

---

## MapStruct - Type-Safe Маппинг

### Базовый маппинг

```java
// Source и target классы
public class UserEntity {
    private Long id;
    private String firstName;
    private String lastName;
    private String emailAddress;
    private LocalDateTime createdDate;
}

public class UserDTO {
    private Long id;
    private String fullName;
    private String email;
    private String createdAt;
}

// MapStruct mapper интерфейс
@Mapper(componentModel = "spring")
public interface UserMapper {

    @Mapping(target = "fullName",
             expression = "java(entity.getFirstName() + \" \" + entity.getLastName())")
    @Mapping(source = "emailAddress", target = "email")
    @Mapping(source = "createdDate", target = "createdAt",
             dateFormat = "yyyy-MM-dd HH:mm:ss")
    UserDTO toDTO(UserEntity entity);

    @InheritInverseConfiguration  // Обратный маппинг
    @Mapping(target = "firstName", ignore = true)
    @Mapping(target = "lastName", ignore = true)
    UserEntity toEntity(UserDTO dto);

    // Маппинг коллекций
    List<UserDTO> toDTOList(List<UserEntity> entities);
}
```

### Генерируемый код

MapStruct генерирует реализацию:

```java
@Component
public class UserMapperImpl implements UserMapper {

    @Override
    public UserDTO toDTO(UserEntity entity) {
        if (entity == null) return null;

        UserDTO dto = new UserDTO();
        dto.setId(entity.getId());
        dto.setEmail(entity.getEmailAddress());

        // Expression маппинг
        dto.setFullName(entity.getFirstName() + " " + entity.getLastName());

        // Форматирование даты
        if (entity.getCreatedDate() != null) {
            dto.setCreatedAt(
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
                    .format(entity.getCreatedDate())
            );
        }

        return dto;
    }

    // Null-safe, type-safe, без reflection
}
```

### Продвинутые возможности

```java
@Mapper(
    componentModel = "spring",
    uses = {DateMapper.class, AddressMapper.class},  // Делегирование
    unmappedTargetPolicy = ReportingPolicy.ERROR     // Strict mode
)
public interface OrderMapper {

    // Nested маппинг
    @Mapping(source = "customer.name", target = "customerName")
    @Mapping(source = "customer.address", target = "shippingAddress")
    OrderDTO toDTO(Order order);

    // Кастомная логика после маппинга
    @AfterMapping
    default void calculateTotal(@MappingTarget OrderDTO dto, Order order) {
        double total = order.getItems().stream()
            .mapToDouble(item -> item.getPrice() * item.getQuantity())
            .sum();
        dto.setTotal(total);
    }

    // Условный маппинг
    @Condition
    default boolean isNotEmpty(String value) {
        return value != null && !value.isEmpty();
    }

    // Qualifier для disambiguation
    @Named("toUpperCase")
    default String toUpperCase(String value) {
        return value != null ? value.toUpperCase() : null;
    }

    @Mapping(source = "status", target = "statusCode",
             qualifiedByName = "toUpperCase")
    OrderDTO toDTOWithUpperCase(Order order);
}
```

---

## Другие Annotation Processors

### Dagger 2 - Dependency Injection

```java
@Module
public class NetworkModule {
    @Provides
    @Singleton
    public OkHttpClient provideHttpClient() {
        return new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .build();
    }
}

@Singleton
@Component(modules = {NetworkModule.class})
public interface AppComponent {
    void inject(MainActivity activity);
}

// Dagger генерирует DaggerAppComponent
AppComponent component = DaggerAppComponent.create();
```

### AutoValue - Immutable Value Types

```java
@AutoValue
public abstract class Money {
    public abstract String currency();
    public abstract long amount();

    public static Money create(String currency, long amount) {
        return new AutoValue_Money(currency, amount);
    }
    // AutoValue генерирует equals(), hashCode(), toString()
}
```

---

## Build Integration

### Maven

```xml
<dependencies>
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <version>1.18.30</version>
        <scope>provided</scope>
    </dependency>

    <dependency>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct</artifactId>
        <version>1.5.5.Final</version>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <configuration>
                <annotationProcessorPaths>
                    <!-- Lombok ПЕРВЫМ -->
                    <path>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok</artifactId>
                        <version>1.18.30</version>
                    </path>
                    <!-- MapStruct ВТОРЫМ -->
                    <path>
                        <groupId>org.mapstruct</groupId>
                        <artifactId>mapstruct-processor</artifactId>
                        <version>1.5.5.Final</version>
                    </path>
                    <!-- Binding для совместимости -->
                    <path>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok-mapstruct-binding</artifactId>
                        <version>0.2.0</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### Gradle

```groovy
dependencies {
    // Lombok
    compileOnly 'org.projectlombok:lombok:1.18.30'
    annotationProcessor 'org.projectlombok:lombok:1.18.30'

    // MapStruct
    implementation 'org.mapstruct:mapstruct:1.5.5.Final'
    annotationProcessor 'org.mapstruct:mapstruct-processor:1.5.5.Final'

    // Binding
    annotationProcessor 'org.projectlombok:lombok-mapstruct-binding:0.2.0'
}

compileJava {
    options.compilerArgs += [
        '-Amapstruct.defaultComponentModel=spring',
        '-Amapstruct.unmappedTargetPolicy=ERROR'
    ]
}
```

### IntelliJ IDEA Setup

1. **Settings → Compiler → Annotation Processors**
   - ✓ Enable annotation processing
   - ✓ Obtain processors from project classpath

2. **Install Plugins:**
   - Lombok Plugin
   - MapStruct Plugin

3. **Rebuild Project:** Build → Rebuild Project

---

## Performance Considerations

### Overhead компиляции

```
Проект 500 классов:
Без процессоров:       15s (baseline)
+ Lombok:              20s (+33%)
+ MapStruct:           25s (+67%)
+ Custom processor:    30s (+100%)

Incremental compilation (Gradle):
- Первая сборка:       100%
- Инкрементальная:     15%
```

### Runtime производительность

**Compile-time генерация vs Runtime reflection:**

```
Операция                  Время (ns)    Относительно
──────────────────────────────────────────────────────
Direct method call                5    1x (baseline)
Generated method call            10    2x
Reflection (cached)             100    20x
Reflection (uncached)         1,000    200x
```

**Вывод:** Compile-time генерация намного быстрее runtime reflection.

---

## Debugging

### Включение verbose логов

```bash
# Maven
mvn clean compile -X

# Gradle
./gradlew clean compileJava --debug

# Javac
javac -processor com.example.MyProcessor \
      -Xlint:processing \
      -verbose \
      MyClass.java
```

### Просмотр сгенерированного кода

```bash
# Maven
ls -la target/generated-sources/annotations/

# Gradle
ls -la build/generated/sources/annotationProcessor/

# Просмотр
cat target/generated-sources/annotations/com/example/UserMapperImpl.java
```

### Remote debugging

```bash
# Maven
mvnDebug clean compile

# Gradle
./gradlew clean compileJava --debug-jvm

# Подключить debugger к порту 5005
```

---

## Типичные проблемы

### 1. Процессор не найден

**Проблема:**
```
warning: No processor claimed any of these annotations: com.example.MyAnnotation
```

**Решение:**
```java
// Полное имя пакета!
@SupportedAnnotationTypes("com.example.MyAnnotation")
public class MyProcessor extends AbstractProcessor { }

// Или META-INF/services/javax.annotation.processing.Processor
com.example.MyProcessor

// Или AutoService
@AutoService(Processor.class)
public class MyProcessor extends AbstractProcessor { }
```

### 2. Lombok + MapStruct порядок

**Проблема:** MapStruct не видит Lombok-generated методы

**Решение:** Правильный порядок в annotationProcessorPaths:
1. Lombok ПЕРВЫМ
2. MapStruct ВТОРЫМ
3. lombok-mapstruct-binding

### 3. Circular Dependencies

**Проблема:** Generated класс ссылается на аннотированный класс

**Решение:** Использовать интерфейсы для разрыва цикла

### 4. IDE не видит сгенерированный код

**Проблема:** Код компилируется, но IDE показывает ошибки

**Решение:**
```
IntelliJ IDEA:
1. File → Invalidate Caches / Restart
2. Build → Rebuild Project
3. Проверить Settings → Build → Compiler → Annotation Processors → ✓ Enable

Gradle:
./gradlew clean build --refresh-dependencies

Maven:
mvn clean compile -U
```

### 5. Процессор выполняется бесконечно

**Проблема:** Процессор генерирует файл с аннотацией, которую сам обрабатывает

```java
// ❌ Бесконечный цикл
@SupportedAnnotationTypes("*")  // Обрабатывает ВСЁ
public class BadProcessor extends AbstractProcessor {
    @Override
    public boolean process(Set<? extends TypeElement> annotations,
                          RoundEnvironment roundEnv) {
        // Генерирует файл с @Entity
        // @Entity тоже обрабатывается → новый файл → и т.д.
    }
}

// ✅ Правильно
@SupportedAnnotationTypes("com.example.MyAnnotation")  // Только своя аннотация
public class GoodProcessor extends AbstractProcessor {
    @Override
    public boolean process(...) {
        // Сгенерированные файлы НЕ содержат @MyAnnotation
        return true;  // Аннотация claimed - другие не обрабатывают
    }
}
```

### 6. Проблемы с Kotlin и APT

**Проблема:** Kotlin использует KAPT, который медленнее

**Решение:**
```kotlin
// build.gradle.kts

// Вариант 1: KAPT (совместим с Java процессорами, но медленнее)
plugins {
    kotlin("kapt") version "1.9.22"
}

dependencies {
    kapt("org.mapstruct:mapstruct-processor:1.5.5.Final")
}

// Вариант 2: KSP (быстрее, но требует поддержки от библиотеки)
plugins {
    id("com.google.devtools.ksp") version "1.9.22-1.0.17"
}

dependencies {
    ksp("com.google.dagger:dagger-compiler:2.48")  // Dagger поддерживает KSP
}
```

**Сравнение KAPT vs KSP:**
| | KAPT | KSP |
|---|---|---|
| Совместимость | Любой Java processor | Только KSP-aware |
| Скорость | Медленный (генерирует stubs) | 2-3x быстрее |
| Kotlin features | Ограниченная поддержка | Полная поддержка |

---

## Compile-time vs Runtime: Decision Tree

```
                    ┌─────────────────────────────────┐
                    │ Нужна ли генерация/валидация?   │
                    └─────────────────────────────────┘
                                    │
                           ┌────────┴────────┐
                           ▼                 ▼
                          Да                Нет
                           │                 │
                           ▼                 ▼
           ┌───────────────────────┐    Обычный код
           │ Зависит от runtime    │
           │ данных?               │
           └───────────────────────┘
                    │
           ┌────────┴────────┐
           ▼                 ▼
          Да                Нет
           │                 │
           ▼                 ▼
    ┌─────────────┐   ┌─────────────────────────┐
    │ Runtime     │   │ Код статичен и известен │
    │ reflection  │   │ на compile-time?        │
    └─────────────┘   └─────────────────────────┘
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                        Да                Нет
                         │                 │
                         ▼                 ▼
               ┌───────────────┐   ┌────────────────┐
               │ Annotation    │   │ Bytecode       │
               │ Processing    │   │ manipulation   │
               │ (APT/KSP)     │   │ (ASM, Byte     │
               └───────────────┘   │ Buddy)         │
                                   └────────────────┘
```

**Примеры выбора:**

| Задача | Подход | Почему |
|--------|--------|--------|
| DTO маппинг | APT (MapStruct) | Типы известны на compile-time |
| DI граф | APT (Dagger) | Зависимости статичны |
| ORM маппинг | Runtime (Hibernate) | Может читать метаданные из DB |
| Мониторинг методов | Runtime proxy | Конфигурация может меняться |
| JSON сериализация | Оба варианта | Moshi (APT) vs Jackson (runtime) |

---

## Anti-patterns

### 1. Слишком много магии

```java
// ❌ Непонятно что происходит
@AutoEverything
@MagicInjection
@SmartSerialization
public class User { }

// ✅ Явные, понятные аннотации
@Data  // Понятно: getters/setters/equals/hashCode
@Builder  // Понятно: builder pattern
@JsonSerialize(using = UserSerializer.class)  // Явный сериализатор
public class User { }
```

### 2. Кастомный процессор для одноразовой задачи

```java
// ❌ Написали процессор для 3 классов
@GenerateAuditLog  // 100 строк процессора
public class Order { }

// ✅ Проще написать руками или использовать template
public class OrderAuditLog {
    // 20 строк прямого кода
}
```

### 3. Процессор изменяет существующие файлы

```java
// ❌ APT НЕ может модифицировать исходники!
// Это работает только для source генерации

// ✅ Если нужно модифицировать существующий код:
// - Lombok использует хаки с javac internals
// - Используйте bytecode manipulation (ASM, ByteBuddy)
// - Или AOP (AspectJ)
```

---

## Связанные темы

**Core Java:**
- [[jvm-reflection-api]] — Runtime обработка аннотаций
- [[jvm-bytecode-manipulation]] — Альтернатива source generation
- [[jvm-class-loader-deep-dive]] — Загрузка сгенерированных классов

**Инструменты:**
- [[jvm-instrumentation-agents]] — Runtime модификация байткода
- [[jvm-service-loader-spi]] — Plugin архитектура (похожие паттерны)

**Фреймворки:**
- Spring annotations (@Component, @Autowired)
- Hibernate annotations (@Entity, @Column)
- Jackson annotations (@JsonProperty)

---

## Чек-лист

### Дизайн аннотаций
- [ ] Выбрать правильный @Retention (SOURCE/CLASS/RUNTIME)
- [ ] Указать @Target (TYPE, FIELD, METHOD, etc.)
- [ ] Документировать JavaDoc
- [ ] Предоставить дефолтные значения для опциональных атрибутов
- [ ] Рассмотреть @Inherited, @Repeatable если нужно

### Реализация процессора
- [ ] Наследовать AbstractProcessor
- [ ] Реализовать getSupportedAnnotationTypes() или @SupportedAnnotationTypes
- [ ] Реализовать getSupportedSourceVersion()
- [ ] Обработать несколько processing rounds
- [ ] Использовать Messager для ошибок/предупреждений
- [ ] Зарегистрировать через META-INF/services или AutoService

### Build конфигурация
- [ ] Добавить annotation processor зависимость
- [ ] Настроить compiler plugin с annotationProcessorPaths
- [ ] Установить compiler arguments (-A опции)
- [ ] Настроить IDE annotation processing
- [ ] Добавить generated sources в source sets
- [ ] Исключить generated код из version control

### Тестирование
- [ ] Тестировать процессор с compile-testing библиотекой
- [ ] Проверить, что сгенерированный код компилируется
- [ ] Тестировать error messages для невалидных входов
- [ ] Проверить incremental compilation
- [ ] Benchmark времени компиляции

### Документация
- [ ] Документировать требуемые зависимости
- [ ] Предоставить примеры использования
- [ ] Объяснить структуру генерируемого кода
- [ ] Перечислить опции конфигурации
- [ ] Описать техники отладки

---

**Summary:** Annotation processing — это мощный механизм compile-time метапрограммирования для генерации кода, валидации и сокращения boilerplate. Выбирайте SOURCE retention для процессоров, RUNTIME для reflection-based фреймворков. Lombok и MapStruct — готовые production решения; кастомные процессоры — для специализированных задач. Всегда правильно настраивайте build tools и тщательно тестируйте сгенерированный код. Compile-time генерация быстрее runtime reflection в 20-200 раз.

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Annotation processors могут модифицировать существующий код" | APT может только генерировать НОВЫЕ файлы. Lombok работает через хаки javac internals, не через стандартный API |
| "KAPT и APT идентичны" | KAPT запускает APT в отдельном процессе, создавая Java stubs из Kotlin кода. KSP — нативная альтернатива, в 2x быстрее |
| "Все аннотации доступны в runtime" | Зависит от @Retention: SOURCE (только компиляция), CLASS (в bytecode, не в runtime), RUNTIME (доступны через reflection) |
| "Annotation processing замедляет сборку незначительно" | Каждый processor добавляет round. Lombok + Dagger + MapStruct = 3+ rounds × N модулей. Может удвоить время компиляции |
| "Generated код не нужно тестировать" | Generated код — часть production. Bugs в генераторе → bugs в приложении. Тестируйте через integration tests |
| "@Inherited работает для всех аннотаций" | @Inherited работает только для CLASS annotations на суперклассах, не для interfaces или methods |
| "AutoService заменяет ручную регистрацию" | AutoService генерирует META-INF/services файлы, но не решает проблемы с classpath isolation или module path |
| "KSP полностью заменяет KAPT" | KSP не поддерживает все Java annotation processors. Dagger, Room перешли на KSP, но некоторые библиотеки требуют KAPT |
| "Compile-time generation всегда лучше reflection" | Для редких операций reflection проще. Для hot paths и startup — compile-time выигрывает 20-200x |
| "Processor должен обрабатывать все rounds" | Processor вызывается в каждом round, но должен генерировать только в первом (processingOver() = false) |

---

## CS-фундамент

| CS-концепция | Применение в Annotation Processing |
|--------------|-----------------------------------|
| **Metaprogramming** | Код, который генерирует код. APT — compile-time metaprogramming vs runtime reflection |
| **Code Generation** | JavaPoet/KotlinPoet создают AST → source code. Type-safe API для генерации валидного кода |
| **Round-Based Processing** | Итеративная обработка: каждый round обрабатывает новые сгенерированные файлы до достижения fixpoint |
| **Incremental Compilation** | Isolating/aggregating processors. Isolating: один input → один output. Aggregating: все inputs → один output |
| **Service Provider Interface** | META-INF/services регистрирует processors. ServiceLoader обнаруживает их при компиляции |
| **Abstract Syntax Tree** | Element API представляет AST программы. TypeMirror, ExecutableElement, VariableElement — узлы дерева |
| **Filer API** | Абстракция файловой системы для генерации. Handles incremental builds, source/class output |
| **Diagnostic Messages** | Messager API для errors/warnings. Compile-time validation с человекочитаемыми сообщениями |
| **Retention Policy** | SOURCE → compile-only, CLASS → bytecode (default), RUNTIME → reflection. Trade-off: overhead vs capabilities |
| **Symbol Resolution** | Elements API для навигации по типам. getEnclosingElement(), getEnclosedElements() для traversal |

---

## Источники

1. [JSR 175: A Metadata Facility for Java](https://jcp.org/en/jsr/detail?id=175) — Официальная спецификация аннотаций
2. [Wikipedia: Java Annotation](https://en.wikipedia.org/wiki/Java_annotation) — История и обзор
3. [Tidelift: Reinier Zwitserloot Interview](https://blog.tidelift.com/project-lombok-core-maintainer-reinier-zwitserloot-shares-his-open-source-journey) — История создания Lombok
4. [Object Computing: Reducing Boilerplate with Lombok](https://objectcomputing.com/resources/publications/sett/january-2010-reducing-boilerplate-code-with-project-lombok) — Обзор Lombok (2010)
5. [Project Lombok](https://projectlombok.org/) — Официальная документация
6. [MapStruct](https://mapstruct.org/) — Официальная документация
7. [Oracle: Processor API](https://docs.oracle.com/javase/8/docs/api/javax/annotation/processing/Processor.html) — Официальный API

---

## Связь с другими темами

**[[jvm-reflection-api]]** — Reflection API и аннотации тесно связаны: runtime-аннотации (@Retention(RUNTIME)) читаются именно через Reflection, а compile-time аннотации обрабатываются APT без участия Reflection. Понимание Reflection необходимо для реализации annotation-driven фреймворков (Spring, Hibernate), где аннотации управляют поведением в runtime. Рекомендуется сначала изучить Reflection, затем переходить к annotation processing, так как APT работает с аналогичными концепциями (Element API вместо java.lang.reflect), но на этапе компиляции.

**[[jvm-bytecode-manipulation]]** — Annotation Processing (APT) и bytecode manipulation — два альтернативных подхода к метапрограммированию на JVM. APT генерирует новые .java файлы на compile-time, тогда как ASM/ByteBuddy модифицируют байткод в runtime или при сборке. Lombok — уникальный случай, сочетающий оба подхода: использует APT-интерфейс, но фактически модифицирует AST через internal API javac. При выборе между подходами учитывайте: если типы известны на compile-time — APT быстрее и безопаснее; если нужна runtime-гибкость — bytecode manipulation.

**[[jvm-service-loader-spi]]** — ServiceLoader и annotation processing используют похожий механизм регистрации: META-INF/services файлы. Annotation processors регистрируются через META-INF/services/javax.annotation.processing.Processor (или через Google AutoService, который сам является annotation processor). Понимание SPI помогает разобраться в том, как javac обнаруживает и загружает processors, а также как устроена модульная система plugins в Java экосистеме. Изучайте SPI параллельно с APT для целостного понимания plugin-архитектуры.

---

## Источники и дальнейшее чтение

- Bloch J. (2018). *Effective Java*, 3rd Edition. — Главы 39-41 посвящены аннотациям: когда создавать собственные, как правильно использовать @Override, и почему marker interfaces иногда лучше marker annotations.
- Evans B., Flanagan D. (2018). *Java in a Nutshell*, 7th Edition. — Подробный справочник по синтаксису аннотаций, retention policies и annotation processing API с практическими примерами.
- Lindholm T. et al. (2014). *The Java Virtual Machine Specification*, Java SE 8 Edition. — Глава 4 описывает формат class-файлов и как аннотации хранятся в атрибутах RuntimeVisibleAnnotations и RuntimeInvisibleAnnotations.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

---
title: "JVM ServiceLoader & SPI - Service Provider Interface"
created: 2025-11-25
modified: 2026-01-02
tags:
  - topic/jvm
  - serviceloader
  - spi
  - plugin
  - modularity
  - extensibility
  - jdbc
  - type/concept
  - level/advanced
type: concept
status: published
area: programming
confidence: high
sources:
  - "https://docs.oracle.com/javase/8/docs/api/java/util/ServiceLoader.html"
  - "https://www.baeldung.com/java-jdbc-loading-drivers"
  - "https://reflectoring.io/service-provider-interface/"
  - "https://northcoder.com/post/class-loaders-service-providers-and/"
related:
  - "[[jvm-class-loader-deep-dive]]"
  - "[[jvm-module-system]]"
  - "[[design-patterns]]"
---

# JVM ServiceLoader & SPI

## Prerequisites (Что нужно знать перед изучением)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **Базовый Java** | Интерфейсы, классы | Любой курс по Java |
| **JAR файлы** | Понимание структуры JAR | [[java-build-tools]] |
| **Classpath** | Как JVM ищет классы | [[jvm-class-loader-deep-dive]] |
| **Reflection** | Основы динамической загрузки | [[jvm-reflection-api]] |

---

## Почему появился ServiceLoader? (История)

### Аналогия: SPI как розетки и вилки

> **Представьте:** У вас дома розетка (интерфейс сервиса). Вы можете подключить любое устройство с подходящей вилкой: лампу, телевизор, пылесос (реализации). Вам не нужно перестраивать дом, чтобы подключить новое устройство — просто вставьте вилку. ServiceLoader — это механизм, который автоматически находит все устройства с подходящими вилками и подключает их.

### До Java 6: Ручная загрузка

**Проблема с JDBC драйверами (до 2006):**

```java
// ❌ До JDBC 4.0 / Java 6:
// Каждый раз приходилось ВРУЧНУЮ загружать драйвер по имени!
Class.forName("org.postgresql.Driver");  // PostgreSQL
Class.forName("com.mysql.jdbc.Driver");  // MySQL

// Это работало через хак:
// static { DriverManager.registerDriver(new PostgresDriver()); }
// Но требовало ЖЁСТКО прописывать имя класса в коде!
```

**Проблемы:**
- Если драйвер переименован → код ломается
- Если драйвер отсутствует → `ClassNotFoundException` в runtime
- Нельзя добавить новый драйвер без изменения кода

### 2006: Java 6 (JSR-221) — Рождение ServiceLoader

> *"В Java 6 появился `java.util.ServiceLoader`, который обеспечивает runtime обнаружение и lazy загрузку реализаций сервисов."*

**После Java 6:**
```java
// ✓ JDBC 4.0+ / Java 6+:
// НИКАКОГО Class.forName! Драйверы обнаруживаются АВТОМАТИЧЕСКИ

Connection conn = DriverManager.getConnection(
    "jdbc:postgresql://localhost/mydb",
    "user", "password"
);

// Как это работает:
// 1. DriverManager использует ServiceLoader<Driver>
// 2. Находит META-INF/services/java.sql.Driver в JAR драйвера
// 3. Загружает и регистрирует драйвер автоматически
```

### 2017: Java 9 — Модульная система

```java
// Java 9+ с модулями:
module com.example.provider {
    provides com.example.api.MyService
        with com.example.provider.MyServiceImpl;
}

// Ещё безопаснее: проверка на этапе компиляции!
```

### Timeline

```
2004          2006           2009           2014           2017
  │             │              │              │              │
  ▼             ▼              ▼              ▼              ▼
Java 5        Java 6        SLF4J         JDBC 4.2       Java 9
Manual      ServiceLoader   Uses SPI     Auto-register   Module
loading      introduced    for logging   improved       provides/uses
  │             │              │              │              │
  └─────────────┴──────────────┴──────────────┴──────────────┘
                               │
                   ┌───────────┴───────────┐
                   │  SPI решает проблемы: │
                   │  • Plugin discovery   │
                   │  • Driver loading     │
                   │  • Loose coupling     │
                   └───────────────────────┘
```

---

## Терминология для новичков

| Термин | Что это простыми словами | Аналогия |
|--------|-------------------------|----------|
| **SPI** | Service Provider Interface — контракт для плагинов | Стандарт розетки (евророзетка) |
| **Service** | Интерфейс, определяющий функциональность | Тип розетки (220V, USB) |
| **Provider** | Конкретная реализация сервиса | Конкретное устройство (лампа, телевизор) |
| **ServiceLoader** | Механизм поиска и загрузки провайдеров | Электрик, который находит все устройства |
| **META-INF/services** | Файл со списком провайдеров | Инструкция "какие устройства совместимы" |
| **Lazy Loading** | Загрузка по требованию | Включить устройство только когда нужно |
| **Classpath** | Путь поиска классов | Карта дома, где искать розетки |
| **FQN** | Fully Qualified Name — полное имя класса | Полный адрес (страна.город.улица.дом) |
| **uses** | Объявление потребления сервиса (Java 9+) | "Мне нужна розетка" |
| **provides** | Объявление предоставления сервиса (Java 9+) | "У меня есть устройство для этой розетки" |

---

## TL;DR

**ServiceLoader** — встроенный механизм Java для **обнаружения и загрузки реализаций во время выполнения**. Паттерн **Service Provider Interface (SPI)** обеспечивает архитектуру плагинов и слабую связанность.

**Ключевые концепции:**
- **Service** — интерфейс, определяющий функциональность
- **Service Provider** — конкретная реализация интерфейса
- **ServiceLoader** — обнаруживает провайдеры через META-INF/services
- **Lazy loading** — провайдеры создаются по требованию
- **Module system** — объявление provides/uses (Java 9+)

**Когда использовать:**
- ✅ Системы плагинов (расширения загружаются динамически)
- ✅ Регистрация драйверов (JDBC, логирование)
- ✅ Расширяемые фреймворки
- ❌ Простое DI (используйте Spring/CDI)
- ❌ Все реализации известны на этапе компиляции

**Реальные примеры:**
- JDBC drivers (DriverManager)
- SLF4J логирование
- Java Cryptography Architecture
- Image I/O плагины

---

## Проблема: Обнаружение реализаций

### Без SPI - жёсткая связанность

```java
// PaymentService зависит от конкретной реализации
public class PaymentService {
    private PaymentProcessor processor;

    public PaymentService() {
        // ПРОБЛЕМА: Жёстко закодированная зависимость
        this.processor = new StripePaymentProcessor();

        // Чтобы добавить PayPal - нужно менять код и перекомпилировать
        // Нельзя выбрать процессор в runtime
        // Сложно тестировать (нельзя подменить mock)
    }
}
```

**Проблемы:**
- Жёсткая связанность с конкретной реализацией
- Нельзя добавить новые процессоры без изменения кода
- Нельзя настроить во время выполнения

### С SPI - слабая связанность

```java
// 1. Интерфейс сервиса
public interface PaymentProcessor {
    void process(Payment payment);
    String getProviderName();
}

// 2. Реализация (в отдельном JAR)
public class StripePaymentProcessor implements PaymentProcessor {
    @Override
    public void process(Payment payment) {
        // Логика обработки через Stripe
    }

    @Override
    public String getProviderName() {
        return "Stripe";
    }
}

// 3. Регистрация: META-INF/services/com.example.PaymentProcessor
com.example.StripePaymentProcessor
com.example.PayPalPaymentProcessor

// 4. Использование - API не знает о конкретных реализациях!
public class PaymentService {
    public void processPayment(Payment payment) {
        ServiceLoader<PaymentProcessor> loader =
            ServiceLoader.load(PaymentProcessor.class);

        // ServiceLoader автоматически находит все реализации
        PaymentProcessor processor = loader.findFirst()
            .orElseThrow(() -> new IllegalStateException("No payment processor found"));

        processor.process(payment);
    }
}
```

**Преимущества:**
- ✅ Слабая связанность (API не знает реализаций)
- ✅ Добавление нового процессора = добавление JAR на classpath
- ✅ Не нужны изменения кода
- ✅ Легко тестировать (предоставить тестовую реализацию)

---

## Архитектура ServiceLoader

```
Как работает ServiceLoader:

1. Приложение:
   ServiceLoader<MyService> loader = ServiceLoader.load(MyService.class);

2. ServiceLoader сканирует classpath:
   - Ищет все файлы META-INF/services/com.example.MyService
   - Во всех JAR файлах на classpath

3. Читает имена классов из файлов:
   provider1.jar: com.provider1.MyServiceImpl
   provider2.jar: com.provider2.AlternativeImpl

4. По требованию (lazy) загружает и создаёт экземпляры:
   - Class.forName(имя класса)
   - Вызов конструктора без параметров
   - Кэширование созданных экземпляров

5. Возвращает итератор по провайдерам
```

**Ключевые особенности:**
- **Lazy loading** — провайдеры создаются только при обращении
- **Кэширование** — созданные экземпляры переиспользуются
- **Thread-safe** — ServiceLoader потокобезопасен
- **Конструктор без параметров** — обязателен для всех провайдеров

---

## Создание SPI (пошагово)

### Шаг 1: Определить интерфейс сервиса

```java
package com.example.service;

// Контракт для всех реализаций
public interface DatabaseDriver {
    Connection connect(String url, Properties props);
    String getDriverName();
}
```

### Шаг 2: Реализовать провайдер

```java
package com.example.provider.postgres;

public class PostgresDriver implements DatabaseDriver {

    // ВАЖНО: public конструктор без параметров обязателен!
    public PostgresDriver() {
        // Минимальная инициализация
    }

    @Override
    public Connection connect(String url, Properties props) {
        // PostgreSQL-специфичная логика подключения
        return new PostgresConnection(url, props);
    }

    @Override
    public String getDriverName() {
        return "PostgreSQL JDBC Driver";
    }
}
```

### Шаг 3: Зарегистрировать провайдер

**Файл:** `META-INF/services/com.example.service.DatabaseDriver`

```
# Полное имя класса реализации (один на строку)
com.example.provider.postgres.PostgresDriver

# Комментарии начинаются с #
# Пустые строки игнорируются
```

**Структура JAR:**
```
postgres-driver.jar
├── META-INF/
│   └── services/
│       └── com.example.service.DatabaseDriver    ← Имя = FQN интерфейса
│           (содержит: com.example.provider.postgres.PostgresDriver)
└── com/example/provider/postgres/
    └── PostgresDriver.class
```

### Шаг 4: Использовать ServiceLoader

```java
public class DatabaseManager {
    public static void main(String[] args) {
        // Загружаем все доступные драйверы
        ServiceLoader<DatabaseDriver> loader =
            ServiceLoader.load(DatabaseDriver.class);

        // Итерация по провайдерам (lazy loading)
        for (DatabaseDriver driver : loader) {
            System.out.println("Found: " + driver.getDriverName());
        }

        // Или получить первый доступный
        DatabaseDriver driver = loader.findFirst()
            .orElseThrow(() -> new RuntimeException("No database driver found"));

        // Использовать
        Connection conn = driver.connect("jdbc:postgresql://localhost/db", null);
    }
}
```

**Что происходит:**
1. ServiceLoader сканирует classpath
2. Находит `META-INF/services/com.example.service.DatabaseDriver`
3. Читает имена классов
4. При итерации создаёт экземпляры через рефлексию
5. Кэширует созданные объекты

---

## Продвинутые возможности

### Lazy Loading (ленивая загрузка)

```java
System.out.println("1. Создаём ServiceLoader...");
ServiceLoader<MyService> loader = ServiceLoader.load(MyService.class);
// Провайдеры ещё НЕ загружены!

System.out.println("2. Начинаем итерацию...");
for (MyService service : loader) {
    // ТОЛЬКО ЗДЕСЬ происходит загрузка:
    // 1. Class.forName(провайдер)
    // 2. Вызов конструктора
    // 3. Возврат экземпляра
    System.out.println("Loaded: " + service.getClass().getName());
}
```

**Преимущества:**
- Экономия памяти (не создаём неиспользуемые провайдеры)
- Быстрый старт
- Можем прервать итерацию досрочно

### Stream API (Java 9+)

```java
ServiceLoader<PaymentProcessor> loader = ServiceLoader.load(PaymentProcessor.class);

// Фильтрация БЕЗ создания экземпляров!
PaymentProcessor preferred = loader.stream()
    .filter(provider -> {
        // Проверяем имя класса БЕЗ вызова конструктора
        Class<? extends PaymentProcessor> type = provider.type();
        return type.getSimpleName().contains("Stripe");
    })
    .map(ServiceLoader.Provider::get)  // ТОЛЬКО ЗДЕСЬ создаём экземпляр
    .findFirst()
    .orElse(null);

// БЫСТРЕЕ: проверили имена классов → загрузили только нужный
// МЕДЛЕННЕЕ: загрузить все → отфильтровать → взять первый
```

### Перезагрузка провайдеров

```java
ServiceLoader<Plugin> loader = ServiceLoader.load(Plugin.class);

// Первая загрузка
for (Plugin plugin : loader) {
    System.out.println(plugin.getName());
}

// Пользователь добавил новый плагин в classpath
// Перезагружаем
loader.reload();  // Очистить кэш, заново сканировать classpath

// Вторая загрузка - увидим новые плагины
for (Plugin plugin : loader) {
    System.out.println(plugin.getName());
}
```

---

## Интеграция с модульной системой

### Объявления модулей (Java 9+)

```java
// module-info.java для API модуля
module com.example.api {
    // Экспортируем интерфейс
    exports com.example.api;

    // Объявляем что потребляем реализации
    uses com.example.api.PaymentProcessor;
}

// module-info.java для провайдера
module com.example.provider.stripe {
    requires com.example.api;

    // Предоставляем реализацию
    provides com.example.api.PaymentProcessor
        with com.example.provider.stripe.StripePaymentProcessor;

    // Пакет НЕ экспортируется - детали реализации скрыты
}

// Приложение
module com.example.app {
    requires com.example.api;
    // ServiceLoader автоматически найдёт все provides
}
```

**Преимущества модульного подхода:**
- ✅ Не нужны файлы META-INF/services
- ✅ Проверка на этапе компиляции
- ✅ Лучшая инкапсуляция
- ✅ IDE поддержка

**Обратная совместимость:** ServiceLoader поддерживает оба способа (META-INF/services И module-info.java).

---

## Реальные примеры

### Пример 1: JDBC драйверы

```java
// JDBC использует ServiceLoader для автоматической регистрации драйверов

// Старый способ (до Java 6):
Class.forName("org.postgresql.Driver");  // ❌ Больше не нужно

// Новый способ (с Java 6+):
Connection conn = DriverManager.getConnection(
    "jdbc:postgresql://localhost/mydb",
    "user", "password"
);
// ServiceLoader автоматически находит и загружает PostgreSQL драйвер

// Как это работает:
// 1. DriverManager использует ServiceLoader<Driver>
// 2. Находит postgres-driver.jar с META-INF/services/java.sql.Driver
// 3. Загружает org.postgresql.Driver
// 4. Driver регистрирует себя в static блоке
```

### Пример 2: SLF4J логирование

```java
// SLF4J использует SPI для выбора логирования

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// API - всегда одинаковый
Logger log = LoggerFactory.getLogger(MyClass.class);
log.info("Application started");

// Бэкенд - выбирается через ServiceLoader:
// - Если есть logback-classic.jar → используется Logback
// - Если есть log4j-slf4j-impl.jar → используется Log4j2
// - Если ничего нет → простой System.out

// Смена бэкенда:
// 1. Удалить старый JAR (logback-classic.jar)
// 2. Добавить новый JAR (log4j-slf4j-impl.jar)
// 3. ВСЁ! Код приложения НЕ МЕНЯЕТСЯ
```

### Пример 3: Система плагинов

```java
// Интерфейс плагина
public interface EditorPlugin {
    String getName();
    void initialize(EditorContext context);
}

// Менеджер плагинов
public class PluginManager {
    public void loadPlugins() {
        ServiceLoader<EditorPlugin> loader = ServiceLoader.load(EditorPlugin.class);

        for (EditorPlugin plugin : loader) {
            try {
                plugin.initialize(context);
                System.out.println("✓ Loaded: " + plugin.getName());
            } catch (Exception e) {
                // Один сломанный плагин не роняет всё приложение
                System.err.println("✗ Failed to load: " + e.getMessage());
            }
        }
    }
}

// Добавление нового плагина:
// 1. Создать MarkdownPlugin implements EditorPlugin
// 2. Создать META-INF/services/com.example.EditorPlugin
// 3. Скомпилировать в markdown-plugin.jar
// 4. Положить JAR в plugins/
// ВСЁ! Редактор автоматически загрузит плагин при старте
```

---

## Лучшие практики

### 1. Лёгкий конструктор

```java
// ❌ ПЛОХО: Тяжёлый конструктор
public class BadProvider implements MyService {
    public BadProvider() {
        connectToDatabase();         // 100ms
        loadConfiguration();         // 500ms
        initializeThreadPool();      // 50ms
        // ServiceLoader вызовет это для ВСЕХ провайдеров!
    }
}

// ✅ ХОРОШО: Лёгкий конструктор + lazy init
public class GoodProvider implements MyService {
    private Connection conn;

    public GoodProvider() {
        // Ничего не делаем
    }

    private Connection getConnection() {
        if (conn == null) {
            conn = connectToDatabase();  // Только при первом использовании
        }
        return conn;
    }
}
```

### 2. Обработка ошибок

```java
// Загрузка с обработкой ошибок
public static <S> List<S> loadAllSafe(Class<S> serviceClass) {
    List<S> services = new ArrayList<>();
    ServiceLoader<S> loader = ServiceLoader.load(serviceClass);

    for (ServiceLoader.Provider<S> provider : loader.stream().toList()) {
        try {
            S service = provider.get();
            services.add(service);
            System.out.println("✓ Loaded: " + provider.type().getName());
        } catch (ServiceConfigurationError e) {
            // Один сломанный провайдер не роняет всё
            System.err.println("✗ Failed: " + provider.type().getName());
            e.printStackTrace();
        }
    }

    return services;
}
```

### 3. Выбор провайдера

```java
// Приоритизация провайдеров через аннотацию
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface Priority {
    int value();  // Чем больше, тем выше приоритет
}

@Priority(100)  // Высокий приоритет
public class StripeProcessor implements PaymentProcessor { }

@Priority(50)   // Средний приоритет
public class PayPalProcessor implements PaymentProcessor { }

// Сортировка по приоритету
public static <S> List<S> loadSorted(Class<S> serviceClass) {
    return ServiceLoader.load(serviceClass).stream()
        .sorted((a, b) -> {
            int prioA = a.type().getAnnotation(Priority.class).value();
            int prioB = b.type().getAnnotation(Priority.class).value();
            return Integer.compare(prioB, prioA);  // Убывание
        })
        .map(ServiceLoader.Provider::get)
        .toList();
}
```

---

## Частые ошибки

### Ошибка 1: Нет конструктора без параметров

```java
// ❌ НЕПРАВИЛЬНО
public class BrokenProvider implements MyService {
    // Только конструктор с параметрами
    public BrokenProvider(String config) {
        this.config = config;
    }
}

// Результат: ServiceConfigurationError: Provider could not be instantiated

// ✅ ПРАВИЛЬНО
public class CorrectProvider implements MyService {
    private String config;

    // Public конструктор без параметров обязателен
    public CorrectProvider() {
        this.config = "default";
    }

    // Опционально: метод конфигурации
    public void configure(String config) {
        this.config = config;
    }
}
```

### Ошибка 2: Неправильный путь к файлу

```
❌ НЕПРАВИЛЬНО:
- services/MyService
- META/services/MyService
- METAINF/services/MyService

✅ ПРАВИЛЬНО:
- META-INF/services/com.example.MyService
  ↑           ↑     ↑
  Точно так    Дефис  Полное имя интерфейса (FQN)
```

### Ошибка 3: Неправильные имена классов в файле

```
❌ НЕПРАВИЛЬНО (в META-INF/services/com.example.MyService):
MyServiceImpl                    # Нет пакета
com/example/impl/MyServiceImpl   # Слэши вместо точек

✅ ПРАВИЛЬНО:
com.example.impl.MyServiceImpl   # Полное имя с пакетом
```

---

## Производительность

```
Overhead ServiceLoader:

Первый поиск:          ~100-500 μs  (сканирование classpath)
Закэшированный поиск:  ~1-5 μs      (возврат из кэша)
Создание провайдера:   зависит от конструктора

Рекомендации:
✅ Кэшируйте ServiceLoader instance
✅ Используйте stream() для фильтрации до создания
✅ Избегайте тяжёлых конструкторов
✅ Мониторьте производительность в production
```

---

## Чек-лист

### Дизайн SPI
- [ ] Определить чёткий интерфейс сервиса
- [ ] Документировать контракт
- [ ] Продумать версионирование

### Реализация
- [ ] Public конструктор без параметров
- [ ] Лёгкий конструктор (без тяжёлых операций)
- [ ] Обработка ошибок инициализации

### Конфигурация
- [ ] Правильная структура: META-INF/services/
- [ ] Имя файла = FQN интерфейса
- [ ] Содержимое = FQN реализаций (одна на строку)
- [ ] Файл включён в JAR

### Модули (Java 9+)
- [ ] Объявить `uses` в модуле потребителя
- [ ] Объявить `provides...with` в модуле провайдера
- [ ] Экспортировать пакет интерфейса
- [ ] Поддерживать совместимость с classpath

### Производительность
- [ ] Кэшировать ServiceLoader
- [ ] Использовать stream() для фильтрации
- [ ] Профилировать инициализацию
- [ ] Рассмотреть lazy vs eager loading

---

## Связанные темы

- [[design-patterns]] — DI и паттерны расширяемости как альтернативы ServiceLoader
- [[android-dependency-injection]] — DI в Android (Hilt, Koin)
- [[jvm-module-system]] — JPMS интеграция
- [[jvm-class-loader-deep-dive]] — как загружаются провайдеры

---

**Резюме:** ServiceLoader — стандартный механизм Java для обнаружения и загрузки реализаций через SPI. Обеспечивает архитектуру плагинов и слабую связанность. Реальные примеры: JDBC драйверы, SLF4J логирование. Всегда предоставляйте конструкторы без параметров, кэшируйте ServiceLoader instances и обрабатывайте ошибки загрузки.

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "ServiceLoader = Dependency Injection" | ServiceLoader — service discovery, не DI. Нет lifecycle management, scoping, injection. DI frameworks делают больше |
| "ServiceLoader медленный" | Первый поиск ~100-500μs (classpath scan). Кэшированный ~1-5μs. Для startup-time operations это OK |
| "Провайдер должен иметь default constructor" | До Java 9 — да. С JPMS можно использовать static provider method, возвращающий instance |
| "META-INF/services работает с JPMS" | Работает, но для module path нужен `provides...with` в module-info.java. META-INF — fallback для classpath |
| "ServiceLoader потокобезопасен" | Один instance НЕ thread-safe. Создавайте новый ServiceLoader или синхронизируйте доступ |
| "Все провайдеры загружаются сразу" | ServiceLoader lazy — провайдер instantiates только при итерации. stream() позволяет фильтровать до создания |
| "ServiceLoader заменяет Factory pattern" | SPI — для расширяемости (plugins). Factory — для внутреннего создания. Разные use cases |
| "Ошибка в одном провайдере ломает всё" | ServiceConfigurationError для одного провайдера не влияет на другие. Обрабатывайте ошибки при итерации |
| "JDBC драйверы всегда загружаются через ServiceLoader" | С JDBC 4.0+ — да (auto-discovery). До JDBC 4.0 нужен был Class.forName("com.mysql.jdbc.Driver") |
| "ServiceLoader — устаревшая технология" | ServiceLoader живёт и развивается. Java 9 добавила stream(), JPMS интеграцию. Используется в JDK internals |

---

## CS-фундамент

| CS-концепция | Применение в ServiceLoader |
|--------------|---------------------------|
| **Service Locator Pattern** | ServiceLoader реализует Service Locator — runtime discovery сервисов по интерфейсу |
| **Inversion of Control** | Потребитель не знает реализацию — IoC через configuration files / module declarations |
| **Plugin Architecture** | META-INF/services enables plugin systems — добавить JAR = добавить функциональность |
| **Late Binding** | Реализация выбирается в runtime, не в compile-time. Loose coupling |
| **Lazy Initialization** | Провайдеры создаются по требованию — экономия ресурсов при старте |
| **Configuration over Code** | Связь interface→implementation декларативная (файлы/module-info), не hardcoded |
| **Interface Segregation** | Service interface определяет контракт. Implementations могут меняться независимо |
| **Classpath Scanning** | ServiceLoader сканирует META-INF/services на classpath для обнаружения провайдеров |
| **Provider Registration** | Провайдер регистрируется через файл (convention over configuration). Нет central registry |
| **Module Services** | JPMS добавляет явное объявление uses/provides — compile-time проверка зависимостей |

---

## Источники

1. [Oracle: ServiceLoader Javadoc](https://docs.oracle.com/javase/8/docs/api/java/util/ServiceLoader.html) — Официальная документация
2. [Baeldung: Loading JDBC Drivers](https://www.baeldung.com/java-jdbc-loading-drivers) — История загрузки JDBC драйверов
3. [Reflectoring: Implementing Plugins with SPI](https://reflectoring.io/service-provider-interface/) — Практическое руководство по SPI
4. [NorthCoder: Class Loaders and Service Providers](https://northcoder.com/post/class-loaders-service-providers-and/) — Глубокий разбор ServiceLoader и JDBC

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

---
title: "JVM ServiceLoader & SPI - Service Provider Interface"
created: 2025-11-25
modified: 2026-02-13
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
reading_time: 22
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[jvm-class-loader-deep-dive]]"
  - "[[jvm-module-system]]"
  - "[[jvm-reflection-api]]"
related:
  - "[[jvm-class-loader-deep-dive]]"
  - "[[jvm-module-system]]"
  - "[[design-patterns-overview]]"
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

### Аналогия: Lazy Loading как ресторанное меню

> **Представьте:** Вы приходите в ресторан и получаете меню (ServiceLoader). Меню перечисляет все доступные блюда (провайдеры), но кухня не начинает готовить, пока вы не сделаете заказ (итерация). Если вы заказали только суп — остальные блюда не готовятся, экономя ресурсы. А если ресторан добавил новое блюдо (новый JAR на classpath), оно просто появляется в меню без перестройки кухни. Это и есть lazy discovery + lazy instantiation, которые делают ServiceLoader эффективным.

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

- [[design-patterns-overview]] — DI и паттерны расширяемости как альтернативы ServiceLoader
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

## Связь с другими темами

**[[jvm-class-loader-deep-dive]]** — ServiceLoader внутренне использует ClassLoader для обнаружения и загрузки провайдеров: сканирует META-INF/services через ClassLoader.getResources(), затем загружает классы провайдеров через Class.forName() с указанным ClassLoader'ом. Проблемы с ServiceLoader часто связаны с ClassLoader hierarchy: провайдер в child ClassLoader не виден parent'у. Понимание ClassLoader delegation model необходимо для диагностики «ServiceLoader не находит провайдер», особенно в web-контейнерах (Tomcat) с изолированными ClassLoader'ами.

**[[jvm-module-system]]** — JPMS глубоко интегрирован с ServiceLoader через директивы uses/provides в module-info.java. Модульная система добавляет compile-time проверку сервисных зависимостей: если модуль объявляет uses SomeService, но ни один модуль на module path не объявляет provides SomeService — это обнаруживается при сборке. Это эволюция от runtime-обнаружения (META-INF/services) к compile-time-обнаружению (module declarations). Рекомендуется изучить SPI с META-INF/services для понимания основ, затем модульный подход для новых проектов.

**[[design-patterns-overview]]** — ServiceLoader реализует комбинацию нескольких паттернов: Service Locator (runtime обнаружение реализаций), Strategy (выбор реализации по критерию), и Inversion of Control (потребитель не знает о конкретных реализациях). Сравнение ServiceLoader с DI-контейнерами (Spring, Guice) показывает trade-offs: ServiceLoader проще и не требует внешних зависимостей, но не поддерживает lifecycle management, scoping и injection. Для plugin-архитектуры ServiceLoader достаточен; для application wiring — DI-фреймворк лучше.

---

## Источники и дальнейшее чтение

- Bloch J. (2018). *Effective Java*, 3rd Edition. — Item 59 «Know and use the libraries» и Item 1 «Consider static factory methods» описывают паттерны, которые ServiceLoader реализует на уровне платформы, включая service provider framework pattern.
- Parlog N. (2019). *The Java Module System*. — Главы о services in modules подробно описывают интеграцию ServiceLoader с JPMS: uses/provides директивы, provider methods, и миграцию от META-INF/services.
- Evans B., Flanagan D. (2018). *Java in a Nutshell*, 7th Edition. — Практическое описание ServiceLoader API с примерами создания SPI, регистрации провайдеров и обработки ошибок загрузки.

---

## Проверь себя

> [!question]- Почему ServiceLoader не является полноценным DI-контейнером, и в каких случаях его всё равно стоит предпочесть Spring/Guice?
> ServiceLoader обеспечивает только service discovery — нахождение и создание экземпляров по интерфейсу. Он не поддерживает: lifecycle management (нет destroy/close callbacks), scoping (singleton, request, session), injection зависимостей в провайдеры, AOP/proxy, конфигурирование провайдеров. Однако ServiceLoader стоит предпочесть DI-фреймворкам когда: (1) нужна plugin-архитектура с zero-dependency — добавление JAR на classpath автоматически регистрирует провайдер; (2) библиотека не должна тянуть за собой Spring/Guice; (3) использование в JDK-internal (JDBC, SLF4J) где зависимость от внешних фреймворков неприемлема.

> [!question]- Сценарий: вы создаёте систему плагинов для IDE и один из плагинов бросает исключение в конструкторе. Что произойдёт с остальными плагинами при итерации через ServiceLoader?
> Поведение зависит от того, как реализована итерация. При использовании for-each цикла по ServiceLoader, ServiceConfigurationError при создании одного провайдера прервёт итерацию — остальные провайдеры не будут загружены. Правильный подход: использовать stream() API (Java 9+), вызывать provider.get() в try-catch для каждого провайдера отдельно. Тогда ошибка одного плагина логируется, но не влияет на загрузку остальных. Также можно итерировать через Iterator и вызывать next() в try-catch.

> [!question]- Почему конструктор ServiceLoader-провайдера должен быть лёгким, и как обойти это ограничение, если провайдеру нужна тяжёлая инициализация?
> ServiceLoader при итерации вызывает конструктор каждого найденного провайдера. Если конструкторы тяжёлые (подключение к БД, загрузка конфигурации, создание thread pool), то загрузка всех провайдеров займёт значительное время, даже если нужен только один. Решения: (1) использовать lazy initialization — в конструкторе ничего не делать, инициализировать при первом вызове метода; (2) в Java 9+ использовать stream() API с provider.type() для фильтрации по классу без создания экземпляра, и вызывать provider.get() только для нужного; (3) использовать static provider method (JPMS) который может возвращать lightweight proxy.

> [!question]- Как ServiceLoader находит провайдеры на classpath и чем отличается механизм обнаружения в classpath-mode от module-path-mode?
> В classpath-mode: ServiceLoader использует ClassLoader.getResources("META-INF/services/" + serviceInterfaceFQN) для поиска файлов регистрации во всех JAR на classpath. Каждый файл содержит FQN классов-провайдеров, которые загружаются через Class.forName(). В module-path-mode: модуль объявляет provides ServiceInterface with ImplementationClass в module-info.java. Компилятор проверяет корректность на этапе сборки. ServiceLoader получает информацию о провайдерах из module descriptor без сканирования файлов. Преимущества module-path: compile-time проверка, лучшая инкапсуляция (пакет реализации не нужно экспортировать), поддержка static provider methods.

---

## Ключевые карточки

Что такое SPI и чем он отличается от обычного API?
?
API (Application Programming Interface) — контракт, который вызывает потребитель. SPI (Service Provider Interface) — контракт, который реализует провайдер. API определяет "что можно вызвать", SPI определяет "что нужно реализовать". ServiceLoader находит реализации SPI в runtime.

Как зарегистрировать провайдер в classpath-mode?
?
Создать файл META-INF/services/<FQN интерфейса> внутри JAR. Содержимое файла — полные имена классов-реализаций (по одному на строку). Имя файла должно точно совпадать с FQN интерфейса сервиса. Конструктор провайдера — public без параметров.

Чем stream() API (Java 9+) лучше прямой итерации по ServiceLoader?
?
stream() возвращает Stream<ServiceLoader.Provider<S>>, где Provider предоставляет метод type() для получения Class без создания экземпляра. Это позволяет фильтровать провайдеры по классу, аннотациям или имени до вызова get(), экономя ресурсы на создание ненужных экземпляров.

Как ServiceLoader интегрируется с JPMS (Java 9+)?
?
Модуль-потребитель объявляет uses ServiceInterface в module-info.java. Модуль-провайдер объявляет provides ServiceInterface with ImplementationClass. Файлы META-INF/services не нужны. Compile-time проверка корректности. Пакет реализации не нужно экспортировать — детали скрыты.

Какие реальные системы используют ServiceLoader/SPI?
?
JDBC 4.0+ — автоматическая регистрация драйверов (DriverManager использует ServiceLoader<Driver>). SLF4J — обнаружение бэкенда логирования (Logback, Log4j2). Java Cryptography Architecture — провайдеры шифрования. Image I/O — плагины форматов изображений. Charset — провайдеры кодировок.

Почему ServiceLoader instance НЕ thread-safe и как с этим работать?
?
Один экземпляр ServiceLoader кэширует загруженные провайдеры и поддерживает внутреннее состояние итератора. Конкурентный доступ может привести к ConcurrentModificationException или пропуску провайдеров. Решения: создавать отдельный ServiceLoader для каждого потока, синхронизировать доступ через synchronized/Lock, или загрузить все провайдеры в List при инициализации.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубление | [[jvm-class-loader-deep-dive]] | Понять как ClassLoader загружает провайдеры и почему child ClassLoader не виден parent'у |
| Углубление | [[jvm-module-system]] | JPMS uses/provides — compile-time альтернатива META-INF/services |
| Связь | [[jvm-reflection-api]] | ServiceLoader использует рефлексию для создания экземпляров провайдеров |
| Кросс-область | [[design-patterns-overview]] | Service Locator, Strategy, IoC — паттерны, реализуемые ServiceLoader |
| Навигация | [[jvm-overview]] | Вернуться к обзору JVM-тем |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

---
title: "Class Loader: как JVM загружает классы"
created: 2025-11-25
modified: 2026-01-03
tags:
  - jvm
  - class-loader
  - bytecode
type: deep-dive
area: programming
confidence: high
related:
  - "[[jvm-memory-model]]"
  - "[[jvm-bytecode-manipulation]]"
  - "[[jvm-module-system]]"
---

# Class Loader: как JVM загружает классы

> **TL;DR:** ClassLoader загружает .class файлы лениво (при первом использовании). Три встроенных: Bootstrap (java.lang.*) → Platform (javax.*) → Application (ваш код). Parent Delegation = сначала спроси родителя. Это даёт безопасность (нельзя подменить String) и изоляцию (Tomcat = разные ClassLoader для разных webapp). Hot reload работает через создание нового ClassLoader.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Как работает JVM | Понимать роль ClassLoader в архитектуре | [[jvm-basics-history]] |
| Bytecode basics | Что такое .class файл | [[jvm-virtual-machine-concept]] |
| Иерархия классов Java | Наследование, интерфейсы | Любой Java tutorial |

---

# Class Loader: как JVM загружает классы

ClassLoader — подсистема JVM, которая находит .class файлы, верифицирует их безопасность и создаёт объекты классов в памяти. В отличие от C++, где весь код линкуется при компиляции в один исполняемый файл, Java загружает классы лениво — только при первом реальном обращении.

Эта ленивая загрузка открывает мощные возможности: динамическое подключение плагинов без перезапуска приложения, hot reload кода в development, изоляция зависимостей между модулями. Серверы приложений вроде Tomcat используют отдельные ClassLoader для каждого веб-приложения, позволяя им работать с разными версиями библиотек одновременно.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **ClassLoader** | Объект, отвечающий за поиск и загрузку классов | Библиотекарь, который ищет книги по запросу |
| **Bytecode** | Скомпилированный .class файл | Рецепт блюда, записанный в стандартном формате |
| **Loading** | Поиск и чтение .class файла | Библиотекарь нашёл книгу на полке |
| **Linking** | Верификация, подготовка памяти, разрешение ссылок | Проверка книги на подлинность и подготовка места |
| **Initialization** | Выполнение static блоков | Открытие книги и чтение предисловия |
| **Parent Delegation** | Модель делегирования загрузки родительскому ClassLoader | Сначала спроси начальника, потом делай сам |
| **Context ClassLoader** | ClassLoader, привязанный к потоку | VIP-карта, определяющая доступ к ресурсам |
| **Hot Reload** | Перезагрузка классов без рестарта | Замена колеса на ходу, без остановки машины |

---

## Три фазы загрузки класса

Когда JVM впервые встречает ссылку на класс, происходит трёхфазный процесс. Понимание этих фаз помогает диагностировать ошибки вроде `NoClassDefFoundError` или проблемы со static инициализацией.

### Фаза 1: Loading

На этой фазе ClassLoader находит физический .class файл и читает его байты в память. Источником может быть файловая система, JAR-архив, сеть, или даже генерация байткода на лету.

После чтения байтов JVM создаёт объект `java.lang.Class`, который представляет загруженный класс. Этот объект содержит метаинформацию: имя класса, список полей и методов, суперкласс, интерфейсы.

```
.class файл → Чтение байтов → Создание java.lang.Class
             (с диска, JAR,    (объект в Metaspace)
              сети, памяти)
```

Важно: на этом этапе класс ещё не готов к использованию. Static поля не инициализированы, ссылки на другие классы не разрешены.

### Фаза 2: Linking

Linking делится на три подфазы:

**Verification (верификация)** — JVM проверяет, что байткод безопасен и соответствует спецификации. Это защита от вредоносного кода: проверяется, что стек не переполняется, типы используются корректно, нет обращений к приватным полям чужих классов.

Если загрузить модифицированный .class файл с невалидным байткодом, верификация провалится с `VerifyError`. Это одна из причин, почему Java безопаснее C++ — виртуальная машина не доверяет входящему коду.

**Preparation (подготовка)** — JVM выделяет память для static полей класса и присваивает им значения по умолчанию (0, false, null). Не пользовательские значения — именно default values по типу.

```java
class Example {
    static int counter = 42;      // На этапе Preparation: counter = 0
    static String name = "test";  // На этапе Preparation: name = null
}
```

**Resolution (разрешение)** — символические ссылки преобразуются в прямые адреса. Когда ваш код ссылается на `java.util.ArrayList`, в байткоде это текстовая строка. Resolution находит реальный объект класса ArrayList и заменяет символическую ссылку на прямой указатель.

Resolution может происходить лениво (при первом использовании ссылки) или сразу — это зависит от реализации JVM.

### Фаза 3: Initialization

Самая важная для программиста фаза. Здесь выполняются static блоки и присваиваются начальные значения static полям — в порядке их появления в коде.

```java
class Database {
    static {
        System.out.println("Connecting to database...");
        connection = DriverManager.getConnection(url);  // Может бросить Exception!
    }

    static Connection connection;
}
```

**Критический момент:** если static инициализатор бросает исключение, класс помечается как "failed" и все последующие попытки использовать его приведут к `NoClassDefFoundError`, а не к повторной инициализации.

Initialization происходит при первом **активном использовании** класса:
- Создание экземпляра (`new`)
- Вызов static метода
- Обращение к static полю (кроме compile-time констант)
- Reflection: `Class.forName()`
- Инициализация подкласса (сначала инициализируется суперкласс)

```
.class файл → Loading → Linking → Initialization → Готов к использованию
                         │
                         ├─ Verification
                         ├─ Preparation
                         └─ Resolution
```

---

## Иерархия ClassLoaders

JVM использует несколько ClassLoader, организованных в иерархию. Каждый отвечает за загрузку классов из определённых источников.

### Bootstrap ClassLoader

Самый первый ClassLoader, написанный на C++ (не Java). Загружает ядро JDK: `java.lang.*`, `java.util.*`, `java.io.*` и другие фундаментальные классы.

Эти классы находятся в модулях JDK (начиная с Java 9) или в rt.jar (Java 8 и ранее). Когда вы вызываете `String.class.getClassLoader()`, получаете `null` — потому что Bootstrap ClassLoader не представлен Java-объектом.

### Platform ClassLoader (Java 9+) / Extension ClassLoader (Java 8)

Загружает расширения JDK: `javax.*`, `java.sql.*`, `java.security.*`. В Java 8 это был ExtClassLoader, в Java 9+ переименован в Platform ClassLoader.

Находит классы в JDK extension modules. В отличие от Bootstrap, это уже Java-объект.

### Application ClassLoader (System ClassLoader)

Загружает ваш код и ваши зависимости. Источники:
- Classpath (`-cp` или переменная CLASSPATH)
- JAR-файлы вашего приложения
- Maven/Gradle зависимости

Именно этот ClassLoader вы получаете через `ClassLoader.getSystemClassLoader()`.

### Custom ClassLoaders

Вы можете создавать свои ClassLoader для специальных задач: загрузка плагинов из отдельных директорий, шифрованные .class файлы, генерация классов на лету.

```
Bootstrap ClassLoader (C++, загружает java.lang.*, java.util.*)
    │
    ▼
Platform ClassLoader (загружает javax.*, java.sql.*)
    │
    ▼
Application ClassLoader (загружает ваш код и зависимости)
    │
    ▼
Custom ClassLoaders (плагины, изолированные модули)
```

---

## Parent Delegation Model

Когда ClassLoader получает запрос на загрузку класса, он сначала делегирует запрос родителю. Только если родитель не смог найти класс, дочерний ClassLoader пытается загрузить его сам.

Рассмотрим пример: ваш код вызывает `new ArrayList()`.

1. Application ClassLoader получает запрос "загрузи java.util.ArrayList"
2. Вместо самостоятельного поиска, он спрашивает Platform ClassLoader
3. Platform ClassLoader спрашивает Bootstrap ClassLoader
4. Bootstrap ClassLoader: "ArrayList у меня!" → загружает и возвращает класс
5. Класс передаётся вниз по цепочке к вашему коду

**Зачем такая модель?**

**Безопасность:** Вы не можете подменить `java.lang.String` своей версией. Даже если создадите файл `java/lang/String.class` в своём проекте, Application ClassLoader сначала спросит Bootstrap, и Bootstrap загрузит настоящий String.

**Консистентность:** Гарантируется, что базовые классы JDK одинаковы для всего приложения. Нет риска, что разные части кода видят разные версии String.

**Единственный экземпляр:** Класс загружается только один раз (если не используются изолированные ClassLoader). Это важно для static полей и синглтонов.

```
Запрос: "загрузи com.example.MyClass"

Application CL: Есть ли у родителя? → спрашивает Platform CL
Platform CL:    Есть ли у родителя? → спрашивает Bootstrap CL
Bootstrap CL:   Нет, это не мой класс → возвращает null
Platform CL:    Не нашёл в своих источниках → возвращает null
Application CL: Ищу сам в CLASSPATH → нашёл! → загружаю → возвращаю класс
```

---

## Типичные ошибки ClassLoader

### ClassNotFoundException

```java
Class.forName("com.example.MyClass");
// → ClassNotFoundException: com.example.MyClass
```

**Что произошло:** ClassLoader не нашёл .class файл при явном запросе через `Class.forName()` или `ClassLoader.loadClass()`.

**Причины:**
- Класс отсутствует в CLASSPATH
- Опечатка в имени класса
- JAR-файл не добавлен в зависимости

**Диагностика:**
```bash
# Проверить, есть ли класс в JAR
jar -tf mylib.jar | grep MyClass

# Запустить с verbose для отладки
java -verbose:class -cp myapp.jar com.example.Main
```

### NoClassDefFoundError

```java
new MyClass();
// → NoClassDefFoundError: com/example/MyClass
```

**Что произошло:** Класс был доступен при компиляции, но отсутствует или сломан при запуске. Это Error, не Exception — ситуация считается фатальной.

**Разница с ClassNotFoundException:**
- ClassNotFoundException — класс не найден при явном запросе
- NoClassDefFoundError — класс был при компиляции, но нет при запуске, или инициализация провалилась

**Частая скрытая причина — ошибка в static инициализации:**

```java
class DatabaseConfig {
    static {
        // Это бросит exception при первой загрузке
        Connection conn = DriverManager.getConnection("bad-url");
    }
}

// Первый вызов:
new DatabaseConfig();  // → ExceptionInInitializerError

// Все последующие вызовы:
new DatabaseConfig();  // → NoClassDefFoundError (класс помечен как failed)
```

JVM не повторяет инициализацию — если она провалилась один раз, класс считается непригодным навсегда (до перезапуска JVM).

### ClassCastException между "одинаковыми" классами

```java
ClassLoader cl1 = new URLClassLoader(urls);
ClassLoader cl2 = new URLClassLoader(urls);

Object obj = cl1.loadClass("com.example.User").newInstance();
User user = (User) obj;  // ClassCastException!
```

**Что произошло:** Класс загружен двумя разными ClassLoader. Для JVM это два **разных** класса, даже если они имеют одинаковое имя и идентичный байткод.

**Правило идентичности класса:** Класс уникально идентифицируется парой (ClassLoader, FullyQualifiedName). Два ClassLoader — два разных класса.

**Когда возникает:**
- Плагинные системы с изолированными ClassLoader
- OSGi контейнеры
- Web-приложения в сервлетных контейнерах (каждый webapp имеет свой ClassLoader)

**Решение:** Использовать общий ClassLoader для типов, которые нужно передавать между модулями, или работать через интерфейсы из общего родительского ClassLoader.

---

## Custom ClassLoader

Создание собственного ClassLoader позволяет контролировать источник и обработку классов.

### Зачем нужен

- **Плагины:** Загружать расширения из отдельных директорий, не добавляя их в основной CLASSPATH
- **Hot reload:** Создавать новый ClassLoader для перезагрузки изменённых классов без рестарта
- **Изоляция:** Позволять разным модулям использовать разные версии библиотек
- **Защита:** Расшифровывать зашифрованные .class файлы

### Пример реализации

```java
public class PluginClassLoader extends ClassLoader {

    private final Path pluginDir;

    public PluginClassLoader(Path pluginDir, ClassLoader parent) {
        super(parent);
        this.pluginDir = pluginDir;
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        // Преобразуем имя класса в путь к файлу
        // com.example.Plugin → com/example/Plugin.class
        String path = name.replace('.', '/') + ".class";
        Path classFile = pluginDir.resolve(path);

        if (!Files.exists(classFile)) {
            throw new ClassNotFoundException(name);
        }

        try {
            byte[] bytes = Files.readAllBytes(classFile);
            // defineClass() — защищённый метод ClassLoader,
            // который превращает байты в объект Class
            return defineClass(name, bytes, 0, bytes.length);
        } catch (IOException e) {
            throw new ClassNotFoundException(name, e);
        }
    }
}

// Использование
Path pluginsDir = Paths.get("/app/plugins");
ClassLoader pluginLoader = new PluginClassLoader(pluginsDir,
                                                  getClass().getClassLoader());

// Загружаем и создаём экземпляр плагина
Class<?> pluginClass = pluginLoader.loadClass("com.plugin.MyPlugin");
Plugin plugin = (Plugin) pluginClass.getDeclaredConstructor().newInstance();
plugin.execute();
```

Обратите внимание: метод `loadClass()` (унаследованный) реализует parent delegation — сначала спросит родителя. Метод `findClass()` вызывается только если родитель не нашёл класс.

### Практические сценарии Custom ClassLoader

**Сценарий 1: Hot Reload в Development**

```java
/**
 * ClassLoader для hot reload - перезагружает классы без перезапуска JVM.
 * Важно: каждый раз создаём НОВЫЙ ClassLoader, потому что
 * существующий ClassLoader не может перезагрузить уже загруженный класс.
 */
public class HotReloadClassLoader extends ClassLoader {
    private final Path classPath;
    private final Set<String> reloadablePackages;

    public HotReloadClassLoader(Path classPath, Set<String> packages, ClassLoader parent) {
        super(parent);
        this.classPath = classPath;
        this.reloadablePackages = packages;
    }

    @Override
    public Class<?> loadClass(String name) throws ClassNotFoundException {
        // Перехватываем загрузку только для наших пакетов
        // Остальные делегируем родителю
        if (shouldReload(name)) {
            return findClass(name);  // Загружаем сами, НЕ спрашивая родителя!
        }
        return super.loadClass(name);  // Стандартная делегация
    }

    private boolean shouldReload(String name) {
        return reloadablePackages.stream().anyMatch(name::startsWith);
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        Path classFile = classPath.resolve(name.replace('.', '/') + ".class");
        try {
            byte[] bytes = Files.readAllBytes(classFile);
            return defineClass(name, bytes, 0, bytes.length);
        } catch (IOException e) {
            throw new ClassNotFoundException(name, e);
        }
    }
}

// Использование
public class DevServer {
    private volatile HotReloadClassLoader currentLoader;

    public void reload() {
        // Создаём НОВЫЙ ClassLoader - старые классы остаются в памяти
        // пока на них есть ссылки (GC соберёт когда станут unreachable)
        currentLoader = new HotReloadClassLoader(
            Paths.get("target/classes"),
            Set.of("com.myapp.handlers", "com.myapp.services"),
            getClass().getClassLoader()
        );

        // Загружаем и пересоздаём обработчики
        Class<?> handlerClass = currentLoader.loadClass("com.myapp.handlers.RequestHandler");
        this.handler = (Handler) handlerClass.getDeclaredConstructor().newInstance();
    }
}
```

**Сценарий 2: Изоляция версий библиотек (Multi-tenant)**

```java
/**
 * Каждый tenant использует свою версию библиотек.
 * Похоже на то, как работают servlet containers (Tomcat, Jetty).
 */
public class TenantClassLoader extends URLClassLoader {
    private final String tenantId;
    private final Set<String> sharedPackages;  // Общие для всех tenants

    public TenantClassLoader(String tenantId, URL[] urls, ClassLoader parent) {
        super(urls, parent);
        this.tenantId = tenantId;
        this.sharedPackages = Set.of(
            "com.myapp.api",      // API интерфейсы - общие
            "com.myapp.shared"    // Shared types - общие
        );
    }

    @Override
    protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
        synchronized (getClassLoadingLock(name)) {
            // 1. Проверяем, уже ли загружен
            Class<?> c = findLoadedClass(name);
            if (c != null) return c;

            // 2. Java core классы - всегда родителю
            if (name.startsWith("java.") || name.startsWith("javax.")) {
                return getParent().loadClass(name);
            }

            // 3. Shared packages - родителю (единая версия для всех)
            if (isSharedPackage(name)) {
                return getParent().loadClass(name);
            }

            // 4. Tenant-specific - сначала ищем у себя, потом у родителя
            //    (обратный порядок! child-first)
            try {
                c = findClass(name);
            } catch (ClassNotFoundException e) {
                c = getParent().loadClass(name);
            }

            if (resolve) resolveClass(c);
            return c;
        }
    }

    private boolean isSharedPackage(String name) {
        return sharedPackages.stream().anyMatch(name::startsWith);
    }
}

// Использование
public class TenantManager {
    private final Map<String, TenantClassLoader> tenantLoaders = new ConcurrentHashMap<>();

    public TenantClassLoader getOrCreate(String tenantId) {
        return tenantLoaders.computeIfAbsent(tenantId, id -> {
            URL[] urls = getTenantLibraries(id);  // Библиотеки конкретного tenant
            return new TenantClassLoader(id, urls, getClass().getClassLoader());
        });
    }

    // Освобождение ресурсов при удалении tenant
    public void removeTenant(String tenantId) throws IOException {
        TenantClassLoader loader = tenantLoaders.remove(tenantId);
        if (loader != null) {
            loader.close();  // URLClassLoader.close() освобождает JAR handles
        }
    }
}
```

**Сценарий 3: Расшифровка защищённого кода**

```java
/**
 * Загружает зашифрованные .class файлы (защита от декомпиляции).
 * Реальная защита требует native agent, это упрощённый пример.
 */
public class DecryptingClassLoader extends ClassLoader {
    private final Path encryptedPath;
    private final Cipher cipher;

    public DecryptingClassLoader(Path path, SecretKey key, ClassLoader parent)
            throws GeneralSecurityException {
        super(parent);
        this.encryptedPath = path;
        this.cipher = Cipher.getInstance("AES/GCM/NoPadding");
        this.cipher.init(Cipher.DECRYPT_MODE, key);
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        Path encrypted = encryptedPath.resolve(name.replace('.', '/') + ".class.enc");

        try {
            byte[] encryptedBytes = Files.readAllBytes(encrypted);
            byte[] decrypted = cipher.doFinal(encryptedBytes);
            return defineClass(name, decrypted, 0, decrypted.length);
        } catch (Exception e) {
            throw new ClassNotFoundException("Cannot decrypt " + name, e);
        }
    }
}
```

**Когда НЕ стоит использовать Custom ClassLoader:**

| Ситуация | Почему не нужен Custom ClassLoader |
|----------|-----------------------------------|
| Простая модульность | Используйте Java Modules (JPMS) |
| Разные версии для тестов | Maven/Gradle dependency scopes |
| Динамическая загрузка JAR | `URLClassLoader` достаточен |
| Изоляция в микросервисах | Отдельные процессы надёжнее |

---

## Context ClassLoader

Thread Context ClassLoader — механизм для фреймворков и библиотек, которым нужно загружать классы, определённые пользователем.

### Проблема

Представьте: вы используете ServiceLoader для поиска реализаций интерфейса. ServiceLoader — часть JDK, загружен Bootstrap ClassLoader. Но реализации находятся в вашем коде, загруженном Application ClassLoader.

Bootstrap ClassLoader не видит Application ClassLoader — он выше в иерархии. Как ServiceLoader найдёт ваши реализации?

### Решение

Thread Context ClassLoader — способ "передать" ClassLoader вниз по стеку вызовов:

```java
// Фреймворк или библиотека:
ClassLoader contextCL = Thread.currentThread().getContextClassLoader();
ServiceLoader<MyService> loader = ServiceLoader.load(MyService.class, contextCL);
```

По умолчанию Context ClassLoader установлен в Application ClassLoader. Вы можете изменить его для специальных случаев:

```java
ClassLoader original = Thread.currentThread().getContextClassLoader();
try {
    Thread.currentThread().setContextClassLoader(myPluginClassLoader);
    // Теперь фреймворки будут использовать myPluginClassLoader
    runFrameworkCode();
} finally {
    Thread.currentThread().setContextClassLoader(original);
}
```

---

## Отладка проблем с ClassLoader

### Определить, кто загрузил класс

```java
Class<?> clazz = MyClass.class;
ClassLoader cl = clazz.getClassLoader();

System.out.println("Class: " + clazz.getName());
System.out.println("ClassLoader: " + cl);
System.out.println("Source: " + clazz.getProtectionDomain()
                                     .getCodeSource()
                                     .getLocation());
```

Вывод покажет полный путь к JAR или директории, откуда загружен класс — критически полезно при конфликтах версий.

### JVM флаги для отладки

```bash
# Показать каждую загрузку класса
java -verbose:class MyApp

# Вывод:
# [Loaded java.lang.Object from jrt:/java.base]
# [Loaded com.example.MyClass from file:/app.jar]

# Более детально (Java 9+)
java -Xlog:class+load=info MyApp
```

### Найти дубликаты классов

Конфликты возникают, когда один класс присутствует в нескольких JAR:

```bash
# Поиск класса во всех JAR
for jar in lib/*.jar; do
  jar -tf "$jar" | grep -q "com/example/MyClass.class" && echo "$jar"
done

# Если нашли в нескольких — порядок в CLASSPATH определяет, какой загрузится
```

---

## Java 9+ Module System

Начиная с Java 9, модульная система (JPMS) добавляет ещё один уровень контроля над видимостью классов.

Модули явно декларируют, какие пакеты они экспортируют и какие модули требуют. Даже если класс физически находится в модуле, он может быть недоступен для reflection без директивы `opens`.

```
Java 8:
  Bootstrap → Extension → Application
  (всё видят всё через reflection)

Java 9+:
  Bootstrap → Platform → Application
      │
      └── Module Layer (контроль exports/opens)
```

Подробнее: [[jvm-module-system]]

---

## Чеклист диагностики

```
□ ClassNotFoundException: класс в CLASSPATH?
  → jar -tf lib/*.jar | grep ClassName

□ NoClassDefFoundError: класс был при компиляции?
  → Проверить static initializers на exceptions
  → Проверить зависимости в runtime vs compile time

□ ClassCastException между "одинаковыми" классами:
  → obj.getClass().getClassLoader() — один ли ClassLoader?

□ LinkageError: конфликт версий?
  → Найти дубликаты классов в разных JAR

□ Включить отладку: java -verbose:class MyApp
□ Найти источник: clazz.getProtectionDomain().getCodeSource()
```

---

## Кто использует и реальные примеры

| Технология | Как использует ClassLoader | Зачем |
|------------|---------------------------|-------|
| **Tomcat/Jetty** | Отдельный ClassLoader для каждого webapp | Изоляция: webapp A с Guava 28 и webapp B с Guava 31 одновременно |
| **OSGi** | Динамические модули с собственными ClassLoader | Enterprise (Eclipse, IntelliJ IDEA plugins) |
| **Spring DevTools** | Два ClassLoader: restartLoader + baseLoader | Fast restart: перезагружаем только ваш код, не библиотеки |
| **JRebel** | Bytecode instrumentation + custom ClassLoader | Hot reload в development: сохранил файл → код обновился |
| **HotswapAgent** | Open-source альтернатива JRebel | Бесплатный hot reload с поддержкой Spring, Hibernate |
| **Minecraft mods** | Custom ClassLoader для загрузки модов | Расширяемость игры без доступа к исходникам |

### Spring DevTools: как работает fast restart

```
Первый запуск:
baseClassLoader → библиотеки (Spring, Hibernate, etc.) — НЕ перезагружается
restartClassLoader → ваш код (com.myapp.*) — перезагружается

При изменении файла:
1. Старый restartClassLoader выбрасывается
2. Создаётся новый restartClassLoader
3. Ваш код загружается заново
4. Приложение "перезапускается" за 1-2 секунды вместо 30-60
```

---

## Рекомендуемые источники

### Документация
- [JVM Specification: Loading, Linking, Initializing](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-5.html) — официальная спецификация
- [ClassLoader javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ClassLoader.html) — API документация

### Статьи
- [JVM Internals: ClassLoaders](https://blog.jamesdbloom.com/JVMInternals.html) — глубокий разбор
- [Understanding Class Loading](https://www.baeldung.com/java-classloaders) — Baeldung tutorial
- [Live Reloading on JVM](https://seroperson.me/2025/11/28/jvm-live-reload/) — современный обзор hot reload

### Инструменты
- [Spring DevTools](https://docs.spring.io/spring-boot/reference/using/devtools.html) — официальный hot reload для Spring
- [JRebel](https://www.jrebel.com/) — коммерческий hot reload
- [HotswapAgent](https://github.com/HotswapProjects/HotswapAgent) — open-source альтернатива

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Класс загружается при запуске программы" | Класс загружается **lazy** — только при первом обращении. JVM использует отложенную загрузку для экономии памяти и быстрого старта. `Class.forName()` или первый вызов статического метода триггерит загрузку |
| "Parent ClassLoader физически содержит child" | Это **делегирование**, не наследование. Parent и child — отдельные объекты, связанные через ссылку. Child делегирует загрузку parent'у, но сам parent не знает о child'ах |
| "System ClassLoader загружает всё из classpath" | System ClassLoader (Application CL) загружает только из `-cp`. Платформенные классы грузит Platform CL, а bootstrap классы (java.lang.*) — Bootstrap CL, написанный на C++ |
| "Два класса с одинаковым именем — это один класс" | Класс уникален парой **(имя + ClassLoader)**. `com.app.User` от ClassLoader A и от ClassLoader B — это два РАЗНЫХ типа, несовместимых при присваивании |
| "ClassNotFoundException = класс не существует" | Это значит, что ClassLoader не нашёл класс **в своей иерархии**. Класс может существовать в другом ClassLoader (например, в дочернем или параллельном) |
| "Custom ClassLoader = сложно и не нужно" | IDE (IntelliJ), серверы (Tomcat), frameworks (Spring) активно используют custom ClassLoader'ы. Это основа hot reload, модульности и изоляции |
| "Загруженный класс нельзя выгрузить" | Класс выгружается когда **нет ссылок** ни на ClassLoader, ни на объекты класса. GC собирает и ClassLoader, и загруженные им классы |
| "Bootstrap ClassLoader можно получить через getClassLoader()" | `String.class.getClassLoader()` возвращает **null**. Bootstrap CL — это native код JVM, не Java объект. null здесь означает "bootstrap" |
| "Все классы в JAR загружаются одним ClassLoader" | Зависит от контекста. В Tomcat каждый WAR имеет свой ClassLoader. В OSGi каждый bundle может иметь свой. В обычном приложении — да, все из одного JAR грузит System CL |
| "ClassLoader работает одинаково во всех JVM" | Есть нюансы: GraalVM Native Image требует все классы на этапе компиляции, модульная система Java 9+ добавила Platform CL, механизм изменился. Специфика реализации может отличаться |

---

## CS-фундамент

| CS-концепция | Применение в ClassLoader |
|--------------|-------------------------|
| **Lazy Loading** | Классы загружаются on-demand, не все сразу при старте. Это экономит память и ускоряет запуск — особенно критично для больших приложений с тысячами классов |
| **Delegation Pattern** | Паттерн делегирования: child ClassLoader сначала спрашивает parent, только потом ищет сам. Обеспечивает приоритет системных классов над пользовательскими |
| **Namespace Isolation** | Каждый ClassLoader создаёт своё пространство имён. Это позволяет загрузить несколько версий библиотеки одновременно (Guava 28 и Guava 31 в разных webapp) |
| **Linking (Verification, Preparation, Resolution)** | После loading класс проходит linking: bytecode verification (безопасность), preparation (выделение памяти для static полей), resolution (связывание символических ссылок) |
| **Graph Theory (DAG)** | Иерархия ClassLoader'ов — направленный ациклический граф. Parent-first делегирование обеспечивает отсутствие циклов и предсказуемый порядок поиска |
| **Caching / Memoization** | Загруженный класс кэшируется в ClassLoader. Повторные вызовы loadClass() возвращают закэшированный Class<?> объект мгновенно |
| **Reference Counting & GC** | ClassLoader и его классы выгружаются GC когда нет reachable ссылок. Это основа hot reload: создаём новый ClassLoader, старый собирается GC |
| **Visibility / Access Control** | ClassLoader определяет видимость: дочерний видит классы parent'а, но не наоборот. Это односторонняя visibility, критичная для безопасности |
| **Binary Compatibility** | JVM проверяет совместимость классов при загрузке. Если интерфейс изменился несовместимо, получаем NoSuchMethodError / IncompatibleClassChangeError |
| **Symbol Resolution** | Символические ссылки (имена классов, методов) резолвятся в конкретные адреса при первом использовании. Это позволяет загружать классы независимо |

---

## Связи

- [[jvm-memory-model]] — где хранятся загруженные классы (Metaspace)
- [[jvm-bytecode-manipulation]] — как модифицировать классы при загрузке
- [[jvm-module-system]] — JPMS и модульная система Java 9+
- [[jvm-reflection-api]] — доступ к загруженным классам через reflection

---

*Проверено: 2026-01-09 | Источники: Oracle JVM Spec, Baeldung, Spring docs — Педагогический контент проверен*

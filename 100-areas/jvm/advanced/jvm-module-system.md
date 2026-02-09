---
title: "Java Module System (JPMS): Модульность и инкапсуляция"
created: 2025-11-25
modified: 2025-11-25
tags:
  - jvm
  - modules
  - jpms
  - jigsaw
  - java9
type: note
area: programming
confidence: 4
sources:
  - "The Java Module System" by Nicolai Parlog (2019)
  - "Java 9 Modularity" by Sander Mak & Paul Bakker (2017)
  - "JEP 261: Module System"
  - "Oracle Java Platform Module System Documentation"
---

# Java Module System (JPMS): Модульность и инкапсуляция

> Java 9 Module System (Project Jigsaw) — крупнейшее изменение платформы за 20 лет. Модульность вместо Classpath Hell.

---

## TL;DR

**Java Module System (JPMS) — система модулей, введённая в Java 9.**

Ключевые концепции:
- **Module** — единица инкапсуляции выше package
- **module-info.java** — дескриптор модуля
- **exports** — явное объявление публичных API
- **requires** — явное объявление зависимостей
- **Strong encapsulation** — доступ только к экспортированным пакетам

Преимущества:
- ✅ Явные зависимости (нет скрытых)
- ✅ Надёжная инкапсуляция (нельзя обойти)
- ✅ Меньше размер приложений (только нужные модули)
- ✅ Быстрый старт (меньше загрузка)

Проблемы:
- ❌ Breaking changes для legacy кода
- ❌ Reflection ограничен (нет доступа к internal API)
- ❌ Сложность migration с classpath

---

## Проблема: Classpath Hell

### До Java 9: Classpath

```bash
java -cp app.jar:lib/guava.jar:lib/commons-lang.jar:lib/jackson.jar:... Main
```

**Проблемы:**

**1. Нет инкапсуляции пакетов**
```java
// В library.jar есть internal package:
package com.library.internal;
public class InternalUtils { ... }

// Приложение может использовать internal API:
import com.library.internal.InternalUtils;
public class MyApp {
    public void run() {
        InternalUtils.hack();  // НЕ ДОЛЖНО РАБОТАТЬ, НО РАБОТАЕТ!
    }
}

// Библиотека обновляется → internal API изменился → приложение сломалось
```

**2. Неявные зависимости**
```
app.jar зависит от library-v1.jar
library-v1.jar зависит от commons-v1.jar (но это не указано явно!)

Разработчик:
  java -cp app.jar:library-v1.jar Main
  → ClassNotFoundException: commons.Utils (забыли добавить commons!)

Решение: добавить все транзитивные зависимости вручную
  java -cp app.jar:library-v1.jar:commons-v1.jar:... Main
```

**3. Jar Hell (Duplicate Classes)**
```
app.jar содержит:  com.example.Utils (v1)
lib.jar содержит:  com.example.Utils (v2)

java -cp app.jar:lib.jar Main

Какая версия загрузится? Первая в classpath!
  → app.jar version (v1)

Поменяли порядок:
java -cp lib.jar:app.jar Main
  → lib.jar version (v2)

Недетерминированное поведение!
```

**4. Всё в одном namespace**
```
-cp app.jar:lib1.jar:lib2.jar:lib3.jar:...

Все классы видны всем!
  - lib1 видит internal классы lib2
  - lib2 видит internal классы lib3
  - Нет изоляции
```

---

## Решение: Module System

### Концепция модуля

**Module — единица инкапсуляции с явными границами.**

```
До Java 9 (package):
  ┌─────────────────────────────────┐
  │  Package com.example.api        │
  │    - public class User          │  → Видны всем!
  │    - public class UserService   │  → Видны всем!
  └─────────────────────────────────┘
  ┌─────────────────────────────────┐
  │  Package com.example.internal   │
  │    - public class InternalUtils │  → Тоже видны всем!
  └─────────────────────────────────┘

Java 9+ (module):
  ┌─────────────────────────────────────────────────┐
  │  Module com.example.app                         │
  │                                                  │
  │  exports com.example.api;  ← Только этот package│
  │                                                  │
  │  ┌───────────────────────────────────────────┐ │
  │  │ Package com.example.api (exported)        │ │  → Видны снаружи
  │  │   - public class User                     │ │
  │  │   - public class UserService              │ │
  │  └───────────────────────────────────────────┘ │
  │  ┌───────────────────────────────────────────┐ │
  │  │ Package com.example.internal (не exported)│ │  → Скрыты!
  │  │   - public class InternalUtils            │ │
  │  └───────────────────────────────────────────┘ │
  └─────────────────────────────────────────────────┘

Даже public class InternalUtils недоступен снаружи модуля!
```

---

## module-info.java: Дескриптор модуля

### Базовый пример

```
Структура проекта:
my-app/
  ├── module-info.java
  └── com/
      └── example/
          ├── api/
          │   └── UserService.java
          └── internal/
              └── DatabaseUtils.java
```

**module-info.java:**
```java
module com.example.app {
    // Экспортируем public API
    exports com.example.api;

    // com.example.internal НЕ экспортирован → недоступен снаружи

    // Зависимости
    requires java.sql;
    requires com.library.utils;
}
```

**Что это даёт:**
- Только `com.example.api` доступен другим модулям
- `com.example.internal` скрыт (даже public классы!)
- Явно указаны зависимости: `java.sql`, `com.library.utils`

---

### Директивы module-info.java

**1. exports**
```java
module com.example.app {
    // Экспортировать package для всех
    exports com.example.api;

    // Экспортировать только для конкретных модулей
    exports com.example.internal to com.example.tests;
}
```

**2. requires**
```java
module com.example.app {
    // Обязательная зависимость
    requires java.sql;

    // Transitive зависимость (re-export)
    requires transitive com.library.utils;
    // → Модули, зависящие от com.example.app, автоматически видят com.library.utils

    // Опциональная зависимость
    requires static com.google.guava;
    // → Compile-time нужен, runtime опционально
}
```

**3. opens (для Reflection)**
```java
module com.example.app {
    // Разрешить Reflection доступ к package
    opens com.example.internal to com.fasterxml.jackson.databind;
    // → Jackson может использовать Reflection для сериализации

    // Открыть для всех
    opens com.example.dto;
}
```

**4. uses / provides (ServiceLoader)**
```java
module com.example.app {
    // Декларируем использование сервиса
    uses com.example.spi.PluginInterface;
}

module com.example.plugin {
    // Предоставляем реализацию
    provides com.example.spi.PluginInterface
        with com.example.plugin.MyPluginImpl;
}
```

---

## Миграция с Classpath на Modules

### Bottom-Up Migration

**Стратегия:** Модульизировать зависимости снизу вверх.

```
Шаг 1: Legacy приложение на classpath
  app.jar
    └── depends on: library.jar
                      └── depends on: utils.jar

Все на classpath (Java 8):
  java -cp app.jar:library.jar:utils.jar Main

Шаг 2: Модульизировать utils.jar
  utils.jar → module com.library.utils

Шаг 3: Модульизировать library.jar
  library.jar → module com.library.api
    requires com.library.utils;

Шаг 4: Модульизировать app.jar
  app.jar → module com.example.app
    requires com.library.api;

Шаг 5: Запуск как модули (Java 9+)
  java --module-path mods --module com.example.app/com.example.Main
```

---

### Unnamed Module (Compatibility)

**Java 9+ поддерживает смешанный режим: modules + classpath.**

```
Unnamed Module:
  - Все JAR на classpath попадают в "unnamed module"
  - Unnamed module читает ВСЕ модули
  - Unnamed module экспортирует ВСЕ пакеты

┌───────────────────────────────────────────────────┐
│  Module Path (--module-path)                      │
│                                                    │
│  module com.example.app {                         │
│      requires java.sql;                           │
│      requires com.library.api;                    │
│  }                                                 │
└───────────────┬───────────────────────────────────┘
                │ can read
                ▼
┌───────────────────────────────────────────────────┐
│  Classpath (--class-path)                         │
│                                                    │
│  <unnamed module>                                 │
│    - legacy-lib.jar                               │
│    - commons-lang.jar                             │
│    - ...все legacy JARs...                        │
│                                                    │
│  → Читает ВСЕ модули                              │
│  → Экспортирует ВСЕ packages                      │
└───────────────────────────────────────────────────┘
```

**Запуск:**
```bash
java --module-path mods \
     --class-path legacy/commons-lang.jar:legacy/guava.jar \
     --module com.example.app/com.example.Main
```

---

### Automatic Modules

**JAR без module-info.java на module path → automatic module.**

```bash
# guava.jar не имеет module-info.java
# Положили на module-path:
java --module-path mods:libs/guava.jar --module com.example.app

# JVM автоматически создаёт модуль:
#   - Имя модуля = имя JAR (guava)
#   - Экспортирует ВСЕ packages
#   - Читает ВСЕ модули (named + unnamed)
```

**module-info.java приложения:**
```java
module com.example.app {
    requires guava;  // Automatic module
}
```

**Проблемы:**
- Имя модуля нестабильно (зависит от имени JAR)
- Экспортирует всё (нет инкапсуляции)

**Решение:** Указать имя модуля в MANIFEST.MF:
```
Automatic-Module-Name: com.google.guava
```

---

## JDK Modules

### Структура JDK 9+

**До Java 9:**
```
JDK/
  └── lib/
      └── rt.jar (60MB) — всё в одном JAR!
          - java.lang.*
          - java.util.*
          - java.sql.*
          - javax.swing.*
          - ...ВСЁ...
```

**Java 9+:**
```
JDK/
  └── jmods/  (модули)
      ├── java.base.jmod          (Core: String, Object, etc.)
      ├── java.sql.jmod           (JDBC)
      ├── java.desktop.jmod       (Swing, AWT)
      ├── java.xml.jmod           (XML parsing)
      ├── jdk.compiler.jmod       (javac)
      ├── jdk.jshell.jmod         (JShell REPL)
      └── ...90+ модулей...
```

**Главные модули:**

| Модуль | Содержимое |
|--------|------------|
| `java.base` | Core классы (автоматически required всеми) |
| `java.sql` | JDBC API |
| `java.xml` | XML, SAX, DOM |
| `java.logging` | java.util.logging |
| `java.desktop` | Swing, AWT, JavaFX |
| `java.net.http` | HTTP Client (Java 11+) |
| `jdk.compiler` | javac компилятор |
| `jdk.jfr` | Java Flight Recorder |

---

### Dependency Graph

```
                    ┌──────────────┐
                    │  java.base   │  ← Все модули зависят
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │java.sql │      │java.xml  │      │java.     │
   │         │      │          │      │logging   │
   └────┬────┘      └─────┬────┘      └──────────┘
        │                 │
        ▼                 ▼
   ┌─────────────────────────────┐
   │  java.sql.rowset            │
   └─────────────────────────────┘
```

**Посмотреть зависимости:**
```bash
jdeps --module java.sql

# Output:
# java.sql
#   requires java.base
#   requires java.logging
#   requires java.xml
```

---

## jlink: Создание custom runtime

### Проблема: Огромный JDK

```
JDK 21 full:  ~160 MB
Приложение использует только:
  - java.base (core)
  - java.sql (JDBC)
  - java.logging

Зачем распространять весь JDK?
```

### Решение: jlink

**jlink создаёт минимальный runtime с только нужными модулями.**

```bash
# Создать custom runtime
jlink --module-path $JAVA_HOME/jmods:mods \
      --add-modules com.example.app \
      --output custom-runtime

# Результат:
custom-runtime/
  ├── bin/
  │   └── java  (исполняемый файл)
  ├── conf/
  ├── legal/
  └── lib/  (~30-50MB вместо 160MB!)
```

**Запуск:**
```bash
./custom-runtime/bin/java -m com.example.app/com.example.Main
```

**Преимущества:**
- Меньший размер (30-50MB вместо 160MB)
- Быстрый старт (меньше модулей для загрузки)
- Security (меньше attack surface)

**Реальный пример:**
```bash
# Минимальное приложение (только java.base)
jlink --module-path $JAVA_HOME/jmods \
      --add-modules java.base \
      --output minimal-runtime

du -sh minimal-runtime
# → 28M

# С java.sql + java.logging
jlink --module-path $JAVA_HOME/jmods \
      --add-modules java.base,java.sql,java.logging \
      --output sql-runtime

du -sh sql-runtime
# → 42M

# Полный JDK
du -sh $JAVA_HOME
# → 165M
```

---

## Strong Encapsulation

### Запрет доступа к internal API

**До Java 9:**
```java
// Приложение использует internal JDK API
import sun.misc.Unsafe;

public class MyApp {
    public void hack() {
        Unsafe unsafe = Unsafe.getUnsafe();  // РАБОТАЛО!
        // Direct memory access
    }
}
```

**Java 9+:**
```java
import sun.misc.Unsafe;

public class MyApp {
    public void hack() {
        Unsafe unsafe = Unsafe.getUnsafe();  // ERROR!
        // IllegalAccessError: module java.base does not export sun.misc
    }
}
```

**Почему?**

```java
// jdk.unsupported module
module jdk.unsupported {
    exports sun.misc;  // Только для совместимости
}

// НО java.base НЕ экспортирует sun.misc!
module java.base {
    // sun.misc НЕ exported
}
```

---

### Обход через --add-exports (temporary fix)

```bash
# Разрешить доступ к internal package (НЕ РЕКОМЕНДУЕТСЯ!)
java --add-exports java.base/sun.misc=ALL-UNNAMED \
     -cp app.jar Main
```

**Альтернативы:**
- Использовать public API
- VarHandle вместо Unsafe (Java 9+)
- Foreign Memory API (Java 14+)

---

## Reflection и Modules

### Проблема: Reflection ограничен

```java
// До Java 9: Reflection работал везде
Class<?> clazz = Class.forName("sun.misc.Unsafe");
Field field = clazz.getDeclaredField("theUnsafe");
field.setAccessible(true);  // РАБОТАЛО
Object unsafe = field.get(null);

// Java 9+: Reflection не работает с non-exported packages
field.setAccessible(true);  // InaccessibleObjectException!
```

---

### opens directive

**Разрешить Reflection для конкретных модулей:**

```java
module com.example.app {
    // Обычный export (код доступен)
    exports com.example.api;

    // Opens (только Reflection доступен)
    opens com.example.internal to
        com.fasterxml.jackson.databind,
        org.hibernate.core;

    // Opens для всех
    opens com.example.dto;
}
```

**Использование:**

```java
// Jackson может десериализовать даже private поля
module com.example.app {
    opens com.example.dto to com.fasterxml.jackson.databind;
}

// DTO с private полями
package com.example.dto;
public class User {
    private String name;  // Jackson может получить доступ!
    private int age;
}

// Jackson использует Reflection
ObjectMapper mapper = new ObjectMapper();
User user = mapper.readValue(json, User.class);  // Работает!
```

---

### --add-opens (runtime override)

```bash
# Открыть package для Reflection
java --add-opens java.base/java.lang=ALL-UNNAMED \
     -cp app.jar Main
```

**Когда нужно:**
- Legacy библиотеки используют Reflection
- Нет возможности изменить module-info.java

---

## Build Tools Integration

### Maven и Modules

**Структура проекта:**
```
my-app/
  ├── pom.xml
  └── src/
      └── main/
          ├── java/
          │   ├── module-info.java
          │   └── com/example/app/
          │       └── Main.java
          └── resources/
```

**pom.xml:**
```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
    </properties>

    <build>
        <plugins>
            <!-- Maven Compiler Plugin 3.11+ поддерживает modules -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
            </plugin>

            <!-- jlink для создания custom runtime -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jlink-plugin</artifactId>
                <version>3.1.0</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>jlink</goal>
                        </goals>
                    </execution>
                </executions>
                <configuration>
                    <launcher>my-app-launcher</launcher>
                    <compress>2</compress> <!-- Максимальная компрессия -->
                    <stripDebug>true</stripDebug>
                </configuration>
            </plugin>
        </plugins>
    </build>

    <dependencies>
        <!-- Dependency с module support -->
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <version>32.1.3-jre</version>
        </dependency>
    </dependencies>
</project>
```

**Что происходит:**
- Maven автоматически распознаёт `module-info.java`
- Зависимости с `Automatic-Module-Name` в MANIFEST.MF работают как модули
- jlink-plugin создаёт custom runtime в `target/image/`

**Результат:**
```bash
mvn clean package

# Создан custom runtime:
target/image/
  ├── bin/
  │   └── my-app-launcher  (исполняемый файл)
  └── lib/
      └── modules  (~30-50MB)

# Запуск:
./target/image/bin/my-app-launcher
```

**Метрики:**
- Full JDK: 165MB
- Custom runtime: 42MB (3.9x меньше)
- Startup time: 1.2s → 0.6s (2x быстрее)

---

### Gradle и Modules

**build.gradle:**
```groovy
plugins {
    id 'java'
    id 'application'
}

java {
    modularity.inferModulePath = true  // Автоматически определять module path
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

application {
    mainModule = 'com.example.app'
    mainClass = 'com.example.app.Main'
}

dependencies {
    implementation 'com.google.guava:guava:32.1.3-jre'
}

// jlink задача
tasks.register('customRuntime', JavaExec) {
    group = 'build'
    description = 'Create custom runtime with jlink'

    doLast {
        exec {
            commandLine 'jlink',
                '--module-path', "${System.getProperty('java.home')}/jmods:${configurations.runtimeClasspath.asPath}",
                '--add-modules', 'com.example.app',
                '--launcher', 'my-app=com.example.app/com.example.app.Main',
                '--output', 'build/custom-runtime',
                '--compress', '2',
                '--strip-debug'
        }
    }
}
```

**Запуск:**
```bash
./gradlew customRuntime

# Результат:
build/custom-runtime/
  └── bin/
      └── my-app

./build/custom-runtime/bin/my-app
```

---

## Split Packages Проблема

### Что такое Split Package?

**Split Package — когда один package распределён по нескольким модулям.**

```
Модуль A:
  com.example.utils.StringUtils
  com.example.utils.DateUtils

Модуль B:
  com.example.utils.FileUtils  ← ТОТ ЖЕ package!

❌ Split package: com.example.utils в обоих модулях!
```

**Почему это проблема в JPMS?**

```java
// Модуль A
module com.example.a {
    exports com.example.utils;
}

// Модуль B
module com.example.b {
    exports com.example.utils;  // ERROR!
    // "Package com.example.utils is declared in modules com.example.a and com.example.b"
}
```

**JPMS запрещает split packages!**

---

### Реальный пример: java.xml

```
До Java 9:
  rt.jar содержал:
    - javax.xml.bind.*     (часть JDK)
    - org.w3c.dom.*        (часть JDK)

  JAXB JAR содержал:
    - javax.xml.bind.*     (та же package!)

Split package в classpath работал (первый в classpath побеждал),
но в modules — НЕТ!
```

**Решение в Java 9:**
```
JDK modules:
  - java.xml          (org.w3c.dom.*)
  - java.xml.bind     (javax.xml.bind.*)  ← Deprecated в Java 9, удалён в Java 11

JAXB external library (Jakarta XML Binding):
  - jakarta.xml.bind.*  (новый package name!)
```

---

### Как решить Split Packages

**1. Переименовать packages**
```java
// Модуль A
package com.example.utils.string;  // Уникальный subpackage
public class StringUtils { ... }

// Модуль B
package com.example.utils.file;    // Уникальный subpackage
public class FileUtils { ... }
```

**2. Объединить в один модуль**
```
Модуль com.example.utils:
  - com.example.utils.StringUtils
  - com.example.utils.DateUtils
  - com.example.utils.FileUtils
```

**3. Переместить классы в разные packages**
```java
// Модуль A
package com.example.string;
public class StringUtils { ... }

// Модуль B
package com.example.file;
public class FileUtils { ... }
```

---

## Cyclic Dependencies

### Проблема: Циклические зависимости

```
Модуль A требует модуль B
Модуль B требует модуль A

┌─────────┐
│ Module A│──requires──▶┌─────────┐
│         │             │ Module B│
│         │◀──requires──│         │
└─────────┘             └─────────┘

❌ Циклическая зависимость!
```

**JPMS запрещает циклы!**

**Пример:**
```java
// Module A
module com.example.a {
    exports com.example.a;
    requires com.example.b;  // A требует B
}

// Module B
module com.example.b {
    exports com.example.b;
    requires com.example.a;  // B требует A → ERROR!
}

// Ошибка компиляции:
// "Cyclic dependence involving com.example.a"
```

---

### Решение 1: Создать общий модуль

```
┌─────────┐               ┌─────────┐
│ Module A│──requires──▶  │ Module  │
│         │               │ Common  │
└─────────┘               └────┬────┘
                               │
                               ▲
┌─────────┐                    │
│ Module B│────requires────────┘
└─────────┘
```

**Реализация:**
```java
// Module Common (shared interfaces)
module com.example.common {
    exports com.example.common;
}

package com.example.common;
public interface Service { ... }

// Module A
module com.example.a {
    requires com.example.common;
    exports com.example.a;
    provides com.example.common.Service with com.example.a.ServiceA;
}

// Module B
module com.example.b {
    requires com.example.common;
    exports com.example.b;
    uses com.example.common.Service;  // Использует ServiceA через ServiceLoader
}
```

**Преимущества:**
- Нет цикла
- Common модуль содержит interfaces/abstractions
- A и B зависят от abstractions, не друг от друга

---

### Решение 2: ServiceLoader (Dependency Inversion)

```java
// Module API (interfaces)
module com.example.api {
    exports com.example.api;
}

package com.example.api;
public interface UserService {
    User findUser(int id);
}

// Module Implementation
module com.example.impl {
    requires com.example.api;
    provides com.example.api.UserService
        with com.example.impl.UserServiceImpl;
}

// Module Consumer
module com.example.app {
    requires com.example.api;
    uses com.example.api.UserService;  // НЕ требует impl модуль!
}

// Использование
ServiceLoader<UserService> loader = ServiceLoader.load(UserService.class);
UserService service = loader.findFirst().orElseThrow();
User user = service.findUser(123);
```

**Преимущества:**
- Loose coupling через interfaces
- app модуль НЕ знает о impl модуле
- Runtime dependency injection без цикла

---

## Multi-Release JARs

### Проблема: Поддержка старых Java версий

```
Библиотека должна работать на Java 8 + Java 9+:
  - Java 8: нет modules, classpath
  - Java 9+: есть modules, module path

Как распространить одну библиотеку для обеих версий?
```

### Решение: Multi-Release JAR (MRJAR)

**Multi-Release JAR — JAR с разными версиями классов для разных Java версий.**

**Структура:**
```
my-library.jar
  ├── META-INF/
  │   ├── MANIFEST.MF
  │   └── versions/
  │       ├── 9/
  │       │   ├── module-info.class  ← Только для Java 9+
  │       │   └── com/example/
  │       │       └── FastImpl.class  ← Java 9+ версия
  │       └── 11/
  │           └── com/example/
  │               └── FasterImpl.class  ← Java 11+ версия
  └── com/
      └── example/
          ├── Main.class  ← Java 8+ версия (base)
          └── FastImpl.class  ← Java 8 fallback
```

**MANIFEST.MF:**
```
Manifest-Version: 1.0
Multi-Release: true
Automatic-Module-Name: com.example.library
```

**Что происходит:**
- Java 8: Использует `com/example/FastImpl.class` (base version)
- Java 9: Использует `META-INF/versions/9/com/example/FastImpl.class` + `module-info.class`
- Java 11: Использует `META-INF/versions/11/com/example/FasterImpl.class`

---

### Maven создание MRJAR

**pom.xml:**
```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.11.0</version>
            <executions>
                <!-- Java 8 base version -->
                <execution>
                    <id>default-compile</id>
                    <configuration>
                        <release>8</release>
                    </configuration>
                </execution>

                <!-- Java 9 version with module-info -->
                <execution>
                    <id>java9-compile</id>
                    <phase>compile</phase>
                    <goals>
                        <goal>compile</goal>
                    </goals>
                    <configuration>
                        <release>9</release>
                        <compileSourceRoots>
                            <compileSourceRoot>${project.basedir}/src/main/java9</compileSourceRoot>
                        </compileSourceRoots>
                        <outputDirectory>${project.build.outputDirectory}/META-INF/versions/9</outputDirectory>
                    </configuration>
                </execution>

                <!-- Java 11 version -->
                <execution>
                    <id>java11-compile</id>
                    <phase>compile</phase>
                    <goals>
                        <goal>compile</goal>
                    </goals>
                    <configuration>
                        <release>11</release>
                        <compileSourceRoots>
                            <compileSourceRoot>${project.basedir}/src/main/java11</compileSourceRoot>
                        </compileSourceRoots>
                        <outputDirectory>${project.build.outputDirectory}/META-INF/versions/11</outputDirectory>
                    </configuration>
                </execution>
            </executions>
        </plugin>

        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-jar-plugin</artifactId>
            <version>3.3.0</version>
            <configuration>
                <archive>
                    <manifestEntries>
                        <Multi-Release>true</Multi-Release>
                        <Automatic-Module-Name>com.example.library</Automatic-Module-Name>
                    </manifestEntries>
                </archive>
            </configuration>
        </plugin>
    </plugins>
</build>
```

**Структура проекта:**
```
src/
  ├── main/
  │   ├── java/          (Java 8 base)
  │   │   └── com/example/
  │   │       └── Main.java
  │   ├── java9/         (Java 9 версия)
  │   │   ├── module-info.java
  │   │   └── com/example/
  │   │       └── FastImpl.java
  │   └── java11/        (Java 11 версия)
  │       └── com/example/
  │           └── FasterImpl.java
```

**Результат:**
```bash
mvn clean package

# Создан MRJAR:
target/my-library-1.0.jar

# Проверка:
jar -tf my-library-1.0.jar
# META-INF/MANIFEST.MF (Multi-Release: true)
# com/example/Main.class
# com/example/FastImpl.class
# META-INF/versions/9/module-info.class
# META-INF/versions/9/com/example/FastImpl.class
# META-INF/versions/11/com/example/FasterImpl.class
```

**Использование:**
```bash
# Java 8: Использует base version
java -cp my-library.jar com.example.Main

# Java 9+: Использует version 9 (с module support)
java --module-path my-library.jar --module com.example.library/com.example.Main

# Java 11+: Использует version 11 (самая оптимизированная)
```

**Реальные примеры MRJAR:**
- **Guava 31+**: Java 8 base + Java 11 версия
- **Jackson 2.13+**: Java 8 base + Java 9 модули
- **Netty 4.1+**: Java 8 + Java 9 оптимизации

---

## Production Case Study: Microservice с Modules

### Проблема

```
Microservice на Spring Boot 3.2:
  - Fat JAR: 85MB
  - Docker image: 280MB (openjdk:21)
  - Startup time: 3.2s
  - Memory: 512MB базовый heap

Цель: Уменьшить размер и ускорить старт
```

### Решение: Модули + jlink

**1. Модульная структура:**
```
com.example.user-service/
  ├── module-info.java
  └── com/example/userservice/
      ├── UserServiceApplication.java
      ├── controller/
      ├── service/
      └── repository/
```

**module-info.java:**
```java
module com.example.userservice {
    // Spring требует открытых packages для component scanning
    opens com.example.userservice to spring.core, spring.beans;
    opens com.example.userservice.controller to spring.core, spring.beans, spring.web;
    opens com.example.userservice.service to spring.core, spring.beans;
    opens com.example.userservice.repository to spring.core, spring.beans, spring.data.jpa;

    // Export public API
    exports com.example.userservice.dto;

    // Dependencies
    requires spring.boot;
    requires spring.boot.autoconfigure;
    requires spring.web;
    requires spring.data.jpa;
    requires java.sql;
    requires java.naming;  // Для JNDI (если используется)
    requires java.instrument;  // Для Spring AOP

    // Jackson для JSON
    requires com.fasterxml.jackson.databind;
    opens com.example.userservice.dto to com.fasterxml.jackson.databind;
}
```

**2. jlink custom runtime:**
```bash
# Собрать приложение
mvn clean package

# Создать custom runtime с jlink
jlink \
  --module-path $JAVA_HOME/jmods:target/libs \
  --add-modules com.example.userservice \
  --add-modules jdk.crypto.ec \
  --add-modules jdk.crypto.cryptoki \
  --launcher userservice=com.example.userservice/com.example.userservice.UserServiceApplication \
  --output target/custom-runtime \
  --compress=2 \
  --strip-debug \
  --no-header-files \
  --no-man-pages
```

**3. Dockerfile:**
```dockerfile
# Stage 1: Build
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package

# Stage 2: Create custom runtime with jlink
FROM eclipse-temurin:21-jdk AS jlink
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
RUN jlink \
    --module-path $JAVA_HOME/jmods:/app/app.jar \
    --add-modules com.example.userservice \
    --output /custom-runtime \
    --compress=2 \
    --strip-debug

# Stage 3: Runtime image
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=jlink /custom-runtime ./jre
COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["./jre/bin/java", "-m", "com.example.userservice/com.example.userservice.UserServiceApplication"]
```

**Результаты:**

| Метрика | До (Fat JAR) | После (Modules + jlink) | Улучшение |
|---------|--------------|-------------------------|-----------|
| JAR размер | 85MB | 85MB | - |
| Docker image | 280MB | 92MB | **3.0x меньше** |
| JRE размер | 165MB | 38MB | **4.3x меньше** |
| Startup time | 3.2s | 1.8s | **1.8x быстрее** |
| Memory baseline | 512MB | 380MB | **25% меньше** |
| Module count | ~90 | 15 | **6x меньше** |

**Почему быстрее:**
- Меньше модулей → меньше class loading
- Меньше JDK классов → быстрее JIT warm-up
- Меньше memory footprint → меньше GC паузы

**Production метрики (после деплоя):**
```
Kubernetes pod:
  - Replicas: 3
  - Memory limit: 512MB → 384MB (savings: 128MB * 3 = 384MB)
  - Image pull time: 18s → 6s (3x faster deployment)
  - Cold start p95: 4.1s → 2.3s (1.8x faster)
```

---

## Когда использовать Modules

### ✅ Подходящие случаи

**1. Новые проекты**
- Начинать с модулей с самого начала
- Явные зависимости → меньше ошибок
- Лучшая инкапсуляция

**2. Библиотеки**
```java
// Чёткий public API
module com.library.api {
    exports com.library.api;
    // internal packages скрыты
}
```

**3. Большие monolith приложения**
```
Разбить на модули:
  - com.example.core
  - com.example.api
  - com.example.persistence
  - com.example.web

Каждый модуль — чёткие границы
```

**4. Microservices**
- Каждый сервис = модуль
- jlink для создания минимальных docker images

---

### ❌ Когда НЕ стоит

**1. Legacy приложения с Reflection-heavy кодом**
- Spring, Hibernate используют Reflection
- Нужны многочисленные `opens`

**2. Приложения с большим количеством legacy зависимостей**
- Библиотеки без module support
- Много automatic modules

**3. Rapid prototyping**
- Overhead на настройку module-info.java
- Classpath проще для быстрых экспериментов

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Modules обязательны в Java 9+" | Modules опциональны. Classpath работает как раньше — unnamed module автоматически видит все packages. Migration path гибкий |
| "JPMS заменяет Maven/Gradle modules" | JPMS — runtime encapsulation, Maven — build-time dependency management. Они дополняют друг друга, не конкурируют |
| "Automatic modules полностью совместимы" | Automatic modules не объявляют requires — они видят всё. Это workaround для legacy, не полноценная модульность |
| "exports делает package полностью публичным" | exports открывает только compile-time доступ. Reflection требует отдельного `opens`. Можно экспортировать API, но скрыть internals от reflection |
| "Module нельзя использовать с Spring/Hibernate" | Можно, но требует `opens` для reflection. Spring 6+ имеет native module support. Сложность в legacy dependencies |
| "jlink создаёт полностью статичный executable" | jlink создаёт custom runtime image с выбранными модулями. JVM всё ещё нужна — это не GraalVM native-image |
| "Все JDK internal API недоступны" | До Java 16 были warnings. С Java 16+ strong encapsulation — доступ закрыт. Но `--add-opens` позволяет обойти (use case: legacy code) |
| "Module descriptor читается каждый раз" | module-info.class парсится при загрузке модуля. После загрузки информация в памяти — никаких повторных чтений |
| "requires transitive всегда нужен для API types" | Только если тип используется в сигнатуре public API. Internal use не требует transitive. Минимизируйте transitive dependencies |
| "Modules решают все проблемы versioning" | JPMS не поддерживает версионирование! Нельзя загрузить две версии одного модуля. OSGi решает это, JPMS — нет |

---

## CS-фундамент

| CS-концепция | Применение в JPMS |
|--------------|-------------------|
| **Information Hiding** | exports/opens реализуют Parnas' principle — модули скрывают implementation details, открывая только необходимый API |
| **Dependency Graph** | Module graph = DAG (directed acyclic graph). JVM строит граф при запуске, проверяет отсутствие циклов |
| **Strong Encapsulation** | JPMS обеспечивает compile-time AND runtime encapsulation — недоступные packages невидимы даже через reflection |
| **Namespace Management** | Modules решают split package problem — один package в одном модуле. Уникальность через module boundaries |
| **Separate Compilation** | module-info.java компилируется отдельно, определяя interface модуля. Изменение implementation не требует recompilation dependents |
| **Linking** | jlink реализует link-time optimization — удаление неиспользуемых модулей при сборке custom runtime |
| **Access Control Matrix** | exports to / opens to реализуют fine-grained ACL — разные модули имеют разные права на package |
| **Service Locator Pattern** | uses/provides реализуют Service Locator — модуль объявляет какие сервисы использует и предоставляет |
| **Interface Segregation** | exports разделяет public API от internal implementation. Каждый package — отдельный "interface" |
| **Transitive Closure** | requires transitive вычисляет transitive closure зависимостей — клиент автоматически видит dependencies своих dependencies |

---

## Связанные темы

- [[jvm-class-loader-deep-dive]] — Platform ClassLoader загружает modules
- [[jvm-basics-history]] — Архитектура JVM и байткод
- [[jvm-reflection-api]] — Reflection ограничен module boundaries
- [[jvm-service-loader-spi]] — ServiceLoader интегрирован с JPMS (uses/provides)
- [[java-modern-features]] — Modules появились в Java 9

---

## Чеклист: Module System

**Базовое понимание:**
- [ ] Понимаю проблемы Classpath (Hell, no encapsulation)
- [ ] Знаю, что такое модуль (unit of encapsulation)
- [ ] Умею создать module-info.java
- [ ] Понимаю директивы: exports, requires, opens

**Migration:**
- [ ] Знаю разницу named / unnamed / automatic modules
- [ ] Понимаю bottom-up migration стратегию
- [ ] Умею запускать смешанный режим (modules + classpath)
- [ ] Знаю про --add-exports и --add-opens

**JDK Modules:**
- [ ] Понимаю структуру JDK 9+ (jmods)
- [ ] Знаю основные модули (java.base, java.sql, etc.)
- [ ] Умею использовать jlink для custom runtime
- [ ] Понимаю strong encapsulation (internal API закрыты)

**Production:**
- [ ] Знаю, когда стоит использовать modules
- [ ] Понимаю проблемы с Reflection
- [ ] Умею настроить opens для frameworks
- [ ] Знаю про jdeps для анализа зависимостей

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

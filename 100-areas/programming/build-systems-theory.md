---
title: "Build Systems: от Make до Gradle"
created: 2026-01-09
modified: 2026-01-09
type: concept
status: published
confidence: high
tags:
  - programming/build
  - topic/devops
  - gradle
  - make
  - type/concept
  - level/intermediate
related:
  - "[[module-systems]]"
  - "[[dependency-resolution]]"
  - "[[ci-cd-pipelines]]"
prerequisites:
  - "[[module-systems]]"
  - "[[dependency-resolution]]"
---

# Build Systems: от Make до Gradle

> **TL;DR:** Build system автоматизирует превращение исходного кода в исполняемый артефакт. Make (1976) — первая система, работает с файлами и timestamps. Gradle (современный) — декларативный DSL, умный кэш, инкрементальная сборка. Главная задача: собрать МИНИМУМ того, что изменилось.

---

## Интуиция: 5 аналогий

### 1. Build как рецепт приготовления

```
РЕЦЕПТ ТОРТА:
  1. Взбить яйца (если не взбиты)
  2. Добавить муку (зависит от шага 1)
  3. Испечь (зависит от шага 2)
  4. Украсить (зависит от шага 3)

BUILD ФАЙЛ:
  1. Скомпилировать src/*.kt (если изменились)
  2. Создать JAR (зависит от .class файлов)
  3. Запустить тесты (зависит от JAR)
  4. Создать Docker image (зависит от тестов)

Build система = повар, который знает рецепт и не делает лишнего
```

### 2. Incremental build как умный повар

```
ГЛУПЫЙ ПОВАР:
  Гость: "Добавь соль в суп"
  Повар: Выливает суп, готовит заново с нуля

УМНЫЙ ПОВАР (инкрементальная сборка):
  Гость: "Добавь соль в суп"
  Повар: Добавляет соль (только то, что нужно)

Gradle/Bazel = умный повар
- Отслеживает что изменилось
- Пересобирает ТОЛЬКО изменённое
- Кэширует результаты
```

### 3. Dependency graph как дерево сборки

```
                        APP.jar
                           │
              ┌────────────┼────────────┐
              │            │            │
          core.jar    data.jar     ui.jar
              │            │            │
         kotlin-std    room.jar   compose.jar
              │            │            │
              └────────────┼────────────┘
                           │
                      kotlin-std

Изменился core.jar → пересобрать core.jar + APP.jar
Изменился kotlin-std → пересобрать ВСЁ
```

### 4. Task как единица работы

```
┌─────────────────────────────────────────────────┐
│                    TASK                          │
│                                                  │
│  Inputs:     src/main/kotlin/*.kt               │
│  Outputs:    build/classes/*.class              │
│  Action:     kotlinc (компилятор)               │
│                                                  │
│  Если inputs не изменились → UP-TO-DATE         │
│  Если outputs в кэше → FROM-CACHE               │
│  Иначе → выполнить action                       │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 5. Build cache как общая память

```
ЛОКАЛЬНЫЙ КЭШ:
  Я вчера собирал module A → результат в ~/.gradle/caches
  Сегодня module A не изменился → взять из кэша

REMOTE КЭШ (CI):
  Коллега собрал module A → результат на сервере
  Я pull → взять из remote cache
  → Экономия времени всей команды

  Developer 1 ──────► Remote Cache ◄────── Developer 2
       │                   │                    │
       │                   │                    │
       └─────── CI Server ─┴────────────────────┘
```

---

## Исторический контекст

Первой build-системой стал **Make**, созданный Stuart Feldman в Bell Labs в 1976 году. Make решал конкретную проблему: при изменении одного файла пересобирать только зависящие от него части, используя timestamps файлов и граф зависимостей (Makefile). За Make Feldman получил ACM Software System Award (2003).

В Java-мире build-системы прошли три поколения. **Apache Ant** (2000) перенёс идеи Make в XML-формат, но остался императивным — разработчик описывал "как" собирать. **Maven** (Jason van Zyl, 2004) совершил revolution, введя convention-over-configuration: стандартная структура каталогов, lifecycle phases и централизованные репозитории артефактов (Maven Central). **Gradle** (Hans Dockter, 2007) объединил декларативность Maven с гибкостью Groovy/Kotlin DSL, добавив incremental build и build cache.

Параллельно Google внутренне разработал Blaze (2005), опубликованный как **Bazel** (2015) — build-систему с hermetic builds (полная изоляция от окружения) и remote execution, рассчитанную на монорепозитории с миллионами файлов. Facebook создал **Buck** (2013) для мобильной разработки. В JavaScript-экосистеме появились **Turborepo** и **Nx** (2020+) для управления монорепозиториями.

```
1976: Make (файлы, timestamps)
        │
1999: Ant (XML, Java-centric)
        │
2004: Maven (conventions, dependency management)
        │
2007: Gradle (DSL, incremental, flexible)
        │
2015: Bazel (Google, hermetic, remote execution)
        │
2020+: Turborepo, Nx (monorepo, JS ecosystem)
```

### Сравнение

| Система | Парадигма | Сильные стороны | Слабые стороны |
|---------|-----------|-----------------|----------------|
| **Make** | Императивная | Простота, везде есть | Нет dependency management |
| **Maven** | Декларативная | Conventions, репозитории | Негибкий, XML |
| **Gradle** | Декларативная + scripting | Гибкость, кэш, KTS | Сложность, learning curve |
| **Bazel** | Декларативная, hermetic | Масштаб, воспроизводимость | Сложность настройки |

---

## Gradle: современный стандарт

### Основные концепции

```kotlin
// build.gradle.kts

// 1. Plugins — расширяют функциональность
plugins {
    kotlin("jvm") version "2.0.0"
    application
}

// 2. Dependencies — внешние библиотеки
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")
    testImplementation(kotlin("test"))
}

// 3. Tasks — единицы работы
tasks.register("hello") {
    doLast {
        println("Hello from Gradle!")
    }
}

// 4. Configurations — группы зависимостей
configurations {
    create("myConfig") {
        extendsFrom(configurations.implementation.get())
    }
}
```

### Task Dependencies

```kotlin
// Явные зависимости
tasks.named("build") {
    dependsOn("test", "assemble")
}

// Неявные через inputs/outputs
tasks.register("generateCode") {
    inputs.file("schema.json")
    outputs.dir("generated/")

    doLast {
        // Генерация кода
    }
}

tasks.named("compileKotlin") {
    dependsOn("generateCode")  // Сначала генерация
}
```

### Incremental Build

```kotlin
// Gradle отслеживает:
// 1. Inputs — если не изменились, task UP-TO-DATE
// 2. Outputs — если в кэше, task FROM-CACHE

tasks.register<Copy>("copyDocs") {
    from("src/docs")           // Input
    into("build/docs")          // Output
    include("**/*.md")

    // Gradle автоматически:
    // - Копирует только изменённые файлы
    // - Пропускает, если ничего не изменилось
}
```

### Build Cache

```kotlin
// settings.gradle.kts
buildCache {
    local {
        directory = File(rootDir, ".gradle/build-cache")
        removeUnusedEntriesAfterDays = 30
    }

    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/")
        isPush = System.getenv("CI") != null
        credentials {
            username = System.getenv("CACHE_USER")
            password = System.getenv("CACHE_PASS")
        }
    }
}
```

---

## Частые ошибки: 6 проблем

### ❌ Ошибка 1: Task не кэшируется

**Симптом:** Task всегда выполняется, даже без изменений

```kotlin
// ПЛОХО — нет inputs/outputs:
tasks.register("badTask") {
    doLast {
        val timestamp = System.currentTimeMillis()  // Каждый раз разный!
        File("output.txt").writeText("Generated at $timestamp")
    }
}

// ХОРОШО — детерминированные inputs/outputs:
tasks.register("goodTask") {
    inputs.files(fileTree("src"))
    outputs.file("build/output.txt")

    doLast {
        val content = inputs.files.joinToString("\n") { it.readText() }
        outputs.files.singleFile.writeText(content)
    }
}
```

**Решение:** Всегда объявляй inputs и outputs. Task без них не кэшируется.

---

### ❌ Ошибка 2: Configuration time vs Execution time

**Симптом:** Build медленный даже для `./gradlew help`

```kotlin
// ПЛОХО — код выполняется при конфигурации:
tasks.register("slowConfig") {
    val files = fileTree("src").files  // ❌ Сканирует FS сейчас!
    println("Found ${files.size} files")  // ❌ Каждый build!
}

// ХОРОШО — ленивое выполнение:
tasks.register("fastConfig") {
    val files = fileTree("src")  // Ленивый, не сканирует сразу

    doLast {  // Выполняется только когда task запущен
        println("Found ${files.files.size} files")
    }
}
```

**Решение:** Тяжёлые операции — в `doLast {}` или `doFirst {}`.

---

### ❌ Ошибка 3: Циклические зависимости tasks

**Симптом:** `Circular dependency between tasks`

```kotlin
// ПЛОХО:
tasks.named("taskA") {
    dependsOn("taskB")
}
tasks.named("taskB") {
    dependsOn("taskA")  // ❌ Цикл!
}

// ХОРОШО — выделить общую часть:
tasks.register("sharedSetup") {
    // Общая подготовка
}

tasks.named("taskA") {
    dependsOn("sharedSetup")
}
tasks.named("taskB") {
    dependsOn("sharedSetup")
}
```

**Решение:** Разбить циклические зависимости на отдельные tasks.

---

### ❌ Ошибка 4: Игнорирование configuration cache

**Симптом:** Build медленный, configuration занимает много времени

```kotlin
// ПЛОХО — нарушение configuration cache:
tasks.register("broken") {
    val env = System.getenv("MY_VAR")  // ❌ Читает environment в configuration time

    doLast {
        println(env)
    }
}

// ХОРОШО — через Provider:
tasks.register("correct") {
    val env = providers.environmentVariable("MY_VAR")

    doLast {
        println(env.get())  // Читает в execution time
    }
}
```

**Решение:** Используй `providers.*` для environment, properties, files.

---

### ❌ Ошибка 5: Monolithic build.gradle

**Симптом:** 1000+ строк в одном файле, сложно понять

```kotlin
// ПЛОХО — всё в одном файле
// build.gradle.kts (1500 строк)
plugins { /* 20 плагинов */ }
dependencies { /* 100 зависимостей */ }
tasks.register("task1") { /* ... */ }
// ... ещё 50 tasks

// ХОРОШО — разбить на convention plugins:
// buildSrc/src/main/kotlin/my-kotlin-library.gradle.kts
plugins {
    kotlin("jvm")
}

dependencies {
    testImplementation(kotlin("test"))
}

// build.gradle.kts
plugins {
    id("my-kotlin-library")  // Чистый, понятный
}
```

**Решение:** Convention plugins в buildSrc или отдельном проекте.

---

### ❌ Ошибка 6: Неправильное использование version catalogs

**Симптом:** Дублирование версий, конфликты

```toml
# ПЛОХО — версии везде разные:
# module-a/build.gradle.kts
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.0")
# module-b/build.gradle.kts
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")  # Конфликт!

# ХОРОШО — централизованный version catalog:
# gradle/libs.versions.toml
[versions]
coroutines = "1.8.0"

[libraries]
coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }

# build.gradle.kts
dependencies {
    implementation(libs.coroutines.core)  # Единая версия везде
}
```

**Решение:** Используй Version Catalog (libs.versions.toml).

---

## Ментальные модели

### 1. DAG (Directed Acyclic Graph)

```
Build = DAG of tasks

        ┌─────────┐
        │  clean  │
        └────┬────┘
             │
        ┌────▼────┐
        │ compile │
        └────┬────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼───┐┌───▼───┐┌───▼───┐
│ test  ││  jar  ││ docs  │
└───┬───┘└───┬───┘└───┬───┘
    │        │        │
    └────────┼────────┘
             │
        ┌────▼────┐
        │  build  │
        └─────────┘

Gradle выполняет в правильном порядке
Параллельно где возможно
```

### 2. Inputs → Action → Outputs

```
Каждый task:

  INPUTS          ACTION          OUTPUTS
  ┌─────┐        ┌──────┐        ┌─────┐
  │.kt  │───────►│kotlinc│───────►│.class│
  │files│        │       │        │files │
  └─────┘        └──────┘        └─────┘

Если INPUTS не изменились → не выполнять ACTION
Если OUTPUTS в кэше → взять из кэша
```

### 3. Configuration vs Execution phases

```
GRADLE BUILD LIFECYCLE:

1. INITIALIZATION
   - Читает settings.gradle.kts
   - Определяет какие проекты участвуют

2. CONFIGURATION
   - Выполняет build.gradle.kts
   - Строит DAG tasks
   - НЕ выполняет task actions!

3. EXECUTION
   - Выполняет запрошенные tasks
   - В порядке зависимостей
   - Параллельно где можно
```

---

## Проверь себя

**Вопрос 1:** Почему Gradle быстрее Maven для повторных сборок?

<details>
<summary>Ответ</summary>

1. **Incremental build:** Gradle отслеживает inputs/outputs каждого task и пропускает UP-TO-DATE tasks.

2. **Build cache:** Результаты tasks кэшируются локально и удалённо.

3. **Daemon:** Gradle daemon держит JVM "тёплой" между сборками.

4. **Parallel execution:** Tasks без зависимостей выполняются параллельно.

Maven перевыполняет все фазы lifecycle каждый раз.
</details>

**Вопрос 2:** Что произойдёт, если task не объявит outputs?

<details>
<summary>Ответ</summary>

Task без outputs:
- Не будет кэшироваться
- Будет выполняться КАЖДЫЙ раз
- Не может быть UP-TO-DATE

Gradle не знает, что считать результатом работы task, поэтому не может определить, нужно ли его перевыполнять.
</details>

---

## Связь с другими темами

**[[module-systems]]** — Build system и module system тесно связаны: build system должна понимать границы модулей, порядок компиляции и visibility rules. Gradle multi-project build напрямую отражает модульную структуру проекта. JPMS (Java Platform Module System) добавляет module-info.java, который build system обрабатывает при компиляции. Правильная модульность — prerequisite для эффективного incremental build.

**[[dependency-resolution]]** — Dependency resolution является подсистемой build system. Gradle, Maven и npm решают задачу: какие версии библиотек включить в сборку, как разрешить конфликты транзитивных зависимостей, когда кэшировать артефакты. Без понимания resolution-алгоритмов (newest wins, nearest wins) невозможно диагностировать проблемы сборки.

**[[ci-cd-pipelines]]** — Build system — это ядро CI/CD pipeline. Jenkins, GitHub Actions, GitLab CI вызывают Gradle/Maven/npm для сборки, тестирования и упаковки. Remote build cache (Gradle Enterprise, Bazel Remote Cache) ускоряет CI в разы, разделяя результаты между разработчиками и CI-серверами. Понимание build lifecycle критично для оптимизации pipeline time.

---

## Источники и дальнейшее чтение

Humble J., Farley D. (2010). *"Continuous Delivery."* — Фундаментальная книга о pipeline от коммита до production. Объясняет почему reproducible builds, artifact management и deployment automation критичны для надёжной поставки софта. Build system рассматривается как первое звено delivery pipeline.

Mokhov A., Mitchell N., Peyton Jones S. (2018). *"Build Systems a la Carte."* — Академическая статья (Microsoft Research), систематизирующая теорию build-систем. Классифицирует Make, Shake, Bazel и др. по двум осям: scheduling (topological vs restarting) и rebuilding (dirty bit vs traces). Даёт глубокое понимание "почему" системы устроены именно так.

Aho A.V., Lam M.S., Sethi R., Ullman J.D. (2006). *"Compilers: Principles, Techniques, and Tools"* (Dragon Book). — Хотя фокус на компиляторах, главы о dependency analysis, intermediate representations и code generation объясняют что происходит "внутри" шага compilation, который build system оркестрирует.

- [Gradle User Manual](https://docs.gradle.org/current/userguide/userguide.html) — официальная документация Gradle
- [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html) — руководство по кэшированию
- [Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html) — оптимизация configuration phase

---

*Проверено: 2026-01-09*

---

[[programming-overview|← Programming]] | [[dependency-resolution|Dependency Resolution →]]

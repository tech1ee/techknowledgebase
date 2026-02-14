---
title: "Dependency Resolution: как разрешаются зависимости"
created: 2026-01-09
modified: 2026-02-13
type: concept
status: published
confidence: high
tags:
  - topic/programming
  - programming/dependencies
  - gradle
  - npm
  - maven
  - type/concept
  - level/intermediate
related:
  - "[[module-systems]]"
  - "[[build-systems-theory]]"
  - "[[clean-code-solid]]"
prerequisites:
  - "[[module-systems]]"
reading_time: 16
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Dependency Resolution: как разрешаются зависимости

> **TL;DR:** Dependency resolution — процесс определения какие версии библиотек использовать, когда разные части проекта требуют разные версии одной библиотеки. Gradle использует "newest wins", npm — nested node_modules (или flat с hoisting). Конфликты версий — главная головная боль, решается через BOM, constraints, или lock files.

---

## Исторический контекст

Проблема управления зависимостями возникла с ростом повторного использования кода. В ранних системах (C/C++) зависимости управлялись вручную: разработчик скачивал библиотеку, копировал в проект и разбирался с конфликтами сам. Этот подход получил название **"DLL Hell"** в Windows (1990-е) — ситуация, когда разные программы требовали разные версии одной DLL, и установка одной программы ломала другую.

**Perl CPAN** (1995) стал одним из первых централизованных репозиториев с автоматическим разрешением зависимостей. **Maven Central** (2004) перенёс эту идею в Java-мир, добавив semantic versioning и transitive dependency resolution. **npm** (Isaac Schlueter, 2010) довёл идею до массового масштаба — npm registry стал крупнейшим пакетным репозиторием в истории (более 2 млн пакетов).

Параллельно развивалась теория: **Dependency Inversion Principle** (Robert C. Martin, 1996) сформулировал правило "зависеть от абстракций, не от реализаций", а **Semantic Versioning** (Tom Preston-Werner, 2011) стандартизировал формат версий (MAJOR.MINOR.PATCH) для предсказуемости обновлений. Проблема **diamond dependency** (когда A и B зависят от разных версий C) остаётся одной из нерешённых задач software engineering — каждая экосистема предлагает свой компромисс.

---

## Интуиция: 5 аналогий

### 1. Зависимости как ингредиенты рецепта

```
РЕЦЕПТ ТОРТА:
  - Мука (1 кг)
  - Яйца (5 шт)
  - Крем:
    - Молоко (0.5 л)
    - Сахар (200 г)  ← Крем требует сахар
  - Глазурь:
    - Шоколад (100 г)
    - Сахар (100 г)  ← Глазурь тоже требует сахар

ВОПРОС: Сколько сахара покупать?
  - Минимум: 200 г (крем) — глазурь не хватит
  - Сумма: 300 г — будет лишний
  - Правильно: 200 г (один мешок, хватит обоим)

Это и есть dependency resolution!
```

### 2. Конфликт версий как семейный ужин

```
СЕМЕЙНЫЙ УЖИН:
  Мама хочет:     Пиццу с грибами
  Папа хочет:     Пиццу с пепперони
  Ребёнок хочет:  Пиццу с ананасом

ВАРИАНТЫ РЕШЕНИЯ:
  1. "Newest wins": последний заказавший выигрывает
  2. "Fail": "Невозможно, расходимся"
  3. "Negotiate": Пицца четыре сыра (компромисс)
  4. "Force": Мама решает за всех

В Gradle: newest version wins по умолчанию
В npm: каждый получает свою версию (nested)
```

### 3. Transitive dependencies как цепочка

```
Ты зависишь от A
A зависит от B
B зависит от C

           Ты
            │
            ▼
     ┌──────────┐
     │    A     │  (прямая зависимость)
     └────┬─────┘
          │
          ▼
     ┌──────────┐
     │    B     │  (транзитивная)
     └────┬─────┘
          │
          ▼
     ┌──────────┐
     │    C     │  (транзитивная)
     └──────────┘

Ты НЕ писал "зависимость от C"
Но C всё равно попадёт в твой проект!

→ Потенциальные проблемы с безопасностью
→ Конфликты версий
→ Bloated dependencies
```

### 4. Diamond dependency problem

```
         Твой проект
           /     \
          /       \
    Library A   Library B
          \       /
           \     /
         Library C
            v1     vs     v2

A требует C v1.0
B требует C v2.0

Какую версию C использовать?

ВАРИАНТЫ:
1. Newest wins (Gradle): C v2.0
   Риск: A может сломаться с v2.0

2. Fail fast (strict mode): Ошибка сборки
   "Conflict: C v1.0 vs v2.0"

3. Nested (npm legacy): обе версии
   Размер бандла растёт

4. Manual resolution: Ты решаешь
   constraints { ... }
```

### 5. Lock file как фотография

```
БЕЗ LOCK FILE:
  build.gradle:  kotlinx-coroutines:1.+

  Понедельник: получаешь 1.7.0
  Вторник:     выходит 1.8.0
  Среда:       получаешь 1.8.0  ← ДРУГАЯ ВЕРСИЯ!

  "Работало вчера, сломалось сегодня"

С LOCK FILE (gradle.lockfile, package-lock.json):
  Lock file = "фотография" зависимостей

  Понедельник: 1.7.0 → записано в lock file
  Среда:       читаем lock file → 1.7.0

  "Всегда одна версия, пока не обновишь явно"
```

---

## Алгоритмы resolution

### Gradle: Conflict Resolution

```kotlin
// По умолчанию: newest version wins
dependencies {
    implementation("com.google.guava:guava:30.0-jre")  // Module A требует
    implementation("some-lib:lib:1.0")                 // Внутри требует guava:31.0
}
// Результат: guava:31.0-jre (newer wins)

// Строгий режим: fail on conflict
configurations.all {
    resolutionStrategy {
        failOnVersionConflict()
    }
}
// Результат: Build fails с описанием конфликта

// Принудительная версия
configurations.all {
    resolutionStrategy {
        force("com.google.guava:guava:30.0-jre")
    }
}
// Результат: guava:30.0-jre независимо от транзитивных
```

### npm: Node Resolution

```
npm install lodash

АЛГОРИТМ ПОИСКА (Node.js):
1. ./node_modules/lodash
2. ../node_modules/lodash
3. ../../node_modules/lodash
... до корня файловой системы

NESTED VS FLAT:
npm v2 (legacy):
  node_modules/
    A/
      node_modules/
        lodash@3.0.0/  ← A's версия
    B/
      node_modules/
        lodash@4.0.0/  ← B's версия

npm v3+ (flat + hoisting):
  node_modules/
    A/
    B/
    lodash@4.0.0/     ← Hoisted (A использует эту тоже)

Проблема: phantom dependencies
```

### Maven: Nearest Definition Wins

```xml
<!-- Nearest to root wins -->
<project>
  <dependencies>
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>A</artifactId>  <!-- A → C:1.0 -->
    </dependency>
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>B</artifactId>  <!-- B → D → C:2.0 -->
    </dependency>
  </dependencies>
</project>

<!-- C:1.0 wins (ближе к root через A) -->
```

---

## Управление зависимостями

### Version Catalog (Gradle)

```toml
# gradle/libs.versions.toml

[versions]
kotlin = "2.0.0"
coroutines = "1.8.0"
ktor = "2.3.0"

[libraries]
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }
coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-okhttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }

[bundles]
ktor-client = ["ktor-client-core", "ktor-client-okhttp"]

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
```

```kotlin
// build.gradle.kts
dependencies {
    implementation(libs.kotlin.stdlib)
    implementation(libs.coroutines.core)
    implementation(libs.bundles.ktor.client)  // Группа библиотек
}
```

### BOM (Bill of Materials)

```kotlin
// Гарантирует совместимые версии
dependencies {
    // BOM управляет версиями всех Ktor библиотек
    implementation(platform("io.ktor:ktor-bom:2.3.0"))

    // Без указания версии — берётся из BOM
    implementation("io.ktor:ktor-client-core")
    implementation("io.ktor:ktor-client-okhttp")
    implementation("io.ktor:ktor-serialization-kotlinx-json")
}
```

### Dependency Constraints

```kotlin
dependencies {
    // Constraints применяются если библиотека попадает в граф
    constraints {
        implementation("com.google.guava:guava") {
            version {
                strictly("[30.0, 31.0[")  // Диапазон версий
                reject("30.0.1")          // Исключить конкретную
            }
            because("Security vulnerability in older versions")
        }
    }
}
```

### Lock Files

```kotlin
// settings.gradle.kts
dependencyLocking {
    lockAllConfigurations()
}

// Создать lock file:
// ./gradlew dependencies --write-locks

// gradle/dependency-locks/compileClasspath.lockfile
com.google.guava:guava:31.0.1-jre
org.jetbrains.kotlin:kotlin-stdlib:2.0.0
org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0
```

---

## Частые ошибки: 6 проблем

### ❌ Ошибка 1: Неуправляемые транзитивные зависимости

**Симптом:** Уязвимость в транзитивной зависимости

```kotlin
// ПЛОХО — не знаешь что тянешь:
dependencies {
    implementation("some-lib:lib:1.0")
    // Внутри: log4j:2.14.0 с уязвимостью!
}

// ХОРОШО — явный контроль:
dependencies {
    implementation("some-lib:lib:1.0") {
        exclude(group = "org.apache.logging.log4j")
    }
    implementation("org.apache.logging.log4j:log4j-core:2.17.0")  // Безопасная версия
}

// Или через constraints:
dependencies {
    constraints {
        implementation("org.apache.logging.log4j:log4j-core:2.17.0") {
            because("CVE-2021-44228 fix")
        }
    }
}
```

---

### ❌ Ошибка 2: Runtime vs Compile classpath confusion

**Симптом:** `NoClassDefFoundError` в runtime

```kotlin
// ПЛОХО:
dependencies {
    compileOnly("com.example:runtime-needed:1.0")  // ❌ Нужен в runtime!
}

// ХОРОШО:
dependencies {
    // compileOnly — только для компиляции (annotations, etc.)
    compileOnly("org.projectlombok:lombok:1.18.0")

    // implementation — компиляция + runtime
    implementation("com.example:runtime-needed:1.0")

    // runtimeOnly — только runtime (JDBC drivers, etc.)
    runtimeOnly("org.postgresql:postgresql:42.6.0")
}
```

**Правило:**
- `compileOnly` = нужен только компилятору
- `implementation` = нужен везде
- `runtimeOnly` = не нужен компилятору, нужен в runtime

---

### ❌ Ошибка 3: Snapshot зависимости в production

**Симптом:** Build работает по-разному в разное время

```kotlin
// ПЛОХО:
dependencies {
    implementation("com.example:lib:1.0-SNAPSHOT")  // ❌ Меняется!
}

// ХОРОШО:
dependencies {
    implementation("com.example:lib:1.0.0")  // Фиксированная версия
}

// Или lock file для CI:
dependencyLocking {
    lockAllConfigurations()
}
```

---

### ❌ Ошибка 4: Игнорирование dependency updates

**Симптом:** Устаревшие версии с уязвимостями

```kotlin
// ПЛОХО: "Работает — не трогай" годами

// ХОРОШО: регулярные обновления
// Используй плагин для проверки:
plugins {
    id("com.github.ben-manes.versions") version "0.50.0"
}

// ./gradlew dependencyUpdates
// Покажет устаревшие зависимости
```

**Инструменты:**
- Gradle: `ben-manes.versions`
- npm: `npm outdated`, `npm audit`
- Dependabot (GitHub)

---

### ❌ Ошибка 5: Circular dependency между модулями

**Симптом:** Build fails или непредсказуемый порядок

```kotlin
// ПЛОХО:
// module-a/build.gradle.kts
dependencies {
    implementation(project(":module-b"))
}

// module-b/build.gradle.kts
dependencies {
    implementation(project(":module-a"))  // ❌ Цикл!
}

// ХОРОШО — выделить общий модуль:
// module-common/build.gradle.kts
// (общие интерфейсы)

// module-a/build.gradle.kts
dependencies {
    implementation(project(":module-common"))
}

// module-b/build.gradle.kts
dependencies {
    implementation(project(":module-common"))
}
```

---

### ❌ Ошибка 6: Leaking implementation details

**Симптом:** Изменение внутренней зависимости ломает потребителей

```kotlin
// ПЛОХО:
dependencies {
    api("com.google.guava:guava:31.0")  // Exposes Guava to consumers!
}

// Твой код:
fun process(): ImmutableList<String> { ... }  // Guava type в API

// Потребитель твоей библиотеки:
// Теперь ДОЛЖЕН знать про Guava

// ХОРОШО:
dependencies {
    implementation("com.google.guava:guava:31.0")  // Hidden from consumers
}

// Твой код:
fun process(): List<String> { ... }  // Стандартный тип в API
```

**Правило:** `api` только для типов, которые являются частью твоего публичного API.

---

## Ментальные модели

### 1. Dependency Graph

```
Любой проект = граф зависимостей

         Your Project
              │
    ┌─────────┼─────────┐
    │         │         │
    A         B         C
    │         │
   ┌┴┐       ┌┴┐
   D E       F G
   │
   H

Resolution = обход графа + разрешение конфликтов
```

### 2. Scope влияет на distribution

```
              compile    runtime    test
api             ✓          ✓         ✓      (leaks to consumers)
implementation  ✓          ✓         ✓      (hidden from consumers)
compileOnly     ✓          ✗         ✓      (compile only)
runtimeOnly     ✗          ✓         ✓      (runtime only)
testImplement.  ✗          ✗         ✓      (test only)
```

### 3. Version Selection Strategy

```
POSSIBLE STRATEGIES:

1. NEWEST WINS (Gradle default)
   A wants C:1.0, B wants C:2.0 → C:2.0

2. NEAREST WINS (Maven)
   Closest to root in tree wins

3. FIRST WINS (older npm)
   First declared wins

4. FAIL FAST (strict mode)
   Any conflict = build failure

5. MANUAL (constraints)
   Developer decides explicitly
```

---

## Проверь себя

**Вопрос 1:** В чём разница между `api` и `implementation` в Gradle?

<details>
<summary>Ответ</summary>

- `implementation`: зависимость НЕ видна потребителям твоей библиотеки
- `api`: зависимость ВИДНА потребителям (leaks to compile classpath)

```kotlin
// Твоя библиотека
dependencies {
    api("com.google.guava:guava:31.0")        // Потребители видят Guava
    implementation("com.squareup.okhttp3:okhttp:4.0")  // Потребители НЕ видят
}
```

Используй `api` только если тип из зависимости появляется в твоём публичном API.
</details>

**Вопрос 2:** Почему нужны lock files?

<details>
<summary>Ответ</summary>

Lock files фиксируют точные версии ВСЕХ зависимостей (включая транзитивные):

1. **Воспроизводимость:** Одинаковый результат сегодня и через год
2. **CI стабильность:** Все машины получают одинаковые версии
3. **Security:** Защита от supply chain attacks (подмены версий)
4. **Debugging:** Точно знаешь какая версия используется

Без lock file: `kotlinx-coroutines:1.+` может означать разные версии в разное время.
</details>

---

## Связь с другими темами

**[[module-systems]]** — Module systems определяют границы и interfaces между компонентами, а dependency resolution определяет какие конкретные версии этих компонентов попадут в runtime. ESM tree shaking работает только при корректно объявленных зависимостях (sideEffects в package.json). JPMS requires/exports — это compile-time dependency declaration, которая затем разрешается build system. Модульность без правильного dependency management приводит к "dependency hell".

**[[build-systems-theory]]** — Build system оркестрирует dependency resolution как один из ключевых шагов сборки. Gradle реализует resolution strategy (newest wins, fail on conflict, force), Maven — nearest definition wins, Bazel — hermetic pinning. Понимание того, как build system разрешает транзитивные зависимости, необходимо для диагностики `NoClassDefFoundError`, `ClassNotFoundException` и version mismatch проблем.

**[[clean-code-solid]]** — Dependency Inversion Principle (DIP) из SOLID напрямую связан с dependency resolution на архитектурном уровне. DIP говорит: "модули верхнего уровня не должны зависеть от модулей нижнего уровня; оба должны зависеть от абстракций". Это проявляется в `api` vs `implementation` scope в Gradle — `implementation` скрывает зависимость от потребителей, обеспечивая инверсию на уровне build graph.

---

## Источники и дальнейшее чтение

Szyperski C. (2002). *"Component Software: Beyond Object-Oriented Programming."* — Фундаментальная работа о компонентном подходе к построению ПО. Детально разбирает проблемы версионирования, совместимости интерфейсов и composition of independently deployed components — ту самую задачу, которую решает dependency resolution.

Gamma E., Helm R., Johnson R., Vlissides J. (1994). *"Design Patterns: Elements of Reusable Object-Oriented Software."* — GoF-книга описывает паттерны, снижающие coupling между компонентами (Abstract Factory, Bridge, Strategy). Dependency Inversion, лежащий в основе `api` vs `implementation` scope, вырос из принципов, описанных в этой книге.

Cox R. (2019). *"Surviving Software Dependencies."* Communications of the ACM. — Практическая статья от автора Go module system о том, как управлять зависимостями в масштабе. Описывает minimum version selection (MVS) — альтернативный подход Go, где выбирается минимальная совместимая версия вместо newest wins.

- [Gradle Dependency Management](https://docs.gradle.org/current/userguide/dependency_management.html) — официальная документация по resolution в Gradle
- [npm Dependency Resolution](https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json) — как npm разрешает и фиксирует зависимости

---

---

## Ключевые карточки

Что такое diamond dependency problem?
?
Ситуация, когда два модуля (A и B) зависят от разных версий одной библиотеки (C v1.0 и C v2.0). Gradle решает через "newest wins" (берёт v2.0, рискуя сломать A). npm legacy создавал nested copies (обе версии). Maven использует "nearest wins" (ближе к root в дереве). Strict mode — падает с ошибкой конфликта.

Чем `api` отличается от `implementation` в Gradle?
?
`implementation` — зависимость скрыта от потребителей библиотеки (information hiding). `api` — зависимость ВИДНА потребителям и попадает в их compile classpath. Используй `api` только если тип из зависимости появляется в публичном API. `implementation` ускоряет инкрементальную сборку, потому что изменение скрытой зависимости не вызывает перекомпиляцию потребителей.

Зачем нужны lock files?
?
Lock file фиксирует точные версии ВСЕХ зависимостей (включая транзитивные). Гарантирует: (1) воспроизводимость — одинаковый результат сегодня и через год; (2) стабильность CI — все машины получают одинаковые версии; (3) защита от supply chain attacks; (4) debugging — точно знаешь, какая версия используется. Без lock file `1.+` означает разные версии в разное время.

Что такое BOM (Bill of Materials) и какую проблему он решает?
?
BOM — специальный POM/артефакт, который объявляет совместимые версии набора библиотек. Подключается через `platform()` в Gradle. После этого зависимости из BOM можно добавлять без указания версии — она берётся из BOM. Решает проблему несовместимых версий (например, Ktor client + serialization + server должны быть одной версии).

Чем "newest wins" (Gradle) отличается от "nearest wins" (Maven)?
?
Gradle default: при конфликте A→C:1.0 и B→C:2.0 выбирает C:2.0 (новейшая версия). Риск: A может сломаться с v2.0. Maven: выбирает версию, которая ближе к root в дереве зависимостей (A→C:1.0 ближе, чем B→D→C:2.0, поэтому C:1.0). Риск: может выбрать старую версию, отсутствующую API.

Что такое phantom dependencies и почему они опасны?
?
Phantom dependency — использование пакета, который НЕ объявлен в твоём package.json, но доступен через hoisting (npm v3+). npm "поднимает" зависимости зависимостей в корневой node_modules. Код работает локально, но ломается: (1) при обновлении зависимости, которая больше не тянет phantom; (2) у другого разработчика с другим порядком установки; (3) при переходе на pnpm (strict node_modules).

Чем `compileOnly` отличается от `runtimeOnly` в Gradle?
?
`compileOnly` — зависимость нужна только компилятору, НЕ попадает в runtime classpath (annotations, Lombok). `runtimeOnly` — не нужна компилятору, но нужна в runtime (JDBC drivers, SLF4J implementations). `implementation` — нужна и там, и там. Неправильный scope = `NoClassDefFoundError` в runtime или лишние зависимости в артефакте.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[build-systems-theory]] | Как build system оркестрирует resolution при сборке проекта |
| Углубиться | [[android-dependencies]] | Практика: dependency management в Android multi-module проектах |
| Смежная тема | [[module-systems]] | Как модульная система определяет контракты между зависимостями |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

*Проверено: 2026-01-09*

---

[[build-systems-theory|← Build Systems]] | [[module-systems|Module Systems →]]

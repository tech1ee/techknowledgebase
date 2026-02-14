---
title: "Инструменты качества кода: Detekt, ktlint, Lint"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
area: android
tags:
  - topic/android
  - topic/code-quality
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-ci-cd]]"
  - "[[android-gradle-fundamentals]]"
  - "[[android-testing]]"
  - "[[android-ecosystem-2026]]"
prerequisites:
  - "[[android-gradle-fundamentals]]"
reading_time: 18
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Инструменты качества кода: Detekt, ktlint, Lint

Lint ловит баги до того, как их увидят пользователи. Статический анализ и автоформатирование -- это первая линия обороны качества кода. В отличие от тестов, которые проверяют поведение, линтеры проверяют структуру: стиль, сложность, потенциальные ошибки, Android-специфичные паттерны. Правильно настроенный pipeline из Detekt + ktlint + Android Lint + Spotless автоматизирует 80% code review замечаний.

> **Prerequisites:**
> - [[android-gradle-fundamentals]] -- основы Gradle и Android Gradle Plugin
> - Базовое понимание Kotlin и Gradle DSL

---

## Обзор инструментов

| Инструмент | Назначение | Scope | Тип |
|------------|-----------|-------|-----|
| **Detekt** | Статический анализ Kotlin | Code smells, complexity, naming, exceptions | Анализ |
| **ktlint** | Форматирование Kotlin | Indentation, spacing, imports, line length | Форматирование |
| **Android Lint** | Android-специфичные проверки | Security, performance, accessibility, API compatibility | Анализ |
| **Spotless** | Мультиязычное форматирование | Kotlin, Java, XML, Gradle KTS, JSON | Форматирование |

**Ключевое различие:** Detekt и Android Lint анализируют логику и структуру кода (code smells, потенциальные баги). ktlint и Spotless обеспечивают единый стиль (форматирование). Они дополняют друг друга, а не конкурируют.

---

## Detekt

Detekt -- статический анализатор для Kotlin, специализирующийся на code smells и метриках сложности. Текущая стабильная версия -- **1.23.8** (февраль 2025, Kotlin 2.0.21). Версия 2.0.0 в alpha-стадии (Kotlin 2.3.0, Gradle 9.x).

### Подключение

```kotlin
// build.gradle.kts (project-level)
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.8"
}

// build.gradle.kts (module-level)
detekt {
    config.setFrom("$rootDir/config/detekt/detekt.yml")
    buildUponDefaultConfig = true  // использовать default rules + кастомные
    parallel = true                // параллельный анализ модулей
    autoCorrect = true             // автоисправление (где возможно)
    baseline = file("detekt-baseline.xml")  // для legacy проектов
}

dependencies {
    detektPlugins("io.gitlab.arturbosch.detekt:detekt-formatting:1.23.8")
}
```

### Конфигурация detekt.yml

Генерация default config:

```bash
./gradlew detektGenerateConfig
# Создаёт config/detekt/detekt.yml
```

Ключевые rule sets:

```yaml
# config/detekt/detekt.yml
complexity:
  active: true
  CyclomaticComplexMethod:
    active: true
    threshold: 10          # max цикломатическая сложность метода
  LongMethod:
    active: true
    threshold: 40          # max строк в методе
  LongParameterList:
    active: true
    functionThreshold: 5   # max параметров функции
  TooManyFunctions:
    active: true
    thresholdInFiles: 15
    thresholdInClasses: 12

naming:
  active: true
  FunctionNaming:
    active: true
    functionPattern: '[a-z][a-zA-Z0-9]*'
    excludes: ['**/test/**', '**/androidTest/**']  # тесты могут `should_return_true`
  VariableNaming:
    active: true
    variablePattern: '[a-z][a-zA-Z0-9]*'

exceptions:
  active: true
  SwallowedException:
    active: true           # запрет пустого catch {}
  TooGenericExceptionCaught:
    active: true           # предупреждение при catch(Exception)

performance:
  active: true
  SpreadOperator:
    active: true           # *array создаёт копию -- медленно
  ArrayPrimitive:
    active: true           # Array<Int> → IntArray для производительности

style:
  active: true
  MagicNumber:
    active: true
    ignoreNumbers: ['-1', '0', '1', '2']
    ignoreEnums: true
    ignorePropertyDeclaration: true
  MaxLineLength:
    active: true
    maxLineLength: 120
  WildcardImport:
    active: true           # запрет import foo.*
```

### Baseline для legacy проектов

Когда Detekt подключается к существующему проекту, сотни warnings блокируют CI. Baseline -- файл с "допустимыми" нарушениями, которые игнорируются:

```bash
# Генерация baseline (фиксация текущего состояния)
./gradlew detektBaseline

# Результат: detekt-baseline.xml
# Новый код проверяется строго, старый -- по baseline
```

**Стратегия:** каждый спринт уменьшать baseline на 10-20 issues. Через полгода baseline станет пустым.

### Подавление предупреждений

```kotlin
@Suppress("MagicNumber")  // конкретное правило
fun calculateDiscount(price: Double): Double = price * 0.15

@Suppress("TooManyFunctions")  // на уровне класса
class LargeRepository { ... }
```

Используйте `@Suppress` точечно. Если подавляете правило в >5 местах -- пересмотрите threshold в config.

### Gradle tasks

| Task | Описание |
|------|----------|
| `detekt` | Анализ всех source sets |
| `detektMain` | Только production code |
| `detektTest` | Только тесты |
| `detektBaseline` | Генерация baseline |
| `detektGenerateConfig` | Генерация default config |

### Метрики

Detekt вычисляет:
- **Cyclomatic complexity** -- количество независимых путей выполнения (threshold: 10)
- **Cognitive complexity** -- сложность понимания кода человеком
- **Code smells count** -- общее количество нарушений
- **Lines of code** -- LOC, eLOC (effective), cLOC (comments)

Отчёты: HTML, XML, SARIF (для GitHub Code Scanning), Markdown.

### Кастомные правила

```kotlin
class NoAndroidLogRule(config: Config) : Rule(config) {
    override val issue = Issue(
        id = "NoAndroidLog",
        severity = Severity.Warning,
        description = "Use Timber instead of android.util.Log",
        debt = Debt.FIVE_MINS
    )

    override fun visitImportDirective(importDirective: KtImportDirective) {
        val importPath = importDirective.importPath?.pathStr ?: return
        if (importPath == "android.util.Log") {
            report(CodeSmell(issue, Entity.from(importDirective),
                "Replace android.util.Log with Timber"))
        }
    }
}
```

Кастомные правила упаковываются в отдельный модуль и подключаются как `detektPlugins` dependency.

---

## ktlint

ktlint -- форматтер Kotlin от Pinterest. Текущая версия **1.7.0** (декабрь 2025, Kotlin 2.2.0). Обеспечивает единый стиль кодирования без бесконечных дискуссий в code review.

### Подключение

ktlint чаще всего используется через Spotless или отдельный Gradle-плагин:

```kotlin
// Через Spotless (рекомендуемый способ -- см. секцию Spotless)

// Или отдельный плагин
plugins {
    id("org.jlleitschuh.gradle.ktlint") version "12.1.2"
}

ktlint {
    version.set("1.7.0")
    android.set(true)              // Android code style
    outputToConsole.set(true)
    enableExperimentalRules.set(true)
}
```

### Конфигурация .editorconfig

ktlint использует `.editorconfig` для настройки правил:

```ini
# .editorconfig (корень проекта)
root = true

[*.{kt,kts}]
ktlint_code_style = android_studio

# Длина строки
max_line_length = 120

# Запрет wildcard imports
ij_kotlin_packages_to_use_import_on_demand = unset

# Trailing comma
ij_kotlin_allow_trailing_comma = true
ij_kotlin_allow_trailing_comma_on_call_site = true

# Управление правилами
ktlint_standard = enabled
ktlint_experimental = enabled
ktlint_standard_no-wildcard-imports = enabled
ktlint_standard_filename = enabled

# Отключение конкретных правил (при необходимости)
# ktlint_standard_function-naming = disabled
```

### Категории правил

| Категория | Примеры | Количество |
|-----------|---------|------------|
| **Standard** | Indentation, spacing, imports, final-newline | ~50 правил |
| **Experimental** | Trailing comma, function signature, annotation | ~20 правил |
| **Custom** | Возможность писать свои правила | Без ограничений |

### ktfmt как альтернатива

**ktfmt** (от Meta/Facebook) -- альтернативный форматтер Kotlin с более опinionated подходом:

| Аспект | ktlint | ktfmt |
|--------|--------|-------|
| **Философия** | Настраиваемые правила | Один "правильный" стиль |
| **Конфигурация** | Гибкая (.editorconfig) | Минимальная (3 стиля) |
| **Скорость** | ~14.8 сек / 3500 файлов | ~5.9 сек / 3500 файлов |
| **Автоформат** | Check + format | Только format (перезапись) |
| **Стили** | android_studio, ktlint_official | kotlinlang, google, meta |
| **Maintainer** | Pinterest | Meta |

**Когда что выбирать:**
- **ktlint** -- когда нужна гибкая настройка и постепенное внедрение
- **ktfmt** -- когда нужен zero-config подход и максимальная скорость

### ktlint vs Detekt

Они не конкурируют, а дополняют друг друга:

- **ktlint** = форматирование (пробелы, отступы, imports, trailing commas)
- **Detekt** = анализ (complexity, code smells, naming conventions, потенциальные баги)

Detekt включает ktlint formatting rules через плагин `detekt-formatting`, но рекомендуется использовать их раздельно для прозрачности pipeline.

---

## Android Lint

Android Lint -- встроенный анализатор Android Gradle Plugin. Содержит **~400 built-in проверок**, покрывающих Android-специфичные проблемы: совместимость API, accessibility, security, performance, i18n.

### Конфигурация lint.xml

```xml
<!-- lint.xml (корень проекта или модуля) -->
<?xml version="1.0" encoding="UTF-8"?>
<lint>
    <!-- Повысить severity -->
    <issue id="HardcodedText" severity="error" />
    <issue id="MissingTranslation" severity="error" />
    <issue id="Accessibility" severity="error" />

    <!-- Понизить severity -->
    <issue id="ObsoleteLintCustomCheck" severity="warning" />

    <!-- Отключить -->
    <issue id="GradleDependency" severity="ignore" />

    <!-- Игнорировать в конкретных файлах -->
    <issue id="MissingTranslation">
        <ignore path="src/test/**" />
    </issue>
</lint>
```

Настройка в `build.gradle.kts`:

```kotlin
android {
    lint {
        abortOnError = true        // CI падает при ошибках
        warningsAsErrors = false
        checkDependencies = true   // проверять зависимости тоже
        baseline = file("lint-baseline.xml")
        htmlReport = true
        sarifReport = true         // для GitHub Code Scanning
        disable += setOf("GradleDependency", "OldTargetApi")
        enable += setOf("Interoperability")
    }
}
```

### Категории проверок

| Категория | Примеры | Зачем |
|-----------|---------|-------|
| **Correctness** | WrongThread, MissingPermission, InvalidPackage | Баги runtime |
| **Security** | HardcodedDebugMode, ExportedContentProvider | Уязвимости |
| **Performance** | DrawAllocation, Recycle, UseCompoundDrawables | Производительность |
| **Accessibility** | ContentDescription, TouchTargetSizeCheck | Доступность |
| **Internationalization** | HardcodedText, SetTextI18n | Локализация |
| **Interoperability** | Kotlin-Java interop проблемы | Совместимость |

### Compose Lint checks

Jetpack Compose поставляется с собственными Lint-правилами:

```
ComposableNaming          -- @Composable функции с заглавной буквы
ComposableModifierFactory -- modifier factory должен возвращать Modifier
MutableCollectionMutableState -- mutableStateOf(mutableListOf()) -- ошибка
RememberReturnType        -- remember {} должен возвращать значение
ProduceStateDoesNotAssignValue -- produceState без value = ...
```

Дополнительные правила от сообщества:
- **compose-lint-rules** (ReactiveCircus) -- naming, modifiers, preview
- **compose-lints** (Slack) -- stability, performance, best practices

### Кастомные Lint rules

Архитектура кастомного правила:

```kotlin
// 1. Issue definition
val ISSUE_NO_TOAST = Issue.create(
    id = "NoToast",
    briefDescription = "Use Snackbar instead of Toast",
    explanation = "Toast is deprecated in modern Android. Use Snackbar.",
    category = Category.CORRECTNESS,
    priority = 6,
    severity = Severity.WARNING,
    implementation = Implementation(
        NoToastDetector::class.java,
        Scope.JAVA_FILE_SCOPE    // Kotlin тоже покрывается
    )
)

// 2. Detector с UElementVisitor паттерном
class NoToastDetector : Detector(), SourceCodeScanner {

    override fun getApplicableMethodNames(): List<String> =
        listOf("makeText")

    override fun visitMethodCall(
        context: JavaContext,
        node: UCallExpression,
        method: PsiMethod
    ) {
        if (context.evaluator.isMemberInClass(method, "android.widget.Toast")) {
            context.report(
                ISSUE_NO_TOAST,
                node,
                context.getLocation(node),
                "Replace Toast.makeText() with Snackbar.make()"
            )
        }
    }
}

// 3. Registry
class CustomIssueRegistry : IssueRegistry() {
    override val issues = listOf(ISSUE_NO_TOAST)
    override val api = CURRENT_API
}
```

Кастомные правила размещаются в отдельном модуле `lint-checks` и подключаются через `lintChecks(project(":lint-checks"))`.

### Baseline для legacy

```bash
# Генерация baseline (фиксация текущих предупреждений)
./gradlew lintDebug -Dlint.baselines.continue=true
# Создаёт lint-baseline.xml

# Последующие запуски игнорируют baseline issues
# Новые проблемы -- fail
```

---

## Spotless

Spotless -- универсальный форматтер от DiffPlug. Текущая версия **8.2.1** (январь 2026). Главное преимущество: единая точка конфигурации для Kotlin, Java, XML, Gradle KTS, JSON, YAML.

### Подключение

```kotlin
// build.gradle.kts (project-level)
plugins {
    id("com.diffplug.spotless") version "8.2.1"
}

spotless {
    kotlin {
        target("**/*.kt")
        targetExclude("**/build/**")
        ktlint("1.7.0")
            .setEditorConfigPath("$rootDir/.editorconfig")
        trimTrailingWhitespace()
        endWithNewline()
    }

    kotlinGradle {
        target("**/*.gradle.kts")
        ktlint("1.7.0")
    }

    format("xml") {
        target("**/*.xml")
        targetExclude("**/build/**")
        indentWithSpaces(4)
        trimTrailingWhitespace()
        endWithNewline()
    }

    format("json") {
        target("**/*.json")
        targetExclude("**/build/**")
        trimTrailingWhitespace()
        endWithNewline()
    }
}
```

**Важно для Android:** Spotless не может автоматически обнаружить Android source sets. Необходимо явно указывать `target("src/*/kotlin/**/*.kt", "src/*/java/**/*.kt")` или использовать `**/*.kt` с exclude для build-директорий.

### Команды

| Команда | Описание |
|---------|----------|
| `./gradlew spotlessCheck` | Проверить -- fail при нарушениях (для CI) |
| `./gradlew spotlessApply` | Автоисправление всех нарушений (для dev) |
| `./gradlew spotlessKotlinCheck` | Проверить только Kotlin |
| `./gradlew spotlessKotlinApply` | Исправить только Kotlin |

---

## Стратегия интеграции

### Pre-commit hooks

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Running spotlessCheck..."
./gradlew spotlessCheck --daemon 2>/dev/null
SPOTLESS_EXIT=$?

echo "Running detekt..."
./gradlew detektMain --daemon 2>/dev/null
DETEKT_EXIT=$?

if [ $SPOTLESS_EXIT -ne 0 ] || [ $DETEKT_EXIT -ne 0 ]; then
    echo "Code quality checks failed."
    echo "Run ./gradlew spotlessApply to fix formatting."
    exit 1
fi
```

Для автоматической установки hooks используйте Gradle task:

```kotlin
// build.gradle.kts
tasks.register<Copy>("installGitHooks") {
    from("$rootDir/scripts/pre-commit")
    into("$rootDir/.git/hooks")
    filePermissions { unix("rwxr-xr-x") }
}

tasks.named("prepareKotlinBuildScriptModel") {
    dependsOn("installGitHooks")
}
```

### CI pipeline

Рекомендуемый порядок выполнения в CI:

```
┌──────────────────────────────────────────────────────┐
│                    CI PIPELINE                        │
├──────────────────────────────────────────────────────┤
│                                                       │
│  1. spotlessCheck  (1-2 min)   — форматирование      │
│       ↓                                               │
│  2. detektMain     (2-3 min)   — статический анализ  │
│       ↓                                               │
│  3. lintDebug      (3-5 min)   — Android Lint         │
│       ↓                                               │
│  4. testDebug      (5-10 min)  — unit тесты          │
│       ↓                                               │
│  5. assembleDebug  (5-10 min)  — сборка              │
│                                                       │
│  Быстрые проверки первыми — fail fast!               │
└──────────────────────────────────────────────────────┘
```

GitHub Actions пример:

```yaml
# .github/workflows/code-quality.yml
name: Code Quality
on: [pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Spotless Check
        run: ./gradlew spotlessCheck

      - name: Detekt
        run: ./gradlew detektMain

      - name: Android Lint
        run: ./gradlew lintDebug

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: app/build/reports/detekt/detekt.sarif
```

### IDE live feedback

IntelliJ IDEA / Android Studio:
- **Detekt plugin** -- подсвечивает нарушения в реальном времени, использует проектный `detekt.yml`
- **ktlint plugin** -- автоформат при сохранении (Actions on Save)
- **Android Lint** -- встроен в Android Studio, работает out of the box
- **Spotless** -- нет IDE-плагина, только Gradle tasks

### Composite Gradle task

```kotlin
// build.gradle.kts
tasks.register("codeQuality") {
    group = "verification"
    description = "Run all code quality checks"
    dependsOn("spotlessCheck", "detektMain", "lintDebug")
}

// Использование:
// ./gradlew codeQuality
```

---

## Рекомендуемая стартовая конфигурация

### Минимальный detekt.yml

```yaml
# config/detekt/detekt.yml — старт для нового проекта
build:
  maxIssues: 0  # zero tolerance для нового кода

complexity:
  active: true
  CyclomaticComplexMethod:
    threshold: 15  # начните с 15, снижайте до 10
  LongMethod:
    threshold: 60
  LongParameterList:
    functionThreshold: 6

naming:
  active: true
  FunctionNaming:
    excludes: ['**/test/**']

exceptions:
  active: true
  SwallowedException:
    active: true

style:
  active: true
  MagicNumber:
    ignorePropertyDeclaration: true
    ignoreEnums: true
  WildcardImport:
    active: true
```

### .editorconfig для ktlint

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.{kt,kts}]
max_line_length = 120
ktlint_code_style = android_studio
ij_kotlin_allow_trailing_comma = true
ij_kotlin_allow_trailing_comma_on_call_site = true
ij_kotlin_packages_to_use_import_on_demand = unset
```

### lint.xml для Android Lint

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lint>
    <!-- Критичные проверки — error -->
    <issue id="HardcodedText" severity="error" />
    <issue id="MissingTranslation" severity="error" />
    <issue id="HardcodedDebugMode" severity="error" />
    <issue id="ExportedContentProvider" severity="error" />
    <issue id="WrongThread" severity="error" />

    <!-- Шум — отключить -->
    <issue id="GradleDependency" severity="ignore" />
    <issue id="OldTargetApi" severity="ignore" />
    <issue id="UnusedResources" severity="warning" />
</lint>
```

---

## Проверь себя

> [!question]- Чем отличается Detekt от ktlint? Можно ли использовать оба одновременно?
> **Detekt** -- статический анализатор: ищет code smells, complexity, потенциальные баги (complexity, naming, exceptions, performance). **ktlint** -- форматтер: обеспечивает единый стиль кода (indentation, spacing, imports, trailing commas). Они дополняют друг друга и должны использоваться совместно. Detekt анализирует "что написано", ktlint -- "как выглядит". Detekt включает ktlint rules через плагин `detekt-formatting`, но рекомендуется использовать их раздельно для прозрачности CI pipeline.

> [!question]- Как внедрить Detekt в legacy проект с тысячами предупреждений?
> 1) Сгенерировать baseline: `./gradlew detektBaseline` -- фиксирует текущие нарушения. 2) Настроить CI на проверку только нового кода (baseline исключает старые issues). 3) Постепенно уменьшать baseline: каждый спринт исправлять 10-20 issues. 4) Через 3-6 месяцев baseline станет пустым. **Главное:** не пытаться исправить всё сразу -- это парализует команду и создаёт merge conflicts.

> [!question]- Зачем Spotless, если уже есть ktlint?
> ktlint форматирует только Kotlin. Spotless -- мета-форматтер, который управляет несколькими инструментами: ktlint для Kotlin, google-java-format для Java, xmlstarlet для XML, prettier для JSON. Единая команда `spotlessApply` форматирует все языки проекта. Кроме того, Spotless интегрируется с CI через `spotlessCheck` и не требует отдельного Gradle-плагина для ktlint. Spotless также позволяет переключаться между ktlint и ktfmt без изменения pipeline.

---

## Ключевые карточки

Что такое Detekt и зачем он нужен?
?
Detekt -- статический анализатор для Kotlin. Ищет code smells, complexity, naming violations, performance issues. Текущая версия 1.23.8. Конфигурация через detekt.yml. Основные rule sets: complexity, naming, exceptions, performance, style. Поддерживает baseline для legacy проектов и кастомные правила.

Чем ktlint отличается от ktfmt?
?
ktlint (Pinterest) -- настраиваемый форматтер с .editorconfig конфигурацией, ~70 правил (standard + experimental). ktfmt (Meta) -- opinionated форматтер с минимальной конфигурацией (3 стиля), на 40% быстрее. ktlint -- гибкость и постепенное внедрение, ktfmt -- zero-config подход. Оба инструмента -- только форматирование, не анализ.

Как работает Android Lint baseline?
?
baseline -- XML-файл с текущими нарушениями, которые игнорируются при проверке. Генерация: `./gradlew lintDebug -Dlint.baselines.continue=true`. Новый код проверяется строго, старые issues -- по baseline. Аналогично работает Detekt baseline (`./gradlew detektBaseline`). Стратегия: постепенно уменьшать baseline каждый спринт.

Что делает Spotless и как его использовать?
?
Spotless -- мультиязычный форматтер (Kotlin, Java, XML, JSON, Gradle KTS). Версия 8.2.1. Две команды: `spotlessCheck` (CI -- fail при нарушениях) и `spotlessApply` (dev -- автоисправление). Внутри использует ktlint или ktfmt для Kotlin. Не определяет Android source sets автоматически -- нужен явный target.

Какой порядок проверок в CI pipeline?
?
Быстрые проверки первыми (fail fast): 1) spotlessCheck (1-2 мин), 2) detektMain (2-3 мин), 3) lintDebug (3-5 мин), 4) testDebug (5-10 мин), 5) assembleDebug (5-10 мин). SARIF-отчёты загружаются в GitHub Code Scanning. Pre-commit hooks запускают spotless + detekt локально до push.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-ci-cd]] | Интеграция code quality в полный CI/CD pipeline |
| Углубиться | [[android-gradle-fundamentals]] | Понять Gradle tasks, на которых основаны все инструменты |
| Смежная тема | [[android-testing]] | Тесты -- следующий уровень quality gates после lint |
| Обзор | [[android-ecosystem-2026]] | Общая картина инструментов Android экосистемы |

---

## Источники

**Официальная документация:**
- [Detekt -- Static Code Analysis for Kotlin](https://detekt.dev/)
- [Detekt Configuration](https://detekt.dev/docs/introduction/configurations/)
- [Detekt Gradle Plugin](https://detekt.dev/docs/gettingstarted/gradle/)
- [ktlint -- An Anti-bikeshedding Kotlin Linter](https://github.com/pinterest/ktlint)
- [ktfmt -- Kotlin Code Formatter](https://github.com/facebook/ktfmt)
- [Spotless -- Keep Your Code Spotless](https://github.com/diffplug/spotless)
- [Android Lint -- Improve Your Code](https://developer.android.com/studio/write/lint)
- [Compose Lint Checks](https://developer.android.com/develop/ui/compose/tooling/lint)
- [Custom Lint Rules -- Google Samples](https://github.com/googlesamples/android-custom-lint-rules)
- [Slack Compose Lints](https://slackhq.github.io/compose-lints/)

**Статьи и руководства:**
- [Choosing the Right Static Code Analysis Tool for Android in 2025](https://medium.com/@cristian.torrado/choosing-the-right-static-code-analysis-tool-for-android-in-2025-aefafaad70ce)
- [Adopting Ktfmt and Detekt -- Block Engineering Blog](https://engineering.block.xyz/blog/adopting-ktfmt-and-detekt)
- [Enforcing Code Quality with Detekt and Ktlint](https://medium.com/@mohamad.alemicode/enforcing-code-quality-in-android-with-detekt-and-ktlint-a-practical-guide-907b57d047ec)

---

*Проверено: 2026-02-14 | На основе Detekt 1.23.8, ktlint 1.7.0, Spotless 8.2.1, AGP 8.x*

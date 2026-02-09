---
title: "Android CI/CD: от локального билда до Play Store"
tags: [android, devops, ci-cd, github-actions, fastlane, gradle, testing, automation]
category: android
level: senior
created: 2025-12-28
modified: 2026-01-05
cs-foundations: [continuous-integration, pipeline-automation, artifact-management, deployment-strategies]
sources: [developer.android.com, fastlane.tools, firebase.google.com, docs.gradle.org, circleci.com, runway.team]
---

# Android CI/CD: от локального билда до Play Store

## TL;DR

> **Android CI/CD** автоматизирует build → test → sign → deploy. Elite команды деплоят в **973x чаще** (State of DevOps 2024).
>
> **GitHub Actions** + **Fastlane** = стандарт индустрии 2025. Gradle Build Cache ускоряет билды на **20-50%**. Roborazzi для screenshot-тестов на JVM (без эмулятора). Firebase Test Lab для cloud-тестирования на реальных устройствах.
>
> **Критично:** Google требует target API 35 к августу 2025. Play App Signing обязателен. Никогда не хранить keystore в репозитории.

---

## Зачем это нужно

### Проблема: ручной релиз — это боль

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| **"Релиз занимает день"** | Ручная сборка, подпись, загрузка | Медленный time-to-market |
| **"Работает на моей машине"** | Разные версии SDK, зависимостей | Баги в production |
| **"Забыли прогнать тесты"** | Human error, спешка перед релизом | Регрессии у пользователей |
| **"Кто собирал последний APK?"** | Нет audit trail | Невозможно воспроизвести билд |
| **"Потеряли keystore"** | Локальное хранение ключей | Невозможно обновить приложение |

### Кому нужен Android CI/CD

| Роль | Зачем | Глубина |
|------|-------|---------|
| **Senior Android Dev** | Настройка pipeline, оптимизация | Глубокая |
| **Staff/Principal** | Архитектура CI/CD, стандарты команды | Глубокая |
| **Tech Lead** | Процессы релиза, quality gates | Средняя |
| **DevOps/SRE** | Инфраструктура, мониторинг | Глубокая |

---

## Актуальность 2025

| Тренд | Статус | Что важно знать |
|-------|--------|-----------------|
| **Target API 35** | Обязательно | Новые apps/updates требуют API 35 к августу 2025 |
| **Play App Signing** | Стандарт | Google управляет signing key, вы — upload key |
| **Roborazzi** | 🔥 Hot | Screenshot тесты на JVM без эмулятора, используется в Now in Android |
| **Gradle Build Cache** | ✅ Production | Remote cache ускоряет билды на 20-50% |
| **Gradle Managed Devices** | ✅ Mature | Декларативный запуск эмуляторов в Gradle |
| **Fastlane supply** | ✅ Стандарт | Автоматический upload в Play Console |

### DORA Metrics (State of DevOps 2024)

| Метрика | Elite | High | Medium | Low |
|---------|-------|------|--------|-----|
| **Deployment Frequency** | Multiple/day | Weekly | Monthly | <6 months |
| **Lead Time** | <1 hour | 1 day-1 week | 1-6 months | >6 months |
| **Change Failure Rate** | 0-15% | 16-30% | 31-45% | 46-60% |
| **Time to Restore** | <1 hour | <1 day | 1 day-1 week | >6 months |

**Elite команды деплоят в 973x чаще и восстанавливаются в 6570x быстрее.**

---

## Архитектура Android CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ANDROID CI/CD PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │  PUSH/PR │───▶│   BUILD  │───▶│   TEST   │───▶│  QUALITY GATES   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────────┘  │
│                       │               │                   │             │
│                       ▼               ▼                   ▼             │
│                  - Lint           - Unit tests      - Coverage >80%    │
│                  - Compile        - Screenshot      - No critical      │
│                  - Build APK/AAB  - Integration       issues          │
│                                   - Firebase TL     - APK size limit   │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │   SIGN   │───▶│ ARTIFACT │───▶│  DEPLOY  │───▶│    MONITOR       │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────────┘  │
│       │               │               │                   │             │
│       ▼               ▼               ▼                   ▼             │
│  - Release key   - Upload to    - Internal track   - Crash reports    │
│  - Play Signing    storage      - Alpha/Beta       - ANR rate         │
│  - Verify        - Versioning   - Production       - Vitals           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## GitHub Actions для Android

### Базовый CI Workflow

```yaml
# .github/workflows/android-ci.yml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  JAVA_VERSION: '17'
  GRADLE_OPTS: "-Dorg.gradle.jvmargs=-Xmx4g -Dorg.gradle.daemon=false"

jobs:
  # Job 1: Валидация Gradle Wrapper (security)
  validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gradle/wrapper-validation-action@v2

  # Job 2: Lint + Unit Tests
  test:
    needs: validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: ${{ env.JAVA_VERSION }}

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}

      - name: Grant execute permission
        run: chmod +x gradlew

      - name: Run Lint
        run: ./gradlew lint

      - name: Run Unit Tests
        run: ./gradlew test

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: '**/build/reports/tests/'

  # Job 3: Build APK/AAB
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: ${{ env.JAVA_VERSION }}

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Build Debug APK
        run: ./gradlew assembleDebug

      - name: Build Release AAB
        run: ./gradlew bundleRelease

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: debug-apk
          path: app/build/outputs/apk/debug/*.apk
```

### Instrumentation Tests с Эмулятором

```yaml
# Job для instrumentation tests
instrumentation:
  needs: test
  runs-on: macos-latest  # macOS быстрее для эмуляторов
  timeout-minutes: 30

  steps:
    - uses: actions/checkout@v4

    - name: Setup JDK
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Setup Gradle
      uses: gradle/actions/setup-gradle@v3

    - name: AVD Cache
      uses: actions/cache@v4
      id: avd-cache
      with:
        path: |
          ~/.android/avd/*
          ~/.android/adb*
        key: avd-api-31-${{ runner.os }}

    - name: Create AVD and Generate Snapshot
      if: steps.avd-cache.outputs.cache-hit != 'true'
      uses: reactivecircus/android-emulator-runner@v2
      with:
        api-level: 31
        arch: x86_64
        force-avd-creation: false
        emulator-options: -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim
        disable-animations: true
        script: echo "AVD created"

    - name: Run Instrumentation Tests
      uses: reactivecircus/android-emulator-runner@v2
      with:
        api-level: 31
        arch: x86_64
        force-avd-creation: false
        emulator-options: -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim
        disable-animations: true
        script: ./gradlew connectedCheck
```

### Screenshot Tests с Roborazzi

```yaml
# Job для screenshot tests (без эмулятора!)
screenshot-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Setup JDK
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Setup Gradle
      uses: gradle/actions/setup-gradle@v3

    - name: Run Roborazzi Tests
      run: ./gradlew verifyRoborazziDebug

    - name: Upload Screenshot Diffs
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: screenshot-diffs
        path: '**/build/outputs/roborazzi/'
```

---

## Fastlane для Android

### Установка и настройка

```bash
# 1. Установка Fastlane
gem install fastlane -NV

# 2. Инициализация в проекте
cd android_project
fastlane init

# 3. Структура создаётся автоматически:
# fastlane/
# ├── Appfile       # Package name, JSON key
# ├── Fastfile      # Lanes (задачи)
# └── Pluginfile    # Плагины (опционально)
```

### Appfile

```ruby
# fastlane/Appfile
json_key_file("fastlane/play-store-key.json")
package_name("com.example.myapp")
```

### Fastfile с основными lanes

```ruby
# fastlane/Fastfile
default_platform(:android)

platform :android do

  # === BUILD LANES ===

  desc "Build debug APK"
  lane :build_debug do
    gradle(task: "assembleDebug")
  end

  desc "Build release AAB"
  lane :build_release do
    gradle(
      task: "bundle",
      build_type: "Release",
      print_command: false,
      properties: {
        "android.injected.signing.store.file" => ENV["KEYSTORE_PATH"],
        "android.injected.signing.store.password" => ENV["KEYSTORE_PASSWORD"],
        "android.injected.signing.key.alias" => ENV["KEY_ALIAS"],
        "android.injected.signing.key.password" => ENV["KEY_PASSWORD"]
      }
    )
  end

  # === TEST LANES ===

  desc "Run unit tests"
  lane :test do
    gradle(task: "test")
  end

  desc "Run lint check"
  lane :lint do
    gradle(task: "lint")
  end

  # === DEPLOY LANES ===

  desc "Deploy to Internal track"
  lane :deploy_internal do
    build_release
    upload_to_play_store(
      track: "internal",
      release_status: "draft",
      aab: "app/build/outputs/bundle/release/app-release.aab"
    )
  end

  desc "Deploy to Alpha track"
  lane :deploy_alpha do
    build_release
    upload_to_play_store(
      track: "alpha",
      release_status: "completed",
      aab: "app/build/outputs/bundle/release/app-release.aab"
    )
  end

  desc "Deploy to Production"
  lane :deploy_production do
    build_release
    upload_to_play_store(
      track: "production",
      release_status: "completed",
      aab: "app/build/outputs/bundle/release/app-release.aab"
    )
  end

  desc "Promote from internal to production"
  lane :promote_to_production do
    upload_to_play_store(
      track: "internal",
      track_promote_to: "production",
      skip_upload_apk: true,
      skip_upload_aab: true
    )
  end

  # === VERSION MANAGEMENT ===

  desc "Increment version code"
  lane :increment_version do
    # Получаем текущий version code из Play Store
    latest_version = google_play_track_version_codes(track: "internal").max || 0
    new_version = latest_version + 1

    # Обновляем build.gradle
    android_set_version_code(
      version_code: new_version,
      gradle_file: "app/build.gradle"
    )

    UI.success("Version code updated to #{new_version}")
  end
end
```

### GitHub Actions + Fastlane

```yaml
# .github/workflows/deploy.yml
name: Deploy to Play Store

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Decode Keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > keystore.jks

      - name: Decode Play Store Key
        run: |
          echo "${{ secrets.PLAY_STORE_KEY_BASE64 }}" | base64 -d > fastlane/play-store-key.json

      - name: Deploy to Internal
        env:
          KEYSTORE_PATH: ${{ github.workspace }}/keystore.jks
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: bundle exec fastlane deploy_internal
```

---

## Signing и Security

### Play App Signing (рекомендуется)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLAY APP SIGNING                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ВЫ:                          GOOGLE:                           │
│  ┌──────────────┐            ┌──────────────┐                   │
│  │ Upload Key   │───────────▶│ App Signing  │                   │
│  │ (ваш ключ)  │  Upload    │    Key       │                   │
│  └──────────────┘  AAB      │ (Google хранит)│                  │
│                              └──────────────┘                   │
│                                     │                           │
│                                     ▼                           │
│                              ┌──────────────┐                   │
│                              │ Signed APK   │───▶ Users        │
│                              │ (для users)  │                   │
│                              └──────────────┘                   │
│                                                                  │
│  ПРЕИМУЩЕСТВА:                                                   │
│  ✓ Потеряли upload key? Можно запросить сброс                  │
│  ✓ Google оптимизирует APK для каждого устройства              │
│  ✓ Меньший размер скачивания (App Bundle)                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Хранение Keystore в CI

```bash
# 1. Закодировать keystore в base64
base64 -i release-keystore.jks -o keystore-base64.txt

# 2. Добавить в GitHub Secrets:
# KEYSTORE_BASE64 = содержимое keystore-base64.txt
# KEYSTORE_PASSWORD = пароль keystore
# KEY_ALIAS = alias ключа
# KEY_PASSWORD = пароль ключа

# 3. В workflow декодируем:
echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > release-keystore.jks
```

### Security Best Practices

| Практика | Важность | Реализация |
|----------|----------|------------|
| **Не хранить keystore в git** | Критично | .gitignore, secrets в CI |
| **Play App Signing** | Высокая | Включить в Play Console |
| **Rotate passwords** | Средняя | Каждые 3-6 месяцев |
| **Least privilege** | Высокая | Только релиз-инженеры имеют доступ |
| **Backup keystore** | Критично | Encrypted backup в secure storage |
| **Audit trail** | Высокая | Логирование кто и когда подписывал |

**Статистика:** 80% security breaches в mobile apps связаны с неправильным управлением ключами.

---

## Версионирование

### Semantic Versioning для Android

```kotlin
// build.gradle.kts
android {
    defaultConfig {
        // versionName для пользователей: MAJOR.MINOR.PATCH
        versionName = "2.3.1"

        // versionCode должен всегда увеличиваться
        // Формула: MAJOR * 10000 + MINOR * 100 + PATCH
        // 2.3.1 → 2 * 10000 + 3 * 100 + 1 = 20301
        versionCode = 20301
    }
}
```

### Автоматическое версионирование из Git

```kotlin
// build.gradle.kts
plugins {
    id("io.github.reactivecircus.app-versioning") version "1.3.2"
}

appVersioning {
    // Из git tag v1.2.3 автоматически:
    // versionName = "1.2.3"
    // versionCode = 10203

    overrideVersionName { gitTag, _, _ ->
        gitTag.rawTagName.removePrefix("v")
    }

    overrideVersionCode { gitTag, _, buildNumber ->
        val (major, minor, patch) = gitTag.semanticVersion
        major * 10000 + minor * 100 + patch + (buildNumber ?: 0)
    }
}
```

### CI Version Increment

```yaml
# Автоматический bump версии при merge в main
- name: Bump Version
  run: |
    # Получаем тип изменения из commit message
    COMMIT_MSG=$(git log -1 --pretty=%B)

    if [[ "$COMMIT_MSG" == *"BREAKING"* ]]; then
      VERSION_BUMP="major"
    elif [[ "$COMMIT_MSG" == *"feat:"* ]]; then
      VERSION_BUMP="minor"
    else
      VERSION_BUMP="patch"
    fi

    # Используем semantic-release или custom script
    ./scripts/bump-version.sh $VERSION_BUMP
```

---

## Тестирование в CI

### Пирамида тестов Android

```
                    ┌─────────────┐
                    │    E2E      │  5%   Firebase Test Lab
                    │  (UI Tests) │       Real devices
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │   Integration       │  15%  Roborazzi
                │   Screenshot Tests  │       Compose Preview Tests
                └──────────┬──────────┘
                           │
           ┌───────────────┴───────────────┐
           │         Unit Tests            │  80%  JUnit, MockK
           │   (ViewModel, Repository)     │       Turbine for Flow
           └───────────────────────────────┘
```

### Unit Tests

```yaml
- name: Run Unit Tests with Coverage
  run: ./gradlew testDebugUnitTest jacocoTestReport

- name: Check Coverage Threshold
  run: |
    COVERAGE=$(cat app/build/reports/jacoco/jacocoTestReport/html/index.html | grep -oP 'Total.*?(\d+)%' | grep -oP '\d+')
    if [ "$COVERAGE" -lt 80 ]; then
      echo "Coverage $COVERAGE% is below 80% threshold"
      exit 1
    fi
```

### Screenshot Tests (Roborazzi)

```kotlin
// build.gradle.kts
plugins {
    id("io.github.takahirom.roborazzi") version "1.8.0"
}

dependencies {
    testImplementation("io.github.takahirom.roborazzi:roborazzi:1.8.0")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-compose:1.8.0")
}
```

```kotlin
// ScreenshotTest.kt
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class HomeScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun homeScreen_default() {
        composeTestRule.setContent {
            HomeScreen()
        }

        composeTestRule.onRoot()
            .captureRoboImage("HomeScreen_default.png")
    }
}
```

```bash
# Команды Roborazzi
./gradlew recordRoborazziDebug  # Записать reference screenshots
./gradlew verifyRoborazziDebug  # Сравнить с reference
./gradlew compareRoborazziDebug # Показать diff
```

### Firebase Test Lab

```yaml
- name: Setup gcloud
  uses: google-github-actions/setup-gcloud@v2
  with:
    service_account_key: ${{ secrets.GCP_SA_KEY }}
    project_id: ${{ secrets.GCP_PROJECT_ID }}

- name: Run Tests on Firebase Test Lab
  run: |
    gcloud firebase test android run \
      --type instrumentation \
      --app app/build/outputs/apk/debug/app-debug.apk \
      --test app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk \
      --device model=Pixel6,version=33,locale=en,orientation=portrait \
      --timeout 15m \
      --results-bucket gs://my-bucket/test-results
```

---

## Gradle Optimization

### Build Cache Configuration

```kotlin
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        directory = File(rootDir, "build-cache")
        removeUnusedEntriesAfterDays = 7
    }

    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/cache/")
        isPush = System.getenv("CI") != null  // Push только из CI
        credentials {
            username = System.getenv("CACHE_USER")
            password = System.getenv("CACHE_PASSWORD")
        }
    }
}
```

```properties
# gradle.properties
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.configureondemand=true
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError
```

### GitHub Actions Caching

```yaml
- name: Setup Gradle
  uses: gradle/actions/setup-gradle@v3
  with:
    cache-read-only: ${{ github.ref != 'refs/heads/main' }}
    gradle-home-cache-cleanup: true

# Результат: билды ускоряются на 20-50%
```

### Gradle Managed Devices

```kotlin
// build.gradle.kts
android {
    testOptions {
        managedDevices {
            devices {
                create<ManagedVirtualDevice>("pixel6api33") {
                    device = "Pixel 6"
                    apiLevel = 33
                    systemImageSource = "google"
                }
            }

            groups {
                create("phoneGroup") {
                    targetDevices.add(devices["pixel6api33"])
                }
            }
        }
    }
}
```

```bash
# Запуск тестов на managed devices
./gradlew pixel6api33DebugAndroidTest
./gradlew phoneGroupDebugAndroidTest  # На всей группе
```

---

## Flaky Tests: как бороться

### Причины flakiness

| Причина | Симптом | Решение |
|---------|---------|---------|
| **Async operations** | Тест проходит/падает случайно | IdlingResource |
| **Thread.sleep()** | Медленные, нестабильные тесты | Explicit waits |
| **Shared state** | Тесты влияют друг на друга | Изоляция, @Before/@After |
| **Network calls** | Зависит от интернета | MockWebServer |
| **Animations** | Timing issues | Отключить animations |
| **Race conditions** | Intermittent failures | Synchronization |

### Espresso IdlingResource

```kotlin
// Для async операций
class OkHttp3IdlingResource(
    private val name: String,
    private val dispatcher: Dispatcher
) : IdlingResource {

    override fun getName() = name

    override fun isIdleNow(): Boolean {
        return dispatcher.runningCallsCount() == 0
    }

    override fun registerIdleTransitionCallback(callback: IdlingResource.ResourceCallback) {
        dispatcher.idleCallback = Runnable { callback.onTransitionToIdle() }
    }
}

// Регистрация в тесте
@Before
fun setup() {
    IdlingRegistry.getInstance().register(okHttp3IdlingResource)
}

@After
fun teardown() {
    IdlingRegistry.getInstance().unregister(okHttp3IdlingResource)
}
```

### Retry Strategy в CI

```yaml
# Автоматический retry для flaky tests
- name: Run Tests with Retry
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 15
    max_attempts: 3
    command: ./gradlew connectedCheck
```

```kotlin
// Или через @FlakyTest annotation
@FlakyTest(tolerance = 3)
@Test
fun sometimesFlaky() {
    // Будет retry до 3 раз
}
```

### Test Sharding

```bash
# Firebase Test Lab sharding
gcloud firebase test android run \
  --num-flaky-test-attempts 2 \
  --num-uniform-shards 4  # Разбить на 4 параллельных shard
```

---

## Quality Gates

### Обязательные проверки в CI

```yaml
quality-gates:
  runs-on: ubuntu-latest
  steps:
    # 1. Lint без warnings
    - name: Lint
      run: ./gradlew lint

    # 2. Detekt для Kotlin
    - name: Detekt
      run: ./gradlew detekt

    # 3. Coverage threshold
    - name: Test Coverage
      run: |
        ./gradlew jacocoTestReport
        ./gradlew jacocoTestCoverageVerification

    # 4. APK size limit
    - name: Check APK Size
      run: |
        APK_SIZE=$(stat -f%z app/build/outputs/apk/release/app-release.apk)
        MAX_SIZE=50000000  # 50MB
        if [ $APK_SIZE -gt $MAX_SIZE ]; then
          echo "APK size $APK_SIZE exceeds limit $MAX_SIZE"
          exit 1
        fi

    # 5. Dependency vulnerabilities
    - name: Dependency Check
      run: ./gradlew dependencyCheckAnalyze
```

### Branch Protection Rules

```yaml
# GitHub Branch Protection для main:
# ✅ Require status checks: lint, test, build
# ✅ Require pull request reviews: 1+
# ✅ Require signed commits
# ✅ Do not allow bypassing
```

---

## Типичные ошибки

### 1. Хранение секретов в коде

```kotlin
// ❌ НИКОГДА
android {
    signingConfigs {
        release {
            storeFile file("release.keystore")
            storePassword "password123"  // EXPOSED!
        }
    }
}

// ✅ ПРАВИЛЬНО
android {
    signingConfigs {
        release {
            storeFile file(System.getenv("KEYSTORE_PATH"))
            storePassword System.getenv("KEYSTORE_PASSWORD")
            keyAlias System.getenv("KEY_ALIAS")
            keyPassword System.getenv("KEY_PASSWORD")
        }
    }
}
```

### 2. Игнорирование Gradle Wrapper Validation

```yaml
# ❌ Security risk — wrapper может быть compromised
- run: ./gradlew build

# ✅ Сначала валидация
- uses: gradle/wrapper-validation-action@v2
- run: ./gradlew build
```

### 3. Thread.sleep() в тестах

```kotlin
// ❌ Медленно и flaky
@Test
fun loadData() {
    viewModel.loadData()
    Thread.sleep(5000)  // BAD!
    assertThat(viewModel.state.value).isEqualTo(Success)
}

// ✅ Используй Turbine для Flow
@Test
fun loadData() = runTest {
    viewModel.loadData()
    viewModel.state.test {
        assertThat(awaitItem()).isEqualTo(Loading)
        assertThat(awaitItem()).isEqualTo(Success)
    }
}
```

### 4. Отсутствие cache в CI

```yaml
# ❌ Каждый билд с нуля — 10+ минут
- run: ./gradlew build

# ✅ С кэшем — 2-3 минуты
- uses: gradle/actions/setup-gradle@v3
  with:
    cache-read-only: ${{ github.ref != 'refs/heads/main' }}
- run: ./gradlew build
```

---

## Checklist: Production-Ready CI/CD

```
БАЗОВЫЙ CI:
□ Gradle Wrapper Validation
□ Lint check
□ Unit tests
□ Build APK/AAB
□ Artifact upload

ТЕСТИРОВАНИЕ:
□ Screenshot tests (Roborazzi)
□ Instrumentation tests
□ Firebase Test Lab для release
□ Coverage threshold (80%+)
□ Flaky test strategy

SECURITY:
□ Secrets в GitHub/CI secrets, не в коде
□ Play App Signing включен
□ Keystore backup в secure location
□ Dependency vulnerability scanning
□ Code scanning (CodeQL)

DEPLOYMENT:
□ Fastlane настроен
□ Automatic versioning
□ Internal → Alpha → Beta → Production track
□ Release notes generation
□ Rollback strategy

OPTIMIZATION:
□ Gradle Build Cache (local + remote)
□ Parallelization
□ Conditional jobs
□ Cache dependencies
□ Matrix builds (если нужно)

MONITORING:
□ Build time tracking
□ Test success rate
□ Flaky test detection
□ DORA metrics
```

---

## Проверь себя

**Вопрос 1:** Почему нужна Gradle Wrapper Validation в CI?

<details>
<summary>Ответ</summary>

Gradle Wrapper включает `gradle-wrapper.jar` — бинарный файл, который GitHub не может diff'ить. Злоумышленник может заменить его на malicious версию.

`gradle/wrapper-validation-action` проверяет, что JAR файл соответствует официальным релизам Gradle.

**Security risk:** Compromised wrapper может выполнить произвольный код на CI runner'е с доступом к secrets.
</details>

**Вопрос 2:** Roborazzi vs Paparazzi — когда что использовать?

<details>
<summary>Ответ</summary>

| Критерий | Roborazzi | Paparazzi |
|----------|-----------|-----------|
| **Основа** | Robolectric | LayoutLib |
| **Interaction** | ✅ Можно кликать | ❌ Нельзя |
| **Hilt/DI** | ✅ Совместим | ❌ Несовместим |
| **Compose** | ✅ | ✅ |
| **Views** | ✅ | ✅ |
| **Скорость** | Быстрый | Быстрый |

**Вывод:** Roborazzi более гибкий, используется в Now in Android (Google). Paparazzi проще для статических превью.
</details>

**Вопрос 3:** Как правильно хранить keystore для CI/CD?

<details>
<summary>Ответ</summary>

1. **Base64 encode** keystore файл
2. Сохранить в **GitHub Secrets** или аналогичный vault
3. В workflow **decode** и записать в temporary файл
4. После использования **удалить** файл
5. Включить **Play App Signing** — так Google хранит signing key, а вы только upload key

```bash
# Encode
base64 -i release.keystore > keystore.b64

# In workflow
echo "${{ secrets.KEYSTORE_B64 }}" | base64 -d > release.keystore
./gradlew assembleRelease
rm release.keystore
```
</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "CI/CD слишком сложно для мобильной разработки" | GitHub Actions + базовый workflow = 30 минут настройки. Gradle caching даёт 50%+ ускорение. Сложность оправдана качеством |
| "Все тесты надо запускать на каждый commit" | Стратегия тестирования: unit tests на каждый PR, UI tests на merge to main, full test suite nightly. Оптимизация по feedback loop |
| "Fastlane обязателен для Android" | Fastlane полезен для сложных workflows (screenshots, metadata). Для базового CI/CD достаточно Gradle + GitHub Actions |
| "Firebase Test Lab дорогой" | Spark plan = 10 tests/day бесплатно. Blaze = pay as you go. Для большинства проектов достаточно local Robolectric + minimal device tests |
| "Robolectric = не настоящие тесты" | Robolectric покрывает 90%+ Android API. Для UI логики и ViewModels — достаточно. Device tests только для hardware-specific фич |
| "Gradle Build Cache не работает с CI" | Remote Build Cache работает отлично. GitHub Actions cache action + Gradle Cache = 50-70% reduction build time. Требует правильной настройки |
| "Screenshot tests flaky" | Flakiness от animation timing, font rendering. Roborazzi + compare-with-threshold + disable animations = stable. Платформа важнее теста |
| "Релизы надо делать вручную" | CD = автоматический deploy на beta track при merge to main. Promotion to production — manual trigger. Полная автоматизация возможна |
| "Keystore безопасно хранить в репо" | Никогда! Base64 в Secrets, Play App Signing для production. Upload key можно перевыпустить, signing key — нет |
| "Mono workflow для всего" | Разделяйте: build-test (PR), deploy-beta (main), deploy-prod (release tag). Parallelism для независимых jobs |

---

## CS-фундамент

| CS-концепция | Как применяется в CI/CD |
|--------------|-------------------------|
| **Pipeline Pattern** | CI/CD = последовательность stages: build → test → deploy. Каждый stage может fail-fast. Визуализация как DAG |
| **Caching** | Build Cache, Dependency Cache, Docker Layer Cache. Trade-off: cache invalidation vs rebuild cost. Content-addressable storage |
| **Idempotency** | Повторный запуск pipeline даёт тот же результат. Важно для retry при transient failures. Immutable artifacts |
| **Parallelism** | Matrix builds (разные API levels), parallel test shards. Amdahl's law: sequential parts ограничивают speedup |
| **Artifact Management** | APK/AAB как immutable artifact с версией. Traceability: commit → artifact → deployment. Content hash для integrity |
| **Secrets Management** | Encryption at rest, masked in logs. Principle of least privilege. Rotation policies. Vault integration |
| **Blue-Green / Canary** | Staged rollouts: 1% → 10% → 100%. A/B testing на production. Rollback capability. Play Console native support |
| **Observability** | Build metrics (duration, failure rate), Test metrics (pass rate, flakiness). DORA metrics: lead time, deployment frequency |
| **Immutable Infrastructure** | Each build = clean environment. No state between runs. Docker containers for reproducibility |
| **Fail-Fast** | Быстрые checks первыми (lint, compile), медленные (UI tests) последними. Сокращение feedback loop |

---

## Связанные заметки

- [[ci-cd-pipelines]] — Общие принципы CI/CD
- [[android-gradle-fundamentals]] — Gradle для Android
- [[android-testing]] — Стратегии тестирования Android
- [[android-proguard-r8]] — Obfuscation и оптимизация
- [[android-apk-aab]] — Форматы дистрибуции

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Android CI/CD with GitHub Actions - LogRocket](https://blog.logrocket.com/android-ci-cd-using-github-actions/) | Guide | GitHub Actions setup |
| 2 | [Fastlane + GitHub Actions - Runway](https://www.runway.team/blog/ci-cd-pipeline-android-app-fastlane-github-actions) | Guide | Fastlane integration |
| 3 | [Gradle Build Cache - Gradle Docs](https://docs.gradle.org/current/userguide/build_cache.html) | Docs | Caching strategy |
| 4 | [Roborazzi - GitHub](https://github.com/takahirom/roborazzi) | Tool | Screenshot testing |
| 5 | [Firebase Test Lab CI - Google](https://firebase.google.com/docs/test-lab/android/continuous) | Docs | Cloud testing |
| 6 | [Android App Signing - Google](https://developer.android.com/studio/publish/app-signing) | Docs | Signing best practices |
| 7 | [Flaky Tests Stability - Android Developers](https://developer.android.com/training/testing/instrumented-tests/stability) | Docs | Reducing flakiness |
| 8 | [App Versioning Plugin - ReactiveCircus](https://github.com/ReactiveCircus/app-versioning) | Tool | Git-based versioning |
| 9 | [State of DevOps 2024 - Puppet](https://puppet.com/resources/state-of-devops-report) | Report | DORA metrics |
| 10 | [Test Retries - Shopify](https://shopify.engineering/unreasonable-effectiveness-test-retries-android-monorepo-case-study) | Case Study | Flaky test strategy |
| 11 | [KMP CI/CD 2025 - KMPShip](https://www.kmpship.app/blog/ci-cd-kotlin-multiplatform-2025) | Guide | Modern practices |
| 12 | [Mobile CI/CD Blueprint - DevelopersVoice](https://developersvoice.com/blog/mobile/mobile-cicd-blueprint/) | Guide | 2025 architecture |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

---

[[android-overview|← Android Overview]] | [[ci-cd-pipelines|CI/CD Pipelines →]] | [[android-gradle-fundamentals|Gradle →]]

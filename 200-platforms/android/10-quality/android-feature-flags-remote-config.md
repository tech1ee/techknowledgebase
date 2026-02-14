---
title: "Feature Flags и Remote Config"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
area: android
tags:
  - topic/android
  - topic/feature-flags
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-firebase-platform]]"
  - "[[android-ci-cd]]"
  - "[[android-ecosystem-2026]]"
prerequisites:
  - "[[android-overview]]"
reading_time: 18
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Feature Flags и Remote Config

**Ship to 1% before you ship to 100%.** Feature flags превращают деплой из бинарного события ("выкатили — молимся") в управляемый процесс: сначала 1% пользователей, потом 10%, потом все. Если что-то пошло не так — kill switch мгновенно отключает фичу без нового релиза. Remote Config расширяет эту идею: любой параметр приложения (цвет кнопки, лимит запросов, текст баннера) можно менять с сервера в реальном времени.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание структуры Android-приложения
> - Знакомство с Gradle-зависимостями и Firebase Console
> - Базовое понимание Kotlin Coroutines и Flow

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Feature Flag** | Булевый или многозначный переключатель, управляющий доступом к фиче |
| **Remote Config** | Серверные параметры, загружаемые в runtime |
| **Kill Switch** | Экстренное отключение фичи без релиза |
| **Gradual Rollout** | Постепенное увеличение % пользователей с фичей |
| **A/B Test** | Эксперимент: группа A видит вариант 1, группа B — вариант 2 |
| **Flag Debt** | Накопление неиспользуемых/устаревших флагов в коде |
| **Stale Config** | Устаревшие значения из кеша до первого fetch |
| **Activation Strategy** | Правило, определяющее кому и когда показывать фичу |

---

## Зачем это нужно

### 1. Gradual Rollouts
Новая фича выкатывается на 1% аудитории. Мониторинг crash rate, ANR, latency. Если всё стабильно — 5%, 25%, 100%. Если что-то сломалось — откат без релиза.

### 2. A/B Testing
Два варианта UI, разные алгоритмы ранжирования, другой onboarding flow — feature flags позволяют тестировать гипотезы на живых пользователях и принимать решения на основе данных.

### 3. Kill Switches
Новый платёжный провайдер упал в 3 часа ночи? Kill switch переключает на старый без пробуждения дежурного инженера. Это страховка, которая окупается в первый же инцидент.

### 4. Trunk-Based Development
Feature flags позволяют мержить недоделанные фичи в main — код присутствует, но скрыт за флагом. Никаких долгоживущих feature branches, никаких merge conflicts через месяц.

### 5. Runtime Configuration
Изменение лимитов, таймаутов, URL эндпоинтов, текстов — без публикации нового APK. Особенно ценно для приложений с долгим review-циклом.

---

## Firebase Remote Config

Firebase Remote Config — самый распространённый выбор для Android. Бесплатный, интегрирован с Firebase Console, поддерживает A/B Testing и real-time updates.

### Setup

```kotlin
// build.gradle.kts (app)
dependencies {
    // Firebase BoM управляет версиями всех Firebase-библиотек
    implementation(platform("com.google.firebase:firebase-bom:34.9.0"))

    implementation("com.google.firebase:firebase-config")
    implementation("com.google.firebase:firebase-analytics")
}
```

### Инициализация и default values

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        FirebaseApp.initializeApp(this)

        val remoteConfig = Firebase.remoteConfig
        val configSettings = remoteConfigSettings {
            // В debug — частый fetch; в production — 12 часов
            minimumFetchIntervalInSeconds = if (BuildConfig.DEBUG) 0 else 43200
        }
        remoteConfig.setConfigSettingsAsync(configSettings)

        // In-app defaults — используются до первого fetch
        remoteConfig.setDefaultsAsync(R.xml.remote_config_defaults)
    }
}
```

Default values в `res/xml/remote_config_defaults.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<defaultsMap>
    <entry>
        <key>new_checkout_enabled</key>
        <value>false</value>
    </entry>
    <entry>
        <key>max_retry_count</key>
        <value>3</value>
    </entry>
    <entry>
        <key>promo_banner_text</key>
        <value>Welcome!</value>
    </entry>
</defaultsMap>
```

### Fetch + Activate lifecycle

Remote Config работает в три фазы: **fetch** (загрузка с сервера), **activate** (применение значений), **read** (чтение в коде).

```kotlin
val remoteConfig = Firebase.remoteConfig

// Вариант 1: fetchAndActivate — простой
remoteConfig.fetchAndActivate()
    .addOnCompleteListener { task ->
        if (task.isSuccessful) {
            val newCheckout = remoteConfig.getBoolean("new_checkout_enabled")
            Log.d("RC", "new_checkout_enabled = $newCheckout")
        }
    }

// Вариант 2: Kotlin Coroutines
suspend fun fetchConfig() {
    try {
        Firebase.remoteConfig.fetchAndActivate().await()
        val enabled = Firebase.remoteConfig.getBoolean("new_checkout_enabled")
        // Использовать значение
    } catch (e: Exception) {
        // Fallback на default values
    }
}
```

**Важно:** `fetch()` загружает значения в кеш, но НЕ применяет их. `activate()` применяет закешированные значения. `fetchAndActivate()` делает оба шага. Разделение полезно, когда нужно применить новые значения только при следующем запуске приложения.

### Conditions (правила таргетинга)

Firebase Console позволяет задавать условия для параметров:

| Условие | Пример |
|---------|--------|
| **Percentage rollout** | 10% пользователей |
| **App version** | >= 5.0.0 |
| **Country/Region** | Только Казахстан, Узбекистан |
| **OS type** | Android / iOS |
| **User in segment** | Firebase Analytics audience |
| **Custom property** | `user_tier == "premium"` |
| **Date/Time** | После 2026-03-01 |

Условия комбинируются через AND/OR. Один параметр может иметь разные значения для разных условий.

### Real-time Remote Config

Начиная с Firebase BoM 31.3.0+, доступны real-time updates через SSE (Server-Sent Events). Вместо периодического polling приложение получает push-уведомление при изменении конфига:

```kotlin
remoteConfig.addOnConfigUpdateListener(object : ConfigUpdateListener {
    override fun onUpdate(configUpdate: ConfigUpdate) {
        Log.d("RC", "Updated keys: ${configUpdate.updatedKeys}")

        // Активируем новые значения
        remoteConfig.activate().addOnCompleteListener { task ->
            if (task.isSuccessful) {
                // Обновить UI с новыми значениями
                val promoText = remoteConfig.getString("promo_banner_text")
                updatePromoBanner(promoText)
            }
        }
    }

    override fun onError(error: FirebaseRemoteConfigException) {
        Log.w("RC", "Config update error", error)
    }
})
```

**Требование:** в Google Cloud Console должен быть включен Firebase Remote Config Realtime API. Real-time updates обходят `minimumFetchIntervalInSeconds` — изменения приходят мгновенно.

### Интеграция с Firebase A/B Testing

Firebase A/B Testing позволяет создавать эксперименты прямо из Firebase Console:

1. **Создать эксперимент** → выбрать Remote Config
2. **Определить аудиторию** — % пользователей, страна, версия
3. **Задать варианты** — Control (текущее значение) + Treatment (новое)
4. **Выбрать метрику** — retention, revenue, crash-free users, custom event
5. **Запустить** — Firebase автоматически распределяет пользователей

На стороне клиента код одинаковый — `getBoolean("feature_x")` возвращает значение в зависимости от группы. Вся логика эксперимента — на сервере.

---

## LaunchDarkly

LaunchDarkly — enterprise-решение для feature management. Позиционируется как стандарт для крупных команд с требованиями к audit log, approval workflows и сложному таргетингу.

### Setup

```kotlin
// build.gradle.kts (app)
dependencies {
    implementation("com.launchdarkly:launchdarkly-android-client-sdk:5.9.2")
}
```

### Инициализация

```kotlin
// Application.onCreate()
val ldConfig = LDConfig.Builder(AutoEnvAttributes.Enabled)
    .mobileKey("mob-xxxx-your-mobile-key")
    .build()

val context = LDContext.builder(ContextKind.DEFAULT, "user-key-123")
    .set("email", "user@example.com")
    .set("plan", "premium")
    .set("country", "KZ")
    .build()

// init возвращает Future — блокирует до получения флагов
val client = LDClient.init(application, ldConfig, context, 5) // 5 sec timeout
```

### Использование флагов

```kotlin
val showNewCheckout = LDClient.get().boolVariation("new-checkout", false)

// String variation с fallback
val bannerColor = LDClient.get().stringVariation("banner-color", "#FFFFFF")

// JSON variation для сложных конфигов
val config = LDClient.get().jsonValueVariation("onboarding-config", LDValue.ofNull())
```

### Ключевые возможности

| Возможность | Описание |
|------------|----------|
| **Targeting Rules** | Комбинации условий: user attributes, segments, percentages |
| **User Segments** | Группы пользователей, переиспользуемые между флагами |
| **Audit Log** | Полная история: кто, когда, что изменил |
| **Approval Workflows** | Требование approve перед включением флага в production |
| **Relay Proxy** | Self-hosted прокси для данных — актуально для on-premise |
| **Experimentation** | A/B тесты с интеграцией в analytics |
| **Contexts** | Мульти-контекстная оценка: user + device + organization |

### Когда выбирать LaunchDarkly

- Команда 50+ разработчиков с enterprise-требованиями
- Нужны approval workflows и audit trail для compliance
- Сложный таргетинг по множеству атрибутов
- Бюджет позволяет (от $10K/год для стартовых планов)

---

## Open-Source альтернативы

### Unleash

**Unleash** — наиболее зрелая open-source платформа для feature management. Self-hosted или облачный.

```kotlin
// build.gradle.kts
dependencies {
    implementation("io.getunleash:unleash-android:0.5.0")
}
```

```kotlin
val unleash = DefaultUnleash(
    androidContext = applicationContext,
    unleashConfig = UnleashConfig.newBuilder()
        .proxyUrl("https://your-unleash-proxy.com/api/frontend")
        .clientKey("your-proxy-client-key")
        .pollingMode(UnleashConfig.PollingMode.Autopolling(pollIntervalInSeconds = 60))
        .build()
)

val enabled = unleash.isEnabled("new-checkout")
```

**Activation strategies** — встроенные правила:
- `standard` — вкл/выкл
- `gradualRollout` — % пользователей
- `userIds` — конкретные пользователи
- `remoteAddress` — по IP
- Custom strategies

### Flagsmith

**Flagsmith** — feature flags + remote config в одном. Open-source (BSD-3), self-hosted или облачный.

Ключевые преимущества:
- Feature flags И remote config (ключ-значение) в одном инструменте
- REST API + Webhooks для интеграций
- Edge Proxy для low-latency
- Встроенная аналитика использования флагов

### GrowthBook

**GrowthBook** — ориентирован на A/B testing + feature flags. Open-source (MIT).

Ключевые преимущества:
- Статистический движок для экспериментов (Bayesian + Frequentist)
- Lightweight SDK — evaluates locally, без сетевых запросов при каждой проверке
- Интеграция с warehouse (BigQuery, Snowflake, Redshift)
- Визуальный редактор экспериментов

### Сравнительная таблица open-source решений

| Критерий | Unleash | Flagsmith | GrowthBook |
|----------|---------|-----------|------------|
| **Лицензия** | Apache 2.0 | BSD-3 | MIT |
| **Фокус** | Feature flags | Flags + Config | A/B + Flags |
| **Android SDK** | Да | Через REST | Kotlin SDK |
| **Self-hosted** | Docker / Helm | Docker / Helm | Docker |
| **A/B Testing** | Enterprise | Нет | Ядро продукта |
| **Activation rules** | 6 встроенных | Segments | Attributes |
| **UI Console** | Хороший | Простой, быстрый | Ориентирован на эксперименты |
| **Бесплатный план** | 2 environments | Неограниченные flags | Полностью бесплатный self-hosted |

---

## Architecture Patterns

### Абстракция: FeatureFlagProvider

Главное правило — **не привязывайся к конкретной реализации**. Сегодня Firebase, завтра LaunchDarkly, послезавтра — собственный сервис. Интерфейс абстрагирует провайдера:

```kotlin
interface FeatureFlagProvider {
    fun isEnabled(flag: String, default: Boolean = false): Boolean
    fun getString(key: String, default: String = ""): String
    fun getLong(key: String, default: Long = 0L): Long
    fun getDouble(key: String, default: Double = 0.0): Double

    /** Flow для реактивного наблюдения за изменениями */
    fun observeFlag(flag: String): Flow<Boolean>

    /** Принудительный fetch с сервера */
    suspend fun refresh()
}
```

### Firebase-реализация

```kotlin
class FirebaseFeatureFlagProvider(
    private val remoteConfig: FirebaseRemoteConfig
) : FeatureFlagProvider {

    override fun isEnabled(flag: String, default: Boolean): Boolean {
        return remoteConfig.getBoolean(flag)
    }

    override fun getString(key: String, default: String): String {
        return remoteConfig.getString(key).ifEmpty { default }
    }

    override fun getLong(key: String, default: Long): Long {
        return remoteConfig.getLong(key)
    }

    override fun getDouble(key: String, default: Double): Double {
        return remoteConfig.getDouble(key)
    }

    override fun observeFlag(flag: String): Flow<Boolean> = callbackFlow {
        // Начальное значение
        trySend(remoteConfig.getBoolean(flag))

        val listener = ConfigUpdateListener(
            onUpdate = { configUpdate ->
                if (flag in configUpdate.updatedKeys) {
                    remoteConfig.activate().addOnSuccessListener {
                        trySend(remoteConfig.getBoolean(flag))
                    }
                }
            },
            onError = { /* log */ }
        )
        remoteConfig.addOnConfigUpdateListener(listener)

        awaitClose { /* remove listener if API supports it */ }
    }

    override suspend fun refresh() {
        remoteConfig.fetchAndActivate().await()
    }
}
```

### DI (Hilt)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object FeatureFlagModule {

    @Provides
    @Singleton
    fun provideFeatureFlagProvider(
        remoteConfig: FirebaseRemoteConfig
    ): FeatureFlagProvider {
        return FirebaseFeatureFlagProvider(remoteConfig)
    }

    @Provides
    @Singleton
    fun provideRemoteConfig(): FirebaseRemoteConfig {
        return Firebase.remoteConfig.apply {
            setConfigSettingsAsync(
                remoteConfigSettings {
                    minimumFetchIntervalInSeconds =
                        if (BuildConfig.DEBUG) 0 else 43200
                }
            )
            setDefaultsAsync(R.xml.remote_config_defaults)
        }
    }
}
```

### Compose-интеграция: feature-gated Composable

```kotlin
@Composable
fun FeatureGate(
    flag: String,
    featureFlagProvider: FeatureFlagProvider = hiltViewModel<FeatureGateViewModel>().provider,
    fallback: @Composable () -> Unit = {},
    content: @Composable () -> Unit
) {
    val isEnabled by featureFlagProvider
        .observeFlag(flag)
        .collectAsStateWithLifecycle(initialValue = false)

    if (isEnabled) {
        content()
    } else {
        fallback()
    }
}

// Использование
@Composable
fun CheckoutScreen() {
    FeatureGate(flag = "new_checkout_enabled") {
        NewCheckoutFlow()
    }
    // Или с fallback:
    FeatureGate(
        flag = "redesigned_cart",
        fallback = { OldCartView() }
    ) {
        NewCartView()
    }
}
```

### Compile-time vs Runtime flags

| Критерий | BuildConfig (compile-time) | Remote Config (runtime) |
|----------|---------------------------|------------------------|
| **Изменение** | Требует новый билд | Мгновенно, без билда |
| **Использование** | Debug/release варианты, API endpoints | Rollouts, A/B тесты, kill switches |
| **Безопасность** | Статически определён в APK | Значение приходит с сервера |
| **Скорость** | Мгновенный доступ | Требует fetch (задержка на старте) |
| **Рекомендация** | Окружения, build flavors | Фичи, эксперименты, конфиги |

**Правило:** если значение не должно меняться между релизами одной версии — compile-time. Если может понадобиться изменить без релиза — runtime.

---

## Сравнительная таблица платформ

| Критерий | Firebase RC | LaunchDarkly | Unleash |
|----------|------------|--------------|---------|
| **Цена** | Бесплатно | От $10K/год | Open-source / от $80/мес |
| **Хостинг** | Google Cloud | SaaS | Self-hosted / Cloud |
| **Real-time** | SSE (BoM 31.3+) | Streaming | Polling (Enterprise: SSE) |
| **A/B Testing** | Firebase A/B | Experimentation | Enterprise only |
| **Targeting** | Conditions (5-7 типов) | Rules + Segments (мощный) | Strategies (6+ типов) |
| **Android SDK** | Отличный | Зрелый (v5.9+) | Базовый |
| **Audit Log** | Нет | Полный | Enterprise |
| **Approval Flow** | Нет | Да | Enterprise |
| **Кривая входа** | Низкая | Средняя | Средняя |
| **Лучше для** | Стартапы, indie | Enterprise | Self-hosted/compliance |

---

## Подводные камни

### 1. Stale Cache на первом запуске

**Проблема:** при первом запуске приложения Remote Config ещё не загрузился, и используются default values из XML. Пользователь видит старое поведение, а после fetch+activate — внезапно новое.

**Решение:**
- Задавать разумные defaults, которые совпадают с текущим production-состоянием
- Показывать splash screen до завершения `fetchAndActivate()`
- Использовать `fetchAndActivate()` в `Application.onCreate()` и кешировать результат

### 2. Race Conditions на старте

**Проблема:** экран уже отрисован, а fetch ещё не завершился. Флаг возвращает default, через секунду — реальное значение. UI "мигает".

**Решение:**
```kotlin
// Блокировать навигацию до готовности
class SplashViewModel @Inject constructor(
    private val flags: FeatureFlagProvider
) : ViewModel() {

    val isReady = flow {
        flags.refresh() // Дождаться fetch
        emit(true)
    }.stateIn(viewModelScope, SharingStarted.Lazily, false)
}
```

### 3. Flag Debt

**Проблема:** через год в проекте 200 флагов, из которых 150 давно включены на 100% и никому не нужны. Код засорён `if (isEnabled("..."))` блоками.

**Решение:**
- Каждый флаг имеет дату создания и owner'а
- Автоматический alert после 90 дней "жизни" флага
- Линтер или Detekt-правило: предупреждение при превышении лимита активных флагов
- Процесс: при rollout на 100% — задача в backlog на удаление флага

### 4. Безопасность: чувствительные флаги

**Проблема:** Remote Config значения загружаются на клиент и могут быть прочитаны через декомпиляцию или перехват трафика. Не стоит хранить в них секреты или бизнес-логику, которую пользователь не должен видеть.

**Решение:**
- Чувствительные флаги — только server-side (API возвращает результат решения, а не сам флаг)
- Не передавать через Remote Config: ключи API, цены до публикации, внутренние URL
- Использовать certificate pinning для защиты трафика

### 5. Тестирование

**Проблема:** как тестировать код, если поведение зависит от серверного флага?

**Решение:** абстракция `FeatureFlagProvider` позволяет подставлять fake-реализацию:

```kotlin
class FakeFeatureFlagProvider(
    private val flags: Map<String, Boolean> = emptyMap()
) : FeatureFlagProvider {
    override fun isEnabled(flag: String, default: Boolean) = flags[flag] ?: default
    // ... остальные методы
}

// В тесте
val provider = FakeFeatureFlagProvider(
    mapOf("new_checkout_enabled" to true)
)
```

---

## Проверь себя

**Q1:** Чем отличается `fetch()` от `fetchAndActivate()` в Firebase Remote Config?

**A1:** `fetch()` загружает новые значения с сервера в локальный кеш, но не применяет их — приложение продолжает использовать старые значения. `fetchAndActivate()` делает оба шага: загружает и сразу применяет. Разделение полезно, когда новые значения нужно применить только при следующем запуске, чтобы избежать "мигания" UI.

---

**Q2:** Почему нельзя хранить API-ключи в Remote Config?

**A2:** Значения Remote Config загружаются на клиент и хранятся в локальном кеше. Они могут быть извлечены через декомпиляцию APK, перехват трафика или root-доступ. Чувствительные данные должны оставаться на сервере — клиент получает только результат решения (например, "использовать провайдер А"), а не сам секрет.

---

**Q3:** Как избежать "мигания" UI при загрузке флагов на старте приложения?

**A3:** Три подхода: (1) показывать splash screen до завершения `fetchAndActivate()`, (2) задавать in-app defaults, идентичные текущему production-состоянию, чтобы даже при задержке fetch пользователь видел корректный UI, (3) при использовании real-time updates — активировать изменения только между экранами, а не посреди текущего.

---

## Ключевые карточки

| # | Вопрос | Ответ |
|---|--------|-------|
| 1 | Что такое kill switch? | Флаг для экстренного отключения фичи без нового релиза — мгновенный откат через консоль |
| 2 | Зачем нужна абстракция `FeatureFlagProvider`? | Отвязывает бизнес-логику от конкретного провайдера (Firebase, LaunchDarkly, Unleash) — замена без изменения кода фич |
| 3 | Что такое flag debt? | Накопление устаревших флагов, которые давно включены на 100%, но не удалены из кода — усложняет поддержку и чтение |
| 4 | Compile-time vs runtime flag? | Compile-time (BuildConfig) — для build variants и окружений; runtime (Remote Config) — для rollouts, экспериментов, kill switches |
| 5 | Как работает real-time Remote Config? | Firebase использует SSE (Server-Sent Events) — приложение держит соединение и получает push при изменении параметров, обходя `minimumFetchIntervalInSeconds` |

---

## Куда дальше

- [[android-firebase-platform]] — Firebase-экосистема: Analytics, Crashlytics, Cloud Messaging
- [[android-ci-cd]] — интеграция feature flags в CI/CD pipeline
- [[android-analytics-crash-reporting]] — метрики для принятия решений по rollout
- [[android-testing]] — тестирование кода с feature flags через fake-реализации
- [[android-ecosystem-2026]] — тренды Android-разработки

---

## Источники

- [Firebase Remote Config — Get Started (Android)](https://firebase.google.com/docs/remote-config/android/get-started) — официальная документация Firebase
- [Real-time Remote Config](https://firebase.google.com/docs/remote-config/real-time) — SSE-обновления в реальном времени
- [Firebase A/B Testing with Remote Config](https://firebase.google.com/docs/ab-testing/abtest-config) — создание экспериментов
- [LaunchDarkly Android SDK Reference](https://launchdarkly.com/docs/sdk/client-side/android) — документация LaunchDarkly
- [Unleash Android SDK](https://docs.getunleash.io/reference/sdks/android) — open-source feature flags
- [Unleash Feature Flag Best Practices](https://docs.getunleash.io/guides/feature-flag-best-practices) — 11 принципов управления флагами
- [Feature Flags — A Successful Architecture (Jeroen Mols)](https://jeroenmols.com/blog/2019/09/12/featureflagsarchitecture/) — архитектура feature flags в Android
- [Kotlin Flow + Firebase Real-time Remote Config in MVVM/Clean Architecture](https://medium.com/bforbank-tech/using-kotlin-flow-and-firebase-realtime-remote-config-in-an-mvvm-clean-architecture-e9934f4b76ba) — reactive подход
- [Android Feature Flag Implementation with Firebase + Kotlin Flow + Compose (droidcon 2025)](https://www.droidcon.com/2025/01/21/android-feature-flag-implementation-with-firebase-remote-config-kotlin-flow-jetpack-compose/) — современный подход
- [The Best Feature Flag Providers for Apps in 2025 (WorkOS)](https://workos.com/blog/the-best-feature-flag-providers-for-apps-in-2025) — обзор провайдеров
- [Flagsmith vs GrowthBook Comparison](https://www.flagsmith.com/compare/flagsmith-vs-growthbook) — сравнение open-source решений

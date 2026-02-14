---
title: "Аналитика и крэш-репортинг в Android"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
area: android
tags:
  - topic/android
  - topic/analytics
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-firebase-platform]]"
  - "[[android-permissions-security]]"
  - "[[android-ecosystem-2026]]"
prerequisites:
  - "[[android-overview]]"
reading_time: 20
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Аналитика и крэш-репортинг в Android

**"You can't improve what you don't measure."** Без аналитики продуктовые решения строятся на предположениях. Без crash reporting баги обнаруживаются только по отзывам в Google Play -- когда уже поздно. Эта статья -- полный гайд по инструментам, паттернам и best practices для сбора данных о поведении пользователей и стабильности Android-приложения.

> **Prerequisites:**
> - [[android-overview]] -- базовое понимание структуры Android-приложения
> - Знакомство с Gradle и dependency management
> - Базовое понимание Kotlin coroutines (для async analytics calls)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Crash** | Неперехваченное исключение, приводящее к завершению процесса |
| **ANR** | Application Not Responding -- UI thread заблокирован >5 сек |
| **Non-fatal exception** | Перехваченное исключение, залогированное без краша |
| **Crash-free rate** | Доля сессий/пользователей без крэшей |
| **Event** | Дискретное действие пользователя или системы (screen_view, purchase) |
| **User property** | Атрибут пользователя (plan_type, locale), привязанный ко всем событиям |
| **Funnel** | Последовательность шагов, по которой мы измеряем конверсию |
| **Cohort** | Группа пользователей, объединённая общим признаком |
| **Retention** | Доля пользователей, вернувшихся через N дней |
| **Breadcrumb** | Лог действий пользователя перед крэшем |
| **Obfuscation mapping** | Файл маппинга R8/ProGuard для деобфускации стектрейсов |
| **Trace** | Измерение длительности операции (app start, network request) |

---

## Зачем это нужно

### Crash reporting -- деньги и репутация

Каждый crash -- потенциальная потеря пользователя. По данным Google, приложения с crash-free rate ниже 99% теряют до 2x больше пользователей. Google Play Console использует Android Vitals для ранжирования -- высокий crash rate снижает visibility в поиске.

**Реальные цифры:**
- 1% crash rate = ~10 000 крэшей при 1M DAU
- Средний пользователь после 2 крэшей удаляет приложение
- ANR ещё хуже -- пользователь видит системный диалог "Wait / Close"

### Analytics -- продуктовые решения на данных

Без аналитики вы не узнаете:
- Какие фичи реально используются (а какие можно удалить)
- Где пользователи уходят из воронки
- Как изменения влияют на retention
- Какой сегмент пользователей приносит выручку

---

## Crash Reporting: глубокое погружение

### Firebase Crashlytics

Стандарт индустрии для мобильных крэшей. Бесплатный, интегрирован с Firebase ecosystem.

**Настройка:**

```kotlin
// build.gradle.kts (project)
plugins {
    id("com.google.gms.google-services") version "4.4.2" apply false
    id("com.google.firebase.crashlytics") version "3.0.3" apply false
}

// build.gradle.kts (app)
plugins {
    id("com.google.gms.google-services")
    id("com.google.firebase.crashlytics")
}

dependencies {
    // Firebase BoM контролирует версии всех Firebase SDK
    implementation(platform("com.google.firebase:firebase-bom:33.8.0"))
    implementation("com.google.firebase:firebase-crashlytics")
    implementation("com.google.firebase:firebase-analytics") // для breadcrumbs
}
```

**Custom keys и breadcrumbs:**

```kotlin
// Добавляем контекст к крэш-репортам
Firebase.crashlytics.apply {
    setUserId("user_12345")
    setCustomKey("subscription_plan", "premium")
    setCustomKey("screen", "checkout")
    setCustomKey("cart_items_count", 3)
}

// Breadcrumb через Analytics -- автоматически попадёт в Crashlytics
Firebase.analytics.logEvent("add_to_cart") {
    param("item_id", "SKU_001")
    param("price", 29.99)
}
```

**Non-fatal exceptions -- перехватываем, но логируем:**

```kotlin
try {
    val result = riskyApiCall()
} catch (e: ApiException) {
    // Приложение не крэшится, но мы видим проблему в dashboard
    Firebase.crashlytics.recordException(e)
    // Показываем пользователю friendly error
    showErrorSnackbar("Something went wrong")
}
```

**ANR tracking:** Crashlytics автоматически детектирует ANR начиная с SDK 18.3.0+. В dashboard ANR отображаются отдельной вкладкой с полным стектрейсом заблокированного main thread.

**Obfuscation mapping upload (CI/CD):**

```bash
# В CI pipeline после каждого release build
# Gradle plugin загружает mapping автоматически при:
# 1. Подключении com.google.firebase.crashlytics plugin
# 2. Включении minification: isMinifyEnabled = true
# Mapping файл: app/build/outputs/mapping/{variant}/mapping.txt
```

> **Важно:** Без mapping file стектрейсы в dashboard будут обфусцированными -- `a.b.c()` вместо `UserRepository.fetchUser()`. Автоматизируйте upload через CI.

### Sentry

Мощная альтернатива с self-hosted опцией и глубоким performance tracing.

```kotlin
// build.gradle.kts (app)
dependencies {
    implementation("io.sentry:sentry-android:8.31.0")
}
```

```xml
<!-- AndroidManifest.xml -->
<meta-data
    android:name="io.sentry.dsn"
    android:value="https://examplePublicKey@o0.ingest.sentry.io/0" />
<meta-data
    android:name="io.sentry.traces.sample-rate"
    android:value="0.2" /> <!-- 20% транзакций -->
```

**Преимущества Sentry:**
- **Performance tracing**: distributed traces через backend + mobile
- **Source context**: фрагменты кода вокруг строки с ошибкой в dashboard
- **Feature flags**: SDK хранит до 100 последних evaluations и привязывает к ошибкам
- **Self-hosted**: полный контроль над данными (on-premise Docker deployment)
- **Release health**: crash-free rate, adoption rate, sessions по release

### Bugsnag

Фокус на стабильности -- Stability Score как центральная метрика.

**Ключевые фичи:**
- **Stability Score**: процент error-free сессий, трекается между релизами
- **Performance Score** (2025): дополняет Stability Score метриками скорости
- **App Hangs**: детектирует не только ANR, но и короткие freezes UI
- **Release tracking**: автоматическое сравнение стабильности между версиями

### Сравнительная таблица: Crash Reporting

| Критерий | Firebase Crashlytics | Sentry | Bugsnag |
|----------|---------------------|--------|---------|
| **Цена** | Бесплатно | Free tier + от $29/мес | От $47.90/мес |
| **Self-hosted** | Нет | Да (Docker) | Нет |
| **ANR tracking** | Да | Да | Да + App Hangs |
| **Performance tracing** | Отдельный SDK | Встроен | Performance Score |
| **Breadcrumbs** | Через Analytics | Встроенные | Встроенные |
| **Native crashes (NDK)** | Да | Да | Да |
| **Source maps / deobfuscation** | Mapping upload | Source context | Mapping upload |
| **Stability Score** | Crash-free users | Release health | Stability Score |
| **Интеграции** | Firebase ecosystem | Jira, Slack, PagerDuty, 100+ | Jira, Slack, 50+ |
| **Лучше всего для** | Маленькие/средние проекты | Крупные проекты, self-hosted | Enterprise, SLA |

---

## Analytics Platforms

### Firebase Analytics (GA4)

Бесплатная аналитика, глубоко интегрированная с Firebase ecosystem.

**Характеристики:**
- **Бесплатно** -- без ограничений по объёму данных
- До **500 типов событий** (distinct event names)
- До **25 user properties**
- **Automatic events**: `first_open`, `session_start`, `screen_view`, `app_update`
- **DebugView**: real-time просмотр событий с устройства
- Экспорт в **BigQuery** для произвольных SQL-запросов

```kotlin
// Логирование событий
Firebase.analytics.logEvent("purchase_completed") {
    param("item_id", "SKU_001")
    param("item_name", "Premium Plan")
    param("price", 9.99)
    param("currency", "USD")
    param("payment_method", "google_pay")
}

// User properties -- привязываются ко всем последующим событиям
Firebase.analytics.setUserProperty("subscription_tier", "premium")
Firebase.analytics.setUserProperty("app_theme", "dark")
```

**DebugView** -- незаменимый инструмент при разработке:

```bash
# Включаем debug mode для конкретного пакета
adb shell setprop debug.firebase.analytics.app com.example.myapp

# Отключаем
adb shell setprop debug.firebase.analytics.app .none.
```

### Amplitude

Product analytics с мощным поведенческим анализом.

```kotlin
// Инициализация
val amplitude = Amplitude(
    Configuration(
        apiKey = "YOUR_API_KEY",
        context = applicationContext,
        defaultTracking = DefaultTrackingOptions(
            sessions = true,
            appLifecycles = true,
            screenViews = true
        )
    )
)

// Трекинг событий
amplitude.track("subscription_started", mapOf(
    "plan" to "annual",
    "price" to 99.99,
    "trial" to true
))

// Идентификация пользователя
amplitude.identify(Identify().apply {
    set("subscription_plan", "premium")
    set("company_size", "50-200")
    setOnce("first_login_date", "2026-02-14")
})
```

**Сила Amplitude:**
- **Funnels**: визуализация конверсии между шагами
- **Retention curves**: D1, D7, D30 retention по когортам
- **Cohort analysis**: сегментация по поведению
- **Predictions**: ML-модели для прогноза churn и conversion
- **Frustration analytics** (v1.22.0+): автоматический трекинг rage clicks и dead clicks
- **Network tracking** (v1.21.0+): автоматический мониторинг сетевых запросов через OkHttp

### Mixpanel

Event-based аналитика с мощными инструментами для продуктовых команд.

**Ключевые возможности:**
- **Funnels**: конверсионные воронки с breakdown по свойствам
- **Flows**: визуализация реальных путей пользователей
- **Impact reports**: корреляция между feature adoption и retention
- **Cohort analysis**: детальная сегментация
- Real-time данные (в отличие от Firebase с задержкой до 24 часов)

### Сравнительная таблица: Analytics

| Критерий | Firebase Analytics | Amplitude | Mixpanel |
|----------|-------------------|-----------|----------|
| **Free tier** | Безлимитный | 200K MTU | 1M events/мес |
| **Платный от** | Бесплатно (GA4) | ~$49/мес | ~$140/мес (1.5M events) |
| **Лимит событий** | 500 типов | Безлимитно | 5000 типов (soft limit) |
| **Real-time** | DebugView only | Да | Да |
| **Retention analysis** | Базовый | Продвинутый | Продвинутый |
| **Funnels** | Базовые | Продвинутые | Продвинутые |
| **Predictive analytics** | Нет | Да (ML) | Нет |
| **Data export** | BigQuery (бесплатно) | S3/GCS (платно) | S3/GCS (платно) |
| **Задержка данных** | До 24 часов | Минуты | Real-time |
| **Лучше для** | MVP, маленькие команды | Product-led growth | Marketing + Product |

---

## Implementation Patterns

### Analytics abstraction layer

Главный паттерн -- **абстракция над провайдерами**. Никогда не вызывайте `Firebase.analytics.logEvent()` напрямую из ViewModel или UseCase. Завтра вы добавите Amplitude, послезавтра -- Mixpanel, а через месяц уберёте Firebase.

```kotlin
// === Контракт ===
interface AnalyticsTracker {
    fun trackEvent(name: String, params: Map<String, Any> = emptyMap())
    fun setUserProperty(key: String, value: String)
    fun setUserId(id: String?)
    fun trackScreen(screenName: String)
}

// === Firebase реализация ===
class FirebaseTracker : AnalyticsTracker {

    override fun trackEvent(name: String, params: Map<String, Any>) {
        Firebase.analytics.logEvent(name) {
            params.forEach { (key, value) ->
                when (value) {
                    is String -> param(key, value)
                    is Long -> param(key, value)
                    is Double -> param(key, value)
                    is Int -> param(key, value.toLong())
                    is Boolean -> param(key, if (value) 1L else 0L)
                }
            }
        }
    }

    override fun setUserProperty(key: String, value: String) {
        Firebase.analytics.setUserProperty(key, value)
    }

    override fun setUserId(id: String?) {
        Firebase.analytics.setUserId(id)
    }

    override fun trackScreen(screenName: String) {
        Firebase.analytics.logEvent(FirebaseAnalytics.Event.SCREEN_VIEW) {
            param(FirebaseAnalytics.Param.SCREEN_NAME, screenName)
        }
    }
}

// === Amplitude реализация ===
class AmplitudeTracker(
    private val amplitude: Amplitude
) : AnalyticsTracker {

    override fun trackEvent(name: String, params: Map<String, Any>) {
        amplitude.track(name, params)
    }

    override fun setUserProperty(key: String, value: String) {
        amplitude.identify(Identify().apply { set(key, value) })
    }

    override fun setUserId(id: String?) {
        amplitude.setUserId(id)
    }

    override fun trackScreen(screenName: String) {
        amplitude.track("screen_viewed", mapOf("screen_name" to screenName))
    }
}

// === Composite: отправляем во все провайдеры ===
class CompositeTracker(
    private val trackers: List<AnalyticsTracker>
) : AnalyticsTracker {

    override fun trackEvent(name: String, params: Map<String, Any>) {
        trackers.forEach { it.trackEvent(name, params) }
    }

    override fun setUserProperty(key: String, value: String) {
        trackers.forEach { it.setUserProperty(key, value) }
    }

    override fun setUserId(id: String?) {
        trackers.forEach { it.setUserId(id) }
    }

    override fun trackScreen(screenName: String) {
        trackers.forEach { it.trackScreen(screenName) }
    }
}
```

**DI setup (Hilt):**

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AnalyticsModule {

    @Provides
    @Singleton
    fun provideAnalyticsTracker(
        @ApplicationContext context: Context
    ): AnalyticsTracker {
        val trackers = mutableListOf<AnalyticsTracker>()

        trackers.add(FirebaseTracker())

        if (!BuildConfig.DEBUG) {
            val amplitude = Amplitude(
                Configuration(
                    apiKey = BuildConfig.AMPLITUDE_API_KEY,
                    context = context
                )
            )
            trackers.add(AmplitudeTracker(amplitude))
        }

        return CompositeTracker(trackers)
    }
}
```

### Event naming conventions

Консистентность в именовании -- ключ к полезной аналитике.

**Правила:**
1. **snake_case** -- `purchase_completed`, не `PurchaseCompleted`
2. **Максимум 40 символов** (ограничение Firebase)
3. **Namespace по фиче**: `onboarding_step_completed`, `checkout_payment_selected`
4. **Глагол в прошедшем времени**: `button_clicked`, `screen_viewed`, `item_added`
5. **Не более 25 параметров** на событие (ограничение Firebase)

```kotlin
// ❌ Плохо
tracker.trackEvent("click") // Слишком общее
tracker.trackEvent("User Pressed The Buy Button") // Пробелы, регистр
tracker.trackEvent("ev_123") // Непонятно

// ✅ Хорошо
tracker.trackEvent("purchase_button_clicked", mapOf(
    "screen" to "product_detail",
    "product_id" to "SKU_001",
    "price" to 29.99
))
```

### User properties vs event parameters

| Аспект | User Property | Event Parameter |
|--------|--------------|-----------------|
| **Что** | Атрибут пользователя | Контекст конкретного действия |
| **Когда менять** | При изменении состояния | На каждое событие |
| **Примеры** | `subscription_plan`, `locale` | `item_id`, `price`, `screen` |
| **Лимит Firebase** | 25 custom properties | 25 параметров на событие |
| **Фильтрация** | По всем событиям | Только по конкретному событию |

---

## Performance Monitoring

### Firebase Performance

Автоматический и кастомный мониторинг производительности.

**Automatic traces (из коробки):**
- **App start**: cold start, warm start время
- **Screen rendering**: slow frames (>16ms), frozen frames (>700ms)
- **Network requests**: latency, payload size, success rate по URL pattern

**Custom traces:**

```kotlin
// Измеряем время загрузки ленты
val trace = Firebase.performance.newTrace("feed_load")
trace.start()

try {
    val items = repository.loadFeed()
    trace.putMetric("items_count", items.size.toLong())
    trace.putAttribute("cache_hit", if (fromCache) "true" else "false")
} finally {
    trace.stop() // Длительность автоматически
}

// Или с extension function
suspend fun <T> measureTrace(
    traceName: String,
    block: suspend (Trace) -> T
): T {
    val trace = Firebase.performance.newTrace(traceName)
    trace.start()
    return try {
        block(trace)
    } finally {
        trace.stop()
    }
}

// Использование
val feed = measureTrace("feed_load") { trace ->
    val items = repository.loadFeed()
    trace.putMetric("items_count", items.size.toLong())
    items
}
```

**Что мониторить в первую очередь:**
- **Cold start time**: цель <1 сек (см. [[android-app-startup-performance]])
- **Screen rendering**: >10% slow frames -- проблема
- **API latency**: P50, P95, P99 по эндпоинтам
- **Image loading time**: особенно на медленных сетях

---

## Privacy & Compliance

### GDPR / CCPA consent management

С 2025 года enforcement GDPR значительно ужесточился. Meta получила штраф $1.3B частично за нарушения в мобильном трекинге. Для Android-приложений это означает:

**1. Default consent state -- консервативный:**

```xml
<!-- AndroidManifest.xml -->
<!-- Firebase по умолчанию НЕ собирает данные до получения consent -->
<meta-data
    android:name="firebase_analytics_collection_deferred"
    android:value="true" />
```

**2. Runtime consent management:**

```kotlin
class ConsentManager @Inject constructor(
    private val preferences: SharedPreferences
) {

    fun updateConsent(analyticsConsented: Boolean, crashlyticsConsented: Boolean) {
        // Firebase Analytics
        Firebase.analytics.setConsent {
            analyticsStorage(
                if (analyticsConsented) ConsentStatus.GRANTED
                else ConsentStatus.DENIED
            )
            adStorage(ConsentStatus.DENIED) // Явно отключаем ad tracking
        }

        // Crashlytics
        Firebase.crashlytics.setCrashlyticsCollectionEnabled(crashlyticsConsented)

        // Сохраняем выбор пользователя
        preferences.edit {
            putBoolean("analytics_consent", analyticsConsented)
            putBoolean("crashlytics_consent", crashlyticsConsented)
        }
    }

    fun revokeAllConsent() {
        updateConsent(
            analyticsConsented = false,
            crashlyticsConsented = false
        )
    }
}
```

**3. User data deletion:**

```kotlin
// Firebase предоставляет API для удаления данных пользователя
// По запросу пользователя (GDPR "Right to be forgotten")
Firebase.analytics.resetAnalyticsData()

// Для Amplitude
amplitude.reset() // Сбрасывает userId и deviceId
```

**Checklist для compliance:**
- [ ] Показать consent dialog до инициализации SDK
- [ ] Хранить выбор пользователя и позволять менять его
- [ ] Defer collection до получения consent
- [ ] Не отправлять PII (email, phone) в event parameters
- [ ] Реализовать data deletion по запросу
- [ ] Документировать все собираемые данные в Privacy Policy

---

## Key Metrics Dashboard

Минимальный набор метрик, который должен быть на dashboard любого Android-приложения:

### Стабильность

| Метрика | Цель | Источник |
|---------|------|----------|
| **Crash-free users** | >99.5% | Crashlytics / Play Console |
| **Crash-free sessions** | >99.95% | Crashlytics |
| **ANR rate** | <0.5% | Play Console / Crashlytics |
| **Non-fatal exception rate** | Тренд вниз | Crashlytics |

### Engagement

| Метрика | Что показывает | Источник |
|---------|---------------|----------|
| **DAU / MAU** | Stickiness (цель >20%) | Firebase / Amplitude |
| **Retention D1** | Первый день после установки (цель >40%) | Amplitude / Mixpanel |
| **Retention D7** | Неделя (цель >20%) | Amplitude / Mixpanel |
| **Retention D30** | Месяц (цель >10%) | Amplitude / Mixpanel |
| **Session length** | Среднее время в приложении | Firebase / Amplitude |
| **Sessions per user** | Частота использования | Firebase / Amplitude |

### Производительность

| Метрика | Цель | Источник |
|---------|------|----------|
| **Cold start time** | <1 сек (P90) | Firebase Performance |
| **Slow rendering frames** | <5% от всех frames | Firebase Performance |
| **API P95 latency** | <500ms | Firebase Performance / Sentry |

---

## Подводные камни

### 1. Event spam
Логировать каждый tap -- путь к бесполезным данным и счетам за Mixpanel. Определите **event taxonomy** до начала разработки. Каждое событие должно отвечать на конкретный продуктовый вопрос.

### 2. PII leaks в analytics
```kotlin
// ❌ НИКОГДА не делайте так
tracker.trackEvent("login", mapOf(
    "email" to user.email,         // PII!
    "phone" to user.phone,         // PII!
    "credit_card" to user.cardNum  // PII + PCI DSS violation!
))

// ✅ Используйте анонимные идентификаторы
tracker.trackEvent("login", mapOf(
    "user_id" to user.hashedId,
    "auth_method" to "google",
    "account_type" to "premium"
))
```

### 3. Obfuscation mapping не загружен
Самая частая проблема: release build крэшится, а в Crashlytics видны только обфусцированные имена. Решение -- автоматический upload mapping через CI/CD и проверка наличия mapping в pipeline.

### 4. Debug vs Release данные
```kotlin
// Не смешивайте debug и production данные
class DebugAnalyticsTracker : AnalyticsTracker {
    override fun trackEvent(name: String, params: Map<String, Any>) {
        Log.d("Analytics", "Event: $name, params: $params")
        // НЕ отправляем в production систему
    }

    override fun setUserProperty(key: String, value: String) {
        Log.d("Analytics", "Property: $key = $value")
    }

    override fun setUserId(id: String?) {
        Log.d("Analytics", "UserId: $id")
    }

    override fun trackScreen(screenName: String) {
        Log.d("Analytics", "Screen: $screenName")
    }
}
```

### 5. Игнорирование ANR
ANR хуже крэша -- пользователь видит системный диалог и осознанно закрывает приложение. Google Play считает ANR rate >0.47% "плохим порогом" (bad behavior threshold), что влияет на visibility приложения в поиске.

### 6. Отсутствие event taxonomy документации
Без единого документа с описанием всех событий, их параметров и бизнес-вопросов, на которые они отвечают, аналитика превращается в хаос. Ведите event catalog в Confluence/Notion и review'те каждое новое событие.

---

## Проверь себя

**Q1: Почему нельзя вызывать `Firebase.analytics.logEvent()` напрямую из ViewModel?**

> **A:** Прямой вызов создаёт жёсткую связь с конкретным провайдером. При добавлении второго провайдера (Amplitude) или замене Firebase придётся менять код во всех ViewModel. Абстракция через `AnalyticsTracker` interface позволяет добавлять/убирать провайдеров в одном месте (DI module) без изменения бизнес-логики.

**Q2: Чем crash-free users отличается от crash-free sessions?**

> **A:** Crash-free users -- процент пользователей, у которых не было ни одного крэша за период. Crash-free sessions -- процент сессий без крэшей. Один пользователь может иметь 10 сессий, из которых 1 с крэшем -- crash-free sessions = 90%, но crash-free users показал бы этого пользователя как "с крэшами". Sessions -- более строгая метрика.

**Q3: Когда Firebase Analytics недостаточно и нужно переходить на Amplitude/Mixpanel?**

> **A:** Когда нужны: (1) продвинутые funnels с breakdown по свойствам, (2) retention analysis по когортам, (3) real-time данные (Firebase имеет задержку до 24 часов), (4) predictive analytics (ML-модели для прогноза churn), (5) гибкие dashboards для продуктовой команды. Firebase отлично подходит для MVP и маленьких команд, но ограничен для product-led growth.

**Q4: Что случится, если не загрузить R8 mapping file после release build?**

> **A:** Все стектрейсы в Crashlytics будут обфусцированными -- вместо `UserRepository.fetchUser()` вы увидите `a.b.c()`. Это делает диагностику крэшей практически невозможной. Mapping file нужно загружать автоматически через CI pipeline при каждом release build.

---

## Ключевые карточки

**Crashlytics custom key** :: `Firebase.crashlytics.setCustomKey("key", value)` добавляет контекст к крэш-репортам -- максимум 64 пары ключ-значение, помогает понять состояние приложения в момент краша.

**Non-fatal exception** :: `Firebase.crashlytics.recordException(e)` логирует перехваченное исключение без краша приложения -- позволяет трекать проблемы, которые обрабатываются gracefully, но требуют внимания.

**Analytics abstraction** :: Composite pattern: `AnalyticsTracker` interface + `FirebaseTracker`, `AmplitudeTracker` реализации + `CompositeTracker` для отправки во все провайдеры -- смена провайдера без изменения бизнес-кода.

**GDPR consent** :: До инициализации analytics SDK показать consent dialog; использовать `firebase_analytics_collection_deferred = true` в manifest; хранить выбор; предоставить data deletion API.

**Crash-free rate targets** :: Crash-free users >99.5%, crash-free sessions >99.95%, ANR rate <0.47% (Google Play bad behavior threshold). Ниже этих порогов -- Google Play снижает visibility приложения.

**Event naming** :: snake_case, максимум 40 символов, namespace по фиче (`checkout_payment_selected`), глагол в прошедшем времени (`item_added`), не более 500 типов событий (Firebase), не более 25 параметров на событие.

---

## Куда дальше

- [[android-app-startup-performance]] -- оптимизация cold start, который трекается через Performance Monitoring
- [[android-permissions-security]] -- runtime permissions, связь с consent management
- [[android-firebase-platform]] -- обзор Firebase ecosystem: Auth, Firestore, Remote Config
- [[android-testing]] -- тестирование analytics layer: проверка корректности отправки событий
- [[android-ecosystem-2026]] -- тренды Android-разработки и место analytics в современном стеке

---

## Источники

1. [Firebase Crashlytics -- Get Started (Android)](https://firebase.google.com/docs/crashlytics/android/get-started) -- официальная документация по настройке Crashlytics
2. [Firebase Performance Monitoring -- Custom Code Traces](https://firebase.google.com/docs/perf-mon/custom-code-traces) -- создание custom traces
3. [Sentry Android SDK Documentation](https://docs.sentry.io/platforms/android/) -- полная документация Sentry для Android
4. [Sentry Android SDK Features](https://docs.sentry.io/platforms/android/features/) -- обзор возможностей Sentry SDK
5. [Bugsnag Android Platform](https://docs.bugsnag.com/platforms/android/) -- документация Bugsnag для Android
6. [Bugsnag Stability Score](https://www.bugsnag.com/product/stability-score/) -- описание метрики Stability Score
7. [Amplitude Android-Kotlin SDK](https://amplitude.com/docs/sdks/analytics/android/android-kotlin-sdk) -- официальный SDK Amplitude для Android
8. [Mixpanel Android SDK](https://docs.mixpanel.com/docs/tracking-methods/sdks/android) -- документация Mixpanel SDK
9. [Mixpanel Pricing](https://docs.mixpanel.com/docs/pricing) -- структура ценообразования Mixpanel
10. [Best Mobile Analytics Tools in 2025](https://www.statsig.com/comparison/best-mobile-analytics-tools) -- обзор и сравнение инструментов
11. [Android Crash Reporting Best Practices](https://instabug.com/blog/android-crash-reporting-best-practices/) -- best practices для crash reporting
12. [GDPR Compliance for Apps: 2025 Guide](https://gdprlocal.com/gdpr-compliance-for-apps/) -- гайд по GDPR compliance для мобильных приложений
13. [Mobile App Consent Management SDK](https://secureprivacy.ai/blog/mobile-app-sdk-consent-management) -- управление consent в мобильных приложениях
14. [Google Play -- Crashes and ANR](https://developer.android.com/games/optimize/vitals/crash) -- Android Vitals: crash и ANR метрики

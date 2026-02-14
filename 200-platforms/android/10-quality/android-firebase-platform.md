---
title: "Firebase Platform: полный гайд для Android"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
area: android
tags:
  - topic/android
  - topic/firebase
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-notifications]]"
  - "[[android-analytics-crash-reporting]]"
  - "[[android-feature-flags-remote-config]]"
  - "[[android-ecosystem-2026]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-gradle-fundamentals]]"
reading_time: 25
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Firebase Platform: полный гайд для Android

> Firebase — это Backend-as-a-Service (BaaS) платформа от Google, объединяющая 20+ сервисов: от Authentication и Cloud Firestore до Crashlytics, Remote Config и App Check. Для Android-разработчика Firebase закрывает серверную часть без написания backend-кода, позволяя сосредоточиться на продукте. С 2024-2025 платформа добавила Firebase Studio (AI-powered IDE), Data Connect (PostgreSQL через GraphQL), Firebase MCP Server (GA) и Gemini-интеграцию в Crashlytics. KTX-модули упразднены с BoM v34.0.0 — Kotlin API переехали в основные модули.

---

## Зачем это нужно

| Сценарий | Без Firebase | С Firebase |
|----------|-------------|------------|
| Auth для MVP | Свой backend, OAuth flow, хранение токенов | `FirebaseAuth.signInWithCredential()` — 10 строк |
| Realtime-чат | WebSocket-сервер, масштабирование, reconnect | Firestore `addSnapshotListener` — автоматический sync |
| Push-уведомления | Свой push-сервер, FCM API, retry-логика | FCM SDK + topic messaging — zero backend |
| Crash-мониторинг | Sentry/Bugsnag setup, символизация | Crashlytics — auto-symbolication, Gemini insights |
| A/B тесты | Feature flag сервер, статистика | Remote Config + A/B Testing — встроено |
| Beta-раздача | APK по email, TestFlight-аналог | App Distribution — тестеры, группы, feedback |

### Indie-разработчик vs Enterprise

**Indie / стартап:** Firebase идеален на старте — бесплатный Spark plan покрывает до 50K MAU в Auth, 50K reads/day в Firestore, Crashlytics без лимитов. Один `google-services.json` — и backend готов.

**Enterprise:** Firebase масштабируется, но появляются нюансы — vendor lock-in, ценовые скачки при росте трафика, ограничения security rules для сложной бизнес-логики. Крупные проекты часто используют Firebase для Auth + Analytics + Crashlytics, а бизнес-логику держат на своём backend.

---

## Firebase Services Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      FIREBASE PLATFORM                          │
├───────────────────┬──────────────────┬──────────────────────────┤
│       BUILD       │  RELEASE & MON.  │        ENGAGE            │
├───────────────────┼──────────────────┼──────────────────────────┤
│ Authentication    │ Crashlytics      │ Analytics                │
│ Cloud Firestore   │ Performance Mon. │ Remote Config            │
│ Realtime Database │ Test Lab         │ A/B Testing              │
│ Cloud Functions   │ App Distribution │ Cloud Messaging (FCM)    │
│ Cloud Storage     │ App Check        │ In-App Messaging         │
│ Hosting           │                  │ Dynamic Links (deprecated│
│ Data Connect (NEW)│                  │   → App Links)           │
│ App Hosting (NEW) │                  │                          │
│ ML / Vertex AI    │                  │                          │
│ Genkit            │                  │                          │
└───────────────────┴──────────────────┴──────────────────────────┘

Новое в 2025:
• Firebase Studio — AI-powered IDE для полного lifecycle
• Data Connect — PostgreSQL (Cloud SQL) + GraphQL schema
• App Hosting — GA, для web-приложений
• MCP Server — GA, интеграция с AI-агентами
• Genkit — Go (Beta), Python (Alpha) для AI workflows
• Phone Number Verification (PNV) — one-tap sign-in
```

---

## Core Services

### Authentication

Firebase Auth поддерживает множество провайдеров и интегрируется с Android Credential Manager (API 34+).

**Поддерживаемые провайдеры:**
- Email/Password — классический flow
- Google Sign-In — через Credential Manager (замена deprecated GoogleSignInClient)
- Apple Sign-In — для кросс-платформенных приложений
- Phone (SMS OTP) — с новой Phone Number Verification (PNV) для one-tap
- Anonymous — для гостевого доступа с возможностью link к постоянному аккаунту
- GitHub, Twitter/X, Microsoft, Yahoo — OAuth провайдеры
- Custom token — интеграция с существующим backend

**Лимиты Spark plan:** 50,000 MAU для Email/Social, безлимитно для Anonymous и Custom.

```kotlin
// Firebase Auth + Credential Manager (2025+)
class AuthRepository @Inject constructor(
    private val auth: FirebaseAuth,
    private val credentialManager: CredentialManager
) {
    suspend fun signInWithGoogle(context: Context): FirebaseUser? {
        val googleIdOption = GetGoogleIdOption.Builder()
            .setFilterByAuthorizedAccounts(false)
            .setServerClientId(WEB_CLIENT_ID)
            .build()

        val request = GetCredentialRequest.Builder()
            .addCredentialOption(googleIdOption)
            .build()

        val result = credentialManager.getCredential(context, request)
        val credential = result.credential as? CustomCredential ?: return null

        val googleIdToken = GoogleIdTokenCredential
            .createFrom(credential.data).idToken

        val firebaseCredential = GoogleAuthProvider
            .getCredential(googleIdToken, null)

        return auth.signInWithCredential(firebaseCredential)
            .await().user
    }
}
```

### Cloud Firestore

Document-oriented NoSQL база данных с real-time sync и offline persistence.

| Характеристика | Описание |
|---------------|----------|
| Модель данных | Collections → Documents → Fields (nested maps, arrays) |
| Real-time | `addSnapshotListener` — push-обновления через WebSocket |
| Offline | Встроенный кэш (до 100 MB по умолчанию, настраивается) |
| Запросы | Composable queries, composite indexes, `where`, `orderBy`, `limit` |
| Масштабирование | Автоматическое, до миллионов concurrent connections |
| Security Rules | Декларативные правила доступа на уровне document/collection |
| Транзакции | Optimistic concurrency — до 500 writes в одной транзакции |

**Spark plan лимиты:** 50K reads/day, 20K writes/day, 20K deletes/day, 1 GiB storage.

```kotlin
// Firestore с offline persistence и snapshot listener
@Singleton
class TaskRepository @Inject constructor(
    private val firestore: FirebaseFirestore
) {
    private val tasksCollection = firestore.collection("tasks")

    fun observeTasks(userId: String): Flow<List<Task>> = callbackFlow {
        val listener = tasksCollection
            .whereEqualTo("userId", userId)
            .orderBy("createdAt", Query.Direction.DESCENDING)
            .addSnapshotListener { snapshot, error ->
                if (error != null) {
                    close(error)
                    return@addSnapshotListener
                }
                val tasks = snapshot?.documents
                    ?.mapNotNull { it.toObject<Task>() }
                    ?: emptyList()
                trySend(tasks)
            }
        awaitClose { listener.remove() }
    }

    suspend fun addTask(task: Task): String {
        val docRef = tasksCollection.add(task).await()
        return docRef.id
    }
}
```

### Realtime Database vs Cloud Firestore

| Критерий | Realtime Database | Cloud Firestore |
|----------|-------------------|-----------------|
| Модель данных | Один большой JSON-дерево | Collections / Documents |
| Запросы | Ограниченные (один индекс) | Составные запросы, `where`, `in` |
| Offline | Android / iOS | Android / iOS / Web |
| Масштабирование | До ~200K concurrent, manual sharding | Автоматическое |
| Ценообразование | По объёму данных + bandwidth | По операциям (reads/writes/deletes) |
| Лучше для | Простой real-time sync (presence, typing indicators) | Сложные queries, структурированные данные |
| Security rules | JSON-based | CEL-подобный язык, гибче |
| Регионы | US-central1 или EU | Multi-region |

**Правило выбора:** используйте Firestore как default. Realtime Database оправдана для presence-систем (кто онлайн), typing indicators и сценариев, где нужна оплата по bandwidth, а не по операциям.

### Cloud Functions

Serverless-функции на Node.js, Python или Go, исполняемые в ответ на события Firebase.

**Типы триггеров:**
- **Firestore triggers** — `onDocumentCreated`, `onDocumentUpdated`, `onDocumentDeleted`
- **Auth triggers** — `onUserCreated`, `onUserDeleted`
- **Storage triggers** — `onObjectFinalized` (upload завершён)
- **FCM triggers** — обработка upstream-сообщений
- **HTTP triggers** — REST endpoints (callable functions)
- **Scheduled triggers** — cron-подобное расписание
- **Remote Config triggers** — при обновлении конфигурации

**Spark plan:** 2M invocations/month, 400K GB-seconds compute, 200K CPU-seconds.

### Cloud Messaging (FCM)

Push-уведомления для Android, iOS и Web. Подробности о notification pipeline — в [[android-notifications]].

**Ключевые концепции:**
- **Device token** — уникальный идентификатор устройства, обновляется периодически
- **Topic messaging** — подписка на каналы (`/topics/news`), до 2000 подписок на устройство
- **Condition messaging** — логические комбинации топиков (`'news' in topics && 'weather' in topics`)
- **Data messages** — обрабатываются в `onMessageReceived`, не показывают notification автоматически
- **Notification messages** — автоматически показываются системой, если приложение в background

```kotlin
class AppFirebaseMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        // Отправить token на свой backend или сохранить в Firestore
        CoroutineScope(Dispatchers.IO).launch {
            tokenRepository.updateToken(token)
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        val data = message.data
        when (data["type"]) {
            "chat" -> handleChatMessage(data)
            "order" -> handleOrderUpdate(data)
            else -> showDefaultNotification(message)
        }
    }
}
```

### Cloud Storage

Хранение файлов (изображения, видео, документы) с security rules и resume upload.

**Важное изменение (февраль 2026):** бакеты `*.appspot.com` на Spark plan теряют доступ через API — необходимо перейти на Blaze plan или мигрировать.

```kotlin
suspend fun uploadAvatar(userId: String, uri: Uri): String {
    val ref = storage.reference.child("avatars/$userId.jpg")
    ref.putFile(uri).await()
    return ref.downloadUrl.await().toString()
}
```

---

## Build & Deploy

### App Distribution

Раздача beta-сборок тестерам без Google Play.

- Поддержка APK и AAB
- Группы тестеров с email-приглашениями
- In-app feedback SDK
- Интеграция с CI/CD (Gradle plugin, CLI, Fastlane)
- Автообновление через Firebase App Tester

### Test Lab

Облачное тестирование на реальных и виртуальных устройствах.

| Возможность | Описание |
|-------------|----------|
| Robo Test | AI-driven автоматический обход UI |
| Instrumentation | Стандартные Espresso/UI Automator тесты |
| Game Loop | Тестирование игр с custom loops |
| Устройства | 100+ моделей, включая Samsung, Pixel, Xiaomi |
| Spark plan | 15 тестов/день на виртуальных, 5 на физических |

### Remote Config

Изменение поведения и внешнего вида приложения без деплоя. Подробнее — в [[android-feature-flags-remote-config]].

- Параметры с default values
- Условия (по стране, OS version, user property, % rollout)
- Интеграция с A/B Testing
- Real-time config updates (`addOnConfigUpdateListener`)
- Personalization с ML — автоматический подбор значений

### App Check

Защита backend-ресурсов Firebase от несанкционированного доступа. Использует Play Integrity API на Android.

```
Как работает App Check:
┌─────────┐    attestation    ┌──────────────┐     token     ┌──────────┐
│ Android │ ───────────────→ │ Play Integrity│ ───────────→ │ App Check│
│   App   │                  │   Provider    │              │  Server  │
└─────────┘                  └──────────────┘              └──────────┘
     │                                                          │
     │              App Check token (short-lived)               │
     │ ◄──────────────────────────────────────────────────────  │
     │                                                          │
     │              token в каждом запросе                       │
     ▼                                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  Firebase Backend (Firestore, Storage, Functions, etc.)         │
│  Проверяет App Check token → разрешает или отклоняет запрос     │
└─────────────────────────────────────────────────────────────────┘
```

**Play Integrity API:**
- Проверяет: genuine app (не модифицирован), genuine device (сертифицирован Play Protect), licensed user (установлен через Play Store)
- Verdict уровни: `MEETS_BASIC_INTEGRITY`, `MEETS_DEVICE_INTEGRITY`, `MEETS_STRONG_INTEGRITY` (Android 13+, свежие security patches)
- Квота: 10,000 standard requests/day (классические), unlimited для warmup

```kotlin
// Инициализация App Check с Play Integrity
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        FirebaseApp.initializeApp(this)

        val appCheckFactory = PlayIntegrityAppCheckProviderFactory
            .getInstance()

        FirebaseAppCheck.getInstance()
            .installAppCheckProviderFactory(appCheckFactory)
    }
}
```

---

## Monitoring

### Crashlytics

Мониторинг крашей и ANR в реальном времени. Подробнее — в [[android-analytics-crash-reporting]].

**Ключевые возможности:**
- Автоматическая группировка крашей по root cause
- Gemini-powered crash insights (2025) — AI объясняет причину и предлагает fix
- NDK crash reporting для native-кода
- Non-fatal exception logging
- Custom keys и breadcrumb logs для контекста
- Интеграция с Android Studio App Quality Insights
- Velocity alerts — уведомление при росте crash rate
- BigQuery export для custom analytics

**Без лимитов** на обоих планах — Spark и Blaze.

### Performance Monitoring

Автоматические и custom traces для отслеживания производительности.

- **Automatic traces:** app start, screen rendering (slow/frozen frames), HTTP/S network requests
- **Custom traces:** произвольные участки кода с метриками
- **Network monitoring:** latency, success rate, payload size по endpoint
- **Dashboard:** breakdown по device, OS version, country

```kotlin
// Custom trace для отслеживания загрузки данных
suspend fun loadDashboard(): Dashboard {
    val trace = Firebase.performance.newTrace("load_dashboard")
    trace.start()
    try {
        val data = repository.fetchDashboard()
        trace.putMetric("items_count", data.items.size.toLong())
        trace.putAttribute("cache_hit", data.fromCache.toString())
        return data
    } finally {
        trace.stop()
    }
}
```

### Analytics

Основа для всех engagement-сервисов. Подробнее — в [[android-analytics-crash-reporting]].

- Автоматические события: `first_open`, `session_start`, `screen_view`, `app_update`
- Custom events (до 500 типов, 25 параметров каждое)
- User properties (до 25)
- Audiences — сегменты для Remote Config и FCM targeting
- BigQuery export (Blaze plan) — raw event data
- Google Analytics 4 интеграция

---

## Сравнение альтернатив

| Feature | Firebase | Supabase | Appwrite | AWS Amplify |
|---------|----------|----------|----------|-------------|
| **Database** | Firestore (NoSQL) | PostgreSQL (SQL) | MariaDB (document API) | DynamoDB / Aurora |
| **Real-time** | Встроенный | Postgres logical replication | WebSocket channels | AppSync (GraphQL) |
| **Auth** | 10+ провайдеров | 20+ провайдеров | 10+ провайдеров | Cognito |
| **Functions** | Cloud Functions (Node/Py/Go) | Edge Functions (Deno) | Functions (15+ runtimes) | Lambda |
| **Storage** | Cloud Storage | S3-compatible | S3-compatible | S3 |
| **Push** | FCM (встроен) | Нет (интеграция) | Push API | SNS/Pinpoint |
| **Crash monitoring** | Crashlytics | Нет | Нет | Нет (CloudWatch) |
| **Open source** | Частично (SDK) | Да (полностью) | Да (полностью) | Да (SDK) |
| **Self-hosting** | Нет | Да | Да | Нет |
| **Vendor lock-in** | Высокий | Низкий | Низкий | Высокий (AWS) |
| **Android SDK** | Отличный (первоклассный) | Community SDK | Community SDK | Официальный |
| **Ценообразование** | По операциям | Предсказуемое ($25/mo Pro) | Предсказуемое / free self-host | По потреблению |
| **Стоимость ~10K MAU** | $50-150/mo | $25-75/mo | $15-30/mo (self-host) | $80-200/mo |
| **Лучше для** | Mobile-first, быстрый старт | SQL-driven, open source | Полный контроль, self-host | Enterprise, AWS экосистема |

**Итог:** Firebase остаётся лучшим выбором для Android — нативный SDK, глубокая интеграция с Google Play, Crashlytics и FCM не имеют аналогов. Supabase — лучшая open-source альтернатива для SQL-проектов. Appwrite — для тех, кто хочет self-hosting. Amplify — только если уже живёте в AWS.

---

## Ценообразование: подводные камни

### Бесплатный уровень (Spark Plan)

| Сервис | Бесплатно в день/месяц |
|--------|----------------------|
| Auth | 50K MAU (Email/Social), безлимит Anonymous |
| Firestore reads | 50,000 / day |
| Firestore writes | 20,000 / day |
| Firestore deletes | 20,000 / day |
| Firestore storage | 1 GiB |
| Cloud Storage | 5 GB storage, 1 GB download/day |
| Cloud Functions | 2M invocations/month |
| Hosting | 10 GB storage, 360 MB/day transfer |
| Test Lab | 15 virtual / 5 physical tests per day |
| Crashlytics | Без лимитов |
| Analytics | Без лимитов |
| Remote Config | Без лимитов |
| FCM | Без лимитов |

### Blaze Plan — ключевые расценки

| Ресурс | Цена |
|--------|------|
| Firestore reads | $0.06 / 100K (после бесплатной квоты) |
| Firestore writes | $0.18 / 100K |
| Firestore deletes | $0.02 / 100K |
| Firestore storage | $0.18 / GiB / month |
| Cloud Storage bandwidth | $0.12 / GB |
| Cloud Functions invocations | $0.40 / million |
| Phone Auth (SMS) | $0.01-0.06 / verification |
| Outgoing bandwidth (Aug 2025+) | $0.20/GiB uncached, $0.15/GiB cached |

### Ценовые ловушки

```
⚠ GOTCHA #1: Firestore reads explosion
─────────────────────────────────────
addSnapshotListener на коллекцию с 1000 документов:
→ Первый вызов = 1000 reads
→ Один документ изменился = 1 read (дельта)
→ Listener отключился на 30+ мин → reconnect = 1000 reads заново!

Решение: пагинация, узкие запросы, composite queries

⚠ GOTCHA #2: Cloud Storage bandwidth
─────────────────────────────────────
Приложение с 100K пользователей, каждый загружает аватар (200 KB):
→ 100K × 200 KB = 20 GB bandwidth → ~$2.40/day → $72/month
→ Добавьте image feed — легко 10x

Решение: CDN (Firebase Hosting), resize images, cache aggressively

⚠ GOTCHA #3: Cloud Functions cold starts
─────────────────────────────────────
Бесплатных invocations 2M, но:
→ Каждый Firestore trigger — это invocation
→ 10 triggers на 1 write → 10 invocations
→ 200K writes/month × 10 = 2M → бесплатная квота исчерпана

Решение: batch operations, минимизация triggers, 2nd gen functions

⚠ GOTCHA #4: Phone Auth SMS costs
─────────────────────────────────────
SMS OTP стоит $0.01-0.06 за верификацию:
→ 100K пользователей × SMS sign-in = $1,000-6,000/month
→ Злоумышленники могут спамить SMS endpoint

Решение: App Check для защиты, reCAPTCHA, PNV (one-tap, без SMS)
```

---

## Integration Patterns: Hilt + Firebase

```kotlin
// FirebaseModule.kt — Hilt DI setup
@Module
@InstallIn(SingletonComponent::class)
object FirebaseModule {

    @Provides
    @Singleton
    fun provideFirebaseAuth(): FirebaseAuth =
        FirebaseAuth.getInstance()

    @Provides
    @Singleton
    fun provideFirestore(): FirebaseFirestore =
        FirebaseFirestore.getInstance().apply {
            firestoreSettings = firestoreSettings {
                isPersistenceEnabled = true
                cacheSizeBytes = FirebaseFirestoreSettings
                    .CACHE_SIZE_UNLIMITED
            }
        }

    @Provides
    @Singleton
    fun provideStorage(): FirebaseStorage =
        FirebaseStorage.getInstance()

    @Provides
    @Singleton
    fun provideRemoteConfig(): FirebaseRemoteConfig =
        FirebaseRemoteConfig.getInstance().apply {
            setConfigSettingsAsync(remoteConfigSettings {
                minimumFetchIntervalInSeconds = if (BuildConfig.DEBUG) 0 else 3600
            })
            setDefaultsAsync(R.xml.remote_config_defaults)
        }

    @Provides
    @Singleton
    fun provideAnalytics(
        @ApplicationContext context: Context
    ): FirebaseAnalytics =
        FirebaseAnalytics.getInstance(context)
}
```

```kotlin
// build.gradle.kts (app level) — Firebase BoM setup (2025+)
// Важно: KTX-модули больше не нужны с BoM v34.0.0+
dependencies {
    // Firebase BoM — управляет версиями всех Firebase SDK
    implementation(platform("com.google.firebase:firebase-bom:33.9.0"))

    // Core — без указания версий (управляет BoM)
    implementation("com.google.firebase:firebase-auth")
    implementation("com.google.firebase:firebase-firestore")
    implementation("com.google.firebase:firebase-storage")
    implementation("com.google.firebase:firebase-messaging")
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-crashlytics")
    implementation("com.google.firebase:firebase-perf")
    implementation("com.google.firebase:firebase-config")
    implementation("com.google.firebase:firebase-appcheck-playintegrity")

    // Credential Manager для Google Sign-In
    implementation("androidx.credentials:credentials:1.5.0")
    implementation("com.google.android.libraries.identity.googleid:googleid:1.1.1")
}
```

Подробнее о Hilt — в [[android-hilt-deep-dive]].

---

## Подводные камни

### 1. Firestore security rules — "открытый доступ" в продакшене

По умолчанию test-правила разрешают всё. Забыть заменить их — самая частая ошибка.

```
// ПЛОХО — всё открыто
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}

// ХОРОШО — проверка auth и ownership
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null
                         && request.auth.uid == userId;
    }
    match /posts/{postId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null
                    && request.resource.data.authorId == request.auth.uid;
      allow update, delete: if request.auth != null
                            && resource.data.authorId == request.auth.uid;
    }
  }
}
```

### 2. Unsubscribe от snapshot listeners

Каждый `addSnapshotListener` — это активное WebSocket-соединение. Если не отписываться в `onStop` / `onCleared`, получаете утечку ресурсов и лишние reads.

### 3. Firestore document size limit — 1 MB

Нельзя хранить массивы с тысячами элементов внутри документа. Решение — subcollections.

### 4. FCM token rotation

Token обновляется без предупреждения. Если хранить его только локально и не обновлять на сервере — push перестанут доходить. Всегда обрабатывайте `onNewToken`.

### 5. Offline persistence + security rules race condition

При offline-записи данные попадают в локальный кэш мгновенно, но security rules проверяются только при sync. Пользователь может увидеть "успех", а затем данные откатятся.

### 6. Analytics debug mode забыт в release

`adb shell setprop debug.firebase.analytics.app PACKAGE_NAME` включает real-time analytics. Забыть выключить — не страшно (работает только по ADB), но `setAnalyticsCollectionEnabled(false)` в debug-сборках снижает noise.

### 7. Crashlytics debug symbols для R8/ProGuard

Без mapping file в консоли — obfuscated stack traces. Убедитесь, что Crashlytics Gradle plugin загружает `mapping.txt` автоматически.

---

## Проверь себя

<details>
<summary>Чем отличается Firestore snapshot listener от обычного get()?</summary>

`get()` — одноразовый запрос, возвращает текущее состояние и закрывает соединение. `addSnapshotListener` — устанавливает постоянное WebSocket-соединение и пушит обновления в реальном времени. Первый вызов listener считается как reads по количеству документов, последующие обновления — по дельте (только изменённые документы). При disconnection дольше 30 минут — listener заново считывает все документы.
</details>

<details>
<summary>Почему App Check не гарантирует 100% защиту от abuse?</summary>

App Check проверяет, что запрос пришёл от подлинного приложения на непротиворечивом устройстве, но: (1) attestation token может быть перехвачен через MITM на rooted-устройстве, (2) Play Integrity возвращает вероятностный verdict, (3) debug provider в debug-сборках обходит проверку. App Check — это defence-in-depth layer, не замена серверной авторизации. Всегда проверяйте business-level permissions в security rules и на backend.
</details>

<details>
<summary>Когда Realtime Database лучше Firestore?</summary>

Realtime Database предпочтительнее в трёх сценариях: (1) presence systems (кто онлайн) — встроенный `onDisconnect()` handler, (2) ценообразование по bandwidth, а не по операциям — если у вас много мелких частых reads, RTDB дешевле, (3) ultra-low latency для простых данных — single JSON tree без overhead коллекций/документов. Для всего остального — Firestore.
</details>

<details>
<summary>Как предотвратить Firestore reads explosion при использовании listeners?</summary>

Четыре стратегии: (1) Narrow queries — вместо слушания всей коллекции, фильтруйте по конкретному userId/status, (2) Пагинация с `limit()` — слушайте только видимые данные, (3) Avoid listener churn — не пересоздавайте listener при каждом recomposition/configuration change, используйте ViewModel, (4) Composite indexes — один запрос вместо нескольких. Мониторьте reads в Firebase Console → Usage.
</details>

---

## Ключевые карточки

> **Q:** Какой Firebase SDK manager рекомендуется для управления версиями?
> **A:** Firebase BoM (Bill of Materials) — platform dependency, которая синхронизирует версии всех Firebase SDK. С v34.0.0 KTX-модули упразднены, Kotlin API включены в основные модули.

> **Q:** Что такое App Check token и его lifetime?
> **A:** Короткоживущий JWT-токен (обычно 1 час), выданный Firebase App Check после успешной attestation через Play Integrity. Автоматически обновляется SDK, прикрепляется к каждому запросу в Firebase backend.

> **Q:** Как Firebase Auth взаимодействует с Credential Manager?
> **A:** С 2024+ Google Sign-In мигрировал с deprecated `GoogleSignInClient` на Credential Manager API. Firebase Auth получает `GoogleIdTokenCredential` от Credential Manager и обменивает его на Firebase credential через `GoogleAuthProvider.getCredential()`.

> **Q:** В чём разница между notification message и data message в FCM?
> **A:** Notification message — JSON с `"notification"` ключом, автоматически показывается системой в background, попадает в `onMessageReceived` только в foreground. Data message — JSON с `"data"` ключом, всегда попадает в `onMessageReceived`, разработчик сам решает, показывать ли notification.

> **Q:** Какие Firebase сервисы бесплатны без лимитов?
> **A:** Crashlytics, Analytics, Remote Config, FCM, A/B Testing, In-App Messaging, App Indexing. Эти сервисы не имеют usage-based pricing и доступны на Spark plan без ограничений.

> **Q:** Что произойдёт с Cloud Storage bucket на Spark plan после февраля 2026?
> **A:** Бакеты `*.appspot.com` на Spark plan теряют console access и API access (ошибки 402/403). Необходимо перейти на Blaze plan или мигрировать данные. Google предоставляет $300 кредитов при первом апгрейде.

---

## Куда дальше

| Тема | Ссылка | Зачем |
|------|--------|-------|
| Push-уведомления | [[android-notifications]] | FCM pipeline, каналы, foreground/background handling |
| Аналитика и крашлитика | [[android-analytics-crash-reporting]] | Crashlytics setup, custom events, BigQuery export |
| Feature flags | [[android-feature-flags-remote-config]] | Remote Config patterns, A/B testing, gradual rollouts |
| Dependency Injection | [[android-hilt-deep-dive]] | Firebase module setup, scoping, testing |
| Networking | [[android-networking]] | REST API, OkHttp interceptors для Firebase REST |
| Безопасность | [[android-permissions-security]] | Runtime permissions, App Check, attestation |
| Firebase ML | [[mobile-ai-ml-guide]] | ML Kit, Vertex AI in Firebase, on-device inference |
| Экосистема Android | [[android-ecosystem-2026]] | Полный ландшафт инструментов |

---

## Источники

1. [Firebase Documentation](https://firebase.google.com/docs) — официальная документация
2. [Firebase Pricing](https://firebase.google.com/pricing) — актуальные тарифы и лимиты
3. [What's new in Firebase at I/O 2025](https://firebase.blog/posts/2025/05/whats-new-at-google-io/) — анонсы I/O 2025
4. [What's new in Firebase at Cloud Next 2025](https://firebase.blog/posts/2025/04/cloud-next-announcements/) — Firebase Studio, Data Connect GA
5. [Firebase App Check with Play Integrity](https://firebase.google.com/docs/app-check/android/play-integrity-provider) — настройка App Check
6. [Kotlin Migration from KTX](https://firebase.google.com/docs/android/kotlin-migration) — миграция с KTX на основные модули
7. [Appwrite vs Supabase vs Firebase](https://uibakery.io/blog/appwrite-vs-supabase-vs-firebase) — сравнение BaaS платформ 2026
8. [Cloud Firestore Billing](https://firebase.google.com/docs/firestore/pricing) — детали ценообразования Firestore
9. [Firebase in 2025: 8 New Features](https://medium.com/@hiren6997/firebase-in-2025-8-new-features-that-make-it-hard-to-ignore-5007f7891733) — обзор новых функций
10. [Play Integrity API Updates](https://android-developers.googleblog.com/2025/10/stronger-threat-detection-simpler.html) — улучшения Play Integrity 2025

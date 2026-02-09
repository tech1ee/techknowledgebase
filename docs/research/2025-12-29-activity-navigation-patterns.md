# Research Report: Activity-Based Navigation Patterns

**Date:** 2025-12-29
**Sources Evaluated:** 25+
**Research Depth:** Deep (production patterns focus)

## Executive Summary

Activity-based navigation — фундаментальный подход Android с 2008 года. Ключевые компоненты: Intent (explicit/implicit), Activity Result API (замена deprecated `startActivityForResult`), launch modes (standard, singleTop, singleTask, singleInstance, singleInstancePerTask), intent flags (NEW_TASK, CLEAR_TOP, SINGLE_TOP). Task и Back Stack управляют историей навигации. Android 12+ требует FLAG_IMMUTABLE/FLAG_MUTABLE для PendingIntent. Передача данных: Parcelable (10x быстрее) с `@Parcelize` аннотацией.

---

## Key Findings

### 1. Activity Result API (Modern Approach)

**Замена deprecated `startActivityForResult()` и `onActivityResult()`**

**Ключевые компоненты:**
```kotlin
// 1. Регистрация callback
val getContent = registerForActivityResult(GetContent()) { uri: Uri? ->
    // Handle the returned Uri
}

// 2. Запуск activity
selectButton.setOnClickListener {
    getContent.launch("image/*")
}
```

**Built-in Contracts:**
| Contract | Purpose |
|----------|---------|
| `StartActivityForResult` | Generic for any intent |
| `RequestPermission` | Single permission |
| `RequestMultiplePermissions` | Multiple permissions |
| `GetContent` | Select content |
| `GetMultipleContents` | Select multiple items |
| `TakePicturePreview` | Camera thumbnail |
| `TakePicture` | Full photo to URI |
| `CreateDocument` | Create document |
| `OpenDocument` | Open single document |
| `OpenMultipleDocuments` | Open multiple documents |

**Custom Contract:**
```kotlin
class PickRingtone : ActivityResultContract<Int, Uri?>() {
    override fun createIntent(context: Context, ringtoneType: Int) =
        Intent(RingtoneManager.ACTION_RINGTONE_PICKER).apply {
            putExtra(RingtoneManager.EXTRA_RINGTONE_TYPE, ringtoneType)
        }

    override fun parseResult(resultCode: Int, result: Intent?): Uri? {
        if (resultCode != Activity.RESULT_OK) return null
        return result?.getParcelableExtra(RingtoneManager.EXTRA_RINGTONE_PICKED_URI)
    }
}
```

**Lifecycle Rules:**
- **MUST** register before fragment/activity CREATED
- **CAN** launch only after Lifecycle reaches CREATED
- Callbacks safe even if process destroyed between launch and result

**Testing:**
```kotlin
val testRegistry = object : ActivityResultRegistry() {
    override fun <I, O> onLaunch(
        requestCode: Int,
        contract: ActivityResultContract<I, O>,
        input: I,
        options: ActivityOptionsCompat?
    ) {
        dispatchResult(requestCode, expectedResult)
    }
}

with(launchFragmentInContainer { MyFragment(testRegistry) }) {
    onFragment { fragment ->
        fragment.takePicture()
        assertThat(fragment.thumbnailLiveData.value)
            .isSameInstanceAs(expectedResult)
    }
}
```

### 2. Why startActivityForResult Was Deprecated

**Проблемы старого API:**
1. **Request Code Conflicts** — управление уникальностью requestCode error-prone
2. **Results lost on recreation** — результаты терялись при пересоздании activity/fragment
3. **Hard to trace** — сложно найти caller в больших проектах
4. **Fragment complexity** — особенно сложно при вызове из fragments

**Было:**
```kotlin
// Запуск
startActivityForResult(intent, REQUEST_CODE)

// Callback в одном месте для ВСЕХ requests
override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    when (requestCode) {
        REQUEST_CODE_1 -> { ... }
        REQUEST_CODE_2 -> { ... }
        REQUEST_CODE_3 -> { ... }
        // Много case'ов, сложно поддерживать
    }
}
```

**Стало:**
```kotlin
// Каждый contract — отдельный launcher с отдельным callback
val launcher1 = registerForActivityResult(Contract1()) { result -> /* handle */ }
val launcher2 = registerForActivityResult(Contract2()) { result -> /* handle */ }

// Нет requestCode, type-safe, легко тестировать
```

### 3. Intent Types: Explicit vs Implicit

#### Explicit Intent
```kotlin
// Знаем exact class
val intent = Intent(this, ProfileActivity::class.java).apply {
    putExtra("USER_ID", userId)
}
startActivity(intent)
```
**Use case:** Навигация внутри своего приложения

#### Implicit Intent
```kotlin
// Описываем action, система находит handler
val intent = Intent(Intent.ACTION_VIEW).apply {
    data = Uri.parse("https://example.com")
}
startActivity(intent)
```
**Use case:** Делегирование действия другим приложениям

#### Intent Filter (для получения implicit intents)
```xml
<activity android:name=".ShareActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="text/plain" />
    </intent-filter>
</activity>
```

**Components:**
- **Action** — что делать (VIEW, SEND, EDIT, PICK)
- **Category** — тип компонента (DEFAULT, LAUNCHER, BROWSABLE)
- **Data** — MIME type или URI scheme

### 4. Intent Flags Explained

| Flag | Effect | Use Case |
|------|--------|----------|
| `FLAG_ACTIVITY_NEW_TASK` | Запуск в новом task | Из Service/BroadcastReceiver, notification |
| `FLAG_ACTIVITY_CLEAR_TOP` | Удалить все activities сверху | Возврат к Login после logout |
| `FLAG_ACTIVITY_SINGLE_TOP` | Reuse если на вершине stack | Избежать дубликатов, notifications |
| `FLAG_ACTIVITY_CLEAR_TASK` | Очистить весь task | С NEW_TASK для полного reset |
| `FLAG_ACTIVITY_NO_HISTORY` | Не добавлять в back stack | Splash screen, intermediate screens |

**Комбинации:**
```kotlin
// После logout — clear all и показать Login
val intent = Intent(this, LoginActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
}
startActivity(intent)
finish()

// Notification tap — reuse existing или create
val intent = Intent(this, ChatActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
}
```

### 5. Launch Modes

**В Manifest:**
```xml
<activity
    android:name=".MainActivity"
    android:launchMode="singleTop" />
```

| Mode | Instances | Task | onNewIntent |
|------|-----------|------|-------------|
| **standard** | Multiple | Same as caller | No |
| **singleTop** | Multiple (1 at top) | Same as caller | Yes (if at top) |
| **singleTask** | Single system-wide | Own/affinity task | Yes |
| **singleInstance** | Single system-wide | Exclusive task | Yes |
| **singleInstancePerTask** (API 31+) | Single per task | Root of task | Yes |

**Когда использовать:**
- **standard** — большинство activities (default)
- **singleTop** — notification handlers, search results
- **singleTask** — main entry point (Inbox, Timeline, Home)
- **singleInstance** — video call, authentication (редко!)
- **singleInstancePerTask** — document-based apps

**onNewIntent() handling:**
```kotlin
override fun onNewIntent(intent: Intent) {
    super.onNewIntent(intent)
    // ВАЖНО: setIntent() чтобы getIntent() возвращал новый
    setIntent(intent)
    handleIntent(intent)
}
```

### 6. Task and Back Stack

**Task** — коллекция activities для выполнения задачи
**Back Stack** — LIFO структура: last opened = first removed

```
User flow:
[A] → start B → [A, B] → start C → [A, B, C] → Back → [A, B] → Back → [A]
```

**taskAffinity:**
```xml
<activity
    android:name=".ReportActivity"
    android:taskAffinity="com.example.reports"
    android:allowTaskReparenting="true" />
```
- Определяет preferred task для activity
- `allowTaskReparenting` позволяет перемещаться между tasks

**Clearing Back Stack:**
| Attribute | Effect |
|-----------|--------|
| `alwaysRetainTaskState="true"` | Сохранять stack долго |
| `clearTaskOnLaunch="true"` | Очищать при возврате |
| `finishOnTaskLaunch="true"` | Finish activity при возврате |

### 7. Activity Lifecycle During Navigation

```
Activity A starts Activity B:
─────────────────────────────
A.onPause()        ← First!
    B.onCreate()
    B.onStart()
    B.onResume()   ← B visible
A.onStop()         ← A not visible
─────────────────────────────

User presses Back on B:
─────────────────────────────
B.onPause()
    A.onRestart()
    A.onStart()
    A.onResume()   ← A visible
B.onStop()
B.onDestroy()      ← B destroyed
─────────────────────────────
```

**Key insight:** B.onCreate() НЕ вызовется пока A.onPause() не завершится!

### 8. Passing Data Between Activities

#### Primitives
```kotlin
// Send
intent.putExtra("USER_ID", 123)
intent.putExtra("NAME", "John")

// Receive
val userId = intent.getIntExtra("USER_ID", -1)
val name = intent.getStringExtra("NAME")
```

#### Complex Objects — Parcelable (recommended)

**С @Parcelize (Kotlin):**
```kotlin
// build.gradle.kts
plugins {
    id("kotlin-parcelize")
}

// Data class
@Parcelize
data class User(
    val id: String,
    val name: String,
    val email: String
) : Parcelable

// Usage
intent.putExtra("USER", user)
val user = intent.getParcelableExtra<User>("USER")
```

**Parcelable vs Serializable:**
| Aspect | Parcelable | Serializable |
|--------|------------|--------------|
| **Speed** | ~10x faster | Slower (reflection) |
| **Boilerplate** | Minimal with @Parcelize | None |
| **Android-specific** | Yes | No (Java standard) |
| **Use case** | IPC, Intents, Bundles | File storage, legacy |

**Size limits:** Keep data < few KB in intents!

### 9. Process Death and State Saving

**Проблема:** System может убить process в background

**Решение 1: onSaveInstanceState**
```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putString("KEY", value)
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    savedInstanceState?.getString("KEY")?.let { value = it }
}
```

**Решение 2: SavedStateHandle в ViewModel (recommended)**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    var searchQuery: String
        get() = savedStateHandle["query"] ?: ""
        set(value) { savedStateHandle["query"] = value }

    // StateFlow version
    val queryFlow = savedStateHandle.getStateFlow("query", "")
}
```

**Что сохранять:**
- IDs, scroll position, user input
- НЕ сохранять: isLoading, error messages (transient state)

**Testing process death:**
```bash
adb shell am kill com.example.myapp
```

### 10. Activity Transitions

#### Simple transitions
```kotlin
startActivity(intent)
overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)
```

#### Shared Element Transitions
```kotlin
// Activity A — setup shared element
val options = ActivityOptionsCompat.makeSceneTransitionAnimation(
    this,
    imageView,
    "hero_image"  // transitionName
)
startActivity(intent, options.toBundle())

// Layout A & B
<ImageView
    android:transitionName="hero_image"
    ... />

// Activity B — reverse on finish
supportFinishAfterTransition()
```

#### Multiple shared elements
```kotlin
val options = ActivityOptionsCompat.makeSceneTransitionAnimation(
    this,
    androidx.core.util.Pair(imageView, "hero_image"),
    androidx.core.util.Pair(titleView, "hero_title")
)
```

### 11. PendingIntent (Android 12+ Requirements)

**MUST specify mutability:**
```kotlin
// Для большинства случаев — IMMUTABLE
val pendingIntent = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
)

// Только если intent будет модифицирован (inline replies, bubbles)
val mutablePendingIntent = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
)
```

**Notification example:**
```kotlin
val contentIntent = PendingIntent.getActivity(
    context,
    0,
    Intent(context, MainActivity::class.java),
    PendingIntent.FLAG_IMMUTABLE
)

val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentIntent(contentIntent)
    .build()
```

### 12. App Chooser and Intent Resolution

**Android 11+ изменения:**
```kotlin
// OLD (may fail on Android 11+)
if (intent.resolveActivity(packageManager) != null) {
    startActivity(intent)
}

// NEW — recommended approach
try {
    startActivity(intent)
} catch (e: ActivityNotFoundException) {
    // Show error or fallback
}
```

**Force chooser:**
```kotlin
val sendIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Share this!")
}
val chooser = Intent.createChooser(sendIntent, "Share via")
startActivity(chooser)
```

### 13. Back vs Up Navigation

| Button | Behavior | Use Case |
|--------|----------|----------|
| **Back** | Pop current from stack | System button, returns to previous |
| **Up** | Navigate to logical parent | Toolbar arrow, may recreate parent |

**Implementation:**
```kotlin
// Toolbar Up button
supportActionBar?.setDisplayHomeAsUpEnabled(true)

override fun onOptionsItemSelected(item: MenuItem): Boolean {
    return when (item.itemId) {
        android.R.id.home -> {
            onBackPressedDispatcher.onBackPressed()
            true
        }
        else -> super.onOptionsItemSelected(item)
    }
}
```

**AndroidX Back Handling (Predictive Back):**
```kotlin
val callback = object : OnBackPressedCallback(enabled = true) {
    override fun handleOnBackPressed() {
        if (hasUnsavedChanges) {
            showConfirmDialog()
        } else {
            isEnabled = false
            onBackPressedDispatcher.onBackPressed()
        }
    }
}
onBackPressedDispatcher.addCallback(this, callback)
```

---

## Common Patterns

### Login/Logout Flow
```kotlin
// After successful login
startActivity(Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
})
finish()

// After logout
startActivity(Intent(this, LoginActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
})
finish()
```

### Deep Link Handling
```xml
<activity android:name=".DeepLinkActivity">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="https"
            android:host="example.com"
            android:pathPrefix="/product" />
    </intent-filter>
</activity>
```

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    intent.data?.let { uri ->
        val productId = uri.lastPathSegment
        loadProduct(productId)
    }
}
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Overriding `onBackPressed()` directly | Breaks predictive back | Use `OnBackPressedCallback` |
| Large data in Intent extras | TransactionTooLargeException | Pass ID, load from DB/cache |
| `singleInstance` for normal activities | Unexpected task behavior | Use `singleTop` or `singleTask` |
| Not handling process death | Lost state | Use `SavedStateHandle` |
| `resolveActivity()` on Android 11+ | Returns null incorrectly | Use try-catch with `startActivity()` |

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Get a result from an activity](https://developer.android.com/training/basics/intents/result) | Official | 0.95 | Activity Result API |
| 2 | [Tasks and back stack](https://developer.android.com/guide/components/activities/tasks-and-back-stack) | Official | 0.95 | Task management, launch modes |
| 3 | [Intents and intent filters](https://developer.android.com/guide/components/intents-filters) | Official | 0.95 | Intent types, filters |
| 4 | [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) | Official | 0.95 | Lifecycle callbacks |
| 5 | [Start activity with animation](https://developer.android.com/develop/ui/views/animations/transitions/start-activity) | Official | 0.95 | Shared element transitions |
| 6 | [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) | Official | 0.95 | SavedStateHandle |
| 7 | [Understand Activity launchMode](https://inthecheesefactory.com/blog/understand-android-activity-launchmode/en) | Blog | 0.90 | Visual launch mode explanation |
| 8 | [Navigation and Task Stacks](https://guides.codepath.com/android/Navigation-and-Task-Stacks) | Guide | 0.90 | Task navigation patterns |
| 9 | [Mastering Intent Flags](https://medium.com/@snaresh22/mastering-android-app-navigation-with-intent-flags-36f84409432b) | Blog | 0.85 | Flag combinations |
| 10 | [Activity Result API - Realm Blog](https://medium.com/realm/startactivityforresult-is-deprecated-82888d149f5d) | Blog | 0.85 | Migration guide |
| 11 | [Parcelable vs Serializable](https://proandroiddev.com/serializable-or-parcelable-why-and-which-one-17b274f3d3bb) | Blog | 0.85 | Performance comparison |
| 12 | [Process Death Handling](https://programmerofpersia.medium.com/best-practices-for-handling-process-death-in-android-applications-cheat-sheet-series-42004afda242) | Blog | 0.85 | State restoration patterns |
| 13 | [Shared Element Activity Transition](https://guides.codepath.com/android/shared-element-activity-transition) | Guide | 0.90 | Transition implementation |
| 14 | [PendingIntent](https://developer.android.com/reference/android/app/PendingIntent) | Official | 0.95 | Android 12 requirements |
| 15 | [Provide custom back navigation](https://developer.android.com/guide/navigation/navigation-custom-back) | Official | 0.95 | OnBackPressedCallback |

---

## Timeline: Activity Navigation Evolution

```
2008 ─── Activity + Intent (Android 1.0)
         └── startActivity, startActivityForResult
         └── Explicit/Implicit Intents

2011 ─── Fragments introduced (Honeycomb)
         └── Activity still main navigation unit

2015 ─── Activity transitions (Lollipop)
         └── Shared element animations
         └── Scene transitions

2020 ─── Activity Result API (Jetpack)
         └── registerForActivityResult
         └── ActivityResultContract

2021 ─── Android 12 changes
         └── PendingIntent FLAG_IMMUTABLE required
         └── singleInstancePerTask launch mode
         └── Back button moves to background (root activity)

2023 ─── Predictive Back (Android 13+)
         └── OnBackPressedCallback
         └── Gesture preview animations
```

---

*Generated: 2025-12-29*
*Purpose: Activity navigation patterns for android-navigation.md expansion*

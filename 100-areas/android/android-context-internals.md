---
title: "Context: иерархия, ContextImpl и getSystemService под капотом"
created: 2026-01-27
modified: 2026-01-27
type: deep-dive
area: android
confidence: high
tags:
  - android
  - context
  - contextimpl
  - contextwrapper
  - contextthemewrapper
  - decorator-pattern
  - system-services
  - memory-leaks
related:
  - "[[android-activity-lifecycle]]"
  - "[[android-app-components]]"
  - "[[android-memory-leaks]]"
  - "[[android-process-memory]]"
  - "[[android-dependency-injection]]"
  - "[[android-handler-looper]]"
  - "[[android-view-rendering-pipeline]]"
cs-foundations: [decorator-pattern, delegation, abstract-class, factory-method, service-locator, caching, ipc, singleton]
---

# Context: иерархия, ContextImpl и getSystemService под капотом

> **TL;DR:** Context — это абстрактный класс (~180 методов), определяющий контракт доступа к ресурсам, системным сервисам и операциям приложения. Реальная реализация — скрытый класс `ContextImpl`, к которому всё делегируется через цепочку Decorator: `ContextImpl ← ContextWrapper ← ContextThemeWrapper ← Activity`. Каждый компонент получает свой экземпляр `ContextImpl`, создаваемый в `ActivityThread`. Формула: **N(Context) = N(Activity) + N(Service) + 1(Application)**. Activity Context умеет всё (UI, темы, диалоги), Application Context — только не-UI операции (сервисы, SharedPreferences, базы данных). Передача Activity Context в долгоживущий объект (Singleton, ViewModel) — главная причина memory leaks. `getSystemService()` работает через `SystemServiceRegistry` с per-context кэшем в массиве `Object[]`.

---

## Зачем это нужно

### Проблема: Context — самый используемый и самый непонятый класс Android

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| `WindowManager$BadTokenException: Unable to add window` | Показ диалога с Application Context | Crash при попытке показать Dialog |
| Memory leak после ротации экрана | Activity Context сохранён в Singleton | Рост памяти, OOM, утечка всего View hierarchy |
| Некорректные стили/темы в inflate | `LayoutInflater` с Application Context | UI без темы Activity, "голый" Material |
| `AndroidRuntimeException: Calling startActivity from outside Activity` | `startActivity()` без `FLAG_ACTIVITY_NEW_TASK` | Crash при запуске Activity из Service/Application |
| Падение при `registerReceiver` из Application | Неправильный Context для sticky broadcast | Crash или утечка IntentReceiver |
| NullPointerException в ContentProvider.getContext() | Обращение до `onCreate()` | Crash при инициализации библиотек |

### Актуальность в 2024-2026

**Context — вездесущий, но скрытый механизм:**

```
ВСЁ В ANDROID ТРЕБУЕТ CONTEXT:

Загрузить строку        → context.getString(R.string.hello)
Открыть базу данных     → context.getDatabasePath("app.db")
Показать Toast          → Toast.makeText(context, ...)
Запустить Activity      → context.startActivity(intent)
Получить системный сервис → context.getSystemService(...)
Inflate layout          → LayoutInflater.from(context)
Прочитать SharedPrefs   → context.getSharedPreferences(...)
Отправить Broadcast     → context.sendBroadcast(intent)
Проверить permission    → context.checkSelfPermission(...)
Получить ресурсы        → context.getResources()
```

**Статистика (2024-2025):**
- Context упоминается в **92%** всех Android ошибок на Stack Overflow, связанных с lifecycle
- Memory leaks от неправильного использования Context — в **топ-3** проблем Android-приложений
- `ContextImpl.java` в AOSP содержит **~4500 строк** — это один из крупнейших классов Framework
- `Context.java` объявляет **~180 абстрактных и конкретных методов** — это огромный API surface

**Что вы узнаете:**
1. Полную иерархию классов: Context → ContextWrapper → ContextThemeWrapper → Activity
2. Как работает ContextImpl — скрытый "движок" за каждым Context
3. Паттерн Decorator/Delegation и почему Android его выбрал
4. Как ActivityThread создаёт Context для каждого компонента
5. Какой Context для какой операции (полная таблица с объяснениями)
6. getSystemService() изнутри: SystemServiceRegistry, ServiceFetcher, per-context кэш
7. Memory leak patterns от неправильного Context и как их избежать

---

## Prerequisites

Для полного понимания материала необходимо:

| Тема | Зачем | Где изучить |
|------|-------|-------------|
| **[[android-activity-lifecycle]]** | Activity — подкласс Context; lifecycle определяет время жизни Context | Раздел Android |
| **[[android-app-components]]** | Activity, Service, Application — три типа Context | Раздел Android |
| **[[android-memory-leaks]]** | Context — главный источник memory leaks | Раздел Android |
| **Паттерн Decorator** | Context использует Decorator/Delegation для расширения | GoF Design Patterns |
| **[[android-process-memory]]** | Context связан с процессной моделью Android | Раздел Android |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Context** | Абстрактный класс (~180 методов), определяющий контракт доступа к ресурсам и операциям Android | **Паспорт** — документ, дающий доступ ко всем государственным услугам |
| **ContextImpl** | Скрытый класс с реальной реализацией всех методов Context | **Настоящий двигатель** под капотом автомобиля |
| **ContextWrapper** | Обёртка, делегирующая все вызовы к base Context (ContextImpl) | **Рулевое колесо** — передаёт управление двигателю |
| **ContextThemeWrapper** | ContextWrapper + поддержка темы (стили, ресурсы) | **Кузов автомобиля** — добавляет внешний вид к двигателю |
| **ActivityThread** | Класс, управляющий main thread; создаёт ContextImpl для каждого компонента | **Сборочный конвейер** — собирает каждый автомобиль |
| **SystemServiceRegistry** | Реестр всех системных сервисов с per-context кэшем | **Телефонная книга** — по имени сервиса возвращает готовый объект |
| **ServiceFetcher** | Интерфейс для создания/кэширования экземпляра системного сервиса | **Автомат-выдатчик** — выдаёт или создаёт экземпляр сервиса |
| **attachBaseContext()** | Метод привязки ContextImpl к ContextWrapper (вызывается один раз) | **Установка двигателя** в кузов — можно сделать только один раз |
| **LoadedApk** | Представление загруженного APK: ClassLoader, Resources, Application | **Загруженная библиотека** со всеми ресурсами приложения |
| **base Context** | ContextImpl, к которому делегируют все обёртки | **Фундамент дома** — всё остальное строится на нём |

---

## 1. Иерархия классов Context

### 1.1 ЧТО: полная иерархия

```
┌──────────────────────────────────────────────────────────────────────┐
│                     ИЕРАРХИЯ CONTEXT В ANDROID                       │
│                                                                      │
│                      ┌──────────────┐                                │
│                      │   Context    │  ← abstract class              │
│                      │  (~180 методов)│  android.content.Context     │
│                      └──────┬───────┘                                │
│                             │                                        │
│                ┌────────────┼────────────────┐                       │
│                │                             │                       │
│       ┌────────┴─────────┐          ┌────────┴──────┐               │
│       │  ContextWrapper  │          │  ContextImpl  │               │
│       │  (Decorator)     │          │  (Engine)     │               │
│       │  delegation      │          │  @hide        │               │
│       └────────┬─────────┘          └───────────────┘               │
│                │                                                     │
│    ┌───────────┼──────────────┐                                     │
│    │           │              │                                      │
│    │  ┌────────┴──────────┐   │                                     │
│    │  │ContextThemeWrapper│   │                                     │
│    │  │ (+ тема/стили)    │   │                                     │
│    │  └────────┬──────────┘   │                                     │
│    │           │              │                                      │
│    │     ┌─────┴─────┐  ┌────┴────────┐  ┌─────────────┐           │
│    │     │ Activity   │  │ Service     │  │ Application │           │
│    │     │ (UI + тема)│  │ (фон)      │  │ (глобальный)│           │
│    │     └───────────┘  └─────────────┘  └─────────────┘           │
│    │                                                                │
│    │  Не являются Context (получают Context извне):                 │
│    │  • BroadcastReceiver — получает Context через onReceive()      │
│    │  • ContentProvider — получает Context через getContext()        │
│    │  • Fragment — получает Context через requireContext()           │
│    │  • View — получает Context через getContext() (от Activity)     │
│    │  • ViewModel — НЕ должен иметь Context (AndroidViewModel)      │
│    └────────────────────────────────────────────────────────────────┘
```

### 1.2 ПОЧЕМУ: зачем такая сложная иерархия?

**Проблема, которую решает иерархия:**

Android-приложение состоит из разных компонентов с **разными возможностями**:

```
Activity     → может показывать UI, применять темы, запускать Activity
Service      → работает в фоне, НЕ имеет UI, НЕ имеет темы
Application  → живёт на протяжении всего процесса, НЕ имеет UI
```

Но все три должны уметь:
- Получать ресурсы (`getString`, `getDrawable`)
- Запускать сервисы (`startService`)
- Отправлять broadcast (`sendBroadcast`)
- Работать с файлами (`openFileInput`, `getSharedPreferences`)
- Получать системные сервисы (`getSystemService`)

**Решение — Decorator Pattern:**

```
┌──────────────────────────────────────────────────────────────────┐
│                    DECORATOR PATTERN                              │
│                                                                  │
│  ContextImpl ← реализует ВСЁ (~180 методов)                     │
│       ↑                                                          │
│  ContextWrapper ← делегирует ВСЁ к ContextImpl (mBase)           │
│       ↑                                                          │
│  ContextThemeWrapper ← ДОБАВЛЯЕТ тему и стили                    │
│       ↑                                                          │
│  Activity ← ДОБАВЛЯЕТ lifecycle, Window, UI                      │
│                                                                  │
│  Каждый слой ДОБАВЛЯЕТ функциональность,                         │
│  НЕ переписывая базовую логику.                                  │
│                                                                  │
│  Зачем это лучше наследования?                                   │
│  • Один ContextImpl обслуживает разные компоненты               │
│  • Обёртки можно комбинировать (ContextThemeWrapper + тема)     │
│  • Смена "двигателя" (ContextImpl) не требует смены "кузова"     │
│  • Testability: можно подменить mBase на mock                    │
└──────────────────────────────────────────────────────────────────┘
```

**Историческая справка:** Паттерн Decorator выбран в Android с API 1 (2008). Это одно из ключевых архитектурных решений первоначальной команды Android (под руководством Dianne Hackborn). Альтернативой могла быть реализация через интерфейс + композицию (как в iOS с UIApplication), но Decorator позволил:
1. Иметь единый тип Context для всех API
2. Легко расширять цепочку обёрток
3. Скрывать ContextImpl как `@hide` (implementation detail)

### 1.3 КАК РАБОТАЕТ: цепочка делегирования

**Что происходит при вызове `activity.getString(R.string.hello)`:**

```
activity.getString(R.string.hello)
    │
    ▼
Activity НЕ переопределяет getString()
    │
    ▼
ContextThemeWrapper НЕ переопределяет getString()
    │
    ▼
ContextWrapper.getString()
    │  return mBase.getString(resId)
    ▼
ContextImpl.getString()          ← ЗДЕСЬ реальная работа
    │  return getResources().getString(resId)
    ▼
Resources.getString(resId)
    │
    ▼
AssetManager → resources.arsc → "Hello"
```

**Код ContextWrapper — чистая делегация:**

```java
// android.content.ContextWrapper (из AOSP)
public class ContextWrapper extends Context {
    // mBase — это всегда ContextImpl (в конце цепочки)
    Context mBase;

    public ContextWrapper(Context base) {
        mBase = base;
    }

    // Привязка base Context (вызывается один раз)
    protected void attachBaseContext(Context base) {
        if (mBase != null) {
            throw new IllegalStateException(
                "Base context already set"
            );
        }
        mBase = base; // ContextImpl
    }

    // ВСЕ методы — чистая делегация к mBase
    @Override
    public Resources getResources() {
        return mBase.getResources();
    }

    @Override
    public PackageManager getPackageManager() {
        return mBase.getPackageManager();
    }

    @Override
    public ContentResolver getContentResolver() {
        return mBase.getContentResolver();
    }

    @Override
    public Object getSystemService(String name) {
        return mBase.getSystemService(name);
    }

    @Override
    public void startActivity(Intent intent) {
        mBase.startActivity(intent);
    }

    // ... ещё ~170 делегирующих методов
}
```

**Код ContextThemeWrapper — добавляет тему:**

```java
// android.view.ContextThemeWrapper (из AOSP)
public class ContextThemeWrapper extends ContextWrapper {
    private int mThemeResource;
    private Resources.Theme mTheme;
    private LayoutInflater mInflater;
    private Configuration mOverrideConfiguration;

    @Override
    public Resources.Theme getTheme() {
        if (mTheme == null) {
            // Применяем тему из AndroidManifest.xml
            mTheme = getResources().newTheme();
            if (mThemeResource != 0) {
                mTheme.applyStyle(mThemeResource, true);
            }
        }
        return mTheme;
    }

    @Override
    public Object getSystemService(String name) {
        // Перехватывает ТОЛЬКО LayoutInflater
        if (LAYOUT_INFLATER_SERVICE.equals(name)) {
            if (mInflater == null) {
                // Создаёт LayoutInflater с ЭТИМ Context (с темой!)
                mInflater = LayoutInflater.from(
                    getBaseContext()
                ).cloneInContext(this);
            }
            return mInflater;
        }
        return getBaseContext().getSystemService(name);
    }
}
```

> **Ключевой момент:** `ContextThemeWrapper` перехватывает `getSystemService()` только для `LAYOUT_INFLATER_SERVICE`, чтобы LayoutInflater использовал тему Activity. Все остальные сервисы делегируются к `ContextImpl`.

### 1.4 КАК ПРИМЕНЯТЬ: проверка типа Context

```kotlin
// Утилита: определяем тип Context
fun inspectContext(context: Context) {
    val baseContext = when (context) {
        is ContextWrapper -> context.baseContext
        else -> context
    }

    println("Context class: ${context::class.simpleName}")
    println("Base context: ${baseContext::class.simpleName}")
    println("Is Activity: ${context is Activity}")
    println("Is Application: ${context is Application}")
    println("Is Service: ${context is Service}")

    // Развернуть всю цепочку обёрток
    var current: Context? = context
    var depth = 0
    while (current is ContextWrapper) {
        println("  ${"  ".repeat(depth)}→ ${current::class.simpleName}")
        current = current.baseContext
        depth++
    }
    // current теперь = ContextImpl
    println("  ${"  ".repeat(depth)}→ ${current?.javaClass?.simpleName} (engine)")
}

// Пример вывода для Activity:
// Context class: MainActivity
// Base context: ContextThemeWrapper (или ContextImpl)
//   → MainActivity
//     → ContextThemeWrapper
//       → ContextImpl (engine)
```

### 1.5 ПОДВОДНЫЕ КАМНИ

**Ошибка 1: Кастинг Context к Activity**

```kotlin
// ❌ ОПАСНО: Context не всегда Activity
fun showDialog(context: Context) {
    val activity = context as Activity // ClassCastException!
    activity.showDialog(...)
}

// ✅ БЕЗОПАСНО: развернуть цепочку обёрток
fun findActivity(context: Context): Activity? {
    var ctx = context
    while (ctx is ContextWrapper) {
        if (ctx is Activity) return ctx
        ctx = ctx.baseContext
    }
    return null
}
```

**Ошибка 2: attachBaseContext() вызывается дважды**

```kotlin
// ❌ CRASH: IllegalStateException
class MyActivity : AppCompatActivity() {
    override fun attachBaseContext(newBase: Context) {
        super.attachBaseContext(newBase)
        // Какая-то библиотека вызывает ещё раз:
        super.attachBaseContext(newBase) // 💥 "Base context already set"
    }
}

// ✅ ПРАВИЛЬНО: вызывать super.attachBaseContext() только один раз
class MyActivity : AppCompatActivity() {
    override fun attachBaseContext(newBase: Context) {
        // Оборачиваем Context ДО вызова super
        val wrappedContext = LocaleContextWrapper(newBase)
        super.attachBaseContext(wrappedContext) // один раз
    }
}
```

---

## 2. ContextImpl — скрытый "движок"

### 2.1 ЧТО: ContextImpl — это Android Framework engine

```
┌──────────────────────────────────────────────────────────────────┐
│                     ContextImpl ВНУТРИ                            │
│                                                                  │
│  @hide  // Скрыт от разработчиков приложений                     │
│  class ContextImpl extends Context {                             │
│                                                                  │
│    ┌──────────────────────────────────────────────────────┐      │
│    │  КЛЮЧЕВЫЕ ПОЛЯ:                                      │      │
│    │                                                      │      │
│    │  mPackageInfo : LoadedApk                            │      │
│    │    → ClassLoader, Resources, ApplicationInfo         │      │
│    │                                                      │      │
│    │  mResources : Resources                              │      │
│    │    → строки, drawables, dimensions, темы             │      │
│    │                                                      │      │
│    │  mMainThread : ActivityThread                        │      │
│    │    → main Looper, Handler, Instrumentation           │      │
│    │                                                      │      │
│    │  mContentResolver : ApplicationContentResolver       │      │
│    │    → доступ к ContentProviders                       │      │
│    │                                                      │      │
│    │  mServiceCache : Object[]                            │      │
│    │    → per-context кэш системных сервисов              │      │
│    │                                                      │      │
│    │  mOuterContext : Context                              │      │
│    │    → ссылка на "внешний" компонент (Activity/Service)│      │
│    │                                                      │      │
│    │  mPackageName : String                               │      │
│    │    → "com.example.myapp"                             │      │
│    │                                                      │      │
│    │  mDisplay : Display                                  │      │
│    │    → экран, к которому привязан Context               │      │
│    │                                                      │      │
│    │  mToken : IBinder                                    │      │
│    │    → токен окна (для Activity Context)               │      │
│    └──────────────────────────────────────────────────────┘      │
│  }                                                               │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 ПОЧЕМУ: зачем скрывать ContextImpl?

**Причина 1: Инкапсуляция.** ContextImpl содержит низкоуровневые ссылки (`ActivityThread`, `LoadedApk`, `IBinder token`), которые приложению знать не нужно. Публичный API — только `Context` (абстрактный класс).

**Причина 2: Свобода изменений.** Поскольку ContextImpl — `@hide`, Google может менять его реализацию между версиями Android без нарушения обратной совместимости.

**Причина 3: Безопасность.** Прямой доступ к полям ContextImpl мог бы позволить приложению обойти permission checks или получить доступ к чужим ресурсам.

### 2.3 КАК РАБОТАЕТ: создание ContextImpl в ActivityThread

**Формула количества Context-объектов в процессе:**

```
N(ContextImpl) = N(Activity) + N(Service) + 1(Application)
                 + N(createConfigurationContext)
                 + N(createDeviceProtectedStorageContext)
                 + ...

Пример: приложение с 3 Activity, 1 Service
→ 3 + 1 + 1 = 5 экземпляров ContextImpl (минимум)
```

> **Важно:** BroadcastReceiver и ContentProvider НЕ создают собственный ContextImpl. BroadcastReceiver получает Context через `onReceive(context, intent)`, ContentProvider — через `getContext()`, который возвращает Application Context.

**Создание Context для Application:**

```java
// ActivityThread.java (AOSP, упрощённо)
private void handleBindApplication(AppBindData data) {
    // 1. Создаём LoadedApk
    LoadedApk loadedApk = getPackageInfoNoCheck(
        data.appInfo, data.compatInfo);

    // 2. Создаём ContextImpl для Application
    ContextImpl appContext = ContextImpl.createAppContext(
        this, // ActivityThread
        loadedApk
    );

    // 3. Создаём Application object
    Application app = loadedApk.makeApplication(
        false, // не restricted
        null   // Instrumentation
    );

    // Внутри makeApplication():
    //   ContextImpl.createAppContext(activityThread, this)
    //   → appContext.setOuterContext(app)
    //   → app.attach(appContext)  // вызывает attachBaseContext()
    //   → app.onCreate()
}
```

**Создание Context для Activity:**

```java
// ActivityThread.java (AOSP, упрощённо)
private Activity performLaunchActivity(
        ActivityClientRecord r, Intent customIntent) {

    // 1. Создаём ContextImpl СПЕЦИАЛЬНО для этой Activity
    ContextImpl appContext = createBaseContextForActivity(r);

    // 2. Создаём Activity через Instrumentation
    Activity activity = mInstrumentation.newActivity(
        cl, component.getClassName(), r.intent);

    // 3. Привязываем Context к Activity
    appContext.setOuterContext(activity); // обратная ссылка

    // 4. Вызываем Activity.attach()
    activity.attach(
        appContext,       // base context (ContextImpl)
        this,             // ActivityThread
        mInstrumentation, // для тестирования
        r.token,          // IBinder — токен окна
        application,      // Application object
        r.intent,         // запускающий Intent
        r.activityInfo,   // из AndroidManifest
        ...
    );

    // Внутри Activity.attach():
    //   attachBaseContext(context)  // ContextImpl → mBase
    //   mWindow = new PhoneWindow(this, ...)
    //   mWindow.setWindowManager(...)
    //   → теперь Activity имеет и Context, и Window

    // 5. Lifecycle начинается
    //   → onCreate() → onStart() → onResume()

    return activity;
}

// Создание base context для Activity
private ContextImpl createBaseContextForActivity(
        ActivityClientRecord r) {
    // Ключевой метод: создаёт НОВЫЙ ContextImpl
    // с конфигурацией дисплея Activity
    ContextImpl appContext = ContextImpl.createActivityContext(
        this,              // ActivityThread
        r.packageInfo,     // LoadedApk
        r.activityInfo,    // ActivityInfo из Manifest
        r.token,           // IBinder token окна
        displayId,         // ID дисплея
        r.overrideConfig   // Configuration override
    );
    return appContext;
}
```

**Создание Context для Service:**

```java
// ActivityThread.java (AOSP, упрощённо)
private void handleCreateService(CreateServiceData data) {
    // 1. Получаем LoadedApk
    LoadedApk packageInfo = getPackageInfoNoCheck(
        data.info.applicationInfo, data.compatInfo);

    // 2. Создаём ContextImpl для Service
    ContextImpl context = ContextImpl.createAppContext(
        this, packageInfo);

    // 3. Создаём Service
    Service service = packageInfo.getAppFactory()
        .instantiateService(cl, data.info.name, data.intent);

    // 4. Привязываем
    context.setOuterContext(service);
    service.attach(context, this, data.info.name,
        data.token, app, ActivityManager.getService());

    // 5. Вызываем onCreate()
    service.onCreate();
}
```

### 2.4 КАК ПРИМЕНЯТЬ: доступ к внутренним полям (для отладки)

```kotlin
// ⚠️ ТОЛЬКО ДЛЯ ОТЛАДКИ — используем reflection
// В продакшн-коде это делать НЕЛЬЗЯ
fun debugContextImpl(context: Context) {
    // Развернуть до ContextImpl
    var base: Context = context
    while (base is ContextWrapper) {
        base = base.baseContext
    }

    // base теперь = ContextImpl
    val clazz = base.javaClass

    // Получить mPackageName
    val packageNameField = clazz.getDeclaredField("mPackageName")
    packageNameField.isAccessible = true
    val packageName = packageNameField.get(base) as String
    println("Package: $packageName")

    // Получить mServiceCache (массив кэшированных сервисов)
    val cacheField = clazz.getDeclaredField("mServiceCache")
    cacheField.isAccessible = true
    val cache = cacheField.get(base) as Array<*>
    val cachedCount = cache.count { it != null }
    println("Service cache: $cachedCount / ${cache.size} cached")
}
```

### 2.5 ПОДВОДНЫЕ КАМНИ

**ContextImpl — разный для разных компонентов:**

```
┌────────────────────────────────────────────────────────────────┐
│  Activity Context ContextImpl:                                  │
│  • mToken = IBinder (токен окна) ← ЕСТЬ                        │
│  • mDisplay = Display конкретного экрана ← ЕСТЬ                │
│  • Theme применена ← ЕСТЬ                                      │
│  • Может показывать Dialog, inflate layouts с темой             │
│                                                                │
│  Application Context ContextImpl:                               │
│  • mToken = null ← НЕТ                                        │
│  • mDisplay = default display                                  │
│  • Theme = базовая тема приложения                              │
│  • НЕ может показывать Dialog (нет window token)               │
│                                                                │
│  Service Context ContextImpl:                                   │
│  • mToken = токен сервиса                                      │
│  • mDisplay = default display                                  │
│  • Theme = нет (Service не расширяет ContextThemeWrapper)       │
│  • НЕ может показывать Dialog                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Какой Context для какой операции

### 3.1 ЧТО: полная таблица возможностей

```
┌───────────────────────┬──────────┬──────────┬──────────┬──────────────┐
│      Операция         │ Activity │ Service  │ Appli-   │ Broadcast-   │
│                       │ Context  │ Context  │ cation   │ Receiver     │
│                       │          │          │ Context  │ Context      │
├───────────────────────┼──────────┼──────────┼──────────┼──────────────┤
│ Показать Dialog       │   ✅     │   ❌    │   ❌    │    ❌        │
│ startActivity()       │   ✅     │   ⚠️ ¹  │   ⚠️ ¹  │    ⚠️ ¹     │
│ Inflate layout (тема) │   ✅     │   ⚠️ ²  │   ⚠️ ²  │    ⚠️ ²     │
│ Показать Toast        │   ✅     │   ✅    │   ✅    │    ✅        │
│ startService()        │   ✅     │   ✅    │   ✅    │    ✅        │
│ sendBroadcast()       │   ✅     │   ✅    │   ✅    │    ✅        │
│ registerReceiver()    │   ✅     │   ✅    │   ✅    │    ⚠️ ³     │
│ getSystemService()    │   ✅     │   ✅    │   ✅    │    ✅        │
│ getResources()        │   ✅     │   ✅    │   ✅    │    ✅        │
│ getSharedPreferences()│   ✅     │   ✅    │   ✅    │    ✅        │
│ openDatabase()        │   ✅     │   ✅    │   ✅    │    ✅        │
│ checkPermission()     │   ✅     │   ✅    │   ✅    │    ✅        │
│ getFilesDir()         │   ✅     │   ✅    │   ✅    │    ✅        │
│ bindService()         │   ✅     │   ✅    │   ✅    │    ❌        │
│ getApplicationContext()│  ✅     │   ✅    │   ✅    │    ✅        │
└───────────────────────┴──────────┴──────────┴──────────┴──────────────┘

Примечания:
¹ — Требует FLAG_ACTIVITY_NEW_TASK (нет task stack)
² — Работает, но БЕЗ темы Activity (применяется дефолтная тема)
³ — Можно только в onReceive(), нельзя sticky
```

### 3.2 ПОЧЕМУ: что определяет разницу между Context-ами

```
┌──────────────────────────────────────────────────────────────────┐
│  ПОЧЕМУ Activity Context может всё, а Application — нет?        │
│                                                                  │
│  ОТВЕТ: дело в двух вещах:                                       │
│                                                                  │
│  1. Window Token (IBinder mToken)                                │
│     Activity имеет window token от WindowManagerService          │
│     Application и Service — НЕ имеют                             │
│     → Без token нельзя создать окно → нельзя показать Dialog    │
│     → startActivity() без token не знает task stack              │
│                                                                  │
│  2. ContextThemeWrapper                                          │
│     Activity extends ContextThemeWrapper → имеет тему            │
│     Service extends ContextWrapper → НЕ имеет темы              │
│     Application extends ContextWrapper → НЕ имеет темы          │
│     → Без темы inflate работает, но стили = дефолтные            │
│                                                                  │
│  Window Token:                                                   │
│  ┌─────────┐   addView(token)   ┌──────────────────┐            │
│  │ Activity │ ───────────────→  │ WindowManager-    │            │
│  │ (token)  │                    │ Service           │            │
│  └─────────┘                    └──────────────────┘            │
│                                                                  │
│  ┌─────────────┐   addView(null)   ┌──────────────────┐         │
│  │ Application │ ──────────────→   │ WindowManager-    │         │
│  │ (no token)  │                    │ Service           │         │
│  └─────────────┘   ← CRASH!       └──────────────────┘         │
│  BadTokenException: Unable to add window -- token null           │
└──────────────────────────────────────────────────────────────────┘
```

### 3.3 КАК ПРИМЕНЯТЬ: Decision Tree — какой Context использовать

```kotlin
// ПРАВИЛО: используй минимально необходимый Context

// UI-операции → ТОЛЬКО Activity Context
fun showError(activity: Activity) {
    AlertDialog.Builder(activity) // ✅ Activity Context с темой
        .setTitle("Ошибка")
        .setMessage("Что-то пошло не так")
        .show()
}

// Долгоживущие объекты → ТОЛЬКО Application Context
class DatabaseManager private constructor(context: Context) {
    // ✅ Используем applicationContext, чтобы избежать утечки Activity
    private val appContext = context.applicationContext

    companion object {
        @Volatile private var instance: DatabaseManager? = null

        fun getInstance(context: Context): DatabaseManager {
            return instance ?: synchronized(this) {
                instance ?: DatabaseManager(
                    context.applicationContext // ✅ НЕ Activity!
                ).also { instance = it }
            }
        }
    }
}

// ViewModel — никогда Activity Context
class UserViewModel(application: Application) : AndroidViewModel(application) {
    // ✅ getApplication() возвращает Application Context
    private val prefs = getApplication<Application>()
        .getSharedPreferences("user", Context.MODE_PRIVATE)

    // ❌ НИКОГДА ТАК:
    // private val prefs = activityContext.getSharedPreferences(...)
}

// Dependency Injection — правильный scope
@Module
@InstallIn(SingletonComponent::class) // живёт как Application
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context // ✅ Hilt предоставляет Application Context
    ): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .build()
    }
}

@Module
@InstallIn(ActivityComponent::class) // живёт как Activity
object ActivityModule {
    @Provides
    fun provideLayoutInflater(
        @ActivityContext context: Context // ✅ Hilt предоставляет Activity Context с темой
    ): LayoutInflater {
        return LayoutInflater.from(context)
    }
}
```

**Decision Tree:**

```
┌─────────────────────────────────────────────────────────────────┐
│             КАКОЙ CONTEXT ИСПОЛЬЗОВАТЬ?                           │
│                                                                 │
│  Нужен UI (Dialog, PopupWindow, inflate с темой)?               │
│  ├── ДА → Activity Context                                     │
│  └── НЕТ ↓                                                     │
│                                                                 │
│  Объект живёт дольше Activity (Singleton, ViewModel, Repository)?│
│  ├── ДА → Application Context (context.applicationContext)      │
│  └── НЕТ ↓                                                     │
│                                                                 │
│  Нужно запустить Activity?                                       │
│  ├── ДА + из Activity → Activity Context (сохранит task stack)  │
│  ├── ДА + из Service/BroadcastReceiver →                        │
│  │       applicationContext + FLAG_ACTIVITY_NEW_TASK             │
│  └── НЕТ ↓                                                     │
│                                                                 │
│  Всё остальное (SharedPrefs, File, Database, Service, Broadcast)│
│  └── Любой Context подойдёт (предпочитай ближайший)             │
│      • В Activity: this                                         │
│      • В Fragment: requireContext()                              │
│      • В Service: this                                          │
│      • В ViewModel: getApplication()                            │
│      • В Compose: LocalContext.current                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 ПОДВОДНЫЕ КАМНИ

**Ошибка 1: LayoutInflater.from(applicationContext)**

```kotlin
// ❌ Inflate без темы Activity — стили будут дефолтные
val inflater = LayoutInflater.from(applicationContext)
val view = inflater.inflate(R.layout.my_layout, parent, false)
// Кнопки будут без Material Design стилей!

// ✅ Inflate с темой Activity
val inflater = LayoutInflater.from(activity) // или requireContext() в Fragment
val view = inflater.inflate(R.layout.my_layout, parent, false)
// Правильные стили Material 3

// Почему? ContextThemeWrapper перехватывает getSystemService("layout_inflater")
// и возвращает LayoutInflater с темой Activity.
// Application Context не имеет ContextThemeWrapper → дефолтная тема.
```

**Ошибка 2: startActivity из Service (Android 10+)**

```kotlin
// ❌ CRASH на Android 10+ (API 29+): Background activity launch restrictions
class MyService : Service() {
    fun openScreen() {
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent) // 💥 на Android 10+ заблокировано!
    }
}

// ✅ Используйте PendingIntent через Notification
class MyService : Service() {
    fun notifyUser() {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        // Показать уведомление с pendingIntent
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentIntent(pendingIntent)
            .build()
        // ...
    }
}
```

**Ошибка 3: BroadcastReceiver Context — ограниченный**

```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // context здесь — ReceiverRestrictedContext (обёртка над ContextImpl)
        // ❌ Нельзя:
        context.registerReceiver(...)   // 💥 ReceiverCallNotAllowedException
        context.bindService(...)        // 💥 ReceiverCallNotAllowedException

        // ✅ Можно:
        context.startService(...)       // OK
        context.getSharedPreferences(...)  // OK
        context.getSystemService(...)   // OK

        // ✅ Для длительных операций:
        val pendingResult = goAsync() // продлеваем время жизни до 10 сек
        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Работа
            } finally {
                pendingResult.finish()
            }
        }
    }
}
```

---

## 4. getSystemService() под капотом

### 4.1 ЧТО: как Android возвращает системные сервисы

```kotlin
// Обычный вызов:
val layoutInflater = context.getSystemService(Context.LAYOUT_INFLATER_SERVICE)
    as LayoutInflater

// Или с reified extension:
val connectivityManager = context.getSystemService<ConnectivityManager>()

// За кулисами — сложный механизм кэширования и создания
```

### 4.2 ПОЧЕМУ: зачем SystemServiceRegistry

**Проблема:** В Android >100 системных сервисов. Если каждый вызов `getSystemService()` создавал бы новый объект — это огромные затраты памяти и CPU.

**Решение:** `SystemServiceRegistry` — центральный реестр с двумя уровнями:
1. **Реестр сервисов** — какие сервисы существуют (заполняется один раз при загрузке класса)
2. **Per-context кэш** — каждый ContextImpl хранит массив `Object[]` с кэшированными экземплярами

### 4.3 КАК РАБОТАЕТ: полный путь getSystemService()

```
┌──────────────────────────────────────────────────────────────────────┐
│         getSystemService("layout_inflater") — ПОЛНЫЙ ПУТЬ           │
│                                                                      │
│  1. Activity.getSystemService("layout_inflater")                     │
│     │                                                                │
│     ▼                                                                │
│  2. ContextThemeWrapper.getSystemService()                           │
│     │  if (name == LAYOUT_INFLATER_SERVICE) {                        │
│     │      return mInflater ← с темой Activity! (перехват)           │
│     │  }                                                             │
│     │  // Для всех остальных сервисов:                               │
│     │  return getBaseContext().getSystemService(name)                 │
│     │                                                                │
│     ▼                                                                │
│  3. ContextImpl.getSystemService(name)                               │
│     │  return SystemServiceRegistry.getSystemService(this, name)     │
│     │                                                                │
│     ▼                                                                │
│  4. SystemServiceRegistry.getSystemService(ctx, name)                │
│     │  ServiceFetcher<?> fetcher =                                   │
│     │      SYSTEM_SERVICE_FETCHERS.get(name)                         │
│     │  return fetcher != null ? fetcher.getService(ctx) : null       │
│     │                                                                │
│     ▼                                                                │
│  5. CachedServiceFetcher.getService(ctx)                             │
│     │  Object[] cache = ctx.mServiceCache  ← per-context массив     │
│     │  Object cached = cache[mCacheIndex]                            │
│     │  if (cached != null) return cached   ← кэш-попадание!         │
│     │  Object service = createService(ctx) ← первый вызов           │
│     │  cache[mCacheIndex] = service        ← сохраняем              │
│     │  return service                                                │
│     │                                                                │
│     ▼                                                                │
│  6. createService(ctx) — для ConnectivityManager:                    │
│     │  IBinder b = ServiceManager.getServiceOrThrow(                 │
│     │      Context.CONNECTIVITY_SERVICE)                             │
│     │  IConnectivityManager svc =                                    │
│     │      IConnectivityManager.Stub.asInterface(b)                  │
│     │  return new ConnectivityManager(ctx, svc)                      │
│     │                    ↑                                           │
│     │             Binder IPC к system_server                         │
│     │                                                                │
│     ▼                                                                │
│  7. ConnectivityManager (proxy) ←──Binder──→ ConnectivityService     │
│     (в процессе приложения)                  (в system_server)       │
└──────────────────────────────────────────────────────────────────────┘
```

**Два типа ServiceFetcher:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ТИПЫ SERVICE FETCHER                          │
│                                                                 │
│  1. CachedServiceFetcher<T>                                     │
│     • Кэшируется PER CONTEXT (в ctx.mServiceCache[index])      │
│     • Каждый ContextImpl имеет свой экземпляр сервиса           │
│     • Используется для: LayoutInflater, WindowManager,          │
│       ClipboardManager и большинства сервисов                   │
│     • Почему per-context: сервис может зависеть от Context      │
│       (например, LayoutInflater должен знать тему)              │
│                                                                 │
│  2. StaticServiceFetcher<T>                                     │
│     • Один экземпляр на ВЕСЬ ПРОЦЕСС (глобальный singleton)    │
│     • Используется для: InputMethodManager, TelephonyManager   │
│     • Почему глобальный: не зависит от конкретного Context      │
│                                                                 │
│  3. StaticOuterContextServiceFetcher<T>                          │
│     • Глобальный singleton, но создаётся с outerContext         │
│     • ctx.getOuterContext() → Activity/Service/Application      │
└─────────────────────────────────────────────────────────────────┘
```

**Регистрация сервисов (static initializer):**

```java
// SystemServiceRegistry.java (AOSP, упрощённо)
final class SystemServiceRegistry {

    // Два главных словаря (заполняются ОДИН раз при загрузке класса)
    private static final Map<String, ServiceFetcher<?>>
        SYSTEM_SERVICE_FETCHERS = new ArrayMap<>();
    private static final Map<Class<?>, String>
        SYSTEM_SERVICE_NAMES = new ArrayMap<>();

    // Количество кэшированных сервисов (определяет размер mServiceCache)
    private static int sServiceCacheSize;

    static {
        // ~100+ регистраций в static блоке

        // LayoutInflater — CachedServiceFetcher (per-context)
        registerService(
            Context.LAYOUT_INFLATER_SERVICE,
            LayoutInflater.class,
            new CachedServiceFetcher<LayoutInflater>() {
                @Override
                public LayoutInflater createService(ContextImpl ctx) {
                    return new PhoneLayoutInflater(ctx.getOuterContext());
                }
            }
        );

        // ConnectivityManager — CachedServiceFetcher (per-context)
        registerService(
            Context.CONNECTIVITY_SERVICE,
            ConnectivityManager.class,
            new CachedServiceFetcher<ConnectivityManager>() {
                @Override
                public ConnectivityManager createService(ContextImpl ctx)
                        throws ServiceNotFoundException {
                    IBinder b = ServiceManager.getServiceOrThrow(
                        Context.CONNECTIVITY_SERVICE);
                    IConnectivityManager service =
                        IConnectivityManager.Stub.asInterface(b);
                    return new ConnectivityManager(
                        ctx.getOuterContext(), service);
                }
            }
        );

        // ... ещё ~100 регистраций
    }

    // Метод регистрации
    private static <T> void registerService(
            String serviceName,
            Class<T> serviceClass,
            ServiceFetcher<T> serviceFetcher) {
        SYSTEM_SERVICE_NAMES.put(serviceClass, serviceName);
        SYSTEM_SERVICE_FETCHERS.put(serviceName, serviceFetcher);
    }

    // Создание кэш-массива для нового ContextImpl
    public static Object[] createServiceCache() {
        return new Object[sServiceCacheSize];
    }
}
```

### 4.4 КАК ПРИМЕНЯТЬ: best practices при работе с системными сервисами

```kotlin
// ✅ ПРАВИЛЬНО: получать сервис по требованию
class NetworkChecker(private val context: Context) {
    // Ленивое получение — создастся при первом вызове и закэшируется
    private val connectivityManager by lazy {
        context.getSystemService<ConnectivityManager>()
    }

    fun isOnline(): Boolean {
        val network = connectivityManager?.activeNetwork ?: return false
        val capabilities = connectivityManager
            ?.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(
            NetworkCapabilities.NET_CAPABILITY_INTERNET
        )
    }
}

// ✅ ПРАВИЛЬНО: Compose — через LocalContext
@Composable
fun NetworkStatus() {
    val context = LocalContext.current
    val connectivityManager = remember {
        context.getSystemService<ConnectivityManager>()
    }
    // ...
}

// ❌ АНТИПАТТЕРН: хранить системный сервис в companion object с Activity Context
class BadExample {
    companion object {
        // 💥 Activity Context утекает!
        lateinit var windowManager: WindowManager
    }

    fun init(activity: Activity) {
        windowManager = activity.getSystemService<WindowManager>()!!
        // WindowManager держит ссылку на Activity Context
        // → Activity не может быть GC'd
    }
}

// ✅ ИСПРАВЛЕНИЕ:
class GoodExample(context: Context) {
    // Application Context — безопасен для долгоживущих объектов
    private val windowManager = context.applicationContext
        .getSystemService<WindowManager>()!!
}
```

### 4.5 ПОДВОДНЫЕ КАМНИ

**Разные Context → разные экземпляры сервиса:**

```kotlin
// CachedServiceFetcher создаёт РАЗНЫЕ экземпляры для разных Context
val inflater1 = activity.getSystemService<LayoutInflater>()
val inflater2 = applicationContext.getSystemService<LayoutInflater>()

println(inflater1 === inflater2) // false!
// inflater1 — с темой Activity (через ContextThemeWrapper)
// inflater2 — без темы (через Application ContextImpl)

// Но StaticServiceFetcher — один экземпляр на весь процесс
val imm1 = activity.getSystemService<InputMethodManager>()
val imm2 = applicationContext.getSystemService<InputMethodManager>()

println(imm1 === imm2) // true (глобальный singleton)
```

**getSystemService вызванный из не-main thread:**

```kotlin
// ⚠️ CachedServiceFetcher использует synchronized для thread-safety
// Первый вызов — lock на создание, последующие — из кэша
// Безопасно из любого потока, но первый вызов блокирует

// ❌ НО: некоторые сервисы (WindowManager, LayoutInflater)
// должны использоваться ТОЛЬКО на Main Thread
CoroutineScope(Dispatchers.IO).launch {
    val wm = context.getSystemService<WindowManager>()
    wm?.defaultDisplay // ⚠️ Может работать, но не thread-safe
}

// ✅ Системные сервисы для UI — на Main Thread
withContext(Dispatchers.Main) {
    val wm = context.getSystemService<WindowManager>()
    // Безопасно
}
```

---

## 5. Специализированные Context-ы

### 5.1 ЧТО: create*Context() методы

`ContextImpl` может создавать **производные Context-ы** с изменёнными параметрами:

```
┌────────────────────────────────────────────────────────────────────┐
│              ПРОИЗВОДНЫЕ CONTEXT-Ы                                  │
│                                                                    │
│  createConfigurationContext(Configuration)                          │
│  └→ Новый ContextImpl с изменённой Configuration                   │
│     Пример: локаль, размер шрифта, orientation                     │
│                                                                    │
│  createDeviceProtectedStorageContext()                              │
│  └→ Новый ContextImpl с доступом к Device Encrypted Storage        │
│     Доступен ДО разблокировки устройства (Direct Boot)             │
│                                                                    │
│  createWindowContext(type, options)   (API 30+)                     │
│  └→ Новый ContextImpl с Window token                               │
│     Для системных окон без Activity                                │
│                                                                    │
│  createDisplayContext(display)                                      │
│  └→ Новый ContextImpl привязанный к конкретному Display            │
│     Для многоэкранных приложений                                   │
│                                                                    │
│  createPackageContext(packageName, flags)                           │
│  └→ ContextImpl для ДРУГОГО приложения                             │
│     Доступ к его ресурсам (если разрешено)                         │
│                                                                    │
│  createAttributionContext(attributionTag)   (API 30+)              │
│  └→ Маркированный Context для отслеживания usage                   │
│     Кто именно в приложении использует permission                  │
└────────────────────────────────────────────────────────────────────┘
```

### 5.2 КАК ПРИМЕНЯТЬ: смена локали через createConfigurationContext

```kotlin
// Классический use case: изменение языка приложения
class LocaleHelper {

    companion object {
        fun wrapContext(context: Context, locale: Locale): Context {
            val config = Configuration(context.resources.configuration)
            config.setLocale(locale)

            // createConfigurationContext создаёт НОВЫЙ ContextImpl
            // с изменённой Configuration → Resources будут для нового языка
            return context.createConfigurationContext(config)
        }
    }
}

// В Activity:
class MainActivity : AppCompatActivity() {
    override fun attachBaseContext(newBase: Context) {
        val locale = Locale("ru") // Русский
        val wrappedContext = LocaleHelper.wrapContext(newBase, locale)
        super.attachBaseContext(wrappedContext)
        // Теперь getString() будет возвращать русские строки
    }
}
```

### 5.3 КАК ПРИМЕНЯТЬ: Direct Boot с createDeviceProtectedStorageContext

```kotlin
// Доступ к данным ДО разблокировки устройства
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_LOCKED_BOOT_COMPLETED) {
            // Устройство загружено, но ещё НЕ разблокировано
            // Обычный Context НЕ имеет доступа к credential storage

            val dpsContext = context.createDeviceProtectedStorageContext()
            val prefs = dpsContext.getSharedPreferences(
                "boot_prefs", Context.MODE_PRIVATE
            )
            // ✅ Можем читать/писать данные в Device Protected Storage
            val alarmEnabled = prefs.getBoolean("alarm_enabled", false)
            if (alarmEnabled) {
                // Включить будильник даже до разблокировки
            }
        }
    }
}
```

---

## 6. Memory Leak Patterns от неправильного Context

### 6.1 ЧТО: как Context вызывает утечки

```
┌──────────────────────────────────────────────────────────────────┐
│          ПОЧЕМУ УТЕЧКА CONTEXT = УТЕЧКА ВСЕГО                    │
│                                                                  │
│  Activity Context держит ссылки на:                               │
│                                                                  │
│  Activity                                                        │
│  ├── Window (PhoneWindow)                                        │
│  │   ├── DecorView                                               │
│  │   │   ├── ContentView (ваш layout)                            │
│  │   │   │   ├── TextView, Button, ImageView...                  │
│  │   │   │   │   ├── Bitmap (может быть мегабайты!)              │
│  │   │   │   │   ├── Drawable                                    │
│  │   │   │   │   └── OnClickListener → ...                       │
│  │   │   │   └── RecyclerView → Adapter → данные                 │
│  │   │   └── ActionBar, NavigationBar                            │
│  │   └── WindowManager reference                                 │
│  ├── mFragments (FragmentManager)                                │
│  │   └── Fragment instances → их Views                           │
│  ├── mMenuInflater, mActionBar                                   │
│  └── ContextImpl (base context)                                  │
│      ├── mServiceCache[] (все системные сервисы)                 │
│      ├── mResources (Resources)                                  │
│      └── mContentResolver                                        │
│                                                                  │
│  Утечка Activity Context = утечка ВСЕГО дерева выше              │
│  Типичный размер: 5-50 МБ на одну Activity!                      │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 КАК РАБОТАЕТ: 5 самых частых паттернов утечки через Context

**Паттерн 1: Singleton с Activity Context**

```kotlin
// ❌ УТЕЧКА: Singleton держит Activity Context
object Analytics {
    private lateinit var context: Context

    fun init(context: Context) {
        this.context = context // Если передать Activity → утечка!
    }

    fun trackEvent(name: String) {
        // context.packageName, context.getSharedPreferences(...)
    }
}

// В Activity:
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Analytics.init(this) // 💥 Activity утечёт!
        // При ротации: старая Activity не может быть GC'd
        // потому что Analytics (Singleton = GC Root) держит ссылку
    }
}

// ✅ ИСПРАВЛЕНИЕ:
object Analytics {
    private lateinit var context: Context

    fun init(context: Context) {
        this.context = context.applicationContext // ← безопасно!
    }
}
```

**Паттерн 2: Handler с неявной ссылкой на Activity**

```kotlin
// ❌ УТЕЧКА: анонимный inner class Handler
class LeakyActivity : AppCompatActivity() {
    // Handler — inner class → неявная ссылка на LeakyActivity
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Отложенное сообщение на 60 секунд
        handler.postDelayed({
            // this лямбда захватывает Activity Context
            updateUI()
        }, 60_000)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Если не удалить — handler держит Message → Looper → Activity
        handler.removeCallbacksAndMessages(null) // ✅ Обязательно!
    }
}

// ✅ ЛУЧШЕ: lifecycle-aware подход
class SafeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            delay(60_000)
            // Автоматически отменяется при onDestroy
            updateUI()
        }
    }
}
```

**Паттерн 3: Listener не отписан**

```kotlin
// ❌ УТЕЧКА: Activity как listener для глобального объекта
class LeakyActivity : AppCompatActivity(),
    LocationListener { // Activity реализует интерфейс

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val locationManager = getSystemService<LocationManager>()
        locationManager?.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            1000L, 0f,
            this // Activity как listener → утечка!
        )
    }

    override fun onLocationChanged(location: Location) { }

    // ❌ Забыли отписаться в onDestroy!
}

// ✅ ИСПРАВЛЕНИЕ:
class SafeActivity : AppCompatActivity() {
    private var locationManager: LocationManager? = null
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            // Обработка
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        locationManager = getSystemService<LocationManager>()
        locationManager?.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 0f,
            locationListener
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        locationManager?.removeUpdates(locationListener) // ✅ Отписка
    }
}
```

**Паттерн 4: Static reference к View (который держит Context)**

```kotlin
// ❌ УТЕЧКА: static reference к View
class LeakyActivity : AppCompatActivity() {
    companion object {
        var cachedView: View? = null // 💥 Static → GC Root!
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        cachedView = findViewById(R.id.my_view)
        // View.getContext() = Activity → утечка Activity
    }
}

// ✅ ИСПРАВЛЕНИЕ: НИКОГДА не храните View в static/companion
// Используйте ViewModel для данных, а не для View
```

**Паттерн 5: AsyncTask / GlobalScope с Context**

```kotlin
// ❌ УТЕЧКА: GlobalScope захватывает Activity Context
class LeakyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        GlobalScope.launch { // Живёт вечно!
            val data = fetchData()
            withContext(Dispatchers.Main) {
                // this@LeakyActivity захвачен лямбдой
                showData(data) // Activity может быть уже уничтожена
            }
        }
    }
}

// ✅ ИСПРАВЛЕНИЕ: lifecycle-aware scope
class SafeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch { // Отменяется при onDestroy
            val data = fetchData()
            showData(data) // Безопасно — scope привязан к lifecycle
        }
    }
}
```

### 6.3 ПОДВОДНЫЕ КАМНИ

**Compose уменьшает, но не устраняет проблему:**

```kotlin
// ❌ Compose всё ещё может утечь Context
@Composable
fun LeakyComposable() {
    val context = LocalContext.current // Activity Context

    LaunchedEffect(Unit) {
        // ✅ OK: LaunchedEffect привязан к Composition lifecycle
    }

    // ❌ ОПАСНО: передача context в долгоживущий объект
    val analytics = remember {
        Analytics(context) // Если Analytics — Singleton → утечка!
    }

    // ✅ БЕЗОПАСНО:
    val analytics2 = remember {
        Analytics(context.applicationContext) // Application Context
    }
}
```

---

## 7. Специальные случаи: BroadcastReceiver, ContentProvider, Fragment

### 7.1 BroadcastReceiver — НЕ является Context

```
┌────────────────────────────────────────────────────────────────┐
│  BroadcastReceiver ≠ Context                                   │
│                                                                │
│  class BroadcastReceiver { // НЕ extends Context!              │
│      abstract fun onReceive(context: Context, intent: Intent)  │
│  }                                                             │
│                                                                │
│  Получает Context как ПАРАМЕТР в onReceive()                   │
│                                                                │
│  Какой Context приходит?                                       │
│  • Зарегистрирован в Manifest → ReceiverRestrictedContext       │
│    (обёртка над Application ContextImpl с ограничениями)        │
│  • Зарегистрирован через registerReceiver() →                  │
│    Context того компонента, который вызвал registerReceiver()  │
│                                                                │
│  ReceiverRestrictedContext запрещает:                           │
│  • registerReceiver() — нельзя регистрировать вложенные        │
│  • bindService() — нельзя привязывать сервисы                  │
│  Но разрешает всё остальное (startService, getSharedPrefs...)  │
└────────────────────────────────────────────────────────────────┘
```

### 7.2 ContentProvider — получает Context отложенно

```kotlin
class MyProvider : ContentProvider() {

    // ⚠️ getContext() возвращает null ДО onCreate()!
    // ContentProvider.onCreate() вызывается ДО Application.onCreate()

    override fun onCreate(): Boolean {
        val ctx = context // ✅ Application Context уже доступен
        // Но Application.onCreate() ещё НЕ вызван!
        return true
    }

    override fun query(...): Cursor? {
        val ctx = requireContext() // ✅ Безопасно после onCreate()
        // ...
    }
}

// Порядок инициализации:
// 1. Application.<init>()         — конструктор
// 2. Application.attachBaseContext()  — ContextImpl привязан
// 3. ContentProvider.onCreate()   — Application Context доступен
// 4. Application.onCreate()       — только после всех ContentProviders
```

### 7.3 Fragment — использует host Activity Context

```kotlin
class MyFragment : Fragment() {

    // ⚠️ getContext() / requireContext() возвращает Activity Context
    // Он доступен только ПОСЛЕ onAttach() и ДО onDetach()

    override fun onAttach(context: Context) {
        super.onAttach(context)
        // context = Activity (host)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ✅ requireContext() = Activity Context
        val prefs = requireContext().getSharedPreferences("app", MODE_PRIVATE)

        // ✅ requireActivity() = host Activity
        val vm = ViewModelProvider(requireActivity())[SharedViewModel::class.java]
    }

    override fun onDetach() {
        super.onDetach()
        // После этого getContext() = null
        // requireContext() → IllegalStateException
    }
}
```

---

## 8. Context в Jetpack Compose

### 8.1 ЧТО: LocalContext.current

```kotlin
@Composable
fun MyScreen() {
    // LocalContext.current = Activity Context (в большинстве случаев)
    val context = LocalContext.current

    // Это Activity, если Composable вызван из:
    // setContent { ... } — Activity.setContent()
    // ComponentActivity → ContextThemeWrapper → ContextImpl

    // ✅ Можно использовать для:
    val resources = context.resources
    val packageName = context.packageName
    val toast = { Toast.makeText(context, "Hello", Toast.LENGTH_SHORT).show() }
}
```

### 8.2 КАК ПРИМЕНЯТЬ: получение правильного Context в Compose

```kotlin
@Composable
fun ContextExamples() {
    // Activity Context (с темой)
    val context = LocalContext.current

    // Application Context (для долгоживущих объектов)
    val appContext = LocalContext.current.applicationContext

    // Для получения Activity:
    val activity = LocalContext.current as? ComponentActivity

    // Для получения LifecycleOwner:
    val lifecycleOwner = LocalLifecycleOwner.current

    // ✅ Правильное использование в side effects
    val connectivityManager = remember(context) {
        context.getSystemService<ConnectivityManager>()
    }

    LaunchedEffect(Unit) {
        // ✅ context доступен из closure
        val isOnline = connectivityManager?.activeNetwork != null
    }

    // ❌ АНТИПАТТЕРН: передача context в ViewModel
    // val viewModel = viewModel<MyViewModel>(factory = MyViewModelFactory(context))
    // ✅ Используйте Hilt: val viewModel: MyViewModel = hiltViewModel()
}
```

---

## Мифы и заблуждения

| # | Миф | Реальность |
|---|-----|------------|
| 1 | "Context — это интерфейс" | Context — **абстрактный класс** с ~180 методами. В Java нет default methods в интерфейсах (до Java 8), поэтому абстрактный класс |
| 2 | "Application Context безопасен всегда" | Application Context **не может** показывать Dialog, inflate с темой, запускать Activity без FLAG_ACTIVITY_NEW_TASK. Для UI нужен Activity Context |
| 3 | "getApplicationContext() и getApplication() — одно и то же" | `getApplication()` возвращает **Application** объект (доступен только в Activity/Service). `getApplicationContext()` возвращает **Context** (доступен везде). Обычно один и тот же объект, но `getApplication()` типизирован сильнее |
| 4 | "Один Context на всё приложение" | Каждый компонент (Activity, Service, Application) получает **свой ContextImpl**. Минимум 1 + N(Activity) + N(Service) экземпляров |
| 5 | "BroadcastReceiver — это Context" | BroadcastReceiver **НЕ** наследует от Context. Получает Context как параметр в `onReceive()` |
| 6 | "View.getContext() всегда возвращает Activity" | Возвращает тот Context, который был передан при создании View. В RecyclerView с `applicationContext` — будет Application Context |
| 7 | "getSystemService() каждый раз создаёт объект" | Используется **кэширование**: `CachedServiceFetcher` хранит объект в `mServiceCache[]` per-context. Второй вызов — из кэша |
| 8 | "ContextWrapper — это тонкая обёртка" | ContextWrapper — ~170+ делегирующих методов. Это **полная** реализация паттерна Decorator, не просто обёртка |
| 9 | "Только Activity может запускать другую Activity" | Любой Context может `startActivity()`, но не-Activity Context требует `FLAG_ACTIVITY_NEW_TASK`. С Android 10+ фоновые запуски ограничены |
| 10 | "Compose не нуждается в Context" | `LocalContext.current` используется повсеместно: Resources, Toast, системные сервисы, файловые операции. Compose **строится поверх** Activity Context |

---

## CS-фундамент

| Концепция | Где проявляется | Суть |
|-----------|-----------------|------|
| **Decorator Pattern** | Context → ContextWrapper → ContextThemeWrapper | Обёртка добавляет поведение без изменения базового класса |
| **Delegation** | ContextWrapper делегирует к mBase (ContextImpl) | Все вызовы перенаправляются к реальной реализации |
| **Abstract Class** | Context — абстрактный, ContextImpl — конкретный | Контракт без реализации vs полная реализация |
| **Factory Method** | ActivityThread.createBaseContextForActivity() | Создание объекта инкапсулировано в специальном методе |
| **Service Locator** | SystemServiceRegistry + getSystemService() | Центральный реестр для получения зависимостей по ключу |
| **Caching** | CachedServiceFetcher + mServiceCache[] | Per-context кэширование для избежания повторного создания |
| **IPC (Binder)** | getSystemService → ServiceManager → system_server | Прозрачная межпроцессная коммуникация через Binder |
| **Singleton** | Application Context, StaticServiceFetcher | Один экземпляр на весь процесс |
| **Information Hiding** | ContextImpl = @hide | Скрытие реализации за публичным API |
| **Composition over Inheritance** | ContextWrapper содержит Context (mBase), а не наследует реализацию | Гибкость: можно менять base Context без изменения обёрток |

---

## Проверь себя

### Вопрос 1: Иерархия классов
**Q:** Какой путь проходит вызов `activity.getResources()` через цепочку Context?

<details>
<summary>Ответ</summary>

```
Activity (не переопределяет)
  → ContextThemeWrapper (не переопределяет getResources напрямую,
    но может вернуть Resources с override configuration)
    → ContextWrapper.getResources()
      → return mBase.getResources()
        → ContextImpl.getResources()
          → return mResources (Resources объект, связанный с AssetManager)
```

ContextThemeWrapper может переопределить `getResources()` если был вызван `applyOverrideConfiguration()` — в этом случае возвращаются Resources с изменённой Configuration (например, другая локаль).
</details>

### Вопрос 2: Количество ContextImpl
**Q:** Приложение имеет 1 Application, 3 Activity (2 сейчас в стеке), 1 Foreground Service, 2 BroadcastReceiver (зарегистрированы в Manifest). Сколько экземпляров ContextImpl существует?

<details>
<summary>Ответ</summary>

**4 экземпляра ContextImpl:**
- 1 для Application
- 2 для Activity (только те, что в стеке — третья, если уничтожена, её ContextImpl тоже GC'd)
- 1 для Foreground Service
- **0 для BroadcastReceiver** — они не создают собственный ContextImpl, а получают Context через параметр `onReceive()`

Формула: N(ContextImpl) = 1(App) + 2(живые Activity) + 1(Service) = 4
</details>

### Вопрос 3: Dialog с Application Context
**Q:** Почему `AlertDialog.Builder(applicationContext).show()` вызывает crash? Объясните на уровне WindowManager.

<details>
<summary>Ответ</summary>

Dialog вызывает `WindowManager.addView()`, которому нужен **window token** (IBinder). Activity Context имеет token, полученный от WindowManagerService при создании Activity окна. Application Context **не имеет window token** (mToken = null).

WindowManagerService проверяет token и отклоняет запрос:
```
WindowManager$BadTokenException:
  Unable to add window -- token null is not valid;
  is your activity running?
```

Решение: использовать Activity Context для показа Dialog.
</details>

### Вопрос 4: getSystemService кэширование
**Q:** Вызов `activity.getSystemService<ConnectivityManager>()` и `applicationContext.getSystemService<ConnectivityManager>()` — вернут один и тот же объект?

<details>
<summary>Ответ</summary>

**Нет** — вернут **разные объекты**. ConnectivityManager использует `CachedServiceFetcher`, который кэширует per-context в `mServiceCache[]`. Activity и Application имеют **разные** экземпляры ContextImpl с **разными** `mServiceCache` массивами.

Первый вызов на каждом Context создаст новый ConnectivityManager; второй вызов на том же Context вернёт из кэша.

Если бы использовался `StaticServiceFetcher` (как для InputMethodManager) — вернулся бы один глобальный объект.
</details>

### Вопрос 5: Memory leak
**Q:** Почему следующий код вызывает memory leak?
```kotlin
class MyViewModel : ViewModel() {
    lateinit var context: Context
    fun init(context: Context) { this.context = context }
}
// В Activity: viewModel.init(this)
```

<details>
<summary>Ответ</summary>

ViewModel **живёт дольше Activity** (переживает configuration changes). Если передать Activity Context (this), то:
1. Пользователь поворачивает экран
2. Старая Activity уничтожается (onDestroy)
3. Но ViewModel **всё ещё жив** и держит ссылку на старую Activity через `context`
4. GC не может собрать старую Activity → утечка всего View hierarchy (5-50 МБ)

Исправление:
```kotlin
class MyViewModel(application: Application) : AndroidViewModel(application) {
    // getApplication() возвращает Application Context — безопасно
    val context: Context get() = getApplication()
}
```

Или лучше: не хранить Context в ViewModel вообще. Использовать Hilt для injection зависимостей.
</details>

### Вопрос 6: attachBaseContext
**Q:** Что произойдёт если вызвать `attachBaseContext()` дважды? Почему Android это запрещает?

<details>
<summary>Ответ</summary>

Вызов `attachBaseContext()` дважды выбросит:
```
IllegalStateException: Base context already set
```

Android запрещает это потому что:
1. **Консистентность:** После привязки ContextImpl все вызовы делегируются к нему. Смена base Context на лету нарушила бы инварианты (например, кэшированные сервисы стали бы неактуальны).
2. **Безопасность:** Если бы можно было менять base Context, вредоносный код мог бы подменить ContextImpl и перехватывать вызовы (MITM на уровне Context).
3. **Порядок инициализации:** `attachBaseContext()` вызывается в `Activity.attach()`, ДО `onCreate()`. Повторный вызов означал бы ошибку в логике инициализации.

Правильный подход: если нужно обернуть Context (например, для смены локали), делайте это в `attachBaseContext()` Activity, оборачивая входящий `newBase`:
```kotlin
override fun attachBaseContext(newBase: Context) {
    val wrapped = MyWrapper(newBase) // обернуть ДО super
    super.attachBaseContext(wrapped)  // один вызов
}
```
</details>

---

## Связи

### Прямые зависимости (prerequisite)
- **[[android-activity-lifecycle]]** — Activity наследует от ContextThemeWrapper; lifecycle определяет время жизни Activity Context; `Activity.attach()` вызывает `attachBaseContext()` с ContextImpl
- **[[android-app-components]]** — Activity, Service, Application — три типа компонентов, каждый получает свой ContextImpl от ActivityThread
- **[[android-memory-leaks]]** — Context — главный источник memory leaks; неправильное хранение Activity Context в Singleton/ViewModel/static → утечка View hierarchy

### Тесно связанные темы
- **[[android-process-memory]]** — ContextImpl создаётся ActivityThread внутри процесса приложения; число Context-ов влияет на потребление памяти
- **[[android-handler-looper]]** — ActivityThread.mH (Handler) управляет созданием Context-ов через сообщения LAUNCH_ACTIVITY, CREATE_SERVICE
- **[[android-view-rendering-pipeline]]** — LayoutInflater получается через Context.getSystemService(); тема применяется через ContextThemeWrapper
- **[[android-dependency-injection]]** — Hilt предоставляет @ApplicationContext и @ActivityContext для правильного scope; решает проблему передачи Context

### Дополнительный контекст
- **[[android-bundle-parcelable]]** — savedInstanceState работает через Context (Activity); Bundle передаётся через Binder, к которому Context обеспечивает доступ
- **[[android-state-management]]** — SavedStateHandle, ViewModel, SharedPreferences — все требуют Context для работы
- **[[android-navigation]]** — NavController использует Activity Context для запуска новых Activity/Fragment через Intent/FragmentManager

---

## Источники

| # | Источник | Тип | Описание |
|---|---------|-----|----------|
| 1 | [AOSP: ContextImpl.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/app/ContextImpl.java) | AOSP | Исходный код ContextImpl (~4500 строк) |
| 2 | [AOSP: ActivityThread.java](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/app/ActivityThread.java) | AOSP | Создание Context для каждого компонента |
| 3 | [AOSP: Context.java](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/content/Context.java) | AOSP | Абстрактный класс Context (~180 методов) |
| 4 | [Android Context — Part 2: The Android Internals Deep Dive](https://proandroiddev.com/android-context-part-2-the-android-internals-deep-dive-8a401985579c) | Article | Ioannis Anifantakis, ProAndroidDev (2025) — глубокий разбор Decorator pattern и ContextImpl |
| 5 | [Using the Android Context and Manifest to unveil the Android System Internals (2025 Edition)](https://proandroiddev.com/using-the-android-context-and-manifest-to-unveil-the-android-system-internals-2025-edition-eb730dd95f1d) | Article | Ioannis Anifantakis, ProAndroidDev (2025) — Context и Manifest как окно в Android internals |
| 6 | [Fully understand Context in Android](https://ericyang505.github.io/android/Context.html) | Article | Eric Yang — полный разбор иерархии и количества Context-ов |
| 7 | [Context in Android development](https://karatos.com/art?id=80afc113-935e-4418-ae6d-4a8da5c95c8a) | Article | Karatos — createBaseContextForActivity и setOuterContext |
| 8 | [RTFSC: context-getSystemService](https://github.com/RTFSC-Android/RTFSC/blob/master/context-getsystemservice.md) | Article | Подробный разбор SystemServiceRegistry и ServiceFetcher |
| 9 | [How Android apps get handles to system services](https://xizzhu.me/post/2020-05-14-android-getsystemservice/) | Article | xizzhu — CachedServiceFetcher и mServiceCache flow |
| 10 | [getSystemService — from Context to Android system](https://blog.propaneapps.com/android/getsystemservice-from-context-to-android/) | Article | Michał Łuszczuk — per-context caching behaviour |
| 11 | [Context API reference](https://developer.android.com/reference/android/content/Context) | Docs | Официальная документация Android Context |
| 12 | [ContextWrapper API reference](https://developer.android.com/reference/android/content/ContextWrapper) | Docs | Официальная документация ContextWrapper |
| 13 | [Application Context, Activity Context and Memory leaks](https://shashankmistry30.medium.com/application-context-activity-context-and-memory-leaks-7e1461ab1d9a) | Article | Shashank Mistry — таблица операций и memory leak patterns |
| 14 | [Android Developers Blog: Avoiding memory leaks](https://android-developers.googleblog.com/2009/01/avoiding-memory-leaks.html) | Blog | Romain Guy (2009) — оригинальный пост Google о Context leaks |
| 15 | [Activity Context vs Application Context: A Deep Dive](https://medium.com/@mahmoud.alkateb22/activity-context-vs-application-context-a-deep-dive-into-android-development-94fc41233de7) | Article | Mahmoud Alkateb — сравнение двух типов Context |
| 16 | [Context and memory leaks in Android](https://medium.com/swlh/context-and-memory-leaks-in-android-82a39ed33002) | Article | Juan Rinconada — утечки через Context и как их предотвратить |

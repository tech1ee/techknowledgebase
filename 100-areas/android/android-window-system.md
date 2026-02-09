---
title: "Window System: PhoneWindow, DecorView, WindowManager и Surface"
created: 2026-01-27
modified: 2026-01-29
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/internals
  - type/deep-dive
  - level/expert
related:
  - "[[android-overview]]"
  - "[[android-view-rendering-pipeline]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-touch-handling]]"
  - "[[android-compose]]"
  - "[[android-context-internals]]"
cs-foundations: [decorator-pattern, bridge-pattern, ipc, compositor, double-buffering]
---

# Window System: PhoneWindow, DecorView, WindowManager и Surface

> Каждый пиксель на экране Android принадлежит какому-то окну (Window). Activity, Dialog, Toast, клавиатура, статус-бар — все это окна, управляемые WindowManagerService в system_server и отображаемые через SurfaceFlinger. Window System — это многоуровневая архитектура: приложение работает с абстрактным Window API, ViewRootImpl транслирует это в Binder IPC к WMS, а SurfaceFlinger композитит все Surface в финальное изображение синхронно с VSYNC. Понимание этой системы критично для edge-to-edge дизайна, правильной работы с insets и диагностики rendering issues.

---

## Зачем это нужно

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| UI залезает под статус-бар | Не обработаны insets | Текст перекрыт, не читаем |
| Dialog crash: BadTokenException | Использован Application Context | Crash при показе |
| Клавиатура перекрывает поле ввода | Не обработан IME inset | Пользователь не видит что вводит |
| Display cutout обрезает контент | Не настроен layoutInDisplayCutoutMode | Потеря важного контента |
| UI ломается на Android 15 | Edge-to-edge стал обязательным | Визуальные регрессии |
| Jank при скролле | Неоптимальная работа с Surface | Пропуск кадров, дёрганье |
| Overlay не показывается | Нет SYSTEM_ALERT_WINDOW permission | Функция не работает |
| Gesture navigation конфликтует | Не учтены systemGestures insets | Back gesture не работает |
| Activity не получает touch events | Неправильный window flag | Приложение не отзывается |
| Memory leak от Window | Dialog/PopupWindow не dismissed | OutOfMemoryError |

### Актуальность (2024-2025)

```
Timeline эволюции Window System:
───────────────────────────────────────────────────────────────────

Android 1.0       ── Window Manager Service, SurfaceFlinger (Cairo)
        │
Android 3.0 (11)  ── Hardware acceleration, RenderThread preview
        │
Android 4.0 (14)  ── Project Butter: VSYNC, triple buffering
        │
Android 4.4 (19)  ── Immersive mode (hide system bars)
        │
Android 5.0 (21)  ── Material Design, elevation, RenderThread
        │
Android 8.0 (26)  ── Autofill windows, PiP (TYPE_APPLICATION_OVERLAY)
        │
Android 9.0 (28)  ── Display cutout API
        │
Android 10 (29)   ── Gesture navigation, Bubbles
        │
Android 11 (30)   ── WindowMetrics API, WindowInsetsController
        │
Android 12 (31)   ── Splash Screen API (Starting Window), Material You
        │                    └─ SplashScreen становится обязательным окном
        │
Android 13 (33)   ── Per-app language (window recreation)
        │
Android 14 (34)   ── Predictive back gesture animations
        │
Android 15 (35)   ── EDGE-TO-EDGE ОБЯЗАТЕЛЬНО
                     ├─ Системные бары прозрачные
                     ├─ layoutInDisplayCutoutMode = ALWAYS
                     └─ Приложение рисует под system bars
```

**Ключевые изменения:**

- **Android 15:** Edge-to-edge **обязательно** для targetSdk 35. Без обработки insets — сломанный UI
- **Android 11+:** WindowInsetsController заменяет deprecated systemUiVisibility
- **Gesture Navigation:** 70%+ пользователей используют gesture nav — нужно учитывать systemGestures insets
- **Foldables/Large screens:** WindowMetrics API для правильного определения размеров

---

## Prerequisites

| Тема | Зачем | Где изучить |
|------|-------|-------------|
| View rendering | Window содержит View hierarchy, рендеринг через Surface | [[android-view-rendering-pipeline]] |
| Activity lifecycle | Window создаётся при attach Activity, виден после makeVisible | [[android-activity-lifecycle]] |
| Context | Window привязано к Context (token), разные контексты = разные возможности | [[android-context-internals]] |
| Binder IPC | Все операции с WMS через Binder calls | [[android-binder-ipc]] |
| Handler/Looper | Choreographer, VSYNC callbacks, message queue | [[android-handler-looper]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Window** | Абстрактный класс — контейнер для View hierarchy | Рамка для картины |
| **PhoneWindow** | Единственная реализация Window в Android | Конкретная рамка с паспарту |
| **DecorView** | Корневой FrameLayout, содержит system chrome + content | Паспарту с окошком для картины |
| **ContentParent** | FrameLayout внутри DecorView для пользовательского контента | Окошко в паспарту для картины |
| **ViewRootImpl** | Мост между View деревом и WindowManagerService | Курьер между художником и галереей |
| **Surface** | Буфер в RAM/GPU для рисования (producer side) | Холст художника |
| **SurfaceControl** | Handle для управления Surface в SurfaceFlinger | Паспорт холста |
| **BufferQueue** | Очередь буферов между producer и consumer | Конвейер готовых холстов |
| **SurfaceFlinger** | Системный композитор, собирает все Surface | Проекционист в кинотеатре |
| **WindowManagerService (WMS)** | Системный сервис управления окнами в system_server | Администратор галереи |
| **WindowState** | Запись об окне внутри WMS | Учётная карточка в архиве |
| **IWindowSession** | Binder interface: app ↔ WMS (per-process) | Канал связи с администратором |
| **IWindow** | Callback interface: WMS → app | Обратный канал для уведомлений |
| **Insets** | Области экрана, занятые системным UI | Поля страницы |
| **DisplayCutout** | Вырез камеры/сенсоров в экране | Отверстие в рамке |
| **Edge-to-Edge** | Режим когда app рисует под системными барами | Картина во всю стену |
| **WindowToken** | IBinder идентификатор окна/группы окон | Пропуск в галерею |
| **Z-order** | Порядок наложения окон (ближе/дальше) | Слои картин друг над другом |

---

## Архитектура Window System

### Общая диаграмма

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            APPLICATION PROCESS                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Activity                                                         │   │
│  │  ┌─────────────┐                                                  │   │
│  │  │ PhoneWindow │ ─── Window (abstract)                           │   │
│  │  │  ┌────────────────────────────────────────────────────────┐   │   │
│  │  │  │ DecorView (FrameLayout)                                 │   │   │
│  │  │  │  ┌──────────────────────────────────────────────────┐  │   │   │
│  │  │  │  │ LinearLayout (screen_simple.xml)                  │  │   │   │
│  │  │  │  │  ┌────────────────────────────────────────────┐  │  │   │   │
│  │  │  │  │  │ @android:id/content (FrameLayout)          │  │  │   │   │
│  │  │  │  │  │  ┌──────────────────────────────────────┐ │  │  │   │   │
│  │  │  │  │  │  │ YOUR LAYOUT (setContentView)         │ │  │  │   │   │
│  │  │  │  │  │  │  ├── TextView                        │ │  │  │   │   │
│  │  │  │  │  │  │  ├── Button                          │ │  │  │   │   │
│  │  │  │  │  │  │  └── RecyclerView                    │ │  │  │   │   │
│  │  │  │  │  │  └──────────────────────────────────────┘ │  │  │   │   │
│  │  │  │  │  └────────────────────────────────────────────┘  │  │   │   │
│  │  │  │  └──────────────────────────────────────────────────┘  │   │   │
│  │  │  └────────────────────────────────────────────────────────┘   │   │
│  │  └─────────────┘                                                  │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                              │                                            │
│                              ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  WindowManagerGlobal (Singleton per process)                      │   │
│  │  ├── mViews: ArrayList<View>         // all DecorViews            │   │
│  │  ├── mRoots: ArrayList<ViewRootImpl> // all ViewRootImpls         │   │
│  │  └── mParams: ArrayList<LayoutParams>// all LayoutParams          │   │
│  │                           │                                        │   │
│  │                           ▼                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐   │   │
│  │  │  ViewRootImpl                                               │   │   │
│  │  │  ├── mView: DecorView (root of View tree)                  │   │   │
│  │  │  ├── mSurface: Surface (drawing target)                    │   │   │
│  │  │  ├── mChoreographer: Choreographer (VSYNC)                 │   │   │
│  │  │  ├── mWindowSession: IWindowSession (Binder to WMS)        │   │   │
│  │  │  └── mWindow: W extends IWindow.Stub (callback from WMS)   │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                              │                                            │
│                              │ Binder IPC                                 │
│                              ▼                                            │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │
┌─────────────────────────────────────────────────────────────────────────┐
│                            SYSTEM_SERVER PROCESS                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  WindowManagerService                                             │   │
│  │  ├── mWindowMap: HashMap<IBinder, WindowState>                   │   │
│  │  ├── mRoot: RootWindowContainer                                  │   │
│  │  │   └── DisplayContent[] (per display)                          │   │
│  │  │       └── WindowState[] (all windows on display)              │   │
│  │  ├── mInputManager: InputManagerService                          │   │
│  │  └── mAnimator: WindowAnimator                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                            │
│                              │ Binder IPC                                 │
│                              ▼                                            │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │
┌─────────────────────────────────────────────────────────────────────────┐
│                         SURFACEFLINGER PROCESS                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  SurfaceFlinger (native daemon)                                   │   │
│  │  ├── Layer[] (one per Surface)                                   │   │
│  │  ├── HWComposer (Hardware Composer HAL)                          │   │
│  │  └── Composes all layers → Display                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                         ┌───────────┐
                         │  DISPLAY  │
                         └───────────┘
```

---

## Activity → PhoneWindow → DecorView → ContentView

### Полный путь setContentView

```
Activity.setContentView(R.layout.activity_main)
  │
  │ // Activity.java
  ├─→ getWindow().setContentView(layoutResID)
  │     │
  │     │ // PhoneWindow.java
  │     ├─→ if (mContentParent == null) {
  │     │       installDecor()  // создать DecorView если ещё нет
  │     │   }
  │     │
  │     ├─→ installDecor():
  │     │     │
  │     │     ├─→ if (mDecor == null) {
  │     │     │       mDecor = generateDecor(-1)
  │     │     │       // new DecorView(context, featureId, this, getAttributes())
  │     │     │   }
  │     │     │
  │     │     └─→ if (mContentParent == null) {
  │     │             mContentParent = generateLayout(mDecor)
  │     │             │
  │     │             ├─→ // 1. Прочитать window features из темы
  │     │             │   TypedArray a = getWindowStyle()
  │     │             │   // windowNoTitle, windowActionBar, windowFullscreen...
  │     │             │
  │     │             ├─→ // 2. Выбрать layout для DecorView
  │     │             │   int layoutResource;
  │     │             │   if (features == FEATURE_NO_TITLE) {
  │     │             │       layoutResource = R.layout.screen_simple
  │     │             │   } else if (features == FEATURE_ACTION_BAR) {
  │     │             │       layoutResource = R.layout.screen_action_bar
  │     │             │   } // ... много вариантов
  │     │             │
  │     │             ├─→ // 3. Inflate layout в DecorView
  │     │             │   mDecor.onResourcesLoaded(inflater, layoutResource)
  │     │             │   // LinearLayout с ActionBarContainer и content FrameLayout
  │     │             │
  │     │             └─→ // 4. Найти content parent
  │     │                 ViewGroup contentParent = findViewById(ID_ANDROID_CONTENT)
  │     │                 // ID_ANDROID_CONTENT = com.android.internal.R.id.content
  │     │                 return contentParent
  │     │         }
  │     │
  │     └─→ // 5. Inflate ваш layout в content parent
  │         mLayoutInflater.inflate(layoutResID, mContentParent)
  │         // Ваш activity_main.xml становится child of mContentParent
  │
  │ // ... позже, в ActivityThread.handleResumeActivity()
  └─→ Activity.makeVisible()
        │
        └─→ WindowManager wm = getWindowManager()
            wm.addView(mDecor, getWindow().getAttributes())
            │
            │ // WindowManagerImpl.java
            └─→ mGlobal.addView(view, params, display, parentWindow, userId)
                  │
                  │ // WindowManagerGlobal.java
                  ├─→ ViewRootImpl root = new ViewRootImpl(context, display)
                  ├─→ mViews.add(view)      // track DecorView
                  ├─→ mRoots.add(root)      // track ViewRootImpl
                  ├─→ mParams.add(params)   // track LayoutParams
                  │
                  └─→ root.setView(view, params, panelParentView, userId)
                        │
                        │ // ViewRootImpl.java
                        ├─→ mView = view  // DecorView
                        ├─→ requestLayout()
                        │     └─→ scheduleTraversals()
                        │           └─→ mChoreographer.postCallback(TRAVERSAL, ...)
                        │
                        └─→ mWindowSession.addToDisplayAsUser(mWindow, ...)
                              // Binder IPC → WMS
                              // WMS создаёт WindowState
                              // WMS выделяет Surface
```

### Иерархия View с разными темами

```
═══════════════════════════════════════════════════════════════════════════
ТЕМА БЕЗ ACTION BAR (Theme.Material3.DayNight.NoActionBar):
═══════════════════════════════════════════════════════════════════════════

DecorView (FrameLayout)
├── LinearLayout (orientation=vertical)
│   └── FrameLayout (@android:id/content)
│       └── [ВАШ LAYOUT]
└── View (navigationBarBackground) — если edge-to-edge


═══════════════════════════════════════════════════════════════════════════
ТЕМА С ACTION BAR (Theme.Material3.DayNight):
═══════════════════════════════════════════════════════════════════════════

DecorView (FrameLayout)
├── LinearLayout (orientation=vertical)
│   ├── ViewStub (@android:id/action_mode_bar_stub)
│   ├── FrameLayout (ActionBarOverlayLayout)
│   │   ├── ContentFrameLayout (@android:id/content)
│   │   │   └── [ВАШ LAYOUT]
│   │   └── ActionBarContainer (@android:id/action_bar_container)
│   │       └── Toolbar / ActionBarView
│   └── (optional) NavigationBarBackground
└── View (statusBarBackground) — если edge-to-edge


═══════════════════════════════════════════════════════════════════════════
COMPOSE ACTIVITY (ComponentActivity + setContent):
═══════════════════════════════════════════════════════════════════════════

DecorView (FrameLayout)
├── LinearLayout
│   └── FrameLayout (@android:id/content)
│       └── ComposeView
│           └── AndroidComposeView
│               └── [Compose UI tree - LayoutNodes]
└── View (navigationBarBackground)
```

### Код: навигация по View hierarchy

```kotlin
class DebugActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // После setContentView можно исследовать иерархию
        window.decorView.post {
            printViewHierarchy()
        }
    }

    private fun printViewHierarchy() {
        // 1. Получить DecorView
        val decorView = window.decorView
        Log.d("Window", "DecorView: $decorView")
        Log.d("Window", "DecorView parent: ${decorView.parent}")
        // parent = ViewRootImpl (не View!)

        // 2. Получить content container
        val contentParent = findViewById<ViewGroup>(android.R.id.content)
        Log.d("Window", "Content parent: $contentParent")
        Log.d("Window", "Content children: ${contentParent.childCount}")

        // 3. Получить ваш корневой View
        val myRootView = contentParent.getChildAt(0)
        Log.d("Window", "My root view: $myRootView")

        // 4. Traverse всё дерево
        fun traverse(view: View, depth: Int = 0) {
            val indent = "  ".repeat(depth)
            val id = try {
                resources.getResourceEntryName(view.id)
            } catch (e: Exception) {
                "no-id"
            }
            Log.d("Window", "$indent${view.javaClass.simpleName} (id=$id)")
            if (view is ViewGroup) {
                for (i in 0 until view.childCount) {
                    traverse(view.getChildAt(i), depth + 1)
                }
            }
        }
        traverse(decorView)
    }
}
```

---

## WindowManager и WindowManagerService

### Клиентская сторона — три уровня

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WindowManager (interface)                                               │
│  ├── addView(View, LayoutParams)                                        │
│  ├── updateViewLayout(View, LayoutParams)                               │
│  └── removeView(View)                                                   │
│                                                                          │
│  Наследует от ViewManager                                                │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  WindowManagerImpl (per-Context implementation)                          │
│  ├── mContext: Context (Activity, Application, etc.)                    │
│  ├── mParentWindow: Window? (для sub-windows)                           │
│  │                                                                       │
│  │  Делегирует ВСЁ в WindowManagerGlobal:                               │
│  │  fun addView(view, params) {                                          │
│  │      mGlobal.addView(view, params, mContext.display,                  │
│  │                      mParentWindow, mContext.userId)                  │
│  │  }                                                                    │
│  └───────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  WindowManagerGlobal (SINGLETON per process)                             │
│  ├── sDefaultWindowManager: WindowManagerGlobal (static)                │
│  │                                                                       │
│  │  Хранит ВСЕ окна процесса:                                           │
│  ├── mViews: ArrayList<View>           // все DecorView / root views    │
│  ├── mRoots: ArrayList<ViewRootImpl>   // соответствующие ViewRootImpl  │
│  ├── mParams: ArrayList<LayoutParams>  // параметры каждого окна        │
│  ├── mDyingViews: ArraySet<View>       // окна в процессе удаления      │
│  │                                                                       │
│  │  addView():                                                           │
│  │  1. Проверки (не дубликат, валидные params)                          │
│  │  2. new ViewRootImpl(context, display)                               │
│  │  3. mViews.add(view), mRoots.add(root), mParams.add(params)          │
│  │  4. root.setView(view, params, ...) → Binder IPC → WMS               │
│  │                                                                       │
│  │  removeView():                                                        │
│  │  1. Найти индекс в mViews                                            │
│  │  2. root.die(immediate) → отложенное удаление через Handler          │
│  │  3. root отправляет MSG_DIE, вызывает doDie()                        │
│  │  4. mWindowSession.remove(mWindow) → Binder IPC → WMS                │
│  │  5. Очистка mViews, mRoots, mParams                                  │
│  └───────────────────────────────────────────────────────────────────────┘
```

### Серверная сторона — WindowManagerService

```
WindowManagerService (system_server process)
│
├── Основные структуры данных:
│   ├── mRoot: RootWindowContainer
│   │   └── DisplayContent[] — по одному на каждый дисплей
│   │       └── DisplayArea hierarchy
│   │           └── WindowState[] — все окна на дисплее
│   │
│   ├── mWindowMap: HashMap<IBinder, WindowState>
│   │   // Быстрый поиск окна по его IBinder token
│   │
│   └── mSessions: ArraySet<Session>
│       // По одной Session на каждый клиентский процесс
│       // Session implements IWindowSession
│
├── Жизненный цикл окна в WMS:
│   │
│   │  Session.addToDisplay() [Binder call from ViewRootImpl]
│   │      │
│   │      ▼
│   │  WMS.addWindow()
│   │      ├── Валидация token
│   │      ├── Проверка permissions (для system windows)
│   │      ├── new WindowState(...)
│   │      ├── mWindowMap.put(client.asBinder(), win)
│   │      ├── win.attach() — создание SurfaceSession
│   │      ├── Определение z-order
│   │      └── Trigger layout pass
│   │
│   │  Session.relayout() [Binder call для получения Surface]
│   │      │
│   │      ▼
│   │  WMS.relayoutWindow()
│   │      ├── Обновить размеры окна
│   │      ├── Создать/обновить Surface через SurfaceControl
│   │      ├── Вернуть Surface клиенту
│   │      └── Вычислить insets
│   │
│   │  Session.remove() [Binder call при removeView]
│   │      │
│   │      ▼
│   │  WMS.removeWindow()
│   │      ├── win.removeIfPossible()
│   │      ├── Очистка mWindowMap
│   │      ├── Освобождение Surface
│   │      └── Trigger layout pass
│
├── Input Management:
│   ├── mInputManager: InputManagerService
│   │   // WMS определяет какое окно получает input
│   │   // На основе: z-order, focus, touchable regions
│   └── Распределение touch/key events по окнам
│
├── Animation:
│   ├── mAnimator: WindowAnimator
│   │   // Window transitions
│   │   // App launch animations
│   │   // Rotation animations
│   └── SurfaceAnimator для каждого WindowState
│
└── Policy:
    └── mPolicy: WindowManagerPolicy (PhoneWindowManager)
        // Навигационные кнопки
        // System UI visibility
        // Lock screen
        // Orientation
```

### IPC между клиентом и WMS

```
App Process                              system_server
┌──────────────────┐                    ┌──────────────────────┐
│  ViewRootImpl    │                    │  WindowManagerService │
│                  │                    │                       │
│  ┌────────────┐  │  addToDisplay()   │  ┌─────────────────┐  │
│  │IWindowSess.│──────────────────────→  │  Session        │  │
│  │  mSession  │  │  relayout()       │  │  (per-process)  │  │
│  │            │  │  remove()         │  │                 │  │
│  │            │  │  finishDrawing()  │  │                 │  │
│  └────────────┘  │                    │  └─────────────────┘  │
│                  │                    │                       │
│  ┌────────────┐  │  resized()        │                       │
│  │ W (IWindow)│←─────────────────────────── callbacks ────── │
│  │  callback  │  │  moved()          │                       │
│  │            │  │  dispatchAppVis() │                       │
│  │            │  │  insetsChanged()  │                       │
│  └────────────┘  │                    │                       │
└──────────────────┘                    └──────────────────────┘

Основные Binder вызовы:

App → WMS:
  • addToDisplay() — добавить окно
  • relayout() — пересчитать размеры, получить Surface
  • remove() — удалить окно
  • finishDrawing() — сообщить что нарисовали первый кадр
  • setInsets() — установить insets для IME
  • performHapticFeedback() — вибрация

WMS → App (через IWindow callback):
  • resized() — размер окна изменился
  • moved() — позиция изменилась
  • windowFocusChanged() — фокус изменился
  • insetsChanged() — insets изменились
  • dispatchAppVisibility() — visibility изменился
```

---

## ViewRootImpl — сердце Window

### Ключевые факты о ViewRootImpl

```
ViewRootImpl — НЕ View, а ViewParent!

                    ViewParent (interface)
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ViewGroup          ViewRootImpl    (other impls)
   (is View)        (NOT a View!)

decorView.getParent() → ViewRootImpl
viewRootImpl.getParent() → null (root of hierarchy)

Почему это важно:
1. requestLayout() поднимается вверх по parent chain до ViewRootImpl
2. invalidate() поднимается вверх до ViewRootImpl
3. ViewRootImpl — единственный кто знает о Surface и WMS
4. ViewRootImpl содержит Choreographer для VSYNC
```

### Основные поля ViewRootImpl

```kotlin
// ViewRootImpl.java (упрощённо, ~15,000 строк в AOSP)
class ViewRootImpl : ViewParent, AttachInfo.Callbacks {

    // ═══ View tree ═══
    var mView: View                    // DecorView (root of tree)
    var mAttachInfo: AttachInfo       // Shared info for all views in tree
    var mLayoutRequested: Boolean     // Needs layout pass?
    var mFirst: Boolean = true        // First traversal?

    // ═══ WMS connection ═══
    val mWindowSession: IWindowSession  // Binder proxy to WMS (per-process)
    val mWindow: W                      // IWindow.Stub callback for WMS
    var mWindowAttributes: LayoutParams // Current window attributes
    var mAdded: Boolean = false         // Added to WMS?
    var mStopped: Boolean = false       // Activity stopped?

    // ═══ Surface ═══
    val mSurface: Surface = Surface()   // Drawing target
    var mSurfaceControl: SurfaceControl // Handle for SurfaceFlinger
    val mBlastBufferQueue: BLASTBufferQueue? // Android 11+ buffer queue

    // ═══ Rendering ═══
    val mChoreographer: Choreographer   // VSYNC coordination
    var mTraversalRunnable: Runnable    // performTraversals callback
    var mTraversalScheduled: Boolean    // Traversal already scheduled?
    val mThreadedRenderer: ThreadedRenderer? // Hardware acceleration

    // ═══ Input ═══
    var mInputEventReceiver: InputEventReceiver?
    var mInputChannel: InputChannel?    // For receiving input events

    // ═══ Insets ═══
    val mInsetsController: InsetsController
    var mLastWindowInsets: WindowInsets?

    // ═══ Measurements ═══
    var mWidth: Int = -1               // Current width
    var mHeight: Int = -1              // Current height
    val mWinFrame: Rect = Rect()       // Window frame from WMS
    val mPendingInsets: Rect = Rect()  // Pending insets from WMS

    // ═══ Dirty region ═══
    val mDirty: Rect = Rect()          // Area to redraw
    var mIsAnimating: Boolean = false
}
```

### scheduleTraversals() и Choreographer

```
Что запускает traversal:
─────────────────────────

View.invalidate()
  → ViewGroup.invalidateChild()
    → ... up parent chain ...
      → ViewRootImpl.invalidateChildInParent()
        → scheduleTraversals()

View.requestLayout()
  → ViewGroup.requestLayout()
    → ... up parent chain ...
      → ViewRootImpl.requestLayout()
        → scheduleTraversals()

WindowManager.updateViewLayout()
  → ViewRootImpl.setLayoutParams()
    → scheduleTraversals()

WMS callback: resized(), insetsChanged()
  → requestLayout()
    → scheduleTraversals()


Как работает scheduleTraversals():
──────────────────────────────────

scheduleTraversals():
│
├── if (!mTraversalScheduled) {
│       mTraversalScheduled = true
│
├──     // Barrier предотвращает обработку sync messages
│       mTraversalBarrier = mHandler.postSyncBarrier()
│
└──     // Регистрируем callback на следующий VSYNC
        mChoreographer.postCallback(
            Choreographer.CALLBACK_TRAVERSAL,
            mTraversalRunnable,  // → doTraversal()
            null
        )
    }

... VSYNC arrives ...

Choreographer.doFrame():
│
├── doCallbacks(CALLBACK_INPUT, ...)
├── doCallbacks(CALLBACK_ANIMATION, ...)
├── doCallbacks(CALLBACK_INSETS_ANIMATION, ...)
├── doCallbacks(CALLBACK_TRAVERSAL, ...)  // ← наш callback
│       │
│       └── mTraversalRunnable.run()
│               │
│               └── doTraversal()
│                       │
│                       ├── mTraversalScheduled = false
│                       ├── mHandler.removeSyncBarrier(mTraversalBarrier)
│                       └── performTraversals()  // THE MAIN WORK
│
└── doCallbacks(CALLBACK_COMMIT, ...)
```

### performTraversals() — детальный разбор

```
performTraversals() — ~1200 строк в AOSP!
────────────────────────────────────────

performTraversals():
│
├── // ═══ PHASE 1: Pre-measure setup ═══
│   │
│   ├── Обработать pending configuration changes
│   ├── Обновить mAttachInfo.mWindowVisibility
│   ├── Проверить display state
│   │
│   └── if (mFirst || windowShouldResize || ...) {
│           // Нужно relayout с WMS
│           relayoutResult = relayoutWindow(params, ...)
│           │
│           └── mWindowSession.relayout(...)
│               // Binder IPC → WMS
│               // Получаем: new frame, insets, Surface
│       }
│
├── // ═══ PHASE 2: Measure ═══
│   │
│   ├── Вычислить desiredWindowWidth/Height
│   │   // На основе: WindowManager.LayoutParams
│   │   // MATCH_PARENT → размер экрана (минус insets если нужно)
│   │   // WRAP_CONTENT → measure с AT_MOST
│   │
│   ├── if (mLayoutRequested) {
│   │       int childWidthMeasureSpec = getRootMeasureSpec(
│   │           desiredWindowWidth, lp.width)
│   │       int childHeightMeasureSpec = getRootMeasureSpec(
│   │           desiredWindowHeight, lp.height)
│   │
│   │       performMeasure(childWidthMeasureSpec, childHeightMeasureSpec)
│   │       │
│   │       └── mView.measure(widthSpec, heightSpec)
│   │           // Рекурсивно измеряет всё дерево
│   │   }
│   │
│   └── if (measureAgain) {
│           // Иногда нужен второй проход measure
│           performMeasure(...)
│       }
│
├── // ═══ PHASE 3: Layout ═══
│   │
│   ├── if (didLayout) {
│   │       performLayout(lp, desiredWindowWidth, desiredWindowHeight)
│   │       │
│   │       └── mView.layout(0, 0, mView.measuredWidth, mView.measuredHeight)
│   │           // Рекурсивно позиционирует всё дерево
│   │   }
│   │
│   └── Обработать layout listeners
│
├── // ═══ PHASE 4: Update window ═══
│   │
│   ├── if (surfaceChanged) {
│   │       notifySurfaceCreated() / notifySurfaceDestroyed()
│   │   }
│   │
│   └── Report drawn state to WMS if needed
│       mWindowSession.finishDrawing(...)
│
└── // ═══ PHASE 5: Draw ═══
    │
    ├── if (cancelDraw) {
    │       scheduleTraversals() // try again
    │       return
    │   }
    │
    └── if (!dirty.isEmpty() || mIsAnimating) {
            performDraw()
            │
            ├── if (mAttachInfo.mThreadedRenderer != null) {
            │       // Hardware accelerated path
            │       mAttachInfo.mThreadedRenderer.draw(mView, ...)
            │   } else {
            │       // Software path
            │       drawSoftware(surface, ...)
            │       │
            │       └── canvas = mSurface.lockCanvas(dirty)
            │           mView.draw(canvas)
            │           mSurface.unlockCanvasAndPost(canvas)
            │   }
            │
            └── reportDrawFinished()
        }
```

---

## Типы окон (Window Types)

### Полная классификация

```
Z-order (от заднего к переднему):
══════════════════════════════════════════════════════════════════════════

  WALLPAPER WINDOWS
  ─────────────────────────────────────────────────────────────────────────
    TYPE_WALLPAPER = 2013
      Обои рабочего стола

  APPLICATION WINDOWS (1-99)
  ─────────────────────────────────────────────────────────────────────────
    TYPE_BASE_APPLICATION = 1
      Базовое окно приложения (обычно первое окно)

    TYPE_APPLICATION = 2
      Стандартное окно приложения (Activity)

    TYPE_APPLICATION_STARTING = 3
      Starting window (splash screen до onCreate)
      Создаётся системой, показывает windowBackground из темы

    TYPE_DRAWN_APPLICATION = 4
      Starting window с custom content

    TYPE_APPLICATION_PANEL = 1000    // SUB-WINDOW!
    TYPE_APPLICATION_MEDIA = 1001
    TYPE_APPLICATION_SUB_PANEL = 1002
    TYPE_APPLICATION_ATTACHED_DIALOG = 1003

  SUB-WINDOWS (1000-1999)
  ─────────────────────────────────────────────────────────────────────────
    Окна, привязанные к родительскому окну (нужен parent token)

    TYPE_APPLICATION_PANEL = 1000
      PopupMenu, Spinner dropdown

    TYPE_APPLICATION_MEDIA = 1001
      SurfaceView media content

    TYPE_APPLICATION_SUB_PANEL = 1002
      Sub-panel поверх panel

    TYPE_APPLICATION_ATTACHED_DIALOG = 1003
      Dialog, привязанный к Activity

    TYPE_APPLICATION_MEDIA_OVERLAY = 1004
      Overlay поверх media

    TYPE_APPLICATION_ABOVE_SUB_PANEL = 1005
      Выше sub-panel (Android 6+)

  SYSTEM WINDOWS (2000+)
  ─────────────────────────────────────────────────────────────────────────
    Требуют специальных permissions (кроме некоторых)

    TYPE_STATUS_BAR = 2000
      Статус-бар (только SystemUI)

    TYPE_SEARCH_BAR = 2001
      Поисковая строка

    TYPE_PHONE = 2002
      Incoming call UI

    TYPE_SYSTEM_ALERT = 2003 (DEPRECATED!)
      Системные алерты — deprecated в Android 8+

    TYPE_KEYGUARD = 2004
      Lock screen

    TYPE_TOAST = 2005
      Toast уведомления (НЕ требует permission!)

    TYPE_SYSTEM_OVERLAY = 2006 (DEPRECATED!)
      System overlay — deprecated

    TYPE_PRIORITY_PHONE = 2007
      Priority phone UI

    TYPE_SYSTEM_DIALOG = 2008
      System dialogs

    TYPE_KEYGUARD_DIALOG = 2009
      Dialogs поверх keyguard

    TYPE_SYSTEM_ERROR = 2010
      System error dialogs

    TYPE_INPUT_METHOD = 2011
      Клавиатура (IME)

    TYPE_INPUT_METHOD_DIALOG = 2012
      IME dialogs

    TYPE_WALLPAPER = 2013
      Обои

    TYPE_STATUS_BAR_PANEL = 2014
      Panel под статус-баром (deprecated)

    TYPE_SECURE_SYSTEM_OVERLAY = 2015
      Secure overlay

    TYPE_DRAG = 2016
      Drag & drop surface

    TYPE_STATUS_BAR_SUB_PANEL = 2017
      Sub-panel статус-бара

    TYPE_POINTER = 2018
      Pointer cursor

    TYPE_NAVIGATION_BAR = 2019
      Navigation bar

    TYPE_VOLUME_OVERLAY = 2020
      Volume controls

    TYPE_BOOT_PROGRESS = 2021
      Boot animation

    TYPE_INPUT_CONSUMER = 2022
      Input consumer

    TYPE_NAVIGATION_BAR_PANEL = 2024
      Panel nav bar

    TYPE_DISPLAY_OVERLAY = 2026
      Display overlay

    TYPE_MAGNIFICATION_OVERLAY = 2027
      Magnification overlay

    TYPE_PRIVATE_PRESENTATION = 2030
      Private display presentation

    TYPE_VOICE_INTERACTION = 2031
      Voice interaction

    TYPE_ACCESSIBILITY_OVERLAY = 2032
      Accessibility (TalkBack highlights)

    TYPE_VOICE_INTERACTION_STARTING = 2033

    TYPE_DOCK_DIVIDER = 2034
      Split-screen divider

    TYPE_QS_DIALOG = 2035
      Quick Settings dialogs

    TYPE_SCREENSHOT = 2036
      Screenshot UI

    TYPE_PRESENTATION = 2037
      Presentation на external display

    TYPE_APPLICATION_OVERLAY = 2038
      App overlay (Android 8+) — требует SYSTEM_ALERT_WINDOW
      Пузыри (Bubbles), Picture-in-Picture, overlay apps

    TYPE_ACCESSIBILITY_MAGNIFICATION_OVERLAY = 2039

    TYPE_NOTIFICATION_SHADE = 2040
      Notification shade

    TYPE_STATUS_BAR_ADDITIONAL = 2041
      Additional status bar (foldables)
```

### Permission requirements

| Тип окна | Permission | Примечание |
|----------|------------|------------|
| TYPE_APPLICATION (1-99) | Нет | Обычные Activity |
| TYPE_APPLICATION_PANEL (1000) | Нет | Нужен parent token |
| TYPE_TOAST (2005) | Нет | Только через Toast API |
| TYPE_APPLICATION_OVERLAY (2038) | SYSTEM_ALERT_WINDOW | Запрашивается через Settings |
| TYPE_STATUS_BAR (2000) | Signature | Только system apps |
| TYPE_INPUT_METHOD (2011) | BIND_INPUT_METHOD | Только IME apps |
| TYPE_ACCESSIBILITY_OVERLAY | BIND_ACCESSIBILITY | Только accessibility services |

### Проверка и запрос SYSTEM_ALERT_WINDOW

```kotlin
// Проверка permission
fun canDrawOverlays(context: Context): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        Settings.canDrawOverlays(context)
    } else {
        true // Pre-M: было обычным dangerous permission
    }
}

// Запрос permission (открывает Settings)
fun requestOverlayPermission(activity: Activity) {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        if (!Settings.canDrawOverlays(activity)) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:${activity.packageName}")
            )
            activity.startActivity(intent)
        }
    }
}

// Использование overlay window
fun showOverlay(context: Context) {
    if (!canDrawOverlays(context)) {
        Log.e("Overlay", "No permission!")
        return
    }

    val windowManager = context.getSystemService<WindowManager>()!!

    val overlayView = LayoutInflater.from(context)
        .inflate(R.layout.overlay, null)

    val params = WindowManager.LayoutParams(
        WindowManager.LayoutParams.WRAP_CONTENT,
        WindowManager.LayoutParams.WRAP_CONTENT,
        WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
        WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
            WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
        PixelFormat.TRANSLUCENT
    ).apply {
        gravity = Gravity.TOP or Gravity.START
        x = 100
        y = 100
    }

    windowManager.addView(overlayView, params)

    // Не забыть удалить!
    // windowManager.removeView(overlayView)
}
```

---

## Dialog, PopupWindow, Toast — разные модели

### Dialog — создаёт PhoneWindow

```kotlin
// Dialog.java (упрощённо)
class Dialog {
    private val mWindow: Window        // СВОЙ PhoneWindow!
    private val mDecor: View           // СВОЙ DecorView!
    private val mWindowManager: WindowManager
    private val mContext: Context

    init {
        mWindowManager = context.getSystemService(WINDOW_SERVICE) as WindowManager

        // Создаём СВОЙ PhoneWindow (не используем Activity window)
        mWindow = PhoneWindow(context)
        mWindow.setWindowManager(mWindowManager, null, null)

        // Если context — Activity, берём её window token
        // Иначе — crash (BadTokenException)
    }

    fun show() {
        // 1. Создать DecorView с контентом
        mDecor = mWindow.decorView
        val params = mWindow.attributes

        // 2. Добавить в WindowManager
        mWindowManager.addView(mDecor, params)
        // TYPE_APPLICATION → требует Activity token
    }

    fun dismiss() {
        mWindowManager.removeViewImmediate(mDecor)
    }
}
```

**Почему Dialog + Application Context = BadTokenException:**

```
Activity Context:                Application Context:
─────────────────               ─────────────────────
┌─────────────────┐             ┌──────────────────┐
│  Activity       │             │  Application     │
│  ├── mToken ────┼──→ IBinder  │  └── mToken = null
│  └── mWindow    │             │                   │
└─────────────────┘             └──────────────────┘
         │
         ▼
Dialog берёт token из Activity.getWindowToken()
и использует его в WindowManager.addView()

WMS проверяет: token существует? привязан к Activity?
  → Activity token: OK
  → null token: BadTokenException!
```

### PopupWindow — без PhoneWindow

```kotlin
// PopupWindow.java (упрощённо)
class PopupWindow {
    private var mContentView: View?
    private var mPopupView: PopupDecorView?  // Обёртка
    private val mWindowManager: WindowManager

    // НЕ создаёт PhoneWindow!
    // Напрямую добавляет View в WindowManager

    fun showAsDropDown(anchor: View, xoff: Int, yoff: Int) {
        // 1. Вычислить позицию относительно anchor
        val location = IntArray(2)
        anchor.getLocationOnScreen(location)
        val x = location[0] + xoff
        val y = location[1] + anchor.height + yoff

        // 2. Создать обёртку для контента
        mPopupView = PopupDecorView(mContext).apply {
            addView(mContentView)
        }

        // 3. Параметры окна
        val params = WindowManager.LayoutParams(
            mWidth,
            mHeight,
            WindowManager.LayoutParams.TYPE_APPLICATION_PANEL, // Sub-window!
            WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            PixelFormat.TRANSLUCENT
        ).apply {
            this.x = x
            this.y = y
            // token берётся из anchor view → Activity window
            token = anchor.windowToken
        }

        // 4. Добавить напрямую в WindowManager
        mWindowManager.addView(mPopupView, params)
    }

    fun dismiss() {
        mWindowManager.removeView(mPopupView)
    }
}
```

### Toast — свой token (работает отовсюду)

```kotlin
// Toast использует INotificationManager для показа
// Не зависит от Activity token!

// Toast.java (упрощённо)
class Toast {
    fun show() {
        val tn = TN()  // Binder callback
        val service = INotificationManager.Stub.asInterface(
            ServiceManager.getService(Context.NOTIFICATION_SERVICE))

        // Toast запрашивает у системы СВОЙ token
        service.enqueueToast(packageName, tn, duration)
    }

    // TN — transient notification callback
    inner class TN : ITransientNotification.Stub() {
        override fun show(windowToken: IBinder) {
            // Система даёт token специально для этого Toast
            // TYPE_TOAST не требует Activity
            mHandler.post { handleShow(windowToken) }
        }

        private fun handleShow(windowToken: IBinder) {
            val params = WindowManager.LayoutParams(
                WRAP_CONTENT, WRAP_CONTENT,
                TYPE_TOAST,  // Системный тип, не требует permission
                FLAG_NOT_FOCUSABLE or FLAG_NOT_TOUCHABLE,
                PixelFormat.TRANSLUCENT
            ).apply {
                token = windowToken  // Token от системы, не от Activity!
            }
            mWM.addView(mView, params)
        }
    }
}

// Поэтому работает:
Toast.makeText(applicationContext, "Hello", Toast.LENGTH_SHORT).show()
// applicationContext НЕ имеет Activity token, но Toast не зависит от него
```

### Сравнительная таблица

| Компонент | Создаёт PhoneWindow | Token source | Требует Activity Context |
|-----------|---------------------|--------------|-------------------------|
| Activity | Да (в attach()) | Системный | N/A (это Activity) |
| Dialog | Да | Activity window | Да |
| AlertDialog | Да | Activity window | Да |
| BottomSheetDialog | Да | Activity window | Да |
| PopupWindow | Нет | Anchor view | Да (через anchor) |
| PopupMenu | Нет (PopupWindow) | Anchor view | Да |
| Toast | Нет | Системный (NMS) | Нет |
| Snackbar | Нет (View) | Activity | Да (нужна CoordinatorLayout) |

---

## Surface и SurfaceFlinger

### Архитектура графической подсистемы

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              APP PROCESS                                 │
│                                                                          │
│  ┌──────────────────┐     ┌──────────────────┐     ┌────────────────┐   │
│  │ View.draw() /    │     │    Canvas /      │     │    Surface     │   │
│  │ Canvas drawing   │ ──→ │  RenderThread    │ ──→ │   (producer)   │   │
│  │                  │     │  (HW accel)      │     │                │   │
│  └──────────────────┘     └──────────────────┘     └────────────────┘   │
│                                                           │              │
│                                                           │ dequeue/queue│
│                                                           ▼              │
│                                                    ┌────────────────┐   │
│                                                    │  BufferQueue   │   │
│                                                    │  (IPC shared)  │   │
│                                                    └────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                                           │
                                                           │ acquire/release
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SURFACEFLINGER PROCESS                           │
│                                                                          │
│  ┌────────────────┐    ┌────────────────────────────────────────────┐   │
│  │   Layer #1     │    │                                            │   │
│  │ (StatusBar)    │    │           COMPOSITION                      │   │
│  └───────┬────────┘    │                                            │   │
│          │             │    ┌─────────────────────────────────────┐ │   │
│  ┌───────▼────────┐    │    │  Client Composition (GPU)           │ │   │
│  │   Layer #2     │────┼───→│  - OpenGL ES / Vulkan               │ │   │
│  │ (App Window)   │    │    │  - Renders to framebuffer           │ │   │
│  └───────┬────────┘    │    └─────────────────────────────────────┘ │   │
│          │             │                 OR                          │   │
│  ┌───────▼────────┐    │    ┌─────────────────────────────────────┐ │   │
│  │   Layer #3     │────┼───→│  Device Composition (HWC)           │ │   │
│  │ (NavBar)       │    │    │  - Hardware Composer HAL            │ │   │
│  └───────┬────────┘    │    │  - Direct hardware overlay          │ │   │
│          │             │    │  - More efficient, less power       │ │   │
│  ┌───────▼────────┐    │    └─────────────────────────────────────┘ │   │
│  │   Layer #4     │    │                                            │   │
│  │ (IME)          │    │                                            │   │
│  └────────────────┘    └────────────────────────────────────────────┘   │
│                                        │                                 │
└────────────────────────────────────────┼─────────────────────────────────┘
                                         │
                                         ▼
                                  ┌────────────┐
                                  │  DISPLAY   │
                                  │  (VSYNC)   │
                                  └────────────┘
```

### BufferQueue — producer/consumer model

```
BufferQueue — очередь графических буферов

Producer (App)                BufferQueue                 Consumer (SF)
─────────────                ────────────                ─────────────
     │                    ┌──────────────┐                    │
     │                    │ Slots:       │                    │
     │  1. dequeueBuffer  │ ┌──┐┌──┐┌──┐ │                    │
     │  ─────────────────→│ │B1││B2││B3│ │                    │
     │  "Give me empty    │ └──┘└──┘└──┘ │                    │
     │   buffer to draw"  │    FREE      │                    │
     │                    │              │                    │
     │  ← Buffer #1       │ ┌──┐         │                    │
     │                    │ │B1│ DEQUEUED│                    │
     │                    │ └──┘         │                    │
     │                    │              │                    │
     │  ... draw to B1 ...│              │                    │
     │                    │              │                    │
     │  2. queueBuffer    │ ┌──┐         │                    │
     │  ─────────────────→│ │B1│ QUEUED  │                    │
     │  "I'm done, take   │ └──┘         │                    │
     │   this buffer"     │              │                    │
     │                    │              │  3. acquireBuffer  │
     │                    │              │  ←─────────────────│
     │                    │ ┌──┐         │  "Give me buffer   │
     │                    │ │B1│ ACQUIRED│   to display"      │
     │                    │ └──┘         │                    │
     │                    │              │  ... display B1 ...│
     │                    │              │                    │
     │                    │              │  4. releaseBuffer  │
     │                    │ ┌──┐         │  ←─────────────────│
     │                    │ │B1│ FREE    │  "Done displaying" │
     │                    │ └──┘         │                    │


Buffer states:
  FREE      → можно dequeue
  DEQUEUED  → app рисует
  QUEUED    → готов к показу
  ACQUIRED  → SF показывает
```

### Triple buffering и VSYNC

```
Timeline с triple buffering:
────────────────────────────

VSYNC  │    │    │    │    │    │    │
───────┼────┼────┼────┼────┼────┼────┼──────
       │    │    │    │    │    │    │
       ▼    ▼    ▼    ▼    ▼    ▼    ▼

App    ┌────┐    ┌────┐    ┌────┐
CPU    │ A1 │    │ A2 │    │ A3 │
       └────┘    └────┘    └────┘

App         ┌────┐    ┌────┐    ┌────┐
GPU         │ G1 │    │ G2 │    │ G3 │
            └────┘    └────┘    └────┘

Display          ┌────┐    ┌────┐    ┌────┐
                 │ D1 │    │ D2 │    │ D3 │
                 └────┘    └────┘    └────┘

Buffer flow:
  Frame 1: App draws A1 → GPU renders G1 → Display shows D1
  Frame 2: App draws A2 → GPU renders G2 → Display shows D2
  ...

With 3 buffers:
  - Buffer 1: being displayed (ACQUIRED)
  - Buffer 2: being rendered by GPU (DEQUEUED)
  - Buffer 3: being drawn by CPU (DEQUEUED)

Benefits:
  - App never waits for GPU
  - GPU never waits for display
  - Consistent 60/90/120 fps
```

### SurfaceView vs TextureView

```
SurfaceView:
────────────
┌─────────────────────────────────────────┐
│  Activity Window (z=2)                  │
│  ┌─────────────────────────────────┐    │
│  │  DecorView                      │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  SurfaceView (hole punch) │  │    │  ← "дырка" в Activity window
│  │  │  ██████████████████████████│  │    │
│  │  └───────────────────────────┘  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│  SurfaceView Surface (z=1)              │  ← ОТДЕЛЬНЫЙ Surface!
│  (Video content rendered here)          │    Ниже Activity window
└─────────────────────────────────────────┘

+ Отдельный Surface = отдельный rendering thread
+ Идеально для video, camera, games
+ Меньше latency
- Не работают View transforms (rotation, scale, alpha)
- Не работает в RecyclerView (сложно)


TextureView:
────────────
┌─────────────────────────────────────────┐
│  Activity Window                        │
│  ┌─────────────────────────────────┐    │
│  │  DecorView                      │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  TextureView               │  │    │  ← Часть View hierarchy
│  │  │  ┌─────────────────────┐  │  │    │
│  │  │  │ SurfaceTexture      │  │  │    │
│  │  │  │ (renders to texture)│  │  │    │  ← OpenGL texture
│  │  │  └─────────────────────┘  │  │    │
│  │  └───────────────────────────┘  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

+ Работают View transforms
+ Работает в RecyclerView
+ Часть View hierarchy
- Hardware acceleration REQUIRED
- Больше memory (extra texture copy)
- Больше latency
```

---

## Window Insets — детальный разбор

### Все типы инсетов

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ██████████████████████████████████████████████████████████████████████ │
│ ██                                                                   ██ │
│ ██  ┌──────────────────────────────────────────────────────────┐    ██ │
│ ██  │ STATUS BAR (24-48dp)                                      │    ██ │
│ ██  │ statusBars(), statusBarsIgnoringVisibility()             │    ██ │
│ ██  └──────────────────────────────────────────────────────────┘    ██ │
│ ██                                                                   ██ │
│ ██████                                                         ██████ │
│      █ ┌──────────────────────────────────────────────────┐ █        │
│      █ │                                                  │ █        │
│ DISPLAY│                                                  │DISPLAY   │
│ CUTOUT │            SAFE CONTENT AREA                     │CUTOUT    │
│      █ │                                                  │ █        │
│      █ │         safeDrawing()                           │ █        │
│      █ │         safeContent()                           │ █        │
│      █ │                                                  │ █        │
│      █ └──────────────────────────────────────────────────┘ █        │
│ ██████                                                         ██████ │
│ ██                                                                   ██ │
│ ██  ┌──────────────────────────────────────────────────────────┐    ██ │
│ ██  │ NAVIGATION BAR (gesture: 16-48dp, buttons: 48dp)         │    ██ │
│ ██  │ navigationBars(), navigationBarsIgnoringVisibility()     │    ██ │
│ ██  └──────────────────────────────────────────────────────────┘    ██ │
│ ██                                                                   ██ │
│ ██████████████████████████████████████████████████████████████████████ │
│ SYSTEM GESTURES                                                         │
│ (edge swipe areas)                                                     │
│ systemGestures()                                                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │                     APP CONTENT                                   │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ████████████████████████████████████████████████████████████████ │   │
│  │ ██                                                            ██ │   │
│  │ ██  KEYBOARD (IME)                                            ██ │   │
│  │ ██  ime()                                                     ██ │   │
│  │ ██                                                            ██ │   │
│  │ ████████████████████████████████████████████████████████████████ │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### WindowInsetsCompat.Type — полный справочник

```kotlin
object Type {
    // ═══ System bars ═══
    fun statusBars(): Int              // Status bar area
    fun navigationBars(): Int          // Navigation bar area
    fun systemBars(): Int              // statusBars() | navigationBars()

    // ═══ Keyboard ═══
    fun ime(): Int                     // Input Method (keyboard)

    // ═══ Display cutout ═══
    fun displayCutout(): Int           // Notch / hole punch camera

    // ═══ Gestures ═══
    fun systemGestures(): Int          // Edge swipe gesture areas
    fun mandatorySystemGestures(): Int // Non-excludable gesture areas
    fun tappableElement(): Int         // Where system taps work

    // ═══ Caption bar ═══
    fun captionBar(): Int              // Freeform window caption

    // ═══ Combined ═══
    fun safeDrawing(): Int     // systemBars | displayCutout
    fun safeContent(): Int     // safeDrawing | ime
    fun safeGestures(): Int    // systemGestures | mandatorySystemGestures

    // ═══ IgnoringVisibility variants ═══
    // Возвращают insets даже когда bars скрыты
    // Полезно для stable layout
}
```

### View System — обработка инсетов

```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge() // Включить edge-to-edge

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ═══ Способ 1: OnApplyWindowInsetsListener (рекомендуется) ═══
        val rootView = findViewById<View>(R.id.root)
        ViewCompat.setOnApplyWindowInsetsListener(rootView) { view, windowInsets ->
            // Получить нужные insets
            val systemBars = windowInsets.getInsets(WindowInsetsCompat.Type.systemBars())
            val ime = windowInsets.getInsets(WindowInsetsCompat.Type.ime())
            val cutout = windowInsets.getInsets(WindowInsetsCompat.Type.displayCutout())

            // Применить padding
            view.updatePadding(
                left = systemBars.left,
                top = systemBars.top,
                right = systemBars.right,
                bottom = maxOf(systemBars.bottom, ime.bottom) // keyboard aware
            )

            // ВАЖНО: что возвращать?
            // - WindowInsetsCompat.CONSUMED → insets не передаются детям
            // - windowInsets → insets передаются детям для дальнейшей обработки
            windowInsets
        }

        // ═══ Способ 2: Для конкретного View (например FAB) ═══
        val fab = findViewById<FloatingActionButton>(R.id.fab)
        ViewCompat.setOnApplyWindowInsetsListener(fab) { view, insets ->
            val navBars = insets.getInsets(WindowInsetsCompat.Type.navigationBars())
            val ime = insets.getInsets(WindowInsetsCompat.Type.ime())

            // Margin вместо padding для FAB
            val lp = view.layoutParams as ViewGroup.MarginLayoutParams
            lp.bottomMargin = maxOf(navBars.bottom, ime.bottom) + 16.dp
            view.layoutParams = lp

            insets
        }

        // ═══ Способ 3: Для RecyclerView (scroll под bars) ═══
        val recyclerView = findViewById<RecyclerView>(R.id.recycler)
        // В XML: android:clipToPadding="false"
        ViewCompat.setOnApplyWindowInsetsListener(recyclerView) { view, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())

            // Padding позволяет контенту скроллиться под bars
            view.updatePadding(
                bottom = systemBars.bottom
            )
            // Контент начинается под toolbar, заканчивается над nav bar
            // Но скроллится под оба

            insets
        }
    }
}
```

### Compose — обработка инсетов

```kotlin
@Composable
fun MyScreen() {
    // ═══ Scaffold автоматически обрабатывает insets ═══
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("App Title") }
                // TopAppBar автоматически добавляет statusBarsPadding
            )
        },
        bottomBar = {
            NavigationBar {
                // NavigationBar автоматически добавляет navigationBarsPadding
            }
        }
    ) { innerPadding ->
        // innerPadding включает все необходимые insets
        LazyColumn(
            modifier = Modifier.padding(innerPadding),
            contentPadding = PaddingValues(bottom = 16.dp)
        ) {
            items(100) { index ->
                Text("Item $index")
            }
        }
    }
}

@Composable
fun ManualInsetsHandling() {
    // ═══ Получить текущие insets ═══
    val systemBars = WindowInsets.systemBars
    val ime = WindowInsets.ime
    val displayCutout = WindowInsets.displayCutout

    // ═══ Modifier extensions ═══
    Box(
        modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding()          // Отступ от status bar
            .navigationBarsPadding()      // Отступ от nav bar
            .imePadding()                 // Отступ от клавиатуры
            .displayCutoutPadding()       // Отступ от выреза
            .safeDrawingPadding()         // systemBars + cutout
            .safeContentPadding()         // safeDrawing + ime
    ) {
        // Content
    }

    // ═══ WindowInsets как значения ═══
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(
                top = systemBars.asPaddingValues()
                    .calculateTopPadding(),
                bottom = ime.asPaddingValues()
                    .calculateBottomPadding()
            )
    ) {
        // Content
    }

    // ═══ Consumption ═══
    Box(
        modifier = Modifier
            .fillMaxSize()
            .consumeWindowInsets(WindowInsets.systemBars)
            // После этого дети получат insets = 0 для systemBars
    ) {
        // Children won't see systemBars insets
    }
}

@Composable
fun KeyboardAwareContent() {
    var text by remember { mutableStateOf("") }

    // ime() возвращает анимированные insets!
    // Клавиатура плавно появляется, контент плавно сдвигается
    val imeInsets = WindowInsets.ime

    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding() // Автоматическая анимация!
    ) {
        Spacer(modifier = Modifier.weight(1f))

        TextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

### Excluding system gestures

```kotlin
// Исключить зону от system gestures
// Полезно для: seekbar, drawing canvas, game controls

fun excludeSystemGestures(view: View) {
    view.doOnLayout {
        // Исключить всю область View из system gestures
        val rect = Rect(0, 0, view.width, view.height)
        ViewCompat.setSystemGestureExclusionRects(view, listOf(rect))
    }
}

// Compose
@Composable
fun SeekBarWithGestureExclusion() {
    Slider(
        value = progress,
        onValueChange = { progress = it },
        modifier = Modifier
            .fillMaxWidth()
            .systemGestureExclusion() // Compose 1.7+
    )
}
```

---

## Edge-to-Edge (Android 15 обязательно)

### Что изменилось в Android 15

```
До Android 15:                    Android 15 (targetSdk 35):
─────────────────                 ──────────────────────────
┌─────────────────┐               ┌─────────────────┐
│ ▓▓ Status ▓▓▓▓ │ opaque        │ ░░ Status ░░░░ │ transparent!
├─────────────────┤               │                 │
│                 │               │    APP DRAWS    │
│   App Content   │               │    UNDER BARS   │
│                 │               │                 │
├─────────────────┤               │                 │
│ ▓▓▓ NavBar ▓▓▓ │ opaque        │ ░░░ NavBar ░░░ │ transparent!
└─────────────────┘               └─────────────────┘

Принудительно для targetSdk 35:
• window.statusBarColor = transparent
• window.navigationBarColor = transparent
• layoutInDisplayCutoutMode = LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
• 3-button nav: полупрозрачный scrim (можно настроить)
```

### Полная миграция на edge-to-edge

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // ШАГ 1: Включить edge-to-edge
        // Для API < 35 это opt-in, для 35+ — обязательно
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.auto(
                lightScrim = Color.TRANSPARENT,
                darkScrim = Color.TRANSPARENT
            ),
            navigationBarStyle = SystemBarStyle.auto(
                lightScrim = Color.TRANSPARENT,
                darkScrim = Color.TRANSPARENT
            )
        )

        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_main)

        // ШАГ 2: Обработать insets для КАЖДОГО важного элемента

        // 2.1: Root layout — не добавлять padding (иначе нет edge-to-edge)
        // Но обработать его для передачи детям
        val root = findViewById<View>(R.id.root)
        ViewCompat.setOnApplyWindowInsetsListener(root) { _, insets ->
            // Не потреблять, передать детям
            insets
        }

        // 2.2: Toolbar — padding сверху
        val toolbar = findViewById<Toolbar>(R.id.toolbar)
        ViewCompat.setOnApplyWindowInsetsListener(toolbar) { view, insets ->
            val statusBars = insets.getInsets(WindowInsetsCompat.Type.statusBars())
            view.updatePadding(top = statusBars.top)
            insets
        }

        // 2.3: ScrollView/RecyclerView — padding снизу + clipToPadding=false
        val recyclerView = findViewById<RecyclerView>(R.id.recycler)
        recyclerView.clipToPadding = false // XML: android:clipToPadding="false"
        ViewCompat.setOnApplyWindowInsetsListener(recyclerView) { view, insets ->
            val navBars = insets.getInsets(WindowInsetsCompat.Type.navigationBars())
            view.updatePadding(bottom = navBars.bottom)
            insets
        }

        // 2.4: FAB — margin от nav bar
        val fab = findViewById<FloatingActionButton>(R.id.fab)
        ViewCompat.setOnApplyWindowInsetsListener(fab) { view, insets ->
            val navBars = insets.getInsets(WindowInsetsCompat.Type.navigationBars())
            val lp = view.layoutParams as ViewGroup.MarginLayoutParams
            lp.bottomMargin = navBars.bottom + 16.dpToPx()
            view.layoutParams = lp
            insets
        }

        // 2.5: BottomNavigationView — padding для nav bar
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)
        ViewCompat.setOnApplyWindowInsetsListener(bottomNav) { view, insets ->
            val navBars = insets.getInsets(WindowInsetsCompat.Type.navigationBars())
            view.updatePadding(bottom = navBars.bottom)
            insets
        }

        // ШАГ 3: Handle display cutout (если нужен landscape)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            window.attributes.layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        }
    }
}
```

### Compose edge-to-edge

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)

        setContent {
            MyAppTheme {
                // Compose Material 3 компоненты обрабатывают insets автоматически
                Scaffold(
                    topBar = {
                        TopAppBar(
                            title = { Text("My App") }
                            // TopAppBar автоматически: statusBarsPadding()
                        )
                    },
                    bottomBar = {
                        NavigationBar {
                            // NavigationBar автоматически: navigationBarsPadding()
                        }
                    },
                    floatingActionButton = {
                        // FAB автоматически учитывает навигацию
                        FloatingActionButton(onClick = { }) {
                            Icon(Icons.Default.Add, null)
                        }
                    }
                ) { innerPadding ->
                    LazyColumn(
                        modifier = Modifier.padding(innerPadding),
                        // contentPadding для scroll под bars
                        contentPadding = PaddingValues(bottom = 8.dp)
                    ) {
                        items(100) { Text("Item $it") }
                    }
                }
            }
        }
    }
}
```

### 3-button navigation scrim

```kotlin
// Для 3-button navigation на Android 15
// можно настроить защитный scrim

enableEdgeToEdge(
    navigationBarStyle = SystemBarStyle.auto(
        lightScrim = Color.argb(0x80, 0xFF, 0xFF, 0xFF), // Semi-transparent white
        darkScrim = Color.argb(0x80, 0x00, 0x00, 0x00)   // Semi-transparent black
    )
)

// Или убрать scrim совсем (не рекомендуется для 3-button):
enableEdgeToEdge(
    navigationBarStyle = SystemBarStyle.auto(
        lightScrim = Color.TRANSPARENT,
        darkScrim = Color.TRANSPARENT
    )
)

// Проверить тип навигации
val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
// isAppearanceLightNavigationBars — светлые иконки на тёмном фоне
```

---

## Multi-Window и Foldables

### WindowMetrics API

```kotlin
// Размер окна (не экрана!) — важно для multi-window
fun getWindowSize(activity: Activity): Pair<Int, Int> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
        val metrics = activity.windowManager.currentWindowMetrics
        val bounds = metrics.bounds
        bounds.width() to bounds.height()
    } else {
        @Suppress("DEPRECATION")
        val display = activity.windowManager.defaultDisplay
        val size = Point()
        display.getSize(size)
        size.x to size.y
    }
}

// Максимальный размер (весь экран)
fun getMaxWindowSize(activity: Activity): Pair<Int, Int> {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
        val metrics = activity.windowManager.maximumWindowMetrics
        val bounds = metrics.bounds
        bounds.width() to bounds.height()
    } else {
        @Suppress("DEPRECATION")
        val display = activity.windowManager.defaultDisplay
        val size = Point()
        display.getRealSize(size)
        size.x to size.y
    }
}

// Insets из WindowMetrics (API 30+)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
    val metrics = activity.windowManager.currentWindowMetrics
    val insets = metrics.windowInsets

    val systemBars = insets.getInsets(WindowInsets.Type.systemBars())
    val displayCutout = insets.getInsets(WindowInsets.Type.displayCutout())

    val safeWidth = metrics.bounds.width() - systemBars.left - systemBars.right
    val safeHeight = metrics.bounds.height() - systemBars.top - systemBars.bottom
}
```

### WindowSizeClass для адаптивного UI

```kotlin
// Material 3 WindowSizeClass
@Composable
fun AdaptiveLayout() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Телефон portrait: < 600dp
            // Single column, bottom nav
            CompactLayout()
        }
        WindowWidthSizeClass.Medium -> {
            // Телефон landscape / tablet portrait: 600-840dp
            // Two columns, navigation rail
            MediumLayout()
        }
        WindowWidthSizeClass.Expanded -> {
            // Tablet landscape / desktop: > 840dp
            // Three columns, permanent navigation drawer
            ExpandedLayout()
        }
    }
}

// WindowSizeClass breakpoints:
// Compact: width < 600dp
// Medium: 600dp <= width < 840dp
// Expanded: width >= 840dp
```

### Foldables и FoldingFeature

```kotlin
// Jetpack WindowManager library
implementation("androidx.window:window:1.2.0")

class FoldableActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                WindowInfoTracker.getOrCreate(this@FoldableActivity)
                    .windowLayoutInfo(this@FoldableActivity)
                    .collect { layoutInfo ->
                        handleFoldingFeatures(layoutInfo)
                    }
            }
        }
    }

    private fun handleFoldingFeatures(layoutInfo: WindowLayoutInfo) {
        for (feature in layoutInfo.displayFeatures) {
            if (feature is FoldingFeature) {
                when (feature.state) {
                    FoldingFeature.State.FLAT -> {
                        // Полностью раскрыт (tablet mode)
                        Log.d("Foldable", "FLAT - full tablet mode")
                    }
                    FoldingFeature.State.HALF_OPENED -> {
                        // Наполовину открыт (laptop/tent mode)
                        Log.d("Foldable", "HALF_OPENED - laptop mode")
                        // Можно разделить UI по fold
                    }
                }

                when (feature.orientation) {
                    FoldingFeature.Orientation.HORIZONTAL -> {
                        // Горизонтальный fold (Galaxy Fold)
                        // Top/bottom split
                    }
                    FoldingFeature.Orientation.VERTICAL -> {
                        // Вертикальный fold (Surface Duo)
                        // Left/right split
                    }
                }

                // Границы fold
                val foldBounds = feature.bounds
                // Можно позиционировать контент relative to fold
            }
        }
    }
}
```

---

## Window Flags и Window Attributes

### Основные флаги

```kotlin
// WindowManager.LayoutParams flags
object WindowFlags {
    // ═══ Focus и Touch ═══
    const val FLAG_NOT_FOCUSABLE = 0x00000008
    // Окно не получает фокус, input идёт на окно позади
    // Используется для: overlays, toasts

    const val FLAG_NOT_TOUCHABLE = 0x00000010
    // Touch events проходят насквозь
    // Используется для: visual-only overlays

    const val FLAG_NOT_TOUCH_MODAL = 0x00000020
    // Touch события за пределами окна идут другим окнам
    // По умолчанию: modal (поглощает все touch)

    // ═══ Display ═══
    const val FLAG_FULLSCREEN = 0x00000400
    // Скрыть status bar (deprecated, use WindowInsetsController)

    const val FLAG_LAYOUT_NO_LIMITS = 0x00000200
    // Разрешить layout за пределами экрана
    // Используется для: animations, overscan

    const val FLAG_LAYOUT_IN_SCREEN = 0x00000100
    // Layout относительно экрана, не window frame
    // Используется для: edge-to-edge

    // ═══ Security ═══
    const val FLAG_SECURE = 0x00002000
    // Запретить screenshots и screen recording
    // Используется для: banking apps, passwords

    // ═══ Dim и Blur ═══
    const val FLAG_DIM_BEHIND = 0x00000002
    // Затемнить окна позади
    // dimAmount задаёт степень (0.0-1.0)

    const val FLAG_BLUR_BEHIND = 0x00000004
    // Blur окна позади (требует hardware support)

    // ═══ Keyboard ═══
    const val FLAG_ALT_FOCUSABLE_IM = 0x00020000
    // Инвертировать поведение IME focus
}

// Примеры использования
fun setWindowFlags(window: Window) {
    // Secure window (no screenshots)
    window.setFlags(
        WindowManager.LayoutParams.FLAG_SECURE,
        WindowManager.LayoutParams.FLAG_SECURE
    )

    // Non-focusable overlay
    window.setFlags(
        WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
        WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
    )

    // Dim behind (for dialogs)
    window.setFlags(
        WindowManager.LayoutParams.FLAG_DIM_BEHIND,
        WindowManager.LayoutParams.FLAG_DIM_BEHIND
    )
    window.attributes = window.attributes.apply {
        dimAmount = 0.6f
    }
}
```

### Soft Input Mode

```kotlin
// Как окно реагирует на клавиатуру
window.setSoftInputMode(
    // ═══ Resize behavior ═══
    WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE or
    // Окно уменьшается чтобы поместиться над клавиатурой
    // DEPRECATED на API 30+, используйте insets

    WindowManager.LayoutParams.SOFT_INPUT_ADJUST_PAN or
    // Окно pan'ится чтобы focused view был видим
    // Content может обрезаться

    WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING or
    // Ничего не менять
    // Используйте insets для ручной обработки

    // ═══ Visibility ═══
    WindowManager.LayoutParams.SOFT_INPUT_STATE_HIDDEN or
    // Клавиатура скрыта при открытии Activity

    WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE or
    // Клавиатура показана при открытии Activity

    WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE
    // Всегда показывать клавиатуру
)

// Modern approach: WindowInsetsController
@RequiresApi(Build.VERSION_CODES.R)
fun showKeyboard(view: View) {
    view.windowInsetsController?.show(WindowInsets.Type.ime())
}

@RequiresApi(Build.VERSION_CODES.R)
fun hideKeyboard(view: View) {
    view.windowInsetsController?.hide(WindowInsets.Type.ime())
}

// Backwards compatible
fun showKeyboardCompat(view: View) {
    ViewCompat.getWindowInsetsController(view)?.show(WindowInsetsCompat.Type.ime())
}
```

---

## Мифы и заблуждения

| # | Миф | Реальность |
|---|-----|-----------|
| 1 | "Window — это отдельный физический объект" | Window — **абстракция**. Реализуется как View tree + ViewRootImpl + Surface. Физический объект — Surface (буфер в памяти) |
| 2 | "setContentView создаёт DecorView" | setContentView вызывает installDecor() который создаёт DecorView **если его ещё нет**. Обычно DecorView уже создан в Activity.attach() |
| 3 | "Dialog не создаёт отдельное окно" | Dialog создаёт **свой PhoneWindow** + DecorView + ViewRootImpl. Это полноценное отдельное окно |
| 4 | "Toast зависит от Activity" | Toast использует **системный token** от NotificationManager. Работает из Service, Application, любого Context |
| 5 | "Edge-to-edge — это opt-in фича" | С **Android 15 (targetSdk 35)** edge-to-edge **обязательно**. Системные бары прозрачны принудительно |
| 6 | "ViewRootImpl — это View" | ViewRootImpl implements **ViewParent**, но **не наследует от View**. Это мост между View tree и WMS |
| 7 | "Все окна имеют одинаковый тип" | **3 категории**: Application (1-99), Sub-window (1000-1999), System (2000+). Разные permissions, разный z-order |
| 8 | "SurfaceFlinger рисует содержимое окон" | SurfaceFlinger — **композитор**. Он собирает готовые буферы (Surfaces) в финальное изображение. Рисует содержимое **приложение** |
| 9 | "windowManager.addView() = новый PhoneWindow" | addView создаёт **ViewRootImpl**, но **не PhoneWindow**. PhoneWindow создаётся только для Activity и Dialog |
| 10 | "Insets нужны только для status bar" | Нужно обрабатывать: statusBars, navigationBars, ime, displayCutout, systemGestures, caption bar, tappable elements |
| 11 | "Configuration change пересоздаёт Window" | **Window остаётся**. Пересоздаётся Activity, но PhoneWindow и DecorView сохраняются (с мелкими обновлениями) |
| 12 | "PopupWindow и Dialog — одно и то же" | PopupWindow **не создаёт PhoneWindow**, напрямую добавляет View. Это TYPE_APPLICATION_PANEL (sub-window) |

---

## CS-фундамент

| Концепция | Как используется | Пример |
|-----------|-----------------|--------|
| **Decorator pattern** | DecorView "декорирует" content добавляя ActionBar, system backgrounds | DecorView wraps mContentParent, добавляет chrome |
| **Bridge pattern** | ViewRootImpl — мост между View hierarchy и WMS | View API ↔ ViewRootImpl ↔ WMS Binder API |
| **IPC (Binder)** | Все операции с WMS через Binder calls | addToDisplay(), relayout(), remove() |
| **Double/Triple Buffering** | BufferQueue: пока SF показывает один буфер, app рисует в другой | Нет мерцания, smooth 60fps |
| **Compositor** | SurfaceFlinger собирает все Surfaces в финальное изображение | StatusBar + App + NavBar + IME → screen |
| **Producer-Consumer** | App (producer) → BufferQueue → SurfaceFlinger (consumer) | Асинхронный rendering pipeline |
| **Z-ordering** | Окна упорядочены по типу и z-layer | System windows (z>2000) всегда поверх app windows (z<100) |
| **Observer pattern** | View.invalidate() → bubbles up → ViewRootImpl → scheduleTraversals() | Dirty region tracking |
| **Singleton** | WindowManagerGlobal — один на процесс | Управляет всеми окнами процесса |

---

## Проверь себя

### Вопрос 1
**Q:** Кто является parent для DecorView? Что вернёт `decorView.getParent()`?

<details>
<summary>Ответ</summary>

**ViewRootImpl**. Несмотря на то что ViewRootImpl не наследует от View, он реализует интерфейс ViewParent. DecorView.getParent() возвращает ViewRootImpl, который был создан в WindowManagerGlobal.addView() и привязан через ViewRootImpl.setView(decorView, ...).

ViewRootImpl — это корень иерархии Views с точки зрения parent chain. Выше него уже ничего нет (getParent() на ViewRootImpl возвращает null).
</details>

### Вопрос 2
**Q:** Почему Dialog с Application Context вызывает BadTokenException?

<details>
<summary>Ответ</summary>

Dialog вызывает WindowManager.addView() с TYPE_APPLICATION. WMS требует window token (IBinder) для привязки окна к Activity.

- **Activity Context** имеет token (mToken), полученный при создании Activity окна в ActivityThread
- **Application Context** не имеет token (mToken = null)

Когда Dialog пытается addView с null token, WMS отклоняет запрос:
```
BadTokenException: Unable to add window -- token null is not valid; is your activity running?
```

Решение: всегда передавать Activity context в конструктор Dialog.
</details>

### Вопрос 3
**Q:** Сколько Surface существует на экране с одним Activity, клавиатурой и системными барами?

<details>
<summary>Ответ</summary>

Минимум **4 Surface**:
1. StatusBar Surface (SystemUI)
2. App Surface (Activity + DecorView)
3. NavigationBar Surface (SystemUI)
4. InputMethod Surface (клавиатура)

Каждый Surface — отдельный буфер в памяти, SurfaceFlinger композитит их в финальное изображение на каждом VSYNC. При наличии Dialog — ещё один Surface. PopupWindow обычно рисуется в том же Surface что и parent.
</details>

### Вопрос 4
**Q:** Чем отличается PopupWindow от Dialog с точки зрения Window System?

<details>
<summary>Ответ</summary>

| Аспект | Dialog | PopupWindow |
|--------|--------|-------------|
| PhoneWindow | Создаёт свой | Не создаёт |
| DecorView | Свой | Нет (обёртка PopupDecorView) |
| Window type | TYPE_APPLICATION | TYPE_APPLICATION_PANEL |
| Token | Activity token | Anchor view token |
| Z-order | Отдельное окно | Sub-window (поверх parent) |
| Focus | Может быть modal | FLAG_NOT_FOCUSABLE типично |

Dialog — полноценное отдельное окно. PopupWindow — sub-window, привязанное к anchor view.
</details>

### Вопрос 5
**Q:** Что произойдёт если не обработать insets на Android 15 с targetSdk 35?

<details>
<summary>Ответ</summary>

На Android 15 с targetSdk 35 edge-to-edge **обязательно**:
1. Системные бары станут прозрачными
2. Приложение будет рисовать под status bar и navigation bar
3. Контент будет перекрыт системными барами
4. Текст и кнопки под status bar будут нечитаемы
5. Интерактивные элементы под nav bar будут недоступны

Необходимо:
1. Вызвать `enableEdgeToEdge()` для совместимости с pre-35
2. Обработать insets через `ViewCompat.setOnApplyWindowInsetsListener()` или Compose modifiers
3. Добавить padding/margin к важным элементам
</details>

---

## Связи

### Фундамент
- **[[android-view-rendering-pipeline]]** — ViewRootImpl запускает measure/layout/draw; Surface — конечный target рисования; Choreographer и VSYNC
- **[[android-activity-lifecycle]]** — Window создаётся в Activity.attach(), DecorView добавляется в makeVisible() после onResume()
- **[[android-context-internals]]** — Window token привязан к Activity Context; Application Context не имеет token → Dialog crash

### Тесно связаны
- **[[android-touch-handling]]** — Input events идут: WMS → ViewRootImpl → DecorView → View tree; touch dispatch policy
- **[[android-compose]]** — ComposeView встраивается в DecorView; Compose WindowInsets API; Material 3 automatic insets handling
- **[[android-handler-looper]]** — Choreographer использует Handler для VSYNC callbacks; scheduleTraversals()

### Дополнительно
- **[[android-performance-profiling]]** — Perfetto показывает SurfaceFlinger timing, frame composition, jank причины
- **[[android-binder-ipc]]** — Все операции с WMS через Binder: addToDisplay, relayout, remove, finishDrawing

---

## Источники

| # | Источник | Тип | Описание |
|---|---------|-----|----------|
| 1 | [AOSP: PhoneWindow.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/com/android/internal/policy/PhoneWindow.java) | AOSP | Единственная реализация Window |
| 2 | [AOSP: ViewRootImpl.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/view/ViewRootImpl.java) | AOSP | Мост View↔WMS (~15,000 строк) |
| 3 | [AOSP: WindowManagerService.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/services/core/java/com/android/server/wm/WindowManagerService.java) | AOSP | Системный сервис окон |
| 4 | [AOSP: DecorView.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/com/android/internal/policy/DecorView.java) | AOSP | Root view окна |
| 5 | [Edge-to-edge display](https://developer.android.com/develop/ui/views/layout/edge-to-edge) | Docs | Официальное руководство по edge-to-edge |
| 6 | [Window Insets](https://developer.android.com/develop/ui/views/layout/insets) | Docs | Обработка инсетов |
| 7 | [SurfaceFlinger and HWC](https://source.android.com/docs/core/graphics/surfaceflinger-windowmanager) | Docs | SurfaceFlinger архитектура |
| 8 | [BufferQueue and gralloc](https://source.android.com/docs/core/graphics/arch-bq-gralloc) | Docs | BufferQueue internals |
| 9 | [WindowMetrics API](https://developer.android.com/reference/android/view/WindowMetrics) | Docs | API для размеров окна (Android 11+) |
| 10 | [Compose Window Insets](https://developer.android.com/develop/ui/compose/layouts/insets) | Docs | Insets в Jetpack Compose |
| 11 | [Foldables and large screens](https://developer.android.com/guide/topics/large-screens) | Docs | Адаптация для foldables |
| 12 | [WindowManager Jetpack library](https://developer.android.com/jetpack/androidx/releases/window) | Docs | FoldingFeature, WindowLayoutInfo |
| 13 | [Android 15 edge-to-edge](https://developer.android.com/about/versions/15/behavior-changes-15) | Docs | Обязательный edge-to-edge в Android 15 |
| 14 | [How Android Renders UI](https://medium.com/@nicholasnielson/how-android-renders-the-ui) | Article | Window → Surface → SurfaceFlinger pipeline |

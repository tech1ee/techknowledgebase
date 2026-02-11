---
title: "Система ресурсов Android: типы, квалификаторы, R класс"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [resource-abstraction, locale-matching, qualifier-system, code-generation]
tags:
  - topic/android
  - topic/resources
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-project-structure]]"
  - "[[android-ui-views]]"
  - "[[android-compilation-pipeline]]"
  - "[[android-apk-aab]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-project-structure]]"
---

# Система ресурсов Android: типы, квалификаторы, R класс

Ресурсы в Android — это отделённые от кода данные: строки, изображения, layouts, цвета, размеры. Система ресурсов автоматически подбирает правильные варианты для разных устройств, языков и конфигураций.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android
> - [[android-project-structure]] — структура проекта

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Resource** | Внешний файл или значение, используемое приложением |
| **Qualifier** | Суффикс директории для альтернативных ресурсов |
| **R class** | Автогенерированный класс с ID ресурсов |
| **AAPT2** | Android Asset Packaging Tool — компилирует ресурсы |
| **Resource Merging** | Объединение ресурсов из модулей и библиотек |
| **Configuration** | Состояние устройства (язык, плотность, ориентация) |

---

## Типы ресурсов

```
res/
├── drawable/           # Графика (vectors, shapes, selectors)
├── drawable-hdpi/      # Растровая графика для плотности hdpi
├── layout/             # XML layouts
├── menu/               # Menu definitions
├── mipmap-*/           # Иконки приложения
├── values/             # Строки, цвета, размеры, стили
├── values-night/       # Значения для тёмной темы
├── values-ru/          # Русская локализация
├── raw/                # Произвольные файлы (audio, video)
├── xml/                # Конфигурационные XML
├── font/               # Шрифты
├── navigation/         # Navigation graphs
├── animator/           # Property animations
├── anim/               # View animations
└── color/              # Color state lists
```

### drawable/

```xml
<!-- res/drawable/ic_heart.xml — Vector Drawable -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF0000"
        android:pathData="M12,21.35l-1.45,-1.32C5.4,15.36 2,12.28 2,8.5 2,5.42 4.42,3 7.5,3c1.74,0 3.41,0.81 4.5,2.09C13.09,3.81 14.76,3 16.5,3 19.58,3 22,5.42 22,8.5c0,3.78 -3.4,6.86 -8.55,11.54L12,21.35z"/>
</vector>

<!-- res/drawable/button_background.xml — Shape -->
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="@color/primary"/>
    <corners android:radius="8dp"/>
    <stroke android:width="1dp" android:color="@color/primary_dark"/>
</shape>

<!-- res/drawable/button_selector.xml — State List -->
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_pressed="true" android:drawable="@drawable/button_pressed"/>
    <item android:state_focused="true" android:drawable="@drawable/button_focused"/>
    <item android:state_enabled="false" android:drawable="@drawable/button_disabled"/>
    <item android:drawable="@drawable/button_normal"/>
</selector>
```

### values/

```xml
<!-- res/values/strings.xml -->
<resources>
    <string name="app_name">My Application</string>
    <string name="welcome_message">Welcome, %1$s!</string>
    <string name="items_count">%1$d items</string>

    <!-- Plurals -->
    <plurals name="notification_count">
        <item quantity="one">%d notification</item>
        <item quantity="other">%d notifications</item>
    </plurals>

    <!-- String Array -->
    <string-array name="countries">
        <item>Russia</item>
        <item>USA</item>
        <item>Germany</item>
    </string-array>
</resources>

<!-- res/values/colors.xml -->
<resources>
    <color name="primary">#6200EE</color>
    <color name="primary_dark">#3700B3</color>
    <color name="accent">#03DAC5</color>
    <color name="text_primary">#212121</color>
    <color name="text_secondary">#757575</color>
    <color name="background">#FFFFFF</color>

    <!-- Color with alpha -->
    <color name="overlay">#80000000</color>
</resources>

<!-- res/values/dimens.xml -->
<resources>
    <dimen name="spacing_small">8dp</dimen>
    <dimen name="spacing_medium">16dp</dimen>
    <dimen name="spacing_large">24dp</dimen>
    <dimen name="text_body">14sp</dimen>
    <dimen name="text_title">20sp</dimen>
    <dimen name="corner_radius">8dp</dimen>
</resources>

<!-- res/values/styles.xml -->
<resources>
    <style name="TextAppearance.Body" parent="TextAppearance.Material3.BodyMedium">
        <item name="android:textSize">@dimen/text_body</item>
        <item name="android:textColor">@color/text_primary</item>
    </style>

    <style name="Button.Primary" parent="Widget.Material3.Button">
        <item name="android:background">@drawable/button_background</item>
        <item name="android:textColor">@android:color/white</item>
        <item name="android:paddingHorizontal">@dimen/spacing_medium</item>
    </style>
</resources>
```

### raw/ и assets/

```
res/raw/                    # Доступ через R.raw.filename
├── notification.mp3
├── config.json
└── data.db

assets/                     # Доступ через AssetManager (не через R)
├── fonts/
│   └── custom_font.ttf
├── webview/
│   └── index.html
└── databases/
    └── prepopulated.db
```

```kotlin
// Доступ к raw ресурсам
val inputStream = resources.openRawResource(R.raw.config)

// Доступ к assets
val assetManager = context.assets
val inputStream = assetManager.open("webview/index.html")

// Список файлов в assets
val files = assetManager.list("fonts")
```

---

## Resource Qualifiers

Квалификаторы позволяют создавать альтернативные ресурсы для разных конфигураций устройств.

```
res/
├── values/                     # По умолчанию (английский)
│   └── strings.xml
├── values-ru/                  # Русский
│   └── strings.xml
├── values-uk/                  # Украинский
│   └── strings.xml
├── values-night/               # Тёмная тема
│   └── colors.xml
├── values-sw600dp/             # Планшеты (ширина >= 600dp)
│   └── dimens.xml
├── drawable/                   # Vectors (не зависят от плотности)
│   └── ic_icon.xml
├── drawable-hdpi/              # ~160dpi → 240dpi
│   └── logo.png
├── drawable-xhdpi/             # ~240dpi → 320dpi
│   └── logo.png
├── drawable-xxhdpi/            # ~320dpi → 480dpi
│   └── logo.png
├── drawable-xxxhdpi/           # ~480dpi → 640dpi
│   └── logo.png
├── layout/                     # По умолчанию (телефон, портрет)
│   └── activity_main.xml
├── layout-land/                # Ландшафт
│   └── activity_main.xml
├── layout-sw600dp/             # Планшет
│   └── activity_main.xml
└── layout-sw600dp-land/        # Планшет в ландшафте
    └── activity_main.xml
```

### Порядок квалификаторов

Квалификаторы должны идти в строго определённом порядке:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  ПОРЯДОК КВАЛИФИКАТОРОВ (обязательный)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. MCC и MNC (мобильный код страны и сети)  mcc310-mnc004             │
│  2. Язык и регион                            ru, en-rUS                 │
│  3. Layout direction                         ldrtl, ldltr               │
│  4. Smallest width                           sw600dp                    │
│  5. Available width                          w720dp                     │
│  6. Available height                         h1024dp                    │
│  7. Screen size                              small, normal, large       │
│  8. Screen aspect                            long, notlong              │
│  9. Round screen                             round, notround            │
│  10. Wide Color Gamut                        widecg, nowidecg           │
│  11. HDR                                     highdr, lowdr              │
│  12. Screen orientation                      port, land                 │
│  13. UI mode                                 car, desk, television      │
│  14. Night mode                              night, notnight            │
│  15. Screen density                          hdpi, xhdpi, xxhdpi        │
│  16. Touchscreen type                        finger, notouch            │
│  17. Keyboard availability                   keysexposed, keyshidden    │
│  18. Primary text input method               nokeys, qwerty, 12key      │
│  19. Navigation key availability             navexposed, navhidden      │
│  20. Primary non-touch navigation            nonav, dpad, trackball     │
│  21. Platform version                        v21, v26, v33              │
│                                                                         │
│  Пример: values-ru-sw600dp-land-night-v26                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Density Qualifiers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SCREEN DENSITIES                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Qualifier   │ DPI Range  │ Scale │ Пример устройства                  │
│  ────────────┼────────────┼───────┼────────────────────────────────────│
│  ldpi        │ ~120 dpi   │ 0.75x │ Редкие старые устройства            │
│  mdpi        │ ~160 dpi   │ 1x    │ Baseline (старые устройства)        │
│  hdpi        │ ~240 dpi   │ 1.5x  │ Nexus 5X                            │
│  xhdpi       │ ~320 dpi   │ 2x    │ Pixel 4a                            │
│  xxhdpi      │ ~480 dpi   │ 3x    │ Pixel 6, Samsung S21               │
│  xxxhdpi     │ ~640 dpi   │ 4x    │ Pixel 7 Pro, Samsung S23 Ultra     │
│                                                                         │
│  Формула: физический размер = dp × (dpi / 160)                         │
│                                                                         │
│  Пример: иконка 48dp                                                    │
│  mdpi:    48 × 1 = 48px                                                 │
│  hdpi:    48 × 1.5 = 72px                                               │
│  xhdpi:   48 × 2 = 96px                                                 │
│  xxhdpi:  48 × 3 = 144px                                                │
│  xxxhdpi: 48 × 4 = 192px                                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Smallest Width Qualifiers

```kotlin
// sw = Smallest Width — минимальная из ширины и высоты экрана

// values-sw320dp/  → Телефоны (большинство)
// values-sw600dp/  → Планшеты 7"
// values-sw720dp/  → Планшеты 10"
// values-sw840dp/  → Большие планшеты / настольные
```

```xml
<!-- res/values/dimens.xml (телефон) -->
<resources>
    <dimen name="content_padding">16dp</dimen>
    <integer name="grid_columns">2</integer>
</resources>

<!-- res/values-sw600dp/dimens.xml (планшет) -->
<resources>
    <dimen name="content_padding">32dp</dimen>
    <integer name="grid_columns">3</integer>
</resources>

<!-- res/values-sw720dp/dimens.xml (большой планшет) -->
<resources>
    <dimen name="content_padding">48dp</dimen>
    <integer name="grid_columns">4</integer>
</resources>
```

---

## R Class

AAPT2 генерирует R класс с идентификаторами всех ресурсов.

```kotlin
// Автогенерированный R класс (упрощённо)
public final class R {
    public static final class drawable {
        public static final int ic_launcher = 0x7f080001;
        public static final int button_background = 0x7f080002;
    }

    public static final class layout {
        public static final int activity_main = 0x7f0c0001;
        public static final int fragment_home = 0x7f0c0002;
    }

    public static final class string {
        public static final int app_name = 0x7f120001;
        public static final int welcome_message = 0x7f120002;
    }

    public static final class color {
        public static final int primary = 0x7f050001;
    }

    public static final class dimen {
        public static final int spacing_medium = 0x7f060001;
    }

    public static final class id {
        public static final int button_submit = 0x7f0a0001;
        public static final int text_title = 0x7f0a0002;
    }
}
```

### Доступ к ресурсам

```kotlin
// Строки
val appName = getString(R.string.app_name)
val formatted = getString(R.string.welcome_message, userName)

// Plurals
val count = resources.getQuantityString(R.plurals.notification_count, n, n)

// Цвета
val color = ContextCompat.getColor(context, R.color.primary)

// Размеры
val padding = resources.getDimensionPixelSize(R.dimen.spacing_medium)

// Drawables
val drawable = ContextCompat.getDrawable(context, R.drawable.ic_icon)

// Arrays
val countries = resources.getStringArray(R.array.countries)

// Integer
val columns = resources.getInteger(R.integer.grid_columns)

// Raw файлы
val inputStream = resources.openRawResource(R.raw.data)

// Идентификаторы
val view = findViewById<View>(R.id.button_submit)
```

### Non-Transitive R Classes

```kotlin
// gradle.properties
android.nonTransitiveRClass=true

// До (transitive):
// Каждый модуль видит R класс всех зависимых модулей
// R класс содержит все ресурсы из всех зависимостей
// Приводит к огромным R классам и медленной компиляции

// После (non-transitive):
// Каждый модуль видит только свои ресурсы
// Нужно явно импортировать R из зависимостей

// feature/home/src/main/kotlin/...
import com.example.core.ui.R as CoreR
import com.example.feature.home.R

class HomeFragment {
    fun setup() {
        // Локальный ресурс
        getString(R.string.home_title)

        // Ресурс из core:ui
        getColor(CoreR.color.primary)
    }
}
```

---

## Локализация

### Структура локализованных строк

```
res/
├── values/
│   └── strings.xml           # Язык по умолчанию (английский)
├── values-ru/
│   └── strings.xml           # Русский
├── values-uk/
│   └── strings.xml           # Украинский
├── values-de/
│   └── strings.xml           # Немецкий
├── values-es/
│   └── strings.xml           # Испанский
├── values-zh-rCN/
│   └── strings.xml           # Китайский (упрощённый, Китай)
├── values-zh-rTW/
│   └── strings.xml           # Китайский (традиционный, Тайвань)
├── values-pt-rBR/
│   └── strings.xml           # Португальский (Бразилия)
└── values-pt-rPT/
    └── strings.xml           # Португальский (Португалия)
```

### Форматирование строк

```xml
<!-- res/values/strings.xml -->
<resources>
    <!-- Простая строка -->
    <string name="hello">Hello</string>

    <!-- С форматированием -->
    <string name="welcome">Welcome, %1$s!</string>
    <string name="stats">%1$d files, %2$.2f MB</string>

    <!-- Plurals -->
    <plurals name="items">
        <item quantity="one">%d item</item>
        <item quantity="other">%d items</item>
    </plurals>

    <!-- HTML-форматирование -->
    <string name="styled">This is <b>bold</b> and <i>italic</i></string>

    <!-- Специальные символы -->
    <string name="apostrophe">It\'s a test</string>
    <string name="quotes">"Quoted text"</string>
    <string name="ampersand">Rock &amp; Roll</string>
    <string name="newline">First line\nSecond line</string>

    <!-- XLIFF для переводчиков -->
    <string name="greeting">
        Hello, <xliff:g id="name" example="John">%1$s</xliff:g>!
    </string>
</resources>

<!-- res/values-ru/strings.xml -->
<resources>
    <string name="hello">Привет</string>
    <string name="welcome">Добро пожаловать, %1$s!</string>

    <!-- Plurals с учётом русской грамматики -->
    <plurals name="items">
        <item quantity="one">%d элемент</item>
        <item quantity="few">%d элемента</item>
        <item quantity="many">%d элементов</item>
        <item quantity="other">%d элемента</item>
    </plurals>
</resources>
```

### Использование в коде

```kotlin
// Простая строка
val hello = getString(R.string.hello)

// С форматированием
val welcome = getString(R.string.welcome, userName)

// Plurals
val items = resources.getQuantityString(R.plurals.items, count, count)

// HTML строки
val styled = HtmlCompat.fromHtml(
    getString(R.string.styled),
    HtmlCompat.FROM_HTML_MODE_COMPACT
)

// Compose
@Composable
fun Greeting() {
    Text(text = stringResource(R.string.hello))
    Text(text = stringResource(R.string.welcome, userName))
    Text(text = pluralStringResource(R.plurals.items, count, count))
}
```

### Per-App Language (Android 13+)

```xml
<!-- res/xml/locales_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<locale-config xmlns:android="http://schemas.android.com/apk/res/android">
    <locale android:name="en"/>
    <locale android:name="ru"/>
    <locale android:name="de"/>
    <locale android:name="es"/>
</locale-config>

<!-- AndroidManifest.xml -->
<application
    android:localeConfig="@xml/locales_config">
</application>
```

```kotlin
// Программное переключение языка
val localeManager = context.getSystemService(LocaleManager::class.java)
localeManager.applicationLocales = LocaleList.forLanguageTags("ru")
```

---

## Resource Merging

При сборке ресурсы из разных источников объединяются.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       RESOURCE MERGING                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Приоритет (высший → низший):                                           │
│                                                                         │
│  1. Build Variant (src/devDebug/)                                       │
│  2. Build Type (src/debug/)                                             │
│  3. Product Flavor (src/dev/)                                           │
│  4. Main source set (src/main/)                                         │
│  5. Dependencies (библиотеки)                                           │
│  6. Generated resources                                                 │
│                                                                         │
│  Правила:                                                               │
│  • Файлы (png, xml layout) — заменяются полностью                      │
│  • values/*.xml — мержатся (элементы объединяются)                     │
│  • Конфликтующие элементы — выигрывает высший приоритет               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Переопределение ресурсов библиотеки

```xml
<!-- Библиотека определяет -->
<!-- library/res/values/strings.xml -->
<resources>
    <string name="lib_title">Library Title</string>
    <color name="lib_primary">#FF0000</color>
</resources>

<!-- Приложение переопределяет -->
<!-- app/res/values/strings.xml -->
<resources>
    <!-- Переопределяем с тем же именем -->
    <string name="lib_title">Custom Title</string>
    <color name="lib_primary">#0000FF</color>
</resources>
```

---

## Vector Drawables

### Преимущества Vector Drawables

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 VECTOR vs RASTER DRAWABLES                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Растровые (PNG):                                                       │
│  drawable-mdpi/icon.png     (48×48, 2KB)                               │
│  drawable-hdpi/icon.png     (72×72, 4KB)                               │
│  drawable-xhdpi/icon.png    (96×96, 6KB)                               │
│  drawable-xxhdpi/icon.png   (144×144, 10KB)                            │
│  drawable-xxxhdpi/icon.png  (192×192, 14KB)                            │
│  ИТОГО: 5 файлов, ~36KB                                                 │
│                                                                         │
│  Векторные (XML):                                                       │
│  drawable/icon.xml          (~1KB)                                      │
│  ИТОГО: 1 файл, ~1KB                                                    │
│                                                                         │
│  Преимущества:                                                          │
│  ✓ Один файл для всех плотностей                                       │
│  ✓ Меньший размер APK                                                   │
│  ✓ Масштабируется без потери качества                                  │
│  ✓ Можно анимировать (AnimatedVectorDrawable)                          │
│                                                                         │
│  Недостатки:                                                            │
│  ✗ Не подходит для сложных изображений (фото)                         │
│  ✗ Требует CPU для рендеринга (но кэшируется)                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Создание Vector Drawable

```xml
<!-- res/drawable/ic_arrow_back.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="?attr/colorControlNormal"
    android:autoMirrored="true">

    <path
        android:fillColor="@android:color/white"
        android:pathData="M20,11H7.83l5.59,-5.59L12,4l-8,8 8,8 1.41,-1.41L7.83,13H20v-2z"/>

</vector>
```

### Поддержка старых API

```kotlin
// build.gradle.kts
android {
    defaultConfig {
        vectorDrawables {
            useSupportLibrary = true
        }
    }
}
```

```xml
<!-- Использование с AppCompat -->
<ImageView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:srcCompat="@drawable/ic_arrow_back" />
```

---

## Оптимизация ресурсов

### Удаление неиспользуемых ресурсов

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isShrinkResources = true
            isMinifyEnabled = true  // Обязательно для shrinkResources
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}
```

### Сохранение нужных ресурсов

```xml
<!-- res/raw/keep.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools"
    tools:keep="@layout/activity_*,@drawable/ic_*"
    tools:discard="@layout/unused_*"
    tools:shrinkMode="strict" />
```

### Оптимизация изображений

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            // Конвертация PNG в WebP
            // (автоматически с AGP 4.1+)
        }
    }

    // Исключение плотностей
    defaultConfig {
        resourceConfigurations += listOf("en", "ru", "xxhdpi", "xxxhdpi")
    }
}
```

### APK Splits по плотности

```kotlin
android {
    splits {
        density {
            isEnable = true
            exclude("ldpi", "mdpi")
            compatibleScreens("normal", "large", "xlarge")
        }
    }
}
```

---

## Типичные ошибки

### 1. Hardcoded строки

```xml
<!-- ❌ ПЛОХО -->
<TextView android:text="Hello World" />

<!-- ✅ ПРАВИЛЬНО -->
<TextView android:text="@string/hello" />
```

### 2. Использование px вместо dp

```xml
<!-- ❌ ПЛОХО — разный размер на разных устройствах -->
<View android:layout_width="100px" />

<!-- ✅ ПРАВИЛЬНО — одинаковый физический размер -->
<View android:layout_width="100dp" />

<!-- ✅ Для текста используйте sp -->
<TextView android:textSize="16sp" />
```

### 3. Растровые иконки вместо векторных

```xml
<!-- ❌ ПЛОХО — нужно 5 файлов разного размера -->
<ImageView android:src="@drawable/ic_menu" />
<!-- drawable-mdpi/ic_menu.png
     drawable-hdpi/ic_menu.png
     drawable-xhdpi/ic_menu.png
     ... -->

<!-- ✅ ПРАВИЛЬНО — один векторный файл -->
<ImageView app:srcCompat="@drawable/ic_menu" />
<!-- drawable/ic_menu.xml (vector) -->
```

### 4. Дублирование ресурсов

```xml
<!-- ❌ ПЛОХО — одинаковые значения -->
<!-- values/colors.xml -->
<color name="button_text">#FFFFFF</color>
<color name="title_text">#FFFFFF</color>
<color name="header_bg">#FFFFFF</color>

<!-- ✅ ПРАВИЛЬНО — переиспользование -->
<color name="white">#FFFFFF</color>
<!-- Используйте @color/white везде -->
```

### 5. Неполная локализация

```
res/
├── values/
│   └── strings.xml      # 50 строк
└── values-ru/
    └── strings.xml      # 30 строк (неполная!)

# Результат: часть UI на английском, часть на русском
```

---

## Проверь себя

<details>
<summary>1. В каком порядке система выбирает ресурсы?</summary>

**Ответ:**
Система исключает папки, не соответствующие конфигурации устройства, в порядке приоритета квалификаторов (MCC → язык → ширина → плотность → ...). Из оставшихся выбирается наиболее специфичный.

Например, для устройства ru, xxhdpi:
1. values-ru-xxhdpi/ (если есть)
2. values-ru/ (если есть)
3. values-xxhdpi/ (если есть)
4. values/ (по умолчанию)

</details>

<details>
<summary>2. Почему нужен nonTransitiveRClass?</summary>

**Ответ:**
`nonTransitiveRClass=true` делает R класс локальным для каждого модуля:
1. **Меньший размер R класса** — содержит только ресурсы модуля
2. **Быстрее компиляция** — меньше кода для генерации
3. **Явные зависимости** — видно, откуда ресурс
4. **Изоляция** — изменения в одном модуле не влияют на R классы других

</details>

<details>
<summary>3. Когда использовать Vector Drawables, а когда растровые?</summary>

**Ответ:**
**Vector Drawables:**
- Иконки, логотипы, простые иллюстрации
- Когда нужна анимация (AnimatedVectorDrawable)
- Когда важен размер APK

**Растровые (PNG/WebP):**
- Фотографии
- Сложные изображения с градиентами и тенями
- Когда производительность критична (очень сложные vectors)

</details>

<details>
<summary>4. Как работает shrinkResources?</summary>

**Ответ:**
`shrinkResources = true` удаляет неиспользуемые ресурсы из APK:
1. Требует `minifyEnabled = true` (R8 должен удалить неиспользуемый код)
2. Анализирует код и находит используемые ресурсы
3. Удаляет остальные из финального APK
4. Можно настроить через `res/raw/keep.xml`

Важно: динамически загружаемые ресурсы (`getIdentifier()`) нужно явно указать в keep.xml.

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "strings.xml — единственный способ хранить строки" | strings.xml — recommended, но не единственный. Hardcoded strings в коде работают, но не поддерживают локализацию. Plurals требуют plurals.xml, arrays — arrays.xml |
| "Квалификаторы можно комбинировать как угодно" | Порядок квалификаторов фиксирован: mcc → mnc → language → layout → smallestWidth → width → height → size → density → etc. Нарушение порядка = ресурс не найден |
| "WebP всегда лучше PNG" | WebP эффективнее по размеру, но: decode медленнее, не поддерживается в VectorDrawable, некоторые старые версии библиотек не понимают. Для иконок — PNG или SVG → Vector |
| "Vector Drawables масштабируются бесплатно" | Vector Drawables требуют CPU для рендеринга при каждом изменении размера. Очень сложные vectors (много path) могут быть медленнее, чем pre-rendered PNG |
| "shrinkResources удалит всё неиспользуемое" | shrinkResources не может определить динамически загружаемые ресурсы (getIdentifier). Такие ресурсы нужно явно указать в keep.xml |
| "nonTransitiveRClass ломает совместимость" | nonTransitiveRClass — recommended practice. Да, требует explicit imports (R.string.xxx → com.lib.R.string.xxx), но улучшает build time и делает зависимости явными |
| "dimens.xml нужен для всех размеров" | dimens.xml нужен для: переиспользуемых размеров, размеров зависящих от density/configuration. Inline размеры (16dp) допустимы для одноразовых значений |
| "Локализация — это только strings" | Локализация включает: strings, plurals, drawables (RTL), layouts (разная длина текста), date/time formats, numbers, currencies. Полная локализация — комплексная задача |
| "Ресурсы компилируются как есть" | AAPT2 компилирует ресурсы в бинарный формат (.flat), оптимизирует, валидирует, генерирует R.java/R.class. XML → binary protobuf для быстрого парсинга |
| "Night theme автоматически меняет все цвета" | Night theme использует values-night/colors.xml. Если цвет не определён в night — используется default. Каждый цвет нужно явно адаптировать |

---

## CS-фундамент

| CS-концепция | Применение в Android Resources System |
|--------------|---------------------------------------|
| **Configuration Management** | Система ресурсов реализует configuration-based selection. Device configuration → matching resources. Позволяет адаптацию без изменения кода |
| **Fallback Strategy** | Best match → fallback to less specific → default. Гарантирует, что ресурс всегда найден, даже если exact match отсутствует |
| **Compile-time Resolution** | R.java генерируется при компиляции. Ошибки в ресурсах — compile errors, не runtime. Type-safe access к ресурсам |
| **Binary Serialization** | AAPT2 конвертирует XML в binary format (Protocol Buffers). Быстрее парсинг, меньше размер, эффективнее memory usage |
| **Content-based Addressing** | Resource IDs — integers, сгенерированные из имён. Позволяет fast lookup без string comparison |
| **Density Independence** | dp/sp — абстракция над пикселями. Система автоматически конвертирует в физические пиксели по density ratio |
| **Internationalization (i18n)** | Separation of content (strings) from code. BCP-47 language tags для идентификации локалей. ICU для форматирования |
| **Asset Pipeline** | Resources проходят через transformation pipeline: validation → compilation → optimization → packaging. Каждый этап оптимизирует output |
| **Namespace Isolation** | nonTransitiveRClass изолирует R class по модулям. Предотвращает conflicts и уменьшает compile scope |
| **Tree Shaking** | shrinkResources анализирует code references и удаляет unreachable resources. Dead code elimination для assets |

---

## Связь с другими темами

**[[android-compilation-pipeline]]** — AAPT2 (Android Asset Packaging Tool) компилирует ресурсы в бинарный формат на этапе сборки, генерирует R класс с ID ресурсов и выполняет resource merging из модулей и библиотек. Понимание compilation pipeline объясняет, почему R.id генерируется автоматически, как resource merging разрешает конфликты между модулями и почему изменение ресурса требует частичной пересборки. Без этого знания сложно диагностировать ошибки сборки связанные с ресурсами. Изучите compilation pipeline для системного понимания.

**[[android-ui-views]]** — система ресурсов тесно связана с View system: XML layouts определяют структуру UI, drawable ресурсы используются в View backgrounds, а dimension ресурсы задают размеры элементов. Понимание View system объясняет, как LayoutInflater парсит XML layouts в иерархию View, как qualifier system подбирает правильные ресурсы для разных конфигураций экрана, и почему Vector Drawable предпочтительнее растровых изображений. Ресурсы и View system — неразрывная пара.

**[[android-compose]]** — Compose использует ресурсы через функции stringResource(), painterResource(), dimensionResource(). Понимание того, как Compose интегрируется с системой ресурсов, помогает правильно использовать локализацию, тематизацию (MaterialTheme) и адаптивный дизайн. Compose также вводит собственные механизмы тем, дополняющие XML-based ресурсы.

**[[android-apk-aab]]** — ресурсы упаковываются в APK/AAB и составляют значительную часть размера приложения. AAB формат позволяет Play Store доставлять только нужные ресурсы для конкретного устройства (language splits, density splits), оптимизируя размер. Понимание ресурсной системы помогает правильно использовать App Bundle для уменьшения размера загрузки.

---

## Источники

- [App resources overview - Android Developers](https://developer.android.com/guide/topics/resources/providing-resources)
- [Providing alternative resources - Android Developers](https://developer.android.com/guide/topics/resources/providing-resources#AlternativeResources)
- [Localize your app - Android Developers](https://developer.android.com/guide/topics/resources/localization)
- [Vector drawables overview - Android Developers](https://developer.android.com/develop/ui/views/graphics/vector-drawable-resources)
- [Shrink, obfuscate, and optimize your app - Android Developers](https://developer.android.com/build/shrink-code)

---

## Источники и дальнейшее чтение

- Meier (2022). *Professional Android*. — полное покрытие ресурсной системы Android: типы ресурсов, qualifier matching algorithm, resource merging в multi-module проектах и оптимизация размера через App Bundle.
- Phillips et al. (2022). *Android Programming: The Big Nerd Ranch Guide*. — практические примеры работы с ресурсами: локализация, поддержка тёмной темы, адаптивные layouts и Vector Drawable.
- Vasavada (2019). *Android Internals*. — внутреннее устройство AAPT2, бинарный формат ресурсов в APK, R класс генерация и runtime resource resolution через AssetManager.

---

*Проверено: 2026-01-09 | На основе официальной документации Android*

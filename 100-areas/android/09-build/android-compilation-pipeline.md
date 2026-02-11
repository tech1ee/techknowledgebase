---
title: "Compilation Pipeline: от исходников до APK"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [compiler-design, intermediate-representation, bytecode, linking]
tags:
  - topic/android
  - topic/build-system
  - type/deep-dive
  - level/advanced
related:
  - "[[android-overview]]"
  - "[[android-gradle-fundamentals]]"
  - "[[android-proguard-r8]]"
  - "[[android-apk-aab]]"
  - "[[android-architecture]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-gradle-fundamentals]]"
  - "[[android-project-structure]]"
---

# Compilation Pipeline: от исходников до APK

Понимание того, как исходный код превращается в APK, помогает диагностировать проблемы сборки, оптимизировать время компиляции и понимать, что происходит под капотом Android.

> **Prerequisites:**
> - [[android-gradle-fundamentals]] — основы Gradle
> - [[android-architecture]] — ART и DEX формат
> - Базовое понимание компиляции

---

## Терминология

| Термин | Значение |
|--------|----------|
| **JVM Bytecode** | Байткод для Java Virtual Machine (.class файлы) |
| **DEX** | Dalvik Executable — байткод для Android Runtime |
| **D8** | Современный компилятор JVM bytecode → DEX |
| **R8** | D8 + shrinking + obfuscation + optimization |
| **AAPT2** | Android Asset Packaging Tool — компиляция ресурсов |
| **Desugaring** | Преобразование Java 8+ features для старых API |
| **Multidex** | Разбиение DEX на несколько файлов (>64K методов) |

---

## Обзор Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ANDROID COMPILATION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        SOURCE CODE                                 │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐  │ │
│  │  │ Kotlin  │  │  Java   │  │  AIDL   │  │    Resources        │  │ │
│  │  │  .kt    │  │  .java  │  │  .aidl  │  │  (XML, images)      │  │ │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └──────────┬──────────┘  │ │
│  └───────┼────────────┼────────────┼─────────────────┼──────────────┘ │
│          │            │            │                 │                │
│          ▼            ▼            ▼                 ▼                │
│  ┌───────────────────────────────────────┐  ┌─────────────────────┐   │
│  │           KOTLIN COMPILER              │  │       AAPT2         │   │
│  │           JAVA COMPILER                │  │  Resource Compiler  │   │
│  │           AIDL COMPILER                │  │                     │   │
│  └──────────────────┬────────────────────┘  └──────────┬──────────┘   │
│                     │                                   │              │
│                     ▼                                   ▼              │
│  ┌───────────────────────────────────────┐  ┌─────────────────────┐   │
│  │         JVM BYTECODE (.class)          │  │   Compiled Resources│   │
│  │                                        │  │   R.java generated  │   │
│  └──────────────────┬────────────────────┘  └──────────┬──────────┘   │
│                     │                                   │              │
│                     └───────────────┬───────────────────┘              │
│                                     │                                  │
│                                     ▼                                  │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    D8 / R8 COMPILER                                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │ │
│  │  │ Desugaring  │→│  Shrinking  │→│ Obfuscation │→│    DEX    │ │ │
│  │  │ (Java 8+)   │  │ (R8 only)  │  │ (R8 only)   │  │ Generation│ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │ │
│  └──────────────────────────────────────┬────────────────────────────┘ │
│                                         │                              │
│                                         ▼                              │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                      DEX FILES                                     │ │
│  │              classes.dex, classes2.dex, ...                        │ │
│  └──────────────────────────────────────┬────────────────────────────┘ │
│                                         │                              │
│                                         ▼                              │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    PACKAGING & SIGNING                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │ │
│  │  │  Merge       │→│   Zipalign   │→│        Sign APK           │ │ │
│  │  │  Resources   │  │              │  │  (v1, v2, v3, v4)        │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘ │ │
│  └──────────────────────────────────────┬────────────────────────────┘ │
│                                         │                              │
│                                         ▼                              │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                         APK / AAB                                  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Компиляция исходного кода

### Kotlin Compiler (kotlinc)

```kotlin
// Kotlin код компилируется в JVM bytecode

// 1. Фронтенд: парсинг, анализ типов
// 2. Генерация IR (Intermediate Representation)
// 3. Бэкенд: генерация .class файлов

// Пример: Data class
data class User(val id: String, val name: String)

// Генерирует:
// - User.class с полями, геттерами
// - equals(), hashCode(), toString(), copy()
// - componentN() для деструктуризации
```

### Java Compiler (javac)

```java
// Java код также компилируется в JVM bytecode
public class Utils {
    public static String format(String value) {
        return value.toUpperCase();
    }
}
// → Utils.class
```

### AIDL Compiler

```java
// IMyService.aidl
interface IMyService {
    void performAction(String input);
    String getResult();
}

// Генерирует:
// - IMyService.java (интерфейс)
// - IMyService.Stub (для реализации сервиса)
// - IMyService.Stub.Proxy (для клиента)
```

---

## AAPT2: компиляция ресурсов

AAPT2 (Android Asset Packaging Tool 2) работает в два этапа.

### Этап 1: Compile

```bash
# Компилирует отдельные ресурсы в .flat файлы
aapt2 compile res/values/strings.xml -o compiled/
# → compiled/values_strings.arsc.flat

aapt2 compile res/layout/activity_main.xml -o compiled/
# → compiled/layout_activity_main.xml.flat

aapt2 compile res/drawable/icon.png -o compiled/
# → compiled/drawable_icon.png.flat
```

### Этап 2: Link

```bash
# Связывает все .flat файлы в resources.arsc и генерирует R.java
aapt2 link compiled/*.flat \
    -I android.jar \
    --manifest AndroidManifest.xml \
    -o output.apk \
    --java gen/
# → resources.arsc (бинарная таблица ресурсов)
# → R.java (ID ресурсов)
```

### Структура R.java

```java
// Автогенерированный R.java
public final class R {
    public static final class layout {
        public static final int activity_main = 0x7f0b0001;
    }
    public static final class string {
        public static final int app_name = 0x7f0f0001;
        public static final int hello = 0x7f0f0002;
    }
    public static final class drawable {
        public static final int icon = 0x7f080001;
    }
    public static final class id {
        public static final int button_submit = 0x7f0a0001;
    }
}
```

### resources.arsc

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      resources.arsc structure                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    STRING POOL                                   │   │
│  │  "app_name", "Hello", "Submit", "activity_main", ...            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    PACKAGE CHUNK                                 │   │
│  │  Package ID: 0x7f                                                │   │
│  │  Package Name: com.example.myapp                                 │   │
│  │                                                                  │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │                TYPE SPECS                                  │  │   │
│  │  │  drawable: 3 entries                                       │  │   │
│  │  │  layout: 5 entries                                         │  │   │
│  │  │  string: 50 entries                                        │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  │                                                                  │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │                TYPE CHUNKS                                 │  │   │
│  │  │  string (default): {...}                                   │  │   │
│  │  │  string-ru: {...}                                          │  │   │
│  │  │  drawable-hdpi: {...}                                      │  │   │
│  │  │  drawable-xhdpi: {...}                                     │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## D8: DEX Compilation

D8 преобразует JVM bytecode в DEX формат, понятный Android Runtime.

### Зачем нужен DEX?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    JVM BYTECODE vs DEX                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  JVM Bytecode (.class):                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Stack-based VM                                                │   │
│  │  • Один класс = один файл                                        │   │
│  │  • Много дублирования (constant pools в каждом файле)           │   │
│  │  • Рассчитан на JIT компиляцию                                  │   │
│  │  • Размер: ~X байт                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  DEX Bytecode (.dex):                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Register-based VM (эффективнее на ARM)                       │   │
│  │  • Все классы в одном файле                                     │   │
│  │  • Единый string/type/method pool                               │   │
│  │  • Оптимизирован для мобильных устройств                        │   │
│  │  • Размер: ~0.5X байт (меньше!)                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Причина: Android изначально создавался для устройств с ограниченными  │
│  ресурсами — памятью, CPU, батареей.                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Desugaring

D8 поддерживает Java 8+ features на старых версиях Android.

```kotlin
// Код с Java 8 features
val list = listOf(1, 2, 3)
val doubled = list.stream()
    .map { it * 2 }
    .collect(Collectors.toList())

// Lambda выражения
val onClick = View.OnClickListener { view -> handleClick(view) }

// Method references
val formatter = items.map(String::uppercase)
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DESUGARING                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Java 8+ Feature          │ Min API │ Desugaring                       │
│  ─────────────────────────┼─────────┼───────────────────────────────── │
│  Lambda expressions       │ 26      │ Anonymous classes                │
│  Method references        │ 26      │ Synthetic methods                │
│  Default methods          │ 24      │ Synthetic static methods         │
│  Static interface methods │ 24      │ Companion classes                │
│  try-with-resources       │ 19      │ Try-finally blocks               │
│  Repeating annotations    │ 24      │ Container annotations            │
│  Stream API               │ 24      │ Backport library (coreLibrary)   │
│  java.time                │ 26      │ Backport library (coreLibrary)   │
│                                                                         │
│  coreLibraryDesugaring — полноценный backport API:                     │
│  - java.util.stream.*                                                   │
│  - java.time.*                                                          │
│  - java.util.function.*                                                 │
│  - java.util.Optional                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```kotlin
// build.gradle.kts — включение core library desugaring
android {
    compileOptions {
        isCoreLibraryDesugaringEnabled = true
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.3")
}
```

### Multidex

DEX формат имеет ограничение: 65,536 методов (64K) в одном файле.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MULTIDEX                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Проблема: DEX reference limit                                          │
│  • 16-bit index для методов → max 65,536 методов                       │
│  • 16-bit index для полей → max 65,536 полей                           │
│  • 16-bit index для типов → max 65,536 типов                           │
│                                                                         │
│  Крупные приложения легко превышают лимит:                              │
│  • AndroidX ~10K методов                                                │
│  • Firebase ~15K методов                                                │
│  • Google Play Services ~20K+ методов                                  │
│  • Kotlin stdlib ~7K методов                                            │
│                                                                         │
│  Решение: Multidex                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  classes.dex  (primary — загружается первым)                    │   │
│  │  classes2.dex (secondary)                                        │   │
│  │  classes3.dex (secondary)                                        │   │
│  │  ...                                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  minSdk >= 21: Multidex поддерживается нативно (ART)                   │
│  minSdk < 21: Требуется библиотека androidx.multidex                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```kotlin
// build.gradle.kts
android {
    defaultConfig {
        // Автоматически при minSdk >= 21
        minSdk = 21

        // Для minSdk < 21
        multiDexEnabled = true
    }
}

dependencies {
    // Только для minSdk < 21
    implementation("androidx.multidex:multidex:2.0.1")
}
```

```kotlin
// Для minSdk < 21: Application class
class MyApplication : MultiDexApplication() {
    // или
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(base)
        MultiDex.install(this)
    }
}
```

---

## D8 vs DX

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         D8 vs DX (Legacy)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DX (2008-2018):                                                        │
│  • Первый DEX компилятор                                                │
│  • Медленный                                                            │
│  • Большой output                                                       │
│  • Ограниченный desugaring                                              │
│  • Deprecated с AGP 3.1, удалён в 2021                                 │
│                                                                         │
│  D8 (2017+):                                                            │
│  • На 20% быстрее DX                                                    │
│  • Меньший размер DEX                                                   │
│  • Полный desugaring Java 8+                                           │
│  • Лучшая debug информация                                              │
│  • Default с AGP 3.1                                                    │
│                                                                         │
│  Timeline:                                                              │
│  • 2017: D8 preview                                                     │
│  • 2018: D8 default                                                     │
│  • 2019: DX deprecated                                                  │
│  • 2021: DX removed                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## R8: оптимизация и shrinking

R8 = D8 + code shrinking + obfuscation + optimization.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              R8                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     INPUT                                        │   │
│  │  .class files, .jar files, AAR libraries                        │   │
│  └──────────────────────────────────┬──────────────────────────────┘   │
│                                     │                                   │
│                                     ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  1. TREE SHAKING (Code Shrinking)                                │   │
│  │     • Удаление неиспользуемых классов                           │   │
│  │     • Удаление неиспользуемых методов                           │   │
│  │     • Удаление неиспользуемых полей                             │   │
│  └──────────────────────────────────┬──────────────────────────────┘   │
│                                     │                                   │
│                                     ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  2. OPTIMIZATION                                                 │   │
│  │     • Inlining методов                                          │   │
│  │     • Удаление мёртвого кода                                    │   │
│  │     • Constant propagation                                       │   │
│  │     • Devirtualization                                           │   │
│  └──────────────────────────────────┬──────────────────────────────┘   │
│                                     │                                   │
│                                     ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  3. OBFUSCATION                                                  │   │
│  │     • Переименование классов: com.example.MyClass → a.a.a       │   │
│  │     • Переименование методов: getData() → a()                   │   │
│  │     • Переименование полей: userName → a                        │   │
│  └──────────────────────────────────┬──────────────────────────────┘   │
│                                     │                                   │
│                                     ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  4. DEX GENERATION                                               │   │
│  │     • Конвертация в DEX bytecode                                │   │
│  │     • Desugaring                                                 │   │
│  └──────────────────────────────────┬──────────────────────────────┘   │
│                                     │                                   │
│                                     ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     OUTPUT                                       │   │
│  │  classes.dex + mapping.txt                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

Подробнее о R8 — в [[android-proguard-r8]].

---

## APK Packaging

### Структура APK

```
my-app.apk (ZIP archive)
├── AndroidManifest.xml      # Бинарный XML
├── classes.dex              # DEX bytecode
├── classes2.dex             # Multidex (если нужен)
├── resources.arsc           # Compiled resources table
├── res/
│   ├── drawable-hdpi-v4/
│   │   └── icon.png
│   ├── layout/
│   │   └── activity_main.xml  # Бинарный XML
│   └── ...
├── assets/                  # Raw assets
├── lib/
│   ├── arm64-v8a/
│   │   └── libnative.so
│   ├── armeabi-v7a/
│   │   └── libnative.so
│   └── x86_64/
│       └── libnative.so
├── META-INF/
│   ├── MANIFEST.MF          # JAR manifest
│   ├── CERT.SF              # Signature file
│   └── CERT.RSA             # Certificate
└── kotlin/                  # Kotlin metadata
    └── ...
```

### Zipalign

```bash
# Выравнивание несжатых данных по 4-байтовым границам
zipalign -v 4 input.apk output-aligned.apk

# Позволяет:
# • mmap() для прямого доступа к ресурсам
# • Меньше памяти при загрузке
# • Быстрее запуск приложения
```

### Signing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      APK SIGNING SCHEMES                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  v1 (JAR Signing):                                                      │
│  • Оригинальный метод (Android 1.0+)                                   │
│  • Подписывает каждый файл отдельно                                    │
│  • META-INF/MANIFEST.MF, *.SF, *.RSA                                   │
│  • Медленная верификация                                                │
│  • Можно модифицировать некоторые части APK                            │
│                                                                         │
│  v2 (APK Signature Scheme):                                             │
│  • Android 7.0+ (API 24)                                                │
│  • Подписывает весь APK целиком                                        │
│  • Быстрая верификация                                                  │
│  • Защита от модификации                                                │
│                                                                         │
│  v3 (APK Signature Scheme v3):                                          │
│  • Android 9.0+ (API 28)                                                │
│  • Key rotation support                                                 │
│  • Можно менять signing key без потери identity                        │
│                                                                         │
│  v4 (APK Signature Scheme v4):                                          │
│  • Android 11+ (API 30)                                                 │
│  • Инкрементальная установка (ADB)                                     │
│  • Streaming install                                                    │
│                                                                         │
│  Рекомендация: v1 + v2 + v3 (для максимальной совместимости)           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```kotlin
// build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file("../keystore/release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = "my-app"
            keyPassword = System.getenv("KEY_PASSWORD")

            // Включить все схемы подписи
            enableV1Signing = true
            enableV2Signing = true
            enableV3Signing = true
            enableV4Signing = true
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

---

## Gradle Tasks

### Ключевые задачи сборки

```bash
# Компиляция Kotlin
./gradlew :app:compileDebugKotlin

# Компиляция Java
./gradlew :app:compileDebugJavaWithJavac

# Генерация R класса
./gradlew :app:generateDebugRFile

# Обработка ресурсов (AAPT2)
./gradlew :app:processDebugResources

# DEX компиляция (D8)
./gradlew :app:dexBuilderDebug

# Merge DEX файлов
./gradlew :app:mergeDebugDex

# Упаковка APK
./gradlew :app:packageDebug

# Полная сборка
./gradlew :app:assembleDebug
```

### Цепочка зависимостей

```
assembleDebug
├── packageDebug
│   ├── mergeDebugAssets
│   ├── mergeDebugJniLibFolders
│   ├── mergeDebugNativeLibs
│   ├── stripDebugDebugSymbols
│   ├── mergeDebugResources
│   ├── processDebugResources
│   │   └── generateDebugRFile
│   ├── mergeDebugDex
│   │   └── dexBuilderDebug
│   │       └── compileDebugKotlin
│   │           └── compileDebugJavaWithJavac
│   └── validateSigningDebug
└── (sign)
```

---

## Оптимизация времени сборки

### Инкрементальная компиляция

```kotlin
// gradle.properties
# Kotlin incremental
kotlin.incremental=true

# Gradle incremental
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.configuration-cache=true
```

### Анализ времени сборки

```bash
# Build scan
./gradlew assembleDebug --scan

# Profile
./gradlew assembleDebug --profile

# Detailed timing
./gradlew assembleDebug --info
```

### Типичные bottlenecks

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BUILD TIME BOTTLENECKS                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Проблема                    │ Решение                                  │
│  ────────────────────────────┼──────────────────────────────────────── │
│  Kotlin compilation slow     │ K2 compiler, parallel compilation       │
│  KAPT slow                   │ Migrate to KSP                          │
│  Too many modules           │ Reduce module count, parallel build     │
│  Large resources            │ Shrink resources, use WebP              │
│  Configuration phase slow   │ Configuration cache                      │
│  No build cache             │ Enable local + remote cache             │
│  Slow tests                 │ Parallel tests, mock expensive deps     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

<details>
<summary>1. Зачем нужен DEX формат, почему не использовать обычный JVM bytecode?</summary>

**Ответ:**
DEX оптимизирован для мобильных устройств:
1. **Register-based VM** — эффективнее на ARM процессорах (меньше инструкций)
2. **Единый string/type/method pool** — меньше дублирования, компактнее
3. **Все классы в одном файле** — быстрее загрузка
4. **Меньший размер** — ~50% от эквивалентного JAR

Android изначально создавался для устройств с ограниченными ресурсами.

</details>

<details>
<summary>2. Что такое desugaring и зачем он нужен?</summary>

**Ответ:**
Desugaring — преобразование Java 8+ features в код, работающий на старых API:
- **Lambda** → anonymous class
- **Method reference** → synthetic method
- **Default methods** → static methods in companion
- **try-with-resources** → try-finally

Core Library Desugaring дополнительно backport-ит Stream API, java.time и другие библиотеки.

</details>

<details>
<summary>3. В чём разница между D8 и R8?</summary>

**Ответ:**
- **D8** — только DEX компиляция и desugaring. Используется для debug builds.
- **R8** — D8 + shrinking + obfuscation + optimization. Используется для release builds.

R8 объединяет в одном инструменте то, что раньше делали ProGuard + DX отдельно.

</details>

<details>
<summary>4. Что делает AAPT2?</summary>

**Ответ:**
AAPT2 (Android Asset Packaging Tool 2):
1. **Compile** — компилирует отдельные ресурсы в .flat файлы
2. **Link** — связывает все ресурсы в resources.arsc
3. **Генерирует R.java** — класс с ID ресурсов
4. **Компилирует XML** в бинарный формат
5. **Валидирует** ресурсы на ошибки

Инкрементальная компиляция: при изменении одного ресурса перекомпилируется только он.

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "DEX = JAR для Android" | DEX принципиально отличается: register-based VM vs stack-based, единый string/type pool, оптимизация для ARM. Это не просто другой формат, а другая архитектура |
| "R8 = ProGuard с другим именем" | R8 объединяет dexing + shrinking + optimization в одном проходе. ProGuard + D8 требовали двух проходов. R8 более агрессивен в оптимизациях |
| "Desugaring только для lambdas" | Desugaring включает: lambdas, method references, default interface methods, try-with-resources, и Core Library Desugaring (java.time, Streams) |
| "AAPT2 просто компилирует XML" | AAPT2 делает: validation, binary XML compilation, string pool generation, R.java generation, incremental compilation, resource linking |
| "65K method limit — история" | MultiDex встроен с API 21+, но понимание важно: D8 оптимизирует method count, R8 удаляет неиспользуемое. Мониторинг всё ещё полезен |
| "Debug build = Release без obfuscation" | Debug build: no R8/shrinking, debuggable=true, debug symbols, Timber logging, slower ART optimizations. Производительность может отличаться в 2-3x |
| "Resources не оптимизируются" | AAPT2 оптимизирует: binary XML compression, unused resource removal (с R8), string pool deduplication, resource table optimization |
| "Incremental build всегда быстрее" | Incremental build требует: правильную cache configuration, avoided full rebuilds, stable task inputs. Неправильная настройка может сделать хуже |
| "APK Analyzer — только для debugging" | APK Analyzer показывает: DEX method count, resource size breakdown, native libs, manifest analysis. Критичен для optimization |
| "Kotlin компилируется напрямую в DEX" | Kotlin → JVM bytecode → DEX. Kotlin compiler не знает о DEX. D8/R8 работают с .class файлами от Kotlin compiler |

---

## CS-фундамент

| CS-концепция | Применение в Compilation Pipeline |
|--------------|----------------------------------|
| **Multi-stage Compilation** | Kotlin → JVM bytecode → DEX. Каждый stage оптимизирует для своего target. Separation of concerns в compiler design |
| **Register vs Stack Machine** | JVM = stack-based (push/pop operands). DEX/ART = register-based (8-16 named registers). Register более эффективен на RISC (ARM) |
| **Dead Code Elimination** | R8 анализирует reachability от entry points. Unreachable code удаляется. Tree-shaking pattern |
| **Name Mangling** | Obfuscation переименовывает: classes (a, b, c), methods (a, b, c), fields. Dictionary-based или random. Reversible через mapping.txt |
| **Constant Folding** | R8 вычисляет константные выражения: `2 + 3` → `5`, string concatenation, enum ordinals. Compile-time evaluation |
| **Method Inlining** | R8 inline small methods: getter/setter, single-line methods. Eliminates call overhead. Trade-off: code size vs speed |
| **String Interning** | DEX string pool: все строки дедуплицированы и интернированы. `"hello"` появляется в DEX только один раз |
| **Resource Bundling** | AAPT2 creates resources.arsc: indexed lookup table для всех ресурсов. O(1) access по resource ID |
| **Incremental Compilation** | AAPT2 compile step обрабатывает файлы независимо. Только изменённые файлы перекомпилируются. Content-based invalidation |
| **Binary Serialization** | XML → binary protobuf (resources), Java bytecode → DEX bytecode. Compact, fast to parse, efficient to load |

---

## Связь с другими темами

**[[android-gradle-fundamentals]]** — Gradle управляет compilation pipeline через Android Gradle Plugin: каждый этап компиляции (kotlinc, KAPT/KSP, D8, R8, AAPT2, APK packaging) реализован как Gradle task. Понимание Gradle build lifecycle (configuration -> execution) объясняет, почему incremental compilation работает и как оптимизировать время сборки.

**[[android-proguard-r8]]** — R8 является частью compilation pipeline: после D8 dexing R8 выполняет shrinking (удаление неиспользуемого кода), obfuscation (переименование классов) и optimization (inlining, devirtualization). R8 работает на уровне DEX bytecode и может значительно уменьшить размер APK. Изучайте R8 после понимания общего pipeline.

**[[android-apk-aab]]** — APK/AAB являются конечным продуктом compilation pipeline. Понимание pipeline объясняет структуру APK: classes.dex (результат D8/R8), resources.arsc (результат AAPT2 link), lib/ (нативные библиотеки). AAB добавляет дополнительный этап — bundletool для генерации split APKs из module protobuf format.

**[[android-architecture]]** — ART runtime выполняет DEX bytecode, сгенерированный compilation pipeline. Pipeline оптимизирует код для ART: D8 desugaring поддерживает Java 8+ features на старых API levels, а Baseline Profiles направляют AOT-компиляцию в ART для ускорения startup.

**[[android-build-evolution]]** — эволюция систем сборки (Ant -> Maven -> Gradle) отражает усложнение compilation pipeline. Ant использовал dx (один DEX файл), Maven добавил dependency management, а Gradle с AGP принёс incremental compilation, multi-dex, R8 и AAB support.

---

## Источники и дальнейшее чтение

**Книги:**
- Vasavada N. (2019). Android Internals: A Confectioner's Cookbook. — внутреннее устройство Android: DEX формат, ART runtime, dex2oat компиляция на уровне ядра
- Meier R. (2022). Professional Android, 4th Edition. — комплексное руководство по Android-разработке, включая build process и compilation stages
- Leiva A. (2017). Kotlin for Android Developers. — Kotlin-first Android разработка, включая особенности компиляции Kotlin в DEX bytecode

**Веб-ресурсы:**
- [d8 - Android Developers](https://developer.android.com/tools/d8)
- [R8 shrinking - Android Developers](https://developer.android.com/build/shrink-code)
- [Configure your build - Android Developers](https://developer.android.com/build)
- [AAPT2 - Android Developers](https://developer.android.com/tools/aapt2)
- [Android App Bundle - Android Developers](https://developer.android.com/guide/app-bundle)
- [Next-generation Dex Compiler - Android Developers Blog](https://android-developers.googleblog.com/2017/08/next-generation-dex-compiler-now-in.html)

---

*Проверено: 2026-01-09 | Обновлено с 22 | На основе официальной документации Android*

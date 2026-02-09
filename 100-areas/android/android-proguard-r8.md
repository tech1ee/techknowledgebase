---
title: "Android ProGuard и R8: Code Shrinking, Obfuscation и Optimization"
created: 2025-01-15
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [dead-code-elimination, tree-shaking, name-mangling, bytecode-optimization]
tags:
  - topic/android
  - topic/build-system
  - topic/security
  - type/deep-dive
  - level/advanced
related:
  - "[[android-compilation-pipeline]]"
  - "[[android-apk-aab]]"
  - "[[android-gradle-fundamentals]]"
  - "[[android-build-evolution]]"
---

## Терминология

| Термин | Определение |
|--------|-------------|
| **Code Shrinking** | Удаление неиспользуемого кода (dead code elimination, tree shaking) |
| **Obfuscation** | Переименование классов, методов, полей в короткие нечитаемые имена |
| **Optimization** | Улучшение bytecode: inlining, constant propagation, devirtualization |
| **ProGuard** | Оригинальный инструмент shrinking/obfuscation (2002) |
| **R8** | Замена ProGuard от Google (2018), интегрирован с D8 |
| **Keep Rules** | Правила, указывающие какой код НЕ удалять/обфусцировать |
| **Mapping File** | Файл соответствия обфусцированных имён оригинальным |
| **Entry Points** | Точки входа в код (main, Activities, отражение) |
| **Tree Shaking** | Анализ графа вызовов и удаление недостижимого кода |
| **Reflection** | Динамический доступ к коду по имени (проблема для obfuscation) |

---

## Эволюция: ProGuard → R8

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ЭВОЛЮЦИЯ CODE PROCESSING                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  2002-2018: ProGuard Era                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  .class ──▶ ProGuard ──▶ .class ──▶ DX ──▶ .dex                    │    │
│  │             (shrink/     (optimized)                                │    │
│  │             obfuscate)                                              │    │
│  │                                                                     │    │
│  │  Проблема: два отдельных инструмента, двойная обработка            │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  2018-present: R8 Era                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  .class ──────────────▶ R8 ──────────────▶ .dex                    │    │
│  │                        (shrink +                                    │    │
│  │                         obfuscate +                                 │    │
│  │                         optimize +                                  │    │
│  │                         dexing)                                     │    │
│  │                                                                     │    │
│  │  Преимущество: единый pipeline, лучшая оптимизация                 │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Timeline

| Год | Событие |
|-----|---------|
| 2002 | ProGuard создан Eric Lafortune |
| 2008 | ProGuard интегрирован в Android SDK |
| 2014 | ProGuard 5.0 с поддержкой Java 8 |
| 2017 | Google анонсирует R8 |
| 2018 | R8 в preview (AGP 3.2) |
| 2019 | R8 по умолчанию (AGP 3.4) |
| 2020 | R8 Full Mode в preview |
| 2022 | R8 Full Mode по умолчанию (AGP 8.0) |
| 2024 | ProGuard deprecation в Android |

### Почему R8 заменил ProGuard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROGUARD VS R8 COMPARISON                            │
├───────────────────────┬───────────────────────┬─────────────────────────────┤
│      Критерий         │      ProGuard         │           R8                │
├───────────────────────┼───────────────────────┼─────────────────────────────┤
│ Архитектура           │ Отдельный инструмент  │ Интегрирован с D8           │
│ Входной формат        │ .class файлы          │ .class и .dex               │
│ Выходной формат       │ .class файлы          │ .dex напрямую               │
│ Скорость сборки       │ Медленнее (2 прохода) │ Быстрее (1 проход)          │
│ Размер APK            │ Базовый               │ ~10-15% меньше              │
│ Оптимизации           │ Базовые               │ Продвинутые                 │
│ Поддержка Kotlin      │ Ограниченная          │ Native support              │
│ Desugaring            │ Отдельно              │ Встроен                     │
│ Keep rules            │ ProGuard формат       │ Совместим + расширения      │
│ Разработчик           │ GuardSquare           │ Google                      │
└───────────────────────┴───────────────────────┴─────────────────────────────┘
```

---

## Включение R8

### Базовая конфигурация

```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        release {
            // Включить shrinking и obfuscation
            isMinifyEnabled = true

            // Включить resource shrinking (требует minifyEnabled)
            isShrinkResources = true

            // Файлы с keep rules
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }

        debug {
            // Обычно отключено для debug (быстрая сборка)
            isMinifyEnabled = false
        }
    }
}
```

### Встроенные ProGuard файлы

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ВСТРОЕННЫЕ PROGUARD КОНФИГУРАЦИИ                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  proguard-android.txt                                                       │
│  ├── Базовые правила для Android                                           │
│  ├── Keep для основных Android классов                                     │
│  └── БЕЗ оптимизаций (консервативный)                                      │
│                                                                             │
│  proguard-android-optimize.txt                                              │
│  ├── Всё из proguard-android.txt                                           │
│  ├── + Включены оптимизации                                                │
│  └── Рекомендуется для production                                          │
│                                                                             │
│  Расположение:                                                              │
│  $ANDROID_HOME/tools/proguard/                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### R8 Full Mode vs Compatibility Mode

```kotlin
// gradle.properties

// Compatibility Mode (default до AGP 8.0)
// Максимально совместим с ProGuard правилами
android.enableR8.fullMode=false

// Full Mode (default с AGP 8.0)
// Более агрессивные оптимизации
android.enableR8.fullMode=true
```

**Отличия Full Mode:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPATIBILITY VS FULL MODE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Compatibility Mode:                                                        │
│  ├── -dontshrink НЕ влияет на оптимизации                                  │
│  ├── Все default конструкторы сохраняются                                  │
│  ├── Enum.values() всегда сохраняется                                      │
│  └── Serializable поля автоматически keep                                  │
│                                                                             │
│  Full Mode:                                                                 │
│  ├── Более агрессивный tree shaking                                        │
│  ├── Default конструкторы удаляются если не используются                   │
│  ├── Оптимизация enum (могут стать int)                                    │
│  ├── Serializable требует явных keep rules                                 │
│  └── ~5-10% дополнительное уменьшение размера                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Три столпа R8

### 1. Code Shrinking (Tree Shaking)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TREE SHAKING PROCESS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Исходный код:                        После shrinking:                      │
│                                                                             │
│  ┌────────────────────┐               ┌────────────────────┐                │
│  │  MainActivity      │               │  MainActivity      │                │
│  │  ├── onCreate()    │──────────────▶│  ├── onCreate()    │                │
│  │  ├── onResume()    │    KEEP       │  ├── onResume()    │                │
│  │  └── helper()      │               │  └── helper()      │                │
│  └────────────────────┘               └────────────────────┘                │
│                                                                             │
│  ┌────────────────────┐               ┌────────────────────┐                │
│  │  UserRepository    │               │  UserRepository    │                │
│  │  ├── getUser()     │──────────────▶│  └── getUser()     │                │
│  │  ├── deprecated()  │    PARTIAL    │                    │                │
│  │  └── unused()      │               └────────────────────┘                │
│  └────────────────────┘                                                     │
│                                                                             │
│  ┌────────────────────┐                                                     │
│  │  LegacyUtils       │───────────────▶  УДАЛЁН (весь класс)               │
│  │  ├── oldMethod1()  │    REMOVE                                           │
│  │  └── oldMethod2()  │                                                     │
│  └────────────────────┘                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Как работает:**

```
Entry Points (keep rules)
         │
         ▼
┌─────────────────┐
│ Build Call Graph│ ──▶ Анализ всех вызовов из entry points
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Mark Reachable  │ ──▶ Пометить все достижимые классы/методы
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Remove Unmarked │ ──▶ Удалить всё что не помечено
└─────────────────┘
```

### 2. Obfuscation (Name Minification)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OBFUSCATION EXAMPLE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  До обфускации:                       После обфускации:                     │
│                                                                             │
│  package com.myapp.feature.user;     package a.b.c;                         │
│                                                                             │
│  class UserRepository {               class a {                             │
│      String userName;                     String a;                         │
│      int userAge;                         int b;                            │
│                                                                             │
│      User getUser(String id) {            b a(String a) {                   │
│          // ...                               // ...                        │
│      }                                    }                                  │
│                                                                             │
│      void updateProfile(                  void b(b a) {                     │
│          UserProfile profile              // ...                            │
│      ) {                                  }                                  │
│          // ...                       }                                      │
│      }                                                                       │
│  }                                                                           │
│                                                                             │
│  Результат:                                                                 │
│  • Меньше размер (короткие имена)                                          │
│  • Сложнее reverse engineering                                              │
│  • НЕ является защитой от профессионалов                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Что обфусцируется:**

| Элемент | Обфусцируется? | Почему |
|---------|----------------|--------|
| Имена классов | ✅ Да | Уменьшение размера, защита |
| Имена методов | ✅ Да | Уменьшение размера, защита |
| Имена полей | ✅ Да | Уменьшение размера |
| Имена пакетов | ✅ Да | Уменьшение размера |
| Строковые литералы | ❌ Нет | Нужны runtime |
| Имена ресурсов | ❌ Нет* | Связаны с R.java |
| Native методы | ❌ Нет | JNI binding |

### 3. Optimization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         R8 OPTIMIZATIONS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Method Inlining:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // До                          // После                            │   │
│  │  fun calculate() {              fun main() {                        │   │
│  │      return helper() + 1            // helper() заинлайнен          │   │
│  │  }                                  return (x * 2) + 1              │   │
│  │  fun helper() = x * 2           }                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. Constant Propagation:                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // До                          // После                            │   │
│  │  val DEBUG = false              // Весь if блок удалён              │   │
│  │  if (DEBUG) {                   doReleaseThing()                    │   │
│  │      log("debug")                                                   │   │
│  │  }                                                                  │   │
│  │  doReleaseThing()                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. Devirtualization:                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // До (virtual call)           // После (direct call)              │   │
│  │  interface Repo { fun get() }   // Если только одна реализация:     │   │
│  │  class RepoImpl : Repo          repoImpl.get() // прямой вызов      │   │
│  │  repo.get() // virtual call                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. Class Merging:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // До                          // После                            │   │
│  │  abstract class Base            class Merged {                      │   │
│  │  class Child : Base()               // поля и методы объединены     │   │
│  │                                 }                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  5. Enum Unboxing (Full Mode):                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // До                          // После (если возможно)            │   │
│  │  enum class State {             // State.LOADING = 0                │   │
│  │      LOADING, SUCCESS, ERROR    // State.SUCCESS = 1                │   │
│  │  }                              // State.ERROR = 2                  │   │
│  │  val state = State.LOADING      val state = 0                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Keep Rules: Синтаксис и Best Practices

### Базовый синтаксис

```proguard
# proguard-rules.pro

# ═══════════════════════════════════════════════════════════════════════════
# ОСНОВНЫЕ ДИРЕКТИВЫ
# ═══════════════════════════════════════════════════════════════════════════

# Keep класс и все его члены
-keep class com.example.MyClass { *; }

# Keep только класс (члены могут быть удалены/обфусцированы)
-keep class com.example.MyClass

# Keep члены если класс используется
-keepclassmembers class com.example.MyClass { *; }

# Keep класс и члены если класс используется
-keepclasseswithmembers class * {
    public <init>(android.content.Context);
}

# Keep имена (без shrinking, но с obfuscation)
-keepnames class com.example.MyClass

# ═══════════════════════════════════════════════════════════════════════════
# WILDCARDS
# ═══════════════════════════════════════════════════════════════════════════

# * - любая последовательность символов (не включая package separator)
-keep class com.example.* { *; }           # Только в com.example

# ** - любая последовательность символов (включая package separator)
-keep class com.example.** { *; }          # com.example и все подпакеты

# *** - любой тип (включая primitive и array)
-keep class * { *** myField; }

# % - любой primitive type
-keep class * { % myField; }

# ? - любой один символ
-keep class com.example.?lass { *; }       # Class, Blass, etc.

# ═══════════════════════════════════════════════════════════════════════════
# MEMBER SPECIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

# Все поля
-keep class * { <fields>; }

# Все методы
-keep class * { <methods>; }

# Конструкторы
-keep class * { <init>(...); }             # Все конструкторы
-keep class * { <init>(); }                # Только default конструктор
-keep class * { <init>(android.content.Context, android.util.AttributeSet); }

# Конкретные методы
-keep class * {
    public void onClick(android.view.View);
}

# По модификаторам
-keep class * {
    public *;                              # Все public члены
    public static *;                       # Все public static
    private <fields>;                      # Все private поля
}

# ═══════════════════════════════════════════════════════════════════════════
# CLASS SPECIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

# По наследованию
-keep class * extends android.app.Activity { *; }
-keep class * implements java.io.Serializable { *; }

# По аннотации
-keep @interface com.example.Keep
-keep @com.example.Keep class * { *; }
-keep class * {
    @com.example.Keep *;
}

# С конкретными членами
-keepclasseswithmembers class * {
    native <methods>;
}
```

### Разница между директивами

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      KEEP DIRECTIVES COMPARISON                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Директива                │ Shrinking │ Obfuscation │ Когда применять      │
│  ─────────────────────────┼───────────┼─────────────┼──────────────────────│
│  -keep                    │    ✗      │     ✗       │ Entry points, API    │
│  -keepnames               │    ✓      │     ✗       │ Reflection по имени  │
│  -keepclassmembers        │    ?      │     ✗       │ Члены если класс жив │
│  -keepclassmembernames    │    ?      │     ✗       │ Имена членов         │
│  -keepclasseswithmembers  │    ✗*     │     ✗       │ Класс с членами      │
│                                                                             │
│  ✓ = применяется                                                            │
│  ✗ = не применяется (код сохраняется)                                      │
│  ? = зависит от достижимости класса                                        │
│  ✗* = не применяется если члены существуют                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Типичные Keep Rules

```proguard
# proguard-rules.pro

# ═══════════════════════════════════════════════════════════════════════════
# ANDROID COMPONENTS (обычно не нужно - AGP добавляет автоматически)
# ═══════════════════════════════════════════════════════════════════════════

# Activities, Services, etc. из Manifest сохраняются автоматически!
# Но если динамическая регистрация:
-keep class * extends android.content.BroadcastReceiver

# ═══════════════════════════════════════════════════════════════════════════
# SERIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

# Java Serializable
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}

# Gson
-keepattributes Signature
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken

# Kotlinx Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class * {
    kotlinx.serialization.KSerializer serializer(...);
}

# Moshi
-keepclasseswithmembers class * {
    @com.squareup.moshi.* <methods>;
}
-keep @com.squareup.moshi.JsonQualifier interface *
-keepclassmembers @com.squareup.moshi.JsonClass class * extends java.lang.Enum {
    <fields>;
}

# ═══════════════════════════════════════════════════════════════════════════
# RETROFIT
# ═══════════════════════════════════════════════════════════════════════════

-keepattributes Signature, InnerClasses, EnclosingMethod
-keepattributes RuntimeVisibleAnnotations, RuntimeVisibleParameterAnnotations
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}
-dontwarn org.codehaus.mojo.animal_sniffer.IgnoreJRERequirement
-dontwarn javax.annotation.**
-dontwarn kotlin.Unit
-dontwarn retrofit2.KotlinExtensions
-dontwarn retrofit2.KotlinExtensions$*
-if interface * { @retrofit2.http.* <methods>; }
-keep,allowobfuscation interface <1>

# ═══════════════════════════════════════════════════════════════════════════
# ROOM
# ═══════════════════════════════════════════════════════════════════════════

-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-dontwarn androidx.room.paging.**

# ═══════════════════════════════════════════════════════════════════════════
# COROUTINES
# ═══════════════════════════════════════════════════════════════════════════

-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}

# ═══════════════════════════════════════════════════════════════════════════
# REFLECTION-BASED LIBRARIES
# ═══════════════════════════════════════════════════════════════════════════

# ViewBinding (если используете reflection)
-keep class * implements androidx.viewbinding.ViewBinding {
    public static *** bind(android.view.View);
    public static *** inflate(android.view.LayoutInflater);
}

# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES (для отладки - optional)
# ═══════════════════════════════════════════════════════════════════════════

# Keep data class toString() для логов (опционально)
-keepclassmembers class * {
    @kotlin.Metadata <methods>;
}

# ═══════════════════════════════════════════════════════════════════════════
# NATIVE METHODS
# ═══════════════════════════════════════════════════════════════════════════

-keepclasseswithmembernames class * {
    native <methods>;
}

# ═══════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════

-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# ═══════════════════════════════════════════════════════════════════════════
# PARCELABLE
# ═══════════════════════════════════════════════════════════════════════════

-keepclassmembers class * implements android.os.Parcelable {
    public static final ** CREATOR;
}
```

### Consumer ProGuard Rules (для библиотек)

```kotlin
// library/build.gradle.kts
android {
    defaultConfig {
        // Правила которые будут применены к приложению-потребителю
        consumerProguardFiles("consumer-rules.pro")
    }
}
```

```proguard
# library/consumer-rules.pro
# Эти правила автоматически добавятся в приложение

-keep public class com.mylib.PublicApi { *; }
-keep public interface com.mylib.PublicInterface { *; }
```

---

## Debugging Obfuscated Code

### Mapping File

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MAPPING FILE WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Build:                                                                     │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  R8 генерирует:                                                    │    │
│  │  app/build/outputs/mapping/release/mapping.txt                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                          │                                                  │
│                          ▼                                                  │
│  Содержимое mapping.txt:                                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  com.myapp.feature.UserRepository -> a.b.c.a:                      │    │
│  │      java.lang.String userName -> a                                │    │
│  │      int userAge -> b                                              │    │
│  │      void updateProfile(UserProfile) -> a                          │    │
│  │      User getUser(java.lang.String) -> b                           │    │
│  │  com.myapp.feature.User -> a.b.c.b:                                │    │
│  │      java.lang.String name -> a                                    │    │
│  │      int age -> b                                                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ВАЖНО: Сохраняйте mapping.txt для КАЖДОГО релиза!                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Retrace: Декодирование stack traces

```bash
# Использование retrace
# $ANDROID_HOME/tools/proguard/bin/retrace.sh

# Из файла
retrace.sh mapping.txt stacktrace.txt

# Интерактивно
retrace.sh mapping.txt
# Вставляем stack trace, Ctrl+D для обработки
```

**Пример:**

```
# Obfuscated stack trace:
java.lang.NullPointerException
    at a.b.c.a.b(Unknown Source:15)
    at a.b.c.d.a(Unknown Source:42)
    at a.b.c.e.onClick(Unknown Source:8)

# После retrace:
java.lang.NullPointerException
    at com.myapp.UserRepository.getUser(UserRepository.kt:15)
    at com.myapp.UserViewModel.loadUser(UserViewModel.kt:42)
    at com.myapp.UserFragment.onClick(UserFragment.kt:8)
```

### Firebase Crashlytics Integration

```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        release {
            // Crashlytics автоматически загружает mapping file
            firebaseCrashlytics {
                mappingFileUploadEnabled = true
            }
        }
    }
}
```

### Сохранение Line Numbers

```proguard
# proguard-rules.pro

# Сохранить номера строк для stack traces
-keepattributes SourceFile,LineNumberTable

# Опционально: скрыть имя исходного файла
-renamesourcefileattribute SourceFile
```

### Debug Build с R8

```kotlin
// Для отладки R8 проблем
android {
    buildTypes {
        debug {
            isMinifyEnabled = true  // Включить для тестирования
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

---

## Типичные проблемы и решения

### 1. Reflection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REFLECTION PROBLEM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Проблема:                                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  // Код использует reflection                                      │    │
│  │  val clazz = Class.forName("com.myapp.DynamicClass")              │    │
│  │  val method = clazz.getMethod("dynamicMethod")                     │    │
│  │                                                                    │    │
│  │  // R8 не видит эти вызовы → удаляет/обфусцирует класс            │    │
│  │  // Runtime: ClassNotFoundException или NoSuchMethodException      │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Решение:                                                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  # proguard-rules.pro                                              │    │
│  │  -keep class com.myapp.DynamicClass { *; }                         │    │
│  │                                                                    │    │
│  │  # Или через аннотацию:                                            │    │
│  │  @Keep                                                             │    │
│  │  class DynamicClass { ... }                                        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Serialization/Deserialization

```kotlin
// Проблема: JSON десериализация использует имена полей

// До R8:
data class User(
    val userName: String,  // JSON: {"userName": "John"}
    val userAge: Int
)

// После R8 (обфускация):
// userName → a
// userAge → b
// JSON {"userName": "John"} → не найдёт поле "userName"!

// Решения:

// 1. @SerializedName (Gson)
data class User(
    @SerializedName("userName") val userName: String,
    @SerializedName("userAge") val userAge: Int
)

// 2. @Json (Moshi)
data class User(
    @Json(name = "userName") val userName: String,
    @Json(name = "userAge") val userAge: Int
)

// 3. @SerialName (Kotlinx Serialization)
@Serializable
data class User(
    @SerialName("userName") val userName: String,
    @SerialName("userAge") val userAge: Int
)

// 4. Keep rule (менее предпочтительно)
// -keep class com.myapp.User { *; }
```

### 3. Missing Classes Warning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MISSING CLASS WARNINGS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Warning: com.example.SomeClass: can't find referenced class               │
│           javax.annotation.Nullable                                         │
│                                                                             │
│  Причины:                                                                   │
│  • Compile-only зависимость не включена в runtime                          │
│  • Опциональная зависимость библиотеки                                     │
│  • Разные версии библиотек                                                 │
│                                                                             │
│  Решения:                                                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  # Если класс действительно не нужен runtime:                      │    │
│  │  -dontwarn javax.annotation.**                                     │    │
│  │                                                                    │    │
│  │  # Или добавить зависимость:                                       │    │
│  │  implementation("com.google.code.findbugs:jsr305:3.0.2")          │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ВАЖНО: Не используйте -dontwarn * (подавляет ВСЕ предупреждения)         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. Kotlin Metadata

```proguard
# Проблема: Kotlin reflection не работает после R8

# Решение: сохранить Kotlin metadata
-keep class kotlin.Metadata { *; }
-keepattributes RuntimeVisibleAnnotations

# Для kotlin-reflect
-keep class kotlin.reflect.** { *; }
-keep class kotlin.** { *; }
```

### 5. Enum Problems

```kotlin
// Проблема: после R8 Full Mode enum может быть оптимизирован

enum class Status {
    LOADING, SUCCESS, ERROR
}

// R8 может превратить в int constants если:
// - Не используется name/ordinal
// - Не сериализуется
// - Не используется в reflection

// Решение если нужен enum:
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
    <fields>;
}
```

### 6. Service Loader

```proguard
# ServiceLoader использует META-INF/services
# R8 может удалить implementations

-keepnames class * implements com.myapp.MyServiceInterface
-keep class * implements com.myapp.MyServiceInterface {
    <init>();
}
```

### 7. JNI/Native Methods

```proguard
# Native методы вызываются из C/C++ по имени
# Имена нельзя обфусцировать

-keepclasseswithmembernames class * {
    native <methods>;
}

# Конкретный класс:
-keep class com.myapp.NativeHelper {
    native <methods>;
}
```

---

## R8 Advanced Configuration

### Aggressive Optimizations

```proguard
# proguard-rules.pro

# ═══════════════════════════════════════════════════════════════════════════
# AGGRESSIVE OPTIMIZATIONS (используйте осторожно!)
# ═══════════════════════════════════════════════════════════════════════════

# Удалить logging
-assumenosideeffects class android.util.Log {
    public static boolean isLoggable(java.lang.String, int);
    public static int v(...);
    public static int d(...);
    public static int i(...);
    public static int w(...);
    public static int e(...);
    public static int wtf(...);
}

# Удалить Kotlin assertions
-assumenosideeffects class kotlin.jvm.internal.Intrinsics {
    public static void check*(...);
    public static void throw*(...);
}

# Удалить Timber logging
-assumenosideeffects class timber.log.Timber {
    public static void v(...);
    public static void d(...);
    public static void i(...);
    public static void w(...);
    public static void e(...);
}

# Assume values (опасно!)
-assumevalues class com.myapp.BuildConfig {
    public static final boolean DEBUG return false;
}
```

### Resource Shrinking Configuration

```xml
<!-- res/raw/keep.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools"
    tools:keep="@layout/activity_used_dynamically,@drawable/*_icon"
    tools:discard="@layout/unused_layout"
    tools:shrinkMode="safe" />

<!--
shrinkMode:
  - safe: удаляет явно неиспользуемые (default)
  - strict: удаляет всё что не referenced напрямую
-->
```

### Baseline Profile Integration

```kotlin
// R8 использует baseline profiles для оптимизации
android {
    buildTypes {
        release {
            // Включить baseline profiles
            baselineProfile {
                automaticGenerationDuringBuild = true
            }
        }
    }
}
```

---

## Анализ результатов R8

### Build Output

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          R8 OUTPUT FILES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  app/build/outputs/                                                         │
│  ├── mapping/                                                               │
│  │   └── release/                                                           │
│  │       ├── mapping.txt        # Mapping обфусцированных имён             │
│  │       ├── seeds.txt          # Классы/члены сохранённые keep rules      │
│  │       ├── usage.txt          # Удалённый код                            │
│  │       └── configuration.txt  # Итоговая конфигурация R8                 │
│  │                                                                          │
│  └── apk/release/                                                          │
│      └── app-release.apk                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Анализ размера

```bash
# Сравнение размеров DEX
# До R8:
# classes.dex: 5.2 MB

# После R8:
# classes.dex: 2.1 MB (-60%)

# APK Analyzer в Android Studio:
# Build → Analyze APK...
```

### R8 Rules Report

```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        release {
            optimization {
                // Включить дополнительную диагностику
                keepRules {
                    // Генерировать файлы с информацией
                    ignoreExternalDependencies = false
                }
            }
        }
    }
}
```

---

## Real-world Case Studies

### Disney+ (30% Faster Startup)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DISNEY+ R8 OPTIMIZATION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Проблема:                                                                  │
│  • Большое приложение с множеством features                                │
│  • Медленный startup на low-end устройствах                                │
│  • Большой размер APK                                                       │
│                                                                             │
│  Решение:                                                                   │
│  • Включили R8 Full Mode                                                   │
│  • Агрессивный tree shaking                                                │
│  • Baseline Profiles + R8 оптимизации                                      │
│                                                                             │
│  Результаты:                                                                │
│  ┌───────────────────────┬───────────────┬───────────────┐                 │
│  │       Метрика         │     До R8     │   После R8    │                 │
│  ├───────────────────────┼───────────────┼───────────────┤                 │
│  │ Startup time          │   2.1 sec     │   1.5 sec     │ (-30%)          │
│  │ APK size              │   45 MB       │   32 MB       │ (-29%)          │
│  │ DEX count             │   8 files     │   3 files     │                 │
│  │ Method count          │   180K        │   95K         │ (-47%)          │
│  └───────────────────────┴───────────────┴───────────────┘                 │
│                                                                             │
│  Ключевые изменения:                                                       │
│  1. Перешли с compatibility на full mode                                   │
│  2. Удалили logging в release                                              │
│  3. Оптимизировали keep rules (убрали лишние)                              │
│  4. Использовали class merging                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Типичный Android App

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TYPICAL APP R8 RESULTS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Средний Android app после R8:                                             │
│                                                                             │
│  ┌───────────────────────┬───────────────┬───────────────┐                 │
│  │       Метрика         │     Debug     │    Release    │                 │
│  ├───────────────────────┼───────────────┼───────────────┤                 │
│  │ APK size              │   25 MB       │   8 MB        │ (-68%)          │
│  │ DEX size              │   12 MB       │   3 MB        │ (-75%)          │
│  │ Method count          │   85K         │   35K         │ (-59%)          │
│  │ Class count           │   12K         │   5K          │ (-58%)          │
│  └───────────────────────┴───────────────┴───────────────┘                 │
│                                                                             │
│  Breakdown удалённого кода:                                                │
│  • Unused library code: 40%                                                │
│  • Debug-only code: 15%                                                    │
│  • Dead application code: 10%                                              │
│  • Logging: 5%                                                             │
│  • Kotlin stdlib unused: 5%                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Anti-patterns и Best Practices

### Anti-patterns

```proguard
# ═══════════════════════════════════════════════════════════════════════════
# ANTI-PATTERNS (не делайте так!)
# ═══════════════════════════════════════════════════════════════════════════

# ❌ Keep всего приложения
-keep class com.myapp.** { *; }
# Результат: нет shrinking, нет obfuscation, бессмысленный R8

# ❌ Подавление всех warnings
-dontwarn **
# Результат: скрывает реальные проблемы

# ❌ Отключение всех оптимизаций
-dontoptimize
-dontshrink
-dontobfuscate
# Результат: зачем тогда R8?

# ❌ Keep всех data классов без разбора
-keep class * extends com.myapp.BaseModel { *; }
# Результат: утечка логики, больший размер

# ❌ Копирование правил из Stack Overflow без понимания
-keep class com.google.** { *; }
# Результат: keep библиотек которые и так работают
```

### Best Practices

```proguard
# ═══════════════════════════════════════════════════════════════════════════
# BEST PRACTICES
# ═══════════════════════════════════════════════════════════════════════════

# ✅ Начните с минимальных правил
# Добавляйте только если есть crash

# ✅ Используйте @Keep аннотацию вместо правил
@Keep
class ApiModel { ... }

# ✅ Используйте специфичные правила
-keep class com.myapp.api.models.User { *; }
# вместо
-keep class com.myapp.api.** { *; }

# ✅ Документируйте каждое правило
# Keep для Retrofit API interface
-keep interface com.myapp.api.UserService { *; }

# ✅ Регулярно проверяйте usage.txt
# Анализируйте что удаляется

# ✅ Тестируйте release build
# Не только debug!

# ✅ Используйте consumer rules в библиотеках
# Библиотека сама знает свои требования
```

### Checklist для Release Build

```
□ minifyEnabled = true
□ shrinkResources = true
□ proguard-android-optimize.txt используется
□ Все API models имеют @SerializedName или keep rules
□ Native методы защищены
□ Reflection-based код защищён
□ mapping.txt сохраняется для каждого релиза
□ Release build протестирован на реальном устройстве
□ Crashlytics mapping upload настроен
□ Warnings проанализированы (не подавлены)
```

---

## R8 vs ProGuard: Migration

### Миграция с ProGuard

```kotlin
// gradle.properties

// Если проблемы с R8, временно вернуться на ProGuard:
android.enableR8=false

// Для новых проектов - не нужно, R8 по умолчанию

// Если миграция с Full Mode даёт проблемы:
android.enableR8.fullMode=false
```

### Несовместимости правил

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PROGUARD → R8 INCOMPATIBILITIES                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ProGuard правило              R8 поведение                                │
│  ────────────────────────────────────────────────────────────────────────  │
│  -optimizations                Игнорируется (свои оптимизации)             │
│  -optimizationpasses           Игнорируется                                │
│  -mergeinterfacesaggressively  Другая реализация                          │
│  -overloadaggressively         Всегда включено                             │
│  -microedition                 Не поддерживается                           │
│  -verbose                      Поддержка частичная                        │
│                                                                             │
│  Обычно эти правила можно просто удалить                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

### Вопросы для самопроверки

1. **Что такое R8 и чем он отличается от ProGuard?**
   - R8 — unified pipeline от Google: shrinking + obfuscation + optimization + dexing в одном инструменте
   - ProGuard только shrinking/obfuscation, требует отдельный DX для dexing
   - R8 быстрее, лучше оптимизации, нативная поддержка Kotlin

2. **Какие три основные функции выполняет R8?**
   - Code Shrinking: удаление неиспользуемого кода
   - Obfuscation: переименование в короткие имена
   - Optimization: inlining, constant propagation, devirtualization

3. **Почему reflection проблема для R8?**
   - R8 анализирует код статически
   - Reflection использует имена классов/методов динамически (строки)
   - R8 не видит эти вызовы → удаляет/обфусцирует → ClassNotFoundException

4. **Что такое mapping.txt и зачем он нужен?**
   - Файл соответствия обфусцированных имён оригинальным
   - Нужен для декодирования crash stack traces
   - Должен сохраняться для каждого релиза

5. **Разница между Full Mode и Compatibility Mode?**
   - Full Mode: агрессивнее оптимизации, enum unboxing, требует точных keep rules
   - Compatibility: совместим с ProGuard правилами, консервативнее

6. **Как защитить data class для JSON сериализации?**
   - @SerializedName/@Json/@SerialName аннотации (предпочтительно)
   - Keep rules для класса и полей

7. **Что делать если release build crashes, а debug работает?**
   - Проверить mapping.txt и retrace stack trace
   - Добавить keep rule для проблемного класса
   - Проверить reflection, serialization, JNI

---

## Связи

- **[[android-compilation-pipeline]]** — R8 часть compilation pipeline (после D8)
- **[[android-apk-aab]]** — результаты R8 идут в APK/AAB
- **[[android-gradle-fundamentals]]** — конфигурация R8 в build.gradle
- **[[android-build-evolution]]** — эволюция от ProGuard к R8

---

## Источники

1. [R8 Official Documentation](https://developer.android.com/studio/build/shrink-code)
2. [ProGuard Manual](https://www.guardsquare.com/manual/home)
3. [R8 FAQ](https://r8.googlesource.com/r8/+/refs/heads/main/compatibility-faq.md)
4. [Shrinking Your App](https://developer.android.com/build/shrink-code)
5. [Disney+ Performance](https://medium.com/disney-streaming/how-disney-uses-android-app-performance-tuning-cb0f9c8b60d0)
6. [Jake Wharton on R8](https://jakewharton.com/r8-optimization-staticization/)
7. [Android Developers Blog: R8 Full Mode](https://android-developers.googleblog.com/2021/02/r8-full-mode-enabled-by-default.html)

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

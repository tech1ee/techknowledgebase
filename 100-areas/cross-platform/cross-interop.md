---
title: "Cross-Platform: Interop — Swift-ObjC vs Kotlin-Java"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - interop
  - swift
  - topic/jvm
  - objc
  - type/comparison
  - level/intermediate
---

# Языковая интероперабельность: Swift-ObjC vs Kotlin-Java

## TL;DR: Сравнительная таблица

| Аспект | Swift ↔ Objective-C | Kotlin ↔ Java |
|--------|---------------------|---------------|
| **Совместимость** | Двусторонняя через headers | Полная бинарная совместимость |
| **Механизм** | Bridging Header / -Swift.h | Прямой вызов JVM bytecode |
| **Дополнительные усилия** | @objc атрибуты, NS_SWIFT_NAME | @JvmStatic, @JvmOverloads |
| **Runtime** | ObjC Runtime для динамики | JVM — единый рантайм |
| **Миграция** | File-by-file | Statement-by-statement |
| **KMP → Swift** | SKIE, Swift Export | N/A — нативный |

---

## 1. Swift-Objective-C Interop

### Bridging Header: ObjC → Swift

```objc
// ProjectName-Bridging-Header.h
#import "LegacyNetworkManager.h"
#import <AFNetworking/AFNetworking.h>
```

```swift
// Swift — ObjC классы доступны напрямую
func fetchData() async throws -> [User] {
    try await withCheckedThrowingContinuation { continuation in
        legacyManager.fetchUsers { users, error in
            if let error { continuation.resume(throwing: error) }
            else { continuation.resume(returning: users ?? []) }
        }
    }
}
```

### @objc: Swift → ObjC

```swift
@objc(MYNetworkService)  // Кастомное ObjC имя
class NetworkService: NSObject {
    @objc var baseURL: String = "https://api.example.com"

    @objc func fetchUser(withId userId: String,
                         completion: @escaping (User?, Error?) -> Void) { }

    @objc func handleButtonTap(_ sender: UIButton) { }  // Для селектора
}
```

### Сценарий миграции: ObjC → Swift

```
1. Создать Bridging Header, добавить ObjC классы
2. Переписать файл на Swift с @objc для совместимости
3. Обновить ссылки в ObjC коде на -Swift.h
4. Удалить старый .m/.h файл
5. Убрать @objc где не нужна обратная совместимость
```

---

## 2. Kotlin-Java Interop

### Базовый интероп (работает из коробки)

```kotlin
// Kotlin — вызов Java напрямую
val javaHelper = JavaLegacyHelper()
val processed = javaHelper.processString(input)
val formatted = JavaUtils.formatDate(Date())
```

```java
// Java — вызов Kotlin
KotlinService service = new KotlinService();
Result result = service.processData("input");
ApiClient client = ApiClient.INSTANCE;  // object singleton
```

### @JvmStatic, @JvmOverloads, @JvmField

```kotlin
class Logger {
    companion object {
        @JvmStatic fun log(message: String) = println(message)
        @JvmField val TAG = "Logger"
    }
}

@JvmOverloads
fun show(title: String, message: String = "", priority: Int = 0) { }
```

```java
// Java — чистый синтаксис благодаря аннотациям
Logger.log("message");      // Без @JvmStatic: Logger.Companion.log()
String tag = Logger.TAG;    // Без @JvmField: Logger.Companion.getTAG()
show("Title");              // @JvmOverloads генерирует перегрузки
```

---

## 3. KMP: Kotlin-Swift Interop (SKIE, Swift Export)

### Проблема без SKIE

```kotlin
sealed class State {
    object Loading : State()
    data class Success(val data: List<Item>) : State()
}
```

```swift
// Swift без SKIE — нет exhaustive switch!
if state is StateLoading { } else if let s = state as? StateSuccess { }
```

### С SKIE — нативный Swift

```swift
switch onEnum(of: state) {
case .loading: showLoader()
case .success(let s): showItems(s.data)
}  // Компилятор проверяет все кейсы

// suspend → async/await
let items = try await repository.fetchItems()

// Flow → for-await
for await items in repository.observeItems() { self.items = items }
```

---

## 4. C/C++ Interop

### iOS: Swift ↔ C

```c
// MathLibrary.h
double calculate_distance(double x1, double y1, double x2, double y2);
```

```swift
// Swift — вызов C напрямую через Bridging Header
let distance = calculate_distance(0.0, 0.0, 100.0, 100.0)
```

### Android: Kotlin ↔ C через JNI

```cpp
extern "C" JNIEXPORT jstring JNICALL
Java_com_app_NativeLib_process(JNIEnv* env, jobject, jstring input) {
    const char* str = env->GetStringUTFChars(input, nullptr);
    // ...
    return env->NewStringUTF(result.c_str());
}
```

```kotlin
class NativeLib {
    init { System.loadLibrary("native-lib") }
    external fun process(input: String): String
}
```

---

## 5. Шесть типичных ошибок

### 1. Забыли @objc для селектора

```swift
// ❌ crash
button.addTarget(self, action: #selector(tap), for: .touchUpInside)
func tap() { }

// ✅
@objc func tap() { }
```

### 2. Nullable mismatch Java → Kotlin

```kotlin
// ❌ NPE
val name = javaApi.getUserName("123")  // platform type String!
textView.text = name.uppercase()

// ✅
val name: String? = javaApi.getUserName("123")
textView.text = name?.uppercase() ?: "Unknown"
```

### 3. Checked exceptions при экспорте Kotlin → Java

```kotlin
// ❌ Java не видит exception
fun saveConfig(content: String) { throw IOException() }

// ✅
@Throws(IOException::class)
fun saveConfig(content: String) { }
```

### 4. SKIE не настроен для sealed classes

```kotlin
// ❌ Swift видит классы без exhaustive switch
sealed class Result { }

// ✅ build.gradle.kts
skie { features { enableSealedEnums.set(true) } }
```

### 5. Companion без @JvmStatic

```kotlin
// ❌ Java: Logger.Companion.log()
companion object { fun log(msg: String) { } }

// ✅ Java: Logger.log()
companion object { @JvmStatic fun log(msg: String) { } }
```

### 6. Retain cycle в Swift-ObjC closure

```swift
// ❌ retain cycle
processor.complete { [self] result in self.handle(result) }

// ✅
processor.complete { [weak self] result in self?.handle(result) }
```

---

## 6. Три ментальные модели

### Модель 1: Уровни совместимости

```
Уровень 4: Идиоматичность  ← NS_SWIFT_NAME, SKIE, @JvmName
Уровень 3: Удобство        ← @JvmOverloads, nullability
Уровень 2: Доступность     ← @objc, @JvmStatic, bridging
Уровень 1: Бинарная        ← ABI, JVM bytecode, ObjC runtime

Kotlin-Java: стартуют с уровня 4
Swift-ObjC: требуют работы для уровней 2-3
KMP-Swift: SKIE поднимает 2→4
```

### Модель 2: Strangler Fig Migration

```
Legacy ███████████    →    Modern ░░░░░░░░░░░
       ██████████░░   →           ░░░░░░░░░░░░
       ████░░░░░░░░   →           ░░░░░░░░░░░░░
       ░░░░░░░░░░░░   →           ░░░░░░░░░░░░░░

Новый код обёртывает старый, постепенно вытесняя
```

### Модель 3: Interface-First

```
protocol Service { }
      ▲         ▲
      │         │
LegacyImpl  ModernImpl   ← Две реализации за одним интерфейсом
(ObjC/Java) (Swift/Kotlin)
```

---

## 7. Quiz: Проверь понимание

### Вопрос 1

Какой код сработает для `#selector`?

```swift
// A
func tap() { }
// B
@objc func tap() { }
// C
@objc private func tap() { }
```

<details><summary>Ответ</summary>
B и C. `#selector` требует `@objc`. `private` не влияет на доступность для селектора в том же классе.
</details>

### Вопрос 2

Как вызвать из Java?

```kotlin
class Logger { companion object { fun log(msg: String) { } } }
```

<details><summary>Ответ</summary>
`Logger.Companion.log("msg")`. Для `Logger.log()` нужен `@JvmStatic`.
</details>

### Вопрос 3

Что видит Swift без SKIE для Kotlin sealed class?

<details><summary>Ответ</summary>
Набор отдельных классов без exhaustive switch. С SKIE — enum с pattern matching.
</details>

---

## 8. Связанные материалы

- [[ios-swift-objc-interop]] — детальный разбор Swift-ObjC мостов
- [[cross-kmp-patterns]] — expect/actual и SKIE паттерны
- [[cross-concurrency-modern]] — async/await и coroutines интероп

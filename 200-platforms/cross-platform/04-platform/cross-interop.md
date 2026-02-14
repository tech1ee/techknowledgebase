---
title: "Cross-Platform: Interop — Swift-ObjC vs Kotlin-Java"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - interop
  - topic/swift
  - topic/jvm
  - objc
  - type/comparison
  - level/intermediate
reading_time: 13
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-memory-management]]"
related:
  - "[[ios-swift-objc-interop]]"
  - "[[kotlin-interop]]"
  - "[[ffi-foreign-function-interface]]"
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

## 8. Связь с другими темами

[[ios-swift-objc-interop]] — Swift-Objective-C интероп — критически важная тема для iOS-проектов с legacy-кодом. Заметка детально разбирает Bridging Header, Generated Interface (-Swift.h), @objc атрибуты, NS_SWIFT_NAME, nullability annotations и типы, которые не bridge-атся (Swift structs, enums with associated values, generics). Понимание этих механизмов необходимо для постепенной миграции ObjC-кодовой базы на Swift и для интеграции ObjC-библиотек в современные Swift-проекты.

[[kotlin-interop]] — Kotlin-Java интероп работает на уровне JVM bytecode, обеспечивая практически бесшовное взаимодействие. Заметка разбирает @JvmStatic, @JvmOverloads, @JvmField, @JvmName, @Throws и SAM conversions. Особое внимание уделено platform types (String!), nullable mappings и разнице в коллекциях (MutableList vs List). Эти знания необходимы для поддержки mixed Kotlin/Java проектов и для понимания, почему KMP-Java интероп проще, чем KMP-Swift.

[[ffi-foreign-function-interface]] — FFI охватывает низкоуровневое взаимодействие между языками: JNI (Java/Kotlin ↔ C/C++), Swift ↔ C через Bridging Header, cinterop в Kotlin/Native. Заметка объясняет calling conventions, memory marshalling, типовые маппинги и накладные расходы на пересечение языковых границ. Это фундаментальная тема для понимания того, как работает интероп под капотом — включая KMP iOS framework export через Objective-C headers.

---

## Источники и дальнейшее чтение

- Skeen J. et al. (2019). *Kotlin Programming: The Big Nerd Ranch Guide.* — Включает разделы о Kotlin-Java interop: @JvmStatic, @JvmOverloads, @JvmField, SAM conversions и platform types. Практические примеры вызова Java из Kotlin и наоборот, что является основой для понимания KMP interop.
- Neuburg M. (2023). *iOS Programming Fundamentals with Swift.* — Разбирает Swift-Objective-C мост: Bridging Header, @objc, NS_SWIFT_NAME, nullability annotations. Незаменима для понимания ограничений интеропа и стратегий миграции legacy ObjC-кода.
- Moskala M. (2021). *Effective Kotlin: Best Practices.* — Содержит рекомендации по проектированию Kotlin API, дружественного к Java-вызывающему коду, включая правильное использование аннотаций интеропа и обработку nullable типов.

---

## Проверь себя

> [!question]- Почему Kotlin-Java интероп работает почти бесшовно, а Swift-ObjC требует Bridging Header и аннотации? Какая техническая причина?
> Kotlin компилируется в JVM bytecode -- тот же формат, что и Java. JVM не различает код Kotlin и Java, оба работают с одними типами (java.lang.String, java.util.List). Swift и Objective-C имеют разные runtime: Swift использует metadata-based dispatch и value types (structs), ObjC -- message passing (objc_msgSend) и только reference types. Bridging Header создаёт маппинг между Swift и ObjC типами. Не все Swift-конструкции имеют ObjC-аналоги (generics, structs, enums with associated values), отсюда ограничения.

> [!question]- Сценарий: Kotlin sealed class экспортируется в iOS через KMP framework. Swift-код не может использовать exhaustive switch. Как решить?
> Kotlin sealed class экспортируется как ObjC class hierarchy (базовый + подклассы). ObjC не имеет exhaustive switch, поэтому Swift видит их как обычные классы без exhaustive pattern matching. Решения: 1) SKIE (Swift Kotlin Interface Enhancer) -- автоматически генерирует Swift enum wrappers для sealed classes, включая exhaustive switch. 2) Ручной маппинг: создать Swift enum и extension с функцией конвертации. SKIE предпочтительнее -- автоматизирует процесс и обновляется при изменении Kotlin кода.

> [!question]- Почему @JvmStatic, @JvmOverloads, @JvmField нужны в Kotlin при вызове из Java?
> Kotlin генерирует bytecode с конструкциями, которые не идиоматичны для Java: companion object создаёт inner class Companion (Java: MyClass.Companion.method()), default parameters не видны Java-вызывающему коду. @JvmStatic генерирует static method в Java-классе. @JvmOverloads создаёт перегрузки для default parameters. @JvmField убирает getter/setter, делая property прямым полем. Без аннотаций интероп работает, но неудобен для Java-потребителя.

---

## Ключевые карточки

Как работает Swift-Objective-C interop через Bridging Header?
?
Bridging Header (ProjectName-Bridging-Header.h) -- файл с #import ObjC headers, делающий ObjC-классы доступными в Swift. Обратное направление: Xcode генерирует ProjectName-Swift.h, экспортирующий @objc-помеченные Swift-классы в ObjC. Ограничения: Swift structs, enums с associated values, generics не экспортируются в ObjC.

Какие аннотации Kotlin улучшают Java-интероп?
?
@JvmStatic -- static method вместо Companion.method(). @JvmOverloads -- перегрузки для default parameters. @JvmField -- прямое поле без getter/setter. @JvmName -- переименование в bytecode (для конфликтов). @Throws -- добавляет throws в Java signature для checked exceptions. @JvmWildcard/@JvmSuppressWildcards -- контроль wildcards для generics.

Что такое SKIE и какие проблемы KMP-iOS интеропа он решает?
?
SKIE (Swift Kotlin Interface Enhancer) от Touchlab: автоматически генерирует Swift-friendly wrappers для Kotlin конструкций. Sealed class -> Swift enum с exhaustive switch. Suspend function -> Swift async function. Flow -> AsyncSequence. Default parameters -> Swift overloads. Без SKIE: sealed = loose classes, suspend = callback, Flow = ручной wrapper.

Чем platform types (String!) в Kotlin отличаются от nullable/non-null?
?
Platform types (T!) -- типы из Java, для которых Kotlin не знает nullability. Kotlin позволяет работать с ними и как с T, и как с T?. Опасность: если Java возвращает null, а Kotlin использует как non-null -- NullPointerException в runtime. Решение: nullability annotations в Java коде (@Nullable, @NonNull), или явная проверка в Kotlin.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-kmp-patterns]] | expect/actual и SKIE для KMP interop |
| Углубиться | [[ios-swift-objc-interop]] | Детальное погружение в Swift-ObjC bridging из раздела iOS |
| Смежная тема | [[ffi-foreign-function-interface]] | Низкоуровневый FFI: JNI, C interop из раздела CS Foundations |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |

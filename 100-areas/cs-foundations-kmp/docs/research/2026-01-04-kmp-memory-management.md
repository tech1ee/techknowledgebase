# Research Report: KMP Memory Management

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Kotlin/Native использует tracing GC (stop-the-world mark + concurrent sweep), который не разделяет heap на поколения. Новый memory manager (default с Kotlin 1.7.20) устранил freeze requirement и позволяет свободно шарить объекты между потоками. При iOS interop Kotlin GC работает совместно со Swift ARC — объекты освобождаются только во время GC, не сразу. Retain cycles между Kotlin и ObjC объектами не могут быть собраны автоматически — требуются weak references. autoreleasepool критичен для циклов с interop вызовами.

## Key Findings

### 1. Kotlin/Native GC Architecture

**Тип:** Stop-the-world mark + concurrent sweep (non-generational)

**Характеристики:**
- Объекты хранятся в shared heap, доступны из любого потока
- GC запускается на отдельном потоке по heuristics памяти или таймеру
- Mark phase может выполняться параллельно на нескольких потоках
- По умолчанию application threads приостанавливаются во время marking

**Memory Allocator:**
- Делит память на pages с независимым sweeping
- Каждый allocation = memory block внутри page
- Защита от spike'ов: если mutator аллоцирует быстрее GC — принудительный stop-the-world

### 2. New Memory Manager (Kotlin 1.7.20+)

**Ключевые изменения:**
| Старая модель | Новая модель |
|---------------|--------------|
| freeze() для sharing между потоками | Свободный sharing |
| @SharedImmutable для top-level | Не требуется |
| AtomicReference требует freeze | Работает без freeze |
| Reference cycles с AtomicReference = утечка | Нет утечек |

**Удалённые API:**
- `freeze()`, `isFrozen`, `ensureNeverFrozen()`
- `FreezingException`, `InvalidMutabilityException`
- `@SharedImmutable`
- `atomicLazy()` → используй `lazy()`

### 3. iOS Interop: Kotlin GC + Swift ARC

**Как работает:**
- Kotlin: tracing GC
- Objective-C/Swift: ARC (reference counting)
- Интеграция: объекты освобождаются только во время GC, не сразу

**Критическая проблема — Retain Cycles:**
```
Kotlin.A ←→ ObjC.B ←→ Kotlin.C
```
Если цикл содержит хотя бы один ObjC объект — **не может быть собран!**

**Решение:** weak/unowned references в Swift коде

### 4. autoreleasepool Usage

**Проблема:** Долгие циклы с interop вызовами накапливают temporary objects.

**Признак:** В GC логах "stable refs in root set" растёт.

**Решение:**
```kotlin
// Плохо — память растёт
fun badLoop() {
    repeat(Int.MAX_VALUE) { NSLog("$it\n") }
}

// Хорошо — память стабильна
fun goodLoop() {
    repeat(Int.MAX_VALUE) {
        autoreleasepool { NSLog("$it\n") }
    }
}
```

### 5. GC Tuning Parameters

| Параметр | Назначение |
|----------|------------|
| `kotlin.native.binary.gc=cms` | Experimental concurrent marking |
| `kotlin.native.binary.gc=noop` | Отключить GC (только для тестов) |
| `kotlin.native.binary.gcMarkSingleThreaded=true` | Single-threaded marking |
| `-Xruntime-logs=gc=info` | Включить GC логирование |
| `kotlin.native.binary.appStateTracking=enabled` | Отключить timer GC в background |

**Ручной запуск:**
```kotlin
kotlin.native.internal.GC.collect()
```

### 6. Performance Considerations

**K/N GC vs Swift ARC:**
- ARC освобождает объекты немедленно
- K/N GC освобождает объекты периодически
- Compose Multiplatform UI может иметь больший memory footprint чем SwiftUI
- K/N GC обрабатывает циклические ссылки, ARC — нет

**Оптимизации:**
- IntArray вместо List<Int> — до 40% speedup
- Inline functions — уменьшает GC pressure
- Минимизировать object creation в tight loops

### 7. Debugging & Monitoring

**GC Logging:**
```kotlin
// gradle.properties
kotlin.native.binary.gcLogLevel=info
```

**Memory Leak Detection:**
```kotlin
@OptIn(ExperimentalStdlibApi::class)
fun getUsage(): Long {
    GC.collect()
    return GC.lastGCInfo!!.memoryUsageAfter["heap"]!!.totalObjectsSizeBytes
}

@Test
fun testNoLeak() {
    val before = getUsage()
    // test code
    val after = getUsage()
    assertEquals(before, after)
}
```

**Xcode Instruments:**
```properties
# gradle.properties
kotlin.native.binary.enableSafepointSignposts=true
kotlin.native.binary.mmapTag=246
```

### 8. Real-World: Netflix Case Study

Netflix использует KMP для Studio apps (физическое производство Film & TV):
- Первая FAANG компания с KMP в production
- Ktor HttpClient для networking
- SQLDelight для disk caching
- Hendrix SDK для rule interpretation
- xcode-kotlin plugin для debugging в Xcode

## Community Sentiment

### Positive
- Новый memory manager значительно упрощает код
- Не нужен freeze — objects свободно шарятся
- GC обрабатывает циклические ссылки автоматически
- Netflix, McDonald's, Cash App успешно используют в production
- ~40% efficiency gains при sharing бизнес-логики

### Negative / Concerns
- Memory footprint выше чем чистый Swift с ARC
- GC pauses могут влиять на UI animations
- iOS extensions с ограничением RAM (50MB) — GC может не успевать
- UIImage и heavy objects требуют особой осторожности
- Retain cycles на границе K/N-Swift требуют manual weak references

### Controversial
- Compose Multiplatform vs SwiftUI для UI: trade-off между code sharing и memory control

## Common Mistakes

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Retain cycle K/N ↔ ObjC | Memory leak | weak references в Swift |
| Цикл без autoreleasepool | Memory growth | Wrap interop calls |
| Использование старого native-mt | Проблемы с новым MM | kotlinx.coroutines 1.6.0+ |
| GC в background drain battery | Battery drain | appStateTracking=enabled |
| UIImage в Kotlin | Memory spike | Обрабатывать на Swift стороне |

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Kotlin/Native Memory Manager](https://kotlinlang.org/docs/native-memory-manager.html) | Official | ★★★★★ | Authoritative |
| 2 | [ARC Integration](https://kotlinlang.org/docs/native-arc-integration.html) | Official | ★★★★★ | iOS interop |
| 3 | [Migration Guide](https://kotlinlang.org/docs/native-migration-guide.html) | Official | ★★★★★ | Migration |
| 4 | [DEV.to XCFramework](https://dev.to/arsenikavalchuk/memory-management-and-garbage-collection-in-kotlin-multiplatform-xcframework-15pa) | Blog | ★★★★☆ | Practical |
| 5 | [Droidcon GC Part 1](https://www.droidcon.com/2024/09/20/garbage-collector-in-kmp-part-1/) | Conference | ★★★★☆ | Deep dive |
| 6 | [Droidcon GC Part 2](https://www.droidcon.com/2024/09/24/garbage-collector-in-kmp-part-2/) | Conference | ★★★★☆ | iOS focus |
| 7 | [Touchlab Netflix](https://touchlab.co/netflix-kotlin-multiplatform) | Blog | ★★★★☆ | Case study |
| 8 | [Kotlin Discussions](https://discuss.kotlinlang.org/) | Forum | ★★★☆☆ | Real issues |

## Research Methodology

- **Queries used:** 8 search queries
- **Sources found:** 30+ total
- **Sources used:** 25 (after quality filter)
- **WebFetch deep reads:** 5 articles
- **Focus areas:** GC internals, ARC integration, retain cycles, migration, performance


---

*Проверено: 2026-01-09*

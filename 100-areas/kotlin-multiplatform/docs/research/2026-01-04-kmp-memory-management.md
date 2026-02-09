# Research Report: KMP Memory Management

**Date:** 2026-01-04
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

Kotlin/Native использует tracing GC (stop-the-world mark + concurrent sweep), Swift использует ARC. Интеграция автоматическая, но mixed retain cycles (Kotlin + Obj-C objects) не собираются! Для loops с interop используй autoreleasepool. GC мониторинг через `-Xruntime-logs=gc=info` и Xcode Instruments signposts. Новый memory manager (default с Kotlin 1.7.20) убрал freeze() — объекты можно шарить между threads свободно.

## Key Findings

1. **GC Algorithm**
   - Stop-the-world mark + concurrent sweep
   - No generational separation
   - Parallel marking on multiple threads
   - Triggered by memory pressure or timer
   - Can be called manually: GC.collect()

2. **Swift/Objective-C ARC Integration**
   - Objects wrapped in DisposableHandle when passed to Swift
   - ARC manages Swift side, GC manages Kotlin side
   - Deinitializers run on main thread (or GC thread)
   - Mixed retain cycles CANNOT be collected!

3. **Common Memory Issues**
   - Retain cycles: use weak/unowned references
   - Long-lived interop objects: use autoreleasepool
   - UIImage passing: can cause rapid memory growth
   - Constants from Kotlin in Swift: potential leaks off main thread

4. **Monitoring Tools**
   - -Xruntime-logs=gc=info for GC logging
   - Xcode Instruments with signposts
   - GC.lastGCInfo for memory tracking
   - enableSafepointSignposts for iOS debugging

5. **Optimization Options**
   - kotlin.native.binary.gc=cms (concurrent marking)
   - kotlin.native.binary.pagedAllocator=false (reduce startup memory)
   - kotlin.native.binary.latin1Strings=true (smaller strings)
   - kotlin.native.binary.appStateTracking=enabled (background apps)

## Community Sentiment

### Positive
- New memory model eliminates freeze() complexity
- Automatic interop with ARC mostly works
- Good tooling for monitoring (Instruments)
- Continuous improvements in each Kotlin version

### Negative
- Mixed retain cycles are a real problem
- Some reported memory leaks with Ktor Darwin
- UIImage handling can be problematic
- Constants usage off main thread can leak

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Native Memory Manager](https://kotlinlang.org/docs/native-memory-manager.html) | Official | 0.95 | Complete GC docs |
| 2 | [ARC Integration](https://kotlinlang.org/docs/native-arc-integration.html) | Official | 0.95 | Swift interop |
| 3 | [GC in KMP Part 2](https://www.droidcon.com/2024/09/24/garbage-collector-in-kmp-part-2/) | Blog | 0.85 | Practical insights |
| 4 | [Memory Management XCFramework](https://dev.to/arsenikavalchuk/memory-management-and-garbage-collection-in-kotlin-multiplatform-xcframework-15pa) | Blog | 0.85 | XCFramework specifics |
| 5 | [Memory Update Blog](https://blog.jetbrains.com/kotlin/2021/05/kotlin-native-memory-management-update/) | Official | 0.90 | New model rationale |

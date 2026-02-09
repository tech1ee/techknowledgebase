# Research Report: KMP Web/WASM

**Date:** 2026-01-05
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Kotlin/WASM и Compose for Web достигли Beta (сентябрь 2025). Safari поддержал WasmGC (декабрь 2024), все major browsers теперь совместимы. Performance: WASM ~3x быстрее JS в UI-heavy сценариях. Для sharing logic only — Kotlin/JS лучше (лучший interop). Для shared UI — Kotlin/WASM + Compose MP. Production apps: Kotlin Playground, KotlinConf app, Rijksmuseum. Interop через external declarations, @JsFun, JsAny type (не dynamic).

## Key Findings

### 1. Platform Status (January 2026)

| Component | Status | Notes |
|-----------|--------|-------|
| Kotlin/WASM | Beta | Since Kotlin 2.x |
| Kotlin/JS | Stable | Production-ready |
| Compose for Web | Beta | Since September 2025 (CMP 1.9) |
| WasmGC browser support | 100% | Safari added December 2024 |

### 2. When to Use What

**Kotlin/JS — Best for:**
- Sharing business logic only
- Native HTML/CSS/JavaScript UI
- Complex JS library interop
- Older browser support required
- Smaller bundle size needed

**Kotlin/WASM — Best for:**
- Sharing UI across platforms
- Performance-critical applications
- Smooth animations
- Modern browsers only acceptable

### 3. Performance Benchmarks

| Metric | Kotlin/JS | Kotlin/WASM |
|--------|-----------|-------------|
| Execution speed | Baseline | ~3x faster |
| UI rendering | Slower | Near-native |
| Startup time | Faster | Slightly slower (WASM loading) |
| Bundle size | Larger (stdlib) | Smaller binary |

**Google Chrome benchmarks:** Kotlin/Wasm approaching JVM performance

### 4. JavaScript Interop

**Key mechanisms:**
- `external` declarations for global scope access
- `@JsFun` annotation for inline JS code
- `JsAny` type (replaces `dynamic` from Kotlin/JS)
- kotlinx-browser library for DOM API

**Example:**
```kotlin
// External declaration
external val window: Window
external val document: Document

// @JsFun for small JS code
@JsFun("(x) => console.log(x)")
external fun log(message: String)

// JsAny for untyped values
fun processJsValue(value: JsAny) { ... }
```

**Differences from Kotlin/JS:**
- No `dynamic` type support
- Stricter type system with JsAny
- Some different behavior in interop edge cases

### 5. Browser Compatibility

| Browser | WasmGC Support | Fallback Available |
|---------|----------------|-------------------|
| Chrome | ✅ | Yes (JS) |
| Firefox | ✅ | Yes (JS) |
| Safari | ✅ (Dec 2024) | Yes (JS) |
| Edge | ✅ | Yes (JS) |
| Older browsers | ❌ | Compatibility mode |

**Compatibility mode:** Build for both wasmJs and js targets, automatic fallback

### 6. Current Limitations

**Library support:**
- Okio doesn't support WASM
- Reflection limited in common modules
- Some KType operations unavailable

**Runtime behavior:**
- Some JVM code crashes on WASM (casting differences)
- Missing fonts in Compose for Web
- Hot reloading issues reported

**Development:**
- IntelliJ debugging requires 2025.3 EAP
- Custom formatters enabled by default since Kotlin 2.1.20

### 7. Production Apps

| App | Type | Notes |
|-----|------|-------|
| Kotlin Playground | Tool | Full Kotlin/WASM |
| KotlinConf App | Conference | Web version |
| Rijksmuseum Demo | Museum | Compose for Web |

### 8. Upcoming Features

- Multithreading support for WASM
- Multiple WebAssembly modules (lazy loading)
- Improved accessibility
- Native HTML element interop

## Community Sentiment

### Positive
- Performance is impressive (~3x faster than JS)
- Safari support completed the browser matrix
- Beta status shows maturity
- Real production apps exist

### Negative / Concerns
- Bundle size still larger than handwritten JS
- Limited library ecosystem for WASM
- Debugging experience improving but not perfect
- Some reflection limitations

### Mixed
- Kotlin/JS vs WASM choice not always clear
- Compatibility mode adds complexity
- Early adopter territory

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Kotlin/Wasm Overview](https://kotlinlang.org/docs/wasm-overview.html) | Official | ★★★★★ | Main docs |
| 2 | [CMP 1.9 Release Blog](https://blog.jetbrains.com/kotlin/2025/09/compose-multiplatform-1-9-0-compose-for-web-beta/) | Official | ★★★★★ | Beta announcement |
| 3 | [Present and Future of Kotlin for Web](https://blog.jetbrains.com/kotlin/2025/05/present-and-future-kotlin-for-web/) | Official | ★★★★★ | Roadmap |
| 4 | [JS Interop Docs](https://kotlinlang.org/docs/wasm-js-interop.html) | Official | ★★★★★ | Interop guide |
| 5 | [Touchlab WASM Interop](https://touchlab.co/kotlin-wasm-js-interop) | Expert | ★★★★☆ | Practical examples |
| 6 | [KMPShip WASM Guide](https://www.kmpship.app/blog/kotlin-wasm-and-compose-web-2025) | Community | ★★★★☆ | 2025 overview |

## Research Methodology

- **Queries used:** 5 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **Focus areas:** Status, performance, interop, limitations


---

*Проверено: 2026-01-09*

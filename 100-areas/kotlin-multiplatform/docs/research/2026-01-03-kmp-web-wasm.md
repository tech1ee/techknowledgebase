---
title: "Research Report: KMP Web/Wasm"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Web/Wasm

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

Kotlin/Wasm (Beta) компилирует Kotlin в WebAssembly с ~3x лучшей performance чем JS в UI scenarios. С декабря 2024 все major browsers поддерживают WasmGC (Safari был последним). Compose Multiplatform Web достиг Beta в сентябре 2025 с Canvas-based rendering. webMain source set (K 2.2.20+) объединяет js и wasmJs targets. Compatibility mode позволяет использовать Wasm для современных браузеров с JS fallback для старых.

## Key Findings

1. **Browser Support (Dec 2024)**
   - All major browsers support WasmGC
   - Safari 18.2+ was the last holdout
   - Chrome/Edge 119+, Firefox 120+

2. **Performance**
   - ~3x faster than JS in UI scenarios
   - Execution speed approaches JVM performance
   - Trade-off: JS loads 0.25-0.5s faster initially

3. **Compose MP Web (Beta Sept 2025)**
   - Canvas-based rendering via Skia
   - Same UI code as mobile/desktop
   - Material 3 components included
   - SEO limitations (canvas not indexed)

4. **JS vs Wasm Decision**
   - Kotlin/JS: business logic sharing, better JS interop
   - Kotlin/Wasm: UI sharing with Compose MP
   - Compatibility mode: both with auto-detection

5. **webMain Source Set**
   - New in Kotlin 2.2.20
   - Single actual for both js and wasmJs
   - Reduces code duplication

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Kotlin/Wasm Overview](https://kotlinlang.org/docs/wasm-overview.html) | Official | 0.95 | Core documentation |
| 2 | [Present and Future of Kotlin for Web](https://blog.jetbrains.com/kotlin/2025/05/present-and-future-kotlin-for-web/) | Official | 0.95 | Roadmap |
| 3 | [Compose MP 1.9.0 Release](https://blog.jetbrains.com/kotlin/2025/09/compose-multiplatform-1-9-0-compose-for-web-beta/) | Official | 0.95 | Beta announcement |
| 4 | [Choosing Web Target](https://www.jetbrains.com/help/kotlin-multiplatform-dev/choosing-web-target.html) | Official | 0.95 | JS vs Wasm |
| 5 | [KMPShip Web Guide](https://www.kmpship.app/blog/kotlin-wasm-and-compose-web-2025) | Blog | 0.80 | Practical guide |

# Research Report: KMP DI Patterns

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

Koin — самый популярный DI framework для KMP благодаря простому DSL, быстрой сборке и полной поддержке всех платформ. kotlin-inject предоставляет compile-time safety (Dagger-like) за счёт более долгой сборки. Manual DI остаётся валидным для маленьких проектов. Koin 4.0+ поддерживает Compose Multiplatform, ViewModel integration и Koin Annotations (KSP). Используйте expect/actual для platform-specific dependencies.

## Key Findings

1. **Koin Dominance in KMP**
   - Most popular DI for Kotlin Multiplatform
   - Simple DSL, fast builds, runtime resolution
   - Full support: Android, iOS, Desktop, Web
   - Koin 4.0+ with Compose Multiplatform support

2. **kotlin-inject as Alternative**
   - Compile-time dependency graph validation
   - Dagger-like API with @Inject annotations
   - Faster runtime, slower builds
   - Growing KMP support

3. **Koin Annotations (Modern Approach)**
   - KSP-based code generation
   - @Single, @Factory, @Module annotations
   - Reduced boilerplate vs DSL
   - No reflection at startup

4. **Platform-Specific Patterns**
   - expect/actual for platform modules
   - Interfaces for testable code
   - Separate platform dependency graphs

5. **Comparison Summary**
   - Build time: Koin > Manual > kotlin-inject
   - Runtime: Manual > kotlin-inject > Koin
   - Safety: kotlin-inject > Manual > Koin
   - Learning: Koin > Manual > kotlin-inject

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Koin KMP Docs](https://insert-koin.io/docs/reference/koin-mp/kmp/) | Official | 0.95 | Full setup guide |
| 2 | [Koin vs kotlin-inject](https://infinum.com/blog/koin-vs-kotlin-inject-dependency-injection/) | Blog | 0.85 | Detailed comparison |
| 3 | [kotlin-inject](https://github.com/evant/kotlin-inject) | GitHub | 0.90 | Compile-time DI |
| 4 | [Modern DI Guide](https://medium.com/@felix.lf/a-guide-to-modern-dependency-injection-in-kmp-with-koin-annotations-dcc086a976f3) | Blog | 0.80 | Koin Annotations |
| 5 | [DI Showdown](https://www.droidcon.com/2024/08/30/koin-vs-kotlin-inject-the-ultimate-dependency-injection-showdown-on-the-kmp-arena/) | Droidcon | 0.85 | Performance comparison |

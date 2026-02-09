# Research Report: Compose Multiplatform Web

**Date:** 2026-01-03
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Compose Multiplatform for Web достиг Beta в сентябре 2025 (CMP 1.9.0). Canvas-based rendering через Skia обеспечивает ~3x лучшую производительность чем JS в UI scenarios. WasmGC поддерживается всеми major browsers с декабря 2024 (Safari 18.2 был последним). Beta включает type-safe navigation с deep linking, HTML interop, базовую accessibility, dark mode support. Ключевые ограничения: не подходит для SEO (Canvas не индексируется), initial load 1-3 секунды, нет SSR.

## Key Findings

1. **Beta Status (September 2025)**
   - Compose Multiplatform 1.9.0 elevated Web to Beta
   - No longer experimental, ready for early adopters
   - Core APIs stabilized for common code

2. **Canvas-Based Rendering**
   - All UI drawn on single <canvas> element via Skia/Skiko
   - ~3x faster than JavaScript in UI scenarios
   - Same code as mobile/desktop
   - Trade-off: no SEO, limited accessibility, no DevTools support

3. **Browser Support**
   - WasmGC required for Kotlin/Wasm
   - All major browsers support since December 2024
   - Chrome 119+, Firefox 120+, Safari 18.2+, Edge 119+
   - Compatibility mode provides JS fallback for older browsers

4. **Beta Features**
   - Type-safe navigation with deep linking (browser back/forward)
   - HTML interop for mixing Compose and native web elements
   - Fundamental accessibility support
   - Dark mode / system preferences auto-detection
   - Material 3 components

5. **Performance Trade-offs**
   - Initial load: 1-3 seconds (Wasm initialization)
   - After cache: 1-1.5 seconds
   - Bundle size: 2-5 MB (vs ~200KB for native web)
   - Runtime performance: excellent once loaded

6. **SEO Limitations**
   - Canvas content not indexable by search engines
   - No SSR/SSG support
   - Not suitable for marketing sites or public content
   - Ideal for SaaS, internal tools, apps behind login

7. **Alternatives for SEO**
   - Compose HTML (DOM-based, SEO-friendly, web-specific)
   - Kobweb (Compose HTML + SSG + routing)
   - Kilua (Composable DOM framework)

## Community Sentiment

### Positive
- Shared UI code across all platforms
- Excellent runtime performance
- Same development experience as mobile/desktop
- Navigation with deep linking works well
- Production apps already deployed (Kotlin Playground, KotlinConf)

### Negative
- Canvas approach "fundamentally not SEO-friendly"
- Accessibility limitations baked into foundation
- DevTools don't work for Compose UI
- Large bundle size compared to native web
- Initial load time noticeable
- "maybe you shouldn't use" for many web use cases

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [CMP 1.9.0 Release](https://blog.jetbrains.com/kotlin/2025/09/compose-multiplatform-1-9-0-compose-for-web-beta/) | Official | 0.95 | Beta announcement |
| 2 | [Present and Future of Kotlin for Web](https://blog.jetbrains.com/kotlin/2025/05/present-and-future-kotlin-for-web/) | Official | 0.95 | Roadmap |
| 3 | [KMPShip Web Guide](https://www.kmpship.app/blog/kotlin-wasm-and-compose-web-2025) | Blog | 0.85 | Practical guide |
| 4 | [C4W Analysis](https://bitspittle.dev/blog/2024/c4w) | Blog | 0.85 | Critical analysis |
| 5 | [Kotlin/Wasm Overview](https://kotlinlang.org/docs/wasm-overview.html) | Official | 0.95 | Technical details |
| 6 | [Choosing Web Target](https://www.jetbrains.com/help/kotlin-multiplatform-dev/choosing-web-target.html) | Official | 0.95 | JS vs Wasm decision |

## Recommendations

1. **For shared UI across platforms**: Use Compose Multiplatform Web
2. **For SEO-critical sites**: Use Compose HTML or Kobweb
3. **For SaaS/internal tools**: Compose Multiplatform Web is ideal
4. **For marketing sites**: Avoid Canvas-based approach
5. **For accessibility-critical apps**: Consider DOM-based alternatives
6. **Always implement**: Loading screen, compression, caching

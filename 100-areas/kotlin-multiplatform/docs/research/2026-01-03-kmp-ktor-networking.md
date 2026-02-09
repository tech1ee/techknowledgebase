# Research Report: Ktor Client in KMP

**Date:** 2026-01-03
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Ktor Client 3.3.x — официальный HTTP-клиент для KMP, использует kotlinx-io (based on Okio) для улучшенной производительности. Engines: OkHttp (Android), Darwin (iOS/macOS), CIO (кросс-платформенный, без HTTP/2), Java (JVM 11+), Js (Browser/Node). Plugins: ContentNegotiation (JSON), Auth (Bearer с refresh), HttpTimeout, Logging, HttpRequestRetry. MockEngine для unit-тестов без сети. WebSocket support на всех платформах. Netflix, McDonald's, Cash App используют в production.

## Key Findings

1. **Ktor 3.0+ Changes**
   - kotlinx-io library integration (based on Okio)
   - WebAssembly (Wasm) target support
   - Improved type safety with AttributeKey
   - WebRTC client (experimental, 3.3.0+)

2. **Engines Comparison**
   - OkHttp: HTTP/2, WebSockets, best for Android
   - Darwin: HTTP/2, WebSockets, NSURLSession
   - CIO: No HTTP/2, WebSockets, cross-platform
   - Java: HTTP/2, WebSockets, requires Java 11+

3. **Authentication**
   - Bearer token with automatic refresh on 401
   - loadTokens/refreshTokens callbacks
   - sendWithoutRequest for proactive auth

4. **Error Handling**
   - expectSuccess = true throws on non-2xx
   - HttpResponseValidator for custom handling
   - ClientRequestException, ServerResponseException

5. **Testing**
   - MockEngine for unit tests without network
   - Shared across all platforms
   - Can route by URL path

6. **Caching Limitations**
   - Built-in HttpCache is in-memory only
   - Kachetor library for persistent caching
   - iOS Darwin disables native caching by default

## Community Sentiment

### Positive
- Easy migration from Retrofit/OkHttp
- Excellent coroutines integration
- MockEngine makes testing simple
- Same API across all platforms

### Negative
- No persistent cache out-of-box
- CIO doesn't support HTTP/2
- Darwin engine caching requires extra work
- Some plugins require separate dependencies

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Ktor Client docs](https://ktor.io/docs/client.html) | Official | 0.95 | Complete reference |
| 2 | [Client Engines](https://ktor.io/docs/client-engines.html) | Official | 0.95 | Engine comparison |
| 3 | [Ktor 3.0 Release](https://blog.jetbrains.com/kotlin/2024/10/ktor-3-0/) | Blog | 0.90 | 3.0 features |
| 4 | [Migration Guide](https://ktor.io/docs/migrating-3.html) | Official | 0.95 | 2.x → 3.x |
| 5 | [Bearer Auth](https://ktor.io/docs/client-bearer-auth.html) | Official | 0.95 | Token refresh |
| 6 | [MockEngine Testing](https://ktor.io/docs/client-testing.html) | Official | 0.95 | Testing setup |
| 7 | [Response Validation](https://ktor.io/docs/client-response-validation.html) | Official | 0.95 | Error handling |
| 8 | [Kachetor](https://github.com/vipulasri/kachetor) | GitHub | 0.80 | Persistent caching |
| 9 | [droidcon Token Refresh](https://www.droidcon.com/2025/03/06/handling-token-expiration-in-ktor/) | Blog | 0.80 | Auth patterns |
| 10 | [Retrofit to Ktor](https://carrion.dev/en/posts/migrating-retrofit-okhttp-to-ktor-kmp/) | Blog | 0.85 | Migration guide |


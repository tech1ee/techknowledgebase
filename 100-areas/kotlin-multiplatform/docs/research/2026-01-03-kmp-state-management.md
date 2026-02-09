# Research Report: KMP State Management

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

Три основных подхода к state management в KMP: StateFlow (официальный, UI-layer), SharedFlow (events), MutableState (Compose-only). StateFlow — стандарт для ViewModel state с iOS bridging через SKIE или KMP-NativeCoroutines. MVI frameworks (MVIKotlin, Orbit) предоставляют structured patterns. Redux-Kotlin для global state. Ключевая проблема — iOS main thread updates требуют Dispatchers.Main.immediate.

## Key Findings

1. **StateFlow Dominance**
   - Standard for UI state in KMP
   - Built-in conflation (only latest value)
   - Requires initial value
   - iOS bridging needed (SKIE recommended)

2. **SharedFlow for Events**
   - Hot stream without initial value
   - Configurable replay and buffer
   - Best for one-shot events (navigation, toasts)
   - Can miss events if no subscribers

3. **MutableState (Compose)**
   - Compose-only, not portable
   - Snapshot system integration
   - Best for local UI state
   - Can't use in shared ViewModels for iOS

4. **iOS Bridging Solutions**
   - SKIE: Auto-generates Swift async sequences
   - KMP-NativeCoroutines: Manual but flexible
   - Both solve Flow collection on iOS

5. **MVI Frameworks**
   - MVIKotlin: Full MVI with time-travel debugging
   - Orbit MVI: Simpler reduce/sideEffect DSL
   - Both provide structured unidirectional flow

6. **Redux-Kotlin**
   - Global state management
   - Single source of truth
   - Middleware for side effects
   - Best for complex cross-feature state

## Community Sentiment

### Positive
- StateFlow + ViewModel is clean and testable
- SKIE dramatically improves iOS developer experience
- MVIKotlin time-travel debugging is excellent
- Orbit MVI has lower learning curve

### Negative
- iOS Flow collection still requires bridging
- MutableState not usable in shared code
- Main thread updates on iOS are tricky
- StateFlow requires initial value (can't use null-free)

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [StateFlow docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) | Official | 0.95 | StateFlow API |
| 2 | [Common ViewModel](https://kotlinlang.org/docs/multiplatform/compose-viewmodel.html) | Official | 0.95 | ViewModel setup |
| 3 | [SKIE](https://skie.touchlab.co/) | Official | 0.90 | iOS bridging |
| 4 | [KMP-NativeCoroutines](https://github.com/rickclephas/KMP-NativeCoroutines) | GitHub | 0.85 | iOS Flow collection |
| 5 | [MVIKotlin](https://arkivanov.github.io/MVIKotlin/) | Official | 0.90 | MVI framework |
| 6 | [Orbit MVI](https://orbit-mvi.org/) | Official | 0.90 | Simple MVI |
| 7 | [Redux-Kotlin](https://reduxkotlin.org/) | Official | 0.85 | Redux pattern |
| 8 | [State Management in KMP](https://proandroiddev.com/state-management-in-kotlin-multiplatform-66ef73ab10ce) | Blog | 0.80 | Practical patterns |


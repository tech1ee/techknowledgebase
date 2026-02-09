# Research Report: KMP Navigation

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

Три основных решения для навигации в KMP: Compose Navigation (официальный, type-safe с @Serializable), Decompose (lifecycle-aware BLoC, UI-independent), Voyager (Compose-first, простой API). Compose Navigation 2.9.1+ рекомендуется для новых CMP проектов благодаря type-safe routes и deep linking. Decompose лучше для complex scenarios с SwiftUI + Compose. Voyager — для быстрого старта.

## Key Findings

1. **Compose Navigation (Official)**
   - Type-safe routes with @Serializable
   - Built-in deep linking support
   - AndroidX Navigation API
   - Transitions and animations
   - Requires kotlinx-serialization

2. **Decompose**
   - Lifecycle-aware Components (BLoC)
   - UI-independent navigation logic
   - Supports SwiftUI, Compose, React
   - Child Stack, Child Slot, Child Pages
   - Unit-testable navigation

3. **Voyager**
   - Compose-first design
   - Simple Screen interface
   - ScreenModel (ViewModel alternative)
   - Tab navigation built-in
   - Lower learning curve

4. **Comparison Summary**
   - Type safety: Compose Nav > Decompose > Voyager
   - UI independence: Decompose > others
   - Learning curve: Voyager < Compose Nav < Decompose
   - Deep linking: Compose Nav > others

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Navigation in Compose](https://kotlinlang.org/docs/multiplatform/compose-navigation.html) | Official | 0.95 | Type-safe setup |
| 2 | [Decompose](https://arkivanov.github.io/Decompose/) | Official | 0.90 | Component navigation |
| 3 | [Voyager](https://voyager.adriel.cafe/) | Official | 0.85 | Simple navigation |
| 4 | [Navigation Solutions](https://proandroiddev.com/navigating-the-waters-of-kotlin-multiplatform-exploring-navigation-solutions-eef81aaa1a61) | Blog | 0.80 | Comparison |

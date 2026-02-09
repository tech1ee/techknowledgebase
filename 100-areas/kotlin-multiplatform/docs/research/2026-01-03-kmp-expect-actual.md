# Research Report: KMP Expect/Actual Mechanism

**Date:** 2026-01-03
**Sources Evaluated:** 12+
**Research Depth:** Deep

## Executive Summary

expect/actual — механизм Kotlin для платформо-зависимого кода. expect объявляет контракт в common, actual предоставляет реализацию в platform source set. Правила: одинаковое имя, один пакет, expect без реализации. Можно использовать для functions, classes, properties, objects, enums, annotations. typealias позволяет маппить на существующие платформенные типы. Best practice: предпочитать interfaces и DI когда возможно.

## Key Findings

1. **Core Rules**
   - expect в commonMain, actual в каждом platformMain
   - Одинаковое имя, один package
   - expect никогда не содержит реализацию
   - Компилятор проверяет наличие всех actual

2. **Supported Declarations**
   - Functions, Properties, Objects
   - Classes (Beta, требует -Xexpect-actual-classes)
   - Enums, Annotations
   - Typealias для маппинга на platform types

3. **Best Practices**
   - Interfaces over Classes — больше гибкости
   - DI для инъекции платформо-зависимых реализаций
   - Actual в intermediate source sets (iosMain вместо iosArm64Main)
   - Typealias для существующих platform types

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Expected/Actual Declarations](https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html) | Official Doc | 0.95 |
| 2 | [ProAndroidDev - Expect Actual Explained](https://proandroiddev.com/expect-actual-mechanism-in-kotlin-multiplatform-explained-a91e7d85af4e) | Blog | 0.85 |
| 3 | [Touchlab - Expect/Actuals](https://touchlab.co/expect-actuals-statements-kotlin-multiplatform) | Expert Blog | 0.90 |
| 4 | [Carrion.dev - Leveraging expect/actual](https://carrion.dev/en/posts/expect-actual-kmp/) | Blog | 0.80 |

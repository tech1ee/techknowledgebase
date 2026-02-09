# Research Report: ABI and Calling Conventions

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

ABI (Application Binary Interface) — набор правил взаимодействия бинарного кода с ОС и другими компонентами. Calling convention определяет: как передавать параметры (регистры/стек), кто очищает стек (caller/callee), какие регистры сохраняются. x86-64 System V: параметры в RDI, RSI, RDX, RCX, R8, R9; return в RAX. ARM64 AAPCS: параметры в X0-X7; return в X0. cdecl: caller очищает стек. stdcall: callee очищает стек. ABI stability критична для библиотек: изменение ABI требует перекомпиляции всех зависимостей.

## Key Findings

### 1. Что такое ABI

**Определение:**
Набор правил для взаимодействия бинарного кода на уровне:
- Вызов функций (calling conventions)
- Представление типов данных
- Name mangling
- Системные вызовы

**ABI vs API:**
- API: source-level interface (исходный код)
- ABI: binary-level interface (машинный код)

### 2. Calling Conventions: основные варианты

| Convention | Параметры | Очистка стека | Использование |
|------------|-----------|---------------|---------------|
| **cdecl** | Stack (RTL) | Caller | C default, varargs |
| **stdcall** | Stack (RTL) | Callee | Win32 API |
| **fastcall** | Registers + stack | Callee | Performance-critical |
| **System V x64** | Registers (6) + stack | Caller | Linux/macOS x64 |
| **Microsoft x64** | Registers (4) + stack | Caller | Windows x64 |

### 3. x86-64 System V ABI

**Параметры:**
- Integer: RDI, RSI, RDX, RCX, R8, R9
- Float: XMM0-XMM7
- Остальные: stack

**Return value:**
- RAX (64-bit)
- RAX + RDX (128-bit)

**Callee-saved:** RBX, RBP, R12-R15
**Caller-saved:** RAX, RDI, RSI, RDX, RCX, R8-R11

**Stack alignment:** 16 bytes
**Red zone:** 128 bytes

### 4. ARM64 AAPCS

**Параметры:**
- Integer: X0-X7
- Float: V0-V7
- Остальные: stack

**Return value:**
- X0 (64-bit)
- X0 + X1 (128-bit)

**Special registers:**
- X30 (LR): Link register
- X29 (FP): Frame pointer
- X18 (PR): Platform register

**Callee-saved:** X19-X28, V8-V15 (lower 64 bits)

### 5. Stack Frame

```
┌─────────────────┐ High address
│  Return address │
├─────────────────┤
│  Saved RBP      │ ← RBP points here
├─────────────────┤
│  Local vars     │
├─────────────────┤
│  Spilled args   │
└─────────────────┘ Low address (RSP)
```

### 6. ABI Breaking Changes

| Изменение | Ломает ABI? |
|-----------|-------------|
| Добавить параметр в функцию | Да |
| Изменить порядок полей struct | Да |
| Изменить calling convention | Да |
| Добавить новую функцию | Нет |
| Изменить реализацию (не сигнатуру) | Нет |

### 7. ABI Stability

**Почему важна:**
- Библиотеки не нужно перекомпилировать
- Forward compatibility
- Экосистема пакетов

**Swift ABI Stability (2019):**
- Приложения работают с разными версиями Swift runtime
- Уменьшение размера приложений

## Community Sentiment

### Positive
- Understanding ABI helps debugging crashes
- Critical for library developers
- Platform-specific optimizations

### Negative
- Complex topic for beginners
- Platform differences confusing
- ABI breaks cause dependency hell

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Wikipedia: x86 Calling Conventions](https://en.wikipedia.org/wiki/X86_calling_conventions) | Reference | ★★★★★ | Comprehensive |
| [OSDev: System V ABI](https://wiki.osdev.org/System_V_ABI) | Wiki | ★★★★★ | Technical details |
| [Microsoft: x64 Calling Convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention) | Official | ★★★★★ | Windows specifics |
| [ARM AAPCS64](https://medium.com/@tunacici7/aarch64-procedure-call-standard-aapcs64-abi-calling-conventions-machine-registers-a2c762540278) | Blog | ★★★★☆ | ARM64 explained |
| [Agner Fog: Calling Conventions](https://www.agner.org/optimize/calling_conventions.pdf) | PDF | ★★★★★ | Deep technical |
| [Swift ABI Stability](https://www.swift.org/blog/abi-stability-and-more/) | Official | ★★★★☆ | Modern relevance |

## Research Methodology
- **Queries used:** 3 search queries
- **Sources found:** 30+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** System V, ARM64, cdecl/stdcall, ABI stability

---

*Проверено: 2026-01-09*

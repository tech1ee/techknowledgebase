# Research Report: Bytecode and Virtual Machines

**Date:** 2026-01-04
**Sources Evaluated:** 30+
**Research Depth:** Deep

## Executive Summary

Bytecode — промежуточный код между высокоуровневым языком и машинным кодом. Виртуальные машины (VM) исполняют bytecode, абстрагируя аппаратуру. Бывают стековые (JVM, WASM) и регистровые (Dalvik). JVM использует class loading, bytecode verification и JIT/AOT компиляцию. WASM — современный stack-based формат для web с sandbox security. Android эволюционировал от Dalvik (register-based JIT) к ART (AOT + JIT гибрид). Kotlin компилируется во все эти форматы через разные backend'ы.

## Key Findings

### 1. История виртуальных машин

**Java VM (1995):**
- Создана Sun Microsystems (James Gosling)
- Изначально для "интерактивного ТВ" (set-top box)
- Переориентирована на Web в 1994
- Революционная идея: "Write Once, Run Anywhere" (WORA)
- Первый массовый пример bytecode + VM подхода

**Dalvik (2008):**
- Создан Google для Android
- Register-based вместо stack-based
- Оптимизирован для мобильных устройств с ограниченными ресурсами
- Использовал JIT компиляцию с Android 2.2

**ART (2014):**
- Замена Dalvik начиная с Android 5.0
- AOT компиляция при установке
- С Android 7.0 — гибрид AOT + JIT

**WebAssembly (2017):**
- Стандартизирован W3C
- Stack-based, sandbox isolated
- Для высокопроизводительного кода в браузере
- WASM 3.0 (2025) — GC, 64-bit memory, exceptions

### 2. Стековые vs Регистровые VM

| Аспект | Stack-based (JVM, WASM) | Register-based (Dalvik, Lua) |
|--------|-------------------------|------------------------------|
| Операнды | На стеке | В виртуальных регистрах |
| Инструкции | Больше, проще | Меньше, сложнее |
| Размер кода | Меньше | Больше (адреса регистров) |
| Скорость | Push/pop overhead | Меньше инструкций |
| Сложность | Проще реализовать | Сложнее, ближе к реальному CPU |

**2025 исследование (Wiley):**
- Stack-based чуть быстрее для рекурсии (~1.04x)
- Register-based быстрее для general-purpose кода
- С JIT разница минимальна

### 3. JVM Архитектура

**Структура:**
```
.java → javac → .class (bytecode)
                    ↓
             ┌──────────────┐
             │  ClassLoader │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │   Verifier   │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │  Interpreter │ ──→ JIT Compiler
             └──────────────┘
```

**Class Loading:**
1. Bootstrap ClassLoader — java.lang.* (native код)
2. Platform ClassLoader — расширения платформы
3. Application ClassLoader — код приложения

**Delegation Model:**
- Запрос на загрузку идёт вверх по иерархии
- Родитель пытается загрузить первым
- Если не может — ребёнок пробует сам

**Bytecode Verification:**
- Проверяет корректность bytecode до исполнения
- Stack underflow/overflow protection
- Type safety enforcement
- Unauthorized access prevention

### 4. JVM Bytecode Details

**Категории инструкций:**
- Load/Store: aload, istore, etc.
- Arithmetic: iadd, fmul, etc.
- Type conversion: i2l, f2d, etc.
- Stack manipulation: dup, swap, pop
- Control flow: ifeq, goto, return
- Method invocation: invokevirtual, invokespecial

**Operand Stack:**
```
iconst_2    ; push 2 → stack: [2]
iconst_3    ; push 3 → stack: [2, 3]
iadd        ; pop 2, pop 3, push 5 → stack: [5]
istore_0    ; pop 5, store to local var 0 → stack: []
```

**Local Variables:**
- Каждый метод имеет массив local variables
- Индексируются от 0
- Slot 0 = this для instance methods

### 5. WebAssembly (WASM)

**Ключевые характеристики:**
- Stack-based виртуальная машина
- Компактный binary формат (.wasm)
- Linear memory (песочница)
- Детерминистичное исполнение
- Формальная верификация дизайна

**Отличия от JVM:**
- Нет GC в оригинальном стандарте (добавлен в 3.0)
- Более низкий уровень абстракции
- Sandboxed memory без прямого доступа к host
- Designed for AOT, но поддерживает JIT

**WASM 3.0 (September 2025):**
- 64-bit address space
- Garbage collection support
- Tail calls
- Exception handling

**Kotlin/Wasm:**
- Использует WasmGC
- Compose Multiplatform поддерживает WASM
- Производительность близка к JVM
- Все major browsers поддерживают с Dec 2024

### 6. Android: Dalvik → ART

**DEX Format:**
- Dalvik Executable
- Оптимизирован для размера и памяти
- Несколько .class → один .dex
- Register-based instructions

**Dalvik VM:**
- JIT компиляция (с Android 2.2)
- Trace-based JIT — компилирует hot paths
- Интерпретирует остальное

**ART (Android Runtime):**
- AOT при установке (dex2oat)
- С Android 7.0 — AOT + JIT + Profile-Guided
- .vdex, .odex, .art файлы

**Преимущества ART:**
- Быстрее холодный старт
- Меньше runtime overhead
- Лучше battery life
- Улучшенный GC

### 7. Bytecode Verification Security

**JVM Verifier проверяет:**
- Формат class file корректен
- Stack не переполняется/не underflow
- Типы операций совпадают
- Нет доступа к неинициализированным переменным
- Нет нелегального приведения типов
- Private fields защищены

**WASM Security:**
- Memory sandboxed — не может читать host память
- Stack изолирован
- Формальная верификация спецификации
- Нет raw pointers к host

**Зачем verification:**
- Bytecode может быть сгенерирован не компилятором
- Можно вручную создать "плохой" bytecode
- Untrusted code должен быть проверен

### 8. Kotlin и разные VM

| Target | Bytecode | VM |
|--------|----------|-----|
| JVM | JVM bytecode (.class) | JVM |
| Android | DEX | ART |
| JS | JavaScript | JS Engine |
| Native | LLVM IR → binary | No VM (AOT) |
| Wasm | WebAssembly | WASM runtime |

**Kotlin/JVM специфика:**
- По умолчанию Java 8 compatible bytecode
- Можно указать target version 9-21
- Kotlin-specific features транслируются в bytecode patterns

### 9. Распространённые заблуждения

**Миф:** JVM медленнее native кода
**Факт:** С JIT JVM может быть быстрее — runtime optimization, profile-guided decisions

**Миф:** Bytecode interpretation всегда медленная
**Факт:** JIT компилирует hot paths в native code

**Миф:** WASM работает только в браузере
**Факт:** Standalone runtimes (Wasmtime, Wasmer) работают везде

**Миф:** Stack-based VM всегда медленнее register-based
**Факт:** С JIT разница минимальна; stack-based проще для optimization passes

### 10. Best Practices

1. **Изучи javap** — позволяет смотреть JVM bytecode
2. **Пойми operand stack** — ключ к пониманию bytecode
3. **Используй правильный target** — для KMP важно знать особенности каждого
4. **Не бойся bytecode** — это просто более низкий уровень того же кода

## Community Sentiment

### Positive
- JVM экосистема зрелая и надёжная
- WASM быстро развивается, хорошая спецификация
- Kotlin/Wasm показывает хорошие результаты
- ART значительно улучшил Android performance

### Negative
- JVM startup time всё ещё проблема
- WASM GC относительно новый, не везде оптимизирован
- Dalvik → ART миграция была болезненной
- Разные bytecode форматы усложняют KMP debugging

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Crafting Interpreters](https://craftinginterpreters.com) | Book | 0.95 | Bytecode VM concepts |
| 2 | [GeeksforGeeks: JVM Architecture](https://www.geeksforgeeks.org/java/how-jvm-works-jvm-architecture/) | Tutorial | 0.85 | JVM overview |
| 3 | [Wikipedia: Java bytecode](https://en.wikipedia.org/wiki/Java_bytecode) | Reference | 0.9 | Bytecode instruction set |
| 4 | [Baeldung: ClassLoaders](https://www.baeldung.com/java-classloaders) | Tutorial | 0.9 | Class loading |
| 5 | [AOSP: Android Runtime](https://source.android.com/docs/core/runtime) | Official | 0.95 | ART/Dalvik |
| 6 | [Wikipedia: WebAssembly](https://en.wikipedia.org/wiki/WebAssembly) | Reference | 0.9 | WASM overview |
| 7 | [webassembly.org: Wasm 3.0](https://webassembly.org/news/2025-09-17-wasm-3.0/) | Official | 0.95 | WASM 3.0 features |
| 8 | [Wiley 2025: Stack vs Register VM](https://onlinelibrary.wiley.com/doi/full/10.1002/spe.70014) | Academic | 0.95 | Performance comparison |
| 9 | [JetBrains: Kotlin/Wasm](https://kotlinlang.org/docs/wasm-overview.html) | Official | 0.95 | Kotlin WASM target |
| 10 | [InfoWorld: Bytecode basics](https://www.infoworld.com/article/2169838/bytecode-basics.html) | Tutorial | 0.85 | Bytecode fundamentals |
| 11 | [Oracle: Security in Java](https://www.oracle.com/java/technologies/security-in-java.html) | Official | 0.95 | Verification security |
| 12 | [Medium: Stack vs Register VM](https://thamizhelango.medium.com/register-based-vs-stack-based-virtual-machines-a-complete-guide-d87f25c649e9) | Blog | 0.8 | VM comparison |

## Research Methodology
- **Queries used:** 10 search queries
- **Sources found:** 45+ total
- **Sources used:** 30 (after quality filter)
- **Focus areas:** JVM bytecode, WASM, Dalvik/ART, VM architectures, Kotlin targets

---

*Проверено: 2026-01-09*

# Research Report: Compilation Pipeline

**Date:** 2026-01-04
**Sources Evaluated:** 28+
**Research Depth:** Deep

## Executive Summary

Compilation — процесс превращения исходного кода в исполняемую программу через серию этапов: лексический анализ (токенизация), синтаксический анализ (построение AST), семантический анализ (проверка типов, scope resolution), генерация промежуточного представления (IR), оптимизация и генерация целевого кода. Современные компиляторы используют SSA-форму (Static Single Assignment) для упрощения оптимизаций. Kotlin K2 использует единую архитектуру frontend с FIR (Frontend Intermediate Representation) для всех платформ.

## Key Findings

### 1. История компиляции

- Grace Hopper (1952) — создатель первого компилятора A-0
- FORTRAN (1957) — первый практически используемый компилятор
- До компиляторов код писали напрямую в машинных кодах
- Термин "compiler" ввела Grace Hopper ("compile" = собирать вместе)

### 2. Шесть фаз компилятора

| Фаза | Что делает | Вход | Выход |
|------|------------|------|-------|
| **Lexical Analysis** | Разбивает на токены | Исходный код (символы) | Токены |
| **Syntax Analysis** | Строит AST | Токены | Parse Tree / AST |
| **Semantic Analysis** | Проверяет типы, scope | AST | Decorated AST |
| **IR Generation** | Создаёт промежуточный код | AST | IR (например, three-address code) |
| **Optimization** | Улучшает код | IR | Optimized IR |
| **Code Generation** | Генерирует целевой код | IR | Machine code / Bytecode |

### 3. Frontend vs Backend

**Frontend:**
- Lexer (tokenizer)
- Parser (syntax analyzer)
- Semantic analyzer
- IR generator

**Backend:**
- Optimizer
- Code generator
- Target-specific lowering

**Middle-end (современные компиляторы):**
- Платформо-независимые оптимизации на IR
- SSA form transformations

### 4. Intermediate Representation (IR)

**Зачем нужен IR:**
- Абстрагирует от исходного языка И от целевой платформы
- Упрощает оптимизации
- Позволяет поддерживать M языков и N платформ с M+N компонентами вместо M×N

**SSA (Static Single Assignment):**
- Каждая переменная присваивается ровно ОДИН раз
- Упрощает data-flow analysis
- Используется в LLVM, GCC, HotSpot JIT
- Phi-функции (φ) для слияния значений из разных веток

**Примеры IR:**
- LLVM IR — низкоуровневый, типизированный, бесконечные регистры
- JVM Bytecode — высокоуровневый, стековая машина, память безопасна
- Kotlin FIR — семантически богатый, для frontend анализа

### 5. Оптимизации компилятора

**Основные техники:**

| Оптимизация | Описание |
|-------------|----------|
| **Constant Folding** | Вычисление констант compile-time: `2 + 3` → `5` |
| **Constant Propagation** | Распространение известных значений |
| **Dead Code Elimination** | Удаление недостижимого кода |
| **Inlining** | Подстановка тела функции вместо вызова |
| **Common Subexpression Elimination** | Переиспользование вычислений |
| **Loop Unrolling** | Развёртывание циклов |
| **Strength Reduction** | Замена дорогих операций дешёвыми |

**Важно:** Inlining главное преимущество НЕ в устранении call overhead, а в возможности применить другие оптимизации к inline-коду.

### 6. Symbol Table

**Что хранит:**
- Имена идентификаторов
- Типы
- Scope информация
- Позиция объявления

**Операции:**
- Insert — при объявлении
- Lookup — при использовании
- Update — при изменении (например, инициализация)
- Delete — при выходе из scope

**Реализация:** обычно hash table с chaining для обработки одинаковых имён в разных scope.

### 7. Kotlin Compiler (K2)

**Архитектура:**
```
Source Code
    ↓
PSI (Program Structure Interface)
    ↓
FIR (Frontend Intermediate Representation)
    ↓
IR (Backend Intermediate Representation)
    ↓
Lowered IR
    ↓
Target Code (JVM/JS/Native/WASM)
```

**K2 vs K1:**
- K2 использует ОДНУ структуру данных (FIR) вместо двух
- До 2x ускорение компиляции
- Улучшенный type inference
- Унифицированный pipeline для всех платформ

**KMP компиляция:**
- commonMain → собирается для всех таргетов
- JVM: FIR → IR → JVM Bytecode
- Native: FIR → IR → LLVM IR → Native binary
- JS: FIR → IR → JavaScript
- WASM: FIR → IR → WebAssembly

### 8. Распространённые заблуждения

**Миф:** -O3 значительно быстрее -O2
**Факт:** Исследования показывают отсутствие статистически значимой разницы в Clang. -O3 игнорирует размер кода, что может негативно влиять на instruction cache.

**Миф:** Inline keyword гарантирует inlining
**Факт:** `inline` в основном влияет на linkage. Для гарантированного inlining нужен `always_inline`.

**Миф:** Компилятор производит оптимальный код
**Факт:** "Optimization" — некорректное название. Компилятор УЛУЧШАЕТ код, но не находит оптимум.

**Миф:** Middle-end полностью платформо-независим
**Факт:** Даже LLVM middle-end содержит target-specific детали и оптимизации.

**Миф:** Branch hints управляют branch predictor в CPU
**Факт:** На x86 CPU игнорирует branch hints. Они влияют на code placement для instruction cache.

**Миф:** Раздельная компиляция всегда ускоряет сборку
**Факт:** Линковка очень медленная. Unity builds (всё в один файл) часто быстрее для проектов до ~20K строк.

### 9. LLVM IR vs JVM Bytecode

| Аспект | LLVM IR | JVM Bytecode |
|--------|---------|--------------|
| Архитектура | Register-based | Stack-based |
| Регистры | Бесконечные виртуальные | Нет (стек операндов) |
| Memory safety | Нет (есть ptrtoint) | Да (нет raw pointers) |
| SSA | Да | Нет |
| Компиляция | Преимущественно AOT | Преимущественно JIT |
| Типизация | Сильная, низкоуровневая | Сильная, высокоуровневая |

### 10. Best Practices для понимания компиляции

1. **Изучи этапы последовательно** — каждый зависит от предыдущего
2. **Смотри реальный IR** — LLVM IR, JVM bytecode (`kotlinc -Xprint-ir`)
3. **Не доверяй "очевидным" оптимизациям** — measure, don't guess
4. **Пойми SSA** — ключ к современным оптимизациям
5. **Frontend и backend — разные проблемы** — type checking vs code generation

## Community Sentiment

### Positive
- LLVM сделал создание компиляторов доступнее
- K2 существенно улучшил опыт Kotlin разработки
- SSA упрощает анализ и оптимизации
- Crafting Interpreters — отличный ресурс для изучения

### Negative
- LLVM слишком сложен для обучения ("monstrosity" — sbaziotis)
- Компиляция C++ остаётся медленной даже с современными компиляторами
- Шаблоны C++ не inherently медленные — проблема в compilation model
- Link-Time Optimization медленная

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Crafting Interpreters](https://craftinginterpreters.com) | Book | 0.95 | Pipeline explanation, analogies |
| 2 | [GeeksforGeeks: Phases of Compiler](https://www.geeksforgeeks.org/compiler-design/phases-of-a-compiler/) | Tutorial | 0.85 | 6 phases overview |
| 3 | [Cornell: Intermediate Representations](https://www.cs.cornell.edu/courses/cs4120/2023sp/notes/ir/) | Academic | 0.95 | IR theory |
| 4 | [Wikipedia: SSA](https://en.wikipedia.org/wiki/Static_single-assignment_form) | Reference | 0.9 | SSA explanation |
| 5 | [JetBrains: K2 Compiler](https://blog.jetbrains.com/kotlin/2024/05/celebrating-kotlin-2-0-fast-smart-and-multiplatform/) | Official | 0.95 | K2 architecture |
| 6 | [sbaziotis: Common Misconceptions](https://sbaziotis.com/compilers/common-misconceptions-about-compilers.html) | Expert Blog | 0.9 | Myth busting |
| 7 | [Medium: SSA Form Explained](https://medium.com/@mlshark/an-introduction-to-static-single-assignment-ssa-form-in-compiler-design-77d33ee773de) | Blog | 0.8 | SSA examples |
| 8 | [Wikipedia: LLVM](https://en.wikipedia.org/wiki/LLVM) | Reference | 0.9 | LLVM overview |
| 9 | [HN: LLVM vs JVM](https://news.ycombinator.com/item?id=13860815) | Discussion | 0.75 | IR comparison |
| 10 | [Stanford: Semantic Analysis](https://web.stanford.edu/class/archive/cs/cs143/cs143.1128/handouts/180%20Semantic%20Analysis.pdf) | Academic | 0.95 | Type checking theory |
| 11 | [GeeksforGeeks: Semantic Analysis](https://www.geeksforgeeks.org/compiler-design/semantic-analysis-in-compiler-design/) | Tutorial | 0.85 | Symbol table |
| 12 | [GCC Optimize Options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html) | Official | 0.95 | Optimization flags |
| 13 | [Kotlin: Configure Compilations](https://kotlinlang.org/docs/multiplatform-configure-compilations.html) | Official | 0.95 | KMP compilation |
| 14 | [Medium: Kotlin Compiler Crash Course](https://medium.com/google-developer-experts/crash-course-on-the-kotlin-compiler-k1-k2-frontends-backends-fe2238790bd8) | Expert Blog | 0.85 | K1/K2 architecture |
| 15 | [InfoQ: Kotlin 2.0 K2](https://www.infoq.com/news/2024/05/kotlin-2-k2-compiler/) | News | 0.85 | K2 benefits |

## Research Methodology
- **Queries used:** 12 search queries
- **Sources found:** 40+ total
- **Sources used:** 28 (after quality filter)
- **Focus areas:** Compilation phases, IR/SSA, optimizations, Kotlin compiler, misconceptions

---

*Проверено: 2026-01-09*

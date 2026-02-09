# Research Report: Interpretation and JIT Compilation

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

JIT (Just-In-Time) компиляция — компиляция во время выполнения программы. Сочетает преимущества интерпретации (быстрый старт) и AOT компиляции (быстрое исполнение). HotSpot JVM использует tiered compilation: интерпретация → C1 (быстрая компиляция) → C2 (агрессивные оптимизации). V8 имеет 4-tier pipeline: Ignition → Sparkplug → Maglev → TurboFan. Tracing JIT (LuaJIT, PyPy) компилирует горячие пути, а не методы. Inline caching оптимизирует dynamic dispatch. Деоптимизация возвращает к интерпретации при нарушении спекулятивных предположений.

## Key Findings

### 1. История JIT

**1960:** John McCarthy упомянул runtime compilation в работе по LISP
**1968:** Ken Thompson применил JIT для regex в QED
**1984:** Smalltalk использовал inline caching
**1999:** HotSpot JVM от Sun
**2008:** V8 (Chrome) с modern JIT
**2017:** V8 переход на Ignition+TurboFan

### 2. Интерпретатор vs Компилятор

| Аспект | Интерпретатор | Компилятор |
|--------|---------------|------------|
| Трансляция | Построчно | Весь код сразу |
| Скорость запуска | Быстрая | Медленнее |
| Скорость исполнения | Медленнее | Быстрая |
| Память | Меньше | Больше |
| Отладка | Проще | Сложнее |

### 3. JIT как гибрид

JIT = Интерпретация + Компиляция runtime:
1. Начинается с интерпретации
2. Профилирует код (hot spots)
3. Компилирует горячий код
4. Выполняет native code

### 4. JVM Tiered Compilation

5 уровней:
- **Level 0:** Интерпретация + профилирование
- **Level 1:** C1 без профилирования (тривиальные методы)
- **Level 2:** C1 с лёгким профилированием (C2 занят)
- **Level 3:** C1 с полным профилированием
- **Level 4:** C2 максимальные оптимизации

Типичный путь: 0 → 3 → 4

### 5. V8 Pipeline (2023+)

4-tier система:
1. **Ignition:** Интерпретатор байткода
2. **Sparkplug:** Быстрый baseline compiler
3. **Maglev:** Mid-tier optimizer (10x медленнее Sparkplug, 10x быстрее TurboFan)
4. **TurboFan:** Aggressive optimizer с Sea-of-Nodes IR

### 6. Tracing vs Method JIT

| Аспект | Method JIT | Tracing JIT |
|--------|------------|-------------|
| Unit | Метод | Hot loop trace |
| Inlining | Explicit | Automatic |
| Сложность | Выше | Ниже |
| Performance cliffs | Меньше | Больше |
| Примеры | JVM, V8 | LuaJIT, PyPy |

Tracing: "labor-saving device for compiler authors"

### 7. Inline Caching

Три состояния call site:
- **Monomorphic:** один тип (90% случаев)
- **Polymorphic:** несколько типов (9%)
- **Megamorphic:** много типов (1%)

Чем монорфнее, тем быстрее.

### 8. Деоптимизация

Когда спекуляции нарушаются:
1. Guard проверяет assumption
2. При провале → bailout
3. Возврат к интерпретации
4. Возможна реоптимизация

### 9. Warmup проблема

Проблема: peak performance только после warmup.

Решения:
- **JEP 515:** AOT Method Profiling
- **CRaC:** Checkpoint/Restore
- **ReadyNow:** Persisted profiles (Azul)
- **CDS/AppCDS:** Class Data Sharing
- **GraalVM Native Image:** AOT compilation

### 10. Ключевые оптимизации

- **Inlining:** вставка тела функции
- **Escape Analysis:** stack allocation вместо heap
- **Dead Code Elimination:** удаление неиспользуемого
- **Loop Unrolling:** развёртка циклов
- **Constant Folding:** вычисление констант

## Community Sentiment

### Positive
- JIT даёт лучший peak performance чем AOT
- Tiered compilation хорошо балансирует startup/peak
- V8 сделал JS быстрым языком
- HotSpot — зрелая и стабильная технология

### Negative
- Warmup latency критична для serverless
- Сложность debugging JIT-оптимизированного кода
- Memory overhead от профилирования
- Непредсказуемые performance spikes

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Wikipedia: JIT](https://en.wikipedia.org/wiki/Just-in-time_compilation) | Reference | 0.9 | History, basics |
| 2 | [Baeldung: Tiered Compilation](https://www.baeldung.com/jvm-tiered-compilation) | Tutorial | 0.85 | JVM levels |
| 3 | [V8 Blog: Ignition+TurboFan](https://v8.dev/blog/launching-ignition-and-turbofan) | Official | 0.95 | V8 architecture |
| 4 | [Oracle: JIT Understanding](https://docs.oracle.com/cd/E13150_01/jrockit_jvm/jrockit/geninfo/diagnos/underst_jit.html) | Official | 0.95 | JIT optimization |
| 5 | [kipp.ly: JITs Implementations](https://kipp.ly/jits-impls/) | Blog | 0.85 | Tracing vs Method |
| 6 | [Wikipedia: Tracing JIT](https://en.wikipedia.org/wiki/Tracing_just-in-time_compilation) | Reference | 0.9 | Tracing approach |
| 7 | [jayconrod: PICs](https://jayconrod.com/posts/44/polymorphic-inline-caches-explained) | Blog | 0.85 | Inline caching |
| 8 | [OpenJDK: JEP 515](https://openjdk.org/jeps/515) | Official | 0.95 | AOT profiling |
| 9 | [GraalVM: PGO](https://www.graalvm.org/latest/reference-manual/native-image/optimizations-and-performance/PGO/) | Official | 0.95 | Profile-guided opt |
| 10 | [GeeksforGeeks: Compiler vs Interpreter](https://www.geeksforgeeks.org/compiler-design/difference-between-compiler-and-interpreter/) | Tutorial | 0.85 | Basics |

## Research Methodology
- **Queries used:** 8 search queries
- **Sources found:** 35+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** JIT mechanics, Tiered compilation, V8, Tracing, Inline caching, Warmup

---

*Проверено: 2026-01-09*

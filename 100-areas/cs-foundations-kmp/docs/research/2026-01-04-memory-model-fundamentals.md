# Research Report: Stack vs Heap Memory Fundamentals

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Stack и Heap — два ключевых сегмента памяти программы с принципиально разным поведением. Stack использует LIFO, автоматически управляется при вызовах функций, быстрый но ограниченный. Heap — динамический, гибкий, требует явного управления, медленнее из-за fragmentation и allocation overhead. Исторически stack появился с ALGOL (1958), heap — с Lisp (1960s). Для KMP критично: JVM использует GC для heap, Kotlin/Native — ARC + cycle collector.

## Key Findings

### 1. Stack Memory
- LIFO структура (Last In, First Out)
- Автоматическое выделение/освобождение при вызове функций
- Stack frame содержит: локальные переменные, параметры, return address
- Размер фиксирован при старте потока (Linux/macOS: 1MB default)
- Растёт вниз (от высоких адресов к низким)
- Каждый поток имеет свой stack

### 2. Heap Memory
- Динамическое выделение через malloc/new
- Требует явного освобождения (free/delete) или GC
- Может фрагментироваться (internal + external fragmentation)
- Общий для всех потоков
- Растёт вверх (от низких адресов к высоким)
- Медленнее из-за поиска свободных блоков

### 3. Историческая эволюция
- Fortran (1950s): только static allocation
- ALGOL 60 (1958): ввёл stack allocation, block structure
- Lisp (1960s): heap + garbage collection
- ALGOL 68: stack + heap + garbage collection
- C (1970s): явное управление через malloc/free

### 4. Распространённые заблуждения
- "Value types всегда на stack" — НЕПРАВДА, зависит от контекста
- "Stack и Heap — разные типы памяти" — оба в RAM
- "C++ требует stack" — это implementation detail
- "Heap data structure = heap memory" — разные концепции

### 5. JVM специфика
- Stack: примитивы + ссылки на объекты
- Heap: все объекты (создаются через new)
- Generations: Young → Old (Tenured)
- Metaspace: class metadata (заменил PermGen)
- Ошибки: StackOverflowError vs OutOfMemoryError

### 6. Kotlin/Native специфика
- Shared heap для всех потоков
- Современный memory manager (похож на JVM)
- Раньше использовал freeze model (deprecated)
- Tracing GC с mark-and-sweep + concurrent marking

## Community Sentiment

### Positive
- Stack/heap separation хорошо изучена и документирована
- Много качественных визуальных объяснений
- Аналогии помогают понять (plates, hotel room, beach)

### Negative
- Часто преподаётся упрощённо ("value types on stack")
- Путаница между heap data structure и heap memory
- C/C++ стандарты не упоминают stack/heap напрямую

## Best Analogies Found

| Концепция | Аналогия | Источник |
|-----------|----------|----------|
| Stack | Стопка тарелок в столовой | CS225 Illinois |
| Stack | Номер в отеле (выехал — всё убрали) | Bitesize Engineering |
| Heap | Пляж (оставляешь где хочешь, сам следи) | Bitesize Engineering |
| Stack | Блокнот для заметок (быстро, мало места) | Medium |
| Heap | Шкаф для документов (много места, нужен порядок) | Medium |
| Stack pointer | Указатель "читать здесь" в книге | Weber State |

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Baeldung CS](https://www.baeldung.com/cs/memory-stack-vs-heap) | Tutorial | 0.9 | Technical depth |
| 2 | [CS225 Illinois](https://courses.grainger.illinois.edu/cs225/fa2022/resources/stack-heap/) | Academic | 0.95 | Visual diagrams |
| 3 | [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/stack-vs-heap-memory-allocation/) | Tutorial | 0.8 | Comprehensive overview |
| 4 | [Bitesize Engineering](https://www.bitesizedengineering.com/p/heaps-and-stacks-explained-like-youre-five) | Blog | 0.85 | Best analogies |
| 5 | [Microsoft Learn](https://learn.microsoft.com/en-us/archive/blogs/abhinaba/back-to-basics-memory-allocation-a-walk-down-the-history) | Official | 0.95 | Historical context |
| 6 | [Kotlin Docs](https://kotlinlang.org/docs/native-memory-manager.html) | Official | 0.95 | K/N specifics |
| 7 | [JetBrains Blog](https://blog.jetbrains.com/kotlin/2021/05/kotlin-native-memory-management-update/) | Official | 0.95 | K/N evolution |
| 8 | [DigitalOcean](https://www.digitalocean.com/community/tutorials/java-heap-space-vs-stack-memory) | Tutorial | 0.85 | JVM specifics |
| 9 | [Weber State CS](https://icarus.cs.weber.edu/~dab/cs1410/textbook/4.Pointers/memory.html) | Academic | 0.9 | Memory layout |
| 10 | [Cornell CS3410](https://www.cs.cornell.edu/courses/cs3410/2025sp/notes/mem.html) | Academic | 0.95 | CPU architecture |
| 11 | [CS341 Illinois Malloc](https://cs341.cs.illinois.edu/coursebook/Malloc) | Academic | 0.95 | Heap internals |
| 12 | [Chessman Substack](https://chessman7.substack.com/p/the-anatomy-of-a-stack-frame-a-guide) | Blog | 0.8 | Stack frames |
| 13 | [Wikipedia Stack Overflow](https://en.wikipedia.org/wiki/Stack_overflow) | Reference | 0.85 | Error causes |
| 14 | [DEV.to Value/Ref Types](https://dev.to/tyrrrz/interview-question-heap-vs-stack-c-5aae) | Blog | 0.8 | Misconceptions |
| 15 | [Memory Management Org](https://www.memorymanagement.org/mmref/lang.html) | Reference | 0.9 | Language history |

## Research Methodology
- **Queries used:** 12 search queries
- **Sources found:** 40+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** fundamentals, history, misconceptions, JVM, Kotlin Native

---

*Проверено: 2026-01-09*

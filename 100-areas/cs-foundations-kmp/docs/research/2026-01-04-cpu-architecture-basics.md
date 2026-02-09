# Research Report: CPU Architecture Basics

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

CPU — центральный процессор, выполняющий инструкции программы. Ключевые компоненты: регистры (сверхбыстрая память в CPU), ALU (арифметико-логическое устройство), Control Unit. Instruction cycle: Fetch → Decode → Execute → (Memory) → Write Back. Pipeline позволяет выполнять несколько инструкций одновременно. Memory hierarchy: L1 cache (~1-3 cycles), L2 (~10 cycles), L3 (~40 cycles), RAM (~100+ cycles). Cache hit/miss критичен для производительности.

## Key Findings

### 1. Регистры

**Определение:**
Сверхбыстрая память внутри CPU, доступ за 1 цикл.

**Типы регистров:**
- **Program Counter (PC):** адрес следующей инструкции
- **Instruction Register (IR):** текущая инструкция
- **Accumulator:** результаты операций
- **General Purpose (R0-R15, RAX-R15):** данные для вычислений
- **Stack Pointer (SP):** вершина стека
- **Flags/Status:** результаты сравнений (zero, carry, overflow)

**Размеры:**
- 32-bit: 4 bytes, старые процессоры
- 64-bit: 8 bytes, современные CPU

### 2. Instruction Cycle

**Fetch → Decode → Execute:**

1. **Fetch:** Загрузка инструкции из памяти по адресу в PC
2. **Decode:** Интерпретация инструкции, определение операции
3. **Execute:** Выполнение (ALU, memory access, branch)
4. **Memory:** Чтение/запись в память (если нужно)
5. **Write Back:** Запись результата в регистр

### 3. Pipelining

**Идея:**
Разбить выполнение на стадии, выполнять несколько инструкций одновременно.

**RISC 5-stage pipeline:**
| Cycle | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 |
|-------|---------|---------|---------|---------|---------|
| 1 | Fetch I1 | | | | |
| 2 | Fetch I2 | Decode I1 | | | |
| 3 | Fetch I3 | Decode I2 | Execute I1 | | |
| 4 | Fetch I4 | Decode I3 | Execute I2 | Memory I1 | |
| 5 | Fetch I5 | Decode I4 | Execute I3 | Memory I2 | WB I1 |

**Pipeline hazards:**
- Data hazards: зависимость от предыдущей инструкции
- Control hazards: branches, jumps
- Structural hazards: конфликт ресурсов

### 4. Cache Hierarchy

| Cache | Размер | Latency | Скорость vs RAM |
|-------|--------|---------|-----------------|
| L1 | 32-128 KB | 1-3 cycles | ~100x |
| L2 | 256 KB - 1 MB | ~10 cycles | ~25x |
| L3 | 4-64 MB | ~40 cycles | ~2x |
| RAM | 8-64 GB | ~100+ cycles | 1x |

**L1 Cache:**
- Split: I-cache (инструкции) + D-cache (данные)
- Per-core
- Fastest

**L2 Cache:**
- Per-core
- Больше, медленнее L1

**L3 Cache:**
- Shared между ядрами
- Largest, slowest cache

### 5. Cache Hit/Miss

**Cache hit:** Данные найдены в cache → быстрый доступ
**Cache miss:** Данные не в cache → загрузка из RAM (медленно)

**Locality of reference:**
- Temporal: недавно используемое будет использоваться снова
- Spatial: данные рядом с используемыми тоже нужны

### 6. Для программистов

**Оптимизации:**
- Data locality: хранить связанные данные рядом
- Cache-friendly loops: итерировать по непрерывной памяти
- Avoid cache pollution: не загружать ненужные данные
- Branch prediction hints

## Community Sentiment

### Positive
- Понимание CPU помогает оптимизировать код
- Cache-aware programming даёт значительный speedup
- Pipelining объясняет почему branches дорогие

### Negative
- Сложная тема для новичков
- Детали зависят от конкретного CPU
- Over-optimization редко нужна

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Wikipedia: CPU](https://en.wikipedia.org/wiki/Central_processing_unit) | Reference | ★★★★★ | Comprehensive |
| [Wikipedia: CPU Cache](https://en.wikipedia.org/wiki/CPU_cache) | Reference | ★★★★★ | Cache details |
| [Bottom Up CS: Chapter 3](https://www.bottomupcs.com/ch03.html) | Book | ★★★★★ | For programmers |
| [Wikipedia: Instruction Pipelining](https://en.wikipedia.org/wiki/Instruction_pipelining) | Reference | ★★★★☆ | Pipeline explained |
| [GeeksforGeeks: Cache Memory](https://www.geeksforgeeks.org/cache-memory-in-computer-organization/) | Tutorial | ★★★★☆ | Clear examples |

## Research Methodology
- **Queries used:** 2 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **Focus areas:** Registers, pipeline, cache hierarchy

---

*Проверено: 2026-01-09*

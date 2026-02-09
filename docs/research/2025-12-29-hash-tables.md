---
title: "Research Report: Hash Tables"
created: 2025-12-29
modified: 2025-12-29
type: concept
status: draft
tags:
  - topic/cs-fundamentals
  - topic/data-structures
---

# Research Report: Hash Tables

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Hash Table — структура данных с O(1) average для insert/search/delete. Использует hash function для вычисления индекса в массиве. Collision resolution: Separate Chaining (linked lists) или Open Addressing (probing). Java HashMap: load factor 0.75, rehashing при превышении threshold, treeification при 8+ collisions (Java 8+). Ключевые паттерны: Two Sum, Frequency Counter, Group Anagrams.

---

## Key Findings

### 1. Hash Table Operations

| Operation | Average | Worst |
|-----------|---------|-------|
| Search | O(1) | O(n) |
| Insert | O(1) | O(n) |
| Delete | O(1) | O(n) |
| Space | O(n) | O(n) |

### 2. Collision Resolution

**Separate Chaining:**
- Каждый bucket содержит linked list
- Простая реализация
- Неограниченный размер
- Плохая cache locality

**Open Addressing:**
- Все элементы в одном массиве
- Linear Probing: i+1, i+2, i+3...
- Quadratic Probing: i+1², i+2², i+3²...
- Double Hashing: i + j*hash2(key)
- Лучше cache, но clustering проблема

### 3. Hash Function Properties

- **Deterministic**: одинаковый input → одинаковый output
- **Uniform Distribution**: равномерное распределение
- **Fast Computation**: O(key length)
- **Avalanche Effect**: small change → big difference
- **Use All Input**: все биты ключа участвуют

### 4. Java HashMap Internals

| Parameter | Default | Description |
|-----------|---------|-------------|
| Initial Capacity | 16 | Начальный размер |
| Load Factor | 0.75 | Порог rehashing |
| Treeify Threshold | 8 | Переход в Red-Black Tree |
| Untreeify Threshold | 6 | Обратно в linked list |

**Rehashing:** когда size > capacity * loadFactor, создаётся новый массив (2x), все элементы перехешируются.

### 5. Interview Patterns

| Pattern | Example Problems |
|---------|-----------------|
| **Two Sum** | Two Sum, 3Sum, 4Sum |
| **Frequency Counter** | Top K Frequent, Valid Anagram |
| **Grouping** | Group Anagrams |
| **Prefix Sum + Hash** | Subarray Sum Equals K |
| **Design** | LRU Cache, Insert Delete Random O(1) |

### 6. When HashMap vs HashSet

- **HashMap**: key → value mapping (number → index)
- **HashSet**: только membership (is X in set?)

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Tech Interview Handbook - Hash Table](https://www.techinterviewhandbook.org/algorithms/hash-table/) | Guide | 0.95 |
| 2 | [GeeksforGeeks - Hash Table](https://www.geeksforgeeks.org/dsa/hash-table-data-structure/) | Tutorial | 0.90 |
| 3 | [Wikipedia - Hash Table](https://en.wikipedia.org/wiki/Hash_table) | Reference | 0.95 |
| 4 | [Baeldung - Java HashMap Load Factor](https://www.baeldung.com/java-hashmap-load-factor) | Tutorial | 0.90 |
| 5 | [GeeksforGeeks - Load Factor and Rehashing](https://www.geeksforgeeks.org/dsa/load-factor-and-rehashing/) | Tutorial | 0.90 |
| 6 | [LeetCode - Hashtable Patterns Guide](https://leetcode.com/discuss/study-guide/4042753/**-Mastering-Hashtable-Patterns:-A-Comprehensive-Guide/) | Patterns | 0.90 |

---

*Generated: 2025-12-29*

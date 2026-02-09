# Research Report: Meet in the Middle Pattern (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Meet in the Middle splits a problem into two halves, solves each independently, then combines results. Reduces O(2^n) to O(2^(n/2) * n). Applicable when n ≤ 40 and brute force is too slow.

## Key Insights

> "The meet-in-middle algorithm is a search technique used when the input size is small but not small enough for brute force. It splits input into two subsets, solves them, then combines results." — [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/meet-in-the-middle/)

> "Given n integers where n <= 40, each element at most 10¹², determine maximum subset sum ≤ S where S ≤ 10¹⁸." — [USACO Guide](https://usaco.guide/gold/meet-in-the-middle)

> "Binary search helps reduce complexity from 2^n to 2^(n/2) * log(2^(n/2)) which is 2^(n/2) * n." — [InfoArena](https://www.infoarena.ro/blog/meet-in-the-middle)

## Algorithm Steps

```
1. Split input array A into two halves: left[0..n/2], right[n/2..n]
2. Generate all 2^(n/2) subset sums for left → leftSums[]
3. Generate all 2^(n/2) subset sums for right → rightSums[]
4. Sort rightSums
5. For each sum in leftSums:
   - Binary search in rightSums for best complementary value
   - Update answer
```

## Complexity Analysis

| Approach | Time | Space | Limit |
|----------|------|-------|-------|
| Brute Force | O(2^n) | O(n) | n ≤ 20 |
| Meet in Middle | O(2^(n/2) * n) | O(2^(n/2)) | n ≤ 40 |

For n = 40:
- Brute Force: 2^40 ≈ 10^12 (too slow)
- Meet in Middle: 2^20 * 40 ≈ 4 * 10^7 (feasible)

## Classic Problems

1. **Subset Sum ≤ S**: Find max subset sum not exceeding S
2. **4-SUM**: Find 4 numbers summing to target (split into pairs)
3. **Equal Partition**: Split array into two equal-sum halves
4. **Bidirectional BFS**: 6 degrees of separation

## LeetCode Problems
- 1755. Closest Subsequence Sum (n ≤ 40)
- 805. Split Array With Same Average
- 18. 4Sum (can use meet in middle approach)
- 454. 4Sum II (split into two halves)
- 2035. Partition Array Into Two Arrays to Minimize Sum Difference

## When to Use

✅ Use when:
- n ≤ 40 (brute force too slow, DP too large)
- Problem involves subset/combination enumeration
- Can split problem into independent halves
- Results can be combined with sorting + binary search

❌ Don't use when:
- n > 45 (2^22.5 still too large)
- n ≤ 20 (brute force works)
- Problem has overlapping subproblems (use DP instead)

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/meet-in-the-middle/) | Tutorial | 0.90 | Algorithm |
| 2 | [USACO Guide](https://usaco.guide/gold/meet-in-the-middle) | Guide | 0.95 | Competitive |
| 3 | [LeetCode](https://leetcode.com/discuss/interview-question/2077168/meet-in-the-middle-algorithm-subset-bitmask/) | Discuss | 0.85 | Interview |
| 4 | [InfoArena](https://www.infoarena.ro/blog/meet-in-the-middle) | Blog | 0.85 | Complexity |
| 5 | [Codeforces](https://codeforces.com/blog/entry/95571) | Blog | 0.90 | Advanced |

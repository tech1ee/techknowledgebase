# Research Report: Bit Manipulation Pattern (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Bit manipulation uses bitwise operations for efficient problem-solving. Key patterns: XOR for unique elements, `n & (n-1)` to clear lowest bit, bitmask DP for subset problems. Essential for systems programming and coding interviews.

## Key Insights

> "XOR of all elements will give us the unique element. XOR of a number with itself is 0, and XOR of a number with 0 is the number itself." — [InterviewBit](https://www.interviewbit.com/courses/programming/bit-manipulation/)

> "A number is a power of two if n & (n - 1) equals 0, and n > 0. This works because powers of two have only one bit set to 1." — [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/bits-manipulation-important-tactics/)

> "DP + Bitmasks is a well-known technique. This trick is usually used when one of the variables have very small constraints that can allow exponential solutions." — [LeetCode](https://leetcode.com/discuss/post/3695233/all-types-of-patterns-for-bits-manipulat-qezp/)

## Core Bitwise Operations

| Operation | Symbol | Description | Example |
|-----------|--------|-------------|---------|
| AND | & | 1 if both 1 | 5 & 3 = 1 |
| OR | \| | 1 if any 1 | 5 \| 3 = 7 |
| XOR | ^ | 1 if different | 5 ^ 3 = 6 |
| NOT | ~ | Flip all bits | ~5 = -6 |
| Left Shift | << | Multiply by 2^n | 5 << 1 = 10 |
| Right Shift | >> | Divide by 2^n | 5 >> 1 = 2 |

## Essential Tricks

| Pattern | Code | Purpose |
|---------|------|---------|
| Check if even | `n & 1 == 0` | Last bit is 0 |
| Check power of 2 | `n & (n-1) == 0` | Only one bit set |
| Clear lowest bit | `n & (n-1)` | Remove rightmost 1 |
| Get lowest bit | `n & (-n)` | Isolate rightmost 1 |
| Set bit at pos | `n \| (1 << pos)` | Turn on bit |
| Clear bit at pos | `n & ~(1 << pos)` | Turn off bit |
| Toggle bit at pos | `n ^ (1 << pos)` | Flip bit |
| Check bit at pos | `(n >> pos) & 1` | Get bit value |

## Bitmask DP Pattern
```
// Iterate over all subsets (2^n)
for mask in 0..(1 << n):
    for i in 0..n:
        if (mask >> i) & 1:
            // i-th element is in subset
```

## LeetCode Problems
- 136. Single Number (XOR all elements)
- 137. Single Number II (count bits mod 3)
- 260. Single Number III (XOR + split by lowest bit)
- 191. Number of 1 Bits (Brian Kernighan)
- 231. Power of Two (n & (n-1) == 0)
- 338. Counting Bits (DP + bit manipulation)
- 78. Subsets (bitmask enumeration)
- 1239. Maximum Length of Concatenated String (bitmask DP)

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [InterviewBit](https://www.interviewbit.com/courses/programming/bit-manipulation/) | Course | 0.90 | XOR patterns |
| 2 | [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/bits-manipulation-important-tactics/) | Tutorial | 0.90 | Bit tricks |
| 3 | [AlgoCademy](https://algocademy.com/blog/approaching-bit-manipulation-problems-a-comprehensive-guide-for-coding-interviews/) | Guide | 0.85 | Interview prep |
| 4 | [DevInterview](https://devinterview.io/blog/bit-manipulation-interview-questions/) | Interview | 0.85 | Questions 2025 |
| 5 | [LeetCode](https://leetcode.com/discuss/post/3695233/all-types-of-patterns-for-bits-manipulat-qezp/) | Discuss | 0.80 | Patterns |

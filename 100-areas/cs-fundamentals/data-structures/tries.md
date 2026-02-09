---
title: "Префиксное дерево (Trie)"
created: 2025-12-29
modified: 2026-01-06
type: deep-dive
status: published
difficulty: intermediate
confidence: high
cs-foundations:
  - tree-data-structure
  - prefix-sharing
  - space-time-tradeoff
  - string-processing
  - dfs-traversal
  - alphabet-branching-factor
prerequisites:
  - "[[trees-binary]]"
  - "[[hash-tables]]"
  - "[[arrays-strings]]"
  - "[[recursion-fundamentals]]"
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/intermediate
  - interview
related:
  - "[[graphs]]"
  - "[[dfs-bfs-patterns]]"
  - "[[backtracking]]"
  - "[[dynamic-programming]]"
---

# Trie (Префиксное дерево)

## TL;DR

Trie (произносится "трай") — дерево для хранения строк, где каждый узел представляет символ. Все операции (insert, search, startsWith) выполняются за **O(m)**, где m — длина строки, независимо от количества слов. Идеально для **автодополнения**, **проверки орфографии** и **поиска по префиксу**. Два варианта хранения детей: массив[26] (быстрее) или HashMap (экономнее по памяти).

---

## Часть 1: Интуиция без кода

### Аналогия 1: Поиск в телефонной книге

Представь старую бумажную телефонную книгу с алфавитными закладками:

```
┌─────────────────────────────────────────┐
│         ТЕЛЕФОННАЯ КНИГА                │
├────┬────┬────┬────┬────┬────┬────┬─────┤
│ А  │ Б  │ В  │ ... │ И  │ ... │ Я  │    │
└────┴────┴────┴────┴────┴────┴────┴─────┘
```

Ищешь "Иванов"? Не нужно листать с начала!
1. Открываешь закладку "И"
2. На странице "И" ищешь "Ив"
3. Среди "Ив" ищешь "Ива"
4. И так далее...

**Это и есть Trie** — вместо просмотра ВСЕХ записей, ты идёшь по "указателям" букв.

### Аналогия 2: Автодополнение в Google

> "If you type something in a text box and you see a list of potential searches with same prefix, that's probably being handled by a Trie behind the scenes." — [Interview Cake](https://www.interviewcake.com/concept/java/trie)

```
Ты печатаешь: "прог"

Google мгновенно показывает:
┌──────────────────────────────┐
│ 🔍 прог                      │
├──────────────────────────────┤
│   программирование           │
│   программа телепередач      │
│   прогноз погоды             │
│   прогресс                   │
└──────────────────────────────┘

КАК ЭТО РАБОТАЕТ?

В памяти Google есть Trie со всеми запросами:

        [root]
           │
          [п]
           │
          [р]
           │
          [о]
           │
          [г]  ← ТЫ СЕЙЧАС ЗДЕСЬ (после ввода "прог")
         / | \
       [р][н][...]
        |   |
       ... [о]
            |
           [з]* ← "прогноз"

Все слова ПОД узлом "г" — это автодополнения!
```

### Аналогия 3: Организованный шкаф для слов

> "Think of it as a super-organized closet for your words, where each letter is a hanger, and the words are the clothes hanging neatly in order." — [YouCademy](https://youcademy.org/trie-data-structure/)

```
ОБЫЧНЫЙ ШКАФ (список):              TRIE-ШКАФ (дерево):
┌────────────────────┐              ┌─────────────────────────┐
│ cat                │              │         [шкаф]          │
│ car                │              │        /      \         │
│ card               │              │      [c]      [d]       │
│ dog                │              │       |        |        │
└────────────────────┘              │      [a]      [o]       │
                                    │     / | \      |        │
Найти все на "ca"?                  │   [t][r]*    [g]*       │
→ Просмотреть ВСЕ слова              │       |                │
→ O(n) операций                     │      [d]*               │
                                    └─────────────────────────┘

                                    Найти все на "ca"?
                                    → Спуститься c→a
                                    → Собрать всё поддерево
                                    → O(m) где m = длина "ca"
```

### Почему "Trie", а не "Tree"?

```
┌──────────────────────────────────────────────────────────────────┐
│ ВАЖНО: Произносится "ТРАЙ", не "ТРИ"!                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Название происходит от re-TRIE-val (извлечение).                 │
│                                                                  │
│ Автор структуры Edward Fredkin (1960) произносил "трай",         │
│ чтобы отличать от слова "tree" (дерево) в устной речи.           │
│                                                                  │
│ ❌ "три"  — неправильно (путается с tree)                        │
│ ✅ "трай" — правильно (от retrieval)                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Ключевая идея: Общие префиксы хранятся ОДИН раз

```
Слова: "car", "cat", "card", "care"

БЕЗ Trie (HashSet): каждое слово хранится отдельно
  "car"  → 3 символа
  "cat"  → 3 символа
  "card" → 4 символа
  "care" → 4 символа
  ИТОГО: 14 символов

С Trie: общие префиксы хранятся один раз
            [root]
               |
              [c] ← 1 символ
               |
              [a] ← 1 символ
             / | \
           [t]*[r]* \
               |\   [r] (второй r не нужен, используем тот же!)
             [d]*[e]*

  Уникальные узлы: c, a, t, r, d, e = 6 символов
  ЭКОНОМИЯ: 14 - 6 = 8 символов!

Чем больше общих префиксов, тем больше экономия.
```

---

## Часть 2: Почему Trie сложный (типичные ошибки)

### Ошибка 1: Забыли флаг "конец слова" (isEndOfWord)

> **Ключевой вопрос:** "What happens if we have two words and one is a prefix of the other?" — [Interview Cake](https://www.interviewcake.com/concept/java/trie)

```
Вставляем: "car" и "card"

              [root]
                 |
                [c]
                 |
                [a]
                 |
                [r]  ← Это слово "car"? Или просто часть "card"?
                 |
                [d]  ← Это слово "card"

ПРОБЛЕМА: Без флага мы не можем отличить!

❌ НЕПРАВИЛЬНО:
search("car") → нашли путь c-a-r → true
НО это может быть просто ПРЕФИКС слова "card"!

✅ ПРАВИЛЬНО: Помечаем узлы флагом isEndOfWord
              [root]
                 |
                [c]
                 |
                [a]
                 |
                [r]* ← isEndOfWord = true (слово "car")
                 |
                [d]* ← isEndOfWord = true (слово "card")

search("car") → нашли путь c-a-r, isEndOfWord=true → TRUE
search("ca")  → нашли путь c-a, isEndOfWord=false → FALSE (только префикс)
```

### Ошибка 2: "Trie экономит память" — НЕ ВСЕГДА!

> "Tries rarely save space when compared to storing strings in a set. Each link between trie nodes is a pointer — eight bytes on a 64-bit system." — [Interview Cake](https://www.interviewcake.com/concept/java/trie)

```
РЕАЛЬНОСТЬ: Trie часто ТРАТИТ больше памяти!

Почему? Каждый узел хранит:
- 26 указателей (для a-z) × 8 байт = 208 байт
- isEndOfWord флаг = 1 байт
- ИТОГО: ~209 байт на УЗЕЛ

Сравни:
- Слово "cat" в HashSet: 3 байта (3 символа)
- Слово "cat" в Trie: 3 узла × 209 байт = 627 байт!

┌──────────────────────────────────────────────────────────────────┐
│                    КОГДА TRIE ЭКОНОМИТ ПАМЯТЬ?                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ✅ Много слов с общими префиксами                                │
│    Пример: словарь английского (много слов на "un-", "re-")      │
│                                                                  │
│ ✅ HashMap-based Trie (не Array[26])                             │
│    Хранит только реальных детей                                  │
│                                                                  │
│ ❌ Мало слов                                                     │
│ ❌ Случайные строки (нет общих префиксов)                        │
│ ❌ Array[26] на каждый узел (209 байт)                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Ошибка 3: Trie vs HashMap — неправильный выбор

```
┌──────────────────────────────────────────────────────────────────┐
│                    TRIE vs HASHMAP: КОГДА ЧТО?                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   НУЖЕН ПОИСК ПО ПРЕФИКСУ?                                       │
│   "Найди все слова на 'prog'"                                    │
│        │                                                         │
│   ┌────┴────┐                                                    │
│   │  ДА     │                                                    │
│   │  ↓      │                                                    │
│   │ TRIE    │         HashMap НЕ ПОДХОДИТ!                       │
│   │ O(m+k)  │         HashMap.filter { startsWith("prog") }      │
│   └─────────┘         = O(n) — нужно проверить ВСЕ слова         │
│                                                                  │
│   НУЖЕН ТОЛЬКО ТОЧНЫЙ ПОИСК?                                     │
│   "Есть ли слово 'programming'?"                                 │
│        │                                                         │
│   ┌────┴────┐                                                    │
│   │  ДА     │                                                    │
│   │  ↓      │                                                    │
│   │ HASHSET │         Trie избыточен!                            │
│   │  O(1)   │         Trie.search("programming") = O(11)         │
│   └─────────┘                                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Ошибка 4: Регистр символов (Case Sensitivity)

```kotlin
// ❌ ОШИБКА: 'A' - 'a' = -32, выход за границы массива!
fun insert(word: String) {
    for (c in word) {
        val index = c - 'a'  // 'A' даёт -32!
        node.children[index] = ...  // ArrayIndexOutOfBoundsException!
    }
}

// ✅ РЕШЕНИЕ 1: Нормализация к lowercase
fun insert(word: String) {
    for (c in word.lowercase()) {
        val index = c - 'a'
        // ...
    }
}

// ✅ РЕШЕНИЕ 2: HashMap вместо Array[26]
class TrieNode {
    val children = mutableMapOf<Char, TrieNode>()  // любые символы!
}
```

### Ошибка 5: Удаление слова — каскадная очистка

```
Удаляем "car" из Trie с ["car", "card"]:

❌ НЕПРАВИЛЬНО: Просто снять флаг isEndOfWord

              [root]                      [root]
                 |                           |
                [c]         →               [c]
                 |                           |
                [a]                         [a]
                 |                           |
                [r]*  isEndOfWord=false     [r]  ← узел остаётся!
                 |                           |
                [d]*                        [d]*

Проблема: узел [r] занимает память, хотя используется только
как промежуточный для "card"

✅ ПРАВИЛЬНО: Каскадное удаление неиспользуемых узлов

1. isEndOfWord[r] = false
2. Проверяем: у [r] есть дети? → Да, [d] → НЕ удаляем [r]

Если бы удаляли "card" из ["car", "card"]:
1. isEndOfWord[d] = false
2. У [d] есть дети? → Нет → УДАЛЯЕМ [d]
3. У [r] теперь нет детей и isEndOfWord=true → НЕ удаляем [r]
```

---

## Часть 3: Ментальные модели

### Модель 1: Алфавитный указатель (для поиска)

```
Представь энциклопедию с многоуровневым указателем:

УРОВЕНЬ 1: Первая буква
┌─────┬─────┬─────┬─────┬─────┐
│  A  │  B  │  C  │  D  │ ... │
└──┬──┴─────┴──┬──┴─────┴─────┘
   │           │
   ▼           ▼
УРОВЕНЬ 2: Вторая буква
┌─────┬─────┐  ┌─────┬─────┐
│ AA  │ AB  │  │ CA  │ CO  │
└──┬──┴─────┘  └──┬──┴─────┘
   │              │
   ▼              ▼
...             ...

Поиск слова = спуск по уровням указателя
Автодополнение = собрать всё под текущим уровнем
```

**Когда использовать эту модель:**
- Понимание структуры Trie
- Объяснение O(m) сложности поиска
- Визуализация "пути" к слову

### Модель 2: Дерево решений (для вставки)

```
Вставляем слово "cat":

Вопрос 1: Какая первая буква?
          [c]
Вопрос 2: Какая вторая буква?
          [a]
Вопрос 3: Какая третья буква?
          [t]
Вопрос 4: Слово закончилось?
          → ДА → помечаем isEndOfWord = true

Каждый узел = ответ на вопрос "какая следующая буква?"
Путь от корня = последовательность ответов = слово
```

**Когда использовать эту модель:**
- Объяснение алгоритма вставки
- Понимание isEndOfWord
- Рекурсивный обход

### Модель 3: GPS-навигатор (для автодополнения)

```
Ты ввёл "прог" — навигатор показывает все возможные маршруты:

     [п] → [р] → [о] → [г]
                         │
              ┌──────────┼──────────┐
              │          │          │
            [р]        [н]        [р]
              │          │          │
            [а]        [о]        [е]
              │          │          │
            [м]*       [з]*       [с]*
              │                     │
            [м]*                   [с]*
              │
            [и]*
              │
            [р]*
              │
           [о]*
              │
           [в]*
              │
           [а]*
              │
           [н]*
              │
           [и]*
              │
           [е]*

Все конечные точки (*) = варианты автодополнения:
- программа, программирование
- прогноз
- прогресс
```

**Когда использовать эту модель:**
- Функция getAllWithPrefix
- DFS для сбора всех слов
- Понимание поддерева под префиксом

### Модель 4: Фильтр (для понимания эффективности)

```
ПРОБЛЕМА: Найти все слова на "pro" среди 1 миллиона слов

БЕЗ TRIE (HashSet):
┌─────────────────────────────────────────────────────────────────┐
│ 1,000,000 слов → ФИЛЬТР (startsWith "pro") → результаты        │
│                                                                 │
│ Проверяем КАЖДОЕ слово: O(n × m)                                │
└─────────────────────────────────────────────────────────────────┘

С TRIE:
┌─────────────────────────────────────────────────────────────────┐
│         [root]                                                  │
│        /  |  \                                                  │
│      [a] [p] [z]                                                │
│           |                                                     │
│          [r]                                                    │
│           |                                                     │
│          [o]  ← Мгновенно дошли до этого узла!                  │
│         / | \                                                   │
│       [g][b][...]  ← ВСЁ ПОДДЕРЕВО = ответ                      │
│                                                                 │
│ Спускаемся за O(3), собираем поддерево за O(k)                  │
│ где k = количество результатов (не n!)                          │
└─────────────────────────────────────────────────────────────────┘
```

**Когда использовать эту модель:**
- Объяснение преимущества Trie над HashSet
- Понимание O(m + k) vs O(n × m)
- Масштабирование на большие словари

### Сравнительная таблица: Когда какую модель использовать

```
┌──────────────────────────────────────────────────────────────────┐
│                    МОДЕЛИ МЫШЛЕНИЯ О TRIE                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  МОДЕЛЬ             │ ЛУЧШЕ ВСЕГО ДЛЯ                           │
│  ──────────────────────────────────────────────────────────────  │
│  Алфавитный указатель │ Понимание структуры, визуализация       │
│                        │                                         │
│  Дерево решений        │ Алгоритм вставки, isEndOfWord           │
│                        │                                         │
│  GPS-навигатор         │ Автодополнение, DFS-обход               │
│                        │                                         │
│  Фильтр                │ Сравнение с HashSet, эффективность      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Зачем это нужно?

### Мотивирующая проблема

**Задача: Поисковая строка Google**

У тебя есть словарь из 1 миллиона слов. Пользователь печатает "prog" и хочет увидеть все слова, начинающиеся с этого префикса:
- program
- programming
- progress
- ...

**Как найти все слова с префиксом "prog"?**

```
Вариант 1: Проверить каждое слово
for word in dictionary:
    if word.startsWith("prog"):
        results.add(word)
→ O(n * m) где n = 1M слов — МЕДЛЕННО

Вариант 2: HashSet
hashSet.contains("prog")  // O(1)
→ Проблема: находит только точное совпадение, не префиксы!

Вариант 3: Отсортированный список + бинарный поиск
→ O(log n) найти начало, но O(k) собрать все совпадения

Вариант 4: Trie (Префиксное дерево)
→ O(m) дойти до узла "prog"
→ Все поддерево — это слова с префиксом "prog"
→ Идеально!
```

### Где используются Trie?

| Область | Применение | Пример |
|---------|------------|--------|
| Поисковые системы | Автодополнение | Google Search |
| IDE | Автокомплит кода | IntelliJ IDEA |
| Браузеры | История URL | Chrome omnibox |
| Телефоны | T9 ввод | Старые Nokia |
| Spell checkers | Проверка орфографии | Microsoft Word |
| Сети | IP routing | Longest prefix match |
| Игры | Словарные игры | Scrabble, Wordle |

**Факт:** Google обрабатывает 8.5 миллиардов поисков в день. Без Trie автодополнение занимало бы секунды вместо миллисекунд.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Binary Trees | Trie — это дерево, понимание parent-child связей критично | [[trees-binary]] |
| Hash Tables | HashMap — альтернативное хранение детей узла | [[hash-tables]] |
| Strings/Arrays | Строки — это массивы символов, работа с индексами | [[arrays-strings]] |
| Recursion | DFS обход Trie рекурсивен (delete, collect all words) | [[recursion-fundamentals]] |
| **CS: Character Encoding** | Понимание ASCII/Unicode для индексации `char - 'a'` | Символы = числа |
| **CS: Tree Traversal** | DFS для сбора всех слов, BFS для level-order | Обход деревьев |

---

## Что это такое?

### Объяснение для 5-летнего

Представь, что ты организуешь книги в библиотеке:
- Все книги на "А" — на одной полке
- На полке "А" есть подполки: "Ав", "Ан", "Ар"...
- На подполке "Ан" есть: "Анд", "Анн"...
- И так далее

Чтобы найти книгу "Андерсен", ты идёшь: А → Ан → Анд → Анде → Андер → Андерс → Андерсе → Андерсен

Не нужно перебирать все книги — только идти по "указателям"!

```
          [root]
         /   |   \
       [a]  [b]  [c]
       /     |
     [n]    [a]
     /       |
   [d]      [t]  ← "bat"
   /
 [e]
  |
 [r]
  |
 [s]
  |
 [e]
  |
 [n]* ← "andersen" (* = конец слова)
```

### Формальное определение

**Trie (Prefix Tree)** — это древовидная структура данных для хранения множества строк, где:

1. **Корень** представляет пустую строку
2. **Каждый узел** представляет один символ
3. **Путь от корня** к узлу = префикс
4. **Узлы помечаются** флагом `isEndOfWord` для обозначения конца слова
5. **Дети узла** — следующие возможные символы

```
Хранение слов: ["cat", "car", "card", "care", "dog"]

               [root]
              /      \
           [c]       [d]
            |         |
           [a]       [o]
          / | \       |
        [t]*[r]*    [g]*
             |\
           [d]*[e]*

* = isEndOfWord = true

Путь root→c→a→r = "car" ✓
Путь root→c→a→r→d = "card" ✓
Путь root→c→a = "ca" (не слово, isEndOfWord = false)
```

### Свойства Trie

| Свойство | Описание |
|----------|----------|
| Без дублирования | Общие префиксы хранятся один раз |
| Детерминированный | Каждая строка имеет единственный путь |
| Быстрый поиск | O(m) независимо от размера словаря |
| Префиксный поиск | Естественная поддержка startsWith |
| Сортировка | DFS даёт слова в лексикографическом порядке |

---

## Терминология

| Термин | Английский | Определение | Пример |
|--------|------------|-------------|--------|
| Trie | Trie, Prefix Tree | Дерево для хранения строк по символам | Словарь автодополнения |
| Корень | Root | Узел, представляющий пустую строку | Начало всех слов |
| Узел | Node | Содержит символ и ссылки на детей | Буква 'a' |
| Ребро | Edge | Связь родитель→ребёнок, представляет символ | 'a' → 'b' |
| isEndOfWord | Terminal flag | Флаг: узел — конец валидного слова | true для "cat" |
| Префикс | Prefix | Путь от корня до любого узла | "ca" для "cat" |
| Словарь | Dictionary | Множество слов, хранимых в Trie | ["cat", "car"] |
| Radix Tree | Compressed Trie | Trie со сжатыми цепочками | "tion" как один узел |
| Wildcard | Wildcard | Символ, соответствующий любому | '.' в regex |

---

## Как это работает?

### Операция: Insert

```
Вставляем "cat" в пустой Trie:

Шаг 1: Начинаем с корня
[root]

Шаг 2: Добавляем 'c' (нет ребёнка 'c' → создаём)
[root]
   |
  [c]

Шаг 3: Добавляем 'a' (нет ребёнка 'a' у 'c' → создаём)
[root]
   |
  [c]
   |
  [a]

Шаг 4: Добавляем 't' (нет ребёнка 't' у 'a' → создаём)
[root]
   |
  [c]
   |
  [a]
   |
  [t]

Шаг 5: Помечаем 't' как конец слова
[root]
   |
  [c]
   |
  [a]
   |
  [t]* ← isEndOfWord = true

Теперь вставляем "car":

Шаг 1-2: root → 'c' → 'a' (узлы уже существуют!)
Шаг 3: Добавляем 'r' (нет ребёнка 'r' у 'a')
[root]
   |
  [c]
   |
  [a]
  / \
[t]* [r]*
```

### Операция: Search

```
Ищем "car" в Trie с ["cat", "car", "card"]:

        [root]
           |
          [c]
           |
          [a]
          / \
       [t]* [r]*
              |
            [d]*

Шаг 1: root → ищем ребёнка 'c' → найден
Шаг 2: [c] → ищем ребёнка 'a' → найден
Шаг 3: [a] → ищем ребёнка 'r' → найден
Шаг 4: Строка закончилась, проверяем isEndOfWord
       [r].isEndOfWord = true → НАЙДЕНО!

Ищем "ca":
Шаги 1-2: root → 'c' → 'a' → найдены
Шаг 3: Строка закончилась, isEndOfWord = false → НЕ НАЙДЕНО
       (префикс есть, но не слово)

Ищем "can":
Шаги 1-2: root → 'c' → 'a'
Шаг 3: [a] → ищем ребёнка 'n' → НЕТ → НЕ НАЙДЕНО
```

### Операция: StartsWith (Prefix Search)

```
Проверяем, есть ли слова с префиксом "ca":

        [root]
           |
          [c]
           |
          [a]   ← Дошли сюда = префикс существует!
          / \
       [t]* [r]*

Шаг 1: root → 'c' → найден
Шаг 2: [c] → 'a' → найден
Шаг 3: Префикс исчерпан, узел существует → TRUE

Все слова с префиксом "ca" — это всё поддерево под 'a':
- cat (путь: a → t)
- car (путь: a → r)
- card (путь: a → r → d)
```

### Операция: Delete

```
Удаляем "car" из ["cat", "car", "card"]:

До:                          После:
     [root]                      [root]
        |                           |
       [c]                         [c]
        |                           |
       [a]                         [a]
       / \                         / \
    [t]* [r]*    ←удаляем       [t]* [r]   ← убираем флаг
            |                         |
          [d]*                      [d]*

Шаг 1: Находим узел 'r' (конец "car")
Шаг 2: Снимаем флаг isEndOfWord = false
Шаг 3: НЕ удаляем узел 'r', т.к. у него есть ребёнок 'd' ("card")

Если удаляем "card":
Шаг 1: isEndOfWord['d'] = false
Шаг 2: 'd' не имеет детей → удаляем узел
Шаг 3: 'r' теперь не имеет детей и isEndOfWord=false → удаляем
       (каскадное удаление пока не встретим isEndOfWord=true или детей)
```

---

## Сложность операций

### Основные операции

| Операция | Время | Память | Описание |
|----------|-------|--------|----------|
| insert | O(m) | O(m) | m = длина слова |
| search | O(m) | O(1) | m = длина слова |
| startsWith | O(m) | O(1) | m = длина префикса |
| delete | O(m) | O(1) | m = длина слова |
| getAllWithPrefix | O(m + k) | O(k) | k = количество результатов |

### Память

| Реализация | Память на узел | Общая память |
|------------|---------------|--------------|
| Array[26] | 26 указателей + 1 bool | O(n * 26) |
| HashMap | В среднем 2-5 указателей | O(n * avg_children) |

Где n = общее количество символов во всех словах.

### Сравнение с альтернативами

| Операция | Trie | HashSet | Sorted Array |
|----------|------|---------|--------------|
| Insert | O(m) | O(m) | O(n) |
| Search exact | O(m) | O(m) avg | O(m log n) |
| Prefix search | O(m + k) | O(n * m) | O(log n + k) |
| Space | O(Σm) | O(Σm) | O(Σm) |
| Ordered iteration | Natural | Need sort | Natural |

---

## Реализация

### Kotlin — Array-based Trie (для lowercase a-z)

```kotlin
/**
 * Trie для слов из строчных латинских букв
 *
 * WHY array[26]: фиксированный алфавит, O(1) доступ к ребёнку
 * Trade-off: быстрее HashMap, но 26 указателей на каждый узел
 */
class TrieNode {
    // WHY 26: только lowercase a-z, индекс = char - 'a'
    val children = arrayOfNulls<TrieNode>(26)
    var isEndOfWord = false
}

class Trie {
    private val root = TrieNode()

    /**
     * Вставляет слово в Trie
     *
     * WHY traverse + create: идём по существующим узлам,
     * создаём новые только когда нужно
     *
     * Time: O(m), Space: O(m) worst case (все новые узлы)
     */
    fun insert(word: String) {
        var node = root

        for (char in word) {
            // Конвертируем символ в индекс массива:
            // 'a' - 'a' = 0, 'b' - 'a' = 1, ..., 'z' - 'a' = 25
            // Это работает потому что коды символов идут подряд
            val index = char - 'a'

            if (node.children[index] == null) {
                node.children[index] = TrieNode()  // Создаём новый узел
            }
            node = node.children[index]!!  // Переходим к ребёнку
        }

        // ВАЖНО: помечаем конец слова!
        // Без этого не отличить "car" (слово) от "car" (префикс "card")
        node.isEndOfWord = true
    }

    /**
     * Проверяет наличие слова (не префикса!)
     *
     * WHY isEndOfWord check: "car" есть в trie с "card",
     * но "car" — слово только если помечено
     */
    fun search(word: String): Boolean {
        val node = findNode(word)
        return node != null && node.isEndOfWord
    }

    /**
     * Проверяет наличие любого слова с данным префиксом
     */
    fun startsWith(prefix: String): Boolean {
        return findNode(prefix) != null
    }

    /**
     * Вспомогательный метод: находит узел по строке
     * Возвращает null если путь не существует
     */
    private fun findNode(s: String): TrieNode? {
        var node = root

        for (char in s) {
            val index = char - 'a'
            node = node.children[index] ?: return null
        }

        return node
    }

    /**
     * Возвращает все слова с данным префиксом
     *
     * WHY DFS: обходим всё поддерево под prefix node
     */
    fun getAllWithPrefix(prefix: String): List<String> {
        val result = mutableListOf<String>()
        val startNode = findNode(prefix) ?: return result

        // DFS для сбора всех слов
        fun dfs(node: TrieNode, current: StringBuilder) {
            if (node.isEndOfWord) {
                result.add(current.toString())
            }

            for (i in 0 until 26) {
                val child = node.children[i]
                if (child != null) {
                    current.append('a' + i)
                    dfs(child, current)
                    current.deleteCharAt(current.lastIndex)  // Backtrack
                }
            }
        }

        dfs(startNode, StringBuilder(prefix))
        return result
    }
}
```

### Kotlin — HashMap-based Trie (универсальный алфавит)

```kotlin
/**
 * Trie с HashMap для детей — работает с любыми символами
 *
 * WHY HashMap: экономит память для разреженных узлов,
 * поддерживает Unicode, emoji, любые символы
 */
class FlexibleTrieNode {
    val children = mutableMapOf<Char, FlexibleTrieNode>()
    var isEndOfWord = false
}

class FlexibleTrie {
    private val root = FlexibleTrieNode()

    fun insert(word: String) {
        var node = root

        for (char in word) {
            // WHY getOrPut: создаёт узел если не существует
            node = node.children.getOrPut(char) { FlexibleTrieNode() }
        }

        node.isEndOfWord = true
    }

    fun search(word: String): Boolean {
        var node = root

        for (char in word) {
            node = node.children[char] ?: return false
        }

        return node.isEndOfWord
    }

    fun startsWith(prefix: String): Boolean {
        var node = root

        for (char in prefix) {
            node = node.children[char] ?: return false
        }

        return true
    }

    /**
     * Удаляет слово из Trie
     *
     * WHY рекурсия: нужно удалять узлы снизу вверх,
     * только если они не используются другими словами
     */
    fun delete(word: String): Boolean {
        fun deleteRecursive(node: FlexibleTrieNode, word: String, index: Int): Boolean {
            if (index == word.length) {
                if (!node.isEndOfWord) return false
                node.isEndOfWord = false
                return node.children.isEmpty()  // Можно удалить узел?
            }

            val char = word[index]
            val child = node.children[char] ?: return false

            val shouldDeleteChild = deleteRecursive(child, word, index + 1)

            if (shouldDeleteChild) {
                node.children.remove(char)
                return !node.isEndOfWord && node.children.isEmpty()
            }

            return false
        }

        return deleteRecursive(root, word, 0)
    }

    /**
     * Подсчёт слов с данным префиксом
     */
    fun countWithPrefix(prefix: String): Int {
        var node = root

        for (char in prefix) {
            node = node.children[char] ?: return 0
        }

        fun countWords(node: FlexibleTrieNode): Int {
            var count = if (node.isEndOfWord) 1 else 0
            for (child in node.children.values) {
                count += countWords(child)
            }
            return count
        }

        return countWords(node)
    }
}
```

### Java — Classic Implementation

```java
/**
 * Classic Trie implementation in Java
 */
class TrieNode {
    TrieNode[] children = new TrieNode[26];
    boolean isEndOfWord = false;
}

class Trie {
    private TrieNode root = new TrieNode();

    public void insert(String word) {
        TrieNode node = root;

        for (char c : word.toCharArray()) {
            int index = c - 'a';

            if (node.children[index] == null) {
                node.children[index] = new TrieNode();
            }
            node = node.children[index];
        }

        node.isEndOfWord = true;
    }

    public boolean search(String word) {
        TrieNode node = findNode(word);
        return node != null && node.isEndOfWord;
    }

    public boolean startsWith(String prefix) {
        return findNode(prefix) != null;
    }

    private TrieNode findNode(String s) {
        TrieNode node = root;

        for (char c : s.toCharArray()) {
            int index = c - 'a';
            if (node.children[index] == null) {
                return null;
            }
            node = node.children[index];
        }

        return node;
    }
}
```

### Python — Compact Implementation

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None

    def _find_node(self, s: str) -> TrieNode:
        node = self.root
        for char in s:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def get_all_with_prefix(self, prefix: str) -> list:
        """Return all words with given prefix."""
        result = []
        node = self._find_node(prefix)
        if node is None:
            return result

        def dfs(node, current):
            if node.is_end:
                result.append(current)
            for char, child in node.children.items():
                dfs(child, current + char)

        dfs(node, prefix)
        return result
```

---

## Паттерны решения задач

### Паттерн 1: Word Dictionary с Wildcard (LeetCode 211)

```kotlin
/**
 * Поиск слова с wildcards '.'
 * '.' соответствует любому символу
 *
 * Пример: ".at" находит "cat", "bat", "hat"
 */
class WordDictionary {
    class TrieNode {
        val children = arrayOfNulls<TrieNode>(26)
        var isWord = false
    }

    private val root = TrieNode()

    fun addWord(word: String) {
        var node = root
        for (c in word) {
            val i = c - 'a'
            if (node.children[i] == null) node.children[i] = TrieNode()
            node = node.children[i]!!
        }
        node.isWord = true
    }

    /**
     * WHY DFS: при '.' нужно проверить все 26 веток
     */
    fun search(word: String): Boolean {
        return dfs(word, 0, root)
    }

    private fun dfs(word: String, index: Int, node: TrieNode): Boolean {
        if (index == word.length) {
            return node.isWord
        }

        val c = word[index]

        if (c == '.') {
            // WHY try all: wildcard соответствует любому символу
            for (child in node.children) {
                if (child != null && dfs(word, index + 1, child)) {
                    return true
                }
            }
            return false
        } else {
            val child = node.children[c - 'a'] ?: return false
            return dfs(word, index + 1, child)
        }
    }
}
```

### Паттерн 2: Word Search II (LeetCode 212)

```kotlin
/**
 * Найти все слова из словаря на 2D доске
 *
 * WHY Trie + DFS:
 * - Trie позволяет проверить префикс за O(1)
 * - Раннее отсечение: если префикс не в Trie → прекращаем поиск
 */
fun findWords(board: Array<CharArray>, words: Array<String>): List<String> {
    // Строим Trie из словаря
    val root = buildTrie(words)
    val result = mutableSetOf<String>()
    val m = board.size
    val n = board[0].size

    fun dfs(i: Int, j: Int, node: TrieNode, path: StringBuilder) {
        if (i < 0 || i >= m || j < 0 || j >= n) return

        val char = board[i][j]
        if (char == '#') return  // Уже посещено

        val child = node.children[char - 'a'] ?: return  // Нет в Trie

        path.append(char)

        if (child.word != null) {
            result.add(child.word!!)
            // Обнуляем слово, чтобы не добавить его повторно!
            // Одно и то же слово можно найти несколькими путями на доске
            child.word = null
        }

        board[i][j] = '#'  // Mark visited

        // Explore 4 directions
        dfs(i + 1, j, child, path)
        dfs(i - 1, j, child, path)
        dfs(i, j + 1, child, path)
        dfs(i, j - 1, child, path)

        board[i][j] = char  // Backtrack
        path.deleteCharAt(path.lastIndex)
    }

    for (i in 0 until m) {
        for (j in 0 until n) {
            dfs(i, j, root, StringBuilder())
        }
    }

    return result.toList()
}

// Модифицированный TrieNode хранит слово целиком
class TrieNode {
    val children = arrayOfNulls<TrieNode>(26)
    var word: String? = null  // Храним слово вместо isEndOfWord
}
```

### Паттерн 3: Prefix и Suffix Search

```kotlin
/**
 * Поиск слов по префиксу И суффиксу одновременно
 *
 * Trick: храним комбинацию suffix#prefix
 * Для "apple": "#apple", "e#apple", "le#apple", "ple#apple", "pple#apple", "apple#apple"
 */
class WordFilter(words: Array<String>) {
    private val trie = Trie()

    init {
        for ((weight, word) in words.withIndex()) {
            // Генерируем все комбинации suffix#word
            for (i in 0..word.length) {
                val key = word.substring(i) + "#" + word
                trie.insert(key, weight)
            }
        }
    }

    fun f(prefix: String, suffix: String): Int {
        val key = "$suffix#$prefix"
        return trie.searchWithPrefix(key)  // Возвращает максимальный weight
    }
}
```

---

## Распространённые ошибки

### 1. Забыли isEndOfWord

```kotlin
// НЕПРАВИЛЬНО: search вернёт true для любого префикса
fun searchBroken(word: String): Boolean {
    var node = root
    for (c in word) {
        node = node.children[c - 'a'] ?: return false
    }
    return true  // BUG: возвращает true для "car" если есть только "card"
}

// ПРАВИЛЬНО: проверяем флаг конца слова
fun searchCorrect(word: String): Boolean {
    var node = root
    for (c in word) {
        node = node.children[c - 'a'] ?: return false
    }
    return node.isEndOfWord  // Только если это конец валидного слова
}
```

### 2. Неправильное удаление

```kotlin
// НЕПРАВИЛЬНО: удаляем узел, который используется другими словами
fun deleteBroken(word: String) {
    var node = root
    for (c in word) {
        node = node.children[c - 'a'] ?: return
    }
    // BUG: просто удаляем узел, ломая "card" при удалении "car"
}

// ПРАВИЛЬНО: только снимаем флаг, удаляем узлы каскадно если пустые
fun deleteCorrect(word: String) {
    fun helper(node: TrieNode, index: Int): Boolean {
        if (index == word.length) {
            if (!node.isEndOfWord) return false
            node.isEndOfWord = false
            return node.children.all { it == null }
        }
        val i = word[index] - 'a'
        val child = node.children[i] ?: return false
        if (helper(child, index + 1)) {
            node.children[i] = null
            return !node.isEndOfWord && node.children.all { it == null }
        }
        return false
    }
    helper(root, 0)
}
```

### 3. Case sensitivity

```kotlin
// НЕПРАВИЛЬНО: 'A' - 'a' = -32, выход за границы массива!
fun insertBroken(word: String) {
    var node = root
    for (c in word) {
        val index = c - 'a'  // BUG: 'A' даёт -32
        node = node.children[index]!!
    }
}

// ПРАВИЛЬНО: нормализуем к lowercase
fun insertCorrect(word: String) {
    var node = root
    for (c in word.lowercase()) {
        val index = c - 'a'
        // ...
    }
}

// ИЛИ: используем HashMap для любых символов
```

### 4. Пустая строка

```kotlin
// НЕПРАВИЛЬНО: не обрабатываем пустую строку
fun insert(word: String) {
    if (word.isEmpty()) return  // BUG: пустая строка может быть валидным словом
    // ...
}

// ПРАВИЛЬНО: пустая строка = помечаем root
fun insertCorrect(word: String) {
    var node = root
    for (c in word) {
        // ...
    }
    node.isEndOfWord = true  // Работает даже для пустой строки (node = root)
}
```

### 5. Memory leak при частичном удалении

```kotlin
// ПРОБЛЕМА: узлы накапливаются, хотя не используются
class BadTrie {
    fun delete(word: String) {
        val node = findNode(word) ?: return
        node.isEndOfWord = false  // Узел остаётся, занимает память
    }
}

// РЕШЕНИЕ: каскадное удаление неиспользуемых узлов (см. пример выше)
```

---

## Когда использовать?

### Trie vs Hash Table

```
                ВЫБОР СТРУКТУРЫ
                      │
       ┌──────────────┼──────────────┐
       │              │              │
  Нужен поиск     Только точное    Нужна
  по префиксу?    совпадение?      сортировка?
       │              │              │
       ▼              ▼              ▼
     TRIE         HASH TABLE       TRIE
  O(m) prefix     O(1) lookup     Natural order
```

### Когда использовать Trie

| Сценарий | Почему Trie |
|----------|-------------|
| Автодополнение | Быстрый поиск всех слов с префиксом |
| Spell checker | Проверка существования + предложения |
| IP routing | Longest prefix matching |
| Словарные игры | Проверка валидности + подсказки |
| Phone book | T9-style поиск контактов |

### Когда НЕ использовать Trie

| Сценарий | Лучшая альтернатива |
|----------|---------------------|
| Точное совпадение без prefix | HashSet — O(1) |
| Мало слов (< 100) | Простой список |
| Ограниченная память | HashSet (меньше overhead) |
| Частые обновления | HashSet (проще) |

---

## Практика

### Концептуальные вопросы

1. **Q:** Почему Trie хранит символы на рёбрах, а не в узлах?

   **A:** Концептуально символы хранятся на рёбрах (переходах). Узел представляет состояние после прочтения префикса. Технически мы храним детей в массиве/map, где индекс/ключ — это символ. Сам узел хранит только isEndOfWord.

2. **Q:** Как Trie экономит память при общих префиксах?

   **A:** Слова "cat", "car", "card" делят путь c→a. Вместо хранения 3+3+4=10 символов, храним 4 узла (root, c, a, t/r/d). Чем больше общих префиксов, тем больше экономия.

3. **Q:** Почему search и startsWith имеют одинаковую сложность O(m)?

   **A:** Оба метода проходят путь длины m. Единственная разница — search дополнительно проверяет isEndOfWord, что O(1).

4. **Q:** Когда Array[26] лучше HashMap?

   **A:** Когда алфавит фиксирован и небольшой (a-z). Array даёт O(1) доступ без hash overhead. HashMap лучше для Unicode, разреженных узлов, или когда большинство букв не используются.

5. **Q:** Как реализовать поиск с опечатками (fuzzy search)?

   **A:** BFS/DFS с "бюджетом" на ошибки. На каждом шаге можем: 1) сопоставить символ (бесплатно), 2) заменить (−1 бюджет), 3) вставить (−1), 4) удалить (−1). Когда бюджет = 0, только точное совпадение.

### LeetCode задачи

#### Core (обязательно)

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 208 | [Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/) | Базовая реализация |
| 211 | [Design Add and Search Words](https://leetcode.com/problems/design-add-and-search-words-data-structure/) | Wildcard '.' |
| 212 | [Word Search II](https://leetcode.com/problems/word-search-ii/) | Trie + DFS на board |

#### Medium

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 139 | [Word Break](https://leetcode.com/problems/word-break/) | DP + Trie для словаря |
| 648 | [Replace Words](https://leetcode.com/problems/replace-words/) | Найти кратчайший префикс |
| 677 | [Map Sum Pairs](https://leetcode.com/problems/map-sum-pairs/) | Trie с суммой значений |
| 720 | [Longest Word in Dictionary](https://leetcode.com/problems/longest-word-in-dictionary/) | Слово строится посимвольно |
| 1268 | [Search Suggestions System](https://leetcode.com/problems/search-suggestions-system/) | Autocomplete top 3 |

#### Hard

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 472 | [Concatenated Words](https://leetcode.com/problems/concatenated-words/) | Trie + DP |
| 336 | [Palindrome Pairs](https://leetcode.com/problems/palindrome-pairs/) | Trie с reverse |
| 745 | [Prefix and Suffix Search](https://leetcode.com/problems/prefix-and-suffix-search/) | suffix#prefix trick |

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Trie всегда экономит память по сравнению с HashSet" | **Нет!** Trie часто потребляет БОЛЬШЕ памяти. Каждый узел хранит 26 указателей (200+ байт на 64-bit), тогда как строка — 1 байт на символ. HashSet выигрывает для небольших словарей или слов без общих префиксов. |
| "Trie — всегда лучший выбор для строк" | **Зависит от задачи.** Для точного поиска HashSet даёт O(1), Trie — O(m). Trie выигрывает только когда нужен prefix search или autocomplete. |
| "Поиск в Trie всегда O(1)" | **Нет, O(m)** где m — длина строки. Это независимо от количества слов n, но зависит от длины искомой строки. Для очень длинных слов это может быть медленнее HashSet. |
| "Trie не имеет коллизий, значит быстрее Hash Table" | **Частично верно.** Нет hash-коллизий, но cache locality хуже — узлы разбросаны по памяти. Hash table с хорошей hash-функцией может быть быстрее из-за cache-friendliness. |
| "Array[26] всегда лучше HashMap для детей" | **Нет.** Array[26] тратит память на пустые слоты. Если большинство узлов имеют 1-3 детей, HashMap экономнее. Array[26] оправдан только для плотных Trie. |
| "Radix Tree (Compressed Trie) всегда лучше обычного Trie" | **Trade-off.** Radix Tree экономит память, но усложняет реализацию и может замедлить операции из-за работы со строками вместо символов. |
| "Trie подходит для любого алфавита" | **С оговорками.** Для Unicode (65K+ символов) Array-based Trie невозможен. Нужен HashMap, но это увеличивает overhead и снижает производительность. |
| "Название 'Trie' произносится как 'tree'" | **Нет!** Произносится "трай" (от re**trie**val). Это отличает Trie от Tree в устной речи. Некоторые говорят "три", но "трай" — оригинальное произношение автора. |

---

## CS-фундамент

| CS-концепция | Применение в Trie |
|--------------|-------------------|
| **Tree Data Structure** | Trie — это n-арное дерево, где каждый узел может иметь до |Σ| детей (размер алфавита). Корень = пустая строка, каждое ребро = символ, путь от корня = префикс. |
| **Prefix Sharing (Structural Sharing)** | Ключевая оптимизация Trie: слова "cat", "car", "card" делят узлы c→a. Это форма структурного разделения данных, используемая в persistent data structures (Clojure, Scala). |
| **Space-Time Tradeoff** | Array[26] vs HashMap: массив даёт O(1) доступ, но тратит память на пустые слоты. HashMap экономит память, но добавляет overhead на хеширование. Выбор зависит от плотности данных. |
| **Branching Factor** | Trie имеет branching factor = |Σ| (размер алфавита). Для a-z это 26. Высокий branching factor = широкое, но неглубокое дерево. Глубина = длина самого длинного слова. |
| **DFS/BFS Traversal** | Сбор всех слов с префиксом = DFS от узла префикса. DFS даёт слова в лексикографическом порядке (если дети обходятся по алфавиту). BFS даёт слова по длине. |
| **Amortized Analysis** | Вставка n слов суммарной длины L занимает O(L) времени. Хотя каждая вставка O(m), общее время пропорционально общей длине всех слов, что эффективно для batch операций. |
| **Finite Automaton** | Trie — это детерминированный конечный автомат (DFA) для распознавания множества строк. Каждый узел = состояние, isEndOfWord = accepting state. Это связь со [[string-algorithms]] и regex. |

---

## Связанные темы

### Prerequisites

- [[trees-binary]] — Trie — это дерево
- [[hash-tables]] — HashMap для детей
- [[strings]] — работа со строками
- [[recursion]] — DFS обход

### Что изучать после Trie

- [[dfs-bfs-patterns]] — обход Trie
- [[backtracking]] — Word Search II
- [[dynamic-programming]] — Word Break
- [[string-algorithms]] — KMP, Rabin-Karp

### Продвинутые варианты

- **Radix Tree (Compressed Trie)** — сжатие цепочек
- **Suffix Tree** — все суффиксы строки
- **Ternary Search Tree** — BST символов
- **PATRICIA Trie** — побитовое представление

---

## Источники

1. [LeetCode 208 — Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/)
2. [Tech Interview Handbook — Trie](https://www.techinterviewhandbook.org/algorithms/trie/)
3. [GeeksforGeeks — Trie](https://www.geeksforgeeks.org/dsa/trie-insert-and-search/)
4. [Baeldung — Hash Table vs Trie](https://www.baeldung.com/cs/hash-table-vs-trie-prefix-tree)
5. [Kodeco — Tries in Kotlin](https://www.kodeco.com/books/data-structures-algorithms-in-kotlin/v1.0/chapters/10-tries)
6. [Medium — Trie Kotlin](https://1gravityllc.medium.com/trie-kotlin-50d8ae041202)
7. Research: [2025-12-29-trie-prefix-tree.md](../../docs/research/2025-12-29-trie-prefix-tree.md)
8. [Codecademy — Complete Guide to Prefix Trees](https://www.codecademy.com/article/trie-data-structure-complete-guide-to-prefix-trees)
9. [Medium/basecs — "Trying to Understand Tries"](https://medium.com/basecs/trying-to-understand-tries-3ec6bede0014)
10. [Baeldung — Hash Table vs Trie](https://www.baeldung.com/cs/hash-table-vs-trie-prefix-tree)
11. [DEV.to — Comprehensive List of Trie Questions](https://dev.to/nozibul_islam_113b1d5334f/comprehensive-list-of-trie-based-questions-d70)
12. [AlgoCademy — Trie in Coding Interviews](https://algocademy.com/blog/how-often-does-the-trie-data-structure-appear-in-coding-interviews/)

---

## Навигация

← Предыдущая: [[heaps-priority-queues|Heaps & Priority Queues]]
→ Следующая: [[sorting-algorithms|Sorting Algorithms]]
↑ Вверх: [[_moc-data-structures|Data Structures MOC]]

*Обновлено: 2026-01-06 — добавлены педагогические секции (интуиция Trie, типичные ошибки, 4 ментальные модели)*

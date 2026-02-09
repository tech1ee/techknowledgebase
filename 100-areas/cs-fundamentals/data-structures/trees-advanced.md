# Advanced Trees: AVL & Red-Black Trees

## TL;DR

Self-balancing BST гарантируют O(log n) для всех операций. **AVL**: строже сбалансирован (высота ≤ 1.44 log n), лучше для read-heavy. **Red-Black**: меньше ротаций при insert/delete, лучше для write-heavy. Red-Black используется в std::map (C++), TreeMap (Java), Linux kernel.

---

## Интуиция

### Аналогия 1: AVL как педантичный библиотекарь

```
AVL TREE = ПЕДАНТИЧНЫЙ БИБЛИОТЕКАРЬ:

"Полки должны быть ИДЕАЛЬНО сбалансированы!"
Разница высоты ≤ 1 для КАЖДОГО узла.

Добавляем книгу → полка перекосилась?
→ НЕМЕДЛЕННО перестроить! (ротация)
→ Возможно несколько ротаций

Результат: Идеальный поиск, но много перестановок.
Хорошо для: библиотеки с частым поиском, редким добавлением.
```

### Аналогия 2: Red-Black как расслабленный менеджер

```
RED-BLACK = МЕНЕДЖЕР С ГИБКИМИ ПРАВИЛАМИ:

"Пока дерево примерно сбалансировано — ОК!"
Правила через цвета: красный родитель → чёрные дети.

Добавляем сотрудника → небольшой дисбаланс?
→ Может, просто перекрасим? (дёшево)
→ Ротация только если совсем плохо

Результат: Меньше перестановок, чуть хуже поиск.
Хорошо для: часто меняющейся команды.
```

---

## Частые ошибки

### Ошибка 1: Забыть обновить высоту после ротации

**СИМПТОМ:** Неправильный balance factor, лишние ротации

```kotlin
// НЕПРАВИЛЬНО:
fun rotateRight(y: Node): Node {
    val x = y.left!!
    y.left = x.right
    x.right = y
    return x  // высоты не обновлены!
}

// ПРАВИЛЬНО:
fun rotateRight(y: Node): Node {
    val x = y.left!!
    y.left = x.right
    x.right = y
    y.updateHeight()  // сначала нижний узел
    x.updateHeight()  // потом верхний
    return x
}
```

### Ошибка 2: Путать LL/LR/RL/RR ротации

**СИМПТОМ:** Дерево не балансируется

```
ВЫБОР РОТАЦИИ по Balance Factor:

BF > 1 (левый перевес):
  BF(left) >= 0 → LL → rotateRight(node)
  BF(left) < 0  → LR → rotateLeft(left), rotateRight(node)

BF < -1 (правый перевес):
  BF(right) <= 0 → RR → rotateLeft(node)
  BF(right) > 0  → RL → rotateRight(right), rotateLeft(node)
```

### Ошибка 3: Не сохранять родителя в Red-Black

**СИМПТОМ:** Fixup не может подняться к корню

```kotlin
// НЕПРАВИЛЬНО: узел без ссылки на родителя
class Node(val key: Int, var color: Color, var left: Node?, var right: Node?)

// ПРАВИЛЬНО: нужен parent для fixup
class Node(val key: Int, var color: Color,
           var left: Node?, var right: Node?, var parent: Node?)
```

---

## Ментальные модели

### Модель 1: "AVL строже, Red-Black гибче"

```
СРАВНЕНИЕ ВЫСОТЫ:

AVL:       h ≤ 1.44 * log₂(n)   ← строгий баланс
Red-Black: h ≤ 2 * log₂(n)      ← допускает перекос

ПОСЛЕДСТВИЯ:

            AVL             Red-Black
Search      Быстрее         Чуть медленнее
Insert      1-2 ротации     ≤2 ротации
Delete      O(log n) рот.   ≤3 ротации
Use case    Read-heavy      Write-heavy
```

### Модель 2: "Red-Black = 2-3-4 дерево в маскировке"

```
Red-Black эквивалентен 2-3-4 дереву:

Чёрный узел с красными детьми = 3-node или 4-node

     B           [R-B-R]
    / \    =     2-3-4
   R   R          node

Правила Red-Black — это правила 2-3-4, переформулированные для бинарного дерева.
```

---

## Зачем это нужно?

**Проблема обычного BST:**

```
Вставляем: 1, 2, 3, 4, 5

BST становится linked list:
    1
     \
      2
       \
        3
         \
          4
           \
            5

Search: O(n) вместо O(log n)!
```

**Self-balancing BST решают:**
- Гарантированный O(log n) для всех операций
- Высота ограничена O(log n)
- Автоматическое восстановление баланса

---

## AVL Tree

### Определение

**AVL Tree** — BST, где для каждого узла разница высот левого и правого поддерева ≤ 1.

```
Balance Factor = height(left) - height(right)
Valid: -1, 0, +1
```

### Визуализация

```
Сбалансированное AVL:        Несбалансированное (BF = 2):
       10 (BF=0)                    10 (BF=2)
      /  \                         /
     5    15 (BF=0)               5 (BF=1)
    / \   / \                    /
   3   7 12  20                 3 (BF=0)
                               /
                              1  ← нарушает баланс
```

### Четыре типа ротаций

#### 1. Left-Left (LL) — Single Right Rotation

```
Проблема:             Решение (Right Rotate):
    30 (BF=2)              20
   /                      /  \
  20 (BF=1)              10   30
 /
10

Code:
fun rightRotate(y: Node): Node {
    val x = y.left
    val T2 = x.right

    x.right = y
    y.left = T2

    updateHeight(y)
    updateHeight(x)
    return x
}
```

#### 2. Right-Right (RR) — Single Left Rotation

```
Проблема:             Решение (Left Rotate):
10 (BF=-2)                 20
  \                       /  \
   20 (BF=-1)            10   30
     \
      30
```

#### 3. Left-Right (LR) — Double Rotation

```
Проблема:             Шаг 1 (Left Rotate 10):    Шаг 2 (Right Rotate 30):
    30 (BF=2)              30                          20
   /                      /                           /  \
  10 (BF=-1)             20                          10   30
    \                   /
     20                10
```

#### 4. Right-Left (RL) — Double Rotation

```
Проблема:             Шаг 1 (Right Rotate 30):   Шаг 2 (Left Rotate 10):
10 (BF=-2)                 10                          20
  \                          \                        /  \
   30 (BF=1)                  20                     10   30
  /                             \
 20                              30
```

### Реализация AVL (Kotlin)

```kotlin
class AVLTree {
    data class Node(
        var key: Int,
        var left: Node? = null,
        var right: Node? = null,
        var height: Int = 1
    )

    private var root: Node? = null

    private fun height(node: Node?): Int = node?.height ?: 0

    private fun balanceFactor(node: Node?): Int =
        height(node?.left) - height(node?.right)

    private fun updateHeight(node: Node) {
        node.height = 1 + maxOf(height(node.left), height(node.right))
    }

    /**
     * ПРАВЫЙ ПОВОРОТ — используется при LL дисбалансе
     *
     *       y                x
     *      / \              / \
     *     x   T3    →     T1   y
     *    / \                  / \
     *   T1  T2              T2  T3
     *
     * Результат: x становится новым корнем, y уходит вправо
     */
    private fun rightRotate(y: Node): Node {
        val x = y.left!!
        val T2 = x.right

        x.right = y
        y.left = T2

        updateHeight(y)
        updateHeight(x)
        return x
    }

    /**
     * ЛЕВЫЙ ПОВОРОТ — используется при RR дисбалансе
     *
     *     x                  y
     *    / \                / \
     *   T1  y      →       x  T3
     *      / \            / \
     *     T2  T3        T1  T2
     *
     * Результат: y становится новым корнем, x уходит влево
     */
    private fun leftRotate(x: Node): Node {
        val y = x.right!!
        val T2 = y.left

        y.left = x
        x.right = T2

        updateHeight(x)
        updateHeight(y)
        return y
    }

    /**
     * БАЛАНСИРОВКА — вызывается после каждой вставки/удаления
     *
     * Проверяем 4 случая дисбаланса:
     * - LL: левый-левый → один правый поворот
     * - LR: левый-правый → левый + правый повороты
     * - RR: правый-правый → один левый поворот
     * - RL: правый-левый → правый + левый повороты
     */
    private fun balance(node: Node): Node {
        updateHeight(node)
        val bf = balanceFactor(node)

        // LL Case
        if (bf > 1 && balanceFactor(node.left) >= 0) {
            return rightRotate(node)
        }

        // LR Case
        if (bf > 1 && balanceFactor(node.left) < 0) {
            node.left = leftRotate(node.left!!)
            return rightRotate(node)
        }

        // RR Case
        if (bf < -1 && balanceFactor(node.right) <= 0) {
            return leftRotate(node)
        }

        // RL Case
        if (bf < -1 && balanceFactor(node.right) > 0) {
            node.right = rightRotate(node.right!!)
            return leftRotate(node)
        }

        return node
    }

    fun insert(key: Int) {
        root = insertRec(root, key)
    }

    private fun insertRec(node: Node?, key: Int): Node {
        if (node == null) return Node(key)

        when {
            key < node.key -> node.left = insertRec(node.left, key)
            key > node.key -> node.right = insertRec(node.right, key)
            else -> return node  // Дубликаты игнорируем
        }

        // ВАЖНО: балансировка происходит на ОБРАТНОМ пути рекурсии!
        // Сначала вставляем элемент вглубь, потом при "всплытии"
        // проверяем и исправляем баланс каждого предка
        return balance(node)
    }
}
```

---

## Red-Black Tree

### Определение

**Red-Black Tree** — BST с раскраской узлов, гарантирующей высоту ≤ 2 log n.

### Пять свойств

```
1. Каждый узел красный или чёрный
2. Корень всегда чёрный
3. Каждый лист (NIL) чёрный
4. Красный узел имеет только чёрных детей
5. Все пути от узла до листьев имеют одинаковое число чёрных узлов
```

### Визуализация

```
        8(B)
       /    \
     4(R)    12(R)
    /  \     /   \
  2(B) 6(B) 10(B) 14(B)
```

### Операции вставки

```
Новый узел всегда КРАСНЫЙ (кроме корня)

Case 1: Дядя красный → Перекрасить
        G(B)             G(R)
       /   \            /   \
      P(R)  U(R)  →   P(B)  U(B)
     /                /
    N(R)             N(R)

Case 2: Дядя чёрный, узел внутри → Ротация к Case 3
        G(B)             G(B)
       /   \            /   \
      P(R)  U(B)  →   N(R)  U(B)
        \             /
        N(R)        P(R)

Case 3: Дядя чёрный, узел снаружи → Ротация + перекраска
        G(B)             P(B)
       /   \            /   \
      P(R)  U(B)  →   N(R)  G(R)
     /                        \
    N(R)                      U(B)
```

### Реализация Red-Black (Kotlin)

```kotlin
class RedBlackTree {
    enum class Color { RED, BLACK }

    data class Node(
        var key: Int,
        var color: Color = Color.RED,
        var left: Node? = null,
        var right: Node? = null,
        var parent: Node? = null
    )

    private var root: Node? = null
    // NIL — это "страж" (sentinel), общий для всех листьев
    // Вместо null используем специальный ЧЁРНЫЙ узел
    // Это упрощает код: не нужно проверять на null везде
    private val NIL = Node(0, Color.BLACK)

    private fun leftRotate(x: Node) {
        val y = x.right ?: return
        x.right = y.left

        y.left?.parent = x
        y.parent = x.parent

        when {
            x.parent == null -> root = y
            x == x.parent?.left -> x.parent?.left = y
            else -> x.parent?.right = y
        }

        y.left = x
        x.parent = y
    }

    private fun rightRotate(y: Node) {
        val x = y.left ?: return
        y.left = x.right

        x.right?.parent = y
        x.parent = y.parent

        when {
            y.parent == null -> root = x
            y == y.parent?.right -> y.parent?.right = x
            else -> y.parent?.left = x
        }

        x.right = y
        y.parent = x
    }

    fun insert(key: Int) {
        val newNode = Node(key)

        // ШАГ 1: Стандартная BST вставка
        // Находим место для нового узла и вставляем
        var y: Node? = null
        var x = root

        while (x != null) {
            y = x
            x = if (key < x.key) x.left else x.right
        }

        newNode.parent = y
        when {
            y == null -> root = newNode
            key < y.key -> y.left = newNode
            else -> y.right = newNode
        }

        // ШАГ 2: Восстанавливаем свойства RB-дерева
        // Новый узел КРАСНЫЙ, это может нарушить свойство 4
        // (два красных узла подряд запрещены)
        fixInsert(newNode)
    }

    private fun fixInsert(node: Node) {
        var z = node

        // Пока родитель КРАСНЫЙ — есть нарушение свойства 4:
        // "Оба ребёнка красного узла должны быть чёрными"
        // Мы только что вставили красный узел под красным родителем!
        while (z.parent?.color == Color.RED) {
            if (z.parent == z.parent?.parent?.left) {
                val uncle = z.parent?.parent?.right

                if (uncle?.color == Color.RED) {
                    // Case 1: Дядя красный
                    z.parent?.color = Color.BLACK
                    uncle.color = Color.BLACK
                    z.parent?.parent?.color = Color.RED
                    z = z.parent?.parent ?: break
                } else {
                    if (z == z.parent?.right) {
                        // Case 2: Узел внутри
                        z = z.parent ?: break
                        leftRotate(z)
                    }
                    // Case 3: Узел снаружи
                    z.parent?.color = Color.BLACK
                    z.parent?.parent?.color = Color.RED
                    z.parent?.parent?.let { rightRotate(it) }
                }
            } else {
                // Симметричный случай (parent — правый ребёнок)
                val uncle = z.parent?.parent?.left

                if (uncle?.color == Color.RED) {
                    z.parent?.color = Color.BLACK
                    uncle.color = Color.BLACK
                    z.parent?.parent?.color = Color.RED
                    z = z.parent?.parent ?: break
                } else {
                    if (z == z.parent?.left) {
                        z = z.parent ?: break
                        rightRotate(z)
                    }
                    z.parent?.color = Color.BLACK
                    z.parent?.parent?.color = Color.RED
                    z.parent?.parent?.let { leftRotate(it) }
                }
            }
        }

        // ВАЖНО: корень всегда ЧЁРНЫЙ!
        // Это свойство 2 RB-дерева.
        // После всех манипуляций корень мог стать красным — исправляем
        root?.color = Color.BLACK
    }
}
```

---

## Сравнение AVL vs Red-Black

| Критерий | AVL | Red-Black |
|----------|-----|-----------|
| Баланс | Строгий (|BF| ≤ 1) | Relaxed (черная высота) |
| Высота | ≤ 1.44 log n | ≤ 2 log n |
| Поиск | Немного быстрее | Немного медленнее |
| Вставка | До 2 ротаций + перебалансировка | До 2 ротаций |
| Удаление | До O(log n) ротаций | До 3 ротаций |
| Память | Меньше (только height) | Больше (color + parent) |
| Использование | Databases, lookup-heavy | std::map, TreeMap, kernels |

### Когда что использовать

```
AVL Tree:
✓ Много поисков, мало изменений
✓ Критична минимальная высота
✓ Примеры: индексы в базах данных, словари

Red-Black Tree:
✓ Частые вставки/удаления
✓ Нужен баланс между всеми операциями
✓ Примеры: std::map, TreeMap, scheduler в Linux
```

---

## Сложность операций

| Операция | AVL | Red-Black | Обычный BST |
|----------|-----|-----------|-------------|
| Search | O(log n) | O(log n) | O(n) worst |
| Insert | O(log n) | O(log n) | O(n) worst |
| Delete | O(log n) | O(log n) | O(n) worst |
| Min/Max | O(log n) | O(log n) | O(n) worst |
| Space | O(n) | O(n) | O(n) |

---

## Практика

### Концептуальные вопросы

1. **Почему новый узел в RB-дереве красный?**
   - Чёрный нарушил бы свойство 5 (разное число чёрных на путях)
   - Красный может нарушить только свойство 4 (красный родитель)
   - Свойство 4 легче исправить

2. **Почему AVL лучше для поиска?**
   - Меньшая высота = меньше сравнений
   - 1.44 log n vs 2 log n

3. **Почему RB используется в стандартных библиотеках?**
   - Меньше ротаций при модификациях
   - Более предсказуемое поведение
   - Проще реализация удаления

### Связанные задачи

- Реализация самобалансирующегося дерева
- Validate BST with balance check
- Найти k-й элемент в BST
- Merge two BSTs

---

## Связанные темы

### Prerequisites
- Binary Search Tree basics
- Tree rotations
- Recursion

### Unlocks
- B-Trees (для дисковых структур)
- Segment Trees
- Interval Trees
- Treaps (randomized BST)

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [GeeksforGeeks AVL](https://www.geeksforgeeks.org/dsa/introduction-to-avl-tree/) | Tutorial | AVL impl |
| 2 | [AlgoCademy](https://algocademy.com/blog/balancing-trees-avl-vs-red-black-trees/) | Blog | Comparison |
| 3 | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) | Book | Formal proofs |
| 4 | [Visualgo](https://visualgo.net/en/bst) | Tool | Visualization |

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции: 2 аналогии (AVL как педантичный библиотекарь, Red-Black как расслабленный менеджер), 3 типичные ошибки (обновление высоты, LL/LR/RL/RR ротации, parent в Red-Black), 2 ментальные модели (AVL строже/Red-Black гибче, Red-Black = 2-3-4 дерево)*

---
title: "Персистентные структуры данных"
created: 2026-02-09
modified: 2026-02-10
type: deep-dive
status: published
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/expert
related:
  - "[[segment-tree]]"
  - "[[trees-binary]]"
prerequisites:
  - "[[trees-binary]]"
  - "[[segment-tree]]"
  - "[[recursion-fundamentals]]"
  - "[[big-o-complexity]]"
---

# Persistent Data Structures

## TL;DR

Persistent Data Structures — структуры, сохраняющие **все предыдущие версии** после модификаций. Основная техника — **Path Copying** (копируем только путь от корня до изменённого узла). Память O(log n) на update через **structural sharing**. Используются в Git, Redux, Clojure, и для offline queries в competitive programming.

---

## Интуиция

### Аналогия 1: Git как persistent структура

```
GIT COMMITS = PERSISTENT ДЕРЕВО:

v1: A → B → C              (первоначальная история)

Изменяем файл в C:
v2: A → B → C'             (новая ветка)
         ↗
v1: A → B → C              (старая история сохранена!)

A и B НЕ копируются — они РАЗДЕЛЯЮТСЯ между версиями.
Копируется только путь от корня до изменённого узла.
```

### Аналогия 2: Path Copying как минимальный ремонт

```
РЕМОНТ ДОМА = PATH COPYING:

Нужно заменить лампочку в комнате 3:

НАИВНО: Построить новый дом, скопировав всё
        → O(n) стоимость

PATH COPYING:
- Новая лампочка в комнате 3 (изменение)
- Новая дверь в комнату 3 (путь)
- Новый коридор к двери (путь)
- Новый вход в дом (корень)
- Остальные комнаты → показываем на СТАРЫЕ
        → O(log n) стоимость
```

---

## Частые ошибки

### Ошибка 1: Модифицировать узел вместо создания нового

**СИМПТОМ:** Старые версии "повреждены"

```kotlin
// НЕПРАВИЛЬНО: мутируем существующий узел
fun update(node: Node, key: Int, value: Int): Node {
    if (node.key == key) {
        node.value = value  // портит старую версию!
        return node
    }
    // ...
}

// ПРАВИЛЬНО: создаём новый узел
fun update(node: Node?, key: Int, value: Int): Node {
    if (node == null) return Node(key, value)
    return when {
        key < node.key -> Node(node.key, node.value,
                               update(node.left, key, value), node.right)
        key > node.key -> Node(node.key, node.value,
                               node.left, update(node.right, key, value))
        else -> Node(key, value, node.left, node.right)
    }
}
```

### Ошибка 2: Хранить все корни вместо массива версий

**СИМПТОМ:** Потерянные версии, MLE

```kotlin
// НЕПРАВИЛЬНО: теряем доступ к старым версиям
var root = build(arr)
root = update(root, 5, 100)  // v1 потеряна!

// ПРАВИЛЬНО: массив корней версий
val roots = mutableListOf<Node>()
roots.add(build(arr))                    // v0
roots.add(update(roots[0], 5, 100))      // v1
roots.add(update(roots[1], 3, 200))      // v2
// query(roots[0], ...) — запрос к v0
```

### Ошибка 3: Path copying для всех узлов

**СИМПТОМ:** O(n) память вместо O(log n)

```kotlin
// НЕПРАВИЛЬНО: копируем поддерево целиком
fun copyTree(node: Node?): Node? {
    if (node == null) return null
    return Node(node.key, node.value,
                copyTree(node.left), copyTree(node.right))  // O(n)!
}

// ПРАВИЛЬНО: копируем ТОЛЬКО путь до изменения
// Неизменённые поддеревья переиспользуются
```

---

## Ментальные модели

### Модель 1: "Structural Sharing экономит память"

```
ВЕРСИОНИРОВАНИЕ ДЕРЕВА:

         v0              v1 (update leaf 7)
         [A]             [A']
        /   \           /    \
      [B]   [C]       [B]    [C']    ← B переиспользован
      / \   / \       / \    /  \
     1  2  3  [D]    1  2   3   [D']
              / \              /   \
             6   7            6    7'  ← только путь A-C-D скопирован

Память на update: O(высота) = O(log n)
```

### Модель 2: "Версия = корень"

```
ДОСТУП К ВЕРСИЯМ:

roots[0] → дерево на момент t=0
roots[1] → дерево на момент t=1
roots[k] → дерево на момент t=k

ЗАПРОС: query(roots[version], l, r)
UPDATE: roots[t+1] = update(roots[t], idx, val)

Каждый корень — "точка входа" в свою версию.
Узлы могут быть общими между версиями.
```

---

## Зачем это нужно?

### Проблема: как запомнить прошлое

Представьте текстовый редактор. Пользователь набирает текст, удаляет абзацы, вставляет слова. Через 50 правок он нажимает Ctrl+Z двадцать раз, возвращается к версии "30 правок назад", и продолжает работу оттуда. Как это реализовать?

Наивный подход: после каждой правки сохранять ПОЛНУЮ копию документа. Документ на 10 000 символов, 1 000 правок -- 10 миллионов символов в памяти. Для текстового редактора это терпимо, но для дерева из миллиона узлов -- катастрофа.

Более умный подход: при каждой правке сохранять ТОЛЬКО то, что изменилось. Если пользователь исправил одно слово, зачем копировать весь документ? Достаточно создать "патч" -- запись об изменении, ссылающуюся на предыдущую версию для всего остального. Именно эту идею реализуют персистентные структуры данных.

Аналогия: Git хранит историю проекта не как серию полных копий, а как серию "снимков" (snapshots), где неизменённые файлы РАЗДЕЛЯЮТСЯ между коммитами. Коммит -- это "версия" проекта. Path copying в персистентных деревьях работает по тому же принципу: неизменённые поддеревья разделяются между версиями, копируется только путь от корня до изменённого листа.

**Проблема в формальных терминах:**

```
Задача: "Дерево отрезков. После каждого update нужно
         отвечать на запросы к ЛЮБОЙ версии дерева."

Наивно: Копировать всё дерево после каждого update
        → O(n) памяти на update
        → 10^5 updates × 10^5 узлов = 10^10 памяти = MLE

Path Copying: Копировать только путь (O(log n) узлов)
        → O(log n) памяти на update
        → 10^5 updates × 17 узлов = 1.7 × 10^6 = OK
```

### Trade-off: время vs память

Персистентность -- это не бесплатный обед. Вот что мы платим и что получаем:

| Аспект | Ephemeral (обычная) | Persistent |
|--------|---------------------|------------|
| Память на update | O(1) (изменяем in-place) | O(log n) (path copying) |
| Доступ к прошлым версиям | Невозможен | O(1) -- просто обращаемся к корню |
| Thread-safety | Требует синхронизации | Immutable = безопасно для чтения |
| Garbage collection | Просто | Сложно (shared nodes между версиями) |
| Cache performance | Хорошая (данные рядом) | Хуже (новые узлы разбросаны в памяти) |

Последний пункт неочевиден, но важен на практике: при path copying новые узлы аллоцируются в разных местах памяти, что ухудшает cache locality. На современных процессорах cache miss стоит в 10-100 раз дороже, чем обращение к L1 кэшу.

**Реальные применения:**

| Область | Использование |
|---------|---------------|
| Git | Immutable objects (blobs, trees, commits) |
| Redux/React | State management с time-travel |
| Clojure | Все структуры данных persistent по умолчанию |
| Databases | MVCC (Multi-Version Concurrency Control) |
| Undo/Redo | История изменений документа |
| CP | Offline queries, версионные структуры |

---

## Что это такое?

### Для 5-летнего

```
Представь альбом с фотографиями.

Обычный альбом: если хочешь изменить фото —
выкидываешь старое, вставляешь новое.
Старое фото потеряно навсегда!

Persistent альбом: когда меняешь фото,
старая страница остаётся, создаётся НОВАЯ страница
с изменением. Можешь посмотреть ЛЮБУЮ старую версию!

Хитрость: если фото не изменилось,
не копируем его — просто показываем на старое место.
Экономим бумагу!
```

### Формально

**Persistent Data Structure** — структура данных, которая при модификации создаёт новую версию, сохраняя все предыдущие версии доступными.

```
Ephemeral (обычная):
  v0 → update(x) → v0 изменён, старая версия потеряна

Persistent:
  v0 → update(x) → v1 (новая версия)
                   v0 всё ещё доступна!
```

### Уровни персистентности

| Уровень | Описание | Пример |
|---------|----------|--------|
| **Partially Persistent** | Читать любую версию, писать только в последнюю | Fat Node |
| **Fully Persistent** | Читать/писать любую версию | Path Copying |
| **Confluently Persistent** | Можно merge две версии | Advanced |

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **Version** | Состояние структуры после серии операций |
| **Path Copying** | Копируем только узлы на пути к изменению |
| **Structural Sharing** | Неизменённые части разделяются между версиями |
| **Fat Node** | Узел хранит все свои значения с timestamps |
| **Immutable** | Объект нельзя изменить после создания |
| **Copy-on-Write (COW)** | Копируем только при модификации |

---

## Как это работает?

### Техника: Path Copying

```
BST Insert: добавляем 25

Версия 0:                      Версия 1:
       20                            20'  ← новый узел
      /  \                          /  \
    10    30                      10    30' ← новый узел
         /  \                          /  \
       25    40                      25    40
                                     ↑
                                  новый узел

Только 3 узла скопированы (путь от корня до 25)
Узлы 10, 25, 40 — shared между версиями!

Память на update: O(высота) = O(log n) для balanced tree
```

### Визуализация Structural Sharing

```
Исходный массив версии 0:
[1, 2, 3, 4, 5, 6, 7, 8]

Представляем как дерево (Persistent Array):

           v0:root
          /        \
      [1,2,3,4]   [5,6,7,8]
       /    \       /    \
    [1,2]  [3,4]  [5,6]  [7,8]

Update: arr[2] = 99 (индекс 2, значение было 3)

Версия 1:
           v1:root'  ← новый
          /        \
      [1,2,99,4]'   [5,6,7,8]  ← shared!
       /    \         ↗    ↖
    [1,2]  [99,4]'  shared  shared
     ↗
  shared   новый

Скопировано: 3 узла (путь к изменённому листу)
Shared: 5 узлов

Память: O(log n) вместо O(n)
```

### Fat Node vs Path Copying

```
FAT NODE (Partially Persistent):

Узел хранит историю значений:
┌────────────────────────────┐
│ value: [(v0, 10), (v3, 15)]│  ← значение 10 в v0, 15 в v3
│ left:  [(v0, ptr1)]        │
│ right: [(v0, ptr2), (v2, ptr3)]│
└────────────────────────────┘

+ O(1) память на изменение
- O(log m) доступ (бинарный поиск по версиям)
- Можно модифицировать только последнюю версию

PATH COPYING (Fully Persistent):

Создаём новые узлы на пути:
v0:root ────────────────┐
    │                   │
v1:root' (copy of root) │
    │      └──────┬─────┘
    │         shared nodes

+ O(1) доступ (как обычная структура)
+ Можно модифицировать любую версию
- O(log n) память на изменение
```

---

## Сложность операций

### Persistent Segment Tree

| Операция | Время | Память |
|----------|-------|--------|
| Build | O(n) | O(n) |
| Point Update | O(log n) | O(log n) новых узлов |
| Range Query | O(log n) | O(1) |
| Access Version v | O(1) | — |
| Total (m updates) | O(m log n) | O(n + m log n) |

### Persistent Array (Path Copying)

| Операция | Время | Память |
|----------|-------|--------|
| Build | O(n) | O(n) |
| Get(version, index) | O(log n) | O(1) |
| Update(version, index, value) | O(log n) | O(log n) |

---

## Реализация (Kotlin)

### Persistent Segment Tree

```kotlin
/**
 * Персистентное дерево отрезков
 *
 * ИДЕЯ ПЕРСИСТЕНТНОСТИ:
 * - Каждое обновление создаёт новую "версию" дерева
 * - Старые версии остаются доступными
 * - Structural Sharing: переиспользуем неизменённые поддеревья
 *
 * STRUCTURAL SHARING:
 * При update(index) копируем только O(log n) узлов на пути к index
 * Остальные поддеревья разделяются между версиями
 *
 * ВИЗУАЛИЗАЦИЯ (update index=1 в массиве [1,2,3,4]):
 *
 * Версия 0:           Версия 1 (после update):
 *      [10]                [11]  ← новый корень
 *      /  \                /  \
 *    [3]  [7]           [4]  [7]  ← [7] shared!
 *    / \   / \          / \   / \
 *  [1][2][3][4]       [1][3][3][4]  ← только [3] новый
 *
 * Память на версию: O(log n), не O(n)!
 */
class PersistentSegmentTree(private val arr: IntArray) {
    // Узлы — immutable объекты (не массив!)
    // Каждый узел содержит ссылки на детей
    data class Node(
        val sum: Long,
        val left: Node? = null,
        val right: Node? = null
    )

    private val n = arr.size
    // roots[v] = корень дерева версии v
    // Храним только корни, узлы разделяются через ссылки
    private val roots = mutableListOf<Node>()

    init {
        // Версия 0 — исходное дерево из массива
        roots.add(build(0, n - 1))
    }

    // Строим исходное дерево рекурсивно
    private fun build(l: Int, r: Int): Node {
        if (l == r) {
            return Node(sum = arr[l].toLong())
        }
        val mid = (l + r) / 2
        val leftChild = build(l, mid)
        val rightChild = build(mid + 1, r)
        return Node(
            sum = leftChild.sum + rightChild.sum,
            left = leftChild,
            right = rightChild
        )
    }

    /**
     * Point update — создаёт новую версию дерева
     *
     * @return номер новой версии
     */
    fun update(version: Int, index: Int, value: Int): Int {
        val newRoot = update(roots[version], 0, n - 1, index, value)
        roots.add(newRoot)
        return roots.size - 1  // Номер новой версии
    }

    private fun update(node: Node, l: Int, r: Int, index: Int, value: Int): Node {
        if (l == r) {
            // Создаём новый лист с новым значением
            return Node(sum = value.toLong())
        }

        val mid = (l + r) / 2

        // Копируем только узлы на пути к index
        // Ребёнок, который не изменяется — shared (переиспользуется)
        return if (index <= mid) {
            // Идём влево → правый ребёнок shared
            val newLeft = update(node.left!!, l, mid, index, value)
            Node(
                sum = newLeft.sum + node.right!!.sum,
                left = newLeft,
                right = node.right  // Structural sharing: тот же объект
            )
        } else {
            // Идём вправо → левый ребёнок shared
            val newRight = update(node.right!!, mid + 1, r, index, value)
            Node(
                sum = node.left!!.sum + newRight.sum,
                left = node.left,  // Structural sharing: тот же объект
                right = newRight
            )
        }
    }

    /**
     * Query к любой версии дерева
     */
    fun query(version: Int, queryL: Int, queryR: Int): Long {
        return query(roots[version], 0, n - 1, queryL, queryR)
    }

    private fun query(node: Node?, l: Int, r: Int, queryL: Int, queryR: Int): Long {
        if (node == null || queryL > r || queryR < l) {
            return 0
        }
        if (queryL <= l && r <= queryR) {
            return node.sum
        }
        val mid = (l + r) / 2
        return query(node.left, l, mid, queryL, queryR) +
               query(node.right, mid + 1, r, queryL, queryR)
    }

    fun versionsCount(): Int = roots.size
}
```

### Использование

```kotlin
val arr = intArrayOf(1, 2, 3, 4, 5)
val pst = PersistentSegmentTree(arr)

// Версия 0: [1, 2, 3, 4, 5]
println(pst.query(0, 0, 4))  // 15

// Update arr[2] = 10, получаем версию 1
val v1 = pst.update(0, 2, 10)  // v1 = 1

// Версия 0: [1, 2, 3, 4, 5] — не изменилась!
println(pst.query(0, 0, 4))  // 15

// Версия 1: [1, 2, 10, 4, 5]
println(pst.query(v1, 0, 4))  // 22
println(pst.query(v1, 2, 2))  // 10

// Branching: update от версии 0
val v2 = pst.update(0, 0, 100)  // v2 = 2
// Версия 2: [100, 2, 3, 4, 5] — ветка от v0, не v1
println(pst.query(v2, 0, 4))  // 114
```

### Persistent Array (Implicit Segment Tree)

```kotlin
class PersistentArray<T>(private val arr: Array<T>) {
    data class Node<T>(
        val value: T? = null,
        val left: Node<T>? = null,
        val right: Node<T>? = null
    )

    private val n = arr.size
    private val roots = mutableListOf<Node<T>>()

    init {
        roots.add(build(0, n - 1))
    }

    private fun build(l: Int, r: Int): Node<T> {
        if (l == r) {
            return Node(value = arr[l])
        }
        val mid = (l + r) / 2
        return Node(
            left = build(l, mid),
            right = build(mid + 1, r)
        )
    }

    /**
     * Получение значения по индексу в указанной версии
     *
     * СЛОЖНОСТЬ O(log n): Проход от корня до листа — высота дерева
     *
     * ПРИМЕР: get(version=0, index=2) в массиве [1,2,3,4]
     *         Корень → mid=1 → 2>1 → идём вправо
     *         [2,3,4] → mid=2 → 2<=2 → идём влево
     *         Лист [3] → возвращаем 3
     */
    operator fun get(version: Int, index: Int): T {
        return get(roots[version], 0, n - 1, index)
    }

    private fun get(node: Node<T>, l: Int, r: Int, index: Int): T {
        if (l == r) {
            return node.value!!
        }
        val mid = (l + r) / 2
        return if (index <= mid) {
            get(node.left!!, l, mid, index)
        } else {
            get(node.right!!, mid + 1, r, index)
        }
    }

    /**
     * Изменение значения по индексу — создаёт НОВУЮ версию
     *
     * СЛОЖНОСТЬ O(log n): Создаём только log n новых узлов (путь до листа)
     *                     Остальные O(n) узлов переиспользуются (structural sharing)
     *
     * ВИЗУАЛИЗАЦИЯ set(version=0, index=1, value=10) в [1,2,3,4]:
     *
     * Версия 0:           Версия 1 (новая):
     *      [10]                [12]  ← новый узел
     *      /  \                /  \
     *    [3]  [7]           [11] [7]  ← [7] SHARED!
     *    / \  / \           /  \ / \
     *  [1][2][3][4]      [1][10][3][4]  ← [3][4] SHARED!
     *                          ↑ новый лист
     *
     * Память: O(log n) новых узлов вместо O(n) при полном копировании
     */
    fun set(version: Int, index: Int, value: T): Int {
        roots.add(set(roots[version], 0, n - 1, index, value))
        return roots.size - 1
    }

    private fun set(node: Node<T>, l: Int, r: Int, index: Int, value: T): Node<T> {
        if (l == r) {
            return Node(value = value)
        }
        val mid = (l + r) / 2
        return if (index <= mid) {
            Node(
                left = set(node.left!!, l, mid, index, value),
                right = node.right  // Structural sharing: правое поддерево без изменений
            )
        } else {
            Node(
                left = node.left,  // Structural sharing: левое поддерево без изменений
                right = set(node.right!!, mid + 1, r, index, value)
            )
        }
    }
}
```

### Java реализация

```java
class PersistentSegmentTree {
    static class Node {
        long sum;
        Node left, right;

        Node(long sum) { this.sum = sum; }
        Node(long sum, Node left, Node right) {
            this.sum = sum;
            this.left = left;
            this.right = right;
        }
    }

    private int n;
    private List<Node> roots = new ArrayList<>();

    public PersistentSegmentTree(int[] arr) {
        n = arr.length;
        roots.add(build(arr, 0, n - 1));
    }

    private Node build(int[] arr, int l, int r) {
        if (l == r) {
            return new Node(arr[l]);
        }
        int mid = (l + r) / 2;
        Node left = build(arr, l, mid);
        Node right = build(arr, mid + 1, r);
        return new Node(left.sum + right.sum, left, right);
    }

    /**
     * Point Update — обновление одного элемента
     *
     * Создаёт НОВУЮ версию дерева, не изменяя старую.
     * Возвращает номер новой версии.
     *
     * Память: O(log n) новых узлов на каждый update
     */
    public int update(int version, int index, int value) {
        roots.add(update(roots.get(version), 0, n - 1, index, value));
        return roots.size() - 1;
    }

    private Node update(Node node, int l, int r, int index, int value) {
        if (l == r) {
            return new Node(value);
        }
        int mid = (l + r) / 2;
        if (index <= mid) {
            // Structural Sharing: node.right переиспользуется без копирования
            // Экономит O(n/2) памяти на каждый уровень
            Node newLeft = update(node.left, l, mid, index, value);
            return new Node(newLeft.sum + node.right.sum, newLeft, node.right);
        } else {
            Node newRight = update(node.right, mid + 1, r, index, value);
            return new Node(node.left.sum + newRight.sum, node.left, newRight);
        }
    }

    public long query(int version, int queryL, int queryR) {
        return query(roots.get(version), 0, n - 1, queryL, queryR);
    }

    private long query(Node node, int l, int r, int queryL, int queryR) {
        if (node == null || queryL > r || queryR < l) return 0;
        if (queryL <= l && r <= queryR) return node.sum;
        int mid = (l + r) / 2;
        return query(node.left, l, mid, queryL, queryR) +
               query(node.right, mid + 1, r, queryL, queryR);
    }
}
```

### Python реализация

```python
class PersistentSegmentTree:
    class Node:
        def __init__(self, sum_val=0, left=None, right=None):
            self.sum = sum_val
            self.left = left
            self.right = right

    def __init__(self, arr):
        self.n = len(arr)
        self.roots = [self._build(arr, 0, self.n - 1)]

    def _build(self, arr, l, r):
        if l == r:
            return self.Node(arr[l])
        mid = (l + r) // 2
        left = self._build(arr, l, mid)
        right = self._build(arr, mid + 1, r)
        return self.Node(left.sum + right.sum, left, right)

    def update(self, version, index, value):
        """Returns new version number"""
        new_root = self._update(self.roots[version], 0, self.n - 1, index, value)
        self.roots.append(new_root)
        return len(self.roots) - 1

    def _update(self, node, l, r, index, value):
        if l == r:
            return self.Node(value)

        mid = (l + r) // 2
        if index <= mid:
            # Structural Sharing: правый ребёнок переиспользуется
            new_left = self._update(node.left, l, mid, index, value)
            return self.Node(new_left.sum + node.right.sum, new_left, node.right)
        else:
            # Structural Sharing: левый ребёнок переиспользуется
            new_right = self._update(node.right, mid + 1, r, index, value)
            return self.Node(node.left.sum + new_right.sum, node.left, new_right)

    def query(self, version, query_l, query_r):
        return self._query(self.roots[version], 0, self.n - 1, query_l, query_r)

    def _query(self, node, l, r, query_l, query_r):
        if not node or query_l > r or query_r < l:
            return 0
        if query_l <= l and r <= query_r:
            return node.sum
        mid = (l + r) // 2
        return (self._query(node.left, l, mid, query_l, query_r) +
                self._query(node.right, mid + 1, r, query_l, query_r))
```

---

## Применения

### 1. K-th Smallest in Range (Online)

```kotlin
/**
 * Задача: Дан массив. Для каждого запроса [l, r, k]
 * найти k-й минимальный элемент на отрезке.
 *
 * Решение: Persistent Segment Tree по значениям
 */
class KthSmallest(arr: IntArray) {
    data class Node(val count: Int, val left: Node? = null, val right: Node? = null)

    private val sorted = arr.sorted().distinct()
    private val compress = sorted.withIndex().associate { it.value to it.index }
    private val roots = mutableListOf<Node>()
    private val m = sorted.size

    init {
        // Версия 0: пустое дерево (все count = 0)
        // Это "база" для первого элемента
        roots.add(buildEmpty(0, m - 1))

        /**
         * Создаём версии 1..n:
         * - Версия i содержит count элементов arr[0..i-1]
         * - roots[i] — дерево после добавления первых i элементов
         *
         * ПРИМЕР: arr = [3,1,4,1,5]
         *   roots[0]: пусто
         *   roots[1]: {3: 1}
         *   roots[2]: {1: 1, 3: 1}
         *   roots[3]: {1: 1, 3: 1, 4: 1}
         *   roots[4]: {1: 2, 3: 1, 4: 1}
         *   roots[5]: {1: 2, 3: 1, 4: 1, 5: 1}
         */
        for (x in arr) {
            val idx = compress[x]!!
            val newRoot = insert(roots.last(), 0, m - 1, idx)
            roots.add(newRoot)
        }
    }

    private fun buildEmpty(l: Int, r: Int): Node {
        if (l == r) return Node(0)
        val mid = (l + r) / 2
        return Node(0, buildEmpty(l, mid), buildEmpty(mid + 1, r))
    }

    private fun insert(node: Node, l: Int, r: Int, idx: Int): Node {
        if (l == r) {
            return Node(node.count + 1)
        }
        val mid = (l + r) / 2
        return if (idx <= mid) {
            Node(
                node.count + 1,
                insert(node.left!!, l, mid, idx),
                node.right
            )
        } else {
            Node(
                node.count + 1,
                node.left,
                insert(node.right!!, mid + 1, r, idx)
            )
        }
    }

    /**
     * Поиск k-го минимального на отрезке [l, r]
     *
     * КЛЮЧЕВАЯ ИДЕЯ: Разность версий
     *   roots[r+1] - roots[l] = "виртуальное дерево" только для [l, r]
     *
     * ПРИМЕР: arr = [3,1,4,1,5], запрос (l=1, r=3, k=2)
     *   roots[4] содержит {1:2, 3:1, 4:1} — prefix [0..3]
     *   roots[1] содержит {3:1} — prefix [0..0]
     *   Разность: {1:2, 4:1} — элементы [1,4,1] на [1..3]
     *   k=2 → второй минимум = 1 (есть два раза)
     */
    fun query(l: Int, r: Int, k: Int): Int {
        return query(roots[l], roots[r + 1], 0, m - 1, k)
    }

    private fun query(nodeL: Node, nodeR: Node, l: Int, r: Int, k: Int): Int {
        if (l == r) return sorted[l]

        val mid = (l + r) / 2
        // Разность count: сколько элементов из отрезка попало в левое поддерево
        // leftCount = (элементов ≤ mid в [0..r]) - (элементов ≤ mid в [0..l-1])
        val leftCount = nodeR.left!!.count - nodeL.left!!.count

        return if (k <= leftCount) {
            // k-й элемент находится слева
            query(nodeL.left!!, nodeR.left!!, l, mid, k)
        } else {
            // k-й элемент справа, но индекс сдвигаем: k - leftCount
            query(nodeL.right!!, nodeR.right!!, mid + 1, r, k - leftCount)
        }
    }
}
```

### 2. Undo/Redo Stack

```kotlin
/**
 * Массив с поддержкой Undo
 *
 * Использует персистентный массив для хранения всех версий.
 * history хранит стек посещённых версий для навигации.
 *
 * ПРИМЕР:
 *   [1,2,3] → set(0, 10) → [10,2,3]
 *           → set(1, 20) → [10,20,3]
 *           → undo()     → [10,2,3]
 *           → undo()     → [1,2,3]
 */
class UndoableArray<T>(initial: Array<T>) {
    private val pArray = PersistentArray(initial)
    private var currentVersion = 0
    // Стек версий: [v0, v1, v2, ...] — путь истории
    private val history = mutableListOf(0)

    operator fun get(index: Int): T = pArray[currentVersion, index]

    fun set(index: Int, value: T) {
        val newVersion = pArray.set(currentVersion, index, value)
        currentVersion = newVersion
        /**
         * "Обрезка будущего" при новом действии после undo:
         *
         * История была: [v0] → [v1] → [v2] → [v3]
         * После 2× undo: currentVersion = v1
         * При новом set: создаётся v4, но v2,v3 — "мёртвые ветки"
         *
         * Отсекаем всё после текущей позиции, добавляем новую версию
         */
        while (history.size > 0 && history.last() != currentVersion - 1) {
            history.removeAt(history.size - 1)
        }
        history.add(currentVersion)
    }

    fun undo(): Boolean {
        if (history.size <= 1) return false
        history.removeAt(history.size - 1)
        currentVersion = history.last()
        return true
    }

    // Redo требует отдельного "forward stack" — отсечённые версии
    // При undo сохраняем версию в redoStack
    // При redo достаём из redoStack
    // При новом set очищаем redoStack (branching)
}
```

### 3. 2D Range Sum (Online)

```kotlin
/**
 * Offline задачи: можно использовать сортировку
 * Online: Persistent Segment Tree
 *
 * Идея: Каждый столбец — версия дерева
 */
class Persistent2DSum(matrix: Array<IntArray>) {
    // Каждая версия = prefix sum до этого столбца
    private val pst: PersistentSegmentTree
    private val versions: List<Int>

    init {
        val n = matrix.size
        val m = matrix[0].size

        /**
         * Построение по столбцам:
         *
         * versions[j] = дерево с prefix sum столбцов [0..j]
         *
         * ВИЗУАЛИЗАЦИЯ для матрицы 3×3:
         *   Col 0    Col 1    Col 2
         *   [1]      [1+2]    [1+2+3]
         *   [4]  →   [4+5] →  [4+5+6]
         *   [7]      [7+8]    [7+8+9]
         *
         * Каждый столбец — новая версия PST
         */
        val firstCol = IntArray(n) { matrix[it][0] }
        pst = PersistentSegmentTree(firstCol)

        val vers = mutableListOf(0)
        for (j in 1 until m) {
            var version = vers.last()
            for (i in 0 until n) {
                version = pst.update(version, i,
                    (pst.query(version, i, i) + matrix[i][j]).toInt())
            }
            vers.add(version)
        }
        versions = vers
    }

    /**
     * Сумма в прямоугольнике [r1,c1] → [r2,c2]
     *
     * ФОРМУЛА:
     *   sum(r1..r2, c1..c2) = prefix[c2] - prefix[c1-1]
     *
     * ПРИМЕР: query(0,1, 2,2) в матрице выше
     *   versions[2]: prefix sum [0..2] → [6, 15, 24]
     *   versions[0]: prefix sum [0..0] → [1, 4, 7]
     *   Результат: (6+15+24) - (1+4+7) = 33
     */
    fun query(r1: Int, c1: Int, r2: Int, c2: Int): Long {
        val right = pst.query(versions[c2], r1, r2)
        val left = if (c1 > 0) pst.query(versions[c1 - 1], r1, r2) else 0L
        return right - left
    }
}
```

---

## Распространённые ошибки

### 1. Модификация shared узлов

```kotlin
// ❌ НЕПРАВИЛЬНО: мутация shared node
fun update(node: Node, ...): Node {
    node.sum += delta  // ОШИБКА! Изменяет все версии!
    return node
}

// ✅ ПРАВИЛЬНО: создаём новый узел
fun update(node: Node, ...): Node {
    return Node(
        sum = node.sum + delta,  // Новый объект! Старый node не меняется
        left = node.left,        // Structural sharing: дети общие
        right = node.right
    )
}
```

### 2. Memory leak от циклических ссылок

```kotlin
// ❌ НЕПРАВИЛЬНО: ссылка на parent создаёт цикл
data class Node(
    val value: Int,
    val left: Node?,
    val right: Node?,
    var parent: Node?  // ОШИБКА! Цикл, память не освобождается
)

// ✅ ПРАВИЛЬНО: без parent, или WeakReference
data class Node(
    val value: Int,
    val left: Node?,
    val right: Node?
)
```

### 3. Неправильный выбор версии для branching

```kotlin
// ❌ НЕПРАВИЛЬНО: всегда update от последней версии
fun update(index: Int, value: Int) {
    val newRoot = update(roots.last(), ...)  // Линейная история
    roots.add(newRoot)
}

// ✅ ПРАВИЛЬНО: можно branch от любой версии
fun update(version: Int, index: Int, value: Int): Int {
    /**
     * Branching: создаём "ветку" от любой версии
     *
     *       v0 ─── v1 ─── v2 ─── v3
     *               │
     *               └── v4 ─── v5  ← branch от v1
     *
     * Полезно для: git-like истории, альтернативных сценариев,
     *              undo с сохранением обоих путей
     */
    val newRoot = update(roots[version], ...)
    roots.add(newRoot)
    return roots.size - 1
}
```

### 4. Переполнение при большом количестве версий

```kotlin
// ❌ НЕПРАВИЛЬНО: все версии в памяти навсегда
val roots = mutableListOf<Node>()  // Память растёт бесконечно

// ✅ ПРАВИЛЬНО: GC-friendly или явное удаление старых версий
class PersistentWithGC {
    // Используй WeakReference или explicit cleanup
    // Или ограничь количество версий
}
```

### 5. O(n) при обходе всех элементов

```kotlin
// ❌ НЕПРАВИЛЬНО: обход O(n) на каждую версию
fun toList(version: Int): List<Int> {
    return (0 until n).map { get(version, it) }  // O(n log n)!
}

// ✅ ПРАВИЛЬНО: рекурсивный обход
fun toList(version: Int): List<Int> {
    val result = mutableListOf<Int>()
    collectLeaves(roots[version], 0, n - 1, result)
    return result  // O(n)
}
```

---

## Когда использовать

### Persistent Data Structures лучше когда:

| Критерий | Почему |
|----------|--------|
| Нужна история изменений | Undo/Redo, audit log |
| Версионные запросы | "Какой была сумма на шаге k?" |
| Concurrency | Immutable = thread-safe |
| Functional programming | Clojure, Haskell стиль |
| Offline queries | Запросы отсортированы по времени |

### Альтернативы

| Ситуация | Используй |
|----------|-----------|
| Не нужны старые версии | Обычные структуры |
| Нужны только последние k версий | Rolling snapshots |
| Частые обновления, редкие версии | Copy-on-Write с batching |

---

## Сравнение с альтернативами

| Подход | Update | Query | Space | Versions |
|--------|--------|-------|-------|----------|
| Copy entire | O(n) | O(query) | O(n × m) | m |
| Persistent | O(log n) | O(query) | O(n + m log n) | m |
| Ephemeral | O(update) | O(query) | O(n) | 1 |

---

## Практика

### Концептуальные вопросы

1. **Почему Path Copying работает?**

   Неизменённые поддеревья разделяются между версиями. Изменение затрагивает только O(log n) узлов на пути от корня.

2. **Fat Node vs Path Copying?**

   Fat Node: O(1) память, O(log m) доступ, частичная персистентность.
   Path Copying: O(log n) память, O(1) доступ, полная персистентность.

3. **Как сделать persistent linked list?**

   Cons cell (head, tail). Добавление в начало O(1) — просто создаём новый head, tail shared.

4. **Thread-safety?**

   Immutable структуры автоматически thread-safe для чтения. Для создания новых версий нужна синхронизация.

### LeetCode задачи

| # | Название | Сложность | Паттерн |
|---|----------|-----------|---------|
| 315 | Count of Smaller Numbers | Hard | Persistent + Merge Sort |
| 493 | Reverse Pairs | Hard | Persistent ST |
| 1649 | Create Sorted Array | Hard | BIT / Persistent |
| — | SPOJ MKTHNUM | — | K-th in range (classic) |

### Задача: Kth Smallest in Subarray

```
Дано: массив a[0..n-1]
Запросы: (l, r, k) — k-й минимальный на [l, r]

Решение:
1. Сжатие координат значений
2. Persistent Segment Tree по значениям
3. Версия i = элементы a[0..i-1]
4. count[l,r] = count[0,r] - count[0,l-1]
5. Бинарный спуск по дереву
```

---

## Связь с функциональным программированием

Персистентные структуры данных -- не просто инструмент олимпиадного программирования. Они являются ОСНОВОЙ функциональных языков программирования.

В Clojure ВСЕ стандартные структуры данных персистентны по умолчанию. Когда вы пишете `(assoc my-map :key "value")`, вы получаете НОВУЮ версию map'а, а старая остаётся неизменной. Под капотом Clojure использует Hash Array Mapped Trie (HAMT) -- разновидность персистентного дерева с branching factor 32. Это не совсем path copying (используется wider tree для лучшей cache locality), но принцип тот же: structural sharing.

В Haskell иммутабельность -- свойство самого языка. Каждое "изменение" структуры данных создаёт новую версию. Компилятор и runtime оптимизируют это: если старая версия больше не нужна, garbage collector освобождает её узлы (а shared узлы остаются, пока на них ссылается хотя бы одна версия).

В React/Redux состояние приложения -- персистентный объект. `dispatch(action)` создаёт новое состояние, старое сохраняется для time-travel debugging. Библиотека Immer реализует это через copy-on-write proxy, а Immutable.js -- через полноценные persistent trie.

> **Ключевой инсайт:** Иммутабельность не противоречит эффективности. Structural sharing позволяет создавать "новые" версии данных за O(log n), сохраняя доступ к старым. Это фундаментальная идея, объединяющая теоретическую CS, функциональное программирование и практические системы (Git, databases, UI frameworks).

---

## Связь с другими темами

**[[segment-tree]]** -- Persistent Segment Tree -- это Segment Tree + path copying. Все операции работают аналогично обычному Segment Tree, но вместо модификации узлов мы создаём новые. Понимание обычного Segment Tree -- абсолютный prerequisite.

**[[trees-binary]]** -- Path copying работает на любых деревьях, но наиболее эффективен на сбалансированных (O(log n) путь). На несбалансированном дереве высотой n path copying потребует O(n) памяти на update -- теряем все преимущества.

**Functional Programming** -- Персистентные структуры данных -- это материализация принципа иммутабельности. Clojure, Haskell, Elm, Scala используют их как фундамент. Понимание path copying и structural sharing делает работу с этими языками значительно проще.

**MVCC в базах данных** -- PostgreSQL использует Multi-Version Concurrency Control, где каждая транзакция видит свою "версию" данных. Это концептуально идентично персистентным структурам: старые версии сосуществуют с новыми, читатели не блокируют писателей.

---

## Источники и дальнейшее чтение

- **Driscoll, J., Sarnak, N., Sleator, D., Tarjan, R. (1989). Making Data Structures Persistent.** -- Оригинальная статья, формализовавшая понятие персистентности и предложившая Fat Node и Path Copying. Классика алгоритмической теории.

- **Okasaki, C. (1998). Purely Functional Data Structures.** -- Книга о персистентных структурах данных в контексте функционального программирования. Показывает, как достичь амортизированной эффективности без мутаций. Обязательна для понимания связи FP и persistence.

- **Cormen, T. et al. (2009). Introduction to Algorithms (CLRS), Chapter 13 (Problem 13-1).** -- Задача на persistent Red-Black tree. Показывает, как path copying применяется к сбалансированным деревьям.

- **Hickey, R. (2009). Are We There Yet? (talk).** -- Создатель Clojure объясняет, почему персистентные структуры данных фундаментальны для правильного моделирования состояния и времени в программировании.

---

*Последнее обновление: 2026-02-10 -- Добавлена глубокая теория: проблема запоминания прошлого (текстовый редактор, Git аналогия), trade-off время/память, связь с функциональным программированием (Clojure, Haskell, React/Redux), связь с MVCC в базах данных*

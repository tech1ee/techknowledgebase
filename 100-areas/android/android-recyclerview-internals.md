---
title: "RecyclerView Internals: кэширование, переработка и производительность"
created: 2026-01-27
modified: 2026-01-29
type: deep-dive
area: android
confidence: high
tags:
  - android
  - recyclerview
  - viewholder
  - diffutil
  - performance
related:
  - "[[android-overview]]"
  - "[[android-view-rendering-pipeline]]"
  - "[[android-compose]]"
  - "[[android-ui-views]]"
  - "[[android-custom-view-fundamentals]]"
  - "[[android-performance-profiling]]"
cs-foundations: [object-pool, cache-hierarchy, producer-consumer, diff-algorithm, amortized-complexity]
---

# RecyclerView Internals: кэширование, переработка и производительность

> RecyclerView — это не просто "улучшенный ListView". Это четырёхуровневая система кэширования с предиктивной предзагрузкой, алгоритмом Eugene Myers для diff-вычислений и паттерном ViewHolder, который превращает дорогую операцию inflation (5-10мс) в дешёвое связывание данных (0.01мс). Для списка в 1000 элементов создаётся всего 10-15 ViewHolder, остальные переиспользуются через Object Pool pattern. Понимание этих механизмов — ключ к спискам на 60+ FPS.

---

## Зачем это нужно

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| Лист дёргается при скролле | Inflation новых View на каждый кадр | Jank, < 60 FPS |
| Белые/пустые элементы при быстром скролле | Пустой RecycledViewPool | Плохой UX |
| OOM при длинных списках | Нет переработки View, утечки в onBindViewHolder | Crash |
| Долгий первый скролл | Нет prefetch, тяжёлый onCreateViewHolder | Задержка, фриз |
| Мигание элементов при обновлении | `notifyDataSetChanged()` вместо DiffUtil | Потеря анимаций |
| Вложенные списки тормозят | Нет shared pool, много inflation | Серьёзный jank |
| Анимации не работают | ItemAnimator отключен или неверный notify | Резкие переходы |
| Scroll position сбрасывается | Неверная работа с state restoration | Плохой UX |

### Актуальность (2024-2025)

```
Timeline эволюции списков в Android:
────────────────────────────────────────────────────────────────────

Android 1.0      ── ListView, Gallery, GridView
        │            └── convertView pattern (опционально)
        │
Android 2.3 (9)  ── AbsListView optimizations
        │
Android 5.0 (21) ── RecyclerView в Support Library
        │            ├── ОБЯЗАТЕЛЬНЫЙ ViewHolder
        │            ├── LayoutManager архитектура
        │            ├── ItemAnimator
        │            └── ItemDecoration
        │
Android 7.0 (24) ── GapWorker prefetch
        │            └── Предзагрузка в idle time
        │
Android 8.0 (26) ── ListAdapter, AsyncListDiffer
        │            └── Background diff computation
        │
Android 10 (29)  ── ConcatAdapter, MergeAdapter
        │            └── Объединение нескольких адаптеров
        │
Android 11 (30)  ── StateRestorationPolicy
        │            └── Контроль восстановления scroll position
        │
Android 12 (31)  ── Stretch overscroll effect
        │
Jetpack Compose  ── LazyColumn, LazyRow, LazyGrid
                     ├── Декларативный подход
                     ├── Automatic diffing with key
                     └── НО: нет shared pool между списками
```

**Текущая ситуация (2025):**
- **>80%** production apps используют RecyclerView
- Compose LazyColumn набирает популярность, но не заменяет RecyclerView полностью
- RecyclerView критичен для: nested lists, complex animations, shared ViewHolder pools
- Глубокое понимание internals необходимо для оптимизации

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|------------|-------------|
| View rendering pipeline | RecyclerView — ViewGroup; measure/layout/draw | [[android-view-rendering-pipeline]] |
| Custom View | ViewHolder = findView cache pattern, LayoutManager | [[android-custom-view-fundamentals]] |
| Handler/Looper/Choreographer | GapWorker prefetch, VSYNC | [[android-handler-looper]] |
| View system | LayoutParams, measure specs, View lifecycle | [[android-ui-views]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **ViewHolder** | Объект-кэш для View элемента: хранит references на child views | Шкафчик с именными ячейками — не нужно искать заново |
| **Recycler** | Внутренний класс RecyclerView, управляет переработкой ViewHolder | Конвейер на заводе: готовые детали используются повторно |
| **Adapter** | Мост между данными и ViewHolder: создаёт, связывает | Оператор конвейера: знает какую деталь как покрасить |
| **LayoutManager** | Позиционирует элементы на экране, определяет scroll behavior | Архитектор — решает где что стоит |
| **Scrap** | Временно открепленные View во время layout pass | Карточки на столе — вернутся на место без изменений |
| **Cache (mCachedViews)** | ViewHolder-ы недавно ушедшие за экран | Полка рядом с конвейером — быстрый доступ без rebind |
| **RecycledViewPool** | Общий пул ViewHolder-ов по viewType | Склад деталей — нужна покраска (rebind) |
| **DiffUtil** | Вычислитель разницы между списками (Eugene Myers algorithm) | Diff в Git — находит что изменилось |
| **ListAdapter** | Adapter + AsyncListDiffer для автоматического background diff | Умный конвейер с автоматическим diff |
| **ItemDecoration** | Рисует декорации (разделители, отступы, backgrounds) | Рамки и линейки между карточками |
| **ItemAnimator** | Анимирует добавление/удаление/перемещение/изменение | Режиссёр переходов между сценами |
| **GapWorker** | Предзагрузчик элементов в idle time между кадрами | Ассистент, готовящий материалы пока мастер отдыхает |
| **SnapHelper** | Выравнивает элементы после скролла (как ViewPager) | Магнит, притягивающий к определённым позициям |
| **ItemTouchHelper** | Drag & drop, swipe to dismiss | Помощник для жестов |

---

## Архитектура RecyclerView

### Компоненты и их взаимодействие

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             RecyclerView                                     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                          PUBLIC API                                     │ │
│  │  setAdapter(), setLayoutManager(), addItemDecoration(),                │ │
│  │  setItemAnimator(), scrollToPosition(), smoothScrollToPosition()       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                   │                                          │
│           ┌───────────────────────┼───────────────────────┐                 │
│           ▼                       ▼                       ▼                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐      │
│  │    Adapter<VH>   │  │  LayoutManager   │  │      Recycler        │      │
│  │                  │  │                  │  │  (inner class)       │      │
│  │ • getItemCount() │  │ • onLayoutChild  │  │                      │      │
│  │ • onCreateVH()   │  │   ren()          │  │ • mAttachedScrap     │      │
│  │ • onBindVH()     │  │ • scrollBy()     │  │ • mChangedScrap      │      │
│  │ • getItemViewType│  │ • findViewBy     │  │ • mCachedViews       │      │
│  │ • onViewRecycled │  │   Position()     │  │ • mViewCacheExtension│      │
│  │ • onViewAttached │  │ • canScroll*()   │  │ • mRecyclerPool      │      │
│  │ • onViewDetached │  │ • prefetch*()    │  │                      │      │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────┬───────────┘      │
│           │                     │                       │                   │
│           │    ┌────────────────┼───────────────────────┘                   │
│           │    │                │                                           │
│           ▼    ▼                ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        ViewHolder                                    │   │
│  │  • itemView: View          • mPosition: int                         │   │
│  │  • mItemViewType: int      • mPreLayoutPosition: int                │   │
│  │  • mOwnerRecyclerView      • mFlags: int (bound, invalid, ...)      │   │
│  │  • mNestedRecyclerView     • mPayloads: List<Object>                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐      │
│  │  ItemDecoration  │  │   ItemAnimator   │  │      State           │      │
│  │                  │  │                  │  │  (inner class)       │      │
│  │ • onDraw()       │  │ • animateAdd()   │  │                      │      │
│  │ • onDrawOver()   │  │ • animateRemove()│  │ • mTargetPosition    │      │
│  │ • getItemOffsets │  │ • animateMove()  │  │ • mLayoutStep        │      │
│  │                  │  │ • animateChange()│  │ • mItemCount         │      │
│  │                  │  │ • runPending()   │  │ • mIsMeasuring       │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘      │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐      │
│  │    GapWorker     │  │   SnapHelper     │  │  ItemTouchHelper     │      │
│  │  (prefetch)      │  │  (alignment)     │  │  (drag & swipe)      │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Жизненный цикл ViewHolder

```
                    ┌─────────────────────────────────────────┐
                    │              LIFECYCLE                   │
                    └─────────────────────────────────────────┘

   Adapter.onCreateViewHolder()
            │
            ▼
   ┌────────────────┐
   │   CREATED      │ ← ViewHolder создан, itemView inflated
   │  (unbound)     │    mPosition = NO_POSITION (-1)
   └───────┬────────┘
           │
           │ Adapter.onBindViewHolder(holder, position)
           ▼
   ┌────────────────┐
   │    BOUND       │ ← Данные привязаны
   │  (attached)    │    mPosition = adapter position
   │                │    FLAG_BOUND = true
   └───────┬────────┘
           │
           │ RecyclerView.addView() → onViewAttachedToWindow()
           ▼
   ┌────────────────┐
   │   VISIBLE      │ ← На экране, пользователь видит
   │  (on screen)   │
   └───────┬────────┘
           │
           │ Scroll off screen
           ▼
   ┌────────────────┐
   │   DETACHED     │ ← Ушёл за экран
   │ (off screen)   │    onViewDetachedFromWindow()
   └───────┬────────┘
           │
           ├───────────────────────────┐
           │                           │
           ▼                           ▼
   ┌────────────────┐         ┌────────────────┐
   │  mCachedViews  │         │ RecycledView   │
   │  (position-    │         │ Pool (viewType │
   │   specific)    │         │  only)         │
   │                │         │                │
   │ NO rebind!     │         │ NEEDS rebind!  │
   └───────┬────────┘         └───────┬────────┘
           │                           │
           │ Return to same position   │ Return to any position
           │                           │ of same viewType
           ▼                           │
   ┌────────────────┐                  │
   │   VISIBLE      │ ←────────────────┘
   │  (reused)      │    onBindViewHolder() called (for pool)
   └────────────────┘

   Special states:
   ┌────────────────┐
   │   REMOVED      │ ← Adapter removed item
   │                │    Pending removal animation
   └────────────────┘

   ┌────────────────┐
   │   INVALID      │ ← notifyDataSetChanged()
   │                │    Must rebind
   └────────────────┘

   ┌────────────────┐
   │   RECYCLED     │ ← onViewRecycled() called
   │                │    Clear listeners, cancel async ops
   └────────────────┘
```

### Сравнение ListView vs RecyclerView

| Аспект | ListView | RecyclerView |
|--------|----------|-------------|
| ViewHolder | Опционально (if convertView == null) | **ОБЯЗАТЕЛЬНО** |
| LayoutManager | Только вертикальный | Linear, Grid, Staggered, Custom |
| Orientation | Только вертикальный | Любая |
| Item animations | Нет встроенных | ItemAnimator (fade, translate) |
| DiffUtil | Нет | Встроенная поддержка |
| Декорации | divider XML attribute | ItemDecoration (гибко) |
| Prefetch | Нет | GapWorker (автоматически) |
| Nested scrolling | Проблемы | NestedScrollingChild |
| Item touch (drag/swipe) | Нет | ItemTouchHelper |
| Snap to position | Нет | SnapHelper |
| Multi-adapter | Нет | ConcatAdapter |
| State restoration | Автоматически | Контролируемо (StateRestorationPolicy) |

---

## ViewHolder Pattern — почему inflation дорог

### Стоимость операций (профилированные данные)

```
╔══════════════════════════════════════════════════════════════════════════╗
║                      СТОИМОСТЬ ОПЕРАЦИЙ (Pixel 6)                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  View inflation (XML → View tree):              ~3-15 мс                 ║
║  ══════════════════════════════════════════════                          ║
║    • XmlPullParser чтение XML                   ~0.5 мс                  ║
║    • Рефлексия (Class.forName, newInstance)     ~1-3 мс per View         ║
║    • LayoutParams парсинг                       ~0.2 мс                  ║
║    • Построение дерева View                     ~0.5 мс                  ║
║    • Custom attributes (obtainStyledAttrib)    ~0.3 мс                  ║
║    • Сложный layout (ConstraintLayout):         ~5-10 мс                 ║
║    • Простой layout (LinearLayout):             ~2-5 мс                  ║
║                                                                          ║
║  View binding (данные → View):                  ~0.01-0.5 мс             ║
║  ══════════════════════════════════════════════                          ║
║    • TextView.setText()                         ~0.01 мс                 ║
║    • ImageView.setImageResource()               ~0.02 мс (sync res load) ║
║    • ImageView.setImageBitmap()                 ~0.05 мс                 ║
║    • Async image load (Glide/Coil)              ~0.01 мс (schedule only) ║
║    • Click listeners                            ~0.001 мс                ║
║                                                                          ║
║  ══════════════════════════════════════════════════════════════════════  ║
║  РАЗНИЦА: 100-1000x — именно это экономит ViewHolder                     ║
║                                                                          ║
║  Frame budget at 60 FPS:  16.6 мс                                        ║
║  Frame budget at 120 FPS: 8.3 мс                                         ║
║                                                                          ║
║  Один inflation = 30-90% frame budget!                                   ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### ViewHolder implementation

```kotlin
class UserAdapter(
    private val onClick: (User) -> Unit
) : RecyclerView.Adapter<UserAdapter.UserViewHolder>() {

    private var users: List<User> = emptyList()

    // ═══════════════════════════════════════════════════════════════
    // onCreateViewHolder — вызывается ТОЛЬКО когда нужен НОВЫЙ ViewHolder
    // Это ДОРОГАЯ операция (inflation)
    // Для списка в 1000 элементов вызывается ~10-15 раз
    // ═══════════════════════════════════════════════════════════════
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        // ~5-10ms на inflation
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)

        return UserViewHolder(view, onClick)
    }

    // ═══════════════════════════════════════════════════════════════
    // onBindViewHolder — вызывается ЧАСТО (при каждом показе элемента)
    // Это ДЕШЁВАЯ операция (только присваивание)
    // Для списка в 1000 элементов вызывается ~1000+ раз
    // ═══════════════════════════════════════════════════════════════
    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        // ~0.1ms на bind
        holder.bind(users[position])
    }

    // Partial bind — только изменившиеся поля
    override fun onBindViewHolder(
        holder: UserViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
        if (payloads.isEmpty()) {
            // Full bind
            onBindViewHolder(holder, position)
        } else {
            // Partial bind — обновить только изменённое
            payloads.forEach { payload ->
                when (payload) {
                    is UserPayload.NameChanged -> holder.updateName(payload.newName)
                    is UserPayload.AvatarChanged -> holder.updateAvatar(payload.newUrl)
                }
            }
        }
    }

    override fun getItemCount() = users.size

    // Stable IDs для эффективных анимаций
    override fun getItemId(position: Int): Long = users[position].id

    // Очистка при recycling (отменить async операции)
    override fun onViewRecycled(holder: UserViewHolder) {
        holder.clear()
    }

    fun submitList(newUsers: List<User>) {
        users = newUsers
        notifyDataSetChanged() // или используйте ListAdapter для DiffUtil
    }

    // ═══════════════════════════════════════════════════════════════
    // ViewHolder — кэш references на child views
    // findViewById вызывается ОДИН РАЗ при создании
    // ═══════════════════════════════════════════════════════════════
    class UserViewHolder(
        itemView: View,
        private val onClick: (User) -> Unit
    ) : RecyclerView.ViewHolder(itemView) {

        // View references — кэшируются в ViewHolder
        private val nameText: TextView = itemView.findViewById(R.id.name)
        private val emailText: TextView = itemView.findViewById(R.id.email)
        private val avatarImage: ImageView = itemView.findViewById(R.id.avatar)

        private var currentUser: User? = null

        init {
            // Click listener устанавливается ОДИН РАЗ
            itemView.setOnClickListener {
                currentUser?.let(onClick)
            }
        }

        fun bind(user: User) {
            currentUser = user
            nameText.text = user.name
            emailText.text = user.email

            // Async image loading
            Glide.with(avatarImage)
                .load(user.avatarUrl)
                .placeholder(R.drawable.avatar_placeholder)
                .circleCrop()
                .into(avatarImage)
        }

        fun updateName(name: String) {
            nameText.text = name
        }

        fun updateAvatar(url: String) {
            Glide.with(avatarImage)
                .load(url)
                .circleCrop()
                .into(avatarImage)
        }

        fun clear() {
            // ВАЖНО: отменить async операции при recycling
            Glide.with(avatarImage).clear(avatarImage)
            currentUser = null
        }
    }

    // Payload для partial updates
    sealed class UserPayload {
        data class NameChanged(val newName: String) : UserPayload()
        data class AvatarChanged(val newUrl: String) : UserPayload()
    }
}
```

### ViewBinding в ViewHolder (современный подход)

```kotlin
class UserViewHolder(
    private val binding: ItemUserBinding,
    private val onClick: (User) -> Unit
) : RecyclerView.ViewHolder(binding.root) {

    private var currentUser: User? = null

    init {
        binding.root.setOnClickListener {
            currentUser?.let(onClick)
        }
    }

    fun bind(user: User) {
        currentUser = user
        binding.apply {
            name.text = user.name
            email.text = user.email
            Glide.with(avatar).load(user.avatarUrl).circleCrop().into(avatar)
        }
    }
}

// В Adapter:
override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
    val binding = ItemUserBinding.inflate(
        LayoutInflater.from(parent.context), parent, false
    )
    return UserViewHolder(binding, onClick)
}
```

---

## Четыре уровня кэша Recycler

Это **ключевая архитектурная особенность** RecyclerView.

### Обзор иерархии кэширования

```
╔══════════════════════════════════════════════════════════════════════════╗
║        Recycler.tryGetViewHolderForPositionByDeadline()                  ║
║                                                                          ║
║  Поиск ViewHolder для заданной позиции:                                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  УРОВЕНЬ 1: mChangedScrap                                                ║
║  ─────────────────────────────────────                                   ║
║  ├── Назначение: ViewHolder с изменёнными данными (анимация)             ║
║  ├── Когда: notifyItemChanged() → анимация old→new                       ║
║  ├── Rebind: ДА (для анимации)                                           ║
║  └── Найден? → return (для анимации изменения)                           ║
║         ↓ нет                                                            ║
║                                                                          ║
║  УРОВЕНЬ 2: mAttachedScrap                                               ║
║  ─────────────────────────────────────                                   ║
║  ├── Назначение: временно открепленные View при layout pass              ║
║  ├── Когда: onLayoutChildren(), requestLayout()                          ║
║  ├── Rebind: НЕТ (тот же position, те же данные)                         ║
║  └── Найден? → return (мгновенно, без работы)                            ║
║         ↓ нет                                                            ║
║                                                                          ║
║  УРОВЕНЬ 3: mCachedViews                                                 ║
║  ─────────────────────────────────────                                   ║
║  ├── Назначение: ViewHolder недавно ушедшие за экран                     ║
║  ├── Размер: DEFAULT_CACHE_SIZE = 2                                      ║
║  ├── Rebind: НЕТ (хранит position + данные)                              ║
║  ├── Match: position + stable id                                         ║
║  └── Найден? → return (мгновенно, без rebind)                            ║
║         ↓ нет                                                            ║
║                                                                          ║
║  УРОВЕНЬ 4: mViewCacheExtension                                          ║
║  ─────────────────────────────────────                                   ║
║  ├── Назначение: пользовательский кэш-слой                               ║
║  ├── API: getViewForPositionAndType(recycler, position, type)            ║
║  ├── Используется: КРАЙНЕ РЕДКО                                          ║
║  └── Найден? → return                                                    ║
║         ↓ нет                                                            ║
║                                                                          ║
║  УРОВЕНЬ 5: mRecyclerPool (RecycledViewPool)                             ║
║  ─────────────────────────────────────                                   ║
║  ├── Назначение: пул ViewHolder по viewType                              ║
║  ├── Размер: DEFAULT_MAX_SCRAP = 5 per viewType                          ║
║  ├── Rebind: ДА ВСЕГДА (только viewType, данные очищены)                 ║
║  ├── Match: viewType ONLY                                                ║
║  ├── КЛЮЧЕВОЕ: можно shared между RecyclerView!                          ║
║  └── Найден? → return + onBindViewHolder()                               ║
║         ↓ нет                                                            ║
║                                                                          ║
║  УРОВЕНЬ 6: Adapter.onCreateViewHolder()                                 ║
║  ─────────────────────────────────────                                   ║
║  └── Создать новый ViewHolder (дорого: inflation)                        ║
║      + onBindViewHolder()                                                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Уровень 1-2: Scrap (mAttachedScrap + mChangedScrap)

```
Scrap — ВРЕМЕННОЕ хранилище во время layout pass
══════════════════════════════════════════════════

Layout pass начинается:
┌────────────────────────────────────────────────────┐
│  onLayoutChildren()                                │
│                                                    │
│  1. detachAndScrapAttachedViews(recycler)         │
│     ┌─────────────────────────────────────────┐   │
│     │ Все attached views → mAttachedScrap     │   │
│     │                                          │   │
│     │ View1 → scrap (pos=0)                   │   │
│     │ View2 → scrap (pos=1)                   │   │
│     │ View3 → scrap (pos=2)                   │   │
│     │ View4 → scrap (pos=3)                   │   │
│     │ View5 → scrap (pos=4)                   │   │
│     └─────────────────────────────────────────┘   │
│                                                    │
│  2. fill() — заполнить layout                     │
│     ┌─────────────────────────────────────────┐   │
│     │ for position in visible range:          │   │
│     │   vh = getViewForPosition(pos)          │   │
│     │        ↓                                │   │
│     │   Сначала ищем в scrap (по position)    │   │
│     │        ↓                                │   │
│     │   Нашли? → return из scrap (БЕЗ rebind) │   │
│     │   Не нашли? → следующий уровень кэша    │   │
│     └─────────────────────────────────────────┘   │
│                                                    │
│  3. recycleAndClearCachedViews()                  │
│     Оставшиеся в scrap → RecycledViewPool         │
│                                                    │
└────────────────────────────────────────────────────┘

mChangedScrap — для анимации изменений:
────────────────────────────────────────
notifyItemChanged(pos=2)
  │
  ▼
┌─────────────────────────────────────────────────┐
│  Pre-layout: старый ViewHolder(pos=2) → scrap   │
│  Создать новый ViewHolder → bind с новыми данными│
│  Post-layout: анимация old → new                │
│  old ViewHolder → RecycledViewPool              │
└─────────────────────────────────────────────────┘
```

### Уровень 3: mCachedViews (position-specific cache)

```
mCachedViews — ViewHolder ушедшие за экран
═══════════════════════════════════════════

Структура: ArrayList<ViewHolder>
Размер по умолчанию: 2 (DEFAULT_CACHE_SIZE)
Вытеснение: FIFO (старейший → RecycledViewPool)

Scroll DOWN (элементы уходят вверх):
──────────────────────────────────────

  Visible:     [0] [1] [2] [3] [4]
                ↑
  Scroll...
                ↓
  Visible:     [1] [2] [3] [4] [5]
               │
               └─ Element[0] → mCachedViews

  mCachedViews: [ VH(pos=0) ]
  Match by: position + stable id (if hasStableIds)

Scroll UP (вернуться к элементу 0):
──────────────────────────────────────

  getViewForPosition(0)
    ↓
  mCachedViews содержит VH(pos=0)?
    ↓ ДА
  Return VH → БЕЗ вызова onBindViewHolder!
  (данные уже привязаны, position тот же)

Scroll DOWN дальше:
──────────────────────────────────────

  mCachedViews: [ VH(pos=0), VH(pos=1) ]  ← max size = 2

  Ещё scroll → VH(pos=2) нужно добавить
    ↓
  FIFO eviction: VH(pos=0) → RecycledViewPool
  mCachedViews: [ VH(pos=1), VH(pos=2) ]

КЛЮЧЕВОЕ преимущество:
  • Scroll up-down в пределах кэша → 0 bind calls
  • Идеально для "осциллирующего" скролла
```

### Уровень 5: RecycledViewPool (type-specific pool)

```
RecycledViewPool — пул по viewType
════════════════════════════════════

Структура:
┌─────────────────────────────────────────────────────────────┐
│  SparseArray<ScrapData>                                     │
│  ├── viewType=0 → ScrapData                                 │
│  │   └── mScrapHeap: ArrayList<ViewHolder> (max=5)         │
│  │       [VH, VH, VH, ...]                                  │
│  ├── viewType=1 → ScrapData                                 │
│  │   └── mScrapHeap: ArrayList<ViewHolder> (max=5)         │
│  │       [VH, VH, ...]                                      │
│  └── ...                                                    │
└─────────────────────────────────────────────────────────────┘

При получении из pool:
──────────────────────
  getViewForPosition(pos=42, type=1)
    ↓
  pool.getRecycledView(viewType=1)
    ↓
  Возвращает ЛЮБОЙ ViewHolder с viewType=1
    ↓
  ОБЯЗАТЕЛЬНО: onBindViewHolder(vh, 42)
  (данные очищены, нужен полный bind)

При возврате в pool:
────────────────────
  ViewHolder ушёл за экран
    ↓
  mCachedViews полон? (> DEFAULT_CACHE_SIZE)
    ↓ ДА
  Вытеснение → pool.putRecycledView(vh)
    ↓
  vh.clearPayload()
  vh.mPosition = NO_POSITION
  vh → mScrapHeap (если < max)

DEFAULT_MAX_SCRAP = 5 per viewType
Настройка: pool.setMaxRecycledViews(viewType, max)
```

### Shared RecycledViewPool для nested RecyclerView

```kotlin
// Сценарий: вертикальный список с горизонтальными каруселями
// Без shared pool: каждая карусель создаёт ViewHolder с нуля

class MainAdapter(
    private val sharedPool: RecyclerView.RecycledViewPool
) : RecyclerView.Adapter<MainAdapter.CarouselViewHolder>() {

    // Создаём shared pool ОДИН РАЗ
    companion object {
        fun createSharedPool(): RecyclerView.RecycledViewPool {
            return RecyclerView.RecycledViewPool().apply {
                // Увеличиваем размер для card viewType
                setMaxRecycledViews(VIEW_TYPE_CARD, 20)
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CarouselViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_carousel, parent, false)
        return CarouselViewHolder(view, sharedPool)
    }

    class CarouselViewHolder(
        itemView: View,
        private val sharedPool: RecyclerView.RecycledViewPool
    ) : RecyclerView.ViewHolder(itemView) {

        private val innerRecyclerView: RecyclerView =
            itemView.findViewById(R.id.inner_recycler)

        init {
            // КЛЮЧЕВОЕ: все inner RecyclerView используют ОДИН pool
            innerRecyclerView.setRecycledViewPool(sharedPool)

            // Настройка LayoutManager
            innerRecyclerView.layoutManager = LinearLayoutManager(
                itemView.context,
                LinearLayoutManager.HORIZONTAL,
                false
            ).apply {
                // Prefetch для вложенных списков
                initialPrefetchItemCount = 4
            }

            // Фиксированный размер (оптимизация)
            innerRecyclerView.setHasFixedSize(true)
        }

        fun bind(items: List<CardItem>) {
            (innerRecyclerView.adapter as? CardAdapter)?.submitList(items)
                ?: run {
                    innerRecyclerView.adapter = CardAdapter().apply { submitList(items) }
                }
        }
    }
}

// Использование:
val sharedPool = MainAdapter.createSharedPool()
val mainAdapter = MainAdapter(sharedPool)
mainRecyclerView.adapter = mainAdapter
// Все горизонтальные карусели делят ViewHolder-ы!
```

### Сводная таблица уровней кэша

| Уровень | Структура | Размер | Rebind? | Match по | Когда используется |
|---------|-----------|--------|---------|----------|-------------------|
| **Scrap (attached)** | ArrayList | Без лимита | Нет | Position | Layout pass |
| **Scrap (changed)** | ArrayList | Без лимита | Да | Position | Item change animation |
| **mCachedViews** | ArrayList | 2 | Нет | Position + id | Scroll, back-forth |
| **ViewCacheExtension** | Custom | Custom | Custom | Custom | Очень редко |
| **RecycledViewPool** | SparseArray | 5/type | Да | viewType | Нет в Cache |
| **Create new** | — | — | Да | — | Ничего не найдено |

---

## LayoutManager — позиционирование элементов

### Встроенные LayoutManager

```
LinearLayoutManager          GridLayoutManager         StaggeredGridLayoutManager
═══════════════════          ═══════════════════       ═══════════════════════════

Vertical:                    spanCount=2:              spanCount=2:
┌─────────────────┐          ┌────────┬────────┐       ┌────────┬────────┐
│     Item 0      │          │ Item 0 │ Item 1 │       │ Item 0 │ Item 1 │
├─────────────────┤          ├────────┼────────┤       │        ├────────┤
│     Item 1      │          │ Item 2 │ Item 3 │       ├────────┤ Item 2 │
├─────────────────┤          ├────────┼────────┤       │ Item 3 │        │
│     Item 2      │          │ Item 4 │ Item 5 │       │        ├────────┤
├─────────────────┤          └────────┴────────┘       ├────────┤ Item 4 │
│     Item 3      │                                    │ Item 5 │        │
└─────────────────┘                                    └────────┴────────┘

Horizontal:                  spanCount=3:
┌─────┬─────┬─────┬─────┐    ┌─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │    │  0  │  1  │  2  │
└─────┴─────┴─────┴─────┘    ├─────┼─────┼─────┤
                             │  3  │  4  │  5  │
                             └─────┴─────┴─────┘

reverseLayout=true:          SpanSizeLookup (custom spans):
┌─────────────────┐          ┌─────────────────┐
│     Item 3      │          │     Item 0      │ ← span=2
├─────────────────┤          ├────────┬────────┤
│     Item 2      │          │ Item 1 │ Item 2 │ ← span=1 each
├─────────────────┤          ├────────┴────────┤
│     Item 1      │          │     Item 3      │ ← span=2
├─────────────────┤          └─────────────────┘
│     Item 0      │
└─────────────────┘
```

### Ответственности LayoutManager

```kotlin
abstract class LayoutManager {

    // ═══ Layout ═══

    // Главный метод — расположить все видимые элементы
    abstract fun onLayoutChildren(recycler: Recycler, state: State)

    // Параметры по умолчанию для child views
    abstract fun generateDefaultLayoutParams(): RecyclerView.LayoutParams

    // ═══ Scroll ═══

    // Можно ли скроллить?
    open fun canScrollVertically(): Boolean = false
    open fun canScrollHorizontally(): Boolean = false

    // Обработать скролл, вернуть consumed pixels
    open fun scrollVerticallyBy(dy: Int, recycler: Recycler, state: State): Int = 0
    open fun scrollHorizontallyBy(dx: Int, recycler: Recycler, state: State): Int = 0

    // ═══ Focus & Navigation ═══

    // Найти View по позиции
    open fun findViewByPosition(position: Int): View?

    // Smooth scroll к позиции
    open fun smoothScrollToPosition(rv: RecyclerView, state: State, position: Int)

    // ═══ Prefetch (GapWorker) ═══

    // Позиции для предзагрузки при скролле
    open fun collectAdjacentPrefetchPositions(
        dx: Int, dy: Int, state: State, layoutPrefetchRegistry: LayoutPrefetchRegistry
    )

    // Позиции для предзагрузки при initial layout (nested RV)
    open fun collectInitialPrefetchPositions(
        adapterItemCount: Int, layoutPrefetchRegistry: LayoutPrefetchRegistry
    )

    // ═══ State ═══

    // Сохранить/восстановить scroll position
    open fun onSaveInstanceState(): Parcelable?
    open fun onRestoreInstanceState(state: Parcelable)
}
```

### LinearLayoutManager.fill() — алгоритм заполнения

```
fill(recycler, layoutState, state, stopOnFocusable):
════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────┐
  │                                                     │
  │  remainingSpace = layoutState.mAvailable            │
  │  (сколько пикселей нужно заполнить)                 │
  │                                                     │
  │  while (remainingSpace > 0 && hasMore(layoutState)) │
  │  │                                                  │
  │  │  // 1. Получить ViewHolder из Recycler           │
  │  │  view = layoutState.next(recycler)               │
  │  │     ↓                                            │
  │  │  recycler.getViewForPosition(currentPosition)    │
  │  │     ↓                                            │
  │  │  [Cache lookup: scrap → cache → pool → create]   │
  │  │                                                  │
  │  │  // 2. Добавить view в RecyclerView              │
  │  │  if (layoutState.mScrapList == null) {           │
  │  │      addView(view)  // или addView(view, 0)      │
  │  │  }                                               │
  │  │                                                  │
  │  │  // 3. Измерить                                  │
  │  │  measureChildWithMargins(view, 0, 0)             │
  │  │                                                  │
  │  │  // 4. Расположить                               │
  │  │  layoutDecoratedWithMargins(view, l, t, r, b)    │
  │  │                                                  │
  │  │  // 5. Обновить consumed space                   │
  │  │  consumed = layoutState.mLayoutDirection *       │
  │  │             mOrientationHelper.getDecoratedMeas..│
  │  │  remainingSpace -= consumed                      │
  │  │                                                  │
  │  │  // 6. Next position                             │
  │  │  layoutState.mCurrentPosition += itemDirection   │
  │  │                                                  │
  │  └─────────────────────────────────────────────────-┘
  │                                                     │
  │  return totalConsumed                               │
  └─────────────────────────────────────────────────────┘
```

### GridLayoutManager SpanSizeLookup

```kotlin
// Custom span sizes
val gridLayoutManager = GridLayoutManager(context, 3).apply {
    spanSizeLookup = object : GridLayoutManager.SpanSizeLookup() {
        override fun getSpanSize(position: Int): Int {
            return when (adapter.getItemViewType(position)) {
                VIEW_TYPE_HEADER -> 3  // Full width
                VIEW_TYPE_LARGE -> 2   // 2/3 width
                VIEW_TYPE_NORMAL -> 1  // 1/3 width
                else -> 1
            }
        }
    }

    // Кэширование span sizes (оптимизация)
    spanSizeLookup.isSpanIndexCacheEnabled = true
}
```

---

## DiffUtil — алгоритм Eugene Myers

### Проблема: notifyDataSetChanged()

```kotlin
// ❌ АНТИПАТТЕРН
fun updateData(newList: List<Item>) {
    items = newList
    notifyDataSetChanged()
}

// Что происходит:
// 1. ВСЕ ViewHolder помечаются INVALID
// 2. ВСЕ ViewHolder требуют rebind
// 3. НЕТ анимаций (RecyclerView не знает что изменилось)
// 4. O(N) rebind даже если изменился 1 элемент
```

### Алгоритм Eugene Myers (1986)

```
Задача: найти минимальный edit script для преобразования Old → New

Old: [A, B, C, D]     New: [A, C, D, E]

Edit Graph:
────────────
  Координаты: X = позиция в Old, Y = позиция в New
  Diagonal = совпадение (не требует операции)
  Horizontal → = удаление из Old
  Vertical ↓ = вставка в New

        Old
      A   B   C   D
    ┌───┬───┬───┬───┐
  A │ ╲ │   │   │   │   ╲ = diagonal (A=A)
    ├───┼───┼───┼───┤
N C │   │   │ ╲ │   │   ╲ = diagonal (C=C)
e   ├───┼───┼───┼───┤
w D │   │   │   │ ╲ │   ╲ = diagonal (D=D)
    ├───┼───┼───┼───┤
  E │   │   │   │   │   Нет диагонали (E не в Old)
    └───┴───┴───┴───┘

Кратчайший путь от (0,0) до (4,4):
  Start(0,0) → A diagonal(1,1) → B delete(2,1) →
  → C diagonal(3,2) → D diagonal(4,3) → E insert(4,4)

Edit script:
  • delete(1)  — удалить B
  • insert(3, E) — вставить E на позицию 3

Сложность:
  • Время: O(N + D²) где N = |Old| + |New|, D = размер diff
  • Память: O(N)
  • Best case (идентичные списки): O(N)
  • Worst case (полностью разные): O(N²)
```

### DiffUtil.Callback

```kotlin
class ItemDiffCallback(
    private val oldList: List<Item>,
    private val newList: List<Item>
) : DiffUtil.Callback() {

    // Размеры списков
    override fun getOldListSize(): Int = oldList.size
    override fun getNewListSize(): Int = newList.size

    // Это ТОТ ЖЕ элемент? (по идентификатору)
    // Определяет: это update существующего или add/remove
    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
        return oldList[oldPos].id == newList[newPos].id
    }

    // Содержимое ОДИНАКОВОЕ? (все поля)
    // Если false → вызовется onBindViewHolder
    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        return oldList[oldPos] == newList[newPos]
    }

    // Что именно изменилось? (для partial bind)
    // Возвращает payload → onBindViewHolder(holder, pos, payloads)
    override fun getChangePayload(oldPos: Int, newPos: Int): Any? {
        val old = oldList[oldPos]
        val new = newList[newPos]

        return buildList {
            if (old.title != new.title) add(Payload.TITLE)
            if (old.subtitle != new.subtitle) add(Payload.SUBTITLE)
            if (old.imageUrl != new.imageUrl) add(Payload.IMAGE)
        }.ifEmpty { null }
    }

    enum class Payload { TITLE, SUBTITLE, IMAGE }
}

// Использование (НА BACKGROUND THREAD!)
fun updateItems(newList: List<Item>) {
    val diffResult = DiffUtil.calculateDiff(
        ItemDiffCallback(currentList, newList),
        true // detectMoves — O(N²) дополнительно, но находит перемещения
    )

    currentList = newList

    // dispatchUpdatesTo ТОЛЬКО на main thread
    diffResult.dispatchUpdatesTo(adapter)
}
```

### ListAdapter — автоматический background diff

```kotlin
class ItemAdapter : ListAdapter<Item, ItemAdapter.ViewHolder>(ItemDiffCallback()) {

    // DiffUtil.ItemCallback — упрощённый callback для ListAdapter
    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        // areItemsTheSame — по ID
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem.id == newItem.id

        // areContentsTheSame — по содержимому
        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean =
            oldItem == newItem

        // getChangePayload (опционально)
        override fun getChangePayload(oldItem: Item, newItem: Item): Any? {
            return if (oldItem.title != newItem.title) "title" else null
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(
            LayoutInflater.from(parent.context)
                .inflate(R.layout.item, parent, false)
        )
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // Partial bind с payload
    override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: List<Any>) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            // Только title изменился
            if (payloads.contains("title")) {
                holder.updateTitle(getItem(position).title)
            }
        }
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val titleText: TextView = view.findViewById(R.id.title)

        fun bind(item: Item) {
            titleText.text = item.title
        }

        fun updateTitle(title: String) {
            titleText.text = title
        }
    }
}

// Использование — ПРОСТО
adapter.submitList(newList)
// AsyncListDiffer автоматически:
// 1. Запускает calculateDiff на background thread
// 2. dispatchUpdatesTo на main thread
// 3. Анимации работают!
```

### ВАЖНО: submitList требует НОВЫЙ список

```kotlin
// ❌ НЕ СРАБОТАЕТ
val list = mutableListOf(item1, item2, item3)
adapter.submitList(list)
list.add(item4)  // Мутируем тот же список
adapter.submitList(list)  // list === previousList → no-op!

// ✅ ПРАВИЛЬНО
adapter.submitList(list.toList())  // Создаём копию

// Или используйте immutable collections:
val list = listOf(item1, item2, item3)
adapter.submitList(list)
adapter.submitList(list + item4)  // Новый список
```

### Бенчмарки DiffUtil

| Элементов | Изменений | Время (calculateDiff) | Примечание |
|-----------|-----------|----------------------|------------|
| 100 | 10 | ~0.4 мс | Мгновенно |
| 500 | 50 | ~5 мс | OK |
| 1,000 | 200 | ~27 мс | Заметно |
| 5,000 | 500 | ~100 мс | Background обязателен |
| 10,000 | 1000 | ~250 мс | Серьёзная задержка |

**Вывод:** Для >100 элементов всегда используйте ListAdapter (background diff) или вручную вызывайте calculateDiff на background thread.

---

## GapWorker и Prefetch — предзагрузка

### Проблема: inflation во время scroll

```
Без prefetch (jank):
────────────────────

Frame N (16.6ms budget @ 60fps)
├── Input (1ms)
├── Animation (2ms)
├── Layout + fill (8ms)
│   └── onCreateViewHolder (5ms) ← ДОРОГО!
│       └── inflate XML
├── Draw (3ms)
└── Idle (1.6ms) ← НЕ ИСПОЛЬЗУЕТСЯ

Total: 19ms → JANK (превышен frame budget)


С prefetch (smooth):
────────────────────

Frame N (16.6ms budget)
├── Input (1ms)
├── Animation (2ms)
├── Layout + fill (3ms)
│   └── ViewHolder уже готов в кэше!
├── Draw (3ms)
└── Idle (7.6ms)
    └── GapWorker: onCreateViewHolder для СЛЕДУЮЩЕГО элемента

Total: 9ms → OK, prefetch в idle time
```

### Как работает GapWorker

```
GapWorker (package-private class in RecyclerView)
═════════════════════════════════════════════════

1. RecyclerView регистрируется в GapWorker при onAttachedToWindow()

2. При скролле:
   ┌─────────────────────────────────────────────────────────────┐
   │  onScrolled() / scrollBy()                                  │
   │      ↓                                                      │
   │  mGapWorker.postFromTraversal(this, prefetchDx, prefetchDy) │
   │      ↓                                                      │
   │  Записать: какой RecyclerView, направление скролла          │
   └─────────────────────────────────────────────────────────────┘

3. GapWorker использует Choreographer:
   ┌─────────────────────────────────────────────────────────────┐
   │  mChoreographer.postFrameCallback(this /* GapWorker */)     │
   │      ↓                                                      │
   │  doFrame(frameTimeNanos)                                    │
   │      ↓                                                      │
   │  prefetch(deadlineNanos)                                    │
   │      ↓                                                      │
   │  flushTasksWithDeadline(deadlineNanos)                      │
   └─────────────────────────────────────────────────────────────┘

4. Prefetch с deadline:
   ┌─────────────────────────────────────────────────────────────┐
   │  for (task in mTasks) {                                     │
   │      if (System.nanoTime() > deadlineNanos) break           │
   │      // Время вышло — не блокируем следующий frame          │
   │                                                             │
   │      val vh = recycler.tryGetViewHolderForPositionByDeadline│
   │                  (position, dryRun=false, deadlineNanos)    │
   │      // Создаёт ViewHolder если нужно, bind                 │
   │      // ViewHolder → mCachedViews (готов к использованию)   │
   │  }                                                          │
   └─────────────────────────────────────────────────────────────┘

5. LayoutManager предоставляет позиции для prefetch:
   ┌─────────────────────────────────────────────────────────────┐
   │  LinearLayoutManager.collectAdjacentPrefetchPositions()     │
   │      ↓                                                      │
   │  // Scroll DOWN → prefetch следующий элемент               │
   │  layoutPrefetchRegistry.addPosition(lastVisiblePos + 1, 0)  │
   │                                                             │
   │  // Scroll UP → prefetch предыдущий элемент                │
   │  layoutPrefetchRegistry.addPosition(firstVisiblePos - 1, 0) │
   └─────────────────────────────────────────────────────────────┘
```

### Nested RecyclerView prefetch

```kotlin
// Для вложенных RecyclerView нужно настроить initialPrefetchItemCount

// Outer (vertical) RecyclerView adapter:
class OuterAdapter : RecyclerView.Adapter<OuterViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OuterViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_row, parent, false)

        // Настройка inner RecyclerView
        val innerRV = view.findViewById<RecyclerView>(R.id.inner_recycler)
        innerRV.layoutManager = LinearLayoutManager(
            parent.context,
            LinearLayoutManager.HORIZONTAL,
            false
        ).apply {
            // КЛЮЧЕВОЕ: сколько элементов prefetch для inner
            // По умолчанию = 2, увеличиваем для карусели
            initialPrefetchItemCount = 4
        }

        return OuterViewHolder(view, innerRV)
    }
}

// LayoutManager.collectInitialPrefetchPositions():
// Вызывается GapWorker при первом layout вложенного RecyclerView
// Возвращает позиции для prefetch (0, 1, 2, 3 для initialPrefetchItemCount=4)
```

---

## ItemDecoration — рисование декораций

### Три callback метода

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DRAW ORDER                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. onDraw(canvas, parent, state)                                        │
│     └── Рисует ПОД child views (background)                              │
│         Примеры: background colors, zebra stripes                        │
│                                                                          │
│  2. [Child views draw themselves]                                        │
│                                                                          │
│  3. onDrawOver(canvas, parent, state)                                    │
│     └── Рисует ПОВЕРХ child views (foreground)                          │
│         Примеры: sticky headers, overlays                                │
│                                                                          │
│  getItemOffsets(outRect, view, parent, state)                            │
│     └── Добавляет пространство (как padding/margin)                      │
│         outRect.left/top/right/bottom = offset в pixels                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Divider decoration

```kotlin
class DividerDecoration(
    private val dividerHeight: Int,
    @ColorInt private val dividerColor: Int
) : RecyclerView.ItemDecoration() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = dividerColor
        style = Paint.Style.FILL
    }

    // Рисуем divider ПОД элементами (в промежутках)
    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft
        val right = parent.width - parent.paddingRight

        for (i in 0 until parent.childCount - 1) { // Не после последнего!
            val child = parent.getChildAt(i)
            val params = child.layoutParams as RecyclerView.LayoutParams

            val top = child.bottom + params.bottomMargin
            val bottom = top + dividerHeight

            canvas.drawRect(
                left.toFloat(),
                top.toFloat(),
                right.toFloat(),
                bottom.toFloat(),
                paint
            )
        }
    }

    // Резервируем место под divider
    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val itemCount = state.itemCount

        // Не добавлять offset после последнего элемента
        if (position < itemCount - 1) {
            outRect.bottom = dividerHeight
        }
    }
}

// Использование:
recyclerView.addItemDecoration(
    DividerDecoration(
        dividerHeight = 1.dpToPx(),
        dividerColor = Color.LTGRAY
    )
)
```

### Sticky header decoration

```kotlin
class StickyHeaderDecoration(
    private val adapter: StickyHeaderAdapter
) : RecyclerView.ItemDecoration() {

    interface StickyHeaderAdapter {
        fun getHeaderId(position: Int): Long
        fun onCreateHeaderViewHolder(parent: ViewGroup): RecyclerView.ViewHolder
        fun onBindHeaderViewHolder(holder: RecyclerView.ViewHolder, position: Int)
    }

    private var cachedHeader: View? = null
    private var cachedHeaderPosition = -1

    // Рисуем sticky header ПОВЕРХ контента
    override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val topChild = parent.getChildAt(0) ?: return
        val topPosition = parent.getChildAdapterPosition(topChild)
        if (topPosition == RecyclerView.NO_POSITION) return

        val currentHeaderId = adapter.getHeaderId(topPosition)
        val header = getOrCreateHeader(parent, topPosition)

        // Вычислить позицию header
        val nextHeader = findNextHeaderView(parent, topPosition)
        val headerOffset = if (nextHeader != null) {
            minOf(0, nextHeader.top - header.height)
        } else {
            0
        }

        // Рисуем header
        canvas.save()
        canvas.translate(0f, headerOffset.toFloat())
        header.draw(canvas)
        canvas.restore()
    }

    private fun getOrCreateHeader(parent: RecyclerView, position: Int): View {
        val headerId = adapter.getHeaderId(position)

        if (cachedHeader != null && cachedHeaderPosition == headerId.toInt()) {
            return cachedHeader!!
        }

        val holder = adapter.onCreateHeaderViewHolder(parent)
        adapter.onBindHeaderViewHolder(holder, position)

        val header = holder.itemView

        // Measure & layout header
        val widthSpec = View.MeasureSpec.makeMeasureSpec(
            parent.width, View.MeasureSpec.EXACTLY
        )
        val heightSpec = View.MeasureSpec.makeMeasureSpec(
            parent.height, View.MeasureSpec.UNSPECIFIED
        )
        header.measure(widthSpec, heightSpec)
        header.layout(0, 0, header.measuredWidth, header.measuredHeight)

        cachedHeader = header
        cachedHeaderPosition = headerId.toInt()

        return header
    }

    private fun findNextHeaderView(parent: RecyclerView, currentPosition: Int): View? {
        val currentHeaderId = adapter.getHeaderId(currentPosition)

        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)
            if (position != RecyclerView.NO_POSITION &&
                adapter.getHeaderId(position) != currentHeaderId) {
                return child
            }
        }
        return null
    }
}
```

---

## ItemAnimator — анимация элементов

### DefaultItemAnimator

```
notify* call              ItemAnimator method       Animation
───────────────────────────────────────────────────────────────

notifyItemInserted()  →   animateAdd()          →   fade in (alpha 0→1)
notifyItemRemoved()   →   animateRemove()       →   fade out (alpha 1→0)
notifyItemMoved()     →   animateMove()         →   translate
notifyItemChanged()   →   animateChange()       →   cross-fade

Timing:
  • Add/Remove: 120ms
  • Move: 250ms
  • Change: 120ms
```

### Predictive animations (pre-layout / post-layout)

```
notifyItemRemoved(position=2):
══════════════════════════════

PRE-LAYOUT (что было ДО удаления):
┌─────────────────┐
│     Item 0      │  visible
├─────────────────┤
│     Item 1      │  visible
├─────────────────┤
│     Item 2      │  visible (будет удалён)
├─────────────────┤
│     Item 3      │  visible
├─────────────────┤
│     Item 4      │  OFF SCREEN (но нужен для анимации!)
└─────────────────┘

POST-LAYOUT (что будет ПОСЛЕ удаления):
┌─────────────────┐
│     Item 0      │  same position
├─────────────────┤
│     Item 1      │  same position
├─────────────────┤
│     Item 3      │  moved up (was Item 2 position)
├─────────────────┤
│     Item 4      │  moved up + appeared!
└─────────────────┘

Анимации:
  • Item 2: animateRemove() — fade out
  • Item 3: animateMove() — translate up
  • Item 4: animateMove() + animateAppear() — translate up + fade in

supportsPredictiveItemAnimations() = true
  → Включает pre-layout для off-screen items
  → Более плавные анимации
```

### Custom ItemAnimator

```kotlin
class FadeSlideItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView

        // Начальное состояние
        view.alpha = 0f
        view.translationY = view.height.toFloat()

        // Анимация
        view.animate()
            .alpha(1f)
            .translationY(0f)
            .setDuration(addDuration)
            .setInterpolator(DecelerateInterpolator())
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    dispatchAddFinished(holder)
                }
                override fun onAnimationCancel(animation: Animator) {
                    clearAnimatedValues(view)
                }
            })
            .start()

        return true // Анимация запущена
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView

        view.animate()
            .alpha(0f)
            .translationX(-view.width.toFloat())
            .setDuration(removeDuration)
            .setInterpolator(AccelerateInterpolator())
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    clearAnimatedValues(view)
                    dispatchRemoveFinished(holder)
                }
            })
            .start()

        return true
    }

    private fun clearAnimatedValues(view: View) {
        view.alpha = 1f
        view.translationX = 0f
        view.translationY = 0f
    }
}

// Использование:
recyclerView.itemAnimator = FadeSlideItemAnimator().apply {
    addDuration = 300
    removeDuration = 300
}
```

---

## SnapHelper — выравнивание элементов

### LinearSnapHelper vs PagerSnapHelper

```
LinearSnapHelper:                    PagerSnapHelper:
═════════════════                    ════════════════

Scroll anywhere:                     Scroll one page at a time:

Before snap:                         Before snap:
┌──────────────────────┐             ┌──────────────────────┐
│  ┌───┐   ┌───┐      │             │  ┌────────────┐      │
│  │ A │   │ B │...   │             │  │     A      │  B   │
│  └───┘   └───┘      │             │  └────────────┘      │
└──────────────────────┘             └──────────────────────┘

After snap (ближайший к центру):     After snap (ближайший к краю):
┌──────────────────────┐             ┌──────────────────────┐
│     ┌───┐   ┌───┐   │             │┌────────────────────┐│
│     │ B │   │ C │...│             ││         B          ││
│     └───┘   └───┘   │             │└────────────────────┘│
└──────────────────────┘             └──────────────────────┘

Использование:                       Использование:
- Карусели с несколькими             - Галереи (одно фото на экран)
  видимыми элементами                - Onboarding (один шаг на экран)
- Подбор к ближайшему центру         - ViewPager-like поведение
```

### Использование SnapHelper

```kotlin
// LinearSnapHelper — snap к ближайшему центру
LinearSnapHelper().attachToRecyclerView(recyclerView)

// PagerSnapHelper — snap к краю (одна страница)
PagerSnapHelper().attachToRecyclerView(recyclerView)

// Получить snap position
val layoutManager = recyclerView.layoutManager
val snapHelper = LinearSnapHelper()
val snapView = snapHelper.findSnapView(layoutManager)
val snapPosition = layoutManager?.getPosition(snapView ?: return)

// Smooth scroll к snap
snapHelper.findTargetSnapPosition(layoutManager, velocityX, velocityY)
```

---

## ItemTouchHelper — Drag & Drop, Swipe

### Drag & Drop + Swipe to Dismiss

```kotlin
val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
    // dragDirs: направления drag
    ItemTouchHelper.UP or ItemTouchHelper.DOWN,
    // swipeDirs: направления swipe
    ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    // Drag: переместить элемент
    override fun onMove(
        recyclerView: RecyclerView,
        viewHolder: RecyclerView.ViewHolder,
        target: RecyclerView.ViewHolder
    ): Boolean {
        val fromPos = viewHolder.adapterPosition
        val toPos = target.adapterPosition

        // Уведомить adapter о перемещении
        Collections.swap(items, fromPos, toPos)
        adapter.notifyItemMoved(fromPos, toPos)

        return true
    }

    // Swipe: удалить элемент
    override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
        val position = viewHolder.adapterPosition

        when (direction) {
            ItemTouchHelper.LEFT -> {
                // Удалить
                items.removeAt(position)
                adapter.notifyItemRemoved(position)
            }
            ItemTouchHelper.RIGHT -> {
                // Archive или другое действие
                archiveItem(items[position])
                items.removeAt(position)
                adapter.notifyItemRemoved(position)
            }
        }
    }

    // Визуальная обратная связь
    override fun onChildDraw(
        c: Canvas,
        recyclerView: RecyclerView,
        viewHolder: RecyclerView.ViewHolder,
        dX: Float, dY: Float,
        actionState: Int,
        isCurrentlyActive: Boolean
    ) {
        if (actionState == ItemTouchHelper.ACTION_STATE_SWIPE) {
            // Fade out при swipe
            val alpha = 1 - abs(dX) / viewHolder.itemView.width
            viewHolder.itemView.alpha = alpha
        }

        super.onChildDraw(c, recyclerView, viewHolder, dX, dY, actionState, isCurrentlyActive)
    }

    // Сброс после анимации
    override fun clearView(
        recyclerView: RecyclerView,
        viewHolder: RecyclerView.ViewHolder
    ) {
        super.clearView(recyclerView, viewHolder)
        viewHolder.itemView.alpha = 1f
    }
})

itemTouchHelper.attachToRecyclerView(recyclerView)

// Programmatic drag start (например, по long press на handle)
itemTouchHelper.startDrag(viewHolder)
```

---

## ConcatAdapter — объединение адаптеров

### Сценарий: Header + Items + Footer

```kotlin
// До ConcatAdapter: один Adapter с viewTypes
// Проблема: сложный код, трудно переиспользовать

// С ConcatAdapter: три отдельных Adapter
class HeaderAdapter : RecyclerView.Adapter<HeaderViewHolder>() {
    override fun getItemCount() = 1
    // ...
}

class ItemsAdapter : ListAdapter<Item, ItemViewHolder>(DiffCallback()) {
    // ... основной контент
}

class FooterAdapter : RecyclerView.Adapter<FooterViewHolder>() {
    var isLoading: Boolean = false
        set(value) {
            field = value
            notifyDataSetChanged()
        }
    override fun getItemCount() = if (isLoading) 1 else 0
    // ...
}

// Объединение
val concatAdapter = ConcatAdapter(
    headerAdapter,
    itemsAdapter,
    footerAdapter
)
recyclerView.adapter = concatAdapter

// Изолированные позиции
// Header: position 0
// Items: positions 1..N
// Footer: position N+1 (если isLoading)

// Конфигурация
val config = ConcatAdapter.Config.Builder()
    .setIsolateViewTypes(true)  // viewTypes не пересекаются между адаптерами
    .setStableIdMode(ConcatAdapter.Config.StableIdMode.NO_STABLE_IDS)
    .build()

val concatAdapter = ConcatAdapter(config, headerAdapter, itemsAdapter, footerAdapter)
```

---

## State Restoration — восстановление scroll position

### StateRestorationPolicy

```kotlin
class MyAdapter : RecyclerView.Adapter<MyViewHolder>() {

    init {
        // Когда восстанавливать scroll position?
        stateRestorationPolicy = StateRestorationPolicy.PREVENT_WHEN_EMPTY
    }
}

enum class StateRestorationPolicy {
    // Восстановить сразу (может быть проблема если данные ещё не загружены)
    ALLOW,

    // Восстановить только когда adapter не пустой
    // Рекомендуется для async data loading
    PREVENT_WHEN_EMPTY,

    // Не восстанавливать автоматически
    PREVENT
}

// Ручное восстановление
val savedPosition = savedInstanceState?.getInt("scroll_position") ?: 0
recyclerView.scrollToPosition(savedPosition)

// Сохранение
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    val layoutManager = recyclerView.layoutManager as? LinearLayoutManager
    val position = layoutManager?.findFirstVisibleItemPosition() ?: 0
    outState.putInt("scroll_position", position)
}
```

---

## Оптимизация производительности

### Чеклист оптимизации

```kotlin
// ══════════════════════════════════════════════════════════════
// 1. setHasFixedSize — если размер RV не зависит от содержимого
// ══════════════════════════════════════════════════════════════
recyclerView.setHasFixedSize(true)
// Пропускает requestLayout() при изменении данных

// ══════════════════════════════════════════════════════════════
// 2. setHasStableIds — для эффективных анимаций
// ══════════════════════════════════════════════════════════════
adapter.setHasStableIds(true)
// + override getItemId(position): Long = items[position].id

// ══════════════════════════════════════════════════════════════
// 3. Увеличить cache для частого back-forth scroll
// ══════════════════════════════════════════════════════════════
recyclerView.setItemViewCacheSize(10)  // по умолчанию 2

// ══════════════════════════════════════════════════════════════
// 4. Shared pool для nested RecyclerView
// ══════════════════════════════════════════════════════════════
val sharedPool = RecyclerView.RecycledViewPool()
sharedPool.setMaxRecycledViews(VIEW_TYPE_CARD, 20)
recyclerView.setRecycledViewPool(sharedPool)

// ══════════════════════════════════════════════════════════════
// 5. RecyclerListener для очистки ресурсов
// ══════════════════════════════════════════════════════════════
recyclerView.setRecyclerListener { holder ->
    (holder as? ImageViewHolder)?.clearImage()
}

// ══════════════════════════════════════════════════════════════
// 6. Prefetch для nested RecyclerView
// ══════════════════════════════════════════════════════════════
(innerRecyclerView.layoutManager as LinearLayoutManager)
    .initialPrefetchItemCount = 4

// ══════════════════════════════════════════════════════════════
// 7. Плоские layouts (ConstraintLayout вместо вложенных)
// ══════════════════════════════════════════════════════════════
// ConstraintLayout с ~10 views быстрее чем 3 уровня вложенности

// ══════════════════════════════════════════════════════════════
// 8. ListAdapter для автоматического background diff
// ══════════════════════════════════════════════════════════════
class MyAdapter : ListAdapter<Item, VH>(DiffCallback()) {
    // submitList() автоматически на background thread
}

// ══════════════════════════════════════════════════════════════
// 9. Partial updates с payload
// ══════════════════════════════════════════════════════════════
override fun onBindViewHolder(holder: VH, position: Int, payloads: List<Any>) {
    if (payloads.isEmpty()) {
        onBindViewHolder(holder, position)
    } else {
        // Обновить только изменившееся
        holder.updatePartial(payloads)
    }
}
```

### Антипаттерны

| Антипаттерн | Проблема | Решение |
|-------------|----------|---------|
| RecyclerView в ScrollView | Все элементы создаются сразу, recycling отключён | Один RecyclerView с разными viewTypes |
| `notifyDataSetChanged()` | Убивает анимации, rebind ВСЕГО | DiffUtil / ListAdapter |
| Глубокая иерархия item layout | Медленный measure/layout | ConstraintLayout (плоская) |
| Тяжёлая работа в onBindViewHolder | Блокирует UI thread | Async: Glide/Coil, корутины |
| `wrap_content` высота RV | Лишний measure pass | `match_parent` / фиксированная |
| Не используется setHasFixedSize | Лишний requestLayout | `setHasFixedSize(true)` |
| Создание объектов в onBind | GC pressure | Переиспользуйте объекты |
| Не отменяются async операции | Утечки, wrong images | `onViewRecycled()` cleanup |

---

## RecyclerView vs Compose LazyColumn

| Аспект | RecyclerView | LazyColumn |
|--------|-------------|------------|
| **Парадигма** | Императивная | Декларативная |
| **Recycling** | Explicit (ViewHolder pattern) | Automatic (subcomposition) |
| **Кэширование** | 4-уровневый Recycler | SubcomposeLayout (менее эффективен) |
| **Shared pool** | RecycledViewPool ✅ | Нет ❌ |
| **DiffUtil** | Manual / ListAdapter | Automatic с `key` |
| **Animations** | ItemAnimator, complex | `animateItem()`, проще |
| **Decorations** | ItemDecoration | Spacer, Divider, modifier |
| **Drag & Drop** | ItemTouchHelper | LazyListReorderableState |
| **Snap** | SnapHelper | SnapFlingBehavior |
| **Nested perf** | Shared pool, prefetch | Проблематично |
| **Memory** | Контролируемая | Выше (compositions) |

### Когда что использовать

**RecyclerView:**
- Legacy codebase
- Сложные nested списки (shared pool критичен)
- Требуется ViewCacheExtension
- Кастомные сложные анимации
- Максимальная производительность

**LazyColumn:**
- Новые Compose проекты
- Простые списки
- Declarative UI важнее микро-оптимизаций
- Простые анимации

---

## Мифы и заблуждения

| # | Миф | Реальность |
|---|-----|-----------|
| 1 | "RecyclerView автоматически оптимизирует всё" | Нужна ручная оптимизация: DiffUtil, setHasFixedSize, flat layouts, shared pool |
| 2 | "DiffUtil можно вызвать на Main Thread" | `calculateDiff()` блокирует поток! Для >100 элементов — только background |
| 3 | "setHasFixedSize = фиксированный размер элементов" | Это про размер **самого RecyclerView**, не элементов |
| 4 | "notifyDataSetChanged() — нормально для небольших списков" | Убивает анимации, rebind ВСЕГО. Всегда используйте точные notify* |
| 5 | "ViewHolder создаётся для каждого элемента данных" | Создаётся только ~10-15 штук, остальные переиспользуются |
| 6 | "Больше кэш = лучше" | Больше памяти, diminishing returns. Default (2+5) оптимален |
| 7 | "LazyColumn полностью заменяет RecyclerView" | Нет shared pool — проблемы с nested списками |
| 8 | "RecycledViewPool shared по умолчанию" | Каждый RV имеет СВОЙ pool. Shared нужно создать явно |
| 9 | "submitList(sameList) обновит данные" | Сравнивает по ===. Нужен НОВЫЙ объект списка |
| 10 | "Scrap = кэш" | Scrap — ВРЕМЕННОЕ хранилище только во время layout pass |
| 11 | "setItemViewCacheSize(100) ускорит scroll" | Тратит память, prefetch важнее. 5-10 обычно достаточно |
| 12 | "Partial updates не дают значительного выигрыша" | Обновление одного TextView вместо всего item — до 10x быстрее |

---

## CS-фундамент

| Концепция | Как используется | Пример |
|-----------|-----------------|--------|
| **Object Pool** | RecycledViewPool: пул ViewHolder по viewType | 5 VH типа "card" ждут переиспользования |
| **Cache Hierarchy** | L1(Scrap) → L2(Cache) → L3(Pool) | Как L1/L2/L3 кэш CPU: ближе = быстрее |
| **Amortized O(1)** | Inflation O(N) один раз, bind O(1) много раз | Первый scroll дороже |
| **Diff Algorithm** | Eugene Myers O(N+D²) для edit script | Git diff — тот же алгоритм |
| **Producer-Consumer** | Adapter (producer) → Recycler → LayoutManager (consumer) | Разделение ответственности |
| **Flyweight** | ViewHolder — lightweight wrapper для View | 7 VH для 1000 элементов |
| **Observer** | AdapterDataObserver для notify* | notifyItemChanged → observer → update |
| **Template Method** | LayoutManager определяет алгоритм, subclass — детали | Linear vs Grid vs Staggered |
| **Decorator** | ItemDecoration декорирует items | Dividers, backgrounds |
| **Strategy** | ItemAnimator — стратегия анимации | Custom анимации для разных действий |

---

## Проверь себя

### Вопрос 1
**Q:** В каком порядке RecyclerView ищет ViewHolder? Какие уровни НЕ требуют rebind?

<details>
<summary>Ответ</summary>

Порядок: **mChangedScrap → mAttachedScrap → mCachedViews → ViewCacheExtension → RecycledViewPool → create**

**БЕЗ rebind:** mAttachedScrap, mCachedViews (хранят ViewHolder с привязкой к позиции)

**С rebind:** mChangedScrap (анимация), RecycledViewPool (только viewType, данные очищены)
</details>

### Вопрос 2
**Q:** Почему этот код не обновит список?
```kotlin
val list = mutableListOf(1, 2, 3)
adapter.submitList(list)
list.add(4)
adapter.submitList(list)
```

<details>
<summary>Ответ</summary>

`submitList()` сначала проверяет `newList === oldList` по ссылке. Если тот же объект — считает diff=0 (no-op).

**Решение:** передать НОВЫЙ список: `adapter.submitList(list.toList())`
</details>

### Вопрос 3
**Q:** У вас nested RecyclerView (вертикальный с горизонтальными). Как оптимизировать?

<details>
<summary>Ответ</summary>

1. **Shared pool:** `val sharedPool = RecycledViewPool()` → установить для всех inner RV
2. **Увеличить pool:** `sharedPool.setMaxRecycledViews(cardType, 20)`
3. **Prefetch:** `innerLayoutManager.initialPrefetchItemCount = 5`
4. **setHasFixedSize(true)** для inner RV
</details>

### Вопрос 4
**Q:** Что оптимизирует setHasFixedSize(true)?

<details>
<summary>Ответ</summary>

Говорит RecyclerView: "мой размер НЕ зависит от содержимого". При notify* пропускает requestLayout() родителя.

**НЕ использовать** когда RV имеет wrap_content и размер реально зависит от элементов.
</details>

### Вопрос 5
**Q:** Чем опасен calculateDiff() на main thread?

<details>
<summary>Ответ</summary>

Синхронная операция O(N+D²). Для 1000 элементов с 200 изменениями — ~27мс (почти 2 кадра).

**Решение:** ListAdapter (AsyncListDiffer) или ручной вызов на background thread.
</details>

---

## Связи

### Фундамент
- **[[android-view-rendering-pipeline]]** — RecyclerView участвует в measure/layout/draw; понимание нужно для оптимизации
- **[[android-ui-views]]** — ViewGroup основа; LayoutParams, measure specs

### Альтернативы
- **[[android-compose]]** — LazyColumn/LazyRow как декларативная альтернатива

### Производительность
- **[[android-performance-profiling]]** — Profiling scroll, systrace, GPU rendering

### Паттерны
- **[[android-custom-view-fundamentals]]** — Custom LayoutManager требует знания Custom View API

---

## Источники

| # | Источник | Тип | Описание |
|---|---------|-----|----------|
| 1 | [RecyclerView Docs](https://developer.android.com/develop/ui/views/layout/recyclerview) | Docs | Официальная документация |
| 2 | [AOSP: RecyclerView.java](https://cs.android.com/androidx/platform/frameworks/support/+/master:recyclerview/recyclerview/src/main/java/androidx/recyclerview/widget/RecyclerView.java) | AOSP | Исходный код (~13,000 строк) |
| 3 | [DiffUtil Docs](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil) | Docs | API с бенчмарками |
| 4 | [Anatomy of RecyclerView: Search for ViewHolder](https://android.jlelse.eu/anatomy-of-recyclerview-part-1-a-search-for-a-viewholder-404ba3453714) | Article | tryGetViewHolderForPositionByDeadline |
| 5 | [RecyclerView Caching](https://medium.com/@nicholasnielson/recyclerview-caching-9e7d6b27c0fe) | Article | 4 уровня кэша |
| 6 | [Eugene Myers Diff Algorithm](http://www.xmailserver.org/diff2.pdf) | Paper | Оригинальная статья 1986 |
| 7 | [RecyclerView Prefetch](https://medium.com/google-developers/recyclerview-prefetch-c2f269075710) | Article | GapWorker, Chris Craik |
| 8 | [ListAdapter Docs](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter) | Docs | AsyncListDiffer wrapper |
| 9 | [ConcatAdapter](https://developer.android.com/reference/androidx/recyclerview/widget/ConcatAdapter) | Docs | Merge adapters |
| 10 | [ItemTouchHelper](https://developer.android.com/reference/androidx/recyclerview/widget/ItemTouchHelper) | Docs | Drag & swipe |
| 11 | [RecyclerView Performance](https://developer.android.com/topic/performance/vitals/render) | Docs | Performance best practices |
| 12 | [Shared RecycledViewPool](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView.RecycledViewPool) | Docs | Nested RV optimization |

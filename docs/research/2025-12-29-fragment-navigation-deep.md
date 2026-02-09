---
title: "Research Report: Fragment Navigation Deep Dive"
created: 2025-12-29
modified: 2025-12-29
type: reference
status: draft
tags:
  - topic/android
  - topic/navigation
---

# Research Report: Fragment Navigation Deep Dive (Legacy)

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep (internals, lifecycle, best practices)

## Executive Summary

FragmentManager и FragmentTransaction — низкоуровневый API для навигации между Fragments до появления Navigation Component (2018). Back stack состоит из транзакций, не фрагментов. Четыре типа commit: `commit()` (async), `commitNow()` (sync), `commitAllowingStateLoss()` и `commitNowAllowingStateLoss()`. Fragment Result API заменил deprecated `setTargetFragment()`. Для nested fragments использовать `childFragmentManager`, не `parentFragmentManager`. Shared element transitions требуют API 21+.

---

## Key Findings

### 1. FragmentManager Internals

**Что такое back stack:**
```
Back stack = список FragmentTransaction, НЕ фрагментов

┌─────────────────────────────────────┐
│         FragmentManager             │
├─────────────────────────────────────┤
│  Back Stack:                        │
│  ┌───────────────────────────────┐  │
│  │ Transaction 3 (add Fragment C)│  │ ← top
│  ├───────────────────────────────┤  │
│  │ Transaction 2 (replace A→B)  │  │
│  ├───────────────────────────────┤  │
│  │ Transaction 1 (add Fragment A)│  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘

popBackStack() → reverse Transaction 3 → remove Fragment C
```

**Как работает addToBackStack:**
```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragmentB)
    .addToBackStack("fragmentB")  // Сохраняет транзакцию
    .commit()

// При popBackStack():
// 1. FragmentManager берёт top transaction
// 2. Выполняет обратную операцию (replace → remove B, add A)
// 3. Удаляет transaction из stack
```

**Два типа tags:**
| Tag | Назначение | Как использовать |
|-----|------------|-----------------|
| Fragment tag | Найти fragment по имени | `findFragmentByTag("myFragment")` |
| BackStack name | Найти transaction | `popBackStack("name", flags)` |

---

### 2. FragmentTransaction Operations

**Основные операции:**
| Операция | Описание | Lifecycle |
|----------|----------|-----------|
| `add()` | Добавляет fragment | onCreate → onStart → onResume |
| `remove()` | Удаляет fragment | onPause → onStop → onDestroy |
| `replace()` | = remove existing + add new | Комбинация |
| `show()` | Показывает скрытый fragment | Без lifecycle changes |
| `hide()` | Скрывает fragment | Без lifecycle changes |
| `attach()` | Переаттачивает detached | onCreateView → onStart → onResume |
| `detach()` | Detach view, сохраняет state | onPause → onStop → onDestroyView |

**show/hide vs attach/detach vs add/remove:**
```kotlin
// show/hide — быстро, view остаётся в памяти
// Используй для табов, быстрого переключения
fragmentManager.beginTransaction()
    .hide(fragmentA)
    .show(fragmentB)
    .commit()

// attach/detach — освобождает view, сохраняет state
// Используй для экономии памяти
fragmentManager.beginTransaction()
    .detach(fragmentA)  // onDestroyView(), state сохраняется
    .attach(fragmentA)  // onCreateView()
    .commit()

// add/remove — полный lifecycle
// Используй для одноразовых fragments
fragmentManager.beginTransaction()
    .remove(fragmentA)  // onDestroy()
    .commit()
```

---

### 3. Commit Variants

**Четыре типа commit:**

| Метод | Async/Sync | Back Stack | State Loss |
|-------|-----------|------------|------------|
| `commit()` | Async | ✅ | Throws Exception |
| `commitAllowingStateLoss()` | Async | ✅ | Ignores |
| `commitNow()` | Sync | ❌ | Throws Exception |
| `commitNowAllowingStateLoss()` | Sync | ❌ | Ignores |

**Когда какой использовать:**
```kotlin
// ✅ commit() — большинство случаев
// Async, можно добавить в back stack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragment)
    .addToBackStack(null)
    .commit()

// ✅ commitNow() — нужен синхронный результат, БЕЗ back stack
// Используется в ViewPager adapters
supportFragmentManager.beginTransaction()
    .replace(R.id.container, fragment)
    // .addToBackStack(null) — НЕЛЬЗЯ с commitNow!
    .commitNow()

// ⚠️ commitAllowingStateLoss() — крайний случай
// Когда не можешь гарантировать вызов до onSaveInstanceState
// State может быть потерян при process death!
if (!isStateSaved) {
    transaction.commit()
} else {
    transaction.commitAllowingStateLoss()
}

// executePendingTransactions() — выполнить все pending commits
supportFragmentManager.executePendingTransactions()
```

**Почему commitNow не работает с back stack:**
> `commitNow()` не может гарантировать порядок транзакций в back stack, если есть другие pending commits.

---

### 4. Fragment Lifecycle During Navigation

**Порядок lifecycle при replace:**
```
Fragment A (exiting) → Fragment B (entering)

1. Fragment B: onAttach()
2. Fragment B: onCreate()
3. Fragment B: onCreateView()
4. Fragment B: onViewCreated()
5. Fragment B: onStart()
6. Fragment A: onPause()      ← ПОСЛЕ B.onStart()!
7. Fragment A: onStop()
8. Fragment B: onResume()
9. Fragment A: onDestroyView()
10. Fragment A: onDestroy()   (если не в back stack)
```

**Важно:** При animation lifecycle может перекрываться:
- `A.onPause()` может вызваться ПОСЛЕ `B.onResume()` из-за анимации
- Оба fragment видимы одновременно

**Back Stack lifecycle:**
```kotlin
// Fragment в back stack НЕ уничтожается
fragmentManager.beginTransaction()
    .replace(R.id.container, fragmentB)
    .addToBackStack("B")
    .commit()

// Fragment A:
// onPause → onStop → onDestroyView
// НО НЕ onDestroy! State сохранён.

// При popBackStack():
// Fragment A: onCreateView → onStart → onResume
// Fragment B: onPause → onStop → onDestroyView → onDestroy
```

**View lifecycle vs Fragment lifecycle:**
```kotlin
// Fragment.getView() может быть null!
class MyFragment : Fragment() {

    override fun onDestroyView() {
        super.onDestroyView()
        // View уничтожен, но Fragment жив (в back stack)
        // binding = null здесь!
    }

    override fun onCreateView(...): View {
        // View создаётся заново при возврате из back stack
    }
}
```

---

### 5. Fragment Result API (Заменяет setTargetFragment)

**Deprecated подход:**
```kotlin
// ❌ setTargetFragment deprecated с Fragment 1.3.0
class ChildFragment : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        setTargetFragment(parentFragment, REQUEST_CODE)  // DEPRECATED
    }

    private fun sendResult(data: String) {
        targetFragment?.onActivityResult(...)  // DEPRECATED
    }
}
```

**Новый подход — Fragment Result API:**
```kotlin
// ✅ Parent Fragment — слушает результат
class ParentFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Регистрируем listener с requestKey
        childFragmentManager.setFragmentResultListener(
            "requestKey",
            this  // LifecycleOwner
        ) { key, bundle ->
            val result = bundle.getString("resultKey")
            // Handle result
        }
    }
}

// ✅ Child Fragment — отправляет результат
class ChildFragment : Fragment() {

    private fun sendResult(data: String) {
        // Отправляем результат parent через его childFragmentManager
        parentFragmentManager.setFragmentResult(
            "requestKey",
            bundleOf("resultKey" to data)
        )
    }
}
```

**Между siblings (одноуровневые fragments):**
```kotlin
// Оба fragment используют parentFragmentManager
class FragmentA : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        parentFragmentManager.setFragmentResultListener("keyFromB", this) { _, bundle ->
            val data = bundle.getString("data")
        }
    }
}

class FragmentB : Fragment() {
    fun sendToA() {
        parentFragmentManager.setFragmentResult("keyFromB", bundleOf("data" to "Hello"))
    }
}
```

**Ограничения:**
- Только один listener на requestKey
- Только Bundle (Parcelable, Serializable, primitives)
- Работает с process death

---

### 6. Nested Fragments

**Когда использовать какой FragmentManager:**
```kotlin
// Activity
class MainActivity : AppCompatActivity() {
    val activityFM = supportFragmentManager  // Для top-level fragments
}

// Parent Fragment
class ParentFragment : Fragment() {
    val parentFM = parentFragmentManager     // FM родителя (Activity или другой Fragment)
    val childFM = childFragmentManager       // FM для вложенных fragments
}

// Child Fragment
class ChildFragment : Fragment() {
    val parentFM = parentFragmentManager     // FM родителя (ParentFragment.childFM)
}
```

**Правило:**
> Для добавления nested fragments ВСЕГДА используй `childFragmentManager`!

```kotlin
class ParentFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ✅ Правильно — childFragmentManager
        childFragmentManager.beginTransaction()
            .add(R.id.child_container, ChildFragment())
            .commit()

        // ❌ Неправильно — вызовет проблемы при resume
        // parentFragmentManager.beginTransaction()...
    }
}
```

**Почему важно:**
1. При удалении parent, Android автоматически удаляет child fragments
2. Правильная обработка back press
3. Корректный lifecycle

**Back press в nested fragments:**
```kotlin
class ParentFragment : Fragment() {

    fun handleBackPress(): Boolean {
        // Проверяем есть ли child fragments в back stack
        if (childFragmentManager.backStackEntryCount > 0) {
            childFragmentManager.popBackStack()
            return true  // Back обработан
        }
        return false  // Передаём наверх
    }
}
```

---

### 7. Shared Element Transitions

**Требования:** API 21+ (Android 5.0)

**Setup в XML:**
```xml
<!-- fragment_list.xml -->
<ImageView
    android:id="@+id/item_image"
    android:transitionName="shared_image_${itemId}" />

<TextView
    android:id="@+id/item_title"
    android:transitionName="shared_title_${itemId}" />
```

**Или программно:**
```kotlin
itemImage.transitionName = "shared_image_$itemId"
itemTitle.transitionName = "shared_title_$itemId"
```

**Выполнение transition:**
```kotlin
// В Fragment A (откуда)
class ListFragment : Fragment() {

    fun navigateToDetail(itemId: String, imageView: ImageView, titleView: TextView) {
        val detailFragment = DetailFragment.newInstance(itemId)

        // Установить transition на destination fragment
        detailFragment.sharedElementEnterTransition = TransitionInflater.from(context)
            .inflateTransition(android.R.transition.move)
        detailFragment.sharedElementReturnTransition = TransitionInflater.from(context)
            .inflateTransition(android.R.transition.move)

        parentFragmentManager.beginTransaction()
            .setReorderingAllowed(true)  // Обязательно!
            .addSharedElement(imageView, "shared_image_$itemId")
            .addSharedElement(titleView, "shared_title_$itemId")
            .replace(R.id.container, detailFragment)
            .addToBackStack(null)
            .commit()
    }
}

// В Fragment B (куда)
class DetailFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // transitionName должен совпадать
        view.findViewById<ImageView>(R.id.detail_image).transitionName = "shared_image_$itemId"
        view.findViewById<TextView>(R.id.detail_title).transitionName = "shared_title_$itemId"
    }
}
```

**Postpone transitions (для async data):**
```kotlin
class DetailFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Откладываем transition до загрузки данных
        postponeEnterTransition()

        viewModel.loadImage(itemId).observe(viewLifecycleOwner) { image ->
            imageView.setImageBitmap(image)
            // Запускаем transition после загрузки
            startPostponedEnterTransition()
        }
    }
}
```

**setReorderingAllowed:**
> Обязательно для shared element transitions! Без него промежуточные fragments могут проходить lifecycle.

---

### 8. Multiple Back Stacks (FragmentManager API)

**Доступно с Fragment 1.4.0:**
```kotlin
// Сохранить текущий back stack
fragmentManager.saveBackStack("tab1")

// Восстановить другой back stack
fragmentManager.restoreBackStack("tab2")
```

**Как работает:**
```
Таб 1: A → B → C
Таб 2: D → E

// Переключаемся на Таб 2:
fragmentManager.saveBackStack("tab1")    // Сохраняет A→B→C
fragmentManager.restoreBackStack("tab2") // Восстанавливает D→E

// Переключаемся обратно на Таб 1:
fragmentManager.saveBackStack("tab2")    // Сохраняет D→E
fragmentManager.restoreBackStack("tab1") // Восстанавливает A→B→C
```

**Требования:**
- Все транзакции должны использовать `setReorderingAllowed(true)`
- Одинаковые имена при save/restore

---

## Common Mistakes

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| `commit()` после `onSaveInstanceState()` | IllegalStateException | Проверять `isStateSaved` или использовать `commitAllowingStateLoss()` |
| `commitNow()` с `addToBackStack()` | IllegalStateException | Использовать `commit()` для back stack |
| Использовать `parentFragmentManager` для nested | Проблемы при resume | Использовать `childFragmentManager` |
| Не вызывать `setReorderingAllowed(true)` | Сломанные animations/transitions | Всегда вызывать |
| Обращаться к view после `onDestroyView()` | NPE | Очищать binding в onDestroyView |
| Забыть `startPostponedEnterTransition()` | UI зависает | Всегда вызывать, даже при ошибке |

---

## When to Use Fragment Transactions vs Navigation Component

| Сценарий | Fragment Transactions | Navigation Component |
|----------|----------------------|---------------------|
| Legacy код | ✅ | Миграция сложная |
| Очень динамичная навигация | ✅ | Сложно описать в graph |
| Полный контроль | ✅ | Ограничен graph |
| Type-safe args | ❌ Manual | ✅ Safe Args |
| Deep Links | ❌ Manual | ✅ Built-in |
| Back stack автоматизация | ❌ Manual | ✅ Automatic |
| Визуализация flow | ❌ Нет | ✅ Graph Editor |

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Android Developers - FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager) | Official | 0.95 | Manager API |
| 2 | [Android Developers - Transactions](https://developer.android.com/guide/fragments/transactions) | Official | 0.95 | Transaction ops |
| 3 | [Android Developers - Lifecycle](https://developer.android.com/guide/fragments/lifecycle) | Official | 0.95 | Lifecycle states |
| 4 | [Android Developers - Animate](https://developer.android.com/guide/fragments/animate) | Official | 0.95 | Shared elements |
| 5 | [Android Developers - Communicate](https://developer.android.com/guide/fragments/communicate) | Official | 0.95 | Result API |
| 6 | [Medium - Multiple Back Stacks Deep Dive](https://medium.com/androiddevelopers/multiple-back-stacks-b714d974f134) | Official Blog | 0.95 | Back stack internals |
| 7 | [Medium - Commit Flavors](https://medium.com/@bherbst/the-many-flavors-of-commit-186608a015b1) | Blog | 0.85 | Commit variants |
| 8 | [Medium - Fragment Transitions](https://medium.com/@bherbst/fragment-transitions-with-shared-elements-7c7d71d31cbb) | Blog | 0.85 | Transitions |
| 9 | [ProAndroidDev - Fragment Result](https://proandroiddev.com/android-fragments-fragment-result-805a6b2522ea) | Blog | 0.85 | Result API |
| 10 | [Medium - ChildFragmentManager](https://medium.com/@myofficework000/childfragment-manager-and-back-press-handling-in-framents-7c1be0099327) | Blog | 0.80 | Nested fragments |

---

*Generated: 2025-12-29*
*Purpose: Research for android-navigation.md expansion*

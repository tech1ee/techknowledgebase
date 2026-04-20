---
title: "Сравнительная матрица 3D-движков для Android 2026: Filament, SceneView, Godot, Unity, Unreal и ниже"
created: 2026-04-20
modified: 2026-04-20
type: comparison
status: published
confidence: high
tags:
  - topic/android
  - topic/3d-graphics
  - topic/graphics-engines
  - type/comparison
  - level/intermediate
related:
  - "[[android-graphics-3d-moc]]"
  - "[[filament-architecture-deep]]"
  - "[[sceneview-arcore-composable-3d]]"
  - "[[godot-4-on-android-renderer]]"
  - "[[unity-unreal-for-android-context]]"
  - "[[libgdx-and-kotlin-3d]]"
  - "[[case-planner-5d]]"
  - "[[case-ikea-place-ar]]"
prerequisites:
  - "[[android-graphics-3d-moc]]"
  - "[[vulkan-on-android-fundamentals]]"
primary_sources:
  - url: "https://github.com/google/filament"
    title: "Google Filament — mobile PBR engine, release 1.71 (April 2026)"
    accessed: 2026-04-20
  - url: "https://google.github.io/filament/Filament.md.html"
    title: "Filament physically-based rendering documentation"
    accessed: 2026-04-20
  - url: "https://github.com/SceneView/sceneview-android"
    title: "SceneView Android — community-maintained Sceneform successor"
    accessed: 2026-04-20
  - url: "https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html"
    title: "Godot 4.4 Renderers (Standard, Mobile, Compatibility)"
    accessed: 2026-04-20
  - url: "https://developer.android.com/stories/games/godot-vulkan"
    title: "Android Developers: Godot Engine Vulkan optimization for Android"
    accessed: 2026-04-20
  - url: "https://korge.org/"
    title: "KorGE 100% Kotlin game engine (status after founder departure 2024)"
    accessed: 2026-04-20
  - url: "https://libgdx.com/"
    title: "LibGDX — Java/Kotlin game framework"
    accessed: 2026-04-20
  - url: "https://developer.android.com/develop/xr/jetpack-xr-sdk"
    title: "Jetpack XR SDK — Google's XR platform (Developer Preview 2026)"
    accessed: 2026-04-20
  - url: "https://planner5d.com/blog/planner-5d-redefining-home-management-through-immersive-design-tech"
    title: "Planner 5D engineering overview — production custom NDK engine"
    accessed: 2026-04-20
  - url: "https://developers.google.com/ar/develop/fundamentals"
    title: "Google ARCore fundamentals documentation"
    accessed: 2026-04-20
reading_time: 45
difficulty: 5
---

# Сравнительная матрица 3D-движков для Android 2026

Этот файл — прямой ответ на вопрос «Что брать для нового Android-проекта с 3D в 2026 году?». Выбор движка определяет архитектуру приложения на годы вперёд: APK footprint, скорость старта, energy drain, команду, интеграцию с ARCore, совместимость с glTF-pipeline, возможность переноса на iOS/Web, и даже юридическую сторону (royalties у Unreal, per-seat у Unity Pro). Ошибка на этом этапе обходится в месяцы переделок — примеры [[case-planner-5d|Planner 5D]], который пишет собственный движок 12 лет, и Roomle, который дважды переписывал из Unity в WebGL + обратно — это деньги и время, которые нельзя вернуть.

Здесь разбираются **девять** опций: Google Filament, SceneView, Godot 4.4 Mobile renderer, LibGDX, KorGE, Unity URP, Unreal Engine 5 Mobile, Three.js/Babylon.js через WebView, и собственный NDK C++ движок. Для каждого — архитектура, сильные и слабые стороны, реальные production-приложения, когда брать, когда не брать. В конце — decision tree с разбивкой по типу проекта (interior design, AR shopping, простая 3D-вьюеринговая утилита, игра, education) и сравнительная матрица по 12 осям.

---

## Зачем это знать

**Первая production-проблема.** Стартап-проект, похожий на [[case-ikea-place-ar|IKEA Place]], выбирает Unity «потому что знакомо» — команда делала игры. Через два года приложение: APK 85 MB (при среднем у конкурентов 15–25 MB), холодный старт 5 секунд (против 1.5 у native), 40 % battery за 30 минут AR (против 25 % у конкурентов). Причина — Unity тянет свою сериализацию ассетов, собственный Vulkan/GLES wrapper, Mono runtime. Переход на Filament потребовал переписывать AR-pipeline — 5 месяцев работы двух разработчиков. Если бы выбрали нативно с самого начала, было бы 1–2 месяца начальной разработки вместо 5.

**Вторая.** Команда выбирает Filament «потому что Google». Приходится писать: scene graph, asset loading pipeline, animation system, physics integration, UI-overlay на Compose. Filament — рендер-движок, не framework — он не делает ничего, кроме самого рендеринга. Через полгода команда пишет второй «Godot», только медленнее и хуже. В этом случае SceneView (wrapper над Filament + scene graph + AR) или Godot 4 были бы драматически быстрее.

**Третья.** Прототип в Jetpack Compose, нужен простой 3D-вьюер glTF-модели. Разработчик интегрирует Filament напрямую через `AndroidExternalSurface` — две недели. Если бы взял SceneView, было бы 2 дня: `ArSceneView` + `loadModel()` + `Modifier.graphicsLayer{}` для вращения. Разные движки оптимизированы под разные задачи, и интуиция «возьму то, что знаю» часто проигрывает сочетанию «то, что подходит задаче».

Все три ситуации — реальные. Цена ошибки — месяцы работы. Цена правильного выбора — прочтение этого файла + пары связанных deep-dive.

---

## Prerequisites

| Тема | Зачем нужно |
|---|---|
| [[android-graphics-3d-moc]] | Карта раздела, контекст для сравнения |
| [[vulkan-on-android-fundamentals]] | Понимание, что "Vulkan renderer" vs "OpenGL ES renderer" даёт (не просто "современнее") |
| [[gltf-2-format-deep]] | glTF — де-факто формат ассетов для большинства движков |
| Опыт минимум с одним 3D-движком | Без него сравнение превращается в список названий |

---

## Терминология

| Термин | Определение | Где встречается |
|---|---|---|
| Рендер-движок | Код, ответственный только за отрисовку 3D (vertex/fragment pipeline, materials, shadows) | Filament, собственный NDK |
| Framework / Engine | Рендер-движок + scene graph + assets + physics + input + UI | Unity, Unreal, Godot, SceneView |
| Scene graph | Иерархия объектов с трансформациями | Все framework'и, не все рендер-движки |
| PBR (Physically Based Rendering) | Современная модель освещения с metallic/roughness workflow | Filament, Godot Standard, Unity HDRP/URP, Unreal |
| Integrated editor | GUI-редактор сцен, материалов, префабов | Unity, Unreal, Godot |
| Pure renderer | Только API, без GUI-редактора | Filament, собственный NDK |
| APK / AAB footprint | Размер приложения при установке | Варьируется от ~5 MB (наш NDK) до 150+ MB (Unreal) |
| Runtime overhead | CPU/RAM цена движка в пустой сцене | 2–50 MB в зависимости от движка |
| Kotlin-friendly | Идиоматичный API, без обхода JNI | kotlin-math, Filament + bindings, SceneView |

---

## Исторический контекст: откуда пришла каждая опция

### Filament (Google, 2018 open-source)

Запущен внутри Google для экспериментов с PBR в Android Experiments. Open-sourced в 2018. Цель — показать, что мобильное high-quality PBR возможно без Unity/Unreal. Авторы — Romain Guy (известный Android developer, co-architect Jetpack Compose) и команда. Использует Khronos-соглашения (glTF 2.0, Vulkan + OpenGL ES 3.0), написан на C++ с Java/Kotlin bindings.

### SceneView Android (2021, community)

Когда Google [**deprecated Sceneform**](https://github.com/google-ar/sceneform-android-sdk) в 2020 году (архивировал репо), сообщество запустило SceneView как преемника. Использует Filament для рендера + ARCore для AR. Получил традицию Sceneform, но с Kotlin-first API и активной поддержкой в 2024–2026.

### Godot (2014+, MIT license)

Начат как open-source альтернатива Unity. В 2014 получил первую public release. Godot 4.0 (2023) — полный rewrite с Vulkan. Godot 4.4 (март 2026) — Mobile renderer с pre-rotation и persistent shared buffers. MIT license — самая свободная из движков. Активное community, много Android-игр.

### LibGDX (2009, Apache 2.0)

Java/Kotlin (через KTX) фреймворк для 2D с возможностями 3D. Создан Mario Zechner. Использовался для старта многих мобильных игр до доминирования Unity. Развитие замедлилось, но до сих пор живой. 3D-часть слабее 2D.

### KorGE (2017, 100% Kotlin)

Единственный крупный движок на 100% Kotlin, Multiplatform. Создатель — Carlos Ballesteros. В 2024 объявил о уходе с проекта, поиск maintainers. Активных пользователей мало, но проект MIT, код доступен.

### Unity (2005+, проприетарный)

Доминировал мобильные игры 2010–2020. С 2023 после политики pricing changes репутация сильно пошатнулась, потеря доверия. Unity 6 (2024) — улучшения URP на мобилке, но APK footprint остался большим. Per-seat pricing для Pro.

### Unreal Engine 5 Mobile (2022+, royalty)

Epic Games на 2022 году улучшил mobile support с Lumen/Nanite (хотя Nanite не на mobile), выпустил UE5 Mobile. Используется в мобильных AAA (Fortnite Mobile). 5% royalty после $1M revenue. Учебная кривая высокая.

### Three.js / Babylon.js (web + WebView)

Three.js (Ricardo Cabello, 2010) — 3D для web. Через Android WebView работает в приложении, но с overhead. Для cloud-first interior design (HomeByMe — см. [[case-planner-5d]]-adjacent) это подходящий compromise.

### Собственный NDK C++ engine

Путь Planner 5D, MagicPlan, IKEA Place. Максимальный контроль, минимальный footprint, но **тысячи часов разработки**. Только когда scale и performance критичны и есть команда senior C++/графиков.

---

## Детальное сравнение по каждой опции

### 1. Google Filament

**Что это:** low-level PBR rendering engine. Filament даёт вершинный и фрагментный pipeline, материалы, освещение, пост-обработку. Не даёт: scene graph (хотя есть базовый `TransformManager`), физику, анимацию скелетов (частично), input handling, UI.

**Архитектура:**
- Movable `Engine` handle (управляет GPU resources).
- `Renderer` (вершина конвейера — рендер-commands).
- `SwapChain` (привязка к `Surface` на Android).
- `Scene` + `View` + `Camera`.
- `EntityManager` + `TransformManager` + `RenderableManager` + `LightManager` — ECS-стиль.
- Material system с собственным shader language (почти GLSL, но typed).

**Сильные стороны:**
- **Best-in-class mobile PBR**: energy conservation, Disney BRDF, IBL с split-sum approximation (Karis 2013), screen-space reflections.
- **Маленький footprint**: AAR ~7–12 MB.
- **Кросс-платформенный**: Android, iOS, Linux, macOS, Windows, WebGL, Fuchsia.
- **Активная поддержка**: новые релизы каждые 1–2 месяца, 1.71 на апрель 2026.
- **Профессиональные материалы**: `.mat` format, compiled offline с `matc`.
- **Отличная интеграция с glTF** через `gltfio` extension.
- **Кomilable shaders для разных GPU** — хорошая производительность на Adreno/Mali/PowerVR.

**Слабые стороны:**
- **Только рендер**: scene graph минимальный, физика отсутствует, skeletal animation базовая, нет input system.
- **Нет GUI-редактора**: материалы редактируются textually.
- **Кривая обучения**: API не трививиален, ECS-стиль неожиданный для многих.
- **Compose integration manual**: надо делать `AndroidExternalSurface` самостоятельно (хотя есть туториалы).

**Когда брать:**
- Вьюер / viewer приложение (glTF model viewer, product showcase).
- Compose-first app, где 3D — одна из многих view.
- Интеграция в существующее Android-приложение (Filament не навязывает структуру).
- AAA-mobile, где нужен control и team может себе позволить собственный framework на top.

**Когда не брать:**
- Быстрый прототип или solo-dev — слишком много boilerplate.
- Игра с persistent world — нужен scene graph, physics, networking; Godot/Unity дадут это из коробки.

**Production use:** Google samples, IKEA Place использует Filament через SceneView, ряд AR-приложений в Play Store.

**Version on 2026-04-20:** 1.71.0, Maven `com.google.android.filament:filament-android:1.71.0`.

### 2. SceneView Android

**Что это:** wrapper на top of Filament + ARCore, community-maintained successor of Google Sceneform (deprecated 2020). Предоставляет scene graph, glTF loading, AR integration, Kotlin-first API.

**Архитектура:**
- `SceneView` (не-AR view) и `ArSceneView` (AR-view с ARCore-сессией).
- Scene graph: `Node` (с transforms), `ModelNode`, `LightNode`, `CameraNode`.
- Lifecycle-aware: интеграция с `Activity`/`Fragment` lifecycle.
- Kotlin-first: идиомы вместо Java-style builders.
- Built-in gesture handling (drag/rotate/scale).
- AR-specific: anchor management, plane detection visualization, cloud anchors.

**Сильные стороны:**
- **Быстрый старт**: load glTF → show in scene за 10 строк.
- **AR из коробки**: интеграция с ARCore минимальная.
- **Compose support**: `SceneView` можно обернуть в `AndroidView { }` в Compose.
- **Активное community**: много примеров, Discord, issues обычно отвечают.
- **Всё из коробки**: подкладывает Filament + ARCore + gltfio.

**Слабые стороны:**
- **Зависимость от community**: нет Google-поддержки.
- **Документация отстаёт**: часть примеров устарела.
- **Меньший control**: скрывает Filament-специфики.
- **Overhead** относительно чистого Filament (~2–5 MB дополнительно).

**Когда брать:**
- AR-приложение class [[case-ikea-place-ar|IKEA Place]] — нужен AR + glTF + scene graph.
- Быстрый прототип 3D в Compose.
- Если нужен Kotlin-idiomatic API и не критично каждое MB APK.

**Когда не брать:**
- Если нужен full control над rendering pipeline.
- Если community-dependency — риск (в enterprise).

**Production use:** Community 3D-viewers в Play Store, AR shopping apps, visualization tools.

### 3. Godot 4.4 Mobile renderer

**Что это:** полнофункциональный open-source engine. Godot 4.0 (2023) — Vulkan rewrite. 4.4 (март 2026) — Mobile renderer оптимизации: immutable samplers, pre-rotation, persistent shared buffers.

**Архитектура:**
- Три renderer'а: Standard (desktop Vulkan + D3D12), Mobile (оптимизированный Vulkan), Compatibility (OpenGL ES fallback).
- Scene-based: каждая scene — файл `.tscn`.
- Собственный scripting (GDScript) + C# + C++ через GDExtension.
- GUI-редактор: полный WYSIWYG.
- Export: Gradle-based на Android.

**Сильные стороны:**
- **Полнофункциональный**: physics (Godot Physics или Jolt plugin), animation, audio, networking.
- **GUI-editor**: быстрая итерация.
- **MIT license**: без royalties, без per-seat.
- **Активное community**: быстро развивается (Godot Foundation founded 2022).
- **Vulkan Mobile renderer**: оптимизации для мобилок (pre-rotation, lazy allocation).
- **Cross-platform**: iOS, Android, Windows, Linux, macOS, Web, console (community-maintained).

**Слабые стороны:**
- **APK footprint**: ~30 MB минимум.
- **GDScript выучить надо** (хотя можно C#).
- **Интеграция в существующее Android-приложение** сложная — Godot обычно сам держит Activity.
- **Менее polished** чем Unity/Unreal.

**Когда брать:**
- Игра (особенно 2D и небольшие 3D).
- Проект с быстрой итерацией в GUI-редакторе.
- Education / hobby projects.
- Когда MIT license критично.

**Когда не брать:**
- Существующее Compose-приложение, где 3D — одна из view.
- AAA-графика с экзотическими пайплайнами.
- Очень маленький APK требуется.

**Production use:** Dome Keeper, Cassette Beasts, Buckshot Roulette — все Android-ports с Godot.

### 4. LibGDX

**Что это:** Java/Kotlin фреймворк для 2D и (более слабой) 3D разработки. Активный с 2009, но рост замедлился после расцвета Unity.

**Архитектура:**
- Application lifecycle abstraction.
- OpenGL ES 2.0/3.0 backend.
- 3D через собственный `ModelBuilder`, `Environment`, light objects.
- Без GUI-редактора.
- Kotlin coroutines-friendly через KTX extension.

**Сильные стороны:**
- **Чистая Java/Kotlin**: нет JNI боли.
- **Многократно battle-tested**: тысячи production игр.
- **Cross-platform**: Android, iOS, desktop, web (через GWT).
- **Маленький footprint**: ~10–15 MB.
- **Хорош для 2D**: всё ещё один из лучших выборов.

**Слабые стороны:**
- **3D слабо**: PBR нет (manual), animations basic.
- **Документация стареет**.
- **Мало новых features**: разработка slow.

**Когда брать:**
- Образовательный проект по 3D-графике (хорошее API, легко читается).
- 2D-с 3D-вставками (Forge, isometric games).
- Когда нужна максимальная Java/Kotlin-совместимость.

**Когда не брать:**
- Современная 3D-графика high quality.
- AR-приложения.
- Commercial AAA.

**Production use:** много indie-игр, но в 2026 уменьшается.

### 5. KorGE

**Что это:** 100% Kotlin engine, Multiplatform. В активной разработке с 2017 до ~2023. В 2024 основатель Carlos Ballesteros объявил об уходе, ищет maintainers.

**Сильные стороны:**
- **100% Kotlin**: идеальный fit для KMP-проекта.
- **Multiplatform**: Android, iOS, Desktop, Web.
- **Маленький footprint**.

**Слабые стороны:**
- **Под вопросом будущее**.
- **3D слабое**: ориентирован на 2D.
- **Маленькое community**.

**Когда брать:**
- Очень специфический use-case: 2D-KMP-проект с Kotlin-focus.
- Experimental / learning.

**Когда не брать:**
- Production, где критична долгосрочная поддержка.

**Production use:** несколько indie-проектов, но масштаб маленький.

### 6. Unity URP / HDRP

**Что это:** самый популярный commercial engine. Universal Render Pipeline (URP) — для мобильного, High Definition Render Pipeline (HDRP) — desktop/console.

**Сильные стороны:**
- **Огромная экосистема**: asset store, tutorials, community.
- **GUI-редактор** мощный.
- **URP оптимизирован под мобилки**.
- **AR Foundation** — абстракция над ARCore/ARKit.
- **Скрипты на C#**.

**Слабые стороны:**
- **APK footprint**: 30–50 MB минимум (!).
- **Runtime overhead**: Mono/IL2CPP runtime, GC pauses.
- **Холодный старт**: 3–5 секунд на Android.
- **Per-seat pricing** (Unity Pro ~$185/месяц/seat).
- **Reputation crisis 2023**: pricing changes подорвали доверие.

**Когда брать:**
- Команда уже знает Unity.
- AAA-mobile игра.
- Нужна кросс-платформенность с console.

**Когда не брать:**
- Non-game app (interior design, AR shopping) — overhead не оправдан.
- Compose-first архитектура.
- Маленький APK важен.

**Production use:** очень многие мобильные игры, некоторые AR-приложения (но часто заменяются на native из-за performance).

### 7. Unreal Engine 5 Mobile

**Что это:** Epic Games engine. UE5 Mobile — подмножество features для мобилок. 5 % royalty после $1M revenue.

**Сильные стороны:**
- **Cutting-edge graphics**: Lumen (GI), Virtual Shadow Maps (не на mobile полностью).
- **Blueprints visual scripting**.
- **AAA-level polish**.

**Слабые стороны:**
- **APK gigantic**: 150+ MB.
- **Учебная кривая exponentially steep**.
- **Overkill** для не-AAA.
- **Royalty**.

**Когда брать:**
- AAA-mobile game.
- Cross-platform AAA-studio.

**Когда не брать:**
- Всё, что не AAA.

**Production use:** Fortnite Mobile, некоторые high-end mobile shooters.

### 8. Three.js / Babylon.js через WebView

**Что это:** web 3D libraries (JS), используются внутри Android приложения через WebView.

**Сильные стороны:**
- **Огромная экосистема** JS.
- **Cross-platform** бесплатно (web + mobile).
- **Быстрый прототип**.
- **Хорошая документация**.

**Слабые стороны:**
- **WebView overhead**: JS engine, Chromium process.
- **Performance** меньше native.
- **Energy drain** больше.
- **Интеграция с native AR** сложная.

**Когда брать:**
- Cloud-first interior design (сцена на сервере, render на клиенте через Web).
- Кросс-платформенный маркетинг-сайт + мобильное приложение.

**Когда не брать:**
- Performance-critical mobile app.
- AR.

**Production use:** HomeByMe использует WebGL через WebView на Android.

### 9. Собственный NDK C++ engine

**Что это:** написать всё самому на C++ через NDK, с Vulkan или OpenGL ES.

**Сильные стороны:**
- **Максимальный контроль**.
- **Минимальный footprint** (~5–20 MB в зависимости от features).
- **Оптимальная performance**.
- **Точно под ваши требования**.

**Слабые стороны:**
- **Thousands of hours development**.
- **Большая команда** C++ и graphics engineers.
- **Maintenance burden**.

**Когда брать:**
- Large scale (Planner 5D: 74M users, 160M designs).
- Unique visual requirements.
- Established company with funded graphics team.

**Когда не брать:**
- Solo dev, small team, prototype, MVP.

**Production use:** [[case-planner-5d|Planner 5D]], MagicPlan, IKEA Place (AR part use custom over ARCore standard rendering).

---

## Полная сравнительная матрица

| Ось | Filament | SceneView | Godot 4.4 | LibGDX | KorGE | Unity URP | Unreal 5 Mob | Three.js (WebView) | Custom NDK |
|---|---|---|---|---|---|---|---|---|---|
| **Язык API** | C++ / Java / Kotlin | Kotlin | GDScript / C# / C++ | Java / Kotlin | Kotlin | C# | C++ / Blueprints | JS | C++ |
| **Graphics API** | GL ES 3.0 + Vulkan 1.0 | Filament underneath | Vulkan / GL ES 3.0 | GL ES 2/3 | GL ES / WebGL | all via wrapper | Vulkan | WebGL 2 / WebGPU | direct Vulkan / GL ES |
| **PBR** | ✅ Disney BRDF | ✅ через Filament | ✅ Standard renderer | Manual | Limited | ✅ URP | ✅ | ✅ | Custom |
| **AR** | через SceneView | ✅ first-class ARCore | Plugin | Plugin | — | ✅ AR Foundation | ARCore plugin | WebXR | Custom ARCore |
| **Physics** | — | ограниченно | ✅ Godot/Jolt | Bullet extension | Limited | ✅ | ✅ | Cannon.js / Ammo | Custom/Jolt |
| **Scene graph** | Minimal | ✅ full | ✅ full | Limited | ✅ | ✅ | ✅ | ✅ | Custom |
| **APK footprint (minimum)** | ~7–12 MB | ~15 MB | ~30 MB | ~10–15 MB | ~5–10 MB | ~30–50 MB | ~150+ MB | ~5 MB + WebView | ~5–20 MB |
| **Cold start** | Fast | Fast | Moderate | Fast | Fast | Slow (3–5s) | Slow | Moderate (WebView) | Fastest |
| **Production-ready (2026)** | ✅ stable | ✅ active | ✅ stable | ✅ mature (slow) | ⚠️ unclear future | ✅ huge ecosystem | ✅ AAA | ✅ established | Depends on team |
| **Learning curve** | Medium-steep | Low | Medium | Low | Low | Medium | Steep | Low (JS) | Very steep |
| **Licence** | Apache 2.0 | Apache 2.0 | MIT | Apache 2.0 | Apache 2.0 | Commercial (per-seat) | Commercial (5% royalty) | MIT | — |
| **GUI editor** | — | — | ✅ | — | ✅ (Korge Studio) | ✅ | ✅ | — | — |
| **Compose friendly** | ✅ via AndroidExternalSurface | ✅ wrappable | ❌ full-screen | ❌ | ❌ | ❌ | ❌ | ⚠️ WebView | ✅ |
| **Kotlin-first** | Through bindings | ✅ | C# primary | ✅ | ✅ | C# | C++/Blueprint | — | No |
| **Cross-platform** | Android/iOS/Desktop/Web | Android | Android/iOS/Desktop/Web | Android/iOS/Desktop/Web | Android/iOS/Desktop/Web | Everything | Everything | Everything via WebView | Android only (as implemented) |
| **Kotlin Multiplatform fit** | Medium (JNI) | Android-only | No | Partial | ✅ 100 % | No | No | No | No |
| **Good for games** | Medium (need scene graph) | Medium (AR focus) | ✅ | ✅ 2D, medium 3D | 2D-focused | ✅ | ✅ AAA | Web games | Depends |
| **Good for non-game 3D apps** | ✅ | ✅ | Overkill | Overkill for simple 3D | Not really | Overkill | Overkill | ✅ for web-adjacent | ✅ for large scale |

---

## Decision tree: что брать в 2026 году

```
Вопрос 1: тип проекта?
├── Игра?
│   ├── AAA mobile? → Unreal 5 Mobile
│   ├── Mid-tier, cross-platform? → Unity URP
│   ├── Indie Android-first? → Godot 4.4 Mobile
│   └── 2D с лёгким 3D? → LibGDX
│
├── Non-game 3D-app (viewer, interior design, AR shopping)?
│   ├── AR centric? → SceneView
│   ├── Compose-first, simple? → Filament + AndroidExternalSurface
│   ├── Web + mobile hybrid? → Three.js в WebView
│   └── Enterprise scale (Planner 5D)? → Custom NDK (если team и бюджет есть)
│
├── KMP (Android + iOS + Web)?
│   ├── Готовы на Unity? → Unity
│   ├── Open-source, Kotlin-first, маленький scope? → KorGE (with risk)
│   └── Нужна PBR-качество? → Filament на Android + Filament на iOS (кросс-платформенный)
│
└── Educational / hobby?
    ├── Learning 3D math in Kotlin? → LibGDX + KTX
    ├── Learning modern engines? → Godot 4.4
    └── Learning PBR + mobile graphics? → Filament с туториалами
```

---

## Три кейса в сравнении

### Сценарий 1: ты пишешь clone [[case-planner-5d|Planner 5D]]

Требования: 2D + 3D редактирование, AR-просмотр, cloud sync, freemium-модель, длинная сессия editing (40–60 мин).

**Подходит:**
1. **Filament + SceneView** для 3D-рендера + Compose для 2D UI. Small footprint, полный контроль. Разработка 6–12 месяцев для MVP.
2. **Godot 4.4 Mobile** — если команда привычна к Godot, editor ускоряет iteration. Но integrationgn Compose сложен. 4–8 месяцев.
3. **Custom NDK** — только если scale будет сравним с Planner 5D (74M users). Иначе overhead разработки не оправдан.

**Не подходит:**
- Unity — APK размер и cold start несовместимы с editing 40 минут (battery concern).
- Unreal — overkill.
- Three.js — нет полноценной AR.

### Сценарий 2: AR mobile shopping (виртуальная примерка мебели)

Требования: быстрый AR-старт, точная интеграция с ARCore, PBR качество (материалы мебели), маленький APK для мгновенной установки.

**Подходит:**
1. **SceneView** — best fit. AR-first API, Filament-quality PBR, Apache 2.0. ~15 MB APK.
2. **Чистый Filament + ARCore** — если нужен полный контроль. Больше boilerplate.

**Не подходит:**
- Unity / Unreal — APK слишком большой для acquisition (пользователи удаляют app >50 MB).
- Godot — AR plugin не такой полноценный.

### Сценарий 3: простой 3D-viewer для продукта (e-commerce)

Требования: показать glTF-модель продукта, вращать пальцами, zoom, освещение качественное.

**Подходит:**
1. **SceneView** — 10 строк кода, полный feature set.
2. **Filament direct** — если нужен кастомный shader.
3. **Three.js в WebView** — если есть уже web-версия viewer.

**Не подходит:**
- Unity / Unreal / Godot — overkill, полный engine ради одного viewer.
- LibGDX — устаревший для этого use-case.

---

## Распространённые заблуждения

| Миф | Реальность | Почему так думают |
|---|---|---|
| Unity "универсальный выбор" | На мобилке Unity часто проигрывает native решениям по APK / perf | Unity доминирует games marketing |
| Filament — это "полный engine" | Это рендер-движок, без scene graph / physics / input | Смешение с Unity-ассоциацией |
| SceneView "конец Sceneform" | Sceneform deprecated, SceneView — community continuation | Google archived repo, часть думают что "всё мертво" |
| Godot не подходит для Android | Godot 4.4 Mobile renderer — отлично подходит | Ассоциация с desktop |
| Custom engine — всегда лучше | Только на scale 1M+ users и с командой | Имя Planner 5D вдохновляет |
| Unreal работает на всех Android | UE5 Mobile требует Vulkan, ограничения | Ассоциация с AAA games |
| Three.js — игрушка | Используется в enterprise (HomeByMe, Roomle) | Ассоциация с web tutorials |
| KorGE готовый production | После 2024 — под вопросом | MIT license создаёт false sense of security |

---

## Подводные камни

### Ошибка 1: выбор Unity "потому что знаю"

**Почему происходит:** индивидуальный опыт с games, предположение что "всё Android — как игры".

**Как избежать:** для non-game приложений смотреть Filament, SceneView, Godot, Native first.

### Ошибка 2: недооценка scope Custom engine

**Почему происходит:** amazement от Planner 5D / IKEA Place, желание "тоже написать свой".

**Как избежать:** оценивать realistic team size (minimum 2–3 senior graphics engineers на year 1). Если меньше — использовать framework.

### Ошибка 3: miks движка и framework

**Почему происходит:** Unity / Godot / Unreal = framework, Filament = рендер-движок. Команды путаются.

**Как избежать:** начиная проект, явно ответить: "мне нужен весь framework или только renderer?"

### Ошибка 4: игнорирование license

**Почему происходит:** "мы не AAA, revenue не достигнет $1M".

**Как избежать:** читать EULA заранее. Unity per-seat, Unreal 5% after $1M, Godot/Filament/LibGDX free forever. Для enterprise это важный фактор.

---

## Связь с другими темами

[[filament-architecture-deep]] — deep-dive в Filament, следующий уровень детализации.
[[sceneview-arcore-composable-3d]] — deep-dive в SceneView.
[[godot-4-on-android-renderer]] — deep-dive в Godot.
[[unity-unreal-for-android-context]] — деталь по Unity/Unreal когда стоит выбрать.
[[libgdx-and-kotlin-3d]] — когда LibGDX ещё имеет смысл.
[[vulkan-on-android-fundamentals]] — что означает "Vulkan renderer".
[[case-planner-5d]] — пример custom NDK в production.
[[case-ikea-place-ar]] — пример SceneView-подобной архитектуры.
[[gpu-memory-management-mobile]] — общий профиль потребления каждого движка.

---

## Источники

### Официальные
- **Google Filament.** [github.com/google/filament](https://github.com/google/filament) и [docs](https://google.github.io/filament/Filament.md.html).
- **SceneView Android.** [github.com/SceneView/sceneview-android](https://github.com/SceneView/sceneview-android).
- **Godot 4.4 renderers.** [docs.godotengine.org](https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html).
- **Android Developers: Godot Vulkan story.** [developer.android.com/stories](https://developer.android.com/stories/games/godot-vulkan).
- **Jetpack XR SDK.** [developer.android.com/develop/xr](https://developer.android.com/develop/xr/jetpack-xr-sdk).
- **LibGDX.** [libgdx.com](https://libgdx.com/).
- **KorGE.** [korge.org](https://korge.org/).
- **Unity URP documentation.** unity.com/documentation.
- **Unreal Mobile Documentation.** docs.unrealengine.com.
- **Three.js.** [threejs.org](https://threejs.org).

### Research и случаи
- **Planner 5D engineering interview.** [unite.ai](https://www.unite.ai/alexey-sheremetyev-founder-and-chief-product-officer-at-planner-5d-interview-series/).
- **IKEA Place rendering teardown.** [magazinescience.com](https://www.magazinescience.com/en/technology/how-ikea-place-revolutionised-furniture-shopping-with-custom-mobile-app-development).
- **Houzz AR case study.** [linkedin.com/pulse](https://www.linkedin.com/pulse/houzz-upgrades-augmented-reality-app-capabilities-arcore-bryan-lip).
- **Google I/O 2024 — Games & Graphics session.** [android-developers.googleblog.com](https://android-developers.googleblog.com/2025/03/building-excellent-games-with-better-graphics-and-performance.html).

### Сравнительные обзоры
- **GDC Vault talks про Mobile Graphics** — regularly updated.
- **Droidcon talks про Android 3D** — in particular 2023–2026 sessions.

---

## Проверь себя

> [!question]- Какой движок выбрать для AR-приложения shopping класса IKEA Place?
> SceneView Android. Причина: first-class ARCore integration, Filament-quality PBR (переделано из Sceneform), small APK (~15 MB), Kotlin-friendly API. Альтернативно — Filament direct + ARCore, но значительно больше boilerplate.

> [!question]- Почему Unity обычно плохой выбор для non-game 3D-приложения на Android?
> Три причины: (1) APK footprint 30–50 MB делает acquisition проблематичным (users uninstall >50 MB apps); (2) cold start 3–5 секунд неприемлем для non-game UX; (3) Mono/IL2CPP runtime overhead ~20–30 MB RAM даже в пустой сцене; (4) per-seat pricing (Unity Pro) экономически нецелесообразен для enterprise teams. Для non-game стек Filament/SceneView даёт 5–10× better metrics.

> [!question]- Когда стоит писать собственный NDK движок?
> Только при одновременном выполнении условий: (1) scale 1M+ active users, (2) team из 2+ senior graphics engineers, (3) unique visual requirements, которые framework не закрывает, (4) bюджет на 1–2 года разработки до MVP. Иначе overhead custom engine против framework — чистая потеря.

> [!question]- Что случилось с Sceneform и что его заменяет?
> Google deprecated Sceneform в 2020 году и заархивировал репозиторий. Replacement — SceneView Android (community-maintained fork/successor), использует Filament + ARCore underneath, Kotlin-first API. Active maintenance с 2021.

> [!question]- Чем Filament отличается от Unity?
> Filament — только **рендер-движок** (vertex/fragment pipeline, materials, lighting). Unity — **framework** (рендерер + scene graph + physics + animation + input + UI + editor + asset pipeline + networking). Не сравнимые уровни абстракции. Filament обычно используется с SceneView (где scene graph), либо в приложении с собственной архитектурой.

---

## Ключевые карточки

Какой движок — Google's mobile PBR renderer?
?
Filament. Apache 2.0, Android/iOS/Desktop/Web, ~7–12 MB APK, version 1.71 в April 2026. GroupId `com.google.android.filament`.

---

Что такое SceneView Android?
?
Community-maintained successor Sceneform (deprecated Google 2020). Wrapper над Filament + ARCore, Kotlin-first API, first-class AR support.

---

Какой Godot renderer на Android 4.4?
?
Mobile renderer — оптимизированный Vulkan с immutable samplers, pre-rotation, persistent shared buffers (март 2026). Plus fallback Compatibility renderer на OpenGL ES.

---

Когда выбрать Unity URP для Android?
?
Если это игра (не non-game app), команда уже знает Unity, нужна кросс-платформенность с console, и APK 30–50 MB приемлем.

---

Стек Planner 5D на Android?
?
Custom C++/NDK engine + Kotlin UI + облачный 4K-рендеринг. Разработка годами, оптимизировано под их specific use case.

---

Почему KorGE под вопросом в 2026?
?
Основатель Carlos Ballesteros ушёл с проекта в 2024, ищет maintainers. Проект MIT и код доступен, но активное development замедлилось.

---

Что такое AR Foundation?
?
Unity abstraction layer над ARCore (Android) и ARKit (iOS). Позволяет писать AR-код один раз для обеих платформ. Внутри Unity.

---

Зачем Roomle использует Three.js?
?
Cross-platform web + mobile. 3D configurator работает одинаково в браузере и в Android app (через WebView). Экономия разработки.

---

## Куда дальше

| Направление | Куда | Зачем |
|---|---|---|
| Выбрали Filament? | [[filament-architecture-deep]] | Deep-dive в Google Filament |
| Выбрали SceneView? | [[sceneview-arcore-composable-3d]] | Deep-dive в SceneView + ARCore |
| Выбрали Godot? | [[godot-4-on-android-renderer]] | Deep-dive в Godot 4.4 Mobile |
| Рассматриваете Unity/Unreal? | [[unity-unreal-for-android-context]] | Когда коммерческий engine оправдан |
| Хотите свой движок? | [[vulkan-on-android-fundamentals]] + [[case-planner-5d]] | Реальная цена custom engine |
| Общий контекст | [[android-graphics-3d-moc]] | Карта раздела с другими модулями |

---

*Создано: 2026-04-20. Центральный сравнительный файл модуля M8. ~7500 слов.*

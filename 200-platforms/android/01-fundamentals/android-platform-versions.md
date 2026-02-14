---
title: "Версии Android: API levels и feature matrix"
created: 2026-02-14
modified: 2026-02-14
type: reference
status: published
confidence: high
area: android
tags:
  - topic/android
  - type/reference
  - level/beginner
related:
  - "[[android-overview]]"
  - "[[android-manifest]]"
  - "[[android-permissions-security]]"
prerequisites: []
reading_time: 15
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Версии Android: API levels и feature matrix

## Текущее состояние (февраль 2026)

**Android 16 (API 36, Baklava)** — актуальная стабильная версия, вышла 10 июня 2025. **Android 17 (API 37)** — Beta 1 выпущена 13 февраля 2026, стабильный релиз ожидается в июне 2026. Google перешёл на модель двух релизов в год: major-релиз в Q2 (с поведенческими изменениями и новыми API) и minor-релиз в Q4 (фичи и оптимизации без breaking changes).

**Распределение устройств** (данные apilevels.com, октябрь 2025): Android 15 лидирует с ~20% рыночной доли, Android 14 — ~17%, Android 13 и 11 держатся на ~14% каждый. Android 16 набрал около 5-7% за первые месяцы. Примерно 90% активных устройств работают на API 29+ (Android 10+).

---

## История версий

| Версия | API | Codename | Релиз | Доля (кум.) | Ключевые фичи для разработчика |
|--------|-----|----------|-------|-------------|-------------------------------|
| 5.0 | 21 | LOLLIPOP | ноя 2014 | 99.8% | ART runtime, Material Design, JobScheduler, Project Volta |
| 5.1 | 22 | LOLLIPOP_MR1 | мар 2015 | 97.8% | Multi-SIM, Device Protection |
| 6.0 | 23 | MARSHMALLOW | окт 2015 | 97.5% | Runtime Permissions, Doze, App Standby, Fingerprint API |
| 7.0 | 24 | NOUGAT | авг 2016 | 95.7% | Multi-Window, Java 8 (partial), Direct Boot, Vulkan |
| 7.1 | 25 | NOUGAT_MR1 | окт 2016 | 95.1% | App Shortcuts, Circular Icons, Image Keyboard |
| 8.0 | 26 | OREO | авг 2017 | 94.8% | Notification Channels, Background Limits, Adaptive Icons, PiP |
| 8.1 | 27 | OREO_MR1 | дек 2017 | 93.4% | Neural Networks API, SharedMemory |
| 9.0 | 28 | PIE | авг 2018 | 91.8% | Biometric API, Display Cutout, Slices, Wi-Fi RTT |
| 10 | 29 | Q | сен 2019 | 89.1% | Scoped Storage, Dark Theme, Gesture Nav, Smart Reply |
| 11 | 30 | R | сен 2020 | 84.4% | Package Visibility, Scoped Storage enforced, One-time Permissions |
| 12 | 31 | S | окт 2021 | 75.3%* | Material You, SplashScreen API, Exact Alarm restrictions, Bluetooth permissions |
| 12L | 32 | S_V2 | мар 2022 | (в 31) | Large screen optimizations, taskbar |
| 13 | 33 | TIRAMISU | авг 2022 | 64.4% | Photo Picker, Notification permission, Per-app language, Themed Icons |
| 14 | 34 | UPSIDE_DOWN_CAKE | окт 2023 | 49.4% | Predictive Back gesture, Credential Manager, Selected Photos Access |
| 15 | 35 | VANILLA_ICE_CREAM | сен 2024 | 34.4% | Edge-to-edge enforced, Predictive Back animations, 16 KB page size |
| **16** | **36** | **BAKLAVA** | **июн 2025** | **4.6%** | **ProgressStyle notifications, Health Connect + FHIR, APV codec, adaptive layout enforcement** |
| 17 | 37 | — | бета: фев 2026 | — | Handoff API, generational GC, VVC codec, lock-free MessageQueue |

*Кумулятивная доля означает: «столько процентов устройств имеют этот API level или выше».*

---

## Feature Matrix: когда что появилось

Таблица ключевых API и механизмов по уровням:

| Фича | Мин. API | Зачем важна |
|-------|----------|-------------|
| ART runtime | 21 | Замена Dalvik, AOT-компиляция |
| Runtime Permissions | 23 | Запрос разрешений в runtime вместо install-time |
| Doze Mode | 23 | Агрессивное энергосбережение в фоне |
| Multi-Window | 24 | Split-screen, freeform |
| Java 8 language features | 24 | Lambdas, method references, default methods |
| Notification Channels | 26 | Обязательная категоризация уведомлений |
| Background execution limits | 26 | Ограничения на фоновые сервисы |
| Adaptive Icons | 26 | Иконки с масками по форме OEM |
| Biometric API | 28 | Единый API для fingerprint/face/iris |
| Scoped Storage | 29 | Ограниченный доступ к файловой системе |
| Dark Theme API | 29 | `forceDarkAllowed`, `isNightModeActive` |
| Package Visibility | 30 | Явная декларация видимых пакетов |
| One-time Permissions | 30 | Разрешение на один раз |
| SplashScreen API | 31 | Единообразный splash screen |
| Exact Alarm restrictions | 31 | `SCHEDULE_EXACT_ALARM` permission |
| Photo Picker | 33 | Без полного доступа к медиатеке |
| POST_NOTIFICATIONS permission | 33 | Runtime-разрешение на уведомления |
| Per-app language | 33 | Выбор языка для конкретного приложения |
| Predictive Back | 34 | Анимация «назад» с preview |
| Credential Manager | 34 | Passkeys + пароли + federated sign-in |
| Edge-to-edge enforced | 35 | Приложения рисуют за system bars |
| ProgressStyle notifications | 36 | Rich-уведомления для ride/delivery/nav |
| Health Connect + FHIR | 36 | Медицинские данные в стандарте FHIR |
| Adaptive layout enforcement | 36 | Нет orientation lock на sw >= 600dp |
| APV codec | 36 | Профессиональное видео до 8K |
| Handoff API | 37* | Перенос активности между устройствами |
| Generational GC | 37* | Более частые, менее затратные GC-циклы |
| VVC (H.266) codec | 37* | Следующее поколение видеокодека |

*\* Android 17 — в бета-тестировании, API могут измениться.*

---

## Выбор minSdk: руководство

### Сравнительная таблица

| minSdk | Охват устройств | Что получаете | Что теряете |
|--------|----------------|---------------|-------------|
| 21 (Lollipop) | ~99.8% | Максимальный охват, Compose совместим | Нет runtime permissions, больше compat-кода |
| 23 (Marshmallow) | ~97.5% | Runtime Permissions нативно, минимум для многих AndroidX 2025+ | Нет multi-window, нет Java 8 streams |
| 24 (Nougat) | ~95.7% | Java 8 language features, multi-window | Нет notification channels, нет background limits |
| 26 (Oreo) | ~94.8% | Notification channels, background limits, adaptive icons | Потеря ~5% устройств (старые бюджетники) |
| 29 (Android 10) | ~89% | Scoped Storage, Dark Theme, security patches | Потеря ~11% устройств |

### Рекомендации по ситуации

**Новый проект (2026):**
- **minSdk 26** — оптимальный баланс. Notification channels — обязательны. Background limits — out of the box. Охват ~95%.
- **minSdk 24** — если важен максимальный охват, особенно для emerging markets (Африка, Юго-Восточная Азия).

**Существующий проект:**
- Проверьте в Google Play Console раздел «Android Vitals → Devices» — какой процент ваших пользователей на каждом API level.
- Если < 2% пользователей на API ниже 26, безопасно поднимать minSdk.

**Безопасность (OWASP рекомендация):**
- minSdk 29 — устройства ниже Android 10 не получают security patches от Google. Если приложение работает с чувствительными данными (финансы, здоровье), рассмотрите этот порог.

---

## targetSdk: требования Google Play

### Таймлайн обязательных обновлений

| Дедлайн | Требование | Что нужно сделать |
|---------|------------|-------------------|
| 31 авг 2025 | Новые приложения и обновления: targetSdk >= 35 | Поддержка edge-to-edge, 16 KB pages |
| 31 авг 2025 | Существующие приложения: targetSdk >= 34 | Иначе скрытие от пользователей Android 15+ |
| 1 ноя 2025 | Расширенный дедлайн (по запросу) | Запрос через Play Console |
| ~авг 2026 (ожид.) | targetSdk >= 36 (прогноз) | Adaptive layouts, ProgressStyle |

**Важно:** Google не устанавливает требований к minSdk — только к targetSdk.

### Поведенческие изменения при повышении targetSdk

Каждый targetSdk level активирует новые behavioral changes только когда приложение явно заявляет этот target:

| targetSdk | Что меняется |
|-----------|-------------|
| 23 | Runtime Permissions обязательны |
| 26 | Background services ограничены, channels обязательны |
| 28 | Cleartext HTTP запрещён по умолчанию |
| 29 | Scoped Storage, ограничен доступ к location в фоне |
| 30 | Package visibility фильтрация |
| 31 | Pending Intent mutability обязательна, foreground service type |
| 33 | `POST_NOTIFICATIONS` разрешение |
| 34 | Foreground service type обязателен при объявлении |
| 35 | Edge-to-edge принудительно, predictive back animations |
| 36 | Orientation/resize restrictions сняты на sw >= 600dp |
| 37* | Ещё более строгие adaptive layout, lock-free MessageQueue |

### Стратегия обновления targetSdk

```
1. Читать release notes: developer.android.com/about/versions/XX/behavior-changes-XX
2. Обновить compileSdk до нового уровня
3. Запустить тесты (unit + UI) — поймать compile errors
4. Поднять targetSdk
5. Тестировать на устройстве / эмуляторе с новым API level
6. Обратить внимание на deprecation warnings
7. Выпустить в closed testing → open testing → production
```

---

## compileSdk vs targetSdk vs minSdk

### Определения

```
compileSdk  — версия SDK, против которой компилируется код
              (какие API видит компилятор)

targetSdk   — заявленная целевая версия
              (какие behavioral changes система применяет)

minSdk      — минимальная версия для установки
              (APK не встанет на устройство ниже этого уровня)
```

### Визуальная схема

```
API Level:  21  23  26  29  33  34  35  36  37
             │                           │
             ▼                           ▼
          minSdk=26                 compileSdk=36
             │         targetSdk=36      │
             │              │            │
             ▼              ▼            ▼
         ┌───────────────────────────────────┐
         │   minSdk ≤ targetSdk ≤ compileSdk │  ← ПРАВИЛО
         └───────────────────────────────────┘

Устройство пользователя:
  API < minSdk  → приложение не устанавливается
  API >= minSdk → приложение работает
  API > targetSdk → система включает compatibility behaviors
```

### Частые ошибки

| Ошибка | Проблема | Решение |
|--------|----------|---------|
| `compileSdk < targetSdk` | Gradle ошибка, не скомпилируется | compileSdk >= targetSdk всегда |
| `targetSdk = compileSdk`, но не тестировали | Behavioral changes ломают приложение | Тестировать на устройстве с этим API level |
| `compileSdk` не обновляют | Нет доступа к новым API, lint warnings | Обновлять compileSdk при каждом релизе SDK |
| `minSdk` слишком низкий | Куча compat-кода, трудно тестировать | Анализировать аудиторию в Play Console |

### Пример build.gradle.kts (февраль 2026)

```kotlin
android {
    compileSdk = 36  // Последний стабильный

    defaultConfig {
        minSdk = 26      // Oreo — оптимальный баланс
        targetSdk = 36   // Актуальное требование Play
    }
}
```

---

## Android 16 (API 36): ключевые фичи

Android 16 вышел 10 июня 2025. Кодовое имя — **Baklava**. Главные изменения:

### ProgressStyle Notifications (Live Updates)
Новый стиль уведомлений `Notification.ProgressStyle` для отслеживания пользовательских сценариев: поездка в такси, доставка, навигация. Поддерживает Points (этапы) и Segments (отрезки прогресса).

### Health Connect + FHIR
Медицинские записи в формате FHIR (Fast Healthcare Interoperability Resources) — стандарт обмена медицинскими данными. Разрешения: `READ_MEDICAL_DATA_IMMUNIZATION`, `WRITE_MEDICAL_DATA`. Начальная поддержка — записи о вакцинации.

### Adaptive Layout Enforcement
Для приложений с targetSdk 36 на экранах sw >= 600dp: игнорируются `screenOrientation`, `resizeableActivity=false`, ограничения aspect ratio. Приложение заполняет всё окно. Это требует адаптации UI для планшетов и складных устройств.

### APV Codec (Advanced Professional Video)
Новый видеокодек `MIMETYPE_VIDEO_APV` для профессиональной съёмки — поддержка до 8K при битрейте до 2 Гбит/с.

### Camera API: профессиональные функции
- Hybrid Auto-Exposure с приоритетом ISO
- Точная настройка цветовой температуры (`COLOR_CORRECTION_MODE_CCT`)
- Night mode detection для camera extensions
- Motion Photo Capture API

### Другие заметные API
- **RuntimeColorFilter / RuntimeXfermode** — кастомные графические эффекты через AGSL
- **RangingManager** — универсальный API для BLE/UWB/Wi-Fi RTT измерения расстояний
- **Vertical Text** — поддержка вертикального текста для CJK
- **KeyStoreManager** — sharing криптоключей между приложениями
- **Adaptive Refresh Rate** — API для динамической частоты обновления дисплея

---

## Android 17 (API 37): предварительный обзор

Beta 1 выпущена 13 февраля 2026. Google заменил Developer Previews на модель **Canary builds** (непрерывные обновления между бетами). Стабильный релиз ожидается в Q2 2026.

### Подтверждённые фичи

**Handoff API** — перенос активности приложения между устройствами Android (аналог Apple Handoff). Разработчики могут интегрировать cross-device continuity.

**Generational GC** — ART получает generational сборку мусора для Concurrent Mark-Compact collector. Более частые, менее затратные young-generation коллекции.

**Lock-free MessageQueue** — новая реализация `android.os.MessageQueue` без блокировок. Уменьшает пропущенные кадры. Ломает приложения, использующие reflection на приватные поля MessageQueue.

**VVC (H.266) Codec** — следующее поколение видеокодека после HEVC.

**Camera Session Transitions** — `updateOutputConfigurations()` позволяет переключать режимы камеры без перезапуска CameraCaptureSession.

**Advanced Protection Mode** — `AdvancedProtectionManager` API для обнаружения усиленного режима безопасности.

**Adaptive Layout (окончательно)** — убран developer opt-out для ограничений ориентации на больших экранах. В API 36 был opt-out, в 37 его больше нет.

**Профилирование** — новые триггеры в `ProfilingManager`: `TRIGGER_TYPE_COLD_START`, `TRIGGER_TYPE_OOM`, `TRIGGER_TYPE_KILL_EXCESSIVE_CPU_USAGE`.

### Таймлайн Android 17

| Этап | Дата |
|------|------|
| Canary builds | с января 2026 |
| Beta 1 | 13 февраля 2026 |
| Beta 2-3 | март–апрель 2026 (ожид.) |
| Stable | июнь 2026 (ожид.) |
| Minor release | Q4 2026 (ожид.) |

---

## Проверь себя

**Q1: Чем targetSdk отличается от compileSdk?**

compileSdk определяет, какие API доступны компилятору — он влияет только на этап сборки. targetSdk сообщает системе Android, под какую версию приложение разработано и протестировано. Система использует targetSdk для решения: применять ли новые поведенческие изменения (behavioral changes) или включить режим совместимости. Правило: `minSdk <= targetSdk <= compileSdk`.

**Q2: Приложение с targetSdk 33 запускается на устройстве с Android 16 (API 36). Нужно ли оно обрабатывать adaptive layout enforcement?**

Нет. Adaptive layout enforcement (снятие ограничений ориентации на sw >= 600dp) применяется только к приложениям с targetSdk >= 36. Приложение с targetSdk 33 получит compatibility behavior — его orientation restrictions будут работать как раньше. Но для публикации обновления в Google Play потребуется поднять targetSdk до актуального уровня.

**Q3: Почему OWASP рекомендует minSdk 29, а большинство проектов используют 26?**

OWASP рекомендует minSdk 29 (Android 10) из соображений безопасности: устройства ниже Android 10 больше не получают security patches от Google. Для приложений с чувствительными данными (финтех, здоровье) это оправдано. Однако minSdk 26 охватывает ~95% устройств и даёт notification channels, background limits — достаточно для большинства consumer-приложений. Решение зависит от risk profile конкретного продукта.

---

## Ключевые карточки

**Карточка 1: API level**
**Вопрос:** Что определяет API level?
**Ответ:** API level — целочисленный идентификатор, однозначно определяющий набор framework API, доступных в конкретной версии Android. Каждый новый API level добавляет API и может менять поведение системы. Пример: API 36 = Android 16 (Baklava).

**Карточка 2: Behavioral changes**
**Вопрос:** Когда применяются behavioral changes нового API level?
**Ответ:** Behavioral changes делятся на два типа: (1) для всех приложений, запущенных на новой версии Android — применяются независимо от targetSdk; (2) для приложений, targeting новый API level — применяются только при targetSdk >= этого уровня. Второй тип даёт время на миграцию.

**Карточка 3: Google Play targetSdk deadline**
**Вопрос:** Какой targetSdk обязателен для публикации обновлений в Google Play (2025)?
**Ответ:** С 31 августа 2025: новые приложения и обновления — targetSdk >= 35 (Android 15). Существующие приложения без обновлений — targetSdk >= 34, иначе скрываются от пользователей Android 15+. Расширенный дедлайн — 1 ноября 2025 по запросу.

**Карточка 4: Scoped Storage**
**Вопрос:** Как менялся Scoped Storage от API 29 до API 30?
**Ответ:** API 29: Scoped Storage введён, но приложения могли использовать `requestLegacyExternalStorage=true` для opt-out. API 30: этот флаг перестаёт работать для targetSdk >= 30, Scoped Storage принудителен. Доступ к чужим файлам — только через SAF или MediaStore.

**Карточка 5: compileSdk best practice**
**Вопрос:** Какой compileSdk выбирать?
**Ответ:** Всегда последний стабильный. В феврале 2026 — compileSdk = 36 (Android 16). Это даёт доступ к новейшим API, актуальные lint-проверки и лучшую совместимость с Gradle plugin. compileSdk не влияет на runtime-поведение — только на этап компиляции.

---

## Куда дальше

- [[android-overview]] — общая архитектура Android и компонентная модель
- [[android-manifest]] — как `<uses-sdk>` определяет minSdk/targetSdk в манифесте
- [[android-permissions-security]] — runtime permissions (API 23+) и новые модели доступа
- [[android-notifications]] — notification channels (API 26+) и ProgressStyle (API 36+)
- [[android-compose]] — Jetpack Compose (минимум API 21, рекомендуется API 24+)

---

## Источники

- [Android API Levels — apilevels.com](https://apilevels.com/) — кумулятивное распределение по API levels
- [Android version history — Wikipedia](https://en.wikipedia.org/wiki/Android_version_history) — полная история версий
- [Android 16 Features and APIs — developer.android.com](https://developer.android.com/about/versions/16/features) — официальная документация API 36
- [Android 16 Behavior Changes — developer.android.com](https://developer.android.com/about/versions/16/behavior-changes-16) — поведенческие изменения для targetSdk 36
- [The First Beta of Android 17 — Android Developers Blog](https://android-developers.googleblog.com/2026/02/the-first-beta-of-android-17.html) — анонс Android 17 Beta 1
- [Target API level requirements — Google Play Console Help](https://support.google.com/googleplay/android-developer/answer/11926878) — дедлайны targetSdk
- [Meet Google Play's target API level requirement — developer.android.com](https://developer.android.com/google/play/requirements/target-sdk) — руководство по обновлению
- [Android Distribution Chart — composables.com](https://composables.com/android-distribution-chart) — визуализация распределения
- [AppBrain Android version stats](https://www.appbrain.com/stats/top-android-sdk-versions) — актуальная статистика по версиям
- [OWASP MASTG-BEST-0010: minSdkVersion](https://mas.owasp.org/MASTG/best-practices/MASTG-BEST-0010/) — рекомендации по безопасности

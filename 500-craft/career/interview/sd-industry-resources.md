---
title: "Mobile System Design: Engineering Blog Posts"
created: 2026-02-14
modified: 2026-02-14
type: reference
status: published
confidence: high
tags:
  - topic/career
  - type/reference
  - level/advanced
  - interview
  - system-design
related:
  - "[[system-design-android]]"
  - "[[android-networking]]"
  - "[[caching-strategies]]"
  - "[[architecture-resilience-patterns]]"
prerequisites:
  - "[[system-design-android]]"
reading_time: 8
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Mobile System Design: Engineering Blog Posts

Курированная подборка статей из инженерных блогов ведущих компаний. Каждая статья описывает реальные trade-offs и архитектурные решения — идеальный материал для подготовки к System Design интервью.

> Большой список корпоративных блогов: [engineering-blogs](https://github.com/sumodirjo/engineering-blogs)

---

## По темам

### Backend API Design

| Компания | Статья | Ключевая идея |
|----------|--------|---------------|
| Airbnb | [How Airbnb is Moving 10x Faster at Scale with GraphQL and Apollo](https://medium.com/airbnb-engineering/how-airbnb-is-moving-10x-faster-at-scale-with-graphql-and-apollo-aa4ec92d69e2) | Миграция на GraphQL для ускорения разработки |
| Instacart | [Building Instacart's view model API — Part 1](https://tech.instacart.com/building-instacarts-view-model-api-part-1-why-view-model-4362f64ffd2a) | View Model API на серверной стороне |
| Slack | [How We Design Our APIs at Slack](https://slack.engineering/how-we-design-our-apis-at-slack/) | Принципы проектирования API |
| Slack | [Evolving API Pagination at Slack](https://slack.engineering/evolving-api-pagination-at-slack/) | Эволюция подходов к пагинации |
| Trello | [Adopting GraphQL and Apollo in a Legacy Application](https://tech.trello.com/adopting-graphql-and-apollo/) | Интеграция GraphQL в legacy |
| Twitter | [Pagination Overview](https://developer.twitter.com/en/docs/twitter-api/pagination) | Cursor-based пагинация в продакшене |

→ Связано: [[api-design]], [[api-rest-deep-dive]], [[api-graphql-deep-dive]]

### Caching & Offline

| Компания | Статья | Ключевая идея |
|----------|--------|---------------|
| Instagram | [Building an Open Source, Carefree Android Disk Cache](https://instagram-engineering.com/building-an-open-source-carefree-android-disk-cache-af57aa9b7c7) | Disk cache для Android |
| Trello | [Airplane Mode: Enabling Trello Mobile Offline](https://tech.trello.com/sync-architecture/) | Архитектура offline sync |
| Trello | [Syncing Changes](https://tech.trello.com/syncing-changes/) | Механика синхронизации |
| Trello | [Sync Failure Handling](https://tech.trello.com/sync-failure-handling/) | Обработка ошибок sync |
| Trello | [The Two ID Problem](https://tech.trello.com/sync-two-id-problem/) | Проблема локальных vs серверных ID |
| Trello | [Offline Attachments](https://tech.trello.com/sync-offline-attachments/) | Вложения в offline |
| Trello | [Sync is a Two-Way Street](https://tech.trello.com/sync-downloads/) | Двусторонняя синхронизация |
| Trello | [Displaying Sync State](https://tech.trello.com/sync-indicators/) | UI индикаторы sync |

→ Связано: [[caching-strategies]], [[android-data-persistence]], [[android-room-deep-dive]]

### Networking & Performance

| Компания | Статья | Ключевая идея |
|----------|--------|---------------|
| Dropbox | [Making camera uploads for Android faster and more reliable](https://dropbox.tech/mobile/making-camera-uploads-for-android-faster-and-more-reliable) | Оптимизация загрузки медиа |
| Instagram | [Improving performance with background data prefetching](https://instagram-engineering.com/improving-performance-with-background-data-prefetching-b191acb39898) | Prefetching для UX |
| Instagram | [Making Direct Messages Reliable and Fast](https://instagram-engineering.com/making-direct-messages-reliable-and-fast-a152bdfd697f) | Надёжность real-time сообщений |
| LinkedIn | [Building a smooth Stories experience on iOS](https://engineering.linkedin.com/blog/2020/building-stories-on-ios) | Stories: производительность |
| Uber | [How Uber's New Driver App Overcomes Network Lag](https://eng.uber.com/driver-app-optimistic-mode/) | Optimistic UI updates |

→ Связано: [[android-networking]], [[android-app-startup-performance]], [[performance-optimization]]

### Networking & Reliability

| Компания | Статья | Ключевая идея |
|----------|--------|---------------|
| Snapchat | [QUIC at Snapchat](https://eng.snap.com/quic-at-snap) | Внедрение QUIC протокола |
| Uber | [Engineering Failover Handling in Uber's Mobile Networking](https://eng.uber.com/eng-failover-handling/) | Failover стратегии |
| Uber | [Employing QUIC Protocol to Optimize Uber's App Performance](https://eng.uber.com/employing-quic-protocol/) | QUIC для производительности |

→ Связано: [[architecture-resilience-patterns]], [[network-fundamentals-for-developers]]

### Server-Driven UI

| Компания | Статья | Ключевая идея |
|----------|--------|---------------|
| Airbnb | [A Deep Dive into Airbnb's Server-Driven UI System](https://medium.com/airbnb-engineering/a-deep-dive-into-airbnbs-server-driven-ui-system-842244c5f5) | SDUI архитектура в масштабе |
| DoorDash | [Improving Development Velocity with Generic, Server-Driven UI Components](https://doordash.engineering/2021/08/24/improving-development-velocity-with-generic-server-driven-ui-components/) | Ускорение разработки через SDUI |
| Uber | [Building the New Uber Freight App as Lists of Modular, Reusable Components](https://eng.uber.com/uber-freight-app-architecture-design/) | Модульные UI компоненты |
| Uber | [Architecting Driver Preferences with RIBs](https://eng.uber.com/carbon-driver-app-preferences-ribs/) | RIBs архитектура |

### Build & Platform

| Компания | Статья | Ключевая идея |
|----------|--------|---------------|
| Airbnb | [Designing for Productivity in a Large-Scale iOS Application](https://medium.com/airbnb-engineering/designing-for-productivity-in-a-large-scale-ios-application-9376a430a0bf) | Масштабирование iOS-проекта |
| Facebook | [Rethinking Android app compilation with Buck](https://engineering.fb.com/2017/11/09/android/rethinking-android-app-compilation-with-buck/) | Альтернативная система сборки |
| Pinterest | [Developing fast & reliable iOS builds at Pinterest](https://medium.com/pinterest-engineering/developing-fast-reliable-ios-builds-at-pinterest-part-one-cb1810407b92) | Ускорение CI/CD для iOS |
| Reddit | [iOS and Bazel at Reddit: A Journey](https://www.reddit.com/r/RedditEng/comments/syz5dw/ios_and_bazel_at_reddit_a_journey/) | Миграция на Bazel |
| Uber | [The Journey To Android Monorepo](https://eng.uber.com/android-engineering-code-monorepo/) | Монорепозиторий для Android |

→ Связано: [[android-gradle-fundamentals]], [[android-compilation-pipeline]], [[android-ci-cd]]

### Emerging Markets

| Компания | Статья | Ключевая идея |
|----------|--------|---------------|
| Facebook | [How we built Facebook Lite for every Android phone](https://engineering.fb.com/2016/03/09/android/how-we-built-facebook-lite-for-every-android-phone-and-network/) | Lite-версия для слабых устройств |
| Microsoft | [Microsoft Teams — Designing for Emerging Markets](https://medium.com/microsoft-mobile-engineering/microsoft-teams-designing-for-emerging-markets-part-1-network-profile-2daeaa09f313) | Network profile для развивающихся рынков |
| Spotify | [How We Built It: Spotify Lite, One Year Later](https://engineering.atspotify.com/2020/12/how-we-built-it-spotify-lite-one-year-later/) | Spotify Lite — результаты |
| Uber | [Expanding Access: Engineering Uber Lite](https://eng.uber.com/engineering-uber-lite/) | Uber Lite для emerging markets |

### A/B Testing

| Компания | Статья | Ключевая идея |
|----------|--------|---------------|
| Netflix | [It's All A/Bout Testing: The Netflix Experimentation Platform](https://netflixtechblog.com/its-all-a-bout-testing-the-netflix-experimentation-platform-4e1ca458c15) | A/B тестирование в масштабе |

---

## По компаниям

### Uber
Одна из самых открытых компаний по мобильной инженерии:
- Optimistic UI, QUIC, Failover, Monorepo, RIBs, Server-Driven UI, Lite
- [Все мобильные статьи Uber](https://eng.uber.com/category/articles/mobile/)

### Instagram
Фокус на производительности и кэшировании:
- Disk cache, Prefetching, Reliable messaging
- [iOS](https://instagram-engineering.com/tagged/ios) | [Android](https://instagram-engineering.com/tagged/android)

### Trello
Лучший открытый ресурс по offline-first архитектуре (7 статей):
- Sync architecture, Failure handling, Two ID problem, Offline attachments
- [Все статьи](https://tech.trello.com/)

### Airbnb
GraphQL, Server-Driven UI, масштабная iOS разработка:
- [Все мобильные статьи](https://medium.com/airbnb-engineering/tagged/mobile)

### Другие
- [Dropbox](https://dropbox.tech/mobile) — загрузка медиа
- [Square/Cash App](https://code.cash.app) — финтех мобильная разработка
- [Reddit](https://www.redditinc.com/blog/topic/technology) — Bazel, масштабирование
- [Lyft Mobile Podcast](https://podcasts.apple.com/us/podcast/lyft-mobile/id1453587931) — аудио формат

---

## Как использовать для подготовки

1. **Перед интервью в конкретную компанию** — прочитай их блог, чтобы понимать стек и подходы
2. **При изучении темы** — найди 2-3 статьи по теме, сравни подходы разных компаний
3. **Для примеров на интервью** — "В статье Instagram Engineering описано, как они решали проблему prefetching..."
4. **Mock-practice** — возьми архитектуру из статьи и попробуй спроектировать аналог

---

## Проверь себя

> [!question]- Почему блог-посты инженерных команд полезнее учебников для подготовки к SD интервью?
> Блог-посты описывают реальные trade-offs в продакшен-системах: конкретные числа, метрики, неудачные решения и их исправления. Учебники дают теорию, а блоги — контекст. На интервью ценится именно "thinking from first principles" с реальными примерами.

> [!question]- Назови 3 компании с лучшей документацией по offline-first мобильной архитектуре.
> 1) Trello — серия из 7 статей покрывающих все аспекты sync (архитектура, конфликты, Two ID problem, offline attachments). 2) Instagram — disk cache, prefetching. 3) Uber — optimistic UI, failover handling.

> [!question]- Что такое Server-Driven UI и какие компании его активно используют?
> SDUI — подход, при котором сервер определяет структуру и содержимое UI (не только данные, но и layout). Компоненты рендерятся на клиенте по серверной схеме. Активно используют: Airbnb (полная SDUI система), DoorDash (generic UI components), Uber (RIBs + Freight). Преимущества: быстрый rollout, A/B тесты без релиза, единообразие iOS/Android.

---

## Ключевые карточки

Зачем читать engineering blogs перед SD интервью?
?
1) Реальные trade-offs (не теоретические). 2) Понимание стека конкретной компании. 3) Примеры для аргументации решений ("Instagram решает это через prefetching"). 4) Актуальные подходы (SDUI, QUIC, offline-first).

Лучший открытый ресурс по offline-first?
?
Trello engineering blog — серия из 7 статей: sync architecture, syncing changes, failure handling, Two ID problem, offline attachments, downloads, sync indicators.

Какие компании активно используют Server-Driven UI?
?
Airbnb (полная SDUI система), DoorDash (generic components), Uber (RIBs + Freight modular components). SDUI позволяет обновлять UI без релиза приложения.

Uber engineering blog — какие мобильные темы покрывает?
?
Optimistic UI (network lag), QUIC protocol, Failover handling, Android monorepo, RIBs architecture, Server-Driven UI (Freight), Uber Lite (emerging markets).

---

## Куда дальше

| Направление | Тема | Ссылка |
|------------|------|--------|
| Framework | Mobile System Design framework | [[system-design-android]] |
| Упражнение | Chat App design | [[sd-exercise-chat-app]] |
| Упражнение | Caching Library design | [[sd-exercise-caching-library]] |
| Deep dive | Стратегии кэширования | [[caching-strategies]] |
| Deep dive | Паттерны устойчивости | [[architecture-resilience-patterns]] |

---

## Источники

- [iartr/mobile-system-design — BLOGPOSTS.MD](https://github.com/iartr/mobile-system-design/blob/master/BLOGPOSTS.MD)
- [weeeBox/mobile-system-design](https://github.com/weeeBox/mobile-system-design) — оригинальный репозиторий
- [Server-driven UI strategies discussion](https://github.com/MobileNativeFoundation/discussions/discussions/47)
- [Monorepo discussion](https://github.com/MobileNativeFoundation/discussions/discussions/31)

---

*Обновлено: 2026-02-14*

---
title: "Content Backlog: реестр пробелов и задач"
created: 2026-02-13
modified: 2026-02-14
type: reference
status: published
tags:
  - system/guidelines
  - system/metadata
---

# Content Backlog

> Живой документ: реестр пробелов в покрытии, недоработок и задач по улучшению vault.
> Обновляется при каждой обработке файлов. Задачи вне текущего scope — фиксируются здесь.

---

## Приоритет: Высокий

### Области с недостаточным покрытием

- [ ] **Programming**: 0 beginner-файлов, 0 advanced — вся область intermediate (12 файлов)
- [ ] **Operating Systems**: 8 файлов на всю тему, 0 advanced, 88% intermediate
- [ ] **Cloud**: 7 файлов — AWS, GCP частично, Azure отсутствует. 0 advanced
- [ ] **Security**: 0 advanced-файлов (19 файлов, все beginner/intermediate)
- [ ] **Thinking & Learning**: 22 файла, 100% intermediate — нет beginner/advanced/expert

### Missing beginner-контент (входные точки)

- [ ] Career: 0 beginner — нет "с чего начать карьеру в IT"
- [ ] CS Foundations (KMP): 0 beginner — нет вводного материала
- [ ] Programming: 0 beginner — нет "основы для начинающих"
- [ ] Thinking & Learning: 0 beginner — нет вводного материала

### Missing expert-контент (глубина)

14 областей без expert-уровня:
- [ ] AI/ML, Architecture, Career, Communication
- [ ] Cross-Platform, Databases, iOS, JVM
- [ ] KMP, Leadership, Networking, Programming
- [ ] Security, Thinking & Learning

---

## Приоритет: Средний

### Missing Learning Paths

**Существующие learning paths (11):**
- По областям (6): Android, iOS, JVM, KMP, CS Fundamentals, CS Foundations
- Интерливинг (5): Backend Engineer, Mobile Expert, Interview Prep, Tech Lead, Full Stack Foundation

**Покрытие через интерливинг-пути:**
- [x] Architecture — через Backend Engineer + Tech Lead
- [x] Databases — через Backend Engineer + Full Stack Foundation
- [x] Security — через Backend Engineer + Full Stack Foundation
- [x] DevOps — через Backend Engineer
- [x] Cloud — через Backend Engineer + Full Stack Foundation
- [x] Networking — через Backend Engineer + Full Stack Foundation
- [x] Programming — через Full Stack Foundation
- [x] Operating Systems — через Full Stack Foundation
- [x] Career — через Interview Prep + Tech Lead
- [x] Leadership — через Tech Lead
- [x] Communication — через Tech Lead
- [x] Cross-Platform — через Mobile Expert

**Остаются без отдельного пути (покрыты интерливингом):**
- [ ] AI/ML — нет отдельного learning path (ни прямого, ни через интерливинг)
- [ ] Thinking & Learning — нет отдельного learning path

### Missing Cross-Domain Links

Обнаруженные при обработке файлов (обновляется):

- [ ] android-networking → network-http-evolution, security-https-tls
- [ ] kotlin-coroutines → concurrency-vs-parallelism, jvm-executors-futures
- [ ] ai-cost-optimization → cloud-serverless-patterns, performance-optimization
- [ ] android-data-persistence → mobile-databases-complete, databases-fundamentals-complete
- [ ] ios-networking → network-http-evolution, security-https-tls
- [ ] android-compose → ios-swiftui (cross-platform comparison)
- [ ] authentication-authorization → api-design
- [ ] caching-strategies → databases-fundamentals-complete
- [ ] event-driven-architecture → kubernetes-advanced

*(Список пополняется при обработке файлов в Фазах 2-4)*

---

## Приоритет: Низкий

### Области с перекосом уровней

- [ ] Cross-Platform: 96% intermediate — нужны advanced/expert файлы
- [ ] Programming: 100% intermediate — нужны beginner/advanced
- [ ] Thinking & Learning: 100% intermediate — нужны beginner/advanced
- [ ] Operating Systems: 88% intermediate — нужны advanced

### Потенциальные новые темы

- [ ] Web Development (Frontend/Backend) — отсутствует полностью
- [ ] Data Engineering — отсутствует
- [ ] Rust / Go / Python — другие языки кроме Kotlin/Java
- [ ] System Design (отдельная область, не только интервью)

---

## Files Below Standard

*(Обнаруженные при обработке — обновляется)*

| Файл | Проблема | Приоритет |
|------|----------|-----------|

---

## Устаревший контент

*(Файлы с прошедшим review_date — обновляется)*

| Файл | review_date | Статус |
|------|-------------|--------|

---

## Статистика

| Метрика | Значение |
|---------|----------|
| Всего задач | ~35 |
| Высокий приоритет | ~9 |
| Средний приоритет | ~14 |
| Низкий приоритет | ~12 |
| Последнее обновление | 2026-02-14 |

---

*Создано: 2026-02-13*

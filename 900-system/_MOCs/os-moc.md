---
title: "OS MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/operating-systems
  - type/moc
  - navigation
---
# OS MOC

> Операционные системы: от процессов и потоков до файловых систем и виртуализации.

---

## Рекомендуемый путь изучения

```
1. [[os-overview]]              — Карта раздела, обзор ОС
         ↓
2. [[os-processes-threads]]     — Процессы, потоки, context switch
         ↓
3. [[os-scheduling]]            — Планирование: FIFO, Round Robin, CFS
         ↓
4. [[os-synchronization]]       — Mutex, semaphore, deadlock, lock-free
         ↓
5. [[os-memory-management]]     — Виртуальная память, paging, TLB
         ↓
6. [[os-file-systems]]          — Хранение данных: ext4, APFS, journaling
         ↓
7. [[os-io-devices]]            — I/O: polling, interrupts, DMA
         ↓
8. [[os-virtualization]]        — VM, hypervisors, контейнеры, Docker
```

---

## Статьи по категориям

### Обзор
- [[os-overview]] — карта раздела, роль ОС как абстракции над железом

### Процессы и потоки
- [[os-processes-threads]] — процессы, потоки, fork/exec, context switch, green threads
- [[os-scheduling]] — алгоритмы планирования: FIFO, SJF, Round Robin, CFS (Linux), priority scheduling

### Синхронизация
- [[os-synchronization]] — mutex, semaphore, monitor, deadlock (4 условия Coffman), lock-free и wait-free алгоритмы

### Память
- [[os-memory-management]] — виртуальная память, paging, page table, TLB, swap, OOM killer, memory-mapped files

### Файловые системы
- [[os-file-systems]] — файловые системы (ext4, APFS, NTFS), inode, journaling, RAID, SSD vs HDD

### Ввод/Вывод
- [[os-io-devices]] — I/O модели: blocking, non-blocking, polling, interrupts, DMA, io_uring (Linux)

### Виртуализация
- [[os-virtualization]] — Type 1/2 hypervisors, VM vs контейнеры, Docker, cgroups, namespaces

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| Process vs Thread | Процесс = изолированное выполнение; Поток = легковесная единица внутри процесса | [[os-processes-threads]] |
| Context Switch | Сохранение/восстановление состояния CPU при переключении между задачами (~1-10 мкс) | [[os-scheduling]] |
| Deadlock | Взаимная блокировка: A ждёт B, B ждёт A; 4 условия Coffman | [[os-synchronization]] |
| Virtual Memory | Каждый процесс видит своё адресное пространство; ОС транслирует через page table | [[os-memory-management]] |
| Page Fault | Обращение к странице, которой нет в RAM → загрузка с диска (медленно) | [[os-memory-management]] |
| Journaling | Журналирование операций ФС для восстановления после сбоя | [[os-file-systems]] |
| DMA | Direct Memory Access: устройство пишет в RAM напрямую, без участия CPU | [[os-io-devices]] |
| Containers | Изоляция через cgroups + namespaces: легче VM, быстрый старт | [[os-virtualization]] |

## Связанные области

- [[jvm-moc]] — JVM управляет памятью и потоками поверх ОС
- [[cs-foundations-moc]] — низкоуровневые основы: память, компиляция, concurrency
- [[devops-moc]] — Docker и Kubernetes используют виртуализацию ОС

# Research Report: OS Fundamentals for Developers

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Операционная система управляет hardware и предоставляет абстракции программам. Kernel mode (ring 0) — полный доступ к hardware. User mode (ring 3) — ограниченный доступ. System calls — контролируемый интерфейс между user space и kernel. Переход user→kernel (mode switch) быстрее, чем context switch между процессами. Virtual memory изолирует процессы. Fork/exec создают процессы в Unix.

## Key Findings

### 1. Kernel vs User Mode

**Kernel mode (Ring 0):**
- Полный доступ к hardware
- Может выполнять любые инструкции
- Управляет памятью, процессами, I/O
- Ошибка → crash всей системы

**User mode (Ring 3):**
- Ограниченный доступ
- Не может напрямую обращаться к hardware
- Изолирован от других процессов
- Ошибка → crash только процесса

### 2. System Calls

**Определение:**
Интерфейс для запроса сервисов kernel из user space.

**Как работает:**
1. Программа выполняет инструкцию syscall/int 0x80
2. CPU переключается в kernel mode
3. Kernel выполняет запрошенную операцию
4. Результат возвращается, CPU → user mode

**Примеры syscalls:**
| Категория | Syscalls |
|-----------|----------|
| Файлы | open, read, write, close |
| Процессы | fork, exec, wait, exit |
| Память | mmap, brk |
| Сеть | socket, connect, send, recv |
| Время | gettimeofday |

### 3. Mode Switch vs Context Switch

**Mode switch:**
- User → Kernel → User
- Тот же процесс
- Быстрее (~100-1000 ns)
- Сохранение минимального контекста

**Context switch:**
- Процесс A → Процесс B
- Полное сохранение/восстановление состояния
- Дороже (~1-10 μs)
- Смена address space, регистров, стека

### 4. Virtual Memory

**Изоляция:**
- Каждый процесс видит свой address space
- Не может читать/писать память другого процесса
- Page fault при доступе к невыделенной памяти

**Механизм:**
- Page tables: virtual → physical address
- TLB (Translation Lookaside Buffer): cache для page tables
- Demand paging: страницы загружаются по требованию

### 5. Process Management

**Process Control Block (PCB):**
- PID (process ID)
- Состояние (running, waiting, etc.)
- Регистры
- Память (page tables)
- Открытые файлы

**Fork/Exec (Unix):**
- fork(): создаёт копию процесса
- exec(): заменяет код новой программой
- fork() + exec() = запуск новой программы

### 6. vDSO: быстрые syscalls

Некоторые syscalls не требуют перехода в kernel:
- gettimeofday
- clock_gettime

Kernel mapping часть кода в user space → вызов без overhead.

## Community Sentiment

### Positive
- Понимание OS помогает отладке
- Объясняет performance характеристики
- Важно для системного программирования

### Negative
- Сложная тема
- Детали зависят от ОС
- Редко нужно application developers

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Wikipedia: System Call](https://en.wikipedia.org/wiki/System_call) | Reference | ★★★★★ | Overview |
| [Form3: Linux Fundamentals](https://www.form3.tech/blog/engineering/linux-fundamentals-user-kernel-space) | Blog | ★★★★★ | Practical |
| [Linux Kernel Labs: Syscalls](https://linux-kernel-labs.github.io/refs/heads/master/lectures/syscalls.html) | Official | ★★★★★ | Deep dive |
| [GeeksforGeeks: System Call](https://www.geeksforgeeks.org/operating-systems/introduction-of-system-call/) | Tutorial | ★★★★☆ | Clear examples |
| [The Skilled Coder: OS Fundamentals](https://theskilledcoder.com/posts/fundamental-concepts/operating-system-fundamentals/) | Blog | ★★★★☆ | For developers |

## Research Methodology
- **Queries used:** 2 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **Focus areas:** Syscalls, kernel/user mode, virtual memory

---

*Проверено: 2026-01-09*

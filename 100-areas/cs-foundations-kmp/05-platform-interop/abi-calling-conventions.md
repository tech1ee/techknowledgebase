---
title: "ABI и Calling Conventions: как бинарный код общается"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, platform-interop, abi, calling-conventions, low-level]
related:
  - "[[memory-model-fundamentals]]"
  - "[[native-compilation-llvm]]"
  - "[[ffi-foreign-function-interface]]"
---

# ABI и Calling Conventions: как бинарный код общается

> **TL;DR:** ABI (Application Binary Interface) — контракт между скомпилированным кодом и операционной системой. Calling convention определяет: в каких регистрах передавать аргументы, кто очищает стек, какие регистры сохраняются. x86-64 System V (Linux/macOS): аргументы в RDI, RSI, RDX, RCX, R8, R9; возврат в RAX. ARM64 AAPCS: аргументы в X0-X7; возврат в X0. ABI stability критична для библиотек — изменение ABI требует перекомпиляции всех зависимостей.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Memory Model** | Stack vs heap, адресация | [[memory-model-fundamentals]] |
| **Native Compilation** | Как код становится машинным | [[native-compilation-llvm]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **ABI** | Бинарный контракт между программой и ОС | Стандарт размера розеток в стране |
| **Calling Convention** | Правила вызова функций | Протокол телефонного разговора: кто первый говорит, кто кладёт трубку |
| **Register** | Сверхбыстрая память в CPU | Карманы рабочего — самое доступное место |
| **Stack Frame** | Область стека для одного вызова функции | Страница в блокноте для одной задачи |
| **Caller** | Функция, которая вызывает другую | Тот, кто звонит |
| **Callee** | Функция, которую вызвали | Тот, кому звонят |

---

## ПОЧЕМУ существует ABI

### Проблема: код компилируется отдельно

Представь ситуацию: ты написал приложение на Kotlin/Native. Оно использует библиотеку, скомпилированную кем-то другим. Как твой код "общается" с библиотекой?

```
┌─────────────────────────────────────────────────────────────┐
│                    ПРОБЛЕМА БЕЗ ABI                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Твой код (Kotlin):                                        │
│   val result = someLibrary.calculate(10, 20)                │
│                                                             │
│   Библиотека (C):                                           │
│   int calculate(int a, int b) { return a + b; }             │
│                                                             │
│   ВОПРОСЫ:                                                  │
│   - Где искать аргументы 10 и 20?                          │
│   - В регистрах? В каких? В стеке?                         │
│   - Куда положить результат 30?                            │
│   - Кто должен освободить память?                          │
│                                                             │
│   Без соглашений — хаос. Код не сможет общаться.           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Аналогия: международная почта

ABI — как международные почтовые стандарты:

- **Формат адреса:** куда писать страну, индекс, город
- **Размер конверта:** стандартные размеры для автоматической сортировки
- **Язык адреса:** латиница для международных отправлений

Без этих стандартов письма бы терялись. Каждая страна изобретала бы свой формат.

### ABI vs API

Многие путают эти понятия:

| Аспект | API | ABI |
|--------|-----|-----|
| **Уровень** | Исходный код | Машинный код |
| **Что определяет** | Имена функций, типы параметров | Регистры, stack layout, name mangling |
| **Когда нужен** | При написании кода | При линковке и runtime |
| **Изменение** | Требует переписывания кода | Требует перекомпиляции |

```
┌─────────────────────────────────────────────────────────────┐
│                    API vs ABI                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   API (Source Level):                                       │
│   fun greet(name: String): String                          │
│                                                             │
│   "Функция greet принимает строку, возвращает строку"      │
│                                                             │
│   ─────────────────────────────────────────────────────    │
│                                                             │
│   ABI (Binary Level):                                       │
│   - name передаётся в регистре RDI                         │
│   - Возврат через RAX (указатель на строку)                │
│   - Символ: _Z5greetPKc (name mangling)                    │
│   - Stack alignment: 16 bytes                              │
│                                                             │
│   "КАК именно это происходит на уровне машинного кода"     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ЧТО определяет ABI

ABI — это набор соглашений о:

### 1. Calling Conventions

Как вызывать функции:
- Где передавать аргументы (регистры, стек)
- Как возвращать значения
- Кто очищает стек после вызова

### 2. Data Representation

Как представлять данные:
- Размеры примитивных типов (`int` = 4 байта)
- Alignment (выравнивание)
- Порядок байтов (endianness)
- Layout структур

### 3. Name Mangling

Как кодировать имена функций:
- C++: `greet(std::string)` → `_Z5greetNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE`
- C: `greet` → `greet` (без mangling)

### 4. Exception Handling

Как обрабатывать исключения:
- Stack unwinding
- Exception tables

### 5. System Calls

Как обращаться к ОС:
- Номера syscall
- Регистры для параметров

---

## Calling Conventions: главные варианты

### Обзор основных конвенций

| Convention | Аргументы | Очистка стека | Где используется |
|------------|-----------|---------------|------------------|
| **cdecl** | Stack (RTL) | Caller | C default, varargs |
| **stdcall** | Stack (RTL) | Callee | Win32 API |
| **fastcall** | Registers + stack | Callee | Performance-critical |
| **System V x64** | 6 регистров + stack | Caller | Linux/macOS x64 |
| **Microsoft x64** | 4 регистра + stack | Caller | Windows x64 |
| **AAPCS64** | 8 регистров + stack | Caller | ARM64 (iOS, Android) |

### cdecl (C Declaration)

Классическая конвенция для C на x86:

```
┌─────────────────────────────────────────────────────────────┐
│                    cdecl: calculate(10, 20)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Caller (вызывающий):                                      │
│   1. push 20         ; Второй аргумент в стек              │
│   2. push 10         ; Первый аргумент в стек              │
│   3. call calculate  ; Вызов функции                       │
│   4. add esp, 8      ; Caller очищает стек!                │
│                                                             │
│   Stack (до вызова):        Stack (после push):            │
│   │           │              │    20     │ ← ESP           │
│   │           │              │    10     │                  │
│   │           │              │ ret addr  │                  │
│   └───────────┘              └───────────┘                  │
│                                                             │
│   RTL = Right To Left: аргументы справа налево             │
│   Это позволяет varargs (printf)!                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Почему caller очищает стек?**

Это позволяет функции с переменным числом аргументов (varargs):

```c
printf("%d %d %d", 1, 2, 3);  // 4 аргумента
printf("%d", 42);              // 2 аргумента
```

`printf` не знает сколько аргументов получила. Только caller знает и очищает.

### stdcall (Standard Call)

Конвенция Win32 API:

```
┌─────────────────────────────────────────────────────────────┐
│                    stdcall vs cdecl                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   cdecl:                      stdcall:                      │
│   push arg2                   push arg2                     │
│   push arg1                   push arg1                     │
│   call func                   call func                     │
│   add esp, 8  ← Caller        ; Callee очищает!            │
│                               ; ret 8 внутри func           │
│                                                             │
│   Преимущество stdcall:                                     │
│   Меньше кода в caller (очистка один раз в callee)         │
│                                                             │
│   Недостаток:                                               │
│   Нельзя varargs — callee должен знать размер              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### x86-64 System V ABI (Linux/macOS)

Современная конвенция для 64-bit:

```
┌─────────────────────────────────────────────────────────────┐
│                 x86-64 System V ABI                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   INTEGER ARGUMENTS (первые 6):                             │
│   ┌─────┬─────┬─────┬─────┬─────┬─────┐                    │
│   │ RDI │ RSI │ RDX │ RCX │  R8 │  R9 │                    │
│   │ 1st │ 2nd │ 3rd │ 4th │ 5th │ 6th │                    │
│   └─────┴─────┴─────┴─────┴─────┴─────┘                    │
│   7+ аргументы → stack                                      │
│                                                             │
│   FLOATING POINT (первые 8):                                │
│   XMM0, XMM1, XMM2, XMM3, XMM4, XMM5, XMM6, XMM7           │
│                                                             │
│   RETURN VALUE:                                             │
│   RAX        — integer/pointer (64 bit)                    │
│   RAX + RDX  — 128 bit values                              │
│   XMM0       — floating point                              │
│                                                             │
│   CALLEE-SAVED (сохраняет вызываемая функция):             │
│   RBX, RBP, R12, R13, R14, R15                             │
│                                                             │
│   CALLER-SAVED (может изменить вызываемая):                │
│   RAX, RDI, RSI, RDX, RCX, R8, R9, R10, R11                │
│                                                             │
│   STACK ALIGNMENT: 16 bytes                                 │
│   RED ZONE: 128 bytes ниже RSP (можно использовать)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Пример вызова на System V:**

```c
long calculate(long a, long b, long c) {
    return a + b + c;
}

// Вызов: calculate(10, 20, 30)
```

```asm
; Caller
mov rdi, 10      ; Первый аргумент
mov rsi, 20      ; Второй аргумент
mov rdx, 30      ; Третий аргумент
call calculate
; Результат в RAX

; Callee (calculate)
calculate:
    ; a в RDI, b в RSI, c в RDX
    add rdi, rsi
    add rdi, rdx
    mov rax, rdi  ; Возврат через RAX
    ret
```

### ARM64 AAPCS (iOS, Android)

Apple и Android используют ARM64 AAPCS:

```
┌─────────────────────────────────────────────────────────────┐
│                    ARM64 AAPCS                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   INTEGER ARGUMENTS (первые 8):                             │
│   ┌────┬────┬────┬────┬────┬────┬────┬────┐                │
│   │ X0 │ X1 │ X2 │ X3 │ X4 │ X5 │ X6 │ X7 │                │
│   └────┴────┴────┴────┴────┴────┴────┴────┘                │
│   9+ аргументы → stack                                      │
│                                                             │
│   FLOATING POINT: V0-V7                                     │
│                                                             │
│   RETURN VALUE:                                             │
│   X0        — integer/pointer                              │
│   X0 + X1   — 128 bit                                      │
│   V0        — floating point                               │
│                                                             │
│   SPECIAL REGISTERS:                                        │
│   X29 (FP)  — Frame Pointer                                │
│   X30 (LR)  — Link Register (return address)               │
│   X18 (PR)  — Platform Register (reserved)                 │
│   SP        — Stack Pointer                                │
│                                                             │
│   CALLEE-SAVED: X19-X28, V8-V15 (lower 64 bits)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Почему ARM использует Link Register (LR)?**

На x86 return address кладётся в стек командой `call`. ARM использует регистр X30 (LR):

```asm
; x86-64
call function    ; Push return address to stack
ret              ; Pop and jump

; ARM64
bl function      ; Branch with Link (LR = return address)
ret              ; Branch to LR
```

Это быстрее для leaf functions (функций без вложенных вызовов) — не нужен stack access.

---

## Stack Frame: анатомия

### Структура кадра стека

```
┌─────────────────────────────────────────────────────────────┐
│                    STACK FRAME                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Высокие адреса                                            │
│   ┌─────────────────┐                                       │
│   │  Argument 8+    │  ← Аргументы сверх регистров         │
│   │  Argument 7     │                                       │
│   ├─────────────────┤                                       │
│   │  Return Address │  ← Куда вернуться после ret          │
│   ├─────────────────┤                                       │
│   │  Saved RBP      │  ← Предыдущий frame pointer          │
│   ├─────────────────┤ ← RBP указывает сюда                 │
│   │  Local var 1    │                                       │
│   │  Local var 2    │                                       │
│   │  ...            │                                       │
│   ├─────────────────┤                                       │
│   │  Saved regs     │  ← Callee-saved регистры             │
│   ├─────────────────┤                                       │
│   │  (Red zone)     │  ← 128 bytes для leaf functions      │
│   └─────────────────┘ ← RSP указывает сюда                 │
│   Низкие адреса                                             │
│                                                             │
│   Stack растёт ВНИЗ (к меньшим адресам)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Пролог и эпилог функции

```asm
; Function prologue (начало)
push rbp           ; Сохранить старый frame pointer
mov rbp, rsp       ; Установить новый frame pointer
sub rsp, 32        ; Выделить место для локальных переменных
push rbx           ; Сохранить callee-saved регистры

; ... тело функции ...

; Function epilogue (конец)
pop rbx            ; Восстановить callee-saved
mov rsp, rbp       ; Освободить локальные переменные
pop rbp            ; Восстановить старый frame pointer
ret                ; Вернуться
```

### Red Zone (System V)

System V ABI определяет "красную зону" — 128 байт ниже RSP, которые можно использовать без изменения RSP:

```
┌─────────────────────────────────────────────────────────────┐
│                    RED ZONE                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Обычно:                       С Red Zone:                 │
│   sub rsp, 16                   ; Ничего не делаем         │
│   mov [rsp], rax                mov [rsp-8], rax           │
│   ...                           ...                         │
│   add rsp, 16                   ; Ничего не делаем         │
│                                                             │
│   Условие: leaf function (не вызывает другие функции)      │
│   Преимущество: быстрее, меньше инструкций                 │
│                                                             │
│   Windows x64 НЕ имеет red zone — нужен shadow space       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ABI Stability: почему это важно

### Что ломает ABI

| Изменение | Ломает ABI? | Почему |
|-----------|-------------|--------|
| Добавить аргумент в функцию | Да | Другие регистры/stack layout |
| Изменить порядок полей struct | Да | Смещения полей изменятся |
| Добавить поле в struct | Да | Размер struct изменится |
| Изменить calling convention | Да | Весь механизм вызова другой |
| Добавить новую функцию | Нет | Не влияет на существующий код |
| Изменить реализацию (не сигнатуру) | Нет | Интерфейс не изменился |

### Пример поломки ABI

```c
// Версия 1.0
struct User {
    int id;
    char name[32];
};

// Версия 2.0 — добавили поле
struct User {
    int id;
    int age;        // НОВОЕ ПОЛЕ
    char name[32];
};
```

```
┌─────────────────────────────────────────────────────────────┐
│                    ABI BREAK                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   v1.0 скомпилированный код:                               │
│   user.name находится по смещению 4 (sizeof(int))          │
│                                                             │
│   v2.0 скомпилированный код:                               │
│   user.name находится по смещению 8 (2 * sizeof(int))      │
│                                                             │
│   Если v1.0 код вызывает v2.0 библиотеку:                  │
│   v1.0 читает name по смещению 4 → получает age!           │
│   → Мусор, crash, undefined behavior                       │
│                                                             │
│   Решение: перекомпилировать ВСЕ зависимости               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Swift ABI Stability (2019)

До Swift 5.0 каждое приложение включало Swift runtime:

```
┌─────────────────────────────────────────────────────────────┐
│              Swift До и После ABI Stability                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Swift 4.x (до ABI stability):                            │
│   ┌───────────────┐                                         │
│   │    App.app    │                                         │
│   │  ┌─────────┐  │                                         │
│   │  │ Swift   │  │  ← Каждое приложение ~5-10 MB          │
│   │  │ Runtime │  │    runtime внутри                      │
│   │  └─────────┘  │                                         │
│   └───────────────┘                                         │
│                                                             │
│   Swift 5.0+ (с ABI stability):                            │
│   ┌───────────────┐    ┌─────────────────┐                 │
│   │    App.app    │───▶│  iOS/macOS      │                 │
│   │  (меньше!)    │    │  Swift Runtime  │                 │
│   └───────────────┘    └─────────────────┘                 │
│                                                             │
│   Преимущества:                                             │
│   - Приложения меньше (runtime в ОС)                       │
│   - Обновления Swift без перекомпиляции                    │
│   - Можно использовать Swift в системных frameworks        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Практика: отладка ABI проблем

### Симптомы ABI mismatch

```kotlin
// Kotlin/Native вызывает C библиотеку
// После обновления библиотеки:

// 1. Crash при вызове
// SIGSEGV in libsomething.so

// 2. Неправильные данные
val user = getUser()
println(user.name)  // Выводит мусор

// 3. Corrupted memory
// Heap corruption detected
```

### Диагностика

```bash
# Проверить символы в библиотеке
nm -D libsomething.so | grep myFunction

# Проверить ABI версию
readelf -d libsomething.so | grep SONAME

# Сравнить header и .so
# Если header обновился, а .so нет — ABI mismatch
```

### Kotlin/Native и ABI

Kotlin/Native генерирует код под конкретную платформу:

```kotlin
// build.gradle.kts
kotlin {
    // Каждый target имеет свой ABI
    iosArm64()    // ARM64 AAPCS
    iosX64()      // x86-64 System V (симулятор)
    linuxX64()    // x86-64 System V
    mingwX64()    // Microsoft x64 ABI
}
```

При использовании `cinterop` важно:
- Header файлы должны соответствовать библиотеке
- Версия библиотеки должна быть совместима
- Структуры должны иметь одинаковый layout

---

## Подводные камни

### Распространённые ошибки

| Ошибка | Последствие | Как избежать |
|--------|-------------|--------------|
| Смешивание calling conventions | Crash, wrong data | Explicit annotation |
| Обновление .h без обновления .so | ABI mismatch | Rebuild all |
| Разный alignment на платформах | Memory corruption | Use fixed-size types |
| Игнорирование endianness | Wrong byte order | Network byte order |

### Мифы и заблуждения

**Миф:** "ABI и API — это одно и то же"
**Реальность:** API — контракт для программиста (исходный код). ABI — контракт для машинного кода. Можно изменить API без изменения ABI и наоборот.

**Миф:** "Calling conventions — деталь реализации компилятора"
**Реальность:** Calling conventions — часть ABI платформы. Все компиляторы должны следовать одним правилам для interoperability.

**Миф:** "На современных платформах ABI не важен"
**Реальность:** ABI критичен для interop между языками (Kotlin ↔ C ↔ Swift), использования системных библиотек, и стабильности экосистемы.

---

## Куда дальше

**Если здесь впервые:**
→ Попрактикуйся с отладчиком: посмотри регистры при вызове функции

**Если понял и хочешь глубже:**
→ [[ffi-foreign-function-interface]] — как языки общаются через FFI

**Практическое применение:**
→ cinterop в Kotlin/Native использует эти концепции

---

## Источники

- [Wikipedia: x86 Calling Conventions](https://en.wikipedia.org/wiki/X86_calling_conventions) — comprehensive reference
- [OSDev: System V ABI](https://wiki.osdev.org/System_V_ABI) — technical details
- [Microsoft: x64 Calling Convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention) — Windows specifics
- [ARM AAPCS64](https://medium.com/@tunacici7/aarch64-procedure-call-standard-aapcs64-abi-calling-conventions-machine-registers-a2c762540278) — ARM64 explained
- [Agner Fog: Calling Conventions](https://www.agner.org/optimize/calling_conventions.pdf) — deep technical reference
- [Swift ABI Stability](https://www.swift.org/blog/abi-stability-and-more/) — modern relevance

---

*Проверено: 2026-01-09*

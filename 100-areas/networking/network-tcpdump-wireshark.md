---
title: "Network Packet Analysis: tcpdump & Wireshark"
created: 2025-12-26
modified: 2025-12-26
type: tutorial
status: published
level: middle
tags:
  - topic/networking
  - packet-analysis
  - tcpdump
  - wireshark
  - debugging
  - type/tutorial
  - level/intermediate
---

# Network Packet Analysis: tcpdump & Wireshark

> Глубокий анализ сетевого трафика: от захвата до диагностики

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **TCP/IP** | Понимание структуры пакетов | [[network-transport-layer]] |
| **Debugging basics** | Когда применять packet analysis | [[network-debugging-basics]] |
| **Linux CLI** | tcpdump работает в терминале | Bash basics |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ⚠️ Сложно | Сначала debugging basics |
| **Intermediate** | ✅ Да | Основная аудитория |
| **Advanced** | ✅ Да | Глубокий анализ TCP |

### Терминология для новичков

> 💡 **Packet Analysis** = "МРТ для сети". Видишь каждый пакет, каждый байт. Когда другие инструменты не помогают.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **tcpdump** | CLI инструмент захвата пакетов | **Диктофон** — записать разговор |
| **Wireshark** | GUI анализатор пакетов | **Студия монтажа** — разобрать запись |
| **PCAP** | Формат файла с пакетами | **Аудиофайл** — запись разговора |
| **Filter** | Отбор нужных пакетов | **Поиск по ключевым словам** |
| **BPF** | Berkeley Packet Filter — язык фильтров | **Язык поиска** |
| **Retransmission** | Повторная отправка потерянного | **Повторить, не расслышал** |
| **Window Zero** | Получатель просит остановиться | **"Подожди, не успеваю"** |
| **RST** | Reset — принудительный разрыв | **Бросить трубку** |
| **FIN** | Graceful закрытие соединения | **"До свидания"** |
| **Follow Stream** | Собрать весь разговор | **Склеить записи в диалог** |

---

## Часть 1: Интуиция без кода

> Прежде чем погружаться в команды, построим ментальные образы для понимания packet analysis

### Аналогия 1: Packet capture как прослушка телефонного разговора

**Обычные инструменты:**
```
ping    → "Алло, ты меня слышишь?" — "Да, слышу!"
curl    → "Пришли мне документ" — *получает документ*
ss      → Список всех активных звонков
```

**Packet capture:**
```
┌─────────────────────────────────────────────────────┐
│               ЗАПИСЬ ВСЕГО РАЗГОВОРА                │
│                                                     │
│  [00:00.001] А: "Привет, это Алиса"                 │
│  [00:00.025] Б: "Привет Алиса, это Боб"             │
│  [00:00.050] А: "Пришли мне файл report.pdf"        │
│  [00:00.052] Б: "Ок, шлю..."                        │
│  [00:00.100] Б: *первая часть файла*                │
│  [00:00.150] Б: *вторая часть файла*                │
│  [00:00.200] А: "Не получил вторую часть!"          │
│  [00:00.250] Б: *повторно вторая часть*             │ ← Retransmission!
│  [00:00.300] А: "Получил, спасибо, пока!"           │
│  [00:00.301] Б: "Пока!"                             │
│                                                     │
│  ТЕПЕРЬ ВИДНО: пакет потерялся, была повторная     │
│  отправка — вот почему было медленно!              │
└─────────────────────────────────────────────────────┘
```

---

### Аналогия 2: tcpdump vs Wireshark — диктофон vs студия монтажа

**tcpdump — полевой диктофон:**
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  [СЕРВЕР]  ─────►  tcpdump  ─────►  capture.pcap    │
│                       │                             │
│                       │ • Работает везде            │
│                       │ • Лёгкий, быстрый           │
│                       │ • CLI — без GUI             │
│                       │ • Базовый вывод             │
│                                                     │
│  Применение:                                        │
│  "Запиши всё что происходит на порту 443"           │
│  "Покажи пакеты от IP 10.0.0.5"                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Wireshark — профессиональная студия:**
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  capture.pcap  ─────►  Wireshark  ─────►  Анализ    │
│                           │                         │
│                           │ • Цветовая подсветка    │
│                           │ • Автоматический анализ │
│                           │ • Follow Stream         │
│                           │ • Статистика            │
│                           │ • Графики               │
│                                                     │
│  Применение:                                        │
│  "Покажи все проблемы в этом трафике"              │
│  "Собери весь HTTP диалог в текст"                 │
│  "Найди retransmissions автоматически"              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Типичный workflow:**
```
[Сервер] → tcpdump -w capture.pcap → scp → [Ноутбук] → Wireshark
```

---

### Аналогия 3: Пакет как письмо с конвертом

**Каждый пакет = письмо в конверте:**
```
┌─────────────────────────────────────────────────────┐
│                     КОНВЕРТ                         │
│  ┌─────────────────────────────────────────────┐    │
│  │ От: 192.168.1.5:54321 (IP+порт отправителя) │    │
│  │ Кому: 93.184.216.34:443 (IP+порт получателя)│    │
│  │ Тип: TCP                                    │    │
│  │ Флаги: SYN (начинаю разговор)              │    │
│  │ Seq: 1000 (номер этого письма)             │    │
│  │ Ack: 0 (какое письмо подтверждаю)          │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │             СОДЕРЖИМОЕ ПИСЬМА               │    │
│  │                                             │    │
│  │  GET /api/users HTTP/1.1                    │    │
│  │  Host: api.example.com                      │    │
│  │  Authorization: Bearer eyJ...               │    │
│  │                                             │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
└─────────────────────────────────────────────────────┘

tcpdump читает ВСЁ: и конверт, и содержимое (если не зашифровано)
```

---

### Аналогия 4: TCP Handshake как знакомство

**Три шага для установки соединения:**
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Клиент                              Сервер         │
│     │                                   │           │
│     │                                   │           │
│     │ ──────── SYN ─────────────────►  │           │
│     │        "Привет, давай общаться?" │           │
│     │                                   │           │
│     │ ◄────── SYN+ACK ───────────────  │           │
│     │        "Привет! Давай, я готов!" │           │
│     │                                   │           │
│     │ ──────── ACK ─────────────────►  │           │
│     │        "Отлично, начинаем!"      │           │
│     │                                   │           │
│     │       [СОЕДИНЕНИЕ УСТАНОВЛЕНО]    │           │
│     │                                   │           │
│                                                     │
│  В Wireshark это выглядит:                          │
│  1. [SYN]         10.0.0.1 → 93.184.216.34         │
│  2. [SYN, ACK]    93.184.216.34 → 10.0.0.1         │
│  3. [ACK]         10.0.0.1 → 93.184.216.34         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Что если что-то пошло не так:**
```
SYN → (тишина)        = Firewall DROP / хост недоступен
SYN → RST             = Connection Refused (порт закрыт)
SYN → SYN+ACK → RST   = Клиент передумал
```

---

### Аналогия 5: Retransmission как "повтори, не расслышал"

**Нормальный разговор:**
```
А: "Передаю данные 1, 2, 3, 4, 5"
Б: "Получил 1-5, жду 6"
```

**Разговор с потерей пакета:**
```
А: "Передаю данные 1, 2, 3, 4, 5"
   (пакет 3 потерялся в пути)
Б: "Получил 1, 2, жду 3"    ← ACK
Б: "Получил 4, но жду 3!"   ← Duplicate ACK
Б: "Получил 5, но жду 3!"   ← Duplicate ACK
   (после 3 Dup ACK)
А: "Ок, повторяю 3"         ← Fast Retransmission
Б: "Получил 3, жду 6"
```

**В Wireshark это выглядит:**
```
┌─────────────────────────────────────────────────────┐
│  No.  Time     Source         Info                  │
├─────────────────────────────────────────────────────┤
│  1    0.000    Client         [PSH, ACK] Seq=1     │
│  2    0.001    Client         [PSH, ACK] Seq=1001  │
│  3    0.002    Client         [PSH, ACK] Seq=2001  │ ← ПОТЕРЯН
│  4    0.003    Client         [PSH, ACK] Seq=3001  │
│  5    0.020    Server         [ACK] Ack=2001       │
│  6    0.021    Server         [TCP Dup ACK]        │ ← красное
│  7    0.022    Server         [TCP Dup ACK]        │ ← красное
│  8    0.023    Client         [TCP Retransmission] │ ← красное
│                               Seq=2001             │
│  9    0.040    Server         [ACK] Ack=4001       │
└─────────────────────────────────────────────────────┘
```

---

## Часть 2: Почему это сложно

> 6 типичных ошибок при работе с packet analysis

### Ошибка 1: Захват без фильтра на нагруженном сервере

**СИМПТОМ:**
```bash
# "Давай посмотрим что происходит"
sudo tcpdump -i any -w capture.pcap

# Через 30 секунд:
ls -lh capture.pcap
# -rw-r--r-- 1 root root 2.3G capture.pcap

# "Упс, 2.3 гигабайта за 30 секунд"
# Диск заполнен, Wireshark не может открыть файл
```

**ПОЧЕМУ ЭТО ПРОБЛЕМА:**
```
Нагруженный сервер может генерировать:
• 10,000+ пакетов в секунду
• 100+ MB/sec трафика
• Гигабайты за минуты

Без фильтра захватывается ВСЁ:
• SSH сессия через которую работаете
• Мониторинг, healthchecks
• Все другие сервисы
```

**РЕШЕНИЕ:**
```bash
# ВСЕГДА используйте фильтр

# Конкретный хост
sudo tcpdump -i any host 10.0.0.5 -w capture.pcap

# Конкретный порт
sudo tcpdump -i any port 8080 -w capture.pcap

# Исключите SSH (если работаете удалённо)
sudo tcpdump -i any 'port 80 and not port 22' -w capture.pcap

# Ограничьте по времени
timeout 60 sudo tcpdump -i any port 443 -w capture.pcap

# Ограничьте по количеству пакетов
sudo tcpdump -i any port 443 -c 1000 -w capture.pcap
```

---

### Ошибка 2: Забыть флаг -n (DNS lookups)

**СИМПТОМ:**
```bash
sudo tcpdump -i any port 80

# Вывод ОЧЕНЬ медленный
# Пакеты появляются с задержкой в секунды
# tcpdump как будто "думает"
```

**ПОЧЕМУ ЭТО ПРОБЛЕМА:**
```
Без -n tcpdump пытается резолвить КАЖДЫЙ IP в hostname:

Пакет пришёл от 93.184.216.34
  → DNS запрос: "Кто такой 93.184.216.34?"
  → Ждём ответ... (может быть таймаут)
  → Показываем: example.com вместо IP

На нагруженном сервере это создаёт:
• Тысячи DNS запросов
• Задержки в отображении
• Возможно, сами DNS запросы попадают в захват
```

**РЕШЕНИЕ:**
```bash
# ВСЕГДА используйте -n
sudo tcpdump -n -i any port 80

# -n = no DNS resolution
# -nn = no DNS + no port name resolution (443 вместо https)
sudo tcpdump -nn -i any port 443
```

---

### Ошибка 3: Захватывать собственную SSH сессию

**СИМПТОМ:**
```bash
# Работаете по SSH на сервере
ssh user@server

# Запускаете tcpdump без фильтра
sudo tcpdump -i any

# Результат:
# Бесконечный поток пакетов
# Каждый вывод tcpdump → SSH пакет → ещё вывод → ...
# Feedback loop!
```

**ПОЧЕМУ ЭТО ПРОБЛЕМА:**
```
SSH работает на порту 22 (обычно)
tcpdump захватывает SSH пакеты
Вывод tcpdump передаётся через SSH
Это создаёт новые SSH пакеты
Которые tcpdump захватывает...

┌───────────────────────────────────────┐
│  tcpdump → stdout → SSH → tcpdump →  │
│      ↑                          │     │
│      └──────────────────────────┘     │
│           БЕСКОНЕЧНЫЙ ЦИКЛ            │
└───────────────────────────────────────┘
```

**РЕШЕНИЕ:**
```bash
# Исключите SSH порт
sudo tcpdump -i any 'not port 22'

# Или захватывайте только нужное
sudo tcpdump -i any port 80

# При записи в файл проблемы нет (нет stdout)
sudo tcpdump -i any -w capture.pcap
```

---

### Ошибка 4: Путать Capture filters и Display filters

**СИМПТОМ:**
```bash
# В tcpdump пишете:
sudo tcpdump -i any 'tcp.port == 80'
# tcpdump: syntax error

# В Wireshark capture filter пишете:
tcp.port == 80
# This isn't a valid capture filter
```

**ПОЧЕМУ ЭТО ПРОБЛЕМА:**
```
ДВА РАЗНЫХ ЯЗЫКА ФИЛЬТРОВ:

┌─────────────────────────────────────────────────────┐
│  BPF (Berkeley Packet Filter)                       │
│  ═══════════════════════════                        │
│  Используется: tcpdump, Wireshark CAPTURE filter    │
│                                                     │
│  Синтаксис:                                         │
│  • port 80                                          │
│  • host 192.168.1.1                                │
│  • tcp and port 443                                │
│  • tcp[tcpflags] & tcp-syn != 0                    │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Wireshark Display Filter                           │
│  ═══════════════════════                            │
│  Используется: Wireshark DISPLAY filter, tshark -Y  │
│                                                     │
│  Синтаксис:                                         │
│  • tcp.port == 80                                  │
│  • ip.addr == 192.168.1.1                          │
│  • tcp and tcp.port == 443                         │
│  • tcp.flags.syn == 1                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**РЕШЕНИЕ:**
```
Запомните:
• tcpdump / Wireshark Capture = BPF
• Wireshark Display / tshark -Y = Wireshark syntax

tcpdump:     sudo tcpdump port 80
tshark -Y:   tshark -Y "tcp.port == 80"
```

---

### Ошибка 5: Паниковать из-за retransmissions

**СИМПТОМ:**
```
Открыл capture в Wireshark
Увидел красные строки [TCP Retransmission]
"OMG! У нас packet loss! Сеть сломана!"

Потратил день на debugging
Оказалось: 0.1% retransmissions — это нормально
```

**ПОЧЕМУ ЭТО НЕ ВСЕГДА ПРОБЛЕМА:**
```
┌─────────────────────────────────────────────────────┐
│  RETRANSMISSION RATE     │  ИНТЕРПРЕТАЦИЯ          │
├─────────────────────────────────────────────────────┤
│  < 0.1%                  │  ОТЛИЧНО                │
│  0.1% - 1%               │  НОРМАЛЬНО для интернета│
│  1% - 3%                 │  ЕСТЬ ПРОБЛЕМЫ          │
│  > 3%                    │  СЕРЬЁЗНЫЕ ПРОБЛЕМЫ     │
└─────────────────────────────────────────────────────┘

В интернете пакеты ИНОГДА теряются.
Это нормальная работа TCP — он переотправляет.
```

**РЕШЕНИЕ:**
```bash
# Подсчитайте ПРОЦЕНТ retransmissions

# Всего пакетов
total=$(tshark -r capture.pcap | wc -l)

# Retransmissions
retrans=$(tshark -r capture.pcap -Y "tcp.analysis.retransmission" | wc -l)

# Процент
echo "scale=2; $retrans * 100 / $total" | bc
# → 0.05%  — это нормально!

# Смотрите на ПАТТЕРН:
# • Спорадические по всему файлу = нормально
# • Burst к одному IP = проблема с этим хостом
# • Постоянные > 1% = проблема сети
```

---

### Ошибка 6: Пытаться расшифровать TLS 1.3 через RSA key

**СИМПТОМ:**
```
Добавил private key сервера в Wireshark
TLS 1.2 трафик расшифровался
TLS 1.3 трафик — НЕТ

"Почему не работает?!"
```

**ПОЧЕМУ ЭТО НЕ РАБОТАЕТ:**
```
┌─────────────────────────────────────────────────────┐
│  TLS 1.2 (без PFS)       │  TLS 1.2 (с PFS)        │
│  RSA key exchange        │  ECDHE key exchange     │
│                          │                         │
│  Клиент шифрует          │  Обе стороны генерируют │
│  session key             │  ephemeral keys         │
│  публичным ключом        │                         │
│  сервера                 │  Private key сервера    │
│                          │  НЕ ПОМОГАЕТ            │
│  Private key сервера     │                         │
│  РАСШИФРУЕТ              │                         │
├─────────────────────────────────────────────────────┤
│  TLS 1.3                                            │
│  ════════                                           │
│  ТОЛЬКО ephemeral keys (DHE/ECDHE)                  │
│  Perfect Forward Secrecy обязателен                 │
│                                                     │
│  Private key сервера НИКОГДА не расшифрует          │
│  прошлый трафик — это by design!                    │
└─────────────────────────────────────────────────────┘
```

**РЕШЕНИЕ:**
```bash
# Используйте SSLKEYLOGFILE (Pre-Master Secret Log)

# 1. Экспортируйте переменную ДО запуска приложения
export SSLKEYLOGFILE=/tmp/sslkeys.log

# 2. Запустите браузер/curl/приложение
curl https://example.com

# 3. В Wireshark:
#    Edit → Preferences → Protocols → TLS
#    "(Pre)-Master-Secret log filename" = /tmp/sslkeys.log

# 4. Трафик расшифруется (даже TLS 1.3!)
```

---

## Часть 3: Ментальные модели

### Модель 1: Уровни видимости информации

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  УРОВЕНЬ           │  ЧТО ВИДНО         │ ИНСТРУМЕНТ│
│                                                     │
├─────────────────────────────────────────────────────┤
│  Приложение        │  "Ошибка 500"      │  Логи     │
│  (самый высокий)   │  "Timeout"         │  APM      │
│                    │  Мало деталей      │           │
├─────────────────────────────────────────────────────┤
│  HTTP              │  Headers, Body     │  curl -v  │
│                    │  Status codes      │  DevTools │
│                    │  Timing            │           │
├─────────────────────────────────────────────────────┤
│  TLS               │  Handshake         │  openssl  │
│                    │  Certificates      │  Wireshark│
│                    │  Alerts            │           │
├─────────────────────────────────────────────────────┤
│  TCP               │  Seq/Ack numbers   │  tcpdump  │
│                    │  Flags, Window     │  Wireshark│
│                    │  Retransmissions   │           │
├─────────────────────────────────────────────────────┤
│  IP                │  Src/Dst IP        │  tcpdump  │
│  (самый низкий)    │  TTL, Fragments    │  Wireshark│
│                    │  ВСЕГО БОЛЬШЕ      │           │
└─────────────────────────────────────────────────────┘

ПРАВИЛО: Чем ниже уровень — тем больше деталей.
         Packet analysis = самый детальный уровень.
```

---

### Модель 2: Временная шкала пакетов

```
┌─────────────────────────────────────────────────────┐
│  Каждый пакет имеет TIMESTAMP                       │
│  Интервалы между пакетами = ключ к диагностике      │
│                                                     │
│  Time     │ Event                │ Интервал         │
│  ─────────┼──────────────────────┼─────────────     │
│  0.000    │ SYN                  │                  │
│  0.025    │ SYN+ACK              │ 25ms (RTT/2)     │
│  0.026    │ ACK                  │ 1ms              │
│  0.027    │ GET /api             │ 1ms              │
│  0.300    │ HTTP 200             │ 273ms ← МЕДЛЕННО!│
│           │                      │                  │
│  Вывод: RTT = 50ms, но ответ через 273ms           │
│         Backend тратит 273-50 = 223ms на обработку │
│                                                     │
└─────────────────────────────────────────────────────┘

Wireshark: Statistics → Flow Graph
           Показывает визуально где время тратится
```

---

### Модель 3: "Следуй за потоком" (Follow the Stream)

```
┌─────────────────────────────────────────────────────┐
│  Сырые пакеты:                                      │
│  ────────────                                       │
│  Пакет 1: [TCP] Seq=1, Len=100                      │
│  Пакет 2: [TCP] Seq=101, Len=200                    │
│  Пакет 3: [TCP] Seq=301, Len=50                     │
│  Пакет 4: [TCP] Ack=351                             │
│  ...                                                │
│                                                     │
│  Follow TCP Stream:                                 │
│  ─────────────────                                  │
│  GET /api/users HTTP/1.1                            │
│  Host: api.example.com                              │
│  Authorization: Bearer eyJhbGc...                   │
│                                                     │
│  HTTP/1.1 200 OK                                    │
│  Content-Type: application/json                     │
│                                                     │
│  {"users": [{"id": 1, "name": "Alice"}]}            │
│                                                     │
│  WIRESHARK СОБРАЛ ВСЕ ПАКЕТЫ В ЧИТАЕМЫЙ ДИАЛОГ     │
└─────────────────────────────────────────────────────┘

Как использовать:
1. Правый клик на любом пакете TCP
2. Follow → TCP Stream
3. Видите весь HTTP диалог как текст
```

---

### Модель 4: Красный = проблема (цветовая схема)

```
┌─────────────────────────────────────────────────────┐
│  Wireshark использует цвета для быстрой диагностики │
│                                                     │
│  ██████ ЗЕЛЁНЫЙ  │  HTTP успешный                   │
│  ██████ ГОЛУБОЙ  │  UDP трафик                      │
│  ██████ ЖЁЛТЫЙ   │  TCP, TLS (норма)                │
│  ██████ КРАСНЫЙ  │  ПРОБЛЕМА!                       │
│                  │  • Retransmission                │
│                  │  • RST (reset)                   │
│                  │  • Dup ACK                       │
│  ██████ ЧЁРНЫЙ   │  Плохие пакеты (checksum error)  │
│                                                     │
│  ПРАВИЛО: Если много красного — есть проблемы      │
│           Если красное спорадическое — возможно ок │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### Модель 5: Когда использовать packet analysis

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ДИАГНОСТИЧЕСКАЯ ПИРАМИДА                           │
│                                                     │
│                    ┌─────┐                          │
│                    │PACKET│ ← Только когда всё      │
│                    │ANALY-│    остальное не помогло │
│                    │SIS   │                         │
│                    └──┬──┘                          │
│                ┌─────┴─────┐                        │
│                │  curl -v  │ ← HTTP проблемы        │
│                │  DevTools │                        │
│                └─────┬─────┘                        │
│            ┌─────────┴─────────┐                    │
│            │  ss, netstat, nc  │ ← TCP/порты        │
│            │  telnet           │                    │
│            └─────────┬─────────┘                    │
│        ┌─────────────┴─────────────┐                │
│        │  ping, traceroute, mtr   │ ← Связность    │
│        │  dig, nslookup           │                 │
│        └───────────────────────────┘                │
│                                                     │
│  ПРАВИЛО: Начинай снизу пирамиды!                   │
│           Packet analysis = "тяжёлая артиллерия"    │
│                                                     │
└─────────────────────────────────────────────────────┘

Когда НУЖЕН packet analysis:
• Простые инструменты дают противоречивые результаты
• "Работает, но медленно" — нужно понять где задержка
• Подозрение на TCP проблемы (retrans, window)
• Нужно ДОКАЗАТЬ что проблема не на вашей стороне
```

---

## Зачем нужен Packet Analysis

### Философия packet analysis: когда обычные инструменты не справляются

**Packet analysis — это "последний рубеж" диагностики.** Когда ping работает, telnet на порт проходит, curl возвращает ответ, но что-то всё равно не так — только просмотр реальных пакетов покажет, что происходит на самом деле.

**Аналогия из медицины.** Врач сначала слушает жалобы (логи), меряет температуру и давление (ping, curl), делает базовые анализы (mtr, dig). Но если диагноз неясен — назначает МРТ или биопсию, чтобы увидеть, что происходит внутри. Packet analysis — это "МРТ" для сети.

**Почему это сложнее других инструментов:**
1. **Объём данных.** За минуту можно захватить гигабайты. Без правильных фильтров — утонете в информации
2. **Требует понимания протоколов.** Нужно знать, как выглядит нормальный TCP handshake, чтобы увидеть ненормальный
3. **Сложность интерпретации.** Retransmission — это проблема? Или нормальное поведение для интернета?

**Когда переходить к packet analysis:**
- Простые инструменты (ping, curl, ss) дают противоречивые результаты
- "Работает, но странно" — нужно увидеть, что именно странно
- Подозрение на проблемы уровня TCP: retransmissions, window issues, MTU
- TLS/SSL ошибки, которые не понятны из сообщений об ошибках
- Нужно доказать, что проблема на стороне другой системы

**Когда packet analysis — overkill:**
- Сервис просто не запущен (ss -tuln сразу покажет)
- DNS не резолвится (dig ответит за секунду)
- Firewall блокирует (nc -zv даст быстрый ответ)
- Базовые HTTP-ошибки (curl -v покажет всё нужное)

**Что даёт packet analysis, чего не дают другие инструменты:**
- **Точные timestamps.** Видно, сколько миллисекунд между каждым пакетом
- **Полную картину обмена.** Все запросы и ответы, включая те, о которых приложение не знает
- **Состояние TCP.** Sequence numbers, acknowledgments, window sizes
- **Доказательства.** pcap-файл — это документальное свидетельство того, что произошло

---

## tcpdump: Быстрый захват в CLI

### Когда использовать tcpdump

**tcpdump — ваш главный инструмент для захвата трафика на сервере.** На серверах обычно нет GUI, а tcpdump есть практически на любой Unix-системе. Типичный workflow: захватить трафик через tcpdump, скачать .pcap файл на локальную машину, анализировать в Wireshark.

**Почему tcpdump, а не сразу Wireshark:**
- Wireshark требует GUI → не работает на серверах через SSH
- tcpdump есть почти везде из коробки
- Для быстрой проверки ("идут ли пакеты на порт 80?") tcpdump достаточен
- Меньше overhead на production-сервере

**Золотое правило tcpdump: всегда используйте фильтры.** Без фильтра на загруженном сервере за секунды захватятся гигабайты трафика. Начинайте с максимально узкого фильтра и расширяйте при необходимости.

**Типичные ошибки новичков:**
- Забыли `-n` → tcpdump делает DNS lookups для каждого IP, это медленно
- Забыли фильтр → захватили всё включая SSH-сессию, через которую работаете
- Забыли `-s0` → по умолчанию захватываются только первые 262144 байт пакета (зависит от версии)
- Захватывали слишком долго → файл на гигабайты

### Базовый захват

```bash
# Показать доступные интерфейсы
tcpdump -D

# Захват на конкретном интерфейсе
sudo tcpdump -i eth0

# Захват на всех интерфейсах
sudo tcpdump -i any

# Ограничить количество пакетов
sudo tcpdump -c 100 -i any

# Без DNS resolution (быстрее)
sudo tcpdump -n -i any

# Verbose output
sudo tcpdump -v -i any
sudo tcpdump -vv -i any  # ещё подробнее
```

### Фильтры по протоколу и порту

```bash
# Только TCP
sudo tcpdump -i any tcp

# Только UDP
sudo tcpdump -i any udp

# ICMP (ping)
sudo tcpdump -i any icmp

# Конкретный порт
sudo tcpdump -i any port 80
sudo tcpdump -i any port 443

# Диапазон портов
sudo tcpdump -i any portrange 8000-9000

# Source или destination порт
sudo tcpdump -i any src port 443
sudo tcpdump -i any dst port 80
```

### Фильтры по хосту

```bash
# Траффик от/к конкретному хосту
sudo tcpdump -i any host 192.168.1.100

# Только исходящий
sudo tcpdump -i any src host 192.168.1.100

# Только входящий
sudo tcpdump -i any dst host 192.168.1.100

# Подсеть
sudo tcpdump -i any net 192.168.1.0/24
```

### Комбинация фильтров (BPF)

```bash
# AND — оба условия
sudo tcpdump -i any 'port 80 and host 192.168.1.100'

# OR — любое из условий
sudo tcpdump -i any 'port 80 or port 443'

# NOT — исключить
sudo tcpdump -i any 'not port 22'

# Сложные комбинации
sudo tcpdump -i any 'tcp port 443 and (host 10.0.0.1 or host 10.0.0.2)'

# HTTP траффик без SSH (полезно при remote capture)
sudo tcpdump -i any 'tcp port 80 and not port 22'
```

### Advanced BPF Filters

```bash
# TCP SYN пакеты (новые соединения)
sudo tcpdump -i any 'tcp[tcpflags] & tcp-syn != 0'

# TCP SYN+ACK (ответы на соединения)
sudo tcpdump -i any 'tcp[tcpflags] & (tcp-syn|tcp-ack) == (tcp-syn|tcp-ack)'

# TCP RST (сброс соединения)
sudo tcpdump -i any 'tcp[tcpflags] & tcp-rst != 0'

# TCP FIN (завершение соединения)
sudo tcpdump -i any 'tcp[tcpflags] & tcp-fin != 0'

# Пакеты больше определённого размера
sudo tcpdump -i any 'greater 1000'

# Пакеты меньше определённого размера
sudo tcpdump -i any 'less 100'
```

**TCP Flags reference:**
| Флаг | Синтаксис BPF | Значение |
|------|---------------|----------|
| SYN | `tcp-syn` | Начало соединения |
| ACK | `tcp-ack` | Подтверждение |
| FIN | `tcp-fin` | Завершение |
| RST | `tcp-rst` | Сброс |
| PSH | `tcp-push` | Передать данные немедленно |
| URG | `tcp-urg` | Urgent data |

### Сохранение и чтение

```bash
# Сохранить в файл (для Wireshark)
sudo tcpdump -i any -w capture.pcap

# Сохранить полные пакеты (snap length unlimited)
sudo tcpdump -i any -s0 -w capture.pcap

# Читать из файла
tcpdump -r capture.pcap

# Читать с фильтром
tcpdump -r capture.pcap 'port 80'

# Rotate files (новый файл каждые 100MB)
sudo tcpdump -i any -w capture.pcap -C 100

# Rotate по времени (новый файл каждые 60 сек)
sudo tcpdump -i any -w capture.pcap -G 60
```

### Вывод содержимого пакетов

```bash
# ASCII вывод (читаемый текст)
sudo tcpdump -A -i any port 80

# Hex + ASCII
sudo tcpdump -X -i any port 80

# Только hex
sudo tcpdump -x -i any port 80

# Пример вывода HTTP:
# GET /api/users HTTP/1.1
# Host: api.example.com
# User-Agent: curl/7.88.1
```

### Практические примеры

```bash
# DNS запросы
sudo tcpdump -i any -n port 53

# HTTP запросы (показать URL)
sudo tcpdump -i any -A -s0 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'

# Найти SYN flood
sudo tcpdump -i any 'tcp[tcpflags] == tcp-syn'

# Slow connections (большой интервал)
sudo tcpdump -i any -ttt port 443
```

---

## Wireshark: GUI Analysis

### Когда использовать Wireshark

**Wireshark — лучший инструмент для глубокого анализа трафика.** Его GUI даёт то, чего не может дать CLI: визуализацию TCP streams, автоматическое определение проблем, удобную навигацию по тысячам пакетов.

**Преимущества GUI перед tcpdump:**
- **Цветовая кодировка.** Retransmissions красные, HTTP зелёный — сразу видно аномалии
- **Expert Information.** Wireshark автоматически находит типичные проблемы: retransmissions, zero window, out-of-order
- **Follow Stream.** Можно увидеть весь диалог между клиентом и сервером как текст
- **Statistics.** Графики, диаграммы, распределение по протоколам
- **Фильтрация на лету.** Можно экспериментировать с фильтрами без перезахвата

**Типичный workflow:**
1. Захватить трафик на сервере через tcpdump: `sudo tcpdump -i any -w capture.pcap port 443`
2. Скопировать файл на локальную машину: `scp server:capture.pcap ./`
3. Открыть в Wireshark: `wireshark capture.pcap`
4. Применить фильтры, проанализировать, найти проблему

**Capture filters vs Display filters — важное различие:**
- **Capture filters** (синтаксис BPF) — применяются во время захвата, ограничивают что попадёт в файл
- **Display filters** (синтаксис Wireshark) — применяются после захвата, фильтруют что показывать

Capture filter: `port 80` (BPF syntax)
Display filter: `tcp.port == 80` (Wireshark syntax)

Всегда захватывайте больше, чем нужно (широким capture filter), а потом сужайте display filter'ами. Недостающие пакеты не восстановить, а лишние можно отфильтровать.

### Установка

```bash
# macOS
brew install wireshark

# Ubuntu/Debian
sudo apt install wireshark

# Arch
sudo pacman -S wireshark-qt
```

### Базовые фильтры

**Display filters (после захвата):**

```
# По протоколу
http
tcp
udp
dns
tls

# По IP
ip.addr == 192.168.1.100
ip.src == 192.168.1.100
ip.dst == 8.8.8.8

# По порту
tcp.port == 443
tcp.srcport == 80
tcp.dstport == 8080

# По содержимому
http.request.method == "GET"
http.response.code == 200
http.host contains "api"

# Комбинации
http.request and ip.src == 192.168.1.100
tcp.port == 80 || tcp.port == 443
!(arp or icmp)
```

### TCP Analysis Filters

```
# Все TCP проблемы
tcp.analysis.flags

# Retransmissions
tcp.analysis.retransmission

# Duplicate ACKs
tcp.analysis.duplicate_ack

# Lost segments
tcp.analysis.lost_segment

# Zero window
tcp.analysis.zero_window

# Out of order
tcp.analysis.out_of_order

# Fast retransmission
tcp.analysis.fast_retransmission

# Spurious retransmission
tcp.analysis.spurious_retransmission

# Reset connections
tcp.flags.reset == 1
```

### TLS/HTTPS Analysis

```
# TLS handshake
tls.handshake

# Client Hello
tls.handshake.type == 1

# Server Hello
tls.handshake.type == 2

# Certificate
tls.handshake.type == 11

# TLS версия
tls.record.version == 0x0303  # TLS 1.2
tls.record.version == 0x0304  # TLS 1.3

# TLS alerts
tls.alert_message
```

### HTTP/2 Analysis

```
# HTTP/2 frames
http2

# HEADERS frames
http2.type == 1

# DATA frames
http2.type == 0

# GOAWAY frames (connection closing)
http2.type == 7

# По stream ID
http2.streamid == 1
```

---

## TCP Analysis: Что искать

### Понимание TCP на уровне пакетов

**Зачем разбираться в TCP internals.** TCP — транспортный протокол, который обеспечивает надёжную доставку данных поверх ненадёжной IP-сети. Он делает это через acknowledgments, retransmissions, flow control. Понимание этих механизмов позволяет:
- Видеть, где именно теряются данные
- Понимать, почему соединение "медленное"
- Отличать проблемы сети от проблем приложения

**Ключевые концепции TCP для packet analysis:**
- **Sequence Numbers (Seq)** — номер первого байта в пакете. Позволяет собрать данные в правильном порядке
- **Acknowledgment Numbers (Ack)** — "я получил все байты до этого номера". Подтверждает получение данных
- **Window Size** — "я готов принять ещё столько байт". Flow control для защиты от перегрузки
- **Flags** — SYN, ACK, FIN, RST — управляют состоянием соединения

**Что Wireshark показывает автоматически.** В колонке Info Wireshark подсвечивает проблемы:
- `[TCP Retransmission]` — пакет отправлен повторно
- `[TCP Dup ACK]` — дублированное подтверждение (признак потери)
- `[TCP Zero Window]` — получатель не успевает обрабатывать
- `[TCP Out-Of-Order]` — пакеты пришли не в том порядке

### Three-Way Handshake — начало TCP соединения

```
Нормальный handshake:

Client                          Server
   |                               |
   |------- SYN (seq=100) -------->|
   |                               |
   |<-- SYN+ACK (seq=200,ack=101) -|
   |                               |
   |------- ACK (ack=201) -------->|
   |                               |
   [Connection Established]
```

**Wireshark filter:** `tcp.flags.syn == 1`

**Проблемы:**
| Симптом | Что значит | Фильтр |
|---------|------------|--------|
| SYN без SYN+ACK | Сервер не отвечает (firewall, не слушает) | `tcp.flags.syn==1 and tcp.flags.ack==0` |
| SYN+ACK без ACK | Клиент не завершил handshake | - |
| RST после SYN | Connection refused | `tcp.flags.reset==1` |

### Connection Termination

```
Нормальное завершение (4-way):

Client                          Server
   |                               |
   |------- FIN ------------------>|
   |<------ ACK -------------------|
   |<------ FIN -------------------|
   |------- ACK ------------------>|
   |                               |
   [Connection Closed]

Быстрое завершение:
   |------- FIN+ACK -------------->|
   |<------ FIN+ACK ---------------|
   |------- ACK ------------------>|
```

**Ненормальное завершение:**
```
RST (сброс):
   |------- RST ------------------>|
   [Connection Reset - abruptly terminated]
```

### Retransmissions

**Типы retransmission:**

| Тип | Wireshark Info | Причина |
|-----|----------------|---------|
| TCP Retransmission | Пакет не был подтверждён в timeout | Packet loss |
| Fast Retransmission | 3+ duplicate ACKs получено | Быстрая реакция на loss |
| Spurious Retransmission | Retransmit пакета, который уже ACK'd | Ложное срабатывание |

**Filter:** `tcp.analysis.retransmission`

**Что проверять:**
1. **Retransmission Rate** — не должен быть >1%
2. **RTT** — высокий RTT = больше retransmissions
3. **Pattern** — постоянные или спорадические?

### Duplicate ACKs

```
Сценарий:
Сервер отправляет пакеты 1, 2, 3, 4, 5
Клиент получает: 1, 2, _, 4, 5 (3 потерян)

Клиент отправляет:
ACK 3 (получил 1,2, жду 3)
ACK 3 (duplicate - получил 4, но всё ещё жду 3)
ACK 3 (duplicate - получил 5, но всё ещё жду 3)

После 3 duplicate ACKs → Fast Retransmission packet 3
```

**Filter:** `tcp.analysis.duplicate_ack`

### Window Size Issues

```
# Zero Window — получатель не успевает обрабатывать
tcp.analysis.zero_window

# Window Update — получатель снова готов
tcp.analysis.window_update

# Window Full — отправитель заполнил window
tcp.analysis.window_full
```

**Причины Zero Window:**
- Приложение медленно читает данные
- CPU overload на receiver
- Disk I/O bottleneck

---

## TLS Decryption

### Когда и зачем расшифровывать TLS

**Проблема: HTTPS везде.** Современный интернет почти полностью зашифрован. Это хорошо для безопасности, но плохо для диагностики. Когда вы захватываете HTTPS-трафик, вы видите только метаданные: IP-адреса, размеры пакетов, timing. Само содержимое — HTTP-заголовки, тело запроса/ответа — зашифровано.

**Когда нужна расшифровка:**
- Нужно увидеть HTTP-заголовки и тело ответа
- Подозрение на проблемы на уровне приложения (не TLS)
- Debugging клиент-серверного взаимодействия
- Проверка, что сервер отправляет правильные данные

**Когда расшифровка НЕ нужна:**
- Проблемы на уровне TCP (retransmissions, latency) видны и в зашифрованном трафике
- TLS handshake failures — видно по TLS alerts
- Базовая connectivity — и так понятно

**Важно: расшифровка возможна только для трафика, который вы контролируете.** Вы можете расшифровать трафик вашего браузера или приложения. Вы не можете расшифровать чужой трафик — TLS специально спроектирован для защиты от этого.

### Без ключей видно только метаданные

HTTPS/TLS шифрует содержимое — без ключей видно только:
- IP адреса
- Размер пакетов
- Timing
- TLS handshake (частично)

С decryption видно:
- HTTP headers и body
- Actual request/response
- Application-level errors

### Method 1: Pre-Master Secret Log (рекомендуется)

**Работает для:** Chrome, Firefox, curl, Node.js

```bash
# 1. Установить переменную окружения
export SSLKEYLOGFILE=/tmp/sslkeys.log

# 2. Запустить браузер из терминала (важно!)
# Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome

# Firefox
/Applications/Firefox.app/Contents/MacOS/firefox

# curl
curl https://example.com

# 3. В Wireshark: Edit → Preferences → Protocols → TLS
#    Установить "(Pre)-Master-Secret log filename" = /tmp/sslkeys.log

# 4. Захватить трафик — он будет расшифрован
```

**Для Node.js:**
```bash
node --tls-keylog=/tmp/sslkeys.log app.js
```

### Method 2: RSA Private Key (legacy)

**Работает только для:**
- TLS 1.2 и ниже
- Без Perfect Forward Secrecy (no DHE/ECDHE)
- Когда есть private key сервера

```
Wireshark: Edit → Preferences → Protocols → TLS → RSA keys list
```

> **Важно:** НЕ работает с TLS 1.3 — используйте Pre-Master Secret Log.

### Проверка decryption

После настройки должны появиться:
- HTTP протокол в колонке Protocol (вместо TCP)
- Readable HTTP headers
- HTTP request/response в packet details

**Filter для проверки:**
```
http.request or http.response
```

---

## tshark: CLI версия Wireshark

### Базовое использование

```bash
# Захват на интерфейсе
tshark -i eth0

# С display filter
tshark -i any -Y "http.request"

# Читать pcap файл
tshark -r capture.pcap

# JSON output
tshark -r capture.pcap -T json
```

### Извлечение полей

```bash
# Извлечь IP адреса
tshark -r capture.pcap -T fields -e ip.src -e ip.dst

# С заголовками
tshark -r capture.pcap -T fields -E header=y -e ip.src -e ip.dst -e tcp.port

# HTTP requests
tshark -r capture.pcap -Y "http.request" -T fields \
  -e http.host -e http.request.uri -e http.user_agent

# DNS queries
tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields \
  -e dns.qry.name
```

### Статистика

```bash
# Conversations
tshark -r capture.pcap -q -z conv,tcp

# Protocol hierarchy
tshark -r capture.pcap -q -z io,phs

# HTTP statistics
tshark -r capture.pcap -q -z http,tree

# DNS statistics
tshark -r capture.pcap -q -z dns,tree
```

### Полезные комбинации

```bash
# Top talkers (IP addresses)
tshark -r capture.pcap -T fields -e ip.src | sort | uniq -c | sort -rn | head

# HTTP hosts accessed
tshark -r capture.pcap -Y "http.request" -T fields -e http.host | sort -u

# Failed TCP connections (RST)
tshark -r capture.pcap -Y "tcp.flags.reset==1" -T fields \
  -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport

# TLS versions used
tshark -r capture.pcap -Y "tls.handshake.type==1" -T fields \
  -e ip.dst -e tls.handshake.version

# Retransmission count
tshark -r capture.pcap -Y "tcp.analysis.retransmission" | wc -l
```

---

## Практические сценарии

### Сценарий 1: "Почему запрос медленный?"

```bash
# 1. Захватить трафик
sudo tcpdump -i any -w slow-request.pcap port 443

# 2. Воспроизвести медленный запрос
curl https://slow-api.example.com/endpoint

# 3. Открыть в Wireshark
wireshark slow-request.pcap

# 4. Посмотреть на timing:
#    - Statistics → Flow Graph
#    - Выбрать TCP flow
#    - Смотреть на интервалы между пакетами
```

**Что искать:**
| Где задержка | Вероятная причина |
|--------------|-------------------|
| Между SYN и SYN+ACK | Network latency или server slow to respond |
| Между TLS Client Hello и Server Hello | TLS processing slow |
| Между HTTP request и response | Backend processing |
| Между DATA пакетами | Network congestion или slow sender |

### Сценарий 2: "Connection refused vs timeout"

```bash
# Connection refused — видим RST:
tshark -r capture.pcap -Y "tcp.flags.reset==1"
# IP → IP RST, ACK Seq=...

# Connection timeout — видим только SYN:
tshark -r capture.pcap -Y "tcp.flags.syn==1 and tcp.flags.ack==0"
# Множество SYN без ответа = firewall DROP
```

### Сценарий 3: "TLS handshake fails"

```bash
# Фильтр для TLS alerts
tshark -r capture.pcap -Y "tls.alert_message"

# Посмотреть версии TLS
tshark -r capture.pcap -Y "tls.handshake.type==1" -T fields \
  -e ip.dst -e tls.handshake.extensions.supported_version
```

**Common TLS errors:**
| Alert | Значение | Решение |
|-------|----------|---------|
| handshake_failure | Нет общих cipher suites | Проверить supported ciphers |
| certificate_unknown | Неизвестный CA | Добавить CA certificate |
| certificate_expired | Сертификат истёк | Обновить certificate |
| bad_certificate | Невалидный сертификат | Проверить chain |

### Сценарий 4: "Много retransmissions"

```bash
# Подсчитать retransmissions
tshark -r capture.pcap -Y "tcp.analysis.retransmission" | wc -l

# Посмотреть паттерн
tshark -r capture.pcap -Y "tcp.analysis.flags" -T fields \
  -e frame.time_relative -e ip.src -e ip.dst -e tcp.analysis.flags
```

**Анализ:**
- **Спорадические retransmissions** — нормально для интернета
- **Burst retransmissions** — network congestion или packet loss на router
- **Постоянные retransmissions к одному IP** — проблема с этим хостом

---

## Quick Reference

### tcpdump cheat sheet

```bash
# Basics
tcpdump -i eth0              # Capture on interface
tcpdump -i any               # Capture on all interfaces
tcpdump -c 100               # Capture 100 packets
tcpdump -n                   # No DNS resolution
tcpdump -w file.pcap         # Write to file
tcpdump -r file.pcap         # Read from file

# Filters
tcpdump host 1.2.3.4         # By host
tcpdump port 80              # By port
tcpdump tcp                  # By protocol
tcpdump 'port 80 and host 1.2.3.4'  # Combined

# Output
tcpdump -A                   # ASCII
tcpdump -X                   # Hex + ASCII
tcpdump -v / -vv / -vvv      # Verbose levels
```

### Wireshark display filters

```
# Protocol
http, tcp, udp, dns, tls

# IP
ip.addr == 1.2.3.4
ip.src == 1.2.3.4

# TCP
tcp.port == 443
tcp.flags.syn == 1
tcp.analysis.retransmission

# HTTP
http.request.method == "POST"
http.response.code == 500

# TLS
tls.handshake.type == 1

# Operators
== != > < >= <=
and or not
contains matches
```

### Полезные Wireshark views

| Меню | Что показывает |
|------|----------------|
| Statistics → Conversations | Топ connections |
| Statistics → Protocol Hierarchy | Breakdown по протоколам |
| Statistics → Flow Graph | Визуализация обмена |
| Analyze → Follow → TCP Stream | Весь диалог TCP |
| Analyze → Expert Information | Автоматический анализ проблем |

---

## Ссылки и источники

### Официальная документация
- [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html/)
- [tcpdump man page](https://www.tcpdump.org/manpages/tcpdump.1.html)
- [Wireshark TCP Analysis](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvTCPAnalysis.html)
- [TLS Decryption Wiki](https://wiki.wireshark.org/TLS)

### Tutorials
- [tshark tutorial (HackerTarget)](https://hackertarget.com/tshark-tutorial-and-filter-examples/)
- [TLS decryption guide (Palo Alto)](https://unit42.paloaltonetworks.com/wireshark-tutorial-decrypting-https-traffic/)
- [BPF syntax reference](https://biot.com/capstats/bpf.html)

### Deep dives
- [TCP Analysis in Wireshark](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvTCPAnalysis.html)
- [Understanding TCP Spurious Retransmissions](https://www.packetsafari.com/blog/2021/10/23/tcp-spurious-retransmissions/)

---

## Связанные материалы

### В этом разделе
→ [[network-debugging-basics]] — systematic debugging approach
→ [[network-tools-reference]] — справочник всех инструментов
→ [[network-transport-layer]] — TCP/UDP в деталях
→ [[network-troubleshooting-advanced]] — сложные кейсы

### Смежные темы
→ [[observability]] — мониторинг и tracing
→ [[security-moc]] — network security analysis

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции: 5 аналогий (packet capture как прослушка, tcpdump vs Wireshark как диктофон vs студия, пакет как письмо с конвертом, TCP handshake как знакомство, retransmission как "повтори"), 6 типичных ошибок packet analysis (захват без фильтра, забыть -n, захват SSH сессии, путать capture/display filters, паника из-за retransmissions, TLS 1.3 с RSA key), 5 ментальных моделей (уровни видимости, временная шкала пакетов, follow stream, цветовая схема, диагностическая пирамида)*

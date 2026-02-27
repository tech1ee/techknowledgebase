---
title: "Real-time протоколы: WebSocket, SSE, WebRTC, gRPC"
created: 2025-12-18
modified: 2026-02-13
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/networking
  - networking/protocols
  - networking/realtime
  - type/concept
  - level/intermediate
related:
  - "[[network-http-evolution]]"
  - "[[network-transport-layer]]"
  - "[[android-networking]]"
prerequisites:
  - "[[network-http-evolution]]"
  - "[[network-transport-layer]]"
reading_time: 108
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Real-time протоколы: WebSocket, SSE, WebRTC, gRPC

---

## Теоретические основы

> **Real-time протоколы** — протоколы, обеспечивающие двустороннюю или push-коммуникацию с минимальной задержкой. Решают фундаментальную проблему HTTP: request-response модель не подходит для потоковых данных.

### Эволюция real-time в вебе

| Год | Технология | Механизм | Проблема |
|-----|-----------|----------|----------|
| 1999 | **Polling** | Периодические HTTP-запросы | Нагрузка, задержки |
| 2003 | **Long Polling (Comet)** | HTTP-запрос ждёт события | Один канал, overhead |
| 2011 | **WebSocket** (RFC 6455) | Persistent full-duplex TCP | Proxy/firewall issues |
| 2015 | **SSE** (EventSource API) | Server → Client push по HTTP | Только server→client |
| 2011 | **WebRTC** (W3C/IETF) | P2P media + data channels | Сложный NAT traversal |
| 2022 | **WebTransport** (IETF draft) | HTTP/3 (QUIC) based bidirectional | Новый, ещё adoption |

### Сравнение протоколов

| Аспект | WebSocket | SSE | WebRTC | gRPC Streaming |
|--------|-----------|-----|--------|---------------|
| Направление | Bidirectional | Server → Client | Bidirectional (P2P) | Bidirectional |
| Транспорт | TCP | HTTP/1.1+ | UDP (DTLS/SRTP) | HTTP/2 |
| Reconnect | Ручной | Автоматический | ICE restart | Ручной |
| Binary data | ✅ | ❌ (text only) | ✅ | ✅ (protobuf) |
| Через CDN/proxy | ⚠️ (upgrade) | ✅ (обычный HTTP) | ⚠️ (TURN fallback) | ✅ |

> **См. также**: [[network-http-evolution]] — HTTP/1 → HTTP/3, [[network-transport-layer]] — TCP/UDP

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **HTTP** | WebSocket начинается как HTTP upgrade | [[network-http-evolution]] |
| **TCP/UDP** | Понимание transport layer | [[network-transport-layer]] |
| **JavaScript async** | Для клиентской части | JS async/await |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Новичок** | ⚠️ С подготовкой | Сначала HTTP |
| **Intermediate** | ✅ Да | Основная аудитория |
| **Advanced** | ✅ Да | WebRTC P2P |

### Терминология для новичков

> 💡 **Real-time** = данные приходят сразу, без задержки. Как телефонный разговор, а не SMS.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **WebSocket** | Постоянное двустороннее соединение | **Телефонный разговор** — оба говорят когда хотят |
| **SSE** | Server-Sent Events — поток от сервера | **Радио** — ты только слушаешь |
| **WebRTC** | P2P аудио/видео в браузере | **Видеозвонок напрямую** — без сервера |
| **gRPC** | Быстрый RPC от Google | **Экспресс-почта для программ** |
| **Polling** | Клиент постоянно спрашивает "есть новое?" | **Проверять почтовый ящик каждую минуту** |
| **Long Polling** | Сервер держит запрос до появления данных | **Ждать у почтового ящика пока не придёт** |
| **Backpressure** | Замедление при перегрузке | **"Подожди, не успеваю записывать"** |
| **STUN/TURN** | NAT traversal для WebRTC | **Посредник для соединения за NAT** |
| **Full Duplex** | Оба говорят одновременно | **Телефон** (vs рация — half duplex) |
| **Heartbeat** | Проверка "живо" соединение | **"Ты ещё там?"** каждые N секунд |

---

## Терминология

| Термин | Описание | Примечания |
|--------|----------|------------|
| **WebSocket** | Протокол полнодуплексной связи поверх TCP с upgrade от HTTP | RFC 6455, порты 80/443 |
| **SSE** | Server-Sent Events - однонаправленный push от сервера к клиенту | Работает через стандартный HTTP |
| **WebRTC** | Web Real-Time Communication - P2P коммуникация с аудио/видео | Использует UDP, DTLS, SRTP |
| **gRPC** | Google RPC фреймворк с Protocol Buffers и HTTP/2 | Поддерживает 4 типа streaming |
| **Socket.IO** | Библиотека поверх WebSocket с fallback и дополнениями | Event-based API, auto-reconnect |
| **ICE** | Interactive Connectivity Establishment - NAT traversal | Комбинация STUN и TURN |
| **STUN** | Session Traversal Utilities for NAT - обнаружение публичного IP | Используется WebRTC |
| **TURN** | Traversal Using Relays around NAT - relay через сервер | Fallback для симметричного NAT |
| **Backpressure** | Механизм контроля потока данных при перегрузке | Поддерживается Streams API |
| **EventSource** | Browser API для работы с SSE | Автоматический reconnect |
| **RTCPeerConnection** | WebRTC API для P2P соединений | Управление медиа потоками |
| **RTCDataChannel** | WebRTC канал для произвольных данных | Low-latency, binary support |

---

## Часть 1: Интуиция без кода

> Прежде чем погружаться в код, построим ментальные образы для каждого протокола

### Аналогия 1: WebSocket как телефонный звонок

**HTTP — это обмен письмами:**
```
Вы: [пишет письмо] "Есть новости?"     → Почта → Сервер
Сервер: [пишет ответ] "Нет новостей"   ← Почта ← Сервер
... через 5 секунд ...
Вы: [пишет письмо] "А теперь есть?"    → Почта → Сервер
```

**WebSocket — это телефонный звонок:**
```
┌─────────────────────────────────────────────────────┐
│  Вы          [ЗВОНОК УСТАНОВЛЕН]          Сервер   │
│   │              (один раз)                  │      │
│   │◄─────────────────────────────────────────┤      │
│   ├─────────────────────────────────────────►│      │
│   │         Мгновенный обмен                 │      │
│   │◄─────────────────────────────────────────┤      │
│   │         в обе стороны                    │      │
│   ├─────────────────────────────────────────►│      │
│   │         пока трубка поднята              │      │
└─────────────────────────────────────────────────────┘
```

**Ключевое отличие:**
- HTTP: каждый вопрос требует нового "конверта" с адресом и марками
- WebSocket: линия открыта — просто говорите

---

### Аналогия 2: SSE как радиоприёмник

**Server-Sent Events — это радиотрансляция:**
```
          📡 Радиостанция (Сервер)
              │
              │ Один поток вещания
              ▼
    ┌─────────────────────────┐
    │  📻  📻  📻  📻  📻    │
    │  Слушатели (клиенты)    │
    │                         │
    │  • Только принимают     │
    │  • Не могут ответить    │
    │  • Авто-reconnect       │
    └─────────────────────────┘
```

**Когда использовать:**
- Лента новостей (Twitter-like feed)
- Котировки акций
- Уведомления о событиях
- Прогресс длительной операции

**Преимущество перед WebSocket:**
- Работает через обычный HTTP (не нужен upgrade)
- Проще проходит через корпоративные proxy
- Автоматический reconnect встроен в браузер

---

### Аналогия 3: WebRTC как прямой видеозвонок

**WebSocket/HTTP — звонок через АТС (сервер):**
```
    Алиса                 Сервер                 Боб
      │                     │                     │
      ├────── данные ──────►├────── данные ──────►│
      │◄───── данные ───────┤◄───── данные ───────┤
      │                     │                     │
         Всё проходит через центр
         (+ задержка, + нагрузка на сервер)
```

**WebRTC — прямой звонок peer-to-peer:**
```
    Алиса ◄══════════════════════════════► Боб
                   │
                   │ Прямое соединение!
                   │ Минимальная задержка
                   │ Сервер не нужен*
                   │
    * кроме сигнального сервера для "знакомства"
```

**Три роли серверов в WebRTC:**
```
┌─────────────────────────────────────────────────────┐
│  1. Signaling Server — "Сваха"                      │
│     Помогает найти друг друга, передать SDP offer   │
│                                                     │
│  2. STUN Server — "Зеркало"                         │
│     "Твой публичный IP: 73.45.123.89:49152"         │
│     Нужен чтобы узнать себя за NAT                  │
│                                                     │
│  3. TURN Server — "Почтальон-посредник"             │
│     Когда P2P невозможен (strict NAT/firewall)      │
│     ~30% звонков требуют TURN                       │
└─────────────────────────────────────────────────────┘
```

---

### Аналогия 4: gRPC как экспресс-почта для программ

**REST API — обычная почта:**
```
┌─────────────────────────────────────────┐
│  Отправитель пишет на бумаге (JSON)     │
│  Упаковывает в конверт (HTTP)           │
│  Получатель читает и понимает           │
│                                         │
│  + Человекочитаемо                      │
│  + Простой debugging                    │
│  - Много "бумаги" (overhead)            │
│  - Медленная "распаковка" (parsing)     │
└─────────────────────────────────────────┘
```

**gRPC — экспресс-курьер с контрактом:**
```
┌─────────────────────────────────────────┐
│  Контракт заранее (.proto файл):        │
│  "Посылка весит X кг, размер Y"         │
│                                         │
│  Данные в бинарном виде (Protobuf)      │
│  HTTP/2 мультиплексирование             │
│  Типизация на этапе компиляции          │
│                                         │
│  + В 7-10 раз быстрее REST              │
│  + Streaming из коробки                 │
│  - Нечитаемо без .proto                 │
│  - Сложнее debugging                    │
└─────────────────────────────────────────┘
```

**Четыре режима gRPC:**
```
1. Unary:           Клиент ──► Сервер ──► Ответ
                    (как обычный REST)

2. Server Stream:   Клиент ──► Сервер ═══► Поток ответов
                    (скачивание большого файла)

3. Client Stream:   Клиент ═══► Сервер ──► Один ответ
                    (загрузка файла по частям)

4. Bidirectional:   Клиент ◄═══════════► Сервер
                    (чат, игры)
```

---

### Аналогия 5: NAT Traversal как поиск адреса за забором

**Проблема: ваш дом за забором (NAT)**
```
┌─────────────────────────────────────────────────────┐
│                    ИНТЕРНЕТ                         │
│                                                     │
│                  Ваш роутер                         │
│              ┌──────┴──────┐                        │
│              │ NAT ЗАБОР   │                        │
│              │             │                        │
│     Публичный IP: 73.45.123.89                      │
│              │             │                        │
│     ─────────┴─────────────┴─────────               │
│                    │                                │
│    ┌───────────────┼───────────────┐                │
│    │               │               │                │
│  Ваш ПК      Ваш телефон     IoT устройство         │
│ 192.168.1.5  192.168.1.6    192.168.1.7             │
│                                                     │
│    "Все 47 устройств имеют один публичный IP"       │
└─────────────────────────────────────────────────────┘
```

**STUN — узнать свой "внешний адрес":**
```
Вы: "Как я выгляжу снаружи?"

STUN сервер (публичный):
   │
   ▼
"Твой запрос пришёл с 73.45.123.89:49152"
   │
   ▼
Теперь вы знаете свой публичный IP:port
и можете сообщить его собеседнику
```

**TURN — когда P2P невозможен:**
```
Ситуация: Симметричный NAT или строгий firewall
          блокирует входящие соединения

Решение: TURN сервер как посредник

    Алиса ──────► TURN ◄────── Боб
                  │
                  │ Все данные через relay
                  │ Работает всегда, но:
                  │ - Больше latency
                  │ - Дороже (bandwidth)
```

---

## Часть 2: Почему это сложно

> 6 типичных ошибок при работе с real-time протоколами

### Ошибка 1: WebSocket для простых уведомлений

**СИМПТОМ:**
```
// Для простой ленты уведомлений создаём WebSocket
const ws = new WebSocket('/notifications');
ws.onmessage = (e) => showNotification(e.data);

// Проблемы:
// - Сложная логика reconnect
// - Нужен heartbeat
// - Проблемы с proxy/load balancers
```

**РЕШЕНИЕ:**
```javascript
// SSE намного проще для односторонних уведомлений
const events = new EventSource('/notifications');

events.onmessage = (e) => showNotification(e.data);
events.onerror = () => console.log('Авто-reconnect...');

// Преимущества:
// + Автоматический reconnect (встроен в браузер)
// + Работает через HTTP — дружит с proxy
// + Last-Event-ID для восстановления пропущенных
```

**Правило выбора:**
```
┌─────────────────────────────────────────────────────┐
│  Нужна двусторонняя связь?                          │
│     │                                               │
│     ├── ДА → WebSocket                              │
│     │        (чат, игры, collaborative editing)     │
│     │                                               │
│     └── НЕТ → SSE                                   │
│              (уведомления, ленты, котировки)        │
└─────────────────────────────────────────────────────┘
```

---

### Ошибка 2: Неправильная обработка reconnect

**СИМПТОМ:**
```javascript
// Наивный reconnect
ws.onclose = () => {
    new WebSocket(url);  // Немедленное переподключение
};

// Проблемы:
// 1. При проблемах сети — бесконечный цикл
// 2. Тысячи клиентов reconnect одновременно → DDoS своего сервера
// 3. Потеря сообщений между disconnect и reconnect
```

**РЕШЕНИЕ:**
```javascript
class ReconnectingWebSocket {
    constructor(url) {
        this.url = url;
        this.reconnectDelay = 1000;
        this.maxDelay = 30000;
        this.lastMessageId = null;
        this.connect();
    }

    connect() {
        // Восстановление с последнего сообщения
        const urlWithResume = this.lastMessageId
            ? `${this.url}?lastId=${this.lastMessageId}`
            : this.url;

        this.ws = new WebSocket(urlWithResume);

        this.ws.onmessage = (e) => {
            const msg = JSON.parse(e.data);
            this.lastMessageId = msg.id;
            this.reconnectDelay = 1000;  // Reset on success
            this.onmessage?.(msg);
        };

        this.ws.onclose = () => {
            // Exponential backoff с jitter
            const jitter = Math.random() * 1000;
            const delay = Math.min(this.reconnectDelay + jitter, this.maxDelay);

            console.log(`Reconnecting in ${delay}ms...`);
            setTimeout(() => this.connect(), delay);

            this.reconnectDelay *= 2;  // Exponential backoff
        };
    }
}
```

---

### Ошибка 3: Забыть про heartbeat

**СИМПТОМ:**
```
Соединение "живое" по мнению клиента,
но на самом деле TCP connection давно умер.

Причины:
- NAT timeout (обычно 30-120 секунд без активности)
- Мобильная сеть переключилась
- Промежуточный proxy закрыл соединение
```

**РЕШЕНИЕ:**
```javascript
class HeartbeatWebSocket {
    constructor(url) {
        this.pingInterval = 25000;  // < NAT timeout (обычно 30s)
        this.pongTimeout = 5000;
        this.connect(url);
    }

    connect(url) {
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            this.startHeartbeat();
        };

        this.ws.onmessage = (e) => {
            if (e.data === 'pong') {
                this.pongReceived = true;
                return;
            }
            // ... handle other messages
        };
    }

    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            this.pongReceived = false;
            this.ws.send('ping');

            // Если pong не пришёл за 5 секунд — connection dead
            setTimeout(() => {
                if (!this.pongReceived) {
                    console.log('Connection dead, reconnecting...');
                    this.ws.close();
                }
            }, this.pongTimeout);
        }, this.pingInterval);
    }
}
```

---

### Ошибка 4: WebRTC без TURN fallback

**СИМПТОМ:**
```
"WebRTC работает в офисе, но не работает у клиентов"

Причина: ~30% пользователей за symmetric NAT или
         строгими корпоративными firewalls
```

**РЕШЕНИЕ:**
```javascript
// ВСЕГДА включайте TURN сервер как fallback
const config = {
    iceServers: [
        // STUN — бесплатный, для простых NAT
        { urls: 'stun:stun.l.google.com:19302' },

        // TURN — платный, но работает ВСЕГДА
        {
            urls: 'turn:your-turn-server.com:3478',
            username: 'user',
            credential: 'pass'
        },

        // TURNS — TURN over TLS (через 443 порт)
        // Проходит даже через строгие firewalls
        {
            urls: 'turns:your-turn-server.com:443',
            username: 'user',
            credential: 'pass'
        }
    ]
};

const pc = new RTCPeerConnection(config);

// Мониторинг типа соединения
pc.oniceconnectionstatechange = () => {
    console.log('ICE state:', pc.iceConnectionState);

    // Проверяем, используется ли relay (TURN)
    pc.getStats().then(stats => {
        stats.forEach(report => {
            if (report.type === 'candidate-pair' && report.state === 'succeeded') {
                console.log('Connection type:', report.remoteCandidateType);
                // 'host' = direct, 'srflx' = STUN, 'relay' = TURN
            }
        });
    });
};
```

---

### Ошибка 5: gRPC streaming для простых запросов

**СИМПТОМ:**
```protobuf
// Оверинжиниринг: streaming для одного запроса
service UserService {
    rpc GetUser(stream GetUserRequest) returns (stream User);
}

// Клиент:
stream = client.GetUser()
stream.write(GetUserRequest(id=123))
response = stream.read()
stream.close()

// 4 шага вместо одного!
```

**РЕШЕНИЕ:**
```protobuf
// Unary RPC для простых запросов
service UserService {
    // Простой запрос-ответ
    rpc GetUser(GetUserRequest) returns (User);

    // Streaming только когда НУЖНО:
    // - Большие данные (файлы, логи)
    // - Непрерывный поток (метрики, события)
    // - Bidirectional (чат)
    rpc StreamMetrics(MetricsRequest) returns (stream Metric);
    rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}
```

**Когда использовать streaming:**
```
┌─────────────────────────────────────────────────────┐
│  Unary (request-response):                          │
│    • CRUD операции                                  │
│    • Аутентификация                                 │
│    • Любой "вопрос-ответ"                          │
│                                                     │
│  Server streaming:                                  │
│    • Скачивание больших файлов                      │
│    • Пагинация без offset                          │
│    • Подписка на события                           │
│                                                     │
│  Client streaming:                                  │
│    • Загрузка файлов по частям                      │
│    • Batch операции                                │
│                                                     │
│  Bidirectional:                                     │
│    • Чат                                            │
│    • Игры в реальном времени                        │
│    • Collaborative editing                          │
└─────────────────────────────────────────────────────┘
```

---

### Ошибка 6: Игнорирование backpressure

**СИМПТОМ:**
```
Сервер отправляет данные быстрее, чем клиент обрабатывает.
Результат: OOM, зависания, потеря данных.

Пример: стриминг 1000 сообщений/сек на медленный клиент
```

**РЕШЕНИЕ:**
```javascript
// Node.js с явным backpressure
class BackpressureWebSocket {
    constructor(ws) {
        this.ws = ws;
        this.queue = [];
        this.sending = false;
    }

    send(data) {
        this.queue.push(data);
        this.drain();
    }

    drain() {
        if (this.sending) return;

        while (this.queue.length > 0) {
            // Проверяем bufferedAmount
            if (this.ws.bufferedAmount > 1024 * 1024) {
                // Буфер переполнен — ждём
                this.sending = true;
                setTimeout(() => {
                    this.sending = false;
                    this.drain();
                }, 100);
                return;
            }

            this.ws.send(this.queue.shift());
        }
    }
}

// gRPC с flow control
async function* generateData() {
    for (const item of largeDataset) {
        yield item;
        // gRPC автоматически применяет backpressure
        // через HTTP/2 flow control
    }
}
```

---

## Часть 3: Ментальные модели

### Модель 1: Спектр Latency

```
                    LATENCY / COMPLEXITY
    ◄────────────────────────────────────────────────►
    LOW                                            HIGH

    Polling ─► Long-Polling ─► SSE ─► WebSocket ─► WebRTC

    ┌──────────┬─────────────┬───────────────────────┐
    │ Polling  │ 1-30 сек    │ Пустые запросы,       │
    │          │ задержка    │ нагрузка на сервер    │
    ├──────────┼─────────────┼───────────────────────┤
    │ Long-    │ 0-30 сек    │ Держит соединение,    │
    │ Polling  │             │ сложный для балансера │
    ├──────────┼─────────────┼───────────────────────┤
    │ SSE      │ ~0 мс       │ Только server→client  │
    │          │             │ Простой, HTTP-based   │
    ├──────────┼─────────────┼───────────────────────┤
    │ WebSocket│ ~0 мс       │ Bidirectional         │
    │          │             │ Нужен upgrade, proxy  │
    ├──────────┼─────────────┼───────────────────────┤
    │ WebRTC   │ ~0 мс       │ P2P, минимальный hop  │
    │          │             │ Сложный setup (ICE)   │
    └──────────┴─────────────┴───────────────────────┘
```

---

### Модель 2: Направление потока данных

```
┌─────────────────────────────────────────────────────┐
│           UNIDIRECTIONAL (Server → Client)          │
│  ┌─────────────────────────────────────────────┐    │
│  │  SSE, Server Push, gRPC Server Streaming    │    │
│  │                                             │    │
│  │  Клиент: "Подписаться на обновления"        │    │
│  │  Сервер: "Вот новые данные... ещё... ещё"   │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│           BIDIRECTIONAL (Client ↔ Server)           │
│  ┌─────────────────────────────────────────────┐    │
│  │  WebSocket, gRPC Bidirectional, WebRTC      │    │
│  │                                             │    │
│  │  Оба могут инициировать сообщения           │    │
│  │  в любой момент                             │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘

Вопрос для выбора: "Клиенту нужно отправлять данные
                   ПОСЛЕ установки соединения?"

    НЕТ → SSE (проще, надёжнее)
    ДА  → WebSocket / gRPC / WebRTC
```

---

### Модель 3: Топология соединений

```
┌─────────────────────────────────────────────────────┐
│  CLIENT-SERVER (звезда)                             │
│  ═══════════════════════                            │
│                                                     │
│       C1  C2  C3  C4  C5                            │
│        \  |   |   |  /                              │
│         \ |   |   | /                               │
│          \|   |   |/                                │
│           ════S════                                 │
│                                                     │
│  Протоколы: HTTP, WebSocket, SSE, gRPC              │
│  Плюсы: Простая авторизация, централизованная логика│
│  Минусы: Сервер — узкое место, latency через центр  │
│                                                     │
├─────────────────────────────────────────────────────┤
│  PEER-TO-PEER (mesh)                                │
│  ═══════════════════                                │
│                                                     │
│       C1 ════════ C2                                │
│       ║ ╲        ╱ ║                                │
│       ║  ╲      ╱  ║                                │
│       ║   ╲    ╱   ║                                │
│       ║    ╲  ╱    ║                                │
│       C4 ════════ C3                                │
│                                                     │
│  Протоколы: WebRTC                                  │
│  Плюсы: Минимальная latency, нет нагрузки на сервер │
│  Минусы: NAT traversal, N*(N-1)/2 соединений        │
│                                                     │
├─────────────────────────────────────────────────────┤
│  HYBRID (SFU — Selective Forwarding Unit)           │
│  ═══════════════════════════════════════            │
│                                                     │
│       C1  C2  C3  C4                                │
│        \  |   |  /                                  │
│         \ |   | /                                   │
│          SFU═════                                   │
│                                                     │
│  Протоколы: WebRTC + Media Server                   │
│  Используется: Zoom, Google Meet, Discord           │
│  Каждый отправляет 1 поток, получает N-1            │
└─────────────────────────────────────────────────────┘
```

---

### Модель 4: NAT Traversal как навигация

```
Представьте: вы хотите доставить посылку другу,
но оба живёте в закрытых посёлках (NAT).

┌─────────────────────────────────────────────────────┐
│  ШАГ 1: Узнать свой "внешний адрес" (STUN)          │
│  ──────────────────────────────────────────         │
│                                                     │
│  Вы звоните на публичный номер:                     │
│  "С какого номера я звоню?"                         │
│  "Вы звоните с +7-XXX-XXX-XXXX"                     │
│                                                     │
│  Теперь знаете свой публичный IP:port               │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ШАГ 2: Обмен адресами (Signaling)                  │
│  ─────────────────────────────────                  │
│                                                     │
│  Через общего знакомого (signaling server):         │
│  "Передай Бобу мой адрес: 73.45.123.89:49152"       │
│  "Передай Алисе мой адрес: 82.12.45.67:51234"       │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ШАГ 3: Попытка прямого соединения (ICE)            │
│  ───────────────────────────────────────            │
│                                                     │
│  ICE пробует все варианты:                          │
│  1. Прямой IP (host candidate) — если в одной сети  │
│  2. STUN адрес (srflx) — если NAT "дружелюбный"     │
│  3. TURN relay — если ничего не работает            │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ШАГ 4: TURN как последний resort                   │
│  ───────────────────────────────                    │
│                                                     │
│  Когда P2P невозможен:                              │
│  Алиса → TURN сервер → Боб                          │
│                                                     │
│  Как отправка через почтовое отделение:             │
│  работает всегда, но медленнее и дороже             │
└─────────────────────────────────────────────────────┘
```

---

### Модель 5: Выбор протокола как выбор транспорта

```
┌─────────────────────────────────────────────────────┐
│  ВОПРОС                          →  ПРОТОКОЛ        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  "Нужно уведомлять клиента о событиях"              │
│  └──► SSE (простой, надёжный, HTTP-based)           │
│                                                     │
│  "Клиент и сервер обмениваются в реальном времени"  │
│  └──► WebSocket (чат, игры, collaborative)          │
│                                                     │
│  "P2P видео/аудио между пользователями"             │
│  └──► WebRTC (минимальная latency, P2P)             │
│                                                     │
│  "Микросервисы общаются между собой"                │
│  └──► gRPC (типизация, streaming, производительность│
│                                                     │
│  "Нужен fallback для старых браузеров"              │
│  └──► Socket.IO (WS + long-polling fallback)        │
│                                                     │
│  "Публичный API для внешних разработчиков"          │
│  └──► REST или GraphQL (не gRPC!)                   │
│                                                     │
└─────────────────────────────────────────────────────┘

Гибридный подход (2025):
┌─────────────────────────────────────────────────────┐
│  • REST — публичные API, CRUD                       │
│  • gRPC — внутренние микросервисы                   │
│  • WebSocket/SSE — real-time клиентские фичи        │
│  • WebRTC — P2P медиа                               │
│  • Kafka/NATS — async события между сервисами       │
└─────────────────────────────────────────────────────┘
```

---

## ПОЧЕМУ: Зачем нужны real-time протоколы

### Проблемы классического HTTP

**HTTP запрос-ответ не подходит для real-time:**

1. **Неэффективность polling**
   - Постоянные HTTP запросы каждые N секунд
   - Пустые ответы при отсутствии данных
   - Высокая нагрузка на сервер и клиент
   - Задержка до N секунд

2. **Long-polling ограничения**
   - Удержание соединения до получения данных
   - Необходимость постоянного переподключения
   - Проблемы с timeout и proxy
   - Сложность масштабирования

3. **HTTP/1.1 overhead**
   - Полные HTTP заголовки в каждом запросе
   - Head-of-line blocking
   - Невозможность server push

### Решаемые проблемы

**Real-time протоколы решают:**

- **Мгновенные обновления** - данные push'ятся сразу при появлении
- **Низкая latency** - WebSocket ~50ms vs polling seconds
- **Снижение нагрузки** - одно соединение вместо тысяч запросов
- **Bidirectional** - одновременная отправка в обе стороны
- **Эффективность** - минимальный overhead на фреймы

### Use Cases

**Когда необходим real-time:**

| Сценарий | Требования | Подходящий протокол |
|----------|------------|---------------------|
| Chat приложения | Bidirectional, низкая latency | WebSocket, Socket.IO |
| Live updates (биржа, спорт) | Server-to-client push | SSE |
| Collaborative editing | Bidirectional, частые обновления | WebSocket |
| Video/audio звонки | P2P, низкая latency, UDP | WebRTC |
| Микросервисы communication | Binary, streaming, typed | gRPC |
| Gaming multiplayer | Низкая latency, bidirectional | WebSocket, WebRTC |
| IoT sensor data | Continuous streaming | gRPC, WebSocket |
| Live notifications | Server push, auto-reconnect | SSE |

---

## ЧТО: Обзор real-time протоколов

### WebSocket

**Полнодуплексный протокол поверх TCP с upgrade от HTTP**

#### Основные характеристики

- **Протокол:** RFC 6455 (2011), Living Standard WHATWG (2025)
- **Transport:** TCP с upgrade от HTTP
- **Схемы URI:** `ws://` (port 80), `wss://` (port 443 TLS)
- **Направление:** Bidirectional (full-duplex)
- **Данные:** Text (UTF-8) и Binary (ArrayBuffer, Blob)
- **Reconnection:** Отсутствует (требует реализации)

#### WebSocket Handshake

```
Client → Server:
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

Server → Client:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

#### WebSocket Frame Structure

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
```

**Opcodes:**
- `0x0` - Continuation frame
- `0x1` - Text frame
- `0x2` - Binary frame
- `0x8` - Connection close
- `0x9` - Ping
- `0xA` - Pong

#### Преимущества

- Полная bidirectional коммуникация
- Минимальный overhead после handshake
- Binary data support
- Широкая поддержка браузеров и серверов
- Низкая latency (~50ms)

#### Недостатки

- Нет встроенного reconnect
- Нет встроенного backpressure (решается WebSocketStream)
- Сложнее масштабировать чем SSE
- Требует отдельного протокола поверх для room/broadcast

---

### Server-Sent Events (SSE)

**Однонаправленный server-to-client push через стандартный HTTP**

#### Основные характеристики

- **Протокол:** HTML5 EventSource API
- **Transport:** HTTP/HTTPS (стандартный)
- **Направление:** Unidirectional (server → client)
- **Данные:** Text only (UTF-8)
- **Reconnection:** Автоматический с exponential backoff
- **Content-Type:** `text/event-stream`

#### SSE Message Format

```
data: Simple message\n\n

data: Multi-line\n
data: message\n\n

id: 123\n
event: userUpdate\n
data: {"user": "John", "status": "online"}\n\n

retry: 5000\n\n
```

**Поля:**
- `data:` - содержимое сообщения (может быть многострочным)
- `event:` - имя события (по умолчанию "message")
- `id:` - идентификатор для Last-Event-ID при reconnect
- `retry:` - задержка перед reconnect в миллисекундах

#### HTTP/2 Multiplexing

**С HTTP/1.1:** максимум 6 параллельных SSE соединений

**С HTTP/2:** множество SSE streams через одно TCP соединение:
- Multiplexing устраняет connection limit
- Более эффективное использование ресурсов
- Single TCP connection для всех streams

#### Преимущества

- Простота реализации (стандартный HTTP)
- Автоматический reconnect с Last-Event-ID
- Поддержка HTTP/2 multiplexing
- Работает через стандартные proxy/firewall
- Меньше overhead для server push
- Event-based API из коробки

#### Недостатки

- Только text data (нет binary)
- Только server → client (нет bidirectional)
- Ограничения HTTP/1.1 (решается HTTP/2)
- Нет встроенной поддержки rooms/channels

---

### WebRTC (Web Real-Time Communication)

**P2P коммуникация с аудио/видео прямо в браузере**

#### Основные характеристики

- **Стандарт:** W3C WebRTC + IETF протоколы
- **Transport:** UDP (SRTP для медиа, SCTP для данных)
- **Направление:** Bidirectional P2P
- **Latency:** Очень низкая (~50ms)
- **NAT Traversal:** ICE (STUN + TURN)
- **Шифрование:** Обязательное (DTLS, SRTP)

#### WebRTC Architecture

```
Peer A                                    Peer B
  |                                          |
  |-- Signaling (WebSocket/HTTP) ---------->|
  |<--------- Signaling ---------------------|
  |                                          |
  |======== ICE Connection Check ===========>|
  |<======== ICE Connection Check ===========|
  |                                          |
  |######## P2P Media/Data Streams #########>|
  |<####### P2P Media/Data Streams ##########|
```

#### NAT Traversal: ICE, STUN, TURN

**1. STUN (Session Traversal Utilities for NAT)**
- Обнаруживает публичный IP:port
- Определяет тип NAT
- Большинство соединений проходят через STUN

**2. TURN (Traversal Using Relays around NAT)**
- Relay сервер для симметричного NAT
- Fallback когда P2P невозможен
- Выше latency, требует больше ресурсов

**3. ICE (Interactive Connectivity Establishment)**
- Пробует все возможные пути
- Собирает candidates (local, reflexive, relay)
- Выбирает оптимальный путь

#### WebRTC Components

**RTCPeerConnection:**
- Управление P2P соединением
- Negotiation через SDP (Session Description Protocol)
- Media streams management

**RTCDataChannel:**
- Произвольные данные поверх SCTP
- Binary и text support
- Настраиваемая надежность (ordered/unordered, reliable/unreliable)

**MediaStream:**
- Захват локального аудио/видео
- Tracks management

#### Преимущества

- Прямая P2P коммуникация (низкая latency)
- Встроенное end-to-end encryption
- Поддержка аудио/видео из коробки
- RTCDataChannel для любых данных
- Адаптивный bitrate
- Широкая поддержка браузеров (2025)

#### Недостатки

- Сложность настройки и отладки
- Требует signaling server
- TURN server для ~10-20% соединений
- Firewall/NAT issues
- Не подходит для server-based broadcasting

---

### gRPC Streaming

**High-performance RPC с Protocol Buffers и HTTP/2**

#### Основные характеристики

- **Протокол:** HTTP/2
- **Сериализация:** Protocol Buffers (binary)
- **Направление:** 4 типа (Unary, Server, Client, Bidirectional)
- **Transport:** TCP
- **Типизация:** Строгая через .proto схемы

#### Типы gRPC вызовов

**1. Unary RPC (стандартный запрос-ответ)**
```protobuf
rpc GetUser(GetUserRequest) returns (GetUserResponse);
```

**2. Server Streaming**
```protobuf
rpc StreamPrices(SubscribeRequest) returns (stream PriceUpdate);
```

**3. Client Streaming**
```protobuf
rpc UploadFile(stream FileChunk) returns (UploadResponse);
```

**4. Bidirectional Streaming**
```protobuf
rpc Chat(stream ChatMessage) returns (stream ChatMessage);
```

#### gRPC HTTP/2 Features

- **Multiplexing:** множество streams через одно соединение
- **Header compression:** HPACK для эффективности
- **Binary protocol:** меньше overhead чем HTTP/1.1 text
- **Flow control:** встроенный backpressure
- **Server push:** для proactive data delivery

#### Преимущества

- Высокая производительность (binary, HTTP/2)
- Строгая типизация через Protocol Buffers
- Code generation для многих языков
- Встроенный streaming (4 типа)
- Эффективная сериализация (~3-10x меньше JSON)
- Deadlines и cancellation из коробки

#### Недостатки

- Нет нативной поддержки в браузерах (нужен gRPC-Web)
- Сложность debugging (binary protocol)
- Требует HTTP/2
- Learning curve для Protocol Buffers
- Ограниченная поддержка в некоторых языках

---

### Socket.IO

**Библиотека поверх WebSocket с fallback и удобствами**

#### Основные характеристики

- **Тип:** JavaScript библиотека (не протокол)
- **Базируется на:** WebSocket с fallback (HTTP long-polling)
- **API:** Event-based
- **Features:** Rooms, namespaces, broadcast, auto-reconnect

#### Socket.IO Message Overhead

**Native WebSocket:**
```
Binary frame: 2-14 bytes header + payload
```

**Socket.IO:**
```
Event wrapper: {"event":"message","data":"..."}
+ namespace/room metadata
+ acknowledgment callbacks
```

Overhead ~20-50% больше чем native WebSocket

#### Основные возможности

**1. Automatic Reconnection**
```javascript
const socket = io({
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: Infinity
});
```

**2. Rooms**
```javascript
// Server
socket.join('room1');
io.to('room1').emit('news', data);

// Broadcasting
socket.broadcast.emit('event', data);
```

**3. Namespaces**
```javascript
const chat = io('/chat');
const notifications = io('/notifications');
```

**4. Acknowledgments**
```javascript
socket.emit('update', data, (response) => {
  console.log(response);
});
```

#### Преимущества

- Автоматический reconnect с exponential backoff
- Fallback на HTTP long-polling
- Rooms и namespaces из коробки
- Acknowledgments для request-response
- Проще масштабировать с Redis adapter
- Удобный event-based API

#### Недостатки

- Больший размер bundle (~40KB min+gzip)
- Performance overhead vs native WebSocket
- Дополнительная сложность для простых случаев
- Несовместимость с чистым WebSocket
- Требует Socket.IO на сервере

---

## КАК: Примеры кода и использование

### WebSocket: Chat Application

#### JavaScript/TypeScript Client

```typescript
// Basic WebSocket connection
const ws = new WebSocket('wss://example.com/chat');

// Connection events
ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({ type: 'join', user: 'Alice' }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
  console.log('Closed:', event.code, event.reason);
  // Manual reconnect logic
  setTimeout(() => reconnect(), 5000);
};

// Send binary data
const buffer = new Uint8Array([1, 2, 3, 4]);
ws.send(buffer);

// Close connection
ws.close(1000, 'Normal closure');
```

**Reconnection with exponential backoff:**

```typescript
class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private reconnectAttempts = 0;

  connect(url: string) {
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('Connected');
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
    };

    this.ws.onclose = () => {
      this.reconnect(url);
    };
  }

  private reconnect(url: string) {
    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    setTimeout(() => this.connect(url), delay);
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}
```

#### Kotlin/Android Client

```kotlin
import okhttp3.*
import okio.ByteString

class ChatWebSocketClient {
    private var webSocket: WebSocket? = null
    private val client = OkHttpClient()

    fun connect(url: String) {
        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                println("Connected")
                sendMessage("""{"type":"join","user":"Alice"}""")
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                println("Received: $text")
                // Parse JSON and update UI
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                println("Received binary: ${bytes.hex()}")
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
                println("Closing: $code $reason")
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                println("Error: ${t.message}")
                // Implement reconnection logic
            }
        })
    }

    fun sendMessage(message: String) {
        webSocket?.send(message)
    }

    fun disconnect() {
        webSocket?.close(1000, "Normal closure")
    }
}

// Usage
val chatClient = ChatWebSocketClient()
chatClient.connect("wss://example.com/chat")
chatClient.sendMessage("""{"type":"message","text":"Hello"}""")
```

---

### Server-Sent Events: Live Updates

#### JavaScript Client

```javascript
// Basic SSE connection
const eventSource = new EventSource('/api/updates');

// Default "message" event
eventSource.onmessage = (event) => {
  console.log('New message:', event.data);
  console.log('ID:', event.lastEventId);
};

// Custom event types
eventSource.addEventListener('priceUpdate', (event) => {
  const data = JSON.parse(event.data);
  updatePriceDisplay(data);
});

eventSource.addEventListener('userStatus', (event) => {
  const { user, status } = JSON.parse(event.data);
  updateUserStatus(user, status);
});

// Connection state
eventSource.onopen = () => {
  console.log('SSE connected');
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  if (eventSource.readyState === EventSource.CLOSED) {
    console.log('Connection closed');
  }
  // Browser will auto-reconnect
};

// Manual close
eventSource.close();
```

**With Last-Event-ID for resume:**

```javascript
// Server example (Node.js/Express)
app.get('/api/updates', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const lastEventId = req.headers['last-event-id'];
  console.log('Resume from:', lastEventId);

  let messageId = lastEventId ? parseInt(lastEventId) : 0;

  const interval = setInterval(() => {
    messageId++;
    res.write(`id: ${messageId}\n`);
    res.write(`event: priceUpdate\n`);
    res.write(`data: ${JSON.stringify({ symbol: 'BTC', price: 50000 })}\n\n`);
  }, 1000);

  req.on('close', () => {
    clearInterval(interval);
  });
});
```

#### Kotlin/Android Client (OkHttp SSE)

```kotlin
import okhttp3.*
import okhttp3.sse.EventSource
import okhttp3.sse.EventSourceListener
import okhttp3.sse.EventSources

class SSEClient {
    private val client = OkHttpClient()
    private var eventSource: EventSource? = null

    fun connect(url: String) {
        val request = Request.Builder()
            .url(url)
            .header("Accept", "text/event-stream")
            .build()

        eventSource = EventSources.createFactory(client)
            .newEventSource(request, object : EventSourceListener() {
                override fun onOpen(eventSource: EventSource, response: Response) {
                    println("SSE Connected")
                }

                override fun onEvent(
                    eventSource: EventSource,
                    id: String?,
                    type: String?,
                    data: String
                ) {
                    println("Event[$type] ID[$id]: $data")

                    when (type) {
                        "priceUpdate" -> handlePriceUpdate(data)
                        "userStatus" -> handleUserStatus(data)
                        else -> handleMessage(data)
                    }
                }

                override fun onClosed(eventSource: EventSource) {
                    println("SSE Closed")
                }

                override fun onFailure(
                    eventSource: EventSource,
                    t: Throwable?,
                    response: Response?
                ) {
                    println("SSE Error: ${t?.message}")
                    // Auto-reconnect handled by library
                }
            })
    }

    private fun handlePriceUpdate(data: String) {
        // Parse JSON and update UI
    }

    fun disconnect() {
        eventSource?.cancel()
    }
}

// Usage
val sseClient = SSEClient()
sseClient.connect("https://api.example.com/updates")
```

---

### WebRTC: Video Chat

#### JavaScript Implementation

```javascript
// WebRTC peer connection with signaling
class VideoChatClient {
  constructor(signalServer) {
    this.pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        {
          urls: 'turn:turn.example.com:3478',
          username: 'user',
          credential: 'pass'
        }
      ]
    });

    this.signaling = new WebSocket(signalServer);
    this.setupSignaling();
    this.setupPeerConnection();
  }

  setupPeerConnection() {
    // ICE candidates
    this.pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.signaling.send(JSON.stringify({
          type: 'ice-candidate',
          candidate: event.candidate
        }));
      }
    };

    // Remote stream
    this.pc.ontrack = (event) => {
      const remoteVideo = document.getElementById('remoteVideo');
      remoteVideo.srcObject = event.streams[0];
    };
  }

  setupSignaling() {
    this.signaling.onmessage = async (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'offer':
          await this.handleOffer(message.offer);
          break;
        case 'answer':
          await this.handleAnswer(message.answer);
          break;
        case 'ice-candidate':
          await this.handleIceCandidate(message.candidate);
          break;
      }
    };
  }

  async startCall() {
    // Get local media
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });

    const localVideo = document.getElementById('localVideo');
    localVideo.srcObject = stream;

    // Add tracks to peer connection
    stream.getTracks().forEach(track => {
      this.pc.addTrack(track, stream);
    });

    // Create offer
    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);

    this.signaling.send(JSON.stringify({
      type: 'offer',
      offer: offer
    }));
  }

  async handleOffer(offer) {
    await this.pc.setRemoteDescription(new RTCSessionDescription(offer));

    // Get local media
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });

    stream.getTracks().forEach(track => {
      this.pc.addTrack(track, stream);
    });

    // Create answer
    const answer = await this.pc.createAnswer();
    await this.pc.setLocalDescription(answer);

    this.signaling.send(JSON.stringify({
      type: 'answer',
      answer: answer
    }));
  }

  async handleAnswer(answer) {
    await this.pc.setRemoteDescription(new RTCSessionDescription(answer));
  }

  async handleIceCandidate(candidate) {
    await this.pc.addIceCandidate(new RTCIceCandidate(candidate));
  }

  // Data channel for chat/metadata
  createDataChannel() {
    const dataChannel = this.pc.createDataChannel('chat');

    dataChannel.onopen = () => {
      console.log('Data channel open');
      dataChannel.send('Hello!');
    };

    dataChannel.onmessage = (event) => {
      console.log('Received:', event.data);
    };

    return dataChannel;
  }
}

// Usage
const client = new VideoChatClient('wss://signal.example.com');
client.startCall();
```

#### Kotlin/Android WebRTC

```kotlin
import org.webrtc.*

class WebRTCClient(
    private val context: Context,
    private val signalingClient: SignalingClient
) {
    private val peerConnectionFactory: PeerConnectionFactory
    private var peerConnection: PeerConnection? = null
    private val eglBase = EglBase.create()

    init {
        PeerConnectionFactory.initialize(
            PeerConnectionFactory.InitializationOptions
                .builder(context)
                .createInitializationOptions()
        )

        peerConnectionFactory = PeerConnectionFactory.builder()
            .setVideoEncoderFactory(
                DefaultVideoEncoderFactory(
                    eglBase.eglBaseContext,
                    true,
                    true
                )
            )
            .setVideoDecoderFactory(
                DefaultVideoDecoderFactory(eglBase.eglBaseContext)
            )
            .createPeerConnectionFactory()
    }

    fun createPeerConnection() {
        val iceServers = listOf(
            PeerConnection.IceServer.builder("stun:stun.l.google.com:19302").createIceServer(),
            PeerConnection.IceServer.builder("turn:turn.example.com:3478")
                .setUsername("user")
                .setPassword("pass")
                .createIceServer()
        )

        peerConnection = peerConnectionFactory.createPeerConnection(
            iceServers,
            object : PeerConnection.Observer {
                override fun onIceCandidate(candidate: IceCandidate) {
                    signalingClient.sendIceCandidate(candidate)
                }

                override fun onAddStream(stream: MediaStream) {
                    // Handle remote stream
                }

                override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) {
                    println("ICE Connection: $state")
                }

                // ... other callbacks
            }
        )
    }

    fun startCall(localVideoTrack: VideoTrack, audioTrack: AudioTrack) {
        val stream = peerConnectionFactory.createLocalMediaStream("local")
        stream.addTrack(localVideoTrack)
        stream.addTrack(audioTrack)

        peerConnection?.addStream(stream)

        peerConnection?.createOffer(object : SdpObserver {
            override fun onCreateSuccess(description: SessionDescription) {
                peerConnection?.setLocalDescription(object : SdpObserver {
                    override fun onSetSuccess() {
                        signalingClient.sendOffer(description)
                    }
                    // ... other callbacks
                }, description)
            }
            // ... other callbacks
        }, MediaConstraints())
    }

    fun handleOffer(offer: SessionDescription) {
        peerConnection?.setRemoteDescription(object : SdpObserver {
            override fun onSetSuccess() {
                peerConnection?.createAnswer(object : SdpObserver {
                    override fun onCreateSuccess(answer: SessionDescription) {
                        peerConnection?.setLocalDescription(object : SdpObserver {
                            override fun onSetSuccess() {
                                signalingClient.sendAnswer(answer)
                            }
                            // ... other callbacks
                        }, answer)
                    }
                    // ... other callbacks
                }, MediaConstraints())
            }
            // ... other callbacks
        }, offer)
    }
}
```

---

### gRPC: Bidirectional Streaming

#### Protocol Buffers Definition

```protobuf
syntax = "proto3";

package chat;

service ChatService {
  // Unary
  rpc SendMessage(ChatMessage) returns (SendResponse);

  // Server streaming
  rpc StreamMessages(SubscribeRequest) returns (stream ChatMessage);

  // Client streaming
  rpc UploadImages(stream ImageChunk) returns (UploadResponse);

  // Bidirectional streaming
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message ChatMessage {
  string user = 1;
  string text = 2;
  int64 timestamp = 3;
}

message SubscribeRequest {
  string room = 1;
}

message SendResponse {
  bool success = 1;
  string message_id = 2;
}

message ImageChunk {
  bytes data = 1;
  int32 chunk_number = 2;
}

message UploadResponse {
  string image_url = 1;
}
```

#### Kotlin/Android gRPC Client

```kotlin
import io.grpc.ManagedChannelBuilder
import io.grpc.stub.StreamObserver
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class ChatGrpcClient(serverAddress: String) {
    private val channel = ManagedChannelBuilder
        .forTarget(serverAddress)
        .usePlaintext() // Use .useTransportSecurity() for TLS
        .build()

    private val asyncStub = ChatServiceGrpc.newStub(channel)
    private val blockingStub = ChatServiceGrpc.newBlockingStub(channel)

    // Unary RPC
    fun sendMessage(user: String, text: String) {
        val request = ChatMessage.newBuilder()
            .setUser(user)
            .setText(text)
            .setTimestamp(System.currentTimeMillis())
            .build()

        asyncStub.sendMessage(request, object : StreamObserver<SendResponse> {
            override fun onNext(response: SendResponse) {
                println("Message sent: ${response.messageId}")
            }

            override fun onError(t: Throwable) {
                println("Error: ${t.message}")
            }

            override fun onCompleted() {
                println("Send completed")
            }
        })
    }

    // Server streaming
    fun streamMessages(room: String, onMessage: (ChatMessage) -> Unit) {
        val request = SubscribeRequest.newBuilder()
            .setRoom(room)
            .build()

        asyncStub.streamMessages(request, object : StreamObserver<ChatMessage> {
            override fun onNext(message: ChatMessage) {
                onMessage(message)
            }

            override fun onError(t: Throwable) {
                println("Stream error: ${t.message}")
            }

            override fun onCompleted() {
                println("Stream completed")
            }
        })
    }

    // Bidirectional streaming
    fun chat(
        onMessageReceived: (ChatMessage) -> Unit
    ): StreamObserver<ChatMessage> {
        val responseObserver = object : StreamObserver<ChatMessage> {
            override fun onNext(message: ChatMessage) {
                onMessageReceived(message)
            }

            override fun onError(t: Throwable) {
                println("Chat error: ${t.message}")
            }

            override fun onCompleted() {
                println("Chat completed")
            }
        }

        return asyncStub.chat(responseObserver)
    }

    fun shutdown() {
        channel.shutdown()
    }
}

// Usage
fun main() = runBlocking {
    val client = ChatGrpcClient("localhost:50051")

    // Send unary message
    client.sendMessage("Alice", "Hello!")

    // Stream messages from server
    client.streamMessages("general") { message ->
        println("${message.user}: ${message.text}")
    }

    // Bidirectional chat
    val chatStream = client.chat { message ->
        println("Received: ${message.user}: ${message.text}")
    }

    // Send messages
    launch {
        repeat(10) { i ->
            val message = ChatMessage.newBuilder()
                .setUser("Alice")
                .setText("Message $i")
                .setTimestamp(System.currentTimeMillis())
                .build()
            chatStream.onNext(message)
            delay(1000)
        }
        chatStream.onCompleted()
    }

    delay(15000)
    client.shutdown()
}
```

#### TypeScript gRPC-Web Client

```typescript
import { ChatServiceClient } from './generated/chat_grpc_web_pb';
import { ChatMessage, SubscribeRequest } from './generated/chat_pb';

class ChatClient {
  private client: ChatServiceClient;

  constructor(serverUrl: string) {
    this.client = new ChatServiceClient(serverUrl);
  }

  // Unary call
  async sendMessage(user: string, text: string): Promise<void> {
    const request = new ChatMessage();
    request.setUser(user);
    request.setText(text);
    request.setTimestamp(Date.now());

    return new Promise((resolve, reject) => {
      this.client.sendMessage(request, {}, (err, response) => {
        if (err) {
          reject(err);
        } else {
          console.log('Message sent:', response.getMessageId());
          resolve();
        }
      });
    });
  }

  // Server streaming
  streamMessages(room: string, onMessage: (message: ChatMessage) => void): void {
    const request = new SubscribeRequest();
    request.setRoom(room);

    const stream = this.client.streamMessages(request, {});

    stream.on('data', (message: ChatMessage) => {
      onMessage(message);
    });

    stream.on('error', (err) => {
      console.error('Stream error:', err);
    });

    stream.on('end', () => {
      console.log('Stream ended');
    });
  }

  // Note: Bidirectional streaming not supported in gRPC-Web
  // Use WebSocket or Server Streaming + Unary calls instead
}

// Usage
const client = new ChatClient('http://localhost:8080');

await client.sendMessage('Alice', 'Hello!');

client.streamMessages('general', (message) => {
  console.log(`${message.getUser()}: ${message.getText()}`);
});
```

---

### Socket.IO: Full-Featured Chat

#### JavaScript/TypeScript Client

```typescript
import { io, Socket } from 'socket.io-client';

class ChatClient {
  private socket: Socket;

  constructor(serverUrl: string) {
    this.socket = io(serverUrl, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: Infinity,
      timeout: 20000,
      autoConnect: true
    });

    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.socket.on('connect', () => {
      console.log('Connected:', this.socket.id);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected:', reason);
    });

    this.socket.on('reconnect_attempt', (attempt) => {
      console.log('Reconnecting, attempt:', attempt);
    });

    this.socket.on('error', (error) => {
      console.error('Socket error:', error);
    });
  }

  // Join room
  joinRoom(room: string, callback?: (response: any) => void) {
    this.socket.emit('join-room', { room }, callback);
  }

  // Send message with acknowledgment
  sendMessage(room: string, message: string) {
    this.socket.emit('message', { room, message }, (response) => {
      console.log('Message sent:', response);
    });
  }

  // Listen for messages
  onMessage(callback: (data: any) => void) {
    this.socket.on('message', callback);
  }

  // Typing indicator
  startTyping(room: string) {
    this.socket.emit('typing-start', { room });
  }

  stopTyping(room: string) {
    this.socket.emit('typing-stop', { room });
  }

  onTyping(callback: (data: any) => void) {
    this.socket.on('user-typing', callback);
  }

  // Broadcasting
  broadcast(event: string, data: any) {
    this.socket.emit('broadcast', { event, data });
  }

  // Disconnect
  disconnect() {
    this.socket.disconnect();
  }

  // Reconnect
  reconnect() {
    this.socket.connect();
  }
}

// Usage
const chat = new ChatClient('http://localhost:3000');

chat.joinRoom('general', (response) => {
  console.log('Joined room:', response);
});

chat.onMessage((data) => {
  console.log(`${data.user}: ${data.message}`);
});

chat.sendMessage('general', 'Hello everyone!');

chat.onTyping((data) => {
  console.log(`${data.user} is typing...`);
});
```

#### Kotlin/Android Socket.IO

```kotlin
import io.socket.client.IO
import io.socket.client.Socket
import io.socket.emitter.Emitter
import org.json.JSONObject

class ChatSocketClient(serverUrl: String) {
    private val socket: Socket

    init {
        val options = IO.Options().apply {
            transports = arrayOf("websocket", "polling")
            reconnection = true
            reconnectionDelay = 1000
            reconnectionDelayMax = 5000
            timeout = 20000
        }

        socket = IO.socket(serverUrl, options)
        setupEventListeners()
    }

    private fun setupEventListeners() {
        socket.on(Socket.EVENT_CONNECT) {
            println("Connected: ${socket.id()}")
        }

        socket.on(Socket.EVENT_DISCONNECT) { args ->
            println("Disconnected: ${args[0]}")
        }

        socket.on(Socket.EVENT_CONNECT_ERROR) { args ->
            println("Connection error: ${args[0]}")
        }

        socket.on(Socket.EVENT_RECONNECT_ATTEMPT) { args ->
            println("Reconnecting, attempt: ${args[0]}")
        }
    }

    fun connect() {
        socket.connect()
    }

    fun disconnect() {
        socket.disconnect()
    }

    // Join room
    fun joinRoom(room: String, callback: ((JSONObject) -> Unit)? = null) {
        val data = JSONObject().apply {
            put("room", room)
        }

        if (callback != null) {
            socket.emit("join-room", data) { args ->
                callback(args[0] as JSONObject)
            }
        } else {
            socket.emit("join-room", data)
        }
    }

    // Send message with acknowledgment
    fun sendMessage(room: String, message: String) {
        val data = JSONObject().apply {
            put("room", room)
            put("message", message)
        }

        socket.emit("message", data) { args ->
            println("Message sent: ${args[0]}")
        }
    }

    // Listen for messages
    fun onMessage(callback: (String, String, Long) -> Unit) {
        socket.on("message") { args ->
            val data = args[0] as JSONObject
            callback(
                data.getString("user"),
                data.getString("message"),
                data.getLong("timestamp")
            )
        }
    }

    // Typing indicator
    fun startTyping(room: String) {
        socket.emit("typing-start", JSONObject().apply {
            put("room", room)
        })
    }

    fun onTyping(callback: (String, String) -> Unit) {
        socket.on("user-typing") { args ->
            val data = args[0] as JSONObject
            callback(
                data.getString("user"),
                data.getString("room")
            )
        }
    }

    // Custom event listener
    fun on(event: String, callback: (JSONObject) -> Unit) {
        socket.on(event) { args ->
            callback(args[0] as JSONObject)
        }
    }

    // Custom event emitter
    fun emit(event: String, data: JSONObject) {
        socket.emit(event, data)
    }
}

// Usage in Activity/Fragment
class ChatActivity : AppCompatActivity() {
    private lateinit var chatClient: ChatSocketClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        chatClient = ChatSocketClient("http://10.0.2.2:3000")

        chatClient.onMessage { user, message, timestamp ->
            runOnUiThread {
                addMessageToUI(user, message, timestamp)
            }
        }

        chatClient.joinRoom("general") { response ->
            println("Joined: ${response.getString("message")}")
        }

        chatClient.connect()
    }

    private fun sendButtonClick() {
        val message = messageEditText.text.toString()
        chatClient.sendMessage("general", message)
    }

    override fun onDestroy() {
        super.onDestroy()
        chatClient.disconnect()
    }
}
```

---

## Decision Tree: Выбор протокола

```
┌─────────────────────────────────────────┐
│   Нужна ли P2P коммуникация?            │
│   (видео/аудио звонки)                  │
└───────────┬─────────────────────────────┘
            │
      ┌─────┴─────┐
      │    ДА     │
      └─────┬─────┘
            │
            ▼
    ┌──────────────┐
    │   WebRTC     │  ← Video/audio calls, P2P data
    └──────────────┘

      ┌─────┴─────┐
      │    НЕТ    │
      └─────┬─────┘
            │
            ▼
┌─────────────────────────────────────────┐
│   Нужна bidirectional коммуникация?     │
└───────────┬─────────────────────────────┘
            │
      ┌─────┴─────┐
      │    НЕТ    │  (только server → client)
      └─────┬─────┘
            │
            ▼
┌─────────────────────────────────────────┐
│   Нужны binary данные?                  │
└───────────┬─────────────────────────────┘
            │
      ┌─────┴─────┐
      │    НЕТ    │  (только text/JSON)
      └─────┬─────┘
            │
            ▼
    ┌──────────────┐
    │     SSE      │  ← Live updates, notifications
    └──────────────┘     Auto-reconnect, simple

      ┌─────┴─────┐
      │    ДА     │  (нужен binary)
      └─────┬─────┘
            │
            ▼
  ┌──────────────────┐
  │   WebSocket      │  ← Binary streaming server → client
  └──────────────────┘

      ┌─────┴─────┐
      │    ДА     │  (bidirectional нужен)
      └─────┬─────┘
            │
            ▼
┌─────────────────────────────────────────┐
│   Микросервисы communication?           │
└───────────┬─────────────────────────────┘
            │
      ┌─────┴─────┐
      │    ДА     │
      └─────┬─────┘
            │
            ▼
┌─────────────────────────────────────────┐
│   Нужна строгая типизация?              │
└───────────┬─────────────────────────────┘
            │
      ┌─────┴─────┐
      │    ДА     │
      └─────┬─────┘
            │
            ▼
    ┌──────────────┐
    │ gRPC Stream  │  ← Microservices, typed, binary
    └──────────────┘     Protocol Buffers

      ┌─────┴─────┐
      │    НЕТ    │
      └─────┬─────┘
            │
            ▼
┌─────────────────────────────────────────┐
│   Нужны rooms/namespaces/broadcast?     │
└───────────┬─────────────────────────────┘
            │
      ┌─────┴─────┐
      │    ДА     │
      └─────┬─────┘
            │
            ▼
    ┌──────────────┐
    │  Socket.IO   │  ← Chat, collaboration, gaming
    └──────────────┘     Auto-reconnect, rooms, fallback

      ┌─────┴─────┐
      │    НЕТ    │
      └─────┬─────┘
            │
            ▼
┌─────────────────────────────────────────┐
│   Критична максимальная производительность?  │
└───────────┬─────────────────────────────┘
            │
      ┌─────┴─────┐
      │    ДА     │
      └─────┬─────┘
            │
            ▼
  ┌──────────────────┐
  │  Native WebSocket│  ← Trading, gaming, high-frequency
  └──────────────────┘     Minimal overhead

      ┌─────┴─────┐
      │    НЕТ    │
      └─────┬─────┘
            │
            ▼
    ┌──────────────┐
    │  Socket.IO   │  ← General purpose, developer friendly
    └──────────────┘
```

### Сравнительная таблица

| Критерий | WebSocket | SSE | WebRTC | gRPC | Socket.IO |
|----------|-----------|-----|--------|------|-----------|
| **Направление** | Bidirectional | Server→Client | P2P Bidirectional | Bidirectional | Bidirectional |
| **Transport** | TCP | HTTP/HTTPS | UDP (SRTP) | TCP (HTTP/2) | TCP (WebSocket) |
| **Типы данных** | Text, Binary | Text only | Binary, Media | Binary (Protobuf) | Text, Binary |
| **Latency** | ~50ms | ~100ms | ~50ms (P2P) | ~30ms | ~60ms |
| **Reconnect** | Manual | Auto | Manual | Manual | Auto |
| **Complexity** | Medium | Low | High | Medium-High | Low |
| **Browser support** | Excellent | Excellent | Excellent | Limited (gRPC-Web) | Excellent |
| **Overhead** | Low | Medium | Low | Very Low | Medium |
| **Best for** | Chat, realtime | Live updates | Video/audio | Microservices | General realtime |
| **Scaling** | Medium | Easy | Hard (P2P) | Easy | Medium |
| **Backpressure** | WebSocketStream | No | No | Yes (HTTP/2) | No |

---

## Подводные камни

### WebSocket

**1. Reconnection Hell**
```javascript
// Проблема: бесконечные reconnect при ошибке авторизации
ws.onclose = () => {
  setTimeout(() => reconnect(), 1000); // Будет спамить сервер
};

// Решение: exponential backoff + max attempts
let attempts = 0;
const maxAttempts = 10;

function reconnect() {
  if (attempts >= maxAttempts) {
    console.error('Max reconnection attempts reached');
    return;
  }

  const delay = Math.min(1000 * Math.pow(2, attempts), 30000);
  setTimeout(() => {
    attempts++;
    connect();
  }, delay);
}
```

**2. Message Order**
```javascript
// Проблема: нет гарантии порядка при быстрой отправке
ws.send(message1);
ws.send(message2); // Может прийти раньше message1

// Решение: sequence numbers или acknowledgments
let messageSeq = 0;
function sendMessage(data) {
  ws.send(JSON.stringify({
    seq: messageSeq++,
    data: data
  }));
}
```

**3. Buffering при readyState !== OPEN**
```javascript
// Проблема: потеря сообщений при отключении
function send(data) {
  ws.send(data); // Ошибка если ws.readyState !== OPEN
}

// Решение: очередь сообщений
const messageQueue = [];

function send(data) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(data);
  } else {
    messageQueue.push(data);
  }
}

ws.onopen = () => {
  while (messageQueue.length > 0) {
    ws.send(messageQueue.shift());
  }
};
```

**4. Memory Leaks в SPA**
```javascript
// Проблема: не закрыли WebSocket при unmount
useEffect(() => {
  const ws = new WebSocket('wss://example.com');
  // ... setup
}, []); // Утечка памяти

// Решение: cleanup
useEffect(() => {
  const ws = new WebSocket('wss://example.com');

  return () => {
    ws.close();
  };
}, []);
```

**5. Ping/Pong для Keep-Alive**
```javascript
// Проблема: proxy/firewall закрывают idle соединения
// Решение: регулярный ping/pong
let pingInterval;

ws.onopen = () => {
  pingInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
    }
  }, 30000); // каждые 30 секунд
};

ws.onclose = () => {
  clearInterval(pingInterval);
};
```

### Server-Sent Events

**1. HTTP/1.1 Connection Limit**
```javascript
// Проблема: максимум 6 SSE соединений в HTTP/1.1
const sse1 = new EventSource('/stream1');
const sse2 = new EventSource('/stream2');
// ... 4 more ... 7-е соединение блокируется

// Решение 1: используйте HTTP/2
// Решение 2: multiplexing через один SSE stream
const sse = new EventSource('/multiplexed');
sse.addEventListener('stream1', handler1);
sse.addEventListener('stream2', handler2);
```

**2. Only Text Data**
```javascript
// Проблема: нет поддержки binary
// Обходной путь: Base64 encoding (увеличивает размер на ~33%)
// Server
res.write(`data: ${Buffer.from(binaryData).toString('base64')}\n\n`);

// Client
eventSource.onmessage = (event) => {
  const binaryData = Uint8Array.from(atob(event.data), c => c.charCodeAt(0));
};
```

**3. No Request Headers после подключения**
```javascript
// Проблема: нельзя отправить дополнительные данные после connect
// EventSource не поддерживает custom headers (кроме Last-Event-ID)

// Решение: используйте query params для авторизации
const token = getAuthToken();
const eventSource = new EventSource(`/updates?token=${token}`);

// Или WebSocket для bidirectional
```

**4. CORS Issues**
```javascript
// Проблема: CORS требует правильных заголовков
// Server должен отправлять:
res.setHeader('Access-Control-Allow-Origin', 'https://example.com');
res.setHeader('Access-Control-Allow-Credentials', 'true');

// Client
const eventSource = new EventSource('/updates', {
  withCredentials: true // для cookies
});
```

**5. Browser Caching**
```javascript
// Проблема: browser может кешировать SSE response
// Решение: правильные cache headers
res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
res.setHeader('X-Accel-Buffering', 'no'); // для nginx
```

### WebRTC

**1. Symmetric NAT Problems**
```javascript
// Проблема: ~10-20% соединений не могут установить P2P
// Решение: TURN server (но дорого в плане ресурсов)

const config = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    {
      urls: 'turn:turn.example.com:3478',
      username: 'user',
      credential: 'pass'
    }
  ],
  iceCandidatePoolSize: 10 // больше candidates
};
```

**2. Firewall Restrictions**
```javascript
// Проблема: корпоративные firewall блокируют UDP
// Решение: TURN over TCP/TLS
{
  urls: 'turn:turn.example.com:443?transport=tcp',
  username: 'user',
  credential: 'pass'
}
```

**3. ICE Trickle Optimization**
```javascript
// Проблема: ждать все ICE candidates долго
// Решение: trickle ICE (отправлять по мере получения)

pc.onicecandidate = (event) => {
  if (event.candidate) {
    // Отправляем сразу
    signalingChannel.send({
      type: 'ice-candidate',
      candidate: event.candidate
    });
  }
};

// Без trickle (медленнее):
pc.onicecandidate = (event) => {
  if (event.candidate === null) {
    // Все candidates собраны
    signalingChannel.send({
      type: 'offer',
      sdp: pc.localDescription
    });
  }
};
```

**4. Mobile Battery Drain**
```javascript
// Проблема: постоянная WebRTC передача жрет батарею
// Решение: адаптивный bitrate и разрешение

const sender = pc.getSenders().find(s => s.track?.kind === 'video');
const parameters = sender.getParameters();

if (batteryLevel < 20) {
  parameters.encodings[0].maxBitrate = 500000; // 500 kbps
  parameters.encodings[0].scaleResolutionDownBy = 2; // половина разрешения
  await sender.setParameters(parameters);
}
```

**5. Memory Leaks с MediaStream**
```javascript
// Проблема: не останавливаем tracks при unmount
useEffect(() => {
  let localStream;

  async function setup() {
    localStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });
    // ... use stream
  }

  setup();

  return () => {
    // ОБЯЗАТЕЛЬНО останавливаем tracks
    localStream?.getTracks().forEach(track => track.stop());
  };
}, []);
```

### gRPC

**1. Browser Limitations**
```javascript
// Проблема: нет нативной поддержки в браузерах
// Решение: gRPC-Web (но ограничения)

// gRPC-Web НЕ поддерживает:
// - Client streaming
// - Bidirectional streaming

// Используйте WebSocket для browser real-time
```

**2. Binary Debugging**
```bash
# Проблема: сложно отлаживать binary протокол
# Решение: используйте grpcurl

# Unary call
grpcurl -plaintext -d '{"user":"Alice"}' \
  localhost:50051 chat.ChatService/SendMessage

# Server streaming
grpcurl -plaintext -d '{"room":"general"}' \
  localhost:50051 chat.ChatService/StreamMessages
```

**3. Load Balancing Issues**
```yaml
# Проблема: HTTP/2 держит одно TCP соединение
# L4 балансировка не работает эффективно

# Решение: используйте client-side LB или proxy
apiVersion: v1
kind: Service
metadata:
  name: grpc-service
spec:
  type: ClusterIP
  sessionAffinity: None # НЕ используйте ClientIP
```

**4. Deadline Propagation**
```kotlin
// Проблема: timeout не передается между сервисами
// Решение: устанавливайте deadline явно

val channel = ManagedChannelBuilder
    .forTarget("service:50051")
    .build()

val stub = ServiceGrpc.newBlockingStub(channel)
    .withDeadlineAfter(5, TimeUnit.SECONDS) // Важно!

try {
    val response = stub.method(request)
} catch (e: StatusRuntimeException) {
    if (e.status.code == Status.Code.DEADLINE_EXCEEDED) {
        // Handle timeout
    }
}
```

**5. Protocol Buffers Versioning**
```protobuf
// Проблема: breaking changes ломают клиентов
// Решение: следуйте правилам обратной совместимости

// ✅ МОЖНО:
message User {
  string name = 1;
  int32 age = 2;
  string email = 3;  // Добавление нового поля
}

// ❌ НЕЛЬЗЯ:
message User {
  string name = 1;
  string age = 2;  // Изменение типа поля - BREAKING!
}

// Используйте новые номера полей вместо изменения старых
```

### Socket.IO

**1. Version Incompatibility**
```javascript
// Проблема: Socket.IO client и server версии должны совпадать
// Socket.IO v2 несовместим с v3/v4

// Решение: проверяйте версии
// package.json
{
  "socket.io": "^4.7.0",  // Server
  "socket.io-client": "^4.7.0"  // Client - та же мажорная версия
}
```

**2. Room Scaling Issues**
```javascript
// Проблема: rooms не синхронизируются между серверами
// Решение: используйте Redis adapter

// Server
const io = require('socket.io')(server);
const { createAdapter } = require('@socket.io/redis-adapter');
const { createClient } = require('redis');

const pubClient = createClient({ url: 'redis://localhost:6379' });
const subClient = pubClient.duplicate();

io.adapter(createAdapter(pubClient, subClient));

// Теперь io.to('room').emit() работает через все сервера
```

**3. Event Name Collisions**
```javascript
// Проблема: reserved event names
const reservedEvents = [
  'connect', 'connect_error', 'disconnect',
  'disconnecting', 'newListener', 'removeListener'
];

// ❌ НЕ используйте
socket.on('disconnect', () => {}); // Конфликт с системным

// ✅ Используйте custom prefixes
socket.on('app:disconnect', () => {});
```

**4. Acknowledgment Timeout**
```javascript
// Проблема: acknowledgment callbacks не имеют timeout
socket.emit('request', data, (response) => {
  // Может никогда не вызваться
});

// Решение: добавьте timeout вручную
function emitWithTimeout(event, data, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('Acknowledgment timeout'));
    }, timeout);

    socket.emit(event, data, (response) => {
      clearTimeout(timer);
      resolve(response);
    });
  });
}

// Usage
try {
  const response = await emitWithTimeout('request', data);
} catch (err) {
  console.error('Timeout:', err);
}
```

**5. Memory Leaks с Listeners**
```javascript
// Проблема: забыли удалить listeners
function setupChat() {
  socket.on('message', handleMessage); // Добавляется каждый раз
}

setupChat(); // listener 1
setupChat(); // listener 2 (утечка!)

// Решение: удаляйте или используйте once
function setupChat() {
  socket.off('message', handleMessage); // Удаляем старый
  socket.on('message', handleMessage);
}

// Или используйте once для одноразовых
socket.once('welcome', (data) => {
  console.log('Welcome message:', data);
});
```

---

## Best Practices

### WebSocket

1. **Всегда используйте WSS (TLS)** в продакшене
2. **Реализуйте exponential backoff** для reconnection
3. **Добавьте ping/pong** для keep-alive (каждые 30-60 сек)
4. **Валидируйте сообщения** на сервере и клиенте
5. **Используйте message queue** для buffering при reconnect
6. **Мониторьте connection lifetime** и rate limits

### SSE

1. **Используйте HTTP/2** для устранения connection limit
2. **Добавляйте ID к сообщениям** для resume после reconnect
3. **Устанавливайте retry** разумно (5-10 секунд)
4. **Правильные cache headers** (no-cache)
5. **Compression** для больших JSON payload
6. **Heartbeat messages** каждые 15-30 секунд

### WebRTC

1. **Всегда предоставляйте TURN server** для fallback
2. **Используйте trickle ICE** для быстрого соединения
3. **Адаптивный bitrate** для плохих сетей
4. **Мониторьте connection quality** (RTCStatsReport)
5. **Graceful degradation** (отключайте видео при плохой сети)
6. **Останавливайте media tracks** при завершении

### gRPC

1. **Используйте deadline** для всех вызовов
2. **Retry policy** с exponential backoff
3. **Client-side load balancing** для множества серверов
4. **Protocol Buffers versioning** для обратной совместимости
5. **Мониторинг latency** и error rates
6. **Компрессия** для больших payload (gzip)

### Socket.IO

1. **Синхронизируйте версии** client/server
2. **Используйте Redis adapter** для multi-server
3. **Namespace** для логического разделения
4. **Rate limiting** для предотвращения спама
5. **Валидация** всех incoming events
6. **Cleanup listeners** при unmount

---

## Источники

### Теоретические основы
- [RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455) (2011). *The WebSocket Protocol*. — Fette & Melnikov, IETF
- [RFC 8831](https://datatracker.ietf.org/doc/html/rfc8831) (2021). *WebRTC Data Channels*. — Формальная модель P2P data transfer
- Rescorla E. (2018). *WebRTC: APIs and SRTP Architecture*. — Медиа-стек WebRTC

### Практические руководства (проверено 2025-12-18)

**WebSocket:**
- [WebSockets Standard - WHATWG Living Standard](https://websockets.spec.whatwg.org/)
- [WebSocket API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Future of WebSockets: HTTP/3 and WebTransport](https://websocket.org/guides/future-of-websockets/)

**Server-Sent Events:**
- [WebSockets vs Server-Sent Events - Ably](https://ably.com/blog/websockets-vs-sse)
- [SSE vs WebSockets - RxDB](https://rxdb.info/articles/websockets-sse-polling-webrtc-webtransport.html)
- [Server-Sent Events vs WebSockets - freeCodeCamp](https://www.freecodecamp.org/news/server-sent-events-vs-websockets/)
- [SSE vs WebSockets Comparison - WebSocket.org](https://websocket.org/comparisons/sse/)

**WebRTC:**
- [Introduction to WebRTC protocols - MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Protocols)
- [WebRTC Protocol in 2025 - VideoSDK](https://www.videosdk.live/developer-hub/webrtc/webrtc-protocol)
- [WebRTC W3C Specification](https://www.w3.org/TR/webrtc/)
- [Getting started with peer connections - WebRTC.org](https://webrtc.org/getting-started/peer-connections)

**gRPC:**
- [gRPC with Bidirectional Streaming - Medium](https://medium.com/@rahul.jindal57/grpc-with-bidirectional-streaming-for-real-time-updates-df07e44e209c)
- [gRPC with TypeScript in 2025](https://caisy.io/blog/grpc-typescript)
- [gRPC Streaming - Apidog](https://apidog.com/blog/grpc-streaming/)
- [gRPC in 2025: Why Companies Switch from REST - Medium](https://medium.com/@miantalha.t08/grpc-in-2025-why-top-companies-are-switching-from-rest-36e3c6e2ec4c)

**Socket.IO:**
- [WebSocket vs Socket.IO - Ably](https://ably.com/topic/socketio-vs-websocket)
- [Socket.IO vs WebSocket Guide - Velt](https://velt.dev/blog/socketio-vs-websocket-guide-developers)
- [Socket.IO vs WebSocket - VideoSDK](https://www.videosdk.live/developer-hub/websocket/socketio-vs-websocket)
- [Socket.io vs WebSockets - CometChat](https://www.cometchat.com/blog/socket-io-vs-websockets)

---

## Связь с другими темами

[[network-http-evolution]] — WebSocket начинается как HTTP Upgrade, SSE работает через стандартный HTTP, а gRPC построен на HTTP/2. Понимание эволюции HTTP объясняет, почему WebSocket потребовал отдельный протокол (HTTP/1.1 не поддерживал серверный push), почему gRPC выбрал HTTP/2 (multiplexing и streaming), и как WebTransport в HTTP/3 может заменить WebSocket в будущем. Рекомендуется изучить HTTP-эволюцию перед real-time протоколами.

[[network-transport-layer]] — выбор между TCP и UDP лежит в основе архитектуры real-time протоколов. WebSocket использует TCP (гарантия доставки, но HOL blocking), WebRTC использует UDP через DTLS/SRTP (минимальная latency для аудио/видео), а gRPC работает поверх HTTP/2 (TCP). Понимание компромисса reliability vs latency на транспортном уровне критически важно для выбора протокола.

[[android-networking]] — Android-приложения активно используют real-time протоколы: WebSocket для чатов и push-уведомлений, gRPC для эффективного взаимодействия с backend, SSE для ленты обновлений. Особенности Android (Doze mode, background restrictions, lifecycle) влияют на поддержание long-lived соединений и требуют специфических паттернов reconnect и heartbeat.

---

## Источники и дальнейшее чтение

- **Grigorik I. (2013). High Performance Browser Networking.** — Детальный разбор WebSocket, SSE и оптимизации real-time коммуникации в браузерах. Объясняет WebSocket handshake, frame format и performance considerations. Бесплатно доступна онлайн.

- **Kurose J., Ross K. (2021). Computer Networking: A Top-Down Approach, 8th Edition.** — Академический фундамент для понимания socket programming, мультимедийных сетевых приложений и протоколов реального времени (RTP/RTCP). Даёт теоретическую базу, на которой построены все real-time протоколы.

- **Stevens W.R. (1994). TCP/IP Illustrated, Volume 1: The Protocols.** — Классический разбор TCP и UDP, который объясняет, почему real-time приложения выбирают UDP (WebRTC) или TCP с оптимизациями (WebSocket с TCP_NODELAY). Незаменим для понимания сетевого поведения real-time систем.

---

---

## Проверь себя

> [!question]- Почему SSE может быть лучшим выбором, чем WebSocket, для ленты уведомлений?
> SSE проще: работает через обычный HTTP (проходит прокси), автоматический reconnect встроен в браузер (EventSource API), не требует upgrade. Для уведомлений достаточно однонаправленного потока сервер->клиент. WebSocket избыточен, если клиент не отправляет данные обратно.

> [!question]- WebRTC-звонок не устанавливается у 30% пользователей. Какова наиболее вероятная причина и решение?
> Симметричный NAT или корпоративный firewall блокирует P2P-соединение. STUN помогает обойти обычный NAT, но не симметричный. Решение --- TURN-сервер как relay: трафик идёт через сервер, обходя NAT. Около 30% звонков требуют TURN. Нужен ICE с fallback на TURN.

> [!question]- В каких случаях gRPC предпочтительнее REST API?
> gRPC лучше для: микросервисной коммуникации (бинарный Protobuf в 3-10 раз компактнее JSON), streaming (4 типа: unary, server, client, bidirectional), строгая типизация контрактов (.proto файлы), автогенерация клиентов. Хуже для: браузеров (нужен gRPC-Web), публичных API (JSON привычнее), отладки (бинарный формат).

---

## Ключевые карточки

Чем WebSocket отличается от HTTP?
?
WebSocket --- постоянное полнодуплексное соединение поверх TCP. Начинается как HTTP Upgrade, затем переключается на бинарный фрейминг. Оба направления одновременно, минимальный overhead (2 байта). HTTP --- request-response, каждый запрос с полными заголовками.

Когда использовать SSE вместо WebSocket?
?
SSE --- когда нужен только поток от сервера к клиенту: уведомления, ленты, прогресс. Преимущества: обычный HTTP, автоматический reconnect, проходит через прокси, Event ID для восстановления. WebSocket --- когда нужна двунаправленная связь: чаты, игры, совместное редактирование.

Что такое ICE, STUN и TURN в WebRTC?
?
ICE --- протокол поиска оптимального пути соединения. STUN --- сервер, показывающий клиенту его публичный IP (обход NAT). TURN --- relay-сервер, пересылающий трафик, когда P2P невозможен (симметричный NAT). ICE пробует host -> STUN -> TURN по порядку.

Какие 4 типа streaming поддерживает gRPC?
?
Unary (один запрос, один ответ), Server streaming (один запрос, поток ответов), Client streaming (поток запросов, один ответ), Bidirectional streaming (потоки в обе стороны). Все работают поверх HTTP/2 multiplexing с Protocol Buffers.

Что такое heartbeat и зачем он нужен в WebSocket?
?
Heartbeat --- периодические ping/pong сообщения для проверки, что соединение живо. Без heartbeat мёртвое соединение (например, после потери сети) не будет обнаружено, пока не придут данные. Типичный интервал: 30-60 секунд.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[network-latency-optimization]] | Оптимизация задержек для real-time приложений |
| Углубиться | [[network-transport-layer]] | Понять TCP и UDP, на которых работают протоколы |
| Смежная тема | [[android-networking]] | Реализация WebSocket и gRPC в Android |
| Обзор | [[networking-overview]] | Вернуться к карте раздела |

---

*Последнее обновление: 2026-01-09 --- Добавлены педагогические секции: 5 аналогий (WebSocket-телефонный звонок, SSE-радиоприёмник, WebRTC-прямой P2P звонок, gRPC-экспресс-почта, NAT Traversal-поиск за забором), 6 типичных ошибок real-time протоколов с диагностикой (выбор WS вместо SSE, reconnect, heartbeat, TURN fallback, gRPC streaming, backpressure), 5 ментальных моделей (спектр latency, направление потока, топология соединений, NAT traversal, выбор протокола)*

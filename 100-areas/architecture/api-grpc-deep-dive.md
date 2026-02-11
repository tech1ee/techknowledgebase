---
title: "gRPC: high-performance RPC framework"
created: 2026-02-10
modified: 2026-02-10
type: deep-dive
status: published
confidence: high
sources_verified: true
tags:
  - topic/architecture
  - topic/networking
  - architecture/api
  - architecture/grpc
  - backend/grpc
  - type/deep-dive
  - level/intermediate
related:
  - "[[api-design]]"
  - "[[api-rest-deep-dive]]"
  - "[[api-graphql-deep-dive]]"
  - "[[api-modern-patterns]]"
  - "[[network-http-evolution]]"
  - "[[network-realtime-protocols]]"
  - "[[architecture-distributed-systems]]"
cs-foundations:
  - serialization
  - binary-protocols
  - streaming
  - service-discovery
  - load-balancing
  - code-generation
---

# gRPC: high-performance RPC framework

Google отправляет 10 миллиардов внутренних RPC-вызовов в секунду. Не в день — в секунду. С 2001 года эту нагрузку обслуживала внутренняя система Stubby. В 2015 Google открыл её переработанную версию миру под названием gRPC. Буква «g» — не «Google»: она меняется с каждым релизом (good, green, groovy...). Сейчас gRPC — стандарт de facto для межсервисной коммуникации в Cloud Native.

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **HTTP/2** | gRPC работает поверх HTTP/2 (multiplexing, binary framing) | [[network-http-evolution]] |
| **REST API** | Понимание request/response, чтобы сравнивать с RPC | [[api-rest-deep-dive]] |
| **Сериализация** | Protocol Buffers — бинарный формат | Базовые знания JSON, XML |
| **TCP** | gRPC использует TCP (через HTTP/2) | [[network-transport-layer]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **gRPC** | Google Remote Procedure Call — фреймворк для вызова функций на удалённом сервере | Телефонный звонок: вызываешь функцию «на другом конце провода» |
| **Protocol Buffers (Protobuf)** | Бинарный формат сериализации от Google | Zip-архив для данных: компактно, быстро, но нечитаемо глазами |
| **`.proto` file** | Описание сервиса и сообщений | Контракт/договор между клиентом и сервером |
| **Stub** | Сгенерированный клиентский код | Пульт ДУ: нажимаешь кнопку — команда уходит на сервер |
| **Channel** | Соединение с gRPC-сервером | Телефонная линия: один раз установил, используешь много раз |
| **Unary RPC** | Один запрос → один ответ | Обычный телефонный звонок |
| **Streaming** | Потоковая передача сообщений | Конференц-звонок: несколько сообщений в обе стороны |
| **Metadata** | Заголовки (как HTTP headers) | Конверт письма: адрес, марка, пометки |
| **Deadline** | Максимальное время ожидания ответа | «Если через 5 секунд не ответишь — вешаю трубку» |
| **Interceptor** | Middleware для перехвата вызовов | Секретарь: фильтрует звонки, записывает, авторизует |
| **Status Code** | Код результата операции (16 кодов) | Код ответа оператора: «выполнено», «не найдено», «занято» |

---

## Зачем gRPC существует: от Stubby до CNCF

### Google Stubby (2001): внутренняя система

В начале 2000-х Google столкнулся с проблемой: тысячи микросервисов должны общаться друг с другом. REST ещё не стал стандартом (Филдинг только защитил диссертацию). SOAP — слишком тяжёлый. Google построил Stubby — внутреннюю RPC-систему с бинарной сериализацией и кодогенерацией.

Stubby обслуживал всё: Search, Gmail, YouTube, Maps. Но он был привязан к внутренней инфраструктуре Google и не мог быть открыт миру.

### gRPC (2015): open-source переосмысление

В 2015 Google выпустил gRPC — новую версию, построенную на открытых стандартах:
- **HTTP/2** вместо проприетарного транспорта
- **Protocol Buffers 3** вместо внутреннего формата
- **Открытая спецификация** вместо closed-source

| Год | Событие |
|-----|---------|
| **2001** | Google создаёт Stubby |
| **2008** | Protocol Buffers открыты (proto2) |
| **2015** | gRPC выпущен как open source |
| **2016** | gRPC 1.0 stable |
| **2017** | gRPC принят в CNCF (Cloud Native Computing Foundation) |
| **2019** | gRPC-Web стабилен (поддержка браузеров через прокси) |
| **2023** | gRPC — стандарт в Kubernetes, Envoy, Istio |
| **2025** | 10+ языков, используется Netflix, Uber, Dropbox, Square |

### REST vs gRPC: не конкуренция, а разные ниши

```
┌──────────────────────────────────────────────────────────────┐
│                    REST vs gRPC                               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  REST                              gRPC                       │
│  ────                              ────                       │
│  Текстовый (JSON)                  Бинарный (Protobuf)        │
│  HTTP/1.1 или HTTP/2               HTTP/2 обязателен          │
│  Человекочитаемый                  Машиночитаемый             │
│  Браузер-friendly                  Нужен прокси для браузера  │
│  curl для дебага                   grpcurl для дебага         │
│  Кэширование из коробки            Кэширование руками         │
│  Стандартов документации (OpenAPI)  .proto файл = документация │
│  Любой язык, любой клиент          Кодогенерация обязательна  │
│                                                               │
│  КОГДА REST:                       КОГДА gRPC:                │
│  • Public API                      • Микросервисы             │
│  • Браузерные клиенты              • Межсервисная связь       │
│  • Простой CRUD                    • Low-latency системы      │
│  • Кэширование критично            • Streaming                │
│  • Третьи разработчики             • Мобильные (low bandwidth)│
│                                                               │
│  БЕНЧМАРКИ:                                                   │
│  Latency:  REST ~250ms  vs  gRPC ~25ms  (10x разница)        │
│  Payload:  JSON 100%    vs  Protobuf 10-30%                   │
│  CPU:      Baseline     vs  -40%                              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Protocol Buffers: бинарная сериализация

### Что такое Protobuf

Protocol Buffers — формат сериализации от Google. Данные описываются в `.proto` файле и компилируются в код на любом языке. Protobuf — не часть gRPC: его можно использовать отдельно для хранения, передачи, конфигурации.

### .proto файл: язык определения

```protobuf
// Файл: user_service.proto

syntax = "proto3";           // Версия протокола (proto3 — текущая)

package userservice;         // Пространство имён

// Описание сервиса (какие RPC-методы доступны)
service UserService {
  // Unary: один запрос → один ответ
  rpc GetUser(GetUserRequest) returns (User);

  // Server streaming: один запрос → поток ответов
  rpc ListUsers(ListUsersRequest) returns (stream User);

  // Client streaming: поток запросов → один ответ
  rpc UploadAvatar(stream AvatarChunk) returns (UploadResult);

  // Bidirectional streaming: поток ↔ поток
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

// Описание сообщений (структура данных)
message User {
  int64 id = 1;              // Поле 1 (номер, не значение!)
  string name = 2;           // Поле 2
  string email = 3;          // Поле 3
  Role role = 4;             // Enum
  repeated string tags = 5;  // Массив строк
  Address address = 6;       // Вложенное сообщение
  optional string bio = 7;   // Опциональное поле (proto3)
}

enum Role {
  ROLE_UNSPECIFIED = 0;      // Обязательный 0 для default value
  ADMIN = 1;
  EDITOR = 2;
  VIEWER = 3;
}

message Address {
  string city = 1;
  string street = 2;
  int32 zip = 3;
}

message GetUserRequest {
  int64 id = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}
```

### Как Protobuf кодирует данные

```
JSON (текстовый):
{"id": 123, "name": "Иван", "email": "ivan@mail.com"}
→ 52 байта (UTF-8 текст)

Protobuf (бинарный):
08 7b 12 08 d0 98 d0 b2 d0 b0 d0 bd 1a 0d 69 76...
→ 30 байт (бинарные данные)

Экономия: ~42% для маленьких сообщений, до 90% для больших.

КАК ЭТО РАБОТАЕТ:
─────────────────

Каждое поле кодируется как: [tag] [value]

Tag = (field_number << 3) | wire_type

Wire types:
┌──────────┬────────────────┬───────────────────────────┐
│ Wire Type│ Значение       │ Используется для          │
├──────────┼────────────────┼───────────────────────────┤
│    0     │ Varint         │ int32, int64, bool, enum  │
│    1     │ 64-bit         │ fixed64, double           │
│    2     │ Length-delimited│ string, bytes, message    │
│    5     │ 32-bit         │ fixed32, float            │
└──────────┴────────────────┴───────────────────────────┘

ПРИМЕР: Кодирование id = 123

Поле id: field_number = 1, тип int64 → wire_type = 0
Tag = (1 << 3) | 0 = 0x08

Значение 123 → varint = 0x7b (один байт, т.к. < 128)

Результат: 08 7b (2 байта вместо "id": 123 = 8 байт)
```

### Varint: переменная длина

```
Varint = Variable-length Integer
Алгоритм LEB128: маленькие числа = меньше байт

Число 1:     0x01           (1 байт)
Число 127:   0x7f           (1 байт)
Число 128:   0x80 0x01      (2 байта)
Число 300:   0xac 0x02      (2 байта)
Число 100000: 0xa0 0x8d 0x06 (3 байта)

MSB (старший бит) каждого байта:
  1 = есть ещё байты
  0 = последний байт

Пример: 300 (0x012c)
  Байт 1: 10101100 → MSB=1 (продолжение), payload = 0101100
  Байт 2: 00000010 → MSB=0 (конец),        payload = 0000010

  Результат: 0000010 ++ 0101100 = 100101100 = 300

КОГДА VARINT НЕВЫГОДЕН:
─────────────────────
Отрицательные числа int32/int64 → 10 байт (two's complement)!
Решение: sint32/sint64 → ZigZag encoding:
  0 → 0, -1 → 1, 1 → 2, -2 → 3, 2 → 4...
  Маленькие отрицательные = маленькие varints.
```

### Обратная совместимость: золотые правила

Protobuf спроектирован для эволюции — старые клиенты читают новые сообщения (и наоборот). Но для этого нужно следовать правилам:

```
✅ МОЖНО (обратно совместимо):
─────────────────────────────
1. Добавить новое поле (старые клиенты игнорируют неизвестные поля)
2. Удалить поле (но ЗАРЕЗЕРВИРОВАТЬ номер!)
3. Переименовать поле (важен номер, не имя)
4. Изменить singular → repeated (для compatible типов)

❌ НЕЛЬЗЯ (ломает совместимость):
──────────────────────────────
1. Изменить номер поля (это ключ в бинарном формате!)
2. Изменить тип поля на несовместимый (int32 → string)
3. Переиспользовать номер удалённого поля

РЕЗЕРВИРОВАНИЕ (защита от переиспользования):
─────────────────────────────────────────────
message User {
  reserved 2, 15, 9 to 11;     // Эти номера больше нельзя использовать
  reserved "old_field", "temp"; // Эти имена тоже

  int64 id = 1;    // Поле 1
  // Поле 2 удалено, номер зарезервирован
  string name = 3;  // Поле 3
}
```

---

## Четыре паттерна коммуникации

gRPC поддерживает четыре типа вызовов. Это одно из главных преимуществ перед REST (который ограничен request-response).

```
┌──────────────────────────────────────────────────────────────┐
│               4 ПАТТЕРНА gRPC                                 │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. UNARY (как REST)                                          │
│  ────────────────────                                         │
│  Client ──[request]──→ Server                                 │
│  Client ←──[response]── Server                                │
│                                                               │
│  2. SERVER STREAMING                                          │
│  ────────────────────                                         │
│  Client ──[request]──→ Server                                 │
│  Client ←──[response 1]── Server                              │
│  Client ←──[response 2]── Server                              │
│  Client ←──[response N]── Server                              │
│  Client ←──[done]────── Server                                │
│                                                               │
│  3. CLIENT STREAMING                                          │
│  ────────────────────                                         │
│  Client ──[message 1]──→ Server                               │
│  Client ──[message 2]──→ Server                               │
│  Client ──[message N]──→ Server                               │
│  Client ──[done]───────→ Server                               │
│  Client ←──[response]─── Server                               │
│                                                               │
│  4. BIDIRECTIONAL STREAMING                                   │
│  ────────────────────────                                     │
│  Client ──[message]──→ Server                                 │
│  Client ←──[message]── Server                                 │
│  Client ──[message]──→ Server                                 │
│  Client ←──[message]── Server                                 │
│  (независимо друг от друга)                                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### 1. Unary RPC

Классический request-response. Как REST, но бинарный и быстрее.

```python
# Python: Unary RPC (gRPC)

# server.py
class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        user = db.get_user(request.id)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User {request.id} not found")
            return user_pb2.User()

        return user_pb2.User(
            id=user.id,
            name=user.name,
            email=user.email
        )

# client.py
channel = grpc.insecure_channel('localhost:50051')
stub = user_pb2_grpc.UserServiceStub(channel)

try:
    user = stub.GetUser(user_pb2.GetUserRequest(id=123))
    print(f"User: {user.name}")
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        print("Пользователь не найден")
```

### 2. Server Streaming

Сервер отправляет поток сообщений. Использование: real-time данные, большие выборки, прогресс загрузки.

```python
# Пример: стриминг биржевых котировок

# .proto
# rpc StreamPrices(PriceRequest) returns (stream PriceUpdate);

# server.py
class MarketServiceServicer(market_pb2_grpc.MarketServiceServicer):
    def StreamPrices(self, request, context):
        while context.is_active():  # Пока клиент подключён
            price = get_current_price(request.symbol)
            yield market_pb2.PriceUpdate(
                symbol=request.symbol,
                price=price,
                timestamp=int(time.time())
            )
            time.sleep(0.1)  # 10 обновлений в секунду

# client.py
for update in stub.StreamPrices(market_pb2.PriceRequest(symbol="AAPL")):
    print(f"{update.symbol}: ${update.price}")
    # Получаем обновления пока соединение активно
```

### 3. Client Streaming

Клиент отправляет поток сообщений, сервер отвечает один раз. Использование: upload файлов, batch-вставка, агрегация данных.

```python
# Пример: загрузка файла чанками

# .proto
# rpc UploadFile(stream FileChunk) returns (UploadResult);

# client.py
def upload_chunks(filepath):
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(64 * 1024)  # 64KB чанки
            if not chunk:
                break
            yield file_pb2.FileChunk(
                data=chunk,
                filename="report.pdf"
            )

result = stub.UploadFile(upload_chunks("report.pdf"))
print(f"Uploaded: {result.bytes_received} bytes")
```

### 4. Bidirectional Streaming

Оба отправляют сообщения независимо. Потоки не синхронизированы — клиент может отправить 3 сообщения, получить 1, отправить ещё 2. Использование: чат, интерактивные игры, collaborative editing.

```python
# Пример: чат

# .proto
# rpc Chat(stream ChatMessage) returns (stream ChatMessage);

# client.py
def send_messages():
    while True:
        text = input("> ")
        yield chat_pb2.ChatMessage(
            user="Alice",
            text=text
        )

# Отправка и получение — в параллельных потоках
responses = stub.Chat(send_messages())
for response in responses:
    print(f"{response.user}: {response.text}")
```

---

## gRPC поверх HTTP/2

gRPC не изобретает свой транспорт — он использует HTTP/2 (подробнее: [[network-http-evolution]]). Это ключевое решение: HTTP/2 уже поддерживается прокси, load balancers, CDN.

```
КАК gRPC МАПИТСЯ НА HTTP/2:
────────────────────────────

gRPC Call = HTTP/2 request/response

┌──────────────┬──────────────────────────────────────────┐
│ gRPC         │ HTTP/2                                    │
├──────────────┼──────────────────────────────────────────┤
│ Сервис       │ :path = /package.Service/Method           │
│ Метод        │ :method = POST                            │
│ Metadata     │ HTTP/2 headers (custom headers с grpc-)   │
│ Сообщение    │ HTTP/2 data frame (length-prefixed)       │
│ Status       │ Trailers: grpc-status, grpc-message       │
│ Deadline     │ Header: grpc-timeout                      │
└──────────────┴──────────────────────────────────────────┘

HTTP/2 фреймы для gRPC Unary Call:
───────────────────────────────────

Client → Server:
  HEADERS frame:
    :method = POST
    :path = /userservice.UserService/GetUser
    :scheme = https
    content-type = application/grpc
    grpc-timeout = 5S

  DATA frame:
    [5 bytes header: compressed? + length]
    [Protobuf-encoded GetUserRequest]

Server → Client:
  HEADERS frame:
    :status = 200
    content-type = application/grpc

  DATA frame:
    [5 bytes header + Protobuf-encoded User]

  TRAILERS frame:
    grpc-status = 0          ← OK
    grpc-message = ""
```

**Почему HTTP/2 идеален для gRPC:**
- **Multiplexing:** множество RPC-вызовов через одно TCP-соединение
- **Binary framing:** данные уже бинарные, как и Protobuf
- **Header compression (HPACK):** повторяющиеся заголовки сжимаются
- **Server push:** (не используется в gRPC, но доступен)
- **Flow control:** встроенное управление потоком

---

## Error Handling: gRPC Status Codes

gRPC имеет свою систему status codes — 16 кодов, каждый с чётким значением. Не путать с HTTP status codes — gRPC-статус передаётся в trailers.

```
┌──────────────────────────────────────────────────────────────┐
│                  gRPC STATUS CODES                            │
├──────┬───────────────────┬───────────────────────────────────┤
│ Code │ Название          │ Когда использовать                │
├──────┼───────────────────┼───────────────────────────────────┤
│  0   │ OK                │ Успех                             │
│  1   │ CANCELLED         │ Клиент отменил запрос             │
│  2   │ UNKNOWN           │ Неизвестная ошибка                │
│  3   │ INVALID_ARGUMENT  │ Невалидные параметры (400 в REST) │
│  4   │ DEADLINE_EXCEEDED │ Таймаут (504 в REST)              │
│  5   │ NOT_FOUND         │ Ресурс не найден (404 в REST)     │
│  6   │ ALREADY_EXISTS    │ Ресурс уже существует (409)       │
│  7   │ PERMISSION_DENIED │ Нет прав (403 в REST)             │
│  8   │ RESOURCE_EXHAUSTED│ Rate limit (429 в REST)           │
│  9   │ FAILED_PRECONDIT. │ Предусловие не выполнено (412)    │
│ 10   │ ABORTED           │ Операция прервана (конфликт)      │
│ 11   │ OUT_OF_RANGE      │ Значение за пределами диапазона   │
│ 12   │ UNIMPLEMENTED     │ Метод не реализован (501)         │
│ 13   │ INTERNAL          │ Внутренняя ошибка (500)           │
│ 14   │ UNAVAILABLE       │ Сервис недоступен (503). Retry!   │
│ 15   │ DATA_LOSS         │ Потеря данных (неисправимая)      │
│ 16   │ UNAUTHENTICATED   │ Не аутентифицирован (401)         │
└──────┴───────────────────┴───────────────────────────────────┘
```

### Rich Error Model

Базовый Status (code + message) часто недостаточен. Google предлагает Rich Error Model — дополнительные детали через `google.rpc.Status`:

```protobuf
// google/rpc/status.proto
message Status {
  int32 code = 1;
  string message = 2;
  repeated google.protobuf.Any details = 3;  // Произвольные детали
}

// Типы деталей (google/rpc/error_details.proto):
// RetryInfo     → через сколько повторить
// DebugInfo     → stack trace (только dev)
// BadRequest    → какие поля невалидны
// ResourceInfo  → какой ресурс не найден
// QuotaFailure  → какая квота превышена
```

```python
# Пример: Rich Error с деталями

from grpc_status import rpc_status
from google.protobuf import any_pb2
from google.rpc import error_details_pb2, status_pb2

def GetUser(self, request, context):
    if not request.id:
        # Создаём детальную ошибку
        detail = error_details_pb2.BadRequest()
        violation = detail.field_violations.add()
        violation.field = "id"
        violation.description = "ID is required and must be positive"

        rich_status = status_pb2.Status(
            code=grpc.StatusCode.INVALID_ARGUMENT.value[0],
            message="Invalid request parameters"
        )
        detail_any = any_pb2.Any()
        detail_any.Pack(detail)
        rich_status.details.append(detail_any)

        context.abort_with_status(rpc_status.to_status(rich_status))
```

---

## Deadlines и Timeouts

### Deadline vs Timeout

```
TIMEOUT = "жди 5 секунд"
DEADLINE = "ответь до 14:30:05.000"

Разница критична в цепочке микросервисов:

Client → Service A → Service B → Service C

С TIMEOUT (каждый сервис ставит свой):
  Client:    timeout 10s
  Service A: timeout 10s (не знает сколько потратил Client)
  Service B: timeout 10s

  Client уже ждёт 10s, но Service C ещё работает.
  Общее время: до 30 секунд! Client давно бросил ждать.

С DEADLINE (gRPC передаёт deadline по цепочке):
  Client:    deadline = now + 10s
  Service A: получает deadline, тратит 2s → осталось 8s
  Service B: получает deadline, тратит 3s → осталось 5s
  Service C: получает deadline, тратит 4s → осталось 1s

  Если Service C не успевает до deadline → DEADLINE_EXCEEDED.
  Вся цепочка укладывается в 10 секунд.
```

**Deadline propagation** — killer-feature gRPC. Deadline автоматически передаётся через всю цепочку вызовов. Если начальный deadline истёк — все нижестоящие сервисы прекращают работу.

```python
# Клиент устанавливает deadline
response = stub.GetUser(
    request,
    timeout=5.0  # 5 секунд deadline
)

# Сервер проверяет оставшееся время
def GetUser(self, request, context):
    remaining = context.time_remaining()
    if remaining < 0.5:  # Осталось меньше 500ms
        context.abort(grpc.StatusCode.DEADLINE_EXCEEDED,
                      "Not enough time to process")

    # Передаём deadline дальше (автоматически через metadata)
    response = other_service_stub.GetData(
        data_request,
        timeout=remaining - 0.1  # Оставляем запас
    )
```

---

## Interceptors: middleware для gRPC

Interceptors — аналог middleware в Express/Django. Они перехватывают вызовы для cross-cutting concerns: логирование, метрики, авторизация, трейсинг.

```python
# Серверный interceptor: логирование и метрики

class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method  # Имя метода
        start = time.time()

        # Вызываем следующий interceptor или handler
        response = continuation(handler_call_details)

        duration = time.time() - start
        print(f"[gRPC] {method} — {duration:.3f}s")

        # Отправляем метрику в Prometheus
        grpc_request_duration.labels(method=method).observe(duration)

        return response

# Клиентский interceptor: добавление auth-токена

class AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, token):
        self.token = token

    def intercept_unary_unary(self, continuation, client_call_details, request):
        # Добавляем токен в metadata
        metadata = list(client_call_details.metadata or [])
        metadata.append(("authorization", f"Bearer {self.token}"))

        new_details = client_call_details._replace(metadata=metadata)
        return continuation(new_details, request)

# Подключение interceptors
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    interceptors=[LoggingInterceptor(), AuthInterceptor()]
)
```

**Chaining:** Interceptors выполняются в порядке добавления. Логирование → Авторизация → Rate Limiting → Трейсинг → Handler.

---

## Load Balancing для gRPC

### Проблема: HTTP/2 + multiplexing

gRPC использует долгоживущие HTTP/2 соединения. Все запросы мультиплексируются через одно TCP-соединение. Стандартный L4 load balancer (Kubernetes Service) распределяет *соединения*, а не *запросы*. Результат: один сервер получает все запросы, остальные простаивают.

```
❌ L4 Load Balancing (Kubernetes default):

Client ──[connection]──→ LB ──[connection]──→ Server A (100% нагрузки)
                              ──[idle]──→     Server B (0%)
                              ──[idle]──→     Server C (0%)

Все RPC-вызовы идут через одно соединение к Server A.

✅ L7 Load Balancing:

Client ──[RPC 1]──→ LB ──→ Server A
Client ──[RPC 2]──→ LB ──→ Server B
Client ──[RPC 3]──→ LB ──→ Server C

LB «понимает» HTTP/2 и распределяет запросы, не соединения.
```

### Подходы к балансировке

| Подход | Как работает | Плюсы | Минусы |
|--------|-------------|-------|--------|
| **L7 Proxy** (Envoy, Nginx) | Прокси парсит HTTP/2, балансирует запросы | Прозрачно для клиента | Extra hop, latency |
| **Client-side (DNS)** | Клиент получает список IP, балансирует сам | Нет extra hop | Stale DNS, нет health check |
| **Client-side (xDS)** | Control plane (Envoy) сообщает endpoints | Dynamic, advanced routing | Сложная инфраструктура |
| **Service Mesh** (Istio, Linkerd) | Sidecar proxy рядом с каждым pod | Прозрачно, language-agnostic | Sidecar overhead |

**Для Kubernetes:** Два стандартных решения:
1. **Headless Service** + client-side LB (клиент видит все pod IP)
2. **Service Mesh** (Linkerd/Istio) — sidecar делает L7 балансировку

---

## gRPC-Web: браузеры и Connect

### Почему gRPC не работает в браузерах

Браузерные API (fetch, XMLHttpRequest) не дают прямого доступа к HTTP/2 frames. Нельзя читать trailers (где gRPC-статус). Нельзя отправлять бинарные Protobuf напрямую.

### gRPC-Web

gRPC-Web — адаптированный протокол для браузеров. Нужен прокси (Envoy) между браузером и gRPC-сервером:

```
Browser ──[gRPC-Web/HTTP]──→ Envoy Proxy ──[gRPC/HTTP2]──→ gRPC Server

Ограничения gRPC-Web:
• Unary и Server Streaming — работают
• Client Streaming и Bidirectional — НЕ работают
• Base64 encoding для text mode (overhead ~33%)
```

### Connect Protocol (Buf)

Альтернатива gRPC-Web от компании Buf. Connect поддерживает:
- Нативный gRPC
- gRPC-Web
- Простой HTTP JSON (для curl/browser)

Один сервер, три протокола. Без Envoy-прокси.

```
// Connect: один handler, три протокола

// gRPC client:      → binary protobuf over HTTP/2
// gRPC-Web client:  → binary protobuf over HTTP/1.1
// curl/browser:     → JSON over HTTP/1.1

curl https://api.example.com/userservice.UserService/GetUser \
  -H "Content-Type: application/json" \
  -d '{"id": 123}'
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|------------|
| **«gRPC только для микросервисов»** | gRPC используется для мобильных приложений (меньше трафика), CLI-инструментов (kubectl использует gRPC к Kubernetes API), IoT (компактные сообщения). Не только server-to-server |
| **«Protocol Buffers = gRPC»** | Protobuf — формат сериализации. gRPC — RPC-фреймворк. Protobuf можно использовать без gRPC (для хранения, конфигов). gRPC можно использовать без Protobuf (с JSON, FlatBuffers) |
| **«gRPC не работает с браузерами»** | gRPC-Web работает через Envoy proxy. Connect Protocol позволяет обращаться к gRPC-сервисам через обычный HTTP/JSON. Ограничение: no bidirectional streaming |
| **«gRPC заменяет REST»** | REST лучше для публичных API (кэширование, curl-friendly, стандарты). gRPC лучше для внутренней связи (скорость, типизация, streaming). Netflix, Uber — используют оба |
| **«gRPC сложно дебажить»** | Бинарный формат нечитаем, да. Но: `grpcurl` (как curl для gRPC), `grpc-web-devtools`, Postman поддерживает gRPC, server reflection для discovery |
| **«Protobuf несовместим с JSON»** | Protobuf имеет стандартный JSON mapping. `google.protobuf.util.JsonFormat` конвертирует в обе стороны. gRPC gateway (grpc-ecosystem/grpc-gateway) — REST/JSON прокси перед gRPC |
| **«Streaming = WebSocket»** | gRPC streaming работает поверх HTTP/2, не WebSocket. HTTP/2 multiplexing эффективнее: множество стримов через одно TCP-соединение без отдельного upgrade |
| **«Нужен отдельный port для gRPC»** | gRPC можно запустить на стандартных портах. В Kubernetes — через один Service. Envoy и многие прокси различают gRPC и HTTP по content-type |

---

## Подводные камни

### Камень 1: Нет deadline propagation

```
❌ ПЛОХО:
def GetOrder(self, request, context):
    user = user_stub.GetUser(user_request)      # Нет deadline!
    products = product_stub.GetProducts(prod_req) # Нет deadline!
    # Если user_stub зависнет — весь запрос зависнет

✅ ХОРОШО:
def GetOrder(self, request, context):
    remaining = context.time_remaining()
    user = user_stub.GetUser(
        user_request,
        timeout=min(remaining * 0.4, 5.0)  # 40% бюджета или 5s
    )
    products = product_stub.GetProducts(
        prod_req,
        timeout=min(remaining * 0.4, 5.0)
    )
```

### Камень 2: Нарушение backward compatibility в .proto

```
❌ НЕЛЬЗЯ: Переиспользовать номер удалённого поля

// Версия 1:
message User {
  string name = 1;
  string old_field = 2;  // ← потом удалили
}

// Версия 2:
message User {
  string name = 1;
  string new_field = 2;  // ← номер 2 переиспользован!
  // Старый клиент с версией 1 будет парсить new_field
  // как old_field. Данные испортятся!
}

✅ ПРАВИЛЬНО:
message User {
  reserved 2;
  reserved "old_field";
  string name = 1;
  string new_field = 3;  // ← НОВЫЙ номер
}
```

### Камень 3: L4 load balancing для gRPC

Стандартный Kubernetes Service (ClusterIP) — L4 балансировка. Для gRPC все запросы уходят на один pod. Решение: Headless Service + client-side LB или Service Mesh.

### Камень 4: Блокирующие вызовы в async gRPC

```python
# ❌ ПЛОХО: Блокирующий вызов в async-контексте
async def GetUser(self, request, context):
    user = db.get_user_sync(request.id)  # Блокирует event loop!
    return user_pb2.User(name=user.name)

# ✅ ХОРОШО: Async вызовы
async def GetUser(self, request, context):
    user = await db.get_user_async(request.id)  # Не блокирует
    return user_pb2.User(name=user.name)
```

---

## CS-фундамент

| Концепция | Применение в gRPC |
|-----------|-------------------|
| **Serialization** | Protobuf: binary encoding (varint, length-delimited). 10-30% размера JSON. Trade-off: нечитаемость ↔ компактность и скорость |
| **Binary Protocols** | Wire types, tag-length-value (TLV) кодирование. Парсер не знает имён полей — только номера и типы |
| **Code Generation** | protoc компилирует .proto в stubs на 10+ языках. Типобезопасность на этапе компиляции, как в статически типизированных языках |
| **Streaming** | HTTP/2 multiplexing: множество потоков через одно TCP-соединение. Flow control на уровне stream'а |
| **Service Discovery** | DNS SRV records, Consul, etcd для client-side LB. xDS protocol для dynamic endpoint discovery |
| **Load Balancing** | L4 (connection) vs L7 (request). gRPC требует L7 из-за HTTP/2 multiplexing. Client-side vs proxy vs mesh |
| **Backward Compatibility** | Protobuf schema evolution: добавление полей, reserved номера. Forward + backward compatible by design |
| **Deadline Propagation** | Deadline (абсолютное время) вместо timeout (относительного). Автоматическая передача по цепочке вызовов |

---

## Куда дальше

Если начинаешь с API:
→ [[api-design]] — обзор REST, GraphQL, gRPC: когда что выбрать

Если хочешь понять альтернативы:
→ [[api-rest-deep-dive]] — REST для публичных API: constraints Филдинга, идемпотентность
→ [[api-graphql-deep-dive]] — GraphQL для сложных клиентских данных: schema, federation, caching

Современные паттерны:
→ [[api-modern-patterns]] — tRPC, Webhooks, API Gateway, BFF

HTTP/2, на котором построен gRPC:
→ [[network-http-evolution]] — multiplexing, binary framing, HPACK, QUIC

Real-time протоколы:
→ [[network-realtime-protocols]] — WebSocket, SSE, gRPC streaming — сравнение подходов

Распределённые системы:
→ [[architecture-distributed-systems]] — паттерны для систем, где gRPC используется как клей

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [gRPC Official Documentation](https://grpc.io/docs/) | Документация | Concepts, guides, tutorials |
| 2 | [Protocol Buffers: Encoding](https://protobuf.dev/programming-guides/encoding/) | Документация | Varint, wire types, TLV |
| 3 | [Protocol Buffers: Language Guide (proto3)](https://protobuf.dev/programming-guides/proto3/) | Документация | SDL, types, default values |
| 4 | [gRPC Load Balancing — grpc.io](https://grpc.io/blog/grpc-load-balancing/) | Блог | Client-side vs proxy, L4 vs L7 |
| 5 | [gRPC Custom Load Balancing](https://grpc.io/docs/guides/custom-load-balancing/) | Документация | xDS, custom policies |
| 6 | [Kubernetes: gRPC Load Balancing Without Tears](https://kubernetes.io/blog/2018/11/07/grpc-load-balancing-on-kubernetes-without-tears/) | Блог | Headless services, Linkerd |
| 7 | [Microsoft: gRPC Client-Side Load Balancing](https://learn.microsoft.com/en-us/aspnet/core/grpc/loadbalancing) | Документация | .NET gRPC, DNS resolver |
| 8 | [gRPC-Web Protocol](https://github.com/nicholasgasior/gRPC-Web-compatibility) | GitHub | Browser compatibility |
| 9 | [Connect Protocol — Buf](https://connectrpc.com/) | Документация | gRPC + gRPC-Web + JSON в одном сервере |
| 10 | [gRPC Status Codes](https://grpc.io/docs/guides/status-codes/) | Документация | 16 status codes, when to use |
| 11 | [Google Cloud: Proxyless gRPC with xDS](https://docs.google.com/service-mesh/docs/service-routing/proxyless-overview) | Документация | xDS protocol, control plane |
| 12 | [Protobuf Wire Format — Kreya](https://kreya.app/blog/protocolbuffers-wire-format/) | Блог | Visual explanation of encoding |
| 13 | [gRPC From Scratch: Protobuf Encoding](https://kmcd.dev/posts/grpc-from-scratch-part-3/) | Блог | Hands-on varint encoding |
| 14 | [Exploring gRPC Load Balancing — Medium](https://phuc-ch.medium.com/exploring-grpc-load-balancing-gateway-service-mesh-and-xds-with-go-a527ab0e7ce8) | Статья | Go examples, xDS, service mesh |
| 15 | [gRPC Load Balancing in K8s and Istio](https://shahbhat.medium.com/the-complete-guide-to-grpc-load-balancing-in-kubernetes-and-istio-01ac506f6d7f) | Статья | Service mesh approach |
| 16 | [gRPC Ecosystem: grpc-gateway](https://github.com/grpc-ecosystem/grpc-gateway) | GitHub | REST/JSON прокси для gRPC |
| 17 | [Protocol Buffers — Wikipedia](https://en.wikipedia.org/wiki/Protocol_Buffers) | Энциклопедия | История, хронология |
| 18 | [gRPC: Motivation and Design Principles](https://grpc.io/blog/principles/) | Блог | Философия дизайна от авторов |

---

**Последняя верификация**: 2026-02-10
**Уровень достоверности**: high

---

*Проверено: 2026-02-10*

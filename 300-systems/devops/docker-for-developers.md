---
title: "Docker для разработчиков: от хаоса к порядку"
created: 2025-11-24
modified: 2026-02-13
type: tutorial
status: published
confidence: high
sources_verified: true
tags:
  - topic/devops
  - devops/docker
  - devops/containers
  - tools/docker
  - type/tutorial
  - level/intermediate
related:
  - "[[microservices-vs-monolith]]"
  - "[[technical-debt]]"
  - "[[networking-overview]]"
  - "[[os-networking]]"
prerequisites:
  - "[[git-workflows]]"
reading_time: 16
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Docker для разработчиков: от хаоса к порядку

> **Аналогия для понимания:** Docker — это как **морской контейнер** для перевозки грузов. До контейнеров: каждый груз упаковывали по-своему, краны и корабли должны были адаптироваться под каждый тип. С контейнерами: стандартный размер, стандартный способ погрузки — любой корабль, любой кран, любой порт. Docker делает то же самое для софта: упаковал приложение в "контейнер" — и оно запустится одинаково на твоём маке, сервере, в AWS или Google Cloud. Netflix запускает 500,000 контейнеров в день именно благодаря этой стандартизации.

Docker — не "для DevOps", а для всех. Упаковываешь приложение + зависимости в образ. Образ работает одинаково везде: на твоём маке, на сервере, в облаке. "У меня работает" → "Работает везде".

---

## Теоретические основы

> **Контейнер** — изолированный процесс, использующий механизмы ядра Linux для ограничения видимости и ресурсов. **Docker** (Solomon Hykes, 2013) — платформа, стандартизировавшая создание, распространение и запуск контейнеров через OCI (Open Container Initiative) спецификации.

### Механизмы изоляции Linux

| Механизм | Что изолирует | Пример |
|----------|--------------|--------|
| **Namespaces** | Видимость ресурсов (PID, NET, MNT, UTS, IPC, USER) | Процессы в контейнере не видят процессы хоста |
| **cgroups** (Control Groups) | Лимиты ресурсов (CPU, RAM, I/O) | Контейнер не может использовать > 512MB RAM |
| **Union FS** (OverlayFS) | Слоистая файловая система (layers) | Образ = стек read-only слоёв + writable layer |
| **seccomp** | Системные вызовы | Блокировка опасных syscalls (e.g., reboot) |

### VM vs Container: архитектурное различие

```
VM:                            Container:
┌────────┐ ┌────────┐         ┌────────┐ ┌────────┐
│  App   │ │  App   │         │  App   │ │  App   │
│  Bins  │ │  Bins  │         │  Bins  │ │  Bins  │
│ Guest  │ │ Guest  │         └────┬───┘ └────┬───┘
│  OS    │ │  OS    │              │           │
└────┬───┘ └────┬───┘         ┌───┴───────────┴───┐
┌────┴──────────┴───┐         │   Container Engine │
│   Hypervisor      │         │   (Docker/containerd)│
└────────┬──────────┘         └────────┬──────────┘
┌────────┴──────────┐         ┌────────┴──────────┐
│   Host OS         │         │   Host OS (Linux)  │
└───────────────────┘         └───────────────────┘
```

### OCI Standards

- **OCI Image Spec** — формат образа контейнера (layers, manifest, config)
- **OCI Runtime Spec** — как запускать контейнер (lifecycle, environment)
- **OCI Distribution Spec** — как передавать образы (push/pull to registry)

> **См. также**: [[os-virtualization]] — VM vs контейнеры, [[kubernetes-basics]] — оркестрация

---

## Prerequisites (Что нужно знать заранее)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **Linux basics** | Docker построен на Linux-механизмах (namespaces, cgroups) | Любой курс Linux |
| **Командная строка** | 90% работы с Docker — через CLI | Базовый bash/terminal |
| **Что такое процесс** | Контейнер = изолированный процесс | Основы операционных систем |
| **Сеть (basics)** | Понимание портов, localhost, IP | [[networking-overview]] |
| **YAML синтаксис** | docker-compose.yml пишется на YAML | 15-минутный туториал |

---

## TL;DR (если совсем нет времени)

- **Docker** = упаковка приложения со всеми зависимостями в переносимый образ
- **Image (образ)** = read-only шаблон, **Container** = запущенный экземпляр образа
- **Multi-stage build** = builder stage (компиляция) → production stage (только runtime), экономия 60-80% размера
- **Netflix** запускает 500,000 контейнеров/день, Spotify — 10M запросов/сек на Kubernetes
- **Базовые образы**: `slim` = минимальный (~150MB), `alpine` = ещё меньше (~50MB, но может ломать пакеты)
- **Безопасность**: не запускать от root, не хранить секреты в образе, сканировать Trivy
- **2025 тренд**: Docker для dev, containerd для production (52-70% production сред)
- **Правило слоёв**: сначала редко меняющееся (requirements), потом код → быстрый кэш

---

## Кто использует Docker в production

| Компания | Масштаб | Технологии | Результат |
|----------|---------|------------|-----------|
| **Netflix** | 500,000 контейнеров/день | Titus, Docker на AWS | Миллионы batch jobs ежедневно |
| **Spotify** | 10M+ запросов/сек | Kubernetes, Helios | CPU utilization улучшился в 2-3x |
| **Uber** | Глобальная сеть | Docker microservices | Независимый деплой команд |
| **PayPal** | Финтех-масштаб | Docker + Kubernetes | Скорость релизов выросла 10x |
| **Google** | Миллиарды контейнеров/неделю | Borg → Kubernetes | Создатели Kubernetes |

> **Источники**: [Kubernetes Case Study: Spotify](https://kubernetes.io/case-studies/spotify/), [Netflix Titus](https://netflix.github.io/titus/)

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Image (Образ)** | Read-only шаблон с приложением + зависимостями | **Рецепт торта**: инструкции как сделать, но не сам торт |
| **Container** | Запущенный экземпляр образа | **Готовый торт по рецепту**: из одного рецепта — много тортов |
| **Dockerfile** | Инструкции для создания образа | **Пошаговый рецепт**: "взять муку, добавить яйца..." |
| **Registry** | Хранилище образов (Docker Hub, ECR) | **Кулинарная книга**: хранит все рецепты |
| **Layer (Слой)** | Каждая инструкция = отдельный слой | **Слоёный торт**: каждый слой отдельно, вместе — торт |
| **Volume** | Постоянное хранилище данных | **Холодильник**: торт съели, но продукты остались |
| **Docker Daemon** | Фоновый процесс, управляющий Docker | **Шеф-повар на кухне**: принимает заказы, управляет поварами |
| **Multi-stage build** | Сборка в этапах: build → production | **Съёмки фильма**: декорации в павильоне, в кино — только финал |
| **Namespace** | Изоляция ресурсов (PID, NET, MNT) | **Отдельная квартира**: свой адрес, своя мебель |
| **Cgroup** | Ограничение ресурсов (CPU, память) | **Бюджет квартиры**: не больше X электричества/воды |
| **slim** | Минимальный образ (~150MB) | **Лёгкий чемодан**: только нужное для поездки |
| **alpine** | Ещё меньше (~5MB), но musl вместо glibc | **Ручная кладь**: минимум, но не всё влезет |
| **HEALTHCHECK** | Проверка здоровья контейнера | **Датчик дыма**: проверяет "всё ли в порядке?" |
| **.dockerignore** | Исключения при COPY | **.gitignore для Docker**: не копировать лишнее |
| **depends_on** | Порядок запуска (НЕ ждёт готовности!) | **Очередь на входе**: кто первый встал, но не ждёт готовности |
| **Trivy/Snyk** | Сканеры уязвимостей | **Металлодетектор**: ищет опасные предметы в багаже |

---

## История: зачем вообще контейнеры

Представь: 2010 год. Ты деплоишь приложение на сервер.

```
Твоя машина:
- Python 3.8
- PostgreSQL 12
- Redis 6
- Ubuntu 20.04

Сервер заказчика:
- Python 2.7 (!!!)
- PostgreSQL 9
- Redis отсутствует
- CentOS 6
```

Результат предсказуем: "У меня работает!" — "А у меня нет."

Решения того времени:
- Виртуальные машины (тяжёлые, медленные)
- Vagrant (лучше, но всё равно VM)
- Документация "как настроить окружение" на 15 страниц (никто не читает)

Docker решил это элегантно: упаковываешь приложение со всеми зависимостями в образ. Этот образ работает одинаково везде — на твоём маке, на сервере, в облаке.

*Забавный факт: Docker появился в 2013, но контейнеры как концепция существовали с 1979 года (chroot в Unix). Docker просто сделал их удобными.*

---

## Как Docker работает внутри

Docker использует три механизма Linux для создания изолированных окружений:

### Namespaces — изоляция ресурсов

Namespaces делают так, что процесс "видит" только своё окружение:

```
┌─────────────────────────────────────────────────────────────┐
│ HOST SYSTEM                                                   │
│                                                               │
│  ┌─────────────────────┐     ┌─────────────────────┐         │
│  │ Container A          │     │ Container B          │         │
│  │                      │     │                      │         │
│  │ PID namespace:       │     │ PID namespace:       │         │
│  │  PID 1 = nginx       │     │  PID 1 = python      │         │
│  │  (на хосте PID 4521) │     │  (на хосте PID 4789) │         │
│  │                      │     │                      │         │
│  │ NET namespace:       │     │ NET namespace:       │         │
│  │  eth0: 172.17.0.2    │     │  eth0: 172.17.0.3    │         │
│  │                      │     │                      │         │
│  │ MNT namespace:       │     │ MNT namespace:       │         │
│  │  /: overlay fs       │     │  /: overlay fs       │         │
│  └─────────────────────┘     └─────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**Типы namespaces:**
- **PID** — процессы видят только свои PID (PID 1 внутри контейнера)
- **NET** — своя сеть, IP, порты
- **MNT** — своя файловая система
- **USER** — свои пользователи (root в контейнере ≠ root на хосте)
- **UTS** — свой hostname
- **IPC** — своя межпроцессная коммуникация

### Cgroups — ограничение ресурсов

Control Groups ограничивают сколько ресурсов может использовать контейнер:

```bash
# Ограничить память до 512MB
docker run --memory=512m my-app

# Ограничить CPU до 1.5 ядер
docker run --cpus=1.5 my-app

# Ограничить I/O
docker run --device-read-bps /dev/sda:10mb my-app
```

**Без cgroups:** один контейнер может съесть всю память и уронить хост.
**С cgroups:** OOM killer убьёт контейнер, не хост.

### OverlayFS — слоистая файловая система

Слои образа объединяются в единую файловую систему:

```
Запись (Copy-on-Write):
┌───────────────────────────────┐
│ Container writable layer       │ ← Изменения записываются сюда
├───────────────────────────────┤
│ Image layer 3 (app code)       │ ← Read-only
├───────────────────────────────┤
│ Image layer 2 (pip packages)   │ ← Read-only
├───────────────────────────────┤
│ Image layer 1 (python:slim)    │ ← Read-only
└───────────────────────────────┘

Когда контейнер читает /app/main.py:
1. Ищет в writable layer → не найден
2. Ищет в layer 3 → НАЙДЕН → читает

Когда контейнер пишет /app/main.py:
1. Копирует файл из layer 3 в writable layer (copy-on-write)
2. Изменяет копию в writable layer
3. Оригинал в layer 3 не изменён
```

**Преимущества:**
- 100 контейнеров из одного образа = 1 копия образа на диске
- Каждый контейнер видит свои изменения
- Удаление контейнера удаляет только writable layer

---

## Концепции за 5 минут

### Image (образ)

Снимок файловой системы + метаданные. Как ISO-образ диска, только умнее.

```dockerfile
# Dockerfile создаёт образ
FROM python:3.11-slim
COPY app.py /app/
CMD ["python", "/app/app.py"]
```

**Почему `python:3.11-slim`, а не просто `python:3.11`?**

Базовые образы бывают разных "размеров":

| Вариант | Размер | Что внутри |
|---------|--------|------------|
| `python:3.11` | ~1 GB | Полный Debian + gcc, dev-библиотеки, документация |
| `python:3.11-slim` | ~150 MB | Минимальный Debian, только runtime |
| `python:3.11-alpine` | ~50 MB | Alpine Linux (musl libc вместо glibc) |

**slim** — оптимальный выбор для большинства случаев. Маленький, но совместим со всеми Python-пакетами.

**alpine** — ещё меньше, но использует musl вместо glibc. Некоторые пакеты (numpy, pandas) требуют компиляции и могут ломаться. Используй если точно знаешь что делаешь.

### Container (контейнер)

Запущенный экземпляр образа. Можно запустить 100 контейнеров из одного образа.

```bash
# Создаём контейнер из образа
docker run my-app

# Несколько контейнеров из одного образа
docker run --name app1 my-app
docker run --name app2 my-app
docker run --name app3 my-app
```

### Layer (слой) — почему Docker такой быстрый

Представь слоёный торт. Каждый слой — это изменение поверх предыдущего.

```
┌─────────────────────────────┐
│ COPY . . (твой код)         │  ← Слой 4: меняется часто
├─────────────────────────────┤
│ RUN pip install -r ...      │  ← Слой 3: меняется редко
├─────────────────────────────┤
│ COPY requirements.txt .     │  ← Слой 2: меняется редко
├─────────────────────────────┤
│ FROM python:3.11            │  ← Слой 1: базовый образ
└─────────────────────────────┘
```

**Магия слоёв — кэширование:**

```
Сценарий: Ты изменил одну строчку в app.py

Без слоёв: Пересобрать ВСЁ заново (5 минут)

Со слоями:
- Слой 1 (python:3.11) → В кэше ✓
- Слой 2 (requirements.txt) → Не менялся → В кэше ✓
- Слой 3 (pip install) → Не менялся → В кэше ✓
- Слой 4 (твой код) → Изменился → Пересобираем (5 секунд)

Итого: 5 секунд вместо 5 минут
```

**Правило:** Сначала то, что меняется РЕДКО. В конце — то, что меняется ЧАСТО.

```dockerfile
# ❌ Плохой порядок: каждое изменение кода пересобирает pip install
FROM python:3.11
COPY . .                      # Код меняется → всё после этого пересобирается
RUN pip install -r requirements.txt  # 3 минуты каждый раз 😭

# ✅ Хороший порядок: pip install кэшируется
FROM python:3.11
COPY requirements.txt .       # Меняется редко
RUN pip install -r requirements.txt  # Кэшируется!
COPY . .                      # Код меняется, но pip уже установлен
```

*Это простая оптимизация, но она превращает "билд 5 минут" в "билд 10 секунд". Серьёзно.*

---

## Типичные ошибки (с реальными последствиями)

### Ошибка 1: Использование `latest`

```dockerfile
# ❌ Плохо
FROM python:latest
```

**Что происходит:**
- Понедельник: latest = 3.11
- Вторник: Python выпускает 3.12, latest обновляется
- Среда: твой билд ломается без изменений в коде

**История из жизни:** Команда не могла понять, почему CI красный. Код не менялся. Оказалось, обновился базовый образ nginx:latest с breaking changes.

```dockerfile
# ✅ Хорошо
FROM python:3.11.6-slim
```

### Ошибка 2: Запуск от root

```dockerfile
# ❌ Так делают 80% новичков
FROM node:18
COPY . /app
CMD ["node", "app.js"]
# Контейнер работает от root!
```

**Почему плохо:**
- Если атакующий получает доступ к контейнеру, он сразу root
- Потенциально может выйти на хост-систему
- Нарушает принцип least privilege

```dockerfile
# ✅ Правильно
FROM node:18
RUN useradd -r -u 1001 appuser
WORKDIR /app
COPY --chown=appuser:appuser . .
USER appuser
CMD ["node", "app.js"]
```

### Ошибка 3: Секреты в Dockerfile

```dockerfile
# ❌ НИКОГДА так не делай
ENV DATABASE_PASSWORD=super_secret_123
COPY .env /app/.env
```

**Что происходит:**
- Секреты сохраняются в слоях образа
- `docker history` покажет их любому
- Образ пушится в registry → секреты доступны всем

```dockerfile
# ✅ Секреты через runtime
ENV DATABASE_PASSWORD=""
# Передаём при запуске:
# docker run -e DATABASE_PASSWORD=xxx my-app
```

### Ошибка 4: Огромные образы

```dockerfile
# ❌ 1.2 GB образ для простого Python-приложения
FROM python:3.11
COPY . .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y gcc build-essential
```

**Проблемы:**
- Долгий pull/push (1.2 GB качать при каждом деплое)
- Больше attack surface (больше кода = больше уязвимостей)
- Дороже хранение в registry
- Медленный старт контейнера

**Multi-stage builds — это как съёмки фильма**

Представь: для съёмок фильма нужна огромная площадка, декорации, гримёрки, камеры. Но в кинотеатр попадает только готовый фильм — без всего этого.

```dockerfile
# === STAGE 1: СТРОЙКА (builder) ===
# Здесь все инструменты: компиляторы, dev-зависимости
FROM python:3.11 AS builder

WORKDIR /build
COPY requirements.txt .

# Устанавливаем ВСЕ зависимости, включая те что нужны для компиляции
RUN pip install --user -r requirements.txt
# Тут может быть gcc, build-essential, всякий мусор
# Но это нормально — мы это выкинем

# === STAGE 2: ФИНАЛЬНЫЙ ОБРАЗ (runtime) ===
# Только то, что нужно для запуска
FROM python:3.11-slim
# slim = минимальный образ без лишнего

WORKDIR /app

# Копируем ТОЛЬКО установленные пакеты из builder
COPY --from=builder /root/.local /root/.local
# Копируем код
COPY . .

# Результат: компиляторы и build-мусор остались в builder
# В финальный образ попало только нужное

CMD ["python", "app.py"]
```

**Результат на практике:**

```
Без multi-stage:
python:3.11 base        → 1.1 GB
+ твои зависимости      → 1.3 GB
+ build tools           → 1.5 GB
= Финальный образ: 1.5 GB

С multi-stage:
python:3.11-slim base   → 150 MB
+ установленные пакеты  → 100 MB
= Финальный образ: 250 MB

Уменьшение: 83%
```

*Multi-stage — это не advanced техника. Это должно быть дефолтом для production.*

### Ошибка 5: apt-get в отдельных RUN

```dockerfile
# ❌ Кэш apt-get остаётся в образе
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
```

```dockerfile
# ✅ Один слой, чистка после установки
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*
# -y = yes to all (неинтерактивно)
# --no-install-recommends = только указанные пакеты, без "рекомендуемых"
#                           (экономит ~50-200MB на образе)
# rm -rf /var/lib/apt/lists/* = удалить кэш apt (ещё ~30MB)
```

---

## Best Practices: чеклист

### Dockerfile

```
☐ Указан конкретный тег образа (не latest)
☐ Используется slim/alpine где возможно
☐ Multi-stage build для production
☐ USER не root
☐ HEALTHCHECK определён
☐ Секреты не в образе
☐ .dockerignore настроен
☐ Слои оптимизированы (редко меняющееся — сверху)
```

### .dockerignore

```dockerignore
# Обязательно исключить:
.git
.env
*.log
node_modules
__pycache__
.pytest_cache
.coverage
*.pyc
.DS_Store
```

### Пример хорошего Dockerfile

```dockerfile
# === BUILDER STAGE ===
FROM python:3.11-slim AS builder

WORKDIR /app

# Зависимости отдельно (кэшируются)
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# === PRODUCTION STAGE ===
FROM python:3.11-slim

# Безопасность: не root
RUN useradd -r -u 1001 appuser

WORKDIR /app

# Копируем только нужное
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

# Переменные окружения
ENV PATH=/home/appuser/.local/bin:$PATH
# PYTHONDONTWRITEBYTECODE=1 — не создавать .pyc файлы (экономия места)
ENV PYTHONDONTWRITEBYTECODE=1
# PYTHONUNBUFFERED=1 — логи сразу в stdout (без буферизации)
ENV PYTHONUNBUFFERED=1

USER appuser

# Health check — Docker будет проверять здоровье контейнера
# interval: каждые 30с, timeout: макс 3с на ответ
# start-period: 5с на старт приложения перед проверками
# CMD: если curl вернёт ошибку → контейнер unhealthy
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD curl -f http://localhost:8000/health || exit 1

# EXPOSE — документация: контейнер слушает порт 8000
# НЕ открывает порт наружу! Для этого нужен -p при docker run
EXPOSE 8000

# gunicorn — production WSGI-сервер для Python
# app:app = модуль app.py, переменная app (Flask/FastAPI instance)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

---

## Docker Compose: локальная разработка

Для локальной разработки с несколькими сервисами:

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .               # Собрать образ из Dockerfile в текущей директории
    ports:
      - "8000:8000"        # host_port:container_port
    environment:
      # db и redis — имена сервисов, Docker Compose создаёт DNS
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:            # Запустить db и redis ДО app
      - db                 # ВАЖНО: не ждёт готовности сервиса, только запуска!
      - redis
    volumes:
      - .:/app             # Bind mount: локальная . → /app в контейнере
                           # Изменения файлов на хосте видны внутри (hot reload)

  db:
    image: postgres:15     # Официальный образ PostgreSQL
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      # Named volume — данные сохраняются между перезапусками
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine  # alpine = минимальный образ (~30MB)

volumes:
  postgres_data:           # Объявление named volume
```

**Запуск:**
```bash
docker compose up -d      # Запустить всё
docker compose logs -f    # Смотреть логи
docker compose down       # Остановить
docker compose down -v    # Остановить + удалить volumes
```

---

## Полезные команды

### Ежедневные

```bash
# Собрать образ из Dockerfile в текущей директории
# -t = tag (имя:версия)
docker build -t my-app:1.0 .

# Запустить контейнер
# -d = detached (в фоне, без блокировки терминала)
# -p = port mapping (host:container)
# --name = имя контейнера (для удобства вместо ID)
docker run -d -p 8000:8000 --name app my-app:1.0

# Выполнить команду в запущенном контейнере
# -it = interactive + tty (интерактивный терминал)
docker exec -it app /bin/sh

# Логи контейнера
# -f = follow (как tail -f, показывает новые логи)
docker logs -f app

# Остановить (SIGTERM, ждёт 10с) и удалить контейнер
docker stop app && docker rm app
```

### Очистка (важно!)

```bash
# Удалить остановленные контейнеры
docker container prune

# Удалить неиспользуемые образы
docker image prune

# Ядерная опция: удалить ВСЁ неиспользуемое
docker system prune -a --volumes
```

*Без регулярной очистки Docker съест весь диск. Проверено на личном опыте.*

### Дебаг

```bash
# Посмотреть слои образа
docker history my-app:1.0

# Размер образов
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Что происходит в контейнере
docker stats
docker top <container>
```

---

## Production checklist

Перед деплоем в прод:

```
☐ Образ собирается из конкретных версий (не latest)
☐ Multi-stage build используется
☐ Размер образа минимальный (<500MB для большинства приложений)
☐ Не запускается от root
☐ Секреты не в образе
☐ HEALTHCHECK настроен
☐ Resource limits заданы (--memory, --cpus)
☐ Логи идут в stdout/stderr
☐ Образ проверен на уязвимости (Trivy, Snyk)
```

---

## Частые вопросы

### "Docker на M1/M2 Mac тормозит"

Да, эмуляция amd64 на ARM медленная. Решения:
- Используй arm64 образы где возможно
- `--platform linux/arm64` в docker build
- Для тяжёлых задач — remote Docker host

### "Контейнер падает сразу после запуска"

```bash
# Посмотри логи
docker logs <container>

# Или запусти интерактивно
docker run -it my-app /bin/sh
```

Обычно причина: команда завершается сразу или падает с ошибкой.

### "Изменения в коде не видны"

- Проверь, что volume смонтирован
- Проверь .dockerignore — может, файлы исключены
- Для production: пересобери образ

---

## Связи

- Архитектура приложений: [[microservices-vs-monolith]]
- Качество кода: [[technical-debt]]
- Деплой AI-приложений: [[ai-engineer-tech-stack]]
- Системный подход: [[systems-thinking]]

---

## Container Runtimes: Docker vs Podman vs containerd (2025)

| Критерий | Docker | Podman | containerd |
|----------|--------|--------|------------|
| **Архитектура** | Daemon (dockerd) | Daemonless | Low-level runtime |
| **Rootless** | Да (с 2020, зрелый) | Да (нативно) | Да |
| **Kubernetes** | Deprecated с 1.24 | CRI через Podman | Стандарт (52-70%) |
| **Startup time** | 151ms | ~150ms | 87ms |
| **Лучше для** | Development | Secure environments | Production K8s |
| **Доля рынка** | 68% dev | Растёт | 52-70% prod |

> **Рекомендация 2025**: Docker для локальной разработки, containerd для production Kubernetes. Podman — если нужна безопасность (rootless из коробки) или совместимость с Red Hat.
>
> **Источники**: [Container Runtime Comparison](https://sanj.dev/post/docker-vs-podman-comparison), [Spacelift: containerd vs Docker](https://spacelift.io/blog/containerd-vs-docker)

---

## Источники

### Теоретические основы
- Merkel D. (2014). *Docker: Lightweight Linux Containers for Consistent Development and Deployment*. — Linux Journal, первая публикация о Docker
- [OCI Specifications](https://opencontainers.org/) — Open Container Initiative: стандарты Image, Runtime, Distribution

### Официальная документация
- [Docker Docs: Best Practices](https://docs.docker.com/build/building/best-practices/) — проверено 2025-01-03
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/) — проверено 2025-01-03
- [Docker BuildKit](https://docs.docker.com/build/buildkit/) — проверено 2025-01-03

### Кейсы компаний
- [Kubernetes Case Study: Spotify](https://kubernetes.io/case-studies/spotify/) — проверено 2025-01-03
- [Netflix Titus Container Platform](https://netflix.github.io/titus/) — проверено 2025-01-03
- [Medium: How Netflix Uses Docker](https://medium.com/@priyamsanodiya340/how-netflix-uses-docker-to-run-millions-of-containers-every-week-08b0f2bea2a9) — проверено 2025-01-03

### Best Practices 2024-2025
- [Docker Blog: 8 Top Tips for 2024](https://www.docker.com/blog/8-top-docker-tips-tricks-for-2024/) — проверено 2025-01-03
- [Better Stack: Docker Build Best Practices](https://betterstack.com/community/guides/scaling-docker/docker-build-best-practices/) — проверено 2025-01-03
- [Northflank: Docker Build Optimization](https://northflank.com/blog/docker-build-and-buildx-best-practices-for-optimized-builds) — проверено 2025-01-03
- [Thinksys: Docker Best Practices 2025](https://thinksys.com/devops/docker-best-practices/) — проверено 2025-01-03

### Container Runtimes
- [Container Runtime Comparison: Docker vs Podman vs containerd](https://sanj.dev/post/docker-vs-podman-comparison) — проверено 2025-01-03
- [Spacelift: containerd vs Docker](https://spacelift.io/blog/containerd-vs-docker) — проверено 2025-01-03
- [Spacelift: Podman vs Docker](https://spacelift.io/blog/podman-vs-docker) — проверено 2025-01-03

---

**Последняя верификация**: 2025-01-03
**Уровень достоверности**: high

---

---

## Проверь себя

> [!question]- Почему порядок инструкций в Dockerfile критичен для скорости сборки?
> Docker кэширует слои. Если слой изменился -- все последующие слои пересобираются. Поэтому редко меняющиеся инструкции (COPY requirements.txt, RUN pip install) ставят в начало, а часто меняющийся код (COPY . .) -- в конец. При таком порядке изменение одной строчки кода пересобирает только последний слой (5 секунд), а не все зависимости (5 минут).

> [!question]- В чём отличие Docker-контейнера от виртуальной машины с точки зрения изоляции?
> Контейнер использует ядро хост-системы и изолируется через namespaces (PID, NET, MNT) и cgroups. VM имеет собственное ядро и полную изоляцию через гипервизор. Контейнеры легче (MБ vs ГБ), быстрее запускаются (мс vs мин), но изоляция слабее -- уязвимость в ядре хоста может затронуть контейнер. Поэтому важно не запускать контейнеры от root и использовать seccomp/AppArmor.

> [!question]- Сценарий: образ вашего Python-приложения весит 1.5 ГБ. Какие шаги уменьшат его размер?
> 1) Multi-stage build: builder stage с gcc и dev-зависимостями, production stage на python:slim только с runtime. 2) Базовый образ slim вместо полного (150 МБ vs 1 ГБ). 3) Объединить RUN-команды для apt-get и удалять кэш (rm -rf /var/lib/apt/lists/*). 4) Добавить .dockerignore для исключения .git, node_modules, __pycache__. Результат: 250 МБ вместо 1.5 ГБ (уменьшение 83%).

> [!question]- Почему depends_on в docker-compose не гарантирует готовность зависимого сервиса?
> depends_on контролирует только порядок запуска контейнеров, но не ждёт готовности сервиса внутри контейнера. PostgreSQL может стартовать контейнер за секунду, но инициализация базы займёт ещё 10 секунд. Приложение получит "connection refused". Решение: healthcheck в compose + condition: service_healthy, или retry-логика в приложении.

---

## Ключевые карточки

Чем Image отличается от Container?
?
Image (образ) -- read-only шаблон с приложением и зависимостями. Container -- запущенный экземпляр образа с собственным writable layer. Из одного образа можно запустить множество контейнеров.

Что такое Namespace в контексте Docker?
?
Механизм Linux для изоляции ресурсов. PID namespace -- свои процессы, NET -- своя сеть, MNT -- своя файловая система, USER -- свои пользователи. Контейнер "видит" только своё окружение.

Что такое Multi-stage build?
?
Сборка Docker-образа в несколько этапов: builder stage содержит компиляторы и dev-зависимости, а финальный stage -- только runtime и скомпилированный результат. Уменьшает размер образа на 60-80%.

Почему нельзя использовать тег latest в production?
?
latest указывает на последнюю версию образа, которая может измениться в любой момент. Билд может сломаться без изменений в коде. Нужно фиксировать конкретную версию (python:3.11.6-slim).

Что такое Copy-on-Write (CoW) в OverlayFS?
?
Все слои образа read-only. Когда контейнер изменяет файл, он копируется из read-only слоя в writable layer контейнера. Оригинал не изменяется. Это позволяет 100 контейнерам из одного образа занимать 1 копию на диске.

Что такое cgroups и зачем они нужны?
?
Control Groups -- механизм Linux для ограничения ресурсов контейнера (CPU, память, I/O). Без cgroups один контейнер может съесть всю память хоста. С cgroups OOM killer убьёт контейнер, а не хост.

Почему контейнер не должен работать от root?
?
Если атакующий получает доступ к контейнеру, он сразу root и потенциально может выйти на хост-систему. Решение: USER appuser в Dockerfile. Принцип least privilege.

В чём разница между slim и alpine образами?
?
slim -- минимальный Debian (~150 МБ), совместим со всеми пакетами. alpine -- ещё меньше (~50 МБ), но использует musl вместо glibc, что может ломать некоторые пакеты (numpy, pandas). slim -- оптимальный выбор для большинства.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kubernetes-basics]] | Оркестрация контейнеров: масштабирование, self-healing, rolling updates |
| Углубиться | [[ci-cd-pipelines]] | Контейнеры в pipeline: Docker build/push как часть CI/CD |
| Смежная тема | [[os-processes-threads]] | Процессы и namespaces -- фундамент, на котором работает Docker |
| Обзор | [[devops-overview]] | Вернуться к карте раздела DevOps |

*Проверено: 2026-01-09*

---
title: "Networking MOC"
created: 2025-12-26
modified: 2025-12-26
type: moc
tags:
  - moc
  - networking
  - protocols
  - infrastructure
---

# Networking MOC

> От битов до микросервисов: сетевые технологии для разработчиков

---

## Карта раздела

```
                              ┌─────────────────┐
                              │   APPLICATION   │
                              │   HTTP, gRPC    │
                              │   WebSocket     │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
          ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
          │   TRANSPORT     │ │   SECURITY      │ │   REAL-TIME     │
          │   TCP/UDP/QUIC  │ │   TLS, DNSSEC   │ │   WS, gRPC, SSE │
          └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                   │                   │                   │
                   └───────────────────┼───────────────────┘
                                       │
                              ┌────────┴────────┐
                              │     NETWORK     │
                              │   IP, Routing   │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
          ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
          │   DATA LINK     │ │    WIRELESS     │ │     CLOUD       │
          │   Ethernet,MAC  │ │   WiFi, BLE     │ │   VPC, LB, CDN  │
          └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                   │                   │                   │
                   └───────────────────┼───────────────────┘
                                       │
                              ┌────────┴────────┐
                              │    PHYSICAL     │
                              │   Cables, NIC   │
                              └─────────────────┘
```

---

## Статьи по уровням OSI

### Fundamentals (Начало изучения)
- [[network-fundamentals-for-developers]] — Что происходит при вводе URL, DNS, TCP, HTTP lifecycle

### Layer 1-2: Physical и Data Link
- [[network-physical-layer]] — Ethernet, WiFi, MAC-адреса, VLAN, коллизии

### Layer 3: Network
- [[network-ip-routing]] — IP, ICMP, ARP, маршрутизация, NAT, подсети

### Layer 4: Transport
- [[network-transport-layer]] — TCP, UDP, QUIC: handshake, flow control, congestion

### Layer 5-7: Session, Presentation, Application
- [[network-dns-tls]] — DNS резолвинг, TLS 1.3, сертификаты, HTTPS
- [[network-http-evolution]] — HTTP/1.1 → HTTP/2 → HTTP/3, эволюция протокола
- [[network-realtime-protocols]] — WebSocket, gRPC, SSE — real-time коммуникация

### Специализированные протоколы
- [[network-bluetooth]] — Bluetooth Classic, BLE, GATT, profiles
- [[network-wireless-iot]] — Zigbee, Thread, Matter, NFC, LoRaWAN
- [[network-cellular]] — 4G LTE, 5G NR, NSA/SA, Network Slicing

### Cloud и инфраструктура
- [[network-cloud-modern]] — Service Mesh, CDN, Load Balancing, eBPF
- [[os-networking]] — Linux сетевой стек, сокеты, netfilter, eBPF

### Навигация
- [[networking-overview]] — Карта раздела, терминология, learning paths

---

## Практические навыки

### Debugging и Troubleshooting
| Заметка | Уровень | Описание |
|---------|---------|----------|
| [[network-debugging-basics]] | Junior | Чеклист диагностики, базовые инструменты |
| [[network-tools-reference]] | Middle | Справочник CLI/GUI инструментов |
| [[network-tcpdump-wireshark]] | Middle | Packet analysis, анализ трафика |
| [[network-troubleshooting-advanced]] | Senior | Systematic debugging, case studies |

### Performance и Tuning
| Заметка | Уровень | Описание |
|---------|---------|----------|
| [[network-performance-optimization]] | Senior | TCP tuning, benchmarking, метрики |
| [[network-latency-optimization]] | Senior | Где теряется время, как оптимизировать |

### Security
| Заметка | Уровень | Описание |
|---------|---------|----------|
| [[network-security-fundamentals]] | Middle | DDoS, MITM, firewalls, Zero Trust |

### Container Networking
| Заметка | Уровень | Описание |
|---------|---------|----------|
| [[network-docker-deep-dive]] | Middle | Docker networking modes, namespaces |
| [[network-kubernetes-deep-dive]] | Senior | CNI, Services, Network Policies |

### Observability
| Заметка | Уровень | Описание |
|---------|---------|----------|
| [[network-observability]] | Senior | Metrics, tracing, alerting |

---

## Learning Paths

### По уровню опыта

```
JUNIOR DEVELOPER
────────────────────────────────────────────────────────────
1. [[networking-overview]]           → Общая картина, терминология
      │
2. [[network-fundamentals-for-developers]] → Что происходит при запросе
      │
3. [[network-debugging-basics]]      → Чеклист "не работает сеть"
      │
4. [[network-dns-tls]]               → DNS + HTTPS basics

MIDDLE DEVELOPER
────────────────────────────────────────────────────────────
5. [[network-transport-layer]]       → TCP/UDP/QUIC глубже
      │
6. [[network-http-evolution]]        → HTTP/1.1 → HTTP/2 → HTTP/3
      │
7. [[network-tools-reference]]       → tcpdump, curl, dig mastery
      │
8. [[network-tcpdump-wireshark]]     → Packet analysis
      │
9. [[network-security-fundamentals]] → Атаки и защита

SENIOR DEVELOPER
────────────────────────────────────────────────────────────
10. [[network-troubleshooting-advanced]] → Complex debugging
       │
11. [[network-performance-optimization]] → TCP tuning, benchmarks
       │
12. [[network-cloud-modern]]         → Service Mesh, eBPF
       │
13. [[network-kubernetes-deep-dive]] → K8s networking deep dive
       │
14. [[network-observability]]        → Network monitoring
```

### По роли

#### Backend Developer
```
[[networking-overview]] → [[network-transport-layer]] → [[network-http-evolution]]
→ [[network-realtime-protocols]] → [[network-performance-optimization]]
```

#### DevOps / SRE
```
[[network-ip-routing]] → [[network-cloud-modern]] → [[network-docker-deep-dive]]
→ [[network-kubernetes-deep-dive]] → [[network-troubleshooting-advanced]]
→ [[network-observability]]
```

#### Mobile Developer
```
[[networking-overview]] → [[network-http-evolution]] → [[network-dns-tls]]
→ [[network-transport-layer]] (QUIC) → [[network-cellular]]
→ [[network-bluetooth]] → [[network-latency-optimization]]
```

#### Security Engineer
```
[[network-dns-tls]] → [[network-security-fundamentals]]
→ [[network-tcpdump-wireshark]] → [[network-troubleshooting-advanced]]
```

---

## Ключевые концепции

### Протоколы и модели

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| **OSI Model** | 7 уровней: Physical → Application | [[networking-overview]] |
| **TCP/IP Model** | 4 уровня: практическая модель интернета | [[networking-overview]] |
| **TCP** | Надёжный, с порядком, connection-oriented | [[network-transport-layer]] |
| **UDP** | Быстрый, без гарантий, connectionless | [[network-transport-layer]] |
| **QUIC** | UDP + reliability + TLS integrated | [[network-transport-layer]] |
| **TLS 1.3** | Шифрование, 1-RTT handshake | [[network-dns-tls]] |
| **HTTP/2** | Multiplexing, header compression | [[network-http-evolution]] |
| **HTTP/3** | QUIC transport, no HOL blocking | [[network-http-evolution]] |

### Сетевые метрики

| Метрика | Что измеряет | Где используется |
|---------|--------------|------------------|
| **RTT** | Round-Trip Time | [[network-transport-layer]] |
| **TTFB** | Time To First Byte | [[network-http-evolution]] |
| **Latency** | Задержка (p50/p95/p99) | [[network-performance-optimization]] |
| **Throughput** | Пропускная способность | [[network-performance-optimization]] |
| **Packet Loss** | Процент потерянных пакетов | [[network-troubleshooting-advanced]] |

### Инфраструктурные паттерны

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| **Load Balancing** | L4 vs L7, алгоритмы | [[network-cloud-modern]] |
| **Service Mesh** | Sidecar proxy pattern | [[network-cloud-modern]] |
| **CDN** | Edge caching, geo-routing | [[network-cloud-modern]] |
| **CNI** | Container Network Interface | [[network-kubernetes-deep-dive]] |
| **Network Policies** | Pod isolation в K8s | [[network-kubernetes-deep-dive]] |

---

## Quick Reference

### Стандартные порты

| Порт | Протокол | Назначение |
|------|----------|------------|
| 22 | TCP | SSH |
| 53 | UDP/TCP | DNS |
| 80 | TCP | HTTP |
| 443 | TCP/UDP | HTTPS, HTTP/3 (QUIC) |
| 3306 | TCP | MySQL |
| 5432 | TCP | PostgreSQL |
| 6379 | TCP | Redis |
| 8080 | TCP | HTTP альтернативный |
| 9090 | TCP | Prometheus |

### HTTP Status Codes

| Код | Значение | Типичная причина |
|-----|----------|------------------|
| 200 | OK | Успех |
| 301 | Moved Permanently | Редирект постоянный |
| 302 | Found | Редирект временный |
| 400 | Bad Request | Ошибка в запросе |
| 401 | Unauthorized | Нет аутентификации |
| 403 | Forbidden | Нет прав |
| 404 | Not Found | Ресурс не найден |
| 500 | Internal Server Error | Ошибка сервера |
| 502 | Bad Gateway | Upstream не отвечает |
| 503 | Service Unavailable | Сервис перегружен |
| 504 | Gateway Timeout | Upstream timeout |

### Инструменты диагностики

| Инструмент | Назначение | Пример |
|------------|------------|--------|
| `ping` | ICMP echo, доступность | `ping 8.8.8.8` |
| `dig` | DNS lookup | `dig example.com` |
| `curl` | HTTP запросы | `curl -v https://example.com` |
| `ss` | Socket statistics | `ss -tuln` |
| `tcpdump` | Packet capture | `tcpdump -i any port 80` |
| `mtr` | Traceroute + ping | `mtr example.com` |
| `netstat` | Network statistics | `netstat -an` |

---

## Связанные области

### DevOps и инфраструктура
→ [[devops-moc]] — CI/CD, контейнеры, IaC
→ [[docker-for-developers]] — Container basics, затем [[network-docker-deep-dive]]
→ [[kubernetes-basics]] — K8s basics, затем [[network-kubernetes-deep-dive]]
→ [[observability]] — Общий observability, затем [[network-observability]]

### Security
→ [[security-moc]] — Общая безопасность
→ [[web-security-owasp]] — Web security, связано с [[network-security-fundamentals]]
→ [[authentication-authorization]] — Auth flows через сеть

### Architecture
→ [[architecture-moc]] — Архитектурные паттерны
→ [[microservices-vs-monolith]] — Сеть критична для микросервисов
→ [[api-design]] — API поверх HTTP
→ [[event-driven-architecture]] — Message brokers поверх TCP

### Cloud
→ [[cloud-moc]] — Облачные платформы
→ [[cloud-platforms-essentials]] — VPC, networking в облаках

### Operating Systems
→ [[os-processes-threads]] — Сокеты как file descriptors
→ [[os-io-devices]] — NIC, DMA, ring buffers

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 23 |
| Уровни | Junior → Middle → Senior |
| Последнее обновление | 2025-12-27 |

### Распределение по уровням

| Уровень | Количество | Темы |
|---------|------------|------|
| Junior | 4 | Fundamentals, debugging basics, DNS/TLS, HTTP |
| Middle | 8 | Transport, tools, tcpdump, security, Docker |
| Senior | 6 | Troubleshooting, performance, K8s, observability |
| Reference | 5 | Physical layer, wireless, cellular, IoT |

---

*Последнее обновление: 2025-12-27*

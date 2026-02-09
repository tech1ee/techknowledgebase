---
title: "HTTPS & TLS: handshake, сертификаты, certificate pinning"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: verified
confidence: high
tags:
  - security
  - tls
  - https
  - certificates
related:
  - "[[security-overview]]"
  - "[[security-cryptography-fundamentals]]"
  - "[[cloud-networking-security]]"
---

# HTTPS & TLS: handshake, сертификаты, certificate pinning

> HTTPS — это HTTP over TLS. TLS обеспечивает encryption, integrity, authentication. Без HTTPS любой в сети может читать/изменять трафик.

---

## TL;DR

- **TLS 1.3** — используй его (TLS 1.2 минимум)
- **Let's Encrypt** — бесплатные сертификаты, auto-renewal
- **HSTS** — принудительный HTTPS
- **Certificate Pinning** — защита от MITM (для mobile apps)
- **Никогда:** TLS 1.0/1.1, самоподписанные сертификаты в production

---

## Терминология

| Термин | Значение |
|--------|----------|
| **TLS** | Transport Layer Security (наследник SSL) |
| **Handshake** | Процесс установки TLS соединения |
| **Certificate** | Публичный ключ + identity, подписанный CA |
| **CA** | Certificate Authority — выдаёт сертификаты |
| **Chain of Trust** | Root CA → Intermediate → Server cert |
| **HSTS** | HTTP Strict Transport Security |
| **SNI** | Server Name Indication — hostname в handshake |
| **OCSP** | Online Certificate Status Protocol — проверка отзыва |
| **Pinning** | Привязка к конкретному сертификату/public key |

---

## TLS Handshake

```
┌─────────────────────────────────────────────────────────────────┐
│                 TLS 1.3 HANDSHAKE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client                                   Server                │
│    │                                         │                  │
│    │ ─────── ClientHello ──────────────────▶│                  │
│    │         (TLS version, cipher suites,   │                  │
│    │          client random, key share)     │                  │
│    │                                         │                  │
│    │◀─────── ServerHello ─────────────────── │                  │
│    │         (selected cipher, key share,   │                  │
│    │          certificate, signature)       │                  │
│    │                                         │                  │
│    │ ─────── Finished ─────────────────────▶│                  │
│    │         (encrypted with derived keys)  │                  │
│    │                                         │                  │
│    │◀─────── Finished ─────────────────────  │                  │
│    │                                         │                  │
│    │◀═══════ Encrypted Data ═══════════════▶│                  │
│    │                                         │                  │
│                                                                 │
│  TLS 1.3: 1 round-trip (1-RTT), иногда 0-RTT                  │
│  TLS 1.2: 2 round-trips (2-RTT)                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Что происходит

1. **ClientHello:** Клиент предлагает версии TLS, cipher suites, отправляет ephemeral public key
2. **ServerHello:** Сервер выбирает параметры, отправляет сертификат и подпись
3. **Key Derivation:** Обе стороны вычисляют shared secret (ECDH)
4. **Finished:** Подтверждение, что handshake прошёл успешно
5. **Encrypted:** Дальнейшие данные шифруются symmetric encryption

---

## Сертификаты

```
┌─────────────────────────────────────────────────────────────────┐
│                  CERTIFICATE CHAIN                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────┐                                     │
│  │     Root CA           │  Встроен в браузер/OS               │
│  │  (Self-signed)        │  DigiCert, Let's Encrypt, etc.      │
│  └───────────┬───────────┘                                     │
│              │ signs                                           │
│  ┌───────────▼───────────┐                                     │
│  │   Intermediate CA     │  Подписан Root CA                   │
│  │                       │                                     │
│  └───────────┬───────────┘                                     │
│              │ signs                                           │
│  ┌───────────▼───────────┐                                     │
│  │   Server Certificate  │  Подписан Intermediate              │
│  │   (example.com)       │  Это твой сертификат                │
│  └───────────────────────┘                                     │
│                                                                 │
│  Браузер проверяет всю цепочку до trusted Root CA             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Let's Encrypt (бесплатные сертификаты)

```bash
# Certbot — автоматическое получение и обновление
sudo apt install certbot python3-certbot-nginx

# Получить сертификат
sudo certbot --nginx -d example.com -d www.example.com

# Автоматическое обновление (cron)
sudo certbot renew --dry-run

# Сертификаты в /etc/letsencrypt/live/example.com/
# - fullchain.pem (cert + intermediate)
# - privkey.pem (private key)
```

### Nginx TLS Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # Сертификаты
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # TLS версии (только 1.2 и 1.3)
    ssl_protocols TLSv1.2 TLSv1.3;

    # Cipher suites (TLS 1.3 сам выбирает)
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Security Headers

```nginx
# Recommended security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### HSTS (HTTP Strict Transport Security)

```
┌─────────────────────────────────────────────────────────────────┐
│                        HSTS                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Без HSTS:                                                     │
│  User ──▶ http://example.com ──▶ 301 Redirect ──▶ https://     │
│                 ↑                                               │
│           MITM attack возможен здесь!                          │
│                                                                 │
│  С HSTS:                                                       │
│  User ──▶ Браузер сразу идёт на https://                      │
│                                                                 │
│  Header: Strict-Transport-Security: max-age=31536000           │
│                                                                 │
│  Браузер запоминает: "example.com — только HTTPS на год"       │
│                                                                 │
│  HSTS Preload:                                                 │
│  • Добавить домен в hstspreload.org                            │
│  • Браузеры уже знают про HTTPS до первого визита              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Certificate Pinning

```
┌─────────────────────────────────────────────────────────────────┐
│               CERTIFICATE PINNING                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Проблема: CA может быть скомпрометирован                      │
│            → выдать сертификат атакующему                      │
│            → MITM даже с валидным сертификатом                 │
│                                                                 │
│  Решение: Pin конкретный сертификат или public key             │
│                                                                 │
│  В mobile app:                                                 │
│  • Зашить ожидаемый public key/hash                           │
│  • Проверять при подключении                                   │
│  • Reject если не совпадает                                   │
│                                                                 │
│  ⚠️ Осторожно:                                                 │
│  • При ротации сертификата — app перестаёт работать           │
│  • Pin intermediate или backup pins                           │
│  • Только для mobile/desktop apps (не для браузеров)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Android Certificate Pinning

```kotlin
// OkHttp Certificate Pinner
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com",
        "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=") // current
    .add("api.example.com",
        "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=") // backup
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

### iOS Certificate Pinning

```swift
// TrustKit configuration
let trustKitConfig: [String: Any] = [
    kTSKPinnedDomains: [
        "api.example.com": [
            kTSKPublicKeyHashes: [
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
            ],
            kTSKEnforcePinning: true
        ]
    ]
]
TrustKit.initSharedInstance(withConfiguration: trustKitConfig)
```

---

## Проверка TLS

```bash
# OpenSSL — проверка сертификата
openssl s_client -connect example.com:443 -servername example.com

# Показать сертификат
openssl s_client -connect example.com:443 | openssl x509 -text

# Проверить chain
openssl s_client -connect example.com:443 -showcerts

# SSL Labs (онлайн)
# https://www.ssllabs.com/ssltest/

# testssl.sh — локальный аудит
./testssl.sh example.com
```

---

## Проверь себя

<details>
<summary>1. Зачем нужен TLS handshake?</summary>

**Ответ:** Установить защищённое соединение:
- Согласовать версию TLS и cipher suite
- Аутентифицировать сервер (сертификат)
- Обменяться ключами для symmetric encryption
- Проверить целостность handshake

Результат: shared secret для шифрования данных.

</details>

<details>
<summary>2. Что такое HSTS и зачем он нужен?</summary>

**Ответ:** HSTS заставляет браузер всегда использовать HTTPS.

Проблема без HSTS: первый запрос может быть HTTP → MITM возможен.

С HSTS браузер помнит: "этот домен — только HTTPS" и сразу идёт на HTTPS.

HSTS Preload — домен в списке браузера до первого визита.

</details>

<details>
<summary>3. Когда использовать certificate pinning?</summary>

**Ответ:** Для mobile/desktop apps с высокими требованиями security:
- Banking apps
- Healthcare apps
- Enterprise apps

НЕ использовать:
- Для веб-сайтов (браузеры не поддерживают)
- Если сложно обновлять app при ротации сертификата

Всегда pin backup certificate!

</details>

<details>
<summary>4. Почему TLS 1.3 лучше TLS 1.2?</summary>

**Ответ:**
- **Быстрее:** 1-RTT вместо 2-RTT handshake
- **Безопаснее:** Убраны слабые cipher suites
- **0-RTT:** Опциональный режим для resumption
- **Forward secrecy:** Всегда ECDHE

TLS 1.0/1.1 — deprecated, не использовать.

</details>

---

## Связи

- [[security-overview]] — карта раздела
- [[security-cryptography-fundamentals]] — криптографические примитивы
- [[cloud-networking-security]] — HTTPS в облаке
- [[web-security-owasp]] — HTTPS в контексте веб-безопасности

---

## Источники

- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Best Practices](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

*Проверено: 2025-12-22*

---
title: "HTTPS & TLS: handshake, сертификаты, certificate pinning"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/security
  - tls
  - "https"
  - certificates
  - type/concept
  - level/intermediate
related:
  - "[[security-overview]]"
  - "[[security-cryptography-fundamentals]]"
  - "[[cloud-networking-security]]"
prerequisites:
  - "[[security-cryptography-fundamentals]]"
reading_time: 6
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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

---

## Проверь себя

> [!question]- Мобильное приложение банка использует certificate pinning по leaf-сертификату. Через 3 месяца сертификат ротируется. Что произойдёт и как архитектурно решить эту проблему?
> Приложение перестанет подключаться к серверу — TLS handshake будет отклонён, потому что hash нового сертификата не совпадёт с захардкоженным. Решение: (1) пинить не leaf, а intermediate CA — он ротируется реже; (2) всегда добавлять backup pin с hash будущего сертификата; (3) реализовать механизм обновления pins через защищённый канал (например, через app update или конфиг с сервера, подписанный отдельным ключом). Это пересекается с архитектурой мобильных приложений — нужен graceful degradation и force-update механизм.

> [!question]- Почему в TLS 1.3 убрали поддержку RSA key exchange и оставили только ephemeral ECDHE?
> Потому что RSA key exchange не обеспечивает forward secrecy. Если приватный ключ сервера утечёт, атакующий сможет расшифровать весь ранее записанный трафик. С ECDHE каждая сессия использует уникальную ephemeral key pair — компрометация долгосрочного ключа не раскрывает прошлые сессии. Это принципиальное улучшение безопасности: TLS 1.3 делает forward secrecy обязательным, а не опциональным.

> [!question]- Сервер отдаёт HSTS-заголовок с max-age=31536000. Пользователь впервые заходит на сайт через HTTP по ссылке из письма. Защитит ли HSTS от MITM при этом первом заходе? Как решается проблема на уровне транспортного протокола?
> Нет, HSTS не защитит при самом первом визите — браузер ещё не получал заголовок и не знает, что домен требует HTTPS. Это классическая проблема "first visit". Решение — HSTS Preload: домен добавляется в hardcoded-список браузеров (hstspreload.org), и браузер знает о требовании HTTPS ещё до первого соединения. На уровне сети (см. [[network-dns-tls]]) параллельно помогает DNS-over-HTTPS/TLS, исключая перехват DNS-запросов.

> [!question]- У тебя есть два сервиса: публичный API (api.example.com) и внутренний микросервис (internal.example.com в Kubernetes). Нужен ли TLS для внутреннего трафика? Проанализируй trade-offs.
> Да, TLS для внутреннего трафика (mTLS) рекомендуется даже внутри кластера. Аргументы за: (1) zero-trust модель — сеть внутри кластера не считается безопасной; (2) compliance-требования (PCI DSS, SOC 2); (3) mutual authentication — сервисы проверяют друг друга. Trade-offs: (1) overhead на handshake и шифрование (обычно <1ms latency); (2) сложность управления сертификатами — решается service mesh (Istio, Linkerd) с автоматической ротацией; (3) усложнение отладки трафика. В большинстве production-сред mTLS оправдан.

---

## Ключевые карточки

TLS 1.3 handshake: сколько round-trips и какие основные шаги?
?
1-RTT (один round-trip). ClientHello (версия, cipher suites, ephemeral key share) → ServerHello (выбранный cipher, key share, сертификат, подпись) → обе стороны вычисляют shared secret через ECDHE → Finished. Опционально поддерживает 0-RTT для resumption.

Что такое chain of trust в сертификатах и как браузер проверяет сертификат?
?
Root CA (встроен в браузер/OS) подписывает Intermediate CA, который подписывает Server Certificate. Браузер проходит цепочку от серверного сертификата вверх до trusted Root CA. Если цепочка не ведёт к доверенному корню — соединение отклоняется.

В чём разница между certificate pinning по leaf-сертификату и по intermediate CA?
?
Pin по leaf — максимальная точность, но при любой ротации сертификата приложение ломается. Pin по intermediate — менее строгий, но intermediate ротируется значительно реже (годы, не месяцы). На практике рекомендуют пинить intermediate + добавлять backup pin.

Что такое HSTS Preload и какую проблему он решает?
?
HSTS Preload — это hardcoded-список доменов в браузерах, требующих HTTPS. Решает проблему первого визита: обычный HSTS-заголовок работает только после первого посещения, а Preload защищает даже до первого визита. Добавляется через hstspreload.org.

Почему forward secrecy важен и как TLS 1.3 его обеспечивает?
?
Forward secrecy гарантирует, что компрометация долгосрочного приватного ключа не раскроет прошлый трафик. TLS 1.3 обеспечивает это обязательным использованием ephemeral ECDHE — для каждой сессии генерируется уникальная пара ключей, которая удаляется после handshake.

Что такое OCSP Stapling и зачем его включать на сервере?
?
OCSP Stapling — сервер сам получает подтверждение от CA, что его сертификат не отозван, и прикрепляет (staple) ответ к TLS handshake. Без stapling — клиент должен сам обращаться к CA, что создаёт задержку и проблему приватности. С stapling — проверка быстрая и не требует отдельного запроса.

Какие security headers обязательны при настройке HTTPS и зачем нужен каждый?
?
HSTS (принудительный HTTPS), X-Content-Type-Options: nosniff (запрет MIME-sniffing), X-Frame-Options (защита от clickjacking), Content-Security-Policy (контроль загрузки ресурсов), Referrer-Policy (контроль утечки URL). Вместе они создают defence in depth поверх TLS.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Криптографическая база | [[security-cryptography-fundamentals]] | Понять symmetric/asymmetric encryption и хеширование, на которых строится TLS |
| Безопасность веб-приложений | [[web-security-owasp]] | HTTPS — лишь транспорт; OWASP Top 10 покрывает уязвимости уровня приложения |
| Сетевые протоколы | [[network-http-evolution]] | Как HTTP/2 и HTTP/3 (QUIC) работают поверх TLS и меняют модель соединений |
| DNS и TLS | [[network-dns-tls]] | DNS-over-TLS/HTTPS, SNI и связь DNS-резолвинга с безопасностью TLS |
| Безопасность мобильных приложений | [[mobile-security-owasp]] | OWASP Mobile Top 10 — certificate pinning в контексте полного спектра мобильных угроз |
| Защита мобильных приложений | [[mobile-app-protection]] | Практики защиты: obfuscation, tamper detection, root/jailbreak detection вместе с pinning |
| Облачная сетевая безопасность | [[cloud-networking-security]] | TLS termination, load balancers, mTLS в облачной инфраструктуре |

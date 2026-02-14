---
title: "Cryptography Fundamentals: шифрование, хеширование, подписи"
created: 2025-12-22
modified: 2025-12-22
type: concept
status: published
confidence: high
tags:
  - topic/security
  - cryptography
  - encryption
  - hashing
  - type/concept
  - level/beginner
related:
  - "[[security-overview]]"
  - "[[security-https-tls]]"
  - "[[authentication-authorization]]"
  - "[[auth-sessions-jwt-tokens]]"
  - "[[auth-passwordless-mfa]]"
reading_time: 7
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Cryptography Fundamentals: шифрование, хеширование, подписи

> Криптография — математическая основа безопасности. Не изобретай свою криптографию. Используй проверенные библиотеки.

---

## TL;DR

- **Symmetric** — один ключ для encrypt/decrypt (AES)
- **Asymmetric** — пара ключей: public/private (RSA, ECDSA)
- **Hashing** — one-way функция, необратимо (SHA-256, bcrypt)
- **Signing** — proof of authorship (private key signs, public verifies)
- **Никогда:** MD5, SHA-1 (сломаны), своя криптография

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Plaintext** | Исходные данные (открытый текст) |
| **Ciphertext** | Зашифрованные данные |
| **Key** | Секрет для шифрования/дешифрования |
| **Symmetric** | Один ключ для обеих операций |
| **Asymmetric** | Пара ключей: public + private |
| **Hash** | Фиксированная длина, необратимо |
| **Salt** | Случайные данные, добавленные перед хешированием |
| **IV/Nonce** | Initialization Vector — уникальность шифрования |
| **MAC** | Message Authentication Code — целостность |
| **Digital Signature** | Криптографическая подпись |

---

## Три столпа криптографии

```
┌─────────────────────────────────────────────────────────────────┐
│                  ТРИ ЦЕЛИ КРИПТОГРАФИИ                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CONFIDENTIALITY (Конфиденциальность)                          │
│  ─────────────────────────────────────                         │
│  Только авторизованные могут читать                            │
│  → Encryption (symmetric/asymmetric)                           │
│                                                                 │
│  INTEGRITY (Целостность)                                       │
│  ───────────────────────                                       │
│  Данные не изменены                                            │
│  → Hashing, MAC, Digital Signatures                            │
│                                                                 │
│  AUTHENTICITY (Подлинность)                                    │
│  ──────────────────────────                                    │
│  Данные от заявленного отправителя                             │
│  → Digital Signatures, Certificates                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Symmetric Encryption

```
┌─────────────────────────────────────────────────────────────────┐
│                SYMMETRIC ENCRYPTION                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Один ключ для encrypt и decrypt                               │
│                                                                 │
│  ┌───────────┐      ┌───────────┐      ┌───────────┐           │
│  │ Plaintext │ ──▶  │  Encrypt  │ ──▶  │Ciphertext │           │
│  └───────────┘      └─────┬─────┘      └───────────┘           │
│                           │                                     │
│                      ┌────┴────┐                                │
│                      │   Key   │                                │
│                      └────┬────┘                                │
│                           │                                     │
│  ┌───────────┐      ┌─────▼─────┐      ┌───────────┐           │
│  │Ciphertext │ ──▶  │  Decrypt  │ ──▶  │ Plaintext │           │
│  └───────────┘      └───────────┘      └───────────┘           │
│                                                                 │
│  Алгоритмы:                                                    │
│  ✅ AES-256-GCM — стандарт, authenticated encryption           │
│  ✅ ChaCha20-Poly1305 — быстрый, для mobile                    │
│  ❌ DES, 3DES — устаревшие                                      │
│  ❌ RC4 — сломан                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Пример AES в Python

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# ✅ Генерация ключа (256 бит)
key = AESGCM.generate_key(bit_length=256)

# Шифрование
aesgcm = AESGCM(key)
nonce = os.urandom(12)  # Уникальный для каждого сообщения!
ciphertext = aesgcm.encrypt(nonce, b"secret message", b"associated data")

# Дешифрование
plaintext = aesgcm.decrypt(nonce, ciphertext, b"associated data")

# ⚠️ ВАЖНО:
# - Nonce должен быть уникальным для каждого сообщения
# - Nonce можно передавать открыто (не секрет)
# - Key НИКОГДА не передавать открыто
```

---

## Asymmetric Encryption

```
┌─────────────────────────────────────────────────────────────────┐
│                ASYMMETRIC ENCRYPTION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Пара ключей: Public (открытый) + Private (секретный)          │
│                                                                 │
│  ENCRYPTION:                                                    │
│  ┌───────────┐    ┌─────────────┐    ┌───────────┐             │
│  │ Plaintext │ ──▶│ Public Key  │──▶│Ciphertext │             │
│  └───────────┘    │  Encrypt    │    └───────────┘             │
│                   └─────────────┘                               │
│                                                                 │
│  DECRYPTION:                                                    │
│  ┌───────────┐    ┌─────────────┐    ┌───────────┐             │
│  │Ciphertext │ ──▶│ Private Key │──▶│ Plaintext │             │
│  └───────────┘    │  Decrypt    │    └───────────┘             │
│                   └─────────────┘                               │
│                                                                 │
│  Алгоритмы:                                                    │
│  ✅ RSA-2048+ — классика, проверенный                          │
│  ✅ ECDH/ECDSA — меньший ключ, быстрее                         │
│  ✅ X25519 — modern key exchange                               │
│  ❌ RSA-1024 — слишком короткий                                 │
│                                                                 │
│  Use cases:                                                     │
│  • Key exchange (TLS handshake)                                │
│  • Digital signatures                                          │
│  • Encrypt small data (symmetric key)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Пример RSA

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Генерация ключей
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Шифрование (public key)
message = b"secret message"
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Дешифрование (private key)
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
```

---

## Hashing

```
┌─────────────────────────────────────────────────────────────────┐
│                      HASHING                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  One-way function: невозможно восстановить input               │
│                                                                 │
│  "password123" ──▶ SHA-256 ──▶ "ef92b77...a8d3" (64 hex)       │
│  "password124" ──▶ SHA-256 ──▶ "1a4f8c...b7e2" (совсем другой) │
│                                                                 │
│  Свойства хорошего хеша:                                       │
│  • Deterministic: same input → same output                     │
│  • One-way: нельзя получить input из hash                      │
│  • Collision resistant: сложно найти 2 input с одним hash     │
│  • Avalanche effect: 1 бит изменён → ~50% hash меняется       │
│                                                                 │
│  Алгоритмы:                                                    │
│  ✅ SHA-256, SHA-3 — для integrity                              │
│  ✅ bcrypt, Argon2 — для паролей (slow by design)              │
│  ❌ MD5 — сломан, collision attacks                             │
│  ❌ SHA-1 — deprecated, collision найдены                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Password Hashing

```python
import bcrypt

# ✅ Хеширование пароля при регистрации
password = b"user_password"
salt = bcrypt.gensalt(rounds=12)  # cost factor
hashed = bcrypt.hashpw(password, salt)
# Сохраняем hashed в БД

# ✅ Проверка при login
def verify_password(password: bytes, hashed: bytes) -> bool:
    return bcrypt.checkpw(password, hashed)

# ❌ НИКОГДА не делай так:
# hash = hashlib.sha256(password).hexdigest()  # Нет salt!
# hash = hashlib.md5(password).hexdigest()     # MD5 сломан!
```

### Argon2 (рекомендуемый)

```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=2,      # iterations
    memory_cost=65536, # 64MB
    parallelism=1
)

# Hash
hashed = ph.hash("password")

# Verify
try:
    ph.verify(hashed, "password")
    print("Valid")
except:
    print("Invalid")
```

---

## Digital Signatures

```
┌─────────────────────────────────────────────────────────────────┐
│                  DIGITAL SIGNATURES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Доказательство: "Это сообщение от меня и не изменено"         │
│                                                                 │
│  SIGNING:                                                       │
│  ┌─────────┐    ┌──────────┐    ┌───────────┐                  │
│  │ Message │ ──▶│ Hash     │──▶│ Encrypt   │──▶ Signature     │
│  └─────────┘    │ (SHA-256)│    │ (Private) │                  │
│                 └──────────┘    └───────────┘                  │
│                                                                 │
│  VERIFICATION:                                                  │
│  ┌───────────┐    ┌───────────┐                                │
│  │ Signature │ ──▶│ Decrypt   │──▶ Hash1                       │
│  └───────────┘    │ (Public)  │                                │
│                   └───────────┘                                │
│  ┌─────────┐      ┌──────────┐                                 │
│  │ Message │ ──▶  │ Hash     │──▶ Hash2                        │
│  └─────────┘      │ (SHA-256)│                                 │
│                   └──────────┘                                 │
│                                                                 │
│  Hash1 == Hash2 → Valid signature                              │
│                                                                 │
│  Алгоритмы:                                                    │
│  ✅ Ed25519 — современный, быстрый                              │
│  ✅ ECDSA — широко используется (Bitcoin, TLS)                 │
│  ✅ RSA-PSS — классика                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Пример Ed25519

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Генерация ключей
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Подпись
message = b"Important document"
signature = private_key.sign(message)

# Верификация (любой с public key может проверить)
try:
    public_key.verify(signature, message)
    print("Valid signature")
except:
    print("Invalid signature")
```

---

## Когда что использовать

| Задача | Алгоритм |
|--------|----------|
| Шифрование данных | AES-256-GCM |
| Обмен ключами | X25519 (ECDH) |
| Подпись | Ed25519 |
| Hash для integrity | SHA-256 |
| Password hashing | Argon2id, bcrypt |
| TLS certificates | RSA-2048+, ECDSA P-256 |
| JWT signing | RS256, ES256 |

---

## Связи

- [[security-overview]] — карта раздела
- [[security-https-tls]] — TLS использует эти примитивы
- [[authentication-authorization]] — JWT signing
- [[security-secrets-management]] — хранение ключей

---

## Источники

- [Cryptography Engineering](https://www.schneier.com/books/cryptography-engineering/) by Bruce Schneier
- [Python cryptography library](https://cryptography.io/)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)

---

*Проверено: 2025-12-22*

---

## Проверь себя

> [!question]- Почему в TLS handshake используется асимметричное шифрование только для обмена ключами, а не для всего трафика?
> Асимметричное шифрование (RSA, ECDH) в 100-1000 раз медленнее симметричного (AES). Шифровать весь трафик asymmetric-алгоритмами было бы непрактично по производительности. Поэтому TLS использует гибридную схему: asymmetric — для безопасного обмена symmetric-ключом, далее весь трафик шифруется быстрым AES-256-GCM. Это компромисс между безопасностью key exchange и скоростью передачи данных.

> [!question]- Разработчик хранит пароли как SHA-256(password + username). Какие проблемы у этого подхода и как исправить?
> Проблемы: (1) SHA-256 слишком быстрый — GPU перебирает миллиарды хешей в секунду; (2) username как salt предсказуем и одинаков на разных сервисах, что позволяет строить rainbow tables для популярных username. Исправление: использовать Argon2id или bcrypt — они специально медленные (time/memory cost), генерируют случайный salt автоматически и хранят его вместе с хешем.

> [!question]- JWT токен подписан алгоритмом HS256 (HMAC-SHA256). Как изменится архитектура, если нужно, чтобы токен проверяли несколько независимых микросервисов? Какой алгоритм выбрать и почему?
> HS256 — symmetric (один shared secret). Все микросервисы должны знать секрет — если один скомпрометирован, утекает ключ для всех, и любой сервис может подделывать токены. Переход на RS256 или ES256 (asymmetric): auth-сервис подписывает private key, микросервисы проверяют public key. Public key можно раздавать безопасно, и ни один потребитель не может создавать токены.

> [!question]- Система использует AES-256-GCM для шифрования файлов. Разработчик для простоты использует один и тот же nonce для всех файлов. Почему это критическая уязвимость?
> В AES-GCM повторное использование nonce с тем же ключом полностью разрушает безопасность: (1) XOR двух ciphertext раскрывает XOR двух plaintext, что позволяет восстанавливать содержимое; (2) утекает authentication key (GHASH), позволяя подделывать сообщения. Nonce должен быть уникальным для каждой операции шифрования — либо случайный (12 байт), либо счётчик.

---

## Ключевые карточки

Чем symmetric encryption отличается от asymmetric?
?
Symmetric — один ключ для шифрования и дешифрования (AES), быстрый. Asymmetric — пара ключей public/private (RSA, ECDSA), медленнее, но public key можно передавать открыто. На практике asymmetric используют для обмена symmetric-ключом (гибридная схема TLS).

Почему для хеширования паролей нельзя использовать SHA-256?
?
SHA-256 слишком быстрый — GPU перебирает миллиарды хешей в секунду. Для паролей нужны специально медленные алгоритмы: Argon2id или bcrypt с настраиваемым cost factor и автоматическим salt.

Что такое salt и зачем он нужен при хешировании паролей?
?
Salt — случайные данные, уникальные для каждого пароля, добавляемые перед хешированием. Без salt одинаковые пароли дают одинаковые хеши, что позволяет использовать rainbow tables. Salt хранится вместе с хешем и не является секретом.

Как работает digital signature (подписание и проверка)?
?
Подписание: вычисляется hash сообщения, затем hash шифруется private key — это и есть signature. Проверка: signature расшифровывается public key, отдельно вычисляется hash сообщения, хеши сравниваются. Совпадение гарантирует integrity и authenticity.

Почему nonce/IV должен быть уникальным для каждой операции шифрования?
?
Повторное использование nonce с тем же ключом в AES-GCM позволяет XOR-ить ciphertext для восстановления plaintext и утечки authentication key. Nonce должен быть уникальным — случайным или счётчиком.

Какой алгоритм выбрать для JWT-подписей в микросервисной архитектуре и почему?
?
RS256 или ES256 (asymmetric). Auth-сервис подписывает private key, остальные сервисы проверяют public key. В отличие от HS256 (symmetric shared secret), компрометация одного сервиса не позволяет подделывать токены.

Какие криптографические алгоритмы считаются устаревшими и небезопасными?
?
MD5 — сломан, найдены коллизии. SHA-1 — deprecated, коллизии найдены в 2017. DES/3DES — устаревшие. RC4 — сломан. RSA-1024 — слишком короткий ключ. Ни один из них нельзя использовать в новых системах.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| TLS/HTTPS | [[security-https-tls]] | Увидеть, как криптографические примитивы работают вместе в TLS handshake |
| JWT и сессии | [[auth-sessions-jwt-tokens]] | Понять, как подписи и HMAC применяются в токенах аутентификации |
| OAuth 2.0 / OIDC | [[authentication-authorization]] | Разобраться, как криптография обеспечивает безопасность протоколов авторизации |
| Passwordless и MFA | [[auth-passwordless-mfa]] | Изучить, как асимметричная криптография используется в WebAuthn/FIDO2 |
| Управление секретами | [[security-secrets-management]] | Научиться безопасно хранить и ротировать криптографические ключи |
| Карта раздела | [[security-overview]] | Получить полную картину области безопасности и выбрать следующую тему |

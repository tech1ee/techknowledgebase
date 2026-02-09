# OWASP MASVS & MASTG: Mobile Application Security Verification

## Metadata
- **Тип:** Deep-dive
- **Технологии:** Mobile Security, OWASP, Android, iOS
- **Уровень:** Advanced
- **Дата обновления:** 2026-01-29
- **Версии:** MASVS 2.1.0, MASTG 1.7.x

---

## TL;DR

> **MASVS** (Mobile Application Security Verification Standard) — это стандарт безопасности мобильных приложений от OWASP, определяющий ЧТО проверять.
> **MASTG** (Mobile Application Security Testing Guide) — это руководство по тестированию, описывающее КАК проверять.
> Вместе они образуют MAS (Mobile Application Security) — комплексный фреймворк для оценки и улучшения безопасности мобильных приложений.

**MASVS 2.0+ структура:**
```
┌─────────────────────────────────────────────────────────────┐
│                    MASVS 2.0 Categories                      │
├─────────────────────────────────────────────────────────────┤
│  MASVS-STORAGE   │  Secure Data Storage                     │
│  MASVS-CRYPTO    │  Cryptography                            │
│  MASVS-AUTH      │  Authentication & Authorization          │
│  MASVS-NETWORK   │  Network Communication                   │
│  MASVS-PLATFORM  │  Platform Interaction                    │
│  MASVS-CODE      │  Code Quality & Security                 │
│  MASVS-RESILIENCE│  Anti-Tampering & Reverse Engineering   │
│  MASVS-PRIVACY   │  Privacy Protection (NEW in 2.0)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Почему это важно

### Проблема хаотичного тестирования

До появления MASVS и MASTG тестирование мобильной безопасности было:

```
Проблема 1: Inconsistency
├── Каждый пентестер использовал свой чеклист
├── Разные компании — разные стандарты
├── Невозможно сравнить результаты аудитов
└── "Secure" означало разное для разных людей

Проблема 2: Incomplete Coverage
├── Фокус на очевидных уязвимостях
├── Пропуск специфичных для mobile проблем
├── Игнорирование privacy аспектов
└── Отсутствие систематического подхода

Проблема 3: No Verification Baseline
├── Как доказать заказчику безопасность?
├── Какой уровень защиты достаточен?
├── Как приоритизировать исправления?
└── Нет общепринятых метрик
```

### История создания MAS

```
Timeline развития стандартов:

2016 ─── MASVS 1.0
         └── Первый релиз, L1/L2 уровни

2017 ─── MSTG 1.0
         └── Mobile Security Testing Guide

2018 ─── MASVS 1.1
         └── Уточнения требований

2019 ─── MSTG 1.1.3
         └── Расширение тест-кейсов

2020 ─── MASVS 1.2
         └── Актуализация под новые платформы

2023 ─── MASVS 2.0 (Major Refactor!)
         ├── Новая структура категорий
         ├── Убраны L1/L2 уровни
         ├── Добавлена категория PRIVACY
         └── Атомарные требования

2024 ─── MASVS 2.1 + MASTG → MAS
         ├── Unified MAS Framework
         ├── MAS Testing Profiles
         └── MAS Checklist integration

2025 ─── MAS ecosystem maturity
         ├── MASTG 1.7.x
         ├── Integration с CI/CD
         └── Automated compliance checking
```

### MASVS 2.0: Революционные изменения

**Почему потребовался рефакторинг:**

```
MASVS 1.x проблемы:
├── L1/L2/R уровни создавали путаницу
│   └── "L2 нужен только для банков" — миф
├── Требования были слишком абстрактными
│   └── "Use secure storage" — что конкретно?
├── Сложно мапить на конкретные тесты
│   └── Одно требование — много тест-кейсов
└── Privacy был разбросан по разным секциям

MASVS 2.0 решения:
├── Атомарные требования (одно требование = один тест)
├── Чёткая структура по категориям
├── MAS Testing Profiles вместо L1/L2
├── Отдельная категория PRIVACY
└── Прямая связь с MASTG тест-кейсами
```

### Роль в индустрии

```
Кто использует MASVS/MASTG:

Разработчики
├── Secure coding guidelines
├── Security requirements для features
└── Self-assessment checklist

Security Teams
├── Penetration testing methodology
├── Vulnerability assessment
└── Security architecture review

Compliance Officers
├── PCI DSS mobile requirements
├── GDPR privacy compliance
├── Industry-specific regulations

Procurement
├── Vendor security assessment
├── Third-party app evaluation
└── Contract security requirements
```

---

## Что такое MASVS 2.0+

### Структура стандарта

MASVS 2.0 организован в 8 категорий, каждая содержит атомарные требования:

```
MASVS 2.0 Structure
│
├── MASVS-STORAGE (12 требований)
│   └── Защита данных в покое
│
├── MASVS-CRYPTO (4 требования)
│   └── Криптографические практики
│
├── MASVS-AUTH (3 требования)
│   └── Аутентификация и авторизация
│
├── MASVS-NETWORK (3 требования)
│   └── Сетевая безопасность
│
├── MASVS-PLATFORM (4 требования)
│   └── Взаимодействие с платформой
│
├── MASVS-CODE (4 требования)
│   └── Качество и безопасность кода
│
├── MASVS-RESILIENCE (4 требования)
│   └── Защита от реверс-инжиниринга
│
└── MASVS-PRIVACY (4 требования)
    └── Приватность пользователей
```

### MASVS-STORAGE: Безопасное хранение данных

Защита конфиденциальных данных в покое — одна из критических областей мобильной безопасности.

```
MASVS-STORAGE Controls:

MASVS-STORAGE-1
├── Описание: Приложение безопасно хранит sensitive данные
├── Проверка: Данные зашифрованы или в secure storage
└── Платформы: Android Keystore, iOS Keychain

MASVS-STORAGE-2
├── Описание: Приложение не хранит sensitive данные в логах
├── Проверка: Логи не содержат PII, credentials, tokens
└── Инструменты: Logcat analysis, Console.app

MASVS-STORAGE-3
├── Описание: Приложение не делится sensitive данными с third parties
├── Проверка: SDK analytics не получают PII
└── Важно: Crash reporting, analytics SDKs

MASVS-STORAGE-4
├── Описание: Keyboard cache не содержит sensitive данных
├── Проверка: Secure text fields отключают кеширование
└── Платформы: textNoSuggestions, secureTextEntry

MASVS-STORAGE-5
├── Описание: Clipboard не содержит sensitive данных
├── Проверка: Копирование отключено для паролей
└── Риск: Другие приложения могут читать clipboard

MASVS-STORAGE-6
├── Описание: Sensitive данные не в backups
├── Проверка: android:allowBackup="false", excludes
└── Платформы: Auto Backup, iCloud Backup

MASVS-STORAGE-7
├── Описание: Sensitive данные не отображаются при уходе в background
├── Проверка: Screenshot protection, window flags
└── Механизм: FLAG_SECURE, UIApplication lifecycle

MASVS-STORAGE-8
├── Описание: Sensitive данные не в device logs
├── Проверка: System logs проверены
└── Инструменты: adb logcat, idevice_id

MASVS-STORAGE-9
├── Описание: Приложение удаляет sensitive данные по необходимости
├── Проверка: Logout очищает все данные
└── Важно: Memory, files, caches, databases

MASVS-STORAGE-10
├── Описание: Приложение не хранит sensitive данные в WebView cache
├── Проверка: WebView storage очищается
└── Риск: Cookies, localStorage, indexedDB

MASVS-STORAGE-11
├── Описание: PII хранится минимально необходимое время
├── Проверка: Data retention policies implemented
└── Связь: GDPR, CCPA compliance

MASVS-STORAGE-12
├── Описание: Минимизация PII в запросах разрешений
├── Проверка: Только необходимые permissions
└── Принцип: Data minimization
```

**Примеры безопасного хранения:**

```kotlin
// Android: Использование EncryptedSharedPreferences
// MASVS-STORAGE-1 compliant

class SecureStorageManager(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val securePrefs = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun storeToken(token: String) {
        securePrefs.edit()
            .putString("auth_token", token)
            .apply()
    }

    fun getToken(): String? {
        return securePrefs.getString("auth_token", null)
    }

    fun clearAll() {
        // MASVS-STORAGE-9: Очистка при logout
        securePrefs.edit().clear().apply()
    }
}
```

```swift
// iOS: Keychain Services
// MASVS-STORAGE-1 compliant

class KeychainManager {

    enum KeychainError: Error {
        case duplicateItem
        case itemNotFound
        case unexpectedStatus(OSStatus)
    }

    func store(token: Data, for account: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            kSecValueData as String: token
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        guard status == errSecSuccess else {
            if status == errSecDuplicateItem {
                try update(token: token, for: account)
                return
            }
            throw KeychainError.unexpectedStatus(status)
        }
    }

    func retrieve(for account: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data else {
            throw KeychainError.itemNotFound
        }

        return data
    }

    func delete(for account: String) throws {
        // MASVS-STORAGE-9: Удаление при logout
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }
}
```

### MASVS-CRYPTO: Криптография

```
MASVS-CRYPTO Controls:

MASVS-CRYPTO-1
├── Описание: Приложение использует современную криптографию
├── Требования:
│   ├── AES-256 для симметричного шифрования
│   ├── RSA-2048+ или ECDSA P-256+ для асимметричного
│   ├── SHA-256+ для хеширования
│   └── PBKDF2/Argon2/bcrypt для паролей
└── Запрещено: DES, 3DES, RC4, MD5, SHA-1, ECB mode

MASVS-CRYPTO-2
├── Описание: Приложение использует проверенные реализации
├── Требования:
│   ├── Platform crypto APIs (Android Keystore, iOS CryptoKit)
│   ├── Проверенные библиотеки (Tink, libsodium)
│   └── Нет custom crypto implementations
└── Риск: Homegrown crypto почти всегда уязвима

MASVS-CRYPTO-3
├── Описание: Ключи управляются безопасно
├── Требования:
│   ├── Hardware-backed key storage (TEE, Secure Enclave)
│   ├── Ключи не hardcoded в коде
│   └── Key derivation из user input корректен
└── Инструменты: Android Keystore, iOS Secure Enclave

MASVS-CRYPTO-4
├── Описание: Случайные числа криптографически стойкие
├── Требования:
│   ├── SecureRandom (Android)
│   ├── Security.randomBytes (iOS)
│   └── Нет Math.random() для security
└── Атака: Predictable PRNG → session hijacking
```

**Пример правильной криптографии:**

```kotlin
// Android: Hardware-backed keys
// MASVS-CRYPTO-1, MASVS-CRYPTO-3 compliant

class CryptoManager(private val context: Context) {

    companion object {
        private const val KEY_ALIAS = "app_encryption_key"
        private const val TRANSFORMATION = "AES/GCM/NoPadding"
    }

    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }

    init {
        if (!keyStore.containsAlias(KEY_ALIAS)) {
            generateKey()
        }
    }

    private fun generateKey() {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val spec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setUserAuthenticationRequired(false) // или true для biometric
            .setRandomizedEncryptionRequired(true)
            .build()

        keyGenerator.init(spec)
        keyGenerator.generateKey()
    }

    fun encrypt(data: ByteArray): EncryptedData {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        val key = keyStore.getKey(KEY_ALIAS, null) as SecretKey

        cipher.init(Cipher.ENCRYPT_MODE, key)

        val encryptedBytes = cipher.doFinal(data)
        val iv = cipher.iv

        return EncryptedData(
            ciphertext = encryptedBytes,
            iv = iv
        )
    }

    fun decrypt(encryptedData: EncryptedData): ByteArray {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        val key = keyStore.getKey(KEY_ALIAS, null) as SecretKey

        val spec = GCMParameterSpec(128, encryptedData.iv)
        cipher.init(Cipher.DECRYPT_MODE, key, spec)

        return cipher.doFinal(encryptedData.ciphertext)
    }
}

data class EncryptedData(
    val ciphertext: ByteArray,
    val iv: ByteArray
)
```

```swift
// iOS: CryptoKit для современной криптографии
// MASVS-CRYPTO-1, MASVS-CRYPTO-2 compliant

import CryptoKit

class ModernCrypto {

    // AES-GCM encryption
    func encrypt(data: Data, using key: SymmetricKey) throws -> Data {
        let sealedBox = try AES.GCM.seal(data, using: key)
        return sealedBox.combined!
    }

    func decrypt(combinedData: Data, using key: SymmetricKey) throws -> Data {
        let sealedBox = try AES.GCM.SealedBox(combined: combinedData)
        return try AES.GCM.open(sealedBox, using: key)
    }

    // Key derivation from password
    func deriveKey(from password: String, salt: Data) -> SymmetricKey {
        let passwordData = Data(password.utf8)

        // HKDF for key derivation
        let derivedKey = HKDF<SHA256>.deriveKey(
            inputKeyMaterial: SymmetricKey(data: passwordData),
            salt: salt,
            info: Data("encryption".utf8),
            outputByteCount: 32
        )

        return derivedKey
    }

    // Secure random generation
    func generateRandomBytes(count: Int) -> Data {
        var bytes = [UInt8](repeating: 0, count: count)
        let status = SecRandomCopyBytes(kSecRandomDefault, count, &bytes)

        guard status == errSecSuccess else {
            fatalError("Failed to generate random bytes")
        }

        return Data(bytes)
    }

    // Digital signature with Secure Enclave
    func signWithSecureEnclave(data: Data) throws -> Data {
        // Создаём ключ в Secure Enclave
        var error: Unmanaged<CFError>?

        guard let accessControl = SecAccessControlCreateWithFlags(
            kCFAllocatorDefault,
            kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            [.privateKeyUsage],
            &error
        ) else {
            throw error!.takeRetainedValue() as Error
        }

        let attributes: [String: Any] = [
            kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
            kSecAttrKeySizeInBits as String: 256,
            kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave,
            kSecPrivateKeyAttrs as String: [
                kSecAttrIsPermanent as String: true,
                kSecAttrAccessControl as String: accessControl
            ]
        ]

        guard let privateKey = SecKeyCreateRandomKey(
            attributes as CFDictionary,
            &error
        ) else {
            throw error!.takeRetainedValue() as Error
        }

        // Подписываем данные
        guard let signature = SecKeyCreateSignature(
            privateKey,
            .ecdsaSignatureMessageX962SHA256,
            data as CFData,
            &error
        ) else {
            throw error!.takeRetainedValue() as Error
        }

        return signature as Data
    }
}
```

### MASVS-AUTH: Аутентификация и авторизация

```
MASVS-AUTH Controls:

MASVS-AUTH-1
├── Описание: Приложение использует безопасные механизмы аутентификации
├── Требования:
│   ├── Биометрия связана с cryptographic operations
│   ├── Не только UI-based биометрия
│   ├── Fallback к PIN/password безопасен
│   └── Session management на сервере
└── Риск: Biometric bypass через Frida

MASVS-AUTH-2
├── Описание: Sensitive операции требуют re-authentication
├── Примеры:
│   ├── Изменение пароля
│   ├── Финансовые транзакции
│   ├── Изменение security settings
│   └── Доступ к PII
└── Паттерн: Step-up authentication

MASVS-AUTH-3
├── Описание: Authorization проверяется на сервере
├── Требования:
│   ├── Сервер валидирует все действия
│   ├── Клиент НЕ доверяет для авторизации
│   └── Role-based access control
└── Атака: Client-side authorization bypass
```

**Пример безопасной биометрии:**

```kotlin
// Android: Cryptographic biometric authentication
// MASVS-AUTH-1 compliant

class BiometricAuthManager(
    private val activity: FragmentActivity,
    private val cryptoManager: CryptoManager
) {
    private val executor = ContextCompat.getMainExecutor(activity)

    fun authenticateAndDecrypt(
        encryptedData: EncryptedData,
        onSuccess: (ByteArray) -> Unit,
        onError: (String) -> Unit
    ) {
        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {

                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    // Криптографическая операция требует биометрию
                    val cipher = result.cryptoObject?.cipher
                    if (cipher != null) {
                        try {
                            val decrypted = cipher.doFinal(encryptedData.ciphertext)
                            onSuccess(decrypted)
                        } catch (e: Exception) {
                            onError("Decryption failed: ${e.message}")
                        }
                    } else {
                        onError("No crypto object")
                    }
                }

                override fun onAuthenticationError(
                    errorCode: Int,
                    errString: CharSequence
                ) {
                    onError(errString.toString())
                }

                override fun onAuthenticationFailed() {
                    // Пользователь не распознан, можно повторить
                }
            }
        )

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Authenticate")
            .setSubtitle("Confirm your identity")
            .setNegativeButtonText("Cancel")
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG
            )
            .build()

        // Получаем cipher для дешифрования
        val cipher = cryptoManager.getDecryptionCipher(encryptedData.iv)
        val cryptoObject = BiometricPrompt.CryptoObject(cipher)

        biometricPrompt.authenticate(promptInfo, cryptoObject)
    }
}
```

```swift
// iOS: LAContext with crypto binding
// MASVS-AUTH-1 compliant

import LocalAuthentication
import Security

class BiometricAuth {

    func authenticateAndAccess(completion: @escaping (Result<Data, Error>) -> Void) {
        let context = LAContext()
        var error: NSError?

        guard context.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            error: &error
        ) else {
            completion(.failure(error ?? BiometricError.notAvailable))
            return
        }

        // Keychain item с requiresBiometry
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: "protected_secret",
            kSecReturnData as String: true,
            kSecUseAuthenticationContext as String: context,
            kSecUseOperationPrompt as String: "Authenticate to access secret"
        ]

        // Биометрия привязана к криптографической операции
        DispatchQueue.global().async {
            var result: AnyObject?
            let status = SecItemCopyMatching(query as CFDictionary, &result)

            DispatchQueue.main.async {
                if status == errSecSuccess, let data = result as? Data {
                    completion(.success(data))
                } else {
                    completion(.failure(BiometricError.accessDenied))
                }
            }
        }
    }

    // Сохранение с биометрической защитой
    func storeProtectedSecret(_ secret: Data) throws {
        var error: Unmanaged<CFError>?

        guard let accessControl = SecAccessControlCreateWithFlags(
            kCFAllocatorDefault,
            kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
            [.biometryCurrentSet], // Invalidate при изменении биометрии
            &error
        ) else {
            throw error!.takeRetainedValue() as Error
        }

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: "protected_secret",
            kSecValueData as String: secret,
            kSecAttrAccessControl as String: accessControl
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw BiometricError.storeFailed
        }
    }
}

enum BiometricError: Error {
    case notAvailable
    case accessDenied
    case storeFailed
}
```

### MASVS-NETWORK: Сетевая безопасность

```
MASVS-NETWORK Controls:

MASVS-NETWORK-1
├── Описание: Приложение использует TLS для всех соединений
├── Требования:
│   ├── TLS 1.2+ обязателен
│   ├── Нет cleartext traffic
│   ├── Сильные cipher suites
│   └── Certificate validation включена
└── Android: Network Security Config

MASVS-NETWORK-2
├── Описание: TLS настроен по best practices
├── Требования:
│   ├── Нет trust всех сертификатов
│   ├── Certificate pinning для критичных endpoints
│   ├── Проверка hostname
│   └── Нет user-installed CA trust
└── Атака: MitM без pinning

MASVS-NETWORK-3
├── Описание: Приложение валидирует сертификаты правильно
├── Проверки:
│   ├── Chain of trust
│   ├── Certificate expiration
│   ├── Revocation (OCSP/CRL)
│   └── Hostname matching
└── Риск: Insecure TrustManager
```

**Network Security Configuration (Android):**

```xml
<!-- res/xml/network_security_config.xml -->
<!-- MASVS-NETWORK-1, MASVS-NETWORK-2 compliant -->

<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Глобальная конфигурация: запрет cleartext -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <!-- Доверять только системным CA -->
            <certificates src="system" />
            <!-- НЕ включаем user CA в production -->
        </trust-anchors>
    </base-config>

    <!-- Certificate pinning для критичных endpoints -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2026-12-31">
            <!-- Primary pin (SPKI hash) -->
            <pin digest="SHA-256">
                AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
            </pin>
            <!-- Backup pin -->
            <pin digest="SHA-256">
                BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
            </pin>
        </pin-set>
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </domain-config>

    <!-- Debug-only: разрешить user CA для тестирования -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

```kotlin
// Programmatic certificate pinning с OkHttp
// MASVS-NETWORK-2 compliant

class SecureHttpClient {

    fun createPinnedClient(): OkHttpClient {
        val certificatePinner = CertificatePinner.Builder()
            .add(
                "api.example.com",
                "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
            )
            .add(
                "api.example.com",
                "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
            )
            .build()

        val spec = ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
            .tlsVersions(TlsVersion.TLS_1_2, TlsVersion.TLS_1_3)
            .cipherSuites(
                CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
                CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
                CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
                CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
            )
            .build()

        return OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .connectionSpecs(listOf(spec))
            .build()
    }
}
```

```swift
// iOS: URLSession с pinning через delegate
// MASVS-NETWORK-2 compliant

class PinnedURLSession: NSObject, URLSessionDelegate {

    private let pinnedCertificates: [Data]

    init(pinnedCertificates: [Data]) {
        self.pinnedCertificates = pinnedCertificates
    }

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Стандартная валидация
        var error: CFError?
        let isValid = SecTrustEvaluateWithError(serverTrust, &error)

        guard isValid else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Certificate pinning
        guard let serverCertificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        let serverCertData = SecCertificateCopyData(serverCertificate) as Data

        if pinnedCertificates.contains(serverCertData) {
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

### MASVS-PLATFORM: Взаимодействие с платформой

```
MASVS-PLATFORM Controls:

MASVS-PLATFORM-1
├── Описание: Приложение использует IPC безопасно
├── Компоненты Android:
│   ├── Intent validation
│   ├── Content Provider permissions
│   ├── Broadcast receivers protection
│   └── Service binding security
└── Компоненты iOS: URL Schemes, Universal Links

MASVS-PLATFORM-2
├── Описание: WebViews настроены безопасно
├── Требования:
│   ├── JavaScript отключен если не нужен
│   ├── Нет file:// доступа
│   ├── Нет JavaScript bridges к sensitive функциям
│   └── SSL errors не игнорируются
└── Атака: XSS через WebView, JavaScript injection

MASVS-PLATFORM-3
├── Описание: Приложение валидирует deep links
├── Требования:
│   ├── Параметры sanitized
│   ├── Нет sensitive actions через URI
│   └── App Links/Universal Links предпочтительнее
└── Атака: URL scheme hijacking

MASVS-PLATFORM-4
├── Описание: Sensitive функции защищены от других приложений
├── Механизмы:
│   ├── exported="false" по умолчанию
│   ├── Permission protection
│   ├── Signature-level permissions
│   └── Intent filtering
└── Android 12+: explicit export required
```

**Пример безопасной работы с WebView:**

```kotlin
// Android: Secure WebView configuration
// MASVS-PLATFORM-2 compliant

class SecureWebViewActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_webview)

        webView = findViewById(R.id.webView)
        configureSecureWebView()
    }

    private fun configureSecureWebView() {
        webView.settings.apply {
            // Минимально необходимые настройки
            javaScriptEnabled = false  // Включать только если необходимо

            // Запрет доступа к файловой системе
            allowFileAccess = false
            allowFileAccessFromFileURLs = false
            allowUniversalAccessFromFileURLs = false
            allowContentAccess = false

            // Запрет геолокации и т.д.
            setGeolocationEnabled(false)

            // Mixed content
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW

            // Кеширование
            cacheMode = WebSettings.LOAD_NO_CACHE
        }

        // Secure WebViewClient
        webView.webViewClient = object : WebViewClient() {

            override fun onReceivedSslError(
                view: WebView?,
                handler: SslErrorHandler?,
                error: SslError?
            ) {
                // НИКОГДА не вызывать handler.proceed()
                handler?.cancel()
                showSecurityError()
            }

            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
                val url = request?.url?.toString() ?: return true

                // Whitelist разрешённых доменов
                val allowedDomains = listOf("example.com", "trusted.com")
                val host = Uri.parse(url).host ?: return true

                return !allowedDomains.any { host.endsWith(it) }
            }
        }

        // Очистка при уходе
        webView.clearCache(true)
        webView.clearHistory()
    }

    override fun onDestroy() {
        super.onDestroy()
        // MASVS-STORAGE-10: очистка WebView данных
        webView.clearCache(true)
        webView.clearHistory()
        webView.clearFormData()

        // Удаление cookies
        CookieManager.getInstance().apply {
            removeAllCookies(null)
            flush()
        }

        webView.destroy()
    }

    private fun showSecurityError() {
        // Показать ошибку пользователю
    }
}
```

### MASVS-CODE: Качество и безопасность кода

```
MASVS-CODE Controls:

MASVS-CODE-1
├── Описание: Приложение подписано и собрано правильно
├── Требования:
│   ├── Release builds с proper signing
│   ├── Debugging отключен
│   ├── Debug symbols stripped
│   └── ProGuard/R8 оптимизация
└── Проверка: APK/IPA analysis

MASVS-CODE-2
├── Описание: Приложение защищено от memory corruption
├── Проверки:
│   ├── Нет buffer overflows в native code
│   ├── Format string vulnerabilities
│   ├── Integer overflows
│   └── Use-after-free
└── Инструменты: ASan, Valgrind

MASVS-CODE-3
├── Описание: Приложение защищено от reverse engineering
├── Опционально: зависит от risk profile
├── Механизмы:
│   ├── Obfuscation
│   ├── String encryption
│   └── Native code protection
└── Связь: MASVS-RESILIENCE

MASVS-CODE-4
├── Описание: Free security features платформы включены
├── Android:
│   ├── targetSdkVersion актуален
│   ├── Network Security Config
│   └── StrictMode в debug
└── iOS: ATS enabled, PIE, stack canaries
```

### MASVS-RESILIENCE: Защита от реверс-инжиниринга

```
MASVS-RESILIENCE Controls:

MASVS-RESILIENCE-1
├── Описание: Приложение обнаруживает и реагирует на tampering
├── Проверки:
│   ├── Signature verification
│   ├── Integrity checks
│   ├── Installer verification
│   └── Debugger detection
└── Реакция: Graceful degradation или блокировка

MASVS-RESILIENCE-2
├── Описание: Приложение защищено от dynamic analysis
├── Проверки:
│   ├── Debugger detection
│   ├── Frida detection
│   ├── Xposed/Substrate detection
│   └── Emulator detection
└── Цель: Повысить стоимость атаки

MASVS-RESILIENCE-3
├── Описание: Приложение затрудняет static analysis
├── Механизмы:
│   ├── Code obfuscation
│   ├── String encryption
│   ├── Control flow obfuscation
│   └── Symbol stripping
└── Инструменты: ProGuard, R8, DexGuard, iXGuard

MASVS-RESILIENCE-4
├── Описание: Приложение обнаруживает скомпрометированное окружение
├── Проверки:
│   ├── Root/Jailbreak detection
│   ├── Bypassed biometrics
│   ├── Hooked functions
│   └── Modified system
└── Важно: Не единственная линия защиты!
```

**Пример: Multi-layer integrity checking:**

```kotlin
// Android: Integrity verification
// MASVS-RESILIENCE-1 compliant

class IntegrityChecker(private val context: Context) {

    sealed class IntegrityResult {
        object Valid : IntegrityResult()
        data class Invalid(val reason: String) : IntegrityResult()
    }

    fun checkIntegrity(): IntegrityResult {
        // 1. Проверка подписи APK
        val signatureResult = verifySignature()
        if (signatureResult is IntegrityResult.Invalid) return signatureResult

        // 2. Проверка источника установки
        val installerResult = verifyInstaller()
        if (installerResult is IntegrityResult.Invalid) return installerResult

        // 3. Проверка debuggable flag
        val debugResult = checkDebuggable()
        if (debugResult is IntegrityResult.Invalid) return debugResult

        return IntegrityResult.Valid
    }

    private fun verifySignature(): IntegrityResult {
        return try {
            val packageInfo = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                context.packageManager.getPackageInfo(
                    context.packageName,
                    PackageManager.GET_SIGNING_CERTIFICATES
                )
            } else {
                @Suppress("DEPRECATION")
                context.packageManager.getPackageInfo(
                    context.packageName,
                    PackageManager.GET_SIGNATURES
                )
            }

            val signatures = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                packageInfo.signingInfo.apkContentsSigners
            } else {
                @Suppress("DEPRECATION")
                packageInfo.signatures
            }

            val currentSignature = signatures.firstOrNull()
                ?.toByteArray()
                ?.let { MessageDigest.getInstance("SHA-256").digest(it) }
                ?.let { Base64.encodeToString(it, Base64.NO_WRAP) }

            // Сравнение с ожидаемой подписью (хранить безопасно!)
            val expectedSignature = getExpectedSignature()

            if (currentSignature == expectedSignature) {
                IntegrityResult.Valid
            } else {
                IntegrityResult.Invalid("Signature mismatch")
            }
        } catch (e: Exception) {
            IntegrityResult.Invalid("Signature verification failed: ${e.message}")
        }
    }

    private fun verifyInstaller(): IntegrityResult {
        val installer = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            context.packageManager.getInstallSourceInfo(context.packageName).installingPackageName
        } else {
            @Suppress("DEPRECATION")
            context.packageManager.getInstallerPackageName(context.packageName)
        }

        val allowedInstallers = listOf(
            "com.android.vending",        // Google Play
            "com.amazon.venezia",          // Amazon Appstore
            "com.huawei.appmarket"         // Huawei AppGallery
        )

        return if (installer in allowedInstallers) {
            IntegrityResult.Valid
        } else {
            IntegrityResult.Invalid("Unknown installer: $installer")
        }
    }

    private fun checkDebuggable(): IntegrityResult {
        val isDebuggable = (context.applicationInfo.flags and
            ApplicationInfo.FLAG_DEBUGGABLE) != 0

        return if (!isDebuggable) {
            IntegrityResult.Valid
        } else {
            IntegrityResult.Invalid("App is debuggable")
        }
    }

    private fun getExpectedSignature(): String {
        // В реальности получать из secure storage или native code
        return BuildConfig.EXPECTED_SIGNATURE
    }
}
```

### MASVS-PRIVACY: Приватность

```
MASVS-PRIVACY Controls (NEW in MASVS 2.0):

MASVS-PRIVACY-1
├── Описание: Приложение информирует о сборе данных
├── Требования:
│   ├── Privacy policy доступна
│   ├── Data collection disclosure
│   ├── Purpose specification
│   └── User consent механизмы
└── Регуляции: GDPR Article 13, CCPA

MASVS-PRIVACY-2
├── Описание: Приложение позволяет управлять данными
├── Требования:
│   ├── Data export (right to access)
│   ├── Data deletion (right to erasure)
│   ├── Consent withdrawal
│   └── Preference management
└── GDPR: Articles 15, 17, 7(3)

MASVS-PRIVACY-3
├── Описание: Приложение минимизирует использование PII
├── Принципы:
│   ├── Data minimization
│   ├── Purpose limitation
│   ├── Storage limitation
│   └── Pseudonymization где возможно
└── Privacy by Design

MASVS-PRIVACY-4
├── Описание: Приложение использует privacy-preserving идентификаторы
├── Требования:
│   ├── Нет hardware identifiers (IMEI, MAC)
│   ├── Advertising ID с consent
│   ├── Resettable identifiers
│   └── Scoped identifiers
└── Android: Scoped Storage, advertising ID guidelines
```

---

## MAS Testing Profiles

### Переход от L1/L2 к профилям

MASVS 2.0 отказался от уровней L1/L2 в пользу MAS Testing Profiles:

```
MASVS 1.x (устарело):
├── L1: Standard Security
├── L2: Defense-in-Depth
└── R: Reverse Engineering Resilience

MASVS 2.0 MAS Profiles:
├── L1 Profile: Basic Security Testing
├── L2 Profile: In-Depth Security Testing
├── R Profile: Resilience Testing
└── P Profile: Privacy Testing (NEW)
```

### Описание профилей

```
MAS-L1: Basic Security Testing
├── Цель: Минимальный уровень безопасности
├── Для: Все мобильные приложения
├── Покрытие:
│   ├── MASVS-STORAGE (базовые проверки)
│   ├── MASVS-CRYPTO (современные алгоритмы)
│   ├── MASVS-AUTH (базовая аутентификация)
│   ├── MASVS-NETWORK (TLS, no cleartext)
│   ├── MASVS-PLATFORM (базовые IPC проверки)
│   └── MASVS-CODE (release конфигурация)
└── Методы: Automated scanning + manual review

MAS-L2: In-Depth Security Testing
├── Цель: Глубокая проверка безопасности
├── Для: High-risk приложения (финансы, здоровье, PII)
├── Покрытие:
│   ├── Все L1 проверки
│   ├── Динамический анализ
│   ├── Runtime manipulation testing
│   ├── Advanced authentication testing
│   └── Full code review
└── Методы: Manual penetration testing, source code review

MAS-R: Resilience Testing
├── Цель: Защита от реверс-инжиниринга
├── Для: Приложения с IP, DRM, anti-fraud
├── Покрытие:
│   ├── MASVS-RESILIENCE полностью
│   ├── Anti-debugging bypass attempts
│   ├── Hooking framework testing
│   ├── Obfuscation effectiveness
│   └── Runtime protection bypass
└── Методы: Reverse engineering, dynamic instrumentation

MAS-P: Privacy Testing
├── Цель: Проверка приватности
├── Для: Приложения с PII, регулируемые данные
├── Покрытие:
│   ├── MASVS-PRIVACY полностью
│   ├── Data flow analysis
│   ├── Third-party SDK tracking
│   ├── Consent mechanism testing
│   └── Data retention verification
└── Методы: Traffic analysis, SDK behavior analysis
```

### Выбор профиля

```
Decision tree для выбора профиля:

                    ┌──────────────────┐
                    │ Mobile App Type? │
                    └────────┬─────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Consumer │      │ Business │      │ Critical │
    │   App    │      │   App    │      │   App    │
    └────┬─────┘      └────┬─────┘      └────┬─────┘
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐       ┌─────────┐      ┌─────────┐
    │   L1    │       │  L1+L2  │      │L1+L2+R  │
    │  + P?   │       │   + P   │      │   + P   │
    └─────────┘       └─────────┘      └─────────┘

Когда добавлять профили:

+P (Privacy):
├── Собираете PII
├── Подпадаете под GDPR/CCPA
├── Используете analytics/tracking
└── Обрабатываете health/financial данные

+R (Resilience):
├── Финансовые транзакции
├── DRM/лицензирование
├── Anti-fraud критичен
├── Интеллектуальная собственность в коде
└── Игры с in-app purchases
```

---

## MASTG: Mobile Application Security Testing Guide

### Структура руководства

MASTG организован для практического тестирования:

```
MASTG Structure:
│
├── General Testing Guide
│   ├── Mobile App Taxonomy
│   ├── Mobile App Security Testing
│   └── Mobile App Authentication Architectures
│
├── Android Testing Guide
│   ├── Platform Overview
│   ├── Setting up the Testing Environment
│   ├── Data Storage Testing
│   ├── Cryptography Testing
│   ├── Authentication Testing
│   ├── Network Testing
│   ├── Platform Interaction Testing
│   ├── Code Quality Testing
│   ├── Resilience Testing
│   └── Privacy Testing
│
├── iOS Testing Guide
│   ├── Platform Overview
│   ├── Setting up the Testing Environment
│   ├── [Same categories as Android]
│   └── ...
│
└── Tools
    ├── Testing Tools (Frida, Objection, etc.)
    ├── Environment Setup
    └── Automation Scripts
```

### Тест-кейсы MASTG

Каждый MASVS control мапится на конкретные тест-кейсы:

```
Пример маппинга MASVS → MASTG:

MASVS-STORAGE-1 (Secure storage)
├── MASTG-TEST-0001: Testing Local Storage for Sensitive Data
├── MASTG-TEST-0002: Testing SQLite Databases
├── MASTG-TEST-0003: Testing Firebase Databases
├── MASTG-TEST-0004: Testing Realm Databases
└── MASTG-TEST-0005: Testing the Device-Access-Security Policy

MASVS-CRYPTO-1 (Modern cryptography)
├── MASTG-TEST-0013: Testing the Configuration of Crypto Algorithms
├── MASTG-TEST-0014: Testing Key Generation
├── MASTG-TEST-0015: Testing Random Number Generation
└── MASTG-TEST-0016: Testing Key Management

MASVS-NETWORK-2 (TLS best practices)
├── MASTG-TEST-0019: Testing Endpoint Identification
├── MASTG-TEST-0020: Testing Custom Certificate Stores
├── MASTG-TEST-0021: Testing Certificate Pinning
└── MASTG-TEST-0022: Testing the Security Provider
```

### Практическое тестирование

**Среда тестирования:**

```
Android Testing Environment:
│
├── Physical Device (рекомендуется)
│   ├── Rooted для полного доступа
│   ├── Magisk для modern root
│   └── ADB debugging enabled
│
├── Emulator (для базового тестирования)
│   ├── Android Studio AVD
│   ├── Genymotion
│   └── Ограничения: TEE, biometrics, некоторые API
│
├── Инструменты
│   ├── Frida (dynamic instrumentation)
│   ├── Objection (Frida wrapper)
│   ├── Jadx (decompilation)
│   ├── APKTool (APK manipulation)
│   ├── MobSF (automated analysis)
│   ├── Burp Suite (traffic interception)
│   └── adb, logcat
│
└── Тестовое приложение
    ├── Debug build (для разработки)
    └── Release build (для финального теста)
```

```
iOS Testing Environment:
│
├── Physical Device (обязательно для полного теста)
│   ├── Jailbroken для runtime анализа
│   ├── checkra1n/unc0ver/Dopamine
│   └── Developer certificate для sideloading
│
├── Simulator (ограниченно)
│   ├── Xcode Simulator
│   ├── Нет Keychain с Secure Enclave
│   └── Нет биометрии
│
├── Инструменты
│   ├── Frida
│   ├── Objection
│   ├── Hopper/IDA (disassembly)
│   ├── class-dump
│   ├── MobSF
│   └── Burp Suite/mitmproxy
│
└── Тестовое приложение
    ├── IPA с правильным provisioning
    └── Development/Ad Hoc/Enterprise
```

**Пример: Тестирование хранения данных (MASTG-TEST-0001):**

```bash
# Android: Проверка локального хранилища

# 1. Получить доступ к данным приложения
adb shell
run-as com.example.app
cd /data/data/com.example.app

# 2. Проверить SharedPreferences
cat shared_prefs/*.xml
# Ищем: токены, пароли, PII в открытом виде

# 3. Проверить SQLite базы
sqlite3 databases/app.db
.tables
SELECT * FROM users;
# Ищем: незашифрованные sensitive данные

# 4. Проверить файлы
ls -la files/
cat files/*.json
# Ищем: credentials, tokens

# 5. Проверить external storage (если используется)
ls -la /sdcard/Android/data/com.example.app/
# External storage доступен всем приложениям!
```

```python
# Автоматизация с Frida
# Перехват операций записи в SharedPreferences

import frida

script_code = """
Java.perform(function() {
    var SharedPreferencesEditor = Java.use('android.content.SharedPreferences$Editor');

    SharedPreferencesEditor.putString.implementation = function(key, value) {
        console.log('[SharedPrefs] PUT: ' + key + ' = ' + value);

        // Проверяем на sensitive данные
        var sensitivePatterns = ['password', 'token', 'secret', 'key', 'auth'];
        sensitivePatterns.forEach(function(pattern) {
            if (key.toLowerCase().includes(pattern)) {
                console.log('[!] SENSITIVE DATA DETECTED: ' + key);
            }
        });

        return this.putString(key, value);
    };
});
"""

device = frida.get_usb_device()
pid = device.spawn(['com.example.app'])
session = device.attach(pid)
script = session.create_script(script_code)
script.load()
device.resume(pid)
input() # Ждём взаимодействия с приложением
```

**Пример: Тестирование сертификат пиннинга (MASTG-TEST-0021):**

```python
# Frida script для bypass certificate pinning
# Используется для ТЕСТИРОВАНИЯ, не для атаки!

bypass_script = """
Java.perform(function() {
    console.log('[*] Certificate Pinning Bypass loaded');

    // OkHttp CertificatePinner bypass
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List')
            .implementation = function(hostname, peerCertificates) {
                console.log('[*] OkHttp pinning bypassed for: ' + hostname);
                return;
            };
    } catch(e) {
        console.log('[-] OkHttp not found');
    }

    // TrustManager bypass
    try {
        var TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');

        var TrustAllCerts = Java.registerClass({
            name: 'com.test.TrustAllCerts',
            implements: [TrustManager],
            methods: {
                checkClientTrusted: function(chain, authType) {},
                checkServerTrusted: function(chain, authType) {},
                getAcceptedIssuers: function() { return []; }
            }
        });

        console.log('[*] TrustManager bypass ready');
    } catch(e) {
        console.log('[-] TrustManager bypass failed: ' + e);
    }

    // Network Security Config bypass (Android 7+)
    try {
        var NetworkSecurityConfig = Java.use(
            'android.security.net.config.NetworkSecurityConfig'
        );
        // Implementation varies by Android version
    } catch(e) {}
});
"""
```

---

## Инструменты тестирования

### Frida

Frida — основной инструмент для динамического анализа мобильных приложений:

```
Frida Overview:
│
├── Что такое
│   ├── Dynamic instrumentation framework
│   ├── Inject JavaScript в running process
│   └── Cross-platform (Android, iOS, Windows, macOS, Linux)
│
├── Возможности
│   ├── Hook functions
│   ├── Modify return values
│   ├── Trace method calls
│   ├── Access memory
│   └── Bypass security controls
│
└── Компоненты
    ├── frida-server (на устройстве)
    ├── frida-tools (CLI утилиты)
    └── frida Python bindings
```

**Установка и базовое использование:**

```bash
# Установка Frida
pip install frida-tools

# Загрузка frida-server на Android
# Скачать с https://github.com/frida/frida/releases
adb push frida-server-16.x.x-android-arm64 /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# Проверка подключения
frida-ps -U  # Список процессов на USB устройстве

# Подключение к приложению
frida -U -f com.example.app  # Spawn и attach
frida -U com.example.app      # Attach к running процессу
```

**Полезные Frida скрипты:**

```javascript
// Перечисление загруженных классов
Java.perform(function() {
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            if (className.includes('crypto') ||
                className.includes('Crypto') ||
                className.includes('encrypt')) {
                console.log('[Class] ' + className);
            }
        },
        onComplete: function() {
            console.log('[*] Class enumeration complete');
        }
    });
});

// Трассировка вызовов методов
Java.perform(function() {
    var Activity = Java.use('android.app.Activity');

    Activity.onCreate.implementation = function(bundle) {
        console.log('[*] Activity.onCreate called');
        console.log('    Class: ' + this.getClass().getName());
        this.onCreate(bundle);
    };
});

// Дамп аргументов и return value
Java.perform(function() {
    var EncryptedSharedPreferences = Java.use(
        'androidx.security.crypto.EncryptedSharedPreferences'
    );

    EncryptedSharedPreferences.create.overload(
        'java.lang.String',
        'androidx.security.crypto.MasterKey',
        'android.content.Context',
        'androidx.security.crypto.EncryptedSharedPreferences$PrefKeyEncryptionScheme',
        'androidx.security.crypto.EncryptedSharedPreferences$PrefValueEncryptionScheme'
    ).implementation = function(name, masterKey, context, keyScheme, valueScheme) {
        console.log('[*] EncryptedSharedPreferences.create()');
        console.log('    Name: ' + name);
        console.log('    KeyScheme: ' + keyScheme);
        console.log('    ValueScheme: ' + valueScheme);
        return this.create(name, masterKey, context, keyScheme, valueScheme);
    };
});
```

### Objection

Objection — высокоуровневая обёртка над Frida:

```bash
# Установка
pip install objection

# Подключение к приложению
objection -g com.example.app explore

# Полезные команды

# Информация об окружении
objection> env

# Disable SSL pinning
objection> android sslpinning disable

# Root detection bypass
objection> android root disable

# Список activities
objection> android hooking list activities

# Список классов
objection> android hooking list classes

# Методы класса
objection> android hooking list class_methods com.example.app.MainActivity

# Hook метод
objection> android hooking watch class_method com.example.app.Auth.login --dump-args --dump-return

# Keystore
objection> android keystore list

# Memory dump
objection> memory dump all keystore.bin

# SQLite browser
objection> sqlite connect /data/data/com.example.app/databases/app.db
objection> sqlite execute "SELECT * FROM users"
```

### MobSF (Mobile Security Framework)

Автоматизированный анализ мобильных приложений:

```bash
# Docker установка (рекомендуется)
docker pull opensecurity/mobile-security-framework-mobsf
docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf

# Открыть http://localhost:8000

# Возможности:
# - Static Analysis (APK/IPA)
# - Dynamic Analysis (требует эмулятор/устройство)
# - API security testing
# - Malware analysis
# - Automatic report generation
```

```
MobSF Analysis Coverage:

Static Analysis:
├── Manifest Analysis
│   ├── Permissions
│   ├── Exported components
│   ├── Debuggable flag
│   └── Backup settings
│
├── Code Analysis
│   ├── Hardcoded secrets
│   ├── Insecure API usage
│   ├── Weak crypto
│   └── SQL injection
│
├── Binary Analysis
│   ├── PIE/Stack Canary/ARC
│   ├── Symbol stripping
│   └── Code signing
│
└── Third-party Libraries
    ├── Known vulnerabilities
    ├── Outdated versions
    └── Tracker detection

Dynamic Analysis:
├── Network traffic capture
├── API monitoring
├── File system changes
├── Logs analysis
└── Runtime tests
```

### Jadx

Декомпилятор для Android APK:

```bash
# Установка
# macOS
brew install jadx

# Использование
jadx -d output_dir application.apk

# GUI версия
jadx-gui application.apk

# Полезные опции
jadx --show-bad-code  # Показать проблемный код
jadx --deobf          # Деобфускация
jadx --deobf-min 3    # Минимальная длина имён
```

```
Что искать в декомпилированном коде:

Security Issues:
├── Hardcoded credentials
│   └── grep -r "password\|secret\|api_key" src/
│
├── Insecure HTTP
│   └── grep -r "http://" src/
│
├── Weak crypto
│   └── grep -r "DES\|MD5\|SHA1\|ECB" src/
│
├── SQL injection
│   └── grep -r "rawQuery\|execSQL" src/
│
├── WebView issues
│   └── grep -r "setJavaScriptEnabled\|addJavascriptInterface" src/
│
└── Logging
    └── grep -r "Log\.\|println" src/
```

---

## Чеклисты тестирования

### MASVS-STORAGE Checklist

```
□ MASVS-STORAGE-1: Sensitive data in secure storage
  ├── □ Android: EncryptedSharedPreferences/Keystore
  ├── □ iOS: Keychain Services
  ├── □ No plaintext in SharedPreferences/NSUserDefaults
  └── □ Databases encrypted (SQLCipher, Realm encryption)

□ MASVS-STORAGE-2: No sensitive data in logs
  ├── □ Logcat не содержит PII
  ├── □ Console.app чист
  └── □ Crash reports sanitized

□ MASVS-STORAGE-3: No sensitive data to third parties
  ├── □ Analytics SDK не получает PII
  ├── □ Crash reporting sanitized
  └── □ Third-party SDKs reviewed

□ MASVS-STORAGE-4: No sensitive data in keyboard cache
  ├── □ android:inputType="textNoSuggestions"
  ├── □ textContentType="oneTimeCode" (iOS)
  └── □ Password fields configured correctly

□ MASVS-STORAGE-5: No sensitive data in clipboard
  ├── □ Копирование отключено для паролей
  ├── □ Clipboard очищается
  └── □ android:longClickable="false" для sensitive fields

□ MASVS-STORAGE-6: No sensitive data in backups
  ├── □ android:allowBackup="false" или
  ├── □ android:fullBackupContent с exclusions
  └── □ iOS: Files с correct protection class

□ MASVS-STORAGE-7: No sensitive data in background snapshots
  ├── □ FLAG_SECURE для sensitive screens
  ├── □ iOS: blur/cover in applicationWillResignActive
  └── □ Тест: проверка recent apps preview

□ MASVS-STORAGE-8: No sensitive data in system logs
  ├── □ adb logcat проверен
  ├── □ System logs чисты
  └── □ Debug logging отключен в release

□ MASVS-STORAGE-9: Sensitive data cleared on logout
  ├── □ Keystore/Keychain очищен
  ├── □ Databases deleted/cleared
  ├── □ Caches cleared
  └── □ Memory wiped (где возможно)

□ MASVS-STORAGE-10: No sensitive data in WebView caches
  ├── □ WebView cache cleared
  ├── □ Cookies cleared
  └── □ localStorage/IndexedDB cleared

□ MASVS-STORAGE-11: PII retention minimized
  └── □ Data retention policies implemented

□ MASVS-STORAGE-12: PII minimization in permission requests
  └── □ Only necessary permissions requested
```

### MASVS-NETWORK Checklist

```
□ MASVS-NETWORK-1: TLS for all connections
  ├── □ No cleartext traffic
  ├── □ android:usesCleartextTraffic="false"
  ├── □ ATS enabled (iOS)
  └── □ TLS 1.2+ only

□ MASVS-NETWORK-2: TLS best practices
  ├── □ Certificate pinning implemented
  ├── □ Pin backup certificates included
  ├── □ No trust-all TrustManager
  └── □ No user CA trust in production

□ MASVS-NETWORK-3: Certificate validation correct
  ├── □ Chain of trust verified
  ├── □ Hostname verification enabled
  ├── □ No SSL errors ignored
  └── □ Expiration checked

Test Commands:
├── # Traffic interception test
│   mitmproxy / Burp Suite
│
├── # Certificate pinning test
│   objection> android sslpinning disable
│   # Если трафик перехватывается после bypass → pinning работал
│
└── # Cleartext test
    adb shell "dumpsys connectivity | grep -i cleartext"
```

### MASVS-RESILIENCE Checklist

```
□ MASVS-RESILIENCE-1: Tampering detection
  ├── □ Signature verification
  ├── □ Installer verification
  ├── □ File integrity checks
  └── □ Appropriate response to tampering

□ MASVS-RESILIENCE-2: Anti-debugging
  ├── □ Debugger detection
  ├── □ Frida detection
  ├── □ Xposed/Substrate detection
  └── □ Emulator detection

□ MASVS-RESILIENCE-3: Static analysis protection
  ├── □ Code obfuscation (ProGuard/R8/DexGuard)
  ├── □ String encryption
  ├── □ Control flow obfuscation
  └── □ Native code protection

□ MASVS-RESILIENCE-4: Environment detection
  ├── □ Root/Jailbreak detection
  ├── □ Hook detection
  ├── □ System modification detection
  └── □ Graceful degradation

Bypass Tests (для проверки эффективности):
├── # Root bypass
│   Magisk Hide / Shamiko
│
├── # Frida detection bypass
│   frida-server rename
│   Gadget injection
│
├── # Debugger detection bypass
│   ptrace tricks
│
└── # Signature bypass
    APK resign and install
```

---

## Интеграция в SDLC

### Security в CI/CD

```yaml
# GitHub Actions: Mobile Security Pipeline

name: Mobile Security Checks

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build APK
        run: ./gradlew assembleDebug

      - name: MobSF Static Analysis
        run: |
          docker run -d -p 8000:8000 opensecurity/mobile-security-framework-mobsf
          sleep 30
          # Upload APK for analysis
          curl -F 'file=@app/build/outputs/apk/debug/app-debug.apk' \
               http://localhost:8000/api/v1/upload \
               -H "Authorization: ${{ secrets.MOBSF_API_KEY }}"

      - name: Check for hardcoded secrets
        run: |
          pip install trufflehog
          trufflehog filesystem . --only-verified

      - name: Dependency vulnerability scan
        run: ./gradlew dependencyCheckAnalyze

  lint-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Android Lint Security Checks
        run: ./gradlew lint

      - name: Check lint results for security issues
        run: |
          if grep -q "Security" app/build/reports/lint-results.xml; then
            echo "Security issues found!"
            exit 1
          fi

  masvs-compliance:
    runs-on: ubuntu-latest
    needs: [static-analysis]
    steps:
      - name: Generate MASVS Compliance Report
        run: |
          # Генерация отчёта соответствия MASVS
          python scripts/masvs_compliance_check.py \
            --mobsf-report mobsf_report.json \
            --output masvs_compliance.md

      - name: Upload Compliance Report
        uses: actions/upload-artifact@v4
        with:
          name: masvs-compliance-report
          path: masvs_compliance.md
```

### Автоматизация проверок

```python
#!/usr/bin/env python3
"""
MASVS Compliance Checker
Автоматическая проверка соответствия MASVS на основе MobSF отчёта
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

class ComplianceStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    MANUAL = "manual_review_required"
    NA = "not_applicable"

@dataclass
class MASVSCheck:
    id: str
    description: str
    status: ComplianceStatus
    evidence: str
    remediation: str = ""

class MASVSComplianceChecker:
    def __init__(self, mobsf_report: Dict):
        self.report = mobsf_report
        self.results: List[MASVSCheck] = []

    def check_storage_1(self) -> MASVSCheck:
        """MASVS-STORAGE-1: Secure storage for sensitive data"""

        issues = []

        # Проверка SharedPreferences
        if "shared_preferences" in self.report.get("code_analysis", {}):
            prefs = self.report["code_analysis"]["shared_preferences"]
            for pref in prefs:
                if not pref.get("encrypted", False):
                    issues.append(f"Unencrypted SharedPreferences: {pref['file']}")

        # Проверка SQLite
        if "sqlite" in self.report.get("code_analysis", {}):
            for db in self.report["code_analysis"]["sqlite"]:
                if not db.get("encrypted", False):
                    issues.append(f"Unencrypted database: {db['name']}")

        if issues:
            return MASVSCheck(
                id="MASVS-STORAGE-1",
                description="App securely stores sensitive data",
                status=ComplianceStatus.FAIL,
                evidence="\n".join(issues),
                remediation="Use EncryptedSharedPreferences or SQLCipher"
            )

        return MASVSCheck(
            id="MASVS-STORAGE-1",
            description="App securely stores sensitive data",
            status=ComplianceStatus.PASS,
            evidence="No unencrypted sensitive storage detected"
        )

    def check_crypto_1(self) -> MASVSCheck:
        """MASVS-CRYPTO-1: Modern cryptography"""

        weak_crypto = []

        crypto_findings = self.report.get("code_analysis", {}).get("crypto", [])

        weak_algorithms = ["DES", "3DES", "RC4", "MD5", "SHA1", "ECB"]

        for finding in crypto_findings:
            algorithm = finding.get("algorithm", "")
            if any(weak in algorithm.upper() for weak in weak_algorithms):
                weak_crypto.append(f"{algorithm} at {finding.get('location', 'unknown')}")

        if weak_crypto:
            return MASVSCheck(
                id="MASVS-CRYPTO-1",
                description="App uses modern cryptography",
                status=ComplianceStatus.FAIL,
                evidence="\n".join(weak_crypto),
                remediation="Replace with AES-256-GCM, SHA-256+, RSA-2048+"
            )

        return MASVSCheck(
            id="MASVS-CRYPTO-1",
            description="App uses modern cryptography",
            status=ComplianceStatus.PASS,
            evidence="No weak cryptographic algorithms detected"
        )

    def check_network_1(self) -> MASVSCheck:
        """MASVS-NETWORK-1: TLS for all connections"""

        issues = []

        # Проверка Network Security Config
        nsc = self.report.get("manifest_analysis", {}).get("network_security_config", {})

        if nsc.get("cleartext_permitted", False):
            issues.append("Cleartext traffic permitted in Network Security Config")

        # Проверка hardcoded HTTP URLs
        urls = self.report.get("urls", [])
        http_urls = [url for url in urls if url.startswith("http://")]

        if http_urls:
            issues.append(f"HTTP URLs found: {len(http_urls)}")

        if issues:
            return MASVSCheck(
                id="MASVS-NETWORK-1",
                description="App uses TLS for all connections",
                status=ComplianceStatus.FAIL,
                evidence="\n".join(issues),
                remediation="Enable Network Security Config, use HTTPS only"
            )

        return MASVSCheck(
            id="MASVS-NETWORK-1",
            description="App uses TLS for all connections",
            status=ComplianceStatus.PASS,
            evidence="All connections use TLS"
        )

    def check_code_1(self) -> MASVSCheck:
        """MASVS-CODE-1: App is signed and built correctly"""

        issues = []

        # Проверка debuggable
        if self.report.get("manifest_analysis", {}).get("debuggable", False):
            issues.append("Application is debuggable")

        # Проверка подписи
        signing = self.report.get("apk_info", {}).get("signing", {})
        if signing.get("v1_signing", False) and not signing.get("v2_signing", False):
            issues.append("Only v1 signing (consider v2/v3)")

        if issues:
            return MASVSCheck(
                id="MASVS-CODE-1",
                description="App is signed and built correctly",
                status=ComplianceStatus.FAIL,
                evidence="\n".join(issues),
                remediation="Set debuggable=false, use v2/v3 signing"
            )

        return MASVSCheck(
            id="MASVS-CODE-1",
            description="App is signed and built correctly",
            status=ComplianceStatus.PASS,
            evidence="Release configuration correct"
        )

    def run_all_checks(self) -> List[MASVSCheck]:
        """Run all automated MASVS checks"""

        self.results = [
            self.check_storage_1(),
            self.check_crypto_1(),
            self.check_network_1(),
            self.check_code_1(),
            # Добавить остальные проверки...
        ]

        return self.results

    def generate_report(self) -> str:
        """Generate markdown compliance report"""

        report = "# MASVS Compliance Report\n\n"

        passed = sum(1 for r in self.results if r.status == ComplianceStatus.PASS)
        failed = sum(1 for r in self.results if r.status == ComplianceStatus.FAIL)
        manual = sum(1 for r in self.results if r.status == ComplianceStatus.MANUAL)

        report += f"## Summary\n\n"
        report += f"- ✅ Passed: {passed}\n"
        report += f"- ❌ Failed: {failed}\n"
        report += f"- 🔍 Manual Review: {manual}\n\n"

        report += "## Detailed Results\n\n"

        for check in self.results:
            status_emoji = {
                ComplianceStatus.PASS: "✅",
                ComplianceStatus.FAIL: "❌",
                ComplianceStatus.MANUAL: "🔍",
                ComplianceStatus.NA: "➖"
            }[check.status]

            report += f"### {status_emoji} {check.id}\n\n"
            report += f"**Description:** {check.description}\n\n"
            report += f"**Status:** {check.status.value}\n\n"
            report += f"**Evidence:**\n```\n{check.evidence}\n```\n\n"

            if check.remediation:
                report += f"**Remediation:** {check.remediation}\n\n"

            report += "---\n\n"

        return report


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], 'r') as f:
        mobsf_report = json.load(f)

    checker = MASVSComplianceChecker(mobsf_report)
    checker.run_all_checks()

    report = checker.generate_report()
    print(report)
```

---

## Распространённые мифы и заблуждения

### Миф 1: "MASVS — это только для аудиторов"

```
Реальность:

MASVS полезен для ВСЕХ участников:

Разработчики
├── Security requirements до написания кода
├── Secure coding guidelines
└── Self-assessment перед аудитом

Архитекторы
├── Security architecture decisions
├── Threat modeling input
└── Technology selection criteria

Product Managers
├── Security features prioritization
├── Compliance requirements понимание
└── Risk-based decisions

QA/Testing
├── Security test cases
├── Acceptance criteria
└── Regression testing scope
```

### Миф 2: "L1 достаточно для обычных приложений"

```
Реальность:

L1 — это МИНИМУМ, не "достаточно":

❌ "L1 для обычных, L2 для банков"
   └── Даже "обычные" приложения хранят:
       ├── Email, пароли, токены
       ├── Персональные данные
       ├── Платёжную информацию
       └── Приватный контент

✓ Правильный подход:
   └── Risk assessment определяет профиль
       ├── Какие данные обрабатываете?
       ├── Какие угрозы актуальны?
       ├── Какие регуляции применимы?
       └── Какой ущерб от компрометации?

Пример:
├── Dating app с фото → L2 + P (privacy критичен)
├── Health tracker → L2 + P (medical data)
├── Simple game → L1 (если нет purchases/accounts)
└── Banking app → L2 + R + P (полный профиль)
```

### Миф 3: "Pinning защищает от всех MitM атак"

```
Реальность:

Pinning — это defense in depth, НЕ silver bullet:

Что pinning защищает:
├── Перехват на скомпрометированном Wi-Fi
├── Corporate proxy с custom CA
└── Rogue CA (маловероятно, но возможно)

Что pinning НЕ защищает:
├── Compromised server endpoint
├── Backend vulnerabilities
├── Malware на устройстве
├── Physical access + Frida bypass
└── Compromised development machine

Важно:
├── Pinning МОЖНО обойти на jailbroken/rooted устройстве
├── Attacker с физическим доступом обойдёт
├── Нужны backup pins для rotation
└── Pinning failures нужно правильно обрабатывать

Рекомендация:
└── Pinning как один слой defense in depth
    ├── + Strong TLS configuration
    ├── + Mutual TLS где возможно
    ├── + Certificate Transparency monitoring
    └── + Server-side security
```

### Миф 4: "Root/Jailbreak detection надёжно защищает"

```
Реальность:

Root detection — это DETERRENT, не BARRIER:

Любой root detection обходится:
├── Magisk Hide / Shamiko (Android)
├── Various jailbreak detection bypasses (iOS)
├── Frida scripts
└── Custom kernels

Правильное понимание:
├── Root detection → ПОДНИМАЕТ ПЛАНКУ для атакующего
├── Не полагаться как на единственную защиту
├── Defense in depth подход
└── Server-side валидация ОБЯЗАТЕЛЬНА

Паттерн:
┌─────────────────────────────────────────┐
│         Root/Jailbreak detected         │
├─────────────────────────────────────────┤
│ ❌ НЕПРАВИЛЬНО: Показать "rooted" и    │
│    всё равно работать                   │
│                                         │
│ ⚠️ ПРИЕМЛЕМО: Ограничить функционал    │
│    (нет биометрии, нет offline mode)    │
│                                         │
│ ✓ ПРАВИЛЬНО: Server-side проверки      │
│    + Device attestation                 │
│    + Risk-based authentication          │
│    + Anomaly detection                  │
└─────────────────────────────────────────┘
```

### Миф 5: "Obfuscation делает код нечитаемым"

```
Реальность:

Obfuscation ЗАМЕДЛЯЕТ анализ, не ПРЕДОТВРАЩАЕТ:

Что делает obfuscation:
├── Переименовывает классы/методы → a, b, c
├── Убирает debug info
├── Может шифровать strings
└── Может усложнять control flow

Что НЕ делает obfuscation:
├── Не скрывает алгоритмы (они в bytecode)
├── Не защищает ключи (их можно найти runtime)
├── Не предотвращает dynamic analysis
└── Не защищает от Frida/debugging

Реальность:
├── Опытный reverse engineer справится за часы/дни
├── Automated deobfuscators существуют
├── Runtime значения видны через instrumentation
└── Native code сложнее, но тоже анализируется

Рекомендация:
├── Obfuscation — хорошая практика
├── НЕ полагаться только на неё
├── Secrets НЕ хранить в коде
├── Критичную логику — на сервере
└── Layered defense approach
```

### Миф 6: "MASTG тесты нужно делать только раз"

```
Реальность:

Security testing — НЕПРЕРЫВНЫЙ процесс:

Почему одного раза недостаточно:
├── Новые уязвимости в зависимостях
├── Изменения в коде
├── Новые attack vectors
├── Platform updates (новые API, deprecated методы)
└── Изменения в требованиях (GDPR updates, etc.)

Рекомендуемый подход:
├── CI/CD: Автоматические проверки каждый build
├── Release: Full security review
├── Quarterly: Penetration testing (L2+)
├── Annually: Third-party audit
└── Continuous: Dependency monitoring

Integration:
┌─────────────────────────────────────────┐
│              CI/CD Pipeline             │
├─────────────────────────────────────────┤
│ Commit → Static Analysis (MobSF)        │
│        → Dependency Check               │
│        → Lint Security Rules            │
├─────────────────────────────────────────┤
│ Release → Full MASTG Test Suite         │
│         → Manual Penetration Test       │
│         → Compliance Check              │
└─────────────────────────────────────────┘
```

---

## Практические примеры

### Пример 1: Полный аудит MASVS-STORAGE

```bash
#!/bin/bash
# MASVS-STORAGE Complete Test Script for Android

APP_PACKAGE="com.example.app"
OUTPUT_DIR="./masvs_storage_audit"

mkdir -p $OUTPUT_DIR

echo "=== MASVS-STORAGE Audit for $APP_PACKAGE ==="

# MASVS-STORAGE-1: Check SharedPreferences
echo "[*] Checking SharedPreferences..."
adb shell "run-as $APP_PACKAGE cat shared_prefs/*.xml" > $OUTPUT_DIR/shared_prefs.txt 2>&1

# Check for sensitive patterns
grep -i "password\|token\|key\|secret\|api" $OUTPUT_DIR/shared_prefs.txt > $OUTPUT_DIR/sensitive_prefs.txt

if [ -s $OUTPUT_DIR/sensitive_prefs.txt ]; then
    echo "[!] MASVS-STORAGE-1 FAIL: Sensitive data in SharedPreferences"
    cat $OUTPUT_DIR/sensitive_prefs.txt
else
    echo "[+] MASVS-STORAGE-1 PASS: No obvious sensitive data in SharedPreferences"
fi

# MASVS-STORAGE-2: Check logs
echo "[*] Checking logs for sensitive data..."
adb logcat -d | grep -i "$APP_PACKAGE" > $OUTPUT_DIR/app_logs.txt
grep -i "password\|token\|key\|secret" $OUTPUT_DIR/app_logs.txt > $OUTPUT_DIR/sensitive_logs.txt

if [ -s $OUTPUT_DIR/sensitive_logs.txt ]; then
    echo "[!] MASVS-STORAGE-2 FAIL: Sensitive data in logs"
else
    echo "[+] MASVS-STORAGE-2 PASS: No sensitive data in logs"
fi

# MASVS-STORAGE-6: Check backup configuration
echo "[*] Checking backup configuration..."
adb shell "pm dump $APP_PACKAGE | grep -i backup" > $OUTPUT_DIR/backup_config.txt

if grep -q "allowBackup=true" $OUTPUT_DIR/backup_config.txt; then
    echo "[!] MASVS-STORAGE-6 WARN: Backup enabled - verify exclusions"
else
    echo "[+] MASVS-STORAGE-6 PASS: Backup disabled"
fi

# MASVS-STORAGE-7: Check for FLAG_SECURE
echo "[*] Checking screenshot protection..."
# This requires dynamic testing with Frida

# Generate report
echo "=== Audit Complete ==="
echo "Results saved to $OUTPUT_DIR/"
```

### Пример 2: Frida script для комплексной проверки

```javascript
// comprehensive_masvs_test.js
// Комплексный Frida скрипт для MASVS тестирования

Java.perform(function() {
    console.log('[*] MASVS Comprehensive Test Started');

    // ===== MASVS-STORAGE =====

    // Hook SharedPreferences для мониторинга записи
    var SharedPreferencesEditor = Java.use('android.content.SharedPreferences$Editor');

    SharedPreferencesEditor.putString.implementation = function(key, value) {
        var sensitivePatterns = ['password', 'token', 'secret', 'key', 'auth', 'session'];
        var isSensitive = sensitivePatterns.some(function(p) {
            return key.toLowerCase().includes(p) ||
                   (value && value.toLowerCase().includes(p));
        });

        if (isSensitive) {
            console.log('[MASVS-STORAGE-1] ALERT: Sensitive data written to SharedPreferences');
            console.log('    Key: ' + key);
            console.log('    Value: ' + (value ? value.substring(0, 50) + '...' : 'null'));
            console.log('    Stack: ' + Java.use('android.util.Log').getStackTraceString(
                Java.use('java.lang.Exception').$new()
            ));
        }

        return this.putString(key, value);
    };

    // Hook Log для проверки MASVS-STORAGE-2
    var Log = Java.use('android.util.Log');
    var logMethods = ['d', 'i', 'w', 'e', 'v'];

    logMethods.forEach(function(method) {
        Log[method].overload('java.lang.String', 'java.lang.String').implementation = function(tag, msg) {
            var sensitivePatterns = ['password', 'token', 'secret', 'bearer', 'authorization'];
            var isSensitive = sensitivePatterns.some(function(p) {
                return msg.toLowerCase().includes(p);
            });

            if (isSensitive) {
                console.log('[MASVS-STORAGE-2] ALERT: Sensitive data in logs');
                console.log('    Tag: ' + tag);
                console.log('    Message: ' + msg.substring(0, 100));
            }

            return this[method](tag, msg);
        };
    });

    // ===== MASVS-CRYPTO =====

    // Hook Cipher для проверки алгоритмов
    var Cipher = Java.use('javax.crypto.Cipher');

    Cipher.getInstance.overload('java.lang.String').implementation = function(transformation) {
        console.log('[MASVS-CRYPTO-1] Cipher.getInstance: ' + transformation);

        var weakAlgorithms = ['DES', '3DES', 'RC4', 'RC2', 'Blowfish', 'ECB'];
        var isWeak = weakAlgorithms.some(function(weak) {
            return transformation.toUpperCase().includes(weak);
        });

        if (isWeak) {
            console.log('[MASVS-CRYPTO-1] ALERT: Weak algorithm detected: ' + transformation);
        }

        return this.getInstance(transformation);
    };

    // Hook MessageDigest для проверки хешей
    var MessageDigest = Java.use('java.security.MessageDigest');

    MessageDigest.getInstance.overload('java.lang.String').implementation = function(algorithm) {
        console.log('[MASVS-CRYPTO-1] MessageDigest.getInstance: ' + algorithm);

        if (algorithm.toUpperCase() === 'MD5' || algorithm.toUpperCase() === 'SHA1') {
            console.log('[MASVS-CRYPTO-1] ALERT: Weak hash algorithm: ' + algorithm);
        }

        return this.getInstance(algorithm);
    };

    // Hook SecureRandom для проверки PRNG
    var SecureRandom = Java.use('java.security.SecureRandom');
    var Random = Java.use('java.util.Random');

    Random.$init.overload('long').implementation = function(seed) {
        console.log('[MASVS-CRYPTO-4] ALERT: java.util.Random with seed - potentially predictable');
        console.log('    Seed: ' + seed);
        return this.$init(seed);
    };

    // ===== MASVS-NETWORK =====

    // Hook URL connections
    var URL = Java.use('java.net.URL');

    URL.openConnection.overload().implementation = function() {
        var url = this.toString();
        console.log('[MASVS-NETWORK-1] URL.openConnection: ' + url);

        if (url.startsWith('http://')) {
            console.log('[MASVS-NETWORK-1] ALERT: HTTP connection (cleartext)');
        }

        return this.openConnection();
    };

    // Hook TrustManager для проверки MASVS-NETWORK-3
    try {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');

        TrustManagerImpl.checkServerTrusted.overload(
            '[Ljava.security.cert.X509Certificate;',
            'java.lang.String'
        ).implementation = function(chain, authType) {
            console.log('[MASVS-NETWORK-3] TrustManager.checkServerTrusted called');
            console.log('    Chain length: ' + chain.length);
            console.log('    AuthType: ' + authType);

            // Проверяем, что validation действительно происходит
            try {
                this.checkServerTrusted(chain, authType);
                console.log('[MASVS-NETWORK-3] Certificate validation passed');
            } catch (e) {
                console.log('[MASVS-NETWORK-3] Certificate validation failed: ' + e);
                throw e;
            }
        };
    } catch (e) {
        console.log('[-] TrustManager hook failed: ' + e);
    }

    // ===== MASVS-RESILIENCE =====

    // Detect if app checks for root
    var Runtime = Java.use('java.lang.Runtime');

    Runtime.exec.overload('java.lang.String').implementation = function(cmd) {
        console.log('[MASVS-RESILIENCE-4] Runtime.exec: ' + cmd);

        var rootIndicators = ['su', 'which', 'busybox', 'magisk'];
        var isRootCheck = rootIndicators.some(function(indicator) {
            return cmd.includes(indicator);
        });

        if (isRootCheck) {
            console.log('[MASVS-RESILIENCE-4] Root detection command detected');
        }

        return this.exec(cmd);
    };

    // Hook file existence checks (common root detection)
    var File = Java.use('java.io.File');

    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        var rootPaths = ['/system/app/Superuser.apk', '/sbin/su', '/system/bin/su',
                        '/system/xbin/su', '/data/local/xbin/su', '/data/local/bin/su',
                        '/system/sd/xbin/su', '/system/bin/failsafe/su', '/data/local/su',
                        '/su/bin/su', '/magisk'];

        var isRootPath = rootPaths.some(function(rp) {
            return path.includes(rp);
        });

        if (isRootPath) {
            console.log('[MASVS-RESILIENCE-4] Root file check: ' + path);
        }

        return this.exists();
    };

    console.log('[*] All MASVS hooks installed');
});
```

### Пример 3: iOS тестирование с Objection

```bash
#!/bin/bash
# iOS MASVS Testing Script with Objection

APP_ID="com.example.app"

echo "=== iOS MASVS Audit ==="

# Подключение к приложению
objection -g "$APP_ID" explore << 'EOF'

# MASVS-STORAGE: Keychain dump
ios keychain dump

# MASVS-STORAGE: Plist files
ios plist cat NSUserDefaults

# MASVS-STORAGE: SQLite databases
sqlite connect /var/mobile/Containers/Data/Application/*/Documents/*.db
.tables

# MASVS-NETWORK: SSL Pinning status
ios sslpinning disable

# MASVS-RESILIENCE: Jailbreak detection status
ios jailbreak disable

# MASVS-CODE: Binary info
ios info binary

# MASVS-PLATFORM: URL Schemes
ios bundles list_bundles

# Memory analysis
memory search "password"
memory search "token"
memory search "secret"

exit
EOF

echo "=== Audit Complete ==="
```

---

## Ресурсы и ссылки

### Официальные ресурсы

```
OWASP MAS Project:
├── GitHub: https://github.com/OWASP/owasp-mastg
├── MASVS: https://mas.owasp.org/MASVS/
├── MASTG: https://mas.owasp.org/MASTG/
├── Checklists: https://mas.owasp.org/checklists/
└── MAS Crackmes: https://mas.owasp.org/crackmes/

Инструменты:
├── Frida: https://frida.re/
├── Objection: https://github.com/sensepost/objection
├── MobSF: https://github.com/MobSF/Mobile-Security-Framework-MobSF
├── Jadx: https://github.com/skylot/jadx
├── APKTool: https://ibotpeaches.github.io/Apktool/
└── Ghidra: https://ghidra-sre.org/
```

### Обучающие материалы

```
Курсы и тренинги:
├── OWASP MAS Crackmes (практика)
├── Hacker101 Mobile Hacking
├── PentesterLab Mobile
└── SANS SEC575 (Mobile Security)

Книги:
├── "The Mobile Application Hacker's Handbook"
├── "Android Security Internals"
├── "iOS Application Security"
└── "Hacking and Securing iOS Applications"

Конференции:
├── DEF CON Mobile Hacking Village
├── OWASP Global AppSec
└── Objective by the Sea (iOS)
```

### Связанные материалы в базе знаний

```
Связи:
├── security-fundamentals.md — базовые концепции
├── mobile-security-owasp.md — OWASP Mobile Top 10
├── threat-modeling.md — моделирование угроз
├── android-permissions-security.md — Android permissions
└── mobile-app-protection.md — защита приложений (БУДЕТ СОЗДАН)
```

---

## Резюме

### Ключевые выводы

```
1. MASVS 2.0 — атомарные требования
   └── Один control = один тест = чёткая проверка

2. MAS Testing Profiles заменили L1/L2
   └── L1, L2, R, P — комбинируйте по risk assessment

3. MASTG — практическое руководство
   └── Конкретные тест-кейсы для каждого control

4. Автоматизация необходима
   └── CI/CD интеграция, но manual testing тоже нужен

5. Defense in Depth
   └── Никакая одна мера не достаточна

6. Continuous Security
   └── Не разовый аудит, а процесс
```

### Quick Reference

```
MASVS Categories Quick Check:

STORAGE  → Данные зашифрованы? Нет в логах? Нет в backups?
CRYPTO   → AES-256? SHA-256+? Hardware keys?
AUTH     → Crypto biometrics? Step-up auth? Server validation?
NETWORK  → TLS 1.2+? Pinning? No cleartext?
PLATFORM → WebView secure? IPC protected? Deep links validated?
CODE     → Release build? No debuggable? Obfuscated?
RESILIENCE → Root detection? Anti-debug? Integrity checks?
PRIVACY  → Consent? Data minimization? User control?
```

### Следующие шаги

```
После изучения этого материала:

1. Скачать MASTG и изучить structure
2. Настроить testing environment (Frida, Objection)
3. Пройти OWASP MAS Crackmes
4. Провести self-assessment своего приложения
5. Интегрировать автоматические проверки в CI/CD
6. Запланировать регулярные security reviews
```

---

*Материал создан на основе OWASP MASVS 2.1.0 и MASTG 1.7.x. Актуален на январь 2026.*

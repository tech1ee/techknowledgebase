---
title: "OWASP Mobile Top 10 2024: Угрозы мобильных приложений"
type: concept
status: published
tags:
  - topic/security
  - type/concept
  - level/intermediate
---

# OWASP Mobile Top 10 2024: Угрозы мобильных приложений

---

cs-foundations: [Mobile Security, Authentication, Cryptography, Supply Chain Security, Data Protection]
---

## Зачем это нужно

OWASP Mobile Top 10 2024 — первое крупное обновление списка за 8 лет (с 2016). За это время мобильный ландшафт кардинально изменился: более 90% приложений интегрируют хотя бы один сторонний SDK, атаки на supply chain стали массовыми, а требования к приватности (GDPR, CCPA) — обязательными.

**Проблема:** Разработчики мобильных приложений часто фокусируются на функциональности, игнорируя безопасность. Результат — утечки credentials, MITM-атаки, reverse engineering и компрометация данных миллионов пользователей.

**Решение:** OWASP Mobile Top 10 2024 даёт структурированный подход к защите мобильных приложений, охватывая критичные уязвимости от хранения credentials до binary protection.

```
┌─────────────────────────────────────────────────────────────────┐
│                OWASP MOBILE TOP 10 2024                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   M1   Improper Credential Usage        (Неправильное           │
│                                          использование credentials)
│   M2   Inadequate Supply Chain Security (Небезопасная цепочка   │
│                                          поставок)               │
│   M3   Insecure Authentication/         (Небезопасная           │
│        Authorization                     AuthN/AuthZ)            │
│   M4   Insufficient Input/Output        (Недостаточная          │
│        Validation                        валидация I/O)          │
│   M5   Insecure Communication           (Небезопасная связь)     │
│   M6   Inadequate Privacy Controls      (Недостаточный контроль │
│                                          приватности)            │
│   M7   Insufficient Binary Protections  (Недостаточная защита   │
│                                          бинарников)             │
│   M8   Security Misconfiguration        (Неправильная           │
│                                          конфигурация)           │
│   M9   Insecure Data Storage            (Небезопасное хранение  │
│                                          данных)                 │
│   M10  Insufficient Cryptography        (Недостаточная          │
│                                          криптография)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| Security Fundamentals | CIA Triad, базовые принципы | [[security-fundamentals]] |
| Криптография | Шифрование, хеширование | [[security-cryptography-fundamentals]] |
| Android/iOS разработка | Понимание платформ | [[android-permissions-security]], [[ios-permissions-security]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **PII** | Personally Identifiable Information — данные, идентифицирующие человека | Паспортные данные |
| **MITM** | Man-in-the-Middle — атака с перехватом коммуникации | Прослушка телефона |
| **Certificate Pinning** | Привязка сертификата сервера в приложении | Запомнить лицо курьера |
| **SDK** | Software Development Kit — набор инструментов/библиотек | Готовые детали конструктора |
| **Reverse Engineering** | Анализ бинарного кода для понимания логики | Разобрать устройство, чтобы понять, как оно работает |
| **Obfuscation** | Запутывание кода для усложнения анализа | Шифр, понятный только автору |

---

## Что изменилось с 2016 года

```
┌─────────────────────────────────────────────────────────────────┐
│                    2016 → 2024 CHANGES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   НОВЫЕ КАТЕГОРИИ:                                               │
│   • M1: Improper Credential Usage (NEW)                          │
│   • M2: Inadequate Supply Chain Security (NEW)                   │
│   • M6: Inadequate Privacy Controls (NEW)                        │
│                                                                  │
│   ОБЪЕДИНЁННЫЕ КАТЕГОРИИ:                                        │
│   • M4 (2016) + M6 (2016) → M3 (2024): Insecure Auth/Authz       │
│   • M8 (2016) + M9 (2016) → M7 (2024): Insufficient Binary       │
│     Protections (Code Tampering + Reverse Engineering)           │
│                                                                  │
│   ИЗМЕНЕНИЕ ПРИОРИТЕТОВ:                                         │
│   • Insecure Data Storage: M2 (2016) → M9 (2024)                 │
│     (Улучшились платформенные механизмы защиты)                  │
│   • Supply Chain поднялся на M2 (отражает современные атаки)     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## M1: Improper Credential Usage (Неправильное использование credentials)

**Новая категория в 2024.** Отражает критичность защиты секретов в мобильных приложениях.

### Описание

Improper Credential Usage происходит, когда приложение неправильно обрабатывает credentials: хардкодит их в коде, хранит небезопасно или передаёт без шифрования.

### Типичные ошибки

```
┌─────────────────────────────────────────────────────────────────┐
│                    M1: COMMON MISTAKES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. HARDCODED CREDENTIALS                                       │
│      API ключи, токены, пароли прямо в коде                      │
│      → Легко извлекаются через reverse engineering               │
│                                                                  │
│   2. INSECURE STORAGE                                            │
│      Credentials в SharedPreferences (Android) без шифрования    │
│      Credentials в UserDefaults (iOS) без Keychain               │
│      → Доступны на rooted/jailbroken устройствах                 │
│                                                                  │
│   3. INSECURE TRANSMISSION                                       │
│      Передача credentials по HTTP                                │
│      Передача в URL query parameters                             │
│      → Перехватываются через MITM                                │
│                                                                  │
│   4. CREDENTIALS IN LOGS                                         │
│      Логирование паролей, токенов                                │
│      → Видны в logcat, crash reports                             │
│                                                                  │
│   5. CREDENTIAL REUSE                                            │
│      Один API key для всех операций                              │
│      → Компрометация одного ключа даёт доступ ко всему           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Примеры уязвимого кода

```kotlin
// ❌ ПЛОХО: Hardcoded API key
class ApiClient {
    companion object {
        // Легко извлекается из APK через strings или jadx
        private const val API_KEY = "YOUR_API_KEY_HERE"  // Never hardcode!
    }
}

// ❌ ПЛОХО: Credentials в SharedPreferences без шифрования
fun saveCredentials(context: Context, token: String) {
    context.getSharedPreferences("prefs", Context.MODE_PRIVATE)
        .edit()
        .putString("auth_token", token)  // Plaintext!
        .apply()
}

// ❌ ПЛОХО: Credentials в URL
fun fetchUserData(userId: String, token: String) {
    val url = "https://api.example.com/users/$userId?token=$token"
    // token виден в server logs, browser history, analytics
}
```

### Правильная реализация

```kotlin
// ✅ ХОРОШО: Использование EncryptedSharedPreferences (Android)
class SecureCredentialStorage(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "secure_credentials",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveToken(token: String) {
        encryptedPrefs.edit()
            .putString("auth_token", token)
            .apply()
    }

    fun getToken(): String? = encryptedPrefs.getString("auth_token", null)

    fun clearCredentials() {
        encryptedPrefs.edit().clear().apply()
    }
}

// ✅ ХОРОШО: API key из secure backend или build config
class ApiClient(private val credentialProvider: CredentialProvider) {

    fun makeRequest(): Response {
        val apiKey = credentialProvider.getApiKey()  // Из secure storage или backend
        return httpClient.newCall(
            Request.Builder()
                .url("https://api.example.com/data")
                .header("Authorization", "Bearer $apiKey")  // В header, не в URL
                .build()
        ).execute()
    }
}
```

```swift
// ✅ ХОРОШО: Keychain для iOS
import Security

class KeychainManager {

    func saveToken(_ token: String, forKey key: String) throws {
        let data = token.data(using: .utf8)!

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        // Удаляем существующий, если есть
        SecItemDelete(query as CFDictionary)

        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.saveFailed(status)
        }
    }

    func getToken(forKey key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data,
              let token = String(data: data, encoding: .utf8) else {
            return nil
        }

        return token
    }
}
```

### Mitigation Checklist

```
□ Никаких hardcoded credentials в коде
□ API keys хранятся на сервере или в secure storage
□ Используется EncryptedSharedPreferences (Android) / Keychain (iOS)
□ Credentials передаются в headers, не в URL
□ Credentials не логируются
□ Токены имеют ограниченный срок жизни и ротируются
□ Используется MFA для критичных операций
```

---

## M2: Inadequate Supply Chain Security (Небезопасная цепочка поставок)

**Новая категория в 2024.** Отражает рост атак через third-party SDK и библиотеки.

### Описание

Более 90% мобильных приложений используют хотя бы один сторонний SDK. Каждый SDK — потенциальный вектор атаки: устаревшие версии, вредоносный код, избыточные permissions.

### Типичные проблемы

```
┌─────────────────────────────────────────────────────────────────┐
│                M2: SUPPLY CHAIN RISKS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. OUTDATED DEPENDENCIES                                       │
│      Библиотеки с известными CVE                                 │
│      → Атакующий эксплуатирует известную уязвимость              │
│                                                                  │
│   2. MALICIOUS SDK                                               │
│      SDK с backdoor или data exfiltration                        │
│      → Данные пользователей утекают третьим сторонам             │
│                                                                  │
│   3. EXCESSIVE PERMISSIONS                                       │
│      SDK запрашивает больше permissions, чем нужно               │
│      → Расширяет attack surface приложения                       │
│                                                                  │
│   4. UNVETTED COMPONENTS                                         │
│      Использование SDK без security review                       │
│      → Неизвестные риски в production                            │
│                                                                  │
│   5. COMPROMISED CI/CD                                           │
│      Secrets в plaintext, незащищённые pipelines                 │
│      → Injection malicious code при сборке                       │
│                                                                  │
│   6. NO SBOM                                                     │
│      Отсутствие Software Bill of Materials                       │
│      → Невозможно быстро реагировать на новые CVE                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Реальные примеры атак

- **SolarWinds (2020):** Компрометация build pipeline → malicious update для 18,000 организаций
- **Log4Shell (2021):** Уязвимость в популярной библиотеке затронула миллионы приложений
- **Malicious npm packages:** Typosquatting и dependency confusion атаки

### Mitigation Strategies

```kotlin
// build.gradle.kts - Пример настройки dependency verification

dependencyLocking {
    lockAllConfigurations()  // Фиксируем версии зависимостей
}

// Регулярное сканирование на уязвимости
// ./gradlew dependencyCheckAnalyze (OWASP Dependency-Check)
```

```yaml
# GitHub Actions - Security scanning в CI/CD
name: Security Scan

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/gradle@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Generate SBOM
        run: ./gradlew cyclonedxBom

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: build/reports/bom.json
```

### Mitigation Checklist

```
□ Регулярное сканирование зависимостей (Snyk, OWASP Dependency-Check)
□ Dependency locking для фиксации версий
□ Security review для новых SDK
□ Минимизация количества зависимостей
□ SBOM (Software Bill of Materials) для отслеживания компонентов
□ Мониторинг security advisories для используемых библиотек
□ Изоляция критичных SDK за internal API
□ Secure CI/CD с protected secrets
```

---

## M3: Insecure Authentication/Authorization

**Объединение M4 и M6 из 2016.** Подчёркивает, что аутентификация без авторизации недостаточна.

### Описание

Слабая аутентификация позволяет обойти проверку личности. Слабая авторизация позволяет получить доступ к чужим данным или привилегированным функциям.

### Типичные уязвимости

```
┌─────────────────────────────────────────────────────────────────┐
│                M3: AUTH VULNERABILITIES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   AUTHENTICATION ISSUES:                                         │
│   • Слабые пароли без валидации                                  │
│   • Отсутствие MFA для критичных операций                        │
│   • Biometric bypass через fallback                              │
│   • Session не инвалидируется при logout                         │
│   • Несколько пользователей под одним логином                    │
│                                                                  │
│   AUTHORIZATION ISSUES:                                          │
│   • IDOR (Insecure Direct Object Reference)                      │
│     GET /api/users/123 → GET /api/users/124 работает             │
│   • Privilege Escalation                                         │
│     Обычный пользователь получает admin-функции                  │
│   • Missing function-level access control                        │
│     API endpoint без проверки прав                               │
│   • Client-side authorization                                    │
│     Проверка прав только на клиенте, не на сервере               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Пример IDOR уязвимости

```kotlin
// ❌ ПЛОХО: IDOR — нет проверки владельца
@GET("/api/orders/{orderId}")
suspend fun getOrder(@Path("orderId") orderId: String): Order {
    // Любой пользователь может получить любой заказ, зная ID
    return orderRepository.findById(orderId)
}

// ✅ ХОРОШО: Проверка владельца на сервере
@GET("/api/orders/{orderId}")
suspend fun getOrder(
    @Path("orderId") orderId: String,
    @Header("Authorization") token: String
): Order {
    val userId = tokenService.extractUserId(token)
    val order = orderRepository.findById(orderId)

    // Проверяем, что заказ принадлежит текущему пользователю
    if (order.userId != userId) {
        throw ForbiddenException("Access denied")
    }

    return order
}
```

### Безопасная биометрическая аутентификация

```kotlin
// ✅ Android: BiometricPrompt с CryptoObject
class SecureBiometricAuth(
    private val activity: FragmentActivity,
    private val keyManager: BiometricKeyManager
) {

    fun authenticate(onSuccess: (ByteArray) -> Unit, onError: (String) -> Unit) {
        val cipher = keyManager.getCipherForDecryption()

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Подтвердите личность")
            .setSubtitle("Используйте биометрию для доступа")
            .setNegativeButtonText("Отмена")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {

                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    // Используем authenticated cipher для криптографической операции
                    // Это гарантирует, что биометрия действительно прошла
                    result.cryptoObject?.cipher?.let { authenticatedCipher ->
                        val decryptedData = keyManager.decrypt(authenticatedCipher)
                        onSuccess(decryptedData)
                    }
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(errString.toString())
                }
            }
        )

        // CryptoObject связывает биометрию с криптографией
        // Без него биометрия может быть обойдена на rooted устройствах
        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
    }
}
```

### Mitigation Checklist

```
□ MFA для критичных операций (платежи, смена пароля)
□ Биометрия с CryptoObject (не просто callback)
□ Проверка авторизации на СЕРВЕРЕ для каждого запроса
□ Защита от IDOR — проверка владельца ресурса
□ Session timeout и инвалидация при logout
□ Rate limiting для защиты от brute force
□ Secure password policy
```

---

## M4: Insufficient Input/Output Validation

### Описание

Недостаточная валидация данных из внешних источников: пользовательский ввод, deep links, intents, сетевые ответы.

### Типы атак

```
┌─────────────────────────────────────────────────────────────────┐
│                M4: INPUT/OUTPUT ATTACKS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SQL INJECTION                                                  │
│   → Инъекция SQL через input fields                              │
│   → SQLite на устройстве тоже уязвим                             │
│                                                                  │
│   COMMAND INJECTION                                              │
│   → Выполнение shell-команд через пользовательский ввод          │
│                                                                  │
│   PATH TRAVERSAL                                                 │
│   → ../../etc/passwd через filename input                        │
│                                                                  │
│   DEEP LINK INJECTION (Android/iOS)                              │
│   → Вредоносный deep link вызывает privileged action             │
│   → myapp://transfer?to=attacker&amount=1000                     │
│                                                                  │
│   INTENT SPOOFING (Android)                                      │
│   → Вредоносное приложение отправляет crafted intent             │
│                                                                  │
│   WEBVIEW XSS                                                    │
│   → JavaScript injection в WebView                               │
│                                                                  │
│   DESERIALIZATION                                                │
│   → Malicious serialized objects                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Пример Deep Link уязвимости

```kotlin
// ❌ ПЛОХО: Deep link без валидации
// AndroidManifest.xml
// <data android:scheme="myapp" android:host="transfer" />

class TransferActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        intent.data?.let { uri ->
            val recipient = uri.getQueryParameter("to")
            val amount = uri.getQueryParameter("amount")?.toDoubleOrNull()

            // Опасно! Атакующий может отправить:
            // myapp://transfer?to=attacker&amount=10000
            if (recipient != null && amount != null) {
                transferService.transfer(recipient, amount)
            }
        }
    }
}
```

```kotlin
// ✅ ХОРОШО: Валидация deep link + подтверждение пользователя
class TransferActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        intent.data?.let { uri ->
            // 1. Валидация источника
            if (!isValidReferrer()) {
                finish()
                return
            }

            // 2. Валидация параметров
            val recipient = uri.getQueryParameter("to")?.takeIf { isValidRecipient(it) }
            val amount = uri.getQueryParameter("amount")?.toDoubleOrNull()
                ?.takeIf { it > 0 && it <= MAX_TRANSFER_AMOUNT }

            if (recipient == null || amount == null) {
                showError("Invalid transfer parameters")
                return
            }

            // 3. Требуем явное подтверждение пользователя
            showTransferConfirmationDialog(recipient, amount) { confirmed ->
                if (confirmed) {
                    // 4. Требуем аутентификацию для критичной операции
                    biometricAuth.authenticate(
                        onSuccess = { transferService.transfer(recipient, amount) },
                        onError = { showError(it) }
                    )
                }
            }
        }
    }

    private fun isValidRecipient(recipient: String): Boolean {
        // Whitelist validation
        return recipient.matches(Regex("^[a-zA-Z0-9_]{3,20}$"))
    }
}
```

### Mitigation Checklist

```
□ Input validation на клиенте И сервере
□ Whitelist validation где возможно
□ Parameterized queries для SQL
□ Deep links требуют подтверждения для критичных действий
□ WebView: отключить JavaScript если не нужен
□ WebView: ограничить загружаемые URL
□ Intent validation для exported components
```

---

## M5: Insecure Communication

### Описание

Передача данных по незащищённым каналам. Даже при использовании HTTPS возможны атаки через repackaged apps или hooking frameworks (Frida).

### Угрозы

```
┌─────────────────────────────────────────────────────────────────┐
│                M5: COMMUNICATION THREATS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   CLEARTEXT TRAFFIC                                              │
│   → HTTP вместо HTTPS                                            │
│   → Данные видны в plaintext                                     │
│                                                                  │
│   MITM ATTACK                                                    │
│   → Атакующий перехватывает и модифицирует трафик                │
│   → Возможен даже с HTTPS если нет pinning                       │
│                                                                  │
│   WEAK TLS CONFIGURATION                                         │
│   → Устаревшие версии (TLS 1.0, 1.1)                             │
│   → Слабые cipher suites                                         │
│                                                                  │
│   CERTIFICATE VALIDATION BYPASS                                  │
│   → trustAllCertificates() в коде                                │
│   → Принятие self-signed сертификатов                            │
│                                                                  │
│   MISSING CERTIFICATE PINNING                                    │
│   → Приложение принимает любой valid сертификат                  │
│   → MITM с подменённым CA                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Certificate Pinning

```kotlin
// ✅ Android: Certificate Pinning с OkHttp
val certificatePinner = CertificatePinner.Builder()
    .add(
        "api.example.com",
        // SHA-256 hash публичного ключа сертификата
        "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    )
    .add(
        "api.example.com",
        // Backup pin на случай ротации сертификата
        "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
    )
    .build()

val okHttpClient = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

```xml
<!-- ✅ Android: Network Security Config -->
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Запрет cleartext traffic -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Certificate pinning для production -->
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2025-01-01">
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

```swift
// ✅ iOS: Certificate Pinning с TrustKit
import TrustKit

let trustKitConfig: [String: Any] = [
    kTSKSwizzleNetworkDelegates: true,
    kTSKPinnedDomains: [
        "api.example.com": [
            kTSKEnforcePinning: true,
            kTSKIncludeSubdomains: true,
            kTSKPublicKeyHashes: [
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
            ]
        ]
    ]
]

TrustKit.initSharedInstance(withConfiguration: trustKitConfig)
```

### Mitigation Checklist

```
□ HTTPS only (no cleartext)
□ TLS 1.2+ (предпочтительно TLS 1.3)
□ Certificate pinning
□ Network Security Config (Android)
□ App Transport Security (iOS)
□ Никогда не отключать certificate validation
□ Backup pins для ротации сертификатов
```

---

## M6: Inadequate Privacy Controls

**Новая категория в 2024.** Отражает требования GDPR, CCPA и растущее внимание к приватности.

### Описание

Неадекватный контроль приватности: сбор избыточных данных, утечки через логи, clipboard, URL parameters, отсутствие consent.

### Vectors утечки данных

```
┌─────────────────────────────────────────────────────────────────┐
│                M6: PRIVACY LEAKAGE VECTORS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   LOGS                                                           │
│   → PII в logcat/console                                         │
│   → Crash reports с sensitive data                               │
│   → Analytics events с PII                                       │
│                                                                  │
│   CLIPBOARD                                                      │
│   → Пользователь копирует пароль                                 │
│   → Другие приложения читают clipboard                           │
│                                                                  │
│   URL QUERY PARAMETERS                                           │
│   → ?email=user@example.com в URL                                │
│   → Видно в server logs, analytics, history                      │
│                                                                  │
│   BACKUPS                                                        │
│   → Sensitive data включается в device backup                    │
│   → Доступно через adb backup или iCloud                         │
│                                                                  │
│   SCREENSHOTS/SCREEN RECORDING                                   │
│   → Task switcher показывает sensitive screens                   │
│   → Screen recording захватывает PII                             │
│                                                                  │
│   THIRD-PARTY ANALYTICS                                          │
│   → SDK отправляет больше данных, чем нужно                      │
│   → Tracking без consent                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Защита от утечек

```kotlin
// ✅ Защита от screenshots в task switcher
class SensitiveActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Предотвращает screenshots и показ в task switcher
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
    }
}

// ✅ Исключение из backup
// AndroidManifest.xml
// android:allowBackup="false"
// или использовать backup rules:
```

```xml
<!-- res/xml/backup_rules.xml -->
<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <!-- Исключаем sensitive данные из backup -->
    <exclude domain="sharedpref" path="secure_credentials.xml"/>
    <exclude domain="database" path="sensitive.db"/>
    <exclude domain="file" path="private_keys/"/>
</full-backup-content>
```

```kotlin
// ✅ Безопасное логирование
object SecureLogger {
    private val SENSITIVE_PATTERNS = listOf(
        Regex("password[\"']?\\s*[:=]\\s*[\"']?[^\"'\\s]+"),
        Regex("token[\"']?\\s*[:=]\\s*[\"']?[^\"'\\s]+"),
        Regex("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
    )

    fun log(tag: String, message: String) {
        if (BuildConfig.DEBUG) {
            val sanitized = sanitize(message)
            Log.d(tag, sanitized)
        }
        // В release — только в secure logging service
    }

    private fun sanitize(message: String): String {
        var result = message
        SENSITIVE_PATTERNS.forEach { pattern ->
            result = result.replace(pattern, "[REDACTED]")
        }
        return result
    }
}
```

### Mitigation Checklist

```
□ Минимизация сбора PII
□ FLAG_SECURE для sensitive screens
□ Исключение sensitive данных из backup
□ Санитизация логов
□ Очистка clipboard после использования
□ Consent для tracking и analytics
□ Privacy policy в приложении
□ Data retention policy
```

---

## M7: Insufficient Binary Protections

**Объединение M8 (Code Tampering) и M9 (Reverse Engineering) из 2016.**

### Описание

Мобильные приложения распространяются как бинарники, которые можно декомпилировать и модифицировать. Без защиты атакующий может:
- Извлечь secrets и API keys
- Понять бизнес-логику
- Обойти license checks
- Внедрить malicious code

### Инструменты атакующего

```
┌─────────────────────────────────────────────────────────────────┐
│                M7: ATTACKER TOOLKIT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   REVERSE ENGINEERING                                            │
│   • jadx, apktool (Android) — декомпиляция APK                   │
│   • Hopper, IDA Pro (iOS) — дизассемблирование                   │
│   • class-dump (iOS) — извлечение Objective-C headers            │
│   • Ghidra — универсальный reverse engineering tool              │
│                                                                  │
│   RUNTIME MANIPULATION                                           │
│   • Frida — dynamic instrumentation                              │
│   • Xposed Framework (Android) — runtime hooks                   │
│   • Cycript (iOS) — runtime manipulation                         │
│                                                                  │
│   CODE TAMPERING                                                 │
│   • Repackaging APK/IPA с модификациями                          │
│   • Patching бинарника                                           │
│   • Memory editing                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Защитные меры

```kotlin
// ✅ Android: ProGuard/R8 obfuscation
// proguard-rules.pro
-keep class com.example.publicapi.** { *; }
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

// Obfuscate всё остальное
-repackageclasses ''
-allowaccessmodification
-optimizationpasses 5
```

```kotlin
// ✅ Проверка целостности приложения
class IntegrityChecker(private val context: Context) {

    fun isAppTampered(): Boolean {
        return !isSignatureValid() || isDebuggable() || isRunningOnEmulator()
    }

    private fun isSignatureValid(): Boolean {
        return try {
            val packageInfo = context.packageManager.getPackageInfo(
                context.packageName,
                PackageManager.GET_SIGNING_CERTIFICATES
            )
            val signatures = packageInfo.signingInfo.apkContentsSigners

            // Сравниваем с ожидаемым hash подписи
            val expectedHash = BuildConfig.EXPECTED_SIGNATURE_HASH
            val actualHash = signatures.firstOrNull()?.let {
                MessageDigest.getInstance("SHA-256")
                    .digest(it.toByteArray())
                    .joinToString("") { byte -> "%02x".format(byte) }
            }

            expectedHash == actualHash
        } catch (e: Exception) {
            false
        }
    }

    private fun isDebuggable(): Boolean {
        return (context.applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0
    }

    private fun isRunningOnEmulator(): Boolean {
        return Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MANUFACTURER.contains("Genymotion")
    }
}
```

### Mitigation Checklist

```
□ Code obfuscation (ProGuard/R8, SwiftShield)
□ String encryption для sensitive strings
□ Integrity checks (signature verification)
□ Anti-debugging measures
□ Emulator/root detection
□ RASP (Runtime Application Self-Protection)
□ Не хранить secrets в бинарнике
```

---

## M8: Security Misconfiguration

### Описание

Неправильные настройки безопасности: debug builds в production, exported components, избыточные permissions.

### Типичные проблемы

```
┌─────────────────────────────────────────────────────────────────┐
│                M8: MISCONFIGURATION EXAMPLES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   DEBUG IN PRODUCTION                                            │
│   • android:debuggable="true" в release                          │
│   • Verbose logging enabled                                      │
│   • Debug menus accessible                                       │
│                                                                  │
│   EXPORTED COMPONENTS (Android)                                  │
│   • Activity exported без проверки caller                        │
│   • Content Provider с world-readable данными                    │
│   • BroadcastReceiver принимает любые intents                    │
│                                                                  │
│   INSECURE PERMISSIONS                                           │
│   • Запрос избыточных permissions                                │
│   • World-readable/writable files                                │
│                                                                  │
│   BACKUP ENABLED                                                 │
│   • android:allowBackup="true" с sensitive данными               │
│                                                                  │
│   CLEARTEXT TRAFFIC                                              │
│   • usesCleartextTraffic="true"                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Безопасный AndroidManifest

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="false"
        android:usesCleartextTraffic="false"
        android:networkSecurityConfig="@xml/network_security_config">

        <!-- Exported activity — только если НУЖЕН внешний доступ -->
        <activity
            android:name=".DeepLinkActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:scheme="myapp" android:host="action" />
            </intent-filter>
        </activity>

        <!-- Internal activity — НЕ exported -->
        <activity
            android:name=".SensitiveActivity"
            android:exported="false" />

        <!-- Content Provider — restricted access -->
        <provider
            android:name=".SecureContentProvider"
            android:authorities="com.example.provider"
            android:exported="false"
            android:grantUriPermissions="false" />

        <!-- Broadcast Receiver с permission -->
        <receiver
            android:name=".SecureReceiver"
            android:exported="true"
            android:permission="com.example.SECURE_PERMISSION">
            <intent-filter>
                <action android:name="com.example.SECURE_ACTION" />
            </intent-filter>
        </receiver>

    </application>

</manifest>
```

### Mitigation Checklist

```
□ debuggable="false" в release
□ Явный exported="false" для internal components
□ Network Security Config с cleartextTrafficPermitted="false"
□ allowBackup="false" или backup rules
□ Минимальные permissions
□ Secure file permissions (MODE_PRIVATE)
□ Отключить debug logs в release
□ CI/CD проверки на misconfigurations
```

---

## M9: Insecure Data Storage

**Понижение с M2 (2016) до M9 (2024)** — платформы улучшили защиту, но проблема остаётся.

### Описание

Хранение sensitive данных в незащищённых местах: plaintext в SharedPreferences, SQLite без шифрования, файлы с world-readable permissions.

### Безопасные варианты хранения

```
┌─────────────────────────────────────────────────────────────────┐
│                M9: SECURE STORAGE OPTIONS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ANDROID                                                        │
│   ├── Credentials → EncryptedSharedPreferences                   │
│   ├── Keys → Android Keystore                                    │
│   ├── Database → SQLCipher или Room с encryption                 │
│   └── Files → EncryptedFile                                      │
│                                                                  │
│   iOS                                                            │
│   ├── Credentials → Keychain                                     │
│   ├── Keys → Secure Enclave                                      │
│   ├── Database → Core Data + Data Protection                     │
│   └── Files → Data Protection API                                │
│                                                                  │
│   ❌ НЕБЕЗОПАСНО:                                                │
│   • SharedPreferences без шифрования                             │
│   • UserDefaults для sensitive данных                            │
│   • SQLite без encryption                                        │
│   • External storage (SD card)                                   │
│   • Cache directories                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Подробнее см. [[android-permissions-security]] и [[ios-permissions-security]]

---

## M10: Insufficient Cryptography

### Описание

Использование слабой или неправильно реализованной криптографии: устаревшие алгоритмы, hardcoded ключи, неправильные режимы шифрования.

### Типичные ошибки

```kotlin
// ❌ ПЛОХО: Hardcoded key
val key = "mysecretkey12345".toByteArray()

// ❌ ПЛОХО: Устаревший алгоритм
val cipher = Cipher.getInstance("DES/ECB/PKCS5Padding")

// ❌ ПЛОХО: ECB mode (не использует IV)
val cipher = Cipher.getInstance("AES/ECB/PKCS5Padding")

// ❌ ПЛОХО: Weak random
val random = Random()  // java.util.Random — предсказуем!
```

```kotlin
// ✅ ХОРОШО: Android Keystore для генерации ключей
class SecureCrypto {

    private val keyAlias = "my_secure_key"

    init {
        if (!keyExists()) {
            generateKey()
        }
    }

    private fun generateKey() {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        keyGenerator.init(
            KeyGenParameterSpec.Builder(
                keyAlias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .setUserAuthenticationRequired(false)
                .build()
        )

        keyGenerator.generateKey()
    }

    fun encrypt(data: ByteArray): EncryptedData {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, getKey())

        val ciphertext = cipher.doFinal(data)
        return EncryptedData(
            ciphertext = ciphertext,
            iv = cipher.iv
        )
    }

    fun decrypt(encryptedData: EncryptedData): ByteArray {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, encryptedData.iv)
        cipher.init(Cipher.DECRYPT_MODE, getKey(), spec)

        return cipher.doFinal(encryptedData.ciphertext)
    }

    private fun getKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)
        return keyStore.getKey(keyAlias, null) as SecretKey
    }

    private fun keyExists(): Boolean {
        val keyStore = KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)
        return keyStore.containsAlias(keyAlias)
    }
}

data class EncryptedData(
    val ciphertext: ByteArray,
    val iv: ByteArray
)
```

### Рекомендации

```
┌─────────────────────────────────────────────────────────────────┐
│                M10: CRYPTOGRAPHY GUIDELINES                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ✅ ИСПОЛЬЗОВАТЬ:                                               │
│   • AES-256-GCM для symmetric encryption                         │
│   • RSA-2048+ или ECDSA для asymmetric                           │
│   • SHA-256+ для hashing                                         │
│   • Argon2/bcrypt/scrypt для password hashing                    │
│   • SecureRandom для генерации случайных чисел                   │
│   • Platform keystores (Android Keystore, iOS Keychain)          │
│                                                                  │
│   ❌ НЕ ИСПОЛЬЗОВАТЬ:                                            │
│   • DES, 3DES, RC4                                               │
│   • MD5, SHA-1 для security purposes                             │
│   • ECB mode                                                     │
│   • Hardcoded keys                                               │
│   • java.util.Random                                             │
│   • Custom crypto implementations                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Соответствие MASVS

OWASP Mobile Top 10 соответствует категориям OWASP MASVS:

| Mobile Top 10 | MASVS Category |
|---------------|----------------|
| M1, M3 | MASVS-AUTH |
| M2 | MASVS-CODE |
| M4 | MASVS-PLATFORM |
| M5 | MASVS-NETWORK |
| M6 | MASVS-PRIVACY |
| M7 | MASVS-RESILIENCE |
| M8 | MASVS-PLATFORM |
| M9, M10 | MASVS-STORAGE, MASVS-CRYPTO |

Подробнее: [[mobile-security-masvs]]

---

## Мифы и заблуждения

### Миф 1: "App Store/Play Store проверяют безопасность"

**Реальность:** Магазины проверяют на malware и policy violations, но не проводят полный security audit. Уязвимости в вашем коде — ваша ответственность.

### Миф 2: "iOS безопаснее Android, можно не защищать"

**Реальность:** Обе платформы имеют уязвимости. Jailbroken iOS устройства так же уязвимы, как rooted Android. Код приложения уязвим на обеих платформах.

### Миф 3: "Certificate pinning достаточно для защиты от MITM"

**Реальность:** Pinning можно обойти через Frida/Xposed на rooted устройствах. Нужна комплексная защита: pinning + root detection + integrity checks.

### Миф 4: "Obfuscation делает reverse engineering невозможным"

**Реальность:** Obfuscation усложняет, но не делает невозможным. Это layer of defense, не полная защита. Не храните secrets в бинарнике.

### Миф 5: "Данные в приложении безопасны, т.к. песочница"

**Реальность:** Sandbox защищает от других приложений, но не от:
- Пользователя с root/jailbreak
- Backup extraction
- Physical access к устройству
- Malware с root-правами

---

## Куда дальше (Навигация)

### Углублённое изучение

→ [[mobile-security-masvs]] — MASVS стандарт и MSTG тестирование
→ [[mobile-app-protection]] — Root detection, attestation, anti-tampering

### Платформенная специфика

→ [[android-permissions-security]] — Android permissions и безопасное хранение
→ [[ios-permissions-security]] — iOS permissions, Keychain, Data Protection

### Защита приложений

→ [[android-proguard-r8]] — Obfuscation для Android

---

## Связанные материалы

| Материал | Связь |
|----------|-------|
| [[security-fundamentals]] | Базовые принципы безопасности |
| [[mobile-security-masvs]] | Стандарт верификации безопасности |
| [[mobile-app-protection]] | Runtime protection, attestation |
| [[android-permissions-security]] | Android-специфичная безопасность |
| [[ios-permissions-security]] | iOS-специфичная безопасность |
| [[security-cryptography-fundamentals]] | Криптографические основы |
| [[security-https-tls]] | TLS и certificate pinning |

---

## Источники

- [OWASP Mobile Top 10 2024 - Official](https://owasp.org/www-project-mobile-top-10/)
- [M1: Improper Credential Usage - OWASP](https://owasp.org/www-project-mobile-top-10/2023-risks/m1-improper-credential-usage)
- [M2: Inadequate Supply Chain Security - OWASP](https://owasp.org/www-project-mobile-top-10/2023-risks/m2-inadequate-supply-chain-security.html)
- [M6: Inadequate Privacy Controls - OWASP](https://owasp.org/www-project-mobile-top-10/2023-risks/m6-inadequate-privacy-controls)
- [M8: Security Misconfiguration - OWASP](https://owasp.org/www-project-mobile-top-10/2023-risks/m8-security-misconfiguration)
- [OWASP Mobile Top 10 2024 - Indusface](https://www.indusface.com/blog/owasp-mobile-top-10-2024/)
- [OWASP Mobile Top 10 2024 Update - Cobalt](https://www.cobalt.io/blog/owasp-mobile-top-10-2024-update)
- [OWASP Mobile Top 10 2024 - Astra](https://www.getastra.com/blog/mobile/owasp-mobile-top-10-2024-a-security-guide/)
- [2024 OWASP Mobile Top Ten Risks - Approov](https://approov.io/blog/2024-owasp-mobile-top-ten-risks)
- [OWASP Mobile Top 10 - Strobes](https://strobes.co/blog/owasp-mobile-top-10-vulnerabilities-2024-updated/)

---

*Обновлено: 2026-01-29*
*Версия: 1.0*

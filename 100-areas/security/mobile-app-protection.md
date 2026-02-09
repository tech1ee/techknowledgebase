# Mobile App Protection: Защита приложений от атак

## Metadata
- **Тип:** Deep-dive
- **Технологии:** Android, iOS, RASP, Attestation
- **Уровень:** Advanced
- **Дата обновления:** 2026-01-29

---

## TL;DR

> **Mobile App Protection** — это комплекс технологий и практик для защиты мобильных приложений от реверс-инжиниринга, тампирования, динамического анализа и работы в скомпрометированных средах.
> Современная защита требует **Defense in Depth**: множество слоёв от code hardening до runtime protection.

**Ключевые компоненты защиты:**
```
┌─────────────────────────────────────────────────────────────┐
│                 Mobile App Protection Stack                  │
├─────────────────────────────────────────────────────────────┤
│  Code Hardening                                              │
│  ├── Obfuscation (name, control flow, data)                 │
│  ├── String encryption                                       │
│  └── Native code protection                                  │
├─────────────────────────────────────────────────────────────┤
│  Runtime Protection (RASP)                                   │
│  ├── Root/Jailbreak detection                               │
│  ├── Debugger detection                                      │
│  ├── Hooking framework detection (Frida, Xposed)            │
│  ├── Emulator detection                                      │
│  └── Integrity verification                                  │
├─────────────────────────────────────────────────────────────┤
│  Attestation Services                                        │
│  ├── Play Integrity API (Android)                           │
│  ├── App Attest + DeviceCheck (iOS)                         │
│  └── Backend verification                                    │
├─────────────────────────────────────────────────────────────┤
│  Secrets Protection                                          │
│  ├── No hardcoded keys                                       │
│  ├── Runtime secrets delivery                                │
│  └── Secure storage (Keystore/Keychain)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Почему это важно

### Угрозы современным мобильным приложениям

```
Ландшафт угроз 2025:

Reverse Engineering
├── Декомпиляция APK/IPA
├── Анализ бизнес-логики
├── Извлечение API ключей и secrets
└── Кража интеллектуальной собственности

Runtime Attacks
├── Frida/Objection instrumentation
├── Xposed/Substrate hooking
├── Memory manipulation
└── Function hooking и bypass

Environment Attacks
├── Rooted/Jailbroken devices
├── Emulators с spoofing
├── Modified system libraries
└── Malware на устройстве

Man-in-the-Middle
├── SSL/TLS interception
├── Certificate pinning bypass
├── API manipulation
└── Session hijacking

Code Tampering
├── App repackaging
├── Malicious code injection
├── Resource modification
└── Signature bypass
```

### Статистика рисков

Согласно исследованиям Zimperium, риски на rooted устройствах значительно выше:

```
Rooted vs Stock Device Risk Factor:

Malware attacks:           3.5x чаще
Compromised apps:          12x чаще
System compromise:         250x чаще
Filesystem compromise:     3000x чаще

Источник: Zimperium 2024 Mobile Threat Report
```

### Экономический ущерб

```
Cost of Mobile Security Incidents (2025):

Average incident cost:     $1M - $5M+
API key leak impact:       Unauthorized usage, data breach
IP theft impact:           Competitive disadvantage, revenue loss
Fraud impact:              Direct financial losses
Reputation impact:         User trust, brand damage
```

### Почему одной меры недостаточно

```
Single Point of Failure:

❌ "У нас есть root detection"
   └── Magisk Hide/Shamiko обходит за минуты

❌ "Мы используем ProGuard"
   └── Только name obfuscation, легко читается

❌ "Мы проверяем certificate pinning"
   └── Frida bypass scripts публично доступны

❌ "Мы используем Play Integrity"
   └── Не защищает от runtime attacks

✓ Defense in Depth:
   └── Множество слоёв защиты
       ├── Каждый слой замедляет атакующего
       ├── Bypass одного не компрометирует всё
       └── Стоимость атаки возрастает экспоненциально
```

---

## Code Hardening

### Уровни обфускации

Code hardening защищает от статического анализа — изучения декомпилированного кода:

```
Obfuscation Levels:

Level 1: Name Obfuscation (ProGuard/R8)
├── Переименование классов: MyClass → a
├── Переименование методов: getUserToken() → b()
├── Переименование полей: authToken → c
└── Эффективность: Низкая (легко понять логику)

Level 2: String Encryption
├── Шифрование строковых констант
├── Расшифровка в runtime
├── API URLs, error messages скрыты
└── Эффективность: Средняя (Frida может перехватить)

Level 3: Control Flow Obfuscation
├── Изменение структуры кода
├── Fake branches и dead code
├── Loop transformations
└── Эффективность: Высокая (значительно усложняет анализ)

Level 4: Code Virtualization
├── Код превращается в bytecode для custom VM
├── Интерпретатор выполняет instructions
├── Практически невозможно статически анализировать
└── Эффективность: Очень высокая (требует динамический анализ)
```

### ProGuard vs R8 vs DexGuard

```
Comparison Table:

Feature              │ ProGuard/R8 │ DexGuard
─────────────────────┼─────────────┼──────────
Name obfuscation     │     ✓       │    ✓
String encryption    │     ✗       │    ✓
Control flow obfusc  │     ✗       │    ✓
Code virtualization  │     ✗       │    ✓
Class encryption     │     ✗       │    ✓
Resource encryption  │     ✗       │    ✓
RASP integration     │     ✗       │    ✓
Anti-debugging       │     ✗       │    ✓
Anti-hooking         │     ✗       │    ✓
Cost                 │   Free      │  $$$
```

### Настройка ProGuard/R8

```groovy
// build.gradle.kts (Android)
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

```proguard
# proguard-rules.pro

# Optimize aggressively
-optimizationpasses 5
-allowaccessmodification
-repackageclasses ''

# Remove logging
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
    public static *** w(...);
    public static *** e(...);
}

# Obfuscate more aggressively
-obfuscationdictionary obfuscation-dictionary.txt
-classobfuscationdictionary obfuscation-dictionary.txt
-packageobfuscationdictionary obfuscation-dictionary.txt

# Keep security-critical classes (for signature verification)
-keep class com.myapp.security.** { *; }

# Don't optimize security checks (prevents removal)
-keep,allowobfuscation class com.myapp.security.IntegrityChecker {
    public <methods>;
}
```

### String Encryption (Manual Implementation)

```kotlin
// Простая string encryption для критичных значений
// Примечание: Для production используйте DexGuard или аналоги

object SecureStrings {

    // XOR-based encryption (базовый пример)
    // В production используйте AES или native реализацию

    private val key = byteArrayOf(0x4a, 0x7b, 0x3c, 0x1d, 0x5e, 0x6f, 0x2a, 0x8b)

    private fun decrypt(encrypted: ByteArray): String {
        val decrypted = ByteArray(encrypted.size)
        for (i in encrypted.indices) {
            decrypted[i] = (encrypted[i].toInt() xor key[i % key.size].toInt()).toByte()
        }
        return String(decrypted, Charsets.UTF_8)
    }

    // Зашифрованные строки (сгенерированы build script)
    private val API_BASE_URL_ENCRYPTED = byteArrayOf(
        0x2a, 0x1f, 0x5c, 0x7e, 0x3a, 0x4d, 0x6b, 0x19,
        // ... encrypted bytes
    )

    val apiBaseUrl: String
        get() = decrypt(API_BASE_URL_ENCRYPTED)
}
```

### Native Code Protection

```cpp
// jni/security.cpp
// Критичная логика в native коде сложнее анализировать

#include <jni.h>
#include <string>

// Anti-debugging: ptrace check
bool isDebuggerAttached() {
    // На Linux/Android ptrace(PTRACE_TRACEME) вернёт -1 если уже под дебаггером
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {
        return true;
    }
    ptrace(PTRACE_DETACH, 0, 0, 0);
    return false;
}

// Encrypted API key (decrypted at runtime)
extern "C" JNIEXPORT jstring JNICALL
Java_com_myapp_security_NativeSecurity_getApiKey(
    JNIEnv *env,
    jobject /* this */
) {
    // Anti-debug check
    if (isDebuggerAttached()) {
        return env->NewStringUTF("");
    }

    // Encrypted key (XOR с compile-time key)
    unsigned char encrypted[] = {
        0x4a, 0x7b, 0x3c, 0x1d, 0x5e, 0x6f, 0x2a, 0x8b,
        // ... encrypted API key bytes
    };

    unsigned char key[] = {0x12, 0x34, 0x56, 0x78};

    char decrypted[sizeof(encrypted) + 1];
    for (size_t i = 0; i < sizeof(encrypted); i++) {
        decrypted[i] = encrypted[i] ^ key[i % sizeof(key)];
    }
    decrypted[sizeof(encrypted)] = '\0';

    return env->NewStringUTF(decrypted);
}
```

---

## Runtime Protection (RASP)

### Root/Jailbreak Detection

Root/jailbreak detection — одна из базовых проверок, но с множеством нюансов:

```
Root Detection Methods:

1. File Existence Checks
   ├── /system/app/Superuser.apk
   ├── /sbin/su
   ├── /system/bin/su
   ├── /system/xbin/su
   ├── /data/local/bin/su
   ├── /su/bin/su
   ├── /magisk/.core
   └── Bypass: Magisk Hide скрывает эти файлы

2. Package Checks
   ├── com.topjohnwu.magisk
   ├── eu.chainfire.supersu
   ├── com.koushikdutta.superuser
   └── Bypass: Package name randomization

3. Build Properties
   ├── ro.build.tags=test-keys (вместо release-keys)
   ├── ro.debuggable=1
   └── Bypass: Props override

4. Su Binary Execution
   ├── Runtime.exec("su")
   ├── Проверка return code
   └── Bypass: Shamiko blocks su for specific apps

5. Native Checks
   ├── /proc/self/mounts analysis
   ├── Memory scanning
   └── Bypass: Сложнее, но возможно

6. SafetyNet/Play Integrity
   ├── Server-side verification
   ├── Hardware attestation (сложно обойти)
   └── Bypass: Модули для spoofing (менее надёжны)
```

**Реализация multi-layer root detection:**

```kotlin
// Android Root Detection
class RootDetector(private val context: Context) {

    sealed class RootStatus {
        object NotRooted : RootStatus()
        data class Rooted(val indicators: List<String>) : RootStatus()
    }

    fun checkRoot(): RootStatus {
        val indicators = mutableListOf<String>()

        // Layer 1: File checks
        if (checkRootFiles()) {
            indicators.add("root_files")
        }

        // Layer 2: Package checks
        if (checkRootPackages()) {
            indicators.add("root_packages")
        }

        // Layer 3: Build properties
        if (checkBuildTags()) {
            indicators.add("test_keys")
        }

        // Layer 4: Su binary
        if (checkSuBinary()) {
            indicators.add("su_binary")
        }

        // Layer 5: Native check
        if (checkRootNative()) {
            indicators.add("native_detection")
        }

        // Layer 6: Magisk specific
        if (checkMagisk()) {
            indicators.add("magisk")
        }

        return if (indicators.isEmpty()) {
            RootStatus.NotRooted
        } else {
            RootStatus.Rooted(indicators)
        }
    }

    private fun checkRootFiles(): Boolean {
        val paths = listOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su",
            "/data/adb/magisk",
            "/sbin/.magisk"
        )

        return paths.any { path ->
            try {
                File(path).exists()
            } catch (e: Exception) {
                false
            }
        }
    }

    private fun checkRootPackages(): Boolean {
        val packages = listOf(
            "com.topjohnwu.magisk",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.noshufou.android.su",
            "com.thirdparty.superuser",
            "com.yellowes.su",
            "com.kingroot.kinguser",
            "com.kingo.root",
            "com.smedialink.onecleanmaster",
            "com.zhiqupk.root.global"
        )

        val pm = context.packageManager
        return packages.any { pkg ->
            try {
                pm.getPackageInfo(pkg, 0)
                true
            } catch (e: PackageManager.NameNotFoundException) {
                false
            }
        }
    }

    private fun checkBuildTags(): Boolean {
        val tags = Build.TAGS
        return tags != null && tags.contains("test-keys")
    }

    private fun checkSuBinary(): Boolean {
        return try {
            val process = Runtime.getRuntime().exec(arrayOf("/system/xbin/which", "su"))
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            reader.readLine() != null
        } catch (e: Exception) {
            false
        }
    }

    // Native check через JNI
    private external fun checkRootNative(): Boolean

    private fun checkMagisk(): Boolean {
        // Проверка через mount points
        return try {
            val mounts = File("/proc/self/mounts").readText()
            mounts.contains("magisk") || mounts.contains("/sbin/.core")
        } catch (e: Exception) {
            false
        }
    }

    companion object {
        init {
            System.loadLibrary("security")
        }
    }
}
```

```swift
// iOS Jailbreak Detection
class JailbreakDetector {

    enum JailbreakStatus {
        case notJailbroken
        case jailbroken(indicators: [String])
    }

    func checkJailbreak() -> JailbreakStatus {
        var indicators: [String] = []

        // Layer 1: File checks
        if checkJailbreakFiles() {
            indicators.append("jailbreak_files")
        }

        // Layer 2: URL Schemes
        if checkCydiaScheme() {
            indicators.append("cydia_scheme")
        }

        // Layer 3: Sandbox integrity
        if checkSandboxViolation() {
            indicators.append("sandbox_violation")
        }

        // Layer 4: Dylib injection
        if checkDylibInjection() {
            indicators.append("dylib_injection")
        }

        // Layer 5: Fork check
        if checkForkAbility() {
            indicators.append("fork_available")
        }

        // Layer 6: Symbolic links
        if checkSymbolicLinks() {
            indicators.append("suspicious_symlinks")
        }

        if indicators.isEmpty {
            return .notJailbroken
        } else {
            return .jailbroken(indicators: indicators)
        }
    }

    private func checkJailbreakFiles() -> Bool {
        let paths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/usr/bin/ssh",
            "/private/var/lib/apt",
            "/private/var/lib/cydia",
            "/private/var/stash",
            "/usr/libexec/cydia",
            "/var/cache/apt",
            "/var/lib/dpkg",
            "/jb/lzma",
            "/.bootstrapped_electra",
            "/usr/lib/libjailbreak.dylib",
            "/jb/jailbreakd.plist",
            "/jb/amfid_payload.dylib",
            "/jb/libjailbreak.dylib",
            "/usr/libexec/sftp-server",
            "/Library/PreferenceBundles/LibertyPref.bundle",
            "/Library/PreferenceLoader/Preferences/LibertyPref.plist"
        ]

        for path in paths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }

        return false
    }

    private func checkCydiaScheme() -> Bool {
        if let url = URL(string: "cydia://package/com.example.package") {
            return UIApplication.shared.canOpenURL(url)
        }
        return false
    }

    private func checkSandboxViolation() -> Bool {
        // Попытка записи вне sandbox
        let testPath = "/private/test_jailbreak_\(UUID().uuidString)"
        do {
            try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
            try FileManager.default.removeItem(atPath: testPath)
            return true // Если получилось — sandbox нарушен
        } catch {
            return false
        }
    }

    private func checkDylibInjection() -> Bool {
        // Проверка загруженных dylib
        let suspiciousDylibs = [
            "MobileSubstrate",
            "SubstrateLoader",
            "TweakInject",
            "libhooker",
            "substitute",
            "frida",
            "cycript"
        ]

        var count: UInt32 = 0
        let images = UnsafeBufferPointer(
            start: _dyld_get_image_name as? UnsafePointer<UnsafePointer<CChar>?>,
            count: Int(_dyld_image_count())
        )

        for i in 0..<_dyld_image_count() {
            if let imageName = _dyld_get_image_name(i) {
                let name = String(cString: imageName)
                for suspicious in suspiciousDylibs {
                    if name.lowercased().contains(suspicious.lowercased()) {
                        return true
                    }
                }
            }
        }

        return false
    }

    private func checkForkAbility() -> Bool {
        // На jailbroken устройствах fork() работает
        let pid = fork()
        if pid >= 0 {
            if pid > 0 {
                kill(pid, SIGTERM)
            }
            return true
        }
        return false
    }

    private func checkSymbolicLinks() -> Bool {
        let paths = [
            "/Applications",
            "/Library/Ringtones",
            "/Library/Wallpaper",
            "/usr/arm-apple-darwin9",
            "/usr/include",
            "/usr/libexec",
            "/usr/share"
        ]

        for path in paths {
            var isSymlink: ObjCBool = false
            if FileManager.default.fileExists(atPath: path, isDirectory: &isSymlink) {
                do {
                    let attrs = try FileManager.default.attributesOfItem(atPath: path)
                    if attrs[.type] as? FileAttributeType == .typeSymbolicLink {
                        return true
                    }
                } catch {}
            }
        }

        return false
    }
}
```

### Debugger Detection

```kotlin
// Android Debugger Detection
class DebuggerDetector {

    fun isDebuggerAttached(): Boolean {
        // Method 1: Debug.isDebuggerConnected()
        if (Debug.isDebuggerConnected()) {
            return true
        }

        // Method 2: Tracerpid check
        if (checkTracerPid()) {
            return true
        }

        // Method 3: Debug flags
        if (checkDebugFlags()) {
            return true
        }

        // Method 4: Native ptrace check
        if (checkPtraceNative()) {
            return true
        }

        return false
    }

    private fun checkTracerPid(): Boolean {
        return try {
            val status = File("/proc/self/status").readText()
            val tracerPid = Regex("TracerPid:\\s+(\\d+)")
                .find(status)
                ?.groupValues
                ?.get(1)
                ?.toIntOrNull() ?: 0
            tracerPid != 0
        } catch (e: Exception) {
            false
        }
    }

    private fun checkDebugFlags(): Boolean {
        return (context.applicationInfo.flags and
                ApplicationInfo.FLAG_DEBUGGABLE) != 0
    }

    private external fun checkPtraceNative(): Boolean
}
```

### Frida Detection

Frida — основной инструмент для динамического анализа, его обнаружение критично:

```kotlin
// Frida Detection
class FridaDetector {

    fun isFridaDetected(): Boolean {
        // Method 1: Default port check
        if (checkDefaultPort()) {
            return true
        }

        // Method 2: Process name check
        if (checkFridaProcess()) {
            return true
        }

        // Method 3: Library mapping check
        if (checkFridaLibraries()) {
            return true
        }

        // Method 4: D-Bus check
        if (checkDBus()) {
            return true
        }

        // Method 5: Memory artifacts
        if (checkMemoryArtifacts()) {
            return true
        }

        // Method 6: Named pipes
        if (checkNamedPipes()) {
            return true
        }

        return false
    }

    private fun checkDefaultPort(): Boolean {
        // Frida default ports: 27042, 27043
        val ports = listOf(27042, 27043)

        return ports.any { port ->
            try {
                Socket("127.0.0.1", port).use { true }
            } catch (e: Exception) {
                false
            }
        }
    }

    private fun checkFridaProcess(): Boolean {
        return try {
            val process = Runtime.getRuntime().exec("ps")
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            var line: String?
            while (reader.readLine().also { line = it } != null) {
                if (line?.contains("frida") == true ||
                    line?.contains("gum-js-loop") == true ||
                    line?.contains("gmain") == true) {
                    return true
                }
            }
            false
        } catch (e: Exception) {
            false
        }
    }

    private fun checkFridaLibraries(): Boolean {
        return try {
            val maps = File("/proc/self/maps").readText()
            maps.contains("frida") ||
            maps.contains("gadget") ||
            maps.contains("gum-js-loop")
        } catch (e: Exception) {
            false
        }
    }

    private fun checkDBus(): Boolean {
        // Frida использует D-Bus для IPC
        return try {
            val cmd = File("/proc/self/cmdline").readText()
            cmd.contains("frida") || cmd.contains("gadget")
        } catch (e: Exception) {
            false
        }
    }

    private fun checkMemoryArtifacts(): Boolean {
        // Frida оставляет специфичные строки в памяти
        val artifacts = listOf(
            "LIBFRIDA",
            "frida:rpc",
            "frida-agent",
            "GumJS"
        )

        return try {
            val maps = File("/proc/self/maps").readText()
            artifacts.any { artifact ->
                maps.contains(artifact, ignoreCase = true)
            }
        } catch (e: Exception) {
            false
        }
    }

    private fun checkNamedPipes(): Boolean {
        // Frida создаёт named pipes для коммуникации
        val linjectorPath = "/data/local/tmp/linjector"
        val fridaPipePath = "/data/local/tmp/frida"

        return File(linjectorPath).exists() || File(fridaPipePath).exists()
    }
}
```

### Emulator Detection

```kotlin
// Android Emulator Detection
class EmulatorDetector {

    data class EmulatorCheck(
        val isEmulator: Boolean,
        val confidence: Float, // 0.0 - 1.0
        val indicators: List<String>
    )

    fun detect(): EmulatorCheck {
        val indicators = mutableListOf<String>()
        var score = 0f

        // Check 1: Build properties (weight: 0.2)
        if (checkBuildProperties()) {
            indicators.add("build_properties")
            score += 0.2f
        }

        // Check 2: Hardware properties (weight: 0.15)
        if (checkHardwareProperties()) {
            indicators.add("hardware")
            score += 0.15f
        }

        // Check 3: Telephony (weight: 0.15)
        if (checkTelephony()) {
            indicators.add("telephony")
            score += 0.15f
        }

        // Check 4: Sensors (weight: 0.2)
        if (checkSensors()) {
            indicators.add("sensors")
            score += 0.2f
        }

        // Check 5: Files (weight: 0.15)
        if (checkEmulatorFiles()) {
            indicators.add("emulator_files")
            score += 0.15f
        }

        // Check 6: Network (weight: 0.15)
        if (checkNetwork()) {
            indicators.add("network")
            score += 0.15f
        }

        return EmulatorCheck(
            isEmulator = score >= 0.5f,
            confidence = score.coerceIn(0f, 1f),
            indicators = indicators
        )
    }

    private fun checkBuildProperties(): Boolean {
        val suspiciousProperties = mapOf(
            Build.FINGERPRINT to listOf("generic", "unknown", "google/sdk"),
            Build.MODEL to listOf("google_sdk", "Emulator", "Android SDK"),
            Build.MANUFACTURER to listOf("Genymotion", "unknown"),
            Build.BRAND to listOf("generic", "generic_x86"),
            Build.DEVICE to listOf("generic", "generic_x86", "vbox86p"),
            Build.PRODUCT to listOf("sdk", "google_sdk", "sdk_x86", "vbox86p"),
            Build.HARDWARE to listOf("goldfish", "ranchu", "vbox86")
        )

        return suspiciousProperties.any { (property, suspicious) ->
            suspicious.any {
                property?.lowercase()?.contains(it.lowercase()) == true
            }
        }
    }

    private fun checkHardwareProperties(): Boolean {
        // IMEI check
        val telephonyManager = context.getSystemService(
            Context.TELEPHONY_SERVICE
        ) as? TelephonyManager

        @SuppressLint("HardwareIds")
        val deviceId = try {
            telephonyManager?.deviceId
        } catch (e: SecurityException) {
            null
        }

        if (deviceId == "000000000000000" || deviceId == null) {
            return true
        }

        return false
    }

    private fun checkTelephony(): Boolean {
        val telephonyManager = context.getSystemService(
            Context.TELEPHONY_SERVICE
        ) as? TelephonyManager

        // Эмуляторы часто имеют специфичные номера
        val phoneNumber = try {
            telephonyManager?.line1Number
        } catch (e: SecurityException) {
            null
        }

        val suspiciousNumbers = listOf(
            "15555215554", "15555215556", "15555215558",
            "15555215560", "15555215562"
        )

        return suspiciousNumbers.contains(phoneNumber)
    }

    private fun checkSensors(): Boolean {
        val sensorManager = context.getSystemService(
            Context.SENSOR_SERVICE
        ) as SensorManager

        // Реальные устройства имеют множество сенсоров
        val sensorCount = sensorManager.getSensorList(Sensor.TYPE_ALL).size

        // Эмуляторы обычно имеют мало сенсоров
        return sensorCount < 5
    }

    private fun checkEmulatorFiles(): Boolean {
        val emulatorFiles = listOf(
            "/dev/socket/qemud",
            "/dev/qemu_pipe",
            "/system/lib/libc_malloc_debug_qemu.so",
            "/sys/qemu_trace",
            "/system/bin/qemu-props",
            "/dev/socket/genyd",
            "/dev/socket/baseband_genyd"
        )

        return emulatorFiles.any { File(it).exists() }
    }

    private fun checkNetwork(): Boolean {
        // Стандартный IP эмулятора Android Studio
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val iface = interfaces.nextElement()
                val addresses = iface.inetAddresses
                while (addresses.hasMoreElements()) {
                    val addr = addresses.nextElement()
                    val ip = addr.hostAddress
                    if (ip == "10.0.2.15" || ip == "10.0.2.16") {
                        return true
                    }
                }
            }
        } catch (e: Exception) {}

        return false
    }
}
```

### Integrity Verification

```kotlin
// APK Integrity Verification
class IntegrityVerifier(private val context: Context) {

    sealed class IntegrityStatus {
        object Valid : IntegrityStatus()
        data class Invalid(val reason: String) : IntegrityStatus()
    }

    fun verify(): IntegrityStatus {
        // Step 1: Verify APK signature
        val signatureResult = verifySignature()
        if (signatureResult is IntegrityStatus.Invalid) {
            return signatureResult
        }

        // Step 2: Verify installer source
        val installerResult = verifyInstaller()
        if (installerResult is IntegrityStatus.Invalid) {
            return installerResult
        }

        // Step 3: Verify APK checksum
        val checksumResult = verifyChecksum()
        if (checksumResult is IntegrityStatus.Invalid) {
            return checksumResult
        }

        return IntegrityStatus.Valid
    }

    private fun verifySignature(): IntegrityStatus {
        try {
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
                packageInfo.signingInfo?.apkContentsSigners
            } else {
                @Suppress("DEPRECATION")
                packageInfo.signatures
            }

            if (signatures.isNullOrEmpty()) {
                return IntegrityStatus.Invalid("No signatures found")
            }

            // Compute SHA-256 of certificate
            val signature = signatures[0]
            val md = MessageDigest.getInstance("SHA-256")
            val digest = md.digest(signature.toByteArray())
            val currentHash = Base64.encodeToString(digest, Base64.NO_WRAP)

            // Compare with expected hash (stored securely, ideally in native)
            val expectedHash = getExpectedSignatureHash()

            return if (currentHash == expectedHash) {
                IntegrityStatus.Valid
            } else {
                IntegrityStatus.Invalid("Signature mismatch")
            }

        } catch (e: Exception) {
            return IntegrityStatus.Invalid("Signature verification failed: ${e.message}")
        }
    }

    private fun verifyInstaller(): IntegrityStatus {
        val allowedInstallers = listOf(
            "com.android.vending",      // Google Play
            "com.amazon.venezia",        // Amazon Appstore
            "com.huawei.appmarket",      // Huawei AppGallery
            "com.sec.android.app.samsungapps" // Samsung Galaxy Store
        )

        val installer = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            context.packageManager
                .getInstallSourceInfo(context.packageName)
                .installingPackageName
        } else {
            @Suppress("DEPRECATION")
            context.packageManager.getInstallerPackageName(context.packageName)
        }

        return if (installer in allowedInstallers) {
            IntegrityStatus.Valid
        } else {
            IntegrityStatus.Invalid("Unknown installer: $installer")
        }
    }

    private fun verifyChecksum(): IntegrityStatus {
        try {
            val apkPath = context.packageCodePath
            val apkFile = File(apkPath)

            val md = MessageDigest.getInstance("SHA-256")
            FileInputStream(apkFile).use { fis ->
                val buffer = ByteArray(8192)
                var bytesRead: Int
                while (fis.read(buffer).also { bytesRead = it } != -1) {
                    md.update(buffer, 0, bytesRead)
                }
            }

            val currentChecksum = Base64.encodeToString(md.digest(), Base64.NO_WRAP)
            val expectedChecksum = getExpectedApkChecksum()

            return if (currentChecksum == expectedChecksum) {
                IntegrityStatus.Valid
            } else {
                IntegrityStatus.Invalid("APK checksum mismatch")
            }

        } catch (e: Exception) {
            return IntegrityStatus.Invalid("Checksum verification failed: ${e.message}")
        }
    }

    // В реальности получать из native кода или secure server
    private external fun getExpectedSignatureHash(): String
    private external fun getExpectedApkChecksum(): String

    companion object {
        init {
            System.loadLibrary("security")
        }
    }
}
```

---

## Platform Attestation Services

### Play Integrity API (Android)

Play Integrity API заменил SafetyNet и предоставляет более надёжную аттестацию:

```
Play Integrity API Overview:

Timeline:
├── Oct 2023: SafetyNet deprecation announced
├── Jan 2025: SafetyNet fully discontinued
├── May 2025: Hardware-backed signals required for STRONG
└── Aug 2025: Version 1.5.0 с remediation dialogs

Verdicts:
├── MEETS_DEVICE_INTEGRITY
│   └── App running on genuine Android device
├── MEETS_BASIC_INTEGRITY
│   └── Device passes basic integrity (may be rooted)
├── MEETS_STRONG_INTEGRITY
│   └── Hardware-backed + recent security patch
└── App License Verification
    └── App installed from Play Store
```

**Реализация Play Integrity:**

```kotlin
// Play Integrity API Implementation
class PlayIntegrityChecker(private val context: Context) {

    private val integrityManager = IntegrityManagerFactory.create(context)

    data class IntegrityResult(
        val meetsDeviceIntegrity: Boolean,
        val meetsBasicIntegrity: Boolean,
        val meetsStrongIntegrity: Boolean,
        val appLicensed: Boolean,
        val rawToken: String
    )

    suspend fun requestIntegrityToken(): Result<IntegrityResult> {
        return withContext(Dispatchers.IO) {
            try {
                // Generate nonce (should come from your server)
                val nonce = generateNonce()

                val request = IntegrityTokenRequest.builder()
                    .setNonce(nonce)
                    .setCloudProjectNumber(YOUR_CLOUD_PROJECT_NUMBER)
                    .build()

                val tokenResponse = integrityManager
                    .requestIntegrityToken(request)
                    .await()

                val token = tokenResponse.token()

                // ВАЖНО: Токен должен быть проверен на СЕРВЕРЕ
                // Клиент не может самостоятельно декодировать его
                val serverResult = verifyTokenOnServer(token, nonce)

                Result.success(serverResult)

            } catch (e: IntegrityServiceException) {
                handleIntegrityError(e)
                Result.failure(e)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    private fun generateNonce(): String {
        // В production nonce должен приходить с сервера
        val bytes = ByteArray(32)
        SecureRandom().nextBytes(bytes)
        return Base64.encodeToString(bytes, Base64.URL_SAFE or Base64.NO_WRAP)
    }

    private suspend fun verifyTokenOnServer(
        token: String,
        nonce: String
    ): IntegrityResult {
        // Отправляем токен на бэкенд для верификации
        val response = apiService.verifyIntegrity(
            VerifyIntegrityRequest(token = token, nonce = nonce)
        )

        return IntegrityResult(
            meetsDeviceIntegrity = response.deviceIntegrity,
            meetsBasicIntegrity = response.basicIntegrity,
            meetsStrongIntegrity = response.strongIntegrity,
            appLicensed = response.appLicensed,
            rawToken = token
        )
    }

    private fun handleIntegrityError(e: IntegrityServiceException) {
        when (e.errorCode) {
            IntegrityErrorCode.API_NOT_AVAILABLE -> {
                // Play Services не установлен или устарел
            }
            IntegrityErrorCode.PLAY_STORE_NOT_FOUND -> {
                // Play Store не найден (custom ROM?)
            }
            IntegrityErrorCode.NETWORK_ERROR -> {
                // Сетевая ошибка
            }
            IntegrityErrorCode.TOO_MANY_REQUESTS -> {
                // Превышена квота (10,000/день)
            }
            else -> {
                // Другие ошибки
            }
        }
    }

    companion object {
        private const val YOUR_CLOUD_PROJECT_NUMBER = 123456789L
    }
}
```

**Backend верификация (Node.js):**

```javascript
// Backend: Play Integrity Token Verification
const { google } = require('googleapis');

class PlayIntegrityVerifier {
    constructor() {
        this.playintegrity = google.playintegrity('v1');
    }

    async verifyToken(token, expectedNonce, packageName) {
        try {
            // Decode and verify token
            const response = await this.playintegrity.v1.decodeIntegrityToken({
                packageName: packageName,
                requestBody: {
                    integrityToken: token
                }
            });

            const payload = response.data.tokenPayloadExternal;

            // Verify nonce
            if (payload.requestDetails.nonce !== expectedNonce) {
                return { valid: false, reason: 'Nonce mismatch' };
            }

            // Verify timestamp (token should be recent)
            const timestamp = parseInt(payload.requestDetails.timestampMillis);
            const now = Date.now();
            const maxAge = 5 * 60 * 1000; // 5 minutes

            if (now - timestamp > maxAge) {
                return { valid: false, reason: 'Token expired' };
            }

            // Check device integrity
            const deviceIntegrity = payload.deviceIntegrity?.deviceRecognitionVerdict || [];

            const result = {
                valid: true,
                meetsDeviceIntegrity: deviceIntegrity.includes('MEETS_DEVICE_INTEGRITY'),
                meetsBasicIntegrity: deviceIntegrity.includes('MEETS_BASIC_INTEGRITY'),
                meetsStrongIntegrity: deviceIntegrity.includes('MEETS_STRONG_INTEGRITY'),
                appLicensed: payload.appLicensing?.appLicensingVerdict === 'LICENSED',
                packageName: payload.appIntegrity?.packageName,
                versionCode: payload.appIntegrity?.versionCode
            };

            // Verify package name
            if (result.packageName !== packageName) {
                return { valid: false, reason: 'Package name mismatch' };
            }

            return result;

        } catch (error) {
            console.error('Play Integrity verification failed:', error);
            return { valid: false, reason: error.message };
        }
    }
}

module.exports = PlayIntegrityVerifier;
```

### App Attest + DeviceCheck (iOS)

```
iOS Attestation Overview:

App Attest (iOS 14+):
├── Цель: Подтверждение целостности приложения
├── Механизм: Secure Enclave генерирует key pair
├── Что проверяет:
│   ├── Приложение не модифицировано
│   ├── Запущено на реальном устройстве
│   └── Подписано Apple
└── Ограничения:
    ├── Только runtime binary integrity
    └── Не защищает от runtime attacks

DeviceCheck:
├── Цель: Идентификация устройства для бизнес-логики
├── Механизм: 2 бита на device + app combo
├── Use cases:
│   ├── Отслеживание trial periods
│   ├── Fraud prevention
│   └── Device-level flags
└── Ограничения: Нет integrity checks
```

**App Attest Implementation:**

```swift
// iOS App Attest Implementation
import DeviceCheck

class AppAttestManager {

    private let attestService = DCAppAttestService.shared

    // Step 1: Check availability and generate key
    func generateAttestKey() async throws -> String {
        guard attestService.isSupported else {
            throw AttestError.notSupported
        }

        // Generate key in Secure Enclave
        let keyId = try await attestService.generateKey()

        // Store keyId securely (Keychain)
        try KeychainManager.shared.store(keyId: keyId)

        return keyId
    }

    // Step 2: Attest key with Apple
    func attestKey(keyId: String, serverChallenge: Data) async throws -> Data {
        // Create client data hash
        let clientDataHash = SHA256.hash(data: serverChallenge)
        let hashData = Data(clientDataHash)

        // Get attestation from Apple
        let attestation = try await attestService.attestKey(
            keyId,
            clientDataHash: hashData
        )

        return attestation
    }

    // Step 3: Generate assertion for API requests
    func generateAssertion(
        keyId: String,
        requestData: Data
    ) async throws -> Data {
        let clientDataHash = SHA256.hash(data: requestData)
        let hashData = Data(clientDataHash)

        let assertion = try await attestService.generateAssertion(
            keyId,
            clientDataHash: hashData
        )

        return assertion
    }

    // Full attestation flow
    func performAttestation() async throws -> AttestationResult {
        // 1. Get challenge from server
        let challenge = try await apiService.getAttestationChallenge()

        // 2. Generate or retrieve key
        let keyId: String
        if let existingKeyId = KeychainManager.shared.getKeyId() {
            keyId = existingKeyId
        } else {
            keyId = try await generateAttestKey()
        }

        // 3. Attest key
        let attestation = try await attestKey(
            keyId: keyId,
            serverChallenge: challenge
        )

        // 4. Send attestation to server for verification
        let result = try await apiService.verifyAttestation(
            keyId: keyId,
            attestation: attestation,
            challenge: challenge
        )

        return result
    }
}

enum AttestError: Error {
    case notSupported
    case keyGenerationFailed
    case attestationFailed
    case verificationFailed
}

struct AttestationResult {
    let isValid: Bool
    let deviceId: String?
    let appId: String?
}
```

**Backend Verification (Node.js):**

```javascript
// Backend: App Attest Verification
const cbor = require('cbor');
const crypto = require('crypto');
const { Certificate } = require('@peculiar/x509');

class AppAttestVerifier {
    constructor() {
        // Apple's root CA for App Attest
        this.appleRootCA = `-----BEGIN CERTIFICATE-----
        // Apple App Attestation Root CA
        -----END CERTIFICATE-----`;
    }

    async verifyAttestation(attestationBase64, keyId, clientDataHash, appId, teamId) {
        try {
            // Decode CBOR attestation
            const attestationBuffer = Buffer.from(attestationBase64, 'base64');
            const attestation = cbor.decodeFirstSync(attestationBuffer);

            // Extract components
            const { fmt, attStmt, authData } = attestation;

            if (fmt !== 'apple-appattest') {
                throw new Error('Invalid attestation format');
            }

            // Parse authenticator data
            const rpIdHash = authData.slice(0, 32);
            const flags = authData[32];
            const signCount = authData.readUInt32BE(33);
            const aaguid = authData.slice(37, 53);
            const credentialIdLength = authData.readUInt16BE(53);
            const credentialId = authData.slice(55, 55 + credentialIdLength);

            // Verify RP ID hash (SHA256 of App ID)
            const expectedAppId = `${teamId}.${appId}`;
            const expectedRpIdHash = crypto
                .createHash('sha256')
                .update(expectedAppId)
                .digest();

            if (!rpIdHash.equals(expectedRpIdHash)) {
                throw new Error('App ID mismatch');
            }

            // Verify credential ID matches keyId
            if (credentialId.toString('base64') !== keyId) {
                throw new Error('Key ID mismatch');
            }

            // Verify certificate chain
            const x5c = attStmt.x5c;
            const credCert = new Certificate(x5c[0]);

            // Verify the certificate chain leads to Apple's root CA
            await this.verifyCertificateChain(x5c);

            // Verify nonce in certificate extension
            const nonceData = this.extractNonceFromCertificate(credCert);
            const expectedNonce = crypto
                .createHash('sha256')
                .update(Buffer.concat([authData, clientDataHash]))
                .digest();

            if (!nonceData.equals(expectedNonce)) {
                throw new Error('Nonce mismatch');
            }

            // Extract public key for future assertions
            const publicKey = credCert.publicKey;

            return {
                valid: true,
                keyId: keyId,
                publicKey: publicKey,
                signCount: signCount
            };

        } catch (error) {
            console.error('Attestation verification failed:', error);
            return { valid: false, error: error.message };
        }
    }

    async verifyAssertion(assertionBase64, publicKey, clientDataHash, storedSignCount) {
        try {
            const assertionBuffer = Buffer.from(assertionBase64, 'base64');
            const assertion = cbor.decodeFirstSync(assertionBuffer);

            const { authenticatorData, signature } = assertion;

            // Verify sign count increased (replay protection)
            const signCount = authenticatorData.readUInt32BE(33);
            if (signCount <= storedSignCount) {
                throw new Error('Sign count not incremented - possible replay attack');
            }

            // Verify signature
            const signedData = Buffer.concat([authenticatorData, clientDataHash]);

            const verify = crypto.createVerify('SHA256');
            verify.update(signedData);

            const isValid = verify.verify(publicKey, signature);

            if (!isValid) {
                throw new Error('Invalid signature');
            }

            return {
                valid: true,
                newSignCount: signCount
            };

        } catch (error) {
            console.error('Assertion verification failed:', error);
            return { valid: false, error: error.message };
        }
    }

    async verifyCertificateChain(x5c) {
        // Implement certificate chain verification to Apple Root CA
        // This is simplified - use a proper PKI library in production
    }

    extractNonceFromCertificate(cert) {
        // Extract nonce from certificate extension OID 1.2.840.113635.100.8.2
        // Implementation depends on certificate parsing library
    }
}

module.exports = AppAttestVerifier;
```

---

## Secrets Protection

### Проблема hardcoded secrets

```
Statistics (2025):

iOS Apps:
├── 71% утечка минимум одного credential
├── 815,000+ secrets извлечено из 156,000 apps
└── Источник: Symantec/NowSecure research

Android Apps:
├── 56% содержат hardcoded secrets
├── Extractable через базовую автоматизацию
└── Источник: Academic research 2025

Common Leaked Secrets:
├── API keys (Google, AWS, Firebase)
├── OAuth client secrets
├── Database credentials
├── Encryption keys
├── Push notification keys
└── Third-party SDK keys
```

### Backend-for-Frontend (BFF) Pattern

```
BFF Pattern для защиты secrets:

Traditional (INSECURE):
┌──────────────┐     ┌──────────────┐
│  Mobile App  │────▶│  Third-party │
│  (API key    │     │     API      │
│   exposed)   │     │              │
└──────────────┘     └──────────────┘

BFF Pattern (SECURE):
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Mobile App  │────▶│    Your      │────▶│  Third-party │
│  (no secrets)│     │   Backend    │     │     API      │
│              │     │ (holds keys) │     │              │
└──────────────┘     └──────────────┘     └──────────────┘

Benefits:
├── Secrets никогда не покидают backend
├── Можно добавить rate limiting
├── Audit logging всех запросов
├── Легко ротировать ключи
└── Валидация и санитизация запросов
```

### Runtime Secrets Delivery

```kotlin
// Runtime secrets delivery
class SecureSecretsManager(
    private val context: Context,
    private val apiService: ApiService,
    private val attestationManager: AttestationManager
) {

    private val secretsCache = mutableMapOf<String, CachedSecret>()
    private val encryptedStorage = EncryptedSharedPreferences.create(
        context,
        "secure_secrets",
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    suspend fun getSecret(secretId: String): Result<String> {
        // Check cache first
        secretsCache[secretId]?.let { cached ->
            if (!cached.isExpired()) {
                return Result.success(cached.value)
            }
        }

        // Fetch from server with attestation
        return fetchSecretFromServer(secretId)
    }

    private suspend fun fetchSecretFromServer(secretId: String): Result<String> {
        return try {
            // Step 1: Get attestation token
            val attestationResult = attestationManager.getAttestationToken()
            if (attestationResult.isFailure) {
                return Result.failure(attestationResult.exceptionOrNull()!!)
            }

            // Step 2: Request secret with attestation
            val response = apiService.fetchSecret(
                FetchSecretRequest(
                    secretId = secretId,
                    attestationToken = attestationResult.getOrThrow(),
                    deviceFingerprint = getDeviceFingerprint()
                )
            )

            // Step 3: Decrypt secret (server sends encrypted)
            val decryptedSecret = decryptSecret(response.encryptedSecret)

            // Step 4: Cache with expiration
            secretsCache[secretId] = CachedSecret(
                value = decryptedSecret,
                expiresAt = System.currentTimeMillis() + response.ttlMs
            )

            Result.success(decryptedSecret)

        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun decryptSecret(encrypted: EncryptedPayload): String {
        // Use device-specific key from Keystore
        val secretKey = getOrCreateDecryptionKey()

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, encrypted.iv)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)

        val decrypted = cipher.doFinal(encrypted.ciphertext)
        return String(decrypted, Charsets.UTF_8)
    }

    private fun getOrCreateDecryptionKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

        val alias = "secrets_decryption_key"

        if (!keyStore.containsAlias(alias)) {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                "AndroidKeyStore"
            )

            keyGenerator.init(
                KeyGenParameterSpec.Builder(
                    alias,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
                )
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setKeySize(256)
                    .build()
            )

            keyGenerator.generateKey()
        }

        return keyStore.getKey(alias, null) as SecretKey
    }

    private fun getDeviceFingerprint(): String {
        // Generate device fingerprint for additional verification
        // Should include multiple device characteristics
        return DeviceFingerprintGenerator.generate(context)
    }

    data class CachedSecret(
        val value: String,
        val expiresAt: Long
    ) {
        fun isExpired() = System.currentTimeMillis() > expiresAt
    }

    data class EncryptedPayload(
        val ciphertext: ByteArray,
        val iv: ByteArray
    )
}
```

### Secure API Key Management

```kotlin
// Secure API key management with multiple layers
class SecureApiKeyManager(
    private val context: Context,
    private val secretsManager: SecureSecretsManager
) {

    // API keys NEVER stored in code
    // Fetched at runtime from secure backend

    suspend fun getApiKey(keyType: ApiKeyType): String {
        // Check security environment first
        val securityCheck = performSecurityChecks()
        if (!securityCheck.isPassed) {
            throw SecurityException("Security check failed: ${securityCheck.reason}")
        }

        // Get key from secrets manager
        val result = secretsManager.getSecret(keyType.secretId)

        return result.getOrThrow()
    }

    private fun performSecurityChecks(): SecurityCheckResult {
        // Check root
        val rootDetector = RootDetector(context)
        if (rootDetector.checkRoot() is RootDetector.RootStatus.Rooted) {
            return SecurityCheckResult(false, "Device is rooted")
        }

        // Check debugger
        val debuggerDetector = DebuggerDetector()
        if (debuggerDetector.isDebuggerAttached()) {
            return SecurityCheckResult(false, "Debugger detected")
        }

        // Check Frida
        val fridaDetector = FridaDetector()
        if (fridaDetector.isFridaDetected()) {
            return SecurityCheckResult(false, "Hooking framework detected")
        }

        // Check emulator
        val emulatorCheck = EmulatorDetector().detect()
        if (emulatorCheck.isEmulator && emulatorCheck.confidence > 0.8f) {
            return SecurityCheckResult(false, "Emulator detected")
        }

        return SecurityCheckResult(true, null)
    }

    enum class ApiKeyType(val secretId: String) {
        MAPS("api_key_maps"),
        ANALYTICS("api_key_analytics"),
        PUSH("api_key_push"),
        PAYMENT("api_key_payment")
    }

    data class SecurityCheckResult(
        val isPassed: Boolean,
        val reason: String?
    )
}
```

---

## Commercial Solutions

### DexGuard (Android)

```
DexGuard Features:

Code Protection:
├── Multi-layer obfuscation
├── String encryption
├── Asset/resource encryption
├── Class encryption
├── Control flow obfuscation
└── Code virtualization

Runtime Protection (RASP):
├── Root detection
├── Debugger detection
├── Emulator detection
├── Hook detection (Frida, Xposed)
├── Tampering detection
├── Repackaging detection
└── Overlay attack detection

Integration:
├── Gradle plugin
├── CI/CD compatible
├── No code changes required
└── Automatic updates

Pricing: Enterprise licensing ($$$)
```

### iXGuard (iOS)

```
iXGuard Features:

Code Protection:
├── Swift/Objective-C obfuscation
├── Bitcode obfuscation
├── String encryption
├── Control flow flattening
└── Symbol stripping

Runtime Protection:
├── Jailbreak detection
├── Debugger detection
├── Hooking detection
├── Integrity verification
└── Environment checks

Platform Support:
├── iOS
├── macOS
├── watchOS
├── tvOS
└── React Native / Flutter

Pricing: Enterprise licensing ($$$)
```

### Open Source Alternatives

```
Free/Open Source Options:

ProGuard/R8 (Android)
├── Name obfuscation only
├── Built into Android Gradle Plugin
├── Free
└── Limited protection

RootBeer (Android)
├── Root detection library
├── Open source
├── Basic checks only
└── Easily bypassed

IOSSecuritySuite (iOS)
├── Jailbreak detection
├── Debugger detection
├── Open source
└── Community maintained

Limitations:
├── Публичный код = известные bypasses
├── Нет string encryption
├── Нет control flow obfuscation
├── Нет commercial support
└── Требует постоянного обновления
```

---

## Best Practices

### Defense in Depth Strategy

```
Layered Protection Model:

Layer 1: Code Hardening (Build Time)
├── Obfuscation (DexGuard/iXGuard или R8 минимум)
├── String encryption
├── Debug code removal
└── Resource protection

Layer 2: Integrity Verification (Launch Time)
├── Signature verification
├── Installer verification
├── Checksum validation
└── Certificate pinning setup

Layer 3: Environment Checks (Runtime)
├── Root/Jailbreak detection
├── Emulator detection
├── Debugger detection
├── Hooking detection

Layer 4: Continuous Monitoring (Ongoing)
├── Anomaly detection
├── Behavior analysis
├── Server-side validation
└── Attestation refresh

Layer 5: Response (On Detection)
├── Graceful degradation
├── Feature restriction
├── Server notification
└── Data protection
```

### Response Strategies

```kotlin
// Security Response Strategy
class SecurityResponseManager(
    private val context: Context,
    private val analyticsService: AnalyticsService
) {

    enum class ThreatLevel {
        LOW,      // Logging only
        MEDIUM,   // Feature restriction
        HIGH,     // Critical feature block
        CRITICAL  // App termination
    }

    fun handleSecurityThreat(
        threat: SecurityThreat,
        level: ThreatLevel
    ) {
        // Always log
        analyticsService.logSecurityEvent(threat)

        when (level) {
            ThreatLevel.LOW -> {
                // Just log, continue normal operation
                Log.w("Security", "Low threat detected: ${threat.type}")
            }

            ThreatLevel.MEDIUM -> {
                // Disable non-critical features
                FeatureFlags.disableNonCritical()
                showSecurityWarning()
            }

            ThreatLevel.HIGH -> {
                // Disable sensitive operations
                FeatureFlags.disableSensitiveFeatures()
                clearSensitiveData()
                showSecurityAlert()
            }

            ThreatLevel.CRITICAL -> {
                // Clear all data and exit
                clearAllData()
                notifyServer(threat)
                terminateApp()
            }
        }
    }

    private fun clearSensitiveData() {
        // Clear tokens, credentials, cached secrets
        SecureStorageManager(context).clearSensitive()
    }

    private fun clearAllData() {
        // Clear all app data
        SecureStorageManager(context).clearAll()
        context.cacheDir.deleteRecursively()

        // Clear WebView data
        WebStorage.getInstance().deleteAllData()
        CookieManager.getInstance().removeAllCookies(null)
    }

    private fun notifyServer(threat: SecurityThreat) {
        // Notify backend about security incident
        // for audit and potential account protection
    }

    private fun terminateApp() {
        // Exit gracefully
        android.os.Process.killProcess(android.os.Process.myPid())
    }

    private fun showSecurityWarning() {
        // Show non-blocking warning
    }

    private fun showSecurityAlert() {
        // Show blocking alert
    }
}

data class SecurityThreat(
    val type: String,
    val details: Map<String, Any>,
    val timestamp: Long = System.currentTimeMillis()
)
```

### CI/CD Integration

```yaml
# GitHub Actions: Security Checks Pipeline

name: Mobile Security Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Secret Scanner
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}

      - name: Dependency Check
        run: ./gradlew dependencyCheckAnalyze

      - name: Static Analysis
        run: ./gradlew lint detekt

  build-protected:
    needs: security-scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Release APK
        run: ./gradlew assembleRelease
        env:
          DEXGUARD_LICENSE: ${{ secrets.DEXGUARD_LICENSE }}

      - name: MobSF Analysis
        run: |
          docker run -d -p 8000:8000 opensecurity/mobile-security-framework-mobsf
          sleep 30
          curl -F 'file=@app/build/outputs/apk/release/app-release.apk' \
               http://localhost:8000/api/v1/upload

      - name: Upload Protected APK
        uses: actions/upload-artifact@v4
        with:
          name: protected-apk
          path: app/build/outputs/apk/release/app-release.apk
```

---

## Распространённые мифы

### Миф 1: "Root detection — это надёжная защита"

```
Реальность:

Root detection ВСЕГДА обходится:
├── Magisk Hide / Shamiko / Zygisk
├── Frida scripts (публично доступны)
├── Патченные APK
└── Время bypass: минуты-часы

Root detection — это:
├── Deterrent (отпугивание)
├── Повышение планки для атакующего
├── Один слой из многих
└── НЕ единственная защита

Правильный подход:
├── Root detection + другие проверки
├── Server-side validation ОБЯЗАТЕЛЬНА
├── Sensitive logic на сервере
└── Defense in depth
```

### Миф 2: "Obfuscation делает код нечитаемым"

```
Реальность:

Что obfuscation делает:
├── Затрудняет чтение
├── Увеличивает время анализа
├── Повышает стоимость атаки

Что obfuscation НЕ делает:
├── Не скрывает алгоритмы (они в bytecode)
├── Не защищает runtime значения
├── Не предотвращает dynamic analysis
├── Не прячет network traffic

Реальность:
├── Опытный RE справится за дни
├── Automated deobfuscators существуют
├── Frida читает runtime значения
└── Business logic всё равно видна

Вывод:
├── Obfuscation необходима
├── Но недостаточна одна
├── Комбинировать с RASP
└── Критичную логику — на сервер
```

### Миф 3: "Play Integrity/App Attest защищают от всего"

```
Реальность:

Что Attestation защищает:
├── Подтверждение genuine device
├── Подтверждение app integrity (binary)
├── Подтверждение app licensing

Что Attestation НЕ защищает:
├── Runtime attacks (Frida работает)
├── Memory manipulation
├── Network interception
├── Modified rooted devices (могут пройти)

Ограничения:
├── Play Integrity: 10,000 requests/day limit
├── App Attest: не защищает runtime
├── Оба: обходимы на rooted/jailbroken
└── Требуют server-side verification

Вывод:
├── Attestation — важный слой
├── Но не единственный
├── Комбинировать с RASP
└── Server-side checks обязательны
```

### Миф 4: "Certificate Pinning достаточно для защиты API"

```
Реальность:

Что pinning защищает:
├── MitM на скомпрометированном Wi-Fi
├── Corporate proxy interception
├── Rogue CA (маловероятно)

Что pinning НЕ защищает:
├── Compromised device (Frida bypass)
├── Server-side vulnerabilities
├── API logic flaws
├── Replay attacks

Bypass методы:
├── Frida scripts (публичные)
├── Objection one-liner
├── Custom Frida gadget
└── Время bypass: минуты

Правильный подход:
├── Pinning + mutual TLS
├── Request signing
├── API rate limiting
├── Anomaly detection
└── Server-side validation
```

---

## Ресурсы

### Официальные документации

```
Platform Documentation:
├── Play Integrity: developer.android.com/google/play/integrity
├── App Attest: developer.apple.com/documentation/devicecheck
├── Android Keystore: developer.android.com/training/articles/keystore
└── iOS Keychain: developer.apple.com/documentation/security/keychain_services

OWASP:
├── MASVS: mas.owasp.org/MASVS
├── MASTG: mas.owasp.org/MASTG
└── Mobile Top 10: owasp.org/www-project-mobile-top-10
```

### Commercial Solutions

```
Enterprise Solutions:
├── Guardsquare (DexGuard, iXGuard): guardsquare.com
├── Promon SHIELD: promon.io
├── Appdome: appdome.com
├── Approov: approov.io
└── Zimperium: zimperium.com
```

### Связанные материалы

```
В базе знаний:
├── mobile-security-owasp.md — OWASP Mobile Top 10
├── mobile-security-masvs.md — MASVS & MASTG
├── security-fundamentals.md — основы безопасности
└── threat-modeling.md — моделирование угроз
```

---

## Резюме

### Ключевые выводы

```
1. Defense in Depth обязателен
   └── Ни одна мера сама по себе не достаточна

2. Server-side validation критична
   └── Клиент всегда можно скомпрометировать

3. Secrets НИКОГДА в коде
   └── Runtime delivery или BFF pattern

4. Attestation — важный слой
   └── Но не защищает от runtime attacks

5. RASP дополняет code hardening
   └── Static + dynamic protection

6. Continuous security
   └── Не разовая настройка, а процесс
```

### Quick Security Checklist

```
□ Code hardening
  ├── □ Obfuscation enabled (минимум R8)
  ├── □ Debug code removed
  └── □ Logging disabled in release

□ Runtime protection
  ├── □ Root/Jailbreak detection
  ├── □ Debugger detection
  ├── □ Hooking detection
  └── □ Emulator detection

□ Attestation
  ├── □ Play Integrity API (Android)
  ├── □ App Attest (iOS)
  └── □ Backend verification

□ Secrets management
  ├── □ No hardcoded secrets
  ├── □ Secure storage (Keystore/Keychain)
  └── □ Runtime delivery or BFF

□ Integrity
  ├── □ Signature verification
  ├── □ Certificate pinning
  └── □ Installer verification

□ Response strategy
  ├── □ Graceful degradation defined
  ├── □ Server notification on threats
  └── □ Data protection on detection
```

---

*Материал основан на актуальных практиках 2025-2026. Технологии защиты постоянно эволюционируют — следите за обновлениями платформ и security advisories.*

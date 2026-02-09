---
title: iOS Networking - URLSession и современные подходы
created: 2026-01-11
tags: [ios, networking, urlsession, async-await, codable, swift]
related: [[android-networking]]
---

## TL;DR

iOS networking построен вокруг URLSession - мощного фреймворка для HTTP-запросов. Современный подход использует async/await (iOS 15+) с Codable протоколами для type-safe сериализации. URLSession предоставляет различные конфигурации (shared, default, ephemeral, background) для разных сценариев, от простых запросов до фоновых загрузок файлов.

## Аналогии

**URLSession как почтовое отделение**: URLSessionConfiguration определяет правила работы (часы работы, политики доставки), URLRequest - это конверт с адресом и содержимым, а URLSessionTask - почтальон, доставляющий письмо. Data task доставляет короткие сообщения в память, download task - большие посылки на диск, upload task - отправка тяжелых грузов.

**Codable как переводчик**: Swift структуры говорят на языке типов, а сервер - на языке JSON. Codable автоматически переводит между ними, а CodingKeys - это словарь, где вы указываете, что "firstName" на сервере соответствует "имени" в вашем коде.

## Архитектура URLSession

```
┌─────────────────────────────────────────────────────────────┐
│                       URLSession                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Configuration │  │  Delegate    │  │  Task Queue  │      │
│  │  - timeout   │  │  - callbacks │  │  - priority  │      │
│  │  - policies  │  │  - auth      │  │  - lifecycle │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼─────┐      ┌──────▼──────┐    ┌──────▼──────┐
   │ DataTask │      │DownloadTask │    │ UploadTask  │
   │ (memory) │      │   (disk)    │    │  (stream)   │
   └──────────┘      └─────────────┘    └─────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │  URLResponse   │
                    │  - statusCode  │
                    │  - headers     │
                    └────────────────┘
```

### Типы URLSession конфигураций

```swift
// 1. Shared - singleton для простых запросов
// Ограничения: нет кастомизации, нет delegate callbacks
let sharedSession = URLSession.shared

// 2. Default - стандартная конфигурация с кешированием
// Использует дисковый кеш, куки, credentials
let defaultConfig = URLSessionConfiguration.default
defaultConfig.timeoutIntervalForRequest = 30
defaultConfig.waitsForConnectivity = true // iOS 11+
let defaultSession = URLSession(configuration: defaultConfig)

// 3. Ephemeral - без персистентного хранилища
// Для приватных режимов, sensitive data
let ephemeralConfig = URLSessionConfiguration.ephemeral
ephemeralConfig.urlCache = nil
let ephemeralSession = URLSession(configuration: ephemeralConfig)

// 4. Background - для длительных загрузок
// Работает даже когда app suspended/terminated
let backgroundConfig = URLSessionConfiguration.background(
    withIdentifier: "com.app.background-downloads"
)
backgroundConfig.isDiscretionary = true // только Wi-Fi и зарядка
backgroundConfig.sessionSendsLaunchEvents = true
let backgroundSession = URLSession(configuration: backgroundConfig)
```

## URLRequest - конфигурация запросов

```swift
import Foundation

// Базовая настройка request
var request = URLRequest(url: URL(string: "https://api.example.com/users")!)

// HTTP метод
request.httpMethod = "POST" // GET, POST, PUT, DELETE, PATCH

// Headers
request.setValue("application/json", forHTTPHeaderField: "Content-Type")
request.setValue("Bearer token123", forHTTPHeaderField: "Authorization")
request.addValue("gzip", forHTTPHeaderField: "Accept-Encoding")

// Timeout (переопределяет session timeout)
request.timeoutInterval = 60

// Caching policy
request.cachePolicy = .reloadIgnoringLocalCacheData

// Body для POST/PUT
let bodyData = try? JSONEncoder().encode(user)
request.httpBody = bodyData

// Multipart form data
let boundary = UUID().uuidString
request.setValue(
    "multipart/form-data; boundary=\(boundary)",
    forHTTPHeaderField: "Content-Type"
)
```

## Типы URLSessionTask

```
Task Lifecycle:
┌─────────┐  resume()  ┌─────────┐  completion  ┌───────────┐
│Suspended├───────────►│ Running ├─────────────►│ Completed │
└────┬────┘            └────┬────┘              └───────────┘
     │                      │
     │ cancel()             │ suspend()
     │                      │
     └──────────────────────┼──────────► ┌──────────┐
                            └───────────►│ Canceled │
                                         └──────────┘
```

### DataTask - данные в память

```swift
// Для API responses, небольших файлов (<10MB)
let task = session.dataTask(with: request) { data, response, error in
    guard let data = data,
          let httpResponse = response as? HTTPURLResponse,
          error == nil else {
        print("Error: \(error?.localizedDescription ?? "Unknown")")
        return
    }

    print("Status: \(httpResponse.statusCode)")
    // Обработка data
}
task.resume() // ВАЖНО: tasks создаются в suspended состоянии
```

### DownloadTask - файлы на диск

```swift
// Для больших файлов, поддерживает resume после прерывания
let task = session.downloadTask(with: url) { localURL, response, error in
    guard let localURL = localURL else { return }

    // localURL - временный файл, нужно переместить
    let documentsURL = FileManager.default.urls(
        for: .documentDirectory,
        in: .userDomainMask
    )[0]
    let destinationURL = documentsURL.appendingPathComponent("file.zip")

    try? FileManager.default.moveItem(at: localURL, to: destinationURL)
}

// Прогресс загрузки через delegate
task.progress.observe(\.fractionCompleted) { progress, _ in
    print("Progress: \(progress.fractionCompleted * 100)%")
}
task.resume()
```

### UploadTask - отправка данных

```swift
// Для отправки файлов, больших данных
let fileURL = URL(fileURLWithPath: "/path/to/file.jpg")

// Вариант 1: из файла
let uploadTask = session.uploadTask(
    with: request,
    fromFile: fileURL
) { data, response, error in
    // Handle response
}

// Вариант 2: из Data
let uploadTask = session.uploadTask(
    with: request,
    from: bodyData
) { data, response, error in
    // Handle response
}

uploadTask.resume()
```

## async/await с URLSession (iOS 15+)

```swift
// Современный подход вместо completion handlers

// DataTask с async/await
func fetchData() async throws -> Data {
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          (200...299).contains(httpResponse.statusCode) else {
        throw NetworkError.invalidResponse
    }

    return data
}

// С custom request
func fetchData(request: URLRequest) async throws -> Data {
    let (data, response) = try await URLSession.shared.data(for: request)

    guard let httpResponse = response as? HTTPURLResponse else {
        throw NetworkError.invalidResponse
    }

    guard httpResponse.statusCode == 200 else {
        throw NetworkError.httpError(httpResponse.statusCode)
    }

    return data
}

// Download с async/await
func downloadFile(from url: URL) async throws -> URL {
    let (localURL, response) = try await URLSession.shared.download(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.downloadFailed
    }

    // Переместить из temporary location
    let documentsURL = FileManager.default.urls(
        for: .documentDirectory,
        in: .userDomainMask
    )[0]
    let destinationURL = documentsURL.appendingPathComponent(url.lastPathComponent)
    try FileManager.default.moveItem(at: localURL, to: destinationURL)

    return destinationURL
}

// Upload с async/await
func uploadFile(data: Data, to url: URL) async throws -> Data {
    var request = URLRequest(url: url)
    request.httpMethod = "POST"

    let (responseData, response) = try await URLSession.shared.upload(
        for: request,
        from: data
    )

    guard let httpResponse = response as? HTTPURLResponse,
          (200...299).contains(httpResponse.statusCode) else {
        throw NetworkError.uploadFailed
    }

    return responseData
}
```

## Codable - Type-Safe сериализация

```
JSON Encoding/Decoding Pipeline:
┌──────────────┐   JSONEncoder   ┌──────────┐
│ Swift Struct ├────────────────►│   JSON   │
│              │◄────────────────┤  String  │
└──────────────┘   JSONDecoder   └──────────┘
       │                                │
       │ Encodable protocol             │ Decodable protocol
       │                                │
       ▼                                ▼
  encode(to:)                      init(from:)
  - encodeIfPresent()              - decode(_:forKey:)
  - encode(_:forKey:)              - decodeIfPresent(_:forKey:)
```

### Базовое использование Codable

```swift
// Codable = Encodable + Decodable
struct User: Codable {
    let id: Int
    let name: String
    let email: String
    let isActive: Bool
    let createdAt: Date
}

// Encoding: Swift → JSON
let user = User(
    id: 1,
    name: "Ivan",
    email: "ivan@example.com",
    isActive: true,
    createdAt: Date()
)

let encoder = JSONEncoder()
encoder.dateEncodingStrategy = .iso8601
encoder.outputFormatting = .prettyPrinted

let jsonData = try encoder.encode(user)
let jsonString = String(data: jsonData, encoding: .utf8)

// Decoding: JSON → Swift
let decoder = JSONDecoder()
decoder.dateDecodingStrategy = .iso8601

let decodedUser = try decoder.decode(User.self, from: jsonData)
```

### Custom CodingKeys - маппинг полей

```swift
struct User: Codable {
    let id: Int
    let firstName: String
    let lastName: String
    let emailAddress: String
    let isAdmin: Bool

    // Маппинг snake_case API → camelCase Swift
    enum CodingKeys: String, CodingKey {
        case id
        case firstName = "first_name"
        case lastName = "last_name"
        case emailAddress = "email"
        case isAdmin = "is_admin"
    }
}

// Вложенные ключи для nested JSON
struct Product: Codable {
    let id: Int
    let title: String
    let price: Double
    let currency: String

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case pricing // вложенный объект
    }

    enum PricingKeys: String, CodingKey {
        case price = "amount"
        case currency = "code"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)

        // Декодирование вложенного объекта
        let pricingContainer = try container.nestedContainer(
            keyedBy: PricingKeys.self,
            forKey: .pricing
        )
        price = try pricingContainer.decode(Double.self, forKey: .price)
        currency = try pricingContainer.decode(String.self, forKey: .currency)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(title, forKey: .title)

        var pricingContainer = container.nestedContainer(
            keyedBy: PricingKeys.self,
            forKey: .pricing
        )
        try pricingContainer.encode(price, forKey: .price)
        try pricingContainer.encode(currency, forKey: .currency)
    }
}
```

### JSONEncoder/JSONDecoder кастомизация

```swift
// Date encoding strategies
encoder.dateEncodingStrategy = .iso8601 // "2026-01-11T12:00:00Z"
encoder.dateEncodingStrategy = .millisecondsSince1970
encoder.dateEncodingStrategy = .secondsSince1970
encoder.dateEncodingStrategy = .formatted(DateFormatter())
encoder.dateEncodingStrategy = .custom { date, encoder in
    // Custom logic
}

// Data encoding strategies
encoder.dataEncodingStrategy = .base64 // default
encoder.dataEncodingStrategy = .deferredToData
encoder.dataEncodingStrategy = .custom { data, encoder in
    // Custom logic
}

// Key encoding strategies
encoder.keyEncodingStrategy = .convertToSnakeCase // camelCase → snake_case
encoder.keyEncodingStrategy = .custom { keys in
    // Custom transformation
}

// Non-conforming float strategies (NaN, Infinity)
encoder.nonConformingFloatEncodingStrategy = .convertToString(
    positiveInfinity: "inf",
    negativeInfinity: "-inf",
    nan: "null"
)

// Output formatting
encoder.outputFormatting = .prettyPrinted
encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]

// Аналогичные strategies для decoder
decoder.dateDecodingStrategy = .iso8601
decoder.keyDecodingStrategy = .convertFromSnakeCase
decoder.dataDecodingStrategy = .base64
decoder.nonConformingFloatDecodingStrategy = .convertFromString(
    positiveInfinity: "inf",
    negativeInfinity: "-inf",
    nan: "null"
)
```

## Error Handling - обработка ошибок

### URLError типы

```swift
import Foundation

// URLError.Code - enum со всеми типами ошибок
enum NetworkError: Error {
    case urlError(URLError)
    case decodingError(DecodingError)
    case httpError(Int)
    case invalidResponse
    case noData
    case unknown(Error)
}

func handleURLError(_ error: URLError) {
    switch error.code {
    // Network connectivity
    case .notConnectedToInternet:
        print("No internet connection")
    case .networkConnectionLost:
        print("Connection lost during request")
    case .cannotFindHost:
        print("Cannot resolve hostname")
    case .cannotConnectToHost:
        print("Cannot connect to server")
    case .dnsLookupFailed:
        print("DNS lookup failed")

    // Timeout errors
    case .timedOut:
        print("Request timed out")

    // SSL/TLS errors
    case .secureConnectionFailed:
        print("SSL/TLS connection failed")
    case .serverCertificateHasBadDate:
        print("Server certificate expired")
    case .serverCertificateUntrusted:
        print("Untrusted certificate")
    case .serverCertificateHasUnknownRoot:
        print("Unknown certificate authority")
    case .clientCertificateRejected:
        print("Client certificate rejected")

    // HTTP errors
    case .badServerResponse:
        print("Invalid server response")
    case .redirectToNonExistentLocation:
        print("Invalid redirect")
    case .badURL:
        print("Malformed URL")

    // File errors (download/upload)
    case .cannotWriteToFile:
        print("Cannot save file to disk")
    case .cannotOpenFile:
        print("Cannot open file")
    case .noPermissionsToReadFile:
        print("No permission to read file")

    // Request errors
    case .cancelled:
        print("Request was cancelled")
    case .userCancelledAuthentication:
        print("User cancelled auth")

    // Background session errors
    case .backgroundSessionRequiresSharedContainer:
        print("Background session needs app group")
    case .backgroundSessionInUseByAnotherProcess:
        print("Background session conflict")

    default:
        print("URLError: \(error.localizedDescription)")
    }
}
```

### HTTP Status Code обработка

```swift
extension HTTPURLResponse {
    var isSuccess: Bool {
        (200...299).contains(statusCode)
    }

    var statusCodeCategory: StatusCodeCategory {
        switch statusCode {
        case 100..<200: return .informational
        case 200..<300: return .success
        case 300..<400: return .redirection
        case 400..<500: return .clientError
        case 500..<600: return .serverError
        default: return .unknown
        }
    }
}

enum StatusCodeCategory {
    case informational // 1xx
    case success       // 2xx
    case redirection   // 3xx
    case clientError   // 4xx
    case serverError   // 5xx
    case unknown
}

// Детальная обработка кодов
func handleHTTPStatus(_ statusCode: Int) throws {
    switch statusCode {
    // Success
    case 200: break // OK
    case 201: break // Created
    case 204: break // No Content

    // Client errors
    case 400: throw NetworkError.badRequest
    case 401: throw NetworkError.unauthorized
    case 403: throw NetworkError.forbidden
    case 404: throw NetworkError.notFound
    case 422: throw NetworkError.validationFailed
    case 429: throw NetworkError.tooManyRequests

    // Server errors
    case 500: throw NetworkError.internalServerError
    case 502: throw NetworkError.badGateway
    case 503: throw NetworkError.serviceUnavailable
    case 504: throw NetworkError.gatewayTimeout

    default:
        if (400..<500).contains(statusCode) {
            throw NetworkError.clientError(statusCode)
        } else if (500..<600).contains(statusCode) {
            throw NetworkError.serverError(statusCode)
        }
    }
}
```

## Authentication - аутентификация

### Basic Authentication

```swift
// HTTP Basic Auth: username:password → Base64
func createBasicAuthRequest(
    url: URL,
    username: String,
    password: String
) -> URLRequest {
    var request = URLRequest(url: url)

    let credentials = "\(username):\(password)"
    guard let credentialsData = credentials.data(using: .utf8) else {
        return request
    }

    let base64Credentials = credentialsData.base64EncodedString()
    request.setValue(
        "Basic \(base64Credentials)",
        forHTTPHeaderField: "Authorization"
    )

    return request
}
```

### Bearer Token Authentication

```swift
// OAuth 2.0, JWT tokens
func createBearerTokenRequest(url: URL, token: String) -> URLRequest {
    var request = URLRequest(url: url)
    request.setValue(
        "Bearer \(token)",
        forHTTPHeaderField: "Authorization"
    )
    return request
}

// Token refresh logic
actor TokenManager {
    private var currentToken: String?
    private var tokenExpirationDate: Date?
    private var refreshTask: Task<String, Error>?

    func getValidToken() async throws -> String {
        // Если есть задача на обновление, ждем её
        if let refreshTask = refreshTask {
            return try await refreshTask.value
        }

        // Если токен валиден, возвращаем его
        if let token = currentToken,
           let expirationDate = tokenExpirationDate,
           Date() < expirationDate {
            return token
        }

        // Создаем задачу на обновление токена
        let task = Task<String, Error> {
            let newToken = try await refreshToken()
            self.currentToken = newToken
            self.tokenExpirationDate = Date().addingTimeInterval(3600) // 1 hour
            self.refreshTask = nil
            return newToken
        }

        refreshTask = task
        return try await task.value
    }

    private func refreshToken() async throws -> String {
        // API call to refresh token
        let url = URL(string: "https://api.example.com/auth/refresh")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw NetworkError.refreshFailed
        }

        let tokenResponse = try JSONDecoder().decode(
            TokenResponse.self,
            from: data
        )
        return tokenResponse.accessToken
    }
}

struct TokenResponse: Codable {
    let accessToken: String
    let expiresIn: Int
}
```

### URLSession Authentication Challenge

```swift
// Для более сложных схем аутентификации
class AuthenticatedSessionDelegate: NSObject, URLSessionDelegate {
    let credentials: URLCredential

    init(username: String, password: String) {
        self.credentials = URLCredential(
            user: username,
            password: password,
            persistence: .forSession
        )
    }

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodHTTPBasic {
            completionHandler(.useCredential, credentials)
        } else {
            completionHandler(.performDefaultHandling, nil)
        }
    }
}

// Использование
let delegate = AuthenticatedSessionDelegate(
    username: "user",
    password: "pass"
)
let session = URLSession(
    configuration: .default,
    delegate: delegate,
    delegateQueue: nil
)
```

## SSL Pinning - защита от MITM атак

```swift
// Certificate Pinning - проверка сертификата сервера
class SSLPinningDelegate: NSObject, URLSessionDelegate {
    let pinnedCertificates: [SecCertificate]

    init(certificateNames: [String]) {
        var certificates: [SecCertificate] = []

        for name in certificateNames {
            if let certPath = Bundle.main.path(
                forResource: name,
                ofType: "cer"
            ),
               let certData = try? Data(contentsOf: URL(fileURLWithPath: certPath)),
               let certificate = SecCertificateCreateWithData(
                nil,
                certData as CFData
               ) {
                certificates.append(certificate)
            }
        }

        self.pinnedCertificates = certificates
    }

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard challenge.protectionSpace.authenticationMethod ==
                NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Получаем сертификат сервера
        guard let serverCertificate = SecTrustGetCertificateAtIndex(
            serverTrust,
            0
        ) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Проверяем, совпадает ли с pinned сертификатами
        let serverCertificateData = SecCertificateCopyData(
            serverCertificate
        ) as Data

        for pinnedCert in pinnedCertificates {
            let pinnedCertData = SecCertificateCopyData(pinnedCert) as Data

            if serverCertificateData == pinnedCertData {
                let credential = URLCredential(trust: serverTrust)
                completionHandler(.useCredential, credential)
                return
            }
        }

        // Сертификат не совпал
        completionHandler(.cancelAuthenticationChallenge, nil)
    }
}

// Public Key Pinning - более гибкий подход
class PublicKeyPinningDelegate: NSObject, URLSessionDelegate {
    let pinnedPublicKeyHashes: Set<String>

    init(publicKeyHashes: [String]) {
        self.pinnedPublicKeyHashes = Set(publicKeyHashes)
    }

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard challenge.protectionSpace.authenticationMethod ==
                NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Извлекаем public key из сертификата
        guard let serverCertificate = SecTrustGetCertificateAtIndex(
            serverTrust,
            0
        ),
              let serverPublicKey = SecCertificateCopyKey(serverCertificate),
              let serverPublicKeyData = SecKeyCopyExternalRepresentation(
                serverPublicKey,
                nil
              ) as Data? else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Вычисляем SHA256 hash
        let hash = serverPublicKeyData.sha256Hash()

        if pinnedPublicKeyHashes.contains(hash) {
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}

extension Data {
    func sha256Hash() -> String {
        var hash = [UInt8](repeating: 0, count: Int(CC_SHA256_DIGEST_LENGTH))
        self.withUnsafeBytes {
            _ = CC_SHA256($0.baseAddress, CC_LONG(self.count), &hash)
        }
        return hash.map { String(format: "%02x", $0) }.joined()
    }
}
```

## Background Downloads - фоновые загрузки

```swift
// Background downloads продолжаются даже когда app не запущен
class BackgroundDownloadManager: NSObject, URLSessionDownloadDelegate {
    static let shared = BackgroundDownloadManager()

    private var session: URLSession!
    private var completionHandlers: [String: () -> Void] = [:]

    private override init() {
        super.init()

        let config = URLSessionConfiguration.background(
            withIdentifier: "com.app.background-downloads"
        )
        config.isDiscretionary = false // загружать сразу, не ждать Wi-Fi
        config.sessionSendsLaunchEvents = true

        session = URLSession(
            configuration: config,
            delegate: self,
            delegateQueue: nil
        )
    }

    func downloadFile(from url: URL) {
        let task = session.downloadTask(with: url)
        task.resume()
    }

    // AppDelegate должен вызвать при background completion
    func setBackgroundCompletionHandler(_ handler: @escaping () -> Void) {
        completionHandlers[session.configuration.identifier!] = handler
    }

    // MARK: - URLSessionDownloadDelegate

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        // Переместить файл из временной директории
        let documentsURL = FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        )[0]

        let fileName = downloadTask.originalRequest?.url?.lastPathComponent ?? "file"
        let destinationURL = documentsURL.appendingPathComponent(fileName)

        try? FileManager.default.removeItem(at: destinationURL)
        try? FileManager.default.moveItem(at: location, to: destinationURL)

        print("Downloaded to: \(destinationURL)")
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didWriteData bytesWritten: Int64,
        totalBytesWritten: Int64,
        totalBytesExpectedToWrite: Int64
    ) {
        let progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite)
        print("Progress: \(progress * 100)%")

        // Обновить UI через notification
        NotificationCenter.default.post(
            name: .downloadProgress,
            object: nil,
            userInfo: ["progress": progress, "taskIdentifier": downloadTask.taskIdentifier]
        )
    }

    func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didCompleteWithError error: Error?
    ) {
        if let error = error {
            print("Download error: \(error.localizedDescription)")
        }

        // Вызвать completion handler от системы
        if let identifier = session.configuration.identifier,
           let handler = completionHandlers[identifier] {
            completionHandlers.removeValue(forKey: identifier)
            DispatchQueue.main.async {
                handler()
            }
        }
    }
}

// В AppDelegate или SceneDelegate
func application(
    _ application: UIApplication,
    handleEventsForBackgroundURLSession identifier: String,
    completionHandler: @escaping () -> Void
) {
    BackgroundDownloadManager.shared.setBackgroundCompletionHandler(
        completionHandler
    )
}

extension Notification.Name {
    static let downloadProgress = Notification.Name("downloadProgress")
}
```

## Network Reachability - мониторинг соединения

```swift
import Network

// NWPathMonitor (iOS 12+) - современная замена Reachability
@Observable
class NetworkMonitor {
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "NetworkMonitor")

    var isConnected: Bool = false
    var connectionType: ConnectionType = .unknown
    var isExpensive: Bool = false
    var isConstrained: Bool = false

    enum ConnectionType {
        case wifi
        case cellular
        case wiredEthernet
        case unknown
    }

    init() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isConnected = path.status == .satisfied
                self?.isExpensive = path.isExpensive
                self?.isConstrained = path.isConstrained

                if path.usesInterfaceType(.wifi) {
                    self?.connectionType = .wifi
                } else if path.usesInterfaceType(.cellular) {
                    self?.connectionType = .cellular
                } else if path.usesInterfaceType(.wiredEthernet) {
                    self?.connectionType = .wiredEthernet
                } else {
                    self?.connectionType = .unknown
                }
            }
        }
    }

    func startMonitoring() {
        monitor.start(queue: queue)
    }

    func stopMonitoring() {
        monitor.cancel()
    }
}

// Использование в SwiftUI
struct ContentView: View {
    @State private var networkMonitor = NetworkMonitor()

    var body: some View {
        VStack {
            if networkMonitor.isConnected {
                Text("Connected via \(networkMonitor.connectionType)")
                    .foregroundColor(.green)

                if networkMonitor.isExpensive {
                    Text("Expensive connection (cellular)")
                        .foregroundColor(.orange)
                }
            } else {
                Text("No internet connection")
                    .foregroundColor(.red)
            }
        }
        .onAppear {
            networkMonitor.startMonitoring()
        }
        .onDisappear {
            networkMonitor.stopMonitoring()
        }
    }
}

// Использование для условных запросов
class APIClient {
    private let networkMonitor = NetworkMonitor()

    func fetchData() async throws -> Data {
        guard networkMonitor.isConnected else {
            throw NetworkError.noConnection
        }

        // Если соединение дорогое, использовать кеш
        if networkMonitor.isExpensive {
            if let cachedData = loadFromCache() {
                return cachedData
            }
        }

        // Обычный запрос
        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }
}
```

## Production-Ready API Client

```swift
import Foundation
import Combine

// MARK: - Endpoint Protocol

protocol Endpoint {
    var baseURL: URL { get }
    var path: String { get }
    var method: HTTPMethod { get }
    var headers: [String: String]? { get }
    var parameters: [String: Any]? { get }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}

extension Endpoint {
    var urlRequest: URLRequest {
        let url = baseURL.appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue

        // Headers
        headers?.forEach { request.setValue($1, forHTTPHeaderField: $0) }

        // Parameters
        if let parameters = parameters {
            if method == .get {
                // Query parameters для GET
                var components = URLComponents(url: url, resolvingAgainstBaseURL: false)
                components?.queryItems = parameters.map {
                    URLQueryItem(name: $0.key, value: "\($0.value)")
                }
                request.url = components?.url
            } else {
                // Body для POST/PUT/PATCH
                request.httpBody = try? JSONSerialization.data(
                    withJSONObject: parameters
                )
                request.setValue(
                    "application/json",
                    forHTTPHeaderField: "Content-Type"
                )
            }
        }

        return request
    }
}

// MARK: - API Error

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(Int, Data?)
    case decodingError(DecodingError)
    case encodingError(EncodingError)
    case noData
    case underlying(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Неверный URL"
        case .invalidResponse:
            return "Некорректный ответ сервера"
        case .httpError(let statusCode, _):
            return "HTTP ошибка: \(statusCode)"
        case .decodingError(let error):
            return "Ошибка декодирования: \(error.localizedDescription)"
        case .encodingError(let error):
            return "Ошибка кодирования: \(error.localizedDescription)"
        case .noData:
            return "Нет данных в ответе"
        case .underlying(let error):
            return error.localizedDescription
        }
    }
}

// MARK: - Network Logger

protocol NetworkLogger {
    func logRequest(_ request: URLRequest)
    func logResponse(_ response: URLResponse?, data: Data?, error: Error?)
}

class ConsoleNetworkLogger: NetworkLogger {
    func logRequest(_ request: URLRequest) {
        print("🌐 REQUEST: \(request.httpMethod ?? "") \(request.url?.absoluteString ?? "")")
        if let headers = request.allHTTPHeaderFields {
            print("📋 Headers: \(headers)")
        }
        if let body = request.httpBody,
           let bodyString = String(data: body, encoding: .utf8) {
            print("📦 Body: \(bodyString)")
        }
    }

    func logResponse(_ response: URLResponse?, data: Data?, error: Error?) {
        if let error = error {
            print("❌ ERROR: \(error.localizedDescription)")
            return
        }

        guard let httpResponse = response as? HTTPURLResponse else { return }

        let statusEmoji = (200..<300).contains(httpResponse.statusCode) ? "✅" : "⚠️"
        print("\(statusEmoji) RESPONSE: \(httpResponse.statusCode)")

        if let data = data,
           let responseString = String(data: data, encoding: .utf8) {
            print("📦 Response: \(responseString)")
        }
    }
}

// MARK: - API Client

actor APIClient {
    static let shared = APIClient()

    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    private let logger: NetworkLogger?
    private let tokenManager: TokenManager

    init(
        configuration: URLSessionConfiguration = .default,
        logger: NetworkLogger? = ConsoleNetworkLogger(),
        tokenManager: TokenManager = TokenManager()
    ) {
        self.session = URLSession(configuration: configuration)
        self.logger = logger
        self.tokenManager = tokenManager

        // Configure decoder
        self.decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        decoder.keyDecodingStrategy = .convertFromSnakeCase

        // Configure encoder
        self.encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.keyEncodingStrategy = .convertToSnakeCase
    }

    // MARK: - Request Methods

    func request<T: Decodable>(
        _ endpoint: Endpoint,
        authenticated: Bool = true
    ) async throws -> T {
        var request = endpoint.urlRequest

        // Add auth token if needed
        if authenticated {
            let token = try await tokenManager.getValidToken()
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        logger?.logRequest(request)

        do {
            let (data, response) = try await session.data(for: request)

            logger?.logResponse(response, data: data, error: nil)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }

            guard (200...299).contains(httpResponse.statusCode) else {
                throw APIError.httpError(httpResponse.statusCode, data)
            }

            do {
                let decodedData = try decoder.decode(T.self, from: data)
                return decodedData
            } catch let error as DecodingError {
                throw APIError.decodingError(error)
            }
        } catch let error as URLError {
            logger?.logResponse(nil, data: nil, error: error)
            throw APIError.underlying(error)
        } catch {
            logger?.logResponse(nil, data: nil, error: error)
            throw error
        }
    }

    func requestWithoutResponse(
        _ endpoint: Endpoint,
        authenticated: Bool = true
    ) async throws {
        var request = endpoint.urlRequest

        if authenticated {
            let token = try await tokenManager.getValidToken()
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        logger?.logRequest(request)

        let (data, response) = try await session.data(for: request)

        logger?.logResponse(response, data: data, error: nil)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode, data)
        }
    }

    func upload<T: Decodable>(
        _ endpoint: Endpoint,
        data: Data,
        authenticated: Bool = true
    ) async throws -> T {
        var request = endpoint.urlRequest

        if authenticated {
            let token = try await tokenManager.getValidToken()
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        logger?.logRequest(request)

        let (responseData, response) = try await session.upload(for: request, from: data)

        logger?.logResponse(response, data: responseData, error: nil)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode, responseData)
        }

        do {
            return try decoder.decode(T.self, from: responseData)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        }
    }

    func download(
        _ endpoint: Endpoint,
        authenticated: Bool = true,
        progressHandler: ((Double) -> Void)? = nil
    ) async throws -> URL {
        var request = endpoint.urlRequest

        if authenticated {
            let token = try await tokenManager.getValidToken()
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        logger?.logRequest(request)

        let (localURL, response) = try await session.download(for: request)

        logger?.logResponse(response, data: nil, error: nil)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode, nil)
        }

        return localURL
    }
}

// MARK: - Example API Endpoints

enum UserAPI {
    case getUsers
    case getUser(id: Int)
    case createUser(name: String, email: String)
    case updateUser(id: Int, name: String)
    case deleteUser(id: Int)
}

extension UserAPI: Endpoint {
    var baseURL: URL {
        URL(string: "https://api.example.com/v1")!
    }

    var path: String {
        switch self {
        case .getUsers:
            return "/users"
        case .getUser(let id):
            return "/users/\(id)"
        case .createUser:
            return "/users"
        case .updateUser(let id, _):
            return "/users/\(id)"
        case .deleteUser(let id):
            return "/users/\(id)"
        }
    }

    var method: HTTPMethod {
        switch self {
        case .getUsers, .getUser:
            return .get
        case .createUser:
            return .post
        case .updateUser:
            return .put
        case .deleteUser:
            return .delete
        }
    }

    var headers: [String: String]? {
        ["Accept": "application/json"]
    }

    var parameters: [String: Any]? {
        switch self {
        case .createUser(let name, let email):
            return ["name": name, "email": email]
        case .updateUser(_, let name):
            return ["name": name]
        default:
            return nil
        }
    }
}

// MARK: - Models

struct User: Codable, Identifiable {
    let id: Int
    let name: String
    let email: String
    let createdAt: Date
    let isActive: Bool
}

struct UserResponse: Codable {
    let users: [User]
    let total: Int
    let page: Int
}

// MARK: - Repository

protocol UserRepository {
    func fetchUsers() async throws -> [User]
    func fetchUser(id: Int) async throws -> User
    func createUser(name: String, email: String) async throws -> User
    func updateUser(id: Int, name: String) async throws -> User
    func deleteUser(id: Int) async throws
}

final class RemoteUserRepository: UserRepository {
    private let apiClient = APIClient.shared

    func fetchUsers() async throws -> [User] {
        let response: UserResponse = try await apiClient.request(
            UserAPI.getUsers
        )
        return response.users
    }

    func fetchUser(id: Int) async throws -> User {
        try await apiClient.request(UserAPI.getUser(id: id))
    }

    func createUser(name: String, email: String) async throws -> User {
        try await apiClient.request(
            UserAPI.createUser(name: name, email: email)
        )
    }

    func updateUser(id: Int, name: String) async throws -> User {
        try await apiClient.request(
            UserAPI.updateUser(id: id, name: name)
        )
    }

    func deleteUser(id: Int) async throws {
        try await apiClient.requestWithoutResponse(
            UserAPI.deleteUser(id: id)
        )
    }
}

// MARK: - ViewModel Usage

@MainActor
@Observable
class UsersViewModel {
    private let repository: UserRepository

    var users: [User] = []
    var isLoading = false
    var errorMessage: String?

    init(repository: UserRepository = RemoteUserRepository()) {
        self.repository = repository
    }

    func loadUsers() async {
        isLoading = true
        errorMessage = nil

        do {
            users = try await repository.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func createUser(name: String, email: String) async {
        isLoading = true
        errorMessage = nil

        do {
            let newUser = try await repository.createUser(
                name: name,
                email: email
            )
            users.append(newUser)
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}
```

## 6 типичных ошибок

### ❌ Ошибка 1: Забывают вызвать resume()

```swift
// НЕПРАВИЛЬНО - task создан но не запущен
let task = URLSession.shared.dataTask(with: url) { data, response, error in
    print(data)
}
// Task в состоянии .suspended, запрос не отправляется
```

### ✅ Правильно: Всегда вызывать resume()

```swift
let task = URLSession.shared.dataTask(with: url) { data, response, error in
    print(data)
}
task.resume() // Запускает выполнение task

// Или с async/await (resume не нужен)
let (data, _) = try await URLSession.shared.data(from: url)
```

---

### ❌ Ошибка 2: Не проверяют HTTP status code

```swift
// НЕПРАВИЛЬНО - только проверка error
let (data, response) = try await URLSession.shared.data(from: url)
if data != nil {
    let users = try JSONDecoder().decode([User].self, from: data)
    // Может быть 404, 500, но error == nil
}
```

### ✅ Правильно: Проверка статуса ответа

```swift
let (data, response) = try await URLSession.shared.data(from: url)

guard let httpResponse = response as? HTTPURLResponse else {
    throw NetworkError.invalidResponse
}

guard (200...299).contains(httpResponse.statusCode) else {
    throw NetworkError.httpError(httpResponse.statusCode)
}

let users = try JSONDecoder().decode([User].self, from: data)
```

---

### ❌ Ошибка 3: Используют shared session с delegate

```swift
// НЕПРАВИЛЬНО - shared session не поддерживает delegate
class MyDelegate: NSObject, URLSessionDelegate {
    // ...
}

let delegate = MyDelegate()
URLSession.shared.delegate = delegate // delegate всегда nil для shared
```

### ✅ Правильно: Создать custom session

```swift
class MyDelegate: NSObject, URLSessionDelegate {
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        // Handle authentication
    }
}

let delegate = MyDelegate()
let session = URLSession(
    configuration: .default,
    delegate: delegate,
    delegateQueue: nil
)
```

---

### ❌ Ошибка 4: Неправильная обработка background downloads

```swift
// НЕПРАВИЛЬНО - сохраняют файл из completion handler
let task = session.downloadTask(with: url) { localURL, response, error in
    guard let localURL = localURL else { return }
    // localURL удаляется сразу после completion
    DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
        // Файл уже удален!
        self.processFile(at: localURL)
    }
}
```

### ✅ Правильно: Немедленное перемещение файла

```swift
let task = session.downloadTask(with: url) { localURL, response, error in
    guard let localURL = localURL else { return }

    let documentsURL = FileManager.default.urls(
        for: .documentDirectory,
        in: .userDomainMask
    )[0]
    let destinationURL = documentsURL.appendingPathComponent("file.zip")

    // Переместить СРАЗУ
    try? FileManager.default.moveItem(at: localURL, to: destinationURL)

    // Теперь можно обрабатывать асинхронно
    DispatchQueue.main.async {
        self.processFile(at: destinationURL)
    }
}
```

---

### ❌ Ошибка 5: Декодируют без обработки ошибок

```swift
// НЕПРАВИЛЬНО - crash при изменении API
struct User: Codable {
    let id: Int
    let name: String
    let email: String
    let phoneNumber: String // Новое required поле
}

let user = try! JSONDecoder().decode(User.self, from: data)
// Crash если сервер не вернул phoneNumber
```

### ✅ Правильно: Optional поля и обработка ошибок

```swift
struct User: Codable {
    let id: Int
    let name: String
    let email: String
    let phoneNumber: String? // Optional для новых полей

    // Или default значения
    let isActive: Bool

    enum CodingKeys: String, CodingKey {
        case id, name, email, phoneNumber, isActive
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        email = try container.decode(String.self, forKey: .email)
        phoneNumber = try? container.decode(String.self, forKey: .phoneNumber)
        isActive = (try? container.decode(Bool.self, forKey: .isActive)) ?? true
    }
}

// Обработка ошибок декодирования
do {
    let user = try JSONDecoder().decode(User.self, from: data)
} catch let DecodingError.keyNotFound(key, context) {
    print("Missing key: \(key.stringValue)")
    print("Context: \(context.debugDescription)")
} catch let DecodingError.typeMismatch(type, context) {
    print("Type mismatch for type: \(type)")
    print("Context: \(context.debugDescription)")
} catch {
    print("Decoding error: \(error)")
}
```

---

### ❌ Ошибка 6: Race condition при refresh token

```swift
// НЕПРАВИЛЬНО - multiple requests refresh token одновременно
class TokenManager {
    var currentToken: String?

    func getValidToken() async throws -> String {
        if let token = currentToken {
            return token
        }

        // Если 10 requests одновременно, будет 10 refresh calls!
        let newToken = try await refreshToken()
        currentToken = newToken
        return newToken
    }
}
```

### ✅ Правильно: Actor с single refresh task

```swift
actor TokenManager {
    private var currentToken: String?
    private var refreshTask: Task<String, Error>?

    func getValidToken() async throws -> String {
        // Если уже refreshing, ждем тот же task
        if let refreshTask = refreshTask {
            return try await refreshTask.value
        }

        // Если токен валиден, возвращаем
        if let token = currentToken {
            return token
        }

        // Создаем ОДИН task для refresh
        let task = Task<String, Error> {
            let newToken = try await self.refreshToken()
            self.currentToken = newToken
            self.refreshTask = nil
            return newToken
        }

        refreshTask = task
        return try await task.value
    }

    private func refreshToken() async throws -> String {
        // Actual refresh logic
        let url = URL(string: "https://api.example.com/auth/refresh")!
        let (data, _) = try await URLSession.shared.data(from: url)
        let response = try JSONDecoder().decode(TokenResponse.self, from: data)
        return response.accessToken
    }
}
```

## Сравнение с Android

| Аспект | iOS (URLSession) | Android (Retrofit/OkHttp) |
|--------|------------------|---------------------------|
| **Базовый фреймворк** | URLSession (system framework) | OkHttp (library) |
| **API стиль** | Protocol-oriented, async/await | Interface-based, Coroutines/RxJava |
| **Type safety** | Codable protocols | Gson/Moshi/kotlinx.serialization |
| **Configuration** | URLSessionConfiguration | OkHttpClient.Builder |
| **Interceptors** | URLProtocol (сложнее) | Interceptor interface (проще) |
| **SSL Pinning** | Delegate-based | CertificatePinner API |
| **Caching** | URLCache (встроен) | Cache (настраивается) |
| **Background** | Background sessions | WorkManager (отдельно) |
| **Reactive** | Combine | RxJava/Flow |
| **Mock/Testing** | URLProtocol, mock URLSession | MockWebServer, Hilt |

Детальное сравнение см. [[android-networking]]

---

## Дополнительные ресурсы

- [Apple URLSession Documentation](https://developer.apple.com/documentation/foundation/urlsession)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Codable Documentation](https://developer.apple.com/documentation/swift/codable)
- [Network Framework](https://developer.apple.com/documentation/network)
- [App Transport Security](https://developer.apple.com/documentation/security/preventing_insecure_network_connections)

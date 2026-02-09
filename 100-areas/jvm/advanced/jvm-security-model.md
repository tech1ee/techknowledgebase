---
title: "JVM Security Model - Модель безопасности Java"
created: 2025-11-25
modified: 2026-01-02
tags:
  - topic/jvm
  - topic/security
  - securitymanager
  - permissions
  - sandbox
  - deprecated
  - docker
  - kubernetes
  - type/concept
  - level/advanced
type: concept
status: published
area: programming
confidence: high
sources:
  - "https://openjdk.org/jeps/411"
  - "https://openjdk.org/jeps/486"
  - "https://snyk.io/blog/securitymanager-removed-java/"
  - "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/SecurityManager.html"
related:
  - "[[jvm-class-loader-deep-dive]]"
  - "[[docker-for-developers]]"
  - "[[kubernetes-basics]]"
---

# JVM Security Model - Модель безопасности

## Prerequisites (Что нужно знать перед изучением)

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| **Базовый Java** | Понимание classloader, exceptions | Любой курс по Java |
| **Основы безопасности** | Угрозы, атаки, защита | Security basics |
| **Docker/Kubernetes** | Современные альтернативы | [[docker-for-developers]] |
| **Reflection API** | Как SecurityManager проверял доступ | [[jvm-reflection-api]] |

---

## Почему изучать deprecated технологию?

### Аналогия: SecurityManager как музейный экспонат

> **Представьте:** SecurityManager — это как старый замок на двери. В 1995 году это была лучшая защита. Сегодня есть сигнализация (контейнеры), видеонаблюдение (мониторинг), охрана на уровне здания (OS security). Замок всё ещё работает, но он deprecated — новые здания строят без него, используя современные системы.

### Зачем знать deprecated SecurityManager?

1. **Legacy код** — многие системы ещё используют его
2. **Миграция** — понимание что и на что заменять
3. **История** — понимание эволюции Java security
4. **JEP 411/486** — официальная документация требует знания контекста

---

## Терминология для новичков

| Термин | Что это простыми словами | Аналогия |
|--------|-------------------------|----------|
| **SecurityManager** | Охранник, проверяющий права доступа | Охрана на входе в офис |
| **Permission** | Разрешение на действие | Пропуск в определённую зону |
| **Policy** | Набор правил безопасности | Устав охранной службы |
| **Sandbox** | Ограниченная среда для недоверенного кода | Песочница для детей (безопасно играть) |
| **Stack Inspection** | Проверка всех вызывающих методов | Проверка всех кто открывал дверь до вас |
| **Protection Domain** | Группа кода с одинаковыми правами | Отдел в офисе (все имеют одинаковый доступ) |
| **Applet** | Java код в браузере (deprecated) | Flash/JavaScript в браузере |
| **Privileged Action** | Действие с повышенными правами | Временный VIP-пропуск |
| **Container Isolation** | Изоляция на уровне ОС | Отдельное здание вместо комнаты |
| **Static Analysis** | Проверка кода до запуска | Рентген багажа в аэропорту |

---

## История SecurityManager

### Timeline: Жизнь и смерть SecurityManager

```
1995          2009          2017          2018          2021          2024
  │             │             │             │             │             │
  ▼             ▼             ▼             ▼             ▼             ▼
Java 1.0      Java 6       Java 9        Java 11      Java 17      Java 24
Security     "Peak"        Applets      Applets       JEP 411     JEP 486
Manager     Usage         deprecated   removed       SM depr.    SM disabled
born                                                 @Deprecated  permanently
  │             │             │             │             │             │
  └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
                              │
              ┌───────────────┴───────────────┐
              │  Причины deprecation:          │
              │  • Applets мертвы              │
              │  • 190% overhead               │
              │  • Редко использовался         │
              │  • Контейнеры лучше           │
              └───────────────────────────────┘
```

### Ключевые даты

**1995: Java 1.0** — SecurityManager создан для applets
> *"SecurityManager был частью Java Platform с самого начала — JDK 1.0."*
> — JEP 411

**2017: Java 9 (JEP 398)** — Applet API deprecated
> *"Угроза вредоносного удалённого кода отступила, потому что Java Platform больше не поддерживает applets."*

**2021: Java 17 (JEP 411)** — SecurityManager deprecated for removal
> *"Он не был основным средством защиты клиентского Java кода много лет, редко использовался для защиты серверного кода, и дорого его поддерживать."*

**2024: Java 24 (JEP 486)** — SecurityManager permanently disabled
> *"Разработчики не смогут включить его, и классы Platform не будут на него ссылаться."*

---

## TL;DR

**SecurityManager** — механизм безопасности Java для контроля доступа недоверенного кода. **Deprecated в Java 17, удалён в Java 21+** из-за низкого использования, overhead производительности и появления лучших альтернатив.

**Исторические концепции:**
- **SecurityManager** — точка принятия решений о доступе к ресурсам
- **Permissions** — иерархия разрешений (FilePermission, SocketPermission)
- **Policy файлы** — конфигурация разрешений для кода
- **Protection Domains** — группировка кода с одинаковыми правами

**Почему deprecated:**
- ❌ Редко использовался (только для applets, которые тоже deprecated)
- ❌ Overhead производительности до 190% (почти 3x медленнее)
- ❌ Сложная конфигурация (policy файлы трудно писать корректно)
- ✅ Лучшие альтернативы (контейнеры Docker/K8s, OS изоляция)

**Современные альтернативы:**
- Container sandboxing (Docker, Kubernetes Pod Security)
- Process isolation (запуск недоверенного кода в отдельных процессах)
- Static analysis (проверка кода до запуска)
- OS-level security (seccomp, AppArmor, SELinux)

---

## Проблема: Запуск недоверенного кода

### Оригинальный use case: Java Applets (1995-2017)

**Сценарий:**
1. Пользователь открывает веб-страницу
2. Браузер скачивает Java applet (небольшое Java приложение)
3. Applet автоматически запускается в браузере
4. **Проблема:** Applet может быть вредоносным!

**Что мог сделать вредоносный applet:**
- Удалить файлы пользователя
- Украсть пароли и личные данные
- Отправить данные злоумышленнику
- Установить вирус

**Решение:** SecurityManager блокировал опасные операции:

```java
// Вредоносный applet пытается удалить файлы
public class MaliciousApplet {
    public void init() {
        File home = new File(System.getProperty("user.home"));
        home.delete();  // ❌ ЗАБЛОКИРОВАНО!
    }
}

// SecurityManager выбрасывает исключение:
// java.security.AccessControlException: access denied
//   ("java.io.FilePermission" "/home/user" "delete")
```

**Почему эта модель провалилась:**
- Applets не стали популярными (Flash и JavaScript победили)
- Браузеры перестали поддерживать Java плагин (2015-2017)
- SecurityManager стал ненужным багажом в JVM

---

## Архитектура Security Model

### Компоненты

```
┌──────────────────────────────────────────────┐
│  Java код пытается выполнить операцию        │
│  Пример: new FileInputStream("/etc/passwd")  │
└──────────────────┬───────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────┐
│  SecurityManager.checkRead("/etc/passwd")    │
│  Проверяет: есть ли разрешение?              │
└──────────────────┬───────────────────────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
   НЕТ РАЗРЕШЕНИЯ      ЕСТЬ РАЗРЕШЕНИЕ
         │                    │
         ↓                    ↓
  AccessControlException   Операция выполнена
  (блокировка)
```

**Ключевые компоненты:**

1. **SecurityManager** — точка принятия решений
   - `checkRead(file)` — проверить чтение файла
   - `checkWrite(file)` — проверить запись
   - `checkConnect(host, port)` — проверить сетевое подключение
   - `checkExec(cmd)` — проверить запуск команды

2. **Permissions** — объекты разрешений
   - `FilePermission` — файловые операции
   - `SocketPermission` — сетевые операции
   - `RuntimePermission` — системные операции

3. **Policy** — набор правил из policy файлов
   - Определяет какой код какие разрешения имеет
   - Основано на codebase (откуда загружен код)

4. **Protection Domain** — группа кода с одинаковыми правами
   - Каждый класс принадлежит одному protection domain
   - Domain имеет набор permissions

### Stack Inspection — проверка всего стека вызовов

SecurityManager проверял **весь стек вызовов**, не только непосредственного caller:

```
Call stack:
  UntrustedCode.readFile()         [НЕТ file permission]
    → TrustedLibrary.doRead()      [ЕСТЬ file permission]
      → FileInputStream.open()
        → SecurityManager.checkRead()

Логика: Если хоть ОДИН caller в стеке не имеет права → DENIED
```

**Почему так работало:**
- Защита от атак через библиотеки
- Недоверенный код не может "подкупить" доверенную библиотеку

**Проблема:** Огромный overhead — проверка стека на каждой операции!

---

## Permissions (система разрешений)

### Иерархия разрешений

```java
// FilePermission — файловые операции
FilePermission("/home/user/data.txt", "read")        // Чтение файла
FilePermission("/home/user/*", "read,write")         // Все файлы в директории
FilePermission("/home/user/-", "read,write,delete")  // Рекурсивно все файлы
FilePermission("<<ALL FILES>>", "read")              // ВСЕ файлы системы

// SocketPermission — сетевые операции
SocketPermission("example.com:80", "connect")        // HTTP подключение
SocketPermission("*:1024-", "accept,connect")        // Любой хост, порты 1024+
SocketPermission("*:*", "connect,resolve")           // Любой хост и порт

// RuntimePermission — системные операции
RuntimePermission("createClassLoader")               // Создать ClassLoader
RuntimePermission("exitVM")                          // Завершить JVM
RuntimePermission("setSecurityManager")              // Поменять SecurityManager
```

### Implications (импликации разрешений)

**Важная концепция:** одно разрешение может *implies* другое (быть сильнее).

```
FilePermission("/home/user/*", "read,write")
  implies (включает в себя)
FilePermission("/home/user/file.txt", "read")
```

**Примеры импликаций:**
- `<<ALL FILES>>` implies любой конкретный файл
- `/home/user/-` (рекурсивно) implies `/home/user/subdir/file.txt`
- `*:*` (любой хост:порт) implies `example.com:80`

**Почему важно:**
- SecurityManager при проверке учитывает импликации
- Достаточно иметь более широкое разрешение

---

## Policy Files (конфигурация)

Policy файлы определяют разрешения для кода:

```
// java.policy
grant codeBase "file:/home/user/myapp.jar" {
    // Разрешить чтение своей директории
    permission java.io.FilePermission "/home/user/*", "read";

    // Разрешить подключение к API
    permission java.net.SocketPermission "api.example.com:443", "connect";
};

grant codeBase "file:/untrusted/*" {
    // Недоверенный код может только читать /tmp
    permission java.io.FilePermission "/tmp/-", "read";

    // Никаких сетевых подключений
    // (отсутствие SocketPermission = запрет)
};

// Доверенный код — все разрешения
grant codeBase "file:/system/lib/*" {
    permission java.security.AllPermission;
};
```

**Запуск с policy:**

```bash
java -Djava.security.manager \
     -Djava.security.policy=/path/to/my.policy \
     MyApp
```

**Проблемы:**
- Синтаксис сложный и подверженный ошибкам
- Трудно предсказать какие разрешения нужны
- Одна ошибка = либо незащищённость, либо неработающее приложение

---

## Почему SecurityManager deprecated

### Причина 1: Низкое использование

**Факты:**
- 95%+ Java приложений никогда не использовали SecurityManager
- Основной use case (applets) deprecated с 2017
- Большинство разработчиков не знают как им пользоваться

### Причина 2: Огромный overhead производительности

**Benchmark:**

```java
// Тест: 1 млн операций file.canRead()
// БЕЗ SecurityManager:  145 ms
// С SecurityManager:    420 ms
// Overhead: +190% (почти 3x медленнее!)
```

**Почему такой overhead:**
- Stack inspection на каждой операции
- Проверка permissions на каждом вызове
- Невозможно оптимизировать JIT компилятором

### Причина 3: Сложность конфигурации

```
// Пример реальной ошибки конфигурации
grant {
    permission java.io.FilePermission "<<ALL FILES>>", "read,write";
    // Ой! Мы дали ВСЕ права, а хотели только /tmp
    // SecurityManager есть, но защиты НЕТ
};
```

### Причина 4: Лучшие альтернативы

**Современные подходы более эффективны:**
- Контейнеры (Docker) изолируют на уровне ОС
- Kubernetes Pod Security Standards
- Process isolation (отдельный процесс для недоверенного кода)
- Static analysis (находит проблемы до запуска)

---

## Современные альтернативы

### 1. Container Sandboxing (Docker/Kubernetes)

**Docker с ограничениями:**

```dockerfile
FROM openjdk:21-slim

# Non-root пользователь
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Read-only root filesystem
# Приложение НЕ может изменять систему
CMD ["java", "-jar", "app.jar"]
```

```bash
# Запуск с ограничениями
docker run --rm \
  --read-only \                    # Read-only filesystem
  --memory="512m" \                # Лимит памяти
  --cpus="0.5" \                   # Лимит CPU
  --network=none \                 # Без сети
  --security-opt=no-new-privileges \
  myapp
```

**Kubernetes Pod Security:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: restricted-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
```

**Преимущества:**
- ✅ Изоляция на уровне ОС (kernel namespaces, cgroups)
- ✅ Нет overhead производительности
- ✅ Стандартная индустриальная практика
- ✅ Защита от всего приложения, не только Java кода

### 2. Process Isolation

**Запуск недоверенного кода в отдельном процессе:**

```java
/**
 * Запуск untrusted кода в изолированном процессе с ограничениями.
 */
public class ProcessSandbox {

    public static String runUntrusted(String javaCode) throws Exception {
        // 1. Записать код во временный файл
        Path tempFile = Files.createTempFile("untrusted", ".java");
        Files.writeString(tempFile, javaCode);

        // 2. Скомпилировать
        Process compiler = new ProcessBuilder("javac", tempFile.toString()).start();
        if (compiler.waitFor() != 0) {
            throw new RuntimeException("Compilation failed");
        }

        // 3. Запустить с лимитами (Linux)
        String className = tempFile.getFileName().toString().replace(".java", "");

        ProcessBuilder runner = new ProcessBuilder(
            "timeout", "5s",        // 5 секунд максимум
            "java",
            "-Xmx64m",              // 64MB памяти максимум
            "-cp", tempFile.getParent().toString(),
            className
        );

        // 4. Захватить output
        Process process = runner.start();
        String output = new String(process.getInputStream().readAllBytes());

        // 5. Cleanup
        process.destroyForcibly();
        Files.delete(tempFile);

        return output;
    }
}
```

**Преимущества:**
- ✅ Полная изоляция (отдельный process = нельзя повредить родителя)
- ✅ Лимиты на CPU, память, время
- ✅ Если untrusted код крашится — родитель не пострадает

### 3. Static Analysis

**Проверка кода ДО запуска:**

```java
// Checker Framework — проверка null safety
import org.checkerframework.checker.nullness.qual.*;

public class UserService {
    // Гарантия: метод никогда не вернёт null
    public @NonNull String getUserName(@NonNull User user) {
        return user.getName();
    }

    // Может вернуть null
    public @Nullable String findUser(int id) {
        User user = database.find(id);
        return user != null ? user.getName() : null;
    }

    public void process() {
        User user = getUser();
        String name = getUserName(user);  // OK

        User maybe = findUser(123);
        String name2 = getUserName(maybe);  // COMPILE ERROR!
        // "incompatible types: @Nullable User cannot be converted to @NonNull User"
    }
}
```

**Преимущества:**
- ✅ Находит проблемы на этапе компиляции
- ✅ Нет runtime overhead
- ✅ Предотвращает целые классы ошибок (NPE, injection)

---

## Migration Guide (миграция от SecurityManager)

### Удаление SecurityManager из кода

**Было (до Java 17):**

```java
// Установка SecurityManager
System.setSecurityManager(new SecurityManager());

// Проверка разрешений
SecurityManager sm = System.getSecurityManager();
if (sm != null) {
    sm.checkRead("/etc/passwd");
}

// Privileged action
AccessController.doPrivileged((PrivilegedAction<Void>) () -> {
    System.loadLibrary("native");
    return null;
});
```

**Стало (Java 21+):**

```java
// 1. Удалить setSecurityManager
// Метод deprecated, не делает ничего

// 2. Удалить checkPermission вызовы
// Просто удаляем проверки

// 3. Убрать doPrivileged
// Просто вызываем код напрямую
System.loadLibrary("native");  // Работает без doPrivileged
```

### Замена на современные подходы

**Вместо файловых разрешений → контейнеры:**

```bash
# Было: policy файл с FilePermission
# Стало: Docker с read-only filesystem
docker run --read-only --tmpfs /tmp myapp
```

**Вместо сетевых разрешений → Network Policies:**

```yaml
# Kubernetes Network Policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

---

## Чек-лист

### Если используете SecurityManager (миграция)
- [ ] Проверить почему используется (может не нужен?)
- [ ] Задокументировать требования безопасности
- [ ] Выбрать альтернативу (контейнеры, process isolation, static analysis)
- [ ] Удалить `System.setSecurityManager()`
- [ ] Удалить `SecurityManager.check*()` вызовы
- [ ] Удалить `AccessController.doPrivileged()`
- [ ] Удалить policy файлы
- [ ] Протестировать без SecurityManager

### Для новых проектов
- [ ] НЕ использовать SecurityManager (deprecated)
- [ ] Использовать контейнеры для изоляции
- [ ] Применять принцип наименьших привилегий
- [ ] Запускать с non-root пользователем
- [ ] Использовать static analysis (Checker Framework, SpotBugs)
- [ ] Настроить security scanning в CI/CD

---

## Связанные темы

- [[jvm-class-loader-deep-dive]] — загрузка классов и security
- [[jvm-bytecode-manipulation]] — проверка байткода
- [[docker-for-developers]] — контейнерная безопасность
- [[kubernetes-basics]] — K8s security standards

---

**Резюме:** SecurityManager был решением проблемы 1995 года (Java applets). Сегодня он deprecated и удалён из Java 21+. Современные альтернативы (контейнеры, OS изоляция, static analysis) более эффективны и проще в использовании. Для новых проектов используйте Docker/Kubernetes security features вместо SecurityManager.

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "SecurityManager защищает от всех атак" | SecurityManager защищал только от **Java-кода** атак. Нативный код (JNI), OS уязвимости, сетевые атаки — вне его контроля. Это была лишь часть defense-in-depth |
| "SecurityManager всё ещё работает в Java 21+" | В Java 21 он **deprecated for removal**, в Java 24 **полностью отключён**. Попытка использовать `System.setSecurityManager()` выбросит исключение |
| "Без SecurityManager Java небезопасна" | Современная безопасность — контейнеры (Docker), OS isolation (seccomp), принцип наименьших привилегий, static analysis. Они эффективнее чем in-process песочница |
| "Policy файлы были удобны для настройки" | Policy синтаксис был **крайне неудобным**: grant/permission/codeBase с regex-подобными patterns. Ошибки приводили к runtime failures, сложно дебажить |
| "AccessController.doPrivileged() безопасен" | doPrivileged() — **опасный API**. Он повышает привилегии, что открывает путь для privilege escalation атак. Код внутри doPrivileged должен быть минимальным и проверенным |
| "Applet sandbox была хорошей моделью" | Applet sandbox провалилась: бесконечные CVE, escape-уязвимости, невозможность обновить все клиенты. Браузеры удалили поддержку плагинов именно из-за проблем безопасности |
| "Контейнеры менее безопасны чем SecurityManager" | Контейнеры изолируют на **уровне OS**: namespaces, cgroups, seccomp. Это hardware-backed изоляция vs software-only sandbox в одном процессе |
| "SecurityManager нужен для multi-tenant приложений" | Multi-tenant изоляция в 2025: отдельные processes/containers, Kubernetes namespaces, service mesh policies. In-process isolation через SecurityManager — устаревший подход |
| "Без SecurityManager нельзя ограничить file access" | OS-уровень: read-only файловые системы, AppArmor/SELinux policies, container volume mounts с ограниченными правами. Это надёжнее Java-based ограничений |
| "Код на Java безопасен по умолчанию" | Java защищает от buffer overflow (bounds checking), memory corruption (GC). Но SQL injection, XSS, десериализация, dependency vulnerabilities — ответственность разработчика |

---

## CS-фундамент

| CS-концепция | Применение в Security Model |
|--------------|----------------------------|
| **Principle of Least Privilege** | Центральный принцип: давать только минимально необходимые права. SecurityManager пытался реализовать это через permissions. Сегодня — через контейнеры и IAM |
| **Sandboxing** | Изоляция недоверенного кода. SecurityManager был in-process sandbox для Java applets. Современные sandbox'ы: WebAssembly, gVisor, Firecracker |
| **Stack Inspection** | SecurityManager проверял весь call stack для определения привилегий. Каждый caller должен был иметь нужное permission. AccessController.doPrivileged() обрезал проверку |
| **Defense in Depth** | Несколько слоёв защиты: OS security + container isolation + network policies + application security + code scanning. SecurityManager был только одним слоём |
| **Trust Boundaries** | Границы доверия: код из интернета vs локальный код. SecurityManager различал codeSource для назначения permissions. В containers: trust boundary на границе контейнера |
| **Access Control Lists (ACL)** | Policy файлы — форма ACL: principal (code source) → permissions (file read, network connect). Современные ACL: Kubernetes RBAC, cloud IAM |
| **Process Isolation** | OS-уровень изоляция процессов надёжнее in-process. Один crash/exploit не влияет на другие процессы. Containers используют namespace isolation |
| **Static Analysis** | Альтернатива runtime проверкам: SpotBugs, Checker Framework, Semgrep находят уязвимости до запуска. Это shift-left security — проблемы фиксим раньше |
| **Bytecode Verification** | JVM verifier проверяет bytecode на type safety и stack consistency при загрузке. Это осталось после deprecation SecurityManager — базовая защита от malformed class files |
| **Capability-based Security** | Модель где доступ определяется наличием capability (token/reference), а не identity. SecurityManager был более ACL-based. Capabilities считаются более безопасным подходом |

---

## Источники

1. [JEP 411: Deprecate the Security Manager for Removal](https://openjdk.org/jeps/411) — Официальное обоснование deprecation
2. [JEP 486: Permanently Disable the Security Manager](https://openjdk.org/jeps/486) — Окончательное отключение в Java 24
3. [Snyk: SecurityManager Removed from Java](https://snyk.io/blog/securitymanager-removed-java/) — Практическое руководство по миграции
4. [Oracle: SecurityManager Javadoc (Java 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/SecurityManager.html) — Официальная документация

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

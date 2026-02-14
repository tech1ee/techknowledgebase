---
title: "JVM Security Model - Модель безопасности Java"
created: 2025-11-25
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/security
  - securitymanager
  - permissions
  - sandbox
  - deprecated
  - topic/docker
  - topic/kubernetes
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
reading_time: 18
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[jvm-basics-history]]"
  - "[[jvm-class-loader-deep-dive]]"
  - "[[jvm-module-system]]"
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

> **Аналогия из жизни: цепочка поручительств в банке.** Представьте, что вы хотите получить доступ к банковской ячейке. Банк проверяет не только ваш паспорт, но и всю цепочку людей, которые привели вас сюда: кто вас рекомендовал, кто рекомендовал рекомендателя и так далее. Если хоть один человек в цепочке не имеет нужного уровня доверия — доступ запрещён. Именно так работал Stack Inspection: SecurityManager проверял каждый вызывающий метод в стеке, и если хоть один caller не имел нужного permission — вся операция блокировалась. А `doPrivileged()` — это как если бы доверенный сотрудник банка сказал: «Дальше проверять не нужно, я беру ответственность на себя».

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

## Связь с другими темами

**[[jvm-class-loader-deep-dive]]** — ClassLoader и SecurityManager исторически были тесно связаны: каждый класс принадлежал Protection Domain, определяемому его ClassLoader'ом и code source. ClassLoader определял «откуда загружен код» (local disk, network, JAR), а SecurityManager на основе этого назначал permissions. Хотя SecurityManager deprecated, понимание этой связи важно для legacy-кода и для осознания того, почему ClassLoader в Java — это не просто механизм загрузки классов, а элемент security-архитектуры.

**[[docker-for-developers]]** — Docker-контейнеры стали основной заменой SecurityManager для изоляции Java-приложений. Контейнеры обеспечивают изоляцию на уровне OS (Linux namespaces, cgroups, seccomp), что надёжнее in-process песочницы SecurityManager. При миграции от SecurityManager к контейнерам файловые permissions заменяются на read-only filesystem, сетевые permissions — на network policies, а ограничения ресурсов — на cgroups лимиты. Рекомендуется изучить Docker security features (USER, --read-only, --cap-drop) как прямую замену policy файлов.

**[[kubernetes-basics]]** — Kubernetes Pod Security Standards и Network Policies обеспечивают security на уровне оркестрации, заменяя централизованные policy-файлы SecurityManager. Pod Security admission controller контролирует, какие capabilities доступны контейнеру (аналог RuntimePermission), Network Policies ограничивают сетевой доступ (аналог SocketPermission), а RBAC управляет доступом к API ресурсам. Для production Java-приложений комбинация Kubernetes security + container hardening обеспечивает более надёжную защиту, чем SecurityManager когда-либо предоставлял.

---

## Источники и дальнейшее чтение

- Oaks S. (2001). *Java Security*, 2nd Edition. — Историческое руководство по Java Security Model: SecurityManager, AccessController, policy files. Ценно для понимания legacy-систем и контекста, в котором создавалась модель безопасности Java.
- Bloch J. (2018). *Effective Java*, 3rd Edition. — Item 85 «Prefer alternatives to Java serialization» и другие items по безопасности показывают современный подход к security в Java без SecurityManager.
- McLaughlin D. (2018). *Java Security: Writing and Deploying Secure Applications*. — Обзор эволюции Java security от applets до контейнеров, включая практические рекомендации по миграции от SecurityManager к современным альтернативам.
- OpenJDK (2021). *JEP 411: Deprecate the Security Manager for Removal*. — Официальное обоснование deprecation с анализом причин (низкое использование, overhead, сложность) и рекомендациями по альтернативам.
- OpenJDK (2024). *JEP 486: Permanently Disable the Security Manager*. — Финальное решение об отключении SecurityManager в Java 24, описание migration path и влияния на существующий код.

---

## Проверь себя

> [!question]- Почему контейнерная изоляция (Docker) считается более надёжной, чем in-process sandbox SecurityManager?
> SecurityManager работал внутри того же процесса, что и защищаемый код — это software-only sandbox. Если обнаруживалась уязвимость в JVM (а таких CVE были десятки), недоверенный код мог обойти SecurityManager. Docker-контейнеры используют kernel-level изоляцию: Linux namespaces (отдельное представление файловой системы, сети, процессов), cgroups (лимиты ресурсов), seccomp (фильтрация системных вызовов). Это hardware-backed изоляция на уровне ОС, которую обойти значительно сложнее. Кроме того, контейнеры защищают от любого кода (JNI, native libraries), а SecurityManager контролировал только Java-код.

> [!question]- Сценарий: вы унаследовали legacy-приложение на Java 11, которое использует System.setSecurityManager() и AccessController.doPrivileged(). Вам нужно мигрировать на Java 21. Опишите план миграции
> 1. Провести аудит использования SecurityManager: найти все вызовы setSecurityManager(), checkPermission(), doPrivileged() и policy-файлы. 2. Задокументировать требования безопасности: какие ресурсы защищались (файлы, сеть, системные вызовы). 3. Удалить System.setSecurityManager() — в Java 21 метод deprecated и не работает. 4. Удалить все SecurityManager.check*() вызовы и AccessController.doPrivileged() — заменить прямыми вызовами. 5. Удалить policy-файлы. 6. Заменить файловые ограничения на Docker read-only filesystem и volume mounts. 7. Заменить сетевые ограничения на Kubernetes Network Policies. 8. Запустить интеграционные тесты без SecurityManager. 9. Применить принцип наименьших привилегий через контейнерную конфигурацию (non-root user, drop ALL capabilities).

> [!question]- В чём заключалась проблема performance overhead SecurityManager и почему JIT-компилятор не мог её решить?
> SecurityManager выполнял stack inspection на каждой security-sensitive операции (чтение файла, сетевое подключение, создание ClassLoader). Stack inspection означает обход всего call stack для проверки, что каждый caller имеет нужное permission. Overhead составлял до 190% (почти 3x замедление). JIT-компилятор не мог оптимизировать эти проверки, потому что: (1) результат зависит от runtime call stack, который различен при каждом вызове; (2) permissions могут меняться динамически через policy refresh; (3) doPrivileged() обрезает проверку стека в произвольных точках, что делает inline невозможным.

> [!question]- Почему модель безопасности через Applet sandbox провалилась, и какие уроки из этого можно извлечь для современного дизайна систем?
> Applet sandbox провалилась по нескольким причинам: (1) бесконечные CVE — sandbox-escape уязвимости находили регулярно, потому что in-process изоляция фундаментально ненадёжна; (2) невозможность обновить клиентов — у пользователей стояли устаревшие JRE; (3) сложность policy-конфигурации — ошибки приводили либо к нерабочему приложению, либо к отсутствию защиты; (4) Flash и JavaScript победили как платформы для браузерного контента. Уроки: предпочитать изоляцию на уровне ОС, а не внутри процесса; автоматические обновления security-компонентов; defense in depth вместо единственного слоя защиты; простота конфигурации безопасности снижает вероятность ошибок.

---

## Ключевые карточки

SecurityManager — что это и в каком состоянии сейчас?
?
Механизм контроля доступа в Java, проверявший permissions при security-sensitive операциях. Deprecated в Java 17 (JEP 411), полностью отключён в Java 24 (JEP 486). Основной use case (applets) исчез, overhead до 190%, лучшие альтернативы в виде контейнеров.

Как работал Stack Inspection в SecurityManager?
?
При каждой security-sensitive операции SecurityManager обходил весь call stack, проверяя, что каждый caller имеет нужное permission. Если хоть один вызывающий метод в стеке не имел разрешения — операция блокировалась. AccessController.doPrivileged() позволял обрезать проверку стека в доверенном коде.

Какие три основных компонента составляли модель безопасности Java?
?
1) SecurityManager — точка принятия решений (check-методы для файлов, сети, системных вызовов). 2) Permissions — иерархия разрешений (FilePermission, SocketPermission, RuntimePermission) с системой импликаций. 3) Policy — конфигурационные файлы, определяющие какой код (по codeBase) какие permissions имеет.

Чем заменить SecurityManager в современных Java-приложениях?
?
Четыре основных альтернативы: 1) Container sandboxing — Docker с read-only filesystem, ограничениями памяти, CPU и сети. 2) Kubernetes Pod Security — runAsNonRoot, drop ALL capabilities, seccompProfile. 3) Process isolation — запуск недоверенного кода в отдельном процессе с лимитами. 4) Static analysis — проверка кода до запуска (Checker Framework, SpotBugs, Semgrep).

Почему overhead SecurityManager составлял до 190%?
?
Stack inspection на каждой security-sensitive операции: обход всего call stack, проверка permissions для каждого caller, невозможность оптимизации JIT-компилятором (результат зависит от runtime stack, permissions могут меняться динамически, doPrivileged() обрезает стек в произвольных точках).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубление | [[jvm-class-loader-deep-dive]] | Понять связь ClassLoader и Protection Domain в security-архитектуре |
| Углубление | [[jvm-module-system]] | JPMS как замена access control SecurityManager через модульную инкапсуляцию |
| Практика | [[jvm-reflection-api]] | Понять как SecurityManager ограничивал reflective access и setAccessible() |
| Кросс-область | [[docker-for-developers]] | Контейнерная изоляция как основная замена SecurityManager |
| Навигация | [[jvm-overview]] | Вернуться к обзору JVM-тем |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

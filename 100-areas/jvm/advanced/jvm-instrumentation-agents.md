---
title: "JVM Instrumentation & Agents - Модификация байткода в runtime"
tags: [java, jvm, agents, instrumentation, bytecode, apm, javaagent, monitoring, profiling]
sources: [java-instrumentation-api, jvmti-spec, asm-guide, agent-best-practices]
confidence: 4
date: 2025-11-25
---

# JVM Instrumentation & Agents

## TL;DR

**Java агенты** — это программы, которые модифицируют байткод классов **в runtime** через API `java.lang.instrument`. Позволяют добавлять логику без изменения исходного кода.

**Ключевые концепции:**
- **Premain-агенты** — загружаются при старте JVM (`-javaagent:agent.jar`)
- **Agentmain-агенты** — подключаются к работающей JVM (dynamic attach)
- **ClassFileTransformer** — перехватывает загрузку классов и модифицирует байткод
- **APM-инструменты** (New Relic, DataDog, Dynatrace) построены на этой технологии

**Когда использовать:**
- ✅ Application Performance Monitoring (APM)
- ✅ Code coverage (JaCoCo, Cobertura)
- ✅ Профайлеры (YourKit, JProfiler)
- ✅ Aspect-Oriented Programming (AspectJ)
- ✅ Hot reload / live debugging
- ❌ Сложная бизнес-логика (используйте обычный код)
- ❌ Когда достаточно annotation processors

---

## Проблема: Модификация поведения без изменения кода

### Традиционный подход

**Без агента — дублирование кода:**
```java
public class UserService {
    public User getUser(Long id) {
        long start = System.nanoTime();
        try {
            return userRepository.findById(id);
        } finally {
            MetricsCollector.record("getUser", System.nanoTime() - start);
        }
    }

    // 50+ методов с идентичным boilerplate...
}
```

**С агентом — чистый код, инструментация автоматическая:**
```java
public class UserService {
    public User getUser(Long id) {
        return userRepository.findById(id);
    }
}

// java -javaagent:monitor-agent.jar -jar app.jar
// Агент автоматически добавляет timing во все методы
```

---

## Архитектура Java Agents

### Жизненный цикл агента

```
java -javaagent:agent.jar -jar application.jar
          │
          ↓
   ┌──────────────────┐
   │ JVM загружает    │
   │ агент JAR        │
   └────────┬─────────┘
            │
            ↓
   ┌─────────────────────────────┐
   │ Вызов метода premain()      │
   │   public static void        │
   │   premain(String args,      │
   │            Instrumentation) │
   └────────┬────────────────────┘
            │
            ↓
   ┌──────────────────────────────┐
   │ Регистрация трансформера:    │
   │ inst.addTransformer(...)     │
   └────────┬─────────────────────┘
            │
            ↓
   ┌─────────────────────────────────┐
   │ При загрузке каждого класса:    │
   │ 1. ClassLoader читает .class    │
   │ 2. Трансформер перехватывает    │
   │ 3. Модифицирует байткод         │
   │ 4. Возвращает новые байты       │
   │ 5. JVM создаёт класс            │
   └─────────────────────────────────┘
```

### Типы агентов

**Premain-агент (startup):**
```java
public class MonitoringAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        System.out.println("Agent started: " + agentArgs);
        inst.addTransformer(new PerformanceTransformer());
    }
}
```

**Agentmain-агент (dynamic attach):**
```java
public class MonitoringAgent {
    public static void agentmain(String agentArgs, Instrumentation inst) {
        System.out.println("Agent attached to running JVM");
        // true = можно retransform уже загруженных классов
        inst.addTransformer(new PerformanceTransformer(), true);
    }
}
```

---

## Instrumentation API

### Основной интерфейс

```java
package java.lang.instrument;

public interface Instrumentation {
    // Добавить трансформер для новых классов
    void addTransformer(ClassFileTransformer transformer);

    // С возможностью retransform
    void addTransformer(ClassFileTransformer transformer, boolean canRetransform);

    // Удалить трансформер
    boolean removeTransformer(ClassFileTransformer transformer);

    // Retransform уже загруженных классов
    void retransformClasses(Class<?>... classes);

    // Получить все загруженные классы
    Class[] getAllLoadedClasses();

    // Размер объекта в памяти
    long getObjectSize(Object obj);
}
```

### ClassFileTransformer

```java
public interface ClassFileTransformer {
    /**
     * @param loader       ClassLoader, загружающий класс
     * @param className    Имя класса (e.g., "java/lang/String")
     * @param classfileBuffer Оригинальный байткод
     * @return Модифицированный байткод, или null если не трансформируем
     */
    byte[] transform(
        ClassLoader loader,
        String className,
        Class<?> classBeingRedefined,
        ProtectionDomain protectionDomain,
        byte[] classfileBuffer
    ) throws IllegalClassFormatException;
}
```

---

## Создание простого агента

### Шаг 1: Класс агента

```java
public class SimpleAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        System.out.println("=== Agent Started ===");
        inst.addTransformer(new SimpleTransformer());
    }

    static class SimpleTransformer implements ClassFileTransformer {
        @Override
        public byte[] transform(ClassLoader loader, String className,
                              Class<?> redefined, ProtectionDomain domain,
                              byte[] classfileBuffer) {

            // Фильтр: трансформируем только свои классы
            if (className == null || !className.startsWith("com/example/app")) {
                return null;  // Не трансформируем
            }

            System.out.println("Transforming: " + className);

            // Здесь модификация байткода через ASM
            return modifyBytecode(classfileBuffer);
        }
    }
}
```

### Шаг 2: MANIFEST.MF

```
Manifest-Version: 1.0
Premain-Class: com.example.agent.SimpleAgent
Agent-Class: com.example.agent.SimpleAgent
Can-Retransform-Classes: true
Can-Redefine-Classes: true
Boot-Class-Path: asm-9.5.jar
```

### Шаг 3: Запуск

```bash
# Собрать агент
mvn clean package

# Запустить приложение с агентом
java -javaagent:target/agent.jar -jar application.jar

# С аргументами
java -javaagent:agent.jar=debug=true,port=8080 -jar app.jar
```

---

## Модификация байткода с ASM

### Базовая структура трансформера

```java
public class PerformanceTransformer implements ClassFileTransformer {

    @Override
    public byte[] transform(ClassLoader loader, String className,
                          Class<?> redefined, ProtectionDomain domain,
                          byte[] classfileBuffer) {

        if (!shouldTransform(className)) {
            return null;
        }

        try {
            ClassReader reader = new ClassReader(classfileBuffer);
            ClassWriter writer = new ClassWriter(reader,
                ClassWriter.COMPUTE_FRAMES);

            // Visitor добавляет timing в методы
            ClassVisitor visitor = new PerformanceClassVisitor(writer);
            reader.accept(visitor, ClassReader.EXPAND_FRAMES);

            return writer.toByteArray();
        } catch (Exception e) {
            e.printStackTrace();
            return null; // Возвращаем null = используем оригинальный класс
        }
    }
}
```

### Результат трансформации

**Оригинальный метод:**
```java
public User getUser(Long id) {
    return userRepository.findById(id);
}
```

**После трансформации (декомпилированный):**
```java
public User getUser(Long id) {
    long startTime = System.nanoTime();
    try {
        return userRepository.findById(id);
    } finally {
        long duration = System.nanoTime() - startTime;
        MetricsCollector.record("UserService", "getUser", duration);
    }
}
```

---

## Dynamic Attach API

### Подключение к работающей JVM

```java
import com.sun.tools.attach.*;

public class DynamicAttacher {
    public static void main(String[] args) throws Exception {
        // Список всех работающих JVM
        for (VirtualMachineDescriptor desc : VirtualMachine.list()) {
            System.out.printf("PID: %s, Name: %s%n",
                desc.id(), desc.displayName());
        }

        // Подключение к конкретной JVM
        String pid = args[0];
        String agentPath = args[1];

        VirtualMachine vm = VirtualMachine.attach(pid);
        try {
            vm.loadAgent(agentPath, "runtime-args");
            System.out.println("Agent loaded successfully");
        } finally {
            vm.detach();
        }
    }
}
```

**Использование:**
```bash
# Найти процесс
jps -l
# Output: 12345 com.example.Application

# Подключить агент
java -cp .:$JAVA_HOME/lib/tools.jar DynamicAttacher 12345 agent.jar
```

---

## Retransformation

### Перезагрузка уже загруженных классов

```java
public class ReloadableAgent {
    private static Instrumentation instrumentation;

    public static void agentmain(String args, Instrumentation inst) {
        instrumentation = inst;
        inst.addTransformer(new HotSwapTransformer(), true);
    }

    // Вызывается через JMX или HTTP endpoint
    public static void reloadClass(String className) throws Exception {
        Class<?> clazz = Class.forName(className);

        if (!instrumentation.isModifiableClass(clazz)) {
            throw new IllegalStateException("Not modifiable: " + className);
        }

        instrumentation.retransformClasses(clazz);
        System.out.println("Retransformed: " + className);
    }

    // Перезагрузить все классы пакета
    public static void reloadPackage(String packagePrefix) throws Exception {
        List<Class<?>> classes = new ArrayList<>();

        for (Class<?> clazz : instrumentation.getAllLoadedClasses()) {
            if (clazz.getName().startsWith(packagePrefix) &&
                instrumentation.isModifiableClass(clazz)) {
                classes.add(clazz);
            }
        }

        instrumentation.retransformClasses(classes.toArray(new Class[0]));
        System.out.println("Retransformed " + classes.size() + " classes");
    }
}
```

---

## APM Agent Architecture

### Структура коммерческих APM

**Как работают New Relic, DataDog, Dynatrace:**

```
┌──────────────────────────────────────┐
│ Application JVM                      │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Bootstrap Agent (premain)      │  │
│ │ - Инжектирует фреймворк        │  │
│ └─────────┬──────────────────────┘  │
│           │                          │
│ ┌─────────▼──────────────────────┐  │
│ │ Instrumentation Modules        │  │
│ │ • JDBC → перехват DB queries   │  │
│ │ • HTTP → перехват requests     │  │
│ │ • Spring → @Controller         │  │
│ │ • Redis → cache operations     │  │
│ └─────────┬──────────────────────┘  │
│           │                          │
│ ┌─────────▼──────────────────────┐  │
│ │ Data Collection                │  │
│ │ - Transaction traces           │  │
│ │ - Error tracking               │  │
│ │ - Metrics buffering            │  │
│ └─────────┬──────────────────────┘  │
│           │                          │
│ ┌─────────▼──────────────────────┐  │
│ │ Reporter (background thread)   │  │
│ │ - Batch send every 60s         │  │
│ └─────────┬──────────────────────┘  │
└───────────┼──────────────────────────┘
            │ HTTPS
            ↓
    ┌──────────────┐
    │ APM Backend  │
    │ (Cloud SaaS) │
    └──────────────┘
```

### Упрощённый APM агент

```java
public class SimpleAPMAgent {
    private static final MetricsCollector metrics = new MetricsCollector();

    public static void premain(String args, Instrumentation inst) {
        // Фоновый reporter
        startReporter();

        // Трансформеры для разных слоёв
        inst.addTransformer(new JDBCTransformer());    // БД
        inst.addTransformer(new HTTPTransformer());    // HTTP
        inst.addTransformer(new SpringTransformer());  // Spring
    }

    private static void startReporter() {
        Thread reporter = new Thread(() -> {
            while (true) {
                try {
                    Thread.sleep(60_000);  // Отправка каждую минуту
                    metrics.flush();
                } catch (InterruptedException e) {
                    break;
                }
            }
        }, "apm-reporter");
        reporter.setDaemon(true);
        reporter.start();
    }
}
```

---

## Performance Considerations

### Overhead агентов

```
Приложение без агента:       100ms (baseline)
Лёгкий агент (logging):      105ms (+5%)
Средний (metrics):           115ms (+15%)
Тяжёлый (full APM):          130ms (+30%)
Плохо написанный агент:      180ms (+80%) ⚠️
```

### Оптимизация производительности

**1. Ранняя фильтрация:**
```java
@Override
public byte[] transform(ClassLoader loader, String className, ...) {
    // Быстрое отклонение
    if (className == null) return null;
    if (className.startsWith("java/")) return null;
    if (className.startsWith("sun/")) return null;
    if (className.contains("$$")) return null;  // Generated classes

    // Только свои классы
    if (!className.startsWith("com/example/app")) return null;

    // Теперь дорогая трансформация
    return doTransform(bytecode);
}
```

**2. Кэширование:**
```java
private static final ConcurrentHashMap<String, Boolean> classCache =
    new ConcurrentHashMap<>();

private static boolean shouldInstrument(String className) {
    return classCache.computeIfAbsent(className, key -> {
        return expensiveAnalysis(key);  // Только один раз на класс
    });
}
```

**3. Батчинг метрик:**
```java
static class BatchedMetrics {
    private final AtomicLong counter = new AtomicLong();

    public void record(long duration) {
        counter.incrementAndGet();

        // Flush каждые 1000 вызовов, а не на каждом
        if (counter.get() % 1000 == 0) {
            flush();
        }
    }
}
```

**4. COMPUTE_MAXS вместо COMPUTE_FRAMES:**
```java
// Быстрее, но требует корректного байткода
ClassWriter writer = new ClassWriter(reader, ClassWriter.COMPUTE_MAXS);
```

---

## Типичные проблемы

### 1. ClassCircularityError

**Причина:** Загрузка класса во время трансформации этого же класса

**Решение:** Предзагрузить хелперы в premain()
```java
public static void premain(String args, Instrumentation inst) {
    // Предзагрузить все вспомогательные классы
    try {
        Class.forName("com.example.agent.MetricsCollector");
        Class.forName("com.example.agent.TimingHelper");
    } catch (ClassNotFoundException e) {
        throw new RuntimeException(e);
    }

    inst.addTransformer(new MyTransformer());
}
```

### 2. VerifyError после трансформации

**Причина:** Некорректный байткод

**Решение:** Использовать `COMPUTE_FRAMES`
```java
ClassWriter writer = new ClassWriter(reader, ClassWriter.COMPUTE_FRAMES);
```

### 3. Медленный startup

**Причина:** Трансформация слишком многих классов

**Решение:** Добавить фильтрацию (см. выше)

### 4. NoClassDefFoundError

**Причина:** Agent классы не в bootstrap classpath

**Решение:** `Boot-Class-Path` в MANIFEST.MF
```
Boot-Class-Path: asm-9.5.jar my-agent-helpers.jar
```

---

## JVMTI Native Agents

Java agents построены поверх **JVMTI** (JVM Tool Interface) — низкоуровневого C API.

**Возможности JVMTI:**
- Breakpoint callbacks
- GC events
- Thread lifecycle
- Heap inspection
- Method entry/exit на native уровне

**Когда использовать:**
- Нужна максимальная производительность
- Требуется доступ к JVM internals
- Кросс-язычное профилирование

**Пример нативного агента:**
```c
// agent.c
JNIEXPORT jint JNICALL Agent_OnLoad(JavaVM *jvm, char *options, void *reserved) {
    jvmtiEnv *jvmti;
    (*jvm)->GetEnv(jvm, (void **)&jvmti, JVMTI_VERSION_1_2);

    // Запросить возможности
    jvmtiCapabilities capabilities;
    memset(&capabilities, 0, sizeof(capabilities));
    capabilities.can_generate_method_entry_events = 1;
    jvmti->AddCapabilities(&capabilities);

    // Установить callbacks
    // ...

    return JNI_OK;
}

// Компиляция:
// gcc -shared -fPIC -I$JAVA_HOME/include -o libagent.so agent.c

// Запуск:
// java -agentpath:/path/to/libagent.so -jar app.jar
```

---

## Debugging

### Включение debug-логов

```java
public class DebugAgent {
    private static final boolean DEBUG = Boolean.getBoolean("agent.debug");

    public static void premain(String args, Instrumentation inst) {
        if (DEBUG) {
            System.out.println("Agent args: " + args);
            System.out.println("Retransform supported: " +
                inst.isRetransformClassesSupported());
        }

        inst.addTransformer(new DebugTransformer());
    }

    static class DebugTransformer implements ClassFileTransformer {
        @Override
        public byte[] transform(...) {
            if (DEBUG && className.startsWith("com/example")) {
                System.out.println("Transforming: " + className);
            }
            return null;
        }
    }
}

// java -Dagent.debug=true -javaagent:agent.jar -jar app.jar
```

---

## Связанные темы

**Манипуляция байткодом:**
- [[jvm-bytecode-manipulation]] — ASM, Javassist, ByteBuddy
- [[jvm-class-loader-deep-dive]] — Архитектура загрузки классов
- [[jvm-jit-compiler]] — Как JIT взаимодействует с агентами

**Альтернативные подходы:**
- [[jvm-annotations-processing]] — Генерация кода на compile-time
- AspectJ load-time weaving
- Spring AOP (proxy-based)

**Мониторинг:**
- JMX для runtime мониторинга
- [[jvm-profiling]] — Профилирование
- [[jvm-production-debugging]] — JFR, thread dumps

---

## Чек-лист

### Разработка агента
- [ ] Выбрать тип агента (premain vs agentmain)
- [ ] Создать MANIFEST.MF с Premain-Class/Agent-Class
- [ ] Реализовать ClassFileTransformer
- [ ] Добавить раннюю фильтрацию классов
- [ ] Обрабатывать исключения (никогда не ронять приложение)
- [ ] Использовать COMPUTE_FRAMES для безопасности
- [ ] Тестировать с целевым приложением

### Build & Packaging
- [ ] Включить все зависимости (maven-shade-plugin)
- [ ] Установить Boot-Class-Path если нужно
- [ ] Документировать command-line аргументы
- [ ] Предоставить примеры запуска

### Производительность
- [ ] Фильтровать классы перед трансформацией
- [ ] Кэшировать дорогие операции
- [ ] Батчинг для метрик/логов
- [ ] Минимизировать метод exit инструментацию
- [ ] Профилировать overhead агента
- [ ] Тестировать с production load

### Безопасность
- [ ] Проверить, что агент можно отключить
- [ ] Защитить чувствительные данные в логах
- [ ] Использовать HTTPS для телеметрии
- [ ] Реализовать rate limiting
- [ ] Аудит собираемых данных

### Тестирование
- [ ] Разные версии JVM (8, 11, 17, 21)
- [ ] Разные ClassLoaders
- [ ] Dynamic attach
- [ ] Retransformation
- [ ] Нет ClassCircularityError
- [ ] Load тесты для оценки overhead

---

**Summary:** Java agents — это мощный механизм runtime модификации байткода через `java.lang.instrument` API. Используются в APM инструментах (New Relic, DataDog), профайлерах (YourKit), code coverage (JaCoCo). Premain для startup инструментации, agentmain для dynamic attach. Всегда фильтруйте классы рано, используйте ASM COMPUTE_FRAMES, минимизируйте overhead. Коммерческие APM построены на этих основах с модульной архитектурой трансформеров для разных слоёв (JDBC, HTTP, Spring, Redis).

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Agents замедляют приложение значительно" | Хорошо написанный agent добавляет 1-5% overhead. Проблема в неэффективной фильтрации и частом логировании |
| "premain и agentmain взаимозаменяемы" | premain запускается ДО main(). agentmain — через dynamic attach к запущенному процессу. Разные use cases |
| "Agent может модифицировать любой класс" | Системные классы (java.lang.*) часто нельзя retransform. Bootstrap loaded classes имеют ограничения |
| "ClassFileTransformer вызывается один раз" | Transformer вызывается при каждой загрузке класса. С retransformation — может вызываться повторно |
| "ASM — единственный вариант" | ByteBuddy, Javassist — более высокоуровневые альтернативы. ASM быстрее, но сложнее |
| "Can-Retransform-Classes всегда нужен" | Retransformation дорогая. Для startup-only инструментации достаточно premain без retransform |
| "Agent работает в том же classloader что и app" | Agent может иметь свой classloader (Boot-Class-Path). Это изолирует зависимости |
| "Dynamic attach работает везде" | На некоторых JVM/ОС dynamic attach отключен по безопасности. -XX:+EnableDynamicAgentLoading |
| "Один agent на JVM" | Можно добавить несколько agents: -javaagent:a.jar -javaagent:b.jar. Порядок имеет значение |
| "Исключение в transformer ломает JVM" | JVM продолжает работать, но класс может не загрузиться. Всегда возвращайте null при ошибке |

---

## CS-фундамент

| CS-концепция | Применение в Java Agents |
|--------------|-------------------------|
| **Bytecode Instrumentation** | Модификация скомпилированного кода без доступа к исходникам. AOP на уровне bytecode |
| **Aspect-Oriented Programming** | Agents реализуют cross-cutting concerns (logging, monitoring) без изменения business logic |
| **Proxy Pattern** | Agents могут обернуть методы в proxy-like логику (before/after/around advice) |
| **Class Loading Interception** | ClassFileTransformer перехватывает загрузку классов — hook в ClassLoader chain |
| **JVM Tool Interface (JVMTI)** | Instrumentation API построен на JVMTI — native interface для profilers и debuggers |
| **Dynamic Code Generation** | ASM/ByteBuddy генерируют bytecode в runtime — метапрограммирование на низком уровне |
| **Attach API** | Dynamic attach использует процессный socket/pipe для коммуникации с JVM |
| **Stack Frame Computation** | COMPUTE_FRAMES автоматически вычисляет stack map frames, требуемые с Java 7+ |
| **Manifest Attributes** | MANIFEST.MF декларирует agent capabilities — convention-based configuration |
| **Two-Phase Class Loading** | Классы загружаются в два этапа: find (читаем bytes) → define (парсим в Class). Transformer работает между ними |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

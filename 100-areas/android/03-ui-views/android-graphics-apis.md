---
title: "Graphics APIs: OpenGL, Vulkan, Metal для мобильных"
created: 2026-01-09
modified: 2026-01-09
type: concept
area: android
status: published
confidence: high
tags:
  - topic/android
  - topic/graphics
  - type/concept
  - level/advanced
related:
  - "[[android-overview]]"
  - "[[android-view-rendering-pipeline]]"
  - "[[android-canvas-drawing]]"
  - "[[android-performance-profiling]]"
  - "[[android-window-system]]"
prerequisites:
  - "[[android-ui-views]]"
  - "[[android-view-rendering-pipeline]]"
---

# Graphics APIs: OpenGL, Vulkan, Metal для мобильных

> **TL;DR:** Graphics API — это интерфейс между приложением и GPU. OpenGL ES — legacy стандарт (высокоуровневый, проще). Vulkan — современный (низкоуровневый, производительнее, сложнее). Metal — Apple exclusive. Для большинства Android задач хватает Canvas/Compose, OpenGL для игр, Vulkan для AAA-графики.

---

## Интуиция: 5 аналогий

### 1. GPU как фабрика

```
CPU = Директор (принимает решения, один)
GPU = Фабрика с 1000 рабочими (делают одно и то же параллельно)

ЗАДАЧА: Покрасить 1 000 000 пикселей

CPU подход:
  for (pixel in pixels) {
      pixel.color = calculate(pixel)
  }
  // 1 000 000 последовательных операций

GPU подход:
  // Запустить 1 000 000 рабочих одновременно
  // Каждый красит СВОЙ пиксель
  // ~1000x быстрее для таких задач
```

### 2. OpenGL vs Vulkan как автомат vs механика

```
OPENGL ES (автоматическая коробка):
┌─────────────────────────────────────────────┐
│  "Нарисуй треугольник с этой текстурой"     │
│                    │                        │
│                    ▼                        │
│  ┌──────────────────────────────────────┐  │
│  │       ДРАЙВЕР ДЕЛАЕТ ВСЁ САМ         │  │
│  │  - Управление памятью                │  │
│  │  - Синхронизация                     │  │
│  │  - Оптимизация                       │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
Проще, но меньше контроля

VULKAN (механическая коробка):
┌─────────────────────────────────────────────┐
│  "Выдели память, загрузи текстуру,          │
│   создай command buffer, записи команды,    │
│   submit в queue, синхронизируй..."         │
│                    │                        │
│                    ▼                        │
│  ┌──────────────────────────────────────┐  │
│  │       ТЫ КОНТРОЛИРУЕШЬ ВСЁ           │  │
│  │  - Явное управление памятью          │  │
│  │  - Явная синхронизация               │  │
│  │  - Твоя ответственность              │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
Сложнее, но максимум производительности
```

### 3. Rendering Pipeline как конвейер

```
        VERTEX DATA                    SCREEN
            │                            │
            ▼                            │
    ┌───────────────┐                   │
    │ Vertex Shader │  Позиция точек    │
    └───────┬───────┘                   │
            │                            │
            ▼                            │
    ┌───────────────┐                   │
    │ Rasterization │  Точки → Пиксели  │
    └───────┬───────┘                   │
            │                            │
            ▼                            │
    ┌───────────────┐                   │
    │Fragment Shader│  Цвет пикселей    │
    └───────┬───────┘                   │
            │                            │
            ▼                            ▼
    ┌───────────────┐            ┌───────────┐
    │   Blending    │  ────────► │  ЭКРАН    │
    └───────────────┘            └───────────┘
```

### 4. Shader как программа для каждого пикселя

```
VERTEX SHADER (для каждой вершины):
  "Куда поставить эту точку на экране?"

  uniform mat4 mvpMatrix;  // Матрица преобразования
  attribute vec3 position; // Входная позиция

  void main() {
      gl_Position = mvpMatrix * vec4(position, 1.0);
  }

FRAGMENT SHADER (для каждого пикселя):
  "Какого цвета этот пиксель?"

  uniform sampler2D texture;
  varying vec2 texCoord;

  void main() {
      gl_FragColor = texture2D(texture, texCoord);
  }

GPU запускает миллионы копий этих программ ПАРАЛЛЕЛЬНО
```

### 5. Double/Triple Buffering как очередь кадров

```
БЕЗ BUFFERING (tearing):
  Рисуем прямо на экран
  Экран обновляется посередине рисования
  → Видим половину старого + половину нового кадра

DOUBLE BUFFERING:
  ┌─────────┐     ┌─────────┐
  │ Front   │     │  Back   │
  │ Buffer  │     │ Buffer  │
  │(показ.) │     │(рисуем) │
  └─────────┘     └─────────┘
       ↑              ↑
       │              │
    Экран         GPU рисует
    показывает    следующий кадр

  После VSync: swap buffers

TRIPLE BUFFERING:
  + Ещё один буфер
  + GPU не ждёт VSync
  + Больше latency, но плавнее
```

---

## Сравнение Graphics APIs

### Обзор

| API | Платформы | Уровень | Сложность | Производительность |
|-----|-----------|---------|-----------|-------------------|
| **OpenGL ES** | Android, iOS*, Web | Высокий | Средняя | Хорошая |
| **Vulkan** | Android, Win, Linux | Низкий | Высокая | Отличная |
| **Metal** | iOS, macOS | Низкий | Средняя | Отличная |
| **WebGL/WebGPU** | Браузеры | Высокий/Низкий | Средняя | Хорошая |

*iOS deprecated OpenGL ES

### OpenGL ES vs Vulkan

```
                    OpenGL ES              Vulkan
────────────────────────────────────────────────────────
Управление памятью   Автоматическое        Явное
Многопоточность      Ограниченная          Полная
Command buffers      Нет                   Да
Validation           Runtime               Отключаемая
Driver overhead      Высокий               Низкий
Код для треугольника ~100 строк            ~1000 строк
Debug                Проще                 Сложнее
Батарея              Больше расход         Меньше расход
Когда использовать   Простая графика       AAA игры, VR
```

---

## Android Graphics Stack

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION                           │
├───────────────┬───────────────┬────────────────────────┤
│    Canvas     │   OpenGL ES   │        Vulkan          │
│  (2D, простой)│  (3D, игры)   │   (3D, высокая произв.)│
├───────────────┴───────────────┴────────────────────────┤
│                   SKIA / HWUI                           │
│              (Android rendering engine)                  │
├─────────────────────────────────────────────────────────┤
│               SurfaceFlinger (compositor)               │
├─────────────────────────────────────────────────────────┤
│              Hardware Abstraction Layer                  │
├─────────────────────────────────────────────────────────┤
│                    GPU DRIVER                           │
├─────────────────────────────────────────────────────────┤
│                       GPU                               │
└─────────────────────────────────────────────────────────┘

Jetpack Compose → Canvas → Skia → OpenGL/Vulkan → GPU
```

### Когда что использовать

| Задача | Рекомендация | Почему |
|--------|--------------|--------|
| UI приложения | Compose/Canvas | Достаточно, проще |
| 2D игра простая | Canvas | Хватит производительности |
| 2D игра сложная | OpenGL ES | Больше контроля |
| 3D игра | OpenGL ES или Vulkan | Зависит от сложности |
| VR/AR | Vulkan | Нужна низкая latency |
| Видео обработка | OpenGL ES/Vulkan | Hardware acceleration |

---

## OpenGL ES: Основы

### Минимальный пример

```kotlin
class MyGLRenderer : GLSurfaceView.Renderer {

    private lateinit var triangle: Triangle

    override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
        // Цвет фона
        GLES20.glClearColor(0f, 0f, 0f, 1f)
        triangle = Triangle()
    }

    override fun onDrawFrame(gl: GL10?) {
        // Очистить экран
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT)
        // Нарисовать треугольник
        triangle.draw()
    }

    override fun onSurfaceChanged(gl: GL10?, width: Int, height: Int) {
        GLES20.glViewport(0, 0, width, height)
    }
}

class Triangle {
    private val vertexShaderCode = """
        attribute vec4 vPosition;
        void main() {
            gl_Position = vPosition;
        }
    """.trimIndent()

    private val fragmentShaderCode = """
        precision mediump float;
        uniform vec4 vColor;
        void main() {
            gl_FragColor = vColor;
        }
    """.trimIndent()

    private val coords = floatArrayOf(
        0.0f,  0.5f, 0.0f,  // Верх
       -0.5f, -0.5f, 0.0f,  // Лево низ
        0.5f, -0.5f, 0.0f   // Право низ
    )

    private val color = floatArrayOf(1.0f, 0.0f, 0.0f, 1.0f) // Красный

    private val program: Int
    private val vertexBuffer: FloatBuffer

    init {
        // Создать буфер вершин
        vertexBuffer = ByteBuffer.allocateDirect(coords.size * 4)
            .order(ByteOrder.nativeOrder())
            .asFloatBuffer()
            .put(coords)
        vertexBuffer.position(0)

        // Скомпилировать шейдеры
        val vertexShader = loadShader(GLES20.GL_VERTEX_SHADER, vertexShaderCode)
        val fragmentShader = loadShader(GLES20.GL_FRAGMENT_SHADER, fragmentShaderCode)

        // Создать программу
        program = GLES20.glCreateProgram().also {
            GLES20.glAttachShader(it, vertexShader)
            GLES20.glAttachShader(it, fragmentShader)
            GLES20.glLinkProgram(it)
        }
    }

    fun draw() {
        GLES20.glUseProgram(program)

        // Передать вершины
        val positionHandle = GLES20.glGetAttribLocation(program, "vPosition")
        GLES20.glEnableVertexAttribArray(positionHandle)
        GLES20.glVertexAttribPointer(positionHandle, 3, GLES20.GL_FLOAT, false, 12, vertexBuffer)

        // Передать цвет
        val colorHandle = GLES20.glGetUniformLocation(program, "vColor")
        GLES20.glUniform4fv(colorHandle, 1, color, 0)

        // Нарисовать
        GLES20.glDrawArrays(GLES20.GL_TRIANGLES, 0, 3)

        GLES20.glDisableVertexAttribArray(positionHandle)
    }

    private fun loadShader(type: Int, shaderCode: String): Int {
        return GLES20.glCreateShader(type).also { shader ->
            GLES20.glShaderSource(shader, shaderCode)
            GLES20.glCompileShader(shader)
        }
    }
}
```

---

## Частые ошибки: 6 проблем

### ❌ Ошибка 1: Утечка OpenGL ресурсов

**Симптом:** Out of memory, графические артефакты

```kotlin
// ПЛОХО — не освобождаем ресурсы:
class BadRenderer : GLSurfaceView.Renderer {
    override fun onDrawFrame(gl: GL10?) {
        val texture = loadTexture(bitmap)  // Каждый кадр новая текстура!
        // Никогда не вызываем glDeleteTextures
    }
}

// ХОРОШО — управляем lifecycle:
class GoodRenderer : GLSurfaceView.Renderer {
    private var textureId: Int = 0

    override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
        textureId = loadTexture(bitmap)  // Один раз
    }

    override fun onDrawFrame(gl: GL10?) {
        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textureId)
        // Используем существующую текстуру
    }

    fun cleanup() {
        GLES20.glDeleteTextures(1, intArrayOf(textureId), 0)
    }
}
```

---

### ❌ Ошибка 2: Блокировка GL thread

**Симптом:** Фризы, низкий FPS

```kotlin
// ПЛОХО — тяжёлая работа на GL thread:
override fun onDrawFrame(gl: GL10?) {
    val bitmap = loadBitmapFromNetwork()  // ❌ Сетевой запрос!
    val texture = loadTexture(bitmap)
    draw(texture)
}

// ХОРОШО — загрузка асинхронно:
class AsyncRenderer : GLSurfaceView.Renderer {
    private val textureQueue = ConcurrentLinkedQueue<Bitmap>()

    fun loadTextureAsync(url: String) {
        scope.launch(Dispatchers.IO) {
            val bitmap = loadBitmapFromNetwork(url)
            textureQueue.add(bitmap)
        }
    }

    override fun onDrawFrame(gl: GL10?) {
        // Обработать очередь на GL thread
        textureQueue.poll()?.let { bitmap ->
            uploadTexture(bitmap)
            bitmap.recycle()
        }
        draw()
    }
}
```

---

### ❌ Ошибка 3: Неправильный формат текстуры

**Симптом:** Размытые текстуры, артефакты

```kotlin
// ПЛОХО — NPOT текстура без правильных параметров:
fun loadTexture(bitmap: Bitmap): Int {
    // Bitmap 100x100 (не степень двойки)
    GLES20.glTexImage2D(...)
    // GL_REPEAT не работает для NPOT!
}

// ХОРОШО — правильные параметры для NPOT:
fun loadTexture(bitmap: Bitmap): Int {
    val textureIds = IntArray(1)
    GLES20.glGenTextures(1, textureIds, 0)
    GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textureIds[0])

    // Для NPOT текстур:
    GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_S, GLES20.GL_CLAMP_TO_EDGE)
    GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_T, GLES20.GL_CLAMP_TO_EDGE)
    GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MIN_FILTER, GLES20.GL_LINEAR)
    GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MAG_FILTER, GLES20.GL_LINEAR)

    GLUtils.texImage2D(GLES20.GL_TEXTURE_2D, 0, bitmap, 0)
    return textureIds[0]
}
```

---

### ❌ Ошибка 4: Игнорирование GL errors

**Симптом:** Молчаливые сбои, непонятное поведение

```kotlin
// ПЛОХО — не проверяем ошибки:
GLES20.glCompileShader(shader)
// Шейдер может не скомпилироваться, но мы не узнаем

// ХОРОШО — проверяем ошибки:
fun compileShader(type: Int, code: String): Int {
    val shader = GLES20.glCreateShader(type)
    GLES20.glShaderSource(shader, code)
    GLES20.glCompileShader(shader)

    // Проверить результат компиляции
    val compiled = IntArray(1)
    GLES20.glGetShaderiv(shader, GLES20.GL_COMPILE_STATUS, compiled, 0)

    if (compiled[0] == 0) {
        val error = GLES20.glGetShaderInfoLog(shader)
        GLES20.glDeleteShader(shader)
        throw RuntimeException("Shader compilation failed: $error")
    }

    return shader
}

// Общая проверка GL ошибок:
fun checkGLError(op: String) {
    var error: Int
    while (GLES20.glGetError().also { error = it } != GLES20.GL_NO_ERROR) {
        Log.e("GL", "$op: glError $error")
    }
}
```

---

### ❌ Ошибка 5: Overdraw

**Симптом:** Низкий FPS, высокое энергопотребление

```kotlin
// ПЛОХО — рисуем невидимые объекты:
fun drawScene() {
    drawBackground()      // 100% экрана
    drawMiddleLayer()     // 80% экрана (перекрывает фон)
    drawUI()              // 50% экрана (перекрывает всё)
    // Многие пиксели нарисованы 3 раза!
}

// ХОРОШО — минимизируем overdraw:
fun drawScene() {
    // 1. Включить depth test
    GLES20.glEnable(GLES20.GL_DEPTH_TEST)

    // 2. Рисовать front-to-back (для opaque)
    drawUI()              // Сначала ближнее
    drawMiddleLayer()     // Depth test отсечёт скрытое
    drawBackground()      // Depth test отсечёт скрытое

    // 3. Для прозрачных — back-to-front
    GLES20.glEnable(GLES20.GL_BLEND)
    drawTransparentObjects()
}
```

---

### ❌ Ошибка 6: Синхронизация CPU-GPU

**Симптом:** CPU ждёт GPU, низкий FPS

```kotlin
// ПЛОХО — синхронное чтение:
fun captureFrame(): Bitmap {
    GLES20.glReadPixels(...)  // CPU ждёт GPU!
    return bitmap
}

// ХОРОШО — использовать PBO для async read:
fun captureFrameAsync() {
    // Pixel Buffer Object для асинхронного чтения
    val pbo = IntArray(1)
    GLES30.glGenBuffers(1, pbo, 0)
    GLES30.glBindBuffer(GLES30.GL_PIXEL_PACK_BUFFER, pbo[0])
    GLES30.glBufferData(GLES30.GL_PIXEL_PACK_BUFFER, size, null, GLES30.GL_STREAM_READ)

    // Начать async read
    GLES30.glReadPixels(0, 0, width, height, GLES30.GL_RGBA, GLES30.GL_UNSIGNED_BYTE, 0)

    // В следующем кадре — получить данные
    val buffer = GLES30.glMapBufferRange(...) as ByteBuffer
    // CPU не ждёт, данные уже готовы
}
```

---

## Ментальные модели

### 1. Pipeline мышление

```
Каждый кадр проходит через stages:

Application → Geometry → Rasterization → Pixel → Display
     │            │            │           │
  CPU work    Vertex       Fill         Fragment
              Shader      triangles     Shader

Bottleneck может быть на любом этапе
Profile чтобы найти!
```

### 2. GPU parallelism

```
GPU НЕ как CPU:

CPU: 8 мощных ядер, сложные задачи
GPU: 1000+ слабых ядер, простые задачи параллельно

  CPU:    ████████ (один thread)

  GPU:    ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪ (тысячи threads)

Хорошо для GPU: одинаковые операции над многими данными
Плохо для GPU: условные переходы, разные пути выполнения
```

### 3. Memory bandwidth

```
GPU ограничен не только compute, но и memory bandwidth

                    GPU
                     │
          ┌──────────┼──────────┐
          │          │          │
      Compute    Memory BW    Cache
        16       8 GB/s       2 MB
       TFLOPS

Оптимизация:
- Сжатые текстуры (ETC2, ASTC)
- Mipmaps (меньше fetch для далёких объектов)
- Texture atlases (меньше texture switches)
```

---

## Проверь себя

**Вопрос 1:** Почему Vulkan может быть быстрее OpenGL ES?

<details>
<summary>Ответ</summary>

1. **Меньше driver overhead:** Vulkan не делает валидацию каждый вызов
2. **Явное управление памятью:** Программист контролирует allocation
3. **Command buffers:** Можно записать команды заранее и переиспользовать
4. **Многопоточность:** Можно строить command buffers параллельно
5. **Pipeline state objects:** Состояние задаётся целиком, меньше изменений

Но: Vulkan требует ~10x больше кода и глубокого понимания GPU.
</details>

**Вопрос 2:** Зачем нужен double buffering?

<details>
<summary>Ответ</summary>

Без double buffering:
- GPU рисует прямо в видеопамять которую показывает монитор
- Если монитор обновляется посреди рисования — видим "разорванный" кадр (tearing)

С double buffering:
- Front buffer показывается на экране
- Back buffer — GPU рисует следующий кадр
- После VSync — swap (мгновенный)
- Никогда не видим незаконченный кадр
</details>

---

## Связь с другими темами

**[[android-view-rendering-pipeline]]** — Rendering pipeline — это основной способ, которым Android рисует UI. Graphics APIs (OpenGL ES, Vulkan) работают на уровне ниже стандартного pipeline: HWUI использует OpenGL ES/Vulkan под капотом для hardware-accelerated rendering. Понимание rendering pipeline объясняет, когда стандартного Canvas достаточно, а когда нужен прямой доступ к GPU. Рекомендуется изучить rendering pipeline перед Graphics APIs.

**[[android-canvas-drawing]]** — Canvas API предоставляет 2D-рисование поверх Skia, который, в свою очередь, использует OpenGL ES или Vulkan для hardware acceleration. Для большинства задач (Custom View, графики, диаграммы) Canvas достаточно. Graphics APIs нужны только для 3D-графики, игр и вычислений на GPU. Изучайте Canvas как более практичную альтернативу.

**[[android-performance-profiling]]** — GPU Profiler, Systrace и GPU overdraw inspection являются ключевыми инструментами для диагностики проблем производительности графики. Понимание Graphics APIs помогает интерпретировать результаты профилирования (shader compilation stalls, draw call overhead, texture upload bottlenecks). Изучайте profiling после базового понимания Graphics APIs.

**[[android-window-system]]** — Window system управляет поверхностями (Surface, SurfaceFlinger), на которых отрисовываются результаты работы Graphics APIs. SurfaceView и TextureView предоставляют Surface для прямого OpenGL/Vulkan рендеринга. Понимание window system объясняет, как GPU output попадает на экран.

---

## Источники и дальнейшее чтение

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [OpenGL ES Android](https://developer.android.com/develop/ui/views/graphics/opengl) | Docs | Android specific |
| 2 | [Vulkan Tutorial](https://vulkan-tutorial.com/) | Tutorial | Vulkan basics |
| 3 | [GPU Gems](https://developer.nvidia.com/gpugems/gpugems/contributors) | Book | Advanced techniques |

### Книги

- **Meier R. (2022)** *Professional Android* — введение в SurfaceView, TextureView и использование OpenGL ES для custom rendering в Android приложениях.
- **Phillips B. et al. (2022)** *Android Programming: The Big Nerd Ranch Guide* — практические примеры работы с Canvas и базовым OpenGL ES для создания интерактивных визуализаций.

---

*Проверено: 2026-01-09*

---

[[android-overview|← Android]] | [[android-view-rendering-pipeline|Rendering Pipeline →]]

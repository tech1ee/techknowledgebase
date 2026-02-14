---
title: "On-Device AI: Gemini Nano, ML Kit, TFLite"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
area: android
tags:
  - topic/android
  - topic/ai-ml
  - type/deep-dive
  - level/advanced
related:
  - "[[mobile-ai-ml-guide]]"
  - "[[android-app-startup-performance]]"
  - "[[android-ecosystem-2026]]"
prerequisites:
  - "[[android-overview]]"
  - "[[mobile-ai-ml-guide]]"
reading_time: 22
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# On-Device AI: Gemini Nano, ML Kit, LiteRT, MediaPipe

## Терминология

| Термин | Значение |
|--------|----------|
| **Gemini Nano** | Самая компактная модель семейства Gemini, оптимизированная для запуска на устройстве |
| **AICore** | Системный сервис Android, управляющий on-device GenAI-моделями |
| **ML Kit** | SDK от Google для мобильного ML — classic-задачи (OCR, barcode) + GenAI APIs |
| **LiteRT** | Новое имя TensorFlow Lite — runtime для пользовательских моделей на устройстве |
| **MediaPipe** | Фреймворк Google AI Edge для vision, audio, text задач + LLM Inference |
| **NPU** | Neural Processing Unit — выделенный чип для ML-вычислений |
| **NNAPI** | Android Neural Networks API — deprecated, заменяется LiteRT delegates |
| **Quantization** | Уменьшение точности весов модели (FP32 -> INT8 -> INT4) для компактности |
| **Gemma 3n** | Open-source мультимодальная модель Google, архитектурная основа Gemini Nano v3 |
| **Prompt API** | ML Kit GenAI API для отправки произвольных промптов в Gemini Nano |

---

## AI переехал из облака на телефон

Pixel 10 запускает Gemini Nano с мультимодальным пониманием текста, изображений и аудио прямо на чипе Tensor G5. Samsung Galaxy S25 делает то же самое на Snapdragon 8 Elite. В 2025 году on-device AI перестал быть экспериментом -- это production-ready стек, доступный через стандартные Android API.

Для разработчика это означает конкретный выбор: какой инструмент использовать для какой задачи. В этом deep-dive -- полная карта стека on-device AI на Android: от Gemini Nano до custom-моделей через LiteRT.

---

## Зачем это нужно

### Privacy: данные не покидают устройство

On-device inference означает, что пользовательские данные -- текст, фото, голос -- обрабатываются локально. Никаких сетевых запросов, никаких логов на стороне сервера. Это критично для:

- **Медицинских приложений** (HIPAA compliance)
- **Финансовых данных** (GDPR, PCI DSS)
- **Персональных ассистентов** (переписка, фото, голосовые заметки)

### Latency: нет network round-trip

Cloud API: 200-500 ms latency (сеть + inference). On-device: < 10 ms для classic ML задач, 50-200 ms для GenAI. Разница критична для real-time сценариев -- камера, voice input, live translation.

### Offline capability

2.6 миллиарда людей не имеют стабильного интернета. On-device AI работает в самолёте, в метро, в горах. Перевод, диктовка, распознавание объектов -- всё доступно без сети.

### Cost: нет API-вызовов

Каждый вызов Gemini Pro / GPT-4o стоит денег. On-device inference -- бесплатно после загрузки модели. Для приложения с миллионами пользователей экономия может составить десятки тысяч долларов в месяц.

---

## Gemini Nano

### Что это

Gemini Nano -- самая компактная модель семейства Gemini, специально оптимизированная для запуска на мобильных устройствах. Текущая версия (nano-v3) построена на архитектуре Gemma 3n и поддерживает мультимодальный ввод (текст + изображения + аудио).

### AICore: системный сервис Android

AICore -- это системный сервис Android (начиная с Android 14), который:

- **Управляет загрузкой и обновлением** моделей -- разработчику не нужно распространять модели самостоятельно
- **Оптимизирует inference** под конкретное железо (GPU, NPU)
- **Изолирует модели** от приложения -- модель не влияет на APK size
- **Обновляется** через Google Play Services -- новые версии моделей приходят автоматически

```
Приложение -> ML Kit GenAI API -> AICore Service -> Gemini Nano
                                        |
                                   Hardware (GPU/NPU)
```

### Доступность устройств

| Производитель | Устройства | Мультимодальность |
|---------------|-----------|-------------------|
| **Google** | Pixel 8 Pro, Pixel 9 серия, Pixel 10 серия | Pixel 10+ (nano-v3) |
| **Samsung** | Galaxy S24/S24+/S24 Ultra/S24 FE, S25 серия, Z Fold 6, Z Flip 6 | Galaxy S25+ |
| **Motorola** | Moto Razr, флагманские модели | Ограниченно |
| **Xiaomi** | Отдельные флагманские модели | Ограниченно |
| **Honor** | Отдельные модели | Ограниченно |

### Возможности

- **Summarization** -- сжатие длинных текстов в ключевые тезисы
- **Smart Reply** -- генерация контекстных ответов на сообщения
- **Proofreading** -- исправление грамматики и орфографии
- **Rewriting** -- перефразирование текста с сохранением смысла
- **Image Understanding** (nano-v3) -- описание изображений, классификация
- **Speech Recognition** -- распознавание речи на устройстве

### Ограничения

- **Device fragmentation** -- работает только на premium-устройствах
- **Model download** -- AICore загружает модели по требованию, не мгновенно (сотни MB)
- **Quality gap** -- Gemini Nano значительно уступает Gemini Pro/Flash по качеству генерации
- **Контекстное окно** -- ограничено по сравнению с cloud-моделями
- **Не все языки** поддерживаются одинаково хорошо

---

## ML Kit GenAI APIs

ML Kit GenAI APIs -- основной рекомендуемый способ работы с Gemini Nano. Запущены в мае 2025, работают поверх AICore.

### Use-Case Specific APIs (Stable)

#### Summarization API

Принимает текст, возвращает краткое содержание в виде bullet-points:

```kotlin
val summarizer = Summarizer.builder(context)
    .setOutputType(OutputType.BULLET_POINTS)
    .build()

// Проверяем доступность
summarizer.checkFeatureStatus().addOnSuccessListener { status ->
    if (status == FeatureStatus.AVAILABLE) {
        summarizer.run(inputText)
            .addOnSuccessListener { summary ->
                // summary содержит краткое содержание
            }
    }
}
```

#### Proofreading API

Исправляет грамматику и орфографию коротких текстов:

```kotlin
val proofreader = Proofreader.builder(context).build()

proofreader.run(inputText)
    .addOnSuccessListener { correctedText ->
        // correctedText -- исправленный текст
    }
```

#### Image Description API

Генерирует текстовое описание изображения на естественном языке:

```kotlin
val imageDescriber = ImageDescriber.builder(context).build()

val image = InputImage.fromBitmap(bitmap, 0)
imageDescriber.run(image)
    .addOnSuccessListener { description ->
        // description -- текстовое описание изображения
    }
```

### Prompt API (Alpha)

Prompt API -- это прорыв: вы отправляете **произвольные** текстовые и мультимодальные промпты в Gemini Nano. Это открывает кастомные use-cases:

```kotlin
val promptApi = PromptApi.builder(context).build()

// Текстовый промпт
val request = PromptRequest.builder()
    .setPrompt("Classify this review as positive, negative, or neutral: '$reviewText'")
    .build()

promptApi.run(request)
    .addOnSuccessListener { response ->
        // response.getText() -- ответ модели
    }

// Мультимодальный промпт (текст + изображение)
val multimodalRequest = PromptRequest.builder()
    .setPrompt("What objects are in this image?")
    .setImage(inputImage)
    .build()
```

**Рекомендованные use-cases для Prompt API:**
- Классификация изображений и документов
- Извлечение информации из email/сообщений
- Генерация заголовков и описаний контента
- Анализ тональности отзывов
- Контекстные подсказки пользователю

> **Важно:** Prompt API лучше всего работает на Pixel 10 (nano-v3 / Gemma 3n). На более старых устройствах качество ниже.

### Streaming

Все GenAI APIs поддерживают streaming для длинных ответов:

```kotlin
summarizer.runStreaming(inputText)
    .collect { partialResult ->
        // Обновляем UI инкрементально
        updateUI(partialResult)
    }
```

---

## ML Kit Classic

ML Kit Classic -- стабильные, production-ready API для конкретных ML-задач. Работают на **любом** Android-устройстве, не требуют AICore.

### Основные API

| API | Возможности | On-device | Cloud |
|-----|-------------|-----------|-------|
| **Text Recognition** | OCR, 300+ языков, рукописный текст | Да | Да |
| **Barcode Scanning** | QR, UPC, EAN, Code 128, все стандарты | Да | -- |
| **Face Detection** | Landmarks, contours, classification, 468 3D face mesh | Да | -- |
| **Object Detection** | Real-time tracking, custom models | Да | -- |
| **Pose Estimation** | 33 body landmarks, BlazePose | Да | -- |
| **Selfie Segmentation** | Отделение человека от фона | Да | -- |
| **Image Labeling** | Классификация содержимого изображений | Да | Да |
| **Language Detection** | Определение языка текста | Да | -- |
| **Translation** | On-device перевод между языками | Да | -- |

### Classic vs GenAI: когда что использовать

| Критерий | ML Kit Classic | ML Kit GenAI |
|----------|---------------|--------------|
| **Задачи** | OCR, barcode, face detection, pose | Summarization, rewriting, image description |
| **Устройства** | Любой Android 5.0+ | Premium-устройства с AICore |
| **Детерминизм** | Высокий -- одинаковый результат | Вариативный -- генеративная природа |
| **Latency** | 1-50 ms | 50-500 ms |
| **Offline** | Всегда | Да, после загрузки модели |
| **Размер модели** | 1-20 MB | 100+ MB (управляет AICore) |
| **Кастомизация** | Custom TFLite модели | Промпты (Prompt API) |

**Правило:** если задачу можно решить Classic API (OCR, barcode) -- используйте его. GenAI APIs нужны для задач, требующих **понимания** и **генерации** текста.

---

## LiteRT (бывший TensorFlow Lite)

### Что изменилось

TensorFlow Lite переименован в **LiteRT** (Lite RunTime). Существующие пакеты TFLite продолжают работать, но все новые фичи и оптимизации -- только в LiteRT.

**Миграция** минимальна -- замена зависимости:

```kotlin
// Было (TFLite)
implementation("org.tensorflow:tensorflow-lite:2.x.x")

// Стало (LiteRT)
implementation("com.google.ai.edge.litert:litert:2.1.0")
```

### Когда использовать LiteRT

LiteRT -- для **собственных моделей**. Если вам нужна custom image classification, audio processing, NLP-модель, обученная на ваших данных -- LiteRT ваш инструмент.

### Hardware Acceleration

```
LiteRT Model
    |
    ├── CPU Delegate (по умолчанию, везде работает)
    ├── GPU Delegate (mobile GPU, значительное ускорение)
    └── Vendor NPU Delegate (максимальная производительность)
```

- **CPU** -- работает везде, базовая производительность
- **GPU Delegate** -- ускорение на мобильном GPU, поддерживает INT8 quantized модели
- **NPU Delegate** -- прямой доступ к нейропроцессору (Qualcomm Hexagon, Samsung, MediaTek APU)

> **Важно:** Android NNAPI deprecated. LiteRT напрямую работает с vendor NPU delegates.

### Quantization: размер vs качество

| Формат | Размер модели | Качество | Latency | Когда использовать |
|--------|--------------|----------|---------|-------------------|
| **FP32** | 100% (baseline) | Максимальное | Медленно | Разработка, baseline |
| **FP16** | ~50% | Близко к FP32 | Быстрее | GPU inference |
| **INT8** | ~25% | -1-3% accuracy | Быстро | Production на CPU/GPU |
| **INT4** | ~12.5% | -3-7% accuracy | Очень быстро | Экстремальная оптимизация |

```python
# Post-training quantization (Python, при конвертации модели)
converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # INT8
converter.target_spec.supported_types = [tf.int8]
tflite_model = converter.convert()
```

### On-Device Training

LiteRT поддерживает **инкрементальное дообучение** модели прямо на устройстве -- персонализация без отправки данных на сервер.

---

## MediaPipe

### Pre-built Solutions

MediaPipe -- фреймворк Google AI Edge, предоставляющий готовые решения для vision, audio и text задач. Ключевое отличие от ML Kit: больше гибкости, больше моделей, кроссплатформенность.

| Solution | Landmarks/Output | FPS (Android) |
|----------|-----------------|---------------|
| **Face Mesh** | 468 3D face landmarks | 30+ |
| **Hand Tracking** | 21 landmarks per hand | 30+ |
| **Pose Estimation** | 33 body landmarks + segmentation | 25+ |
| **Object Detection** | Bounding boxes + labels | 30+ |
| **Holistic** | 543 landmarks (face+hands+body) | 15-20 |
| **Image Segmentation** | Per-pixel classification | 25+ |

### LLM Inference API

MediaPipe LLM Inference API позволяет запускать LLM-модели на устройстве **без AICore** -- вы сами управляете моделью:

```kotlin
// Зависимость
implementation("com.google.mediapipe:tasks-genai:0.10.27")

// Инициализация
val options = LlmInference.LlmInferenceOptions.builder()
    .setModelPath("/path/to/model.task")
    .setMaxTokens(1024)
    .build()

val llmInference = LlmInference.createFromOptions(context, options)
val response = llmInference.generateResponse("Your prompt here")
```

**Поддерживаемые модели:**
- **Gemma 3n E2B** -- effective 2B parameters, мультимодальный (текст + изображения + аудио)
- **Gemma 3n E4B** -- effective 4B parameters, лучше качество, больше RAM
- **Gemma 2 2B** -- text-only, стабильный
- Кастомные модели в формате `.task`

> **Gemma 3n E2B** стартует ~1.5x быстрее Gemma 3 4B и требует всего 2 GB RAM.

### MediaPipe vs ML Kit

| Критерий | MediaPipe | ML Kit |
|----------|-----------|--------|
| **Модели** | Свои + Google (Gemma) | Gemini Nano через AICore |
| **Управление моделями** | Вы сами (bundle или download) | AICore управляет |
| **Кроссплатформенность** | Android, iOS, Web, Python | Android (GenAI), Android+iOS (Classic) |
| **Гибкость** | Высокая -- custom pipelines | Средняя -- use-case APIs |
| **Простота** | Средняя | Высокая |
| **LLM inference** | Да (LLM Inference API) | Через Prompt API |

**Правило:** ML Kit -- для быстрой интеграции стандартных задач. MediaPipe -- когда нужен полный контроль над моделью и pipeline.

---

## Integration Patterns

### Feature Detection: проверка возможностей устройства

Никогда не предполагайте, что Gemini Nano доступен. Всегда проверяйте:

```kotlin
// Проверка доступности GenAI feature
val summarizer = Summarizer.builder(context).build()

summarizer.checkFeatureStatus().addOnSuccessListener { status ->
    when (status) {
        FeatureStatus.AVAILABLE -> {
            // Gemini Nano готов -- используем on-device
        }
        FeatureStatus.DOWNLOADING -> {
            // Модель загружается -- покажем прогресс
        }
        FeatureStatus.UNAVAILABLE -> {
            // Устройство не поддерживает -- fallback на cloud
        }
    }
}
```

### Fallback Strategy: on-device -> cloud -> degradation

```
Запрос на summarization
    |
    ├── [1] Gemini Nano доступен? → On-device inference
    |
    ├── [2] Есть интернет? → Cloud API (Gemini Flash/Pro)
    |
    └── [3] Нет ничего → Graceful degradation
                         (показываем первые N слов / скрываем фичу)
```

### Hilt: инъекция AI-сервисов

```kotlin
// Абстракция
interface TextSummarizer {
    suspend fun summarize(text: String): Result<String>
    suspend fun isAvailable(): Boolean
}

// On-device реализация
class OnDeviceSummarizer @Inject constructor(
    @ApplicationContext private val context: Context
) : TextSummarizer {

    private val summarizer = Summarizer.builder(context)
        .setOutputType(OutputType.BULLET_POINTS)
        .build()

    override suspend fun isAvailable(): Boolean =
        suspendCoroutine { cont ->
            summarizer.checkFeatureStatus()
                .addOnSuccessListener { status ->
                    cont.resume(status == FeatureStatus.AVAILABLE)
                }
                .addOnFailureListener { cont.resume(false) }
        }

    override suspend fun summarize(text: String): Result<String> =
        suspendCoroutine { cont ->
            summarizer.run(text)
                .addOnSuccessListener { cont.resume(Result.success(it)) }
                .addOnFailureListener { cont.resume(Result.failure(it)) }
        }
}

// Cloud fallback реализация
class CloudSummarizer @Inject constructor(
    private val geminiApi: GeminiApiService
) : TextSummarizer {

    override suspend fun isAvailable(): Boolean = true // Всегда доступен с сетью

    override suspend fun summarize(text: String): Result<String> =
        runCatching { geminiApi.summarize(text) }
}

// Hilt Module
@Module
@InstallIn(SingletonComponent::class)
object AiModule {

    @Provides
    @Named("onDevice")
    fun provideOnDeviceSummarizer(
        @ApplicationContext context: Context
    ): TextSummarizer = OnDeviceSummarizer(context)

    @Provides
    @Named("cloud")
    fun provideCloudSummarizer(
        geminiApi: GeminiApiService
    ): TextSummarizer = CloudSummarizer(geminiApi)
}

// UseCase с fallback
class SummarizeUseCase @Inject constructor(
    @Named("onDevice") private val onDevice: TextSummarizer,
    @Named("cloud") private val cloud: TextSummarizer,
    private val connectivityManager: ConnectivityManager
) {
    suspend fun execute(text: String): Result<String> {
        // Приоритет: on-device → cloud → error
        if (onDevice.isAvailable()) {
            return onDevice.summarize(text)
        }
        if (connectivityManager.isConnected()) {
            return cloud.summarize(text)
        }
        return Result.failure(AiUnavailableException())
    }
}
```

---

## Performance Considerations

### Model Size vs Quality vs Latency

| Модель / API | Размер | Качество (отн.) | Latency | RAM |
|-------------|--------|-----------------|---------|-----|
| **Gemini Nano v3** (AICore) | ~300 MB (управляет AICore) | Высокое | 100-300 ms | 2-4 GB |
| **Gemma 3n E2B** (MediaPipe) | ~1.5 GB (.task) | Среднее-высокое | 150-400 ms | 2 GB |
| **Gemma 3n E4B** (MediaPipe) | ~3 GB (.task) | Высокое | 200-600 ms | 4 GB |
| **ML Kit Classic** (OCR) | 1-5 MB | Высокое (для задачи) | 5-30 ms | 50-200 MB |
| **Custom LiteRT INT8** | 5-50 MB | Зависит от модели | 5-50 ms | 50-300 MB |

### Влияние quantization на accuracy

Типичная потеря accuracy при quantization (зависит от модели):

- **FP32 -> FP16:** < 0.5% потери -- практически бесплатно
- **FP32 -> INT8:** 1-3% потери -- рекомендуемый production формат
- **FP32 -> INT4:** 3-7% потери -- только для экстремальных ограничений

### Battery consumption

Интенсивные ML-задачи разряжают батарею. Рекомендации:

- **Batch inference** вместо continuous -- группируйте запросы
- **Throttling** -- ограничивайте частоту inference (не чаще 1 раз/секунду для GenAI)
- **NPU > GPU > CPU** по энергоэффективности -- используйте аппаратное ускорение
- **Мониторинг** через `BatteryManager` -- снижайте ML-нагрузку при низком заряде

### Warm-up time

Первый inference всегда медленнее из-за загрузки модели в память:

```kotlin
// Прогрев модели при старте Activity/Fragment
lifecycleScope.launch {
    withContext(Dispatchers.Default) {
        // Инициализируем модель заранее
        summarizer.checkFeatureStatus().await()
    }
}
```

---

## Подводные камни

### 1. Device Fragmentation

Gemini Nano работает на < 10% Android-устройств (premium сегмент). Ваше приложение **обязано** работать и без него. Проектируйте GenAI-фичи как progressive enhancement, не как core functionality.

### 2. Model Download: не мгновенно

AICore загружает модели on demand. Первый вызов может потребовать загрузки 300+ MB. Если пользователь в этот момент без Wi-Fi -- модель не загрузится. Всегда проверяйте `FeatureStatus.DOWNLOADING` и информируйте пользователя.

### 3. Privacy perception vs reality

On-device означает "данные не отправляются для inference". Но:

- Приложение всё ещё может логировать ввод и результат
- Crash reports могут содержать фрагменты данных
- Analytics SDK могут отслеживать использование AI-фич

Честная on-device privacy требует осознанного подхода ко всему data pipeline.

### 4. Testing в CI: нет реального железа

On-device AI невозможно полноценно протестировать в эмуляторе. MediaPipe LLM Inference API прямо указывает: "does not reliably support device emulators". Стратегии:

- **Unit-тесты:** мокайте AI-интерфейсы (`TextSummarizer` в примере выше)
- **Integration-тесты:** Firebase Test Lab с реальными устройствами
- **Quality-тесты:** отдельный pipeline с golden datasets на реальных Pixel/Samsung

### 5. Версионирование моделей

AICore обновляет модели через Google Play Services. Это означает:

- Вы **не контролируете** версию модели на устройстве пользователя
- Результаты inference могут меняться между обновлениями
- Regression testing должен быть continuous

---

## Проверь себя

### Q1: Какой API использовать для OCR на бюджетном Android-устройстве?

**A:** ML Kit Classic Text Recognition. Он работает на любом Android 5.0+ устройстве, не требует AICore или premium-железа. Модель занимает 1-5 MB и обрабатывает текст за 5-30 ms.

### Q2: Чем отличается Prompt API от Summarization API в ML Kit?

**A:** Summarization API -- use-case specific: вы даёте текст, получаете краткое содержание. Prompt API -- general-purpose: вы отправляете произвольный промпт (текстовый или мультимодальный) и получаете ответ. Prompt API даёт полный контроль, но находится в Alpha и лучше работает на Pixel 10 (nano-v3).

### Q3: Почему нельзя полагаться только на on-device AI в production-приложении?

**A:** Device fragmentation. Gemini Nano доступен менее чем на 10% устройств. Обязательна fallback-стратегия: on-device -> cloud API -> graceful degradation. Кроме того, AICore загружает модели по требованию (300+ MB), что создаёт задержку при первом использовании.

### Q4: В чём разница между MediaPipe LLM Inference и ML Kit GenAI?

**A:** ML Kit GenAI использует Gemini Nano через AICore (Google управляет моделью). MediaPipe LLM Inference позволяет загружать и запускать собственные модели (Gemma 3n, кастомные .task файлы) -- вы полностью контролируете модель, но сами отвечаете за размер, загрузку и обновления.

---

## Ключевые карточки

**Card 1. AICore** -- системный сервис Android 14+, управляющий on-device GenAI моделями. Скачивает, обновляет, оптимизирует inference Gemini Nano. Разработчик не управляет моделью напрямую.

**Card 2. ML Kit GenAI APIs** -- высокоуровневые API (Summarization, Proofreading, Image Description, Prompt API), работающие поверх AICore и Gemini Nano. Рекомендуемый способ интеграции on-device GenAI.

**Card 3. Gemma 3n** -- open-source мультимодальная модель Google (text + image + audio), работающая на устройствах с 2 GB RAM. Архитектурная основа Gemini Nano v3. Доступна через MediaPipe LLM Inference API.

**Card 4. Quantization trade-off** -- FP32 -> INT8 уменьшает размер модели в 4x с потерей 1-3% accuracy. INT4 -- ещё в 2x, но с потерей 3-7%. Для production на мобиле рекомендуется INT8.

**Card 5. Fallback pattern** -- on-device AI проектируется как progressive enhancement: (1) проверить доступность Gemini Nano, (2) если нет -- cloud API, (3) если нет сети -- graceful degradation. Никогда не делайте GenAI единственным путём.

**Card 6. LiteRT (TFLite)** -- runtime для custom ML-моделей. Поддерживает CPU/GPU/NPU delegates, quantization, on-device training. NNAPI deprecated -- замена через LiteRT vendor delegates напрямую.

---

## Куда дальше

- **[[mobile-ai-ml-guide]]** -- общий ландшафт мобильного ML, включая iOS (Core ML) и кроссплатформенные решения
- **[[android-app-startup-performance]]** -- оптимизация времени запуска с учётом ML warm-up
- **[[android-permissions-security]]** -- privacy-аспекты работы с пользовательскими данными
- **[[android-performance-profiling]]** -- профилирование battery и memory при ML inference

---

## Источники

- [Gemini Nano -- Android Developers](https://developer.android.com/ai/gemini-nano)
- [ML Kit GenAI APIs -- Android Developers](https://developer.android.com/ai/gemini-nano/ml-kit-genai)
- [ML Kit GenAI Overview -- Google for Developers](https://developers.google.com/ml-kit/genai)
- [ML Kit Prompt API -- Google for Developers](https://developers.google.com/ml-kit/genai/prompt/android)
- [On-device GenAI APIs as part of ML Kit -- Android Developers Blog (May 2025)](https://android-developers.googleblog.com/2025/05/on-device-gen-ai-apis-ml-kit-gemini-nano.html)
- [Latest Gemini Nano with ML Kit GenAI APIs -- Android Developers Blog (Aug 2025)](https://android-developers.googleblog.com/2025/08/the-latest-gemini-nano-with-on-device-ml-kit-genai-apis.html)
- [ML Kit Prompt API Alpha Release -- Android Developers Blog (Oct 2025)](https://android-developers.googleblog.com/2025/10/ml-kit-genai-prompt-api-alpha-release.html)
- [LiteRT (TensorFlow Lite) -- Google AI Edge](https://ai.google.dev/edge/litert)
- [MediaPipe LLM Inference -- Google AI Edge](https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference/android)
- [Gemma 3n -- Google DeepMind](https://deepmind.google/models/gemma/gemma-3n/)
- [ML Kit -- Google for Developers](https://developers.google.com/ml-kit)
- [Google AI Edge SDK -- Android Developers](https://developer.android.com/ai/gemini-nano/ai-edge-sdk)

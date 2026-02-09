---
title: "AsyncTask: история, проблемы и уроки"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [thread-pool, producer-consumer, callback-pattern, memory-leak-patterns]
tags:
  - topic/android
  - topic/threading
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-async-evolution]]"
  - "[[android-handler-looper]]"
  - "[[android-executors]]"
  - "[[android-threading]]"
---

# AsyncTask: история, проблемы и уроки

## История создания: зачем нужен был AsyncTask

### Проблема: Thread + Handler слишком verbose

В ранних версиях Android (2008-2009) для выполнения фоновой работы и обновления UI разработчики использовали комбинацию `Thread` и `Handler`. Типичный код выглядел так:

```java
// Android 1.x-2.x: типичный паттерн для фоновой работы
public class MainActivity extends Activity {
    private Handler handler = new Handler();

    private void loadData() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                // Фоновая работа
                final String result = downloadData();

                // Переключение на UI thread
                handler.post(new Runnable() {
                    @Override
                    public void run() {
                        // Обновление UI
                        textView.setText(result);
                    }
                });
            }
        }).start();
    }
}
```

Проблемы такого подхода:
- Слишком много boilerplate кода
- Легко забыть про переключение на UI thread
- Нет стандартизации обработки прогресса
- Сложно отменить операцию
- Нет встроенной обработки ошибок

### Решение: простая абстракция для UI-bound задач

В Android 1.5 (API 3, Cupcake, апрель 2009) Google представил `AsyncTask` — класс, который инкапсулировал всю сложность Thread + Handler в простой API:

```java
// Android 1.5+: простой AsyncTask
private class DownloadTask extends AsyncTask<URL, Integer, String> {
    @Override
    protected String doInBackground(URL... urls) {
        return downloadData(urls[0]);
    }

    @Override
    protected void onPostExecute(String result) {
        textView.setText(result);
    }
}

// Использование
new DownloadTask().execute(url);
```

### Первоначальный дизайн и предполагаемое использование

AsyncTask проектировался для:
- **Коротких операций** (несколько секунд максимум)
- **UI-bound задач** (результат нужен для обновления UI)
- **Простых случаев** (скачать данные, обработать, показать)

**Официальная документация (2009):**
> "AsyncTask enables proper and easy use of the UI thread. This class allows you to perform background operations and publish results on the UI thread without having to manipulate threads and/or handlers."

### Google Blog 2009: "Painless threading"

В 2009 году Android Developers Blog опубликовал статью "Painless Threading" Гуса Сакласа (Gus Saklatvala), где AsyncTask представлялся как решение всех проблем многопоточности:

**Цитата:**
> "AsyncTask is designed to be a helper class around Thread and Handler and does not constitute a generic threading framework. AsyncTasks should ideally be used for short operations (a few seconds at the most.)"

Ключевое слово — **"ideally"**. На практике разработчики начали использовать AsyncTask для всего подряд.

---

## API и lifecycle AsyncTask

### Структура класса

```java
public abstract class AsyncTask<Params, Progress, Result> {
    // Lifecycle методы
    protected void onPreExecute() { }
    protected abstract Result doInBackground(Params... params);
    protected void onProgressUpdate(Progress... values) { }
    protected void onPostExecute(Result result) { }
    protected void onCancelled(Result result) { }
    protected void onCancelled() { }

    // Execution методы
    public final AsyncTask<Params, Progress, Result> execute(Params... params);
    public final AsyncTask<Params, Progress, Result> executeOnExecutor(
        Executor exec, Params... params);

    // Utility методы
    public final boolean cancel(boolean mayInterruptIfRunning);
    protected final void publishProgress(Progress... values);
    public final boolean isCancelled();
}
```

### Generics: AsyncTask<Params, Progress, Result>

- **Params** — тип параметров для `doInBackground()`
- **Progress** — тип для обновления прогресса
- **Result** — тип результата

Если параметр не нужен, используется `Void`:

```java
// Нет параметров, нет прогресса, возвращает String
private class SimpleTask extends AsyncTask<Void, Void, String> {
    @Override
    protected String doInBackground(Void... params) {
        return "Done";
    }
}
```

### Lifecycle методы

#### 1. onPreExecute()

Вызывается **на UI thread** перед началом фоновой работы:

```java
@Override
protected void onPreExecute() {
    super.onPreExecute();
    // Показать ProgressBar
    progressBar.setVisibility(View.VISIBLE);
    // Отключить кнопки
    submitButton.setEnabled(false);
}
```

**Использование:**
- Показать индикатор загрузки
- Отключить UI элементы
- Сохранить начальное состояние

#### 2. doInBackground(Params...)

Вызывается **на background thread**. Единственный метод, который выполняется не на UI thread:

```java
@Override
protected String doInBackground(URL... urls) {
    String result = "";
    for (int i = 0; i < urls.length; i++) {
        // Проверка отмены
        if (isCancelled()) break;

        result += downloadUrl(urls[i]);

        // Публикация прогресса
        publishProgress((i + 1) * 100 / urls.length);
    }
    return result;
}
```

**Важно:**
- НЕ обращайтесь к View напрямую
- Используйте `publishProgress()` для обновления UI
- Проверяйте `isCancelled()` регулярно
- Возвращаемое значение передается в `onPostExecute()`

#### 3. onProgressUpdate(Progress...)

Вызывается **на UI thread** после вызова `publishProgress()`:

```java
@Override
protected void onProgressUpdate(Integer... values) {
    super.onProgressUpdate(values);
    // Обновить ProgressBar
    progressBar.setProgress(values[0]);
    statusText.setText("Loading: " + values[0] + "%");
}
```

#### 4. onPostExecute(Result)

Вызывается **на UI thread** после завершения `doInBackground()`:

```java
@Override
protected void onPostExecute(String result) {
    super.onPostExecute(result);
    // Скрыть индикатор
    progressBar.setVisibility(View.GONE);
    // Включить кнопки
    submitButton.setEnabled(true);
    // Показать результат
    resultTextView.setText(result);
}
```

#### 5. onCancelled() / onCancelled(Result)

Вызывается **на UI thread** вместо `onPostExecute()`, если задача была отменена:

```java
@Override
protected void onCancelled(String result) {
    super.onCancelled(result);
    // Очистка ресурсов
    progressBar.setVisibility(View.GONE);
    Toast.makeText(context, "Operation cancelled", Toast.LENGTH_SHORT).show();
}
```

### Полный пример

```java
public class DownloadImageTask extends AsyncTask<String, Integer, Bitmap> {
    private WeakReference<ImageView> imageViewRef;

    public DownloadImageTask(ImageView imageView) {
        this.imageViewRef = new WeakReference<>(imageView);
    }

    @Override
    protected void onPreExecute() {
        ImageView imageView = imageViewRef.get();
        if (imageView != null) {
            imageView.setImageResource(R.drawable.placeholder);
        }
    }

    @Override
    protected Bitmap doInBackground(String... urls) {
        String url = urls[0];
        Bitmap bitmap = null;

        try {
            InputStream in = new URL(url).openStream();
            bitmap = BitmapFactory.decodeStream(in);

            // Симуляция прогресса
            for (int i = 0; i <= 100; i += 10) {
                if (isCancelled()) break;
                publishProgress(i);
                Thread.sleep(100);
            }
        } catch (Exception e) {
            Log.e("DownloadImage", "Error downloading", e);
        }

        return bitmap;
    }

    @Override
    protected void onProgressUpdate(Integer... progress) {
        Log.d("DownloadImage", "Progress: " + progress[0] + "%");
    }

    @Override
    protected void onPostExecute(Bitmap result) {
        ImageView imageView = imageViewRef.get();
        if (imageView != null && result != null) {
            imageView.setImageBitmap(result);
        }
    }

    @Override
    protected void onCancelled() {
        Log.d("DownloadImage", "Download cancelled");
    }
}
```

---

## Эволюция поведения: критические изменения

### Android 1.6 - 2.3 (API 4-10): параллельный thread pool

**Первоначальная реализация:**
```java
// AsyncTask.java (Android 1.6-2.3)
private static final int CORE_POOL_SIZE = 5;
private static final int MAXIMUM_POOL_SIZE = 128;

private static final ThreadPoolExecutor sExecutor =
    new ThreadPoolExecutor(
        CORE_POOL_SIZE,
        MAXIMUM_POOL_SIZE,
        1, TimeUnit.SECONDS,
        new LinkedBlockingQueue<Runnable>(10)
    );
```

**Поведение:**
- До 5 задач выполняются параллельно
- Очередь до 10 задач
- Максимум 128 потоков
- **Задачи выполняются в произвольном порядке**

**Проблема:**
```java
// Три задачи запускаются параллельно
new DownloadTask().execute("url1"); // Может завершиться второй
new DownloadTask().execute("url2"); // Может завершиться первый
new DownloadTask().execute("url3"); // Может завершиться третий
```

Это приводило к **race conditions** и непредсказуемым результатам.

### Android 3.0+ (API 11+): SERIAL_EXECUTOR по умолчанию

**Критическое изменение в Android Honeycomb (2011):**

```java
// AsyncTask.java (Android 3.0+)
public static final Executor SERIAL_EXECUTOR = new SerialExecutor();

private static class SerialExecutor implements Executor {
    final ArrayDeque<Runnable> mTasks = new ArrayDeque<Runnable>();
    Runnable mActive;

    public synchronized void execute(final Runnable r) {
        mTasks.offer(new Runnable() {
            public void run() {
                try {
                    r.run();
                } finally {
                    scheduleNext();
                }
            }
        });
        if (mActive == null) {
            scheduleNext();
        }
    }

    protected synchronized void scheduleNext() {
        if ((mActive = mTasks.poll()) != null) {
            THREAD_POOL_EXECUTOR.execute(mActive);
        }
    }
}

private static volatile Executor sDefaultExecutor = SERIAL_EXECUTOR;
```

**Поведение:**
- **Только одна задача выполняется одновременно**
- Остальные ждут в очереди
- Гарантированный порядок выполнения (FIFO)

**Почему изменили:**

1. **Устранение race conditions:**
```java
// Теперь выполняется последовательно: 1 → 2 → 3
new DownloadTask().execute("url1"); // Выполнится первым
new DownloadTask().execute("url2"); // Выполнится вторым
new DownloadTask().execute("url3"); // Выполнится третьим
```

2. **Предсказуемое поведение для разработчиков**

3. **Защита от thread pool starvation**

**Цитата из официального changelog:**
> "When first introduced, AsyncTasks were executed serially on a single background thread. Starting with DONUT, this was changed to a pool of threads allowing multiple tasks to operate in parallel. Starting with HONEYCOMB, tasks are executed on a single thread to avoid common application errors caused by parallel execution."

### executeOnExecutor() для параллельного выполнения

Для обратной совместимости добавили `executeOnExecutor()`:

```java
// Android 3.0+
// Последовательное выполнение (по умолчанию)
new DownloadTask().execute(url);

// Параллельное выполнение (как в Android 2.x)
new DownloadTask().executeOnExecutor(
    AsyncTask.THREAD_POOL_EXECUTOR,
    url
);

// Собственный Executor
Executor customExecutor = Executors.newFixedThreadPool(4);
new DownloadTask().executeOnExecutor(customExecutor, url);
```

**Когда использовать параллельное выполнение:**
- Независимые задачи (нет shared state)
- Множественные сетевые запросы
- Обработка изображений

**Когда использовать последовательное выполнение:**
- Операции с базой данных
- Работа с файлами
- Любые операции с shared state

### Проблемы, которые это решило

**До Android 3.0 (параллельный pool):**
```java
// Проблема: race condition
private int counter = 0;

for (int i = 0; i < 10; i++) {
    new AsyncTask<Void, Void, Void>() {
        @Override
        protected Void doInBackground(Void... params) {
            counter++; // Race condition!
            return null;
        }
    }.execute();
}
// counter может быть любым от 1 до 10
```

**После Android 3.0 (последовательный executor):**
```java
// Проблема решена: последовательное выполнение
for (int i = 0; i < 10; i++) {
    new AsyncTask<Void, Void, Void>() {
        @Override
        protected Void doInBackground(Void... params) {
            counter++; // Безопасно
            return null;
        }
    }.execute();
}
// counter всегда будет 10
```

### Проблемы, которые это создало

**Новая проблема: блокировка очереди**

```java
// Первая задача блокирует очередь на 10 секунд
new AsyncTask<Void, Void, Void>() {
    @Override
    protected Void doInBackground(Void... params) {
        Thread.sleep(10000); // 10 секунд
        return null;
    }
}.execute();

// Эти задачи ждут первую, даже если могут выполняться параллельно
new QuickTask1().execute(); // Ждет 10 секунд
new QuickTask2().execute(); // Ждет 10+ секунд
new QuickTask3().execute(); // Ждет 10++ секунд
```

**Решение:**
```java
// Быстрые независимые задачи - параллельно
new QuickTask1().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
new QuickTask2().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
new QuickTask3().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
```

---

## 5 главных проблем AsyncTask

### Проблема 1: Memory leaks — implicit reference к Activity/Fragment

#### Суть проблемы

AsyncTask, объявленный как **внутренний нестатический класс**, содержит **неявную ссылку** на внешний класс (Activity/Fragment). Это предотвращает garbage collection Activity даже после её уничтожения.

#### Проблемный код

```java
public class MainActivity extends AppCompatActivity {
    private TextView resultTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        resultTextView = findViewById(R.id.resultTextView);

        // Запускаем долгую задачу
        new LongRunningTask().execute();
    }

    // ПРОБЛЕМА: нестатический внутренний класс
    private class LongRunningTask extends AsyncTask<Void, Void, String> {
        @Override
        protected String doInBackground(Void... params) {
            // Симуляция долгой работы
            try {
                Thread.sleep(30000); // 30 секунд
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            return "Task completed";
        }

        @Override
        protected void onPostExecute(String result) {
            // Обращение к полю Activity
            resultTextView.setText(result);
        }
    }
}
```

#### Что происходит

1. Пользователь запускает Activity
2. AsyncTask начинает выполнение (30 секунд)
3. Пользователь поворачивает экран через 5 секунд
4. Activity уничтожается (onDestroy())
5. Создается новая Activity
6. **Старая Activity не может быть удалена GC, потому что AsyncTask держит на неё ссылку**
7. AsyncTask завершается через 30 секунд и пытается обновить UI старой Activity

#### Как обнаружить

**LeakCanary:**
```
┬───
│ GC Root: Thread
│
├─ java.lang.Thread instance
│    name = "AsyncTask #1"
│    ↓ Thread.target
├─ AsyncTask$3 instance
│    ↓ AsyncTask$3.this$0
├─ MainActivity instance
│    Leaking: YES (Activity destroyed but still in memory)
│    ↓ MainActivity.resultTextView
└─ TextView instance
```

**Android Studio Profiler:**
- Memory Profiler → Dump heap
- Analyze → Detect Leaks
- Найти экземпляры Activity > 1 для одного класса

**Симптомы:**
- Увеличение потребления памяти со временем
- OutOfMemoryError при длительном использовании
- Множественные экземпляры Activity в heap dump

#### Исправление

**Решение 1: Статический класс + WeakReference**

```java
public class MainActivity extends AppCompatActivity {
    private TextView resultTextView;
    private LongRunningTask task;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        resultTextView = findViewById(R.id.resultTextView);

        task = new LongRunningTask(this);
        task.execute();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Отменить задачу
        if (task != null) {
            task.cancel(true);
        }
    }

    // РЕШЕНИЕ: статический класс
    private static class LongRunningTask extends AsyncTask<Void, Void, String> {
        // WeakReference предотвращает утечку
        private WeakReference<MainActivity> activityRef;

        LongRunningTask(MainActivity activity) {
            this.activityRef = new WeakReference<>(activity);
        }

        @Override
        protected String doInBackground(Void... params) {
            try {
                Thread.sleep(30000);
            } catch (InterruptedException e) {
                return null;
            }
            return "Task completed";
        }

        @Override
        protected void onPostExecute(String result) {
            // Проверка, что Activity ещё жива
            MainActivity activity = activityRef.get();
            if (activity != null && !activity.isFinishing()) {
                activity.resultTextView.setText(result);
            }
        }
    }
}
```

**Решение 2: Отмена в onDestroy()**

```java
@Override
protected void onDestroy() {
    super.onDestroy();

    // Отменить задачу и прервать поток
    if (task != null && task.getStatus() != AsyncTask.Status.FINISHED) {
        task.cancel(true);
        task = null;
    }
}
```

---

### Проблема 2: Configuration change crashes — Activity уничтожена, AsyncTask пытается обновить UI

#### Суть проблемы

При повороте экрана (или любом configuration change) Activity уничтожается и пересоздается, но AsyncTask продолжает работать со ссылкой на **старую уничтоженную Activity**.

#### Проблемный код

```java
public class DownloadActivity extends AppCompatActivity {
    private ProgressBar progressBar;
    private TextView statusText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_download);

        progressBar = findViewById(R.id.progressBar);
        statusText = findViewById(R.id.statusText);

        // Запуск задачи
        new DownloadTask().execute("https://example.com/largefile.zip");
    }

    private class DownloadTask extends AsyncTask<String, Integer, String> {
        @Override
        protected void onPreExecute() {
            progressBar.setVisibility(View.VISIBLE);
            statusText.setText("Downloading...");
        }

        @Override
        protected String doInBackground(String... urls) {
            // Симуляция скачивания
            for (int i = 0; i <= 100; i++) {
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    return null;
                }
                publishProgress(i);
            }
            return "Download complete";
        }

        @Override
        protected void onProgressUpdate(Integer... progress) {
            // ПРОБЛЕМА: progressBar может быть null или из старой Activity
            progressBar.setProgress(progress[0]);
            statusText.setText("Progress: " + progress[0] + "%");
        }

        @Override
        protected void onPostExecute(String result) {
            // ПРОБЛЕМА: Views из старой Activity
            progressBar.setVisibility(View.GONE);
            statusText.setText(result);
        }
    }
}
```

#### Что происходит

**Сценарий краша:**
1. Пользователь запускает скачивание (10 секунд)
2. Через 3 секунды поворачивает экран
3. Android уничтожает старую Activity
4. `progressBar` и `statusText` из старой Activity больше не валидны
5. AsyncTask продолжает работать и вызывает `onProgressUpdate()`
6. **Попытка обновить View из уничтоженной Activity**

**Результат:**
```
java.lang.NullPointerException:
    Attempt to invoke virtual method 'void android.widget.ProgressBar.setProgress(int)'
    on a null object reference
```

Или ещё хуже:
```
android.view.WindowLeaked:
    Activity com.example.DownloadActivity has leaked window
```

#### Как обнаружить

**Logcat при повороте экрана:**
```
E/AndroidRuntime: FATAL EXCEPTION: main
    android.view.ViewRootImpl$CalledFromWrongThreadException:
    Only the original thread that created a view hierarchy can touch its views.
```

**Тестирование:**
1. Запустить долгую AsyncTask
2. Повернуть экран несколько раз
3. Наблюдать краши или странное поведение UI

**Android Studio:**
- Enable "Don't keep activities" в Developer Options
- Проверить восстановление после recreation

#### Исправление

**Решение 1: Сохранение и восстановление AsyncTask**

```java
public class DownloadActivity extends AppCompatActivity {
    private ProgressBar progressBar;
    private TextView statusText;
    private DownloadTask downloadTask;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_download);

        progressBar = findViewById(R.id.progressBar);
        statusText = findViewById(R.id.statusText);

        // Восстановление задачи после configuration change
        DownloadTask task = (DownloadTask) getLastCustomNonConfigurationInstance();
        if (task == null) {
            // Новая задача
            downloadTask = new DownloadTask(this);
            downloadTask.execute("https://example.com/largefile.zip");
        } else {
            // Переиспользуем существующую задачу
            downloadTask = task;
            downloadTask.attach(this);
        }
    }

    @Override
    public Object onRetainCustomNonConfigurationInstance() {
        // Сохраняем задачу перед уничтожением Activity
        if (downloadTask != null) {
            downloadTask.detach();
        }
        return downloadTask;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (downloadTask != null) {
            downloadTask.detach();
        }
    }

    private static class DownloadTask extends AsyncTask<String, Integer, String> {
        private WeakReference<DownloadActivity> activityRef;

        DownloadTask(DownloadActivity activity) {
            attach(activity);
        }

        void attach(DownloadActivity activity) {
            this.activityRef = new WeakReference<>(activity);
        }

        void detach() {
            this.activityRef.clear();
        }

        @Override
        protected void onPreExecute() {
            DownloadActivity activity = activityRef.get();
            if (activity != null) {
                activity.progressBar.setVisibility(View.VISIBLE);
                activity.statusText.setText("Downloading...");
            }
        }

        @Override
        protected String doInBackground(String... urls) {
            for (int i = 0; i <= 100; i++) {
                if (isCancelled()) break;

                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    return null;
                }
                publishProgress(i);
            }
            return "Download complete";
        }

        @Override
        protected void onProgressUpdate(Integer... progress) {
            DownloadActivity activity = activityRef.get();
            if (activity != null && !activity.isFinishing()) {
                activity.progressBar.setProgress(progress[0]);
                activity.statusText.setText("Progress: " + progress[0] + "%");
            }
        }

        @Override
        protected void onPostExecute(String result) {
            DownloadActivity activity = activityRef.get();
            if (activity != null && !activity.isFinishing()) {
                activity.progressBar.setVisibility(View.GONE);
                activity.statusText.setText(result);
            }
        }
    }
}
```

**Решение 2: Использование ViewModel + LiveData (современный подход)**

```java
// ViewModel переживает configuration changes
public class DownloadViewModel extends ViewModel {
    private MutableLiveData<Integer> progress = new MutableLiveData<>();
    private MutableLiveData<String> status = new MutableLiveData<>();

    public LiveData<Integer> getProgress() {
        return progress;
    }

    public LiveData<String> getStatus() {
        return status;
    }

    public void startDownload(String url) {
        new DownloadTask(progress, status).execute(url);
    }

    private static class DownloadTask extends AsyncTask<String, Integer, String> {
        private MutableLiveData<Integer> progress;
        private MutableLiveData<String> status;

        DownloadTask(MutableLiveData<Integer> progress, MutableLiveData<String> status) {
            this.progress = progress;
            this.status = status;
        }

        @Override
        protected String doInBackground(String... urls) {
            for (int i = 0; i <= 100; i++) {
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    return null;
                }
                publishProgress(i);
            }
            return "Download complete";
        }

        @Override
        protected void onProgressUpdate(Integer... values) {
            progress.postValue(values[0]);
        }

        @Override
        protected void onPostExecute(String result) {
            status.postValue(result);
        }
    }
}

// Activity
public class DownloadActivity extends AppCompatActivity {
    private DownloadViewModel viewModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_download);

        ProgressBar progressBar = findViewById(R.id.progressBar);
        TextView statusText = findViewById(R.id.statusText);

        viewModel = new ViewModelProvider(this).get(DownloadViewModel.class);

        // Наблюдение за данными
        viewModel.getProgress().observe(this, progress -> {
            progressBar.setProgress(progress);
        });

        viewModel.getStatus().observe(this, status -> {
            statusText.setText(status);
        });

        // Запуск только при первом создании
        if (savedInstanceState == null) {
            viewModel.startDownload("https://example.com/largefile.zip");
        }
    }
}
```

---

### Проблема 3: Lifecycle unawareness — не знает о lifecycle компонента

#### Суть проблемы

AsyncTask не интегрирован с Android Lifecycle. Он не знает о состояниях Activity/Fragment (onPause, onStop, onDestroy) и продолжает работать даже когда компонент невидим или уничтожен.

#### Проблемный код

```java
public class UserProfileActivity extends AppCompatActivity {
    private ImageView avatarImageView;
    private TextView nameTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_profile);

        avatarImageView = findViewById(R.id.avatarImageView);
        nameTextView = findViewById(R.id.nameTextView);

        // Загрузка данных пользователя
        new LoadUserDataTask().execute("user123");
    }

    private class LoadUserDataTask extends AsyncTask<String, Void, UserData> {
        @Override
        protected UserData doInBackground(String... userIds) {
            // Долгий запрос к серверу (5 секунд)
            return api.getUserData(userIds[0]);
        }

        @Override
        protected void onPostExecute(UserData userData) {
            // ПРОБЛЕМА: Activity может быть в onPause/onStop
            nameTextView.setText(userData.getName());
            loadImageIntoView(avatarImageView, userData.getAvatarUrl());
        }
    }
}
```

#### Что происходит

**Сценарий 1: Activity в background**
1. Пользователь открывает Activity
2. LoadUserDataTask начинает работу (5 секунд)
3. Через 1 секунду пользователь нажимает Home
4. Activity переходит в onPause() → onStop()
5. AsyncTask завершается через 5 секунд
6. **onPostExecute() обновляет UI невидимой Activity**
7. Растрата ресурсов батареи и CPU

**Сценарий 2: Быстрое закрытие Activity**
1. Пользователь открывает Activity
2. LoadUserDataTask начинает работу
3. Через 0.5 секунды пользователь нажимает Back
4. Activity уничтожается (onDestroy())
5. AsyncTask продолжает работу и выполняет сетевой запрос
6. **Бессмысленная трата сетевого трафика и батареи**

**Сценарий 3: Fragment transaction**
```java
// Fragment с AsyncTask
public class UserListFragment extends Fragment {
    @Override
    public void onViewCreated(View view, Bundle savedInstanceState) {
        // Загрузка списка
        new LoadUsersTask().execute();
    }

    private class LoadUsersTask extends AsyncTask<Void, Void, List<User>> {
        @Override
        protected List<User> doInBackground(Void... params) {
            return api.getUsers(); // 3 секунды
        }

        @Override
        protected void onPostExecute(List<User> users) {
            // ПРОБЛЕМА: Fragment может быть detached
            adapter.setUsers(users); // CRASH!
        }
    }
}

// Activity заменяет Fragment
getSupportFragmentManager()
    .beginTransaction()
    .replace(R.id.container, new OtherFragment())
    .commit();

// UserListFragment detached, но AsyncTask продолжает работать
```

#### Как обнаружить

**Логи при закрытии Activity:**
```
D/UserProfileActivity: onPause
D/UserProfileActivity: onStop
D/UserProfileActivity: onDestroy
D/AsyncTask: doInBackground() still running... // ПРОБЛЕМА!
D/AsyncTask: onPostExecute() called after destroy // ПРОБЛЕМА!
```

**Battery Profiler в Android Studio:**
- Обнаружение фоновой активности после закрытия Activity
- Unnecessary network requests после onStop

**Симптомы:**
- Быстрая разрядка батареи
- Сетевые запросы после закрытия экрана
- Краши при обращении к Views после detach

#### Исправление

**Решение 1: Ручная проверка lifecycle state**

```java
public class UserProfileActivity extends AppCompatActivity {
    private LoadUserDataTask task;
    private boolean isActivityVisible = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_profile);

        task = new LoadUserDataTask(this);
        task.execute("user123");
    }

    @Override
    protected void onStart() {
        super.onStart();
        isActivityVisible = true;
    }

    @Override
    protected void onStop() {
        super.onStop();
        isActivityVisible = false;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (task != null) {
            task.cancel(true);
        }
    }

    private static class LoadUserDataTask extends AsyncTask<String, Void, UserData> {
        private WeakReference<UserProfileActivity> activityRef;

        LoadUserDataTask(UserProfileActivity activity) {
            this.activityRef = new WeakReference<>(activity);
        }

        @Override
        protected UserData doInBackground(String... userIds) {
            // Проверка отмены перед долгой операцией
            if (isCancelled()) return null;

            return api.getUserData(userIds[0]);
        }

        @Override
        protected void onPostExecute(UserData userData) {
            UserProfileActivity activity = activityRef.get();

            // Проверка состояния Activity
            if (activity == null || activity.isFinishing() || activity.isDestroyed()) {
                Log.d("LoadUserData", "Activity not available, skipping UI update");
                return;
            }

            // Проверка видимости
            if (!activity.isActivityVisible) {
                Log.d("LoadUserData", "Activity not visible, skipping UI update");
                return;
            }

            // Безопасное обновление UI
            activity.nameTextView.setText(userData.getName());
            activity.loadImageIntoView(activity.avatarImageView, userData.getAvatarUrl());
        }
    }
}
```

**Решение 2: Использование Lifecycle-Aware компонентов**

```java
// Lifecycle-aware AsyncTask wrapper
public abstract class LifecycleAsyncTask<Params, Progress, Result>
        extends AsyncTask<Params, Progress, Result>
        implements LifecycleObserver {

    private WeakReference<LifecycleOwner> lifecycleOwnerRef;

    public LifecycleAsyncTask(LifecycleOwner lifecycleOwner) {
        this.lifecycleOwnerRef = new WeakReference<>(lifecycleOwner);
        lifecycleOwner.getLifecycle().addObserver(this);
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
    public void onDestroy() {
        cancel(true);
        LifecycleOwner owner = lifecycleOwnerRef.get();
        if (owner != null) {
            owner.getLifecycle().removeObserver(this);
        }
    }

    @Override
    protected final void onPostExecute(Result result) {
        LifecycleOwner owner = lifecycleOwnerRef.get();
        if (owner != null && owner.getLifecycle().getCurrentState()
                .isAtLeast(Lifecycle.State.STARTED)) {
            onPostExecuteWithLifecycle(result);
        }
    }

    protected abstract void onPostExecuteWithLifecycle(Result result);
}

// Использование
public class UserProfileActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_profile);

        new LifecycleAsyncTask<String, Void, UserData>(this) {
            @Override
            protected UserData doInBackground(String... userIds) {
                return api.getUserData(userIds[0]);
            }

            @Override
            protected void onPostExecuteWithLifecycle(UserData userData) {
                // Вызывается только если Activity STARTED или выше
                nameTextView.setText(userData.getName());
            }
        }.execute("user123");
    }
}
```

**Решение 3: Coroutines + Lifecycle (современный подход)**

```kotlin
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user_profile)

        // Автоматическая отмена при onDestroy
        lifecycleScope.launch {
            val userData = withContext(Dispatchers.IO) {
                api.getUserData("user123")
            }

            // Выполнится только если Activity жива
            nameTextView.text = userData.name
        }
    }
}
```

---

### Проблема 4: Silent exception swallowing — исключения в doInBackground теряются

#### Суть проблемы

Исключения, брошенные в `doInBackground()`, **молча проглатываются** AsyncTask. `onPostExecute()` не вызывается, приложение продолжает работать, но без результата и без уведомления об ошибке.

#### Проблемный код

```java
public class FetchDataActivity extends AppCompatActivity {
    private TextView dataTextView;
    private ProgressBar progressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fetch_data);

        dataTextView = findViewById(R.id.dataTextView);
        progressBar = findViewById(R.id.progressBar);

        new FetchDataTask().execute("https://api.example.com/data");
    }

    private class FetchDataTask extends AsyncTask<String, Void, String> {
        @Override
        protected void onPreExecute() {
            progressBar.setVisibility(View.VISIBLE);
            dataTextView.setText("Loading...");
        }

        @Override
        protected String doInBackground(String... urls) {
            // ПРОБЛЕМА: исключения здесь молча проглатываются
            String result = downloadData(urls[0]); // Может бросить IOException
            JSONObject json = new JSONObject(result); // Может бросить JSONException
            return json.getString("data");
        }

        @Override
        protected void onPostExecute(String result) {
            // НЕ ВЫЗЫВАЕТСЯ при исключении!
            progressBar.setVisibility(View.GONE);
            dataTextView.setText(result);
        }
    }
}
```

#### Что происходит

**Сценарий 1: Network exception**
```java
protected String doInBackground(String... urls) {
    // Нет сети - IOException
    return downloadData(urls[0]); // Бросает IOException
}

// Что происходит:
// 1. IOException брошен в doInBackground()
// 2. AsyncTask ловит исключение внутри
// 3. onPostExecute() НЕ ВЫЗЫВАЕТСЯ
// 4. ProgressBar остается видимым навсегда
// 5. Пользователь видит "Loading..." без возможности повторить
// 6. Никакого сообщения об ошибке
```

**Сценарий 2: Parse exception**
```java
protected String doInBackground(String... urls) {
    String result = downloadData(urls[0]);
    // Невалидный JSON - JSONException
    JSONObject json = new JSONObject(result); // Бросает JSONException
    return json.getString("data");
}

// Результат:
// - onPostExecute() не вызван
// - UI застрял в состоянии "Loading"
// - Нет информации для debugging
```

**Внутренняя реализация AsyncTask:**
```java
// AsyncTask.java (упрощенно)
private Result doInBackground(Params... params) {
    try {
        return doInBackground(params);
    } catch (Throwable tr) {
        // ПРОБЛЕМА: исключение проглатывается
        mCancelled.set(true);
        throw tr; // Но не передается в onPostExecute!
    }
}
```

#### Как обнаружить

**Симптомы:**
- ProgressBar не исчезает после загрузки
- UI застрял в промежуточном состоянии
- Данные не появляются, но и ошибки нет
- Logcat пустой (нет stack trace)

**Debugging:**
```java
@Override
protected String doInBackground(String... urls) {
    Log.d("FetchData", "Starting background work");

    try {
        String result = downloadData(urls[0]);
        Log.d("FetchData", "Download successful");
        return result;
    } catch (Exception e) {
        // Без этого catch исключение потеряется
        Log.e("FetchData", "Error in doInBackground", e);
        return null;
    }
}

// Logcat покажет:
// D/FetchData: Starting background work
// E/FetchData: Error in doInBackground
//     java.net.UnknownHostException: Unable to resolve host
```

**Android Studio Debugger:**
- Breakpoint в `doInBackground()`
- Exception breakpoints (Run → View Breakpoints → Java Exception Breakpoints)
- Добавить `Throwable` для отлова всех исключений

#### Исправление

**Решение 1: Try-catch с передачей ошибки**

```java
private class FetchDataTask extends AsyncTask<String, Void, TaskResult> {
    @Override
    protected TaskResult doInBackground(String... urls) {
        try {
            String data = downloadData(urls[0]);
            JSONObject json = new JSONObject(data);
            String result = json.getString("data");

            return new TaskResult(result, null);
        } catch (IOException e) {
            Log.e("FetchData", "Network error", e);
            return new TaskResult(null, e);
        } catch (JSONException e) {
            Log.e("FetchData", "Parse error", e);
            return new TaskResult(null, e);
        } catch (Exception e) {
            Log.e("FetchData", "Unexpected error", e);
            return new TaskResult(null, e);
        }
    }

    @Override
    protected void onPostExecute(TaskResult taskResult) {
        progressBar.setVisibility(View.GONE);

        if (taskResult.error != null) {
            // Обработка ошибки
            String errorMessage = getErrorMessage(taskResult.error);
            dataTextView.setText("Error: " + errorMessage);
            dataTextView.setTextColor(Color.RED);

            // Показать Snackbar с возможностью повтора
            Snackbar.make(dataTextView, errorMessage, Snackbar.LENGTH_LONG)
                .setAction("Retry", v -> new FetchDataTask().execute(urls))
                .show();
        } else {
            // Успех
            dataTextView.setText(taskResult.data);
            dataTextView.setTextColor(Color.BLACK);
        }
    }

    private String getErrorMessage(Exception error) {
        if (error instanceof IOException) {
            return "Network error. Check your connection.";
        } else if (error instanceof JSONException) {
            return "Invalid data format.";
        } else {
            return "Unexpected error occurred.";
        }
    }
}

// Вспомогательный класс для результата
private static class TaskResult {
    String data;
    Exception error;

    TaskResult(String data, Exception error) {
        this.data = data;
        this.error = error;
    }
}
```

**Решение 2: Sealed Result type (более type-safe)**

```java
// Result wrapper
private abstract static class Result<T> {
    private Result() {}

    static class Success<T> extends Result<T> {
        final T data;
        Success(T data) { this.data = data; }
    }

    static class Error<T> extends Result<T> {
        final Exception error;
        Error(Exception error) { this.error = error; }
    }
}

private class FetchDataTask extends AsyncTask<String, Void, Result<String>> {
    @Override
    protected Result<String> doInBackground(String... urls) {
        try {
            String data = downloadData(urls[0]);
            JSONObject json = new JSONObject(data);
            String result = json.getString("data");
            return new Result.Success<>(result);
        } catch (Exception e) {
            Log.e("FetchData", "Error", e);
            return new Result.Error<>(e);
        }
    }

    @Override
    protected void onPostExecute(Result<String> result) {
        progressBar.setVisibility(View.GONE);

        if (result instanceof Result.Success) {
            String data = ((Result.Success<String>) result).data;
            dataTextView.setText(data);
        } else if (result instanceof Result.Error) {
            Exception error = ((Result.Error<String>) result).error;
            dataTextView.setText("Error: " + error.getMessage());
        }
    }
}
```

**Решение 3: Callback interface для ошибок**

```java
private interface TaskCallback {
    void onSuccess(String data);
    void onError(Exception error);
}

private static class FetchDataTask extends AsyncTask<String, Void, Void> {
    private WeakReference<TaskCallback> callbackRef;
    private String resultData;
    private Exception resultError;

    FetchDataTask(TaskCallback callback) {
        this.callbackRef = new WeakReference<>(callback);
    }

    @Override
    protected Void doInBackground(String... urls) {
        try {
            String data = downloadData(urls[0]);
            JSONObject json = new JSONObject(data);
            resultData = json.getString("data");
        } catch (Exception e) {
            resultError = e;
            Log.e("FetchData", "Error", e);
        }
        return null;
    }

    @Override
    protected void onPostExecute(Void aVoid) {
        TaskCallback callback = callbackRef.get();
        if (callback != null) {
            if (resultError == null) {
                callback.onSuccess(resultData);
            } else {
                callback.onError(resultError);
            }
        }
    }
}

// Использование
new FetchDataTask(new TaskCallback() {
    @Override
    public void onSuccess(String data) {
        progressBar.setVisibility(View.GONE);
        dataTextView.setText(data);
    }

    @Override
    public void onError(Exception error) {
        progressBar.setVisibility(View.GONE);
        dataTextView.setText("Error: " + error.getMessage());
    }
}).execute("https://api.example.com/data");
```

---

### Проблема 5: Thread pool starvation — много AsyncTask'ов блокируют друг друга

#### Суть проблемы

Начиная с Android 3.0, AsyncTask использует **SERIAL_EXECUTOR** по умолчанию — только одна задача выполняется одновременно. Если одна долгая задача блокирует очередь, все остальные задачи ждут её завершения, даже если они независимы и могут выполняться параллельно.

#### Проблемный код

```java
public class GalleryActivity extends AppCompatActivity {
    private RecyclerView recyclerView;
    private ImageAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_gallery);

        recyclerView = findViewById(R.id.recyclerView);
        adapter = new ImageAdapter();
        recyclerView.setAdapter(adapter);

        // Загрузка 50 изображений
        String[] imageUrls = getImageUrls(); // 50 URLs

        for (String url : imageUrls) {
            // ПРОБЛЕМА: все задачи в serial queue
            new LoadImageTask().execute(url);
        }
    }

    private class LoadImageTask extends AsyncTask<String, Void, Bitmap> {
        @Override
        protected Bitmap doInBackground(String... urls) {
            // Загрузка изображения (2 секунды на каждое)
            return downloadBitmap(urls[0]);
        }

        @Override
        protected void onPostExecute(Bitmap bitmap) {
            adapter.addImage(bitmap);
        }
    }
}
```

#### Что происходит

**Сценарий: Serial execution bottleneck**

```
Task 1: [====================] 2 сек
Task 2:                         [====================] 2 сек
Task 3:                                                 [====================] 2 сек
...
Task 50:                                                                        ... 100 сек

Общее время: 50 задач × 2 сек = 100 секунд!
```

Вместо параллельной загрузки изображения загружаются последовательно.

**Проблема усугубляется:**

```java
// В другой части приложения
public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Критичная задача - проверка аутентификации
        new CheckAuthTask().execute();
    }

    private class CheckAuthTask extends AsyncTask<Void, Void, Boolean> {
        @Override
        protected Boolean doInBackground(Void... params) {
            return checkAuthentication(); // 1 секунда
        }

        @Override
        protected void onPostExecute(Boolean isAuthenticated) {
            if (!isAuthenticated) {
                // Redirect to login
                startActivity(new Intent(MainActivity.this, LoginActivity.class));
            }
        }
    }
}
```

**Что происходит:**
1. GalleryActivity запускает 50 LoadImageTask
2. Все 50 задач в serial queue
3. MainActivity запускает CheckAuthTask
4. **CheckAuthTask ждет завершения всех 50 LoadImageTask!**
5. Задержка аутентификации на 100 секунд
6. Плохой UX - пользователь не понимает, почему приложение "зависло"

#### Как обнаружить

**Симптомы:**
- Медленная загрузка списков/галерей
- ANR (Application Not Responding) dialogs
- Долгое ожидание между действиями пользователя
- "Ступенчатая" загрузка вместо плавной

**Логирование:**

```java
private class LoadImageTask extends AsyncTask<String, Void, Bitmap> {
    private long startTime;
    private String url;

    @Override
    protected void onPreExecute() {
        startTime = System.currentTimeMillis();
        Log.d("LoadImage", "Task queued: " + url);
    }

    @Override
    protected Bitmap doInBackground(String... urls) {
        url = urls[0];
        long waitTime = System.currentTimeMillis() - startTime;
        Log.d("LoadImage", "Task started after " + waitTime + "ms wait");

        Bitmap result = downloadBitmap(url);

        long totalTime = System.currentTimeMillis() - startTime;
        Log.d("LoadImage", "Task completed in " + totalTime + "ms");

        return result;
    }
}

// Logcat покажет:
// D/LoadImage: Task queued: url1
// D/LoadImage: Task queued: url2
// ...
// D/LoadImage: Task queued: url50
// D/LoadImage: Task started after 0ms wait (url1)
// D/LoadImage: Task completed in 2000ms (url1)
// D/LoadImage: Task started after 2000ms wait (url2)  // ПРОБЛЕМА!
// D/LoadImage: Task completed in 4000ms (url2)
// D/LoadImage: Task started after 4000ms wait (url3)  // ПРОБЛЕМА!
```

**Android Profiler:**
- CPU Profiler → Thread activity
- Наблюдение за `AsyncTask #1` thread
- Только один AsyncTask thread активен одновременно

**Systrace:**
```bash
python systrace.py -t 10 -o trace.html sched freq idle am wm gfx view
```

Покажет, что только один worker thread AsyncTask активен.

#### Исправление

**Решение 1: executeOnExecutor() с THREAD_POOL_EXECUTOR**

```java
public class GalleryActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_gallery);

        String[] imageUrls = getImageUrls();

        for (String url : imageUrls) {
            // РЕШЕНИЕ: параллельное выполнение
            new LoadImageTask().executeOnExecutor(
                AsyncTask.THREAD_POOL_EXECUTOR,
                url
            );
        }
    }

    private class LoadImageTask extends AsyncTask<String, Void, Bitmap> {
        @Override
        protected Bitmap doInBackground(String... urls) {
            return downloadBitmap(urls[0]);
        }

        @Override
        protected void onPostExecute(Bitmap bitmap) {
            adapter.addImage(bitmap);
        }
    }
}

// Результат:
// 50 задач выполняются параллельно
// Общее время: ~2-4 секунды (вместо 100)
```

**Параметры THREAD_POOL_EXECUTOR:**
```java
// AsyncTask.java
private static final int CORE_POOL_SIZE = CPU_COUNT + 1;
private static final int MAXIMUM_POOL_SIZE = CPU_COUNT * 2 + 1;

public static final Executor THREAD_POOL_EXECUTOR;

static {
    ThreadPoolExecutor threadPoolExecutor = new ThreadPoolExecutor(
        CORE_POOL_SIZE,
        MAXIMUM_POOL_SIZE,
        30, TimeUnit.SECONDS,
        new LinkedBlockingQueue<Runnable>(128)
    );
    threadPoolExecutor.allowCoreThreadTimeOut(true);
    THREAD_POOL_EXECUTOR = threadPoolExecutor;
}
```

На устройстве с 8 ядрами:
- Core pool: 9 threads
- Max pool: 17 threads
- Queue: 128 tasks

**Решение 2: Собственный Executor с оптимальными параметрами**

```java
public class ImageLoadingExecutor {
    // Оптимизированный executor для загрузки изображений
    private static final int CORE_POOL_SIZE = 4;  // 4 параллельных загрузки
    private static final int MAX_POOL_SIZE = 8;
    private static final int KEEP_ALIVE_TIME = 60; // seconds

    private static final Executor INSTANCE = new ThreadPoolExecutor(
        CORE_POOL_SIZE,
        MAX_POOL_SIZE,
        KEEP_ALIVE_TIME,
        TimeUnit.SECONDS,
        new LinkedBlockingQueue<>(),
        new ThreadFactory() {
            private final AtomicInteger count = new AtomicInteger(1);

            @Override
            public Thread newThread(Runnable r) {
                Thread thread = new Thread(r, "ImageLoader-" + count.getAndIncrement());
                thread.setPriority(Thread.NORM_PRIORITY - 1); // Низкий приоритет
                return thread;
            }
        }
    );

    public static Executor getExecutor() {
        return INSTANCE;
    }
}

// Использование
new LoadImageTask().executeOnExecutor(
    ImageLoadingExecutor.getExecutor(),
    url
);
```

**Решение 3: Приоритезация задач**

```java
// Критичные задачи - serial executor (по умолчанию)
new CheckAuthTask().execute(); // Выполнится первым

// Фоновые задачи - parallel executor
for (String url : imageUrls) {
    new LoadImageTask().executeOnExecutor(
        AsyncTask.THREAD_POOL_EXECUTOR,
        url
    );
}
```

**Решение 4: Ограничение числа параллельных задач**

```java
public class GalleryActivity extends AppCompatActivity {
    private static final int MAX_CONCURRENT_DOWNLOADS = 5;
    private final Semaphore semaphore = new Semaphore(MAX_CONCURRENT_DOWNLOADS);

    private class LoadImageTask extends AsyncTask<String, Void, Bitmap> {
        @Override
        protected Bitmap doInBackground(String... urls) {
            try {
                // Ограничение параллельных загрузок
                semaphore.acquire();

                return downloadBitmap(urls[0]);
            } catch (InterruptedException e) {
                return null;
            } finally {
                semaphore.release();
            }
        }

        @Override
        protected void onPostExecute(Bitmap bitmap) {
            if (bitmap != null) {
                adapter.addImage(bitmap);
            }
        }
    }

    // Запуск всех задач параллельно, но только 5 одновременно скачивают
    for (String url : imageUrls) {
        new LoadImageTask().executeOnExecutor(
            AsyncTask.THREAD_POOL_EXECUTOR,
            url
        );
    }
}
```

**Решение 5: Современные библиотеки (рекомендуется)**

Вместо AsyncTask используйте специализированные библиотеки:

```gradle
// Coil - современная библиотека для загрузки изображений
implementation("io.coil-kt:coil:2.5.0")
```

```kotlin
imageView.load(url) {
    crossfade(true)
    placeholder(R.drawable.placeholder)
    error(R.drawable.error)
}

// Coil автоматически:
// - Управляет thread pool
// - Кеширует изображения
// - Отменяет загрузку при detach View
// - Обрабатывает lifecycle
```

---

## Миграция на современные подходы

### AsyncTask → Kotlin Coroutines (рекомендуется)

Kotlin Coroutines — это современная замена AsyncTask с полной поддержкой lifecycle, structured concurrency и лучшей обработкой ошибок.

#### Шаг 1: Добавление зависимостей

```gradle
// build.gradle (app level)
dependencies {
    // Kotlin Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'

    // Lifecycle для lifecycleScope
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.2'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.2'
}
```

#### Шаг 2: Базовая миграция

**До (AsyncTask):**
```java
public class MainActivity extends AppCompatActivity {
    private TextView resultTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        resultTextView = findViewById(R.id.resultTextView);

        new DownloadTask().execute("https://api.example.com/data");
    }

    private class DownloadTask extends AsyncTask<String, Integer, String> {
        @Override
        protected void onPreExecute() {
            resultTextView.setText("Loading...");
        }

        @Override
        protected String doInBackground(String... urls) {
            return downloadData(urls[0]);
        }

        @Override
        protected void onPostExecute(String result) {
            resultTextView.setText(result);
        }
    }

    private String downloadData(String url) {
        // Network operation
        return "Data from " + url;
    }
}
```

**После (Coroutines):**
```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var resultTextView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        resultTextView = findViewById(R.id.resultTextView)

        // lifecycleScope автоматически отменяется при onDestroy
        lifecycleScope.launch {
            resultTextView.text = "Loading..."

            // Фоновая работа
            val result = withContext(Dispatchers.IO) {
                downloadData("https://api.example.com/data")
            }

            // Обновление UI (автоматически на Main thread)
            resultTextView.text = result
        }
    }

    private fun downloadData(url: String): String {
        // Network operation
        return "Data from $url"
    }
}
```

**Преимущества:**
- Автоматическая отмена при onDestroy
- Нет утечек памяти
- Читабельный последовательный код
- Встроенная обработка ошибок

#### Шаг 3: Миграция с обработкой прогресса

**До (AsyncTask с Progress):**
```java
private class DownloadFileTask extends AsyncTask<String, Integer, File> {
    @Override
    protected void onPreExecute() {
        progressBar.setVisibility(View.VISIBLE);
        progressBar.setProgress(0);
    }

    @Override
    protected File doInBackground(String... urls) {
        File outputFile = new File(getCacheDir(), "download.zip");

        try (InputStream input = new URL(urls[0]).openStream();
             FileOutputStream output = new FileOutputStream(outputFile)) {

            byte[] buffer = new byte[4096];
            long downloaded = 0;
            long total = getContentLength(urls[0]);
            int count;

            while ((count = input.read(buffer)) != -1) {
                downloaded += count;
                output.write(buffer, 0, count);

                // Обновление прогресса
                publishProgress((int) (downloaded * 100 / total));
            }
        } catch (IOException e) {
            return null;
        }

        return outputFile;
    }

    @Override
    protected void onProgressUpdate(Integer... values) {
        progressBar.setProgress(values[0]);
        statusText.setText("Downloaded: " + values[0] + "%");
    }

    @Override
    protected void onPostExecute(File file) {
        progressBar.setVisibility(View.GONE);

        if (file != null) {
            statusText.setText("Download complete: " + file.getAbsolutePath());
        } else {
            statusText.setText("Download failed");
        }
    }
}
```

**После (Coroutines с Flow):**
```kotlin
data class DownloadProgress(val downloaded: Long, val total: Long) {
    val percentage: Int get() = ((downloaded * 100) / total).toInt()
}

suspend fun downloadFile(url: String, outputFile: File): Flow<DownloadProgress> = flow {
    URL(url).openStream().use { input ->
        FileOutputStream(outputFile).use { output ->
            val buffer = ByteArray(4096)
            var downloaded = 0L
            val total = getContentLength(url)
            var count: Int

            while (input.read(buffer).also { count = it } != -1) {
                downloaded += count
                output.write(buffer, 0, count)

                // Эмиссия прогресса
                emit(DownloadProgress(downloaded, total))
            }
        }
    }
}.flowOn(Dispatchers.IO)

// Activity
class DownloadActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_download)

        val progressBar = findViewById<ProgressBar>(R.id.progressBar)
        val statusText = findViewById<TextView>(R.id.statusText)

        lifecycleScope.launch {
            progressBar.visibility = View.VISIBLE
            progressBar.progress = 0

            try {
                val outputFile = File(cacheDir, "download.zip")

                downloadFile("https://example.com/largefile.zip", outputFile)
                    .collect { progress ->
                        // Обновление прогресса
                        progressBar.progress = progress.percentage
                        statusText.text = "Downloaded: ${progress.percentage}%"
                    }

                // Завершение
                progressBar.visibility = View.GONE
                statusText.text = "Download complete: ${outputFile.absolutePath}"

            } catch (e: IOException) {
                progressBar.visibility = View.GONE
                statusText.text = "Download failed: ${e.message}"
            }
        }
    }
}
```

#### Шаг 4: Миграция с обработкой ошибок

**До (AsyncTask):**
```java
private static class FetchDataTask extends AsyncTask<String, Void, TaskResult> {
    private WeakReference<Activity> activityRef;

    FetchDataTask(Activity activity) {
        this.activityRef = new WeakReference<>(activity);
    }

    @Override
    protected TaskResult doInBackground(String... urls) {
        try {
            String data = downloadData(urls[0]);
            return new TaskResult(data, null);
        } catch (IOException e) {
            return new TaskResult(null, e);
        }
    }

    @Override
    protected void onPostExecute(TaskResult result) {
        Activity activity = activityRef.get();
        if (activity == null || activity.isFinishing()) return;

        if (result.error != null) {
            Toast.makeText(activity, "Error: " + result.error.getMessage(),
                Toast.LENGTH_SHORT).show();
        } else {
            ((TextView) activity.findViewById(R.id.resultTextView))
                .setText(result.data);
        }
    }
}
```

**После (Coroutines):**
```kotlin
class FetchDataActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_fetch_data)

        val resultTextView = findViewById<TextView>(R.id.resultTextView)

        lifecycleScope.launch {
            try {
                val data = withContext(Dispatchers.IO) {
                    downloadData("https://api.example.com/data")
                }

                resultTextView.text = data

            } catch (e: IOException) {
                Toast.makeText(
                    this@FetchDataActivity,
                    "Network error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()

            } catch (e: Exception) {
                Toast.makeText(
                    this@FetchDataActivity,
                    "Unexpected error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }
}
```

#### Шаг 5: Миграция с ViewModel

**Лучший подход для production:**

```kotlin
// ViewModel
class DataViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Idle : UiState()
        object Loading : UiState()
        data class Success(val data: String) : UiState()
        data class Error(val message: String) : UiState()
    }

    fun loadData(url: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val data = withContext(Dispatchers.IO) {
                    downloadData(url)
                }
                _uiState.value = UiState.Success(data)

            } catch (e: IOException) {
                _uiState.value = UiState.Error("Network error: ${e.message}")
            }
        }
    }

    private fun downloadData(url: String): String {
        // Network operation
        return "Data from $url"
    }
}

// Activity
class MainActivity : AppCompatActivity() {
    private val viewModel: DataViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val resultTextView = findViewById<TextView>(R.id.resultTextView)
        val progressBar = findViewById<ProgressBar>(R.id.progressBar)
        val retryButton = findViewById<Button>(R.id.retryButton)

        // Наблюдение за состоянием
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is DataViewModel.UiState.Idle -> {
                        progressBar.visibility = View.GONE
                        resultTextView.text = ""
                    }

                    is DataViewModel.UiState.Loading -> {
                        progressBar.visibility = View.VISIBLE
                        resultTextView.text = "Loading..."
                        retryButton.isEnabled = false
                    }

                    is DataViewModel.UiState.Success -> {
                        progressBar.visibility = View.GONE
                        resultTextView.text = state.data
                        retryButton.isEnabled = true
                    }

                    is DataViewModel.UiState.Error -> {
                        progressBar.visibility = View.GONE
                        resultTextView.text = state.message
                        retryButton.isEnabled = true
                    }
                }
            }
        }

        // Загрузка данных
        if (savedInstanceState == null) {
            viewModel.loadData("https://api.example.com/data")
        }

        retryButton.setOnClickListener {
            viewModel.loadData("https://api.example.com/data")
        }
    }
}
```

### AsyncTask → Executors + LiveData

Для проектов на Java без Kotlin.

**До (AsyncTask):**
```java
private class LoadDataTask extends AsyncTask<Void, Void, String> {
    @Override
    protected String doInBackground(Void... params) {
        return fetchDataFromNetwork();
    }

    @Override
    protected void onPostExecute(String result) {
        textView.setText(result);
    }
}

new LoadDataTask().execute();
```

**После (Executors + LiveData):**
```java
// ViewModel
public class DataViewModel extends ViewModel {
    private final MutableLiveData<String> dataLiveData = new MutableLiveData<>();
    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    public LiveData<String> getData() {
        return dataLiveData;
    }

    public void loadData() {
        executor.execute(() -> {
            // Фоновая работа
            String result = fetchDataFromNetwork();

            // Обновление LiveData (thread-safe)
            dataLiveData.postValue(result);
        });
    }

    @Override
    protected void onCleared() {
        super.onCleared();
        executor.shutdown();
    }

    private String fetchDataFromNetwork() {
        // Network operation
        return "Data from network";
    }
}

// Activity
public class MainActivity extends AppCompatActivity {
    private DataViewModel viewModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView textView = findViewById(R.id.textView);

        viewModel = new ViewModelProvider(this).get(DataViewModel.class);

        // Наблюдение за данными
        viewModel.getData().observe(this, data -> {
            textView.setText(data);
        });

        // Загрузка
        viewModel.loadData();
    }
}
```

### Чек-лист миграции

#### Подготовка
- [ ] Инвентаризация всех AsyncTask в проекте
- [ ] Анализ зависимостей и callback chains
- [ ] Определение стратегии миграции (Coroutines vs Executors)
- [ ] Добавление необходимых зависимостей

#### Для каждого AsyncTask
- [ ] Идентифицировать lifecycle owner (Activity/Fragment/ViewModel)
- [ ] Проверить наличие configuration change handling
- [ ] Проверить memory leaks (внутренний класс vs статический)
- [ ] Определить executor type (serial vs parallel)
- [ ] Проанализировать обработку ошибок

#### Миграция
- [ ] Заменить AsyncTask на Coroutine/Executor
- [ ] Использовать lifecycleScope/viewModelScope
- [ ] Добавить обработку ошибок (try-catch)
- [ ] Удалить WeakReference (больше не нужен)
- [ ] Убрать manual lifecycle management

#### Тестирование
- [ ] Unit tests для бизнес-логики
- [ ] Проверить configuration changes (поворот экрана)
- [ ] Проверить отмену при onDestroy
- [ ] LeakCanary проверка на утечки
- [ ] Performance testing (Profiler)

#### Очистка
- [ ] Удалить AsyncTask классы
- [ ] Удалить WeakReference wrappers
- [ ] Удалить TaskResult/Result wrappers (если использовались)
- [ ] Обновить документацию

---

## Уроки для индустрии

### Почему простые API скрывают сложность

AsyncTask был задуман как "простое решение" для threading, но эта простота была обманчивой.

**Иллюзия простоты:**
```java
// Кажется просто и понятно
new AsyncTask<Void, Void, String>() {
    @Override
    protected String doInBackground(Void... params) {
        return downloadData();
    }

    @Override
    protected void onPostExecute(String result) {
        textView.setText(result);
    }
}.execute();
```

**Скрытая сложность:**
- Memory leaks (implicit reference)
- Configuration changes (Activity recreation)
- Exception swallowing (silent failures)
- Thread pool starvation (serial executor)
- Lifecycle unawareness (no cancellation)

**Урок:**
> Простой API не должен скрывать фундаментальную сложность проблемы. Он должен делать правильное решение простым, но не скрывать edge cases.

**Сравнение с Coroutines:**
```kotlin
lifecycleScope.launch {
    try {
        val data = withContext(Dispatchers.IO) {
            downloadData()
        }
        textView.text = data
    } catch (e: Exception) {
        // Явная обработка ошибок
    }
}
```

Код немного длиннее, но:
- Explicit lifecycle management (`lifecycleScope`)
- Explicit threading (`Dispatchers.IO`)
- Explicit error handling (`try-catch`)
- No hidden pitfalls

### Lifecycle awareness как требование

AsyncTask был создан до появления Android Architecture Components и концепции lifecycle-aware компонентов.

**Проблема:**
```java
// AsyncTask не знает о lifecycle
new AsyncTask<>() {
    protected String doInBackground(Void... params) {
        // Activity может быть уничтожена
        return downloadData();
    }

    protected void onPostExecute(String result) {
        // Попытка обновить UI уничтоженной Activity
        textView.setText(result);
    }
}.execute();
```

**Решение в современных API:**
```kotlin
// lifecycleScope автоматически отменяется при onDestroy
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        downloadData()
    }
    textView.text = data // Безопасно
}
```

**Урок:**
> Любой API, работающий с асинхронностью в Android, должен быть lifecycle-aware по умолчанию.

**Примеры lifecycle-aware компонентов:**
- `LifecycleObserver` — наблюдение за lifecycle events
- `lifecycleScope` — coroutine scope привязанный к lifecycle
- `viewModelScope` — scope для ViewModel
- `LiveData` — lifecycle-aware observable
- `Flow.flowWithLifecycle()` — Flow с lifecycle awareness

### Structured concurrency как ответ

AsyncTask позволял "запустить и забыть" без контроля над выполнением.

**Проблема:**
```java
// Запустили 10 задач
for (int i = 0; i < 10; i++) {
    new DownloadTask().execute(urls[i]);
}

// Как отменить все? Как дождаться завершения всех?
// Нет встроенного механизма
```

**Structured Concurrency в Coroutines:**
```kotlin
lifecycleScope.launch {
    // Все дочерние coroutines автоматически отменяются
    // если родительский scope отменен

    val results = urls.map { url ->
        async(Dispatchers.IO) {
            downloadData(url)
        }
    }.awaitAll() // Дождаться всех

    // Если Activity уничтожена, все автоматически отменится
}
```

**Преимущества:**
- **Parent-child relationship:** отмена родителя отменяет всех детей
- **Exception propagation:** ошибка в дочернем coroutine отменяет всех siblings
- **Resource cleanup:** гарантированная очистка ресурсов
- **No leaks:** невозможно "забыть" про coroutine

**Урок:**
> Concurrency должна быть structured — четкая иерархия, автоматическая отмена, гарантированная очистка.

**Сравнение:**

| Aspect | AsyncTask | Coroutines |
|--------|-----------|------------|
| Cancellation | Manual, error-prone | Automatic, structured |
| Error handling | Silent swallowing | Explicit propagation |
| Lifecycle | Manual management | Automatic with scopes |
| Composition | Difficult (callbacks) | Easy (sequential code) |
| Testing | Complex mocking | Simple with TestDispatcher |

---

## Проверь себя

### Вопрос 1: Почему AsyncTask deprecated в API 30?

**Краткий ответ:**
AsyncTask deprecated из-за множества фундаментальных проблем: memory leaks, lifecycle unawareness, silent exception swallowing, и отсутствия structured concurrency.

**Подробный ответ:**

AsyncTask был объявлен deprecated в Android API 30 (Android 11, сентябрь 2020) по следующим причинам:

1. **Фундаментальные проблемы дизайна:**
   - Implicit reference к Activity/Fragment → memory leaks
   - Нет интеграции с Lifecycle → невозможность корректной отмены
   - Silent exception swallowing → сложный debugging
   - Serial executor по умолчанию → thread pool starvation

2. **Наличие лучших альтернатив:**
   - Kotlin Coroutines (с 2017) — modern, lifecycle-aware
   - RxJava — powerful reactive programming
   - Executors + LiveData — Java-friendly approach
   - WorkManager — для фоновых задач

3. **Несовместимость с современными паттернами:**
   - Нет поддержки structured concurrency
   - Callback-based API вместо sequential code
   - Невозможность composition (нельзя легко комбинировать задачи)

**Официальная документация (API 30):**
> "This class is deprecated. Use the standard java.util.concurrent or Kotlin concurrency utilities instead."

**Что использовать вместо:**
- **Kotlin:** Coroutines с `lifecycleScope` или `viewModelScope`
- **Java:** `java.util.concurrent.Executor` с `LiveData`
- **Background tasks:** `WorkManager`

### Вопрос 2: Что случится если повернуть экран во время AsyncTask?

**Сценарий:**
```java
public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        new LongTask().execute();
    }

    private class LongTask extends AsyncTask<Void, Void, String> {
        @Override
        protected String doInBackground(Void... params) {
            Thread.sleep(10000); // 10 секунд
            return "Done";
        }

        @Override
        protected void onPostExecute(String result) {
            textView.setText(result); // textView из старой Activity!
        }
    }
}
```

**Что происходит:**

1. **t=0s:** Activity создана, AsyncTask запущен
2. **t=3s:** Пользователь поворачивает экран
3. **t=3s:** Android вызывает `onDestroy()` для старой Activity
4. **t=3s:** Android создает новую Activity с `onCreate()`
5. **t=3s - 10s:** AsyncTask продолжает выполняться
6. **t=10s:** AsyncTask завершается и вызывает `onPostExecute()`
7. **t=10s:** Попытка обновить `textView` из **старой уничтоженной Activity**

**Возможные результаты:**

**Результат 1: NullPointerException**
```
java.lang.NullPointerException:
    Attempt to invoke virtual method 'void android.widget.TextView.setText(String)'
    on a null object reference
```

**Результат 2: Memory Leak**
- Старая Activity не может быть удалена GC
- AsyncTask держит ссылку на старую Activity
- При каждом повороте экрана — новая утечка
- OutOfMemoryError после нескольких поворотов

**Результат 3: Обновление неправильной Activity**
- Если `textView` не null, обновится View из старой Activity
- Новая Activity показывает старое состояние
- Пользователь не видит результата

**Результат 4: WindowLeaked Exception**
```
android.view.WindowLeaked:
    Activity com.example.MainActivity has leaked window
```

**Правильное решение:**
```java
private static class LongTask extends AsyncTask<Void, Void, String> {
    private WeakReference<MainActivity> activityRef;

    LongTask(MainActivity activity) {
        this.activityRef = new WeakReference<>(activity);
    }

    @Override
    protected String doInBackground(Void... params) {
        Thread.sleep(10000);
        return "Done";
    }

    @Override
    protected void onPostExecute(String result) {
        MainActivity activity = activityRef.get();
        if (activity != null && !activity.isFinishing() && !activity.isDestroyed()) {
            activity.textView.setText(result);
        }
    }
}

@Override
protected void onDestroy() {
    super.onDestroy();
    if (longTask != null) {
        longTask.cancel(true);
    }
}
```

### Вопрос 3: Чем execute() отличается от executeOnExecutor()?

**Краткий ответ:**
`execute()` использует `SERIAL_EXECUTOR` (одна задача за раз), `executeOnExecutor()` позволяет указать собственный executor для параллельного выполнения.

**Подробный ответ:**

**execute():**
```java
// Внутренняя реализация
public final AsyncTask<Params, Progress, Result> execute(Params... params) {
    return executeOnExecutor(sDefaultExecutor, params);
}

// sDefaultExecutor = SERIAL_EXECUTOR (с Android 3.0+)
private static volatile Executor sDefaultExecutor = SERIAL_EXECUTOR;
```

**Поведение:**
- Использует `SERIAL_EXECUTOR` по умолчанию
- **Только одна задача выполняется одновременно**
- Остальные ждут в очереди (FIFO)
- Гарантированный порядок выполнения

**Пример:**
```java
new Task1().execute(); // Выполняется сразу
new Task2().execute(); // Ждет Task1
new Task3().execute(); // Ждет Task1 и Task2

// Timeline:
// Task1: [==========] 5s
// Task2:             [==========] 5s
// Task3:                         [==========] 5s
// Total: 15 секунд
```

**executeOnExecutor():**
```java
public final AsyncTask<Params, Progress, Result> executeOnExecutor(
    Executor exec,
    Params... params
)
```

**Поведение:**
- Позволяет указать **собственный Executor**
- Может выполняться параллельно (зависит от executor)
- Нет гарантий порядка выполнения

**Пример:**
```java
// Параллельное выполнение
new Task1().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
new Task2().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
new Task3().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);

// Timeline:
// Task1: [==========]
// Task2: [==========]
// Task3: [==========]
// Total: 5 секунд (все параллельно)
```

**Доступные Executors:**

```java
// 1. SERIAL_EXECUTOR (по умолчанию в execute())
AsyncTask.SERIAL_EXECUTOR
// - Одна задача за раз
// - FIFO порядок

// 2. THREAD_POOL_EXECUTOR
AsyncTask.THREAD_POOL_EXECUTOR
// - До CPU_COUNT * 2 + 1 потоков
// - Параллельное выполнение
// - Очередь до 128 задач

// 3. Собственный Executor
Executor customExecutor = Executors.newFixedThreadPool(4);
task.executeOnExecutor(customExecutor, params);
```

**Когда использовать execute():**
- Database операции (serialized для consistency)
- Операции с shared state
- Когда важен порядок выполнения
- По умолчанию для простых случаев

**Когда использовать executeOnExecutor():**
- Независимые network requests
- Параллельная загрузка изображений
- Batch processing независимых данных
- Когда нужна максимальная производительность

**Важно:**
```java
// ОПАСНО: race condition
for (int i = 0; i < 10; i++) {
    new Task().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
}
// Все 10 задач выполняются параллельно
// Если они модифицируют shared state → race condition

// БЕЗОПАСНО: sequential execution
for (int i = 0; i < 10; i++) {
    new Task().execute();
}
// Задачи выполняются последовательно
```

### Вопрос 4: Как AsyncTask вызывает memory leaks?

**Механизм утечки:**

```java
public class MainActivity extends AppCompatActivity {
    private TextView resultTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        resultTextView = findViewById(R.id.resultTextView);

        // ПРОБЛЕМА: внутренний нестатический класс
        new LongRunningTask().execute();
    }

    // Нестатический внутренний класс
    private class LongRunningTask extends AsyncTask<Void, Void, String> {
        @Override
        protected String doInBackground(Void... params) {
            // Долгая работа - 30 секунд
            Thread.sleep(30000);
            return "Done";
        }

        @Override
        protected void onPostExecute(String result) {
            // Implicit reference к MainActivity
            resultTextView.setText(result);
        }
    }
}
```

**Пошаговое объяснение:**

**Шаг 1: Создание implicit reference**

Когда вы создаете нестатический внутренний класс, Java автоматически создает **скрытую ссылку** на внешний класс:

```java
// Что вы пишете:
private class LongRunningTask extends AsyncTask<...> { }

// Что создает Java (псевдокод):
private class LongRunningTask extends AsyncTask<...> {
    final MainActivity this$0; // Implicit reference!

    LongRunningTask(MainActivity outer) {
        this.this$0 = outer; // Автоматически
    }
}
```

**Шаг 2: Lifecycle mismatch**

```
Activity lifecycle:
onCreate() → onStart() → onResume() → [USER ROTATES] → onPause() → onStop() → onDestroy()
                                                                                    ↓
                                                                        Activity должна быть удалена GC

AsyncTask lifecycle:
execute() → doInBackground() [30 seconds...] → onPostExecute()
            ↑                                   ↑
            Хранит ссылку на Activity          Пытается обновить UI через 30 секунд
```

**Шаг 3: Garbage Collection не может удалить Activity**

```
GC Root (Thread pool)
    ↓
AsyncTask instance
    ↓ (this$0 implicit reference)
MainActivity instance (старая, уничтоженная)
    ↓
resultTextView
    ↓
Весь view hierarchy
    ↓
Все ресурсы Activity (Bitmap, Drawable, etc.)
```

**Последствия:**

1. **Memory leak:**
   - Старая Activity остается в памяти 30 секунд
   - При повороте экрана — новая Activity + старая в памяти
   - 5 поворотов = 5 Activity в памяти
   - OutOfMemoryError

2. **Multiple instances:**
   ```
   Heap dump после 3 поворотов экрана:
   - MainActivity@12345 (живая)
   - MainActivity@23456 (leaked, AsyncTask работает)
   - MainActivity@34567 (leaked, AsyncTask работает)
   - MainActivity@45678 (leaked, AsyncTask работает)
   ```

3. **Wasted resources:**
   - CPU тратится на фоновую работу для уничтоженной Activity
   - Память занята view hierarchy мертвых Activity
   - Battery drain

**Решения:**

**Решение 1: Статический класс + WeakReference**
```java
private static class LongRunningTask extends AsyncTask<Void, Void, String> {
    private WeakReference<MainActivity> activityRef;

    LongRunningTask(MainActivity activity) {
        // Weak reference — не предотвращает GC
        this.activityRef = new WeakReference<>(activity);
    }

    @Override
    protected String doInBackground(Void... params) {
        Thread.sleep(30000);
        return "Done";
    }

    @Override
    protected void onPostExecute(String result) {
        MainActivity activity = activityRef.get();

        // Activity может быть null если была удалена GC
        if (activity != null && !activity.isFinishing()) {
            activity.resultTextView.setText(result);
        }
    }
}
```

**Решение 2: Отмена в onDestroy**
```java
private LongRunningTask task;

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);

    resultTextView = findViewById(R.id.resultTextView);

    task = new LongRunningTask();
    task.execute();
}

@Override
protected void onDestroy() {
    super.onDestroy();

    // Отменить задачу — прервать поток
    if (task != null && task.getStatus() != AsyncTask.Status.FINISHED) {
        task.cancel(true);
    }
}
```

**Решение 3: Современный подход (Coroutines)**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val resultTextView = findViewById<TextView>(R.id.resultTextView)

        // lifecycleScope автоматически отменяется при onDestroy
        // Утечка памяти НЕВОЗМОЖНА
        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                delay(30000)
                "Done"
            }
            resultTextView.text = result
        }
    }
}
```

**Проверка утечек:**

**LeakCanary:**
```gradle
debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
```

После установки автоматически обнаруживает утечки и показывает notification с детальным анализом.

---

## Связи

### Развитие асинхронных API в Android

AsyncTask был первым, но не последним решением для асинхронности в Android. Понимание его проблем важно для оценки современных подходов:

- **[[android-async-evolution]]** — полная эволюция асинхронных API в Android от Thread + Handler до Coroutines
- **[[android-threading]]** — фундаментальные концепции многопоточности в Android
- **[[android-coroutines-mistakes]]** — современная альтернатива AsyncTask и типичные ошибки

### Базовые Android компоненты

AsyncTask строился поверх более низкоуровневых примитивов:

- **[[android-handler-looper]]** — механизм, который AsyncTask использовал под капотом для переключения на UI thread
- **[[android-executors]]** — ThreadPoolExecutor и другие executors, которые AsyncTask использовал для фоновых задач
- **[[android-handler-looper]]** — почему нельзя блокировать UI thread и как AsyncTask это решал (Main Thread = Handler + Looper)

### Архитектурные паттерны

Проблемы AsyncTask привели к развитию новых архитектурных паттернов:

- **[[android-viewmodel-internals]]** — как ViewModel решает проблему configuration changes (ViewModelStore переживает пересоздание Activity)
- **[[android-state-management]]** — lifecycle-aware observable (LiveData, StateFlow) для замены AsyncTask callbacks
- **[[android-activity-lifecycle]]** — компоненты, которые знают о lifecycle (в отличие от AsyncTask)
- **[[android-background-work]]** — для фоновых задач, которые должны пережить процесс (WorkManager)

### Memory management

Утечки памяти — ключевая проблема AsyncTask:

- **[[android-memory-leaks]]** — типы утечек памяти, WeakReference, LeakCanary и способы их обнаружения

### Testing

Сложности тестирования AsyncTask:

- **[[android-testing]]** — стратегии тестирования асинхронного кода, Espresso IdlingResources и мокирование

---

## Заключение

AsyncTask был важным шагом в развитии Android — он упростил многопоточность для разработчиков в эпоху, когда альтернатив практически не было. Однако его фундаментальные проблемы (memory leaks, lifecycle unawareness, exception swallowing) сделали его непригодным для современной разработки.

**Ключевые выводы:**

1. **Простота API не должна скрывать сложность** — AsyncTask казался простым, но скрывал множество edge cases
2. **Lifecycle awareness критически важна** — любой асинхронный API в Android должен быть lifecycle-aware
3. **Structured concurrency предотвращает утечки** — четкая иерархия задач и автоматическая отмена
4. **Explicit лучше implicit** — явная обработка ошибок, явное управление потоками

**Современные альтернативы:**
- **Kotlin Coroutines** — рекомендуется для новых проектов
- **Executors + LiveData** — для Java проектов
- **WorkManager** — для фоновых задач
- **RxJava** — для сложных reactive scenarios

AsyncTask deprecated, но уроки, которые мы извлекли из его проблем, формируют современные best practices Android разработки.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

# IT Market Report 2025 - Визуализация данных

Комплексный набор скриптов для визуализации данных из отчёта по рынку IT за 2025 год.

## Установка

### 1. Создайте виртуальное окружение (рекомендуется)

```bash
python3 -m venv venv
source venv/bin/activate  # На macOS/Linux
# или
venv\Scripts\activate     # На Windows
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

## Структура проекта

```
visualization/
├── requirements.txt                    # Зависимости Python
├── README.md                           # Эта инструкция
├── 01_job_market_graphs.py            # Графики рынка труда
├── 02_programming_languages_graphs.py # Графики языков программирования
├── 03_salary_analysis_graphs.py       # Графики зарплат
├── 04_layoffs_analysis_graphs.py      # Графики увольнений
├── 05_regional_comparison_graphs.py   # Региональные сравнения
├── 06_interactive_dashboard.py        # Интерактивный dashboard
└── output/                            # Папка для сохранённых графиков (создаётся автоматически)
```

## Использование

### Запуск отдельных скриптов

Каждый скрипт можно запустить независимо:

```bash
# Графики рынка труда
python 01_job_market_graphs.py

# Графики языков программирования
python 02_programming_languages_graphs.py

# Графики зарплат
python 03_salary_analysis_graphs.py

# Графики увольнений
python 04_layoffs_analysis_graphs.py

# Региональные сравнения
python 05_regional_comparison_graphs.py

# Интерактивный dashboard (откроется в браузере)
python 06_interactive_dashboard.py
```

### Запуск всех скриптов сразу

```bash
# На macOS/Linux
for script in 0*.py; do python "$script"; done

# На Windows PowerShell
Get-ChildItem -Filter "0*.py" | ForEach-Object { python $_.Name }
```

## Описание скриптов

### 01_job_market_graphs.py
Создаёт следующие графики:
- Помесячная динамика IT вакансий (2025)
- Indeed Job Postings Index тренд
- Распределение моделей работы (On-Site/Hybrid/Remote)
- Время найма по позициям
- Конкуренция за вакансии

### 02_programming_languages_graphs.py
Создаёт следующие графики:
- Топ-10 языков по индексам (TIOBE, PYPL, Stack Overflow)
- Year-over-Year изменения популярности
- Рост GitHub contributors по языкам
- Доменно-специфические лидеры
- Frontend/Backend фреймворки market share

### 03_salary_analysis_graphs.py
Создаёт следующие графики:
- Зарплаты по уровням опыта
- Зарплаты по языкам программирования
- Региональные сравнения зарплат
- Cloud certification ROI
- FAANG+ total compensation
- Cost-of-living adjusted покупательная способность
- Инфляция vs реальный рост зарплат

### 04_layoffs_analysis_graphs.py
Создаёт следующие графики:
- Помесячная хронология увольнений
- Топ-10 компаний по увольнениям
- Причины увольнений (breakdown)
- Сравнение 2023 vs 2024 vs 2025
- Наиболее затронутые роли

### 05_regional_comparison_graphs.py
Создаёт следующие графики:
- Глобальное распределение IT workforce
- Зарплаты по tech-хабам
- Темпы роста по регионам
- Employment outlook по странам
- Tech job postings decline (Europe)

### 06_interactive_dashboard.py
Запускает интерактивный dashboard в браузере с:
- Фильтрами по регионам, языкам, ролям
- Интерактивными графиками
- Hover tooltips с детальной информацией
- Экспортом данных

## Выходные файлы

Все графики сохраняются в папку `output/` в следующих форматах:
- PNG (высокое разрешение, 300 DPI)
- SVG (векторный формат для редактирования)
- HTML (для интерактивных графиков)

## Настройка

### Изменение цветовой схемы

В каждом скрипте есть секция `# Color scheme` в начале файла:

```python
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#43AA8B',
    'warning': '#F18F01',
    'danger': '#C73E1D'
}
```

### Изменение размера графиков

Измените параметры в функции `plt.figure()`:

```python
plt.figure(figsize=(14, 8))  # ширина, высота в дюймах
```

### Изменение DPI (качества)

```python
plt.savefig('output/graph.png', dpi=300, bbox_inches='tight')
```

## Требования к системе

- Python 3.9 или выше
- 2 GB RAM (минимум)
- 100 MB свободного места на диске

## Поддерживаемые ОС

- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian 11+)
- ✅ Windows 10/11

## Troubleshooting

### Проблема: "ModuleNotFoundError: No module named 'matplotlib'"
**Решение:** Установите зависимости: `pip install -r requirements.txt`

### Проблема: "Permission denied" при создании output папки
**Решение:** Создайте папку вручную: `mkdir output`

### Проблема: Шрифты не отображаются корректно (русские символы)
**Решение:** Установите шрифты DejaVu или настройте matplotlib:

```python
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'DejaVu Sans'
```

### Проблема: Interactive dashboard не открывается в браузере
**Решение:** Откройте вручную: http://127.0.0.1:8050/

## Лицензия

Данные и код предоставлены для анализа рынка IT. Все данные взяты из публичных источников и верифицированы.

## Контакты

При обнаружении проблем или вопросов создайте issue в репозитории.

---

**Последнее обновление:** 25 ноября 2025

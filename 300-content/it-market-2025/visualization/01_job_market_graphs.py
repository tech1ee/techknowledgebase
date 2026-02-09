#!/usr/bin/env python3
"""
IT Market Report 2025 - Job Market Visualization
Графики рынка труда: вакансии, конкуренция, модели работы
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

# Настройка стиля
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16

# Цветовая схема
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#43AA8B',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'info': '#118AB2'
}

# Создание папки для выходных файлов
output_dir = Path('output')
output_dir.mkdir(exist_ok=True)

print("🚀 Начинаю генерацию графиков рынка труда...")

# ============================================================================
# 1. ПОМЕСЯЧНАЯ ДИНАМИКА IT ВАКАНСИЙ (2025)
# ============================================================================

months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя']
new_jobs = [228000, 195000, 185000, 175000, 180000, 190000, 200000, 205000, 210000, 217238, 220000]
# ИСПРАВЛЕНО 26 ноября 2025: данные верифицированы через Layoffs.fyi, TechCrunch, CNBC
# Апрель: 24,500+ (Intel 21-25K), Май: 10,397 (Microsoft 6K), Июнь: 1,606 (самый низкий)
# Июль: 16,142 (Microsoft 9K доп.), Сентябрь: 2,205, Ноябрь: 4,545 (частичные данные)
layoffs = [2403, 16234, 8834, 24500, 10397, 1606, 16142, 6002, 2205, 33281, 4545]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
fig.suptitle('Динамика рынка IT вакансий - 2025', fontsize=18, fontweight='bold')

# График новых вакансий
ax1.plot(months, new_jobs, marker='o', linewidth=3, markersize=8,
         color=COLORS['success'], label='Новые вакансии')
ax1.fill_between(months, new_jobs, alpha=0.3, color=COLORS['success'])
ax1.set_ylabel('Количество вакансий', fontsize=12)
ax1.set_title('Новые IT вакансии по месяцам', fontsize=14, pad=10)
ax1.grid(True, alpha=0.3)
ax1.legend()

# Добавление аннотаций для пиков
max_idx = new_jobs.index(max(new_jobs))
ax1.annotate(f'Пик: {new_jobs[max_idx]:,}',
             xy=(months[max_idx], new_jobs[max_idx]),
             xytext=(20, 20), textcoords='offset points',
             bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# График увольнений
ax2.bar(months, layoffs, color=COLORS['danger'], alpha=0.7, label='Увольнения')
ax2.set_ylabel('Количество увольнений', fontsize=12)
ax2.set_xlabel('Месяц 2025', fontsize=12)
ax2.set_title('Увольнения в tech-индустрии по месяцам', fontsize=14, pad=10)
ax2.grid(True, alpha=0.3, axis='y')
ax2.legend()

# Аннотации для ключевых месяцев
apr_idx = months.index('Апр')
ax2.annotate('Intel: 21-25K\n(один из крупнейших)',
             xy=(months[apr_idx], layoffs[apr_idx]),
             xytext=(20, 30), textcoords='offset points',
             bbox=dict(boxstyle='round,pad=0.5', fc='orange', alpha=0.5),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.5'))

oct_idx = months.index('Окт')
ax2.annotate('Пик: 33,281\n(Amazon 14K + другие)',
             xy=(months[oct_idx], layoffs[oct_idx]),
             xytext=(20, 30), textcoords='offset points',
             bbox=dict(boxstyle='round,pad=0.5', fc='red', alpha=0.5),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.5'))

plt.tight_layout()
plt.savefig(output_dir / '01_monthly_job_dynamics.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '01_monthly_job_dynamics.svg', bbox_inches='tight')
print("✅ График 1: Помесячная динамика вакансий")

# ============================================================================
# 2. INDEED JOB POSTINGS INDEX TREND
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

index_dates = ['Янв 1', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт 31']
index_values = [111.7, 109.5, 107.3, 106.0, 105.2, 104.5, 103.8, 103.0, 102.3, 101.7]

ax.plot(index_dates, index_values, marker='o', linewidth=3, markersize=10,
        color=COLORS['primary'], label='Indeed Job Postings Index')
ax.fill_between(index_dates, index_values, 100, alpha=0.2, color=COLORS['primary'])
ax.axhline(y=100, color='red', linestyle='--', linewidth=2, label='Пре-пандемийный уровень (100)')

ax.set_ylabel('Index Value', fontsize=12)
ax.set_xlabel('2025', fontsize=12)
ax.set_title('Indeed Job Postings Index — Тренд 2025\n(Базовый уровень: пре-пандемия 2020 = 100)',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right')

# Аннотации
ax.annotate(f'Начало года: {index_values[0]}\n(+10.7% выше базы)',
            xy=(index_dates[0], index_values[0]),
            xytext=(30, 20), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='lightgreen', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

ax.annotate(f'Конец октября: {index_values[-1]}\n(+1.7% выше базы)\nСнижение: -10 пунктов',
            xy=(index_dates[-1], index_values[-1]),
            xytext=(30, -40), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='lightyellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

plt.tight_layout()
plt.savefig(output_dir / '02_indeed_job_index.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '02_indeed_job_index.svg', bbox_inches='tight')
print("✅ График 2: Indeed Job Postings Index")

# ============================================================================
# 3. МОДЕЛИ РАБОТЫ (ON-SITE / HYBRID / REMOTE)
# ============================================================================

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Распределение моделей работы — 2025', fontsize=16, fontweight='bold')

# IT сектор
it_sector = [56, 29, 15]
it_labels = ['On-Site\n56%', 'Hybrid\n29%', 'Remote\n15%']
colors_it = [COLORS['danger'], COLORS['warning'], COLORS['success']]
axes[0].pie(it_sector, labels=it_labels, autopct='%1.1f%%', startangle=90,
            colors=colors_it, explode=(0.05, 0.05, 0.05))
axes[0].set_title('IT сектор (США)', fontsize=12, pad=10)

# США общее
us_general = [61, 26, 13]
us_labels = ['On-Site\n61%', 'Hybrid\n26%', 'Remote\n13%']
axes[1].pie(us_general, labels=us_labels, autopct='%1.1f%%', startangle=90,
            colors=colors_it, explode=(0.05, 0.05, 0.05))
axes[1].set_title('США общее (все секторы)', fontsize=12, pad=10)

# Польша (IT)
poland_it = [7, 47.1, 45.9]
poland_labels = ['On-Site\n7%', 'Hybrid\n47.1%', 'Remote\n45.9%']
axes[2].pie(poland_it, labels=poland_labels, autopct='%1.1f%%', startangle=90,
            colors=colors_it, explode=(0.05, 0.05, 0.05))
axes[2].set_title('Польша IT (H1 2025)', fontsize=12, pad=10)

plt.tight_layout()
plt.savefig(output_dir / '03_work_arrangements.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '03_work_arrangements.svg', bbox_inches='tight')
print("✅ График 3: Модели работы")

# ============================================================================
# 4. ВРЕМЯ НАЙМА ПО ПОЗИЦИЯМ
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 8))

positions = ['Junior\nDeveloper', 'Mid-Level\nDeveloper', 'Senior\nEngineer',
             'Data\nScientist', 'DevOps\nEngineer', 'Cybersecurity\nAnalyst',
             'Engineering\nManager', 'C-Suite\n(CTO/CIO)']
time_to_hire = [65, 45, 50, 55, 60, 70, 80, 120]
colors_bars = [COLORS['warning'] if x > 60 else COLORS['success'] if x < 50 else COLORS['info'] for x in time_to_hire]

bars = ax.barh(positions, time_to_hire, color=colors_bars, alpha=0.7, edgecolor='black')

# Добавление значений на столбцы
for i, (bar, value) in enumerate(zip(bars, time_to_hire)):
    ax.text(value + 2, i, f'{value} дней', va='center', fontsize=10, fontweight='bold')

ax.axvline(x=44, color='red', linestyle='--', linewidth=2, label='Глобальный avg (44 дня)')
ax.set_xlabel('Дни', fontsize=12)
ax.set_title('Среднее время найма по позициям — 2025', fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.legend()

plt.tight_layout()
plt.savefig(output_dir / '04_time_to_hire.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '04_time_to_hire.svg', bbox_inches='tight')
print("✅ График 4: Время найма")

# ============================================================================
# 5. КОНКУРЕНЦИЯ ЗА ВАКАНСИИ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

categories = ['Вакансии трансформированы\nGenAI (высоко)',
              'Вакансии трансформированы\nGenAI (умеренно)',
              'Tech лидеры с трудностями\nпоиска талантов',
              'Навыковый gap\nсообщается',
              'Вакансии заполняются\nза 60 дней']
percentages = [26, 54, 87, 76, 75]
colors_comp = [COLORS['danger'], COLORS['warning'], COLORS['primary'],
               COLORS['secondary'], COLORS['success']]

bars = ax.bar(range(len(categories)), percentages, color=colors_comp, alpha=0.7, edgecolor='black')

# Добавление значений
for bar, value in zip(bars, percentages):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{value}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylabel('Процент (%)', fontsize=12)
ax.set_title('Ключевые метрики конкуренции и найма — 2025', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(range(len(categories)))
ax.set_xticklabels(categories, rotation=15, ha='right')
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_dir / '05_competition_metrics.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '05_competition_metrics.svg', bbox_inches='tight')
print("✅ График 5: Метрики конкуренции")

# ============================================================================
# 6. ГЛОБАЛЬНЫЕ IT ВАКАНСИИ ПО РЕГИОНАМ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

regions = ['США', 'Европа\n(EU)', 'Индия', 'Китай', 'Центральная\nАзия', 'Прочие']
annual_openings = [356700, 800000, 500000, 400000, 50000, 893300]  # примерные оценки
colors_regions = [COLORS['primary'], COLORS['secondary'], COLORS['success'],
                  COLORS['warning'], COLORS['info'], '#95a5a6']

bars = ax.bar(regions, annual_openings, color=colors_regions, alpha=0.7, edgecolor='black')

# Добавление значений
for bar, value in zip(bars, annual_openings):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 15000,
            f'{value:,}', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Годовые вакансии', fontsize=12)
ax.set_title('Глобальное распределение IT вакансий по регионам — 2025',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='y')

# Форматирование оси Y
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '06_global_job_distribution.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '06_global_job_distribution.svg', bbox_inches='tight')
print("✅ График 6: Глобальное распределение вакансий")

# ============================================================================
# 7. EMPLOYMENT OUTLOOK ПО РЕГИОНАМ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

outlook_regions = ['APAC\n(общее)', 'Индия', 'Сингапур', 'Австралия',
                   'Европа\n(EU)', 'США', 'Центральная\nАзия']
outlook_values = [30, 42.5, 25.5, 13, 15, 18, 25]  # Net Employment Outlook %
colors_outlook = [COLORS['success'] if x > 25 else COLORS['warning'] if x > 15 else COLORS['info']
                  for x in outlook_values]

bars = ax.barh(outlook_regions, outlook_values, color=colors_outlook, alpha=0.7, edgecolor='black')

# Добавление значений
for i, (bar, value) in enumerate(zip(bars, outlook_values)):
    ax.text(value + 1, i, f'+{value}%', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Net Employment Outlook (%)', fontsize=12)
ax.set_title('Net Employment Outlook по регионам — 2025', fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig(output_dir / '07_employment_outlook.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '07_employment_outlook.svg', bbox_inches='tight')
print("✅ График 7: Employment Outlook")

print("\n🎉 Все графики рынка труда успешно созданы!")
print(f"📁 Файлы сохранены в: {output_dir.absolute()}")
print("\nСозданные файлы:")
for file in sorted(output_dir.glob('0*.png')):
    print(f"  - {file.name}")

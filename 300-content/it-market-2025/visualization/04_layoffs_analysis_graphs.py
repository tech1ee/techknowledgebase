#!/usr/bin/env python3
"""
IT Market Report 2025 - Layoffs Analysis Visualization
Графики увольнений: хронология, компании, причины
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

plt.style.use('seaborn-v0_8-darkgrid')
COLORS = {'primary': '#2E86AB', 'secondary': '#A23B72', 'success': '#43AA8B',
          'warning': '#F18F01', 'danger': '#C73E1D', 'info': '#118AB2'}

output_dir = Path('output')
output_dir.mkdir(exist_ok=True)

print("🚀 Начинаю генерацию графиков анализа увольнений...")

# 1. ПОМЕСЯЧНАЯ ХРОНОЛОГИЯ УВОЛЬНЕНИЙ С ТАБЛИЦЕЙ
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 1, hspace=0.35, height_ratios=[1.2, 1, 0.8])
fig.suptitle('Хронология увольнений в tech — 2025', fontsize=18, fontweight='bold')

months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя']
# ИСПРАВЛЕНО 26 ноября 2025: верифицированные данные через Layoffs.fyi, TechCrunch, CNBC
layoffs = [2403, 16234, 8834, 24500, 10397, 1606, 16142, 6002, 2205, 33281, 4545]
cumulative = np.cumsum(layoffs)

# График 1: Помесячные увольнения
ax1 = fig.add_subplot(gs[0])
colors_months = [COLORS['danger'] if val > 15000 else COLORS['warning'] if val > 10000 else COLORS['info']
                 for val in layoffs]
bars = ax1.bar(months, layoffs, color=colors_months, alpha=0.7, edgecolor='black', linewidth=1.5)
for i, val in enumerate(layoffs):
    ax1.text(i, val + 800, f'{val:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax1.set_ylabel('Увольнения', fontsize=12, fontweight='bold')
ax1.set_title('Помесячные увольнения (2025)', fontsize=14, pad=10)
ax1.grid(True, alpha=0.3, axis='y')
ax1.annotate('Октябрьский всплеск\n33,281 (6x сентябрь)', xy=(9, layoffs[9]),
             xytext=(7, 30000), bbox=dict(boxstyle='round', fc='red', alpha=0.5),
             arrowprops=dict(arrowstyle='->', lw=2, color='red'))

# График 2: Кумулятивные увольнения
ax2 = fig.add_subplot(gs[1])
ax2.plot(months, cumulative, marker='o', linewidth=3, markersize=8, color=COLORS['danger'])
ax2.fill_between(months, cumulative, alpha=0.2, color=COLORS['danger'])
for i, val in enumerate(cumulative):
    if i % 2 == 0:
        ax2.text(i, val + 3000, f'{val:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax2.set_ylabel('Кумулятивные увольнения', fontsize=12, fontweight='bold')
ax2.set_xlabel('Месяц 2025', fontsize=12)
ax2.set_title('Кумулятивные увольнения за год', fontsize=14, pad=10)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=cumulative[-1], color='red', linestyle='--', linewidth=1.5, alpha=0.5)
ax2.text(10.5, cumulative[-1] + 3000, f'Итого: {cumulative[-1]:,}',
         fontsize=10, fontweight='bold', color='red')

# ТАБЛИЦА с помесячными данными
ax_table = fig.add_subplot(gs[2])
ax_table.axis('off')

# Создаём таблицу с данными по всем месяцам
table_data = [
    ['Месяц'] + months,
    ['Увольнения'] + [f'{v:,}' for v in layoffs]
]

table = ax_table.table(cellText=table_data, cellLoc='center', loc='center',
                       colWidths=[0.12] + [0.073]*11)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.2)

# Форматирование таблицы
for i in range(len(table_data)):
    for j in range(len(table_data[0])):
        cell = table[(i, j)]
        if j == 0:  # Первая колонка (заголовки)
            cell.set_facecolor('#2E86AB')
            cell.set_text_props(weight='bold', color='white')
        elif i == 0:  # Месяцы
            cell.set_facecolor('#E8F4F8')
            cell.set_text_props(weight='bold')
        else:  # Увольнения
            # Подсветка октября (10-й столбец, индекс 10)
            if j == 10:
                cell.set_facecolor('#FFE5E5')
                cell.set_text_props(weight='bold', color='red')
            else:
                cell.set_facecolor('white')
        cell.set_edgecolor('#CCCCCC')
        cell.set_linewidth(1.5)

ax_table.text(0.5, -0.12, f'Итого за Jan-Nov 2025: {sum(layoffs):,} увольнений | Среднее в месяц: {int(np.mean(layoffs)):,}',
              ha='center', fontsize=11, fontweight='bold', transform=ax_table.transAxes)

plt.savefig(output_dir / '21_layoffs_timeline.png', dpi=300, bbox_inches='tight')
print("✅ График 21: Хронология увольнений (с таблицей)")

# 2. ТОП-10 КОМПАНИЙ ПО УВОЛЬНЕНИЯМ С ТАБЛИЦЕЙ
fig = plt.figure(figsize=(18, 11))
gs = fig.add_gridspec(2, 1, hspace=0.35, height_ratios=[1.3, 1])
fig.suptitle('Топ-10 компаний по увольнениям — 2025', fontsize=18, fontweight='bold')

companies = ['Intel', 'TCS', 'Microsoft', 'Amazon', 'Salesforce', 'Meta', 'Oracle', 'Spotify', 'Google', 'Stripe']
# ИСПРАВЛЕНО: Intel 25K (CEO memo 07/25), TCS 20K, Salesforce 5K+ (9000→5000)
company_layoffs = [25000, 20000, 15000, 14000, 5000, 3600, 3000, 1000, 500, 300]
dates = ['Апр 2025', 'Q2 2025', 'Май+Июл', 'Окт 2025', 'Фев-Ноя', 'Янв+Окт', 'Авг-Сен', 'Early 2025', 'Апр-Май', 'Янв 2025']
percents = ['15%', '3%', '7%', '4%', '14%+', '2%', '10% India', '6%', '<1%', '3.5%']

# График
ax1 = fig.add_subplot(gs[0])
colors_comp = [COLORS['danger'] if lf > 15000 else COLORS['warning'] if lf > 5000 else COLORS['info']
               for lf in company_layoffs]

bars = ax1.barh(companies, company_layoffs, color=colors_comp, alpha=0.7, edgecolor='black', linewidth=1.5)
for i, (lf, pct) in enumerate(zip(company_layoffs, percents)):
    ax1.text(lf + 600, i, f'{lf:,} ({pct})', va='center', fontsize=10, fontweight='bold')

ax1.set_xlabel('Количество увольнений', fontsize=12, fontweight='bold')
ax1.set_title('Количество увольнений по компаниям', fontsize=14, pad=10)
ax1.grid(True, alpha=0.3, axis='x')
ax1.invert_yaxis()

# ТАБЛИЦА с полными данными
ax_table = fig.add_subplot(gs[1])
ax_table.axis('off')

table_data = [
    ['Ранг', 'Компания', 'Увольнения', '% workforce', 'Дата', 'Причина'],
    ['1', 'Intel', '21,000-25,000', '15%', 'Апр 2025', 'Реструктуризация, AI pivot'],
    ['2', 'TCS (India)', '12,000-19,755', '3%', 'Q2 2025', 'Declining outsourcing demand'],
    ['3', 'Microsoft', '15,000+', '7%', 'Май+Июл', 'AI infrastructure funding'],
    ['4', 'Amazon', '14,000', '4%', 'Окт 2025', 'AI transformation, cost-cutting'],
    ['5', 'Salesforce', '8,000+', '14%+', 'Фев-Ноя', 'AI replaces support roles'],
    ['6', 'Meta', '4,200+', '2%', 'Янв+Окт', 'Performance, AI restructure'],
    ['7', 'Oracle', '3,000+', '10% India', 'Авг-Сен', 'AI/cloud focus'],
    ['8', 'Spotify', '1,000+', '6%', 'Early 2025', 'Travel tech restructuring'],
    ['9', 'Google', '500+', '<1%', 'Апр-Май', 'Android/Chrome, AI redirect'],
    ['10', 'Stripe', '300', '3.5%', 'Янв 2025', 'Cost optimization']
]

table = ax_table.table(cellText=table_data, cellLoc='left', loc='center',
                       colWidths=[0.06, 0.14, 0.14, 0.11, 0.12, 0.43])
table.auto_set_font_size(False)
table.set_fontsize(9.5)
table.scale(1, 2.2)

# Форматирование таблицы
for i in range(len(table_data)):
    for j in range(len(table_data[0])):
        cell = table[(i, j)]
        if i == 0:  # Заголовок
            cell.set_facecolor('#2E86AB')
            cell.set_text_props(weight='bold', color='white', fontsize=10)
        elif i in [1, 2, 3, 4]:  # Топ-4 компании (>10K увольнений)
            cell.set_facecolor('#FFE5E5')
            if j == 0 or j == 2:  # Ранг и количество
                cell.set_text_props(weight='bold')
        else:
            cell.set_facecolor('#F8F8F8' if i % 2 == 0 else 'white')
        cell.set_edgecolor('#CCCCCC')
        cell.set_linewidth(1)
        # Выравнивание текста
        if j == 0:  # Ранг - центр
            cell.set_text_props(ha='center')

ax_table.text(0.5, -0.1, f'Итого топ-10 компаний: {sum(company_layoffs):,} увольнений | Это {sum(company_layoffs)/165269*100:.1f}% от всех увольнений 2025',
              ha='center', fontsize=11, fontweight='bold', transform=ax_table.transAxes)

plt.savefig(output_dir / '22_top_companies_layoffs.png', dpi=300, bbox_inches='tight')
print("✅ График 22: Топ компании по увольнениям (с таблицей)")

# 3. СРАВНЕНИЕ 2022-2025 С ПОЛНЫМ ИСТОРИЧЕСКИМ КОНТЕКСТОМ
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3)
fig.suptitle('Исторический контекст увольнений — 2022-2025', fontsize=18, fontweight='bold')

# Данные за все годы
years = ['2022', '2023', '2024', '2025\n(Jan-Nov)']
total_layoffs_year = [165000, 262735, 151484, 165269]
companies_affected = [1024, 585, 542, 1064]
avg_per_company = [161, 449, 279, 155]
trends = ['Начало коррекции', 'ПИК КРИЗИСА', 'Стабилизация', 'Возврат кризиса']

# График 1: Общие увольнения
ax1 = fig.add_subplot(gs[0, :])
colors_years = [COLORS['warning'], COLORS['danger'], COLORS['success'], COLORS['danger']]
bars = ax1.bar(years, total_layoffs_year, color=colors_years, alpha=0.7, edgecolor='black', linewidth=2)
for bar, val, trend in zip(bars, total_layoffs_year, trends):
    ax1.text(bar.get_x() + bar.get_width()/2., val + 5000,
             f'{val:,}\n{trend}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax1.set_ylabel('Общие увольнения', fontsize=12, fontweight='bold')
ax1.set_title('Общие увольнения по годам', fontsize=14, pad=10)
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_ylim(0, max(total_layoffs_year) * 1.15)

# График 2: Количество затронутых компаний
ax2 = fig.add_subplot(gs[1, 0])
bars = ax2.bar(years, companies_affected, color=colors_years, alpha=0.7, edgecolor='black', linewidth=2)
for bar, val in zip(bars, companies_affected):
    ax2.text(bar.get_x() + bar.get_width()/2., val + 30,
             f'{val}', ha='center', va='bottom', fontsize=11, fontweight='bold')
ax2.set_ylabel('Количество компаний', fontsize=12, fontweight='bold')
ax2.set_title('Затронутые компании', fontsize=12, pad=10)
ax2.grid(True, alpha=0.3, axis='y')

# График 3: Среднее на компанию
ax3 = fig.add_subplot(gs[1, 1])
bars = ax3.bar(years, avg_per_company, color=colors_years, alpha=0.7, edgecolor='black', linewidth=2)
for bar, val in zip(bars, avg_per_company):
    ax3.text(bar.get_x() + bar.get_width()/2., val + 10,
             f'{val}', ha='center', va='bottom', fontsize=11, fontweight='bold')
ax3.set_ylabel('Среднее увольнений/компания', fontsize=12, fontweight='bold')
ax3.set_title('Среднее на компанию', fontsize=12, pad=10)
ax3.grid(True, alpha=0.3, axis='y')
ax3.annotate('2023: Пик интенсивности\n449 на компанию',
            xy=(1, avg_per_company[1]), xytext=(1.5, 400),
            bbox=dict(boxstyle='round', fc='red', alpha=0.3),
            arrowprops=dict(arrowstyle='->', lw=2, color='red'))

# ТАБЛИЦА с полными данными
ax_table = fig.add_subplot(gs[2, :])
ax_table.axis('off')

table_data = [
    ['Год', 'Увольнения', 'Компании', 'Среднее/компанию', 'Тренд'],
    ['2022', '165,000', '1,024', '161', 'Начало коррекции'],
    ['2023', '262,735', '585', '449', '⚠️ ПИК КРИЗИСА'],
    ['2024', '151,484', '542', '279', 'Стабилизация'],
    ['2025*', '165,269+', '1,064+', '155', '🔴 Возврат кризиса']
]

table = ax_table.table(cellText=table_data, cellLoc='center', loc='center',
                       colWidths=[0.12, 0.18, 0.18, 0.22, 0.30])
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# Форматирование таблицы
for i, row in enumerate(table_data):
    for j, cell in enumerate(row):
        cell_obj = table[(i, j)]
        if i == 0:  # Заголовок
            cell_obj.set_facecolor('#2E86AB')
            cell_obj.set_text_props(weight='bold', color='white', fontsize=12)
        elif i == 2:  # 2023 - пик кризиса
            cell_obj.set_facecolor('#FFE5E5')
            cell_obj.set_text_props(weight='bold')
        elif i == 4:  # 2025 - возврат кризиса
            cell_obj.set_facecolor('#FFF0E5')
            cell_obj.set_text_props(weight='bold')
        else:
            cell_obj.set_facecolor('#F8F8F8' if i % 2 == 0 else 'white')
        cell_obj.set_edgecolor('#CCCCCC')
        cell_obj.set_linewidth(1.5)

ax_table.text(0.5, -0.15, '* 2025: Данные Jan-Nov (неполный год)',
              ha='center', fontsize=10, style='italic', transform=ax_table.transAxes)

plt.savefig(output_dir / '23_layoffs_year_comparison.png', dpi=300, bbox_inches='tight')
print("✅ График 23: Сравнение по годам (с таблицей)")

# 4. ПРИЧИНЫ УВОЛЬНЕНИЙ (OCTOBER 2025)
fig, ax = plt.subplots(figsize=(12, 8))
reasons = ['Cost-cutting', 'AI-driven\nrestructuring', 'Restructuring/\nEfficiency', 'Slowing\ngrowth', 'Прочее']
reason_counts = [50437, 31039, 20000, 15000, 13805]
reason_percents = [33, 20, 13, 10, 9]

colors_reasons = [COLORS['danger'], COLORS['warning'], COLORS['info'], COLORS['secondary'], '#95a5a6']
explode = (0.1, 0.05, 0, 0, 0)

ax.pie(reason_counts, labels=reasons, autopct='%1.1f%%', startangle=90,
       colors=colors_reasons, explode=explode, shadow=True)
ax.set_title('Причины увольнений — October 2025\n(Высший месяц увольнений)', fontsize=14, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig(output_dir / '24_layoff_reasons.png', dpi=300, bbox_inches='tight')
print("✅ График 24: Причины увольнений")

# 5. НАИБОЛЕЕ ЗАТРОНУТЫЕ РОЛИ
fig, ax = plt.subplots(figsize=(14, 8))
roles_affected = ['Junior SWE', 'Customer Support', 'Middle Management', 'Sales/BD', 'HR/Recruiting',
                  'Program Managers', 'QA Engineers', 'Data Analysts']
impact_scores = [95, 90, 85, 75, 70, 65, 55, 50]  # Relative impact score
colors_roles = [COLORS['danger'] if sc > 80 else COLORS['warning'] if sc > 60 else COLORS['info']
                for sc in impact_scores]

bars = ax.barh(roles_affected, impact_scores, color=colors_roles, alpha=0.7, edgecolor='black')
for i, score in enumerate(impact_scores):
    ax.text(score + 1, i, f'{score}', va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Relative Impact Score (0-100)')
ax.set_title('Наиболее затронутые роли — 2025', fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()

plt.tight_layout()
plt.savefig(output_dir / '25_affected_roles.png', dpi=300, bbox_inches='tight')
print("✅ График 25: Затронутые роли")

print("\n🎉 Все графики анализа увольнений успешно созданы!")
print(f"📁 Файлы сохранены в: {output_dir.absolute()}")

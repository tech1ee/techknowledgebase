#!/usr/bin/env python3
"""
IT Market Report 2025 - Salary Comparison 2023-2025
Сравнительные графики зарплат по годам, языкам, ролям и регионам
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

output_dir = Path('output')
output_dir.mkdir(exist_ok=True)

# Настройка стиля
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("🚀 Создание сравнительных графиков зарплат 2023-2025...")

# ============================================================================
# ГРАФИК 31: ЗАРПЛАТЫ ПО УРОВНЯМ ОПЫТА (США) 2023-2025
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

experience_levels = ['Junior\n(0-2 года)', 'Mid-level\n(2-5 лет)', 'Senior\n(5-10 лет)',
                     'Staff/Lead\n(10+ лет)', 'Principal\n(15+ лет)']
x = np.arange(len(experience_levels))
width = 0.25

# Данные (средние значения диапазонов)
salaries_2023 = [77500, 104000, 157500, 205000, 247500]
salaries_2024 = [80000, 110000, 162500, 212500, 260000]
salaries_2025 = [77968, 104840, 164482, 215295, 269546]

bars1 = ax.bar(x - width, salaries_2023, width, label='2023', color='#C73E1D', alpha=0.8)
bars2 = ax.bar(x, salaries_2024, width, label='2024', color='#F18F01', alpha=0.8)
bars3 = ax.bar(x + width, salaries_2025, width, label='2025', color='#43AA8B', alpha=0.8)

# Аннотации с процентами изменения
changes_24 = [+3.2, +5.8, +3.2, +3.7, +5.0]
changes_25 = [-2.5, -4.7, +1.2, +1.3, +3.7]

for i, (bar1, bar2, bar3) in enumerate(zip(bars1, bars2, bars3)):
    height1 = bar1.get_height()
    height2 = bar2.get_height()
    height3 = bar3.get_height()

    # 2023 значения
    ax.text(bar1.get_x() + bar1.get_width()/2., height1 + 5000,
            f'${height1/1000:.0f}K', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # 2024 значения с % изменением
    ax.text(bar2.get_x() + bar2.get_width()/2., height2 + 5000,
            f'${height2/1000:.0f}K\n({changes_24[i]:+.1f}%)',
            ha='center', va='bottom', fontsize=9, fontweight='bold', color='#F18F01')

    # 2025 значения с % изменением
    ax.text(bar3.get_x() + bar3.get_width()/2., height3 + 5000,
            f'${height3/1000:.0f}K\n({changes_25[i]:+.1f}%)',
            ha='center', va='bottom', fontsize=9, fontweight='bold',
            color='#43AA8B' if changes_25[i] > 0 else '#C73E1D')

ax.set_xlabel('Уровень опыта', fontsize=12, fontweight='bold')
ax.set_ylabel('Средняя зарплата (USD)', fontsize=12, fontweight='bold')
ax.set_title('Зарплаты Software Engineers в США по уровням опыта (2023-2025)',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(experience_levels)
ax.legend(loc='upper left', fontsize=11)
ax.yaxis.grid(True, alpha=0.3)
ax.set_ylim(0, 300000)

# Добавим горизонтальную линию медианы
median_2025 = 164482
ax.axhline(y=median_2025, color='#2E86AB', linestyle='--', linewidth=2, alpha=0.5)
ax.text(len(experience_levels)-0.5, median_2025 + 10000,
        f'Senior медиана 2025: ${median_2025/1000:.0f}K',
        fontsize=10, color='#2E86AB', fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / '31_salary_by_experience_usa.png', dpi=300, bbox_inches='tight')
print("✅ График 31: Зарплаты по уровням опыта (США)")
plt.close()

# ============================================================================
# ГРАФИК 32: ЗАРПЛАТЫ ПО ЯЗЫКАМ ПРОГРАММИРОВАНИЯ (Senior) 2023-2025
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 9))

languages = ['Rust', 'Go', 'Scala', 'TypeScript', 'Python', 'Kotlin', 'Java', 'C#']
x = np.arange(len(languages))
width = 0.25

# США (средние значения диапазонов)
usa_2023 = [140, 135, 133, 130, 125, 127, 115, 113]
usa_2024 = [145, 140, 137, 133, 128, 130, 117, 115]
usa_2025 = [140, 137.5, 140, 136, 125.7, 133, 131, 117]

bars1 = ax.bar(x - width, usa_2023, width, label='2023', color='#2E86AB', alpha=0.8)
bars2 = ax.bar(x, usa_2024, width, label='2024', color='#F18F01', alpha=0.8)
bars3 = ax.bar(x + width, usa_2025, width, label='2025', color='#43AA8B', alpha=0.8)

# Аннотации
for i, (bar1, bar2, bar3) in enumerate(zip(bars1, bars2, bars3)):
    height3 = bar3.get_height()
    ax.text(bar3.get_x() + bar3.get_width()/2., height3 + 2,
            f'${height3:.0f}K', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Язык программирования', fontsize=12, fontweight='bold')
ax.set_ylabel('Средняя зарплата Senior (USD, тыс.)', fontsize=12, fontweight='bold')
ax.set_title('Зарплаты по языкам программирования в США — Senior Level (2023-2025)',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(languages, rotation=45, ha='right')
ax.legend(loc='upper right', fontsize=11)
ax.yaxis.grid(True, alpha=0.3)
ax.set_ylim(0, 160)

# Добавим область AI/ML премии
ax.axhspan(140, 160, alpha=0.1, color='purple', label='AI/ML премия зона')
ax.text(0.5, 150, 'AI/ML\nпремия', fontsize=9, color='purple',
        fontweight='bold', ha='center', va='center', alpha=0.7)

plt.tight_layout()
plt.savefig(output_dir / '32_salary_by_language_usa.png', dpi=300, bbox_inches='tight')
print("✅ График 32: Зарплаты по языкам (США)")
plt.close()

# ============================================================================
# ГРАФИК 33: ЗАРПЛАТЫ ПО РОЛЯМ (Senior) 2023-2025
# ============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

roles = ['ML/AI', 'DevOps/SRE', 'Security', 'Backend', 'Full-Stack', 'Mobile', 'Frontend']
x = np.arange(len(roles))
width = 0.25

# США
usa_roles_2023 = [192.5, 150, 145, 140, 135, 130, 125]
usa_roles_2024 = [220, 165, 153.5, 147.5, 140, 135, 130]
usa_roles_2025 = [241.4, 170, 151.5, 158.9, 139.9, 116.4, 127.5]

bars1 = ax1.bar(x - width, usa_roles_2023, width, label='2023', color='#C73E1D', alpha=0.8)
bars2 = ax1.bar(x, usa_roles_2024, width, label='2024', color='#F18F01', alpha=0.8)
bars3 = ax1.bar(x + width, usa_roles_2025, width, label='2025', color='#43AA8B', alpha=0.8)

# Аннотации для 2025
for i, bar in enumerate(bars3):
    height = bar.get_height()
    change = ((usa_roles_2025[i] - usa_roles_2024[i]) / usa_roles_2024[i]) * 100
    ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
            f'${height:.0f}K\n({change:+.1f}%)',
            ha='center', va='bottom', fontsize=8, fontweight='bold',
            color='#43AA8B' if change > 0 else '#C73E1D')

ax1.set_xlabel('Роль', fontsize=11, fontweight='bold')
ax1.set_ylabel('Средняя зарплата (USD, тыс.)', fontsize=11, fontweight='bold')
ax1.set_title('США — Senior Roles (2023-2025)', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(roles, rotation=45, ha='right')
ax1.legend(loc='upper right', fontsize=9)
ax1.yaxis.grid(True, alpha=0.3)
ax1.set_ylim(0, 270)

# Европа (EUR в тысячах)
eu_roles_2023 = [105, 85, 82, 79, 76.5, 73.5, 70]
eu_roles_2024 = [115, 90, 86.5, 83.5, 80.5, 77, 73.5]
eu_roles_2025 = [122.5, 93.5, 89, 85.5, 82.5, 79, 75.5]

bars1 = ax2.bar(x - width, eu_roles_2023, width, label='2023', color='#C73E1D', alpha=0.8)
bars2 = ax2.bar(x, eu_roles_2024, width, label='2024', color='#F18F01', alpha=0.8)
bars3 = ax2.bar(x + width, eu_roles_2025, width, label='2025', color='#43AA8B', alpha=0.8)

# Аннотации для 2025
for i, bar in enumerate(bars3):
    height = bar.get_height()
    change = ((eu_roles_2025[i] - eu_roles_2024[i]) / eu_roles_2024[i]) * 100
    ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
            f'€{height:.0f}K\n({change:+.1f}%)',
            ha='center', va='bottom', fontsize=8, fontweight='bold',
            color='#43AA8B')

ax2.set_xlabel('Роль', fontsize=11, fontweight='bold')
ax2.set_ylabel('Средняя зарплата (EUR, тыс.)', fontsize=11, fontweight='bold')
ax2.set_title('Европа — Senior Roles (2023-2025)', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(roles, rotation=45, ha='right')
ax2.legend(loc='upper right', fontsize=9)
ax2.yaxis.grid(True, alpha=0.3)
ax2.set_ylim(0, 140)

plt.tight_layout()
plt.savefig(output_dir / '33_salary_by_role_comparison.png', dpi=300, bbox_inches='tight')
print("✅ График 33: Зарплаты по ролям (США vs Европа)")
plt.close()

# ============================================================================
# ГРАФИК 34: ЗАРПЛАТЫ ПО ГОРОДАМ США 2023-2025
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

cities = ['SF Bay\nArea', 'Seattle', 'NYC', 'Austin', 'Remote\nUS']
x = np.arange(len(cities))
width = 0.25

# Данные (средние значения)
cities_2023 = [249, 225, 185, 165, 157.5]
cities_2024 = [265, 242, 190, 175, 172.5]
cities_2025 = [257, 202, 155, 142.5, 155.4]

bars1 = ax.bar(x - width, cities_2023, width, label='2023', color='#2E86AB', alpha=0.8)
bars2 = ax.bar(x, cities_2024, width, label='2024', color='#F18F01', alpha=0.8)
bars3 = ax.bar(x + width, cities_2025, width, label='2025', color='#43AA8B', alpha=0.8)

# Процент изменения 2024-2025
changes = [-3.0, -16.5, -18.4, -18.6, -9.9]

for i, (bar1, bar2, bar3) in enumerate(zip(bars1, bars2, bars3)):
    height3 = bar3.get_height()
    ax.text(bar3.get_x() + bar3.get_width()/2., height3 + 5,
            f'${height3:.0f}K\n({changes[i]:.1f}%)',
            ha='center', va='bottom', fontsize=9, fontweight='bold',
            color='#C73E1D')

ax.set_xlabel('Город/Тип', fontsize=12, fontweight='bold')
ax.set_ylabel('Средняя зарплата Senior SWE (USD, тыс.)', fontsize=12, fontweight='bold')
ax.set_title('Зарплаты по городам США — Senior Software Engineer (2023-2025)\n⚠️ Коррекция 2025: RTO policies + oversupply',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(cities)
ax.legend(loc='upper right', fontsize=11)
ax.yaxis.grid(True, alpha=0.3)
ax.set_ylim(0, 300)

# Highlight снижения remote премии
ax.annotate('Remote премия\nснизилась\nс +10% до -10%',
            xy=(4, 155.4), xytext=(3.2, 220),
            arrowprops=dict(arrowstyle='->', color='#C73E1D', lw=2),
            fontsize=10, color='#C73E1D', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

plt.tight_layout()
plt.savefig(output_dir / '34_salary_by_city_usa.png', dpi=300, bbox_inches='tight')
print("✅ График 34: Зарплаты по городам США")
plt.close()

# ============================================================================
# ГРАФИК 35: ЗАРПЛАТЫ ПО СТРАНАМ ЕВРОПЫ 2023-2025
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

countries = ['Switzerland\n(Zurich)', 'UK\n(London)', 'Netherlands\n(Amsterdam)',
             'Germany\n(Berlin)', 'Poland\n(Warsaw)']
x = np.arange(len(countries))
width = 0.25

# Данные (средние значения в USD)
eu_2023 = [108, 115, 70, 62, 45]
eu_2024 = [114, 117, 75, 65, 50]
eu_2025 = [143, 100, 115, 74.8, 56.5]

bars1 = ax.bar(x - width, eu_2023, width, label='2023', color='#A23B72', alpha=0.8)
bars2 = ax.bar(x, eu_2024, width, label='2024', color='#F18F01', alpha=0.8)
bars3 = ax.bar(x + width, eu_2025, width, label='2025', color='#43AA8B', alpha=0.8)

# Процент изменения 2024-2025
changes_eu = [+25.4, -14.5, +53.3, +15.1, +13.0]

for i, (bar1, bar2, bar3) in enumerate(zip(bars1, bars2, bars3)):
    height3 = bar3.get_height()
    color = '#43AA8B' if changes_eu[i] > 0 else '#C73E1D'
    ax.text(bar3.get_x() + bar3.get_width()/2., height3 + 3,
            f'${height3:.0f}K\n({changes_eu[i]:+.1f}%)',
            ha='center', va='bottom', fontsize=9, fontweight='bold',
            color=color)

ax.set_xlabel('Страна (город)', fontsize=12, fontweight='bold')
ax.set_ylabel('Средняя зарплата Senior SWE (USD, тыс.)', fontsize=12, fontweight='bold')
ax.set_title('Зарплаты по странам Европы — Senior Software Engineer (2023-2025)\n⚠️ Высокая вариация данных 2025',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(countries)
ax.legend(loc='upper left', fontsize=11)
ax.yaxis.grid(True, alpha=0.3)
ax.set_ylim(0, 160)

# Amsterdam highlight
ax.annotate('Amsterdam:\nтримодальное\nраспределение\n(big tech boom)',
            xy=(2, 115), xytext=(1, 140),
            arrowprops=dict(arrowstyle='->', color='#43AA8B', lw=2),
            fontsize=9, color='#43AA8B', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.3))

plt.tight_layout()
plt.savefig(output_dir / '35_salary_by_country_europe.png', dpi=300, bbox_inches='tight')
print("✅ График 35: Зарплаты по странам Европы")
plt.close()

# ============================================================================
# ГРАФИК 36: CIS REMOTE ЗАРПЛАТЫ 2023-2025
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

years = [2023, 2024, 2025]

# Украина (средние значения по уровням)
ukraine_junior = [20, 21.5, 20]
ukraine_mid = [30, 32.5, 32.5]
ukraine_senior = [41.5, 46, 45]

# Беларусь
belarus_junior = [18, 20, 20]
belarus_mid = [28, 31, 33]
belarus_senior = [39, 44, 46]

# Россия (оценка)
russia_avg = [38.5, 34, 30]

ax.plot(years, ukraine_junior, marker='o', linewidth=2, markersize=8,
        label='Украина Junior', color='#2E86AB', linestyle='-')
ax.plot(years, ukraine_mid, marker='s', linewidth=2, markersize=8,
        label='Украина Mid', color='#2E86AB', linestyle='--')
ax.plot(years, ukraine_senior, marker='^', linewidth=2, markersize=8,
        label='Украина Senior', color='#2E86AB', linestyle=':')

ax.plot(years, belarus_junior, marker='o', linewidth=2, markersize=8,
        label='Беларусь Junior', color='#43AA8B', linestyle='-')
ax.plot(years, belarus_mid, marker='s', linewidth=2, markersize=8,
        label='Беларусь Mid', color='#43AA8B', linestyle='--')
ax.plot(years, belarus_senior, marker='^', linewidth=2, markersize=8,
        label='Беларусь Senior', color='#43AA8B', linestyle=':')

ax.plot(years, russia_avg, marker='D', linewidth=2, markersize=8,
        label='Россия Avg (оценка)', color='#C73E1D', linestyle='-.')

# Аннотации
for i, year in enumerate(years):
    ax.text(year, ukraine_senior[i] + 1, f'${ukraine_senior[i]:.0f}K',
            fontsize=8, ha='center', color='#2E86AB', fontweight='bold')
    ax.text(year, belarus_senior[i] + 1, f'${belarus_senior[i]:.0f}K',
            fontsize=8, ha='center', color='#43AA8B', fontweight='bold')
    if i == 2:  # 2025 год
        ax.text(year, russia_avg[i] - 2, f'${russia_avg[i]:.0f}K\n(санкции)',
                fontsize=8, ha='center', color='#C73E1D', fontweight='bold')

ax.set_xlabel('Год', fontsize=12, fontweight='bold')
ax.set_ylabel('Зарплата remote для Western компаний (USD, тыс.)', fontsize=12, fontweight='bold')
ax.set_title('Зарплаты CIS remote разработчиков (2023-2025)\nРабота на Western компании',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(years)
ax.legend(loc='upper left', fontsize=9, ncol=2)
ax.grid(True, alpha=0.3)
ax.set_ylim(15, 55)

# Добавим зону стагнации
ax.axhspan(32, 46, alpha=0.1, color='orange')
ax.text(2024, 40, 'Зона стагнации\n2024-2025', fontsize=9, color='orange',
        fontweight='bold', ha='center', va='center', alpha=0.7,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.2))

plt.tight_layout()
plt.savefig(output_dir / '36_salary_cis_remote.png', dpi=300, bbox_inches='tight')
print("✅ График 36: CIS remote зарплаты")
plt.close()

# ============================================================================
# ГРАФИК 37: YoY ИЗМЕНЕНИЯ HEATMAP
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

# Категории и годовые изменения (2024-2025)
categories = [
    'Junior USA', 'Mid USA', 'Senior USA', 'Staff USA', 'Principal USA',
    'Junior EU', 'Mid EU', 'Senior EU', 'Staff EU',
    'Rust USA', 'Go USA', 'Python USA', 'TypeScript USA', 'Java USA',
    'ML/AI USA', 'DevOps USA', 'Backend USA', 'Frontend USA', 'Mobile USA',
    'SF Bay', 'Seattle', 'NYC', 'Austin', 'Remote US',
    'Ukraine Mid', 'Belarus Mid', 'Russia'
]

yoy_changes = [
    -2.5, -4.7, 1.2, 1.3, 3.7,  # USA by exp
    -3.3, -5.0, -2.8, -3.9,  # EU by exp
    -3.4, -2.9, -1.8, 2.2, 6.5,  # Languages
    9.7, 3.0, 7.9, -1.7, -13.8,  # Roles
    -3.0, -16.5, -18.4, -18.6, -9.9,  # US cities
    0, 6.5, -21.1  # CIS
]

# Создаем цветовую карту
colors = ['#C73E1D' if x < -5 else '#F18F01' if x < 0 else '#FFD700' if x < 3 else '#43AA8B'
          for x in yoy_changes]

bars = ax.barh(categories, yoy_changes, color=colors, alpha=0.8)

# Аннотации
for i, (bar, change) in enumerate(zip(bars, yoy_changes)):
    width = bar.get_width()
    label_x_pos = width + 0.5 if width > 0 else width - 0.5
    ax.text(label_x_pos, bar.get_y() + bar.get_height()/2,
            f'{change:+.1f}%', ha='left' if width > 0 else 'right',
            va='center', fontsize=8, fontweight='bold')

ax.set_xlabel('YoY изменение 2024→2025 (%)', fontsize=12, fontweight='bold')
ax.set_title('Year-over-Year изменения зарплат 2024→2025 по всем категориям\n🔴 Сильное падение | 🟠 Падение | 🟡 Стагнация | 🟢 Рост',
             fontsize=14, fontweight='bold', pad=20)
ax.axvline(x=0, color='black', linewidth=2, linestyle='-')
ax.grid(axis='x', alpha=0.3)
ax.set_xlim(-25, 15)

# Легенда
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#C73E1D', alpha=0.8, label='< -5% (Сильное падение)'),
    Patch(facecolor='#F18F01', alpha=0.8, label='-5% to 0% (Падение)'),
    Patch(facecolor='#FFD700', alpha=0.8, label='0% to +3% (Стагнация)'),
    Patch(facecolor='#43AA8B', alpha=0.8, label='> +3% (Рост)')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

plt.tight_layout()
plt.savefig(output_dir / '37_yoy_changes_heatmap.png', dpi=300, bbox_inches='tight')
print("✅ График 37: YoY изменения (heatmap)")
plt.close()

# ============================================================================
# ГРАФИК 38: AI/ML ПРЕМИЯ VS ОСТАЛЬНЫЕ РОЛИ (ТРЕНД)
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

years = [2023, 2024, 2025]

# Данные по ролям
ml_ai = [192.5, 220, 241.4]
devops = [150, 165, 170]
backend = [140, 147.5, 158.9]
frontend = [125, 130, 127.5]
mobile = [130, 135, 116.4]

# Средняя по всем ролям (кроме ML/AI)
avg_other = [136.3, 144.4, 143.2]

ax.plot(years, ml_ai, marker='o', linewidth=3, markersize=10,
        label='ML/AI Engineer', color='#A23B72', linestyle='-')
ax.plot(years, devops, marker='s', linewidth=2, markersize=8,
        label='DevOps/SRE', color='#2E86AB', linestyle='--')
ax.plot(years, backend, marker='^', linewidth=2, markersize=8,
        label='Backend Engineer', color='#43AA8B', linestyle=':')
ax.plot(years, frontend, marker='D', linewidth=2, markersize=8,
        label='Frontend Engineer', color='#F18F01', linestyle='-.')
ax.plot(years, mobile, marker='v', linewidth=2, markersize=8,
        label='Mobile Developer', color='#C73E1D', linestyle='-.')
ax.plot(years, avg_other, marker='x', linewidth=2, markersize=10,
        label='Среднее (кроме ML/AI)', color='gray', linestyle='--', alpha=0.7)

# Расчет премии ML/AI
premiums = [(ml_ai[i] / avg_other[i] - 1) * 100 for i in range(len(years))]

# Аннотации премии
for i, year in enumerate(years):
    ax.text(year, ml_ai[i] + 5, f'${ml_ai[i]:.0f}K\n(+{premiums[i]:.0f}%)',
            fontsize=9, ha='center', color='#A23B72', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='pink', alpha=0.3))

ax.set_xlabel('Год', fontsize=12, fontweight='bold')
ax.set_ylabel('Средняя зарплата Senior (USD, тыс.)', fontsize=12, fontweight='bold')
ax.set_title('AI/ML Engineer Premium vs Остальные роли (2023-2025)\nМашинное обучение = золотая жила IT индустрии',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(years)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_ylim(100, 260)

# Выделим зону AI boom
ax.axvspan(2023.5, 2025.5, alpha=0.1, color='purple')
ax.text(2024.5, 220, 'AI Boom\n2024-2025', fontsize=11, color='purple',
        fontweight='bold', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lavender', alpha=0.5))

plt.tight_layout()
plt.savefig(output_dir / '38_ai_ml_premium_trend.png', dpi=300, bbox_inches='tight')
print("✅ График 38: AI/ML премия тренд")
plt.close()

print("\n🎉 Все 8 сравнительных графиков успешно созданы!")
print(f"📁 Файлы сохранены в: {output_dir.absolute()}")
print("\nГрафики:")
print("  31_salary_by_experience_usa.png - Зарплаты по уровням опыта (США)")
print("  32_salary_by_language_usa.png - Зарплаты по языкам (США)")
print("  33_salary_by_role_comparison.png - Зарплаты по ролям (США vs EU)")
print("  34_salary_by_city_usa.png - Зарплаты по городам США")
print("  35_salary_by_country_europe.png - Зарплаты по странам Европы")
print("  36_salary_cis_remote.png - CIS remote зарплаты")
print("  37_yoy_changes_heatmap.png - YoY изменения heatmap")
print("  38_ai_ml_premium_trend.png - AI/ML премия тренд")

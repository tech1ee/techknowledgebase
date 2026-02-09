#!/usr/bin/env python3
"""
IT Market Report 2025 - Salary Analysis Visualization
Графики зарплат: по опыту, регионам, ролям, сертификациям
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.size'] = 11

COLORS = {'primary': '#2E86AB', 'secondary': '#A23B72', 'success': '#43AA8B',
          'warning': '#F18F01', 'danger': '#C73E1D', 'info': '#118AB2'}

output_dir = Path('output')
output_dir.mkdir(exist_ok=True)

print("🚀 Начинаю генерацию графиков зарплатного анализа...")

# ============================================================================
# 1. ЗАРПЛАТЫ ПО УРОВНЯМ ОПЫТА
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

experience_levels = ['Junior\n(0-3 года)', 'Mid-Level\n(4-9 лет)', 'Senior\n(10-15 лет)',
                     'Architect/Lead', 'Director/VP']
base_salaries = [62500, 119000, 142500, 180000, 250000]
total_comp = [70000, 145000, 185000, 250000, 400000]
yoy_changes = [-1.4, 5.8, 3.1, 2.5, 1.8]

x = np.arange(len(experience_levels))
width = 0.35

bars1 = ax.bar(x - width/2, base_salaries, width, label='Base Salary',
               color=COLORS['primary'], alpha=0.7, edgecolor='black')
bars2 = ax.bar(x + width/2, total_comp, width, label='Total Compensation',
               color=COLORS['success'], alpha=0.7, edgecolor='black')

# Добавление значений и YoY
for i, (base, total, yoy) in enumerate(zip(base_salaries, total_comp, yoy_changes)):
    ax.text(i - width/2, base + 5000, f'${base/1000:.0f}K',
            ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(i + width/2, total + 5000, f'${total/1000:.0f}K',
            ha='center', va='bottom', fontsize=9, fontweight='bold')
    color_yoy = 'green' if yoy > 0 else 'red'
    ax.text(i, total + 30000, f'{yoy:+.1f}% YoY',
            ha='center', va='bottom', fontsize=9, color=color_yoy, fontweight='bold')

ax.set_ylabel('Salary (USD)', fontsize=12)
ax.set_xlabel('Experience Level', fontsize=12)
ax.set_title('Зарплаты по уровням опыта — USA 2025', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(experience_levels)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3, axis='y')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '15_salary_by_experience.png', dpi=300, bbox_inches='tight')
print("✅ График 15: Зарплаты по опыту")

# ============================================================================
# 2. РЕГИОНАЛЬНЫЕ ЗАРПЛАТЫ — ТОП TECH-ХАБЫ
# ============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Региональные зарплаты tech-хабов — 2025', fontsize=16, fontweight='bold')

# USA Tech Hubs (Senior SWE, актуализировано 2025)
us_cities = ['SF Bay\nArea', 'NYC', 'Seattle', 'Austin', 'US\nAverage']
us_salaries = [168000, 160000, 155000, 153000, 135000]
us_col_index = [190, 175, 145, 120, 100]  # Cost of Living Index

colors_us = [COLORS['danger'] if col > 170 else COLORS['warning'] if col > 140
             else COLORS['success'] for col in us_col_index]

bars = ax1.bar(us_cities, us_salaries, color=colors_us, alpha=0.7, edgecolor='black')
for bar, salary, col in zip(bars, us_salaries, us_col_index):
    ax1.text(bar.get_x() + bar.get_width()/2., salary + 2000,
             f'${salary:,}\nCoL: {col}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax1.set_ylabel('Average Salary (USD)')
ax1.set_title('USA Tech Hubs', fontsize=12, pad=10)
ax1.grid(True, alpha=0.3, axis='y')
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

# Europe Tech Hubs (Senior SWE gross, актуализировано 2025)
eu_cities = ['Zurich', 'London', 'Amsterdam', 'Munich', 'Berlin']
eu_salaries = [145000, 96000, 76000, 71000, 70000]
colors_eu = [COLORS['success'] if sal > 100000 else COLORS['warning'] if sal > 70000
             else COLORS['info'] for sal in eu_salaries]

bars = ax2.bar(eu_cities, eu_salaries, color=colors_eu, alpha=0.7, edgecolor='black')
for bar, salary in zip(bars, eu_salaries):
    ax2.text(bar.get_x() + bar.get_width()/2., salary + 2000,
             f'${salary:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax2.set_ylabel('Average Salary (USD)')
ax2.set_title('Europe Tech Hubs', fontsize=12, pad=10)
ax2.grid(True, alpha=0.3, axis='y')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '16_regional_salaries_tech_hubs.png', dpi=300, bbox_inches='tight')
print("✅ График 16: Региональные зарплаты")

# ============================================================================
# 3. ЗАРПЛАТЫ ПО РОЛЯМ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

roles = ['AI/ML Engineer', 'Cloud Architect', 'DevOps Engineer (Senior)',
         'Data Scientist', 'Cybersecurity (Senior)', 'Full-Stack Developer',
         'Frontend Developer', 'Backend Developer', 'SRE', 'Engineering Manager']
role_salaries = [190000, 165000, 155000, 145000, 155000, 137500, 132500, 144000, 155000, 185000]
premiums = [58, 38, 29, 21, 29, 15, 10, 20, 29, 54]  # % премия vs Java baseline

colors_roles = [COLORS['success'] if prem > 40 else COLORS['warning'] if prem > 20
                else COLORS['info'] for prem in premiums]

bars = ax.barh(roles, role_salaries, color=colors_roles, alpha=0.7, edgecolor='black')

for i, (salary, premium) in enumerate(zip(role_salaries, premiums)):
    ax.text(salary + 3000, i, f'${salary:,}\n(+{premium}% premium)',
            va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Average Total Compensation (USD)', fontsize=12)
ax.set_title('Зарплаты по ролям — USA 2025\n(Premium vs Java baseline $120K)',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '17_salary_by_role.png', dpi=300, bbox_inches='tight')
print("✅ График 17: Зарплаты по ролям")

# ============================================================================
# 4. CLOUD CERTIFICATION ROI
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

certifications = ['AWS Solutions\nArchitect Pro', 'AWS DevOps\nEngineer Pro',
                  'AWS Security\nSpecialty', 'Azure Solutions\nArchitect',
                  'Google Cloud\nArchitect', 'AWS Cloud\nPractitioner']
cert_salaries = [167500, 142000, 167500, 160000, 160000, 85866]
salary_premiums = [39.6, 18.3, 39.6, 33.3, 33.3, -28.4]  # vs $120K baseline

colors_cert = [COLORS['success'] if prem > 30 else COLORS['warning'] if prem > 15
               else COLORS['info'] if prem > 0 else COLORS['danger'] for prem in salary_premiums]

bars = ax.bar(certifications, cert_salaries, color=colors_cert, alpha=0.7, edgecolor='black')

for bar, salary, premium in zip(bars, cert_salaries, salary_premiums):
    ax.text(bar.get_x() + bar.get_width()/2., salary + 3000,
            f'${salary:,}\n({premium:+.1f}%)', ha='center', va='bottom',
            fontsize=9, fontweight='bold')

ax.set_ylabel('Average Salary (USD)', fontsize=12)
ax.set_title('Cloud Certifications — Salary Impact 2025\n(73% получили raise, средний raise 27%)',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='y')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '18_cloud_certification_roi.png', dpi=300, bbox_inches='tight')
print("✅ График 18: Cloud certification ROI")

# ============================================================================
# 5. FAANG+ TOTAL COMPENSATION
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

companies = ['OpenAI', 'Meta', 'LinkedIn', 'NVIDIA', 'Google', 'Amazon', 'Microsoft']
median_tc = [875000, 453000, 355000, 290000, 265000, 265000, 240000]

colors_faang = [COLORS['success'] if tc > 400000 else COLORS['warning'] if tc > 280000
                else COLORS['info'] for tc in median_tc]

bars = ax.barh(companies, median_tc, color=colors_faang, alpha=0.7, edgecolor='black')

for i, tc in enumerate(median_tc):
    ax.text(tc + 15000, i, f'${tc:,}', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Median Total Compensation (All Levels, USD)', fontsize=12)
ax.set_title('FAANG+ Median Total Compensation — 2025',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '19_faang_total_compensation.png', dpi=300, bbox_inches='tight')
print("✅ График 19: FAANG+ compensation")

# ============================================================================
# 6. ИНФЛЯЦИЯ VS РЕАЛЬНЫЙ РОСТ ЗАРПЛАТ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

quarters = ['Q1\n2024', 'Q2\n2024', 'Q3\n2024', 'Q4\n2024', 'Q1\n2025', 'Q2\n2025', 'Q3\n2025']
wage_growth = [3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.2]
inflation = [3.2, 3.0, 2.9, 2.8, 2.6, 2.4, 2.7]
real_growth = [0.6, 0.9, 1.1, 1.3, 1.6, 1.9, 1.5]

ax.plot(quarters, wage_growth, marker='o', linewidth=3, markersize=8,
        color=COLORS['success'], label='Nominal Wage Growth')
ax.plot(quarters, inflation, marker='s', linewidth=3, markersize=8,
        color=COLORS['danger'], label='Inflation')
ax.plot(quarters, real_growth, marker='^', linewidth=3, markersize=8,
        color=COLORS['primary'], label='Real Wage Growth', linestyle='--')

ax.fill_between(quarters, wage_growth, inflation, where=np.array(wage_growth) > np.array(inflation),
                alpha=0.2, color=COLORS['success'], label='Positive Real Growth Area')

ax.set_ylabel('Percent (%)', fontsize=12)
ax.set_xlabel('Quarter', fontsize=12)
ax.set_title('Инфляция vs Реальный рост зарплат — 2024-2025\n(Real growth = Wage growth - Inflation)',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper left')
ax.axhline(y=0, color='black', linestyle='-', linewidth=1)

plt.tight_layout()
plt.savefig(output_dir / '20_inflation_vs_wage_growth.png', dpi=300, bbox_inches='tight')
print("✅ График 20: Инфляция vs зарплаты")

print("\n🎉 Все графики зарплатного анализа успешно созданы!")
print(f"📁 Файлы сохранены в: {output_dir.absolute()}")

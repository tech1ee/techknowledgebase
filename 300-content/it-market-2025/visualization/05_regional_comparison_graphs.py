#!/usr/bin/env python3
"""
IT Market Report 2025 - Regional Comparison Visualization
Графики региональных сравнений: workforce, зарплаты, рост
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

print("🚀 Начинаю генерацию графиков региональных сравнений...")

# 1. ГЛОБАЛЬНОЕ РАСПРЕДЕЛЕНИЕ IT WORKFORCE
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Глобальное распределение IT Workforce — 2025', fontsize=16, fontweight='bold')

regions = ['США', 'Европа\n(EU)', 'Индия', 'Китай', 'Центральная\nАзия', 'Прочие\nAPAC']
workforce = [6100000, 2000000, 3500000, 4000000, 189500, 1500000]
colors_wf = [COLORS['primary'], COLORS['secondary'], COLORS['success'],
             COLORS['warning'], COLORS['info'], '#95a5a6']

ax1.pie(workforce, labels=regions, autopct='%1.1f%%', startangle=90,
        colors=colors_wf, explode=(0.05, 0, 0, 0, 0, 0))
ax1.set_title('IT Workforce Distribution', fontsize=12, pad=10)

growth_rates = [13, 5, 12.4, 8, 9.36, 10]
bars = ax2.barh(regions, growth_rates, color=colors_wf, alpha=0.7, edgecolor='black')
for i, rate in enumerate(growth_rates):
    ax2.text(rate + 0.3, i, f'{rate}%', va='center', fontsize=10, fontweight='bold')
ax2.set_xlabel('Annual Growth Rate (%)')
ax2.set_title('Projected Growth Rates', fontsize=12, pad=10)
ax2.grid(True, alpha=0.3, axis='x')
ax2.invert_yaxis()

plt.tight_layout()
plt.savefig(output_dir / '26_global_workforce_distribution.png', dpi=300, bbox_inches='tight')
print("✅ График 26: Глобальное распределение workforce")

# 2. ЗАРПЛАТЫ ПО РЕГИОНАМ (SENIOR SWE)
fig, ax = plt.subplots(figsize=(16, 10))

cities = ['SF Bay Area', 'NYC', 'Seattle', 'Austin', 'Zurich', 'London', 'Amsterdam', 'Berlin',
          'Singapore', 'Sydney', 'Bangalore', 'Almaty', 'Tashkent']
# Актуализировано 2025 (Senior SWE)
salaries_usd = [168000, 160000, 155000, 153000, 145000, 96000, 76000, 70000,
                136000, 90000, 24000, 62000, 23700]
regions_cat = ['USA', 'USA', 'USA', 'USA', 'Europe', 'Europe', 'Europe', 'Europe',
               'APAC', 'APAC', 'APAC', 'Central Asia', 'Central Asia']

color_map = {'USA': COLORS['primary'], 'Europe': COLORS['secondary'],
             'APAC': COLORS['success'], 'Central Asia': COLORS['info']}
colors_cities = [color_map[cat] for cat in regions_cat]

bars = ax.barh(cities, salaries_usd, color=colors_cities, alpha=0.7, edgecolor='black')
for i, salary in enumerate(salaries_usd):
    ax.text(salary + 3000, i, f'${salary:,}', va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Average Senior SWE Salary (USD)', fontsize=12)
ax.set_title('Senior Software Engineer зарплаты по городам — 2025',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

# Легенда
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=COLORS['primary'], label='USA'),
                   Patch(facecolor=COLORS['secondary'], label='Europe'),
                   Patch(facecolor=COLORS['success'], label='APAC'),
                   Patch(facecolor=COLORS['info'], label='Central Asia')]
ax.legend(handles=legend_elements, loc='lower right')

plt.tight_layout()
plt.savefig(output_dir / '27_regional_salaries_comparison.png', dpi=300, bbox_inches='tight')
print("✅ График 27: Региональное сравнение зарплат")

# 3. COST-OF-LIVING ADJUSTED PURCHASING POWER
fig, ax = plt.subplots(figsize=(14, 10))

cities_col = ['Austin', 'Seattle', 'Berlin', 'Bangalore', 'Singapore', 'NYC', 'SF Bay Area', 'London', 'Zurich']
nominal_sal = [143629, 136523, 65524, 15000, 70000, 145149, 148924, 73993, 145000]
real_purchasing = [120000, 94000, 69000, 50000, 38000, 83000, 78000, 48000, 69000]

x = np.arange(len(cities_col))
width = 0.35

bars1 = ax.bar(x - width/2, nominal_sal, width, label='Nominal Salary',
               color=COLORS['warning'], alpha=0.7, edgecolor='black')
bars2 = ax.bar(x + width/2, real_purchasing, width, label='Real Purchasing Power',
               color=COLORS['success'], alpha=0.7, edgecolor='black')

for i, (nom, real) in enumerate(zip(nominal_sal, real_purchasing)):
    ax.text(i - width/2, nom + 3000, f'${nom/1000:.0f}K',
            ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(i + width/2, real + 3000, f'${real/1000:.0f}K',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('Salary (USD)', fontsize=12)
ax.set_xlabel('City', fontsize=12)
ax.set_title('Nominal vs Real Purchasing Power (CoL-Adjusted) — 2025',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(cities_col, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '28_col_adjusted_purchasing_power.png', dpi=300, bbox_inches='tight')
print("✅ График 28: CoL-adjusted покупательная способность")

# 4. EUROPE TECH JOB POSTINGS DECLINE
fig, ax = plt.subplots(figsize=(14, 8))

eu_countries = ['UK', 'France', 'Germany', 'Netherlands', 'Poland']
decline_from_peak = [-41, -39, -30, -12, -10]
colors_decline = [COLORS['danger'] if d < -30 else COLORS['warning'] if d < -20 else COLORS['info']
                  for d in decline_from_peak]

bars = ax.barh(eu_countries, decline_from_peak, color=colors_decline, alpha=0.7, edgecolor='black')
for i, decline in enumerate(decline_from_peak):
    ax.text(decline - 2, i, f'{decline}%', va='center', ha='right',
            fontsize=11, fontweight='bold', color='white')

ax.axvline(x=0, color='black', linestyle='-', linewidth=2)
ax.set_xlabel('Decline from Peak (%)', fontsize=12)
ax.set_title('Europe Tech Job Postings — Decline from Peak (Feb 2020 - Oct 2025)',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()

plt.tight_layout()
plt.savefig(output_dir / '29_europe_job_postings_decline.png', dpi=300, bbox_inches='tight')
print("✅ График 29: Europe job postings decline")

# 5. CENTRAL ASIA FASTEST GROWING ROLES
fig, ax = plt.subplots(figsize=(14, 8))

ca_roles = ['Big Data\nSpecialists', 'Fintech\nEngineers', 'AI/ML\nExperts',
            'Software\nDevelopers', 'Data\nAnalysts']
ca_growth = [100, 92, 83, 57, 41]

colors_ca = [COLORS['success'] if g > 80 else COLORS['warning'] if g > 50 else COLORS['info']
             for g in ca_growth]

bars = ax.bar(ca_roles, ca_growth, color=colors_ca, alpha=0.7, edgecolor='black')
for bar, growth in zip(bars, ca_growth):
    ax.text(bar.get_x() + bar.get_width()/2., growth + 2,
            f'+{growth}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Projected Demand Growth (%)', fontsize=12)
ax.set_title('Центральная Азия — Fastest-Growing Roles (Projected Demand)',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_dir / '30_central_asia_growing_roles.png', dpi=300, bbox_inches='tight')
print("✅ График 30: Central Asia растущие роли")

print("\n🎉 Все графики региональных сравнений успешно созданы!")
print(f"📁 Файлы сохранены в: {output_dir.absolute()}")

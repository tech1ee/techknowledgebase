#!/usr/bin/env python3
"""
IT Market Report 2025 - Programming Languages Visualization
Графики языков программирования: популярность, рост, зарплаты
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

# Цветовая схема
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#43AA8B',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'info': '#118AB2'
}

output_dir = Path('output')
output_dir.mkdir(exist_ok=True)

print("🚀 Начинаю генерацию графиков языков программирования...")

# ============================================================================
# 1. ТОП-10 ЯЗЫКОВ ПО ИНДЕКСАМ
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Популярность языков программирования по индексам — 2025', fontsize=18, fontweight='bold')

# TIOBE Index
languages_tiobe = ['Python', 'C', 'C++', 'Java', 'C#', 'JavaScript', 'Visual Basic', 'Go', 'SQL', 'TypeScript']
scores_tiobe = [23.37, 9.68, 8.95, 8.54, 7.65, 3.42, 2.15, 1.87, 1.67, 1.42]
colors_tiobe = [COLORS['success'] if lang == 'Python' else COLORS['warning'] if lang == 'TypeScript'
                else COLORS['primary'] for lang in languages_tiobe]

axes[0, 0].barh(languages_tiobe, scores_tiobe, color=colors_tiobe, alpha=0.7, edgecolor='black')
for i, score in enumerate(scores_tiobe):
    axes[0, 0].text(score + 0.3, i, f'{score}%', va='center', fontsize=10, fontweight='bold')
axes[0, 0].set_xlabel('Score (%)')
axes[0, 0].set_title('TIOBE Index (November 2025)', fontsize=12, pad=10)
axes[0, 0].grid(True, alpha=0.3, axis='x')
axes[0, 0].invert_yaxis()

# PYPL Index
languages_pypl = ['Python', 'Java', 'JavaScript', 'C#', 'C++', 'C', 'R', 'PHP', 'TypeScript', 'Rust']
scores_pypl = [28.97, 15.92, 8.38, 6.77, 6.48, 4.73, 4.45, 4.28, 3.50, 2.59]
colors_pypl = [COLORS['success'] if lang == 'Python' else COLORS['warning'] if lang == 'TypeScript'
               else COLORS['danger'] if lang == 'Rust' else COLORS['primary'] for lang in languages_pypl]

axes[0, 1].barh(languages_pypl, scores_pypl, color=colors_pypl, alpha=0.7, edgecolor='black')
for i, score in enumerate(scores_pypl):
    axes[0, 1].text(score + 0.5, i, f'{score}%', va='center', fontsize=10, fontweight='bold')
axes[0, 1].set_xlabel('Share (%)')
axes[0, 1].set_title('PYPL PopularitY (2025)', fontsize=12, pad=10)
axes[0, 1].grid(True, alpha=0.3, axis='x')
axes[0, 1].invert_yaxis()

# Stack Overflow Survey 2025
languages_so = ['Python', 'TypeScript', 'Rust', 'Go', 'Kotlin', 'C#', 'Swift', 'Java', 'JavaScript', 'PHP']
scores_so = [57.9, 38.2, 9.1, 11.2, 8.5, 27.3, 6.2, 30.5, 63.2, 20.1]
colors_so = [COLORS['success'] if lang == 'Python' else COLORS['warning'] if lang == 'TypeScript'
             else COLORS['danger'] if lang == 'Rust' else COLORS['primary'] for lang in languages_so]

axes[1, 0].barh(languages_so, scores_so, color=colors_so, alpha=0.7, edgecolor='black')
for i, score in enumerate(scores_so):
    axes[1, 0].text(score + 1, i, f'{score}%', va='center', fontsize=10, fontweight='bold')
axes[1, 0].set_xlabel('Adoption (%)')
axes[1, 0].set_title('Stack Overflow Survey 2025', fontsize=12, pad=10)
axes[1, 0].grid(True, alpha=0.3, axis='x')
axes[1, 0].invert_yaxis()

# GitHub Octoverse 2025 - Top Contributors Growth
languages_github = ['TypeScript', 'Python', 'Rust', 'Go', 'Java', 'JavaScript', 'C#', 'PHP', 'Swift', 'Kotlin']
growth_github = [66.63, 48.78, 35.0, 20.0, 5.0, 3.0, 10.0, -5.0, 8.0, 15.0]
colors_github = [COLORS['success'] if g > 30 else COLORS['warning'] if g > 10
                 else COLORS['info'] if g > 0 else COLORS['danger'] for g in growth_github]

axes[1, 1].barh(languages_github, growth_github, color=colors_github, alpha=0.7, edgecolor='black')
for i, growth in enumerate(growth_github):
    axes[1, 1].text(growth + 2, i, f'{growth:+.1f}%', va='center', fontsize=10, fontweight='bold')
axes[1, 1].set_xlabel('YoY Growth (%)')
axes[1, 1].set_title('GitHub Contributors Growth (2025)', fontsize=12, pad=10)
axes[1, 1].grid(True, alpha=0.3, axis='x')
axes[1, 1].invert_yaxis()
axes[1, 1].axvline(x=0, color='black', linestyle='-', linewidth=1)

plt.tight_layout()
plt.savefig(output_dir / '08_languages_popularity_indices.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '08_languages_popularity_indices.svg', bbox_inches='tight')
print("✅ График 8: Популярность языков по индексам")

# ============================================================================
# 2. YEAR-OVER-YEAR ИЗМЕНЕНИЯ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

languages_yoy = ['TypeScript', 'Rust', 'Python', 'Go', 'C#', 'Kotlin', 'Swift',
                 'Java', 'JavaScript', 'C++', 'C', 'PHP']
# TIOBE YoY changes (Nov 2024-2025), TypeScript/Rust используют GitHub growth т.к. не в TIOBE топ-20
yoy_changes = [66.63, 35.0, 2.10, -0.2, 1.20, 1.0, 0.8, -0.45, -0.50, -0.30, -0.15, -2.5]
colors_yoy = [COLORS['success'] if c > 5 else COLORS['warning'] if c > 1
              else COLORS['info'] if c > 0 else COLORS['danger'] for c in yoy_changes]

bars = ax.barh(languages_yoy, yoy_changes, color=colors_yoy, alpha=0.7, edgecolor='black')

for i, change in enumerate(yoy_changes):
    ax.text(change + (2 if change > 0 else -2), i, f'{change:+.2f}%',
            va='center', ha='left' if change > 0 else 'right',
            fontsize=11, fontweight='bold')

ax.axvline(x=0, color='black', linestyle='-', linewidth=2)
ax.set_xlabel('Year-over-Year Change (%)', fontsize=12)
ax.set_title('Изменение популярности языков программирования — YoY 2024-2025',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()

# Аннотации
ax.annotate('TypeScript: Historic Rise\n#1 на GitHub впервые',
            xy=(66.63, 0), xytext=(70, 2),
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.3'))

ax.annotate('Python: +2.1% TIOBE YoY\n(+7.0pp Stack Overflow)',
            xy=(2.10, 2), xytext=(15, 5),
            bbox=dict(boxstyle='round,pad=0.5', fc='lightgreen', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.3'))

plt.tight_layout()
plt.savefig(output_dir / '09_languages_yoy_changes.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '09_languages_yoy_changes.svg', bbox_inches='tight')
print("✅ График 9: YoY изменения языков")

# ============================================================================
# 3. ДОМЕННО-СПЕЦИФИЧЕСКИЕ ЛИДЕРЫ
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 10))

domains = ['Web\nFrontend', 'Web\nBackend', 'Mobile\niOS', 'Mobile\nAndroid',
           'Cross-Platform\nMobile', 'Data Science\n/ AI', 'DevOps /\nCloud',
           'Systems\nProgramming', 'Game\nDev', 'Enterprise']

leaders = ['TypeScript\n+ React', 'Python\n(FastAPI)', 'Swift', 'Kotlin',
           'Kotlin\nMultiplatform', 'Python\n(PyTorch)', 'Go', 'Rust', 'C++ /\nC#', 'Java']

adoption_rates = [87, 73, 95, 80, 23, 85, 49, 35, 65, 97]  # Процент доминирования

colors_domains = [COLORS['warning'], COLORS['success'], COLORS['primary'],
                  COLORS['success'], COLORS['warning'], COLORS['success'],
                  COLORS['info'], COLORS['danger'], COLORS['primary'], COLORS['secondary']]

bars = ax.bar(domains, adoption_rates, color=colors_domains, alpha=0.7, edgecolor='black')

# Добавление лидирующих языков на столбцы
for bar, leader, rate in zip(bars, leaders, adoption_rates):
    ax.text(bar.get_x() + bar.get_width()/2., rate + 2,
            leader, ha='center', va='bottom', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))
    ax.text(bar.get_x() + bar.get_width()/2., rate - 8,
            f'{rate}%', ha='center', va='top', fontsize=12, fontweight='bold', color='white')

ax.set_ylabel('Adoption / Dominance (%)', fontsize=12)
ax.set_xlabel('Domain', fontsize=12)
ax.set_title('Лидирующие языки по доменам разработки — 2025',
             fontsize=14, fontweight='bold', pad=15)
ax.set_ylim(0, 110)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_dir / '10_domain_specific_leaders.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '10_domain_specific_leaders.svg', bbox_inches='tight')
print("✅ График 10: Доменно-специфические лидеры")

# ============================================================================
# 4. FRONTEND ФРЕЙМВОРКИ MARKET SHARE
# ============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('Frontend Фреймворки — Market Share 2025', fontsize=16, fontweight='bold')

# Pie chart
frameworks = ['React', 'Angular', 'Vue.js', 'Svelte', 'Прочие']
market_share = [40, 22, 15.4, 12, 10.6]
colors_fw = [COLORS['primary'], COLORS['danger'], COLORS['success'],
             COLORS['warning'], '#95a5a6']
explode = (0.1, 0, 0, 0.05, 0)

ax1.pie(market_share, labels=frameworks, autopct='%1.1f%%', startangle=90,
        colors=colors_fw, explode=explode, shadow=True)
ax1.set_title('Market Share', fontsize=12, pad=10)

# Bar chart с YoY changes
yoy_changes_fw = [-6.3, -15, 45, 180, 5]
colors_yoy_fw = [COLORS['danger'] if c < 0 else COLORS['success'] for c in yoy_changes_fw]

bars = ax2.barh(frameworks, yoy_changes_fw, color=colors_yoy_fw, alpha=0.7, edgecolor='black')

for i, change in enumerate(yoy_changes_fw):
    ax2.text(change + (5 if change > 0 else -5), i, f'{change:+.1f}%',
             va='center', ha='left' if change > 0 else 'right',
             fontsize=11, fontweight='bold')

ax2.axvline(x=0, color='black', linestyle='-', linewidth=2)
ax2.set_xlabel('YoY Growth (%)')
ax2.set_title('Year-over-Year Change', fontsize=12, pad=10)
ax2.grid(True, alpha=0.3, axis='x')
ax2.invert_yaxis()

plt.tight_layout()
plt.savefig(output_dir / '11_frontend_frameworks.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '11_frontend_frameworks.svg', bbox_inches='tight')
print("✅ График 11: Frontend фреймворки")

# ============================================================================
# 5. AI/ML ФРЕЙМВОРКИ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

ml_frameworks = ['PyTorch', 'TensorFlow', 'Hugging Face\nTransformers',
                 'LangChain', 'scikit-learn', 'Keras', 'JAX']
production_share = [55, 30, 20, 8, 45, 15, 5]  # Примерные проценты использования в production

colors_ml = [COLORS['success'] if share > 40 else COLORS['warning'] if share > 15
             else COLORS['info'] for share in production_share]

bars = ax.barh(ml_frameworks, production_share, color=colors_ml, alpha=0.7, edgecolor='black')

for i, share in enumerate(production_share):
    ax.text(share + 1, i, f'{share}%', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Production Adoption (%)', fontsize=12)
ax.set_title('AI/ML Фреймворки — Production Adoption 2025',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()

# Аннотации
ax.annotate('PyTorch доминирует:\n85%+ research papers\n55% production',
            xy=(55, 0), xytext=(60, 2),
            bbox=dict(boxstyle='round,pad=0.5', fc='lightgreen', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-.3'))

ax.annotate('LangChain: 30% agent\nframework market share',
            xy=(8, 3), xytext=(20, 5),
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.3'))

plt.tight_layout()
plt.savefig(output_dir / '12_ai_ml_frameworks.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '12_ai_ml_frameworks.svg', bbox_inches='tight')
print("✅ График 12: AI/ML фреймворки")

# ============================================================================
# 6. ЗАРПЛАТЫ ПО ЯЗЫКАМ ПРОГРАММИРОВАНИЯ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

languages_salary = ['Rust', 'TypeScript', 'Go', 'Swift', 'Python', 'Java', 'C#', 'JavaScript', 'PHP', 'Ruby']
salaries = [160000, 160000, 150000, 145000, 130000, 120000, 125000, 110000, 95000, 134000]
job_growth = [35, 15, 20, 8, 25, 0, 8, -2, -5, 3]  # YoY job growth %

# Цвет по росту вакансий
colors_salary = [COLORS['success'] if growth > 20 else COLORS['warning'] if growth > 10
                 else COLORS['info'] if growth > 0 else COLORS['danger']
                 for growth in job_growth]

bars = ax.barh(languages_salary, salaries, color=colors_salary, alpha=0.7, edgecolor='black')

for i, (salary, growth) in enumerate(zip(salaries, job_growth)):
    ax.text(salary + 3000, i, f'${salary:,}\n({growth:+d}% jobs)',
            va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Average Annual Salary (USD)', fontsize=12)
ax.set_title('Зарплаты по языкам программирования — USA 2025\n(с указанием роста вакансий YoY)',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()

# Форматирование оси X
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '13_salaries_by_language.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '13_salaries_by_language.svg', bbox_inches='tight')
print("✅ График 13: Зарплаты по языкам")

# ============================================================================
# 7. ТОП TECH STACKS — ЗАРПЛАТНЫЕ КОМБИНАЦИИ
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

tech_stacks = ['Python + PyTorch\n+ CUDA (AI/ML)',
               'TypeScript + React\n+ Node.js',
               'Python + AWS\n+ Kubernetes',
               'Go + Docker\n+ Kubernetes',
               'Rust + Systems\nProgramming',
               'Java + Spring Boot\n+ AWS',
               'C# + .NET\n+ Azure']

stack_salaries = [190000, 140000, 160000, 145000, 175000, 135000, 132000]

colors_stacks = [COLORS['success'] if sal > 160000 else COLORS['warning'] if sal > 140000
                 else COLORS['info'] for sal in stack_salaries]

bars = ax.barh(tech_stacks, stack_salaries, color=colors_stacks, alpha=0.7, edgecolor='black')

for i, salary in enumerate(stack_salaries):
    ax.text(salary + 3000, i, f'${salary:,}', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Average Total Compensation (USD)', fontsize=12)
ax.set_title('Топ Tech Stacks — Average Total Compensation 2025',
             fontsize=14, fontweight='bold', pad=15)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()

# Форматирование оси X
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.tight_layout()
plt.savefig(output_dir / '14_top_tech_stacks.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / '14_top_tech_stacks.svg', bbox_inches='tight')
print("✅ График 14: Топ tech stacks")

print("\n🎉 Все графики языков программирования успешно созданы!")
print(f"📁 Файлы сохранены в: {output_dir.absolute()}")

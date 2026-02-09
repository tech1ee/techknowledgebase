#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дополнительные визуализации для IT Market Report 2025
Графики 39-42: Remote work decline, RTO, Languages, CIS market
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib import rcParams

# Настройка шрифтов для кириллицы
rcParams['font.family'] = 'DejaVu Sans'
rcParams['font.size'] = 10
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['savefig.bbox'] = 'tight'

# Цветовая палитра
colors = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'danger': '#D64045',
    'warning': '#F18F01',
    'neutral': '#6C757D'
}

output_dir = 'output/'

# ============================================================================
# График 39: Remote Work Decline (2022-2025)
# ============================================================================

def plot_remote_work_decline():
    """График падения remote позиций 2022-2025"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Данные
    years = ['Q1 2022', 'Q3 2022', 'Q1 2023', 'Q3 2023', 'Q1 2024', 'Q3 2024', 'Q4 2025']
    remote_percent = [56, 48, 38, 28, 20, 15, 12]
    fortune_500_full_office = [5, 12, 22, 35, 45, 52, 54]

    # График 1: Падение remote позиций
    ax1.plot(years, remote_percent, marker='o', linewidth=3,
             markersize=10, color=colors['danger'], label='Fully Remote позиции')
    ax1.fill_between(range(len(years)), remote_percent, alpha=0.3, color=colors['danger'])

    # Аннотации ключевых точек
    ax1.annotate('Пик пандемии\n56%', xy=(0, 56), xytext=(0.5, 60),
                fontsize=10, ha='center',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    ax1.annotate('Текущий уровень\n12%', xy=(6, 12), xytext=(5.2, 18),
                fontsize=10, ha='center',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    ax1.annotate('-79% падение', xy=(3, 28), xytext=(2.5, 35),
                fontsize=11, ha='center', fontweight='bold', color=colors['danger'])

    ax1.set_xlabel('Период', fontsize=12, fontweight='bold')
    ax1.set_ylabel('% Fully Remote вакансий', fontsize=12, fontweight='bold')
    ax1.set_title('Падение Remote Work: 56% → 12%', fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_ylim(0, 70)
    ax1.legend(loc='upper right', fontsize=10)

    # График 2: Fortune 500 Return to Office
    ax2.bar(years, fortune_500_full_office, color=colors['warning'], edgecolor='black', linewidth=1.5)

    # Аннотации
    for i, (year, value) in enumerate(zip(years, fortune_500_full_office)):
        ax2.text(i, value + 2, f'{value}%', ha='center', fontsize=10, fontweight='bold')

    ax2.axhline(y=50, color=colors['danger'], linestyle='--', linewidth=2, label='Большинство (50%)')
    ax2.set_xlabel('Период', fontsize=12, fontweight='bold')
    ax2.set_ylabel('% компаний с full office', fontsize=12, fontweight='bold')
    ax2.set_title('Fortune 500: Возврат в офис (5% → 54%)', fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.set_ylim(0, 65)
    ax2.legend(loc='upper left', fontsize=10)

    plt.suptitle('КРИЗИС REMOTE WORK: Массовый возврат в офис',
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{output_dir}39_remote_work_decline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ График 39 создан: remote_work_decline.png")


# ============================================================================
# График 40: RTO Mandates Timeline
# ============================================================================

def plot_rto_timeline():
    """Timeline RTO мандатов по компаниям"""

    fig, ax = plt.subplots(figsize=(14, 8))

    # Данные о RTO мандатах (дата, компания, дней в офисе, описание)
    rto_events = [
        ('2023-06', 'Meta', 3, 'Hybrid: 3 дня/неделю'),
        ('2024-01', 'Google', 3, 'Enforced: 3 дня mandatory'),
        ('2024-02', 'Microsoft', 3, 'Hybrid flexible (3 дня)'),
        ('2024-09', 'Dell', 5, 'Full RTO: 5 дней/неделю'),
        ('2025-01-02', 'Amazon', 5, 'САМАЯ ЖЕСТКАЯ: 5 дней обязательно'),
        ('2025-01', 'AT&T', 5, 'Full office return'),
        ('2025-04', 'Google', 3, 'Ужесточение: "return or leave"'),
        ('2023-01', 'Apple', 3, '3 дня maintained (всегда был офис-центрик)')
    ]

    # Преобразование в DataFrame
    df = pd.DataFrame(rto_events, columns=['Date', 'Company', 'Days', 'Description'])
    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
    df = df.sort_values('Date')

    # Цвета по количеству дней
    colors_map = {3: colors['warning'], 5: colors['danger']}
    bar_colors = [colors_map[days] for days in df['Days']]

    # График
    y_positions = range(len(df))
    bars = ax.barh(y_positions, df['Days'], color=bar_colors, edgecolor='black', linewidth=2)

    # Аннотации
    for i, (idx, row) in enumerate(df.iterrows()):
        # Название компании
        ax.text(-0.3, i, row['Company'], ha='right', va='center',
                fontsize=12, fontweight='bold')

        # Количество дней
        ax.text(row['Days'] + 0.15, i, f"{row['Days']} дней/неделю",
                ha='left', va='center', fontsize=10, fontweight='bold')

        # Дата
        date_str = row['Date'].strftime('%b %Y')
        ax.text(row['Days']/2, i, date_str, ha='center', va='center',
                fontsize=9, color='white', fontweight='bold')

    # Настройка осей
    ax.set_yticks(y_positions)
    ax.set_yticklabels(['' for _ in y_positions])  # Убираем автоматические labels
    ax.set_xlabel('Дней в офисе (в неделю)', fontsize=12, fontweight='bold')
    ax.set_xlim(-1, 6)
    ax.set_title('RTO Mandates 2023-2025: Кто и когда вернулся в офис',
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')

    # Легенда
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colors['warning'], edgecolor='black', label='Hybrid (3 дня)'),
        Patch(facecolor=colors['danger'], edgecolor='black', label='Full RTO (5 дней)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)

    # Вертикальная линия сейчас
    ax.axvline(x=3, color='gray', linestyle='--', linewidth=1.5, alpha=0.5, label='Стандарт: 3 дня')

    plt.tight_layout()
    plt.savefig(f'{output_dir}40_rto_mandates_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ График 40 создан: rto_mandates_timeline.png")


# ============================================================================
# График 41: Languages - Demand vs Competition
# ============================================================================

def plot_languages_demand_competition():
    """Спрос и конкуренция по языкам программирования"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Данные
    languages = ['Python\nAI/ML', 'Go\nDevOps', 'TypeScript\nBackend', 'Rust', 'Java',
                 'C#/.NET', 'Kotlin', 'TypeScript\nFrontend']

    # US зарплаты (median)
    salaries_us = [170, 157.5, 135, 155, 131, 117, 133, 113]

    # CIS remote зарплаты (realistic median)
    salaries_cis = [110, 97.5, 70, 115, 70, 70, 62.5, 57.5]

    # Конкуренция (applications per position)
    competition = [300, 175, 400, 75, 400, 300, 300, 1000]

    # CIS hire вероятность %
    hire_probability = [80, 75, 67.5, 55, 70, 75, 70, 35]

    # График 1: Зарплаты US vs CIS
    x = np.arange(len(languages))
    width = 0.35

    bars1 = ax1.bar(x - width/2, salaries_us, width, label='USA Remote',
                    color=colors['primary'], edgecolor='black', linewidth=1.5)
    bars2 = ax1.bar(x + width/2, salaries_cis, width, label='CIS Remote',
                    color=colors['success'], edgecolor='black', linewidth=1.5)

    # Аннотации
    for i, (us, cis) in enumerate(zip(salaries_us, salaries_cis)):
        ax1.text(i - width/2, us + 5, f'${us}K', ha='center', fontsize=8, fontweight='bold')
        ax1.text(i + width/2, cis + 5, f'${cis}K', ha='center', fontsize=8, fontweight='bold')

    ax1.set_xlabel('Язык программирования', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Зарплата (тыс. USD/год)', fontsize=12, fontweight='bold')
    ax1.set_title('Зарплаты Senior: USA vs CIS Remote', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x)
    ax1.set_xticklabels(languages, fontsize=9)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax1.set_ylim(0, 200)

    # График 2: Конкуренция vs Hire Probability
    ax2_twin = ax2.twinx()

    # Конкуренция (bars)
    bars_comp = ax2.bar(x, competition, color=colors['danger'], alpha=0.7,
                        edgecolor='black', linewidth=1.5, label='Конкуренция (заявок)')

    # Hire Probability (line)
    line_hire = ax2_twin.plot(x, hire_probability, marker='o', linewidth=3,
                               markersize=10, color=colors['success'],
                               label='CIS Hire %')

    # Аннотации конкуренции
    for i, comp in enumerate(competition):
        if comp >= 1000:
            ax2.text(i, comp + 50, f'{comp}+', ha='center', fontsize=9,
                    fontweight='bold', color=colors['danger'])
        else:
            ax2.text(i, comp + 30, f'{comp}', ha='center', fontsize=9, fontweight='bold')

    # Аннотации hire probability
    for i, hire in enumerate(hire_probability):
        ax2_twin.text(i + 0.15, hire + 3, f'{hire}%', ha='left', fontsize=8,
                      fontweight='bold', color=colors['success'])

    ax2.set_xlabel('Язык программирования', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Конкуренция (заявок на позицию)', fontsize=12, fontweight='bold', color=colors['danger'])
    ax2_twin.set_ylabel('Вероятность найма из СНГ (%)', fontsize=12, fontweight='bold', color=colors['success'])
    ax2.set_title('Конкуренция vs Шанс найма для CIS', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xticks(x)
    ax2.set_xticklabels(languages, fontsize=9)
    ax2.tick_params(axis='y', labelcolor=colors['danger'])
    ax2_twin.tick_params(axis='y', labelcolor=colors['success'])
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.set_ylim(0, 1200)
    ax2_twin.set_ylim(0, 100)

    # Объединенная легенда
    lines, labels = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left', fontsize=10)

    plt.suptitle('ЯЗЫКИ ПРОГРАММИРОВАНИЯ 2025: Зарплаты и Конкуренция',
                 fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(f'{output_dir}41_languages_demand_competition.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ График 41 создан: languages_demand_competition.png")


# ============================================================================
# График 42: CIS Job Market Size
# ============================================================================

def plot_cis_market_size():
    """Размер рынка IT по странам СНГ"""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Данные по странам
    countries = ['Kazakhstan', 'Russia', 'Uzbekistan', 'Ukraine', 'Belarus', 'Kyrgyzstan', 'Armenia']

    # IT вакансии 2025
    vacancies_2025 = [50000, 59000, 18000, 35000, 12000, 5000, 8000]

    # Средние зарплаты Senior (USD/год)
    salaries_senior = [48000, 65000, 36000, 45000, 46000, 30000, 38000]

    # Рост рынка % YoY
    market_growth_yoy = [15, 63, 22, -2, 4.5, 18, 12]

    # Доступность для remote (subjective score 0-100)
    remote_accessibility = [85, 20, 75, 90, 35, 70, 80]  # Russia/Belarus низкие из-за sanctions

    # График 1: IT вакансии 2025
    colors_countries = [colors['success'] if v > 25000 else colors['warning'] if v > 10000 else colors['neutral']
                        for v in vacancies_2025]

    bars1 = ax1.barh(countries, vacancies_2025, color=colors_countries, edgecolor='black', linewidth=1.5)

    for i, (country, vac) in enumerate(zip(countries, vacancies_2025)):
        ax1.text(vac + 2000, i, f'{vac:,}', ha='left', va='center', fontsize=10, fontweight='bold')

    ax1.set_xlabel('Количество IT вакансий', fontsize=12, fontweight='bold')
    ax1.set_title('Размер IT рынка 2025 (количество вакансий)', fontsize=13, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='x')
    ax1.set_xlim(0, max(vacancies_2025) + 10000)

    # График 2: Средние зарплаты Senior
    colors_salaries = [colors['success'] if s > 50000 else colors['warning'] if s > 35000 else colors['neutral']
                       for s in salaries_senior]

    bars2 = ax2.bar(range(len(countries)), salaries_senior, color=colors_salaries,
                    edgecolor='black', linewidth=1.5)

    for i, sal in enumerate(salaries_senior):
        ax2.text(i, sal + 2000, f'${sal/1000:.0f}K', ha='center', fontsize=10, fontweight='bold')

    ax2.set_xticks(range(len(countries)))
    ax2.set_xticklabels(countries, rotation=45, ha='right', fontsize=10)
    ax2.set_ylabel('Зарплата Senior SWE (USD/год)', fontsize=12, fontweight='bold')
    ax2.set_title('Средние зарплаты Senior (локальный рынок)', fontsize=13, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.set_ylim(0, max(salaries_senior) + 10000)

    # График 3: Рост рынка % YoY
    colors_growth = [colors['success'] if g > 15 else colors['warning'] if g > 5
                     else colors['danger'] if g < 0 else colors['neutral']
                     for g in market_growth_yoy]

    bars3 = ax3.barh(countries, market_growth_yoy, color=colors_growth, edgecolor='black', linewidth=1.5)

    for i, growth in enumerate(market_growth_yoy):
        sign = '+' if growth > 0 else ''
        ax3.text(growth + 2 if growth > 0 else growth - 2, i, f'{sign}{growth}%',
                ha='left' if growth > 0 else 'right', va='center', fontsize=10, fontweight='bold')

    ax3.axvline(x=0, color='black', linewidth=2)
    ax3.set_xlabel('Рост рынка % YoY', fontsize=12, fontweight='bold')
    ax3.set_title('Темпы роста IT рынка (2024→2025)', fontsize=13, fontweight='bold', pad=15)
    ax3.grid(True, alpha=0.3, linestyle='--', axis='x')

    # График 4: Доступность для remote work
    colors_remote = [colors['success'] if r > 70 else colors['warning'] if r > 40 else colors['danger']
                     for r in remote_accessibility]

    bars4 = ax4.bar(range(len(countries)), remote_accessibility, color=colors_remote,
                    edgecolor='black', linewidth=1.5)

    for i, acc in enumerate(remote_accessibility):
        status = '✅' if acc > 70 else '⚠️' if acc > 40 else '❌'
        ax4.text(i, acc + 3, f'{acc}%\n{status}', ha='center', fontsize=9, fontweight='bold')

    ax4.set_xticks(range(len(countries)))
    ax4.set_xticklabels(countries, rotation=45, ha='right', fontsize=10)
    ax4.set_ylabel('Доступность для remote (0-100)', fontsize=12, fontweight='bold')
    ax4.set_title('Доступность для US/EU remote работы', fontsize=13, fontweight='bold', pad=15)
    ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax4.set_ylim(0, 110)

    # Аннотации причин
    ax4.text(1, 15, 'Sanctions', ha='center', fontsize=8, style='italic', color=colors['danger'])
    ax4.text(4, 30, 'Sanctions', ha='center', fontsize=8, style='italic', color=colors['danger'])

    plt.suptitle('РЫНОК IT В СНГ: Вакансии, Зарплаты, Рост, Remote',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(f'{output_dir}42_cis_market_size.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ График 42 создан: cis_market_size.png")


# ============================================================================
# Главная функция
# ============================================================================

def main():
    """Создание всех дополнительных визуализаций"""
    print("\n" + "="*60)
    print("Создание дополнительных визуализаций для IT Market Report 2025")
    print("Графики 39-42")
    print("="*60 + "\n")

    try:
        plot_remote_work_decline()
        plot_rto_timeline()
        plot_languages_demand_competition()
        plot_cis_market_size()

        print("\n" + "="*60)
        print("✅ ВСЕ ВИЗУАЛИЗАЦИИ СОЗДАНЫ УСПЕШНО!")
        print("="*60)
        print("\nСозданные файлы:")
        print("  39_remote_work_decline.png")
        print("  40_rto_mandates_timeline.png")
        print("  41_languages_demand_competition.png")
        print("  42_cis_market_size.png")
        print("\nЛокация: visualization/output/")

    except Exception as e:
        print(f"\n❌ ОШИБКА при создании визуализаций: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

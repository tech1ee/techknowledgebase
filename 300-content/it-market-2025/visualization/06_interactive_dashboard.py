#!/usr/bin/env python3
"""
IT Market Report 2025 - Interactive Dashboard
Интерактивный dashboard с фильтрами и динамическими графиками
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path

output_dir = Path('output')
output_dir.mkdir(exist_ok=True)

print("🚀 Создание интерактивных графиков...")

# ============================================================================
# 1. ИНТЕРАКТИВНАЯ ПОМЕСЯЧНАЯ ДИНАМИКА
# ============================================================================

months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя']
new_jobs = [228000, 195000, 185000, 175000, 180000, 190000, 200000, 205000, 210000, 217238, 220000]
# ИСПРАВЛЕНО 26 ноября 2025: верифицированные данные
layoffs = [2403, 16234, 8834, 24500, 10397, 1606, 16142, 6002, 2205, 33281, 4545]

fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Новые IT вакансии по месяцам', 'Увольнения по месяцам'),
    vertical_spacing=0.15
)

fig.add_trace(
    go.Scatter(x=months, y=new_jobs, mode='lines+markers', name='Новые вакансии',
               line=dict(color='#43AA8B', width=3), marker=dict(size=10),
               hovertemplate='%{x}<br>Вакансии: %{y:,}<extra></extra>'),
    row=1, col=1
)

fig.add_trace(
    go.Bar(x=months, y=layoffs, name='Увольнения', marker_color='#C73E1D',
           hovertemplate='%{x}<br>Увольнения: %{y:,}<extra></extra>'),
    row=2, col=1
)

fig.update_layout(
    title_text='Динамика рынка IT — 2025 (интерактивно)',
    showlegend=True,
    height=800,
    hovermode='x unified'
)

fig.write_html(output_dir / 'interactive_01_job_market_dynamics.html')
print("✅ Интерактивный график 1: Динамика рынка")

# ============================================================================
# 2. ИНТЕРАКТИВНЫЕ ЯЗЫКИ ПРОГРАММИРОВАНИЯ
# ============================================================================

languages = ['Python', 'TypeScript', 'Rust', 'Go', 'Java', 'JavaScript', 'C#', 'C++']
tiobe_scores = [23.37, 1.42, 0, 1.87, 8.54, 3.42, 7.65, 8.95]
# YoY: TIOBE для Python/Go/Java/JS/C#/C++, GitHub growth для TypeScript/Rust
yoy_changes = [2.10, 66.63, 35.0, -0.2, -0.45, -0.50, 1.20, -0.30]
salaries = [130000, 160000, 160000, 150000, 120000, 110000, 125000, 135000]

df_lang = pd.DataFrame({
    'Language': languages,
    'TIOBE Score': tiobe_scores,
    'YoY Change (%)': yoy_changes,
    'Salary (USD)': salaries
})

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Popularity (TIOBE)', 'YoY Growth', 'Average Salary'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]],
    horizontal_spacing=0.1
)

fig.add_trace(
    go.Bar(x=df_lang['Language'], y=df_lang['TIOBE Score'],
           marker_color='#2E86AB', name='TIOBE Score',
           hovertemplate='%{x}<br>Score: %{y:.2f}%<extra></extra>'),
    row=1, col=1
)

fig.add_trace(
    go.Bar(x=df_lang['Language'], y=df_lang['YoY Change (%)'],
           marker_color=['#43AA8B' if y > 10 else '#F18F01' if y > 0 else '#C73E1D'
                         for y in df_lang['YoY Change (%)']],
           name='YoY Change',
           hovertemplate='%{x}<br>Change: %{y:+.2f}%<extra></extra>'),
    row=1, col=2
)

fig.add_trace(
    go.Bar(x=df_lang['Language'], y=df_lang['Salary (USD)'],
           marker_color='#43AA8B', name='Salary',
           hovertemplate='%{x}<br>Salary: $%{y:,}<extra></extra>'),
    row=1, col=3
)

fig.update_layout(
    title_text='Языки программирования — Multi-View 2025',
    showlegend=False,
    height=500
)

fig.write_html(output_dir / 'interactive_02_programming_languages.html')
print("✅ Интерактивный график 2: Языки программирования")

# ============================================================================
# 3. ИНТЕРАКТИВНЫЕ РЕГИОНАЛЬНЫЕ ЗАРПЛАТЫ
# ============================================================================

cities = ['SF Bay Area', 'NYC', 'Seattle', 'Austin', 'Zurich', 'London', 'Amsterdam',
          'Berlin', 'Singapore', 'Sydney', 'Bangalore', 'Almaty']
# Актуализировано из отчёта 2025 (Senior SWE)
salaries_city = [168000, 160000, 155000, 153000, 145000, 96000, 76000,
                 70000, 136000, 90000, 24000, 62000]
col_index = [190, 175, 145, 120, 210, 155, 155, 95, 185, 140, 30, 110]
regions = ['USA', 'USA', 'USA', 'USA', 'Europe', 'Europe', 'Europe',
           'Europe', 'APAC', 'APAC', 'APAC', 'Central Asia']

df_regions = pd.DataFrame({
    'City': cities,
    'Salary': salaries_city,
    'CoL Index': col_index,
    'Region': regions
})

fig = px.scatter(df_regions, x='CoL Index', y='Salary', size='Salary',
                 color='Region', hover_name='City', size_max=50,
                 color_discrete_map={'USA': '#2E86AB', 'Europe': '#A23B72',
                                     'APAC': '#43AA8B', 'Central Asia': '#F18F01'},
                 title='Зарплаты vs Cost of Living по регионам — 2025')

fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>CoL Index: %{x}<br>Salary: $%{y:,}<extra></extra>')
fig.update_layout(height=600, hovermode='closest')
fig.update_xaxes(title_text='Cost of Living Index (базовый = 100)')
fig.update_yaxes(title_text='Average Senior SWE Salary (USD)')

fig.write_html(output_dir / 'interactive_03_regional_salaries.html')
print("✅ Интерактивный график 3: Региональные зарплаты")

# ============================================================================
# 4. ИНТЕРАКТИВНЫЕ FAANG COMPENSATION
# ============================================================================

companies = ['OpenAI', 'Meta', 'LinkedIn', 'NVIDIA', 'Google', 'Amazon', 'Microsoft']
median_tc = [875000, 453000, 355000, 290000, 265000, 265000, 240000]
entry_level = [242000, 183000, 151000, 165000, 187000, 184000, 167000]
senior_level = [900000, 600000, 500000, 400000, 500000, 550000, 450000]

df_faang = pd.DataFrame({
    'Company': companies,
    'Median TC': median_tc,
    'Entry Level': entry_level,
    'Senior Level': senior_level
})

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_faang['Company'],
    y=df_faang['Entry Level'],
    name='Entry Level (L3/IC1)',
    marker_color='#118AB2',
    hovertemplate='%{x}<br>Entry: $%{y:,}<extra></extra>'
))

fig.add_trace(go.Bar(
    x=df_faang['Company'],
    y=df_faang['Median TC'],
    name='Median (All Levels)',
    marker_color='#F18F01',
    hovertemplate='%{x}<br>Median: $%{y:,}<extra></extra>'
))

fig.add_trace(go.Bar(
    x=df_faang['Company'],
    y=df_faang['Senior Level'],
    name='Senior (L5/IC3)',
    marker_color='#43AA8B',
    hovertemplate='%{x}<br>Senior: $%{y:,}<extra></extra>'
))

fig.update_layout(
    title='FAANG+ Total Compensation по уровням — 2025',
    xaxis_title='Company',
    yaxis_title='Total Compensation (USD)',
    barmode='group',
    height=600,
    hovermode='x unified'
)

fig.write_html(output_dir / 'interactive_04_faang_compensation.html')
print("✅ Интерактивный график 4: FAANG compensation")

# ============================================================================
# 5. ИНТЕРАКТИВНАЯ SUNBURST — TECH ECOSYSTEM
# ============================================================================

labels = ['IT Market',
          'USA', 'Europe', 'APAC', 'Central Asia',
          'SF Bay', 'NYC', 'London', 'Berlin', 'Singapore', 'Bangalore', 'Almaty',
          'Python', 'TypeScript', 'Rust', 'Go', 'Java',
          'AI/ML', 'Web Dev', 'Mobile', 'DevOps']
parents = ['',
           'IT Market', 'IT Market', 'IT Market', 'IT Market',
           'USA', 'USA', 'Europe', 'Europe', 'APAC', 'APAC', 'Central Asia',
           'IT Market', 'IT Market', 'IT Market', 'IT Market', 'IT Market',
           'IT Market', 'IT Market', 'IT Market', 'IT Market']
values = [100,
          35, 15, 40, 1,
          12, 8, 6, 4, 15, 12, 0.5,
          8, 7, 2, 3, 9,
          15, 20, 10, 8]

fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues='total',
    hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percent: %{percentRoot}<extra></extra>'
))

fig.update_layout(
    title='IT Market Ecosystem — Hierarchical View 2025',
    height=700
)

fig.write_html(output_dir / 'interactive_05_tech_ecosystem_sunburst.html')
print("✅ Интерактивный график 5: Tech ecosystem sunburst")

# ============================================================================
# 6. ИНТЕРАКТИВНАЯ ВРЕМЕННАЯ ШКАЛА — LAYOFFS
# ============================================================================

companies_timeline = ['Intel', 'Microsoft', 'Amazon', 'Salesforce', 'Meta', 'Oracle', 'Google']
dates = ['2025-04-01', '2025-05-01', '2025-10-28', '2025-03-01', '2025-01-15', '2025-08-13', '2025-04-15']
layoff_counts = [23000, 15000, 14000, 8000, 4200, 3000, 500]

df_timeline = pd.DataFrame({
    'Company': companies_timeline,
    'Date': pd.to_datetime(dates),
    'Layoffs': layoff_counts
})

df_timeline = df_timeline.sort_values('Date')

fig = px.scatter(df_timeline, x='Date', y='Layoffs', size='Layoffs',
                 color='Company', hover_name='Company', size_max=60,
                 title='Хронология крупнейших увольнений — 2025')

fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Date: %{x}<br>Layoffs: %{y:,}<extra></extra>')
fig.update_layout(height=600, hovermode='closest')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Number of Layoffs')

fig.write_html(output_dir / 'interactive_06_layoffs_timeline.html')
print("✅ Интерактивный график 6: Layoffs timeline")

print("\n🎉 Все интерактивные графики успешно созданы!")
print(f"📁 HTML файлы сохранены в: {output_dir.absolute()}")
print("\nОткройте HTML файлы в браузере для интерактивного просмотра:")
for file in sorted(output_dir.glob('interactive_*.html')):
    print(f"  - {file.name}")
print("\nДля запуска full dashboard с фильтрами используйте:")
print("  python 06_interactive_dashboard.py --server")

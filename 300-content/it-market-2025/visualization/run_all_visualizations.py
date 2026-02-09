#!/usr/bin/env python3
"""
IT Market Report 2025 - Master Visualization Script
Запускает все скрипты визуализации последовательно
"""

import subprocess
import sys
from pathlib import Path
import time

# Цветные выводы для терминала
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def run_script(script_path):
    """Запускает Python скрипт и возвращает код завершения"""
    script_name = script_path.name
    print_info(f"Запуск: {script_name}")

    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 минут timeout
        )

        elapsed_time = time.time() - start_time

        if result.returncode == 0:
            print_success(f"{script_name} завершён успешно за {elapsed_time:.1f}с")
            # Показать ключевые строки вывода
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if '✅' in line or '🎉' in line:
                        print(f"  {line}")
            return True
        else:
            print_error(f"{script_name} завершён с ошибкой (код: {result.returncode})")
            if result.stderr:
                print(f"{Colors.FAIL}Stderr:{Colors.ENDC}")
                print(result.stderr[:500])  # Первые 500 символов ошибки
            return False

    except subprocess.TimeoutExpired:
        print_error(f"{script_name} превысил timeout (5 минут)")
        return False
    except Exception as e:
        print_error(f"Ошибка при запуске {script_name}: {str(e)}")
        return False

def main():
    print_header("IT MARKET REPORT 2025 - VISUALIZATION GENERATOR")

    # Проверка текущей директории
    current_dir = Path.cwd()
    if not (current_dir / 'requirements.txt').exists():
        print_error("requirements.txt не найден!")
        print_info("Убедитесь, что вы находитесь в папке visualization/")
        sys.exit(1)

    # Создание output директории
    output_dir = current_dir / 'output'
    output_dir.mkdir(exist_ok=True)
    print_success(f"Output директория: {output_dir.absolute()}")

    # Список скриптов для выполнения
    scripts = [
        '01_job_market_graphs.py',
        '02_programming_languages_graphs.py',
        '03_salary_analysis_graphs.py',
        '04_layoffs_analysis_graphs.py',
        '05_regional_comparison_graphs.py',
        '06_interactive_dashboard.py'
    ]

    print_info(f"Будет выполнено {len(scripts)} скриптов")
    print_info("Это займёт примерно 2-3 минуты")
    print()

    # Запуск всех скриптов
    start_time = time.time()
    results = {}

    for i, script_name in enumerate(scripts, 1):
        script_path = current_dir / script_name

        if not script_path.exists():
            print_error(f"Скрипт не найден: {script_name}")
            results[script_name] = False
            continue

        print(f"\n{Colors.BOLD}[{i}/{len(scripts)}] {script_name}{Colors.ENDC}")
        results[script_name] = run_script(script_path)

    total_time = time.time() - start_time

    # Итоговый отчёт
    print_header("ИТОГИ ВЫПОЛНЕНИЯ")

    successful = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    print(f"Общее время выполнения: {Colors.BOLD}{total_time:.1f} секунд{Colors.ENDC}")
    print()
    print(f"{Colors.OKGREEN}Успешно выполнено: {successful}/{len(scripts)}{Colors.ENDC}")

    if failed > 0:
        print(f"{Colors.FAIL}Провалено: {failed}/{len(scripts)}{Colors.ENDC}")
        print("\nПровалившиеся скрипты:")
        for script, success in results.items():
            if not success:
                print(f"  {Colors.FAIL}❌ {script}{Colors.ENDC}")

    # Список созданных файлов
    print(f"\n{Colors.BOLD}Созданные файлы:{Colors.ENDC}")

    png_files = sorted(output_dir.glob('*.png'))
    svg_files = sorted(output_dir.glob('*.svg'))
    html_files = sorted(output_dir.glob('*.html'))

    print(f"  PNG изображения: {len(png_files)}")
    print(f"  SVG векторы: {len(svg_files)}")
    print(f"  HTML интерактивные: {len(html_files)}")
    print(f"  {Colors.BOLD}Всего: {len(png_files) + len(svg_files) + len(html_files)} файлов{Colors.ENDC}")

    print(f"\n{Colors.OKCYAN}📁 Все файлы сохранены в: {output_dir.absolute()}{Colors.ENDC}")

    # Финальное сообщение
    if failed == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ВСЕ ВИЗУАЛИЗАЦИИ УСПЕШНО СОЗДАНЫ!{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Чтобы просмотреть интерактивные графики:{Colors.ENDC}")
        print(f"  cd {output_dir.absolute()}")
        print(f"  open interactive_01_job_market_dynamics.html  # macOS")
        print(f"  # или")
        print(f"  start interactive_01_job_market_dynamics.html  # Windows")
    else:
        print(f"\n{Colors.WARNING}⚠️  Некоторые скрипты завершились с ошибками{Colors.ENDC}")
        print(f"Проверьте логи выше для деталей")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Прервано пользователем{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Критическая ошибка: {str(e)}")
        sys.exit(1)

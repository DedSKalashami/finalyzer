# display.py - весь интерфейс: баннеры, менюшки, подменюшки

from colorama import init, Fore, Style
from analysator import Analysis
from loader import add_expense, load_data, generate_by_category, get_categories

init(autoreset=True)


# пауза
def pause():
    input(Fore.CYAN + "\n[Нажмите Enter, чтобы продолжить...]")


# баннер
def print_banner():
    banner = r"""
         _______ _________ _        _______  _              _______  _______  _______ 
        (  ____ \\__   __/( (    /|(  ___  )( \   |\     /|/ ___   )(  ____ \(  ____ )
        | (    \/   ) (   |  \  ( || (   ) || (   ( \   / )\/   )  || (    \/| (    )|
        | (__       | |   |   \ | || (___) || |    \ (_) /     /   )| (__    | (____)|
        |  __)      | |   | (\ \) ||  ___  || |     \   /     /   / |  __)   |     __)
        | (         | |   | | \   || (   ) || |      ) (     /   /  | (      | (\ (   
        | )      ___) (___| )  \  || )   ( || (____/\| |    /   (_/\| (____/\| ) \ \__
        |/       \_______/|/    )_)|/     \|(_______/\_/   (_______/(_______/|/   \__/

                                 Анализатор личных финансов                            """
    print(Fore.YELLOW + banner)
    print(
        Fore.WHITE + Style.DIM + "                                                           ~ Знай куда уходят твои деньги\n")


# подменю - запуск и назад
def submenu(title, has_settings=False):
    print(Fore.CYAN + f"\n  ┌─ {title} ─┐")
    print("  1.   Запустить")
    if has_settings:
        print("  2.   Настройки")
    print("  0.   Назад")

    while True:
        choice = input(Fore.WHITE + "\n  Команда: ").strip()

        if choice == "0":
            return "0"
        elif choice == "1":
            return "1"
        elif choice == "2" and has_settings:
            return "2"
        else:
            print(Fore.RED + "     Нет такой команды")


# меню
def analysis_menu(analys):
    while True:
        print(Fore.YELLOW + "\n  ╔══════════════════════════════════╗")
        print(Fore.YELLOW + "  ║          МЕНЮ АНАЛИТИКИ          ║")
        print(Fore.YELLOW + "  ╚══════════════════════════════════╝")

        print(
            "  1. Топ категорий по расходам\n"
            "  2. Лучший и худший месяц\n"
            "  3. Выходные vs будни\n"
            "  4. Стабильность расходов (numpy)\n"
            "  5. Самый дорогой день\n"
            "  6. Динамика расходов (тренд)\n"
            "  7. Крупные траты (выше порога)\n"
            "  8. График по месяцам\n"
            "  9. Диаграмма по категориям\n"
            " 10. Все траты по категории\n"
            "  0. Вернуться в главное меню"
        )

        command = input(Fore.WHITE + "\n  Выберите пункт: ").strip()

        try:
            if command == "0":  # 0. Вернуться в главное меню
                break

            elif command == "1":  # 1. Топ категорий по расходам
                if submenu("Топ категорий") == "1":
                    analys.top_categories()
                    pause()

            elif command == "2":  # 2. Лучший и худший месяц
                if submenu("Анализ по месяцам") == "1":
                    analys.best_and_worst_month()
                    pause()

            elif command == "3":  # 3. Выходные vs будни
                if submenu("Выходные vs будни") == "1":
                    analys.weekend_vs_weekday()
                    pause()

            elif command == "4":  # 4. Стабильность расходов (numpy)
                if submenu("Стабильность расходов") == "1":
                    analys.expense_stability()
                    pause()

            elif command == "5":  # 5. Самый дорогой день
                if submenu("Самый дорогой день") == "1":
                    analys.most_expensive_day()
                    pause()

            elif command == "6":  # 6. Динамика расходов (тренд)
                if submenu("Динамика расходов") == "1":
                    analys.expense_trend()
                    pause()

            elif command == "7":  # 7. Крупные траты (выше порога)
                # Этот пункт с настройками - можно менять порог
                choice = submenu("Крупные траты", has_settings=True)

                if choice == "1":
                    _show_expensive(analys, threshold=3000)

                elif choice == "2":
                    # юзер хочет изменить порог
                    while True:
                        try:
                            threshold = float(input(
                                Fore.WHITE + "  Введите порог в рублях (например 5000): "
                            ))
                            if threshold > 0:
                                break
                            print(Fore.RED + "     Введите число больше 0")
                        except ValueError:
                            print(Fore.RED + "     Введите число!")
                    _show_expensive(analys, threshold)

            elif command == "8":  # 8. График по месяцам
                if submenu("График по месяцам") == "1":
                    analys.plot_monthly()

            elif command == "9":  # 9. Диаграмма по категориям
                if submenu("Диаграмма категорий") == "1":
                    analys.plot_categories()

            elif command == "10":  # 10. Все траты по категории
                _show_by_category()

            else:  # не та команда
                print(Fore.RED + "     Нет такой команды")

        except Exception as e:  # обработка ошибок
            print(Fore.RED + f"\n     Ошибка при анализе: {e}")
            pause()


# ???????????
def _show_expensive(analys, threshold):
    print(Fore.YELLOW + f"\n  ═══ Траты выше {threshold:,.0f} руб ═══")
    count = 0
    for transaction in analys.get_expensive_transactions(threshold):
        print(f"  {transaction}")
        count += 1

    if count == 0:
        print(Fore.GREEN + f"   Нет трат выше {threshold:,.0f} руб")
    else:
        print(Fore.CYAN + f"\n   Всего крупных трат: {count}")
    pause()


# показать все траты по выбранной категории через generate_by_category()
def _show_by_category():
    # получаем список всех категорий из CSV
    categories = get_categories()

    if not categories:
        print(Fore.RED + "   Нет данных!")
        pause()
        return

    # показываем список с номерами
    print(Fore.YELLOW + "\n  ═══ Выберите категорию ═══")
    for i, cat in enumerate(categories, 1):
        print(f"  {i:2}. {cat}")

    # пользователь вводит номер
    while True:
        try:
            num = int(input(Fore.WHITE + "\n  Номер категории (0 - назад): "))
            if num == 0:
                return
            if 1 <= num <= len(categories):
                break
            print(Fore.RED + f"     Введите число от 1 до {len(categories)}")
        except ValueError:
            print(Fore.RED + "     Введите число!")

    chosen = categories[num - 1]

    # используем генератор generate_by_category() из loader.py
    print(Fore.YELLOW + f"\n  ═══ Все траты: {chosen} ═══")
    print(f"  {'Дата':<12} {'Сумма':>10}   {'Описание'}")
    print("  " + "─" * 45)

    count = 0
    total = 0.0

    for row in generate_by_category(chosen):
        # generate_by_category отдаёт по одной строке — это генератор!
        print(f"  {row['date']:<12} {row['amount']:>10,.0f} руб  {row['description']}")
        total += row["amount"]
        count += 1

    print("  " + "─" * 45)

    if count == 0:
        print(Fore.GREEN + "   Нет трат в этой категории")
    else:
        print(Fore.CYAN + f"  Покупок: {count}   |   Итого: {total:,.0f} руб   |   Среднее: {total / count:,.0f} руб")

    pause()


def interactive_menu():
    while True:

        analys = Analysis()  # правка бага: теперь подтягивает данные если юзер добавил новую трату

        print_banner()

        print(Fore.YELLOW + "  ╔══════════════════════════════════╗")
        print(Fore.YELLOW + "  ║           ГЛАВНОЕ МЕНЮ           ║")
        print(Fore.YELLOW + "  ╚══════════════════════════════════╝")
        print(
            "  1. Аналитика\n"
            "  2. Добавить трату\n"
            "  3. Выйти"
        )

        try:
            command = int(input(Fore.WHITE + "\n  Команда: "))

        except ValueError:
            print(Fore.RED + "     Введите число!")
            continue

        if command == 1:
            analysis_menu(analys)

        elif command == 2:
            add_expense(load_data(check=False))
            pause()

        elif command == 3:
            print(Fore.YELLOW + "\n   Следи за деньгами! До встречи!\n")
            break

        else:
            print(Fore.RED + "     Нет такой команды!")
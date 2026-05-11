# main.py - запуск программы (через терминал, команда:   python main.py   )

import argparse
from colorama import init, Fore

from src.analysator import Analysis
from src.loader import add_expense, load_data
from src.display import interactive_menu, analysis_menu

init(autoreset=True)

def main():

    # argparse                                                                  ???
    parser = argparse.ArgumentParser(description="💰 Finance Analyzer - анализатор личных финансов", formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Примеры использования:                                  \n"
            "  python main.py                → открыть меню          \n"
            "  python main.py stats          → быстрая сводка        \n"
            "  python main.py report         → полный отчёт          \n"
            "  python main.py expensive 5000 → траты выше 5000 руб   \n" )
    )

    parser.add_argument("command", nargs="?", default="menu", choices=["menu", "add", "analyze", "stats", "report", "expensive", "import"],
        help=(
            "Команда для выполнения:\n"
            "  menu       -  интерактивное меню (по умолчанию) \n"
            "  add        -  добавить новую трату              \n"
            "  analyze    -  открыть меню аналитики            \n"
            "  stats      -  быстрая сводка по расходам        \n"
            "  report     -  полный отчёт по всем выводам      \n"
            "  expensive  -  показать крупные траты            \n" 
            "  import     -  импортирует csv c т-банка         \n")
    )

    parser.add_argument("--threshold", "-t", type=float, default=3000, help="Порог для команды expensive (по умолчанию 3000 руб)")
    parser.add_argument("--top", "-n", type=int, default=5, help="Количество топ-категорий (по умолчанию 5)")
    parser.add_argument("--file", "-f", type=str, help="Путь к CSV файлу из Т-банка")

    args = parser.parse_args()



    # обработка команд
    # интерактивное меню
    if args.command == "menu":
        interactive_menu()



    # добавление траты
    elif args.command == "add":
        add_expense(load_data(check=False))



    # открытие меню аналитики
    elif args.command == "analyze":
        analys = Analysis()
        analysis_menu(analys)



    # быстрая сводка
    elif args.command == "stats":
        print(Fore.YELLOW + "\n" + "═" * 45)
        print(Fore.YELLOW + "   БЫСТРАЯ СВОДКА ПО РАСХОДАМ")
        print(Fore.YELLOW + "═" * 45)

        analys = Analysis()
        analys.top_categories(top_n=args.top)
        analys.best_and_worst_month()
        analys.weekend_vs_weekday()

        print(Fore.YELLOW + "\n" + "═" * 45 + "\n")



    # полный отчёт
    elif args.command == "report":
        print(Fore.YELLOW + "\n" + "#" * 50)
        print(Fore.YELLOW + "   ПОЛНЫЙ ОТЧЁТ ПО ФИНАНСАМ")
        print(Fore.YELLOW + "#" * 50)

        analys = Analysis()

        # запуск всей аналитики
        analys.top_categories(top_n=args.top)
        analys.best_and_worst_month()
        analys.weekend_vs_weekday()
        analys.expense_stability()
        analys.most_expensive_day()
        analys.expense_trend()

        # допом категории через генераторы
        print(Fore.CYAN + "\n   Все категории в твоих данных:")
        for cat in analys.unique_categories():
            print(f"    • {cat}")

        print(Fore.YELLOW + "\n" + "#" * 50)
        print(Fore.GREEN + "   Отчёт успешно сгенерирован!")
        print(Fore.YELLOW + "#" * 50 + "\n")



    # крупные траты выше порога (по умолчанию 3000, можно изменить: python main.py expensive -t 5000)
    elif args.command == "expensive":
        analys = Analysis()
        threshold = args.threshold

        print(Fore.YELLOW + f"\n   Траты выше {threshold:,.0f} руб:")
        print("═" * 55)

        count = 0
        for transaction in analys.get_expensive_transactions(threshold):

            print(f"  {transaction}")
            count += 1

        print("═" * 55)
        if count == 0:
            print(Fore.GREEN + f"   Нет трат выше {threshold:,.0f} руб")
        else:
            print(Fore.CYAN + f"  Найдено: {count} трат")


    elif args.command == "import":
        if not args.file:
            print(Fore.RED + "     Укажи путь к файлу: python main.py import --file путь_к_файлу.csv")
        else:
            from src.loader import convert_tbank
            convert_tbank(args.file)


# запуск
if __name__ == "__main__":
    main()
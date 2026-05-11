# loader.py - загрузка данных, добавление трат и генераторы для обработки csvшки

import os
import csv
import pandas as pd
from datetime import datetime
from colorama import init, Fore
from decorators import log_action

init(autoreset=True) # для colorama - сброс цвета вывода после каждого print'a

DATA_PATH = "data/expenses.csv"      # наш формат (после конвертации)
TBANK_PATH = "data/tbank.csv"        # сырой файл из Т-банка



# проверка существования файла
@log_action
def check_data():
    # Если нашего файла нет - ищем файл Т-банка
    if not os.path.exists(DATA_PATH):
        if os.path.exists(TBANK_PATH):
            print(Fore.CYAN + "  Найден файл Т-банка, конвертируем...")
            convert_tbank(TBANK_PATH)
        else:
            print(Fore.YELLOW + "  Файл с данными не найден!")
            print(Fore.CYAN + "\n  Как загрузить данные?")
            print("  1. Указать путь к выгрузке из Т-банка")
            print("  2. Начать с пустой базы вручную")

            while True:
                choice = input(Fore.WHITE + "\n  Выбери вариант (1 или 2): ").strip()

                if choice == "1":
                    path = input(Fore.WHITE + "  Путь к файлу из Т-банка: ").strip()
                    if os.path.exists(path):
                        convert_tbank(path)
                        break
                    else:
                        print(Fore.RED + "     Файл не найден! Проверь путь.")

                elif choice == "2":
                    os.makedirs("data", exist_ok=True)
                    df = pd.DataFrame(columns=["date", "category", "amount", "description", "is_weekend"])
                    df.to_csv(DATA_PATH, index=False)
                    add_expense(load_data(check=False))
                    break
                else:
                    print(Fore.RED + "     Введи 1 или 2")



# функция загрузки данных из CSV
@log_action
def load_data(check=True):

    if check:
        check_data()
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"]) # удаляет строки где amount = NaN
    return df



# функция добавления новой траты
@log_action
def add_expense(df):

    print(Fore.CYAN + "\n=== ➕ Добавление новой траты ===")

    categories = [
        "Продукты", "Кафе/Рестораны", "Транспорт", "Такси",
        "Маркетплейсы", "Одежда и обувь", "Развлечения", "Кино",
        "Медицина", "Аптеки", "Цифровые товары", "Мобильная связь",
        "Подарки", "Цветы", "Ремонт и мебель", "Книги и канцтовары",
        "Различные товары", "Сервис", "Красота", "Спорттовары",
        "Госуслуги", "Наличные", "Образование", "Путешествия", "Другое" ]

    while True:
        date_input = input('\nВведите дату (ГГГГ-ММ-ДД), "сегодня", "вчера", "позавчера" или Enter для выхода: ').strip().lower()

        # стоп
        if date_input == "":
            if len(df) == 0:
                print(Fore.RED + "❌ Нет данных! Введите хотя бы одну трату.")
                continue
            break

        # шорткаты
        from datetime import date, timedelta
        shortcuts = {
            "сегодня": date.today(),
            "вчера": date.today() - timedelta(days=1),
            "позавчера": date.today() - timedelta(days=2),
        }
        if date_input in shortcuts:
            valid_date = datetime.combine(shortcuts[date_input], datetime.min.time())
            date_str = valid_date.strftime("%Y-%m-%d")
            print(Fore.GREEN + f"📅 Дата: {date_str}")
        else:
            # выбор даты
            try:
                valid_date = datetime.strptime(date_input, "%Y-%m-%d")
                date_str = valid_date.strftime("%Y-%m-%d")
            except ValueError:
                print(Fore.RED + "     Неверный формат! Пример: 2025-03-15 или 'сегодня'")
                continue

        # выбор категории
        print("\nКатегории:")
        for i, cat in enumerate(categories, 1):
            print(f"  {i:2}. {cat}")

        while True:
            try:
                cat_num = int(input("Выберите номер категории: "))
                if 1 <= cat_num <= len(categories):
                    category = categories[cat_num - 1]
                    break
                print(Fore.RED + f"     Введите число от 1 до {len(categories)}")
            except ValueError:
                print(Fore.RED + "     Введите число!")

        # ввод описания
        description = input("Описание (например: Пятёрочка, Яндекс Go): ").strip()
        if not description:
            description = category # если нет описания, описание = категория

        # ввод суммы
        while True:
            try:
                amount = float(input("Сумма в рублях: "))
                if amount <= 0:
                    print(Fore.RED + "     Сумма должна быть больше 0!")
                    continue
                break
            except ValueError:
                print(Fore.RED + "     Введите число (можно дробное, например 349.90)!")
        # выходной или будний день
        is_weekend = int(valid_date.weekday() >= 5)

        # добавление строки в таблицу
        new_row = {
            "date": date_str,
            "category": category,
            "amount": amount,
            "description": description,
            "is_weekend": is_weekend,
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        print(Fore.GREEN + f"   Добавлено: {category} - {amount:.2f} руб.")

    # сохранение в CSV
    df["date"] = pd.to_datetime(df["date"])
    df_sorted = df.sort_values("date")
    df_sorted.to_csv(DATA_PATH, index=False)
    print(Fore.GREEN + f"\n   Сохранено в '{DATA_PATH}'. Всего записей: {len(df_sorted)}")

    return df_sorted



# конвертатор csv-шки т-банка в нормальный для нас csv
def convert_tbank(tbank_path, output_path=DATA_PATH):

    category_map = {
        "Супермаркеты":        "Продукты",
        "Фастфуд":             "Кафе/Рестораны",
        "Рестораны":           "Кафе/Рестораны",
        "Местный транспорт":   "Транспорт",
        "Транспорт":           "Транспорт",
        "Такси":               "Такси",
        "Цветы":               "Цветы",
        "Одежда и обувь":      "Одежда и обувь",
        "Маркетплейсы":        "Маркетплейсы",
        "Мобильная связь":     "Мобильная связь",
        "Медицина":            "Медицина",
        "Аптеки":              "Аптеки",
        "Развлечения":         "Развлечения",
        "Кино":                "Кино",
        "Цифровые товары":     "Цифровые товары",
        "Подарки и творчество":"Подарки",
        "Сервис":              "Сервис",
        "Различные товары":    "Различные товары",
        "Фото и копицентры":   "Различные товары",
        "Отели":               "Другое",
        "Госуслуги":            "Госуслуги",
        "Заправки":             "Транспорт",
        "Канцтовары":           "Книги и канцтовары",
        "Книги и канцтовары":   "Книги и канцтовары",
        "Красота":              "Красота",
        "Наличные":             "Наличные",
        "Образование":          "Образование",
        "Различные услуги":     "Различные товары",
        "Ремонт и мебель":      "Ремонт и мебель",
        "Связь":                "Мобильная связь",
        "Спорттовары":          "Спорттовары",
        "Путешествия":          "Путешествия",
        "Переводы":              None,
        "Финансы":               None,                 }

    try:
        df = pd.read_csv(tbank_path, sep=";", encoding="utf-8", quotechar='"')
    except UnicodeDecodeError:
        df = pd.read_csv(tbank_path, sep=";", encoding="cp1251", quotechar='"')
    # т-банк иногда выгружает в cp1251 - пробуем оба варианта (by ии)

    df = df[df["Статус"] == "OK"]
    df = df[df["Валюта операции"] == "RUB"]

    df["amount"] = df["Сумма операции"].str.replace(",", ".").astype(float)
    df = df[df["amount"] < 0]
    df["amount"] = df["amount"].abs().round(2)

    df["date"] = pd.to_datetime(
        df["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    ).dt.strftime("%Y-%m-%d")

    df["category"] = df["Категория"].map(category_map)
    df = df[df["category"].notna()]

    df["description"] = df["Описание"]
    df["is_weekend"] = pd.to_datetime(df["date"]).dt.weekday.ge(5).astype(int)

    result = df[["date", "category", "amount", "description", "is_weekend"]]
    result = result.sort_values("date").reset_index(drop=True)

    if os.path.exists(output_path):
        existing = pd.read_csv(output_path)
        result = pd.concat([existing, result]).drop_duplicates().sort_values("date")
        print(Fore.YELLOW + f"     Найден существующий файл - объединяем данные")

    result.to_csv(output_path, index=False)
    print(Fore.GREEN + f"   Импортировано {len(result)} строк из Т-банка → {output_path}")
    return result



# генератор 1: читает csv по строкам
def generate_rows(filepath=DATA_PATH):
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["amount"] = float(row["amount"])
            yield row



# генератор 2: фильтрация трат по категории
def generate_by_category(category, filepath=DATA_PATH):
    for row in generate_rows(filepath):
        if row["category"] == category:
            yield row # если категория совпала - отдаёт строку / если нет переходит к следующей строке.



# список уникальных категорий
def get_categories(filepath=DATA_PATH):
    seen = set()
    for row in generate_rows(filepath):
        seen.add(row["category"])
    return sorted(seen)




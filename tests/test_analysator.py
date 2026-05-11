import types
import pytest
import numpy as np
import pandas as pd

from analysator import Analysis



# фикстуры
@pytest.fixture
def sample_df():
    data = {
        "date": [
            "2025-01-05", "2025-01-15", "2025-01-20",
            "2025-02-03", "2025-02-14", "2025-02-28",
            "2025-03-10", "2025-03-22", "2025-03-31",
            "2025-04-05", "2025-04-18", "2025-04-25",
            "2025-05-01", "2025-05-15", "2025-05-30",
            "2025-06-10", "2025-06-20", "2025-06-28",
        ],
        "category": [
            "Продукты",      "Транспорт",      "Кафе/Рестораны",
            "Продукты",      "Маркетплейсы",   "Транспорт",
            "Кафе/Рестораны","Продукты",        "Аптеки",
            "Маркетплейсы",  "Транспорт",       "Продукты",
            "Развлечения",   "Продукты",        "Транспорт",
            "Кафе/Рестораны","Маркетплейсы",    "Продукты",
        ],
        "amount": [
            1500.0, 200.0,  850.0,
            2300.0, 3500.0, 150.0,
            1200.0, 1800.0, 400.0,
            5000.0, 300.0,  2100.0,
            800.0,  1600.0, 250.0,
            950.0,  4200.0, 1900.0,
        ],
        "description": [
            "Пятёрочка",  "Метро",       "Додо Пицца",
            "ВкусВилл",   "Wildberries", "Автобус",
            "Суши",       "Магнит",      "Аптека 36.6",
            "Ozon",       "Яндекс Go",   "Перекрёсток",
            "Кино",       "Лента",       "Электричка",
            "Кофейня",    "Wildberries", "Пятёрочка",
        ],
        "is_weekend": [
            0, 0, 1,
            0, 1, 0,
            1, 0, 0,
            1, 0, 0,
            0, 0, 1,
            0, 1, 0,
        ],
    }
    return pd.DataFrame(data)


@pytest.fixture
def analysis(sample_df):
    return Analysis(sample_df)


@pytest.fixture
def invalid_df():
    data = {
        "date":        ["2025-01-01"],
        "category":    ["Продукты"],
        "amount":      ["не число"],
        "description": ["Тест"],
        "is_weekend":  [0],
    }
    return pd.DataFrame(data)



 # инициализация и подготовка данных

def test_prepare_adds_month_column(analysis):
    assert "month" in analysis.df.columns

def test_prepare_adds_year_column(analysis):
    assert "year" in analysis.df.columns

def test_prepare_adds_month_name_column(analysis):
    assert "month_name" in analysis.df.columns

def test_prepare_adds_year_month_column(analysis):
    assert "year_month" in analysis.df.columns

def test_prepare_month_value_correct(analysis):
    assert analysis.df["month"].iloc[0] == 1

def test_prepare_year_value_correct(analysis):
    assert analysis.df["year"].iloc[0] == 2025

def test_prepare_month_name_correct(analysis):
    assert analysis.df["month_name"].iloc[0] == "Январь"

def test_prepare_date_is_datetime(analysis):
    assert pd.api.types.is_datetime64_any_dtype(analysis.df["date"])

def test_validate_raises_on_invalid_data(invalid_df):
    with pytest.raises(ValueError):
        Analysis(invalid_df)

def test_dict_month_has_12_months(analysis):
    assert len(analysis.dict_month) == 12

def test_dict_month_january(analysis):
    assert analysis.dict_month[1] == "Январь"

def test_dict_month_december(analysis):
    assert analysis.dict_month[12] == "Декабрь"



 # top_categories
def test_top_categories_returns_string(analysis):
    result = analysis.top_categories()
    assert isinstance(result, str)

def test_top_categories_contains_top_category(analysis):
    result = analysis.top_categories()
    assert "Продукты" in result

def test_top_categories_has_total(analysis):
    result = analysis.top_categories()
    assert "Итого" in result

def test_top_categories_has_percent(analysis):
    result = analysis.top_categories()
    assert "%" in result

def test_top_categories_top_n_limits(analysis):
    result_3 = analysis.top_categories(top_n=3)
    result_5 = analysis.top_categories(top_n=5)
    assert len(result_3) < len(result_5)



 # best_and_worst_month
def test_best_and_worst_month_returns_string(analysis):
    result = analysis.best_and_worst_month()
    assert isinstance(result, str)

def test_best_month_is_april(analysis):
    result = analysis.best_and_worst_month()
    assert "Апрель" in result

def test_worst_month_label_present(analysis):
    result = analysis.best_and_worst_month()
    assert "экономный" in result.lower()

def test_best_worst_month_has_average(analysis):
    result = analysis.best_and_worst_month()
    assert "редн" in result



# weekend_vs_weekday
def test_weekend_vs_weekday_returns_string(analysis):
    result = analysis.weekend_vs_weekday()
    assert isinstance(result, str)

def test_weekend_vs_weekday_has_weekday_label(analysis):
    result = analysis.weekend_vs_weekday()
    assert "Будни" in result

def test_weekend_vs_weekday_has_weekend_label(analysis):
    result = analysis.weekend_vs_weekday()
    assert "Выходные" in result

def test_weekend_vs_weekday_has_percent(analysis):
    result = analysis.weekend_vs_weekday()
    assert "%" in result

def test_weekend_vs_weekday_no_data():
    data = {
        "date":        ["2025-01-06", "2025-01-07"],
        "category":    ["Продукты", "Транспорт"],
        "amount":      [1000.0, 200.0],
        "description": ["Магнит", "Метро"],
        "is_weekend":  [0, 0],
    }
    df = pd.DataFrame(data)
    analys = Analysis(df)
    result = analys.weekend_vs_weekday()
    assert "Недостаточно" in result



# expense_stability
def test_expense_stability_returns_string(analysis):
    result = analysis.expense_stability()
    assert isinstance(result, str)

def test_expense_stability_has_mean(analysis):
    result = analysis.expense_stability()
    assert "Среднемесячные" in result

def test_expense_stability_has_median(analysis):
    result = analysis.expense_stability()
    assert "Медиана" in result

def test_expense_stability_has_std(analysis):
    result = analysis.expense_stability()
    assert "отклонение" in result

def test_expense_stability_has_cv(analysis):
    result = analysis.expense_stability()
    assert "вариации" in result

def test_expense_stability_numpy_mean(sample_df):
    analys = Analysis(sample_df)
    monthly = analys.df.groupby("year_month")["amount"].sum()
    arr = np.array(monthly)
    assert np.mean(arr) > 0

def test_expense_stability_numpy_std(sample_df):
    analys = Analysis(sample_df)
    monthly = analys.df.groupby("year_month")["amount"].sum()
    arr = np.array(monthly)
    assert np.std(arr) >= 0



# most_expensive_day
def test_most_expensive_day_returns_string(analysis):
    result = analysis.most_expensive_day()
    assert isinstance(result, str)

def test_most_expensive_day_has_date(analysis):
    result = analysis.most_expensive_day()
    assert "2025" in result

def test_most_expensive_day_correct_date(analysis):
    result = analysis.most_expensive_day()
    assert "05.04.2025" in result

def test_most_expensive_day_has_category(analysis):
    result = analysis.most_expensive_day()
    assert "Маркетплейсы" in result



# expense_trend
def test_expense_trend_returns_string(analysis):
    result = analysis.expense_trend()
    assert isinstance(result, str)

def test_expense_trend_has_trend_word(analysis):
    result = analysis.expense_trend()
    has_trend = "растут" in result or "падают" in result or "стабильн" in result
    assert has_trend

def test_expense_trend_polyfit(sample_df):
    analys = Analysis(sample_df)
    monthly = analys.df.groupby("year_month")["amount"].sum()
    x = np.arange(len(monthly))
    y = np.array(monthly)
    coeffs = np.polyfit(x, y, 1)
    assert len(coeffs) == 2

def test_expense_trend_polyval(sample_df):
    analys = Analysis(sample_df)
    monthly = analys.df.groupby("year_month")["amount"].sum()
    x = np.arange(len(monthly))
    y = np.array(monthly)
    coeffs = np.polyfit(x, y, 1)
    trend = np.polyval(coeffs, x)
    assert len(trend) == len(x)



# генераторы
def test_unique_categories_is_generator(analysis):
    gen = analysis.unique_categories()
    assert isinstance(gen, types.GeneratorType)

def test_unique_categories_contains_produkty(analysis):
    cats = list(analysis.unique_categories())
    assert "Продукты" in cats

def test_unique_categories_count(analysis):
    cats = list(analysis.unique_categories())
    expected = len(analysis.df["category"].unique())
    assert len(cats) == expected

def test_get_expensive_is_generator(analysis):
    gen = analysis.get_expensive_transactions(1000)
    assert isinstance(gen, types.GeneratorType)

def test_get_expensive_filters_correctly(analysis):
    expensive = list(analysis.get_expensive_transactions(3000))
    assert len(expensive) == 3

def test_get_expensive_empty_above_limit(analysis):
    expensive = list(analysis.get_expensive_transactions(999999))
    assert len(expensive) == 0

def test_get_expensive_returns_strings(analysis):
    for t in analysis.get_expensive_transactions(100):
        assert isinstance(t, str)
        break




# другие
def test_single_row_doesnt_crash():
    data = {
        "date":        ["2025-06-01"],
        "category":    ["Продукты"],
        "amount":      [1000.0],
        "description": ["Магнит"],
        "is_weekend":  [0],
    }
    df = pd.DataFrame(data)
    analys = Analysis(df)
    assert len(analys.df) == 1

def test_all_same_category():
    data = {
        "date":        ["2025-01-01", "2025-01-15", "2025-02-01"],
        "category":    ["Продукты", "Продукты", "Продукты"],
        "amount":      [500.0, 700.0, 900.0],
        "description": ["Магнит", "Пятёрочка", "Лента"],
        "is_weekend":  [0, 0, 1],
    }
    df = pd.DataFrame(data)
    analys = Analysis(df)
    result = analys.top_categories()
    assert "Продукты" in result

def test_amount_sum_preserved(sample_df):
    analys = Analysis(sample_df)
    expected = sample_df["amount"].sum()
    actual = analys.df["amount"].sum()
    assert abs(actual - expected) < 0.01
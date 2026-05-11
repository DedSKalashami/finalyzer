# analysator.py - тут весь анализ данных

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from colorama import init, Fore

from decorators import log_action, format_output
from loader import load_data

init(autoreset=True)

class Analysis:

    def __init__(self, df=None):
        if df is None:
            self.df = load_data()
        else:
            self.df = df
        self.dict_month = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь",
            7: "Июль", 8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
        }
        self._prepare() # вызываем подготовку данных сразу при создании объекта
        if not self._validate():
            raise ValueError("Неверная структура данных - проверь CSV файл")




    # подготовка данных
    @log_action
    def _prepare(self):
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["month"] = self.df["date"].dt.month
        self.df["year"] = self.df["date"].dt.year
        self.df["month_name"] = self.df["month"].map(self.dict_month)
        self.df["year_month"] = self.df["date"].dt.to_period("M").astype(str)

    @log_action
    def _validate(self):
        try:
            need_cols = ["date", "category", "amount", "is_weekend"]
            for col in need_cols:
                if col not in self.df.columns:
                    return False
            if not pd.api.types.is_datetime64_any_dtype(self.df["date"]):
                return False
            if not pd.api.types.is_numeric_dtype(self.df["amount"]):
                return False
            return True
        except KeyError:
            return False


    # топ категорий по расходам
    @log_action
    @format_output("ТОП КАТЕГОРИЙ ПО РАСХОДАМ")
    def top_categories(self, top_n=5):

        total = self.df["amount"].sum()
        # считаем общую сумму всех расходов

        stats = (self.df.groupby("category")["amount"].sum().sort_values(ascending=False).head(top_n))

        result = ""
        for i, (cat, amount) in enumerate(stats.items(), 1):
            procent = amount / total * 100 # процент от общих расходов
            bar = "█" * int(procent / 2) # 1 блок = 2%
            result += f"  {i}. {cat:<20} {amount:>10,.0f} руб  {procent:5.1f}%  {bar}\n"

        result += f"\n  Итого по всем категориям: {total:,.0f} руб"
        return result



    # лучший и худший месяц
    @log_action
    @format_output("АНАЛИЗ ПО МЕСЯЦАМ")
    def best_and_worst_month(self):

        monthly = (self.df.groupby(["year", "month"])["amount"].sum())
        best_year, best_month = monthly.idxmax()
        worst_year, worst_month = monthly.idxmin()

        best_sum  = monthly.max()
        worst_sum = monthly.min()
        avg_sum   = monthly.mean()

        best_name  = f"{self.dict_month[best_month]} {best_year}"
        worst_name = f"{self.dict_month[worst_month]} {worst_year}"

        diff = best_sum - worst_sum

        result = (
            f"  Самый дорогой месяц:      {best_name:<20} {best_sum:>10,.0f} руб  \n"
            f"  Самый экономный месяц:    {worst_name:<20} {worst_sum:>10,.0f} руб  \n"
            f"  Средние расходы в месяц:  {' ':<20} {avg_sum:>10,.0f} руб  \n"
            f"\n  Разница между макс. и мин.: {diff:,.0f} руб"
        )
        return result



    # выхи vs будни
    @log_action
    @format_output("ВЫХОДНЫЕ VS БУДНИ")
    def weekend_vs_weekday(self):

        stats = (self.df.groupby("is_weekend")["amount"].agg(["sum", "mean", "count"]))

        if 0 not in stats.index or 1 not in stats.index:
            return "Недостаточно данных для сравнения"

        wd_sum   = stats.loc[0, "sum"]
        wd_mean  = stats.loc[0, "mean"]
        wd_count = stats.loc[0, "count"]

        we_sum   = stats.loc[1, "sum"]
        we_mean  = stats.loc[1, "mean"]
        we_count = stats.loc[1, "count"]

        diff_pct = (we_mean - wd_mean) / wd_mean * 100

        if diff_pct > 0:
            conclusion = f"   В выходные тратишь на {diff_pct:.1f}% БОЛЬШЕ за одну покупку"
        else:
            conclusion = f"   В выходные тратишь на {abs(diff_pct):.1f}% МЕНЬШЕ за одну покупку"

        result = (
            f"  {'':<8} {'Сумма':>14}  {'Ср. трата':>14}  {'Покупок':>14}\n"
            f"  {'Будни':<8} {wd_sum:>14,.0f}  {wd_mean:>14,.0f}  {int(wd_count):>14}\n"
            f"  {'Выходные':<8} {we_sum:>14,.0f}  {we_mean:>14,.0f}  {int(we_count):>14}\n"
            f"\n{conclusion}"
        )
        return result



    # стабильность расходов
    @log_action
    @format_output("СТАБИЛЬНОСТЬ РАСХОДОВ")
    def expense_stability(self):

        monthly_sums = (self.df.groupby("year_month")["amount"].sum())
        arr = np.array(monthly_sums)
        mean   = np.mean(arr)
        median = np.median(arr)
        std    = np.std(arr)
        cv = std / mean * 100
        max_month = monthly_sums.idxmax()
        min_month = monthly_sums.idxmin()

        if cv < 15:
            stability = " Маленький разброс - расходы почти не меняются"
        elif cv < 30:
            stability = " Умеренный разброс - бывают пики и спады"
        else:
            stability = " Высокий разброс - расходы сильно скачут"

        result = (
            f"  Среднемесячные расходы:      {mean:>10,.0f} руб\n"
            f"  Медиана:                     {median:>10,.0f} руб\n"
            f"  Стандартное отклонение (std):{std:>10,.0f} руб\n"
            f"  Коэффициент вариации (CV):   {cv:>9.1f}%\n\n"
            f"  Самый дорогой период: {max_month}\n"
            f"  Самый дешёвый период: {min_month}\n\n"
            f"  Вывод: {stability}")
        return result



    # самый дорогой день
    @log_action
    @format_output("САМЫЙ ДОРОГОЙ ДЕНЬ")
    def most_expensive_day(self):

        daily = (self.df.groupby("date").agg(total=("amount", "sum"), count=("amount", "count"), top_cat=("category", lambda x: x.value_counts().index[0])))

        peak_date  = daily["total"].idxmax()
        peak_total = daily.loc[peak_date, "total"]
        peak_count = daily.loc[peak_date, "count"]
        peak_cat   = daily.loc[peak_date, "top_cat"]
        avg_daily = daily["total"].mean()
        diff_pct = (peak_total - avg_daily) / avg_daily * 100
        formatted_date = peak_date.strftime("%d.%m.%Y")
        day_names = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
        day_name = day_names[peak_date.weekday()]
        result = (
            f"   Дата:                {formatted_date} ({day_name})\n"
            f"   Потрачено:           {peak_total:,.0f} руб\n"
            f"   Количество покупок:  {int(peak_count)}\n"
            f"   Главная категория:   {peak_cat}\n\n"
            f"  Это на {diff_pct:.0f}% больше среднего дня ({avg_daily:,.0f} руб)"
        )
        return result



    # динамика расходов - растёт или падает
    @log_action
    @format_output("ДИНАМИКА РАСХОДОВ")
    def expense_trend(self):

        monthly = (self.df.groupby("year_month")["amount"].sum().reset_index())
        monthly["index_num"] = range(len(monthly))
        x = np.array(monthly["index_num"])
        y = np.array(monthly["amount"])

        coeffs = np.polyfit(x, y, 1)
        k = coeffs[0]
        trend_line = np.polyval(coeffs, x)
        first_trend = trend_line[0]
        last_trend  = trend_line[-1]
        total_change = last_trend - first_trend

        if k > 500:
            trend_msg = (f"   Расходы растут: +{k:,.0f} руб/мес в среднем\n"
                         f"   За весь период траты выросли на {total_change:,.0f} руб")
        elif k < -500:
            trend_msg = (f"   Расходы падают: {k:,.0f} руб/мес в среднем\n"
                         f"   За весь период траты снизились на {abs(total_change):,.0f} руб")
        else:
            trend_msg = "   Расходы стабильны - нет выраженного роста или падения"

        recent = monthly.tail(6)
        table = "\n  Последние месяцы:\n"
        for _, row in recent.iterrows():
            bar = "█" * int(row["amount"] / 5000)
            table += f"  {row['year_month']}  {row['amount']:>10,.0f} руб  {bar}\n"

        return trend_msg + "\n" + table



    # уникальные категории (кстати тоже генератор)
    def unique_categories(self):
        categories = self.df["category"].unique()
        for cat in categories:
            yield cat



    # дорогие траты выше порога (тоже генератор)
    def get_expensive_transactions(self, threshold=3000):
        daily = self.df.sort_values("amount", ascending=False)
        for _, row in daily.iterrows():
            if row["amount"] >= threshold:
                yield (
                    f"{row['date'].strftime('%d.%m.%Y')}  "
                    f"{row['category']:<20}  "
                    f"{row['amount']:>10,.0f} руб  "
                    f"{row['description']}"
                )


    # графики - динамика расходов по месяцам
    @log_action
    def plot_monthly(self):
        monthly = (self.df.groupby("year_month")["amount"].sum())

        plt.figure(figsize=(12, 5))
        # figsize=(12, 5) - размер графика: 12 дюймов на 5 дюймов

        plt.plot(
            monthly.index,
            monthly.values,
            marker="o",
            linestyle="-",
            color="#4A90D9",
            linewidth=2,
            label="Расходы"
        )

        # тренд-линия
        x = np.arange(len(monthly))
        coeffs = np.polyfit(x, monthly.values, 1)
        trend = np.polyval(coeffs, x)
        plt.plot(monthly.index, trend, linestyle="--", color="#E74C3C",
                 linewidth=1.5, label="Тренд")
        # пунктир красная линия тренда поверх основного графика

        plt.title("Динамика расходов по месяцам", fontsize=14, fontweight="bold")
        plt.xlabel("Месяц")
        plt.ylabel("Сумма (руб)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        print("⏳ Открываю график в новом окне...")
        plt.show()



    # график расходов по категориям (круговая диаграмма)
    @log_action
    def plot_categories(self):
        cat_sums = (self.df .groupby("category")["amount"] .sum() .sort_values(ascending=False))
        plt.figure(figsize=(10, 7))
        plt.pie(cat_sums.values, labels=cat_sums.index, autopct="%1.1f%%", startangle=90)
        plt.title("Расходы по категориям", fontsize=14, fontweight="bold")
        plt.tight_layout()
        print("⏳ Открываю диаграмму в новом окне...")
        plt.show()



# йоу
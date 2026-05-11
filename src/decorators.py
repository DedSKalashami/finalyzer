# decorators.py - декораторы проекта

import os
from datetime import datetime
from functools import wraps



# создаём папку для логов
if not os.path.exists("logs"):
    os.mkdir("logs")
SESSION_TIME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE_PATH = f"logs/session_{SESSION_TIME}.txt"
# имя лога в формате logs/session_YYYY-MM-DD_HH-MM-SS.txt



# декоратор 1: логирование вызовов функций
def log_action(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        action_time = datetime.now().strftime("%H:%M:%S")
        # запоминаем время вызова в формате "18:30:00"

        with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{action_time}] ВЫЗОВ: {func.__name__}\n")

            if len(args) > 1 or kwargs:
                log_file.write(f"    Аргументы: args={args[1:]}, kwargs={kwargs}\n")

        try:
            result = func(*args, **kwargs) # выполнение функции
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
                log_file.write(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"УСПЕХ: {func.__name__} выполнен без ошибок\n"
                )
            return result
        # ошибки в лог
        except Exception as e:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
                log_file.write(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"ОШИБКА в {func.__name__}: {e}\n"
                )
            raise e

    return wrapper



# декоратор 2: делает красивые рамки вокруг вывода для всех аналитических функций из analysator.py.
def format_output(title, show_result=True):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            print(f"\n{'=' * 10} {title.upper()} {'=' * 10}")
            # выглядит:
            # ========== ЗАГОЛОВОК ==========

            result = func(*args, **kwargs) # вызов ориг функции

            if show_result and result:
                print(result)
            print("=" * (22 + len(title)))

            return result

        return wrapper
    return decorator




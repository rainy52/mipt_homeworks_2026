#!/usr/bin/env python
from __future__ import annotations

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_LIST_LENGTH = 3
MONTHS_NUMBER = 12
FEBRUARY_NUMBER = 2
ALLOWED_SYMBOLS = "0123456789.-"
CATEGORY_PARTS_COUNT = 2
INCOME_QUERY_LENGTH = 3
COST_CATEGORIES_QUERY_LENGTH = 2
COST_QUERY_LENGTH = 4
STATS_QUERY_LENGTH = 2
AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"
MONTH_LAST_DAY = (
    31, 28, 31, 30, 31, 30,
    31, 31, 30, 31, 30, 31
)

DATA_DATE = tuple[int, int, int]
RESULT_OF_CALC = tuple[float, float, dict[str, float]]
INCOME_EXPENSES_RESULT = tuple[float, float]
DETAILS_DATA = dict[str, float]
TRANSACTION_DATA = dict[str, Any]
DETAILS_CAT_DATA = dict[str, float]

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """

    if year % 4 == 0 and year % 100 != 0:
        return True
    return year % 400 == 0


def get_days_in_month(month: int, year: int) -> int:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int month: Номер месяца, int year: Номер года
    :return: Количество дней в месяце
    :rtype: int
    """
    if month == FEBRUARY_NUMBER:
        if is_leap_year(year):
            return 29
        return 28
    return MONTH_LAST_DAY[month - 1]


def extract_date(date_str: str) -> DATA_DATE | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str date_str: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """

    input_date = date_str.split("-")
    if len(input_date) != DATE_LIST_LENGTH:
        return None

    if any(not date_fragment.isdigit() for date_fragment in input_date):
        return None

    day = int(input_date[0])
    month = int(input_date[1])
    year = int(input_date[2])

    if not (1 <= month <= MONTHS_NUMBER and year > 0):
        return None

    max_days = get_days_in_month(month, year)
    if not (1 <= day <= max_days):
        return None

    return day, month, year


def extract_amount(amount: str) -> float | None:
    """
    Парсит стоимость из строки.

    :param str amount: Проверяемая строка
    :return: float или None, если не является числом.
    :rtype: float | None
    """
    normalized_amount = amount.replace(",", ".")

    if normalized_amount.startswith("-"):
        if normalized_amount.count("-") > 1:
            return None
        amount_str = normalized_amount[1:]
    else:
        amount_str = normalized_amount

    if amount_str.count(".") > 1:
        return None

    for symbol in amount_str:
        if symbol not in "0123456789.":
            return None

    amount_value = float(normalized_amount)

    if amount_value <= 0:
        return -1

    return amount_value


def validate_category(category_input: str) -> bool:
    """
    Проверяет формат категории

    :param str category_input: Проверяемая строка
    :return: Валиден ли ввод
    :rtype: bool
    """
    category_parts = category_input.split("::")
    if len(category_parts) != CATEGORY_PARTS_COUNT:
        return False

    common_category, target_category = category_parts
    return common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]


def get_target_category(category_input: str) -> str:
    """
    Возвращает вложенную категорию

    :param str category_input: Запрос
    :return: Вложенная категория
    :rtype: str
    """
    return category_input.split("::", maxsplit=1)[1]


def save_transaction() -> None:
    """
    Сохранение транзакции
    """
    financial_transactions_storage.append({})


def income_handler(amount: float, income_date: str) -> str:
    """
    Вносит данные в базу при использовании команды income

    :param int amount: Сумма, str income_date: Дата
    :return: OP_SUCCESS_MSG
    :rtype: str
    """
    if amount <= 0:
        save_transaction()
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        save_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({AMOUNT_KEY: amount, DATE_KEY: date})
    return OP_SUCCESS_MSG


def handle_income_command(input_parts: list[str]) -> None:
    """
    Обработка команды income
    """
    if len(input_parts) != INCOME_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = extract_amount(input_parts[1])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(income_handler(amount, input_parts[2]))


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    """
    Вносит данные в базу при использовании команды cost

    :param int amount: Сумма, str income_date: Дата, str category_name: Категория
    :return: OP_SUCCESS_MSG
    :rtype: str
    """
    if not validate_category(category_name):
        save_transaction()
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        save_transaction()
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        save_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({CATEGORY_KEY: category_name, AMOUNT_KEY: amount, DATE_KEY: date})
    return OP_SUCCESS_MSG


def handle_cost_command(input_parts: list[str]) -> None:
    """
    Обработка команды cost
    """
    if len(input_parts) == COST_CATEGORIES_QUERY_LENGTH and input_parts[1] == "categories":
        print(cost_categories_handler())
        return

    if len(input_parts) != COST_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = extract_amount(input_parts[2])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    output_handler(cost_handler(input_parts[1], amount, input_parts[3]))


def cost_categories_handler() -> str:
    return "\n".join([
        f"{common_category}::{target_category}"
        for common_category, subcategories in EXPENSE_CATEGORIES.items()
        for target_category in subcategories
    ])


def is_same_month(date1: DATA_DATE, date2: DATA_DATE) -> bool:
    """
    Проверяет, одинаковый ли месяц подан в data1 и data2

    :param date1, date2
    :rtype: bool
    """
    first_check = date1[1] == date2[1]
    second_check = date1[2] == date2[2]
    return first_check and second_check


def is_date_earlier_or_equals(date1: DATA_DATE, date2: DATA_DATE) -> bool:
    """
    Проверяет, data1 раньше, чем data2 или равна ей

    :param date1, date2
    :rtype: bool
    """
    for i in range(2, -1, -1):
        if date2[i] != date1[i]:
            return date1[i] < date2[i]
    return True


def process_income_transaction(amount: float, month_income: float) -> float:
    return month_income + amount


def process_expenses_of_transaction(
    amount: float,
    category: str,
    expenses_by_category: DETAILS_CAT_DATA
) -> DETAILS_CAT_DATA:
    """
    Обработка транзакции: добавление суммы к категории

    :param int amount: сумма, str category: категория, expenses_by_category: расходы по категории
    :rtype: dict[str, float]
    """
    target_category = get_target_category(category)
    expenses_by_category[target_category] = expenses_by_category.get(target_category, 0) + amount
    return expenses_by_category


def validate_transaction(
    transaction: TRANSACTION_DATA,
    date: DATA_DATE
) -> bool:
    """
    Валидация транзакции

    :param transaction, date
    :rtype: bool
    """
    tr_date = transaction.get(DATE_KEY)
    if tr_date is None:
        return True

    if not is_same_month(tr_date, date):
        return True

    return not bool(is_date_earlier_or_equals(date, tr_date))


def process_expenses_by_category(date: DATA_DATE) -> dict[str, float]:
    expenses_by_category: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        expenses_by_category = process_transaction_details(transaction, date, expenses_by_category)

    return expenses_by_category


def calculate_month_stats(date: DATA_DATE) -> RESULT_OF_CALC:
    """
    Вычисление статистики за месяц

    :param date
    :rtype: RESULT_OF_CALC
    """
    month_income = float(0)
    month_expenses = float(0)
    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        income, expenses = process_transaction(transaction, date)
        month_income += income
        month_expenses += expenses

    return month_income, month_expenses, process_expenses_by_category(date)


def process_transaction(
    transaction: TRANSACTION_DATA,
    date: DATA_DATE,
) -> INCOME_EXPENSES_RESULT:
    """
    Проведение транзакции

    :param transaction, date
    :rtype: tuple
    """
    month_income = float(0)
    month_expenses = float(0)

    if validate_transaction(transaction, date):
        return month_income, month_expenses

    amount = transaction.get(AMOUNT_KEY)
    if amount is None:
        return month_income, month_expenses

    category = transaction.get(CATEGORY_KEY)
    if category is None:
        month_income = process_income_transaction(amount, month_income)
    else:
        month_expenses += amount

    return month_income, month_expenses


def process_transaction_details(
    transaction: TRANSACTION_DATA,
    date: DATA_DATE,
    details_by_category: DETAILS_CAT_DATA
) -> dict[str, float]:
    if validate_transaction(transaction, date):
        return details_by_category

    amount = transaction.get(AMOUNT_KEY)
    if amount is None:
        return details_by_category

    category = transaction.get(CATEGORY_KEY)
    if category is not None:
        details_by_category = process_expenses_of_transaction(
            amount, category, details_by_category
        )
    return details_by_category


def calculate_total_capital() -> float:
    """
    Расчет накопленной суммы

    :param transaction, date
    :rtype: float
    """
    total_capital = 0

    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        amount = transaction[AMOUNT_KEY]
        if CATEGORY_KEY in transaction:
            total_capital -= amount
        else:
            total_capital += amount

    return total_capital


def handle_stats_command(input_parts: list[str]) -> None:
    """
    Обработка команды stats
    """
    if len(input_parts) != STATS_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(stats_handler(input_parts[1]))


def _category_key(item: tuple[str, float]) -> str:
    return item[0].lower()


def sort_categories(details: DETAILS_DATA, statistics: list[str]) -> str:
    sorted_categories = sorted(details.items(), key=_category_key)
    for idx, (category_name, amount) in enumerate(sorted_categories, start=1):
        statistics.append(f"{idx}. {category_name}: {amount:.2f}")
    return "\n".join(statistics)


def format_statistics(report_date: str, total: float, income: float, expenses: float, details: DETAILS_DATA) -> str:
    """
    Приведение статистики к читаемому виду

    :param report_date, total, income, expenses
    :rtype: str
    """
    result_amount = abs(income - expenses)
    result_type = "loss" if income - expenses < 0 else "profit"

    statistics = [
        "===== STATISTICS =====",
        f"Date: {report_date},",
        f"Total capital: {total:.2f}",
        f"This month, the {result_type} amounted to {result_amount:.2f}",
        f"Income: {income:.2f}",
        f"Expenses: {expenses:.2f}",
        "",
        "Details (category: amount):",
    ]

    return sort_categories(details, statistics)


def output_handler(result: str) -> None:
    print(result)
    if result == NOT_EXISTS_CATEGORY:
        categories_info = cost_categories_handler()
        if categories_info:
            print(categories_info)


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG

    total_capital = calculate_total_capital()
    month_income, month_expenses, details_by_category = calculate_month_stats(date)

    return format_statistics(report_date, total_capital, month_income, month_expenses, details_by_category)


def dispatch_command() -> bool:
    """
    Обработка ввода
    """
    input_line = input().strip()
    if not input_line:
        return False

    input_parts = input_line.split()
    command_name = input_parts[0]

    if command_name == "income":
        handle_income_command(input_parts)
    elif command_name == "cost":
        handle_cost_command(input_parts)
    elif command_name == "stats":
        handle_stats_command(input_parts)
    else:
        print(UNKNOWN_COMMAND_MSG)

    return True


def main() -> None:
    true = True
    while true:
        dispatch_command()


if __name__ == "__main__":
    main()

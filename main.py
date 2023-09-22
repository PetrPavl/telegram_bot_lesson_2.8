import logging
import datetime
from collections import defaultdict
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, ConversationHandler
import pickle
import os


TOKEN_BOT = "6060454250:AAH8QcnM9xaDzXcnBDeqLpN3w8y9yPi16jE"

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Command start was triggered")
    await update.message.reply_text(
        "Ласкаво просимо до бота для ведення доходів і витрат!\n"
        "Команди:\n"
        "Список категорій витрат: /list_exp\n"
        "Додати витрату: /add_exp\n"
        "Показати всі витрати: /show_exp_all\n"
        "Показати витрати за місяць: /show_exp_month\n"
        "Показати витрати за тиждень: /show_exp_week\n"
        "Додати дохід: /add_inc\n"
        "Показати всі транзакції доходів: /show_all_trans\n"
        "Видалити дохід: /del_inc\n"
        "Видалити витрату: /del_exp\n"
        "Статистика за день: /show_stats_day\n"
        "Статистика за поточний тиждень: /show_stats_week\n"
        "Статистика за поточний місяць: /show_stats_month\n"
        "Статистика за поточний рік: /show_stats_year\n"
        "Завершити: /end\n"
    )


async def list_expenses_categories(update: Update, context: CallbackContext) -> None:
    expenses_categories = ["Їжа", "Транспорт", "Житло", "Розваги", "Спорт", "Навчання", "Шоппінг"]
    result = '\n'.join(expenses_categories)
    await update.message.reply_text(f'Категорії витрат: \n{result}')


expenses = ["Їжа", "Транспорт", "Житло", "Розваги", "Спорт", "Навчання", "Шоппінг"]


DATA_FILE = "transactions.pkl"


def save_data(transactions):
    with open(DATA_FILE, "wb") as file:
        pickle.dump(transactions, file)


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as file:
            return pickle.load(file)
    return {"витрати": [], "доходи": []}


transactions = load_data()


async def add_expense(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text.split()

    if len(text) == 3:
        category, amount = text[1], float(text[2])
        if category in expenses:
            date = datetime.datetime.now()
            transactions["витрати"].append({"category": category, "amount": amount, "date": date})
            await update.message.reply_text(
                f"Додано {amount} до категорії '{category}' ({date.strftime('%Y-%m-%d')})."
                )
            save_data(transactions)
        else:
            await update.message.reply_text(
                "Неприпустима категорія витрат. Оберіть зі списку категорій витрат /list_exp"
            )
    else:
        await update.message.reply_text(f"Невірний формат команди. Використовуйте: /add_exp [категорія] [сума]")


async def show_all_expenses(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = "Список всіх витрат:\n"
    for expense in transactions["витрати"]:
        message += (f"Категорія: {expense['category']}, "
                    f"Сума: {expense['amount']}, "
                    f"Дата: {expense['date'].strftime('%Y-%m-%d')}\n")
    await update.message.reply_text(message)


async def show_expenses_by_month(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    message = f"Витрати за поточний місяць ({first_day_of_month.strftime('%B %Y')}):\n"

    total = 0
    for expense in transactions["витрати"]:
        if expense['category'] in expenses and expense['date'].date() >= first_day_of_month:
            total += expense['amount']
            message += (f"Категорія: {expense['category']}, "
                        f"Сума: {expense['amount']}, "
                        f"Дата: {expense['date'].strftime('%Y-%m-%d')}\n")

    message += f"Загальна сума витрат за місяць: {total}"
    await update.message.reply_text(message)


async def show_expenses_by_week(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    message = f"Витрати за поточний тиждень ({start_of_week.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}):\n"

    total = 0
    for expense in transactions["витрати"]:
        if expense['category'] in expenses and start_of_week <= expense['date'].date() <= today:
            total += expense['amount']
            message += (f"Категорія: {expense['category']}, "
                        f"Сума: {expense['amount']}, "
                        f"Дата: {expense['date'].strftime('%Y-%m-%d')}\n")

    message += f"Загальна сума витрат за тиждень: {total}"
    await update.message.reply_text(message)


async def add_income(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text.split()

    if len(text) == 3:
        category, amount = text[1], float(text[2])
        date = datetime.datetime.now()
        transactions["доходи"].append({"category": category, "amount": amount, "date": date})
        await update.message.reply_text(
            f"Додано доход {amount} до категорії '{category}' ({date.strftime('%Y-%m-%d')}).")
        save_data(transactions)
    else:
        await update.message.reply_text(f"Невірний формат команди. Використовуйте: /add_inc [категорія] [сума]")


async def show_all_transactions(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = "Список всіх транзакцій (витрати та доходи):\n"
    for transaction_type, transactions_list in transactions.items():
        for transaction in transactions_list:
            message += (f"Тип: {transaction_type}, "
                        f"Категорія: {transaction['category']}, "
                        f"Сума: {transaction['amount']}, "
                        f"Дата: {transaction['date'].strftime('%Y-%m-%d')}\n"
                        )
    await update.message.reply_text(message)


async def end(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("До побачення!")
    return ConversationHandler.END


async def delete_expense(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text.split()

    if len(text) == 2:
        index = int(text[1]) - 1
        if 0 <= index < len(transactions["витрати"]):
            deleted_transaction = transactions["витрати"].pop(index)
            await update.message.reply_text(
                f"Видалено витрату: Категорія: {deleted_transaction['category']}, "
                f"Сума: {deleted_transaction['amount']}")
            save_data(transactions)
        else:
            await update.message.reply_text("Невірний індекс витрати.")
    else:
        await update.message.reply_text(f"Невірний формат команди. Використовуйте: /del_exp [індекс]")


async def delete_income(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text.split()

    if len(text) == 2:
        index = int(text[1]) - 1
        if 0 <= index < len(transactions["доходи"]):
            deleted_transaction = transactions["доходи"].pop(index)
            await update.message.reply_text(
                f"Видалено дохід: Категорія: {deleted_transaction['category']}, "
                f"Сума: {deleted_transaction['amount']}")
            save_data(transactions)
        else:
            await update.message.reply_text("Невірний індекс доходу.")
    else:
        await update.message.reply_text(f"Невірний формат команди. Використовуйте: /del_inc [індекс]")


async def show_statistics_by_day(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    today = datetime.date.today()
    message = f"Статистика за поточний день ({today.strftime('%Y-%m-%d')}):\n"

    stats_expenses = defaultdict(float)
    stats_income = defaultdict(float)

    for transaction in transactions["витрати"]:
        if transaction['date'].date() == today:
            stats_expenses[transaction['category']] += transaction['amount']

    for transaction in transactions["доходи"]:
        if transaction['date'].date() == today:
            stats_income[transaction['category']] += transaction['amount']

    message += "Витрати:\n"
    for category, total in stats_expenses.items():
        message += f"Категорія: {category}, Сума: {total}\n"

    message += "\nДоходи:\n"
    for category, total in stats_income.items():
        message += f"Категорія: {category}, Сума: {total}\n"

    await update.message.reply_text(message)


async def show_statistics_by_week(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    message = f"Статистика за поточний тиждень ({start_of_week.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}):\n"

    stats_expenses = defaultdict(float)
    stats_income = defaultdict(float)

    for transaction in transactions["витрати"]:
        if start_of_week <= transaction['date'].date() <= today:
            stats_expenses[transaction['category']] += transaction['amount']

    for transaction in transactions["доходи"]:
        if start_of_week <= transaction['date'].date() <= today:
            stats_income[transaction['category']] += transaction['amount']

    message += "Витрати:\n"
    for category, total in stats_expenses.items():
        message += f"Категорія: {category}, Сума: {total}\n"

    message += "\nДоходи:\n"
    for category, total in stats_income.items():
        message += f"Категорія: {category}, Сума: {total}\n"

    await update.message.reply_text(message)


async def show_statistics_by_month(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    message = f"Статистика за поточний місяць ({first_day_of_month.strftime('%B %Y')}):\n"

    stats_expenses = defaultdict(float)
    stats_income = defaultdict(float)

    for transaction in transactions["витрати"]:
        if transaction['date'].date() >= first_day_of_month:
            stats_expenses[transaction['category']] += transaction['amount']

    for transaction in transactions["доходи"]:
        if transaction['date'].date() >= first_day_of_month:
            stats_income[transaction['category']] += transaction['amount']

    message += "Витрати:\n"
    for category, total in stats_expenses.items():
        message += f"Категорія: {category}, Сума: {total}\n"

    message += "\nДоходи:\n"
    for category, total in stats_income.items():
        message += f"Категорія: {category}, Сума: {total}\n"

    await update.message.reply_text(message)


async def show_statistics_by_year(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    today = datetime.date.today()
    current_year = today.year
    message = f"Статистика за поточний рік ({current_year}):\n"

    stats_expenses = defaultdict(float)
    stats_income = defaultdict(float)

    for transaction in transactions["витрати"]:
        if transaction['date'].year == current_year:
            stats_expenses[transaction['category']] += transaction['amount']

    for transaction in transactions["доходи"]:
        if transaction['date'].year == current_year:
            stats_income[transaction['category']] += transaction['amount']

    message += "Витрати:\n"
    for category, total in stats_expenses.items():
        message += f"Категорія: {category}, Сума: {total}\n"

    message += "\nДоходи:\n"
    for category, total in stats_income.items():
        message += f"Категорія: {category}, Сума: {total}\n"

    await update.message.reply_text(message)


def run():
    try:
        with open("transactions.pkl", "rb") as file:
            transaction = pickle.load(file)
    except FileNotFoundError:
        transaction = {"витрати": [], "доходи": []}
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("Application build successfully!")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("list_exp", list_expenses_categories))
    app.add_handler(CommandHandler("add_exp", add_expense))
    app.add_handler(CommandHandler("show_exp_all", show_all_expenses))
    app.add_handler(CommandHandler("show_exp_month", show_expenses_by_month))
    app.add_handler(CommandHandler("show_exp_week", show_expenses_by_week))
    app.add_handler(CommandHandler("add_inc", add_income))
    app.add_handler(CommandHandler("show_all_trans", show_all_transactions))
    app.add_handler(CommandHandler("del_exp", delete_expense))
    app.add_handler(CommandHandler("del_inc", delete_income))
    app.add_handler(CommandHandler("show_stats_day", show_statistics_by_day))
    app.add_handler(CommandHandler("show_stats_week", show_statistics_by_week))
    app.add_handler(CommandHandler("show_stats_month", show_statistics_by_month))
    app.add_handler(CommandHandler("show_stats_year", show_statistics_by_year))
    app.add_handler(CommandHandler("end", end))

    app.run_polling()


if __name__ == "__main__":
    run()

import time
from contextlib import closing

from psycopg2.extras import DictCursor

from config import DATABASE, USER, PASSWORD, HOST, hello, menu, token, proxy_list, menu_reports, menu_projects, \
    menu_tenders, S_START, S_MENU
import telebot
from telebot import apihelper
import psycopg2
import sql_requests

# ============================== BOT API CONNECTION ==============================
from db_worker import States

apihelper.proxy = {'https': f'socks5h://{proxy_list[1]}'}
bot = telebot.TeleBot(token)

# ============================== PROCESS MESSAGE ==============================


@bot.message_handler(commands=["start"])
def say_hello(message):
    bot.send_message(message.chat.id, hello(message.from_user.first_name))
    time.sleep(2)
    bot.send_message(message.chat.id, 'Чтобы получить меню команд, отправьте /menu')
    States.add_state(message.chat.id, message.text)


@bot.message_handler(commands=["back"])
def callbacks(message):
    back = States.get_state(message.chat.id)
    if back == "/start":
        say_hello(message)
    elif back == "/menu":
        send_menu(message)
    elif back == "/reports":
        report(message)
    elif back == "/projects":
        projects(message)
    elif back == "/tenders":
        tenders(message)
    elif back == "/customers":
        customer(message)
    elif back == "None":
        print("None")
    else:
        print("Ошибка в callbacks")

# ======================================================= MAIN MENU ====================================================


@bot.message_handler(commands=["menu"])
def send_menu(message):
    bot.send_message(message.chat.id, menu)
    States.add_state(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["reports"])
def report(message):
    bot.send_message(message.chat.id, menu_reports)
    States.add_state(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["projects"])
def projects(message):
    bot.send_message(message.chat.id, menu_projects)
    States.add_state(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["tenders"])
def tenders(message):
    bot.send_message(message.chat.id, menu_tenders)
    States.add_state(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


# ======================================================= REPORTS ======================================================

@bot.message_handler(commands=["categories"])
def russia(message):
    bot.send_message(message.chat.id, 'Подробный отчет о категориях дорожных сооружений и их статистические данные Вы '
                                      'можете изучить в статье на информационно-аналитическом портале '
                                      'http://127.0.0.1:8000/report/categories')
    States.add_state(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["russia"])
def russia(message):
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_requests.top_10_regions)
            for i in cursor:
                bot.send_message(message.chat.id, f"{i['name']}.\n"
                                                  f"Сооружений в регионе: {i['count']} шт.")
    States.add_state(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["customers"])
def customer_list(message):
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_requests.top_10_customers)
            for i in cursor:
                bot.send_message(message.chat.id, f"{i['fullname']}\nИНН: /{i['inn']}\nСооружений на балансе: {i['count']} шт.")
    States.add_state(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(regexp="\d{10}")
def customer(message):
    rep = sql_requests.get_report(message.text[1:])
    bot.send_message(message.chat.id, rep)
    States.add_state(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


# command_list = ("/start", "/menu", "/reports", "/projects", "/tenders", "/russia", "/customers")


@bot.message_handler(func=lambda message: message.text)
def echo(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)

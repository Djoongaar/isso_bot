import re
import time
from contextlib import closing

from psycopg2.extras import DictCursor
from tabulate import tabulate

import loader
from config import DATABASE, USER, PASSWORD, HOST, hello, menu, token, proxy_list, in_development
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
    time.sleep(1)
    bot.send_message(message.chat.id, menu)
    States.add_state(message.chat.id, message.text)


@bot.message_handler(commands=["back"])
def callbacks(message):
    back = States.get_state(message.chat.id)
    if back == "/start":
        say_hello(message)
    elif back == "/menu":
        send_menu(message)
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


# ==================================================== CURRENT MENU ===================================================


@bot.message_handler(commands=["regions"])
def regions(message):
    regions = []
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_requests.top_regions)
            for i in cursor:
                region_id = i['id'] if i['id'] >= 10 else f"0{i['id']}"
                regions.append([f"<i>/{region_id}</i>", f"[ {i['count']} шт. ]", f"<i>{i['name'][:15]}</i>"])

    bot.send_message(message.chat.id, tabulate(regions, headers=['<b>Код</b>', '<b>[кол-во иссо, шт.]</b>', '<b>Название</b>']),
                     parse_mode='HTML')
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["next5"])
def next5(message):
    try:
        for i in range(5):
            report, length = States.get_customers(message.chat.id)
            bot.send_message(message.chat.id, report, parse_mode='HTML')
            print(length)
        if length > 0:
            bot.send_message(message.chat.id, '1) Cледующие 5 Заказчиков: /next5\n'
                                              '2) Вернуться в главное меню: /menu')
        else:
            bot.send_message(message.chat.id, 'Конец списка ...\n'
                                              'Вернуться в главное меню: /menu')
    except:
        bot.send_message(message.chat.id, 'Конец списка ...\n'
                                          'Вернуться в главное меню: /menu')


@bot.message_handler(commands=["customers"])
def customer_list(message):
    customers = []
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_requests.top_customers)
            for i in cursor:
                customers.append(
                    f"<b>Название: </b>{i['title']}\n"
                    f"<b>ИНН: </b>/{i['inn']}\n"
                    f"<b>Кол-во ИССО: </b>{i['count']} шт."
                )
    States.add_customers(message.chat.id, customers)
    next5(message)


@bot.message_handler(regexp="/\d{10}")
def customer(message):
    rep = sql_requests.get_report(message.text[1:])
    bot.send_message(message.chat.id, rep, parse_mode="HTML")
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(regexp="/plans\d+")
def download_plans(message):
    plans = loader.download_plans(''.join(re.findall(r'\d+', message.text)))
    for plan in plans:
        report = loader.create_report(plan)
        if report:
            bot.send_message(message.chat.id, report, parse_mode="HTML")


# ===================================================== ADVANCED MENU ==================================================


@bot.message_handler(commands=["menu"])
def send_menu(message):
    bot.send_message(message.chat.id, menu)


@bot.message_handler(commands=["reports"])
def reports(message):
    bot.send_message(message.chat.id, in_development)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["projects"])
def projects(message):
    bot.send_message(message.chat.id, in_development)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["tenders"])
def tenders(message):
    bot.send_message(message.chat.id, in_development)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(commands=["categories"])
def categories(message):
    bot.send_message(message.chat.id, 'Подробный отчет о категориях дорожных сооружений и их статистические данные Вы '
                                      'можете изучить в статье на информационно-аналитическом портале '
                                      '<a href="http://127.0.0.1:8000/report/categories">isso.su</a>',
                     parse_mode="HTML", disable_web_page_preview=True)
    bot.send_message(message.chat.id, 'Чтобы вернуться в предыдущий раздел введите /back')


@bot.message_handler(func=lambda message: message.text)
def echo(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)

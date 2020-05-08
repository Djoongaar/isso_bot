import re
import time
from contextlib import closing

from psycopg2.extras import DictCursor

import loader
from config import DATABASE, USER, PASSWORD, HOST, hello, menu, token, proxy_list, in_development
import telebot
from telebot import apihelper
import psycopg2
import sql_requests

# ============================== BOT API CONNECTION ==============================
from db_worker import States

apihelper.proxy = {'https': f'socks5h://{proxy_list[4]}'}
bot = telebot.TeleBot(token)

# ============================== PROCESS MESSAGE ==============================


@bot.message_handler(commands=["start"])
def say_hello(message):
    bot.send_message(message.chat.id, hello(message.from_user.first_name))
    time.sleep(1)
    bot.send_message(message.chat.id, menu, parse_mode='HTML')
    States.add_state(message.chat.id, message.text)


@bot.message_handler(commands=["back"])
def callbacks(message):
    back = States.get_state(message.chat.id)
    if back == "/start":
        say_hello(message)
    elif back == "/menu":
        send_menu(message)
    elif back == "/tenders":
        tenders(message)
    elif back == "/customers":
        customer_list(message)
    elif back == "None":
        print("None")
    else:
        print("Ошибка в callbacks")


# ==================================================== CURRENT MENU ===================================================

@bot.message_handler(commands=["nextRegions"])
def next_regions(message):
    try:
        for i in range(5):
            report, length = States.get_regions(message.chat.id)
            bot.send_message(message.chat.id, report, parse_mode='HTML')
        if length > 0:
            bot.send_message(message.chat.id, '... следующие 5: <i>/nextRegions</i>\n'
                                              'Главное меню: <i>/menu</i>', parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, '[...] Конец списка\n'
                                              'Главное меню: <i>/menu</i>', parse_mode='HTML')
    except:
        bot.send_message(message.chat.id, '[...] Конец списка\n'
                                          'Главное меню: <i>/menu</i>', parse_mode='HTML')


@bot.message_handler(commands=["regions"])
def regions_list(message):
    regions = []
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_requests.top_regions)
            for i in cursor:
                region_id = i['id'] if i['id'] >= 10 else f"0{i['id']}"
                regions.append(
                    f"{i['name']}\n"
                    f"Подробная информация: <i>/region{region_id}</i>"
                )
    States.add_regions(message.chat.id, regions)
    next_regions(message)


@bot.message_handler(commands=["nextCustomers"])
def next_customers(message):
    try:
        for i in range(5):
            report, length = States.get_customers(message.chat.id)
            bot.send_message(message.chat.id, report, parse_mode='HTML')
        if length > 0:
            bot.send_message(message.chat.id, '1) Cледующие 5: <i>/nextCustomers</i>\n'
                                              '2) Вернуться в главное меню: <i>/menu</i>', parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'Конец списка ...\n'
                                              'Вернуться в главное меню: <i>/menu</i>', parse_mode='HTML')
    except:
        bot.send_message(message.chat.id, 'Конец списка ...\n'
                                          'Вернуться в главное меню: <i>/menu</i>', parse_mode='HTML')


@bot.message_handler(commands=["customers"])
def customer_list(message):
    customers = []
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_requests.top_customers)
            for i in cursor:
                customers.append(
                    f"{i['title']}\n"
                    f"ИНН: <i>/{i['inn']}</i>"
                )
    States.add_customers(message.chat.id, customers)
    next_customers(message)


@bot.message_handler(regexp="/\d{10}")  # customer_inn, customer details
def customer_details(message):
    rep = sql_requests.get_customer_details(message.text[1:])
    States.set_inn(message.chat.id, message.text[1:])
    bot.send_message(message.chat.id, rep, parse_mode="HTML")

    bot.send_photo(message.chat.id, photo=open(sql_requests.type_report(message.text[1:]), 'rb'))
    bot.send_photo(message.chat.id, photo=open(sql_requests.category_report(message.text[1:]), 'rb'))


@bot.message_handler(commands=["future_projects"])
def download_plans(message):
    future_projects = sql_requests.future_projects(States.get_inn(message.chat.id))
    for project in future_projects:
        bot.send_message(message.chat.id, project)


# ===================================================== ADVANCED MENU ==================================================


@bot.message_handler(commands=["menu"])
def send_menu(message):
    bot.send_message(message.chat.id, menu, parse_mode='HTML')


@bot.message_handler(commands=["reports"])
def reports(message):
    bot.send_message(message.chat.id, in_development, parse_mode='HTML')


@bot.message_handler(commands=["tenders"])
def tenders(message):
    bot.send_message(message.chat.id, in_development, parse_mode='HTML')


@bot.message_handler(commands=["categories"])
def categories(message):
    bot.send_message(message.chat.id, 'Подробный отчет о категориях дорожных сооружений и их статистические данные Вы '
                                      'можете изучить в статье на информационно-аналитическом портале '
                                      '<a href="http://isso.su/report/categories">isso.su</a>',
                     parse_mode="HTML", disable_web_page_preview=True)


@bot.message_handler(func=lambda message: message.text)
def echo(message):
    bot.send_message(message.chat.id, message.text, parse_mode='HTML')


if __name__ == '__main__':
    bot.polling(none_stop=True)

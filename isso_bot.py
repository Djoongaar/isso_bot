from contextlib import closing

from psycopg2.extras import DictCursor

from config import DATABASE, USER, PASSWORD, HOST, hello, menu, token, proxy_list
import telebot
from telebot import apihelper
import requests
import psycopg2
import sql_requests

# ============================== BOT API CONNECTION ==============================

apihelper.proxy = {'https': f'socks5h://{proxy_list[1]}'}
bot = telebot.TeleBot(token)

# ============================== PROCESS MESSAGE ==============================


@bot.message_handler(commands=["start"])
def say_hello(message):
    bot.send_message(message.chat.id, hello(message.from_user.first_name))
    bot.send_message(message.chat.id, menu)


@bot.message_handler(commands=["report"])
def report(message):
    response = requests.get('http://isso.su/projects/api/project/report/')
    data = response.json()[0]
    msg = f"Всего сооружений: {data['total_projects']} шт. \n" \
          f"Статистика по категориям мостов: \n" \
          f"Сооружений 1 и 2 кат.: {data['count_big_bridges']} шт. ({data['shape_big_bridges']}) \n" \
          f"Сооружений 3 кат.: {data['count_medium_bridges']} шт. ({data['shape_medium_bridges']}) \n" \
          f"Сооружений 4 кат.: {data['count_small_bridges']} шт. ({data['shape_small_bridges']})"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["russia"])
def russia(message):
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_requests.top_20_regions)
            for i in cursor:
                bot.send_message(message.chat.id, f"{i['name']}.\n"
                                                  f"Сооружений в регионе: {i['count']} шт.")
    bot.send_message(message.chat.id, menu)


@bot.message_handler(commands=["customers"])
def customers(message):
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_requests.top_10_customers)
            for i in cursor:
                bot.send_message(message.chat.id, f"{i['fullname']}\nИНН: /{i['inn']}\nСооружений на балансе: {i['count']} шт.")
    bot.send_message(message.chat.id, menu)


@bot.message_handler(regexp="\d{10}")
def customer(message):
    rep = sql_requests.get_report(message.text[1:])
    bot.send_message(message.chat.id, rep)


@bot.message_handler(func=lambda message: message.text)
def echo(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)

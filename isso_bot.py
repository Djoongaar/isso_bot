import config
import telebot
from telebot import apihelper


apihelper.proxy = {'https': f'socks5h://{config.proxy_list[1]}'}
bot = telebot.TeleBot(config.token)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)

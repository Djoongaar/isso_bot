import config
import telebot
from telebot import apihelper

proxy_list = [
    '49.12.4.194:40878',
    '96.113.176.101:1080',
    '49.12.33.219:1080',
    '82.223.120.213:1080',
    '96.96.33.133:1080',
    '216.144.230.233:15993',
    '96.44.133.110:58690',
    '212.129.25.23:30166',
    '198.12.154.22:15687',
    '139.99.104.233:4883',
    '198.12.157.28:62615',
    '92.223.93.212:1080',
    '178.170.168.212:1080',
    '104.248.63.49:30588'
]
apihelper.proxy = {'https': f'socks5h://{proxy_list[1]}'}
bot = telebot.TeleBot(config.token)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)

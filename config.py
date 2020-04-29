# =========================== BOT CONNECTION ===========================

token = '1258620743:AAH0ilCQPFZGVd31nMVduAavSAzyqiTSgVQ'

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

# =========================== DATABASE SETTINGS ===========================

DATABASE = 'isso'
USER = 'issohost'
PASSWORD = 'ws3iysiw'
HOST = '127.0.0.1'

# =========================== VEDIS DATABASE SETTINGS ===========================

DB_VEDIS = "db_vedis.vdb"

S_START = "start"  # /start
S_MENU = "menu"  # /menu
S_REPORTS = "reports"  # /reports /projects /tenders
S_PROJECTS = "projects"  # /reports /projects /tenders
S_TENDERS = "tenders"  # /reports /projects /tenders
S_CUSTOMER = "customer"  # /customers /regions /categories
S_REGIONS = "regions"  # /customers /regions /categories
S_CATEGORIES = "categories"  # /customers /regions /categories
S_OBJECT = "3"  # /region_id /customer_inn /project_category /tender_id

# ================================= MESSAGES =================================


def hello(name):
    return f"Привет {name}, я бот-аналитик отрасли транспортного строительства " \
           f"EVGEN 2.0. У меня можно узнать всю интересующую Вас информацию об" \
           f"искусственных сооружениях дорожного хозяйства страны, заказчиках и " \
           f"их торгах. " \
           f"Для продолжения работы выберите один из пунктов меню: "


menu = f"1) Общие данные статистики: отправьте команду /reports \n" \
       f"2) Поиск информации о проектах: /projects \n" \
       f"3) Крупные аукционы и тендеры: /tenders \n" \
       f"4) Подробная информация о боте-аналитике EVGEN 2.0 /evgen2 \n"

menu_reports = f"1) Данные по типам и категориям ИССО /categories \n" \
       f"2) Общие данные по стране /russia \n" \
       f"3) Данные по регионам России /regions \n" \
       f"4) Статистика по балансодержателям /customers \n"

menu_projects = f"Раздел в разработке. Чтобы связаться с автором " \
                f"бота EVGEN 2.0 пишите в телеграм для @U_geen\n"
menu_tenders = f"Раздел в разработке. Чтобы связаться с автором " \
                f"бота EVGEN 2.0 пишите в телеграм для @U_geen\n"

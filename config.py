# =========================== BOT CONNECTION ===========================

token = '1258620743:AAH0ilCQPFZGVd31nMVduAavSAzyqiTSgVQ'

proxy_list = [
    '49.12.4.194:40878',
    '96.113.176.101:1080',
    '49.12.33.219:1080',
    '82.223.120.213:1080',
    '96.96.33.133:1080',  # 08/09/2020
    '216.144.230.233:15993',
    '96.44.133.110:58690',
    '212.129.25.23:30166',
    '198.12.154.22:15687',
    '139.99.104.233:4883',  # 09/05/2020
    '198.12.157.28:62615',
    '92.223.93.212:1080',
    '178.170.168.212:1080',
    '104.248.63.49:30588'
]

# =========================== DADATA SETTINGS ===========================

API_KEY = 'dde55f7841162de9a5a2dedfe7722c9b9f98300a'
SECRET_KEY = '1fd0b6605316b049c175247cf882852b73d9ff53'

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
           f"EVGEN 2.0. У меня можно узнать всю интересующую Вас информацию об " \
           f"искусственных сооружениях дорожного хозяйства страны, заказчиках и " \
           f"их торгах. " \
           f"Для продолжения работы выберите один из пунктов меню: "


menu = f"1) Информация по регионам: <i>/regions</i> \n" \
       f"2) Данные по заказчикам: <i>/customers</i> \n"


in_development = f"Раздел в разработке. Чтобы связаться с автором " \
                f"бота EVGEN 2.0 пишите в телеграм для @U_geen\n"

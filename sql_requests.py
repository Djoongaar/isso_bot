from contextlib import closing

import psycopg2
from psycopg2.extras import DictCursor

from config import DATABASE, USER, PASSWORD, HOST
from isso_bot import bot

top_regions = """
            select count(p.id) as count, r.id, r.name
            from projectsapp_project as p
            join projectsapp_region as r
            on p.region_id = r.id
            group by r.id
            order by count desc
            limit 30
            """

top_customers = """
SELECT count(*) AS count,
c.title,
c.fullname,
c.address,
c.inn
FROM projectsapp_project p
JOIN projectsapp_customer c ON p.customer_id = c.id
GROUP BY c.id
ORDER BY (count(*)) DESC
LIMIT 50;
"""


def get_report(customer_inn):
    report = {
        'cat_1': 0,
        'cat_2': 0,
        'cat_3': 0,
        'cat_4': 0
    }
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                select title, name, fullname, form_title, address, inn, kpp, management
                from projectsapp_customer
                where inn = '{customer_inn}'
                """
            )
            for i in cursor:
                report['title'] = i['title']
                report['name'] = i['name']
                report['form_title'] = i['form_title']
                report['fullname'] = i['fullname']
                report['address'] = i['address']
                report['inn'] = i['inn']
                report['kpp'] = i['kpp']
                report['management'] = i['management']
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                select count(p.id) as count, p.category
                from projectsapp_project as p
                join projectsapp_customer as c
                on p.customer_id = c.id
                where c.inn = '{customer_inn}'
                group by p.category
                """
            )
            for i in cursor:
                report[f'cat_{i["category"]}'] = f'{i["count"]}'
        print(report)
    return f"<b>Полное название оранизации</b>\n" \
           f"{report['fullname']}\n" \
           f" \n" \
           f"<b>ИНН / КПП</b>\n" \
           f"{report['inn']} / {report['kpp']}\n" \
           f" \n" \
           f"<b>Адрес</b>\n" \
           f"{report['address']}\n" \
           f" \n" \
           f"<b>{report['management'].title()}</b>\n" \
           f"{report['name']}\n" \
           f" \n" \
           f"<b>Количество сооружений 1, 2, 3 и 4 кат.:</b>\n" \
           f"{report['cat_1'] if report['cat_1'] else 0}, {report['cat_2'] if report['cat_2'] else 0}, " \
           f"{report['cat_3'] if report['cat_3'] else 0} и {report['cat_4'] if report['cat_4'] else 0} штук " \
           f"соответственно \n" \
           f" \n" \
           f"<b>Мостов, путепроводов, эстакад, тоннелей</b>\n" \
           f"pass - в разработке\n" \
           f" \n" \
           f"<b>Позиция в рейтинге:</b>\n" \
           f"pass - в разработке\n" \
           f" \n" \
           f"<b>Общая сумма контрактов в 2019г.</b>\n" \
           f"pass - в разработке \n" \
           f" \n" \
           f"<b>Сумма контрактов с начала года:</b>\n" \
           f"pass - в разработке\n" \
           f" \n" \
           f"<b>Планы на текущий год: </b>\n" \
           f"/plans{customer_inn}\n" \
           f" \n"


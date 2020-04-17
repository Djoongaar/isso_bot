from contextlib import closing

import psycopg2
from psycopg2.extras import DictCursor

from config import DATABASE, USER, PASSWORD, HOST
from isso_bot import bot

top_20_regions = """
            select count(p.id) as count, r.name
            from projectsapp_project as p
            join projectsapp_region as r
            on p.region_id = r.id
            group by r.id
            order by count desc
            limit 20
            """

top_10_customers = """
SELECT count(*) AS count,
c.fullname,
c.inn
FROM projectsapp_project p
JOIN projectsapp_customer c ON p.customer_id = c.id
GROUP BY c.id
ORDER BY (count(*)) DESC
LIMIT 10;
"""


def get_report(customer_inn):
    report = {}
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                select title, name, fullname, form_title, address
                from projectsapp_customer
                where inn = '{customer_inn}'
                """
            )
            for i in cursor:
                report['Краткое название'] = i['title']
                report['ФИО руководителя'] = i['name']
                report['Форма предприятия'] = i['form_title']
                report['Полное наименование'] = i['fullname']
                report['Адрес'] = i['address']
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
                report[f'категория {i["category"]}'] = f'{i["count"]} сооружений'
    return f"{report}"

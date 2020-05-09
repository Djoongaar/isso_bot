import os
from contextlib import closing
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from psycopg2.extras import DictCursor

from config import DATABASE, USER, PASSWORD, HOST

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


def get_rate(money):
    try:
        money = float(money)
        if money >= 1000000000:
            value = f"{round(money / 1000000000, 2)} млрд."
        else:
            value = f"{round(money / 1000000, 2)} млн."
    except ValueError as e:
        print(e)
        value = "Данные отсутствуют"
    return value

# =============================== INSERT INTO DATABASE ===============================


def insert_into_tendersapp_tender(data):
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                insert into tendersapp_tender 
                (id,
                name,
                start_price,
                final_price,
                created,
                updated,
                status,
                customer_inn)
                values ('{
                data['pk']}', 
                '{data['fields']['name']}', 
                '{data['fields']['start_price']}',
                '{data['fields']['final_price']}',
                '{data['fields']['created']}',
                '{data['fields']['updated']}',
                '{data['fields']['status']}',
                '{data['fields']['customer_inn']}') 
                on conflict(id) do nothing;
                """
            )
        conn.commit()


def insert_into_tendersapp_plan(data):
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                insert into tendersapp_plan 
                (id,
                name,
                start_price,
                created,
                updated,
                customer_inn,
                year)
                values ('{
                data['pk']}', 
                '{data['fields']['name']}', 
                '{data['fields']['start_price']}',
                '{data['fields']['created']}',
                '{data['fields']['updated']}',
                '{data['fields']['customer_inn']}',
                '{data['fields']['year']}') 
                on conflict(id) do update set 
                start_price = EXCLUDED.start_price,
                name = EXCLUDED.name,
                updated = EXCLUDED.updated,
                customer_inn = EXCLUDED.customer_inn,
                year = EXCLUDED.year;
                """
            )
        conn.commit()


def insert_into_projectsapp_customer(data):
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                insert into projectsapp_customer 
                (id,
                title,
                fullname,
                management,
                name,
                inn,
                kpp,
                okved,
                form_code,
                form_title,
                address,
                district_id)
                values ('{
                data['pk']}', 
                '{data['fields']['title']}', 
                '{data['fields']['fullname']}',
                '{data['fields']['management']}',
                '{data['fields']['name']}',
                '{data['fields']['inn']}',
                '{data['fields']['kpp']}',
                '{data['fields']['okved']}',
                '{data['fields']['form_code']}',
                '{data['fields']['form_title']}',
                '{data['fields']['address']}',
                '{data['fields']['district_id']}') 
                on conflict(id) do nothing;
                """
            )
        conn.commit()


# =============================== SELECT FROM DATABASE ===============================


def customer_details(customer_inn):
    report = {}
    try:
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
        return f"<b>Название организации: </b>\n" \
               f"{report['fullname']}\n" \
               f"\n" \
               f"<b>ИНН / КПП:</b>\n" \
               f"{report['inn']} / {report['kpp']}\n" \
               f"\n" \
               f"<b>Адрес: </b>\n" \
               f"{report['address']}\n" \
               f" \n" \
               f"<b>Форма организации:</b>\n" \
               f"{report['form_title']}\n" \
               f"\n" \
               f"<b>{report['management'].title()}:</b>\n" \
               f"{report['name']}"
    except KeyError as e:
        print(e)
        return False


def category_report(customer_inn):
    bridges = {
        'КАТЕГОРИЯ 1': 0,
        'КАТЕГОРИЯ 2': 0,
        'КАТЕГОРИЯ 3': 0,
        'КАТЕГОРИЯ 4': 0
    }
    customers = []
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
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
                bridges[f'КАТЕГОРИЯ {i["category"]}'] = f'{i["count"]}'
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                 SELECT count(*) AS count,
                    c.title,
                    c.fullname,
                    c.inn
                   FROM projectsapp_project p
                     JOIN projectsapp_customer c ON p.customer_id = c.id
                  GROUP BY c.id
                  ORDER BY (count(*)) DESC
                 LIMIT 5;
                """
            )
            for i in cursor:
                customers.append({
                    "name": i['title'],
                    "fullname": i['fullname'],
                    "inn": i['inn'],
                    "count": int(i["count"])
                })
    categories = [i for i in bridges.keys()]
    values = [int(i) for i in bridges.values()]
    if sum(values):
        pd.DataFrame(values, categories, columns=['Количество']).plot(kind='bar', color='magenta', rot=0, width=0.8)
        plt.title('Количество сооружений по категориям, шт.')
        category_hist_path = os.path.join('media', f'category_hist_{customer_inn}.png')
        plt.savefig(category_hist_path)
        plt.close()
        return category_hist_path
    else:
        return False


def type_report(customer_inn):
    types = []
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                SELECT count(p.id),
                    'МОСТЫ'::text as types
                   FROM projectsapp_project as p
                   JOIN projectsapp_customer as c
                    ON p.customer_id = c.id
                  WHERE c.inn::text = '{customer_inn}' and
                  (to_tsvector('russian', p.name) @@ to_tsquery('russian', 'мост'))

                UNION

                SELECT count(p.id),
                    'ПУТЕПРОВОДЫ'::text as types
                   FROM projectsapp_project as p
                   JOIN projectsapp_customer as c
                    ON p.customer_id = c.id
                  WHERE c.inn::text = '{customer_inn}' and
                  (to_tsvector('russian', p.name) @@ to_tsquery('russian', 'путепровод'))

                UNION

                SELECT count(p.id),
                    'ЭСТАКАДЫ'::text as types
                   FROM projectsapp_project as p
                   JOIN projectsapp_customer as c
                    ON p.customer_id = c.id
                  WHERE c.inn::text = '{customer_inn}' and
                  (to_tsvector('russian', p.name) @@ to_tsquery('russian', 'эстакада'))

                UNION

                SELECT count(p.id),
                    'ТОННЕЛИ'::text as types
                   FROM projectsapp_project as p
                   JOIN projectsapp_customer as c
                    ON p.customer_id = c.id
                  WHERE c.inn::text = '{customer_inn}' and
                  (to_tsvector('russian', p.name) @@ to_tsquery('russian', 'тоннель'));
                """
            )
            for i in cursor:
                types.append({
                    "types": i["types"],
                    "count": i["count"]
                })
    types = pd.DataFrame(types)
    plt.bar(types['types'], types['count'], width=0.8)
    plt.title('Количество сооружений по типам, шт.')
    types_hist_path = os.path.join('media', f'types_hist_{customer_inn}.png')
    plt.savefig(types_hist_path)
    plt.close()
    return types_hist_path


def financial_report(customer_inn):
    report = {}
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                select sum(start_price)
                from tendersapp_tender
                where customer_inn = '{customer_inn}' 
                and created between '2019-01-01' and '2020-01-01'
                """
            )
            for i in cursor:
                report['contracts_2019'] = f'{i["sum"]}'
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                select sum(start_price)
                from tendersapp_tender
                where to_tsvector('russian', name) @@ to_tsquery('russian', '(мост | путепровод | эстакада | тоннель)') and customer_inn = '{customer_inn}' 
                    and (created between '2019-01-01' and '2020-01-01')
                """
            )
            for i in cursor:
                report['bridges_2019'] = f'{i["sum"]}'
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                select sum(start_price)
                from tendersapp_plan
                where customer_inn = '{customer_inn}'
                """
            )
            for i in cursor:
                report['plans_2020'] = f'{i["sum"]}'
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                select sum(start_price)
                from tendersapp_plan
                where to_tsvector('russian', name) @@ to_tsquery('russian', '(мост | путепровод | эстакада | тоннель)') and customer_inn = '{customer_inn}'
                """
            )
            for i in cursor:
                report['plans_isso_2020'] = f'{i["sum"]}'
    if report['contracts_2019'] != 'None':
        contracts_2019 = get_rate(report['contracts_2019'])
        bridges_2019 = get_rate(report['bridges_2019'])
        plans_2020 = get_rate(report['plans_2020'])
        plans_isso_2020 = get_rate(report['plans_isso_2020'])
        return f"<b>Финансовая статистика:</b>\n" \
               f"Освоено в 2019г.: {contracts_2019}\n" \
               f"... в том числе на ИССО: {bridges_2019}\n" \
               f"План бюджета на 2020: {plans_2020}\n" \
               f"... в том числе на ИССО: {plans_isso_2020}\n" \
               f"\n" \
               f"<b>Планируемые проекты: </b>\n" \
               f"/future_projects\n"
    else:
        return False


def future_projects(customer_inn):
    projects = []
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                select *
                from tendersapp_plan
                where customer_inn = '{customer_inn}' 
                    and to_tsvector('russian', name) @@ to_tsquery('russian', '(мост | путепровод | эстакада | тоннель)')
                """
            )
            for i in cursor:
                projects.append(i['name'])
    return projects


def customers_list():
    customers = []
    with closing(psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"""
                     SELECT count(*) AS count,
                        c.fullname,
                        c.inn
                       FROM projectsapp_project p
                         JOIN projectsapp_customer c ON p.customer_id = c.id
                      GROUP BY c.id
                      ORDER BY (count(*)) DESC
                     LIMIT 200;
                    """
            )
            for i in cursor:
                customers.append({
                    "count": i['count'],
                    "fullname": i['fullname'],
                    "inn": i['inn']
                })
    return customers

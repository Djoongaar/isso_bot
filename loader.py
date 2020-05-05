import json
import os
import random
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def timekeeper(function_to_decorate):
    start_time = datetime.now()

    def wrapper(*args, **kwargs):
        func = function_to_decorate(*args, **kwargs)
        result = datetime.now() - start_time
        print(f"Время выполнения {function_to_decorate.__name__}: {result}")
        return func

    return wrapper


# ================================== БОТ ЗАГРУЗКИ И ПАРСИНГА ТЕНДЕРОВ ==================================
@timekeeper
def parsing_data(customer_inn):
    tenders = []
    path = os.path.join("./tendersapp/loaded_pages/", str(customer_inn))
    for j in os.listdir(path):
        with open(f"{path}/{j}", "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, 'html.parser')
            file.close()
            numbers = soup.find_all("div", class_="search-registry-entry-block box-shadow-search-input")
            for i in numbers:
                try:
                    number = i.find("div", class_="registry-entry__header-mid__number").text.strip()[2:]
                    start_prices = sum([int(''.join(re.findall(r'\d', price.text))) / 100 for price in i
                                       .find_all("div", class_="price-block__value")])
                    dates = i.find_all("div", class_="data-block mt-auto")
                    created = "-".join(
                        re.findall(r'\d+', dates[0].find_all("div", class_="data-block__value")[0].text)[::-1])
                    updated = "-".join(
                        re.findall(r'\d+', dates[0].find_all("div", class_="data-block__value")[1].text)[::-1])
                    statuses = i.find("div", class_="registry-entry__header-mid__title").text.strip()
                    names = i.find("div", class_="registry-entry__body-value").text.strip()
                    tenders.append({
                        "model": "tendersapp.tender",
                        "pk": number,
                        "fields": {
                            "start_price": start_prices,
                            "final_price": 0,
                            "created": created,
                            "updated": updated,
                            "status": statuses,
                            "name": names,
                            "customer_inn": str(customer_inn)
                        }
                    })
                except:
                    print(f'Exception erased with number {i}')

    with open(f'./tendersapp/loaded_data/{customer_inn}.json', 'w', encoding='utf-8') as file:
        json.dump(tenders, file, ensure_ascii=False, indent=4)
        file.close()


@timekeeper
def download_tenders(customer_inn):
    driver = webdriver.Chrome()
    driver.get("https://zakupki.gov.ru/")
    input_search = driver.find_element_by_id("quickSearchForm_header_searchString")
    input_search.click()
    input_search.send_keys(customer_inn)
    time.sleep(random.randint(1, 3))
    input_search.submit()
    time.sleep(random.randint(5, 7))
    page_number = 1
    path = os.path.join("./tendersapp/loaded_pages/", str(customer_inn))
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"{path}/page_{str(page_number)}.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)
        file.close()
    # Запускаем цикл сбора информации, котррую затем преобразовавыем в формат json и складываем в переменную tenders
    try:
        while True:
            time.sleep(random.randint(1, 2))
            button_next = driver.find_element_by_class_name("paginator-button-next")
            driver.execute_script("arguments[0].click();", button_next)
            time.sleep(random.randint(2, 4))
            page_number += 1
            with open(f"{path}/page_{str(page_number)}.html", "w", encoding="utf-8") as file:
                file.write(driver.page_source)
                file.close()
    # Если в блоке пагинации нет элемента "next page" значит мы дошли до конца списка
    except NoSuchElementException:
        print(f"{customer_inn} finished normally")

    # Вызвать сообщение если возникнет какая-то другая ошибка
    except:
        print(f"{customer_inn} raised exception")


@timekeeper
def download_plans(customer_inn):
    driver = webdriver.Chrome()
    driver.get(
        "https://zakupki.gov.ru/epz/orderplan/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&structured=true&fz44=on&customerPlaceWithNested=on&actualPeriodRangeYearFrom=2020&sortBy=BY_MODIFY_DATE&pageNumber=1&sortDirection=false&recordsPerPage=_10&searchType=false")
    input_search = driver.find_element_by_id("searchString")
    input_search.click()
    input_search.send_keys(customer_inn)
    time.sleep(0.5)
    input_search.submit()
    time.sleep(1)
    plans = []
    try:
        link_div = driver.find_element_by_class_name("registry-entry__body-caption")
        button = link_div.find_element_by_tag_name('a')
        driver.execute_script("arguments[0].click();", button)
        page = driver.page_source
        plans_list = parsing_plans_dir(page, customer_inn)
        print(type(plans_list))
        plans.extend(plans_list)
        # Запускаем цикл сбора информации, котррую затем преобразовавыем в формат json и складываем в переменную tenders
        try:
            while True:
                time.sleep(random.randint(1, 2))
                button_next = driver.find_element_by_class_name("paginator-button-next")
                driver.execute_script("arguments[0].click();", button_next)
                time.sleep(random.randint(1, 2))
                page = driver.page_source
                plans_list = parsing_plans_dir(page, customer_inn)
                plans.extend(plans_list)
        # Если в блоке пагинации нет элемента "next page" значит мы дошли до конца списка
        except NoSuchElementException:
            print(f"{customer_inn} finished normally")
        # Вызвать сообщение если возникнет какая-то другая ошибка
        except IndexError as e:
            print(f"{customer_inn} raised exception {e}")
    except NoSuchElementException as e:
        print(e)
    return plans


def parsing_plans_dir(page, customer_inn):
    plans = []
    soup = BeautifulSoup(page, 'html.parser')
    numbers = soup.find_all("div", class_="search-registry-entry-block box-shadow-search-input")
    for i in numbers:
        try:
            number = i.find("div", class_="registry-entry__header-mid__number").text.strip()
            dates = i.find_all("div", class_="data-block mt-auto")
            start_prices = "".join(
                re.findall(r'\d+', dates[0].find_all("div", class_="data-block__value")[0].text))
            created = "-".join(
                re.findall(r'\d+', dates[0].find_all("div", class_="data-block__value")[1].text)[::-1])
            updated = "-".join(
                re.findall(r'\d+', dates[0].find_all("div", class_="data-block__value")[2].text)[::-1])
            names = i.find("div", class_="registry-entry__body-value").text.strip()
            year = i.find("div", class_="d-flex lots-wrap-content__body__val").text.strip()
            plans.append({
                "model": "tendersapp.plan",
                "pk": number,
                "fields": {
                    "start_price": int(start_prices) / 100,
                    "created": created,
                    "updated": updated,
                    "name": names,
                    "year": year,
                    "customer_inn": str(customer_inn)
                }
            })
        except IndexError as e:
            number = i.find("div", class_="registry-entry__header-mid__number").text.strip()
            dates = i.find_all("div", class_="data-block mt-auto")
            start_prices = 0
            created = "-".join(
                re.findall(r'\d+', dates[0].find_all("div", class_="data-block__value")[0].text)[::-1])
            updated = "-".join(
                re.findall(r'\d+', dates[0].find_all("div", class_="data-block__value")[1].text)[::-1])
            names = i.find("div", class_="registry-entry__body-value").text.strip()
            year = i.find("div", class_="d-flex lots-wrap-content__body__val").text.strip()
            plans.append({
                "model": "tendersapp.plan",
                "pk": number,
                "fields": {
                    "start_price": start_prices,
                    "created": created,
                    "updated": updated,
                    "name": names,
                    "year": year,
                    "customer_inn": str(customer_inn)
                }
            })
            print(f'{customer_inn} {number}')
            print(f'{e}')
    print(type(plans))
    return plans


def create_report(plan):
    pattern = re.compile(r'.*мост.* | .*путепровод.*')
    if pattern.match(plan['fields']['name']):
        return f"<b>Полное название мероприятия</b>\n" \
               f"{plan['fields']['name']}\n" \
               f" \n" \
               f"<b>ID в план-графике</b>\n" \
               f"{plan['pk']}\n" \
               f" \n" \
               f"<b>Запланировано на год: </b>\n" \
               f"{plan['fields']['year']}\n"

# ================================== БОТ ОБНОВЛЕНИЯ ТЕНДЕРОВ КЛИЕНТА ==================================


customers = [
    "1660049283",
    "0274162934",
    "7717151380",
    "5000001525",
    "2538030581",
    "6905009018",
    "7722765428",
    "2900000511",
    "6658078110",
    "3664098214",
    "5257056163",
    "2725022365",
    "6315800523",
    "3525092617",
    "1101160228",
    "6234066600",
    "1831088158",
    "7714125897",
    "5610070022",
    "7826062821",
    "2225079331",
    "6163053715",
    "5321047240",
    "2460017720",
    "2309075012",
    "3808059441",
    "5836010699",
    "3234046165",
    "2320100329",
    "4027074134"
]
customer_plans = [
    "0278007048",
    "0326012322",
    "1001117010",
    "1402008636",
    "1660061210",
    "2126000323",
    "2309033598",
    "2460028834",
    "2632041647",
    "2725022365",
    # "2721144517",
    "3525065660",
    "3800000140",
    "4909083435",
    "5031035549",
    "5752000133",
    "5836010699",
    # "6147014910",
    "6725000810",
    "6832018699",
    "6905005038",
    "7223007316",
    "7451189048",
    "7714125897",
    "7826062821",
    "0814041687",
    "2320100329",
    "5405201071",
    "7814148129",
    "2225061905",
    "7536053744",
    "1435193127",
    "9102157783"
]
set_customers = [
    '6147014910',
    '5031035549',
    '7722765428',
    '7717151380',
    '2309075012',
    '7814148129',
    '3234046165',
    '1660049283',
    '1001117010',
    '2225061905',
    '0274162934',
    '9102157783',
    '2725022365',
    '5836010699',
    '2900000511',
    '5000001525',
    '6905009018',
    '2460017720',
    '0814041687',
    '7223007316',
    '7536053744',
    '2632041647',
    '3525065660',
    '5257056163',
    '4909083435',
    '7451189048',
    '3808059441',
    '5405201071',
    '3525092617',
    '6163053715',
    '2126000323',
    '3800000140',
    '6725000810',
    '0278007048',
    '7714125897',
    '1660061210',
    '1402008636',
    '6658078110',
    '3664098214',
    '1831088158',
    '1101160228',
    '4027074134',
    '6315800523',
    '5321047240',
    '2721144517',
    '6832018699',
    '6905005038',
    '5610070022',
    '1435193127',
    '2225079331',
    '2460028834',
    '6234066600',
    '7826062821',
    '2538030581',
    '0326012322',
    '5752000133',
    '2309033598',
    '2320100329'
]

if __name__ == '__main__':
    download_plans(customers[0])

import random
import re
import time
from datetime import datetime

from selenium import webdriver
from xvfbwrapper import Xvfb
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException

import sql_requests
import requests
import config
from bs4 import BeautifulSoup


# ================================== ЗАГРУЗКА ТЕНДЕРОВ ==================================


def parsing_data(page, customer_inn):
    tenders = []
    soup = BeautifulSoup(page, 'html.parser')
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
    return tenders


def download_tenders(customer_inn):
    vdisplay = Xvfb()
    vdisplay.start()
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")
    driver = webdriver.Chrome('/usr/bin/chromedriver')
    # driver = webdriver.Chrome()
    driver.get("https://zakupki.gov.ru/")
    input_search = driver.find_element_by_id("quickSearchForm_header_searchString")
    input_search.click()
    input_search.send_keys(customer_inn)
    time.sleep(0.5)
    input_search.submit()
    time.sleep(random.randint(1, 3))
    number = int(''.join(re.findall(r'\d+', driver.find_element_by_class_name("search-results__total").text)))
    print(number)
    tenders = []
    # Запускаем цикл сбора информации, которую затем преобразовавыем в формат json и складываем в переменную tenders
    try:
        while True:
            time.sleep(0.5)
            page = driver.page_source
            tenders_list = parsing_data(page, customer_inn)
            tenders.extend(tenders_list)
            time.sleep(0.5)
            button_next = driver.find_element_by_class_name("paginator-button-next")
            driver.execute_script("arguments[0].click();", button_next)
            time.sleep(random.randint(1, 3))

    # Если в блоке пагинации нет элемента "next page" значит мы дошли до конца списка
    except NoSuchElementException:
        if len(tenders) == 0:
            print(f"У клиента с ИНН {customer_inn} нет закупок.\n")
            driver.close()
            vdisplay.stop()
            return False
        elif len(tenders) >= number*0.99 or len(tenders) == 1000:
            print(f"Загрузка торгов по ИНН {customer_inn} завершена успешно.")
            driver.close()
            vdisplay.stop()
            for tender in tenders:
                # Идем циклом по тендерам и вставляем в СУБД
                sql_requests.insert_into_tendersapp_tender(tender)
            return True
        elif len(tenders) < number*0.99:
            driver.close()
            vdisplay.stop()
            print(f"Во время загрузки торгов по ИНН {customer_inn} часть данных была потеряна.\n"
                  f"Объявлено торгов: {number}, загружено торгов: {len(tenders)}\n")
            download_tenders(customer_inn)
            return True
        else:
            driver.close()
            print(f"Что-то пошло не так во время загрузки тендеров клиента с ИНН {customer_inn}")
            return False
    except:
        print("Неизвестная ошибка при загрузке тендеров")
        return False

# ================================== ЗАГРУЗКА ПЛАН-ГРАФИКОВ ==================================


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
        plans_list = parsing_plans(page, customer_inn)
        print(type(plans_list))
        plans.extend(plans_list)
        # Запускаем цикл сбора информации, которую затем преобразовавыем в формат json и складываем в переменную tenders
        try:
            while True:
                time.sleep(random.randint(1, 2))
                button_next = driver.find_element_by_class_name("paginator-button-next")
                driver.execute_script("arguments[0].click();", button_next)
                time.sleep(random.randint(1, 2))
                page = driver.page_source
                plans_list = parsing_plans(page, customer_inn)
                plans.extend(plans_list)
        # Если в блоке пагинации нет элемента "next page" значит мы дошли до конца списка
        except NoSuchElementException:
            print(f"{customer_inn} finished normally")
        # Вызвать сообщение если возникнет какая-то другая ошибка
        except IndexError as e:
            print(f"{customer_inn} raised exception {e}")
    except NoSuchElementException as e:
        print(e)
    for plan in plans:
        sql_requests.insert_into_tendersapp_plan(plan)


def parsing_plans(page, customer_inn):
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


# ================================== ЗАГРУЗКА ЮРЛИЦ ИЗ DADATA API ==================================


def find_customer(company_inn):
    post = f"https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f"Token {config.API_KEY}"
    }
    data = {
        'query': f"{company_inn}"
    }
    res = requests.post(post, headers=headers, json=data)
    response = res.json()["suggestions"][0]
    district = response["data"]["address"]["data"]["federal_district"]
    if district == 'Центральный':
        district_id = 91
    elif district == 'Южный':
        district_id = 92
    elif district == 'Северо-Западный':
        district_id = 93
    elif district == 'Дальневосточный':
        district_id = 94
    elif district == 'Сибирский':
        district_id = 95
    elif district == 'Уральский':
        district_id = 96
    elif district == 'Приволжский':
        district_id = 97
    elif district == 'Северо-Кавказский':
        district_id = 98
    else:
        district_id = 91
    valid_data = {
        "model": "projectsapp.customer",
        "pk": str(response["data"]["ogrn"]),
        "fields": {
            "title": response["value"],
            "fullname": response["data"]["name"]["full_with_opf"],
            "management": response["data"]["management"]["post"] if response["data"]["management"] else None,
            "name": response["data"]["management"]["name"] if response["data"]["management"] else None,
            "inn": response["data"]["inn"],
            "kpp": response["data"]["kpp"],
            "okved": response["data"]["okved"],
            "form_code": response["data"]["opf"]["code"] if response["data"]["opf"] else None,
            "form_title": response["data"]["opf"]["full"] if response["data"]["opf"] else None,
            "address": response["data"]["address"]["unrestricted_value"],
            "district_id": district_id
        }
    }
    print(valid_data)
    sql_requests.insert_into_projectsapp_customer(valid_data)
    return valid_data

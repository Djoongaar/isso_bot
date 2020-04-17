import json
import os
import re

from bs4 import BeautifulSoup
import time
from datetime import datetime

from selenium import webdriver


def timekeeper(function_to_decorate):
    def wrapper(arg):
        start_time = datetime.now()
        function_to_decorate(arg)
        result = datetime.now() - start_time
        print(f"Время выполнения {function_to_decorate.__name__}: {result}")
    return wrapper


def parsing_data(file, customer_inn):
    tenders = []
    soup = BeautifulSoup(file)
    numbers = soup.find_all("div", class_="registry-entry__header-mid__number")
    start_prices = soup.find_all("div", class_="price-block__value")
    dates = soup.find_all("div", class_="data-block mt-auto")
    statuses = soup.find_all("div", class_="registry-entry__header-mid__title")
    names = soup.find_all("div", class_="registry-entry__body-value")
    for i in range(len(numbers)):
        updated = "-".join(re.findall(r'\d+', dates[i].findChildren()[4].text))
        if updated == '16-04-2020':  # datetime.now().strftime('%d-%b-%Y'):
            tenders.append({
                "model": "tendersapp.tender",
                "pk": numbers[i].text.strip()[2:],
                "fields": {
                    "start_price": int(''.join(re.findall(r'\d+', start_prices[i].text))) / 100,
                    "created": "-".join(re.findall(r'\d+', dates[i].findChildren()[1].text)),
                    "updated": updated,
                    "status": statuses[i].text.strip(),
                    "name": names[i].text.strip(),
                    "customer_inn": str(customer_inn)
                }
            })
    return tenders if len(tenders) > 0 else None


@timekeeper
def download_tenders(customer_inn):
    path = f"./tenders/{str(customer_inn)}/{datetime.now().strftime('%d-%b-%Y')}"

    if not os.path.exists(path):
        # Если такой директории нет значит эту компанию сегодня еще не парсили или парсили без результатов
        driver = webdriver.Chrome()
        driver.get("https://zakupki.gov.ru/")
        input_search = driver.find_element_by_id("quickSearchForm_header_searchString")
        input_search.click()
        input_search.send_keys(customer_inn)
        input_search.submit()
        page_number = 1
        os.makedirs(path)
        time.sleep(0.5)
        try:
            while page_number <= 2:
                page = driver.page_source
                data = parsing_data(page, customer_inn)
                if data:
                    with open(f"{path}/page_{str(page_number)}.json", "w", encoding="utf-8") as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                button_next = driver.find_element_by_class_name("paginator-button-next")
                driver.execute_script("arguments[0].click();", button_next)
                time.sleep(0.5)
                page_number += 1
        # Вызвать сообщение если возникнет исключение
        except:
            print(f"{customer_inn} raised exception")
    else:
        # А иначе выдаем юзеру уже имеющиеся данные c API www.isso.su
        pass


if __name__ == '__main__':
    download_tenders('7722765428')

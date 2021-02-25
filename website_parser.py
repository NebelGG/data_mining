import os
import json
import time
import datetime
from abc import ABC, abstractmethod
import requests
import bs4
from urllib.parse import urljoin
import pymongo

PERIODS = {
    "янв": (1, 2021),
    "фев": (2, 2021),
    "мар": (3, 2021),
    "апр": (4, 2021),
    "мая": (5, 2021),
    "июн": (6, 2021),
    "июл": (7, 2020),
    "авг": (8, 2020),
    "сен": (9, 2020),
    "окт": (10, 2020),
    "ноя": (11, 2020),
    "дек": (12, 2020),
}
class WebsiteParser(ABC):
    '''
    Абстрактный класс для парсера вебсайтов
    '''

    def __init__(self, start_url):
        self.start_url = start_url

        self.headers = {
            "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0", }
        self.result = []
        self.result_index = []
        self.finished = False
        self.maximum_attemts = 10

    def launch_parsing(self):
        '''
        Запускает процесс чтения и обработки данных.
        '''
        attempts = 0

        while True:
            # выполнять чтение и парсинг до тех пор, пока данные не будут прочитаны
            # или количество попыток превысит максимальное значение
            attempts += 1
            self.parse()
            if self.finished or attempts >= self.maximum_attemts:
                break
            else:
                time.sleep(1)
                continue


    @abstractmethod
    def parse(self):
        '''
        Разбор полученных данных.
        Каждый подкласс должен обязательно описать этот метод
        '''
        pass


    @abstractmethod
    def save_result(self):
        '''
        Сохраняет полученный результат.
        Каждый подкласс должен обязательно описать этот метод
        '''
        pass


class WebsiteParser_5ka_ToFile(WebsiteParser):

    def __init__(self, start_url):
        self.params = {
            'records_per_page': 100,
        }
        super(WebsiteParser_5ka_ToFile, self).__init__(start_url)

    def parse(self):
        current_url = self.start_url
        params = self.params
        while current_url:
            response: requests.Response = requests.get(current_url, params=params, headers=self.headers)
            if response.status_code != 200:
                break

            data = response.json()

            for product in data.get('results', []):
                prod_id = product.get('id', '')

                # Добавление происходит только в том случае, если в индексе такого номера нет
                if prod_id not in self.result_index:
                    try:
                        self.result.append(product)
                    except AttributeError:
                        pass
                    else:
                        # При удачном добавлении нового элемента в результат, добавляем id в индекс,
                        # чтобы в случае повторного чтения при сбое не добавить дубль.986\
                        self.result_index.append(prod_id)

            current_url = data.get('next')
            if params:
                params = {}

        if not current_url:
            self.finished = True


    def save_result(self):
        '''
        Сохраняет полученный результат.
        '''
        with open(f'data/result.json', 'w', encoding='UTF-8') as file:
            json.dump(self.result, file, ensure_ascii=False)


class WebsiteParser_Magnit_ToMongoDB(WebsiteParser):

    def __init__(self, start_url):
        mongo_client = pymongo.MongoClient(os.getenv('DATA_BASE'))
        self.db = mongo_client['parse_11']

        super(WebsiteParser_Magnit_ToMongoDB, self).__init__(start_url)

    def get_data(self):
        response = requests.get(self.start_url)
        if response.status_code != 200:
            result = None
        else:
            result = bs4.BeautifulSoup(response.text, 'lxml')

        return result

    def parse_soup_src(self, soup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.findChildren('a'):
            try:
                date_from, date_to = parse_date(product.find('div', attrs={'class': 'card-sale__date'}).text)
                pr_data = {
                    'url': urljoin(self.start_url, product.attrs.get('href')),
                    # 'name': product.find('div', attrs={'class': 'card-sale__title'}).text,
                    'promo_name': product.find('div', attrs={'class': 'card-sale__header'}).text,
                    'product_name': str(product.find('div', attrs={'class': 'card-sale__title'}).text),
                    'old_price': float(
                        '.'.join(itm for itm in product.find('div', attrs={'class': 'label__price_old'}).text.split())),
                    'new_price': float(
                        '.'.join(itm for itm in product.find('div', attrs={'class': 'label__price_new'}).text.split())),
                    'image_url': urljoin(self.start_url, product.find('img').attrs.get('data-src')),
                    'date_from': date_from,
                    'date_to': date_to,
                }
                yield pr_data
            except AttributeError:
                continue

    def parse(self):
        try:
            soup = self.get_data()
            for product in self.parse_soup_src(soup):
                self.save_result(product)
        except IndentationError:
            pass
        else:
            self.finished = True

    def save_result(self, product):
        '''
        Сохраняет полученный результат.
        '''
        # print(product)
        collection = self.db['magnit']
        collection.insert_one(product)

    @staticmethod
    def parse_date(date_template):
        list_of_elemens = date_template.split()
        date_from = datetime.datetime(year=PERIODS[list_of_elemens[2][:3]][1], day=int(list_of_elemens[1]), month=PERIODS[list_of_elemens[2][:3]][0])
        date_to = datetime.datetime(year=PERIODS[list_of_elemens[5][:3]][1], day=int(list_of_elemens[4]), month=PERIODS[list_of_elemens[5][:3]][0])
        return date_from, date_to

if __name__ == '__main__':
    # parser = WebsiteParser_5ka_ToFile('https://5ka.ru/api/v2/special_offers/')
    # parser.launch_parsing()
    # parser.save_result()

    parser = WebsiteParser_Magnit_ToMongoDB('https://magnit.ru/promo/?geo=moskva')
    parser.launch_parsing()
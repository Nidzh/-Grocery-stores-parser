import json

import requests
from bs4 import BeautifulSoup as BS
from loguru import logger

URL = 'https://www.vprok.ru/catalog/'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    'accept': '*/*'}
HOST = 'https://www.vprok.ru'
category_links = []
good_links = []
all_goods = []
logger.add('debug_vprok.log', format='{time} {level} {message}', encoding='UTF-8')
dict_product = {}


@logger.catch()
def get_category_link(url):
    html = requests.get(url, headers=HEADERS)
    soup = BS(html.text, 'lxml')

    for href in soup.findAll('li', class_='xf-catalog-categories__item'):
        category_links.append(HOST + href.find('a').get('href'))

    logger.success(f"Ссылки на категории собраны. Кол-вы ссылок: {len(category_links)}")


@logger.catch()
def get_products_link(url):
    logger.info(url)
    html = requests.get(url, headers=HEADERS)
    soup = BS(html.text, 'lxml')
    count = int(soup.find('span', class_='js-list-total__total-count').text)
    page_count = count // 30 + 1
    logger.info(f"Кол-во страниц пагинации: {page_count}")

    for i in range(1, page_count + 1):
        get_content_links(url, i)


@logger.catch()
def get_content_links(url, i):
    html = requests.get(url + f'?attr%5Brate%5D%5B%5D=0&page={i}&sort=rate_desc', headers=HEADERS)
    soup = BS(html.text, 'lxml')
    for link in soup.findAll('a', class_='xf-product__main-link'):
        good_links.append(HOST + link.get('href'))
        logger.info(f"Ссылка на товар добавлена. {link.get('href')}")
    logger.debug(f"Страница пагинации № {i} спарсена.")


@logger.catch()
def get_content(url):
    html = requests.get(url, headers=HEADERS)
    soup = BS(html.text, 'lxml')
    logger.debug(url)

    if html.status_code == 200:

        try:
            name = soup.find('h1', class_='xf-product-new__title js-product__title js-product-new-title').text.strip()
        except:
            name = 'Без имени'
            logger.error("Не обнаржуено ИМЯ !")

        try:
            composition = soup.find('div', class_='xf-product-new-about-section__property__value-content '
                                                  'js-product-new-about-property-composition-value').text.strip()
        except:
            composition = 'Нет состава'
            logger.error("Не обнаржуен СОСТАВ !")

        dict_product[name] = composition
        logger.success(f"Товар добавлен в словарь.")


if __name__ == "__main__":
    get_category_link(URL)

    for link in category_links:
        get_products_link(link)

    for link in good_links:
        get_content(link)

    with open('vprok.json', 'w', encoding='utf-8') as file:
        json.dump(dict_product, file, ensure_ascii=False, indent=4)

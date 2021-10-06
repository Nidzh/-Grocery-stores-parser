import json
import time

import requests
from bs4 import BeautifulSoup
from loguru import logger

URL = 'https://vkusvill.ru'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                         '92.0.4515.159 Safari/537.36', 'accept': '*/*'}
category_links = []
good_links = []
collected_dict = {}
startwith = 0
start_time = time.time()
logger.add('debug_vkusvill.log', format='{time} {level} {message}', encoding='UTF-8')


@logger.catch()
def get_category_links():
    html = requests.get(URL + '/goods', headers=HEADERS)
    soup = BeautifulSoup(html.text, 'lxml')
    for item in soup.find_all('a', class_='VVCategCards2020__Item'):
        category_links.append(item.get('href'))
    category_links.remove('/ratsiony-na-kazhdyy-den/')
    category_links.remove('/tort/')
    logger.success(f"Список категорий получен. Кол-во категорий: {len(category_links)}.")


@logger.catch()
def get_goods_links(link):
    html = requests.get(URL + link, headers=HEADERS)
    soup = BeautifulSoup(html.text, 'lxml')
    goods_count = int(soup.find('input', class_='js-catalog-page-params').get('value'))
    page_count = goods_count // 24 + 1

    for i in range(1, page_count + 1):
        add_link = f'?PAGEN_1={i}'
        html = requests.get(URL + link + add_link, headers=HEADERS)
        soup = BeautifulSoup(html.text, 'lxml')

        for item in soup.find_all('a', class_='ProductCard__link js-datalayer-catalog-list-name'):
            good_links.append(item.get('href'))
            logger.info(f"Ссылка на товар получена. Кол-во ссылок: {len(good_links)}.")

    logger.success(f"Все товары получены. Кол-во ссылок: {len(good_links)}")


@logger.catch()
def get_goods_content(link):
    html = requests.get(URL + link, headers=HEADERS)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'lxml')
        good_link = URL + link

        name = soup.find('div', class_='Product__headRow').text.strip()
        composition_not_format = soup.find('div', class_='Product__composition').findNext().text

        if "Состав: " in composition_not_format:
            composition = composition_not_format.split('Состав: ')[1].split('Информация на этикетке')[0].strip().split(
                'производится на предприятии, где используются')[0].strip().capitalize()
        else:
            composition = 'Нет состава в описании'

        collected_dict[name] = composition
        logger.info(f"Запись добавлена:{good_link}")


if __name__ == "__main__":
    get_category_links()

    for link in category_links:
        get_goods_links(link)

    for link in good_links:
        get_goods_content(link)
        startwith += 1
        logger.debug(f'Прогресс: {startwith}/{len(good_links)}')

    with open('vkusvill.json', 'w', encoding='utf-8') as f:
        json.dump(collected_dict, f, ensure_ascii=False, indent=4)

    finish_time = time.time() - start_time
    logger.success(f"--- Программа выполнена. Потрачено времени: {finish_time} seconds ---")

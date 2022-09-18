from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
import time
import json
import asyncio
import aiohttp

headers = {
    
}


def has_next_pag(data):
    soup = BeautifulSoup(data, 'lxml')
    next_pag = None
    if soup.find('ul', class_='pagination').find(
        'li', class_='pagination__item'\
            ' pagination__item_arrow pagination__item_next'
    ):
        next_pag = soup.find('ul', class_='pagination').find(
            'li', class_='pagination__item pagination__item_arrow'\
                ' pagination__item_next').find(
                    'a', class_='pagination__link'
                ).get('href')
    return next_pag


def get_links(data):
    links = []
    soup = BeautifulSoup(data, 'lxml')
    items = soup.find_all('div', class_='product-card')
    for item in items:
        link = item.find('a', class_='product-card__link').get('href')
        links.append(f'https://brandshop.ru{link}')
    
    return links


product_data = {}

async def get_items(link, session, ind):
    async with session.get(
        url=link,
        headers={'user-agent': UserAgent().random},
        ssl=False
    ) as response:
        print(ind, link)
        print(headers)
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')
        desc = soup.find('div', class_='product-page__header-top').\
            text.strip().split('\n')
        description = '\n'.join([
            name.strip() for name in desc if name.strip()
        ])
        old_price = soup.find('span', class_='product-order__price_old').\
            text.strip()
        new_price = soup.find('div', class_='product-order__price_new').\
            text.strip()
        discount = soup.find('span', class_='product-order__price-discount').\
            text.strip()
        main_data = soup.find_all('div', class_='product-data__name font_m')
        articul = main_data[0].text
        product_code = int(main_data[1].text)
        product_data[product_code] = {
        'articul': articul,
        'description': description,
        'url': link,
        'old_price': old_price,
        'new_price': new_price,
        'discount': discount,
        }
        print(f'Item number {ind} {len(product_data)} items DOWNLOADED')
        return product_data


async def get_all_links(url, session):
    all_links = []
    async def walk(next_pag):
        async with session.get(
            url=f'{url}{next_pag}',
            headers=headers,
            ssl=False
        ) as response:
            response_text = await response.text()
            page_links = get_links(response_text)
            all_links.extend(page_links)
            new_pag = has_next_pag(response_text)
            if new_pag:
                await walk(new_pag)
    await walk('?page=1')
    print('ALL LINKS', len(all_links))
    print('ALL LINKS SET', len(set(all_links)))
    return set(all_links)
    

async def get_all_items(url):
    conn = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=conn) as session:
        all_links = await get_all_links(url, session)
        tasks = []
        for ind, link in enumerate(all_links):
            task = asyncio.create_task(get_items(link, session, ind))
            tasks.append(task)
        await asyncio.gather(*tasks)
    
    today_items = datetime.strftime(datetime.now(), '%Y_%m_%d')
    with open(f'data/{today_items}_items_data.json', 'w') as file:
        json.dump(product_data, file, indent=4, ensure_ascii=False)

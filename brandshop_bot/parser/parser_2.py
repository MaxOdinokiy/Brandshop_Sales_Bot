from fake_useragent import UserAgent
from math import ceil
from datetime import datetime
import asyncio
import aiohttp
import json

products_data = {}


async def get_api_data(url, session):
    async with session.get(
            url=url,
            headers={
                'user-agent': UserAgent().random,
                'accept': 'application/json, text/plain, */*'
            },
            ssl=False) as response:
        return await response.json()


async def get_pages_count(url, session):
    api_data = await get_api_data(url, session)
    items_count = api_data.get('pagination').get('totalProduct')
    limit = api_data.get('pagination').get('currentLimit')
    pages_count = ceil(items_count / limit)
    return pages_count


async def get_items(url, session):
    api_data = await get_api_data(url, session)
    products = api_data.get('products')
    for item in products:
        item_artucul = item.get('sku')
        item_id = item.get('productId')
        item_key = '/'.join([str(item_id), item_artucul])
        item_name = item.get('productName').get('fullName')
        item_url = f"https://brandshop.ru{item.get('url')}"
        old_price = item.get('price').get('price')
        new_price = item.get('price').get('discount')
        discount = item.get('price').get('discountPercent')
        sizes = [size.get('name') for size in item.get('size')]
        products_data[item_key] = {
            'name': item_name,
            'url': item_url,
            'old_price': old_price,
            'new_price': new_price,
            'discount': discount,
            'sizes': ', '.join(sizes)
        }


async def get_all_items():
    API_URL = 'https://api.brandshop.ru/xhr/catalog/?url=%2Fsale%2F'
    conn = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=conn) as session:
        pages_count = await get_pages_count(API_URL, session)
        tasks = []
        for i in range(1, pages_count + 1):
            task = asyncio.create_task(get_items(f'{API_URL}&page={i}', session)) # noqa
            tasks.append(task)
        await asyncio.gather(*tasks)

    today_items = datetime.strftime(datetime.now(), '%Y_%m_%d')
    print(len(products_data))
    with open(f'brandshop_bot/data/{today_items}_items_data.json', 'w') as file: # noqa
        json.dump(products_data, file, indent=4, ensure_ascii=False)


def main():
    asyncio.run(get_all_items())


if __name__ == '__main__':
    main()

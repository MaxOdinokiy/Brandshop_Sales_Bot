from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import json

URL = 'https://brandshop.ru/sale/'

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36'
}

product_data = {}

def get_data(url):
    response = requests.get(url=url, headers=headers)
    with open('first_request.html', 'w') as f:
        f.write(response.text)


def get_soup(data):
    start_time = datetime.now()
    count = 0
    soup = BeautifulSoup(data, 'lxml')
    items = soup.find_all('div', class_='product-card')
    for item in items:
        link = item.find('a', class_='product-card__link').get('href')
        url = f'https://brandshop.ru{link}'
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        desc = soup.find('div', class_='product-page__header-top').text.strip().split('\n')
        description = '\n'.join([name.strip() for name in desc if name.strip()])
        old_price = soup.find('span', class_='product-order__price_old').text.strip()
        new_price = soup.find('div', class_='product-order__price_new').text.strip()
        discount = soup.find('span', class_='product-order__price-discount').text.strip()
        main_data = soup.find_all('div', class_='product-data__name font_m')
        articul = main_data[0].text
        product_code = int(main_data[1].text)
        product_data[product_code] = {
            'articul': articul,
            'description': description,
            'url': url,
            'old_price': old_price,
            'new_price': new_price,
            'discount': discount,
        }
        count += 1
        time.sleep(5)
        print(f'!!! {count} item downloaded')
    print(datetime.now() - start_time)
    return product_data


with open('first_request.html', 'r') as f:
    data = f.read()


with open('product_data.json', 'w') as f:
    json.dump(get_soup(data), f, ensure_ascii=False, indent=4)



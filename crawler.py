import time

import requests
from bs4 import BeautifulSoup

CONST_URL = "https://guide.michelin.com/en/it/restaurants"

def get_html(url):
    response = requests.get(url)
    response.raise_for_status()  # проверка на ошибки
    return response.content


r = requests.get(CONST_URL)
soup = BeautifulSoup(r.content, "html.parser")

restaurant_urls = []
page = 1

last_page_link = soup.select(
    "div.js-restaurant__bottom-pagination ul.pagination a.btn.btn-outline-secondary.btn-sm")
max_pages = int(last_page_link[-2].get_text().strip())

print(max_pages)

while page <= max_pages:
    print("Number", page)
    url = f"{CONST_URL}/page/{page}"
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    print(url)

    restaurant_list = soup.select("div.row.restaurant__list-row.js-restaurant__list_items a.link")

    if not restaurant_list:
        break

    for link in restaurant_list:
        restaurant_url = link["href"]
        if restaurant_url:
            full_url = f"https://guide.michelin.com{restaurant_url}"
            restaurant_urls.append(full_url)

    page += 1
    time.sleep(1)

print(len(set(restaurant_urls)))
with open('restaurant_urls.txt', 'w') as f:
    for url in restaurant_urls:
        f.write(url + "\n")

print(f"Saved {len(restaurant_urls)} URL into restaurant_urls.txt")

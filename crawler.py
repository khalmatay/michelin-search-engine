import time
from typing import List

import requests
from bs4 import BeautifulSoup

CONST_URL = "https://guide.michelin.com/en/it/restaurants"


def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def get_number_of_max_pages() -> int:
    html = get_html(CONST_URL)
    soup = BeautifulSoup(html, "html.parser")
    last_page_link = soup.select(
        "div.js-restaurant__bottom-pagination ul.pagination a.btn.btn-outline-secondary.btn-sm")
    max_pages = int(last_page_link[-2].get_text().strip())
    return max_pages


def get_restaurant_urls(max_pages) -> List[str]:
    restaurant_urls = []
    page = 1
    while page <= max_pages:
        url = f"{CONST_URL}/page/{page}"
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")

        print(page, url)

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
    print("Unique restaurant urls", len(set(restaurant_urls)))
    return restaurant_urls


def save_urls_to_file(restaurant_urls) -> None:
    with open('restaurant_urls.txt', 'w') as f:
        for url in restaurant_urls:
            f.write(url + "\n")
    print(f"Saved {len(restaurant_urls)} URL into restaurant_urls.txt")


def crawler():
    max_pages = get_number_of_max_pages()
    restaurant_urls = get_restaurant_urls(max_pages)
    save_urls_to_file(restaurant_urls)


if __name__ == "__main__":
    crawler()

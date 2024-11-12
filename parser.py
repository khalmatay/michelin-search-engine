import os

import pandas as pd
from bs4 import BeautifulSoup


def get_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    restaurant_name = soup.find("h1", class_="data-sheet__title").get_text(strip=True)
    blocks = soup.find_all("div", class_="data-sheet__block--text")

    if len(blocks) >= 2:
        text_address_city_code_country = blocks[0].get_text(strip=True).split(",")
        address = text_address_city_code_country[0] if len(text_address_city_code_country) > 0 else None
        city = text_address_city_code_country[1] if len(text_address_city_code_country) > 1 else None
        postal_code = text_address_city_code_country[2] if len(text_address_city_code_country) > 2 else None
        country = text_address_city_code_country[-1] if len(text_address_city_code_country) > 3 else None

        text_price_cuisine = blocks[1].get_text(separator=" ", strip=True).replace("·", "").split()
        price_range = text_price_cuisine[0] if text_price_cuisine else None
        cuisine_type = " ".join(text_price_cuisine[1:]) if len(text_price_cuisine) > 1 else None
    else:
        address = city = postal_code = country = price_range = cuisine_type = None

    description = soup.find("div", class_="data-sheet__description").get_text(strip=True)

    facilities_section = soup.find("div", class_="restaurant-details__services")
    facilities_services = [item.get_text(strip=True) for item in facilities_section.find_all("li")]

    credit_cards_section = soup.find("div", class_="list--card")
    credit_cards = []
    if credit_cards_section:
        credit_cards_images = [img["data-src"] for img in credit_cards_section.find_all("img")]
        credit_cards = [card.split("-")[0] for card in [el.split("/")[-1] for el in credit_cards_images]]

    phone_number = soup.find("span", class_="flex-fill").get_text(strip=True)

    website_div = soup.find("div", class_="collapse__block-item link-item")
    website = website_div.find("a")["href"] if website_div and website_div.find("a") else None

    restaurant_data = {
        "restaurantName": restaurant_name,
        "address": address,
        "city": city,  # Заполните на основе адреса, если возможно
        "postalCode": postal_code,  # Заполните на основе адреса, если возможно
        "country": country,  # Заполните на основе адреса, если возможно
        "priceRange": price_range,
        "cuisineType": cuisine_type,
        "description": description,
        "facilitiesServices": facilities_services,
        "creditCards": credit_cards,
        "phoneNumber": phone_number,
        "website": website
    }

    return restaurant_data


def main():
    columns = [
        "restaurantName", "address", "city", "postalCode", "country",
        "priceRange", "cuisineType", "description", "facilitiesServices",
        "creditCards", "phoneNumber", "website"
    ]
    restaurant_data_list = []
    count = 0
    data_folder = 'data'

    for page in os.listdir(data_folder):
        page_path = os.path.join(data_folder, page)
        for link in os.listdir(page_path):
            full_path = os.path.join(page_path, link)
            count += 1
            print(full_path, "Number " + str(count))
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()

            restaurant_data = get_data(content)
            restaurant_data_list.append(restaurant_data)

    restaurants_df = pd.DataFrame(restaurant_data_list, columns=columns)
    restaurants_df.to_csv("restaurants_i.tsv", index=False, encoding="utf-8", sep = "\t")


if __name__ == "__main__":
    main()

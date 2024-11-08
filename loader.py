import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def download_html(url, data_folder, folder_name, file_name):
    try:
        full_folder_path = os.path.join(data_folder, folder_name)
        os.makedirs(full_folder_path, exist_ok=True)
        file_path = os.path.join(full_folder_path, file_name)

        if os.path.exists(file_path):
            print(f"File is exists: {file_path}")
            return

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved: {file_path}")
    except Exception as e:
        print(f"Error with {url}: {e}")


def get_urls_file(restaurant_urls_file_name):
    urls = []
    with open(restaurant_urls_file_name) as my_file:
        for line in my_file:
            urls.append(line.strip())
    return urls


def main():
    restaurant_urls_file_name = 'restaurant_urls.txt'
    urls = get_urls_file(restaurant_urls_file_name)
    print(f"{len(urls)}")

    urls_per_page = 100
    max_workers = 10
    start_index = 0
    data_folder = 'data'

    os.makedirs(data_folder, exist_ok=True)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {}

        for idx, url in enumerate(urls[start_index:], start=start_index):
            page_number = idx // urls_per_page + 1
            folder_name = f"page{page_number}"
            file_name = f"restaurant_{idx + 1}.html"
            future = executor.submit(download_html, url, data_folder, folder_name, file_name)
            future_to_url[future] = url

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error with {url}: {e}")


if __name__ == "__main__":
    main()

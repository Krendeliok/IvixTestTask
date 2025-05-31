from time import sleep
from urllib import parse
import csv
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

html_url = "https://coinmarketcap.com/?"
api_url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=500&sortBy=rank&sortType=desc&convert=USD&cryptoType=all&tagType=all&audited=false&aux=cmc_rank"


def parse_percent_change_24_h(row: webdriver.remote.webelement.WebElement) -> str:
    value = row.find_element(By.XPATH, "td[6]").text
    sign_class = row.find_element(By.XPATH, "td[6]/span/span").get_attribute("class")
    if "down" in sign_class:
        return f"-{value}"
    return value


cols = {
    "Rank": lambda x: x.find_element(By.XPATH, "td[2]").text,
    "Name": lambda x: x.find_element(By.XPATH, "td[3]//span/div/div/p").text,
    "Symbol": lambda x: x.find_element(By.XPATH, "td[3]//span/div/div/div/p").text,
    "Price": lambda x: x.find_element(By.XPATH, "td[4]").text,
    "24h%Change": parse_percent_change_24_h,
    "MarketCap": lambda x: x.find_element(By.XPATH, "td[8]").text,
}


def write_to_file(data: list, filename="data.csv"):
    with open(filename, "w") as file:
        csv_writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL, delimiter=',', lineterminator='\n')
        csv_writer.writerow(cols.keys())
        csv_writer.writerows([row.values() for row in data])
    print(f"Data written to {filename}")


def parse_row(row: webdriver.remote.webelement.WebElement):
    return {
        col_name: col_func(row) for col_name, col_func in cols.items()
    }


def load_all_page_rows(driver: webdriver.remote.webdriver.WebDriver):
    footer = driver.find_element(By.CLASS_NAME, "table_footer-left")
    driver.execute_script(f"window.scrollTo({{ behavior: 'smooth', top: {int(footer.location['y'] / 2)}, left: 0}});")
    sleep(2)
    driver.execute_script(f"window.scrollTo({{ behavior: 'smooth', top: {int(footer.location['y'])}, left: 0}});")
    sleep(1)


def get_page_table_rows(driver: webdriver.remote.webdriver.WebDriver):
    load_all_page_rows(driver)
    return driver.find_elements(By.XPATH, "//table/tbody/tr")


def parse_page(driver: webdriver.remote.webdriver.WebDriver):
    return [parse_row(row) for row in get_page_table_rows(driver)]


def compact_number(n):
    if n >= 1_000_000_000_000:
        return f"{n / 1_000_000_000_000:.2f}T".rstrip('0').rstrip('.')
    elif n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B".rstrip('0').rstrip('.')
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M".rstrip('0').rstrip('.')
    elif n >= 1_000:
        return f"{n / 1_000:.2f}K".rstrip('0').rstrip('.')
    else:
        return str(n)


def prepare_data(data):
    return [
        {
            "Rank": item.get("cmcRank", ""),
            "Name": item.get("name", ""),
            "Symbol": item.get("symbol", ""),
            "Price": f"${item.get("quotes", [])[0].get("price", ""):,.5f}".rstrip('0').rstrip('.'),
            "24h%Change": f"{item.get("quotes", [])[0].get("percentChange24h", ""):.2f}%",
            "MarketCap": f"${compact_number(item.get("quotes", [])[0].get("marketCap", ""))}",
        }
        for item in data
    ]


def get_data_from_api():
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return prepare_data(data.get("data", {}).get("cryptoCurrencyList", []))
    else:
        print(f"Error fetching data from API: {response.status_code}")
        return []


def get_data_from_html():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    all_data = []
    for page in range(1, 6):
        url = html_url + parse.urlencode({"page": page})
        driver.get(url)
        print(f"Parsing page {page}...")
        all_data += parse_page(driver)
        print(f"Parsed {len(all_data)} rows so far...")
    driver.quit()
    return all_data


def main():
    all_data = get_data_from_api()
    write_to_file(all_data, "data_api.csv")


if __name__ == '__main__':
    main()

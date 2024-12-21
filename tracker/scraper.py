import requests
from bs4 import BeautifulSoup

def fetch_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_name = soup.find('h1', {'class': 'product-title'}).text
    price = float(soup.find('span', {'class': 'price'}).text.replace('$', ''))

    return product_name, price

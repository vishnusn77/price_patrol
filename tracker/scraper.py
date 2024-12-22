import aiohttp
import aiofiles
import os
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup

# Define rate limiter: 10 requests per minute
rate_limiter = AsyncLimiter(10, 60)

async def save_to_cache(html, file_path):
    """Save HTML response to a cache file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiofiles.open(file_path, mode="w", encoding="utf-8") as file:
        await file.write(html)

async def read_from_cache(file_path):
    """Read HTML response from a cache file."""
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as file:
        return await file.read()

async def fetch_html(url, headers, cache_path=None):
    """Fetch HTML from a URL, using cache if available."""
    if cache_path and os.path.exists(cache_path):
        return await read_from_cache(cache_path)

    async with rate_limiter:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                html = await response.text()
                if cache_path:
                    await save_to_cache(html, cache_path)
                return html

async def fetch_price(url, cache_path=None):
    """Fetch product name and price asynchronously."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    html = await fetch_html(url, headers, cache_path)
    soup = BeautifulSoup(html, 'html.parser')

    # Update the selectors to match the target site
    product_name = soup.find("span", {"id": "productTitle"})
    product_name = product_name.text.strip() if product_name else "Product not found"

    price_whole = soup.find("span", {"class": "a-price-whole"})
    price_fraction = soup.find("span", {"class": "a-price-fraction"})

    if price_whole and price_fraction:
        price = float(price_whole.text.replace(",", "") + "." + price_fraction.text)
    else:
        price = None

    return product_name, price

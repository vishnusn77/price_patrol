import aiohttp
import aiofiles
import os
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup
import hashlib

# Define rate limiter: 10 requests per minute
rate_limiter = AsyncLimiter(10, 60)

def get_cache_path(url, cache_dir="tracker/cache"):
    """
    Generate a valid cache path by hashing the URL.
    """
    # Hash the URL to create a unique filename
    hashed_url = hashlib.md5(url.encode()).hexdigest()
    sanitized_filename = f"{hashed_url}.html"

    # Ensure the cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    # Return the full cache path
    return os.path.join(cache_dir, sanitized_filename)
    print(f"Cache Path: {os.path.join(cache_dir, sanitized_filename)}")


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

async def fetch_price(url):
    """
    Fetch product name and price asynchronously with proper cache handling.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    # Get a safe cache path
    cache_path = get_cache_path(url)

    # Fetch HTML (use cache if available)
    html = await fetch_html(url, headers, cache_path)
    soup = BeautifulSoup(html, 'html.parser')

    # Extract product name
    product_name_tag = soup.find("span", {"id": "productTitle"})
    product_name = product_name_tag.text.strip() if product_name_tag else "Product Name Not Found"

    # Extract price details
    price_whole = soup.find("span", {"class": "a-price-whole"})
    price_fraction = soup.find("span", {"class": "a-price-fraction"})

    # Clean and parse price components
    def clean_price(value):
        if value:
            return value.replace(",", "").replace(".", "").strip()
        return "0"

    if price_whole and price_fraction:
        try:
            whole = clean_price(price_whole.text)
            fraction = clean_price(price_fraction.text)
            price = float(f"{whole}.{fraction}")
        except ValueError:
            price = None
    elif price_whole:  # If fractional part is missing
        try:
            whole = clean_price(price_whole.text)
            price = float(f"{whole}.0")
        except ValueError:
            price = None
    else:
        price = None

    return product_name, price







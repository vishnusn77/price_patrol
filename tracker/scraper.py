import aiohttp
import aiofiles
import os
import logging
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup
import hashlib

# Define rate limiter: 10 requests per minute
rate_limiter = AsyncLimiter(10, 60)

# Set up logging
logger = logging.getLogger("scraper_logger")

def get_cache_path(url, cache_dir="tracker/cache"):
    """
    Generate a valid cache path by hashing the URL.
    """
    try:
        hashed_url = hashlib.md5(url.encode()).hexdigest()
        sanitized_filename = f"{hashed_url}.html"
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, sanitized_filename)
    except Exception as e:
        logger.error(f"Error generating cache path for URL {url}: {e}")
        raise

async def save_to_cache(html, file_path):
    """Save HTML response to a cache file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as file:
            await file.write(html)
    except Exception as e:
        logger.error(f"Error saving HTML to cache at {file_path}: {e}")

async def read_from_cache(file_path):
    """Read HTML response from a cache file."""
    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as file:
            return await file.read()
    except Exception as e:
        logger.error(f"Error reading HTML from cache at {file_path}: {e}")
        return None

async def fetch_html(url, headers, cache_path=None):
    """Fetch HTML from a URL, using cache if available."""
    try:
        if cache_path and os.path.exists(cache_path):
            logger.info(f"Cache hit for URL: {url}")
            return await read_from_cache(cache_path)

        async with rate_limiter:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    html = await response.text()
                    if cache_path:
                        await save_to_cache(html, cache_path)
                    return html
    except Exception as e:
        logger.error(f"Error fetching HTML for URL {url}: {e}")
        return None

async def fetch_price(url):
    """
    Fetch product name and price asynchronously with proper cache handling.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        logger.info(f"Fetching price for URL: {url}")
        
        cache_path = get_cache_path(url)
        html = await fetch_html(url, headers, cache_path)
        
        if html is None:
            logger.warning(f"Failed to fetch or cache HTML for URL: {url}")
            return "Product Name Not Found", None

        soup = BeautifulSoup(html, 'html.parser')

        # Extract product name
        product_name_tag = soup.find("span", {"id": "productTitle"})
        product_name = product_name_tag.text.strip() if product_name_tag else "Product Name Not Found"
        
        logger.info(f"Product name fetched: {product_name}")

        # Extract price details
        price_whole = soup.find("span", {"class": "a-price-whole"})
        price_fraction = soup.find("span", {"class": "a-price-fraction"})

        def clean_price(value):
            if value:
                return value.replace(",", "").replace(".", "").strip()
            return "0"

        price = None  # Default value for price
        if price_whole and price_fraction:
            try:
                whole = clean_price(price_whole.text)
                fraction = clean_price(price_fraction.text)
                price = float(f"{whole}.{fraction}")
                logger.info(f"Price fetched successfully: {price}")
            except ValueError as e:
                logger.error(f"ValueError while parsing price for URL {url}: {e}")
        elif price_whole:
            try:
                whole = clean_price(price_whole.text)
                price = float(f"{whole}.0")
                logger.info(f"Whole price fetched successfully: {price}")
            except ValueError as e:
                logger.error(f"ValueError while parsing whole price for URL {url}: {e}")
        else:
            logger.warning(f"Price not found for URL {url}")

        logger.info(f"Returning product name: {product_name} and price: {price}")
        return product_name, price

    except Exception as e:
        logger.error(f"Critical error in fetch_price for URL {url}: {e}")
        return "Product Name Not Found", None

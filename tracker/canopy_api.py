import requests
from decouple import config
from tracker.models import APIUsage
import logging

CANOPY_API_URL = "https://graphql.canopyapi.co"
logger = logging.getLogger('cron_logger')


async def fetch_amazon_product_data(url):
    """
    Fetch product data from Canopy API using the provided Amazon product URL.
    """
    api_key = config("CANOPY_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    query = """
    query amazonProduct($url: String!) {
        amazonProduct(input: { urlLookup: { url: $url } }) {
            title
            brand
            mainImageUrl
            ratingsTotal
            rating
            price {
                display
            }
        }
    }
    """
    variables = {"url": url}

    # Check API usage before making the request
    if not await APIUsage.increment():
        raise RuntimeError("API usage limit reached. Skipping request.")

    try:
        response = requests.post(
            CANOPY_API_URL,
            json={"query": query, "variables": variables},
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        product_data = data.get("data", {}).get("amazonProduct", None)
        if product_data:
            return product_data
        else:
            raise ValueError("No product data returned from Canopy API.")
    except Exception as e:
        logger.error(f"Failed to fetch product data: {e}")
        raise RuntimeError(f"Failed to fetch product data: {e}")

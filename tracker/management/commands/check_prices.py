import asyncio
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from tracker.models import Product
from tracker.tasks import send_price_drop_email
from tracker.canopy_api import fetch_amazon_product_data
import logging

logger = logging.getLogger('cron_logger')  # Use the dedicated cron logger


class Command(BaseCommand):
    help = 'Check product prices and notify users of price drops'

    def handle(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.check_prices())
        finally:
            loop.close()

    async def check_prices(self):
        products = await sync_to_async(list)(Product.objects.all())

        for product in products:
            try:
                # Fetch product data (directly calling the sync function)
                product_data = await fetch_amazon_product_data(product.url)  # No sync_to_async needed
                logger.info(f"Fetched product data: {product_data}")

                if not product_data or 'price' not in product_data or not product_data['price']:
                    logger.warning(f"Failed to fetch price for URL: {product.url}")
                    continue

                # Extract the price from the 'display' key
                price_display = product_data['price'].get('display')
                if not price_display:
                    logger.warning(f"No display price found for {product.name}. Skipping...")
                    continue

                # Clean and convert the price to a float
                current_price = float(price_display.replace('$', '').replace(',', ''))
                logger.info(f"Fetched price for {product.name}: {current_price}")

                # Convert last_notified_price to float if it exists
                last_notified_price = (
                    float(product.last_notified_price.to_decimal())  # Convert Decimal128 to float
                    if product.last_notified_price is not None
                    else None
                )

                # Check if an email was already sent for this price
                if last_notified_price is not None and last_notified_price == current_price:
                    logger.info(f"Email already sent for {product.name} at price {current_price}. Skipping...")
                    continue

                if current_price <= product.desired_price:
                    send_price_drop_email(product, current_price)
                    product.last_notified_price = current_price  # Record the notified price
                    product.current_price = current_price  # Update current price
                    await sync_to_async(product.save)()
                    logger.info(f"Email sent for {product.name} to {product.user_email}")
                else:
                    # Update current price if no email is sent
                    product.current_price = current_price
                    await sync_to_async(product.save)()
                    logger.info(f"No price drop for {product.name}. Updated current price.")

            except Exception as e:
                logger.error(f"Error checking price for {product.name}: {e}")

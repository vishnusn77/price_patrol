import asyncio
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from tracker.models import Product
from tracker.tasks import send_price_drop_email
from tracker.scraper import fetch_price  # Your asynchronous price-fetching logic

class Command(BaseCommand):
    help = 'Check product prices and notify users of price drops'

    def handle(self, *args, **kwargs):
        # Run the price-checking logic in an event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._check_prices())

    async def _check_prices(self):
        # Fetch products asynchronously
        products = await sync_to_async(list)(Product.objects.all())  # Convert QuerySet to a list asynchronously

        for product in products:
            try:
                # Fetch the current price using the scraper
                product_name, current_price = await fetch_price(product.url)  # Fetch name and price using async function

                if current_price is None:
                    self.stdout.write(f"Could not fetch price for {product.name}. Skipping...")
                    continue

                # Convert last_notified_price to float if it exists
                last_notified_price = (
                    float(product.last_notified_price.to_decimal()) 
                    if product.last_notified_price else None
                )

                # Check if the email has already been sent for this price
                if last_notified_price is not None and last_notified_price == current_price:
                    self.stdout.write(f"Email already sent for {product.name} at price {current_price}. Skipping...")
                    continue

                # Send email if the price is below or equal to the desired price
                if current_price <= product.desired_price:
                    send_price_drop_email(product, current_price)
                    product.last_notified_price = current_price  # Update the notified price
                    await sync_to_async(product.save)()  # Save the updated product
                    self.stdout.write(f"Email sent for {product.name} to {product.user_email}")
                else:
                    self.stdout.write(f"No price drop for {product.name}")

            except Exception as e:
                self.stdout.write(f"Error checking price for {product.name}: {e}")

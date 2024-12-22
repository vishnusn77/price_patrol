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
            current_price = await fetch_price(product.url)  # Fetch price using your asynchronous function

            # Debug statement to inspect the value returned by fetch_price
            print(f"Fetched price for {product.name}: {current_price} ({type(current_price)})")

            if current_price is None:
                self.stdout.write(f"Could not fetch price for {product.name}. Skipping...")
                continue

            if isinstance(current_price, (tuple, list)):
                self.stdout.write(f"Unexpected return type from fetch_price for {product.name}. Skipping...")
                continue

            if current_price <= product.desired_price:
                send_price_drop_email(product, current_price)
                self.stdout.write(f"Email sent for {product.name} to {product.user_email}")
            else:
                self.stdout.write(f"No price drop for {product.name}")


async def check_prices(self):
    # Fetch products asynchronously
    products = await sync_to_async(list)(Product.objects.all())  # Convert QuerySet to a list asynchronously

    for product in products:
        current_price = await fetch_price(product.url)  # Fetch price using your asynchronous function

        # Debug statement to inspect the value returned by fetch_price
        print(f"Fetched price for {product.name}: {current_price} ({type(current_price)})")

        if current_price is None:
            self.stdout.write(f"Could not fetch price for {product.name}. Skipping...")
            continue

        if isinstance(current_price, (tuple, list)):
            self.stdout.write(f"Unexpected return type from fetch_price for {product.name}. Skipping...")
            continue

        if current_price <= product.desired_price:
            send_price_drop_email(product, current_price)
            self.stdout.write(f"Email sent for {product.name} to {product.user_email}")
        else:
            self.stdout.write(f"No price drop for {product.name}")

        
       


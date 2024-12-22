from django_cron import CronJobBase, Schedule
from tracker.models import Product
from tracker.scraper import fetch_price
from tracker.tasks import send_price_drop_email
import asyncio
from asgiref.sync import sync_to_async

class PriceCheckCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # Run every hour

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'tracker.price_check_cron'

    def do(self):
        asyncio.run(self._check_prices())

    async def _check_prices(self):
        products = await sync_to_async(list)(Product.objects.all())

        for product in products:
            try:
                product_name, current_price = await fetch_price(product.url)

                if current_price is None:
                    print(f"Could not fetch price for {product.name}. Skipping...")
                    continue

                if current_price <= product.desired_price:
                    send_price_drop_email(product, current_price)
                    print(f"Email sent for {product.name} to {product.user_email}")
                else:
                    print(f"No price drop for {product.name}")
            except Exception as e:
                print(f"Error processing {product.name}: {e}")

from djongo import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from datetime import timedelta
import logging

logger = logging.getLogger('cron_logger')


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=1000)
    current_price = models.FloatField()
    desired_price = models.FloatField()
    price_history = models.JSONField(default=list)
    user_email = models.EmailField(default="")
    last_notified_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class APIUsage(models.Model):
    date = models.DateField(auto_now_add=True, unique=True)  # Tracks the start of the month
    total_requests = models.IntegerField(default=0)          # Tracks total requests made in the month

    @classmethod
    async def increment(cls):
        """
        Increment the request count for the current month in an async-compatible way.
        Returns True if the increment is successful (within limit), False otherwise.
        """
        try:
            today = now().date()
            start_of_month = today.replace(day=1)

            # Get or create the usage record for the current month
            usage, created = await sync_to_async(cls.objects.get_or_create)(date=start_of_month)

            if usage.total_requests < 100:  # Assuming 100 requests/month
                usage.total_requests += 1
                await sync_to_async(usage.save)()
                return True  # Request is allowed

            logger.warning("API usage limit for the month has been reached.")
            return False  # Limit reached

        except Exception as e:
            logger.error(f"Failed to check or update API usage: {e}")
            return False

    @classmethod
    async def reset_if_needed(cls):
        """
        Clean up old API usage records beyond 30 days in an async-compatible way.
        """
        try:
            threshold_date = now().date() - timedelta(days=30)
            await sync_to_async(cls.objects.filter(date__lt=threshold_date).delete)()
        except Exception as e:
            logger.error(f"Error resetting API usage records: {e}")

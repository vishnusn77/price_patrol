from djongo import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from asgiref.sync import sync_to_async
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
    date = models.DateField(auto_now_add=True, unique=True)
    total_requests = models.IntegerField(default=0)

    @classmethod
    async def increment(cls):
        """
        Increment the request count for the current day in an async-compatible way.
        Returns True if the increment is successful (within limit), False otherwise.
        """
        today = date.today()
        try:
            usage = await sync_to_async(cls.objects.get_or_create)(date=today)
            usage_instance = usage[0]  # Get the actual usage instance
            if usage_instance.total_requests < 100:  # Assuming limit is 100 requests/day
                usage_instance.total_requests += 1
                await sync_to_async(usage_instance.save)()
                return True  # Request is allowed
            logger.warning("API usage limit reached.")
            return False  # Limit reached
        except Exception as e:
            logger.error(f"Failed to check or update API usage: {e}")
            return False

    @classmethod
    async def reset_if_needed(cls):
        """
        Remove old API usage records beyond 30 days in an async-compatible way.
        """
        try:
            threshold_date = date.today() - timedelta(days=30)
            await sync_to_async(cls.objects.filter(date__lt=threshold_date).delete)()
        except Exception as e:
            logger.error(f"Error resetting API usage records: {e}")

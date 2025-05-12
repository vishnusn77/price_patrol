from djongo import models
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger('cron_logger')


class Product(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
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
    total_requests = models.IntegerField(default=0)  # Tracks total requests

    @classmethod
    async def increment(cls):
        """
        Increment the global API request count.
        Returns True if successful, False if the limit is reached.
        """
        try:
            # Ensure there is only one global record
            usage, _ = await sync_to_async(cls.objects.get_or_create)(id=1)
            usage.total_requests += 1
            await sync_to_async(usage.save)()
            logger.info(f"API usage incremented: {usage.total_requests}")
            return True  # Allow the request  
        except Exception as e:
            logger.error(f"Failed to check or update API usage: {e}")
            return True  

from djongo import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    current_price = models.FloatField()
    desired_price = models.FloatField()
    price_history = models.JSONField(default=list)

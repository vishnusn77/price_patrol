from djongo import models
from django.contrib.auth.models import User

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField()
    current_price = models.FloatField()
    desired_price = models.FloatField()
    price_history = models.JSONField(default=list)
    user_email = models.EmailField(default="anonymous@example.com")

    def __str__(self):
        return self.name

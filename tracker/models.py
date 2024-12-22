from djongo import models

class Product(models.Model):
    user = models.CharField(max_length=100, default='Anonymous')  # Add ForeignKey to User later
    name = models.CharField(max_length=255)
    url = models.URLField()
    current_price = models.FloatField()
    desired_price = models.FloatField()
    price_history = models.JSONField(default=list)
    user_email = models.EmailField(default="anonymous@example.com")

    def __str__(self):
        return self.name

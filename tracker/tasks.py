from django.core.mail import send_mail
from django.conf import settings

def send_price_drop_email(product, current_price):
    """Send an email to the user about a price drop."""
    subject = f"Price Drop Alert: {product.name}"
    message = (
        f"The price of {product.name} has dropped to {current_price}!\n\n"
        f"Check it out here: {product.url}"
    )
    recipient_list = [product.user_email]

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
    )

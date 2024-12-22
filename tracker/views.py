from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import RegisterForm
from .models import Product
from .forms import ProductForm
from django.contrib import messages
from .scraper import fetch_price
import asyncio
from asgiref.sync import sync_to_async
from django.core.mail import send_mail
from django.http import JsonResponse
from tracker.crons import PriceCheckCronJob

def run_price_check(request):
    try:
        # Run the cron job logic
        PriceCheckCronJob().do()
        return JsonResponse({"status": "success", "message": "Price check completed."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

def home_view(request):
    return render(request, 'tracker/home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)  # Don't save to DB yet
            product_name, current_price = asyncio.run(fetch_price(product.url))  # Fetch name and price
            
            if current_price is None:
                form.add_error('url', 'Could not fetch price for the given URL.')
            else:
                product.name = product_name  # Save the scraped product name
                product.current_price = current_price
                product.save()  # Save to the database
                return redirect('product_list')  # Redirect to the product list page

    else:
        form = ProductForm()

    return render(request, 'tracker/add_product.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'tracker/product_list.html', {'products': products})

def send_price_alert(product):
    """
    Send an email to the user when the product's price drops below the desired price.
    """
    subject = f"Price Drop Alert: {product.name}"
    message = f"""
    Great news!
    
    The price for {product.name} has dropped to ${product.current_price}.
    Check it out here: {product.url}

    Happy Shopping!
    """
    recipient_list = [product.user_email]
    send_mail(
        subject,
        message,
        'REDACTED',  # Replace with your Gmail address
        recipient_list,
        fail_silently=False,  # Set to True in production to avoid email failures causing crashes
    )
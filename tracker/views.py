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

async def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if await sync_to_async(form.is_valid)():
            product_url = form.cleaned_data['url']
            current_price = await fetch_price(product_url)

            if not current_price:
                await sync_to_async(form.add_error)('url', "Failed to fetch price. Please check the URL.")
                return await sync_to_async(render)(request, 'tracker/add_product.html', {'form': form})

            # Save product details to the database
            form.instance.current_price = current_price
            await sync_to_async(form.save)()
            return await sync_to_async(redirect)('product_list')
    else:
        form = await sync_to_async(ProductForm)()
    return await sync_to_async(render)(request, 'tracker/add_product.html', {'form': form})

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
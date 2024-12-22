from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import RegisterForm
from .models import Product
from .forms import ProductForm
from django.contrib import messages
from .scraper import fetch_price
import asyncio

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
        if form.is_valid():
            product_url = form.cleaned_data['url']
            cache_path = f"tracker/cache/{product_url.split('/')[-1]}.html"

            product_name, current_price = await fetch_price(product_url, cache_path)

            if not current_price:
                form.add_error('url', "Failed to fetch price. Please check the URL.")
                return render(request, 'tracker/add_product.html', {'form': form})

            form.instance.name = product_name
            form.instance.current_price = current_price
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'tracker/add_product.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'tracker/product_list.html', {'products': products})
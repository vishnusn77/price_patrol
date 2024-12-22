from django.urls import path
from .views import register_view, login_view, logout_view, home_view, add_product, product_list
from . import views

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add_product/', add_product, name='add_product'),
    path('products/', product_list, name='product_list'),
    path('run-price-check/', views.run_price_check, name='run_price_check'),
]

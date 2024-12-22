from django.urls import path
from .views import register_view, login_view, logout_view, home_view, add_product, product_list

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add_product/', add_product, name='add_product'),
    path('products/', product_list, name='product_list'),
]

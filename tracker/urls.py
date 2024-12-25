from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    home_view,
    add_product,
    product_list,
    run_check_prices,
    keep_alive_view,
)

urlpatterns = [
    path('', login_view, name='home'),  # Redirect root URL to the login page
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add_product/', add_product, name='add_product'),
    path('products/', product_list, name='product_list'),
    path('run_check_prices/', run_check_prices, name='run_check_prices'),
    path('keep-alive/', keep_alive_view, name='keep_alive'),
]

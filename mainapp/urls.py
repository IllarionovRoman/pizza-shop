from django.urls import path
from .views import *

urlpatterns = [
    path('', BaseView.as_view(), name='base_url'),
    path('products/create/', ProductsCreate.as_view(), name='products_create_url'),
    path('products/<str:slug>/', products_detail, name='products_detail_url'),
    path('cart/', CartView.as_view(), name='cart_url'),
    path('add-to-cart/<str:slug>/', AddToCartView.as_view(), name='add_to_cart_url'),
    path('delete-to-cart/<str:slug>/', DeleteFromCartView.as_view(), name='delete_to_cart_url'),
    path('change-qty/<str:slug>/', ChangeQTYView.as_view(), name='change_qty_url'),
    path('profile/', ProfileView.as_view(), name='profile_url'),
    path('checkout/', CheckoutView.as_view(), name='checkout_url'),
    path('make-order/', OrderCreate.as_view(), name='make_order'),
    path('orders/', OrdersView.as_view(), name='orders_url'),
    path('orders/<str:slug>/', OrdersDetail.as_view(), name='orders_detail_url'),
    path('profile/', ProfileView.as_view(), name='profile_url'),
    path('category/create/', CategoryCreate.as_view(), name='category_create_url'),
    path('category/<str:slug>/', CategoryDetail.as_view(), name='category_detail_url'),
    path('registration/', RegistrationView.as_view(), name='registration_url'),
    path('login/', LoginView.as_view(), name='login_url'),
]
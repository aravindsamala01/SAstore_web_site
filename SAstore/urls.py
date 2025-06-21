from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import admin_dashboard
from .views import combined_login_signup_view

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.all_products, name='all_products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),

    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('charge/', views.charge, name='charge'),

    path('orders/', views.order_list, name='order_list'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),

    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),

    path('accounts/', combined_login_signup_view, name='login'),
    path('signup/', combined_login_signup_view, name='signup'),

    path('signup/', views.signup_view, name='signup'),
    path('signup/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),


]

from django.urls import path

from . import views

urlpatterns = [
    path('', views.customer_login, name='customer_login'),
    path('home/', views.customer_home, name='customer_home'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('catalog/<str:category>/', views.customer_catalog, name='customer_catalog'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('cart/create/', views.create_cart, name='create_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/items/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/items/<int:item_id>/remove/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    path('api/search/', views.search_products, name='search_products'),
]

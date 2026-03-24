from django.urls import path

from . import views

urlpatterns = [
    path('', views.laptop_home, name='laptop_home'),
    path('api/laptops/', views.laptop_api_page, name='laptop_api_page'),
    path('api/laptops/search/', views.search_laptops, name='search_laptops'),
]

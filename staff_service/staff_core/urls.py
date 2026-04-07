from django.urls import path

from . import views

urlpatterns = [
    path('', views.staff_login, name='staff_login'),
    path('home/', views.staff_home, name='staff_home'),
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('customers/', views.staff_customers, name='staff_customers'),
    path('inventory/', views.staff_inventory, name='staff_inventory'),
    path('catalog/<str:category>/', views.staff_catalog, name='staff_catalog'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('items/<int:item_id>/update/', views.update_item, name='update_item'),
    path('items/<int:item_id>/delete/', views.delete_item, name='delete_item'),
]

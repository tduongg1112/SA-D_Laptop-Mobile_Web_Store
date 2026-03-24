from django.urls import path

from . import views

urlpatterns = [
    path('', views.mobile_home, name='mobile_home'),
    path('api/mobiles/', views.mobile_api_page, name='mobile_api_page'),
    path('api/mobiles/search/', views.search_mobiles, name='search_mobiles'),
]

from django.contrib import admin
from django.urls import path
from searches import views

urlpatterns = [
    path('', views.all_searches, name="all_searches"),
    path('<int:search_id>', views.search, name="search"),
    path('update_prices/<int:search_id>', views.update_prices, name="update_prices"),
    path('new_search', views.new_search, name="new_search")
]
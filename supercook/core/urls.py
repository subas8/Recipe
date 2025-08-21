from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('api/search/', views.search_recipes, name='api-search'),
    path('api/suggestions/', views.suggest_ingredients, name='api-suggestions'),
    path('api/favorites/', views.favorites, name='api-favorites'),
]


from django.urls import path
from . import views

urlpatterns = [
    path('price/<str:ticker>/', views.get_stock_price, name='stock-price'),
    path('search/', views.search_stocks_view, name='stock-search'),
    path('top-movers/', views.top_movers, name='top-movers'),
]
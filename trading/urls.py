from django.urls import path
from trading.ml_views import TradeInsightsView
from trading.views import (
    BuyView, SellView, PlaceOrderView, CancelOrderView,
    PortfolioView, TransactionHistoryView, PendingOrdersView,PnlHistoryView,
    LeaderboardView,
)

urlpatterns = [
    path('buy/', BuyView.as_view(), name='buy'),
    path('sell/', SellView.as_view(), name='sell'),
    path('order/', PlaceOrderView.as_view(), name='place-order'),
    path('order/<int:order_id>/', CancelOrderView.as_view(), name='cancel-order'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('history/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('orders/', PendingOrdersView.as_view(), name='pending-orders'),
    path('pnl-history/', PnlHistoryView.as_view()),
    path('leaderboard/', LeaderboardView.as_view()),
    path('insights/', TradeInsightsView.as_view(), name='trade-insights'),
]

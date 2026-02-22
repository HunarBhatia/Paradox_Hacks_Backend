import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from market.utils import get_market_status
from services.price_service import get_multiple_prices, get_price, search_stocks

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stock_price(request, ticker):
    """GET /api/market/price/<ticker>/"""
    data = get_price(ticker.upper())
    if not data:
        return Response(
            {'error': f'Could not fetch price for {ticker}'},
            status=404
        )
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_stocks_view(request):
    """GET /api/market/search/?q=reliance"""
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response(
            {'error': 'Query param `q` is required'},
            status=400
        )
    results = search_stocks(query)
    return Response({'results': results, 'count': len(results)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_movers(request):
    """GET /api/market/top-movers/"""
    WATCHLIST = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
        'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 'AXISBANK',
        'LT', 'WIPRO', 'HCLTECH', 'MARUTI', 'BAJFINANCE',
    ]

    prices = get_multiple_prices(WATCHLIST)
    valid = [v for v in prices.values() if v and v.get('change_percent') is not None]
    sorted_prices = sorted(valid, key=lambda x: x['change_percent'], reverse=True)

    return Response({
        'gainers': sorted_prices[:5],
        'losers': sorted_prices[-5:][::-1],
        'market_status': get_market_status(),
    })
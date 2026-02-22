import logging
from typing import Dict

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from market.utils import get_market_status
from services.price_service import get_multiple_prices, get_price, search_stocks

logger = logging.getLogger(__name__)

# 🔥 HARDCODED FALLBACKS for weekends/market closed (RELIANCE etc.)
COMMON_STOCKS: Dict[str, Dict] = {
    'RELIANCE': {'ticker': 'RELIANCE', 'name': 'Reliance Industries Ltd'},
    'TCS': {'ticker': 'TCS', 'name': 'Tata Consultancy Services'},
    'INFY': {'ticker': 'INFY', 'name': 'Infosys Ltd'},
    'HDFCBANK': {'ticker': 'HDFCBANK', 'name': 'HDFC Bank Ltd'},
    'ICICIBANK': {'ticker': 'ICICIBANK', 'name': 'ICICI Bank Ltd'},
    'SBIN': {'ticker': 'SBIN', 'name': 'State Bank of India'},
}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stock_price(request, ticker):
    """GET /api/market/price/<ticker>/"""
    clean_ticker = ticker.upper().strip()
    logger.info(f"Fetching price for: {clean_ticker}")

    data = get_price(clean_ticker)

    if not data or 'price' not in data:
        logger.warning(f"No price data for {clean_ticker}")
        return Response(
            {'error': f'Could not fetch price for {clean_ticker} (market closed?)'},
            status=404
        )

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_stocks_view(request):
    """GET /api/market/search/?q=reliance"""
    query = request.query_params.get('q', '').strip().upper()
    logger.info(f"Searching stocks for: {query}")

    if not query or len(query) < 2:
        return Response(
            {'error': 'Query param `q` must be 2+ characters'},
            status=400
        )

    # 🔥 PRIORITY 1: Exact match in common stocks
    if query in COMMON_STOCKS:
        result = COMMON_STOCKS[query]
        return Response({
            'results': [result],
            'count': 1,
            'source': 'fallback'
        })

    # 🔥 PRIORITY 2: Fuzzy match common stocks
    matches = []
    for key, stock in COMMON_STOCKS.items():
        if query in key or query in stock['name'].upper():
            matches.append(stock)

    if matches:
        return Response({
            'results': matches[:5],
            'count': len(matches),
            'source': 'fallback'
        })

    # 🔥 PRIORITY 3: Finnhub search (via price_service)
    try:
        results = search_stocks(query)
        valid_results = []

        for r in results:
            if r.get('symbol') and len(r['symbol'].strip()) > 0:
                valid_results.append({
                    'ticker': r['symbol'].strip().upper(),
                    'name': r.get('name', 'Unknown')
                })

        if valid_results:
            return Response({
                'results': valid_results[:10],
                'count': len(valid_results),
                'source': 'finnhub'
            })

    except Exception as e:
        logger.error(f"Stock search failed: {e}")

    # 🔥 FINAL FALLBACK
    return Response({
        'results': [{'ticker': query, 'name': f"{query} Ltd (fallback)"}],
        'count': 1,
        'source': 'generic-fallback'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_movers(request):
    """GET /api/market/top-movers/"""
    WATCHLIST = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
        'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 'AXISBANK',
        'LT', 'WIPRO', 'HCLTECH', 'MARUTI', 'BAJFINANCE',
    ]

    try:
        prices = get_multiple_prices(WATCHLIST)
        valid = []

        for ticker in WATCHLIST:
            p = prices.get(ticker)

            if p:
                valid.append({
                    "ticker": ticker,
                    "price": p.get("price"),
                    "change": p.get("change", 0),
                    "change_percent": p.get("change_percent", 0),
                    "source": p.get("source"),
                    "cached": p.get("cached", False),
                })
            else:
                valid.append({
                    "ticker": ticker,
                    "price": None,
                    "change": 0,
                    "change_percent": 0,
                    "source": "unavailable",
                    "cached": False,
                })

        sorted_prices = sorted(
            valid,
            key=lambda x: x.get('change_percent', 0),
            reverse=True
        )

        return Response({
            'gainers': sorted_prices[:5],
            'losers': sorted_prices[-5:][::-1],
            'market_status': get_market_status(),
        })

    except Exception as e:
        logger.error(f"Top movers failed: {e}")
        return Response({'error': 'Top movers unavailable'}, status=500)
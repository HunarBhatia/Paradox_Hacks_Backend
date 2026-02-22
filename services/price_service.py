import json
import logging

import finnhub
import redis
import yfinance as yf
from django.conf import settings

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)

CACHE_TTL = 30


def _nse_ticker(symbol: str) -> str:
    symbol = symbol.upper().strip()
    if not symbol.endswith('.NS') and not symbol.endswith('.BSE'):
        return f"{symbol}.NS"
    return symbol


def get_price(symbol: str) -> dict | None:
    symbol = symbol.upper().strip()
    cache_key = f"price:{symbol}"

    # 1. Check cache first
    cached = redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        data['cached'] = True
        return data

    # 2. Try yfinance
    try:
        ticker = yf.Ticker(_nse_ticker(symbol))
        info = ticker.fast_info
        price = info.last_price
        prev_close = info.previous_close

        if price:
            change = round(price - prev_close, 2) if prev_close else 0
            change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
            data = {
                'symbol': symbol,
                'price': round(float(price), 2),
                'change': change,
                'change_percent': change_pct,
                'volume': info.three_month_average_volume,
                'source': 'yfinance',
                'cached': False,
            }
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
            return data

    except Exception as e:
        logger.warning(f"yfinance failed for {symbol}: {e}")

    # 3. Finnhub fallback
    try:
        quote = finnhub_client.quote(symbol)
        if quote and quote.get('c'):
            data = {
                'symbol': symbol,
                'price': round(float(quote['c']), 2),
                'change': round(float(quote['d']), 2),
                'change_percent': round(float(quote['dp']), 2),
                'volume': None,
                'source': 'finnhub',
                'cached': False,
            }
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
            return data

    except Exception as e:
        logger.error(f"Finnhub fallback failed for {symbol}: {e}")

    return None


def get_multiple_prices(symbols: list[str]) -> dict:
    return {symbol: get_price(symbol) for symbol in symbols}


def search_stocks(query: str) -> list:
    try:
        results = finnhub_client.symbol_lookup(query)
        nse = [
            {
                'symbol': r['symbol'].replace('.NS', ''),
                'name': r['description'],
                'exchange': r.get('type', ''),
            }
            for r in results.get('result', [])
            if 'NS' in r.get('symbol', '') or 'NSE' in r.get('displaySymbol', '')
        ]
        return nse[:10]
    except Exception as e:
        logger.error(f"Stock search failed: {e}")
        return []
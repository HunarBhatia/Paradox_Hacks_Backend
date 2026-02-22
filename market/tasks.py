import logging

from celery import shared_task

from market.utils import is_market_open
from services.price_service import get_multiple_prices

logger = logging.getLogger(__name__)

TOP_NSE_STOCKS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
    'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'BAJFINANCE',
    'HCLTECH', 'WIPRO', 'ULTRACEMCO', 'TITAN', 'SUNPHARMA',
    'ONGC', 'POWERGRID', 'NTPC', 'TECHM', 'NESTLEIND',
    'BAJAJFINSV', 'JSWSTEEL', 'TATAMOTORS', 'ADANIENT', 'ADANIPORTS',
    'TATASTEEL', 'COALINDIA', 'DIVISLAB', 'DRREDDY', 'CIPLA',
    'HDFCLIFE', 'SBILIFE', 'INDUSINDBK', 'GRASIM', 'BRITANNIA',
    'EICHERMOT', 'HEROMOTOCO', 'APOLLOHOSP', 'TATACONSUM', 'BPCL',
    'VEDL', 'IOC', 'SHREECEM', 'UPL', 'HINDALCO',
]


@shared_task(name='market.warm_price_cache')
def warm_price_cache():
    if not is_market_open():
        logger.info('Market closed — skipping cache warm.')
        return {'skipped': True, 'reason': 'market_closed'}

    success, failed = 0, 0
    for symbol in TOP_NSE_STOCKS:
        result = get_multiple_prices([symbol])
        if result.get(symbol):
            success += 1
        else:
            failed += 1

    logger.info(f'Cache warm complete — success: {success}, failed: {failed}')
    return {'success': success, 'failed': failed}
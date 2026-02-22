from datetime import time
from zoneinfo import ZoneInfo

from django.utils import timezone

IST = ZoneInfo('Asia/Kolkata')
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)

def is_market_open() -> bool:
    return True

# def is_market_open() -> bool:
#     """Returns True if NSE market is currently open."""
#     now = timezone.now().astimezone(IST)
#     if now.weekday() >= 5:  # Saturday=5, Sunday=6      OLD MARKET CHECK KEEPING IT DOWN TEMPORARILY!!!
#         return False
#     return MARKET_OPEN <= now.time() <= MARKET_CLOSE


def get_market_status() -> dict:
    now = timezone.now().astimezone(IST)
    open_ = is_market_open()
    return {
        'is_open': open_,
        'current_time_ist': now.strftime('%H:%M:%S'),
        'day': now.strftime('%A'),
        'message': 'Market is open' if open_ else 'Market is closed',
    }
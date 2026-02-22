from celery import shared_task
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import datetime
import redis

from market.utils import is_market_open
from services.price_service import get_price, get_multiple_prices
from services.trade_service import execute_buy, execute_sell
from trading.models import Order, PortfolioSnapshot

User = get_user_model()

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
LEADERBOARD_KEY = "leaderboard:returns"
STARTING_BALANCE = Decimal("100000.00")


@shared_task
def process_pending_orders():
    if not is_market_open():
        return "Market closed. Skipping order processing."

    pending_orders = Order.objects.filter(status='PENDING').select_related('user')

    executed, failed = 0, 0

    for order in pending_orders:
        try:
            raw_price = get_price(order.ticker)
            if not raw_price:
                continue

            current_price = Decimal(str(raw_price))
            target = order.target_price
            should_execute = False

            if order.order_type == 'LIMIT_BUY' and current_price <= target:
                should_execute = True
            elif order.order_type == 'LIMIT_SELL' and current_price >= target:
                should_execute = True
            elif order.order_type == 'STOP_LOSS' and current_price <= target:
                should_execute = True

            if should_execute:
                if order.order_type == 'LIMIT_BUY':
                    execute_buy(order.user, order.ticker, order.quantity, order_type='LIMIT')
                else:
                    execute_sell(order.user, order.ticker, order.quantity, order_type='LIMIT')

                order.status = 'EXECUTED'
                order.save()
                executed += 1

        except Exception as e:
            failed += 1
            print(f"Failed to execute order {order.id}: {e}")

    return f"Processed {len(pending_orders)} orders. Executed: {executed}, Failed: {failed}"


@shared_task
def take_portfolio_snapshots():
    today = timezone.localdate()
    yesterday = today - datetime.timedelta(days=1)

    users = User.objects.prefetch_related('portfolioposition_set', 'wallet').all()

    for user in users:
        try:
            positions = list(user.portfolioposition_set.all())

            invested_value = Decimal("0.00")
            if positions:
                tickers = [p.ticker for p in positions]
                prices = get_multiple_prices(tickers)
                for position in positions:
                    price = Decimal(str(prices.get(position.ticker, 0)))
                    invested_value += price * position.quantity

            cash_balance = user.wallet.balance
            total_value = cash_balance + invested_value

            daily_pnl = Decimal("0.00")
            try:
                yesterday_snap = PortfolioSnapshot.objects.get(user=user, date=yesterday)
                daily_pnl = total_value - yesterday_snap.total_value
            except PortfolioSnapshot.DoesNotExist:
                pass

            PortfolioSnapshot.objects.update_or_create(
                user=user,
                date=today,
                defaults={
                    'total_value': total_value,
                    'cash_balance': cash_balance,
                    'invested_value': invested_value,
                    'daily_pnl': daily_pnl,
                }
            )

        except Exception as e:
            print(f"Snapshot failed for {user.username}: {e}")

    return f"Snapshots taken for {users.count()} users"


@shared_task
def update_leaderboard():
    if not is_market_open():
        return "Market closed. Skipping leaderboard update."

    users = User.objects.prefetch_related('portfolioposition_set', 'wallet').all()
    pipeline = redis_client.pipeline()

    for user in users:
        try:
            positions = list(user.portfolioposition_set.all())

            invested_value = Decimal("0.00")
            if positions:
                tickers = [p.ticker for p in positions]
                prices = get_multiple_prices(tickers)
                for position in positions:
                    price = Decimal(str(prices.get(position.ticker, 0)))
                    invested_value += price * position.quantity

            total_value = user.wallet.balance + invested_value
            return_pct = float(((total_value - STARTING_BALANCE) / STARTING_BALANCE) * 100)

            pipeline.zadd(LEADERBOARD_KEY, {user.username: return_pct})

        except Exception as e:
            print(f"Leaderboard update failed for {user.username}: {e}")

    pipeline.execute()
    return f"Leaderboard updated for {users.count()} users"
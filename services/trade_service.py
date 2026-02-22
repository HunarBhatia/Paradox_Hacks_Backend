import random
from decimal import Decimal
from django.db import transaction

from market.utils import is_market_open
from services.price_service import get_price
from trading.models import Transaction, PortfolioPosition
from users.models import Wallet


def _apply_slippage(price: Decimal) -> Decimal:
    """Add random slippage between 0.05% and 0.1% to simulate real market conditions."""
    slippage = Decimal(str(random.uniform(1.0005, 1.001)))
    return (price * slippage).quantize(Decimal('0.01'))


def _calculate_brokerage(total_cost: Decimal) -> Decimal:
    """Brokerage is 0.1% of trade value, capped at ₹20."""
    return min(Decimal('20.00'), (total_cost * Decimal('0.001')).quantize(Decimal('0.01')))


def execute_buy(user, ticker: str, quantity: int, order_type: str = 'MARKET') -> dict:
    if not is_market_open():
        raise ValueError("Market is currently closed. Trading is only allowed between 9:15 AM and 3:30 PM IST on weekdays.")

    raw_price = get_price(ticker)
    if not raw_price:
        raise ValueError(f"Could not fetch price for {ticker}. Please try again.")

    price = _apply_slippage(Decimal(str(raw_price['price'])))
    total_cost = (price * quantity).quantize(Decimal('0.01'))
    brokerage = _calculate_brokerage(total_cost)
    total_deduction = total_cost + brokerage

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(user=user)

        if wallet.balance < total_deduction:
            raise ValueError(
                f"Insufficient balance. Required: ₹{total_deduction}, Available: ₹{wallet.balance}"
            )

        wallet.balance -= total_deduction
        wallet.save()

        position, created = PortfolioPosition.objects.get_or_create(
            user=user,
            ticker=ticker,
            defaults={'quantity': quantity, 'avg_buy_price': price}
        )

        if not created:
            total_qty = position.quantity + quantity
            new_avg = ((position.avg_buy_price * position.quantity) + (price * quantity)) / total_qty
            position.avg_buy_price = new_avg.quantize(Decimal('0.01'))
            position.quantity = total_qty
            position.save()

        Transaction.objects.create(
            user=user,
            ticker=ticker,
            action='BUY',
            quantity=quantity,
            price_at_execution=price,
            brokerage=brokerage,
            total_value=total_cost,
            order_type=order_type,
        )

    return {
        'ticker': ticker,
        'quantity': quantity,
        'price': float(price),
        'brokerage': float(brokerage),
        'total_deducted': float(total_deduction),
        'remaining_balance': float(wallet.balance),
    }


def execute_sell(user, ticker: str, quantity: int, order_type: str = 'MARKET') -> dict:
    if not is_market_open():
        raise ValueError("Market is currently closed. Trading is only allowed between 9:15 AM and 3:30 PM IST on weekdays.")

    try:
        position = PortfolioPosition.objects.get(user=user, ticker=ticker)
    except PortfolioPosition.DoesNotExist:
        raise ValueError(f"You don't hold any shares of {ticker}.")

    if position.quantity < quantity:
        raise ValueError(
            f"Insufficient shares. You hold {position.quantity} shares of {ticker}, tried to sell {quantity}."
        )

    raw_price = get_price(ticker)
    if not raw_price:
        raise ValueError(f"Could not fetch price for {ticker}. Please try again.")

    price = _apply_slippage(Decimal(str(raw_price['price'])))
    total_credit = (price * quantity).quantize(Decimal('0.01'))
    brokerage = _calculate_brokerage(total_credit)
    net_credit = total_credit - brokerage

    pnl = ((price - position.avg_buy_price) * quantity).quantize(Decimal('0.01'))

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(user=user)

        wallet.balance += net_credit
        wallet.save()

        if position.quantity == quantity:
            position.delete()
        else:
            position.quantity -= quantity
            position.save()

        Transaction.objects.create(
            user=user,
            ticker=ticker,
            action='SELL',
            quantity=quantity,
            price_at_execution=price,
            brokerage=brokerage,
            total_value=total_credit,
            order_type=order_type,
            pnl=pnl,
        )

    return {
        'ticker': ticker,
        'quantity': quantity,
        'price': float(price),
        'brokerage': float(brokerage),
        'net_credited': float(net_credit),
        'pnl': float(pnl),
        'remaining_balance': float(wallet.balance),
    }
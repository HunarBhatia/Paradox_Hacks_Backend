import pandas as pd
import yfinance as yf
import ta
from datetime import timedelta
from django.contrib.auth import get_user_model
from trading.models import Transaction

User = get_user_model()


def _get_time_of_day_bucket(hour: int) -> str:
    """Categorize trade time into morning / afternoon / late."""
    if 9 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 14:
        return 'afternoon'
    else:
        return 'late'


def _get_trend(closes: pd.Series) -> str:
    """Simple trend detection using 20-day MA."""
    if len(closes) < 20:
        return 'SIDEWAYS'
    ma = closes.rolling(20).mean().iloc[-1]
    current = closes.iloc[-1]
    if current > ma * 1.02:
        return 'UP'
    elif current < ma * 0.98:
        return 'DOWN'
    return 'SIDEWAYS'


def _get_volatility(closes: pd.Series) -> str:
    """High volatility if std dev of last 10 days is above threshold."""
    if len(closes) < 10:
        return 'LOW'
    std = closes.pct_change().rolling(10).std().iloc[-1]
    return 'HIGH' if std > 0.02 else 'LOW'


def _get_volume_level(volumes: pd.Series) -> str:
    """Compare latest volume to 20-day average."""
    if len(volumes) < 20:
        return 'LOW'
    avg_volume = volumes.rolling(20).mean().iloc[-1]
    current = volumes.iloc[-1]
    return 'HIGH' if current > avg_volume * 1.2 else 'LOW'


def _fetch_market_state(ticker: str, trade_date) -> dict:
    """
    Fetch historical data from yfinance for a ticker around a trade date.
    Computes all market state columns needed by the ML model.
    """
    try:
        start = trade_date - timedelta(days=60)
        end = trade_date + timedelta(days=1)

        data = yf.download(
            f"{ticker}.NS",
            start=start,
            end=end,
            progress=False
        )

        if data.empty or len(data) < 5:
            return {}

        closes = data['Close']
        volumes = data['Volume']
        highs = data['High']
        lows = data['Low']

        # RSI using ta library — one line
        rsi_series = ta.momentum.RSIIndicator(closes, window=14).rsi()
        rsi_value = round(float(rsi_series.iloc[-1]), 2) if not rsi_series.empty else None

        # Moving average distance
        ma_20 = closes.rolling(20).mean().iloc[-1]
        current_price = closes.iloc[-1]
        distance_from_ma = round(float((current_price - ma_20) / ma_20), 4) if ma_20 else None

        # Distance from recent high and low (last 20 days)
        recent_high = highs.rolling(20).max().iloc[-1]
        recent_low = lows.rolling(20).min().iloc[-1]
        distance_from_high = round(float((current_price - recent_high) / recent_high), 4) if recent_high else None
        distance_from_low = round(float((current_price - recent_low) / recent_low), 4) if recent_low else None

        return {
            'trend': _get_trend(closes),
            'volatility': _get_volatility(closes),
            'volume_level': _get_volume_level(volumes),
            'distance_from_ma': distance_from_ma,
            'rsi_value': rsi_value,
            'distance_from_recent_high': distance_from_high,
            'distance_from_recent_low': distance_from_low,
        }

    except Exception as e:
        print(f"Market state fetch failed for {ticker} on {trade_date}: {e}")
        return {}


def _match_trades(transactions: list) -> list:
    """
    Match BUY transactions to SELL transactions for the same ticker.
    Uses FIFO matching — first buy matched to first sell.
    Returns a list of completed trade dicts.
    """
    from collections import defaultdict
    buys = defaultdict(list)
    completed_trades = []
    trade_id = 1

    for txn in transactions:
        if txn.action == 'BUY':
            buys[txn.ticker].append(txn)

        elif txn.action == 'SELL' and buys[txn.ticker]:
            buy_txn = buys[txn.ticker].pop(0)  # FIFO

            entry_time = buy_txn.timestamp
            exit_time = txn.timestamp
            holding_seconds = (exit_time - entry_time).total_seconds()
            holding_hours = round(holding_seconds / 3600, 2)

            position_size = float(buy_txn.price_at_execution * buy_txn.quantity)
            pnl = float(txn.pnl) if txn.pnl else 0
            pnl_pct = round((pnl / position_size) * 100, 2) if position_size else 0

            completed_trades.append({
                'trade_id': trade_id,
                'ticker': txn.ticker,
                'direction': 'LONG',  # paper trading only supports LONG for now
                'entry_time': entry_time,
                'exit_time': exit_time,
                'entry_price': float(buy_txn.price_at_execution),
                'exit_price': float(txn.price_at_execution),
                'quantity': txn.quantity,
                'position_size': position_size,
                'holding_time': holding_hours,
                'time_of_day_bucket': _get_time_of_day_bucket(entry_time.hour),
                'day_of_week': entry_time.strftime('%A'),
                'pnl': pnl,
                'pnl_pct': pnl_pct,
            })
            trade_id += 1

    return completed_trades


def build_trade_dataframe(user) -> pd.DataFrame:
    """
    Main function. Builds the complete DataFrame for a user's trades.
    Fetches all their transactions, matches buys to sells,
    enriches each completed trade with market state data from yfinance.
    Returns a pandas DataFrame ready to pass to the ML function.
    """
    transactions = list(
        Transaction.objects.filter(user=user).order_by('timestamp')
    )

    if not transactions:
        return pd.DataFrame()

    completed_trades = _match_trades(transactions)

    if not completed_trades:
        return pd.DataFrame()

    # Enrich each trade with market state
    enriched = []
    for trade in completed_trades:
        market_state = _fetch_market_state(
            trade['ticker'],
            trade['entry_time'].date()
        )
        enriched.append({**trade, **market_state})

    df = pd.DataFrame(enriched)
    return df


def export_trades_to_csv(user, filepath: str = None) -> str:
    """
    Optional — export the DataFrame to a CSV file.
    Returns the filepath. Used if ML friend wants a file instead of DataFrame.
    """
    df = build_trade_dataframe(user)

    if df.empty:
        return None

    if not filepath:
        filepath = f"/tmp/trades_{user.username}.csv"

    df.to_csv(filepath, index=False)
    return filepath
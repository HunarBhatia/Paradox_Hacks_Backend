def compute_metrics(df):
    if len(df) == 0:
        return None

    total_trades = len(df)
    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] <= 0]
    win_rate = len(wins) / total_trades
    avg_win = wins["pnl"].mean() if len(wins) > 0 else 0.0
    avg_loss = abs(losses["pnl"].mean()) if len(losses) > 0 else 0.0
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    total_profit = wins["pnl"].sum()
    total_loss = abs(losses["pnl"].sum())
    profit_factor = total_profit / total_loss if total_loss > 0 else None

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 3),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "expectancy": round(expectancy, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor else None,
    }
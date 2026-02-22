import pandas as pd

REQUIRED_MARKET_COLUMNS = [
    "trend",
    "volatility",
    "volume_level",
    "distance_from_ma",
    "rsi_value",
    "distance_from_recent_high",
    "distance_from_recent_low",
]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["entry_time", "exit_time"])

    df["pnl"] = (
        (df["exit_price"] - df["entry_price"]) * df["quantity"]
    )

    df.loc[df["direction"] == "SHORT", "pnl"] *= -1

    df["return_pct"] = df["pnl"] / (
        df["entry_price"] * df["quantity"]
    )

    df["outcome"] = df["pnl"].apply(
        lambda x: "WIN" if x > 0 else "LOSS"
    )

    return df


def validate_market_features(df: pd.DataFrame) -> pd.DataFrame:
    # missing = [
    #     col for col in REQUIRED_MARKET_COLUMNS if col not in df.columns
    # ]

    # if missing:
    #     raise ValueError(f"Missing market columns: {missing}")

    return df
import pandas as pd
from services.ml.data_loader import validate_market_features
from services.ml.metric import compute_metrics
from services.ml.segmentation import segment_by_column
from services.ml.llm_report import generate_report
from services.ml.data_loader import validate_market_features
from services.ml.metric import compute_metrics
from services.ml.segmentation import segment_by_column
from services.ml.llm_report import generate_report


def run_analysis_from_df(df: pd.DataFrame) -> dict:
    df = validate_market_features(df)

    overall = compute_metrics(df)

    segmentation = {
        "trend": segment_by_column(df, "trend"),
        "volatility": segment_by_column(df, "volatility"),
        "direction": segment_by_column(df, "direction"),
        "time_of_day": segment_by_column(df, "time_of_day_bucket"),
        "day_of_week": segment_by_column(df, "day_of_week"),
    }

    behavior = {
        "avg_holding_time": float(df["holding_time"].mean()),
        "avg_win_hold_time": float(df[df["pnl"] > 0]["holding_time"].mean()) if len(df[df["pnl"] > 0]) > 0 else None,
        "avg_loss_hold_time": float(df[df["pnl"] <= 0]["holding_time"].mean()) if len(df[df["pnl"] <= 0]) > 0 else None,
    }

    return {
        "overall": overall,
        "segmentation": segmentation,
        "behavior": behavior,
    }


def get_ml_insights(df: pd.DataFrame) -> tuple:
    analytics = run_analysis_from_df(df)
    report = generate_report(analytics)
    return report, analytics
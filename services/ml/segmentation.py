from services.ml.metric import compute_metrics


def segment_by_column(df, column):
    if column not in df.columns:
        return {}

    results = {}
    for value in df[column].dropna().unique():
        subset = df[df[column] == value]
        results[str(value)] = compute_metrics(subset)

    return results
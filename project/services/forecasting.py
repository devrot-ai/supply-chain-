from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd



def moving_average(data: Iterable[float], n: int = 3) -> float:
    values = list(data)
    if not values:
        return 0.0
    window = min(n, len(values))
    return float(sum(values[-window:]) / window)



def linear_regression_forecast(data: Iterable[float], horizon: int = 1) -> float:
    values = list(data)
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])

    try:
        from sklearn.linear_model import LinearRegression

        x_values = np.arange(len(values)).reshape(-1, 1)
        y_values = np.array(values)
        model = LinearRegression().fit(x_values, y_values)
        future_index = np.array([[len(values) + horizon - 1]])
        prediction = model.predict(future_index)[0]
        return float(prediction)
    except Exception:
        # Fallback keeps engine functional when sklearn is unavailable.
        x_values = np.arange(len(values))
        slope, intercept = np.polyfit(x_values, np.array(values), 1)
        future_x = len(values) + horizon - 1
        return float(slope * future_x + intercept)



def forecast_by_product(
    demand_df: pd.DataFrame,
    method: str = "moving_average",
    window: int = 3,
) -> pd.DataFrame:
    if method not in {"moving_average", "linear_regression"}:
        raise ValueError("method must be either 'moving_average' or 'linear_regression'")

    rows: list[dict[str, float | str]] = []
    sorted_df = demand_df.sort_values("date")

    for product_id, product_df in sorted_df.groupby("product_id"):
        series = product_df["demand"].tolist()
        if method == "moving_average":
            forecast = moving_average(series, n=window)
        else:
            forecast = linear_regression_forecast(series)

        rows.append(
            {
                "product_id": product_id,
                "predicted_demand": round(float(forecast), 2),
                "forecast_method": method,
            }
        )

    return pd.DataFrame(rows)

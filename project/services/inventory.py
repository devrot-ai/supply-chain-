from __future__ import annotations

import math

import pandas as pd



def reorder_decision(stock: float, predicted_demand: float, safety_buffer: float = 20) -> bool:
    return stock < (predicted_demand + safety_buffer)



def recommended_reorder_qty(stock: float, predicted_demand: float, safety_buffer: float = 20) -> int:
    target_level = predicted_demand + safety_buffer
    return max(0, math.ceil(target_level - stock))



def build_inventory_actions(
    inventory_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    safety_buffer: float = 20,
) -> pd.DataFrame:
    stock_by_product = (
        inventory_df.groupby("product_id", as_index=False)["stock_level"]
        .sum()
        .rename(columns={"stock_level": "current_stock"})
    )

    merged = stock_by_product.merge(forecast_df, on="product_id", how="left")
    merged["predicted_demand"] = merged["predicted_demand"].fillna(0)
    merged["reorder_required"] = merged.apply(
        lambda row: reorder_decision(row["current_stock"], row["predicted_demand"], safety_buffer),
        axis=1,
    )
    merged["reorder_qty"] = merged.apply(
        lambda row: recommended_reorder_qty(row["current_stock"], row["predicted_demand"], safety_buffer),
        axis=1,
    )
    return merged

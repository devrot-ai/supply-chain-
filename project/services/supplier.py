from __future__ import annotations

import pandas as pd



def supplier_risk(score: float, delay: float) -> str:
    if delay > 0.3 or score < 0.6:
        return "HIGH RISK"
    return "SAFE"



def assess_suppliers(suppliers_df: pd.DataFrame) -> pd.DataFrame:
    assessed = suppliers_df.copy()
    assessed["risk_level"] = assessed.apply(
        lambda row: supplier_risk(row["reliability_score"], row["delay_rate"]), axis=1
    )
    return assessed



def best_supplier_for_product(suppliers_df: pd.DataFrame, product_id: str) -> dict[str, str | float]:
    product_suppliers = suppliers_df[suppliers_df["product_id"] == product_id].copy()
    if product_suppliers.empty:
        return {
            "supplier_id": "N/A",
            "supplier_action": "No supplier available",
            "recommended_unit_cost": 0.0,
            "baseline_unit_cost": 0.0,
            "cost_reduction_per_unit": 0.0,
        }

    baseline_supplier = product_suppliers.sort_values("cost_per_unit", ascending=True).iloc[0]
    safe_suppliers = product_suppliers[product_suppliers["risk_level"] == "SAFE"]

    if safe_suppliers.empty:
        recommended = product_suppliers.sort_values("reliability_score", ascending=False).iloc[0]
        action = "No safe option; use highest reliability"
    else:
        recommended = safe_suppliers.sort_values(
            ["cost_per_unit", "reliability_score"], ascending=[True, False]
        ).iloc[0]
        if baseline_supplier["supplier_id"] != recommended["supplier_id"]:
            action = f"Switch to {recommended['supplier_id']}"
        else:
            action = f"Keep {recommended['supplier_id']}"

    baseline_cost = float(baseline_supplier["cost_per_unit"])
    recommended_cost = float(recommended["cost_per_unit"])

    return {
        "supplier_id": str(recommended["supplier_id"]),
        "supplier_action": action,
        "recommended_unit_cost": round(recommended_cost, 2),
        "baseline_unit_cost": round(baseline_cost, 2),
        "cost_reduction_per_unit": round(baseline_cost - recommended_cost, 2),
    }

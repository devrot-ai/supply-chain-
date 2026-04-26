from __future__ import annotations

from services.forecasting import forecast_by_product
from services.inventory import build_inventory_actions
from services.processing import aggregate_weekly_demand, prepare_data
from services.routing import fastest_route_between
from services.supplier import assess_suppliers, best_supplier_for_product
from services.data_loader import DataRepository



def generate_decisions(
    repo: DataRepository,
    forecast_method: str = "moving_average",
    safety_buffer: float = 20,
    source: str = "Warehouse-A",
    destination: str = "City-1",
) -> dict:
    cleaned = prepare_data(repo)
    demand_summary = aggregate_weekly_demand(cleaned.demand)
    forecast_df = forecast_by_product(cleaned.demand, method=forecast_method)
    inventory_actions = build_inventory_actions(cleaned.inventory, forecast_df, safety_buffer=safety_buffer)

    suppliers_assessed = assess_suppliers(cleaned.suppliers)
    route_plan = fastest_route_between(cleaned.routes, source=source, destination=destination)

    demand_lookup = demand_summary.set_index("product_id")["avg_weekly_demand"].to_dict()

    recommendations: list[dict] = []
    for _, row in inventory_actions.iterrows():
        product_id = str(row["product_id"])
        supplier_pick = best_supplier_for_product(suppliers_assessed, product_id)

        route_action = "Use optimized route"
        if route_plan["total_time_hr"] > 5:
            route_action = "Route slow; monitor delay risk"

        recommendations.append(
            {
                "product_id": product_id,
                "avg_weekly_demand": round(float(demand_lookup.get(product_id, 0.0)), 2),
                "predicted_demand": round(float(row["predicted_demand"]), 2),
                "current_stock": int(row["current_stock"]),
                "reorder_required": bool(row["reorder_required"]),
                "reorder_qty": int(row["reorder_qty"]),
                "supplier_id": supplier_pick["supplier_id"],
                "supplier_action": supplier_pick["supplier_action"],
                "recommended_unit_cost": supplier_pick["recommended_unit_cost"],
                "baseline_unit_cost": supplier_pick["baseline_unit_cost"],
                "cost_reduction_per_unit": supplier_pick["cost_reduction_per_unit"],
                "route_action": route_action,
            }
        )

    high_risk_suppliers = suppliers_assessed[suppliers_assessed["risk_level"] == "HIGH RISK"]
    alerts = {
        "high_risk_suppliers": high_risk_suppliers[
            ["supplier_id", "product_id", "delay_rate", "reliability_score"]
        ].to_dict(orient="records"),
        "reorder_alerts": [
            {
                "product_id": item["product_id"],
                "reorder_qty": item["reorder_qty"],
            }
            for item in recommendations
            if item["reorder_required"]
        ],
        "route_warning": route_plan["total_time_hr"] > 5,
    }

    return {
        "forecast_method": forecast_method,
        "route_recommendation": route_plan,
        "recommendations": recommendations,
        "alerts": alerts,
    }

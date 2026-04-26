from __future__ import annotations



def compute_operational_metrics(decision_output: dict) -> dict[str, float | int]:
    recommendations = decision_output["recommendations"]
    route_info = decision_output["route_recommendation"]

    reorder_units = int(sum(item["reorder_qty"] for item in recommendations))
    stockout_prevention_count = int(sum(1 for item in recommendations if item["reorder_required"]))

    cost_reduction = 0.0
    for item in recommendations:
        cost_reduction += item["cost_reduction_per_unit"] * item["reorder_qty"]

    direct_time = route_info["direct_time_hr"]
    optimized_time = route_info["total_time_hr"]
    delivery_time_saved = 0.0
    if direct_time != float("inf"):
        delivery_time_saved = round(max(0.0, direct_time - optimized_time), 2)

    return {
        "estimated_reorder_units": reorder_units,
        "stockout_prevention_count": stockout_prevention_count,
        "cost_reduction_estimate": round(cost_reduction, 2),
        "delivery_time_saved_hr": delivery_time_saved,
        "high_risk_supplier_count": len(decision_output["alerts"]["high_risk_suppliers"]),
    }

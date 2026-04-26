from __future__ import annotations

from services.data_loader import DataRepository



def simulate_disruption(
    repo: DataRepository,
    demand_spike_product: str | None = None,
    demand_spike_factor: float = 1.0,
    failed_supplier_id: str | None = None,
    route_delay_factor: float = 1.0,
) -> DataRepository:
    simulated = DataRepository(
        products=repo.products.copy(),
        demand=repo.demand.copy(),
        inventory=repo.inventory.copy(),
        suppliers=repo.suppliers.copy(),
        routes=repo.routes.copy(),
    )

    if demand_spike_product and demand_spike_factor > 1.0:
        mask = simulated.demand["product_id"] == demand_spike_product
        simulated.demand.loc[mask, "demand"] = simulated.demand.loc[mask, "demand"] * demand_spike_factor

    if failed_supplier_id:
        supplier_mask = simulated.suppliers["supplier_id"] == failed_supplier_id
        simulated.suppliers.loc[supplier_mask, "delay_rate"] = 0.8
        simulated.suppliers.loc[supplier_mask, "reliability_score"] = 0.3

    if route_delay_factor > 1.0:
        simulated.routes["avg_time_hr"] = simulated.routes["avg_time_hr"] * route_delay_factor

    simulated.build_indexes()
    return simulated

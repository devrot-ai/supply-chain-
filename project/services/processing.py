from __future__ import annotations

import pandas as pd

from services.data_loader import DataRepository



def prepare_data(repo: DataRepository) -> DataRepository:
    """Clean and normalize raw dataframes before intelligence engines run."""
    demand = repo.demand.copy()
    inventory = repo.inventory.copy()
    suppliers = repo.suppliers.copy()
    routes = repo.routes.copy()
    products = repo.products.copy()

    demand["date"] = pd.to_datetime(demand["date"], errors="coerce")
    demand["demand"] = pd.to_numeric(demand["demand"], errors="coerce").fillna(0)
    demand = demand.dropna(subset=["date", "product_id"])

    inventory["stock_level"] = pd.to_numeric(inventory["stock_level"], errors="coerce").fillna(0)
    suppliers["cost_per_unit"] = pd.to_numeric(suppliers["cost_per_unit"], errors="coerce").fillna(0)
    suppliers["delay_rate"] = pd.to_numeric(suppliers["delay_rate"], errors="coerce").fillna(0)
    suppliers["reliability_score"] = pd.to_numeric(suppliers["reliability_score"], errors="coerce").fillna(0)

    routes["distance_km"] = pd.to_numeric(routes["distance_km"], errors="coerce").fillna(0)
    routes["avg_time_hr"] = pd.to_numeric(routes["avg_time_hr"], errors="coerce").fillna(0)

    cleaned = DataRepository(
        products=products,
        demand=demand,
        inventory=inventory,
        suppliers=suppliers,
        routes=routes,
    )
    cleaned.build_indexes()
    return cleaned



def aggregate_weekly_demand(demand_df: pd.DataFrame) -> pd.DataFrame:
    weekly = (
        demand_df.groupby("product_id", as_index=False)["demand"]
        .mean()
        .rename(columns={"demand": "avg_weekly_demand"})
    )
    return weekly

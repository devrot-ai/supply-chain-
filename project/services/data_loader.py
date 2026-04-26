from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class DataRepository:
    products: pd.DataFrame
    demand: pd.DataFrame
    inventory: pd.DataFrame
    suppliers: pd.DataFrame
    routes: pd.DataFrame

    def build_indexes(self) -> None:
        """Build in-memory indexes for faster lookups in downstream engines."""
        self.products.set_index("product_id", inplace=True, drop=False)
        self.products.index = self.products.index.rename("product_key")
        self.inventory.set_index(["warehouse_id", "product_id"], inplace=True, drop=False)
        self.inventory.index = self.inventory.index.set_names(["warehouse_key", "product_key"])
        self.suppliers.set_index(["supplier_id", "product_id"], inplace=True, drop=False)
        self.suppliers.index = self.suppliers.index.set_names(["supplier_key", "product_key"])


def load_data(data_dir: str | Path) -> DataRepository:
    data_path = Path(data_dir)
    repo = DataRepository(
        products=pd.read_csv(data_path / "products.csv"),
        demand=pd.read_csv(data_path / "demand_history.csv"),
        inventory=pd.read_csv(data_path / "inventory.csv"),
        suppliers=pd.read_csv(data_path / "suppliers.csv"),
        routes=pd.read_csv(data_path / "routes.csv"),
    )
    repo.build_indexes()
    return repo

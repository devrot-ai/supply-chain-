from __future__ import annotations

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    demand_spike_product: str | None = Field(default=None, description="Product ID for demand spike")
    demand_spike_factor: float = Field(default=1.0, ge=1.0, le=5.0)
    failed_supplier_id: str | None = Field(default=None, description="Supplier ID to simulate failure")
    route_delay_factor: float = Field(default=1.0, ge=1.0, le=3.0)


class RecommendationResponse(BaseModel):
    scenario: str
    decisions: dict
    metrics: dict

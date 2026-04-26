from __future__ import annotations

from fastapi import FastAPI

from main import DATA_DIR, build_snapshot
from models.schemas import RecommendationResponse, SimulationRequest


app = FastAPI(title="Supply Chain Decision API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(method: str = "moving_average") -> dict:
    snapshot = build_snapshot(data_dir=DATA_DIR, forecast_method=method)
    return {
        "scenario": snapshot["scenario"],
        "decisions": snapshot["decisions"],
        "metrics": snapshot["metrics"],
    }


@app.post("/simulate", response_model=RecommendationResponse)
def simulate(payload: SimulationRequest) -> dict:
    snapshot = build_snapshot(
        data_dir=DATA_DIR,
        forecast_method="moving_average",
        simulation=payload.model_dump(exclude_none=True),
    )
    return {
        "scenario": snapshot["scenario"],
        "decisions": snapshot["decisions"],
        "metrics": snapshot["metrics"],
    }

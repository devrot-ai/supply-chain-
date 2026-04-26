from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from services.data_loader import load_data
from services.decision import generate_decisions
from services.metrics import compute_operational_metrics
from services.simulation import simulate_disruption


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"



def build_snapshot(
    data_dir: str | Path = DATA_DIR,
    forecast_method: str = "moving_average",
    simulation: dict | None = None,
) -> dict:
    repo = load_data(data_dir)

    scenario_name = "normal"
    if simulation:
        repo = simulate_disruption(repo=repo, **simulation)
        scenario_name = "simulated_disruption"

    decisions = generate_decisions(repo=repo, forecast_method=forecast_method)
    metrics = compute_operational_metrics(decisions)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "scenario": scenario_name,
        "decisions": decisions,
        "metrics": metrics,
    }


if __name__ == "__main__":
    snapshot = build_snapshot()
    print(json.dumps(snapshot, indent=2))

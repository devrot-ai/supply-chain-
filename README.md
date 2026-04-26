# Supply Chain Intelligence MVP

An end-to-end decision system built around one principle:

**Data -> Logic -> Decision -> Action**

This project ingests operational supply chain data, runs forecasting and optimization engines, and produces actionable recommendations through both an API and a live dashboard.

## Why This Project

Most demos stop at analytics. This one goes further:

- Predicts demand
- Detects inventory risk and reorder needs
- Flags risky suppliers
- Optimizes delivery routes
- Combines all of the above into one decision output
- Simulates disruptions to test resilience
- Tracks business-facing metrics (time saved, stockout prevention, cost impact)

## Architecture

The system follows a layered architecture:

1. Data Layer
2. Processing Layer
3. Intelligence Layer
4. Decision Engine
5. API Layer
6. Frontend Dashboard

Pipeline flow:

```text
CSV Data -> Pandas Processing -> Forecasting/Inventory/Routing/Risk Engines
-> Decision Engine -> API + Dashboard -> Actionable Recommendations
```

## Data Model (MVP)

Files under `data/`:

- `products.csv`: `product_id`, `name`, `category`
- `demand_history.csv`: `product_id`, `date`, `demand`
- `inventory.csv`: `warehouse_id`, `product_id`, `stock_level`
- `suppliers.csv`: `supplier_id`, `product_id`, `cost_per_unit`, `delay_rate`, `reliability_score`
- `routes.csv`: `source`, `destination`, `distance_km`, `avg_time_hr`

## Core Engines

### 1) Demand Forecasting

- Moving Average (default)
- Linear Regression (optional)

Output example:

- `P001 -> predicted_demand: 147.67`

### 2) Inventory Optimization

Reorder rule:

```text
Reorder Point = Predicted Demand + Safety Buffer
```

If stock is below reorder point, the engine returns reorder quantity.

### 3) Route Optimization

- Direct route baseline (distance/time sort)
- Dijkstra shortest-time route recommendation

Output includes selected path and estimated time saved vs direct route.

### 4) Supplier Risk Engine

Risk rule:

```text
HIGH RISK if delay_rate > 0.3 OR reliability_score < 0.6
```

Then the system selects the best available safe supplier (cost/reliability aware).

### 5) Decision Engine

Combines forecasting, stock status, supplier risk, and routing into one recommendation payload with alerts and operational metrics.

### 6) Simulation Engine

Supports disruption testing:

- Demand spike by product
- Supplier failure scenario
- Route delay multiplier

## Project Structure

```text
project/
├── api/
│   └── app.py
├── data/
│   ├── demand_history.csv
│   ├── inventory.csv
│   ├── products.csv
│   ├── routes.csv
│   └── suppliers.csv
├── frontend/
│   └── app.py
├── models/
│   └── schemas.py
├── services/
│   ├── data_loader.py
│   ├── decision.py
│   ├── forecasting.py
│   ├── inventory.py
│   ├── metrics.py
│   ├── processing.py
│   ├── routing.py
│   ├── simulation.py
│   └── supplier.py
├── main.py
├── requirements.txt
└── README.md
```

## Tech Stack

- Python 3.11+
- Pandas, NumPy, Scikit-learn
- FastAPI + Uvicorn
- Streamlit + Altair

## Setup

From the `project/` folder:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run Locally

### Run decision engine (CLI)

```bash
python main.py
```

### Run API

```bash
uvicorn api.app:app --reload
```

API endpoints:

- `GET /health`
- `GET /recommendations?method=moving_average`
- `GET /recommendations?method=linear_regression`
- `POST /simulate`

Sample simulation payload:

```json
{
  "demand_spike_product": "P001",
  "demand_spike_factor": 1.8,
  "failed_supplier_id": "S1",
  "route_delay_factor": 1.4
}
```

Example with `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/simulate" \
  -H "Content-Type: application/json" \
  -d "{\"demand_spike_product\":\"P001\",\"demand_spike_factor\":1.8,\"failed_supplier_id\":\"S1\",\"route_delay_factor\":1.4}"
```

### Run dashboard

```bash
streamlit run frontend/app.py
```

Dashboard includes:

- Inventory Panel (stock, demand, reorder alerts)
- Demand Graph (actual vs forecast)
- Alerts Panel (supplier risk and route warnings)
- Recommendations Panel (reorder + supplier + route actions)
- Simulate disruption controls in sidebar

## Demo Flow

1. Start with normal operations view.
2. Observe baseline recommendations.
3. Trigger `Simulate disruption` from the dashboard sidebar.
4. Show how supplier/route/inventory recommendations change in real time.
5. Compare metric shifts (time saved, stockout prevention, estimated cost impact).

## Metrics Tracked

- `estimated_reorder_units`
- `stockout_prevention_count`
- `cost_reduction_estimate`
- `delivery_time_saved_hr`
- `high_risk_supplier_count`

## Known Notes

- This is an MVP using CSV files, not a production database.
- If `pip` reports unrelated package conflicts from your global Python setup, create/use a clean virtual environment and reinstall requirements.

## Next Improvements

- Replace CSV with Postgres and scheduled ingestion.
- Add model versioning for forecasts.
- Add automated tests for each service layer.
- Add auth and role-based access for API endpoints.
- Add multi-warehouse, multi-destination scenario planner.

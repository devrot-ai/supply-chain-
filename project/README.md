# Supply Chain Intelligence MVP

This project implements a complete **Data -> Logic -> Decision -> Action** system:

- Data Layer
- Processing Layer
- Forecasting, Inventory, Routing, Supplier Risk Engines
- Decision Engine
- FastAPI Layer
- Streamlit Dashboard
- Simulation and Metrics Engine

## Project Structure

```text
project/
├── data/
├── models/
├── services/
│   ├── data_loader.py
│   ├── processing.py
│   ├── forecasting.py
│   ├── inventory.py
│   ├── routing.py
│   ├── supplier.py
│   ├── decision.py
│   ├── simulation.py
│   └── metrics.py
├── api/
│   └── app.py
├── frontend/
│   └── app.py
├── main.py
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Decision Engine (CLI)

```bash
python main.py
```

## Run API

```bash
uvicorn api.app:app --reload
```

Endpoints:

- `GET /health`
- `GET /recommendations?method=moving_average`
- `POST /simulate`

Sample payload for `/simulate`:

```json
{
  "demand_spike_product": "P001",
  "demand_spike_factor": 1.8,
  "failed_supplier_id": "S1",
  "route_delay_factor": 1.4
}
```

## Run Dashboard

```bash
streamlit run frontend/app.py
```

## Final Demo Flow

1. Open dashboard and view normal operations.
2. Click **Simulate disruption** in sidebar.
3. Observe updated recommendations and alerts.
4. Compare metrics like time saved and stockout prevention.

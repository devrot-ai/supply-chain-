from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from main import build_snapshot
from services.data_loader import load_data
from services.forecasting import forecast_by_product
from services.processing import prepare_data


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


st.set_page_config(page_title="Supply Chain Intelligence Dashboard", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    .main {
        background: radial-gradient(circle at 10% 10%, #d4f4dd 0%, #fef6d7 45%, #d8ecff 100%);
    }
    .hero {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 16px;
        padding: 1rem 1.25rem;
        box-shadow: 0 12px 30px rgba(20, 30, 40, 0.08);
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }
    .hero p {
        margin: 0.35rem 0 0;
        font-family: 'IBM Plex Mono', monospace;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Data -> Logic -> Decision -> Action</h1>
        <p>Forecast demand, optimize inventory, detect supplier risk, and route deliveries with live recommendations.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

forecast_method = st.sidebar.selectbox(
    "Forecast Method", ["moving_average", "linear_regression"], index=0
)

repo = prepare_data(load_data(DATA_DIR))
products = sorted(repo.products["product_id"].tolist())
suppliers = sorted(repo.suppliers["supplier_id"].unique().tolist())

spike_product = st.sidebar.selectbox("Demand Spike Product", ["None"] + products)
spike_factor = st.sidebar.slider("Demand Spike Factor", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
failed_supplier = st.sidebar.selectbox("Fail Supplier", ["None"] + suppliers)
route_delay_factor = st.sidebar.slider("Route Delay Factor", min_value=1.0, max_value=2.0, value=1.3, step=0.1)

run_simulation = st.sidebar.button("Simulate disruption")

simulation_payload = None
if run_simulation:
    simulation_payload = {
        "demand_spike_product": None if spike_product == "None" else spike_product,
        "demand_spike_factor": spike_factor,
        "failed_supplier_id": None if failed_supplier == "None" else failed_supplier,
        "route_delay_factor": route_delay_factor,
    }

snapshot = build_snapshot(
    data_dir=DATA_DIR,
    forecast_method=forecast_method,
    simulation=simulation_payload,
)

recommendations_df = pd.DataFrame(snapshot["decisions"]["recommendations"])
metrics = snapshot["metrics"]
alerts = snapshot["decisions"]["alerts"]
route_info = snapshot["decisions"]["route_recommendation"]

metric_cols = st.columns(4)
metric_cols[0].metric("Reorder Units", int(metrics["estimated_reorder_units"]))
metric_cols[1].metric("Stockouts Prevented", int(metrics["stockout_prevention_count"]))
metric_cols[2].metric("Delivery Time Saved (hr)", float(metrics["delivery_time_saved_hr"]))
metric_cols[3].metric("Cost Reduction Estimate", float(metrics["cost_reduction_estimate"]))

left, right = st.columns([1.4, 1])

with left:
    st.subheader("Inventory Panel")
    inventory_view = recommendations_df[
        ["product_id", "current_stock", "predicted_demand", "reorder_required", "reorder_qty"]
    ].copy()
    inventory_view["alert"] = inventory_view["reorder_required"].map({True: "RED", False: "GREEN"})
    st.dataframe(inventory_view, use_container_width=True)

    st.subheader("Demand Graph")
    selected_product = st.selectbox("Product", products, index=0)
    product_demand = repo.demand[repo.demand["product_id"] == selected_product].sort_values("date")
    forecast_value = float(
        forecast_by_product(repo.demand, method=forecast_method)
        .set_index("product_id")
        .loc[selected_product, "predicted_demand"]
    )
    forecast_date = product_demand["date"].max() + pd.Timedelta(days=1)

    actual_chart_df = product_demand[["date", "demand"]].copy()
    actual_chart_df["type"] = "actual"

    forecast_chart_df = pd.DataFrame(
        [{"date": forecast_date, "demand": forecast_value, "type": "forecast"}]
    )

    chart_df = pd.concat([actual_chart_df, forecast_chart_df], ignore_index=True)
    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("demand:Q", title="Units"),
            color=alt.Color("type:N", scale=alt.Scale(range=["#0e7490", "#ea580c"])),
            strokeDash="type:N",
            tooltip=["date:T", "demand:Q", "type:N"],
        )
    )
    st.altair_chart(chart, use_container_width=True)

with right:
    st.subheader("Alerts Panel")
    st.write(f"Scenario: **{snapshot['scenario']}**")

    if alerts["high_risk_suppliers"]:
        st.error("High-risk suppliers detected")
        st.dataframe(pd.DataFrame(alerts["high_risk_suppliers"]), use_container_width=True)
    else:
        st.success("No high-risk suppliers")

    if alerts["reorder_alerts"]:
        st.warning("Reorder actions required")
        st.dataframe(pd.DataFrame(alerts["reorder_alerts"]), use_container_width=True)
    else:
        st.success("No reorder alert")

    st.info(
        " -> ".join(route_info["path"]) + f" | total time: {route_info['total_time_hr']} hr"
        if route_info["path"]
        else "No route available"
    )

st.subheader("Recommendations Panel")
st.dataframe(
    recommendations_df[
        [
            "product_id",
            "reorder_required",
            "reorder_qty",
            "supplier_id",
            "supplier_action",
            "route_action",
        ]
    ],
    use_container_width=True,
)

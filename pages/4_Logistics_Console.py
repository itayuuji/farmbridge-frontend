import numpy as np
import pandas as pd
import streamlit as st

from mock_data import init_state, AREAS, LOGISTICS_PARTNERS, advance_status

st.set_page_config(page_title="Logistics Console · FarmBridge", page_icon="🚚", layout="wide")
init_state()

st.title("🚚 Logistics Console")

partner = st.sidebar.selectbox("Logged in as (mock login)", LOGISTICS_PARTNERS)

tab_tasks, tab_route = st.tabs(["My Tasks", "Route Optimization Demo"])

# ---------------- tasks ----------------
with tab_tasks:
    tasks = st.session_state.logistics_tasks
    mine = tasks[tasks["assigned_to"] == partner]
    if mine.empty:
        st.info("No tasks assigned to you right now.")
    else:
        for _, task in mine.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.markdown(f"**{task['task_id']}** — {task['order_id']}")
                c1.caption(f"Pickup: {task['pickup_area']} → Drop: {task['drop_area']}")
                c2.progress(
                    (["Created", "Confirmed", "Ready", "Picked Up", "Out for Delivery", "Delivered"]
                     .index(task["status"]) + 1) / 6,
                    text=task["status"],
                )
                if task["status"] != "Delivered":
                    if c3.button("Update status", key=f"upd_{task['task_id']}"):
                        advance_status(task["order_id"])
                        st.rerun()

# ---------------- route optimization demo ----------------
with tab_route:
    st.markdown("#### Optimized pickup/delivery sequence")
    st.caption(
        "Demo only: random stop coordinates are generated for a set of pickups, "
        "then compared **unsorted** vs a **nearest-neighbor route** — a simplified "
        "stand-in for a real OR-Tools Vehicle Routing Problem solve."
    )

    n_stops = st.slider("Number of stops in this run", 3, 10, 6)

    if "route_seed" not in st.session_state or st.button("🎲 Generate new stops"):
        st.session_state.route_seed = np.random.default_rng().integers(0, 100000)

    rng = np.random.default_rng(st.session_state.route_seed)
    base_lat, base_lon = 19.076, 72.877  # Mumbai-area anchor for the demo
    lats = base_lat + rng.uniform(-0.15, 0.15, n_stops)
    lons = base_lon + rng.uniform(-0.15, 0.15, n_stops)
    labels = [f"Stop {i+1} ({AREAS[i % len(AREAS)]})" for i in range(n_stops)]
    coords = list(zip(lats, lons))

    def total_distance(order):
        d = 0.0
        for i in range(len(order) - 1):
            (x1, y1), (x2, y2) = coords[order[i]], coords[order[i + 1]]
            d += np.hypot(x1 - x2, y1 - y2)
        return d

    unsorted_order = list(range(n_stops))

    # naive nearest-neighbor heuristic starting from stop 0
    remaining = set(range(1, n_stops))
    nn_order = [0]
    while remaining:
        last = nn_order[-1]
        nxt = min(remaining, key=lambda j: np.hypot(
            coords[last][0] - coords[j][0], coords[last][1] - coords[j][1]))
        nn_order.append(nxt)
        remaining.remove(nxt)

    dist_before = total_distance(unsorted_order)
    dist_after = total_distance(nn_order)
    saved_pct = (dist_before - dist_after) / dist_before * 100 if dist_before else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Unoptimized distance (relative units)", f"{dist_before:.3f}")
    c2.metric("Optimized distance (relative units)", f"{dist_after:.3f}")
    c3.metric("Distance saved", f"{saved_pct:.0f}%")

    st.markdown("**Before optimization (visit order as received)**")
    before_df = pd.DataFrame({
        "lat": [coords[i][0] for i in unsorted_order],
        "lon": [coords[i][1] for i in unsorted_order],
    })
    st.map(before_df, size=40)

    st.markdown("**After optimization (nearest-neighbor route)**")
    after_df = pd.DataFrame({
        "lat": [coords[i][0] for i in nn_order],
        "lon": [coords[i][1] for i in nn_order],
    })
    st.map(after_df, size=40)

    st.markdown("**Stop sequence**")
    seq_df = pd.DataFrame({
        "Order received (unoptimized)": [labels[i] for i in unsorted_order],
        "Optimized sequence": [labels[i] for i in nn_order],
    })
    st.dataframe(seq_df, use_container_width=True, hide_index=True)

    st.caption(
        "Production version: model pickup hubs and buyers as nodes with capacity "
        "and time-window constraints, then solve with Google OR-Tools (VRP)."
    )

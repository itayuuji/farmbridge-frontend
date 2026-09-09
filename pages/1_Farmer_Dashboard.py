from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

from mock_data import init_state, FARMER_NAMES, FPO_NAMES, CROPS, AREAS, advance_status

st.set_page_config(page_title="Farmer Dashboard · FarmBridge", page_icon="👨‍🌾", layout="wide")
init_state()

st.title("👨‍🌾 Farmer / FPO Dashboard")

st.session_state.current_farmer = st.sidebar.selectbox(
    "Logged in as (mock login)", FARMER_NAMES + FPO_NAMES,
    index=(FARMER_NAMES + FPO_NAMES).index(st.session_state.current_farmer),
)
farmer = st.session_state.current_farmer

tab_listings, tab_add, tab_demand, tab_orders = st.tabs(
    ["My Listings", "Add Produce", "Demand & Price Signal", "Incoming Orders"]
)

# ---------------- My listings ----------------
with tab_listings:
    my = st.session_state.listings[st.session_state.listings["farmer"] == farmer]
    if my.empty:
        st.info("No listings yet — add your first one in the **Add Produce** tab.")
    else:
        st.dataframe(my, use_container_width=True, hide_index=True)

# ---------------- Add produce ----------------
with tab_add:
    st.markdown("#### Create a listing")
    with st.form("add_produce"):
        c1, c2, c3 = st.columns(3)
        crop = c1.selectbox("Crop", CROPS)
        variety = c2.selectbox("Variety", ["Local", "Hybrid", "Desi", "Premium"])
        grade = c3.selectbox("Quality grade", ["A", "B", "C"])
        c4, c5, c6 = st.columns(3)
        qty = c4.number_input("Quantity (kg)", min_value=1, value=100)
        price = c5.number_input("Price per kg (₹)", min_value=1.0, value=20.0, step=0.5)
        area = c6.selectbox("Service area", AREAS)
        c7, c8 = st.columns(2)
        harvest_date = c7.date_input("Harvest date", value=date.today())
        available_from = c8.date_input("Available from", value=date.today())
        photo = st.file_uploader("Lot photo (optional, evidence for trust/quality)",
                                  type=["png", "jpg", "jpeg"])
        offline = st.checkbox(
            "📴 Save as offline draft (simulates no connectivity — sync later)"
        )
        submitted = st.form_submit_button("Save draft" if offline else "Publish listing",
                                           use_container_width=True)

        if submitted:
            new_row = {
                "listing_id": f"L{len(st.session_state.listings) + len(st.session_state.drafts) + 1:03d}",
                "farmer": farmer, "crop": crop, "variety": variety,
                "quantity_kg": qty, "unit_price": price,
                "harvest_date": harvest_date, "available_from": available_from,
                "area": area, "quality_grade": grade, "verified": False,
            }
            if offline:
                st.session_state.drafts.append(new_row)
                st.warning("Saved locally as an offline draft. Sync when back online "
                           "(see button below).")
            else:
                st.session_state.listings = pd.concat(
                    [st.session_state.listings, pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                st.success(f"Listing published: {qty} kg of {crop} ({variety}).")

    if st.session_state.drafts:
        st.markdown("---")
        st.markdown(f"**📴 Offline drafts pending sync: {len(st.session_state.drafts)}**")
        st.dataframe(pd.DataFrame(st.session_state.drafts), use_container_width=True,
                     hide_index=True)
        if st.button("🔄 Sync drafts now"):
            st.session_state.listings = pd.concat(
                [st.session_state.listings, pd.DataFrame(st.session_state.drafts)],
                ignore_index=True,
            )
            st.session_state.drafts = []
            st.success("All drafts synced and published.")
            st.rerun()

# ---------------- Demand / price signal ----------------
with tab_demand:
    st.markdown("#### Demand & price signal for your crops")
    st.caption("Simulated trend based on recent seeded activity — a stand-in for "
               "the real demand-forecast model (see AI Insights page).")
    my_crops = st.session_state.listings[st.session_state.listings["farmer"] == farmer]["crop"].unique()
    crop_pick = st.selectbox("Crop", my_crops if len(my_crops) else CROPS)
    hist = st.session_state.demand_history.get(crop_pick)
    if hist is not None:
        chart_df = pd.DataFrame({"day": np.arange(1, len(hist) + 1), "demand_kg": hist})
        st.line_chart(chart_df, x="day", y="demand_kg")
        recent = hist[-7:].mean()
        prior = hist[-14:-7].mean()
        delta = (recent - prior) / prior * 100
        st.metric(f"7-day nearby demand for {crop_pick}", f"{recent:.0f} kg/day",
                   f"{delta:+.0f}% vs previous week")
        if delta > 5:
            st.success("Demand is trending up nearby — a good time to list more.")
        elif delta < -5:
            st.warning("Demand is softening nearby — consider group/bulk offers.")

# ---------------- Incoming orders ----------------
with tab_orders:
    st.markdown("#### Orders against your listings")
    st.caption("Demo linkage: showing a sample of platform orders as if matched "
               "to this farmer's lots.")
    sample_orders = st.session_state.orders.sample(
        min(4, len(st.session_state.orders)), random_state=hash(farmer) % 1000
    )
    for _, o in sample_orders.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.markdown(f"**{o['order_id']}** — {o['crop']} · {o['quantity_kg']} kg")
            c1.caption(f"Buyer: {o['buyer']}")
            c2.progress(
                (["Created", "Confirmed", "Ready", "Picked Up", "Out for Delivery", "Delivered"]
                 .index(o["status"]) + 1) / 6,
                text=o["status"],
            )
            # fairness meter
            fig_data = pd.DataFrame({
                "component": ["Farmer amount", "Logistics fee", "Service fee"],
                "amount": [o["farmer_amount"], o["logistics_fee"], o["service_fee"]],
            })
            c3.caption("Fairness meter")
            c3.bar_chart(fig_data.set_index("component"))
            if o["status"] != "Delivered":
                if c3.button("Advance status", key=f"adv_{o['order_id']}"):
                    advance_status(o["order_id"])
                    st.rerun()

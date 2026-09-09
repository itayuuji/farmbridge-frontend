from datetime import date

import pandas as pd
import streamlit as st

from mock_data import init_state, CROPS, AREAS, BUYER_NAMES

st.set_page_config(page_title="Bulk Buyer Console · FarmBridge", page_icon="🏢", layout="wide")
init_state()

st.title("🏢 Bulk Buyer / Retailer Console")

buyer = st.sidebar.selectbox("Logged in as (mock login)", BUYER_NAMES)

tab_post, tab_browse, tab_mine = st.tabs(
    ["Post Demand", "Browse Verified Lots", "My Recurring Demands"]
)

with tab_post:
    st.markdown("#### Post recurring or one-off demand")
    with st.form("post_demand"):
        c1, c2, c3 = st.columns(3)
        crop = c1.selectbox("Crop", CROPS)
        qty = c2.number_input("Quantity needed (kg)", min_value=10, value=200)
        area = c3.selectbox("Delivery area", AREAS)
        req_date = st.date_input("Required by", value=date.today())
        recurring = st.checkbox("Recurring order (e.g. weekly)")
        submitted = st.form_submit_button("Post demand", use_container_width=True)
        if submitted:
            new_demand = {
                "demand_id": f"D{len(st.session_state.demands) + 1:03d}",
                "buyer": buyer, "crop": crop, "quantity_kg": qty,
                "required_date": req_date, "delivery_area": area,
            }
            st.session_state.demands = pd.concat(
                [st.session_state.demands, pd.DataFrame([new_demand])],
                ignore_index=True,
            )
            st.success(
                f"Demand posted for {qty} kg of {crop}" +
                (" (recurring)." if recurring else ".")
            )

with tab_browse:
    st.markdown("#### Harvest-to-Demand Matching")
    st.caption("Verified lots that can plausibly cover your open demand, ranked by "
               "match on crop, area and quantity.")
    open_demand = st.session_state.demands[st.session_state.demands["buyer"] == buyer]
    if open_demand.empty:
        st.info("Post a demand first to see matching lots.")
    else:
        for _, d in open_demand.iterrows():
            st.markdown(f"**Matches for {d['demand_id']}: {d['quantity_kg']} kg {d['crop']} "
                        f"in {d['delivery_area']}**")
            matches = st.session_state.listings[
                (st.session_state.listings["crop"] == d["crop"]) &
                (st.session_state.listings["verified"])
            ].sort_values("quantity_kg", ascending=False)
            if matches.empty:
                st.warning("No verified lots currently match — consider aggregation "
                            "across smaller farmers.")
            else:
                st.dataframe(matches[["farmer", "quantity_kg", "unit_price",
                                       "quality_grade", "area"]],
                             use_container_width=True, hide_index=True)
                if st.button("Confirm & schedule fulfillment", key=f"confirm_{d['demand_id']}"):
                    st.success("Fulfillment scheduled (demo) — logistics task created.")

with tab_mine:
    mine = st.session_state.demands[st.session_state.demands["buyer"] == buyer]
    if mine.empty:
        st.info("No demands posted yet.")
    else:
        st.dataframe(mine, use_container_width=True, hide_index=True)

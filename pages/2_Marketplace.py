import pandas as pd
import streamlit as st

from mock_data import init_state, CROPS, AREAS

st.set_page_config(page_title="Marketplace · FarmBridge", page_icon="🛒", layout="wide")
init_state()

st.title("🛒 Marketplace")
st.caption("Discover nearby produce, compare price and delivery, order directly "
           "or join a group order.")

listings = st.session_state.listings

with st.sidebar:
    st.markdown("### Filters")
    area = st.selectbox("Your area", ["Any"] + AREAS)
    crop_filter = st.multiselect("Crop", CROPS)
    max_price = st.slider("Max price per kg (₹)", 5, 50, 50)
    verified_only = st.checkbox("Verified listings only", value=False)

filtered = listings.copy()
if area != "Any":
    filtered = filtered[filtered["area"] == area]
if crop_filter:
    filtered = filtered[filtered["crop"].isin(crop_filter)]
filtered = filtered[filtered["unit_price"] <= max_price]
if verified_only:
    filtered = filtered[filtered["verified"]]

st.markdown(f"**{len(filtered)} lots found**")

# ---------------- group orders (community aggregation) ----------------
with st.expander("👥 Group Buying — combine demand with neighbors to cut delivery cost"):
    st.write(
        "Your housing society / apartment can combine individual orders into one "
        "delivery. Below is a simulated open group order you can join."
    )
    g1, g2, g3 = st.columns(3)
    g1.metric("Group order", "Sunrise Society — Tomato 60kg")
    g2.metric("Members joined", "7 / 12 needed")
    g3.metric("Est. delivery saving", "₹4 / kg")
    st.button("Join this group order")

st.divider()

for _, row in filtered.iterrows():
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        c1.markdown("🥬" if row["crop"] not in ("Mango", "Banana") else "🍌")
        c2.markdown(f"**{row['crop']} ({row['variety']})** — {row['farmer']}")
        badges = f"Grade {row['quality_grade']} · {row['area']}"
        if row["verified"]:
            badges += " · ✅ Verified"
        c2.caption(badges)
        c2.caption(f"Harvested {row['harvest_date']} · Available from {row['available_from']}")

        farmer_amt = row["unit_price"]
        logistics = round(farmer_amt * 0.08, 1)
        service = round(farmer_amt * 0.05, 1)
        total = round(farmer_amt + logistics + service, 1)

        c3.metric("Price / kg", f"₹{total}")
        with c3.popover("Price breakup"):
            st.write(f"Farmer amount: ₹{farmer_amt}")
            st.write(f"Logistics fee: ₹{logistics}")
            st.write(f"Service fee: ₹{service}")
            st.write(f"**Buyer total: ₹{total}**")

        qty = c3.number_input("Qty (kg)", min_value=1,
                               max_value=int(row["quantity_kg"]), value=1,
                               key=f"qty_{row['listing_id']}")
        if c3.button("Add to cart", key=f"add_{row['listing_id']}"):
            st.session_state.cart.append({
                "listing_id": row["listing_id"], "crop": row["crop"],
                "farmer": row["farmer"], "qty": qty, "unit_total": total,
            })
            st.toast(f"Added {qty} kg {row['crop']} to cart")

st.divider()
st.markdown("### 🧺 Your cart")
if not st.session_state.cart:
    st.info("Cart is empty — add produce above.")
else:
    cart_df = pd.DataFrame(st.session_state.cart)
    cart_df["line_total"] = cart_df["qty"] * cart_df["unit_total"]
    st.dataframe(cart_df, use_container_width=True, hide_index=True)
    st.metric("Cart total", f"₹{cart_df['line_total'].sum():.0f}")
    c1, c2 = st.columns(2)
    if c1.button("Place order", type="primary", use_container_width=True):
        new_orders = []
        for _, item in cart_df.iterrows():
            new_orders.append({
                "order_id": f"O{len(st.session_state.orders) + len(new_orders) + 1:04d}",
                "buyer": "Household Consumer", "crop": item["crop"],
                "quantity_kg": item["qty"], "status": "Created",
                "farmer_amount": item["unit_total"] * 0.87 * item["qty"],
                "logistics_fee": item["unit_total"] * 0.08 * item["qty"],
                "service_fee": item["unit_total"] * 0.05 * item["qty"],
                "total": item["line_total"],
            })
        st.session_state.orders = pd.concat(
            [st.session_state.orders, pd.DataFrame(new_orders)], ignore_index=True
        )
        st.session_state.cart = []
        st.success("Order placed! Track it from the order-status view below next visit.")
        st.rerun()
    if c2.button("Clear cart", use_container_width=True):
        st.session_state.cart = []
        st.rerun()

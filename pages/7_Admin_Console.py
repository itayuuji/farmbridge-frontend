import streamlit as st

from mock_data import init_state

st.set_page_config(page_title="Admin Console · FarmBridge", page_icon="🛡️", layout="wide")
init_state()

st.title("🛡️ Admin Console")

tab_verify, tab_listings, tab_disputes, tab_txn = st.tabs(
    ["Verify Users", "Moderate Listings", "Disputes", "Transactions Monitor"]
)

with tab_verify:
    users = st.session_state.users
    pending = users[users["status"] == "Pending"]
    st.markdown(f"**{len(pending)} account(s) pending verification**")
    for i, u in pending.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"**{u['name']}** — {u['role']}")
            if c2.button("Approve", key=f"appr_{i}"):
                st.session_state.users.loc[i, "status"] = "Verified"
                st.rerun()
            if c3.button("Reject", key=f"rej_{i}"):
                st.session_state.users.loc[i, "status"] = "Rejected"
                st.rerun()
    st.markdown("---")
    st.markdown("**All users**")
    st.dataframe(users, use_container_width=True, hide_index=True)

with tab_listings:
    listings = st.session_state.listings
    unverified = listings[~listings["verified"]]
    st.markdown(f"**{len(unverified)} listing(s) awaiting verification**")
    if unverified.empty:
        st.success("All current listings are verified.")
    else:
        st.dataframe(unverified, use_container_width=True, hide_index=True)
        pick = st.selectbox("Select listing to verify", unverified["listing_id"])
        if st.button("✅ Mark verified"):
            idx = listings.index[listings["listing_id"] == pick]
            listings.loc[idx, "verified"] = True
            st.success(f"{pick} marked verified.")
            st.rerun()

with tab_disputes:
    st.info("No open disputes in this demo session.")
    with st.form("raise_dispute"):
        st.write("Log a demo dispute (for judges to see the workflow):")
        order_id = st.selectbox("Order", st.session_state.orders["order_id"])
        reason = st.text_area("Reason")
        if st.form_submit_button("Log dispute"):
            st.warning(f"Dispute logged for {order_id}: {reason or '(no reason given)'} "
                       "— routed to admin queue (demo).")

with tab_txn:
    st.markdown("#### All transactions")
    st.dataframe(st.session_state.orders, use_container_width=True, hide_index=True)
    st.metric("Gross transaction value (demo)",
              f"₹{st.session_state.orders['total'].sum():,.0f}")

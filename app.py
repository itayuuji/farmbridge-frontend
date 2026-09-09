import streamlit as st

from mock_data import init_state, t, LANGUAGES

st.set_page_config(page_title="FarmBridge", page_icon="🌾", layout="wide")
init_state()

# ---------- sidebar: language + role shortcuts ----------
with st.sidebar:
    st.markdown("### 🌾 FarmBridge")
    st.session_state.lang = st.selectbox(
        "Language / भाषा", list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.lang),
    )
    st.caption("Multilingual-ready UI — demo covers 3 languages; more can be "
               "added via a strings dictionary.")
    st.divider()
    st.caption("SIH26033 · Frontend prototype (Streamlit) · Mock data only")

texts = t()

# ---------- hero ----------
st.title("🌾 FarmBridge")
st.subheader(texts["tagline"])
st.write(
    "**Problem statement:** \u201cMultiple intermediaries reduce farmers "
    "earnings and increase consumer prices.\u201d — SIH26033"
)
st.info(f"**Pitch:** {texts['pitch']}")

st.divider()

# ---------- quick impact snapshot ----------
orders = st.session_state.orders
listings = st.session_state.listings

col1, col2, col3, col4 = st.columns(4)
col1.metric("Active listings", len(listings))
col2.metric("Orders in flight", int((orders["status"] != "Delivered").sum()))
col3.metric("Verified farmers/FPOs", int(listings["verified"].sum()))
avg_farmer_share = (orders["farmer_amount"] / orders["total"]).mean() * 100
col4.metric("Avg. farmer share of price", f"{avg_farmer_share:.0f}%")

st.divider()

# ---------- role picker ----------
st.markdown("### Choose your role to open the matching workspace")
st.caption("This is a frontend prototype — pick a role below, or use the "
           "sidebar page list, to explore that user's journey.")

roles = [
    ("👨‍🌾", "Farmer / FPO", "List produce, see demand signals, accept orders.",
     "pages/1_Farmer_Dashboard.py"),
    ("🛒", "Consumer", "Discover nearby produce, compare price, order or join a group buy.",
     "pages/2_Marketplace.py"),
    ("🏢", "Bulk Buyer", "Post recurring demand, confirm verified lots.",
     "pages/3_Bulk_Buyer_Console.py"),
    ("🚚", "Logistics Partner", "View tasks, run the route-optimization demo.",
     "pages/4_Logistics_Console.py"),
    ("🤖", "AI Insights", "Demand forecasting, route optimization, voice-to-listing demos.",
     "pages/5_AI_Insights.py"),
    ("📊", "Impact Dashboard", "Track the metrics judges care about.",
     "pages/6_Impact_Dashboard.py"),
    ("🛡️", "Admin", "Verify users/listings, monitor disputes and transactions.",
     "pages/7_Admin_Console.py"),
]

cols = st.columns(4)
for i, (icon, name, desc, page) in enumerate(roles):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"#### {icon} {name}")
            st.caption(desc)
            try:
                st.page_link(page, label=f"Open {name}", icon="➡️")
            except Exception:
                st.write(f"Open via sidebar → **{name}**")

st.divider()
st.caption(
    "Note: this build is the **frontend only**, in Python + Streamlit, using "
    "seeded demo data held in session state. There is no real backend, "
    "database, payment gateway or trained ML model behind it — every "
    "AI/forecast/route output is clearly labelled as simulated, per the "
    "SIH26033 blueprint's guidance to keep prototype data transparent."
)

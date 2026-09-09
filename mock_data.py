"""
FarmBridge — shared mock/demo data and session-state helpers.
This is a FRONTEND-ONLY prototype: there is no real backend, database or ML
model. All data lives in st.session_state (in-memory, per browser session)
and every "AI" output is a clearly-labelled simulated/demo value, in line
with the SIH26033 blueprint's guidance to use transparent, labelled
prototype data.
"""

import random
from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st

RNG = random.Random(42)
NP_RNG = np.random.default_rng(42)

LANGUAGES = {
    "English": {
        "tagline": "From Farm to Buyer, With Fewer Barriers.",
        "pitch": "FarmBridge does not merely connect a farmer to a buyer. "
                 "It coordinates demand, aggregation and delivery so direct "
                 "trade can actually work at scale.",
    },
    "हिन्दी (Hindi)": {
        "tagline": "खेत से खरीदार तक, कम बाधाओं के साथ।",
        "pitch": "FarmBridge केवल किसान को खरीदार से नहीं जोड़ता — यह मांग, "
                 "एकत्रीकरण और डिलीवरी का समन्वय करता है ताकि सीधा व्यापार "
                 "बड़े पैमाने पर सफल हो सके।",
    },
    "मराठी (Marathi)": {
        "tagline": "शेतापासून खरेदीदारापर्यंत, कमी अडथळ्यांसह.",
        "pitch": "FarmBridge फक्त शेतकऱ्याला खरेदीदाराशी जोडत नाही — ते मागणी, "
                 "एकत्रीकरण आणि वितरण यांचे समन्वय साधते.",
    },
}

CROPS = ["Tomato", "Onion", "Potato", "Okra", "Brinjal", "Spinach",
         "Cauliflower", "Mango", "Banana", "Green Chilli"]

AREAS = ["Nashik North", "Nashik South", "Pune East", "Pune West",
         "Thane Rural", "Nagpur Belt"]

FARMER_NAMES = ["Ramesh Patil", "Sunita Jadhav", "Vinod Shinde",
                 "Anita Kale", "Ganesh More", "Kavita Pawar"]

FPO_NAMES = ["Sahyadri Farmers FPO", "Godavari Growers Collective"]

BUYER_NAMES = ["Green Basket Retail", "CityMart Wholesale",
                "Sunrise Housing Society", "Fresh Table Hotels"]

LOGISTICS_PARTNERS = ["Ankit (Rider #12)", "Priya (Rider #07)",
                       "FastVan Logistics"]

ORDER_STATUSES = ["Created", "Confirmed", "Ready", "Picked Up",
                   "Out for Delivery", "Delivered"]


def _seed_listings():
    rows = []
    for i in range(14):
        crop = RNG.choice(CROPS)
        farmer = RNG.choice(FARMER_NAMES + FPO_NAMES)
        qty = RNG.choice([50, 80, 100, 150, 200, 300, 500])
        price = round(RNG.uniform(8, 45), 1)
        rows.append({
            "listing_id": f"L{i+1:03d}",
            "farmer": farmer,
            "crop": crop,
            "variety": RNG.choice(["Local", "Hybrid", "Desi", "Premium"]),
            "quantity_kg": qty,
            "unit_price": price,
            "harvest_date": date.today() - timedelta(days=RNG.randint(0, 5)),
            "available_from": date.today() + timedelta(days=RNG.randint(0, 2)),
            "area": RNG.choice(AREAS),
            "quality_grade": RNG.choice(["A", "A", "B", "B", "C"]),
            "verified": RNG.choice([True, True, True, False]),
        })
    return pd.DataFrame(rows)


def _seed_demands():
    rows = []
    for i in range(6):
        rows.append({
            "demand_id": f"D{i+1:03d}",
            "buyer": RNG.choice(BUYER_NAMES),
            "crop": RNG.choice(CROPS),
            "quantity_kg": RNG.choice([100, 200, 400, 600]),
            "required_date": date.today() + timedelta(days=RNG.randint(1, 7)),
            "delivery_area": RNG.choice(AREAS),
        })
    return pd.DataFrame(rows)


def _seed_orders():
    rows = []
    for i in range(10):
        rows.append({
            "order_id": f"O{i+1:04d}",
            "buyer": RNG.choice(BUYER_NAMES + ["Household Consumer"]),
            "crop": RNG.choice(CROPS),
            "quantity_kg": RNG.choice([5, 10, 20, 50, 100]),
            "status": RNG.choice(ORDER_STATUSES),
            "farmer_amount": 0,
            "logistics_fee": 0,
            "service_fee": 0,
            "total": 0,
        })
    df = pd.DataFrame(rows)
    base = NP_RNG.uniform(10, 40, size=len(df))
    df["farmer_amount"] = (df["quantity_kg"] * base).round(0)
    df["logistics_fee"] = (df["farmer_amount"] * 0.08).round(0)
    df["service_fee"] = (df["farmer_amount"] * 0.05).round(0)
    df["total"] = df["farmer_amount"] + df["logistics_fee"] + df["service_fee"]
    return df


def _seed_users():
    rows = []
    for n in FARMER_NAMES:
        rows.append({"name": n, "role": "Farmer", "status": "Verified"})
    for n in FPO_NAMES:
        rows.append({"name": n, "role": "FPO", "status": "Verified"})
    for n in BUYER_NAMES:
        rows.append({"name": n, "role": "Buyer", "status": "Verified"})
    rows.append({"name": "New Farmer - Rajesh Gaikwad", "role": "Farmer",
                 "status": "Pending"})
    rows.append({"name": "New Buyer - QuickMart", "role": "Buyer",
                 "status": "Pending"})
    return pd.DataFrame(rows)


def _seed_demand_history():
    """Historical daily demand (kg) per crop for the last 30 days — used by
    the AI Insights demand-forecast demo."""
    out = {}
    for crop in CROPS:
        base = NP_RNG.uniform(40, 120)
        trend = NP_RNG.uniform(-0.5, 1.5)
        noise = NP_RNG.normal(0, 8, size=30)
        series = base + trend * np.arange(30) + noise
        out[crop] = np.clip(series, 5, None)
    return out


def _seed_logistics_tasks(orders_df):
    rows = []
    for _, o in orders_df.sample(min(6, len(orders_df)), random_state=1).iterrows():
        rows.append({
            "task_id": f"T-{o['order_id']}",
            "order_id": o["order_id"],
            "pickup_area": RNG.choice(AREAS),
            "drop_area": RNG.choice(AREAS),
            "assigned_to": RNG.choice(LOGISTICS_PARTNERS),
            "status": o["status"],
        })
    return pd.DataFrame(rows)


def init_state():
    """Call at the top of every page. Seeds session_state once per session
    so data (and any in-session edits) persist across page navigation."""
    if "lang" not in st.session_state:
        st.session_state.lang = "English"
    if "listings" not in st.session_state:
        st.session_state.listings = _seed_listings()
    if "demands" not in st.session_state:
        st.session_state.demands = _seed_demands()
    if "orders" not in st.session_state:
        st.session_state.orders = _seed_orders()
    if "users" not in st.session_state:
        st.session_state.users = _seed_users()
    if "demand_history" not in st.session_state:
        st.session_state.demand_history = _seed_demand_history()
    if "logistics_tasks" not in st.session_state:
        st.session_state.logistics_tasks = _seed_logistics_tasks(
            st.session_state.orders
        )
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "drafts" not in st.session_state:
        st.session_state.drafts = []
    if "current_farmer" not in st.session_state:
        st.session_state.current_farmer = FARMER_NAMES[0]


def t():
    """Return the current language's text dict."""
    return LANGUAGES[st.session_state.get("lang", "English")]


def advance_status(order_id):
    order_statuses = ORDER_STATUSES
    df = st.session_state.orders
    idx = df.index[df["order_id"] == order_id]
    if len(idx):
        cur = df.loc[idx[0], "status"]
        pos = order_statuses.index(cur)
        if pos < len(order_statuses) - 1:
            df.loc[idx[0], "status"] = order_statuses[pos + 1]
    # keep logistics task status in sync
    lt = st.session_state.logistics_tasks
    lidx = lt.index[lt["order_id"] == order_id]
    if len(lidx):
        lt.loc[lidx[0], "status"] = df.loc[idx[0], "status"]

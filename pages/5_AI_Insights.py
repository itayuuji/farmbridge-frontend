import numpy as np
import pandas as pd
import streamlit as st

from mock_data import init_state, CROPS, AREAS

st.set_page_config(page_title="AI Insights · FarmBridge", page_icon="🤖", layout="wide")
init_state()

st.title("🤖 AI Insights")
st.warning(
    "⚠️ **All predictions on this page are simulated demo outputs**, computed with "
    "simple statistics over seeded mock data — not a trained production model. "
    "This follows the blueprint's guidance to keep prototype AI explainable and "
    "clearly labelled rather than overbuilt.",
    icon="⚠️",
)

tab_forecast, tab_route, tab_voice = st.tabs(
    ["📈 Demand Forecasting", "🗺️ Route Optimization", "🎙️ AI Voice-to-Listing"]
)

# ---------------- demand forecasting ----------------
with tab_forecast:
    c1, c2 = st.columns(2)
    crop = c1.selectbox("Crop", CROPS)
    area = c2.selectbox("Region", AREAS)

    hist = st.session_state.demand_history[crop]
    days = np.arange(1, len(hist) + 1)

    # simple baseline: moving-average forecast with a naive confidence band
    window = 5
    ma = pd.Series(hist).rolling(window).mean()
    last_ma = ma.iloc[-1]
    trend = (ma.iloc[-1] - ma.iloc[-window - 1]) / window if len(ma) > window else 0
    horizon = 7
    future_days = np.arange(len(hist) + 1, len(hist) + horizon + 1)
    forecast = last_ma + trend * np.arange(1, horizon + 1)
    resid_std = np.nanstd(hist - ma.values) if len(hist) > window else np.std(hist) * 0.2
    upper = forecast + 1.28 * resid_std
    lower = np.clip(forecast - 1.28 * resid_std, 0, None)

    chart_df = pd.DataFrame({
        "day": np.concatenate([days, future_days]),
        "history": np.concatenate([hist, [np.nan] * horizon]),
        "forecast": np.concatenate([[np.nan] * len(hist), forecast]),
        "upper_80pct": np.concatenate([[np.nan] * len(hist), upper]),
        "lower_80pct": np.concatenate([[np.nan] * len(hist), lower]),
    }).set_index("day")

    st.line_chart(chart_df)
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Next-7-day avg. predicted demand — {crop}", f"{forecast.mean():.0f} kg/day")
    c2.metric("Demo forecast method", "Moving-average + trend")
    c3.metric("80% band width", f"±{1.28 * resid_std:.0f} kg")
    st.caption(
        "Production path: compare this baseline against ARIMA/SARIMA, Prophet-style "
        "forecasting, or XGBoost with calendar/season/weather features, and report "
        "MAE/MAPE against a held-out period."
    )

# ---------------- route optimization explainer ----------------
with tab_route:
    st.markdown("#### How route optimization would work")
    st.write(
        "Model every pickup hub and buyer/drop location as a node, with vehicle "
        "capacity and delivery time-window constraints, and solve the resulting "
        "Vehicle Routing Problem with **Google OR-Tools**."
    )
    st.markdown(
        "- Inputs: stop coordinates, demand per stop, vehicle capacity, time windows\n"
        "- Objective: minimize total distance / time subject to constraints\n"
        "- Output: an ordered stop sequence per vehicle\n"
    )
    st.info("Try the interactive before/after demo on the **Logistics Console → "
            "Route Optimization Demo** tab.")

# ---------------- voice-to-listing ----------------
with tab_voice:
    st.markdown("#### AI Voice-to-Listing (typed demo)")
    st.caption(
        "In production, a farmer would speak a description and speech-to-text + "
        "an NLP extraction step would draft the listing fields for confirmation. "
        "This demo uses simple keyword/pattern matching over typed text as a "
        "stand-in for that pipeline."
    )
    example = "I have 200 kilograms of A grade tomato ready, harvested today, price 22 rupees per kg"
    spoken = st.text_area("Simulated spoken description (type it in)", value=example, height=80)

    if st.button("🎙️ Convert to draft listing"):
        text = spoken.lower()
        crop_found = next((c for c in CROPS if c.lower() in text), None)
        qty_match = re.search(r"(\d+)\s*(kg|kilograms?|kilos?)", text)
        price_match = re.search(r"(\d+)\s*(rupees?|₹|rs)", text)
        grade_match = re.search(r"\b(a|b|c)\s*grade\b", text)

        st.markdown("**Draft listing (please confirm before publishing):**")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Crop", crop_found or "— not detected —")
        d2.metric("Quantity", f"{qty_match.group(1)} kg" if qty_match else "— not detected —")
        d3.metric("Price/kg", f"₹{price_match.group(1)}" if price_match else "— not detected —")
        d4.metric("Grade", grade_match.group(1).upper() if grade_match else "— not detected —")
        st.caption("Fields marked \u2018not detected\u2019 would prompt the farmer for "
                    "confirmation rather than being guessed.")

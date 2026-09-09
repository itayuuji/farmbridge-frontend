# FarmBridge — Frontend Prototype (Streamlit)

Frontend-only prototype for **SIH26033**. Built in Python + Streamlit with
seeded, in-memory demo data — no real backend, database, or trained ML model.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## Structure

```
app.py                          Landing page + role picker + language switch
mock_data.py                    Shared seeded demo data & session-state helpers
pages/
  1_Farmer_Dashboard.py         Listings, Add Produce (+ offline drafts), demand signal, orders
  2_Marketplace.py              Consumer browse/filter, group buying, price breakup, cart, checkout
  3_Bulk_Buyer_Console.py       Post demand, harvest-to-demand matching, recurring demand
  4_Logistics_Console.py        Task list + interactive route-optimization (before/after) demo
  5_AI_Insights.py              Demand forecast demo, route explainer, voice-to-listing demo
  6_Impact_Dashboard.py         Judge-facing impact metrics
  7_Admin_Console.py            Verify users/listings, disputes, transactions monitor
```

## Notes

- All "AI" outputs (forecast, route optimization, voice-to-listing) are clearly
  labelled simulated/demo values computed with simple statistics — swap in a
  real model / OR-Tools / STT+NLP pipeline for production.
- Data lives in `st.session_state`, so it resets when the app restarts and is
  not shared across browser sessions.
- Multilingual UI is demonstrated for English / Hindi / Marathi via a small
  strings dictionary in `mock_data.py` — extend `LANGUAGES` to add more.

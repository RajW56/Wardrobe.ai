# Wardrobe Engine — Streamlit App

Full wardrobe recommendation engine with user feedback collection.

## Files

```
wardrobe-streamlit/
├── app.py                  ← Main Streamlit app
├── wardrobe_engine.py      ← Python engine (v3.0)
├── requirements.txt        ← Dependencies
└── README.md
```

## Run Locally

```bash
pip install streamlit pandas
streamlit run app.py
```

Opens at http://localhost:8501

## Deploy to Streamlit Cloud (free)

1. Push this folder to a GitHub repository
2. Go to share.streamlit.io
3. Click "New app"
4. Select your repo + branch + app.py
5. Click Deploy

Live in ~2 minutes. Free forever on Streamlit Community Cloud.

## Admin Dashboard

View all feedback responses at:
```
https://your-app-url.streamlit.app/?admin=true
```

Shows:
- Total responses
- Average star rating
- Average NPS score
- % who would buy the ₹299 card
- Most recommended shirt colors
- Raw data table + CSV download

## Feedback Collected

| Field | Type |
|---|---|
| Star rating | 1–5 scale |
| Would buy ₹299 card | Yes / Maybe / No |
| NPS score | 0–10 |
| Wardrobe input | Colors submitted |
| Recommendations given | Engine output |
| Timestamp | UTC |

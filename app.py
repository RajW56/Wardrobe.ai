import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os
from wardrobe_engine import (
    generate_recommendations,
    load_master_colors,
    SKIN_PROFILES,
)

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wardrobe Engine",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: #f7f3ec;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #fffdf7;
    border-right: 1px solid #e8dfc8;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Hide default header */
[data-testid="stHeader"] {
    background: transparent;
}

/* Swatch color circle helper */
.swatch {
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
    border: 1px solid rgba(0,0,0,0.12);
}

/* Card */
.profile-card {
    background: #fffdf7;
    border: 1.5px solid #e0d4b8;
    border-radius: 16px;
    padding: 24px;
    position: relative;
    box-shadow: 0 4px 24px rgba(139,105,20,0.08);
}
.card-top-bar {
    height: 4px;
    background: linear-gradient(90deg, #C9A84C, #e8c56a, #C9A84C);
    border-radius: 4px 4px 0 0;
    margin: -24px -24px 20px -24px;
    border-radius: 14px 14px 0 0;
}
.card-eyebrow {
    font-size: 10px;
    letter-spacing: 0.16em;
    color: #C9A84C;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;
    color: #1a1208;
    letter-spacing: -0.3px;
    margin-bottom: 4px;
}
.card-subtitle {
    font-size: 12px;
    color: #9a8a70;
    margin-bottom: 20px;
}
.section-label {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #9a8a70;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::before {
    content: '';
    display: inline-block;
    width: 16px;
    height: 1.5px;
    background: #C9A84C;
}
.swatch-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 20px;
}
.swatch-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}
.swatch-block {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    position: relative;
}
.swatch-name {
    font-size: 9px;
    color: #7a6a50;
    text-align: center;
    max-width: 56px;
    line-height: 1.3;
    font-weight: 600;
}
.swatch-score {
    font-size: 9px;
    color: #C9A84C;
    font-weight: 700;
    font-family: monospace;
}
.rank-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #C9A84C;
    color: white;
    font-size: 8px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}
.skin-badge {
    position: absolute;
    bottom: -4px;
    right: -4px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #e8734a;
    color: white;
    font-size: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Outfit folded stack */
.outfit-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 14px;
    border-radius: 12px;
    background: #faf7f2;
    border: 1px solid #ede5d4;
    margin-bottom: 6px;
}
.outfit-rank {
    font-size: 11px;
    color: #C9A84C;
    font-weight: 700;
    font-family: monospace;
    width: 24px;
    text-align: center;
    flex-shrink: 0;
}
.outfit-stack {
    display: flex;
    flex-direction: column;
    gap: 2px;
    flex-shrink: 0;
}
.outfit-shirt-block {
    width: 44px;
    height: 22px;
    border-radius: 6px 6px 2px 2px;
    position: relative;
}
.outfit-pant-block {
    width: 38px;
    height: 26px;
    border-radius: 2px 2px 6px 6px;
    margin-left: 3px;
    display: flex;
    gap: 2px;
}
.outfit-pant-leg {
    flex: 1;
    border-radius: 2px 2px 6px 6px;
}
.outfit-names {
    font-size: 12px;
    color: #2a1f0a;
    font-weight: 500;
    flex: 1;
}
.outfit-score-wrap {
    display: flex;
    flex-direction: column;
    gap: 3px;
    align-items: flex-end;
    flex-shrink: 0;
}
.score-num {
    font-size: 11px;
    color: #C9A84C;
    font-weight: 700;
    font-family: monospace;
}
.score-bar-bg {
    width: 64px;
    height: 3px;
    background: #ede5d4;
    border-radius: 2px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #C9A84C, #e8c56a);
}

/* Quality badge */
.quality-badge {
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}

/* Feedback section */
.feedback-card {
    background: #fffdf7;
    border: 1.5px solid #e0d4b8;
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 4px 24px rgba(139,105,20,0.06);
}
.feedback-title {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 700;
    color: #1a1208;
    margin-bottom: 4px;
}
.feedback-sub {
    font-size: 12px;
    color: #9a8a70;
    margin-bottom: 20px;
}
.thankyou-box {
    background: #f0f7e8;
    border: 1.5px solid #b8d98855;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.thankyou-title {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    color: #3a6020;
    margin-bottom: 8px;
}
.thankyou-sub {
    font-size: 13px;
    color: #5a7a40;
}

/* Divider */
.gold-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #e0d4b8, transparent);
    margin: 20px 0;
}

/* Metric tiles */
.metric-tile {
    background: #fffdf7;
    border: 1px solid #e0d4b8;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    color: #C9A84C;
    font-weight: 700;
}
.metric-label {
    font-size: 11px;
    color: #9a8a70;
    margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA STORAGE  — CSV file (persists across sessions on
# Streamlit Community Cloud via the repo's data/ folder)
# ─────────────────────────────────────────────────────────────

FEEDBACK_FILE = "feedback.csv"

COLUMNS = [
    "id", "timestamp",
    "shirts_input", "pants_input", "season", "skin_profile",
    "smart_shirts", "smart_pants", "neutrals",
    "top_outfit",
    "star_rating", "buy_card", "nps_score",
]

def get_storage() -> pd.DataFrame:
    """Load feedback CSV. Returns empty DataFrame if file does not exist yet."""
    if os.path.exists(FEEDBACK_FILE):
        try:
            return pd.read_csv(FEEDBACK_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)

def save_feedback(row: dict):
    """Append one row to the CSV file, creating it if needed."""
    db = get_storage()
    new_row = pd.DataFrame([row])
    updated = pd.concat([db, new_row], ignore_index=True)
    updated.to_csv(FEEDBACK_FILE, index=False)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
MASTER_COLORS = load_master_colors()
SHIRT_COLORS  = sorted([n for n, d in MASTER_COLORS.items() if d["shirt_allowed"]])
PANT_COLORS   = sorted([n for n, d in MASTER_COLORS.items() if d["pant_allowed"]])
SEASONS       = ["All", "Spring", "Summer", "Autumn", "Winter"]
SKIN_KEYS     = list(SKIN_PROFILES.keys())

SKIN_HEX = {
    "Light_Warm": "#F5CBA7", "Light_Cool": "#FAD7C3", "Light_Neutral": "#F0C89A",
    "Medium_Warm": "#C68642", "Medium_Cool": "#B87333", "Medium_Neutral": "#A0724A",
    "Deep_Warm": "#6B3A2A",  "Deep_Cool": "#4A2C2A",  "Deep_Neutral": "#3B1F1A",
}

QUALITY_STYLE = {
    "Premium":    ("background:#fdf3dc;color:#8B5E00;border:1px solid #C9A84C44", "Premium"),
    "Strong":     ("background:#e8f7f0;color:#2a6a4a;border:1px solid #4a9a7044", "Strong"),
    "Developing": ("background:#fff8ec;color:#5a3e00;border:1px solid #d4a04044", "Developing"),
    "Starter":    ("background:#f5f2ee;color:#6a6050;border:1px solid #b0a08044", "Starter"),
}

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "result"            not in st.session_state: st.session_state.result = None
if "feedback_done"     not in st.session_state: st.session_state.feedback_done = False
if "show_all_combos"   not in st.session_state: st.session_state.show_all_combos = False
if "session_id"        not in st.session_state: st.session_state.session_id = str(uuid.uuid4())[:8]

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def lum(hex_code):
    h = hex_code.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return 0.2126*r + 0.7152*g + 0.0722*b

def text_col(hex_code):
    return "#1a1208" if lum(hex_code) > 155 else "#fffdf7"

def quality_label(top_score):
    if top_score > 12: return "Premium"
    if top_score > 8:  return "Strong"
    if top_score > 4:  return "Developing"
    return "Starter"

def swatch_html(items, score_key):
    html = '<div class="swatch-grid">'
    for i, item in enumerate(items):
        score = item.get(score_key, 0)
        tc    = text_col(item["hex"])
        rank  = f'<div class="rank-badge">{i+1}</div>' if i == 0 else ""
        skin  = '<div class="skin-badge">★</div>' if item.get("skin_delta", 0) > 0 else ""
        html += f"""
        <div class="swatch-item">
          <div class="swatch-block" style="background:{item['hex']};position:relative">
            {rank}{skin}
          </div>
          <div class="swatch-name">{item['color']}</div>
          <div class="swatch-score">{score:.1f}</div>
        </div>"""
    html += "</div>"
    return html

def outfit_row_html(outfit, index):
    pct  = round((outfit["score"] / 5) * 100)
    tc_s = text_col(outfit["shirt_hex"])
    tc_p = text_col(outfit["pant_hex"])
    return f"""
    <div class="outfit-row">
      <div class="outfit-rank">#{index+1}</div>
      <div>
        <div style="display:flex;flex-direction:column;gap:3px">
          <div style="width:48px;height:22px;border-radius:6px 6px 2px 2px;background:{outfit['shirt_hex']};box-shadow:0 1px 3px rgba(0,0,0,.15)"></div>
          <div style="display:flex;gap:3px">
            <div style="width:21px;height:22px;border-radius:2px 2px 6px 6px;background:{outfit['pant_hex']};box-shadow:0 1px 3px rgba(0,0,0,.12)"></div>
            <div style="width:21px;height:22px;border-radius:2px 2px 6px 6px;background:{outfit['pant_hex']};box-shadow:0 1px 3px rgba(0,0,0,.12)"></div>
          </div>
        </div>
      </div>
      <div style="flex:1">
        <div style="font-size:12px;color:#2a1f0a;font-weight:500;margin-bottom:4px">{outfit['shirt']} + {outfit['pant']}</div>
        <div style="height:3px;border-radius:2px;background:#ede5d4;overflow:hidden">
          <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#C9A84C,#e8c56a);border-radius:2px"></div>
        </div>
      </div>
      <div style="font-size:11px;color:#C9A84C;font-weight:700;font-family:monospace">{outfit['score']:.1f}</div>
    </div>"""

def combo_card_html(outfit):
    pct   = round((outfit["score"] / 5) * 100)
    qual  = "Excellent" if outfit["score"]>=4 else "Good" if outfit["score"]>=3 else "Decent" if outfit["score"]>=2 else "Weak"
    qcol  = "#5a7a2a" if outfit["score"]>=4 else "#2a6a4a" if outfit["score"]>=3 else "#8a6a20" if outfit["score"]>=2 else "#9a8a70"
    qbg   = "#f0f7e8" if outfit["score"]>=4 else "#e8f7f0" if outfit["score"]>=3 else "#fdf3dc" if outfit["score"]>=2 else "#f5f2ee"
    return f"""
    <div style="background:#faf7f2;border:1px solid #ede5d4;border-radius:14px;padding:14px 10px;display:flex;flex-direction:column;align-items:center;gap:8px">
      <div style="display:flex;flex-direction:column;gap:3px;align-items:center">
        <div style="width:52px;height:24px;border-radius:7px 7px 3px 3px;background:{outfit['shirt_hex']};box-shadow:0 2px 4px rgba(0,0,0,.12)"></div>
        <div style="display:flex;gap:3px">
          <div style="width:23px;height:26px;border-radius:3px 3px 7px 7px;background:{outfit['pant_hex']};box-shadow:0 2px 4px rgba(0,0,0,.1)"></div>
          <div style="width:23px;height:26px;border-radius:3px 3px 7px 7px;background:{outfit['pant_hex']};box-shadow:0 2px 4px rgba(0,0,0,.1)"></div>
        </div>
      </div>
      <div style="font-size:10px;color:#4a3a20;text-align:center;line-height:1.4;font-weight:500">{outfit['shirt']}<br>{outfit['pant']}</div>
      <div style="display:flex;align-items:center;justify-content:space-between;width:100%">
        <span style="font-size:9px;font-weight:700;padding:2px 6px;border-radius:6px;background:{qbg};color:{qcol}">{qual}</span>
        <span style="font-size:11px;color:#C9A84C;font-weight:700;font-family:monospace">{outfit['score']:.1f}</span>
      </div>
    </div>"""

# ─────────────────────────────────────────────────────────────
# SIDEBAR — INPUT
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
      <div style="width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#C9A84C,#8B5E00);display:flex;align-items:center;justify-content:center">
        <span style="color:#fffdf7;font-size:14px;font-weight:700;font-family:'Playfair Display',serif">W</span>
      </div>
      <span style="font-size:15px;font-weight:700;color:#1a1208;font-family:'Playfair Display',serif">Wardrobe <span style="color:#C9A84C">Engine</span></span>
    </div>
    <div style="font-size:11px;color:#9a8a70;margin-bottom:24px;padding-left:38px">Personal Color Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:8px">① Shirts you own</div>', unsafe_allow_html=True)
    selected_shirts = st.multiselect(
        label="shirts",
        options=SHIRT_COLORS,
        label_visibility="collapsed",
        placeholder="Select shirt colors…",
        format_func=lambda n: f"{n}"
    )
    if selected_shirts:
        dots = "".join([f'<span class="swatch" style="background:{MASTER_COLORS[s]["hex"]}"></span>{s}&nbsp;&nbsp;' for s in selected_shirts])
        st.markdown(f'<div style="font-size:11px;color:#8B5E00;margin-top:4px;margin-bottom:8px">{dots}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#ede5d4;margin:12px 0"></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:8px">② Pants you own</div>', unsafe_allow_html=True)
    selected_pants = st.multiselect(
        label="pants",
        options=PANT_COLORS,
        label_visibility="collapsed",
        placeholder="Select pant colors…",
    )

    st.markdown('<div style="height:1px;background:#ede5d4;margin:12px 0"></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:8px">③ Season</div>', unsafe_allow_html=True)
    selected_season = st.radio(
        label="season",
        options=SEASONS,
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown('<div style="height:1px;background:#ede5d4;margin:12px 0"></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:8px">④ Skin tone <span style="font-weight:400;text-transform:none;letter-spacing:0;color:#c0b090">(optional)</span></div>', unsafe_allow_html=True)

    # 3×3 skin tone grid
    skin_rows = [
        ("Light",  ["Light_Warm",  "Light_Cool",  "Light_Neutral"]),
        ("Medium", ["Medium_Warm", "Medium_Cool", "Medium_Neutral"]),
        ("Deep",   ["Deep_Warm",   "Deep_Cool",   "Deep_Neutral"]),
    ]
    selected_skin = st.session_state.get("selected_skin", "")

    for depth_label, keys in skin_rows:
        st.markdown(f'<div style="font-size:9px;color:#c0b090;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">{depth_label}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for col, key in zip(cols, keys):
            label = key.replace(f"{depth_label}_", "")
            hex_c = SKIN_HEX[key]
            is_sel = selected_skin == key
            border = "3px solid #C9A84C" if is_sel else "2px solid rgba(0,0,0,0.1)"
            bg = "#fdf3dc" if is_sel else "#faf7f2"
            with col:
                if st.button(
                    label=f"{'✓ ' if is_sel else ''}{label}",
                    key=f"skin_{key}",
                    use_container_width=True,
                    help=key.replace("_", " "),
                ):
                    st.session_state["selected_skin"] = "" if is_sel else key
                    st.rerun()
                st.markdown(
                    f'<div style="text-align:center;margin-top:-8px;margin-bottom:6px">'
                    f'<span style="display:inline-block;width:22px;height:22px;border-radius:50%;background:{hex_c};border:{border};box-shadow:0 1px 4px rgba(0,0,0,.2)"></span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    selected_skin = st.session_state.get("selected_skin", "")
    if selected_skin:
        st.markdown(
            f'<div style="margin-top:4px;padding:7px 12px;border-radius:9px;background:#fdf3dc;border:1px solid #e8c56a55;font-size:11px;color:#5a3e00;font-weight:600">'
            f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{SKIN_HEX[selected_skin]};border:1px solid rgba(0,0,0,.15);margin-right:6px;vertical-align:middle"></span>'
            f'{selected_skin.replace("_"," ")} · active ✓</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    has_input = len(selected_shirts) > 0 or len(selected_pants) > 0
    run = st.button(
        "Generate My Color Profile →",
        type="primary",
        use_container_width=True,
        disabled=not has_input,
    )
    if not has_input:
        st.caption("Select at least one shirt or pant color to begin")

# ─────────────────────────────────────────────────────────────
# RUN ENGINE
# ─────────────────────────────────────────────────────────────
if run:
    st.session_state.feedback_done = False
    st.session_state.show_all_combos = False
    with st.spinner("Analysing your colour network…"):
        result = generate_recommendations({
            "shirts":      selected_shirts,
            "pants":       selected_pants,
            "season":      selected_season,
            "skin_profile": selected_skin or None,
        })
    st.session_state.result = result
    st.session_state.last_input = {
        "shirts":  selected_shirts,
        "pants":   selected_pants,
        "season":  selected_season,
        "skin":    selected_skin,
    }

# ─────────────────────────────────────────────────────────────
# MAIN — EMPTY STATE
# ─────────────────────────────────────────────────────────────
if st.session_state.result is None:
    st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style="text-align:center;padding:48px 32px;background:#fffdf7;border:1.5px solid #e0d4b8;border-radius:20px;box-shadow:0 4px 24px rgba(139,105,20,0.06)">
          <div style="font-size:48px;margin-bottom:16px">🎨</div>
          <div style="font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:#1a1208;margin-bottom:8px">Your colour profile awaits</div>
          <div style="font-size:13px;color:#9a8a70;line-height:1.7;max-width:320px;margin:0 auto">
            Select the colours you already own from the sidebar.
            The engine will recommend what to buy next — scored by compatibility, season, and skin tone.
          </div>
          <div style="margin-top:20px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
            <span style="font-size:11px;color:#8B5E00;background:#fdf3dc;border:1px solid #e8c56a55;padding:5px 12px;border-radius:20px">Smart shirt recommendations</span>
            <span style="font-size:11px;color:#8B5E00;background:#fdf3dc;border:1px solid #e8c56a55;padding:5px 12px;border-radius:20px">Smart pant recommendations</span>
            <span style="font-size:11px;color:#8B5E00;background:#fdf3dc;border:1px solid #e8c56a55;padding:5px 12px;border-radius:20px">Outfit combinations</span>
            <span style="font-size:11px;color:#8B5E00;background:#fdf3dc;border:1px solid #e8c56a55;padding:5px 12px;border-radius:20px">Folded stack visuals</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────
# MAIN — RESULTS
# ─────────────────────────────────────────────────────────────
result   = st.session_state.result
inp      = st.session_state.last_input
top_sc   = result["smart_shirts"][0]["shirt_score"] if result["smart_shirts"] else 0
qual     = quality_label(top_sc)
qs, ql   = QUALITY_STYLE[qual]
skin_lbl = inp["skin"].replace("_", " ") if inp["skin"] else "Universal"
season_d = inp["season"] if inp["season"] != "All" else "All Seasons"

# header
st.markdown(f"""
<div style="margin-bottom:24px">
  <div style="font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:#1a1208;letter-spacing:-.3px">Your Colour Profile</div>
  <div style="font-size:12px;color:#9a8a70;margin-top:4px">
    Based on {len(inp['shirts'])} shirt{'s' if len(inp['shirts'])!=1 else ''} and {len(inp['pants'])} pant{'s' if len(inp['pants'])!=1 else ''} you own · {season_d}
  </div>
</div>
""", unsafe_allow_html=True)

col_card, col_outfits = st.columns([1.1, 1], gap="large")

# ── PROFILE CARD ──────────────────────────────────────────────
with col_card:
    card_html = f"""
    <div class="profile-card">
      <div class="card-top-bar"></div>
      <div class="card-eyebrow">Wardrobe Engine · Colour Profile</div>
      <div class="card-title">Your Style Profile</div>
      <div class="card-subtitle">{season_d} · {skin_lbl}</div>
      <span class="quality-badge" style="{qs}">{ql}</span>
      <div class="gold-divider"></div>
    """

    if result["smart_shirts"]:
        card_html += '<div class="section-label">Smart Shirts to Buy</div>'
        card_html += swatch_html(result["smart_shirts"], "shirt_score")

    if result["smart_pants"]:
        card_html += '<div class="section-label">Smart Pants to Buy</div>'
        card_html += swatch_html(result["smart_pants"], "pant_score")

    if result["all_season_neutrals"]:
        card_html += '<div class="section-label" style="--c:#9a8a70">All-Season Neutrals</div>'
        card_html += swatch_html(result["all_season_neutrals"], "neutral_score")

    card_html += f"""
      <div class="gold-divider"></div>
      <div style="display:flex;justify-content:space-between;font-size:9px;color:#c0b090">
        <span>Season: <b style="color:#8B5E00">{season_d}</b> · Skin: <b style="color:#8B5E00">{skin_lbl}</b></span>
        <span style="font-family:monospace">wardrobeengine.com</span>
      </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# ── OUTFIT COMBINATIONS ───────────────────────────────────────
with col_outfits:
    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:12px">Top Outfit Combinations</div>', unsafe_allow_html=True)

    outfits_html = ""
    for i, o in enumerate(result["outfits"]):
        outfits_html += outfit_row_html(o, i)
    st.markdown(outfits_html, unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    all_outfits = result.get("allOutfits", result.get("outfits", []))

    if not st.session_state.show_all_combos:
        st.markdown(
            f'<div style="background:#fffdf7;border:1.5px solid #e0d4b8;border-radius:14px;padding:14px 18px;margin-top:4px">'
            f'<div style="font-size:13px;font-weight:600;color:#1a1208">See all outfit combinations?</div>'
            f'<div style="font-size:11px;color:#9a8a70;margin-top:2px">{len(all_outfits)} possible pairings</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        bc1, bc2 = st.columns([1, 1])
        with bc1:
            if st.button("Show all combinations", use_container_width=True):
                st.session_state.show_all_combos = True
                st.rerun()
        with bc2:
            st.button("Skip", use_container_width=True, key="skip_combos")
    else:
        st.markdown(f'<div style="font-size:12px;color:#9a8a70;margin-bottom:10px">{len(all_outfits)} pairings</div>', unsafe_allow_html=True)
        grid_cols = st.columns(3)
        for i, o in enumerate(all_outfits):
            with grid_cols[i % 3]:
                st.markdown(combo_card_html(o), unsafe_allow_html=True)
        if st.button("Hide combinations ↑", use_container_width=True):
            st.session_state.show_all_combos = False
            st.rerun()

# ─────────────────────────────────────────────────────────────
# FEEDBACK SECTION
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#e0d4b8,transparent);margin-bottom:32px"></div>', unsafe_allow_html=True)

if st.session_state.feedback_done:
    # ── THANK YOU ──
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class="thankyou-box">
          <div class="thankyou-title">Thank you! 🙏</div>
          <div class="thankyou-sub">Your feedback helps improve the engine and will shape the ₹299 colour card.<br>We'll notify you when it launches.</div>
        </div>
        """, unsafe_allow_html=True)
else:
    # ── FEEDBACK FORM ──
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class="feedback-card">
          <div class="feedback-title">Share your feedback</div>
          <div class="feedback-sub">2 minutes · helps us build a better product</div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:12px;font-weight:600;color:#2a1f0a;margin-bottom:6px">How useful were these recommendations?</div>', unsafe_allow_html=True)
        star_rating = st.select_slider(
            label="star_rating",
            options=[1, 2, 3, 4, 5],
            value=4,
            format_func=lambda x: "⭐" * x,
            label_visibility="collapsed",
        )

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#2a1f0a;margin-bottom:6px">Would you buy a personalised colour card for ₹299?</div>', unsafe_allow_html=True)
        buy_card = st.radio(
            label="buy_card",
            options=["Yes — I'd buy this", "Maybe — need to see the physical card", "No — not for me"],
            label_visibility="collapsed",
            horizontal=False,
        )

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;font-weight:600;color:#2a1f0a;margin-bottom:2px">How likely are you to recommend this to a friend?</div>', unsafe_allow_html=True)
        st.caption("0 = Not at all likely · 10 = Extremely likely")
        nps = st.slider(
            label="nps",
            min_value=0,
            max_value=10,
            value=7,
            label_visibility="collapsed",
        )

        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

        if st.button("Submit Feedback →", type="primary", use_container_width=True):
            save_feedback({
                "id":            st.session_state.session_id,
                "timestamp":     datetime.utcnow().isoformat(),
                "shirts_input":  ", ".join(inp["shirts"]),
                "pants_input":   ", ".join(inp["pants"]),
                "season":        inp["season"],
                "skin_profile":  inp["skin"],
                "smart_shirts":  ", ".join([r["color"] for r in result["smart_shirts"]]),
                "smart_pants":   ", ".join([r["color"] for r in result["smart_pants"]]),
                "neutrals":      ", ".join([r["color"] for r in result["all_season_neutrals"]]),
                "top_outfit":    f"{result['outfits'][0]['shirt']} + {result['outfits'][0]['pant']}" if result["outfits"] else "",
                "star_rating":   star_rating,
                "buy_card":      buy_card,
                "nps_score":     nps,
            })
            st.session_state.feedback_done = True
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ADMIN DASHBOARD  (hidden at /admin via ?admin=true in URL)
# ─────────────────────────────────────────────────────────────
params = st.query_params
if params.get("admin") == "true":
    st.markdown("---")
    st.markdown("### 📊 Feedback Dashboard")

    # Password gate
    admin_pw = st.secrets.get("ADMIN_PASSWORD", "")
    entered  = st.text_input("Admin password", type="password", key="admin_pw")
    if entered != admin_pw:
        if entered:
            st.error("Incorrect password.")
        else:
            st.info("Enter the admin password to view feedback data.")
        st.stop()

    db = get_storage()
    if db.empty:
        st.info("No feedback submitted yet.")
    else:
        total = len(db)
        avg_star = round(db["star_rating"].mean(), 1)
        avg_nps  = round(db["nps_score"].mean(), 1)
        buy_yes  = round((db["buy_card"].str.startswith("Yes").sum() / total) * 100)

        m1, m2, m3, m4 = st.columns(4)
        for col, val, label in [
            (m1, total,    "Responses"),
            (m2, avg_star, "Avg Rating ⭐"),
            (m3, avg_nps,  "Avg NPS"),
            (m4, f"{buy_yes}%", "Would Buy Card"),
        ]:
            col.markdown(f"""
            <div class="metric-tile">
              <div class="metric-val">{val}</div>
              <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

        st.markdown("**Buy card distribution**")
        st.bar_chart(db["buy_card"].value_counts())

        st.markdown("**Most recommended shirts**")
        shirt_series = db["smart_shirts"].str.split(", ").explode()
        st.bar_chart(shirt_series.value_counts().head(10))

        st.markdown("**Raw responses**")
        st.dataframe(db, use_container_width=True)

        csv = db.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="wardrobe_feedback.csv",
            mime="text/csv",
        )

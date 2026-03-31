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
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS  — Blue & White theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Lora:wght@600;700&family=DM+Mono:wght@400&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #0f1923;
}
.stApp { background: #f0f4f8; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #dde3ea;
    box-shadow: 2px 0 12px rgba(15,25,80,.06);
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1.2rem 2rem !important;
}

/* ── Hide default chrome ── */
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

/* ── Main area ── */
.block-container { padding: 2rem 2.5rem !important; max-width: 1400px; }

/* ── Sidebar divider label ── */
.sb-label {
    font-size: 10px; font-weight: 700; letter-spacing: .14em;
    text-transform: uppercase; color: #8896a8; margin: 20px 0 8px;
    display: flex; align-items: center; gap: 8px;
}
.sb-label::after { content:''; flex:1; height:1px; background:#e8edf2; }

/* ── Colour pill rows (shown after selecting) ── */
.colour-pills { display:flex; flex-wrap:wrap; gap:5px; margin: 4px 0 10px; }
.colour-pill {
    display:flex; align-items:center; gap:5px;
    padding: 4px 10px 4px 5px;
    border-radius: 20px; background: #eef2ff;
    border: 1px solid #c7d2fe; font-size: 11px; color: #3730a3; font-weight: 500;
}
.pill-dot {
    width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0;
    border: 1px solid rgba(0,0,0,.1); box-shadow: inset 0 1px 2px rgba(0,0,0,.1);
}

/* ── Season buttons ── */
.season-row { display:flex; gap:5px; flex-wrap:wrap; margin-bottom:8px; }
.season-btn {
    display:flex; flex-direction:column; align-items:center; gap:3px;
    padding: 8px 6px; border-radius: 10px; cursor: pointer; min-width: 48px;
    border: 1.5px solid #dde3ea; background: #f8fafc;
    transition: all .15s;
}
.season-btn:hover { border-color: #93afd4; background: #eef4fb; }
.season-btn.sel {
    border-color: #1d4ed8; background: #eff6ff;
    box-shadow: 0 2px 8px rgba(29,78,216,.15);
}
.season-icon { font-size: 20px; line-height:1; }
.season-name {
    font-size: 8px; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; color: #8896a8;
}
.season-btn.sel .season-name { color: #1d4ed8; }

/* ── Skin tone grid ── */
.depth-row-label {
    font-size: 9px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: #8896a8; margin: 10px 0 5px;
}
.skin-card {
    display:flex; flex-direction:column; align-items:center; gap:5px;
    padding: 8px 4px; border-radius: 10px; cursor: pointer;
    border: 1.5px solid #dde3ea; background: #f8fafc;
    transition: all .15s;
}
.skin-card:hover { border-color: #93afd4; background: #eef4fb; }
.skin-card.sel {
    border-color: #1d4ed8; background: #eff6ff;
    box-shadow: 0 2px 8px rgba(29,78,216,.15);
}
.skin-face { width:32px; height:32px; }
.skin-lbl {
    font-size: 8.5px; font-weight: 600; color: #64748b;
    text-align: center; line-height: 1.2; letter-spacing: .03em;
}
.skin-card.sel .skin-lbl { color: #1d4ed8; }

/* ── Generate button ── */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 12px !important; font-weight: 600 !important;
    font-size: 13px !important; padding: 14px !important;
    letter-spacing: .02em !important;
    box-shadow: 0 4px 14px rgba(29,78,216,.3) !important;
    transition: all .15s !important;
}
.stButton > button:hover { opacity: .9 !important; transform: translateY(-1px) !important; }
.stButton > button:disabled {
    background: #e2e8f0 !important; color: #94a3b8 !important;
    box-shadow: none !important; transform: none !important;
}

/* ── Page header ── */
.page-header {
    font-family: 'Lora', serif; font-size: 32px; font-weight: 700;
    color: #0f172a; letter-spacing: -.4px; margin-bottom: 4px;
}
.page-sub { font-size: 13px; color: #64748b; margin-bottom: 28px; }

/* ── Profile card ── */
.profile-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 20px; padding: 28px;
    box-shadow: 0 4px 20px rgba(15,25,80,.07);
    position: relative; overflow: hidden;
}
.card-accent {
    position: absolute; top:0; left:0; right:0; height:4px;
    background: linear-gradient(90deg, #1d4ed8, #3b82f6, #93c5fd, #3b82f6, #1d4ed8);
    border-radius: 20px 20px 0 0;
}
.card-eyebrow {
    font-size: 9px; letter-spacing: .18em; color: #3b82f6;
    font-weight: 700; text-transform: uppercase; margin-bottom: 6px;
}
.card-title {
    font-family: 'Lora', serif; font-size: 24px; font-weight: 700;
    color: #0f172a; letter-spacing: -.3px; margin-bottom: 2px;
}
.card-meta { font-size: 11px; color: #94a3b8; margin-bottom: 20px; }
.card-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    margin: 16px 0;
}
.sec-label {
    font-size: 9px; font-weight: 700; letter-spacing: .16em;
    text-transform: uppercase; color: #94a3b8; margin: 0 0 12px;
    display: flex; align-items: center; gap: 8px;
}
.sec-label::before {
    content:''; width:12px; height:2px;
    background: linear-gradient(90deg, #1d4ed8, #3b82f6);
    border-radius: 2px;
}

/* ── Rectangular colour swatches ── */
.rect-grid { display:flex; flex-wrap:wrap; gap:12px; margin-bottom:18px; }
.rect-item { display:flex; flex-direction:column; align-items:center; gap:5px; }
.rect-block {
    width: 64px; height: 96px; border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,.12);
    position: relative; transition: transform .15s;
}
.rect-block:hover { transform: translateY(-3px); }
.rect-name {
    font-size: 9px; color: #475569; text-align: center;
    max-width: 68px; line-height: 1.3; font-weight: 600;
}
.rect-score {
    font-size: 9px; color: #3b82f6; font-weight: 700;
    font-family: 'DM Mono', monospace;
}
.rect-rank {
    position:absolute; top:-5px; right:-5px; width:16px; height:16px;
    border-radius:50%; background:#1d4ed8; color:white;
    font-size:8px; font-weight:700;
    display:flex; align-items:center; justify-content:center;
    box-shadow: 0 2px 4px rgba(29,78,216,.4);
}
.rect-star {
    position:absolute; bottom:-5px; right:-5px; width:16px; height:16px;
    border-radius:50%; background:#f97316; color:white;
    font-size:9px; display:flex; align-items:center; justify-content:center;
}

/* ── Quality badge ── */
.q-badge {
    display:inline-block; padding:4px 14px; border-radius:20px;
    font-size:10px; font-weight:700; letter-spacing:.05em;
}

/* ── Outfit entry ── */
.outfit-entry {
    display:flex; align-items:center; gap:14px;
    padding:12px 16px; border-radius:14px;
    background:#ffffff; border:1px solid #e2e8f0;
    margin-bottom:8px; transition:all .15s;
    box-shadow: 0 1px 4px rgba(15,25,80,.05);
}
.outfit-entry:hover { border-color:#93c5fd; box-shadow:0 3px 12px rgba(59,130,246,.1); }
.outfit-rank {
    font-size:11px; color:#94a3b8; font-weight:700;
    font-family:'DM Mono',monospace; width:22px; text-align:center; flex-shrink:0;
}
.outfit-name { font-size:12px; color:#0f172a; font-weight:600; }
.outfit-sub  { font-size:10px; color:#94a3b8; margin-top:2px; }
.outfit-bar-bg {
    width:64px; height:3px; background:#e2e8f0;
    border-radius:2px; overflow:hidden; margin-top:4px;
}
.outfit-bar-fill {
    height:100%; border-radius:2px;
    background:linear-gradient(90deg,#1d4ed8,#3b82f6);
}
.outfit-score-num {
    font-size:12px; color:#3b82f6; font-weight:700;
    font-family:'DM Mono',monospace;
}

/* ── Combo card ── */
.combo-cell {
    background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
    padding:14px 10px; display:flex; flex-direction:column;
    align-items:center; gap:8px; transition:all .15s;
    box-shadow:0 1px 4px rgba(15,25,80,.04);
}
.combo-cell:hover { border-color:#93c5fd; box-shadow:0 3px 10px rgba(59,130,246,.1); }

/* ── Prompt bubble ── */
.prompt-bubble {
    background:#eff6ff; border:1px solid #bfdbfe;
    border-radius:14px; padding:16px 20px;
    display:flex; align-items:center; justify-content:space-between;
    gap:16px; margin-top:12px;
}
.pb-q { font-size:13px; font-weight:600; color:#1e3a8a; }
.pb-sub { font-size:11px; color:#3b82f6; margin-top:2px; }

/* ── Feedback ── */
.feedback-wrap {
    background:#ffffff; border:1px solid #e2e8f0;
    border-radius:20px; padding:32px; max-width:560px; margin:0 auto;
    box-shadow:0 4px 20px rgba(15,25,80,.07);
}
.fb-title {
    font-family:'Lora',serif; font-size:24px;
    font-weight:700; color:#0f172a; margin-bottom:6px;
}
.fb-sub { font-size:12px; color:#64748b; margin-bottom:24px; }
.fb-label { font-size:12px; font-weight:600; color:#1e3a8a; margin-bottom:6px; }

.thankyou {
    background:#f0fdf4; border:1px solid #bbf7d0;
    border-radius:16px; padding:36px; text-align:center;
    max-width:480px; margin:0 auto;
}
.ty-title {
    font-family:'Lora',serif; font-size:26px;
    color:#166534; font-weight:700; margin-bottom:8px;
}
.ty-sub { font-size:13px; color:#15803d; line-height:1.6; }

/* ── Admin metrics ── */
.metric-tile {
    background:#ffffff; border:1px solid #e2e8f0;
    border-radius:14px; padding:18px; text-align:center;
    box-shadow:0 1px 4px rgba(15,25,80,.05);
}
.metric-val {
    font-family:'Lora',serif; font-size:30px;
    color:#1d4ed8; font-weight:700;
}
.metric-lbl { font-size:11px; color:#64748b; margin-top:3px; }

/* ── Streamlit widget overrides for light theme ── */
.stMultiSelect > div > div {
    background:#f8fafc !important; border-color:#dde3ea !important;
    border-radius:10px !important;
}
.stMultiSelect label, .stMultiSelect span { color:#0f172a !important; }
.stMultiSelect [data-baseweb="tag"] {
    background:#dbeafe !important; border-color:#93c5fd !important;
}
.stMultiSelect [data-baseweb="tag"] span { color:#1e3a8a !important; }

.stRadio label, .stRadio label p,
.stRadio span { color: #0f172a !important; font-size:13px !important; }
.stRadio > div > label > div:first-child div {
    border-color: #3b82f6 !important;
}

[data-testid="stSelectSlider"] > div { color:#1d4ed8 !important; }
.stSlider > div > div > div { background:#3b82f6 !important; }
.stSlider p, .stSlider label,
[data-testid="stTickBarMin"],
[data-testid="stTickBarMax"] { color:#64748b !important; }

.stCaption, .stCaption p { color:#94a3b8 !important; }
div[data-testid="stMarkdownContainer"] p { color:#334155; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STORAGE
# ─────────────────────────────────────────────────────────────
FEEDBACK_FILE = "feedback.csv"
COLUMNS = ["id","timestamp","shirts_input","pants_input","season","skin_profile",
           "smart_shirts","smart_pants","neutrals","top_outfit",
           "star_rating","buy_card","nps_score"]

def get_storage():
    if os.path.exists(FEEDBACK_FILE):
        try: return pd.read_csv(FEEDBACK_FILE)
        except: pass
    return pd.DataFrame(columns=COLUMNS)

def save_feedback(row):
    db = get_storage()
    pd.concat([db, pd.DataFrame([row])], ignore_index=True).to_csv(FEEDBACK_FILE, index=False)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
MASTER_COLORS = load_master_colors()
SHIRT_COLORS  = sorted([n for n,d in MASTER_COLORS.items() if d["shirt_allowed"]])
PANT_COLORS   = sorted([n for n,d in MASTER_COLORS.items() if d["pant_allowed"]])

SEASON_META = {
    "All":    {"icon":"🌀","label":"All"},
    "Spring": {"icon":"🌸","label":"Spring"},
    "Summer": {"icon":"☀️","label":"Summer"},
    "Autumn": {"icon":"🍂","label":"Autumn"},
    "Winter": {"icon":"❄️","label":"Winter"},
}

# ── Softened, realistic skin tones ──
SKIN_META = {
    "Light_Warm":    {"hex":"#FDDBB4","label":"Warm"},
    "Light_Cool":    {"hex":"#FAE0D0","label":"Cool"},
    "Light_Neutral": {"hex":"#F8D5A8","label":"Neutral"},
    "Medium_Warm":   {"hex":"#D4956A","label":"Warm"},
    "Medium_Cool":   {"hex":"#C98B6E","label":"Cool"},
    "Medium_Neutral":{"hex":"#C07A52","label":"Neutral"},
    "Deep_Warm":     {"hex":"#8B5A3C","label":"Warm"},
    "Deep_Cool":     {"hex":"#7A4A4A","label":"Cool"},
    "Deep_Neutral":  {"hex":"#6B4535","label":"Neutral"},
}

QUALITY_STYLE = {
    "Premium":    "background:#dbeafe;color:#1e3a8a;border:1px solid #93c5fd",
    "Strong":     "background:#dcfce7;color:#166534;border:1px solid #86efac",
    "Developing": "background:#fef9c3;color:#854d0e;border:1px solid #fde047",
    "Starter":    "background:#f1f5f9;color:#475569;border:1px solid #cbd5e1",
}

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
for k,v in [("result",None),("last_input",{}),("feedback_done",False),
             ("show_all_combos",False),("selected_skin",""),
             ("selected_season","All"),("session_id",str(uuid.uuid4())[:8])]:
    if k not in st.session_state: st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def lum(h):
    h=h.lstrip("#")
    return 0.2126*int(h[0:2],16)+0.7152*int(h[2:4],16)+0.0722*int(h[4:6],16)

def text_col(h): return "#0f172a" if lum(h)>155 else "#ffffff"

def quality_label(s):
    return "Premium" if s>12 else "Strong" if s>8 else "Developing" if s>4 else "Starter"

def skin_face_svg(hex_color, size=32):
    """SVG face with softened skin tone colour."""
    is_dark = lum(hex_color) < 120
    eye_col  = "#ffffff" if is_dark else "#2a1208"
    brow_col = "#1a0a00" if not is_dark else "#c8a880"
    shadow   = "rgba(0,0,0,0.18)" if not is_dark else "rgba(0,0,0,0.30)"
    smile    = "rgba(0,0,0,0.15)" if not is_dark else "rgba(0,0,0,0.25)"
    # slightly darker shade for hair
    h=hex_color.lstrip("#")
    r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    hair = f"#{max(0,r-70):02x}{max(0,g-70):02x}{max(0,b-70):02x}"
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="18" cy="15" rx="11" ry="12" fill="{hex_color}"/>
      <ellipse cx="18" cy="14" rx="10" ry="11" fill="{hex_color}"/>
      <ellipse cx="7"  cy="15" rx="3"  ry="4"  fill="{hex_color}"/>
      <ellipse cx="29" cy="15" rx="3"  ry="4"  fill="{hex_color}"/>
      <ellipse cx="14" cy="13" rx="2.2" ry="1.6" fill="{shadow}"/>
      <ellipse cx="22" cy="13" rx="2.2" ry="1.6" fill="{shadow}"/>
      <ellipse cx="14" cy="12.5" rx="1.4" ry="1.3" fill="{eye_col}" opacity=".9"/>
      <ellipse cx="22" cy="12.5" rx="1.4" ry="1.3" fill="{eye_col}" opacity=".9"/>
      <circle  cx="14.5" cy="12" r=".6" fill="{eye_col}" opacity=".4"/>
      <circle  cx="22.5" cy="12" r=".6" fill="{eye_col}" opacity=".4"/>
      <path d="M11,8.5 Q14,6.5 17,8" stroke="{brow_col}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".7"/>
      <path d="M19,8 Q22,6.5 25,8.5" stroke="{brow_col}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".7"/>
      <ellipse cx="18" cy="18" rx="1.3" ry=".9" fill="{smile}" opacity=".6"/>
      <path d="M13,21.5 Q18,24.5 23,21.5" stroke="{smile}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".8"/>
      <ellipse cx="18" cy="28" rx="9"  ry="6" fill="{hex_color}" opacity=".6"/>
      <rect    x="9"  y="25"  width="18" height="11" rx="5" fill="{hex_color}" opacity=".4"/>
      <path d="M7,8 Q10,1 18,0 Q26,1 29,8 Q25,4 18,4 Q11,4 7,8Z" fill="{hair}"/>
    </svg>"""

def colour_pills_html(names, colors_dict):
    """Render selected colours as pills with actual colour dot."""
    if not names: return ""
    pills = ""
    for name in names:
        hex_c = colors_dict.get(name, {}).get("hex", "#888")
        pills += f"""<div class="colour-pill">
          <span class="pill-dot" style="background:{hex_c}"></span>
          {name}
        </div>"""
    return f'<div class="colour-pills">{pills}</div>'

def rect_swatch_html(items, score_key):
    html = '<div class="rect-grid">'
    for i, item in enumerate(items):
        score = item.get(score_key, 0)
        tc    = text_col(item["hex"])
        rank  = f'<div class="rect-rank">{i+1}</div>' if i==0 else ""
        star  = '<div class="rect-star">★</div>' if item.get("skin_delta",0)>0 else ""
        html += f"""
        <div class="rect-item">
          <div class="rect-block" style="background:{item['hex']}">{rank}{star}</div>
          <div class="rect-name">{item['color']}</div>
          <div class="rect-score">{score:.1f}</div>
        </div>"""
    return html + "</div>"

def mannequin_svg(shirt_hex, pant_hex, shirt_name, pant_name, width=100):
    def darker(h, a=30):
        hx=h.lstrip("#")
        r,g,b=int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
        return f"#{max(0,r-a):02x}{max(0,g-a):02x}{max(0,b-a):02x}"
    sh=darker(shirt_hex,28); ph=darker(pant_hex,28)
    sk="#D4956A"  # neutral skin
    scale = width/110
    h = int(220*scale)
    return f"""<svg width="{width}" height="{h}"
      viewBox="0 0 110 220" xmlns="http://www.w3.org/2000/svg"
      style="filter:drop-shadow(0 3px 8px rgba(15,25,80,.15))">

      <!-- shadow -->
      <ellipse cx="55" cy="216" rx="26" ry="4" fill="rgba(0,0,0,.12)"/>

      <!-- shoes -->
      <ellipse cx="41" cy="208" rx="13" ry="5" fill="#1e293b"/>
      <ellipse cx="69" cy="208" rx="13" ry="5" fill="#1e293b"/>
      <rect x="31" y="202" width="22" height="8" rx="4" fill="#1e293b"/>
      <rect x="57" y="202" width="22" height="8" rx="4" fill="#1e293b"/>

      <!-- pants -->
      <rect x="34" y="118" width="19" height="88" rx="7" fill="{pant_hex}"/>
      <rect x="57" y="118" width="19" height="88" rx="7" fill="{pant_hex}"/>
      <rect x="34" y="118" width="5"  height="88" rx="4" fill="{ph}" opacity=".3"/>
      <rect x="57" y="118" width="5"  height="88" rx="4" fill="{ph}" opacity=".3"/>

      <!-- belt -->
      <rect x="31" y="112" width="48" height="11" rx="5" fill="{ph}"/>
      <rect x="51" y="114" width="8"  height="7"  rx="2" fill="#94a3b8" opacity=".7"/>

      <!-- shirt torso -->
      <rect x="29" y="60" width="52" height="58" rx="8" fill="{shirt_hex}"/>
      <rect x="29" y="60" width="7"  height="58" rx="4" fill="{sh}" opacity=".25"/>
      <rect x="74" y="60" width="7"  height="58" rx="4" fill="{sh}" opacity=".25"/>
      <polygon points="55,62 47,73 55,77 63,73" fill="{sh}" opacity=".35"/>
      <circle cx="55" cy="82" r="1.5" fill="{sh}" opacity=".45"/>
      <circle cx="55" cy="91" r="1.5" fill="{sh}" opacity=".45"/>
      <circle cx="55" cy="100" r="1.5" fill="{sh}" opacity=".45"/>
      <rect x="36" y="71" width="13" height="10" rx="3" fill="{sh}" opacity=".2"/>

      <!-- left sleeve -->
      <path d="M29,62 Q11,67 9,93 Q8,101 17,103 Q27,105 30,97 L30,62Z" fill="{shirt_hex}"/>
      <path d="M29,62 Q19,67 17,93 Q16,101 17,103 Q11,99 9,91 Q9,69 29,62Z" fill="{sh}" opacity=".18"/>
      <ellipse cx="14" cy="106" rx="6" ry="4" fill="{sk}"/>

      <!-- right sleeve -->
      <path d="M81,62 Q99,67 101,93 Q102,101 93,103 Q83,105 80,97 L80,62Z" fill="{shirt_hex}"/>
      <path d="M81,62 Q91,67 93,93 Q94,101 93,103 Q99,99 101,91 Q101,69 81,62Z" fill="{sh}" opacity=".18"/>
      <ellipse cx="96" cy="106" rx="6" ry="4" fill="{sk}"/>

      <!-- neck -->
      <rect x="48" y="44" width="14" height="20" rx="6" fill="{sk}"/>

      <!-- head hair -->
      <ellipse cx="55" cy="26" rx="19" ry="21" fill="#2d1b00"/>
      <!-- face -->
      <ellipse cx="55" cy="28" rx="16" ry="18" fill="{sk}"/>
      <!-- ears -->
      <ellipse cx="39" cy="29" rx="3.5" ry="4.5" fill="{sk}"/>
      <ellipse cx="71" cy="29" rx="3.5" ry="4.5" fill="{sk}"/>
      <!-- eyes -->
      <ellipse cx="49" cy="25" rx="2.5" ry="2.2" fill="#1a0a00"/>
      <ellipse cx="61" cy="25" rx="2.5" ry="2.2" fill="#1a0a00"/>
      <circle cx="50" cy="24.2" r=".8" fill="white" opacity=".7"/>
      <circle cx="62" cy="24.2" r=".8" fill="white" opacity=".7"/>
      <!-- brows -->
      <path d="M45,20 Q49,18 53,19.5" stroke="#2d1b00" stroke-width="1.3" fill="none" stroke-linecap="round"/>
      <path d="M57,19.5 Q61,18 65,20" stroke="#2d1b00" stroke-width="1.3" fill="none" stroke-linecap="round"/>
      <!-- nose -->
      <ellipse cx="55" cy="30.5" rx="1.8" ry="1.3" fill="rgba(0,0,0,.12)"/>
      <!-- mouth -->
      <path d="M50,35.5 Q55,39 60,35.5" stroke="rgba(0,0,0,.2)" stroke-width="1.3" fill="none" stroke-linecap="round"/>
      <!-- hair fringe -->
      <path d="M36,20 Q40,8 55,6 Q70,8 74,20 Q69,13 55,13 Q41,13 36,20Z" fill="#2d1b00"/>

      <!-- shirt label -->
      <rect x="8"  y="66" width="44" height="13" rx="4" fill="rgba(255,255,255,.7)"/>
      <text x="30" y="75.5" text-anchor="middle" font-size="7" font-family="Plus Jakarta Sans,sans-serif"
            font-weight="600" fill="#0f172a">{shirt_name[:10]}</text>

      <!-- pant label -->
      <rect x="20" y="142" width="70" height="13" rx="4" fill="rgba(255,255,255,.7)"/>
      <text x="55" y="151.5" text-anchor="middle" font-size="7" font-family="Plus Jakarta Sans,sans-serif"
            font-weight="600" fill="#0f172a">{pant_name[:14]}</text>
    </svg>"""

def outfit_row_html(outfit, index):
    pct  = round((outfit["score"]/5)*100)
    svg  = mannequin_svg(outfit["shirt_hex"], outfit["pant_hex"],
                         outfit["shirt"], outfit["pant"], width=80)
    qual = "Excellent" if outfit["score"]>=4 else "Good" if outfit["score"]>=3 else "Decent" if outfit["score"]>=2 else "Weak"
    qc   = "#1d4ed8" if outfit["score"]>=4 else "#16a34a" if outfit["score"]>=3 else "#d97706" if outfit["score"]>=2 else "#94a3b8"
    return f"""<div class="outfit-entry">
      <div class="outfit-rank">#{index+1}</div>
      <div style="flex-shrink:0">{svg}</div>
      <div style="flex:1;min-width:0">
        <div class="outfit-name">{outfit['shirt']} + {outfit['pant']}</div>
        <div class="outfit-sub">Match score {outfit['score']:.1f} / 5.0</div>
        <div class="outfit-bar-bg">
          <div class="outfit-bar-fill" style="width:{pct}%"></div>
        </div>
      </div>
      <div style="text-align:right;flex-shrink:0">
        <div class="outfit-score-num">{outfit['score']:.1f}</div>
        <div style="font-size:9px;color:{qc};font-weight:700;margin-top:2px">{qual}</div>
      </div>
    </div>"""

def combo_card_html(combo):
    score   = combo.get("score", combo.get("pair_score", 0))
    shirt_h = combo.get("shirt_hex","#888")
    pant_h  = combo.get("pant_hex","#888")
    shirt   = combo.get("shirt","")
    pant    = combo.get("pant","")
    svg     = mannequin_svg(shirt_h, pant_h, shirt, pant, width=70)
    pct     = round((score/5)*100)
    qual    = "Excellent" if score>=4 else "Good" if score>=3 else "Decent" if score>=2 else "Weak"
    qc      = "#1d4ed8" if score>=4 else "#16a34a" if score>=3 else "#d97706" if score>=2 else "#94a3b8"
    return f"""<div class="combo-cell">
      {svg}
      <div style="font-size:10px;color:#334155;text-align:center;line-height:1.4;font-weight:500">{shirt}<br>{pant}</div>
      <div style="display:flex;align-items:center;justify-content:space-between;width:100%">
        <span style="font-size:9px;font-weight:700;color:{qc}">{qual}</span>
        <span style="font-size:11px;color:#3b82f6;font-weight:700;font-family:monospace">{score:.1f}</span>
      </div>
      <div style="width:100%;height:3px;background:#e2e8f0;border-radius:2px;overflow:hidden">
        <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#1d4ed8,#3b82f6);border-radius:2px"></div>
      </div>
    </div>"""

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
      <div style="width:34px;height:34px;border-radius:10px;
                  background:linear-gradient(135deg,#1d4ed8,#3b82f6);
                  display:flex;align-items:center;justify-content:center;
                  box-shadow:0 3px 10px rgba(29,78,216,.3)">
        <span style="color:#fff;font-size:17px;font-family:'Lora',serif;font-weight:700">W</span>
      </div>
      <div>
        <div style="font-size:15px;font-weight:700;color:#0f172a;
                    font-family:'Lora',serif;letter-spacing:-.2px">
          Wardrobe <span style="color:#3b82f6">Engine</span>
        </div>
        <div style="font-size:10px;color:#94a3b8;margin-top:1px">Personal Colour Intelligence</div>
      </div>
    </div>
    <div style="height:1px;background:#e2e8f0;margin:14px 0 18px"></div>
    """, unsafe_allow_html=True)

    # ── SHIRTS ──
    st.markdown('<div class="sb-label">① Shirts you own</div>', unsafe_allow_html=True)
    selected_shirts = st.multiselect(
        "shirts", SHIRT_COLORS,
        label_visibility="collapsed",
        placeholder="Choose shirt colours…",
    )
    st.markdown(
        colour_pills_html(selected_shirts, MASTER_COLORS),
        unsafe_allow_html=True
    )

    # ── PANTS ──
    st.markdown('<div class="sb-label">② Pants you own</div>', unsafe_allow_html=True)
    selected_pants = st.multiselect(
        "pants", PANT_COLORS,
        label_visibility="collapsed",
        placeholder="Choose pant colours…",
    )
    st.markdown(
        colour_pills_html(selected_pants, MASTER_COLORS),
        unsafe_allow_html=True
    )

    # ── SEASON ──
    st.markdown('<div class="sb-label">③ Season</div>', unsafe_allow_html=True)
    seas_cols = st.columns(5)
    for col, (key, meta) in zip(seas_cols, SEASON_META.items()):
        is_sel = st.session_state.selected_season == key
        with col:
            border = "#1d4ed8" if is_sel else "#dde3ea"
            bg     = "#eff6ff" if is_sel else "#f8fafc"
            nc     = "#1d4ed8" if is_sel else "#8896a8"
            if st.button(meta["icon"], key=f"s_{key}", help=key, use_container_width=True):
                st.session_state.selected_season = key
                st.rerun()
            st.markdown(
                f'<div style="text-align:center;font-size:8px;font-weight:700;'
                f'letter-spacing:.07em;text-transform:uppercase;margin-top:-6px;'
                f'color:{nc}">{meta["label"]}</div>',
                unsafe_allow_html=True
            )
    selected_season = st.session_state.selected_season
    # show selected season indicator
    if selected_season != "All":
        st.markdown(
            f'<div style="margin-top:6px;padding:5px 10px;border-radius:8px;'
            f'background:#eff6ff;border:1px solid #bfdbfe;'
            f'font-size:11px;color:#1d4ed8;font-weight:600;display:inline-block">'
            f'{SEASON_META[selected_season]["icon"]} {selected_season} selected</div>',
            unsafe_allow_html=True
        )

    # ── SKIN TONE ──
    st.markdown('<div class="sb-label">④ Skin tone <span style="color:#94a3b8;font-weight:400;text-transform:none;letter-spacing:0;font-size:9px">(optional)</span></div>', unsafe_allow_html=True)

    for depth, keys in [
        ("Light",  ["Light_Warm",  "Light_Cool",  "Light_Neutral"]),
        ("Medium", ["Medium_Warm", "Medium_Cool", "Medium_Neutral"]),
        ("Deep",   ["Deep_Warm",   "Deep_Cool",   "Deep_Neutral"]),
    ]:
        st.markdown(f'<div class="depth-row-label">{depth}</div>', unsafe_allow_html=True)
        skin_cols = st.columns(3)
        for col, key in zip(skin_cols, keys):
            meta   = SKIN_META[key]
            is_sel = st.session_state.selected_skin == key
            with col:
                border = "#1d4ed8" if is_sel else "#dde3ea"
                bg     = "#eff6ff" if is_sel else "#f8fafc"
                lc     = "#1d4ed8" if is_sel else "#64748b"
                face   = skin_face_svg(meta["hex"], size=32)
                st.markdown(
                    f'<div class="skin-card {"sel" if is_sel else ""}" '
                    f'style="border-color:{border};background:{bg}">'
                    f'{face}'
                    f'<div class="skin-lbl" style="color:{lc}">{meta["label"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button("·", key=f"sk_{key}", help=key.replace("_"," "),
                             use_container_width=True):
                    st.session_state.selected_skin = "" if is_sel else key
                    st.rerun()

    selected_skin = st.session_state.selected_skin
    if selected_skin:
        meta = SKIN_META[selected_skin]
        face = skin_face_svg(meta["hex"], size=16)
        st.markdown(
            f'<div style="margin-top:8px;padding:7px 12px;border-radius:9px;'
            f'background:#eff6ff;border:1px solid #bfdbfe;'
            f'display:flex;align-items:center;gap:8px;'
            f'font-size:11px;color:#1d4ed8;font-weight:600">'
            f'{face} {selected_skin.replace("_"," ")} · active ✓</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    # ── GENERATE ──
    has_input = bool(selected_shirts or selected_pants)
    run = st.button(
        "✦  Generate My Colour Profile" if has_input else "Generate My Colour Profile",
        type="primary", use_container_width=True, disabled=not has_input,
    )
    if not has_input:
        st.markdown(
            '<div style="font-size:10px;color:#94a3b8;text-align:center;margin-top:6px">'
            'Select at least one colour to begin</div>',
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────────────────────
# RUN ENGINE
# ─────────────────────────────────────────────────────────────
if run:
    st.session_state.feedback_done   = False
    st.session_state.show_all_combos = False
    with st.spinner("Analysing your colour network…"):
        result = generate_recommendations({
            "shirts":       selected_shirts,
            "pants":        selected_pants,
            "season":       selected_season,
            "skin_profile": selected_skin or None,
        })
    st.session_state.result     = result
    st.session_state.last_input = {
        "shirts":selected_shirts, "pants":selected_pants,
        "season":selected_season, "skin":selected_skin,
    }

# ─────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────
if st.session_state.result is None:
    st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)
    _, c, _ = st.columns([1,2,1])
    with c:
        st.markdown("""
        <div style="text-align:center;padding:56px 40px;background:#ffffff;
                    border:1px solid #e2e8f0;border-radius:24px;
                    box-shadow:0 4px 20px rgba(15,25,80,.07)">
          <div style="font-size:52px;margin-bottom:16px">👔</div>
          <div style="font-family:'Lora',serif;font-size:28px;font-weight:700;
                      color:#0f172a;margin-bottom:10px">Your colour profile awaits</div>
          <div style="font-size:13px;color:#64748b;line-height:1.8;
                      max-width:300px;margin:0 auto">
            Select colours you already own from the sidebar.
            The engine recommends what to buy next — scored by compatibility,
            season and skin tone.
          </div>
          <div style="margin-top:24px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
            <span style="font-size:11px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:5px 12px;border-radius:20px">Smart shirt picks</span>
            <span style="font-size:11px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:5px 12px;border-radius:20px">Smart pant picks</span>
            <span style="font-size:11px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:5px 12px;border-radius:20px">Outfit combinations</span>
            <span style="font-size:11px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:5px 12px;border-radius:20px">Folded stack visuals</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────
result   = st.session_state.result
inp      = st.session_state.last_input
top_sc   = result["smart_shirts"][0]["shirt_score"] if result["smart_shirts"] else 0
qual     = quality_label(top_sc)
skin_lbl = inp["skin"].replace("_"," ") if inp["skin"] else "Universal"
season_d = inp["season"] if inp["season"]!="All" else "All Seasons"
s_icon   = SEASON_META[inp["season"]]["icon"]

st.markdown(f"""
<div class="page-header">{s_icon} Your Colour Profile</div>
<div class="page-sub">
  {len(inp['shirts'])} shirt{'s' if len(inp['shirts'])!=1 else ''}
  · {len(inp['pants'])} pant{'s' if len(inp['pants'])!=1 else ''}
  · {season_d} · {skin_lbl}
</div>
""", unsafe_allow_html=True)

col_card, col_outfits = st.columns([1.05,1], gap="large")

# ── PROFILE CARD ──────────────────────────────────────────────
with col_card:
    qs = QUALITY_STYLE[qual]
    card = f"""<div class="profile-card">
      <div class="card-accent"></div>
      <div class="card-eyebrow">Wardrobe Engine · Colour Profile</div>
      <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:4px">
        <div class="card-title">Your Style Profile</div>
        <span class="q-badge" style="{qs}">{qual}</span>
      </div>
      <div class="card-meta">{s_icon} {season_d} · {skin_lbl}</div>
      <div class="card-divider"></div>"""
    if result["smart_shirts"]:
        card += '<div class="sec-label">Smart Shirts to Buy</div>'
        card += rect_swatch_html(result["smart_shirts"],"shirt_score")
    if result["smart_pants"]:
        card += '<div class="sec-label">Smart Pants to Buy</div>'
        card += rect_swatch_html(result["smart_pants"],"pant_score")
    if result["all_season_neutrals"]:
        card += '<div class="sec-label">All-Season Neutrals</div>'
        card += rect_swatch_html(result["all_season_neutrals"],"neutral_score")
    card += f"""<div class="card-divider"></div>
      <div style="display:flex;justify-content:space-between;font-size:9px;color:#94a3b8">
        <span>{s_icon} {season_d} · {skin_lbl}</span>
        <span style="font-family:'DM Mono',monospace;letter-spacing:.06em">wardrobeengine.com</span>
      </div></div>"""
    st.markdown(card, unsafe_allow_html=True)

# ── OUTFITS ───────────────────────────────────────────────────
with col_outfits:
    st.markdown('<div class="sec-label" style="margin-bottom:14px">Top Outfit Combinations</div>', unsafe_allow_html=True)
    for i, o in enumerate(result.get("outfits",[])):
        st.markdown(outfit_row_html(o,i), unsafe_allow_html=True)

    all_combos = result.get("pair_matrix",[])
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    if not st.session_state.show_all_combos:
        st.markdown(
            f'<div class="prompt-bubble">'
            f'<div><div class="pb-q">See all outfit combinations?</div>'
            f'<div class="pb-sub">{len(all_combos)} possible pairings</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("Show all ✦", use_container_width=True):
                st.session_state.show_all_combos = True
                st.rerun()
        with bc2:
            if st.button("Skip", use_container_width=True):
                pass
    else:
        st.markdown(
            f'<div style="font-size:12px;font-weight:600;color:#0f172a;margin-bottom:14px">'
            f'All combinations <span style="color:#94a3b8;font-weight:400">· {len(all_combos)} pairings</span></div>',
            unsafe_allow_html=True
        )
        cols3 = st.columns(3)
        for i, combo in enumerate(all_combos):
            with cols3[i%3]:
                st.markdown(combo_card_html(combo), unsafe_allow_html=True)
        if st.button("Hide combinations ↑", use_container_width=True):
            st.session_state.show_all_combos = False
            st.rerun()

# ─────────────────────────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#dde3ea,transparent);margin-bottom:40px"></div>', unsafe_allow_html=True)

if st.session_state.feedback_done:
    _, c, _ = st.columns([1,2,1])
    with c:
        st.markdown("""
        <div class="thankyou">
          <div style="font-size:48px;margin-bottom:16px">🙏</div>
          <div class="ty-title">Thank you!</div>
          <div class="ty-sub">Your feedback shapes the ₹299 colour card.<br>We'll build a better product because of it.</div>
        </div>
        """, unsafe_allow_html=True)
else:
    _, c, _ = st.columns([1,2,1])
    with c:
        st.markdown('<div class="feedback-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="fb-title">Share your feedback</div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-sub">2 minutes · helps us build a better product</div>', unsafe_allow_html=True)

        st.markdown('<div class="fb-label">How useful were these recommendations?</div>', unsafe_allow_html=True)
        star_rating = st.select_slider(
            "star_rating", options=[1,2,3,4,5], value=4,
            format_func=lambda x:"⭐"*x,
            label_visibility="collapsed",
        )
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-label">Would you buy a personalised colour card for ₹299?</div>', unsafe_allow_html=True)
        buy_card = st.radio(
            "buy_card",
            ["Yes — I'd buy this","Maybe — need to see the physical card","No — not for me"],
            label_visibility="collapsed",
        )
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-label">How likely are you to recommend this to a friend?</div>', unsafe_allow_html=True)
        st.caption("0 = Not at all · 10 = Definitely")
        nps = st.slider("nps", 0, 10, 7, label_visibility="collapsed")
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

        if st.button("Submit Feedback →", type="primary", use_container_width=True):
            outfits = result.get("outfits",[])
            top_o   = f"{outfits[0]['shirt']} + {outfits[0]['pant']}" if outfits else ""
            save_feedback({
                "id":           st.session_state.session_id,
                "timestamp":    datetime.utcnow().isoformat(),
                "shirts_input": ", ".join(inp["shirts"]),
                "pants_input":  ", ".join(inp["pants"]),
                "season":       inp["season"],
                "skin_profile": inp["skin"],
                "smart_shirts": ", ".join([r["color"] for r in result["smart_shirts"]]),
                "smart_pants":  ", ".join([r["color"] for r in result["smart_pants"]]),
                "neutrals":     ", ".join([r["color"] for r in result["all_season_neutrals"]]),
                "top_outfit":   top_o,
                "star_rating":  star_rating,
                "buy_card":     buy_card,
                "nps_score":    nps,
            })
            st.session_state.feedback_done = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────────────────────
if st.query_params.get("admin") == "true":
    st.markdown("---")
    st.markdown("### 📊 Feedback Dashboard")
    admin_pw = st.secrets.get("ADMIN_PASSWORD","")
    entered  = st.text_input("Admin password", type="password", key="admin_pw_input")
    if entered != admin_pw:
        st.error("Incorrect password.") if entered else st.info("Enter the admin password.")
        st.stop()
    db = get_storage()
    if db.empty:
        st.info("No feedback yet.")
        st.stop()
    total    = len(db)
    avg_star = round(db["star_rating"].mean(),1)
    avg_nps  = round(db["nps_score"].mean(),1)
    buy_yes  = round(db["buy_card"].str.startswith("Yes").sum()/total*100)
    m1,m2,m3,m4 = st.columns(4)
    for col,val,lbl in [(m1,total,"Responses"),(m2,f"{avg_star}⭐","Avg Rating"),
                        (m3,avg_nps,"Avg NPS"),(m4,f"{buy_yes}%","Would Buy")]:
        col.markdown(
            f'<div class="metric-tile"><div class="metric-val">{val}</div>'
            f'<div class="metric-lbl">{lbl}</div></div>',
            unsafe_allow_html=True
        )
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        st.markdown("**Buy card responses**")
        st.bar_chart(db["buy_card"].value_counts())
    with cb:
        st.markdown("**Most recommended shirts**")
        st.bar_chart(db["smart_shirts"].str.split(", ").explode().value_counts().head(8))
    st.dataframe(db, use_container_width=True)
    st.download_button("⬇ Download CSV", data=db.to_csv(index=False),
                       file_name="wardrobe_feedback.csv", mime="text/csv")

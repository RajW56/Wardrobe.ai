import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os
import base64
from wardrobe_engine import (
    generate_recommendations,
    load_master_colors,
    SKIN_PROFILES,
    build_color_objects,
    get_match_strength,
    wardrobe_gap_analysis,
)

st.set_page_config(
    page_title="Wardrobe Engine",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Lora:wght@600;700&family=DM+Mono:wght@400&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: #f0f4f8; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── All buttons default: light outlined ── */
.stButton > button {
    background: #ffffff !important; color: #1e3a8a !important;
    border: 1.5px solid #bfdbfe !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 12px !important;
    padding: 7px 12px !important; transition: all .15s !important;
    box-shadow: 0 1px 3px rgba(15,25,80,.08) !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: #eff6ff !important; border-color: #93c5fd !important;
}

/* ── Generate button: primary blue ── */
div[data-testid="stVerticalBlock"] div.generate-btn .stButton > button {
    background: linear-gradient(135deg,#1d4ed8,#3b82f6) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 12px !important; font-size: 14px !important;
    padding: 14px 24px !important;
    box-shadow: 0 4px 14px rgba(29,78,216,.3) !important;
}

/* ── Colour swatch buttons: square, just the colour ── */
button[data-swatch="true"] {
    width: 44px !important; height: 44px !important;
    padding: 0 !important; border-radius: 10px !important;
    min-height: unset !important; font-size: 0px !important;
    line-height: 0 !important;
}

/* Streamlit widget resets */
.stMultiSelect > div > div { background:#f8fafc !important; border-color:#bfdbfe !important; }
.stRadio label, .stRadio label p, .stRadio span { color:#0f172a !important; font-size:13px !important; }
[data-testid="stSelectSlider"] > div { color:#1d4ed8 !important; }
.stSlider > div > div > div { background:#3b82f6 !important; }
[data-testid="stTickBarMin"],[data-testid="stTickBarMax"] { color:#64748b !important; }
.stCaption, .stCaption p { color:#94a3b8 !important; }
div[data-testid="stMarkdownContainer"] p { color:#334155; }

/* ── Section labels ── */
.step-label {
    font-size:11px; font-weight:700; letter-spacing:.12em;
    text-transform:uppercase; color:#64748b;
    margin-bottom:10px; display:flex; align-items:center; gap:8px;
}
.step-label::after { content:''; flex:1; height:1px; background:#e2e8f0; }

/* ── Colour swatch grid ── */
.swatch-grid-wrap { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px; }
.swatch-cell {
    display:flex; flex-direction:column; align-items:center; gap:3px; width:48px;
}
.swatch-btn {
    width:44px; height:44px; border-radius:10px; cursor:pointer;
    border:2.5px solid transparent; transition:all .15s;
    box-shadow:0 1px 4px rgba(0,0,0,.12);
    position:relative; display:flex; align-items:center; justify-content:center;
}
.swatch-btn:hover { transform:scale(1.08); box-shadow:0 3px 8px rgba(0,0,0,.2); }
.swatch-btn.sel {
    border-color:#1d4ed8 !important;
    box-shadow:0 0 0 3px rgba(29,78,216,.25),0 2px 8px rgba(0,0,0,.2) !important;
    transform:scale(1.08);
}
.swatch-check {
    width:16px; height:16px; border-radius:50%;
    background:#1d4ed8; color:white;
    font-size:10px; font-weight:700;
    display:flex; align-items:center; justify-content:center;
    position:absolute; top:-4px; right:-4px;
    box-shadow:0 1px 3px rgba(0,0,0,.3);
}
.swatch-name {
    font-size:8px; color:#64748b; text-align:center;
    line-height:1.2; width:48px; font-weight:500;
}
.swatch-name.sel { color:#1d4ed8; font-weight:700; }

/* ── Selected pills ── */
.colour-pills { display:flex; flex-wrap:wrap; gap:5px; margin:4px 0 8px; }
.colour-pill {
    display:flex; align-items:center; gap:5px;
    padding:3px 10px 3px 5px; border-radius:20px;
    background:#eff6ff; border:1px solid #bfdbfe;
    font-size:11px; color:#1e3a8a; font-weight:500;
}
.pill-dot { width:12px; height:12px; border-radius:50%; flex-shrink:0; border:1px solid rgba(0,0,0,.1); }

/* ── Season buttons ── */
.depth-row-label { font-size:9px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#8896a8; margin:8px 0 4px; }

/* ── Profile card ── */
.profile-card {
    background:#ffffff; border:1px solid #e2e8f0;
    border-radius:20px; padding:24px;
    box-shadow:0 4px 20px rgba(15,25,80,.07); position:relative; overflow:hidden;
}
.card-accent { position:absolute; top:0; left:0; right:0; height:4px;
    background:linear-gradient(90deg,#1d4ed8,#3b82f6,#93c5fd,#3b82f6,#1d4ed8); }
.card-eyebrow { font-size:9px; letter-spacing:.18em; color:#3b82f6; font-weight:700; text-transform:uppercase; margin-bottom:5px; }
.card-title { font-family:'Lora',serif; font-size:22px; font-weight:700; color:#0f172a; margin-bottom:2px; }
.card-meta { font-size:11px; color:#94a3b8; margin-bottom:18px; }
.card-divider { height:1px; background:linear-gradient(90deg,transparent,#e2e8f0,transparent); margin:14px 0; }
.sec-label { font-size:9px; font-weight:700; letter-spacing:.15em; text-transform:uppercase;
    color:#94a3b8; margin:0 0 10px; display:flex; align-items:center; gap:8px; }
.sec-label::before { content:''; width:10px; height:2px;
    background:linear-gradient(90deg,#1d4ed8,#3b82f6); border-radius:2px; }

/* ── Rectangular swatches ── */
.rect-grid { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:16px; }
.rect-item { display:flex; flex-direction:column; align-items:center; gap:4px; }
.rect-block { width:60px; height:90px; border-radius:11px; position:relative;
    box-shadow:0 3px 10px rgba(0,0,0,.12); transition:transform .15s; }
.rect-block:hover { transform:translateY(-3px); }
.rect-name { font-size:9px; color:#475569; text-align:center; max-width:64px; line-height:1.3; font-weight:600; }
.rect-score { font-size:9px; color:#3b82f6; font-weight:700; font-family:'DM Mono',monospace; }
.rect-rank { position:absolute; top:-5px; right:-5px; width:15px; height:15px;
    border-radius:50%; background:#1d4ed8; color:white; font-size:8px; font-weight:700;
    display:flex; align-items:center; justify-content:center; box-shadow:0 2px 4px rgba(29,78,216,.4); }
.rect-star { position:absolute; bottom:-5px; right:-5px; width:15px; height:15px;
    border-radius:50%; background:#f97316; color:white; font-size:9px;
    display:flex; align-items:center; justify-content:center; }
.q-badge { display:inline-block; padding:4px 12px; border-radius:20px; font-size:10px; font-weight:700; }

/* ── Outfit rows ── */
.outfit-entry { display:flex; align-items:center; gap:14px; padding:10px 14px;
    border-radius:14px; background:#ffffff; border:1px solid #e2e8f0;
    margin-bottom:8px; transition:all .15s; box-shadow:0 1px 4px rgba(15,25,80,.05); }
.outfit-entry:hover { border-color:#93c5fd; box-shadow:0 3px 12px rgba(59,130,246,.1); }
.outfit-rank { font-size:11px; color:#94a3b8; font-weight:700;
    font-family:'DM Mono',monospace; width:22px; text-align:center; flex-shrink:0; }
.outfit-name { font-size:12px; color:#0f172a; font-weight:600; }
.outfit-sub  { font-size:10px; color:#94a3b8; margin-top:2px; }
.outfit-bar-bg { height:3px; background:#e2e8f0; border-radius:2px; overflow:hidden; margin-top:4px; }
.outfit-bar-fill { height:100%; border-radius:2px; background:linear-gradient(90deg,#1d4ed8,#3b82f6); }
.outfit-score-num { font-size:12px; color:#3b82f6; font-weight:700; font-family:'DM Mono',monospace; }

/* ── Combo card ── */
.combo-cell { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
    padding:12px 8px; display:flex; flex-direction:column; align-items:center; gap:8px;
    transition:all .15s; box-shadow:0 1px 3px rgba(15,25,80,.04); }
.combo-cell:hover { border-color:#93c5fd; }

/* ── Gap analysis ── */
.metric-tile { background:#ffffff; border:1px solid #e2e8f0; border-radius:12px;
    padding:14px 16px; box-shadow:0 1px 4px rgba(15,25,80,.05); }
.metric-val { font-family:'Lora',serif; font-size:22px; color:#0f172a; font-weight:700; }
.metric-lbl { font-size:11px; font-weight:600; color:#475569; }
.metric-sub { font-size:10px; color:#94a3b8; margin-top:3px; }

/* ── Feedback ── */
.feedback-wrap { background:#ffffff; border:1px solid #e2e8f0; border-radius:20px;
    padding:32px; max-width:560px; margin:0 auto; box-shadow:0 4px 20px rgba(15,25,80,.07); }
.fb-title { font-family:'Lora',serif; font-size:22px; font-weight:700; color:#0f172a; margin-bottom:5px; }
.fb-sub { font-size:12px; color:#64748b; margin-bottom:20px; }
.fb-label { font-size:12px; font-weight:600; color:#1e3a8a; margin-bottom:6px; }
.thankyou { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:16px;
    padding:32px; text-align:center; max-width:480px; margin:0 auto; }

/* ── Admin ── */
.adm-tile { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
    padding:18px; text-align:center; }
.adm-val { font-family:'Lora',serif; font-size:28px; color:#1d4ed8; font-weight:700; }
.adm-lbl { font-size:11px; color:#64748b; margin-top:3px; }
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
SHIRT_COLORS  = [(n, d["hex"]) for n,d in MASTER_COLORS.items() if d["shirt_allowed"]]
PANT_COLORS   = [(n, d["hex"]) for n,d in MASTER_COLORS.items() if d["pant_allowed"]]
SHIRT_NAMES   = [n for n,_ in SHIRT_COLORS]
PANT_NAMES    = [n for n,_ in PANT_COLORS]

SEASON_META = {
    "All":    {"icon":"🌀","label":"All"},
    "Spring": {"icon":"🌸","label":"Spring"},
    "Summer": {"icon":"☀️","label":"Summer"},
    "Autumn": {"icon":"🍂","label":"Autumn"},
    "Winter": {"icon":"❄️","label":"Winter"},
}

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
for k,v in [
    ("result",None),("last_input",{}),("feedback_done",False),
    ("show_all_combos",False),("selected_skin",""),
    ("selected_season","All"),("session_id",str(uuid.uuid4())[:8]),
    ("sel_shirts",set()),("sel_pants",set()),
]:
    if k not in st.session_state: st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def lum(h):
    h=h.lstrip("#")
    return 0.2126*int(h[0:2],16)+0.7152*int(h[2:4],16)+0.0722*int(h[4:6],16)

def darker(h, amt=22):
    hx=h.lstrip("#")
    r,g,b=int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
    return f"#{max(0,r-amt):02x}{max(0,g-amt):02x}{max(0,b-amt):02x}"

def lighter(h, amt=30):
    hx=h.lstrip("#")
    r,g,b=int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
    return f"#{min(255,r+amt):02x}{min(255,g+amt):02x}{min(255,b+amt):02x}"

def quality_label(s):
    return "Premium" if s>12 else "Strong" if s>8 else "Developing" if s>4 else "Starter"

def svg_b64_img(svg_str, width, height):
    b64 = base64.b64encode(svg_str.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{b64}" width="{width}" height="{height}" style="display:block;flex-shrink:0"/>'

def mannequin_svg(shirt_hex="#87CEEB", pant_hex="#001F5B", skin_hex="#D4956A"):
    """Stylised fashion illustration mannequin — posed, with face, hands and feet."""
    sh_d = darker(shirt_hex, 25)
    sh_l = lighter(shirt_hex, 22)
    pt_d = darker(pant_hex, 20)
    sk_d = darker(skin_hex, 20)
    hx=skin_hex.lstrip("#")
    sr,sg,sb=int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
    hair = "#2d1b00" if (0.2126*sr+0.7152*sg+0.0722*sb)>100 else "#1a0a00"

    return f"""<svg width="90" height="160" viewBox="0 0 90 160" xmlns="http://www.w3.org/2000/svg">
  <!-- shadow -->
  <ellipse cx="45" cy="157" rx="18" ry="3" fill="rgba(0,0,0,0.12)"/>
  <!-- shoes -->
  <ellipse cx="36" cy="152" rx="9" ry="4" fill="#1e1e2e" transform="rotate(-5,36,152)"/>
  <rect x="29" y="148" width="14" height="6" rx="3" fill="#1e1e2e" transform="rotate(-5,36,152)"/>
  <ellipse cx="54" cy="153" rx="9" ry="4" fill="#252535" transform="rotate(8,54,153)"/>
  <rect x="47" y="149" width="14" height="6" rx="3" fill="#252535" transform="rotate(8,54,153)"/>
  <!-- legs -->
  <path d="M 36,108 C 34,120 33,132 33,148" stroke="{pant_hex}" stroke-width="10" stroke-linecap="round" fill="none"/>
  <path d="M 36,108 C 34.5,120 33.8,132 33.8,144" stroke="{pt_d}" stroke-width="1.5" stroke-linecap="round" fill="none" opacity="0.4"/>
  <path d="M 52,108 C 54,120 55,133 57,149" stroke="{pant_hex}" stroke-width="10" stroke-linecap="round" fill="none"/>
  <path d="M 52,108 C 54,120 55,133 56,145" stroke="{pt_d}" stroke-width="1.5" stroke-linecap="round" fill="none" opacity="0.4"/>
  <!-- waistband -->
  <rect x="33" y="104" width="24" height="8" rx="3" fill="{pt_d}"/>
  <rect x="42" y="105" width="6" height="5" rx="1" fill="#888" opacity="0.7"/>
  <rect x="44" y="106" width="2" height="3" rx="0.5" fill="#aaa" opacity="0.6"/>
  <!-- left arm — relaxed, slightly away -->
  <path d="M 30,62 C 22,68 18,78 17,90" stroke="{shirt_hex}" stroke-width="9" stroke-linecap="round" fill="none"/>
  <path d="M 17,90 C 16,94 16,97 17,99" stroke="{sh_d}" stroke-width="9" stroke-linecap="round" fill="none"/>
  <ellipse cx="17" cy="102" rx="5" ry="4" fill="{skin_hex}" transform="rotate(-10,17,102)"/>
  <path d="M 13,101 Q 12,104 14,105" stroke="{sk_d}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <path d="M 17,103 Q 16,106 18,106" stroke="{sk_d}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <path d="M 20,102 Q 21,105 20,106" stroke="{sk_d}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <!-- right arm — slightly bent/posed -->
  <path d="M 60,62 C 68,70 71,80 70,92" stroke="{shirt_hex}" stroke-width="9" stroke-linecap="round" fill="none"/>
  <path d="M 70,92 C 70,96 69,99 68,101" stroke="{sh_d}" stroke-width="9" stroke-linecap="round" fill="none"/>
  <ellipse cx="68" cy="104" rx="5" ry="4" fill="{skin_hex}" transform="rotate(15,68,104)"/>
  <path d="M 64,103 Q 63,106 65,107" stroke="{sk_d}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <path d="M 68,105 Q 67,108 69,108" stroke="{sk_d}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <path d="M 71,104 Q 73,107 72,108" stroke="{sk_d}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <!-- shirt torso — tapered silhouette -->
  <path d="M 28,58 C 26,72 27,88 30,106 L 60,106 C 63,88 64,72 62,58 Z" fill="{shirt_hex}"/>
  <path d="M 28,58 C 26,72 27,88 30,106 L 34,106 C 32,88 31,72 32,58 Z" fill="{sh_d}" opacity="0.3"/>
  <path d="M 62,58 C 64,72 63,88 60,106 L 56,106 C 57,88 58,72 58,58 Z" fill="{sh_d}" opacity="0.25"/>
  <path d="M 40,60 C 40,74 40,88 41,104" stroke="{sh_l}" stroke-width="1" stroke-linecap="round" fill="none" opacity="0.35"/>
  <path d="M 45,56 L 36,64 L 45,70 Z" fill="{sh_d}" opacity="0.5"/>
  <path d="M 45,56 L 54,64 L 45,70 Z" fill="{sh_d}" opacity="0.35"/>
  <line x1="45" y1="70" x2="45" y2="103" stroke="{sh_d}" stroke-width="1.2" stroke-dasharray="2,3" opacity="0.5"/>
  <rect x="33" y="72" width="11" height="9" rx="2" fill="{sh_d}" opacity="0.2"/>
  <!-- neck -->
  <path d="M 40,54 C 40,50 50,50 50,54 L 50,60 C 50,62 40,62 40,60 Z" fill="{skin_hex}"/>
  <!-- head - hair back -->
  <ellipse cx="45" cy="30" rx="15" ry="17" fill="{hair}"/>
  <!-- face -->
  <ellipse cx="45" cy="31" rx="13" ry="15" fill="{skin_hex}"/>
  <ellipse cx="32" cy="31" rx="3" ry="4" fill="{skin_hex}"/>
  <ellipse cx="58" cy="31" rx="3" ry="4" fill="{skin_hex}"/>
  <!-- hair fringe -->
  <path d="M 32,18 Q 35,10 45,8 Q 55,10 58,18 Q 52,14 45,14 Q 38,14 32,18 Z" fill="{hair}"/>
  <!-- eyes -->
  <ellipse cx="40" cy="28" rx="3.5" ry="2.5" fill="rgba(0,0,0,0.1)"/>
  <ellipse cx="50" cy="28" rx="3.5" ry="2.5" fill="rgba(0,0,0,0.1)"/>
  <ellipse cx="40" cy="27.5" rx="2.5" ry="2.2" fill="#1a0a00"/>
  <ellipse cx="50" cy="27.5" rx="2.5" ry="2.2" fill="#1a0a00"/>
  <circle cx="41" cy="26.5" r="0.9" fill="white" opacity="0.8"/>
  <circle cx="51" cy="26.5" r="0.9" fill="white" opacity="0.8"/>
  <!-- eyebrows -->
  <path d="M 36.5,23.5 Q 40,21.5 43.5,23" stroke="{hair}" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M 46.5,23 Q 50,21.5 53.5,23.5" stroke="{hair}" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <!-- nose -->
  <path d="M 44,30 Q 43,34 45,35 Q 47,34 46,30" stroke="{sk_d}" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.5"/>
  <!-- mouth — slight smile -->
  <path d="M 41,38.5 Q 45,41.5 49,38.5" stroke="{sk_d}" stroke-width="1.4" fill="none" stroke-linecap="round" opacity="0.7"/>
  <path d="M 41,38.5 Q 40.5,39.5 41.5,40" stroke="{sk_d}" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.5"/>
  <path d="M 49,38.5 Q 49.5,39.5 48.5,40" stroke="{sk_d}" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.5"/>
</svg>"""

def mannequin_img(shirt_hex, pant_hex, skin_hex="#D4956A", width=90, height=160):
    svg = mannequin_svg(shirt_hex, pant_hex, skin_hex)
    return svg_b64_img(svg, width, height)

def skin_face_svg(hex_color, size=32):
    is_dark = lum(hex_color) < 120
    eye_col = "#ffffff" if is_dark else "#2a1208"
    brow_col = "#1a0a00" if not is_dark else "#d4b896"
    shadow = "rgba(0,0,0,0.18)" if not is_dark else "rgba(0,0,0,0.30)"
    h=hex_color.lstrip("#"); r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    hair = f"#{max(0,r-70):02x}{max(0,g-70):02x}{max(0,b-70):02x}"
    svg = (
        f'<svg width="{size}" height="{size}" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg" style="display:block">'
        f'<ellipse cx="18" cy="15" rx="11" ry="12" fill="{hex_color}"/>'
        f'<ellipse cx="7" cy="15" rx="3" ry="4" fill="{hex_color}"/>'
        f'<ellipse cx="29" cy="15" rx="3" ry="4" fill="{hex_color}"/>'
        f'<ellipse cx="14" cy="13" rx="2.2" ry="1.6" fill="{shadow}"/>'
        f'<ellipse cx="22" cy="13" rx="2.2" ry="1.6" fill="{shadow}"/>'
        f'<ellipse cx="14" cy="12.5" rx="1.4" ry="1.3" fill="{eye_col}" opacity=".9"/>'
        f'<ellipse cx="22" cy="12.5" rx="1.4" ry="1.3" fill="{eye_col}" opacity=".9"/>'
        f'<path d="M11,8.5 Q14,6.5 17,8" stroke="{brow_col}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".7"/>'
        f'<path d="M19,8 Q22,6.5 25,8.5" stroke="{brow_col}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".7"/>'
        f'<path d="M13,21.5 Q18,24.5 23,21.5" stroke="{shadow}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".8"/>'
        f'<ellipse cx="18" cy="28" rx="9" ry="6" fill="{hex_color}" opacity=".6"/>'
        f'<path d="M7,8 Q10,1 18,0 Q26,1 29,8 Q25,4 18,4 Q11,4 7,8Z" fill="{hair}"/>'
        f'</svg>'
    )
    return svg_b64_img(svg, size, size)

def colour_pills_html(names):
    if not names: return ""
    pills = "".join([
        f'<div class="colour-pill">'
        f'<span class="pill-dot" style="background:{MASTER_COLORS.get(n,{}).get("hex","#888")}"></span>'
        f'{n}</div>'
        for n in names
    ])
    return f'<div class="colour-pills">{pills}</div>'

def colour_swatch_grid(color_list, selected_set, key_prefix, n_cols=6):
    """Render a visual colour swatch grid with click-to-select."""
    rows = [color_list[i:i+n_cols] for i in range(0, len(color_list), n_cols)]
    for row in rows:
        cols = st.columns(len(row))
        for col, (name, hex_c) in zip(cols, row):
            is_sel = name in selected_set
            tc = "#0f172a" if lum(hex_c) > 155 else "#ffffff"
            border = "#1d4ed8" if is_sel else "rgba(0,0,0,0.15)"
            check = '<div class="swatch-check">✓</div>' if is_sel else ""
            with col:
                st.markdown(
                    f'<div class="swatch-cell">'
                    f'<div class="swatch-btn {"sel" if is_sel else ""}" '
                    f'style="background:{hex_c};border-color:{border}">{check}</div>'
                    f'<div class="swatch-name {"sel" if is_sel else ""}">{name}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button(".", key=f"{key_prefix}_{name}",
                             help=name, use_container_width=True):
                    if name in selected_set:
                        selected_set.discard(name)
                    else:
                        selected_set.add(name)
                    st.rerun()

def rect_swatch_html(items, score_key):
    html = '<div class="rect-grid">'
    for i, item in enumerate(items):
        score = item.get(score_key, 0)
        rank  = f'<div class="rect-rank">{i+1}</div>' if i==0 else ""
        star  = '<div class="rect-star">★</div>' if item.get("skin_delta",0)>0 else ""
        html += (
            f'<div class="rect-item">'
            f'<div class="rect-block" style="background:{item["hex"]}">{rank}{star}</div>'
            f'<div class="rect-name">{item["color"]}</div>'
            f'<div class="rect-score">{score:.1f}</div>'
            f'</div>'
        )
    return html + "</div>"

def outfit_row_html(outfit, index, skin_hex="#D4956A"):
    pct   = round((outfit["score"]/5)*100)
    img   = mannequin_img(outfit["shirt_hex"], outfit["pant_hex"], skin_hex, width=75, height=133)
    qual  = "Excellent" if outfit["score"]>=4 else "Good" if outfit["score"]>=3 else "Decent" if outfit["score"]>=2 else "Weak"
    qc    = "#1d4ed8" if outfit["score"]>=4 else "#16a34a" if outfit["score"]>=3 else "#d97706" if outfit["score"]>=2 else "#94a3b8"
    return (
        f'<div class="outfit-entry">'
        f'<div class="outfit-rank">#{index+1}</div>'
        f'{img}'
        f'<div style="flex:1;min-width:0">'
        f'<div class="outfit-name">{outfit["shirt"]} + {outfit["pant"]}</div>'
        f'<div class="outfit-sub">Match score {outfit["score"]:.1f} / 5.0</div>'
        f'<div class="outfit-bar-bg"><div class="outfit-bar-fill" style="width:{pct}%"></div></div>'
        f'</div>'
        f'<div style="text-align:right;flex-shrink:0">'
        f'<div class="outfit-score-num">{outfit["score"]:.1f}</div>'
        f'<div style="font-size:9px;color:{qc};font-weight:700;margin-top:2px">{qual}</div>'
        f'</div></div>'
    )

def combo_card_html(combo, skin_hex="#D4956A"):
    score   = combo.get("score", 0)
    shirt_h = combo.get("shirt_hex","#888")
    pant_h  = combo.get("pant_hex","#888")
    img     = mannequin_img(shirt_h, pant_h, skin_hex, width=70, height=124)
    pct     = round((score/5)*100)
    qual    = "Excellent" if score>=4 else "Good" if score>=3 else "Decent" if score>=2 else "Weak"
    qc      = "#1d4ed8" if score>=4 else "#16a34a" if score>=3 else "#d97706" if score>=2 else "#94a3b8"
    shirt   = combo.get("shirt","")
    pant    = combo.get("pant","")
    return (
        f'<div class="combo-cell">{img}'
        f'<div style="font-size:10px;color:#334155;text-align:center;line-height:1.4;font-weight:500">'
        f'{shirt}<br>{pant}</div>'
        f'<div style="display:flex;align-items:center;justify-content:space-between;width:100%">'
        f'<span style="font-size:9px;font-weight:700;color:{qc}">{qual}</span>'
        f'<span style="font-size:11px;color:#3b82f6;font-weight:700;font-family:monospace">{score:.1f}/5</span>'
        f'</div>'
        f'<div style="width:100%;height:3px;background:#e2e8f0;border-radius:2px;overflow:hidden">'
        f'<div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#1d4ed8,#3b82f6);border-radius:2px"></div>'
        f'</div></div>'
    )

# ─────────────────────────────────────────────────────────────
# NAVBAR
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#ffffff;border-bottom:1px solid #e2e8f0;
            padding:12px 32px;display:flex;align-items:center;gap:12px;
            box-shadow:0 1px 6px rgba(15,25,80,.06)">
  <div style="width:32px;height:32px;border-radius:9px;
              background:linear-gradient(135deg,#1d4ed8,#3b82f6);
              display:flex;align-items:center;justify-content:center;
              box-shadow:0 2px 8px rgba(29,78,216,.3);flex-shrink:0">
    <span style="color:#fff;font-size:16px;font-family:'Lora',serif;font-weight:700">W</span>
  </div>
  <div>
    <span style="font-size:16px;font-weight:700;color:#0f172a;
                 font-family:'Lora',serif;letter-spacing:-.2px">
      Wardrobe <span style="color:#3b82f6">Engine</span>
    </span>
    <span style="font-size:10px;color:#94a3b8;margin-left:10px">Personal Colour Intelligence</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# INPUT SECTION — horizontal layout
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="background:#ffffff;border-bottom:1px solid #e2e8f0;padding:20px 32px 24px">', unsafe_allow_html=True)

col_shirts, col_pants, col_right = st.columns([2.2, 1.5, 1.3], gap="large")

with col_shirts:
    st.markdown('<div class="step-label">① Shirts you own — tap to select</div>', unsafe_allow_html=True)
    colour_swatch_grid(SHIRT_COLORS, st.session_state.sel_shirts, "sh", n_cols=6)
    if st.session_state.sel_shirts:
        st.markdown(colour_pills_html(sorted(st.session_state.sel_shirts)), unsafe_allow_html=True)

with col_pants:
    st.markdown('<div class="step-label">② Pants you own</div>', unsafe_allow_html=True)
    colour_swatch_grid(PANT_COLORS, st.session_state.sel_pants, "pt", n_cols=5)
    if st.session_state.sel_pants:
        st.markdown(colour_pills_html(sorted(st.session_state.sel_pants)), unsafe_allow_html=True)

with col_right:
    # Season
    st.markdown('<div class="step-label">③ Season</div>', unsafe_allow_html=True)
    seas_cols = st.columns(5)
    for col, (key, meta) in zip(seas_cols, SEASON_META.items()):
        is_sel = st.session_state.selected_season == key
        nc = "#1d4ed8" if is_sel else "#64748b"
        border = "#1d4ed8" if is_sel else "#e2e8f0"
        bg = "#dbeafe" if is_sel else "#f8fafc"
        with col:
            st.markdown(
                f'<div style="text-align:center;padding:7px 3px;border-radius:10px;'
                f'border:1.5px solid {border};background:{bg}">'
                f'<div style="font-size:18px;line-height:1.2">{meta["icon"]}</div>'
                f'<div style="font-size:7px;font-weight:700;color:{nc};'
                f'text-transform:uppercase;letter-spacing:.06em;margin-top:2px">{meta["label"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button(meta["label"], key=f"s_{key}", help=key, use_container_width=True):
                st.session_state.selected_season = key
                st.rerun()

    selected_season = st.session_state.selected_season

    # Skin tone
    st.markdown('<div class="step-label" style="margin-top:14px">④ Skin tone <span style="font-weight:400;text-transform:none;letter-spacing:0;font-size:9px;color:#94a3b8">(optional)</span></div>', unsafe_allow_html=True)

    for depth, keys in [
        ("Light",  ["Light_Warm",  "Light_Cool",  "Light_Neutral"]),
        ("Medium", ["Medium_Warm", "Medium_Cool", "Medium_Neutral"]),
        ("Deep",   ["Deep_Warm",   "Deep_Cool",   "Deep_Neutral"]),
    ]:
        st.markdown(f'<div class="depth-row-label">{depth}</div>', unsafe_allow_html=True)
        sk_cols = st.columns(3)
        for col, key in zip(sk_cols, keys):
            meta   = SKIN_META[key]
            is_sel = st.session_state.selected_skin == key
            border = "#1d4ed8" if is_sel else "#e2e8f0"
            bg     = "#dbeafe" if is_sel else "#f8fafc"
            with col:
                face_img = skin_face_svg(meta["hex"], size=28)
                st.markdown(
                    f'<div style="display:flex;flex-direction:column;align-items:center;gap:3px;'
                    f'padding:7px 3px;border-radius:10px;border:1.5px solid {border};background:{bg}">'
                    f'{face_img}'
                    f'<div style="font-size:8px;font-weight:700;'
                    f'color:{"#1d4ed8" if is_sel else "#64748b"};text-align:center">{meta["label"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button("·", key=f"sk_{key}", help=key.replace("_"," "), use_container_width=True):
                    st.session_state.selected_skin = "" if is_sel else key
                    st.rerun()

    selected_skin = st.session_state.selected_skin
    if selected_skin:
        meta = SKIN_META[selected_skin]
        face = skin_face_svg(meta["hex"], size=14)
        st.markdown(
            f'<div style="margin-top:6px;padding:5px 10px;border-radius:8px;'
            f'background:#eff6ff;border:1px solid #bfdbfe;'
            f'display:flex;align-items:center;gap:6px;'
            f'font-size:10px;color:#1d4ed8;font-weight:600">'
            f'{face} {selected_skin.replace("_"," ")} · active ✓</div>',
            unsafe_allow_html=True
        )

    # Generate button
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    selected_shirts = list(st.session_state.sel_shirts)
    selected_pants  = list(st.session_state.sel_pants)
    has_input = bool(selected_shirts or selected_pants)
    run = st.button(
        "✦  Generate My Profile" if has_input else "Generate My Profile",
        type="primary", use_container_width=True, disabled=not has_input,
    )
    if not has_input:
        st.markdown(
            '<div style="font-size:10px;color:#94a3b8;text-align:center;margin-top:5px">'
            'Tap colours above to begin</div>',
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ENGINE
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
        "shirts": selected_shirts, "pants": selected_pants,
        "season": selected_season, "skin":  selected_skin,
    }

# ─────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────
if st.session_state.result is None:
    st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)
    _, c, _ = st.columns([1,2,1])
    with c:
        st.markdown("""
        <div style="text-align:center;padding:52px 40px;background:#ffffff;
                    border:1px solid #e2e8f0;border-radius:24px;
                    box-shadow:0 4px 20px rgba(15,25,80,.07)">
          <div style="font-size:48px;margin-bottom:14px">👔</div>
          <div style="font-family:'Lora',serif;font-size:26px;font-weight:700;
                      color:#0f172a;margin-bottom:8px">Your colour profile awaits</div>
          <div style="font-size:13px;color:#64748b;line-height:1.8;
                      max-width:280px;margin:0 auto">
            Tap the colour swatches above to select what you own, then hit Generate.
          </div>
        </div>""", unsafe_allow_html=True)
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
skin_hex = SKIN_META[inp["skin"]]["hex"] if inp["skin"] else "#D4956A"

# Build unified outfit list (match_strength 0-5)
_colors  = build_color_objects()
_all_s   = list(dict.fromkeys(inp["shirts"]+[x["color"] for x in result["smart_shirts"]]))
_all_p   = list(dict.fromkeys(inp["pants"] +[x["color"] for x in result["smart_pants"]]))
all_combos = sorted([
    {"shirt":s,"pant":p,
     "shirt_hex":_colors[s]["hex"],"pant_hex":_colors[p]["hex"],
     "score":round(get_match_strength(_colors[s],_colors[p]),2)}
    for s in _all_s for p in _all_p
    if s in _colors and p in _colors
], key=lambda x:x["score"], reverse=True)
top_outfits = all_combos[:6]

st.markdown('<div style="padding:24px 32px">', unsafe_allow_html=True)
st.markdown(
    f'<div style="margin-bottom:20px">'
    f'<span style="font-family:\'Lora\',serif;font-size:26px;font-weight:700;color:#0f172a">'
    f'{s_icon} Your Colour Profile</span>'
    f'<span style="font-size:12px;color:#94a3b8;margin-left:12px">'
    f'{len(inp["shirts"])} shirt{"s" if len(inp["shirts"])!=1 else ""} · '
    f'{len(inp["pants"])} pant{"s" if len(inp["pants"])!=1 else ""} · '
    f'{season_d} · {skin_lbl}</span></div>',
    unsafe_allow_html=True
)

col_card, col_outfits = st.columns([1.05,1], gap="large")

# ── PROFILE CARD ──
with col_card:
    qs   = QUALITY_STYLE[qual]
    card = (
        f'<div class="profile-card"><div class="card-accent"></div>'
        f'<div class="card-eyebrow">Wardrobe Engine · Colour Profile</div>'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:4px">'
        f'<div class="card-title">Your Style Profile</div>'
        f'<span class="q-badge" style="{qs}">{qual}</span></div>'
        f'<div class="card-meta">{s_icon} {season_d} · {skin_lbl}</div>'
        f'<div class="card-divider"></div>'
    )
    if result["smart_shirts"]:
        card += '<div class="sec-label">Smart Shirts to Buy</div>'
        card += rect_swatch_html(result["smart_shirts"],"shirt_score")
    if result["smart_pants"]:
        card += '<div class="sec-label">Smart Pants to Buy</div>'
        card += rect_swatch_html(result["smart_pants"],"pant_score")
    if result["all_season_neutrals"]:
        card += '<div class="sec-label">All-Season Neutrals</div>'
        card += rect_swatch_html(result["all_season_neutrals"],"neutral_score")
    card += (
        f'<div class="card-divider"></div>'
        f'<div style="display:flex;justify-content:space-between;font-size:9px;color:#94a3b8">'
        f'<span>{s_icon} {season_d} · {skin_lbl}</span>'
        f'<span style="font-family:\'DM Mono\',monospace">wardrobeengine.com</span>'
        f'</div></div>'
    )
    st.markdown(card, unsafe_allow_html=True)

# ── OUTFITS ──
with col_outfits:
    st.markdown('<div class="sec-label" style="margin-bottom:14px">Top Outfit Combinations</div>', unsafe_allow_html=True)
    for i, o in enumerate(top_outfits):
        st.markdown(outfit_row_html(o, i, skin_hex=skin_hex), unsafe_allow_html=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    if not st.session_state.show_all_combos:
        st.markdown(
            f'<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:14px;padding:14px 18px;margin-top:10px">'
            f'<div style="font-size:13px;font-weight:600;color:#1e3a8a">See all outfit combinations?</div>'
            f'<div style="font-size:11px;color:#3b82f6;margin-top:2px">'
            f'{len(all_combos)} pairings · ranked by match score</div></div>',
            unsafe_allow_html=True
        )
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("Show all ✦", use_container_width=True):
                st.session_state.show_all_combos = True
                st.rerun()
        with bc2:
            if st.button("Skip", use_container_width=True): pass
    else:
        st.markdown(
            f'<div style="font-size:12px;font-weight:600;color:#0f172a;margin-bottom:12px">'
            f'All {len(all_combos)} combinations '
            f'<span style="color:#94a3b8;font-weight:400">· ranked by match score</span></div>',
            unsafe_allow_html=True
        )
        cols3 = st.columns(3)
        for i, combo in enumerate(all_combos):
            with cols3[i%3]:
                st.markdown(combo_card_html(combo, skin_hex=skin_hex), unsafe_allow_html=True)
        if st.button("Hide combinations ↑", use_container_width=True):
            st.session_state.show_all_combos = False
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# GAP ANALYSIS
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#dde3ea,transparent);margin:0 32px"></div>', unsafe_allow_html=True)
st.markdown('<div style="padding:24px 32px 8px">', unsafe_allow_html=True)

gap   = wardrobe_gap_analysis(inp["shirts"], inp["pants"],
                               smart_shirts=result["smart_shirts"],
                               smart_pants=result["smart_pants"])
score = gap["score"]; band = gap["band"]
stats = gap["stats"]; praises = gap["praises"]; gaps_list = gap["gaps"]

score_color  = "#16a34a" if score>=80 else "#2563eb" if score>=60 else "#d97706" if score>=40 else "#dc2626"
score_bg     = "#dcfce7" if score>=80 else "#dbeafe" if score>=60 else "#fef9c3" if score>=40 else "#fee2e2"
score_border = "#86efac" if score>=80 else "#93c5fd" if score>=60 else "#fde047" if score>=40 else "#fca5a5"

st.markdown(
    '<div style="font-family:\'Lora\',serif;font-size:22px;font-weight:700;'
    'color:#0f172a;margin-bottom:18px">Wardrobe Health Analysis</div>',
    unsafe_allow_html=True
)

sc_col, st_col = st.columns([1,2], gap="large")
with sc_col:
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;
                padding:24px;text-align:center;box-shadow:0 2px 12px rgba(15,25,80,.06)">
      <div style="font-size:11px;font-weight:700;letter-spacing:.14em;
                  text-transform:uppercase;color:#94a3b8;margin-bottom:10px">Wardrobe Score</div>
      <div style="font-family:'Lora',serif;font-size:52px;font-weight:700;
                  color:{score_color};line-height:1">{score}</div>
      <div style="font-size:12px;color:#94a3b8;margin:4px 0 14px">out of 100</div>
      <div style="height:8px;background:#f1f5f9;border-radius:4px;overflow:hidden;margin-bottom:12px">
        <div style="height:100%;width:{score}%;background:{score_color};border-radius:4px"></div>
      </div>
      <span style="display:inline-block;padding:5px 16px;border-radius:20px;font-size:11px;
                   font-weight:700;background:{score_bg};color:{score_color};
                   border:1px solid {score_border}">{band}</span>
    </div>""", unsafe_allow_html=True)

with st_col:
    m1,m2,m3 = st.columns(3)
    for col,val,lbl,sub in [
        (m1, stats["current_outfits"], "Outfit combos", f"→ {stats['potential_outfits']} with top picks"),
        (m2, f"{stats['ratio']}:1",   "Shirt-pant ratio", f"{stats['shirts']} shirts · {stats['pants']} pants"),
        (m3, f"{stats['neut_pant_count']} neutral pant{'s' if stats['neut_pant_count']!=1 else ''}",
             "Neutral anchors", f"{stats['n_families']} colour {'families' if stats['n_families']!=1 else 'family'}"),
    ]:
        col.markdown(f"""
        <div class="metric-tile">
          <div class="metric-val">{val}</div>
          <div class="metric-lbl">{lbl}</div>
          <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    if praises:
        st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
        praise_html = "".join([
            f'<div style="display:flex;align-items:flex-start;gap:8px;padding:7px 12px;'
            f'border-radius:9px;background:#f0fdf4;border:1px solid #bbf7d0;margin-bottom:6px">'
            f'<span style="color:#16a34a;font-weight:700;font-size:13px;flex-shrink:0">{p["icon"]}</span>'
            f'<span style="font-size:12px;color:#15803d;line-height:1.5">{p["text"]}</span>'
            f'</div>'
            for p in praises
        ])
        st.markdown(praise_html, unsafe_allow_html=True)

if gaps_list:
    st.markdown('<div style="margin-top:20px">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:10px">Gaps to address</div>', unsafe_allow_html=True)
    SEV = {
        "high":   {"bg":"#fff1f2","border":"#fecdd3","dot":"#dc2626","label":"High priority"},
        "medium": {"bg":"#fffbeb","border":"#fde68a","dot":"#d97706","label":"Worth addressing"},
        "low":    {"bg":"#f0f9ff","border":"#bae6fd","dot":"#0284c7","label":"Nice to have"},
    }
    for g in gaps_list:
        sty = SEV.get(g["severity"], SEV["low"])
        st.markdown(f"""
        <div style="background:{sty['bg']};border:1px solid {sty['border']};
                    border-radius:12px;padding:14px 16px;margin-bottom:8px;
                    display:flex;align-items:flex-start;gap:12px">
          <div style="width:8px;height:8px;border-radius:50%;background:{sty['dot']};
                      flex-shrink:0;margin-top:5px"></div>
          <div style="flex:1">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <span style="font-size:12px;font-weight:700;color:#0f172a">{g['title']}</span>
              <span style="font-size:9px;font-weight:600;color:{sty['dot']};
                           background:rgba(255,255,255,.7);padding:2px 7px;
                           border-radius:10px;border:1px solid {sty['border']}">{sty['label']}</span>
            </div>
            <div style="font-size:12px;color:#334155;line-height:1.6">{g['text']}</div>
            <div style="font-size:11px;font-weight:600;color:{sty['dot']};margin-top:6px">→ {g['action']}</div>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#dde3ea,transparent);margin:0 32px"></div>', unsafe_allow_html=True)
st.markdown('<div style="padding:32px 32px 48px">', unsafe_allow_html=True)

if st.session_state.feedback_done:
    _, c, _ = st.columns([1,2,1])
    with c:
        st.markdown("""
        <div class="thankyou">
          <div style="font-size:44px;margin-bottom:12px">🙏</div>
          <div style="font-family:'Lora',serif;font-size:22px;color:#166534;font-weight:700;margin-bottom:8px">Thank you!</div>
          <div style="font-size:13px;color:#15803d;line-height:1.6">
            Your feedback shapes the ₹299 colour card.<br>We'll build a better product because of it.
          </div>
        </div>""", unsafe_allow_html=True)
else:
    _, c, _ = st.columns([1,2,1])
    with c:
        st.markdown('<div class="feedback-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="fb-title">Share your feedback</div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-sub">2 minutes · helps us build a better product</div>', unsafe_allow_html=True)

        st.markdown('<div class="fb-label">How useful were these recommendations?</div>', unsafe_allow_html=True)
        star_rating = st.select_slider("star_rating", options=[1,2,3,4,5], value=4,
                                        format_func=lambda x:"⭐"*x, label_visibility="collapsed")
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-label">Would you buy a personalised colour card for ₹299?</div>', unsafe_allow_html=True)
        buy_card = st.radio("buy_card",
                            ["Yes — I'd buy this","Maybe — need to see the physical card","No — not for me"],
                            label_visibility="collapsed")
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-label">How likely are you to recommend this to a friend?</div>', unsafe_allow_html=True)
        st.caption("0 = Not at all · 10 = Definitely")
        nps = st.slider("nps", 0, 10, 7, label_visibility="collapsed")
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

        if st.button("Submit Feedback →", type="primary", use_container_width=True):
            top_o = f"{top_outfits[0]['shirt']} + {top_outfits[0]['pant']}" if top_outfits else ""
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

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────────────────────
if st.query_params.get("admin") == "true":
    st.markdown("---")
    st.markdown("### 📊 Feedback Dashboard")
    admin_pw = st.secrets.get("ADMIN_PASSWORD","")
    entered  = st.text_input("Admin password", type="password", key="admin_pw")
    if entered != admin_pw:
        st.error("Incorrect password.") if entered else st.info("Enter the admin password.")
        st.stop()
    db = get_storage()
    if db.empty:
        st.info("No feedback yet.")
        st.stop()
    total=len(db); avg_star=round(db["star_rating"].mean(),1)
    avg_nps=round(db["nps_score"].mean(),1)
    buy_yes=round(db["buy_card"].str.startswith("Yes").sum()/total*100)
    m1,m2,m3,m4=st.columns(4)
    for col,val,lbl in [(m1,total,"Responses"),(m2,f"{avg_star}⭐","Avg Rating"),
                        (m3,avg_nps,"Avg NPS"),(m4,f"{buy_yes}%","Would Buy")]:
        col.markdown(f'<div class="adm-tile"><div class="adm-val">{val}</div><div class="adm-lbl">{lbl}</div></div>',
                     unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca:
        st.markdown("**Buy card responses**")
        st.bar_chart(db["buy_card"].value_counts())
    with cb:
        st.markdown("**Most recommended shirts**")
        st.bar_chart(db["smart_shirts"].str.split(", ").explode().value_counts().head(8))
    st.dataframe(db, use_container_width=True)
    st.download_button("⬇ Download CSV", data=db.to_csv(index=False),
                       file_name="wardrobe_feedback.csv", mime="text/csv")

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os
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

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp { background: #f0f4f8; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Override ALL Streamlit buttons to be light ── */
.stButton > button {
    background: #ffffff !important;
    color: #1e3a8a !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
    transition: all .15s !important;
    box-shadow: 0 1px 3px rgba(15,25,80,.08) !important;
}
.stButton > button:hover {
    background: #eff6ff !important;
    border-color: #93c5fd !important;
    box-shadow: 0 2px 6px rgba(29,78,216,.15) !important;
}
.stButton > button:focus,
.stButton > button[aria-pressed="true"] {
    background: #dbeafe !important;
    border-color: #1d4ed8 !important;
    color: #1d4ed8 !important;
}

/* Primary generate button */
.stButton.primary-btn > button,
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg,#1d4ed8,#3b82f6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    padding: 14px 24px !important;
    box-shadow: 0 4px 14px rgba(29,78,216,.3) !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    opacity: .9 !important;
}

/* Multiselect */
.stMultiSelect > div > div {
    background: #ffffff !important;
    border-color: #bfdbfe !important;
    border-radius: 10px !important;
}
.stMultiSelect label { color: #1e3a8a !important; font-weight: 600 !important; font-size:12px !important; }
.stMultiSelect [data-baseweb="tag"] { background: #dbeafe !important; }
.stMultiSelect [data-baseweb="tag"] span { color: #1e3a8a !important; }
.stMultiSelect input { color: #0f172a !important; }
.stMultiSelect [data-baseweb="menu"] { background: #ffffff !important; }
.stMultiSelect [data-baseweb="option"] { color: #0f172a !important; }

/* Radio */
.stRadio label, .stRadio label p, .stRadio span { color: #0f172a !important; font-size:13px !important; }

/* Slider */
.stSlider > div > div > div { background: #3b82f6 !important; }
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] { color: #64748b !important; }

/* Select slider */
[data-testid="stSelectSlider"] > div { color: #1d4ed8 !important; }

/* Caption */
.stCaption, .stCaption p { color: #94a3b8 !important; }

/* Markdown text */
div[data-testid="stMarkdownContainer"] p { color: #334155; }

/* Section headers */
.step-label {
    font-size: 11px; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #64748b;
    margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
}
.step-label::after { content:''; flex:1; height:1px; background:#e2e8f0; }

/* Season grid */
.season-grid { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px; }
.season-card {
    display:flex; flex-direction:column; align-items:center; gap:4px;
    padding:10px 8px; border-radius:12px; cursor:pointer; min-width:60px;
    border:1.5px solid #e2e8f0; background:#ffffff;
    transition:all .15s; box-shadow:0 1px 3px rgba(0,0,0,.05);
}
.season-card:hover { border-color:#93c5fd; background:#f0f9ff; }
.season-card.sel { border-color:#1d4ed8; background:#eff6ff; box-shadow:0 2px 8px rgba(29,78,216,.15); }
.season-icon { font-size:22px; line-height:1; }
.season-name { font-size:9px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.07em; }
.season-card.sel .season-name { color:#1d4ed8; }

/* Skin tone grid */
.skin-depth { font-size:9px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#64748b; margin:10px 0 6px; }
.skin-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.skin-card {
    display:flex; flex-direction:column; align-items:center; gap:5px;
    padding:10px 6px; border-radius:12px; cursor:pointer;
    border:1.5px solid #e2e8f0; background:#ffffff;
    transition:all .15s; box-shadow:0 1px 3px rgba(0,0,0,.05);
}
.skin-card:hover { border-color:#93c5fd; background:#f0f9ff; }
.skin-card.sel { border-color:#1d4ed8; background:#eff6ff; box-shadow:0 2px 8px rgba(29,78,216,.15); }
.skin-face-wrap { width:36px; height:36px; }
.skin-label { font-size:9px; font-weight:700; color:#475569; text-align:center; letter-spacing:.04em; }
.skin-card.sel .skin-label { color:#1d4ed8; }

/* Colour pills */
.colour-pills { display:flex; flex-wrap:wrap; gap:5px; margin:4px 0 8px; }
.colour-pill {
    display:flex; align-items:center; gap:5px;
    padding:3px 10px 3px 5px; border-radius:20px;
    background:#eff6ff; border:1px solid #bfdbfe;
    font-size:11px; color:#1e3a8a; font-weight:500;
}
.pill-dot { width:13px; height:13px; border-radius:50%; flex-shrink:0; border:1px solid rgba(0,0,0,.1); }

/* Profile card */
.profile-card {
    background:#ffffff; border:1px solid #e2e8f0;
    border-radius:20px; padding:24px;
    box-shadow:0 4px 20px rgba(15,25,80,.07);
    position:relative; overflow:hidden;
}
.card-accent { position:absolute; top:0; left:0; right:0; height:4px;
    background:linear-gradient(90deg,#1d4ed8,#3b82f6,#93c5fd,#3b82f6,#1d4ed8); }
.card-eyebrow { font-size:9px; letter-spacing:.18em; color:#3b82f6; font-weight:700; text-transform:uppercase; margin-bottom:5px; }
.card-title { font-family:'Lora',serif; font-size:22px; font-weight:700; color:#0f172a; margin-bottom:2px; }
.card-meta { font-size:11px; color:#94a3b8; margin-bottom:18px; }
.card-divider { height:1px; background:linear-gradient(90deg,transparent,#e2e8f0,transparent); margin:14px 0; }
.sec-label { font-size:9px; font-weight:700; letter-spacing:.15em; text-transform:uppercase;
    color:#94a3b8; margin:0 0 10px; display:flex; align-items:center; gap:8px; }
.sec-label::before { content:''; width:10px; height:2px; background:linear-gradient(90deg,#1d4ed8,#3b82f6); border-radius:2px; }

/* Rectangular swatches */
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

/* Quality badge */
.q-badge { display:inline-block; padding:4px 12px; border-radius:20px; font-size:10px; font-weight:700; }

/* Outfit entry */
.outfit-entry { display:flex; align-items:center; gap:14px; padding:12px 16px;
    border-radius:14px; background:#ffffff; border:1px solid #e2e8f0;
    margin-bottom:8px; transition:all .15s; box-shadow:0 1px 4px rgba(15,25,80,.05); }
.outfit-entry:hover { border-color:#93c5fd; box-shadow:0 3px 12px rgba(59,130,246,.1); }
.outfit-rank { font-size:11px; color:#94a3b8; font-weight:700; font-family:'DM Mono',monospace;
    width:22px; text-align:center; flex-shrink:0; }
.outfit-name { font-size:12px; color:#0f172a; font-weight:600; }
.outfit-sub  { font-size:10px; color:#94a3b8; margin-top:2px; }
.outfit-bar-bg { height:3px; background:#e2e8f0; border-radius:2px; overflow:hidden; margin-top:4px; }
.outfit-bar-fill { height:100%; border-radius:2px; background:linear-gradient(90deg,#1d4ed8,#3b82f6); }
.outfit-score-num { font-size:12px; color:#3b82f6; font-weight:700; font-family:'DM Mono',monospace; }

/* Combo card */
.combo-cell { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
    padding:12px 8px; display:flex; flex-direction:column; align-items:center; gap:8px;
    transition:all .15s; box-shadow:0 1px 3px rgba(15,25,80,.04); }
.combo-cell:hover { border-color:#93c5fd; box-shadow:0 3px 10px rgba(59,130,246,.1); }

/* Prompt bubble */
.prompt-bubble { background:#eff6ff; border:1px solid #bfdbfe; border-radius:14px;
    padding:14px 18px; margin-top:10px; }

/* Feedback */
.feedback-wrap { background:#ffffff; border:1px solid #e2e8f0; border-radius:20px;
    padding:32px; max-width:560px; margin:0 auto; box-shadow:0 4px 20px rgba(15,25,80,.07); }
.fb-title { font-family:'Lora',serif; font-size:22px; font-weight:700; color:#0f172a; margin-bottom:5px; }
.fb-sub { font-size:12px; color:#64748b; margin-bottom:20px; }
.fb-label { font-size:12px; font-weight:600; color:#1e3a8a; margin-bottom:6px; }
.thankyou { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:16px; padding:32px;
    text-align:center; max-width:480px; margin:0 auto; }

/* Metric tile */
.metric-tile { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
    padding:16px; text-align:center; }
.metric-val { font-family:'Lora',serif; font-size:28px; color:#1d4ed8; font-weight:700; }
.metric-lbl { font-size:11px; color:#64748b; margin-top:3px; }
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
             ("selected_season","All"),("selected_type","Both"),
             ("selected_style","Any"),("session_id",str(uuid.uuid4())[:8])]:
    if k not in st.session_state: st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def lum(h):
    h=h.lstrip("#")
    return 0.2126*int(h[0:2],16)+0.7152*int(h[2:4],16)+0.0722*int(h[4:6],16)

def darker(h, amt=28):
    hx=h.lstrip("#")
    r,g,b=int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
    return f"#{max(0,r-amt):02x}{max(0,g-amt):02x}{max(0,b-amt):02x}"

def quality_label(s):
    return "Premium" if s>12 else "Strong" if s>8 else "Developing" if s>4 else "Starter"

def skin_face_svg(hex_color, size=36):
    is_dark  = lum(hex_color) < 120
    eye_col  = "#ffffff" if is_dark else "#2a1208"
    brow_col = "#1a0a00" if not is_dark else "#d4b896"
    shadow   = "rgba(0,0,0,0.18)" if not is_dark else "rgba(0,0,0,0.30)"
    h        = hex_color.lstrip("#")
    r,g,b    = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    hair     = f"#{max(0,r-70):02x}{max(0,g-70):02x}{max(0,b-70):02x}"
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 36 36" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:block">'
        f'<ellipse cx="18" cy="15" rx="11" ry="12" fill="{hex_color}"/>'
        f'<ellipse cx="7"  cy="15" rx="3"  ry="4"  fill="{hex_color}"/>'
        f'<ellipse cx="29" cy="15" rx="3"  ry="4"  fill="{hex_color}"/>'
        f'<ellipse cx="14" cy="13" rx="2.2" ry="1.6" fill="{shadow}"/>'
        f'<ellipse cx="22" cy="13" rx="2.2" ry="1.6" fill="{shadow}"/>'
        f'<ellipse cx="14" cy="12.5" rx="1.4" ry="1.3" fill="{eye_col}" opacity=".9"/>'
        f'<ellipse cx="22" cy="12.5" rx="1.4" ry="1.3" fill="{eye_col}" opacity=".9"/>'
        f'<path d="M11,8.5 Q14,6.5 17,8" stroke="{brow_col}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".7"/>'
        f'<path d="M19,8 Q22,6.5 25,8.5" stroke="{brow_col}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".7"/>'
        f'<path d="M13,21.5 Q18,24.5 23,21.5" stroke="{shadow}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".8"/>'
        f'<ellipse cx="18" cy="28" rx="9"  ry="6"  fill="{hex_color}" opacity=".6"/>'
        f'<path d="M7,8 Q10,1 18,0 Q26,1 29,8 Q25,4 18,4 Q11,4 7,8Z" fill="{hair}"/>'
        f'</svg>'
    )

def colour_pills_html(names, colors_dict):
    if not names: return ""
    pills = "".join([
        f'<div class="colour-pill">'
        f'<span class="pill-dot" style="background:{colors_dict.get(n,{}).get("hex","#888")}"></span>'
        f'{n}</div>'
        for n in names
    ])
    return f'<div class="colour-pills">{pills}</div>'

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

def folded_stack_html(shirt_hex, pant_hex, shirt_name, pant_name,
                      compact=False, skin_hex="#D4956A"):
    """CSS folded stack WITH a face/head above the shirt."""
    w    = 70  if compact else 86
    sh   = 40  if compact else 50
    pw   = 60  if compact else 74
    ph   = 46  if compact else 58
    ov   = 12  if compact else 16
    fold = 11  if compact else 14
    sh_d = darker(shirt_hex)
    ph_d = darker(pant_hex)
    total_h = sh + ph - ov + 4

    # face measurements
    face_sz   = 22 if compact else 28
    neck_h    = 8  if compact else 10
    head_top  = 0
    shirt_top = face_sz + neck_h  # shirt starts below face+neck
    total_with_face = shirt_top + total_h

    nm_sz = 9 if compact else 10

    # face SVG inline
    face = skin_face_svg(skin_hex, size=face_sz)

    return (
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:5px">'
        f'<div style="position:relative;width:{w}px;height:{total_with_face}px">'

        # ── HEAD + NECK ──
        f'<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);'
        f'display:flex;flex-direction:column;align-items:center">'
        f'{face}'
        # neck
        f'<div style="width:{8 if compact else 10}px;height:{neck_h}px;'
        f'background:{skin_hex};border-radius:0 0 4px 4px;margin-top:-1px"></div>'
        f'</div>'

        # ── SHIRT (positioned below face) ──
        f'<div style="position:absolute;top:{shirt_top}px;left:50%;transform:translateX(-50%);'
        f'width:{w}px;height:{sh}px">'
        f'<div style="position:absolute;inset:0;border-radius:8px;background:{shirt_hex};'
        f'box-shadow:0 3px 10px rgba(0,0,0,.13),inset 0 1px 0 rgba(255,255,255,.2)"></div>'
        # collar
        f'<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);'
        f'width:13px;height:9px;border-radius:0 0 7px 7px;background:{sh_d};opacity:.4"></div>'
        # fold crease
        f'<div style="position:absolute;bottom:0;right:0;width:0;height:0;border-style:solid;'
        f'border-width:{fold}px {fold}px 0 0;border-color:transparent #f0f4f8 transparent transparent"></div>'
        # left sleeve
        f'<div style="position:absolute;top:4px;left:-7px;width:8px;height:{sh//2}px;'
        f'border-radius:4px 0 0 8px;background:{sh_d};opacity:.8;'
        f'transform:rotate(-4deg);transform-origin:top right"></div>'
        # right sleeve
        f'<div style="position:absolute;top:4px;right:-7px;width:8px;height:{sh//2}px;'
        f'border-radius:0 4px 8px 0;background:{sh_d};opacity:.8;'
        f'transform:rotate(4deg);transform-origin:top left"></div>'
        # button line
        f'<div style="position:absolute;top:10px;bottom:7px;left:50%;transform:translateX(-50%);'
        f'width:1px;background:rgba(0,0,0,.09);border-radius:1px"></div>'
        f'</div>'

        # ── PANT (positioned below shirt) ──
        f'<div style="position:absolute;top:{shirt_top+sh-ov}px;left:50%;transform:translateX(-50%);width:{pw}px">'
        f'<div style="width:100%;height:8px;border-radius:5px 5px 0 0;background:{ph_d}"></div>'
        f'<div style="display:flex;gap:3px;width:100%">'
        f'<div style="flex:1;height:{ph-8}px;border-radius:0 0 6px 6px;background:{pant_hex};'
        f'box-shadow:inset 2px 0 0 rgba(255,255,255,.1)"></div>'
        f'<div style="width:3px;height:{ph-8}px;background:rgba(0,0,0,.07)"></div>'
        f'<div style="flex:1;height:{ph-8}px;border-radius:0 0 6px 6px;background:{pant_hex};'
        f'box-shadow:inset -2px 0 0 rgba(0,0,0,.08)"></div>'
        f'</div></div>'
        f'</div>'

        # labels
        f'<div style="text-align:center;max-width:{w+16}px">'
        f'<div style="font-size:{nm_sz}px;font-weight:600;color:#334155;line-height:1.3">'
        f'<span style="color:#1d4ed8">{shirt_name[:9]}</span>'
        f'<span style="color:#94a3b8;margin:0 3px">+</span>'
        f'{pant_name[:9]}</div></div>'
        f'</div>'
    )

def outfit_row_html(outfit, index, skin_hex="#D4956A"):
    pct   = round((outfit["score"]/5)*100)
    stack = folded_stack_html(outfit["shirt_hex"], outfit["pant_hex"],
                              outfit["shirt"], outfit["pant"],
                              compact=True, skin_hex=skin_hex)
    qual  = "Excellent" if outfit["score"]>=4 else "Good" if outfit["score"]>=3 else "Decent" if outfit["score"]>=2 else "Weak"
    qc    = "#1d4ed8" if outfit["score"]>=4 else "#16a34a" if outfit["score"]>=3 else "#d97706" if outfit["score"]>=2 else "#94a3b8"
    return (
        f'<div class="outfit-entry">'
        f'<div class="outfit-rank">#{index+1}</div>'
        f'<div style="flex-shrink:0">{stack}</div>'
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
    shirt   = combo.get("shirt","")
    pant    = combo.get("pant","")
    stack   = folded_stack_html(shirt_h, pant_h, shirt, pant,
                                compact=True, skin_hex=skin_hex)
    pct     = round((score/5)*100)
    qual    = "Excellent" if score>=4 else "Good" if score>=3 else "Decent" if score>=2 else "Weak"
    qc      = "#1d4ed8" if score>=4 else "#16a34a" if score>=3 else "#d97706" if score>=2 else "#94a3b8"
    return (
        f'<div class="combo-cell">{stack}'
        f'<div style="display:flex;align-items:center;justify-content:space-between;width:100%">'
        f'<span style="font-size:9px;font-weight:700;color:{qc}">{qual}</span>'
        f'<span style="font-size:11px;color:#3b82f6;font-weight:700;font-family:monospace">{score:.1f}/5</span>'
        f'</div>'
        f'<div style="width:100%;height:3px;background:#e2e8f0;border-radius:2px;overflow:hidden">'
        f'<div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#1d4ed8,#3b82f6);border-radius:2px"></div>'
        f'</div></div>'
    )

# ─────────────────────────────────────────────────────────────
# TOP NAVBAR
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
# HORIZONTAL INPUT SECTION
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="background:#ffffff;border-bottom:1px solid #e2e8f0;padding:20px 32px 24px">', unsafe_allow_html=True)

# Row 1: Shirts + Pants + Season (3 columns)
c1, c2, c3 = st.columns([2, 2, 2], gap="large")

with c1:
    st.markdown('<div class="step-label">① Shirts you own</div>', unsafe_allow_html=True)
    selected_shirts = st.multiselect(
        "shirts", SHIRT_COLORS,
        label_visibility="collapsed",
        placeholder="Select shirt colours…",
    )
    st.markdown(colour_pills_html(selected_shirts, MASTER_COLORS), unsafe_allow_html=True)

with c2:
    st.markdown('<div class="step-label">② Pants you own</div>', unsafe_allow_html=True)
    selected_pants = st.multiselect(
        "pants", PANT_COLORS,
        label_visibility="collapsed",
        placeholder="Select pant colours…",
    )
    st.markdown(colour_pills_html(selected_pants, MASTER_COLORS), unsafe_allow_html=True)

with c3:
    st.markdown('<div class="step-label">③ Season</div>', unsafe_allow_html=True)
    # Season as horizontal button row
    seas_cols = st.columns(5)
    for col, (key, meta) in zip(seas_cols, SEASON_META.items()):
        is_sel = st.session_state.selected_season == key
        with col:
            border = "#1d4ed8" if is_sel else "#e2e8f0"
            bg     = "#dbeafe" if is_sel else "#ffffff"
            nc     = "#1d4ed8" if is_sel else "#64748b"
            st.markdown(
                f'<div style="text-align:center;padding:8px 4px;border-radius:10px;'
                f'border:1.5px solid {border};background:{bg};cursor:pointer;'
                f'box-shadow:{"0 2px 6px rgba(29,78,216,.15)" if is_sel else "0 1px 3px rgba(0,0,0,.05)"}">'
                f'<div style="font-size:20px;line-height:1.2">{meta["icon"]}</div>'
                f'<div style="font-size:8px;font-weight:700;color:{nc};'
                f'text-transform:uppercase;letter-spacing:.07em;margin-top:3px">{meta["label"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button(meta["label"], key=f"s_{key}", help=key,
                         use_container_width=True):
                st.session_state.selected_season = key
                st.rerun()
    selected_season = st.session_state.selected_season

# Row 2: Clothing Type + Style Preference
st.markdown('<div style="margin-top:16px"></div>', unsafe_allow_html=True)
type_col, style_col = st.columns([1, 1], gap="large")

TYPE_META = {
    "Both":   {"icon":"👔","label":"Both"},
    "Formal": {"icon":"🎩","label":"Formal"},
    "T-Shirt":{"icon":"👕","label":"T-Shirt"},
}
STYLE_META = {
    "Any":     {"icon":"✦","label":"Any style"},
    "Classic": {"icon":"🎯","label":"Classic"},
    "Bold":    {"icon":"⚡","label":"Bold"},
}

with type_col:
    st.markdown('<div class="step-label">④ Clothing type</div>', unsafe_allow_html=True)
    type_cols = st.columns(3)
    for col, (key, meta) in zip(type_cols, TYPE_META.items()):
        is_sel = st.session_state.selected_type == key
        border = "#1d4ed8" if is_sel else "#e2e8f0"
        bg     = "#dbeafe" if is_sel else "#ffffff"
        nc     = "#1d4ed8" if is_sel else "#64748b"
        with col:
            st.markdown(
                f'<div style="text-align:center;padding:10px 4px;border-radius:10px;'
                f'border:1.5px solid {border};background:{bg};'
                f'box-shadow:{"0 2px 6px rgba(29,78,216,.15)" if is_sel else "0 1px 3px rgba(0,0,0,.05)"}">'
                f'<div style="font-size:22px;line-height:1.2">{meta["icon"]}</div>'
                f'<div style="font-size:9px;font-weight:700;color:{nc};'
                f'text-transform:uppercase;letter-spacing:.07em;margin-top:3px">{meta["label"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button(meta["label"], key=f"type_{key}", use_container_width=True):
                st.session_state.selected_type = key
                st.rerun()

with style_col:
    st.markdown('<div class="step-label">⑤ Style preference</div>', unsafe_allow_html=True)
    style_cols = st.columns(3)
    for col, (key, meta) in zip(style_cols, STYLE_META.items()):
        is_sel = st.session_state.selected_style == key
        border = "#1d4ed8" if is_sel else "#e2e8f0"
        bg     = "#dbeafe" if is_sel else "#ffffff"
        nc     = "#1d4ed8" if is_sel else "#64748b"
        with col:
            st.markdown(
                f'<div style="text-align:center;padding:10px 4px;border-radius:10px;'
                f'border:1.5px solid {border};background:{bg};'
                f'box-shadow:{"0 2px 6px rgba(29,78,216,.15)" if is_sel else "0 1px 3px rgba(0,0,0,.05)"}">'
                f'<div style="font-size:22px;line-height:1.2">{meta["icon"]}</div>'
                f'<div style="font-size:9px;font-weight:700;color:{nc};'
                f'text-transform:uppercase;letter-spacing:.07em;margin-top:3px">{meta["label"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button(meta["label"], key=f"style_{key}", use_container_width=True):
                st.session_state.selected_style = key
                st.rerun()

selected_type  = st.session_state.selected_type
selected_style = st.session_state.selected_style

# Row 3: Skin tone (full width, compact)
st.markdown('<div style="margin-top:16px"></div>', unsafe_allow_html=True)
st.markdown('<div class="step-label">⑥ Skin tone <span style="font-weight:400;text-transform:none;letter-spacing:0;font-size:10px;color:#94a3b8">(optional)</span></div>', unsafe_allow_html=True)

skin_row = st.columns(9)
for col, (key, meta) in zip(skin_row, SKIN_META.items()):
    is_sel = st.session_state.selected_skin == key
    depth  = key.split("_")[0]
    label  = f"{depth[:1]}·{meta['label'][:1]}"  # e.g. "L·W"
    border = "#1d4ed8" if is_sel else "#e2e8f0"
    bg     = "#dbeafe" if is_sel else "#ffffff"
    face   = skin_face_svg(meta["hex"], size=28)
    with col:
        st.markdown(
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:3px;'
            f'padding:8px 4px;border-radius:10px;border:1.5px solid {border};'
            f'background:{bg};box-shadow:{"0 2px 6px rgba(29,78,216,.15)" if is_sel else "0 1px 3px rgba(0,0,0,.05)"}">'
            f'{face}'
            f'<div style="font-size:8px;font-weight:700;'
            f'color:{"#1d4ed8" if is_sel else "#64748b"};text-align:center;'
            f'letter-spacing:.04em">{meta["label"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button("·", key=f"sk_{key}", help=key.replace("_"," "),
                     use_container_width=True):
            st.session_state.selected_skin = "" if is_sel else key
            st.rerun()

selected_skin = st.session_state.selected_skin

# Row 3: depth labels + active indicator + generate button
lab_c, act_c, btn_c = st.columns([3, 3, 2])
with lab_c:
    st.markdown(
        '<div style="display:flex;gap:0;margin-top:4px">'
        + "".join([f'<div style="flex:1;font-size:8px;color:#94a3b8;text-align:center;font-weight:600;text-transform:uppercase;letter-spacing:.06em">{d}</div>' for d in ["Light","Light","Light","Medium","Medium","Medium","Deep","Deep","Deep"]])
        + '</div>',
        unsafe_allow_html=True
    )
with act_c:
    if selected_skin:
        meta = SKIN_META[selected_skin]
        face = skin_face_svg(meta["hex"], size=16)
        st.markdown(
            f'<div style="margin-top:6px;padding:5px 10px;border-radius:8px;'
            f'background:#eff6ff;border:1px solid #bfdbfe;'
            f'display:flex;align-items:center;gap:6px;'
            f'font-size:11px;color:#1d4ed8;font-weight:600;display:inline-flex">'
            f'{face} {selected_skin.replace("_"," ")} · active ✓</div>',
            unsafe_allow_html=True
        )
with btn_c:
    has_input = bool(selected_shirts or selected_pants)
    run = st.button(
        "✦  Generate Profile" if has_input else "Generate Profile",
        type="primary", use_container_width=True, disabled=not has_input,
        key="generate_btn"
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
            "shirts":             selected_shirts,
            "pants":              selected_pants,
            "season":             selected_season,
            "skin_profile":       selected_skin or None,
            "clothing_type":      selected_type,
            "style_preference":   selected_style,
        })
    st.session_state.result     = result
    st.session_state.last_input = {
        "shirts": selected_shirts, "pants": selected_pants,
        "season": selected_season, "skin":  selected_skin,
        "type":   selected_type,   "style": selected_style,
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
          <div style="font-size:13px;color:#64748b;line-height:1.8;max-width:280px;margin:0 auto">
            Select colours you own above and click Generate.
          </div>
          <div style="margin-top:20px;display:flex;flex-wrap:wrap;gap:7px;justify-content:center">
            <span style="font-size:10px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:4px 11px;border-radius:20px">Smart shirt picks</span>
            <span style="font-size:10px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:4px 11px;border-radius:20px">Smart pant picks</span>
            <span style="font-size:10px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:4px 11px;border-radius:20px">Outfit combinations</span>
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

# Build unified combo list using match_strength (0–5)
_colors = build_color_objects()
_all_s  = list(dict.fromkeys(inp["shirts"] + [x["color"] for x in result["smart_shirts"]]))
_all_p  = list(dict.fromkeys(inp["pants"]  + [x["color"] for x in result["smart_pants"]]))
all_combos = []
for s in _all_s:
    for p in _all_p:
        if s not in _colors or p not in _colors: continue
        sc = round(get_match_strength(_colors[s], _colors[p]), 2)
        all_combos.append({
            "shirt": s, "pant": p,
            "shirt_hex": _colors[s]["hex"],
            "pant_hex":  _colors[p]["hex"],
            "score": sc,
        })
all_combos.sort(key=lambda x: x["score"], reverse=True)
top_outfits = all_combos[:6]

st.markdown('<div style="padding:24px 32px">', unsafe_allow_html=True)

type_lbl  = inp.get("type",  "Both")
style_lbl = inp.get("style", "Any")
type_icon  = {"Both":"👔","Formal":"🎩","T-Shirt":"👕"}.get(type_lbl,"👔")
style_icon = {"Any":"✦","Classic":"🎯","Bold":"⚡"}.get(style_lbl,"✦")

st.markdown(
    f'<div style="margin-bottom:20px">'
    f'<span style="font-family:\'Lora\',serif;font-size:26px;font-weight:700;color:#0f172a">'
    f'{s_icon} Your Colour Profile</span>'
    f'<span style="font-size:12px;color:#94a3b8;margin-left:12px">'
    f'{len(inp["shirts"])} shirt{"s" if len(inp["shirts"])!=1 else ""} · '
    f'{len(inp["pants"])} pant{"s" if len(inp["pants"])!=1 else ""} · '
    f'{season_d} · {type_icon} {type_lbl} · {style_icon} {style_lbl} · {skin_lbl}</span></div>',
    unsafe_allow_html=True
)

col_card, col_outfits = st.columns([1.05, 1], gap="large")

# ── PROFILE CARD ──
with col_card:
    qs   = QUALITY_STYLE[qual]
    card = (
        f'<div class="profile-card"><div class="card-accent"></div>'
        f'<div class="card-eyebrow">Wardrobe Engine · Colour Profile</div>'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:4px">'
        f'<div class="card-title">Your Style Profile</div>'
        f'<span class="q-badge" style="{qs}">{qual}</span></div>'
        f'<div class="card-meta">{s_icon} {season_d} · {type_icon} {type_lbl} · {style_icon} {style_lbl} · {skin_lbl}</div>'
        f'<div class="card-divider"></div>'
    )
    if result["smart_shirts"]:
        card += '<div class="sec-label">Smart Shirts to Buy</div>'
        card += rect_swatch_html(result["smart_shirts"], "shirt_score")
    if result["smart_pants"]:
        card += '<div class="sec-label">Smart Pants to Buy</div>'
        card += rect_swatch_html(result["smart_pants"], "pant_score")
    if result["all_season_neutrals"]:
        card += '<div class="sec-label">All-Season Neutrals</div>'
        card += rect_swatch_html(result["all_season_neutrals"], "neutral_score")
    card += (
        f'<div class="card-divider"></div>'
        f'<div style="display:flex;justify-content:space-between;font-size:9px;color:#94a3b8">'
        f'<span>{s_icon} {season_d} · {skin_lbl}</span>'
        f'<span style="font-family:\'DM Mono\',monospace">wardrobeengine.com</span>'
        f'</div></div>'
    )
    st.markdown(card, unsafe_allow_html=True)

# ── OUTFIT COMBINATIONS ──
with col_outfits:
    st.markdown('<div class="sec-label" style="margin-bottom:14px">Top Outfit Combinations</div>', unsafe_allow_html=True)
    for i, o in enumerate(top_outfits):
        st.markdown(outfit_row_html(o, i, skin_hex=skin_hex), unsafe_allow_html=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    if not st.session_state.show_all_combos:
        st.markdown(
            f'<div class="prompt-bubble">'
            f'<div style="font-size:13px;font-weight:600;color:#1e3a8a">See all outfit combinations?</div>'
            f'<div style="font-size:11px;color:#3b82f6;margin-top:2px">'
            f'{len(all_combos)} pairings · same 0–5 match score</div></div>',
            unsafe_allow_html=True
        )
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("Show all combinations ✦", use_container_width=True):
                st.session_state.show_all_combos = True
                st.rerun()
        with bc2:
            if st.button("Skip", use_container_width=True):
                pass
    else:
        st.markdown(
            f'<div style="font-size:12px;font-weight:600;color:#0f172a;margin-bottom:12px">'
            f'All {len(all_combos)} combinations '
            f'<span style="color:#94a3b8;font-weight:400">· ranked by match score</span></div>',
            unsafe_allow_html=True
        )
        cols3 = st.columns(3)
        for i, combo in enumerate(all_combos):
            with cols3[i % 3]:
                st.markdown(combo_card_html(combo, skin_hex=skin_hex), unsafe_allow_html=True)
        if st.button("Hide combinations ↑", use_container_width=True):
            st.session_state.show_all_combos = False
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
# WARDROBE GAP ANALYSIS
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="padding:0 32px 8px">', unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#dde3ea,transparent);margin-bottom:28px"></div>', unsafe_allow_html=True)

# Run gap analysis
gap = wardrobe_gap_analysis(
    inp["shirts"], inp["pants"],
    smart_shirts=result["smart_shirts"],
    smart_pants=result["smart_pants"],
)

score     = gap["score"]
band      = gap["band"]
praises   = gap["praises"]
gaps_list = gap["gaps"]
stats     = gap["stats"]

# Score colour
score_color = (
    "#16a34a" if score >= 80 else
    "#2563eb" if score >= 60 else
    "#d97706" if score >= 40 else
    "#dc2626"
)
score_bg = (
    "#dcfce7" if score >= 80 else
    "#dbeafe" if score >= 60 else
    "#fef9c3" if score >= 40 else
    "#fee2e2"
)
score_border = (
    "#86efac" if score >= 80 else
    "#93c5fd" if score >= 60 else
    "#fde047" if score >= 40 else
    "#fca5a5"
)

# Section header
st.markdown(
    '<div style="font-family:''Lora'',serif;font-size:22px;font-weight:700;'
    'color:#0f172a;margin-bottom:18px">Wardrobe Health Analysis</div>',
    unsafe_allow_html=True
)

# Score card + stats row
score_col, stats_col = st.columns([1, 2], gap="large")

with score_col:
    # Big score display
    bar_pct = score
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;
                padding:24px;text-align:center;box-shadow:0 2px 12px rgba(15,25,80,.06)">
      <div style="font-size:11px;font-weight:700;letter-spacing:.14em;
                  text-transform:uppercase;color:#94a3b8;margin-bottom:10px">
        Wardrobe Score
      </div>
      <div style="font-family:'Lora',serif;font-size:52px;font-weight:700;
                  color:{score_color};line-height:1">{score}</div>
      <div style="font-size:12px;color:#94a3b8;margin:4px 0 14px">out of 100</div>
      <div style="height:8px;background:#f1f5f9;border-radius:4px;overflow:hidden;margin-bottom:12px">
        <div style="height:100%;width:{bar_pct}%;background:{score_color};
                    border-radius:4px;transition:width .6s ease"></div>
      </div>
      <span style="display:inline-block;padding:5px 16px;border-radius:20px;
                   font-size:11px;font-weight:700;
                   background:{score_bg};color:{score_color};
                   border:1px solid {score_border}">
        {band}
      </span>
    </div>
    """, unsafe_allow_html=True)

with stats_col:
    # 3-column stat grid
    s1, s2, s3 = st.columns(3)
    for col, val, lbl, sub in [
        (s1, stats["current_outfits"],  "Outfit combos",    f"→ {stats['potential_outfits']} with top picks"),
        (s2, f"{stats['ratio']}:1",     "Shirt-pant ratio", f"{stats['shirts']} shirts · {stats['pants']} pants"),
        (s3, f"{stats['neut_pant_count']} neutral pant{'s' if stats['neut_pant_count']!=1 else ''}",
             "Neutral anchors", f"{stats['n_families']} colour {'families' if stats['n_families']!=1 else 'family'}"),
    ]:
        col.markdown(f"""
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;
                    padding:14px 16px;box-shadow:0 1px 4px rgba(15,25,80,.04)">
          <div style="font-family:'Lora',serif;font-size:22px;font-weight:700;
                      color:#0f172a;margin-bottom:3px">{val}</div>
          <div style="font-size:11px;font-weight:600;color:#475569">{lbl}</div>
          <div style="font-size:10px;color:#94a3b8;margin-top:3px">{sub}</div>
        </div>""", unsafe_allow_html=True)

    # Praises
    if praises:
        st.markdown('<div style="margin-top:12px">', unsafe_allow_html=True)
        praise_html = "".join([
            f'<div style="display:flex;align-items:flex-start;gap:8px;'
            f'padding:7px 12px;border-radius:9px;background:#f0fdf4;'
            f'border:1px solid #bbf7d0;margin-bottom:6px">'
            f'<span style="color:#16a34a;font-weight:700;font-size:13px;flex-shrink:0">{p["icon"]}</span>'
            f'<span style="font-size:12px;color:#15803d;line-height:1.5">{p["text"]}</span>'
            f'</div>'
            for p in praises
        ])
        st.markdown(praise_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Gaps
if gaps_list:
    st.markdown('<div style="margin-top:20px">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:10px">'
        'Gaps to address</div>',
        unsafe_allow_html=True
    )

    SEV_STYLE = {
        "high":   {"bg":"#fff1f2","border":"#fecdd3","dot":"#dc2626","label":"High priority"},
        "medium": {"bg":"#fffbeb","border":"#fde68a","dot":"#d97706","label":"Worth addressing"},
        "low":    {"bg":"#f0f9ff","border":"#bae6fd","dot":"#0284c7","label":"Nice to have"},
    }

    for gap_item in gaps_list:
        sty = SEV_STYLE.get(gap_item["severity"], SEV_STYLE["low"])
        st.markdown(f"""
        <div style="background:{sty['bg']};border:1px solid {sty['border']};
                    border-radius:12px;padding:14px 16px;margin-bottom:8px;
                    display:flex;align-items:flex-start;gap:12px">
          <div style="width:8px;height:8px;border-radius:50%;
                      background:{sty['dot']};flex-shrink:0;margin-top:5px"></div>
          <div style="flex:1">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <span style="font-size:12px;font-weight:700;color:#0f172a">{gap_item['title']}</span>
              <span style="font-size:9px;font-weight:600;color:{sty['dot']};
                           background:rgba(255,255,255,.7);padding:2px 7px;
                           border-radius:10px;border:1px solid {sty['border']}">{sty['label']}</span>
            </div>
            <div style="font-size:12px;color:#334155;line-height:1.6">{gap_item['text']}</div>
            <div style="font-size:11px;font-weight:600;color:{sty['dot']};
                        margin-top:6px">→ {gap_item['action']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div style="height:1px;background:linear-gradient(90deg,transparent,#dde3ea,transparent);'
    'margin:0 32px"></div>',
    unsafe_allow_html=True
)
st.markdown('<div style="padding:32px 32px 40px">', unsafe_allow_html=True)

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
        star_rating = st.select_slider(
            "star_rating", options=[1,2,3,4,5], value=4,
            format_func=lambda x:"⭐"*x, label_visibility="collapsed",
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
            outfits = top_outfits
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
    total=len(db); avg_star=round(db["star_rating"].mean(),1)
    avg_nps=round(db["nps_score"].mean(),1)
    buy_yes=round(db["buy_card"].str.startswith("Yes").sum()/total*100)
    m1,m2,m3,m4=st.columns(4)
    for col,val,lbl in [(m1,total,"Responses"),(m2,f"{avg_star}⭐","Avg Rating"),
                        (m3,avg_nps,"Avg NPS"),(m4,f"{buy_yes}%","Would Buy")]:
        col.markdown(
            f'<div class="metric-tile"><div class="metric-val">{val}</div>'
            f'<div class="metric-lbl">{lbl}</div></div>',
            unsafe_allow_html=True
        )
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

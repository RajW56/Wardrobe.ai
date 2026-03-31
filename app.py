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

st.set_page_config(
    page_title="Wardrobe Engine",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Lora:wght@600;700&family=DM+Mono:wght@400&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #0f1923; }
.stApp { background: #f0f4f8; }
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #dde3ea; box-shadow: 2px 0 12px rgba(15,25,80,.06); }
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem 2rem !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1400px; }

.sb-label { font-size:10px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#8896a8; margin:20px 0 8px; display:flex; align-items:center; gap:8px; }
.sb-label::after { content:''; flex:1; height:1px; background:#e8edf2; }

.colour-pills { display:flex; flex-wrap:wrap; gap:5px; margin:4px 0 10px; }
.colour-pill { display:flex; align-items:center; gap:5px; padding:4px 10px 4px 5px; border-radius:20px; background:#eef2ff; border:1px solid #c7d2fe; font-size:11px; color:#3730a3; font-weight:500; }
.pill-dot { width:14px; height:14px; border-radius:50%; flex-shrink:0; border:1px solid rgba(0,0,0,.1); box-shadow:inset 0 1px 2px rgba(0,0,0,.1); }

.depth-row-label { font-size:9px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#8896a8; margin:10px 0 5px; }

.stButton > button { background:linear-gradient(135deg,#1d4ed8,#3b82f6) !important; color:#ffffff !important; border:none !important; border-radius:12px !important; font-weight:600 !important; font-size:13px !important; padding:14px !important; letter-spacing:.02em !important; box-shadow:0 4px 14px rgba(29,78,216,.3) !important; transition:all .15s !important; }
.stButton > button:hover { opacity:.9 !important; transform:translateY(-1px) !important; }
.stButton > button:disabled { background:#e2e8f0 !important; color:#94a3b8 !important; box-shadow:none !important; transform:none !important; }

.page-header { font-family:'Lora',serif; font-size:32px; font-weight:700; color:#0f172a; letter-spacing:-.4px; margin-bottom:4px; }
.page-sub { font-size:13px; color:#64748b; margin-bottom:28px; }

.profile-card { background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; padding:28px; box-shadow:0 4px 20px rgba(15,25,80,.07); position:relative; overflow:hidden; }
.card-accent { position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg,#1d4ed8,#3b82f6,#93c5fd,#3b82f6,#1d4ed8); border-radius:20px 20px 0 0; }
.card-eyebrow { font-size:9px; letter-spacing:.18em; color:#3b82f6; font-weight:700; text-transform:uppercase; margin-bottom:6px; }
.card-title { font-family:'Lora',serif; font-size:24px; font-weight:700; color:#0f172a; letter-spacing:-.3px; margin-bottom:2px; }
.card-meta { font-size:11px; color:#94a3b8; margin-bottom:20px; }
.card-divider { height:1px; background:linear-gradient(90deg,transparent,#e2e8f0,transparent); margin:16px 0; }
.sec-label { font-size:9px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; color:#94a3b8; margin:0 0 12px; display:flex; align-items:center; gap:8px; }
.sec-label::before { content:''; width:12px; height:2px; background:linear-gradient(90deg,#1d4ed8,#3b82f6); border-radius:2px; }

.rect-grid { display:flex; flex-wrap:wrap; gap:12px; margin-bottom:18px; }
.rect-item { display:flex; flex-direction:column; align-items:center; gap:5px; }
.rect-block { width:64px; height:96px; border-radius:12px; box-shadow:0 3px 12px rgba(0,0,0,.12); position:relative; transition:transform .15s; }
.rect-block:hover { transform:translateY(-3px); }
.rect-name { font-size:9px; color:#475569; text-align:center; max-width:68px; line-height:1.3; font-weight:600; }
.rect-score { font-size:9px; color:#3b82f6; font-weight:700; font-family:'DM Mono',monospace; }
.rect-rank { position:absolute; top:-5px; right:-5px; width:16px; height:16px; border-radius:50%; background:#1d4ed8; color:white; font-size:8px; font-weight:700; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 4px rgba(29,78,216,.4); }
.rect-star { position:absolute; bottom:-5px; right:-5px; width:16px; height:16px; border-radius:50%; background:#f97316; color:white; font-size:9px; display:flex; align-items:center; justify-content:center; }

.q-badge { display:inline-block; padding:4px 14px; border-radius:20px; font-size:10px; font-weight:700; letter-spacing:.05em; }

.outfit-entry { display:flex; align-items:center; gap:14px; padding:12px 16px; border-radius:14px; background:#ffffff; border:1px solid #e2e8f0; margin-bottom:8px; transition:all .15s; box-shadow:0 1px 4px rgba(15,25,80,.05); }
.outfit-entry:hover { border-color:#93c5fd; box-shadow:0 3px 12px rgba(59,130,246,.1); }
.outfit-rank { font-size:11px; color:#94a3b8; font-weight:700; font-family:'DM Mono',monospace; width:22px; text-align:center; flex-shrink:0; }
.outfit-name { font-size:12px; color:#0f172a; font-weight:600; }
.outfit-sub  { font-size:10px; color:#94a3b8; margin-top:2px; }
.outfit-bar-bg { width:64px; height:3px; background:#e2e8f0; border-radius:2px; overflow:hidden; margin-top:4px; }
.outfit-bar-fill { height:100%; border-radius:2px; background:linear-gradient(90deg,#1d4ed8,#3b82f6); }
.outfit-score-num { font-size:12px; color:#3b82f6; font-weight:700; font-family:'DM Mono',monospace; }

.combo-cell { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:14px 10px; display:flex; flex-direction:column; align-items:center; gap:8px; transition:all .15s; box-shadow:0 1px 4px rgba(15,25,80,.04); }
.combo-cell:hover { border-color:#93c5fd; box-shadow:0 3px 10px rgba(59,130,246,.1); }

.prompt-bubble { background:#eff6ff; border:1px solid #bfdbfe; border-radius:14px; padding:16px 20px; display:flex; align-items:center; justify-content:space-between; gap:16px; margin-top:12px; }
.pb-q { font-size:13px; font-weight:600; color:#1e3a8a; }
.pb-sub { font-size:11px; color:#3b82f6; margin-top:2px; }

.feedback-wrap { background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; padding:32px; max-width:560px; margin:0 auto; box-shadow:0 4px 20px rgba(15,25,80,.07); }
.fb-title { font-family:'Lora',serif; font-size:24px; font-weight:700; color:#0f172a; margin-bottom:6px; }
.fb-sub { font-size:12px; color:#64748b; margin-bottom:24px; }
.fb-label { font-size:12px; font-weight:600; color:#1e3a8a; margin-bottom:6px; }

.thankyou { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:16px; padding:36px; text-align:center; max-width:480px; margin:0 auto; }
.ty-title { font-family:'Lora',serif; font-size:26px; color:#166534; font-weight:700; margin-bottom:8px; }

.metric-tile { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:18px; text-align:center; box-shadow:0 1px 4px rgba(15,25,80,.05); }
.metric-val { font-family:'Lora',serif; font-size:30px; color:#1d4ed8; font-weight:700; }
.metric-lbl { font-size:11px; color:#64748b; margin-top:3px; }

.stMultiSelect > div > div { background:#f8fafc !important; border-color:#dde3ea !important; border-radius:10px !important; }
.stMultiSelect label, .stMultiSelect span { color:#0f172a !important; }
.stMultiSelect [data-baseweb="tag"] { background:#dbeafe !important; border-color:#93c5fd !important; }
.stMultiSelect [data-baseweb="tag"] span { color:#1e3a8a !important; }

.stRadio label, .stRadio label p, .stRadio span { color:#0f172a !important; font-size:13px !important; }
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

# Soft, realistic skin tones
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
    h = h.lstrip("#")
    return 0.2126*int(h[0:2],16) + 0.7152*int(h[2:4],16) + 0.0722*int(h[4:6],16)

def darker(h, amt=28):
    hx = h.lstrip("#")
    r,g,b = int(hx[0:2],16), int(hx[2:4],16), int(hx[4:6],16)
    return f"#{max(0,r-amt):02x}{max(0,g-amt):02x}{max(0,b-amt):02x}"

def quality_label(s):
    return "Premium" if s>12 else "Strong" if s>8 else "Developing" if s>4 else "Starter"

def skin_face_svg(hex_color, size=32):
    """SVG face — Streamlit allows SVG inside st.markdown via unsafe_allow_html."""
    is_dark  = lum(hex_color) < 120
    eye_col  = "#ffffff" if is_dark else "#2a1208"
    brow_col = "#1a0a00" if not is_dark else "#d4b896"
    shadow   = "rgba(0,0,0,0.18)" if not is_dark else "rgba(0,0,0,0.30)"
    h        = hex_color.lstrip("#")
    r,g,b    = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    hair     = f"#{max(0,r-70):02x}{max(0,g-70):02x}{max(0,b-70):02x}"
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 36 36" '
        f'xmlns="http://www.w3.org/2000/svg">'
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
        rank  = f'<div class="rect-rank">{i+1}</div>' if i == 0 else ""
        star  = '<div class="rect-star">★</div>' if item.get("skin_delta",0) > 0 else ""
        html += (
            f'<div class="rect-item">'
            f'<div class="rect-block" style="background:{item["hex"]}">{rank}{star}</div>'
            f'<div class="rect-name">{item["color"]}</div>'
            f'<div class="rect-score">{score:.1f}</div>'
            f'</div>'
        )
    return html + "</div>"

def folded_stack_html(shirt_hex, pant_hex, shirt_name, pant_name, compact=False):
    """CSS-only folded stack — works reliably in Streamlit markdown."""
    w    = 72  if compact else 88
    sh   = 44  if compact else 54
    pw   = 64  if compact else 76
    ph   = 50  if compact else 62
    ov   = 14  if compact else 18
    fold = 12  if compact else 16
    sh_d = darker(shirt_hex)
    ph_d = darker(pant_hex)
    total_h = sh + ph - ov + 4
    nm_size = 9 if compact else 10

    return (
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px">'
        f'<div style="position:relative;width:{w}px;height:{total_h}px">'

        # pant
        f'<div style="position:absolute;bottom:0;left:50%;transform:translateX(-50%);width:{pw}px">'
        f'<div style="width:100%;height:8px;border-radius:5px 5px 0 0;background:{ph_d}"></div>'
        f'<div style="display:flex;gap:3px;width:100%">'
        f'<div style="flex:1;height:{ph-8}px;border-radius:0 0 6px 6px;background:{pant_hex};'
        f'box-shadow:inset 2px 0 0 rgba(255,255,255,.1)"></div>'
        f'<div style="width:3px;height:{ph-8}px;background:rgba(0,0,0,.07)"></div>'
        f'<div style="flex:1;height:{ph-8}px;border-radius:0 0 6px 6px;background:{pant_hex};'
        f'box-shadow:inset -2px 0 0 rgba(0,0,0,.08)"></div>'
        f'</div></div>'

        # shirt
        f'<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);'
        f'width:{w}px;height:{sh}px">'
        f'<div style="position:absolute;inset:0;border-radius:8px;background:{shirt_hex};'
        f'box-shadow:0 3px 10px rgba(0,0,0,.13),inset 0 1px 0 rgba(255,255,255,.2)"></div>'
        f'<div style="position:absolute;top:0;left:50%;transform:translateX(-50%);'
        f'width:14px;height:10px;border-radius:0 0 8px 8px;background:{sh_d};opacity:.45"></div>'
        f'<div style="position:absolute;bottom:0;right:0;width:0;height:0;border-style:solid;'
        f'border-width:{fold}px {fold}px 0 0;border-color:transparent #f0f4f8 transparent transparent"></div>'
        f'<div style="position:absolute;top:4px;left:-7px;width:9px;height:{sh//2}px;'
        f'border-radius:4px 0 0 8px;background:{sh_d};opacity:.8;'
        f'transform:rotate(-4deg);transform-origin:top right"></div>'
        f'<div style="position:absolute;top:4px;right:-7px;width:9px;height:{sh//2}px;'
        f'border-radius:0 4px 8px 0;background:{sh_d};opacity:.8;'
        f'transform:rotate(4deg);transform-origin:top left"></div>'
        f'<div style="position:absolute;top:12px;bottom:8px;left:50%;transform:translateX(-50%);'
        f'width:1px;background:rgba(0,0,0,.09);border-radius:1px"></div>'
        f'</div></div>'

        # labels
        f'<div style="text-align:center;max-width:{w+16}px">'
        f'<div style="font-size:{nm_size}px;font-weight:600;color:#334155;line-height:1.3">'
        f'<span style="color:#1d4ed8">{shirt_name[:9]}</span>'
        f'<span style="color:#94a3b8;margin:0 3px">+</span>'
        f'{pant_name[:9]}</div></div>'
        f'</div>'
    )

def outfit_row_html(outfit, index):
    pct   = round((outfit["score"]/5)*100)
    stack = folded_stack_html(outfit["shirt_hex"], outfit["pant_hex"],
                              outfit["shirt"], outfit["pant"], compact=True)
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

def combo_card_html(combo):
    score   = combo.get("score", combo.get("pair_score", 0))
    shirt_h = combo.get("shirt_hex", "#888")
    pant_h  = combo.get("pant_hex",  "#888")
    shirt   = combo.get("shirt", "")
    pant    = combo.get("pant",  "")
    stack   = folded_stack_html(shirt_h, pant_h, shirt, pant, compact=True)
    pct     = round((score/5)*100)
    qual    = "Excellent" if score>=4 else "Good" if score>=3 else "Decent" if score>=2 else "Weak"
    qc      = "#1d4ed8" if score>=4 else "#16a34a" if score>=3 else "#d97706" if score>=2 else "#94a3b8"
    return (
        f'<div class="combo-cell">{stack}'
        f'<div style="display:flex;align-items:center;justify-content:space-between;width:100%">'
        f'<span style="font-size:9px;font-weight:700;color:{qc}">{qual}</span>'
        f'<span style="font-size:11px;color:#3b82f6;font-weight:700;font-family:monospace">{score:.1f}</span>'
        f'</div>'
        f'<div style="width:100%;height:3px;background:#e2e8f0;border-radius:2px;overflow:hidden">'
        f'<div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#1d4ed8,#3b82f6);border-radius:2px"></div>'
        f'</div></div>'
    )

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
      <div style="width:34px;height:34px;border-radius:10px;
                  background:linear-gradient(135deg,#1d4ed8,#3b82f6);
                  display:flex;align-items:center;justify-content:center;
                  box-shadow:0 3px 10px rgba(29,78,216,.3)">
        <span style="color:#fff;font-size:17px;font-family:'Lora',serif;font-weight:700">W</span>
      </div>
      <div>
        <div style="font-size:15px;font-weight:700;color:#0f172a;font-family:'Lora',serif;letter-spacing:-.2px">
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
        "shirts", SHIRT_COLORS, label_visibility="collapsed",
        placeholder="Choose shirt colours…",
    )
    st.markdown(colour_pills_html(selected_shirts, MASTER_COLORS), unsafe_allow_html=True)

    # ── PANTS ──
    st.markdown('<div class="sb-label">② Pants you own</div>', unsafe_allow_html=True)
    selected_pants = st.multiselect(
        "pants", PANT_COLORS, label_visibility="collapsed",
        placeholder="Choose pant colours…",
    )
    st.markdown(colour_pills_html(selected_pants, MASTER_COLORS), unsafe_allow_html=True)

    # ── SEASON ──
    st.markdown('<div class="sb-label">③ Season</div>', unsafe_allow_html=True)
    seas_cols = st.columns(5)
    for col, (key, meta) in zip(seas_cols, SEASON_META.items()):
        is_sel = st.session_state.selected_season == key
        with col:
            nc = "#1d4ed8" if is_sel else "#8896a8"
            if st.button(meta["icon"], key=f"s_{key}", help=key, use_container_width=True):
                st.session_state.selected_season = key
                st.rerun()
            st.markdown(
                f'<div style="text-align:center;font-size:8px;font-weight:700;'
                f'letter-spacing:.07em;text-transform:uppercase;margin-top:-6px;color:{nc}">'
                f'{meta["label"]}</div>',
                unsafe_allow_html=True
            )
    selected_season = st.session_state.selected_season
    if selected_season != "All":
        st.markdown(
            f'<div style="margin-top:6px;padding:5px 10px;border-radius:8px;'
            f'background:#eff6ff;border:1px solid #bfdbfe;'
            f'font-size:11px;color:#1d4ed8;font-weight:600;display:inline-block">'
            f'{SEASON_META[selected_season]["icon"]} {selected_season} selected</div>',
            unsafe_allow_html=True
        )

    # ── SKIN TONE ──
    st.markdown(
        '<div class="sb-label">④ Skin tone '
        '<span style="color:#94a3b8;font-weight:400;text-transform:none;'
        'letter-spacing:0;font-size:9px">(optional)</span></div>',
        unsafe_allow_html=True
    )

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
                # Face SVG shown above button
                face = skin_face_svg(meta["hex"], size=30)
                lc   = "#1d4ed8" if is_sel else "#64748b"
                st.markdown(
                    f'<div style="text-align:center;margin-bottom:2px">{face}</div>',
                    unsafe_allow_html=True
                )
                btn_label = ("✓ " if is_sel else "") + meta["label"]
                if st.button(btn_label, key=f"sk_{key}",
                             help=key.replace("_"," "),
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
        <div style="text-align:center;padding:56px 40px;background:#ffffff;
                    border:1px solid #e2e8f0;border-radius:24px;
                    box-shadow:0 4px 20px rgba(15,25,80,.07)">
          <div style="font-size:52px;margin-bottom:16px">👔</div>
          <div style="font-family:'Lora',serif;font-size:28px;font-weight:700;color:#0f172a;margin-bottom:10px">
            Your colour profile awaits
          </div>
          <div style="font-size:13px;color:#64748b;line-height:1.8;max-width:300px;margin:0 auto">
            Select colours you already own from the sidebar.
            The engine recommends what to buy next.
          </div>
          <div style="margin-top:24px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
            <span style="font-size:11px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:5px 12px;border-radius:20px">Smart shirt picks</span>
            <span style="font-size:11px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:5px 12px;border-radius:20px">Smart pant picks</span>
            <span style="font-size:11px;color:#1d4ed8;background:#eff6ff;border:1px solid #bfdbfe;padding:5px 12px;border-radius:20px">Outfit combinations</span>
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
season_d = inp["season"] if inp["season"] != "All" else "All Seasons"
s_icon   = SEASON_META[inp["season"]]["icon"]

st.markdown(
    f'<div class="page-header">{s_icon} Your Colour Profile</div>'
    f'<div class="page-sub">{len(inp["shirts"])} shirt{"s" if len(inp["shirts"])!=1 else ""}'
    f' · {len(inp["pants"])} pant{"s" if len(inp["pants"])!=1 else ""}'
    f' · {season_d} · {skin_lbl}</div>',
    unsafe_allow_html=True
)

col_card, col_outfits = st.columns([1.05, 1], gap="large")

# ── CARD ──
with col_card:
    qs = QUALITY_STYLE[qual]
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

# ── OUTFITS ──
with col_outfits:
    st.markdown('<div class="sec-label" style="margin-bottom:14px">Top Outfit Combinations</div>', unsafe_allow_html=True)
    for i, o in enumerate(result.get("outfits", [])):
        st.markdown(outfit_row_html(o, i), unsafe_allow_html=True)

    all_combos = result.get("pair_matrix", [])
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
            with cols3[i % 3]:
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
          <div style="font-size:13px;color:#15803d;line-height:1.6">
            Your feedback shapes the ₹299 colour card.<br>
            We'll build a better product because of it.
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
            format_func=lambda x: "⭐"*x, label_visibility="collapsed",
        )
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-label">Would you buy a personalised colour card for ₹299?</div>', unsafe_allow_html=True)
        buy_card = st.radio(
            "buy_card",
            ["Yes — I'd buy this", "Maybe — need to see the physical card", "No — not for me"],
            label_visibility="collapsed",
        )
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-label">How likely are you to recommend this to a friend?</div>', unsafe_allow_html=True)
        st.caption("0 = Not at all · 10 = Definitely")
        nps = st.slider("nps", 0, 10, 7, label_visibility="collapsed")
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

        if st.button("Submit Feedback →", type="primary", use_container_width=True):
            outfits = result.get("outfits", [])
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
    admin_pw = st.secrets.get("ADMIN_PASSWORD", "")
    entered  = st.text_input("Admin password", type="password", key="admin_pw_input")
    if entered != admin_pw:
        st.error("Incorrect password.") if entered else st.info("Enter the admin password.")
        st.stop()
    db = get_storage()
    if db.empty:
        st.info("No feedback yet.")
        st.stop()
    total    = len(db)
    avg_star = round(db["star_rating"].mean(), 1)
    avg_nps  = round(db["nps_score"].mean(), 1)
    buy_yes  = round(db["buy_card"].str.startswith("Yes").sum() / total * 100)
    m1,m2,m3,m4 = st.columns(4)
    for col, val, lbl in [
        (m1, total,         "Responses"),
        (m2, f"{avg_star}⭐","Avg Rating"),
        (m3, avg_nps,        "Avg NPS"),
        (m4, f"{buy_yes}%",  "Would Buy"),
    ]:
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

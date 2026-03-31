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
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── App background ── */
.stApp { background: #1c1a17; }
section[data-testid="stSidebar"] { background: #141210 !important; border-right: 1px solid #2e2a22; }
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem 2rem; }
[data-testid="stHeader"] { background: transparent !important; }

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Main content area ── */
.block-container { padding: 2rem 2.5rem !important; max-width: 1400px; }

/* ── Sidebar section headers ── */
.sb-section {
  font-size: 9px; font-weight: 600; letter-spacing: .2em;
  color: #6b5f4a; text-transform: uppercase; margin: 18px 0 8px;
  display: flex; align-items: center; gap: 8px;
}
.sb-section::after {
  content: ''; flex: 1; height: 1px; background: #2e2a22;
}

/* ── Season buttons ── */
.season-btn {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 10px 6px; border-radius: 12px; cursor: pointer;
  border: 1.5px solid #2e2a22; background: #1c1a17;
  transition: all .15s; min-width: 52px;
}
.season-btn:hover { border-color: #8b6914; background: #221f18; }
.season-btn.sel { border-color: #C9A84C; background: #231e0e; }
.season-icon { font-size: 22px; line-height: 1; }
.season-name { font-size: 9px; font-weight: 600; color: #6b5f4a;
               text-transform: uppercase; letter-spacing: .08em; }
.season-btn.sel .season-name { color: #C9A84C; }

/* ── Skin tone buttons ── */
.skin-row { display: flex; gap: 6px; margin-bottom: 6px; }
.skin-card {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  gap: 5px; padding: 8px 4px; border-radius: 10px;
  border: 1.5px solid #2e2a22; background: #1c1a17;
  cursor: pointer; transition: all .15s;
}
.skin-card:hover { border-color: #8b6914; background: #1f1c14; }
.skin-card.sel { border-color: #C9A84C; background: #231e0e; }
.skin-face { width: 32px; height: 32px; }
.skin-label { font-size: 8px; font-weight: 600; color: #5a5040;
              text-align: center; line-height: 1.2; letter-spacing: .04em; }
.skin-card.sel .skin-label { color: #C9A84C; }
.depth-label { font-size: 9px; color: #4a4030; text-transform: uppercase;
               letter-spacing: .1em; margin: 8px 0 4px; font-weight: 500; }

/* ── Generate button ── */
.stButton > button {
  background: linear-gradient(135deg, #C9A84C, #8B5E00) !important;
  color: #fffdf7 !important; border: none !important;
  border-radius: 12px !important; font-weight: 600 !important;
  font-size: 13px !important; padding: 14px !important;
  letter-spacing: .02em !important;
  box-shadow: 0 4px 16px rgba(201,168,76,.25) !important;
}
.stButton > button:hover { opacity: .88 !important; }
.stButton > button:disabled {
  background: #2e2a22 !important; color: #5a5040 !important;
  box-shadow: none !important;
}

/* ── Page header ── */
.page-header {
  font-family: 'Cormorant Garamond', serif;
  font-size: 36px; font-weight: 700; color: #f0ece4;
  letter-spacing: -.5px; margin-bottom: 4px;
}
.page-sub { font-size: 12px; color: #6b5f4a; margin-bottom: 28px; }

/* ── Profile card ── */
.profile-card {
  background: #211e18; border: 1px solid #3a3020;
  border-radius: 20px; padding: 28px; position: relative; overflow: hidden;
}
.card-accent { position: absolute; top: 0; left: 0; right: 0; height: 3px;
               background: linear-gradient(90deg,#8B5E00,#C9A84C,#e8c56a,#C9A84C,#8B5E00); }
.card-glow { position: absolute; top: -60px; right: -60px; width: 200px; height: 200px;
             border-radius: 50%;
             background: radial-gradient(circle,rgba(201,168,76,.06) 0%,transparent 70%);
             pointer-events: none; }
.card-eyebrow { font-size: 9px; letter-spacing: .2em; color: #C9A84C;
                font-weight: 600; text-transform: uppercase; margin-bottom: 6px; }
.card-title {
  font-family: 'Cormorant Garamond', serif; font-size: 26px;
  font-weight: 700; color: #f0ece4; letter-spacing: -.3px; margin-bottom: 2px;
}
.card-meta { font-size: 11px; color: #6b5f4a; margin-bottom: 20px; }
.card-divider { height: 1px; background: linear-gradient(90deg,transparent,#3a3020,transparent); margin: 16px 0; }

/* ── Section label ── */
.sec-label {
  font-size: 9px; font-weight: 600; letter-spacing: .16em;
  text-transform: uppercase; color: #6b5f4a; margin: 0 0 12px;
  display: flex; align-items: center; gap: 8px;
}
.sec-label::before { content:''; width:12px; height:1px; background:#C9A84C; }

/* ── Rectangular color swatches ── */
.rect-swatch-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
.rect-swatch-item { display: flex; flex-direction: column; align-items: center; gap: 5px; }
.rect-swatch {
  width: 60px; height: 90px; border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0,0,0,.4); position: relative;
  transition: transform .15s;
}
.rect-swatch:hover { transform: translateY(-3px); }
.rect-swatch-name { font-size: 9px; color: #9a8a70; text-align: center;
                    max-width: 64px; line-height: 1.3; font-weight: 500; }
.rect-swatch-score { font-size: 9px; color: #C9A84C; font-weight: 700;
                     font-family: 'DM Mono', monospace; }
.swatch-rank { position: absolute; top: -5px; right: -5px; width: 16px; height: 16px;
               border-radius: 50%; background: #C9A84C; color: #1c1a17;
               font-size: 8px; font-weight: 700;
               display: flex; align-items: center; justify-content: center; }
.swatch-skin-star { position: absolute; bottom: -5px; right: -5px; width: 16px; height: 16px;
                    border-radius: 50%; background: #e8734a; color: white;
                    font-size: 9px; display: flex; align-items: center; justify-content: center; }

/* ── Outfit mannequin row ── */
.outfit-entry { display: flex; align-items: center; gap: 14px; padding: 12px 16px;
                border-radius: 14px; background: #1a1812; border: 1px solid #2e2a22;
                margin-bottom: 8px; transition: border-color .15s; }
.outfit-entry:hover { border-color: #C9A84C44; }
.outfit-rank { font-size: 11px; color: #4a4030; font-weight: 700;
               font-family: 'DM Mono', monospace; width: 22px; text-align: center; flex-shrink: 0; }
.outfit-names { font-size: 12px; color: #d0c8b0; font-weight: 500; flex: 1; }
.outfit-family { font-size: 10px; color: #5a5040; margin-top: 2px; }
.outfit-score-wrap { text-align: right; flex-shrink: 0; }
.outfit-score-num { font-size: 12px; color: #C9A84C; font-weight: 700;
                    font-family: 'DM Mono', monospace; }
.outfit-bar-bg { width: 60px; height: 3px; background: #2e2a22; border-radius: 2px;
                 overflow: hidden; margin-top: 4px; }
.outfit-bar-fill { height: 100%; border-radius: 2px;
                   background: linear-gradient(90deg, #8B5E00, #C9A84C); }

/* ── Quality badge ── */
.q-badge { display: inline-block; padding: 4px 14px; border-radius: 20px;
           font-size: 10px; font-weight: 700; letter-spacing: .06em; }

/* ── Prompt bubble ── */
.prompt-bubble { background: #1a1812; border: 1px solid #3a3020; border-radius: 14px;
                 padding: 16px 20px; display: flex; align-items: center;
                 justify-content: space-between; gap: 16px; margin-top: 12px; }
.pb-q { font-size: 13px; font-weight: 600; color: #f0ece4; }
.pb-sub { font-size: 11px; color: #6b5f4a; margin-top: 2px; }

/* ── Combo grid ── */
.combo-cell { background: #1a1812; border: 1px solid #2e2a22; border-radius: 14px;
              padding: 14px 10px; display: flex; flex-direction: column;
              align-items: center; gap: 8px; transition: border-color .15s; }
.combo-cell:hover { border-color: #C9A84C44; }

/* ── Feedback ── */
.feedback-wrap { background: #fffdf7; border: 1px solid #e0d4b8; border-radius: 20px;
                 padding: 32px; max-width: 560px; margin: 0 auto; }
.fb-title { font-family: 'Cormorant Garamond', serif; font-size: 24px;
            font-weight: 700; color: #1a1208; margin-bottom: 6px; }
.fb-sub { font-size: 12px; color: #9a8a70; margin-bottom: 24px; }
.fb-label { font-size: 12px; font-weight: 600; color: #2a1f0a; margin-bottom: 6px; }
.thankyou { background: #141f10; border: 1px solid #3a5a2a55; border-radius: 16px;
            padding: 36px; text-align: center; max-width: 480px; margin: 0 auto; }
.ty-title { font-family: 'Cormorant Garamond', serif; font-size: 26px;
            color: #7ab05a; font-weight: 700; margin-bottom: 8px; }
.ty-sub { font-size: 13px; color: #5a7a40; line-height: 1.6; }

/* ── Metric tile ── */
.metric-tile { background: #211e18; border: 1px solid #3a3020; border-radius: 14px;
               padding: 18px; text-align: center; }
.metric-val { font-family: 'Cormorant Garamond', serif; font-size: 32px;
              color: #C9A84C; font-weight: 700; }
.metric-lbl { font-size: 11px; color: #6b5f4a; margin-top: 3px; }

/* ── Streamlit widget overrides for dark theme ── */
.stMultiSelect > div > div { background: #1a1812 !important; border-color: #3a3020 !important; color: #d0c8b0 !important; }
.stRadio > div { gap: 8px !important; }
/* ── Radio button text readable on dark bg ── */
.stRadio label, .stRadio label p,
.stRadio span[data-testid="stMarkdownContainer"] p { color: #c0b090 !important; font-size:13px !important; }
.stRadio [data-testid="stWidgetLabel"] { color: #c0b090 !important; }
/* ── Select slider labels ── */
[data-testid="stSelectSlider"] > div { color: #C9A84C !important; }
[data-testid="stSelectSlider"] label { color: #c0b090 !important; }
/* ── Slider ── */
.stSlider > div > div > div { background: #C9A84C !important; }
.stSlider p, .stSlider label { color: #c0b090 !important; }
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] { color: #6b5f4a !important; }
/* ── Caption ── */
.stCaption, .stCaption p { color: #6b5f4a !important; }
/* ── All markdown text ── */
div[data-testid="stMarkdownContainer"] p { color: #c0b090; }
/* ── Multiselect text ── */
.stMultiSelect span, .stMultiSelect p, .stMultiSelect label { color: #c0b090 !important; }
.stMultiSelect [data-baseweb="tag"] span { color: #f0ece4 !important; }
/* ── Feedback section widget text on LIGHT bg ── */
.feedback-wrap .stRadio label, .feedback-wrap .stRadio label p { color: #2a1f0a !important; }
.feedback-wrap label { color: #2a1f0a !important; }
.feedback-wrap p { color: #5a4a30 !important; }
.feedback-wrap [data-testid="stMarkdownContainer"] p { color: #2a1f0a !important; }
.feedback-wrap .stCaption p { color: #9a8a70 !important; }
.feedback-wrap [data-testid="stTickBarMin"],
.feedback-wrap [data-testid="stTickBarMax"] { color: #9a8a70 !important; }
/* ── Sidebar multiselect ── */
[data-testid="stSidebar"] .stMultiSelect > div { background: #1a1812 !important; border-color: #3a3020 !important; }
[data-testid="stSidebar"] .stMultiSelect span { color: #d0c8b0 !important; }
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
    "All":    {"icon": "🌀", "label": "All"},
    "Spring": {"icon": "🌸", "label": "Spring"},
    "Summer": {"icon": "☀️", "label": "Summer"},
    "Autumn": {"icon": "🍂", "label": "Autumn"},
    "Winter": {"icon": "❄️", "label": "Winter"},
}

SKIN_META = {
    "Light_Warm":    {"hex":"#F5CBA7","label":"Warm"},
    "Light_Cool":    {"hex":"#FAD7C3","label":"Cool"},
    "Light_Neutral": {"hex":"#F0C89A","label":"Neutral"},
    "Medium_Warm":   {"hex":"#C68642","label":"Warm"},
    "Medium_Cool":   {"hex":"#B87333","label":"Cool"},
    "Medium_Neutral":{"hex":"#A0724A","label":"Neutral"},
    "Deep_Warm":     {"hex":"#6B3A2A","label":"Warm"},
    "Deep_Cool":     {"hex":"#4A2C2A","label":"Cool"},
    "Deep_Neutral":  {"hex":"#3B1F1A","label":"Neutral"},
}

QUALITY_STYLE = {
    "Premium":    "background:#3a2e08;color:#e8c56a;border:1px solid #C9A84C55",
    "Strong":     "background:#0e2a1a;color:#6ec99a;border:1px solid #4a9a7055",
    "Developing": "background:#2a1e08;color:#d4a040;border:1px solid #a07030aa",
    "Starter":    "background:#201e1a;color:#8a8070;border:1px solid #5a503844",
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

def text_col(h): return "#1a1208" if lum(h)>155 else "#fffdf7"

def quality_label(s):
    return "Premium" if s>12 else "Strong" if s>8 else "Developing" if s>4 else "Starter"

def skin_face_svg(hex_color, size=32):
    """SVG face silhouette filled with the skin tone hex."""
    tc = "#ffffff" if lum(hex_color) < 100 else "#2a1a0a"
    shadow = "#00000030"
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="16" cy="14" rx="10" ry="11" fill="{hex_color}"/>
      <ellipse cx="16" cy="13" rx="9" ry="10" fill="{hex_color}"/>
      <ellipse cx="13" cy="12" rx="2" ry="1.5" fill="{shadow}"/>
      <ellipse cx="19" cy="12" rx="2" ry="1.5" fill="{shadow}"/>
      <ellipse cx="13" cy="11.5" rx="1.3" ry="1.2" fill="{tc}" opacity=".7"/>
      <ellipse cx="19" cy="11.5" rx="1.3" ry="1.2" fill="{tc}" opacity=".7"/>
      <ellipse cx="13.5" cy="12" rx=".7" ry=".8" fill="{tc}" opacity=".15"/>
      <ellipse cx="19.5" cy="12" rx=".7" ry=".8" fill="{tc}" opacity=".15"/>
      <ellipse cx="16" cy="16.5" rx="1.2" ry=".8" fill="{shadow}" opacity=".5"/>
      <path d="M12.5,19.5 Q16,22 19.5,19.5" stroke="{shadow}" stroke-width="1.2" fill="none" stroke-linecap="round" opacity=".6"/>
      <ellipse cx="16" cy="25" rx="8" ry="5" fill="{hex_color}" opacity=".7"/>
      <rect x="8" y="22" width="16" height="10" rx="4" fill="{hex_color}" opacity=".5"/>
    </svg>"""

def rect_swatch_html(items, score_key):
    html = '<div class="rect-swatch-grid">'
    for i, item in enumerate(items):
        score = item.get(score_key, 0)
        rank  = f'<div class="swatch-rank">{i+1}</div>' if i == 0 else ""
        star  = '<div class="swatch-skin-star">★</div>' if item.get("skin_delta",0)>0 else ""
        tc    = text_col(item["hex"])
        html += f"""
        <div class="rect-swatch-item">
          <div class="rect-swatch" style="background:{item['hex']}">
            {rank}{star}
          </div>
          <div class="rect-swatch-name">{item['color']}</div>
          <div class="rect-swatch-score">{score:.1f}</div>
        </div>"""
    html += "</div>"
    return html

def mannequin_svg(shirt_hex, pant_hex, shirt_name, pant_name, width=110):
    """Clean SVG mannequin figure — shirt fills torso+sleeves, pant fills legs."""
    stc = text_col(shirt_hex)
    ptc = text_col(pant_hex)
    # shadow/highlight helpers
    def darker(h, amt=30):
        hx=h.lstrip("#")
        r,g,b=int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
        return f"#{max(0,r-amt):02x}{max(0,g-amt):02x}{max(0,b-amt):02x}"
    sh = darker(shirt_hex, 25)
    ph = darker(pant_hex, 25)
    return f"""<svg width="{width}" height="220" viewBox="0 0 110 220"
      xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 4px 12px rgba(0,0,0,.5))">

      <!-- SHADOW -->
      <ellipse cx="55" cy="214" rx="28" ry="5" fill="#00000044"/>

      <!-- SHOES -->
      <ellipse cx="41" cy="206" rx="14" ry="6" fill="#1a1812"/>
      <ellipse cx="69" cy="206" rx="14" ry="6" fill="#1a1812"/>
      <rect x="30" y="200" width="24" height="8" rx="4" fill="#1a1812"/>
      <rect x="56" y="200" width="24" height="8" rx="4" fill="#1a1812"/>

      <!-- PANTS -->
      <rect x="33" y="118" width="20" height="86" rx="7" fill="{pant_hex}"/>
      <rect x="57" y="118" width="20" height="86" rx="7" fill="{pant_hex}"/>
      <!-- pant shading -->
      <rect x="33" y="118" width="6" height="86" rx="4" fill="{ph}" opacity=".35"/>
      <rect x="57" y="118" width="6" height="86" rx="4" fill="{ph}" opacity=".35"/>
      <!-- belt -->
      <rect x="30" y="112" width="50" height="12" rx="5" fill="{ph}"/>
      <rect x="51" y="114" width="8" height="8" rx="2" fill="#888" opacity=".6"/>

      <!-- SHIRT TORSO -->
      <rect x="28" y="60" width="54" height="60" rx="8" fill="{shirt_hex}"/>
      <!-- shirt side shading -->
      <rect x="28" y="60" width="8" height="60" rx="4" fill="{sh}" opacity=".3"/>
      <rect x="74" y="60" width="8" height="60" rx="4" fill="{sh}" opacity=".3"/>
      <!-- collar V -->
      <polygon points="55,62 47,74 55,78 63,74" fill="{sh}" opacity=".4"/>
      <!-- buttons -->
      <circle cx="55" cy="82" r="1.5" fill="{sh}" opacity=".5"/>
      <circle cx="55" cy="92" r="1.5" fill="{sh}" opacity=".5"/>
      <circle cx="55" cy="102" r="1.5" fill="{sh}" opacity=".5"/>
      <!-- pocket -->
      <rect x="36" y="72" width="14" height="11" rx="3" fill="{sh}" opacity=".25"/>

      <!-- LEFT SLEEVE -->
      <path d="M28,62 Q10,66 8,94 Q7,102 16,104 Q26,106 30,98 L30,62 Z"
            fill="{shirt_hex}"/>
      <path d="M28,62 Q18,66 16,94 Q15,102 16,104 Q10,100 8,92 Q8,68 28,62Z"
            fill="{sh}" opacity=".2"/>
      <!-- left hand -->
      <ellipse cx="13" cy="108" rx="7" ry="5" fill="#C68642"/>

      <!-- RIGHT SLEEVE -->
      <path d="M82,62 Q100,66 102,94 Q103,102 94,104 Q84,106 80,98 L80,62 Z"
            fill="{shirt_hex}"/>
      <path d="M82,62 Q92,66 94,94 Q95,102 94,104 Q100,100 102,92 Q102,68 82,62Z"
            fill="{sh}" opacity=".2"/>
      <!-- right hand -->
      <ellipse cx="97" cy="108" rx="7" ry="5" fill="#C68642"/>

      <!-- NECK -->
      <rect x="47" y="44" width="16" height="20" rx="6" fill="#C68642"/>

      <!-- HEAD -->
      <!-- hair -->
      <ellipse cx="55" cy="26" rx="20" ry="22" fill="#1a0f00"/>
      <!-- face -->
      <ellipse cx="55" cy="28" rx="17" ry="19" fill="#C68642"/>
      <!-- ears -->
      <ellipse cx="38" cy="29" rx="4" ry="5" fill="#C68642"/>
      <ellipse cx="72" cy="29" rx="4" ry="5" fill="#C68642"/>
      <!-- eye shadows -->
      <ellipse cx="48" cy="26" rx="4" ry="2.5" fill="#00000020"/>
      <ellipse cx="62" cy="26" rx="4" ry="2.5" fill="#00000020"/>
      <!-- eyes -->
      <ellipse cx="48" cy="25.5" rx="2.8" ry="2.5" fill="#1a0f00"/>
      <ellipse cx="62" cy="25.5" rx="2.8" ry="2.5" fill="#1a0f00"/>
      <!-- eye shine -->
      <circle cx="49" cy="24.5" r=".9" fill="white" opacity=".7"/>
      <circle cx="63" cy="24.5" r=".9" fill="white" opacity=".7"/>
      <!-- eyebrows -->
      <path d="M44,21 Q48,18.5 52,20" stroke="#1a0f00" stroke-width="1.4" fill="none" stroke-linecap="round"/>
      <path d="M58,20 Q62,18.5 66,21" stroke="#1a0f00" stroke-width="1.4" fill="none" stroke-linecap="round"/>
      <!-- nose -->
      <ellipse cx="55" cy="31" rx="2" ry="1.5" fill="#00000022"/>
      <!-- mouth -->
      <path d="M49,36 Q55,40 61,36" stroke="#00000033" stroke-width="1.4" fill="none" stroke-linecap="round"/>
      <!-- hair fringe -->
      <path d="M35,20 Q40,8 55,6 Q70,8 75,20 Q70,14 55,13 Q40,14 35,20Z" fill="#1a0f00"/>

      <!-- COLOR LABELS -->
      <rect x="6" y="66" width="45" height="14" rx="4" fill="#00000066"/>
      <text x="28" y="76" text-anchor="middle" font-size="7.5" font-family="DM Sans,sans-serif"
            font-weight="600" fill="{stc if stc=='#fffdf7' else '#f0ece4'}" opacity=".9">{shirt_name[:10]}</text>

      <rect x="22" y="140" width="66" height="14" rx="4" fill="#00000066"/>
      <text x="55" y="150" text-anchor="middle" font-size="7.5" font-family="DM Sans,sans-serif"
            font-weight="600" fill="{ptc if ptc=='#fffdf7' else '#f0ece4'}" opacity=".9">{pant_name[:12]}</text>
    </svg>"""

def outfit_row_html(outfit, index):
    pct = round((outfit["score"] / 5) * 100)
    svg = mannequin_svg(outfit["shirt_hex"], outfit["pant_hex"],
                        outfit["shirt"], outfit["pant"], width=80)
    qual_col = "#e8c56a" if outfit["score"]>=4 else "#6ec99a" if outfit["score"]>=3 else "#d4a040" if outfit["score"]>=2 else "#8a8070"
    return f"""
    <div class="outfit-entry">
      <div class="outfit-rank">#{index+1}</div>
      <div style="flex-shrink:0">{svg}</div>
      <div style="flex:1;min-width:0">
        <div class="outfit-names">{outfit['shirt']} + {outfit['pant']}</div>
        <div class="outfit-family">Match score {outfit['score']:.1f} / 5.0</div>
        <div class="outfit-bar-bg" style="margin-top:6px">
          <div class="outfit-bar-fill" style="width:{pct}%"></div>
        </div>
      </div>
      <div class="outfit-score-wrap">
        <div class="outfit-score-num">{outfit['score']:.1f}</div>
        <div style="font-size:9px;color:{qual_col};font-weight:600;margin-top:2px">
          {"Excellent" if outfit["score"]>=4 else "Good" if outfit["score"]>=3 else "Decent" if outfit["score"]>=2 else "Weak"}
        </div>
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
    qcol    = "#e8c56a" if score>=4 else "#6ec99a" if score>=3 else "#d4a040" if score>=2 else "#8a8070"
    return f"""
    <div class="combo-cell">
      {svg}
      <div style="font-size:10px;color:#c0b090;text-align:center;line-height:1.4;font-weight:500">{shirt}<br>{pant}</div>
      <div style="display:flex;align-items:center;justify-content:space-between;width:100%">
        <span style="font-size:9px;font-weight:700;color:{qcol}">{qual}</span>
        <span style="font-size:11px;color:#C9A84C;font-weight:700;font-family:monospace">{score:.1f}</span>
      </div>
      <div style="width:100%;height:3px;background:#2e2a22;border-radius:2px;overflow:hidden">
        <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#8B5E00,#C9A84C);border-radius:2px"></div>
      </div>
    </div>"""

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
      <div style="width:32px;height:32px;border-radius:9px;
                  background:linear-gradient(135deg,#C9A84C,#6B3A00);
                  display:flex;align-items:center;justify-content:center;
                  box-shadow:0 3px 8px rgba(201,168,76,.3)">
        <span style="color:#fffdf7;font-size:16px;font-family:'Cormorant Garamond',serif;font-weight:700">W</span>
      </div>
      <div>
        <div style="font-size:15px;font-weight:700;color:#f0ece4;
                    font-family:'Cormorant Garamond',serif;letter-spacing:-.2px">
          Wardrobe <span style="color:#C9A84C">Engine</span>
        </div>
        <div style="font-size:10px;color:#4a4030;margin-top:1px">Personal Colour Intelligence</div>
      </div>
    </div>
    <div style="height:1px;background:#2e2a22;margin:12px 0 18px"></div>
    """, unsafe_allow_html=True)

    # ── SHIRTS ──
    st.markdown('<div class="sb-section">① Shirts you own</div>', unsafe_allow_html=True)
    selected_shirts = st.multiselect(
        "shirts", SHIRT_COLORS,
        label_visibility="collapsed",
        placeholder="Choose shirt colours…",
    )
    if selected_shirts:
        dots = "".join([
            f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
            f'background:{MASTER_COLORS[s]["hex"]};margin-right:4px;vertical-align:middle;'
            f'border:1px solid rgba(255,255,255,.1)"></span>'
            f'<span style="font-size:10px;color:#8a7a60">{s}</span>&nbsp;&nbsp;'
            for s in selected_shirts
        ])
        st.markdown(f'<div style="margin:-4px 0 6px;line-height:2">{dots}</div>', unsafe_allow_html=True)

    # ── PANTS ──
    st.markdown('<div class="sb-section">② Pants you own</div>', unsafe_allow_html=True)
    selected_pants = st.multiselect(
        "pants", PANT_COLORS,
        label_visibility="collapsed",
        placeholder="Choose pant colours…",
    )

    # ── SEASON ──
    st.markdown('<div class="sb-section">③ Season</div>', unsafe_allow_html=True)
    season_cols = st.columns(5)
    for col, (key, meta) in zip(season_cols, SEASON_META.items()):
        is_sel = st.session_state.selected_season == key
        with col:
            if st.button(meta["icon"], key=f"season_{key}", help=key, use_container_width=True):
                st.session_state.selected_season = key
                st.rerun()
            st.markdown(
                f'<div style="text-align:center;font-size:8px;font-weight:600;'
                f'letter-spacing:.06em;text-transform:uppercase;margin-top:-6px;'
                f'color:{"#C9A84C" if is_sel else "#4a4030"}">{meta["label"]}</div>',
                unsafe_allow_html=True
            )
    selected_season = st.session_state.selected_season

    # ── SKIN TONE ──
    st.markdown('<div class="sb-section">④ Skin tone <span style="color:#4a4030;font-weight:400;text-transform:none;letter-spacing:0;font-size:9px">(optional)</span></div>', unsafe_allow_html=True)

    for depth, keys in [
        ("Light",  ["Light_Warm",  "Light_Cool",  "Light_Neutral"]),
        ("Medium", ["Medium_Warm", "Medium_Cool", "Medium_Neutral"]),
        ("Deep",   ["Deep_Warm",   "Deep_Cool",   "Deep_Neutral"]),
    ]:
        st.markdown(f'<div class="depth-label">{depth}</div>', unsafe_allow_html=True)
        skin_cols = st.columns(3)
        for col, key in zip(skin_cols, keys):
            meta   = SKIN_META[key]
            is_sel = st.session_state.selected_skin == key
            with col:
                face_svg = skin_face_svg(meta["hex"], size=32)
                border   = "#C9A84C" if is_sel else "#2e2a22"
                bg       = "#231e0e" if is_sel else "#1c1a17"
                skin_title = key.replace("_", " ")
                skin_sel_class = "sel" if is_sel else ""
                skin_html = (
                    f'<div class="skin-card {skin_sel_class}" '
                    f'style="border-color:{border};background:{bg}">'
                    + face_svg
                    + f'<div class="skin-label">{meta["label"]}</div></div>'
                )
                st.markdown(skin_html, unsafe_allow_html=True)
                # Invisible button for click handling
                if st.button("·", key=f"sk_{key}", help=key.replace("_"," "),
                             use_container_width=True):
                    st.session_state.selected_skin = "" if is_sel else key
                    st.rerun()

    selected_skin = st.session_state.selected_skin
    if selected_skin:
        meta = SKIN_META[selected_skin]
        face = skin_face_svg(meta["hex"], size=18)
        st.markdown(
            f'<div style="margin-top:8px;padding:8px 12px;border-radius:9px;'
            f'background:#231e0e;border:1px solid #C9A84C44;'
            f'display:flex;align-items:center;gap:8px;font-size:11px;color:#C9A84C;font-weight:600">'
            f'{face} {selected_skin.replace("_"," ")} · active ✓</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    # ── GENERATE ──
    has_input = bool(selected_shirts or selected_pants)
    run = st.button(
        f"{'✦  ' if has_input else ''}Generate My Colour Profile",
        type="primary", use_container_width=True, disabled=not has_input,
    )
    if not has_input:
        st.markdown('<div style="font-size:10px;color:#4a4030;text-align:center;margin-top:6px">Select at least one colour to begin</div>', unsafe_allow_html=True)

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
        "shirts":selected_shirts,"pants":selected_pants,
        "season":selected_season,"skin":selected_skin,
    }

# ─────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────
if st.session_state.result is None:
    st.markdown('<div style="height:80px"></div>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.markdown(f"""
        <div style="text-align:center;padding:56px 40px;background:#211e18;
                    border:1px solid #3a3020;border-radius:24px">
          <div style="font-size:52px;margin-bottom:16px">👔</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:28px;
                      font-weight:700;color:#f0ece4;margin-bottom:10px">
            Your colour profile awaits
          </div>
          <div style="font-size:13px;color:#6b5f4a;line-height:1.8;max-width:300px;margin:0 auto">
            Select the colours you already own from the sidebar.
            The engine recommends what to buy next.
          </div>
          <div style="margin-top:24px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
            {"".join([f'<span style="font-size:10px;color:#C9A84C;background:#2a2010;border:1px solid #C9A84C33;padding:5px 12px;border-radius:20px">{t}</span>' for t in ["Smart shirt picks","Smart pant picks","Outfit combinations","Graph network"]])}
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
season_icon = SEASON_META[inp["season"]]["icon"]

# Page header
st.markdown(f"""
<div class="page-header">{season_icon} Your Colour Profile</div>
<div class="page-sub">
  {len(inp['shirts'])} shirt{'s' if len(inp['shirts'])!=1 else ''}
  · {len(inp['pants'])} pant{'s' if len(inp['pants'])!=1 else ''}
  · {season_d} · {skin_lbl}
</div>
""", unsafe_allow_html=True)

col_card, col_outfits = st.columns([1.05, 1], gap="large")

# ── PROFILE CARD ─────────────────────────────────────────────
with col_card:
    q_style = QUALITY_STYLE[qual]
    card = f"""
    <div class="profile-card">
      <div class="card-accent"></div>
      <div class="card-glow"></div>
      <div class="card-eyebrow">Wardrobe Engine · Colour Profile</div>
      <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:4px">
        <div class="card-title">Your Style Profile</div>
        <span class="q-badge" style="{q_style}">{qual}</span>
      </div>
      <div class="card-meta">{season_icon} {season_d} · {skin_lbl}</div>
      <div class="card-divider"></div>"""

    if result["smart_shirts"]:
        card += '<div class="sec-label">Smart Shirts to Buy</div>'
        card += rect_swatch_html(result["smart_shirts"], "shirt_score")

    if result["smart_pants"]:
        card += '<div class="sec-label">Smart Pants to Buy</div>'
        card += rect_swatch_html(result["smart_pants"], "pant_score")

    if result["all_season_neutrals"]:
        card += '<div class="sec-label">All-Season Neutrals</div>'
        card += rect_swatch_html(result["all_season_neutrals"], "neutral_score")

    card += f"""
      <div class="card-divider"></div>
      <div style="display:flex;justify-content:space-between;font-size:9px;color:#4a4030">
        <span>{season_icon} {season_d} · {skin_lbl}</span>
        <span style="font-family:monospace;letter-spacing:.06em">wardrobeengine.com</span>
      </div>
    </div>"""
    st.markdown(card, unsafe_allow_html=True)

# ── OUTFIT COMBINATIONS ──────────────────────────────────────
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
            if st.button("Show all combinations ✦", use_container_width=True):
                st.session_state.show_all_combos = True
                st.rerun()
        with bc2:
            if st.button("Skip", use_container_width=True):
                pass
    else:
        st.markdown(f'<div style="font-size:12px;font-weight:600;color:#d0c8b0;margin-bottom:14px">All combinations <span style="color:#4a4030;font-weight:400">· {len(all_combos)} pairings</span></div>', unsafe_allow_html=True)
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
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#3a3020,transparent);margin-bottom:40px"></div>', unsafe_allow_html=True)

if st.session_state.feedback_done:
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.markdown("""
        <div class="thankyou">
          <div style="font-size:48px;margin-bottom:16px">🙏</div>
          <div class="ty-title">Thank you!</div>
          <div class="ty-sub">Your feedback shapes the ₹299 colour card.<br>We'll build a better product because of it.</div>
        </div>
        """, unsafe_allow_html=True)
else:
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.markdown('<div class="feedback-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="fb-title">Share your feedback</div>', unsafe_allow_html=True)
        st.markdown('<div class="fb-sub">2 minutes · helps us build a better product</div>', unsafe_allow_html=True)

        st.markdown('<div class="fb-label">How useful were these recommendations?</div>', unsafe_allow_html=True)
        star_rating = st.select_slider(
            "star_rating", options=[1,2,3,4,5], value=4,
            format_func=lambda x: "⭐"*x,
            label_visibility="collapsed",
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
            outfits  = result.get("outfits", [])
            top_o    = f"{outfits[0]['shirt']} + {outfits[0]['pant']}" if outfits else ""
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
    total=len(db)
    avg_star=round(db["star_rating"].mean(),1)
    avg_nps=round(db["nps_score"].mean(),1)
    buy_yes=round(db["buy_card"].str.startswith("Yes").sum()/total*100)
    m1,m2,m3,m4=st.columns(4)
    for col,val,lbl in [(m1,total,"Responses"),(m2,f"{avg_star}⭐","Avg Rating"),
                        (m3,avg_nps,"Avg NPS"),(m4,f"{buy_yes}%","Would Buy")]:
        col.markdown(f'<div class="metric-tile"><div class="metric-val">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
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
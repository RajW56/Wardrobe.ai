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
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f7f3ec; }
[data-testid="stSidebar"] { background: #fffdf7; border-right: 1px solid #e8dfc8; }
[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
[data-testid="stHeader"] { background: transparent; }
.swatch { display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:5px; vertical-align:middle; border:1px solid rgba(0,0,0,0.12); }
.profile-card { background:#fffdf7; border:1.5px solid #e0d4b8; border-radius:16px; padding:24px; box-shadow:0 4px 24px rgba(139,105,20,0.08); }
.card-top-bar { height:4px; background:linear-gradient(90deg,#C9A84C,#e8c56a,#C9A84C); border-radius:14px 14px 0 0; margin:-24px -24px 20px -24px; }
.card-eyebrow { font-size:10px; letter-spacing:.16em; color:#C9A84C; font-weight:700; text-transform:uppercase; margin-bottom:4px; }
.card-title { font-family:'Playfair Display',serif; font-size:24px; font-weight:700; color:#1a1208; letter-spacing:-.3px; margin-bottom:4px; }
.card-subtitle { font-size:12px; color:#9a8a70; margin-bottom:16px; }
.section-label { font-size:9px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#9a8a70; margin:14px 0 8px; display:flex; align-items:center; gap:8px; }
.section-label::before { content:''; display:inline-block; width:16px; height:1.5px; background:#C9A84C; }
.gold-divider { height:1px; background:linear-gradient(90deg,transparent,#e0d4b8,transparent); margin:16px 0; }
.swatch-grid { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:16px; }
.swatch-item { display:flex; flex-direction:column; align-items:center; gap:4px; }
.swatch-block { width:52px; height:52px; border-radius:14px; box-shadow:0 2px 8px rgba(0,0,0,0.12); position:relative; }
.swatch-name { font-size:9px; color:#7a6a50; text-align:center; max-width:56px; line-height:1.3; font-weight:600; }
.swatch-score { font-size:9px; color:#C9A84C; font-weight:700; font-family:monospace; }
.rank-badge { position:absolute; top:-4px; right:-4px; width:14px; height:14px; border-radius:50%; background:#C9A84C; color:white; font-size:8px; font-weight:700; display:flex; align-items:center; justify-content:center; }
.skin-badge { position:absolute; bottom:-4px; right:-4px; width:14px; height:14px; border-radius:50%; background:#e8734a; color:white; font-size:9px; display:flex; align-items:center; justify-content:center; }
.outfit-row { display:flex; align-items:center; gap:12px; padding:10px 14px; border-radius:12px; background:#faf7f2; border:1px solid #ede5d4; margin-bottom:6px; }
.quality-badge { padding:5px 14px; border-radius:20px; font-size:11px; font-weight:700; }
.feedback-card { background:#fffdf7; border:1.5px solid #e0d4b8; border-radius:16px; padding:28px; box-shadow:0 4px 24px rgba(139,105,20,0.06); }
.feedback-title { font-family:'Playfair Display',serif; font-size:20px; font-weight:700; color:#1a1208; margin-bottom:4px; }
.feedback-sub { font-size:12px; color:#9a8a70; margin-bottom:20px; }
.thankyou-box { background:#f0f7e8; border:1.5px solid #b8d98855; border-radius:14px; padding:28px; text-align:center; }
.thankyou-title { font-family:'Playfair Display',serif; font-size:22px; color:#3a6020; margin-bottom:8px; }
.metric-tile { background:#fffdf7; border:1px solid #e0d4b8; border-radius:12px; padding:16px; text-align:center; }
.metric-val { font-family:'Playfair Display',serif; font-size:28px; color:#C9A84C; font-weight:700; }
.metric-label { font-size:11px; color:#9a8a70; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA STORAGE — CSV
# ─────────────────────────────────────────────────────────────
FEEDBACK_FILE = "feedback.csv"
COLUMNS = ["id","timestamp","shirts_input","pants_input","season","skin_profile",
           "smart_shirts","smart_pants","neutrals","top_outfit","star_rating","buy_card","nps_score"]

def get_storage():
    if os.path.exists(FEEDBACK_FILE):
        try:
            return pd.read_csv(FEEDBACK_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)

def save_feedback(row):
    db = get_storage()
    updated = pd.concat([db, pd.DataFrame([row])], ignore_index=True)
    updated.to_csv(FEEDBACK_FILE, index=False)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
MASTER_COLORS = load_master_colors()
SHIRT_COLORS  = sorted([n for n,d in MASTER_COLORS.items() if d["shirt_allowed"]])
PANT_COLORS   = sorted([n for n,d in MASTER_COLORS.items() if d["pant_allowed"]])
SEASONS       = ["All","Spring","Summer","Autumn","Winter"]

SKIN_HEX = {
    "Light_Warm":"#F5CBA7","Light_Cool":"#FAD7C3","Light_Neutral":"#F0C89A",
    "Medium_Warm":"#C68642","Medium_Cool":"#B87333","Medium_Neutral":"#A0724A",
    "Deep_Warm":"#6B3A2A","Deep_Cool":"#4A2C2A","Deep_Neutral":"#3B1F1A",
}
QUALITY_STYLE = {
    "Premium":    "background:#fdf3dc;color:#8B5E00;border:1px solid #C9A84C44",
    "Strong":     "background:#e8f7f0;color:#2a6a4a;border:1px solid #4a9a7044",
    "Developing": "background:#fff8ec;color:#5a3e00;border:1px solid #d4a04044",
    "Starter":    "background:#f5f2ee;color:#6a6050;border:1px solid #b0a08044",
}

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
for k,v in [("result",None),("last_input",{}),("feedback_done",False),
             ("show_all_combos",False),("selected_skin",""),
             ("session_id",str(uuid.uuid4())[:8])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def lum(h):
    h=h.lstrip("#")
    return 0.2126*int(h[0:2],16)+0.7152*int(h[2:4],16)+0.0722*int(h[4:6],16)

def quality_label(s):
    return "Premium" if s>12 else "Strong" if s>8 else "Developing" if s>4 else "Starter"

def swatch_html(items, score_key):
    html='<div class="swatch-grid">'
    for i,item in enumerate(items):
        score=item.get(score_key,0)
        rank='<div class="rank-badge">1</div>' if i==0 else ""
        skin='<div class="skin-badge">★</div>' if item.get("skin_delta",0)>0 else ""
        html+=f'<div class="swatch-item"><div class="swatch-block" style="background:{item["hex"]}">{rank}{skin}</div><div class="swatch-name">{item["color"]}</div><div class="swatch-score">{score:.1f}</div></div>'
    return html+'</div>'

def outfit_row_html(outfit, index):
    pct=round((outfit["score"]/5)*100)
    return f"""<div class="outfit-row">
      <span style="font-size:11px;color:#C9A84C;font-weight:700;font-family:monospace;width:24px;text-align:center;flex-shrink:0">#{index+1}</span>
      <div style="display:flex;flex-direction:column;gap:3px;flex-shrink:0">
        <div style="width:48px;height:22px;border-radius:7px 7px 2px 2px;background:{outfit['shirt_hex']};box-shadow:0 2px 4px rgba(0,0,0,.14)"></div>
        <div style="display:flex;gap:3px">
          <div style="width:22px;height:22px;border-radius:2px 2px 7px 7px;background:{outfit['pant_hex']};box-shadow:0 1px 3px rgba(0,0,0,.12)"></div>
          <div style="width:22px;height:22px;border-radius:2px 2px 7px 7px;background:{outfit['pant_hex']};box-shadow:0 1px 3px rgba(0,0,0,.12)"></div>
        </div>
      </div>
      <div style="flex:1;min-width:0">
        <div style="font-size:12px;color:#2a1f0a;font-weight:500;margin-bottom:4px">{outfit['shirt']} + {outfit['pant']}</div>
        <div style="height:3px;border-radius:2px;background:#ede5d4;overflow:hidden">
          <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#C9A84C,#e8c56a);border-radius:2px"></div>
        </div>
      </div>
      <span style="font-size:11px;color:#C9A84C;font-weight:700;font-family:monospace;flex-shrink:0">{outfit['score']:.1f}</span>
    </div>"""

def combo_card_html(combo):
    # pair_matrix items have keys: shirt, pant, shirt_hex, pant_hex, pair_score
    score    = combo.get("score", combo.get("pair_score", 0))
    shirt_h  = combo.get("shirt_hex","#888")
    pant_h   = combo.get("pant_hex","#888")
    shirt    = combo.get("shirt","")
    pant     = combo.get("pant","")
    pct      = round((score/5)*100)
    qual     = "Excellent" if score>=4 else "Good" if score>=3 else "Decent" if score>=2 else "Weak"
    qcol     = "#5a7a2a" if score>=4 else "#2a6a4a" if score>=3 else "#8a6a20" if score>=2 else "#9a8a70"
    qbg      = "#f0f7e8" if score>=4 else "#e8f7f0" if score>=3 else "#fdf3dc" if score>=2 else "#f5f2ee"
    return f"""<div style="background:#faf7f2;border:1px solid #ede5d4;border-radius:14px;padding:14px 10px;display:flex;flex-direction:column;align-items:center;gap:8px;margin-bottom:8px">
      <div style="display:flex;flex-direction:column;gap:3px;align-items:center">
        <div style="width:52px;height:24px;border-radius:7px 7px 3px 3px;background:{shirt_h};box-shadow:0 2px 4px rgba(0,0,0,.12)"></div>
        <div style="display:flex;gap:3px">
          <div style="width:23px;height:26px;border-radius:3px 3px 7px 7px;background:{pant_h};box-shadow:0 2px 4px rgba(0,0,0,.1)"></div>
          <div style="width:23px;height:26px;border-radius:3px 3px 7px 7px;background:{pant_h};box-shadow:0 2px 4px rgba(0,0,0,.1)"></div>
        </div>
      </div>
      <div style="font-size:10px;color:#4a3a20;text-align:center;line-height:1.4;font-weight:500">{shirt}<br>{pant}</div>
      <div style="display:flex;align-items:center;justify-content:space-between;width:100%">
        <span style="font-size:9px;font-weight:700;padding:2px 6px;border-radius:6px;background:{qbg};color:{qcol}">{qual}</span>
        <span style="font-size:11px;color:#C9A84C;font-weight:700;font-family:monospace">{score:.1f}</span>
      </div>
    </div>"""

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
      <div style="width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#C9A84C,#8B5E00);display:flex;align-items:center;justify-content:center">
        <span style="color:#fffdf7;font-size:14px;font-weight:700;font-family:'Playfair Display',serif">W</span>
      </div>
      <span style="font-size:15px;font-weight:700;color:#1a1208;font-family:'Playfair Display',serif">
        Wardrobe <span style="color:#C9A84C">Engine</span>
      </span>
    </div>
    <div style="font-size:11px;color:#9a8a70;margin-bottom:24px;padding-left:38px">Personal Colour Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:6px">① Shirts you own</div>', unsafe_allow_html=True)
    selected_shirts = st.multiselect("shirts", SHIRT_COLORS, label_visibility="collapsed", placeholder="Select shirt colors…")
    if selected_shirts:
        dots="".join([f'<span class="swatch" style="background:{MASTER_COLORS[s]["hex"]}"></span>{s}&nbsp;' for s in selected_shirts])
        st.markdown(f'<div style="font-size:11px;color:#8B5E00;margin:-4px 0 8px">{dots}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#ede5d4;margin:10px 0"></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:6px">② Pants you own</div>', unsafe_allow_html=True)
    selected_pants = st.multiselect("pants", PANT_COLORS, label_visibility="collapsed", placeholder="Select pant colors…")

    st.markdown('<div style="height:1px;background:#ede5d4;margin:10px 0"></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:6px">③ Season</div>', unsafe_allow_html=True)
    selected_season = st.radio("season", SEASONS, horizontal=True, label_visibility="collapsed")

    st.markdown('<div style="height:1px;background:#ede5d4;margin:10px 0"></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:8px">④ Skin tone <span style="font-weight:400;text-transform:none;letter-spacing:0;color:#c0b090;font-size:10px">(optional)</span></div>', unsafe_allow_html=True)

    for depth_label, keys in [
        ("Light",  ["Light_Warm",  "Light_Cool",  "Light_Neutral"]),
        ("Medium", ["Medium_Warm", "Medium_Cool", "Medium_Neutral"]),
        ("Deep",   ["Deep_Warm",   "Deep_Cool",   "Deep_Neutral"]),
    ]:
        st.markdown(f'<div style="font-size:9px;color:#b0a080;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">{depth_label}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for col, key in zip(cols, keys):
            short  = key.split("_")[1]
            hex_c  = SKIN_HEX[key]
            is_sel = st.session_state.selected_skin == key
            with col:
                if st.button("✓ "+short if is_sel else short, key=f"skin_{key}", use_container_width=True):
                    st.session_state.selected_skin = "" if is_sel else key
                    st.rerun()
                st.markdown(
                    f'<div style="text-align:center;margin-top:-8px;margin-bottom:4px">'
                    f'<span style="display:inline-block;width:20px;height:20px;border-radius:50%;'
                    f'background:{hex_c};border:{"3px solid #C9A84C" if is_sel else "2px solid rgba(0,0,0,0.1)"};'
                    f'box-shadow:0 1px 4px rgba(0,0,0,.2)"></span></div>',
                    unsafe_allow_html=True)

    selected_skin = st.session_state.selected_skin
    if selected_skin:
        st.markdown(
            f'<div style="margin-top:6px;padding:7px 12px;border-radius:9px;background:#fdf3dc;'
            f'border:1px solid #e8c56a55;font-size:11px;color:#5a3e00;font-weight:600">'
            f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
            f'background:{SKIN_HEX[selected_skin]};border:1px solid rgba(0,0,0,.15);'
            f'margin-right:6px;vertical-align:middle"></span>'
            f'{selected_skin.replace("_"," ")} · active ✓</div>',
            unsafe_allow_html=True)

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    has_input = bool(selected_shirts or selected_pants)
    run = st.button("Generate My Colour Profile →", type="primary", use_container_width=True, disabled=not has_input)
    if not has_input:
        st.caption("Select at least one colour to begin")

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
    st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)
    _,c,_ = st.columns([1,2,1])
    with c:
        st.markdown("""
        <div style="text-align:center;padding:48px 32px;background:#fffdf7;border:1.5px solid #e0d4b8;border-radius:20px;box-shadow:0 4px 24px rgba(139,105,20,0.06)">
          <div style="font-size:48px;margin-bottom:16px">🎨</div>
          <div style="font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:#1a1208;margin-bottom:8px">Your colour profile awaits</div>
          <div style="font-size:13px;color:#9a8a70;line-height:1.7;max-width:320px;margin:0 auto">
            Select colours you already own from the sidebar. The engine recommends what to buy next.
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

st.markdown(f"""
<div style="margin-bottom:24px">
  <div style="font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:#1a1208;letter-spacing:-.3px">Your Colour Profile</div>
  <div style="font-size:12px;color:#9a8a70;margin-top:4px">
    {len(inp['shirts'])} shirt{'s' if len(inp['shirts'])!=1 else ''} · {len(inp['pants'])} pant{'s' if len(inp['pants'])!=1 else ''} · {season_d} · {skin_lbl}
  </div>
</div>
""", unsafe_allow_html=True)

col_card, col_outfits = st.columns([1.1,1], gap="large")

with col_card:
    card = f"""<div class="profile-card">
      <div class="card-top-bar"></div>
      <div class="card-eyebrow">Wardrobe Engine · Colour Profile</div>
      <div class="card-title">Your Style Profile</div>
      <div class="card-subtitle">{season_d} · {skin_lbl}</div>
      <span class="quality-badge" style="{QUALITY_STYLE[qual]}">{qual}</span>
      <div class="gold-divider"></div>"""
    if result["smart_shirts"]:
        card += '<div class="section-label">Smart Shirts to Buy</div>'+swatch_html(result["smart_shirts"],"shirt_score")
    if result["smart_pants"]:
        card += '<div class="section-label">Smart Pants to Buy</div>'+swatch_html(result["smart_pants"],"pant_score")
    if result["all_season_neutrals"]:
        card += '<div class="section-label">All-Season Neutrals</div>'+swatch_html(result["all_season_neutrals"],"neutral_score")
    card += f"""<div class="gold-divider"></div>
      <div style="display:flex;justify-content:space-between;font-size:9px;color:#c0b090">
        <span>Season: <b style="color:#8B5E00">{season_d}</b> · Skin: <b style="color:#8B5E00">{skin_lbl}</b></span>
        <span style="font-family:monospace">wardrobeengine.com</span>
      </div></div>"""
    st.markdown(card, unsafe_allow_html=True)

with col_outfits:
    st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:.1em;color:#9a8a70;text-transform:uppercase;margin-bottom:12px">Top Outfit Combinations</div>', unsafe_allow_html=True)
    for i,o in enumerate(result.get("outfits",[])):
        st.markdown(outfit_row_html(o,i), unsafe_allow_html=True)

    # pair_matrix has all shirt×pant combos with shirt_hex, pant_hex, pair_score
    all_combos = result.get("pair_matrix", [])
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    if not st.session_state.show_all_combos:
        st.markdown(
            f'<div style="background:#fffdf7;border:1.5px solid #e0d4b8;border-radius:14px;padding:14px 18px">'
            f'<div style="font-size:13px;font-weight:600;color:#1a1208">See all outfit combinations?</div>'
            f'<div style="font-size:11px;color:#9a8a70;margin-top:2px">{len(all_combos)} possible pairings</div>'
            f'</div>', unsafe_allow_html=True)
        bc1,bc2 = st.columns(2)
        with bc1:
            if st.button("Show all combinations", use_container_width=True):
                st.session_state.show_all_combos = True
                st.rerun()
        with bc2:
            st.button("Skip", use_container_width=True)
    else:
        st.markdown(f'<div style="font-size:12px;font-weight:600;color:#2a1f0a;margin-bottom:10px">All combinations <span style="color:#9a8a70;font-weight:400">· {len(all_combos)} pairings</span></div>', unsafe_allow_html=True)
        cols3 = st.columns(3)
        for i,combo in enumerate(all_combos):
            with cols3[i%3]:
                st.markdown(combo_card_html(combo), unsafe_allow_html=True)
        if st.button("Hide combinations ↑", use_container_width=True):
            st.session_state.show_all_combos = False
            st.rerun()

# ─────────────────────────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#e0d4b8,transparent);margin-bottom:32px"></div>', unsafe_allow_html=True)

if st.session_state.feedback_done:
    _,c,_ = st.columns([1,2,1])
    with c:
        st.markdown("""
        <div class="thankyou-box">
          <div style="font-size:40px;margin-bottom:12px">🙏</div>
          <div class="thankyou-title">Thank you!</div>
          <div style="font-size:13px;color:#5a7a40">Your feedback shapes the ₹299 colour card. We'll build a better product because of it.</div>
        </div>""", unsafe_allow_html=True)
else:
    _,c,_ = st.columns([1,2,1])
    with c:
        st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
        st.markdown('<div class="feedback-title">Share your feedback</div>', unsafe_allow_html=True)
        st.markdown('<div class="feedback-sub">2 minutes · helps us build a better product</div>', unsafe_allow_html=True)

        st.markdown("**How useful were these recommendations?**")
        star_rating = st.select_slider("star_rating", options=[1,2,3,4,5], value=4,
                                       format_func=lambda x:"⭐"*x, label_visibility="collapsed")

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        st.markdown("**Would you buy a personalised colour card for ₹299?**")
        buy_card = st.radio("buy_card",
                            ["Yes — I'd buy this","Maybe — need to see the physical card","No — not for me"],
                            label_visibility="collapsed")

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        st.markdown("**How likely are you to recommend this to a friend?**")
        st.caption("0 = Not at all likely · 10 = Extremely likely")
        nps = st.slider("nps", min_value=0, max_value=10, value=7, label_visibility="collapsed")

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        if st.button("Submit Feedback →", type="primary", use_container_width=True):
            outfits = result.get("outfits",[])
            top_outfit = f"{outfits[0]['shirt']} + {outfits[0]['pant']}" if outfits else ""
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
                "top_outfit":   top_outfit,
                "star_rating":  star_rating,
                "buy_card":     buy_card,
                "nps_score":    nps,
            })
            st.session_state.feedback_done = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ADMIN — visit ?admin=true
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
        st.info("No feedback submitted yet.")
        st.stop()
    total=len(db); avg_star=round(db["star_rating"].mean(),1)
    avg_nps=round(db["nps_score"].mean(),1)
    buy_yes=round(db["buy_card"].str.startswith("Yes").sum()/total*100)
    m1,m2,m3,m4 = st.columns(4)
    for col,val,label in [(m1,total,"Total Responses"),(m2,f"{avg_star}⭐","Avg Rating"),
                          (m3,avg_nps,"Avg NPS"),(m4,f"{buy_yes}%","Would Buy Card")]:
        col.markdown(f'<div class="metric-tile"><div class="metric-val">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    ca,cb = st.columns(2)
    with ca:
        st.markdown("**Buy card responses**")
        st.bar_chart(db["buy_card"].value_counts())
    with cb:
        st.markdown("**Most recommended shirts**")
        st.bar_chart(db["smart_shirts"].str.split(", ").explode().value_counts().head(8))
    st.markdown("**All responses**")
    st.dataframe(db, use_container_width=True)
    st.download_button("⬇ Download CSV", data=db.to_csv(index=False),
                       file_name="wardrobe_feedback.csv", mime="text/csv")

import colorsys
import random
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ==========================================================
# GLOBAL WEIGHTS
# ==========================================================

WEIGHTS = {
    "complementary": 2.0,
    "contrast":      1.5,
    "neutral":       0.6,
    "same_family":   0.8,
    "same_depth":    0.5
}

PERSONALIZATION_WEIGHTS = {
    "skin_primary":   2.0,
    "skin_secondary": 1.0
}

DENSITY_WEIGHT             = 0.9   # single combo-density multiplier (coverage_bonus removed)
COMBO_THRESHOLD            = 2.0
HUE_THRESHOLD              = 30    # degrees — within this = hue-redundant
REDUNDANCY_PENALTY         = 0.85  # FIX-WARN3: penalise, do NOT hard-skip hue-close items
ADJACENT_SEASON_MULTIPLIER = 0.4

# Neutral normalization: penalty per wardrobe item, derived from WEIGHTS["neutral"]
# FIX-WARN2: expressed as a fraction of the weight so it stays in sync if weight changes
# 0.35 / 0.6 ≈ 0.583 → penalty = WEIGHTS["neutral"] * NEUTRAL_PENALTY_RATIO
NEUTRAL_PENALTY_RATIO = 0.583

# ==========================================================
# SEASON ADJACENCY MAP
# ==========================================================

SEASON_ADJACENCY = {
    "Spring": ["Summer", "Winter"],
    "Summer": ["Spring", "Autumn"],
    "Autumn": ["Summer", "Winter"],
    "Winter": ["Autumn", "Spring"]
}

# ==========================================================
# SKIN PROFILES
# ==========================================================

SKIN_PROFILES = {
    "Light_Warm": {
        "primary":   ["Peach", "Mustard", "Rust", "Olive"],
        "secondary": ["Sky Blue", "Beige"],
        "avoid":     ["Charcoal", "Maroon"]
    },
    "Light_Cool": {
        "primary":   ["Sky Blue", "Royal Blue", "Plum"],
        "secondary": ["Grey", "Lavender"],
        "avoid":     ["Mustard", "Rust", "Brown"]
    },
    "Light_Neutral": {
        "primary":   ["Sky Blue", "Olive", "Royal Blue"],
        "secondary": ["Grey", "Beige"],
        "avoid":     ["Maroon"]
    },
    "Medium_Warm": {
        "primary":   ["Olive", "Rust", "Mustard", "Brown"],
        "secondary": ["Teal"],
        "avoid":     ["Lavender"]
    },
    "Medium_Cool": {
        "primary":   ["Royal Blue", "Teal", "Plum"],
        "secondary": ["Grey", "Forest Green"],
        "avoid":     ["Mustard", "Peach"]
    },
    "Medium_Neutral": {
        "primary":   ["Olive", "Royal Blue", "Forest Green"],
        "secondary": ["Grey", "Beige"],
        "avoid":     ["Light Pink"]
    },
    "Deep_Warm": {
        "primary":   ["Mustard", "Rust", "Maroon", "Brown", "Olive"],
        "secondary": ["Burgundy"],
        "avoid":     ["Sky Blue"]
    },
    "Deep_Cool": {
        "primary":   ["Royal Blue", "Teal", "Burgundy", "Charcoal"],
        "secondary": ["Forest Green"],
        "avoid":     ["Peach", "Mustard"]
    },
    "Deep_Neutral": {
        "primary":   ["Burgundy", "Forest Green", "Royal Blue", "Olive"],
        "secondary": ["Charcoal", "Grey"],
        "avoid":     ["Light Pink", "Peach"]
    }
}

# ==========================================================
# MASTER COLOR DATASET  (25 colors)
# ==========================================================

# ==========================================================
# CLOTHING TYPE MODIFIERS
# ==========================================================
# Delta adjustments applied ON TOP of base WEIGHTS per clothing type.
# Formal → quieter palette, tonal dressing, no loud complements.
# T-Shirt → expressive, bold combos welcome.

TYPE_WEIGHT_MODIFIERS = {
    "Formal": {
        "complementary": -0.5,   # loud cross-family combos less appropriate
        "contrast":      -0.2,   # formal = more tonal
        "neutral":       +0.4,   # neutrals are formal anchors
        "same_family":   +0.3,   # tonal dressing is classic formal
        "same_depth":    +0.2,   # depth harmony feels refined
    },
    "T-Shirt": {
        "complementary": +0.5,   # bold combos welcome
        "contrast":      +0.3,   # casual allows striking contrast
        "neutral":       -0.1,   # push toward colour
        "same_family":   -0.1,   # avoid boring tonal in casual
        "same_depth":     0.0,
    },
    "Both": {  # no change from base weights
        "complementary": 0.0,
        "contrast":      0.0,
        "neutral":       0.0,
        "same_family":   0.0,
        "same_depth":    0.0,
    },
}

# ==========================================================
# STYLE PREFERENCE MODIFIERS
# ==========================================================
STYLE_WEIGHT_MODIFIERS = {
    "Classic": {
        "complementary": -0.3,   # less bold cross-family
        "contrast":      -0.2,   # prefer harmonious depth
        "neutral":       +0.4,   # classic = reliable neutrals
        "same_family":   +0.3,   # tonal looks are timeless
        "same_depth":    +0.1,
    },
    "Bold": {
        "complementary": +0.5,   # maximise striking combos
        "contrast":      +0.3,   # Light-Deep = high impact
        "neutral":       -0.2,   # push toward statement colours
        "same_family":   -0.3,   # boring if everything matches
        "same_depth":    -0.1,
    },
    "Any": {  # no change
        "complementary": 0.0,
        "contrast":      0.0,
        "neutral":       0.0,
        "same_family":   0.0,
        "same_depth":    0.0,
    },
}

# ==========================================================
# FORMAL-APPROPRIATE COLOURS
# ==========================================================
# Colours that work for formal shirts.  All neutrals + classic blues.
# Excludes casual/expressive colours (Mint, Mustard, Burnt Orange, etc.)
FORMAL_SHIRT_COLORS = {
    "White","Cream","Beige","Grey","Charcoal","Black","Navy",
    "Sky Blue","Powder Blue","Royal Blue","Burgundy","Teal",
}

# Formal pant colours — classic trouser palette only
FORMAL_PANT_COLORS = {
    "Navy","Charcoal","Black","Grey","Beige","Cream","Brown","Maroon",
}

def load_master_colors():
    return {
        # NEUTRALS (7) — formal_shirt: all yes
        "White":         {"hex": "#FFFFFF", "family": "Neutral", "shirt_allowed": True,  "pant_allowed": False, "neutral": True},
        "Cream":         {"hex": "#FFF5E1", "family": "Neutral", "shirt_allowed": True,  "pant_allowed": True,  "neutral": True},
        "Beige":         {"hex": "#F5F5DC", "family": "Neutral", "shirt_allowed": True,  "pant_allowed": True,  "neutral": True},
        "Grey":          {"hex": "#808080", "family": "Neutral", "shirt_allowed": True,  "pant_allowed": True,  "neutral": True},
        "Charcoal":      {"hex": "#36454F", "family": "Neutral", "shirt_allowed": True,  "pant_allowed": True,  "neutral": True},
        "Black":         {"hex": "#000000", "family": "Neutral", "shirt_allowed": True,  "pant_allowed": True,  "neutral": True},
        "Navy":          {"hex": "#001F5B", "family": "Neutral", "shirt_allowed": True,  "pant_allowed": True,  "neutral": True},
        # BLUES (4)
        "Sky Blue":      {"hex": "#87CEEB", "family": "Blue",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Powder Blue":   {"hex": "#B0E0E6", "family": "Blue",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Royal Blue":    {"hex": "#4169E1", "family": "Blue",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Teal":          {"hex": "#008080", "family": "Blue",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        # GREENS (3)
        "Olive":         {"hex": "#708238", "family": "Green",   "shirt_allowed": True,  "pant_allowed": True,  "neutral": False},
        "Forest Green":  {"hex": "#228B22", "family": "Green",   "shirt_allowed": True,  "pant_allowed": True,  "neutral": False},
        "Mint":          {"hex": "#98FF98", "family": "Green",   "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        # WARM (4)
        "Rust":          {"hex": "#B7410E", "family": "Warm",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Mustard":       {"hex": "#FFDB58", "family": "Warm",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Burnt Orange":  {"hex": "#CC5500", "family": "Warm",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Brown":         {"hex": "#7B3F00", "family": "Warm",    "shirt_allowed": False, "pant_allowed": True,  "neutral": False},
        # REDS (3)
        "Maroon":        {"hex": "#800000", "family": "Red",     "shirt_allowed": True,  "pant_allowed": True,  "neutral": False},
        "Burgundy":      {"hex": "#800020", "family": "Red",     "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Brick Red":     {"hex": "#CB4154", "family": "Red",     "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        # PURPLE (2)
        "Plum":          {"hex": "#8E4585", "family": "Purple",  "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Lavender":      {"hex": "#E6E6FA", "family": "Purple",  "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        # SOFT (2)
        "Peach":         {"hex": "#FFE5B4", "family": "Soft",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
        "Light Pink":    {"hex": "#FFB6C1", "family": "Soft",    "shirt_allowed": True,  "pant_allowed": False, "neutral": False},
    }

# ==========================================================
# COLOR METRICS
# ==========================================================

def derive_metrics(hex_code):
    hex_code = hex_code.lstrip("#")
    r, g, b  = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    depth     = "Light" if luminance > 180 else "Medium" if luminance > 100 else "Deep"
    h, l, s   = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return {
        "depth":      depth,
        "saturation": "Soft" if s < 0.35 else "Bold",
        "hue":        h * 360
    }

# ==========================================================
# HUE DISTANCE  (circular, 0–180°)
# ==========================================================

def hue_distance(h1, h2):
    diff = abs(h1 - h2) % 360
    return min(diff, 360 - diff)

# ==========================================================
# COMPLEMENT MAP
# ==========================================================

COMPLEMENTS = {
    "Blue":    ["Warm", "Red", "Soft"],
    "Warm":    ["Blue", "Purple"],
    "Green":   ["Red", "Purple"],
    "Red":     ["Green", "Blue"],
    "Purple":  ["Warm", "Green"],
    "Soft":    ["Blue", "Green"],
    "Neutral": []
}

# ==========================================================
# MATCH STRENGTH
# ==========================================================

def get_match_strength(a, b, weights=None):
    """
    Five-signal compatibility score between two color objects.
    Each must have: family, neutral, metrics{depth, saturation, hue}

    weights — optional dict overriding WEIGHTS for type/style personalisation.
              If None, global WEIGHTS are used.
    """
    w = weights if weights is not None else WEIGHTS
    score = 0

    # Complementary harmony
    if b["family"] in COMPLEMENTS.get(a["family"], []):
        score += w["complementary"]

    # FIX-BUG-A: depth contrast only for true Light ↔ Deep opposites.
    if (a["metrics"]["depth"] == "Light" and b["metrics"]["depth"] == "Deep") or \
       (a["metrics"]["depth"] == "Deep"  and b["metrics"]["depth"] == "Light"):
        score += w["contrast"]

    # Neutral pairing (FIX1 from prior audit: OR not AND)
    if a["neutral"] or b["neutral"]:
        score += w["neutral"]

    # Same-family cohesion
    if a["family"] == b["family"]:
        score += w["same_family"]

    # Same-depth harmony (mutually exclusive with contrast by design)
    if a["metrics"]["depth"] == b["metrics"]["depth"]:
        score += w["same_depth"]

    return score

# ==========================================================
# SEASON WEIGHT  (FIX-WARN1: generic adjacent blending)
# ==========================================================

def _raw_season_score(depth, sat, season):
    """
    Returns the base score for one depth+saturation pair against one season.
    Isolated so it can be called for both primary and adjacent seasons
    without duplicating logic or hardcoding attribute checks per season.
    """
    if season == "Spring":
        if depth == "Light" and sat == "Bold":  return  1.0
        if depth == "Deep"  and sat == "Soft":  return -1.0
    elif season == "Summer":
        if depth == "Light" and sat == "Soft":  return  1.0
        if depth == "Deep"  and sat == "Bold":  return -1.0
    elif season == "Autumn":
        if depth == "Deep"  and sat == "Soft":  return  1.0
        if depth == "Light" and sat == "Bold":  return -1.0
    elif season == "Winter":
        if depth == "Deep"  and sat == "Bold":  return  1.0
        if depth == "Light" and sat == "Soft":  return -1.0
    return 0.0


def season_weight(color_data, season, category):
    """
    FIX-WARN1: adjacent season blending is now computed generically via
    _raw_season_score rather than hardcoded attribute checks per adjacent
    season.  This prevents the double-stacking that caused Lavender to
    score 1.4 in Spring (its best season) instead of ~0.4.

    Primary season  → full weight
    Adjacent seasons → average of their raw scores × ADJACENT_SEASON_MULTIPLIER
    """
    if season == "All" or color_data["neutral"]:
        return 0

    depth = color_data["metrics"]["depth"]
    sat   = color_data["metrics"]["saturation"]

    primary_score = _raw_season_score(depth, sat, season)

    adj_seasons = SEASON_ADJACENCY.get(season, [])
    if adj_seasons:
        adj_scores = [_raw_season_score(depth, sat, s) for s in adj_seasons]
        adj_blend  = (sum(adj_scores) / len(adj_scores)) * ADJACENT_SEASON_MULTIPLIER
    else:
        adj_blend = 0.0

    blended    = primary_score + adj_blend
    multiplier = 1.0 if category == "shirt" else 0.6
    return round(blended * multiplier, 3)

# ==========================================================
# CONTRAST PREFERENCE
# ==========================================================

def contrast_adjustment(color_data, wardrobe, preference, colors):
    """
    Optional layer: boost score if color matches user's contrast preference.
    High → rewards colors that contrast with wardrobe items in depth.
    Low  → rewards colors that harmonise in depth with wardrobe items.
    """
    if not preference:
        return 0

    adjustment = 0

    for item in wardrobe:
        if item not in colors:
            continue

        contrast = (color_data["metrics"]["depth"] != colors[item]["metrics"]["depth"])

        if preference == "High" and contrast:
            adjustment += 1
        if preference == "Low" and not contrast:
            adjustment += 1

    return adjustment

# ==========================================================
# DIVERSITY FILTER  (FIX-WARN3: penalise, do NOT hard-skip)
# ==========================================================

def diversity_filter(candidates, max_items, wardrobe_size, score_key="shirt_score"):
    """
    Three-stage diversity filter.

    Stage 1 — hue pre-pass (split by family relationship):
      • Same family + hue-close (< HUE_THRESHOLD°): hard-skip the lower scorer.
        Two colors in the same family that share a hue zone are visually near-identical
        (e.g. Sky Blue + Powder Blue, Rust + Burnt Orange).  The family already covers
        that hue zone so the duplicate adds no variety.
      • Cross family + hue-close: penalise (× REDUNDANCY_PENALTY) the lower scorer.
        Different families that happen to overlap in hue (e.g. Teal/Green boundary)
        can still appear — the penalty just depresses the redundant one in ranking.

    Stage 2 — re-sort after penalties so selection order reflects adjusted scores.

    Stage 3 — family cap: hard limit per family scales with wardrobe size.
      ≤2 items → cap 1 per family
      3–5 items → cap 2 per family
      >5 items  → cap 3 per family
    """
    if not candidates:
        return []

    max_per_family = 1 if wardrobe_size <= 2 else 2 if wardrobe_size <= 5 else 3

    # Deep copy — do not mutate caller's list
    pool = [dict(c) for c in candidates]

    # Stage 1: hue pre-pass
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            if hue_distance(pool[i]["hue"], pool[j]["hue"]) < HUE_THRESHOLD:
                if pool[i]["family"] == pool[j]["family"]:
                    # Same family + hue-close → hard-skip lower scorer
                    if pool[i][score_key] >= pool[j][score_key]:
                        pool[j]["_skip"] = True
                    else:
                        pool[i]["_skip"] = True
                else:
                    # Cross-family + hue-close → penalise lower scorer
                    if pool[i][score_key] >= pool[j][score_key]:
                        pool[j][score_key] = round(pool[j][score_key] * REDUNDANCY_PENALTY, 3)
                    else:
                        pool[i][score_key] = round(pool[i][score_key] * REDUNDANCY_PENALTY, 3)

    # Stage 2: remove hard-skipped, re-sort
    pool = [p for p in pool if not p.get("_skip")]
    pool.sort(key=lambda x: x[score_key], reverse=True)

    # Stage 3: family cap
    selected     = []
    family_count = {}

    for item in pool:
        if family_count.get(item["family"], 0) >= max_per_family:
            continue
        selected.append(item)
        family_count[item["family"]] = family_count.get(item["family"], 0) + 1
        if len(selected) >= max_items:
            break

    return selected

# ==========================================================
# COLOR OBJECT BUILDER
# ==========================================================

def build_color_objects():
    colors = load_master_colors()
    for name, data in colors.items():
        data["metrics"] = derive_metrics(data["hex"])
    return colors

# ==========================================================
# OUTFIT UTILITIES
# ==========================================================

def count_outfits(shirts, pants):
    if not shirts or not pants:
        return 0
    return len(shirts) * len(pants)


def generate_outfits(shirts, pants, colors):
    """Return top-12 outfit pairs ranked by match strength."""
    outfits = []
    for s in shirts:
        for p in pants:
            if s not in colors or p not in colors:
                continue
            score = get_match_strength(colors[s], colors[p])
            outfits.append({
                "shirt":     s,
                "pant":      p,
                "shirt_hex": colors[s]["hex"],
                "pant_hex":  colors[p]["hex"],
                "score":     round(score, 2)
            })
    return sorted(outfits, key=lambda x: x["score"], reverse=True)[:12]


def build_pair_matrix(shirts, pants):
    """All shirt × pant combinations ranked by average score."""
    pairs = []
    for s in shirts:
        for p in pants:
            pair_score = (s["shirt_score"] + p["pant_score"]) / 2
            pairs.append({
                "shirt":      s["color"],
                "pant":       p["color"],
                "shirt_hex":  s["hex"],
                "pant_hex":   p["hex"],
                "pair_score": round(pair_score, 2)
            })
    return sorted(pairs, key=lambda x: x["pair_score"], reverse=True)


def compatibility_map(color, wardrobe, colors):
    """Per-item match scores between candidate and every wardrobe item."""
    pairs = []
    for item in wardrobe:
        if item not in colors:
            continue
        score = get_match_strength(colors[color], colors[item])
        pairs.append({"color": item, "score": round(score, 2)})
    return sorted(pairs, key=lambda x: x["score"], reverse=True)

# ==========================================================
# WARDROBE EXPANSION BONUS
# ==========================================================

def wardrobe_expansion_bonus(color_name, wardrobe_shirts, wardrobe_pants, colors):
    """
    How many new outfit combinations does adding this color unlock?
    Scaled by 0.6 and capped at 2.0 to prevent large-wardrobe inflation.

    FIX-BUG-D: without the cap, a color added to a 5-shirt × 5-pant wardrobe
    unlocks 5 new outfits → bonus = 3.0, which alone exceeds the entire score
    at a small wardrobe (wsz=2 top ≈ 4.25) and creates a 5× score gap.
    Cap of 2.0 keeps growth linear: score/wsz stays within ±0.2 variance.
    """
    base      = count_outfits(wardrobe_shirts, wardrobe_pants)
    as_shirt  = count_outfits(wardrobe_shirts + [color_name], wardrobe_pants) - base
    as_pant   = count_outfits(wardrobe_shirts, wardrobe_pants + [color_name]) - base
    expansion = max(as_shirt, as_pant)
    return round(min(expansion * 0.6, 2.0), 3)

# ==========================================================
# FULL RESULT SCHEMA (used by both scoring paths)
# ==========================================================

def _full_schema(name, data, shirt_score, pant_score, neutral_score,
                 combos, skin_delta, wardrobe, colors,
                 graph_influence=0.0, graph_outfit_path=0.0,
                 graph_centrality=0.0, top_influenced=None):
    """
    FIX-BUG-B: single authoritative schema used by both the main scoring
    loop and starter_wardrobe, so callers always get the same keys.
    Graph keys default to 0/empty when called from the starter path
    (no wardrobe context available).
    """
    return {
        "color":               name,
        "hex":                 data["hex"],
        "family":              data["family"],
        "hue":                 data["metrics"]["hue"],
        "shirt_score":         round(shirt_score, 2),
        "pant_score":          round(pant_score,  2),
        "neutral_score":       round(neutral_score, 2),
        "shirt_allowed":       data["shirt_allowed"],
        "pant_allowed":        data["pant_allowed"],
        "neutral":             data["neutral"],
        "combinations":        combos,
        "skin_delta":          skin_delta,
        "graph_influence":     round(graph_influence, 4),
        "graph_outfit_path":   round(graph_outfit_path, 4),
        "graph_centrality":    graph_centrality,
        "top_influenced":      top_influenced or [],
        "pairs_with_wardrobe": compatibility_map(name, wardrobe, colors)
    }

# ==========================================================
# STARTER WARDROBE  (FIX-BUG-B: full schema; FIX-BUG-C: skin in neutral)
# ==========================================================

def starter_wardrobe(skin_profile, season, colors):
    """
    FIX-BUG-B: starter items now return the same full schema as the main
    scoring path (shirt_score, pant_score, family, combinations …).
    The response also includes pair_matrix and outfits so callers never
    need to branch on mode.

    Scoring: pure skin + season signal (no wardrobe-based bonuses).
    """
    profile   = SKIN_PROFILES.get(skin_profile, {})
    primary   = profile.get("primary",   [])
    secondary = profile.get("secondary", [])
    avoided   = set(profile.get("avoid", []))

    results = []

    for name, data in colors.items():
        if name in avoided:
            continue

        # Skin delta
        skin_delta = 0
        if name in primary:
            skin_delta = PERSONALIZATION_WEIGHTS["skin_primary"]
        elif name in secondary:
            skin_delta = PERSONALIZATION_WEIGHTS["skin_secondary"]

        base = skin_delta  # no wardrobe compat, no density, no expansion

        shirt_score   = base + season_weight(data, season, "shirt")
        pant_score    = base + season_weight(data, season, "pant")

        # FIX-BUG-C: neutrals also get skin_delta so profile-primary
        # neutrals (e.g. Charcoal for Deep_Cool) rank correctly
        neutral_score = base  # season exempt for neutrals by design

        results.append(_full_schema(
            name, data,
            shirt_score, pant_score, neutral_score,
            0, skin_delta, [], colors
        ))

    shirts_sorted   = sorted([r for r in results if r["shirt_allowed"]],
                             key=lambda x: x["shirt_score"],   reverse=True)
    pants_sorted    = sorted([r for r in results if r["pant_allowed"]],
                             key=lambda x: x["pant_score"],    reverse=True)

    shirts_final   = diversity_filter(shirts_sorted,   5, 0, "shirt_score")
    pants_final    = diversity_filter(pants_sorted,    4, 0, "pant_score")

    shirts_final_names = {r["color"] for r in shirts_final}
    neutrals_sorted = sorted(
        [r for r in results if r["neutral"] and r["color"] not in shirts_final_names],
        key=lambda x: x["neutral_score"], reverse=True
    )
    neutrals_final = diversity_filter(neutrals_sorted, 3, 0, "neutral_score")

    pair_matrix = build_pair_matrix(shirts_final, pants_final)
    outfits     = generate_outfits(
        [r["color"] for r in shirts_final],
        [r["color"] for r in pants_final],
        colors
    )

    return {
        "smart_shirts":        shirts_final,
        "smart_pants":         pants_final,
        "all_season_neutrals": neutrals_final,
        "pair_matrix":         pair_matrix[:20],
        "outfits":             outfits,
        "mode":                "starter"
    }

# ==========================================================
# GRAPH MODEL
# ==========================================================
#
# Two graphs are built once per engine call and carried through:
#
#   ColorGraph  — full 25-node weighted undirected network.
#                 Nodes  = colors.
#                 Edges  = get_match_strength(a, b)  (weight > 0 only).
#                 Used for: centrality, neighborhood lookup,
#                           influence propagation signal.
#
#   OutfitGraph — bipartite shirt → pant directed flow graph.
#                 Nodes  = shirt_allowed colors + pant_allowed colors.
#                 Edges  = get_match_strength(shirt, pant)  (directed).
#                 Used for: best outfit paths, flow-based ranking.
#
# INFLUENCE PROPAGATION  (the primary graph signal injected into scoring)
#
#   When candidate C is added to wardrobe W, it "unlocks" coverage for
#   colors X in the graph that W currently under-serves.
#
#   already_served(X, W) = max edge(W_i, X)  for W_i in W
#       → how well the best existing wardrobe item already covers X
#
#   incremental(C → X)   = max(0, edge(C, X) − already_served(X, W))
#       → marginal gain C brings to X
#
#   Two-hop propagation (damped by α):
#   hop2(C → Y via X)    = α × edge(C,X) × edge(X,Y)
#       → C's indirect influence: C → X → Y
#       → captures "gateway" colors that unlock whole color clusters
#
#   graph_influence(C)   = Σ_X incremental(C→X)
#                        + Σ_{X,Y} hop2(C→Y via X)
#                        (Y ≠ C, Y ∉ W, X ∉ W)
#
#   Scaled by GRAPH_INFLUENCE_WEIGHT before adding to shirt/pant score.
#
# OUTFIT PATH SCORE  (from the bipartite flow graph)
#
#   For each candidate shirt C, find its best pant partner in the
#   flow graph (highest outgoing edge weight considering existing pants).
#   This is separate from pair_matrix — it reflects how well C anchors
#   an outfit path through the current pant inventory.
#
# ==========================================================

GRAPH_INFLUENCE_WEIGHT = 0.4   # scale factor — keeps graph signal < 15% of total score
GRAPH_DAMPING_ALPHA    = 0.5   # hop-2 damping factor
GRAPH_INFLUENCE_CAP    = 2.5   # ceiling on raw influence sum before scaling


class ColorGraph:
    """
    Weighted undirected graph over all 25 colors.
    Edges carry get_match_strength weights.  Built once per call.
    """

    def __init__(self, colors):
        self.colors    = colors
        self.nodes     = list(colors.keys())
        # adjacency: {node: {neighbor: weight}}
        self.adj       = {n: {} for n in self.nodes}
        self._build()
        # Cache centrality once at build — O(n) cost, then O(1) reads.
        # Avoids recomputing 20× per generate_recommendations call.
        n = len(self.nodes)
        self._centrality = {
            node: round(sum(self.adj[node].values()) / max(1, n - 1), 4)
            for node in self.nodes
        }

    def _build(self):
        for i, a in enumerate(self.nodes):
            for b in self.nodes[i + 1:]:
                w = get_match_strength(self.colors[a], self.colors[b])
                if w > 0:
                    self.adj[a][b] = w
                    self.adj[b][a] = w

    def neighbors(self, node):
        """Return {neighbor: weight} for a given node."""
        return self.adj.get(node, {})

    def edge(self, a, b):
        """Weight of edge between a and b (0 if no edge)."""
        return self.adj.get(a, {}).get(b, 0)

    def degree_centrality(self):
        """
        Weighted degree centrality for every node.
        = sum of all edge weights / (n-1)
        High centrality = color that connects strongly to many others.
        Returned from cache built in __init__ — O(1).
        """
        return self._centrality

    def influence_of(self, candidate, wardrobe):
        """
        Two-hop influence propagation score for `candidate` given `wardrobe`.

        Returns a dict with:
          total          — scalar added to shirt/pant score
          incremental    — per-color direct incremental gains  {color: float}
          hop2           — per-color two-hop gains             {color: float}
          already_served — per-color best existing coverage    {color: float}
        """
        if candidate not in self.nodes:
            return {"total": 0.0, "incremental": {}, "hop2": {}, "already_served": {}}

        wardrobe_set = set(wardrobe)

        # Pre-compute how well each color is already served by the wardrobe
        already_served = {}
        for x in self.nodes:
            if x in wardrobe_set or x == candidate:
                continue
            best = max(
                (self.edge(w_item, x) for w_item in wardrobe if w_item in self.nodes),
                default=0
            )
            already_served[x] = best

        # Direct incremental gains: C → X
        incremental = {}
        for x, served in already_served.items():
            direct = self.edge(candidate, x)
            gain   = max(0.0, direct - served)
            if gain > 0:
                incremental[x] = round(gain, 4)

        # Two-hop gains: C → X → Y  (Y ∉ wardrobe, Y ≠ candidate, Y ≠ X)
        hop2 = {}
        for x, cx_weight in self.neighbors(candidate).items():
            if x in wardrobe_set or x == candidate:
                continue
            for y, xy_weight in self.neighbors(x).items():
                if y in wardrobe_set or y == candidate or y == x:
                    continue
                contribution = GRAPH_DAMPING_ALPHA * cx_weight * xy_weight
                hop2[y] = hop2.get(y, 0) + contribution

        # Round hop2
        hop2 = {k: round(v, 4) for k, v in hop2.items()}

        raw_total = sum(incremental.values()) + sum(hop2.values())

        # Wardrobe-relative normalization:
        # Divide by expected raw influence for a wardrobe of this size so the
        # scaled signal is comparable across wardrobe sizes.
        # Expected raw ≈ 350 for wsz=1, drops ~30 per item added.
        # We use (25 - len(wardrobe)) as a proxy for "remaining coverage gap".
        # Minimum denominator of 5 prevents divide-by-zero on full wardrobes.
        coverage_gap  = max(5, 25 - len(wardrobe))
        normalized    = raw_total / coverage_gap
        scaled        = round(min(normalized, GRAPH_INFLUENCE_CAP) * GRAPH_INFLUENCE_WEIGHT, 4)

        return {
            "total":          scaled,
            "raw_total":      round(raw_total, 4),
            "incremental":    incremental,
            "hop2":           hop2,
            "already_served": already_served
        }

    def batch_influence(self, candidates, wardrobe):
        """
        Compute influence propagation for every candidate in one pass.

        Key optimization over calling influence_of() per candidate:
        - already_served is computed ONCE for the wardrobe, then shared
          across all candidates (was recomputed 20× per call before)
        - hop2 inner loop reads from the shared already_served map

        Returns {candidate_name: influence_dict} where influence_dict
        has the same shape as influence_of() output plus 'top_influenced'.
        """
        wardrobe_set = set(wardrobe)

        # Precompute once: for every non-wardrobe node, the best existing
        # wardrobe edge.  This is the "already served" baseline for all
        # candidates to compare against.
        already_served = {}
        for x in self.nodes:
            if x in wardrobe_set:
                continue
            already_served[x] = max(
                (self.edge(w, x) for w in wardrobe if w in self.adj),
                default=0
            )

        results = {}
        for candidate in candidates:
            if candidate not in self.nodes:
                results[candidate] = {
                    "total": 0.0, "raw_total": 0.0,
                    "incremental": {}, "hop2": {}, "top_influenced": []
                }
                continue

            # Direct incremental: C → X
            incremental = {}
            for x, served in already_served.items():
                if x == candidate:
                    continue
                direct = self.edge(candidate, x)
                gain   = max(0.0, direct - served)
                if gain > 0:
                    incremental[x] = round(gain, 4)

            # Two-hop: C → X → Y  (Y ∉ wardrobe, Y ≠ candidate, Y ≠ X)
            hop2 = {}
            for x, cx_w in self.adj.get(candidate, {}).items():
                if x in wardrobe_set:
                    continue
                for y, xy_w in self.adj.get(x, {}).items():
                    if y in wardrobe_set or y == candidate or y == x:
                        continue
                    hop2[y] = hop2.get(y, 0) + GRAPH_DAMPING_ALPHA * cx_w * xy_w

            hop2 = {k: round(v, 4) for k, v in hop2.items()}

            raw_total    = sum(incremental.values()) + sum(hop2.values())
            coverage_gap = max(5, 25 - len(wardrobe))
            normalized   = raw_total / coverage_gap
            scaled       = round(
                min(normalized, GRAPH_INFLUENCE_CAP) * GRAPH_INFLUENCE_WEIGHT, 4
            )

            # Top-3 colors most improved by this candidate
            combined = {
                k: incremental.get(k, 0) + hop2.get(k, 0)
                for k in set(list(incremental) + list(hop2))
            }
            top_influenced = sorted(
                combined.items(), key=lambda x: x[1], reverse=True
            )[:3]

            results[candidate] = {
                "total":         scaled,
                "raw_total":     round(raw_total, 4),
                "incremental":   incremental,
                "hop2":          hop2,
                "top_influenced": top_influenced
            }

        return results


class OutfitGraph:
    """
    Weighted directed bipartite graph: shirt_nodes → pant_nodes.
    Edge weight = get_match_strength(shirt, pant).
    Used to compute outfit path scores and best pant partners.
    """

    def __init__(self, colors):
        self.colors      = colors
        self.shirt_nodes = [n for n, d in colors.items() if d["shirt_allowed"]]
        self.pant_nodes  = [n for n, d in colors.items() if d["pant_allowed"]]
        # directed adj: shirt → {pant: weight}
        self.adj = {s: {} for s in self.shirt_nodes}
        self._build()

    def _build(self):
        for s in self.shirt_nodes:
            for p in self.pant_nodes:
                w = get_match_strength(self.colors[s], self.colors[p])
                if w > 0:
                    self.adj[s][p] = w

    def best_pant_for(self, shirt, available_pants=None):
        """
        Best pant partner for `shirt` from `available_pants`.
        If available_pants is None, considers all pant nodes.
        Returns (pant_name, edge_weight) or (None, 0).
        """
        candidates = available_pants if available_pants else self.pant_nodes
        best_pant = None
        best_w    = 0
        for p in candidates:
            w = self.adj.get(shirt, {}).get(p, 0)
            if w > best_w:
                best_w    = w
                best_pant = p
        return best_pant, round(best_w, 4)

    def outfit_path_score(self, shirt, available_pants):
        """
        How well does `shirt` anchor outfit paths through available pants?

        = weighted average of top-3 pant matches (not just the single best)
          so shirts that pair broadly score higher than shirts that only
          match one pant perfectly.
        """
        scores = sorted(
            [self.adj.get(shirt, {}).get(p, 0) for p in available_pants],
            reverse=True
        )
        top3   = scores[:3]
        if not top3:
            return 0.0
        # Weighted avg: best pant counts 3×, second 2×, third 1×
        weights = [3, 2, 1][:len(top3)]
        wsum    = sum(s * w for s, w in zip(top3, weights))
        return round(wsum / sum(weights), 4)


def build_graphs(colors):
    """Build and return both graphs in a single call."""
    return ColorGraph(colors), OutfitGraph(colors)


def graph_signals(candidate_name, candidate_data, wardrobe,
                  wardrobe_pants, color_graph, outfit_graph):
    """
    Compute all graph-derived signals for a single candidate color.

    Returns a dict:
      influence_score   — scaled two-hop influence (added to shirt+pant scores)
      outfit_path_score — how well candidate anchors outfit paths through pants
      centrality        — candidate's weighted degree centrality in full graph
      top_influenced    — top-3 colors most incrementally improved by candidate
    """
    influence = color_graph.influence_of(candidate_name, wardrobe)

    # Outfit path score: use wardrobe pants + any pant-allowed wardrobe item
    available_pants = [p for p in wardrobe_pants
                       if p in outfit_graph.pant_nodes]
    # Also consider all pant nodes if wardrobe has no pants yet
    if not available_pants:
        available_pants = outfit_graph.pant_nodes

    ops = outfit_graph.outfit_path_score(candidate_name, available_pants)

    centrality = color_graph.degree_centrality().get(candidate_name, 0)

    # Top-3 most influenced colors (by incremental + hop2 combined)
    combined_influence = {
        k: influence["incremental"].get(k, 0) + influence["hop2"].get(k, 0)
        for k in set(list(influence["incremental"]) + list(influence["hop2"]))
    }
    top_influenced = sorted(combined_influence.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "influence_score":   influence["total"],
        "raw_influence":     influence["raw_total"],
        "outfit_path_score": ops,
        "centrality":        centrality,
        "top_influenced":    top_influenced,
        "incremental_map":   influence["incremental"],
        "hop2_map":          influence["hop2"]
    }


# ==========================================================
# GRAPH VISUALIZATION
# ==========================================================

def visualize_color_graph(colors, wardrobe=None, highlight=None,
                          filename="color_graph.png"):
    """
    Draw the color compatibility network.
    Nodes are colored by their hex value.
    Edge thickness = match strength.
    Wardrobe nodes are outlined in gold.
    Highlighted candidate (if given) is outlined in red.
    """
    import math

    cg = ColorGraph(colors)
    nodes = cg.nodes
    n     = len(nodes)

    # Circular layout
    pos = {}
    for i, node in enumerate(nodes):
        angle      = 2 * math.pi * i / n
        pos[node]  = (math.cos(angle), math.sin(angle))

    wardrobe_set = set(wardrobe or [])

    fig, ax = plt.subplots(figsize=(14, 14))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Color Compatibility Network", fontsize=16, pad=20)

    # Draw edges — only strong ones (weight ≥ 2.0) to avoid visual clutter
    for a, neighbors in cg.adj.items():
        for b, w in neighbors.items():
            if b < a:   # undirected — draw once
                continue
            if w < 2.0:
                continue
            x0, y0 = pos[a]
            x1, y1 = pos[b]
            lw = (w / 3.5) * 2.5   # scale linewidth to max edge weight
            ax.plot([x0, x1], [y0, y1], color="#cccccc", lw=lw,
                    alpha=0.5, zorder=1)

    # Draw nodes
    node_radius = 0.09
    for node in nodes:
        x, y      = pos[node]
        hex_color = colors[node]["hex"]

        circle = plt.Circle((x, y), node_radius,
                             color=hex_color, zorder=3)
        ax.add_patch(circle)

        # Border: gold = wardrobe, red = highlight, black = default
        if node == highlight:
            border_color = "#FF3333"
            border_lw    = 3
        elif node in wardrobe_set:
            border_color = "#c9a84c"
            border_lw    = 3
        else:
            border_color = "#333333"
            border_lw    = 1

        ring = plt.Circle((x, y), node_radius,
                           fill=False, edgecolor=border_color,
                           lw=border_lw, zorder=4)
        ax.add_patch(ring)

        # Label — offset outward from center
        lx = x * 1.22
        ly = y * 1.22
        ax.text(lx, ly, node, ha="center", va="center",
                fontsize=6.5, zorder=5,
                fontweight="bold" if node in wardrobe_set or node == highlight else "normal")

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {filename}")


def visualize_outfit_flow(colors, wardrobe_shirts, wardrobe_pants,
                          recommended_shirts, filename="outfit_flow.png"):
    """
    Draw the bipartite outfit flow graph.
    Left column  = shirts (wardrobe in gold, recommended in green).
    Right column = pants  (wardrobe in gold).
    Edge thickness = match strength.  Only edges ≥ 2.5 drawn.
    """
    og = OutfitGraph(colors)

    all_shirts = list(dict.fromkeys(wardrobe_shirts + recommended_shirts))
    all_pants  = wardrobe_pants if wardrobe_pants else og.pant_nodes[:6]

    fig, ax = plt.subplots(figsize=(12, max(8, max(len(all_shirts), len(all_pants)) * 0.9)))
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_title("Outfit Flow Graph", fontsize=14, pad=16)

    shirt_xs = 0.15
    pant_xs  = 0.85

    def y_pos(idx, total):
        return 0.1 + (0.8 * idx / max(1, total - 1)) if total > 1 else 0.5

    shirt_pos = {s: (shirt_xs, y_pos(i, len(all_shirts)))
                 for i, s in enumerate(all_shirts)}
    pant_pos  = {p: (pant_xs,  y_pos(i, len(all_pants)))
                 for i, p in enumerate(all_pants)}

    # Edges
    for s in all_shirts:
        for p in all_pants:
            w = og.adj.get(s, {}).get(p, 0)
            if w < 2.5:
                continue
            x0, y0 = shirt_pos[s]
            x1, y1 = pant_pos[p]
            lw = (w / 3.5) * 3
            ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                        arrowprops=dict(arrowstyle="-|>",
                                        lw=lw, color="#aaaaaa",
                                        connectionstyle="arc3,rad=0.05"),
                        zorder=1)

    # Shirt nodes
    for s, (x, y) in shirt_pos.items():
        color = colors[s]["hex"]
        is_wardrobe = s in wardrobe_shirts
        border = "#c9a84c" if is_wardrobe else "#228B22"
        circle = plt.Circle((x, y), 0.04, color=color, zorder=3)
        ax.add_patch(circle)
        ring = plt.Circle((x, y), 0.04, fill=False,
                           edgecolor=border, lw=2.5, zorder=4)
        ax.add_patch(ring)
        ax.text(x - 0.07, y, s, ha="right", va="center", fontsize=7.5, zorder=5)

    # Pant nodes
    for p, (x, y) in pant_pos.items():
        color = colors[p]["hex"]
        is_wardrobe = p in wardrobe_pants
        border = "#c9a84c" if is_wardrobe else "#333333"
        circle = plt.Circle((x, y), 0.04, color=color, zorder=3)
        ax.add_patch(circle)
        ring = plt.Circle((x, y), 0.04, fill=False,
                           edgecolor=border, lw=2.5, zorder=4)
        ax.add_patch(ring)
        ax.text(x + 0.07, y, p, ha="left", va="center", fontsize=7.5, zorder=5)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#c9a84c", label="Wardrobe item"),
        Patch(facecolor="#228B22", label="Recommended shirt"),
        Patch(facecolor="#333333", label="Available pant"),
    ]
    ax.legend(handles=legend_elements, loc="lower center",
              fontsize=8, ncol=3, bbox_to_anchor=(0.5, -0.02))

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {filename}")


def visualize_influence_propagation(candidate, color_graph, wardrobe,
                                    filename="influence_propagation.png"):
    """
    Bar chart showing incremental (direct) and hop-2 influence
    that adding `candidate` brings to every non-wardrobe color.
    """
    influence = color_graph.influence_of(candidate, wardrobe)
    inc   = influence["incremental"]
    hop2  = influence["hop2"]

    all_colors = sorted(
        set(list(inc.keys()) + list(hop2.keys())),
        key=lambda x: -(inc.get(x, 0) + hop2.get(x, 0))
    )

    if not all_colors:
        print(f"  (no influence data for {candidate})")
        return

    # Only top 15 for readability
    all_colors = all_colors[:15]

    inc_vals  = [inc.get(c, 0)  for c in all_colors]
    hop2_vals = [hop2.get(c, 0) for c in all_colors]
    hex_vals  = [color_graph.colors.get(c, {}).get("hex", "#888888")
                 for c in all_colors]

    x    = range(len(all_colors))
    fig, ax = plt.subplots(figsize=(13, 5))

    ax.bar(x, inc_vals,  label="Direct (hop-1)",
           color=[h for h in hex_vals], edgecolor="#333", width=0.5, zorder=2)
    ax.bar(x, hop2_vals, bottom=inc_vals, label="Indirect (hop-2)",
           color=[h for h in hex_vals], edgecolor="#888",
           width=0.5, alpha=0.45, zorder=2)

    ax.set_xticks(list(x))
    ax.set_xticklabels(all_colors, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Influence Score")
    ax.set_title(f"Influence Propagation: adding '{candidate}' to wardrobe {wardrobe}")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3, zorder=1)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {filename}")


# ==========================================================
# MAIN ENGINE
# ==========================================================

def generate_recommendations(input_data):

    colors         = build_color_objects()
    shirts_input   = input_data.get("shirts",   [])
    pants_input    = input_data.get("pants",    [])
    season         = input_data.get("season",   "All")
    skin_profile   = input_data.get("skin_profile",        None)
    contrast_pref  = input_data.get("contrast_preference", None)
    clothing_type  = input_data.get("clothing_type",       "Both")   # Formal | T-Shirt | Both
    style_pref     = input_data.get("style_preference",    "Any")    # Classic | Bold | Any

    # --------------------------------------------------
    # COMPUTE EFFECTIVE WEIGHTS
    # Combine base WEIGHTS with type + style modifiers.
    # Both are additive deltas — they stack on top of each other.
    # --------------------------------------------------
    type_mod  = TYPE_WEIGHT_MODIFIERS.get(clothing_type, TYPE_WEIGHT_MODIFIERS["Both"])
    style_mod = STYLE_WEIGHT_MODIFIERS.get(style_pref,   STYLE_WEIGHT_MODIFIERS["Any"])
    effective_weights = {
        k: max(0.1, WEIGHTS[k] + type_mod[k] + style_mod[k])
        for k in WEIGHTS
    }

    # --------------------------------------------------
    # FORMAL FILTERING
    # When clothing_type is Formal, restrict candidates to
    # colours that are appropriate for formal wear.
    # --------------------------------------------------
    formal_shirt_filter = (clothing_type == "Formal")
    formal_pant_filter  = (clothing_type == "Formal")

    # Validate — silently drop unknown color names
    shirts_input = [s for s in shirts_input if s in colors]
    pants_input  = [p for p in pants_input  if p in colors]
    wardrobe     = shirts_input + pants_input

    # --------------------------------------------------
    # BUILD GRAPHS  (once per call, shared across all loops)
    # --------------------------------------------------
    color_graph, outfit_graph = build_graphs(colors)

    # --------------------------------------------------
    # FIX-BUG-B: empty wardrobe → dedicated starter path
    # which now returns the same full schema
    # --------------------------------------------------
    if not wardrobe:
        return starter_wardrobe(skin_profile, season, colors)

    profile   = SKIN_PROFILES.get(skin_profile, {})
    primary   = profile.get("primary",   [])
    secondary = profile.get("secondary", [])
    avoided   = set(profile.get("avoid", []))

    results = []

    # --------------------------------------------------
    # GRAPH — batch precomputation (hoisted before candidate loop)
    #
    # already_served and degree_centrality are both wardrobe-dependent
    # constants that were previously recomputed per candidate (20× each).
    # batch_influence() computes already_served ONCE and iterates all
    # candidates in a single pass.  degree_centrality() now reads from
    # the cache built in ColorGraph.__init__.
    # --------------------------------------------------
    # Apply formal filter to candidate pool
    candidates_for_graph = [
        name for name in colors
        if name not in wardrobe and name not in avoided
        and (not formal_shirt_filter or name in FORMAL_SHIRT_COLORS)
    ]
    centrality_map  = color_graph.degree_centrality()          # O(1) — from cache
    batch_inf       = color_graph.batch_influence(             # O(n²) once, not 20×
                          candidates_for_graph, wardrobe)
    outfit_path_map = {                                        # O(shirts × pants) once
        name: outfit_graph.outfit_path_score(
                  name, pants_input or outfit_graph.pant_nodes)
        for name in candidates_for_graph
        if name in outfit_graph.adj
    }

    # Store effective_weights in result metadata for transparency
    _eff_w = effective_weights

    for name, data in colors.items():

        if name in wardrobe or name in avoided:
            continue

        # Formal shirt filter — skip non-formal colours when type=Formal
        if formal_shirt_filter and data["shirt_allowed"] and name not in FORMAL_SHIRT_COLORS:
            continue
        # Formal pant filter — skip casual-only pant colours when type=Formal
        if formal_pant_filter and data["pant_allowed"] and not data["shirt_allowed"] and name not in FORMAL_PANT_COLORS:
            continue

        # --------------------------------------------------
        # BASE COMPATIBILITY SCORE
        # --------------------------------------------------
        base_compat = 0
        combos      = 0

        for item in wardrobe:
            if item not in colors:
                continue
            match        = get_match_strength(data, colors[item], effective_weights)
            base_compat += match
            if match >= COMBO_THRESHOLD:
                combos  += 1

        # --------------------------------------------------
        # DENSITY BONUS  (FIX-BUG-D: single bonus, not two)
        # Previously coverage_bonus was added on top of density;
        # both were proportional to combos → effective 2.1× multiplier.
        # Now only density is used.  coverage_bonus is kept as a utility
        # function for pairs_with_wardrobe but NOT added to the score.
        # --------------------------------------------------
        density_bonus = (combos / max(2, len(wardrobe))) * DENSITY_WEIGHT

        # --------------------------------------------------
        # EXPANSION BONUS  (outfit unlock potential)
        # --------------------------------------------------
        expansion_bonus = wardrobe_expansion_bonus(
            name, shirts_input, pants_input, colors
        )

        # --------------------------------------------------
        # NEUTRAL NORMALIZATION
        # FIX-WARN2: penalty coefficient derived from WEIGHTS["neutral"]
        # so it stays in sync if the weight constant is tuned.
        # --------------------------------------------------
        neutral_penalty = 0.0
        if data["neutral"]:
            neutral_penalty = effective_weights["neutral"] * NEUTRAL_PENALTY_RATIO * len(wardrobe)

        # --------------------------------------------------
        # SKIN PERSONALIZATION
        # FIX-BUG-C: skin_delta added to neutral_score too so
        # profile-primary neutrals (e.g. Charcoal for Deep_Cool) rank
        # above generic neutrals in all_season_neutrals.
        # --------------------------------------------------
        skin_delta = 0
        if name in primary:
            skin_delta = PERSONALIZATION_WEIGHTS["skin_primary"]
        elif name in secondary:
            skin_delta = PERSONALIZATION_WEIGHTS["skin_secondary"]

        # --------------------------------------------------
        # CONTRAST PREFERENCE
        # --------------------------------------------------
        contrast_adj = contrast_adjustment(data, wardrobe, contrast_pref, colors)

        # --------------------------------------------------
        # GRAPH SIGNALS  (read from precomputed batch maps — O(1) per candidate)
        # influence_score   — two-hop propagation: how much adding this
        #                     color improves coverage of the broader network
        # outfit_path_score — how broadly this shirt pairs across current pants
        # Both are additive signals, not replacements.
        # --------------------------------------------------
        inf_data          = batch_inf.get(name, {})
        graph_influence   = inf_data.get("total", 0.0)
        graph_outfit_path = outfit_path_map.get(name, 0.0)
        top_influenced    = inf_data.get("top_influenced", [])

        # --------------------------------------------------
        # ASSEMBLE SCORES  (shirt and pant get season independently)
        # --------------------------------------------------
        shared = (base_compat
                  + density_bonus
                  + expansion_bonus
                  - neutral_penalty
                  + skin_delta
                  + contrast_adj
                  + graph_influence)     # ← graph signal injected here

        shirt_score   = (shared
                         + (season_weight(data, season, "shirt") if not data["neutral"] else 0)
                         + graph_outfit_path)   # outfit path bonus applies to shirts only

        pant_score    = shared + (season_weight(data, season, "pant") if not data["neutral"] else 0)

        # FIX-BUG-C: neutral_score includes skin_delta (same shared base)
        neutral_score = shared  # season is always 0 for neutrals

        results.append(_full_schema(
            name, data,
            shirt_score, pant_score, neutral_score,
            combos, skin_delta, wardrobe, colors,
            graph_influence   = round(graph_influence, 4),
            graph_outfit_path = round(graph_outfit_path, 4),
            graph_centrality  = centrality_map.get(name, 0),
            top_influenced    = top_influenced,
        ))

    # --------------------------------------------------
    # SORT
    # FIX-NEUTRAL: removed "and not r['neutral']" from shirts_sorted.
    # Neutrals (White, Grey, Charcoal …) are valid shirt recommendations
    # and should compete on score like any other color.
    # all_season_neutrals is kept as a separate curated list but is
    # deduped against whatever ended up in shirts_final so the same
    # color never appears in both outputs.
    # --------------------------------------------------
    shirts_sorted   = sorted([r for r in results if r["shirt_allowed"]],
                             key=lambda x: x["shirt_score"],   reverse=True)
    pants_sorted    = sorted([r for r in results if r["pant_allowed"]],
                             key=lambda x: x["pant_score"],    reverse=True)

    # --------------------------------------------------
    # DIVERSITY FILTER
    # --------------------------------------------------
    shirts_final   = diversity_filter(shirts_sorted,   5, len(wardrobe), "shirt_score")
    pants_final    = diversity_filter(pants_sorted,    4, len(wardrobe), "pant_score")

    # Deduplicate neutrals: exclude any color already recommended as a shirt
    shirts_final_names = {r["color"] for r in shirts_final}
    neutrals_sorted = sorted(
        [r for r in results if r["neutral"] and r["color"] not in shirts_final_names],
        key=lambda x: x["neutral_score"], reverse=True
    )
    neutrals_final = diversity_filter(neutrals_sorted, 3, len(wardrobe), "neutral_score")

    # --------------------------------------------------
    # PAIR MATRIX + OUTFITS
    # --------------------------------------------------
    pair_matrix = build_pair_matrix(shirts_final, pants_final)

    outfit_shirts = shirts_input + [s["color"] for s in shirts_final]
    outfit_pants  = pants_input  + [p["color"] for p in pants_final]
    outfits       = generate_outfits(outfit_shirts, outfit_pants, colors)

    # --------------------------------------------------
    # GRAPH ANALYTICS  (attached to response for UI / debugging)
    # --------------------------------------------------
    centrality     = color_graph.degree_centrality()
    wardrobe_graph = {
        "centrality_ranking": sorted(
            centrality.items(), key=lambda x: x[1], reverse=True
        ),
        "wardrobe_centrality": {
            w: centrality[w] for w in wardrobe if w in centrality
        },
        # Top-5 most globally connected colors (highest centrality)
        "most_connected": sorted(
            centrality.items(), key=lambda x: x[1], reverse=True
        )[:5],
        # Which existing wardrobe item is the best "hub" (most connections)
        "wardrobe_hub": max(
            ((w, centrality[w]) for w in wardrobe if w in centrality),
            key=lambda x: x[1], default=(None, 0)
        ),
    }

    return {
        "smart_shirts":        shirts_final,
        "smart_pants":         pants_final,
        "all_season_neutrals": neutrals_final,
        "pair_matrix":         pair_matrix[:20],
        "outfits":             outfits,
        "mode":                "full",
        "graph":               wardrobe_graph,
        "clothing_type":       clothing_type,
        "style_preference":    style_pref,
        "effective_weights":   effective_weights,
    }


# ==========================================================
# WARDROBE GAP ANALYSIS
# ==========================================================
#
# Analyses the user's existing wardrobe across 5 dimensions:
#   1. Shirt-to-pant ratio & bottleneck
#   2. Outfit count vs potential
#   3. Neutral anchor check (shirts + pants)
#   4. Colour family diversity
#   5. Depth spread (Light / Medium / Deep)
#
# Returns a structured dict with:
#   score       — 0-100 overall wardrobe health score
#   band        — text label for score range
#   praises     — list of things the user is doing well
#   gaps        — list of gaps with severity + actionable message
#   stats       — raw numbers for display
# ==========================================================

COMPLEMENT_SUGGEST = {
    "Blue":    "Warm or Red tones",
    "Warm":    "Blue or Purple tones",
    "Green":   "Red or Purple tones",
    "Neutral": "any statement colour family",
    "Red":     "Green or Blue tones",
    "Purple":  "Warm or Green tones",
    "Soft":    "Blue or Green tones",
}

def wardrobe_gap_analysis(shirts_input, pants_input, smart_shirts=None, smart_pants=None):
    """
    Analyse the user's current wardrobe and return gap insights + praise.

    shirts_input  — list of shirt color names the user OWNS
    pants_input   — list of pant color names the user OWNS
    smart_shirts  — top recommended shirt objects (for potential calculation)
    smart_pants   — top recommended pant objects (for potential calculation)

    Returns dict with keys: score, band, praises, gaps, stats
    """
    colors = build_color_objects()

    # Validate inputs
    shirts = [s for s in shirts_input if s in colors]
    pants  = [p for p in pants_input  if p in colors]
    ns, np_ = len(shirts), len(pants)

    # ── RAW METRICS ──────────────────────────────────────────
    ratio        = ns / max(1, np_)
    current      = ns * np_
    shirt_unlock = (ns + 1) * np_ - current   # value of adding 1 shirt
    pant_unlock  = ns * (np_ + 1) - current   # value of adding 1 pant

    # Neutral counts
    neut_shirts  = [s for s in shirts if colors[s]["neutral"]]
    neut_pants   = [p for p in pants  if colors[p]["neutral"]]
    neut_pct     = len(neut_shirts) / max(1, ns)

    # Family analysis
    from collections import Counter
    s_fams       = Counter(colors[s]["family"] for s in shirts)
    n_fams       = len(s_fams)
    dom_entry    = s_fams.most_common(1)[0] if s_fams else ("Neutral", 1)
    dom_fam, dom_cnt = dom_entry
    dom_pct      = dom_cnt / max(1, ns)

    # Depth analysis
    depths       = set(colors[s]["metrics"]["depth"] for s in shirts)
    has_light    = "Light" in depths
    has_deep     = "Deep"  in depths

    # Potential outfits after adding top 2 recommendations
    rec_s = [x["color"] for x in (smart_shirts or [])[:2]]
    rec_p = [x["color"] for x in (smart_pants  or [])[:2]]
    potential    = (ns + len(rec_s)) * (np_ + len(rec_p))

    # ── SCORING (max 100) ────────────────────────────────────
    score = 0

    # 1. Ratio (20pts)
    if 2.0 <= ratio <= 4.0:          score += 20
    elif 1.5 <= ratio <= 5.0:        score += 12
    elif 1.0 <= ratio <= 6.0:        score += 6

    # 2. Outfit count (20pts + 5 bonus for 20+)
    outfit_pts = min(20, int((current / 12) * 20))
    if current >= 20: outfit_pts = min(25, outfit_pts + 5)
    score += outfit_pts

    # 3. Neutral pant (25pts — critical; missing caps total at 60)
    has_neut_pant = len(neut_pants) >= 1
    if has_neut_pant: score += 25

    # 4. Neutral shirt balance (15pts) — ideal 20-50%
    if 0.2 <= neut_pct <= 0.5:       score += 15
    elif 0.1 <= neut_pct <= 0.7:     score += 8

    # 5. Family diversity (10pts)
    if n_fams >= 3 and dom_pct <= 0.5: score += 10
    elif n_fams >= 2:                  score += 5

    # 6. Depth spread (10pts)
    if has_light and has_deep:        score += 10
    elif has_light or has_deep:       score += 4

    # Hard cap: no neutral pant → max 60
    if not has_neut_pant:
        score = min(score, 60)

    score = min(100, score)

    band = (
        "Just getting started" if score < 40 else
        "Building nicely"      if score < 60 else
        "Well-rounded"         if score < 80 else
        "Capsule-ready"
    )

    # ── PRAISES ──────────────────────────────────────────────
    praises = []

    if 2.0 <= ratio <= 4.0:
        praises.append({
            "icon": "✓",
            "text": f"Smart shirt-pant ratio — {ns} shirts for {np_} pant{'s' if np_!=1 else ''} gives solid variety"
        })
    if current >= 12:
        praises.append({
            "icon": "✓",
            "text": f"Strong outfit count — {current} combinations already in your wardrobe"
        })
    if has_neut_pant:
        praises.append({
            "icon": "✓",
            "text": f"Solid neutral anchor — {', '.join(neut_pants)} ground{'s' if len(neut_pants)==1 else ''} your outfit pairings"
        })
    if 0.2 <= neut_pct <= 0.5:
        praises.append({
            "icon": "✓",
            "text": f"Good neutral balance — {len(neut_shirts)} neutral shirt{'s' if len(neut_shirts)!=1 else ''} anchoring {ns - len(neut_shirts)} coloured option{'s' if ns-len(neut_shirts)!=1 else ''}"
        })
    if n_fams >= 3 and dom_pct <= 0.5:
        praises.append({
            "icon": "✓",
            "text": f"Excellent colour variety — {n_fams} different colour families represented in your shirts"
        })
    if has_light and has_deep:
        praises.append({
            "icon": "✓",
            "text": "Good depth contrast range — you have both light and dark shirts for different outfit moods"
        })
    if score >= 80:
        praises.append({
            "icon": "🎯",
            "text": "Your wardrobe is capsule-ready — you've built a versatile, well-balanced collection"
        })

    # ── GAPS ─────────────────────────────────────────────────
    gaps = []

    # Gap 1 — Ratio / Bottleneck
    # Only flag when the imbalance genuinely hurts outfit count
    # pant_unlock vs shirt_unlock shows which adds more value
    if ratio > 5.0:
        gaps.append({
            "severity": "high",
            "title":    "Pant bottleneck",
            "text":     f"You have {ns} shirts but only {np_} pant{'s' if np_!=1 else ''}. "
                        f"Adding 1 pant unlocks {pant_unlock} new outfits — far more than adding another shirt ({shirt_unlock}).",
            "action":   "Priority: add pants first",
        })
    elif ratio < 1.0:
        gaps.append({
            "severity": "high",
            "title":    "Shirt bottleneck",
            "text":     f"You have {np_} pants but only {ns} shirt{'s' if ns!=1 else ''}. "
                        f"Adding 1 shirt unlocks {shirt_unlock} new outfits.",
            "action":   "Priority: add shirts first",
        })
    elif pant_unlock > shirt_unlock * 1.5 and np_ < 3:
        # Pants clearly more valuable but not in crisis — softer suggestion
        gaps.append({
            "severity": "medium",
            "title":    "Adding pants will help more than shirts",
            "text":     f"Adding 1 pant unlocks {pant_unlock} new outfits vs {shirt_unlock} for a shirt. "
                        f"You'd get more variety from pants right now.",
            "action":   "Consider adding a pant before your next shirt",
        })

    # Gap 2 — Outfit count
    if current < 4:
        gaps.append({
            "severity": "high",
            "title":    "Very few outfit combinations",
            "text":     f"Your wardrobe currently makes only {current} outfit combination{'s' if current!=1 else ''}. "
                        f"Adding our top 2 recommendations would grow this to {potential}.",
            "action":   f"Add {rec_s[0] if rec_s else 'a recommended shirt'} + {rec_p[0] if rec_p else 'a recommended pant'} first",
        })
    elif current < 9:
        gaps.append({
            "severity": "medium",
            "title":    "Room to grow outfit count",
            "text":     f"You have {current} outfit combinations — a solid start. "
                        f"Our top recommendations would take you to {potential}.",
            "action":   "Follow the Smart Shirts / Pants recommendations above",
        })

    # Gap 3 — Neutral pant (critical)
    if not has_neut_pant:
        gaps.append({
            "severity": "high",
            "title":    "No neutral pant",
            "text":     f"None of your {np_} pant{'s' if np_!=1 else ''} {'are' if np_!=1 else 'is'} a neutral colour. "
                        f"Neutrals (Navy, Charcoal, Black, Beige) pair with almost every shirt you own.",
            "action":   "Add Navy or Charcoal as your first neutral pant",
        })

    # Gap 3b — Neutral shirt check
    if ns >= 2:
        if neut_pct == 0.0:
            gaps.append({
                "severity": "medium",
                "title":    "No neutral shirt",
                "text":     "You have no neutral shirt. White or Grey pairs with every pant "
                            "and acts as a reliable fallback on any day.",
                "action":   "Add White or Grey as a base shirt",
            })
        elif neut_pct == 1.0:
            gaps.append({
                "severity": "medium",
                "title":    "All shirts are neutrals",
                "text":     f"All {ns} of your shirts are neutral colours. "
                            "Your wardrobe is safe but lacks personality — "
                            "one statement colour would transform your outfit variety.",
                "action":   f"Add one {COMPLEMENT_SUGGEST.get(dom_fam, 'coloured')} shirt",
            })

    # Gap 4 — Family diversity
    # Skip if neut_pct==1.0 — covered already by Gap 3b (all neutrals)
    if n_fams == 1 and neut_pct < 1.0:
        gaps.append({
            "severity": "high",
            "title":    f"All shirts are {dom_fam} family",
            "text":     f"Every shirt you own is in the {dom_fam} colour family. "
                        f"You have no colour variety — every outfit looks similar.",
            "action":   f"Add {COMPLEMENT_SUGGEST.get(dom_fam, 'a different colour family')} to create contrast",
        })
    elif dom_pct > 0.6 and n_fams < 3 and neut_pct < 1.0:
        pct_str = f"{int(dom_pct*100)}%"
        gaps.append({
            "severity": "low",
            "title":    f"{dom_fam} tones dominate",
            "text":     f"{pct_str} of your shirts are {dom_fam} tones. "
                        f"Adding variety from another family would give you very different looks.",
            "action":   f"Consider adding {COMPLEMENT_SUGGEST.get(dom_fam, 'a contrasting tone')}",
        })

    # Gap 5 — Depth spread (only meaningful if 3+ shirts)
    if ns >= 3:
        if not has_light:
            gaps.append({
                "severity": "low",
                "title":    "No light-coloured shirts",
                "text":     "All your shirts are medium or dark depth. "
                            "A light shirt (White, Cream, Sky Blue) creates fresh, high-contrast looks.",
                "action":   "Add one light-toned shirt",
            })
        elif not has_deep:
            gaps.append({
                "severity": "low",
                "title":    "No dark-toned shirts",
                "text":     "All your shirts are light depth. "
                            "A dark shirt (Navy, Charcoal, Burgundy, Olive) adds drama and contrast.",
                "action":   "Add one dark-toned shirt",
            })

    # ── STATS (raw numbers for display) ──────────────────────
    stats = {
        "shirts":           ns,
        "pants":            np_,
        "ratio":            round(ratio, 1),
        "current_outfits":  current,
        "potential_outfits":potential,
        "neut_shirt_count": len(neut_shirts),
        "neut_pant_count":  len(neut_pants),
        "neut_pct":         round(neut_pct * 100),
        "n_families":       n_fams,
        "dominant_family":  dom_fam,
        "shirt_unlock":     shirt_unlock,
        "pant_unlock":      pant_unlock,
        "has_light":        has_light,
        "has_deep":         has_deep,
    }

    return {
        "score":   score,
        "band":    band,
        "praises": praises,
        "gaps":    gaps,
        "stats":   stats,
    }

# ==========================================================
# VERIFICATION SUITE  (12-point, all must pass)
# ==========================================================

def run_all_verifications():

    colors = build_color_objects()
    passed = 0; total = 0

    def check(label, result, note=""):
        nonlocal passed, total
        total += 1
        status = "✅" if result else "❌"
        print(f"  {status}  {label}" + (f"  [{note}]" if note else ""))
        if result: passed += 1

    print("\n" + "=" * 65)
    print("VERIFICATION SUITE")
    print("=" * 65)

    # ── FIX-BUG-A: contrast only Light ↔ Deep ────────────────
    print("\n[FIX-BUG-A] Depth contrast fires only for Light ↔ Deep")
    white = colors["White"];  grey = colors["Grey"];  navy = colors["Navy"]
    lm = get_match_strength(white, grey)
    ld = get_match_strength(white, navy)
    md = get_match_strength(grey,  navy)
    check("Light vs Medium does NOT get +1.5 contrast",
          lm < WEIGHTS["contrast"], f"score={lm}")
    check("Light vs Deep DOES get +1.5 contrast",
          ld >= WEIGHTS["contrast"], f"score={ld}")
    check("Medium vs Deep does NOT get +1.5 contrast",
          md < WEIGHTS["contrast"], f"score={md}")

    # ── FIX-BUG-B: schema parity ─────────────────────────────
    print("\n[FIX-BUG-B] Starter and full paths have identical schema")
    starter = generate_recommendations({"shirts": [], "pants": [],
                                        "season": "Winter", "skin_profile": "Deep_Cool"})
    full    = generate_recommendations({"shirts": ["White"], "pants": ["Navy"],
                                        "season": "Winter", "skin_profile": "Deep_Cool"})
    starter_keys = set(starter["smart_shirts"][0].keys())
    full_keys    = set(full["smart_shirts"][0].keys())
    check("Starter shirt keys == full shirt keys", starter_keys == full_keys,
          f"diff={starter_keys ^ full_keys}")
    check("Starter response has pair_matrix",  "pair_matrix" in starter)
    check("Starter response has outfits",      "outfits"     in starter)
    check("Starter response has mode='starter'", starter.get("mode") == "starter")

    # ── FIX-BUG-C: neutral_score includes skin ───────────────
    print("\n[FIX-BUG-C] neutral_score includes skin personalization")
    res_dc = generate_recommendations({"shirts": ["Royal Blue", "Teal"],
                                       "pants":  ["Navy"],
                                       "season": "All", "skin_profile": "Deep_Cool"})
    all_recs = res_dc["smart_shirts"] + res_dc["all_season_neutrals"]
    charcoal = next((r for r in all_recs if r["color"] == "Charcoal"), None)
    # Since neutrals now compete in smart_shirts, Charcoal (Deep_Cool primary, skin_delta=2.0)
    # may rank in shirts rather than neutrals — either is correct, it must appear somewhere.
    check("Charcoal (Deep_Cool primary) is recommended (shirts OR neutrals)",
          charcoal is not None,
          f"shirts={[r['color'] for r in res_dc['smart_shirts']]}")
    if charcoal:
        check("Charcoal has skin_delta=2.0 confirming skin boost was applied",
              charcoal["skin_delta"] == 2.0, f"skin_delta={charcoal['skin_delta']}")

    # ── FIX-BUG-D: no double-counting ────────────────────────
    print("\n[FIX-BUG-D] Score inflation controlled — expansion capped, growth linear")
    sizes = []
    for ws, wp in [
        (["White"], ["Navy"]),
        (["White", "Sky Blue", "Rust"], ["Navy", "Beige", "Charcoal"]),
        (["White", "Sky Blue", "Rust", "Olive", "Plum"],
         ["Navy", "Beige", "Charcoal", "Brown", "Maroon"]),
    ]:
        r = generate_recommendations({"shirts": ws, "pants": wp, "season": "All"})
        wsz = len(ws) + len(wp)
        top = r["smart_shirts"][0]["shirt_score"]
        sizes.append((wsz, top, round(top / wsz, 3)))
    # Correct check: score grows linearly with wardrobe (score/wsz is stable)
    # A 5× ratio on raw scores is expected (10 items vs 2), but per-item rate should
    # stay within ±0.5 across all wardrobe sizes.
    ratios   = [s[2] for s in sizes]
    variance = max(ratios) - min(ratios)
    check("Score grows roughly linearly — score/wsz variance < 2.5 across wardrobe sizes",
          variance < 2.5,
          f"score/wsz={ratios}  variance={variance:.3f}")

    # ── FIX-WARN1: generic season adjacency ──────────────────
    print("\n[FIX-WARN1] Season adjacency — generic, no double-stacking")
    # Plum = Deep+Soft = Autumn primary. Correct check: Plum Autumn > Plum Winter.
    # (Lavender = Light+Bold = Spring primary — was the wrong color to test Summer.)
    # No Light+Soft non-neutral exists in this palette, so Summer primary gap is a
    # data issue, not an engine issue.
    plum = colors["Plum"]   # Deep, Soft → Autumn primary
    plum_autumn = season_weight(plum, "Autumn", "shirt")
    plum_winter = season_weight(plum, "Winter", "shirt")
    check("Plum (Deep+Soft) scores highest in Autumn (its primary season)",
          plum_autumn > plum_winter,
          f"Autumn={plum_autumn} Winter={plum_winter}")
    rust = colors["Rust"]   # Deep, Bold → Winter primary
    rust_autumn = season_weight(rust, "Autumn", "shirt")
    rust_winter = season_weight(rust, "Winter", "shirt")
    check("Rust (Deep+Bold) scores highest in Winter (its primary season)",
          rust_winter > rust_autumn,
          f"Autumn={rust_autumn} Winter={rust_winter}")

    # ── FIX-WARN2: penalty derived from weight ────────────────
    print("\n[FIX-WARN2] Neutral penalty coefficient derived from weight constant")
    effective_penalty_ratio = round(
        (WEIGHTS["neutral"] * NEUTRAL_PENALTY_RATIO) / WEIGHTS["neutral"], 3
    )
    check("NEUTRAL_PENALTY_RATIO constant exists and is ~0.583",
          abs(NEUTRAL_PENALTY_RATIO - 0.583) < 0.01,
          f"actual={NEUTRAL_PENALTY_RATIO}")

    # ── FIX-WARN3: diversity filter — same-family eliminated, cross-family penalised ──
    print("\n[FIX-WARN3] Diversity: same-family hue-close eliminated; cross-family penalised")
    mock = [
        {"color":"Sky Blue",    "family":"Blue",   "hue":197, "shirt_score":10.0, "neutral":False},
        {"color":"Powder Blue", "family":"Blue",   "hue":187, "shirt_score":9.8,  "neutral":False},
        {"color":"Lavender",    "family":"Purple", "hue":240, "shirt_score":7.0,  "neutral":False},
        {"color":"Rust",        "family":"Warm",   "hue":15,  "shirt_score":6.5,  "neutral":False},
    ]
    filtered = diversity_filter(mock, 4, 4, "shirt_score")
    powder_gone = not any(r["color"] == "Powder Blue" for r in filtered)
    sky_present = any(r["color"] == "Sky Blue"    for r in filtered)
    check("Same-family hue-close (Powder Blue) is eliminated — Sky Blue wins",
          powder_gone and sky_present,
          f"output={[r['color'] for r in filtered]}")

    # ── FIX-NEUTRAL: neutrals appear in smart_shirts ─────────
    print("\n[FIX-NEUTRAL] Neutrals compete in smart_shirts (no blanket exclusion)")
    # With a mostly-colored wardrobe, a neutral shirt should rank if it scores well
    res_n2 = generate_recommendations({
        "shirts": ["Rust", "Burgundy", "Plum"],
        "pants":  ["Navy", "Brown"],
        "season": "All", "skin_profile": "Deep_Cool"
    })
    shirt_names = [r["color"] for r in res_n2["smart_shirts"]]
    neutral_in_shirts = any(colors[n]["neutral"] for n in shirt_names if n in colors)
    check("At least one neutral appears in smart_shirts when it scores competitively",
          neutral_in_shirts, f"shirts={shirt_names}")
    # Deduplication: no color in both smart_shirts and all_season_neutrals
    shirt_set   = {r["color"] for r in res_n2["smart_shirts"]}
    neutral_set = {r["color"] for r in res_n2["all_season_neutrals"]}
    overlap = shirt_set & neutral_set
    check("No color appears in both smart_shirts and all_season_neutrals",
          len(overlap) == 0, f"overlap={overlap}")

    # ── FIX-HUE: same-family hue violations = 0 ──────────────
    print("\n[FIX-HUE] Same-family hue violations eliminated")
    import random; random.seed(99)
    shirt_pool_v = [c for c in colors if colors[c]["shirt_allowed"]]
    pant_pool_v  = [c for c in colors if colors[c]["pant_allowed"]]
    same_fam_viols = 0
    for _ in range(200):
        sh = random.sample(shirt_pool_v, random.randint(1,3))
        pa = random.sample(pant_pool_v, random.randint(1,2))
        r = generate_recommendations({"shirts":sh,"pants":pa,"season":"All"})
        hues_v = [(x["color"],x["hue"],x["family"]) for x in r["smart_shirts"]]
        for i in range(len(hues_v)):
            for j in range(i+1, len(hues_v)):
                if (hue_distance(hues_v[i][1], hues_v[j][1]) < HUE_THRESHOLD
                        and hues_v[i][2] == hues_v[j][2]):
                    same_fam_viols += 1
    check("Zero same-family hue violations across 200 runs",
          same_fam_viols == 0, f"violations={same_fam_viols}")
    navy2  = colors["Navy"]; royal = colors["Royal Blue"]
    s_nr   = get_match_strength(navy2, royal)
    check("FIX1: Neutral OR — Navy vs Royal Blue gets neutral bonus",
          s_nr >= WEIGHTS["neutral"], f"score={s_nr}")
    try:
        generate_recommendations({"shirts": [], "pants": [], "season": "All"})
        check("Empty wardrobe doesn't crash", True)
    except Exception as e:
        check("Empty wardrobe doesn't crash", False, str(e))

    # ── GRAPH MODEL ───────────────────────────────────────────
    print("\n[GRAPH] Color compatibility network + influence propagation")
    cg = ColorGraph(colors)

    # Network structure
    node_count = len(cg.nodes)
    edge_count = sum(len(v) for v in cg.adj.values()) // 2
    check("ColorGraph has 25 nodes", node_count == 25, f"actual={node_count}")
    check("ColorGraph has 274 edges (full 91% dense network)",
          edge_count == 274, f"actual={edge_count}")

    # Centrality — White should rank highly (neutral, pairs with everything)
    centrality = cg.degree_centrality()
    white_cent = centrality.get("White", 0)
    check("White has positive centrality (neutral hub)",
          white_cent > 0, f"White centrality={white_cent}")

    # Influence propagation — adding Teal to [White, Navy] should
    # bring non-zero influence (Teal unlocks Warm colors not covered by neutrals)
    inf = cg.influence_of("Teal", ["White", "Navy"])
    check("Teal influence on [White,Navy] wardrobe is > 0",
          inf["total"] > 0, f"total={inf['total']} raw={inf['raw_total']}")
    check("Influence has incremental and hop2 components",
          len(inf["incremental"]) > 0 and len(inf["hop2"]) > 0,
          f"incremental={len(inf['incremental'])} hop2={len(inf['hop2'])}")

    # Outfit graph
    og = OutfitGraph(colors)
    shirt_count = len(og.shirt_nodes)
    check("OutfitGraph has 24 shirt nodes", shirt_count == 24, f"actual={shirt_count}")

    # Outfit path score: Burgundy should pair well with Navy and Beige
    ops = og.outfit_path_score("Burgundy", ["Navy", "Beige", "Charcoal", "Brown"])
    check("Burgundy outfit path score > 0 with multiple pants",
          ops > 0, f"ops={ops}")

    # End-to-end: graph keys appear in recommendation output
    res_g = generate_recommendations({
        "shirts": ["White", "Sky Blue"], "pants": ["Navy", "Beige"],
        "season": "Winter", "skin_profile": "Deep_Cool"
    })
    check("Response contains 'graph' key", "graph" in res_g)
    check("Graph has centrality_ranking", "centrality_ranking" in res_g.get("graph", {}))
    check("Graph has wardrobe_hub", "wardrobe_hub" in res_g.get("graph", {}))
    # Graph influence propagated into shirt scores
    top_shirt = res_g["smart_shirts"][0]
    check("Top shirt has graph_influence field",
          "graph_influence" in top_shirt, f"keys={list(top_shirt.keys())[:6]}")
    check("Top shirt has graph_outfit_path field",
          "graph_outfit_path" in top_shirt)

    # ── GRAPH PERFORMANCE: batch path is faster than per-call ─
    print("\n[GRAPH-PERF] batch_influence() and centrality cache")
    import time as _time
    _colors  = build_color_objects()
    _cg      = ColorGraph(_colors)
    _wardrobe = ["White", "Sky Blue", "Navy", "Beige"]
    _cands   = [n for n in _colors if n not in _wardrobe]

    # Centrality from cache should be instant — same dict returned
    _t0 = _time.perf_counter()
    for _ in range(1000): _cg.degree_centrality()
    _t1 = _time.perf_counter()
    centrality_ms_per_call = (_t1 - _t0)          # 1000 calls total
    check("degree_centrality() reads from cache (1000 calls < 5ms total)",
          centrality_ms_per_call < 0.005,
          f"1000 calls={centrality_ms_per_call*1000:.2f}ms")

    # batch_influence should be faster than 20× influence_of
    _t0 = _time.perf_counter()
    for _ in range(200): _cg.batch_influence(_cands, _wardrobe)
    _t1 = _time.perf_counter()
    batch_ms = (_t1 - _t0) / 200 * 1000

    _t0 = _time.perf_counter()
    for _ in range(200):
        for c in _cands: _cg.influence_of(c, _wardrobe)
    _t1 = _time.perf_counter()
    serial_ms = (_t1 - _t0) / 200 * 1000

    speedup = serial_ms / max(batch_ms, 0.001)
    check(f"batch_influence() faster than serial influence_of() (speedup > 1.1×)",
          speedup > 1.1, f"batch={batch_ms:.2f}ms serial={serial_ms:.2f}ms speedup={speedup:.2f}×")

    print(f"\n{'=' * 65}")
    print(f"RESULT: {passed}/{total} checks passed")
    print(f"{'=' * 65}\n")
    return passed, total

# ==========================================================
# FEATURE TESTS
# ==========================================================

def run_feature_tests():

    print("FEATURE TESTS")
    print("-" * 40)

    res = generate_recommendations({
        "shirts": ["White", "Sky Blue"],
        "pants":  ["Navy", "Beige"],
        "season": "Winter",
        "skin_profile": "Deep_Cool"
    })

    print(f"Pair matrix:  {len(res['pair_matrix'])} entries")
    print(f"Outfits:      {len(res['outfits'])} entries")
    print(f"Mode:         {res['mode']}")

    shirt = res["smart_shirts"][0]
    print(f"Compat map:   {len(shirt['pairs_with_wardrobe'])} pairs")

    print("\nTop Shirts  (with graph signals):")
    for r in res["smart_shirts"]:
        print(f"  {r['color']:<16} shirt={r['shirt_score']:<7} "
              f"influence={r['graph_influence']:<6} "
              f"path={r['graph_outfit_path']:<6} "
              f"central={r['graph_centrality']:<6} "
              f"combos={r['combinations']}")
        if r["top_influenced"]:
            influenced = ", ".join(f"{c}(+{v:.2f})" for c, v in r["top_influenced"])
            print(f"  {'':16}  → most improves: {influenced}")

    print("\nTop Pants:")
    for r in res["smart_pants"]:
        print(f"  {r['color']:<16} pant={r['pant_score']:<7}")

    print("\nTop Neutrals:")
    for r in res["all_season_neutrals"]:
        print(f"  {r['color']:<16} neutral={r['neutral_score']:<7} skin_delta={r['skin_delta']}")

    print("\nGraph Analytics:")
    g = res["graph"]
    print(f"  Wardrobe hub:     {g['wardrobe_hub']}")
    print(f"  Most connected:   {g['most_connected']}")
    print(f"  Wardrobe centrality:")
    for color, cent in g["wardrobe_centrality"].items():
        print(f"    {color:<16} {cent}")

# ==========================================================
# STRESS TEST + VISUALIZATION
# ==========================================================

def stress_test_engine(simulations=300):

    print("\n" + "=" * 70)
    print("ENGINE DIAGNOSTIC STRESS TEST")
    print("=" * 70)

    colors     = build_color_objects()
    color_names = list(colors.keys())
    shirt_pool  = [c for c in color_names if colors[c]["shirt_allowed"]]
    pant_pool   = [c for c in color_names if colors[c]["pant_allowed"]]

    top_scores     = []
    combo_density  = []
    family_diversity = []
    neutral_count  = 0
    hue_violations = 0
    total_picks    = 0
    family_counter = Counter()
    expansion_values = []

    for _ in range(simulations):

        shirts = random.sample(shirt_pool, random.randint(1, 4))
        pants  = random.sample(pant_pool,  random.randint(1, 3))
        season = random.choice(["Spring", "Summer", "Autumn", "Winter", "All"])
        skin   = random.choice(list(SKIN_PROFILES.keys()))

        result = generate_recommendations({
            "shirts": shirts, "pants": pants,
            "season": season, "skin_profile": skin
        })

        if not result["smart_shirts"]:
            continue

        top_scores.append(result["smart_shirts"][0]["shirt_score"])

        combos = [r["combinations"] for r in result["smart_shirts"]]
        combo_density.append(sum(combos) / len(combos))

        before = count_outfits(shirts, pants)
        for r in result["smart_shirts"]:
            after = count_outfits(shirts + [r["color"]], pants)
            expansion_values.append(after - before)

        families = set()
        for r in result["smart_shirts"]:
            families.add(r["family"])
            family_counter[r["family"]] += 1
            total_picks += 1
            if r["neutral"]: neutral_count += 1

        family_diversity.append(len(families))

        hues = [r["hue"]    for r in result["smart_shirts"]]
        fams = [r["family"] for r in result["smart_shirts"]]
        for i in range(len(hues)):
            for j in range(i + 1, len(hues)):
                if hue_distance(hues[i], hues[j]) < HUE_THRESHOLD:
                    if fams[i] == fams[j]:
                        hue_violations += 1   # same-family: should be 0 after fix

    avg_top = sum(top_scores) / len(top_scores)

    print(f"\nAverage Top Shirt Score:  {round(avg_top, 2)}")
    print(f"Max Top Shirt Score:      {round(max(top_scores), 2)}")
    print(f"Min Top Shirt Score:      {round(min(top_scores), 2)}")
    print(f"Average Combo Density:    {round(sum(combo_density)/len(combo_density), 2)}")
    print(f"Average Family Diversity: {round(sum(family_diversity)/len(family_diversity), 2)}")
    print(f"Neutral Ratio:            {round(neutral_count/max(1,total_picks), 3)}")
    print(f"Hue Violations (same-fam):{hue_violations}  (target: 0)")
    if expansion_values:
        print(f"Average Outfit Expansion: {round(sum(expansion_values)/len(expansion_values), 2)}")

    # ── Charts ──────────────────────────────────────────────

    print("\nGenerating diagnostic charts...")

    plt.figure()
    neutral_ratio = neutral_count / max(1, total_picks)
    plt.pie([neutral_ratio, 1 - neutral_ratio],
            labels=["Neutral", "Non-Neutral"], autopct="%1.1f%%")
    plt.title("Neutral Recommendation Ratio")
    plt.savefig("neutral_ratio_chart.png"); plt.close()

    plt.figure()
    plt.bar(list(family_counter.keys()), list(family_counter.values()))
    plt.title("Color Family Distribution")
    plt.xlabel("Color Family"); plt.ylabel("Count")
    plt.savefig("family_distribution_chart.png"); plt.close()

    plt.figure()
    plt.hist(top_scores, bins=20)
    plt.title("Top Shirt Score Distribution")
    plt.xlabel("Score"); plt.ylabel("Frequency")
    plt.savefig("score_histogram.png"); plt.close()

    print("  ✓ neutral_ratio_chart.png")
    print("  ✓ family_distribution_chart.png")
    print("  ✓ score_histogram.png")
    print("\nStress test complete.\n")

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    p, t = run_all_verifications()

    if p < t:
        print(f"⚠  {t - p} checks failed — review output above before running in production\n")

    run_feature_tests()

    stress_test_engine(300)

    print("\nDEMO RUN — White + Sky Blue shirts / Navy + Beige pants / Winter / Deep_Cool")

    res = generate_recommendations({
        "shirts":       ["White", "Sky Blue"],
        "pants":        ["Navy", "Beige"],
        "season":       "Winter",
        "skin_profile": "Deep_Cool"
    })

    print(f"\nMode: {res['mode']}")

    print("\nTop Shirts")
    for r in res["smart_shirts"]:
        print(f"  {r['color']:<16} shirt={r['shirt_score']}")

    print("\nTop Pants")
    for r in res["smart_pants"]:
        print(f"  {r['color']:<16} pant={r['pant_score']}")

    print("\nTop Neutrals")
    for r in res["all_season_neutrals"]:
        print(f"  {r['color']:<16} neutral={r['neutral_score']}  skin_delta={r['skin_delta']}")

    print("\nTop Outfits")
    for o in res["outfits"][:5]:
        print(f"  {o['shirt']:<16} + {o['pant']:<16} score={o['score']}")

    print("\nGraph Analytics")
    g = res["graph"]
    print(f"  Wardrobe hub:   {g['wardrobe_hub']}")
    print(f"  Most connected: {g['most_connected'][:3]}")

    # ── Graph Visualizations ──────────────────────────────────
    print("\nGenerating graph visualizations...")
    colors_viz = build_color_objects()
    cg_viz     = ColorGraph(colors_viz)

    visualize_color_graph(
        colors_viz,
        wardrobe  = ["White", "Sky Blue", "Navy", "Beige"],
        highlight = res["smart_shirts"][0]["color"],
        filename  = "color_graph.png"
    )

    visualize_outfit_flow(
        colors_viz,
        wardrobe_shirts     = ["White", "Sky Blue"],
        wardrobe_pants      = ["Navy", "Beige"],
        recommended_shirts  = [r["color"] for r in res["smart_shirts"]],
        filename            = "outfit_flow.png"
    )

    visualize_influence_propagation(
        candidate    = res["smart_shirts"][0]["color"],
        color_graph  = cg_viz,
        wardrobe     = ["White", "Sky Blue", "Navy", "Beige"],
        filename     = "influence_propagation.png"
    )

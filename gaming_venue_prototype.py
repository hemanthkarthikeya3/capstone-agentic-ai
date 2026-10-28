import os
import re
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Hyderabad Gaming Venue Finder",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("GOOGLE_PLACES_API_KEY")
CITY_CENTER = {"lat": 17.385044, "lng": 78.486671}

CATEGORY_LABELS = {
    "all": "All",
    "f1_sim": "F1 / Racing sim",
    "vr": "VR arcade",
    "gaming_pc": "Gaming PC café",
    "hybrid": "Hybrid gaming café",
    "cat_cafe": "Cat café",
    "board_game_cafe": "Board game café",
}

CATEGORY_KEYWORDS = {
    "f1_sim": ["f1", "racing sim", "sim racing", "simulator", "pit lane"],
    "vr": ["vr", "virtual reality", "virtual reality arcade"],
    "gaming_pc": ["gaming pc", "esports cafe", "pc cafe", "pc gaming", "computer cafe"],
    "hybrid": ["hybrid", "gaming lounge", "arcade", "gaming hub"],
    "cat_cafe": ["cat cafe", "cat lounge", "pet cafe", "cat lounge and cafe"],
    "board_game_cafe": ["board game", "board games", "boardgame", "tabletop", "tabletop cafe"],
}

CURATED_VENUES = [
    {
        "name": "Chrono Circuit",
        "area": "Gachibowli",
        "city": "Hyderabad",
        "lat": 17.4401,
        "lng": 78.3489,
        "category": "f1_sim",
        "price_per_hour": 1800,
        "rating": 4.8,
        "review_count": 412,
        "status": "open",
        "open_time": "12:00",
        "close_time": "23:30",
        "features": ["Motion sim", "Triple monitors", "Private F1 booth", "Group booking"],
        "specs": {"Wheel": "Fanatec ClubSport", "Display": "3x 27\" 144Hz", "GPU": "RTX 4080", "Seat": "Full racing cockpit"},
        "description": "Premium racing sim lounge with motion rigs and a social gaming atmosphere.",
        "image": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=80",
        "capacity": 6,
    },
    {
        "name": "Neon Drift VR",
        "area": "Madhapur",
        "city": "Hyderabad",
        "lat": 17.4403,
        "lng": 78.3914,
        "category": "vr",
        "price_per_hour": 1400,
        "rating": 4.7,
        "review_count": 298,
        "status": "busy",
        "open_time": "11:00",
        "close_time": "00:00",
        "features": ["VR arena", "Room-scale", "Co-op modes", "VR tournaments"],
        "specs": {"Headset": "Meta Quest 3", "Tracking": "Inside-out", "Space": "4x4m room scale", "Audio": "Spatial 3D"},
        "description": "Immersive VR arcade with arenas and social multiplayer rooms.",
        "image": "https://images.unsplash.com/photo-1598550476439-6847785fcea6?auto=format&fit=crop&w=1200&q=80",
        "capacity": 4,
    },
    {
        "name": "Pixel Forge",
        "area": "Kondapur",
        "city": "Hyderabad",
        "lat": 17.4579,
        "lng": 78.3656,
        "category": "gaming_pc",
        "price_per_hour": 900,
        "rating": 4.9,
        "review_count": 540,
        "status": "open",
        "open_time": "10:00",
        "close_time": "00:30",
        "features": ["RTX 4080", "240Hz display", "Streamer setups", "Esports room"],
        "specs": {"GPU": "RTX 4080", "CPU": "Intel i7-14700K", "Monitor": "27\" 240Hz", "Peripherals": "Mechanical + mouse"},
        "description": "High-end gaming PC cafe for serious players and casual sessions alike.",
        "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80",
        "capacity": 10,
    },
    {
        "name": "Arcade Fusion XL",
        "area": "Banjara Hills",
        "city": "Hyderabad",
        "lat": 17.4154,
        "lng": 78.4511,
        "category": "hybrid",
        "price_per_hour": 1500,
        "rating": 4.9,
        "review_count": 610,
        "status": "open",
        "open_time": "11:00",
        "close_time": "00:30",
        "features": ["Multi-zone", "VR bay", "F1 sim", "Gaming PC zone"],
        "specs": {"Zones": "3 zones", "Food": "Cafe service", "Events": "Night tournaments", "Capacity": "18 players"},
        "description": "Hybrid gaming venue that mixes sim racing, gaming PCs, and VR under one roof.",
        "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1200&q=80",
        "capacity": 18,
    },
    {
        "name": "Cat & Coder Lounge",
        "area": "Ameerpet",
        "city": "Hyderabad",
        "lat": 17.4375,
        "lng": 78.4485,
        "category": "cat_cafe",
        "price_per_hour": 700,
        "rating": 4.6,
        "review_count": 206,
        "status": "open",
        "open_time": "09:30",
        "close_time": "21:00",
        "features": ["Cat lounge", "Quiet room", "Board games", "Snacks and tea"],
        "specs": {"Pet zone": "Cat interaction zone", "Seating": "Quiet lounge", "Food": "Tea, snacks and desserts"},
        "description": "A cozy café with a cat lounge, relaxed social vibe, and quiet gaming corners.",
        "image": "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=1200&q=80",
        "capacity": 12,
    },
    {
        "name": "Board & Battle Hub",
        "area": "Jubilee Hills",
        "city": "Hyderabad",
        "lat": 17.4132,
        "lng": 78.4047,
        "category": "board_game_cafe",
        "price_per_hour": 550,
        "rating": 4.5,
        "review_count": 184,
        "status": "open",
        "open_time": "12:00",
        "close_time": "22:00",
        "features": ["Board game library", "Casual tournaments", "Tea and snacks", "Family-friendly"],
        "specs": {"Library": "200+ games", "Tables": "20+ tables", "Food": "Coffee and snacks"},
        "description": "Casual social cafe with a large board game library and welcoming vibes.",
        "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1200&q=80",
        "capacity": 20,
    },
    {
        "name": "Pitlane Masters",
        "area": "Secunderabad",
        "city": "Hyderabad",
        "lat": 17.4399,
        "lng": 78.4983,
        "category": "f1_sim",
        "price_per_hour": 2200,
        "rating": 4.8,
        "review_count": 360,
        "status": "maintenance",
        "open_time": "13:00",
        "close_time": "22:00",
        "features": ["Private booths", "Motion platform", "Competitive racing", "High FPS"],
        "specs": {"Wheel": "Moza R9", "Display": "2x 32\" 4K", "Motion": "Dynamic motion platform"},
        "description": "Private racing sim booths tuned for competitive play and tournament heat.",
        "image": "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?auto=format&fit=crop&w=1200&q=80",
        "capacity": 4,
    },
    {
        "name": "VR Paws & Play",
        "area": "Hitech City",
        "city": "Hyderabad",
        "lat": 17.4474,
        "lng": 78.3818,
        "category": "vr",
        "price_per_hour": 1200,
        "rating": 4.7,
        "review_count": 243,
        "status": "open",
        "open_time": "10:30",
        "close_time": "23:00",
        "features": ["Room-scale VR", "Multiplayer rooms", "Social lounge", "VR racing"],
        "specs": {"Headset": "Valve Index", "Tracking": "Laser tracking", "Space": "Large multiplayer room"},
        "description": "A social, multiplayer-first VR spot built for co-op and social play.",
        "image": "https://images.unsplash.com/photo-1560253023-3ec5d502959f?auto=format&fit=crop&w=1200&q=80",
        "capacity": 8,
    },
]


def status_color(status):
    return {
        "open": "#22c55e",
        "busy": "#fbbf24",
        "maintenance": "#ef4444",
        "closed": "#94a3b8",
    }.get(status, "#94a3b8")


def normalize_category(raw):
    text = (raw or "").lower()
    for key, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return key
    if "f1" in text or "racing" in text:
        return "f1_sim"
    if "vr" in text:
        return "vr"
    if "cat" in text:
        return "cat_cafe"
    if "board" in text or "tabletop" in text:
        return "board_game_cafe"
    if "pc" in text or "esports" in text:
        return "gaming_pc"
    return "hybrid"


def fetch_google_places():
    if not API_KEY:
        return []

    loc = f"{CITY_CENTER['lat']},{CITY_CENTER['lng']}"
    queries = [
        "f1 simulator Hyderabad",
        "vr arcade Hyderabad",
        "gaming pc cafe Hyderabad",
        "gaming lounge Hyderabad",
        "cat cafe Hyderabad",
        "board game cafe Hyderabad",
    ]

    results = []
    seen = set()
    for query in queries:
        try:
            resp = requests.get(
                "https://maps.googleapis.com/maps/api/place/textsearch/json",
                params={"query": query, "location": loc, "radius": 20000, "key": API_KEY},
                timeout=8,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for place in data.get("results", []):
                place_id = place.get("place_id")
                if not place_id or place_id in seen:
                    continue
                seen.add(place_id)
                address = place.get("formatted_address", "Hyderabad")
                area = address.split(",")[-3].strip() if "," in address and len(address.split(",")) > 2 else "Hyderabad"
                results.append({
                    "name": place.get("name"),
                    "area": area,
                    "city": "Hyderabad",
                    "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                    "lng": place.get("geometry", {}).get("location", {}).get("lng"),
                    "category": normalize_category(place.get("name", "") + " " + " ".join(place.get("types", []))),
                    "price_per_hour": 1200,
                    "rating": float(place.get("rating") or 4.2),
                    "review_count": int(place.get("user_ratings_total") or 80),
                    "status": "open" if place.get("opening_hours", {}).get("open_now") else "busy",
                    "open_time": "10:00",
                    "close_time": "23:00",
                    "features": ["Google Places listing", "Popular venue", place.get("types", ["Gaming venue"])[0].replace("_", " ").title()],
                    "specs": {"Source": "Google Places API", "Address": address},
                    "description": f"Google Places listing for {place.get('name', 'gaming venue')} in Hyderabad.",
                    "image": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=80",
                    "capacity": 6,
                })
        except Exception:
            continue
    return results


def venue_matches_query(venue, query):
    if not query:
        return True
    text = (
        f"{venue['name']} {venue['area']} {venue['city']} {venue['description']} "
        f"{' '.join(venue.get('features', []))} {' '.join(venue.get('specs', {}).keys())}"
    ).lower()
    return query.lower() in text


def filter_venues(venues, category, query, max_price, min_rating, open_only, min_capacity):
    results = []
    for venue in venues:
        if category != "all" and venue.get("category") != category:
            continue
        if query and not venue_matches_query(venue, query):
            continue
        if max_price and venue.get("price_per_hour", 0) > max_price:
            continue
        if min_rating and (venue.get("rating") or 0) < min_rating:
            continue
        if open_only and venue.get("status") != "open":
            continue
        if min_capacity and (venue.get("capacity") or 1) < min_capacity:
            continue
        results.append(venue)
    return sorted(results, key=lambda v: (-v.get("rating", 0), v.get("price_per_hour", 0)))


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root {
            --bg: #07111f;
            --panel: #0f1d2f;
            --panel-2: #12243d;
            --line: rgba(148, 163, 184, 0.18);
            --text: #e5eefb;
            --muted: #9fb5d1;
            --cyan: #62d0ff;
            --purple: #7c6bff;
            --green: #34d399;
            --amber: #fbbf24;
            --red: #ef4444;
            --shadow: 0 18px 45px rgba(8, 15, 30, 0.45);
        }
        html, body, [data-testid="stAppViewContainer"] { background: radial-gradient(circle at top left, rgba(124, 107, 255, 0.14), transparent 30%), radial-gradient(circle at top right, rgba(98, 208, 255, 0.10), transparent 26%), var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }
        .block-container { max-width: 1500px; padding-top: 1.2rem; padding-bottom: 2rem; }
        .hero { border-radius: 25px; padding: 30px 28px; background: linear-gradient(135deg, rgba(7,17,31,1) 0%, rgba(18,36,61,1) 100%); border: 1px solid var(--line); box-shadow: var(--shadow); }
        .hero-badge { display: inline-block; background: rgba(98, 208, 255, 0.12); border: 1px solid rgba(98, 208, 255, 0.3); color: var(--cyan); border-radius: 999px; padding: 8px 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
        h1 { font-size: 2.8rem !important; line-height: 1.05 !important; margin: 16px 0 10px !important; font-weight: 800 !important; letter-spacing: -0.06em !important; color: #f8fbff !important; }
        .hero p { color: var(--muted) !important; font-size: 1rem !important; margin: 0; }
        .status-row { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 18px; }
        .status-pill { display: inline-flex; align-items: center; gap: 8px; border-radius: 999px; padding: 8px 12px; font-size: 12px; font-weight: 600; background: rgba(15, 29, 47, 0.9); border: 1px solid var(--line); color: var(--text); }
        .status-dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; background: var(--green); box-shadow: 0 0 12px rgba(52, 211, 153, 0.85); }
        .venue-card { padding: 14px; margin-bottom: 18px; border-radius: 22px; background: linear-gradient(180deg, rgba(18,36,61,0.96), rgba(10,18,30,0.96)); border: 1px solid var(--line); box-shadow: var(--shadow); overflow: hidden; }
        .venue-image { height: 180px; width: 100%; object-fit: cover; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px; }
        .venue-name { font-size: 1.5rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.04em; color: white; }
        .muted { color: var(--muted) !important; }
        .tag { display: inline-flex; align-items: center; padding: 7px 11px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 0.03em; border: 1px solid var(--line); color: var(--text); background: rgba(255,255,255,0.04); margin-right: 8px; margin-bottom: 8px; }
        .price-box { display: inline-block; padding: 8px 12px; background: rgba(124, 107, 255, 0.12); border: 1px solid rgba(124, 107, 255, 0.35); border-radius: 12px; color: #d8d2ff; font-weight: 700; }
        .stButton > button { border-radius: 12px !important; padding: 0.7rem 1rem !important; background: linear-gradient(135deg, #7c6bff, #62d0ff) !important; border: none !important; color: white !important; font-weight: 700 !important; box-shadow: 0 10px 26px rgba(124, 107, 255, 0.3) !important; }
        .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 12px 28px rgba(98, 208, 255, 0.25) !important; }
        .stTextInput > div > div > input { background: rgba(15,29,47,0.96) !important; color: white !important; border: 1px solid var(--line) !important; border-radius: 14px !important; }
        .stSelectbox > div > div, .stMultiSelect > div > div { background: rgba(15,29,47,0.96) !important; color: var(--text) !important; border: 1px solid var(--line) !important; border-radius: 14px !important; }
        .stDataFrame { background: rgba(15,29,47,0.96); border: 1px solid var(--line); border-radius: 16px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def quick_ai_response(query):
    if not query:
        return "Tell me what you want: F1 sim, VR, gaming PC, hybrid café, cat café, or board games."
    text = query.lower()
    selected = []
    if any(k in text for k in ["f1", "racing", "sim"]):
        selected.append("f1_sim")
    if any(k in text for k in ["vr", "virtual reality"]):
        selected.append("vr")
    if any(k in text for k in ["pc", "esports", "computer"]):
        selected.append("gaming_pc")
    if any(k in text for k in ["cat", "pet", "cafe"]):
        selected.append("cat_cafe")
    if any(k in text for k in ["board", "tabletop"]):
        selected.append("board_game_cafe")
    if any(k in text for k in ["hybrid", "arcade", "multizone"]):
        selected.append("hybrid")
    if not selected:
        selected = ["f1_sim", "vr", "gaming_pc", "hybrid"]
    return selected


inject_css()

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">Hyderabad discovery</div>
        <h1>Find the best gaming café, VR arcade, and racing sim near you.</h1>
        <p>Search live-style venues in Hyderabad with premium filters, pricing, ratings, and AI-guided recommendations.</p>
        <div class="status-row">
            <span class="status-pill"><span class="status-dot"></span>Live-style filters</span>
            <span class="status-pill"><span class="status-dot"></span>Google Maps-ready prototype</span>
            <span class="status-pill"><span class="status-dot"></span>F1 / VR / PC / hybrid</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

venues = CURATED_VENUES + fetch_google_places()

with st.sidebar:
    st.header("Filters")
    query = st.text_input("Search venue or vibe", value=st.session_state.get("query", ""), placeholder="F1 sim, VR, gaming pc, cat cafe")
    st.session_state["query"] = query
    category = st.selectbox("Category", ["all"] + list(CATEGORY_LABELS.keys())[1:])
    max_price = st.slider("Max price / hour (₹)", 0, 2500, 2000, step=50)
    min_rating = st.slider("Min rating", 0.0, 5.0, 4.0, step=0.1)
    min_capacity = st.slider("Min capacity", 1, 25, 2, step=1)
    open_only = st.checkbox("Open now only", value=False)

    st.markdown("---")
    st.caption("Quick prompts")
    quick_prompts = [
        "F1 sim in Gachibowli",
        "VR arcade for 4 people",
        "Gaming PC under ₹1000",
        "Cat cafe with board games",
        "Hybrid cafe with VR and racing sim",
    ]
    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True):
            st.session_state["query"] = prompt
            query = prompt

    st.caption(f"Google Maps key loaded: {'Yes' if API_KEY else 'No (using curated fallback data)'}")

filtered = filter_venues(venues, category, query, max_price, min_rating, open_only, min_capacity)

stats1, stats2, stats3 = st.columns(3)
stats1.metric("Matches", len(filtered))
stats2.metric("Open now", sum(1 for v in filtered if v.get("status") == "open"))
stats3.metric("Avg rate", f"₹{int(sum(v.get('price_per_hour', 0) for v in filtered) / len(filtered)) if filtered else 0}/hr")

if not filtered:
    st.warning("No venues match. Try a broader search like 'VR', 'F1 sim', 'gaming PC', or 'hybrid gaming cafe'.")
else:
    left, right = st.columns([1.7, 1.0])

    with left:
        for venue in filtered:
            with st.container():
                st.markdown("<div class='venue-card'>", unsafe_allow_html=True)
                col_image, col_content = st.columns([1.05, 1.9])
                with col_image:
                    st.image(venue["image"], use_column_width=True)
                with col_content:
                    st.markdown(f"<div class='venue-name'>{venue['name']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='muted'>📍 {venue['area']} · {venue['city']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='price-box'>₹{venue['price_per_hour']}/hr</div>", unsafe_allow_html=True)
                    st.markdown(f"**Rating:** {venue['rating']} ★ · {venue['review_count']} reviews")
                    st.markdown(f"**Status:** <span style='color:{status_color(venue.get('status','open'))}; font-weight:700'>{venue.get('status','open').title()}</span>", unsafe_allow_html=True)
                    st.markdown(f"{venue.get('description', '')}")
                    for tag in venue.get("features", [])[:4]:
                        st.markdown(f"<span class='tag'>{tag}</span>", unsafe_allow_html=True)
                    specs = venue.get("specs", {})
                    if specs:
                        st.caption(" • ".join(f"{k}: {v}" for k, v in list(specs.items())[:3]))
                    b1, b2 = st.columns([1, 1])
                    if b1.button(f"Book {venue['name']}", key=f"book_{venue['name']}", use_container_width=True):
                        st.session_state["selected_venue"] = venue
                        st.success(f"{venue['name']} selected for booking.")
                    if b2.button("View details", key=f"details_{venue['name']}", use_container_width=True):
                        st.session_state["selected_venue"] = venue
                st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div style='background: rgba(15,29,47,0.96); border: 1px solid rgba(148,163,184,0.18); border-radius: 22px; padding: 18px;'>", unsafe_allow_html=True)
        st.subheader("Venue map preview")
        map_df = pd.DataFrame([
            {
                "lat": v.get("lat"),
                "lon": v.get("lng"),
                "name": v.get("name"),
                "category": v.get("category"),
                "rating": v.get("rating"),
            }
            for v in filtered[:25]
        ])
        if not map_df.empty:
            st.map(map_df)
        else:
            st.info("Map appears here once there are results.")
        st.markdown("</div>", unsafe_allow_html=True)

        if "selected_venue" in st.session_state:
            selected = st.session_state["selected_venue"]
            st.markdown("<div style='background: rgba(15,29,47,0.96); border: 1px solid rgba(148,163,184,0.18); border-radius: 22px; padding: 18px; margin-top: 18px;'>", unsafe_allow_html=True)
            st.subheader("Selected venue")
            st.markdown(f"## {selected['name']}")
            st.markdown(f"**Area:** {selected['area']} | **Type:** {CATEGORY_LABELS.get(selected.get('category'), selected.get('category'))}")
            st.markdown(f"**Price:** ₹{selected['price_per_hour']}/hr | **Rating:** {selected['rating']} ★")
            for item in selected.get("features", [])[:5]:
                st.markdown(f"- {item}")
            st.json(selected.get("specs", {}), expanded=False)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("AI concierge")
concierge_query = st.text_input("Ask for a venue recommendation", value="", placeholder="Example: I want a VR arcade for 4 people in Hyderabad under ₹1500")
if concierge_query:
    intent_map = quick_ai_response(concierge_query)
    matches = [v for v in filtered if v.get("category") in intent_map][:5]
    if not matches:
        matches = filtered[:5]
    for v in matches:
        st.markdown(f"- **{v['name']}** — {CATEGORY_LABELS.get(v.get('category'), v.get('category'))} — ₹{v['price_per_hour']}/hr — {v['rating']}★")

st.caption("Prototype note: if a Google Maps API key is added, it will fetch real places automatically; otherwise the app uses curated Hyderabad venue data to keep the demo working immediately.")

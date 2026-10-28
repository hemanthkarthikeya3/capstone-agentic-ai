import json
import re
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="Gaming Venue Finder",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)


PLACEHOLDER_IMAGE = "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=80"

VENUES = [
    {
        "id": "chrono-circuit",
        "name": "Chrono Circuit",
        "city": "Bengaluru",
        "category": "f1_sim",
        "venue_type": "Racing Sim Lounge",
        "description": "High-end F1 bays with motion, triple-monitor racing rigs and premium coffee service.",
        "tags": ["f1", "simulator", "multiplayer", "gaming_pc", "group", "food"],
        "features": ["Motion sim", "Triple monitors", "Steering wheel + pedals", "Group booking"],
        "specs": {
            "wheel": "Fanatec ClubSport",
            "display": "3x 27\" 144Hz",
            "cpu": "Ryzen 9 7950X",
            "gpu": "RTX 4080",
            "seat": "Full racing cockpit",
        },
        "price_per_hour": 1800,
        "capacity": 6,
        "rating": 4.8,
        "status": "open",
        "open_time": "12:00",
        "close_time": "23:30",
        "source": "Curated venue catalog",
        "image": PLACEHOLDER_IMAGE,
    },
    {
        "id": "vr-arcade-1",
        "name": "Neon Drift VR",
        "city": "Bengaluru",
        "category": "vr",
        "venue_type": "VR Arcade",
        "description": "VR pods for competitive and co-op play with immersive arena rooms and mixed reality zones.",
        "tags": ["vr", "arena", "multiplayer", "group", "gaming_pc"],
        "features": ["Quest 3 / headset", "Arena maps", "Co-op rooms", "Group-ready"],
        "specs": {
            "headset": "Meta Quest 3",
            "tracking": "Inside-out tracking",
            "space": "Room-scale 4x4m",
            "network": "5G-ready",
            "audio": "Spatial 3D audio",
        },
        "price_per_hour": 1400,
        "capacity": 4,
        "rating": 4.7,
        "status": "busy",
        "open_time": "11:00",
        "close_time": "00:00",
        "source": "Curated venue catalog",
        "image": PLACEHOLDER_IMAGE,
    },
    {
        "id": "pixel-lounge",
        "name": "Pixel Forge",
        "city": "Hyderabad",
        "category": "gaming_pc",
        "venue_type": "Gaming PC Lounge",
        "description": "Premium esports setups with high-refresh monitors, headphones, and budget-friendly hourly sessions.",
        "tags": ["gaming_pc", "esports", "multiplayer", "food", "streaming"],
        "features": ["RTX 4080", "144Hz monitors", "Mouse + keyboard", "Streamer setup"],
        "specs": {
            "gpu": "RTX 4080",
            "cpu": "Intel i7-14700K",
            "monitor": "27\" 240Hz",
            "network": "Fiber internet",
            "peripherals": "Mechanical keyboard + gaming mouse",
        },
        "price_per_hour": 900,
        "capacity": 10,
        "rating": 4.9,
        "status": "open",
        "open_time": "10:00",
        "close_time": "00:30",
        "source": "Curated venue catalog",
        "image": PLACEHOLDER_IMAGE,
    },
    {
        "id": "cat-and-coder",
        "name": "Cat & Coder Lounge",
        "city": "Pune",
        "category": "cat_cafe",
        "venue_type": "Cat Café",
        "description": "A relaxed space with a cat lounge, board games, snacks, and quiet gaming corners.",
        "tags": ["cats", "board_games", "coffee", "quiet", "food"],
        "features": ["Cat lounge", "Quiet room", "Board games", "Tea & snacks"],
        "specs": {
            "pet_zone": "Cat interaction zone",
            "seating": "Comfort lounge seating",
            "food": "Tea, snacks, desserts",
            "ambience": "Quiet and cozy",
        },
        "price_per_hour": 700,
        "capacity": 12,
        "rating": 4.6,
        "status": "open",
        "open_time": "09:30",
        "close_time": "21:00",
        "source": "Curated venue catalog",
        "image": PLACEHOLDER_IMAGE,
    },
    {
        "id": "board-battle-hub",
        "name": "Board & Battle Hub",
        "city": "Chennai",
        "category": "board_game_cafe",
        "venue_type": "Board Game Café",
        "description": "A hybrid café with tabletop games, quick tournaments, and casual social gaming nights.",
        "tags": ["board_games", "social", "food", "casual", "family"],
        "features": ["Tabletop library", "Casual tournaments", "Food service", "Family-friendly"],
        "specs": {
            "table_count": "20+ tables",
            "game_library": "200+ board games",
            "food_service": "Coffee and snacks",
            "social": "Live tournaments",
        },
        "price_per_hour": 550,
        "capacity": 20,
        "rating": 4.5,
        "status": "open",
        "open_time": "12:00",
        "close_time": "22:00",
        "source": "Curated venue catalog",
        "image": PLACEHOLDER_IMAGE,
    },
    {
        "id": "arcade-fusion",
        "name": "Arcade Fusion XL",
        "city": "Mumbai",
        "category": "hybrid",
        "venue_type": "Hybrid Gaming Café",
        "description": "A multi-zone venue combining gaming PCs, VR, racing simulators and group lounges.",
        "tags": ["gaming_pc", "vr", "f1", "simulator", "group", "food"],
        "features": ["Multi-zone", "VR bays", "Racing seats", "PC gaming"],
        "specs": {
            "zones": "3 zones",
            "seating": "Gaming lounges + sim pods",
            "food": "Cafe menu served",
            "events": "Night tournaments",
        },
        "price_per_hour": 1500,
        "capacity": 18,
        "rating": 4.9,
        "status": "open",
        "open_time": "11:00",
        "close_time": "00:30",
        "source": "Curated venue catalog",
        "image": PLACEHOLDER_IMAGE,
    },
    {
        "id": "f1-hub-2",
        "name": "Pitlane Masters",
        "city": "Delhi",
        "category": "f1_sim",
        "venue_type": "Racing Sim Studio",
        "description": "Competitive sim racing with custom steering rigs, motion feedback, and private booths.",
        "tags": ["f1", "simulator", "competitive", "group", "multiplayer"],
        "features": ["Private booths", "F1 wheels", "Motion feedback", "Fast lap contests"],
        "specs": {
            "wheel": "Moza R9",
            "display": "2x 32\" 4K",
            "motion": "Dynamic motion platform",
            "sound": "Surround audio",
        },
        "price_per_hour": 2200,
        "capacity": 4,
        "rating": 4.8,
        "status": "maintenance",
        "open_time": "13:00",
        "close_time": "22:00",
        "source": "Curated venue catalog",
        "image": PLACEHOLDER_IMAGE,
    },
    {
        "id": "vr-paws",
        "name": "VR Paws & Play",
        "city": "Kochi",
        "category": "vr",
        "venue_type": "VR + Social Lounge",
        "description": "A social lounge combining VR experiences, gaming sessions and pet-friendly seating zones.",
        "tags": ["vr", "social", "pets", "gaming_pc", "group"],
        "features": ["VR pods", "Pet-friendly seating", "Group rooms", "Social gaming"],
        "specs": {
            "headset": "Valve Index",
            "tracking": "Laser tracking",
            "space": "Large multiplayer room",
            "social": "Lounge seating",
        },
        "price_per_hour": 1200,
        "capacity": 8,
        "rating": 4.7,
        "status": "open",
        "open_time": "10:30",
        "close_time": "23:00",
        "source": "Curated venue catalog",
        "image": PLACEHOLDER_IMAGE,
    },
]


def venue_is_open(venue):
    now = datetime.now()
    open_h = int(venue["open_time"].split(":")[0])
    close_h = int(venue["close_time"].split(":")[0])
    current = now.hour
    if venue["status"] == "maintenance":
        return False, "Maintenance"
    open_now = open_h <= current < close_h
    return open_now, "Open now" if open_now else "Closed now"


def build_filters():
    category_options = [
        "all",
        "f1_sim",
        "vr",
        "gaming_pc",
        "cat_cafe",
        "board_game_cafe",
        "hybrid",
    ]
    tag_options = ["f1", "vr", "gaming_pc", "cats", "board_games", "food", "group", "multiplayer", "quiet"]
    return category_options, tag_options


def query_venues(query_text, category, selected_tags, max_price, min_rating, max_people):
    text = (query_text or "").lower().strip()
    results = []
    for venue in VENUES:
        tags = {t.lower() for t in venue["tags"]}
        name_tokens = f"{venue['name']} {venue['description']} {' '.join(venue['tags'])} {' '.join(venue['features'])}".lower()

        if category != "all" and venue["category"] != category:
            continue
        if selected_tags and not any(tag in tags for tag in selected_tags):
            continue
        if max_price and venue["price_per_hour"] > max_price:
            continue
        if min_rating and venue["rating"] < min_rating:
            continue
        if max_people and venue["capacity"] < max_people:
            continue
        if text:
            keywords = text.split()
            if not any(keyword in name_tokens for keyword in keywords):
                continue

        results.append(venue)

    return sorted(results, key=lambda v: (-v["rating"], v["price_per_hour"]))


def smart_concierge(query_text: str):
    text = (query_text or "").lower()
    selected_tags = []
    if "f1" in text or "formula" in text or "racing sim" in text:
        selected_tags.append("f1")
    if "vr" in text or "virtual reality" in text:
        selected_tags.append("vr")
    if "pc" in text or "esports" in text or "gaming pc" in text or "computer" in text:
        selected_tags.append("gaming_pc")
    if "cat" in text:
        selected_tags.append("cats")
    if "board game" in text or "tabletop" in text:
        selected_tags.append("board_games")
    if "food" in text or "coffee" in text:
        selected_tags.append("food")

    results = query_venues(text, "all", selected_tags, max_price=0, min_rating=0, max_people=0)
    if not results:
        return "I could not find a matching venue. Try a broader description like: 'f1 sim', 'vr', 'gaming pc', 'cat café', or 'board games'."

    top = results[:3]
    lines = []
    for venue in top:
        open_now, status = venue_is_open(venue)
        lines.append(f"- {venue['name']} ({venue['city']}) — {venue['venue_type']} — {status} — ₹{venue['price_per_hour']}/hr")
    return "\n".join(lines)


st.title("🎮 Gaming Venue Finder")
st.caption("Realtime-style venue discovery for cafes, simulators, VR, gaming PCs, and cat-friendly lounges.")

with st.sidebar:
    st.header("Filters")
    all_categories, all_tags = build_filters()
    category = st.selectbox("Venue type", all_categories, index=0)
    selected_tags = st.multiselect("Match features", all_tags)
    max_price = st.slider("Max price per hour (₹)", 0, 2500, 2000, step=100)
    min_rating = st.slider("Minimum rating", 0.0, 5.0, 4.0, step=0.1)
    max_people = st.slider("Minimum capacity", 1, 25, 2, step=1)

    st.markdown("---")
    st.subheader("Quick filters")
    quick_buttons = [
        "F1 sim",
        "VR",
        "Gaming PC",
        "Cat café",
        "Board games",
        "Hybrid",
    ]
    for button in quick_buttons:
        if st.button(button, use_container_width=True):
            st.session_state["query_text"] = button

    if "query_text" not in st.session_state:
        st.session_state["query_text"] = ""

query_input = st.text_input("Search venue or experience", value=st.session_state.get("query_text", ""), placeholder="Try: f1 sim, vr, gaming pc, cat café, board games")
st.session_state["query_text"] = query_input

results = query_venues(query_input, category, selected_tags, max_price, min_rating, max_people)

status_badges = {
    "open": "🟢 Open",
    "busy": "🟡 Busy",
    "maintenance": "🔴 Maintenance",
}

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Live matches", len(results))
with col2:
    st.metric("Open now", sum(1 for v in results if venue_is_open(v)[0]))
with col3:
    st.metric("Avg rate / hr", f"₹{int(sum(v['price_per_hour'] for v in results) / len(results)) if results else 0}")

if not results:
    st.warning("No venue matches the filters. Try a broader keyword like 'VR', 'F1 sim', 'gaming PC', 'cat café', or 'board games'.")
else:
    for venue in results:
        open_now, status = venue_is_open(venue)
        with st.container():
            st.markdown("---")
            left, right = st.columns([1.4, 2.2])
            with left:
                st.image(venue["image"], use_column_width=True)
            with right:
                st.markdown(f"## {venue['name']}")
                st.markdown(
                    f"**{venue['venue_type']}** · {venue['city']} · {status_badges.get(venue['status'], '⚪ Unknown')}"
                )
                st.markdown(f"{venue['description']}")
                st.markdown(f"**Price:** ₹{venue['price_per_hour']}/hour | **Capacity:** {venue['capacity']} | **Rating:** {venue['rating']} ★")
                st.markdown(f"**Open:** {venue['open_time']} - {venue['close_time']} | **Status:** {status}")
                st.markdown("**Features:** " + " • ".join(venue["features"]))
                st.markdown("**Tags:** " + " • ".join(venue["tags"]))
                st.json(venue["specs"], expanded=False)
                if st.button(f"Book {venue['name']}", key=f"book_{venue['id']}", use_container_width=True):
                    st.session_state["last_booking"] = venue["name"]
                    st.success(f"{venue['name']} selected for booking. Add a time slot in your booking flow next.")

st.markdown("---")
st.subheader("AI concierge")
if st.button("Find best match for my vibe"):
    st.write(smart_concierge(query_input or "best gaming venue for group of 4 with f1 and vr"))

user_question = st.text_input("Ask the venue concierge", value="", placeholder="Example: I want a gaming cafe with F1 simulators and VR for 4 people")
if user_question:
    st.info(smart_concierge(user_question))

st.markdown("---")
st.caption("Prototype note: this uses a curated venue catalog and live-time status simulation. For production, connect to official venue APIs and booking data sources.")

if "last_booking" in st.session_state:
    st.caption(f"Last selected: {st.session_state['last_booking']}")

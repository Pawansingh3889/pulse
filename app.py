"""Pulse — Your personal AI briefing assistant.

Tech, military, world politics, hiking/travel suggestions, and live football scores.
Powered by Ollama (local AI) + free APIs. No cloud. No tracking.

Usage:
    streamlit run app.py
"""
import streamlit as st
import requests
import json
from datetime import datetime

# ── Config ──
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:12b"
NEWS_API = "https://newsdata.io/api/1/latest"  # free tier, 200 req/day
FOOTBALL_API = "https://v3.football.api-sports.io"

st.set_page_config(page_title="Pulse", page_icon="⚡", layout="wide")


def ask_ollama(prompt, context=""):
    """Ask local Ollama model."""
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": f"{context}\n\n{prompt}",
            "stream": False,
        }, timeout=120)
        return resp.json().get("response", "No response from Ollama")
    except requests.exceptions.ConnectionError:
        return "Ollama not running. Start it with: ollama serve"
    except Exception as e:
        return f"Error: {e}"


def fetch_news(category, query=""):
    """Fetch news from free RSS/API sources."""
    feeds = {
        "tech": [
            ("Hacker News Top", "https://hacker-news.firebaseio.com/v0/topstories.json"),
        ],
        "military": [
            ("Defense keyword", "military defense"),
        ],
        "politics": [
            ("World politics", "world politics"),
        ],
    }

    # Use Hacker News API (free, no key needed)
    if category == "tech":
        try:
            resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
            ids = resp.json()[:10]
            stories = []
            for sid in ids:
                story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
                if story and story.get("title"):
                    stories.append({
                        "title": story["title"],
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "score": story.get("score", 0),
                        "comments": story.get("descendants", 0),
                    })
            return stories
        except:
            return []

    # For military/politics — use Reddit JSON (free, no key)
    subreddit = {
        "military": "military+defense+geopolitics",
        "politics": "worldnews+geopolitics+worldpolitics",
    }.get(category, "worldnews")

    try:
        resp = requests.get(
            f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10",
            headers={"User-Agent": "Pulse/1.0"}, timeout=10
        )
        posts = resp.json()["data"]["children"]
        return [{
            "title": p["data"]["title"],
            "url": f"https://reddit.com{p['data']['permalink']}",
            "score": p["data"]["score"],
            "comments": p["data"]["num_comments"],
        } for p in posts if not p["data"].get("stickied")]
    except:
        return []


def fetch_football():
    """Fetch EPL and Champions League scores from free sources."""
    results = []

    # Use ESPN free endpoint
    leagues = {
        "Premier League": "eng.1",
        "Champions League": "uefa.champions",
    }

    for league_name, league_code in leagues.items():
        try:
            resp = requests.get(
                f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard",
                timeout=10
            )
            data = resp.json()
            events = data.get("events", [])
            for event in events[:5]:
                competition = event.get("competitions", [{}])[0]
                competitors = competition.get("competitors", [])
                if len(competitors) == 2:
                    home = competitors[0]
                    away = competitors[1]
                    results.append({
                        "league": league_name,
                        "home": home["team"]["displayName"],
                        "home_score": home.get("score", "-"),
                        "away": away["team"]["displayName"],
                        "away_score": away.get("score", "-"),
                        "status": event.get("status", {}).get("type", {}).get("shortDetail", ""),
                        "date": event.get("date", ""),
                    })
        except:
            pass

    return results


HIKING_DATA = [
    {"name": "Ingleborough", "region": "Yorkshire Dales", "difficulty": "Moderate", "distance": "11.5 km", "time": "4-5 hrs",
     "description": "One of Yorkshire's Three Peaks. Limestone pavements and views across the Dales."},
    {"name": "Pen-y-ghent", "region": "Yorkshire Dales", "difficulty": "Moderate", "distance": "9.5 km", "time": "3-4 hrs",
     "description": "The smallest of the Three Peaks but steep and rewarding. Great for beginners pushing their limits."},
    {"name": "Whernside", "region": "Yorkshire Dales", "difficulty": "Moderate-Hard", "distance": "12 km", "time": "5-6 hrs",
     "description": "Highest point in Yorkshire at 736m. Long ridge walk with views to Morecambe Bay."},
    {"name": "Malham Cove", "region": "Yorkshire Dales", "difficulty": "Easy", "distance": "6 km", "time": "2-3 hrs",
     "description": "Stunning limestone amphitheatre. Easy walk from Malham village. Perfect for a half day."},
    {"name": "Snowdon (Yr Wyddfa)", "region": "Snowdonia, Wales", "difficulty": "Moderate-Hard", "distance": "14.5 km", "time": "5-7 hrs",
     "description": "Highest mountain in Wales at 1085m. Multiple routes — Llanberis Path is the easiest."},
    {"name": "Helvellyn via Striding Edge", "region": "Lake District", "difficulty": "Hard", "distance": "13 km", "time": "6-7 hrs",
     "description": "England's most famous ridge walk. Scrambling required. Not for beginners."},
    {"name": "Scafell Pike", "region": "Lake District", "difficulty": "Hard", "distance": "14 km", "time": "6-8 hrs",
     "description": "England's highest peak at 978m. Rocky terrain. Corridor Route is the most popular."},
    {"name": "Cat Bells", "region": "Lake District", "difficulty": "Easy", "distance": "6 km", "time": "2-3 hrs",
     "description": "Perfect family-friendly fell walk above Derwentwater. Stunning views for minimal effort."},
    {"name": "Ben Nevis", "region": "Scottish Highlands", "difficulty": "Hard", "distance": "17 km", "time": "7-9 hrs",
     "description": "UK's highest mountain at 1345m. Mountain Path is the tourist route. Weather can change fast."},
    {"name": "Kedarnath Trek", "region": "Uttarakhand, India", "difficulty": "Moderate", "distance": "22 km", "time": "2 days",
     "description": "Sacred Hindu pilgrimage trek at 3583m. Your home state. Best: May-June, Sep-Oct."},
    {"name": "Valley of Flowers", "region": "Uttarakhand, India", "difficulty": "Moderate", "distance": "34 km", "time": "4-5 days",
     "description": "UNESCO World Heritage Site. Alpine meadows with rare Himalayan flowers. Best: July-September."},
    {"name": "Roopkund Trek", "region": "Uttarakhand, India", "difficulty": "Hard", "distance": "53 km", "time": "7-8 days",
     "description": "Mystery Lake at 5029m with ancient human skeletons. One of India's most thrilling treks."},
]

TRAVEL_SUGGESTIONS = [
    {"destination": "Edinburgh, Scotland", "type": "Weekend", "budget": "Low",
     "why": "Train from Yorkshire. Arthur's Seat hike, Royal Mile, free museums."},
    {"destination": "Lake District", "type": "Weekend", "budget": "Low",
     "why": "2 hours from Yorkshire. Cat Bells, Helvellyn, Windermere."},
    {"destination": "Snowdonia, Wales", "type": "Weekend", "budget": "Medium",
     "why": "Snowdon summit. Portmeirion village. Zip World if you want adrenaline."},
    {"destination": "Iceland", "type": "Week", "budget": "Medium-High",
     "why": "Blue Lagoon, Golden Circle, northern lights. Direct flights from Manchester."},
    {"destination": "Rishikesh, India", "type": "Week", "budget": "Low",
     "why": "Your roots — white water rafting, bungee jumping, yoga. Gateway to Himalayan treks."},
    {"destination": "Norway", "type": "Week", "budget": "High",
     "why": "Trolltunga hike, fjords, midnight sun in summer. Stunning for a hiking trip."},
    {"destination": "Scottish Highlands", "type": "Long Weekend", "budget": "Medium",
     "why": "Ben Nevis, Glen Coe, Isle of Skye. Wild camping is legal in Scotland."},
    {"destination": "Dolomites, Italy", "type": "Week", "budget": "Medium",
     "why": "Tre Cime di Lavaredo, Alta Via trails. Accessible by budget flight to Venice."},
]


# ── UI ──
st.markdown("""
<style>
    .stApp { background-color: #0f172a; }
    .news-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; margin-bottom: 8px; }
    .score-card { background: #1e293b; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 12px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("Pulse")
st.caption("Tech. Military. Politics. Football. Hiking. All local. All private.")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Yorkshire", "Tech News", "Military & Defense", "World Politics", "Football", "Hiking & Travel", "Ask AI"
])

# ── TAB 0: Yorkshire ──
with tab1:
    from uk_data import (get_weather, get_yorkshire_demographics, get_yorkshire_finance,
                         get_gov_schemes, get_housing_data, get_election_results,
                         get_school_data, get_jobs_exams)

    st.subheader("Yorkshire & Nearby — Live Data")

    # Weather
    st.markdown("#### Weather")
    wcol1, wcol2, wcol3 = st.columns(3)
    locations = ["York", "Leeds", "Sheffield", "Harrogate", "Scarborough", "Hull",
                 "Bradford", "Whitby", "Middlesbrough", "Wakefield", "Huddersfield", "Doncaster"]
    selected = st.multiselect("Select locations", locations, default=["York", "Leeds", "Sheffield"])

    for loc in selected:
        w = get_weather(loc)
        if "error" not in w:
            st.markdown(f"""
            <div class="score-card">
                <span style="color: #60a5fa; font-weight: 700; font-size: 16px;">{w['location']}</span>
                <span style="color: white; font-size: 24px; font-weight: 700; margin-left: 16px;">{w['temp']}C</span>
                <span style="color: #94a3b8; margin-left: 8px;">{w['condition']}</span>
                <span style="color: #64748b; margin-left: 16px;">Humidity: {w['humidity']}% | Wind: {w['wind']} km/h</span>
            </div>
            """, unsafe_allow_html=True)

            # 7-day forecast
            if w.get("forecast"):
                cols = st.columns(7)
                for i, f in enumerate(w["forecast"]):
                    with cols[i]:
                        st.metric(f["date"][5:], f"{f['max']}C", f"{f['rain']}mm rain")

    st.divider()

    # Population
    st.markdown("#### Population & Demographics")
    demo = get_yorkshire_demographics()
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Population", f"{demo['population']['total']:,}")
    d2.metric("Employment Rate", demo['employment_rate'])
    d3.metric("Median Salary", f"GBP {demo['median_salary']:,}")
    d4.metric("Literacy Rate", demo['literacy_rate'].split('(')[0])

    st.markdown("**City Populations**")
    pop_data = demo['population']['cities']
    cols = st.columns(4)
    for i, (city, pop) in enumerate(sorted(pop_data.items(), key=lambda x: -x[1])):
        with cols[i % 4]:
            st.metric(city, f"{pop:,}")

    st.divider()

    # Finance
    st.markdown("#### Council Budgets & Spending")
    finance = get_yorkshire_finance()
    for council in finance['councils']:
        with st.expander(f"{council['name']} — Budget: GBP {council['budget_2024_25']} | Council Tax Band D: GBP {council['council_tax_band_d']:,}"):
            for area, pct in council['key_spend'].items():
                st.write(f"- {area.replace('_', ' ').title()}: **{pct}**")

    st.divider()

    # Housing
    st.markdown("#### Housing Market")
    housing = get_housing_data()
    h_cols = st.columns(4)
    for i, (area, price) in enumerate(sorted(housing['average_prices'].items(), key=lambda x: -x[1])):
        with h_cols[i % 4]:
            diff = price - housing['average_prices'].get('UK Average', 295000)
            st.metric(area, f"GBP {price:,}", f"{diff:+,} vs UK avg" if area != "UK Average" else "")

    if housing.get('council_housing_waiting_list'):
        st.markdown("**Council Housing Waiting List**")
        wl_cols = st.columns(4)
        for i, (city, count) in enumerate(housing['council_housing_waiting_list'].items()):
            with wl_cols[i % 4]:
                st.metric(city, f"{count:,} families")

    st.divider()

    # Government Schemes
    st.markdown("#### Government Schemes & Benefits")
    schemes = get_gov_schemes()
    for s in schemes:
        st.markdown(f"""
        <div class="news-card">
            <a href="{s['link']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">{s['name']}</a>
            <br><span style="color: #94a3b8; font-size: 12px;">{s['who']}</span>
            <br><span style="color: #22c55e; font-weight: 600;">GBP {s['amount']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Elections
    st.markdown("#### Election Results")
    elections = get_election_results()
    ge = elections['general_election_2024']
    st.markdown(f"**General Election {ge['date']}** — {ge['yorkshire_summary']}")
    for r in ge['yorkshire_results']:
        color = {"Labour": "#e11d48", "Conservative": "#2563eb", "Independent": "#8b5cf6", "Green": "#22c55e"}.get(r['party'], "#64748b")
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 4px 0;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background: {color}; margin-right: 8px;"></span>
            <span style="color: white; width: 220px;">{r['constituency']}</span>
            <span style="color: #94a3b8; width: 180px;">{r['winner']}</span>
            <span style="color: {color}; font-weight: 600; width: 120px;">{r['party']}</span>
            <span style="color: #64748b;">Majority: {r['majority']:,}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Schools
    st.markdown("#### Schools & Education")
    schools = get_school_data()
    s_cols = st.columns(5)
    s_cols[0].metric("Total Schools", f"{schools['stats']['total_schools_yorkshire']:,}")
    s_cols[1].metric("Primary", f"{schools['stats']['primary']:,}")
    s_cols[2].metric("Secondary", f"{schools['stats']['secondary']:,}")
    s_cols[3].metric("Outstanding", schools['ofsted_ratings_yorkshire']['outstanding'])
    s_cols[4].metric("Good", schools['ofsted_ratings_yorkshire']['good'])

    st.markdown("**Universities**")
    st.write(" | ".join(schools['stats']['universities']))

    st.divider()

    # Jobs & Exams
    st.markdown("#### Jobs & Exams")
    je = get_jobs_exams()

    j_col1, j_col2 = st.columns(2)
    with j_col1:
        st.markdown("**Job Sites**")
        for j in je['job_sites']:
            st.markdown(f"- [{j['name']}]({j['url']}) — {j['focus']}")

    with j_col2:
        st.markdown("**Upcoming Exams & Certifications**")
        for e in je['upcoming_exams']:
            st.markdown(f"- [{e['exam']}]({e['url']}) — {e.get('deadline', e.get('type', ''))}")

    st.markdown("**Major Employers in Yorkshire**")
    st.write(" | ".join(je['major_employers_yorkshire']))

# ── TAB: Tech ──
with tab2:
    st.subheader("Tech News (Hacker News)")
    if st.button("Refresh Tech", key="tech"):
        st.rerun()
    stories = fetch_news("tech")
    if stories:
        for s in stories:
            st.markdown(f"""
            <div class="news-card">
                <a href="{s['url']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">{s['title']}</a>
                <br><span style="color: #64748b; font-size: 12px;">Score: {s['score']} | Comments: {s['comments']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Could not fetch news. Check internet connection.")

# ── TAB: Military ──
with tab3:
    st.subheader("Military & Defense")
    if st.button("Refresh Military", key="mil"):
        st.rerun()
    posts = fetch_news("military")
    if posts:
        for p in posts:
            st.markdown(f"""
            <div class="news-card">
                <a href="{p['url']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">{p['title']}</a>
                <br><span style="color: #64748b; font-size: 12px;">Upvotes: {p['score']} | Comments: {p['comments']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Could not fetch military news.")

# ── TAB: Politics ──
with tab4:
    st.subheader("World Politics")
    if st.button("Refresh Politics", key="pol"):
        st.rerun()
    posts = fetch_news("politics")
    if posts:
        for p in posts:
            st.markdown(f"""
            <div class="news-card">
                <a href="{p['url']}" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">{p['title']}</a>
                <br><span style="color: #64748b; font-size: 12px;">Upvotes: {p['score']} | Comments: {p['comments']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Could not fetch political news.")

# ── TAB: Football ──
with tab5:
    st.subheader("EPL & Champions League")
    if st.button("Refresh Scores", key="foot"):
        st.rerun()
    matches = fetch_football()
    if matches:
        for m in matches:
            st.markdown(f"""
            <div class="score-card">
                <span style="color: #94a3b8; font-size: 11px;">{m['league']} | {m['status']}</span><br>
                <span style="color: white; font-size: 18px; font-weight: 700;">{m['home']} {m['home_score']} - {m['away_score']} {m['away']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No matches today. Check back on matchday.")

# ── TAB: Hiking & Travel ──
with tab6:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hiking Suggestions")
        difficulty = st.selectbox("Filter by difficulty", ["All", "Easy", "Moderate", "Moderate-Hard", "Hard"])
        region = st.selectbox("Filter by region", ["All"] + sorted(set(h["region"] for h in HIKING_DATA)))

        filtered = HIKING_DATA
        if difficulty != "All":
            filtered = [h for h in filtered if h["difficulty"] == difficulty]
        if region != "All":
            filtered = [h for h in filtered if h["region"] == region]

        for h in filtered:
            color = {"Easy": "#22c55e", "Moderate": "#f59e0b", "Moderate-Hard": "#f97316", "Hard": "#ef4444"}.get(h["difficulty"], "#64748b")
            st.markdown(f"""
            <div class="news-card">
                <span style="color: white; font-size: 16px; font-weight: 600;">{h['name']}</span>
                <span style="background: {color}22; color: {color}; border: 1px solid {color}44; border-radius: 20px; padding: 2px 10px; font-size: 11px; margin-left: 8px;">{h['difficulty']}</span>
                <br><span style="color: #94a3b8; font-size: 12px;">{h['region']} | {h['distance']} | {h['time']}</span>
                <br><span style="color: #cbd5e1; font-size: 13px;">{h['description']}</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("Travel Ideas")
        budget = st.selectbox("Budget", ["All", "Low", "Medium", "Medium-High", "High"])

        filtered_travel = TRAVEL_SUGGESTIONS
        if budget != "All":
            filtered_travel = [t for t in filtered_travel if t["budget"] == budget]

        for t in filtered_travel:
            st.markdown(f"""
            <div class="news-card">
                <span style="color: white; font-size: 16px; font-weight: 600;">{t['destination']}</span>
                <span style="background: #3b82f622; color: #60a5fa; border: 1px solid #3b82f644; border-radius: 20px; padding: 2px 10px; font-size: 11px; margin-left: 8px;">{t['type']} | {t['budget']}</span>
                <br><span style="color: #cbd5e1; font-size: 13px; margin-top: 4px;">{t['why']}</span>
            </div>
            """, unsafe_allow_html=True)

# ── TAB: Ask AI ──
with tab7:
    st.subheader("Ask Anything (Local AI)")
    st.caption(f"Powered by {MODEL} via Ollama. Everything stays on your machine.")

    topic = st.selectbox("Context", [
        "General",
        "Tech & Programming",
        "Military & Defense",
        "World Politics",
        "Hiking & Outdoors",
        "Football Analysis",
        "Travel Planning",
    ])

    question = st.text_area("Your question", placeholder="e.g., Compare Ingleborough vs Pen-y-ghent for a day hike")

    if st.button("Ask", type="primary") and question:
        with st.spinner("Thinking..."):
            context = {
                "General": "You are a helpful assistant.",
                "Tech & Programming": "You are a senior software engineer. Give concise, practical answers.",
                "Military & Defense": "You are a defense analyst. Provide factual, balanced analysis.",
                "World Politics": "You are a geopolitical analyst. Provide balanced, factual analysis without bias.",
                "Hiking & Outdoors": "You are an experienced UK and Himalayan hiker. Give practical trail advice with safety tips.",
                "Football Analysis": "You are a football analyst covering the Premier League and Champions League. Give factual match analysis.",
                "Travel Planning": "You are a budget travel advisor for someone based in Yorkshire, UK. Suggest practical trips.",
            }.get(topic, "You are a helpful assistant.")

            answer = ask_ollama(question, context)
            st.markdown(answer)

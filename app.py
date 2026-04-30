import streamlit as st
import json
import os

st.set_page_config(
    page_title="School Election",
    page_icon="🗳️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = "election_data.json"
ADMIN_PASSWORD = "school2025"   # ← Change this!

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "election_title": "Student Council Election 2025",
        "candidates": [
            {"id": 1, "name": "Arjun Sharma",  "position": "Class President"},
            {"id": 2, "name": "Priya Nair",    "position": "Class President"},
            {"id": 3, "name": "Rahul Mehta",   "position": "Class President"},
        ],
        "votes": {},
        "results_unlocked": False,
        "next_id": 4,
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def total_votes(data):
    return sum(data["votes"].values())

def get_initials(name):
    parts = name.strip().split()
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()

AVATAR_COLORS = [
    ("#B5D4F4", "#0C447C"), ("#9FE1CB", "#085041"),
    ("#F5C4B3", "#712B13"), ("#FAC775", "#633806"),
    ("#F4C0D1", "#72243E"), ("#CECBF6", "#3C3489"),
]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 1rem 4rem; max-width: 480px; margin: auto; }
.vote-card {
    background: #fff; border: 1.5px solid #e5e5e5;
    border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;
    display: flex; align-items: center; gap: 14px;
}
.vote-card.selected { border: 2px solid #185FA5; background: #EAF3FF; }
.avatar {
    width: 46px; height: 46px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 600; font-size: 16px; flex-shrink: 0;
}
.candidate-name { font-weight: 500; font-size: 16px; color: #111; }
.candidate-pos  { font-size: 13px; color: #777; }
.badge { display: inline-block; font-size: 12px; padding: 3px 10px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
.badge-blue  { background: #E6F1FB; color: #185FA5; }
.badge-green { background: #EAF3DE; color: #3B6D11; }
.badge-amber { background: #FAEEDA; color: #854F0B; }
.result-wrap { margin-bottom: 16px; }
.result-header { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 6px; color: #111; }
.result-track { height: 10px; background: #eee; border-radius: 99px; overflow: hidden; }
.result-fill  { height: 100%; border-radius: 99px; }
.stat-card { background: #f7f7f7; border-radius: 12px; padding: 14px 18px; text-align: center; margin-bottom: 12px; }
.stat-num { font-size: 32px; font-weight: 600; color: #111; }
.stat-lbl { font-size: 13px; color: #777; margin-top: 2px; }
.div { border-top: 1px solid #eee; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

if "screen" not in st.session_state:
    st.session_state.screen = "home"
if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "voted_name" not in st.session_state:
    st.session_state.voted_name = ""

data = load_data()

# ── HOME ──────────────────────────────────────────────────────────────────────
if st.session_state.screen == "home":
    st.markdown("### 🗳️ " + data["election_title"])
    if data["results_unlocked"]:
        st.markdown('<span class="badge badge-green">Results available</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-blue">Voting is open</span>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="stat-card"><div class="stat-num">{total_votes(data)}</div>'
        f'<div class="stat-lbl">votes cast so far</div></div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        if data["results_unlocked"]:
            if st.button("📊 View Results", use_container_width=True, type="primary"):
                st.session_state.screen = "results"
                st.rerun()
        else:
            if st.button("🗳️ Vote Now", use_container_width=True, type="primary"):
                st.session_state.screen = "vote"
                st.session_state.selected_candidate = None
                st.rerun()
    with col2:
        if st.button("⚙️ Admin", use_container_width=True):
            st.session_state.screen = "admin_login" if not st.session_state.admin_logged_in else "admin"
            st.rerun()

# ── VOTE ──────────────────────────────────────────────────────────────────────
elif st.session_state.screen == "vote":
    st.markdown('<span class="badge badge-blue">Voting booth</span>', unsafe_allow_html=True)
    st.markdown("### Choose your candidate")
    st.markdown("Tap a candidate to select, then enter your name and submit.")

    for i, c in enumerate(data["candidates"]):
        bg, fg = AVATAR_COLORS[i % len(AVATAR_COLORS)]
        is_sel = st.session_state.selected_candidate == c["id"]
        card_class = "vote-card selected" if is_sel else "vote-card"
        check = "✅ " if is_sel else ""
        st.markdown(
            f'<div class="{card_class}">'
            f'<div class="avatar" style="background:{bg};color:{fg}">{get_initials(c["name"])}</div>'
            f'<div><div class="candidate-name">{check}{c["name"]}</div>'
            f'<div class="candidate-pos">{c["position"]}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button(f"Select {c['name']}", key=f"sel_{c['id']}", use_container_width=True):
            st.session_state.selected_candidate = c["id"]
            st.rerun()

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    voter_name = st.text_input("Your name", placeholder="e.g. Chinmay Kumar")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Submit Vote", type="primary", use_container_width=True):
            if not st.session_state.selected_candidate:
                st.error("Please select a candidate first.")
            elif not voter_name.strip():
                st.error("Please enter your name.")
            else:
                cid = str(st.session_state.selected_candidate)
                data["votes"][cid] = data["votes"].get(cid, 0) + 1
                save_data(data)
                st.session_state.voted_name = voter_name.strip()
                st.session_state.selected_candidate = None
                st.session_state.screen = "voted"
                st.rerun()
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()

# ── VOTED ─────────────────────────────────────────────────────────────────────
elif st.session_state.screen == "voted":
    st.markdown('<span class="badge badge-green">Vote recorded</span>', unsafe_allow_html=True)
    st.markdown("## ✅ Thank you!")
    st.success(
        f"Your vote has been recorded, **{st.session_state.voted_name}**. "
        "Results will be shown once the teacher unlocks them."
    )
    st.markdown(
        f'<div class="stat-card"><div class="stat-num">{total_votes(data)}</div>'
        f'<div class="stat-lbl">total votes cast</div></div>',
        unsafe_allow_html=True,
    )
    if st.button("← Hand device to next voter", type="primary", use_container_width=True):
        st.session_state.screen = "home"
        st.session_state.voted_name = ""
        st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────────────
elif st.session_state.screen == "results":
    st.markdown('<span class="badge badge-green">Results</span>', unsafe_allow_html=True)
    st.markdown(f"### {data['election_title']} — Results")

    total = total_votes(data)
    if total == 0:
        st.info("No votes have been cast yet.")
    else:
        sorted_candidates = sorted(
            data["candidates"],
            key=lambda c: data["votes"].get(str(c["id"]), 0),
            reverse=True,
        )
        max_votes = data["votes"].get(str(sorted_candidates[0]["id"]), 0)
        for rank, c in enumerate(sorted_candidates):
            v = data["votes"].get(str(c["id"]), 0)
            pct = round((v / total) * 100) if total else 0
            is_winner = (v == max_votes and v > 0)
            fill_color = "#1D9E75" if is_winner else "#185FA5"
            label = f"🏆 {c['name']}" if is_winner and rank == 0 else c["name"]
            st.markdown(
                f'<div class="result-wrap">'
                f'<div class="result-header"><span>{label}</span><span>{v} vote{"s" if v!=1 else ""} ({pct}%)</span></div>'
                f'<div class="result-track"><div class="result-fill" style="width:{pct}%;background:{fill_color}"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown(f"**Total votes cast:** {total}")

    if st.button("← Back to home", use_container_width=True):
        st.session_state.screen = "home"
        st.rerun()

# ── ADMIN LOGIN ───────────────────────────────────────────────────────────────
elif st.session_state.screen == "admin_login":
    st.markdown('<span class="badge badge-amber">Admin login</span>', unsafe_allow_html=True)
    st.markdown("### ⚙️ Admin access")
    pwd = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", type="primary", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.session_state.screen = "admin"
                st.rerun()
            else:
                st.error("Incorrect password.")
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()

# ── ADMIN PANEL ───────────────────────────────────────────────────────────────
elif st.session_state.screen == "admin":
    if not st.session_state.admin_logged_in:
        st.session_state.screen = "admin_login"
        st.rerun()

    st.markdown('<span class="badge badge-amber">Admin panel</span>', unsafe_allow_html=True)
    st.markdown("### ⚙️ Admin panel")

    tab1, tab2, tab3 = st.tabs(["👥 Candidates", "📋 Election", "📊 Vote data"])

    with tab1:
        st.markdown("**Current candidates**")
        for c in data["candidates"]:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{c['name']}** — {c['position']} ({data['votes'].get(str(c['id']), 0)} votes)")
            with col2:
                if st.button("Remove", key=f"rm_{c['id']}"):
                    data["candidates"] = [x for x in data["candidates"] if x["id"] != c["id"]]
                    data["votes"].pop(str(c["id"]), None)
                    save_data(data)
                    st.rerun()
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        st.markdown("**Add candidate**")
        new_name = st.text_input("Full name", key="new_name")
        new_pos  = st.text_input("Position", key="new_pos")
        if st.button("➕ Add candidate", type="primary"):
            if new_name.strip() and new_pos.strip():
                data["candidates"].append({"id": data["next_id"], "name": new_name.strip(), "position": new_pos.strip()})
                data["next_id"] += 1
                save_data(data)
                st.success("Candidate added!")
                st.rerun()
            else:
                st.error("Enter both name and position.")

    with tab2:
        st.markdown("**Election title**")
        new_title = st.text_input("Title", value=data["election_title"])
        if st.button("Save title"):
            data["election_title"] = new_title.strip() or data["election_title"]
            save_data(data)
            st.success("Saved!")
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        st.markdown("**Results visibility**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Unlock results", type="primary", use_container_width=True):
                data["results_unlocked"] = True
                save_data(data)
                st.success("Results visible to everyone!")
        with col2:
            if st.button("🔒 Lock results", use_container_width=True):
                data["results_unlocked"] = False
                save_data(data)
                st.info("Results locked.")
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Reset all votes"):
            data["votes"] = {}
            data["results_unlocked"] = False
            save_data(data)
            st.success("All votes cleared.")

    with tab3:
        st.markdown(f"**Total votes:** {total_votes(data)}")
        st.markdown(f"**Results:** {'🔓 Unlocked' if data['results_unlocked'] else '🔒 Locked'}")
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        for c in data["candidates"]:
            v = data["votes"].get(str(c["id"]), 0)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(c["name"])
            with col2:
                st.markdown(f"**{v}**")

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.screen = "home"
        st.rerun()